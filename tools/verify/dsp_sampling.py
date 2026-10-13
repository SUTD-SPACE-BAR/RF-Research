#!/usr/bin/env python3
"""Verification for kb/14-sdr-dsp/sampling-aliasing-bandpass-sampling.md

Checks (each prints PASS/FAIL):
 1. Alias (apparent) frequency formula for real and complex sampling vs FFT peak.
 2. Bandpass-sampling valid-fs rule 2fH/n <= fs <= 2fL/(n-1) vs brute-force
    "band lies in one Nyquist zone" and vs a multitone simulation (injective folding).
 3. Spectral inversion in even Nyquist zones.
 4. Worked examples: 70 MHz IF / 20 MHz BW; 433 MHz ISM band; LoRa 125 kHz channel.
 5. Noise folding: SNR penalty when white noise from K Nyquist zones folds in.
 6. Clock-jitter SNR = -20 log10(2 pi f sigma_t) by Monte-Carlo sampling.
 7. Ideal ADC SNR 6.02N+1.76 dB, oversampling processing gain.
 8. Zero-order-hold (DAC) sinc droop: 3.92 dB at Nyquist.
 9. Whittaker-Shannon sinc reconstruction of a bandlimited signal.
10. Anti-alias filter order needed (Butterworth) for a stated rejection.
"""
import numpy as np

rng = np.random.default_rng(1)
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


# ---------------------------------------------------------------- 1. alias freq
def alias_real(f, fs):
    """Apparent frequency (0..fs/2) of a real tone f sampled at fs."""
    r = np.mod(f, fs)
    return np.where(r > fs / 2, fs - r, r)


def alias_complex(f, fs):
    """Apparent frequency (-fs/2..fs/2) of complex tone exp(j2pi f t)."""
    return np.mod(f + fs / 2, fs) - fs / 2


fs = 1e6
N = 2 ** 14
t = np.arange(N) / fs
worst = 0
for f in rng.uniform(0, 20e6, 50):
    x = np.cos(2 * np.pi * f * t)
    X = np.abs(np.fft.rfft(x * np.hanning(N)))
    fpk = np.argmax(X) * fs / N
    worst = max(worst, abs(fpk - alias_real(f, fs)))
check("real-sampling alias formula vs FFT", worst < 2 * fs / N, f"worst err {worst:.1f} Hz (bin {fs/N:.1f} Hz)")
worst = 0
for f in rng.uniform(-20e6, 20e6, 50):
    x = np.exp(2j * np.pi * f * t)
    X = np.abs(np.fft.fftshift(np.fft.fft(x * np.hanning(N))))
    fax = (np.arange(N) - N // 2) * fs / N
    fpk = fax[np.argmax(X)]
    worst = max(worst, abs(fpk - alias_complex(f, fs)))
check("complex-sampling alias formula vs FFT", worst < 2 * fs / N, f"worst err {worst:.1f} Hz")


# ---------------------------------------------------------------- 2. bandpass rule
def valid_fs_ranges(fL, fH):
    """List of (n, fs_min, fs_max) alias-free uniform real sampling rates."""
    B = fH - fL
    out = []
    for n in range(1, int(np.floor(fH / B)) + 1):
        lo = 2 * fH / n
        hi = np.inf if n == 1 else 2 * fL / (n - 1)
        if lo <= hi:
            out.append((n, lo, hi))
    return out


def in_one_zone(fL, fH, fs):
    """Alias-free iff [fL,fH] fits inside one Nyquist zone [m fs/2, (m+1) fs/2]."""
    m = np.floor(2 * fL / fs)
    return fH <= (m + 1) * fs / 2 + 1e-9


def rule_says_ok(fL, fH, fs):
    return any(lo - 1e-9 <= fs <= hi + 1e-9 for _, lo, hi in valid_fs_ranges(fL, fH))


mism = 0
trials = 0
for _ in range(200):
    fL = rng.uniform(1e6, 100e6)
    B = rng.uniform(0.2e6, 30e6)
    fH = fL + B
    for fs_ in rng.uniform(2 * B * 0.9, 2.5 * fH, 50):
        trials += 1
        mism += rule_says_ok(fL, fH, fs_) != in_one_zone(fL, fH, fs_)
check("bandpass rule == one-Nyquist-zone criterion", mism == 0, f"{mism} mismatches in {trials}")


def multitone_injective(fL, fH, fs, K=4001):
    """Sample K tones densely spread over [fL,fH]; alias-free iff the folded
    frequencies stay strictly ordered (no fold-back => no two tones collide)."""
    fk = np.linspace(fL, fH, K)
    a = alias_real(fk, fs)
    d = np.diff(a)
    return bool(np.all(d > 0) or np.all(d < 0))


mism = 0
for _ in range(2000):
    fL = rng.uniform(1e6, 100e6)
    B = rng.uniform(0.2e6, 30e6)
    fH = fL + B
    fs_ = rng.uniform(2 * B, 2.5 * fH)
    # exclude razor-edge cases within 0.1 % of a boundary
    edges = [e for _, lo, hi in valid_fs_ranges(fL, fH) for e in (lo, hi) if np.isfinite(e)]
    if any(abs(fs_ - e) / e < 2e-3 for e in edges):
        continue
    mism += multitone_injective(fL, fH, fs_) != rule_says_ok(fL, fH, fs_)
check("bandpass rule vs multitone folding simulation", mism == 0, f"{mism} mismatches")

# ---------------------------------------------------------------- 3. spectral inversion
fs = 100e6
x_lo, x_hi = 60e6, 70e6  # zone 2 (50-100 MHz): even zone -> inverted
check("zone-2 band is spectrally inverted", alias_real(x_lo, fs) > alias_real(x_hi, fs),
      f"60->{alias_real(x_lo, fs)/1e6:.0f} MHz, 70->{alias_real(x_hi, fs)/1e6:.0f} MHz")
x_lo, x_hi = 110e6, 120e6  # zone 3 (100-150 MHz): odd -> upright
check("zone-3 band is upright", alias_real(x_lo, fs) < alias_real(x_hi, fs),
      f"110->{alias_real(x_lo, fs)/1e6:.0f} MHz, 120->{alias_real(x_hi, fs)/1e6:.0f} MHz")

# ---------------------------------------------------------------- 4. worked examples
print("\n-- Example: 70 MHz IF, 20 MHz bandwidth (60-80 MHz)")
r = valid_fs_ranges(60e6, 80e6)
for n, lo, hi in r:
    print(f"   n={n}: {lo/1e6:8.3f} <= fs <= {hi/1e6 if np.isfinite(hi) else np.inf:8.3f} MHz")
check("70 MHz IF: n=3 range is 53.33-60 MHz", abs(r[2][1] - 53.333e6) < 1e4 and abs(r[2][2] - 60e6) < 1)
check("70 MHz IF: n=4 range is the single point 40 MHz (pathological)", abs(r[3][1] - 40e6) < 1 and abs(r[3][2] - 40e6) < 1)
# guard-banded version: filter transition bands widen the band to 55-85 MHz
rg = valid_fs_ranges(55e6, 85e6)
print("   with 5 MHz guard bands (55-85 MHz):", [(n, round(lo/1e6, 2), round(hi/1e6, 2) if np.isfinite(hi) else 'inf') for n, lo, hi in rg])

print("-- Example: 433.05-434.79 MHz ISM band sampled directly")
r = valid_fs_ranges(433.05e6, 434.79e6)
nmax = r[-1][0]
print(f"   n_max = {nmax}; highest few n:")
for n, lo, hi in r[-3:]:
    print(f"   n={n}: {lo/1e6:.4f}-{hi/1e6:.4f} MHz (width {(hi-lo)/1e3:.1f} kHz)")
# pick a practical n where the window is >= 2 MHz wide
prac = [(n, lo, hi) for n, lo, hi in r if hi - lo > 2e6 and n > 1]
n, lo, hi = prac[-1]
print(f"   largest n with a >=2 MHz wide fs window: n={n}: {lo/1e6:.3f}-{hi/1e6:.3f} MHz")
check("433 MHz ISM: n_max = floor(fH/B) = 249", nmax == 249)
# e.g. fs = 30 MHz: which zone, where does 433.92 land?
fs = 30e6
check("433 ISM band at fs=30 MHz lies in one zone", in_one_zone(433.05e6, 434.79e6, fs),
      f"433.92 MHz appears at {alias_real(433.92e6, fs)/1e6:.2f} MHz, zone {int(np.floor(2*433.92e6/fs))+1}")

# ---------------------------------------------------------------- 5. noise folding
# white noise of density N0 over 0..K*fs/2 (no AAF) folds into 0..fs/2 -> K x power
fs = 1e6
K = 8
Nn = 2 ** 18
fsim = K * fs  # simulate a K-times faster "analog" grid
wn = rng.standard_normal(Nn * K)  # flat 0..K fs/2
p_band = np.var(wn)  # all of it folds
decim = wn[::K]  # sample without filtering
check("unfiltered decimation keeps full noise power (K-fold density increase)",
      abs(np.var(decim) / p_band - 1) < 0.02, f"ratio {np.var(decim)/p_band:.3f}; density up {10*np.log10(K):.1f} dB")

# ---------------------------------------------------------------- 6. jitter SNR
def jitter_snr_mc(fin, sig_t, n=200000):
    tt = np.arange(n) / 3e9 + rng.uniform(0, 1e-6)
    ideal = np.sin(2 * np.pi * fin * tt)
    jit = np.sin(2 * np.pi * fin * (tt + sig_t * rng.standard_normal(n)))
    e = jit - ideal
    return 10 * np.log10(np.mean(ideal ** 2) / np.mean(e ** 2))


for fin, sj in [(70e6, 100e-15), (433.92e6, 100e-15), (433.92e6, 1e-12), (1575.42e6, 300e-15)]:
    mc = jitter_snr_mc(fin, sj)
    th = -20 * np.log10(2 * np.pi * fin * sj)
    check(f"jitter SNR f={fin/1e6:.2f} MHz sigma={sj*1e15:.0f} fs", abs(mc - th) < 0.2, f"MC {mc:.2f} dB vs formula {th:.2f} dB")

# ---------------------------------------------------------------- 7. ADC SNR / processing gain
for bits in (8, 12, 14):
    n = 2 ** 16
    tt = np.arange(n)
    x = (2 ** (bits - 1) - 0.5) * np.sin(2 * np.pi * 0.1234567 * tt)
    q = np.round(x)
    snr = 10 * np.log10(np.mean(x ** 2) / np.mean((q - x) ** 2))
    check(f"ideal {bits}-bit ADC SNR = 6.02N+1.76", abs(snr - (6.02 * bits + 1.76)) < 0.3, f"{snr:.2f} vs {6.02*bits+1.76:.2f} dB")
pg = 10 * np.log10(2.4e6 / 125e3)
check("processing gain complex 2.4 MS/s -> 125 kHz = 10log(fs/B)", abs(pg - 12.83) < 0.01, f"{pg:.2f} dB (complex sampling: noise spread over fs, not fs/2)")

# ---------------------------------------------------------------- 8. ZOH droop
droop = -20 * np.log10(np.sinc(0.5))
check("ZOH sinc droop at fs/2 = 3.92 dB", abs(droop - 3.92) < 0.01, f"{droop:.3f} dB; at 0.4 fs {-20*np.log10(np.sinc(0.4)):.2f} dB")

# ---------------------------------------------------------------- 9. sinc reconstruction
fs = 10.0
T = 1 / fs
n = np.arange(-400, 401)
freqs = rng.uniform(0, 4.0, 6)  # all < fs/2 = 5
ph = rng.uniform(0, 2 * np.pi, 6)
sig = lambda tt: sum(np.cos(2 * np.pi * f * tt + p) for f, p in zip(freqs, ph))
xs = sig(n * T)
tq = rng.uniform(-5, 5, 200)  # query points well inside the record
xr = np.array([np.sum(xs * np.sinc((tqq - n * T) / T)) for tqq in tq])
err = np.max(np.abs(xr - sig(tq))) / np.sqrt(np.mean(sig(tq) ** 2))
check("sinc (Whittaker-Shannon) reconstruction of bandlimited signal", err < 0.02, f"max rel err {err:.4f} (finite 801-sample truncation)")

# ---------------------------------------------------------------- 10. AAF order
# Butterworth: attenuation at f = 10 log10(1+(f/fc)^(2N))
def butter_order(fc, fstop, att_db):
    return int(np.ceil(np.log10(10 ** (att_db / 10) - 1) / (2 * np.log10(fstop / fc))))


# real-sampling ADC at fs=100 MS/s, passband to 40 MHz, aliases landing in band must be down 74 dB:
# worst alias source is at fs - 40 MHz = 60 MHz
Nb = butter_order(40e6, 60e6, 74)
check("Butterworth order for 74 dB at 1.5x fc", Nb == 22, f"N = {Nb} (why real SDRs oversample + decimate digitally)")
# oversample 4x: passband 40 MHz, fs = 400 MS/s, worst alias at 360 MHz
Nb2 = butter_order(40e6, 360e6, 74)
check("with 4x oversampling order drops", Nb2 == 4, f"N = {Nb2}")

print("\nALL PASS" if ok_all else "\nSOME FAIL")
