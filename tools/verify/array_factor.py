#!/usr/bin/env python3
"""
array_factor.py — verification for kb/12-phased-arrays/array-factor-linear-arrays.md

Checks (all numerical, no external data):
  1. ULA array-factor closed form sin(N psi/2)/(N sin(psi/2)) equals the brute-force phasor sum.
  2. Half-power beamwidth: numeric vs 0.886 lambda/(N d) (broadside) and vs 0.886 lambda/(N d cos th0) (scanned);
     endfire HPBW vs 2 acos(1 - 0.443 lambda/(N d)).
  3. First-sidelobe level vs N (large-N limit -13.26 dB).
  4. Directivity of an isotropic-element ULA: exact double-sum formula vs direct numerical integration,
     D = N at d = lambda/2 for every scan angle, D ~ 2 N d / lambda broadside, ~4 N d/lambda ordinary endfire,
     Hansen-Woodyard improvement (approx 1.789x for large N).
  5. Directivity with directive elements (cos^q element pattern) for the 8-element 5.8 GHz example.
  6. Array SNR gain: Monte-Carlo coherent combining of N channels with independent receiver noise -> N;
     with taper -> |sum w|^2 / sum|w|^2; spatially white vs isotropic noise field (sinc(kd) correlation).
  7. Worked-example numbers used on the page (5.8 GHz 8-el, 915 MHz 4-el, 433 MHz).

Convention: linear array on the x axis, theta measured from broadside (array normal, z axis),
u = sin(theta) in the x-z plane. Phasor convention e^{+j omega t}: a far-field observation in direction u
sees element n with phase +k x_n u; steering weights w_n = a_n exp(-j k x_n u0).
"""
import numpy as np
from scipy.optimize import brentq
from scipy.integrate import quad, dblquad

c0 = 299792458.0
rng = np.random.default_rng(1)


def af_sum(w, x, u, k):
    """Brute-force array factor sum_n w_n exp(j k x_n u)."""
    return np.exp(1j * k * np.outer(u, x)) @ w


def af_closed(N, psi):
    """Normalised uniform ULA array factor magnitude."""
    psi = np.asarray(psi, dtype=float)
    num = np.sin(N * psi / 2)
    den = N * np.sin(psi / 2)
    out = np.ones_like(psi)
    m = np.abs(den) > 1e-12
    out[m] = num[m] / den[m]
    return out


def directivity_exact(a, x, k, u0=0.0, elem=None):
    """Exact directivity of a linear array along x (isotropic elements) steered to u0 (direction cosine
    w.r.t. x axis == sin(theta) from broadside). Uses the closed-form sphere integral
    int exp(j k s cos gamma) dOmega = 4 pi sinc(k s)."""
    a = np.asarray(a, dtype=complex)
    w = a * np.exp(-1j * k * x * u0)
    num = np.abs(np.sum(a)) ** 2
    dx = x[:, None] - x[None, :]
    S = np.sinc(k * dx / np.pi)  # numpy sinc(x) = sin(pi x)/(pi x)
    den = np.real(np.conj(w)[:, None] * w[None, :] * S).sum()
    # careful with conjugation order: P ∝ sum_m sum_n w_m w_n^* sinc(k(x_m-x_n)); symmetric anyway
    return num / den


def directivity_numeric(w, x, k, pattern_el=None, n_th=721, n_ph=720):
    """Direct numerical integration over the sphere. Array along x; element pattern (power) a function of
    (theta, phi) with theta from z (broadside normal). Returns peak directivity and its direction."""
    th = np.linspace(0, np.pi, n_th)
    ph = np.linspace(0, 2 * np.pi, n_ph, endpoint=False)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    ux = np.sin(TH) * np.cos(PH)  # direction cosine along array axis
    AF = np.exp(1j * k * ux[..., None] * x[None, None, :]) @ w
    U = np.abs(AF) ** 2
    if pattern_el is not None:
        U = U * pattern_el(TH, PH)
    dth = th[1] - th[0]
    dph = ph[1] - ph[0]
    wts = np.ones_like(th)
    wts[0] = wts[-1] = 0.5  # trapezoid in theta (non-periodic), rectangle in phi (periodic)
    P = np.sum(U * np.sin(TH) * wts[:, None]) * dth * dph
    return 4 * np.pi * U.max() / P


def hpbw_numeric(N, d_lam, th0_deg=0.0):
    """Numeric HPBW (deg) of uniform ULA in the scan plane."""
    k = 2 * np.pi
    u0 = np.sin(np.radians(th0_deg))
    th0 = np.radians(th0_deg)
    f = lambda th: af_closed(N, np.array([k * d_lam * (np.sin(th) - u0)]))[0] ** 2 - 0.5
    th = np.linspace(-np.pi / 2, np.pi / 2, 200001)
    P = af_closed(N, k * d_lam * (np.sin(th) - u0)) ** 2 - 0.5
    i0 = np.argmin(np.abs(th - th0))
    # walk right and left from the peak to the first sign change
    ir = i0
    while ir < len(th) - 1 and P[ir] > 0:
        ir += 1
    il = i0
    while il > 0 and P[il] > 0:
        il -= 1
    hi = brentq(f, th[ir - 1], th[ir]) if P[ir] <= 0 else np.pi / 2
    lo = brentq(f, th[il], th[il + 1]) if P[il] <= 0 else -np.pi / 2
    return np.degrees(hi - lo)


def first_sidelobe_db(N):
    psi = np.linspace(2 * np.pi / N + 1e-6, 4 * np.pi / N - 1e-6, 20001)
    return 20 * np.log10(np.abs(af_closed(N, psi)).max())


print("=" * 78)
print("1. Closed form vs brute-force sum")
for N in (4, 8, 16):
    k = 2 * np.pi  # lambda = 1
    d = 0.5
    x = np.arange(N) * d
    u = np.linspace(-1, 1, 2001)
    u0 = np.sin(np.radians(25))
    w = np.exp(-1j * k * x * u0)
    brute = np.abs(af_sum(w, x, u, k)) / N
    closed = np.abs(af_closed(N, k * d * (u - u0)))
    print(f"  N={N:2d}: max |brute - closed| = {np.max(np.abs(brute - closed)):.2e}")

print("=" * 78)
print("2. Half-power beamwidth")
for N in (4, 8, 16, 32, 100):
    for th0 in (0, 30, 60):
        num = hpbw_numeric(N, 0.5, th0)
        approx = np.degrees(0.886 / (N * 0.5 * np.cos(np.radians(th0))))
        print(f"  N={N:3d} d=0.5λ th0={th0:2d}°: numeric {num:6.2f}°  0.886λ/(Nd cosθ0) {approx:6.2f}°  ratio {num/approx:.3f}")
# endfire (ordinary): beta = -kd  ->  psi = kd(u - 1) in terms of u = cos(angle from array axis)
print("  Endfire (ordinary, peak on array axis), d = λ/4:")
for N in (8, 16, 32):
    k = 2 * np.pi; d = 0.25
    f = lambda g: af_closed(N, np.array([k * d * (np.cos(g) - 1)]))[0] ** 2 - 0.5
    g3 = brentq(f, 1e-6, np.arccos(max(-1, 1 - 1 / (N * d))) - 1e-9)
    approx = 2 * np.degrees(np.arccos(1 - 0.443 / (N * d)))
    print(f"    N={N:2d}: numeric HPBW {2*np.degrees(g3):6.2f}°, 2acos(1-0.443λ/Nd) {approx:6.2f}°")

print("=" * 78)
print("3. First sidelobe level of uniform ULA")
for N in (2, 3, 4, 5, 6, 8, 10, 16, 32, 100, 1000):
    if N < 3:
        print(f"  N={N:4d}: no sidelobe inside one period (only grating lobes)")
        continue
    print(f"  N={N:4d}: {first_sidelobe_db(N):7.2f} dB")
print(f"  large-N limit (sinc first sidelobe): {20*np.log10(abs(np.sinc(1.4303)) ):.2f} dB")

print("=" * 78)
print("4. Directivity of isotropic-element ULA (exact double sum vs numeric integration)")
k = 2 * np.pi
for N, d, th0 in [(8, 0.5, 0), (8, 0.5, 30), (8, 0.5, 60), (8, 0.5, 90), (8, 0.25, 0), (8, 0.7, 0),
                  (8, 0.7, 45), (8, 1.0, 0), (16, 0.5, 45), (10, 0.25, 0)]:
    x = np.arange(N) * d
    u0 = np.sin(np.radians(th0))
    De = directivity_exact(np.ones(N), x, k, u0)
    Dn = directivity_numeric(np.exp(-1j * k * x * u0), x, k)
    print(f"  N={N:2d} d={d:4.2f}λ θ0={th0:2d}°: exact D={De:7.3f} ({10*np.log10(De):5.2f} dB)  numeric {Dn:7.3f}   2Nd/λ={2*N*d:5.2f}")
print("  Broadside, large N: D vs 2Nd/λ (d=0.25λ,0.4λ):")
for N in (10, 50, 200):
    for d in (0.25, 0.4):
        x = np.arange(N) * d
        De = directivity_exact(np.ones(N), x, k, 0)
        print(f"    N={N:3d} d={d}: D={De:8.2f}  2Nd/λ={2*N*d:7.2f}")
print("  Endfire (ordinary β=-kd, d=λ/4) vs 4Nd/λ, and Hansen–Woodyard (β=-(kd+2.94/N)) and (β=-(kd+π/N)):")
for N in (5, 10, 20, 50, 100):
    d = 0.25
    x = np.arange(N) * d
    # endfire: steering direction cosine u0 = 1 along array axis.
    De_ord = directivity_exact(np.ones(N), x, k, 1.0)
    # HW: extra progressive phase; weights a_n = exp(-j n delta) with steering u0=1
    res = []
    for extra in (2.94 / N, np.pi / N):
        a = np.exp(-1j * np.arange(N) * extra)
        w = a * np.exp(-1j * k * x * 1.0)
        num = np.abs(np.sum(w * np.exp(1j * k * x * 1.0))) ** 2  # field at endfire u=1
        dx = x[:, None] - x[None, :]
        den = np.real(np.conj(w)[:, None] * w[None, :] * np.sinc(k * dx / np.pi)).sum()
        res.append(num / den)
    print(f"    N={N:3d}: ord D={De_ord:7.2f} (4Nd/λ={4*N*d:6.1f}); HW(2.94/N) D={res[0]:7.2f} ratio {res[0]/De_ord:.3f}; HW(π/N) D={res[1]:7.2f} ratio {res[1]/De_ord:.3f}")

print("=" * 78)
print("5. 8-element 5.8 GHz ULA of patch-like elements (element power pattern cos^q(theta), forward hemisphere)")
f = 5.8e9
lam = c0 / f
print(f"  λ = {lam*1e3:.2f} mm, λ/2 = {lam/2*1e3:.2f} mm")
N = 8
x = np.arange(N) * 0.5
for q in (0, 1, 1.5, 2):
    if q == 0:
        el = None
        label = "isotropic"
    else:
        el = (lambda qq: (lambda TH, PH: np.where(TH < np.pi / 2, np.cos(TH) ** qq, 0.0)))(q)
        label = f"cos^{q}"
    Dn = directivity_numeric(np.ones(N, dtype=complex), x, 2 * np.pi, el)
    # element alone
    if el is not None:
        De1 = directivity_numeric(np.ones(1, dtype=complex), np.zeros(1), 2 * np.pi, el)
    else:
        De1 = 1.0
    print(f"  element {label:9s}: D_el = {10*np.log10(De1):5.2f} dBi, array D = {10*np.log10(Dn):5.2f} dBi, "
          f"10log N + D_el = {10*np.log10(N)+10*np.log10(De1):5.2f} dBi")
print(f"  HPBW broadside = {hpbw_numeric(8,0.5,0):.2f}° ; scanned 30° = {hpbw_numeric(8,0.5,30):.2f}° ; 45° = {hpbw_numeric(8,0.5,45):.2f}°")
print(f"  first nulls at sinθ = ±1/(N d/λ) = ±{1/(8*0.5):.3f} -> ±{np.degrees(np.arcsin(0.25)):.2f}°")
print(f"  first sidelobe = {first_sidelobe_db(8):.2f} dB, at θ ≈ ±{np.degrees(np.arcsin(3/8)):.1f}° (approx ψ=3π/N)")

print("=" * 78)
print("6. SNR (array) gain by Monte Carlo")
for N in (2, 4, 5, 8):
    M = 200000
    s = np.exp(1j * rng.uniform(0, 2 * np.pi, M))  # unit-power signal, identical (after steering) on all channels
    n = (rng.standard_normal((M, N)) + 1j * rng.standard_normal((M, N))) / np.sqrt(2)  # unit-power noise each
    snr_in = 1.0
    y = s[:, None] + n
    comb = y.sum(axis=1)
    sig_p = np.abs(N * s) ** 2
    noise_p = np.mean(np.abs(n.sum(axis=1)) ** 2)
    print(f"  N={N}: output SNR/input SNR = {np.mean(sig_p)/noise_p:.3f} (expected {N}) -> {10*np.log10(np.mean(sig_p)/noise_p):.2f} dB")
# tapered weights
N = 8
w = np.hamming(N)
g = np.abs(w.sum()) ** 2 / np.sum(w ** 2)
print(f"  N=8 Hamming taper: SNR gain = |Σw|²/Σw² = {g:.3f} ({10*np.log10(g):.2f} dB) vs uniform 9.03 dB; taper efficiency {g/N:.3f}")
# isotropic noise field: correlation between isotropic elements is sinc(k d)
print("  Isotropic (3-D uniform) noise field, broadside steering, N=8: array gain vs d (should equal directivity):")
for d in (0.2, 0.3, 0.5, 0.7):
    x = np.arange(N) * d
    R = np.sinc(2 * np.pi * (x[:, None] - x[None, :]) / np.pi)
    w = np.ones(N)
    G_iso = (np.abs(w.sum()) ** 2) / (w @ R @ w)
    D = directivity_exact(np.ones(N), x, 2 * np.pi, 0)
    print(f"    d={d}λ: array gain vs isotropic noise = {G_iso:6.3f}, directivity = {D:6.3f}, white-noise gain = {N}")

print("=" * 78)
print("7. Worked-example numbers")
for f, name in [(433e6, "433 MHz"), (915e6, "915 MHz"), (2.45e9, "2.45 GHz"), (5.8e9, "5.8 GHz"), (10.25e9, "10.25 GHz (Phaser)")]:
    lam = c0 / f
    print(f"  {name:18s}: λ = {lam*100:7.2f} cm, λ/2 = {lam/2*100:6.2f} cm")
# 915 MHz 4 dipoles (half-wave, collinear axis along z? -> use side-by-side parallel dipoles along z, array along x)
f = 915e6; lam = c0 / f; N = 4
el = lambda TH, PH: (np.cos(np.pi / 2 * (np.sin(TH) * np.sin(PH))) / np.sqrt(np.maximum(1e-12, 1 - (np.sin(TH) * np.sin(PH)) ** 2))) ** 2
# dipole along y axis (horizontal, perpendicular to array axis x): angle to dipole axis gamma: cos(gamma) = sinθ sinφ
x = np.arange(N) * 0.5
D4 = directivity_numeric(np.ones(N, dtype=complex), x, 2 * np.pi, el)
D1 = directivity_numeric(np.ones(1, dtype=complex), np.zeros(1), 2 * np.pi, el)
print(f"  915 MHz, 4 parallel λ/2 dipoles side-by-side at λ/2 ({lam/2*1000:.0f} mm), no reflector: D = {10*np.log10(D4):.2f} dBi (single dipole {10*np.log10(D1):.2f} dBi)")
print(f"     aperture length N d = {N*lam/2*100:.1f} cm, HPBW (array plane) = {hpbw_numeric(4,0.5,0):.1f}°")
# with ideal reflector (half-space cos-like), approximate by element pattern doubling in forward hemisphere: model as dipole*2 sin^2(kh cos) with h=λ/4
el_ref = lambda TH, PH: el(TH, PH) * (np.sin(np.pi / 2 * np.cos(TH)) ** 2) * (TH < np.pi / 2) * 4
D4r = directivity_numeric(np.ones(N, dtype=complex), x, 2 * np.pi, el_ref)
D1r = directivity_numeric(np.ones(1, dtype=complex), np.zeros(1), 2 * np.pi, el_ref)
print(f"     same over an infinite reflector at λ/4: single {10*np.log10(D1r):.2f} dBi, array {10*np.log10(D4r):.2f} dBi")
# TX EIRP scaling
for N in (1, 4, 8, 16):
    P_el_dBm = 20.0
    eirp = P_el_dBm + 10 * np.log10(N) + 10 * np.log10(N) + 5.0
    print(f"  TX: {N:2d} elements × 20 dBm each, 5 dBi elements: EIRP ≈ {eirp:.1f} dBm (grows as N²)")
print("done")
