#!/usr/bin/env python3
"""Typical S-parameters and noise parameters of the Avago/Broadcom ATF-54143 E-pHEMT.

Re-typed (facts/numbers, no prose) from the ATF-54143 data sheet, tables
"ATF-54143 Typical Scattering Parameters, VDS = 3V, IDS = 60 mA" and
"Typical Noise Parameters, VDS = 3V, IDS = 60 mA".
Reference planes: end of gate lead / end of drain lead, source grounded by
four 0.020" vias on 0.025" alumina (data-sheet note 2).  Fmin below 2 GHz is
extrapolated by the manufacturer (data-sheet note 1).

Used by rfckt_stability.py and rfckt_lna.py.  Import helpers:
    from rfckt_atf54143_data import sparams_network, noise_table, interp_s, interp_noise
"""
import numpy as np

# f_GHz, |S11|, ang S11, |S21|, ang S21, |S12|, ang S12, |S22|, ang S22, MSG/MAG_dB(datasheet)
S_TABLE = np.array([
    [0.1, 0.99, -18.9, 27.66, 167.6, 0.01, 80.0, 0.54, -14.0, 34.42],
    [0.5, 0.81, -80.8, 20.05, 128.0, 0.03, 52.4, 0.40, -58.8, 28.25],
    [0.9, 0.71, -117.9, 14.01, 106.2, 0.04, 41.8, 0.29, -83.8, 25.44],
    [1.0, 0.69, -124.4, 12.94, 102.2, 0.05, 40.4, 0.27, -88.5, 24.13],
    [1.5, 0.64, -149.8, 9.34, 86.1, 0.05, 36.1, 0.21, -105.2, 22.71],
    [1.9, 0.62, -164.9, 7.64, 75.6, 0.06, 33.8, 0.17, -114.7, 21.05],
    [2.0, 0.62, -168.3, 7.31, 73.3, 0.06, 33.3, 0.17, -117.0, 20.86],
    [2.5, 0.60, 176.2, 6.01, 61.8, 0.07, 30.1, 0.13, -129.7, 19.34],
    [3.0, 0.60, 162.3, 5.10, 51.0, 0.08, 26.5, 0.11, -146.5, 18.04],
    [4.0, 0.62, 137.1, 3.90, 30.8, 0.09, 17.1, 0.10, 165.2, 14.87],
    [5.0, 0.66, 115.5, 3.11, 11.7, 0.11, 6.8, 0.14, 131.5, 13.27],
    [6.0, 0.69, 97.2, 2.58, -6.4, 0.12, -3.9, 0.18, 112.4, 11.72],
    [7.0, 0.70, 80.2, 2.20, -24.0, 0.13, -15.8, 0.20, 94.3, 10.22],
    [8.0, 0.72, 62.2, 1.90, -41.8, 0.14, -28.0, 0.23, 70.1, 9.02],
    [9.0, 0.76, 45.0, 1.66, -59.9, 0.15, -39.6, 0.29, 50.6, 8.38],
    [10.0, 0.83, 28.4, 1.42, -78.7, 0.15, -55.1, 0.38, 36.8, 8.71],
])

# f_GHz, Fmin_dB, |Gopt|, ang Gopt (deg), Rn/50, Ga_dB (associated gain)
N_TABLE = np.array([
    [0.5, 0.15, 0.34, 42.3, 0.04, 28.50],
    [0.9, 0.20, 0.32, 62.8, 0.04, 24.18],
    [1.0, 0.22, 0.32, 67.6, 0.04, 23.47],
    [1.9, 0.42, 0.27, 116.3, 0.04, 18.67],
    [2.0, 0.45, 0.27, 120.1, 0.04, 18.29],
    [2.4, 0.52, 0.26, 145.8, 0.04, 16.65],
    [3.0, 0.59, 0.29, 178.0, 0.05, 15.56],
    [3.9, 0.70, 0.36, -145.4, 0.05, 13.53],
    [5.0, 0.93, 0.47, -116.0, 0.10, 12.13],
    [5.8, 1.16, 0.52, -98.9, 0.18, 11.10],
    [6.0, 1.19, 0.55, -96.5, 0.20, 10.95],
])


def _polar(mag, ang_deg):
    return mag * np.exp(1j * np.deg2rad(ang_deg))


def s_matrix_table():
    """Return f (Hz) and S (N,2,2) complex array from the table."""
    f = S_TABLE[:, 0] * 1e9
    S = np.zeros((len(f), 2, 2), complex)
    S[:, 0, 0] = _polar(S_TABLE[:, 1], S_TABLE[:, 2])
    S[:, 1, 0] = _polar(S_TABLE[:, 3], S_TABLE[:, 4])
    S[:, 0, 1] = _polar(S_TABLE[:, 5], S_TABLE[:, 6])
    S[:, 1, 1] = _polar(S_TABLE[:, 7], S_TABLE[:, 8])
    return f, S


def _interp_polar(fq, f, mag, ang):
    """Interpolate magnitude linearly and unwrapped phase linearly."""
    ang_u = np.rad2deg(np.unwrap(np.deg2rad(ang)))
    return _polar(np.interp(fq, f, mag), np.interp(fq, f, ang_u))


def interp_s(f_hz):
    """S-matrix at arbitrary frequencies (Hz) by mag/unwrapped-phase interpolation."""
    f_hz = np.atleast_1d(f_hz)
    ft = S_TABLE[:, 0] * 1e9
    S = np.zeros((len(f_hz), 2, 2), complex)
    for (i, j), (cm, ca) in {(0, 0): (1, 2), (1, 0): (3, 4), (0, 1): (5, 6), (1, 1): (7, 8)}.items():
        S[:, i, j] = _interp_polar(f_hz, ft, S_TABLE[:, cm], S_TABLE[:, ca])
    return S


def interp_noise(f_hz):
    """Return (Fmin_linear, Gamma_opt, Rn_ohm) at f (Hz); clamps below 0.5 GHz to the 0.5 GHz row."""
    f_hz = np.atleast_1d(f_hz)
    ft = N_TABLE[:, 0] * 1e9
    fmin_db = np.interp(f_hz, ft, N_TABLE[:, 1])
    gopt = _interp_polar(f_hz, ft, N_TABLE[:, 2], N_TABLE[:, 3])
    rn = np.interp(f_hz, ft, N_TABLE[:, 4]) * 50.0
    return 10 ** (fmin_db / 10), gopt, rn


def sparams_network(f_hz=None, with_noise=False):
    """scikit-rf Network of the device (interpolated onto f_hz if given)."""
    import skrf as rf
    if f_hz is None:
        f_hz, S = s_matrix_table()
    else:
        S = interp_s(f_hz)
    ntw = rf.Network(frequency=rf.Frequency.from_f(f_hz, unit='hz'), s=S, z0=50, name='ATF-54143 3V60mA')
    if with_noise:
        fmin, gopt, rn = interp_noise(f_hz)
        ntw.set_noise_a(ntw.frequency, nfmin_db=10 * np.log10(fmin), gamma_opt=gopt, rn=rn)
    return ntw


if __name__ == '__main__':
    f, S = s_matrix_table()
    print('rows:', len(f), 'f range GHz', f[0] / 1e9, f[-1] / 1e9)
    print('S at 433 MHz (interp):', np.round(interp_s(433e6)[0], 3))
    print('noise at 1575.42 MHz (interp):', interp_noise(1575.42e6))
