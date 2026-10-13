"""ITS Irregular Terrain Model (ITM, Longley-Rice) version 1.2.2 -- pure-Python port.

Point-to-point mode (terrain profile) and area mode (delta-h statistics), with time/location/situation
(TLS) or confidence/reliability (CR) variability, returning basic transmission loss in dB.

Acknowledgement / licence
-------------------------
This module is a derivative work of the NTIA/ITS reference implementation of the Irregular Terrain
Model, https://github.com/NTIA/itm (C++, "version 1.3 of this code base is functionally identical to
version 1.2.2 of the FORTRAN source"). The original software was developed by employees of the
National Telecommunications and Information Administration (NTIA), Institute for Telecommunication
Sciences (ITS), U.S. Department of Commerce; its LICENSE.md permits modification, derivative works
and redistribution provided that modified versions note the changes and acknowledge NTIA as the
source. We gratefully acknowledge NTIA/ITS as the source of the algorithm and reference code.
NTIA/ITS does not endorse this port and is not responsible for it.

Changes: ported to Python by W5-S11a, 2026-10-13 (RF Physics KB, tools/rfcalc); behaviour intended
identical to NTIA/itm master (src/*.cpp). Differences are interface-only: Python functions return a
dict instead of writing through pointers, hard input errors raise ValueError (the error code is in
the message and in ``ItmError.code``) instead of returning an integer code, and warnings are returned
both as the NTIA bit field and as a list of flag names. Numerical steps, constants and branch order
follow the C++ source statement by statement.

References
----------
- G. A. Hufford, A. G. Longley, W. A. Kissick, "A guide to the use of the ITS Irregular Terrain Model
  in the area prediction mode", NTIA Report 82-100 (1982).
- G. A. Hufford, "The ITS Irregular Terrain Model, version 1.2.2 -- the algorithm" (NTIA/ITS, 1995).
- A. G. Longley, P. L. Rice, "Prediction of tropospheric radio transmission loss over irregular
  terrain -- a computer method", ESSA Tech. Rep. ERL 79-ITS 67 (1968).
- NTIA/itm test vectors p2p.csv, pfls.csv, area.csv (re-typed in tests/data/itm_*.csv).

Conventions (as NTIA): heights in m, distances in m internally (d_km at the API), f in MHz;
pol 0 = horizontal, 1 = vertical; climate 1..7 (1 equatorial, 2 continental subtropical,
3 maritime subtropical, 4 desert, 5 continental temperate, 6 maritime temperate over land,
7 maritime temperate over sea); mdvar 0 single-message, 1 accidental, 2 mobile, 3 broadcast,
+10 = no location variability, +20 = no direct situation variability; siting 0 random,
1 careful, 2 very careful. pfl = [np, xi, z0, z1, ..., z_np] (np intervals of xi metres,
np + 1 elevations in metres).
"""
import cmath
import math

import numpy as np

# ---------------------------------------------------------------- constants (include/itm.h)
A_0__METER = 6370e3
A_9000__METER = 9000e3
THIRD = 1.0 / 3.0
SQRT2 = math.sqrt(2.0)
PI = 3.1415926535897932384

MODE__P2P = 0
MODE__AREA = 1

# include/Enums.h
SINGLE_MESSAGE_MODE, ACCIDENTAL_MODE, MOBILE_MODE, BROADCAST_MODE = 0, 1, 2, 3
POLARIZATION__HORIZONTAL, POLARIZATION__VERTICAL = 0, 1
SITING_CRITERIA__RANDOM, SITING_CRITERIA__CAREFUL, SITING_CRITERIA__VERY_CAREFUL = 0, 1, 2
MODE__NOT_SET, MODE__LINE_OF_SIGHT, MODE__DIFFRACTION, MODE__TROPOSCATTER = 0, 1, 2, 3
MODE_NAMES = {0: "not set", 1: "line-of-sight", 2: "diffraction", 3: "troposcatter"}
CLIMATES = {1: "equatorial", 2: "continental subtropical", 3: "maritime subtropical", 4: "desert",
            5: "continental temperate", 6: "maritime temperate over land", 7: "maritime temperate over sea"}

# include/Warnings.h
WARNINGS = {
    0x0001: "WARN__TX_TERMINAL_HEIGHT",
    0x0002: "WARN__RX_TERMINAL_HEIGHT",
    0x0004: "WARN__FREQUENCY",
    0x0008: "WARN__PATH_DISTANCE_TOO_BIG_1",
    0x0010: "WARN__PATH_DISTANCE_TOO_BIG_2",
    0x0020: "WARN__PATH_DISTANCE_TOO_SMALL_1",
    0x0040: "WARN__PATH_DISTANCE_TOO_SMALL_2",
    0x0080: "WARN__TX_HORIZON_ANGLE",
    0x0100: "WARN__RX_HORIZON_ANGLE",
    0x0200: "WARN__TX_HORIZON_DISTANCE_1",
    0x0400: "WARN__RX_HORIZON_DISTANCE_1",
    0x0800: "WARN__TX_HORIZON_DISTANCE_2",
    0x1000: "WARN__RX_HORIZON_DISTANCE_2",
    0x2000: "WARN__EXTREME_VARIABILITIES",
    0x4000: "WARN__SURFACE_REFRACTIVITY",
}
WARN__TX_TERMINAL_HEIGHT = 0x0001
WARN__RX_TERMINAL_HEIGHT = 0x0002
WARN__FREQUENCY = 0x0004
WARN__PATH_DISTANCE_TOO_BIG_1 = 0x0008
WARN__PATH_DISTANCE_TOO_BIG_2 = 0x0010
WARN__PATH_DISTANCE_TOO_SMALL_1 = 0x0020
WARN__PATH_DISTANCE_TOO_SMALL_2 = 0x0040
WARN__TX_HORIZON_ANGLE = 0x0080
WARN__RX_HORIZON_ANGLE = 0x0100
WARN__TX_HORIZON_DISTANCE_1 = 0x0200
WARN__RX_HORIZON_DISTANCE_1 = 0x0400
WARN__TX_HORIZON_DISTANCE_2 = 0x0800
WARN__RX_HORIZON_DISTANCE_2 = 0x1000
WARN__EXTREME_VARIABILITIES = 0x2000
WARN__SURFACE_REFRACTIVITY = 0x4000

# include/Errors.h
ERRORS = {
    1000: "ERROR__TX_TERMINAL_HEIGHT (TX terminal height out of range)",
    1001: "ERROR__RX_TERMINAL_HEIGHT (RX terminal height out of range)",
    1002: "ERROR__INVALID_RADIO_CLIMATE",
    1003: "ERROR__INVALID_TIME (time percentage out of range)",
    1004: "ERROR__INVALID_LOCATION (location percentage out of range)",
    1005: "ERROR__INVALID_SITUATION (situation percentage out of range)",
    1006: "ERROR__INVALID_CONFIDENCE (confidence percentage out of range)",
    1007: "ERROR__INVALID_RELIABILITY (reliability percentage out of range)",
    1008: "ERROR__REFRACTIVITY (N_0 out of range)",
    1009: "ERROR__FREQUENCY (frequency out of range)",
    1010: "ERROR__POLARIZATION",
    1011: "ERROR__EPSILON",
    1012: "ERROR__SIGMA",
    1013: "ERROR__GROUND_IMPEDANCE (imaginary part of Z_g larger than real part)",
    1014: "ERROR__MDVAR",
    1016: "ERROR__EFFECTIVE_EARTH (effective earth radius invalid)",
    1017: "ERROR__PATH_DISTANCE",
    1018: "ERROR__DELTA_H",
    1019: "ERROR__TX_SITING_CRITERIA",
    1020: "ERROR__RX_SITING_CRITERIA",
    1021: "ERROR__SURFACE_REFRACTIVITY_SMALL",
    1022: "ERROR__SURFACE_REFRACTIVITY_LARGE",
}


class ItmError(ValueError):
    """Hard ITM input/derived-parameter error (NTIA error code in ``.code``)."""

    def __init__(self, code):
        self.code = code
        super().__init__(f"ITM error {code}: {ERRORS.get(code, 'unknown')}")


def warning_names(warnings):
    """Decode the NTIA warning bit field into a list of flag names."""
    return [name for bit, name in WARNINGS.items() if warnings & bit]


def _dim(x, y):
    """Fortran DIM / C fdim: x - y if x > y else 0."""
    return x - y if x > y else 0.0


# ---------------------------------------------------------------- small helpers
def free_space_loss(d__meter, f__mhz):
    """FreeSpaceLoss.cpp: 32.45 + 20 log10(f_MHz) + 20 log10(d_km)."""
    return 32.45 + 20.0 * math.log10(f__mhz) + 20.0 * math.log10(d__meter / 1000.0)


def fresnel_integral(v2):
    """FresnelIntegral.cpp: knife-edge attenuation [dB] as a function of v^2 (TN101 III.24)."""
    if v2 < 5.76:
        return 6.02 + 9.11 * math.sqrt(v2) - 1.27 * v2
    return 12.953 + 10 * math.log10(v2)


def inverse_ccdf(q):
    """InverseComplementaryCumulativeDistributionFunction.cpp: Q^-1(q), Abramowitz & Stegun 26.2.23
    rational approximation (|error| < 4.5e-4)."""
    C_0, C_1, C_2 = 2.515516, 0.802853, 0.010328
    D_1, D_2, D_3 = 1.432788, 0.189269, 0.001308
    x = q
    if q > 0.5:
        x = 1.0 - x
    T_x = math.sqrt(-2.0 * math.log(x))
    zeta_x = ((C_2 * T_x + C_1) * T_x + C_0) / (((D_3 * T_x + D_2) * T_x + D_1) * T_x + 1.0)
    Q_q = T_x - zeta_x
    if q > 0.5:
        Q_q = -Q_q
    return Q_q


def terrain_roughness(d__meter, delta_h__meter):
    """TerrainRoughness.cpp: delta_h(d) = delta_h (1 - 0.8 exp(-d / 50 km))."""
    return delta_h__meter * (1.0 - 0.8 * math.exp(-d__meter / 50e3))


def sigma_h_function(delta_h__meter):
    """SigmaHFunction.cpp: rms terrain deviation within the first Fresnel zone [ERL 79-ITS 67, 3.6a]."""
    return 0.78 * delta_h__meter * math.exp(-0.5 * delta_h__meter ** 0.25)


def _h0_curve(j, r):
    a = (25.0, 80.0, 177.0, 395.0, 705.0)
    b = (24.0, 45.0, 68.0, 80.0, 105.0)
    return 10 * math.log10(1 + a[j] * (1 / r) ** 4 + b[j] * (1.0 / r) ** 2)


def h0_function(r, eta_s):
    """H0Function.cpp: troposcatter frequency-gain function H_0(r, eta_s)."""
    eta_s = min(max(eta_s, 1), 5)
    i = int(eta_s)
    q = eta_s - i
    result = _h0_curve(i - 1, r)
    if q != 0.0:
        result = (1.0 - q) * result + q * _h0_curve(i, r)
    return result


def f_function(td):
    """TroposcatterLoss.cpp FFunction: F(theta d) [Algorithm 6.9]."""
    a = (133.4, 104.6, 71.8)
    b = (0.332e-3, 0.212e-3, 0.157e-3)
    c = (-10, -2.5, 5)
    if td <= 10e3:
        i = 0
    elif td <= 70e3:
        i = 1
    else:
        i = 2
    return a[i] + b[i] * td + c[i] * math.log10(td)


def height_function(x__km, K):
    """SmoothEarthDiffraction.cpp HeightFunction: height-gain F(x, K) [dB]."""
    if x__km < 200.0:
        w = -math.log(K)
        if K < 1e-5 or x__km * w ** 3 > 5495.0:
            result = -117.0
            if x__km > 1.0:
                result = 17.372 * math.log(x__km) + result
        else:
            result = 2.5e-5 * x__km ** 2 / K - 8.686 * w - 15.0
    else:
        result = 0.05751 * x__km - 4.343 * math.log(x__km)
        if x__km < 2000:
            w = 0.0134 * x__km * math.exp(-0.005 * x__km)
            result = (1.0 - w) * result + w * (17.372 * math.log(x__km) - 117.0)
    return result


# ---------------------------------------------------------------- loss mechanisms
def knife_edge_diffraction(d__meter, f__mhz, a_e__meter, theta_los, d_hzn__meter):
    """KnifeEdgeDiffraction.cpp: double knife-edge (one per horizon) loss [dB]."""
    d_ML__meter = d_hzn__meter[0] + d_hzn__meter[1]
    theta_nlos = d__meter / a_e__meter - theta_los
    d_nlos__meter = d__meter - d_ML__meter
    v_1 = 0.0795775 * (f__mhz / 47.7) * theta_nlos ** 2 * d_hzn__meter[0] * d_nlos__meter / (
        d_nlos__meter + d_hzn__meter[0])
    v_2 = 0.0795775 * (f__mhz / 47.7) * theta_nlos ** 2 * d_hzn__meter[1] * d_nlos__meter / (
        d_nlos__meter + d_hzn__meter[1])
    return fresnel_integral(v_1) + fresnel_integral(v_2)


def smooth_earth_diffraction(d__meter, f__mhz, a_e__meter, theta_los, d_hzn__meter, h_e__meter, Z_g):
    """SmoothEarthDiffraction.cpp: Vogler three-radius smooth-earth diffraction loss [dB]."""
    theta_nlos = d__meter / a_e__meter - theta_los
    d_ML__meter = d_hzn__meter[0] + d_hzn__meter[1]
    a__meter = [(d__meter - d_ML__meter) / (d__meter / a_e__meter - theta_los),
                0.5 * d_hzn__meter[0] ** 2 / h_e__meter[0],
                0.5 * d_hzn__meter[1] ** 2 / h_e__meter[1]]
    d__km = [(a__meter[0] * theta_nlos) / 1000.0, d_hzn__meter[0] / 1000.0, d_hzn__meter[1] / 1000.0]
    C_0 = [0.0] * 3
    K = [0.0] * 3
    B_0 = [0.0] * 3
    for i in range(3):
        C_0[i] = ((4.0 / 3.0) * A_0__METER / a__meter[i]) ** THIRD
        K[i] = 0.017778 * C_0[i] * f__mhz ** (-THIRD) / abs(Z_g)
        B_0[i] = 1.607 - K[i]
    x1 = B_0[1] * C_0[1] ** 2 * f__mhz ** THIRD * d__km[1]
    x2 = B_0[2] * C_0[2] ** 2 * f__mhz ** THIRD * d__km[2]
    x0 = B_0[0] * C_0[0] ** 2 * f__mhz ** THIRD * d__km[0] + x1 + x2
    F_x0 = height_function(x1, K[1])
    F_x1 = height_function(x2, K[2])
    G_x__db = 0.05751 * x0 - 10.0 * math.log10(x0)
    return G_x__db - F_x0 - F_x1 - 20


def diffraction_loss(d__meter, d_hzn__meter, h_e__meter, Z_g, a_e__meter, delta_h__meter, h__meter, mode,
                     theta_los, d_sML__meter, f__mhz):
    """DiffractionLoss.cpp: weighted knife-edge / smooth-earth combination plus clutter [dB]."""
    A_k__db = knife_edge_diffraction(d__meter, f__mhz, a_e__meter, theta_los, d_hzn__meter)
    A_se__db = smooth_earth_diffraction(d__meter, f__mhz, a_e__meter, theta_los, d_hzn__meter, h_e__meter, Z_g)
    delta_h_dsML__meter = terrain_roughness(d_sML__meter, delta_h__meter)
    sigma_h_d__meter = sigma_h_function(delta_h_dsML__meter)
    A_fo__db = min(15.0, 5 * math.log10(1.0 + 1e-5 * h__meter[0] * h__meter[1] * f__mhz * sigma_h_d__meter))
    delta_h_d__meter = terrain_roughness(d__meter, delta_h__meter)
    q = h__meter[0] * h__meter[1]
    qk = h_e__meter[0] * h_e__meter[1] - q
    if mode == MODE__P2P:
        q += 10.0
    term1 = math.sqrt(1.0 + qk / q)
    d_ML__meter = d_hzn__meter[0] + d_hzn__meter[1]
    q = (term1 + (-theta_los * a_e__meter + d_ML__meter) / d__meter) * min(delta_h_d__meter * f__mhz / 47.7, 6283.2)
    w = 25.1 / (25.1 + math.sqrt(q))
    return w * A_se__db + (1.0 - w) * A_k__db + A_fo__db


def line_of_sight_loss(d__meter, h_e__meter, Z_g, delta_h__meter, M_d, A_d0, d_sML__meter, f__mhz):
    """LineOfSightLoss.cpp: two-ray (rough-earth reflection) loss blended with extended diffraction [dB]."""
    delta_h_d__meter = terrain_roughness(d__meter, delta_h__meter)
    sigma_h_d__meter = sigma_h_function(delta_h_d__meter)
    wn = f__mhz / 47.7
    sin_psi = (h_e__meter[0] + h_e__meter[1]) / math.sqrt(d__meter ** 2 + (h_e__meter[0] + h_e__meter[1]) ** 2)
    R_e = (sin_psi - Z_g) / (sin_psi + Z_g) * math.exp(-min(10.0, wn * sigma_h_d__meter * sin_psi))
    q = R_e.real ** 2 + R_e.imag ** 2
    if q < 0.25 or q < sin_psi:
        R_e = R_e * math.sqrt(sin_psi / q)
    delta_phi = wn * 2.0 * h_e__meter[0] * h_e__meter[1] / d__meter
    if delta_phi > PI / 2.0:
        delta_phi = PI - (PI / 2.0) ** 2 / delta_phi
    rr = complex(math.cos(delta_phi), -math.sin(delta_phi)) + R_e
    A_t__db = -10 * math.log10(rr.real ** 2 + rr.imag ** 2)
    A_d__db = M_d * d__meter + A_d0
    w = 1 / (1 + f__mhz * delta_h__meter / max(10e3, d_sML__meter))
    return w * A_t__db + (1 - w) * A_d__db


def troposcatter_loss(d__meter, theta_hzn, d_hzn__meter, h_e__meter, a_e__meter, N_s, f__mhz, theta_los, h0):
    """TroposcatterLoss.cpp. ``h0`` is the in/out H_0 value (a one-element list, as the C++ pointer).
    Returns the troposcatter loss [dB] (1001 if undefined)."""
    wn = f__mhz / 47.7
    if h0[0] > 15.0:
        H_0 = h0[0]
    else:
        ad = d_hzn__meter[0] - d_hzn__meter[1]
        rr = h_e__meter[1] / h_e__meter[0]
        if ad < 0.0:
            ad = -ad
            rr = 1.0 / rr
        theta = theta_hzn[0] + theta_hzn[1] + d__meter / a_e__meter
        r_1 = 2.0 * wn * theta * h_e__meter[0]
        r_2 = 2.0 * wn * theta * h_e__meter[1]
        if r_1 < 0.2 and r_2 < 0.2:
            return 1001
        s = (d__meter - ad) / (d__meter + ad)
        q = min(max(0.1, rr / s), 10.0)
        s = max(0.1, s)
        h_0__meter = (d__meter - ad) * (d__meter + ad) * theta * 0.25 / d__meter
        Z_0__meter = 1.7556e3
        Z_1__meter = 8.0e3
        eta_s = (h_0__meter / Z_0__meter) * (1.0 + (0.031 - N_s * 2.32e-3 + N_s ** 2 * 5.67e-6)
                                             * math.exp(-min(1.7, h_0__meter / Z_1__meter) ** 6))
        H_00 = (h0_function(r_1, eta_s) + h0_function(r_2, eta_s)) / 2
        Delta_H_0 = min(H_00, 6.0 * (0.6 - math.log10(max(eta_s, 1.0))) * math.log10(s) * math.log10(q))
        H_0 = H_00 + Delta_H_0
        H_0 = max(H_0, 0.0)
        if eta_s < 1.0:
            H_0 = eta_s * H_0 + (1.0 - eta_s) * 10 * math.log10(
                ((1.0 + SQRT2 / r_1) * (1.0 + SQRT2 / r_2)) ** 2 * (r_1 + r_2) / (r_1 + r_2 + 2 * SQRT2))
        if H_0 > 15.0 and h0[0] >= 0.0:
            H_0 = h0[0]
    h0[0] = H_0
    th = d__meter / a_e__meter - theta_los
    D_0__meter = 40e3
    H__meter = 47.7
    return (f_function(th * d__meter) + 10 * math.log10(wn * H__meter * th ** 4)
            - 0.1 * (N_s - 301.0) * math.exp(-th * d__meter / D_0__meter) + H_0)


# ---------------------------------------------------------------- terrain processing (p2p)
def linear_least_squares_fit(pfl, d_start, d_end):
    """LinearLeastSquaresFit.cpp: least-squares line through pfl between d_start and d_end;
    returns (fit_y1, fit_y2) = fitted heights at the two ends of the whole profile."""
    np_ = int(pfl[0])
    i_start = int(_dim(d_start / pfl[1], 0.0))
    i_end = np_ - int(_dim(np_, d_end / pfl[1]))
    if i_end <= i_start:
        i_start = int(_dim(i_start, 1.0))
        i_end = np_ - int(_dim(np_, i_end + 1.0))
    x_length = i_end - i_start
    mid_shifted_index = -0.5 * x_length
    mid_shifted_end = i_end + mid_shifted_index
    sum_y = 0.5 * (pfl[i_start + 2] + pfl[i_end + 2])
    scaled_sum_y = 0.5 * (pfl[i_start + 2] - pfl[i_end + 2]) * mid_shifted_index
    for _ in range(2, int(x_length) + 1):
        i_start += 1
        mid_shifted_index += 1
        sum_y += pfl[i_start + 2]
        scaled_sum_y += pfl[i_start + 2] * mid_shifted_index
    sum_y = sum_y / x_length
    scaled_sum_y = scaled_sum_y * 12.0 / ((x_length * x_length + 2.0) * x_length)
    fit_y1 = sum_y - scaled_sum_y * mid_shifted_end
    fit_y2 = sum_y + scaled_sum_y * (np_ - mid_shifted_end)
    return fit_y1, fit_y2


def compute_delta_h(pfl, d_start__meter, d_end__meter):
    """ComputeDeltaH.cpp: interdecile range of terrain heights about a fitted line, corrected to
    the asymptotic delta_h [m]."""
    np_ = int(pfl[0])
    x_start = d_start__meter / pfl[1]
    x_end = d_end__meter / pfl[1]
    if x_end - x_start < 2.0:
        return 0
    p10 = int(0.1 * (x_end - x_start + 8.0))
    p10 = min(max(4, p10), 25)
    n = 10 * p10 - 5
    p90 = n - p10
    np_s = float(n - 1)
    s = [0.0] * (n + 2)
    s[0] = np_s
    s[1] = 1.0
    x_end = (x_end - x_start) / np_s
    i = int(x_start)
    x_start -= float(i + 1.0)
    for j in range(n):
        while x_start > 0.0 and (i + 1) < np_:
            x_start -= 1
            i += 1
        s[j + 2] = pfl[i + 3] + (pfl[i + 3] - pfl[i + 2]) * x_start
        x_start += x_end
    fit_y1, fit_y2 = linear_least_squares_fit(s, 0.0, np_s)
    fit_y2 = (fit_y2 - fit_y1) / np_s
    diffs = []
    for j in range(n):
        diffs.append(s[j + 2] - fit_y1)
        fit_y1 += fit_y2
    desc = sorted(diffs, reverse=True)       # nth_element with std::greater -> descending order statistic
    q10 = desc[p10 - 1]
    q90 = desc[p90]
    delta_h_d__meter = q10 - q90
    return delta_h_d__meter / (1.0 - 0.8 * math.exp(-(d_end__meter - d_start__meter) / 50e3))


def find_horizons(pfl, a_e__meter, h__meter):
    """FindHorizons.cpp: terminal horizon angles [rad] and distances [m] from the profile."""
    np_ = int(pfl[0])
    xi = pfl[1]
    d__meter = pfl[0] * pfl[1]
    z_tx__meter = pfl[2] + h__meter[0]
    z_rx__meter = pfl[np_ + 2] + h__meter[1]
    theta_hzn = [(z_rx__meter - z_tx__meter) / d__meter - d__meter / (2 * a_e__meter),
                 -(z_rx__meter - z_tx__meter) / d__meter - d__meter / (2 * a_e__meter)]
    d_hzn__meter = [d__meter, d__meter]
    d_tx__meter = 0.0
    d_rx__meter = d__meter
    for i in range(1, np_):
        d_tx__meter = d_tx__meter + xi
        d_rx__meter = d_rx__meter - xi
        theta_tx = (pfl[i + 2] - z_tx__meter) / d_tx__meter - d_tx__meter / (2 * a_e__meter)
        theta_rx = -(z_rx__meter - pfl[i + 2]) / d_rx__meter - d_rx__meter / (2 * a_e__meter)
        if theta_tx > theta_hzn[0]:
            theta_hzn[0] = theta_tx
            d_hzn__meter[0] = d_tx__meter
        if theta_rx > theta_hzn[1]:
            theta_hzn[1] = theta_rx
            d_hzn__meter[1] = d_rx__meter
    return theta_hzn, d_hzn__meter


def quick_pfl(pfl, gamma_e, h__meter):
    """QuickPfl.cpp: extract path geometry from the profile.
    Returns (theta_hzn, d_hzn__meter, h_e__meter, delta_h__meter, d__meter)."""
    d__meter = pfl[0] * pfl[1]
    np_ = int(pfl[0])
    a_e__meter = 1 / gamma_e
    theta_hzn, d_hzn__meter = find_horizons(pfl, a_e__meter, h__meter)
    d_start__meter = min(15.0 * h__meter[0], 0.1 * d_hzn__meter[0])
    d_end__meter = d__meter - min(15.0 * h__meter[1], 0.1 * d_hzn__meter[1])
    delta_h__meter = compute_delta_h(pfl, d_start__meter, d_end__meter)
    h_e__meter = [0.0, 0.0]
    if d_hzn__meter[0] + d_hzn__meter[1] > 1.5 * d__meter:
        fit_tx, fit_rx = linear_least_squares_fit(pfl, d_start__meter, d_end__meter)
        h_e__meter[0] = h__meter[0] + _dim(pfl[2], fit_tx)
        h_e__meter[1] = h__meter[1] + _dim(pfl[np_ + 2], fit_rx)
        for i in range(2):
            d_hzn__meter[i] = math.sqrt(2.0 * h_e__meter[i] * a_e__meter) * math.exp(
                -0.07 * math.sqrt(delta_h__meter / max(h_e__meter[i], 5.0)))
        combined_horizons__meter = d_hzn__meter[0] + d_hzn__meter[1]
        if combined_horizons__meter <= d__meter:
            q = (d__meter / combined_horizons__meter) ** 2
            for i in range(2):
                h_e__meter[i] = h_e__meter[i] * q
                d_hzn__meter[i] = math.sqrt(2.0 * h_e__meter[i] * a_e__meter) * math.exp(
                    -0.07 * math.sqrt(delta_h__meter / max(h_e__meter[i], 5.0)))
        for i in range(2):
            q = math.sqrt(2.0 * h_e__meter[i] * a_e__meter)
            theta_hzn[i] = (0.65 * delta_h__meter * (q / d_hzn__meter[i] - 1.0) - 2.0 * h_e__meter[i]) / q
    else:
        fit_tx, _ = linear_least_squares_fit(pfl, d_start__meter, 0.9 * d_hzn__meter[0])
        h_e__meter[0] = h__meter[0] + _dim(pfl[2], fit_tx)
        _, fit_rx = linear_least_squares_fit(pfl, d__meter - 0.9 * d_hzn__meter[1], d_end__meter)
        h_e__meter[1] = h__meter[1] + _dim(pfl[np_ + 2], fit_rx)
    return theta_hzn, d_hzn__meter, h_e__meter, delta_h__meter, d__meter


# ---------------------------------------------------------------- initialisation
def initialize_point_to_point(f__mhz, h_sys__meter, N_0, pol, epsilon, sigma):
    """InitializePointToPoint.cpp: returns (Z_g, gamma_e, N_s)."""
    gamma_a = 157e-9
    if h_sys__meter == 0.0:
        N_s = N_0
    else:
        N_s = N_0 * math.exp(-h_sys__meter / 9460.0)
    gamma_e = gamma_a * (1.0 - 0.04665 * math.exp(N_s / 179.3))
    ep_r = complex(epsilon, 18000 * sigma / f__mhz)
    Z_g = cmath.sqrt(ep_r - 1.0)
    if pol == POLARIZATION__VERTICAL:
        Z_g = Z_g / ep_r
    return Z_g, gamma_e, N_s


def initialize_area(site_criteria, gamma_e, delta_h__meter, h__meter):
    """InitializeArea.cpp: effective heights, horizon distances and angles from siting criteria and
    delta_h. Returns (h_e__meter, d_hzn__meter, theta_hzn)."""
    h_e__meter = [0.0, 0.0]
    d_hzn__meter = [0.0, 0.0]
    theta_hzn = [0.0, 0.0]
    for i in range(2):
        if site_criteria[i] == SITING_CRITERIA__RANDOM:
            h_e__meter[i] = h__meter[i]
        else:
            B = 4.0 if site_criteria[i] == SITING_CRITERIA__CAREFUL else 9.0
            if h__meter[i] < 5.0:
                B = B * math.sin(0.1 * PI * h__meter[i])
            h_e__meter[i] = h__meter[i] + (1.0 + B) * math.exp(
                -min(20.0, 2.0 * h__meter[i] / max(1e-3, delta_h__meter)))
        d_Ls__meter = math.sqrt(2.0 * h_e__meter[i] / gamma_e)
        H_3__meter = 5
        d_hzn__meter[i] = d_Ls__meter * math.exp(-0.07 * math.sqrt(delta_h__meter / max(h_e__meter[i], H_3__meter)))
        theta_hzn[i] = (0.65 * delta_h__meter * (d_Ls__meter / d_hzn__meter[i] - 1.0) - 2.0 * h_e__meter[i]) / d_Ls__meter
    return h_e__meter, d_hzn__meter, theta_hzn


def validate_inputs(h_tx__meter, h_rx__meter, climate, time, location, situation, N_0, f__mhz, pol,
                    epsilon, sigma, mdvar):
    """ValidateInputs.cpp: raises ItmError (ValueError) on hard errors; returns the warning bits."""
    w = 0
    if h_tx__meter < 1.0 or h_tx__meter > 1000.0:
        w |= WARN__TX_TERMINAL_HEIGHT
    if h_tx__meter < 0.5 or h_tx__meter > 3000.0:
        raise ItmError(1000)
    if h_rx__meter < 1.0 or h_rx__meter > 1000.0:
        w |= WARN__RX_TERMINAL_HEIGHT
    if h_rx__meter < 0.5 or h_rx__meter > 3000.0:
        raise ItmError(1001)
    if climate not in (1, 2, 3, 4, 5, 6, 7):
        raise ItmError(1002)
    if N_0 < 250 or N_0 > 400:
        raise ItmError(1008)
    if f__mhz < 40.0 or f__mhz > 10000.0:
        w |= WARN__FREQUENCY
    if f__mhz < 20 or f__mhz > 20000:
        raise ItmError(1009)
    if pol not in (POLARIZATION__HORIZONTAL, POLARIZATION__VERTICAL):
        raise ItmError(1010)
    if epsilon < 1:
        raise ItmError(1011)
    if sigma <= 0:
        raise ItmError(1012)
    if (mdvar < 0 or (3 < mdvar < 10) or (13 < mdvar < 20) or (23 < mdvar < 30) or mdvar > 33
            or mdvar != int(mdvar)):
        raise ItmError(1014)
    if situation <= 0 or situation >= 100:
        raise ItmError(1005)
    if time <= 0 or time >= 100:
        raise ItmError(1003)
    if location <= 0 or location >= 100:
        raise ItmError(1004)
    return w


# ---------------------------------------------------------------- core model
def longley_rice(theta_hzn, f__mhz, Z_g, d_hzn__meter, h_e__meter, gamma_e, N_s, delta_h__meter, h__meter,
                 d__meter, mode):
    """LongleyRice.cpp: reference attenuation (median, relative to free space) [dB].
    Returns (A_ref__db, warning_bits, propmode). Raises ItmError on derived-parameter errors."""
    w = 0
    a_e__meter = 1 / gamma_e
    d_hzn_s__meter = [math.sqrt(2.0 * h_e__meter[i] * a_e__meter) for i in range(2)]
    d_sML__meter = d_hzn_s__meter[0] + d_hzn_s__meter[1]
    d_ML__meter = d_hzn__meter[0] + d_hzn__meter[1]
    theta_los = -max(theta_hzn[0] + theta_hzn[1], -d_ML__meter / a_e__meter)

    if abs(theta_hzn[0]) > 200e-3:
        w |= WARN__TX_HORIZON_ANGLE
    if abs(theta_hzn[1]) > 200e-3:
        w |= WARN__RX_HORIZON_ANGLE
    if d_hzn__meter[0] < 0.1 * d_hzn_s__meter[0]:
        w |= WARN__TX_HORIZON_DISTANCE_1
    if d_hzn__meter[1] < 0.1 * d_hzn_s__meter[1]:
        w |= WARN__RX_HORIZON_DISTANCE_1
    if d_hzn__meter[0] > 3.0 * d_hzn_s__meter[0]:
        w |= WARN__TX_HORIZON_DISTANCE_2
    if d_hzn__meter[1] > 3.0 * d_hzn_s__meter[1]:
        w |= WARN__RX_HORIZON_DISTANCE_2

    if N_s < 150:
        raise ItmError(1021)
    if N_s > 400:
        raise ItmError(1022)
    if N_s < 250:
        w |= WARN__SURFACE_REFRACTIVITY
    if a_e__meter < 4000000 or a_e__meter > 13333333:
        raise ItmError(1016)
    if Z_g.real <= abs(Z_g.imag):
        raise ItmError(1013)

    d_3__meter = max(d_sML__meter, d_ML__meter + 5.0 * (a_e__meter ** 2 / f__mhz) ** (1.0 / 3.0))
    d_4__meter = d_3__meter + 10.0 * (a_e__meter ** 2 / f__mhz) ** (1.0 / 3.0)
    A_3__db = diffraction_loss(d_3__meter, d_hzn__meter, h_e__meter, Z_g, a_e__meter, delta_h__meter, h__meter, mode,
                               theta_los, d_sML__meter, f__mhz)
    A_4__db = diffraction_loss(d_4__meter, d_hzn__meter, h_e__meter, Z_g, a_e__meter, delta_h__meter, h__meter, mode,
                               theta_los, d_sML__meter, f__mhz)
    M_d = (A_4__db - A_3__db) / (d_4__meter - d_3__meter)
    A_d0__db = A_3__db - M_d * d_3__meter

    d_min__meter = abs(h_e__meter[0] - h_e__meter[1]) / 200e-3
    if d__meter < d_min__meter:
        w |= WARN__PATH_DISTANCE_TOO_SMALL_1
    if d__meter < 1e3:
        w |= WARN__PATH_DISTANCE_TOO_SMALL_2
    if d__meter > 1000e3:
        w |= WARN__PATH_DISTANCE_TOO_BIG_1
    if d__meter > 2000e3:
        w |= WARN__PATH_DISTANCE_TOO_BIG_2

    if d__meter < d_sML__meter:
        A_sML__db = d_sML__meter * M_d + A_d0__db
        d_0__meter = 0.04 * f__mhz * h_e__meter[0] * h_e__meter[1]
        if A_d0__db >= 0.0:
            d_0__meter = min(d_0__meter, 0.5 * d_ML__meter)
            d_1__meter = d_0__meter + 0.25 * (d_ML__meter - d_0__meter)
        else:
            d_1__meter = max(-A_d0__db / M_d, 0.25 * d_ML__meter)
        A_1__db = line_of_sight_loss(d_1__meter, h_e__meter, Z_g, delta_h__meter, M_d, A_d0__db, d_sML__meter, f__mhz)
        flag = False
        kHat_1 = 0.0
        kHat_2 = 0.0
        if d_0__meter < d_1__meter:
            A_0__db = line_of_sight_loss(d_0__meter, h_e__meter, Z_g, delta_h__meter, M_d, A_d0__db, d_sML__meter,
                                         f__mhz)
            q = math.log(d_sML__meter / d_0__meter)
            kHat_2 = max(0.0, ((d_sML__meter - d_0__meter) * (A_1__db - A_0__db)
                               - (d_1__meter - d_0__meter) * (A_sML__db - A_0__db))
                         / ((d_sML__meter - d_0__meter) * math.log(d_1__meter / d_0__meter)
                            - (d_1__meter - d_0__meter) * q))
            flag = A_d0__db > 0.0 or kHat_2 > 0.0
            if flag:
                kHat_1 = (A_sML__db - A_0__db - kHat_2 * q) / (d_sML__meter - d_0__meter)
                if kHat_1 < 0.0:
                    kHat_1 = 0.0
                    kHat_2 = _dim(A_sML__db, A_0__db) / q
                    if kHat_2 == 0.0:
                        kHat_1 = M_d
        if not flag:
            kHat_1 = _dim(A_sML__db, A_1__db) / (d_sML__meter - d_1__meter)
            kHat_2 = 0.0
            if kHat_1 == 0.0:
                kHat_1 = M_d
        A_o__db = A_sML__db - kHat_1 * d_sML__meter - kHat_2 * math.log(d_sML__meter)
        A_ref__db = A_o__db + kHat_1 * d__meter + kHat_2 * math.log(d__meter)
        propmode = MODE__LINE_OF_SIGHT
    else:
        d_5__meter = d_ML__meter + 200e3
        d_6__meter = d_ML__meter + 400e3
        h0 = [-1.0]
        A_6__db = troposcatter_loss(d_6__meter, theta_hzn, d_hzn__meter, h_e__meter, a_e__meter, N_s, f__mhz,
                                    theta_los, h0)
        A_5__db = troposcatter_loss(d_5__meter, theta_hzn, d_hzn__meter, h_e__meter, a_e__meter, N_s, f__mhz,
                                    theta_los, h0)
        if A_5__db < 1000.0:
            M_s = (A_6__db - A_5__db) / 200e3
            d_x__meter = max(max(d_sML__meter,
                                 d_ML__meter + 1.088 * (a_e__meter ** 2 / f__mhz) ** (1.0 / 3.0) * math.log(f__mhz)),
                             (A_5__db - A_d0__db - M_s * d_5__meter) / (M_d - M_s))
            A_s0__db = (M_d - M_s) * d_x__meter + A_d0__db
        else:
            M_s = M_d
            A_s0__db = A_d0__db
            d_x__meter = 10e6
        if d__meter > d_x__meter:
            A_ref__db = M_s * d__meter + A_s0__db
            propmode = MODE__TROPOSCATTER
        else:
            A_ref__db = M_d * d__meter + A_d0__db
            propmode = MODE__DIFFRACTION

    A_ref__db = max(A_ref__db, 0.0)
    return A_ref__db, w, propmode


def _curve(c1, c2, x1, x2, x3, d_e__meter):
    return (c1 + c2 / (1.0 + ((d_e__meter - x2) / x3) ** 2)) * ((d_e__meter / x1) ** 2) / (1.0 + (d_e__meter / x1) ** 2)


_ALL_YEAR = (
    (-9.67, -0.62, 1.26, -9.21, -0.62, -0.39, 3.15),
    (12.7, 9.19, 15.5, 9.05, 9.19, 2.86, 857.9),
    (144.9e3, 228.9e3, 262.6e3, 84.1e3, 228.9e3, 141.7e3, 2222.e3),
    (190.3e3, 205.2e3, 185.2e3, 101.1e3, 205.2e3, 315.9e3, 164.8e3),
    (133.8e3, 143.6e3, 99.8e3, 98.6e3, 143.6e3, 167.4e3, 116.3e3),
)
_BSM1 = (2.13, 2.66, 6.11, 1.98, 2.68, 6.86, 8.51)
_BSM2 = (159.5, 7.67, 6.65, 13.11, 7.16, 10.38, 169.8)
_XSM1 = (762.2e3, 100.4e3, 138.2e3, 139.1e3, 93.7e3, 187.8e3, 609.8e3)
_XSM2 = (123.6e3, 172.5e3, 242.2e3, 132.7e3, 186.8e3, 169.6e3, 119.9e3)
_XSM3 = (94.5e3, 136.4e3, 178.6e3, 193.5e3, 133.5e3, 108.9e3, 106.6e3)
_BSP1 = (2.11, 6.87, 10.08, 3.68, 4.75, 8.58, 8.43)
_BSP2 = (102.3, 15.53, 9.60, 159.3, 8.12, 13.97, 8.19)
_XSP1 = (636.9e3, 138.7e3, 165.3e3, 464.4e3, 93.2e3, 216.0e3, 136.2e3)
_XSP2 = (134.8e3, 143.7e3, 225.7e3, 93.1e3, 135.9e3, 152.0e3, 188.5e3)
_XSP3 = (95.6e3, 98.6e3, 129.7e3, 94.2e3, 113.4e3, 122.7e3, 122.9e3)
_C_D = (1.224, 0.801, 1.380, 1.000, 1.224, 1.518, 1.518)
_Z_D = (1.282, 2.161, 1.282, 20.0, 1.282, 1.282, 1.282)
_BFM1 = (1.0, 1.0, 1.0, 1.0, 0.92, 1.0, 1.0)
_BFM2 = (0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0)
_BFM3 = (0.0, 0.0, 0.0, 0.0, 1.77, 0.0, 0.0)
_BFP1 = (1.0, 0.93, 1.0, 0.93, 0.93, 1.0, 1.0)
_BFP2 = (0.0, 0.31, 0.0, 0.19, 0.31, 0.0, 0.0)
_BFP3 = (0.0, 2.00, 0.0, 1.79, 2.00, 0.0, 0.0)


def variability(time, location, situation, h_e__meter, delta_h__meter, f__mhz, d__meter, A_ref__db, climate, mdvar):
    """Variability.cpp: quantile of attenuation relative to free space [dB], including the climate
    median V_med. Returns (A_db_rel_free_space, warning_bits)."""
    w = 0
    z_T = inverse_ccdf(time / 100)
    z_L = inverse_ccdf(location / 100)
    z_S = inverse_ccdf(situation / 100)
    c = climate - 1
    wn = f__mhz / 47.7
    d_ex__meter = (math.sqrt(2 * A_9000__METER * h_e__meter[0]) + math.sqrt(2 * A_9000__METER * h_e__meter[1])
                   + (575.7e12 / wn) ** THIRD)
    if d__meter < d_ex__meter:
        d_e__meter = 130e3 * d__meter / d_ex__meter
    else:
        d_e__meter = 130e3 + d__meter - d_ex__meter

    mdv = mdvar
    plus20 = mdv >= 20
    if plus20:
        mdv -= 20
    if plus20:
        sigma_S = 0.0
    else:
        D__meter = 100e3
        sigma_S = 5.0 + 3.0 * math.exp(-d_e__meter / D__meter)
    plus10 = mdv >= 10
    if plus10:
        mdv -= 10

    V_med__db = _curve(_ALL_YEAR[0][c], _ALL_YEAR[1][c], _ALL_YEAR[2][c], _ALL_YEAR[3][c], _ALL_YEAR[4][c], d_e__meter)

    if mdv == SINGLE_MESSAGE_MODE:
        z_T = z_S
        z_L = z_S
    elif mdv == ACCIDENTAL_MODE:
        z_L = z_S
    elif mdv == MOBILE_MODE:
        z_L = z_T

    if abs(z_T) > 3.10 or abs(z_L) > 3.10 or abs(z_S) > 3.10:
        w |= WARN__EXTREME_VARIABILITIES

    if plus10:
        sigma_L = 0.0
    else:
        delta_h_d__meter = terrain_roughness(d__meter, delta_h__meter)
        sigma_L = 10.0 * wn * delta_h_d__meter / (wn * delta_h_d__meter + 13.0)
    Y_L = sigma_L * z_L

    q = math.log(0.133 * wn)
    g_minus = _BFM1[c] + _BFM2[c] / ((_BFM3[c] * q) ** 2 + 1.0)
    g_plus = _BFP1[c] + _BFP2[c] / ((_BFP3[c] * q) ** 2 + 1.0)
    sigma_T_minus = _curve(_BSM1[c], _BSM2[c], _XSM1[c], _XSM2[c], _XSM3[c], d_e__meter) * g_minus
    sigma_T_plus = _curve(_BSP1[c], _BSP2[c], _XSP1[c], _XSP2[c], _XSP3[c], d_e__meter) * g_plus
    sigma_TD = _C_D[c] * sigma_T_plus
    tgtd = (sigma_T_plus - sigma_TD) * _Z_D[c]
    if z_T < 0.0:
        sigma_T = sigma_T_minus
    elif z_T <= _Z_D[c]:
        sigma_T = sigma_T_plus
    else:
        sigma_T = sigma_TD + tgtd / z_T
    Y_T = sigma_T * z_T

    Y_S_temp = sigma_S ** 2 + Y_T ** 2 / (7.8 + z_S ** 2) + Y_L ** 2 / (24.0 + z_S ** 2)
    if mdv == SINGLE_MESSAGE_MODE:
        Y_R = 0.0
        Y_S = math.sqrt(sigma_T ** 2 + sigma_L ** 2 + Y_S_temp) * z_S
    elif mdv == ACCIDENTAL_MODE:
        Y_R = Y_T
        Y_S = math.sqrt(sigma_L ** 2 + Y_S_temp) * z_S
    elif mdv == MOBILE_MODE:
        Y_R = math.sqrt(sigma_T ** 2 + sigma_L ** 2) * z_T
        Y_S = math.sqrt(Y_S_temp) * z_S
    else:
        Y_R = Y_T + Y_L
        Y_S = math.sqrt(Y_S_temp) * z_S

    result = A_ref__db - V_med__db - Y_R - Y_S
    if result < 0.0:
        result = result * (29.0 - result) / (29.0 - 10.0 * result)
    return result, w


# ---------------------------------------------------------------- public API
def profile_from_elevations(elevations_m, spacing_m):
    """Build an ITM pfl list [np, xi, z0, ..., z_np] from equally spaced elevations [m] (TX first)."""
    z = [float(v) for v in np.asarray(elevations_m, dtype=float).ravel()]
    if len(z) < 2:
        raise ValueError("need at least 2 elevation points")
    if not spacing_m > 0:
        raise ValueError("spacing_m must be > 0")
    return [float(len(z) - 1), float(spacing_m)] + z


def _result(A_db, A_fs, A_ref, warnings, d_km, propmode, theta_hzn, d_hzn, h_e, N_s, delta_h, extra=None):
    out = {
        "A_db": A_db,
        "A_fs_db": A_fs,
        "A_ref_db": A_ref,
        "warnings": warnings,
        "warning_names": warning_names(warnings),
        "d_km": d_km,
        "mode": propmode,
        "mode_name": MODE_NAMES[propmode],
        "theta_hzn": tuple(theta_hzn),
        "d_hzn_m": tuple(d_hzn),
        "h_e_m": tuple(h_e),
        "N_s": N_s,
        "delta_h_m": delta_h,
    }
    if extra:
        out.update(extra)
    return out


def itm_p2p_tls(h_tx_m, h_rx_m, pfl, climate, N_0, f_mhz, pol, epsilon, sigma, mdvar,
                time_pct, location_pct, situation_pct):
    """ITM point-to-point mode, time/location/situation variability (ITM_P2P_TLS_Ex).

    pfl: [np, xi, z0..z_np] (see profile_from_elevations). Returns a dict with A_db (basic transmission
    loss), A_fs_db, A_ref_db (median attenuation rel. free space before variability), warnings (bit
    field) and warning_names, d_km, mode (1 LOS / 2 diffraction / 3 troposcatter) and mode_name,
    theta_hzn [rad], d_hzn_m, h_e_m, N_s, delta_h_m. Raises ItmError (a ValueError) on hard errors."""
    pfl = [float(v) for v in pfl]
    warnings = validate_inputs(h_tx_m, h_rx_m, climate, time_pct, location_pct, situation_pct, N_0, f_mhz, pol,
                               epsilon, sigma, mdvar)
    d_km = (pfl[0] * pfl[1]) / 1000
    np_ = int(pfl[0])
    if np_ < 1 or len(pfl) < np_ + 3:
        raise ValueError(f"pfl too short: np={np_} needs {np_ + 3} values, got {len(pfl)}")
    p10 = int(0.1 * np_)
    h_sys__meter = 0.0
    for i in range(p10, np_ - p10 + 1):
        h_sys__meter += pfl[i + 2]
    h_sys__meter = h_sys__meter / (np_ - 2 * p10 + 1)
    Z_g, gamma_e, N_s = initialize_point_to_point(f_mhz, h_sys__meter, N_0, pol, epsilon, sigma)
    h__meter = (h_tx_m, h_rx_m)
    theta_hzn, d_hzn, h_e, delta_h, d__meter = quick_pfl(pfl, gamma_e, h__meter)
    A_ref, w, propmode = longley_rice(theta_hzn, f_mhz, Z_g, d_hzn, h_e, gamma_e, N_s, delta_h, h__meter, d__meter,
                                      MODE__P2P)
    warnings |= w
    A_fs = free_space_loss(d__meter, f_mhz)
    v, w = variability(time_pct, location_pct, situation_pct, h_e, delta_h, f_mhz, d__meter, A_ref, climate, mdvar)
    warnings |= w
    return _result(v + A_fs, A_fs, A_ref, warnings, d_km, propmode, theta_hzn, d_hzn, h_e, N_s, delta_h)


def itm_p2p_cr(h_tx_m, h_rx_m, pfl, climate, N_0, f_mhz, pol, epsilon, sigma, mdvar, confidence_pct,
               reliability_pct):
    """ITM point-to-point, confidence/reliability variability (ITM_P2P_CR_Ex): time = reliability,
    location = 50, situation = confidence."""
    try:
        return itm_p2p_tls(h_tx_m, h_rx_m, pfl, climate, N_0, f_mhz, pol, epsilon, sigma, mdvar,
                           reliability_pct, 50, confidence_pct)
    except ItmError as e:
        if e.code == 1003:
            raise ItmError(1007) from None
        if e.code == 1005:
            raise ItmError(1006) from None
        raise


def itm_area_tls(h_tx_m, h_rx_m, tx_siting, rx_siting, d_km, delta_h_m, climate, N_0, f_mhz, pol, epsilon,
                 sigma, mdvar, time_pct, location_pct, situation_pct):
    """ITM area mode, time/location/situation variability (ITM_AREA_TLS_Ex). Siting 0 random,
    1 careful, 2 very careful. Returns the same dict as itm_p2p_tls."""
    warnings = validate_inputs(h_tx_m, h_rx_m, climate, time_pct, location_pct, situation_pct, N_0, f_mhz, pol,
                               epsilon, sigma, mdvar)
    if d_km <= 0:
        raise ItmError(1017)
    if delta_h_m < 0:
        raise ItmError(1018)
    if tx_siting not in (0, 1, 2):
        raise ItmError(1019)
    if rx_siting not in (0, 1, 2):
        raise ItmError(1020)
    h__meter = (h_tx_m, h_rx_m)
    Z_g, gamma_e, N_s = initialize_point_to_point(f_mhz, 0.0, N_0, pol, epsilon, sigma)
    h_e, d_hzn, theta_hzn = initialize_area((tx_siting, rx_siting), gamma_e, delta_h_m, h__meter)
    d__meter = d_km * 1000
    A_ref, w, propmode = longley_rice(theta_hzn, f_mhz, Z_g, d_hzn, h_e, gamma_e, N_s, delta_h_m, h__meter, d__meter,
                                      MODE__AREA)
    warnings |= w
    A_fs = free_space_loss(d__meter, f_mhz)
    v, w = variability(time_pct, location_pct, situation_pct, h_e, delta_h_m, f_mhz, d__meter, A_ref, climate, mdvar)
    warnings |= w
    return _result(A_fs + v, A_fs, A_ref, warnings, d_km, propmode, theta_hzn, d_hzn, h_e, N_s, delta_h_m)


def itm_area_cr(h_tx_m, h_rx_m, tx_siting, rx_siting, d_km, delta_h_m, climate, N_0, f_mhz, pol, epsilon, sigma,
                mdvar, confidence_pct, reliability_pct):
    """ITM area mode, confidence/reliability variability (ITM_AREA_CR_Ex)."""
    try:
        return itm_area_tls(h_tx_m, h_rx_m, tx_siting, rx_siting, d_km, delta_h_m, climate, N_0, f_mhz, pol, epsilon,
                            sigma, mdvar, reliability_pct, 50, confidence_pct)
    except ItmError as e:
        if e.code == 1003:
            raise ItmError(1007) from None
        if e.code == 1005:
            raise ItmError(1006) from None
        raise
