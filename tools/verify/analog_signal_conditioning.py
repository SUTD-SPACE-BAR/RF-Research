#!/usr/bin/env python3
"""Verification script for kb/05-analog-electronics/analog-signal-conditioning.md

 1. Difference amplifier CMRR vs resistor tolerance: worst-case (1+G)/(4 eps) vs Monte Carlo; why INAs trim.
 2. INA333 gain resistor for a target gain; offset RTI vs gain.
 3. Wheatstone bridge: exact vs linear approximation for quarter/half/full bridges; strain-gauge numbers.
 4. INA RFI input filter: differential and common-mode corners; CM->DM conversion from capacitor mismatch.
 5. Battery-voltage divider into a sampling SAR ADC: Thevenin R, required C, RC settling.
 6. Input protection: clamp-diode current into a rail and rail back-powering; series R sizing; TVS capacitance corner.
 7. Level shifting a bipolar signal into a single-supply ADC: resistor solution and check.
 8. Shunt current sensing (pyro current) with an INA180-class CSA; igniter continuity measurement resolution.
Run: python3 tools/verify/analog_signal_conditioning.py
"""
import numpy as np
rng = np.random.default_rng(3)

print("=== 1. Difference amplifier CMRR vs resistor tolerance ===")
def diff_amp(R1, R2, R3, R4, v1, v2):
    # Vout = v2*(R4/(R3+R4))*(1+R2/R1) - v1*R2/R1  (v2 on + input via R3/R4 divider, v1 via R1, feedback R2)
    return v2 * R4 / (R3 + R4) * (1 + R2 / R1) - v1 * R2 / R1
for G in (1, 10, 100):
    for eps in (1e-2, 1e-3, 1e-4):
        N = 50000
        R1 = 1e3 * (1 + eps * rng.uniform(-1, 1, N)); R3 = 1e3 * (1 + eps * rng.uniform(-1, 1, N))
        R2 = G * 1e3 * (1 + eps * rng.uniform(-1, 1, N)); R4 = G * 1e3 * (1 + eps * rng.uniform(-1, 1, N))
        Acm = diff_amp(R1, R2, R3, R4, 1.0, 1.0)
        Adm = (diff_amp(R1, R2, R3, R4, -0.5, 0.5))
        cmrr = 20 * np.log10(np.abs(Adm / Acm))
        worst = 20 * np.log10((1 + G) / (4 * eps))
        print(f"G={G:3d}, tol={eps*100:5.2f} %: worst-case formula (1+G)/(4 eps) = {worst:5.1f} dB; Monte Carlo (uniform) min {cmrr.min():5.1f} dB, median {np.median(cmrr):5.1f} dB")

print("\n=== 2. INA333 ===")
for G in (10, 100, 500):
    RG = 100e3 / (G - 1)
    vos_typ = 10 + 25 / G; vos_max = 25 + 75 / G
    print(f"G={G}: RG = 100k/(G-1) = {RG:.1f} ohm; offset RTI typ {vos_typ:.2f} uV, max {vos_max:.2f} uV -> RTO max {vos_max*G/1e3:.2f} mV")

print("\n=== 3. Wheatstone bridge ===")
Vex = 3.3
for label, fn_exact, fn_lin in (
        ("quarter", lambda x: Vex * (x / (4 + 2 * x)), lambda x: Vex * x / 4),
        ("half (opposite arms)", lambda x: Vex * (x / (2 + x)), lambda x: Vex * x / 2),
        ("half (adjacent, push-pull)", lambda x: Vex * x / 2, lambda x: Vex * x / 2),
        ("full (push-pull)", lambda x: Vex * x, lambda x: Vex * x)):
    for x in (2e-3, 2e-2):
        e, l = fn_exact(x), fn_lin(x)
        print(f"{label:28s} dR/R={x:.3f}: exact {e*1e3:8.4f} mV, linear {l*1e3:8.4f} mV, nonlinearity {100*(l-e)/e if e else 0:6.3f} %")
GF, strain = 2.0, 1000e-6
print(f"strain gauge GF={GF}, {strain*1e6:.0f} microstrain -> dR/R = {GF*strain:.4f}; full bridge {GF*strain*1e3:.1f} mV/V -> {GF*strain*Vex*1e3:.2f} mV at 3.3 V excitation")

print("\n=== 4. INA RFI filter ===")
R, Cc, Cd = 1e3, 1e-9, 10e-9
f_dm = 1 / (2 * np.pi * R * (2 * Cd + Cc))
f_cm = 1 / (2 * np.pi * R * Cc)
print(f"R={R:.0f} each leg, Cc={Cc*1e9:.0f} nF each to ground, Cd={Cd*1e9:.0f} nF across: f_DM = 1/(2 pi R (2Cd+Cc)) = {f_dm/1e3:.2f} kHz, f_CM = 1/(2 pi R Cc) = {f_cm/1e3:.1f} kHz")
# CM->DM conversion at frequency f with capacitor mismatch
for tol in (0.05, 0.10):
    for f in (10e3, 1e6, 433e6):
        w = 2 * np.pi * f
        worst = 0
        for s1, s2 in ((1 + tol, 1 - tol),):
            c1, c2 = Cc * s1, Cc * s2
            # each leg: R then (C to gnd) with Cd between legs -> solve 2-node network with CM drive 1 V
            Y = np.array([[1 / R + 1j * w * c1 + 1j * w * Cd, -1j * w * Cd], [-1j * w * Cd, 1 / R + 1j * w * c2 + 1j * w * Cd]])
            v = np.linalg.solve(Y, np.array([1 / R, 1 / R]))
            worst = abs(v[0] - v[1])
        # same without Cd
        Y0 = np.array([[1 / R + 1j * w * c1, 0], [0, 1 / R + 1j * w * c2]])
        v0 = np.linalg.solve(Y0, np.array([1 / R, 1 / R]))
        print(f"  Cc mismatch +/-{tol*100:.0f} %, f={f/1e3:9.0f} kHz: CM->DM with Cd = {20*np.log10(worst+1e-30):7.1f} dB; without Cd = {20*np.log10(abs(v0[0]-v0[1])+1e-30):7.1f} dB")

print("\n=== 5. Battery divider into a SAR ADC ===")
Rt, Rb = 100e3, 33e3
Vbatt = 8.4
Vadc = Vbatt * Rb / (Rt + Rb)
Rth = Rt * Rb / (Rt + Rb)
Idiv = Vbatt / (Rt + Rb)
print(f"2S max 8.4 V, 100k/33k: ADC sees {Vadc:.3f} V, Thevenin {Rth/1e3:.1f} kOhm, divider current {Idiv*1e6:.0f} uA = {Idiv*8760*1e3:.0f} mAh per year of storage drain")
Cs, t_acq = 5e-12, 1e-6
tau = Rth * Cs
print(f"without external C: tau = Rth*Cs = {tau*1e9:.0f} ns; 12-bit settling needs {13*np.log(2):.1f} tau = {13*np.log(2)*tau*1e6:.2f} us vs t_acq {t_acq*1e6:.1f} us")
Cext = 100e-9
print(f"with Cext = 100 nF: kickback step Cs/(Cs+Cext) = {Cs/(Cs+Cext)*1e6:.0f} ppm (= {Cs/(Cs+Cext)*4096:.2f} LSB at 12 bit); RC corner {1/(2*np.pi*Rth*Cext):.0f} Hz")

print("\n=== 6. Input protection ===")
for Vfault, Rs in ((24.0, 10e3), (24.0, 1e3), (8.4, 10e3), (-8.4, 10e3)):
    Vrail = 3.3
    Vf = 0.3
    if Vfault > 0:
        I = (Vfault - Vrail - Vf) / Rs
    else:
        I = (Vfault + Vf) / Rs
    P = I**2 * Rs
    print(f"fault {Vfault:+5.1f} V through {Rs/1e3:4.0f} k into a {Vrail} V clamp: I = {I*1e3:+6.2f} mA, P(Rs) = {P*1e3:6.1f} mW")
print("  if the 3.3 V rail's load draws less than the clamp current (e.g. MCU asleep, board unpowered), the rail rises -> back-powering")
for Ctvs, Rsrc in ((30e-12, 10e3), (500e-12, 10e3), (500e-12, 50.0)):
    print(f"TVS {Ctvs*1e12:.0f} pF with {Rsrc:.0f} ohm source: corner {1/(2*np.pi*Rsrc*Ctvs)/1e6:.3f} MHz")

print("\n=== 7. Level shift +/-2.5 V -> 0.15..3.15 V for a 3.3 V ADC ===")
# Non-inverting summing: Vout = a*Vin + b; want a = 3.0/5.0 = 0.6, b = 1.65
a, b = 0.6, 1.65
# Passive: Vin through R1, Vref=3.3 through R2, R3 to ground, node -> buffer. Vout = Vin*G1 + 3.3*G2 with G1=Rp/R1, G2=Rp/R2, Rp = R1||R2||R3
# choose R1 = 10k: G1 = Rp/R1 = 0.6 -> Rp = 6k ; G2 = 1.65/3.3 = 0.5 -> R2 = 12k ; 1/R3 = 1/Rp - 1/R1 - 1/R2
R1 = 10e3; Rp = a * R1; R2 = Rp / (b / 3.3)
invR3 = 1 / Rp - 1 / R1 - 1 / R2
print(f"R1 = 10k, R2 = {R2/1e3:.1f}k, 1/R3 = {invR3:.3e} -> {'R3 = %.1fk' % (1/invR3/1e3) if invR3 > 0 else 'no R3 possible: need gain stage'}")
print(f"  passive summing needs a + b/Vref <= 1; here {a} + {b/3.3:.2f} = {a + b/3.3:.2f} > 1 -> impossible passively")
# option A: equal resistors, a = 0.5, b = 1.65 (a + b/3.3 = 1): Vout = (Vin + 3.3)/2
for Vin in (-2.5, 0.0, 2.5):
    print(f"  option A (R1 = R2, buffer after): Vin={Vin:+.1f} V -> {(Vin + 3.3)/2:.3f} V (uses {(2.9-0.4)/3.3*100:.0f} % of the ADC range); source impedance R/2")
# option B: op-amp difference/summing stage giving a = 0.6, b = 1.65
for Vin in (-2.5, 0, 2.5):
    print(f"  option B (active, a=0.6, b=1.65): Vin={Vin:+.1f} V -> {a*Vin+b:.3f} V")

print("\n=== 8. Current sensing and continuity ===")
for I, Rsh, G in ((3.0, 10e-3, 50), (5.0, 5e-3, 100), (0.5, 50e-3, 20)):
    Vsh = I * Rsh
    print(f"I={I} A, shunt {Rsh*1e3:.0f} mOhm: Vshunt {Vsh*1e3:.0f} mV, P {I*I*Rsh:.2f} W, CSA gain {G} -> {Vsh*G:.2f} V; offset 150 uV -> error {150e-6/Rsh*1e3:.1f} mA")
for Itest, Rig in ((1e-3, 1.5), (10e-3, 1.5), (10e-3, 0.5)):
    V = Itest * Rig
    print(f"continuity: {Itest*1e3:.0f} mA test current through a {Rig} ohm igniter -> {V*1e3:.1f} mV; open circuit -> test source compliance voltage; need offset << {V*1e3:.1f} mV")
