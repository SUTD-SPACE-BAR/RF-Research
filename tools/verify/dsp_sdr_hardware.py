#!/usr/bin/env python3
"""Verification of derived numbers in kb/14-sdr-dsp/sdr-hardware-survey.md

Checks (PASS/FAIL):
 1. Friis cascades for a 433 MHz LoRa ground station with an RTL-SDR (measured NF 5.4 dB @437 MHz):
    SDR alone, SAW->SDR, LNA->SAW->SDR, SAW->LNA->SDR.
 2. In-channel dynamic range estimate of 8-bit (ENOB ~7) vs 12-bit ADCs with processing gain.
 3. Host data rates for common sample formats and rates (USB2 budget).
 4. FMCW range resolution c/2B for Pluto native (20 MHz) and AD9364 (56 MHz) bandwidths.
 5. KrakenSDR array geometry at 433.92 MHz (lambda/2 spacing, circular array radius).
 6. RX888 noise figure implied by a -155 dBm/Hz floor (as reported at +20 dB gain).
"""
import numpy as np

ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def db2lin(x):
    return 10 ** (x / 10)


def lin2db(x):
    return 10 * np.log10(x)


def friis(stages):
    """stages: list of (NF_dB, gain_dB). Returns cascade NF in dB."""
    F, G = 1.0, 1.0
    first = True
    for nf, g in stages:
        f = db2lin(nf)
        F = f if first else F + (f - 1) / G
        G *= db2lin(g)
        first = False
    return lin2db(F)


sdr = (5.4, 0.0)  # RTL-SDR V3 measured NF at 437 MHz (Libre Space Foundation eval); gain irrelevant as last stage
lna = (0.8, 20.0)
saw = (2.0, -2.0)
cases = {
    "SDR alone": [sdr],
    "SAW -> SDR": [saw, sdr],
    "LNA -> SAW -> SDR": [lna, saw, sdr],
    "SAW -> LNA -> SDR": [saw, lna, sdr],
}
res = {k: friis(v) for k, v in cases.items()}
for k, v in res.items():
    print(f"      {k:20s}: NF = {v:.2f} dB")
check("LNA first: system NF ~0.96 dB", abs(res["LNA -> SAW -> SDR"] - 0.96) < 0.02)
check("SAW first (better blocking): ~2.89 dB", abs(res["SAW -> LNA -> SDR"] - 2.89) < 0.02)
check("SAW -> SDR without LNA: ~7.4 dB", abs(res["SAW -> SDR"] - 7.40) < 0.02)

# 2. dynamic range in channel (ADC-limited, full-scale sine to noise in channel B)
for bits_eff, fs, label in [(7.0, 2.4e6, "RTL-SDR (ENOB ~7) 2.4 MS/s"), (10.4, 10e6, "Airspy R2 (ENOB 10.4, 10 MS/s IQ)"),
                           (11.0, 4e6, "AD936x-class (ENOB ~11) 4 MS/s")]:
    snr = 6.02 * bits_eff + 1.76
    pg = 10 * np.log10(fs / 125e3)
    print(f"      {label}: ADC SNR {snr:.1f} dB + PG to 125 kHz {pg:.1f} dB = {snr+pg:.1f} dB in-channel")
check("RTL-SDR in-channel DR ~56.7 dB (ADC-limited, before tuner gain/AGC)", abs(6.02 * 7 + 1.76 + 10 * np.log10(2.4e6 / 125e3) - 56.73) < 0.05)

# 3. data rates
rates = [("RTL-SDR cu8", 2.4e6, 2), ("HackRF sc8", 20e6, 2), ("Pluto sc16", 4e6, 4), ("Pluto sc16", 61.44e6, 4),
         ("B210 sc16 2ch", 30.72e6, 8), ("fc32 file", 2.4e6, 8)]
for name, fs, bps in rates:
    mb = fs * bps / 1e6
    print(f"      {name:16s} @ {fs/1e6:6.2f} MS/s: {mb:7.1f} MB/s, {mb*3600/1000:6.1f} GB/h")
check("USB2 HS (~40 MB/s practical) cannot carry Pluto sc16 at 61.44 MS/s (245.8 MB/s)", 61.44e6 * 4 / 1e6 > 40)
check("RTL-SDR 2.4 MS/s cu8 = 4.8 MB/s = 17.3 GB/h", abs(2.4e6 * 2 * 3600 / 1e9 - 17.28) < 0.01)

# 4. FMCW range resolution
c = 299792458.0
for B in (20e6, 56e6):
    print(f"      FMCW B = {B/1e6:.0f} MHz: range resolution {c/(2*B):.2f} m")
check("20 MHz -> 7.49 m; 56 MHz -> 2.68 m", abs(c / 40e6 - 7.49) < 0.01 and abs(c / 112e6 - 2.68) < 0.01)

# 5. KrakenSDR geometry
lam = c / 433.92e6
d = lam / 2
R = d / (2 * np.sin(np.pi / 5))  # 5-element uniform circular array with chord = d
print(f"      433.92 MHz: lambda = {lam:.3f} m, lambda/2 = {d:.3f} m, 5-element UCA radius for lambda/2 chord = {R:.3f} m")
check("lambda/2 at 433.92 MHz = 0.345 m", abs(d - 0.3454) < 0.001)

# 6. RX888 implied NF
nf = -155 + 174
check("floor -155 dBm/Hz implies NF ~19 dB", abs(nf - 19) < 1e-9, f"{nf} dB")

print("\nALL PASS" if ok_all else "\nSOME FAIL")
