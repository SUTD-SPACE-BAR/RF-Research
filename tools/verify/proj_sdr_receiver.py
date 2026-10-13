#!/usr/bin/env python3
"""
proj_sdr_receiver.py -- design calculations for kb/20-projects-recipes/sdr-receiver-build.md

SDR ground receiver / recorder / spectrum monitor for the LoRa rocket downlinks (433.125 and 868.125/905 MHz),
behind the masthead LNA chain of ground-station-tracking-yagi.md, decoding offline with gr-lora_sdr.

 1. Frequency plan: offset tuning (DC spike, IQ image), sample rate vs LoRa BW and gr-lora_sdr oversampling,
    decimation chain.
 2. Noise cascade into the SDR (LNA -> SAW -> coax -> splitter -> SDR) and how much SDR gain is "enough"
    (noise-floor rise test).
 3. Dynamic-range budget: link received powers from proj_lora_link.py (pad .. 15 km) vs 8-bit / 12-bit
    in-channel dynamic range -> "high" and "low" gain channels.
 4. Recording: data rates, storage, SigMF metadata; timing error of sample-count timestamps with a 1 ppm clock.
 5. Frequency calibration: SDR clock error vs Doppler (why you calibrate on the pad signal).
 6. Spectrum-monitor sweep (rtl_power-style): bins, RBW, revisit time.
Run: python3 tools/verify/proj_sdr_receiver.py
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from rfcalc.noise import Stage, cascade  # noqa: E402
from rfcalc.lora import sensitivity_dbm  # noqa: E402

C0 = 299_792_458.0


def main():
    print("=" * 92)
    print("1) Frequency plan")
    for fc, bw, lab in ((433.125e6, 250e3, "433 primary"), (868.125e6, 250e3, "868 secondary (SG)"),
                        (905.0e6, 500e3, "905 IREC Mode A")):
        for fs in (1.024e6, 2.048e6):
            off = 0.25 * fs if bw <= 0.25 * fs else None
            if off is None:
                print(f"   {lab}: fs {fs/1e6:.3f} MS/s too narrow for offset tuning a {bw/1e3:.0f} kHz channel")
                continue
            lo = fc - off
            img = lo - off
            os_factor = fs / bw
            print(f"   {lab}: fs {fs/1e6:.3f} MS/s, tune LO to {lo/1e6:.4f} MHz (signal at +{off/1e3:.0f} kHz, DC spike "
                  f"{off/1e3:.0f} kHz away, IQ image at {img/1e6:.4f} MHz); oversampling fs/BW = {os_factor:.1f} "
                  f"-> decimate to 4x BW = {4*bw/1e6:.2f} MS/s for gr-lora_sdr (factor {fs/(4*bw):.2f})")
    print("   gr-lora_sdr works at os_factor 2-8; 4 is a robust choice (kb/14 multirate page)")

    print("\n2) Noise cascade into the SDR (433 MHz; LNA TQP3M9036-class, SAW 2.5 dB, 15 m LMR-240 2.6 dB)")
    for nf_sdr, lab in ((5.4, "RTL-SDR V3 (measured 5.4 dB @437 MHz)"), (7.5, "Airspy Mini (measured 7.4 dB)"),
                        (6.2, "Pluto (measured ~6.1 dB)"), (11.1, "HackRF (11 dB)")):
        for split in (3.5, 7.0):
            st = [Stage("LNA", 19.8, nf=0.45), Stage("SAW", -2.5), Stage("coax", -2.6), Stage("split", -split),
                  Stage("sdr", 0, nf=nf_sdr)]
            nf = cascade(st)[-1]["NF_cum_dB"]
            g_before = 19.8 - 2.5 - 2.6 - split
            # SDR contribution to total noise
            te_sdr = 290 * (10 ** (nf_sdr / 10) - 1) / 10 ** (g_before / 10)
            te_tot = 290 * (10 ** (nf / 10) - 1)
            print(f"   {lab:38s}, {split:.1f} dB split: system NF {nf:4.2f} dB; SDR is {100*te_sdr/(te_tot+290):4.1f} % "
                  f"of (T_ant 290 K + T_e); noise rise antenna-vs-terminated-SDR = "
                  f"{10*math.log10((te_tot+290)/(te_sdr + 0)) if te_sdr>0 else 0:5.1f} dB")
    print("   Rule: raise SDR gain until the floor rises >= 6-10 dB when the LNA chain is connected vs a 50-ohm load at the SDR input;")
    print("   more gain only costs headroom.")

    print("\n3) Dynamic range: signals at the SDR input (after +12.2 dB net chain gain to a 2-way split) vs ADC")
    g_net = 19.8 - 2.5 - 2.6 - 3.5
    nf_sys = cascade([Stage("LNA", 19.8, nf=0.45), Stage("SAW", -2.5), Stage("coax", -2.6), Stage("split", -3.5),
                      Stage("sdr", 0, nf=5.4)])[-1]["NF_cum_dB"]
    events = [("pad, 30 m, main lobe (from GS recipe)", -9.6), ("lift-off, station C 5 km, 33 dBm", -58.5),
              ("apogee, station C, 33 dBm", -66.7), ("apogee, station C, 10 mW e.r.p.", -89.2),
              ("15 km tail-null worst case, 10 mW e.r.p.", -106.7), ("SF7/250 sensitivity (system)", None)]
    for bw, lab in ((250e3, "SF7/250"),):
        n_ch = -174 + 10 * math.log10(bw) + nf_sys
        s_sens = sensitivity_dbm(7, bw, nf_db=nf_sys)
        print(f"   system NF {nf_sys:.2f} dB -> noise in {bw/1e3:.0f} kHz = {n_ch:.1f} dBm at the antenna terminals; "
              f"SF7/250 sensitivity {s_sens:.1f} dBm")
        for name, p in events:
            if p is None:
                p = s_sens
            print(f"      {name:42s}: {p:7.1f} dBm at LNA input -> SNR in channel {p - n_ch:6.1f} dB")
    print("   in-channel dynamic range (kb/14 SDR survey): RTL-SDR 8-bit 56.7 dB (125 kHz), ~53.7 dB (250 kHz); Airspy/Pluto ~80 dB")
    for dr, lab in ((53.7, "RTL-SDR"), (80.0, "12-bit SDR")):
        for margin in (6.0, 10.0):
            top = margin + dr - margin * 0          # noise placed 'margin' dB above the quantisation floor
            clip_snr = dr - margin
            print(f"   {lab}: noise {margin:.0f} dB above ADC floor -> clips at in-channel SNR ~{clip_snr:.0f} dB "
                  f"(= {n_ch + clip_snr:.1f} dBm at the LNA input)")
    print("   -> one RTL-SDR cannot hold the pad/early-flight (-10..-60 dBm) and the far link (-100..-125 dBm) at one gain:")
    print("      use two SDRs off the splitter: 'low' channel with a 30 dB pad (or 30 dB less gain), 'high' channel at full gain")

    print("\n4) Recording")
    for fs, bits, lab in ((1.024e6, 8, "RTL 1.024 MS/s cu8"), (2.048e6, 8, "RTL 2.048 MS/s cu8"),
                          (1.0e6, 16, "Pluto 1 MS/s ci16"), (2.0e6, 32, "cf32 after conversion 2 MS/s")):
        rate = fs * 2 * bits / 8
        print(f"   {lab:30s}: {rate/1e6:6.2f} MB/s, {rate*3600/1e9:7.1f} GB/h")
    for ppm in (1.0, 10.0):
        for dur in (600.0, 1800.0):
            err = ppm * 1e-6 * dur
            print(f"   sample-count timestamps, clock error {ppm:4.1f} ppm, {dur/60:4.0f} min: drift {err*1e3:6.2f} ms "
                  f"(vs LoRa SF7/250 packet 41 ms; vs 1 PPS alignment)")

    print("\n5) Frequency calibration vs Doppler")
    for f in (433.125e6, 868.125e6, 905e6):
        for ppm in (0.5, 1.0, 2.0):
            print(f"   {f/1e6:7.3f} MHz: SDR clock {ppm:3.1f} ppm -> {ppm*f/1e6:6.0f} Hz offset; flight Doppler peak "
                  f"(station C, 330 m/s max radial) {330*f/C0:5.0f} Hz")
    print("   -> measure the rocket's carrier on the pad (static) for >= 1 min and use it as the zero-Doppler reference;")
    print("      the rocket's own crystal offset and the SDR's offset cancel in the difference (thermal drift does not)")

    print("\n6) Spectrum monitor (rtl_power-style hop) 400-450 MHz and 850-930 MHz")
    for span, lab in ((50e6, "400-450 MHz"), (80e6, "850-930 MHz")):
        for bin_hz in (1e3, 10e3):
            hops = math.ceil(span / 2.0e6)
            fft = 2.4e6 / bin_hz
            t_hop = 0.05 + 10 * (1 / bin_hz)        # settle + 10 averages per bin
            print(f"   {lab}: {hops} hops of 2 MHz, bin {bin_hz/1e3:.0f} kHz (FFT {fft:.0f}), ~{t_hop*1e3:.0f} ms per hop -> "
                  f"revisit {hops*t_hop:.1f} s")


if __name__ == "__main__":
    main()
