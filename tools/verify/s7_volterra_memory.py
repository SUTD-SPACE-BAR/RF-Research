#!/usr/bin/env python3
"""S7 (W5-S7) Volterra / memory-effect checks for kb/07-noise-linearity/nonlinearity-p1db-ip3-intermod.md
"Level 3 — Volterra series, memory effects and AM-PM".

 §1 envelope-frequency memory: y = a1 x + a3 x^3 + c * x * LPF{x^2}
    closed-form complex IM3 phasors (lower/upper) vs FFT of a time-domain simulation;
    IM3 asymmetry and tone-spacing dependence
 §2 AM-PM from a frequency-dependent cubic kernel: y = a1 x + a3 x^2 (g * x)
    describing function H1 + A^2 a3 (G/2 + G*/4) vs simulation
 §3 memory polynomial (diagonal Volterra) vs generalized memory polynomial (adds cross terms)
    least-squares fit to a baseband model with an envelope-filter memory term
Run: python3 tools/verify/s7_volterra_memory.py  (≈ 3 s)
"""
import numpy as np
from scipy import signal

rng = np.random.default_rng(703)
ok = True


def check(name, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")


# ---------------------------------------------------------------- §1
print("§1 Envelope memory: x^2 through P(w) = one-pole LPF (bias network) + d e^{-jw} (2nd-harmonic termination)")
Nfft = 2 ** 16
a1, a3, c = 1.0, -0.10, 0.12
A = 0.3
pole = 0.995                       # one-pole LPF y[n] = (1-p) x[n] + p y[n-1]
d2 = 0.5                            # strength of the delayed (2f-reactive) path
H = lambda w: (1 - pole) / (1 - pole * np.exp(-1j * w)) + d2 * np.exp(-1j * w)
k1 = 13000                          # carrier bin (~0.2 fs)
res = []
for dk in (2, 8, 32, 128, 512):
    k2 = k1 + dk
    n = np.arange(3 * Nfft)
    x = A * np.cos(2 * np.pi * k1 * n / Nfft) + A * np.cos(2 * np.pi * k2 * n / Nfft)
    env = signal.lfilter([1 - pole], [1, -pole], x ** 2) + d2 * np.concatenate([[0.0], (x ** 2)[:-1]])
    y = a1 * x + a3 * x ** 3 + c * x * env
    Y = np.fft.fft(y[-Nfft:]) * 2 / Nfft            # positive-frequency phasors (cos amplitude)
    L_sim, U_sim = Y[2 * k1 - k2], Y[2 * k2 - k1]
    w = lambda k: 2 * np.pi * k / Nfft
    D = w(dk)
    L_th = 0.75 * a3 * A ** 3 + c * A ** 3 / 2 * np.conj(H(D)) + c * A ** 3 / 4 * H(2 * w(k1))
    U_th = 0.75 * a3 * A ** 3 + c * A ** 3 / 2 * H(D) + c * A ** 3 / 4 * H(2 * w(k2))
    fc_ratio = D / (1 - pole)       # tone spacing / filter corner (rad/sample)
    asym = 20 * np.log10(abs(U_sim) / abs(L_sim))
    res.append((fc_ratio, asym, abs(L_sim), abs(L_th), abs(U_sim), abs(U_th)))
    print(f"  spacing/corner {fc_ratio:7.2f}: IM3 lower {20*np.log10(abs(L_sim)):7.2f} dB (th {20*np.log10(abs(L_th)):7.2f}), "
          f"upper {20*np.log10(abs(U_sim)):7.2f} (th {20*np.log10(abs(U_th)):7.2f}); asymmetry {asym:+.2f} dB")
err = max(max(abs(20 * np.log10(r[2] / r[3])), abs(20 * np.log10(r[4] / r[5]))) for r in res)
check("closed-form IM3 phasors match simulation within 0.05 dB", err < 0.05)
check("IM3 asymmetric near spacing ~ filter corner (> 3 dB)", max(abs(r[1]) for r in res) > 3)
check("IM3 depends on tone spacing (> 10 dB change across sweep)",
      abs(20 * np.log10(res[0][2] / res[-1][2])) > 10)
memless = 0.75 * a3 * A ** 3 + c * A ** 3 * (0.5 * H(0) + 0.25 * H(2 * 2 * np.pi * k1 / Nfft))
print(f"  narrow-spacing limit 3/4 a3 A^3 + c A^3 (P(0)/2 + P(2w)/4) = {20*np.log10(abs(memless)):.2f} dB; "
      f"wide spacing: (3/4)a3 A^3 = {20*np.log10(abs(0.75*a3*A**3)):.2f} dB")

# ---------------------------------------------------------------- §2
print("§2 AM-PM from a frequency-dependent (complex) cubic kernel")
k0 = 4096
n = np.arange(Nfft)
a1, a3 = 1.0, -0.2
gtaps = np.array([0.0, 0.0, 1.0])        # g = 2-sample delay: G(w) = e^{-j2w}
wc = 2 * np.pi * k0 / Nfft
G = np.exp(-1j * 2 * wc)
maxerr = 0
for A in (0.1, 0.4, 0.8, 1.2):
    x = A * np.cos(wc * n)
    gx = np.convolve(np.concatenate([x[-2:], x]), gtaps, "valid")[: len(x)] if False else np.roll(x, 2)
    y = a1 * x + a3 * x ** 2 * gx
    Y1 = np.fft.fft(y)[k0] * 2 / Nfft
    Y1_th = a1 * A + a3 * A ** 3 * (G / 2 + np.conj(G) / 4)
    am_am = 20 * np.log10(abs(Y1) / (a1 * A))
    am_pm = np.degrees(np.angle(Y1))
    maxerr = max(maxerr, abs(Y1 - Y1_th))
    print(f"  A = {A:4.2f}: AM-AM {am_am:+6.2f} dB, AM-PM {am_pm:+7.2f} deg (theory {np.degrees(np.angle(Y1_th)):+7.2f})")
check("describing function a1 + a3 A^2 (G/2 + G*/4) matches", maxerr < 1e-9)
# memoryless (G = 1) => zero AM-PM
x = 0.8 * np.cos(wc * n)
Y1 = np.fft.fft(a1 * x + a3 * x ** 3)[k0]
check("memoryless real polynomial gives zero AM-PM", abs(np.angle(Y1 * np.sign(Y1.real))) < 1e-9)

# ---------------------------------------------------------------- §3
print("§3 Memory polynomial (MP) vs generalized memory polynomial (GMP)")
Ns = 40000
# band-limited complex Gaussian (OFDM-like) drive, PAPR ~ 10 dB
u = (rng.standard_normal(Ns) + 1j * rng.standard_normal(Ns)) / np.sqrt(2)
b = signal.firwin(101, 0.2)
x = np.convolve(u, b, "same")
x = 0.5 * x / np.sqrt(np.mean(np.abs(x) ** 2))
h = np.array([0.0, 0.5, 0.3, 0.2])       # envelope memory (taps 1..3)
env = np.convolve(np.abs(x) ** 2, h)[:Ns]
alpha1, alpha3, beta = 1.0, -0.08 + 0.03j, 0.10 - 0.05j
z = alpha1 * x + alpha3 * np.abs(x) ** 2 * x + beta * x * env


def shift(v, m):
    return np.concatenate([np.zeros(m, v.dtype), v[:len(v) - m]])


def basis_mp(x, K=(1, 3, 5), M=4):
    cols = []
    for m in range(M):
        xm = shift(x, m)
        for k in K:
            cols.append(xm * np.abs(xm) ** (k - 1))
    return np.array(cols).T


def basis_gmp(x, K=(1, 3, 5), M=4, Mc=3):
    cols = list(basis_mp(x, K, M).T)
    for m in range(1, Mc + 1):           # lagging envelope cross terms x[n]|x[n-m]|^(k-1)
        for k in (3, 5):
            cols.append(x * np.abs(shift(x, m)) ** (k - 1))
    return np.array(cols).T


sl = slice(10, Ns)
for name, B in (("MP  (K=1,3,5; M=4; 12 coeffs)", basis_mp(x)), ("GMP (+ 6 cross terms; 18 coeffs)", basis_gmp(x))):
    coef, *_ = np.linalg.lstsq(B[sl], z[sl], rcond=None)
    e = z[sl] - B[sl] @ coef
    nmse = 10 * np.log10(np.sum(np.abs(e) ** 2) / np.sum(np.abs(z[sl]) ** 2))
    print(f"  {name}: NMSE {nmse:7.1f} dB")
    if name.startswith("MP"):
        nm_mp = nmse
    else:
        nm_gmp = nmse
check("MP cannot represent envelope cross-memory (NMSE > -45 dB)", nm_mp > -45)
check("GMP represents it exactly (NMSE < -200 dB)", nm_gmp < -200)
# full baseband Volterra 3rd-order count for comparison
M = 4
n3 = M * M * (M + 1) // 2   # x[n-i] x[n-j] x*[n-l] with i<=j symmetric
print(f"  coefficient count, 3rd order only, memory M = {M}: full Volterra {n3}, MP {M}, GMP (+cross, Mc=3) {M+3}")

print("\nALL PASS" if ok else "\nSOME FAILED")
