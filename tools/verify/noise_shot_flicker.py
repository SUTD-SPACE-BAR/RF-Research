#!/usr/bin/env python3
"""
noise_shot_flicker.py — verification for kb/07-noise-linearity/shot-and-flicker-noise.md

1. Shot noise: simulate a Poisson stream of charge impulses (rate I/q) and compare the measured
   one-sided current PSD with Schottky's 2 q I.
2. Shot vs thermal: 2qI = 4kT/R when I R = 2kT/q (~52 mV at 300 K).
3. BJT input-referred noise voltage from collector shot noise (e_n = sqrt(2 q Ic)/gm = VT sqrt(2q/Ic))
   plus base-resistance thermal noise.
4. 1/f noise: equal power per decade; integrated flicker noise K ln(f2/f1).
5. Zero-IF penalty: baseband noise of a receiver with flicker corner fc integrated over a LoRa
   BW125 baseband (+-62.5 kHz), relative to white noise only.
6. Synthesis of 1/f noise by spectral shaping and its Allan-deviation "flicker floor".
"""
import numpy as np
q = 1.602176634e-19; k = 1.380649e-23
rng = np.random.default_rng(4)

print("=== 1. Poisson shot noise PSD vs 2qI ===")
fs = 2e6; N = 1 << 20; T = N/fs
for I in (1e-12, 1e-11):          # tiny currents so the event count is tractable (1e-11 A = 6.2e7 e/s)
    lam = I/q
    counts = rng.poisson(lam/fs, N)           # electrons per sample
    i_t = counts*q*fs                          # current samples (A)
    x = i_t - i_t.mean()
    X = np.fft.rfft(x)
    psd = 2*np.abs(X)**2/(fs*N)                # one-sided A^2/Hz
    meas = np.mean(psd[10:-10])
    print(f"  I={I:.0e} A: measured {meas:.3e} A^2/Hz, 2qI = {2*q*I:.3e} A^2/Hz (ratio {meas/(2*q*I):.3f})")
for I in (1e-6, 1e-3, 10e-3):
    print(f"  I={I:.0e} A -> i_n = sqrt(2qI) = {np.sqrt(2*q*I)*1e12:.2f} pA/rtHz")

print("\n=== 2. When does shot noise beat the resistor's thermal noise? ===")
for T in (290.0, 300.0):
    print(f"  T={T:.0f} K: 2qI = 4kT/R  <=>  I R = 2kT/q = {2*k*T/q*1e3:.1f} mV")

print("\n=== 3. BJT input-referred noise voltage ===")
VT = k*300/q
for Ic in (1e-3, 5e-3, 20e-3):
    gm = Ic/VT
    en_shot = np.sqrt(2*q*Ic)/gm
    for rb in (5.0, 20.0):
        en_rb = np.sqrt(4*k*300*rb)
        print(f"  Ic={Ic*1e3:4.0f} mA (gm={gm*1e3:5.0f} mS): e_n(shot)={en_shot*1e9:.3f} nV/rtHz "
              f"(= thermal noise of {1/(2*gm):.2f} ohm), + rb={rb:.0f} ohm -> total {np.hypot(en_shot, en_rb)*1e9:.3f} nV/rtHz")

print("\n=== 4. 1/f noise per decade ===")
K = 1e-12   # V^2 (S = K/f)
for f1, f2 in ((1, 10), (10, 100), (1e3, 1e4), (0.01, 1e6)):
    print(f"  integral K/f from {f1:g} to {f2:g} Hz = K ln(f2/f1) = {K*np.log(f2/f1):.3e} V^2 ({np.log10(f2/f1):.0f} decades)")

print("\n=== 5. Zero-IF penalty for a narrow channel ===")
def baseband_noise(fc, f_lo, f_hi):
    """Integral of S0 (1 + fc/f) over [f_lo, f_hi], in units of S0 (white density)."""
    return (f_hi - f_lo) + fc*np.log(f_hi/f_lo)
for fc in (1e3, 10e3, 100e3, 1e6):
    for (lo, hi) in ((100.0, 62.5e3), (1e3, 62.5e3)):
        ratio = baseband_noise(fc, lo, hi)/(hi - lo)
        print(f"  flicker corner {fc/1e3:7.1f} kHz, baseband {lo:6.0f} Hz-62.5 kHz: baseband noise x{ratio:7.2f} "
              f"({10*np.log10(ratio):5.1f} dB above white)")
# referred to the antenna through RF gain: if baseband stage has NF_bb (white) and RF gain G precedes it
for G_db in (20.0, 35.0):
    F_rf = 10**(3/10); F_bb_white = 10**(15/10)
    for fc in (10e3, 100e3):
        ratio = baseband_noise(fc, 100.0, 62.5e3)/(62.5e3 - 100.0)
        F_bb = 1 + (F_bb_white - 1)*ratio
        Ftot = F_rf + (F_bb - 1)/10**(G_db/10)
        Fw = F_rf + (F_bb_white - 1)/10**(G_db/10)
        print(f"  RF NF 3 dB, G_RF {G_db:.0f} dB, baseband NF 15 dB white, fc {fc/1e3:.0f} kHz: "
              f"NF {10*np.log10(Ftot):.2f} dB (white-only {10*np.log10(Fw):.2f} dB)")

print("\n=== 6. Synthesised 1/f noise: Allan deviation flattens ===")
N = 1 << 20
w = rng.standard_normal(N)
W = np.fft.rfft(w)
f = np.arange(len(W)); f[0] = 1
x = np.fft.irfft(W/np.sqrt(f), n=N)
x /= np.std(x)
def adev(y, m):
    n = len(y)//m
    a = y[:n*m].reshape(n, m).mean(axis=1)
    return np.sqrt(0.5*np.mean(np.diff(a)**2))
for m in (1, 10, 100, 1000, 10000):
    print(f"  tau = {m:6d} samples: ADEV(white) = {adev(w, m):.4f}, ADEV(1/f) = {adev(x, m):.4f}")
print("  white noise ADEV falls as tau^-1/2; flicker ADEV is ~flat (the 'bias instability' floor of IMUs/clocks)")
