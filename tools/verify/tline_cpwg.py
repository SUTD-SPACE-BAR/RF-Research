#!/usr/bin/env python3
"""
Coplanar waveguide (CPW) and grounded/conductor-backed CPW (CPWG) calculators + verification for
kb/03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md

Calculators (conformal mapping, zero-thickness conductors, infinitely wide lateral grounds):
  cpw(W, S, h, er)    CPW on a substrate of finite thickness h, no backside metal (Ghione & Naldi / Simons)
  cpwg(W, S, h, er)   conductor-backed CPW (Ghione & Naldi 1984)
Checks:
  1. cpwg / cpw vs own FD field solver (tools/verify/tline_fd2d.py) for several geometries.
  2. cpwg / cpw vs scikit-rf CPW (t = None) — implementation cross-check.
  3. Effect of 35 um copper thickness and of soldermask (FD) on Z0.
  4. Limits: large gap -> microstrip; thin substrate -> parallel-plate dominated.
  5. JLCPCB designs: 2-layer 1.6 mm (er 4.5) CPWG widths for 50 ohm at gaps 0.15-0.30 mm;
     JLC04161H-7628 CPWG (published: 0.34 mm / 0.2 mm, Saturn PCB Toolkit; 0.30 / 0.18 mm LibreCAL).

Run: python3 tools/verify/tline_cpwg.py      (about 1-2 minutes)
"""
import os
import sys
import warnings
import numpy as np
from scipy.special import ellipk
from scipy.optimize import brentq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tline_fd2d as fd  # noqa: E402
from tline_microstrip import ms_hj, width_for  # noqa: E402

warnings.filterwarnings("ignore")
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def KK(k):
    """K(k)/K(k') with modulus k (scipy's ellipk takes m = k^2)."""
    return ellipk(k * k) / ellipk(1 - k * k)


def cpw(W, S, h, er):
    a, b = W / 2, W / 2 + S
    k0 = a / b
    k1 = np.sinh(np.pi * a / (2 * h)) / np.sinh(np.pi * b / (2 * h))
    ee = 1 + (er - 1) / 2 * KK(k1) / KK(k0)
    z = 30 * np.pi / np.sqrt(ee) / KK(k0)
    return z, ee


def cpwg(W, S, h, er):
    a, b = W / 2, W / 2 + S
    k0 = a / b
    k3 = np.tanh(np.pi * a / (2 * h)) / np.tanh(np.pi * b / (2 * h))
    q = KK(k3) / KK(k0)
    ee = (1 + er * q) / (1 + q)
    z = 60 * np.pi / np.sqrt(ee) / (KK(k0) + KK(k3))
    return z, ee


def fd_cpwg(W, S, h, t, er, mask_t=0.0, backed=True, levels=(1.0, 0.5, 0.25)):
    geo = fd.cpwg_geo(W, S, h, t, er, mask_t=mask_t)
    if not backed:
        # remove the bottom ground: put the box floor far below with air under the substrate
        drop = 20 * h
        g2 = fd.Geometry(geo.xmin, geo.xmax, geo.ymax + drop)
        for (x0, x1, y0, y1, e) in geo.diel:
            g2.add_dielectric(x0, x1, y0 + drop, y1 + drop, e)
        for (x0, x1, y0, y1, n) in geo.cond:
            g2.add_conductor(x0, x1, y0 + drop, y1 + drop, n)
        geo = g2
    hmin = min(W, S, 4 * t if t > 0 else S) / 30
    hmax = max(h, S) / 3
    _, ext, _ = fd.refine_study(lambda s: fd.line_params(geo, hmin=hmin * s, hmax=hmax * s)[:2], levels)
    return ext[0], ext[1]


if __name__ == "__main__":
    import skrf as rf

    # ------------------------------------------------ 1-2. formulas vs FD and skrf
    print("1-2. Conformal-mapping CPWG / CPW vs own FD solver and scikit-rf (t = 0)")
    fq = rf.Frequency(1, 1, 1, unit="MHz")
    worst = 0
    worst_skrf = 0
    for W, S, h, er in [(1.0e-3, 0.2e-3, 1.51e-3, 4.5), (0.5e-3, 0.3e-3, 0.8e-3, 4.5),
                        (0.34e-3, 0.2e-3, 0.2104e-3, 4.4), (0.2e-3, 0.1e-3, 0.5e-3, 10.0)]:
        zg, eg = cpwg(W, S, h, er)
        zfd, efd = fd_cpwg(W, S, h, 0.0, er)
        m = rf.media.CPW(frequency=fq, w=W, s=S, h=h, ep_r=er, t=None, has_metal_backside=True,
                         diel="frequencyinvariant", z0_port=50)
        dz = (zg - zfd) / zfd
        worst = max(worst, abs(dz))
        worst_skrf = max(worst_skrf, abs(m.z0[0].real - zg) / zg)
        print(f"   CPWG W {W*1e3:.2f} S {S*1e3:.2f} h {h*1e3:.3f} er {er}: formula {zg:.2f} ohm (eeff {eg:.3f}),"
              f" FD {zfd:.2f} (eeff {efd:.3f}), skrf {m.z0[0].real:.2f}; dZ vs FD {dz*100:+.2f} %")
    check("Ghione-Naldi CPWG formula within 1.5 % of FD field solution", worst < 0.015, f"(worst {worst*100:.2f} %)")
    check("own CPWG formula == scikit-rf CPW(has_metal_backside=True, t=None)", worst_skrf < 1e-3,
          f"(max dev {worst_skrf*100:.3f} %)")
    worst = 0
    for W, S, h, er in [(1.0e-3, 0.2e-3, 1.51e-3, 4.5), (0.3e-3, 0.15e-3, 0.5e-3, 10.0)]:
        zc, ec = cpw(W, S, h, er)
        zfd, efd = fd_cpwg(W, S, h, 0.0, er, backed=False)
        m = rf.media.CPW(frequency=fq, w=W, s=S, h=h, ep_r=er, t=None, has_metal_backside=False,
                         diel="frequencyinvariant", z0_port=50)
        dz = (zc - zfd) / zfd
        worst = max(worst, abs(dz))
        print(f"   CPW  W {W*1e3:.2f} S {S*1e3:.2f} h {h*1e3:.3f} er {er}: formula {zc:.2f} ohm (eeff {ec:.3f}),"
              f" FD {zfd:.2f} (eeff {efd:.3f}), skrf {m.z0[0].real:.2f}")
    check("CPW (no backing) formula within 2 % of FD", worst < 0.02, f"(worst {worst*100:.2f} %)")

    # ------------------------------------------------ 3. thickness and soldermask
    print("3. Copper thickness and soldermask (FD), 2-layer 1.6 mm FR-4 CPWG W 1.0 mm S 0.2 mm")
    z_t0, _ = fd_cpwg(1.0e-3, 0.2e-3, 1.51e-3, 0.0, 4.5)
    z_t35, e35 = fd_cpwg(1.0e-3, 0.2e-3, 1.51e-3, 35e-6, 4.5)
    z_m, em = fd_cpwg(1.0e-3, 0.2e-3, 1.51e-3, 35e-6, 4.5, mask_t=15e-6)
    print(f"   t = 0: {z_t0:.2f} ohm;  t = 35 um: {z_t35:.2f} ohm (eeff {e35:.3f});  + 15 um mask (er 3.8): {z_m:.2f} ohm (eeff {em:.3f})")
    check("35 um copper lowers CPWG Z0 by 1-5 ohm for a 0.2 mm gap", 1 < z_t0 - z_t35 < 5)
    check("soldermask lowers Z0 further (by 0.5-4 ohm)", 0.5 < z_t35 - z_m < 4)

    # ------------------------------------------------ 4. limits
    print("4. Large-gap limit (W 3 mm, h 1.51 mm, er 4.5): formula vs FD vs microstrip")
    zm, _ = ms_hj(3.0e-3, 1.51e-3, 4.5)
    res = []
    for S in [1.5e-3, 3e-3, 6e-3]:
        zf = cpwg(3.0e-3, S, 1.51e-3, 4.5)[0]
        zd = fd_cpwg(3.0e-3, S, 1.51e-3, 0.0, 4.5)[0]
        res.append((S, zf, zd))
        print(f"   S = {S*1e3:.1f} mm (S/h = {S/1.51e-3:.1f}): Ghione-Naldi {zf:.2f}, FD {zd:.2f}, microstrip (H-J) {zm:.2f} ohm")
    check("FD CPWG -> microstrip for S = 4h (within 1 %)", abs(res[-1][2] - zm) / zm < 0.01)
    check("Ghione-Naldi CPWG formula overestimates Z0 by > 2 % once S >= 2h (not valid as gap -> infinity)",
          (res[1][1] - res[1][2]) / res[1][2] > 0.02 and (res[2][1] - res[2][2]) / res[2][2] > 0.04)

    # ------------------------------------------------ 5. JLCPCB designs
    print("5. 50-ohm CPWG widths (formula, t = 0, then FD check with t = 35 um)")
    print("   2-layer 1.6 mm FR-4 (core 1.51 mm between 35 um coppers, er 4.5):")
    for S in [0.15e-3, 0.20e-3, 0.25e-3, 0.30e-3]:
        W0 = brentq(lambda w: cpwg(w, S, 1.51e-3, 4.5)[0] - 50, 0.05e-3, 20e-3)
        # FD with thickness: find W that gives 50 ohm (secant on FD)
        zA, _ = fd_cpwg(W0, S, 1.51e-3, 35e-6, 4.5)
        W1 = W0 * 0.9 if zA < 50 else W0 * 1.1
        zB, _ = fd_cpwg(W1, S, 1.51e-3, 35e-6, 4.5)
        Wt = W0 + (50 - zA) * (W1 - W0) / (zB - zA)
        zC, eC = fd_cpwg(Wt, S, 1.51e-3, 35e-6, 4.5)
        Wt2 = Wt + (50 - zC) * (Wt - W1) / (zC - zB)          # second secant step
        zC, eC = fd_cpwg(Wt2, S, 1.51e-3, 35e-6, 4.5)
        Wt = Wt2
        print(f"     gap {S*1e3:.2f} mm: W(formula, t=0) = {W0*1e3:.3f} mm -> FD with 35 um Cu: {zA:.2f} ohm;"
              f" W for 50 ohm incl. thickness = {Wt*1e3:.3f} mm (FD {zC:.2f} ohm, eeff {eC:.3f})")
    wm = width_for(50, lambda w: ms_hj(w, 1.51e-3, 4.5, 35e-6)[0])
    print(f"     (plain microstrip, same board: {wm*1e3:.2f} mm)")
    print("   JLC04161H-7628 (h 0.2104 mm to L2 ground, er 4.4):")
    for W, S, label in [(0.34e-3, 0.20e-3, "Saturn-PCB design in LibreCAL PR #8"), (0.30e-3, 0.18e-3, "LibreCAL as built"),
                        (0.36e-3, 0.30e-3, "wide gap")]:
        zf, ef = cpwg(W, S, 0.2104e-3, 4.4)
        zt, et = fd_cpwg(W, S, 0.2104e-3, 35e-6, 4.4)
        ztm, etm = fd_cpwg(W, S, 0.2104e-3, 35e-6, 4.4, mask_t=15e-6)
        print(f"     W {W*1e3:.2f} S {S*1e3:.2f} ({label}): formula(t=0) {zf:.2f} ohm; FD t=35 um {zt:.2f} ohm;"
              f" FD + mask {ztm:.2f} ohm (eeff {etm:.3f})")
        if label.startswith("Saturn"):
            check("JLC7628 CPWG 0.34/0.20 mm lands within 50 +/- 3 ohm (FD, with thickness)", abs(zt - 50) < 3)

    print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
