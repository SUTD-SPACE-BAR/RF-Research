#!/usr/bin/env python3
"""W5-S14 checks for 06/receiver-architectures (LNB, offset dish, L-band re-feed, receiver power
budget, LO radiation, why a transmitter cannot sense receivers) and 06/baluns-and-rf-transformers
(SA612 drive levels and matching, dot polarity, bridged footprints).

A. Universal Ku LNB frequency plan and LO error (PLL x390 of a 25 MHz crystal; DRO).
B. LNB + cable + SDR cascade; total IF noise power into the SDR (overload check).
C. Offset-dish geometry: offset angle, feed angles, equivalent f/D; Singapore mount tilt.
D. TV dish re-fed at L-band (1694 MHz): gain, beamwidth, G/T and a relative link budget.
E. Receiver power budgets: SX1262 continuous vs duty-cycled RX; RTL-SDR; preamble sizing.
F. LO radiation at the antenna port vs FCC 15.111 / ETSI-type -57 dBm.
G. A transmitter cannot sense receivers: RCS of a matched / shorted dipole and the echo level.
H. SA612: LO drive in dBm, 50 ohm -> 1.5 kohm L-match, transformer ratio, Si5351 divider.
I. Dot polarity: reversed winding on one IQ leg selects the image; push-pull cancellation.
J. Unpopulated (bridged) balun footprints: pad capacitance vs frequency.
Ends with ALL PASS.
"""
import numpy as np

ok_all = True
def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(("PASS " if cond else "FAIL ") + name)

db = lambda x: 10 * np.log10(x)
kT0 = -173.98
c = 299792458.0
k_B = 1.380649e-23

# ---------------------------------------------------------------- A
print("A: universal LNB plan")
for band, (lo, rf1, rf2) in {"low": (9.75e9, 10.7e9, 11.7e9), "high": (10.6e9, 11.7e9, 12.75e9)}.items():
    print(f"  {band}: LO {lo/1e9:.2f} GHz, RF {rf1/1e9:.2f}-{rf2/1e9:.2f} GHz -> IF {(rf1-lo)/1e6:.0f}-{(rf2-lo)/1e6:.0f} MHz")
check("A1 IF spans 950-2150 MHz", (10.7e9 - 9.75e9) == 950e6 and abs((12.75e9 - 10.6e9) - 2150e6) < 1)
qo = 10489.55e6
print(f"  QO-100 NB beacon region {qo/1e6:.2f} MHz -> IF {(qo-9.75e9)/1e6:.2f} MHz (inside RTL-SDR range)")
mult = 9.75e9 / 25e6
for ppm in [30, 2, 0.5]:
    print(f"  PLL LNB, 25 MHz crystal x{mult:.0f}: {ppm} ppm -> LO error +/-{9.75e9*ppm*1e-6/1e3:.1f} kHz")
check("A2 x390: 30 ppm -> 292.5 kHz (matches +/-300 kHz PLL-LNB specs)", abs(9.75e9 * 30e-6 - 292.5e3) < 1)
print(f"  DRO LNB +/-2.5 MHz over temperature = {2.5e6/9.75e9*1e6:.0f} ppm; a 2.7 kHz SSB signal drifts across ~{2*2.5e6/2.7e3:.0f} channel widths")

# ---------------------------------------------------------------- B
print("\nB: LNB (NF 0.8 dB, G 55 dB) + 20 m RG-6 (~20 dB/100 m at 1.5 GHz) + SDR (NF 6 dB)")
stages = [(55.0, 0.8), (-4.0, 4.0), (30.0, 6.0)]
F, G = 0.0, 1.0
for i, (g, nf) in enumerate(stages):
    f = 10 ** (nf / 10)
    F = f if i == 0 else F + (f - 1) / G
    G *= 10 ** (g / 10)
print(f"  cascade NF = {db(F):.3f} dB (LNB alone 0.800 dB)")
check("B1 cable and SDR add < 0.01 dB after 55 dB of LNB gain", db(F) - 0.8 < 0.01)
Ta, Te = 50.0, 290 * (10 ** 0.08 - 1)
Pn = 10 * np.log10(k_B * (Ta + Te) * 1.2e9 / 1e-3) + 55 - 4
print(f"  total IF noise (T_ant {Ta:.0f} K, T_e {Te:.0f} K, 1.2 GHz) at the SDR: {Pn:.1f} dBm — an 8-bit SDR "
      f"front end sees this whole block: add 10-20 dB of pad or low tuner gain")
check("B2 broadband IF noise into the SDR ~ -40 dBm", -45 < Pn < -35)

# ---------------------------------------------------------------- C
print("\nC: offset dish (parent paraboloid y = x^2/4f; aperture from x = h to h + D)")
fpar, h, D = 0.50, 0.05, 0.80
x1, x2 = h, h + D
y = lambda x: x ** 2 / (4 * fpar)
beta = np.degrees(np.arctan((y(x2) - y(x1)) / (x2 - x1)))
psi1, psi2 = 2 * np.arctan(x1 / (2 * fpar)), 2 * np.arctan(x2 / (2 * fpar))
psi0, Th = np.degrees((psi1 + psi2) / 2), np.degrees((psi2 - psi1) / 2)
fD_eq = 1 / (4 * np.tan(np.radians(Th) / 2))
print(f"  f = {fpar} m, h = {h} m, D = {D} m: rim-plane (offset) angle {beta:.1f} deg; feed tilted {psi0:.1f} deg "
      f"off the paraboloid axis; half-angle subtended {Th:.1f} deg -> equivalent f/D {fD_eq:.2f}")
check("C1 offset angle ~ 20-28 deg and f/D_eq ~ 0.5-0.8 for this TV-like geometry", 20 < beta < 28 and 0.5 < fD_eq < 0.8)
Re, rg = 6378.137, 42164.0
def geo_el(lat, dlon):
    cg = np.cos(np.radians(lat)) * np.cos(np.radians(dlon))
    g = np.arccos(cg)
    return np.degrees(np.arctan((cg - Re / rg) / np.sin(g))), np.sqrt(Re**2 + rg**2 - 2*Re*rg*cg)
for sat, lon in [("105.5E", 105.5), ("146E", 146.0), ("57E", 57.0), ("QO-100 25.9E", 25.9)]:
    el, slant = geo_el(1.35, lon - 103.8)
    print(f"  Singapore -> GEO {sat}: elevation {el:.1f} deg, slant {slant:.0f} km; dish face (rim-plane normal) at {el-beta:.1f} deg")
el105, _ = geo_el(1.35, 105.5 - 103.8)
elqo, _ = geo_el(1.35, 25.9 - 103.8)
check("C3 QO-100 (25.9E) is only ~3-4 deg above the horizon from Singapore", 2.5 < elqo < 4.5)
check("C2 near-overhead GEO from Singapore (~86 deg): offset dish face only ~62 deg up", 84 < el105 < 88)

# ---------------------------------------------------------------- D
print("\nD: TV dish re-fed at 1694.1 MHz")
f_L = 1694.1e6
lam = c / f_L
for Dd, eta in [(0.8, 0.5), (1.0, 0.5), (1.2, 0.5)]:
    Gd = eta * (np.pi * Dd / lam) ** 2
    print(f"  D = {Dd} m ({Dd/lam:.1f} lambda), eta {eta}: G = {db(Gd):.1f} dBi, HPBW ~ {70*lam/Dd:.1f} deg")
G08 = db(0.5 * (np.pi * 0.8 / lam) ** 2)
G10 = db(0.5 * (np.pi * 1.0 / lam) ** 2)
check("D1 0.8 m dish at 1.69 GHz ~ 20 dBi, 1.9 dB below a 1.0 m dish", abs(G08 - 20.0) < 0.6 and abs(G10 - G08 - 1.94) < 0.01)
Tsys = 60 + 290 * (10 ** 0.05 - 1)
GT08 = G08 - db(Tsys)
print(f"  T_sys = 60 K antenna + {290*(10**0.05-1):.0f} K LNA (NF 0.5 dB) = {Tsys:.0f} K -> G/T = {GT08:.1f} dB/K (0.8 m)")
# relative budget: back out the EIRP implied by NOAA's 1.0 m minimum (assumption: needs C/N0 = 61 dB-Hz)
_, slant = geo_el(30.0, 30.0)
fspl = 32.45 + 20 * np.log10(f_L / 1e6) + 20 * np.log10(slant)
CN0_req = 3.0 + 10 * np.log10(400e3) + 2.0
EIRP_impl = CN0_req - (G10 - db(Tsys)) + fspl - 228.6
CN0_08 = EIRP_impl + 30 - 30 - fspl + GT08 + 228.6
print(f"  slant {slant:.0f} km, FSPL {fspl:.1f} dB; if 1.0 m is just enough (C/N0 {CN0_req:.1f} dB-Hz: Eb/N0 3 dB coded + 2 dB), "
      f"implied EIRP = {EIRP_impl:.1f} dBW ({EIRP_impl+30:.1f} dBm); a 0.8 m dish then gets C/N0 {CN0_08:.1f} dB-Hz "
      f"(margin {CN0_08-CN0_req:.1f} dB)")
check("D2 0.8 m margin vs a 1.0 m minimum = -1.9 dB", abs((CN0_08 - CN0_req) + 1.94) < 0.02)

# ---------------------------------------------------------------- E
print("\nE: receiver power budgets")
V = 3.3
rows = [("SX1262 RX, DC-DC", 4.6e-3, V), ("SX1262 RX, LDO", 8.8e-3, V), ("RTL-SDR Blog V3", 0.275, 5.0)]
for n, i, v in rows:
    print(f"  {n:18s}: {i*1e3:6.1f} mA at {v} V = {i*v*1e3:7.1f} mW")
ratio = 0.275 * 5 / (4.6e-3 * 3.3)
print(f"  RTL-SDR / SX1262: {ratio:.0f} x (before the host computer)")
check("E1 SDR receiver ~90x the power of a LoRa chip in RX", 80 < ratio < 100)
Tsym = 2 ** 7 / 125e3
t_rx, t_sl, I_sl = 3e-3, 97e-3, 0.6e-6
Iavg = (4.6e-3 * t_rx + I_sl * t_sl) / (t_rx + t_sl)
pre = int(np.ceil((2 * t_rx + t_sl) / Tsym))
print(f"  duty-cycled RX (SF7/125, T_sym {Tsym*1e3:.3f} ms): {t_rx*1e3:.0f} ms on / {t_sl*1e3:.0f} ms sleep -> "
      f"{Iavg*1e6:.0f} uA average; transmitter preamble must span >= {pre} symbols ({pre*Tsym*1e3:.0f} ms)")
check("E2 duty-cycled average ~ 139 uA (33x lower)", abs(Iavg - 138.6e-6) < 1e-6)
cap = 2.0
print(f"  2000 mAh cell: continuous {cap/4.6e-3/24:.0f} days, duty-cycled {cap/Iavg/24:.0f} days (chip only)")

# ---------------------------------------------------------------- F
print("\nF: LO leakage at the antenna port")
lim = -57.0
cases = {"superhet: +7 dBm LO, DBM LO-RF 30 dB, LNA reverse 20 dB, SAW 2 dB": 7 - 30 - 20 - 2,
         "same with a 35 dB-reverse-isolation LNA and +4 dBm LO": 4 - 30 - 35 - 2,
         "zero-IF: -60 dBm at the LNA input, LNA reverse 20 dB": -60 - 20}
for n, p in cases.items():
    print(f"  {n}: {p} dBm -> {'OVER' if p > lim else 'ok'} ({p-lim:+.0f} dB vs -57 dBm)")
check("F1 first superhet case 12 dB over -57 dBm", (7 - 30 - 20 - 2) - lim == 12)

# ---------------------------------------------------------------- G
print("\nG: can a transmitter detect a receiver? (monostatic echo off the receiving antenna)")
f0 = 433.92e6
lam4 = c / f0
Gd = 1.641
sig_m = Gd ** 2 * lam4 ** 2 / (4 * np.pi)
sig_s = 0.86 * lam4 ** 2
for R in [100.0, 1000.0]:
    for name, sg in [("matched load", sig_m), ("shorted (max)", sig_s)]:
        Pr = 1.0 * Gd * Gd * lam4 ** 2 * sg / ((4 * np.pi) ** 3 * R ** 4)
        print(f"  1 W, dipoles, R = {R:.0f} m, {name:13s} sigma {sg:.3f} m^2: echo {db(Pr/1e-3):.1f} dBm")
Pr1k = 1.0 * Gd ** 2 * lam4 ** 2 * sig_m / ((4 * np.pi) ** 3 * 1e6 ** 2)
print(f"  the echo is co-channel with the 30 dBm transmitter: detecting it needs ~{30-db(Pr1k/1e-3):.0f} dB of "
      f"self-interference cancellation, and the on/off change is only {db(sig_s/sig_m):.1f} dB amid building clutter")
check("G1 matched dipole sigma = G^2 lambda^2/4pi = 0.10 m^2", abs(sig_m - 0.102) < 0.003)
check("G2 echo at 1 km ~ -132 dBm", abs(db(Pr1k / 1e-3) + 131.9) < 0.3)

# ---------------------------------------------------------------- H
print("\nH: SA612 drive")
for vpp in [0.2, 0.3]:
    vr = vpp / (2 * np.sqrt(2))
    print(f"  {vpp*1e3:.0f} mVpp sine = {vr*1e3:.1f} mV rms = {db(vr**2/50/1e-3):.1f} dBm across 50 ohm")
check("H1 200-300 mVpp = -10.0 to -6.5 dBm (50 ohm)", abs(db((0.2/2.828)**2/50e-3) + 10.0) < 0.05 and abs(db((0.3/2.828)**2/50e-3) + 6.5) < 0.05)
f7 = 7.1e6
w = 2 * np.pi * f7
Rs, Rp = 50.0, 1500.0
Q = np.sqrt(Rp / Rs - 1)
Ls, Cp = Q * Rs / w, Q / (w * Rp)
print(f"  50 ohm -> 1.5 kohm single-ended at 7.1 MHz: Q = {Q:.2f}, series L {Ls*1e6:.2f} uH, shunt C {Cp*1e12:.1f} pF "
      f"(minus 3 pF pin capacitance -> {Cp*1e12-3:.1f} pF); balanced 3 kohm by transformer: turns ratio {np.sqrt(3000/50):.2f}:1")
Zl = 1 / (1 / Rp + 1j * w * Cp)
Zin = 1j * w * Ls + Zl
check("H2 L-match gives 50 ohm", abs(Zin - 50) < 0.01)
r1, r2 = 1000.0, 68.0
print(f"  Si5351 3.3 Vpp CMOS into a {r1:.0f}/{r2:.0f} ohm divider: {3.3*r2/(r1+r2)*1e3:.0f} mVpp at the square-wave "
      f"fundamental x4/pi = {3.3*r2/(r1+r2)*4/np.pi*1e3:.0f} mVpp — inside 200-300 mVpp")
check("H3 divider lands the fundamental in 200-300 mVpp", 0.2 < 3.3 * r2 / (r1 + r2) * 4 / np.pi < 0.3)

# ---------------------------------------------------------------- I
print("\nI: dot polarity")
def irr(g, phi):
    return (1 + 2 * g * np.cos(phi) + g ** 2) / (1 - 2 * g * np.cos(phi) + g ** 2)
print(f"  Q leg correct: IRR(g=1, 1 deg) = {db(irr(1, np.radians(1))):.1f} dB; one balun reversed (g = -1): "
      f"IRR = {db(irr(-1, np.radians(1))):.1f} dB -> the receiver now selects the image (sideband swapped)")
check("I1 reversed leg swaps wanted and image (IRR -> -IRR in dB)", abs(db(irr(-1, np.radians(1))) + db(irr(1, np.radians(1)))) < 1e-9)
t = np.linspace(0, 1, 4096, endpoint=False)
ia = np.maximum(np.cos(2 * np.pi * t), 0)
ib = np.maximum(-np.cos(2 * np.pi * t), 0)
def h1(x): return abs(2 * np.mean(x * np.exp(-2j * np.pi * t)))
def h2(x): return abs(2 * np.mean(x * np.exp(-4j * np.pi * t)))
good, bad = ia - ib, ia + ib
print(f"  class-B push-pull halves: correct dots -> fundamental {h1(good):.3f}, 2nd {h2(good):.1e}; "
      f"one winding reversed -> fundamental {h1(bad):.1e}, 2nd {h2(bad):.3f}")
check("I2 reversed winding cancels the fundamental and keeps the 2nd harmonic", h1(bad) < 1e-9 and h2(bad) > 0.4)

# ---------------------------------------------------------------- J
print("\nJ: an empty 0402 pad pair (~0.15 pF) left across/at a 50 ohm line")
for f in [433.92e6, 915e6, 2.45e9, 5.8e9]:
    Y = 1j * 2 * np.pi * f * 0.15e-12
    Zs = 1 / (1 / 50 + Y)
    G_ = (Zs - 50) / (Zs + 50)
    print(f"  {f/1e9:5.3f} GHz: |X| = {1/abs(Y):6.0f} ohm, return loss {-20*np.log10(abs(G_)):.1f} dB")
Y433 = 1j * 2 * np.pi * 433.92e6 * 0.15e-12
check("J1 negligible at 433 MHz (RL > 39 dB), matters at 5.8 GHz (RL < 25 dB)",
      -20*np.log10(abs((1/(1/50+Y433)-50)/(1/(1/50+Y433)+50))) > 39 and
      -20*np.log10(abs((1/(1/50+1j*2*np.pi*5.8e9*0.15e-12)-50)/(1/(1/50+1j*2*np.pi*5.8e9*0.15e-12)+50))) < 25)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
