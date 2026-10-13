#!/usr/bin/env python3
"""
prop2_igrf.py — minimal IGRF-14 main-field synthesis (own implementation) used by the W5-E4 propagation pages.

Data: tools/verify/data/igrf14coeffs.txt (IAGA IGRF-14, Schmidt semi-normalised g/h in nT, fetched 2026-10-02 from
https://www.ngdc.noaa.gov/IAGA/vmod/coeffs/igrf14coeffs.txt — public domain).

Provides field(lat_deg, lon_deg, alt_km, year) -> (X north, Y east, Z down) in nT using the geocentric-sphere
approximation (geodetic latitude treated as geocentric: dip error < ~0.2 deg, adequate for propagation work),
plus dip(), dip_latitude(), modip() (P.1239 modified dip), gyrofrequency(), dipole_geomag_lat().
Run directly to print Singapore values and self-checks.
"""
import os
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_FILE = os.path.join(_HERE, "data", "igrf14coeffs.txt")
A_REF = 6371.2  # km, IGRF reference radius


def _load():
    epochs, rows = None, []
    with open(_FILE) as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            parts = line.split()
            if parts[0] == "c/s":
                continue
            if parts[0] == "g/h":
                epochs = [float(p) for p in parts[3:-1]]  # last column is SV '2025-30'
                continue
            rows.append((parts[0], int(parts[1]), int(parts[2]), [float(p) for p in parts[3:]]))
    return np.array(epochs), rows


_EPOCHS, _ROWS = _load()


def coeffs(year, nmax=13):
    """Return g[n][m], h[n][m] (nT) for decimal year (linear interpolation; SV beyond last epoch)."""
    g = np.zeros((nmax + 1, nmax + 1)); h = np.zeros((nmax + 1, nmax + 1))
    last = _EPOCHS[-1]
    for gh, n, m, vals in _ROWS:
        if n > nmax:
            continue
        if year >= last:
            v = vals[len(_EPOCHS) - 1] + (year - last) * vals[-1]
        else:
            i = np.searchsorted(_EPOCHS, year) - 1
            i = max(i, 0)
            t = (year - _EPOCHS[i]) / (_EPOCHS[i + 1] - _EPOCHS[i])
            v = vals[i] + t * (vals[i + 1] - vals[i])
        (g if gh == "g" else h)[n, m] = v
    return g, h


def _schmidt_legendre(nmax, theta):
    """Schmidt semi-normalised P[n][m](cos theta) and dP/dtheta (recursion)."""
    ct, st = np.cos(theta), np.sin(theta)
    P = np.zeros((nmax + 1, nmax + 1)); dP = np.zeros((nmax + 1, nmax + 1))
    P[0, 0] = 1.0
    for n in range(1, nmax + 1):
        for m in range(0, n + 1):
            if n == m:
                if n == 1:
                    P[1, 1] = st; dP[1, 1] = ct
                else:
                    k = np.sqrt((2 * n - 1) / (2 * n))
                    P[n, n] = k * st * P[n - 1, n - 1]
                    dP[n, n] = k * (st * dP[n - 1, n - 1] + ct * P[n - 1, n - 1])
            else:
                a = (2 * n - 1) / np.sqrt(n * n - m * m)
                b = np.sqrt(((n - 1) ** 2 - m * m) / (n * n - m * m)) if n - 1 >= m else 0.0
                P[n, m] = a * ct * P[n - 1, m] - (b * P[n - 2, m] if n - 2 >= m else 0.0)
                dP[n, m] = a * (ct * dP[n - 1, m] - st * P[n - 1, m]) - (b * dP[n - 2, m] if n - 2 >= m else 0.0)
    return P, dP


def field(lat_deg, lon_deg, alt_km=0.0, year=2026.75, nmax=13):
    g, h = coeffs(year, nmax)
    theta = np.radians(90.0 - lat_deg); phi = np.radians(lon_deg)
    r = A_REF + alt_km
    P, dP = _schmidt_legendre(nmax, theta)
    X = Y = Z = 0.0
    st = np.sin(theta)
    for n in range(1, nmax + 1):
        ar = (A_REF / r) ** (n + 2)
        for m in range(0, n + 1):
            cm, sm = np.cos(m * phi), np.sin(m * phi)
            gc = g[n, m] * cm + h[n, m] * sm
            X += ar * gc * dP[n, m]                       # north = -B_theta
            if st > 1e-10:
                Y += ar * m * (g[n, m] * sm - h[n, m] * cm) * P[n, m] / st
            Z -= (n + 1) * ar * gc * P[n, m]              # down = -B_r
    return X, Y, Z


def dip(lat, lon, alt_km=0.0, year=2026.75):
    X, Y, Z = field(lat, lon, alt_km, year)
    return np.degrees(np.arctan2(Z, np.hypot(X, Y)))


def dip_latitude(lat, lon, alt_km=0.0, year=2026.75):
    """Magnetic (dip) latitude: tan(mu) = tan(I)/2."""
    return np.degrees(np.arctan(np.tan(np.radians(dip(lat, lon, alt_km, year))) / 2))


def modip(lat, lon, alt_km=300.0, year=1960.0):
    """Rawer modified dip X = atan(I / sqrt(cos lat)) (P.1239 eq. 4; I in radians)."""
    I = np.radians(dip(lat, lon, alt_km, year))
    return np.degrees(np.arctan(I / np.sqrt(np.cos(np.radians(lat)))))


def gyrofrequency(lat, lon, alt_km=300.0, year=2026.75):
    """f_H = 2.8 MHz/gauss * |B| (P.1239 eq. 11); 1 gauss = 1e5 nT."""
    X, Y, Z = field(lat, lon, alt_km, year)
    return 2.8 * np.sqrt(X * X + Y * Y + Z * Z) / 1e5


def dipole_geomag_lat(lat, lon, year=2026.75):
    g, h = coeffs(year, 1)
    b0 = np.sqrt(g[1, 0] ** 2 + g[1, 1] ** 2 + h[1, 1] ** 2)
    th_p = np.arccos(-g[1, 0] / b0); ph_p = np.arctan2(-h[1, 1], -g[1, 1])  # north geomagnetic pole
    lat_p = 90 - np.degrees(th_p); lon_p = np.degrees(ph_p)
    la, lo, lp, op = map(np.radians, (lat, lon, lat_p, lon_p))
    s = np.sin(la) * np.sin(lp) + np.cos(la) * np.cos(lp) * np.cos(lo - op)
    return np.degrees(np.arcsin(s)), lat_p, lon_p


def dip_equator_lat(lon, alt_km=0.0, year=2026.75):
    from scipy.optimize import brentq
    return brentq(lambda la: dip(la, lon, alt_km, year), -25, 25)


if __name__ == "__main__":
    ok = True
    def check(name, val, lo, hi):
        global ok
        good = lo <= val <= hi
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] {name}: {val:.3f} (expected {lo}..{hi})")

    print("=== IGRF-14 self-checks ===")
    # Dipole term magnitude ~ 29 900 nT at 2025 (B0 from g10,g11,h11)
    g, h = coeffs(2025.0, 1)
    b0 = np.sqrt(g[1, 0] ** 2 + g[1, 1] ** 2 + h[1, 1] ** 2)
    check("dipole strength B0 2025 (nT)", b0, 29700, 29900)
    lat_g, lat_p, lon_p = dipole_geomag_lat(1.35, 103.82)
    check("north geomagnetic pole latitude 2025-26 (deg)", lat_p, 80.0, 81.5)
    # Boulder (40.0N, 105.27W) total field ~ 51-52 uT, dip ~ 65-66 deg (published NOAA values)
    X, Y, Z = field(40.015, -105.27, 1.65, 2025.0)
    check("Boulder total field 2025 (nT)", np.sqrt(X*X+Y*Y+Z*Z), 50500, 52500)
    check("Boulder dip 2025 (deg)", dip(40.015, -105.27, 1.65, 2025.0), 64.5, 66.5)

    # Published equatorial-station magnetic coordinates (literature, ~2005 epoch): Kototabang (0.20 S, 100.32 E)
    # magnetic latitude ~10.4 S; Chumphon (10.72 N, 99.37 E) dip latitude ~3.3 N; Trivandrum and Jicamarca lie on the
    # dip equator (|dip| ~ 1-2 deg).
    check("Kototabang dipole geomagnetic lat 2005", dipole_geomag_lat(-0.20, 100.32, 2005.0)[0], -11.0, -9.8)
    check("Chumphon dip latitude 2005", dip_latitude(10.72, 99.37, 0, 2005.0), 2.7, 3.9)
    check("Trivandrum |dip| 2005", abs(dip(8.5, 76.9, 0, 2005.0)), 0, 3)
    check("Jicamarca |dip| 2005", abs(dip(-11.95, -76.87, 0, 2005.0)), 0, 2)

    print("\n=== Singapore (1.35 N, 103.82 E) ===")
    I0 = dip(1.35, 103.82, 0, 2026.75); print(f"  dip at ground (2026.75) = {I0:.2f} deg")
    I300 = dip(1.35, 103.82, 300, 2026.75); print(f"  dip at 300 km = {I300:.2f} deg")
    print(f"  dip latitude (tan mu = tan I / 2) = {dip_latitude(1.35, 103.82, 0, 2026.75):.2f} deg")
    print(f"  dipole geomagnetic latitude = {lat_g:.2f} deg")
    print(f"  modified dip (P.1239, 1960 field, 300 km) = {modip(1.35, 103.82):.2f} deg")
    print(f"  gyrofrequency at 300 km = {gyrofrequency(1.35, 103.82):.3f} MHz; at 100 km = {gyrofrequency(1.35, 103.82, 100):.3f} MHz")
    for lon in (95.0, 103.82, 110.0, 120.0):
        print(f"  dip equator at {lon:6.2f} E: {dip_equator_lat(lon):+.2f} deg geographic latitude")
    check("Singapore ground dip in -20..-10 deg", I0, -20, -10)
    print("\nALL PASS" if ok else "\nSOME CHECKS FAILED")
