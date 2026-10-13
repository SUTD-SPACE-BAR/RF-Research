#!/usr/bin/env python3
"""
meas_scope_probe.py -- numerical checks for kb/17-test-measurement/oscilloscopes-and-probing-for-rf.md

1. Rise time vs bandwidth: 10-90 % rise of a Gaussian response (0.332/BW -> "0.35") and of
   1-pole, 4th-order Butterworth and brick-wall responses (0.4-0.45 region for fast scopes).
   Cascade: t_sys = sqrt(t_scope^2 + t_probe^2); measured-rise error vs ratio (3:1 -> 5 %, 5:1 -> 2 %).
2. Amplitude error of a sine at a fraction of the -3 dB bandwidth (Gaussian and 1-pole).
3. Passive 10x probe loading: |Z| of 10 Mohm || 12 pF vs frequency; loading of a 50-ohm-source
   node; low-Z (Z0) resistive divider probe (450 + 50 ohm = 10x into 50 ohm) comparison.
4. Ground-lead ringing: L from the Tektronix example (11 pF, 6-inch lead, ~140 MHz), ringing
   frequency and Q for various lead lengths; spring-tip ground.
5. ADC resolution / ENOB -> SNR, FFT processing gain and scope-FFT dynamic range.
6. Near-field H-loop probe: open-circuit voltage V = j w mu0 H A; sensitivity vs frequency and
   loop size; and the "shielded loop" self-resonance limit.

Run: python3 tools/verify/meas_scope_probe.py
"""
import numpy as np
from scipy import signal

MU0 = 4e-7 * np.pi


# ---------------------------------------------------------------- 1. rise time vs BW
print("=== 1. 10-90 % rise time x bandwidth ===")
B = 1.0   # Hz (normalised)
t = np.linspace(0, 5, 200001)
def rise_10_90(tt, y):
    y = y / y[-1]
    return tt[np.argmax(y >= 0.9)] - tt[np.argmax(y >= 0.1)]
# Gaussian: H(f) = exp(-ln2/2 (f/B)^2) has |H|=-3 dB at f=B; impulse response is Gaussian with
# sigma_t = sqrt(ln2)/(2 pi B) -> step is erf; 10-90 % = 2*1.2816*sigma_t
sig = np.sqrt(np.log(2)) / (2 * np.pi * B)
print(f"Gaussian response      : t_r * BW = {2*1.28155*sig*B:.3f}")
# 1-pole RC
print(f"single pole (RC)       : t_r * BW = {np.log(9)/(2*np.pi):.3f}")
# Butterworth 4th order analog, cutoff 1 Hz
for order in [2, 4, 8]:
    bb, aa = signal.butter(order, 2 * np.pi * B, analog=True)
    tt, yy = signal.step((bb, aa), T=np.linspace(0, 5, 50001))
    print(f"Butterworth order {order}   : t_r * BW = {rise_10_90(tt, yy)*B:.3f}")
# brick-wall (ideal low-pass): step = 1/2 + Si(2 pi B t)/pi
from scipy.special import sici
tt = np.linspace(-5, 5, 400001)
ys = 0.5 + sici(2 * np.pi * B * tt)[0] / np.pi
i10 = np.argmax(ys >= 0.1); i90 = np.argmax(ys >= 0.9)
print(f"brick-wall             : t_r * BW = {(tt[i90]-tt[i10])*B:.3f}")
print("  -> 0.35 is the Gaussian/1-pole value; flat 'brick-wall-like' fast scopes are 0.40-0.45 (Tek primer)")
for ratio in [1, 2, 3, 5, 10]:
    meas = np.sqrt(ratio ** 2 + 1)
    print(f"  signal rise = {ratio} x system rise: displayed rise high by {100*(meas/ratio-1):5.1f} %")

# ---------------------------------------------------------------- 2. amplitude error of a sine near BW
print("\n=== 2. Amplitude error of a sine vs f/BW ===")
for fr in [0.1, 0.2, 0.3, 0.5, 0.7, 1.0]:
    g = 20 * np.log10(np.exp(-np.log(2) / 2 * fr ** 2))
    p1 = 20 * np.log10(1 / np.sqrt(1 + fr ** 2))
    print(f"  f = {fr:.1f} BW: Gaussian {g:6.2f} dB ({100*(10**(g/20)-1):6.1f} %), 1-pole {p1:6.2f} dB ({100*(10**(p1/20)-1):6.1f} %)")
print("  -> for 3 % amplitude accuracy on a Gaussian scope keep f <= ~0.3 BW; a 915 MHz sine needs a ~3 GHz scope")

# ---------------------------------------------------------------- 3. probe loading
print("\n=== 3. Probe loading ===")
Rp, Cp = 10e6, 12e-12
for f in [1e6, 10e6, 100e6, 433e6, 915e6]:
    zc = 1 / (2 * np.pi * f * Cp)
    z = 1 / (1 / Rp + 1j * 2 * np.pi * f * Cp)
    # node driven from a 25-ohm Thevenin (e.g. a 50-ohm line terminated, seen at the midpoint) and 50-ohm
    err25 = 20 * np.log10(abs(z / (z + 25)))
    print(f"  f = {f/1e6:6.0f} MHz: 10x passive 10 Mohm||12 pF -> |Z| = {abs(z):9.1f} ohm; "
          f"on a 25-ohm Thevenin node the signal drops {err25:6.2f} dB")
for R in [450, 950]:
    ratio = (R + 50) / 50
    # low-Z probe tip parasitic ~0.2 pF
    for f in [100e6, 915e6, 2.4e9]:
        z = 1 / (1 / (R + 50) + 1j * 2 * np.pi * f * 0.2e-12)
        err25 = 20 * np.log10(abs(z / (z + 25)))
        print(f"  Z0 probe {R}+50 ohm ({ratio:.0f}x) at {f/1e6:6.0f} MHz: |Z_in| {abs(z):6.0f} ohm, loading of a 25-ohm node {err25:6.2f} dB")

# ---------------------------------------------------------------- 4. ground lead ringing
print("\n=== 4. Ground-lead ringing ===")
f_ring_tek, C_tek, len_tek = 140e6, 11e-12, 0.1524
L_tek = 1 / ((2 * np.pi * f_ring_tek) ** 2 * C_tek)
print(f"Tek example (11 pF, 6-inch lead, ~140 MHz) -> L = {L_tek*1e9:.0f} nH = {L_tek*1e9/(len_tek*1000):.2f} nH/mm")
Lpm = L_tek / len_tek
for length_mm, C in [(152, 11e-12), (76, 11e-12), (25, 11e-12), (5, 11e-12), (152, 1e-12)]:
    L = Lpm * length_mm / 1000
    fr = 1 / (2 * np.pi * np.sqrt(L * C))
    Q = np.sqrt(L / C) / 25.0     # driven from a 25-ohm source (series R), Q ~ Z0/R
    print(f"  lead {length_mm:4d} mm, C {C*1e12:4.0f} pF: L ~ {L*1e9:6.1f} nH, rings at {fr/1e6:7.0f} MHz, Q ~ {Q:.1f} (25-ohm source)")
print("  -> a spring/barrel ground (~5 mm) moves the ring above ~1 GHz; a 15 cm clip rings inside a 200 MHz scope's band")

# ---------------------------------------------------------------- 5. ADC / FFT
print("\n=== 5. Scope ADC and FFT dynamic range ===")
for enob in [6, 7, 8, 10, 12]:
    snr = 6.02 * enob + 1.76
    print(f"  ENOB {enob:2d}: full-scale sine SNR {snr:5.1f} dB")
for N in [1e3, 1e5, 1e6, 1e7]:
    pg = 10 * np.log10(N / 2)
    print(f"  FFT of {N:>9.0f} points: processing gain {pg:5.1f} dB -> noise floor per bin ~{-(6.02*7+1.76)-pg:6.1f} dBFS (ENOB 7)")
print("  -> spurs, not noise, limit the scope FFT: SFDR of an 8-bit scope ADC is typically 40-50 dBc (interleaving spurs)")
fs, N = 5e9, 1e6
for win, enbw_bins in [("rect", 1.0), ("Hann", 1.5), ("flat-top", 3.77)]:
    print(f"  fs 5 GS/s, N = 1e6, {win:8s}: RBW(ENBW) = {enbw_bins*fs/N/1e3:.1f} kHz")

# ---------------------------------------------------------------- 6. near-field loop probe
print("\n=== 6. H-field loop probe sensitivity V = w mu0 H A ===")
for d_mm in [3, 10, 25]:
    A = np.pi * (d_mm / 2000) ** 2
    out = []
    for f in [10e6, 100e6, 433e6, 915e6, 2.4e9]:
        v = 2 * np.pi * f * MU0 * 1.0 * A      # for H = 1 A/m
        out.append(f"{f/1e6:6.0f} MHz: {20*np.log10(v/1e-6):6.1f} dBuV")
    print(f"  loop diameter {d_mm:2d} mm, H = 1 A/m (0 dBuA/m): " + " | ".join(out))
# loop inductance and self-resonance (1-turn loop of wire radius a)
for d_mm in [10, 25]:
    R = d_mm / 2000
    a = 0.25e-3     # 0.5 mm wire / semi-rigid centre
    L = MU0 * R * (np.log(8 * R / a) - 2)
    C_stray = 1e-12
    print(f"  {d_mm} mm loop: L ~ {L*1e9:.1f} nH, with ~1 pF stray self-resonates near {1/(2*np.pi*np.sqrt(L*C_stray))/1e9:.1f} GHz;"
          f" into 50 ohm the 6 dB/oct rise flattens above R/(2 pi L) = {50/(2*np.pi*L)/1e6:.0f} MHz")
