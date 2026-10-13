#!/usr/bin/env python3
"""S7 (W5-S7) receiver-DSP feature checks for kb/14-sdr-dsp/software-demodulation.md
"Receiver DSP features in software" section.

 §1 robust impulse threshold: median|x|/sqrt(ln 2) is unbiased by sparse impulses; mean/rms are not
 §2 LoRa SF7 in Bernoulli-Gaussian impulsive noise: SER with no blanker, a zeroing blanker and a
    clipper, blanker in the wide (4x oversampled) path vs after the decimation filter
 §3 blanking cost on a clean signal: loss ~ -10log10(1 - p_blank)
 §4 spectral subtraction: band SNR improves, SNR inside the occupied bins does not
 §5 IF shift / passband tuning: complex band-pass = low-pass prototype x e^{j w0 n};
    shifting the passband 400 Hz improves rejection of a 2.8 kHz neighbour
Run: python3 tools/verify/s7_noise_blanker.py   (≈ 10 s)
"""
import numpy as np
from scipy import signal

rng = np.random.default_rng(14)
ok = True


def check(name, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")


def cn(n, p=1.0):
    return np.sqrt(p / 2) * (rng.standard_normal(n) + 1j * rng.standard_normal(n))


# ---------------------------------------------------------------- §1
print("§1 Robust noise-level estimate for the blanker threshold")
n = 200000
x = cn(n)  # sigma^2 = 1
imp = rng.random(n) < 0.005
x_imp = x + imp * cn(n, 1e4)   # impulses 40 dB above the noise, 0.5 % of samples
for name, est in (("rms", lambda v: np.sqrt(np.mean(np.abs(v) ** 2))),
                  ("mean|x|*2/sqrt(pi)", lambda v: np.mean(np.abs(v)) * 2 / np.sqrt(np.pi)),
                  ("median|x|/sqrt(ln2)", lambda v: np.median(np.abs(v)) / np.sqrt(np.log(2)))):
    print(f"  {name:22s}: clean {est(x):.3f}, with impulses {est(x_imp):.3f} (true 1.000)")
med = np.median(np.abs(x_imp)) / np.sqrt(np.log(2))
check("median estimator within 1 % despite impulses", abs(med - 1) < 0.01)
check("rms estimator inflated > 2x", np.sqrt(np.mean(np.abs(x_imp) ** 2)) > 2)
# false-blank rate on Gaussian noise for threshold k*sigma: P(|x|>k sigma) = exp(-k^2)
for kk in (3, 4, 5):
    print(f"  threshold {kk} sigma: Gaussian false-blank fraction exp(-k^2) = {np.exp(-kk**2):.1e}, "
          f"measured {np.mean(np.abs(x) > kk):.1e}")
xb = cn(4_000_000)
print(f"  (4e6-sample check at 3 sigma: {np.mean(np.abs(xb) > 3):.2e})")
check("false-blank formula k=3", abs(np.mean(np.abs(xb) > 3) / np.exp(-9) - 1) < 0.1)

# ---------------------------------------------------------------- §2 LoRa
print("§2 LoRa SF7 (BW = 125 kHz) in impulsive noise")
SF = 7
M = 2 ** SF
OS = 4                                   # wide path at 4x BW (500 kS/s)
nn = np.arange(M * OS)
base = np.exp(1j * 2 * np.pi * (nn ** 2 / (2 * M * OS * OS) - 0.5 * nn / OS))  # up-chirp sampled at OS*BW
# decimation filter (wide path -> BW): 63-tap low-pass at 0.5 BW
h = signal.firwin(63, 0.5 / OS * 2 * 0.98)
gd = (len(h) - 1) // 2


# exact shifted chirp: build directly to avoid roll phase discontinuity issues
def chirp_s(s):
    k = (nn / OS + s) % M
    return np.exp(1j * 2 * np.pi * (k ** 2 / (2 * M) - 0.5 * k))


down = np.conj(chirp_s(0)[::OS])


def demod(z_bw):
    return int(np.argmax(np.abs(np.fft.fft(z_bw * down))))


def blank(z, kk=4.0, guard=1):
    sig = np.median(np.abs(z)) / np.sqrt(np.log(2))
    hit = np.abs(z) > kk * sig
    if guard:
        hit = np.convolve(hit, np.ones(2 * guard + 1), "same") > 0
    out = z.copy()
    out[hit] = 0
    return out, hit.mean()


def clip(z, kk=4.0):
    sig = np.median(np.abs(z)) / np.sqrt(np.log(2))
    a = np.abs(z)
    lim = kk * sig
    out = z.copy()
    big = a > lim
    out[big] = z[big] / a[big] * lim
    return out


def decimate(z):
    # filter then take every OS-th sample (zero-phase alignment by group delay, circular)
    zz = np.concatenate([z[-gd:], z, z[:gd]])
    y = np.convolve(zz, h, "valid")
    return y[::OS]


def run(snr_db, p_imp, imp_db, nsym=3000):
    # noise power per sample in the wide path such that SNR in BW = snr_db
    # signal |x|=1; noise in BW = Pn_wide/OS
    Pn_wide = OS * 10 ** (-snr_db / 10)
    err = dict(none=0, blank_wide=0, clip_wide=0, blank_after=0)
    frac = []
    for _ in range(nsym):
        s = rng.integers(M)
        x = chirp_s(s)
        w = cn(len(x), Pn_wide)
        hit = rng.random(len(x)) < p_imp
        w = w + hit * cn(len(x), Pn_wide * 10 ** (imp_db / 10))
        r = x + w
        err["none"] += demod(decimate(r)) != s
        b, fr = blank(r)
        frac.append(fr)
        err["blank_wide"] += demod(decimate(b)) != s
        err["clip_wide"] += demod(decimate(clip(r))) != s
        d = decimate(r)
        db_, _ = blank(d)
        err["blank_after"] += demod(db_) != s
    return {k_: v / nsym for k_, v in err.items()}, np.mean(frac)


res0, _ = run(-8, 0.0, 0)
print(f"  AWGN only, SNR -8 dB: SER {res0['none']:.4f} (no blanker), {res0['blank_wide']:.4f} (blanker on)")
res, fr = run(-8, 0.005, 40)
print(f"  + impulses 0.5 % of wide-path samples, 40 dB above the noise (total noise +{10*np.log10(1+0.005*1e4):.1f} dB):")
for k_, v in res.items():
    print(f"     {k_:12s}: SER {v:.4f}")
print(f"     blanked fraction of samples (incl. +/-1 guard) {fr*100:.2f} %")
check("impulses wreck LoRa SER without blanker (>30 %)", res["none"] > 0.3)
check("wide-path blanker restores SER to within 2x of AWGN-only (or < 1 %)",
      res["blank_wide"] < max(2 * res0["none"], 0.01))
check("blanking after the decimation filter is worse than before it",
      res["blank_after"] > 2 * res["blank_wide"])
check("clipper helps but less than the zeroing blanker", res["blank_wide"] <= res["clip_wide"] < res["none"])
check("blanker costs nothing measurable in pure AWGN", res0["blank_wide"] <= res0["none"] + 0.01)

# ---------------------------------------------------------------- §3
print("§3 Blanking loss on a clean signal")
for p in (0.01, 0.05, 0.2):
    L = -10 * np.log10(1 - p)
    # simulate: tone energy after zeroing fraction p (random), coherent sum
    N = 4096
    t = np.exp(1j * 2 * np.pi * 0.1 * np.arange(N))
    keep = rng.random(N) >= p
    g = np.abs(np.sum(np.conj(t) * t * keep)) ** 2 / N ** 2   # matched (coherent) sum
    nloss = np.mean(keep)  # noise power kept
    snr_loss = -10 * np.log10(g / nloss)
    print(f"  blank {p*100:4.0f} % of samples: theory {L:.2f} dB, simulated coherent SNR loss {snr_loss:.2f} dB")
check("blanking loss formula", abs(snr_loss - (-10 * np.log10(1 - 0.2))) < 0.15)

# ---------------------------------------------------------------- §4 spectral subtraction
print("§4 Spectral subtraction (3 tones in white noise, 256-pt Hann frames, 50 % overlap)")
fs, N = 8000, 256
L = 400 * N
tt = np.arange(L) / fs
tones = sum(0.25 * np.exp(1j * 2 * np.pi * f0 * tt) for f0 in (500, 1250, 2000))   # each -12 dB per sample, ~+10 dB per bin
noise = cn(L, 1.0)
xin = tones + noise
f, t_, Z = signal.stft(xin, fs, window="hann", nperseg=N, noverlap=N // 2, return_onesided=False)
_, _, Zn = signal.stft(noise, fs, window="hann", nperseg=N, noverlap=N // 2, return_onesided=False)
_, _, Zs = signal.stft(tones, fs, window="hann", nperseg=N, noverlap=N // 2, return_onesided=False)
Pn = np.mean(np.abs(Zn) ** 2, axis=1, keepdims=True)  # noise estimate (from a 'pause' = noise-only record)
alpha, beta = 2.0, 0.01   # over-subtraction factor, spectral floor
G = np.maximum(1 - alpha * Pn / np.maximum(np.abs(Z) ** 2, 1e-30), beta)   # power-subtraction gain
Y = np.sqrt(G) * Z
bins = [np.argmin(np.abs(f - f0)) for f0 in (500, 1250, 2000)]
# band SNR: total tone power / total noise power, before and after (apply same gain to separated parts)
Ys, Yn = np.sqrt(G) * Zs, np.sqrt(G) * Zn
band_before = np.sum(np.abs(Zs) ** 2) / np.sum(np.abs(Zn) ** 2)
band_after = np.sum(np.abs(Ys) ** 2) / np.sum(np.abs(Yn) ** 2)
inb_before = np.sum(np.abs(Zs[bins]) ** 2) / np.sum(np.abs(Zn[bins]) ** 2)
inb_after = np.sum(np.abs(Ys[bins]) ** 2) / np.sum(np.abs(Yn[bins]) ** 2)
print(f"  band SNR (0-8 kHz)   : {10*np.log10(band_before):6.1f} dB -> {10*np.log10(band_after):6.1f} dB")
print(f"  SNR in the tone bins : {10*np.log10(inb_before):6.1f} dB -> {10*np.log10(inb_after):6.1f} dB")
iso = np.mean(G[[i for i in range(N) if all(abs(i - b) > 3 for b in bins)]] > 0.5)
print(f"  'musical noise': fraction of empty time-frequency cells passed with gain > 0.5: {iso*100:.1f} %")
check("spectral subtraction raises band SNR by > 5 dB", 10 * np.log10(band_after / band_before) > 5)
check("in-bin SNR changes by < 1.5 dB", abs(10 * np.log10(inb_after / inb_before)) < 1.5)

# ---------------------------------------------------------------- §5 IF shift
print("§5 IF shift / passband tuning (USB filter 300-2700 Hz, fs = 12 kHz)")
fs = 12000
proto = signal.firwin(255, 1200, fs=fs)          # low-pass prototype +/-1.2 kHz -> 2.4 kHz wide
def bpf(center):
    return proto * np.exp(1j * 2 * np.pi * center * np.arange(len(proto)) / fs)
def resp(hh, f0):
    w, H = signal.freqz(hh, worN=[f0], fs=fs)
    return 20 * np.log10(np.abs(H[0]) + 1e-15)
for shift in (0, -300):
    hh = bpf(1500 + shift)
    print(f"  shift {shift:5d} Hz: passband {300+shift}-{2700+shift} Hz; "
          f"gain at 1000 Hz {resp(hh,1000):6.2f} dB, at neighbour 2600 Hz {resp(hh,2600):6.1f} dB")
r0, r1 = resp(bpf(1500), 2600), resp(bpf(1200), 2600)
print(f"  IF shift improves rejection of the 2.6 kHz neighbour by {r0-r1:.1f} dB")
check("300 Hz IF shift adds > 30 dB rejection of an in-passband 2.6 kHz neighbour", r0 - r1 > 30)
check("complex BPF = shifted prototype keeps wanted 1 kHz tone within 0.1 dB", abs(resp(bpf(1200), 1000)) < 0.1)

print("\nALL PASS" if ok else "\nSOME FAILED")
