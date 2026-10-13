#!/usr/bin/env python3
"""
meas_power.py -- numerical checks for kb/17-test-measurement/rf-power-measurement.md

1. Mismatch uncertainty between a source and a power sensor: limits 20 log(1 +/- |Gs||Gl|),
   and how a well-matched pad in front of the sensor improves it.
2. Diode detector law: rectified output of an ideal diode (current-source bias, open video load)
   V_dc = n V_T ln I0(v / n V_T); deviation from square law vs input power (50-ohm drive),
   and single-tone vs two-tone (same average power) reading -> why diode sensors misread
   modulated signals above ~-20 dBm, and why constant-envelope LoRa is safe.
3. Log-detector (AD8307 / AD8318) two-point calibration: slope & intercept from two known levels,
   residual error from log-conformance, and temperature drift.
4. Average vs burst power for LoRa packets on an averaging (thermal) power meter.
5. Directional coupler / through-line wattmeter: effect of coupler directivity on reflected power
   and SWR readings.
6. Attenuator pad dissipation and a tapered pad chain.

Run: python3 tools/verify/meas_power.py
"""
import numpy as np
from scipy import special

VT = 0.025852   # kT/q at 300 K, V


def db(x):
    return 20 * np.log10(np.abs(x))


def g_of_swr(s):
    return (s - 1) / (s + 1)


# ---------------------------------------------------------------- 1. mismatch uncertainty
print("=== 1. Mismatch uncertainty source <-> sensor ===")
for swr_s, swr_l in [(1.5, 1.1), (1.5, 1.3), (2.0, 1.2), (1.2, 1.05), (3.0, 1.2)]:
    gs, gl = g_of_swr(swr_s), g_of_swr(swr_l)
    hi, lo = db(1 + gs * gl), db(1 - gs * gl)
    print(f"source SWR {swr_s:3.1f} (|G| {gs:.3f}), sensor SWR {swr_l:4.2f} (|G| {gl:.3f}): "
          f"+{hi:.3f} / {lo:.3f} dB")
# improve with a 10 dB pad of SWR 1.05 at the source
gs, gl = g_of_swr(2.0), g_of_swr(1.2)
for pad in [0, 6, 10, 20]:
    gpad = g_of_swr(1.05) if pad else 0
    geff = np.hypot(gpad, gs * 10 ** (-2 * pad / 20))    # rss of pad match and attenuated source match
    print(f"  SWR-2.0 source + {pad:2d} dB pad (SWR 1.05): effective source |G| {geff:.3f} -> "
          f"+{db(1+geff*gl):.3f}/{db(1-geff*gl):.3f} dB with a SWR-1.2 sensor")

# ---------------------------------------------------------------- 2. diode detector law
print("\n=== 2. Diode detector: square law -> linear, single vs two tone ===")
nVT = 1.05 * VT


def vdc_cw(p_dbm, R=50.0):
    v = np.sqrt(2 * R * 10 ** (p_dbm / 10) / 1000)     # peak voltage across 50 ohm
    return nVT * np.log(special.i0(v / nVT))


def vdc_two_tone(p_total_dbm, R=50.0, n=4000):
    # two equal tones, total average power p_total; envelope A(t) = 2 a |cos(pi df t)|, a = per-tone peak
    a = np.sqrt(2 * R * 10 ** (p_total_dbm / 10) / 2 / 1000)
    th = np.linspace(0, np.pi, n, endpoint=False)
    env = 2 * a * np.abs(np.cos(th))
    # quasi-static: video filter averages the instantaneous rectified output over the beat
    return np.mean(nVT * np.log(special.i0(env / nVT)))


ref = -50.0
k = vdc_cw(ref) / 10 ** (ref / 10)            # square-law constant fitted at -50 dBm
from scipy.optimize import brentq
print(f"{'P (dBm)':>8} {'Vdc dev. from square law':>26} {'two-tone indicated-power error (CW-calibrated)':>48}")
for p in [-60, -40, -30, -20, -10, 0, 10, 20]:
    dev = 10 * np.log10(vdc_cw(p) / (k * 10 ** (p / 10)))
    v2 = vdc_two_tone(p)
    p_ind = brentq(lambda q: vdc_cw(q) - v2, p - 10, p + 10)     # invert the CW calibration curve
    print(f"{p:8d} {dev:24.2f} dB {p_ind - p:44.2f} dB")
print("  -> a diode sensor calibrated with CW reads a two-tone/modulated signal correctly only in the square-law region;")
print("     constant-envelope signals (FSK, LoRa chirps) read correctly at any level once CW-calibrated.")

# ---------------------------------------------------------------- 3. log detector calibration
print("\n=== 3. Log detector two-point calibration (AD8318-like, 915 MHz) ===")
slope_true, icpt_true = -0.0244, 20.4     # V/dB, dBm (datasheet typ at 1.9 GHz)
def vout(p, temp_drift_db=0.0):
    # add a small log-conformance ripple (+/-0.4 dB) and optional drift
    ripple = 0.4 * np.sin(2 * np.pi * (p + 60) / 18)
    return slope_true * ((p + ripple + temp_drift_db) - icpt_true)
p1, p2 = -40.0, -10.0              # calibration levels from a known source (e.g. generator + pads verified by power meter)
v1, v2 = vout(p1), vout(p2)
slope = (v2 - v1) / (p2 - p1)
icpt = p1 - v1 / slope
print(f"two-point calibrated slope {slope*1000:.2f} mV/dB, intercept {icpt:.2f} dBm (true {slope_true*1000:.1f} mV/dB, {icpt_true} dBm)")
errs = []
for p in np.arange(-55, 0, 5):
    pe = vout(p) / slope + icpt
    errs.append(pe - p)
print(f"two-point: residual error over -55..-5 dBm: max {np.max(np.abs(errs)):.2f} dB (from +/-0.4 dB conformance ripple)")
pc = np.arange(-55, 0, 5.0)
A = np.vstack([pc, np.ones_like(pc)]).T
m_, c_ = np.linalg.lstsq(A, vout(pc), rcond=None)[0]
errs_ls = (vout(pc) - c_) / m_ - pc
print(f"12-point least-squares fit: slope {m_*1000:.2f} mV/dB, residual max {np.max(np.abs(errs_ls)):.2f} dB;"
      f" a lookup table (interpolated) removes the ripple entirely at the cal frequency")
print(f"temperature: +/-0.5 dB spec over -40..+85 C -> recal or use the on-chip temp sensor for < 0.5 dB")
# AD8307: +25 mV/dB, intercept -84 dBm
for p in [-70, -40, 0, 16]:
    print(f"  AD8307 nominal: P {p:+4d} dBm -> Vout = 0.025*(P+84) = {0.025*(p+84):.3f} V")
for p in [-60, -30, 0]:
    print(f"  AD8318 nominal: P {p:+4d} dBm -> Vout = -0.0245*(P-20.4) = {-0.0245*(p-20.4):.3f} V")

# ---------------------------------------------------------------- 4. average vs burst
print("\n=== 4. LoRa packets on an averaging power meter ===")
p_burst = 22.0   # dBm (SX1262 max)
for toa_ms, period_s in [(41.2, 1.0), (370.7, 10.0), (1318.9, 60.0), (41.2, 0.1)]:
    D = toa_ms / 1000 / period_s
    print(f"ToA {toa_ms:7.1f} ms every {period_s:5.1f} s: duty {100*D:6.2f} % -> average reading "
          f"{p_burst + 10*np.log10(D):6.2f} dBm (burst {p_burst} dBm); correction +{-10*np.log10(D):.2f} dB")
print("  -> use a peak/burst-capable sensor, a gated SA zero-span, or a CW test mode; or measure D precisely")

# ---------------------------------------------------------------- 5. directional coupler directivity
print("\n=== 5. Reflected-power reading vs coupler directivity ===")
for D in [15, 20, 25, 30, 40]:
    for rl in [10, 20]:
        g = 10 ** (-rl / 20)
        d = 10 ** (-D / 20)
        lo, hi = max(g - d, 0), g + d
        swr_lo, swr_hi = (1 + lo) / (1 - lo), (1 + hi) / (1 - hi)
        print(f"  directivity {D} dB, true RL {rl} dB (SWR {(1+g)/(1-g):.2f}): SWR reads {swr_lo:.2f}..{swr_hi:.2f}")

# ---------------------------------------------------------------- 6. pads
print("\n=== 6. Attenuator pads: dissipation and tapered chains ===")
p_in_w = 1.0
for chain in [(30,), (10, 20), (20, 20), (3, 10, 30)]:
    p = p_in_w
    parts = []
    for a in chain:
        diss = p * (1 - 10 ** (-a / 10))
        parts.append(f"{a} dB pad dissipates {diss:.3f} W")
        p *= 10 ** (-a / 10)
    print(f"  1 W into {'+'.join(map(str, chain))} dB: " + "; ".join(parts) + f"; out {10*np.log10(p*1000):.1f} dBm")
print("  -> the FIRST pad takes almost all the power; put the highest-rated pad first")
