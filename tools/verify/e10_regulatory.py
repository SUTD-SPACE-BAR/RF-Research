#!/usr/bin/env python3
"""
e10_regulatory.py — arithmetic behind kb/19-regulations-safety/regulatory-faq-misc.md (W5-E10).

 1. FCC field-strength limits (at 3 m) -> equivalent EIRP:  EIRP = E^2 r^2 / 30.
    15.209 (> 960 MHz: 500 uV/m), 15.249 (50 / 250 mV/m), 15.245 (500 / 2500 mV/m), 15.239 (FM 250 uV/m).
 2. 902-928 MHz under the NextNav plan: hopping-channel counts in 26 MHz vs the 11 MHz (907-918 MHz)
    left for Part 15, against 15.247 minimums (50 channels if 20 dB BW < 250 kHz, 25 if >= 250 kHz).
 3. A Baofeng-class handheld (1-8 W, whip ~0 dBd) vs PMR446-style 0.5 W ERP and SG amateur 10 W ERP.
 4. Meshtastic US preset at 30 dBm conducted with 250 kHz LoRa vs 15.249 (non-hopping, not DTS) — size of
    the gap if it were judged under 15.249 (open question on the page).

Run:  python3 tools/verify/e10_regulatory.py
"""
import math

FAIL = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAIL.append(name)


def eirp_w(e_v_per_m, r=3.0):
    return e_v_per_m ** 2 * r ** 2 / 30.0


def dbm(w):
    return 10 * math.log10(w * 1e3)


print("1. FCC field-strength limits at 3 m -> EIRP (average; Part 15 peak limit is 20 dB higher, 15.35)")
rows = [("15.209 general, >960 MHz", 500e-6), ("15.239 FM broadcast band 88-108 MHz", 250e-6),
        ("15.249 902-928 / 2400 / 5800 MHz", 50e-3), ("15.249 24.0-24.25 GHz", 250e-3),
        ("15.245 FDS 902-928, 2435-2465, 5785-5815 MHz", 500e-3), ("15.245 FDS 10.50-10.55, 24.075-24.175 GHz", 2.5)]
for lab, e in rows:
    p = eirp_w(e)
    print(f"  {lab:46s}: {e*1e3:9.3f} mV/m -> EIRP {dbm(p):6.1f} dBm ({p*1e3:9.4f} mW)")
check("500 uV/m at 3 m = -41.2 dBm EIRP", abs(dbm(eirp_w(500e-6)) - (-41.25)) < 0.05)
check("2500 mV/m at 3 m = 32.7 dBm EIRP", abs(dbm(eirp_w(2.5)) - 32.73) < 0.05)
check("50 mV/m at 3 m = -1.2 dBm EIRP", abs(dbm(eirp_w(0.05)) - (-1.25)) < 0.05)

print("\n2. Hopping channels: 26 MHz today vs 11 MHz (907-918) under NextNav's proposed plan")
for bw_khz in (125, 200, 250, 500):
    n26 = int(26000 // bw_khz)
    n11 = int(11000 // bw_khz)
    need = 50 if bw_khz < 250 else 25
    print(f"  channel spacing = 20 dB BW = {bw_khz} kHz: {n26:3d} in 26 MHz, {n11:3d} in 11 MHz; 15.247 needs {need}"
          f" -> {'OK' if n11 >= need else 'NOT POSSIBLE'} in 11 MHz")
check("500 kHz channels: only 22 fit in 11 MHz (< 25)", int(11000 // 500) == 22)
check("125 kHz LoRa hopping: 88 fit in 11 MHz (>= 50)", int(11000 // 125) >= 50)

print("\n3. Handheld power vs limits (ERP; whip assumed 0 dBd, i.e. ERP = conducted power)")
for p_w in (0.5, 1, 4, 5, 8):
    print(f"  {p_w:4.1f} W -> {dbm(p_w):5.1f} dBm ERP; vs 0.5 W PMR446-style: {dbm(p_w)-dbm(0.5):+5.1f} dB;"
          f" vs SG amateur 10 W ERP: {dbm(p_w)-dbm(10):+5.1f} dB")
check("5 W is 10 dB above 0.5 W", abs(dbm(5) - dbm(0.5) - 10) < 1e-9)

print("\n4. 30 dBm conducted, 250 kHz non-hopping LoRa with a 2.15 dBi antenna vs 15.249 limit")
eirp = 30 + 2.15
lim = dbm(eirp_w(0.05))
print(f"  EIRP {eirp:.1f} dBm vs 15.249 average limit {lim:.1f} dBm -> {eirp-lim:.1f} dB over, IF judged under 15.249")
check("gap ~33 dB", abs(eirp - lim - 33.4) < 0.2)

print("\nRESULT:", "ALL PASS" if not FAIL else f"{len(FAIL)} FAIL: {FAIL}")
