#!/usr/bin/env python3
"""Verification for kb/14-sdr-dsp/iq-complex-baseband.md

Checks (PASS/FAIL):
 1. Real cosine -> two spectral lines; complex exponential -> one line.
 2. Quadrature downconversion: real RF at fc+fm -> complex baseband tone at +fm
    (and fc-fm -> -fm): the sign of frequency survives only with I AND Q.
 3. IQ upconversion: Re{x_bb e^{j w_c t}} = I cos - Q sin reproduces the RF.
 4. IQ-imbalance image rejection ratio (IRR) closed form vs simulation.
 5. Small-error approximation IRR ~ 4/(eps^2 + phi^2).
 6. Gram-Schmidt (Churchill 1981) blind IQ correction raises IRR.
 7. DC blocker y[n]=x[n]-x[n-1]+a*y[n-1]: -3 dB notch half-width ~ (1-a) fs / (2 pi).
 8. Offset tuning: DC spike moved out of the channel and removed by the channel filter.
 9. Analytic signal (Hilbert) suppresses negative frequencies; envelope of AM.
10. Oscillator ppm -> Hz offsets at 433.92 MHz / 915 MHz / 1575.42 MHz.
"""
import numpy as np
from scipy import signal

rng = np.random.default_rng(7)
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def peak_bins(x, fs, thresh_db=-40):
    N = len(x)
    X = np.fft.fftshift(np.fft.fft(x * np.blackman(N)))
    f = (np.arange(N) - N // 2) * fs / N
    mag = 20 * np.log10(np.abs(X) / np.abs(X).max() + 1e-300)
    # local maxima above threshold
    idx = [i for i in range(1, N - 1) if mag[i] > thresh_db and mag[i] >= mag[i - 1] and mag[i] >= mag[i + 1]]
    return f[idx], mag[idx]


fs = 1e6
N = 4096
n = np.arange(N)
f0 = 100e3 + 0.37 * fs / N
# 1 ---------------------------------------------------------------
pr, _ = peak_bins(np.cos(2 * np.pi * f0 * n / fs), fs)
pc, _ = peak_bins(np.exp(2j * np.pi * f0 * n / fs), fs)
check("real cosine has lines at +/-f0", len(pr) == 2 and np.allclose(sorted(np.abs(pr)), [f0, f0], atol=fs / N))
check("complex exponential has one line at +f0", len(pc) == 1 and abs(pc[0] - f0) < fs / N)

# 2 --------------------------------------------------------------- quadrature downconversion
fsim = 100e6  # "analog" simulation rate
fc = 20e6
fm = 150e3
t = np.arange(2 ** 17) / fsim
lp = signal.firwin(801, 1e6, fs=fsim)
for sgn in (+1, -1):
    rf = np.cos(2 * np.pi * (fc + sgn * fm) * t)
    i = signal.lfilter(lp, 1, rf * 2 * np.cos(2 * np.pi * fc * t))
    q = signal.lfilter(lp, 1, rf * -2 * np.sin(2 * np.pi * fc * t))
    bb = (i + 1j * q)[2000::25]  # decimate to 4 MS/s
    p, _ = peak_bins(bb, fsim / 25, -30)
    check(f"downconvert fc{'+' if sgn>0 else '-'}fm -> {'+' if sgn>0 else '-'}fm", len(p) == 1 and abs(p[0] - sgn * fm) < 2 * (fsim / 25) / len(bb),
          f"peak at {p[0]/1e3:.1f} kHz")
    # with I only (real mixing) both signs map to both +/-fm: ambiguity
    pi_, _ = peak_bins(i[2000::25].astype(complex), fsim / 25, -30)
    if sgn > 0:
        check("I-only (real) mixing cannot tell +fm from -fm", len(pi_) == 2)

# 3 --------------------------------------------------------------- upconversion identity
I = rng.standard_normal(1000)
Q = rng.standard_normal(1000)
tt = np.arange(1000) / fsim
wc = 2 * np.pi * fc
rf1 = np.real((I + 1j * Q) * np.exp(1j * wc * tt))
rf2 = I * np.cos(wc * tt) - Q * np.sin(wc * tt)
check("Re{(I+jQ)e^{jwt}} = I cos - Q sin", np.allclose(rf1, rf2))


# 4 --------------------------------------------------------------- IQ imbalance IRR
def irr_formula(g, phi):
    return (1 + 2 * g * np.cos(phi) + g ** 2) / (1 - 2 * g * np.cos(phi) + g ** 2)


def apply_imbalance(x, g, phi):
    """Receiver IQ imbalance: I branch ideal, Q branch gain g and phase error phi."""
    return np.real(x) + 1j * g * (np.sin(phi) * np.real(x) + np.cos(phi) * np.imag(x))


def measure_irr(y, fs, ftone):
    N = len(y)
    Y = np.fft.fft(y * np.blackman(N))
    k = int(round(ftone / fs * N))
    return np.abs(Y[k]) ** 2 / np.abs(Y[-k]) ** 2


fs = 1e6
N = 2 ** 14
nn = np.arange(N)
ftone = 1024 * fs / N  # bin-centred
x = np.exp(2j * np.pi * ftone * nn / fs)
for gdb, phdeg in [(0.1, 1.0), (0.5, 2.0), (1.0, 5.0), (0.05, 0.5)]:
    g = 10 ** (gdb / 20)
    ph = np.deg2rad(phdeg)
    y = apply_imbalance(x, g, ph)
    m = 10 * np.log10(measure_irr(y, fs, ftone))
    th = 10 * np.log10(irr_formula(g, ph))
    approx = 10 * np.log10(4 / ((g - 1) ** 2 + ph ** 2))
    check(f"IRR {gdb} dB / {phdeg} deg", abs(m - th) < 0.1, f"sim {m:.2f} dB, formula {th:.2f} dB, 4/(e^2+phi^2) {approx:.2f} dB")

# 5 small-error approx checked above within table; explicit:
g = 10 ** (0.1 / 20)
ph = np.deg2rad(1)
check("small-error approx within 0.1 dB at 0.1 dB/1 deg",
      abs(10 * np.log10(irr_formula(g, ph)) - 10 * np.log10(4 / ((g - 1) ** 2 + ph ** 2))) < 0.1)


# 6 --------------------------------------------------------------- Gram-Schmidt correction
def gram_schmidt_iq(y):
    i = np.real(y) - np.mean(np.real(y))
    q = np.imag(y) - np.mean(np.imag(y))
    q_orth = q - (np.mean(i * q) / np.mean(i * i)) * i  # remove I-correlated part (phase error)
    q_orth *= np.sqrt(np.mean(i * i) / np.mean(q_orth * q_orth))  # equalise power (gain error)
    return i + 1j * q_orth


# a "busy" wideband signal (circular noise band) plus a test tone, with imbalance and noise.
# The estimator's residual error ~ 1/sqrt(N), so achievable IRR grows ~10 log10(N).
g = 10 ** (0.5 / 20)
ph = np.deg2rad(3)
res = []
for NN in (2 ** 14, 2 ** 18):
    nn2 = np.arange(NN)
    ft2 = (NN // 16) * fs / NN
    x2 = np.exp(2j * np.pi * ft2 * nn2 / fs)
    wb = signal.lfilter(signal.firwin(129, 0.3), 1, rng.standard_normal(NN) + 1j * rng.standard_normal(NN))
    sig = wb / np.std(wb) * 0.3 + x2
    y = apply_imbalance(sig, g, ph) + 0.001 * (rng.standard_normal(NN) + 1j * rng.standard_normal(NN))
    before = 10 * np.log10(measure_irr(y, fs, ft2))
    after = 10 * np.log10(measure_irr(gram_schmidt_iq(y), fs, ft2))
    res.append((NN, before, after))
    print(f"      N={NN}: IRR {before:.1f} dB -> {after:.1f} dB after Gram-Schmidt")
check("Gram-Schmidt IQ correction improves IRR by >15 dB", all(a > b + 15 for _, b, a in res))
check("residual improves with averaging length (estimation-limited)", res[1][2] > res[0][2] + 6)

# 7 --------------------------------------------------------------- DC blocker
fs = 2.4e6
for a in (0.999, 0.9999):
    w, h = signal.freqz([1, -1], [1, -a], worN=2 ** 20, fs=fs)
    f3 = w[np.argmax(np.abs(h) >= 1 / np.sqrt(2))]
    pred = (1 - a) * fs / (2 * np.pi)
    check(f"DC blocker a={a}: -3 dB at (1-a)fs/2pi", abs(f3 - pred) / pred < 0.02, f"{f3:.1f} Hz vs {pred:.1f} Hz")

# 8 --------------------------------------------------------------- offset tuning
fs = 2.0e6
N = 2 ** 16
nn = np.arange(N)
f_sig = 433.92e6
f_tune = 433.92e6 - 400e3  # tune 400 kHz low
f_off = f_sig - f_tune  # channel appears at +400 kHz
bw = 125e3
chan = signal.lfilter(signal.firwin(255, bw / 2, fs=fs), 1, rng.standard_normal(N) + 1j * rng.standard_normal(N))
chan *= np.exp(2j * np.pi * f_off * nn / fs)
chan /= np.std(chan)
dc = 3.0 * (1 + 0.5j)  # big LO-leakage spike at 0 Hz
y = chan + dc
shifted = y * np.exp(-2j * np.pi * f_off * nn / fs)  # move channel to 0 Hz, DC spike now at -400 kHz
h = signal.firwin(255, 80e3, fs=fs)
filt = signal.lfilter(h, 1, shifted)[400:]
residual_dc = np.abs(np.mean(filt * np.exp(2j * np.pi * f_off * np.arange(400, N) / fs)))
chan_ref = signal.lfilter(h, 1, chan * np.exp(-2j * np.pi * f_off * nn / fs))[400:]
err = np.std(filt - chan_ref) / np.std(chan_ref)
check("offset tuning: spike falls in stopband, removed by channel filter", err < 0.01 and residual_dc < 0.01 * abs(dc),
      f"residual spike {20*np.log10(residual_dc/abs(dc)):.1f} dB rel. original; channel error {err:.2e}")

# 9 --------------------------------------------------------------- analytic signal
fs = 1e6
N = 2 ** 14
nn = np.arange(N)
fcar = 200e3
m = 0.5 * np.cos(2 * np.pi * 1e3 * nn / fs)
am = (1 + m) * np.cos(2 * np.pi * fcar * nn / fs)
za = signal.hilbert(am)
Z = np.abs(np.fft.fft(za))
neg = np.sum(Z[N // 2 + 1:] ** 2) / np.sum(Z ** 2)
check("analytic signal has no negative-frequency content", neg < 1e-6, f"neg-freq energy fraction {neg:.1e}")
env_err = np.max(np.abs(np.abs(za)[500:-500] - (1 + m)[500:-500]))
check("|analytic signal| = AM envelope", env_err < 0.01, f"max err {env_err:.4f}")

# 10 --------------------------------------------------------------- ppm offsets
for f, ppm in [(433.92e6, 1), (433.92e6, 20), (915e6, 10), (1575.42e6, 0.5)]:
    print(f"      {ppm:>4} ppm at {f/1e6:8.2f} MHz = {f*ppm*1e-6/1e3:7.3f} kHz")
check("20 ppm at 433.92 MHz = 8.68 kHz", abs(433.92e6 * 20e-6 - 8678.4) < 0.1)

print("\nALL PASS" if ok_all else "\nSOME FAIL")
