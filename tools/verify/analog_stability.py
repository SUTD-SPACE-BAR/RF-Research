#!/usr/bin/env python3
"""Verification script for kb/05-analog-electronics/feedback-and-stability.md

 1. Two-pole loop: phase margin <-> damping ratio <-> step overshoot <-> closed-loop peaking.
 2. Nyquist/gain margin: triple-pole loop K/(1+s/p)^3 is unstable for K > 8 (closed-loop poles + encirclement count).
 3. Op-amp driving a capacitive load: phase margin vs CL from Ro*CL pole; isolation resistor Riso restores it.
 4. Two-stage Miller compensation: pole splitting (approx vs exact), RHP zero gm2/Cc, nulling resistor Rz = 1/gm2.
 5. Emitter-follower parasitic oscillation: small-signal critical base-stopper resistance vs ngspice transient,
    and the simple bound gm L/(Cpi + CL).
Run: python3 tools/verify/analog_stability.py
"""
import os, sys
import numpy as np
from numpy.polynomial import polynomial as P
from scipy.optimize import brentq
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def phase_margin(num, den, wmin=1e0, wmax=1e12):
    """num/den: polynomial coefficients (descending) of loop gain T(s). Returns (PM deg, wc)."""
    w = np.logspace(np.log10(wmin), np.log10(wmax), 200000)
    _, H = signal.freqs(num, den, w)
    mag = np.abs(H)
    i = np.where(mag < 1)[0][0]
    wc = w[i]
    ph = np.unwrap(np.angle(H))[i]
    return 180 + np.degrees(ph), wc

print("=== 1. Phase margin vs damping / overshoot / peaking (T = wu/(s(1+s/p2))) ===")
for PM_target in (30, 45, 60, 65, 76):
    # T(s) = K/(s(s/p2+1)); closed loop 2nd order: wn^2 = K p2, 2 zeta wn = p2
    def pm_of_zeta(z):
        return np.degrees(np.arctan(2 * z / np.sqrt(np.sqrt(1 + 4 * z**4) - 2 * z**2)))
    zeta = brentq(lambda z: pm_of_zeta(z) - PM_target, 0.01, 2)
    OS = np.exp(-np.pi * zeta / np.sqrt(1 - zeta**2)) * 100 if zeta < 1 else 0.0
    Mp = 1 / (2 * zeta * np.sqrt(1 - zeta**2)) if zeta < 1 / np.sqrt(2) else 1.0
    # numeric check with an actual loop
    p2 = 1.0; wn = p2 / (2 * zeta); K = wn**2 / p2
    pm_num, _ = phase_margin([K], [1 / p2, 1, 0], 1e-4, 1e4)
    print(f"PM={PM_target:3d} deg: zeta={zeta:.3f} (rule PM/100={PM_target/100:.2f}), overshoot={OS:5.1f} %, peaking={20*np.log10(Mp):4.2f} dB, numeric PM check={pm_num:5.1f}")

print("\n=== 2. Triple-pole loop: gain margin ===")
p = 1.0
for K in (4, 7.9, 8.1, 12):
    # closed loop char: (1+s)^3 + K = 0
    ch = np.polymul(np.polymul([1, 1], [1, 1]), [1, 1]); ch[-1] += K
    r = np.roots(ch)
    # Nyquist: count encirclements of -1 by T(jw) for w from -inf..inf
    w = np.linspace(-200, 200, 400001)
    Tj = K / (1 + 1j * w)**3
    ang = np.unwrap(np.angle(Tj + 1))
    N = -(ang[-1] - ang[0]) / (2 * np.pi)  # clockwise encirclements
    print(f"K={K:5.1f}: max Re(closed-loop pole) = {max(r.real):+.3f}; clockwise encirclements of -1 = {N:+.2f}; GM = {20*np.log10(8/K):+.2f} dB")
print("phase crossover of 1/(1+s)^3 at w = sqrt(3): |T| = 1/8 -> K_crit = 8 (18.1 dB)")

print("\n=== 3. Op-amp with capacitive load ===")
A0, GBW, Ro = 1e5, 10e6, 100.0
wa = 2 * np.pi * GBW / A0
for CL in (0, 100e-12, 1e-9, 10e-9, 100e-9):
    num = [A0]
    den = np.polymul([1 / wa, 1], [Ro * CL, 1])
    pm, wc = phase_margin(num, den, 1e2, 1e11)
    fp = 1 / (2 * np.pi * Ro * CL) / 1e6 if CL > 0 else np.inf
    print(f"unity-gain buffer, Ro=100, CL={CL*1e9:7.2f} nF: load pole {fp:9.3f} MHz, PM = {pm:5.1f} deg at {wc/2/np.pi/1e6:6.2f} MHz")
CL = 10e-9
for Riso in (0, 10, 22, 47, 100):
    # feedback from op-amp output pin (before Riso): the load network adds pole (Ro+Riso)CL and zero Riso*CL
    num = np.polymul([A0], [Riso * CL, 1])
    den = np.polymul([1 / wa, 1], [(Ro + Riso) * CL, 1])
    pm, wc = phase_margin(num, den, 1e2, 1e11)
    fz = 1 / (2 * np.pi * Riso * CL) / 1e6 if Riso > 0 else np.inf
    print(f"CL=10 nF, Riso={Riso:4d}: zero at {fz:8.3f} MHz, PM = {pm:5.1f} deg, crossover {wc/2/np.pi/1e6:5.2f} MHz")

print("\n=== 4. Two-stage Miller compensation ===")
gm1, gm2 = 1e-3, 10e-3
R1, R2 = 1e6, 100e3
C1, C2 = 0.2e-12, 5e-12
for Cc in (1e-12, 3e-12, 10e-12):
    # exact 2-node transfer: nodes v1 (after stage1) and vo
    # node1: gm1 vin + v1/R1 + s C1 v1 + s Cc (v1 - vo) = 0
    # node2: gm2 v1 + vo/R2 + s C2 vo + s Cc (vo - v1) = 0
    # denominator polynomial:
    a2 = R1 * R2 * (C1 * C2 + Cc * (C1 + C2))
    a1 = R1 * (C1 + Cc) + R2 * (C2 + Cc) + gm2 * R1 * R2 * Cc
    den = [a2, a1, 1]
    pe = np.sort(np.abs(np.roots(den)))
    p1_approx = 1 / (gm2 * R1 * R2 * Cc)
    p2_approx = gm2 * Cc / (C1 * C2 + Cc * (C1 + C2))
    z = gm2 / Cc
    GBW = gm1 / Cc
    print(f"Cc={Cc*1e12:4.0f} pF: p1 exact {pe[0]/2/np.pi:9.1f} Hz (approx {p1_approx/2/np.pi:9.1f}); p2 exact {pe[1]/2/np.pi/1e6:7.2f} MHz (approx {p2_approx/2/np.pi/1e6:7.2f}); RHP zero {z/2/np.pi/1e6:7.1f} MHz; GBW=gm1/Cc {GBW/2/np.pi/1e6:6.2f} MHz; p2/GBW = {pe[1]/GBW:.2f}")
print("nulling resistor Rz = 1/gm2 =", 1 / gm2, "ohm moves the zero to infinity; Rz > 1/gm2 puts it in the LHP (can cancel p2)")

print("\n=== 5. Emitter follower VHF oscillation ===")
VT = 0.025852; IC = 5e-3; gm = IC / VT; beta = 200; rpi = beta / gm
Cpi = gm * 40e-12 + 3.4e-12   # TF*gm + forward-biased CJE (SPICE FC linearisation of CJE=2p)
Cmu = 0.29e-12                # CJC=0.5p at VCB=3 V
L, CLd = 20e-9, 20e-12
def char_roots(Rs):
    Ypi = np.array([1 / rpi, Cpi])
    Ncore = P.polyadd(np.array([0, CLd]), P.polyadd(Ypi, [gm]))
    Dcore = P.polymul(Ypi, [0, CLd])
    Din = P.polyadd(Dcore, P.polymul([0, Cmu], Ncore))
    ch = P.polyadd(P.polymul([Rs, L], Din), Ncore)
    return np.roots(ch[::-1])
Rc = brentq(lambda R: max(char_roots(R).real), 0.01, 1000)
r = char_roots(Rc * 0.99); i = np.argmax(r.real)
print(f"small-signal critical base resistance = {Rc:.1f} ohm (oscillation near {abs(r[i].imag)/2/np.pi/1e6:.0f} MHz); simple bound gm L/(Cpi+CL) = {gm*L/(Cpi+CLd):.1f} ohm")
try:
    from analog_ngspice import run_netlist
    def ptp_late(Rstop):
        net = f"""
* emitter follower with base lead inductance and capacitive load
.model QF NPN(IS=1e-15 BF=200 VAF=50 TF=40p CJE=2p CJC=0.5p RB=0)
VCC vcc 0 DC 5
VB bsrc 0 DC 2 PULSE(2 2.05 10n 0.1n 0.1n 1u 2u)
Rst bsrc b1 {Rstop}
Lb b1 b 20n
Q1 vcc b e QF
IE e 0 DC 5m
CL e 0 20p
.tran 0.02n 400n 0 0.02n
.end
"""
        rr = run_netlist(net, ["time", "v(e)"])
        t = rr["time"]; v = rr["v(e)"]
        return np.ptp(v[t > 300e-9])
    for R in (0.1, 47, 82, 100, 150):
        print(f"  ngspice Rstop={R:6.1f} ohm: sustained p-p at 300-400 ns = {ptp_late(R)*1e3:9.3f} mV")
except Exception as e:
    print("ngspice skipped:", e)

print("\n=== 6. Feedback-resistor / input-capacitance pole (TIA and high-value feedback networks) ===")
# Inverting amp / TIA: beta(s) = (1 + s Rf Cf) / (1 + s Rf (Cin + Cf))  (Rg -> inf for TIA); op-amp single pole GBW
GBW = 10e6; A0 = 1e5; wa = 2 * np.pi * GBW / A0
Rf, Cin = 100e3, 20e-12
for Cf in (0.0, 0.3e-12, np.sqrt(Cin / (2 * np.pi * Rf * GBW)), 2e-12, 5e-12):
    num = np.polymul([A0], [Rf * Cf, 1])
    den = np.polymul([1 / wa, 1], [Rf * (Cin + Cf), 1])
    pm, wc = phase_margin(num, den, 1e1, 1e11)
    print(f"TIA Rf=100k, Cin=20 pF, Cf={Cf*1e12:5.2f} pF: PM = {pm:5.1f} deg (crossover {wc/2/np.pi/1e6:.2f} MHz); closed-loop BW ~ 1/(2 pi Rf Cf) = {1/(2*np.pi*Rf*Cf)/1e3 if Cf>0 else float('inf'):8.1f} kHz")
print(f"Graeme rule Cf = sqrt(Cin/(2 pi Rf GBW)) = {np.sqrt(Cin/(2*np.pi*Rf*GBW))*1e12:.2f} pF")
# Inverting amp with finite Rg: neutral compensation Cf = Cin Rg / Rf makes beta flat
Rg = 10e3; Rf2 = 100e3
print(f"inverting amp Rf=100k, Rg=10k, Cin=20 pF: pole at 1/(2 pi (Rf||Rg) Cin) = {1/(2*np.pi*(Rf2*Rg/(Rf2+Rg))*Cin)/1e6:.2f} MHz; neutral Cf = Cin Rg/Rf = {Cin*Rg/Rf2*1e12:.1f} pF")
