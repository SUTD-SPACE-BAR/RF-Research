#!/usr/bin/env python3
"""
s17_p372_city.py -- W5-S17 orchestrator note (a): man-made noise at 425-433 MHz.

Compares ITU-R P.372-13 Table 3 (outdoor measurements in Europe, 425 MHz: Fa = 6/4/3 dB for
city/residential/rural) with the Table 1 lines Fam = c - d log f (valid 0.3-250 MHz only),
extrapolated to 425 and 433 MHz. Values re-typed from the Rec. ITU-R P.372-13 PDF (2016).
Used by kb/15-lora-ism-radios/ground-station-design.md ("External noise" paragraph).
Run: python3 tools/verify/s17_p372_city.py
"""
import math

T0 = 290.0
LINES = {"city": (76.8, 27.7), "residential": (72.5, 27.7), "rural": (67.2, 27.7)}
TABLE3_425 = {"city": 6.0, "residential": 4.0, "rural": 3.0}   # dB above kT0b, measured


def t_of_fa(fa_db):
    return T0 * 10 ** (fa_db / 10)


ok = True
for env, (c, d) in LINES.items():
    for f in (250.0, 425.0, 433.125):
        fa = c - d * math.log10(f)
        tag = "in range" if f <= 250 else "EXTRAPOLATED (> 250 MHz)"
        print(f"  {env:11s} line at {f:7.3f} MHz: Fam = {fa:6.2f} dB -> {t_of_fa(fa):7.0f} K  [{tag}]")
    meas = TABLE3_425[env]
    print(f"  {env:11s} P.372-13 Table 3 at 425 MHz (measured): Fa = {meas:.0f} dB -> {t_of_fa(meas):.0f} K")
t_city_line = t_of_fa(76.8 - 27.7 * math.log10(425))
ok &= abs(t_city_line - 727) < 5          # ~720 K extrapolated
ok &= abs(t_of_fa(6.0) - 1154) < 2        # ~1150 K measured
print("CHECK city line at 425 MHz ~720 K and Table 3 city ~1150 K:", "PASS" if ok else "FAIL")
