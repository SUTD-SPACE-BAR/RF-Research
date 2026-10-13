#!/usr/bin/env python3
"""
prop2_space_weather.py — verification for kb/09-propagation-link-budget/solar-activity-and-space-weather.md

Data used (fetched 2026-10-02 by W5-E4, raw files via curl, values embedded below so the script runs offline):
  SILSO SN_ms_tot_V2.0 / SN_m_tot_V2.0 (13-month smoothed / monthly mean total sunspot number, version 2);
  NOAA SWPC observed-solar-cycle-indices.json, predicted-solar-cycle.json, f107_cm_flux.json.
Physics/definitions: NOAA SWPC scales, D-RAP documentation, K/A-index documentation; ITU-R P.1239-4 (foE);
own derivations (non-deviative absorption, light/CME travel time, Carrington rotation).

Sections
 1. Solar cycle 24/25 extrema and status in 2026 (embedded data) ; F10.7 <-> SSN relation check.
 2. Flare classes, NOAA R scale, D-RAP highest affected frequency HAF = 10 log10(flux) + 65 MHz, cos^0.75 taper,
    absorption frequency scaling (f0/f)^1.5 vs theory 1/(f +- fL)^2.
 3. Non-deviative absorption from first principles (Appleton–Hartree, collisional): kappa = (e^2/(2 eps0 m c)) N nu/(w^2+nu^2).
 4. K, a_k, A, Kp, Ap conversions; G-scale; storm-level frequencies.
 5. Timing: flare photons 8.3 min; CME transit vs speed (15 h - several days); solar wind; 27-day rotation.
 6. PCA (Sauer & Wilkinson 2008 as used in D-RAP) for given proton fluxes; S scale.
 7. foE (P.1239-4 eqs 12-18) at Singapore noon for F10.7 = 70/125/195 -> E-layer cut-off and its solar dependence.
 8. GNSS: TEC delays at L1 for equatorial-anomaly TEC levels; storm-time gradients; S4 frequency scaling;
    Singapore dip latitude (IGRF, via prop2_igrf.py) and P.533 equatorial-scatter occurrence factors.
"""
import numpy as np
import prop2_igrf as igrf

ok = True
def check(name, val, lo, hi, fmt=".3g"):
    global ok
    good = lo <= val <= hi
    ok &= good
    print(f"  [{'PASS' if good else 'FAIL'}] {name}: {val:{fmt}} (expected {lo}..{hi})")

print("=== 1. Solar cycle data (SILSO V2.0 and NOAA SWPC, fetched 2026-10-02) ===")
cycle = {  # (year, month, value)
    "SC23/24 min smoothed SSN": (2008, 12, 2.2),
    "SC24 max smoothed SSN": (2014, 4, 116.4),
    "SC24/25 min smoothed SSN": (2019, 12, 1.8),
    "SC25 max smoothed SSN": (2024, 10, 160.9),
    "latest smoothed SSN": (2026, 3, 94.5),
    "monthly mean SSN Sep 2026 (provisional)": (2026, 9, 60.3),
}
for k, (y, m, v) in cycle.items():
    print(f"  {k:42s} {y}-{m:02d}: {v}")
rise = (2024 + 9/12 + 0.5/12) - (2019 + 11/12 + 0.5/12)
print(f"  SC25 rise time (min Dec 2019 -> max Oct 2024): {rise:.2f} yr; SC25 peak / SC24 peak = {160.9/116.4:.2f}")
f107 = {"SC25 max smoothed F10.7 (2024-10)": 194.5, "highest monthly F10.7 (2024-08)": 245.6,
        "SC24/25 min smoothed F10.7 (2019-11)": 69.4, "monthly F10.7 Sep 2026": 105.4,
        "daily F10.7 1 Oct 2026": 92.0, "SWPC predicted F10.7 Oct 2026": 125.9, "SWPC predicted F10.7 Dec 2030": 70.3}
for k, v in f107.items():
    print(f"  {k:42s} {v:6.1f} sfu (1 sfu = 1e-22 W m^-2 Hz^-1)")
# Classic relation (ITU-R P.371 / CCIR): Phi12 = 63.7 + 0.728 R12 + 0.00089 R12^2
phi = lambda R: 63.7 + 0.728 * R + 0.00089 * R**2
for R, obs in ((1.8, 69.4), (116.4, 146.1), (160.9, 194.5), (94.5, 135.5)):
    print(f"  R12 = {R:6.1f}: relation gives {phi(R):6.1f} sfu, smoothed observed {obs:6.1f} sfu (diff {phi(R)-obs:+.1f})")
check("relation vs observed at SC25 max (sfu diff)", phi(160.9) - 194.5, -15, 15)
check("relation vs observed at solar min (sfu diff)", phi(1.8) - 69.4, -8, 8)

print("\n=== 2. Flares: classes, R scale, D-RAP HAF ===")
classes = {"A": 1e-8, "B": 1e-7, "C": 1e-6, "M": 1e-5, "X": 1e-4}
for c, f in classes.items():
    print(f"  class {c}: peak 0.1-0.8 nm flux >= {f:.0e} W/m^2")
haf = lambda flux: 10 * np.log10(flux) + 65
for lab, fl, exp in (("M1", 1e-5, 15), ("M5", 5e-5, 20), ("X1", 1e-4, 25), ("X5", 5e-4, 30), ("X10", 1e-3, 35)):
    print(f"  {lab:4s} ({fl:.0e} W/m^2): sub-solar HAF = {haf(fl):5.1f} MHz (SWPC table: {exp} MHz)")
check("HAF(X1) MHz", haf(1e-4), 24.9, 25.1)
check("HAF(M5) MHz", haf(5e-5), 21.9, 22.1)   # fit gives 22.0; the SWPC table entry is 20 -> fit residual 2 MHz
print("  NOTE: the fitted line gives 22.0 MHz for M5 and 32.0 MHz for X5, vs table 20 / 30 MHz (fit residual 2 MHz).")
for chi in (0, 30, 60, 80, 90):
    print(f"  X1 flare, solar zenith {chi:2d} deg: HAF = {haf(1e-4)*np.cos(np.radians(chi))**0.75:5.1f} MHz")
# absorption at other frequencies: A(f) = (f0/f)^1.5 A(f0); HAF defined at 1 dB
for f in (3.5, 7, 14, 21, 28):
    print(f"  X1 at sub-solar point, vertical: absorption at {f:4.1f} MHz ~ {(25/f)**1.5:5.1f} dB (2-way vertical, D-RAP law)")
A7 = (25/7)**1.5
check("X1 absorption at 7 MHz (dB, vertical)", A7, 6, 8)
print("  Oblique path: multiply by ~sec(i) at 90 km per D-layer crossing (2 crossings per hop).")

print("\n=== 3. Non-deviative absorption from first principles ===")
e = 1.602176634e-19; me = 9.1093837015e-31; eps0 = 8.8541878128e-12; c = 299792458.0
K = e**2 / (2 * eps0 * me * c)
print(f"  kappa = K N nu / (w^2 + nu^2) Np/m with K = e^2/(2 eps0 m c) = {K:.4e} m^2/s (x8.686 for dB)")
check("K constant", K, 5.30e-6, 5.32e-6)
def absorb_dB(f_MHz, N=1e9, nu=1e6, thick=20e3, fL=0.0):
    w = 2 * np.pi * (f_MHz + fL) * 1e6
    return 8.686 * K * N * nu / (w**2 + nu**2) * thick
for f in (2, 5, 10, 20):
    print(f"  N=1e9 m^-3, nu=1e6 s^-1, 20 km slab: {f:2d} MHz one vertical pass {absorb_dB(f):5.2f} dB; "
          f"with x-like (f-fL) 1 MHz: {absorb_dB(f, fL=-1.0):5.2f} dB, o-like (f+fL): {absorb_dB(f, fL=1.0):5.2f} dB")
ratio = absorb_dB(5) / absorb_dB(10)
check("theory scaling 5 vs 10 MHz (expect ~4 for w >> nu)", ratio, 3.9, 4.05)
print(f"  Empirical D-RAP law would give (10/5)^1.5 = {(10/5)**1.5:.2f}; P.533 uses (f + fL)^-2 per penetration.")
# flare: D-region N rises by ~10x -> absorption rises ~10x (N appears linearly)
print("  An X-class flare raising D-region N by 10x raises absorption by ~10x (kappa is linear in N): e.g. 0.8 -> 8 dB at 5 MHz.")

print("\n=== 4. Geomagnetic indices ===")
ak = {0: 0, 1: 3, 2: 7, 3: 15, 4: 27, 5: 48, 6: 80, 7: 140, 8: 240, 9: 400}
print("  K -> a_k:", ak)
day_K = [2, 3, 3, 5, 6, 5, 4, 3]
A = np.mean([ak[k] for k in day_K])
print(f"  example day K = {day_K}: A = mean(a_k) = {A:.1f}  (a_k in units of 2 nT at Boulder/Fredericksburg)")
check("example A index (pre-registered 39..40 was an arithmetic slip; sum of a_k = 255)", A, 31.5, 32.5)
G = {"G1": 5, "G2": 6, "G3": 7, "G4": 8, "G5": 9}
freq = {"G1": 1700, "G2": 600, "G3": 200, "G4": 100, "G5": 4}
for g, kp in G.items():
    print(f"  {g}: Kp = {kp}{' (incl. 9-)' if g=='G4' else ''}; ~{freq[g]} events per 11-yr cycle")
print("  K >= 5 is a storm; Kp is the standardised mean K of 13 observatories at 44-60 deg geomagnetic latitude.")
print("  Equivalent amplitude for a_k=400 at Boulder: 800 nT (K=9 lower limit 500 nT; conversion factor 2).")

print("\n=== 5. Timing ===")
AU = 1.495978707e11
t_light = AU / c
print(f"  flare photons Sun->Earth: {t_light:.1f} s = {t_light/60:.2f} min")
check("light travel (min)", t_light/60, 8.2, 8.4)
for v in (3000, 2000, 1000, 500, 400, 250):
    t = AU / (v * 1e3) / 3600
    print(f"  CME / wind at constant {v:4d} km/s: {t:6.1f} h = {t/24:4.1f} d")
check("3000 km/s CME transit (h)", AU/3e6/3600, 13, 15)
# Synodic rotation: sidereal ~25.38 d (Carrington) seen from orbiting Earth
P_sid = 25.38; P_yr = 365.256
P_syn = 1/(1/P_sid - 1/P_yr)
print(f"  Carrington sidereal {P_sid} d -> synodic (seen from Earth) {P_syn:.2f} d  -> 27-day recurrence")
check("synodic rotation (d)", P_syn, 27.1, 27.4)

print("\n=== 6. Polar cap absorption (D-RAP / Sauer & Wilkinson 2008) ===")
for J in (10, 100, 1000, 1e4):
    Ad = 0.115 * np.sqrt(J); An = 0.020 * np.sqrt(J)
    f10 = 30 * (Ad / 10) ** (2/3)
    print(f"  J(>~5 MeV) = {J:7.0f} pfu: day {Ad:5.2f} dB, night {An:5.2f} dB at 30 MHz (vertical); "
          f"10 dB affected up to {f10:5.1f} MHz (day)")
print("  (D-RAP thresholds use integral flux above energy cut-offs; S1 = 10 pfu of >=10 MeV protons.)")

print("\n=== 7. foE (ITU-R P.1239-4) at Singapore local noon ===")
def foE(phi12, lat_deg, decl_deg, chi_deg):
    Afac = 1 + 0.0094 * (phi12 - 66)
    lat = abs(lat_deg)
    m = -1.93 + 1.92 * np.cos(np.radians(lat_deg)) if lat <= 32 else 0.11 - 0.49 * np.cos(np.radians(lat_deg))
    N = lat_deg - decl_deg if abs(lat_deg - decl_deg) < 80 else 80
    B = np.cos(np.radians(N)) ** m
    X, Y = (23, 116) if lat <= 32 else (92, 35)
    C = X + Y * np.cos(np.radians(lat_deg))
    p = 1.31 if lat <= 12 else 1.20
    D = np.cos(np.radians(chi_deg)) ** p
    val = (Afac * B * C * D) ** 0.25
    fmin = (0.004 * (1 + 0.021 * phi12) ** 2) ** 0.25
    return max(val, fmin)
for phi12 in (70, 125, 195):
    v = foE(phi12, 1.35, -8.4, abs(1.35 + 8.4))   # mid-October, noon (zenith angle = |lat - decl|)
    print(f"  Phi12 = {phi12:3d} sfu: foE(noon, Oct) = {v:4.2f} MHz; E-layer 2000-km hop MUF ~ foE*sec(i110) (sec ~ 4.6) = {4.6*v:4.1f} MHz")
check("foE noon Singapore Phi=125 (MHz)", foE(125, 1.35, -8.4, 9.75), 3.6, 4.1)
print(f"  night minimum foE (Phi=125): {(0.004*(1+0.021*125)**2)**0.25:.2f} MHz")

print("\n=== 8. GNSS and the low-latitude ionosphere ===")
fL1 = 1575.42e6
for tec in (10, 50, 100, 150, 200):
    print(f"  vertical TEC {tec:3d} TECU: L1 delay {40.3*tec*1e16/fL1**2:5.1f} m vertical, "
          f"{40.3*tec*1e16/fL1**2*1.75:5.1f} m at 30 deg elevation (obliquity 1.75)")
check("L1 delay per TECU (m)", 40.3e16/fL1**2, 0.161, 0.163)
I_sg = igrf.dip(1.35, 103.82, 300, 2026.75)
mu_sg = igrf.dip_latitude(1.35, 103.82, 300, 2026.75)
eq = igrf.dip_equator_lat(103.82)
print(f"  Singapore: dip {I_sg:.1f} deg, dip latitude {mu_sg:.1f} deg; dip equator at 103.8 E lies at {eq:+.1f} deg geographic")
print(f"  EIA crests at ~+-15 deg dip latitude -> southern crest near {eq - 15*1.0:.0f}..{eq-17:.0f} deg geographic (Java/Sumatra region)")
# P.533 Attachment 1 equatorial-scatter occurrence factors
def F_dip(ld):
    ld = abs(ld)
    if ld <= 15: return 1.0
    if ld <= 25:
        x = (25 - ld) / 10
        return x * x * (3 - 2 * x)          # P.533 Att.1: ((25-ld)/10)^2 ((ld-10)/5) = smoothstep
    return 0.0
def F_T(T):
    if T <= 3 or T >= 20: return 1.0
    if 3 < T < 7:
        x = (7 - T) / 4
        return x * x * (3 - 2 * x)          # ((7-T)/4)^2 ((T-1)/2)
    if 19 < T < 20:
        x = T - 19
        return x * x * (3 - 2 * x)          # (T-19)^2 (41-2T)
    return 0.0
FR = lambda R: min(0.1 + 0.008 * R, 1.0)
print(f"  P.533 equatorial-scatter factors at Singapore: F(dip={abs(I_sg):.1f}) = {F_dip(I_sg):.2f}; F(22 LT) = {F_T(22):.2f};"
      f" F(R12=90) = {FR(90):.2f}; F(R12=10) = {FR(10):.2f}")
print("  (season factor peaks near equinox; probability -> ~1 x season at 20-03 LT for |dip| <= 15 deg.)")
check("Singapore |dip| within P.533 full-scatter band (<= 15 deg)", abs(I_sg), 0, 15)
for f in (1575.42e6, 1227.6e6, 1176.45e6, 433e6, 145.9e6):
    print(f"  S4 scaling vs L1 (weak regime, f^-1.5): {f/1e6:8.2f} MHz -> x{(f/fL1)**-1.5:.2f}")
print("  Singapore measurements (Murti 2015, NTU, PolaRxS, 2013 near SC24 max): >2 GPS satellites with S4>0.2 for 7.9 % of"
      " night-time (18-06 LT) in April 2013 and 15.7 % of 20-02 LT; June-July 2013 ~0.01-0.07 %.")

print("\nALL PASS" if ok else "\nSOME CHECKS FAILED")
