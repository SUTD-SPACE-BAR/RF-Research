#!/usr/bin/env python3
"""Verification for kb/11-radar/ambiguity-function-waveforms.md

Run:  python3 tools/verify/radar_ambiguity.py      (~20 s)

Convention (Levanon & Mozeson): chi(tau, nu) = int s(t) s*(t - tau) exp(j 2 pi nu t) dt,
energy E = int |s|^2 dt, so |chi(0,0)| = E.

Checks:
  1. Numerical AF of a rectangular pulse vs closed form |(T-|tau|) sinc(nu (T-|tau|))|.
  2. LFM: closed form |(T-|tau|) sinc((nu + mu tau)(T-|tau|))| (ridge nu = -mu tau in this convention).
  3. Properties: max at origin; volume invariance int int |chi|^2 dtau dnu = E^2 for rect, LFM,
     Barker-13 and a Costas-6 waveform; symmetry |chi(-tau,-nu)| = |chi(tau,nu)|.
  4. Coherent pulse train (N pulses, PRI): "bed of nails" -- peaks at tau = k PRI, nu = m/PRI;
     Doppler resolution 1/(N PRI) of the train vs 1/T of one pulse.
  5. Costas (Welch construction p=7): thumbtack -- off-origin peak <= ~1/N of the origin
     (for chip-grid points) ; Barker-13 Doppler sensitivity visible in AF.
  6. Delay-estimation accuracy: Monte-Carlo std of the matched-filter peak position (LFM, TB=100)
     vs the Cramer-Rao bound sigma_tau = 1 / (2 pi B_rms sqrt(2 SNR)),
     SNR = |a|^2 sum|s|^2 / sigma^2 (complex-baseband matched-filter output SNR), B_rms = B/sqrt(12).
"""
import numpy as np

ok_all = True


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel else 1.0)
    ok = err <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol}{' rel' if rel else ''})")
    return ok


def af(s, fs, taus_idx, nfft):
    """Return chi[tau_i, nu_k] (complex) for integer-sample delays; nu grid = fftfreq(nfft, 1/fs)."""
    L = len(s)
    out = np.zeros((len(taus_idx), nfft), complex)
    for i, k in enumerate(taus_idx):
        prod = np.zeros(L, complex)
        if k >= 0:
            prod[k:] = s[k:] * np.conj(s[:L - k])
        else:
            prod[:L + k] = s[:L + k] * np.conj(s[-k:])
        # chi(tau, nu) = sum prod[n] exp(+j2 pi nu n/fs)/fs  -> use ifft * nfft
        out[i] = np.fft.ifft(prod, nfft) * nfft / fs
    nu = np.fft.fftfreq(nfft, 1 / fs)
    return out, nu


print("=" * 78)
print("1-2. Closed forms: rect pulse and LFM")
T = 1e-6
fs = 64e6
L = int(T * fs)
t = np.arange(L) / fs
rect = np.ones(L, complex)
B = 20e6
mu = B / T
lfm = np.exp(1j * np.pi * mu * (t - T / 2) ** 2)
taus = np.array([0, 5, 16, 32])
nfft = 8192
for name, s, closed in (
        ("rect", rect, lambda tau, nu: np.abs((T - abs(tau)) * np.sinc(nu * (T - abs(tau))))),
        ("LFM", lfm, lambda tau, nu: np.abs((T - abs(tau)) * np.sinc((nu + mu * tau) * (T - abs(tau)))))):
    A, nu = af(s, fs, taus, nfft)
    errs = []
    for i, k in enumerate(taus):
        tau = k / fs
        sel = np.abs(nu) < 30e6
        num = np.abs(A[i, sel])
        th = closed(tau, nu[sel])
        errs.append(np.max(np.abs(num - th)) / T)
    check(f"{name}: numerical AF vs closed form (max err / T)", max(errs), 0.0, 0.02)
# LFM ridge location at tau = 16 samples
A, nu = af(lfm, fs, [16], nfft)
nu_pk = nu[np.argmax(np.abs(A[0]))]
check("LFM ridge: peak Doppler at tau equals -mu*tau (this convention)", nu_pk, -mu * 16 / fs, fs / nfft * 1.5)

print("=" * 78)
print("3. Properties: max at origin, volume invariance, symmetry")


def volume(s, fs, nfft=4096):
    L = len(s)
    ks = np.arange(-(L - 1), L)
    A, nu = af(s, fs, ks, nfft)
    dt = 1 / fs
    dnu = fs / nfft
    vol = np.sum(np.abs(A) ** 2) * dt * dnu
    E = np.sum(np.abs(s) ** 2) / fs
    return vol, E, A, ks, nu


barker13 = np.array([1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1], complex)
osr = 8
# Costas via Welch: p = 7, primitive root 3 -> a_i = 3^i mod 7, i = 0..5 -> values 1..6
p, g = 7, 3
costas = [pow(g, i, p) for i in range(p - 1)]
Nc = len(costas)
tc = 1e-7
fs_c = 16 * Nc / tc / Nc * 4
nper = int(tc * fs_c)
cost_sig = np.concatenate([np.exp(2j * np.pi * (costas[i] / tc) * np.arange(nper) / fs_c) for i in range(Nc)])
sigs = {
    "rect": (rect[::4], fs / 4),
    "LFM": (lfm[::2], fs / 2),
    "Barker-13": (np.repeat(barker13, osr), 8 / 1e-7),
    "Costas-6": (cost_sig, fs_c),
}
store = {}
for name, (s, f) in sigs.items():
    vol, E, A, ks, nu = volume(s, f)
    store[name] = (A, ks, nu, E, f)
    check(f"{name}: volume / E^2 = 1", vol / E ** 2, 1.0, 1e-6)
    mx = np.abs(A).max()
    check(f"{name}: max |chi| at origin equals E", mx / E, 1.0, 1e-9)
    # symmetry |chi(-tau,-nu)| = |chi(tau,nu)|: row -k, column -nu
    i0 = len(ks) // 2
    k = min(5, i0)
    row_p = np.abs(A[i0 + k])
    row_m = np.abs(A[i0 - k])
    row_m_flip = np.roll(row_m[::-1], 1)          # nu -> -nu on fftfreq grid
    check(f"{name}: symmetry |chi(-tau,-nu)| = |chi(tau,nu)|", np.max(np.abs(row_p - row_m_flip)) / E, 0.0, 1e-9)

print("=" * 78)
print("4. Coherent pulse train: bed of nails")
Np = 8
PRI = 4e-6
fs_t = 16e6
tp = 1e-6
Lp = int(tp * fs_t)
Lpri = int(PRI * fs_t)
train = np.zeros(Np * Lpri, complex)
for i in range(Np):
    train[i * Lpri:i * Lpri + Lp] = 1.0
nfft_t = 1 << 16
A0, nu_t = af(train, fs_t, [0, Lpri, 2 * Lpri], nfft_t)
E_t = np.sum(np.abs(train) ** 2) / fs_t
# zero-delay cut: peaks at m / PRI with width 1/(Np PRI)
cut = np.abs(A0[0])
sel = (nu_t > 0.5 / PRI) & (nu_t < 1.5 / PRI)
nu_pk = nu_t[sel][np.argmax(cut[sel])]
check("pulse train: Doppler ambiguity at 1/PRI", nu_pk, 1 / PRI, fs_t / nfft_t * 2)
# -4 dB null-to-null-ish: first null of main Doppler lobe at 1/(Np PRI)
selm = (nu_t >= 0) & (nu_t < 0.5 / PRI)
c0 = cut[selm]
first_null = nu_t[selm][np.argmax(np.diff(c0) > 0)]
check("pulse train: first Doppler null at 1/(N PRI)", first_null, 1 / (Np * PRI), 0.1 / (Np * PRI))
check("pulse train: delay ambiguity peak at PRI has height (N-1)/N", np.abs(A0[1]).max() / E_t, (Np - 1) / Np, 1e-6)
print(f"    single pulse Doppler resolution ~1/T = {1/tp/1e3:.0f} kHz; train of {Np} pulses ~1/(N PRI) = {1/(Np*PRI)/1e3:.2f} kHz")

print("=" * 78)
print("5. Costas thumbtack and Barker Doppler sensitivity")
A, ks, nu, E, f = store["Costas-6"]
# sample chip-grid points: tau = m tc, nu = n / tc, (m,n) != (0,0)
peaks = []
for m in range(-(Nc - 1), Nc):
    kk = int(round(m * tc * f))
    i = np.where(ks == kk)[0]
    if len(i) == 0:
        continue
    for n in range(-(Nc - 1), Nc):
        if m == 0 and n == 0:
            continue
        j = np.argmin(np.abs(nu - n / tc))
        peaks.append(np.abs(A[i[0], j]) / E)
check("Costas-6: max |chi| at off-origin chip-grid points <= 1/N (+tol)", max(peaks), 1 / Nc, 0.02)
diffs = set()
okc = True
for d in range(1, Nc):
    v = [costas[i + d] - costas[i] for i in range(Nc - d)]
    okc &= len(v) == len(set(v))
check("Costas-6 (Welch p=7): distinct-difference property", float(okc), 1.0, 0)
A, ks, nu, E, f = store["Barker-13"]
i0 = len(ks) // 2
T13 = 13 * 1e-7
for fdT in (0.5, 1.0):
    j = np.argmin(np.abs(nu - fdT / T13))
    print(f"    Barker-13 zero-delay AF at fd*T = {fdT}: {20*np.log10(np.abs(A[i0, j])/E):.2f} dB (sinc-like: rect envelope)")

print("=" * 78)
print("6. Delay-estimation accuracy vs Cramer-Rao bound (LFM TB=100)")
rng = np.random.default_rng(12)
B = 10e6
T = 10e-6
fs = 4 * B
Ls = int(T * fs)
tt = np.arange(Ls) / fs
s = np.exp(1j * np.pi * (B / T) * (tt - T / 2) ** 2)
Nfft = 4096
S = np.fft.fft(s, Nfft)
f_ax = np.fft.fftfreq(Nfft, 1 / fs)
Brms = np.sqrt(np.sum(f_ax ** 2 * np.abs(S) ** 2) / np.sum(np.abs(S) ** 2))
print(f"    measured B_rms = {Brms/1e6:.3f} MHz (B/sqrt12 = {B/np.sqrt(12)/1e6:.3f} MHz)")
up = 64
for snr_db in (20.0, 30.0):
    snr = 10 ** (snr_db / 10)
    sigma2 = np.sum(np.abs(s) ** 2) / snr          # |a|=1
    est = []
    tau0 = 0.3 / fs
    X0 = S * np.exp(-2j * np.pi * f_ax * tau0)     # fractional delay
    for trial in range(400):
        w = (rng.standard_normal(Nfft) + 1j * rng.standard_normal(Nfft)) * np.sqrt(sigma2 / 2)
        X = X0 * np.exp(1j * rng.uniform(0, 2 * np.pi)) + np.fft.fft(w)
        # cross-correlation, upsampled by zero-padding in the frequency domain
        C = X * np.conj(S)
        Cz = np.zeros(Nfft * up, complex)
        h = Nfft // 2
        Cz[:h] = C[:h]
        Cz[-h:] = C[-h:]
        r = np.abs(np.fft.ifft(Cz))
        k = np.argmax(r[: up * 8])  # search near zero lag
        # parabolic refinement
        y0, y1, y2 = r[k - 1], r[k], r[k + 1]
        dk = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
        est.append((k + dk) / (fs * up))
    std = np.std(est)
    crlb = 1 / (2 * np.pi * Brms * np.sqrt(2 * snr))
    print(f"    SNR {snr_db:.0f} dB: MC std = {std*1e9:.3f} ns, CRLB = {crlb*1e9:.3f} ns, ratio {std/crlb:.2f}; "
          f"range: {std*3e8/2*100:.2f} cm vs resolution c/2B = {3e8/2/B:.1f} m")
    check(f"delay std within 25% of CRLB at {snr_db:.0f} dB", std / crlb, 1.0, 0.25)

print("=" * 78)
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
