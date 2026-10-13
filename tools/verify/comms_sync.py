#!/usr/bin/env python3
"""Verification for kb/10-comms-modulation/synchronization-carrier-timing.md

Run:  python3 tools/verify/comms_sync.py      (~15 s)

Checks:
  1. Second-order digital PLL / Costas loop (BPSK, e = I*Q) with PI loop filter designed from
     (Bn*T, zeta) using the standard discrete-time formulas (M. Rice, Digital Communications:
     A Discrete-Time Approach, App. C):
       a) steady-state phase-error variance vs linear theory  Bn*T/(Es/N0) * (1 + 1/(2 Es/N0))
          (the second factor = Costas "squaring loss");
       b) pulls in and tracks a constant frequency offset with ~zero mean phase error;
       c) under a frequency *ramp* (Doppler rate) the steady-state phase error is
          (d omega/dt) / omega_n^2  (type-2 loop), omega_n = 2 Bn / (zeta + 1/(4 zeta)).
  2. Timing-error detectors on RRC-shaped QPSK: Gardner (2 samples/symbol, carrier-phase
     independent) and Mueller-Muller (1 sample/symbol, decision-directed): S-curves cross zero at
     the correct timing with the correct slope sign; Gardner output unchanged by carrier phase.
  3. Frequency estimation of a complex tone: FFT peak + parabolic interpolation approaches the
     Cramer-Rao bound var(f) >= 6 fs^2 / ((2 pi)^2 SNR N (N^2-1)) at high SNR; and the
     M-th power method for QPSK recovers an offset within +-fs/(2M).
  4. Rocket Doppler numbers used on the page.
"""
import numpy as np
from scipy import special

rng = np.random.default_rng(8)
ok_all = True


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel else 1.0)
    ok = err <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.5g}, expected {want:.5g} (tol {tol}{' rel' if rel else ''})")


def loop_gains(BnT, zeta, Kp, K0=1.0):
    th = BnT / (zeta + 1 / (4 * zeta))
    d = 1 + 2 * zeta * th + th ** 2
    K1 = 4 * zeta * th / d / (Kp * K0)
    K2 = 4 * th ** 2 / d / (Kp * K0)
    return K1, K2


def costas(r, K1, K2):
    """BPSK Costas loop at 1 sample/symbol. Returns phase estimate per sample."""
    phi = 0.0
    integ = 0.0
    est = np.empty(len(r))
    for n, x in enumerate(r):
        y = x * np.exp(-1j * phi)
        e = y.real * y.imag
        integ += K2 * e
        v = K1 * e + integ
        est[n] = phi
        phi += v
    return est


# ---------------------------------------------------------------------- 1a
esn0_db = 10.0
esn0 = 10 ** (esn0_db / 10)
BnT, zeta = 0.01, 1 / np.sqrt(2)
A = 1.0
Kp = A ** 2            # e = I*Q = (A^2/2) sin(2 phi) ~ A^2 phi
K1, K2 = loop_gains(BnT, zeta, Kp)
N = 200_000
theta0 = 0.7
b = 1 - 2.0 * rng.integers(0, 2, N)
n0 = 1 / esn0
r = A * b * np.exp(1j * theta0) + np.sqrt(n0 / 2) * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
est = costas(r, K1, K2)
err = np.angle(np.exp(1j * (theta0 - est[5000:])) ** 2) / 2      # mod-pi ambiguity of BPSK
var_sim = np.var(err)
var_th = BnT / esn0 * (1 + 1 / (2 * esn0))
print(f"  Costas BPSK, Es/N0 {esn0_db} dB, BnT {BnT}: phase jitter {np.degrees(np.sqrt(var_sim)):.2f} deg rms "
      f"(theory {np.degrees(np.sqrt(var_th)):.2f} deg)")
check("Costas phase-error variance vs linear theory", var_sim, var_th, 0.2, rel=True)

# ---------------------------------------------------------------------- 1b
df_norm = 0.002       # cycles per symbol (e.g. 20 Hz at 10 kbaud)
t = np.arange(N)
r = A * b * np.exp(1j * (theta0 + 2 * np.pi * df_norm * t)) + np.sqrt(n0 / 2) * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
est = costas(r, K1, K2)
err = np.angle(np.exp(1j * (theta0 + 2 * np.pi * df_norm * t[20000:] - est[20000:])) ** 2) / 2
check("type-2 loop: mean phase error under constant frequency offset [rad]", np.mean(err), 0.0, 0.01)

# ---------------------------------------------------------------------- 1c
# frequency ramp: d(omega)/dt in rad/sample^2
ramp = 2e-6           # rad/sample^2
r = A * b * np.exp(1j * (theta0 + 0.5 * ramp * t ** 2)) + np.sqrt(n0 / 2) * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
est = costas(r, K1, K2)
err = np.angle(np.exp(1j * (theta0 + 0.5 * ramp * t[50000:150000] ** 2 - est[50000:150000])) ** 2) / 2
wn = 2 * BnT / (zeta + 1 / (4 * zeta))     # rad/sample (continuous approx)
pred = ramp / wn ** 2
check("steady-state phase error under Doppler ramp = (domega/dt)/wn^2 [rad]", np.mean(err), pred, 0.15, rel=True)

# ---------------------------------------------------------------------- 2


def rrc(tt, beta):
    h = np.empty_like(tt)
    for i, x in enumerate(tt):
        if abs(x) < 1e-12:
            h[i] = 1 - beta + 4 * beta / np.pi
        elif abs(abs(x) - 1 / (4 * beta)) < 1e-12:
            h[i] = beta / np.sqrt(2) * ((1 + 2 / np.pi) * np.sin(np.pi / (4 * beta)) + (1 - 2 / np.pi) * np.cos(np.pi / (4 * beta)))
        else:
            h[i] = (np.sin(np.pi * x * (1 - beta)) + 4 * beta * x * np.cos(np.pi * x * (1 + beta))) / (np.pi * x * (1 - (4 * beta * x) ** 2))
    return h


sps = 32
beta = 0.35
tt = np.arange(-8 * sps, 8 * sps + 1) / sps
h = rrc(tt, beta)
h /= np.sqrt(np.sum(h ** 2))
nsym = 6000
sym = np.exp(1j * (np.pi / 4 + np.pi / 2 * rng.integers(0, 4, nsym)))
up = np.zeros(nsym * sps, complex)
up[::sps] = sym
x = np.convolve(np.convolve(up, h), h)            # TX RRC + RX RRC = RC, noiseless
delay = len(h) - 1                                   # total filter delay in samples
offsets = np.arange(-sps // 2, sps // 2 + 1, 2)
S_g, S_g_rot, S_mm = [], [], []
for off in offsets:
    idx = delay + np.arange(50, nsym - 50) * sps + off
    y = x[idx]
    ymid = x[idx - sps // 2]
    e_g = np.real(np.conj(ymid) * (y - x[idx - sps]))          # Gardner: y(n-1/2)^* [y(n)-y(n-1)]
    rot = np.exp(1j * 1.1)
    e_gr = np.real(np.conj(ymid * rot) * (y * rot - x[idx - sps] * rot))
    a = np.sign(y.real) + 1j * np.sign(y.imag)
    yprev = x[idx - sps]
    aprev = np.sign(yprev.real) + 1j * np.sign(yprev.imag)
    e_mm = np.real(np.conj(aprev) * y - np.conj(a) * yprev)   # Mueller-Muller
    S_g.append(e_g.mean())
    S_g_rot.append(e_gr.mean())
    S_mm.append(e_mm.mean())
S_g, S_mm = np.array(S_g), np.array(S_mm)
i0 = np.where(offsets == 0)[0][0]
check("Gardner S-curve zero at correct timing", S_g[i0], 0.0, 1e-3)
check("M&M S-curve zero at correct timing", S_mm[i0], 0.0, 1e-3)
ok = np.sign(S_g[i0 + 1]) != np.sign(S_g[i0 - 1]) and np.sign(S_mm[i0 + 1]) != np.sign(S_mm[i0 - 1])
ok_all &= ok
print(f"[{'PASS' if ok else 'FAIL'}] both S-curves change sign through the correct timing (odd symmetric)")
check("Gardner invariant to carrier phase (max diff)", np.max(np.abs(np.array(S_g_rot) - S_g)), 0.0, 1e-9)
print("  S-curves (offset in samples at 32 sps):", {int(o): (round(float(g), 3), round(float(m), 3)) for o, g, m in zip(offsets[::2], S_g[::2], S_mm[::2])})

# ---------------------------------------------------------------------- 3
fs = 1.0
Nn = 256
snr_db = 10.0
snr = 10 ** (snr_db / 10)
f0 = 0.1234
trials = 3000
ests = []
for _ in range(trials):
    n = np.arange(Nn)
    z = np.exp(1j * (2 * np.pi * f0 * n + rng.random() * 6.28)) + np.sqrt(1 / snr / 2) * (rng.standard_normal(Nn) + 1j * rng.standard_normal(Nn))
    Z = np.abs(np.fft.fft(z, 16 * Nn))
    k = np.argmax(Z)
    a_, b_, c_ = Z[k - 1], Z[k], Z[(k + 1) % len(Z)]
    p = 0.5 * (a_ - c_) / (a_ - 2 * b_ + c_)
    ests.append((k + p) / (16 * Nn))
ests = np.array(ests)
crb = 6 * fs ** 2 / ((2 * np.pi) ** 2 * snr * Nn * (Nn ** 2 - 1))
print(f"  tone freq estimate: rms error {np.sqrt(np.mean((ests - f0) ** 2)):.3e} cycles/sample, CRB {np.sqrt(crb):.3e}")
check("FFT+interp frequency estimator within ~1 dB of CRB at 10 dB SNR", np.mean((ests - f0) ** 2) / crb, 1.0, 0.3)
# M-th power for QPSK
M = 4
fo = 0.03                  # cycles/symbol, within +-1/(2M)=0.125
n = np.arange(4096)
s = np.exp(1j * (np.pi / 4 + np.pi / 2 * rng.integers(0, 4, len(n)))) * np.exp(1j * 2 * np.pi * fo * n)
s += np.sqrt(0.05) * (rng.standard_normal(len(n)) + 1j * rng.standard_normal(len(n)))
S4 = np.abs(np.fft.fft(s ** 4, 65536))
f4 = np.fft.fftfreq(65536)[np.argmax(S4)] / M
check("4th-power CFO estimate for QPSK [cycles/symbol]", f4, fo, 2e-4)

# ---------------------------------------------------------------------- 4
c = 299_792_458.0
for f, v, want in ((433.0e6, 1000.0, 1444.3), (915e6, 1000.0, 3052.1), (1575.42e6, 1000.0, 5255.0), (433e6, 300.0, 433.3)):
    check(f"Doppler at {f/1e6:.0f} MHz, {v:.0f} m/s [Hz]", v / c * f, want, 1.0)
check("Doppler rate at 915 MHz, 10 g [Hz/s]", 98.07 / c * 915e6, 299.3, 0.5)
check("10 ppm at 433 MHz [Hz]", 10e-6 * 433e6, 4330, 0.5)
# PLL example on page: Bn = 50 Hz, zeta 0.707, ramp 300 Hz/s -> phase error
Bn = 50.0
wn = 2 * Bn / (zeta + 1 / (4 * zeta))
check("wn for Bn=50 Hz, zeta=0.707 [rad/s]", wn, 94.28, 0.05)
check("ramp phase error 300 Hz/s, Bn=50 Hz [deg]", np.degrees(2 * np.pi * 300 / wn ** 2), 12.2, 0.2)

print("\nOVERALL:", "PASS" if ok_all else "FAIL")
