"""Fresnel zones, earth bulge, radio horizon, line-of-sight altitude and elevation angle.

Ported from tools/verify/prop_fresnel_horizon.py (W1-A5). Page:
kb/09-propagation-link-budget/fresnel-zones-los-radio-horizon.md.
"""
import numpy as np

from .constants import C0, R_EARTH


def fresnel_radius(f_hz, d1_m, d2_m, n=1):
    """Paraxial radius [m] of the n-th Fresnel zone at distances d1, d2 from the two ends:
    r_n = sqrt(n lambda d1 d2 / (d1 + d2))."""
    lam = C0 / np.asarray(f_hz, float)
    d1 = np.asarray(d1_m, float)
    d2 = np.asarray(d2_m, float)
    return np.sqrt(n * lam * d1 * d2 / (d1 + d2))


def fresnel_radius_exact(f_hz, d1_m, d2_m, n=1):
    """Exact ellipsoid radius: path-length excess of n lambda/2 (solved numerically)."""
    from scipy.optimize import brentq
    lam = C0 / f_hz

    def g(r):
        return np.hypot(d1_m, r) + np.hypot(d2_m, r) - (d1_m + d2_m) - n * lam / 2

    hi = max(d1_m, d2_m)
    return brentq(g, 0.0, hi)


def fresnel_radius_itu(f_mhz, d1_km, d2_km, n=1):
    """ITU-R P.526 practical form R = 550 sqrt(n d1 d2 / ((d1+d2) f)) with R in m, d in km, f in MHz."""
    return 550.0 * np.sqrt(n * d1_km * d2_km / ((d1_km + d2_km) * f_mhz))


def earth_bulge(d1_m, d2_m, k=4.0 / 3.0):
    """Earth bulge [m] at a point d1, d2 from the ends: h = d1 d2 / (2 k Re)."""
    return np.asarray(d1_m, float) * np.asarray(d2_m, float) / (2 * k * R_EARTH)


def radio_horizon_m(h_m, k=4.0 / 3.0):
    """Distance [m] to the (radio) horizon from height h: sqrt(2 k Re h).
    k = 1 -> 3.57 sqrt(h_m) km; k = 4/3 -> 4.12 sqrt(h_m) km."""
    return np.sqrt(2 * k * R_EARTH * np.asarray(h_m, float))


def max_los_distance_m(h1_m, h2_m, k=4.0 / 3.0):
    return radio_horizon_m(h1_m, k) + radio_horizon_m(h2_m, k)


def los_altitude_m(ground_dist_m, gs_height_m, k=4.0 / 3.0):
    """Minimum altitude [m] of a target at ground distance D for geometric LOS from a station at height hg
    over a smooth sphere of radius k Re (small-angle approximation)."""
    a = k * R_EARTH
    dg = np.sqrt(2 * a * gs_height_m)
    if ground_dist_m <= dg:
        return 0.0
    return (ground_dist_m - dg) ** 2 / (2 * a)


def fresnel_clear_altitude_m(ground_dist_m, gs_height_m, f_hz, frac=0.6, k=4.0 / 3.0, n=400):
    """Minimum target altitude for which the straight ray clears the smooth earth by frac*R1 everywhere
    (brute force, as in prop_fresnel_horizon.py)."""
    a = k * R_EARTH
    lam = C0 / f_hz
    D = ground_dist_m
    x = np.linspace(0, D, n)[1:-1]
    for hr in np.concatenate([np.arange(0, 50, 0.25), np.arange(50, 20000, 2.0)]):
        line = gs_height_m + (hr - gs_height_m) * x / D
        bulge = x * (D - x) / (2 * a)
        r1 = np.sqrt(lam * x * (D - x) / D)
        if np.all(line - bulge >= frac * r1):
            return float(hr)
    return float("nan")


def elevation_deg(ground_dist_m, target_alt_m, gs_height_m=2.0, k=4.0 / 3.0):
    """Elevation angle [deg] and slant range [m] of a target, curvature included (effective radius k Re)."""
    a = k * R_EARTH
    th = ground_dist_m / a
    g = np.array([0.0, a + gs_height_m])
    r = np.array([(a + target_alt_m) * np.sin(th), (a + target_alt_m) * np.cos(th)])
    v = r - g
    up = g / np.linalg.norm(g)
    el = np.degrees(np.arcsin(np.dot(v, up) / np.linalg.norm(v)))
    return float(el), float(np.linalg.norm(v))
