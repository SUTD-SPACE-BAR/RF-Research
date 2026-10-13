#!/usr/bin/env python3
"""Verification script for kb/05-analog-electronics/op-amps-real-limitations.md

 1. GBW and noise gain: closed-loop bandwidth of non-inverting / inverting configurations (numeric vs GBW/NG).
 2. Slew rate: full-power bandwidth SR/(2 pi Vpk); single-pole SR/GBW relation for a BJT diff-pair input.
 3. Noise: en with 1/f corner integrated over a band (closed form vs numeric), pp/rms (6.6x), inferring the
    1/f corner of the MCP6002 from its 0.1-10 Hz spec; single-pole noise bandwidth factor pi/2.
 4. Output-noise budget of a non-inverting gain stage (en, in, resistors).
 5. Offset/error budget with Vos, Ib, drift, CMRR, PSRR (MCP6002 vs OPA333).
 6. CMRR/PSRR vs frequency and supply-ripple feedthrough.
 7. Current-feedback amplifier: bandwidth vs gain compared with a VFB op-amp.
 8. Fully differential amplifier: single-ended input impedance (sympy nodal analysis) and output CM.
Run: python3 tools/verify/analog_opamp.py
"""
import numpy as np
import sympy as sp
from scipy import signal, integrate

k = 1.380649e-23; q = 1.602176634e-19; T = 300.0; VT = k * T / q

print("=== 1. GBW and noise gain ===")
GBW, A0 = 1e6, 1e5
wa = 2 * np.pi * GBW / A0
def closed_loop_bw(beta, sign=+1, Ginv=None):
    # A(s) = A0/(1+s/wa); non-inverting closed loop = A/(1+A beta)
    w = np.logspace(1, 9, 200000)
    A = A0 / (1 + 1j * w / wa)
    H = A / (1 + A * beta)
    if Ginv is not None:  # inverting: H = -(Rf/(Rf+Rg)) A / (1 + A beta)
        H = H * (1 - beta)
    H0 = abs(H[0])
    idx = np.where(abs(H) < H0 / np.sqrt(2))[0][0]
    return w[idx] / 2 / np.pi, H0
for G in (1, 2, 10, 100):
    beta = 1 / G
    f3, H0 = closed_loop_bw(beta)
    print(f"non-inverting G={G:4d} (noise gain {G}): f3dB = {f3/1e3:8.1f} kHz (GBW/NG = {GBW/G/1e3:8.1f} kHz), |H0|={H0:.3f}")
for Gi in (1, 10):
    beta = 1 / (1 + Gi)   # Rg/(Rf+Rg)
    f3, H0 = closed_loop_bw(beta, Ginv=True)
    print(f"inverting G=-{Gi:2d} (noise gain {1+Gi}): f3dB = {f3/1e3:8.1f} kHz (GBW/(1+|G|) = {GBW/(1+Gi)/1e3:8.1f} kHz), |H0|={H0:.3f}")

print("\n=== 2. Slew rate ===")
for name, SR, Vpk in (("MCP6002", 0.6e6, 1.65), ("OPA333", 0.16e6, 1.65), ("OPA1612", 27e6, 10.0), ("THS3091 (CFA)", 6000e6, 10.0)):
    print(f"{name:14s} SR={SR/1e6:7.2f} V/us: full-power BW at {Vpk:5.2f} V peak = SR/(2 pi Vpk) = {SR/(2*np.pi*Vpk)/1e3:10.1f} kHz")
# single-pole BJT-input op-amp: SR = Itail/Cc, GBW = gm1/(2 pi Cc), gm1 = (Itail/2)/VT -> SR = 2 pi GBW * 2 VT
print(f"BJT diff-pair input, single-pole: SR = 4 pi VT GBW = {4*np.pi*VT*1e6/1e6:.3f} V/us per MHz of GBW (degenerate the input pair to raise it)")

print("\n=== 3. 1/f noise integration ===")
def vn_rms(en, fc, f1, f2):
    return en * np.sqrt(fc * np.log(f2 / f1) + (f2 - f1))
en, fc = 10e-9, 100.0
closed = vn_rms(en, fc, 0.1, 10)
num = np.sqrt(integrate.quad(lambda f: en**2 * (1 + fc / f), 0.1, 10)[0])
print(f"en=10 nV/rtHz, fc=100 Hz, 0.1-10 Hz: closed form {closed*1e9:.1f} nV rms, numeric {num*1e9:.1f} nV rms, x6.6 -> {6.6*closed*1e6:.3f} uVpp")
for f2 in (1e3, 20e3, 1e6):
    print(f"   0.1 Hz - {f2:9.0f} Hz: {vn_rms(en, fc, 0.1, f2)*1e6:7.3f} uV rms (white-only {en*np.sqrt(f2)*1e6:7.3f})")
# MCP6002: 28 nV/rtHz @1 kHz, 6.1 uVpp 0.1-10 Hz -> fc estimate
en_m = 28e-9; rms = 6.1e-6 / 6.6
fc_m = ((rms / en_m)**2 - 9.9) / np.log(100)
print(f"MCP6002: 6.1 uVpp -> {rms*1e6:.2f} uV rms; with en=28 nV/rtHz white, implied 1/f corner ~ {fc_m:.0f} Hz")
# noise bandwidth of single-pole = pi/2 f3dB
f3 = 1e3
nbw = integrate.quad(lambda f: 1 / (1 + (f / f3)**2), 0, np.inf)[0]
print(f"single-pole ENBW = {nbw:.1f} Hz for f3dB = 1 kHz (pi/2 = {np.pi/2:.4f})")

print("\n=== 4. Non-inverting stage noise budget (G = 101: Rf = 100k, Rg = 1k, Rs = 1k) ===")
Rf, Rg, Rs = 100e3, 1e3, 1e3
NG = 1 + Rf / Rg
Rpar = Rf * Rg / (Rf + Rg)
for name, en_, in_ in (("OPA1612 (bipolar, 1.1 nV, 1.7 pA)", 1.1e-9, 1.7e-12), ("MCP6002 (CMOS, 28 nV, 0.6 fA)", 28e-9, 0.6e-15), ("THS3091 (CFA, 1.1 nV, 15 pA)", 1.1e-9, 15e-12)):
    terms = {
        "en": en_,
        "in*Rs": in_ * Rs,
        "in*(Rf||Rg)": in_ * Rpar,
        "Rs thermal": np.sqrt(4 * k * T * Rs),
        "Rf||Rg thermal": np.sqrt(4 * k * T * Rpar),
    }
    tot = np.sqrt(sum(v**2 for v in terms.values()))
    s = ", ".join(f"{kk}={vv*1e9:.2f}" for kk, vv in terms.items())
    print(f"{name}: RTI nV/rtHz: {s}; total {tot*1e9:.2f} RTI -> {tot*NG*1e9:.0f} nV/rtHz RTO")

print("\n=== 5. DC error budget (G = +11, Rs = 10k source, dT = 50 K, VCM change 1 V, supply change 0.2 V) ===")
parts = {
    "MCP6002": dict(Vos=4.5e-3, drift=2e-6, Ib=1e-12, cmrr_db=60, psrr_db=86),
    "OPA333": dict(Vos=10e-6, drift=0.05e-6, Ib=200e-12, cmrr_db=106, psrr_db=20 * np.log10(1 / 5e-6)),
}
for name, p in parts.items():
    e = {
        "Vos": p["Vos"],
        "drift*dT": p["drift"] * 50,
        "Ib*Rs": p["Ib"] * 10e3,
        "CMRR (1 V)": 1.0 / 10**(p["cmrr_db"] / 20),
        "PSRR (0.2 V)": 0.2 / 10**(p["psrr_db"] / 20),
    }
    tot = sum(e.values())
    print(f"{name:8s}: " + ", ".join(f"{kk}={vv*1e6:8.2f} uV" for kk, vv in e.items()) + f" | worst-case sum RTI {tot*1e6:8.1f} uV -> RTO {tot*11*1e3:.3f} mV")

print("\n=== 6. CMRR/PSRR vs frequency and ripple feedthrough ===")
psrr_dc, f_corner = 86.0, 100.0
for f in (100, 1e3, 10e3, 100e3, 1e6):
    psrr = psrr_dc - 10 * np.log10(1 + (f / f_corner)**2)
    ripple = 20e-3
    print(f"PSRR {psrr_dc:.0f} dB DC with 100 Hz corner -> at {f/1e3:7.1f} kHz: {psrr:5.1f} dB; 20 mV ripple -> {ripple/10**(psrr/20)*1e6:9.1f} uV RTI")

print("\n=== 7. CFA vs VFA bandwidth ===")
Rt, Ct, Rin, RF = 1e6, 1e-12, 30.0, 1.2e3
GBW_vfa = 250e6
for G in (1, 2, 5, 10):
    RG = RF / (G - 1) if G > 1 else np.inf
    w = np.logspace(5, 10.5, 200000)
    Z = Rt / (1 + 1j * w * Rt * Ct)
    H = G / (1 + (RF + Rin * G) / Z)
    idx = np.where(abs(H) < abs(H[0]) / np.sqrt(2))[0][0]
    f_cfa = w[idx] / 2 / np.pi
    print(f"G={G:3d}: CFA (RF=1.2k fixed, Ct=1 pF, Rin=30) f3dB = {f_cfa/1e6:6.1f} MHz (approx 1/(2 pi Ct (RF+Rin G)) = {1/(2*np.pi*Ct*(RF+Rin*G))/1e6:6.1f}); VFA 250 MHz GBW: {GBW_vfa/G/1e6:6.1f} MHz")

print("\n=== 8. Fully differential amplifier: single-ended input impedance ===")
Vin, RG_, RF_, vp, vn, vop, von, Vocm = sp.symbols('V_in R_G R_F v_p v_n v_op v_on V_ocm')
# ideal FDA: vp = vn (inputs), (vop + von)/2 = Vocm; single-ended source Vin into RG on + side path; other RG to ground.
# currents: input P side: (Vin - vp)/RG = (vp - von)/RF ; input N side: (0 - vn)/RG = (vn - vop)/RF
eqs = [sp.Eq((Vin - vp) / RG_, (vp - von) / RF_), sp.Eq((0 - vn) / RG_, (vn - vop) / RF_), sp.Eq(vp, vn), sp.Eq((vop + von) / 2, Vocm)]
sol = sp.solve(eqs, [vp, vn, vop, von], dict=True)[0]
Iin = (Vin - sol[vp]) / RG_
Zin = sp.simplify(Vin / Iin.subs(Vocm, 0))
print("Zin (Vocm=0) =", sp.simplify(Zin))
print("formula RG/(1 - RF/(2(RG+RF))) matches:", sp.simplify(Zin - RG_ / (1 - RF_ / (2 * (RG_ + RF_)))) == 0)
print("differential gain (vop - von)/Vin =", sp.simplify((sol[vop] - sol[von]) / Vin))
for RGv, RFv in ((1e3, 1e3), (1e3, 2e3)):
    print(f"  RG={RGv:.0f}, RF={RFv:.0f}: Zin = {RGv/(1-RFv/(2*(RGv+RFv))):.0f} ohm, gain {RFv/RGv:.1f}")

print("\n=== 9. Page netlist + FDA noise example ===")
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from analog_ngspice import run_netlist
    net = """
* single-pole op-amp macro (GBW 1 MHz, A0 = 1e5, Ro 100 ohm) in a gain-of-10 non-inverting stage
.subckt OA1 inp inn out
Gin 0 n1 inp inn 1m
Rp n1 0 100Meg
Cp n1 0 159p
Eb n2 0 n1 0 1
Ro n2 out 100
.ends
Vin in 0 AC 1
X1 in fb out OA1
Rf out fb 9k
Rg fb 0 1k
.ac dec 50 10 10MEG
.end
"""
    r = run_netlist(net, ["frequency", "v(out)"])
    f = np.real(r["frequency"]); H = np.abs(r["v(out)"])
    f3 = np.exp(np.interp(-3.0103, (20*np.log10(H/H[0]))[::-1], np.log(f)[::-1]))
    print(f"ngspice gain-10 stage: DC gain {H[0]:.3f}, f3dB = {f3/1e3:.1f} kHz (GBW/NG = 100 kHz)")
except Exception as e:
    print("ngspice skipped:", e)
en = 3.3e-9; R = 1e3
e_res = np.sqrt(4 * k * T * R)
tot = np.sqrt((2 * en)**2 + 4 * e_res**2)
enbw = np.pi / 2 * 100e3
print(f"FDA RF=RG=1k: output noise density {tot*1e9:.1f} nV/rtHz; over RC 100 kHz (ENBW {enbw/1e3:.0f} kHz): {tot*np.sqrt(enbw)*1e6:.2f} uV rms; 16-bit LSB for 10 V p-p diff span = {10/2**16*1e6:.0f} uV")
