#!/usr/bin/env python3
"""
meas_bringup.py -- small numerical checks behind kb/17-test-measurement/rf-bring-up-debug-playbook.md

1. "Range is N x shorter than expected": dB missing under free-space (20 log N) and plane-earth
   (40 log N) propagation.
2. Receiver desense: sensitivity loss when in-band interference/noise is X dB relative to the
   receiver's own noise floor: 10 log(1 + 10^(X/10)).
3. Crystal/TCXO error: ppm -> Hz at 433/868/915 MHz and 1575.42 MHz, as a fraction of a
   125 kHz LoRa channel.
4. Attenuator chain for the flown EBYTE E22-400T33D (33 dBm = 2 W) into a tinySA Ultra / power meter.
5. PA supply droop during a TX burst: dV = I * (R_source + ESR) and the capacitor needed for a
   given ramp (dV = I t / C).
6. Clock-harmonic search: which harmonics of common board clocks fall within +/-2 MHz of 433.175,
   868-870, 902-928 MHz and 1575.42 MHz.

Run: python3 tools/verify/meas_bringup.py
"""
import numpy as np

print("=== 1. Range shortfall vs missing link budget ===")
for N in [2, 3, 5, 10]:
    print(f"  range {N:2d}x shorter: {20*np.log10(N):5.1f} dB missing (free space) or {40*np.log10(N):5.1f} dB (plane-earth, d^4)")

print("\n=== 2. Desense: interference relative to the receiver noise floor ===")
for x in [-10, -6, -3, 0, 3, 10, 20]:
    print(f"  interference {x:+3d} dB re floor -> sensitivity loss {10*np.log10(1+10**(x/10)):5.2f} dB")

print("\n=== 3. Frequency error from reference ppm ===")
for ppm in [0.5, 2, 10, 20]:
    row = []
    for f in [433.175e6, 868e6, 915e6, 1575.42e6]:
        df = f * ppm * 1e-6
        row.append(f"{f/1e6:8.3f} MHz: {df/1e3:6.2f} kHz ({100*df/125e3:5.1f} % of 125 kHz)")
    print(f"  {ppm:4.1f} ppm: " + " | ".join(row))

print("\n=== 4. E22-400T33D (33 dBm) into test gear ===")
p = 33.0
for pads in [(30,), (40,), (30, 10), (30, 20), (40, 10)]:
    a = sum(pads)
    pin = p - a
    first_diss = 10 ** (p / 10) / 1000 * (1 - 10 ** (-pads[0] / 10))
    print(f"  pads {'+'.join(map(str, pads)):>6} dB -> {pin:+5.1f} dBm at instrument; first pad dissipates {first_diss:.2f} W"
          f" -> {'OK for tinySA (<= -10 dBm)' if pin <= -10 else ('power meter range (thermocouple to +20 dBm)' if pin <= 20 else 'too hot')}")
print("  -> first pad >= 5 W rating for a 2 W radio (2x margin), or use a 30-40 dB coupler/dummy load with a sample port")

print("\n=== 5. PA supply droop during a TX burst ===")
for I, R, esr in [(1.0, 0.10, 0.02), (1.0, 0.30, 0.05), (0.6, 0.10, 0.02)]:
    print(f"  I_TX {I:.1f} A, source+trace R {R:.2f} ohm, cap ESR {esr:.2f} ohm: static droop {I*R*1000:.0f} mV, "
          f"step (ESR) {I*esr*1000:.0f} mV")
for I, t_us, dv in [(1.0, 20, 0.1), (1.0, 100, 0.1)]:
    C = I * t_us * 1e-6 / dv
    print(f"  bridging {I:.1f} A for {t_us} us with <= {dv*1000:.0f} mV droop needs C >= {C*1e6:.0f} uF (until the regulator responds)")

print("\n=== 6. Clock harmonics near the radio bands (+/-2 MHz) ===")
bands = {"433.175 MHz": (431.175e6, 435.175e6), "868-870 MHz": (866e6, 872e6),
         "902-928 MHz": (900e6, 930e6), "GNSS L1 1575.42": (1573.42e6, 1577.42e6)}
clocks = {"8 MHz": 8e6, "12 MHz": 12e6, "16 MHz": 16e6, "24 MHz": 24e6, "25 MHz": 25e6, "26 MHz": 26e6,
          "32 MHz": 32e6, "40 MHz (ESP32)": 40e6, "48 MHz (USB)": 48e6, "600 MHz (i.MX RT core)": 600e6}
for bname, (lo, hi) in bands.items():
    hits = []
    for cname, fc in clocks.items():
        n_lo, n_hi = int(np.ceil(lo / fc)), int(np.floor(hi / fc))
        for n in range(n_lo, n_hi + 1):
            hits.append(f"{cname} x{n} = {n*fc/1e6:.1f}")
    print(f"  {bname:16s}: " + ("; ".join(hits) if hits else "none"))
print("  (only a starting list: switching regulators, SD/SPI/SDIO clocks and their intermods add more; confirm with an SA + near-field probe)")
