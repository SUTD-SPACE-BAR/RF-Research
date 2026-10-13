"""Thermal noise, noise figure / temperature, receiver cascade (Friis NF, gain, IIP3, P1dB),
sensitivity, MDS and spurious-free dynamic range.

Ported from tools/verify/noise_cascade.py, noise_thermal.py, noise_sensitivity.py and
noise_ip3_twotone.py (W1-A5). Pages: kb/07-noise-linearity/noise-figure-and-friis.md,
receiver-cascade-analysis.md, sensitivity-and-mds.md, thermal-noise-and-noise-temperature.md,
nonlinearity-p1db-ip3-intermod.md, dynamic-range-sfdr-blocking.md.

Conventions: gains/NF in dB, powers in dBm, all interfaces matched (available gain = transducer gain).
A passive stage given without an NF gets NF = loss (valid at physical temperature 290 K).
Cascade IIP3 is the worst-case (coherent) sum 1/IIP3 = sum G_before,i / IIP3_i (linear, mW).
"""
from dataclasses import dataclass
from typing import Optional

import numpy as np

from .constants import K_B, KT0_DBM_HZ, T0


def db2lin(x):
    return 10.0 ** (np.asarray(x, dtype=float) / 10.0)


def lin2db(x):
    return 10.0 * np.log10(x)


# ------------------------------------------------------------------ thermal noise
def ktb_dbm(bw_hz, t_k=T0):
    """Available thermal noise power k T B [dBm]."""
    return 10 * np.log10(K_B * t_k * np.asarray(bw_hz, float) / 1e-3)


def noise_voltage_rms(r_ohm, bw_hz, t_k=T0):
    """Open-circuit thermal noise voltage sqrt(4 k T R B) [V rms]."""
    return np.sqrt(4 * K_B * t_k * r_ohm * bw_hz)


def nf_to_te(nf_db):
    """Noise figure [dB] -> equivalent noise temperature [K]: Te = T0 (F - 1)."""
    return T0 * (db2lin(nf_db) - 1.0)


def te_to_nf(te_k):
    return lin2db(1.0 + np.asarray(te_k, float) / T0)


def lossy_line_te(loss_db, t_phys=T0):
    """Te of a matched passive attenuator of loss L at physical temperature Tp: Te = (L - 1) Tp."""
    return (db2lin(loss_db) - 1.0) * t_phys


def lossy_line_nf(loss_db, t_phys=T0):
    """NF of a passive loss at Tp: F = 1 + (L - 1) Tp / T0 (= L at Tp = T0)."""
    return lin2db(1 + (db2lin(loss_db) - 1.0) * t_phys / T0)


def antenna_temp_through_loss(ta_k, loss_db, t_phys=T0):
    """Noise temperature at the output of a lossy feeder: Ta/L + Tp (1 - 1/L)."""
    L = db2lin(loss_db)
    return ta_k / L + t_phys * (1 - 1 / L)


# ------------------------------------------------------------------ cascade
@dataclass
class Stage:
    name: str
    gain: float                    # dB (negative for a loss)
    nf: Optional[float] = None     # dB; None -> loss for passive, 0 for active
    iip3: Optional[float] = None   # dBm (input-referred)
    ip1db: Optional[float] = None  # dBm (input-referred)

    def __post_init__(self):
        self.gain = float(self.gain)
        if self.nf is None:
            self.nf = -self.gain if self.gain <= 0 else 0.0
        self.nf = float(self.nf)


def cascade(stages):
    """Cumulative gain / NF / Te / IIP3 / IP1dB after each stage.

    Returns a list of dicts (one per stage) with keys G_cum_dB, NF_cum_dB, Te_cum_K,
    IIP3_cum_dBm (coherent), IIP3_cum_pw_dBm (power-addition variant), IP1dB_cum_dBm, OIP3_cum_dBm.
    """
    out = []
    g_cum = 1.0
    f_tot = 1.0
    inv_iip3 = 0.0
    inv_iip3_pw = 0.0
    inv_p1 = 0.0
    for i, s in enumerate(stages):
        F = float(db2lin(s.nf))
        f_tot = F if i == 0 else f_tot + (F - 1.0) / g_cum
        if s.iip3 is not None:
            term = g_cum / float(db2lin(s.iip3))
            inv_iip3 += term
            inv_iip3_pw += term ** 2
        if s.ip1db is not None:
            inv_p1 += g_cum / float(db2lin(s.ip1db))
        g_cum *= float(db2lin(s.gain))
        iip3 = lin2db(1.0 / inv_iip3) if inv_iip3 > 0 else np.inf
        out.append(dict(
            name=s.name,
            G_cum_dB=float(lin2db(g_cum)),
            NF_cum_dB=float(lin2db(f_tot)),
            Te_cum_K=float(T0 * (f_tot - 1.0)),
            IIP3_cum_dBm=float(iip3),
            IIP3_cum_pw_dBm=float(lin2db(1.0 / np.sqrt(inv_iip3_pw)) if inv_iip3_pw > 0 else np.inf),
            IP1dB_cum_dBm=float(lin2db(1.0 / inv_p1) if inv_p1 > 0 else np.inf),
            OIP3_cum_dBm=float(iip3 + lin2db(g_cum)),
        ))
    return out


def cascade_nf_db(stages):
    return cascade(stages)[-1]["NF_cum_dB"]


def noise_contributions(stages):
    """Fraction of the input-referred excess noise temperature contributed by each stage,
    and the total Te [K]."""
    g_cum = 1.0
    contrib = []
    for s in stages:
        te_i = T0 * (float(db2lin(s.nf)) - 1.0)
        contrib.append(te_i / g_cum)
        g_cum *= float(db2lin(s.gain))
    tot = sum(contrib)
    return [c / tot for c in contrib], tot


def friis_nf_db(nf_db_list, gain_db_list):
    """Plain Friis formula F = F1 + (F2-1)/G1 + (F3-1)/(G1G2) + ... (lists in dB)."""
    F = db2lin(nf_db_list)
    G = db2lin(gain_db_list)
    tot = F[0]
    g = 1.0
    for i in range(1, len(F)):
        g *= G[i - 1]
        tot += (F[i] - 1) / g
    return float(lin2db(tot))


def format_cascade(stages, bw_hz=None, snr_min_db=None, ta_k=T0):
    res = cascade(stages)
    fr, _ = noise_contributions(stages)
    rows = [f"{'stage':22s} {'G':>6s} {'NF':>5s} | {'Gcum':>6s} {'NFcum':>6s} {'Te':>7s} {'IIP3cum':>8s} {'%noise':>6s}"]
    for s, r, f in zip(stages, res, fr):
        rows.append(f"{s.name:22s} {s.gain:6.1f} {s.nf:5.2f} | {r['G_cum_dB']:6.1f} {r['NF_cum_dB']:6.2f} "
                    f"{r['Te_cum_K']:7.1f} {r['IIP3_cum_dBm']:8.1f} {100*f:6.1f}")
    if bw_hz is not None:
        last = res[-1]
        n = system_noise_dbm(bw_hz, last["NF_cum_dB"], ta_k)
        rows.append(f"Tsys = {ta_k + last['Te_cum_K']:.0f} K; noise floor in {bw_hz/1e3:.1f} kHz = {n:.1f} dBm")
        if snr_min_db is not None:
            rows.append(f"Sensitivity (SNRmin {snr_min_db:+.1f} dB) = {n + snr_min_db:.1f} dBm")
        if np.isfinite(last["IIP3_cum_dBm"]):
            rows.append(f"SFDR = {sfdr_db(last['IIP3_cum_dBm'], n):.1f} dB")
    return "\n".join(rows)


# ------------------------------------------------------------------ sensitivity & dynamic range
def system_noise_dbm(bw_hz, nf_db, ta_k=T0):
    """Noise floor [dBm] with antenna temperature ta_k: 10log10(k (Ta + Te) B)."""
    return float(ktb_dbm(bw_hz, ta_k + nf_to_te(nf_db)))


def sensitivity_dbm(bw_hz, nf_db, snr_min_db, ta_k=None):
    """S = -174 + 10log10(B) + NF + SNRmin (T0 source), or with an antenna temperature ta_k."""
    if ta_k is None:
        return float(KT0_DBM_HZ + 10 * np.log10(bw_hz) + nf_db + snr_min_db)
    return system_noise_dbm(bw_hz, nf_db, ta_k) + snr_min_db


def mds_dbm(bw_hz, nf_db):
    """Minimum detectable signal (SNR = 0 dB in bw_hz, T0 source)."""
    return sensitivity_dbm(bw_hz, nf_db, 0.0)


def sfdr_db(iip3_dbm, noise_floor_dbm):
    """IM3-limited spurious-free dynamic range: 2/3 (IIP3 - N)."""
    return 2.0 / 3.0 * (iip3_dbm - noise_floor_dbm)


def cn0_dbhz(c_dbm, nf_db, ta_k=T0):
    """Carrier-to-noise-density ratio C/N0 [dB-Hz] with system temperature Ta + Te."""
    n0 = 10 * np.log10(K_B * (ta_k + nf_to_te(nf_db)) / 1e-3)
    return float(c_dbm - n0)


# ------------------------------------------------------------------ nonlinearity
def iip3_from_two_tone(pin_dbm_per_tone, delta_dbc):
    """IIP3 from a two-tone test: IIP3 = Pin + (P_fund - P_IM3)/2 (all per tone, input-referred)."""
    return pin_dbm_per_tone + delta_dbc / 2.0


def im3_level_dbm(pin_dbm_per_tone, iip3_dbm, gain_db=0.0):
    """Output IM3 level per product for a pure third-order device: P_IM3,out = 3 Pin - 2 IIP3 + G."""
    return 3 * pin_dbm_per_tone - 2 * iip3_dbm + gain_db


def iip2_from_two_tone(pin_dbm_per_tone, delta_dbc):
    """IIP2 = Pin + (P_fund - P_IM2)."""
    return pin_dbm_per_tone + delta_dbc


P1DB_IIP3_GAP_CUBIC_DB = 10 * np.log10(4 / 3 / 0.145)   # 9.64 dB (pure cubic nonlinearity only)
