#!/usr/bin/env python3
"""W5-S9 checks for kb/12-phased-arrays/diy-phased-array-projects.md section
"Printed series-fed patch and comb-line arrays".

Run:  python3 tools/verify/s9_series_fed_squint.py   (<1 s)

1. Microstrip eps_eff (Hammerstad-Jensen quasi-static, no dispersion) and patch length for RO4350B @24 GHz,
   RO3003 @60.5/78.5 GHz.
2. Travelling-wave (end-fed, matched load) series array with d = lambda_g0: beam angle
   sin(theta) = sqrt(eps_eff)*(1 - f0/f); checked against the array-factor peak; squint across the
   SG 24.00-24.25, 57-64 and 76-81 GHz bands.
3. Centre-fed (two halves fed in phase) array: no squint, gain drop at band edges instead.
4. Broadside reflection build-up: N element reflections add in phase at f0 (Hayashi et al. 2011);
   detuning d slightly from lambda_g0 tilts the beam and spreads the reflection phases.
5. Travelling-wave taper: fraction of the remaining power each element must radiate for a -25 dB
   Chebyshev amplitude with 5 % of the power left for the load.
6. Feed-line dielectric loss (FR-4 vs RO3003 vs RO4350B) and a 24 GHz 8-patch column (HPBW, length).
"""
import numpy as np

c = 299_792_458.0
ok_all = True
db = lambda x: 10 * np.log10(x)


def check(name, got, want, tol):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.5g}, expected {want:.5g} (tol {tol})")


def eeff(er, w_h):
    a = 1 + (1 / 49) * np.log((w_h**4 + (w_h / 52) ** 2) / (w_h**4 + 0.432)) + (1 / 18.7) * np.log(1 + (w_h / 18.1) ** 3)
    b = 0.564 * ((er - 0.9) / (er + 3)) ** 0.053
    return (er + 1) / 2 + (er - 1) / 2 * (1 + 10 / w_h) ** (-a * b)


def patch(er, h, f):
    W = c / (2 * f) * np.sqrt(2 / (er + 1))
    ee = eeff(er, W / h)
    dL = 0.412 * h * (ee + 0.3) * (W / h + 0.264) / ((ee - 0.258) * (W / h + 0.8))
    return W, c / (2 * f * np.sqrt(ee)) - 2 * dL, ee


print("=" * 78)
print("1. Substrates, feed-line eps_eff and patch sizes")
cases = (("24.125 GHz RO4350B er 3.66, h 0.254 mm, line w/h 2.2", 24.125e9, 3.66, 0.254e-3, 2.2),
         ("60.5 GHz RO3003 er 3.00, h 0.127 mm, line w/h 2.5", 60.5e9, 3.00, 0.127e-3, 2.5),
         ("78.5 GHz RO3003 er 3.00, h 0.127 mm, line w/h 2.5", 78.5e9, 3.00, 0.127e-3, 2.5))
EE = {}
for lab, f, er, h, wh in cases:
    ee = eeff(er, wh)
    W, L, eep = patch(er, h, f)
    EE[f] = ee
    print(f"    {lab}: line eps_eff {ee:.3f}, lambda_g {c/(f*np.sqrt(ee))*1e3:.2f} mm (lambda0 {c/f*1e3:.2f} mm); patch W {W*1e3:.2f} mm, L {L*1e3:.2f} mm")

print("=" * 78)
print("2. Travelling-wave series array, d = lambda_g0: beam squint")


def af_peak(f, f0, ee, N=12, d_scale=1.0):
    lam_g0 = c / (f0 * np.sqrt(ee))
    d = d_scale * lam_g0
    beta = 2 * np.pi * f * np.sqrt(ee) / c
    k0 = 2 * np.pi * f / c
    th = np.radians(np.linspace(-60, 60, 120001))
    n = np.arange(N)[:, None]
    af = np.abs(np.sum(np.exp(1j * n * (k0 * d * np.sin(th) - beta * d)), axis=0))
    return np.degrees(th[np.argmax(af)])


for (lab, f0, er, h, wh), (b_lo, b_hi) in zip(cases, ((24.0e9, 24.25e9), (57e9, 64e9), (76e9, 81e9))):
    ee = EE[f0]
    for f in (b_lo, b_hi):
        formula = np.degrees(np.arcsin(np.sqrt(ee) * (1 - f0 / f)))
        sim = af_peak(f, f0, ee)
        print(f"    f0 {f0/1e9:6.3f} GHz, f {f/1e9:6.3f} GHz: formula {formula:+6.2f} deg, array-factor peak {sim:+6.2f} deg")
        check(f"squint at {f/1e9} GHz", sim, formula, 0.02)
    rate = np.degrees(np.sqrt(ee) / f0) * 1e9
    print(f"    -> squint rate sqrt(eps_eff)/f0 = {rate:.3f} deg/GHz")
bw12 = np.degrees(0.886 * (c / 78.5e9) / (12 * c / (78.5e9 * np.sqrt(EE[78.5e9]))))
print(f"    12-element column at 78.5 GHz: HPBW ~ 0.886 lambda0/(N d) = {bw12:.1f} deg (squint across 76-81 GHz is comparable)")

print("=" * 78)
print("3. Centre-fed array (two 6-element halves fed in phase): gain at broadside vs frequency")
f0 = 78.5e9; ee = EE[f0]; lam_g0 = c / (f0 * np.sqrt(ee))
for f in (76e9, 78.5e9, 81e9):
    beta = 2 * np.pi * f * np.sqrt(ee) / c
    k0 = 2 * np.pi * f / c
    th = np.radians(np.linspace(-60, 60, 24001))
    n = np.arange(6)[:, None] + 0.5
    halfR = np.exp(1j * n * (k0 * lam_g0 * np.sin(th) - beta * lam_g0 + 2 * np.pi))   # wave travels +x
    halfL = np.exp(1j * n * (-k0 * lam_g0 * np.sin(th) - beta * lam_g0 + 2 * np.pi))  # wave travels -x
    af = np.abs(np.sum(halfR, axis=0) + np.sum(halfL, axis=0))
    pk = np.degrees(th[np.argmax(af)])
    loss = db((af[len(th) // 2] / 12) ** 2)
    print(f"    {f/1e9:5.1f} GHz: broadside AF loss {loss:6.2f} dB, peak at {pk:+.2f} deg (symmetric)")
    if f == 81e9:
        check("centre-fed broadside loss at 81 GHz (dB): each half squints 2.75 deg the opposite way", loss, -0.51, 0.02)

print("=" * 78)
print("4. Input reflection from N in-phase element reflections (|Gamma_e| = 0.05 each, N = 12)")
for ds in (1.0, 0.97, 0.94):
    f = f0
    beta = 2 * np.pi * f * np.sqrt(ee) / c
    d = ds * lam_g0
    G = 0.05 * np.abs(np.sum(np.exp(-2j * beta * d * np.arange(12))))
    tilt = np.degrees(np.arcsin(np.sqrt(ee) * (ds - 1) / ds)) if ds != 1 else 0.0
    print(f"    d = {ds:.2f} lambda_g0: beam {tilt:+5.1f} deg, |Gamma_in| ~ {G:.3f} ({db(G**2):6.1f} dB)")
    if ds == 1.0:
        check("broadside reflection build-up |Gamma| = N*0.05", G, 0.60, 1e-6)

print("=" * 78)
print("5. Travelling-wave taper: radiated fraction per element (-25 dB Chebyshev, N = 10, 5 % to load)")
N = 10
from scipy.signal.windows import chebwin
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    w = chebwin(N, 25)
w = np.abs(w) / np.max(np.abs(w))
p = w**2 / np.sum(w**2) * 0.95                       # 95 % radiated, 5 % to the load
remaining = 1.0 - np.concatenate([[0], np.cumsum(p)[:-1]])
frac = p / remaining
print("    amplitudes:", np.round(w, 3))
print("    fraction of arriving power radiated by element n:", np.round(frac, 3))
check("last element radiates p_N/(p_N+0.05)", frac[-1], p[-1] / (p[-1] + 0.05), 1e-9)
# sidelobe check of the taper
th = np.radians(np.linspace(-90, 90, 36001))
af = np.abs(np.sum(w[:, None] * np.exp(1j * np.pi * np.arange(N)[:, None] * np.sin(th)), axis=0))
afdb = 20 * np.log10(af / af.max())
loc = (afdb[1:-1] > afdb[:-2]) & (afdb[1:-1] > afdb[2:])
pks = np.sort(afdb[1:-1][loc])[::-1]
print(f"    peak sidelobe of these weights (lambda/2 test): {pks[1]:.1f} dB")
check("Chebyshev sidelobe (dB)", pks[1], -25.0, 0.3)

print("=" * 78)
print("6. Dielectric loss of the feed line (Pozar quasi-static) and a 24 GHz worked column")


def alpha_d_db_per_mm(er, ee, tand, f):
    lam0 = c / f
    return 27.3 * er * (ee - 1) * tand / (np.sqrt(ee) * (er - 1) * lam0) / 1000.0


for lab, er, ee, tand, f in (("FR-4 er 4.4 tand 0.02 @77 GHz", 4.4, 3.2, 0.02, 77e9),
                             ("RO3003 er 3.0 tand 0.001 @77 GHz", 3.0, EE[78.5e9], 0.001, 77e9),
                             ("RO4350B er 3.66 tand 0.0037 @24 GHz", 3.66, EE[24.125e9], 0.0037, 24.125e9)):
    a = alpha_d_db_per_mm(er, ee, tand, f)
    print(f"    {lab:36s}: dielectric loss {a:.4f} dB/mm (conductor loss and roughness add more)")
check("FR-4 77 GHz dielectric loss (dB/mm)", alpha_d_db_per_mm(4.4, 3.2, 0.02, 77e9), 0.223, 0.005)
lam0 = c / 24.125e9; lg = c / (24.125e9 * np.sqrt(EE[24.125e9]))
N = 8
print(f"    24.125 GHz, 8 patches at lambda_g = {lg*1e3:.2f} mm: column {N*lg*1e3:.0f} mm, elevation HPBW ~ 0.886 lambda0/(N d) = {np.degrees(0.886*lam0/(N*lg)):.1f} deg, squint +/-0.50 deg over 24.00-24.25 GHz")
check("24 GHz 8-element HPBW (deg)", np.degrees(0.886 * lam0 / (N * lg)), 10.7, 0.1)

print("=" * 78)
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
