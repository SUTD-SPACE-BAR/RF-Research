#!/usr/bin/env python3
"""ant2_qa.py -- numbers for the forum Q&A additions to existing kb/08-antennas pages (W5-E2).

Pre-registered expectations (written before the first run):
 a. Conductor loss of a 433 MHz lambda/2 dipole (2 mm wire): Cu/Al/brass > 99 % efficient, stainless ~97-99 %,
    conductive PLA (rho ~ 0.15 ohm m) essentially non-radiating; at 7 MHz all metals > 95 % except steel.
 b. Tip voltage (transmission-line estimate V ~ I0 Z_a): ~100 V peak for 2 W at 433 MHz, ~1-2 kV for 100 W HF.
 c. A 2.45 GHz quarter-wave monopole (30.6 mm) used at 915 MHz: R ~ 4-6 ohm, X ~ -200..-400 ohm -> mismatch
    loss > 6 dB; a 915 MHz whip at 2.45 GHz (~0.67 lambda): not matched (|Gamma| > 0.5).
 d. Dipole parallel to a large conducting sheet at spacing s: R_rad drops roughly as (k s)^2 for s << lambda/4;
    at s = lambda/50 R < 10 ohm (most of the power then lost to any series resistance) and the resonance moves.
 e. Bending the outer 30 mm of each arm of a 433 MHz dipole by 90 deg raises the resonance by only a few %
    (the bent part still counts, but less than straight).
 f. Series-RLC fit of a 433 MHz dipole near resonance: R ~ 72 ohm, L ~ hundreds of nH, C ~ 0.3-0.5 pF, Q ~ 8-12.
 g. HT stubby (15 cm loaded) vs lambda/4 (49 cm) at 146 MHz: stubby several dB worse (coil loss).
 h. Mag-mount: base capacitance of order 100-500 pF; reactance few ohm at VHF/UHF, tens of ohm at 27 MHz.
 i. Far-field harvesting: 1 W EIRP at 915 MHz, 10 m, 2 dBi -> ~ -20 dBm available; ambient -40..-60 dBm.
Run: python3 tools/verify/ant2_qa.py      (~1 min)
"""
import os
import sys

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ant_mom_wire import C0, Wire, solve, dipole, resonant_length     # noqa: E402
import ant_mom_general as mg                                          # noqa: E402

MU0 = 4e-7 * np.pi
EPS0 = 8.854187817e-12
ETA0 = 376.730313
ok = True


def check(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(f"[{'PASS' if cond else 'MISS'}] {name} {detail}")


print("=== a. Conductor material: loss of a resonant half-wave dipole (sinusoidal current) ===")
# R_loss referred to the feed (current max) = R' * L / 2, R' = Rs / (2 pi a) (skin-limited) or rho/(pi a^2) (DC-limited)
mats = [("copper", 5.8e7, 1.0), ("aluminium", 3.5e7, 1.0), ("brass", 1.5e7, 1.0), ("stainless 304", 1.4e6, 1.0),
        ("mild steel (mu_r ~ 100 assumed)", 1.0e7, 100.0), ("copper-clad steel (Cu skin)", 5.8e7, 1.0),
        ("conductive PLA (rho 0.15 ohm m)", 1 / 0.15, 1.0), ("high-conductivity filament (rho 6e-5 ohm m)", 1 / 6e-5, 1.0)]
for f, a in ((433e6, 1e-3), (7.1e6, 1e-3)):
    lam = C0 / f
    L = 0.475 * lam
    print(f"  f = {f/1e6:.1f} MHz, wire diameter {2*a*1e3:.0f} mm, L = {L:.3f} m:")
    for name, sig, mur in mats:
        delta = np.sqrt(2 / (2 * np.pi * f * MU0 * mur * sig))
        if delta < a / 3:
            Rp = np.sqrt(np.pi * f * MU0 * mur / sig) / (2 * np.pi * a)
        else:
            Rp = 1 / (sig * np.pi * a * a)          # current fills the wire (DC-like)
        Rl = Rp * L / 2
        eff = 72 / (72 + Rl)
        print(f"    {name:42s}: skin depth {delta*1e6:9.1f} um, R_loss {Rl:9.3g} ohm, efficiency {100*eff:6.2f} % "
              f"({10*np.log10(eff):6.2f} dB)")
        if f > 1e8 and name == "copper":
            e_cu = eff
        if f > 1e8 and name.startswith("conductive PLA"):
            e_pla = eff
check("433 MHz copper dipole > 99 % efficient", e_cu > 0.99, f"({100*e_cu:.2f} %)")
check("conductive-PLA dipole < 1 % efficient", e_pla < 0.01, f"({100*e_pla:.3f} %)")
print("  resonant LENGTH depends on diameter/insulation, not on the metal (current is on the surface for all metals)")

print("\n=== b. Tip voltage (thin-wire transmission-line estimate V_tip ~ I0 * Z_a, Z_a = 120 [ln(L/2a) - 1]) ===")
for (desc, P, f, a, R) in (("433 MHz dipole, 2 W, 2 mm wire", 2.0, 433e6, 1e-3, 72),
                           ("433 MHz dipole, 0.1 W", 0.1, 433e6, 1e-3, 72),
                           ("14 MHz dipole, 100 W, 2 mm wire", 100.0, 14.2e6, 1e-3, 72),
                           ("14 MHz dipole, 1500 W", 1500.0, 14.2e6, 1e-3, 72)):
    lam = C0 / f
    L = 0.475 * lam
    I0 = np.sqrt(2 * P / R)
    Za = 120 * (np.log(L / (2 * a)) - 1)
    print(f"  {desc:36s}: I0 = {I0:5.2f} A peak, Z_a = {Za:5.0f} ohm -> tip ~ {I0*Za:6.0f} V peak (vs centre)")
for P, R in ((100.0, 2500.0), (10.0, 2500.0)):
    print(f"  EFHW feed point, {P:.0f} W into {R:.0f} ohm: V = sqrt(2 P R) = {np.sqrt(2*P*R):.0f} V peak")

print("\n=== c. Using an antenna on the wrong band (monopole over a large ground; MoM dipole/2) ===")


def mono(h, f, a=0.5e-3, nseg=40):
    s = dipole(f, 2 * h, a, nseg)
    return s["Zin"][0] / 2


for (desc, h, f) in (("2.45 GHz lambda/4 (29.3 mm) at 2.45 GHz", 0.0293, 2.45e9),
                     ("2.45 GHz lambda/4 (29.3 mm) at 915 MHz", 0.0293, 915e6),
                     ("2.45 GHz lambda/4 (29.3 mm) at 433 MHz", 0.0293, 433e6),
                     ("915 MHz lambda/4 (78 mm) at 915 MHz", 0.078, 915e6),
                     ("915 MHz lambda/4 (78 mm) at 2.45 GHz", 0.078, 2.45e9),
                     ("433 MHz lambda/4 (164 mm) at 915 MHz", 0.164, 915e6),
                     ("433 MHz lambda/4 (164 mm) at 868 MHz", 0.164, 868e6)):
    z = mono(h, f)
    G = abs((z - 50) / (z + 50))
    ml = -10 * np.log10(1 - G * G)
    print(f"  {desc:44s}: Z = {z.real:7.1f}{z.imag:+8.1f}j ohm, |Gamma| = {G:.3f}, mismatch loss {ml:5.1f} dB")
    if "at 915 MHz" in desc and desc.startswith("2.45"):
        ml_24_915 = ml
check("2.45 GHz whip at 915 MHz: mismatch loss > 6 dB", ml_24_915 > 6, f"({ml_24_915:.1f} dB)")

print("\n=== d. Half-wave dipole parallel to a large conducting sheet at spacing s (image = antiphase dipole) ===")
f = 433e6
lam = C0 / f
a = 1e-3
Lr = resonant_length(f, a) * lam
for s_l in (0.25, 0.125, 0.1, 0.05, 0.02, 0.01):
    d = 2 * s_l * lam
    nseg = 40
    sol = solve([Wire(0, 0, -Lr / 2, Lr / 2, a, nseg), Wire(d, 0, -Lr / 2, Lr / 2, a, nseg)],
                [(0, nseg // 2, 1.0), (1, nseg // 2, -1.0)], f)
    z = sol["Zin"][0]
    # efficiency with a fixed 2-ohm series loss (connector + matching + conductor), illustrative
    eff = z.real / (z.real + 2.0)
    print(f"  s = {s_l:5.3f} lambda ({s_l*lam*1e3:5.1f} mm at 433 MHz): Z = {z.real:6.2f}{z.imag:+7.1f}j ohm "
          f"(free space 72 ohm); with 2 ohm of loss: efficiency {100*eff:5.1f} %")
    if abs(s_l - 0.02) < 1e-9:
        R002 = z.real
check("dipole at lambda/50 from metal: R < 10 ohm", R002 < 10, f"({R002:.1f} ohm)")

print("\n=== e. Bent dipole tips (433 MHz, 2 mm wire, total wire length kept) ===")
Lw = 0.328


def arm_points(sgn, tip, mode, n1=16):
    """polyline of one arm (z > 0 for sgn = +1). mode: 'straight', '90', '45', 'fold10' (folded back at 10 mm)."""
    straight = Lw / 2 - tip
    p = [[0, 0, sgn * straight * t] for t in np.linspace(0, 1, n1 + 1)]
    ds = straight / n1
    if mode in ("90", "45"):
        ang = np.radians(float(mode))
        n2 = max(3, int(round(tip / ds)))
        for t in np.linspace(0, 1, n2 + 1)[1:]:
            p.append([tip * np.sin(ang) * t, 0, sgn * (straight + tip * np.cos(ang) * t)])
    elif mode == "fold10":
        g = 0.010
        for t in np.linspace(0, 1, 3)[1:]:
            p.append([g * t, 0, sgn * straight])
        back = tip - g
        n2 = max(3, int(round(back / ds)))
        for t in np.linspace(0, 1, n2 + 1)[1:]:
            p.append([g, 0, sgn * (straight - back * t)])
    return np.array(p)


def bent(f, tip, mode):
    st = mg.Structure()
    for sgn in (1, -1):
        st.add_polyline(arm_points(sgn, tip, mode), 1e-3)
    st.build()
    b = st.basis_at_point([0, 0, 0])
    return mg.solve(st, f, [(b, 1.0)])["Zin"][0]


def fres(tip, mode):
    g = lambda f: bent(f, tip, mode).imag
    return brentq(g, 380e6, 560e6, xtol=1e4)


f0 = fres(0.0, "straight")
print(f"  straight 328 mm (this solver): resonance {f0/1e6:.1f} MHz")
for tip, mode, desc in ((0.03, "90", "outer 30 mm bent 90 deg"), (0.03, "45", "outer 30 mm bent 45 deg"),
                        (0.06, "90", "outer 60 mm bent 90 deg"), (0.03, "fold10", "outer 30 mm folded back (10 mm gap)")):
    fr = fres(tip, mode)
    print(f"  {desc:38s}: resonance {fr/1e6:.1f} MHz ({100*(fr/f0-1):+.1f} %)")
    if tip == 0.03 and mode == "90":
        sh90 = fr / f0 - 1
check("30 mm tips bent 90 deg: resonance shift < 6 %", 0 < sh90 < 0.06, f"({100*sh90:+.1f} %)")

print("\n=== f. Series-RLC equivalent of a 433 MHz dipole near resonance (MoM) ===")
L_d = resonant_length(433e6, 1e-3) * C0 / 433e6
w0 = 2 * np.pi * 433e6
fs = np.array([0.98, 1.0, 1.02]) * 433e6
zs = [dipole(x, L_d, 1e-3)["Zin"][0] for x in fs]
dXdw = (zs[2].imag - zs[0].imag) / (2 * np.pi * (fs[2] - fs[0]))
Ls = dXdw / 2
Cs = 1 / (w0 ** 2 * Ls)
Q = w0 * Ls / zs[1].real
print(f"  resonant length {L_d*1e3:.1f} mm: R = {zs[1].real:.1f} ohm, L_s = {Ls*1e9:.0f} nH, C_s = {Cs*1e12:.3f} pF, "
      f"Q = {Q:.1f} -> VSWR-2 (to R) bandwidth ~ 1/(Q sqrt2) = {100/(Q*np.sqrt(2)):.1f} %")
for fr in (0.9, 1.1):
    z = dipole(433e6 * fr, L_d, 1e-3)["Zin"][0]
    zr = zs[1].real + 1j * (2 * np.pi * 433e6 * fr * Ls - 1 / (2 * np.pi * 433e6 * fr * Cs))
    print(f"    check at {fr:.1f} f0: MoM {z.real:.1f}{z.imag:+.1f}j vs RLC {zr.real:.1f}{zr.imag:+.1f}j ohm")
check("dipole Q in 6-14 (pre-registered; X-slope only)", 6 < Q < 14, f"({Q:.1f})")
dZ = (zs[2] - zs[0]) / (2 * np.pi * (fs[2] - fs[0]))
QZ = w0 * abs(dZ) / (2 * zs[1].real)
fsw = np.linspace(0.85, 1.15, 121) * 433e6
for R0 in (72.0, 50.0):
    v = []
    for x in fsw:
        z = dipole(x, L_d, 1e-3)["Zin"][0]
        G = abs((z - R0) / (z + R0))
        v.append((1 + G) / (1 - G))
    bnd = fsw[np.array(v) <= 2]
    print(f"  Yaghjian-Best Q_Z (incl. dR/dw) = {QZ:.2f}; MoM VSWR<=2 band re {R0:.0f} ohm: "
          f"{bnd.min()/1e6:.1f}-{bnd.max()/1e6:.1f} MHz = {100*(bnd.max()-bnd.min())/433e6:.1f} %")

print("\n=== g. HT antennas at 146 MHz: 15 cm loaded stubby vs 49 cm lambda/4 (good-ground estimate) ===")
f = 146e6
lam = C0 / f
for h, QL, desc in ((0.15, 50, "15 cm stubby, coil Q 50"), (0.15, 100, "15 cm stubby, coil Q 100"),
                    (0.49, None, "49 cm lambda/4 whip")):
    a = 1e-3
    l = 2 * h
    Rr = 40 * np.pi ** 2 * (h / lam) ** 2 if h < 0.15 * lam else 36.5
    if QL:
        X = 0.5 * 120 * (np.log(l / (2 * a)) - 1) / np.tan(np.pi * l / lam)
        Rc = X / QL
        eff = Rr / (Rr + Rc + 0.2)
        print(f"  {desc:26s}: R_rad {Rr:.2f} ohm, X_C {X:.0f} ohm -> coil {Rc:.1f} ohm, efficiency {100*eff:.0f} % "
              f"({10*np.log10(eff):.1f} dB)")
    else:
        eff = 36.5 / (36.5 + 0.5)
        print(f"  {desc:26s}: R ~ 36.5 ohm (on a large ground), efficiency ~ {100*eff:.0f} %")
print("  (on a real HT the radio body + hand is a small, lossy counterpoise for both, which costs more dB)")

print("\n=== h. Mag-mount base capacitance ===")
for dmm, gap, er in ((90, 0.5e-3, 3.0), (125, 0.5e-3, 3.0), (90, 1.0e-3, 3.0)):
    A = np.pi * (dmm / 2e3) ** 2
    Cm = EPS0 * er * A / gap
    xs = ", ".join(f"{f/1e6:g} MHz: {1/(2*np.pi*f*Cm):.1f} ohm" for f in (27e6, 146e6, 446e6))
    print(f"  base {dmm} mm, {gap*1e3} mm paint+rubber (er {er}): C = {Cm*1e12:.0f} pF; X_C at {xs}")

print("\n=== i. Far-field RF energy harvesting (Friis) ===")
for (P, f, d, G) in ((1.0, 915e6, 10.0, 1.58), (4.0, 915e6, 3.0, 1.58), (1.0, 2.45e9, 1.0, 1.58), (0.2, 2.45e9, 5.0, 1.58)):
    lam = C0 / f
    Pr = P * G * (lam / (4 * np.pi * d)) ** 2
    print(f"  EIRP {P} W at {f/1e9:.3f} GHz, d = {d} m, G_rx {10*np.log10(G):.0f} dBi: P_avail = {10*np.log10(Pr*1e3):6.1f} dBm "
          f"({Pr*1e6:8.2f} uW)")
print("  ambient (cell/TV/Wi-Fi) at typical urban distances: -40 to -60 dBm (0.1-100 nW); rectifier efficiency"
      " falls steeply below ~ -20 dBm")

print("\nALL PASS" if ok else "\nSOME MISSES (see above)")
