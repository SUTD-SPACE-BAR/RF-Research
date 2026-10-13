#!/usr/bin/env python3
"""
s1_elrs_link.py — ExpressLRS-class links: air-time, hop-rate and telemetry arithmetic, and a link budget
checked against ExpressLRS's range claim.

Used by: kb/15-lora-ism-radios/other-ism-radios-fsk-2g4.md, section "ExpressLRS-class links".

Mode table re-typed from the ExpressLRS source (community project; GitHub master, src/src/common.cpp,
ExpressLRS_AirRateConfig / ExpressLRS_AirRateRFperf, read 2026-10-03): SF, BW, CR, preamble, hop interval
(packets per hop), packet interval, payload bytes (OTA4 = 8 B), RX sensitivity, ELRS's own TOA figure.
ELRS uses implicit header and carries its own CRC inside the 8-byte packet, so the LoRa CRC is off.
Run: python3 tools/verify/s1_elrs_link.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from rfcalc.lora import time_on_air  # noqa: E402

C = 299_792_458.0
checks = []


def check(name, ok):
    checks.append(bool(ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")


# name: (sf, bw, cr_index (1=4/5 … 3=4/7, 4=4/8), preamble, hop_every, interval_us, payload, sens_dBm, elrs_toa_us)
SX127X_900 = {
    "200Hz": (6, 500e3, 3, 8, 4, 5000, 8, -112, 4380),
    "100Hz": (7, 500e3, 3, 8, 4, 10000, 8, -117, 8770),
    "50Hz":  (8, 500e3, 3, 10, 4, 20000, 8, -120, 18560),
    "25Hz":  (9, 500e3, 3, 10, 2, 40000, 8, -123, 29950),
}
print("=== Air time: rfcalc (SX127x form, implicit header, no LoRa CRC) vs ELRS TOA field ===")
for name, (sf, bw, cr, npre, hop, iv, pl, sens, toa) in SX127X_900.items():
    t = time_on_air(pl, sf, bw, cr=cr, npre=npre, crc=False, explicit=False, chip="sx127x") * 1e6
    rate = 1e6 / iv
    print(f"  900 MHz {name:6s}: SF{sf}/{int(bw/1e3)} CR4/{4+cr}, pre {npre}: rfcalc {t:7.0f} µs, ELRS {toa} µs; "
          f"occupancy {t/iv*100:4.0f} %; hop every {hop} packets → {rate/hop:5.1f} hops/s, dwell {hop*iv/1e3:.0f} ms")
    check(f"ToA {name} within 1 %", abs(t - toa) / toa < 0.01)

print("\n=== Hopping arithmetic (FCC915: 40 channels 903.5–926.9 MHz; ISM2G4: 80 channels) ===")
for band, nch, rate, hop in [("FCC915 200 Hz", 40, 200, 4), ("FCC915 25 Hz", 40, 25, 2), ("ISM2G4 500 Hz", 80, 500, 4),
                             ("ISM2G4 F1000", 80, 1000, 2)]:
    hops = rate / hop
    print(f"  {band:14s}: {hops:6.1f} hops/s; full cycle of {nch} channels in {nch/hops:5.2f} s; "
          f"spacing {(926.9-903.5)/(nch-1)*1e3 if 'FCC' in band else (2479.4-2400.4)/(nch-1)*1e3:.0f} kHz")
print("  the sync channel (middle of the list) is revisited once per cycle; a receiver that loses lock waits there")

print("\n=== Telemetry ratio ===")
for rate, ratio in [(200, 64), (50, 16), (25, 8), (500, 128)]:
    print(f"  {rate} Hz at 1:{ratio}: {rate/ratio:5.2f} downlink telemetry packets/s, uplink keeps {rate*(1-1/ratio):.1f} packets/s")
check("1:64 at 200 Hz gives 3.125 telemetry packets/s", abs(200 / 64 - 3.125) < 1e-9)

print("\n=== Link budget vs the 'over 40 km at 250 Hz, 100 mW, omni antennas' claim (2.4 GHz) ===")
f = 2440e6
for ga in [0.0, 2.0]:
    mapl = 20 + 2 * ga + 108            # 100 mW, -108 dBm at 250 Hz (SF6/800)
    d0 = 10 ** (mapl / 20) * C / (4 * math.pi * f)
    d10 = 10 ** ((mapl - 10) / 20) * C / (4 * math.pi * f)
    print(f"  antennas {ga:.0f} dBi each: MAPL {mapl:.0f} dB → free-space {d0/1e3:.0f} km at 0 dB margin, "
          f"{d10/1e3:.0f} km with 10 dB margin")
mapl2 = 20 + 4 + 108
dkm = 10 ** (mapl2 / 20) * C / (4 * math.pi * f) / 1e3
check("40 km claim ≈ zero-margin free space with 2 dBi antennas", 30 < dkm < 50)
print("  900 MHz 25 Hz (SF9/500, −123 dBm), 1 W, 2 dBi each: " +
      f"{10 ** ((30 + 4 + 123) / 20) * C / (4 * math.pi * 915e6) / 1e3:.0f} km zero-margin free space")
print(f"\nSummary: {sum(checks)} of {len(checks)} checks pass")
