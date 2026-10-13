#!/usr/bin/env python3
"""W5-S9 checks for kb/12-phased-arrays/beamforming-architectures.md case study
"Starlink-class LEO user terminal".

Run:  python3 tools/verify/s9_leo_terminal.py   (<1 s)

Inputs (see the page for sources and confidence):
  FCC STA narratives (2020/2022): Tx 14.0-14.5 GHz, Rx 10.7-12.7 GHz, min elevation 25 deg; flange power
  4.06 W (max slant) / 0.76 W (boresight); EIRP 38.2 / 33.4 dBW; gain Rx/Tx 33.2/34.6 dBi (boresight),
  30.6/32.0 dBi (max slant). Starlink spec sheets: Standard 594 x 383 mm, Mini 298.5 x 259 mm, FoV 110 deg.
  Teardown write-ups (secondary): Gen1 round 1,280 elements, hexagonal, 500-540 mm active diameter,
  80 beamformer ICs x 16 channels; rev4 Standard 1,536 elements, Mini 571 elements.
"""
import numpy as np

c = 299_792_458.0
kdb = -228.6
Re = 6371e3
ok_all = True
db = lambda x: 10 * np.log10(x)


def check(name, got, want, tol):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.5g}, expected {want:.5g} (tol {tol})")


print("=" * 78)
print("1. Filed EIRP = flange power + gain")
for lab, P, G, E in (("max slant", 4.06, 32.0, 38.2), ("boresight", 0.76, 34.6, 33.4)):
    got = db(P) + G
    print(f"    {lab}: {P} W = {db(P):+.2f} dBW + {G} dBi = {got:.2f} dBW (filed {E})")
    check(f"EIRP {lab}", got, E, 0.15)
print(f"    per-element Tx power if all 1,280 elements transmit: {4.06/1280*1e3:.2f} mW ({db(4.06/1280*1e3):.1f} dBm) at max slant")

print("=" * 78)
print("2. Lattice spacing implied by element count and area")
cases = (("Gen1 round, 1280 el., 500 mm", 1280, np.pi * 0.25**2),
         ("Gen1 round, 1280 el., 540 mm", 1280, np.pi * 0.27**2),
         ("rev4 Standard, 1536 el., <= 594 x 383 mm", 1536, 0.594 * 0.383),
         ("Mini, 571 el., <= 298.5 x 259 mm", 571, 0.2985 * 0.259))
for lab, N, A in cases:
    d = np.sqrt(A / N / (np.sqrt(3) / 2))     # equilateral triangular (hexagonal) lattice
    print(f"    {lab:42s}: area/element {A/N*1e4:.2f} cm^2 -> triangular spacing {d*1e3:.1f} mm "
          f"({d/(c/11.7e9):.2f} lambda @11.7 GHz, {d/(c/14.25e9):.2f} lambda @14.25 GHz)")
d1 = np.sqrt(np.pi * 0.25**2 / 1280 / (np.sqrt(3) / 2))
check("Gen1 spacing 500 mm (mm)", d1 * 1e3, 13.3, 0.05)


def gl_free_scan(d_over_lam):
    """Max scan (deg) with no grating lobe entering visible space, equilateral triangular lattice,
    worst plane (towards the nearest reciprocal-lattice point at distance 2/(sqrt3 d))."""
    s = 2 / (np.sqrt(3) * d_over_lam) - 1
    return np.degrees(np.arcsin(min(s, 1.0)))


# numeric check of the rule by brute-force reciprocal lattice
def brute(d_over_lam):
    """Vectorised: smallest scan angle (any azimuth) at which a grating lobe enters |u| <= 1."""
    a1 = np.array([1.0, 0.0]) * d_over_lam
    a2 = np.array([0.5, np.sqrt(3) / 2]) * d_over_lam
    Bm = np.linalg.inv(np.array([a1, a2]).T).T
    G = np.array([Bm @ np.array([m, n]) for m in range(-2, 3) for n in range(-2, 3) if (m, n) != (0, 0)])
    phi = np.radians(np.arange(0, 360, 0.5))[:, None, None]
    th = np.radians(np.arange(0, 90.001, 0.02))[None, :, None]
    ux = np.sin(th) * np.cos(phi) + G[:, 0][None, None, :]
    uy = np.sin(th) * np.sin(phi) + G[:, 1][None, None, :]
    hit = (np.hypot(ux, uy) <= 1.0).any(axis=2)          # [phi, th]
    first = np.where(hit.any(axis=1), hit.argmax(axis=1), hit.shape[1] - 1)
    return float(np.degrees(th[0, first.min(), 0]))


for f in (11.7e9, 12.7e9, 14.25e9, 14.5e9):
    dl = d1 / (c / f)
    print(f"    Gen1 d = {d1*1e3:.1f} mm at {f/1e9:5.2f} GHz: d/lambda {dl:.3f} -> grating-lobe-free scan {gl_free_scan(dl):5.1f} deg (worst plane)")
dl = d1 / (c / 14.5e9)
check("triangular-lattice scan rule vs brute force at 14.5 GHz (deg)", brute(dl), gl_free_scan(dl), 0.3)

print("=" * 78)
print("3. Aperture directivity vs filed gain")
for f, G, lab in ((11.7e9, 33.2, "Rx"), (14.25e9, 34.6, "Tx")):
    lam = c / f
    for A, al in ((np.pi * 0.25**2, "500 mm"), (np.pi * 0.27**2, "540 mm")):
        D = db(4 * np.pi * A / lam**2)
        print(f"    {lab} {f/1e9:5.2f} GHz, {al}: 4piA/lambda^2 = {D:5.1f} dBi; filed {G} dBi -> {D-G:4.1f} dB below (aperture eff. {10**((G-D)/10)*100:3.0f} %)")
D = db(4 * np.pi * np.pi * 0.25**2 / (c / 11.7e9) ** 2)
check("Rx directivity 500 mm (dBi)", D, 35.8, 0.1)

print("=" * 78)
print("4. Scan loss and the 25 deg elevation mask")
for lab, g0, g1 in (("Rx", 33.2, 30.6), ("Tx", 34.6, 32.0)):
    dG = g0 - g1
    th = np.degrees(np.arccos(10 ** (-dG / 10)))
    th13 = np.degrees(np.arccos(10 ** (-dG / 13)))
    print(f"    {lab}: boresight -> max slant drop {dG:.1f} dB -> scan {th:.1f} deg if loss = cos(theta), {th13:.1f} deg if cos^1.3")
print(f"    flat-mounted, zenith-facing panel at 25 deg elevation would scan 65 deg: cos -> {db(np.cos(np.radians(65))):.2f} dB")
print("    spec-sheet FoV 110 deg = +/-55 deg -> consistent with the 2.6 dB drop under a cos-law (56.7 deg)")
check("cos-law scan for 2.6 dB (deg)", np.degrees(np.arccos(10 ** (-0.26))), 56.7, 0.1)

print("=" * 78)
print("5. Geometry and path loss (550 km shell)")
h = 550e3


def slant(el_deg):
    el = np.radians(el_deg)
    return np.sqrt((Re + h) ** 2 - (Re * np.cos(el)) ** 2) - Re * np.sin(el)


for el in (90, 55, 40, 25):
    R = slant(el)
    print(f"    elevation {el:2d} deg: slant {R/1e3:7.1f} km; FSPL {db((4*np.pi*R*11.7e9/c)**2):6.1f} dB @11.7 GHz, {db((4*np.pi*R*14.25e9/c)**2):6.1f} dB @14.25 GHz")
check("slant range at 25 deg (km)", slant(25) / 1e3, 1123.0, 3.0)
span = db((slant(25) / slant(90)) ** 2)
print(f"    path-loss span zenith -> 25 deg: {span:.1f} dB; filed EIRP span 38.2 - 33.4 = 4.8 dB (rest: satellite beam gain/pointing, not stated)")

print("=" * 78)
print("6. Uplink C/N vs satellite G/T, and UT G/T estimate")
EIRP, R = 38.2, slant(25)
L = db((4 * np.pi * R * 14.25e9 / c) ** 2)
for GT in (-5.0, 0.0, 5.0):
    CN0 = EIRP - L + GT - kdb
    print(f"    satellite G/T {GT:+.0f} dB/K: C/N0 = {CN0:5.1f} dB-Hz, C/N in 60 MHz = {CN0 - db(60e6):5.1f} dB")
for Tsys in (150, 250, 400):
    print(f"    UT Rx G/T with T_sys {Tsys} K: {33.2 - db(Tsys):5.1f} dB/K (boresight), {30.6 - db(Tsys):5.1f} dB/K (max slant)")
CN0 = EIRP - L + 0 - kdb
check("uplink C/N0, G/T 0 dB/K (dB-Hz)", CN0, 90.3, 0.1)

print("=" * 78)
print("7. Architecture arithmetic")
print(f"    Gen1: 80 beamformers x 16 channels = {80*16} element channels (= 1,280 elements)")
check("80 x 16", 80 * 16, 1280, 0)
print(f"    a fully digital 1,280-element array at 240 MS/s, 2 x 8 bit = {1280*240e6*16/1e12:.1f} Tb/s -> analog/RFIC beamforming is the only practical choice")

print("=" * 78)
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
