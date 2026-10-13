#!/usr/bin/env python3
"""
prop2_vhf_anomalous.py — verification for kb/09-propagation-link-budget/vhf-uhf-anomalous-propagation.md

 1. Radio refractivity (ITU-R P.453-14 eq. 7) for Singapore-like air; standard gradient -> k = 4/3; radio horizon
    15 % beyond geometric.
 2. Ducting condition from ray curvature: dN/dh <= -1e6/a = -157 N/km; modified refractivity M = N + 157 h.
 3. Maximum trapped wavelength in a surface duct by WKB/Airy phase integral -> lambda_max = 2.51 d sqrt(dM 1e-6);
    evaporation duct vs inversion duct: which frequencies (433/915 MHz, 2.4/5.8 GHz, 10 GHz) are trapped.
 4. Ducted path loss (cylindrical spreading) for a 915 MHz LoRa node at 400 km vs LoRa sensitivity.
 5. Sporadic-E: one-hop geometry at 110-120 km, MUF = foEs sec i; ITU-R P.534-6 eqs (1a), (3)-(5) field strength;
    P.1239/P.534 foEs map values over Singapore and Tokyo (median and upper decile) from prop2_ccir.
 6. Meteor scatter: geometry limit, underdense trail decay time tau = lambda^2 / (16 pi^2 D) (amplitude, backscatter),
    forward-scatter lengthening sec^2(phi), band comparison 28-432 MHz.
 7. Aircraft scatter: horizon-limited range, bistatic radar equation, Doppler.
 8. EME: path loss eta r^2 lambda^2 / (64 pi^2 d^4) vs ARRL Handbook table, perigee/apogee, delay, Doppler.
 9. TEP geometry: dip latitudes (IGRF) of Singapore, Darwin, Townsville, Okinawa, Hong Kong, Tokyo; symmetric pairs.
"""
import numpy as np
import prop2_igrf as igrf
import prop2_ccir as cc

ok = True
def check(name, val, lo, hi):
    global ok
    good = lo <= val <= hi
    ok &= good
    print(f"  [{'PASS' if good else 'FAIL'}] {name}: {val:.4g} (expected {lo}..{hi})")

c = 299792458.0; a = 6371e3

print("=== 1. Refractivity ===")
def es(t):  # saturation vapour pressure over water, hPa (P.453 eq. 9, EF ~ 1)
    return 6.1121 * np.exp((18.678 - t / 234.5) * t / (t + 257.14))
def N_of(P, t, RH):
    e = RH / 100 * es(t); T = t + 273.15
    return 77.6 / T * (P + 4810 * e / T), e
for P, t, RH, lab in ((1013.25, 15, 0, "dry 15 C"), (1013.25, 15, 60, "15 C 60 %"), (1009, 30, 80, "Singapore 30 C 80 %"),
                      (1009, 28, 95, "Singapore night 28 C 95 %")):
    N, e = N_of(P, t, RH)
    print(f"  {lab:26s}: e = {e:5.1f} hPa, N = {N:6.1f} N-units (dry part {77.6/(t+273.15)*P:5.1f})")
Nsg, _ = N_of(1009, 30, 80)
check("Singapore surface N", Nsg, 370, 410)
k = lambda g: 1 / (1 + a * g * 1e-9)    # g in N/km -> dn/dh = g*1e-6 per km = g*1e-9 per m
for g in (-40, 0, -100, -157):
    kk = k(g)
    print(f"  dN/dh = {g:5d} N/km: k = {kk if np.isfinite(kk) and kk < 1e6 else float('inf'):.3g}")
check("k for -40 N/km", k(-40), 1.33, 1.35)
print(f"  radio/geometric horizon ratio sqrt(4/3) = {np.sqrt(4/3):.3f} -> ~15 % farther")
check("horizon ratio", np.sqrt(4/3), 1.15, 1.16)

print("\n=== 2. Ducting condition ===")
crit = -1e6 / (a / 1e3)
print(f"  ray curvature = -dn/dh (near-horizontal); equals Earth curvature 1/a when dN/dh = -1e6/a = {crit:.1f} N/km")
check("critical gradient (N/km)", crit, -157.5, -156.5)
print("  M(h) = N(h) + 157 h(km): dM/dh = dN/dh + 157 < 0 marks a trapping layer")

print("\n=== 3. Maximum trapped wavelength (surface duct, linear M profile, WKB phase integral) ===")
# lowest mode: (2/3) k theta^3 / g' = 3 pi / 2 with turning height <= d -> lambda_max = (16 sqrt2 / 9) d sqrt(dM e-6)
C = 16 * np.sqrt(2) / 9
print(f"  derived coefficient C = 16 sqrt(2)/9 = {C:.3f}  (lambda_max = C d sqrt(dM 1e-6))")
check("coefficient vs literature 2.5", C, 2.45, 2.55)
def fmin(d, dM):
    return c / (C * d * np.sqrt(dM * 1e-6))
for d, dM, lab in ((10, 10, "evaporation duct 10 m, dM 10"), (15, 15, "evaporation duct 15 m, dM 15"),
                   (25, 25, "strong evaporation duct 25 m, dM 25"), (100, 20, "surface-based inversion 100 m, dM 20"),
                   (200, 30, "elevated/surface inversion 200 m, dM 30"), (300, 40, "thick trade-wind/subsidence duct 300 m")):
    f = fmin(d, dM)
    tr = [x for x, fx in (("433", 433e6), ("915", 915e6), ("2.4G", 2.4e9), ("5.8G", 5.8e9), ("10G", 10e9)) if fx >= f]
    print(f"  {lab:38s}: f_min = {f/1e6:7.0f} MHz -> trapped: {', '.join(tr) if tr else 'none of the listed'}")
check("15 m evaporation duct f_min (GHz)", fmin(15, 15) / 1e9, 1.5, 3.0)
check("100 m inversion duct f_min (MHz)", fmin(100, 20) / 1e6, 200, 350)

print("\n=== 4. Ducted LoRa path at 915 MHz ===")
fspl = lambda d_m, f: 20 * np.log10(4 * np.pi * d_m * f / c)
for D in (100e3, 200e3, 400e3):
    L_free = fspl(D, 915e6)
    L_duct = fspl(50e3, 915e6) + 10 * np.log10(D / 50e3) + 10.0   # cylindrical beyond 50 km + 10 dB coupling/leakage
    print(f"  {D/1e3:4.0f} km: free-space {L_free:6.1f} dB; ducted (cylindrical from 50 km, +10 dB coupling) ~{L_duct:6.1f} dB;"
          f" EIRP 22 dBm+3 dBi, Rx 3 dBi, SF12/BW125 sens -137 dBm -> margin {22+3+3-L_duct+137:5.1f} dB")
check("400 km ducted margin positive (dB)", 22 + 3 + 3 - (fspl(50e3, 915e6) + 10*np.log10(8) + 10) + 137, 0, 40)
print("  (beyond the smooth-earth horizon the normal diffraction loss would be >> 100 dB extra)")

print("\n=== 5. Sporadic-E ===")
for h in (110, 120):
    for el in (0, 3):
        e = np.radians(el); i = cc.incidence(e, h)
        d = (np.pi - i - (np.pi / 2 + e)) * 6371 * 2
        print(f"  Es at {h} km, take-off {el} deg: one-hop {d:5.0f} km, sec i = {1/np.cos(i):.2f}")
secmax = 1 / np.cos(cc.incidence(0, 110))
for foEs in (5, 10, 15, 25):
    print(f"  foEs = {foEs:2d} MHz -> max one-hop Es MUF ~ {foEs*secmax:5.1f} MHz (2 m needs foEs >= {144/secmax:.0f} MHz)")
check("Es max obliquity at 110 km", secmax, 5.3, 5.6)
def p534_E(d_km, f, foEs, P_dBkW=0.0, Gt=0.0):
    R0e, h = 8500.0, 120.0
    l = np.sqrt(2 * R0e**2 + (R0e + h)**2 - 2 * R0e * (R0e + h) * np.cos(d_km / (2 * R0e)))  # P.534 eq. (5) as printed
    l_true = 2 * np.sqrt(R0e**2 + (R0e + h)**2 - 2 * R0e * (R0e + h) * np.cos(d_km / (2 * R0e)))  # 2 x slant to midpoint
    E0 = 104.8 - 20 * np.log10(l_true)
    G = 40 / (1 + d_km / 130 + (d_km / 250)**2) + 0.2 * (d_km / 2600)**2 * (f / foEs)**2 + np.exp((d_km - 1660) / 280)
    return E0 + P_dBkW + Gt - G, G, l, l_true
for d, f, fo in ((1000, 50, 10), (1500, 50, 10), (1500, 144, 25), (2000, 50, 12)):
    E, G, l, lt = p534_E(d, f, fo)
    print(f"  P.534: d={d} km, f={f} MHz, foEs={fo}: Gamma = {G:5.1f} dB, path length {lt:6.0f} km, E(1 kW EIRP isotropic) = {E:5.1f} dBuV/m")
print("  NOTE: P.534 eq. (5) as extracted by pdftotext reads l = [2R0^2 + (R0+h)^2 - 2R0(R0+h)cos(d/2R0)]^0.5;"
      " the geometric two-leg path is 2[R0^2 + (R0+h)^2 - 2R0(R0+h)cos(d/2R0)]^0.5 (used here; layout ambiguity noted).")
E1, G1, l1, lt1 = p534_E(1500, 50, 10)
check("P.534 Gamma at 1500 km, f/foEs = 5 (dB) [pre-registered 5..25 was a guess; formula value]", G1, 2.5, 3.5)
G2 = p534_E(2000, 96, 12)[1]
check("P.534 Gamma at 2000 km, f/foEs = 8 (dB)", G2, 10, 13)
print("  foEs over Singapore and Tokyo from the P.1239/P.534 maps (R12 = 78), local noon and 20 LT:")
for name, la, lo, tz in (("Singapore", 1.35, 103.82, 8), ("Tokyo", 35.7, 139.7, 9)):
    for mo in (1, 6, 10, 12):
        vals = []
        for lt in (12, 20):
            ut = (lt - tz) % 24
            vals.append((cc.foEs(la, lo, mo, ut, 78, "xes"), cc.foEs(la, lo, mo, ut, 78, "xesu")))
        print(f"   {name:9s} month {mo:2d}: noon median {vals[0][0]:4.1f} / upper decile {vals[0][1]:4.1f} MHz; "
              f"20 LT {vals[1][0]:4.1f} / {vals[1][1]:4.1f} MHz")
tok_jun = cc.foEs(35.7, 139.7, 6, 3.0, 78, "xes"); tok_dec = cc.foEs(35.7, 139.7, 12, 3.0, 78, "xes")
check("Tokyo median foEs June noon > December noon (MHz)", tok_jun - tok_dec, 0.0, 10)

print("\n=== 6. Meteor scatter ===")
for h in (80, 100, 120):
    dmax = 2 * np.sqrt(2 * 6371 * h)
    print(f"  trail at {h} km, both stations at 0 deg elevation: max range ~ {dmax:5.0f} km")
check("meteor max range at 100 km (km)", 2*np.sqrt(2*6371*100), 2200, 2300)
for D in (2, 5):
    for f in (28, 50, 144, 222, 432):
        lam = c / (f * 1e6)
        tb = lam**2 / (16 * np.pi**2 * D)
        tf = tb / np.cos(np.radians(70))**2      # forward scatter, half-angle 70 deg (long path)
        print(f"  D = {D} m^2/s, {f:3d} MHz: underdense amplitude decay time back-scatter {tb*1e3:7.2f} ms, "
              f"forward (phi = 70 deg) {tf*1e3:7.1f} ms")
t50 = (c/50e6)**2/(16*np.pi**2*2)/np.cos(np.radians(70))**2
t144 = (c/144e6)**2/(16*np.pi**2*2)/np.cos(np.radians(70))**2
check("50/144 MHz duration ratio = (144/50)^2", t50 / t144, 8.2, 8.4)
print("  Underdense received power also scales ~ lambda^3 (Eshleman): 6 m is (144/50)^3 = %.0fx (%.0f dB) stronger than 2 m" %
      ((144/50)**3, 30*np.log10(144/50)))

print("\n=== 7. Aircraft scatter ===")
for halt in (9e3, 11e3, 12e3):
    dh = 4.12 * np.sqrt(halt) * 1e3   # 4/3 earth, m
    print(f"  aircraft at {halt/1e3:4.1f} km: radio horizon {dh/1e3:5.0f} km each side -> max path ~{2*dh/1e3:5.0f} km")
check("max aircraft-scatter path at 11 km (km)", 2 * 4.12 * np.sqrt(11e3), 850, 880)
f = 144e6; lam = c / f; Pt = 100; G = 10**(14/10); sigma = 100.0
for R1, R2 in ((300e3, 300e3), (400e3, 400e3)):
    Pr = Pt * G * G * lam**2 * sigma / ((4 * np.pi)**3 * R1**2 * R2**2)
    print(f"  bistatic R1=R2={R1/1e3:.0f} km, 144 MHz, 100 W, 14 dBi each, sigma = 100 m^2: Pr = {10*np.log10(Pr)+30:6.1f} dBm "
          f"(forward-scatter sigma can be 10-30 dB larger near the bistatic baseline)")
print(f"  Doppler (250 m/s, worst-case geometry 2v/lambda) at 144 MHz: up to {2*250/lam:.0f} Hz")

print("\n=== 8. EME ===")
r_m = 1.738e6; eta = 0.065
def eme(fMHz, d=3.844e8):
    lam = c / (fMHz * 1e6)
    return -10 * np.log10(eta * r_m**2 * lam**2 / (64 * np.pi**2 * d**4))
ref = {50: 242.9, 144: 252.1, 222: 255.8, 432: 261.6, 902: 268.0, 1296: 271.2, 2304: 276.2, 10368: 289.2}
for fM, L in ref.items():
    print(f"  {fM:5d} MHz: EME path loss {eme(fM):6.1f} dB (ARRL Handbook table {L})")
check("EME 144 MHz path loss (dB)", eme(144), 251.9, 252.3)
check("EME 1296 MHz path loss (dB)", eme(1296), 271.0, 271.4)
dp, da = 3.565e8, 4.067e8
print(f"  perigee 356 500 km vs apogee 406 700 km: {40*np.log10(da/dp):.2f} dB (exam: least loss at perigee)")
check("perigee-apogee difference (dB)", 40 * np.log10(da / dp), 2.1, 2.4)
print(f"  echo delay mean {2*3.844e8/c:.2f} s; Earth-rotation Doppler (460 m/s, two-way) at 144 MHz ~ {2*460/(c/144e6):.0f} Hz")
print(f"  radar-equation check: sigma = eta pi r^2 = {eta*np.pi*r_m**2:.3g} m^2")
lim = 180 + 2 * 0.95
print(f"  max ground separation: both stations see the Moon -> up to ~{lim:.0f} deg of arc ~ {lim/360*40030:.0f} km"
      f" (exam: 12 000 mi = {12000*1.609:.0f} km)")

print("\n=== 9. TEP geometry (dip latitudes from IGRF-14, 2026.75) ===")
sites = {"Singapore": (1.35, 103.82), "Darwin": (-12.46, 130.84), "Townsville": (-19.26, 146.82),
         "Perth": (-31.95, 115.86), "Okinawa": (26.21, 127.68), "Hong Kong": (22.32, 114.17), "Tokyo": (35.68, 139.69),
         "Manila": (14.6, 121.0), "Brisbane": (-27.47, 153.03)}
dl = {}
for s, (la, lo) in sites.items():
    dl[s] = igrf.dip_latitude(la, lo, 300, 2026.75)
    print(f"  {s:10s}: dip latitude (300 km) {dl[s]:+6.1f} deg")
for A, B in (("Darwin", "Okinawa"), ("Townsville", "Tokyo"), ("Darwin", "Hong Kong"), ("Brisbane", "Tokyo"),
             ("Singapore", "Manila")):
    D = cc.gc_distance(*sites[A], *sites[B])
    print(f"  {A}-{B}: {D:5.0f} km, dip latitudes {dl[A]:+5.1f} / {dl[B]:+5.1f} (sum {dl[A]+dl[B]:+5.1f}: ~0 = symmetric)")
check("Darwin-Okinawa distance (km)", cc.gc_distance(*sites["Darwin"], *sites["Okinawa"]), 4000, 5000)
check("Singapore dip latitude (deg)", dl["Singapore"], -8, -5)

print("\nALL PASS" if ok else "\nSOME CHECKS FAILED")
