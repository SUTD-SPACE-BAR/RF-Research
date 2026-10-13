#!/usr/bin/env python3
"""Verification for kb/00-math-foundations/laplace-transfer-functions-bode.md

Checks: Laplace pairs via sympy; partial fractions; Bode asymptote errors (3.01 dB, 5.71 deg);
second-order peak magnitude/frequency, Q = 1/(2 zeta), step overshoot formula; rise-time x
bandwidth = ln9/(2 pi); group delay of first-order low-pass and of a resonator at centre
(2Q/w0); minimum-phase vs all-pass (same |H|, different phase); Bode gain-phase integral
reproduces the phase of a real pole from its magnitude alone; final-value theorem.
Run: python3 tools/verify/math_laplace_bode.py
"""
import numpy as np
import sympy as sp
from scipy import signal, integrate

ok_all = True


def check(name, got, want, tol):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol})")


# --- Laplace pairs (sympy) --------------------------------------------------------
t, s = sp.symbols('t s', positive=True)
a, w = sp.symbols('a omega', positive=True)
pairs = [
    (sp.exp(-a * t), 1 / (s + a)),
    (sp.sin(w * t), w / (s ** 2 + w ** 2)),
    (sp.cos(w * t), s / (s ** 2 + w ** 2)),
    (t * sp.exp(-a * t), 1 / (s + a) ** 2),
    (sp.exp(-a * t) * sp.sin(w * t), w / ((s + a) ** 2 + w ** 2)),
]
for f, F in pairs:
    got = sp.laplace_transform(f, t, s, noconds=True)
    check(f"Laplace of {f}", float(sp.simplify(got - F) == 0), 1.0, 0)

# --- partial fractions ---------------------------------------------------------------
# H(s) = (s+3)/((s+1)(s+2)) = 2/(s+1) - 1/(s+2)
r, p, k = signal.residue([1, 3], np.polymul([1, 1], [1, 2]))
res = dict(zip(np.round(p.real, 6), r.real))
check("residue at s=-1", res[-1.0], 2.0, 1e-9)
check("residue at s=-2", res[-2.0], -1.0, 1e-9)

# --- first-order Bode errors -------------------------------------------------------------
wc = 1.0
H1 = lambda ww: 1 / (1 + 1j * ww / wc)
check("|H| at corner [dB]", 20 * np.log10(abs(H1(1.0))), -3.0103, 1e-4)
check("phase at corner [deg]", np.degrees(np.angle(H1(1.0))), -45, 1e-9)
check("phase error of 0.1wc..10wc straight-line at 0.1 wc [deg]", np.degrees(np.angle(H1(0.1))) - 0, -5.71, 0.01)
check("slope well above corner [dB/dec]", 20 * np.log10(abs(H1(1e4)) / abs(H1(1e3))), -20.0, 1e-3)

# --- rise time x bandwidth ----------------------------------------------------------------
tau = 1e-9
sys1 = signal.lti([1], [tau, 1])
tt = np.linspace(0, 10 * tau, 200001)
_, y = signal.step(sys1, T=tt)
t10 = tt[np.searchsorted(y, 0.1)]
t90 = tt[np.searchsorted(y, 0.9)]
f3 = 1 / (2 * np.pi * tau)
check("single-pole tr*f3dB", (t90 - t10) * f3, np.log(9) / (2 * np.pi), 1e-3)

# --- second-order low-pass: H = wn^2/(s^2 + 2 zeta wn s + wn^2) ----------------------------
wn = 2 * np.pi * 1e6
for zeta in [0.1, 0.3, 0.5]:
    num, den = [wn ** 2], [1, 2 * zeta * wn, wn ** 2]
    ww = np.logspace(np.log10(wn) - 2, np.log10(wn) + 2, 400001)
    _, h = signal.freqs(num, den, worN=ww)
    peak = np.max(abs(h))
    wpk = ww[np.argmax(abs(h))]
    check(f"zeta={zeta}: peak |H| = 1/(2 zeta sqrt(1-zeta^2))", peak, 1 / (2 * zeta * np.sqrt(1 - zeta ** 2)), 1e-4 * peak)
    check(f"zeta={zeta}: peak freq = wn sqrt(1-2 zeta^2)", wpk / wn, np.sqrt(1 - 2 * zeta ** 2), 1e-4)
    check(f"zeta={zeta}: |H(j wn)| = Q = 1/(2 zeta)", abs(signal.freqs(num, den, worN=[wn])[1][0]), 1 / (2 * zeta), 1e-9)
    ts = np.linspace(0, 60 / (zeta * wn), 200001)
    _, ys = signal.step(signal.lti(num, den), T=ts)
    check(f"zeta={zeta}: step overshoot = exp(-pi zeta/sqrt(1-zeta^2))", ys.max() - 1, np.exp(-np.pi * zeta / np.sqrt(1 - zeta ** 2)), 1e-4)
# no peaking at zeta = 1/sqrt2 (Butterworth)
num, den = [1], [1, np.sqrt(2), 1]
ww = np.logspace(-3, 3, 200001)
_, h = signal.freqs(num, den, worN=ww)
check("Butterworth 2nd order: max |H| = 1 (no peaking)", np.max(abs(h)), 1.0, 1e-9)
check("Butterworth 2nd order: -3.01 dB at wn", 20 * np.log10(abs(signal.freqs(num, den, worN=[1.0])[1][0])), -3.0103, 1e-4)

# --- group delay -------------------------------------------------------------------------------
def group_delay(num, den, ww):
    _, h = signal.freqs(num, den, worN=ww)
    ph = np.unwrap(np.angle(h))
    return -np.gradient(ph, ww)
tau = 1e-6
ww = np.linspace(1, 5e6, 500001)
gd = group_delay([1], [tau, 1], ww)
check("RC low-pass group delay at DC = tau", gd[0], tau, 1e-9)
i = np.argmin(abs(ww - 1 / tau))
check("RC low-pass group delay at corner = tau/2", gd[i], tau / 2, 1e-9)
# resonator bandpass H = (w0/Q) s /(s^2 + (w0/Q) s + w0^2), group delay at w0 = 2Q/w0
f0 = 433e6
w0 = 2 * np.pi * f0
Q = 10
ww = np.linspace(0.9 * w0, 1.1 * w0, 400001)
gd = group_delay([w0 / Q, 0], [1, w0 / Q, w0 ** 2], ww)
i = np.argmin(abs(ww - w0))
check("resonator group delay at centre = 2Q/w0 [ns]", gd[i] * 1e9, 2 * Q / w0 * 1e9, 1e-3)

# --- minimum phase vs all-pass -----------------------------------------------------------------
ww = np.logspace(-2, 2, 1001)
_, hm = signal.freqs([1, 1], [1, 2], worN=ww)      # zero at -1 (min phase)
_, hn = signal.freqs([-1, 1], [1, 2], worN=ww)     # zero at +1 (non-min phase)
check("same magnitude for LHP vs RHP zero", np.max(abs(abs(hm) - abs(hn))), 0, 1e-12)
extra = np.unwrap(np.angle(hn)) - np.unwrap(np.angle(hm))
check("extra phase lag of RHP zero at w=100 [deg] (-> -180)", np.degrees(extra[-1]), -178.85, 0.1)

# --- Bode gain-phase relation for a real pole ----------------------------------------------------
# phi(w0) = (1/pi) * integral_{-inf}^{inf} dA/du * ln(coth(|u|/2)) du,  A = ln|H|, u = ln(w/w0)
def bode_phase(w0):
    def dA_du(u):
        wv = w0 * np.exp(u)
        # A = -0.5 ln(1 + w^2) -> dA/du = -w^2/(1+w^2)
        return -wv ** 2 / (1 + wv ** 2)
    integrand = lambda u: dA_du(u) * np.log(1 / np.tanh(abs(u) / 2))
    v1, _ = integrate.quad(integrand, -40, -1e-12, limit=400)
    v2, _ = integrate.quad(integrand, 1e-12, 40, limit=400)
    return (v1 + v2) / np.pi
for w0_ in [0.3, 1.0, 3.0]:
    check(f"Bode gain-phase integral phase at w={w0_} [deg]", np.degrees(bode_phase(w0_)), np.degrees(-np.arctan(w0_)), 0.05)

# --- final value theorem -----------------------------------------------------------------------------
# step into H(s) = 5/(s+2): y(inf) = lim s->0 s * H(s)/s = 2.5
_, ys = signal.step(signal.lti([5], [1, 2]), T=np.linspace(0, 20, 2001))
check("final value theorem", ys[-1], 2.5, 1e-6)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
