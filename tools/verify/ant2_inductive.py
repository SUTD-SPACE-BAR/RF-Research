#!/usr/bin/env python3
"""ant2_inductive.py -- verification numbers for kb/08-antennas/inductive-coupling-rfid-nfc-wpt.md (W5-E2).

Pre-registered expectations (written before the first run):
 1. Maxwell's elliptic-integral mutual inductance of two coaxial circular filaments equals a direct
    numerical Neumann double integral to < 0.1 %.
 2. Self-inductance of a thin circular loop from the Neumann integral between the axis filament and an
    edge filament (R vs R - a) matches mu0 R [ln(8R/a) - 2] to < 1 % for a/R < 0.02.
 3. Resonant two-coil link: numerically optimising the load of a series-series resonant link gives
    eta_max = U^2 / (1 + sqrt(1 + U^2))^2 with U = k sqrt(Q1 Q2), at R_L = R2 sqrt(1 + U^2)  (exact).
 4. Mohan et al. (1999) modified-Wheeler and current-sheet formulas for a square planar spiral agree with an
    own partial-inductance (Neumann) filament calculation within ~5 %.
 5. 13.56 MHz worked example: 45 mm square, 4-turn PCB coil -> L ~ 1.5-1.8 uH, Q ~ 60-150 before damping;
    exact solution of the NXP-style symmetric EMC-filter + C1/C2 match to Rmatch = 30 ohm gives C1, C2 of
    tens to a few hundred pF, within ~20 % of the AN11755 approximate formulas.
 6. Kurs et al. 2007 plausibility: r = 30 cm, 5.25-turn, 3 mm-radius copper helices at ~10 MHz: Q of
    order 10^3 and eta_max(2 m) of order 40 %.
Run: python3 tools/verify/ant2_inductive.py      (~20 s)
"""
import numpy as np
from scipy.integrate import dblquad
from scipy.optimize import minimize_scalar
from scipy.special import ellipe, ellipk

MU0 = 4e-7 * np.pi
C0 = 299792458.0
ETA0 = 376.730313
SIGMA_CU = 5.8e7
ok = True


def check(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(f"[{'PASS' if cond else 'MISS'}] {name} {detail}")


def M_coax(a, b, d):
    """Mutual inductance of coaxial circular filaments, radii a, b, axial separation d (Maxwell)."""
    m = 4 * a * b / ((a + b) ** 2 + d ** 2)          # scipy uses parameter m = k^2
    k = np.sqrt(m)
    return MU0 * np.sqrt(a * b) * ((2 / k - k) * ellipk(m) - 2 / k * ellipe(m))


def M_neumann_coax(a, b, d):
    f = lambda p1, p2: np.cos(p1 - p2) / np.sqrt(a * a + b * b - 2 * a * b * np.cos(p1 - p2) + d * d)
    val, _ = dblquad(f, 0, 2 * np.pi, 0, 2 * np.pi, epsabs=1e-12, epsrel=1e-10)
    return MU0 / (4 * np.pi) * a * b * val


print("=== 1. Maxwell vs Neumann, coaxial loops ===")
for (a, b, d) in ((0.05, 0.05, 0.02), (0.05, 0.03, 0.05), (0.3, 0.3, 2.0)):
    m1, m2 = M_coax(a, b, d), M_neumann_coax(a, b, d)
    print(f"  a={a} b={b} d={d} m: Maxwell {m1*1e9:.4f} nH, Neumann {m2*1e9:.4f} nH")
    check("  agree < 0.1 %", abs(m1 / m2 - 1) < 1e-3)

print("\n=== 2. Self-inductance of a thin loop ===")
for R, a in ((0.05, 0.5e-3), (0.3, 3e-3), (0.02, 0.2e-3)):
    Lneu = M_coax(R, R - a, 0.0)
    Lf = MU0 * R * (np.log(8 * R / a) - 2)
    Ldc = MU0 * R * (np.log(8 * R / a) - 1.75)
    print(f"  R={R*1e3:.0f} mm a={a*1e3:.1f} mm: filament-GMD {Lneu*1e9:.1f} nH, mu0R(ln8R/a-2) {Lf*1e9:.1f} nH "
          f"(HF, surface current), mu0R(ln8R/a-1.75) {Ldc*1e9:.1f} nH (DC)")
    check("  within 1 %", abs(Lneu / Lf - 1) < 0.01)

print("\n=== 3. Coupling k vs distance for two identical 25 mm-radius loops (0.5 mm wire) ===")
R, a = 0.025, 0.5e-3
L1 = MU0 * R * (np.log(8 * R / a) - 2)
for d in (0.005, 0.01, 0.025, 0.05, 0.1):
    k = M_coax(R, R, d) / L1
    approx = R ** 3 / (2 * (R ** 2 + d ** 2) ** 1.5) * np.pi * MU0 * R / L1  # far-ish dipole approx
    print(f"  d = {d*1e3:5.0f} mm (d/R = {d/R:4.1f}): k = {k:.4f}   (dipole approx pi mu0 R^4/(2 L (R^2+d^2)^1.5) = {approx:.4f})")

print("\n=== 4. Max efficiency of a resonant two-coil link (series-series) ===")


def eta_link(RL, w, L1, L2, M, R1, R2):
    # both sides resonant at w: loop 2 current I2 = j w M I1 / (R2 + RL); input Z = R1 + (wM)^2/(R2+RL)
    Zr = (w * M) ** 2 / (R2 + RL)
    return (Zr / (R1 + Zr)) * (RL / (R2 + RL))


w = 2 * np.pi * 13.56e6
for (k, Q1, Q2) in ((0.01, 100, 100), (0.05, 50, 30), (0.2, 30, 30), (0.02, 1000, 1000)):
    L1 = L2 = 1e-6
    R1, R2 = w * L1 / Q1, w * L2 / Q2
    M = k * np.sqrt(L1 * L2)
    res = minimize_scalar(lambda r: -eta_link(r, w, L1, L2, M, R1, R2), bounds=(1e-4, 1e4), method="bounded",
                          options={"xatol": 1e-10})
    U = k * np.sqrt(Q1 * Q2)
    eta_f = U ** 2 / (1 + np.sqrt(1 + U ** 2)) ** 2
    print(f"  k={k}, Q1={Q1}, Q2={Q2}: U={U:.2f}; numeric max {(-res.fun)*100:.3f} % at RL/R2 = {res.x/R2:.3f}; "
          f"formula {eta_f*100:.3f} % at RL/R2 = sqrt(1+U^2) = {np.sqrt(1+U**2):.3f}")
    check("  formula exact", abs(-res.fun - eta_f) < 1e-6 and abs(res.x / R2 - np.sqrt(1 + U ** 2)) < 1e-3)
print("  U needed for 50 % / 80 % / 90 %: ",
      [f"{np.sqrt((4*e)/(1-e)**2):.2f}" for e in (0.5, 0.8, 0.9)], "(U = 2 sqrt(eta)/(1-eta))")

print("\n=== 5. Square planar spiral inductance: Mohan (1999) vs own filament model ===")


def seg_self(l, w):
    """Partial self-inductance of a thin flat strip (length l, width w, zero thickness), Grover/Ruehli approx."""
    return MU0 / (2 * np.pi) * l * (np.log(2 * l / w) + 0.5 + w / (3 * l))


def seg_mutual_parallel(l1, l2, offset, dist):
    """Mutual partial inductance of two parallel filaments of lengths l1, l2 (start offset along the axis),
    perpendicular separation dist.  Closed form via F(x) = x asinh(x/d) - sqrt(x^2 + d^2)."""
    def F(x):
        return x * np.arcsinh(x / dist) - np.sqrt(x * x + dist * dist)
    # filament 1 on [0, l1], filament 2 on [offset, offset + l2]
    s = F(offset + l2) - F(offset) - F(offset + l2 - l1) + F(offset - l1)
    return MU0 / (4 * np.pi) * s


def square_spiral_segments(dout, n, w, s):
    """Returns list of segments (x0, y0, x1, y1) of a square spiral, outer side dout, n turns."""
    segs = []
    p = w + s
    x, y = -dout / 2 + w / 2, -dout / 2 + w / 2
    length = dout - w
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    k = 0
    for t in range(4 * n):
        dx, dy = dirs[t % 4]
        if t >= 3 and t % 2 == 1:
            pass
        L = length - (p if (t >= 3 and (t - 3) % 2 == 0) else 0.0)
        # classic spiral: side lengths shrink by p every second side after the first three
        segs.append((x, y, x + dx * L, y + dy * L))
        x, y = x + dx * L, y + dy * L
        if t >= 3 and (t - 3) % 2 == 0:
            length -= p
        k += 1
    return segs


def spiral_L(segs, w):
    Ltot = 0.0
    for i, (ax0, ay0, ax1, ay1) in enumerate(segs):
        li = np.hypot(ax1 - ax0, ay1 - ay0)
        Ltot += seg_self(li, w)
        ui = np.array([ax1 - ax0, ay1 - ay0]) / li
        for j, (bx0, by0, bx1, by1) in enumerate(segs):
            if j == i:
                continue
            lj = np.hypot(bx1 - bx0, by1 - by0)
            uj = np.array([bx1 - bx0, by1 - by0]) / lj
            dot = ui @ uj
            if abs(abs(dot) - 1) > 1e-9:
                continue                                  # orthogonal segments: zero mutual
            # coordinates along ui axis and perpendicular distance
            pa = np.array([ax0, ay0]); pb0 = np.array([bx0, by0]); pb1 = np.array([bx1, by1])
            t0, t1 = (pb0 - pa) @ ui, (pb1 - pa) @ ui
            perp = abs((pb0 - pa) @ np.array([-ui[1], ui[0]]))
            lo, hi = min(t0, t1), max(t0, t1)
            m = seg_mutual_parallel(li, hi - lo, lo, perp)
            Ltot += np.sign(dot) * m
    return Ltot


def mohan_square(n, dout, din):
    davg = (dout + din) / 2
    rho = (dout - din) / (dout + din)
    Lmw = 2.34 * MU0 * n * n * davg / (1 + 2.75 * rho)
    Lcs = MU0 * n * n * davg * 1.27 / 2 * (np.log(2.07 / rho) + 0.18 * rho + 0.13 * rho * rho)
    return Lmw, Lcs, rho


for (dout, n, w, s) in ((45e-3, 4, 0.5e-3, 0.5e-3), (60e-3, 3, 1.0e-3, 1.0e-3), (30e-3, 6, 0.3e-3, 0.3e-3)):
    din = dout - 2 * (n * w + (n - 1) * s)
    segs = square_spiral_segments(dout, n, w, s)
    Lf = spiral_L(segs, w)
    Lmw, Lcs, rho = mohan_square(n, dout, din)
    print(f"  {dout*1e3:.0f} mm, {n} turns, w=s={w*1e3:.1f} mm (din {din*1e3:.1f} mm, fill {rho:.3f}): "
          f"filament {Lf*1e6:.3f} uH, mod. Wheeler {Lmw*1e6:.3f} uH, current sheet {Lcs*1e6:.3f} uH")
    check("  Mohan within 6 % of filament model", abs(Lmw / Lf - 1) < 0.06 and abs(Lcs / Lf - 1) < 0.06)

print("\n=== 6. Worked 13.56 MHz reader coil ===")
f0 = 13.56e6
w0 = 2 * np.pi * f0
dout, n, wt, sp, t_cu = 45e-3, 4, 0.5e-3, 0.5e-3, 35e-6
din = dout - 2 * (n * wt + (n - 1) * sp)
La = spiral_L(square_spiral_segments(dout, n, wt, sp), wt)
length = sum(np.hypot(s[2] - s[0], s[3] - s[1]) for s in square_spiral_segments(dout, n, wt, sp))
delta = np.sqrt(2 / (w0 * MU0 * SIGMA_CU))
Rdc = length / (SIGMA_CU * wt * t_cu)
# AC: current confined to ~delta at both faces (t ~ 2 delta here) -> use effective thickness min(t, 2 delta)
Rac = length / (SIGMA_CU * wt * min(t_cu, 2 * delta)) * (1 - np.exp(-t_cu / (2 * delta))) ** -1 * 0.5 + Rdc * 0.5
Rprox = 1.5 * Rac                                   # proximity-effect allowance for 0.5 mm spacing (assumed)
Qa = w0 * La / Rprox
Ca = 4e-12                                          # typical parasitic (AN11755 range 3-30 pF)
fsr = 1 / (2 * np.pi * np.sqrt(La * Ca))
A = ((dout + din) / 2) ** 2
Rrad = 31171 * (n * A / (C0 / f0) ** 2) ** 2
print(f"  L = {La*1e6:.3f} uH, trace length {length*1e3:.0f} mm, skin depth {delta*1e6:.1f} um, "
      f"R_dc {Rdc:.2f} ohm, R_ac(skin) {Rac:.2f} ohm, with x1.5 proximity {Rprox:.2f} ohm")
print(f"  X_L = {w0*La:.1f} ohm, Q = {Qa:.0f}, self-resonance with Ca = 4 pF: {fsr/1e6:.0f} MHz; "
      f"R_rad = {Rrad:.2e} ohm -> radiation efficiency {Rrad/Rprox:.1e}")
Qt = 30.0
RQ = 0.5 * (w0 * La / Qt - Rprox)
print(f"  damping to Q = {Qt:.0f}: RQ = 0.5 (wL/Q - Ra) = {RQ:.2f} ohm per side (AN11755 form)")
Rser = Rprox + 2 * RQ
# NXP-style symmetric network, half circuit: source Rmatch/2 -> L0 -> node A (C0 to gnd) -> C1 -> node B
# (C2 to gnd) -> half antenna (La/2 + Rser/2) with 2*Ca to ground.  Solve C1, C2 for Zin = Rmatch/2 at TX.
Rmatch, L0 = 30.0, 160e-9
fr0 = 15.5e6
C0f = 1 / ((2 * np.pi * fr0) ** 2 * L0)
Zh_ant = 1 / (1 / (Rser / 2 + 1j * w0 * La / 2) + 1j * w0 * 2 * Ca)


def zin_half(C1, C2):
    zb = 1 / (1 / Zh_ant + 1j * w0 * C2)
    za = zb + 1 / (1j * w0 * C1)
    za = 1 / (1 / za + 1j * w0 * C0f)
    return za + 1j * w0 * L0


# exact solution (no iteration): required impedance at node A looking toward the antenna
Ya_comb = 1 / (Rmatch / 2 - 1j * w0 * L0)            # (Z_A || C0) + j w L0 = Rmatch/2
Za = 1 / (Ya_comb - 1j * w0 * C0f)
Gh = (1 / Zh_ant).real
Bh = (1 / Zh_ant).imag
Bp = -np.sqrt(Gh / Za.real - Gh ** 2)               # net shunt susceptance after C2 (inductive branch)
C2 = (Bp - Bh) / w0
Zb = 1 / (Gh + 1j * Bp)
C1 = 1 / (w0 * (Zb.imag - Za.imag))
zchk = zin_half(C1, C2)
# AN11755 approximate formulas (5)-(6), with Rtr and Xtr taken as DIFFERENTIAL values
# (Rtr = Rmatch/den, Xtr = 2w[...]/den): this reading reproduces the exact result; reading Rtr as Rmatch/(2 den)
# (as the pdftotext layout of eq. (3) suggests) gives C1, C2 about 30-45 % off.
den = (1 - w0 ** 2 * L0 * C0f) ** 2 + (w0 * Rmatch / 2 * C0f) ** 2
Rtr = Rmatch / den
Xtr = 2 * w0 * (L0 * (1 - w0 ** 2 * L0 * C0f) - Rmatch ** 2 / 4 * C0f) / den
Lpa = La
Rpa = (w0 * La) ** 2 / Rser
Cpa = Ca
C1a = 1 / (w0 * (np.sqrt(Rtr * Rpa / 4) + Xtr / 2))
C2a = 1 / (w0 ** 2 * Lpa / 2) - 1 / (w0 * np.sqrt(Rtr * Rpa / 4)) - 2 * Cpa
C1b = 1 / (w0 * (np.sqrt(Rtr / 2 * Rpa / 4) + Xtr / 2))
C2b = 1 / (w0 ** 2 * Lpa / 2) - 1 / (w0 * np.sqrt(Rtr / 2 * Rpa / 4)) - 2 * Cpa
print(f"  EMC filter L0 = {L0*1e9:.0f} nH, C0 = {C0f*1e12:.0f} pF (f_r0 {fr0/1e6} MHz); target Rmatch = {Rmatch} ohm diff.")
print(f"  half-circuit: Z_A needed = {Za.real:.2f}{Za.imag:+.2f}j ohm; parallel R of half antenna = {1/Gh:.0f} ohm")
print(f"  exact solve: C1 = {C1*1e12:.1f} pF, C2 = {C2*1e12:.1f} pF per side (check Zin_half = {zchk.real:.2f}{zchk.imag:+.2f}j)")
print(f"  AN11755 (5)-(6) with differential Rtr = {Rtr:.2f}, Xtr = {Xtr:.2f} ohm: C1 = {C1a*1e12:.1f} pF, C2 = {C2a*1e12:.1f} pF")
print(f"  same formulas with Rtr halved ({Rtr/2:.2f} ohm): C1 = {C1b*1e12:.1f} pF, C2 = {C2b*1e12:.1f} pF")
check("approx C1 (differential Rtr) within 5 % of exact", abs(C1a / C1 - 1) < 0.05, f"({100*(C1a/C1-1):+.1f} %)")
check("approx C2 (differential Rtr) within 5 % of exact", abs(C2a / C2 - 1) < 0.05, f"({100*(C2a/C2-1):+.1f} %)")
# bandwidth of loaded system
fs = np.linspace(12e6, 15e6, 3001)
zz = []
for ff in fs:
    ww = 2 * np.pi * ff
    zh = 1 / (1 / (Rser / 2 + 1j * ww * La / 2) + 1j * ww * 2 * Ca)
    zb = 1 / (1 / zh + 1j * ww * C2)
    za = zb + 1 / (1j * ww * C1)
    za = 1 / (1 / za + 1j * ww * C0f)
    zz.append(za + 1j * ww * L0)
zz = np.array(zz) * 2
print(f"  differential Zmatch at 13.00/13.56/14.00 MHz: "
      + ", ".join(f"{complex(np.interp(x, fs, zz.real), np.interp(x, fs, zz.imag)):.1f}" for x in (13.0e6, 13.56e6, 14.0e6)))
# field on axis of an equivalent circular loop (same area) for 1 A... use N I
aeq = np.sqrt(A / np.pi)
for Irms in (0.05, 0.1, 0.2):
    for dd in (0.02, 0.04, 0.06):
        H = n * Irms * aeq ** 2 / (2 * (aeq ** 2 + dd ** 2) ** 1.5)
        print(f"    I = {Irms*1e3:3.0f} mA rms, d = {dd*1e3:.0f} mm: H_axis = {H:.2f} A/m"
              f"{'  (>= 1.5 A/m ISO 14443 min)' if H >= 1.5 else ''}")
print(f"  optimum loop radius for max H at distance d: a = sqrt(2) d (d/dA of a^2/(a^2+d^2)^1.5 = 0)")

print("\n=== 7. Near-field boundary lambda/2pi ===")
for ff in (125e3, 134.2e3, 13.56e6, 915e6):
    print(f"  {ff/1e6:9.4f} MHz: lambda/2pi = {C0/ff/(2*np.pi):9.3f} m")

print("\n=== 8. Qi / LF RFID tank numbers ===")
L_A11 = 1 / ((2 * np.pi * 100e3) ** 2 * 400e-9)
print(f"  Qi A11 (TI bq500212A: 400 nF tank, 100 kHz resonance, 110-205 kHz operation): L = {L_A11*1e6:.2f} uH")
for Lr in (0.5e-3, 1e-3, 2.4e-3):
    print(f"  125 kHz: L = {Lr*1e3:.1f} mH needs C = {1/((2*np.pi*125e3)**2*Lr)*1e9:.2f} nF")
# Qi-size coil coupling: two coaxial 20 mm-radius loops, 1 mm wire, air, gap 3-8 mm
Rq, aq = 0.020, 0.5e-3
Lq = MU0 * Rq * (np.log(8 * Rq / aq) - 2)
for gap in (0.003, 0.005, 0.008):
    print(f"  air loops R = 20 mm, gap {gap*1e3:.0f} mm: k = {M_coax(Rq, Rq, gap)/Lq:.3f} "
          "(single-turn filament model; multi-turn spirals and ferrite backing change it)")

print("\n=== 9. Kurs et al. 2007 plausibility (own estimate) ===")
r, nt, aw, h = 0.30, 5.25, 3e-3, 0.20
# Wheeler short-solenoid inductance (inches formula converted): L = r^2 N^2 / (9 r + 10 h) [uH, inches]
r_in, h_in = r / 0.0254, h / 0.0254
Lk = r_in ** 2 * nt ** 2 / (9 * r_in + 10 * h_in) * 1e-6
fk = 9.9e6
wk = 2 * np.pi * fk
dk = np.sqrt(2 / (wk * MU0 * SIGMA_CU))
wire_len = nt * 2 * np.pi * r
Rohm = wire_len / (SIGMA_CU * 2 * np.pi * aw * dk)
lamk = C0 / fk
Rrad_m = 31171 * (nt * np.pi * r ** 2 / lamk ** 2) ** 2           # magnetic-dipole radiation
Qk = wk * Lk / (Rohm + Rrad_m)
print(f"  L (Wheeler) = {Lk*1e6:.1f} uH, X = {wk*Lk:.0f} ohm, R_ohm (skin, no proximity) = {Rohm:.3f} ohm, "
      f"R_rad (magnetic) = {Rrad_m:.4f} ohm -> Q ~ {Qk:.0f}")
print("  (the paper reports measured Q ~ 950; proximity effect and the electric-dipole radiation of a"
      " self-resonant helix, which this estimate omits, bring it down)")
for dist in (1.0, 2.0):
    kk = M_coax(r, r, dist) * nt ** 2 / Lk
    for Q in (950.0, Qk):
        U = kk * Q
        eta = U ** 2 / (1 + np.sqrt(1 + U ** 2)) ** 2
        print(f"  d = {dist} m: k = {kk:.2e}, Q = {Q:.0f}: U = {U:.2f}, eta_max = {100*eta:.0f} %")

print("\n=== 10. NFC Q trade-off: 847.5 kHz subcarrier sidebands and ASK-pause ring-down ===")
fsc = 13.56e6 / 16
for Q in (10, 20, 30, 35, 60, 114):
    att = 1 / np.sqrt(1 + (2 * Q * fsc / 13.56e6) ** 2)
    tau = Q / (np.pi * 13.56e6)
    print(f"  Q = {Q:3d}: sideband at +-{fsc/1e3:.1f} kHz attenuated {20*np.log10(att):6.1f} dB; "
          f"energy ring-down tau = Q/(pi f) = {tau*1e6:.2f} us (106 kbit/s Type A pause ~2-3 us)")

print("\n=== 11. Frequency splitting of two identical coupled resonators ===")
L, C = 1e-6, 1 / ((2 * np.pi * 13.56e6) ** 2 * 1e-6)
for k in (0.005, 0.02, 0.1):
    f_lo, f_hi = 13.56e6 / np.sqrt(1 + k), 13.56e6 / np.sqrt(1 - k)
    print(f"  k = {k}: normal modes at {f_lo/1e6:.3f} and {f_hi/1e6:.3f} MHz (f0/sqrt(1+-k)); "
          f"splitting visible in the transfer response only if k > k_c = 1/sqrt(Q1 Q2) "
          f"(Q = 30: k_c = {1/30:.3f}; Q = 950: k_c = {1/950:.4f})")

print("\n=== 12. Passive UHF RFID forward-link read range (Friis) ===")
lam = C0 / 915e6
for Pth_dBm in (-14, -18, -22):
    for G_tag in (1.0, 1.64):
        Pth = 10 ** (Pth_dBm / 10) * 1e-3
        r = lam / (4 * np.pi) * np.sqrt(4.0 * G_tag * 0.9 / Pth)
        print(f"  EIRP 4 W, tag G = {10*np.log10(G_tag):.1f} dBi, match tau 0.9, chip sensitivity {Pth_dBm} dBm: r = {r:5.1f} m")

print("\n=== 13. 125 kHz reader (a = 40 mm, N = 60, 0.2 A rms) and a 20 mm, 100-turn tag coil ===")
for dd in (0.05, 0.10, 0.15, 0.20):
    H = 60 * 0.2 * 0.04 ** 2 / (2 * (0.04 ** 2 + dd ** 2) ** 1.5)
    Voc = 2 * np.pi * 125e3 * 100 * np.pi * 0.01 ** 2 * MU0 * H
    print(f"  d = {dd*1e3:.0f} mm: H = {H:5.2f} A/m rms, tag open-circuit V = {Voc*1e3:6.1f} mV rms, "
          f"x Q_tag 20 (resonant tank) = {20*Voc:.2f} V rms")

print("\nALL PASS" if ok else "\nSOME MISSES (see above)")
