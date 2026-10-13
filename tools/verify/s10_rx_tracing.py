#!/usr/bin/env python3
"""W5-S10 checks for 17/rf-bring-up-debug-playbook (receiver signal tracing, IF alignment)
and 17/spectrum-analyzers (band-edge DANL table, low-frequency limits, gain-phase ground loop).

A. Per-stage signal and noise levels of the 433 MHz superhet used in 06/receiver-architectures
   (same stage list as tools/verify/rfckt_rx_tx.py §E).
B. Can a spectrum analyzer "see" the noise at each test point (noise tracing)?
C. SDR front end: noise-floor rise when the LNA is switched on (the "is my LNA working" test).
D. IF alignment: single-tuned IF can detuning loss; why a limiter hides misalignment.
E. Keysight N9020B DANL table -> analyzer NF per band (the harmonic-mixing stair step).
F. Shunt-thru ground-loop error below 100 kHz (cable-shield current division).
"""
import numpy as np

ok_all = True
def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(("PASS " if cond else "FAIL ") + name)

db = lambda x: 10 * np.log10(x)
kT0 = -173.98  # dBm/Hz

# ---------------------------------------------------------------- A
stages = [  # name, gain dB, NF dB  (06/receiver-architectures, rfckt_rx_tx.py §E)
    ("SAW 433", -2.4, 2.4), ("LNA", 20.0, 0.8), ("SAW", -3.0, 3.0),
    ("mixer (DBM)", -6.5, 7.0), ("IF amp", 20.0, 3.0), ("IF filter", -4.0, 4.0)]
Pin = -100.0
RBW = 10e3
print("A: 433 MHz superhet, -100 dBm CW at the antenna port; noise with the input terminated (290 K) in RBW 10 kHz")
print(f"{'after stage':14s} {'G_cum dB':>8s} {'NF_cum dB':>9s} {'signal dBm':>10s} {'noise dBm/10kHz':>15s} {'SNR dB':>7s}")
F, G = 1.0, 1.0
rows = []
for name, g, nf in stages:
    F = F + (10 ** (nf / 10) - 1) / G
    G = G * 10 ** (g / 10)
    sig = Pin + db(G)
    noise = kT0 + db(RBW) + db(F) + db(G)
    rows.append((name, db(G), db(F), sig, noise))
    print(f"{name:14s} {db(G):8.1f} {db(F):9.2f} {sig:10.1f} {noise:15.1f} {sig - noise:7.1f}")
check("A1 total gain 24.1 dB and NF 3.8 dB (matches 06 page)", abs(rows[-1][1] - 24.1) < 0.05 and abs(rows[-1][2] - 3.8) < 0.1)
check("A2 SNR in 10 kHz falls by only ~0.6 dB after the LNA (later stages add little)",
      max(r[3] - r[4] for r in rows[1:]) - min(r[3] - r[4] for r in rows[1:]) < 0.7)

# ---------------------------------------------------------------- B
print("\nB: noise tracing — output noise vs analyzer DANL in the same 10 kHz RBW (log-avg display, -2.5 dB)")
for sa_nf, label in [(27.0, "tinySA (NF ~27 dB)"), (7.0, "tinySA Ultra + LNA (NF ~7 dB)")]:
    danl = kT0 + sa_nf + db(RBW) - 2.5
    print(f"  {label}: DANL {danl:.1f} dBm")
    for name, gc, fc, sig, noise in rows:
        disp_noise = noise - 2.5
        rise = db(10 ** (disp_noise / 10) + 10 ** (danl / 10)) - danl
        print(f"     at {name:12s} chain noise {disp_noise:7.1f} dBm displayed -> floor rises {rise:5.1f} dB when the chain is powered")
    if sa_nf == 27.0:
        r_lna = db(10 ** ((rows[1][4] - 2.5) / 10) + 10 ** (danl / 10)) - danl
        r_if = db(10 ** ((rows[4][4] - 2.5) / 10) + 10 ** (danl / 10)) - danl
check("B1 a plain tinySA cannot see the LNA-output noise (< 1 dB rise) but sees the IF-amp output (> 5 dB)",
      r_lna < 1.0 and r_if > 5.0)

# ---------------------------------------------------------------- C
print("\nC: SDR front end (SAW 2.4 dB -> LNA 20 dB/0.8 dB -> RTL-SDR NF 5.4 dB at 437 MHz)")
F_saw = 10 ** 0.24; G_saw = 10 ** -0.24
F_lna = 10 ** 0.08; G_lna = 100.0
F_sdr = 10 ** 0.54
F_front = F_saw + (F_lna - 1) / G_saw
G_front = G_saw * G_lna
F_sys = F_front + (F_sdr - 1) / G_front
# noise at SDR input, antenna replaced by a 290 K load, relative to kT0B:
n_on = F_front * G_front + (F_sdr - 1)      # LNA powered
n_off_bypass = F_sdr                         # SDR alone on the load
rise = db(n_on / n_off_bypass)
print(f"  system NF {db(F_sys):.2f} dB (SDR alone 5.4 dB); floor rise when the LNA is switched in: {rise:.1f} dB")
check("C1 system NF ~3.3 dB and the SDR floor rises ~15-16 dB when the LNA chain is inserted", 3.0 < db(F_sys) < 3.6 and 15 < rise < 17)
# rule: a rise of >= 10 dB means the LNA noise dominates the SDR's own (the SDR adds < 0.5 dB)
added = db(F_sys) - db(F_front)
check("C2 SDR adds < 0.5 dB to the system NF when the rise is > 10 dB", added < 0.5)

# ---------------------------------------------------------------- D
print("\nD: IF alignment — single-tuned IF transformer, f0 10.7 MHz, loaded Q 50")
f0, Q = 10.7e6, 50
bw = f0 / Q
for d in [25e3, 50e3, 100e3, 200e3]:
    loss = db(1 + (2 * Q * d / f0) ** 2)
    print(f"  detuned {d/1e3:5.0f} kHz -> {loss:5.2f} dB lower gain (3 dB BW {bw/1e3:.0f} kHz)")
loss100 = db(1 + (2 * Q * 100e3 / f0) ** 2)
check("D1 100 kHz detuning of a Q-50 10.7 MHz can costs ~2.7 dB", abs(loss100 - 2.72) < 0.05)
# A limiter (output constant once the input exceeds its knee) hides misalignment:
knee = -60.0   # dBm at limiter input (illustrative)
def limiter_out(p_in):
    return min(p_in, knee)
p_aligned = -45.0
out_al = limiter_out(p_aligned); out_mis = limiter_out(p_aligned - 10.0)
check("D2 with the IF 15 dB above the limiter knee a 10 dB misalignment changes the output by 0 dB", out_al == out_mis)
out_al2 = limiter_out(-75.0); out_mis2 = limiter_out(-85.0)
check("D3 below the knee the same misalignment shows the full 10 dB", abs((out_al2 - out_mis2) - 10) < 1e-9)

# ---------------------------------------------------------------- E
print("\nE: Keysight N9020B MXA DANL (1 Hz, log-avg, 0 dB att, spec) -> NF_SA = DANL + 174 + 2.5")
bands = [  # range, LO multiple N, DANL spec dBm/Hz (5992-1255)
    ("9 kHz-1 MHz", 1, -130), ("1-10 MHz", 1, -150), ("10 MHz-2.1 GHz", 1, -151), ("2.1-3.6 GHz", 1, -149),
    ("3.6-8.4 GHz", 1, -149), ("8.3-13.6 GHz", 2, -148), ("13.5-17.1 GHz", 2, -144),
    ("17.0-20.0 GHz", 4, -143), ("20.0-26.5 GHz", 4, -136)]
for rng, N, d in bands:
    print(f"  {rng:15s} N={N}  DANL {d:5d} dBm/Hz  NF ~ {d + 173.98 + 2.51:5.1f} dB")
check("E1 NF ~25.5 dB at 10 MHz-2.1 GHz", abs(-151 + 173.98 + 2.51 - 25.5) < 0.1)
check("E2 DANL at 9 kHz-1 MHz is 20 dB worse than at 1-10 MHz (LO-feedthrough skirt / low-f limit)", (-130) - (-150) == 20)
check("E3 the N=4 top band is 15 dB worse than band 0", (-136) - (-151) == 15)
# phase noise penalty of harmonic mixing:
check("E4 phase-noise penalty 20 log N = 6.0 / 12.0 / 18.1 dB for N = 2/4/8",
      [round(20 * np.log10(n), 1) for n in (2, 4, 8)] == [6.0, 12.0, 18.1])

# ---------------------------------------------------------------- F
print("\nF: shunt-thru (PDN) measurement, ground-loop error from cable shields")
Rs = 10e-3     # shield resistance of each 1 m cable (illustrative, RG-58 class)
fc = 2e3       # shield cut-off R/(2 pi L), RG-58 class (Ott)
Rdut = 1e-3
for f in [100, 1e3, 1e4, 1e5, 1e6]:
    Zerr = Rs / (2 + 1j * f / fc)
    print(f"  {f:9.0f} Hz: error impedance {abs(Zerr)*1e3:6.3f} mOhm = {abs(Zerr)/Rdut*100:6.1f} % of a 1 mOhm DUT")
e100k = abs(Rs / (2 + 1j * 1e5 / fc)) / Rdut
eDC = abs(Rs / 2) / Rdut
check("F1 DC error = Rs/2 = 500 % of a 1 mOhm DUT", abs(eDC - 5.0) < 1e-9)
check("F2 error falls to ~20 % at 100 kHz and ~2 % at 1 MHz", abs(e100k - 0.2) < 0.01 and abs(abs(Rs / (2 + 1j * 1e6 / fc)) / Rdut - 0.02) < 0.002)
check("F3 for a 50 Ohm-level DUT the same error is < 0.01 % at 1 kHz", abs(Rs / (2 + 1j * 1e3 / fc)) / 50 < 1e-4)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
