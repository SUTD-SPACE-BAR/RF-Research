#!/usr/bin/env python3
"""
prop2_hf_paths.py — verification / worked numbers for kb/09-propagation-link-budget/hf-propagation-modes-and-prediction.md

Uses prop2_ccir.py (ITU-R P.1239 maps + P.533-14 basic MUF, validated against ITURHFProp) and prop2_igrf.py.

 1. Single-hop limits: maximum E and F2 hop ranges vs take-off angle; critical angle; secant-law recap.
 2. Singapore -> Perth / Darwin / Sydney, October, hourly basic MUF (F2 and E), FOT, lowest-order mode,
    take-off angle, for three solar-index choices (R12 = 53 'V1-equivalent', 78 'from F10.7 = 126 via the
    P.1239 relation', 88 'SILSO V2 predicted') and for solar minimum (R12 = 10).
 3. D-layer absorption per hop at noon, P.533 form Li = n (1 + 0.0067 R12) ATnoon phi_n F(chi)/F(chi_noon)
    / ((f + fL)^2 cos i110) with ATnoon ~ 300 (October, equator: ITU reference program's digitised Fig. 1),
    phi_n ~ 1-1.5 -> crude 'absorption LUF'.
 4. Skip distance vs frequency (P.533 eq. 3 single hop at the Singapore noon ionosphere); NVIS window over Singapore.
 5. Grey line: terminator times at Singapore and Perth mid-October; long-path geometry.
 6. Magneto-ionic splitting fx - fo ~ fH/2 at Singapore; Faraday on HF (qualitative).
 7. P.372 man-made / galactic noise Fam = c - d log10 f (checked against ITURHFProp outputs).
"""
import numpy as np
import prop2_ccir as cc
import prop2_igrf as igrf

ok = True
def check(name, val, lo, hi):
    global ok
    good = lo <= val <= hi
    ok &= good
    print(f"  [{'PASS' if good else 'FAIL'}] {name}: {val:.3f} (expected {lo}..{hi})")

R0 = 6371.0
SIN = (1.35, 103.82); PER = (-31.95, 115.86); DRW = (-12.46, 130.84); SYD = (-33.87, 151.21)

print("=== 1. Hop geometry ===")
for h, lab in ((110, "E"), (300, "F2"), (350, "F2 high")):
    for el in (0, 3, 10):
        e = np.radians(el); i = cc.incidence(e, h)
        d = (np.pi - i - (np.pi / 2 + e)) * R0 * 2
        print(f"  {lab:7s} h={h} km, take-off {el:2d} deg: max one-hop ground range {d:6.0f} km; sec(i) at layer = {1/np.cos(i):.2f}")
dE = cc.max_hop(110.0); dF = (np.pi - cc.incidence(0, 300) - np.pi / 2) * R0 * 2
check("E-layer one-hop range at 3 deg (km) [pre-registered 1900..2100 was wrong: 0 deg gives 2351 km]", dE, 1700, 1850)
dE0 = (np.pi - cc.incidence(0, 110) - np.pi / 2) * R0 * 2
check("E-layer one-hop range at 0 deg (km)", dE0, 2300, 2400)
check("F2 one-hop range at 0 deg, 300 km (km)", dF, 3800, 3950)
print(f"  -> exam rules of thumb: E ~1200 mi (= {1200*1.609:.0f} km), F2 ~2500 mi (= {2500*1.609:.0f} km)")
print("  Critical angle: for a given foF2 and frequency f, rays steeper than the angle where f = foF2 sec(i) penetrate.")
for f, fo in ((7, 8), (14, 8), (21, 12)):
    if f <= fo:
        print(f"   f={f} MHz <= foF2={fo}: reflected even at vertical incidence (no skip zone)")
    else:
        i_c = np.degrees(np.arccos(fo / f))
        # take-off elevation for incidence i_c at 300 km (flat-earth approx and curved)
        el = np.degrees(np.arccos(np.clip(np.sin(np.radians(i_c)) * (R0 + 300) / R0, -1, 1)))
        print(f"   f={f} MHz, foF2={fo}: critical incidence {i_c:.1f} deg -> highest take-off angle that returns ~{el:.1f} deg")

print("\n=== 2. Singapore paths, October ===")
paths = {"Singapore-Perth": (SIN, PER), "Singapore-Darwin": (SIN, DRW), "Singapore-Sydney": (SIN, SYD)}
for name, (a, b) in paths.items():
    D = cc.gc_distance(*a, *b)
    print(f"  {name}: great-circle {D:.0f} km; long path {2*np.pi*R0 - D:.0f} km")
res_store = {}
for R in (53, 78, 88, 10):
    for name, (a, b) in paths.items():
        rows = []
        for ut in range(0, 24, 2):
            r = cc.basic_muf(a, b, 10, float(ut), R)
            e = r.get("BMUF_E", 0.0)
            muf = max(r["BMUF_F2"], e)
            rows.append((ut, r["BMUF_F2"], e, muf, 0.85 * muf, r["n0"], r["elev_n0_deg"]))
        res_store[(R, name)] = rows
        mx = max(rows, key=lambda t: t[3]); mn = min(rows, key=lambda t: t[3])
        print(f"  R12={R:3d} {name:17s}: path MUF max {mx[3]:5.1f} MHz at {mx[0]:02d} UT ({(mx[0]+8)%24:02d} SGT), "
              f"min {mn[3]:5.1f} MHz at {mn[0]:02d} UT ({(mn[0]+8)%24:02d} SGT); lowest-order mode {rows[0][5]}F")
print("\n  Detail: Singapore-Perth, R12 = 78 (UT, SGT, F2 BMUF, E BMUF, FOT=0.85*MUF, n0, take-off(300 km))")
for ut, f2, e, muf, fot, n0, el in res_store[(78, "Singapore-Perth")]:
    print(f"   {ut:02d} UT / {(ut+8)%24:02d} SGT: F2 {f2:5.1f}  E {e:4.1f}  FOT {fot:5.1f}  {n0}F  {el:4.1f} deg")
noon = [t for t in res_store[(78, "Singapore-Perth")] if t[0] == 4][0]
check("Sing-Perth noon (04 UT) F2 BMUF, R12 = 78 (MHz)", noon[1], 20, 40)
night = [t for t in res_store[(78, "Singapore-Perth")] if t[0] == 20][0]
check("Sing-Perth 04 SGT (20 UT) F2 BMUF lower than noon", noon[1] - night[1], 0.5, 30)
smin = [t for t in res_store[(10, "Singapore-Perth")] if t[0] == 4][0]
print(f"  Solar-min (R12=10) noon MUF {smin[3]:.1f} MHz vs R12=78 {noon[3]:.1f} MHz (ratio {smin[3]/noon[3]:.2f})")
r_mp = cc.basic_muf(SIN, PER, 10, 4.0, 78)
mp = r_mp["mp"]
print(f"  Perth path midpoint ({mp['lat']:.1f}, {mp['lon']:.1f}) at 04 UT: foF2 {mp['foF2']:.2f} MHz, M(3000)F2 {mp['M']:.2f}, "
      f"foE {mp['foE']:.2f}, fH {mp['fH']:.2f}, hr {r_mp['hr']:.0f} km, D {r_mp['D']:.0f} km, dmax {r_mp['dmax']:.0f}")

print("\n=== 3. D-layer absorption estimate (P.533 form), Singapore-Perth, noon ===")
fL = abs(igrf.gyrofrequency(1.35, 103.82, 100, 2026.75) * np.sin(np.radians(igrf.dip(1.35, 103.82, 100, 2026.75))))
print(f"  fL (Singapore, 100 km) = |fH sin I| = {fL:.2f} MHz")
n0 = r_mp["n0"]; d = r_mp["D"] / n0
elevF = cc.elevation(d, 300.0)                 # F2 ray take-off (300 km mirror)
i110 = cc.incidence(elevF, 110.0)              # where that ray crosses 110 km
for R in (78, 10):
    for f in (5, 7, 10, 14, 21):
        Li = n0 * (1 + 0.0067 * R) * 300.0 * 1.0 / ((f + fL) ** 2 * np.cos(i110))
        print(f"  R12={R:3d}, {f:2d} MHz, {n0} hop(s), sec i110 = {1/np.cos(i110):.2f}: Li ~ {Li:5.1f} dB (phi_n = 1; x1.5 if phi_n = 1.5)")
L7 = n0 * (1 + 0.0067 * 78) * 300.0 / ((7 + fL) ** 2 * np.cos(i110))
check("noon absorption at 7 MHz, R12 = 78, 2 hops (dB)", L7, 25, 80)
print("  (vertical, 1 crossing pair, 7 MHz: ATnoon*(1+0.0067R)/(f+fL)^2 = %.1f dB; ~26 dB at 2.2 MHz with fL = 1.2 MHz"
      " at mid-latitude, the classic A1-method order of magnitude)" % (300*(1+0.0067*78)/(7+fL)**2))
# crude absorption-limited LUF: frequency where Li = 10 dB
for R in (78, 10):
    fl = np.sqrt(n0 * (1 + 0.0067 * R) * 300.0 / (10.0 * np.cos(i110))) - fL
    print(f"  crude 'absorption LUF' (Li = 10 dB) at noon, R12 = {R}: {fl:.1f} MHz (real LUF needs SNR: field strength + P.372 noise)")

print("\n=== 3b. Rough P.533 link budget, Singapore-Perth 2F, noon, R12 = 78 (eqs 17-19, 27; Lz = 8.72 dB) ===")
th = d / (2 * R0); p_virt = 2 * R0 * n0 * np.sin(th) / np.cos(elevF + th)
print(f"  hop {d:.0f} km, take-off {np.degrees(elevF):.1f} deg, virtual slant range p' = {p_virt:.0f} km")
res_noon = [t for t in res_store[(78, "Singapore-Perth")] if t[0] == 4][0]
for f in (7.0, 10.0, 14.0, 18.1, 21.0, 24.9, 28.0):
    Li = n0 * (1 + 0.0067 * 78) * 300.0 / ((f + fL) ** 2 * np.cos(i110))
    Lm = 0.0 if f <= res_noon[1] else min(36 * np.sqrt(f / res_noon[1] - 1), 62)
    Lb = 32.45 + 20 * np.log10(f) + 20 * np.log10(p_virt) + Li + Lm + 2 * (n0 - 1) + 8.72
    for Pw, G, lab in ((100, 0.0, "100 W, 0 dBi each end"), (100, 8.0, "100 W, 8 dBi Yagis")):
        Pt = 10 * np.log10(Pw / 1000)
        E = 136.6 + Pt + G + 20 * np.log10(f) - Lb
        Pr_dBm = E + G - 20 * np.log10(f) - 107.2 + 30
        N = -174 + 10 * np.log10(3000) + (72.5 - 27.7 * np.log10(f))   # residential man-made noise, 3 kHz
        if G == 0.0:
            print(f"  {f:5.1f} MHz: Li {Li:5.1f}  Lb {Lb:6.1f} dB | {lab}: E {E:6.1f} dBuV/m, Pr {Pr_dBm:7.1f} dBm, "
                  f"noise(resid., 3 kHz) {N:6.1f} dBm, SNR {Pr_dBm-N:5.1f} dB", end="")
        else:
            print(f" | {lab}: SNR {Pr_dBm-N:5.1f} dB")
f14 = 14.0; Li14 = n0 * (1 + 0.0067 * 78) * 300.0 / ((f14 + fL) ** 2 * np.cos(i110))
Lb14 = 32.45 + 20*np.log10(f14) + 20*np.log10(p_virt) + Li14 + 2*(n0-1) + 8.72
check("Lb at 14 MHz (dB)", Lb14, 140, 165)
print("  SSB needs ~+10 dB SNR in 3 kHz; FT8 decodes to ~-20 dB in 2.5 kHz; CW ~0 dB in 3 kHz-equivalent.")

print("\n=== 4. Skip distance and NVIS over Singapore (October, R12 = 78) ===")
cp = cc.cp_params(*SIN, 10, 4.0, 78)
print(f"  Singapore 12 SGT: foF2 {cp['foF2']:.2f} MHz, M(3000)F2 {cp['M']:.2f}, foE {cp['foE']:.2f}")
dmax = min(cc.calc_dmax(cp["M"], max(cp["foF2"] / cp["foE"], 2)), 4000)
def muf_d(dkm):
    return cc.f2dmuf(cp["foF2"], cp["M"], cp["foE"], cp["fH"], dkm, dmax)
from scipy.optimize import brentq
for f in (10, 14, 21, 28):
    if f <= muf_d(50.0):
        print(f"   {f} MHz: below foF2-ish vertical limit -> no skip zone")
        continue
    if f > muf_d(dmax - 1):
        print(f"   {f} MHz: above even the {dmax:.0f} km MUF -> no F2 skywave (skips everything)")
        continue
    ds = brentq(lambda x: muf_d(x) - f, 50.0, dmax - 1)
    print(f"   {f} MHz: skip distance ~ {ds:.0f} km (ground wave dies within tens of km -> silent zone in between)")
hrs = []
for ut in range(0, 24, 1):
    c = cc.cp_params(*SIN, 10, float(ut), 78)
    hrs.append((ut, c["foF2"]))
fmin = min(hrs, key=lambda t: t[1]); fmax = max(hrs, key=lambda t: t[1])
print(f"  foF2 over Singapore: max {fmax[1]:.1f} MHz at {(fmax[0]+8)%24:02d} SGT, min {fmin[1]:.1f} MHz at {(fmin[0]+8)%24:02d} SGT")
print("  NVIS working window ~ (absorption floor, ~0.85-0.9 foF2): by day ~5-11 MHz, at night ~3-0.85*min(foF2)")
check("Singapore noon foF2 Oct R12=78 (MHz)", cp["foF2"], 8, 16)

print("\n=== 5. Grey line (mid-October, declination -8.4 deg) ===")
def sunrise_set(lat, lon, decl=-8.4):
    la, de = np.radians(lat), np.radians(decl)
    h0 = np.degrees(np.arccos(-np.tan(la) * np.tan(de)))      # hour angle at geometric sunrise/set
    noon_ut = 12 - lon / 15.0
    return (noon_ut - h0 / 15) % 24, (noon_ut + h0 / 15) % 24
for name, (la, lo) in (("Singapore", SIN), ("Perth", PER), ("London", (51.5, -0.13)), ("New York", (40.7, -74.0))):
    sr, ss = sunrise_set(la, lo)
    print(f"  {name:9s}: sunrise {sr:5.2f} UT, sunset {ss:5.2f} UT")
print("  Grey-line paths: stations simultaneously near their terminators (e.g. Singapore sunset ~11 UT with"
      " European sunrise in winter) — low D absorption at both ends while F2 still ionised.")

print("\n=== 6. Magneto-ionic splitting at Singapore ===")
fH300 = igrf.gyrofrequency(1.35, 103.82, 300, 2026.75)
print(f"  fH (300 km) = {fH300:.3f} MHz -> fxF2 - foF2 ~ fH/2 = {fH300/2:.2f} MHz (for foF2 >> fH)")
fo = 10.0
fx = (fH300 + np.sqrt(fH300**2 + 4 * fo**2)) / 2      # x-wave reflects where fp^2 = f(f - fH)
print(f"  exact: foF2 = {fo} MHz -> fxF2 = {fx:.3f} MHz (difference {fx-fo:.3f} MHz)")
check("fx - fo ~ fH/2 (MHz)", fx - fo, 0.45, 0.55)

print("\n=== 7. P.372 man-made and galactic noise, Fam = c - d log10(f_MHz) (dB above kT0b) ===")
P372 = {"city": (76.8, 27.7), "residential": (72.5, 27.7), "rural": (67.2, 27.7), "quiet rural": (53.6, 28.6),
        "galactic": (52.0, 23.0)}
for k, (c, dd) in P372.items():
    print(f"  {k:12s}: 3.5 MHz {c-dd*np.log10(3.5):5.1f}  7 MHz {c-dd*np.log10(7):5.1f}  14 MHz {c-dd*np.log10(14):5.1f}  28 MHz {c-dd*np.log10(28):5.1f} dB")
check("residential at 10 MHz vs ITURHFProp 44.80 dB", 72.5 - 27.7, 44.75, 44.85)
check("rural at 6.2 MHz vs ITURHFProp 45.251 dB", 67.2 - 27.7 * np.log10(6.2), 45.2, 45.3)
check("galactic at 10 MHz vs ITURHFProp 29.00 dB", 52.0 - 23.0, 28.95, 29.05)
print("  kT0 = -174 dBm/Hz, so Fa = 45 dB in 3 kHz bandwidth means a noise floor of -174 + 34.8 + 45 = -94 dBm.")

print("\n=== 8. Solar-cycle decline (NOAA predicted F10.7 -> effective R12 via Phi = 63.7 + 0.728R + 0.00089R^2) ===")
for yr, phi in ((2026, 125.9), (2027, 103.8), (2028, 85.1), (2030, 70.8)):
    R = (-0.728 + np.sqrt(0.728**2 + 4 * 0.00089 * (phi - 63.7))) / (2 * 0.00089)
    m = [cc.basic_muf(SIN, PER, 10, ut, R)["BMUF_F2"] for ut in (4.0, 8.0, 20.0)]
    print(f"  Oct {yr}: F10.7 {phi:5.1f} -> R12 {R:5.1f}; Singapore-Perth MUF 12/16/04 SGT = {m[0]:5.1f}/{m[1]:5.1f}/{m[2]:5.1f} MHz;"
          f" Singapore noon foF2 {cc.foF2(*SIN, 10, 4.0, R):5.2f} MHz")

print("\nALL PASS" if ok else "\nSOME CHECKS FAILED")
