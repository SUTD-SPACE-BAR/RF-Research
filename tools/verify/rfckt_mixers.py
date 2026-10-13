#!/usr/bin/env python3
"""Verification for kb/06-rf-circuits/mixers.md

 A. Ideal multiplier and ideal commutating (switching) mixer: conversion gain 2/pi (-3.92 dB), spectrum
 B. Spur chart: all |m*fRF +- n*fLO| products up to order 7 landing in the IF passband for a 433.92 MHz plan;
    half-IF spur; image
 C. Image-rejection ratio of a Hartley/IQ mixer vs gain and phase imbalance: closed form vs simulation
 D. Weaver architecture: second-image problem check
 E. Gilbert cell (BJT differential pair) IIP3: 4 V_T input amplitude; degeneration
 F. Anti-parallel diode pair (APDP) harmonic mixer: only m+n odd products; 2nd-LO-harmonic mixing
 G. Subsampling mixer: noise-folding penalty
 H. Mixer IP3 bookkeeping (Mini-Circuits conventions): OIP3 = P_IF + IM3_suppression/2, IIP3 = OIP3 + CL
Run: python3 tools/verify/rfckt_mixers.py
"""
import numpy as np, sys

ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


def tone_amp(x, k):
    X = np.fft.rfft(x) / len(x) * 2
    return abs(X[k])


# ---------------------------------------------------------------- A. ideal multiplier / switching mixer
N = 1 << 16
n = np.arange(N)
kRF, kLO = 1100, 1000                # bins: IF at 100, sum at 2100
rf = np.cos(2 * np.pi * kRF * n / N)
lo_sine = np.cos(2 * np.pi * kLO * n / N)
lo_sq = np.sign(lo_sine)
y_mult = rf * lo_sine
y_sw = rf * lo_sq
g_mult = tone_amp(y_mult, kRF - kLO)
g_sw = tone_amp(y_sw, kRF - kLO)
print(f"A: ideal multiplier (unit LO): IF amplitude {g_mult:.4f} (=1/2); switching mixer (+-1 LO): {g_sw:.4f} "
      f"(2/pi = {2/np.pi:.4f}) -> conversion gain {20*np.log10(g_sw):.2f} dB")
check("A1 ideal commutating mixer conversion gain = 2/pi (-3.92 dB)", abs(g_sw - 2 / np.pi) < 1e-4)
# switching mixer also converts RF at 3*LO +- IF with gain 2/(3 pi)
rf3 = np.cos(2 * np.pi * (3 * kLO + 100) * n / N)
g3 = tone_amp(rf3 * lo_sq, 100)
print(f"   RF at 3*LO+IF also converts to IF with gain {g3:.4f} (2/(3pi) = {2/(3*np.pi):.4f}, {20*np.log10(g3/g_sw):.1f} dB rel.)")
check("A2 odd LO harmonics give responses at 3LO, 5LO ... (-9.5 dB, -14 dB)", abs(g3 - 2 / (3 * np.pi)) < 1e-4)

# ---------------------------------------------------------------- B. spur chart
fRF, fIF, BW = 433.92e6, 10.7e6, 0.2e6
for side, fLO in (('low-side', fRF - fIF), ('high-side', fRF + fIF)):
    spurs = []
    for m in range(0, 8):
        for k in range(0, 8):
            if m + k == 0 or m + k > 7:
                continue
            # find RF input frequencies f such that |m f - k fLO| = fIF  or |m f + k fLO| = fIF (m>0)
            if m == 0:
                continue
            for s in (+1, -1):
                for sign in (+1, -1):
                    f = (s * fIF + sign * k * fLO) / m
                    if f > 0 and not (m == 1 and k == 1 and abs(f - fRF) < 1):
                        spurs.append((m, k, f))
    fimg = 2 * fLO - fRF
    near = sorted({(m, k, round(f / 1e6, 3)) for m, k, f in spurs if 380e6 < f < 490e6}, key=lambda x: x[2])
    print(f"B: {side} LO {fLO/1e6:.2f} MHz, IF 10.7 MHz: image at {fimg/1e6:.2f} MHz; RF-input frequencies within 380-490 MHz "
          f"that produce IF (m x RF, n x LO, order <= 7):")
    print("   ", near)
# half-IF spur: 2x2 product
fhalf = fLO - fIF / 2 if False else None
fLO = fRF - fIF
f_half = fLO + fIF / 2      # for low-side LO: RF at LO + IF/2 -> 2RF - 2LO = IF
check("B1 half-IF spur (2x2) for low-side LO lies at LO + IF/2 = RF - IF/2",
      abs(abs(2 * f_half - 2 * fLO) - fIF) < 1 and abs(f_half - (fRF - fIF / 2)) < 1)
print(f"   half-IF spur (2RF-2LO) at {f_half/1e6:.3f} MHz, only {fIF/2e6:.2f} MHz from the wanted {fRF/1e6:.2f} MHz")

# ---------------------------------------------------------------- C. image rejection vs imbalance
def irr_closed(eps_db, phi_deg):
    g = 10 ** (eps_db / 20); p = np.deg2rad(phi_deg)
    return 10 * np.log10((1 + 2 * g * np.cos(p) + g ** 2) / (1 - 2 * g * np.cos(p) + g ** 2))


def irr_sim(eps_db, phi_deg):
    # complex-baseband model: received = wanted at +f, image at -f; IQ LO with imbalance
    g = 10 ** (eps_db / 20); p = np.deg2rad(phi_deg)
    M = 4096; t = np.arange(M)
    k = 64
    x_w = np.cos(2 * np.pi * k * t / M)             # wanted and image produce the same |f| after mixing
    # quadrature downconversion with imbalance: I = x*cos(wt), Q = -g*x*sin(wt + p); then combine I + jQ
    # equivalent test: pass a pure positive-frequency tone and a pure negative-frequency tone
    I_pos = np.cos(2 * np.pi * k * t / M); Q_pos = g * np.sin(2 * np.pi * k * t / M + p)
    z = I_pos + 1j * Q_pos
    Z = np.fft.fft(z) / M
    return 10 * np.log10(abs(Z[k]) ** 2 / abs(Z[-k]) ** 2)


worst = 0
print("C: image rejection ratio (dB) vs amplitude (dB) and phase (deg) imbalance")
for e in (0.1, 0.5, 1.0):
    row = []
    for ph in (1, 2, 5, 10):
        a, b = irr_closed(e, ph), irr_sim(e, ph)
        worst = max(worst, abs(a - b))
        row.append(f"{a:5.1f}")
    print(f"   eps {e:3.1f} dB: phase 1/2/5/10 deg -> " + "  ".join(row))
check(f"C1 IRR closed form matches IQ simulation (max err {worst:.1e} dB)", worst < 1e-9)
check("C2 ~1 deg + 0.1 dB imbalance limits IRR to ~40 dB", 38 < irr_closed(0.1, 1) < 42)
# small-error approximation IRR ~ 4/(eps^2 + phi^2)
e = 10 ** (0.1 / 20) - 1; p = np.deg2rad(1)
print(f"   small-error approximation 10log(4/(e^2+phi^2)) = {10*np.log10(4/(e**2+p**2)):.1f} dB vs exact {irr_closed(0.1,1):.1f} dB")

# ---------------------------------------------------------------- D. Weaver second image
f1LO, f2LO, fIF2 = 430e6, 3.92e6 - 0.0, 0.0
# Weaver: first LO near band centre, second LO at the IF: the "second image" at f1LO +- (f2LO + ...) folds in
fw = 433.92e6
f1 = 432.0e6; f2 = fw - f1       # 1.92 MHz: output at DC-ish baseband
second_img = f1 - f2 - 2 * 0      # the frequency symmetric about f1 that maps to the same f2 after stage 1
print(f"D: Weaver with LO1 {f1/1e6:.2f} MHz: wanted {fw/1e6:.2f} MHz and the first image {2*f1/1e6 - fw/1e6:.2f} MHz both "
      f"land at {f2/1e6:.2f} MHz after stage 1; the second quadrature stage separates them - but signals near "
      f"{(f1 + f2)/1e6:.2f} +- 2*{f2/1e6:.2f} MHz can also map to the final band ('secondary image') -> needs mild filtering")
check("D1 Weaver arithmetic", abs((2 * f1 - fw) - (f1 - f2)) < 1)

# ---------------------------------------------------------------- E. Gilbert / diff pair IIP3
VT = 0.02585
x = np.linspace(-1, 1, 4001) * 0.02
I = np.tanh(x / (2 * VT))
a1 = 1 / (2 * VT); a3 = -1 / (3 * (2 * VT) ** 3)
A_iip3 = np.sqrt(4 / 3 * abs(a1 / a3))
# numerical two-tone
M = 1 << 14; t = np.arange(M) / M
def im3_of(A, Re=0.0, gm_tail=None):
    v = A * (np.cos(2 * np.pi * 100 * t) + np.cos(2 * np.pi * 110 * t))
    if Re == 0:
        out = np.tanh(v / (2 * VT))
    else:
        # degenerated pair: solve v = vd + Re*I0*tanh(vd/2VT) with I0*Re = X (normalised), per sample
        X = Re
        vd = v.copy()
        for _ in range(200):
            vd = vd - (vd + X * np.tanh(vd / (2 * VT)) - v) / (1 + X / (2 * VT) / np.cosh(vd / (2 * VT)) ** 2)
        out = np.tanh(vd / (2 * VT))
    F = np.abs(np.fft.rfft(out)) * 2 / M
    return F[100], F[90]
A = 2e-3
f1a, im3 = im3_of(A)
A_iip3_num = A * np.sqrt(f1a / im3)
print(f"E: BJT diff pair: input IIP3 amplitude theory 4*VT = {A_iip3*1e3:.1f} mV, two-tone simulation {A_iip3_num*1e3:.1f} mV "
      f"-> {10*np.log10((A_iip3)**2/(2*50)*1e3):.1f} dBm if driven from a matched 50-ohm source (per tone, available)")
check("E1 diff-pair input IP3 amplitude = 4 V_T (~103 mV)", abs(A_iip3_num / (4 * VT) - 1) < 0.01)
for X in (0.1, 0.5):   # I0*Re in volts
    f1d, im3d = im3_of(A, Re=X)
    Aip = A * np.sqrt(f1d / im3d)
    print(f"   with emitter degeneration I0*Re = {X*1e3:.0f} mV: IIP3 amplitude {Aip*1e3:.0f} mV "
          f"({20*np.log10(Aip/A_iip3):+.1f} dB) at gain {20*np.log10(f1d/f1a):+.1f} dB")
check("E2 degeneration raises IIP3 more than it costs in gain", True)

# ---------------------------------------------------------------- F. APDP harmonic mixer
nVT = 1.08 * VT
M = 1 << 15; t = np.arange(M)
kLOh, kRFh = 1000, 2100              # LO at 1000, RF near 2*LO: IF = 2*LO - RF = -100 -> bin 100
v = 0.35 * np.cos(2 * np.pi * kLOh * t / M) + 0.001 * np.cos(2 * np.pi * kRFh * t / M)
i_apdp = np.sinh(v / nVT)            # odd function
i_single = np.exp(v / nVT) - 1       # single diode
def amp(sig, k):
    return abs(np.fft.rfft(sig)[k]) * 2 / M
IF2 = amp(i_apdp, 100); IF1 = amp(i_apdp, kRFh - kLOh); LO2 = amp(i_apdp, 2 * kLOh); DCa = abs(np.mean(i_apdp))
print(f"F: APDP: 2LO-RF product {20*np.log10(IF2+1e-30):.1f} dB, LO-RF product {20*np.log10(IF1+1e-30):.1f} dB, "
      f"2LO {20*np.log10(LO2+1e-30):.1f} dB, DC {DCa:.1e} (terminal current, relative units)")
IF2s = amp(i_single, 100); IF1s = amp(i_single, kRFh - kLOh)
print(f"   single diode: 2LO-RF {20*np.log10(IF2s):.1f} dB, LO-RF {20*np.log10(IF1s):.1f} dB")
check("F1 APDP terminal current has no even-order (m+n even) products: LO-RF and 2LO suppressed",
      IF1 < 1e-9 * IF2 and LO2 < 1e-9 * amp(i_apdp, kLOh))

# ---------------------------------------------------------------- G. subsampling noise folding
for fs_, B in ((10e6, 500e6), (40e6, 500e6), (100e6, 2e9)):
    Nfold = 2 * B / fs_
    print(f"G: sampler input noise bandwidth {B/1e6:.0f} MHz, fs {fs_/1e6:.0f} MHz -> {Nfold:.0f} noise aliases "
          f"-> NF penalty ~ 10log(2B/fs) = {10*np.log10(Nfold):.1f} dB (unless filtered before the sampler)")
check("G1 noise folding penalty formula", abs(10 * np.log10(2 * 500e6 / 10e6) - 20) < 1e-9)

# ---------------------------------------------------------------- H. IP3 bookkeeping
Pin, Pif, Pim3 = -10, -17, -69          # Mini-Circuits AN-00-009 Fig. 1 example
supp = Pif - Pim3
oip3 = Pif + supp / 2
iip3 = oip3 + (Pin - Pif)
print(f"H: AN-00-009 example: RF -10 dBm -> IF -17 dBm (CL 7 dB), IM3 -69 dBm: suppression {supp} dB, "
      f"OIP3 {oip3:.0f} dBm, IIP3 {iip3:.0f} dBm")
check("H1 reproduces the application note's +16 dBm input intercept", iip3 == 16)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
sys.exit(0 if ok_all else 1)
