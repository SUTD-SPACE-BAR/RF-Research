"""Transmission-line characteristic impedance calculators: microstrip, stripline, CPW/CPWG, coax,
plus synthesis (width for a target Z0), guided wavelength and microstrip loss.

Ported from tools/verify/tline_microstrip.py, tline_cpwg.py and tline_coax.py (W1-A4), which validate
these closed forms against the independent 2-D field solver tools/verify/tline_fd2d.py and scikit-rf.
Page: kb/03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md, coax-and-cables.md.

Geometry in metres. Closed forms model idealised geometry (rectangular conductors, no soldermask,
homogeneous substrate); real boards differ by 1-3 ohm (mask, etch trapezoid, Dk tolerance).
References: Hammerstad & Jensen, IEEE MTT-S Digest 1980; Wheeler, IEEE T-MTT 1977 & 1978;
Kirschning & Jansen, Electron. Lett. 1982 / IEEE T-MTT 1983; Cohn, IRE T-MTT 1954;
Ghione & Naldi, Electron. Lett. 1984 (CPWG); Pozar, Microwave Engineering 4th ed. sec. 3.7-3.8.
"""
import math

import numpy as np
from scipy.optimize import brentq
from scipy.special import ellipk

from .constants import C0, ETA0, MU0, SIGMA_CU


# ================================================================ microstrip
def microstrip_simple(w, h, er):
    """Hammerstad (1975) simple closed forms as given in Pozar sec. 3.8. Returns (Z0, eps_eff)."""
    u = w / h
    ee = (er + 1) / 2 + (er - 1) / 2 / math.sqrt(1 + 12 / u)
    if u <= 1:
        z = 60 / math.sqrt(ee) * math.log(8 / u + u / 4)
    else:
        z = 120 * math.pi / (math.sqrt(ee) * (u + 1.393 + 0.667 * math.log(u + 1.444)))
    return z, ee


def _hj_z01(u):
    fu = 6 + (2 * math.pi - 6) * math.exp(-(30.666 / u) ** 0.7528)
    return ETA0 / (2 * math.pi) * math.log(fu / u + math.sqrt(1 + (2 / u) ** 2))


def _hj_ee(u, er):
    a = 1 + math.log((u ** 4 + (u / 52) ** 2) / (u ** 4 + 0.432)) / 49 + math.log(1 + (u / 18.1) ** 3) / 18.7
    b = 0.564 * ((er - 0.9) / (er + 3)) ** 0.053
    return (er + 1) / 2 + (er - 1) / 2 * (1 + 10 / u) ** (-a * b)


def microstrip_hj(w, h, er, t=0.0):
    """Hammerstad & Jensen (1980) quasi-static microstrip, with strip-thickness correction.
    Returns (Z0 [ohm], eps_eff). Claimed accuracy better than 0.2-1 % for 0.01 <= W/h <= 100, er <= 128."""
    u = w / h
    if t <= 0:
        ee = _hj_ee(u, er)
        return _hj_z01(u) / math.sqrt(ee), ee
    tn = t / h
    du1 = tn / math.pi * math.log(1 + 4 * math.e / (tn / math.tanh(math.sqrt(6.517 * u)) ** 2))
    dur = 0.5 * (1 + 1 / math.cosh(math.sqrt(er - 1))) * du1
    u1, ur = u + du1, u + dur
    ee_r = _hj_ee(ur, er)
    z = _hj_z01(ur) / math.sqrt(ee_r)
    ee = ee_r * (_hj_z01(u1) / _hj_z01(ur)) ** 2
    return z, ee


def microstrip_wheeler77(w, h, er, t=0.0):
    """Wheeler (1977) microstrip Z0 (with its thickness correction). Accuracy ~1 %."""
    if t > 0:
        dw = t / math.pi * math.log(4 * math.e / math.sqrt((t / h) ** 2 + (1 / math.pi / (w / t + 1.1)) ** 2)) \
            * (1 + 1 / er) / 2
        wp = w + dw
    else:
        wp = w
    k = (14 + 8 / er) / 11 * 4 * h / wp
    return ETA0 / (2 * math.pi * math.sqrt(2 * (1 + er))) * math.log(
        1 + 4 * h / wp * (k + math.sqrt(k ** 2 + math.pi ** 2 * (1 + 1 / er) / 2)))


def microstrip_kj(w, h, er, f_hz, t=0.0):
    """Frequency-dependent microstrip: Kirschning-Jansen (1982) eps_eff(f) and Jansen-Kirschning (1983)
    Z0(f), applied to the H-J quasi-static values. Returns (Z0(f), eps_eff(f))."""
    z0s, ee0 = microstrip_hj(w, h, er, t)
    u = w / h
    fn = f_hz / 1e9 * h * 1e3     # GHz * mm
    P1 = 0.27488 + (0.6315 + 0.525 / (1 + 0.0157 * fn) ** 20) * u - 0.065683 * math.exp(-8.7513 * u)
    P2 = 0.33622 * (1 - math.exp(-0.03442 * er))
    P3 = 0.0363 * math.exp(-4.6 * u) * (1 - math.exp(-(fn / 38.7) ** 4.97))
    P4 = 1 + 2.751 * (1 - math.exp(-(er / 15.916) ** 8))
    P = P1 * P2 * ((0.1844 + P3 * P4) * fn) ** 1.5763
    eef = er - (er - ee0) / (1 + P)
    R1 = 0.03891 * er ** 1.4
    R2 = 0.267 * u ** 7.0
    R3 = 4.766 * math.exp(-3.228 * u ** 0.641)
    R4 = 0.016 + (0.0514 * er) ** 4.524
    R5 = (fn / 28.843) ** 12
    R6 = 22.2 * u ** 1.92
    R7 = 1.206 - 0.3144 * math.exp(-R1) * (1 - math.exp(-R2))
    R8 = 1 + 1.275 * (1 - math.exp(-0.004625 * R3 * er ** 1.674 * (fn / 18.365) ** 2.745))
    R9 = 5.086 * R4 * R5 / (0.3838 + 0.386 * R4) * math.exp(-R6) / (1 + 1.2992 * R5) * \
        (er - 1) ** 6 / (1 + 10 * (er - 1) ** 6)
    R10 = 0.00044 * er ** 2.136 + 0.0184
    R11 = (fn / 19.47) ** 6 / (1 + 0.0962 * (fn / 19.47) ** 6)
    R12 = 1 / (1 + 0.00245 * u ** 2)
    R13 = 0.9408 * eef ** R8 - 0.9603
    R14 = (0.9408 - R9) * ee0 ** R8 - 0.9603
    R15 = 0.707 * R10 * (fn / 12.3) ** 1.097
    R16 = 1 + 0.0503 * er ** 2 * R11 * (1 - math.exp(-(u / 15) ** 6))
    R17 = R7 * (1 - 1.1241 * R12 / R16 * math.exp(-0.026 * fn ** 1.15656 - R15))
    zf = z0s * (R13 / R14) ** R17
    return zf, eef


def microstrip_width_pozar(z0, h, er):
    """Closed-form width synthesis (Pozar eq. 3.197, zero thickness). Returns W [m]."""
    A = z0 / 60 * math.sqrt((er + 1) / 2) + (er - 1) / (er + 1) * (0.23 + 0.11 / er)
    B = 377 * math.pi / (2 * z0 * math.sqrt(er))
    u1 = 8 * math.exp(A) / (math.exp(2 * A) - 2)
    if u1 < 2:
        return u1 * h
    u2 = 2 / math.pi * (B - 1 - math.log(2 * B - 1) + (er - 1) / (2 * er) * (math.log(B - 1) + 0.39 - 0.61 / er))
    return u2 * h


def microstrip_width(z0, h, er, t=0.0, model="hj"):
    """Width [m] giving Z0 = z0 by root-finding the chosen analysis model ('hj' or 'wheeler77')."""
    if model == "hj":
        fun = lambda w: microstrip_hj(w, h, er, t)[0]
    elif model == "wheeler77":
        fun = lambda w: microstrip_wheeler77(w, h, er, t)
    else:
        raise ValueError(model)
    return brentq(lambda w: fun(w) - z0, 1e-3 * h, 100 * h, xtol=1e-10)


def microstrip_loss_db_per_m(w, h, er, tand, f_hz, t=35e-6, sigma=SIGMA_CU, rough_rms=0.0):
    """Conductor and dielectric attenuation [dB/m] (Hammerstad current-distribution factor and
    roughness correction, as in Qucs/scikit-rf). Returns (alpha_c, alpha_d)."""
    z, ee = microstrip_hj(w, h, er, t)
    rs = math.sqrt(math.pi * f_hz * MU0 / sigma)
    ds = 1 / math.sqrt(math.pi * f_hz * MU0 * sigma)
    ki = math.exp(-1.2 * (z / ETA0) ** 0.7)
    kr = 1 + 2 / math.pi * math.atan(1.4 * (rough_rms / ds) ** 2)
    ac = rs / (z * w) * ki * kr
    ad = math.pi * er / (er - 1) * (ee - 1) / math.sqrt(ee) * tand * f_hz / C0
    k = 20 / math.log(10)
    return ac * k, ad * k


# ================================================================ stripline
def stripline_cohn(w, b, er):
    """Exact zero-thickness centred stripline (Cohn 1954), b = ground-to-ground spacing."""
    k = 1 / math.cosh(math.pi * w / (2 * b))
    kp = math.sqrt(1 - k * k)
    return 30 * math.pi / math.sqrt(er) * ellipk(k * k) / ellipk(kp * kp)


def stripline_wheeler78(w, b, t, er):
    """Finite-thickness centred stripline (Wheeler 1978)."""
    x = t / b
    m = 2 / (1 + 2 / 3 * x / (1 - x))
    dw = x / math.pi * (1 - 0.5 * math.log((x / (2 - x)) ** 2 + (0.0796 * x / (w / b + 1.1 * x)) ** m)) * (b - t)
    wp = w + dw
    q = 4 / math.pi * (b - t) / wp
    return 30 / math.sqrt(er) * math.log(1 + q * (2 * q + math.sqrt((2 * q) ** 2 + 6.27)))


# ================================================================ coplanar
def _kk(k):
    """K(k)/K(k') for modulus k (scipy ellipk takes m = k^2)."""
    return ellipk(k * k) / ellipk(1 - k * k)


def cpw(w, s, h, er):
    """CPW (no backside metal) on substrate thickness h, gap s, infinitely wide side grounds,
    zero-thickness conductors (conformal mapping, Ghione & Naldi / Simons). Returns (Z0, eps_eff)."""
    a, b = w / 2, w / 2 + s
    k0 = a / b
    k1 = math.sinh(math.pi * a / (2 * h)) / math.sinh(math.pi * b / (2 * h))
    ee = 1 + (er - 1) / 2 * _kk(k1) / _kk(k0)
    z = 30 * math.pi / math.sqrt(ee) / _kk(k0)
    return z, ee


def cpwg(w, s, h, er):
    """Grounded (conductor-backed) CPW, Ghione & Naldi 1984 conformal mapping, zero thickness,
    infinitely wide side grounds. Returns (Z0, eps_eff). Not valid when s >~ 2h (becomes microstrip)."""
    a, b = w / 2, w / 2 + s
    k0 = a / b
    k3 = math.tanh(math.pi * a / (2 * h)) / math.tanh(math.pi * b / (2 * h))
    q = _kk(k3) / _kk(k0)
    ee = (1 + er * q) / (1 + q)
    z = 60 * math.pi / math.sqrt(ee) / (_kk(k0) + _kk(k3))
    return z, ee


def cpwg_width(z0, s, h, er):
    """Centre-strip width [m] for a target CPWG Z0 (conformal-mapping model). The search is limited to
    W <= 10 h (beyond that tanh() saturates and the formula is outside its useful range)."""
    return brentq(lambda w: cpwg(w, s, h, er)[0] - z0, 1e-3 * h, 10 * h, xtol=1e-10)


# ================================================================ coax
def coax_z0(d_inner, d_outer, er=1.0):
    """Coax Z0 = (eta0 / (2 pi sqrt(er))) ln(D/d) ~ (60/sqrt(er)) ln(D/d)."""
    return ETA0 / (2 * math.pi * math.sqrt(er)) * math.log(d_outer / d_inner)


def coax_loss_db_per_m(d_inner, d_outer, er, tand, f_hz, sigma=SIGMA_CU):
    """Smooth-copper conductor + dielectric attenuation of a coax [dB/m] (theory lower bound;
    braided cables are 10-40 % worse, see coax-and-cables.md)."""
    rs = math.sqrt(math.pi * f_hz * MU0 / sigma)
    r = rs / (2 * math.pi) * (2 / d_inner + 2 / d_outer)
    z = coax_z0(d_inner, d_outer, er)
    ac = r / (2 * z)
    ad = math.pi * math.sqrt(er) * tand * f_hz / C0
    return (ac + ad) * 20 / math.log(10)


def coax_te11_cutoff_hz(d_inner, d_outer, er=1.0):
    """Approximate TE11 cutoff: f_c ~ c / (pi (a + b) sqrt(er)) with a, b radii."""
    return C0 / (math.pi * (d_inner + d_outer) / 2 * math.sqrt(er))


# ================================================================ helpers
def guided_wavelength(f_hz, eps_eff):
    return C0 / (f_hz * math.sqrt(eps_eff))


def quarter_wave_length(f_hz, eps_eff):
    return guided_wavelength(f_hz, eps_eff) / 4


def velocity_factor(eps_eff):
    return 1 / math.sqrt(eps_eff)


def lc_per_m(z0, eps_eff):
    """Per-unit-length L [H/m] and C [F/m] of a TEM/quasi-TEM line."""
    v = C0 / math.sqrt(eps_eff)
    return z0 / v, 1 / (z0 * v)
