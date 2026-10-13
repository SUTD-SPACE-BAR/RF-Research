#!/usr/bin/env python3
"""Verification for kb/06-rf-circuits/couplers-dividers-combiners.md

 A. Equal-split Wilkinson: S-matrix at f0, even/odd derivation checks, bandwidth
 B. Unequal-split Wilkinson (Pozar formulas), 2:1 power split
 C. Lumped-element Wilkinson at 433.92 MHz (pi-equivalent of the lambda/4 lines)
 D. Branch-line (90 deg) hybrid at 1575.42 MHz: amplitude/phase balance over the GNSS L1 band
 E. Rat-race (180 deg) hybrid: sum/difference behaviour
 F. Coupled-line directional coupler (10 dB, 20 dB): TEM ideal vs microstrip (unequal velocities) directivity
 G. Resistive 3-resistor splitter
 H. Combining efficiency with phase/amplitude errors; failed-PA case; power in the isolation resistor
 I. Short (weak) coupled section for power sampling: coupling ~ 6 dB/octave
Run: python3 tools/verify/rfckt_couplers.py
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rfckt_netsolve import Circuit, width_for, coupled_synth, hj_z0

ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


db = lambda x: 20 * np.log10(np.abs(x))
Z0 = 50.0

# ---------------------------------------------------------------- A. Wilkinson
f0 = 2.45e9
f = np.linspace(1.2e9, 3.7e9, 2501)


def wilkinson(f, f0, Z2=np.sqrt(2) * 50, Z3=np.sqrt(2) * 50, R=100.0, Zout2=50, Zout3=50):
    c = Circuit(f)
    c.line('p1', 'p2', Z2, f0, 90)
    c.line('p1', 'p3', Z3, f0, 90)
    c.R('p2', 'p3', R)
    return c


S = wilkinson(f, f0).sparams(['p1', 'p2', 'p3'])
i0 = np.argmin(abs(f - f0))
Sf0 = S[i0]
print("A: equal Wilkinson at f0: |S| (dB) =\n", np.round(db(Sf0 + 1e-15), 1))
check("A1 S21 = S31 = -j/sqrt(2) at f0", np.allclose([Sf0[1, 0], Sf0[2, 0]], -1j / np.sqrt(2), atol=1e-9))
check("A2 all ports matched and outputs isolated at f0", np.max(abs(np.array([Sf0[0, 0], Sf0[1, 1], Sf0[2, 2], Sf0[1, 2]]))) < 1e-9)
# lossless? no: isolation resistor absorbs odd-mode power -> S not unitary
check("A3 matched 3-port cannot be lossless: S^H S != I (resistor absorbs odd mode)", not np.allclose(Sf0.conj().T @ Sf0, np.eye(3)))
ok20 = (db(S[:, 0, 0]) < -20) & (db(S[:, 1, 2]) < -20) & (db(S[:, 1, 1]) < -20)
bw = f[ok20]
print(f"   20 dB return-loss/isolation bandwidth: {bw.min()/1e9:.3f}-{bw.max()/1e9:.3f} GHz = {100*np.ptp(bw)/f0:.1f} %")
check("A4 single-section Wilkinson has ~ 35-40 % bandwidth for 20 dB RL/isolation", 0.3 < np.ptp(bw) / f0 < 0.45)
# microstrip dimensions on 0.8 mm FR-4
h, er = 0.8e-3, 4.4
w707 = width_for(np.sqrt(2) * 50, h, er)
_, ee707 = hj_z0(w707, h, er)
lq = 299792458 / (4 * f0 * np.sqrt(ee707))
print(f"   0.8 mm FR-4: 70.7-ohm line W = {w707*1e3:.2f} mm, eeff {ee707:.2f}, lambda/4 = {lq*1e3:.1f} mm; R = 100 ohm (0402)")

# ---------------------------------------------------------------- B. unequal Wilkinson
K2 = 0.5            # P3/P2 = 1/2  (port 2 gets 2/3, port 3 gets 1/3)
K = np.sqrt(K2)
Z03 = Z0 * np.sqrt((1 + K2) / K ** 3)
Z02 = K2 * Z03
R = Z0 * (K + 1 / K)
R2, R3 = Z0 * K, Z0 / K       # output port impedances before transforming back to 50 ohm
c = Circuit(f)
c.line('p1', 'a', Z02, f0, 90); c.line('p1', 'b', Z03, f0, 90); c.R('a', 'b', R)
# output quarter-wave transformers from R2, R3 to 50 ohm
c.line('a', 'p2', np.sqrt(R2 * Z0), f0, 90); c.line('b', 'p3', np.sqrt(R3 * Z0), f0, 90)
Su = c.sparams(['p1', 'p2', 'p3'])[i0]
p2, p3 = abs(Su[1, 0]) ** 2, abs(Su[2, 0]) ** 2
print(f"B: unequal Wilkinson P3/P2 = {K2}: Z02 = {Z02:.1f}, Z03 = {Z03:.1f}, R = {R:.1f} ohm; outputs at "
      f"{R2:.1f}/{R3:.1f} ohm matched by {np.sqrt(R2*Z0):.1f}/{np.sqrt(R3*Z0):.1f}-ohm lambda/4 lines -> "
      f"P2 = {p2:.4f}, P3 = {p3:.4f}, |S23| = {db(Su[1,2]):.1f} dB, |S11| = {db(Su[0,0]):.1f} dB")
check("B1 unequal Wilkinson gives the designed split, match and isolation", abs(p3 / p2 - K2) < 1e-6 and abs(Su[1, 2]) < 1e-6 and abs(Su[0, 0]) < 1e-6)

# ---------------------------------------------------------------- C. lumped Wilkinson at 433.92 MHz
fl0 = 433.92e6; wl = 2 * np.pi * fl0
Zq = np.sqrt(2) * 50
Lw = Zq / wl; Cw = 1 / (Zq * wl)
fl = np.unique(np.append(np.linspace(300e6, 580e6, 1401), fl0))
c = Circuit(fl)
for out in ('p2', 'p3'):
    c.L('p1', out, Lw); c.C(out, 0, Cw)
c.C('p1', 0, 2 * Cw)
c.R('p2', 'p3', 100.0)
Sl = c.sparams(['p1', 'p2', 'p3'])
j0 = np.argmin(abs(fl - fl0))
print(f"C: lumped Wilkinson 433.92 MHz: L = {Lw*1e9:.2f} nH, C = {Cw*1e12:.2f} pF (2C = {2*Cw*1e12:.2f} pF at the input), R = 100 ohm")
okl = (db(Sl[:, 0, 0]) < -20) & (db(Sl[:, 1, 2]) < -20)
print(f"   at f0: S21 {db(Sl[j0,1,0]):.2f} dB, S11 {db(Sl[j0,0,0]):.1f} dB, S23 {db(Sl[j0,1,2]):.1f} dB; "
      f"20 dB bandwidth {fl[okl].min()/1e6:.0f}-{fl[okl].max()/1e6:.0f} MHz ({100*np.ptp(fl[okl])/fl0:.0f} %)")
check("C1 lumped Wilkinson is exact at f0", abs(Sl[j0, 0, 0]) < 1e-9 and abs(Sl[j0, 1, 2]) < 1e-9 and abs(abs(Sl[j0, 1, 0]) - 1 / np.sqrt(2)) < 1e-9)

# ---------------------------------------------------------------- D. branch-line at 1575.42 MHz
fb0 = 1575.42e6
fb = np.unique(np.append(np.linspace(1.3e9, 1.85e9, 1101), fb0))
c = Circuit(fb)
Zs = Z0 / np.sqrt(2)
c.line('p1', 'p2', Zs, fb0, 90); c.line('p4', 'p3', Zs, fb0, 90)
c.line('p1', 'p4', Z0, fb0, 90); c.line('p2', 'p3', Z0, fb0, 90)
Sb = c.sparams(['p1', 'p2', 'p3', 'p4'])
k0 = np.argmin(abs(fb - fb0))
print("D: branch-line at f0: S21 = %.3f%+.3fj, S31 = %.3f%+.3fj, |S41| = %.1e, |S11| = %.1e" %
      (Sb[k0, 1, 0].real, Sb[k0, 1, 0].imag, Sb[k0, 2, 0].real, Sb[k0, 2, 0].imag, abs(Sb[k0, 3, 0]), abs(Sb[k0, 0, 0])))
check("D1 branch-line: S21 = -j/sqrt2, S31 = -1/sqrt2, port 4 isolated", np.allclose([Sb[k0, 1, 0], Sb[k0, 2, 0]], [-1j / np.sqrt(2), -1 / np.sqrt(2)], atol=1e-9) and abs(Sb[k0, 3, 0]) < 1e-9)
band = (fb >= 1559e6) & (fb <= 1610e6)
amp_imb = db(Sb[band, 1, 0]) - db(Sb[band, 2, 0])
ph_diff = np.degrees(np.angle(Sb[band, 1, 0] / Sb[band, 2, 0]))
print(f"   over 1559-1610 MHz: amplitude imbalance {amp_imb.min():+.2f}..{amp_imb.max():+.2f} dB, phase difference "
      f"{ph_diff.min():.2f}..{ph_diff.max():.2f} deg, worst RL {(-db(Sb[band,0,0])).min():.1f} dB, worst isolation {(-db(Sb[band,3,0])).min():.1f} dB")
# axial ratio of a CP antenna fed by this hybrid (ideal orthogonal feeds): AR from amplitude ratio and phase error
def axial_ratio_db(a, dphi_deg):
    d = np.deg2rad(dphi_deg)
    # two orthogonal linear components with amplitudes 1, a and phase difference 90+d
    tau = 0.5 * np.arctan2(2 * a * np.cos(np.pi / 2 + d), 1 - a ** 2)
    num = 1 + a ** 2 + np.sqrt(1 + a ** 4 + 2 * a ** 2 * np.cos(2 * (np.pi / 2 + d)))
    den = 1 + a ** 2 - np.sqrt(1 + a ** 4 + 2 * a ** 2 * np.cos(2 * (np.pi / 2 + d)))
    return 10 * np.log10(num / den)
ar = axial_ratio_db(10 ** (amp_imb / 20), ph_diff - 90)
print(f"   -> axial ratio of an ideal dual-fed patch over L1 band: {ar.min():.2f}..{ar.max():.2f} dB")
check("D2 branch-line keeps AR < 1 dB across GPS/Galileo/GLONASS L1 (1559-1610 MHz)", ar.max() < 1.0)

# ---------------------------------------------------------------- E. rat-race
c = Circuit(fb)
Zr = np.sqrt(2) * Z0
# ring order: 1 -(90)- 2 -(90)- 3 -(90)- 4 -(270)- 1   (ports: 1 = sum? use Pozar numbering)
c.line('p1', 'p2', Zr, fb0, 90); c.line('p2', 'p3', Zr, fb0, 90); c.line('p3', 'p4', Zr, fb0, 90); c.line('p4', 'p1', Zr, fb0, 270)
Sr = c.sparams(['p1', 'p2', 'p3', 'p4'])[k0]
print("E: rat-race |S| (dB) at f0:\n", np.round(db(Sr + 1e-15), 1))
print(f"   port 2 excitation -> ports 1,3 phase difference {np.degrees(np.angle(Sr[0,1]/Sr[2,1])):.1f} deg; "
      f"port 4 excitation -> ports 1,3 phase difference {np.degrees(np.angle(Sr[0,3]/Sr[2,3])):.1f} deg")
check("E1 rat-race: one port splits in phase, the other in anti-phase, with isolation between them",
      abs(np.angle(Sr[0, 1] / Sr[2, 1])) < 1e-6 and abs(abs(np.angle(Sr[0, 3] / Sr[2, 3])) - np.pi) < 1e-6 and abs(Sr[3, 1]) < 1e-9)

# ---------------------------------------------------------------- F. coupled-line couplers
for Cdb in (10.0, 20.0):
    Cv = 10 ** (-Cdb / 20)
    Ze = Z0 * np.sqrt((1 + Cv) / (1 - Cv)); Zo = Z0 * np.sqrt((1 - Cv) / (1 + Cv))
    fc = np.linspace(0.8e9, 4.1e9, 1651)
    ic = np.argmin(abs(fc - f0))
    def coupler(ee_e=None, ee_o=None):
        c = Circuit(fc)
        c.coupled('p1', 'p2', 'p3', 'p4', Ze, Zo, f0, 90, ee_e, ee_o)   # 1 in, 2 through, 3 coupled, 4 isolated
        return c.sparams(['p1', 'p2', 'p3', 'p4'])
    St = coupler()
    w_, s_, ze_, zo_, eee, eeo = coupled_synth(Ze, Zo, h, er, guess=(1.3e-3, 0.3e-3 if Cdb == 10 else 1.0e-3))
    Sm = coupler(eee, eeo)
    Dt = db(St[ic, 2, 0]) - db(St[ic, 3, 0]); Dm = db(Sm[ic, 2, 0]) - db(Sm[ic, 3, 0])
    print(f"F: {Cdb:.0f} dB coupler: Z0e = {Ze:.2f}, Z0o = {Zo:.2f} ohm; ideal TEM: C = {-db(St[ic,2,0]):.2f} dB, "
          f"|S41| = {db(St[ic,3,0]+1e-18):.0f} dB; microstrip (W {w_*1e3:.2f} mm, S {s_*1e3:.2f} mm, ee {eee:.2f}/{eeo:.2f}): "
          f"C = {-db(Sm[ic,2,0]):.2f} dB, directivity {Dm:.1f} dB")
    if Cdb == 10:
        check("F1 ideal TEM coupler: exact coupling, infinite directivity", abs(-db(St[ic, 2, 0]) - Cdb) < 1e-6 and abs(St[ic, 3, 0]) < 1e-9)
        check("F2 microstrip coupler directivity is finite (< 25 dB) because of unequal modal velocities", Dm < 25)
    # coupling bandwidth (within 1 dB of nominal)
    within = abs(-db(St[:, 2, 0]) - Cdb) < 1.0
    print(f"   coupling within +-1 dB over {fc[within].min()/1e9:.2f}-{fc[within].max()/1e9:.2f} GHz (TEM, single section)")

# ---------------------------------------------------------------- G. resistive splitter
c = Circuit(np.array([1e9]))
c.R('p1', 'x', Z0 / 3); c.R('x', 'p2', Z0 / 3); c.R('x', 'p3', Z0 / 3)
Sr3 = c.sparams(['p1', 'p2', 'p3'])[0]
print(f"G: 3-resistor splitter (16.7 ohm each): S11 {db(Sr3[0,0]+1e-15):.0f} dB, S21 {db(Sr3[1,0]):.2f} dB, S23 {db(Sr3[1,2]):.2f} dB")
check("G1 star splitter: matched, -6.02 dB each way, only 6 dB 'isolation'", abs(Sr3[0, 0]) < 1e-12 and abs(db(Sr3[1, 0]) + 6.0206) < 1e-3 and abs(db(Sr3[1, 2]) + 6.0206) < 1e-3)

# ---------------------------------------------------------------- H. combining efficiency
S0 = wilkinson(np.array([f0]), f0).sparams(['p1', 'p2', 'p3'])[0]
for dphi in (0, 10, 30, 60, 90, 180):
    a2, a3 = 1.0, np.exp(1j * np.deg2rad(dphi))           # equal-amplitude sources into ports 2,3
    b1 = S0[0, 1] * a2 + S0[0, 2] * a3
    eta = abs(b1) ** 2 / (abs(a2) ** 2 + abs(a3) ** 2)
    print(f"H: two-way Wilkinson combiner, phase error {dphi:3d} deg: efficiency {eta*100:5.1f} % "
          f"(cos^2(dphi/2) = {np.cos(np.deg2rad(dphi)/2)**2*100:5.1f} %), rest in the 100-ohm resistor")
check("H1 combining efficiency = cos^2(dphi/2)", abs(abs(S0[0, 1] + S0[0, 2] * np.exp(1j * 0.5)) ** 2 / 2 - np.cos(0.25) ** 2) < 1e-9)
for N in (2, 4, 8):
    eta_fail = ((N - 1) / N) ** 2 * N / (N - 1)            # output power relative to (N-1) working PAs' input
    print(f"   N = {N}: one PA dead -> output {(N-1)**2/N**2*100:.1f} % of full ({10*np.log10((N-1)**2/N**2):.2f} dB); "
          f"combiner efficiency for the remaining PAs {(N-1)/N*100:.0f} %")
# amplitude imbalance: efficiency = (a+b)^2 / (2(a^2+b^2))
for r_db in (1, 3, 6):
    a = 10 ** (-r_db / 20)
    print(f"   amplitude imbalance {r_db} dB: efficiency {(1+a)**2/(2*(1+a**2))*100:.1f} %")

# ---------------------------------------------------------------- I. weak sampling coupler
Ze, Zo = 52.0, 48.0      # very loose coupling
L_deg_at = 10.0          # 10 degrees long at 433.92 MHz
fs = np.array([433.92e6, 867.84e6, 915e6, 1.8e9])
c = Circuit(fs)
c.coupled('p1', 'p2', 'p3', 'p4', Ze, Zo, 433.92e6, L_deg_at)
Ss = c.sparams(['p1', 'p2', 'p3', 'p4'])
for fi, s31 in zip(fs, Ss[:, 2, 0]):
    print(f"I: short weak coupler (Z0e/Z0o 52/48, 10 deg at 434 MHz): coupling at {fi/1e6:7.1f} MHz = {-db(s31):.1f} dB")
slope = db(Ss[1, 2, 0]) - db(Ss[0, 2, 0])
check("I1 electrically short coupler: coupling rises ~6 dB per octave", abs(slope - 6.0) < 0.3)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
sys.exit(0 if ok_all else 1)
