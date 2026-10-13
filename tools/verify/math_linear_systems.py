#!/usr/bin/env python3
"""Verification for kb/00-math-foundations/linear-systems-convolution.md

Checks: convolution of a pulse with an RC impulse response vs analytic result; FFT vs
direct convolution; Hilbert transform of cos = sin; causality <-> Hilbert pair of Re/Im
of H(jw) for an RC low-pass; Kramers-Kronig integral reproduces eps' of a Debye model
from eps''; Djordjevic-Sarkar wideband FR-4 model: eps'' ~= (pi/2)/ln10 x (decay of eps'
per decade) and impulse response causal, while a 'constant eps', constant tan-delta'
model has a large non-causal (t<0) response; waveguide dispersion vp*vg = c^2;
BIBO stability integral.
Run: python3 tools/verify/math_linear_systems.py
"""
import numpy as np
from scipy import signal, integrate

ok_all = True


def check(name, got, want, tol):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol})")


# --- convolution: rectangular pulse (width T) through RC (tau) --------------------------
tau, T = 1e-6, 3e-6
dt = 1e-9
t = np.arange(0, 12e-6, dt)
x = ((t >= 0) & (t < T)).astype(float)
h = np.exp(-t / tau) / tau          # RC impulse response (unit DC gain)
y = np.convolve(x, h)[: len(t)] * dt
y_exact = np.where(t < T, 1 - np.exp(-t / tau), (1 - np.exp(-T / tau)) * np.exp(-(t - T) / tau))
check("pulse * RC impulse response vs analytic (max err)", np.max(abs(y - y_exact)), 0, 2e-3)
check("BIBO: integral |h| dt for RC = 1", np.sum(abs(h)) * dt, 1.0, 2e-3)

# --- FFT convolution == direct -------------------------------------------------------------
rng = np.random.default_rng(3)
a, b = rng.standard_normal(300), rng.standard_normal(200)
check("fftconvolve == convolve", np.max(abs(signal.fftconvolve(a, b) - np.convolve(a, b))), 0, 1e-10)

# --- Hilbert transform ---------------------------------------------------------------------------
n = np.arange(4096)
xc = np.cos(2 * np.pi * 64 * n / 4096)
hx = np.imag(signal.hilbert(xc))
check("Hilbert{cos} = sin (max err)", np.max(abs(hx - np.sin(2 * np.pi * 64 * n / 4096))), 0, 1e-10)

# --- causality: Re and Im of H(jw) are a Hilbert pair ----------------------------------------------
# For causal real h(t): H_I(w) = -Hilbert{H_R(w)} (with the e^{-jwt} Fourier convention)
N = 2 ** 16
tt = np.arange(N) * dt
hc = np.exp(-tt / tau) / tau * dt       # sampled causal impulse response
H = np.fft.fft(hc)
HR, HI = H.real, H.imag
# discrete Hilbert via FFT over the frequency index (periodic): HI = -H{HR}
HI_from_HR = -np.imag(signal.hilbert(HR))
check("causal h: Im H = -Hilbert(Re H) (rel max err)", np.max(abs(HI_from_HR - HI)) / np.max(abs(HI)), 0, 2e-2)

# --- Kramers-Kronig for a Debye model ---------------------------------------------------------------
eps_inf, deps, w0 = 4.2, 1.0, 2 * np.pi * 1e6
eps = lambda w: eps_inf + deps / (1 + 1j * w / w0)
epp = lambda w: -eps(w).imag                      # eps'' >= 0 with e^{+jwt}
# KK: eps'(w) - eps_inf = (2/pi) P int_0^inf  w' eps''(w') / (w'^2 - w^2) dw'
def kk_real(w):
    # work in normalised frequency x = w'/w0 to keep quad well-scaled
    xw = w / w0
    eppx = lambda x: epp(x * w0)
    g = lambda x: x * eppx(x) / (x + xw)            # integrand = g/(x - xw)
    v1, _ = integrate.quad(g, 0, 2 * xw, weight='cauchy', wvar=xw, limit=400)
    v2, _ = integrate.quad(lambda x: x * eppx(x) / (x ** 2 - xw ** 2), 2 * xw, np.inf, limit=400)
    return eps_inf + 2 / np.pi * (v1 + v2)
for f_ in [1e5, 1e6, 1e7]:
    w = 2 * np.pi * f_
    check(f"Debye: KK-reconstructed eps' at {f_:.0e} Hz", kk_real(w), eps(w).real, 1e-4)

# --- Djordjevic-Sarkar wideband FR-4 model (IEEE T-EMC 43(4) 2001, eq. 5) --------------------------
m1, m2 = 4.0, 12.0        # w1 = 10^m1, w2 = 10^m2 rad/s
slope = 0.14              # decay of eps' per decade  (= deps/(m2 - m1))
eps_inf_ds = 4.27
w1, w2 = 10 ** m1, 10 ** m2
def eps_ds(w):
    return eps_inf_ds + slope / np.log(10) * np.log((w2 + 1j * w) / (w1 + 1j * w))
w_mid = 2 * np.pi * 1e8   # 100 MHz, deep inside [w1, w2]
check("D-S: eps'' ~= (pi/2)/ln10 * slope", -eps_ds(w_mid).imag, np.pi / 2 / np.log(10) * slope, 2e-3)
check("D-S: eps' decays 'slope' per decade", eps_ds(w_mid).real - eps_ds(10 * w_mid).real, slope, 1e-3)
print(f"      D-S model at 100 MHz: eps'={eps_ds(w_mid).real:.3f}, tan d={-eps_ds(w_mid).imag/eps_ds(w_mid).real:.4f};"
      f" at 1 GHz: eps'={eps_ds(2*np.pi*1e9).real:.3f}; at 10 GHz: eps'={eps_ds(2*np.pi*1e10).real:.3f}")

# causality test of chi(w) = eps(w) - eps(inf) via inverse FFT on a symmetric frequency grid
def impulse_response(chi_fun, fmax=2e12, N=2 ** 18):
    df = 2 * fmax / N
    f = np.fft.fftfreq(N, 1 / (2 * fmax))
    w = 2 * np.pi * f
    X = chi_fun(w)
    # enforce Hermitian symmetry: X(-w) = conj X(w) (true for physical models)
    x = np.fft.ifft(X) * N * df
    t = np.fft.fftfreq(N, df)
    return t, x.real
t_, g_ds = impulse_response(lambda w: np.where(w == 0, eps_ds(1e-3).real - eps_inf_ds, eps_ds(np.abs(w)).real - eps_inf_ds - 1j * np.sign(w) * (-eps_ds(np.abs(w)).imag)))
neg = np.sum(g_ds[t_ < -1e-12] ** 2)
tot = np.sum(g_ds ** 2)
check("D-S model: fraction of impulse-response energy at t<0", neg / tot, 0, 0.02)
# constant eps' = 4.4, constant tan d = 0.02 over all frequencies ("two numbers" model)
epsc, tand = 4.4, 0.02
chi_c = lambda w: np.where(w == 0, 0.0, (epsc - 1) - 1j * np.sign(w) * epsc * tand)
t_, g_c = impulse_response(chi_c)
# remove the instantaneous (delta) part (constant real part) before judging causality:
g_c_disp = g_c.copy()
i0 = np.argmin(abs(t_))
g_c_disp[i0] = 0
neg_c = np.sum(g_c_disp[t_ < 0] ** 2) / np.sum(g_c_disp ** 2)
check("constant-eps'/constant-tan d model: ~half its dispersive response at t<0 (non-causal)", neg_c, 0.5, 0.05)

# --- waveguide dispersion: vp * vg = c^2 --------------------------------------------------------------
c = 299792458.0
a_wg = 22.86e-3          # WR-90 broad wall
fc = c / (2 * a_wg)
f = np.linspace(8e9, 12e9, 2001)
beta = 2 * np.pi / c * np.sqrt(f ** 2 - fc ** 2)
w = 2 * np.pi * f
vp = w / beta
vg = np.gradient(w, beta)
check("WR-90 TE10 cutoff [GHz]", fc / 1e9, 6.557, 1e-3)
check("vp*vg/c^2 at 10 GHz", (vp * vg)[1000] / c ** 2, 1.0, 1e-4)
check("vg/c at 10 GHz", vg[1000] / c, np.sqrt(1 - (fc / 10e9) ** 2), 1e-4)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
