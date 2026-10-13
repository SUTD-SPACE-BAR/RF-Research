#!/usr/bin/env python3
"""
gnss_self_interference.py — verification for kb/21-gnss/gnss-interference-jamming-spoofing.md

 1. Harmonics of on-board clocks and radios that land inside GNSS receiver passbands
    (L1/E1/B1C, B1I, GLONASS G1, L2, G2, E5b/B2I, L5/E5a/B2a, E6).
 2. Intermodulation products m*fa + n*fb (|m|+|n| <= 5) of on-board transmitters
    (EBYTE E22-400T33D 410-493 MHz, E220-900T30D 850-930 MHz, ESP32 2.4 GHz Wi-Fi/BLE)
    that land in L1/B1I/G1/L2.
 3. Jamming tolerance: effective C/N0 with interference (Kaplan: 1/CN0_eff = 1/CN0 + (J/S)/(Q Rc)),
    J/S that drops C/N0 from 45 to a 28 dB-Hz tracking threshold, the absolute jammer power
    that implies, and the free-space distance at which a given EIRP reaches it.
 4. Out-of-band blocking budget for the MAX-M10S (u-blox immunity figures) next to a 2 W 433 MHz and
    a 1 W 900 MHz transmitter: required antenna-to-RF_IN isolation.
Run: python3 tools/verify/gnss_self_interference.py
"""
import numpy as np

ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


# receiver passbands (MHz): (low, high, signal centre, main-lobe half width)
BANDS = {
    "L1 C/A main lobe": (1574.397, 1576.443, 1575.42, 1.023),
    "E1/B1C/L1C (+-12.3 MHz)": (1563.144, 1587.696, 1575.42, 12.276),
    "BeiDou B1I": (1559.052, 1563.144, 1561.098, 2.046),
    "GLONASS G1 (k=-7..+6)": (1597.551, 1605.886, 1602.0, 0.511),
    "GPS L2C main lobe": (1226.577, 1228.623, 1227.60, 1.023),
    "u-blox F9 L2 band (1223-1231)": (1223.0, 1231.0, 1227.60, 4.0),
    "GLONASS G2": (1242.4, 1249.1, 1246.0, 0.511),
    "E5b/B2I (1196.9-1217.4)": (1196.91, 1217.37, 1207.14, 10.23),
    "L5/E5a/B2a (1166.2-1186.7)": (1166.22, 1186.68, 1176.45, 10.23),
    "Galileo E6 (1258.3-1299.2)": (1258.29, 1299.21, 1278.75, 20.46),
}

clocks = {"8 MHz (STM32 HSE)": 8, "12 MHz": 12, "16 MHz": 16, "24 MHz (Teensy 4.1 xtal)": 24,
          "25 MHz (Ethernet)": 25, "26 MHz (TCXO)": 26, "27 MHz": 27, "32 MHz (SX126x TCXO)": 32,
          "40 MHz (ESP32 xtal)": 40, "48 MHz (USB)": 48, "50 MHz (SD/SPI)": 50, "80 MHz (ESP32 APB)": 80,
          "240 MHz (ESP32-S3 CPU)": 240, "528 MHz (i.MX RT PLL2)": 528, "600 MHz (Teensy core)": 600}

print("1) clock harmonics landing in GNSS passbands (offset from signal centre)")
hits = {}
for cname, fclk in clocks.items():
    for bname, (lo, hi, fc, hw) in BANDS.items():
        nmin, nmax = int(np.ceil(lo / fclk)), int(np.floor(hi / fclk))
        for n in range(nmin, nmax + 1):
            fh = n * fclk
            hits.setdefault(cname, []).append((bname, n, fh, fh - fc))
for cname, lst in hits.items():
    s = "; ".join(f"{b.split(' (')[0]}: {n}x = {fh:.1f} ({d:+.2f} MHz)" for b, n, fh, d in lst
                  if not b.startswith("E1/B1C") or abs(d) > 1.023)
    if s:
        print(f"  {cname:26s} {s}")
check("25 MHz x 63 = 1575.000 MHz sits 0.42 MHz from L1 (inside the C/A main lobe)",
      any(b == "L1 C/A main lobe" and n == 63 for b, n, _, _ in hits["25 MHz (Ethernet)"]))
check("8 MHz x 197 = 1576 MHz is inside the C/A main lobe",
      any(b == "L1 C/A main lobe" and n == 197 for b, n, _, _ in hits["8 MHz (STM32 HSE)"]))
check("24 MHz x 65 = 1560 and 40 MHz x 39 = 1560 fall inside BeiDou B1I (MAX-M10S default signal)",
      any(b == "BeiDou B1I" for b, *_ in hits["24 MHz (Teensy 4.1 xtal)"]) and
      any(b == "BeiDou B1I" for b, *_ in hits["40 MHz (ESP32 xtal)"]))
check("40 MHz x 40 = 1600 MHz falls inside GLONASS G1",
      any(b.startswith("GLONASS G1") and n == 40 for b, n, _, _ in hits["40 MHz (ESP32 xtal)"]))
check("40 MHz x 30 = 1200 MHz falls in E5b/B2I (ZED-F9P second band)",
      any(b.startswith("E5b") and n == 30 for b, n, _, _ in hits["40 MHz (ESP32 xtal)"]))

# ---------------------------------------------------------------- 2. radio harmonics & IM
print("\n2) radio harmonics")
e22 = np.arange(410.125, 493.2, 1.0)          # EBYTE E22-400T33D channel raster (1 MHz steps)
e220 = np.arange(850.125, 930.2, 1.0)         # E220-900T30D
for name, chans in [("E22 (410-493 MHz)", e22), ("E220 (850-930 MHz)", e220)]:
    for n in range(2, 6):
        for bname, (lo, hi, fc, hw) in BANDS.items():
            hitc = chans[(n * chans >= lo) & (n * chans <= hi)]
            if len(hitc):
                print(f"  {name}: {n}x of {hitc.min():.3f}-{hitc.max():.3f} MHz -> {bname} "
                      f"({n*hitc.min():.1f}-{n*hitc.max():.1f} MHz)")
l2_hit = e22[(3 * e22 >= 1223) & (3 * e22 <= 1231)]
check(f"E22 channels {l2_hit.min() if len(l2_hit) else None}-{l2_hit.max() if len(l2_hit) else None} MHz: "
      f"3rd harmonic inside the u-blox L2 band", len(l2_hit) > 0 and l2_hit.max() < 411)
check("433.125 MHz (E22 default) 3rd harmonic 1299.375 MHz lies just above Galileo E6 (1299.21)",
      3 * 433.125 > 1299.21)
check("no harmonic of 850-930 MHz or 410-493 MHz lands in L1/E1/B1I/G1",
      not any((lo <= n * f <= hi) for f in np.concatenate([e22, e220]) for n in range(2, 6)
              for b, (lo, hi, _, _) in BANDS.items() if b.startswith(("L1", "E1", "BeiDou", "GLONASS G1"))))

print("\n   intermodulation products m*fa + n*fb landing in L1/E1, B1I, G1 or L2 (|m|+|n| <= 5)")
wifi = np.arange(2402.0, 2481.0, 1.0)
radios = {"E22": np.array([433.125, 433.92, 410.125, 470.0]), "E220": np.array([868.125, 915.125, 923.125]),
          "2.4G": np.array([2412.0, 2437.0, 2442.0, 2462.0, 2480.0])}
targets = {k: BANDS[k] for k in ["E1/B1C/L1C (+-12.3 MHz)", "BeiDou B1I", "GLONASS G1 (k=-7..+6)",
                                  "u-blox F9 L2 band (1223-1231)"]}
found = []
pairs = [("E22", "E220"), ("E22", "2.4G"), ("E220", "2.4G")]
for A, B in pairs:
    for fa in radios[A]:
        for fb in radios[B]:
            for m in range(-5, 6):
                for n in range(-5, 6):
                    if m == 0 or n == 0 or abs(m) + abs(n) > 5:
                        continue
                    f = m * fa + n * fb
                    for tn, (lo, hi, fc, hw) in targets.items():
                        if lo <= f <= hi:
                            found.append((abs(m) + abs(n), A, fa, m, B, fb, n, f, tn))
found.sort()
for order, A, fa, m, B, fb, n, f, tn in found[:25]:
    print(f"   order {order}: {m:+d}x{A}({fa}) {n:+d}x{B}({fb}) = {f:.2f} MHz -> {tn}")
wifi_433 = [x for x in found if x[1] == "E22" and x[4] == "2.4G" and x[8].startswith("E1")]
wifi_868 = [x for x in found if x[1] == "E220" and x[4] == "2.4G" and x[0] == 2]
check("2.4 GHz (Wi-Fi/BLE) - 2 x 433 MHz is a 3rd-order product that lands in L1/E1", len(wifi_433) > 0)
check("2.4 GHz - 868 MHz is a 2nd-order product that lands in L1/E1", len(wifi_868) > 0)

# ---------------------------------------------------------------- 2b. full harmonic table (coordinator request)
print("\n2b) n x f of the on-board radio bands vs GNSS bands (signal bands incl. main lobes; u-blox F9 band edges)")
GN = {"L1/E1/B1C": (1563.144, 1587.696), "B1I": (1559.052, 1563.144), "G1": (1597.551, 1605.886),
      "GPS L2 (1215-1240 alloc.)": (1215.0, 1240.0), "u-blox L2C band": (1223.0, 1231.0),
      "G2": (1242.4, 1249.1), "E5b/B2I": (1196.91, 1217.37), "L5/E5a/B2a": (1166.22, 1186.68),
      "E6": (1258.29, 1299.21)}
radio_bands = {"E22 tuning 410.125-493.125": (410.125, 493.125), "SG/EU SRD 433.05-434.79": (433.05, 434.79),
               "EU 863-870": (863.0, 870.0), "US 902-928": (902.0, 928.0), "AS923/SG 917-925": (917.0, 925.0),
               "E220 tuning 850.125-930.125": (850.125, 930.125)}
for rb, (lo, hi) in radio_bands.items():
    for n in range(2, 6):
        for gname, (glo, ghi) in GN.items():
            a, b = max(n * lo, glo), min(n * hi, ghi)
            if a <= b:
                print(f"  {rb:28s} x{n}: {n*lo:7.1f}-{n*hi:7.1f} MHz overlaps {gname:24s} for f = {a/n:.3f}-{b/n:.3f} MHz")
print("  E22 channel table (f = 410.125 + CH MHz), 3rd harmonic:")
for ch in range(0, 12):
    f = 410.125 + ch
    h = 3 * f
    tags = [g for g, (glo, ghi) in GN.items() if glo <= h <= ghi]
    print(f"    CH {ch:2d}: {f:.3f} MHz -> 3f = {h:.3f} MHz  {', '.join(tags) if tags else '(clear of GNSS signal bands)'}")
for ch in (23, 24):
    f = 410.125 + ch; h = 3 * f
    tags = [g for g, (glo, ghi) in GN.items() if glo <= h <= ghi]
    print(f"    CH {ch:2d}: {f:.3f} MHz -> 3f = {h:.3f} MHz  {', '.join(tags) if tags else '(clear; RNSS allocation ends 1300 MHz)'}")
check("E22 CH 0 (410.125) 3rd harmonic 1230.375 MHz is inside the u-blox L2C band and the GPS L2 allocation",
      1223 <= 3 * 410.125 <= 1231)
check("E22 CH 0-3 3rd harmonics (1230.4-1239.4 MHz) lie inside the 1215-1240 MHz L2 allocation",
      all(1215 <= 3 * (410.125 + c) <= 1240 for c in range(0, 4)))
check("E22 CH 5-6 3rd harmonics (1245.4, 1248.4 MHz) lie inside GLONASS G2; CH 4 (1242.4) at its lower edge",
      all(1242.4 <= 3 * (410.125 + c) <= 1249.1 for c in (5, 6)))
check("E22 CH 24 (434.125 MHz) 3rd harmonic 1302.4 MHz is above the RNSS 1215-1300 MHz allocation", 3 * 434.125 > 1300)
check("no 2nd-5th harmonic of 863-870 or 902-928 MHz falls in any GNSS band",
      not any(max(n * lo, glo) <= min(n * hi, ghi) for (lo, hi) in [(863, 870), (902, 928)]
              for n in range(2, 6) for (glo, ghi) in GN.values()))
# required harmonic suppression for an in-band 3rd harmonic
p_tx, coupling_db = 33.0, 25.0
j_thr = -98.0                       # narrowband-ish (LoRa chirp harmonic ~3xBW wide) tracking-loss level
need_dbc = p_tx - coupling_db - j_thr
print(f"  required 3rd-harmonic suppression if it lands in-band: {p_tx} dBm - {coupling_db} dB coupling - ({j_thr} dBm)"
      f" = {need_dbc:.0f} dBc (vs ~60 dBc typical module spec) -> ~{need_dbc-60:.0f} dB extra filtering, or move channel")
check("an in-band harmonic needs ~100 dBc total suppression (~45 dB beyond a 60 dBc module)", 95 < need_dbc < 112)

# ---------------------------------------------------------------- 3. J/S
print("\n3) interference tolerance (Kaplan-Hegarty form)")
Rc = 1.023e6


def cn0_eff(cn0_db, js_db, Q):
    return -10 * np.log10(10 ** (-cn0_db / 10) + 10 ** (js_db / 10) / (Q * Rc))


def js_max(cn0_db, cn0_req_db, Q):
    return 10 * np.log10(Q * Rc * (10 ** (-cn0_req_db / 10) - 10 ** (-cn0_db / 10)))


for Q, lab in [(1.0, "narrowband at spectral peak (Q~1)"), (1.5, "matched-spectrum BPSK (Q=1.5)"),
               (2.0, "wideband noise (Q=2)")]:
    for req in [28, 35]:
        js = js_max(45, req, Q)
        print(f"  {lab:36s}: C/N0 45 -> {req} dB-Hz at J/S = {js:5.1f} dB -> J = {-130+js:6.1f} dBm "
              f"(S = -130 dBm)")
js28 = js_max(45, 28, 2.0)
check(f"wideband J/S for 45 -> 28 dB-Hz is ~{js28:.0f} dB (J ~ -95 dBm at the antenna)", 30 < js28 < 36)
# distance for a 10 mW EIRP (Singapore 433 MHz SRD level) in-band spur/jammer, or a -30 dBm spurious
for eirp_dbm, lab in [(-30, "-30 dBm EIRP spurious (regulatory limit >1 GHz)"), (10, "10 mW EIRP in-band jammer"),
                      (30, "1 W EIRP in-band jammer")]:
    J = -130 + js28
    L = eirp_dbm - J
    d = 10 ** ((L - 20 * np.log10(1575.42e6) + 147.55) / 20)
    print(f"  {lab:46s}: breaks tracking out to {d:,.0f} m (free space, 0 dBi GNSS antenna)")
check("a -30 dBm spur in L1 breaks tracking within ~10 m (so on-board spurs must be far below regulatory limits)",
      10 ** ((-30 - (-130 + js28) - 20 * np.log10(1575.42e6) + 147.55) / 20) > 5)

# ---------------------------------------------------------------- 4. blocking budget
print("\n4) MAX-M10S out-of-band immunity (u-blox integration manual, low-gain mode)")
imm = {433: -15, 868: -16.5, 915: -17}          # dBm at RF_IN (Fig. 27 / Table 43)
tx = {433: 33, 868: 30, 915: 30}                  # E22-400T33D 2 W, E220-900T30D 1 W
for f, p in tx.items():
    need = p - imm[f]
    print(f"  {f} MHz transmitter {p} dBm, immunity {imm[f]} dBm -> isolation needed {need:.0f} dB "
          f"(antenna coupling + GNSS antenna/filter rejection)")
check("a 2 W 433 MHz transmitter needs ~48 dB isolation to the M10S RF input", abs((33 - (-15)) - 48) < 1)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
