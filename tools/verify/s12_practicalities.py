#!/usr/bin/env python3
"""
s12_practicalities.py -- W5-S12 (G-08-07): NEC-2 (PyNEC) sweeps for antenna practicalities.
 A. Loading-coil position vs efficiency for a short monopole over a perfect ground:
    (i) 2.4 m HF mobile whip at 7.15 MHz (h = 0.057 lambda), coil Q 100 / 300, ground-loss 0 / 5 ohm;
    (ii) 60 mm 433 MHz whip (h = 0.087 lambda) with a chip-inductor-class coil, Q 50.
    For every coil position the inductance is solved for X_in = 0; efficiency = 1 - (coil + ground loss)/P_in.
 B. Element diameter vs bandwidth: 433 MHz resonant dipole, diameters 0.5-12 mm: resonant length, R, Yaghjian-Best Q_Z,
    VSWR <= 2 bandwidth referred to R_res and to 50 ohm.
 C. Front-to-side (and F/B, F/R) of the KB 3-element and 11-element 433 MHz Yagis.
 D. Two-element Yagi: parasitic as reflector vs director, spacing 0.05-0.30 lambda, length optimised for forward gain.
Run: python3 tools/verify/s12_practicalities.py   (~2-4 min)
"""
import os
import sys
import numpy as np
from scipy.optimize import brentq, minimize_scalar

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import PyNEC                                       # noqa: E402
from ant_yagi import dl6wu_design                  # noqa: E402

C0 = 299792458.0
results, misses = [], []


def say(s=""):
    print(s); results.append(s)


def check(name, cond, detail=""):
    if not cond:
        misses.append(name)
    say(f"[{'PASS' if cond else 'MISS'}] {name} {detail}")


def db(x):
    return 10 * np.log10(np.maximum(x, 1e-30))


# ===================================================================================== A. loading coil position
def whip(fmhz, h, a, nseg, p, Lcoil, Q, Rg, return_all=False):
    """vertical monopole on PEC ground, base feed; coil (L, R = wL/Q) in the segment at fractional height p;
    optional ground-loss resistor Rg in series at the base"""
    c = PyNEC.nec_context(); g = c.get_geometry()
    g.wire(1, nseg, 0, 0, 0, 0, 0, h, a, 1, 1)
    c.geometry_complete(1)
    c.gn_card(1, 0, 0, 0, 0, 0, 0, 0)
    w = 2 * np.pi * fmhz * 1e6
    sc = min(nseg, int(p * nseg) + 1)
    Rc = w * Lcoil / Q
    c.ld_card(0, 1, sc, sc, Rc, Lcoil, 0.0)
    if Rg > 0:
        c.ld_card(0, 1, 1, 1, Rg, 0.0, 0.0)
    c.ex_card(0, 1, 1, 0, 1.0, 0, 0, 0, 0, 0)
    c.fr_card(0, 1, fmhz, 0)
    c.xq_card(0)
    Z = complex(c.get_input_parameters(0).get_impedance()[0])
    I = np.array(c.get_structure_currents(0).get_current())
    Pin = 0.5 * (1.0 / Z).real               # V = 1
    Ploss = 0.5 * abs(I[sc - 1]) ** 2 * Rc + (0.5 * abs(I[0]) ** 2 * Rg if Rg > 0 else 0)
    eta = 1 - Ploss / Pin
    if return_all:
        return Z, eta, I
    return Z, eta


def coil_sweep(fmhz, h, a, nseg, Q, Rg, ps):
    rows = []
    for p in ps:
        def X(Lc):
            return whip(fmhz, h, a, nseg, p, Lc, Q, Rg)[0].imag
        # bracket: from tiny to large inductance
        Ls = np.geomspace(1e-9, 1e-3, 60)
        xs = np.array([X(l) for l in Ls])
        idx = np.where(np.sign(xs[:-1]) != np.sign(xs[1:]))[0]
        if len(idx) == 0:
            rows.append((p, np.nan, np.nan, np.nan)); continue
        i = idx[0]
        Lr = brentq(X, Ls[i], Ls[i + 1], xtol=1e-13, rtol=1e-10)
        Z, eta = whip(fmhz, h, a, nseg, p, Lr, Q, Rg)
        rows.append((p, Lr, Z.real, eta))
    return rows


say("=== A1. 2.4 m mobile whip, 7.15 MHz (h = 0.057 lambda, 8 mm dia), perfect ground; coil solved for X_in = 0 ===")
PS = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)
HFW = {}
for Q, Rg in ((300, 0.0), (100, 0.0), (300, 5.0), (100, 5.0)):
    rows = coil_sweep(7.15, 2.4, 0.004, 30, Q, Rg, PS)
    HFW[(Q, Rg)] = rows
    say(f"  coil Q = {Q}, ground loss {Rg:.0f} ohm:   position (fraction of height): L uH / R_in ohm / efficiency %")
    for (p, L, R, e) in rows:
        say(f"     p = {p:.1f}:  L = {L*1e6:7.2f} uH   R_in = {R:6.2f}   eta = {100*e:5.1f} %  ({db(e):6.2f} dB)")
    best = max(rows, key=lambda r: r[3])
    say(f"     -> best position p = {best[0]:.1f} (eta {100*best[3]:.1f} %); base loading {100*rows[0][3]:.1f} %")
b300 = max(HFW[(300, 0.0)], key=lambda r: r[3]); b100 = max(HFW[(100, 0.0)], key=lambda r: r[3])
check("A1a centre-region loading beats base loading (Q = 100 and 300, no ground loss) and the optimum lies at 0.3-0.7 h",
      b300[3] > HFW[(300, 0.0)][0][3] and b100[3] > HFW[(100, 0.0)][0][3] and 0.3 <= b100[0] <= 0.7,
      f"(Q100 best p = {b100[0]}, Q300 best p = {b300[0]})")
b5 = max(HFW[(100, 5.0)], key=lambda r: r[3])
say(f"  with 5 ohm ground loss, Q = 100: best p = {b5[0]:.1f}, eta {100*b5[3]:.1f} % (no ground loss: {100*b100[3]:.1f} %)")

say("\n=== A2. 60 mm whip at 433.92 MHz (h = 0.087 lambda, 1 mm wire), perfect ground, coil Q = 50 ===")
rows = coil_sweep(433.92, 0.060, 0.0005, 24, 50, 0.0, (0.0, 0.2, 0.4, 0.5, 0.6, 0.8))
for (p, L, R, e) in rows:
    say(f"     p = {p:.1f}:  L = {L*1e9:6.1f} nH   R_in = {R:5.2f} ohm   eta = {100*e:5.1f} %")
rowsQ100 = coil_sweep(433.92, 0.060, 0.0005, 24, 100, 0.0, (0.0,))
say(f"  base loading with Q = 100 (the dipoles-page example 4): L = {rowsQ100[0][1]*1e9:.0f} nH, R_in = {rowsQ100[0][2]:.2f} ohm, "
    f"eta = {100*rowsQ100[0][3]:.1f} % (page hand estimate: 136 nH, ~7 ohm, 43 %)")
check("A2b NEC base-loaded 60 mm whip (Q = 100) within 10 percentage points and 20 % in L of the hand estimate (43 %, 136 nH)",
      abs(100 * rowsQ100[0][3] - 43) < 10 and abs(rowsQ100[0][1] * 1e9 - 136) / 136 < 0.2)


# ===================================================================================== B. diameter vs bandwidth
def dip(fmhz, L, a, nseg, ek):
    c = PyNEC.nec_context(); g = c.get_geometry()
    g.wire(1, nseg, 0, 0, -L / 2, 0, 0, L / 2, a, 1, 1)
    c.geometry_complete(0); c.gn_card(-1, 0, 0, 0, 0, 0, 0, 0)
    if ek:
        c.set_extended_thin_wire_kernel(True)
    c.ex_card(0, 1, nseg // 2 + 1, 0, 1.0, 0, 0, 0, 0, 0)
    c.fr_card(0, 1, fmhz, 0); c.xq_card(0)
    return complex(c.get_input_parameters(0).get_impedance()[0])


say("\n=== B. 433 MHz dipole: element diameter vs resonant length, R, Q and VSWR-2 bandwidth (NEC-2) ===")
say("  dia mm  lambda/d   Omega   L_res mm (K)     R_res   Q_Z    BW(VSWR2 re R_res)   BW(VSWR2 re 50 ohm)")
F0 = 433.0; LAM = C0 / 433e6
BW = {}
for d in (0.5, 1.0, 2.0, 4.0, 6.0, 12.0):
    a = d / 2000
    nseg = 21 if a < 0.003 else 13
    ek = (LAM / 2 / nseg) / a < 8
    Lr = brentq(lambda L: dip(F0, L, a, nseg, ek).imag, 0.40 * LAM, 0.50 * LAM, xtol=1e-7)
    Zr = dip(F0, Lr, a, nseg, ek)
    df = 0.002 * F0
    dZ = (dip(F0 + df, Lr, a, nseg, ek) - dip(F0 - df, Lr, a, nseg, ek)) / (2 * df)
    QZ = F0 * abs(dZ) / (2 * Zr.real)
    fs = np.linspace(0.80 * F0, 1.20 * F0, 161)
    Zs = np.array([dip(f, Lr, a, nseg, ek) for f in fs])
    def bw(R0):
        g = np.abs((Zs - R0) / (Zs + R0)); v = (1 + g) / (1 - g)
        ok = fs[v <= 2.0]
        return (ok.max() - ok.min()) / F0 * 100 if len(ok) else 0.0
    Om = 2 * np.log(Lr / a)
    BW[d] = (Lr, Zr.real, QZ, bw(Zr.real), bw(50.0))
    say(f"  {d:5.1f}   {LAM/(d/1000):7.0f}   {Om:5.1f}   {Lr*1000:6.1f} ({Lr/(LAM/2):.3f})   {Zr.real:5.1f}  {QZ:5.2f}       "
        f"{bw(Zr.real):5.1f} %               {bw(50.0):5.1f} %")
check("B1 2 mm dipole: Q_Z 5-7 and VSWR-2 bandwidth 10-14 % re R_res, 7-10 % re 50 ohm (KB dipoles page: 5.9, 11.8 %, 8.2 %)",
      5 < BW[2.0][2] < 7 and 10 < BW[2.0][3] < 14 and 7 < BW[2.0][4] < 10,
      f"(Q {BW[2.0][2]:.2f}, {BW[2.0][3]:.1f} %, {BW[2.0][4]:.1f} %)")
check("B2 bandwidth rises monotonically with diameter", all(BW[a][3] < BW[b][3] for a, b in ((0.5, 1), (1, 2), (2, 4), (4, 6), (6, 12))))
qs = np.array([BW[d][2] for d in BW]); oms = np.array([2 * np.log(BW[d][0] / (d / 2000)) for d in BW])
fit = np.polyfit(oms, qs, 1)
say(f"  Q_Z vs Omega linear fit: Q ~ {fit[0]:.2f} Omega {fit[1]:+.2f}  (thin-dipole theory: Q grows ~linearly with Omega)")


# ===================================================================================== C. F/S of Yagis
def yagi(fmhz, lens, pos, a, nseg=13, pattern="cuts", feed=1):
    c = PyNEC.nec_context(); g = c.get_geometry()
    for i, (L, x) in enumerate(zip(lens, pos)):
        g.wire(i + 1, nseg, x, -L / 2, 0, x, L / 2, 0, a, 1, 1)
    c.geometry_complete(0); c.gn_card(-1, 0, 0, 0, 0, 0, 0, 0)
    c.ex_card(0, feed + 1, nseg // 2 + 1, 0, 1.0, 0, 0, 0, 0, 0)
    c.fr_card(0, 1, fmhz, 0)
    if pattern is None:
        c.xq_card(0)
        return complex(c.get_input_parameters(0).get_impedance()[0])
    c.rp_card(0, 1, 360, 0, 0, 0, 0, 90.0, 0.0, 0.0, 1.0, 0, 0)        # E-plane (horizontal, contains elements)
    c.rp_card(0, 181, 1, 0, 0, 0, 0, 0.0, 0.0, 1.0, 0.0, 0, 0)         # H-plane, phi = 0 (front, x-z)
    c.rp_card(0, 181, 1, 0, 0, 0, 0, 0.0, 180.0, 1.0, 0.0, 0, 0)       # H-plane, phi = 180 (back)
    gE = np.array(c.get_radiation_pattern(0).get_gain()).ravel()
    gH = np.array(c.get_radiation_pattern(1).get_gain()).ravel()
    gHb = np.array(c.get_radiation_pattern(2).get_gain()).ravel()
    return dict(Z=complex(c.get_input_parameters(0).get_impedance()[0]), gE=gE, gH=gH, gHb=gHb)


def fs_metrics(r):
    gE, gH, gHb = r["gE"], r["gH"], r["gHb"]
    Gf = gE[0]
    FB = Gf - gE[180]
    FR = Gf - max(gE[90:271].max(), gHb.max())                    # worst rear lobe (rear half of both planes)
    FS_E = Gf - max(gE[90], gE[270])                              # side in the element plane (dipole null)
    FS_H = Gf - gH[0]                                             # side = zenith in the H-plane
    return Gf, FB, FR, FS_E, FS_H


say("\n=== C. Front-to-side, front-to-back and front-to-rear of the KB 433 MHz Yagis (horizontal, free space) ===")
lam = LAM
r3 = yagi(433.0, [0.3366, 0.3147, 0.2963], [0.0, 0.088, 0.242], 0.003)
m3 = fs_metrics(r3)
DES = dl6wu_design(2.3, 6e-3 / lam, 6e-3 / lam)
pos = DES["pos"] * lam
base = [DES["refl"] * lam, 0.47 * lam] + list(DES["dirs"] * lam)
def xde(L):
    ll = base.copy(); ll[1] = L
    return yagi(433.0, ll, pos, 0.003, pattern=None).imag
base[1] = brentq(xde, 0.44 * lam, 0.5 * lam, xtol=1e-6)
r11 = yagi(433.0, base, pos, 0.003)
m11 = fs_metrics(r11)
for lab, m, r in (("3-element (242 mm boom)", m3, r3), ("11-element DL6WU (1.72 m boom)", m11, r11)):
    say(f"  {lab}: G = {m[0]:.2f} dBi, F/B = {m[1]:.1f} dB, F/R = {m[2]:.1f} dB, F/S (element plane) = {m[3]:.1f} dB, "
        f"F/S (H-plane, 90 deg up) = {m[4]:.1f} dB, Z = {r['Z']:.1f} ohm")
    say(f"    (element-plane F/S is the dipole-element null: {'> 60' if m[3] > 60 else f'{m[3]:.1f}'} dB)")
check("C1 3-element Yagi reproduces the KB numbers (9.15 dBi, F/B 15 dB) within 0.3 dB / 1.5 dB", abs(m3[0] - 9.15) < 0.3 and abs(m3[1] - 15.0) < 1.5,
      f"({m3[0]:.2f} dBi, {m3[1]:.1f} dB)")
check("C2 element-plane F/S >> H-plane F/S (the dipole element null)", m3[3] > m3[4] + 10 and m11[3] > m11[4] + 10)


# ===================================================================================== D. 2-element reflector vs director
say("\n=== D. Two-element Yagi at 433 MHz (6 mm elements): parasitic as reflector vs director ===")
a = 0.003
L_de = brentq(lambda L: dip(433.0, L, a, 21, False).imag, 0.44 * lam, 0.5 * lam, xtol=1e-7)


def two_el(d_l, Lp, cuts=True):
    c = PyNEC.nec_context(); g = c.get_geometry()
    g.wire(1, 21, 0, -L_de / 2, 0, 0, L_de / 2, 0, a, 1, 1)
    g.wire(2, 21, d_l * lam, -Lp / 2, 0, d_l * lam, Lp / 2, 0, a, 1, 1)
    c.geometry_complete(0); c.gn_card(-1, 0, 0, 0, 0, 0, 0, 0)
    c.ex_card(0, 1, 11, 0, 1.0, 0, 0, 0, 0, 0)
    c.fr_card(0, 1, 433.0, 0)
    c.rp_card(0, 1, 2, 0, 0, 0, 0, 90.0, 0.0, 0.0, 180.0, 0, 0)
    gg = np.array(c.get_radiation_pattern(0).get_gain()).ravel()
    return gg[0], gg[1], complex(c.get_input_parameters(0).get_impedance()[0])    # toward +x (parasitic side), -x


say(f"  driven element resonant alone: {L_de*1000:.1f} mm ({L_de/lam:.4f} lambda)")
say("  spacing   REFLECTOR: Lp/lambda  G dBi  F/B dB  Z_in            |  DIRECTOR: Lp/lambda  G dBi  F/B dB  Z_in")
TWO = {}
for d_l in (0.05, 0.075, 0.10, 0.125, 0.15, 0.20, 0.25, 0.30):
    rr = minimize_scalar(lambda Lp: -two_el(d_l, Lp * lam)[1], bounds=(L_de / lam, 0.56), method="bounded",
                         options={"xatol": 1e-5})
    gr_f, gr_b, zr = two_el(d_l, rr.x * lam)[1], two_el(d_l, rr.x * lam)[0], two_el(d_l, rr.x * lam)[2]
    rd = minimize_scalar(lambda Lp: -two_el(d_l, Lp * lam)[0], bounds=(0.38, L_de / lam), method="bounded",
                         options={"xatol": 1e-5})
    gd_f, gd_b, zd = two_el(d_l, rd.x * lam)
    TWO[d_l] = (rr.x, gr_f, gr_f - gr_b, zr, rd.x, gd_f, gd_f - gd_b, zd)
    say(f"   {d_l:5.3f}        {rr.x:.4f}   {gr_f:5.2f}  {gr_f-gr_b:5.1f}  {zr.real:5.1f}{zr.imag:+6.1f}j      |"
        f"      {rd.x:.4f}   {gd_f:5.2f}  {gd_f-gd_b:5.1f}  {zd.real:5.1f}{zd.imag:+6.1f}j")
gR = max(v[1] for v in TWO.values()); gD = max(v[5] for v in TWO.values())
dR = max(TWO, key=lambda k: TWO[k][1]); dD = max(TWO, key=lambda k: TWO[k][5])
say(f"  best reflector-type: {gR:.2f} dBi at {dR} lambda; best director-type: {gD:.2f} dBi at {dD} lambda")
check("D1 both 2-element types reach 6.5-7.8 dBi; director-type optimum at closer spacing than reflector-type",
      6.5 < gR < 7.8 and 6.5 < gD < 7.8 and dD <= dR, f"(R {gR:.2f} @ {dR}, D {gD:.2f} @ {dD})")

say("\nSUMMARY: " + ("ALL PASS" if not misses else f"{len(misses)} MISS: " + "; ".join(misses)))
with open(os.path.join(HERE, "s12_practicalities_output.txt"), "w") as fh:
    fh.write("\n".join(results) + "\n")
