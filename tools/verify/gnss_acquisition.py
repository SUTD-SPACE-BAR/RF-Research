#!/usr/bin/env python3
"""
gnss_acquisition.py — verification for kb/21-gnss/gnss-receiver-architecture-acquisition-tracking.md
                       and kb/21-gnss/sdr-gnss-and-diy-receivers.md

 1. Parallel code-phase (FFT) acquisition of a synthetic GPS L1 C/A signal in complex
    baseband (fs = 4.092 MHz), unknown Doppler within +-5 kHz, 500 Hz bins.
 2. Monte-Carlo detection probability vs C/N0 for coherent 1 ms x K non-coherent sums,
    compared with the non-central chi-square theory (Pfa per cell fixed).
 3. Coherent-integration Doppler loss sinc^2(pi*df*T) and why 1/(2T) bin spacing is used.
 4. ADC quantisation loss: 1-bit (theory 2/pi = -1.96 dB) and 2-bit (~ -0.55 dB) by simulation.
 5. Search-space size and serial vs parallel search time.
Run: python3 tools/verify/gnss_acquisition.py   (~20-40 s)
"""
import numpy as np
from scipy import stats

rng = np.random.default_rng(1)
ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


G2_TAPS = {1: (2, 6), 3: (4, 8), 7: (1, 8), 12: (5, 6), 19: (3, 6), 24: (4, 6)}


def ca_code(prn):
    g1 = [1] * 10; g2 = [1] * 10; t1, t2 = G2_TAPS[prn]; out = []
    for _ in range(1023):
        out.append(g1[9] ^ g2[t1 - 1] ^ g2[t2 - 1])
        f1 = g1[2] ^ g1[9]; f2 = g2[1] ^ g2[2] ^ g2[5] ^ g2[7] ^ g2[8] ^ g2[9]
        g1 = [f1] + g1[:9]; g2 = [f2] + g2[:9]
    return 1 - 2 * np.array(out)


fs = 4.092e6
N = int(fs * 1e-3)                  # samples per 1-ms code period (4092)
chip = 1.023e6
code = ca_code(1)
t = np.arange(N) / fs
code_s = code[(np.floor(t * chip).astype(int)) % 1023].astype(float)
CODE_FFT_CONJ = np.conj(np.fft.fft(code_s))
dopp_bins = np.arange(-5000, 5001, 500.0)


def make_signal(cn0_dbhz, n_ms, fd, tau_samp, phase0=0.0):
    """complex baseband: sqrt(C)*code*exp(j(2 pi fd t + phi)) + noise; noise density N0=1 per Hz
    -> per complex sample variance N0*fs."""
    C = 10 ** (cn0_dbhz / 10)
    n = N * n_ms
    tt = np.arange(n) / fs
    cs = code[(np.floor((tt - tau_samp / fs) * chip).astype(int)) % 1023]
    s = np.sqrt(C) * cs * np.exp(1j * (2 * np.pi * fd * tt + phase0))
    noise = (rng.standard_normal(n) + 1j * rng.standard_normal(n)) * np.sqrt(fs / 2)
    return s + noise


def acquire(x, n_ms):
    """returns (K-sum of |corr|^2 normalised by complex noise variance, per Doppler x code phase)"""
    grid = np.zeros((len(dopp_bins), N))
    sig2 = N * fs          # variance of complex correlator output with noise only (N0=1)
    for k in range(n_ms):
        seg = x[k * N:(k + 1) * N]
        tt = (np.arange(N) + k * N) / fs
        for i, fd in enumerate(dopp_bins):
            y = np.fft.ifft(np.fft.fft(seg * np.exp(-2j * np.pi * fd * tt)) * CODE_FFT_CONJ)
            grid[i] += np.abs(y) ** 2 / sig2
    return grid


# ---- 1. a single acquisition at 45 dB-Hz
fd_true, tau_true = 2250.0, 1234
x = make_signal(45, 1, fd_true, tau_true)
g = acquire(x, 1)
i, j = np.unravel_index(np.argmax(g), g.shape)
print(f"single 1-ms acquisition @45 dB-Hz: peak at Doppler {dopp_bins[i]:.0f} Hz (true {fd_true}), "
      f"code phase {j} samples (true {tau_true}); peak/mean = {g.max()/g.mean():.1f}")
check("FFT acquisition finds the right Doppler bin and code phase", abs(dopp_bins[i] - fd_true) <= 250
      and abs(j - tau_true) <= 1)

# ---- 2. Pd vs C/N0: Monte-Carlo vs theory
n_cells = len(dopp_bins) * 2046          # half-chip cells in +-5 kHz
pfa_sys = 1e-3
pfa_cell = pfa_sys / n_cells
print(f"\nsearch space: {n_cells} cells (2046 code x {len(dopp_bins)} Doppler); Pfa/cell = {pfa_cell:.2e}")


def pd_theory(cn0, K, T=1e-3, loss_db=0.0):
    thr = stats.chi2.isf(pfa_cell, 2 * K) / 2          # statistic here = sum |y|^2/sigma^2 (~Gamma(K,1))
    lam = 2 * K * 10 ** ((cn0 - loss_db) / 10) * T      # noncentrality for 2*stat
    return stats.ncx2.sf(2 * thr, 2 * K, lam), thr


trials = 150
print("  C/N0   K   Pd(sim, on-bin)   Pd(theory)")
res = []
for cn0, K in [(44, 1), (42, 1), (38, 5), (36, 10), (34, 20)]:
    pdt, thr = pd_theory(cn0, K)
    hits = 0
    for _ in range(trials):
        x = make_signal(cn0, K, 1000.0, rng.integers(0, N), rng.uniform(0, 2 * np.pi))
        # statistic at the true Doppler bin (exact bin -> no Doppler loss), max over +-1 sample
        gg = acquire_one = None
        stat = 0
        tt_all = np.arange(N * K) / fs
        grid = np.zeros(N)
        for k in range(K):
            seg = x[k * N:(k + 1) * N] * np.exp(-2j * np.pi * 1000.0 * tt_all[k * N:(k + 1) * N])
            y = np.fft.ifft(np.fft.fft(seg) * CODE_FFT_CONJ)
            grid += np.abs(y) ** 2 / (N * fs)
        hits += grid.max() > thr
    pds = hits / trials
    res.append((cn0, K, pds, pdt))
    print(f"  {cn0:4d} {K:3d}   {pds:14.2f}   {pdt:10.2f}")
# note: simulated uses exact sample alignment ~ within 1/4 chip; theory has zero code loss
check("Monte-Carlo Pd agrees with non-central chi-square theory within 0.15",
      all(abs(a - b) < 0.15 for _, _, a, b in res))
check("1 ms coherent, Pfa_sys 1e-3 over 43k cells needs ~44 dB-Hz for Pd=0.9 (fails at 40)",
      pd_theory(44.5, 1)[0] > 0.9 and pd_theory(40, 1)[0] < 0.2)

# required C/N0 for Pd = 0.9 vs K
print("\n  K (x1 ms non-coherent)  C/N0 for Pd=0.9 [dB-Hz]")
from scipy.optimize import brentq
req = {}
for K in [1, 2, 5, 10, 20, 50, 100]:
    req[K] = brentq(lambda c: pd_theory(c, K)[0] - 0.9, 10, 60)
    print(f"  {K:5d}                    {req[K]:5.1f}")
check("10x non-coherent (K=1->10) buys ~8 dB, < the 10 dB of 10x coherent (squaring loss)",
      7 < req[1] - req[10] < 9.5)
# coherent 10 ms instead of 10x1 ms non-coherent
req_coh10 = brentq(lambda c: pd_theory(c, 1, T=10e-3)[0] - 0.9, 10, 60)
print(f"  coherent 10 ms (K=1): {req_coh10:.1f} dB-Hz  (vs 10x1 ms non-coherent {req[10]:.1f})")
check("coherent integration beats non-coherent for the same total time", req_coh10 < req[10])

# ---- 3. Doppler loss
for T in [1e-3, 10e-3]:
    for dfr in [250, 500]:
        L = 10 * np.log10(np.sinc(dfr * T) ** 2)
        print(f"  coherent T={T*1e3:.0f} ms, frequency error {dfr} Hz -> loss {L:.1f} dB")
check("1 ms, 250 Hz (half of a 500 Hz bin) -> 0.9 dB loss", abs(10 * np.log10(np.sinc(0.25) ** 2) + 0.91) < 0.02)
check("10 ms needs bins ~ 50 Hz: 250 Hz error is a null (sinc^2(2.5) small)", np.sinc(2.5) ** 2 < 0.02)

# ---- 4. quantisation loss
def corr_snr(q, cn0=50, K=3000):
    vals = []
    for _ in range(K):
        x = make_signal(cn0, 1, 0.0, 0, 0.0)
        xr, xi = x.real, x.imag
        if q == 1:
            xr, xi = np.sign(xr), np.sign(xi)
        elif q == 2:
            s = np.std(xr); thr = 0.9674 * s       # near-optimal 2-bit threshold (magnitude 1 or 3)
            xr = np.sign(xr) * np.where(np.abs(xr) > thr, 3, 1)
            xi = np.sign(xi) * np.where(np.abs(xi) > thr, 3, 1)
        y = np.sum((xr + 1j * xi) * code_s)
        vals.append(y)
    vals = np.array(vals)
    m = np.mean(vals.real); v = np.var(vals.real) + np.var(vals.imag)
    return m ** 2 / v


s_inf = corr_snr(None); s1 = corr_snr(1); s2 = corr_snr(2)
l1 = 10 * np.log10(s1 / s_inf); l2 = 10 * np.log10(s2 / s_inf)
print(f"\n  quantisation loss: 1-bit {l1:.2f} dB (theory -1.96), 2-bit {l2:.2f} dB (theory ~ -0.55)")
check("1-bit loss ~ -1.96 dB (+-0.4)", abs(l1 + 1.96) < 0.4)
check("2-bit loss ~ -0.55 dB (+-0.4)", abs(l2 + 0.55) < 0.4)

# ---- 5. search time
dwell = 1e-3
serial = n_cells * dwell
print(f"\n  serial search, 1 correlator, 1 ms dwell: {serial:.0f} s per satellite per full sweep")
print(f"  parallel FFT (all code phases at once): {len(dopp_bins)*dwell*1e3:.0f} ms of signal per sweep "
      f"(21 FFT pairs of {N} points)")
rocket_d = 2 * 600 / 0.1903   # +-600 m/s LOS velocity adds +-3.2 kHz
print(f"  a rocket at 600 m/s LOS adds +-{rocket_d/2/1e3:.1f} kHz -> Doppler range grows "
      f"{(10e3 + rocket_d)/10e3:.1f}x unless aided")
check("serial search of full uncertainty takes tens of seconds (motivates massively parallel correlators)",
      serial > 20)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
