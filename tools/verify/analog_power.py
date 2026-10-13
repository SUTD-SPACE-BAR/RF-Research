#!/usr/bin/env python3
"""Verification script for kb/05-analog-electronics/power-supplies-for-rf-and-analog.md

 1. LDO noise conversions (TPS7A20 7 uVrms 10 Hz-100 kHz; AMS1117 0.003 % of Vout 10 Hz-10 kHz).
 2. Buck converter ripple: inductor ripple current and output ripple (capacitive + ESR), with MLCC DC-bias derating.
 3. Post-regulation: ripple through an LDO with frequency-dependent PSRR (TPS7A20 table) and through an LC filter.
 4. LC / ferrite-bead filter resonance: undamped peaking, and damping with an R-C leg (Rd, Cd = n C).
 5. Supply ripple -> spurs: VCO pushing (narrowband FM) and PA supply AM.
 6. 1S battery + buck-boost feeding a 1-1.2 A LoRa PA burst: input current, droop, ground IR shift in ADC LSBs,
    bulk capacitance for a given droop if the source is current-limited.
 7. Ground bounce L di/dt examples.
Run: python3 tools/verify/analog_power.py
"""
import numpy as np
from scipy import signal

print("=== 1. LDO noise ===")
for name, vrms, f1, f2 in (("TPS7A20 (300 mA)", 7e-6, 10, 100e3), ("TPS7A20 (1 mA)", 10e-6, 10, 100e3), ("AMS1117-3.3 (0.003 % Vout)", 3.3 * 3e-5, 10, 10e3)):
    dens = vrms / np.sqrt(f2 - f1)
    print(f"{name:28s}: {vrms*1e6:6.1f} uVrms over {f1:.0f} Hz-{f2/1e3:.0f} kHz -> average density {dens*1e9:7.1f} nV/rtHz (if white)")
print("  12-bit ADC LSB on 3.3 V = 806 uV; 16-bit on 3.3 V = 50 uV")

print("\n=== 2. Buck ripple (5 V -> 3.3 V, 2 MHz, L = 2.2 uH, C = 22 uF 0805 X5R) ===")
Vin, Vout, fsw, L = 5.0, 3.3, 2e6, 2.2e-6
D = Vout / Vin
dI = (Vin - Vout) * D / (L * fsw)
for Ceff, ESR in ((22e-6, 5e-3), (10e-6, 5e-3), (10e-6, 20e-3)):
    dv_c = dI / (8 * fsw * Ceff)
    dv_esr = dI * ESR
    print(f"D={D:.2f}, dI={dI*1e3:.0f} mA p-p; Ceff={Ceff*1e6:4.0f} uF ESR={ESR*1e3:3.0f} mOhm: ripple C-part {dv_c*1e3:.2f} mV + ESR-part {dv_esr*1e3:.2f} mV (p-p, they are in quadrature-ish; sum is conservative)")
print("  note: a 22 uF 6.3 V 0805 X5R can lose ~50 % or more at 3.3 V DC bias -> use the derated value")

print("\n=== 3. Post-regulation ===")
psrr_tab = {100: 65, 1e3: 92, 10e3: 75, 100e3: 60, 1e6: 40}  # TPS7A20 at 300 mA, VIN = VOUT + 1 V
ripple = 10e-3
for f, p in psrr_tab.items():
    print(f"TPS7A20 (300 mA) PSRR {p} dB at {f/1e3:7.1f} kHz: {ripple*1e3:.0f} mV ripple -> {ripple/10**(p/20)*1e6:8.2f} uV")
def lc_tf(f, L, C, Rload, Rdcr=0.0, Rd=None, Cd=None):
    w = 2 * np.pi * f; s = 1j * w
    ZL = s * L + Rdcr
    Yc = s * C + 1 / Rload
    if Rd is not None:
        Yc = Yc + 1 / (Rd + 1 / (s * Cd))
    return 1 / (1 + ZL * Yc)
f = np.logspace(2, 8, 6001)
Lf, Cf, Rl = 1e-6, 10e-6, 3.3 / 0.3
H = lc_tf(f, Lf, Cf, Rl, Rdcr=0.05)
fr = 1 / (2 * np.pi * np.sqrt(Lf * Cf))
Z0 = np.sqrt(Lf / Cf)
print(f"LC filter L=1 uH (DCR 50 mOhm), C=10 uF, load 11 ohm: fr = {fr/1e3:.1f} kHz, Z0 = {Z0:.3f} ohm, peak {20*np.log10(abs(H).max()):+.1f} dB at {f[np.argmax(abs(H))]/1e3:.1f} kHz; at 2 MHz {20*np.log10(abs(H[np.argmin(abs(f-2e6))])):.1f} dB")
for n in (1, 4):
    for Rd_mult in (0.5, 1.0, 2.0):
        Hd = lc_tf(f, Lf, Cf, Rl, Rdcr=0.05, Rd=Rd_mult * Z0, Cd=n * Cf)
        print(f"  + damping leg Rd = {Rd_mult:.1f} Z0 ({Rd_mult*Z0:.3f} ohm) in series with Cd = {n} C: peak {20*np.log10(abs(Hd).max()):+.2f} dB; at 2 MHz {20*np.log10(abs(Hd[np.argmin(abs(f-2e6))])):.1f} dB")

print("\n=== 4. Ferrite bead + MLCC resonance ===")
# bead low-frequency behaviour ~ inductor (e.g. 1.5 uH) with DCR 0.1 ohm; above ~10 MHz becomes resistive (ignored here)
for Lb, DCR, C in ((1.5e-6, 0.1, 10e-6), (1.5e-6, 0.1, 1e-6), (0.3e-6, 0.05, 10e-6)):
    Hb = lc_tf(f, Lb, C, 1e3, Rdcr=DCR)
    frb = 1 / (2 * np.pi * np.sqrt(Lb * C)); Qb = np.sqrt(Lb / C) / DCR
    print(f"bead L~{Lb*1e6:.1f} uH DCR {DCR} + C {C*1e6:.0f} uF (light load): fr = {frb/1e3:6.1f} kHz, Q ~ {Qb:4.1f}, peak gain {20*np.log10(abs(Hb).max()):+.1f} dB")

print("\n=== 5. Ripple -> spurs ===")
for Kp, Vr, fr_ in ((1e6, 1e-3, 1e6), (5e6, 1e-3, 1e6), (1e6, 1e-3, 100e3), (1e6, 100e-6, 1e6)):
    beta = Kp * Vr / fr_
    print(f"VCO pushing {Kp/1e6:.0f} MHz/V, ripple {Vr*1e3:.2f} mV pk at {fr_/1e3:.0f} kHz: beta = {beta:.2e} -> each sideband {20*np.log10(beta/2):6.1f} dBc")
for Vr, Vdd in ((10e-3, 5.0), (50e-3, 5.0), (10e-3, 3.3)):
    m = Vr / Vdd
    print(f"saturated PA, amplitude ~ Vdd: {Vr*1e3:.0f} mV pk ripple on {Vdd} V -> AM sidebands {20*np.log10(m/2):6.1f} dBc")

print("\n=== 6. 1S battery feeding a 5 V buck-boost for a LoRa PA burst ===")
Vbatt_list = (4.2, 3.7, 3.3)
Iload, Vrad, eta = 1.2, 5.0, 0.88
Rint, Rwire = 0.10, 0.03
for Vb in Vbatt_list:
    # solve Iin with droop: Iin = P/(eta (Vb - Iin R))
    P = Vrad * Iload
    R = Rint + Rwire
    disc = Vb**2 - 4 * R * P / eta
    Iin = (Vb - np.sqrt(disc)) / (2 * R)
    Vterm = Vb - Iin * R
    print(f"Vbatt {Vb:.1f} V: Iin = {Iin:.2f} A, terminal droop {Iin*R*1e3:.0f} mV -> {Vterm:.2f} V at the converter (R_int {Rint*1e3:.0f} + wiring {Rwire*1e3:.0f} mOhm)")
for Rgnd in (1e-3, 5e-3, 20e-3):
    dv = Iload * Rgnd
    print(f"shared ground return {Rgnd*1e3:4.0f} mOhm x {Iload} A = {dv*1e3:5.1f} mV shift = {dv/(3.3/4096):5.1f} LSB (12-bit, 3.3 V) / {dv/(3.3/65536):6.0f} LSB (16-bit)")
for dV, dt in ((0.1, 100e-6), (0.1, 1e-3)):
    C = Iload * dt / dV
    print(f"bulk C to supply {Iload} A for {dt*1e6:.0f} us with {dV*1e3:.0f} mV droop (source current-limited): {C*1e6:.0f} uF")

print("\n=== 7. Ground bounce ===")
for L, dI, dt in ((5e-9, 1.0, 1e-6), (1e-9, 0.05, 1e-9), (10e-9, 1.2, 2e-6)):
    print(f"L={L*1e9:.0f} nH, dI={dI*1e3:.0f} mA in {dt*1e9:.0f} ns: V = L dI/dt = {L*dI/dt*1e3:.1f} mV")

print("\n=== 8. ngspice check of the page's damped LC filter netlist ===")
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from analog_ngspice import run_netlist
    net = """
* LC post-filter with damping leg; V1 = 1 V AC ripple source
V1 in 0 AC 1
L1 in a 1u
RL1 a out 0.05
C1 out 0 10u
Rd out d 0.316
Cd d 0 40u
Rload out 0 11
.ac dec 100 1k 10MEG
.end
"""
    r = run_netlist(net, ["frequency", "v(out)"])
    fr_ = np.real(r["frequency"]); h = np.abs(r["v(out)"])
    print(f"ngspice: peak {20*np.log10(h.max()):+.2f} dB at {fr_[np.argmax(h)]/1e3:.1f} kHz; at 2 MHz {20*np.log10(h[np.argmin(abs(fr_-2e6))]):.1f} dB")
except Exception as e:
    print("ngspice skipped:", e)
print(f"worked example 1: 5 mV x (-64 dB) x (-40 dB) = {5e-3*10**(-64/20)*10**(-40/20)*1e9:.0f} nV")
