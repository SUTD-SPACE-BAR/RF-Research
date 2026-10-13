#!/usr/bin/env python3
"""Verification script for kb/05-analog-electronics/diodes-schottky-pin-varactor.md

Checks (all numbers quoted on the page come from here):
 1. Thermal voltage, 60 mV/decade, forward-voltage temperature coefficient.
 2. Schottky zero-bias detector: video resistance, current/voltage responsivity
    (derived beta = 1/(2 n VT), open-circuit gamma0 = 1/(2 (Is+Ib))),
    confirmed by brute-force time-domain simulation of the diode equation;
    square-law -> linear transition from the exact Bessel solution;
    junction-capacitance roll-off at 433/915/2450/5800 MHz.
 3. PIN diode: RS = W^2/((mu_n+mu_p) IF tau), transit-time frequency,
    series/shunt switch insertion loss and isolation from exact 2-port S21.
 4. Varactor: C-V law, capacitance ratio -> VCO tuning range, Q = 1/(2 pi f RS C).
 5. TVS/ESD capacitance: return loss / insertion loss of a shunt C on 50 ohm.
Run:  python3 tools/verify/analog_diodes.py
"""
import numpy as np
from scipy.special import i0e
from scipy.optimize import brentq

k = 1.380649e-23
q = 1.602176634e-19

print("=== 1. Junction basics ===")
for T in (273.15, 290.0, 298.15, 300.0, 358.15):
    VT = k * T / q
    print(f"T={T:7.2f} K  VT={VT*1e3:6.3f} mV  decade slope (n=1)={VT*np.log(10)*1e3:5.1f} mV")
# dVF/dT for silicon at 1 mA:  VF = Eg/q - (VT) ln(Is0 T^xti / I) ... derivative
# Standard result: dVF/dT = (VF - Eg/q - XTI*VT)/T  with XTI = 3 for pn Si
T = 300.0; VT = k * T / q
for VF, Eg, XTI, name in ((0.65, 1.12, 3.0, "Si pn"), (0.30, 0.69, 2.0, "Schottky (EG=0.69, XTI=2)")):
    dVdT = (VF - Eg - XTI * VT) / T
    print(f"{name:28s}: VF={VF:.2f} V -> dVF/dT = {dVdT*1e3:+.2f} mV/K")

print("\n=== 2. Schottky zero-bias detector (HSMS-2850 SPICE params) ===")
Is, n, Rs, Cj0 = 3e-6, 1.06, 25.0, 0.18e-12
T = 298.15; VT = k * T / q; nVT = n * VT
Rj = nVT / Is
Rj_ds = 8.33e-5 * n * T / Is
print(f"Rj = nVT/Is = {Rj/1e3:.2f} kohm (exact k/q); datasheet formula 8.33e-5*n*T/Is = {Rj_ds/1e3:.2f} kohm; datasheet typ Rv = 8.0 kohm")
beta = 1 / (2 * nVT)
gamma0 = beta * Rj  # = 1/(2 Is)
print(f"current responsivity beta = 1/(2nVT) = {beta:.2f} A/W")
print(f"open-circuit voltage responsivity gamma0 = 1/(2Is) = {gamma0:.3g} V/W = {gamma0*1e-3:.0f} mV/uW (ideal, no Rs/Cj, conjugate-matched)")

# brute-force check: drive the ideal diode (no Rs, Cj) with small v(t) = Vp cos wt, DC short circuit current
Vp = 1e-3
t = np.linspace(0, 1, 20001)[:-1]
i = Is * (np.exp(Vp * np.cos(2 * np.pi * t) / nVT) - 1)
Idc = i.mean()
g = Is / nVT
Pabs = 0.5 * Vp**2 * g   # small-signal power absorbed
print(f"time-domain: Idc/Pabs = {Idc/Pabs:.3f} A/W  (theory {beta:.3f})")

# Exact large-signal open-circuit output (RL -> inf): Is(exp(-Vo/nVT) I0(a) - 1) = 0 -> Vo = nVT ln I0(a), a = Vp/nVT
def vo_exact(Vp):
    a = Vp / nVT
    return nVT * (np.log(i0e(a)) + a)
for Vp in (1e-3, 5e-3, 1e-2, 3e-2, 0.1, 0.3, 1.0):
    sq = Vp**2 / (4 * nVT)
    ex = vo_exact(Vp)
    print(f"Vp={Vp*1e3:7.1f} mV  Vo exact={ex*1e3:9.4f} mV  square-law={sq*1e3:9.4f} mV  ratio={20*np.log10(ex/sq):+6.2f} dB  Vo/Vp={ex/Vp:.3f}")
# where does exact output fall 1 dB (voltage) below square law?
f1 = lambda Vp: 20 * np.log10(vo_exact(Vp) / (Vp**2 / (4 * nVT))) + 1.0
Vp1 = brentq(f1, 1e-3, 1.0)
P1 = Vp1**2 / (2 * Rj)
print(f"1 dB departure from square law at Vp = {Vp1*1e3:.1f} mV; if matched into Rj: P = {10*np.log10(P1/1e-3):.1f} dBm")

# capacitance roll-off of voltage sensitivity: gamma = gamma0 / (1 + w^2 Cj^2 Rs Rj)
for f in (433e6, 915e6, 2.45e9, 5.8e9, 10e9):
    w = 2 * np.pi * f
    fac = 1 / (1 + (w * Cj0)**2 * Rs * Rj)
    print(f"f={f/1e9:6.3f} GHz  sensitivity factor 1/(1+w^2Cj^2RsRj) = {fac:.3f} ({10*np.log10(fac):+.1f} dB)")

# Unmatched: diode across 50-ohm source, high impedance -> Vp ~ Voc = sqrt(8 R P)
P = 1e-6
Vp_um = np.sqrt(8 * 50 * P)
print(f"unmatched on 50 ohm, 1 uW available: Vp~{Vp_um*1e3:.1f} mV -> Vo~{Vp_um**2/(4*nVT)*1e3:.2f} mV i.e. ~{Vp_um**2/(4*nVT)*1e3:.1f} mV/uW (vs ~{gamma0*1e-3:.0f} ideal matched)")

print("\n=== 3. PIN diode ===")
mun, mup = 0.135, 0.048  # m^2/Vs, low-field Si mobilities (upper bound; high-injection values are lower)
for W_um, IF, tau in ((50, 10e-3, 1.5e-6), (50, 1e-3, 1.5e-6), (100, 10e-3, 2e-6), (175, 100e-3, 4e-6)):
    W = W_um * 1e-6
    Q = IF * tau
    RS = W**2 / ((mun + mup) * Q)
    fmin = 1300 / W_um**2  # MHz (Skyworks rule)
    print(f"W={W_um:4d} um IF={IF*1e3:5.1f} mA tau={tau*1e6:.1f} us -> Q={Q*1e9:6.1f} nC RS={RS:6.2f} ohm; transit-time f > {fmin*1e3:8.1f} kHz")

def s21_series(Z, Z0=50.0):
    return 2 * Z0 / (2 * Z0 + Z)
def s21_shunt(Y, Z0=50.0):
    return 2 / (2 + Y * Z0)
Z0 = 50.0
for RS in (1.0, 2.1, 5.0):
    il_ser = -20 * np.log10(abs(s21_series(RS)))
    il_ser_f = 20 * np.log10(1 + RS / (2 * Z0))
    iso_sh = -20 * np.log10(abs(s21_shunt(1 / RS)))
    iso_sh_f = 20 * np.log10(1 + Z0 / (2 * RS))
    print(f"RS={RS:4.1f}: series IL={il_ser:.3f} dB (formula {il_ser_f:.3f}); shunt isolation={iso_sh:.2f} dB (formula {iso_sh_f:.2f})")
for CT in (0.13e-12, 0.3e-12, 1e-12):
    for f in (433e6, 915e6, 2.45e9):
        w = 2 * np.pi * f
        iso_ser = -20 * np.log10(abs(s21_series(1 / (1j * w * CT))))
        iso_ser_f = 10 * np.log10(1 + (1 / (4 * np.pi * f * CT * Z0))**2)
        il_sh = -20 * np.log10(abs(s21_shunt(1j * w * CT)))
        il_sh_f = 10 * np.log10(1 + (np.pi * f * CT * Z0)**2)
        print(f"CT={CT*1e12:4.2f} pF f={f/1e6:6.0f} MHz: series isolation={iso_ser:5.2f} dB (formula {iso_ser_f:5.2f}); shunt IL={il_sh:.4f} dB (formula {il_sh_f:.4f})")
# TFR = tau ln(1 + IF/IR)
tau = 1.55e-6
for r in (1, 2, 5, 10, 20):
    print(f"IF/IR={r:3d}: TFR = {tau*np.log(1+1/r)*1e9:7.1f} ns  (TFR/tau={np.log(1+1/r):.3f})")

print("\n=== 4. Varactor ===")
def Cv(V, C0, phi, gam):
    return C0 / (1 + V / phi)**gam
C0, phi, gam = 10e-12, 0.7, 0.47
for V in (0, 1, 3, 10, 25):
    print(f"abrupt (C0=10 pF, phi=0.7, gamma=0.47): V={V:3d} V C={Cv(V,C0,phi,gam)*1e12:6.2f} pF")
Cr = Cv(1, C0, phi, gam) / Cv(25, C0, phi, gam)
print(f"capacitance ratio C(1V)/C(25V) = {Cr:.2f}; frequency ratio if varactor is the only C = sqrt(Cr) = {np.sqrt(Cr):.2f}")
# Hyperabrupt approx gamma ~ 1: constant sensitivity-ish; with gamma=2, f proportional to (V+phi) -> linear tuning
for gam_h in (0.5, 1.0, 2.0):
    V = np.linspace(0.5, 4.5, 5)
    C = Cv(V, 20e-12, 0.7, gam_h)
    f = 1 / (2 * np.pi * np.sqrt(10e-9 * C))
    print(f"gamma={gam_h}: f(V) MHz =", np.round(f / 1e6, 1), " df/dV =", np.round(np.diff(f) / 1e6, 1))
# VCO at 433 MHz: L = 22 nH, fixed Cfix = 2 pF, varactor 1..6 pF through coupling
L = 22e-9
for Cvar in (1e-12, 2e-12, 4e-12, 6e-12):
    for Cfix in (1.5e-12,):
        Ct = Cfix + Cvar
        print(f"L=22 nH, Cfix=1.5 pF, Cvar={Cvar*1e12:.0f} pF -> f={1/(2*np.pi*np.sqrt(L*Ct))/1e6:6.1f} MHz")
# Q
for f in (50e6, 433e6, 915e6, 2.45e9):
    Qv = 1 / (2 * np.pi * f * 0.8 * 5e-12)
    print(f"RS=0.8 ohm, C=5 pF: Q at {f/1e6:6.0f} MHz = {Qv:6.1f}")

print("\n=== 5. Shunt capacitance of ESD/TVS parts on a 50-ohm RF line ===")
for C in (0.2e-12, 0.5e-12, 1e-12, 5e-12, 30e-12):
    out = []
    for f in (433e6, 915e6, 1575.42e6, 2.45e9, 5.8e9):
        Y = 1j * 2 * np.pi * f * C
        s11 = -Y * Z0 / (2 + Y * Z0)
        s21 = 2 / (2 + Y * Z0)
        out.append(f"{f/1e6:6.0f}MHz IL={-20*np.log10(abs(s21)):5.2f}dB RL={-20*np.log10(abs(s11)):5.1f}dB")
    print(f"C={C*1e12:5.1f} pF: " + " | ".join(out))

print("\n=== 6. Where the square-law ceiling sits in dBm depends on the RF voltage step-up ===")
# 1-dB departure at the junction occurs at Vp1 (computed above, ~40 mV for n=1.06).
for label, R in (("50-ohm terminated broadband detector (Vp = sqrt(2*50*P))", 50.0),
                 ("matched to Rj (voltage step-up sqrt(Rj/50))", Rj)):
    P = Vp1**2 / (2 * R)
    print(f"{label}: 1 dB square-law error at {10*np.log10(P/1e-3):+.1f} dBm")

print("\n=== 7. ngspice (KiCad-bundled) check of the page's detector netlist ===")
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from analog_ngspice import run_netlist
    net = """
* HSMS-2850 zero-bias detector at 433 MHz, 50-ohm terminated, -30 dBm available
Vs src 0 SIN(0 20m 433MEG)
Rsrc src in 50
Rterm in 0 50
D1 in out HSMS2850
Cv out 0 100p
RL out 0 100k
.model HSMS2850 D(IS=3e-6 N=1.06 RS=25 CJO=0.18p VJ=0.35 M=0.5 EG=0.69 XTI=2 BV=3.8 IBV=3e-4)
.options temp=25
.tran 0.05n 40u 30u 0.05n
.end
"""
    r = run_netlist(net, ["time", "v(out)"])
    Vp = 10e-3
    hand = Vp**2 / (4 * nVT) * 100e3 / (100e3 + Rj)
    print(f"ngspice mean Vout = {np.mean(r['v(out)'])*1e3:.3f} mV ; hand estimate Vp^2/(4nVT)*RL/(RL+Rv) = {hand*1e3:.3f} mV")
    # 915 MHz and a VCO-style varactor check could be added here
except Exception as e:  # ngspice not available
    print("ngspice not available:", e)

print("\n=== 8. Worked-example numbers ===")
# Varactor-tuned 433 MHz tank: L=22 nH, Cfix=4.1 pF, varactor (C0=10p, phi .7, gamma .47) via Cc=3.3 pF
L, Cfix, Cc = 22e-9, 4.1e-12, 3.3e-12
for V in (1, 2, 4, 6, 10):
    Cvv = Cv(V, 10e-12, 0.7, 0.47)
    Cs = Cvv * Cc / (Cvv + Cc)
    Ct = Cfix + Cs
    print(f"V={V:2d} V: Cvar={Cvv*1e12:5.2f} pF series-with-Cc={Cs*1e12:4.2f} pF total={Ct*1e12:4.2f} pF f={1/(2*np.pi*np.sqrt(L*Ct))/1e6:6.1f} MHz")
# temperature coefficient of square-law output ~ 1/T
print(f"square-law output tempco d ln Vo/dT = -1/T = {-100/298.15:.3f} %/K at 25 C")
# detector example: forward power monitor, -25 dBm into 50-ohm terminated detector
P = 10**(-25/10) * 1e-3
Vp = np.sqrt(2 * 50 * P)
Vo = Vp**2 / (4 * nVT) * 100e3 / (100e3 + Rj)
print(f"-25 dBm: Vp={Vp*1e3:.1f} mV, Vo~{Vo*1e3:.2f} mV (RL=100k); 33 dBm TX needs {33+25} dB coupling+padding")
# thermal noise of video resistance in 2 MHz video bandwidth
vn = np.sqrt(4 * k * 298.15 * Rj * 2e6)
print(f"thermal noise of Rv={Rj/1e3:.1f}k in 2 MHz: {vn*1e6:.1f} uV rms")
