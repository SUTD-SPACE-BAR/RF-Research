#!/usr/bin/env python3
"""
Verification for kb/04-real-components-hf/crystals-and-resonators.md

  1. Butterworth-Van Dyke model of the SX1261/2 reference crystal (32 MHz, Cm 1.89 fF, C0 0.6 pF,
     R 30 ohm, CL 10 pF): Lm, Q, fs, fp, load resonance, pulling sensitivity; numerical impedance check.
  2. Vig's pulling example (C0 5 pF, C1 14 fF, CL 20 pF).
  3. Load capacitors for a given CL and stray; SX126x internal trim-cap range -> pulling range.
  4. Pierce oscillator critical gm and gain margin; drive level.
  5. ppm -> Hz at 433.92 / 915 MHz; LoRa tolerances (+/-25 % BW offset, SF-dependent ppm limits,
     in-packet drift BW/(3*2^SF), x16 with LDRO).
  6. AT-cut cubic f(T): optimal first-order coefficient for a temperature range; slope near 25 C.
  7. Rocket environment: g-sensitivity during boost, vibration sidebands, and (for context) Doppler rate.
Run: python3 tools/verify/components_crystal.py
"""
import numpy as np
TP = 2 * np.pi

print("=== 1. BVD model, SX1261/2 reference crystal ===")
fs_target = 32e6
Cm, C0, R1, CL = 1.89e-15, 0.6e-12, 30.0, 10e-12
Lm = 1 / ((TP * fs_target)**2 * Cm)
Q = TP * fs_target * Lm / R1
fs = 1 / (TP * np.sqrt(Lm * Cm))
fp = fs * np.sqrt(1 + Cm / C0)
fL = fs * (1 + Cm / (2 * (C0 + CL)))
S = -Cm / (2 * (C0 + CL)**2)          # fractional per farad
print(f"Lm = {Lm*1e3:.2f} mH, Q = {Q:,.0f}, fs = {fs/1e6:.6f} MHz, fp - fs = {(fp-fs)/1e3:.2f} kHz ({(fp/fs-1)*1e6:.0f} ppm)")
print(f"load resonance with CL = 10 pF: fL - fs = {(fL-fs):.0f} Hz ({(fL/fs-1)*1e6:.1f} ppm above fs)")
print(f"pulling sensitivity at CL = 10 pF: {S*1e-12*1e6:.2f} ppm/pF")
# numerical check: find where crystal reactance = +1/(w CL) (i.e., crystal + CL in series resonates)
f = np.linspace(fs - 2e3, fs + 3e4, 2000001)
w = TP * f
Zm = R1 + 1j * w * Lm + 1 / (1j * w * Cm)
Zx = 1 / (1 / Zm + 1j * w * C0)
Ztot = Zx + 1 / (1j * w * CL)
i = np.argmin(np.abs(Ztot.imag))
print(f"numerical series resonance of crystal + CL: {(f[i]-fs):.1f} Hz above fs (formula {(fL-fs):.1f})")
assert abs((f[i] - fs) - (fL - fs)) < 2.0

print("\n=== 2. Vig pulling example ===")
C0v, C1v, CLv = 5e-12, 14e-15, 20e-12
dCL = 10e-15
df = C1v / (2 * (C0v + CLv)**2) * dCL
print(f"dCL = 10 fF -> df/f = {df:.2e} (Vig: 1e-7)")

print("\n=== 3. Load capacitors ===")
for CLspec in [8e-12, 10e-12, 12e-12]:
    for Cs in [2e-12, 3e-12, 5e-12]:
        Cext = 2 * (CLspec - Cs)
        print(f"  CL = {CLspec*1e12:.0f} pF, stray {Cs*1e12:.0f} pF -> C1 = C2 = {Cext*1e12:.1f} pF (nearest E12/E24 then trim)")
Cs = 1.5e-12
for Cfoot in [11.3e-12, 19.7e-12, 33.4e-12]:
    CLeff = Cfoot / 2 + Cs
    ppm = (Cm / (2 * (C0 + CLeff)) - Cm / (2 * (C0 + CL))) * 1e6
    print(f"  SX126x trim caps both = {Cfoot*1e12:.1f} pF -> CL ~ {CLeff*1e12:.2f} pF -> offset vs CL=10 pF: {ppm:+.1f} ppm")

print("\n=== 4. Pierce oscillator ===")
gm_crit = 4 * R1 * (TP * fs)**2 * (C0 + CL)**2
print(f"gm_crit = 4 ESR w^2 (C0+CL)^2 = {gm_crit*1e3:.3f} mA/V ; for gain margin 5: gm >= {5*gm_crit*1e3:.2f} mA/V")
for P in [10e-6, 100e-6]:
    Irms = np.sqrt(P / R1)
    print(f"drive level {P*1e6:.0f} uW in R1 = 30 ohm -> I_rms = {Irms*1e3:.2f} mA")

print("\n=== 5. ppm -> Hz and LoRa limits ===")
for fc in [433.92e6, 868e6, 915e6]:
    print(f"  {fc/1e6:.2f} MHz: 1 ppm = {fc*1e-6:.1f} Hz; +/-10 ppm = {10*fc*1e-6/1e3:.2f} kHz; +/-30 ppm = {30*fc*1e-6/1e3:.2f} kHz")
BWs = [7.8e3, 10.4e3, 15.6e3, 20.8e3, 31.25e3, 41.7e3, 62.5e3, 125e3, 250e3, 500e3]
print("  BW(kHz)  +/-25%BW(Hz)  allowed TX-RX offset ppm @433.92 / @915   (each end ~half of that)")
for bw in BWs:
    off = 0.25 * bw
    print(f"  {bw/1e3:7.2f}  {off:10.0f}     {off/433.92e6*1e6:6.2f} / {off/915e6*1e6:6.2f}")
print("  in-packet drift limit BW/(3*2^SF) [Hz] (x16 with LowDataRateOptimize):")
for sf in [7, 9, 10, 11, 12]:
    row = []
    for bw in [62.5e3, 125e3, 250e3]:
        row.append(f"BW{bw/1e3:g}k: {bw/(3*2**sf):7.2f}")
    Ts = 2**sf / 125e3
    print(f"   SF{sf:2d} (Tsym@125k = {Ts*1e3:6.2f} ms): " + ", ".join(row))
lim = 125e3 / (3 * 2**12)
print(f"  SF12/BW125: {lim:.1f} Hz -> {lim/915e6*1e9:.1f} ppb at 915 MHz; with LDRO {16*lim:.0f} Hz = {16*lim/915e6*1e9:.0f} ppb")

print("\n=== 6. AT-cut cubic ===")
a3 = 1.095e-4   # ppm/K^3 (assumed third-order coefficient, Bechmann-type model)
T0 = 25.0
for Tlo, Thi in [(-20, 70), (-40, 85), (-40, 105)]:
    X = max(T0 - Tlo, Thi - T0)
    # optimal a1 for symmetric interval [-X, X]: equiripple a1 = -(3/4) a3 X^2, max dev = a3 X^3/4
    a1 = -0.75 * a3 * X**2
    T = np.linspace(Tlo, Thi, 1001)
    dev = a1 * (T - T0) + a3 * (T - T0)**3
    print(f"  {Tlo}..{Thi} C: best a1 = {a1:.3f} ppm/K (cut-angle offset ~{a1/-0.0847:.1f} arcmin if dA1/dtheta = -0.0847 ppm/K/arcmin)"
          f" -> max |df/f| = {np.max(np.abs(dev)):.2f} ppm; slope at 25 C = {a1:.3f} ppm/K, at {Thi} C = {a1+3*a3*(Thi-T0)**2:.2f} ppm/K")
a1 = -0.75 * a3 * 60**2
dT_allowed = (16 * lim / 915e6 * 1e6) / abs(a1)
print(f"  with slope {a1:.2f} ppm/K near 25 C, SF12/BW125 + LDRO allows only {dT_allowed:.2f} K of crystal warming during a packet")

print("\n=== 7. Rocket environment ===")
gamma = 2e-9    # 2 ppb/g (Semtech AN1200.14 'typical' low-g crystal)
for g in [5, 15, 30]:
    for fc in [433.92e6, 915e6]:
        print(f"  {g:2d} g static accel, {gamma*1e9:.0f} ppb/g: df = {gamma*g*fc:.1f} Hz at {fc/1e6:.0f} MHz")
fv, arms = 100.0, 10.0
for fc in [433.92e6, 915e6]:
    dfpk = gamma * arms * np.sqrt(2) * fc
    beta = dfpk / fv
    sb = 20 * np.log10(beta / 2)
    print(f"  vibration {arms} g rms @ {fv:.0f} Hz at {fc/1e6:.0f} MHz: peak df = {dfpk:.1f} Hz, beta = {beta:.3f} rad, sidebands {sb:.1f} dBc")
v, a = 300.0, 100.0
for fc in [433.92e6, 915e6]:
    print(f"  Doppler at {fc/1e6:.0f} MHz: {v} m/s -> {fc*v/3e8:.0f} Hz; {a} m/s^2 -> {fc*a/3e8:.0f} Hz/s "
          f"(SF12/BW125 packet ~1.5 s: {1.5*fc*a/3e8:.0f} Hz change)")
print("OK")
