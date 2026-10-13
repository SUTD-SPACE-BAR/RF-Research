#!/usr/bin/env python3
"""
e10_coax.py — numbers for kb/18-components-parts/coax-and-connector-practicalities.md (W5-E10).

 1. 75-ohm cable on a 50-ohm system: single mismatch (Gamma 0.2, 0.18 dB) and the two-ended case
    (50 / 75-ohm line / 50): S21 ripple vs electrical length, worst case at odd lambda/4 (0.69 dB).
 2. Adapter chains: worst-case and RSS mismatch of N adapters at VSWR 1.1-1.25, plus insertion loss.
 3. Phase matching: millimetres per electrical degree at 433/915/1575/2450 MHz for VF 0.66/0.70/0.85.
 4. NanoVNA cable tests: velocity factor from the first quarter-wave S11 dip of an open stub; one-way
    loss = RL/2 with an open/short at the far end; TDR resolution and alias-free range.
 5. Bend radius ratios from the LMR-400 datasheet (25 mm once / 102 mm repeated, OD 10.3 mm).
 6. U.FL mechanical numbers: shock rating in g; pull-force limit vs a pigtail's own mass under g.
 7. Mating-cycle budget.

Run:  python3 tools/verify/e10_coax.py
"""
import cmath
import math

C = 299792458.0
FAIL = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAIL.append(name)


def ml_db(g):
    return -10 * math.log10(1 - g * g)


# ------------------------------------------------------------ 1. 75 on 50
print("1. 75-ohm cable in a 50-ohm system")
g = (75 - 50) / (75 + 50)
print(f"  single interface: Gamma {g:.3f}, SWR {(1+g)/(1-g):.2f}, mismatch loss {ml_db(g):.3f} dB")
check("75/50 mismatch loss 0.177 dB", abs(ml_db(g) - 0.177) < 0.001)


def s21_line(z0_line, zs, zl, theta):
    """|S21|^2 (transducer gain) of a lossless line of electrical length theta between zs and zl."""
    A = math.cos(theta)
    B = 1j * z0_line * math.sin(theta)
    Cc = 1j * math.sin(theta) / z0_line
    D = math.cos(theta)
    s21 = 2 * math.sqrt(zs.real * zl.real) / (A * zl + B + Cc * zs * zl + D * zs)
    return abs(s21) ** 2


worst = 0
for k in range(0, 181):
    th = math.radians(k)
    loss = -10 * math.log10(s21_line(75.0, 50 + 0j, 50 + 0j, th))
    worst = max(worst, loss)
print(f"  50 -> 75-ohm line -> 50: transmission ripple 0 dB (lambda/2 multiples) to {worst:.3f} dB (odd lambda/4)")
zin = 75 ** 2 / 50
gq = (zin - 50) / (zin + 50)
check("worst case equals mismatch of 112.5 ohm (0.69 dB)", abs(worst - ml_db(gq)) < 0.005)

# ------------------------------------------------------------ 2. adapters
print("\n2. Adapter chains")
for vswr in (1.1, 1.15, 1.25):
    gg = (vswr - 1) / (vswr + 1)
    for n in (1, 2, 3, 4):
        worst_g = min(n * gg, 0.99)
        rss_g = math.sqrt(n) * gg
        il = 0.05 * n
        print(f"  VSWR {vswr} x{n}: worst |G| {worst_g:.3f} ({ml_db(worst_g):.2f} dB), RSS |G| {rss_g:.3f} "
              f"({ml_db(rss_g):.2f} dB), + IL ~{il:.2f} dB at 0.05 dB/adapter")
g12 = (1.2 - 1) / 2.2
check("three VSWR-1.2 adapters worst-case mismatch ~0.34 dB", abs(ml_db(3 * g12) - 0.34) < 0.02)

# ------------------------------------------------------------ 3. phase matching
print("\n3. Physical length per electrical degree: l = VF * lambda0 / 360")
for f in (433e6, 915e6, 1575.42e6, 2450e6):
    row = []
    for vf in (0.66, 0.70, 0.85):
        row.append(f"VF {vf}: {vf*C/f/360*1e3:5.2f} mm/deg")
    print(f"  {f/1e6:7.2f} MHz: " + ", ".join(row))
check("433 MHz VF 0.66: 1.27 mm per degree", abs(0.66 * C / 433e6 / 360 * 1e3 - 1.270) < 0.005)
print("  delay per metre: VF 0.66 -> %.3f ns/m, VF 0.85 -> %.3f ns/m" % (1e9 / (0.66 * C), 1e9 / (0.85 * C)))

# ------------------------------------------------------------ 4. NanoVNA tests
print("\n4. NanoVNA cable tests")
L = 1.000
f1 = 0.66 * C / (4 * L)
print(f"  1.000 m open stub of VF 0.66: first S11 phase -180 deg / dip at {f1/1e6:.2f} MHz; VF = 4 L f1 / c")
check("VF recovered", abs(4 * L * f1 / C - 0.66) < 1e-9)
for rl in (0.5, 2.0, 6.0, 20.0):
    print(f"  open far end, |S11| = -{rl:4.1f} dB -> one-way loss {rl/2:5.2f} dB "
          f"(error from 30 dB cal directivity up to ±{20*math.log10(1+10**(-30/20)/10**(-rl/20)):.2f} dB in RL)")
for span, npts, vf in ((900e6, 101, 0.66), (900e6, 401, 0.66), (1.5e9, 1024, 0.66), (6e9, 1024, 0.70)):
    dres = vf * C / (2 * span)
    drange = vf * C * (npts - 1) / (2 * span)
    print(f"  TDR span {span/1e6:6.0f} MHz, {npts} pts, VF {vf}: resolution ~{dres*100:5.1f} cm (before "
          f"windowing), alias-free length {drange:6.1f} m")
check("900 MHz span VF 0.66 resolution 11 cm", abs(0.66 * C / (2 * 900e6) - 0.110) < 0.001)

# ------------------------------------------------------------ 5. bend radius
print("\n5. Bend radius ratios, LMR-400 (OD 10.3 mm): once 25 mm, repeated 102 mm")
print(f"  once = {25/10.3:.1f} x OD, repeated = {102/10.3:.1f} x OD")
check("LMR-400 repeated bend ~10x OD", 9.5 < 102 / 10.3 < 10.5)

# ------------------------------------------------------------ 6. U.FL mechanics
print("\n6. U.FL: shock rating 735 m/s^2 for 11 ms = %.0f g; cable pull limit 2-4 N (1.13 mm assemblies)" % (735 / 9.80665))
m = 0.003  # 3 g of 100 mm pigtail (1.13 mm cable ~ 2-3 g/m plus plug)... use generous 3 g
for gload in (10, 20, 50):
    F = m * 9.80665 * gload
    print(f"  {m*1e3:.0f} g of unsupported cable at {gload:2d} g -> {F:.2f} N (limit 2 N)")
check("U.FL shock rating ~75 g", abs(735 / 9.80665 - 74.9) < 0.2)
print("  -> at deployment-shock levels (tens of g) an unsupported pigtail's own mass approaches the 2 N limit, and"
      " whipping, snagging and harness tension add more. Tie the cable down within ~20 mm of the plug and use a"
      " locking (MHF-LK) variant.")
check("3 g pigtail at 50 g is within 40 % of the 2 N limit", 0.003 * 9.80665 * 50 > 0.6 * 2.0)

# ------------------------------------------------------------ 7. mating cycles
print("\n7. Mating-cycle budget: U.FL 30 cycles; if each integration test unplugs/replugs once (2 ops = 1 cycle)")
for tests in (10, 30, 60):
    print(f"  {tests} test sessions -> {tests} cycles ({100*tests/30:.0f} % of rated life)")

print("\nRESULT:", "ALL PASS" if not FAIL else f"{len(FAIL)} FAIL: {FAIL}")
