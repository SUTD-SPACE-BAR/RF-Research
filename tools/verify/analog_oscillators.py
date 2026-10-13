#!/usr/bin/env python3
"""Verification script for kb/05-analog-electronics/oscillators.md

 1. Colpitts negative resistance: exact input impedance of an ideal-gm device with C1 (b-e) and C2 (e-gnd)
    vs Z = 1/(jwC1) + 1/(jwC2) - gm/(w^2 C1 C2).
 2. Pierce crystal oscillator: load capacitance, C1 = C2 = 2 (CL - Cstray), gm_crit = 4 ESR w^2 (C0 + CL)^2,
    gain margin, pulling sensitivity ppm/pF, drive level. 32 MHz LoRa-type crystal example.
 3. BJT large-signal transconductance (describing function) Gm/gm = 2 I1(x)/(x I0(x)); steady amplitude vs
    start-up margin.
 4. Leeson phase-noise examples (LC VCO at 433 MHz, 32 MHz crystal).
 5. Wien bridge: closed-loop poles vs amplifier gain (oscillation at K = 3).
 6. ngspice transient of a BJT Colpitts oscillator: frequency vs formula, start-up.
Run: python3 tools/verify/analog_oscillators.py
"""
import os, sys
import numpy as np
from scipy.special import i0e, i1e
from scipy.optimize import brentq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
k = 1.380649e-23; T = 300.0; VT = 0.025852

print("=== 1. Colpitts negative resistance ===")
gm, C1, C2 = 20e-3, 100e-12, 100e-12
for f in (10e6, 50e6, 100e6):
    w = 2 * np.pi * f
    # nodes: base b (driven by test current It), emitter e. device current gm*(vb - ve) from collector (ac ground) into emitter
    # KCL b: It = jwC1 (vb - ve) ; KCL e: jwC1 (vb - ve) + gm (vb - ve) = jwC2 ve
    Y1, Y2 = 1j * w * C1, 1j * w * C2
    # from e: ve = (Y1 + gm)(vb - ve)/Y2 -> vbe = vb Y2/(Y1 + gm + Y2)
    vb = 1.0
    vbe = vb * Y2 / (Y1 + gm + Y2)
    It = Y1 * vbe
    Z = vb / It
    Zf = 1 / Y1 + 1 / Y2 - gm / (w**2 * C1 * C2)
    print(f"f={f/1e6:5.0f} MHz: exact Zin = {Z.real:9.2f} {Z.imag:+9.2f}j ohm ; formula {Zf.real:9.2f} {Zf.imag:+9.2f}j")

print("\n=== 2. Pierce crystal oscillator (32 MHz, CL = 10 pF) ===")
f0 = 32e6; ESR = 40.0; C0 = 1.5e-12; Cm = 5e-15; CL = 10e-12; Cstray = 3e-12
Cext = 2 * (CL - Cstray)
w = 2 * np.pi * f0
gm_crit = 4 * ESR * w**2 * (C0 + CL)**2
print(f"C1 = C2 = 2 (CL - Cstray) = {Cext*1e12:.1f} pF ; gm_crit = 4 ESR w^2 (C0+CL)^2 = {gm_crit*1e3:.3f} mA/V")
# cross-check: negative resistance of the inverter with C1=C2=2CL vs effective ESR (1 + C0/CL)^2
Rneg_per_gm = 1 / (w**2 * (2 * CL) * (2 * CL))
ESR_eff = ESR * (1 + C0 / CL)**2
print(f"  check: need gm/(w^2 C1 C2) > ESR (1+C0/CL)^2 -> gm > {ESR_eff/Rneg_per_gm*1e3:.3f} mA/V (same)")
for gm_ in (1e-3, 5e-3, 20e-3):
    print(f"  inverter gm = {gm_*1e3:5.1f} mA/V: gain margin gm/gm_crit = {gm_/gm_crit:5.1f} ({'OK' if gm_/gm_crit >= 5 else 'LOW'}; ST AN2867 recommends >= 5)")
S = -Cm / (2 * (C0 + CL)**2)  # df/f per farad
print(f"pulling sensitivity dF/F/dCL = -Cm/(2(C0+CL)^2) = {S*1e-12*1e6:.2f} ppm/pF")
for fc in (433e6, 868e6, 915e6):
    print(f"  1 pF load error -> {abs(S)*1e-12*1e6:.1f} ppm -> {abs(S)*1e-12*fc/1e3:.1f} kHz at {fc/1e6:.0f} MHz (LoRa BW 125 kHz)")
fL = f0 * (1 + Cm / (2 * (C0 + CL)))
print(f"load-resonance offset above series resonance: {(fL/f0-1)*1e6:.0f} ppm")
Vpp = 1.0
Irms = w * (C0 + CL) * Vpp / (2 * np.sqrt(2))
P = Irms**2 * ESR
print(f"drive level at 1 Vpp across crystal: I = {Irms*1e3:.3f} mA rms, P = I^2 ESR = {P*1e6:.1f} uW (compare the crystal's max drive level)")

print("\n=== 3. Large-signal Gm of a BJT (describing function) ===")
def Gm_ratio(x):
    return 2 * i1e(x) / (x * i0e(x))  # exponentially scaled -> no overflow
for x in (0.1, 1, 2, 5, 10, 20):
    print(f"x = V1/VT = {x:5.1f}: Gm/gm = {Gm_ratio(x):.4f}")
for margin in (2, 3, 5, 10):
    x = brentq(lambda x: Gm_ratio(x) - 1 / margin, 1e-3, 1e4)
    print(f"start-up margin {margin:2d}: steady state when Gm/gm = 1/{margin} -> x = {x:6.2f}, V1(b-e) = {x*VT*1e3:6.1f} mV peak")

print("\n=== 4. Leeson phase noise ===")
# W5-E9 fix (D6 #1, 2026-10-02): Leeson/Rubiola prefactor is F k T0 / (2 Ps) with Ps = carrier power at the
# sustaining-amplifier input and L = S_phi/2 (was 2FkT/Ps, which is Lee-Hajimiri's tank-power form, 6 dB higher).
# T0 = 290 K per CONVENTIONS. Monte-Carlo check of the white floor: tools/verify/fix_leeson_prefactor.py
Tref = 290.0
def leeson(df, f0, QL, Ps, F, fc):
    return 10 * np.log10((F * k * Tref / (2 * Ps)) * (1 + (f0 / (2 * QL * df))**2) * (1 + fc / df))
assert abs(10 * np.log10(k * Tref / (2 * 1e-3)) + 177.0) < 0.05, "white floor for F=1, 0 dBm must be -177 dBc/Hz"
for name, f0_, QL, Ps, F, fc in (("433 MHz LC VCO (QL=20, 0 dBm, F=3 dB, fc=10 kHz)", 433e6, 20, 1e-3, 2, 10e3),
                                  ("433 MHz LC VCO, QL=40", 433e6, 40, 1e-3, 2, 10e3),
                                  ("32 MHz crystal (QL=50k, -10 dBm, F=3 dB, fc=1 kHz)", 32e6, 5e4, 1e-4, 2, 1e3)):
    vals = ", ".join(f"{df/1e3:g} kHz: {leeson(df, f0_, QL, Ps, F, fc):6.1f}" for df in (1e2, 1e3, 1e4, 1e5, 1e6))
    print(f"{name}: L(df) dBc/Hz -> {vals}")
# multiplication of reference noise to RF: +20 log N
print(f"32 MHz reference multiplied to 915 MHz: +{20*np.log10(915/32):.1f} dB in-band")

print("\n=== 5. Wien bridge ===")
R = 10e3; C = 10e-9
for K in (2.9, 3.0, 3.1):
    # loop: beta(s) = sRC / ( (sRC)^2 + 3 sRC + 1 ); closed-loop char: (sRC)^2 + (3 - K) sRC + 1 = 0
    r = np.roots([ (R*C)**2, (3 - K) * R * C, 1])
    print(f"K={K}: poles {r[0]:.1f}, {r[1]:.1f} -> Re max = {max(r.real):+.1f} ; f = |pole|/2pi = {abs(r[0])/2/np.pi:.1f} Hz (1/(2 pi RC) = {1/(2*np.pi*R*C):.1f})")

print("\n=== 6. ngspice Colpitts ===")
try:
    from analog_ngspice import run_netlist
    net = """
* common-base Colpitts oscillator ~10 MHz (tank L1 with C1-C2 divider, feedback to emitter)
.model QC NPN(IS=1e-15 BF=200 VAF=50 TF=0.3n CJE=3p CJC=2p)
VCC vcc 0 DC 9 PULSE(0 9 0 1u)
L1 vcc c 2.2u
C1 c e 220p
C2 e 0 470p
RE e vee 2.2k
VEE vee 0 DC -3
Q1 c b e QC
RB b 0 100
CB b 0 100n
RL c vcc 10k
.tran 1n 60u 50u 1n
.end
"""
    r = run_netlist(net, ["time", "v(c)"])
    t = r["time"]; v = r["v(c)"]
    v = v - v.mean()
    zc = t[1:][(v[:-1] < 0) & (v[1:] >= 0)]
    fosc = 1 / np.mean(np.diff(zc))
    Cs = 220e-12 * 470e-12 / (220e-12 + 470e-12)
    fhand = 1 / (2 * np.pi * np.sqrt(2.2e-6 * Cs))
    print(f"ngspice f_osc = {fosc/1e6:.3f} MHz; hand 1/(2 pi sqrt(L C1C2/(C1+C2))) = {fhand/1e6:.3f} MHz; amplitude {np.ptp(v):.2f} V p-p at collector")
    IC = (3 - 0.7) / 2.2e3
    gm_ = IC / VT
    # start-up (CB Colpitts): needs gm > ~ (C1+C2)^2/(C1 C2 RL_eff) roughly; report margin via n = C1/(C1+C2)
    n = 220 / (220 + 470)
    T0 = gm_ * 10e3 * n * (1 - n)
    print(f"  bias IC ~ {IC*1e3:.2f} mA, gm = {gm_*1e3:.1f} mS, n = C1/(C1+C2) = {n:.3f}: small-signal loop gain ~ gm R n (1-n) = {T0:.0f} (>> 1: hard limiting, large swing)")
except Exception as e:
    print("ngspice skipped:", e)

print("\n=== 7. VCO tuning-line noise -> phase noise ===")
for Kv, vn in ((10e6, 10e-9), (10e6, 100e-9), (1e6, 10e-9)):
    for df in (1e3, 10e3, 100e3):
        L = 20 * np.log10(Kv * vn / (np.sqrt(2) * df))
        print(f"K={Kv/1e6:4.0f} MHz/V, vn={vn*1e9:5.0f} nV/rtHz: L({df/1e3:5.0f} kHz) = {L:7.1f} dBc/Hz")
print("frequency-sensitivity to phase: 1 deg -> df/f = (pi/180)/(2Q):", {Q: round(np.pi/180/(2*Q)*1e6, 2) for Q in (50, 5e4)}, "ppm")
