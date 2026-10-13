#!/usr/bin/env python3
"""Verification for kb/06-rf-circuits/co-site-interference-and-transmitter-intermod.md  (W5-E7)

 A. Antenna isolation (ITU-R M.2244): horizontal I_H = 22 + 20 log(d/lambda) - (Gt + Gr) (Friis), vertical
    I_V = 28 + 40 log(d/lambda); reproduce the report's 465 MHz table; slant interpolation; examples
 B. Transmitter (reverse) intermodulation: two-signal simulation of a saturated PA: 2f1-f2 grows 1 dB/dB
    with the injected interferer, 2f2-f1 grows 2 dB/dB; hard-limiter turnaround ~6 dB; ETSI EN 300 086
    40/70 dB classes -> required conversion loss / isolator isolation
 C. Desense of a LoRa receiver by a nearby transmitter: blocking and transmitter-noise budgets vs distance
 D. Multi-team frequency plans: third-order IM hits on equally spaced vs Golomb-ruler channel sets
 E. On-board coexistence: harmonics and IM products (order <= 5) of 434.125 / 920.125 MHz LoRa and
    2.4 GHz Wi-Fi landing in GNSS bands
Run: python3 tools/verify/rf2_cosite.py   (runtime ~5 s)
"""
import numpy as np, sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rf2_common import check, finish

c = 299792458.0

print("=== A. antenna isolation")
check("Friis constant 20 log10(4 pi) = 21.98 dB (the '22' in I_H)", abs(20 * np.log10(4 * np.pi) - 21.98) < 0.01)
IH = lambda d, lam, G=0.0: 22 + 20 * np.log10(d / lam) - G
IV = lambda d, lam: 28 + 40 * np.log10(d / lam)
lam465 = c / 465e6
dh = [lam465 * 10 ** ((I - 22) / 20) for I in (30, 45, 60)]
dv = [lam465 * 10 ** ((I - 28) / 40) for I in (30, 45, 60)]
print(f"  465 MHz: horizontal 30/45/60 dB at {dh[0]:.2f}/{dh[1]:.2f}/{dh[2]:.2f} m; vertical at {dv[0]:.2f}/{dv[1]:.2f}/{dv[2]:.2f} m")
check("reproduces ITU-R M.2244 Table 1 (1.62/9.11/51.25 m) and Table 2 (0.72/1.72/4.07 m)",
      np.allclose(dh, [1.62, 9.11, 51.25], rtol=0.01) and np.allclose(dv, [0.72, 1.72, 4.07], rtol=0.01))
for f, name in ((434.125e6, "434 MHz"), (920.125e6, "920 MHz")):
    lam = c / f
    print(f"  {name}: two 2 dBi whips 5 m apart side by side: {IH(5, lam, 4):.1f} dB; 20 m: {IH(20, lam, 4):.1f} dB;"
          f" stacked 2 m vertically: {IV(2, lam):.1f} dB (valid d > 10 lambda = {10*lam:.1f} m? {'yes' if 2 > 10*lam else 'no'})")
Is = lambda Iv, Ih, alpha: (Iv - Ih) * alpha / 90 + Ih
print(f"  slant 45 deg, 434 MHz, Ih(10 m)={IH(10, c/434.125e6):.1f}, Iv(10 m)={IV(10, c/434.125e6):.1f} -> {Is(IV(10, c/434.125e6), IH(10, c/434.125e6), 45):.1f} dB")

print("\n=== B. transmitter (reverse) intermodulation")
fs = 1.0; N = 2 ** 16
n = np.arange(N)
k1, k2 = 2000, 2100            # bins: own carrier f1, interferer f2 (offset 100 bins)
f1, f2 = k1 / N, k2 / N


def pa(x, drive):
    return np.tanh(drive * x) / np.tanh(drive)    # saturating device, normalised


def tones(y):
    Y = np.fft.rfft(y) / (N / 2)
    return {k: abs(Y[k]) for k in (k1, k2, 2 * k1 - k2, 2 * k2 - k1)}


A1 = 1.0
levels = np.array([-40, -35, -30, -25, -20])
res = []
for drive in (0.5, 5.0):
    rows = []
    for L in levels:
        A2 = A1 * 10 ** (L / 20)
        x = A1 * np.cos(2 * np.pi * f1 * n) + A2 * np.cos(2 * np.pi * f2 * n)
        t = tones(pa(x, drive))
        rows.append([20 * np.log10(t[k1]), 20 * np.log10(t[k2]), 20 * np.log10(t[2 * k1 - k2]), 20 * np.log10(t[2 * k2 - k1])])
    rows = np.array(rows)
    s_main = np.polyfit(levels, rows[:, 2], 1)[0]; s_other = np.polyfit(levels, rows[:, 3], 1)[0]
    turn = (levels[2] + 20 * np.log10(A1)) - (rows[2, 2] - rows[2, 0] + 0)   # interferer rel. carrier minus IM rel. carrier
    print(f"  drive {drive}: slope of 2f1-f2 {s_main:.2f} dB/dB, of 2f2-f1 {s_other:.2f} dB/dB;"
          f" interferer at -30 dBc -> 2f1-f2 at {rows[2,2]-rows[2,0]:.1f} dBc, 2f2-f1 at {rows[2,3]-rows[2,0]:.1f} dBc;"
          f" 'turnaround' (conversion) loss {turn:.1f} dB")
    res.append((drive, s_main, s_other, turn))
check("2f1-f2 product follows the injected interferer 1 dB/dB, 2f2-f1 at 2 dB/dB", abs(res[1][1] - 1) < 0.05 and abs(res[1][2] - 2) < 0.1)
check("hard-saturated device: conversion loss to 2f1-f2 ~ 6 dB (limiter theory)", 5 < res[1][3] < 8)
# ETSI EN 300 086: interferer ~30 dB below carrier at the TX port; IM attenuation >= 40 dB (general) / 70 dB (special sites)
for cls in (40, 70):
    need = cls - 30
    print(f"  ETSI class {cls} dB with interferer at -30 dBc: total interferer->IM conversion loss >= {need} dB;"
          f" with a 6 dB device turnaround, isolator/filter isolation >= {need-6} dB")
check("70 dB class needs ~34 dB of isolation beyond a 6 dB turnaround (one or two circulator stages)", 70 - 30 - 6 == 34)

print("\n=== C. desense of a LoRa receiver by a nearby 1 W transmitter")
f = 434.125e6; lam = c / f
Ptx = 30.0; G = 2.0 + 2.0
sens = -137.0 + 3          # SX126x SF12/BW125 sensitivity + 3 dB (blocking reference)
for off, block_db in ((1e6, 88), (2e6, 90), (10e6, 99)):
    Pb_max = sens + block_db
    d_need = lam * 10 ** ((Ptx - Pb_max - 22 + G) / 20)
    print(f"  blocker {off/1e6:.0f} MHz away: SX1262 blocking {block_db} dB -> tolerable {Pb_max:.0f} dBm; 1 W, 2+2 dBi, free space:"
          f" separation >= {d_need:.0f} m")
    if off == 1e6:
        d1 = d_need
check("1 W at 1 MHz offset needs ~>100 m separation to keep SF12 within 3 dB (blocking-limited)", d1 > 100)
for Ltx in (-110, -120, -130, -140):
    # transmitter noise at the victim channel: Ptx + L + 10log(125k) - I <= floor(-117 dBm, NF 6) - 6 dB
    floor = -174 + 6 + 10 * np.log10(125e3)
    I_need = Ptx + Ltx + 10 * np.log10(125e3) - (floor - 6)
    d_need = lam * 10 ** ((I_need - 22 + G) / 20)
    print(f"  transmitter noise {Ltx} dBc/Hz at the victim channel: isolation >= {I_need:.0f} dB -> {d_need:.0f} m free space")
    if Ltx == -120:
        dn120 = d_need
check("TX noise of -120 dBc/Hz needs > 1 km free-space separation (cannot be filtered at the victim)", dn120 > 1000)

print("\n=== D. multi-team channel plans and 3rd-order IM")


def im3_hits(ch):
    s = set(ch); hits = set()
    for a, b in itertools.permutations(ch, 2):
        p = 2 * a - b
        if p in s and p not in (a, b):
            hits.add(('2a-b', a, b, p))
    for a, b, cc in itertools.permutations(ch, 3):
        if a < b:
            p = a + b - cc
            if p in s and p not in (a, b, cc):
                hits.add(('a+b-c', a, b, cc, p))
    return hits


grid = 0.125   # MHz channel grid (125 kHz LoRa)
equal = [0, 2, 4, 6, 8]                 # equally spaced, 250 kHz apart
golomb = [0, 1, 4, 9, 11]               # Golomb ruler (all differences distinct), fits 12 grid positions
for name, ch in (("equal spacing", equal), ("Golomb ruler", golomb)):
    h = im3_hits(ch)
    fr = [433.175 + grid * k for k in ch]
    print(f"  5 teams, {name}: channels {', '.join(f'{x:.3f}' for x in fr)} MHz -> {len(h)} third-order IM hits on used channels")
    if name == "Golomb ruler":
        hg = len(h)
    else:
        he = len(h)
check("equal spacing gives IM3 hits; a Golomb-ruler plan gives none", he > 0 and hg == 0)
check("Golomb plan fits inside 433.05-434.79 MHz with 125 kHz channels", 433.175 + grid * 11 + 0.0625 <= 434.79)
diffs = [b - a for a, b in itertools.combinations(golomb, 2)]
check("Golomb ruler has all pairwise differences distinct", len(diffs) == len(set(diffs)))

rulers = {2: [0, 1], 3: [0, 1, 3], 4: [0, 1, 4, 6], 5: [0, 1, 4, 9, 11], 6: [0, 1, 4, 10, 12, 17], 7: [0, 1, 4, 10, 18, 23, 25]}
allok = True
for m, rl in rulers.items():
    d_ = [b - a for a, b in itertools.combinations(rl, 2)]
    ok = len(d_) == len(set(d_)) and len(im3_hits(rl)) == 0
    allok &= ok
    for g_khz in (125, 250):
        span = rl[-1] * g_khz / 1e3 + g_khz / 1e3      # MHz incl. half-channel each side
        print(f"  {m} channels, Golomb {rl} on a {g_khz} kHz grid: span {span:.3f} MHz -> "
              f"{'fits' if span <= 1.74 else 'does NOT fit'} in 433.05-434.79 MHz")
check("optimal Golomb rulers up to 7 marks are IM3-free", allok)

print("\n=== E. on-board coexistence: products landing in GNSS bands")
gnss = {"L5/E5 1164-1215": (1164, 1215), "L2/E6/G2 1215-1300": (1215, 1300), "L1/E1/B1/G1 1559-1610": (1559, 1610)}
fA, fB = 434.125, 920.125
wifi = {"Wi-Fi ch1": (2401, 2423), "Wi-Fi ch6": (2426, 2448), "Wi-Fi ch11": (2451, 2473)}
found = []
for a in range(0, 6):
    for b in range(-5, 6):
        if a + abs(b) == 0 or a + abs(b) > 5:
            continue
        p = a * fA + b * fB
        for gname, (lo, hi) in gnss.items():
            if lo <= p <= hi:
                found.append((f"{a}x434.125 {'+' if b>=0 else '-'} {abs(b)}x920.125", a + abs(b), p, gname))
for wname, (wlo, whi) in wifi.items():
    for a in range(-4, 5):
        for b in range(-4, 5):
            order = 1 + abs(a) + abs(b)
            if order > 5 or (a == 0 and b == 0):
                continue
            lo = wlo + a * fA + b * fB; hi = whi + a * fA + b * fB
            for gname, (glo, ghi) in gnss.items():
                if hi >= glo and lo <= ghi:
                    found.append((f"{wname} {'+' if a>=0 else '-'}{abs(a)}x434.125 {'+' if b>=0 else '-'}{abs(b)}x920.125",
                                  order, (lo + hi) / 2, gname))
for fd in sorted(found, key=lambda x: x[1]):
    print(f"  order {fd[1]}: {fd[0]:45s} -> {fd[2]:7.1f} MHz in {fd[3]}")
hit3 = [fd for fd in found if fd[1] == 3 and 'Wi-Fi ch6' in fd[0] and 'L1' in fd[3]]
check("Wi-Fi ch 6 minus 2 x 434.125 MHz (3rd order) overlaps the L1/E1/B1 band", len(hit3) > 0)
check("3 x 434.125 = 1302.4 MHz clears the 1215-1300 MHz RNSS band (canonical page)", 3 * fA > 1300)

finish()
