"""Free-space path loss, Friis transmission and a line-item link budget.

Ported from tools/verify/prop_fspl.py and tools/verify/prop_link_budget.py (W1-A5) and
tools/verify/lora_link_budget.py (W2-B6). Page references:
kb/09-propagation-link-budget/friis-free-space-path-loss.md,
kb/09-propagation-link-budget/link-budget-methodology.md.
"""
import math
from dataclasses import dataclass, field

import numpy as np

from .constants import C0, K_B, T0
from .units import undb


def fspl_db(f_hz, d_m):
    """Free-space path loss between isotropic antennas: 20 log10(4 pi d f / c) [dB].
    Equivalent to 32.45 + 20log10(f_MHz) + 20log10(d_km)."""
    return 20.0 * np.log10(4 * np.pi * np.asarray(d_m, float) * np.asarray(f_hz, float) / C0)


def distance_for_fspl(loss_db, f_hz):
    """Inverse of fspl_db: distance [m] at which the free-space loss equals loss_db."""
    return 10 ** (np.asarray(loss_db, float) / 20.0) * C0 / (4 * np.pi * np.asarray(f_hz, float))


def friis_pr_dbm(pt_dbm, gt_dbi, gr_dbi, f_hz, d_m, other_losses_db=0.0):
    """Received power [dBm] from the Friis equation, other_losses_db positive = loss."""
    return pt_dbm + gt_dbi + gr_dbi - fspl_db(f_hz, d_m) - other_losses_db


def eirp_dbm(pt_dbm, feeder_loss_db, g_dbi):
    return pt_dbm - feeder_loss_db + g_dbi


def erp_dbm(eirp_dbm_value):
    """ERP (referenced to a half-wave dipole) = EIRP - 2.15 dB."""
    return eirp_dbm_value - 2.15


def effective_aperture_m2(g_dbi, f_hz):
    """A_e = G lambda^2 / (4 pi)."""
    lam = C0 / np.asarray(f_hz, float)
    return undb(g_dbi) * lam ** 2 / (4 * np.pi)


def gain_from_aperture_dbi(a_m2, f_hz, efficiency=1.0):
    lam = C0 / np.asarray(f_hz, float)
    return 10 * np.log10(efficiency * 4 * np.pi * np.asarray(a_m2, float) / lam ** 2)


def noise_floor_dbm(bw_hz, nf_db=0.0, ta_k=None):
    """Receiver noise power [dBm] in bw_hz. With ta_k=None the source is at T0 = 290 K:
    N = -174 + 10log10(B) + NF. Otherwise N = 10log10(k (Ta + Te) B / 1 mW)."""
    te = T0 * (undb(nf_db) - 1.0)
    t = T0 + te if ta_k is None else ta_k + te
    return 10 * np.log10(K_B * t * np.asarray(bw_hz, float) / 1e-3)


@dataclass
class LinkBudget:
    """Line-item link budget. Items are in dB (gains +, losses -) except the first 'Tx power' in dBm.

    Example (kb/09 link-budget-methodology Example A, 433 MHz E22 at 30 km):
        lb = LinkBudget(f_hz=433.125e6, d_m=30e3)
        lb.add('Tx power', 33.0); lb.add('Tx feeder', -0.5); lb.add('Rocket antenna', 0.0)
        lb.add('Gases', -0.1); lb.add('Polarisation', -3.0); lb.add('Pointing', -1.0)
        lb.add('GS antenna', 11.0); lb.add('Rx feeder', -0.45)
        lb.received_dbm()  # -75.8 dBm (FSPL added automatically)
    """
    f_hz: float
    d_m: float
    items: list = field(default_factory=list)
    include_fspl: bool = True

    def add(self, name, value_db):
        self.items.append((name, float(value_db)))
        return self

    def fspl(self):
        return float(fspl_db(self.f_hz, self.d_m))

    def received_dbm(self):
        total = sum(v for _, v in self.items)
        return total - (self.fspl() if self.include_fspl else 0.0)

    def margin_db(self, sensitivity_dbm):
        return self.received_dbm() - sensitivity_dbm

    def range_for_margin_m(self, sensitivity_dbm, margin_db=0.0):
        """Free-space distance at which the margin falls to margin_db (all other items unchanged)."""
        budget = sum(v for _, v in self.items) - sensitivity_dbm - margin_db
        return float(distance_for_fspl(budget, self.f_hz))

    def report(self, sensitivity_dbm=None):
        lines = [f"Link budget at {self.f_hz/1e6:.3f} MHz, {self.d_m/1e3:.2f} km"]
        for n, v in self.items:
            lines.append(f"  {n:28s} {v:+8.2f}")
        if self.include_fspl:
            lines.append(f"  {'Free-space path loss':28s} {-self.fspl():+8.2f}")
        lines.append(f"  {'Received power [dBm]':28s} {self.received_dbm():8.2f}")
        if sensitivity_dbm is not None:
            lines.append(f"  {'Sensitivity [dBm]':28s} {sensitivity_dbm:8.2f}")
            lines.append(f"  {'Margin [dB]':28s} {self.margin_db(sensitivity_dbm):8.2f}")
        return "\n".join(lines)


def range_scaling(delta_db):
    """Free-space range factor for a change of delta_db in budget: 10^(delta/20)."""
    return 10 ** (np.asarray(delta_db, float) / 20.0)
