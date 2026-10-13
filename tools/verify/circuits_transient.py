#!/usr/bin/env python3
"""
Verification for kb/01-circuit-theory/transient-and-step-response.md

  1. RC step response: 10-90 % rise time = tau*ln 9; tr*BW = ln9/(2 pi) = 0.350.
  2. Series RLC step (voltage across C): damping ratio, overshoot formula, ringing frequency, decay.
  3. Rise-time x bandwidth products for several responses (single pole, 2 identical poles, Butterworth
     N=2..5, Bessel N=2..5, Gaussian).
  4. Rise-time addition rule sqrt(sum tr^2): check for cascaded stages.
  5. Worked examples: scope probe ground lead ringing; decoupling cap + trace inductance step;
     settling times.
Run: python3 tools/verify/circuits_transient.py
"""
import numpy as np
from scipy import signal

def rise_time(t, y):
    yf = y[-1]
    t10 = t[np.argmax(y >= 0.1 * yf)]
    t90 = t[np.argmax(y >= 0.9 * yf)]
    return t90 - t10

def bw3(b, a, wmax=100):
    w = np.linspace(1e-4, wmax, 400001)
    _, h = signal.freqs(b, a, worN=w)
    h = np.abs(h) / np.abs(h[0])
    return w[np.argmax(h <= 1 / np.sqrt(2))] / (2 * np.pi)

print("=== 1. RC ===")
tau = 1.0
t = np.linspace(0, 20, 200001)
y = 1 - np.exp(-t / tau)
tr = rise_time(t, y)
print(f"tr = {tr:.5f} tau (ln 9 = {np.log(9):.5f}); BW = 1/(2 pi tau); tr*BW = {tr/(2*np.pi):.4f}")

print("\n=== 2. Series RLC, output across C ===")
L, C = 1.0, 1.0
w0 = 1 / np.sqrt(L * C)
for zeta in [0.05, 0.2, 0.5, 0.707, 1.0, 2.0]:
    R = 2 * zeta * np.sqrt(L / C)
    b, a = [1 / (L * C)], [1, R / L, 1 / (L * C)]
    t = np.linspace(0, 60, 600001)
    _, y = signal.step((b, a), T=t)
    os_num = (y.max() - 1) * 100
    os_formula = 100 * np.exp(-np.pi * zeta / np.sqrt(1 - zeta**2)) if zeta < 1 else 0.0
    Q = 1 / (2 * zeta)
    print(f"zeta={zeta:5.3f} (Q={Q:5.2f}): overshoot numerical {os_num:6.2f} %, formula {os_formula:6.2f} %, "
          f"tr = {rise_time(t,y):.3f}/w0, wd/w0 = {np.sqrt(max(0,1-zeta**2)):.3f}")
    if zeta < 1:
        assert abs(os_num - os_formula) < 0.05

print("\n=== 3. Rise time x bandwidth products ===")
cases = {"1 pole": ([1], [1, 1]), "2 identical poles": ([1], np.polymul([1, 1], [1, 1]))}
for N in [2, 3, 4, 5]:
    cases[f"Butterworth N={N}"] = signal.butter(N, 1, analog=True)
    cases[f"Bessel N={N} (3dB-norm)"] = signal.bessel(N, 1, analog=True, norm="mag")
for name, (b, a) in cases.items():
    t = np.linspace(0, 80, 400001)
    _, y = signal.step((b, a), T=t)
    tr = rise_time(t, y)
    f3 = bw3(b, a)
    os_ = max(0, (y.max() / y[-1] - 1) * 100)
    print(f"{name:24s}: tr*f3dB = {tr*f3:.3f}, overshoot = {os_:5.2f} %")
# Gaussian: H = exp(-a w^2); impulse Gaussian; rise time from erf
sigma = 1.0
# impulse response Gaussian with std sigma -> step = Phi(t/sigma); 10-90 % = 2*1.2816 sigma
tr_g = 2 * 1.2815516 * sigma
# |H(f)| = exp(-(2 pi f sigma)^2/2) -> -3 dB when (2 pi f sigma)^2/2 = ln(sqrt 2)
f3_g = np.sqrt(2 * np.log(np.sqrt(2))) / (2 * np.pi * sigma)
print(f"{'Gaussian':24s}: tr*f3dB = {tr_g*f3_g:.3f}, overshoot =  0.00 %")

print("\n=== 4. Rise time addition rule ===")
t = np.linspace(0, 60, 600001)
for taus in [(1, 1), (1, 3), (1, 1, 1)]:
    a = np.array([1.0])
    for tt in taus:
        a = np.polymul(a, [tt, 1])
    _, y = signal.step(([1], a), T=t)
    tr_true = rise_time(t, y)
    tr_rule = np.sqrt(sum((np.log(9) * tt)**2 for tt in taus))
    print(f"RC stages tau={taus}: actual tr = {tr_true:.3f}, sqrt-sum rule = {tr_rule:.3f} ({(tr_rule/tr_true-1)*100:+.1f} %)")

print("\n=== 5. Worked examples ===")
# (a) scope probe: 15 cm ground lead ~ 150 nH (approx 1 nH/mm is too high for a loop; use 150 nH), probe tip 12 pF
Lg, Cp = 150e-9, 12e-12
f0 = 1 / (2 * np.pi * np.sqrt(Lg * Cp))
Z0 = np.sqrt(Lg / Cp)
Rsrc = 50.0  # source driving through 50 ohm -> damping
zeta = Rsrc / (2 * Z0)
print(f"(a) probe ground lead 150 nH + 12 pF: f_ring = {f0/1e6:.1f} MHz, sqrt(L/C) = {Z0:.0f} ohm, "
      f"with 50 ohm source zeta = {zeta:.3f}, overshoot = {100*np.exp(-np.pi*zeta/np.sqrt(1-zeta**2)):.0f} %")
Lg2 = 5e-9
f02 = 1 / (2 * np.pi * np.sqrt(Lg2 * Cp)); zeta2 = Rsrc / (2 * np.sqrt(Lg2 / Cp))
print(f"    with a 5 nH spring ground: f_ring = {f02/1e6:.0f} MHz, zeta = {zeta2:.2f} -> "
      f"{'no overshoot' if zeta2>=1 else f'{100*np.exp(-np.pi*zeta2/np.sqrt(1-zeta2**2)):.1f} % overshoot'}")
# (b) 10 uF MLCC at the end of 20 nH of wiring/trace, ESR 5 mohm; load step
L2, C2, R2 = 20e-9, 10e-6, 5e-3
f0b = 1 / (2 * np.pi * np.sqrt(L2 * C2)); Z0b = np.sqrt(L2 / C2); zb = R2 / (2 * Z0b)
print(f"(b) 20 nH + 10 uF (ESR 5 mohm): f0 = {f0b/1e3:.0f} kHz, Z0 = {Z0b*1e3:.1f} mohm, zeta = {zb:.3f} (Q = {1/(2*zb):.1f})")
Rd = Z0b  # critical damping-ish: series R ~ Z0 via an electrolytic's ESR
print(f"    adding ~{Rd*1e3:.0f} mohm of series damping (e.g. a polymer/electrolytic bulk cap ESR) gives zeta ~ {(R2+Rd)/(2*Z0b):.2f}")
# (c) settling: first order to 1 %, 0.1 %
print(f"(c) first-order settling: 1 % in {np.log(100):.2f} tau, 0.1 % in {np.log(1000):.2f} tau")
# (d) ring-down of a 915 MHz resonator with QL = 30
QL, f0d = 30, 915e6
tau_env = 2 * QL / (2 * np.pi * f0d)
print(f"(d) 915 MHz, QL=30: amplitude envelope time constant 2QL/w0 = {tau_env*1e9:.2f} ns ({tau_env*f0d:.1f} cycles)")
print("OK")
