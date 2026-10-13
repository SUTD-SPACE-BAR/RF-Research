#!/usr/bin/env python3
"""s6_radial_stub.py — radial (fan) and butterfly stub theory for
kb/03-transmission-lines-matching/input-impedance-stubs-quarter-wave.md (task W5-S6, gap G-03-02).

Model. A sector of angle alpha cut from a parallel-plate radial line (height h) carries the
lowest radial mode: Ez = A J0(kr) + B Y0(kr), H_phi = (j/eta)(A J1 + B Y1). Voltage V = Ez h,
current I = H_phi * alpha * r. An open outer edge (H_phi(r_o) = 0) gives, at the inner radius r_i,
    Z_in = j (eta h / (alpha r_i)) * [J0(k r_i) Y1(k r_o) - Y0(k r_i) J1(k r_o)]
                                  / [J1(k r_i) Y1(k r_o) - Y1(k r_i) J1(k r_o)]
with k = k0 sqrt(eps), eta = eta0 / sqrt(eps).  Checks below:
  1. low-frequency limit = parallel-plate sector capacitor C = eps0 eps alpha (r_o^2 - r_i^2) / (2h);
  2. alpha -> small, r_i -> large with r_o - r_i fixed: the sector becomes a uniform parallel-plate
     stub and Z_in -> -j Z_pp cot(k l), Z_pp = eta h /(alpha r_i);
  3. model variants for 'which eps and which radius' (HP AN 976 discusses eps_r vs eps_eff):
       A  eps_r, geometric r_o
       B  eps_eff of a microstrip whose width halves the stub area (AN 976 rule), geometric r_o
       C  eps_eff as B, r_o + Hammerstad open-end extension (width = arc at r_o)
       D  eps_r, r_o replaced by the circular-disc effective radius (Shen/Wheeler fringing)
     -> outer radius needed for resonance (Z_in = 0) at 2.45 GHz on JLC0216A (h 1.43 mm, eps_r 4.5).
  4. Bandwidth: |S21| of a shunt radial stub, butterfly, and uniform 50/20 ohm open stubs on a 50 ohm
     line — width of the band with |S21| < -20 dB.
These predictions are pre-registered for s6_radial_stub_openems.py (written before that run).
"""
import os
import sys

import numpy as np
from scipy.special import j0, j1, y0, y1
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tline_microstrip import ms_hj, width_for  # noqa: E402

C0 = 299792458.0
ETA0 = 376.730313
EPS0 = 8.8541878188e-12
PASS = []


def check(name, cond, detail=""):
    PASS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def zin_radial(f, ri, ro, alpha, h, eps):
    k = 2 * np.pi * f * np.sqrt(eps) / C0
    eta = ETA0 / np.sqrt(eps)
    a, b = k * ri, k * ro
    num = j0(a) * y1(b) - y0(a) * j1(b)
    den = j1(a) * y1(b) - y1(a) * j1(b)
    return 1j * eta * h / (alpha * ri) * num / den


def ee_hj(W, h, er):
    return ms_hj(W, h, er, 0.0)[1]


def dl_open_hammerstad(W, h, ee):
    u = W / h
    return 0.412 * h * (ee + 0.3) * (u + 0.264) / ((ee - 0.258) * (u + 0.8))


def disc_eff_radius(a, h, er):
    return a * np.sqrt(1 + 2 * h / (np.pi * a * er) * (np.log(np.pi * a / (2 * h)) + 1.7726))


def variant(name, ri, ro, alpha, h, er):
    """return (eps, ro_eff) for a model variant"""
    if name == "A":
        return er, ro
    # width that splits the sector area in half: arc width at r_half, r_half^2 = (ri^2 + ro^2)/2
    r_half = np.sqrt((ri ** 2 + ro ** 2) / 2)
    w_half = alpha * r_half
    ee = ee_hj(w_half, h, er)
    if name == "B":
        return ee, ro
    if name == "C":
        return ee, ro + dl_open_hammerstad(alpha * ro, h, ee)
    if name == "D":
        return er, disc_eff_radius(ro, h, er) if True else ro
    raise ValueError(name)


def zin_variant(f, ri, ro, alpha, h, er, name):
    eps, roe = variant(name, ri, ro, alpha, h, er)
    return zin_radial(f, ri, roe, alpha, h, eps)


def f_res(ri, ro, alpha, h, er, name, f_lo=0.3e9, f_hi=12e9):
    g = lambda f: np.imag(zin_variant(f, ri, ro, alpha, h, er, name))
    fs = np.linspace(f_lo, f_hi, 4000)
    v = np.array([g(x) for x in fs])
    for i in range(len(fs) - 1):
        if v[i] < 0 < v[i + 1] and abs(v[i]) < 1e4 and abs(v[i + 1]) < 1e4:   # capacitive -> inductive: zero
            return brentq(g, fs[i], fs[i + 1])
    return np.nan


def ro_for(f0, ri, alpha, h, er, name):
    g = lambda ro: f_res(ri, ro, alpha, h, er, name) - f0
    ros = np.linspace(ri + 1e-3, 40e-3, 80)
    v = np.array([g(r) for r in ros])
    for i in range(len(ros) - 1):
        if np.isfinite(v[i]) and np.isfinite(v[i + 1]) and v[i] > 0 > v[i + 1]:
            return brentq(g, ros[i], ros[i + 1])
    return np.nan


def main():
    H, ER = 1.43e-3, 4.5
    F0 = 2.45e9
    print("=== 1. low-frequency limit = sector capacitor")
    ri, ro, al = 0.8e-3, 10e-3, np.deg2rad(60)
    f = 10e6
    z = zin_radial(f, ri, ro, al, H, ER)
    C_pp = EPS0 * ER * al * (ro ** 2 - ri ** 2) / (2 * H)
    C_mod = -1 / (2 * np.pi * f * np.imag(z))
    check("Z_in(10 MHz) is a capacitor equal to the sector parallel-plate C", abs(C_mod / C_pp - 1) < 1e-4,
          f"C = {C_mod*1e12:.4f} pF vs {C_pp*1e12:.4f} pF")

    print("=== 2. thin-sector limit = uniform parallel-plate stub")
    ri, L, al = 20.0, 10e-3, 2.5e-6    # r_i = 20 m, alpha small: width alpha*r = 50 um, taper 0.05 %
    f = 2e9
    z = zin_radial(f, ri, ri + L, al, H, ER)
    k = 2 * np.pi * f * np.sqrt(ER) / C0
    zpp = ETA0 / np.sqrt(ER) * H / (al * ri)
    zu = -1j * zpp / np.tan(k * L)
    check("thin sector -> -j Zpp cot(kl)", abs(z / zu - 1) < 1e-3, f"{z.imag:.2f} vs {zu.imag:.2f} ohm")

    print("=== 3. outer radius for resonance at 2.45 GHz, JLC0216A (h 1.43 mm, er 4.5), r_i from 0.8 mm feed")
    WF = 0.8e-3
    W50 = width_for(50, lambda w: ms_hj(w, H, ER, 0.0)[0])
    print(f"   50-ohm width (t = 0, bare) = {W50*1e3:.3f} mm; feed 0.8 mm -> {ms_hj(WF, H, ER)[0]:.1f} ohm")
    rows = {}
    for deg in (60, 90):
        al = np.deg2rad(deg)
        ri = WF / (2 * np.sin(al / 2))       # chord at r_i equals the feed width
        line = f"   alpha {deg:3d} deg, r_i = {ri*1e3:.3f} mm:"
        for name in "ABCD":
            ro = ro_for(F0, ri, al, H, ER, name)
            rows[(deg, name)] = ro
            line += f"  {name}: r_o = {ro*1e3:6.2f} mm"
        print(line)
    # a quarter wave of uniform 50-ohm microstrip for comparison
    ee50 = ee_hj(W50, H, ER)
    q50 = C0 / (4 * F0 * np.sqrt(ee50)) - dl_open_hammerstad(W50, H, ee50)
    print(f"   uniform 50-ohm open stub: lambda_g/4 - dl = {q50*1e3:.2f} mm (eeff {ee50:.3f})")
    spread = max(rows[(60, n)] for n in "ABCD") / min(rows[(60, n)] for n in "ABCD") - 1
    check("model variants disagree by > 5 % in r_o (so an EM check is needed)", spread > 0.05,
          f"spread {spread*100:.1f} %")
    check("radial stub (60 deg) is shorter than a uniform 50-ohm lambda/4 stub",
          rows[(60, "C")] - 0.8e-3 / (2 * np.sin(np.pi / 6)) < q50)

    print("=== PRE-REGISTRATION for s6_radial_stub_openems.py (2026-10-13, before the run)")
    al = np.deg2rad(60)
    ri = WF / (2 * np.sin(al / 2))
    ro_test = round(rows[(60, "C")] * 1e3, 1) * 1e-3
    print(f"   geometry: alpha 60 deg, r_i {ri*1e3:.3f} mm, r_o {ro_test*1e3:.2f} mm, feed 0.8 mm, h 1.43, er 4.5 (lossless)")
    for name in "ABCD":
        print(f"   model {name}: f_res = {f_res(ri, ro_test, al, H, ER, name)/1e9:.3f} GHz")
    print("   expectation: openEMS f_res within +-4 % of model C; A (eps_r, no fringe) high by > 5 %; "
          "|Z_in| model C within 15 % of openEMS at 1.5 GHz (capacitive region).")

    print("=== 4. stop-band width of shunt stubs on a 50-ohm line (|S21| < -20 dB)")
    fs = np.linspace(1.0e9, 4.0e9, 3001)

    def s21_shunt(Z):
        return 2 * Z / (2 * Z + 50.0)        # shunt Z across a matched 50-ohm line: S21 = 2Z/(2Z+Z0)

    def bw20(s):
        m = 20 * np.log10(np.abs(s)) < -20
        return (fs[m].max() - fs[m].min()) if m.any() else 0.0

    res = {}
    for deg in (60, 90):
        al = np.deg2rad(deg)
        ri = WF / (2 * np.sin(al / 2))
        ro = rows[(deg, "C")]
        Z = np.array([zin_variant(x, ri, ro, al, H, ER, "C") for x in fs])
        res[f"radial {deg}"] = bw20(s21_shunt(Z))
        res[f"butterfly 2x{deg}"] = bw20(s21_shunt(Z / 2))
    for z0 in (ms_hj(WF, H, ER)[0], 50.0, 20.0):
        W = width_for(z0, lambda w: ms_hj(w, H, ER, 0.0)[0])
        ee = ee_hj(W, H, ER)
        ell = C0 / (4 * F0 * np.sqrt(ee))
        Z = -1j * z0 / np.tan(2 * np.pi * fs * np.sqrt(ee) / C0 * ell)
        res[f"uniform {z0:.0f} ohm"] = bw20(s21_shunt(Z))
        res[f"uniform {z0:.0f} ohm width"] = W
    for kk, v in res.items():
        if "width" in kk:
            print(f"   {kk}: {v*1e3:.2f} mm")
        else:
            print(f"   {kk:18s}: |S21| < -20 dB over {v/1e6:6.0f} MHz ({v/F0*100:.1f} %)")
    zf = f"uniform {ms_hj(WF, H, ER)[0]:.0f} ohm"
    check("radial 60 deg stop band wider than a uniform stub of the same 0.8 mm contact width",
          res["radial 60"] > 1.25 * res[zf])
    check("faithful: a wide 20-ohm uniform stub beats a 60-deg radial stub on bandwidth (but needs a 9.8 mm contact)",
          res["uniform 20 ohm"] > res["radial 60"])
    check("butterfly wider than single radial", res["butterfly 2x60"] > res["radial 60"])
    print("\nALL PASS" if all(PASS) else "\nSOME CHECKS FAILED")


if __name__ == "__main__":
    main()
