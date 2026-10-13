#!/usr/bin/env python3
"""
e3_signal_id.py -- numerical checks for kb/14-sdr-dsp/signal-identification-and-spectrum-survey.md

1. Symbol-rate line in |x|^2 for linearly modulated RRC signals: the alpha = 1/T Fourier
   coefficient of E|x(t)|^2 relative to the mean power is beta/pi (derived on the page);
   simulated QPSK at several roll-offs.  Rectangular-pulse PSK has NO |x|^2 line, but the
   delay-product x(t) x*(t - T/2) has |c1| = 1/pi.
2. Carrier-power lines: BPSK x^2 -> 2 df; QPSK x^2 none, x^4 -> 4 df; 8PSK x^4 none, x^8 -> 8 df;
   MSK x^2 -> two lines at 2 df +/- Rb/2.  Line-to-median ratio of each spectrum.
3. FSK/GFSK symbol rate: FM-discriminate, low-pass, square -> line at Rs.
4. OFDM cyclic-prefix autocorrelation: |r(N)| / r(0) = CP/(N+CP) (Wi-Fi 64+16 -> 0.2);
   cyclic frequency 1/(N+CP) samples.
5. LoRa chirp duration and slope versus SF/BW (what to read off a waterfall).
6. rtl_power hop plan (re-implementation of frequency_range() in osmocom rtl_power.c).
7. Burst intercept probability for a hopping survey receiver (formula vs Monte Carlo).
8. Occupancy threshold for a K-averaged power bin (Gamma statistics) and minimum SNR for
   Pd = 0.9 (non-central chi-square).
9. Symbol-rate estimator accuracy versus observation length: std ~ N^-1.5.
10. FSK modulation indices / Carson bandwidths for catalogue entries.

Run: python3 tools/verify/e3_signal_id.py      (prints PASS/FAIL per check, ~10 s)
"""
import numpy as np
from scipy import stats, signal

rng = np.random.default_rng(1)
results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")


def rrc_taps(beta, sps, span=12):
    """Unit-energy root-raised-cosine taps, span in symbols."""
    t = np.arange(-span * sps / 2, span * sps / 2 + 1) / sps
    h = np.zeros_like(t)
    for i, ti in enumerate(t):
        if abs(ti) < 1e-12:
            h[i] = 1 - beta + 4 * beta / np.pi
        elif beta > 0 and abs(abs(ti) - 1 / (4 * beta)) < 1e-9:
            h[i] = beta / np.sqrt(2) * ((1 + 2 / np.pi) * np.sin(np.pi / (4 * beta))
                                        + (1 - 2 / np.pi) * np.cos(np.pi / (4 * beta)))
        else:
            h[i] = (np.sin(np.pi * ti * (1 - beta)) + 4 * beta * ti * np.cos(np.pi * ti * (1 + beta))) / \
                   (np.pi * ti * (1 - (4 * beta * ti) ** 2))
    return h / np.sqrt(np.sum(h ** 2))


def psk_symbols(M, n):
    k = rng.integers(0, M, n)
    if M == 4:
        return np.exp(1j * (np.pi / 4 + np.pi / 2 * k))
    return np.exp(2j * np.pi * k / M)


def shaped(sym, sps, beta):
    up = np.zeros(len(sym) * sps, complex)
    up[::sps] = sym
    return np.convolve(up, rrc_taps(beta, sps), mode="same")


def coeff(x, f_norm):
    """Fourier coefficient of sequence x at normalised frequency f (cycles/sample)."""
    n = np.arange(len(x))
    return np.mean(x * np.exp(-2j * np.pi * f_norm * n))


# ---------------------------------------------------------------- 1. |x|^2 line vs roll-off
print("=== 1. Symbol-rate line in |x|^2: |c1/c0| = beta/pi for RRC pulses ===")
sps, nsym = 8, 40000
for beta in [0.1, 0.2, 0.35, 0.5, 1.0]:
    x = shaped(psk_symbols(4, nsym), sps, beta)
    x = x[200:-200]
    p = np.abs(x) ** 2
    ratio = abs(coeff(p, 1 / sps)) / np.mean(p)
    theory = beta / np.pi
    check(f"QPSK RRC beta={beta:4.2f}", abs(ratio - theory) < 0.1 * theory + 0.004,
          f"sim {ratio:.4f} vs beta/pi {theory:.4f} -> line {20*np.log10(theory):.1f} dB below |x|^2 DC")
# rectangular BPSK: no |x|^2 line, delay-product line 1/pi at tau = T/2
sym = psk_symbols(2, 20000)
xr = np.repeat(sym, sps)
p_rect = np.abs(xr) ** 2
c_rect = abs(coeff(p_rect, 1 / sps))
dp = xr[sps // 2:] * np.conj(xr[:-sps // 2])
c_dp = abs(coeff(dp, 1 / sps))
check("rect BPSK: |x|^2 has no symbol line", c_rect < 1e-6, f"|c1| = {c_rect:.2e}")
check("rect BPSK: delay-product (tau = T/2) |c1| = 1/pi", abs(c_dp - 1 / np.pi) < 0.01,
      f"sim {c_dp:.4f} vs {1/np.pi:.4f}")

# ---------------------------------------------------------------- 2. x^M carrier lines
print("\n=== 2. Power-law carrier lines (x^M) ===")
df = 0.03   # carrier offset, cycles/sample


def line_to_median_db(z, f_target, local=0.02):
    """Peak (within +/-2 bins of f_target) over the median of the LOCAL spectrum
    (+/- `local` cycles/sample, excluding +/-5 bins): a line must stand out of the
    continuous hump that the non-linearity also produces, not just out of the noise."""
    n = len(z)
    Z = np.abs(np.fft.fft(z * np.hanning(n))) ** 2
    f = np.fft.fftfreq(n)
    ft = (f_target + 0.5) % 1 - 0.5
    k = np.argmin(np.abs(f - ft))
    d = np.abs(((f - ft) + 0.5) % 1 - 0.5)
    ref = Z[(d < local) & (d > 5.0 / n)]
    return 10 * np.log10(Z[max(k - 2, 0):k + 3].max() / np.median(ref))


nsym = 8192
noise = lambda n, snr_db: (rng.normal(size=n) + 1j * rng.normal(size=n)) * np.sqrt(10 ** (-snr_db / 10) / 2)
cases = {}
for M in [2, 4, 8]:
    x = shaped(psk_symbols(M, nsym), sps, 0.35)
    x = x / np.sqrt(np.mean(np.abs(x) ** 2))
    x = (x + noise(len(x), 10)) * np.exp(2j * np.pi * df * np.arange(len(x)))
    for P in [2, 4, 8]:
        cases[(M, P)] = line_to_median_db(x ** P, P * df)
for (M, P), v in cases.items():
    print(f"  {M}-PSK raised to {P}: line at {P}*df is {v:5.1f} dB above the local spectrum median")
check("BPSK x^2 line present (> 25 dB)", cases[(2, 2)] > 25)
check("QPSK x^2 no line (< 12 dB), x^4 line (> 25 dB)", cases[(4, 2)] < 12 and cases[(4, 4)] > 25)
check("8PSK x^4 no line (< 12 dB), x^8 line (> 15 dB)", cases[(8, 4)] < 12 and cases[(8, 8)] > 15)
# MSK: x^2 -> lines at 2 df +/- Rb/2
bits = rng.integers(0, 2, nsym) * 2 - 1
h = 0.5
phase = np.cumsum(np.repeat(bits, sps)) * np.pi * h / sps
xm = np.exp(1j * phase) * np.exp(2j * np.pi * df * np.arange(len(phase)))
xm = xm + noise(len(xm), 10)
lp = line_to_median_db(xm ** 2, 2 * df + 0.5 / sps)
lm = line_to_median_db(xm ** 2, 2 * df - 0.5 / sps)
lc = line_to_median_db(xm ** 2, 2 * df)
check("MSK x^2 lines at 2df +/- Rb/2 (> 25 dB), none at 2df (< 12 dB)", lp > 25 and lm > 25 and lc < 12,
      f"+{lp:.1f} / -{lm:.1f} / centre {lc:.1f} dB")

# ---------------------------------------------------------------- 3. GFSK symbol rate via discriminator
print("\n=== 3. GFSK symbol rate: discriminator, low-pass, square ===")
bt = 0.5
tg = np.arange(-2 * sps, 2 * sps + 1) / sps
sig = np.sqrt(np.log(2)) / (2 * np.pi * bt)
g = np.exp(-tg ** 2 / (2 * sig ** 2)); g /= g.sum()
freq = np.convolve(np.repeat(bits, sps), g, mode="same")
xg = np.exp(1j * np.cumsum(freq) * np.pi * h / sps)
xg = xg + noise(len(xg), 15)
disc = np.angle(xg[1:] * np.conj(xg[:-1]))          # FM discriminator = PAM of the bits
lpf = signal.firwin(129, 0.75 / sps * 2)             # keep ~0.75 Rs of baseband
d = np.convolve(disc, lpf, mode="same")
y = d ** 2 - np.mean(d ** 2)                          # square-law: line at Rs (like |x|^2 for PSK)
Y = np.abs(np.fft.rfft(y * np.hanning(len(y)))) ** 2
fax = np.fft.rfftfreq(len(y))
band = (fax > 0.06) & (fax < 0.45)
fpk = fax[band][np.argmax(Y[band])]
check("GFSK BT=0.5 h=0.5: discriminator^2 strongest line at Rs = 1/sps", abs(fpk - 1 / sps) < 2 / len(y),
      f"found {fpk:.5f}, expected {1/sps:.5f} cycles/sample")
lr = line_to_median_db(y.astype(complex), 1 / sps)
check("GFSK line stands > 20 dB above its local spectrum", lr > 20, f"{lr:.1f} dB")
# NRZ (unfiltered) FSK: discriminator output is a constant +/-df except at transitions;
# its square is constant -> the line comes only from the transitions (filtering by the receiver)
d_nrz = np.repeat(bits, sps).astype(float)
c_nrz = abs(coeff(d_nrz ** 2, 1 / sps))
check("ideal NRZ discriminator output squared has no line (needs band-limiting)", c_nrz < 1e-9, f"|c1| {c_nrz:.1e}")

# ---------------------------------------------------------------- 4. OFDM CP autocorrelation
print("\n=== 4. OFDM cyclic prefix ===")
N, CP, nsymb = 64, 16, 2000
X = (rng.choice([-1, 1], (nsymb, N)) + 1j * rng.choice([-1, 1], (nsymb, N))) / np.sqrt(2)
X[:, 0] = 0
xt = np.fft.ifft(X, axis=1) * np.sqrt(N)
xo = np.concatenate([np.hstack([s[-CP:], s]) for s in xt])
r0 = np.mean(np.abs(xo) ** 2)
lags = np.arange(1, 100)
r = np.array([abs(np.mean(xo[L:] * np.conj(xo[:-L]))) for L in lags]) / r0
check("autocorrelation peak at lag N = 64", lags[np.argmax(r)] == N, f"peak lag {lags[np.argmax(r)]}")
check("peak height CP/(N+CP) = 0.2", abs(r.max() - CP / (N + CP)) < 0.02, f"sim {r.max():.3f}")
caf = abs(coeff(xo[N:] * np.conj(xo[:-N]), 1 / (N + CP))) / r0
print(f"  cyclic frequency 1/(N+CP) = {1/(N+CP):.5f} cyc/sample -> 250 kHz at 20 MS/s (Wi-Fi 4 us symbols); "
      f"CAF at lag N: {caf:.3f}")
check("CAF at alpha = 1/(N+CP), lag N is non-zero", caf > 0.05)
# LTE numerology for the catalogue
Tu = 1 / 15e3
for name, cp in [("normal CP sym 0", 160), ("normal CP sym 1-6", 144)]:
    print(f"  LTE {name}: CP {cp/30.72e6*1e6:.2f} us, symbol {(2048+cp)/30.72e6*1e6:.2f} us")
check("LTE slot = 0.5 ms (160 + 6*144 + 7*2048 samples at 30.72 MS/s)",
      abs((160 + 6 * 144 + 7 * 2048) / 30.72e6 - 0.5e-3) < 1e-12)

# ---------------------------------------------------------------- 5. LoRa chirps
print("\n=== 5. LoRa chirp duration / slope ===")
for bw in [125e3, 250e3, 500e3]:
    row = []
    for sf in range(7, 13):
        T = 2 ** sf / bw
        row.append(f"SF{sf} {T*1e3:7.3f} ms")
    print(f"  BW {bw/1e3:.0f} kHz: " + ", ".join(row))
check("SF7/125 kHz symbol = 1.024 ms; SF12/125 = 32.768 ms",
      abs(2 ** 7 / 125e3 - 1.024e-3) < 1e-12 and abs(2 ** 12 / 125e3 - 32.768e-3) < 1e-12)
print(f"  chirp slope BW^2/2^SF: SF7/125 {125e3**2/2**7:.3e} Hz/s, SF12/125 {125e3**2/2**12:.3e} Hz/s")
# spectrogram window that resolves the chirp: optimum ~ sqrt(1/slope)
for sf in [7, 12]:
    slope = 125e3 ** 2 / 2 ** sf
    print(f"  SF{sf}: optimum STFT window ~ 1/sqrt(slope) = {1/np.sqrt(slope)*1e6:.0f} us "
          f"(freq. resolution ~ {np.sqrt(slope)/1e3:.1f} kHz)")


# ---------------------------------------------------------------- 6. rtl_power hop plan
print("\n=== 6. rtl_power hop plan (re-implementation of rtl_power.c frequency_range) ===")
MAXR, MINR = 2_800_000, 1_000_000


def rtl_power_plan(lower, upper, max_bin, crop=0.0):
    downsample, passes = 1, 0
    for i in range(1, 1500):
        bw_seen = int((upper - lower) / i)
        bw_used = int(bw_seen / (1.0 - crop))
        if bw_used > MAXR:
            continue
        tunes = i
        break
    if bw_used < MINR:
        tunes = 1
        downsample = MAXR // bw_used
        bw_used = bw_used * downsample
    if downsample > 1:   # default (non-boxcar) path
        passes = int(np.log2(downsample))
        downsample = 1 << passes
        bw_used = int(bw_seen * downsample / (1.0 - crop))
    for i in range(1, 22):
        bin_e = i
        bin_size = bw_used / ((1 << i) * downsample)
        if bin_size <= max_bin:
            break
    nbins_hop = int((1 << bin_e) * (1 - crop))
    fft_time = (1 << bin_e) * downsample / bw_used
    return dict(tunes=tunes, rate=bw_used, bin=bin_size, bins=nbins_hop * tunes, fft_ms=fft_time * 1e3,
                downsample=downsample)


plans = {
    "433.05-434.79 MHz, 1 kHz bins": (433.05e6, 434.79e6, 1e3, 0.0),
    "433.05-434.79 MHz, 1 kHz, crop 25%": (433.05e6, 434.79e6, 1e3, 0.25),
    "863-870 MHz, 5 kHz, crop 25%": (863e6, 870e6, 5e3, 0.25),
    "902-928 MHz, 10 kHz, crop 25%": (902e6, 928e6, 10e3, 0.25),
    "917-925 MHz (SG), 2 kHz, crop 25%": (917e6, 925e6, 2e3, 0.25),
    "1574-1577 MHz (GNSS L1), 1 kHz, crop 25%": (1574e6, 1577e6, 1e3, 0.25),
}
for k, (lo, hi, b, c) in plans.items():
    pl = rtl_power_plan(lo, hi, b, c)
    print(f"  {k:42s}: {pl['tunes']:2d} hop(s) at {pl['rate']/1e6:.3f} MS/s, bin {pl['bin']:7.1f} Hz, "
          f"{pl['bins']} bins, one FFT {pl['fft_ms']:.2f} ms, downsample x{pl['downsample']}")
pl = rtl_power_plan(902e6, 928e6, 10e3, 0.25)
check("902-928 MHz with 25 % crop needs 13 hops at 2.667 MS/s", pl["tunes"] == 13 and abs(pl["rate"] - 2.6667e6) < 1e3)
pl = rtl_power_plan(433.05e6, 434.79e6, 1e3, 0.25)
check("433 MHz SRD band fits one hop", pl["tunes"] == 1)

# ---------------------------------------------------------------- 7. burst intercept probability
print("\n=== 7. Burst intercept by a hopping receiver ===")


def p_overlap(tau, dwell, revisit):
    return min(1.0, (tau + dwell) / revisit)


def p_full(tau, dwell, revisit):
    return max(0.0, (dwell - tau) / revisit)


for tau, dwell, revisit in [(0.05, 0.02, 0.26), (0.05, 0.10, 1.3), (0.0015, 0.02, 0.26)]:
    t0 = rng.uniform(0, revisit, 200000)
    # dwell window [0, dwell) repeated each revisit; burst [t0, t0+tau)
    ov = (t0 < dwell) | (t0 + tau > revisit)
    full = (t0 + tau <= dwell)
    po, pf = p_overlap(tau, dwell, revisit), p_full(tau, dwell, revisit)
    print(f"  burst {tau*1e3:6.1f} ms, dwell {dwell*1e3:5.0f} ms, revisit {revisit*1e3:5.0f} ms: "
          f"P(overlap) {po:.3f} (MC {ov.mean():.3f}), P(whole burst) {pf:.3f} (MC {full.mean():.3f})")
    check(f"  formula vs MC (tau={tau})", abs(po - ov.mean()) < 0.01 and abs(pf - full.mean()) < 0.01)
p = p_overlap(0.05, 0.02, 0.26)
n99 = np.ceil(np.log(0.01) / np.log(1 - p))
print(f"  repeating beacon (each repetition independent): {n99:.0f} repetitions to see it with 99 % probability")

# ---------------------------------------------------------------- 8. occupancy threshold statistics
print("\n=== 8. Occupancy threshold for K-averaged bins (linear averaging, as rtl_power does) ===")
for K in [1, 10, 100, 1000]:
    thr = stats.gamma.isf(1e-3, a=K, scale=1 / K)        # mean-normalised
    # min per-bin SNR for Pd = 0.9 at that threshold: K*avg of |s+n|^2 ~ ncx2(2K, 2K*snr)/2
    def pd(snr):
        return stats.ncx2.sf(thr * 2 * K, df=2 * K, nc=2 * K * snr)
    lo_, hi_ = 1e-4, 100.0
    for _ in range(80):
        mid = np.sqrt(lo_ * hi_)
        lo_, hi_ = (mid, hi_) if pd(mid) < 0.9 else (lo_, mid)
    print(f"  K={K:5d}: threshold {10*np.log10(thr):5.2f} dB above mean noise for Pfa 1e-3; "
          f"min bin SNR for Pd 0.9: {10*np.log10(hi_):6.2f} dB")
    if K == 1:
        check("K=1 threshold = 10log10(ln 1000) = 8.39 dB", abs(10 * np.log10(thr) - 10 * np.log10(np.log(1000))) < 0.01)
x = rng.exponential(size=(20000, 10)).mean(axis=1)
check("Gamma model of 10-average matches simulation (Pfa at threshold)",
      abs((x > stats.gamma.isf(1e-2, a=10, scale=0.1)).mean() - 1e-2) < 2.5e-3)
print(f"  log-average bias of a single exponential bin: {np.mean(10*np.log10(rng.exponential(size=10**6))):.2f} dB "
      f"(theory -2.51 dB) -- why log-averaged waterfalls read noise low")

# ---------------------------------------------------------------- 9. estimator accuracy vs N
print("\n=== 9. Symbol-rate estimate (|x|^2 line peak) std vs number of symbols ===")


def est_rate(x, f0, span):
    p = np.abs(x) ** 2 - np.mean(np.abs(x) ** 2)
    n = np.arange(len(p))
    grid = np.linspace(f0 - span, f0 + span, 401)
    vals = [abs(np.sum(p * np.exp(-2j * np.pi * f * n))) for f in grid]
    k = int(np.argmax(vals))
    lo_, hi_ = grid[max(k - 1, 0)], grid[min(k + 1, 400)]
    for _ in range(40):          # golden-section refine
        m1, m2 = lo_ + 0.382 * (hi_ - lo_), lo_ + 0.618 * (hi_ - lo_)
        v1 = abs(np.sum(p * np.exp(-2j * np.pi * m1 * n)))
        v2 = abs(np.sum(p * np.exp(-2j * np.pi * m2 * n)))
        lo_, hi_ = (m1, hi_) if v1 < v2 else (lo_, m2)
    return 0.5 * (lo_ + hi_)


Ns, stds = [256, 1024, 4096], []
for Nsym in Ns:
    e = []
    for _ in range(30):
        x = shaped(psk_symbols(4, Nsym), sps, 0.35)
        x = x / np.sqrt(np.mean(np.abs(x) ** 2)) + noise(len(x), 10)
        e.append(est_rate(x, 1 / sps, 2 / (Nsym * sps)) * sps - 1)
    stds.append(np.std(e))
    print(f"  N = {Nsym:5d} symbols: relative std of Rs estimate {np.std(e):.2e}")
slope = np.polyfit(np.log10(Ns), np.log10(stds), 1)[0]
check("std scales ~ N^-1.5 (Ciblat et al. 2002)", -1.8 < slope < -1.2, f"fitted slope {slope:.2f}")

# ---------------------------------------------------------------- 10. catalogue FSK numbers
print("\n=== 10. Catalogue: FSK indices and Carson bandwidths ===")
for name, dev, rs in [("POCSAG 512", 4.5e3, 512), ("POCSAG 1200", 4.5e3, 1200), ("POCSAG 2400", 4.5e3, 2400),
                      ("AIS GMSK (h=0.5)", 2.4e3, 9600)]:
    print(f"  {name:18s}: h = 2*df/Rs = {2*dev/rs:5.2f}; Carson 2(df + Rs/2) = {2*(dev+rs/2)/1e3:5.1f} kHz")
check("AIS deviation for h = 0.5 at 9600 b/s is 2.4 kHz", abs(0.5 * 9600 / 2 - 2400) < 1e-9)
print(f"  APRS AFSK on FM (3 kHz dev, 2.2 kHz top tone): Carson {2*(3+2.2):.1f} kHz")
print(f"  Broadcast FM stereo (75 kHz dev, 53 kHz MPX): Carson {2*(75+53):.0f} kHz; with RDS 57 kHz: {2*(75+57):.0f} kHz")
print(f"  ADS-B 1090ES: 8 us preamble + 112 us data = 120 us; PPM 0.5 us pulses -> main lobe +/-2 MHz")
print(f"  GPS C/A: 1.023 Mchip/s BPSK -> null-to-null {2*1.023:.3f} MHz; GSM frame 8 x 576.9 us = "
      f"{8*576.92e-3:.3f} ms -> {1/(8*576.92e-6):.1f} Hz (the '217 Hz' buzz)")
check("GSM TDMA frame rate ~ 216.7 Hz", abs(1 / (8 * 576.92e-6) - 216.7) < 0.2)
print(f"  FT8: 79 symbols x 0.16 s = {79*0.16:.2f} s in a 15 s slot; 8 tones x 6.25 Hz = 50 Hz")

print(f"\n{sum(results)}/{len(results)} checks passed")
print("ALL PASS" if all(results) else "SOME FAILED")
