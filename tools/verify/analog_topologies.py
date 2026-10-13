#!/usr/bin/env python3
"""Verification script for kb/05-analog-electronics/amplifier-topologies.md

 1. Resistive-feedback (shunt-shunt RF + series RE) gain block: symbolic Zin, Av, match condition RF*RE = Z0^2,
    S21 = 1 - RF/Z0; effect of finite gm; ngspice check with a real (SiGe-like) transistor.
 2. Stage formulas (CE, CE+RE, CB, CC, cascode Rout) at a sample bias.
 3. Open-circuit time constants (OCTC) bandwidth of a CE stage vs exact pole (ngspice AC).
 4. Intrinsic IIP3: single BJT (exponential) sqrt(8) VT, diff pair (tanh) 4 VT, and degeneration improvement,
    by two-tone FFT.
 5. Common-base input match 1/gm = 50 ohm and its noise factor 1 + 1/(2 gm Rs).
 6. Current mirrors: simple 1/(1+2/beta), Wilson, Widlar; Darlington composite gm = gm2/2.
 7. Feedback: Zin, Zout scaling by (1+T).
Run: python3 tools/verify/analog_topologies.py
"""
import os, sys
import numpy as np
import sympy as sp
from scipy.optimize import brentq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
k = 1.380649e-23; q = 1.602176634e-19; T = 300.0; VT = k * T / q

print("=== 1. Resistive-feedback gain block (ideal transistor, gm -> inf) ===")
vb, vc, Vs, RF, RE, RL, Rs, Z0 = sp.symbols('v_b v_c V_s R_F R_E R_L R_s Z_0', positive=True)
# KCL at collector: vc/RL + vb/RE + (vc - vb)/RF = 0 ; transistor current = vb/RE (gm->inf, no base current)
Av = sp.simplify(sp.solve(sp.Eq(vc / RL + vb / RE + (vc - vb) / RF, 0), vc)[0] / vb)
Zin = sp.simplify(RF / (1 - Av))
print("Av = vc/vb =", Av)
print("Zin =", sp.simplify(Zin))
sol = sp.solve(sp.Eq(Zin.subs(RL, Z0), Z0), RE)
print("Zin = Z0 (with RL = Z0) requires RE =", sol)
S21 = sp.simplify((Av).subs(RL, Z0).subs(RE, Z0**2 / RF))
print("S21 at match (= Av since vb = Vs/2) =", sp.factor(S21))
for RFv in (250, 500, 1000):
    s21 = 1 - RFv / 50
    print(f"  RF={RFv:5d}, Z0=50: RE = {2500/RFv:5.2f} ohm, S21 = {s21:.0f} ({20*np.log10(abs(s21)):.1f} dB)")
# output impedance: drive the output, input terminated in Z0
# finite gm: transistor current = gm*vbe, vbe = vb - ve, ve = ic*RE -> ic = vb/(RE + 1/gm)
print("finite gm: replace RE by RE' = RE + 1/gm, e.g. IC = 20 mA -> 1/gm =", round(VT / 20e-3, 2), "ohm")

try:
    from analog_ngspice import run_netlist
    IC_target = 20e-3
    net = """
* single-transistor resistive-feedback gain block, RF=500, RE=3.7 (+1/gm ~1.3), 50-ohm ports
.model QS NPN(IS=5e-16 BF=250 VAF=30 TF=2.5p CJE=0.3p CJC=0.08p RB=5 RE=0 RC=2)
VCC vcc 0 DC 8
* collector bias through choke from a resistor (constant-current-ish, like MMIC biasing)
Rbias vcc ch 150
Lch ch c 10u
Q1 c b e QS
RE e 0 3.7
RF c bf 500
CF bf b 100n
* base DC bias divider fed from the collector through a choke (DC feedback only)
RB1 c bb 10k
LB bb b 10u
RB2 b 0 2.65k
* ports
Vin src 0 DC 0 AC 1
Rsrc src in 50
Cin in b 100n
Cout c out 100n
Rload out 0 50
.ac dec 20 1MEG 20G
.end
"""
    r = run_netlist(net, ["frequency", "v(in)", "v(out)", "v(src)", "i(vin)"])
    f = np.real(r["frequency"]); vin = r["v(in)"]; vout = r["v(out)"]
    Iin = -r["i(vin)"]
    Zin = vin / Iin - 0  # impedance looking into 'in' node (right of Rsrc): vin / current through Rsrc
    Zin = vin / ((r["v(src)"] - vin) / 50)
    S11 = (Zin - 50) / (Zin + 50)
    S21 = 2 * vout / r["v(src)"]
    for fq in (10e6, 100e6, 433e6, 915e6, 2.4e9):
        i = np.argmin(abs(f - fq))
        print(f"  ngspice f={f[i]/1e6:7.1f} MHz: |S21|={20*np.log10(abs(S21[i])):5.2f} dB, |S11|={20*np.log10(abs(S11[i])):6.1f} dB, Zin={Zin[i].real:6.1f}{Zin[i].imag:+6.1f}j")
    print("  (ideal-transistor prediction: S21 = -9 -> 19.1 dB, S11 -> -inf; finite loop gain and rb lower S21 slightly)")
except Exception as e:
    print("ngspice step skipped:", e)

print("\n=== 2. Stage formulas at IC = 1 mA, beta 200, VA 75 V ===")
IC = 1e-3; beta = 200; VA = 75; gm = IC / VT; rpi = beta / gm; ro = VA / IC; re = 1 / gm
RC, REv, Rsig = 5e3, 500, 1e3
print(f"CE: Av = -gm (RC||ro) = {-gm*(RC*ro/(RC+ro)):.1f}; Rin = r_pi = {rpi/1e3:.2f}k; Rout = RC||ro = {RC*ro/(RC+ro)/1e3:.2f}k")
print(f"CE+RE: Av ~ -RC/(re+RE) = {-RC/(re+REv):.2f}; Rin = r_pi + (beta+1) RE = {(rpi+(beta+1)*REv)/1e3:.1f}k; Gm = gm/(1+gm RE) = {gm/(1+gm*REv)*1e3:.3f} mS")
print(f"CB: Rin = re = {re:.1f} ohm; Av = gm RC = {gm*RC:.0f}; current gain alpha = {beta/(beta+1):.4f}")
print(f"CC: Av = RE/(re+RE) = {REv/(re+REv):.3f} (RE=500); Rout = re + Rsig/(beta+1) = {re + Rsig/(beta+1):.1f} ohm (Rsig=1k)")
Rout_cascode = ro * (1 + gm * (rpi * 1e9 / (rpi + 1e9)))  # ro(1 + gm (r_pi||Re)), Re large -> ~beta ro
print(f"cascode Rout ~ ro (1 + gm r_pi) ~ beta ro = {Rout_cascode/1e6:.1f} Mohm (vs ro = {ro/1e3:.0f} k); cascode gain -gm Rout_cascode = {gm*Rout_cascode:.0f} (if loaded by an ideal current source)")

print("\n=== 3. OCTC bandwidth of a CE stage vs exact ===")
Rs, rb, RL = 1e3, 50.0, 5e3
Cpi, Cmu = 10e-12, 2e-12
Rs_eff = (Rs + rb) * rpi / (Rs + rb + rpi)
R_pi0 = Rs_eff
R_mu0 = Rs_eff + RL + gm * Rs_eff * RL
tau = Cpi * R_pi0 + Cmu * R_mu0
f_octc = 1 / (2 * np.pi * tau)
print(f"OCTC: R_pi0={R_pi0:.0f}, R_mu0={R_mu0/1e3:.1f}k, tau={tau*1e9:.2f} ns -> f3dB ~ {f_octc/1e6:.3f} MHz")
try:
    net = f"""
* CE stage hybrid-pi for OCTC check
Vs s 0 AC 1
Rs s b {Rs}
Rb b bp {rb}
Rpi bp 0 {rpi}
Cpi bp 0 {Cpi}
Cmu bp c {Cmu}
G1 c 0 bp 0 {gm}
RL c 0 {RL}
.ac dec 200 10k 1G
.end
"""
    r = run_netlist(net, ["frequency", "v(c)"])
    f = np.real(r["frequency"]); H = np.abs(r["v(c)"])
    f3 = np.exp(np.interp(-3.0103, (20 * np.log10(H / H[0]))[::-1], np.log(f)[::-1]))
    print(f"ngspice exact -3 dB: {f3/1e6:.3f} MHz  (low-f gain {20*np.log10(H[0]):.1f} dB)")
except Exception as e:
    print("ngspice step skipped:", e)

print("\n=== 4. Intrinsic IIP3 by two-tone simulation ===")
def two_tone_iip3(f_nl, amps):
    N = 4096; n = np.arange(N)
    k1, k2 = 101, 111
    res = []
    for A in amps:
        v = A * (np.cos(2 * np.pi * k1 * n / N) + np.cos(2 * np.pi * k2 * n / N))
        y = f_nl(v)
        Y = np.abs(np.fft.rfft(y)) / N * 2
        fund = Y[k1]; im3 = Y[2 * k1 - k2]
        res.append((A, fund, im3))
    # extrapolate from the smallest amplitude: IIP3 amplitude where fund = im3 (slopes 1 and 3)
    A, fund, im3 = res[0]
    return A * np.sqrt(fund / im3)
ex = lambda v: np.exp(v / VT) - 1
th = lambda v: np.tanh(v / (2 * VT))
A_ex = two_tone_iip3(ex, [0.5e-3])
A_th = two_tone_iip3(th, [0.5e-3])
print(f"single BJT (exp): IIP3 input amplitude = {A_ex*1e3:.1f} mV peak per tone (theory sqrt(8) VT = {np.sqrt(8)*VT*1e3:.1f} mV)")
print(f"diff pair (tanh): IIP3 = {A_th*1e3:.1f} mV peak per tone, differential (theory 4 VT = {4*VT*1e3:.1f} mV)")
# degenerated BJT: solve ic from v = VT ln(1 + ic/IC0)... use implicit: v_in = vbe + ic*RE, ic = IC0 (exp(vbe/VT) - 1) small-signal about bias IC0
def degenerated(IC0, REv):
    def f_nl(v):
        out = np.empty_like(v)
        for i, vi in enumerate(v):
            g = lambda ic: VT * np.log1p(ic / IC0) + ic * REv - vi
            out[i] = brentq(g, -IC0 * (1 - 1e-12), 50 * IC0 + 10 * abs(vi) / max(REv, 1e-3))
        return out
    return f_nl
# series-feedback algebra: b1 = a1/(1+x), b3 = (a3(1+x) - 2 a2^2 RE)/(1+x)^5 with x = gm RE
# for the exponential this gives A_IIP3 = sqrt(8) VT (1+x)^2 / sqrt(|1-2x|)  (IM3 null at gm RE = 1/2)
for gmRE in (0, 0.25, 0.5, 1, 3, 10):
    IC0 = 1e-3; REv = gmRE / (IC0 / VT)
    if gmRE == 0:
        A = A_ex
    else:
        A = two_tone_iip3(degenerated(IC0, REv), [0.5e-3 * (1 + gmRE)])
    pred = (1 + gmRE)**2 / np.sqrt(abs(1 - 2 * gmRE)) if gmRE != 0.5 else np.inf
    print(f"gm*RE = {gmRE:5.2f}: IIP3 input amplitude = {A*1e3:9.1f} mV ; ratio to undegenerated = {A/A_ex:8.2f} ; theory (1+x)^2/sqrt|1-2x| = {pred:8.2f}")
print("(at gm*RE = 0.5 the third-order term cancels; the residual is set by 5th order / numerical floor)")

print("\n=== 5. Common-base input match ===")
Rs = 50.0
IC = VT / Rs
print(f"1/gm = 50 ohm at IC = VT/50 = {IC*1e3:.3f} mA; NF (collector shot noise only) = 1 + 1/(2 gm Rs) = 1.5 -> {10*np.log10(1.5):.2f} dB")
print(f"MOS common-gate analogue: F = 1 + gamma/alpha, gamma=2/3, alpha=1 -> {10*np.log10(1+2/3):.2f} dB")

print("\n=== 6. Mirrors and Darlington ===")
for beta in (50, 100, 200):
    print(f"beta={beta}: simple mirror Io/Iref = 1/(1+2/beta) = {1/(1+2/beta):.4f}; with beta-helper 1/(1+2/(beta(beta+1))) = {1/(1+2/(beta*(beta+1))):.6f}; Wilson ~ 1/(1+2/(beta^2+2 beta)) = {1/(1+2/(beta**2+2*beta)):.6f}")
Iref = 1e-3
for Io in (100e-6, 10e-6):
    R = VT * np.log(Iref / Io) / Io
    print(f"Widlar: Iref 1 mA -> Io {Io*1e6:.0f} uA needs RE = VT ln(Iref/Io)/Io = {R:.0f} ohm")
IC2 = 10e-3; beta2 = 100
gm2 = IC2 / VT; re1 = VT / (IC2 / beta2); rpi2 = beta2 / gm2
print(f"Darlington: Q1 re = {re1:.0f} ohm equals Q2 r_pi = {rpi2:.0f} ohm -> vin splits equally -> composite gm = gm2/2 = {gm2/2*1e3:.0f} mS")

print("\n=== 7. Feedback impedance scaling ===")
a, f_ = 1e4, 0.01
Tloop = a * f_
print(f"a={a:.0f}, f={f_}: T={Tloop:.0f}; closed-loop gain a/(1+T) = {a/(1+Tloop):.3f} (1/f={1/f_:.0f}); gain error = {100/(1+Tloop):.2f} %")
print(f"series-mixing input: Zin x (1+T) = x{1+Tloop:.0f}; shunt-sampling output: Zout / (1+T) = /{1+Tloop:.0f}")

print("\n=== 8. Worked-example checks ===")
IC = 1e-3; gm = IC / VT; rpi = 200 / gm
Rs2 = (1e3 + 50) * rpi / (1e3 + 50 + rpi)
b1_ce = 10e-12 * Rs2 + 2e-12 * (Rs2 + 5e3 + gm * Rs2 * 5e3)
re2 = 1 / gm
b1_cas = 10e-12 * Rs2 + 2e-12 * (Rs2 + re2 + gm * Rs2 * re2) + 10e-12 * re2 + 2e-12 * 5e3
print(f"cascode OCTC: b1 CE = {b1_ce*1e9:.1f} ns ({1/(2*np.pi*b1_ce)/1e6:.3f} MHz); cascode b1 = {b1_cas*1e9:.1f} ns ({1/(2*np.pi*b1_cas)/1e6:.2f} MHz); improvement x{b1_ce/b1_cas:.1f}")
x = gm * 100
r = (1 + x)**2 / np.sqrt(abs(1 - 2 * x))
print(f"degenerated IF stage RE=100: x={x:.2f}, IIP3 x{r:.2f} ({20*np.log10(r):.1f} dB) -> {np.sqrt(8)*VT*r*1e3:.0f} mV; gain -{20*np.log10(1+x):.1f} dB; OIP3 +{20*np.log10(r)-20*np.log10(1+x):.1f} dB")
print(f"MMIC bias 5 V, Vd 3.3 V, Id 35 mA: Rbias = {(5-3.3)/0.035:.1f} ohm")
