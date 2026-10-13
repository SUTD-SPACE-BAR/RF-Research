#!/usr/bin/env python3
"""Verification for kb/00-math-foundations/probability-random-processes-and-psd.md

Checks: Q-function values and Q = erfc/2; BPSK BER at 9.6 dB; Rayleigh fade probabilities
(analytic vs Monte Carlo); Rician fade probability vs K; exponential power; averaging N powers
(gamma/chi-square) -> relative std 1/sqrt(N); Poisson variance = mean and shot-noise PSD 2qI;
Wiener-Khinchin for an AR(1) process (Welch PSD vs analytic); ENBW of RC, Butterworth-n,
Gaussian; incoherent noise addition; Johnson noise 4kTRB; CLT; Gaussian/Rayleigh peak factors.
Run: python3 tools/verify/math_probability_psd.py
"""
import numpy as np
from scipy import special, stats, signal, integrate, constants as C

ok_all = True
rng = np.random.default_rng(42)


def check(name, got, want, tol):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol})")


Q = lambda x: 0.5 * special.erfc(x / np.sqrt(2))
check("Q(1)", Q(1), 0.158655, 1e-6)
check("Q(2)", Q(2), 0.0227501, 1e-7)
check("Q(3)", Q(3), 1.34990e-3, 1e-8)
check("Q(4.7534) = 1e-6", Q(4.7534), 1.0e-6, 3e-10)
check("Q = norm.sf", Q(2.5), stats.norm.sf(2.5), 1e-15)
check("BPSK BER at Eb/N0 = 9.59 dB ~ 1e-5", Q(np.sqrt(2 * 10 ** (9.59 / 10))), 1e-5, 1e-7)

# --- Rayleigh fading -----------------------------------------------------------------
N = 2_000_000
h = (rng.standard_normal(N) + 1j * rng.standard_normal(N)) / np.sqrt(2)  # E|h|^2 = 1
p = abs(h) ** 2
for dB in [-10, -20, -30]:
    th = 10 ** (dB / 10)
    check(f"Rayleigh P(power < mean {dB} dB) = 1-exp(-x)", np.mean(p < th), 1 - np.exp(-th), 3e-4 if dB > -30 else 1e-4)
check("Rayleigh mean envelope / rms envelope = sqrt(pi)/2", np.mean(abs(h)) / np.sqrt(np.mean(p)), np.sqrt(np.pi) / 2, 1e-3)
check("exponential power: std/mean = 1", np.std(p) / np.mean(p), 1.0, 3e-3)

# --- Rician -----------------------------------------------------------------------------
for KdB in [0, 10]:
    K = 10 ** (KdB / 10)
    # total power 1: LOS power K/(K+1), scatter power 1/(K+1)
    s = np.sqrt(K / (K + 1))
    sig = np.sqrt(1 / (2 * (K + 1)))
    hr = s + sig * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
    th = 10 ** (-10 / 10)
    # analytic via scipy rice: envelope r/sig ~ rice(b = s/sig)
    P_an = stats.rice.cdf(np.sqrt(th) / sig, s / sig)
    check(f"Rician K={KdB} dB: P(power < mean -10 dB) MC vs analytic", np.mean(abs(hr) ** 2 < th), P_an, 5e-4)
    print(f"      (Rician K={KdB} dB: P(fade > 10 dB) = {P_an:.4g})")

# --- averaging N power samples ---------------------------------------------------------------
for Nav in [10, 100]:
    avg = rng.exponential(1.0, (200_000, Nav)).mean(axis=1)
    check(f"avg of {Nav} exp powers: std/mean = 1/sqrt(N)", np.std(avg), 1 / np.sqrt(Nav), 3e-3)
print(f"      (1-sigma of 100-average in dB: +{10*np.log10(1+0.1):.2f}/{10*np.log10(1-0.1):.2f} dB)")

# --- Poisson and shot noise ---------------------------------------------------------------------
lam = 7.3
n = rng.poisson(lam, 1_000_000)
check("Poisson variance = mean", np.var(n) / np.mean(n), 1.0, 5e-3)
I = 1e-3            # 1 mA
q = C.e
dt = 1e-10          # 10 GHz sampling of the pulse train
Ns = 2 ** 22
counts = rng.poisson(I / q * dt, Ns)
i_t = q * counts / dt
f, Pxx = signal.welch(i_t - i_t.mean(), fs=1 / dt, nperseg=2 ** 14, return_onesided=True)
band = (f > 1e8) & (f < 2e9)
check("shot noise one-sided PSD = 2 q I [A^2/Hz]", np.mean(Pxx[band]) / (2 * q * I), 1.0, 0.03)
check("shot noise of 1 mA [pA/rtHz]", np.sqrt(2 * q * I) * 1e12, 17.9, 0.05)

# --- Wiener-Khinchin, AR(1) ----------------------------------------------------------------------
a = 0.9
w_ = rng.standard_normal(2 ** 22)
x = signal.lfilter([1], [1, -a], w_)
f, Pw = signal.welch(x, fs=1.0, nperseg=4096, return_onesided=False, scaling='density')
S_an = 1.0 / abs(1 - a * np.exp(-2j * np.pi * f)) ** 2       # two-sided PSD (unit-variance white input)
sel = abs(f) < 0.45
check("AR(1): Welch PSD / analytic (median ratio)", np.median(Pw[sel] / S_an[sel]), 1.0, 0.03)
# autocorrelation R[m] = a^|m| / (1 - a^2)
m = 5
R5 = np.mean(x[m:] * x[:-m])
check("AR(1): R[5] = a^5/(1-a^2)", R5, a ** 5 / (1 - a ** 2), 0.05)
# FT of R -> S: sum_m a^|m|/(1-a^2) e^{-j w m} at w=0 = 1/(1-a)^2
mm = np.arange(-2000, 2001)
check("W-K at f=0: sum R[m] = S(0)", np.sum(a ** abs(mm) / (1 - a ** 2)), 1 / (1 - a) ** 2, 1e-6)

# --- ENBW ----------------------------------------------------------------------------------------------
ff = np.logspace(-4, 4, 400001)
H2rc = 1 / (1 + ff ** 2)
check("ENBW RC / f3dB = pi/2", integrate.simpson(H2rc, x=ff), np.pi / 2, 1e-3)
for nb in [2, 3, 4]:
    H2 = 1 / (1 + ff ** (2 * nb))
    check(f"ENBW Butterworth n={nb} / f3dB = (pi/2n)/sin(pi/2n)", integrate.simpson(H2, x=ff), (np.pi / (2 * nb)) / np.sin(np.pi / (2 * nb)), 1e-3)
# Gaussian filter, -3 dB full width B3 = 1: |H|^2 = exp(-4 ln2 f^2)
fg = np.linspace(-10, 10, 200001)
check("ENBW Gaussian / B3dB = sqrt(pi/(4 ln2))", integrate.simpson(np.exp(-4 * np.log(2) * fg ** 2), x=fg), np.sqrt(np.pi / (4 * np.log(2))), 1e-6)

# --- noise addition and Johnson noise ------------------------------------------------------------------
v1 = rng.standard_normal(1_000_000) * 1.0
v2 = rng.standard_normal(1_000_000) * 1.0
check("independent 1 uV + 1 uV rms noise -> sqrt(2) uV", np.std(v1 + v2), np.sqrt(2), 3e-3)
check("fully correlated 1 uV + 1 uV -> 2 uV", np.std(v1 + v1), 2.0, 3e-3)
vn = np.sqrt(4 * C.k * 290 * 50 * 1e6)
check("Johnson noise open-circuit 50 ohm, 1 MHz, 290 K [uV rms]", vn * 1e6, 0.8950, 1e-3)
check("available noise power = vn^2/(4R) = kTB [dBm]", 10 * np.log10(vn ** 2 / (4 * 50) / 1e-3), -113.98, 0.01)

# --- CLT ------------------------------------------------------------------------------------------------------
u = rng.uniform(-0.5, 0.5, (400_000, 12)).sum(axis=1)       # variance 12*(1/12)=1
check("CLT: sum of 12 uniforms, P(|x|>2) vs Gaussian 0.0455", np.mean(abs(u) > 2), 2 * Q(2), 1.5e-3)

# --- peak factors ------------------------------------------------------------------------------------------
k4 = stats.norm.isf(0.5e-4)                 # P(|x| > k sigma) = 1e-4, real Gaussian
check("real Gaussian: |x| exceeds k sigma w.p. 1e-4, k", k4, 3.891, 1e-3)
check("  -> instantaneous peak/rms [dB]", 20 * np.log10(k4), 11.80, 0.01)
check("complex Gaussian envelope power exceeds x*mean w.p. 1e-4 -> x [dB]", 10 * np.log10(np.log(1e4)), 9.64, 0.01)

# --- fade margins used on the page ------------------------------------------------------------------------
check("Rayleigh fade margin for 1% outage [dB]", -10 * np.log10(-np.log(1 - 1e-2)), 19.98, 0.01)
K = 10.0
s_, sg_ = np.sqrt(K / (K + 1)), np.sqrt(1 / (2 * (K + 1)))
check("Rician K=10 dB fade margin for 1% outage [dB]", -20 * np.log10(stats.rice.ppf(1e-2, s_ / sg_) * sg_), 6.2, 0.05)
check("Rayleigh-noise threshold for Pfa=1e-6 [dB over mean noise power]", 10 * np.log10(np.log(1e6)), 11.40, 0.01)

check("Marcum/ncx2: SNR for Pd=0.9 at Pfa=1e-6 (non-fluctuating) ~13.2 dB -> Pd", stats.ncx2.sf(2 * np.log(1e6), 2, 2 * 10 ** 1.32), 0.902, 0.005)
check("std of 10log10(exponential) [dB]", 10 / np.log(10) * np.pi / np.sqrt(6), 5.57, 0.01)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
