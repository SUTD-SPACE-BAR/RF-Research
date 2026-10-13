#!/usr/bin/env python3
"""W5-S3 verification for kb/05-analog-electronics/analog-signal-conditioning.md — sections
"Current loops (4-20 mA) and long differential sensor lines" (G-05-01) and
"Comparators, Schmitt triggers and timers" (G-05-03). ngspice via s3_spice.py.

 1. 4-20 mA receiver for a 3.3 V ADC: shunt choice, NAMUR NE 43 levels, loop compliance (ngspice loop with a
    transmitter that needs >= 10 V), resolution and shunt tempco.
 2. Ground offset on a long sensor line: single-ended vs 1 % difference amp vs INA (ngspice worst-case diff amp).
 3. Schmitt trigger as a 1S battery-undervoltage detector (3.3 V falling / 3.5 V rising), E96 values,
    ngspice triangle sweep; chatter with and without hysteresis; open-drain pull-up rise time.
 4. 555 astable: ngspice behavioural 555 (hysteretic switch at Vcc/3, 2Vcc/3) vs f = 1/(ln2 (RA+2RB) C).
Run: python3 tools/verify/s3_lines_comparators.py
"""
import numpy as np
from s3_spice import run, op, first_cross

print("=== 1. 4-20 mA loop receiver for a 3.3 V ADC ===")
Rsh = 150.0
for I, lab in ((3.6e-3, "NE 43 fault low (<= 3.6 mA)"), (3.8e-3, "NE 43 range low"), (4e-3, "zero"), (20e-3, "full scale"),
               (20.5e-3, "NE 43 range high"), (21e-3, "NE 43 fault high (>= 21 mA)")):
    print(f"  {I*1e3:5.1f} mA -> {I*Rsh:.3f} V across 150 ohm  ({lab})")
lsb = 3.3 / 4096
print(f"  12-bit LSB {lsb*1e3:.3f} mV = {lsb/Rsh*1e6:.2f} uA = {lsb/(16e-3*Rsh)*100:.3f} % of span; 25 ppm/K shunt over 50 K = {25e-6*50*100:.3f} % gain error")
Vloop, Vtx, Rwire = 24.0, 10.0, 2 * 200 * 1.72e-8 / 0.5e-6
Rprot = 50.0
Rmax = (Vloop - Vtx) / 22e-3
print(f"  wire 2 x 200 m of 0.5 mm^2 Cu = {Rwire:.1f} ohm; max total loop R at 22 mA = (24 - 10)/22 mA = {Rmax:.0f} ohm "
      f"-> {Rmax - Rsh - Rprot - Rwire:.0f} ohm spare")
# ngspice: transmitter = current source that needs >= 10 V across it (linear collapse below)
tx = """VL p 0 24
Bx p t I = 0.02*min(1, max(0, (V(p,t)-9)/1))
Rw t a {rw}
Rpr a b 50
Rs b 0 150
"""
for rw in (13.8, 400, 600):
    o = op(tx.format(rw=rw), ["v(b)", "v(p,t)"])
    print(f"  ngspice loop, wire+extra R = {rw:5.1f} ohm: I = {o['v(b)']/150*1e3:6.3f} mA, transmitter terminal voltage {o['v(p,t)']:.2f} V")
o1 = op(tx.format(rw=13.8), ["v(b)"]); o3 = op(tx.format(rw=600), ["v(b)"])
assert abs(o1["v(b)"] / 150 - 0.02) < 1e-6 and o3["v(b)"] / 150 < 0.0199

print("\n=== 2. 1 V ground offset between a remote sensor and the flight computer ===")
dif = """Vcm cm 0 DC 1
Vd p cm DC 0
R1 cm n {r1}
R2 n out {r2}
R3 p q {r3}
R4 q 0 {r4}
E1 out 0 q n 1e7
"""
e = 0.01
o = op(dif.format(r1=10e3 * (1 + e), r2=10e3 * (1 - e), r3=10e3 * (1 - e), r4=10e3 * (1 + e)), ["v(out)"])
print(f"  single-ended ADC reading: error = 1 V (the whole offset)")
print(f"  4-resistor difference amp G = 1, worst-case 1 % resistors (ngspice): error {o['v(out)']*1e3:.1f} mV "
      f"-> CMRR {20*np.log10(1/abs(o['v(out)'])):.1f} dB (formula (1+G)/4e = {20*np.log10(2/(4*e)):.1f} dB)")
assert abs(20 * np.log10(1 / abs(o["v(out)"])) - 34.0) < 0.3
print(f"  INA with 100 dB CMRR: {1/10**5*1e6:.0f} uV")

print("\n=== 3. Schmitt trigger: 1S undervoltage detector, comparator on 3.3 V push-pull, Vref = 1.200 V ===")
Vcc, Vref = 3.3, 1.2
VL, VH = 3.3, 3.5
Rt = 100e3
Rh = Rt * Vcc / (VH - VL)
Gb = VH / (Rt * Vref) - 1 / Rt - 1 / Rh
Rb = 1 / Gb
print(f"  ideal: Rt = 100k, Rh = Rt*Vcc/(VH-VL) = {Rh/1e6:.3f} M, Rb = {Rb/1e3:.2f} k")
E96 = np.array([1.00,1.02,1.05,1.07,1.10,1.13,1.15,1.18,1.21,1.24,1.27,1.30,1.33,1.37,1.40,1.43,1.47,1.50,1.54,1.58,1.62,1.65,1.69,1.74,1.78,1.82,1.87,1.91,1.96,2.00,2.05,2.10,2.15,2.21,2.26,2.32,2.37,2.43,2.49,2.55,2.61,2.67,2.74,2.80,2.87,2.94,3.01,3.09,3.16,3.24,3.32,3.40,3.48,3.57,3.65,3.74,3.83,3.92,4.02,4.12,4.22,4.32,4.42,4.53,4.64,4.75,4.87,4.99,5.11,5.23,5.36,5.49,5.62,5.76,5.90,6.04,6.19,6.34,6.49,6.65,6.81,6.98,7.15,7.32,7.50,7.68,7.87,8.06,8.25,8.45,8.66,8.87,9.09,9.31,9.53,9.76])
def e96(x):
    dec = 10 ** np.floor(np.log10(x)); return dec * E96[np.argmin(abs(E96 * dec - x))]
Rh9, Rb9 = e96(Rh), e96(Rb)
G = 1 / Rt + 1 / Rb9 + 1 / Rh9
vh = Rt * Vref * G
vl = Rt * (Vref * G - Vcc / Rh9)
print(f"  E96: Rh = {Rh9/1e6:.2f} M, Rb = {Rb9/1e3:.1f} k -> rising {vh:.3f} V, falling {vl:.3f} V, hysteresis {vh-vl:.3f} V")
sch = f"""Vb bat 0 PWL(0 3.0 10m 3.8 20m 3.0)
VR ref 0 {Vref}
Rt bat p {Rt:g}
Rb p 0 {Rb9:g}
Rh out p {Rh9:g}
Bc out 0 V = 1.65 + 1.65*tanh(2000*(V(p)-V(ref)))
"""
x, d = run(sch, "tran 1u 20m 0 1u", ["v(out)", "v(bat)"])
vo, vb = d["v(out)"], d["v(bat)"]
t_up = first_cross(x, vo, 1.65, rising=True); t_dn = first_cross(x, vo, 1.65, rising=False)
vb_up = np.interp(t_up, x, vb); vb_dn = np.interp(t_dn, x, vb)
print(f"  ngspice sweep: output rises at Vbat = {vb_up:.3f} V, falls at {vb_dn:.3f} V")
assert abs(vb_up - vh) < 0.01 and abs(vb_dn - vl) < 0.01
# chatter: slow ramp through threshold with 20 mV p-p 20 kHz noise at the comparator input
def transitions(rh):
    net = f"""Vb bat 0 PWL(0 3.3 10m 3.6)
Vn nz bat SIN(0 10m 20k)
VR ref 0 {Vref}
Rt nz p {Rt:g}
Rb p 0 {Rb9:g}
Rh out p {rh:g}
Bc out 0 V = 1.65 + 1.65*tanh(2000*(V(p)-V(ref)))
"""
    x, d = run(net, "tran 0.5u 10m 0 0.5u", ["v(out)"])
    v = d["v(out)"] > 1.65
    return int(np.sum(v[1:] != v[:-1]))
n0, n1 = transitions(1e12), transitions(Rh9)
print(f"  ramp 3.3 -> 3.6 V with 20 mV p-p noise: {n0} output transitions without hysteresis (Rh open), {n1} with Rh")
assert n0 > 5 and n1 == 1
Rp, CL = 10e3, 20e-12
print(f"  open-drain pull-up 10k into 20 pF: 10-90 % rise = 2.2 R C = {2.2*Rp*CL*1e9:.0f} ns; keep Rh >= 100 Rp (TI TIDU020)")

print("\n=== 4. 555 astable (Vcc 5 V, RA 10k, RB 47k, C 10 nF) ===")
RA, RB, C = 10e3, 47e3, 10e-9
f = 1 / (np.log(2) * (RA + 2 * RB) * C); duty = (RA + RB) / (RA + 2 * RB)
print(f"  formula: f = 1/(ln2 (RA+2RB) C) = 1.443/((RA+2RB)C) = {f:.1f} Hz, duty {duty*100:.1f} %; monostable t = RC ln3 = 1.1 RC")
n555 = """VCC vcc 0 5
RA vcc dis 10k
RB dis cap 47k
C1 cap 0 10n IC=1.6667
S1 dis 0 cap 0 SWD
.model SWD SW(VT=2.5 VH=0.83333 RON=1 ROFF=1e12)
"""
x, d = run(n555, "tran 0.2u 20m 0 0.2u uic", ["v(cap)", "v(dis)"])
vd = d["v(dis)"]
# output of a real 555 is high while the cap charges (discharge switch off): dis node high
hi = vd > 2.5
edges = np.where((~hi[:-1]) & hi[1:])[0]
per = np.diff(x[edges])[2:]
fs = 1 / per.mean()
falls = np.where(hi[:-1] & (~hi[1:]))[0]
th = np.mean([x[fl] - x[ed] for ed in edges[2:-1] for fl in falls if fl > ed][:5]) if len(falls) else 0
# duty by mean of hi over whole periods
dsim = hi[edges[2]:edges[-1]].mean()
print(f"  ngspice behavioural 555: f = {fs:.1f} Hz ({(fs/f-1)*100:+.2f} %), duty {dsim*100:.1f} %")
assert abs(fs / f - 1) < 0.01 and abs(dsim - duty) < 0.01
print("\nALL S3 LINE/COMPARATOR CHECKS PASS")
