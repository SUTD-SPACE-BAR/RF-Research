#!/usr/bin/env python3
"""
noise_dynamic_range.py — verification for kb/07-noise-linearity/dynamic-range-sfdr-blocking.md

1. SFDR = 2/3 (IIP3 - N_in) derivation check: find the input level where input-referred IM3 equals the
   noise floor, numerically, and compare with the closed form. Second-order SFDR = 1/2 (IIP2 - N).
2. ADC: ideal SNR 6.02N + 1.76 dB, processing gain 10log(fs/(2B)), ADC noise figure
   NF = P_FS(dBm) - SNR - 10 log10(fs/2) + 174 (MT-052 method), and the front-end gain needed so the
   ADC adds < 0.5 dB to the system NF.
3. Desensitisation budget: gain compression + reciprocal mixing + (optional) blocker-induced noise,
   combined into an effective sensitivity loss.
4. Co-sited transmitter blocking example at a ground station (RTK-correction or second-link transmitter).
5. Selectivity: how much filter rejection is needed to keep a blocker below the chain's input P1dB - 10 dB.
"""
import numpy as np
from scipy.optimize import brentq
kT0 = -173.975

print("=== 1. SFDR ===")
for iip3, nf, B in ((-5.0, 6.0, 125e3), (-18.9, 2.55, 125e3), (10.0, 3.0, 1e6), (-43.3, 1.2, 2e6)):
    N = kT0 + nf + 10*np.log10(B)
    P = brentq(lambda p: (3*p - 2*iip3) - N, -200, 50)
    sfdr_num = P - N
    print(f"  IIP3 {iip3:6.1f} dBm, NF {nf} dB, B {B/1e3:6.0f} kHz: N = {N:7.1f} dBm; SFDR numeric {sfdr_num:5.1f} dB, "
          f"2/3(IIP3-N) = {2/3*(iip3-N):5.1f} dB; input level at SFDR edge {P:6.1f} dBm")
for iip2 in (20.0, 40.0, 60.0):
    N = kT0 + 6 + 10*np.log10(125e3)
    print(f"  IIP2 {iip2:.0f} dBm, N {N:.1f} dBm: second-order SFDR = 1/2(IIP2 - N) = {0.5*(iip2-N):.1f} dB")
for p1, nf, B in ((-15.0, 6.0, 125e3), (-28.9, 2.55, 125e3)):
    N = kT0 + nf + 10*np.log10(B)
    print(f"  compression-limited DR: IP1dB {p1} dBm - N {N:.1f} dBm = {p1 - N:.1f} dB")

print("\n=== 2. ADC dynamic range and noise figure ===")
def adc_nf(pfs_dbm, snr_db, fs):
    return pfs_dbm - snr_db - 10*np.log10(fs/2) + 174
for bits, snr, fs, pfs in ((8, 45.0, 2.4e6, 0.0), (12, 65.0, 61.44e6, 4.0), (14, 74.0, 100e6, 10.0), (16, 78.0, 125e6, 10.0)):
    nf = adc_nf(pfs, snr, fs)
    print(f"  {bits:2d}-bit class, SNR {snr} dB, fs {fs/1e6:6.2f} MS/s, full scale {pfs:+.0f} dBm: ADC NF = {nf:5.1f} dB; "
          f"ideal SNR {6.02*bits+1.76:5.1f} dB")
# processing gain
for fs, B in ((100e6, 125e3), (2.4e6, 125e3), (61.44e6, 1e6)):
    print(f"  processing gain fs={fs/1e6:.2f} MS/s -> B={B/1e3:.0f} kHz: 10log(fs/2B) = {10*np.log10(fs/(2*B)):.1f} dB")
# gain needed ahead of ADC for < 0.5 dB degradation, given front-end NF 2 dB
NF_fe = 2.0; F_fe = 10**(NF_fe/10)
for nf_adc in (25.0, 33.0, 40.0):
    F_adc = 10**(nf_adc/10)
    G = brentq(lambda g: 10*np.log10(F_fe + (F_adc - 1)/10**(g/10)) - (NF_fe + 0.5), 0, 100)
    print(f"  ADC NF {nf_adc} dB behind a 2 dB front end: need >= {G:.1f} dB of gain for <= 0.5 dB NF penalty")

print("\n=== 3. Desensitisation budget ===")
def desense(N_thermal, extra_list):
    tot = 10*np.log10(10**(N_thermal/10) + sum(10**(x/10) for x in extra_list))
    return tot - N_thermal
N = kT0 + 6 + 10*np.log10(125e3)
Pb, L = -44.0, -122.0
rm = Pb + L + 10*np.log10(125e3)
gain_drop = 0.5    # dB of small-signal gain compression by the blocker (raises input-referred noise of later stages)
print(f"  thermal floor {N:.1f} dBm; reciprocal-mixing noise {rm:.1f} dBm -> desense {desense(N, [rm]):.2f} dB "
      f"(+ ~{gain_drop} dB from compression if later-stage noise dominates) ")

print("\n=== 4. Co-sited transmitter at a ground station ===")
for Ptx, iso, lab in ((30.0, 30.0, "1 W, antennas 2-3 m apart, same band (isolation ~30 dB, assumption)"),
                      (30.0, 50.0, "1 W, well separated + cross-pol (isolation ~50 dB, assumption)"),
                      (30.0, 30.0 + 40.0, "1 W, 30 dB isolation + 40 dB cavity/SAW rejection (different band)")):
    Pb = Ptx - iso
    for p1_in in (-28.9, -15.0):
        verdict = "COMPRESSED/BLOCKED" if Pb > p1_in - 10 else "ok (>=10 dB below IP1dB)"
        print(f"  {lab:70s}: blocker {Pb:6.1f} dBm vs chain IP1dB {p1_in:6.1f} dBm -> {verdict}")

print("\n=== 5. Required pre-selection ===")
for Pb in (-5.0, -20.0, -40.0):
    for p1_in in (-28.9, -15.0):
        need = Pb - (p1_in - 10)
        print(f"  blocker {Pb:6.1f} dBm at antenna, chain IP1dB {p1_in:6.1f} dBm: filter rejection needed >= {max(need,0):5.1f} dB")
