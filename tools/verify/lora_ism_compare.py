#!/usr/bin/env python3
"""
lora_ism_compare.py — normalise datasheet sensitivities of LoRa and FSK/GFSK/other ISM radios
to a common figure of merit, for kb/15-lora-ism-radios/other-ism-radios-fsk-2g4.md.

FOM = S − 10 log10(Rb) + 174  [dB]  =  NF + Eb/N0 (+ any receiver-filter excess)
Lower is better. Also: sensitivity rescaled to a common bit rate (S + 10 log10(R/Rb)),
assuming the radio could keep the same Eb/N0 at that rate (idealisation).
Datasheet values (see page for sources and test conditions — these differ: PER 1 % vs BER 0.1 % vs 1e-5).

Run: python3 tools/verify/lora_ism_compare.py
"""
import math

RADIOS = [
    # name, band, sensitivity dBm, bit rate b/s, condition
    ("SX1262 LoRa SF12/125", "sub-GHz", -137, 244, "PER 1 %, 64 B"),
    ("SX1262 LoRa SF7/125", "sub-GHz", -124, 5469, "PER 1 %, 64 B"),
    ("SX1262 LoRa SF7/500", "sub-GHz", -117, 21875, "PER 1 %, 64 B"),
    ("LLCC68 LoRa SF9/125", "sub-GHz", -129, 1758, "module DS"),
    ("SX1262 GFSK 4.8 kb/s", "sub-GHz", -118, 4800, "BER 0.1 %"),
    ("SX1262 GFSK 250 kb/s", "sub-GHz", -104, 250000, "BER 0.1 %"),
    ("CC1101 GFSK 0.6 kBaud 433", "sub-GHz", -116, 600, "PER 1 %, 20 B"),
    ("CC1101 GFSK 38.4 kBaud 433", "sub-GHz", -104, 38400, "PER 1 %, 20 B"),
    ("CC1101 GFSK 250 kBaud 433", "sub-GHz", -95, 250000, "PER 1 %, 20 B"),
    ("Si4463 GFSK 0.5 kb/s", "sub-GHz", -126, 500, "BER 0.1 %"),
    ("Si4463 GFSK 40 kb/s", "sub-GHz", -110, 40000, "BER 0.1 %"),
    ("Si4463 GFSK 500 kb/s", "sub-GHz", -97, 500000, "BER 0.1 %"),
    ("RFD900x 12 kb/s", "900 MHz", -111, 12000, "BER 1e-5"),
    ("RFD900x 64 kb/s", "900 MHz", -105, 64000, "BER 1e-5"),
    ("RFD900x 224 kb/s", "900 MHz", -94, 224000, "BER 1e-5"),
    ("XBee-PRO 900HP 10 kb/s", "900 MHz", -110, 10000, "datasheet"),
    ("XBee-PRO 900HP 200 kb/s", "900 MHz", -101, 200000, "datasheet"),
    ("CC1310 LRM 625 b/s", "sub-GHz", -124, 625, "datasheet (TCXO)"),
    ("SX1280 LoRa SF12/203", "2.4 GHz", -132, 476, "PER 1 %, 10 B"),
    ("SX1280 LoRa SF7/1625", "2.4 GHz", -108, 71000, "PER 1 %, 10 B"),
    ("SX1280 FLRC 130 kb/s", "2.4 GHz", -106, 130000, "PER 1 %"),
    ("SX1280 FLRC 650 kb/s", "2.4 GHz", -100.5, 650000, "PER 1 %"),
    ("nRF52840 BLE coded 125 kb/s", "2.4 GHz", -103, 125000, "datasheet"),
    ("nRF52840 BLE 1 Mb/s", "2.4 GHz", -95, 1000000, "datasheet"),
    ("nRF24L01+ 250 kb/s", "2.4 GHz", -94, 250000, "datasheet"),
    ("nRF24L01+ 2 Mb/s", "2.4 GHz", -82, 2000000, "datasheet"),
]


def main():
    print(f"{'radio':32s} {'band':8s} {'S[dBm]':>7s} {'Rb':>9s} {'FOM=NF+Eb/N0':>13s}  S@20kb/s  condition")
    for name, band, s, rb, cond in RADIOS:
        fom = s - 10 * math.log10(rb) + 174
        s20 = s + 10 * math.log10(20000 / rb)
        print(f"{name:32s} {band:8s} {s:7.1f} {rb:9.0f} {fom:13.1f}  {s20:8.1f}  {cond}")
    print("\nFree-space path-loss penalty relative to 433 MHz for equal antenna gains:")
    for f in (433.125, 868, 923, 2440):
        print(f"   {f:7.1f} MHz: +{20*math.log10(f/433.125):4.1f} dB")


if __name__ == "__main__":
    main()
