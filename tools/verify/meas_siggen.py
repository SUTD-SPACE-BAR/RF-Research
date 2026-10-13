#!/usr/bin/env python3
"""
meas_siggen.py -- numerical checks for kb/17-test-measurement/signal-generators-and-sources.md

1. Harmonics of square-wave sources (Si5351, ADF4351 divided outputs, tinySA high/"cleanest" mode):
   odd harmonics 20 log(1/n); even harmonics from duty-cycle error.
2. Low-pass filter needed to clean an ADF4351/MAX2870 output at 433 / 915 MHz to -50 dBc:
   Butterworth and Chebyshev (0.1 dB) order vs attenuation at 2f and 3f.
3. ADF4351 in-band phase noise at 915 MHz from the datasheet normalised floor
   PN = -220 + 10 log fPFD + 20 log N (at the VCO), then -20 log(divider).
4. Attenuator stacks: accumulated uncertainty (worst case vs RSS) and mismatch ripple between pads.
5. Level budget for very low signals (receiver tests) and required isolation.

Run: python3 tools/verify/meas_siggen.py
"""
import numpy as np


def db20(x):
    return 20 * np.log10(np.abs(x))


# ---------------------------------------------------------------- 1. square-wave harmonics
print("=== 1. Harmonics of a square wave (relative to the fundamental) ===")
for duty in [0.50, 0.48, 0.45, 0.40]:
    row = []
    for n in range(1, 8):
        # Fourier amplitude of a pulse train of duty d: (2/(n pi)) |sin(n pi d)|
        a = abs(np.sin(n * np.pi * duty)) / n
        a1 = abs(np.sin(np.pi * duty))
        row.append(f"H{n}: {db20(a/a1) if a > 1e-12 else -np.inf:6.1f}")
    print(f"  duty {duty*100:4.0f} %: " + " | ".join(row[1:]) + " dBc")
print("  -> 50 % duty: H3 -9.5, H5 -14.0, H7 -16.9 dBc; ADF4351 datasheet: H2 -20/-19, H3 -10/-13 dBc (divided/fundamental)")

# ---------------------------------------------------------------- 2. clean-up filter
print("\n=== 2. Low-pass filter order to reach -50 dBc harmonics (square-wave source) ===")
def butter_att(f, fc, n):
    return 10 * np.log10(1 + (f / fc) ** (2 * n))
def cheb_att(f, fc, n, ripple_db=0.1):
    eps = np.sqrt(10 ** (ripple_db / 10) - 1)
    x = f / fc
    Tn = np.cosh(n * np.arccosh(x)) if x >= 1 else np.cos(n * np.arccos(x))
    return 10 * np.log10(1 + eps ** 2 * Tn ** 2)
for f0 in [433e6, 915e6]:
    fc = 1.2 * f0
    need2 = 50 - 20      # H2 at -20 dBc (divided output) -> need 30 dB
    need3 = 50 - 10      # H3 at -10 dBc -> need 40 dB
    print(f"  f0 = {f0/1e6:.0f} MHz, filter fc = {fc/1e6:.0f} MHz: need {need2} dB at 2f0, {need3} dB at 3f0")
    for n in [3, 5, 7, 9]:
        b2, b3 = butter_att(2 * f0, fc, n), butter_att(3 * f0, fc, n)
        c2, c3 = cheb_att(2 * f0, fc, n), cheb_att(3 * f0, fc, n)
        ok_b = "OK" if (b2 >= need2 and b3 >= need3) else "--"
        ok_c = "OK" if (c2 >= need2 and c3 >= need3) else "--"
        print(f"    order {n}: Butterworth {b2:5.1f}/{b3:5.1f} dB {ok_b}; Chebyshev 0.1 dB {c2:5.1f}/{c3:5.1f} dB {ok_c}")
print("  (ideal lossless prototypes; real LC/LTCC filters have finite stopband and re-entrant responses at GHz -- measure S21)")

# ---------------------------------------------------------------- 3. ADF4351 phase noise
print("\n=== 3. ADF4351 in-band phase noise estimate ===")
for f_out, f_pfd in [(915e6, 25e6), (433e6, 25e6), (915e6, 10e6)]:
    div = 1
    f_vco = f_out
    while f_vco < 2.2e9:
        div *= 2
        f_vco = f_out * div
    N = f_vco / f_pfd
    pn_vco = -220 + 10 * np.log10(f_pfd) + 20 * np.log10(N)
    pn_out = pn_vco - 20 * np.log10(div)
    # 1/f contribution at 10 kHz: PN1f = -116 dBc/Hz normalised to 1 GHz at 10 kHz -> + 20 log(fRF/1GHz)
    pn_1f = -116 + 20 * np.log10(f_out / 1e9)
    tot = 10 * np.log10(10 ** (pn_out / 10) + 10 ** (pn_1f / 10))
    print(f"  {f_out/1e6:.0f} MHz (VCO {f_vco/1e9:.2f} GHz / {div}, fPFD {f_pfd/1e6:.0f} MHz, N {N:.1f}): "
          f"floor term {pn_out:.1f} dBc/Hz, 1/f term at 10 kHz {pn_1f:.1f} -> in-band ~{tot:.1f} dBc/Hz")
print("  -> good enough to test most receivers' adjacent-channel/blocking, but the SA must be better than this to measure it")

# ---------------------------------------------------------------- 4. attenuator stacks
print("\n=== 4. Attenuator stack uncertainty ===")
stack = [(30, 0.3), (30, 0.3), (10, 0.2), (20, 0.25)]   # (nominal dB, +/- uncertainty dB) uncalibrated typical
wc = sum(u for _, u in stack)
rss = np.sqrt(sum(u ** 2 for _, u in stack))
print(f"  4 uncalibrated pads (90 dB total): worst-case +/-{wc:.2f} dB, RSS +/-{rss:.2f} dB")
stack_c = [(30, 0.05), (30, 0.05), (10, 0.03), (20, 0.04)]
print(f"  same pads VNA-calibrated at the test frequency: worst-case +/-{sum(u for _,u in stack_c):.2f} dB, "
      f"RSS +/-{np.sqrt(sum(u**2 for _,u in stack_c)):.2f} dB")
for swr in [1.05, 1.1, 1.2]:
    g = (swr - 1) / (swr + 1)
    n_if = len(stack) - 1
    rip = n_if * db20(1 + g * g)
    print(f"  pad SWR {swr}: each pad-pad interface +/-{db20(1+g*g):.3f} dB, {n_if} interfaces worst case +/-{rip:.3f} dB")

# ---------------------------------------------------------------- 5. low-level budget
print("\n=== 5. Producing -137 dBm for a receiver test ===")
for src in [-10.0, -40.0, -80.0, -110.0]:
    att = src - (-137)
    print(f"  source {src:+.0f} dBm -> {att:.0f} dB attenuation; required isolation of leakage paths >= {att+20:.0f} dB")
print("  -> use the generator's lowest reliable level (tinySA Ultra: +/-2 dB down to -72 dBm, less accurate below) and"
      " fewer external pads; shield the generator and the DUT")
