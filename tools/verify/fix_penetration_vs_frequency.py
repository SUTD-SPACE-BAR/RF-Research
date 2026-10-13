#!/usr/bin/env python3
"""Myth check: "higher frequencies penetrate walls better".  (W5-E1, 2026-09-29)

Two independent ITU-R models, both showing that for ordinary building materials the loss
*increases* with frequency across the RF range:

1. ITU-R P.2040-3 (08/2023) Table 3 material model: eps' = a f^b, sigma = c f^d (f in GHz, S/m),
   used here in an exact normal-incidence single-slab transmission calculation (multiple internal
   reflections included) and in the P.2040 low-loss attenuation rate A = 1636 sigma / sqrt(eps') dB/m
   (eq. 27; valid for tan(delta) < 0.5).
2. ITU-R P.2109-2 building entry loss (median, horizontal incidence), imported from the existing
   KB implementation tools/verify/prop_atmospheric.py.

Caveats printed with the results: Table 3 ranges are 1-100 GHz for concrete/plasterboard, 1-40 GHz
for brick (values below 1 GHz are extrapolations); P.2109 thermally-efficient buildings have a loss
minimum near 1-2 GHz (metallised glass/foil pass energy through apertures, which favour short
wavelengths) and the traditional class a very shallow minimum near 0.3-0.5 GHz — the ordinary-building
cases where going *up* in frequency does not immediately increase entry loss. Thin slabs (6 mm glass,
100 mm brick) also show thickness (Fabry-Perot) ripples, so their loss is not monotonic in f even
though the material's attenuation rate is.
Run: python3 tools/verify/fix_penetration_vs_frequency.py   -> prints tables, ends with ALL PASS.
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prop_atmospheric import building_entry_loss  # noqa: E402  (P.2109-2, verified by W1-A5)

C0 = 299_792_458.0
EPS0 = 8.8541878128e-12
# ITU-R P.2040-3 Table 3: (a, b, c, d, validity GHz)
P2040 = {
    "concrete":     (5.24, 0.0, 0.0462, 0.7822, (1, 100)),
    "brick":        (3.91, 0.0, 0.0238, 0.16,   (1, 40)),
    "plasterboard": (2.73, 0.0, 0.0085, 0.9395, (1, 100)),
    "wood":         (1.99, 0.0, 0.0047, 1.0718, (0.001, 100)),
    "glass":        (6.31, 0.0, 0.0036, 1.3394, (0.1, 100)),
}
WALLS = [("concrete", 0.20), ("brick", 0.10), ("plasterboard", 0.0125), ("wood", 0.04), ("glass", 0.006)]
FREQS = [0.433, 0.915, 2.45, 5.8, 10.0, 28.0, 60.0]


def eps_complex(mat, f_ghz):
    a, b, c, d, _ = P2040[mat]
    epsr = a * f_ghz ** b
    sigma = c * f_ghz ** d
    return epsr - 1j * sigma / (2 * np.pi * f_ghz * 1e9 * EPS0), epsr, sigma   # e^{jwt} convention


def slab_loss_db(mat, thick_m, f_ghz):
    """Normal-incidence power transmission loss of a homogeneous slab in air (all internal bounces)."""
    eps, _, _ = eps_complex(mat, f_ghz)
    k0 = 2 * np.pi * f_ghz * 1e9 / C0
    n = np.sqrt(eps)
    if n.imag > 0:
        n = np.conj(n)
    g = (1 - n) / (1 + n)                     # air -> slab reflection
    ph = np.exp(-1j * k0 * n * thick_m)
    t = (1 - g ** 2) * ph / (1 - g ** 2 * ph ** 2)
    return -20 * np.log10(abs(t))


def atten_rate_db_m(mat, f_ghz):
    _, epsr, sigma = eps_complex(mat, f_ghz)
    return 1636.0 * sigma / np.sqrt(epsr)


def main():
    print("=== 1. ITU-R P.2040-3 Table 3: wall transmission loss (dB), normal incidence ===")
    print("wall".ljust(24) + "".join(f"{f:>8.3g}" for f in FREQS) + "   GHz")
    losses = {}
    for mat, t in WALLS:
        row = [slab_loss_db(mat, t, f) for f in FREQS]
        losses[mat] = row
        lo, hi = P2040[mat][4]
        flag = "" if FREQS[0] >= lo else f"   (Table 3 range {lo}-{hi} GHz: <{lo} GHz extrapolated)"
        print(f"{mat} {t*1000:.1f} mm".ljust(24) + "".join(f"{v:8.1f}" for v in row) + flag)
    print("\nattenuation rate A = 1636 sigma/sqrt(eps') (dB/m):")
    for mat, _ in WALLS:
        print(f"  {mat:13s}" + "".join(f"{atten_rate_db_m(mat, f):9.1f}" for f in FREQS))

    print("\n=== 2. ITU-R P.2109-2 median building entry loss (dB), horizontal incidence ===")
    fb = [0.1, 0.433, 0.915, 2.45, 5.8, 10.0, 28.0, 60.0, 100.0]
    print("class".ljust(22) + "".join(f"{f:>8.3g}" for f in fb) + "   GHz")
    bel = {}
    for bt in ("traditional", "thermally-efficient"):
        row = [float(building_entry_loss(f, 0.5, bt)) for f in fb]
        bel[bt] = row
        print(bt.ljust(22) + "".join(f"{v:8.1f}" for v in row))

    # ---- checks ----
    c = losses["concrete"]
    assert all(np.diff(c) > 0), "concrete loss must rise monotonically with frequency"
    assert c[0] < 6 and c[FREQS.index(28.0)] > 60, c          # ~3-4 dB at 433 MHz vs > 60 dB at 28 GHz
    for mat in ("plasterboard", "wood", "glass"):
        assert losses[mat][-1] > losses[mat][0]
    tr = bel["traditional"]
    assert all(np.diff(tr[1:]) > 0), "P.2109 traditional median must rise with frequency above ~0.4 GHz"
    assert abs(tr[0] - tr[1]) < 0.5                            # shallow minimum near 0.3-0.5 GHz
    # every material's attenuation RATE (dB/m) rises with frequency (sigma ~ f^d, d > 0)
    for mat, _ in WALLS:
        r = [atten_rate_db_m(mat, f) for f in FREQS]
        assert all(np.diff(r) > 0), mat
    te = bel["thermally-efficient"]
    imin = int(np.argmin(te))
    assert 0.9 <= fb[imin] <= 2.5, fb[imin]                    # minimum near 1-2.5 GHz
    assert te[-1] - te[imin] > 15                              # but far higher at mm-wave
    # rate formula vs exact slab (thick concrete, 10 GHz): exact includes ~ reflection only
    exact = slab_loss_db("concrete", 0.2, 10.0)
    approx = atten_rate_db_m("concrete", 10.0) * 0.2
    assert abs(exact - approx) < 4.0, (exact, approx)
    print(f"\ncheck: 0.2 m concrete at 10 GHz exact {exact:.1f} dB vs 1636*sigma/sqrt(eps')*d = {approx:.1f} dB"
          " (difference = interface reflection)")
    print("ALL PASS")


if __name__ == "__main__":
    main()
