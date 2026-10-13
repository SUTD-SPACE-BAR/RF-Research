#!/usr/bin/env python3
"""
s1_image_throughput.py — bulk data (camera images, Codec2 voice) over sub-GHz and 2.4 GHz links under
the Singapore licence-exempt limits: time to deliver a 10 / 50 / 600 kB image vs free-space and landed
range, with fragmentation overhead and packet-level erasure FEC.

Used by: kb/10-comms-modulation/modulation-choice-guide.md (Example 6) and
kb/15-lora-ism-radios/other-ism-radios-fsk-2g4.md (section "Bulk data: images and voice").

Model
  * Fragment: payload P_frag = 200 B of image data + 8 B fragment header (image id, index, count, CRC-16
    over the reassembled image is carried once). PHY CRC on.
  * Erasure FEC across fragments at rate k/n = 0.8 (25 % repair fragments, e.g. Reed-Solomon / fountain):
    any k of n received fragments rebuild the block (one-way downlink, no ARQ).
  * Occupancy limited by the legal duty cycle d (433.05-434.79 MHz 10 %, 917-925 MHz LPWAN 1 %,
    866-869 MHz none stated -> 100 % assumed but flagged, 2.4 GHz none) and by 0.7 for TX/RX gaps.
  * Goodput = 200 B * 8 * (k/n) * min(d, 0.7) / T_packet.
  * Sensitivity: LoRa -174 + NF + 10log BW + SNR_req; GFSK/FLRC -174 + NF + 10log R + Eb/N0_req with
    Eb/N0_req = FOM - 6 dB from the KB's datasheet FOMs (GFSK 16 -> 10 dB, FLRC 15.4 -> 9.4 dB).
    NF = 1.8 dB (ground station with masthead LNA). HaLow MCS10 sensitivity is an ESTIMATE.
  * Range: EIRP at the legal limit, rocket antenna 2.15 dBi (counted in EIRP), GS gain 12 dBi
    (sub-GHz Yagi) or 14 dBi (2.4 GHz patch/Yagi), 13 dB fade margin; free space and flat-earth
    two-ray with the rocket landed (antenna 0.1 m) and a 5 m mast.
Run: python3 tools/verify/s1_image_throughput.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from rfcalc.lora import time_on_air, sensitivity_dbm  # noqa: E402

C = 299_792_458.0
NF_GS = 1.8
MARGIN = 13.0
FRAG, HDR, KN = 200, 8, 0.8
checks = []


def check(name, ok):
    checks.append(bool(ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")


def fsk_toa(payload_b, rate_bps, pre_b=4, sync_b=4, len_b=1, crc_b=2):
    return (pre_b + sync_b + len_b + payload_b + crc_b) * 8 / rate_bps


def ranges(eirp_dbm, g_gs, s_dbm, f):
    lmax = eirp_dbm + g_gs - s_dbm - MARGIN
    lam = C / f
    d_fs = 10 ** (lmax / 20) * lam / (4 * math.pi)
    # two-ray: L = 40 log d - 20 log(ht hr)  (beyond the breakpoint)
    d_2r = 10 ** ((lmax + 20 * math.log10(0.1 * 5.0)) / 40)
    return d_fs, d_2r


# band: (label, f, EIRP limit dBm, duty, gs gain)
BANDS = {
    "433": ("433.05–434.79 MHz, 10 mW e.r.p., 10 %", 434.125e6, 12.15, 0.10, 12.0),
    "868": ("866–869 MHz, 500 mW e.r.p., no duty stated", 867.125e6, 29.15, 1.00, 12.0),
    "920": ("917–925 MHz LPWAN, 100 mW e.r.p., 1 %", 920.125e6, 22.15, 0.01, 12.0),
    "2400": ("2.400–2.4835 GHz, 100 mW e.i.r.p. (32d)", 2440e6, 20.0, 1.00, 14.0),
}
MODES = []
for sf, bw in [(7, 500e3), (7, 125e3), (9, 125e3)]:
    t = time_on_air(FRAG + HDR, sf, bw, cr=1, chip="sx126x")
    MODES.append((f"LoRa SF{sf}/{int(bw/1e3)}", t, sensitivity_dbm(sf, bw, NF_GS), ["433", "868", "920"]))
for r in [50e3, 250e3]:
    MODES.append((f"GFSK {int(r/1e3)} kb/s", fsk_toa(FRAG + HDR, r), -173.98 + NF_GS + 10 * math.log10(r) + 10.0,
                  ["433", "868", "920"]))
# HaLow 1 MHz MCS10 150 kb/s PHY; MAC/PHY overhead ~ 50 % assumed -> 75 kb/s; sensitivity ESTIMATE
MODES.append(("HaLow 1 MHz MCS10 (est.)", (FRAG + HDR) * 8 / 75e3, -106.0 - (6 - NF_GS), ["868", "920"]))
MODES.append(("SX1280 FLRC 325 kb/s (650 CR½)", fsk_toa(FRAG + HDR, 325e3), -173.98 + NF_GS + 10 * math.log10(325e3) + 9.4, ["2400"]))
MODES.append(("SX1280 LoRa SF7/1625", time_on_air(FRAG + HDR, 7, 1625e3, cr=1, chip="sx126x"),
              sensitivity_dbm(7, 1625e3, NF_GS), ["2400"]))

SIZES = [10e3, 50e3, 600e3]
print("Image delivery time (s) and range; goodput includes 8 B header, rate-0.8 erasure FEC and min(duty, 0.7)")
print(f"{'band':6s} {'mode':32s} {'T_pkt ms':>8s} {'goodput b/s':>11s} " +
      " ".join(f"{int(s/1e3):>4d} kB" for s in SIZES) + f" {'free-space km':>14s} {'landed km':>10s}")
RESULT = {}
for bkey, (blabel, f, eirp, duty, ggs) in BANDS.items():
    for name, t, s, allowed in MODES:
        if bkey not in allowed:
            continue
        occ = min(duty, 0.7)
        goodput = FRAG * 8 * KN * occ / t
        times = [sz * 8 / goodput for sz in SIZES]
        dfs, d2r = ranges(eirp, ggs, s, f)
        RESULT[(bkey, name)] = (t, goodput, times, dfs, d2r)
        tt = " ".join(f"{x:7.0f}" if x < 1e5 else f"{x:7.1e}" for x in times)
        print(f"{bkey:6s} {name:32s} {t*1e3:8.1f} {goodput:11.0f} {tt} {dfs/1e3:14.0f} {d2r/1e3:10.1f}")
    print(f"       ({blabel})")

g433 = RESULT[("433", "LoRa SF7/500")]
g868 = RESULT[("868", "LoRa SF7/500")]
check("duty cycle ratio 868 (0.7) / 433 (0.1) = 7x goodput", abs(g868[1] / g433[1] - 7) < 1e-6)
check("600 kB at 917-925 MHz LoRa SF9/125 takes > 1 day", RESULT[("920", "LoRa SF9/125")][2][2] > 86400)
check("GFSK 250 kb/s at 868 delivers 50 kB in < 5 s", RESULT[("868", "GFSK 250 kb/s")][2][1] < 5)

print("\nCodec2 voice (bit rates from the Codec2 README: 3200, 2400, 1600, 1400, 1300, 1200, 700C, 450 b/s)")
for rate in [1300, 700, 450]:
    frame_s = 0.4                     # 400 ms of speech per packet
    pl = int(math.ceil(rate * frame_s / 8)) + 4
    for sf, bw in [(7, 125e3), (9, 125e3), (7, 500e3)]:
        t = time_on_air(pl, sf, bw, cr=1, chip="sx126x")
        occ = t / frame_s
        ok433 = "OK" if occ <= 0.10 else "over 10 %"
        print(f"  {rate:4d} b/s, {pl:3d} B per 400 ms, SF{sf}/{int(bw/1e3)}: ToA {t*1e3:6.1f} ms, occupancy {occ*100:5.1f} % "
              f"→ 433 MHz exempt: {ok433}; feasible at all: {'yes' if occ < 0.7 else 'no'}")
t1300 = time_on_air(int(math.ceil(1300 * 0.4 / 8)) + 4, 9, 125e3, cr=1, chip="sx126x")
check("Codec2 1300 at SF9/125 does not fit real time", t1300 / 0.4 > 0.7)

print(f"\nSummary: {sum(checks)} of {len(checks)} checks pass")
