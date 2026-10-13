#!/usr/bin/env python3
"""e11_discontinuities.py — closed-form microstrip discontinuity models, cross-checked, for
kb/03-transmission-lines-matching/microstrip-discontinuities.md (task W5-E11, 2026-10-03).

Models implemented (own Python, from the published equations as documented in the Qucs technical
papers / qucs-core and in Gupta, Garg, Bahl & Bhartia):
  open end   : Kirschning-Jansen-Koster 1981 (KJK), Hammerstad 1981, Hammerstad-Bekkadal "0.412" form
  gap        : Kirschning (1983/84) pi-network (series Cs, shunt Cp1, Cp2)
  step       : Gupta et al. (shunt C, series L split by per-unit-length inductance)
  corner     : Kirschning-Jansen-Koster 1983 (square corner and 50 % mitre), Garg-Bahl 1978 square corner
  mitre      : Douville-James 1978 optimum mitre fraction
  T-junction : Hammerstad 1981 (reference-plane shifts, transformers, shunt susceptance)
  via        : Goldfarb-Pucel 1991
plus network helpers and a comparison with the openEMS runs of e11_discontinuities_openems.py
(read from tools/verify/data/e11_openems_discontinuities.npz if present).

Run:  python3 tools/verify/e11_discontinuities.py        (~5 s; prints a PASS/FAIL list)
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tline_microstrip import ms_hj, ms_kj, width_for   # noqa: E402

C0 = 299792458.0
MU0 = 4e-7 * np.pi
ETA0 = 376.730313
RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}  {detail}")


def line(W, h, er, f=None):
    """(Z0, eeff) quasi-static H-J (t = 0) or K-J dispersive if f given."""
    if f is None:
        return ms_hj(W, h, er, 0.0)
    return ms_kj(W, h, er, f, 0.0)


# ------------------------------------------------------------------ open end
def oe_kjk(W, h, er, f=None):
    """Kirschning, Jansen & Koster 1981: dl/h = Q1 Q3 Q5 / Q4 (eeff dispersive if f given)."""
    _, ee = line(W, h, er, f)
    u = W / h
    q6 = ee ** 0.81
    q7 = u ** 0.8544
    q1 = 0.434907 * (q6 + 0.26) / (q6 - 0.189) * (q7 + 0.236) / (q7 + 0.87)
    q2 = 1 + u ** 0.371 / (2.358 * er + 1)
    q3 = 1 + 0.5274 * np.arctan(0.084 * u ** (1.9413 / q2)) / ee ** 0.9236
    q4 = 1 + 0.0377 * np.arctan(0.067 * u ** 1.456) * (6 - 5 * np.exp(0.036 * (1 - er)))
    q5 = 1 - 0.218 * np.exp(-7.5 * u)
    return h * q1 * q3 * q5 / q4


def oe_hammerstad81(W, h, er):
    u = W / h
    return h * 0.102 * (u + 0.106) / (u + 0.264) * (1.166 + (er + 1) / er * (0.9 + np.log(u + 2.475)))


def oe_hb0412(W, h, er):
    u = W / h
    _, ee = line(W, h, er)
    return h * 0.412 * (ee + 0.3) * (u + 0.264) / ((ee - 0.258) * (u + 0.8))


def c_end(dl, W, h, er, f=None):
    z, ee = line(W, h, er, f)
    return dl * np.sqrt(ee) / (C0 * z)


# ------------------------------------------------------------------ gap (pi network)
def gap_kirschning(W1, W2, s, h, er, f=None):
    flip = W2 < W1
    if flip:
        W1, W2 = W2, W1
    c1 = c_end(oe_kjk(W1, h, er, f), W1, h, er, f)
    c2 = c_end(oe_kjk(W2, h, er, f), W2, h, er, f)
    w21, w1, sn = W2 / W1, W1 / h, s / h
    q5 = 1.23 / (1 + 0.12 * (w21 - 1) ** 0.9)
    q1 = 0.04598 * (0.03 + w1 ** q5) * (0.272 + 0.07 * er)
    q2 = 0.107 * (w1 + 9) * sn ** 3.23 + 2.09 * sn ** 1.05 * (1.5 + 0.3 * w1) / (1 + 0.6 * w1)
    q3 = np.exp(-0.5978 * w21 ** 1.35) - 0.55
    q4 = np.exp(-0.5978 * w21 ** -1.35) - 0.55
    cs = 5e-10 * h * np.exp(-1.86 * sn) * q1 * (1 + 4.19 * (1 - np.exp(-0.785 * np.sqrt(1 / w1) * w21)))
    cp1 = c1 * (q2 + q3) / (q2 + 1)
    cp2 = c2 * (q2 + q4) / (q2 + 1)
    if flip:
        cp1, cp2 = cp2, cp1
    return cs, cp1, cp2


# ------------------------------------------------------------------ step in width
def step_gupta(W1, W2, h, er, f=None):
    """W1 > W2. Returns (C_shunt [F], L1 [H] on the wide side, L2 [H] on the narrow side)."""
    r = W1 / W2
    cs = np.sqrt(W1 * W2) * ((10.1 * np.log10(er) + 2.33) * r - 12.6 * np.log10(er) - 3.17) * 1e-12
    ls = h * (40.5 * (r - 1) - 75 * np.log10(r) + 0.2 * (r - 1) ** 2) * 1e-9
    z1, e1 = line(W1, h, er, f)
    z2, e2 = line(W2, h, er, f)
    lw1, lw2 = z1 * np.sqrt(e1) / C0, z2 * np.sqrt(e2) / C0
    return cs, ls * lw1 / (lw1 + lw2), ls * lw2 / (lw1 + lw2)


# ------------------------------------------------------------------ bends
def corner_kjk(W, h, er):
    """Square 90-degree corner, T-network: series L, shunt C, series L (KJK 1983)."""
    u = W / h
    C = W * ((10.35 * er + 2.5) * u + (2.6 * er + 5.64)) * 1e-12
    L = 220 * h * (1 - 1.35 * np.exp(-0.18 * u ** 1.39)) * 1e-9
    return C, L


def mbend50_kjk(W, h, er):
    u = W / h
    C = W * ((3.93 * er + 0.62) * u + (7.6 * er + 3.80)) * 1e-12
    L = 440 * h * (1 - 1.062 * np.exp(-0.177 * u ** 0.947)) * 1e-9
    return C, L


def corner_garg_bahl(W, h, er):
    """Garg & Bahl 1978 (as tabulated by Gupta et al.): C_b/W [pF/m], L_b/h [nH/m]; T-network with
    L_b/2 per arm (the published L_b is the total series inductance)."""
    u = W / h
    if u < 1:
        cw = ((14 * er + 12.5) * u - (1.83 * er - 2.25)) / np.sqrt(u) + 0.02 * er / u
    else:
        cw = (9.5 * er + 1.25) * u + 5.2 * er + 7.0
    lh = 100 * (4 * np.sqrt(u) - 4.21)
    return cw * W * 1e-12, lh * h * 1e-9 / 2


def mitre_dj(u):
    """Douville & James optimum mitre fraction x/d (d = W*sqrt(2) corner diagonal)."""
    return 0.52 + 0.65 * np.exp(-1.35 * u)


# ------------------------------------------------------------------ via to ground
def via_gp(h, r):
    a = np.sqrt(r * r + h * h)
    return MU0 / (2 * np.pi) * (h * np.log((h + a) / r) + 1.5 * (r - a))


# ------------------------------------------------------------------ network helpers
def s11_tee_network(f, L, C, Z0):
    """|S11| of series jwL - shunt jwC - series jwL between lines of impedance Z0."""
    w = 2 * np.pi * np.asarray(f)
    zl = 1j * w * L
    zc = 1 / (1j * w * C)
    zin = zl + 1 / (1 / zc + 1 / (zl + Z0))
    return (zin - Z0) / (zin + Z0)


def s_gap(f, cs, cp1, cp2, Z0):
    w = 2 * np.pi * np.asarray(f)
    y = np.array([[1j * w * (cp1 + cs), -1j * w * cs], [-1j * w * cs, 1j * w * (cp2 + cs)]])
    y = np.moveaxis(y, -1, 0) if y.ndim == 3 else y
    yn = y * Z0
    I = np.eye(2)
    return (I - yn) @ np.linalg.inv(I + yn)


def tee_hammerstad(Wa, Wb, W2, h, er, f, z0=50.0):
    """Hammerstad 1981 T-junction (as in qucs-core mstee.cpp). Returns 3x3 S at the junction planes
    (ports a, b = main arm, 2 = side arm), including the short line sections La, Lb, L2."""
    za, ea = line(Wa, h, er, f)
    zb, eb = line(Wb, h, er, f)
    z2, e2 = line(W2, h, er, f)
    Da, Db, D2 = ETA0 / za * h / np.sqrt(ea), ETA0 / zb * h / np.sqrt(eb), ETA0 / z2 * h / np.sqrt(e2)
    fpa, fpb = 0.4e6 * za / h, 0.4e6 * zb / h
    lda, ldb = C0 / np.sqrt(ea) / f, C0 / np.sqrt(eb) / f
    da = 0.055 * D2 * za / z2 * (1 - 2 * za / z2 * (f / fpa) ** 2)
    db = 0.055 * D2 * zb / z2 * (1 - 2 * zb / z2 * (f / fpb) ** 2)
    La, Lb = 0.5 * W2 - da, 0.5 * W2 - db
    r = np.sqrt(za * zb) / z2
    q = f ** 2 / fpa / fpb
    d2 = np.sqrt(Da * Db) * (0.5 - r * (0.05 + 0.7 * np.exp(-1.6 * r) + 0.25 * r * q - 0.17 * np.log(r)))
    L2 = 0.5 * max(Wa, Wb) - d2
    Ta2 = max(1 - np.pi * (f / fpa) ** 2 * ((za / z2) ** 2 / 12 + (0.5 - d2 / Da) ** 2), 1e-30)
    Tb2 = max(1 - np.pi * (f / fpb) ** 2 * ((zb / z2) ** 2 / 12 + (0.5 - d2 / Db) ** 2), 1e-30)
    Bt = (5.5 * np.sqrt(Da * Db / lda / ldb) * (er + 2) / er / z2 / np.sqrt(Ta2 * Tb2) * np.sqrt(da * db) / D2
          * (1 + 0.9 * np.log(r) + 4.5 * r * q - 4.4 * np.exp(-1.3 * r) - 20 * (z2 / ETA0) ** 2))
    n1 = Ta2 * (1 + 1 / Tb2 + 1j * Bt * z0)
    n2 = Tb2 * (1 + 1 / Ta2 + 1j * Bt * z0)
    n3 = 1 / Ta2 + 1 / Tb2 + 1j * Bt * z0
    S = np.zeros((3, 3), complex)
    S[0, 0], S[1, 1], S[2, 2] = (1 - n1) / (1 + n1), (1 - n2) / (1 + n2), (1 - n3) / (1 + n3)
    S[0, 2] = S[2, 0] = 2 * np.sqrt(Ta2) / (1 + n1)
    S[1, 2] = S[2, 1] = 2 * np.sqrt(Tb2) / (1 + n2)
    S[0, 1] = S[1, 0] = 2 / (np.sqrt(Ta2 * Tb2) * (1 + 1j * Bt * z0) + np.sqrt(Ta2 / Tb2) + np.sqrt(Tb2 / Ta2))
    # inner junction S is referenced to z0 at the shifted planes; add the line sections (z0 ~ line Z here)
    ph = np.exp(-1j * 2 * np.pi * f / C0 * np.array([La * np.sqrt(ea), Lb * np.sqrt(eb), L2 * np.sqrt(e2)]))
    P = np.diag(ph)
    return P @ S @ P, dict(La=La, Lb=Lb, L2=L2, da=da, d2=d2, Ta2=Ta2, Bt=Bt, fpa=fpa)


# ================================================================== report
def main():
    boards = {
        "2-layer 1.6 mm (h 1.51 mm, er 4.5)": (1.51e-3, 4.5),
        "JLC04161H-7628 (h 0.2104 mm, er 4.4)": (0.2104e-3, 4.4),
    }
    freqs = [0.433e9, 0.915e9, 2.45e9, 5.8e9]
    print("=" * 100)
    print("1. 50-ohm line widths (t = 0, H-J) and open-end length extensions")
    W50 = {}
    for name, (h, er) in boards.items():
        W = width_for(50.0, lambda w: ms_hj(w, h, er, 0.0)[0])
        W50[name] = W
        z, ee = line(W, h, er)
        dk, dh, d4 = oe_kjk(W, h, er), oe_hammerstad81(W, h, er), oe_hb0412(W, h, er)
        print(f"  {name}: W50 = {W*1e3:.3f} mm (u = {W/h:.3f}), Z = {z:.2f} ohm, eeff = {ee:.3f}")
        print(f"     dl: KJK {dk*1e3:.4f} mm ({dk/h:.4f} h), Hammerstad-81 {dh*1e3:.4f} ({dh/h:.4f} h), "
              f"0.412-form {d4*1e3:.4f} ({d4/h:.4f} h); C_end(KJK) = {c_end(dk, W, h, er)*1e15:.1f} fF")
        for f in freqs:
            dkf = oe_kjk(W, h, er, f)
            print(f"       f = {f/1e9:5.3f} GHz: KJK(dispersive) dl = {dkf*1e3:.4f} mm, "
                  f"C_end = {c_end(dkf, W, h, er, f)*1e15:.1f} fF, |Y| = {2*np.pi*f*c_end(dkf, W, h, er, f)*1e3:.3f} mS")
        check(f"open end models agree within 5 % ({name})",
              max(dk, dh, d4) / min(dk, dh, d4) - 1 < 0.05, f"spread {100*(max(dk,dh,d4)/min(dk,dh,d4)-1):.1f} %")
    # the KB 03 stub page quotes 0.62 mm for 1.6 mm FR-4 (h = 1.6 mm)
    W16 = width_for(50.0, lambda w: ms_hj(w, 1.6e-3, 4.5, 0.0)[0])
    d16 = oe_hb0412(W16, 1.6e-3, 4.5)
    check("0.412-form reproduces the stub page's 0.62 mm (h = 1.6 mm)", abs(d16 * 1e3 - 0.62) < 0.015,
          f"{d16*1e3:.3f} mm; KJK {oe_kjk(W16, 1.6e-3, 4.5)*1e3:.3f} mm")
    # range sweep of the three open-end models
    print("\n   dl/h vs u (er 4.5):  u   KJK   H81   0.412")
    worst = 0
    for u in (0.1, 0.25, 0.5, 1, 2, 4, 8):
        h = 1e-3
        a, b, c = oe_kjk(u * h, h, 4.5) / h, oe_hammerstad81(u * h, h, 4.5) / h, oe_hb0412(u * h, h, 4.5) / h
        worst = max(worst, max(a, b, c) / min(a, b, c) - 1)
        print(f"      {u:5.2f}  {a:.4f}  {b:.4f}  {c:.4f}")
    check("open-end models within 8 % for 0.1 <= u <= 8 (er 4.5)", worst < 0.08, f"worst spread {100*worst:.1f} %")

    print("\n2. Square corner, 50 % mitre and Douville-James mitre")
    for name, (h, er) in boards.items():
        W = W50[name]
        u = W / h
        Ck, Lk = corner_kjk(W, h, er)
        Cg, Lg = corner_garg_bahl(W, h, er)
        Cm, Lm = mbend50_kjk(W, h, er)
        z, _ = line(W, h, er)
        M = mitre_dj(u)
        print(f"  {name}: u = {u:.3f}; KJK corner C = {Ck*1e15:.1f} fF, L = {Lk*1e12:.1f} pH/arm; "
              f"Garg-Bahl C = {Cg*1e15:.1f} fF, L = {Lg*1e12:.1f} pH/arm; 50 % mitre C = {Cm*1e15:.1f} fF, "
              f"L = {Lm*1e12:.1f} pH/arm; optimum mitre (D-J) M = {100*M:.1f} %")
        for f in freqs:
            sk = 20 * np.log10(abs(s11_tee_network(f, Lk, Ck, z)))
            sg = 20 * np.log10(abs(s11_tee_network(f, Lg, Cg, z)))
            sm = 20 * np.log10(abs(s11_tee_network(f, Lm, Cm, z)))
            print(f"     f = {f/1e9:5.3f} GHz: |S11| corner KJK {sk:6.1f} dB, Garg-Bahl {sg:6.1f} dB, 50 % mitre KJK {sm:6.1f} dB")
    check("D-J optimum mitre at u = 0.25 is 98.4 % (Wikipedia check value)", abs(100 * mitre_dj(0.25) - 98.4) < 0.1,
          f"{100*mitre_dj(0.25):.2f} %")
    check("D-J optimum mitre tends to 52 % for wide lines", abs(mitre_dj(10) - 0.52) < 1e-4)
    Ck, Lk = corner_kjk(2.80e-3, 1.51e-3, 4.5)
    Cg, Lg = corner_garg_bahl(2.80e-3, 1.51e-3, 4.5)
    check("KJK and Garg-Bahl corner capacitances agree within 25 % (2-layer 50 ohm)", abs(Ck / Cg - 1) < 0.25,
          f"KJK {Ck*1e15:.0f} fF vs G-B {Cg*1e15:.0f} fF")

    print("\n3. Step in width (50 ohm -> 2x width and 50 ohm -> 0.5x width), Gupta et al.")
    for name, (h, er) in boards.items():
        W = W50[name]
        for W1, W2, lab in ((2 * W, W, "2W -> W"), (W, W / 2, "W -> W/2")):
            cs, l1, l2 = step_gupta(W1, W2, h, er)
            z1, _ = line(W1, h, er)
            z2, _ = line(W2, h, er)
            print(f"  {name} {lab}: Z {z1:.1f} -> {z2:.1f} ohm; C = {cs*1e15:.1f} fF, L1 = {l1*1e12:.1f} pH, "
                  f"L2 = {l2*1e12:.1f} pH; at 2.45 GHz wC*Z = {2*np.pi*2.45e9*cs*50:.4f}, wL/Z = {2*np.pi*2.45e9*(l1+l2)/50:.4f}")

    print("\n4. Gaps (series capacitor / DC block) 50-ohm lines")
    for name, (h, er) in boards.items():
        W = W50[name]
        z, _ = line(W, h, er)
        for s in (0.1e-3, 0.2e-3, 0.5e-3):
            cs, cp1, cp2 = gap_kirschning(W, W, s, h, er, 2.45e9)
            S = s_gap(2.45e9, cs, cp1, cp2, z)
            print(f"  {name} s = {s*1e3:.2f} mm: Cs = {cs*1e15:.2f} fF, Cp = {cp1*1e15:.2f} fF; |S21| at 2.45 GHz "
                  f"= {20*np.log10(abs(S[1,0])):.1f} dB")
    cs1, *_ = gap_kirschning(2.8e-3, 2.8e-3, 0.1e-3, 1.51e-3, 4.5, 1e9)
    cs2, *_ = gap_kirschning(2.8e-3, 2.8e-3, 0.5e-3, 1.51e-3, 4.5, 1e9)
    check("gap series C falls with spacing", cs1 > cs2)
    check("a 0.2 mm gap is a poor DC block at 915 MHz on 2-layer FR-4 (|S21| < -10 dB)",
          20 * np.log10(abs(s_gap(0.915e9, *gap_kirschning(2.8e-3, 2.8e-3, 0.2e-3, 1.51e-3, 4.5, 0.915e9),
                                  50.0)[1, 0])) < -10)

    print("\n5. Via to ground (Goldfarb-Pucel)")
    for h, d in ((1.6e-3, 0.3e-3), (1.51e-3, 0.3e-3), (0.2104e-3, 0.3e-3), (0.2104e-3, 0.2e-3)):
        L = via_gp(h, d / 2)
        print(f"  h = {h*1e3:.3f} mm, drill {d*1e3:.2f} mm: L = {L*1e12:.1f} pH, X(915 MHz) = {2*np.pi*0.915e9*L:.3f} ohm, "
              f"X(2.45 GHz) = {2*np.pi*2.45e9*L:.3f} ohm")
    check("Goldfarb-Pucel matches 04 page (1.6 mm, 0.3 mm: 0.54 nH)", abs(via_gp(1.6e-3, 0.15e-3) * 1e9 - 0.54) < 0.01,
          f"{via_gp(1.6e-3, 0.15e-3)*1e9:.3f} nH")

    print("\n6. Symmetric 50-ohm T-junction (Hammerstad 1981)")
    for name, (h, er) in boards.items():
        W = W50[name]
        for f in (0.915e9, 2.45e9, 5.8e9):
            S, p = tee_hammerstad(W, W, W, h, er, f)
            print(f"  {name} f = {f/1e9:5.3f} GHz: |S11| {20*np.log10(abs(S[0,0])):6.2f} dB (ideal -9.54), "
                  f"|S33| {20*np.log10(abs(S[2,2])):6.2f} dB, |S13| {20*np.log10(abs(S[0,2])):6.2f} dB, "
                  f"d_main = {p['da']*1e3:.3f} mm, d_side = {p['d2']*1e3:.3f} mm, Bt*Z0 = {p['Bt']*50:.4f}, "
                  f"f_p = {p['fpa']/1e9:.1f} GHz")
    S, _ = tee_hammerstad(0.4e-3, 0.4e-3, 0.4e-3, 0.2104e-3, 4.4, 0.915e9)
    check("thin-board tee at 915 MHz is near-ideal (|S11| within 0.3 dB of -9.54)",
          abs(20 * np.log10(abs(S[0, 0])) + 9.54) < 0.3, f"{20*np.log10(abs(S[0,0])):.2f} dB")
    # energy conservation of the lossless model
    S, _ = tee_hammerstad(2.8e-3, 2.8e-3, 2.8e-3, 1.51e-3, 4.5, 2.45e9)
    check("Hammerstad tee model is lossless (S^H S = I within 1e-9)",
          np.allclose(S.conj().T @ S, np.eye(3), atol=1e-9))

    # ------------------------------------------------------------ openEMS comparison
    npz = os.path.join(HERE, "data", "e11_openems_discontinuities.npz")
    print("\n7. openEMS comparison (e11_discontinuities_openems.py)")
    if not os.path.exists(npz):
        print("   (no openEMS results yet — run the openEMS script first)")
    else:
        D = np.load(npz)
        h, er = 1.51e-3, 4.5
        for W, rds in ((2.80e-3, (30, 45)), (0.75e-3, (45,))):
            for rd in rds:
                key = f"open_W{W*1e3:.2f}_r{rd}"
                if key + "_f" not in D:
                    continue
                f, dl = D[key + "_f"], D[key + "_dl"]
                print(f"   open end W = {W*1e3:.2f} mm, mesh lambda/{rd}:")
                for f0 in (0.915e9, 2.45e9, 4.0e9, 5.8e9):
                    i = int(np.argmin(abs(f - f0)))
                    kj = oe_kjk(W, h, er, f[i]) * 1e3
                    print(f"      f = {f[i]/1e9:5.3f} GHz: openEMS dl = {dl[i]:.4f} mm, KJK {kj:.4f} mm "
                          f"({100*(dl[i]/kj-1):+.1f} %), H81 {oe_hammerstad81(W, h, er)*1e3:.4f}, "
                          f"0.412 {oe_hb0412(W, h, er)*1e3:.4f}; |G| = {D[key+'_mag'][i]:.4f}")
            key = f"open_W{W*1e3:.2f}_r45"
            if key + "_f" in D:
                f, dl = D[key + "_f"], D[key + "_dl"]
                band = (f > 1.0e9) & (f < 5.0e9)
                kj = np.array([oe_kjk(W, h, er, x) * 1e3 for x in f[band]])
                err = np.mean(dl[band] / kj - 1)
                check(f"openEMS open-end dl within 10 % of KJK, 1-5 GHz (W = {W*1e3:.2f} mm)", abs(err) < 0.10,
                      f"mean deviation {100*err:+.1f} %")
        if "open_W2.80_r30_f" in D and "open_W2.80_r45_f" in D:
            f = D["open_W2.80_r45_f"]
            band = (f > 1.0e9) & (f < 5.0e9)
            c = np.mean(D["open_W2.80_r30_dl"][band] / D["open_W2.80_r45_dl"][band] - 1)
            check("openEMS open-end dl mesh convergence < 5 %", abs(c) < 0.05, f"coarse vs fine {100*c:+.1f} %")
        W = 2.80e-3
        z, _ = line(W, h, er)
        Ck, Lk = corner_kjk(W, h, er)
        Cg, Lg = corner_garg_bahl(W, h, er)
        Cm, Lm = mbend50_kjk(W, h, er)
        for tag in ("sq_r30", "sq", "m50", "mDJ", "m75"):
            if f"bend_{tag}_f" not in D:
                continue
            f, s11 = D[f"bend_{tag}_f"], D[f"bend_{tag}_s11"]
            print(f"   bend {tag}:")
            for f0 in (0.915e9, 2.45e9, 4.0e9, 5.8e9):
                i = int(np.argmin(abs(f - f0)))
                mk = 20 * np.log10(abs(s11_tee_network(f[i], Lk, Ck, z)))
                mg = 20 * np.log10(abs(s11_tee_network(f[i], Lg, Cg, z)))
                mm = 20 * np.log10(abs(s11_tee_network(f[i], Lm, Cm, z)))
                print(f"      f = {f[i]/1e9:5.3f} GHz: openEMS |S11| = {20*np.log10(abs(s11[i])):6.1f} dB; "
                      f"models: corner KJK {mk:6.1f}, Garg-Bahl {mg:6.1f}, 50 % mitre KJK {mm:6.1f} dB")
        if "bend_sq_f" in D:
            f, s11 = D["bend_sq_f"], D["bend_sq_s11"]
            band = (f > 1.0e9) & (f < 6.0e9)
            dk = 20 * np.log10(abs(s11[band])) - 20 * np.log10(abs(s11_tee_network(f[band], Lk, Ck, z)))
            check("openEMS square-bend |S11| within 3 dB of KJK corner model, 1-6 GHz", np.max(abs(dk)) < 3,
                  f"max deviation {np.max(abs(dk)):.1f} dB")
        if "bend_mDJ_f" in D:
            f, s11 = D["bend_mDJ_f"], D["bend_mDJ_s11"]
            band = f <= 4.0e9
            check("openEMS D-J-mitred bend |S11| < -25 dB up to 4 GHz", np.max(20 * np.log10(abs(s11[band]))) < -25,
                  f"max {np.max(20*np.log10(abs(s11[band]))):.1f} dB")
            if "bend_sq_f" in D:
                i = int(np.argmin(abs(f - 2.45e9)))
                imp = 20 * np.log10(abs(D["bend_sq_s11"][i])) - 20 * np.log10(abs(s11[i]))
                check("optimum mitre improves |S11| by > 10 dB at 2.45 GHz", imp > 10, f"{imp:.1f} dB")
    print("\nSummary:", sum(r[1] for r in RESULTS), "/", len(RESULTS), "checks passed")


if __name__ == "__main__":
    main()
