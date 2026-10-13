#!/usr/bin/env python3
"""
array_diy.py — numbers for kb/12-phased-arrays/diy-phased-array-projects.md

  1. Aperture / element count / panel size needed for a target gain at 433, 915, 2440, 5800, 10250 MHz
     (square lambda/2 lattice, Hannan cell gain, aperture efficiency e_ap).
  2. Rocket telemetry link budgets (free space) for the Space Bar radios and for a 5.8 GHz video link:
     received power vs range with a fixed Yagi / phased array; margin vs LoRa sensitivity.
  3. Tracking kinematics: angular rate of a rocket seen from a ground station (vertical ascent at offset D),
     vs beamwidths of candidate antennas -> required steering/slew rates.
  4. DF geometry: bearing error -> cross-range error; two-station triangulation for recovery.
  5. Two-element interferometer: phase difference vs angle, ambiguity for d = lambda/2 vs d = lambda,
     and the effect of a 10° calibration error.
"""
import numpy as np

c0 = 299792458.0

print("=" * 78)
print("1. Aperture needed for a target gain (square λ/2 lattice, cos-like embedded elements)")
for f in (433e6, 915e6, 2.44e9, 5.8e9, 10.25e9):
    lam = c0 / f
    row = []
    for G_dbi in (10, 15, 20, 25):
        e_ap = 0.6  # element + feed losses on FR-4 class hardware (assumption, see page)
        A = 10 ** (G_dbi / 10) * lam ** 2 / (4 * np.pi * e_ap)
        n = A / (lam / 2) ** 2
        side = np.sqrt(A)
        row.append(f"{G_dbi} dBi: {int(np.ceil(n)):4d} el, {side*100:6.1f} cm sq")
    print(f"  {f/1e6:7.0f} MHz (λ/2 = {lam/2*100:5.1f} cm): " + " | ".join(row))

print("=" * 78)
print("2. Link budgets (free space, polarisation-matched, no fading margin)")


def fspl(d, f):
    return 20 * np.log10(4 * np.pi * d * f / c0)


cases = [
    ("433 MHz LoRa, E22-400T33D 2 W (33 dBm), 0 dBi rocket ant", 433e6, 33.0, 0.0, [2.15, 12.0, 14.2], -129.0),
    ("915 MHz LoRa, E220-900T30D 1 W (30 dBm), 0 dBi rocket ant", 915e6, 30.0, 0.0, [2.15, 12.0, 14.3], -129.0),
    ("2.44 GHz 100 mW (20 dBm), 0 dBi", 2.44e9, 20.0, 0.0, [2.15, 14.0, 20.0], -100.0),
    ("5.8 GHz video 25 dBm, 2 dBi", 5.8e9, 25.0, 2.0, [2.15, 14.0, 20.0, 23.0], -90.0),
]
for name, f, ptx, gtx, grx_list, sens in cases:
    print(f"  {name}; Rx sensitivity used {sens} dBm")
    for d_km in (5, 10, 30, 50):
        L = fspl(d_km * 1e3, f)
        row = [f"{g:4.1f} dBi → {ptx+gtx-L+g:7.1f} dBm (margin {ptx+gtx-L+g-sens:5.1f} dB)" for g in grx_list]
        print(f"    {d_km:3d} km (FSPL {L:6.1f} dB): " + " | ".join(row))

print("=" * 78)
print("3. Tracking kinematics: rocket rising vertically at speed v, ground station at horizontal offset D")
for D in (0.5e3, 2e3, 5e3):
    for v in (100, 300, 600):
        # elevation angle el = atan(h/D), d(el)/dt = v D/(D^2+h^2); max at h=0
        rate_max = np.degrees(v / D)
        h = np.array([0, 1e3, 3e3, 10e3])
        rates = np.degrees(v * D / (D ** 2 + h ** 2))
        print(f"  D={D/1e3:3.1f} km, v={v:3d} m/s: max elevation rate {rate_max:6.2f}°/s (at h=0); at h=1/3/10 km: "
              + ", ".join(f"{r:5.2f}" for r in rates[1:]) + " °/s")
beams = {"433 MHz 11-el Yagi (≈14 dBi)": 30.0, "8×8 5.8 GHz panel": 12.7, "4×4 2.44 GHz panel": 25.4}
print("  approximate beamwidths (°): " + "; ".join(f"{k}: {v}" for k, v in beams.items()))
print("  time for the target to cross half a 12.7° beam at 5°/s: %.2f s" % (12.7 / 2 / 5))

print("=" * 78)
print("4. DF bearing error → cross-range error")
for bearing_err in (0.5, 1.0, 3.0, 5.0):
    for R in (1e3, 5e3, 20e3):
        print(f"  σ_bearing {bearing_err:3.1f}° at {R/1e3:4.1f} km → cross-range {R*np.radians(bearing_err):7.1f} m")
# two-station triangulation, stations 2 km apart, target 5 km away broadside
B = 2e3
Rt = 5e3
ang = np.arctan2(Rt, B / 2)
for be in (1.0, 3.0):
    # position error scale ≈ R σθ / sin(intersection angle)
    inter = np.pi - 2 * ang
    print(f"  two stations {B/1e3:.0f} km apart, target {Rt/1e3:.0f} km out: intersection angle {np.degrees(inter):.1f}°, "
          f"position error ≈ {Rt*np.radians(be)/np.sin(inter):.0f} m for {be}° bearings")

print("=" * 78)
print("5. Two-element interferometer (2.44 GHz): phase difference Δφ = k d sinθ")
f = 2.44e9
lam = c0 / f
for d_l in (0.5, 1.0):
    th = np.radians(np.array([-60, -30, 0, 30, 60]))
    dphi = np.degrees(2 * np.pi * d_l * np.sin(th))
    wrapped = (dphi + 180) % 360 - 180
    print(f"  d = {d_l}λ ({d_l*lam*100:.2f} cm): Δφ at -60,-30,0,30,60° = {np.round(wrapped,1)} (wrapped)")
    # ambiguity: angles giving same wrapped phase
    th_test = np.radians(20)
    ph = 2 * np.pi * d_l * np.sin(th_test)
    sols = []
    for m in range(-3, 4):
        s = (ph + 2 * np.pi * m) / (2 * np.pi * d_l)
        if abs(s) <= 1:
            sols.append(np.degrees(np.arcsin(s)))
    print(f"     source at 20° → candidate angles {np.round(sols,1)}")
    # calibration error 10° → angle error near broadside
    err = np.degrees(np.radians(10) / (2 * np.pi * d_l))
    print(f"     10° uncorrected phase error → {err:.2f}° bearing error at broadside")
print("done")
