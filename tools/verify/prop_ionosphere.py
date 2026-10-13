#!/usr/bin/env python3
"""
prop_ionosphere.py — verification for kb/09-propagation-link-budget/ionospheric-hf-propagation.md

1. Plasma frequency f_p = sqrt(Ne e^2/(eps0 m_e))/(2 pi) ~ 8.98 sqrt(Ne) Hz; refractive index n^2 = 1 - (fp/f)^2.
2. Secant law and MUF (flat-earth, virtual height), skip distance, NVIS frequency window.
3. Curved-earth single-hop geometry: maximum one-hop ground range for a reflection height h.
4. Group delay / range error 40.3 TEC/f^2 (from ITU-R P.531 eq. 4: 1.345e-7 NT/f^2 s) at GNSS L1/L2/L5 and
   at 433/915 MHz; dual-frequency ionosphere-free combination.
5. Faraday rotation Omega = 2.36e4 B_av N_T / f^2 (rad; f Hz) (P.531 eq. 2 with f in GHz: 2.36e-14 ... /f_GHz^2)
   and the XPD it causes, for Earth-space paths; note that a rocket below ~60 km never enters the ionosphere.
6. Scintillation S4 frequency scaling f^-1.5 (P.531, weak/moderate regime).
"""
import numpy as np
e = 1.602176634e-19; me = 9.1093837015e-31; eps0 = 8.8541878128e-12; c = 299792458.0

print("=== 1. Plasma frequency ===")
k = np.sqrt(e**2/(eps0*me))/(2*np.pi)
print(f"  f_p = {k:.4f} sqrt(Ne) Hz")
for Ne in (1e9, 1e10, 1e11, 1e12, 3e12):
    print(f"  Ne = {Ne:.0e} m^-3: f_p = {k*np.sqrt(Ne)/1e6:6.2f} MHz")
for fo in (5e6, 8e6, 12e6):
    print(f"  foF2 = {fo/1e6:.0f} MHz -> NmF2 = {(fo/k)**2:.2e} m^-3")
for f in (3e6, 10e6, 30e6, 433e6):
    n2 = 1 - (8e6/f)**2
    print(f"  f={f/1e6:6.0f} MHz in a layer with f_p=8 MHz: n^2 = {n2:+.4f} ({'reflects at vertical incidence' if n2 < 0 else 'passes'})")

print("\n=== 2. Secant law, skip distance, NVIS ===")
h = 300e3   # virtual height F2
for fo in (5e6, 8e6, 12e6):
    for D in (100e3, 500e3, 1000e3, 2000e3):
        th = np.arctan((D/2)/h)       # incidence angle from vertical (flat earth)
        muf = fo/np.cos(th)
        print(f"  foF2={fo/1e6:4.1f} MHz, path {D/1e3:5.0f} km (flat, h'=300 km): MUF = {muf/1e6:5.1f} MHz, "
              f"FOT ~0.85 MUF = {0.85*muf/1e6:5.1f} MHz")
for fo, f in ((8e6, 14e6), (8e6, 21e6), (12e6, 28e6)):
    skip = 2*h*np.sqrt((f/fo)**2 - 1)
    print(f"  f={f/1e6:.0f} MHz, foF2={fo/1e6:.0f} MHz: skip distance ~ {skip/1e3:.0f} km (flat earth)")
print("  NVIS: use f below foF2 (typ. 2-10 MHz, often 0.8-0.9 foF2) with antennas radiating near zenith;"
      " covers 0-~400 km with no skip zone.")

print("\n=== 3. Curved-earth single hop ===")
Re = 6371e3
for hh in (110e3, 300e3, 400e3):
    # grazing take-off (0 deg elevation) maximum range
    phi = np.arccos(Re/(Re + hh))
    print(f"  reflection height {hh/1e3:.0f} km: max one-hop ground range (0 deg take-off) = {2*phi*Re/1e3:.0f} km")
# obliquity factor for a 3000 km path via a 300 km mirror (Tx at central angle -phi, mirror above midpoint)
for D in (1000e3, 2000e3, 3000e3):
    hh = 300e3
    phi = D/(2*Re)
    v = np.array([Re*np.sin(phi), (Re + hh) - Re*np.cos(phi)])          # Tx -> mirror
    up_tx = np.array([-np.sin(phi), np.cos(phi)])
    el = np.degrees(np.arcsin(np.dot(v, up_tx)/np.linalg.norm(v)))
    sec_i = np.linalg.norm(v)/v[1]                                       # vertical at the mirror is (0,1)
    print(f"  {D/1e3:5.0f} km hop via 300 km mirror: take-off elevation {el:5.1f} deg, sec(i) = {sec_i:.2f} "
          f"(MUF = foF2 * sec i; cf. M(3000)F2 ~ 3)")

print("\n=== 4. Ionospheric group delay (range error) ===")
for name, f in (("GPS L1", 1575.42e6), ("GPS L2", 1227.60e6), ("GPS L5", 1176.45e6), ("433 MHz", 433.125e6), ("915 MHz", 915e6)):
    per_tecu = 40.3*1e16/f**2
    print(f"  {name:8s}: {per_tecu:7.3f} m per TECU; 10 TECU -> {10*per_tecu:6.2f} m; 100 TECU -> {100*per_tecu:6.1f} m "
          f"(P.531 form 1.345e-7*1e16/f^2*c = {1.345e-7*1e16/f**2*c:.3f} m/TECU)")
f1, f2 = 1575.42e6, 1227.60e6
a1 = f1**2/(f1**2 - f2**2); a2 = -f2**2/(f1**2 - f2**2)
print(f"  Iono-free L1/L2: P_IF = {a1:.4f} P1 {a2:+.4f} P2; noise amplification sqrt(a1^2 + a2^2) = {np.hypot(a1, a2):.2f}")
# check it removes 40.3 TEC/f^2
TEC = 50e16
I1 = 40.3*TEC/f1**2; I2 = 40.3*TEC/f2**2
print(f"  check: residual iono in P_IF for TEC=50 TECU: {a1*I1 + a2*I2:.2e} m (should be 0)")

print("\n=== 5. Faraday rotation (Earth-space) ===")
for B in (3e-5, 5e-5):
    for TEC in (1e17, 1e18):
        for f in (145.9e6, 433.125e6, 915e6, 1575.42e6):
            om = 2.36e4*B*TEC/f**2
            xpd = -20*np.log10(abs(np.tan(om))) if abs(np.tan(om)) > 1e-9 else np.inf
            print(f"  B_L={B*1e5:.0f}e-5 T, TEC={TEC:.0e}: f={f/1e6:7.1f} MHz -> Omega = {np.degrees(om):9.1f} deg "
                  f"({np.degrees(om) % 180:6.1f} mod 180), XPD(aligned linear) = {xpd:5.1f} dB")
slant = 1/np.cos(np.arcsin(Re*np.cos(np.radians(30))/(Re + 350e3)))   # thin-shell mapping at 350 km, 30 deg elevation
print(f"  P.531 Table 3 check: 1 GHz, vertical TEC 1e18, 30 deg elevation (slant factor {slant:.2f}) -> 108 deg quoted;"
      f" needs B_L = {np.radians(108)/(2.36e4*slant*1e18/1e9**2)*1e5:.1f}e-5 T (plausible mid-latitude value)")
print("  NOTE: the D region starts ~60 km; a rocket at <= 50 km altitude and its ground station are both below the")
print("  ionosphere, so the telemetry path has no Faraday rotation or ionospheric delay. GNSS signals do.")

print("\n=== 6. Scintillation scaling S4 ~ f^-1.5 ===")
for S4_1 in (0.2, 0.5):
    for f in (250e6, 433e6, 1575.42e6):
        print(f"  S4={S4_1} at 1575.42 MHz -> S4 at {f/1e6:7.1f} MHz = {S4_1*(1575.42e6/f)**1.5:.2f} (saturates near 1)")
