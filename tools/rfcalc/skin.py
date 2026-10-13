"""Skin depth, surface resistance, roughness correction and round-wire AC resistance.

Ported from tools/verify/em_skin_depth.py (W1-A3). Page:
kb/02-electromagnetics/skin-effect-conductor-loss-roughness.md.
"""
import math

import numpy as np
from scipy.special import jv

from .constants import MU0, SIGMA_CU

# DC conductivities at ~20 C [S/m] = 1/rho with the CRC Handbook resistivities used in em_skin_depth.py
# (Ag 1.587, Cu 1.678, IACS 1.7241, Au 2.214, Al 2.650, Ni 6.93 micro-ohm cm). Brass and stainless
# steel are typical alloy values (vary +-30 %).
CONDUCTIVITY = {
    "silver": 1 / 1.587e-8,
    "copper": 1 / 1.678e-8,          # pure Cu (CRC 20 C)
    "copper_iacs": 1 / 1.7241e-8,    # annealed-copper standard, 5.80e7 S/m
    "gold": 1 / 2.214e-8,
    "aluminium": 1 / 2.650e-8,
    "nickel": 1 / 6.93e-8,           # mu_r = 1 assumed; real Ni is ferromagnetic below its FMR
    "brass": 1.5e7,
    "stainless_304": 1.4e6,
}


def skin_depth(f_hz, sigma=SIGMA_CU, mu_r=1.0):
    """delta = 1/sqrt(pi f mu sigma) [m] (good-conductor limit)."""
    return 1.0 / np.sqrt(np.pi * np.asarray(f_hz, float) * MU0 * mu_r * sigma)


def surface_resistance(f_hz, sigma=SIGMA_CU, mu_r=1.0):
    """R_s = 1/(sigma delta) = sqrt(pi f mu / sigma) [ohm/square]."""
    return np.sqrt(np.pi * np.asarray(f_hz, float) * MU0 * mu_r / sigma)


def roughness_hammerstad(f_hz, rms_m, sigma=SIGMA_CU):
    """Hammerstad-Jensen roughness factor K = 1 + (2/pi) atan(1.4 (Rq/delta)^2) (saturates at 2)."""
    d = skin_depth(f_hz, sigma)
    return 1 + 2 / np.pi * np.arctan(1.4 * (rms_m / d) ** 2)


def roughness_groiss(f_hz, rms_m, sigma=SIGMA_CU):
    """Groiss roughness factor K = 1 + exp(-(delta/(2 Rq))^1.6)."""
    d = skin_depth(f_hz, sigma)
    return 1 + np.exp(-(d / (2 * rms_m)) ** 1.6)


def wire_resistance_per_m(f_hz, radius_m, sigma=SIGMA_CU):
    """Exact AC resistance per metre of an isolated round wire (Bessel solution of the internal
    impedance). Falls to the DC value at low f and to R_s/(2 pi a) at high f."""
    k = (1 - 1j) * np.sqrt(np.pi * f_hz * MU0 * sigma)       # (1-j)/delta
    ka = k * radius_m
    z_int = k / (2 * np.pi * radius_m * sigma) * jv(0, ka) / jv(1, ka)
    return float(np.real(z_int))


def wire_resistance_hf_per_m(f_hz, radius_m, sigma=SIGMA_CU):
    """High-frequency asymptote R' = R_s / (2 pi a)."""
    return float(surface_resistance(f_hz, sigma) / (2 * math.pi * radius_m))


def dc_resistance_per_m(radius_m, sigma=SIGMA_CU):
    return 1.0 / (sigma * math.pi * radius_m ** 2)
