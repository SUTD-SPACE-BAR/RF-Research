#!/usr/bin/env python3
"""S7 (W5-S7) DSP leftovers for kb/14-sdr-dsp/fft-spectral-analysis-windows.md
"Beyond the bin grid" section.

 §1 inter-bin (sub-bin) frequency estimators, noise-free bias vs true offset delta:
      parabolic on |X| in dB (rect, Hann), Jacobsen (rect), Candan (rect, tan(pi/N)/(pi/N) correction),
      Quinn's first and second estimators (rect), Grandke magnitude formula (Hann)
 §2 Monte-Carlo RMSE vs the Cramer-Rao bound (00/estimation-theory: var(w) >= 6/(rho N (N^2-1)))
 §3 zoom FFT (mix, decimate, FFT) equals the DTFT on the fine grid; resolution fs/(D N)
 §4 sliding DFT: equals direct DFT of the sliding window; damping r for stability
 §5 SNR estimation from a record: M2M4 moment estimator (QPSK) and spectral (in-band minus floor)
 §6 random-data OOK/ASK spectrum: carrier line + (A^2 T/4) sinc^2; dB-scale envelope; RBW vs nulls
Run: python3 tools/verify/s7_interbin_estimators.py   (≈ 15 s)
"""
import numpy as np
from scipy import signal

rng = np.random.default_rng(1402)
ok = True


def check(name, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")


def tone(N, k0, A=1.0, phi=0.0):
    n = np.arange(N)
    return A * np.exp(1j * (2 * np.pi * k0 * n / N + phi))


def three(X, k):
    N = len(X)
    return X[(k - 1) % N], X[k], X[(k + 1) % N]


def est_parabolic(X, k):
    a, b, c = (20 * np.log10(np.abs(v) + 1e-300) for v in three(X, k))
    return 0.5 * (a - c) / (a - 2 * b + c)


def est_jacobsen(X, k):
    a, b, c = three(X, k)
    return np.real((a - c) / (2 * b - a - c))


def est_candan(X, k):
    N = len(X)
    return np.tan(np.pi / N) / (np.pi / N) * est_jacobsen(X, k)


def est_quinn1(X, k):
    a, b, c = three(X, k)
    a1 = np.real(a / b)
    a2 = np.real(c / b)
    d1 = a1 / (1 - a1)
    d2 = -a2 / (1 - a2)
    return d2 if (d1 > 0 and d2 > 0) else d1


def tau(x):
    return 0.25 * np.log(3 * x ** 2 + 6 * x + 1) - np.sqrt(6) / 24 * np.log(
        (x + 1 - np.sqrt(2 / 3)) / (x + 1 + np.sqrt(2 / 3)))


def est_quinn2(X, k):
    """Quinn (1997) second estimator; dp from the k+1 neighbour, dm from the k-1 neighbour."""
    a, b, c = three(X, k)
    ap = np.real(c * np.conj(b)) / np.abs(b) ** 2
    am = np.real(a * np.conj(b)) / np.abs(b) ** 2
    dp = -ap / (1 - ap)
    dm = am / (1 - am)
    return (dp + dm) / 2 + tau(dp ** 2) - tau(dm ** 2)


def est_grandke_hann(X, k):
    a, b, c = (np.abs(v) for v in three(X, k))
    if c >= a:
        return (2 * c - b) / (b + c)
    return -(2 * a - b) / (a + b)


hann = signal.windows.hann  # periodic below
EST = {
    "parabolic dB (rect)": (est_parabolic, "rect"),
    "parabolic dB (Hann)": (est_parabolic, "hann"),
    "Jacobsen (rect)": (est_jacobsen, "rect"),
    "Candan (rect)": (est_candan, "rect"),
    "Quinn 1st (rect)": (est_quinn1, "rect"),
    "Quinn 2nd (rect)": (est_quinn2, "rect"),
    "Grandke (Hann)": (est_grandke_hann, "hann"),
}


def spectrum(x, win):
    N = len(x)
    w = np.ones(N) if win == "rect" else hann(N, sym=False)
    return np.fft.fft(x * w)


# ------------------------------------------------------------------ §1
print("§1 Noise-free bias (bins) vs true offset, N = 64, kc = 20")
N = 64
kc = 20
deltas = np.linspace(-0.45, 0.45, 19)
worst = {}
for name, (f, win) in EST.items():
    errs = []
    for d in deltas:
        X = spectrum(tone(N, kc + d, phi=0.3), win)
        k = int(np.argmax(np.abs(X)))
        errs.append(k + f(X, k) - (kc + d))
    worst[name] = np.max(np.abs(errs))
    print(f"  {name:22s}: max |bias| {worst[name]:.2e} bins")
check("Candan correction cuts Jacobsen bias > 3x (to < 1e-4 bin at N=64)", worst["Candan (rect)"] < min(1e-4, worst["Jacobsen (rect)"] / 3))
check("Quinn 1st/2nd unbiased to < 2e-2 bin (large-N approximation)", max(worst["Quinn 1st (rect)"], worst["Quinn 2nd (rect)"]) < 2e-2)
check("parabolic (rect) biased > 0.05 bin", worst["parabolic dB (rect)"] > 0.05)
check("parabolic on Hann much better than on rect", worst["parabolic dB (Hann)"] < worst["parabolic dB (rect)"] / 3)
check("Grandke Hann formula < 0.01 bin", worst["Grandke (Hann)"] < 0.01)

# ------------------------------------------------------------------ §2
print("§2 RMSE / sqrt(CRB) (random offset in +/-0.5 bin, random phase), N = 64")
trials = 4000
for snr_db in (0, 10, 20, 30):
    rho = 10 ** (snr_db / 10)
    crb_bins = np.sqrt(6 / (rho * N * (N ** 2 - 1))) * N / (2 * np.pi)
    se = {n_: [] for n_ in EST}
    for _ in range(trials):
        d = rng.uniform(-0.5, 0.5)
        x = tone(N, kc + d, phi=rng.uniform(0, 2 * np.pi)) + np.sqrt(1 / (2 * rho)) * (
            rng.standard_normal(N) + 1j * rng.standard_normal(N))
        Xr, Xh = spectrum(x, "rect"), spectrum(x, "hann")
        for name, (f, win) in EST.items():
            X = Xr if win == "rect" else Xh
            k = int(np.argmax(np.abs(X)))
            e = k + f(X, k) - (kc + d)
            e = (e + N / 2) % N - N / 2
            se[name].append(e ** 2)
    line = ", ".join(f"{n_.split(' (')[0][:9]}{'-H' if 'Hann' in n_ else ''} {np.sqrt(np.mean(v))/crb_bins:5.2f}" for n_, v in se.items())
    print(f"  SNR/sample {snr_db:2d} dB (CRB {crb_bins:.4f} bin): {line}")
    if snr_db == 20:
        r20 = {n_: np.sqrt(np.mean(v)) / crb_bins for n_, v in se.items()}
check("Quinn 2nd within 1.3x of CRB at 20 dB", r20["Quinn 2nd (rect)"] < 1.3)
check("Candan/Jacobsen within 1.6x of CRB at 20 dB", r20["Candan (rect)"] < 1.6)
check("parabolic (rect) bias-limited >> CRB at 20 dB", r20["parabolic dB (rect)"] > 5)

# ------------------------------------------------------------------ §3 zoom FFT
print("§3 Zoom FFT")
fs, Ntot = 1.0e6, 2 ** 19
D, Nz = 64, 4096
f0 = 125_000.0           # zoom centre
t = np.arange(Ntot) / fs
ftone = f0 + 37.3
x = np.exp(1j * 2 * np.pi * ftone * t)
y = x * np.exp(-1j * 2 * np.pi * f0 * t)
yd = signal.decimate(y, 8, ftype="fir", zero_phase=True)
yd = signal.decimate(yd, 8, ftype="fir", zero_phase=True)  # total D = 64
seg = yd[1000:1000 + Nz]
Z = np.fft.fftshift(np.fft.fft(seg * hann(Nz, sym=False)))
fz = (np.arange(Nz) - Nz / 2) * fs / D / Nz + f0
kz = np.argmax(np.abs(Z))
print(f"  D = {D}, Nz = {Nz}: bin {fs/D/Nz:.3f} Hz (a direct FFT needs N = {D*Nz} for the same bin); "
      f"peak at {fz[kz]:.2f} Hz (true {ftone:.2f})")
check("zoom FFT peak within one fine bin", abs(fz[kz] - ftone) <= fs / D / Nz)

# ------------------------------------------------------------------ §4 sliding DFT
print("§4 Sliding DFT  X_k[n] = e^{j2pi k/N} (X_k[n-1] + x[n] - x[n-N])")
N, k = 64, 5
x = rng.standard_normal(2000) + 1j * rng.standard_normal(2000)
tw = np.exp(1j * 2 * np.pi * k / N)
ek = np.exp(-1j * 2 * np.pi * k * np.arange(N) / N)
S, buf, err = 0j, np.zeros(N, complex), []
for n in range(len(x)):
    old = buf[n % N]
    buf[n % N] = x[n]
    S = tw * (S + x[n] - old)
    if n >= N - 1:
        err.append(abs(S - np.sum(x[n - N + 1:n + 1] * ek)))
print(f"  max |SDFT - direct DFT| over {len(err)} windows: {max(err):.2e}  (1 complex mult per sample per bin)")
check("SDFT equals direct DFT", max(err) < 1e-9)
r = 0.9999
z = r * tw
S, buf = np.complex64(0), np.zeros(N, np.complex64)
x32 = x.astype(np.complex64)
for n in range(len(x32)):
    old = buf[n % N]
    buf[n % N] = x32[n]
    S = np.complex64(z) * (S + x32[n] - np.complex64(r ** N) * old)
direct = np.sum(z ** (np.arange(N) + 1) * x[::-1][:N])
print(f"  damped SDFT (r = {r}, float32) vs its exact damped sum: |error| = {abs(S - direct):.2e} "
      f"(the undamped recursion has its pole on the unit circle and accumulates rounding error)")
check("damped float32 SDFT accurate", abs(S - direct) < 1e-3)

# ------------------------------------------------------------------ §5 SNR estimation
print("§5 SNR estimation from a record")
Ns = 4000
for snr_db in (-5, 0, 10, 20):
    rho = 10 ** (snr_db / 10)
    est = []
    for _ in range(300):
        s = (rng.choice([-1, 1], Ns) + 1j * rng.choice([-1, 1], Ns)) / np.sqrt(2)
        nse = np.sqrt(1 / (2 * rho)) * (rng.standard_normal(Ns) + 1j * rng.standard_normal(Ns))
        y = s + nse
        M2 = np.mean(np.abs(y) ** 2)
        M4 = np.mean(np.abs(y) ** 4)
        Shat = np.sqrt(max(2 * M2 ** 2 - M4, 1e-12))
        est.append(10 * np.log10(Shat / max(M2 - Shat, 1e-12)))
    est = np.array(est)
    print(f"  M2M4, QPSK, {Ns} symbols, true {snr_db:3d} dB: mean {est.mean():6.2f} dB, std {est.std():.2f} dB")
    if snr_db == 10:
        m2m4_10 = est.mean()
check("M2M4 unbiased within 0.2 dB at 10 dB", abs(m2m4_10 - 10) < 0.2)
# spectral method: oversampled RRC-like signal occupying |f| < 0.25 fs; noise floor from |f| > 0.35 fs
fsym, osr = 1.0, 4
nsym = 20000
sym = (rng.choice([-1, 1], nsym) + 1j * rng.choice([-1, 1], nsym)) / np.sqrt(2)
up = np.zeros(nsym * osr, complex)
up[::osr] = sym
hrrc = signal.firwin(129, 0.27, window=("kaiser", 8))  # band-limiting filter, |f| < ~0.135 fs (normalised to Nyquist)
sig = np.convolve(up, hrrc, "same")
sig /= np.sqrt(np.mean(np.abs(sig) ** 2))
true_snr_db = 3.0   # SNR in the full sampled band fs
rho = 10 ** (true_snr_db / 10)
y = sig + np.sqrt(1 / (2 * rho)) * (rng.standard_normal(len(sig)) + 1j * rng.standard_normal(len(sig)))
f, P = signal.welch(y, fs=1.0, window="hann", nperseg=1024, return_onesided=False, scaling="density")
f = np.fft.fftshift(f)
P = np.fft.fftshift(P)
df = f[1] - f[0]
inb = np.abs(f) < 0.15
oob = np.abs(f) > 0.25
N0 = np.median(P[oob])
Ptot_in = np.sum(P[inb]) * df
S_est = Ptot_in - N0 * np.sum(inb) * df
snr_full = 10 * np.log10(S_est / (N0 * 1.0))
snr_inband_true = true_snr_db + 10 * np.log10(1.0 / (np.sum(inb) * df))
print(f"  spectral method: signal = in-band power - N0*B_in, N0 from out-of-band median; "
      f"SNR in fs: est {snr_full:.2f} dB (true {true_snr_db:.2f}); in {np.sum(inb)*df:.3f} fs band: "
      f"{10*np.log10(S_est/(N0*np.sum(inb)*df)):.2f} dB (true {snr_inband_true:.2f})")
check("spectral SNR estimate within 0.3 dB", abs(snr_full - true_snr_db) < 0.3)

# ------------------------------------------------------------------ §6 OOK spectrum
print("§6 Random-data OOK (unipolar NRZ) spectrum")
osr = 16
nb = 200000
bits = rng.integers(0, 2, nb).astype(float)
a = np.repeat(bits, osr)                     # amplitude 0/1, T = osr samples
f, P = signal.welch(a, fs=osr, window="hann", nperseg=4096, return_onesided=False, scaling="density",
                    detrend=False)
f = np.fft.fftshift(f)                       # f in units of the bit rate R_b
P = np.fft.fftshift(P)
dc = np.argmin(np.abs(f))
cont_th = lambda ff: 0.25 * np.sinc(ff) ** 2 * (1.0)   # (A^2 T /4) sinc^2(fT), T=1 in bit-rate units
# total power check: carrier line holds A^2/4 = 0.25, continuum 0.25
line_pow = (P[dc - 3:dc + 4].sum() - cont_th(0) * 7) * (f[1] - f[0])
cont_pow = np.sum(P) * (f[1] - f[0]) - line_pow
print(f"  carrier line power {line_pow:.3f} (theory A^2/4 = 0.250), continuum {cont_pow:.3f} (0.250 incl. aliasing)")
check("half the OOK power is in the carrier line", abs(line_pow - 0.25) < 0.02)
for ff in (0.25, 0.5, 1.5, 2.5, 4.5):
    i = np.argmin(np.abs(f - ff))
    print(f"  f = {ff:4.2f} R_b: measured {10*np.log10(P[i]):7.2f} dB/Hz·R_b, theory {10*np.log10(cont_th(ff)):7.2f}")
i = np.argmin(np.abs(f - 1.5))
check("continuum matches (A^2T/4)sinc^2 at 1.5 R_b within 0.5 dB", abs(10 * np.log10(P[i] / cont_th(1.5))) < 0.5)
# smoothed (RBW >> R_b... or averaged over sidelobes) envelope: sidelobe-average 1/(2 pi^2 f^2) * 0.25
for ff in (1, 2, 4, 8):
    env = 0.25 / (2 * np.pi ** 2 * ff ** 2)
    print(f"  smoothed sidelobe envelope at {ff} R_b: {10*np.log10(env/0.25):6.1f} dB rel. continuum peak "
          f"(-20 dB/decade, -6 dB/octave)")
# RBW wider than R_b fills the nulls
fw, Pw = signal.welch(a, fs=osr, window="hann", nperseg=16, return_onesided=False, scaling="density", detrend=False)
fw, Pw = np.fft.fftshift(fw), np.fft.fftshift(Pw)
i1 = np.argmin(np.abs(fw - 1.0))
print(f"  null at f = R_b: with fine RBW {10*np.log10(P[np.argmin(np.abs(f-1.0))]/0.25):.1f} dB; "
      f"with RBW = {1.5*osr/16:.1f} R_b (16-pt Hann) {10*np.log10(Pw[i1]/0.25):.1f} dB rel. peak — null filled")
check("coarse RBW fills the first null (> -15 dB)", 10 * np.log10(Pw[i1] / 0.25) > -15)

print("\nALL PASS" if ok else "\nSOME FAILED")
