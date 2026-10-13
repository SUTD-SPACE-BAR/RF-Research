#!/usr/bin/env python3
"""
proj_patch_gnss.py -- analytic design numbers for kb/20-projects-recipes/patch-antenna-design-walkthrough.md

GNSS L1 (1575.42 MHz) RHCP truncated-corner square patch on JLCPCB 2-layer 1.6 mm FR-4, plus the linear
2.45 GHz reference design. Uses the TL/cavity-model functions of tools/verify/ant_patch.py (design,
jackson, directivity_two_slot, cp_two_mode) so the numbers are consistent with kb/08-antennas/patch-antennas.md.

 1. Square patch side for resonance (iterating the TL model with W = L), Q budget, bandwidth, efficiency,
    gain, edge resistance and 50-ohm probe position.
 2. Single-feed CP: required mode split f0/Q; truncation area dS/S = 1/(2 Q) (Sharma & Gupta 1983, as
    quoted in Balanis 4th ed. sec. 14.5 / Garg et al.) -> truncation leg a; AR bandwidth from the two-mode model.
 3. Tolerances: FR-4 er 4.3..4.7, thickness +/-10 %, etch +/-0.05 mm -> resonance shift vs AR bandwidth.
 4. Trimming sensitivity (MHz per mm of side length, per mm of corner truncation leg).
 5. GNSS signal budget: C/N0 with passive FR-4 patch + U.FL + MAX-M10S vs ceramic patch vs active antenna.
 6. 2.45 GHz linear reference (kb/08 example 1) for comparison.

openEMS verification of the same geometry: tools/verify/proj_openems_gnss_patch.py (run with the openEMS venv).
Run: python3 tools/verify/proj_patch_gnss.py
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ant_patch as ap  # noqa: E402

C0 = 299_792_458.0
F_L1 = 1575.42e6
ER, H, TAND = 4.5, 1.51e-3, 0.02          # JLC 2-layer 1.6 mm: dielectric ~1.51 mm, Dk 4.5 (JLC capabilities page)


def square_patch(f, er, h):
    """Side L of a square patch resonant at f (TL model, W = L)."""
    L = C0 / (2 * f * math.sqrt(er))
    for _ in range(50):
        W = L
        eeff = (er + 1) / 2 + (er - 1) / 2 / math.sqrt(1 + 12 * h / W)
        dL = 0.412 * h * (eeff + 0.3) * (W / h + 0.264) / ((eeff - 0.258) * (W / h + 0.8))
        L_new = C0 / (2 * f * math.sqrt(eeff)) - 2 * dL
        if abs(L_new - L) < 1e-9:
            break
        L = 0.5 * (L + L_new)
    return L, eeff, dL


def res_freq_square(L, er, h):
    """Inverse: resonance of a square patch of side L."""
    lo, hi = 0.5e9, 5e9
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        Lm, _, _ = square_patch(mid, er, h)
        if Lm > L:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def main():
    print("=" * 90)
    print(f"1) Square patch at {F_L1/1e6:.2f} MHz on FR-4 er {ER}, h {H*1e3:.2f} mm, tan d {TAND}")
    L, eeff, dL = square_patch(F_L1, ER, H)
    J = ap.jackson(F_L1, ER, H, L, L, TAND)
    D, bwE, bwH = ap.directivity_two_slot(F_L1, L, L + 2 * dL)
    print(f"   side L = W = {L*1e3:.2f} mm (eeff {eeff:.3f}, dL {dL*1e3:.3f} mm)")
    print(f"   Q: Qd {J['Qd']:.0f}, Qc {J['Qc']:.0f}, Qsp {J['Qsp']:.1f}, Qsw {J['Qsw']:.0f} -> Q {J['Q']:.1f}; "
          f"BW(VSWR2) {100*J['BW']:.2f} % = {J['BW']*F_L1/1e6:.1f} MHz")
    print(f"   e_rad {100*J['e_rad']:.1f} %, two-slot D {10*np.log10(D):.2f} dBi -> G {10*np.log10(D*J['e_rad']):.2f} dBi (linear, one mode);"
          f" HPBW E {bwE:.0f} / H {bwH:.0f} deg")
    x50 = ap.inset_depth(J["Redge"], L)
    print(f"   R_edge {J['Redge']:.0f} ohm; 50-ohm point {x50*1e3:.2f} mm in from the edge "
          f"({(L/2-x50)*1e3:.2f} mm from centre) for a linearly polarised (single-mode) patch")

    print("\n2) Single-feed CP by truncated corners")
    Q = J["Q"]
    split = 1 / Q
    S = L * L
    dS = S / (2 * Q)
    a = math.sqrt(dS)          # two isosceles right triangles of leg a: total area a^2
    print(f"   required mode split f0/Q = {split*F_L1/1e6:.1f} MHz ({100*split:.2f} %)")
    print(f"   dS/S = 1/(2Q) = {dS/S*100:.2f} % -> dS {dS*1e6:.1f} mm^2 -> two corners cut with leg a = {a*1e3:.2f} mm "
          f"(hypotenuse {a*math.sqrt(2)*1e3:.2f} mm)")
    f, ar = ap.cp_two_mode(F_L1, Q, split)
    band = f[ar <= 3.0]
    print(f"   two-mode model: AR <= 3 dB over {(band.max()-band.min())/1e6:.1f} MHz ({100*(band.max()-band.min())/F_L1:.2f} %); "
          f"impedance BW {J['BW']*F_L1/1e6:.1f} MHz")
    for sp in (0.8, 1.2):
        f2, ar2 = ap.cp_two_mode(F_L1, Q, split * sp)
        print(f"   split {sp:.1f} x f0/Q: min AR {ar2.min():.2f} dB")
    print("   GNSS bands needing coverage: GPS L1 C/A 1575.42 +/- 1.023 MHz; Galileo E1 +/- ~2 MHz (main lobe of BOC(1,1));"
          " BeiDou B1I 1561.098 MHz (-14.3 MHz); GLONASS L1 1598-1606 MHz")

    print("\n3) Tolerances (resonance of the as-designed side)")
    for er in (4.3, 4.4, 4.5, 4.6, 4.7):
        fr = res_freq_square(L, er, H)
        print(f"   er {er:.1f}: f_res {fr/1e6:8.1f} MHz ({(fr-F_L1)/1e6:+6.1f} MHz)")
    for hh in (0.9 * H, 1.1 * H):
        fr = res_freq_square(L, ER, hh)
        print(f"   h {hh*1e3:.2f} mm: f_res {fr/1e6:8.1f} MHz ({(fr-F_L1)/1e6:+6.1f} MHz)")
    for dLs in (-0.05e-3, 0.05e-3):
        fr = res_freq_square(L + dLs, ER, H)
        print(f"   side {dLs*1e3:+.2f} mm (etch): f_res {(fr-F_L1)/1e6:+6.2f} MHz")

    print("\n4) Trimming sensitivity")
    fr1 = res_freq_square(L - 1e-3, ER, H)
    print(f"   -1 mm of side: +{(fr1-F_L1)/1e6:.1f} MHz ({100*(fr1-F_L1)/F_L1:.2f} %)")
    print(f"   corner leg a: split ~ proportional to a^2: +0.5 mm on a {a*1e3:.2f} mm leg changes the split by "
          f"{100*(((a+0.5e-3)/a)**2-1):.0f} %")

    print("\n5) GNSS C/N0 budget at the minimum GPS L1 C/A signal (-128.5 dBm for a 0 dBic RHCP antenna)")
    k = 1.380649e-23
    s_min = -128.5
    def cn0(g_ant_dbic, loss_before_db, nf_rx_db, t_ant=100.0, gain_lna_db=None, nf_lna=None, loss_after_db=0.0):
        # system temperature referred to the antenna terminals
        Lb = 10 ** (loss_before_db / 10)
        te_loss = (Lb - 1) * 290
        if gain_lna_db is None:
            te_rx = 290 * (10 ** (nf_rx_db / 10) - 1)
            tsys = t_ant + te_loss + Lb * te_rx
        else:
            te_lna = 290 * (10 ** (nf_lna / 10) - 1)
            La = 10 ** (loss_after_db / 10)
            te_rest = (La - 1) * 290 + La * 290 * (10 ** (nf_rx_db / 10) - 1)
            tsys = t_ant + te_loss + Lb * (te_lna + te_rest / 10 ** (gain_lna_db / 10))
        n0 = 10 * math.log10(k * tsys / 1e-3)
        c = s_min + g_ant_dbic - loss_before_db
        return c - n0, tsys
    g_fr4 = 10 * np.log10(D * J["e_rad"])
    cases = [
        ("FR-4 truncated-corner patch (this recipe), 10 cm U.FL, MAX-M10S (internal LNA, NF ~2 dB assumed)", g_fr4, 0.3, 2.0, None, None, 0.0),
        ("25 mm ceramic patch ~3 dBic on 70 mm ground, 10 cm U.FL, MAX-M10S", 3.0, 0.3, 2.0, None, None, 0.0),
        ("FR-4 patch + own LNA (NF 0.8, 20 dB) at the feed, 30 cm RG-316 (0.8 dB), MAX-M10S", g_fr4, 0.1, 2.0, 20.0, 0.8, 0.8),
        ("active ceramic antenna (3 dBic, LNA NF 2 dB, 28 dB), 1 m RG-174 (1.1 dB), ZED-F9P (NF ~3 dB)", 3.0, 0.2, 3.0, 28.0, 2.0, 1.1),
    ]
    for name, g, lb, nf, glna, nfl, la in cases:
        c, ts = cn0(g, lb, nf, gain_lna_db=glna, nf_lna=nfl, loss_after_db=la)
        print(f"   {name}: G {g:.1f} dBic, Tsys {ts:.0f} K -> C/N0 {c:.1f} dB-Hz")

    print("\n6) 2.45 GHz linear reference (kb/08 example 1)")
    W2, L2, ee2, dL2 = ap.design(2.45e9, 4.4, 1.6e-3)
    J2 = ap.jackson(2.45e9, 4.4, 1.6e-3, W2, L2, 0.02)
    print(f"   W {W2*1e3:.2f} x L {L2*1e3:.2f} mm, Q {J2['Q']:.1f}, BW {100*J2['BW']:.2f} %, e_rad {100*J2['e_rad']:.0f} % "
          f"(openEMS in kb/16: f_res 2.397 GHz, D 6.95 dBi, e 44.5 %, G 3.44 dBi)")


if __name__ == "__main__":
    main()
