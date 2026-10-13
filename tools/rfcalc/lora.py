"""LoRa symbol time, time-on-air (SX127x and SX126x forms), bit rate and sensitivity.

Ported from tools/verify/lora_toa.py and lora_link_budget.py (W2-B6) and noise_sensitivity.py (W1-A5).
Pages: kb/15-lora-ism-radios/lora-phy-css-math.md, lora-sensitivity-and-link-budget.md.
ToA formula: Semtech SX1276/77/78/79 datasheet rev 7 sec. 4.1.1.7 (= AN1200.13) and
SX1261/2 datasheet rev 1.2 sec. 6.1.4 (differs for SF5/6).
"""
import math

from .constants import KT0_DBM_HZ

# Demodulator SNR limits [dB] (Semtech SX126x/SX127x datasheet tables)
SNR_REQ_DB = {5: -2.5, 6: -5.0, 7: -7.5, 8: -10.0, 9: -12.5, 10: -15.0, 11: -17.5, 12: -20.0}


def t_sym(sf, bw_hz):
    """Symbol duration 2^SF / BW [s]."""
    return (2 ** sf) / bw_hz


def ldro_auto(sf, bw_hz, chip="sx126x"):
    """Low-data-rate optimisation: on when the symbol time is >= 16.38 ms (SX126x recommendation) or
    > 16 ms (SX127x). Both put the boundary at SF11/125 kHz."""
    ts_ms = t_sym(sf, bw_hz) * 1e3
    return ts_ms >= 16.38 if chip == "sx126x" else ts_ms > 16.0


def n_symbols(pl, sf, cr=1, npre=8, crc=True, explicit=True, ldro=None, bw_hz=125e3, chip="sx127x"):
    """Total number of symbols in a packet (preamble + sync + header/payload).
    cr = 1..4 for coding rate 4/5..4/8."""
    de = ldro_auto(sf, bw_hz, chip) if ldro is None else ldro
    if chip == "sx126x":
        h = 20 if explicit else 0
        ncrc = 16 if crc else 0
        if sf in (5, 6):
            num = max(8 * pl + ncrc - 4 * sf + h, 0)
            return npre + 6.25 + 8 + math.ceil(num / (4 * sf)) * (cr + 4)
        num = max(8 * pl + ncrc - 4 * sf + 8 + h, 0)
        return npre + 4.25 + 8 + math.ceil(num / (4 * (sf - 2 * int(de)))) * (cr + 4)
    ih = 0 if explicit else 1
    num = 8 * pl - 4 * sf + 28 + 16 * int(crc) - 20 * ih
    den = 4 * (sf - 2 * int(de))
    return npre + 4.25 + 8 + max(math.ceil(num / den) * (cr + 4), 0)


def time_on_air(pl, sf, bw_hz, cr=1, npre=8, crc=True, explicit=True, ldro=None, chip="sx127x"):
    """Time on air [s]."""
    return n_symbols(pl, sf, cr, npre, crc, explicit, ldro, bw_hz, chip) * t_sym(sf, bw_hz)


def bitrate(sf, bw_hz, cr=1, ldro=False):
    """Nominal useful bit rate (SF - 2DE) BW/2^SF * 4/(4+CR) [bit/s]."""
    return (sf - 2 * int(ldro)) * bw_hz / 2 ** sf * 4 / (4 + cr)


def sensitivity_dbm(sf, bw_hz, nf_db=6.0, impl_loss_db=0.0):
    """S = -174 + 10 log10(BW) + NF + SNR_req(SF) (+ implementation loss)."""
    return KT0_DBM_HZ + 10 * math.log10(bw_hz) + nf_db + SNR_REQ_DB[sf] + impl_loss_db


def processing_gain_db(sf):
    """10 log10(2^SF)."""
    return 10 * math.log10(2 ** sf)


def max_packet_rate_hz(pl, sf, bw_hz, cr=1, npre=8, duty_cycle=1.0, **kw):
    """Back-to-back packet rate [1/s] allowed by time on air and a duty-cycle limit."""
    return duty_cycle / time_on_air(pl, sf, bw_hz, cr, npre, **kw)
