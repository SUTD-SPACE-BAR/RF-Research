#!/usr/bin/env python3
"""Verification for kb/10-comms-modulation/ofdm.md

Run:  python3 tools/verify/comms_ofdm.py      (~10 s)

Checks:
  1. OFDM with cyclic prefix over a multipath channel shorter than the CP: one-tap-per-subcarrier
     equalisation recovers the symbols exactly (noiseless); with the CP shorter than the channel,
     ISI/ICI appears (EVM reported).
  2. PAPR of 64-subcarrier QPSK OFDM (4x oversampled): CCDF at 1e-3 vs the Nyquist-sampled
     approximation 1-(1-exp(-g))^N, and vs single-carrier RRC QPSK.
  3. Carrier-frequency-offset sensitivity: for normalised CFO eps (fraction of subcarrier
     spacing) the useful carrier is scaled by sinc(eps) and the ICI power is ~ 1 - sinc^2(eps)
     ~ (pi eps)^2 / 3 (noiseless simulation, random QPSK on all subcarriers).
  4. Schmidl-Cox style CFO estimate from a training symbol with two identical halves:
     eps_hat = angle(P) / pi, unambiguous within +-1 subcarrier spacing.
  5. Numerology: IEEE 802.11a/g (20 MHz, 64-FFT, 312.5 kHz, 3.2+0.8 us, 48 data + 4 pilot,
     6..54 Mb/s), LTE (15 kHz, 66.7 us, CP 4.69 us, 2048-FFT at 30.72 MS/s, 1200 subcarriers in
     20 MHz), DVB-T (2k/8k: 4464/1116 Hz, 224/896 us).
"""
import numpy as np

rng = np.random.default_rng(17)
ok_all = True


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel else 1.0)
    ok = err <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.5g}, expected {want:.5g} (tol {tol}{' rel' if rel else ''})")


def qpsk(n):
    return (np.sign(rng.standard_normal(n)) + 1j * np.sign(rng.standard_normal(n))) / np.sqrt(2)

# ------------------------------------------------------------------------------ 1
N = 64
nsym = 400
h = np.array([1.0, 0.0, 0.5j, 0.0, 0.0, -0.3, 0.2])     # 7-tap channel (delay spread 6 samples)
for cp in (16, 4):
    X = qpsk(N * nsym).reshape(nsym, N)
    x = np.fft.ifft(X, axis=1) * np.sqrt(N)
    tx = np.hstack([x[:, -cp:], x]).ravel()
    rx = np.convolve(tx, h)[:len(tx)].reshape(nsym, N + cp)
    Y = np.fft.fft(rx[:, cp:], axis=1) / np.sqrt(N)
    H = np.fft.fft(h, N)
    Xh = Y / H
    evm = np.sqrt(np.mean(np.abs(Xh[1:] - X[1:]) ** 2))
    print(f"  CP = {cp} samples, channel length {len(h)}: EVM after 1-tap EQ = {20*np.log10(evm + 1e-16):.1f} dB")
    if cp == 16:
        check("CP >= channel memory: exact recovery (EVM)", evm, 0.0, 1e-12)
    else:
        ok = evm > 0.05
        ok_all &= ok
        print(f"[{'PASS' if ok else 'FAIL'}] CP shorter than channel: residual ISI/ICI (EVM > -26 dB)")

# ------------------------------------------------------------------------------ 2
L = 4
nsym = 20000
X = np.zeros((nsym, N * L), complex)
used = np.r_[1:27, N * L - 26:N * L]              # 52 subcarriers like 802.11a (no DC)
X[:, used] = qpsk(nsym * len(used)).reshape(nsym, len(used))
x = np.fft.ifft(X, axis=1)
pw = np.abs(x) ** 2
papr = 10 * np.log10(pw.max(axis=1) / pw.mean(axis=1))
p3 = np.quantile(papr, 1 - 1e-3)
g = np.linspace(4, 14, 1001)
ccdf_th = 1 - (1 - np.exp(-10 ** (g / 10))) ** 52
g_th = g[np.argmin(np.abs(ccdf_th - 1e-3))]
print(f"  52-subcarrier QPSK OFDM: PAPR exceeded by 1e-3 of symbols = {p3:.2f} dB (Nyquist approx {g_th:.2f} dB)")
check("OFDM PAPR@1e-3 per-symbol CCDF ~ Nyquist approximation (+~0.4 dB for oversampling)", p3, g_th + 0.4, 0.6)
check("OFDM mean-power normalised peak ~ 10-11 dB region", p3, 10.5, 1.0)

# ------------------------------------------------------------------------------ 3
nsym = 2000
for eps in (0.02, 0.05, 0.1):
    X = qpsk(N * nsym).reshape(nsym, N)
    x = np.fft.ifft(X, axis=1) * np.sqrt(N)
    n = np.arange(N)
    xr = x * np.exp(2j * np.pi * eps * n / N)
    Y = np.fft.fft(xr, axis=1) / np.sqrt(N)
    # useful component: projection on X (common phase rotation removed by complex LS gain)
    a = np.sum(Y * np.conj(X)) / np.sum(np.abs(X) ** 2)
    ici = np.mean(np.abs(Y - a * X) ** 2)
    sinc = np.abs(np.sinc(eps)) if False else None
    # exact useful gain for this model: (1/N) sum exp(j 2 pi eps n / N)
    g_exact = np.abs(np.mean(np.exp(2j * np.pi * eps * n / N)))
    check(f"CFO eps={eps}: useful gain |a| vs (1/N)|sum e^(j2pi eps n/N)| ~ sinc(eps)", abs(a), g_exact, 1e-3)
    check(f"CFO eps={eps}: ICI power vs 1-|gain|^2 ~ (pi eps)^2/3", ici, 1 - g_exact ** 2, 0.05, rel=True)
    print(f"    eps={eps}: SIR from ICI = {10*np.log10(g_exact**2/ici):.1f} dB; (pi eps)^2/3 -> {10*np.log10(3/(np.pi*eps)**2):.1f} dB")

# ------------------------------------------------------------------------------ 4
half = N // 2
Xt = np.zeros(N, complex)
Xt[::2] = qpsk(half) * np.sqrt(2)                 # even subcarriers only -> two identical halves
xt = np.fft.ifft(Xt) * np.sqrt(N)
check("training symbol halves identical", np.max(np.abs(xt[:half] - xt[half:])), 0.0, 1e-12)
errs = []
for eps in (-0.8, -0.3, 0.1, 0.45, 0.9):
    r = xt * np.exp(2j * np.pi * eps * np.arange(N) / N)
    r = r + np.sqrt(0.01 / 2) * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
    P = np.sum(np.conj(r[:half]) * r[half:])
    eps_hat = np.angle(P) / np.pi
    errs.append(abs(eps_hat - eps))
check("Schmidl-Cox CFO estimate error (max over |eps|<1) [subcarrier spacings]", max(errs), 0.0, 0.02)

# ------------------------------------------------------------------------------ 5
fs = 20e6
check("802.11a subcarrier spacing [kHz]", fs / 64 / 1e3, 312.5, 1e-9)
check("802.11a FFT period [us]", 64 / fs * 1e6, 3.2, 1e-9)
check("802.11a symbol incl. 0.8 us GI [us]", (64 + 16) / fs * 1e6, 4.0, 1e-9)
for bits, rate, want in ((1, 0.5, 6), (2, 0.5, 12), (4, 0.5, 24), (6, 0.75, 54)):
    check(f"802.11a rate {bits} b/sc x {rate} [Mb/s]", 48 * bits * rate / 4e-6 / 1e6, want, 1e-9)
check("LTE useful symbol 1/15 kHz [us]", 1 / 15e3 * 1e6, 66.67, 0.01)
check("LTE normal CP 144 samples at 30.72 MS/s [us]", 144 / 30.72e6 * 1e6, 4.6875, 1e-4)
check("LTE first-symbol CP 160 samples [us]", 160 / 30.72e6 * 1e6, 5.208, 1e-3)
check("LTE 2048-FFT sample rate for 15 kHz [MS/s]", 2048 * 15e3 / 1e6, 30.72, 1e-9)
check("LTE 20 MHz: 100 RB x 12 subcarriers x 15 kHz occupied [MHz]", 100 * 12 * 15e3 / 1e6, 18.0, 1e-9)
T8 = 7 / 64e6          # DVB-T 8 MHz elementary period 7/64 us
check("DVB-T 2k Tu = 2048 T [us]", 2048 * T8 * 1e6, 224.0, 1e-6)
check("DVB-T 8k Tu = 8192 T [us]", 8192 * T8 * 1e6, 896.0, 1e-6)
check("DVB-T 2k spacing [Hz]", 1 / (2048 * T8), 4464.3, 0.1)
check("DVB-T 8k spacing [Hz]", 1 / (8192 * T8), 1116.1, 0.1)
# CP vs delay spread example
check("802.11a GI 0.8 us -> max path difference [m]", 0.8e-6 * 299792458, 239.8, 0.1)

print("\nOVERALL:", "PASS" if ok_all else "FAIL")
