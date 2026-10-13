#!/usr/bin/env python3
"""
s1_ranging_error.py — how well can a radio find a landed rocket without GNSS? RSSI ranging, two-way
time of flight (SX1280 ranging engine), one-way TDOA with GNSS-timed receivers, compared with DF.

Used by: kb/15-lora-ism-radios/semtech-chip-family.md, section "Ranging and localisation".

§1 RSSI ranging: log-distance path loss + lognormal shadowing (σ dB, exponent n). Monte Carlo of the
   multiplicative error and the Cramér-Rao bound σ_d/d ≥ (ln10/10)·σ/n (Patwari et al. 2005), plus
   the bias when the assumed exponent is wrong.
§2 Two-way ToF: CRLB σ_d = c·[16π²·SNR·N·BW²·2^SF]^(-1/2) (Müller et al. 2021, eq. 4, back-to-back),
   the clock-offset error Δd ≈ c·δ·T_B/2, the multipath resolution c/BW, and the antenna/cable delay
   (1 ns of uncalibrated delay = 15 cm of range).
§3 One-way TDOA: chirp timing CRLB (rms bandwidth B/√12) vs the GNSS 1PPS (30 ns RMS) budget.
§4 Summary table at a 2 km recovery distance.
Run: python3 tools/verify/s1_ranging_error.py
"""
import math
import numpy as np

C = 299_792_458.0
rng = np.random.default_rng(7)
checks = []


def check(name, ok):
    checks.append(bool(ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")


print("=== §1 RSSI ranging ===")
for sigma, n in [(4, 2.0), (6, 2.5), (8, 3.0), (6, 2.0)]:
    x = sigma * rng.standard_normal(200_000)
    ratio = 10 ** (x / (10 * n))                 # d_hat / d for the ML (median-unbiased) estimate
    lo, hi = np.percentile(ratio, [16, 84])
    f1 = 10 ** (sigma / (10 * n))
    crb = math.log(10) / 10 * sigma / n
    print(f"  σ = {sigma} dB, n = {n}: 68 % interval ×{lo:.2f}…×{hi:.2f} (×/÷ {f1:.2f}); "
          f"CRB σ_d/d ≥ {crb:.2f}; at 2 km: {2*lo:.1f}–{2*hi:.1f} km")
    if (sigma, n) == (6, 2.5):
        check("68 % interval factor = 10^(σ/10n)", abs(hi - f1) / f1 < 0.02)
# wrong exponent: calibrate n=2 near the pad (LOS), use it for a landed rocket where n_true = 3.5
d_true = np.array([500, 1000, 2000, 5000.0])
d0, pl0 = 10.0, 0.0
n_true, n_ass = 3.5, 2.0
pl = 10 * n_true * np.log10(d_true / d0)
d_est = d0 * 10 ** (pl / (10 * n_ass))
print("  exponent mismatch (n_true 3.5, assumed 2.0): " +
      ", ".join(f"{a/1e3:.1f} km → {b/1e3:.1f} km" for a, b in zip(d_true, d_est)))
check("exponent mismatch overestimates distance", np.all(d_est > d_true))

print("\n=== §2 Two-way time of flight (SX1280) ===")


def crlb_tof(snr_db, n_sym, bw, sf):
    snr = 10 ** (snr_db / 10)
    return C * (1 / (16 * math.pi ** 2 * snr * n_sym * bw ** 2 * 2 ** sf)) ** 0.5


s = crlb_tof(12.5, 15, 403e3, 5)
print(f"  CRLB, BW 403 kHz, SF5, SNR 12.5 dB, N = 15: σ_d = {s:.2f} m (paper: 1.26 m; measured 2.11 m)")
print("  NOTE: eq. (4) as transcribed gives half the paper's 1.26 m; the factor of 2 is unresolved (logged as a contradiction).")
check("eq. (4) as transcribed = paper value / 2 (documented discrepancy)", abs(2 * s - 1.26) < 0.05)
for bw, sf in [(406e3, 10), (1625e3, 5)]:
    tsym = 2 ** sf / bw
    t_b = 2 * tsym + 15 * tsym      # switching delay + 15-symbol response (paper)
    dd = C * 40e-6 * t_b / 2
    print(f"  clock offset ±40 ppm, BW {bw/1e3:.0f} kHz SF{sf}: T_B ≈ {t_b*1e3:.1f} ms → Δd ≈ {dd:.0f} m "
          f"(paper: 257 m with T_B 42.9 ms; 2.01 m) — cancelled by role-swapped back-to-back ranging")
dd_paper = C * 40e-6 * 42.9e-3 / 2
check("clock-offset term reproduces 257 m", abs(dd_paper - 257) < 1.5)
for bw in [125e3, 406e3, 812e3, 1625e3]:
    print(f"  multipath resolution c/BW at {bw/1e3:.0f} kHz: {C/bw:.0f} m")
check("c/BW at 1625 kHz = 185 m", abs(C / 1625e3 - 184.5) < 1)
print(f"  uncalibrated delay: 1 ns round trip → {C*1e-9/2*100:.0f} cm of range; the per-SF/BW offsets "
      f"measured over a cable are 'several hundred m' (Müller et al.) — calibration is mandatory")

print("\n=== §3 One-way TDOA with GNSS-timed receivers ===")
for sf, bw, snr_db, n_pre in [(7, 125e3, 0, 8), (9, 125e3, -5, 8), (7, 500e3, 0, 8)]:
    T = n_pre * 2 ** sf / bw
    EN0 = 10 ** (snr_db / 10) * bw * T          # SNR over the full BW times BT
    b_rms = bw / math.sqrt(12)
    st = 1 / (2 * math.pi * b_rms * math.sqrt(2 * EN0))
    tot = math.hypot(st, 30e-9 * math.sqrt(2))   # two receivers' PPS (30 ns RMS each)
    print(f"  SF{sf}/{int(bw/1e3)} kHz, SNR {snr_db} dB, {n_pre}-symbol preamble: chirp timing CRLB {st*1e9:.1f} ns "
          f"({st*C:.1f} m); with 2 × 30 ns PPS: {tot*1e9:.0f} ns → {tot*C:.0f} m range-difference σ")
print("  field LoRaWAN TDoA (Plets et al. 2018): median ≈ 150 m — multipath at 125 kHz (c/BW = 2.4 km) dominates the CRLB")
check("at 125 kHz the 8-symbol chirp CRLB (≈ 100 ns) exceeds the 30 ns PPS jitter", 1 / (2 * math.pi * 125e3 / math.sqrt(12) * math.sqrt(2 * 8 * 128)) > 30e-9)

print("\n=== §4 What each method gives at 2 km (1σ, order of magnitude) ===")
rows = [
    ("RSSI ranging (σ 6 dB, n 2.5)", 2000 * (10 ** (6 / 25) - 1), "range only, ×/÷ 1.74; biased if n is wrong"),
    ("two-station DF, 1° bearings, 2 km baseline", 225, "median miss (s1_df_bearing.py §5)"),
    ("SX1280 two-way ToF (rural LOS)", 84, "σ of range error, 1.4 km links (Müller et al.); needs 3 anchors for 2-D"),
    ("LoRa TDoA, 125 kHz, gateways", 150, "median (Plets et al.); needs ≥ 3 synchronised receivers"),
    ("GNSS fix downlinked before landing", 5, "plus wind drift if the last fix is from the descent"),
]
for a, b, c in rows:
    print(f"  {a:46s} ~{b:5.0f} m   {c}")
print(f"\nSummary: {sum(checks)} of {len(checks)} checks pass")
