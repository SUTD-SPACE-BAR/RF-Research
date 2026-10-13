#!/usr/bin/env python3
"""
s17_rf_exposure_rules.py -- G-19-04 (W5-S17): numbers for the "rule details" section of
kb/19-regulations-safety/rf-exposure-safety.md.

1. Whole-body resonance estimate: f_res ~ k c / L, k = 0.36-0.4 (ungrounded, E parallel to the body,
   dosimetry handbook value) and about half that when standing on a conducting ground
   (quarter-wave-monopole analogy, Hirata et al. 2012). Adult 1.75 m, child 1.2 m, infant 0.7 m.
2. FCC 47 CFR 1.1307(b)(3)(i)(C) Table 1 exemption thresholds incl. the HF rows
   (0.3-1.34 MHz 1920 R^2; 1.34-30 MHz 3450 R^2/f^2) and the R >= lambda/2pi condition: the
   distance at which a 100 W ERP HF station becomes exempt.
3. Multiple transmitters: sum of fractions (ICNIRP / FCC) for the rocket with E22 (2 W) and
   E220 (1 W) on dipoles, and the FCC 5 % rule (1.1307(b)(5)(i)) for a shared ground site.
Run: python3 tools/verify/s17_rf_exposure_rules.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reg_rf_exposure import s_limit_icnirp, s_limit_fcc, power_density, dbm_to_w  # noqa: E402

C0 = 299_792_458.0
ok = True

print("1) Whole-body resonance f = k c / L")
for name, L in (("adult 1.75 m", 1.75), ("child 1.2 m", 1.2), ("infant 0.7 m", 0.7)):
    f_lo, f_hi = 0.36 * C0 / L / 1e6, 0.40 * C0 / L / 1e6
    print(f"   {name:13s}: ungrounded {f_lo:5.0f}-{f_hi:5.0f} MHz; grounded (about half) {f_lo/2:4.0f}-{f_hi/2:4.0f} MHz")
ok &= 60 < 0.38 * C0 / 1.75 / 1e6 < 70


def fcc_threshold_erp(f, R):
    """47 CFR 1.1307(b)(3)(i)(C) Table 1, ERP [W]; f MHz, R m (valid only if R >= lambda/2pi)."""
    if 0.3 <= f < 1.34:
        return 1920 * R**2
    if 1.34 <= f < 30:
        return 3450 * R**2 / f**2
    if 30 <= f < 300:
        return 3.83 * R**2
    if 300 <= f < 1500:
        return 0.0128 * R**2 * f
    if 1500 <= f <= 100000:
        return 19.2 * R**2
    raise ValueError


print("2) FCC exemption distance for ERP = 100 W (formula) and the lambda/2pi floor")
for f in (1.9, 3.6, 7.1, 14.2, 21.2, 28.5, 50.1, 145.0, 433.0):
    a = {f < 1.34: 1920, 1.34 <= f < 30: 3450 / f**2, 30 <= f < 300: 3.83, 300 <= f < 1500: 0.0128 * f}[True]
    r_formula = math.sqrt(100 / a)
    r_floor = C0 / (f * 1e6) / (2 * math.pi)
    print(f"   {f:6.1f} MHz: R(formula) {r_formula:5.2f} m; lambda/2pi {r_floor:5.2f} m -> exempt only if R >= "
          f"{max(r_formula, r_floor):5.2f} m")
ok &= abs(math.sqrt(100 / (3450 / 7.1**2)) - 1.209) < 0.01

print("3a) Rocket with both radios on dipoles (EIRP = P - 0.5 dB + 2.15 dBi), continuous, free space")
tx = [("E22 433.125 MHz 33 dBm", 433.125, 33.0), ("E220 868.125 MHz 30 dBm", 868.125, 30.0)]
for R in (0.3, 0.5, 1.0):
    fi = ff = 0.0
    parts = []
    for name, f, p in tx:
        eirp = dbm_to_w(p - 0.5 + 2.15)
        S = power_density(eirp, R)
        fi += S / s_limit_icnirp(f)
        ff += S / s_limit_fcc(f)
        parts.append(f"{S/s_limit_icnirp(f):.2f}")
    print(f"   R = {R} m: ICNIRP fractions {' + '.join(parts)} = {fi:.2f}; FCC sum {ff:.2f} -> "
          f"{'COMPLIANT' if fi <= 1 else 'over'} (ICNIRP)")
# distance where ICNIRP sum = 1: S ~ 1/R^2 so sum(R) = sum(1 m) / R^2
s1 = sum(power_density(dbm_to_w(p - 0.5 + 2.15), 1.0) / s_limit_icnirp(f) for _, f, p in tx)
print(f"   ICNIRP sum = 1 at R = {math.sqrt(s1):.2f} m (vs {math.sqrt(power_density(dbm_to_w(33.0 - 0.5 + 2.15), 1.0)/s_limit_icnirp(433.125)):.2f} m for the E22 alone)")

print("3b) FCC 5 % rule at a shared site (fractions of the general-population MPE at one spot)")
site = {"broadcast FM 98 MHz": 0.93, "club 2 m repeater 145 MHz": 0.09, "our 433 MHz uplink": 0.03}
tot = sum(site.values())
print(f"   total {tot:.2f} ({'exceeds' if tot > 1 else 'within'} the limit)")
for k, v in site.items():
    print(f"   {k:27s} {100*v:5.1f} % -> {'shares responsibility' if v > 0.05 else 'not responsible (<= 5 %)'}")
print("CHECK:", "PASS" if ok else "FAIL")
