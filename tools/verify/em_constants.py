#!/usr/bin/env python3
"""
em_constants.py — verify electromagnetic constants after the 2019 SI redefinition.

Checks (all numbers from NIST CODATA 2022 / 2018 and BIPM SI Brochure 9th ed.):
  * mu0 = 2 alpha h / (e^2 c)  (exact relation given exact h, e, c)
  * eps0 = 1/(mu0 c^2), Z0 = mu0 c, Y0 = 1/Z0
  * deviation of mu0 from the pre-2019 exact value 4*pi*1e-7 H/m, for CODATA 2018 and 2022
  * handy engineering numbers: 120*pi vs Z0, 1/(36*pi)*1e-9 vs eps0, c ~ 3e8 error
  * dBuV/m <-> V/m <-> W/m^2 conversions used across the KB

Run:  python3 tools/verify/em_constants.py
Used by: kb/02-electromagnetics/electromagnetic-units-and-constants.md
"""
import math

# --- exact SI defining constants (BIPM SI Brochure, 9th ed., 2019) ---
c = 299_792_458.0            # m/s  (exact)
h = 6.626_070_15e-34         # J s  (exact)
e = 1.602_176_634e-19        # C    (exact)
k_B = 1.380_649e-23          # J/K  (exact)

# --- CODATA fine-structure constant (measured) ---
alpha_2018 = 7.297_352_5693e-3   # CODATA 2018, u_r = 1.5e-10
alpha_2022 = 7.297_352_5643e-3   # CODATA 2022, u_r = 1.6e-10 (NIST, fetched 2026-09-27)

# --- CODATA published mu0, eps0, Z0 (for cross-check) ---
mu0_2022_pub = 1.256_637_061_27e-6   # N/A^2, (20) in last digits
eps0_2022_pub = 8.854_187_8188e-12   # F/m, (14)
Z0_2022_pub = 376.730_313_412        # ohm, (59)
mu0_2018_pub = 1.256_637_062_12e-6   # N/A^2, (19)

mu0_old = 4 * math.pi * 1e-7         # exact before 20 May 2019


def derived(alpha):
    mu0 = 2 * alpha * h / (e**2 * c)
    eps0 = 1 / (mu0 * c**2)
    Z0 = mu0 * c
    return mu0, eps0, Z0


print("=== mu0 from alpha (mu0 = 2 alpha h / (e^2 c)) ===")
for tag, a, pub in (("2018", alpha_2018, mu0_2018_pub), ("2022", alpha_2022, mu0_2022_pub)):
    mu0, eps0, Z0 = derived(a)
    print(f"CODATA {tag}: mu0 = {mu0:.14e}  (published {pub:.14e}; diff {abs(mu0-pub)/pub:.1e} rel)")
    print(f"             mu0/(4pi e-7) - 1 = {mu0/mu0_old - 1:+.3e}")
    print(f"             eps0 = {eps0:.12e} F/m, Z0 = {Z0:.9f} ohm")

mu0, eps0, Z0 = derived(alpha_2022)
assert abs(mu0 - mu0_2022_pub) / mu0_2022_pub < 2e-11
assert abs(eps0 - eps0_2022_pub) / eps0_2022_pub < 2e-10
assert abs(Z0 - Z0_2022_pub) < 1e-7

print("\n=== engineering approximations vs CODATA 2022 ===")
print(f"Z0 = {Z0:.6f} ohm; 120*pi = {120*math.pi:.6f} ohm; error = {(120*math.pi-Z0)/Z0*100:+.4f} %")
print(f"eps0 = {eps0:.6e}; 1e-9/(36 pi) = {1e-9/(36*math.pi):.6e}; error = {(1e-9/(36*math.pi)-eps0)/eps0*100:+.4f} %")
print(f"c ~ 3e8: error = {(3e8-c)/c*100:+.4f} %")
print(f"Z0 with old exact mu0 = 4pi e-7 * c = {mu0_old*c:.9f} ohm; differs from CODATA 2022 by {(mu0_old*c-Z0):.2e} ohm")
print(f"Y0 = 1/Z0 = {1/Z0*1e3:.6f} mS")

print("\n=== field-strength unit conversions (plane wave, free space) ===")
def dBuVm_from_Vm(E):
    return 20 * math.log10(E / 1e-6)
def S_from_E(E):              # W/m^2 for rms E in V/m
    return E**2 / Z0
def dBm_m2_from_S(S):
    return 10 * math.log10(S / 1e-3)
for E in (1e-6, 1e-3, 1.0, 61.0):
    print(f"E = {E:g} V/m rms -> {dBuVm_from_Vm(E):7.2f} dBuV/m, S = {S_from_E(E):.3e} W/m^2 = {dBm_m2_from_S(S_from_E(E)):7.2f} dBm/m^2")
# offset between dBuV/m and dBm/m^2 : dBm/m^2 = dBuV/m - 115.76
off = dBuVm_from_Vm(1.0) - dBm_m2_from_S(S_from_E(1.0))
print(f"dBuV/m - dBm/m^2 = {off:.3f} dB  (i.e. dBm/m^2 = dBuV/m - {off:.2f})")
# dBuV/m <-> dBm received by an isotropic antenna at f: P = S * lambda^2/(4 pi)
for f in (433e6, 915e6, 1575.42e6, 2.45e9):
    lam = c / f
    Aeff = lam**2 / (4 * math.pi)
    k = off + 10 * math.log10(1 / Aeff)   # dBuV/m = dBm + k
    print(f"f = {f/1e6:8.2f} MHz: isotropic Ae = {Aeff*1e4:8.2f} cm^2; E[dBuV/m] = P[dBm] + {k:.2f}")

print("\n=== Gaussian <-> SI reminders ===")
print("1 gauss = 1e-4 T; 1 oersted = 1000/(4 pi) A/m =", 1000/(4*math.pi), "A/m")
print("1 statvolt = 299.792458 V; 1 statC = 3.33564e-10 C:", 0.1/c)
print("Gaussian e^2 (in erg cm) ~ alpha*hbar*c; SI: e^2/(4 pi eps0) = alpha hbar c ->",
      e**2/(4*math.pi*eps0), "vs", alpha_2022*h/(2*math.pi)*c)
print("\nAll assertions passed.")
