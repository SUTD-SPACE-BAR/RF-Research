"""Decibel, power, voltage, field-strength and mismatch conversions.

Consolidates the conversions used in kb/00-math-foundations/decibels-and-log-units.md and
kb/03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md.
Logic cross-checked against tools/verify/math_decibels.py (W1-A1).

All functions accept scalars or numpy arrays.
"""
import math

import numpy as np

from .constants import C0, ETA0, Z0_REF

# ------------------------------------------------------------------ plain dB
def db(x_ratio):
    """Power ratio -> dB: 10 log10(x)."""
    return 10.0 * np.log10(x_ratio)


def undb(x_db):
    """dB -> power ratio: 10^(x/10)."""
    return 10.0 ** (np.asarray(x_db, dtype=float) / 10.0)


def db20(v_ratio):
    """Voltage/field amplitude ratio -> dB: 20 log10(|v|)."""
    return 20.0 * np.log10(np.abs(v_ratio))


def undb20(x_db):
    """dB -> amplitude ratio: 10^(x/20)."""
    return 10.0 ** (np.asarray(x_db, dtype=float) / 20.0)


# ------------------------------------------------------------------ absolute power
def dbm_to_w(p_dbm):
    """dBm -> watts."""
    return 1e-3 * undb(p_dbm)


def w_to_dbm(p_w):
    """watts -> dBm."""
    return 10.0 * np.log10(np.asarray(p_w, dtype=float) / 1e-3)


def dbw_to_dbm(p_dbw):
    return np.asarray(p_dbw, dtype=float) + 30.0


def dbm_to_vrms(p_dbm, r=Z0_REF):
    """RMS voltage across a resistor r that dissipates p_dbm."""
    return np.sqrt(dbm_to_w(p_dbm) * r)


def vrms_to_dbm(v_rms, r=Z0_REF):
    return w_to_dbm(np.asarray(v_rms, dtype=float) ** 2 / r)


def dbm_to_vpk(p_dbm, r=Z0_REF):
    """Peak voltage of a sinusoid delivering p_dbm into r."""
    return math.sqrt(2.0) * dbm_to_vrms(p_dbm, r)


def dbm_to_dbuv(p_dbm, r=Z0_REF):
    """dBm into r -> dBuV (RMS). For 50 ohm: dBuV = dBm + 106.99."""
    return 20.0 * np.log10(dbm_to_vrms(p_dbm, r) / 1e-6)


def dbuv_to_dbm(v_dbuv, r=Z0_REF):
    v = 1e-6 * undb20(v_dbuv)
    return vrms_to_dbm(v, r)


def add_powers_dbm(*p_dbm):
    """Sum of uncorrelated powers given in dBm (e.g. -95 and -101 dBm -> -94.03 dBm)."""
    return w_to_dbm(np.sum([dbm_to_w(p) for p in p_dbm], axis=0))


def subtract_power_dbm(total_dbm, noise_dbm):
    """Signal power from a (signal+noise) reading and a noise-only reading (both dBm)."""
    return w_to_dbm(dbm_to_w(total_dbm) - dbm_to_w(noise_dbm))


# ------------------------------------------------------------------ field strength
def eirp_to_field_vpm(eirp_w, d_m):
    """Far-field RMS electric field [V/m] at distance d from an EIRP (free space):
    E = sqrt(eta0 EIRP / (4 pi d^2)) ~ sqrt(30 EIRP)/d."""
    return np.sqrt(ETA0 * np.asarray(eirp_w, float) / (4 * np.pi * np.asarray(d_m, float) ** 2))


def field_dbuvm_to_dbm(e_dbuvm, f_hz, g_dbi=0.0):
    """Power available from a matched antenna of gain g_dbi in a plane-wave field e_dbuvm (dBuV/m).
    P = E^2/eta0 * G lambda^2/(4 pi).  (Worked example: 40 dBuV/m at 433 MHz, 0 dBi -> -89.9 dBm.)"""
    e = 1e-6 * undb20(e_dbuvm)
    lam = C0 / np.asarray(f_hz, float)
    p_w = e ** 2 / ETA0 * undb(g_dbi) * lam ** 2 / (4 * np.pi)
    return w_to_dbm(p_w)


def antenna_factor_db(f_hz, g_dbi=0.0, z=Z0_REF):
    """Antenna factor AF = E/V [dB(1/m)] for a matched antenna of gain g_dbi into z ohm.
    AF = sqrt(4 pi eta0 / (z G lambda^2))."""
    lam = C0 / np.asarray(f_hz, float)
    af = np.sqrt(4 * np.pi * ETA0 / (z * undb(g_dbi) * lam ** 2))
    return 20 * np.log10(af)


# ------------------------------------------------------------------ mismatch
def gamma_from_z(z, z0=Z0_REF):
    """Reflection coefficient of load z on a z0 reference."""
    z = np.asarray(z, dtype=complex)
    return (z - z0) / (z + z0)


def z_from_gamma(g, z0=Z0_REF):
    g = np.asarray(g, dtype=complex)
    return z0 * (1 + g) / (1 - g)


def vswr_from_gamma(g):
    m = np.abs(g)
    return (1 + m) / (1 - m)


def gamma_from_vswr(s):
    s = np.asarray(s, dtype=float)
    return (s - 1) / (s + 1)


def return_loss_db(g):
    """Return loss (positive number) = -20 log10|Gamma|."""
    return -20.0 * np.log10(np.abs(g))


def gamma_from_rl(rl_db):
    return undb20(-np.asarray(rl_db, float))


def mismatch_loss_db(g):
    """Mismatch loss (positive number) = -10 log10(1 - |Gamma|^2)."""
    return -10.0 * np.log10(1 - np.abs(g) ** 2)


def vswr_to_rl(s):
    return return_loss_db(gamma_from_vswr(s))


def rl_to_vswr(rl_db):
    return vswr_from_gamma(gamma_from_rl(rl_db))


# ------------------------------------------------------------------ wavelength
def wavelength(f_hz, eps_eff=1.0):
    """Wavelength [m] in a medium with effective permittivity eps_eff."""
    return C0 / (np.asarray(f_hz, float) * np.sqrt(eps_eff))
