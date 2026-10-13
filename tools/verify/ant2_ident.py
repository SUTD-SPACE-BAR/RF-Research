#!/usr/bin/env python3
"""ant2_ident.py -- numbers for kb/08-antennas/antenna-identification-guide.md (W5-E2).

1. Quarter-wave / half-wave element lengths for common bands (free-space lambda/4 and the ~0.95 practical
   factor for thin elements) and the inverse rule f[MHz] ~ 71.2 / L_quarter[m] = 142.5 / L_half[m].
2. Mismatch loss for the SWR values reported for stock antennas (myembeddedstuff.com 2026 table).
3. Collinear / stacked omni rule: D ~ 2L/lambda, elevation HPBW ~ 50.8 lambda / L (uniform line source).
4. Dish gain at 0.6 aperture efficiency for common sizes.
Run: python3 tools/verify/ant2_ident.py
"""
import numpy as np

C0 = 299792458.0
bands = [("CB 27 MHz", 27.185), ("6 m ham", 50.5), ("FM broadcast", 98.0), ("airband", 127.0),
         ("NOAA APT / 2 m", 137.5), ("2 m ham", 146.0), ("marine VHF", 158.0), ("315 MHz SRD", 315.0),
         ("433 MHz ISM/70 cm", 433.0), ("446 MHz PMR", 446.1), ("UHF TV (centre)", 600.0), ("868 MHz SRD", 868.0),
         ("915 MHz ISM", 915.0), ("ADS-B 1090", 1090.0), ("GNSS L1", 1575.42), ("cellular 1.8-2.1 GHz", 1950.0),
         ("2.4 GHz ISM", 2450.0), ("3.5 GHz 5G", 3500.0), ("5.8 GHz ISM", 5800.0)]
print("=== 1. Element lengths ===")
print(f"  {'band':22s} {'f (MHz)':>8s} {'lambda/4 (mm)':>14s} {'0.95 x lambda/4':>16s} {'lambda/2 (mm)':>14s}")
for name, f in bands:
    q = C0 / (f * 1e6) / 4 * 1e3
    print(f"  {name:22s} {f:8.1f} {q:14.0f} {0.95*q:16.0f} {2*q:14.0f}")
print(f"  inverse rule: f(MHz) = 0.95 * 299.79/(4 L) = {0.95*299.792458/4:.1f}/L_quarter(m) = "
      f"{0.95*299.792458/2:.1f}/L_half(m)")

print("\n=== 2. Mismatch loss of reported stock-antenna SWRs ===")
for s in (1.2, 1.3, 1.5, 2.0, 2.02, 2.9, 3.3, 4.0, 6.0, 10.0):
    G = (s - 1) / (s + 1)
    print(f"  SWR {s:4.2f}: |Gamma| = {G:.3f}, mismatch loss = {-10*np.log10(1-G*G):.2f} dB, return loss = {-20*np.log10(G):.1f} dB")

print("\n=== 3. Collinear omni: gain and elevation beamwidth vs radiating length ===")
for Ll in (0.5, 1.0, 2.0, 3.0, 4.0, 6.0):
    D = 2 * Ll if Ll >= 1 else 1.64
    hp = 50.8 / Ll if Ll >= 1 else 78.0
    print(f"  L = {Ll:3.1f} lambda: D ~ {10*np.log10(D):4.1f} dBi, elevation HPBW ~ {hp:4.0f} deg "
          f"(915 MHz: L = {Ll*C0/915e6*1e3:.0f} mm; 433 MHz: {Ll*C0/433e6*1e3:.0f} mm)")

print("\n=== 4. Dish gain (e_ap 0.6) ===")
for D, f in ((0.6, 11.7e9), (0.9, 11.7e9), (1.2, 1.7e9), (0.45, 5.8e9), (1.0, 2.45e9)):
    lam = C0 / f
    G = 0.6 * (np.pi * D / lam) ** 2
    print(f"  D = {D} m at {f/1e9:.2f} GHz: G = {10*np.log10(G):.1f} dBi, HPBW ~ {70*lam/D:.1f} deg")
