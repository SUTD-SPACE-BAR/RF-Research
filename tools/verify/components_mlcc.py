#!/usr/bin/env python3
"""
Verification for kb/04-real-components-hf/capacitors-at-rf-mlcc.md

  1. ESL implied by published series-resonant frequencies (ATC/Kyocera-AVX coupling-cap table).
  2. SRF vs capacitance for a range of mounted ESL values (0.15 ... 1.2 nH).
  3. DC-block selection at 433.92 / 915 / 2450 MHz: S21 of a series capacitor (C, ESL, ESR) in 50 ohm.
  4. Capacitor Q = |X_net| / ESR at UHF for GJM-class ESR limits.
  5. Parallel-capacitor anti-resonance: 100 nF || 100 pF vs 2 x 100 nF vs 100 nF || 1 nF, peak |Z|
     and how ESR damps it; behaviour at 433 / 915 MHz.
  6. Class-2 derating arithmetic: DC bias example (Maxim/ADI 4.7 uF -> 0.33 uF), ageing law, temperature.
Run: python3 tools/verify/components_mlcc.py
"""
import numpy as np
TP = 2 * np.pi

def zcap(f, C, L, R):
    w = TP * f
    return R + 1j * w * L + 1 / (1j * w * C)

print("=== 1. ESL implied by ATC measured FSR (series-thru, microstrip) ===")
atc = [("ATC 100A101 (55x55 mil)", 100e-12, 1000e6, 0.072), ("ATC 600S101 (0603)", 100e-12, 1340e6, 0.070),
       ("ATC 100A270", 27e-12, 1870e6, 0.161), ("ATC 600S560 (0603)", 56e-12, 1890e6, 0.085),
       ("ATC 100A160", 16e-12, 2410e6, 0.218), ("ATC 600S390 (0603)", 39e-12, 2340e6, 0.140)]
for name, C, fsr, esr in atc:
    L = 1 / ((TP * fsr)**2 * C)
    print(f"{name:26s}: C={C*1e12:5.0f} pF, FSR={fsr/1e6:6.0f} MHz -> ESL = {L*1e9:.3f} nH ; ESR@FSR = {esr} ohm")

print("\n=== 2. SRF (MHz) vs C for mounted ESL ===")
Cs = [1e-12, 3.3e-12, 10e-12, 33e-12, 100e-12, 330e-12, 1e-9, 10e-9, 100e-9, 1e-6, 10e-6]
Ls = [0.15e-9, 0.3e-9, 0.5e-9, 0.7e-9, 1.2e-9]
print("C".ljust(10) + "".join(f"L={L*1e9:.2f}nH".rjust(12) for L in Ls))
for C in Cs:
    lab = f"{C*1e12:.1f} pF" if C < 1e-9 else (f"{C*1e9:.0f} nF" if C < 1e-6 else f"{C*1e6:.0f} uF")
    print(lab.ljust(10) + "".join(f"{1/(TP*np.sqrt(L*C))/1e6:12.1f}" for L in Ls))

print("\n=== 3. DC block: |S21| (dB) of a series cap in 50 ohm; ESL = 0.4 nH, ESR = 0.1 ohm ===")
Z0 = 50.0
freqs = [433.92e6, 915e6, 2450e6]
print("C".ljust(9) + "".join(f"{f/1e6:10.0f}MHz" for f in freqs) + "   (SRF MHz)")
for C in [3.3e-12, 10e-12, 22e-12, 47e-12, 100e-12, 330e-12, 1e-9, 10e-9, 100e-9]:
    row = []
    for f in freqs:
        Z = zcap(f, C, 0.4e-9, 0.1)
        s21 = 2 * Z0 / (2 * Z0 + Z)
        row.append(20 * np.log10(abs(s21)))
    lab = f"{C*1e12:.1f}p" if C < 1e-9 else f"{C*1e9:.0f}n"
    print(lab.ljust(9) + "".join(f"{v:13.3f}" for v in row) + f"   ({1/(TP*np.sqrt(0.4e-9*C))/1e6:.0f})")
print("ideal C for SRF = f with ESL 0.4 nH:", ", ".join(f"{f/1e6:.0f} MHz -> {1/((TP*f)**2*0.4e-9)*1e12:.1f} pF" for f in freqs))
# acceptance: |X_net| giving 0.05 dB loss
x05 = 2 * Z0 * np.sqrt(10**(0.05 / 10) - 1)
print(f"|X_net| for 0.05 dB series loss in 50 ohm = {x05:.1f} ohm; for 0.1 dB = {2*Z0*np.sqrt(10**(0.1/10)-1):.1f} ohm")

print("\n=== 4. Capacitor Q at 433.92 and 915 MHz (ESL 0.35 nH) ===")
for C, esr in [(1e-12, 0.30), (3.3e-12, 0.30), (10e-12, 0.25), (22e-12, 0.40), (100e-12, 0.07)]:
    for f in [433.92e6, 915e6]:
        Z = zcap(f, C, 0.35e-9, esr)
        print(f"  C={C*1e12:5.1f} pF, ESR={esr} ohm, f={f/1e6:.0f} MHz: X_net={Z.imag:8.2f} ohm, Q={abs(Z.imag)/esr:7.0f}")

print("\n=== 5. Parallel capacitor anti-resonance (each with 0.5 nH mounted ESL) ===")
f = np.logspace(6, 10, 40001)
def zpar(*caps):
    Y = sum(1 / zcap(f, C, L, R) for C, L, R in caps)
    return 1 / Y
cases = {
    "100 nF alone": [(100e-9, 0.5e-9, 0.02)],
    "2 x 100 nF": [(100e-9, 0.5e-9, 0.02), (100e-9, 0.5e-9, 0.02)],
    "100 nF || 100 pF (ESR 20m/100m)": [(100e-9, 0.5e-9, 0.02), (100e-12, 0.5e-9, 0.1)],
    "100 nF || 100 pF (low ESR 20m/20m)": [(100e-9, 0.5e-9, 0.02), (100e-12, 0.5e-9, 0.02)],
    "100 nF || 1 nF": [(100e-9, 0.5e-9, 0.02), (1e-9, 0.5e-9, 0.05)],
    "100 nF || 100 pF, 100pF ESL 0.3nH": [(100e-9, 0.5e-9, 0.02), (100e-12, 0.3e-9, 0.1)],
}
for name, caps in cases.items():
    Z = np.abs(zpar(*caps))
    # find anti-resonance peak between 30 MHz and 3 GHz
    from scipy.signal import find_peaks
    pk, _ = find_peaks(Z)
    peaks = ", ".join(f"{Z[i]:.2f} ohm @ {f[i]/1e6:.0f} MHz" for i in pk) or "none (monotonic)"
    z433 = Z[np.argmin(np.abs(f - 433.92e6))]
    z915 = Z[np.argmin(np.abs(f - 915e6))]
    zmin = Z.min(); fmin = f[np.argmin(Z)]
    print(f"{name:36s}: min |Z| {zmin*1e3:6.1f} mohm @ {fmin/1e6:5.1f} MHz; anti-resonance: {peaks};"
          f" |Z|(433.92)={z433:.2f}, |Z|(915)={z915:.2f} ohm")

print("\n=== 6. Class-2 derating arithmetic ===")
print(f"  Maxim/ADI example: 4.7 uF 6.3 V 0603 X5R at 5 V -> 0.33 uF = {0.33/4.7*100:.1f} % of nominal ({(1-0.33/4.7)*100:.1f} % loss)")
for k_age, name in [(2.5, "X7R/X5R"), (7.0, "Y5V")]:
    for t in [1000, 87600]:
        loss = k_age * np.log10(t / 1.0)
        print(f"  ageing {name} ({k_age} %/decade-hour) from 1 h to {t} h: {loss:.1f} % (relative to the 1 h value)")
dT = np.array([-40 - 25, 85 - 25, 125 - 25])
print(f"  C0G +/-30 ppm/K over -40..+125 C: worst {np.max(np.abs(dT))*30e-6*100:.2f} %  (X7R allowed +/-15 %)")
print("OK")
