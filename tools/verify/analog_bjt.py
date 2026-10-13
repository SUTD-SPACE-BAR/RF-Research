#!/usr/bin/env python3
"""Verification script for kb/05-analog-electronics/bjt-fundamentals-small-signal.md

 1. Small-signal parameters gm, r_pi, r_o, intrinsic gain; tempco of IC at fixed VBE.
 2. Ebers-Moll saturation voltage: numeric solve vs closed form.
 3. fT from hybrid-pi (1/2pi fT = tauF + (Cje+Cmu)/gm) vs ngspice |h21|=1 crossing.
 4. fmax: Mason's unilateral gain U of the hybrid-pi (rb, Cpi, Cmu, gm, ro) vs sqrt(fT/(8 pi rb Cmu)).
 5. Miller effect: exact input admittance of a CE stage vs Miller approximation.
 6. Bias stability: 4-resistor bias vs beta 100..400.
 7. Noise: Fmin = 1 + sqrt((1+2 gm rb)/beta), Ropt, optimum IC for a given Rs (cf. BFP740 at 6 mA).
Run: python3 tools/verify/analog_bjt.py
"""
import os, sys
import numpy as np
from scipy.optimize import brentq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
k = 1.380649e-23; q = 1.602176634e-19
T = 300.0; VT = k * T / q

print("=== 1. small-signal parameters ===")
beta, VA = 200.0, 75.0
for IC in (100e-6, 1e-3, 10e-3):
    gm = IC / VT; rpi = beta / gm; ro = VA / IC
    print(f"IC={IC*1e3:6.2f} mA gm={gm*1e3:7.2f} mS  r_pi={rpi/1e3:7.3f} k  r_o={ro/1e3:8.1f} k  gm*ro={gm*ro:6.0f} ({20*np.log10(gm*ro):.1f} dB)")
VBE = 0.65
dlnIC_dT = (1.12 - VBE + 3 * VT) / (VT * T)
print(f"IC tempco at fixed VBE (Eg=1.12, XTI=3, VBE=0.65): {dlnIC_dT*100:.1f} %/K;  via -2 mV/K / VT: {0.002/VT*100:.1f} %/K")

print("\n=== 2. Ebers-Moll saturation ===")
IS, bF, bR = 1e-14, 200.0, 4.0
def em(vbe, vbc):
    ef, er = np.exp(vbe / VT) - 1, np.exp(vbc / VT) - 1
    ic = IS * (ef - er) - IS / bR * er
    ib = IS / bF * ef + IS / bR * er
    return ic, ib
for IC, IB in ((10e-3, 1e-3), (10e-3, 0.5e-3), (1e-3, 0.1e-3), (10e-3, 0.1e-3)):
    # EM transport equations are linear in ef = exp(vbe/VT)-1 and er = exp(vbc/VT)-1
    A = np.array([[IS, -IS * (1 + 1 / bR)], [IS / bF, IS / bR]])
    ef, er = np.linalg.solve(A, [IC, IB])
    vbe, vbc = VT * np.log1p(ef), VT * np.log1p(er)
    bforced = IC / IB
    vce_formula = VT * np.log((1 + (bforced + 1) / bR) / (1 - bforced / bF))
    print(f"IC={IC*1e3:.0f} mA IB={IB*1e3:.2f} mA (forced beta {bforced:.0f}): VBE={vbe:.3f} VBC={vbc:.3f}  VCEsat numeric={1e3*(vbe-vbc):.1f} mV, formula={vce_formula*1e3:.1f} mV")
print("(intrinsic only; real VCEsat adds IC*(RC+RE) ohmic drops, e.g. 10 mA x 5 ohm = 50 mV)")

print("\n=== 3. fT: hybrid-pi formula vs ngspice ===")
IC = 5e-3
tauF, Cje, Cmu = 300e-12, 4e-12, 3e-12   # generic 2N3904-like
gm = IC / VT
fT_hand = 1 / (2 * np.pi * (tauF + (Cje + Cmu) / gm))
print(f"hand: gm={gm*1e3:.1f} mS -> fT = {fT_hand/1e6:.0f} MHz  (C_pi = gm tauF + Cje = {(gm*tauF+Cje)*1e12:.1f} pF)")
try:
    from analog_ngspice import run_netlist
    # Bias via ideal current source into base with collector at fixed VCE, AC current into base, measure ic/ib
    # Note: SPICE CJE/CJC are zero-bias values; at bias Cje(forward) > CJE and Cmu(VCB) < CJC, so use VJE, MJE small to keep ~const
    net = f"""
* fT extraction of a generic NPN (2N3904-like parameters)
.model QG NPN(IS=1e-14 BF=200 VAF=75 TF=300p CJE=4p VJE=0.75 MJE=0.01 CJC=3p VJC=0.75 MJC=0.01 RB=0 RE=0 RC=0)
VCC c 0 DC 5
Ib 0 b DC {IC/200:.6e} AC 1
Q1 c b 0 QG
.ac dec 50 1MEG 2G
.end
"""
    r = run_netlist(net, ["frequency", "i(vcc)"])
    f = np.real(r["frequency"]); h21 = np.abs(r["i(vcc)"])  # |ic| per 1 A ac base current
    idx = np.where(h21 < 1)[0][0]
    fT_sim = np.exp(np.interp(0, np.log(h21[idx-1:idx+1][::-1]), np.log(f[idx-1:idx+1][::-1])))
    # simpler: f at which |h21| = 1 (log interpolation)
    lf = np.log(f); lh = np.log(h21)
    fT_sim = np.exp(np.interp(0.0, lh[::-1], lf[::-1]))
    print(f"ngspice: |h21|=1 at {fT_sim/1e6:.0f} MHz; low-f h21 = {h21[0]:.1f}; beta x f at 50 MHz = {np.interp(50e6,f,h21)*50:.0f} MHz")
except Exception as e:
    print("ngspice step skipped:", e)

print("\n=== 4. fmax from Mason's U of the hybrid-pi ===")
def yparams(f, gm, rpi, Cpi, Cmu, rb, ro):
    w = 2 * np.pi * f
    ypi = 1 / rpi + 1j * w * Cpi
    ymu = 1j * w * Cmu
    # intrinsic (b'-e, c-e) Y matrix
    y11 = ypi + ymu; y12 = -ymu; y21 = gm - ymu; y22 = 1 / ro + ymu
    # add series rb at input: convert via Z
    Y = np.array([[y11, y12], [y21, y22]])
    Z = np.linalg.inv(Y)
    Z[0, 0] += rb
    return np.linalg.inv(Z)
def mason_U(Y):
    y11, y12, y21, y22 = Y[0, 0], Y[0, 1], Y[1, 0], Y[1, 1]
    return abs(y21 - y12)**2 / (4 * (y11.real * y22.real - y12.real * y21.real))
for (IC, beta, tauF, Cje, Cmu, rb, VA, label) in (
        (15e-3, 250, 2.5e-12, 0.3e-12, 0.08e-12, 5.0, 30, "SiGe HBT, BFP740-like"),
        (5e-3, 200, 300e-12, 4e-12, 3e-12, 20.0, 75, "2N3904-like")):
    gm = IC / VT; rpi = beta / gm; ro = VA / IC; Cpi = gm * tauF + Cje
    fT = gm / (2 * np.pi * (Cpi + Cmu))
    fmax_hand = np.sqrt(fT / (8 * np.pi * rb * Cmu))
    g = lambda f: np.log(mason_U(yparams(f, gm, rpi, Cpi, Cmu, rb, ro)))
    fmax_num = brentq(g, fT / 50, fT * 50)
    print(f"{label:22s}: fT={fT/1e9:7.3f} GHz, fmax hand sqrt(fT/(8 pi rb Cmu))={fmax_hand/1e9:7.3f} GHz, Mason U=1 at {fmax_num/1e9:7.3f} GHz")

print("\n=== 5. Miller effect ===")
IC = 1e-3; gm = IC / VT; beta = 200; rpi = beta / gm
Cpi, Cmu = 10e-12, 2e-12
for RL in (1e3, 5e3, 20e3):
    Av = -gm * RL
    Cmiller = Cpi + Cmu * (1 + gm * RL)
    # exact: input admittance at f with load RL (neglect ro), node b'
    f = 100e3
    w = 2 * np.pi * f
    ymu = 1j * w * Cmu
    # vout = -(gm - ymu) vin / (1/RL + ymu)
    Avx = -(gm - ymu) / (1 / RL + ymu)
    Yin = 1 / rpi + 1j * w * Cpi + ymu * (1 - Avx)
    print(f"RL={RL/1e3:5.1f}k Av={Av:7.1f}  Miller Cin={Cmiller*1e12:7.1f} pF  exact Cin(100 kHz)={Yin.imag/w*1e12:7.1f} pF  input pole with Rs=1k||r_pi: {1/(2*np.pi*(1e3*rpi/(1e3+rpi))*Cmiller)/1e6:6.2f} MHz")

print("\n=== 6. Bias stability (4-resistor bias) ===")
VCC, R1, R2, RC, RE, VBE = 5.0, 22e3, 6.8e3, 1.5e3, 470.0, 0.65
VTh = VCC * R2 / (R1 + R2); RTh = R1 * R2 / (R1 + R2)
for beta in (100, 200, 400):
    IC = beta * (VTh - VBE) / (RTh + (beta + 1) * RE)
    print(f"beta={beta:3d}: IC={IC*1e3:.3f} mA, VCE={VCC-IC*RC-IC*(beta+1)/beta*RE:.2f} V")
print(f"(VTh={VTh:.3f} V, RTh={RTh/1e3:.2f} k)")
for beta in (100, 200, 400):
    RB = 820e3
    IC = beta * (VCC - VBE) / RB
    print(f"  base-resistor-only bias RB=820k, beta={beta}: IC={IC*1e3:.2f} mA")

print("\n=== 7. Noise ===")
def Fmin(gm, rb, beta):
    return 1 + np.sqrt((1 + 2 * gm * rb) / beta)
def Ropt(gm, rb, beta):
    return np.sqrt(beta * (1 + 2 * gm * rb)) / gm
for IC, rb, beta in ((1e-3, 50, 100), (1e-3, 5, 250), (100e-6, 50, 100), (6e-3, 5, 250)):
    gm = IC / VT
    F = Fmin(gm, rb, beta)
    print(f"IC={IC*1e3:5.2f} mA rb={rb:3d} beta={beta}: Fmin={10*np.log10(F):.2f} dB  Ropt={Ropt(gm,rb,beta):7.1f} ohm")
# optimum IC for a given Rs (low-frequency): gm_opt = sqrt(beta)/Rs  (from dF/dgm = 0 with F = 1 + rb/Rs + 1/(2 gm Rs) + gm Rs/(2 beta))
for Rs, beta, rb in ((50, 250, 5), (50, 100, 20), (1e3, 200, 50), (10e3, 200, 50)):
    gm_opt = np.sqrt(beta) / Rs
    ICopt = gm_opt * VT
    F = 1 + rb / Rs + 1 / np.sqrt(beta)
    # brute force
    ICs = np.logspace(-6, -1, 5000); gms = ICs / VT
    Fs = 1 + rb / Rs + 1 / (2 * gms * Rs) + gms * Rs / (2 * beta)
    print(f"Rs={Rs:6.0f}, beta={beta}, rb={rb}: IC_opt = VT sqrt(beta)/Rs = {ICopt*1e3:7.3f} mA (brute {ICs[np.argmin(Fs)]*1e3:7.3f}), F={10*np.log10(F):.2f} dB")
# base-spreading resistance thermal noise density
for rb in (5, 20, 50, 200):
    print(f"rb={rb:4d} ohm -> sqrt(4kTrb) = {np.sqrt(4*k*T*rb)*1e9:.2f} nV/rtHz")
print(f"collector shot noise at 1 mA: sqrt(2qIC) = {np.sqrt(2*q*1e-3)*1e12:.1f} pA/rtHz ; referred to input voltage /gm = {np.sqrt(2*q*1e-3)/(1e-3/VT)*1e9:.3f} nV/rtHz (= sqrt(2kT/gm)... check {np.sqrt(4*k*T/(2*1e-3/VT))*1e9:.3f})")
