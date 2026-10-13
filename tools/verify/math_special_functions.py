#!/usr/bin/env python3
"""Verification for kb/00-math-foundations/special-functions-bessel-sinc.md

Checks: sinc integral/nulls; Bessel J_n FM sideband identities (sum of squares = 1,
carrier null 2.4048, Carson's rule power fraction); jinc/Airy pattern (null 1.22 lambda/D,
HPBW 1.03 lambda/D, sidelobe -17.6 dB); Fresnel integrals limits and knife-edge loss
(ITU-R P.526 eq. 30 exact vs eq. 31 approximation; J(0) = 6.02 dB); first Fresnel zone
radius; Chebyshev polynomial forms, Chebyshev filter ripple, Dolph-Chebyshev 8-element
30 dB array (equal sidelobes); Legendre orthogonality; spherical Bessel/Hankel; I0 in
Rician; Gamma(1/2).
Run: python3 tools/verify/math_special_functions.py
"""
import numpy as np
from scipy import special, integrate, signal, optimize

ok_all = True


def check(name, got, want, tol):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol})")


# --- sinc ------------------------------------------------------------------------------
val, _ = integrate.quad(lambda x: np.sinc(x), -2000, 2000, limit=20000)
check("integral of sinc(x) dx = 1", val, 1.0, 1e-3)
check("sinc(3) = 0", np.sinc(3.0), 0.0, 1e-15)

# --- Bessel and FM -------------------------------------------------------------------------
for beta in [0.5, 2.0, 5.0]:
    n = np.arange(-60, 61)
    check(f"FM beta={beta}: sum J_n^2 = 1", np.sum(special.jv(n, beta) ** 2), 1.0, 1e-12)
check("first zero of J0 (carrier null)", special.jn_zeros(0, 1)[0], 2.40483, 1e-5)
check("first zero of J1 (first-sideband null)", special.jn_zeros(1, 1)[0], 3.83171, 1e-5)
for beta in [1.0, 5.0]:
    nmax = int(np.floor(beta + 1))
    n = np.arange(-nmax, nmax + 1)
    frac = np.sum(special.jv(n, beta) ** 2)
    check(f"Carson (|n| <= beta+1) power fraction, beta={beta} (>= 0.98)", float(frac >= 0.98), 1.0, 0)
    print(f"      beta={beta}: fraction within Carson bandwidth = {frac:.4f}")
# numeric FM spectrum check: FFT of cos(wc t + beta sin wm t)
fs, N = 1024, 1024
t = np.arange(N) / fs
beta, km, kc = 2.0, 8, 200
x = np.exp(1j * (2 * np.pi * kc * t + beta * np.sin(2 * np.pi * km * t)))
X = np.fft.fft(x) / N
check("FM line at fc amplitude = |J0(2)|", abs(X[kc]), abs(special.j0(2.0)), 1e-12)
check("FM line at fc+2fm amplitude = |J2(2)|", abs(X[kc + 2 * km]), abs(special.jv(2, 2.0)), 1e-12)

# --- jinc / circular aperture ---------------------------------------------------------------------
jinc = lambda u: np.where(u == 0, 1.0, 2 * special.j1(u) / np.where(u == 0, 1, u))
x_null = special.jn_zeros(1, 1)[0]
check("circular aperture first null: sin(theta) = 1.2197 lambda/D", x_null / np.pi, 1.2197, 1e-4)
x_hp = optimize.brentq(lambda u: jinc(u) ** 2 - 0.5, 0.5, 3.0)
check("circular aperture HPBW = 1.029 lambda/D (small angle)", 2 * x_hp / np.pi, 1.029, 1e-3)
u = np.linspace(x_null + 1e-6, special.jn_zeros(1, 2)[1], 20001)
check("circular aperture first sidelobe [dB]", 20 * np.log10(np.max(abs(jinc(u)))), -17.57, 0.01)

# --- Fresnel integrals and knife-edge -----------------------------------------------------------------
S, Cf = special.fresnel(50.0)
check("C(inf) -> 0.5", Cf, 0.5, 0.01)
check("S(inf) -> 0.5", S, 0.5, 0.01)
def J_exact(nu):
    S, C = special.fresnel(nu)
    return -20 * np.log10(np.sqrt((1 - C - S) ** 2 + (C - S) ** 2) / 2)
def J_approx(nu):
    return 6.9 + 20 * np.log10(np.sqrt((nu - 0.1) ** 2 + 1) + nu - 0.1)
check("knife-edge J(0) (grazing) = 6.02 dB", J_exact(0.0), 6.0206, 1e-3)
for nu in [-0.5, 0.0, 1.0, 2.4, 5.0]:
    check(f"ITU approx vs exact J({nu}) [dB]", J_approx(nu), J_exact(nu), 0.6)
check("J(nu) ~ 0 near nu = -0.78 (approx formula)", J_approx(-0.78), 0.0, 0.05)
# first Fresnel zone radius at midpoint of 10 km path, 433 MHz
lam = 299792458 / 433e6
r1 = np.sqrt(lam * 5e3 * 5e3 / 10e3)
check("first Fresnel zone radius, 10 km @ 433 MHz, midpoint [m]", r1, 41.6, 0.1)
# nu for an obstacle 20 m above LOS at the midpoint
nu = 20 * np.sqrt(2 / lam * (1 / 5e3 + 1 / 5e3))
check("nu for h = 20 m at midpoint (= sqrt2 h/r1)", nu, np.sqrt(2) * 20 / r1, 1e-9)
print(f"      nu = {nu:.3f} -> knife-edge loss J = {J_exact(nu):.2f} dB")

# --- Chebyshev polynomials -------------------------------------------------------------------------------
for n in [3, 5, 8]:
    xs = np.linspace(-1, 1, 101)
    check(f"T_{n}(x) = cos(n arccos x) on [-1,1]", np.max(abs(special.eval_chebyt(n, xs) - np.cos(n * np.arccos(xs)))), 0, 1e-10)
    xo = 1.7
    check(f"T_{n}(1.7) = cosh(n arccosh 1.7)", special.eval_chebyt(n, xo), np.cosh(n * np.arccosh(xo)), 1e-8 * np.cosh(n * np.arccosh(xo)))
# Chebyshev type-I filter: |H|^2 = 1/(1 + eps^2 T_n^2(w/wc)); ripple 0.5 dB -> eps
rip = 0.5
eps = np.sqrt(10 ** (rip / 10) - 1)
check("0.5 dB ripple -> epsilon", eps, 0.3493, 1e-4)
b, a = signal.cheby1(5, rip, 1.0, analog=True)
w = np.array([0.3, 0.8, 1.0, 2.0])
_, h = signal.freqs(b, a, worN=w)
check("cheby1 n=5 matches 1/(1+eps^2 T5^2) at w=2", abs(h[3]) ** 2, 1 / (1 + eps ** 2 * special.eval_chebyt(5, 2.0) ** 2), 1e-9)
check("cheby1 n=5 attenuation at 2 wc [dB]", -10 * np.log10(abs(h[3]) ** 2), 10 * np.log10(1 + eps ** 2 * special.eval_chebyt(5, 2.0) ** 2), 1e-6)
print(f"      Chebyshev 0.5 dB ripple n=5: {-10*np.log10(abs(h[3])**2):.1f} dB at 2x cutoff")
# Dolph-Chebyshev array, N = 8, 30 dB sidelobes, d = lambda/2
Nel, SLL = 8, 30
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    wts = signal.windows.chebwin(Nel, at=SLL)
th = np.linspace(0, np.pi, 200001)
psi = np.pi * np.cos(th)
AF = np.abs(np.exp(1j * np.outer(psi, np.arange(Nel))) @ wts)
AF /= AF.max()
AFdB = 20 * np.log10(AF + 1e-15)
from scipy.signal import find_peaks
pk, _ = find_peaks(AFdB)
side = AFdB[pk][AFdB[pk] < -1]
check("Dolph-Chebyshev 8 el: highest sidelobe [dB]", side.max(), -30.0, 0.05)
check("Dolph-Chebyshev 8 el: sidelobes equal (spread) [dB]", side.max() - side.min(), 0.0, 0.1)
x0 = np.cosh(np.arccosh(10 ** (SLL / 20)) / (Nel - 1))
check("Dolph parameter x0 = cosh(arccosh(R)/(N-1)) for R=31.62, N=8", x0, 1.1807, 1e-3)

# --- Legendre -----------------------------------------------------------------------------------------------
for m_, n_ in [(2, 2), (2, 3), (4, 4)]:
    v, _ = integrate.quad(lambda x: special.eval_legendre(m_, x) * special.eval_legendre(n_, x), -1, 1)
    check(f"int P{m_} P{n_} = 2/(2n+1) delta", v, (2 / (2 * n_ + 1)) if m_ == n_ else 0.0, 1e-10)

# --- spherical Bessel / Hankel -----------------------------------------------------------------------------------
xx = np.linspace(0.5, 20, 50)
check("j0(x) = sin x / x", np.max(abs(special.spherical_jn(0, xx) - np.sin(xx) / xx)), 0, 1e-12)
h2 = special.spherical_jn(0, xx) - 1j * special.spherical_yn(0, xx)
check("h0^(2)(x) = j e^{-jx}/x (outgoing wave, e^{jwt})", np.max(abs(h2 - 1j * np.exp(-1j * xx) / xx)), 0, 1e-12)

# --- modified Bessel I0 and Gamma ---------------------------------------------------------------------------------
check("I0(0) = 1", special.i0(0.0), 1.0, 1e-15)
check("I0(x) ~ e^x/sqrt(2 pi x) at x=50 (ratio)", special.i0(50.0) / (np.exp(50) / np.sqrt(2 * np.pi * 50)), 1.0, 3e-3)
check("Gamma(1/2) = sqrt(pi)", special.gamma(0.5), np.sqrt(np.pi), 1e-14)

# --- page examples ------------------------------------------------------------------------------------------------
xh = 866 / 500
check("5th-order Butterworth at 866/500 [dB]", 10 * np.log10(1 + xh ** 10), 23.87, 0.01)
check("5th-order 0.5 dB Chebyshev at 866/500 [dB]", 10 * np.log10(1 + eps ** 2 * special.eval_chebyt(5, xh) ** 2), 34.62, 0.01)
check("Dolph 8-el 30 dB taper efficiency [dB]", 10 * np.log10(wts.sum() ** 2 / (Nel * (wts ** 2).sum())), -0.749, 0.005)
check("deep-shadow knife edge J(10) ~ 20log(sqrt2 pi nu)", J_exact(10.0), 20 * np.log10(np.sqrt(2) * np.pi * 10), 0.01)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
