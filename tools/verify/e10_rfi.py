#!/usr/bin/env python3
"""
e10_rfi.py — numbers for kb/17-test-measurement/interference-hunting-and-rf-immunity.md (W5-E10).

 1. Distance law near a noise source: near-field H of a small loop ~ 1/r^3 (power 60 dB/decade) vs
    far field 1/r (20 dB/decade); boundary lambda/(2 pi) per band. Exact small-loop field magnitude.
 2. Close-in fox hunting: received power from a 1 W fox vs receiver overload; attenuation needed.
 3. RCD/GFCI: 50 Hz protective-conductor current of Y capacitors; number of devices to reach the
    BS 7671 30 % guidance (9 mA) and the IEC 61008 50 % non-trip floor (15 mA) of a 30 mA RCD;
    BEAMA transient example (1 kV, 50 us rise -> 1.6 nF for 50 mA).
 4. Ferrite choke "threshold effect": current reduction vs added impedance for a resistive and a
    capacitive (resonating) common-mode circuit; square-law detection doubles the dB.
 5. Own-transmitter field at a sensor: E = sqrt(30 P G)/r vs IEC 61000-4-3 test levels.
 6. Verifying a fix: averaging needed to resolve a dB change of the noise floor (MC check of
    std of a K-sample averaged exponential power in dB ~ 4.34/sqrt(K)).
 7. GSM 217 Hz buzz: TDMA frame rate and burst duty.

Run:  python3 tools/verify/e10_rfi.py
"""
import cmath
import math
import random

random.seed(7)
C = 299792458.0
FAIL = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAIL.append(name)


# ------------------------------------------------------------- 1. distance law
print("1. Small-loop (magnetic dipole) field vs distance, broadside, |H| ~ |1/(kr)^3 + j/(kr)^2 - 1/(kr)| form")


def h_mag(r, lam):
    k = 2 * math.pi / lam
    x = k * r
    # theta-component magnitude of a small loop (broadside), up to constant: |1/x - j/x^2 - 1/x^3|... use
    # radial+theta combined on axis-of-maximum for near field: dominated by 1/x^3
    return abs(1 / x - 1j / x ** 2 - 1 / x ** 3)


for f, lab in ((7e6, "7 MHz"), (30e6, "30 MHz"), (146e6, "146 MHz"), (433e6, "433 MHz")):
    lam = C / f
    rb = lam / (2 * math.pi)
    r1, r2 = 0.1 * rb, 0.2 * rb
    d_near = 20 * math.log10(h_mag(r1, lam) / h_mag(r2, lam))
    r1, r2 = 10 * rb, 20 * rb
    d_far = 20 * math.log10(h_mag(r1, lam) / h_mag(r2, lam))
    print(f"  {lab:8s}: lambda/2pi = {rb:6.2f} m; halving distance deep in near field: +{d_near:4.1f} dB; "
          f"in far field: +{d_far:4.1f} dB")
check("near-field halving distance ~ +18 dB", abs(d_near - 18.0) < 0.5)
check("far-field halving distance ~ +6 dB", abs(d_far - 6.0) < 0.3)

# ------------------------------------------------------------- 2. fox hunting close in
print("\n2. Close-in fox: received power from 1 W at 146 MHz (0 dBi both ends, free space)")


def fspl(d, f):
    return 20 * math.log10(4 * math.pi * d * f / C)


for d in (1000, 100, 10, 1):
    pr = 30 - fspl(d, 146e6)
    print(f"  {d:5d} m: FSPL {fspl(d,146e6):5.1f} dB, Pr {pr:6.1f} dBm, above S9 (-73 dBm) by {pr+73:5.1f} dB")
check("1 W fox at 10 m is ~67 dB above S9", abs((30 - fspl(10, 146e6)) + 73 - 67.3) < 0.5)
print("  third-harmonic trick: listening at 3f gives the fox's harmonic, typically 40-60 dB down (HomingIn)")

# ------------------------------------------------------------- 3. RCD leakage
print("\n3. RCD: Y-capacitor protective-conductor current at 230 V 50 Hz")
for cy in (1e-9, 2.2e-9, 4.7e-9, 10e-9):
    i = 2 * math.pi * 50 * cy * 230
    print(f"  Cy {cy*1e9:4.1f} nF -> {i*1e3:5.3f} mA; devices to 9 mA: {math.ceil(9e-3/i):3d}; to 15 mA: "
          f"{math.ceil(15e-3/i):3d}")
i47 = 2 * math.pi * 50 * 4.7e-9 * 230
check("4.7 nF at 230 V 50 Hz = 0.34 mA", abs(i47 - 0.3396e-3) < 2e-6)
# BEAMA example
xc = 1000 / 0.05
f_eq = 1 / (4 * 50e-6)
c_eq = 1 / (2 * math.pi * f_eq * xc)
print(f"  BEAMA transient: Xc {xc:.0f} ohm, f_eq {f_eq:.0f} Hz, C = {c_eq*1e9:.2f} nF gives 50 mA")
check("BEAMA 1.6 nF", abs(c_eq * 1e9 - 1.59) < 0.01)
# 120 V 60 Hz US
i_us = 2 * math.pi * 60 * 4.7e-9 * 120
print(f"  US 120 V 60 Hz, 4.7 nF -> {i_us*1e3:.3f} mA (GFCI trips at 4-6 mA per UL 943 class A)")

# ------------------------------------------------------------- 4. ferrite threshold
print("\n4. Common-mode choke threshold effect (K9YC): reduction = 20 log|Z_loop + Z_choke| / |Z_loop|")
zl_res = 300 + 0j
zl_cap = 50 - 300j
print(f"{'Z_choke':>18s} {'resistive loop dB':>18s} {'capacitive loop dB':>19s} {'detected (x2) dB':>17s}")
for zc in (100 + 0j, 300 + 0j, 1000 + 0j, 3000 + 0j, 0 + 200j, 50 + 250j, 1000 + 1000j):
    r_res = 20 * math.log10(abs(zl_res + zc) / abs(zl_res))
    r_cap = 20 * math.log10(abs(zl_cap + zc) / abs(zl_cap))
    print(f"{str(zc):>18s} {r_res:18.1f} {r_cap:19.1f} {2*r_res:17.1f}")
check("300 ohm resistive choke on 300 ohm loop = 6 dB", abs(20 * math.log10(2) - 6.02) < 0.01)
check("an inductive choke can INCREASE current in a capacitive loop",
      abs(zl_cap + 200j) < abs(zl_cap))
# clamp-on bead turns scaling below resonance
print("  N^2 scaling below self-resonance: 1 turn 150 ohm -> 2 turns 600, 3 turns 1350, 5 turns 3750 ohm (ideal)")

# ------------------------------------------------------------- 5. own-transmitter field
print("\n5. Field from our own transmitter: E = sqrt(30 P G)/r (far-field formula; optimistic inside lambda/2pi)")
for P, G_dbi, lab in ((2.0, 2.15, "E22 2 W, 433 MHz dipole"), (1.0, 2.15, "E220 1 W, 915 MHz dipole"),
                      (0.1, 2.15, "100 mW SRD")):
    G = 10 ** (G_dbi / 10)
    row = []
    for r in (0.05, 0.1, 0.3, 1.0, 3.0):
        row.append(f"{r:4.2f} m:{math.sqrt(30*P*G)/r:6.1f} V/m")
    r10 = math.sqrt(30 * P * G) / 10
    r3 = math.sqrt(30 * P * G) / 3
    print(f"  {lab:26s}: " + ", ".join(row) + f" | 10 V/m at {r10:.2f} m, 3 V/m at {r3:.2f} m")
check("2 W dipole gives ~99 V/m at 10 cm", abs(math.sqrt(30 * 2 * 10 ** 0.215) / 0.1 - 99.2) < 1)
print("  IEC 61000-4-3 test levels: 1, 3, 10, 30 V/m (levels 1-4), 80 MHz-6 GHz")

# ------------------------------------------------------------- 6. averaging to verify a fix
print("\n6. Averaging needed to see a noise-floor change: std of 10log10(mean of K exp samples)")
for K in (1, 10, 100, 1000):
    vals = []
    for _ in range(4000):
        m = sum(random.expovariate(1.0) for _ in range(K)) / K
        vals.append(10 * math.log10(m))
    mu = sum(vals) / len(vals)
    sd = math.sqrt(sum((v - mu) ** 2 for v in vals) / len(vals))
    approx = 4.343 / math.sqrt(K)
    print(f"  K={K:5d}: std {sd:5.2f} dB (approx 4.34/sqrt(K) = {approx:5.2f} dB), mean bias {mu:+5.2f} dB")
    if K >= 10:
        check(f"std ~ 4.34/sqrt(K) at K={K}", abs(sd - approx) / approx < 0.15)
K3 = 2 * (3 * 4.343 / 1.0) ** 2
print(f"  -> before/after difference has std sqrt(2)*4.34/sqrt(K); a 1 dB change at 3 sigma needs K >= {K3:.0f} per reading")
check("K for 1 dB at 3 sigma (difference) ~ 340", 330 < K3 < 350)

# ------------------------------------------------------------- 7. GSM buzz
print("\n7. GSM TDMA: frame 4.615 ms (8 slots of 577 us)")
frame = 120e-3 / 26
print(f"  frame rate {1/frame:.1f} Hz, slot {frame/8*1e6:.0f} us, duty {1/8:.3f}")
check("GSM frame rate 216.7 Hz", abs(1 / frame - 216.67) < 0.05)

# ------------------------------------------------------------- 8. PA supply current vs magnetometer
print("\n8. Magnetic field of PA supply current bursts at a magnetometer (isolated straight wire, upper bound)")
MU0 = 4e-7 * math.pi
for I in (0.5, 1.0, 2.0):
    row = ", ".join(f"{r*100:.0f} cm: {MU0*I/(2*math.pi*r)*1e6:5.1f} uT" for r in (0.01, 0.02, 0.05, 0.10))
    print(f"  {I:3.1f} A: {row}")
# trace over a ground plane at height h: field at distance r >> h ~ mu0 I h /(pi r^2) (two-wire)
h = 0.2e-3
for r in (0.01, 0.02, 0.05):
    b = MU0 * 1.0 * h / (math.pi * r ** 2)  # trace + image current at -h: two-wire line, spacing 2h
    print(f"  1 A trace 0.2 mm over its return plane, {r*100:.0f} cm away: ~{b*1e9:6.1f} nT")
check("1 A at 2 cm = 10 uT (isolated wire)", abs(MU0 * 1 / (2 * math.pi * 0.02) * 1e6 - 10.0) < 0.01)

print("\nRESULT:", "ALL PASS" if not FAIL else f"{len(FAIL)} FAIL: {FAIL}")
