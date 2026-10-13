#!/usr/bin/env python3
"""ant2_slot.py -- verification numbers for kb/08-antennas/slot-antennas.md (W5-E2).

Checks (pre-registered expectations in brackets, written before the first run):
 1. Babinet/Booker: Z_slot * Z_dipole = eta^2/4. Ideal lambda/2 dipole 73.08 + j42.52 ohm
    -> complementary slot 363 - j211 ohm  [Balanis-style textbook value 363 - j211].
 2. Resonant strip dipole (own MoM, strip of width w modelled as a wire of radius w/4) for
    w = lambda/200 ... lambda/20 -> resonant length K*lambda/2 and R_res ~ 65-72 ohm
    -> resonant slot R = eta^2/(4 R_res) ~ 490-550 ohm  [Booker 1946: "about 485 ohm"].
 3. Offset-fed slot (sinusoidal slot-voltage model): R(x) = R_c cos^2(k x) from the centre;
    50 ohm point for R_c = 490 ohm at x ~ 0.20 lambda from centre (~0.04 lambda from the end).
    One-sided (cavity-backed) slot: same aperture field radiates into half space -> R_c doubles.
 4. Slotted-waveguide array (WR-90, 10.368 GHz, 16 slots): reproduce W1GHZ ch.7 spreadsheet:
    lambda_g 37.37 mm, spacing 18.69 mm, Stevenson offset 2.13-2.16 mm, Elliott offset 2.35-2.39 mm,
    gain estimate 10.1 dB, beamwidth 9.8 deg.
 5. Array factor: slots at lambda_g/2 with ALTERNATING offsets -> all in phase (broadside max);
    same-side offsets -> alternating phase -> broadside NULL.
Run: python3 tools/verify/ant2_slot.py      (~30 s)
"""
import os
import sys

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ant_mom_wire import C0, dipole, resonant_length   # noqa: E402

ETA0 = 376.730313
ok = True


def check(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(f"[{'PASS' if cond else 'MISS'}] {name} {detail}")


print("=== 1. Babinet / Booker: Z_s = eta^2 / (4 Z_d) ===")
Zd = 73.08 + 42.52j
Zs = ETA0 ** 2 / (4 * Zd)
print(f"  eta^2/4 = {ETA0**2/4:.0f} ohm^2; ideal lambda/2 dipole {Zd} -> slot {Zs.real:.1f} {Zs.imag:+.1f}j ohm")
check("ideal slot impedance ~363 - j211", abs(Zs - (363 - 211j)) < 3)
print("  Note: X_slot has the OPPOSITE sign of X_dipole: a slot longer than resonance is capacitive.")

print("\n=== 2. Resonant strip dipole (MoM) -> resonant slot ===")
f = 2.45e9
lam = C0 / f
rows = []
for w_l in (1 / 200, 1 / 100, 1 / 50):   # wider slots: w/4 > segment/2 breaks the thin-wire kernel
    a = w_l * lam / 4
    Lr = resonant_length(f, a, 0.40, 0.499, nseg=50)
    R = dipole(f, Lr * lam, a, 50)["Zin"][0].real
    Rs = ETA0 ** 2 / (4 * R)
    rows.append((w_l, Lr, R, Rs))
    print(f"  slot width w = lambda/{1/w_l:4.0f} ({w_l*lam*1e3:5.2f} mm at 2.45 GHz): "
          f"resonant length {Lr:.4f} lambda (K = {2*Lr:.3f}, {Lr*lam*1e3:.1f} mm), "
          f"R_dip {R:.1f} ohm -> R_slot {Rs:.0f} ohm")
check("resonant slot R in 470-560 ohm (Booker ~485)", all(470 < r[3] < 560 for r in rows))

print("  impedance of a lambda/50-wide free-space slot vs frequency (Babinet mapping of the MoM strip):")
a = lam / 50 / 4
Lr = [r for r in rows if abs(r[0] - 1 / 50) < 1e-9][0][1] * lam
for fr in (0.90, 0.95, 1.00, 1.05, 1.10):
    zd = dipole(f * fr, Lr, a, 50)["Zin"][0]
    zs = ETA0 ** 2 / (4 * zd)
    print(f"    f/f0 = {fr:.2f}: Z_strip = {zd.real:6.1f}{zd.imag:+7.1f}j  ->  Z_slot = {zs.real:6.1f}{zs.imag:+7.1f}j ohm")

print("\n=== 3. Offset feed along the slot (R = R_c cos^2 kx) ===")
Rc = 490.0
x50 = np.arccos(np.sqrt(50 / Rc)) / (2 * np.pi)
print(f"  two-sided slot, R_c = {Rc:.0f} ohm: 50 ohm at x = {x50:.4f} lambda from centre "
      f"({0.24 - x50:.4f} lambda from the end of a 0.48 lambda slot)")
check("50-ohm offset ~0.20 lambda", 0.19 < x50 < 0.21)
Rc1 = 2 * Rc
x50b = np.arccos(np.sqrt(50 / Rc1)) / (2 * np.pi)
print(f"  one-sided (cavity-backed) slot, R_c ~ {Rc1:.0f} ohm: 50 ohm at x = {x50b:.4f} lambda from centre")

print("\n=== 4. Slotted waveguide array, WR-90, 10.368 GHz, 16 slots (W1GHZ ch.7 example) ===")
f = 10.368e9
lam0 = C0 / f * 1e3
a_wg, b_wg = 22.86, 10.16
lamc = 2 * a_wg
lamg = 1 / np.sqrt(1 / lam0 ** 2 - 1 / lamc ** 2)
N = 16
g = 1.0 / N
G1_st = 2.09 * (lamg / lam0) * (a_wg / b_wg) * np.cos(np.pi * lam0 / (2 * lamg)) ** 2
x_st = a_wg / np.pi * np.arcsin(np.sqrt(g / G1_st))
G1_el = 2.09 * (lamg / lam0) * (a_wg / b_wg) * (np.cos(0.464 * np.pi * lam0 / lamg) - np.cos(0.464 * np.pi)) ** 2
x_el = a_wg / np.pi * np.arcsin(np.sqrt(g / G1_el))
spacing = lamg / 2
gain = 10 * np.log10(N * spacing / lam0)
bw = 50.7 * lam0 / (N * spacing / 2)
print(f"  lambda0 = {lam0:.2f} mm, lambda_c = {lamc:.2f} mm, lambda_g = {lamg:.2f} mm, spacing lambda_g/2 = {spacing:.2f} mm,"
      f" end short lambda_g/4 = {lamg/4:.2f} mm")
print(f"  Stevenson: G1 = {G1_st:.4f}, offset = {x_st:.2f} mm;  Elliott-corrected: G1 = {G1_el:.4f}, offset = {x_el:.2f} mm")
print(f"  gain estimate 10 log(N s / lambda0) = {gain:.1f} dB(i-ish, DK3BA/DG8SG); elevation beamwidth "
      f"50.7 lambda0/(N s /2) = {bw:.1f} deg (as in the W1GHZ sheet: N counts both walls)")
lamg_3e8 = 1 / np.sqrt(1 / (3e8 / f * 1e3) ** 2 - 1 / lamc ** 2)
print(f"  (with c = 3e8 m/s, as the W1GHZ sheet uses: lambda0 = {3e8/f*1e3:.2f} mm, lambda_g = {lamg_3e8:.2f} mm)")
check("lambda_g 37.37 mm (c = 3e8) / 37.33 mm (exact c)", abs(lamg_3e8 - 37.37) < 0.01)
check("Stevenson offset 2.13-2.16 mm", 2.12 < x_st < 2.17, f"({x_st:.3f})")
check("Elliott offset 2.35-2.39 mm", 2.34 < x_el < 2.40, f"({x_el:.3f})")
check("gain 10.1 dB, beamwidth 9.8 deg", abs(gain - 10.1) < 0.1 and abs(bw - 9.8) < 0.15)
# how sensitive is VSWR to slot conductance error? (all N slots equally wrong)
for err in (0.9, 1.1, 1.25):
    y = err * 1.0
    G = (y - 1) / (y + 1)
    print(f"    if every slot conductance is {err:.2f}x design: y_in = {y:.2f} -> VSWR {(1+abs(G))/(1-abs(G)):.2f}")

print("\n=== 5. Array factor of 8 slots along one wall at lambda_g/2 spacing ===")
n = np.arange(8)
z = n * spacing
beta = 2 * np.pi / lamg
k0 = 2 * np.pi / lam0
th = np.radians(np.linspace(-90, 90, 3601))     # angle from broadside
for name, sgn in (("alternating offsets", (-1.0) ** n), ("all on one side", np.ones(8))):
    exc = sgn * np.exp(-1j * beta * z)            # sign of offset flips the slot excitation
    AF = np.abs(np.sum(exc[:, None] * np.exp(1j * k0 * z[:, None] * np.sin(th)[None, :]), 0))
    i0 = np.argmin(np.abs(th))
    peak = np.degrees(th[np.argmax(AF)])
    print(f"  {name:20s}: |AF| at broadside = {AF[i0]:.3f} (max {AF.max():.3f} at {peak:+.1f} deg from broadside)")
exc = ((-1.0) ** n) * np.exp(-1j * beta * z)
AF0 = abs(np.sum(exc))
check("alternating offsets -> broadside max = N", abs(AF0 - 8) < 1e-9)
exc = np.exp(-1j * beta * z)
check("same-side offsets -> broadside null", abs(np.sum(exc)) < 1e-9)

print("\n=== 6. Squint vs frequency of a resonant (standing-wave) vs travelling-wave array ===")
for fr in (10.25e9, 10.368e9, 10.5e9):
    l0 = C0 / fr * 1e3
    lg = 1 / np.sqrt(1 / l0 ** 2 - 1 / lamc ** 2)
    dphi = np.pi - 2 * np.pi * spacing / lg        # extra inter-element phase beyond the 180 deg flip
    s = dphi / (2 * np.pi * spacing / l0)
    print(f"  f = {fr/1e9:.3f} GHz: lambda_g = {lg:.2f} mm, residual phase/element = {np.degrees(dphi):+.1f} deg "
          f"-> beam tilt (end-fed, travelling-wave view) {np.degrees(np.arcsin(np.clip(s,-1,1))):+.1f} deg")
print("  (a centre-fed or short-terminated resonant array keeps the beam broadside but its match degrades instead)")

print("\nALL PASS" if ok else "\nSOME MISSES (see above)")
