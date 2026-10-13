#!/usr/bin/env python3
"""Verification script for kb/05-analog-electronics/low-noise-analog-design.md

 1. en-in model: F(Rs), Ropt = en/in, Fmin = 1 + en in/(2kT); correlated case.
 2. Op-amp NF vs source resistance (OPA1612, MCP6002, BF862 JFET); transformer step-up to Ropt.
 3. Paralleling N devices: en/sqrt(N), in*sqrt(N).
 4. Resistor excess (current) noise from the noise index (uV/V per decade) vs thermal noise.
 5. kT/C noise.
 6. Equivalent noise bandwidth of Butterworth low-pass filters (orders 1-4) vs TI table (1.57, 1.11, 1.05, 1.025).
 7. Photodiode TIA output noise: Rf thermal, in, and en times the noise-gain peaking (1 + Cin/Cf).
 8. Non-inverting gain stage: noise figure including feedback resistors.
Run: python3 tools/verify/analog_noise.py
"""
import numpy as np
from scipy import integrate, signal

k = 1.380649e-23; q = 1.602176634e-19; T = 290.0; kT = k * T

def F_of_Rs(en, inn, Rs, C=0.0):
    return 1 + (en**2 + inn**2 * Rs**2 + 2 * C * en * inn * Rs) / (4 * kT * Rs)

print("=== 1/2. en-in model and op-amp noise figure vs Rs (T0 = 290 K) ===")
devs = (("OPA1612 bipolar", 1.1e-9, 1.7e-12), ("MCP6002 CMOS", 28e-9, 0.6e-15), ("BF862 JFET", 0.8e-9, 2e-15))
for name, en, inn in devs:
    Ropt = en / inn
    Fmin = 1 + en * inn / (2 * kT)
    row = []
    for Rs in (50, 600, 10e3, 1e6):
        row.append(f"Rs={Rs:>8.0f}: NF={10*np.log10(F_of_Rs(en, inn, Rs)):6.2f} dB")
    print(f"{name:16s}: Ropt = en/in = {Ropt:12.0f} ohm, NFmin = {10*np.log10(Fmin):.3f} dB | " + " | ".join(row))
# brute-force check of Ropt and Fmin
en, inn = 1.1e-9, 1.7e-12
Rs = np.logspace(0, 6, 200001)
F = F_of_Rs(en, inn, Rs)
print(f"brute force OPA1612: Ropt = {Rs[np.argmin(F)]:.1f} ohm, NFmin = {10*np.log10(F.min()):.3f} dB")
# correlation: F = 1 + (en^2 + in^2 Rs^2 + 2C en in Rs)/(4kT Rs) -> Ropt unchanged (real C), Fmin = 1 + en in (1 + C)/(2kT)
for C in (-0.5, 0.0, 0.5):
    Fm = F_of_Rs(en, inn, Rs, C).min()
    print(f"  correlation C={C:+.1f}: NFmin = {10*np.log10(Fm):.3f} dB (formula 1 + en in (1+C)/(2kT) -> {10*np.log10(1+en*inn*(1+C)/(2*kT)):.3f})")
# transformer: 50 ohm source stepped up to Ropt
n = np.sqrt((en / inn) / 50)
print(f"transformer turns ratio sqrt(Ropt/50) = {n:.2f}: NF from {10*np.log10(F_of_Rs(en,inn,50)):.2f} dB to {10*np.log10(F_of_Rs(en,inn,50*n*n)):.2f} dB (lossless transformer)")

print("\n=== 3. Paralleling N devices ===")
for N in (1, 2, 4, 8):
    enN, inN = en / np.sqrt(N), inn * np.sqrt(N)
    print(f"N={N}: en={enN*1e9:.3f} nV/rtHz, in={inN*1e12:.2f} pA/rtHz, Ropt={enN/inN:6.1f} ohm, NF at 50 ohm = {10*np.log10(F_of_Rs(enN,inN,50)):.2f} dB, NFmin unchanged {10*np.log10(1+enN*inN/(2*kT)):.3f} dB")

print("\n=== 4. Resistor excess noise from noise index ===")
def excess_density(NI_dB, Vdc, f):
    ni = 10**(NI_dB / 20) * 1e-6  # V rms per V per decade
    Kf = (ni * Vdc)**2 / np.log(10)  # e^2(f) = Kf / f, integral over a decade = Kf ln 10
    return np.sqrt(Kf / f)
R = 10e3
thermal = np.sqrt(4 * k * 300 * R)
for NI in (0, -20, -35, -40):
    for Vdc in (0.1, 2.5):
        d10 = excess_density(NI, Vdc, 10); d1k = excess_density(NI, Vdc, 1e3)
        print(f"NI={NI:+4d} dB, Vdc={Vdc:3.1f} V: excess {d10*1e9:8.1f} nV/rtHz @10 Hz, {d1k*1e9:7.2f} @1 kHz (10k thermal {thermal*1e9:.1f})")
# check: integral over 1-10 Hz of excess density^2 = (NI*V)^2
ni = 1e-6; V = 1.0
val = np.sqrt(integrate.quad(lambda f: excess_density(0, V, f)**2, 100, 1000)[0])
print(f"check: rms in one decade for NI = 0 dB, 1 V = {val*1e6:.3f} uV (should be 1.000)")

print("\n=== 5. kT/C noise ===")
for C in (1e-12, 10e-12, 100e-12, 1e-9):
    print(f"C={C*1e12:7.1f} pF: sqrt(kT/C) at 300 K = {np.sqrt(k*300/C)*1e6:7.2f} uV rms")

print("\n=== 6. ENBW of Butterworth low-pass ===")
for nord in (1, 2, 3, 4):
    b, a = signal.butter(nord, 1.0, analog=True)
    H2 = lambda w: abs(np.polyval(b, 1j * w) / np.polyval(a, 1j * w))**2
    enbw = integrate.quad(H2, 0, np.inf, limit=500)[0]
    closed = (np.pi / (2 * nord)) / np.sin(np.pi / (2 * nord))
    print(f"order {nord}: ENBW/f3dB numeric {enbw:.4f}, closed form (pi/2n)/sin(pi/2n) = {closed:.4f}")

print("\n=== 7. Photodiode TIA noise ===")
Rf, Cf, Cin, GBW = 100e3, 1.8e-12, 20e-12, 10e6
en_, in_ = 7e-9, 2e-15  # CMOS/JFET-input op-amp class
f = np.logspace(0, 8, 200000)
w = 2 * np.pi * f
Zf = Rf / (1 + 1j * w * Rf * Cf)
beta = 1 / (1 + Zf * 1j * w * Cin)  # Zg = 1/(jw Cin)
A = (2 * np.pi * GBW) / (1j * w)
loop = A * beta / (1 + A * beta)
NG = 1 / beta
e_en = np.abs(en_ * NG * loop)
e_in = np.abs(in_ * Zf * loop)
e_rf = np.abs(np.sqrt(4 * k * 300 * Rf) * (Zf / Rf) * loop)
tot = np.sqrt(e_en**2 + e_in**2 + e_rf**2)
for name, e in (("en x noise gain", e_en), ("in x Zf", e_in), ("Rf thermal", e_rf), ("total", tot)):
    rms = np.sqrt(np.trapezoid(e**2, f))
    print(f"  {name:16s}: {rms*1e6:7.2f} uV rms (1 Hz-100 MHz)")
print(f"  HF noise-gain plateau 1 + Cin/Cf = {1+Cin/Cf:.1f}; signal BW 1/(2 pi Rf Cf) = {1/(2*np.pi*Rf*Cf)/1e3:.0f} kHz; noise-gain zero at {1/(2*np.pi*Rf*(Cin+Cf))/1e3:.0f} kHz")

print("\n=== 8. Noise figure of a non-inverting op-amp stage including feedback resistors ===")
en, inn = 1.1e-9, 1.7e-12
Rs = 50.0
for Rf_, Rg_ in ((1e3, 100.0), (100.0, 10.0), (10e3, 1e3)):
    Rp = Rf_ * Rg_ / (Rf_ + Rg_)
    ntot = en**2 + inn**2 * (Rs**2 + Rp**2) + 4 * kT * Rp
    F = 1 + ntot / (4 * kT * Rs)
    print(f"Rs=50, Rf={Rf_:.0f}, Rg={Rg_:.0f} (Rf||Rg={Rp:.0f}): NF = {10*np.log10(F):.2f} dB")
