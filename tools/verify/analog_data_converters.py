#!/usr/bin/env python3
"""Verification script for kb/05-analog-electronics/data-converters-adc-dac.md

 1. Quantisation SNR = 6.02 N + 1.76 dB: derivation check by simulating a quantised full-scale sine.
 2. ENOB = (SINAD - 1.76)/6.02; ADC3664 numbers (SNR 77.5 dBFS @5 MHz, 75.5 @70 MHz, NSD -156.9 dBFS/Hz).
 3. Jitter-limited SNR = -20 log10(2 pi f sigma_t): Monte Carlo sampling with jitter; ADC3664 consistency (implied jitter).
 4. Oversampling processing gain 10 log(OSR); first-order sigma-delta noise shaping vs 6.02N+1.76-5.17+30 log OSR.
 5. DAC zero-order hold: sinc droop and image attenuation.
 6. Aliasing: where out-of-band tones land (433 MHz, 915 MHz sampled at 61.44 / 125 MSPS).
 7. kT/C sampling capacitor vs resolution; settling time constants to N bits; charge-bucket kickback.
 8. ADC noise figure from full scale, SNR, fs; LoRa-channel processing gain.
 9. Reference noise limit.
Run: python3 tools/verify/analog_data_converters.py
"""
import numpy as np

rng = np.random.default_rng(7)
k = 1.380649e-23; T = 300.0

print("=== 1. Quantisation SNR ===")
Nfft = 2**16
for N in (4, 8, 12, 16):
    cycles = 1021  # prime -> no repeating code pattern
    n = np.arange(Nfft)
    x = np.sin(2 * np.pi * cycles * n / Nfft + 0.3)  # full-scale -1..1
    q = 2 / 2**N
    xq = np.clip(np.round(x / q - 0.5) + 0.5, -2**(N - 1) + 0.5, 2**(N - 1) - 0.5) * q  # mid-rise quantiser
    e = xq - x
    snr = 10 * np.log10(np.mean(x**2) / np.mean(e**2))
    print(f"N={N:2d}: simulated SNR = {snr:6.2f} dB, 6.02N+1.76 = {6.02*N+1.76:6.2f} dB; error rms/q = {np.sqrt(np.mean(e**2))/q:.4f} (1/sqrt12 = {1/np.sqrt(12):.4f})")

print("\n=== 2. ENOB and NSD (ADC3664) ===")
fs = 125e6
for label, snr in (("5 MHz, -1 dBFS", 77.5), ("70 MHz", 75.5), ("5 MHz, -20 dBFS", 78.9)):
    nsd = -snr - 10 * np.log10(fs / 2)
    print(f"ADC3664 {label}: SNR {snr} dBFS -> ENOB(SNR only) {(snr-1.76)/6.02:.2f} bits, NSD = -SNR - 10log(fs/2) = {nsd:.1f} dBFS/Hz")
print("(datasheet NSD -156.9 dBFS/Hz at AIN = -20 dBFS; ideal 14-bit: SNR", round(6.02 * 14 + 1.76, 2), "dB)")

print("\n=== 3. Jitter-limited SNR ===")
for f_in, sj in ((10e6, 1e-12), (70e6, 250e-15), (100e6, 1e-12), (433e6, 100e-15), (1e9, 50e-15)):
    snr_th = -20 * np.log10(2 * np.pi * f_in * sj)
    # Monte Carlo: sample sin(2 pi f t) at jittered instants
    M = 200000
    t = rng.uniform(0, 1 / f_in, M)
    dt = rng.normal(0, sj, M)
    err = np.sin(2 * np.pi * f_in * (t + dt)) - np.sin(2 * np.pi * f_in * t)
    snr_mc = 10 * np.log10(0.5 / np.mean(err**2))
    print(f"f_in={f_in/1e6:7.1f} MHz, sigma_t={sj*1e15:6.0f} fs: theory {snr_th:6.2f} dB, Monte Carlo {snr_mc:6.2f} dB")
# ADC3664 implied jitter from SNR drop 77.5 -> 75.5 dB between 5 and 70 MHz
nj = 10**(-75.5 / 10) - 10**(-77.5 / 10)
snr_j = -10 * np.log10(nj)
tj = 10**(-snr_j / 20) / (2 * np.pi * 70e6)
print(f"ADC3664: SNR drop implies jitter-only SNR {snr_j:.1f} dB at 70 MHz -> total jitter ~ {tj*1e15:.0f} fs (datasheet aperture jitter 250 fs)")

print("\n=== 4. Oversampling and sigma-delta ===")
for OSR in (1, 4, 16, 64, 256):
    print(f"OSR={OSR:4d}: Nyquist-ADC processing gain 10 log OSR = {10*np.log10(OSR):5.1f} dB (= {10*np.log10(OSR)/6.02:.2f} bits)")
# simulate first-order 1-bit sigma-delta
def sd1(x):
    y = np.empty_like(x); integ = 0.0; fb = 0.0
    for i, xi in enumerate(x):
        integ += xi - fb
        y[i] = 1.0 if integ >= 0 else -1.0
        fb = y[i]
    return y
def sd2(x):
    y = np.empty_like(x); i1 = 0.0; i2 = 0.0; fb = 0.0
    for i, xi in enumerate(x):
        i1 += xi - fb
        i2 += i1 - fb
        y[i] = 1.0 if i2 >= 0 else -1.0
        fb = y[i]
    return y
Nsd = 2**18
nn = np.arange(Nsd)
for OSR in (32, 64, 128):
    fb_bins = Nsd // (2 * OSR)
    k0 = max(3, fb_bins // 7) | 1
    A = 0.5  # -6 dBFS
    x = A * np.sin(2 * np.pi * k0 * nn / Nsd) + 1e-3 * rng.standard_normal(Nsd) * 0  # no dither
    w = np.hanning(Nsd)
    for name, mod, L in (("1st-order", sd1, 1), ("2nd-order", sd2, 2)):
        y = mod(x)
        Y = np.abs(np.fft.rfft(y * w))**2
        sig = Y[k0 - 3:k0 + 4].sum()
        noise = Y[1:fb_bins].sum() - sig
        sqnr = 10 * np.log10(sig / noise)
        pred = 6.02 * 1 + 1.76 - 10 * np.log10(np.pi**(2 * L) / (2 * L + 1)) + (2 * L + 1) * 10 * np.log10(OSR) + 20 * np.log10(A)
        print(f"  {name} 1-bit SD, OSR={OSR:4d}, -6 dBFS: simulated SQNR {sqnr:6.1f} dB, linear-model prediction {pred:6.1f} dB")

print("\n=== 5. DAC zero-order hold ===")
for fr in (0.1, 0.25, 0.4, 0.5):
    droop = 20 * np.log10(np.sinc(fr))
    img = 20 * np.log10(abs(np.sinc(1 - fr)))
    print(f"f/fs={fr:.2f}: sinc droop {droop:6.2f} dB; first image at (1-{fr})fs has |sinc| = {img:6.2f} dB -> image/signal = {img-droop:6.2f} dB")

print("\n=== 6. Aliases ===")
def alias(f, fs):
    fa = f % fs
    return fa if fa <= fs / 2 else fs - fa
for fs_ in (61.44e6, 125e6):
    for f in (433.92e6, 915e6, 2.45e9):
        print(f"f={f/1e6:8.2f} MHz sampled at {fs_/1e6:6.2f} MSPS -> appears at {alias(f, fs_)/1e6:7.3f} MHz (zone {int(f // (fs_/2)) + 1})")

print("\n=== 7. kT/C, settling, kickback ===")
for N, Vfs in ((12, 3.3), (16, 5.0), (18, 5.0), (24, 5.0)):
    qv = Vfs / 2**N
    Cmin = 12 * k * T / qv**2  # kT/C = q^2/12
    tau_n = (N + 1) * np.log(2)
    print(f"N={N}, FS={Vfs} V: LSB={qv*1e6:8.3f} uV; C for kT/C = q^2/12: {Cmin*1e12:10.2f} pF; settle to 1/2 LSB = {tau_n:.1f} tau")
Cs, Cext = 30e-12, 1e-9
print(f"charge-bucket: Cs={Cs*1e12:.0f} pF, Cext={Cext*1e9:.0f} nF -> initial kickback step = Cs/(Cs+Cext) = {Cs/(Cs+Cext)*100:.2f} % of the voltage difference")

print("\n=== 8. ADC noise figure and processing gain ===")
Vpp, Rt = 3.2, 200.0
Pfs = (Vpp / (2 * np.sqrt(2)))**2 / Rt
Pfs_dBm = 10 * np.log10(Pfs / 1e-3)
for snr in (77.5, 75.5):
    NF = Pfs_dBm - snr - 10 * np.log10(fs / 2) + 174
    print(f"ADC3664-like: FS {Vpp} Vpp diff into {Rt:.0f} ohm = {Pfs_dBm:.2f} dBm, SNR {snr} dBFS -> NF = {NF:.1f} dB")
for bw in (125e3, 500e3):
    print(f"LoRa channel {bw/1e3:.0f} kHz within fs/2 = 62.5 MHz: processing gain {10*np.log10(fs/2/bw):.1f} dB")

print("\n=== 9. Reference noise ===")
for vn_rms, Vref in ((10e-6, 2.5), (3e-6, 2.5), (30e-6, 3.3)):
    print(f"reference noise {vn_rms*1e6:.0f} uV rms on {Vref} V (in ADC bandwidth): full-scale SNR limit = {20*np.log10(Vref/(2*np.sqrt(2))/vn_rms):.1f} dB (FS sine rms = Vref/(2 sqrt2) for a 0..Vref ADC)")

print("\n=== 10. Worked-example numbers ===")
F_adc = 10**(26.6 / 10)
for G_dB, NF1 in ((20, 1.0), (30, 1.0), (40, 1.0)):
    F = 10**(NF1 / 10) + (F_adc - 1) / 10**(G_dB / 10)
    print(f"LNA+gain {G_dB} dB (NF1 {NF1} dB) ahead of a 26.6 dB-NF ADC: system NF = {10*np.log10(F):.2f} dB")
nsd = -156.9
for bw in (125e3,):
    print(f"NSD {nsd} dBFS/Hz integrated over {bw/1e3:.0f} kHz = {nsd + 10*np.log10(bw):.1f} dBFS")
for snr_need in (70, 75, 80):
    tj = 10**(-snr_need / 20) / (2 * np.pi * 70e6)
    print(f"jitter-limited SNR >= {snr_need} dB at 70 MHz needs sigma_t <= {tj*1e15:.0f} fs")
t_acq = 1e-6; Cext = 1e-9
tau = t_acq / (17 * np.log(2))
print(f"16-bit SAR, 1 us acquisition: tau <= {tau*1e9:.1f} ns -> R <= {tau/Cext:.0f} ohm with a 1 nF charge bucket")

print("\n=== 11. Choosing fs to centre 433.92 MHz in a Nyquist zone ===")
f = 433.92e6
for m in (7, 8):
    fs_c = 2 * f / (m - 0.5)
    print(f"zone {m} centre: fs = 2f/(m-1/2) = {fs_c/1e6:.2f} MSPS -> alias at {alias(f, fs_c)/1e6:.2f} MHz (fs/4 = {fs_c/4e6:.2f}); zone edges {(m-1)*fs_c/2e6:.1f}-{m*fs_c/2e6:.1f} MHz")
print(f"at 125 MSPS zone 7 spans 375.0-437.5 MHz: 433.92 MHz is {437.5-433.92:.2f} MHz from the edge")
