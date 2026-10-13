#!/usr/bin/env python3
"""
lora_doppler.py — Doppler shift, Doppler rate, clock-offset and timing-drift budget for LoRa
links on rockets.

Used by: kb/15-lora-ism-radios/lora-impairments-doppler-drift-timing.md,
         kb/15-lora-ism-radios/rocket-telemetry-radio-design.md

Physics (non-relativistic, v << c):
  f_D   = (v_r / c) f_c                    radial velocity v_r [m/s], carrier f_c [Hz]
  df/dt = (a_r / c) f_c                    radial acceleration a_r [m/s²]  (Doppler rate)
  clock ppm error ε ⇒ carrier error ε f_c AND chip-rate error ε (same crystal drives both)
  Doppler also compresses time: chip-rate error = v_r / c  (v/c expressed in ppm)
Tolerances (Semtech SX1276 Rev 7 / SX1261-2 Rev 1.2 datasheets):
  |Δf_total| ≤ 25 % of BW (carrier offset between TX and RX, no sensitivity degradation)
  SF12 ±50 ppm, SF11 ±100 ppm, SF10 ±200 ppm (the tighter of the two limits applies)
Drift-rate tolerance: from lora_css_sim.critical_drift_rate (idealised receiver that removes
  the start-of-payload offset and does not track; real Semtech tracking is undocumented).

Run:  python3 tools/verify/lora_doppler.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from lora_css_sim import critical_drift_rate, payload_symbols  # noqa: E402
from lora_toa import toa_sx126x, BW_HZ  # noqa: E402

C = 299_792_458.0
G0 = 9.80665
A_SOUND = 343.0  # m/s at 20 °C sea level (ISA 15 °C: 340.3 m/s; 11 km: 295 m/s)

FREQS = {"433.125 MHz (E22-400T33D default)": 433.125e6,
         "868 MHz": 868e6,
         "915 MHz": 915e6,
         "923 MHz (AS923 / SG)": 923e6,
         "2.44 GHz (SX1280)": 2.44e9}


def doppler_hz(v, f):
    return v / C * f


def doppler_rate_hz_s(a, f):
    return a / C * f


def main():
    print("1) Doppler shift vs rocket speed (radial component = full speed, worst case)")
    speeds = [("Mach 0.5", 0.5 * A_SOUND), ("Mach 1", A_SOUND), ("Mach 2", 2 * A_SOUND),
              ("Mach 3", 3 * A_SOUND), ("Mach 5", 5 * A_SOUND), ("orbital LEO 7.6 km/s", 7600.0)]
    hdr = "   speed               v[m/s]  v/c[ppm] | " + " | ".join(k.split(" (")[0] for k in FREQS)
    print(hdr)
    for name, v in speeds:
        cells = " | ".join(f"{doppler_hz(v, f)/1e3:7.2f} kHz" for f in FREQS.values())
        print(f"   {name:18s} {v:7.0f}  {v/C*1e6:7.2f}  | {cells}")

    print("\n2) Carrier-offset budget: 25 % of BW vs Doppler (Mach 5) + clock errors")
    print("   BW[kHz]  25%BW[kHz] | Mach5 Doppler @433 / @923 [kHz] | max per-side clock error left [ppm] @433 / @923")
    vm5 = 5 * A_SOUND
    for bwk in (7.8, 10.4, 15.6, 20.8, 31.25, 41.7, 62.5, 125, 250, 500):
        bw = BW_HZ[bwk]
        lim = 0.25 * bw
        out = []
        for f in (433.125e6, 923e6):
            left = lim - doppler_hz(vm5, f)
            out.append(left / 2 / f * 1e6)  # TX and RX errors add worst-case: 2 ε f
        print(f"   {bwk:7}  {lim/1e3:9.2f}  |   {doppler_hz(vm5,433.125e6)/1e3:5.2f} / {doppler_hz(vm5,923e6)/1e3:5.2f}"
              f"                   |   {out[0]:7.2f} / {out[1]:7.2f}")
    print("   (negative = Doppler alone exceeds the window. Worst case assumes TX and RX clock errors\n"
          "    add. ±20 ppm crystals per side fit at 433 MHz only for BW ≥ 125 kHz and at 923 MHz only\n"
          "    for BW ≥ 250 kHz; ±10 ppm fits 433/62.5 kHz and 923/125 kHz. Below that use a TCXO.)")

    print("\n3) Semtech ppm limits reinterpreted as timing slip per symbol (inference):")
    for sf, ppm in ((10, 200), (11, 100), (12, 50)):
        print(f"   SF{sf}: ±{ppm} ppm × 2^SF = {ppm*1e-6*2**sf:.3f} chip per symbol")
    print("   => constant ≈0.2 chip/symbol: the ppm limit is a chip-timing (sampling-clock) limit.")
    for name, v in speeds[:5]:
        print(f"   {name:8s}: v/c = {v/C*1e6:5.2f} ppm  (≪ 50 ppm SF12 limit)")

    print("\n4) Doppler rate from radial acceleration:")
    accs = [1, 3, 5, 10, 15, 20, 30, 50]
    print("   a[g]  " + "  ".join(f"{k.split(' (')[0]:>12s}" for k in FREQS))
    for a in accs:
        print(f"   {a:4d}  " + "  ".join(f"{doppler_rate_hz_s(a*G0, f):9.1f} Hz/s" for f in FREQS.values()))

    print("\n5) Drift-rate limit per SF (32-byte payload, BW125/250/500, no in-packet tracking)")
    print("   -> max radial acceleration [g] before the last payload symbol hits a decision boundary")
    for bwk in (125, 250, 500):
        bw = BW_HZ[bwk]
        row433, row923 = [], []
        for sf in range(7, 13):
            de = (2 ** sf / bw) >= 16.38e-3
            nsym = payload_symbols(32, sf, de=de)
            rc = critical_drift_rate(sf, bw, nsym, de)
            row433.append(rc * C / 433.125e6 / G0)
            row923.append(rc * C / 923e6 / G0)
        print(f"   BW{bwk:3d} @433: " + " ".join(f"SF{sf}:{g:8.1f}" for sf, g in zip(range(7, 13), row433)))
        print(f"   BW{bwk:3d} @923: " + " ".join(f"SF{sf}:{g:8.1f}" for sf, g in zip(range(7, 13), row923)))

    print("\n5b) Semtech rule: total drift over the packet < Freq_drift_max = BW/(3·2^SF), ×16 with LDRO")
    print("    (SX1261/2 DS Rev 1.2 §4.1.2 p.23, read from the rendered equation; SX1280 DS §6.2.7.2)")
    print("    -> max radial acceleration [g] for a 32-byte packet (drift over whole ToA)")
    for bwk in (125, 250, 500):
        bw = BW_HZ[bwk]
        r433, r923 = [], []
        for sf in range(7, 13):
            de = (2 ** sf / bw) >= 16.38e-3
            t, _ = toa_sx126x(32, sf, bw)
            fmax = bw / (3 * 2 ** sf) * (16 if de else 1)
            rate = fmax / t
            r433.append(rate * C / 433.125e6 / G0)
            r923.append(rate * C / 923e6 / G0)
        print(f"   BW{bwk:3d} @433: " + " ".join(f"SF{sf}:{g:8.1f}" for sf, g in zip(range(7, 13), r433)))
        print(f"   BW{bwk:3d} @923: " + " ".join(f"SF{sf}:{g:8.1f}" for sf, g in zip(range(7, 13), r923)))

    print("\n6) Frequency change across a whole packet during boost (10 g radial) vs one FFT bin")
    for bwk in (125, 500):
        bw = BW_HZ[bwk]
        for sf in (7, 9, 10, 12):
            t, _ = toa_sx126x(32, sf, bw)
            for f in (433.125e6, 923e6):
                df = doppler_rate_hz_s(10 * G0, f) * t
                print(f"   BW{bwk} SF{sf:2d} ToA {t*1e3:7.1f} ms @{f/1e6:7.3f} MHz: Δf = {df:7.1f} Hz "
                      f"= {df/(bw/2**sf):6.2f} bins")

    print("\n7) Crystal vs TCXO frequency error (per device) at the carrier:")
    print("   (plus crystal acceleration sensitivity ~2 ppb/g [AN1200.14]: 20 g step -> "
          f"{20*2e-9*433.125e6:.1f} Hz @433, {20*2e-9*923e6:.1f} Hz @923)")
    for ppm in (0.5, 1, 2, 2.5, 10, 20, 30):
        print(f"   ±{ppm:4} ppm: @433 {ppm*433.125:7.1f} Hz,  @923 {ppm*923:7.1f} Hz")


if __name__ == "__main__":
    main()
