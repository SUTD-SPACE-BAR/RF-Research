#!/usr/bin/env python3
"""Verification script for kb/05-analog-electronics/fets-mosfet-jfet-gaas-gan.md

 1. Long-channel MOSFET: square law, gm = 2 ID/Vov = sqrt(2 k' W/L ID), fT = 3 mu Vov /(4 pi L^2);
    velocity-saturated limit fT ~ vsat/(2 pi L).
 2. gm/ID vs inversion coefficient (EKV interpolation) and its weak/strong-inversion limits.
 3. JFET square law vs BF862 datasheet (IDSS, VGSoff, yfs) and channel thermal noise vs en = 0.8 nV/rtHz.
 4. PA device comparison: class-A power density (Vbr - Vk) Imax / 8, optimum load Ropt = (Vdd-Vk)^2/(2P),
    Johnson-limit Vbr*fT ~ Ec vsat / (2 pi).
 5. Linearity per DC watt: OIP3/PDC for BFP740 vs ATF-54143 at 900 MHz.
 6. Pyro-channel MOSFET at 3.3 V gate drive (AO3400A).
Run: python3 tools/verify/analog_fet.py
"""
import numpy as np

k = 1.380649e-23; q = 1.602176634e-19; T = 300.0; VT = k * T / q

print("=== 1. MOSFET square law and fT ===")
mu = 0.04     # m^2/Vs effective electron mobility (400 cm^2/Vs, typical inversion-layer value)
tox = 4e-9    # m
Cox = 3.45e-11 / tox  # F/m^2 (eps_ox = 3.9*8.854e-12)
for L in (1e-6, 180e-9):
    for Vov in (0.1, 0.2, 0.4):
        W = 10e-6
        kp = mu * Cox
        ID = 0.5 * kp * W / L * Vov**2
        gm = 2 * ID / Vov
        gm2 = np.sqrt(2 * kp * W / L * ID)
        Cgs = 2 / 3 * W * L * Cox
        fT = gm / (2 * np.pi * Cgs)
        fT_formula = 3 * mu * Vov / (4 * np.pi * L**2)
        print(f"L={L*1e9:5.0f} nm Vov={Vov:.1f} V: ID={ID*1e3:7.3f} mA gm={gm*1e3:6.2f} mS (={gm2*1e3:6.2f}) gm/ID={gm/ID:5.1f}/V fT={fT/1e9:7.2f} GHz (formula {fT_formula/1e9:7.2f})")
vsat = 1e5
for L in (180e-9, 65e-9, 28e-9):
    print(f"velocity-saturated estimate fT ~ vsat/(2 pi L) at L={L*1e9:.0f} nm: {vsat/(2*np.pi*L)/1e9:.0f} GHz (upper-bound style estimate; extrinsic caps lower it)")

print("\n=== 2. gm/ID vs inversion coefficient (EKV) ===")
n = 1.3
for IC in (0.01, 0.1, 1, 10, 100):
    gmid = 2 / (1 + np.sqrt(1 + 4 * IC)) / (n * VT)
    strong = 1 / (n * VT * np.sqrt(IC))
    print(f"IC={IC:7.2f}: gm/ID = {gmid:5.1f} /V  (weak limit 1/(n VT) = {1/(n*VT):.1f}; strong-inv. 1/(n VT sqrt(IC)) = {strong:6.1f})")
print(f"BJT for comparison: gm/IC = 1/VT = {1/VT:.1f} /V")
print(f"subthreshold slope n*VT*ln10 = {n*VT*np.log(10)*1e3:.0f} mV/decade (n={n})")

print("\n=== 3. JFET (BF862) ===")
IDSS, VP = 15e-3, 0.8  # typical-ish mid values; datasheet IDSS 10-25 mA, VGSoff 0.3-1.2 (typ 0.8)
gm0 = 2 * IDSS / VP
print(f"gm0 = 2 IDSS/|VP| = {gm0*1e3:.1f} mS (datasheet yfs 35-45 mS)")
for ID in (2e-3, 5e-3, 10e-3):
    gm = gm0 * np.sqrt(ID / IDSS)
    VGS = -VP * (1 - np.sqrt(ID / IDSS))
    en = np.sqrt(4 * k * T * (2 / 3) / gm)
    print(f"ID={ID*1e3:4.0f} mA: VGS={VGS:+.3f} V gm={gm*1e3:5.1f} mS  channel-noise en = sqrt(4kT(2/3)/gm) = {en*1e9:.2f} nV/rtHz")
print("datasheet en = 0.8 nV/rtHz at 100 kHz (includes gate/source resistance and excess noise)")
print(f"gate leakage current noise at IG=10 pA: sqrt(2 q IG) = {np.sqrt(2*q*10e-12)*1e15:.2f} fA/rtHz")

print("\n=== 4. PA device comparison ===")
devs = [  # name, Vbr (V), Imax (A/mm), Vknee (V), Vdd typical
    ("GaAs pHEMT", 15.0, 0.5, 1.0, 5.0),
    ("Si LDMOS", 70.0, 0.25, 4.0, 28.0),
    ("GaN HEMT", 80.0, 1.0, 5.0, 28.0),
]
for name, Vbr, Imax, Vk, Vdd in devs:
    Pd = (Vbr - Vk) * Imax / 8
    print(f"{name:11s}: ideal class-A power density (Vbr-Vk)Imax/8 = {Pd:5.2f} W/mm")
for name, Vdd, Vk in (("3.6 V handset (GaAs HBT / CMOS)", 3.6, 0.3), ("5 V module", 5.0, 0.5), ("28 V LDMOS/GaN", 28.0, 3.0), ("48 V GaN", 48.0, 4.0)):
    for P in (2.0, 10.0, 100.0):
        Ropt = (Vdd - Vk)**2 / (2 * P)
        print(f"  {name:32s} P={P:6.1f} W: Ropt = (Vdd-Vk)^2/(2P) = {Ropt:7.2f} ohm  (50-ohm transform ratio {50/Ropt:6.1f}:1)")
# Johnson limit
mats = [("Si", 0.3e8, 1.0e5), ("GaAs", 0.4e8, 1.0e5), ("GaN", 3.3e8, 2.5e5)]
for name, Ec, vs in mats:
    JL = Ec * vs / (2 * np.pi)
    print(f"{name:5s}: Johnson limit Vbr*fT ~ Ec*vsat/(2 pi) = {JL/1e9:8.0f} V*GHz  -> at fT=20 GHz, Vbr <~ {JL/20e9:5.0f} V")

print("\n=== 5. Linearity per DC watt at 900 MHz ===")
for name, oip3, V, I in (("BFP740 (SiGe HBT)", 22.5, 3.0, 15e-3), ("ATF-54143 (E-pHEMT)", 35.5, 3.0, 60e-3)):
    Pdc = V * I
    ratio = 10**(oip3 / 10) * 1e-3 / Pdc
    print(f"{name:22s}: OIP3={oip3} dBm, PDC={Pdc*1e3:.0f} mW, OIP3/PDC = {ratio:5.1f} ({10*np.log10(ratio):.1f} dB)")

print("\n=== 6. Pyro MOSFET at 3.3 V gate drive ===")
# AO3400A max RDS(on): 26.5 mOhm @10 V, 32 @4.5 V, 48 @2.5 V; interpolate at 3.3 V linearly in 1/(VGS-Vth)
Vth = 1.4  # max
pts = {10: 26.5e-3, 4.5: 32e-3, 2.5: 48e-3}
# model RDS = R0 + K/(VGS - Vth): fit on 4.5 and 2.5
A = np.array([[1, 1 / (4.5 - Vth)], [1, 1 / (2.5 - Vth)]])
R0, K = np.linalg.solve(A, [32e-3, 48e-3])
for VGS in (3.0, 3.3, 10):
    R = R0 + K / (VGS - Vth)
    print(f"VGS={VGS:4.1f} V: RDS(on) max ~ {R*1e3:5.1f} mOhm (model R0={R0*1e3:.1f} m + K/(VGS-Vth))")
R33 = R0 + K / (3.3 - Vth)
for I in (1.0, 3.0, 5.0):
    print(f"  igniter current {I:.0f} A: drop {I*R33*1e3:5.0f} mV, dissipation {I*I*R33:5.2f} W (for the few-ms firing pulse)")

print("\n=== 7. ngspice JFET transfer curve (page netlist) ===")
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from analog_ngspice import run_netlist
    net = """
* JFET square-law check (BF862-like: IDSS ~ 15 mA, VP ~ -0.8 V)
.model JBF NJF(VTO=-0.8 BETA=23.4m LAMBDA=0.02 CGS=8p CGD=2p IS=1e-14)
VD d 0 DC 5
VG g 0 DC 0
J1 d g 0 JBF
.dc VG -0.8 0 0.01
.end
"""
    r = run_netlist(net, ["v(g)", "i(vd)"])
    vg = np.real(r["v(g)"]); idd = -np.real(r["i(vd)"])
    theory = 23.4e-3 * 0.64 * (1 - vg / -0.8)**2 * (1 + 0.02 * 5)
    print(f"ID at VGS=0: sim {idd[-1]*1e3:.2f} mA, theory {theory[-1]*1e3:.2f} mA; max |sim-theory| = {np.max(abs(idd-theory))*1e6:.1f} uA")
    gm_sim = np.gradient(idd, vg)[-1]
    print(f"gm at VGS=0: sim {gm_sim*1e3:.1f} mS, theory 2*IDSS/|VP|*(1+lambda VDS) = {2*23.4e-3*0.64/0.8*1.1*1e3:.1f} mS")
except Exception as e:
    print("ngspice skipped:", e)
