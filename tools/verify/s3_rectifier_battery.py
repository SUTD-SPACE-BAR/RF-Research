#!/usr/bin/env python3
"""W5-S3 verification for kb/05-analog-electronics/power-supplies-for-rf-and-analog.md — sections
"Mains supply fundamentals" (G-05-04) and "Batteries" (G-05-06). ngspice via s3_spice.py.

 1. Capacitor-input rectifiers (Singapore 230 V / 50 Hz mains, 9 V rms secondary, 0.5 ohm winding R, 1N4007-class
    diodes, 4700 uF, 1.2 A constant-current load): half-wave vs bridge in ngspice vs dV = I/(fC), I/(2fC);
    peak, trough, diode peak current, conduction angle.
 2. Linear bench supply for a 2 W LoRa PA (E22-400T33D: 5 V, 1.2 A in TX): low-mains headroom, regulator dissipation,
    heatsink; versus a buck from 12 V.
 3. Zener shunt regulator: resistor design, no-load dissipation, ripple with and without a bypass capacitor (ngspice).
 4. Batteries: Peukert runtime, Ah -> runtime budget for a 1S flight computer, and a cold-launch constant-power
    droop (Python closed form + ngspice battery model with a polarisation RC and a constant-power B-source load).
Run: python3 tools/verify/s3_rectifier_battery.py
"""
import numpy as np
from s3_spice import run, op

print("=== 1. Capacitor-input rectifiers (9 V rms, 50 Hz, 4700 uF, 1.2 A) ===")
Vrms, f, C, I = 9.0, 50.0, 4700e-6, 1.2
D = ".model DR D(IS=7.03n N=1.81 RS=0.034)"
src = f"Vs a 0 SIN(0 {Vrms*np.sqrt(2):.4f} {f:g})\nRw a a1 0.5\n"
nets = {
    "half-wave": src + f"D1 a1 out DR\nC1 out 0 {C:g} IC=11\nIL out 0 DC {I:g}\n{D}\n",
    "bridge": f"Vs a b SIN(0 {Vrms*np.sqrt(2):.4f} {f:g})\nRw a a1 0.5\nRf b 0 1e9\n"
              f"D1 a1 out DR\nD2 b out DR\nD3 0 a1 DR\nD4 0 b DR\nC1 out 0 {C:g} IC=10\nIL out 0 DC {I:g}\n{D}\n",
}
res = {}
for nm, net in nets.items():
    exprs = ["v(out)", "i(Vs)"]
    x, d = run(net, "tran 20u 1.0 0.8 20u uic", exprs)
    v = d[exprs[0]]; iv = np.abs(d["i(Vs)"])
    ripple = v.max() - v.min()
    frac = np.mean(iv > 0.05 * iv.max())
    pred = I / (f * C) if nm == "half-wave" else I / (2 * f * C)
    res[nm] = (v.max(), v.min(), ripple, iv.max(), v.mean())
    nper = 1 if nm == "half-wave" else 2
    print(f"  {nm:9s}: peak {v.max():.2f} V, trough {v.min():.2f} V, mean {v.mean():.2f} V, ripple {ripple:.2f} V p-p "
          f"(I/{nper}fC = {pred:.2f} V), diode peak current {iv.max():.1f} A, conduction {frac*360/nper:.0f} deg per pulse")
    assert 0.6 * pred < ripple <= pred * 1.02   # formula ignores the recharge time: conservative
print(f"  ideal peak sqrt2*Vrms = {Vrms*np.sqrt(2):.2f} V; the bridge loses 2 V_F at the peak current plus I_pk*R_w")

print("\n=== 2. Linear 5 V / 1.2 A bench supply for an E22-400T33D, vs a buck ===")
pk, tr, rp, ipk, vmean = res["bridge"]
low = 0.9
tr_low = low * pk - (1 - low) * 0 - rp  # approx: peak scales with mains, ripple unchanged
tr_low = pk * low - rp
for Vdo in (1.3, 2.0):
    print(f"  regulator dropout {Vdo} V: need trough >= {5+Vdo:.1f} V; nominal trough {tr:.2f} V, at -10 % mains ~{tr_low:.2f} V "
          f"-> {'OK' if tr_low >= 5 + Vdo else 'FAILS'}")
P_reg = (vmean - 5.0) * I
TA, TJ, thJC, thCS = 40.0, 125.0, 3.0, 0.5
print(f"  regulator dissipation (continuous TX) = (V_in,avg - 5) x 1.2 A = ({vmean:.2f} - 5) x 1.2 = {P_reg:.1f} W; "
      f"at 10 % TX duty {P_reg*0.1 + (vmean-5)*0.015*0.9:.2f} W average")
thSA = (TJ - TA) / P_reg - thJC - thCS
print(f"  heatsink for continuous TX at T_A 40 C, T_J 125 C, theta_JC 3, theta_CS 0.5 K/W: theta_SA <= {thSA:.1f} K/W")
Pin_lin = vmean * I
print(f"  efficiency: linear from the rectified rail {5*I/Pin_lin*100:.0f} % (input {Pin_lin:.1f} W), "
      f"transformer VA ~ 1.6-1.8 x DC power for capacitor input -> {1.7*Pin_lin:.0f} VA")
for Vin in (12.0,):
    print(f"  from a 12 V adapter: linear {5/Vin*100:.0f} % ({(Vin-5)*I:.1f} W lost); buck at ~90 % loses {6/0.9-6:.2f} W")
assert P_reg > 3 and thSA > 0

print("\n=== 3. Zener shunt regulator: 5.1 V, 0-20 mA load, from 12 V +/- 1 V ripple (100 Hz) ===")
Vin_min, Vz, ILmax, IZmin = 11.0, 5.1, 20e-3, 5e-3
R = (Vin_min - Vz) / (ILmax + IZmin)
Pz_noload = Vz * (13.0 - Vz) / R
print(f"  R = (Vin_min - Vz)/(I_Lmax + I_Zmin) = {R:.0f} ohm (use 220 ohm); worst Zener dissipation at no load, 13 V in: {Vz*(13-Vz)/220*1e3:.0f} mW; "
      f"R dissipation {(13-Vz)**2/220*1e3:.0f} mW")
z = """Vin in 0 SIN(12 1 100)
R1 in z 220
DZ 0 z DZ5
RL z 0 255
.model DZ5 D(IS=1e-14 N=1 RS=8 BV=5.1 IBV=1m NBV=1.5)
"""
x, d = run(z, "tran 50u 0.3 0.1 50u", ["v(z)"])
r0 = d["v(z)"].max() - d["v(z)"].min()
rr = {}
for Cb in ("100u", "1000u"):
    x, d = run(z + f"Cb z 0 {Cb}\n", "tran 50u 2.0 1.6 50u", ["v(z)"])
    rr[Cb] = d["v(z)"].max() - d["v(z)"].min()
print(f"  ngspice output ripple, 2 V p-p 100 Hz input: {r0*1e3:.1f} mV without bypass (r_z/(R+r_z), r_z ~ 16 ohm at 5 mA + 8 ohm RS), "
      f"{rr['100u']*1e3:.1f} mV with 100 uF, {rr['1000u']*1e3:.1f} mV with 1000 uF across the Zener")
print("  (a bypass C must beat r_z at the ripple frequency: 100 uF = 15.9 ohm at 100 Hz does little; it mainly removes avalanche noise above ~1 kHz)")
assert rr["1000u"] < r0 / 5 and rr["100u"] > r0 / 3
print(f"  series vs shunt: series pass element draws ~I_load (+I_Q); a shunt regulator draws I_Lmax + I_Zmin all the time")

print("\n=== 4. Batteries ===")
def peukert_t(Crated, Hrated, I, k):
    return Hrated * (Crated / (I * Hrated)) ** k
for nm, k in (("LiPo/Li-ion", 1.05), ("lead-acid", 1.25)):
    t = peukert_t(1.0, 1.0, 2.0, k)
    print(f"  Peukert {nm} (k = {k}), 1 Ah rated at 1 h: at 2 A runtime {t*60:.1f} min ({t*2:.2f} Ah delivered, ideal 30 min)")
# 1S flight-computer energy budget
P_logic = 3.3 * 0.12
P_radio = 5.0 * (0.1 * 1.2 + 0.9 * 0.015)
eta = 0.88
P_bat = (P_logic + P_radio) / eta
E = 1.0 * 3.7
for lab, frac in (("25 C, 80 % usable", 0.8), ("0 C, ~70 % usable (assumed)", 0.7), ("-20 C, ~50 % usable (assumed)", 0.5)):
    print(f"  1S 1000 mAh (3.7 Wh), load {P_bat:.2f} W ({P_logic:.2f} W logic + {P_radio:.2f} W radio at 10 % TX, /0.88): "
          f"{lab}: {E*frac/P_bat:.2f} h")
# cold-launch droop: 6 W radio + 0.4 W logic through 0.88 converters
P = (6.0 + 0.4) / 0.88
Rw = 0.03
print(f"  constant-power burst {P:.2f} W from the cell (6 W radio + 0.4 W logic, eta 0.88):")
rows = []
for T, Rc in ((25, 0.05), (0, 0.125), (-20, 0.30)):
    Rt = Rc + Rw
    for Voc in (4.0, 3.7):
        disc = Voc ** 2 - 4 * Rt * P
        if disc < 0:
            print(f"    {T:+3d} C, R_cell {Rc*1e3:.0f} mOhm (+30 wiring), V_oc {Voc:.2f} V: NO SOLUTION — converter input collapses (V_oc < sqrt(4RP) = {np.sqrt(4*Rt*P):.2f} V)")
            rows.append((T, Voc, None)); continue
        Iin = (Voc - np.sqrt(disc)) / (2 * Rt)
        Vt = Voc - Iin * Rt
        rows.append((T, Voc, Vt))
        print(f"    {T:+3d} C, R_cell {Rc*1e3:.0f} mOhm (+30 wiring), V_oc {Voc:.2f} V: I = {Iin:.2f} A, terminal {Vt:.2f} V"
              f"{'  < 3.0 V UVLO/brown-out' if Vt < 3.0 else ''}")
# ngspice: battery with polarisation RC, 1 s constant-power burst, -20 C cell at V_oc = 4.0 V
bat = """Voc oc 0 DC {voc}
R0 oc n1 {r0}
R1 n1 n2 {r1}
C1 n1 n2 {c1}
Rw n2 t 0.03
Bp t 0 I = {p}/max(V(t),1.0) * (time > 0.2 ? 1 : 0.05)
"""
for T, r0, voc in ((25, 0.035, 4.0), (-20, 0.21, 4.0)):
    net = bat.format(voc=voc, r0=r0, r1=r0 * 3 / 7, c1=1.0 / (r0 * 3 / 7), p=P)
    x, d = run(net, "tran 1m 1.2 0 1m", ["v(t)"])
    v = d["v(t)"]
    i02 = np.argmin(abs(x - 0.21)); iend = -1
    print(f"  ngspice {T:+d} C cell (R0 {r0*1e3:.0f} + R1 {r0*3/7*1e3:.0f} mOhm, tau 1 s): terminal {v[i02]:.2f} V just after the step, "
          f"{v[iend]:.2f} V after 1 s of TX (closed-form steady state with R = {r0*10/7*1e3:.0f} + 30 mOhm: "
          f"{voc - (voc-np.sqrt(voc**2-4*(r0*10/7+0.03)*P))/2:.2f} V)")
    if T == -20:
        assert v[iend] < v[i02]
print("\nALL S3 RECTIFIER/BATTERY CHECKS PASS")
