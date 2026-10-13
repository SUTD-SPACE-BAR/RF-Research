#!/usr/bin/env python3
"""Calculations for kb/11-radar/diy-radar-hardware.md

Run:  python3 tools/verify/radar_diy.py      (~1 s)

Computes / checks:
  1. SDR monostatic (two-antenna) budget at 2.4 GHz: echo vs TX leakage vs ADC dynamic range;
     range resolution for SDR bandwidths (20 MHz Pluto AD9363, 56 MHz AD9361/B210).
  2. Stepped-frequency bandwidth synthesis: N LO steps x 20 MHz -> synthetic bandwidth, resolution.
  3. Passive radar (FM / DVB-T): echo-to-direct-path ratio sigma Lb^2/(4 pi Rt^2 Rr^2), CAF processing
     gain B*T, required direct-path cancellation; bistatic range-sum resolution c/B.
  4. Rocket-tracking geometry: elevation angular rate for a vertical climb seen from a radar at
     horizontal offset d; radial velocity fraction; beam-crossing times.
  5. Regulatory conversions (Singapore IMDA TS SRD 2023): field strength at 10 m <-> EIRP.
  6. Radar altimeter / ground return by image theory: P_r ~ 1/(2h)^2 (flat ground) vs 1/R^4.
"""
import numpy as np

c = 299_792_458.0
k = 1.380649e-23
ok_all = True


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel else 1.0)
    ok = err <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol}{' rel' if rel else ''})")
    return ok


db = lambda x: 10 * np.log10(x)
dbm = lambda w: 10 * np.log10(w * 1000)

print("=" * 78)
print("1. SDR monostatic budget (2.4 GHz, two antennas)")
f = 2.44e9
lam = c / f
Pt_dbm = 5.0         # assumed SDR TX output after a small driver
G = 10.0             # dBi each (assumed small panel/patch)
iso = 40.0           # dB TX->RX isolation with separate antennas (assumed)
leak_dbm = Pt_dbm - iso
for R, sig, lab in ((20.0, 0.5, "person"), (50.0, 10.0, "car"), (100.0, 0.01, "drone")):
    Pr = 10 ** (Pt_dbm / 10) / 1000 * 10 ** (2 * G / 10) * lam ** 2 * sig / ((4 * np.pi) ** 3 * R ** 4)
    print(f"    {lab:6s} sigma {sig} m^2 at {R:5.0f} m: echo {dbm(Pr):6.1f} dBm; leakage {leak_dbm:.0f} dBm -> echo {dbm(Pr)-leak_dbm:6.1f} dB below leakage")
adc_bits = 12
print(f"    ideal {adc_bits}-bit ADC SNR over Nyquist: {6.02*adc_bits+1.76:.1f} dB (leakage sets the gain; FFT processing gain adds 10log10(N))")
check("12-bit ideal SQNR", 6.02 * 12 + 1.76, 74.0, 0.1)
for B, lab in ((20e6, "Pluto AD9363 (20 MHz)"), (56e6, "AD9361/B210 (56 MHz)")):
    print(f"    {lab}: range resolution c/2B = {c/(2*B):.2f} m")

print("=" * 78)
print("2. Stepped-frequency synthesis")
for nstep in (10, 50):
    Bsyn = nstep * 20e6
    print(f"    {nstep} steps x 20 MHz = {Bsyn/1e6:.0f} MHz -> {c/(2*Bsyn)*100:.0f} cm; unambiguous range with 20 MHz step = c/(2 df) = {c/(2*20e6):.1f} m per step spacing")
check("stepped 50 x 20 MHz resolution (cm)", c / (2 * 1e9) * 100, 14.99, 0.02)

print("=" * 78)
print("3. Passive radar: direct path vs echo")
for (name, fcent, Bw, T) in (("FM 98 MHz", 98e6, 150e3, 1.0), ("DVB-T 600 MHz", 600e6, 7.6e6, 0.1)):
    Lb, Rt, Rr, sig = 20e3, 20e3, 10e3, 10.0
    ratio = sig * Lb ** 2 / (4 * np.pi * Rt ** 2 * Rr ** 2)
    gain = Bw * T
    print(f"    {name}: echo/direct = {db(ratio):.1f} dB (sigma {sig} m^2, Lb {Lb/1e3:.0f} km, Rt {Rt/1e3:.0f} km, Rr {Rr/1e3:.0f} km); "
          f"CAF gain BT = {db(gain):.1f} dB -> direct-path CAF pedestal ~ -{db(gain):.1f} dB; echo sits {(-db(ratio)) - db(gain):.1f} dB below it: "
          f"cancel the direct path by > {(-db(ratio)) - db(gain) + 10:.0f} dB (10 dB margin)")
    print(f"      bistatic range-sum resolution c/B = {c/Bw:.0f} m; Doppler resolution 1/T = {1/T:.0f} Hz -> {c/fcent/T:.2f} m/s of bistatic range rate")
ratio = 10 * 20e3 ** 2 / (4 * np.pi * 20e3 ** 2 * 10e3 ** 2)
check("echo/direct ratio sigma Lb^2/(4 pi Rt^2 Rr^2) (dB)", db(ratio), -81.0, 0.05)

print("=" * 78)
print("4. Rocket-tracking geometry (vertical climb, radar at horizontal offset d)")
for d in (50.0, 500.0, 2000.0):
    for v in (100.0, 250.0):
        # elevation theta = atan(h/d): dtheta/dt = v d / (d^2 + h^2); max at h = 0
        rate_max = np.degrees(v / d)
        h_at = 1000.0
        rate_1k = np.degrees(v * d / (d ** 2 + h_at ** 2))
        vr_frac = h_at / np.hypot(d, h_at)
        print(f"    d = {d:6.0f} m, v = {v:5.0f} m/s: max elevation rate {rate_max:7.1f} deg/s (near pad); at h = 1 km {rate_1k:6.2f} deg/s, radial = {vr_frac*100:5.1f} % of v")
check("elevation rate max v/d (d=500, v=250) deg/s", np.degrees(250 / 500), 28.65, 0.01)
bw = 5.8
print(f"    a {bw} deg beam at 28.6 deg/s is crossed in {bw/28.65:.2f} s -> needs a slewing mount or a wide beam near the pad")

print("=" * 78)
print("5. Regulatory conversions")
for dbuv in (117.0,):
    E = 10 ** (dbuv / 20) * 1e-6
    eirp = (E * 10) ** 2 / 30
    print(f"    {dbuv} dBuV/m at 10 m = {E:.3f} V/m -> EIRP {dbm(eirp):.1f} dBm")
check("117 dBuV/m @10 m -> 32.2 dBm EIRP", dbm((10 ** (117 / 20) * 1e-6 * 10) ** 2 / 30), 32.2, 0.05)
print(f"    100 mW EIRP (24.00-24.25 / 57-64 GHz) = 20 dBm; field at 10 m = {20*np.log10(np.sqrt(30*0.1)/10*1e6):.1f} dBuV/m")

print("=" * 78)
print("6. Ground return (radar altimeter) by image theory")
# flat perfectly reflecting ground at height h: image antenna at distance 2h -> Friis over 2h
Pt, Gr = 1e-3, 10 ** 1.0
lam60 = c / 60.5e9
for h in (2.0, 10.0, 20.0):
    Pr = Pt * Gr * Gr * lam60 ** 2 / ((4 * np.pi * 2 * h) ** 2)
    print(f"    60 GHz, 0 dBm, 10 dBi, |Gamma|=1: h = {h:4.0f} m -> P_r = {dbm(Pr):6.1f} dBm (x |Gamma|^2 for real ground; scales as 1/h^2, not 1/h^4)")
check("image-theory ground return 6 dB per doubling of height", db((1 / (2 * 2.0) ** 2) / (1 / (2 * 4.0) ** 2)), 6.02, 0.01)

print("=" * 78)
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
