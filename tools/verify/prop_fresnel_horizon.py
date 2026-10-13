#!/usr/bin/env python3
"""
prop_fresnel_horizon.py — verification for kb/09-propagation-link-budget/fresnel-zones-los-radio-horizon.md

1. Fresnel-zone radius: exact ellipsoid vs the paraxial formula r_n = sqrt(n lambda d1 d2/(d1+d2)),
   and ITU-R P.526 practical form R = 550 sqrt(n d1 d2/((d1+d2) f_MHz)) (m, km, MHz).
2. Radio horizon d = sqrt(2 k Re h) -> 3.57 sqrt(h) km (k=1), 4.12 sqrt(h) km (k=4/3); exact vs approx.
3. Earth bulge h_b = d1 d2/(2 k Re) and required antenna heights for 60 % first-Fresnel clearance on
   ground-level LoRa links (433/915 MHz, 1-20 km).
4. Rocket descent: altitude at which LOS to a ground station is lost (smooth earth, k = 4/3), and the
   altitude at which 60 % Fresnel clearance is lost, vs ground distance and GS height.
5. Elevation angle of a rocket vs ground distance with curvature.
"""
import numpy as np
c = 299792458.0
Re = 6371e3

def fresnel_paraxial(n, lam, d1, d2):
    return np.sqrt(n*lam*d1*d2/(d1+d2))

def fresnel_exact(n, lam, d1, d2):
    """Exact radius of the n-th Fresnel ellipsoid at distance d1 from Tx: solve
    sqrt(d1^2 + r^2) + sqrt(d2^2 + r^2) = d1 + d2 + n lam/2."""
    from scipy.optimize import brentq
    D = d1 + d2 + n*lam/2
    return brentq(lambda r: np.sqrt(d1**2 + r**2) + np.sqrt(d2**2 + r**2) - D, 0, 1e6)

print("=== 1. Fresnel radius ===")
for f in (433.125e6, 915e6, 2.45e9):
    lam = c/f
    for d in (1e3, 5e3, 30e3):
        d1 = d2 = d/2
        rp = fresnel_paraxial(1, lam, d1, d2); rx = fresnel_exact(1, lam, d1, d2)
        ritu = 550*np.sqrt(1*(d1/1e3)*(d2/1e3)/((d/1e3)*f/1e6))
        print(f"  f={f/1e6:7.1f} MHz d={d/1e3:5.1f} km: R1(mid) paraxial={rp:6.2f} m, exact={rx:6.2f} m, ITU 550-form={ritu:6.2f} m;"
              f" 0.6 R1={0.6*rp:5.2f} m")
# near-terminal (not mid) values
lam = c/433.125e6
for d1 in (10.0, 100.0, 1000.0):
    print(f"  433 MHz, 30 km path, {d1:6.0f} m from the GS: R1 = {fresnel_paraxial(1, lam, d1, 30e3-d1):5.2f} m")

print("\n=== 2. Radio horizon ===")
for kf in (1.0, 4/3):
    for h in (1.5, 3.0, 10.0, 30.0, 100.0, 1000.0, 10e3, 30e3):
        a = kf*Re
        d_exact = np.sqrt((a+h)**2 - a**2)
        d_approx = np.sqrt(2*a*h)
        coef = np.sqrt(2*a)/1e3*np.sqrt(1.0)  # km per sqrt(m)
        print(f"  k={kf:4.2f} h={h:8.1f} m: d_horizon exact {d_exact/1e3:8.2f} km, sqrt(2kRe h) {d_approx/1e3:8.2f} km "
              f"({np.sqrt(2*a)/1e3:.3f} sqrt(h) km)")
print("  Two-terminal LOS range (k=4/3): 4.12 (sqrt(h1) + sqrt(h2)) km, h in m")

print("\n=== 3. Ground-level LoRa link clearance (k=4/3) ===")
ae = 4/3*Re
for f in (433.125e6, 915e6):
    lam = c/f
    for d in (1e3, 2e3, 5e3, 10e3, 20e3):
        bulge = (d/2)**2/(2*ae)
        r1 = fresnel_paraxial(1, lam, d/2, d/2)
        need = bulge + 0.6*r1
        print(f"  f={f/1e6:6.1f} MHz d={d/1e3:5.1f} km: bulge {bulge:6.2f} m + 0.6 R1 {0.6*r1:5.2f} m -> both antennas at "
              f">= {need:6.2f} m above flat terrain (equal heights, midpoint)")

print("\n=== 4. Rocket descent: altitude where LOS / Fresnel clearance is lost ===")
def los_alt(D, hg, kf=4/3):
    """Minimum rocket altitude (m) for geometric LOS at ground distance D (m) from a GS of height hg (m)
    over a smooth sphere of radius kf*Re."""
    a = kf*Re
    dg = np.sqrt(2*a*hg)          # GS horizon distance
    if D <= dg:
        return 0.0
    return (D - dg)**2/(2*a)

def fresnel_alt(D, hg, f, frac=0.6, kf=4/3, n=400):
    """Minimum rocket altitude for which the ray clears the smooth earth by frac*R1 everywhere.
    Brute force over altitude."""
    a = kf*Re; lam = c/f
    x = np.linspace(0, D, n)[1:-1]
    for hr in np.concatenate([np.arange(0, 50, 0.25), np.arange(50, 5000, 2.0)]):
        # straight line from (0,hg) to (D,hr) in the flat-earth-with-bulge frame
        line = hg + (hr - hg)*x/D
        bulge = x*(D - x)/(2*a)
        r1 = np.sqrt(lam*x*(D - x)/D)
        if np.all(line - bulge >= frac*r1):
            return hr
    return np.nan
print("  D = ground distance GS -> rocket; smooth earth, no terrain, no trees")
for hg in (2.0, 5.0, 20.0):
    for D in (5e3, 10e3, 20e3, 30e3, 50e3):
        print(f"  GS h={hg:4.0f} m, D={D/1e3:4.0f} km: LOS lost below {los_alt(D, hg):7.1f} m; "
              f"0.6 R1 lost below 433 MHz {fresnel_alt(D, hg, 433.125e6):7.1f} m / 915 MHz {fresnel_alt(D, hg, 915e6):7.1f} m")

print("\n=== 5. Elevation angle with curvature ===")
def elevation(D, h, hg=2.0, kf=4/3):
    a = kf*Re
    # central angle
    th = D/a
    # position vectors
    g = np.array([0.0, a + hg])
    r = np.array([(a + h)*np.sin(th), (a + h)*np.cos(th)])
    v = r - g
    up = g/np.linalg.norm(g)
    return np.degrees(np.arcsin(np.dot(v, up)/np.linalg.norm(v))), np.linalg.norm(v)
for h in (1e3, 3e3, 10e3, 30e3):
    for D in (2e3, 10e3, 30e3):
        el, sr = elevation(D, h)
        print(f"  alt {h/1e3:5.1f} km, ground dist {D/1e3:5.1f} km: elevation {el:6.2f} deg, slant range {sr/1e3:6.2f} km")
