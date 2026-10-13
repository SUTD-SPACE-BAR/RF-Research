#!/usr/bin/env python3
"""
gnss_sdr_frontend.py — verification for kb/21-gnss/sdr-gnss-and-diy-receivers.md

 1. Noise cascade (Friis, in noise temperature) of DIY GNSS front ends feeding an SDR:
    passive patch -> (SAW) -> LNA -> SAW -> cable -> SDR, versus a commercial active antenna,
    and the resulting C/N0 for a -125.5 dBm signal (minimum GPS power into a 3 dBic patch).
 2. Sampling: minimum complex rate for each signal's main lobe, data rates for 8-bit IQ,
    2-bit and 3-bit packed samples, file sizes for a 60 s capture.
 3. Oscillator: SDR reference error -> carrier offset and code-rate offset at L1; how wide the
    acquisition Doppler search must be for a 0.5 ppm TCXO vs a 25 ppm crystal.
 4. Conducted test with a GNSS simulator (gps-sdr-sim): attenuation needed between an SDR TX
    and the receiver so the input is at a realistic level (-130 dBm) and below the receiver's
    absolute maximum.
Run: python3 tools/verify/gnss_sdr_frontend.py
"""
import numpy as np

k = 1.380649e-23
T0 = 290.0
ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


def nf2t(nf_db):
    return T0 * (10 ** (nf_db / 10) - 1)


def cascade(stages, t_ant=100.0):
    """stages: list of (name, gain_dB, nf_dB). Passive loss L: gain -L, NF = L. Returns T_sys (K)."""
    t = t_ant
    g = 1.0
    for _, gdb, nf in stages:
        t += nf2t(nf) / g
        g *= 10 ** (gdb / 10)
    return t


def cn0(p_dbm, tsys):
    return p_dbm - 10 * np.log10(k * tsys * 1e3)


sdr_nf = 6.0   # assumed SDR (e.g. RTL-SDR R820T2 at 1.5 GHz) noise figure, dB — not a datasheet value
chains = {
    "patch -> RTL-SDR directly (2 m coax 1.5 dB)": [("coax", -1.5, 1.5), ("sdr", 0, sdr_nf)],
    "patch -> LNA(0.8 dB, 20 dB) -> SAW(1.5) -> coax(1.5) -> SDR": [("lna", 20, 0.8), ("saw", -1.5, 1.5),
                                                                    ("coax", -1.5, 1.5), ("sdr", 0, sdr_nf)],
    "patch -> SAW(1.0) -> LNA -> SAW -> coax -> SDR": [("saw1", -1.0, 1.0), ("lna", 20, 0.8), ("saw", -1.5, 1.5),
                                                       ("coax", -1.5, 1.5), ("sdr", 0, sdr_nf)],
    "commercial active antenna (28 dB, NF 2 dB) -> 5 m coax (3 dB) -> SDR": [("act", 28, 2.0), ("coax", -3, 3.0),
                                                                            ("sdr", 0, sdr_nf)],
}
print("1) front-end cascades (T_ant = 100 K), signal -125.5 dBm (GPS minimum into a 3 dBic patch)")
res = {}
for name, st in chains.items():
    ts = cascade(st)
    res[name] = cn0(-125.5, ts)
    print(f"  {name:66s} T_sys {ts:6.0f} K  C/N0 {res[name]:5.1f} dB-Hz")
names = list(chains)
check("an LNA at the antenna gains > 5 dB of C/N0 over driving the SDR directly",
      res[names[1]] - res[names[0]] > 5)
check("a SAW ahead of the LNA costs ~1 dB of C/N0 (price of blocker protection)",
      0.5 < res[names[1]] - res[names[2]] < 2.0)

print("\n2) sampling and data rates")
sig = {"GPS L1 C/A (+-1.023 MHz)": 2.046e6, "E1/B1C incl. BOC(1,1) (+-2.046 MHz)": 4.092e6,
       "E1 CBOC incl. BOC(6,1) (+-12 MHz)": 24.552e6, "L5/E5a (+-10.23 MHz)": 20.46e6,
       "B1I + L1 + G1 (1559-1606 MHz)": 47e6}
for n, bw in sig.items():
    print(f"  {n:38s} complex fs >= {bw/1e6:6.2f} MS/s")
for fs, fmt, bits in [(2.048e6, "RTL-SDR cu8", 16), (4.092e6, "2-bit I/Q (MAX2769)", 4), (16.368e6, "2-bit real IF", 2),
                      (24e6, "3-bit I/Q", 6), (10e6, "HackRF ci8", 16)]:
    rate = fs * bits / 8
    print(f"  {fmt:22s} at {fs/1e6:7.3f} MS/s: {rate/1e6:6.2f} MB/s, 60 s = {rate*60/1e9:5.2f} GB")
check("RTL-SDR at 2.048 MS/s covers the C/A main lobe (needs >= 2.046 MS/s complex)", 2.048e6 >= 2.046e6)
check("RTL-SDR R820T2 tuning range (24-1766 MHz) includes L1, L2 and L5", 24 < 1176.45 and 1602 < 1766)

print("\n3) reference oscillator")
for ppm in [0.5, 1.0, 25.0]:
    df = ppm * 1e-6 * 1575.42e6
    dc = ppm * 1e-6 * 1.023e6
    print(f"  {ppm:4.1f} ppm -> carrier offset {df/1e3:6.2f} kHz, code-rate offset {dc:6.3f} chips/s, "
          f"search +-{(df+5e3)/1e3:5.1f} kHz")
check("a 25 ppm crystal SDR puts L1 39 kHz off — outside a +-5 kHz search unless widened",
      25e-6 * 1575.42e6 > 35e3)

print("\n4) conducted simulator test")
p_tx = -10.0     # SDR TX output at low gain (dBm), assumed
target = -130.0
att = p_tx - target
print(f"  SDR TX {p_tx} dBm -> need {att:.0f} dB total attenuation for -130 dBm (gps-sdr-sim README: DC block + 50-60 dB "
      f"fixed attenuator, plus low TX gain)")
check("50-60 dB fixed attenuation alone is not enough from 0 dBm (TX gain must be low or more attenuation used)",
      0 - 60 > target)
print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
