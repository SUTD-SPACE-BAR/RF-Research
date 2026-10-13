"""Lumped matching networks (L, pi, T), reactance <-> component values, finite-Q loss,
single shunt stub and quarter-wave transformer.

Ported from tools/verify/tline_matching.py (W1-A4). Page:
kb/03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md
(Pozar, Microwave Engineering, 4th ed., sec. 5.1-5.2 closed forms).

Sign convention: X > 0 is inductive (series L), X < 0 capacitive; B > 0 capacitive (shunt C),
B < 0 inductive (shunt L). All networks match load ZL to a real source/reference Z0.
"""
import math
from dataclasses import dataclass

import numpy as np


def x_to_component(x_ohm, f_hz):
    """Series reactance -> ('L', henry) or ('C', farad)."""
    w = 2 * math.pi * f_hz
    if x_ohm >= 0:
        return ("L", x_ohm / w)
    return ("C", -1.0 / (w * x_ohm))


def b_to_component(b_s, f_hz):
    """Shunt susceptance -> ('C', farad) for B > 0 or ('L', henry) for B < 0."""
    w = 2 * math.pi * f_hz
    if b_s >= 0:
        return ("C", b_s / w)
    return ("L", -1.0 / (w * b_s))


def reactance_l(l_h, f_hz):
    return 2 * math.pi * f_hz * l_h


def reactance_c(c_f, f_hz):
    """Reactance of a capacitor (negative number)."""
    return -1.0 / (2 * math.pi * f_hz * c_f)


@dataclass
class LMatch:
    topology: str      # 'shunt-at-load' (R_L > Z0) or 'series-at-load' (R_L < Z0)
    x_series: float    # ohm
    b_shunt: float     # siemens
    f_hz: float = None

    def components(self, f_hz=None):
        f = f_hz or self.f_hz
        return {"series": x_to_component(self.x_series, f), "shunt": b_to_component(self.b_shunt, f)}

    def zin(self, zl, z0=50.0):
        """Impedance seen by the source (should equal z0)."""
        if self.topology == "shunt-at-load":
            return 1 / (1 / zl + 1j * self.b_shunt) + 1j * self.x_series
        return 1 / (1 / (zl + 1j * self.x_series) + 1j * self.b_shunt)


def l_match(zl, z0=50.0, f_hz=None):
    """Both L-network solutions matching complex zl to real z0 (Pozar 5.1).

    R_L > Z0: shunt B across the load, series X toward the source ('shunt-at-load').
    R_L < Z0: series X at the load, shunt B toward the source ('series-at-load').
    Each topology has two solutions (low-pass-like and high-pass-like); both are returned.
    (A load inside the 1 + jx circle can sometimes also be matched by the other topology; this
    function returns the pair that always exists.)
    """
    zl = complex(zl)
    rl, xl = zl.real, zl.imag
    sols = []
    if rl > z0:
        for s in (+1, -1):
            b = (xl + s * math.sqrt(rl / z0) * math.sqrt(rl ** 2 + xl ** 2 - z0 * rl)) / (rl ** 2 + xl ** 2)
            x = 1 / b + xl * z0 / rl - z0 / (b * rl)
            sols.append(LMatch("shunt-at-load", x, b, f_hz))
    else:
        for s in (+1, -1):
            x = s * math.sqrt(rl * (z0 - rl)) - xl
            b = s * math.sqrt((z0 - rl) / rl) / z0
            sols.append(LMatch("series-at-load", x, b, f_hz))
    return sols


def l_match_real(r1, r2):
    """Real-to-real L network: returns (Q, X_series on the low-R side, X_shunt on the high-R side)
    for the low-pass form (series L, shunt C). Q = sqrt(Rhigh/Rlow - 1)."""
    rh, rlo = max(r1, r2), min(r1, r2)
    q = math.sqrt(rh / rlo - 1)
    return q, q * rlo, -rh / q


def pi_match(rs, rl, q):
    """Low-pass pi network (shunt C - series L - shunt C) between real rs and rl with loaded Q q
    defined on the higher-R side (virtual resistance Rv = Rhigh/(q^2+1)).
    Returns dict(Rv, X_shunt_src, X_series, X_shunt_load) in ohm."""
    rh = max(rs, rl)
    rv = rh / (q ** 2 + 1)
    if rv >= min(rs, rl):
        raise ValueError("Q too low for a pi network: need Q > sqrt(Rhigh/Rlow - 1)")
    q1 = math.sqrt(rs / rv - 1)
    q2 = math.sqrt(rl / rv - 1)
    return dict(Rv=rv, X_shunt_src=-rs / q1, X_series=q1 * rv + q2 * rv, X_shunt_load=-rl / q2)


def t_match(rs, rl, q):
    """Low-pass T network (series L - shunt C - series L) with Q defined on the lower-R side
    (virtual resistance Rv = Rlow (q^2 + 1)). Returns dict(Rv, X_series_src, X_shunt, X_series_load)."""
    rlo = min(rs, rl)
    rv = rlo * (q ** 2 + 1)
    q1 = math.sqrt(rv / rs - 1)
    q2 = math.sqrt(rv / rl - 1)
    xp1, xp2 = -rv / q1, -rv / q2
    xp = 1 / (1 / xp1 + 1 / xp2)
    return dict(Rv=rv, X_series_src=q1 * rs, X_shunt=xp, X_series_load=q2 * rl)


def l_match_loss_db(q_network, q_inductor, q_capacitor=None):
    """Estimated insertion loss of an L network with finite component Q:
    IL ~ 10 log10(1 + Qn/QL + Qn/QC)."""
    s = q_network / q_inductor
    if q_capacitor:
        s += q_network / q_capacitor
    return 10 * math.log10(1 + s)


def l_match_bandwidth(q_network):
    """Rough fractional bandwidth of a single L section ~ 1/Q (3 dB loaded-Q sense)."""
    return 1.0 / q_network


def quarter_wave_z(z0, zl):
    """Characteristic impedance of a quarter-wave transformer between real z0 and zl."""
    return math.sqrt(z0 * zl)


def shunt_stub(zl, z0=50.0):
    """Single shunt-stub tuner (Pozar 5.2). Returns list of dicts with the distance d from the load
    and the open/short stub lengths, all in wavelengths on the line."""
    zl = complex(zl)
    rl, xl = zl.real, zl.imag
    out = []
    if abs(rl - z0) < 1e-12:
        ts = [-xl / (2 * z0)]
    else:
        root = math.sqrt(rl * ((z0 - rl) ** 2 + xl ** 2) / z0)
        ts = [(xl + root) / (rl - z0), (xl - root) / (rl - z0)]
    for t in ts:
        d = (math.atan(t) / (2 * math.pi)) % 0.5
        b = (rl ** 2 * t - (z0 - xl * t) * (xl + z0 * t)) / (z0 * (rl ** 2 + (xl + z0 * t) ** 2))
        lo = (math.atan(-b * z0) / (2 * math.pi)) % 0.5
        ls = (math.atan(1 / (b * z0)) / (2 * math.pi)) % 0.5
        out.append(dict(d_lambda=d, open_lambda=lo, short_lambda=ls))
    return out


def zin_line(zl, z0, beta_l_rad):
    """Input impedance of a lossless line of electrical length beta*l terminated in zl."""
    t = np.tan(beta_l_rad)
    return z0 * (zl + 1j * z0 * t) / (z0 + 1j * zl * t)
