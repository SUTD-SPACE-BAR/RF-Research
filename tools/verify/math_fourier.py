#!/usr/bin/env python3
"""Verification for kb/00-math-foundations/fourier-series-and-transform.md

Checks: square-wave harmonic amplitudes; trapezoidal clock Fourier coefficients
(sinc*sinc formula vs FFT of sampled waveform) and envelope breakpoints; Gibbs overshoot;
rect<->sinc and -3 dB / null bandwidths; Parseval; convolution theorem; modulation theorem;
pulsed-RF line spectrum; Gaussian time-bandwidth product (rms widths); LFM chirp spectrum
width and TB product (LoRa: TB = 2^SF); DFT bin spacing.
Convention: X(f) = integral x(t) exp(-j 2 pi f t) dt ; sinc(x) = sin(pi x)/(pi x) (numpy).
Run: python3 tools/verify/math_fourier.py
"""
import numpy as np

ok_all = True


def check(name, got, want, tol):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol})")


# ---------------- square wave ----------------------------------------------------
N = 2 ** 16
t = np.arange(N) / N           # one period T = 1
sq = np.where(t < 0.5, 1.0, -1.0)   # +/-1 square wave
c = np.fft.fft(sq) / N
for n in [1, 3, 5, 7]:
    check(f"+/-1 square wave harmonic {n} amplitude (4/(pi n))", 2 * abs(c[n]), 4 / (np.pi * n), 2e-3)
check("square wave: even harmonic 2 ~ 0", 2 * abs(c[2]), 0, 1e-9)
# energy fraction in fundamental: (8/pi^2)
check("fraction of square-wave power in fundamental", (2 * abs(c[1])) ** 2 / 2 / np.mean(sq ** 2), 8 / np.pi ** 2, 1e-3)

# ---------------- trapezoid clock --------------------------------------------------
# period T, amplitude A (0..A), pulse width tau (50% points), rise=fall=tr
A, T, tau, tr = 3.3, 1 / 25e6, 20e-9, 2e-9      # 25 MHz clock, 50% duty, 2 ns edges
Ns = 2 ** 18
tt = np.arange(Ns) * T / Ns
x = np.zeros(Ns)
# rising edge from 0 to tr, flat to tau, falling from tau to tau+tr  (50% points at tr/2 and tau+tr/2)
x = np.clip(np.minimum(tt / tr, (tau + tr - tt) / tr), 0, 1) * A
cn = np.fft.fft(x) / Ns
for n in [1, 3, 5, 11, 21]:
    theory = A * tau / T * abs(np.sinc(n * tau / T) * np.sinc(n * tr / T))
    check(f"trapezoid |c_{n}| vs A(tau/T)|sinc(n tau/T) sinc(n tr/T)|", abs(cn[n]), theory, 1e-4 * A)
check("trapezoid 50% duty: |c_2| ~ 0", abs(cn[2]), 0, 1e-6 * A)
# one-sided amplitude of harmonic n is 2|c_n|; 25 MHz clock harmonic at 425 MHz (n=17) lands near 433 band
n = 17
amp17 = 2 * A * tau / T * abs(np.sinc(n * tau / T) * np.sinc(n * tr / T))
check("25 MHz 3.3 V clock, 17th harmonic (425 MHz) amplitude [dBuV]", 20 * np.log10(amp17 / np.sqrt(2) / 1e-6), 20 * np.log10(2 * abs(cn[17]) / np.sqrt(2) / 1e-6), 0.01)
print(f"      (17th harmonic amplitude = {amp17*1e3:.1f} mV peak = {20*np.log10(amp17/np.sqrt(2)/1e-6):.1f} dBuV rms)")
print(f"      breakpoints: 1/(pi tau) = {1/(np.pi*tau)/1e6:.1f} MHz, 1/(pi tr) = {1/(np.pi*tr)/1e6:.1f} MHz")

# ---------------- Gibbs ---------------------------------------------------------------
tg = np.linspace(0, 0.5, 200001)
K = 201
partial = sum(4 / (np.pi * k) * np.sin(2 * np.pi * k * tg) for k in range(1, K + 1, 2))
check("Gibbs overshoot of partial sum (fraction of jump 2)", (partial.max() - 1) / 2, 0.0895, 1e-3)

# ---------------- rect <-> sinc ------------------------------------------------------
from scipy.optimize import brentq
x3 = brentq(lambda u: np.sinc(u) ** 2 - 0.5, 0.1, 0.9)
check("sinc^2(u)=1/2 at u", x3, 0.4429, 1e-4)
check("-3 dB full width of rect(t/tau) spectrum x tau", 2 * x3, 0.8859, 1e-4)
check("first sidelobe of sinc [dB]", 20 * np.log10(abs(np.sinc(1.4303))), -13.26, 0.01)

# ---------------- Parseval / convolution / modulation (DFT versions) ------------------
rng = np.random.default_rng(0)
a = rng.standard_normal(4096)
b = rng.standard_normal(4096)
A_ = np.fft.fft(a)
check("Parseval sum|x|^2 = (1/N) sum|X|^2", np.sum(a ** 2), np.sum(abs(A_) ** 2) / len(a), 1e-8)
circ = np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))
direct = np.array([np.sum(a * np.roll(b[::-1], k + 1)) for k in range(0, 50)])
check("circular convolution via FFT == direct (first 50)", np.max(abs(circ[:50] - direct)), 0, 1e-9)
# modulation: x(t) cos(2 pi f0 t) -> 1/2[X(f-f0)+X(f+f0)]
Nn = 4096
nn = np.arange(Nn)
bb = np.exp(-0.5 * ((nn - Nn / 2) / 40) ** 2)
k0 = 500
mod = bb * np.cos(2 * np.pi * k0 * nn / Nn)
Bm = np.fft.fft(bb)
Mm = np.fft.fft(mod)
pred = 0.5 * (np.roll(Bm, k0) + np.roll(Bm, -k0))
check("modulation theorem max error", np.max(abs(Mm - pred)), 0, 1e-8)

# ---------------- pulsed RF: line spacing and sinc nulls ------------------------------
fs = 1e9
PRI = 1e-6
tau_p = 100e-9
fc = 100e6
Np = 64
tp = np.arange(int(Np * PRI * fs)) / fs
gate = ((tp % PRI) < tau_p).astype(float)
s = gate * np.cos(2 * np.pi * fc * tp)
S = np.abs(np.fft.rfft(s))
fr = np.fft.rfftfreq(len(s), 1 / fs)
df = fr[1]
# line spacing: strongest bins near fc should be at fc + k*PRF
peaks = fr[np.argsort(S)[-5:]]
spacing = np.min(np.diff(np.sort(peaks)))
check("pulsed RF line spacing = PRF [MHz]", spacing / 1e6, 1.0, df / 1e6 + 1e-9)
i_null = np.argmin(abs(fr - (fc + 1 / tau_p)))
check("pulsed RF: envelope null at fc + 1/tau (rel. to peak, dB < -40)", float(20 * np.log10(S[i_null] / S.max()) < -40), 1.0, 0)

# ---------------- Gaussian time-bandwidth (rms) ----------------------------------------
fsg = 1e3
tg = np.arange(-50, 50, 1 / fsg)
sig = 1.3
g = np.exp(-tg ** 2 / (2 * sig ** 2))
G = np.fft.fftshift(np.fft.fft(g))
fg = np.fft.fftshift(np.fft.fftfreq(len(g), 1 / fsg))
pt = g ** 2 / np.sum(g ** 2)
pf = abs(G) ** 2 / np.sum(abs(G) ** 2)
dt = np.sqrt(np.sum(pt * tg ** 2))
dfq = np.sqrt(np.sum(pf * fg ** 2))
check("Gaussian rms duration x rms bandwidth = 1/(4 pi)", dt * dfq, 1 / (4 * np.pi), 1e-6)

# ---------------- LFM chirp -------------------------------------------------------------
for SF in [7, 12]:
    BW = 125e3
    Ts = 2 ** SF / BW
    check(f"LoRa SF{SF} BW125: T*B = 2^SF", Ts * BW, 2 ** SF, 1e-9)
fsc = 10e6
Tc = 100e-6
Bc = 2e6
tc = np.arange(0, Tc, 1 / fsc)
ch = np.exp(1j * np.pi * (Bc / Tc) * (tc - Tc / 2) ** 2)   # sweeps -B/2..+B/2
CH = np.fft.fftshift(np.fft.fft(ch, 2 ** 16))
fch = np.fft.fftshift(np.fft.fftfreq(2 ** 16, 1 / fsc))
P = abs(CH) ** 2
occupied = fch[P > P.max() / 10 ** (6 / 10)]
check("chirp TB=200: -6 dB spectral width / B", (occupied.max() - occupied.min()) / Bc, 1.0, 0.05)
# 99% energy bandwidth
cs = np.cumsum(P) / P.sum()
bw99 = fch[np.searchsorted(cs, 0.995)] - fch[np.searchsorted(cs, 0.005)]
check("chirp 99% energy bandwidth / B (close to 1 for large TB)", bw99 / Bc, 1.0, 0.1)

# ---------------- DFT bin spacing -----------------------------------------------------------
check("DFT bin spacing fs/N [Hz] (fs=2.4 MS/s, N=2048)", 2.4e6 / 2048, 1171.875, 1e-9)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
