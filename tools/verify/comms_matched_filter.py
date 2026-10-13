#!/usr/bin/env python3
"""Verification for kb/10-comms-modulation/matched-filter-detection.md

Run:  python3 tools/verify/comms_matched_filter.py     (~5 s)

Checks:
  1. Matched filter output peak SNR = 2E/N0 for three different pulse shapes (discrete-time
     simulation with white noise of two-sided PSD N0/2), and that correlator == matched filter.
  2. Mismatch loss of a single-pole RC low-pass used on a rectangular pulse: optimum B*T and loss
     (classic result: ~0.9 dB at B_3dB*T ~ 0.2).
  3. Pulse compression: LFM chirp with time-bandwidth product TB -> compressed main-lobe width
     ~1/B and peak SNR still 2E/N0 (energy, not bandwidth, sets detectability).
  4. Detection of a known signal in AWGN: coherent Pd = Q(Qinv(Pfa) - sqrt(2E/N0)) and
     non-coherent (unknown phase, envelope) Pd = Marcum Q1(sqrt(2E/N0), sqrt(-2 ln Pfa)),
     both vs Monte-Carlo.
"""
import numpy as np
from scipy import special, stats, optimize, signal

rng = np.random.default_rng(3)
ok_all = True


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel else 1.0)
    ok = err <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.5g}, expected {want:.5g} (tol {tol}{' rel' if rel else ''})")


fs = 1000.0                   # samples per unit time
dt = 1 / fs
N0 = 0.02                     # one-sided noise PSD (two-sided N0/2)
sigma = np.sqrt(N0 / 2 / dt)  # per-sample std of white noise with two-sided PSD N0/2

# ---------------------------------------------------------------------------- 1
t = np.arange(0, 1, dt)
pulses = {
    "rectangular": np.ones_like(t),
    "half-sine": np.sin(np.pi * t),
    "RRC-like windowed sinc": np.sinc(8 * (t - 0.5)) * np.hanning(len(t)),
}
ntrial = 4000
for nm, p in pulses.items():
    E = np.sum(p ** 2) * dt
    h = p[::-1]                                         # matched filter impulse response
    peak = np.sum(p * p) * dt                           # output at t = T (noise-free) = E
    # noise-only outputs at the sampling instant: correlator form sum(n * p) dt
    noise = sigma * rng.standard_normal((ntrial, len(p)))
    nout = noise @ p * dt
    snr = peak ** 2 / np.var(nout)
    check(f"MF output SNR = 2E/N0 ({nm})", snr, 2 * E / N0, 0.06, rel=True)
    # convolution form equals correlator form at t=T
    x = p + noise[0]
    conv = np.convolve(x, h)[len(p) - 1] * dt
    corr = np.sum(x * p) * dt
    check(f"convolution with h(t)=p(T-t) at t=T == correlator ({nm})", conv, corr, 1e-9)

# ---------------------------------------------------------------------------- 2
# rectangular pulse of duration T=1 through RC low-pass with 3-dB bandwidth B; sample at the
# best instant; SNR relative to matched filter (2E/N0).


def rc_loss(BT):
    tau = 1 / (2 * np.pi * BT)            # time constant (T = 1)
    # deterministic output at t = T is maximal: y(T) = 1 - exp(-T/tau)
    y = 1 - np.exp(-1 / tau)
    # output noise variance for white noise N0/2 into RC with unity DC gain: (N0/2) * 1/(2 tau)
    var = N0 / 2 / (2 * tau)
    E = 1.0
    return (y ** 2 / var) / (2 * E / N0)


res = optimize.minimize_scalar(lambda b: -rc_loss(b), bounds=(0.01, 2), method="bounded")
bt_opt = res.x
loss_db = -10 * np.log10(rc_loss(bt_opt))
print(f"  RC filter on rect pulse: optimum B3dB*T = {bt_opt:.3f}, mismatch loss = {loss_db:.2f} dB")
check("RC mismatch optimum B*T ~ 0.2", bt_opt, 0.2, 0.02)
check("RC mismatch loss ~ 0.9 dB", loss_db, 0.9, 0.05)

# ---------------------------------------------------------------------------- 3
T = 1.0
B = 50.0                                   # chirp sweep bandwidth (TB = 50)
fs2 = 4000.0
t2 = np.arange(0, T, 1 / fs2)
chirp = np.exp(1j * np.pi * (B / T) * (t2 - T / 2) ** 2)   # complex baseband LFM, |.|=1
E = np.sum(np.abs(chirp) ** 2) / fs2
comp = np.correlate(chirp, chirp, mode="full") / fs2
mag = np.abs(comp)
peak = mag.max()
check("compressed peak = E", peak, E, 1e-9, rel=True)
# -4 dB (null-to-null ~ 2/B) width; measure -3.92 dB width ~ 1/B for sinc-like main lobe
above = np.where(mag >= peak / np.sqrt(2) ** 1)[0]      # -3 dB points
w3 = (above[-1] - above[0]) / fs2
check("compressed -3 dB width ~ 0.886/B", w3, 0.886 / B, 0.12, rel=True)
print(f"  pulse compression ratio T/width = {T / w3:.1f} (TB = {T * B:.0f})")
# noise at compressor output
ntr = 800
acc = 0.0
for _ in range(8):
    nz = np.sqrt(N0 / 2 * fs2) * (rng.standard_normal((ntr, len(t2))) + 1j * rng.standard_normal((ntr, len(t2))))
    # complex baseband: per-rail two-sided PSD N0/2 -> per-sample variance N0/2*fs2 on each rail
    acc += np.sum(np.abs(nz @ np.conj(chirp) / fs2) ** 2)
nout_pow = acc / (8 * ntr)
snr_c = peak ** 2 / nout_pow
check("complex MF SNR = E/N0 per complex rail convention -> equals 2E/N0 in real-passband terms", snr_c, E / N0, 0.06, rel=True)

# ---------------------------------------------------------------------------- 4


def pd_coherent(pfa, snr):              # snr = 2E/N0 (linear)
    return stats.norm.sf(stats.norm.isf(pfa) - np.sqrt(snr))


def marcum_q1(a, b):
    # Q1(a,b) = P(|a + n| > b) with n complex N(0,1) per rail variance 1 -> noncentral chi2 df=2
    return stats.ncx2.sf(b ** 2, 2, a ** 2)


def pd_noncoherent(pfa, snr):
    return marcum_q1(np.sqrt(snr), np.sqrt(-2 * np.log(pfa)))


pfa = 1e-3
for snr_db in (10.0, 13.0):
    snr = 10 ** (snr_db / 10)
    n = 400_000
    # coherent: statistic z = sqrt(snr) + n, n ~ N(0,1); threshold Qinv(pfa)
    z1 = np.sqrt(snr) + rng.standard_normal(n)
    thr = stats.norm.isf(pfa)
    check(f"coherent Pd @2E/N0={snr_db} dB, Pfa=1e-3", np.mean(z1 > thr), pd_coherent(pfa, snr), 0.02, rel=True)
    # noncoherent: envelope of complex Gaussian with per-rail variance 1
    ph = rng.random(n) * 2 * np.pi
    zc = np.sqrt(snr) * np.exp(1j * ph) + rng.standard_normal(n) + 1j * rng.standard_normal(n)
    thr_nc = np.sqrt(-2 * np.log(pfa))
    check(f"non-coherent Pd @2E/N0={snr_db} dB, Pfa=1e-3", np.mean(np.abs(zc) > thr_nc), pd_noncoherent(pfa, snr), 0.02, rel=True)
    z0 = rng.standard_normal(n) + 1j * rng.standard_normal(n)
    check("non-coherent Pfa check", np.mean(np.abs(z0) > thr_nc), pfa, 0.12, rel=True)

# required 2E/N0 for Pd = 0.9 at Pfa 1e-6 (typical preamble detector), coherent vs non-coherent
for nm, f in (("coherent", pd_coherent), ("non-coherent", pd_noncoherent)):
    x = optimize.brentq(lambda s: f(1e-6, 10 ** (s / 10)) - 0.9, 0, 25)
    print(f"  {nm}: 2E/N0 for Pd=0.9, Pfa=1e-6 = {x:.2f} dB  (E/N0 = {x - 3.01:.2f} dB)")

# ---------------------------------------------------------------------------- 5
# Frequency-offset and timing-offset loss of a coherent correlator (rectangular BPSK chips)
Tsw = 32 / 10e3                       # 32-bit sync word at 10 kbit/s = 3.2 ms
fsx = 200e3
tt = np.arange(0, Tsw, 1 / fsx)
bits = rng.integers(0, 2, 32)
ref = np.repeat(1 - 2.0 * bits, len(tt) // 32)
for df in (50.0, 200.0, 1000.0):
    rx = ref * np.exp(2j * np.pi * df * tt[:len(ref)])
    gain = np.abs(np.sum(rx * ref)) / np.sum(ref * ref)
    loss_db = -20 * np.log10(gain)
    theory = -20 * np.log10(abs(np.sinc(df * Tsw)))
    print(f"  coherent 32-bit sync correlator, CFO {df:6.0f} Hz: loss {loss_db:5.1f} dB (|sinc(df*T)|^2 -> {theory:5.1f} dB)")
    check(f"CFO loss formula at {df} Hz", loss_db, theory, 0.3)
# timing offset for rectangular pulse: amplitude falls linearly 1 - |tau|/T  -> loss 20log(1-|tau|/T)
for frac in (0.1, 0.25, 0.5):
    theory = -20 * np.log10(1 - frac)
    print(f"  rect-pulse MF sampled {frac:.2f} T late: loss {theory:.2f} dB")
check("quarter-symbol timing error loss (rect) [dB]", -20 * np.log10(0.75), 2.50, 0.01)

print("\nOVERALL:", "PASS" if ok_all else "FAIL")
