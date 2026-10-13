#!/usr/bin/env python3
"""W5-S3 verification for the day-one primers (G-05-05):
  - kb/01-circuit-theory/lumped-elements-impedance-admittance.md  "Level 0 — DC basics"
  - kb/05-analog-electronics/diodes-schottky-pin-varactor.md        "Level 0 — semiconductor primer"
  - kb/05-analog-electronics/bjt-fundamentals-small-signal.md        "Level 0 — V_BE, f_beta, f_alpha, f_T"
 1. Ohm's law / power numbers; ngspice .op of an LED + resistor and a battery divider.
 2. pn-junction primer: built-in potential, depletion width, LED V_F ~ hc/(q lambda); ngspice V_F of a
    1N4148 model, a Schottky (HSMS-282x parameters) and the LED model at 1 and 10 mA.
 3. BJT: V_BE at 1 mA; ngspice f_beta, f_T (common emitter) and f_alpha (common base) of the 2N3904-like model.
Run: python3 tools/verify/s3_primer.py
"""
import numpy as np
from s3_spice import run, op, first_cross

q, k, h, c = 1.602176634e-19, 1.380649e-23, 6.62607015e-34, 299792458.0
eps0 = 8.8541878188e-12

print("=== 1. DC basics ===")
R_led = (3.3 - 2.0) / 10e-3
print(f"  red LED (V_F 2.0 V) at 10 mA from 3.3 V: R = (3.3-2.0)/10 mA = {R_led:.0f} ohm, P_R = {(1.3*0.01)*1e3:.0f} mW, P_LED = 20 mW")
print(f"  2S pack 8.4 V into 100k + 33k: I = {8.4/133e3*1e6:.1f} uA, P = {8.4**2/133e3*1e3:.2f} mW")
print(f"  E22 module 5 V x 1.2 A = {5*1.2:.1f} W; igniter 1 ohm across 8.4 V: {8.4:.1f} A, {8.4**2:.0f} W (why the pyro FET must stay off)")
print(f"  0603 resistor rated 0.1 W: max V across 1 k = sqrt(P R) = {np.sqrt(0.1*1e3):.1f} V; max I in 1 ohm = {np.sqrt(0.1/1):.2f} A")
Rw = 1.72e-8 * 1.0 / 0.5e-6
print(f"  1 m of 0.5 mm^2 copper = {Rw*1e3:.1f} mOhm: at 2 A drops {2*Rw*1e3:.0f} mV and dissipates {4*Rw:.2f} W")
print(f"  energy: 1000 mAh x 3.7 V = {1.0*3.7:.1f} Wh = {3.7*3600:.0f} J")
led = """V1 vdd 0 3.3
R1 vdd a 130
D1 a 0 LEDR
.model LEDR D(IS=1.3e-19 N=2 RS=2)
Vb b 0 8.4
Rt b m 100k
Rbt m 0 33k
"""
o = op(led, ["v(a)", "i(V1)", "v(m)", "i(Vb)"])
print(f"  ngspice: LED node {o['v(a)']:.3f} V, I = {-o['i(V1)']*1e3:.2f} mA; divider {o['v(m)']:.3f} V at {-o['i(Vb)']*1e6:.1f} uA")
assert abs(-o["i(V1)"] - 0.010) < 0.0006 and abs(o["v(m)"] - 2.084) < 0.002

print("\n=== 2. pn junction primer (silicon, 300 K) ===")
VT = k * 300 / q
ni = 9.65e9 * 1e6        # m^-3 (Altermatt 2003 value 9.65e9 cm^-3)
NA, ND = 1e17 * 1e6, 1e16 * 1e6
phi = VT * np.log(NA * ND / ni ** 2)
es = 11.7 * eps0
W0 = np.sqrt(2 * es * phi / q * (1 / NA + 1 / ND))
W5 = np.sqrt(2 * es * (phi + 5) / q * (1 / NA + 1 / ND))
print(f"  N_A 1e17, N_D 1e16 cm^-3: phi = V_T ln(N_A N_D/n_i^2) = {phi:.3f} V; depletion W = {W0*1e6:.3f} um at 0 V, {W5*1e6:.3f} um at 5 V reverse;"
      f" C/A = {es/W0*1e9*1e-6*1e3:.0f} -> {es/W5*1e9*1e-6*1e3:.0f} pF/mm^2")
print(f"  (C/A in nF/cm^2: {es/W0*1e9*1e-4:.1f} -> {es/W5*1e9*1e-4:.1f}); fraction of W on the lightly doped side = {NA/(NA+ND):.2f}")
assert 0.75 < phi < 0.80
for lam, name in ((940e-9, "IR 940 nm"), (630e-9, "red 630 nm"), (590e-9, "amber 590 nm"), (525e-9, "green 525 nm"), (470e-9, "blue 470 nm")):
    print(f"  LED {name:13s}: photon energy hc/lambda = {h*c/lam/q:.2f} eV -> V_F >= ~{h*c/lam/q:.2f} V")
mods = {"1N4148 (IS 2.52n, N 1.752, RS 0.568)": "IS=2.52e-9 N=1.752 RS=0.568",
        "Schottky HSMS-282x (IS 22n, N 1.08, RS 6)": "IS=2.2e-8 N=1.08 RS=6",
        "zero-bias Schottky HSMS-2850 (IS 3u, N 1.06, RS 25)": "IS=3e-6 N=1.06 RS=25",
        "red LED model": "IS=1.3e-19 N=2 RS=2"}
vf = {}
for nm, m in mods.items():
    row = []
    for I in (1e-3, 10e-3):
        o = op(f"I1 0 a DC {I:g}\nD1 a 0 DX\n.model DX D({m})\n.options temp=25", ["v(a)"])
        row.append(o["v(a)"])
    vf[nm] = row
    print(f"  ngspice V_F {nm:52s}: {row[0]:.3f} V at 1 mA, {row[1]:.3f} V at 10 mA")
assert 0.55 < vf["1N4148 (IS 2.52n, N 1.752, RS 0.568)"][0] < 0.70

print("\n=== 3. BJT: V_BE, f_beta, f_T, f_alpha (2N3904-like model of the BJT page) ===")
VT25 = k * 298.15 / q
for IS in (1e-14, 1e-15):
    print(f"  I_S = {IS:g} A: V_BE at 1 mA = V_T ln(I_C/I_S) = {VT25*np.log(1e-3/IS):.3f} V (25 C); per decade {VT25*np.log(10)*1e3:.1f} mV")
model = ".model QG NPN(IS=1e-14 BF=200 VAF=75 TF=300p CJE=4p VJE=0.75 MJE=0.01 CJC=3p VJC=0.75 MJC=0.01 RB=0 RE=0 RC=0)"
ce = model + "\nVCC c 0 DC 5\nIb 0 b DC 25u AC 1\nQ1 c b 0 QG\n"
f, d = run(ce, "ac dec 100 10k 3G", ["mag(i(vcc))"])
h21 = d["mag(i(vcc))"]
fb = first_cross(f, h21, h21[0] / np.sqrt(2))
fT = first_cross(f, h21, 1.0)
o = op(ce, ["i(vcc)"])
Ic = -o["i(vcc)"]
# common base: AC current into the emitter, base grounded, collector at fixed DC voltage
cb = model + f"\nVCC c 0 DC 5\nVB b 0 DC 0\nIe e 0 DC {Ic*(1+1/200):.6g} AC 1\nQ1 c b e QG\n"
f2, d2 = run(cb, "ac dec 100 10k 3G", ["mag(i(vcc))"])
a = d2["mag(i(vcc))"]
fa = first_cross(f2, a, a[0] / np.sqrt(2))
print(f"  I_C = {Ic*1e3:.2f} mA, beta0 = {h21[0]:.0f}: f_beta = {fb/1e6:.2f} MHz, f_T = {fT/1e6:.0f} MHz (f_beta*beta0 = {fb*h21[0]/1e6:.0f} MHz),"
      f" f_alpha = {fa/1e6:.0f} MHz (= {fa/fT:.2f} f_T; single-pole model predicts (beta0+1)/beta0)")
assert abs(fb * h21[0] / fT - 1) < 0.05 and 0.95 < fa / fT < 1.3
print("\nALL S3 PRIMER CHECKS PASS")
