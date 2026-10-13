#!/usr/bin/env python3
"""W5-S3 verification for kb/05-analog-electronics/op-amps-real-limitations.md, section
"Practical recipes" (G-05-01). All circuits run in ngspice (Homebrew CLI via s3_spice.py).

 1. Choosing resistor values: noise / bias-current error / load current / input-capacitance pole for an
    inverting gain of -10 at five impedance levels; ngspice peaking with and without C_F = R_G*C_in/R_F.
 2. AC-coupled single-supply non-inverting stage: bias-return resistor, DC gain 1 via C_G; ngspice .op of
    the right and the two wrong versions; low-frequency corners.
 3. Attenuators: noise gain of an inverting -0.1 stage; unity-gain-stable vs decompensated op-amp; noise-gain
    shaping (R_n + C_n) — ngspice closed-loop peaking.
 4. MOSFET inside the loop (V-to-I current sink): ngspice step response with direct gate drive, and with
    R_gate + C_F/R_F dual feedback.
 5. Summing amplifier noise gain: 4-input summer, ngspice -3 dB vs GBW/NG.
Run: python3 tools/verify/s3_opamp_recipes.py   (about 10 s)
"""
import numpy as np
from s3_spice import run, op, first_cross

k = 1.380649e-23
T = 300.0  # 05 analog budgets use 300 K (labelled; canonical page)

# two-pole op-amp macro: A0 = 1e5, first pole at GBW/A0, second pole p2, output resistance Ro
def oa(name, gbw, p2, ro=50.0):
    a0 = 1e5
    rp = 1e5          # Gm = 1 mS * 100 Meg ... use Gm*Rp = A0 with Gm = 1 S, Rp = 1e5
    cp = 1 / (2 * np.pi * rp * gbw / a0)
    r2, c2 = 1e3, 1 / (2 * np.pi * 1e3 * p2)
    return f""".subckt {name} inp inn out
Gin 0 n1 inp inn 1
Rp n1 0 {rp:g}
Cp n1 0 {cp:g}
E2 n2 0 n1 0 1
R2 n2 n3 {r2:g}
C2 n3 0 {c2:g}
Eo n4 0 n3 0 1
Ro n4 out {ro:g}
.ends
"""

def peak_db(x, y):
    return float(np.max(y))

print("=== 1. Resistor values for an inverting gain of -10 (300 K) ===")
amps = {"bipolar low-noise (1.1 nV, 1.7 pA, I_B 100 nA illustr.)": (1.1e-9, 1.7e-12, 100e-9),
        "CMOS MCP6002 (28 nV, 0.6 fA, 1 pA)": (28e-9, 0.6e-15, 1e-12)}
Cin = 5e-12; GBW = 10e6
print("R_G      R_F     | e_RTI bip  e_RTI CMOS (nV/rtHz, to signal input) | I_B*R_F out err bip | I_load @1V | f_p(5 pF) vs f_c")
rows = []
for RG in (100.0, 1e3, 10e3, 100e3, 1e6):
    RF = 10 * RG; NG = 11; Rp = RF * RG / (RF + RG)
    res = []
    for nm, (en, inn, ib) in amps.items():
        eout = NG * np.sqrt(en**2 + 4 * k * T * Rp + (inn * Rp) ** 2)
        res.append(eout / 10)
    ib_err = amps[list(amps)[0]][2] * RF
    fp = 1 / (2 * np.pi * Rp * Cin); fc = GBW / NG
    rows.append((RG, res))
    print(f"{RG:7.0f} {RF:8.0f} | {res[0]*1e9:9.2f} {res[1]*1e9:10.2f} | {ib_err*1e3:8.3f} mV | {1/RF*1e3:8.3f} mA | {fp/1e3:9.0f} kHz vs {fc/1e3:.0f} kHz")
# assertions on the narrative
assert rows[0][1][0] < 2.2e-9 and rows[4][1][0] > 30e-9
assert abs(1 / (2 * np.pi * (1e7 * 1e6 / 1.1e7) * Cin) - 35e3) < 1e3

# ngspice: R_G = 100k, R_F = 1M, 10 pF at the inverting node, unity-gain-stable 10 MHz op-amp
base = oa("OA", 10e6, 17.3e6)
for CF, label in ((0, "no C_F"), (1e-12, "C_F = R_G C_in/R_F = 1 pF")):
    net = base + f"""V1 in 0 AC 1
X1 0 inn out OA
RG in inn 100k
RF out inn 1Meg
Cn inn 0 10p
""" + (f"CF out inn {CF:g}\n" if CF else "")
    f, d = run(net, "ac dec 200 1k 100Meg", ["vdb(out)"])
    g = d["vdb(out)"]
    print(f"  ngspice, 100k/1M with 10 pF at the - input, {label}: DC {g[0]:.2f} dB, peak {g.max():.2f} dB "
          f"(+{g.max()-g[0]:.1f} dB) at {f[np.argmax(g)]/1e3:.0f} kHz; -3 dB at {first_cross(f, g, g[0]-3)/1e3:.0f} kHz")
    if CF == 0:
        pk0 = g.max() - g[0]
    else:
        pk1 = g.max() - g[0]
assert pk0 > 6 and pk1 < 0.5

print("\n=== 2. AC-coupled non-inverting stage on 3.3 V (gain 21) ===")
lim = """.subckt OAL inp inn out
B1 out 0 V = min(3.3, max(0, 1.65 + 1e5*(V(inp)-V(inn))))
.ends
"""
ac_good = lim + """VDD vdd 0 3.3
R1 vdd mid 100k
R2 mid 0 100k
Cm mid 0 10u
Vs src 0 DC 0 AC 1
Cin src p 1u
RB p mid 100k
IB p 0 DC 100n
X1 p n out OAL
RF out n 100k
RG n g 4.99k
CG g 0 10u
"""
o = op(ac_good, ["v(out)", "v(p)"])
print(f"  correct (R_B to mid-rail, C_G in series with R_G): V(out) = {o['v(out)']:.3f} V (mid 1.650; I_B*R_B = 10 mV error at gain 1)")
assert abs(o["v(out)"] - 1.64) < 0.02
o2 = op(ac_good.replace("CG g 0 10u", "CG g 0 1e-30\nRGND g 0 1m"), ["v(out)"])
print(f"  wrong #1 (R_G straight to ground, DC gain 21): V(out) = {o2['v(out)']:.3f} V  -> pinned to the rail")
assert o2["v(out)"] > 3.29
f, d = run(ac_good, "ac dec 100 0.01 1k", ["vdb(out)"])
g = d["vdb(out)"]
flo = first_cross(f, g, g[-1] - 3)
print(f"  midband {g[-1]:.2f} dB; low -3 dB at {flo:.2f} Hz (corners 1/2piR_BC_in = {1/(2*np.pi*1e5*1e-6):.2f} Hz, 1/2piR_GC_G = {1/(2*np.pi*4990*10e-6):.2f} Hz)")
assert 2.5 < flo < 4.5
# wrong #2: no bias return -> I_B charges C_in
rate = 100e-9 / 1e-6
print(f"  wrong #2 (no R_B): 100 nA of bipolar I_B ramps the + input at I_B/C_in = {rate:.2f} V/s -> rail in ~{1.65/rate:.0f} s;"
      f" a 1 pA CMOS input still drifts {1e-12/1e-6*3600*1e3:.1f} mV/h, set by leakage, i.e. undefined")
x, d = run(ac_good.replace("RB p mid 100k", "RB p mid 1e15") + ".ic v(p)=1.65 v(mid)=1.65 v(g)=1.65 v(n)=1.65 v(out)=1.65\n", "tran 0.1 30 0 0.05 uic", ["v(out)", "v(p)"])
vp = d["v(p)"]
print(f"  ngspice transient without R_B: V(+) falls {vp[0]-vp[-1]:.2f} V in 30 s (expected {rate*30:.1f} V until the output hits 0 V)")

print("\n=== 3. Attenuator: inverting -0.1 (R_in 10k, R_F 1k) ===")
print(f"  noise gain 1 + R_F/R_in = {1+1e3/10e3:.2f} (never below 1) -> a unity-gain-stable part is MORE stable here than as a follower")
uni = oa("OU", 10e6, 17.32e6)            # PM ~60 deg at NG = 1
dec = oa("OD", 50e6, 17.32e6)            # stable only for NG >~ 5 (PM 60 deg at NG = 5)
cases = [
    ("unity-stable, follower (NG 1)", uni + "V1 in 0 AC 1\nX1 in out out OU\n", 1.0),
    ("unity-stable, -0.1 attenuator (NG 1.1)", uni + "V1 in 0 AC 1\nRi in n 10k\nRF out n 1k\nX1 0 n out OU\n", 0.1),
    ("decompensated (NG>=5), -0.1 attenuator", dec + "V1 in 0 AC 1\nRi in n 10k\nRF out n 1k\nX1 0 n out OD\n", 0.1),
    ("decompensated + noise-gain shaping 256 R + 10 nF", dec + "V1 in 0 AC 1\nRi in n 10k\nRF out n 1k\nRn n m 256\nCn m 0 10n\nX1 0 n out OD\n", 0.1),
]
pk = []
for name, net, g0 in cases:
    f, d = run(net, "ac dec 200 1k 500Meg", ["vdb(out)"])
    g = d["vdb(out)"]
    pk.append(g.max() - 20 * np.log10(g0))
    print(f"  {name:48s}: peaking {g.max()-20*np.log10(g0):+5.2f} dB at {f[np.argmax(g)]/1e6:6.2f} MHz")
assert pk[1] < pk[0] and pk[2] > 4 and pk[3] < 1.5

print("\n=== 4. MOSFET inside the loop: 0.1 -> 0.2 A step of a V-to-I sink (R_S = 1 ohm) ===")
mos = oa("OM", 10e6, 17.32e6, ro=100.0) + """.model NM NMOS(VTO=2 KP=2)
VDD dd 0 12
RL dd d 10
Vset set 0 PULSE(0.1 0.2 20u 100n 100n 200u 400u)
M1 d g s s NM W=1 L=1
Cgs g s 1.5n
Cgd g d 0.2n
RS s 0 1
"""
def mos_case(extra):
    x, d = run(mos + extra, "tran 5n 120u 0 5n", ["v(s)"])
    v = d["v(s)"]
    sel = x > 20e-6
    ov = (v[sel].max() - 0.2) / 0.1 * 100
    # 2 % settling time after the step
    idx = np.where(np.abs(v[sel] - 0.2) > 0.002)[0]
    ts = x[sel][idx[-1]] - 20e-6 if len(idx) else 0.0
    return ov, ts
ovA, tsA = mos_case("X1 set s g OM\n")
print(f"  direct gate drive, feedback from R_S        : overshoot {ovA:5.1f} %, 2 % settling {tsA*1e6:6.2f} us")
ovB, tsB = mos_case("X1 set n o OM\nRgate o g 100\nRF s n 1k\nCF o n 220p\n")
print(f"  R_gate 100 R + C_F 220 pF (out->-in) + R_F 1k: overshoot {ovB:5.1f} %, 2 % settling {tsB*1e6:6.2f} us")
assert ovA > 25 and ovB < 5

print("\n=== 5. Summing amplifier noise gain ===")
s1 = oa("OS", 1e6, 50e6) + """V1 a 0 AC 1
R1 a n 10k
R2 0 n 10k
R3 0 n 10k
R4 0 n 10k
RF out n 10k
X1 0 n out OS
"""
f, d = run(s1, "ac dec 200 1k 10Meg", ["vdb(out)"])
g = d["vdb(out)"]
f3 = first_cross(f, g, g[0] - 3)
print(f"  4 inputs x 10k, R_F 10k: signal gain per input {10**(g[0]/20):.3f}, NG = 1 + R_F/(R/4) = 5, "
      f"-3 dB {f3/1e3:.0f} kHz (GBW/NG = 200 kHz); e_n and V_OS are multiplied by 5")
assert abs(f3 - 200e3) < 15e3
print("\nALL S3 OP-AMP RECIPE CHECKS PASS")
