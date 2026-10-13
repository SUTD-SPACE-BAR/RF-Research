#!/usr/bin/env python3
"""Verification for kb/00-math-foundations/complex-numbers-and-phasors.md

Checks: Euler identity; polar/rect conversion; phasor steady-state solution of a
series RLC circuit versus brute-force time-domain ODE integration; complex power
P = 1/2 Re{V I*} versus time-average of v(t) i(t); RMS, PEP and crest factor of a
two-tone signal; analytic signal / Hilbert envelope; one-sided spectrum of a complex
exponential versus two-sided spectrum of a real cosine; IQ downconversion sign of
frequency.
Run: python3 tools/verify/math_complex_phasors.py
"""
import numpy as np
from scipy import signal
from scipy.integrate import solve_ivp

ok_all = True


def check(name, got, want, tol):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol})")


# Euler and conversions
th = 0.7
check("Euler |e^{j th} - (cos + j sin)|", abs(np.exp(1j * th) - (np.cos(th) + 1j * np.sin(th))), 0, 1e-15)
check("e^{j pi} + 1", abs(np.exp(1j * np.pi) + 1), 0, 1e-15)
z = 3 + 4j
check("|3+4j|", abs(z), 5, 1e-12)
check("angle(3+4j) deg", np.degrees(np.angle(z)), 53.1301, 1e-4)
check("j^j (principal) = e^{-pi/2}", (1j ** 1j).real, np.exp(-np.pi / 2), 1e-12)
# multiplication: magnitudes multiply, angles add
z1, z2 = 2 * np.exp(1j * 0.3), 5 * np.exp(1j * 1.1)
check("|z1 z2| = |z1||z2|", abs(z1 * z2), 10, 1e-12)
check("arg(z1 z2) = arg z1 + arg z2", np.angle(z1 * z2), 1.4, 1e-12)

# --- Series RLC driven by v(t) = Vm cos(w t): phasor vs ODE -----------------------
R, L, Cc = 10.0, 1e-6, 1e-9          # f0 = 5.03 MHz
f = 4e6
w = 2 * np.pi * f
Vm = 1.0
Z = R + 1j * w * L + 1 / (1j * w * Cc)
Iph = Vm / Z                          # peak phasor of current
# ODE: L di/dt + R i + q/C = v, dq/dt = i
def rhs(t, y):
    q, i = y
    return [i, (Vm * np.cos(w * t) - R * i - q / Cc) / L]
tau = 2 * L / R                       # envelope decay time constant = 0.2 us
T = 1 / f
t_end = 40 * tau
t_eval = np.linspace(t_end - 5 * T, t_end, 2001)
sol = solve_ivp(rhs, [0, t_end], [0, 0], t_eval=t_eval, rtol=1e-10, atol=1e-16, max_step=T / 200)
i_t = sol.y[1]
i_pred = np.real(Iph * np.exp(1j * w * t_eval))
check("RLC steady state: max|i_ode - Re{I e^{jwt}}| / |I|", np.max(abs(i_t - i_pred)) / abs(Iph), 0, 1e-4)
# complex power vs time average
v_t = Vm * np.cos(w * t_eval)
p_avg_time = np.mean((v_t * i_t)[:-1][: int(2000 / 5) * 5])  # integer number of periods (5 T over 2000 steps)
S = 0.5 * Vm * np.conj(Iph)
check("P_avg = 1/2 Re{V I*} vs time average", p_avg_time, S.real, 1e-3 * abs(S))
check("P_avg = 1/2 |I|^2 R", 0.5 * abs(Iph) ** 2 * R, S.real, 1e-12)
check("Q = 1/2 |I|^2 (X_L + X_C)", 0.5 * abs(Iph) ** 2 * (w * L - 1 / (w * Cc)), S.imag, 1e-12)

# --- RMS / PEP / crest factor --------------------------------------------------------
t = np.linspace(0, 1e-3, 1_000_001)[:-1]
A = 1.0
x = A * np.cos(2 * np.pi * 10e3 * t)
check("RMS of sine = A/sqrt2", np.sqrt(np.mean(x ** 2)), A / np.sqrt(2), 1e-6)
x2 = A * np.cos(2 * np.pi * 100e3 * t) + A * np.cos(2 * np.pi * 101e3 * t)  # two-tone
Pavg = np.mean(x2 ** 2) / 50
env_peak = 2 * A
PEP = (env_peak / np.sqrt(2)) ** 2 / 50
check("two-tone: avg power = 2 x one-tone power", Pavg, 2 * (A ** 2 / 2 / 50), 1e-6)
check("two-tone PEP/avg [dB]", 10 * np.log10(PEP / Pavg), 3.0103, 1e-3)
check("two-tone instantaneous peak^2/avg-power (PAPR incl. carrier) [dB]", 10 * np.log10(np.max(x2 ** 2) / 50 / Pavg), 6.0206, 1e-3)

# --- analytic signal / envelope --------------------------------------------------------
fs = 1e6
tt = np.arange(0, 0.02, 1 / fs)
m = 0.5
am = (1 + m * np.cos(2 * np.pi * 500 * tt)) * np.cos(2 * np.pi * 100e3 * tt)
za = signal.hilbert(am)
env = np.abs(za)
mid = slice(2000, -2000)
check("Hilbert envelope recovers 1+m cos (max err)", np.max(abs(env[mid] - (1 + m * np.cos(2 * np.pi * 500 * tt[mid])))), 0, 2e-3)
Zs = np.fft.fft(za)
fr = np.fft.fftfreq(len(za), 1 / fs)
neg = np.sum(abs(Zs[fr < 0]) ** 2) / np.sum(abs(Zs) ** 2)
check("analytic signal: fraction of energy at negative f", neg, 0, 1e-6)

# --- spectra: complex exponential vs cosine ---------------------------------------------
N = 1000
n = np.arange(N)
k0 = 50
Xc = np.fft.fft(np.exp(2j * np.pi * k0 * n / N)) / N
Xr = np.fft.fft(np.cos(2 * np.pi * k0 * n / N)) / N
check("e^{j w0 n}: bin +k0 amplitude", abs(Xc[k0]), 1.0, 1e-12)
check("e^{j w0 n}: bin -k0 amplitude", abs(Xc[-k0]), 0.0, 1e-12)
check("cos: bin +k0 amplitude (half)", abs(Xr[k0]), 0.5, 1e-12)
check("cos: bin -k0 amplitude (half)", abs(Xr[-k0]), 0.5, 1e-12)

# --- IQ downconversion: signal at fc + df vs fc - df ------------------------------------
fs = 10e6
tt = np.arange(0, 1e-3, 1 / fs)
fc, df = 2e6, 50e3
for sgn in (+1, -1):
    rf = np.cos(2 * np.pi * (fc + sgn * df) * tt)
    bb = rf * np.exp(-2j * np.pi * fc * tt)           # I = rf cos, Q = -rf sin
    b, a = signal.butter(6, 500e3, fs=fs)
    bbf = signal.filtfilt(b, a, bb)
    F = np.fft.fftshift(np.fft.fft(bbf))
    fr = np.fft.fftshift(np.fft.fftfreq(len(bbf), 1 / fs))
    check(f"IQ: tone at fc{'+' if sgn > 0 else '-'}50 kHz appears at baseband [kHz]", fr[np.argmax(abs(F))] / 1e3, sgn * 50, 0.5)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
