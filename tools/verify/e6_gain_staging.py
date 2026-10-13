#!/usr/bin/env python3
"""
e6_gain_staging.py -- checks for kb/14-sdr-dsp/sdr-gain-staging-and-reception-recipes.md

Model: antenna -> analog chain (fixed noise figure NF, gain G) -> 8-bit complex ADC (full scale
0 dBFS, extra converter noise so that ENOB ~ 7, as for the RTL2832U in sdr-hardware-survey.md).
This is a deliberately simple model of an RTL-SDR-class receiver. Real tuners also change NF and
linearity with the gain index, so treat the numbers as an illustration of the *shape* of the trade.

1. Analytic: input-referred noise penalty of the ADC vs how far the analog noise sits above the
   ADC floor ("floor lift" X dB): penalty = 10 log10(1 + 10^(-X/10)). Each extra dB of gain beyond
   the point where analog noise dominates costs 1 dB of headroom and buys almost no sensitivity.
2. Monte-Carlo dynamic-range demonstration: a weak tone (-115 dBm) next to a strong in-band signal
   (-45 dBm) through the 8-bit ADC at different gains. SNR of the weak tone rises with gain, plateaus
   at the analog limit, and collapses when the strong signal clips the ADC (clipping spurs + noise).
3. The librtlsdr R820T/R828D gain table: 29 settings 0-49.6 dB built from alternating LNA and mixer
   steps (VGA fixed at 16.3 dB in manual mode, 26.5 dB with tuner AGC), from osmocom librtlsdr source.
4. Where broadcast-FM harmonics and tuner LO-harmonic responses land relative to common
   hobby bands (137-138, 144-146, 161.975/162.025, 433.05-434.79, 1090 MHz).
5. When a masthead LNA helps: system-temperature SNR gain for Meteor (137.9 MHz, ITU-R P.372
   man-made noise for city/residential/rural) and ADS-B (1090 MHz), with 5 m of RG-58.

Run: python3 tools/verify/e6_gain_staging.py   (PASS/FAIL per check, ~3 s)
"""
import numpy as np

results = []
rng = np.random.default_rng(20261002)


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")


# ---------------------------------------------------------------- 1. analytic floor-lift rule
print("\n§1 ADC noise penalty vs analog 'floor lift' X (analog noise above ADC floor)")
print(f"{'X (dB)':>7s} {'penalty (dB)':>13s}")
pen = {}
for X in (0, 3, 5, 6, 10, 15, 20):
    pen[X] = 10 * np.log10(1 + 10 ** (-X / 10))
    print(f"{X:7d} {pen[X]:13.2f}")
check("X = 0 dB (analog = ADC floor): 3.0 dB penalty", abs(pen[0] - 3.01) < 0.01)
check("X = 6 dB: ~1 dB penalty", abs(pen[6] - 0.97) < 0.02)
check("X = 10 dB: 0.41 dB penalty", abs(pen[10] - 0.41) < 0.01)
check("X = 20 dB: 0.04 dB penalty (10 more dB of gain bought 0.37 dB)", abs(pen[20] - 0.043) < 0.003)

# RTL-SDR-like numbers
FS = 2.4e6
ENOB = 7.0
NF = 4.5                                   # dB, illustrative analog NF at mid/high gain
N_IN = -173.98 + NF                        # dBm/Hz input-referred analog noise
ADC_FLOOR_TOTAL = -(6.02 * ENOB + 1.76)    # dBFS over the full complex band
ADC_FLOOR = ADC_FLOOR_TOTAL - 10 * np.log10(FS)   # dBFS/Hz
P_FS_ADC = 0.0                             # dBm at the ADC input <-> 0 dBFS (reference)
G_cross = ADC_FLOOR - (N_IN - P_FS_ADC)
print(f"\n  ADC floor {ADC_FLOOR_TOTAL:.1f} dBFS total = {ADC_FLOOR:.1f} dBFS/Hz; analog noise {N_IN:.1f} dBm/Hz")
print(f"  analog noise equals the ADC floor at total gain G = {G_cross:.1f} dB (model reference)")
check("model: crossover gain ~62 dB for NF 4.5 dB and ENOB 7 at 2.4 MS/s", 60 < G_cross < 64, f"({G_cross:.1f} dB)")


def input_noise(G):
    """input-referred total noise density (dBm/Hz) at total gain G"""
    a = 10 ** (N_IN / 10)
    d = 10 ** ((ADC_FLOOR + P_FS_ADC - G) / 10)
    return 10 * np.log10(a + d)


def clip_level(G, backoff_db=3.0):
    """antenna-referred CW power that reaches 0 dBFS minus a back-off (dBm)"""
    return P_FS_ADC - G - backoff_db


print(f"\n{'G (dB)':>7s} {'N_in (dBm/Hz)':>14s} {'MDS 12.5k (dBm)':>16s} {'clip (dBm)':>11s} {'window (dB)':>12s}")
win = {}
for G in (40, 50, 55, 60, 65, 70, 75, 80):
    n = input_noise(G)
    mds = n + 10 * np.log10(12.5e3)
    cl = clip_level(G)
    win[G] = cl - mds
    print(f"{G:7d} {n:14.1f} {mds:16.1f} {cl:11.1f} {win[G]:12.1f}")
check("window (clip - MDS) is largest at LOW gain and shrinks ~1 dB per dB once analog noise dominates",
      win[40] > win[60] > win[80] and abs((win[70] - win[80]) - 10) < 0.6)
check("but sensitivity (MDS) at G = 40 is ~20 dB worse than at G = 70",
      (input_noise(40) - input_noise(70)) > 18, f"({input_noise(40) - input_noise(70):.1f} dB)")

# ---------------------------------------------------------------- 2. Monte-Carlo demonstration
print("\n§2 Monte-Carlo: weak -115 dBm tone beside a stronger in-band signal, 8-bit ADC")
N = 2 ** 18
t = np.arange(N) / FS
f_weak, f_strong = 312.5e3, -487.5e3
P_WEAK = -115.0                             # dBm at the antenna


def dbm_to_amp(p_dbm):
    # complex tone amplitude a such that |a|^2 = power in mW relative to 0 dBm ref
    return np.sqrt(10 ** (p_dbm / 10))


analog_noise_mw = 10 ** (N_IN / 10) * FS     # mW in the full band
lsb = 2.0 / 256                              # I and Q each span [-1, 1)
extra_adc_noise = 10 ** (ADC_FLOOR_TOTAL / 10) - 2 * lsb ** 2 / 12   # make total converter noise = ENOB 7
assert extra_adc_noise > 0
base_noise = (rng.standard_normal(N) + 1j * rng.standard_normal(N)) * np.sqrt(analog_noise_mw / 2)
adc_noise = (rng.standard_normal(N) + 1j * rng.standard_normal(N)) * np.sqrt(extra_adc_noise / 2)
w = np.hanning(N)
cg = np.sum(w) ** 2                          # (coherent gain)^2
enbw_bins = N * np.sum(w ** 2) / np.sum(w) ** 2
binhz = FS / N
f_axis = np.fft.fftshift(np.fft.fftfreq(N, 1 / FS))


def quantise(v):
    def q(r):
        r = np.clip(r, -1.0, 1.0 - lsb)
        return (np.floor(r / lsb) + 0.5) * lsb
    return q(v.real) + 1j * q(v.imag)


def measure(G, p_strong):
    x_ant = dbm_to_amp(P_WEAK) * np.exp(2j * np.pi * f_weak * t) + \
        dbm_to_amp(p_strong) * np.exp(2j * np.pi * f_strong * t) + base_noise
    g = 10 ** ((G - P_FS_ADC) / 20)          # amplitude gain antenna -> ADC (0 dBFS = amplitude 1)
    y = quantise(x_ant * g + adc_noise)
    clipped = np.mean((np.abs(y.real) >= 1 - lsb) | (np.abs(y.imag) >= 1 - lsb))
    P = np.abs(np.fft.fftshift(np.fft.fft(y * w))) ** 2 / (cg * enbw_bins)   # power per bin (tone sums correctly)
    kw = np.argmin(np.abs(f_axis - f_weak))
    mask = (np.abs(f_axis - f_weak) > 20e3) & (np.abs(f_axis - f_strong) > 60e3) & (np.abs(f_axis) < 0.8 * FS / 2)
    n_bin = np.mean(P[mask])
    p_tone = np.sum(P[kw - 3:kw + 4]) - 7 * n_bin
    n_density = n_bin / binhz
    snr = 10 * np.log10(max(p_tone, 1e-30) / (n_density * 12.5e3))
    floor = 10 * np.log10(n_density)
    spur = 10 * np.log10(np.max(P[mask]) / np.max(P))
    return snr, floor, clipped, spur


analog_limit = P_WEAK - (N_IN + 10 * np.log10(12.5e3))
print(f"  analog-only SNR limit of the weak tone in 12.5 kHz: {analog_limit:.1f} dB")
mc = {}
for label, p_strong in (("A: quiet band, neighbour at -75 dBm", -75.0), ("B: strong neighbour at -45 dBm", -45.0)):
    print(f"\n  Scenario {label}")
    print(f"  {'G (dB)':>7s} {'SNR weak 12.5k (dB)':>20s} {'floor (dBFS/Hz)':>16s} {'clipped %':>10s} {'max spur (dBc)':>15s}")
    mc[label[0]] = {}
    for G in (30, 36, 42, 46, 50, 54, 58, 62, 66, 70, 74, 78):
        r = measure(G, p_strong)
        mc[label[0]][G] = r
        print(f"  {G:7d} {r[0]:20.1f} {r[1]:16.1f} {100 * r[2]:10.3f} {r[3]:15.1f}")

A, B = mc["A"], mc["B"]
check("A: SNR rises ~dB-for-dB with gain while the ADC floor dominates (G 30 -> 50 gains > 15 dB)",
      A[50][0] - A[30][0] > 15, f"({A[30][0]:.1f} -> {A[50][0]:.1f} dB)")
bestA = max((g for g in A if A[g][2] == 0), key=lambda g: A[g][0])
check("A: best unclipped SNR is within 1.5 dB of the analog-only limit", analog_limit - A[bestA][0] < 1.5,
      f"(best G = {bestA} dB: {A[bestA][0]:.1f} vs {analog_limit:.1f} dB)")
G1 = min(g for g in A if A[g][2] == 0 and analog_limit - A[g][0] <= 1.0)
liftA = A[G1][1] - A[30][1]
check("A: the lowest gain within 1 dB of the analog limit shows a floor lift of ~5-12 dB over the ADC floor",
      5 <= liftA <= 12, f"(G = {G1} dB, lift {liftA:.1f} dB, SNR {A[G1][0]:.1f} dB)")
check("A: going from 62 to 70 dB gain (floor lift 3 -> 9 dB) buys < 2.5 dB SNR",
      A[70][0] - A[62][0] < 2.5, f"({A[70][0] - A[62][0]:.1f} dB)")
clipA = min(g for g in A if A[g][2] > 0)
check("A: once the -75 dBm neighbour clips, SNR collapses or clipping spurs appear (> -50 dBc)",
      (A[bestA][0] - A[78][0] > 10) or (A[78][3] > -50),
      f"(clipping from G = {clipA} dB; SNR at 78 dB {A[78][0]:.1f} dB, spur {A[78][3]:.1f} dBc)")
bestB = max((g for g in B if B[g][2] == 0), key=lambda g: B[g][0])
clipB = min(g for g in B if B[g][2] > 0)
check("B: the -45 dBm neighbour clips the ADC from G ~ 46 dB (0 dBFS at G = 45 dB plus noise peaks)",
      42 <= clipB <= 50, f"(first clipping at G = {clipB} dB)")
check("B: best achievable weak-tone SNR is > 10 dB worse than the analog limit (dynamic-range limited)",
      analog_limit - B[bestB][0] > 10, f"(best {B[bestB][0]:.1f} dB at G = {bestB})")
window_12k5 = 6.02 * ENOB + 1.76 + 10 * np.log10(FS / 12.5e3)
print(f"  ADC-limited window in 12.5 kHz = {window_12k5:.1f} dB; needed here: {-45 - (-115) + 10:.0f} dB (70 dB spread + 10 dB SNR)")
check("B: the spread (-45 to -115 dBm, +10 dB SNR) exceeds the 8-bit ADC's 66.7 dB window in 12.5 kHz", 80 > window_12k5)
G_rule = G_cross + 8
check("B: the strong signal, not the floor-lift rule (G ~ 70 dB), sets the usable gain", clipB < G_rule)

# ---------------------------------------------------------------- 3. librtlsdr gain table
print("\n§3 librtlsdr R820T/R828D gain table (tenths of dB) and LNA/mixer step tables (src/tuner_r82xx.c)")
r82xx_gains = [0, 9, 14, 27, 37, 77, 87, 125, 144, 157, 166, 197, 207, 229, 254, 280, 297, 328,
               338, 364, 372, 386, 402, 421, 434, 439, 445, 480, 496]
lna = [0, 9, 13, 40, 38, 13, 31, 22, 26, 31, 26, 14, 19, 5, 35, 13]
mix = [0, 5, 10, 10, 19, 9, 10, 25, 17, 10, 8, 16, 13, 6, 3, -8]
check("29 settings from 0 to 49.6 dB", len(r82xx_gains) == 29 and r82xx_gains[0] == 0 and r82xx_gains[-1] == 496)
check("LNA steps total 33.5 dB, mixer steps total 15.3 dB (measured relative gains, 928 MHz)",
      sum(lna) == 335 and sum(mix) == 153)
# reproduce the driver's alternating algorithm for a few requested gains
def lna_mix_for(gain):
    tot, li, mi = 0, 0, 0
    for _ in range(15):
        if tot >= gain:
            break
        li += 1
        tot += lna[li]
        if tot >= gain:
            break
        mi += 1
        tot += mix[mi]
    return li, mi, tot


for req in (0, 197, 297, 402, 496):
    li, mi, tot = lna_mix_for(req)
    print(f"  request {req / 10:5.1f} dB -> LNA index {li:2d}, mixer index {mi:2d} (sum of steps {tot / 10:.1f} dB)")
li, mi, tot = lna_mix_for(496)
check("49.6 dB request -> LNA index 15 and mixer index 14-15", li == 15 and mi >= 14)

# ---------------------------------------------------------------- 4. where phantom signals land
print("\n§4 Broadcast-FM harmonics (n x 87.5-108 MHz) and LO-harmonic responses (k f_LO +/- f_IF)")
bands = {"weather sats 137-138": (137e6, 138e6), "2 m 144-146": (144e6, 146e6), "AIS 161.95-162.05": (161.95e6, 162.05e6),
         "433 ISM 433.05-434.79": (433.05e6, 434.79e6), "SG LoRa 917-925": (917e6, 925e6), "ADS-B 1089-1091": (1089e6, 1091e6)}
fm_lo, fm_hi = 87.5e6, 108e6
hits = {}
for name, (lo, hi) in bands.items():
    hs = [n for n in range(2, 12) if not (n * fm_hi < lo or n * fm_lo > hi)]
    hits[name] = hs
    print(f"  {name:24s} FM harmonic orders landing inside: {hs}")
check("433 ISM band is hit by NO FM harmonic (4 x 108 = 432 MHz just misses; 5 x 87.5 = 437.5)", hits["433 ISM 433.05-434.79"] == [])
check("FM 4th harmonic covers 350-432 MHz, e.g. 102.5 MHz -> 410 MHz", 4 * fm_lo == 350e6 and 4 * 102.5e6 == 410e6)
check("ADS-B 1090 MHz lies inside the 10th-12th harmonic span? (not hit up to n = 11 by 87.5-108)", hits["ADS-B 1089-1091"] in ([], [11]))
f_if = 3.57e6
for f_t in (137.9e6, 145.0e6, 162.0e6, 433.92e6):
    f_lo = f_t + f_if
    resp = [(k, (k * f_lo - f_if) / 1e6, (k * f_lo + f_if) / 1e6) for k in (3, 5)]
    print(f"  tuned {f_t / 1e6:7.2f} MHz (LO {f_lo / 1e6:.2f}): " +
          "; ".join(f"k={k}: {a:.1f}/{b:.1f} MHz" for k, a, b in resp))
f_lo = 137.9e6 + f_if
check("tuned to Meteor 137.9 MHz, the 3rd-LO-harmonic response sits near 421-428 MHz (UHF land-mobile)",
      420e6 < 3 * f_lo - f_if < 425e6 and 427e6 < 3 * f_lo + f_if < 432e6)

# ---------------------------------------------------------------- 5. does a masthead LNA help? (depends on the environment)
print("\n§5 SNR gain from a masthead LNA (NF 1 dB, G 20 dB) vs SDR at the end of 5 m RG-58")
T0 = 290.0


def t_from_nf(nf_db):
    return T0 * (10 ** (nf_db / 10) - 1)


def rg58_db_per_100m(f_mhz):
    return 1.123 * np.sqrt(f_mhz) + 0.0123 * f_mhz      # fit from 03/coax-and-cables (Belden 8240)


def p372_fam(f_mhz, env):
    c, d = {"city": (76.8, 27.7), "residential": (72.5, 27.7), "rural": (67.2, 27.7)}[env]
    return c - d * np.log10(f_mhz)


def tsys(t_ant, nf_sdr, loss_db, lna=None):
    L = 10 ** (loss_db / 10)
    t_cable_sdr = (L - 1) * T0 + L * t_from_nf(nf_sdr)      # cable + SDR, referred to cable input
    if lna is None:
        return t_ant + t_cable_sdr
    nf_l, g_l = lna
    return t_ant + t_from_nf(nf_l) + t_cable_sdr / 10 ** (g_l / 10)


rows = []
for name, f, nf_sdr, tants in (("Meteor 137.9 MHz", 137.9, 5.8, None), ("ADS-B 1090 MHz", 1090.0, 11.9, {"sky/ground mix": 150.0})):
    loss = 0.05 * rg58_db_per_100m(f)
    if tants is None:
        tants = {env: T0 * 10 ** (p372_fam(f, env) / 10) for env in ("city", "residential", "rural")}
        tants["galactic only"] = T0 * 10 ** ((52.0 - 23.0 * np.log10(f)) / 10)   # P.372 galactic line
    for env, ta in tants.items():
        g = 10 * np.log10(tsys(ta, nf_sdr, loss) / tsys(ta, nf_sdr, loss, (1.0, 20.0)))
        rows.append((name, env, ta, loss, g))
        print(f"  {name:17s} {env:15s} T_a = {ta:7.0f} K, 5 m RG-58 = {loss:4.2f} dB -> LNA improves SNR by {g:5.1f} dB")
g_city = [r[4] for r in rows if r[1] == "city"][0]
g_rural = [r[4] for r in rows if r[1] == "rural"][0]
g_adsb = [r[4] for r in rows if r[0].startswith("ADS-B")][0]
check("Meteor in a city (P.372 man-made Fa ~ 17.5 dB): masthead LNA buys < 1 dB", g_city < 1.0, f"({g_city:.2f} dB)")
check("Meteor at a rural site: LNA buys ~1.5-2 dB", 1.5 < g_rural < 2.5, f"({g_rural:.2f} dB)")
g_gal = [r[4] for r in rows if r[1] == "galactic only"][0]
check("Meteor at a quiet site (galactic noise only, ~560 K): LNA buys ~3-5 dB", 3.0 < g_gal < 5.5, f"({g_gal:.2f} dB)")
check("ADS-B 1090 MHz (RTL NF ~12 dB at 1.28 GHz, 2.5 dB cable): LNA buys > 8 dB", g_adsb > 8, f"({g_adsb:.1f} dB)")
print(f"  P.372 city/residential/rural Fam at 137.9 MHz: {p372_fam(137.9, 'city'):.1f} / {p372_fam(137.9, 'residential'):.1f} / {p372_fam(137.9, 'rural'):.1f} dB")

print(f"\n{sum(results)}/{len(results)} PASS")
print("ALL PASS" if all(results) else "SOME FAIL")
