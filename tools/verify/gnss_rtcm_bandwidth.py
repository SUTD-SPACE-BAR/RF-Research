#!/usr/bin/env python3
"""
gnss_rtcm_bandwidth.py — verification for kb/21-gnss/rtk-ppp-and-corrections.md

 1. RTCM 3 MSM message sizes from the field layout used by RTKLIB rtcm3e.c:
      header 169 bits + Ncell mask (Nsat x Nsig bits)
      MSM4: 18 bits/satellite + 48 bits/cell     MSM7: 36 bits/satellite + 80 bits/cell
    plus the RTCM3 transport frame (24-bit header + 24-bit CRC-24Q) and byte padding.
    Check: 16 SV x 4 signals -> MSM4 3593 bits, MSM7 5929 bits (NovAtel/EUREF example).
 2. Base-station stream (1005 + MSM4/7 per constellation + 1230) for Singapore-like
    satellite counts, dual-frequency vs L1-only, 4 GNSS vs subsets.
 3. What a LoRa corrections bridge must carry: packets/s and air-time occupancy for SX126x
    settings (SF5/500 = EBYTE "62.5k", SF7/500, SF7/250, SF7/125, SF9/125), using
    tools/verify/lora_toa.py (Semtech SX126x formula).
 4. Carrier-phase / ambiguity numbers: wavelengths, wide-lane, double-difference
    error growth with baseline (1 ppm), corrections age.
Run: python3 tools/verify/gnss_rtcm_bandwidth.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lora_toa import toa_sx126x as _toa   # noqa: E402


def toa_sx126x(pl, sf, bw, cr=1):
    return _toa(pl, sf, bw, cr=cr)[0]

ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


def msm_bits(nsat, nsig_per_sat, kind=4, nsig_mask=None):
    """nsig_per_sat: list of signal counts per satellite (cells); nsig_mask = distinct signals"""
    if isinstance(nsig_per_sat, int):
        nsig_per_sat = [nsig_per_sat] * nsat
    ns = nsig_mask if nsig_mask else max(nsig_per_sat)
    ncell = sum(nsig_per_sat)
    head = 169 + nsat * ns
    sat_b, cell_b = (18, 48) if kind == 4 else (36, 80)
    return head + nsat * sat_b + ncell * cell_b


def frame_bytes(bits):
    return math.ceil(bits / 8) + 6       # 0xD3 + 6 reserved + 10-bit length (3 B) + CRC-24Q (3 B)


b4 = msm_bits(16, 4, 4); b7 = msm_bits(16, 4, 7)
check(f"16 SV x 4 signals: MSM4 {b4} bits (3593), MSM7 {b7} bits (5929)", b4 == 3593 and b7 == 5929)
b1005 = 12 + 12 + 6 + 1 + 1 + 1 + 1 + 38 + 1 + 1 + 38 + 2 + 38   # RTKLIB encode_type1005 field widths
check(f"RTCM 1005 payload = {b1005} bits -> {frame_bytes(b1005)} bytes framed", b1005 == 152)
b1230 = 12 + 12 + 1 + 3 + 4 + 4 * 16      # all four GLONASS code-phase biases present
print(f"  RTCM 1230 (4 biases) = {b1230} bits -> {frame_bytes(b1230)} bytes")

# ---- 2. base stream, Singapore-like counts (real constellations, 10 deg mask; typical, see page)
counts = {"GPS": 10, "GLO": 7, "GAL": 9, "BDS": 16}
# dual-frequency: GPS L2C only on IIR-M/IIF/III (~ 3/4 of the fleet), others all dual
dual = {"GPS": [2] * 8 + [1] * 2, "GLO": [2] * 7, "GAL": [2] * 9, "BDS": [2] * 16}
single = {k: [1] * v for k, v in counts.items()}


def stream(consts, cells, kind=4, rate_hz=1.0):
    per_epoch = sum(frame_bytes(msm_bits(counts[c], cells[c], kind)) for c in consts)
    extra = frame_bytes(b1005) / 10.0 + (frame_bytes(b1230) / 10.0 if "GLO" in consts else 0.0)
    return per_epoch * rate_hz + extra, per_epoch


print("\n  base stream (1 Hz MSM, 1005 & 1230 every 10 s)          B/s   bytes/epoch")
cases = {}
for label, consts, cells, kind in [
        ("GPS+GLO+GAL+BDS dual MSM4 (u-blox default list)", ("GPS", "GLO", "GAL", "BDS"), dual, 4),
        ("GPS+GLO+GAL+BDS dual MSM7", ("GPS", "GLO", "GAL", "BDS"), dual, 7),
        ("GPS+GLO+GAL+BDS L1-only MSM4", ("GPS", "GLO", "GAL", "BDS"), single, 4),
        ("GPS+GAL dual MSM4", ("GPS", "GAL"), dual, 4),
        ("GPS+GAL L1-only MSM4", ("GPS", "GAL"), single, 4),
        ("GPS only L1-only MSM4", ("GPS",), single, 4)]:
    bps, ep = stream(consts, cells, kind)
    cases[label] = (bps, ep)
    print(f"  {label:50s} {bps:6.0f}   {ep:5d}")
full = cases["GPS+GLO+GAL+BDS dual MSM4 (u-blox default list)"][0]
check(f"full dual-frequency MSM4 stream ~ 600-800 B/s (forum measurement 700-750 B/s): {full:.0f}",
      550 < full < 850)
check("L1-only cuts the stream by about a third (headers and per-satellite data don't shrink)",
      0.55 * full < cases["GPS+GLO+GAL+BDS L1-only MSM4"][0] < 0.75 * full)

# ---- 3. LoRa bridge airtime
print("\n  LoRa corrections bridge: epoch split into <=240-byte packets, occupancy per second")
print("  setting        ToA(240 B) [ms]  full-4GNSS-dual  GPS+GAL-dual  GPS+GAL-L1")
settings = [(5, 500e3, "SF5/500 (EBYTE 62.5k)"), (7, 500e3, "SF7/500"), (7, 250e3, "SF7/250"),
            (7, 125e3, "SF7/125"), (9, 125e3, "SF9/125")]
occ = {}
for sf, bw, name in settings:
    t240 = toa_sx126x(240, sf, bw, cr=1)
    row = []
    for label in ["GPS+GLO+GAL+BDS dual MSM4 (u-blox default list)", "GPS+GAL dual MSM4", "GPS+GAL L1-only MSM4"]:
        bps, ep = cases[label]
        npk = math.ceil(ep / 240)
        last = ep - 240 * (npk - 1)
        t = (npk - 1) * t240 + toa_sx126x(last, sf, bw, cr=1)
        t += (frame_bytes(b1005) / 10) / 240 * t240     # amortised 1005/1230
        row.append(t)
    occ[name] = row
    print(f"  {name:22s} {t240*1e3:8.1f}       {row[0]*100:6.0f} %        {row[1]*100:6.0f} %      {row[2]*100:6.0f} %")
check("SF5/500 or SF7/500 carries the full stream with < 50 % occupancy", occ["SF7/500"][0] < 0.5)
check("SF9/125 cannot carry even GPS+GAL L1-only at 1 Hz (> 100 % air time)", occ["SF9/125"][2] > 1.0 or occ["SF9/125"][1] > 1.0)

# ---- 4. carrier-phase numbers
c = 299792458.0
f = {"L1": 1575.42e6, "L2": 1227.60e6, "L5": 1176.45e6, "E5b": 1207.14e6}
lam = {k: c / v for k, v in f.items()}
wl = c / (f["L1"] - f["L2"])
nl = c / (f["L1"] + f["L2"])
print(f"\n  wavelengths: L1 {lam['L1']*100:.2f} cm, L2 {lam['L2']*100:.2f} cm, L5 {lam['L5']*100:.2f} cm; "
      f"wide-lane L1-L2 {wl*100:.1f} cm, narrow-lane {nl*100:.1f} cm")
check("wide-lane L1-L2 = 86.2 cm", abs(wl - 0.8619) < 1e-3)
for bl_km in [0.1, 1, 5, 10, 20]:
    print(f"    baseline {bl_km:5.1f} km -> 1 ppm distance-dependent error {bl_km*1e3*1e-6*100:.1f} cm "
          f"(+ 1 cm) = {1+bl_km*0.1:.1f} cm")
# rocket: baseline growth
for v, t in [(300, 10), (500, 20)]:
    print(f"    rocket at {v} m/s for {t} s -> baseline grows to ~{v*t/1e3:.0f} km (still short-baseline RTK)")

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
