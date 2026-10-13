#!/usr/bin/env python3
"""S7 (W5-S7) small receiver numbers.
 §1 plain-language boxes for kb/07-noise-linearity/dynamic-range-sfdr-blocking.md
    (superposition + selectivity; too close = saturation; cheap SDR vs communications receiver)
 §2 S-meter calibration (IARU Region 1 R.1) for kb/07-noise-linearity/sensitivity-and-mds.md
 §3 additive (residual) phase noise of amplifiers for kb/17-test-measurement/phase-noise-measurement.md
Run: python3 tools/verify/s7_receiver_numbers.py  (< 1 s)
"""
import numpy as np

ok = True
kT0 = -173.98  # dBm/Hz


def check(name, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")


def fspl(f_mhz, d_km):
    return 32.45 + 20 * np.log10(f_mhz) + 20 * np.log10(d_km)


print("§1a Superposition + selectivity: an FM broadcaster vs the weakest LoRa packet")
erp_w = 50e3                       # 50 kW e.r.p. (assumed regional broadcaster)
eirp_dbm = 10 * np.log10(erp_w * 1e3) + 2.15
pr = eirp_dbm - fspl(100, 10) + 2.15   # dipole at 10 km
print(f"  50 kW e.r.p. at 100 MHz, 10 km, dipole: {pr:.1f} dBm; vs SX1262 SF12 sensitivity -137 dBm: {pr+137:.0f} dB")
check("FM station ~ -11 dBm", abs(pr + 11.2) < 0.3)

print("§1b Too close = saturation: 1 W at 434 MHz, 2 dBi both ends")
f = 433.92
for d in (0.001, 0.01, 0.1):
    p = 30 + 2 + 2 - fspl(f, d)
    print(f"  d = {d*1e3:5.0f} m: {p:6.1f} dBm  (chain IP1dB -28.9 dBm; SX1262 blocking @10 MHz -35, @1 MHz -46 dBm)")
p1 = 30 + 4 - fspl(f, 0.001)
check("1 m -> ~ +9 dBm (near-field caveat)", abs(p1 - 8.8) < 0.2)
for lim, lab in ((-35, "10 MHz away"), (-46, "1 MHz away")):
    d = 10 ** ((34 - lim - 32.45 - 20 * np.log10(f)) / 20)
    print(f"  distance to fall to {lim} dBm ({lab}): {d*1e3:.0f} m")
d35 = 10 ** ((34 + 35 - 32.45 - 20 * np.log10(f)) / 20) * 1e3
check("-35 dBm reached at ~155 m", 140 < d35 < 170)

print("§1c Cheap SDR vs communications receiver")
for L, lab in ((-90, "cheap integer-N tuner PLL (illustrative)"), (-130, "low-noise synthesiser (illustrative)")):
    for B in (2.4e3, 125e3):
        rmdr = -L - 10 * np.log10(B)
        print(f"  L(10 kHz) {L} dBc/Hz [{lab}], B {B/1e3:6.1f} kHz: RMDR = {rmdr:.1f} dB")
rm = 90 - 10 * np.log10(2.4e3)
check("RMDR -90 dBc/Hz, 2.4 kHz = 56.2 dB", abs(rm - 56.2) < 0.1)
sq = 6.02 * 8 + 1.76
pg = 10 * np.log10(2.4e6 / 2.4e3)
print(f"  8-bit ADC ideal SQNR {sq:.1f} dB in 2.4 MHz (complex) + processing gain to 2.4 kHz {pg:.1f} dB = {sq+pg:.1f} dB; "
      f"with ~45 dB real SNR: {45+pg:.1f} dB")

print("§2 S-meter (IARU Region 1 Technical Recommendation R.1, 1981)")
for band, s9 in (("HF (< 30 MHz)", -73), ("VHF/UHF", -93)):
    row = []
    for S in (1, 3, 5, 7, 9):
        p = s9 - 6 * (9 - S)
        v = np.sqrt(10 ** (p / 10) * 1e-3 * 50) * 1e6
        row.append(f"S{S} {p} dBm/{v:.3g} uV")
    print(f"  {band}: " + "; ".join(row))
v9 = np.sqrt(10 ** (-73 / 10) * 1e-3 * 50) * 1e6
check("S9 HF = 50 uV in 50 ohm", abs(v9 - 50.1) < 0.2)


def s_units(p, s9):
    return 9 + (p - s9) / 6


n_res = kT0 + 10 * np.log10(2.4e3) + 44.8            # residential 10 MHz, P.372 Fa 44.8 dB
n_th = kT0 + 10 * np.log10(2.4e3)
print(f"  HF 10 MHz, 2.4 kHz SSB: residential external noise {n_res:.1f} dBm = S{s_units(n_res,-73):.1f}; "
      f"290 K thermal only {n_th:.1f} dBm = S{s_units(n_th,-73):.1f} (below S1)")
Ta = 290 * 10 ** (7.4 / 10)
Te = 290 * (10 ** 0.2 - 1)
n_v = 10 * np.log10(1.380649e-23 * (Ta + Te) * 12.5e3) + 30
print(f"  144 MHz rural (Fa 7.4 dB), NF 2 dB, 12.5 kHz: noise {n_v:.1f} dBm = S{s_units(n_v,-93):.1f} (VHF scale)")
check("HF residential noise ~S5", 5.0 < s_units(n_res, -73) < 5.6)
lora = -137
print(f"  a just-decodable SF12 LoRa packet (-137 dBm) on the VHF/UHF scale: S{s_units(lora,-93):.1f} "
      f"(below S1 = -141 dBm? {'no' if lora > -141 else 'yes'})")

print("§3 Additive (residual) phase noise of an amplifier")
for NF, P0 in ((3, -30), (3, -10), (6, 0), (1, 10)):
    Lw = kT0 + NF - P0 - 10 * np.log10(2)
    print(f"  NF {NF} dB, input {P0:4d} dBm: white floor L = FkT0/(2P0) = {Lw:.1f} dBc/Hz")
Lw = kT0 + 3 + 30 - 10 * np.log10(2)
check("NF 3, -30 dBm -> -144 dBc/Hz", abs(Lw + 144.0) < 0.1)
b1 = -130  # dB rad^2/Hz (SiGe LPNT32 in Boudot & Rubiola Table 1)
for fo in (1, 100, 1e4):
    print(f"  flicker b-1 = {b1} dBrad^2/Hz: L({fo:g} Hz) = {b1 - 10*np.log10(fo) - 3.01:.1f} dBc/Hz")
for NF, P0 in ((3, -30), (3, 0)):
    fc = 10 ** (b1 / 10) / 10 ** ((kT0 + NF - P0) / 10)
    print(f"  corner f_c = b-1 P0/(F kT0) at NF {NF} dB, P0 {P0} dBm: {fc:.3g} Hz")
fc0 = 10 ** (b1 / 10) / 10 ** ((kT0 + 3 - 0) / 10)
check("corner moves up with drive (1.26e4 Hz at 0 dBm)", abs(fc0 / 1.25e4 - 1) < 0.03)
print("  cascade of m equal amplifiers: flicker +10log m (2: +3.0 dB, 3: +4.8 dB); m in parallel: -10log m")
for dtau, fo in ((1e-9, 1e4), (1e-9, 1e6), (10e-9, 1e6)):
    sup = 10 * np.log10(4 * np.sin(np.pi * fo * dtau) ** 2)
    print(f"  split-source residual test, delay mismatch {dtau*1e9:.0f} ns at {fo:g} Hz: source noise suppressed by {-sup:.1f} dB")
sup = -10 * np.log10(4 * np.sin(np.pi * 1e4 * 1e-9) ** 2)
check("1 ns mismatch at 10 kHz suppresses source by ~84 dB", abs(sup - 84.0) < 0.2)

print("\nALL PASS" if ok else "\nSOME FAILED")
