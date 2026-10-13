#!/usr/bin/env python3
"""
meas_range.py -- numerical checks for kb/17-test-measurement/antenna-range-ota-testing.md

1. Ground-reflection range design (IEEE Std 149 style): with grazing reflection Gamma ~ -1, the
   field at the AUT height has its first maximum at h_r = lambda R / (4 h_t); field taper over the
   AUT aperture.
2. Why ground-level link tests underestimate rocket range: exact two-ray (Gamma = -1) vs free
   space for antenna heights 1.5 m, 10 m and a 100 m drone, at 433 and 915 MHz; breakpoint
   distance 4 h_t h_r / lambda; first-Fresnel-zone radius.
3. "Range test by attenuating": equivalent free-space distance multiplier 10^(A/20); inferring
   the maximum range and the link margin from the attenuation at which PER reaches the limit.
4. TRP and TIS from sampled 3-D patterns (CTIA-style definitions), for a lossy dipole.
5. RSSI averaging needed for a given confidence in a field test.

Run: python3 tools/verify/meas_range.py
"""
import numpy as np

C0 = 299792458.0


def fspl_db(d, f):
    return 20 * np.log10(4 * np.pi * d * f / C0)


# ---------------------------------------------------------------- 1. ground-reflection range
print("=== 1. Ground-reflection range: AUT height for the first interference maximum ===")
for f in [433e6, 915e6, 1575.42e6]:
    lam = C0 / f
    for R, ht in [(30, 2.0), (50, 3.0)]:
        hr = lam * R / (4 * ht)
        # field vs height around hr (two-ray with Gamma=-1, equal path amplitudes)
        z = np.linspace(hr - 0.5, hr + 0.5, 11)
        d1 = np.sqrt(R ** 2 + (z - ht) ** 2)
        d2 = np.sqrt(R ** 2 + (z + ht) ** 2)
        k = 2 * np.pi / lam
        E = np.abs(np.exp(-1j * k * d1) / d1 - np.exp(-1j * k * d2) / d2)
        E /= E.max()
        taper = 20 * np.log10(E[[0, -1]])
        print(f"  {f/1e6:7.2f} MHz, R = {R} m, h_t = {ht} m: first peak at h_r = {hr:.2f} m; "
              f"field at h_r +/-0.5 m: {taper[0]:.2f} / {taper[1]:.2f} dB")

# ---------------------------------------------------------------- 2. ground tests vs flight
print("\n=== 2. Two-ray (Gamma=-1) path loss vs free space ===")
def two_ray_loss_db(d, f, ht, hr):
    lam = C0 / f
    k = 2 * np.pi / lam
    d1 = np.sqrt(d ** 2 + (ht - hr) ** 2)
    d2 = np.sqrt(d ** 2 + (ht + hr) ** 2)
    E = np.abs(np.exp(-1j * k * d1) / d1 - np.exp(-1j * k * d2) / d2)
    return -20 * np.log10(E * lam / (4 * np.pi))
for f in [433e6, 915e6]:
    lam = C0 / f
    print(f"  {f/1e6:.0f} MHz:")
    for ht, hr, label in [(1.5, 1.5, "both hand-held 1.5 m"), (1.5, 10, "GS mast 10 m, TX 1.5 m"),
                          (100, 10, "TX on drone 100 m, GS 10 m"), (3000, 10, "rocket 3 km up, GS 10 m")]:
        out = []
        for d in [500, 2000, 5000, 10000]:
            ex = two_ray_loss_db(d, f, ht, hr) - fspl_db(np.hypot(d, ht - hr), f)
            out.append(f"{d/1000:4.1f} km: {ex:+6.1f} dB")
        db_ = 4 * ht * hr / lam
        print(f"    {label:28s} (breakpoint {db_/1000:7.2f} km): excess over FSPL " + " | ".join(out))
    for d in [2000, 10000]:
        r1 = np.sqrt(lam * (d / 2) * (d / 2) / d)
        print(f"    first Fresnel radius at mid-path of {d/1000:.0f} km: {r1:.1f} m (clear 0.6 r1 = {0.6*r1:.1f} m)")
print("  (negative = two-ray peaks above FSPL; well past the breakpoint the loss grows 40 dB/decade)")

# ---------------------------------------------------------------- 3. range by attenuation
print("\n=== 3. Range test by attenuating ===")
for A in [10, 20, 30, 40, 50]:
    print(f"  {A} dB extra attenuation = free-space distance x {10**(A/20):7.1f}")
d0 = 200.0           # m, clear line of sight test distance (e.g. drone at 200 m slant range)
A_fail = 43.5        # dB of pads at which PER reaches 10 %
d_max = d0 * 10 ** (A_fail / 20)
print(f"  test at {d0:.0f} m LOS, link fails (PER 10 %) at {A_fail} dB added -> free-space range limit "
      f"{d_max/1000:.1f} km")
for d_flight in [3e3, 10e3, 20e3]:
    margin = A_fail - 20 * np.log10(d_flight / d0)
    print(f"    margin at {d_flight/1000:4.0f} km slant range: {margin:+5.1f} dB (before nulls/roll/plume/fading allowances)")

# ---------------------------------------------------------------- 4. TRP / TIS
print("\n=== 4. TRP and TIS from sampled patterns ===")
th = np.radians(np.arange(7.5, 180, 15))       # CTIA-style 15 deg grid (cell centres)
ph = np.radians(np.arange(0, 360, 15))
TH, PH = np.meshgrid(th, ph, indexing='ij')
eta = 0.6                                      # radiation efficiency 60 % (-2.2 dB)
P_acc_dBm = 20.0
D = 1.5 * np.sin(TH) ** 2                      # short-dipole directivity (1.5 = 1.76 dBi)
G = eta * D
EIRP = P_acc_dBm + 10 * np.log10(np.maximum(G, 1e-12))
w = np.sin(TH) * np.radians(15) ** 2
TRP = 10 * np.log10(np.sum(10 ** (EIRP / 10) * w) / (4 * np.pi))
print(f"  P_acc 20 dBm, eta 60 %: TRP from 15-deg grid = {TRP:.2f} dBm (expected {P_acc_dBm + 10*np.log10(eta):.2f} dBm)")
sens_cond = -120.0                             # conducted sensitivity, dBm
EIS = sens_cond - 10 * np.log10(np.maximum(G, 1e-6))   # effective isotropic sensitivity per direction
TIS = -10 * np.log10(np.sum(10 ** (-EIS / 10) * w) / (4 * np.pi))
print(f"  conducted sensitivity -120 dBm: TIS = {TIS:.2f} dBm (expected -120 - 10log(eta) = {-120 - 10*np.log10(eta):.2f} dBm);"
      f" peak-direction EIS {EIS.min():.2f} dBm")

# ---------------------------------------------------------------- 5. RSSI averaging
print("\n=== 5. How many RSSI samples in a field test? ===")
for sigma in [2, 4, 6]:
    for half_width in [0.5, 1.0]:
        n = (1.96 * sigma / half_width) ** 2
        print(f"  RSSI std {sigma} dB, want mean within +/-{half_width} dB (95 %): N >= {np.ceil(n):.0f} packets")
