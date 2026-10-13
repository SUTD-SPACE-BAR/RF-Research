"""Radar range equation, detection SNR (Albersheim), pulse and FMCW parameters, Doppler, simple RCS.

Albersheim's equation is ported from tools/verify/radar_detection_cfar.py (W2-B4), which checks it
against exact Swerling-0 results (page kb/11-radar/detection-theory-cfar.md).
Range equation and FMCW relations: Skolnik, Radar Handbook 3rd ed. ch. 1; Richards, Fundamentals of
Radar Signal Processing 2nd ed. ch. 2; Iovescu & Rao, "The fundamentals of millimeter wave sensors",
TI white paper SPYY005 (2017) for the FMCW chirp relations.
"""
import math

import numpy as np

from .constants import C0, K_B, T0


def _lin(db):
    return 10 ** (db / 10)


# ------------------------------------------------------------------ range equation
def radar_received_power_w(pt_w, gt_dbi, gr_dbi, f_hz, rcs_m2, r_m, losses_db=0.0):
    """Monostatic/bistatic-at-equal-range received power:
    Pr = Pt Gt Gr lambda^2 sigma / ((4 pi)^3 R^4 L)."""
    lam = C0 / f_hz
    return pt_w * _lin(gt_dbi) * _lin(gr_dbi) * lam ** 2 * rcs_m2 / ((4 * math.pi) ** 3 * r_m ** 4 * _lin(losses_db))


def radar_snr_db(pt_w, gt_dbi, gr_dbi, f_hz, rcs_m2, r_m, nf_db, bw_hz=None, t_int_s=None,
                 losses_db=0.0, ts_k=None):
    """Single-look SNR [dB].  Give either the noise bandwidth bw_hz (SNR = Pr / (k Ts B)) or the
    coherent integration time t_int_s (SNR = Pr T / (k Ts), i.e. B = 1/T: the matched-filter/FFT form
    used for FMCW and pulse-Doppler). Ts defaults to T0 F (source at 290 K)."""
    pr = radar_received_power_w(pt_w, gt_dbi, gr_dbi, f_hz, rcs_m2, r_m, losses_db)
    ts = T0 * _lin(nf_db) if ts_k is None else ts_k + T0 * (_lin(nf_db) - 1)
    if (bw_hz is None) == (t_int_s is None):
        raise ValueError("give exactly one of bw_hz or t_int_s")
    b = bw_hz if bw_hz is not None else 1.0 / t_int_s
    return 10 * math.log10(pr / (K_B * ts * b))


def radar_max_range_m(pt_w, gt_dbi, gr_dbi, f_hz, rcs_m2, snr_min_db, nf_db, bw_hz=None, t_int_s=None,
                      losses_db=0.0):
    """Range at which the SNR falls to snr_min_db (inverse of radar_snr_db; R ~ (.)^(1/4))."""
    snr_1m = radar_snr_db(pt_w, gt_dbi, gr_dbi, f_hz, rcs_m2, 1.0, nf_db, bw_hz, t_int_s, losses_db)
    return 10 ** ((snr_1m - snr_min_db) / 40.0)


def albersheim_snr_db(pd, pfa, n=1):
    """Albersheim's approximation of the single-pulse SNR [dB] required for a non-fluctuating target,
    N non-coherently integrated pulses (linear detector). Valid 1e-7 <= Pfa <= 1e-3, 0.1 <= Pd <= 0.9."""
    A = math.log(0.62 / pfa)
    B = math.log(pd / (1 - pd))
    return -5 * math.log10(n) + (6.2 + 4.54 / math.sqrt(n + 0.44)) * math.log10(A + 0.12 * A * B + 1.7 * B)


# ------------------------------------------------------------------ pulse radar
def range_resolution_m(bw_hz):
    """Range resolution c / (2 B) (pulse compression or FMCW sweep bandwidth B)."""
    return C0 / (2 * bw_hz)


def unambiguous_range_m(prf_hz):
    return C0 / (2 * prf_hz)


def doppler_shift_hz(v_radial_mps, f_hz):
    """Two-way (monostatic) Doppler shift 2 v / lambda (positive for approaching)."""
    return 2 * v_radial_mps * f_hz / C0


def one_way_doppler_hz(v_radial_mps, f_hz):
    """One-way (e.g. rocket beacon to ground) Doppler v / lambda."""
    return v_radial_mps * f_hz / C0


# ------------------------------------------------------------------ FMCW
def fmcw_params(f0_hz, bw_hz, t_chirp_s, fs_if_hz, n_chirps=128, t_frame_s=None, complex_if=True):
    """Key FMCW-radar quantities (TI SPYY005 relations).

    slope S = B/Tc; range resolution c/(2B); beat frequency f_b = 2 S R / c;
    max range limited by IF sampling: R_max = f_IF,max c / (2 S) with f_IF,max = fs (complex) or fs/2 (real);
    max unambiguous velocity lambda/(4 Tc) (chirp repetition = Tc); velocity resolution lambda/(2 N Tc).
    """
    lam = C0 / f0_hz
    s = bw_hz / t_chirp_s
    f_if_max = fs_if_hz if complex_if else fs_if_hz / 2
    t_frame = t_frame_s if t_frame_s is not None else n_chirps * t_chirp_s
    return dict(
        wavelength_m=lam,
        slope_hz_per_s=s,
        range_resolution_m=C0 / (2 * bw_hz),
        max_range_m=f_if_max * C0 / (2 * s),
        v_max_mps=lam / (4 * t_chirp_s),
        v_resolution_mps=lam / (2 * t_frame),
        beat_hz_per_m=2 * s / C0,
    )


def fmcw_beat_frequency_hz(r_m, bw_hz, t_chirp_s):
    return 2 * (bw_hz / t_chirp_s) * r_m / C0


# ------------------------------------------------------------------ RCS of canonical targets
def rcs_sphere_m2(radius_m):
    """Optical-region sphere (radius >> lambda/(2 pi)): pi a^2."""
    return math.pi * radius_m ** 2


def rcs_flat_plate_m2(area_m2, f_hz):
    """Flat plate at normal incidence: 4 pi A^2 / lambda^2."""
    lam = C0 / f_hz
    return 4 * math.pi * area_m2 ** 2 / lam ** 2


def rcs_trihedral_m2(edge_m, f_hz):
    """Triangular trihedral corner reflector, peak: 4 pi a^4 / (3 lambda^2), a = edge length."""
    lam = C0 / f_hz
    return 4 * math.pi * edge_m ** 4 / (3 * lam ** 2)


def dbsm(rcs_m2):
    return 10 * math.log10(rcs_m2)
