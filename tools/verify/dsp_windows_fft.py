#!/usr/bin/env python3
"""Verification for kb/14-sdr-dsp/fft-spectral-analysis-windows.md

Checks (PASS/FAIL):
 1. Window figures of merit computed from first principles (coherent gain, ENBW,
    scalloping loss, highest sidelobe, 3/6 dB widths, worst-case processing loss)
    compared with the values tabulated by harris (1978).
 2. Tone-amplitude error at half-bin offset = scalloping loss.
 3. PSD scaling: |X|^2/(fs*S2) of complex white noise recovers the true density (dBFS/Hz);
    agreement with scipy.signal.welch; per-bin level falls 3 dB per doubling of N.
 4. Periodogram statistics: bins exponentially distributed; std of dB value 5.57 dB;
    averaging in dB under-reads noise by 2.51 dB (10 log10 e^-gamma).
 5. Welch averaging: variance ~ 1/K; 50 % overlap with Hann gives near-independent segments.
 6. Zero padding does not resolve two tones 0.7 bin apart; a 2x longer record does.
 7. Coherent FFT processing gain 10 log10(N/ENBW) for a tone in white noise.
 8. Parseval with window scaling (power in time == integrated PSD).
"""
import numpy as np
from scipy import signal

rng = np.random.default_rng(3)
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


# ---------------------------------------------------------------- 1. window table
def metrics(w, pad=256):
    N = len(w)
    S1, S2 = w.sum(), (w ** 2).sum()
    cg = S1 / N
    enbw = N * S2 / S1 ** 2
    M = N * pad
    W = np.abs(np.fft.fft(w, M))
    W /= W[0]
    WdB = 20 * np.log10(W + 1e-300)
    half = WdB[: M // 2]
    scallop = -WdB[pad // 2]  # half a bin = pad/2 fine-grid points
    # mainlobe edge: first local minimum
    k = 1
    while k < len(half) - 1 and not (half[k] <= half[k - 1] and half[k] <= half[k + 1]):
        k += 1
    sidelobe = half[k:].max()
    bw3 = 2 * np.argmax(half < -3.0103) / pad  # in bins (full width)
    bw6 = 2 * np.argmax(half < -6.0206) / pad
    wcpl = scallop + 10 * np.log10(enbw)
    return dict(cg=cg, enbw=enbw, scallop=scallop, sidelobe=sidelobe, bw3=bw3, bw6=bw6, wcpl=wcpl)


N = 1024
wins = {
    "rectangular": np.ones(N),
    "hann": signal.windows.hann(N, sym=False),
    "hamming": signal.windows.hamming(N, sym=False),
    "blackman": signal.windows.blackman(N, sym=False),
    "blackman-harris-4": signal.windows.blackmanharris(N, sym=False),
    "flattop (scipy/Matlab)": signal.windows.flattop(N, sym=False),
    "kaiser beta=6": signal.windows.kaiser(N, 6, sym=False),
    "kaiser beta=8.6": signal.windows.kaiser(N, 8.6, sym=False),
    "gaussian (sigma=N/8... a=2.5)": signal.windows.gaussian(N, N / 5.0, sym=False),
}
# reference values from harris 1978 Table 1 (highest sidelobe dB, CG, ENBW bins, 3dB BW bins, scallop dB, WCPL dB, 6dB BW)
harris = {
    "rectangular": (-13, 1.00, 1.00, 0.89, 3.92, 3.92, 1.21),
    "hann": (-32, 0.50, 1.50, 1.44, 1.42, 3.18, 2.00),
    "hamming": (-43, 0.54, 1.36, 1.30, 1.78, 3.10, 1.81),
    "blackman": (-58, 0.42, 1.73, 1.68, 1.10, 3.47, 2.35),
    "blackman-harris-4": (-92, 0.36, 2.00, 1.90, 0.83, 3.85, 2.72),
}
print(f"{'window':32s} {'CG':>5s} {'ENBW':>5s} {'3dB':>5s} {'6dB':>5s} {'scal':>5s} {'WCPL':>5s} {'PSLL':>7s}")
table = {}
for name, w in wins.items():
    m = metrics(w)
    table[name] = m
    print(f"{name:32s} {m['cg']:5.3f} {m['enbw']:5.3f} {m['bw3']:5.2f} {m['bw6']:5.2f} {m['scallop']:5.2f} {m['wcpl']:5.2f} {m['sidelobe']:7.1f}")
# Direct computation agrees with harris' Table 1 for rectangular and Hann to the printed precision.
# For Hamming, Blackman and Blackman-Harris a few printed entries differ from direct computation by
# 0.03-0.05 bin (3/6 dB widths) or 0.03 dB (Hamming scalloping: analytic value 1.752 dB, printed 1.78).
# We therefore test with tolerances that expose any gross error and PRINT every difference.
for name, (sl, cg, enbw, bw3, sc, wc, bw6) in harris.items():
    m = table[name]
    diffs = dict(PSLL=m["sidelobe"] - sl, CG=m["cg"] - cg, ENBW=m["enbw"] - enbw, BW3=m["bw3"] - bw3,
                 scallop=m["scallop"] - sc, WCPL=m["wcpl"] - wc, BW6=m["bw6"] - bw6)
    good = (abs(diffs["PSLL"]) < 1.0 and abs(diffs["CG"]) < 0.01 and abs(diffs["ENBW"]) < 0.015
            and abs(diffs["BW3"]) < 0.04 and abs(diffs["scallop"]) < 0.04 and abs(diffs["WCPL"]) < 0.03
            and abs(diffs["BW6"]) < 0.06)
    txt = " ".join(f"{k}{v:+.2f}" for k, v in diffs.items() if abs(v) >= 0.015)
    check(f"window '{name}' vs harris 1978", good, "(computed - printed): " + (txt if txt else "none >= 0.015"))
# analytic Hamming scalloping: W(1/2)/W(0) = (0.54*2/pi + 0.23*(2/pi - 2/(3pi))) / 0.54
ham_sc = -20 * np.log10((0.54 * 2 / np.pi + 0.23 * (2 / np.pi - 2 / (3 * np.pi))) / 0.54)
check("Hamming scalloping analytic = 1.752 dB (harris prints 1.78)", abs(ham_sc - table["hamming"]["scallop"]) < 0.005, f"{ham_sc:.3f} dB")
ft = table["flattop (scipy/Matlab)"]
check("flat-top scalloping < 0.02 dB, ENBW ~3.77 bins", ft["scallop"] < 0.02 and abs(ft["enbw"] - 3.77) < 0.02,
      f"scallop {ft['scallop']:.4f} dB, ENBW {ft['enbw']:.3f}")

# ---------------------------------------------------------------- 2. tone amplitude error
fs = 1.0
n = np.arange(N)
for name in ("rectangular", "hann", "blackman-harris-4", "flattop (scipy/Matlab)"):
    w = wins[name]
    errs = []
    for off in (0.0, 0.5):
        f0 = (100 + off) / N
        x = np.exp(2j * np.pi * f0 * n)  # amplitude 1 complex tone = 0 dBFS
        X = np.fft.fft(x * w) / w.sum()  # amplitude-normalised
        errs.append(20 * np.log10(np.abs(X).max()))
    check(f"half-bin amplitude error '{name}' = scallop", abs(-errs[1] - table[name]["scallop"]) < 0.02 and abs(errs[0]) < 1e-6,
          f"on-bin {errs[0]:.3f} dB, half-bin {errs[1]:.2f} dB")

# ---------------------------------------------------------------- 3. PSD scaling (complex SDR data)
fs = 2.4e6
N0_true = 1e-9  # full-scale units^2 per Hz (two-sided, complex)
Ns = 2 ** 20
sigma2 = N0_true * fs  # total complex variance
x = np.sqrt(sigma2 / 2) * (rng.standard_normal(Ns) + 1j * rng.standard_normal(Ns))
for Nfft in (1024, 2048, 4096):
    w = signal.windows.hann(Nfft, sym=False)
    S2 = (w ** 2).sum()
    segs = x[: (Ns // Nfft) * Nfft].reshape(-1, Nfft)
    P = np.mean(np.abs(np.fft.fft(segs * w, axis=1)) ** 2, axis=0)
    psd = P / (fs * S2)  # units^2/Hz
    per_bin_power = P / w.sum() ** 2  # what an amplitude-normalised FFT shows per bin
    est = 10 * np.log10(np.mean(psd))
    bin_db = 10 * np.log10(np.mean(per_bin_power))
    enbw_hz = fs * Nfft * S2 / w.sum() ** 2 / Nfft
    print(f"      Nfft={Nfft}: PSD {est:.2f} dBFS/Hz (true {10*np.log10(N0_true):.2f}); per-bin {bin_db:.2f} dBFS; ENBW {enbw_hz:.1f} Hz; bin+10log(ENBW)... {bin_db-10*np.log10(enbw_hz):.2f}")
    check(f"PSD estimate (Nfft={Nfft}) within 0.1 dB of true", abs(est - 10 * np.log10(N0_true)) < 0.1)
f, pw = signal.welch(x, fs=fs, window="hann", nperseg=2048, noverlap=1024, return_onesided=False, scaling="density")
check("scipy welch agrees (two-sided density)", abs(10 * np.log10(np.mean(pw)) - 10 * np.log10(N0_true)) < 0.1,
      f"{10*np.log10(np.mean(pw)):.2f} dBFS/Hz")
# per-bin level drops 3 dB per doubling of N
lv = []
for Nfft in (1024, 2048):
    w = signal.windows.hann(Nfft, sym=False)
    segs = x[: (Ns // Nfft) * Nfft].reshape(-1, Nfft)
    lv.append(10 * np.log10(np.mean(np.abs(np.fft.fft(segs * w, axis=1)) ** 2) / w.sum() ** 2))
check("per-bin noise level drops 3.01 dB when N doubles", abs((lv[0] - lv[1]) - 3.01) < 0.05, f"{lv[0]-lv[1]:.2f} dB")

# ---------------------------------------------------------------- 4. periodogram statistics
Nfft = 1024
segs = x[: 1000 * Nfft].reshape(1000, Nfft)
P = np.abs(np.fft.fft(segs * signal.windows.hann(Nfft, sym=False), axis=1)) ** 2
Pn = P / P.mean()
std_db = np.std(10 * np.log10(Pn))
bias_db = np.mean(10 * np.log10(Pn))
check("single periodogram: std of bin value in dB ~ 5.57 dB", abs(std_db - 5.57) < 0.05, f"{std_db:.2f} dB")
check("averaging in dB under-reads by 2.51 dB", abs(bias_db + 2.507) < 0.03, f"{bias_db:.3f} dB (theory {10*np.log10(np.exp(-np.euler_gamma)):.3f})")
check("bin powers exponential: std/mean = 1", abs(np.std(Pn) - 1) < 0.02, f"{np.std(Pn):.3f}")

# ---------------------------------------------------------------- 5. Welch variance
def welch_std_db(K, overlap):
    Nfft = 256
    hop = int(Nfft * (1 - overlap))
    L = Nfft + hop * (K - 1)
    out = []
    for _ in range(400):
        xx = rng.standard_normal(L) + 1j * rng.standard_normal(L)
        f, p = signal.welch(xx, window="hann", nperseg=Nfft, noverlap=Nfft - hop, return_onesided=False)
        out.append(p[10:-10])
    out = np.array(out)
    return np.std(out / out.mean())


for K in (4, 16, 64):
    s = welch_std_db(K, 0.0)
    check(f"Welch K={K} no overlap: normalised std = 1/sqrt(K)", abs(s - 1 / np.sqrt(K)) < 0.1 / np.sqrt(K), f"{s:.3f} vs {1/np.sqrt(K):.3f}")
s50 = welch_std_db(31, 0.5)  # 31 half-overlapped segments span the same data as 16 disjoint
s0 = welch_std_db(16, 0.0)
check("50 % overlap (Hann) on same data lowers variance", s50 < s0 * 0.85, f"std {s50:.3f} (31 segs, 50 %) vs {s0:.3f} (16 segs, 0 %)")

# ---------------------------------------------------------------- 6. zero padding vs resolution
# Two equal tones 0.7 bin apart (rectangular window). Whether a dip appears between them in a
# zero-padded spectrum depends on their relative phase (the lobes add or partly cancel), so
# zero-padding gives an UNRELIABLE answer; a record long enough (>= ~2 bins separation) resolves
# them for every phase.
def resolved(X, grid, fa, fb):
    """True if the two largest local maxima of |X| near the tones sit within 0.2 original bin of the
    true tone positions fa, fb (in original bins) and there is a >=2 dB dip between them.
    grid = FFT points per original bin."""
    m = np.abs(X)
    lo, hi = int(grid * (fa - 1)), int(grid * (fb + 1))
    seg = m[lo:hi]
    pk = [i for i in range(1, len(seg) - 1) if seg[i] > seg[i - 1] and seg[i] > seg[i + 1]]
    if len(pk) < 2:
        return False
    top = sorted(pk, key=lambda i: seg[i])[-2:]
    top.sort()
    pos = [(lo + i) / grid for i in top]
    dip = seg[top[0]:top[1] + 1].min()
    return (abs(pos[0] - fa) < 0.2 and abs(pos[1] - fb) < 0.2 and 20 * np.log10(min(seg[top[0]], seg[top[1]]) / dip) > 2)


Nr = 256
f1 = 60 / Nr
f2 = (60 + 0.7) / Nr
res_pad, res_long = [], []
for ph in rng.uniform(0, 2 * np.pi, 60):
    n = np.arange(Nr)
    x2 = np.exp(2j * np.pi * f1 * n) + np.exp(2j * np.pi * f2 * n + 1j * ph)
    res_pad.append(resolved(np.fft.fft(x2, 16 * Nr), 16, 60, 60.7))
    n2 = np.arange(4 * Nr)
    x3 = np.exp(2j * np.pi * f1 * n2) + np.exp(2j * np.pi * f2 * n2 + 1j * ph)
    res_long.append(resolved(np.fft.fft(x3, 16 * 4 * Nr), 64, 60, 60.7))
# phase-aligned at record centre: lobes add -> never resolved by padding
nc = np.arange(Nr) - (Nr - 1) / 2
xc = np.exp(2j * np.pi * f1 * nc) + np.exp(2j * np.pi * f2 * nc)
aligned = resolved(np.fft.fft(xc, 16 * Nr), 16, 60, 60.7)
# (with a naive local-maximum count, ~20 % of phases show two peaks -- but at the wrong frequencies)
check("zero-padding x16 never correctly resolves a 0.7-bin pair", np.mean(res_pad) == 0,
      f"correctly resolved in {100*np.mean(res_pad):.0f} % of 60 random phases")
check("zero-padding: centre-aligned phases -> not resolved", not aligned)
check("4x longer record resolves the pair for every phase", all(res_long), f"{100*np.mean(res_long):.0f} %")

# ---------------------------------------------------------------- 7. coherent processing gain
Nfft = 4096
w = signal.windows.hann(Nfft, sym=False)
snr_in_db = -20.0
A = 1.0
sig_n = np.sqrt(A ** 2 / 10 ** (snr_in_db / 10))  # total noise std (complex)
res = []
for _ in range(200):
    nn = np.arange(Nfft)
    xx = A * np.exp(2j * np.pi * (500 / Nfft) * nn) + sig_n / np.sqrt(2) * (rng.standard_normal(Nfft) + 1j * rng.standard_normal(Nfft))
    X = np.abs(np.fft.fft(xx * w)) ** 2
    res.append((X[500], np.mean(np.delete(X, [499, 500, 501]))))
res = np.array(res)
snr_bin = 10 * np.log10(np.mean(res[:, 0] - res[:, 1]) / np.mean(res[:, 1]))
pred = snr_in_db + 10 * np.log10(Nfft / table["hann"]["enbw"])
check("FFT processing gain = 10log10(N/ENBW)", abs(snr_bin - pred) < 0.3, f"bin SNR {snr_bin:.2f} dB vs {pred:.2f} dB (input {snr_in_db} dB)")

# ---------------------------------------------------------------- 8. Parseval with scaling
Nfft = 2048
w = signal.windows.blackmanharris(Nfft, sym=False)
xx = x[:Nfft * 200].reshape(200, Nfft)
p_time = np.mean(np.abs(xx) ** 2)
P = np.mean(np.abs(np.fft.fft(xx * w, axis=1)) ** 2, axis=0) / (fs * (w ** 2).sum())
p_freq = np.sum(P) * fs / Nfft
check("Parseval: sum(PSD)*df == mean |x|^2", abs(10 * np.log10(p_freq / p_time)) < 0.05, f"{10*np.log10(p_freq/p_time):+.3f} dB")

print("\nALL PASS" if ok_all else "\nSOME FAIL")
