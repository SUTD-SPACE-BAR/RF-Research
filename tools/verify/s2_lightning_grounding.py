#!/usr/bin/env python3
"""
s2_lightning_grounding.py — numbers behind the lightning, surge and station-grounding section
(gap slice S2, W5-S2; G-19-01).

Used by: kb/19-regulations-safety/lab-safety-esd-high-power.md ("Lightning, surge and station grounding").

What it checks / computes
  1. Electrogeometric striking distance r = 10·I^0.65 (r in m, I in kA) against the IEC 62305 rolling-sphere
     radii 20/30/45/60 m for the minimum currents 3/5/10/16 kA of LPL I–IV (ABB IEC 62305 guide).
  2. Ground-rod resistance: Dwight's formula R = ρ/(2πL)·[ln(4L/a) − 1] cross-checked against an independent
     numerical "average-potential" solution (uniform line current + image in a half-space). Soil values from
     ITU-T K.112 Table B.1. Two rods in parallel (mutual-resistance approximation).
  3. Ground potential rise (GPR) = I·R and the surface potential / step voltage of a hemispherical electrode.
  4. Inductive voltage along a down-conductor or coax shield: partial self-inductance of a straight round
     conductor, V = L·di/dt for IEC 62305-1 steepness values (subsequent stroke 200/150/100 kA/µs, LPL I/II/III–IV).
  5. Magnetically induced voltage in a loop (e.g. launch-controller firing leads) from a nearby stroke.
  6. Quarter-wave shorted-stub arrester: shunt reactance, return loss across 420–450 MHz and at lightning
     frequencies; GDT turn-on voltage vs RF peak voltage of the team's transmitters.

Run:  python3 tools/verify/s2_lightning_grounding.py     (≈ 2 s; ALL PASS expected)
"""
import math
import numpy as np
from scipy import integrate

MU0 = 4e-7 * math.pi * 1.00000000055
FAILS = []


def check(name, got, want, tol):
    ok = abs(got - want) <= tol
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: got {got:.4g}, want {want:.4g} ±{tol:g}")
    if not ok:
        FAILS.append(name)


print("1. Striking distance r = 10 I^0.65 vs IEC 62305 rolling-sphere radii")
for lpl, imin, rs in [("I", 3, 20), ("II", 5, 30), ("III", 10, 45), ("IV", 16, 60)]:
    r = 10 * imin ** 0.65
    check(f"LPL {lpl}: I_min {imin} kA -> r (IEC radii are rounded)", r, rs, 0.06 * rs)
print(f"     median-ish 30 kA stroke: r = {10*30**0.65:.0f} m (a 10 m mast on open ground is well inside this)")


# ------------------------------------------------------------------ 2. ground rods
def dwight(rho, L, a):
    return rho / (2 * math.pi * L) * (math.log(4 * L / a) - 1)


def rod_numeric(rho, L, a, n=400):
    """Average-potential method: rod (length L, radius a) driven into a half-space carries current I uniformly
    along its length; with the image rod the problem is a 2L line source in full space. Potential at the rod
    surface averaged over the rod length, divided by I."""
    I = 1.0
    lam = I / L                                   # A/m leaking per metre (half-space: image doubles)
    zs = (np.arange(n) + 0.5) / n * L             # observation points on rod surface (depth)

    def V(z):
        # line source from -L to +L (rod + image) with density lam, observed at radius a, depth z
        f = lambda zp: 1.0 / math.sqrt(a * a + (z - zp) ** 2)
        val = integrate.quad(f, 0, L, limit=200)[0] + integrate.quad(f, -L, 0, limit=200)[0]
        return rho * lam / (4 * math.pi) * val
    return np.mean([V(z) for z in zs]) / I


print("\n2. Ground-rod resistance: Dwight vs numerical average-potential solution")
for L, d in [(1.2, 0.016), (2.4, 0.016), (3.0, 0.016), (2.4, 0.0127)]:
    rd = dwight(100, L, d / 2)
    rn = rod_numeric(100, L, d / 2, n=120)
    check(f"rod {L} m x {d*1e3:.1f} mm in 100 Ω·m: Dwight {rd:.1f} Ω vs numeric", rn, rd, 0.06 * rd)
print("     rod 2.4 m x 16 mm in K.112 Table B.1 soils:")
for name, rho in [("sea water 1", 1), ("loam/clay ~ 30", 30), ("flat marshy 100", 100), ("hills 200", 200),
                  ("rocky 500", 500), ("city/industrial fill 1000", 1000), ("dry sand 3000", 3000)]:
    print(f"       ρ = {name:26s} Ω·m: R = {dwight(rho, 2.4, 0.008):7.1f} Ω")
R1 = dwight(100, 2.4, 0.008)
for s in (2.4, 4.8, 10):
    R2 = 0.5 * (R1 + 100 / (2 * math.pi * s))
    print(f"       two 2.4 m rods {s:4.1f} m apart in 100 Ω·m: ≈ {R2:5.1f} Ω (one rod {R1:.1f} Ω; ideal half {R1/2:.1f} Ω)")
check("10 Ω target in 100 Ω·m needs several rods (one 2.4 m rod > 30 Ω)", float(R1 > 30), 1.0, 0)

print("\n3. Ground potential rise and step voltage (30 kA stroke, ρ = 100 Ω·m)")
I = 30e3
for R in (10, R1, 100):
    print(f"     earth R = {R:5.1f} Ω -> GPR = I·R = {I*R/1e3:7.0f} kV")
k = 100 * I / (2 * math.pi)                       # hemispherical potential V(r) = ρI/(2πr)
for r in (2, 5, 10, 20, 50):
    vs = k * (1 / r - 1 / (r + 1))
    print(f"     step voltage (1 m stride) at {r:3d} m from the strike point: {vs/1e3:6.2f} kV")
check("step voltage at 10 m (kV)", k * (1 / 10 - 1 / 11) / 1e3, 4.34, 0.02)


# ------------------------------------------------------------------ 4. inductive voltage
def partial_L(l, r):
    return MU0 * l / (2 * math.pi) * (math.log(2 * l / r) - 1)


print("\n4. Inductive voltage along a straight conductor, V = L di/dt")
for l, r, label in [(10, 0.004, "10 m mast/down-conductor, 8 mm"), (10, 0.0036, "10 m of LMR-400-size shield (7.2 mm)"),
                    (3, 0.00163, "3 m of 6 AWG ground wire"), (3, 0.0125, "3 m of 50 mm strap (equiv. radius w/4)")]:
    L = partial_L(l, r)
    print(f"     {label:44s}: L = {L*1e6:5.2f} µH ({L/l*1e6:4.2f} µH/m) -> at 100 kA/µs: {L*1e11/1e3:7.0f} kV;"
          f" at 10 kA/µs: {L*1e10/1e3:6.0f} kV")
check("partial L of 10 m x 8 mm rod (µH)", partial_L(10, 0.004) * 1e6, 15.0, 0.3)

print("\n5. Voltage induced in a loop by a nearby stroke: V = µ0 A (di/dt) / (2π d)")
for A, label in [(50, "100 m firing line, 0.5 m between leads"), (0.5, "same leads twisted (≈ 1 % residual area)"),
                 (2, "1 m x 2 m loop in an av-bay harness / ground-station cable run")]:
    for d in (50, 200):
        for didt in (10e9, 100e9):
            V = MU0 * A * didt / (2 * math.pi * d)
            print(f"     {label:56s} d = {d:3d} m, {didt/1e9:5.0f} kA/µs: {V:8.0f} V")
check("100 m line, 50 m², 200 m away, 10 kA/µs (V)", MU0 * 50 * 10e9 / (2 * math.pi * 200), 500, 1)

print("\n6. Arresters: λ/4 shorted stub and GDT")
Z0, f0 = 50.0, 433.92e6
for f in (1e3, 100e3, 1e6, 420e6, 433.92e6, 450e6, 868e6):
    bl = math.pi / 2 * f / f0
    Zs = 1j * Z0 * math.tan(bl)                   # shorted stub input impedance (lossless)
    if abs(math.cos(bl)) < 1e-9:
        rl = float("inf")
        txt = "open (∞)"
    else:
        Y = 1 / Zs
        G = (-(Y * Z0)) / (2 + Y * Z0)           # shunt admittance across a matched 50 Ω line: Γ = -yZ0/(2+yZ0)
        rl = -20 * math.log10(abs(G)) if abs(G) > 0 else float("inf")
        txt = f"|Z| = {abs(Zs):10.4g} Ω"
    print(f"     f = {f/1e6:10.4f} MHz: stub {txt:22s} return loss {rl:6.1f} dB")
bl = math.pi / 2 * 420e6 / f0
G420 = abs(-(1 / (1j * Z0 * math.tan(bl)) * Z0) / (2 + 1 / (1j * Z0 * math.tan(bl)) * Z0))
check("λ/4 stub (433.92 MHz) return loss at 420 MHz (dB, > 20 required)", -20 * math.log10(G420), 32.0, 0.1)
print("     note: at 868 MHz (2nd harmonic) the stub is a half-wave short -> it also shorts the E22 2nd harmonic,")
print("           but it shorts any DC bias for a masthead LNA too (use a DC-pass GDT type there).")
for P, label in [(2, "E22 2 W"), (1, "E220 1 W"), (100, "100 W HF/VHF rig"), (375, "IS-50NX-C2 rated 375 W")]:
    vpk = math.sqrt(2 * P * 50)
    print(f"     {label:24s}: RF peak {vpk:5.1f} V matched, {2*vpk:5.1f} V worst case (|Γ| = 1) vs GDT turn-on 600 V ±20 %")
check("E22 RF peak voltage (V)", math.sqrt(2 * 2 * 50), 14.14, 0.01)

print("\nALL PASS" if not FAILS else f"\nFAILED: {FAILS}")
