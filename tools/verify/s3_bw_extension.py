#!/usr/bin/env python3
"""W5-S3 verification for kb/05-analog-electronics/amplifier-topologies.md — sections
"Bandwidth extension and broadband amplifiers" (G-05-02) and "Output stages" (G-05-03 part). ngspice via s3_spice.py.

 1. Shunt peaking: gm into (R + sL) || C, m = L/(R^2 C): bandwidth extension, peaking (Python + ngspice).
 2. Series peaking (C1 - L - C2||R, C1 + C2 fixed): best flat (<= 0.1 dB) extension (Python search + ngspice).
 3. Bridged T-coil: constant-resistance design 2L(1+k) = R^2 C, C_B = C(1-k)/(4(1+k)); ngspice Zin and bandwidth.
 4. Distributed amplifier, 4 ideal-gm sections on 50-ohm artificial lines: gain n gm Z0/2 and bandwidth vs a lumped
    stage of the same 4 devices (ngspice).
 5. Balanced amplifier with two branch-line (90 deg) hybrids at 433 MHz, each amp mismatched (Rin 25 ohm): S11 and S21 (ngspice).
 6. Noise figure of the resistive-feedback gain block of this page at 433 MHz (ngspice .noise) vs R_s/R_F estimate.
 7. Push-pull output stages: class B vs class AB (diode-biased) THD in ngspice; class-B efficiency pi/4 (Vp/Vcc).
Run: python3 tools/verify/s3_bw_extension.py
"""
import numpy as np
from s3_spice import run, op, first_cross

def f3db(f, H):
    m = np.abs(H) / abs(H[0])
    i = np.where(m < 1 / np.sqrt(2))[0][0]
    return np.interp(1 / np.sqrt(2), [m[i], m[i - 1]], [f[i], f[i - 1]])

print("=== 1. Shunt peaking ===")
R, C = 1e3, 1e-12
f = np.logspace(6, 10, 40001); s = 2j * np.pi * f
f0 = 1 / (2 * np.pi * R * C)
res1 = {}
for m in (0.0, 0.32, 0.414, 0.5, 0.71):
    L = m * R * R * C
    Z = (R + s * L) / (1 + s * C * (R + s * L))
    bw = f3db(f, Z); pk = 20 * np.log10(np.abs(Z).max() / R)
    # group-delay flatness: max deviation of tau below f3db, relative to tau(0)
    ph = np.unwrap(np.angle(Z)); tau = -np.gradient(ph, 2 * np.pi * f)
    sel = f < bw
    dev = (tau[sel].max() - tau[sel].min()) / tau[0]
    res1[m] = (bw / f0, pk)
    print(f"  m = {m:5.3f}: BW = {bw/f0:.3f} x 1/(2piRC), peaking {pk:+.2f} dB, group-delay spread in band {dev*100:5.1f} %")
x, d = run(f"""I1 0 o AC 1m
R1 o a {R:g}
L1 a 0 {0.414*R*R*C:g}
C1 o 0 {C:g}
""", "ac dec 400 1Meg 10G", ["mag(v(o))"])
bw_sp = first_cross(x, d["mag(v(o))"], d["mag(v(o))"][0] / np.sqrt(2))
print(f"  ngspice m = 0.414: BW {bw_sp/f0:.3f} x (Python {res1[0.414][0]:.3f})")
assert abs(bw_sp / f0 - res1[0.414][0]) < 0.01 and abs(res1[0.414][1]) < 0.05

print("\n=== 2. Series peaking (C1 at the device, L, C2 || R at the load; C1 + C2 = 1 pF) ===")
best = (0,)
for a in np.linspace(0.1, 0.9, 81):
    C1, C2 = a * C, (1 - a) * C
    for m in np.linspace(0.05, 1.5, 146):
        L = m * R * R * C
        # node1: current source, C1, L to node2; node2: C2 || R. Vout at node2
        Y1 = s * C1; Y2 = s * C2 + 1 / R; ZL = s * L
        Vo = 1 / (Y1 + Y2 + Y1 * Y2 * ZL)     # transimpedance to node2
        mag = np.abs(Vo) / R
        if mag.max() > 10 ** (0.1 / 20):
            continue
        bw = f3db(f, Vo) / f0
        if bw > best[0]:
            best = (bw, a, m)
print(f"  best maximally-flat-ish (<= 0.1 dB peaking): BW = {best[0]:.2f} x with C1/C = {best[1]:.2f}, m = {best[2]:.2f}")
a, m = best[1], best[2]
x, d = run(f"""I1 0 n1 AC 1m
C1 n1 0 {a*C:g}
L1 n1 n2 {m*R*R*C:g}
C2 n2 0 {(1-a)*C:g}
R1 n2 0 {R:g}
""", "ac dec 400 1Meg 10G", ["mag(v(n2))"])
bws = first_cross(x, d["mag(v(n2))"], d["mag(v(n2))"][0] / np.sqrt(2))
print(f"  ngspice: BW {bws/f0:.2f} x")
assert abs(bws / f0 - best[0]) < 0.03 and best[0] > 2.0

print("\n=== 3. Bridged T-coil (R = 1k, C = 1 pF) ===")
for kc in (0.2, 1 / 3, 0.5):
    Lt = R * R * C / (2 * (1 + kc))
    CB = C * (1 - kc) / (4 * (1 + kc))
    net = f"""I1 0 a AC 1m
L1 a t {Lt:g}
L2 t b {Lt:g}
K1 L1 L2 {kc:.6f}
CB a b {CB:g}
C1 t 0 {C:g}
R1 b 0 {R:g}
"""
    x, d = run(net, "ac dec 400 1Meg 10G", ["mag(v(a))", "mag(v(t))"])
    zin = d["mag(v(a))"] / 1e-3
    vt = d["mag(v(t))"]
    bwt = first_cross(x, vt, vt[0] / np.sqrt(2))
    print(f"  k = {kc:.3f}: L1 = L2 = {Lt*1e9:.0f} nH, C_B = {CB*1e15:.0f} fF; |Z_in| = {zin.min():.1f}-{zin.max():.1f} ohm (constant R);"
          f" BW at the load capacitor = {bwt/f0:.2f} x 1/(2pi RC), peaking {20*np.log10(vt.max()/vt[0]):+.2f} dB")
    assert zin.max() - zin.min() < 1.0
    if abs(kc - 1 / 3) < 1e-9:
        assert abs(bwt / f0 - 2 * np.sqrt(2)) < 0.05

print("\n=== 4. Distributed amplifier: 4 sections, gm 20 mS, Cgs = Cds = 0.5 pF, 50-ohm lines ===")
n, gm, Cg, Z0 = 4, 20e-3, 0.5e-12, 50.0
Ls = Z0 ** 2 * Cg
fc = 1 / (np.pi * np.sqrt(Ls * Cg))
lines = ["Vs src 0 AC 1", "Rs src g0 50", "Rgt gN 0 50", "Rdr d0 0 50", "Rout dN 0 50"]
# gate line g0 -L/2- g1 -L- g2 ... gn -L/2- gN ; drain line d0 -L/2- e1 -L- ... en -L/2- dN
gnodes = ["g0"] + [f"g{i}" for i in range(1, n + 1)] + ["gN"]
dnodes = ["d0"] + [f"e{i}" for i in range(1, n + 1)] + ["dN"]
for i in range(n + 1):
    Lv = Ls / 2 if i in (0, n) else Ls
    lines.append(f"LG{i} {gnodes[i]} {gnodes[i+1]} {Lv:g}")
    lines.append(f"LD{i} {dnodes[i]} {dnodes[i+1]} {Lv:g}")
for i in range(1, n + 1):
    lines.append(f"CG{i} g{i} 0 {Cg:g}")
    lines.append(f"CD{i} e{i} 0 {Cg:g}")
    lines.append(f"GM{i} e{i} 0 g{i} 0 {gm:g}")
x, d = run("\n".join(lines), "ac dec 200 10Meg 30G", ["mag(v(dN))"])
s21 = 2 * d["mag(v(dN))"]
bwd = first_cross(x, s21, s21[0] / np.sqrt(2))
print(f"  line cut-off 1/(pi sqrt(LC)) = {fc/1e9:.1f} GHz; |S21| at LF = {s21[0]:.3f} (n gm Z0/2 = {n*gm*Z0/2:.2f}); -3 dB at {bwd/1e9:.1f} GHz")
# lumped: same 4 devices in parallel between 50-ohm source and 50-ohm load
x2, d2 = run(f"""Vs src 0 AC 1
Rs src g 50
Rt g 0 50
CG g 0 {n*Cg:g}
GM o 0 g 0 {n*gm:g}
CD o 0 {n*Cg:g}
RL o 0 50
""", "ac dec 200 10Meg 30G", ["mag(v(o))"])
s21l = 2 * d2["mag(v(o))"]
bwl = first_cross(x2, s21l, s21l[0] / np.sqrt(2))
print(f"  lumped (the same 4 devices in parallel, 50-ohm shunt-terminated input, 50-ohm load): |S21| = {s21l[0]:.2f}, -3 dB at {bwl/1e9:.2f} GHz"
      f" -> DA: x {bwd/bwl:.1f} bandwidth at x {s21[0]/s21l[0]:.2f} gain (gain-bandwidth x {bwd*s21[0]/(bwl*s21l[0]):.1f}), and matched to the line cut-off")
assert abs(s21[0] - n * gm * Z0 / 2) < 0.05 and bwd > 3 * bwl

print("\n=== 5. Balanced amplifier, branch-line hybrids at 433 MHz, amps with Rin = 25 ohm (|Gamma| = 1/3), gain 10 dB ===")
f0b = 433e6; TD = 1 / (4 * f0b)
def hybrid(p, a, b, c, d):
    # branch-line: 35.36 ohm series arms a-b and d-c, 50 ohm shunt arms a-d and b-c (ports a in, b thru, c coupled, d isolated)
    return (f"T{p}1 {a} 0 {b} 0 Z0=35.3553 TD={TD:g}\nT{p}2 {d} 0 {c} 0 Z0=35.3553 TD={TD:g}\n"
            f"T{p}3 {a} 0 {d} 0 Z0=50 TD={TD:g}\nT{p}4 {b} 0 {c} 0 Z0=50 TD={TD:g}\n")
amp = lambda nm, i, o: f"R{nm}i {i} 0 25\nE{nm} {nm}x 0 {i} 0 {2*np.sqrt(10)*1.5:g}\nR{nm}o {nm}x {o} 50\n"
# single amp: source 50 ohm -> amp -> 50 ohm load
x, d = run("Vs src 0 AC 1\nRs src i 50\n" + amp("A", "i", "o") + "RL o 0 50\n", "ac lin 201 300Meg 566Meg", ["real(v(i))", "imag(v(i))", "mag(v(o))"])
vi = d["real(v(i))"] + 1j * d["imag(v(i))"]
g1 = 20 * np.log10(abs(2 * d["mag(v(o))"][100]))
s11_single = 20 * np.log10(abs(2 * vi[100] - 1))
# balanced: hybrid 1 (in a1, thru b1 -> amp A, coupled c1 -> amp B, iso d1 -> 50), hybrid 2 combines
net = ("Vs src 0 AC 1\nRs src a1 50\n" + hybrid(1, "a1", "b1", "c1", "d1") + "Rd1 d1 0 50\n" +
       amp("A", "b1", "b2") + amp("B", "c1", "c2") +
       hybrid(2, "c2", "o2", "x2", "b2") + "Rx2 x2 0 50\nRL o2 0 50\n")
x, dr = run(net, "ac lin 201 300Meg 566Meg", ["real(v(a1))", "imag(v(a1))", "mag(v(o2))"])
vac = dr["real(v(a1))"] + 1j * dr["imag(v(a1))"]
s11b = 20 * np.log10(np.abs(2 * vac - 1))
s21b = 20 * np.log10(2 * dr["mag(v(o2))"])
i0 = np.argmin(abs(x - f0b))
band = (x > 0.9 * f0b) & (x < 1.1 * f0b)
print(f"  single amp: |S11| = {s11_single:.1f} dB, |S21| = {g1:.2f} dB")
print(f"  balanced:   |S11| = {s11b[i0]:.1f} dB at 433 MHz, worst {s11b[band].max():.1f} dB over +/-10 %; |S21| = {s21b[i0]:.2f} dB at 433 MHz")
assert s11b[i0] < -40 and abs(s21b[i0] - g1) < 0.1

print("\n=== 6. Noise figure of the resistive-feedback gain block (R_F 500, R_E 3.7) at 433 MHz ===")
gb = """.model QS NPN(IS=5e-16 BF=250 VAF=30 TF=2.5p CJE=0.3p CJC=0.08p RB=5 RE=0 RC=2)
VCC vcc 0 DC 8
Rbias vcc ch 150
Lch ch c 10u
Q1 c b e QS
RE e 0 3.7
RF c bf 500
CF bf b 100n
RB1 c bb 10k
LB bb b 10u
RB2 b 0 2.65k
Vin src 0 DC 0 AC 1
Rsrc src in 50
Cin in b 100n
Cout c out 100n
Rload out 0 50
.options temp=16.85
"""
x, d = run(gb, "noise v(out) Vin dec 10 100Meg 1G\nsetplot noise1", ["inoise_spectrum"])
# input-referred noise includes the 50-ohm source; F = inoise^2 / (4kT0*50)
k = 1.380649e-23
F = d["inoise_spectrum"] ** 2 / (4 * k * 290 * 50)
NF = 10 * np.log10(np.interp(433e6, x, F))
print(f"  ngspice NF at 433 MHz = {NF:.2f} dB (estimate 1 + R_s/R_F alone = {10*np.log10(1+50/500):.2f} dB, plus R_E, r_b and shot noise)")
assert 1.0 < NF < 5.0

print("\n=== 7. Push-pull emitter-follower output stage, +/-5 V, 100 ohm load, 2 V peak 1 kHz ===")
q = ".model QN NPN(IS=1e-14 BF=150 VAF=75)\n.model QP PNP(IS=1e-14 BF=150 VAF=75)\n.model DD D(IS=1e-14 N=1)\n"
classB = q + """VCC vcc 0 5
VEE vee 0 -5
Vin in 0 SIN(0 2 1k)
Q1 vcc in out QN
Q2 vee in out QP
RL out 0 100
"""
classAB = q + """VCC vcc 0 5
VEE vee 0 -5
Vin in 0 SIN(0 2 1k)
I1 vcc bn DC 2m
D1 bn in DD
D2 in bp DD
I2 bp vee DC 2m
Q1 vcc bn e1 QN
Q2 vee bp e2 QP
R1 e1 out 1
R2 e2 out 1
RL out 0 100
"""
def thd(net):
    x, d = run(net, "tran 1u 6m 2m 1u", ["v(out)"])
    t = np.linspace(2e-3, 6e-3, 4000, endpoint=False)
    v = np.interp(t, x, d["v(out)"])
    V = np.abs(np.fft.rfft(v)) / len(v) * 2
    fund = V[4]
    harm = np.sqrt(np.sum(V[8:4 * 20:4] ** 2))
    return harm / fund * 100, fund
tb, ab_ = thd(classB), thd(classAB)
print(f"  class B (no bias): THD {tb[0]:.1f} %, fundamental {tb[1]:.2f} V peak (dead band +/- V_BE ~ 0.6 V)")
print(f"  class AB (2 diodes, 2 mA bias, 1 ohm emitter resistors): THD {ab_[0]:.2f} %, fundamental {ab_[1]:.2f} V peak")
for Vp in (2.0, 5.0):
    print(f"  ideal class-B efficiency at Vp = {Vp} V on +/-5 V: pi/4 * Vp/Vcc = {np.pi/4*Vp/5*100:.0f} %; class A (resistor-biased follower) <= 25 %")
assert tb[0] > 5 and ab_[0] < 1.0
print("\n=== 8. Why an LNA is a poor TX driver: class-A linear output capability P ~ (1/2) V_swing I_bias ===")
for lab, vsw, ib in (("GNSS/ISM LNA, 3 V, 5 mA (V_swing ~2.5 V)", 2.5, 5e-3), ("driver/gain block, 5 V, 60 mA (V_swing ~4 V)", 4.0, 60e-3)):
    P = 0.5 * vsw * ib
    print(f"  {lab}: P_max ~ {P*1e3:.1f} mW = {10*np.log10(P/1e-3):.1f} dBm (ideal class-A ceiling; P1dB is lower)")
print("  BGA524N6 (canonical page): gain 19.6 dB, IP1dB -16 dBm -> OP1dB ~ +2.6 dBm")
print("\nALL S3 BANDWIDTH-EXTENSION / OUTPUT-STAGE CHECKS PASS")
