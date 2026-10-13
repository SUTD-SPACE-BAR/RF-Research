#!/usr/bin/env python3
"""W5-S10 checks for the new page 17/basic-bench-instruments and the bench leftovers in
17/bench-measurement-recipes (R11-R16).

A. Frequency counters: direct (+-1 count), prescaled, reciprocal, time-base and trigger errors.
B. Meters: analogue Ohm/V loading, average-responding vs true-RMS (form factors, crest factor).
C. Scope probe compensation: step error and the compensation corner frequency.
D. Dip meter / coupled resonators: reflected resistance, frequency pulling (mode splitting), critical coupling.
E. NanoVNA coupled-loop (transmission) resonator: Q_L from the 3 dB width, Q0 from the insertion loss.
F. Return-loss bridge + SA/TG: reading spread from bridge directivity.
G. Resistive tap vs coupler: coupling, line loading, effect of the resistor's parasitic capacitance.
H. LCR meter vs VNA: component reactance at LCR test frequencies vs at UHF.
I. WSPR/RBN/RSSI antenna comparisons: spread of a faded signal in dB and the sample size needed.
"""
import numpy as np

ok_all = True
def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(("PASS " if cond else "FAIL ") + name)

# ---------------------------------------------------------------- A
print("A: frequency counter errors")
f = 433.92e6
T = 1.0
print(f"  direct count, 1 s gate: +-{1/T:.0f} Hz = {1/T/f:.1e} relative at 433.92 MHz")
for name, tb in [("uncompensated crystal 5 ppm", 5e-6), ("TCXO 1 ppm", 1e-6), ("OCXO 1e-8", 1e-8), ("GPSDO 1e-11", 1e-11)]:
    print(f"  time base {name:28s}: +-{tb*f:10.4f} Hz at 433.92 MHz")
check("A1 a 5 ppm time base is +-2.17 kHz at 433.92 MHz, 2000x the +-1 count", abs(5e-6 * f - 2169.6) < 0.1)
N = 64
print(f"  prescaler /{N}, 1 s gate, direct counting of f/N: resolution +-{N/T:.0f} Hz")
check("A2 a /64 prescaler costs 64x resolution for the same gate (AN 200)", N / T == 64)
tres = 1e-9    # single-shot time resolution of a simple reciprocal counter (interpolated ones: 20-100 ps)
for fx in (1e3, 10e6, 433.92e6):
    direct = 1 / T
    recip = tres / T * fx
    print(f"  {fx/1e6:10.4f} MHz: direct +-{direct:.3g} Hz ({direct/fx:.1e}), reciprocal (1 ns) +-{recip:.3g} Hz ({tres/T:.0e})")
check("A3 at 1 kHz a reciprocal counter is 10^6 x finer than a direct counter (1 s gate)", (1 / T / 1e3) / (tres / T) > 0.99e6)
# trigger error (AN 200): rms = 1.4 sqrt(x^2 + en^2) / slew
def trig(A, fx, en, x=100e-6):
    return 1.4 * np.sqrt(x ** 2 + en ** 2) / (2 * np.pi * fx * A)
t1 = trig(0.5, 10e6, 1e-3)
t2 = trig(0.5, 50.0, 10e-3)
print(f"  trigger error: 10 MHz, 1 Vpp, 1 mV noise -> {t1*1e12:.0f} ps rms per edge; 50 Hz, 1 Vpp, 10 mV noise -> {t2*1e6:.0f} us")
check("A4 10 MHz 1 Vpp with 1 mV noise: ~45 ps per edge", abs(t1 * 1e12 - 44.8) < 1)
check("A5 single-period 50 Hz measurement with 10 mV noise errs ~0.45 % per edge (average many periods or filter)", 0.004 < t2 * 50 < 0.005)

# ---------------------------------------------------------------- B
print("\nB: meters")
Rth = 100e3
for name, Rin in [("analogue 20 kOhm/V on the 10 V range", 20e3 * 10), ("analogue 1 kOhm/V on 10 V", 1e3 * 10), ("DMM 10 MOhm", 10e6)]:
    print(f"  {name:38s}: reads {Rin/(Rin+Rth)*100:5.1f} % of a 100 kOhm-source node")
check("B1 20 kOhm/V on 10 V reads 2/3 of a 100 kOhm node", abs(200e3 / 300e3 - 2 / 3) < 1e-12)
t = np.linspace(0, 1, 200001)[:-1]
def meter(x):
    rms = np.sqrt(np.mean(x ** 2)); avg = np.mean(np.abs(x))
    return rms, avg * np.pi / (2 * np.sqrt(2)), np.max(np.abs(x)) / rms
waves = {"sine": np.sin(2 * np.pi * 5 * t), "square": np.sign(np.sin(2 * np.pi * 5 * t)),
         "triangle": 2 * np.abs(2 * ((5 * t) % 1) - 1) - 1,
         "10 % duty pulse (AC-coupled)": (((5 * t) % 1) < 0.1).astype(float) - 0.1}
res = {}
for k, x in waves.items():
    rms, avgresp, cf = meter(x)
    res[k] = (avgresp / rms - 1) * 100
    print(f"  {k:30s}: average-responding meter error {res[k]:+6.1f} %, crest factor {cf:.2f}")
check("B2 square reads +11.1 %, triangle -3.8 % on an average-responding meter",
      abs(res["square"] - 11.07) < 0.05 and abs(res["triangle"] + 3.77) < 0.05)
check("B3 a 10 % duty pulse train has crest factor 3 (AC-coupled)", abs(meter(waves["10 % duty pulse (AC-coupled)"])[2] - 3.0) < 0.01)

# ---------------------------------------------------------------- C
print("\nC: 10x probe compensation (R1 9 MOhm tip, R2 1 MOhm scope, C2 = cable + scope ~100 pF)")
R1, R2, C2 = 9e6, 1e6, 100e-12
C1_ok = C2 * R2 / R1
for mis in (0.0, -0.1, 0.1):
    C1 = C1_ok * (1 + mis)
    hf = C1 / (C1 + C2); lf = R2 / (R1 + R2)
    print(f"  C1 {C1*1e12:5.2f} pF ({mis*100:+.0f} %): HF/LF ratio {hf/lf:.3f} -> edge {'overshoots' if hf > lf * 1.001 else 'rounds' if hf < lf * 0.999 else 'flat'}")
tau = (R1 * R2 / (R1 + R2)) * (C1_ok + C2)
fcorner = 1 / (2 * np.pi * tau)
print(f"  settling tau {tau*1e6:.0f} us -> corner {fcorner:.0f} Hz: the 1 kHz calibrator square wave shows the error clearly")
check("C1 a 10 % mis-compensation is a ~9 % amplitude error above the ~1.6 kHz corner",
      abs((C1_ok * 1.1 / (C1_ok * 1.1 + C2)) / (R2 / (R1 + R2)) - 1.089) < 0.005 and 1000 < fcorner < 2500)

# ---------------------------------------------------------------- D
print("\nD: dip meter coupled to a resonant circuit")
f0 = 14e6; L1 = 1e-6; Q2 = 100
for k in (0.01, 0.03, 0.1):
    w0 = 2 * np.pi * f0
    Rrefl = k ** 2 * w0 * L1 * Q2
    split = (1 / np.sqrt(1 - k) - 1 / np.sqrt(1 + k)) * f0
    print(f"  k = {k:.2f}: reflected R into the dipper coil {Rrefl:7.1f} Ohm; coupled-mode split {split/1e3:6.1f} kHz ({split/f0*100:.1f} %)")
print(f"  critical coupling k_c = 1/sqrt(Q1 Q2) = {1/np.sqrt(50*Q2):.3f} for Q1 50, Q2 {Q2}")
check("D1 k = 0.1 splits the response by ~10 % (reads the wrong frequency); k = 0.01 by ~1 %",
      abs((1 / np.sqrt(0.9) - 1 / np.sqrt(1.1)) - 0.1006) < 0.002 and abs((1 / np.sqrt(0.99) - 1 / np.sqrt(1.01)) - 0.0100) < 0.0005)

# ---------------------------------------------------------------- E
print("\nE: NanoVNA two-loop transmission resonance")
for IL in (10, 20, 30, 40):
    s = 10 ** (-IL / 20)
    print(f"  insertion loss {IL} dB: Q0 = Q_L / (1 - |S21|) = Q_L x {1/(1-s):.3f}")
check("E1 at 30 dB insertion loss Q_L is within 3.3 % of Q0", abs(1 / (1 - 10 ** (-1.5)) - 1.0327) < 0.0005)
# simulate a series RLC between two weak couplings to confirm the 3 dB width gives Q_L
f0 = 433.92e6; Q0 = 200.0; L = 50e-9; C = 1 / ((2 * np.pi * f0) ** 2 * L); R = 2 * np.pi * f0 * L / Q0
ff = np.linspace(f0 * 0.97, f0 * 1.03, 200001)
w = 2 * np.pi * ff
n = 0.03    # loop-to-resonator turns ratio (weak coupling)
Zres = R + 1j * w * L + 1 / (1j * w * C)
Zs = 50 * n ** 2   # each 50 Ohm port reflected in series into the resonator
S21 = 2 * Zs / (Zres + 2 * Zs)
mag = np.abs(S21); pk = mag.max()
band = ff[mag >= pk / np.sqrt(2)]
QL = f0 / (band[-1] - band[0])
Q0_est = QL / (1 - pk)
print(f"  simulated: peak S21 {20*np.log10(pk):.1f} dB, Q_L {QL:.1f}, Q0 estimate {Q0_est:.1f} (true {Q0:.0f})")
check("E2 Q0 recovered within 1 % from Q_L and |S21|", abs(Q0_est - Q0) / Q0 < 0.01)

# ---------------------------------------------------------------- F
print("\nF: return-loss bridge + SA/TG (scalar): reading = |Gamma| +- 10^(-D/20)")
for D in (25, 30, 35, 40):
    d = 10 ** (-D / 20)
    G = 10 ** (-20 / 20)
    hi, lo = -20 * np.log10(G - d), -20 * np.log10(G + d)
    print(f"  bridge directivity {D} dB, DUT RL 20 dB: reads {lo:5.1f} ... {hi:5.1f} dB")
d35 = 10 ** (-35 / 20)
check("F1 a 35 dB bridge reads a 20 dB DUT as 18.6-21.7 dB", abs(-20 * np.log10(0.1 + d35) - 18.6) < 0.1 and abs(-20 * np.log10(0.1 - d35) - 21.7) < 0.1)

# ---------------------------------------------------------------- G
print("\nG: resistive tap on a matched 50 Ohm line (node Thevenin 25 Ohm) into a 50 Ohm instrument")
def tap(R, fx, Cp=0.0):
    Zr = 1 / (1 / R + 1j * 2 * np.pi * fx * Cp) if Cp > 0 else R
    k = 50 / (Zr + 50 + 25)            # instrument voltage / node voltage (approx., Thevenin 25 Ohm)
    Ysh = 1 / (Zr + 50)
    Gm = -(Ysh * 50) / (2 + Ysh * 50)  # mismatch the tap causes on the line
    return 20 * np.log10(abs(k)), -20 * np.log10(abs(Gm))
for R in (1000.0, 4950.0):
    for fx, Cp in [(1e6, 0.0), (433e6, 0.15e-12), (915e6, 0.15e-12)]:
        cdb, rl = tap(R, fx, Cp)
        print(f"  R {R:6.0f} Ohm, {fx/1e6:5.0f} MHz, Cp {Cp*1e12:.2f} pF: coupling {cdb:6.1f} dB, line RL {rl:5.1f} dB")
c1k = tap(1000.0, 1e6)[0]
c5k_dc = tap(4950.0, 1e6)[0]; c5k_915 = tap(4950.0, 915e6, 0.15e-12)[0]
check("G1 1 kOhm tap couples ~-26.6 dB and loads the line to RL ~33 dB", abs(c1k + 26.6) < 0.2 and abs(tap(1000.0, 1e6)[1] - 32.6) < 0.3)
check("G2 a 4.95 kOhm '-40 dB' tap reads > 10 dB high at 915 MHz because of 0.15 pF", c5k_915 - c5k_dc > 10)

# ---------------------------------------------------------------- H
print("\nH: LCR meter vs VNA — reactances")
for name, Lv, Cv in [("10 nH", 10e-9, None), ("100 nH", 100e-9, None), ("10 pF", None, 10e-12), ("100 nF", None, 100e-9)]:
    xs = []
    for fx in (1e3, 100e3, 1e6, 433e6):
        X = 2 * np.pi * fx * Lv if Lv else 1 / (2 * np.pi * fx * Cv)
        xs.append(f"{fx/1e6:g} MHz {X:.3g} Ohm")
    print(f"  {name:7s}: " + ", ".join(xs))
check("H1 10 nH is 6.3 mOhm at 100 kHz but 27 Ohm at 433 MHz", abs(2 * np.pi * 1e5 * 10e-9 - 6.28e-3) < 1e-5 and abs(2 * np.pi * 433e6 * 10e-9 - 27.2) < 0.1)

# ---------------------------------------------------------------- I
print("\nI: comparing antennas by received SNR/RSSI on a fading path")
sd_ray = 10 / np.log(10) * np.pi / np.sqrt(6)
x = 10 * np.log10(np.random.default_rng(3).exponential(1.0, 2_000_000))
print(f"  std of a Rayleigh-faded power in dB: {sd_ray:.2f} dB (MC {x.std():.2f} dB); 1 dB quantisation adds {1/np.sqrt(12):.2f} dB")
check("I1 Rayleigh power in dB has a 5.57 dB standard deviation", abs(sd_ray - 5.57) < 0.01 and abs(x.std() - sd_ray) < 0.02)
for sd_d, label in [(np.sqrt(2) * sd_ray, "independent fades on A and B"), (3.0, "partly correlated (alternating slots)")]:
    for delta in (1.0, 2.0, 3.0):
        n = (1.96 * sd_d / delta) ** 2
        print(f"  {label:38s} sigma_d {sd_d:4.1f} dB: n = {np.ceil(n):5.0f} pairs for a +-{delta:.0f} dB 95 % interval")
n1 = (1.96 * np.sqrt(2) * sd_ray / 1.0) ** 2
check("I2 resolving 1 dB with independent Rayleigh fades needs ~240 paired spots", 230 < n1 < 245)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
