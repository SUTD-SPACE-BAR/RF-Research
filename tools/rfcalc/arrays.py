"""Uniform linear array (ULA): array factor, steering phase, beamwidth, grating-lobe limit, directivity.

Ported from tools/verify/array_factor.py (W2-B5). Page: kb/12-phased-arrays/array-factor-linear-arrays.md.
Angles theta are measured from broadside (theta = 0 is perpendicular to the array axis).
"""
import math

import numpy as np


def array_factor(theta_deg, n, d_lambda, steer_deg=0.0, weights=None, normalise=True):
    """Complex array factor of an N-element ULA with spacing d (in wavelengths), progressive phase
    steering to steer_deg, optional amplitude weights. |AF| normalised to 1 at the steer angle."""
    th = np.radians(np.asarray(theta_deg, float))
    k_d = 2 * np.pi * d_lambda
    idx = np.arange(n)
    w = np.ones(n) if weights is None else np.asarray(weights, float)
    phase = k_d * (np.sin(th)[..., None] - math.sin(math.radians(steer_deg))) * idx
    af = np.sum(w * np.exp(1j * phase), axis=-1)
    return af / np.sum(w) if normalise else af


def array_factor_db(theta_deg, n, d_lambda, steer_deg=0.0, weights=None):
    return 20 * np.log10(np.maximum(np.abs(array_factor(theta_deg, n, d_lambda, steer_deg, weights)), 1e-12))


def steering_phase_deg(d_lambda, steer_deg):
    """Progressive element-to-element phase for a steer angle: 360 d sin(theta0) [deg]."""
    return 360.0 * d_lambda * math.sin(math.radians(steer_deg))


def hpbw_deg(n, d_lambda, steer_deg=0.0):
    """Approximate half-power beamwidth 0.886 lambda / (N d cos theta0) (uniform weights, not near endfire)."""
    return math.degrees(0.886 / (n * d_lambda * math.cos(math.radians(steer_deg))))


def first_null_deg(n, d_lambda):
    """First null of a broadside ULA: sin(theta) = 1/(N d)."""
    return math.degrees(math.asin(1.0 / (n * d_lambda)))


def max_spacing_no_grating(steer_max_deg, n=None):
    """Largest spacing (in wavelengths) with no grating lobe in visible space when steering to
    steer_max_deg: d < 1/(1 + |sin theta0|) (the strict large-N form; with N elements the grating lobe
    peak is still partly outside if d < (1 - 1/N)/(1 + |sin theta0|))."""
    s = abs(math.sin(math.radians(steer_max_deg)))
    return (1.0 if n is None else (1 - 1.0 / n)) / (1 + s)


def directivity_ula(n, d_lambda, steer_deg=0.0, weights=None):
    """Exact directivity of a ULA of isotropic elements (closed-form sphere integral
    D = |sum w|^2 / sum_m sum_n w_m w_n* sinc(k (x_m - x_n)))."""
    w = np.ones(n) if weights is None else np.asarray(weights, float)
    x = np.arange(n) * d_lambda
    k = 2 * np.pi
    u0 = math.sin(math.radians(steer_deg))
    ws = w * np.exp(-1j * k * x * u0)
    dx = x[:, None] - x[None, :]
    S = np.sinc(k * dx / np.pi)
    den = np.real(np.conj(ws)[:, None] * ws[None, :] * S).sum()
    return float(np.abs(np.sum(w)) ** 2 / den)


def array_gain_db(n_elements):
    """Coherent-combining SNR gain with uncorrelated per-channel noise: 10 log10 N."""
    return 10 * math.log10(n_elements)
