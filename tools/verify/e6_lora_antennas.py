#!/usr/bin/env python3
"""
e6_lora_antennas.py -- checks for kb/15-lora-ism-radios/choosing-and-judging-lora-antennas.md

1. Collinear "high-gain omni" model: N half-wave dipoles stacked vertically, uniform in-phase
   currents, centre spacing s. Directivity by numerical pattern integration (no mutual-coupling or
   loss model -> an upper bound on what a real collinear of that length achieves). Best spacing,
   peak gain, elevation half-power beamwidth, and gain at given elevation angles.
2. What a rocket overhead looks like to each omni: elevation = atan(h / D) for a 10 km apogee seen
   from 2 / 5 km, and the gain each antenna offers in that direction.
3. Size check for gain claims: minimum collinear length for a claimed omni gain at 433/868/915 MHz,
   and the 5.16 dBi "monopole over an infinite ground" figure that vendors sometimes quote.
4. Mismatch loss vs VSWR / return loss (how much a mistuned antenna really costs).
5. Feeder trade: a +3 dB antenna upgrade on the end of a lossy pigtail/extension.
6. Comparative RSSI (A/B) tests: samples needed for a given fading spread; Monte-Carlo check that
   interleaved A/B swaps are unbiased under slow drift while "all A then all B" is biased.

Run: python3 tools/verify/e6_lora_antennas.py   (PASS/FAIL per check, ~3 s)
"""
import numpy as np
from scipy.stats import norm

results = []
rng = np.random.default_rng(42)


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")


th = np.linspace(1e-6, np.pi - 1e-6, 20001)       # polar angle from the antenna axis (vertical)
dth = th[1] - th[0]


def pattern(n, s):
    """|E|^2 of n collinear half-wave dipoles, centre spacing s (wavelengths)"""
    e_el = np.cos(np.pi / 2 * np.cos(th)) / np.sin(th)
    k = 2 * np.pi
    pos = (np.arange(n) - (n - 1) / 2) * s
    af = np.sum(np.exp(1j * k * np.outer(pos, np.cos(th))), axis=0)
    return (e_el * np.abs(af)) ** 2


def directivity(p):
    return 4 * np.pi * np.max(p) / (2 * np.pi * np.sum(p * np.sin(th)) * dth)


def gain_at_elev(p, elev_deg):
    """directivity (dBi) toward elevation elev_deg (0 = horizon, 90 = zenith)"""
    d = directivity(p)
    theta = np.radians(90 - elev_deg)
    val = np.interp(theta, th, p) / np.max(p)
    return 10 * np.log10(d * max(val, 1e-12))


def hpbw(p):
    pn = p / np.max(p)
    i0 = np.argmax(pn)
    # walk up from the peak (towards theta = 0) until -3 dB
    j = i0
    while j > 0 and pn[j] > 0.5:
        j -= 1
    return 2 * np.degrees(th[i0] - th[j])


# ---------------------------------------------------------------- 1. collinears
print("\n§1 Collinear arrays of half-wave dipoles (uniform, in phase)")
print(f"{'N':>3s} {'best s (lambda)':>16s} {'D (dBi)':>8s} {'HPBW elev (deg)':>16s} {'length (lambda)':>16s} {'D at s=0.5 (dBi)':>17s}")
col = {}
for n in range(1, 9):
    if n == 1:
        p = pattern(1, 0.5)
        best_s = 0.0
    else:
        ss = np.linspace(0.5, 1.0, 51)
        ds = [directivity(pattern(n, s)) for s in ss]
        best_s = ss[int(np.argmax(ds))]
        p = pattern(n, best_s)
    d = directivity(p)
    d05 = directivity(pattern(n, 0.5))
    length = 0.5 + (n - 1) * best_s if n > 1 else 0.5
    col[n] = dict(s=best_s, D=10 * np.log10(d), bw=hpbw(p), L=length, p=p, D05=10 * np.log10(d05))
    print(f"{n:3d} {best_s:16.2f} {col[n]['D']:8.2f} {col[n]['bw']:16.1f} {length:16.2f} {col[n]['D05']:17.2f}")
check("single half-wave dipole: 2.15 dBi, 78 deg elevation beamwidth", abs(col[1]['D'] - 2.15) < 0.02 and abs(col[1]['bw'] - 78.1) < 0.5,
      f"({col[1]['D']:.2f} dBi, {col[1]['bw']:.1f} deg)")
check("2 elements: ~5 dBi; 4 elements: ~8.5 dBi; 8 elements: ~11.6 dBi (upper bounds, best spacing)",
      4.5 < col[2]['D'] < 5.8 and 8.0 < col[4]['D'] < 9.2 and 11.0 < col[8]['D'] < 12.3,
      f"({col[2]['D']:.1f}, {col[4]['D']:.1f}, {col[8]['D']:.1f} dBi)")
check("elevation beamwidth shrinks roughly as 1/N (8 el: < 12 deg)", col[8]['bw'] < 12 and col[4]['bw'] < 22,
      f"(4 el {col[4]['bw']:.1f} deg, 8 el {col[8]['bw']:.1f} deg)")

# ---------------------------------------------------------------- 2. rocket overhead
print("\n§2 Gain toward the rocket (vertical omni at the ground station)")
print("  realistic collinears: s = 0.75 lambda (phasing-coil type, no grating lobe) -- best-s patterns above have")
print("  near-axis grating lobes; §3 searches all spacings for the size bound")
real = {1: pattern(1, 0.5)}
for n in (2, 4, 8):
    real[n] = pattern(n, 0.75)
for n in (2, 4, 8):
    print(f"  N = {n}, s = 0.75: peak {10 * np.log10(directivity(real[n])):.2f} dBi, elevation HPBW {hpbw(real[n]):.1f} deg")
geoms = [("pad, rocket at 100 m from 2 km", 100, 2000), ("1 km altitude from 2 km", 1000, 2000),
         ("3 km altitude from 2 km", 3000, 2000), ("apogee 10 km from 5 km", 10000, 5000),
         ("apogee 10 km from 2 km", 10000, 2000), ("landed rocket 5 km away (horizon)", 0, 5000)]
print(f"{'geometry':36s} {'elev':>6s} " + " ".join(f"{'N=' + str(n):>8s}" for n in (1, 2, 4, 8)))
g_tab = {}
for name, h, dist in geoms:
    el = np.degrees(np.arctan2(h, dist))
    row = [gain_at_elev(real[n], el) for n in (1, 2, 4, 8)]
    g_tab[name] = (el, row)
    print(f"{name:36s} {el:6.1f} " + " ".join(f"{v:8.1f}" for v in row))
els = np.linspace(5, 80, 751)
worst = {n: min(gain_at_elev(real[n], e) for e in els) for n in (1, 2, 4, 8)}
below0 = {n: np.mean([gain_at_elev(real[n], e) < 0 for e in els]) for n in (1, 2, 4, 8)}
for n in (1, 2, 4, 8):
    print(f"  N = {n}: worst gain over 5-80 deg elevation {worst[n]:6.1f} dBi; fraction of 5-80 deg below 0 dBi: {below0[n]:.2f}")
el, row = g_tab["landed rocket 5 km away (horizon)"]
check("at the horizon the 8-element collinear wins by ~7 dB over the dipole", 6 < row[3] - row[0] < 9,
      f"({row[3] - row[0]:.1f} dB)")
el, row = g_tab["apogee 10 km from 2 km"]
check("toward apogee (79 deg) every vertical omni is >= 12 dB below its own peak", all(
      10 * np.log10(directivity(real[n])) - row[i] >= 12 for i, n in enumerate((1, 2, 4, 8))),
      f"(dipole {row[0]:.1f}, N2 {row[1]:.1f}, N4 {row[2]:.1f}, N8 {row[3]:.1f} dBi)")
check("the dipole has no null between 5 and 80 deg; collinears have deep nulls there (worst < -20 dBi)",
      worst[1] > -16 and worst[4] < -20 and worst[8] < -20,
      f"(worst: dipole {worst[1]:.1f}, N4 {worst[4]:.1f}, N8 {worst[8]:.1f} dBi)")
check("the 4- and 8-element collinears are below 0 dBi over most of 5-80 deg elevation (> 70 %)",
      below0[4] > 0.7 and below0[8] > 0.7, f"(N4 {below0[4]:.2f}, N8 {below0[8]:.2f}; dipole {below0[1]:.2f})")
el, row = g_tab["1 km altitude from 2 km"]
check("early boost (27 deg elevation): dipole beats the 4- and 8-element omnis", row[0] > row[2] and row[0] > row[3],
      f"(dipole {row[0]:.1f}, N4 {row[2]:.1f}, N8 {row[3]:.1f} dBi)")

# ---------------------------------------------------------------- 3. size check for gain claims
print("\n§3 Minimum radiator length for a claimed omni gain (search over N = 1..10, s = 0.5..1.0 lambda)")
grid = []
for n in range(1, 11):
    for sp in ([0.5] if n == 1 else np.linspace(0.5, 1.0, 26)):
        dd = 10 * np.log10(directivity(pattern(n, sp)))
        grid.append((0.5 + (n - 1) * sp, dd, n, sp))
claims = (3, 5, 6, 8, 10)
print(f"{'claim (dBi)':>11s} {'min length (lambda)':>20s} {'N, s':>12s} {'433 MHz (cm)':>13s} {'868 MHz (cm)':>13s} {'915 MHz (cm)':>13s} {'line source 2L/lambda (dBi)':>28s}")
need = {}
for c in claims:
    ok = [g for g in grid if g[1] >= c]
    L, dd, n, sp = min(ok, key=lambda g: g[0])
    need[c] = (n, L)
    print(f"{c:11d} {L:20.2f} {f'{n}, {sp:.2f}':>12s} {L * 69.09:13.0f} {L * 34.54:13.0f} {L * 32.76:13.0f} {10 * np.log10(2 * L):28.1f}")
check("an honest 8 dBi omni at 915 MHz needs >= ~2.5 lambda (~80 cm) of radiator, before losses", need[8][1] * 32.76 > 75,
      f"({need[8][1]:.2f} lambda = {need[8][1] * 32.76:.0f} cm)")
check("even 5 dBi needs >= ~1.2 lambda (two stacked half-waves): ~40 cm at 915 MHz, ~85 cm at 433 MHz",
      need[5][0] >= 2 and need[5][1] > 1.15, f"({need[5][1]:.2f} lambda)")
check("cross-check: uniform line source D ~ 2L/lambda agrees within ~1.5 dB for the 8-10 dBi cases",
      all(abs(10 * np.log10(2 * need[c][1]) - c) < 1.6 for c in (8, 10)))
mono_inf = 10 * np.log10(2 * 10 ** (col[1]['D'] / 10))
check("quarter-wave monopole over an INFINITE perfect ground = 5.16 dBi (half-space), not achievable on a small board",
      abs(mono_inf - 5.16) < 0.02, f"({mono_inf:.2f} dBi)")

# ---------------------------------------------------------------- 4. mismatch loss
print("\n§4 Mismatch loss")
print(f"{'VSWR':>5s} {'|Gamma|':>8s} {'RL (dB)':>8s} {'mismatch loss (dB)':>19s}")
ml = {}
for v in (1.2, 1.5, 2.0, 3.0, 5.0, 10.0):
    g = (v - 1) / (v + 1)
    ml[v] = -10 * np.log10(1 - g ** 2)
    print(f"{v:5.1f} {g:8.3f} {-20 * np.log10(g):8.1f} {ml[v]:19.2f}")
check("VSWR 2 costs only 0.51 dB; VSWR 3 1.25 dB; VSWR 5 2.55 dB", abs(ml[2.0] - 0.512) < 0.005 and
      abs(ml[3.0] - 1.249) < 0.005 and abs(ml[5.0] - 2.553) < 0.005)
check("an antenna at VSWR 10 (e.g. a 915 MHz whip used at 433 MHz) loses ~4.8 dB of mismatch alone", abs(ml[10.0] - 4.81) < 0.02)

# ---------------------------------------------------------------- 5. feeder trade
print("\n§5 Feeder loss vs antenna upgrade (loss per 10 m from 03/coax-and-cables, interpolated datasheets)")
loss10 = {"RG-174": {433: 6.4, 915: 10.0}, "RG-316": {433: 7.2, 915: 11.8}, "RG-58": {433: 2.9, 915: 4.5},
          "LMR-240": {433: 1.7, 915: 2.5}, "LMR-400": {433: 0.87, 915: 1.3}}
for cab, d in loss10.items():
    print(f"  {cab:8s} 3 m: {0.3 * d[433]:4.1f} dB at 433 MHz, {0.3 * d[915]:4.1f} dB at 915 MHz")
check("3 m of RG-174 at 915 MHz (3.0 dB) cancels a +3 dB antenna upgrade", abs(0.3 * loss10['RG-174'][915] - 3.0) < 0.05)
check("range factor of a net +3 dB (free space) = x1.41; of -3 dB = x0.71", abs(10 ** (3 / 20) - 1.413) < 0.001 and abs(10 ** (-3 / 20) - 0.708) < 0.001)

# ---------------------------------------------------------------- 6. A/B RSSI test statistics
print("\n§6 Comparative RSSI test: samples per antenna for 80 % power at alpha = 0.05 (two-sided)")
z = norm.ppf(0.975) + norm.ppf(0.80)
print(f"{'sigma (dB)':>10s} " + " ".join(f"{'D=' + str(dd) + ' dB':>9s}" for dd in (0.5, 1, 2, 3)))
nreq = {}
for sig in (1, 2, 4, 6, 8):
    row = []
    for dd in (0.5, 1, 2, 3):
        n = int(np.ceil(2 * z ** 2 * sig ** 2 / dd ** 2))
        nreq[(sig, dd)] = n
        row.append(n)
    print(f"{sig:10d} " + " ".join(f"{v:9d}" for v in row))
check("formula: sigma 4 dB, difference 2 dB -> 63 packets per antenna", nreq[(4, 2)] == 63)


def mc_power(sig, delta, n, drift_per_sample=0.0, interleave=True, trials=2000):
    """fraction of trials in which a two-sample t-test (alpha 0.05) detects delta; mean estimate bias"""
    hits, est = 0, []
    for _ in range(trials):
        total = 2 * n
        drift = np.cumsum(rng.normal(0, drift_per_sample, total)) if drift_per_sample > 0 else np.zeros(total)
        noise = rng.normal(0, sig, total)
        is_b = (np.arange(total) % 2 == 1) if interleave else (np.arange(total) >= n)
        rssi = -100 + drift + noise + delta * is_b
        rssi = np.round(rssi)                      # 1 dB RSSI quantisation (SX126x reports integer dBm-ish)
        a, b = rssi[~is_b], rssi[is_b]
        diff = b.mean() - a.mean()
        se = np.sqrt(a.var(ddof=1) / n + b.var(ddof=1) / n)
        est.append(diff)
        hits += abs(diff / se) > 1.96
    return hits / trials, np.mean(est)


pw, bias = mc_power(4, 2, nreq[(4, 2)])
check("Monte-Carlo: 63 packets/antenna at sigma 4 dB detect a 2 dB difference ~80 % of the time (1 dB RSSI steps)",
      0.74 < pw < 0.86, f"(power {pw:.2f}, mean estimate {bias:.2f} dB)")
pw_i, b_i = mc_power(4, 0.0, 100, drift_per_sample=0.15, interleave=True)
pw_blk, b_blk = mc_power(4, 0.0, 100, drift_per_sample=0.15, interleave=False)
check("with slow drift and NO real difference, interleaved A/B stays near 5 % false alarms",
      pw_i < 0.12, f"(false-alarm rate {pw_i:.2f}, mean diff {b_i:+.2f} dB)")
check("... while 'all A, then all B' flags a fake difference far more often", pw_blk > 2 * pw_i,
      f"(false-alarm rate {pw_blk:.2f}, |mean| spread larger)")

print(f"\n{sum(results)}/{len(results)} PASS")
print("ALL PASS" if all(results) else "SOME FAIL")
