#!/usr/bin/env python3
"""
prop2_ground_wave.py — verification for kb/09-propagation-link-budget/ground-wave-and-lf-mf-propagation.md

Own Python implementation of the ITU-R P.368-10 ground-wave method as realised in NTIA/ITS LFMF
(the P.368-10 "integral software"; algorithm read from github.com/NTIA/LFMF, re-coded here):
  * smooth spherical Earth, effective radius a_e = a0 / (1 - 0.04665 exp(0.005577 Ns)), a0 = 6370 km;
  * surface impedance delta = sqrt(eta - 1) [/eta for vertical pol], eta = eps_r - j sigma/(w eps0);
  * d < 80 / f_MHz^(1/3) km: flat-earth Sommerfeld-Norton attenuation F(p) = 1 + j sqrt(pi) q_i w(q_i)
    (w = Faddeeva function, p = q_i^2 = -j (k d / 2) delta^2 = Norton numerical distance) with first curvature terms;
  * otherwise: Wait/Fock residue series sum_s exp(-j x t_s)/(t_s - q^2) (x height-gain ratios for raised antennas),
    t_s the roots of w1'(t) - q w1(t) = 0 with w1(t) proportional to Ai(t e^{-j 2 pi/3}), q = -j nu delta,
    nu = (a_e k / 2)^(1/3), x = nu d / a_e;
  * reference source: short monopole, 1 kW, 4.77 dBi -> 300 mV/m at 1 km (cymomotive force 300 V).
Validation: the 5 valid reference cases of NTIA LFMF-test-data/LFMF_Examples.csv (embedded below).
Then: field strength vs distance for sea / land / dry ground at 0.2-30 MHz, vertical vs horizontal polarisation,
Norton numerical distance |p| ~ pi d / (lambda x) and Bullington's attenuation approximation, why HF ground wave
dies quickly, MF day/night coverage, Millington mixed path.
"""
import numpy as np
from scipy.special import airy, wofz

ok = True
def check(name, val, lo, hi):
    global ok
    good = lo <= val <= hi
    ok &= good
    print(f"  [{'PASS' if good else 'FAIL'}] {name}: {val:.4g} (expected {lo}..{hi})")

C = 299792458.0; EPS0 = 8.854187817e-12; ETA = 119.9169832 * np.pi; A0 = 6370.0
J = 1j
PH = np.exp(-2j * np.pi / 3)
AKP = [-1.0187929716, -3.2481975822, -4.8200992112, -6.1633073556, -7.3721772550, -8.4884867340, -9.5354490524,
       -10.5276603970, -11.4750666335, -12.3847883718, -13.2636395229]
AK = [-2.3381074105, -4.0879494441, -5.5205698281, -6.7867080901, -7.9441335871, -9.0226508533, -10.0401743416,
      -11.0085243037, -11.9360255632, -12.8287867529, -13.6914890352]


def W(t):
    ai, aip, _, _ = airy(t * PH)
    return ai, PH * aip


def _airy_zero(i, deriv):
    if i <= 11:
        return (AKP if deriv else AK)[i - 1]
    T = 3 * np.pi / 8 * (4 * i - (3 if deriv else 1))
    return -T ** (2 / 3) * (1 + (-7 / 48 if deriv else 5 / 48) * T ** -2)


def root(i, q):
    """i-th root (1-based) of w1'(t) - q w1(t) = 0 by Newton from the q -> 0 or q -> inf asymptote, with continuation."""
    def newton(t, qq, n=60):
        for _ in range(n):
            w, wp = W(t)
            f = wp - qq * w
            fp = t * w - qq * wp
            dt = -f / fp
            t = t + dt
            if abs(dt) < 1e-12 * max(1, abs(t)):
                return t, True
        return t, False
    small = abs(q) ** 3 <= 4 * (i - 1) + 3
    t0 = (_airy_zero(i, True) if small else _airy_zero(i, False)) / PH   # (real root) * e^{+j2pi/3}
    if not small:
        t0 = t0 + 1 / q      # first-order correction from the q -> inf side
    t, good = newton(t0, q)
    if good:
        return t
    t = _airy_zero(i, True) / PH                     # continuation from q = 0
    for s in np.linspace(0, 1, 201)[1:]:
        t, _ = newton(t, q * s, 30)
    return t


def lfmf(h_tx, h_rx, f_mhz, P_w, Ns, d_km, eps, sigma, pol):
    f = f_mhz * 1e6; lam = C / f
    h1 = min(h_tx, h_rx) / 1000; h2 = max(h_tx, h_rx) / 1000
    ae = A0 / (1 - 0.04665 * np.exp(0.005577 * Ns))
    th = d_km / ae
    k = 2 * np.pi * 1000 / lam
    nu = np.cbrt(ae * k / 2)
    eta = eps - J * sigma / (EPS0 * 2 * np.pi * f)
    delta = np.sqrt(eta - 1)
    if pol == 1:
        delta = delta / eta
    q = -nu * J * delta
    if d_km < 80 / np.cbrt(f_mhz):
        qi = (-0.5 + 0.5j) * np.sqrt(k * d_km) * delta
        p = qi * qi
        if abs(q) > 0.1:
            Fp = 1 + np.sqrt(np.pi) * J * qi * wofz(qi)
            fx = Fp + (1 - J * np.sqrt(np.pi * p) - (1 + 2 * p) * Fp) / (4 * q**3)
            fx = fx + (1 - J * np.sqrt(np.pi * p) * (1 - p) - 2 * p + 5 * p**2 / 6 + (p**2 / 2 - 1) * Fp) / (4 * q**6)
        else:
            x = d_km / ae * (k * ae / 2) ** (1 / 3)
            A = [1, -J * np.sqrt(np.pi), -2, J * np.sqrt(np.pi) * (1 + 1 / (4 * q**3)), 4 / 3 * (1 + 1 / (2 * q**3)),
                 -J * np.sqrt(np.pi) / 4 * (1 + 3 / (4 * q**3)), -8 / 15 * (1 + 1 / q**3 + 7 / (32 * q**6)),
                 J * np.sqrt(np.pi) / 6 * (1 + 5 / (4 * q**3) + 27 / (32 * q**6)),
                 16 / 105 * (1 + 3 / (2 * q**3) + 27 / (32 * q**6)),
                 -J * np.sqrt(np.pi) / 24 * (1 + 7 / (4 * q**3) + 5 / (4 * q**6) + 21 / (64 * q**9))]
            fx = sum(A[n] * (np.exp(J * np.pi / 4) * q * np.sqrt(x)) ** n for n in range(10))
        Egw = abs(fx * (1 + J * k * h2 * delta) * (1 + J * k * h1 * delta))
        method = "flat"
    else:
        x = nu * th
        yH, yL = k * h2 / nu, k * h1 / nu
        GW = 0
        for i in range(1, 201):
            t = root(i, q)
            w1, _ = W(t)
            term = 1.0 + 0j
            if h1 > 0:
                term *= W(t - yL)[0] / w1
            if h2 > 0:
                term *= W(t - yH)[0] / w1
            term /= (t - q * q)
            G = term * np.exp(-J * x * t)
            GW += G
            if i > 1 and abs(G / GW) < 5e-4:
                break
        Egw = abs(np.sqrt(x) * (np.sqrt(np.pi / 2) - J * np.sqrt(np.pi / 2)) * GW)
        method = "residue"
    Gt = 10 ** (4.77 / 10)
    E0 = np.sqrt(ETA * P_w * Gt / (4 * np.pi)) / d_km      # mV/m
    E = Egw * E0
    return 60 + 20 * np.log10(E), method, abs(q), abs(p) if method == "flat" else None


print("=== 1. Validation vs NTIA LFMF reference examples (LFMF-test-data/LFMF_Examples.csv, rtn = 0 rows) ===")
REF = [(0, 0, 0.01, 1000, 301, 1000, 15, 0.005, 0, -82.5, "residue"),
       (0, 0, 1, 5000, 301, 5000, 15, 0.005, 1, -387.5, "residue"),
       (5.5, 1.5, 10, 500, 315, 15, 15, 0.005, 0, 7.6, "flat"),
       (1, 1, 0.45, 1000, 315, 3000, 15, 0.005, 1, -129.3, "residue"),
       (10, 10, 30, 10000, 315, 5000, 15, 0.005, 0, -1393.3, "residue")]
for ht, hr, f, P, Ns, d, e, s, pol, Eref, mref in REF:
    E, m, aq, ap = lfmf(ht, hr, f, P, Ns, d, e, s, pol)
    tol = 0.2 if abs(Eref) < 400 else 0.005 * abs(Eref)
    check(f"f={f} MHz d={d} km {'V' if pol else 'H'} ({m}; ref {mref}) E dBuV/m", E, Eref - tol, Eref + tol)

print("\n=== 1b. Internal consistency: flat-earth (Norton + curvature) vs residue series at the switch distance ===")
for f, e, sg in ((1.0, 22, 0.003), (1.0, 70, 5.0), (10.0, 22, 0.003), (0.2, 15, 0.001)):
    dt = 80 / f ** (1 / 3)
    a_ = lfmf(0, 0, f, 1000, 315, dt * 0.999, e, sg, 1)[0]; b_ = lfmf(0, 0, f, 1000, 315, dt * 1.001, e, sg, 1)[0]
    check(f"{f} MHz eps {e} sigma {sg}: jump at {dt:.0f} km (dB)", b_ - a_, -0.1, 0.1)

print("\n=== 2. Field strength (dBuV/m, 1 kW short monopole, ground-level antennas, vertical pol) ===")
grounds = {"sea (avg salinity) 5 S/m, er 70": (70, 5.0), "wet ground 10 mS/m, er 30": (30, 0.01),
           "land 3 mS/m, er 22": (22, 0.003), "medium dry 1 mS/m, er 15": (15, 0.001)}
dists = [10, 30, 100, 300, 1000]
tab = {}
for f in (0.2, 1.0, 3.0, 10.0, 30.0):
    print(f"  f = {f} MHz   (inverse-distance reference: " + ", ".join(f"{d} km {20*np.log10(300e3/d):.1f}" for d in dists) + ")")
    for g, (e, s) in grounds.items():
        row = [lfmf(0, 0, f, 1000, 315, d, e, s, 1)[0] for d in dists]
        tab[(f, g)] = row
        print(f"    {g:32s}: " + "  ".join(f"{v:6.1f}" for v in row))
# sanity: sea 1 MHz 100 km within a few dB of inverse distance (69.5)
check("sea 1 MHz 100 km within 3 dB of inverse-distance 69.5", tab[(1.0, 'sea (avg salinity) 5 S/m, er 70')][2], 66.5, 70.5)
check("land (3 mS/m) 1 MHz 100 km below sea by > 10 dB",
      tab[(1.0, 'sea (avg salinity) 5 S/m, er 70')][2] - tab[(1.0, 'land 3 mS/m, er 22')][2], 10, 40)
check("10 MHz over land: 100 km field much weaker than at 1 MHz (dB)",
      tab[(1.0, 'land 3 mS/m, er 22')][2] - tab[(10.0, 'land 3 mS/m, er 22')][2], 15, 60)

print("\n=== 3. Norton numerical distance and the frequency/conductivity law ===")
for f in (0.5, 1, 3, 10, 30):
    for (e, s, lab) in ((15, 0.001, "1 mS/m"), (22, 0.003, "3 mS/m"), (70, 5.0, "sea")):
        x = s / (2 * np.pi * f * 1e6 * EPS0)
        lam = C / (f * 1e6)
        d = 30e3
        eta = e - J * x
        p = abs(np.pi * d / lam * (eta - 1) / eta**2)
        A_b = (2 + 0.3 * p) / (2 + p + 0.6 * p**2)
        print(f"   {f:4.1f} MHz {lab:7s}: x = sigma/(w eps0) = {x:9.1f}, |p| at 30 km = {p:8.3g}, Bullington A ~ {20*np.log10(A_b):6.1f} dB")
print("   |p| ~ pi d / (lambda |eta|) ~ pi d f^2 eps0 2pi / (c sigma) for x >> eps_r: p grows as f^2 / sigma")
lam = C / 1e6
p1 = np.pi * 30e3 / lam / (0.003 / (2 * np.pi * 1e6 * EPS0))
lam10 = C / 1e7
p10 = np.pi * 30e3 / lam10 / abs(22 - J * 0.003 / (2 * np.pi * 1e7 * EPS0))
print(f"   land 3 mS/m, 30 km: |p| = {p1:.2f} at 1 MHz vs {p10:.1f} at 10 MHz (ratio {p10/p1:.0f}; f^2 law would give 100)")
check("p ratio 10 vs 1 MHz over land (x not >> er at 10 MHz)", p10 / p1, 20, 100)

print("\n=== 4. Vertical vs horizontal polarisation (land 3 mS/m, 1 MHz) ===")
for d in (1, 3, 10, 30):
    Ev = lfmf(0, 0, 1.0, 1000, 315, d, 22, 0.003, 1)[0]; Eh = lfmf(0, 0, 1.0, 1000, 315, d, 22, 0.003, 0)[0]
    print(f"   {d:3d} km: V {Ev:6.1f}  H {Eh:6.1f} dBuV/m  (H - V = {Eh-Ev:6.1f} dB)")
check("H-pol ground wave far weaker at 10 km (dB)", lfmf(0,0,1.0,1000,315,10,22,0.003,1)[0]-lfmf(0,0,1.0,1000,315,10,22,0.003,0)[0], 30, 120)

print("\n=== 5. Coverage: distance at which E falls to 60 dBuV/m (1 mV/m, MW primary service) and 40 dBuV/m ===")
from scipy.optimize import brentq
def dist_to(Etarget, f, e, s, P=1000):
    g = lambda d: lfmf(0, 0, f, P, 315, d, e, s, 1)[0] - Etarget
    try:
        return brentq(g, 1.0, 3000.0)
    except ValueError:
        return np.nan
for f in (0.2, 0.6, 1.0, 1.6, 3.0, 7.0, 14.0):
    out = []
    for g, (e, s) in grounds.items():
        out.append(dist_to(40.0, f, e, s))
    print(f"   {f:4.1f} MHz, 1 kW: 40 dBuV/m reached at " + ", ".join(f"{g.split()[0]} {d:6.0f} km" for g, d in zip(grounds, out)))
d14 = dist_to(40.0, 14.0, 22, 0.003); d1 = dist_to(40.0, 1.0, 22, 0.003)
check("40 dBuV/m range over land: 1 MHz / 14 MHz ratio", d1 / d14, 3, 50)

print("\n=== 6. Millington mixed path (P.368-10 Annex 2): 50 km land (3 mS/m) then 50 km sea, 1 MHz ===")
Eland = lambda d: lfmf(0, 0, 1.0, 1000, 315, d, 22, 0.003, 1)[0]
Esea = lambda d: lfmf(0, 0, 1.0, 1000, 315, d, 70, 5.0, 1)[0]
ER = Eland(50) - Esea(50) + Esea(100)
ET = Esea(50) - Eland(50) + Eland(100)
Em = (ER + ET) / 2
print(f"   all-land 100 km {Eland(100):.1f}, all-sea {Esea(100):.1f}; Millington E_R {ER:.1f}, E_T {ET:.1f} -> mixed {Em:.1f} dBuV/m")
print("   (the 'recovery effect': crossing onto sea raises the field above the all-land value)")
check("Millington mixed between land and sea values", Em, Eland(100), Esea(100))

print("\nALL PASS" if ok else "\nSOME CHECKS FAILED")
