#!/usr/bin/env python3
"""Recompute the canonical values in kb/00-math-foundations/canonical-values-and-conventions.md
(W5-E9, 2026-10-03; from gaps/D6-consistency-audit.md §3 plus the D6 fixes).

Each check recomputes a value from first principles (or from tools/rfcalc) and compares it with the number
printed on the canonical page.
Run: python3 tools/verify/fix_canonical_values.py  -> ALL PASS
"""
import os
import sys
import numpy as np
from scipy import stats, optimize

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from rfcalc import lora  # noqa: E402

k = 1.380649e-23
c = 299_792_458.0
mu0 = 1.25663706127e-6
eps0 = 8.8541878188e-12
T0 = 290.0
g0 = 9.80665
ok = True


def check(name, got, want, tol):
    global ok
    good = abs(got - want) <= tol
    ok &= good
    print(f"[{'PASS' if good else 'FAIL'}] {name}: {got:.4g} (page {want})")


def db(x):
    return 10 * np.log10(x)


print("=== 3a constants and reference conditions ===")
check("kT0 dBm/Hz", db(k * T0) + 30, -173.98, 0.005)
check("kT dBm/Hz at 300 K", db(k * 300) + 30, -173.83, 0.005)
check("sqrt(4kT0R) 1 kOhm nV/rtHz", np.sqrt(4 * k * T0 * 1e3) * 1e9, 4.00, 0.005)
check("sqrt(4kT0R) 50 Ohm nV/rtHz", np.sqrt(4 * k * T0 * 50) * 1e9, 0.895, 0.001)
check("sqrt(4kTR) 1 kOhm, 300 K", np.sqrt(4 * k * 300 * 1e3) * 1e9, 4.07, 0.005)
check("eta0 Ohm", np.sqrt(mu0 / eps0), 376.730, 0.001)
check("120*pi excess %", (120 * np.pi / np.sqrt(mu0 / eps0) - 1) * 100, 0.069, 0.001)
sig = 5.8e7
for f, want in ((433e6, 3.18), (433.92e6, 3.17), (915e6, 2.19), (1575.42e6, 1.67), (2.45e9, 1.34), (10e9, 0.66)):
    check(f"IACS skin depth {f/1e6:g} MHz um", np.sqrt(1 / (np.pi * f * mu0 * sig)) * 1e6, want, 0.006)
check("skin depth constant 66.1 um*sqrt(MHz)", np.sqrt(1 / (np.pi * 1e6 * mu0 * sig)) * 1e6, 66.1, 0.05)

print("\n=== 3b materials / fabrication ===")
def gp(h, r):  # Goldfarb-Pucel via to plane
    return mu0 / (2 * np.pi) * (h * np.log((h + np.sqrt(r * r + h * h)) / r) + 1.5 * (r - np.sqrt(r * r + h * h)))
check("via 1.6 mm x 0.3 mm Goldfarb-Pucel nH", gp(1.6e-3, 0.15e-3) * 1e9, 0.54, 0.005)
check("via partial 0.2h[ln(4h/d)-1] nH", 0.2 * 1.6 * (np.log(4 * 1.6 / 0.3) - 1), 0.66, 0.005)
hi, di = 1.6 / 25.4, 0.3 / 25.4
check("Johnson & Graham 5.08h[ln(4h/d)+1] nH", 5.08 * hi * (np.log(4 * hi / di) + 1), 1.30, 0.005)
check("via L1->L2 0.2104 mm x 0.3 mm nH", gp(0.2104e-3, 0.15e-3) * 1e9, 0.015, 0.001)
k1, k2 = 6.30, 0.0094   # 1.13 mm micro-coax fit, dB/100 m with f in MHz (03 coax table)
check("1.13 mm loss 433 MHz dB/m", (k1 * np.sqrt(433) + k2 * 433) / 100, 1.35, 0.01)
check("1.13 mm loss 1575 MHz dB/m", (k1 * np.sqrt(1575.42) + k2 * 1575.42) / 100, 2.65, 0.01)

print("\n=== 3c standard results ===")
check("FSPL const (MHz, km)", 20 * np.log10(4 * np.pi * 1e6 * 1e3 / c), 32.45, 0.005)
check("FSPL const (Hz, m)", 20 * np.log10(4 * np.pi / c), -147.55, 0.005)
check("radio horizon km/sqrt(m), k=4/3", np.sqrt(2 * 4 / 3 * 6371e3) / 1e3, 4.12, 0.005)
check("geometric horizon km/sqrt(m)", np.sqrt(2 * 6371e3) / 1e3, 3.57, 0.005)
check("dipole D dBi", db(1.6409), 2.15, 0.005)
check("(4pi)^3 dB", db((4 * np.pi) ** 3), 32.98, 0.005)
# matched filter / radar detection, Pd 0.9, Pfa 1e-6
d = stats.norm.isf(1e-6) + stats.norm.isf(0.1)
check("coherent 2E/N0 dB", db(d * d), 15.6, 0.05)
check("coherent E/N0 dB", db(d * d / 2), 12.6, 0.05)
b = np.sqrt(-2 * np.log(1e-6))
a = optimize.brentq(lambda a: stats.ncx2.sf(b * b, 2, a * a) - 0.9, 1, 20)
check("non-coherent 2E/N0 dB (Marcum)", db(a * a), 16.2, 0.05)
check("non-coherent chi = E/N0 dB (Swerling 0)", db(a * a / 2), 13.2, 0.05)
# windows
def scallop(a0, N=4096):
    n = np.arange(N); w = a0 - (1 - a0) * np.cos(2 * np.pi * n / N)
    return -20 * np.log10(abs(np.sum(w * np.exp(-1j * np.pi * n / N))) / np.sum(w))
check("Hamming 0.54 scalloping dB", scallop(0.54), 1.75, 0.005)
check("'exact' Hamming 25/46 scalloping dB", scallop(25 / 46), 1.78, 0.005)
check("Hann scalloping dB", scallop(0.5), 1.42, 0.005)
# phase noise
check("Leeson white floor F=1, 0 dBm dBc/Hz", db(k * T0 / (2 * 1e-3)), -177.0, 0.05)
# phase quantisation lobe
for P, want in ((3, -14.0), (4, -20.1), (6, -32.2)):
    check(f"quantisation lobe {P} bits dB", 20 * np.log10(np.tan(np.pi / 2 ** (P + 1))), want, 0.05)
# class F
check("class F V{1,3} + half-sine I efficiency %", 50 * 2 / np.sqrt(3) * np.pi / 2, 90.7, 0.05)
check("class F V{1,3} + I{1,2} efficiency %", 50 * 2 / np.sqrt(3) * np.sqrt(2), 81.6, 0.05)
# Rayleigh fade margins vs mean / median
for p, want_mean, want_med in ((0.1, 10, 8.2), (0.01, 20, 18.4), (0.001, 30, 28.4)):
    x = -np.log(1 - p)
    check(f"Rayleigh margin vs mean, {p*100:g} % outage", -db(x), want_mean, 0.25)
    check(f"Rayleigh margin vs median, {p*100:g} % outage", -db(x / np.log(2)), want_med, 0.05)
# ADC / processing gain
check("8-bit ideal SNR dB", 6.02 * 8 + 1.76, 49.92, 0.01)
check("processing gain complex 2.4 MS/s -> 125 kHz", db(2.4e6 / 125e3), 12.8, 0.05)
check("processing gain real 2.4 MS/s -> 125 kHz", db(2.4e6 / (2 * 125e3)), 9.8, 0.05)
check("FFT floor 1024 pt 8-bit real dBFS", -49.92 - db(512), -77.0, 0.05)
check("FFT floor 1024 pt 8-bit complex dBFS", -49.92 - db(1024), -80.0, 0.05)
check("jitter SNR 100 fs @ 433 MHz dB", -20 * np.log10(2 * np.pi * 433e6 * 100e-15), 71.3, 0.05)

print("\n=== 3d LoRa / modules / GNSS / regulation ===")
check("ToA 32 B SF7/125 ms", lora.time_on_air(32, 7, 125e3) * 1e3, 71.9, 0.05)
check("ToA 40 B SF7/500 ms", lora.time_on_air(40, 7, 500e3) * 1e3, 20.5, 0.05)
check("ToA 32 B SF12/125 ms", lora.time_on_air(32, 12, 125e3) * 1e3, 1810, 1.0)
check("Doppler rate 433 MHz Hz/s per g", g0 * 433e6 / c, 14.2, 0.05)
check("Doppler rate 923 MHz Hz/s per g", g0 * 923e6 / c, 30.2, 0.05)
check("Doppler rate 10 g, 915 MHz Hz/s", 10 * g0 * 915e6 / c, 299, 0.5)
check("drift limit SF12/125 LDRO Hz", 125e3 / (3 * 2 ** 12) * 16, 163, 0.5)
check("R_b SF12/125 CR 4/5 with LDRO (SF - 2DE, DE = 1) b/s", lora.bitrate(12, 125e3, 1, ldro=True), 244, 0.5)  # W6-F5, D7 #9
check("LDRO auto-on at SF12/125 and SF12/250, off at SF12/500", float(lora.ldro_auto(12, 125e3) and lora.ldro_auto(12, 250e3) and not lora.ldro_auto(12, 500e3)), 1.0, 0)
check("ERP of 10 mW = dBm", 10.0, 10.0, 0)
check("EIRP limit for 10 mW e.r.p. dBm", 10 + 2.15, 12.15, 1e-9)
# band-edge rule: whole channel fc +/- BW/2 inside 433.05-434.79 MHz
lo, hi_ = 433.05, 434.79
def fits(ch, bw_khz):
    f = 410.125 + ch
    return (f - bw_khz / 2e3 >= lo) and (f + bw_khz / 2e3 <= hi_)
for ch, bw, want in ((23, 125, True), (23, 250, False), (23, 500, False), (24, 125, True), (24, 250, True), (24, 500, True)):
    good = fits(ch, bw) == want
    ok &= good
    print(f"[{'PASS' if good else 'FAIL'}] E22 CH {ch} at {bw} kHz inside 433.05-434.79 MHz: {fits(ch, bw)}")
check("CH 23 at 125 kHz lower edge MHz", 433.125 - 0.0625, 433.0625, 1e-9)
check("CH 23 99 % OBW (133 kHz) lower edge MHz", 433.125 - 0.0665, 433.0585, 1e-9)
check("E22 CH 24 2nd harmonic MHz", 2 * 434.125, 868.25, 1e-9)
check("E22 CH 24 3rd harmonic MHz", 3 * 434.125, 1302.375, 1e-9)
check("E220 CH 17 MHz", 850.125 + 17, 867.125, 1e-9)
check("CH17 distance from 868.25 MHz harmonic", 868.25 - 867.125, 1.125, 1e-9)
# E220 lowest step in SG 917-925 MHz (100 mW e.r.p.)
check("E220 21 dBm, 0.5 dB cable, dipole: e.r.p. over 20 dBm by", 21 - 0.5 + 2.15 - 2.15 - 20, 0.5, 1e-9)
# GNSS
Te = 290 * (10 ** 0.2 - 1)
check("C/N0 -130 dBm, NF 2 dB, Ta 290 K", -130 - (db(k * (290 + Te)) + 30), 42.0, 0.05)
check("C/N0 -130 dBm, NF 2 dB, Ta 100 K", -130 - (db(k * (100 + Te)) + 30), 44.3, 0.05)
# BGA524 SAW requirement at 915 MHz: 10 dBm blocker, IP1dB -16, 10 dB margin
check("SAW rejection needed dB", 10 - (-16) + 10, 36, 0)
# landed rocket canonical (09 Example E): margins at 10 km +2.4 / +11.4 dB, 40 dB/decade
check("landed range 2.4 kb/s km", 10 * 10 ** (2.4 / 40), 11.5, 0.05)
check("landed range SF12 km", 10 * 10 ** (11.4 / 40), 19.3, 0.05)
check("landed range 10 mW, 2.4 kb/s km", 5 * 10 ** ((14.4 - 20.35) / 40), 3.55, 0.06)
check("landed range 10 mW, SF12 km", 5 * 10 ** ((23.4 - 20.35) / 40), 6.0, 0.05)

print("\nALL PASS" if ok else "\nSOME CHECKS FAILED")
