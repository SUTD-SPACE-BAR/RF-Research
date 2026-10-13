#!/usr/bin/env python3
# Runtime (W6-F5, 2026-10-14): ~141 s (2.4 min) measured on a 10-core Apple-silicon Mac, run 3 at a time
# under load average 7-70 from other jobs; expect less on an idle machine. It exceeds the 120 s per-script budget
# used by the D7 verify sweep, so give it a >= 15 min timeout and run it with `python3 -u` to see progress.
# Measured run: exit 0, no FAIL lines. Comment only; no code or results changed.
"""s6_coupled_offset.py — coupled-microstrip closed forms, trapezoidal etch and offset stripline on JLC 6-layer
(task W5-S6, gap G-03-10) for kb/03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md.

1. Kirschning-Jansen (1984) and Hammerstad-Jensen (1980) quasi-static even/odd-mode Z and eps_eff for edge-coupled
   microstrip (t = 0), re-implemented from the published equations as coded in Qucs (qucsator mscoupled.cpp),
   compared with the KB's 2-D field solver (tools/verify/tline_fd2d.py) over u = W/h 0.3-3, g = s/h 0.2-2, er 4.4,
   and on the JLC04161H-7628 pair (W 0.1722 / s 0.15 mm).
2. Trapezoidal etch (JLC calculator: top width W2 = W1 - 0.5 mil): FD with a staircased trapezoid vs rectangles.
3. Offset (asymmetric) stripline on L3 of JLC06161H-3313 and -1080 (L2 and L4 as grounds): FD 50-ohm widths.
   Layer data from jlcpcb.com/impedance (read 2026-10-13 via a page summary; re-check before ordering).
"""
import os
import sys

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tline_fd2d as fd                      # noqa: E402
from tline_microstrip import _hj_z01, _hj_ee, ms_hj   # noqa: E402

ETA0 = 376.730313668
PASS = []


def check(name, cond, detail=""):
    PASS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def hj_ab(u, er):
    a = 1 + np.log((u ** 4 + (u / 52) ** 2) / (u ** 4 + 0.432)) / 49 + np.log(1 + (u / 18.1) ** 3) / 18.7
    b = 0.564 * ((er - 0.9) / (er + 3)) ** 0.053
    return a, b


def coupled_kj(W, s, h, er):
    """Kirschning & Jansen 1984 quasi-static, zero thickness. Returns Ze, Zo, ee_e, ee_o."""
    u, g = W / h, s / h
    v = u * (20 + g ** 2) / (10 + g ** 2) + g * np.exp(-g)
    ee_e = _hj_ee(v, er)
    ee = _hj_ee(u, er)
    d = 0.593 + 0.694 * np.exp(-0.562 * u)
    bo = 0.747 * er / (0.15 + er)
    co = bo - (bo - 0.207) * np.exp(-0.414 * u)
    ao = 0.7287 * (ee - (er + 1) / 2) * (1 - np.exp(-0.179 * u))
    ee_o = ((er + 1) / 2 + ao - ee) * np.exp(-co * g ** d) + ee
    Zl1 = _hj_z01(u) / np.sqrt(ee)
    q1 = 0.8695 * u ** 0.194
    q2 = 1 + 0.7519 * g + 0.189 * g ** 2.31
    q3 = 0.1975 + (16.6 + (8.4 / g) ** 6) ** -0.387 + np.log(g ** 10 / (1 + (g / 3.4) ** 10)) / 241
    q4 = q1 / q2 * 2 / (np.exp(-g) * u ** q3 + (2 - np.exp(-g)) * u ** (-q3))
    Ze = np.sqrt(ee / ee_e) * Zl1 / (1 - Zl1 * np.sqrt(ee) * q4 / ETA0)
    q5 = 1.794 + 1.14 * np.log(1 + 0.638 / (g + 0.517 * g ** 2.43))
    q6 = 0.2305 + np.log(g ** 10 / (1 + (g / 5.8) ** 10)) / 281.3 + np.log(1 + 0.598 * g ** 1.154) / 5.1
    q7 = (10 + 190 * g ** 2) / (1 + 82.3 * g ** 3)
    q8 = np.exp(-6.5 - 0.95 * np.log(g) - (g / 0.15) ** 5)
    q9 = np.log(q7) * (q8 + 1 / 16.5)
    q10 = (q2 * q4 - q5 * np.exp(np.log(u) * q6 * u ** (-q9))) / q2
    Zo = np.sqrt(ee / ee_o) * Zl1 / (1 - Zl1 * np.sqrt(ee) * q10 / ETA0)
    return Ze, Zo, ee_e, ee_o


def coupled_hj(W, s, h, er):
    """Hammerstad & Jensen 1980 coupled microstrip, zero thickness."""
    u, g = W / h, s / h
    m = 0.2175 + (4.113 + (20.36 / g) ** 6) ** -0.251 + np.log(g ** 10 / (1 + (g / 13.8) ** 10)) / 323
    al = 0.5 * np.exp(-g)
    psi = 1 + g / 1.45 + g ** 2.09 / 3.95
    phi = 0.8645 * u ** 0.172
    Pe = phi / (psi * (al * u ** m + (1 - al) * u ** (-m)))
    n = (1 / 17.7 + np.exp(-6.424 - 0.76 * np.log(g) - (g / 0.23) ** 5)) * \
        np.log((10 + 68.3 * g ** 2) / (1 + 32.5 * g ** 3.093))
    beta = 0.2306 + np.log(g ** 10 / (1 + (g / 3.73) ** 10)) / 301.8 + np.log(1 + 0.646 * g ** 1.175) / 5.3
    theta = 1.729 + 1.175 * np.log(1 + 0.627 / (g + 0.327 * g ** 2.17))
    Po = Pe - theta / psi * np.exp(beta * u ** (-n) * np.log(u))
    r = 1 + 0.15 * (1 - np.exp(1 - (er - 1) ** 2 / 8.2) / (1 + g ** -6))
    fo1 = 1 - np.exp(-0.179 * g ** 0.15 - 0.328 * g ** r / np.log(np.e + (g / 7) ** 2.8))
    q = np.exp(-1.366 - g)
    p = np.exp(-0.745 * g ** 0.295) / np.cosh(g ** 0.68)
    fo = fo1 * np.exp(p * np.log(u) + q * np.sin(np.pi * np.log10(u)))
    Mu = g * np.exp(-g) + u * (20 + g ** 2) / (10 + g ** 2)
    a, b = hj_ab(Mu, er)
    Fe = (1 + 10 / Mu) ** (-a * b)
    a, b = hj_ab(u, er)
    Fo = fo * (1 + 10 / u) ** (-a * b)
    ee_e = (er + 1) / 2 + (er - 1) / 2 * Fe
    ee_o = (er + 1) / 2 + (er - 1) / 2 * Fo
    Zl1 = _hj_z01(u) / np.sqrt(_hj_ee(u, er))
    return Zl1 / (1 - Zl1 * Pe / ETA0), Zl1 / (1 - Zl1 * Po / ETA0), ee_e, ee_o


def fd_coupled(W, s, h, er, t=0.0, levels=(1.0, 0.5, 0.25)):
    geo = fd.coupled_microstrip_geo(W, s, h, t, er)
    hmin = min(W, s, h) / 30
    hmax = h / 3
    _, ext, _ = fd.refine_study(lambda k: fd.coupled_params(geo, hmin=hmin * k, hmax=hmax * k), levels)
    return ext


def fd_single(geo_fun, W, hmin, hmax, levels=(1.0, 0.5, 0.25)):
    geo = geo_fun(W)
    _, ext, _ = fd.refine_study(lambda k: fd.line_params(geo, hmin=hmin * k, hmax=hmax * k)[:2], levels)
    return ext


def main():
    print("=== 1. coupled microstrip closed forms vs FD (t = 0, er 4.4, h = 1 mm)")
    h, er = 1e-3, 4.4
    worst = {"KJ": 0.0, "HJ": 0.0, "HJ_ee": 0.0}
    for u in (0.3, 1.0, 3.0):
        for g in (0.2, 0.5, 1.0, 2.0):
            ze, zo, eee, eeo = fd_coupled(u * h, g * h, h, er)
            kj = coupled_kj(u * h, g * h, h, er)
            hj = coupled_hj(u * h, g * h, h, er)
            for nm, v in (("KJ", kj), ("HJ", hj)):
                errs = [abs(v[0] / ze - 1), abs(v[1] / zo - 1), abs(v[2] / eee - 1), abs(v[3] / eeo - 1)]
                worst[nm] = max(worst[nm], max(errs))
                if nm == "HJ":
                    worst["HJ_ee"] = max(worst["HJ_ee"], max(errs[2:]))
            print(f"   u {u:3.1f} g {g:3.1f}: FD Ze {ze:6.1f} Zo {zo:5.1f} ee_e {eee:.3f} ee_o {eeo:.3f} | "
                  f"KJ {kj[0]:6.1f} {kj[1]:5.1f} {kj[2]:.3f} {kj[3]:.3f} | HJ {hj[0]:6.1f} {hj[1]:5.1f} {hj[2]:.3f} {hj[3]:.3f}")
    print(f"   worst relative error vs FD: KJ {worst['KJ']*100:.2f} %, HJ {worst['HJ']*100:.2f} % (HJ eps_eff only "
          f"{worst['HJ_ee']*100:.2f} %)")
    check("Kirschning-Jansen within 2 % of FD over u 0.3-3, g 0.2-2", worst["KJ"] < 0.02)
    check("Hammerstad-Jensen coupled (as coded in qucsator): eps_eff within 1 % but Z off by > 5 % -> use KJ",
          worst["HJ_ee"] < 0.01 and worst["HJ"] > 0.05)
    W, s, h7 = 0.1722e-3, 0.15e-3, 0.2104e-3
    kj = coupled_kj(W, s, h7, 4.4)
    ze, zo, _, _ = fd_coupled(W, s, h7, 4.4)
    print(f"   JLC-7628 pair 0.1722/0.15 mm, t = 0: KJ Zdiff {2*kj[1]:.1f}, Zcomm {kj[0]/2:.1f}; FD Zdiff {2*zo:.1f}, "
          f"Zcomm {ze/2:.1f} ohm (t = 35 um FD on the page: 109 ohm)")
    check("KJ Zdiff of the JLC pair within 2 % of FD (t = 0)", abs(kj[1] / zo - 1) < 0.02)

    print("=== 2. trapezoidal etch, JLC04161H-7628 single microstrip, 35 um, bare")
    h, t, er = 0.2104e-3, 35e-6, 4.4
    hmin, hmax = t / 6, h / 3

    def ms_rect(W):
        return fd.microstrip_geo(W, h, t, er)

    def ms_trap(W1, n=5, dW=12.7e-6):
        def mk(_W):
            box_w = max(40 * h, 12 * W1)
            g = fd.Geometry(-box_w / 2, box_w / 2, 25 * h)
            g.add_dielectric(-box_w / 2, box_w / 2, 0, h, er)
            for i in range(n):
                wi = W1 - dW * (i + 0.5) / n
                g.add_conductor(-wi / 2, wi / 2, h + t * i / n, h + t * (i + 1) / n, "sig")
            return g
        return mk

    W1 = 0.377e-3
    zr, _ = fd_single(ms_rect, W1, hmin, hmax)
    zt, _ = fd_single(ms_trap(W1), W1, hmin, hmax)
    zm, _ = fd_single(ms_rect, W1 - 6.35e-6, hmin, hmax)
    print(f"   W1 = 0.377 mm: rectangle {zr:.2f} ohm, trapezoid (W2 = W1 - 12.7 um) {zt:.2f} ohm, "
          f"rectangle at mean width {zm:.2f} ohm")
    check("trapezoid = rectangle at the mean width within 0.3 ohm", abs(zt - zm) < 0.3)
    check("etch-back of 0.5 mil raises Z0 by < 1 ohm on this stackup", 0 < zt - zr < 1.0, f"+{zt-zr:.2f} ohm")

    print("=== 3. offset stripline on L3, JLC 6-layer (L2 and L4 ground; trace 15.2 um on the core face)")
    stacks = {"JLC06161H-3313": (0.55e-3, 4.6, 0.1088e-3, 4.16), "JLC06161H-1080": (0.55e-3, 4.6, 0.2104e-3, 4.4)}
    tt = 15.2e-6
    for name, (hc, erc, hp, erp) in stacks.items():
        def geo(W, hc=hc, erc=erc, hp=hp, erp=erp):
            # y = 0: L4 plane (box wall); prepreg hp (copper-to-copper) up to the trace bottom, trace 15.2 um,
            # core hc above the trace top... the trace sits on the core's lower face, embedded in prepreg.
            ytr0 = hp
            ytop = hp + tt + hc
            box_w = max(30 * (hp + hc), 12 * W)
            g = fd.Geometry(-box_w / 2, box_w / 2, ytop)
            g.add_dielectric(-box_w / 2, box_w / 2, 0, ytr0 + tt, erp)
            g.add_dielectric(-box_w / 2, box_w / 2, ytr0 + tt, ytop, erc)
            g.add_conductor(-W / 2, W / 2, ytr0, ytr0 + tt, "sig")
            return g

        def z_of(W):
            return fd_single(geo, W, tt / 4, min(hp, hc) / 3, levels=(2.0, 1.0, 0.5))[0]

        w50 = brentq(lambda W: z_of(W) - 50, 0.03e-3, 0.4e-3, xtol=2e-6)
        z50, ee = fd_single(geo, w50, tt / 4, min(hp, hc) / 3)
        # sanity: same trace as a microstrip over only the near plane (upper bound on Z)
        zms = ms_hj(w50, hp, erp, tt)[0]
        print(f"   {name}: near plane {hp*1e3:.4f} mm (er {erp}), far plane {hc*1e3:.2f} mm (er {erc}): "
              f"50-ohm width {w50*1e3:.3f} mm (eeff {ee:.2f}); as microstrip over the near plane only it would be {zms:.1f} ohm")
        check(f"{name}: offset stripline Z below the near-plane microstrip value", z50 < zms)
    print("\nALL PASS" if all(PASS) else "\nSOME CHECKS FAILED")


if __name__ == "__main__":
    main()
