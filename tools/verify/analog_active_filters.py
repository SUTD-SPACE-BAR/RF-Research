#!/usr/bin/env python3
"""Verification script for kb/05-analog-electronics/active-filters.md

 1. Sympy derivation of the unity-gain Sallen-Key and MFB low-pass transfer functions (w0, Q, gain).
 2. Design tables: per-section f0/fc and Q for Butterworth, Bessel (-3 dB normalised), 0.5 dB and 1 dB Chebyshev, orders 2-6.
 3. Worked design: 4th-order Butterworth 1 kHz anti-alias filter (two unity-gain SK sections) -> response check.
 4. Sensitivity: Monte Carlo of f0 and Q with 1 % R, 5 % C for SK (unity gain, equal-R), SK equal-component (K = 3 - 1/Q), MFB.
 5. Finite op-amp GBW: Q enhancement / f0 shift of unity-gain SK vs GBW/f0; SK stop-band rebound with op-amp output impedance vs MFB.
 6. Anti-alias order selection for an ADC; ngspice check of one SK section.
Run: python3 tools/verify/analog_active_filters.py
"""
import os, sys
import numpy as np
import sympy as sp
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
rng = np.random.default_rng(1)

print("=== 1. Symbolic transfer functions ===")
s = sp.symbols('s')
R1, R2, R3, C1, C2, Vi, Vo, Va, Vm = sp.symbols('R1 R2 R3 C1 C2 V_i V_o V_a V_m')
# Unity-gain Sallen-Key LP: Vi -R1- a -R2- m ; C1 from a to Vo (feedback); C2 from m to ground; buffer Vo = Vm
eqs = [sp.Eq((Vi - Va) / R1, (Va - Vm) / R2 + (Va - Vo) * s * C1), sp.Eq((Va - Vm) / R2, Vm * s * C2), sp.Eq(Vo, Vm)]
sol = sp.solve(eqs, [Va, Vm, Vo], dict=True)[0]
H_sk = sp.simplify(sol[Vo] / Vi)
num, den = sp.fraction(sp.together(H_sk))
den = sp.Poly(sp.expand(den), s)
a2, a1, a0 = den.all_coeffs()
print("SK (unity gain) H =", sp.factor(H_sk))
print("  w0^2 =", sp.simplify(a0 / a2), "; w0/Q =", sp.simplify(a1 / a2), "-> Q =", sp.simplify(sp.sqrt(a0 / a2) / (a1 / a2)))
# MFB LP: Vi -R1- a ; a -R2- Vo (feedback); a -R3- m (inverting input, virtual ground m=0); C1 from a to ground; C2 from m to Vo
Vm0 = 0
eqs = [sp.Eq((Vi - Va) / R1, Va * s * C1 + (Va - Vo) / R2 + (Va - Vm0) / R3), sp.Eq((Va - Vm0) / R3, (Vm0 - Vo) * s * C2)]
sol = sp.solve(eqs, [Va, Vo], dict=True)[0]
H_mfb = sp.simplify(sol[Vo] / Vi)
num, den = sp.fraction(sp.together(H_mfb))
den = sp.Poly(sp.expand(den), s)
b2, b1, b0 = den.all_coeffs()
print("MFB H =", sp.factor(H_mfb))
print("  DC gain =", sp.simplify(H_mfb.subs(s, 0)), "; w0^2 =", sp.simplify(b0 / b2), "; w0/Q =", sp.simplify(b1 / b2))

print("\n=== 2. Design tables (per 2nd-order section: f0/fc, Q; odd orders have a real pole f/fc) ===")
def sections(z, p):
    out = []
    for pole in p:
        if pole.imag > 1e-12:
            w0 = abs(pole); Q = w0 / (-2 * pole.real)
            out.append(("biquad", w0, Q))
        elif abs(pole.imag) < 1e-12:
            out.append(("real", abs(pole), 0.5))
    return sorted(out, key=lambda x: x[2])
for name, fn in (("Butterworth", lambda n: signal.buttap(n)),
                 ("Bessel (-3dB norm)", lambda n: signal.besselap(n, norm='mag')),
                 ("Chebyshev 0.5 dB", lambda n: signal.cheb1ap(n, 0.5)),
                 ("Chebyshev 1 dB", lambda n: signal.cheb1ap(n, 1.0))):
    print(name)
    for n in range(2, 7):
        z, p, kk = fn(n)
        # normalise Chebyshev to -3 dB frequency = 1 for comparability? keep ripple-band edge = 1 (standard tables)
        secs = sections(z, p)
        txt = "; ".join(f"{'real' if t=='real' else 'SOS'} f0={w:.4f}" + (f" Q={Q:.4f}" if t != 'real' else "") for t, w, Q in secs)
        print(f"  n={n}: {txt}")

print("\n=== 3. 4th-order Butterworth, fc = 1 kHz, two unity-gain SK sections (R = 10k) ===")
fc = 1e3; R = 10e3
z, p, kk = signal.buttap(4)
secs = [x for x in sections(z, p) if x[0] == 'biquad']
comps = []
for _, w0n, Q in secs:
    w0 = 2 * np.pi * fc * w0n
    # equal R: w0 = 1/(R sqrt(C1 C2)), Q = 0.5 sqrt(C1/C2)
    C2v = 1 / (2 * Q * w0 * R)
    C1v = 4 * Q**2 * C2v
    comps.append((C1v, C2v, Q))
    print(f"  section Q={Q:.4f}: C1 (feedback) = {C1v*1e9:.3f} nF, C2 (to ground) = {C2v*1e9:.3f} nF")
def sk_tf(R1v, R2v, C1v, C2v):
    return [1.0], [R1v * R2v * C1v * C2v, C2v * (R1v + R2v), 1.0]
w = 2 * np.pi * np.array([100, 500, 1000, 2000, 5000, 10000])
H = np.ones_like(w, dtype=complex)
for C1v, C2v, Q in comps:
    b, a = sk_tf(R, R, C1v, C2v)
    _, h = signal.freqs(b, a, w); H *= h
bb, aa = signal.butter(4, 2 * np.pi * fc, analog=True)
_, Hideal = signal.freqs(bb, aa, w)
for f_, h, hi in zip(w / 2 / np.pi, H, Hideal):
    print(f"  f={f_:6.0f} Hz: |H| = {20*np.log10(abs(h)):8.3f} dB (ideal Butterworth {20*np.log10(abs(hi)):8.3f} dB)")
# with E24/E12 standard values
def nearest(val, series):
    dec = 10**np.floor(np.log10(val)); cand = np.array(series) * dec
    cand = np.concatenate([cand / 10, cand, cand * 10])
    return cand[np.argmin(abs(cand - val))]
E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
Hs = np.ones_like(w, dtype=complex)
for C1v, C2v, Q in comps:
    b, a = sk_tf(R, R, nearest(C1v, E12), nearest(C2v, E12))
    _, h = signal.freqs(b, a, w); Hs *= h
    print(f"  E12 caps: C1={nearest(C1v,E12)*1e9:.2f} nF C2={nearest(C2v,E12)*1e9:.2f} nF")
print("  with E12 capacitors: |H| at 1 kHz =", round(20*np.log10(abs(Hs[2])), 2), "dB, at 10 kHz =", round(20*np.log10(abs(Hs[-1])), 1), "dB")

print("\n=== 4. Monte Carlo sensitivity (1 % R, 5 % C, 20000 trials) ===")
def mc(Q_target, topology, N=20000):
    w0t = 1.0
    if topology == "SK unity, equal R":
        Rn = 1.0; C2n = 1 / (2 * Q_target * w0t * Rn); C1n = 4 * Q_target**2 * C2n
        r1 = Rn * (1 + 0.01 * rng.standard_normal(N)); r2 = Rn * (1 + 0.01 * rng.standard_normal(N))
        c1 = C1n * (1 + 0.05 * rng.standard_normal(N)); c2 = C2n * (1 + 0.05 * rng.standard_normal(N))
        w0 = 1 / np.sqrt(r1 * r2 * c1 * c2); Q = np.sqrt(r1 * r2 * c1 * c2) / (c2 * (r1 + r2))
    elif topology == "SK equal-component, K=3-1/Q":
        K = 3 - 1 / Q_target
        r1 = 1 + 0.01 * rng.standard_normal(N); r2 = 1 + 0.01 * rng.standard_normal(N)
        c1 = 1 + 0.05 * rng.standard_normal(N); c2 = 1 + 0.05 * rng.standard_normal(N)
        # gain set by resistor ratio with 1 % resistors: K = 1 + Rb/Ra
        Ra = 1 + 0.01 * rng.standard_normal(N); Rb = (K - 1) * (1 + 0.01 * rng.standard_normal(N))
        Kk = 1 + Rb / Ra
        # SK with gain K: den = s^2 R1R2C1C2 + s (R1 C2 + R2 C2 + R1 C1 (1-K)) + 1
        w0 = 1 / np.sqrt(r1 * r2 * c1 * c2)
        Q = np.sqrt(r1 * r2 * c1 * c2) / (r1 * c2 + r2 * c2 + r1 * c1 * (1 - Kk))
    elif topology == "MFB, gain -1":
        # choose R1=R2=R3... standard: R2=R1 (gain -1), R3 free; w0^2 = 1/(R2 R3 C1 C2), w0/Q = (1/C1)(1/R1+1/R2+1/R3)
        Rn = 1.0
        # pick C2 = 1, then need C1 : Q = sqrt(C1/C2) sqrt(R2R3)/(R2R3/R1 + R2 + R3) -> with all R = 1: Q = sqrt(C1/C2)/3
        C2n = 1.0 / (3 * Q_target); C1n = 9 * Q_target**2 * C2n
        r1, r2, r3 = (Rn * (1 + 0.01 * rng.standard_normal(N)) for _ in range(3))
        c1 = C1n * (1 + 0.05 * rng.standard_normal(N)); c2 = C2n * (1 + 0.05 * rng.standard_normal(N))
        w0 = 1 / np.sqrt(r2 * r3 * c1 * c2)
        Q = w0 * c1 / (1 / r1 + 1 / r2 + 1 / r3)
    Q0 = np.median(Q)
    bad = np.mean((Q <= 0) | (abs(Q / Q_target - 1) > 0.2)) * 100
    good = Q[Q > 0]
    robust = 1.4826 * np.median(abs(good / Q_target - 1)) * 100  # MAD-based sigma
    return np.std(w0) / np.mean(w0) * 100, robust, Q0, bad
for Qt in (0.7071, 2.0, 5.0):
    for topo in ("SK unity, equal R", "SK equal-component, K=3-1/Q", "MFB, gain -1"):
        sw, sq, Q0, bad = mc(Qt, topo)
        print(f"  Q={Qt:6.4f} {topo:28s}: sigma(f0) = {sw:5.2f} %, robust sigma(Q) = {sq:6.2f} %, trials with Q off by >20 % or unstable: {bad:5.1f} %")

print("\n=== 5. Finite GBW and output impedance ===")
def sk_with_opamp(f, R1v, R2v, C1v, C2v, GBW, Ro=0.0):
    # op-amp: A(s) = wt/s (integrator), follower; output impedance Ro in series before output node
    wv = 2 * np.pi * f; sv = 1j * wv
    A = 2 * np.pi * GBW / sv
    # unknowns: Va, Vm, Vo ; op-amp internal source Vx = A (Vm - Vo); Vo connected to Vx via Ro, loaded by C1 current
    M = np.zeros((len(f), 3, 3), dtype=complex); rhs = np.zeros((len(f), 3), dtype=complex)
    # node a: (Vi - Va)/R1 = (Va - Vm)/R2 + (Va - Vo) s C1  -> Va(1/R1 + 1/R2 + sC1) - Vm/R2 - Vo sC1 = Vi/R1
    M[:, 0, 0] = 1 / R1v + 1 / R2v + sv * C1v; M[:, 0, 1] = -1 / R2v; M[:, 0, 2] = -sv * C1v; rhs[:, 0] = 1 / R1v
    # node m: (Va - Vm)/R2 = Vm s C2
    M[:, 1, 0] = 1 / R2v; M[:, 1, 1] = -(1 / R2v + sv * C2v)
    # node o: (Vx - Vo)/Ro + (Va - Vo) s C1 = 0, Vx = A (Vm - Vo)  (Ro=0 -> Vo = A(Vm - Vo))
    if Ro == 0:
        M[:, 2, 1] = A; M[:, 2, 2] = -(1 + A)
    else:
        M[:, 2, 1] = A / Ro; M[:, 2, 2] = -(1 + A) / Ro - sv * C1v; M[:, 2, 0] = sv * C1v
    sol = np.linalg.solve(M, rhs[..., None])[..., 0]
    return sol[:, 2]
f0 = 1e3; Q = 0.7071; R = 10e3
C2v = 1 / (2 * Q * 2 * np.pi * f0 * R); C1v = 4 * Q**2 * C2v
f = np.logspace(1, 7, 6001)
for ratio in (1e6, 100, 30, 10, 3):
    Hv = sk_with_opamp(f, R, R, C1v, C2v, ratio * f0)
    mag = abs(Hv)
    pk = 20 * np.log10(mag.max())
    f3 = f[np.where(mag < 1 / np.sqrt(2))[0][0]]
    print(f"  SK Q=0.707 f0=1 kHz, GBW = {ratio:>9.0f} x f0: peaking {pk:5.2f} dB, f-3dB = {f3:7.1f} Hz")
# stop-band rebound: SK with op-amp Ro = 100 ohm, GBW 1 MHz vs MFB
Hsk = sk_with_opamp(f, R, R, C1v, C2v, 1e6, Ro=100.0)
for fq in (10e3, 100e3, 1e6, 5e6):
    i = np.argmin(abs(f - fq))
    ideal = 1 / abs(1 + 1j * (fq / f0) / Q - (fq / f0)**2)
    print(f"  SK (GBW 1 MHz, Ro 100 ohm) at {fq/1e3:7.0f} kHz: {20*np.log10(abs(Hsk[i])):7.1f} dB (ideal 2nd order {20*np.log10(ideal):7.1f} dB)")

print("\n=== 6. Anti-alias order selection and ngspice check ===")
fs, fpass, bits = 10e3, 1e3, 12
A_req = 6.02 * bits + 1.76
fstop = fs - fpass
for n in range(1, 9):
    att = 10 * np.log10(1 + (fstop / fpass)**(2 * n))  # Butterworth with fc = fpass
    ok = "OK" if att >= A_req else ""
    print(f"  Butterworth n={n}: attenuation at {fstop/1e3:.0f} kHz = {att:6.1f} dB (need {A_req:.1f} dB for {bits}-bit) {ok}")
try:
    from analog_ngspice import run_netlist
    C1a, C2a, _ = comps[0]
    net = f"""
* unity-gain Sallen-Key low-pass section (Butterworth 4th-order section 1), ideal op-amp as VCVS
Vin in 0 AC 1
R1 in a 10k
R2 a m 10k
C1 a out {C1a:.6e}
C2 m 0 {C2a:.6e}
E1 out 0 m out 1e6
.ac dec 100 10 100k
.end
"""
    r = run_netlist(net, ["frequency", "v(out)"])
    fr = np.real(r["frequency"]); hv = r["v(out)"]
    b, a = sk_tf(R, R, C1a, C2a)
    _, hth = signal.freqs(b, a, 2 * np.pi * fr)
    print(f"  ngspice vs analytic SK section: max |dB error| = {np.max(abs(20*np.log10(abs(hv)) - 20*np.log10(abs(hth)))):.4f} dB")
except Exception as e:
    print("  ngspice skipped:", e)

print("\n=== 7. High-Q section vs GBW; MFB stop-band with the same op-amp ===")
for Qh in (1.3066, 5.0):
    C2h = 1 / (2 * Qh * 2 * np.pi * f0 * R); C1h = 4 * Qh**2 * C2h
    for ratio in (1e6, 100, 30, 10):
        Hv = sk_with_opamp(f, R, R, C1h, C2h, ratio * f0)
        mag = abs(Hv)
        ideal_pk = Qh / np.sqrt(1 - 1 / (4 * Qh**2)) if Qh > 0.7072 else 1.0
        print(f"  SK Q={Qh:.3f}: GBW = {ratio:>9.0f} x f0 -> peak {20*np.log10(mag.max()):6.2f} dB (ideal {20*np.log10(ideal_pk):6.2f} dB) at {f[np.argmax(mag)]:7.1f} Hz")
def mfb_with_opamp(f, R1v, R2v, R3v, C1v, C2v, GBW, Ro=0.0):
    wv = 2 * np.pi * f; sv = 1j * wv
    A = 2 * np.pi * GBW / sv
    # unknowns Va, Vm (inverting input), Vo ; Vx = -A Vm ; output node via Ro
    M = np.zeros((len(f), 3, 3), dtype=complex); rhs = np.zeros((len(f), 3), dtype=complex)
    # node a: (Vi-Va)/R1 = Va sC1 + (Va-Vo)/R2 + (Va-Vm)/R3
    M[:, 0, 0] = 1/R1v + sv*C1v + 1/R2v + 1/R3v; M[:, 0, 1] = -1/R3v; M[:, 0, 2] = -1/R2v; rhs[:, 0] = 1/R1v
    # node m: (Va-Vm)/R3 = (Vm-Vo) sC2
    M[:, 1, 0] = 1/R3v; M[:, 1, 1] = -(1/R3v + sv*C2v); M[:, 1, 2] = sv*C2v
    # node o: (Vx - Vo)/Ro + (Va-Vo)/R2 + (Vm-Vo) sC2 = 0
    M[:, 2, 1] = -A/Ro + sv*C2v; M[:, 2, 2] = -1/Ro - 1/R2v - sv*C2v; M[:, 2, 0] = 1/R2v
    sol = np.linalg.solve(M, rhs[..., None])[..., 0]
    return sol[:, 2]
# MFB Q=0.707, f0=1 kHz, all R = 10k: Q = sqrt(C1/C2)/3 -> C1/C2 = 9 Q^2 ; w0 = 1/(R sqrt(C1 C2))
Rm = 10e3; ratio_c = 9 * 0.7071**2
C2m = 1 / (2 * np.pi * f0 * Rm * np.sqrt(ratio_c)); C1m = ratio_c * C2m
Hm = mfb_with_opamp(f, Rm, Rm, Rm, C1m, C2m, 1e6, Ro=100.0)
for fq in (10e3, 100e3, 1e6, 5e6):
    i = np.argmin(abs(f - fq))
    print(f"  MFB (GBW 1 MHz, Ro 100 ohm) at {fq/1e3:7.0f} kHz: {20*np.log10(abs(Hm[i])):7.1f} dB  (SK same op-amp: {20*np.log10(abs(Hsk[i])):7.1f} dB)")
