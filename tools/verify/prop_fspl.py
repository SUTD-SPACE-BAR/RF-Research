#!/usr/bin/env python3
"""
prop_fspl.py — verification for kb/09-propagation-link-budget/friis-free-space-path-loss.md

1. Friis transmission equation from effective aperture: Pr/Pt = Gt Gr (lambda/(4 pi d))^2, with
   Ae = G lambda^2/(4 pi); FSPL (isotropic) = (4 pi d/lambda)^2.
2. dB constants: 32.45 (d km, f MHz), 92.45 (d km, f GHz), -147.55 (d m, f Hz), 27.55 (d m, f MHz).
3. "Does free space attenuate high frequencies more?" — no. Three cases for going 433 -> 915 MHz:
   (a) isotropic/fixed-gain antennas both ends: received power falls 20log(f2/f1)
   (b) fixed physical aperture at Rx, isotropic Tx: received power unchanged
   (c) fixed apertures both ends: received power RISES 20log(f2/f1)
4. Power flux density and field strength at the receiver: S = EIRP/(4 pi d^2), E = sqrt(30 EIRP)/d.
5. EIRP vs ERP (ERP = EIRP - 2.15 dB).
6. Far-field distance check 2D^2/lambda for the Friis formula to apply.
7. Sanity check vs the 832 km LoRaWAN balloon record (14 dBm, 868 MHz).
"""
import numpy as np
c = 299792458.0

def fspl_db(f_hz, d_m):
    return 20*np.log10(4*np.pi*d_m*f_hz/c)

print("=== 2. dB constants ===")
print(f"  d km, f MHz : {20*np.log10(4*np.pi*1e3*1e6/c):.4f}")
print(f"  d km, f GHz : {20*np.log10(4*np.pi*1e3*1e9/c):.4f}")
print(f"  d m,  f Hz  : {20*np.log10(4*np.pi/c):.4f}")
print(f"  d m,  f MHz : {20*np.log10(4*np.pi*1e6/c):.4f}")
print(f"  d mi, f MHz : {20*np.log10(4*np.pi*1609.344*1e6/c):.4f}")

print("\n=== FSPL table (dB) ===")
fs = [433.125e6, 868e6, 915e6, 1575.42e6, 2.45e9, 5.8e9, 24e9, 77e9]
ds = [0.1e3, 1e3, 5e3, 10e3, 30e3, 50e3, 100e3]
print("  d(km)  " + "".join(f"{f/1e6:>10.1f}" for f in fs))
for d in ds:
    print(f"  {d/1e3:6.1f} " + "".join(f"{fspl_db(f, d):10.1f}" for f in fs))

print("\n=== 3. Frequency dependence is an aperture effect ===")
f1, f2, d = 433e6, 915e6, 30e3
lam1, lam2 = c/f1, c/f2
Pt = 1.0
# (a) isotropic both ends
pa1 = Pt*(lam1/(4*np.pi*d))**2; pa2 = Pt*(lam2/(4*np.pi*d))**2
# (b) isotropic Tx, fixed Rx aperture 0.5 m^2
Ae = 0.5
pb1 = Pt/(4*np.pi*d**2)*Ae; pb2 = pb1
# (c) fixed aperture both ends: Pr = Pt At Ar/(lambda^2 d^2)
At = 0.1
pc1 = Pt*At*Ae/(lam1**2*d**2); pc2 = Pt*At*Ae/(lam2**2*d**2)
print(f"  (a) isotropic both ends         : 915 vs 433 MHz = {10*np.log10(pa2/pa1):+.2f} dB")
print(f"  (b) iso Tx, fixed 0.5 m^2 Rx     : {10*np.log10(pb2/pb1):+.2f} dB (power flux density is frequency-independent)")
print(f"  (c) fixed apertures both ends    : {10*np.log10(pc2/pc1):+.2f} dB")
print(f"  Gain of a 0.5 m^2 aperture: {10*np.log10(4*np.pi*Ae/lam1**2):.1f} dBi at 433 MHz, {10*np.log10(4*np.pi*Ae/lam2**2):.1f} dBi at 915 MHz")
print(f"  Isotropic effective aperture: {lam1**2/(4*np.pi)*1e4:.0f} cm^2 at 433 MHz, {lam2**2/(4*np.pi)*1e4:.0f} cm^2 at 915 MHz, "
      f"{(c/1575.42e6)**2/(4*np.pi)*1e4:.1f} cm^2 at GPS L1")

print("\n=== 4. Flux density and field strength ===")
for eirp_dbm, d in ((33.0, 30e3), (30.0, 30e3), (14.0, 832e3)):
    eirp = 1e-3*10**(eirp_dbm/10)
    S = eirp/(4*np.pi*d**2)
    E = np.sqrt(30*eirp)/d
    print(f"  EIRP {eirp_dbm} dBm at {d/1e3:.0f} km: S = {10*np.log10(S/1e-3):.1f} dBm/m^2, "
          f"E = {20*np.log10(E/1e-6):.1f} dBuV/m (check eta0*S: {20*np.log10(np.sqrt(S*376.73)/1e-6):.1f})")

print("\n=== 5. EIRP vs ERP ===")
print(f"  ERP = EIRP - 10log10(1.641) = EIRP - {10*np.log10(1.6409):.2f} dB (half-wave dipole gain 2.15 dBi)")

print("\n=== 6. Far-field (Fraunhofer) distance 2 D^2 / lambda ===")
for name, D, f in (("433 MHz 10-el Yagi boom 2.5 m", 2.5, 433e6), ("915 MHz Yagi 1.2 m", 1.2, 915e6),
                   ("1.2 m dish at 10 GHz", 1.2, 10e9)):
    print(f"  {name:32s}: 2D^2/lambda = {2*D**2/(c/f):7.1f} m")

print("\n=== 7. Sanity check: 832 km LoRaWAN balloon record (14 dBm, 868 MHz) ===")
L = fspl_db(868e6, 832e3)
for Gr in (2.0, 5.0, 8.0):
    Pr = 14.0 + 0.0 + Gr - L
    print(f"  FSPL={L:.1f} dB; Gt=0 dBi, Gr={Gr} dBi -> Pr = {Pr:.1f} dBm vs SF12/BW125 sensitivity ~ -137 dBm "
          f"(margin {Pr+137:+.1f} dB)")
print("  -> a free-space budget predicts the record is just possible; consistent with LOS from 38 km altitude.")

print("\n=== 8. Field-strength constant check ===")
for eirp_dbm, d_km in ((33.0, 30.0), (30.0, 0.003)):
    E_formula = eirp_dbm - 20*np.log10(d_km) + 44.77
    E_direct = 20*np.log10(np.sqrt(30*1e-3*10**(eirp_dbm/10))/(d_km*1e3)/1e-6)
    print(f"  EIRP {eirp_dbm} dBm at {d_km} km: formula (+44.77) {E_formula:.2f} dBuV/m, direct sqrt(30P)/d {E_direct:.2f} dBuV/m")
