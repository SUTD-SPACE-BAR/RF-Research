#!/usr/bin/env python3
"""
array_components.py — verification for kb/12-phased-arrays/phase-shifters-ttd-components.md

  1. Switched-line phase bit: phase = beta*dL grows linearly with frequency (it is a true-time-delay bit);
     phase error across a band when used as a "phase" bit.
  2. Loaded-line phase bit: shunt susceptance pair +-jB separated by a lambda/4 line of impedance Zc.
     Matching condition and phase difference found numerically from ABCD; compare with closed forms
     Zc = Z0/sqrt(1+b^2)  and  delta_phi = 2*atan(b)  (b = B Z0).
  3. Reflection-type phase shifter (3-dB 90° hybrid + two identical reactive loads): S21 = -j*Gamma_L;
     phase range with a varactor alone and with a series inductor (resonated), 2.4 GHz and 5.8 GHz examples.
  4. Vector modulator: phase/amplitude from I/Q weights; DAC-resolution phase error; I/Q gain imbalance and
     quadrature error -> phase/amplitude error vs set phase.
  5. Varactor analog phase shifter nonlinearity: Mini-Circuits JSPHS-2484+ datasheet table -> linearisation /
     calibration lookup needed; phase-vs-frequency spread.
  6. TTD sizing: delay span, bits, LSB-induced phase error at f_max for 8/16/32-element arrays; ADAR4002 ranges.
  7. Per-element budget example: an S-band/C-band element chain gain/NF (LNA -> 6-bit PS -> combiner).
"""
import numpy as np
from scipy.optimize import brentq

c0 = 299792458.0

print("=" * 78)
print("1. Switched-line bit (microstrip, eps_eff = 3.3)")
eeff = 3.3
for f0, bit in ((2.44e9, 90), (5.8e9, 45), (5.8e9, 180)):
    lam_g = c0 / f0 / np.sqrt(eeff)
    dL = bit / 360 * lam_g
    for fr in (0.95, 1.0, 1.05):
        ph = 360 * dL / (lam_g / fr)
        print(f"  f0={f0/1e9:.2f} GHz, {bit}° bit: ΔL = {dL*1e3:6.2f} mm; at {fr:.2f} f0 phase = {ph:7.2f}° (error {ph-bit:+6.2f}°)")

print("=" * 78)
print("2. Loaded-line bit (shunt ±jB, λ/4 line Zc) — numeric ABCD vs closed form")
Z0 = 50.0


def abcd_shunt(Y):
    return np.array([[1, 0], [Y, 1]], dtype=complex)


def abcd_line(Zc, th):
    return np.array([[np.cos(th), 1j * Zc * np.sin(th)], [1j * np.sin(th) / Zc, np.cos(th)]], dtype=complex)


def s_from_abcd(M, Z0=50.0):
    A, B, C, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
    den = A + B / Z0 + C * Z0 + D
    S11 = (A + B / Z0 - C * Z0 - D) / den
    S21 = 2 / den
    return S11, S21


for dphi_deg in (11.25, 22.5, 45.0):
    b = np.tan(np.radians(dphi_deg) / 2)
    Zc_pred = Z0 / np.sqrt(1 + b ** 2)
    out = []
    for sgn in (+1, -1):
        M = abcd_shunt(1j * sgn * b / Z0) @ abcd_line(Zc_pred, np.pi / 2) @ abcd_shunt(1j * sgn * b / Z0)
        S11, S21 = s_from_abcd(M)
        out.append((abs(S11), np.degrees(np.angle(S21))))
    dp = out[0][1] - out[1][1]
    print(f"  target Δφ={dphi_deg:6.2f}°: b=tan(Δφ/2)={b:.4f}, Zc={Zc_pred:.2f} Ω -> |S11| = {out[0][0]:.1e}/{out[1][0]:.1e}, "
          f"Δφ numeric = {abs(dp):.3f}°")
# bandwidth of 45° loaded-line bit
b = np.tan(np.radians(22.5)); Zc = Z0 / np.sqrt(1 + b ** 2)
for fr in (0.9, 0.95, 1.05, 1.1):
    ph = []
    for sgn in (+1, -1):
        # susceptance of a capacitor/inductor scales ~ with frequency; assume +B capacitive (∝ f), -B inductive (∝ 1/f)
        B = sgn * b / Z0 * (fr if sgn > 0 else 1 / fr)
        M = abcd_shunt(1j * B) @ abcd_line(Zc, np.pi / 2 * fr) @ abcd_shunt(1j * B)
        S11, S21 = s_from_abcd(M)
        ph.append(np.degrees(np.angle(S21)))
        rl = -20 * np.log10(abs(S11))
    print(f"    45° bit at {fr:.2f} f0: Δφ = {abs(ph[0]-ph[1]):6.2f}°, return loss (last state) {rl:5.1f} dB")

print("=" * 78)
print("3. Reflection-type phase shifter: S21 = -j Γ_L (ideal 90° hybrid, identical loads)")


def gamma(Z, Z0=50.0):
    return (Z - Z0) / (Z + Z0)


for f in (2.44e9, 5.8e9):
    w = 2 * np.pi * f
    Cmin, Cmax = 0.5e-12, 2.5e-12  # a 5:1 varactor
    for L in (0.0, 1.0 / (w ** 2 * np.sqrt(Cmin * Cmax))):
        ph = []
        for C in np.linspace(Cmin, Cmax, 201):
            Z = 1j * w * L + 1 / (1j * w * C)
            ph.append(np.angle(-1j * gamma(Z)))
        ph = np.unwrap(np.array(ph))
        rng_deg = np.degrees(ph.max() - ph.min())
        print(f"  f={f/1e9:.2f} GHz, varactor {Cmin*1e12:.1f}-{Cmax*1e12:.1f} pF, series L={L*1e9:5.2f} nH: phase range {rng_deg:6.1f}°")
    # with transformed load impedance (Z0 -> Zt via λ/4 transformer, i.e. loads see lower reference) — effect of reference
    for Zref in (50.0, 25.0, 15.0):
        L = 1.0 / (w ** 2 * np.sqrt(Cmin * Cmax))
        ph = []
        for C in np.linspace(Cmin, Cmax, 201):
            Z = 1j * w * L + 1 / (1j * w * C)
            ph.append(np.angle(gamma(Z, Zref)))
        ph = np.unwrap(np.array(ph))
        print(f"      resonated load referenced to {Zref:4.1f} Ω (impedance transformer): range {np.degrees(ph.max()-ph.min()):6.1f}°")

print("=" * 78)
print("4. Vector modulator")
for bits in (6, 8, 10):
    q = 2 / 2 ** bits
    errs = []
    aerr = []
    for ph in np.radians(np.arange(0, 360, 0.5)):
        I, Q = np.round(np.cos(ph) / q) * q, np.round(np.sin(ph) / q) * q
        errs.append(np.degrees(np.angle(np.exp(1j * (np.arctan2(Q, I) - ph)))))
        aerr.append(20 * np.log10(np.hypot(I, Q)))
    print(f"  {bits}-bit I/Q DACs (full scale ±1): max phase error {np.max(np.abs(errs)):.3f}°, rms {np.std(errs):.3f}°, amplitude ripple ±{np.max(np.abs(aerr)):.3f} dB")
for eps_db, dq in ((0.2, 1.0), (0.5, 3.0), (1.0, 5.0)):
    g = 10 ** (eps_db / 20)
    errs = []; amps = []
    for ph in np.radians(np.arange(0, 360, 1.0)):
        # set I=cos, Q=sin; Q path has gain g and phase (90+dq) instead of 90
        out = np.cos(ph) + g * np.sin(ph) * np.exp(1j * np.radians(90 + dq))
        errs.append(np.degrees(np.angle(out * np.exp(-1j * ph))))
        amps.append(20 * np.log10(abs(out)))
    errs = np.array(errs)
    print(f"  I/Q gain imbalance {eps_db} dB, quadrature error {dq}°: phase error pk {np.max(np.abs(errs-errs.mean())):.2f}° "
          f"(rms {np.std(errs):.2f}°), amplitude pk-pk {np.ptp(amps):.2f} dB -> calibrate with a 2-D LUT")

print("=" * 78)
print("5. JSPHS-2484+ (datasheet table, phase vs control voltage) — nonlinearity and frequency spread")
V = np.arange(0, 16)
P2150 = np.array([0.01, 5.06, 10.50, 17.42, 27.60, 42.79, 63.72, 89.57, 119.07, 151.83, 187.02, 222.21, 254.14, 280.85, 302.85, 320.70])
P2300 = np.array([0.00, 4.69, 9.70, 16.05, 25.25, 38.72, 56.65, 77.62, 99.77, 122.45, 145.74, 169.98, 195.10, 220.25, 244.62, 266.91])
P2484 = np.array([0.00, 4.22, 8.68, 14.29, 22.27, 33.71, 48.52, 65.24, 82.32, 99.06, 115.49, 135.24, 148.56, 165.52, 183.15, 201.15])
for name, P in (("2150", P2150), ("2300", P2300), ("2484", P2484)):
    slope = np.diff(P)
    print(f"  {name} MHz: 0→15 V phase {P[-1]:6.1f}°, slope min {slope.min():5.2f}°/V max {slope.max():5.2f}°/V (ratio {slope.max()/slope.min():4.1f}×)")
# spread between 2400 and 2484 at the voltage giving 90 deg at 2440 (interpolated between 2300 and 2484)
P2440 = P2300 + (P2484 - P2300) * (2440 - 2300) / (2484 - 2300)
v90 = np.interp(90, P2440, V)
print(f"  voltage for 90° at 2440 MHz (interp) ≈ {v90:.2f} V; phase at that V: 2300 MHz {np.interp(v90,V,P2300):.1f}°, 2484 MHz {np.interp(v90,V,P2484):.1f}°")
print("  -> a varactor phase shifter is NOT a TTD: its phase-frequency slope varies with setting; needs a per-frequency LUT")

print("=" * 78)
print("6. TTD sizing")
for N, d_mm, fmax, thmax in ((8, 25.84, 5.875e9, 60), (16, 25.84, 5.875e9, 60), (32, 15.0, 10.5e9, 45), (8, 14.0, 10.5e9, 60)):
    span = (N - 1) * d_mm * 1e-3 * np.sin(np.radians(thmax)) / c0
    for lsb_ps in (2, 4, 8):
        bits = int(np.ceil(np.log2(span / (lsb_ps * 1e-12) + 1)))
        ph_err = 360 * fmax * lsb_ps * 1e-12 / np.sqrt(12)
        print(f"  N={N:2d}, d={d_mm} mm, ±{thmax}°: span {span*1e12:6.0f} ps; LSB {lsb_ps} ps -> {bits} bits, rms phase error at {fmax/1e9:.2f} GHz {ph_err:5.2f}°")
print("  ADAR4002: 7-bit, 508 ps/4 ps (range 0) or 254 ps/2 ps (range 1)")

print("=" * 78)
print("7. Element chain budgets")


def cascade(stages):
    F, G = 1.0, 1.0
    for i, (g, nf) in enumerate(stages):
        f = 10 ** (nf / 10)
        F = f if i == 0 else F + (f - 1) / G
        G *= 10 ** (g / 10)
    return 10 * np.log10(F), 10 * np.log10(G)


chains = {
    "2.4 GHz: LNA(15 dB,1.0) -> 6-bit PS (IL 6) -> 4:1 Wilkinson (IL 0.5 excess) -> SDR (NF 8)": [(15, 1.0), (-6, 6), (-0.5, 0.5), (0, 8)],
    "2.4 GHz: LNA(30 dB,1.0) -> PS (6) -> 4:1 (0.5) -> SDR (8)": [(30, 1.0), (-6, 6), (-0.5, 0.5), (0, 8)],
    "2.4 GHz: PS (6) first -> LNA(30,1.0) -> SDR": [(-6, 6), (30, 1.0), (0, 8)],
    "X-band: ADTR1107 LNA (18 dB, 2.5) -> ADAR1000 Rx ch (10 dB, NF 8) -> mixer (-7, 7)": [(18, 2.5), (10, 8), (-7, 7)],
    "X-band: ADAR1000 alone (10 dB, NF 8)": [(10, 8), (-7, 7)],
}
for k, ch in chains.items():
    nf, g = cascade(ch)
    print(f"  {k}: NF {nf:5.2f} dB, gain {g:5.1f} dB")
print("done")
