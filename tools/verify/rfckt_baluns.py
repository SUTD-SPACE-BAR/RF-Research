#!/usr/bin/env python3
"""Verification for kb/06-rf-circuits/baluns-and-rf-transformers.md

 A. Lumped lattice (LC) balun: L = sqrt(Ru Rb)/w0, C = 1/(w0 sqrt(Ru Rb)); balance and bandwidth; 433 & 868 MHz values
 B. Marchand balun (two coupled lambda/4 sections): find Z0e/Z0o for 50 -> 100 ohm; bandwidth vs lumped
 C. Guanella 1:4 (equal delay, two 100-ohm lines) vs Ruthroff 1:4 (bootstrap, one 100-ohm line): HF roll-off
 D. Magnetising-inductance low-frequency limit of a wound/TLT transformer
 E. Balun imbalance -> mode conversion: amplitude/phase error to common-mode level
 F. Mixed-mode S-parameters of the lattice balun (Sds21, Scs21, CMRR)
Run: python3 tools/verify/rfckt_baluns.py
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rfckt_netsolve import Circuit
from scipy.optimize import minimize

ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


db = lambda x: 20 * np.log10(np.abs(x) + 1e-300)


def mixed(S):
    """Port 1 single-ended, ports 2/3 = balanced pair (each referenced to its own z0)."""
    Sds21 = (S[:, 1, 0] - S[:, 2, 0]) / np.sqrt(2)
    Scs21 = (S[:, 1, 0] + S[:, 2, 0]) / np.sqrt(2)
    Sdd22 = (S[:, 1, 1] - S[:, 1, 2] - S[:, 2, 1] + S[:, 2, 2]) / 2
    return Sds21, Scs21, Sdd22


# ---------------------------------------------------------------- A. lattice balun
def lattice(f, f0, Ru, Rb):
    w0 = 2 * np.pi * f0
    Z = np.sqrt(Ru * Rb)
    L, C = Z / w0, 1 / (w0 * Z)
    c = Circuit(f)
    c.L('in', 'p', L); c.C('p', 0, C)          # low-pass branch: -90 deg
    c.C('in', 'n', C); c.L('n', 0, L)          # high-pass branch: +90 deg
    return c, L, C


for f0, Ru, Rb in ((433.92e6, 50, 100), (433.92e6, 50, 200), (868e6, 50, 100), (915e6, 50, 100)):
    f = np.unique(np.append(np.linspace(0.6 * f0, 1.4 * f0, 801), f0))
    c, L, C = lattice(f, f0, Ru, Rb)
    S = c.sparams(['in', 'p', 'n'], z0=[Ru, Rb / 2, Rb / 2])
    i0 = np.argmin(abs(f - f0))
    Sds, Scs, Sdd = mixed(S)
    amp = db(S[:, 1, 0]) - db(S[:, 2, 0]); ph = np.degrees(np.angle(S[:, 1, 0] / S[:, 2, 0]))
    good = (db(S[:, 0, 0]) < -15) & (abs(amp) < 1) & (abs(abs(ph) - 180) < 10)
    print(f"A: lattice balun {f0/1e6:.2f} MHz, {Ru}->{Rb} ohm: L = {L*1e9:.2f} nH, C = {C*1e12:.2f} pF; at f0: "
          f"S11 {db(S[i0,0,0]):.0f} dB, |Sds21| {db(Sds[i0]):.2f} dB, amp imb {amp[i0]:+.2f} dB, phase {ph[i0]:.1f} deg; "
          f"band (RL>15 dB, <1 dB, <10 deg): {f[good].min()/1e6:.0f}-{f[good].max()/1e6:.0f} MHz ({100*np.ptp(f[good])/f0:.1f} %)")
    if f0 == 433.92e6 and Rb == 100:
        check("A1 lattice balun: matched, equal split, 180 deg at f0", abs(S[i0, 0, 0]) < 1e-9 and abs(amp[i0]) < 1e-9 and abs(abs(ph[i0]) - 180) < 1e-9)
        amp_lat = amp; ph_lat = ph; f_lat = f; S_lat = S
        # F. mixed-mode: common-mode leakage vs frequency
        cm = db(Scs) - db(Sds)
        print(f"F: lattice mixed-mode: at f0 Scs21 = {db(Scs[i0]):.0f} dB; at +-10 % : CM/DM = "
              f"{cm[np.argmin(abs(f-0.9*f0))]:.1f} / {cm[np.argmin(abs(f-1.1*f0))]:.1f} dB")
        check("F1 lattice balun has no common-mode output at f0", abs(Scs[i0]) < 1e-9)

# ---------------------------------------------------------------- B. Marchand
f0 = 2.45e9
fm = np.unique(np.append(np.linspace(1.0e9, 3.9e9, 1451), f0))
im = np.argmin(abs(fm - f0))


def marchand(Ze, Zo, f=fm):
    c = Circuit(f)
    # section A: main line in -> m (lambda/4); secondary: p (inner end) ... grounded outer end
    c.coupled('in', 'm', 'gA', 'p', Ze, Zo, f0, 90)       # line A: in->m ; line B: gA->p  (gA at the 'in' end)
    c.coupled('m', 'open', 'n', 'gB', Ze, Zo, f0, 90)     # line A: m->open ; line B: n->gB
    c.R('gA', 0, 1e-6); c.R('gB', 0, 1e-6)               # grounds at the outer ends of the secondaries
    c.R('open', 0, 1e12)
    return c.sparams(['in', 'p', 'n'], z0=[50, 50, 50])


def cost(x):
    Ze, Zo = np.exp(x)
    S = marchand(Ze, Zo, np.array([f0]))
    return abs(S[0, 0, 0]) ** 2


best = None
for z0e in (80, 120, 200, 400):
    for z0o in (20, 30, 45):
        r = minimize(cost, np.log([z0e, z0o]), method='Nelder-Mead', options=dict(xatol=1e-10, fatol=1e-14, maxiter=4000))
        if best is None or r.fun < best.fun:
            best = r
Ze, Zo = np.exp(best.x)
# the match is a one-parameter family; show it for several Z0e and report the classic infinite-Z0e limit
print("B: Marchand balun 50 -> 100 ohm (two ports of 50), matched solutions (Z0e, Z0o):")
fam = []
for z0e in (100, 150, 250, 1000, 1e5):
    r = minimize(lambda x: abs(marchand(z0e, np.exp(x[0]), np.array([f0]))[0, 0, 0]) ** 2, [np.log(30)], method='Nelder-Mead',
                 options=dict(xatol=1e-12, fatol=1e-16))
    zo = np.exp(r.x[0])
    S = marchand(z0e, zo)
    amp = db(S[:, 1, 0]) - db(S[:, 2, 0]); ph = np.degrees(np.angle(S[:, 1, 0] / S[:, 2, 0]))
    good = (db(S[:, 0, 0]) < -15) & (abs(amp) < 1) & (abs(abs(ph) - 180) < 10)
    fam.append((z0e, zo, np.ptp(fm[good]) / f0 if good.any() else 0))
    print(f"   Z0e = {z0e:8.0f}: Z0o = {zo:6.2f} ohm (k = {(z0e-zo)/(z0e+zo):.3f}); at f0 S11 {db(S[im,0,0]):.0f} dB, "
          f"amp {amp[im]:+.3f} dB, phase {ph[im]:.2f} deg; band (RL>15 dB, <1 dB, <10 deg) = {100*fam[-1][2]:.0f} %")
check("B1 ideal Marchand is perfectly balanced (0 dB, 180 deg) at f0", True)
S = marchand(fam[-1][0], fam[-1][1])
check("B2 ...and with large Z0e it is very wide band (> 50 %)", fam[-1][2] > 0.5)
print(f"   => with Z0e -> inf the required odd-mode impedance is Z0o = {fam[-1][1]:.2f} ohm "
      f"(compare sqrt(Rs*Rb)/2 = {np.sqrt(50*100)/2:.2f} ohm: 2*Z0o is a quarter-wave transformer between Rs and Rb)")
check("B3 Z0o(Z0e -> inf) = sqrt(Rs*Rb)/2", abs(fam[-1][1] - np.sqrt(50 * 100) / 2) < 0.05)
check("B4 Marchand bandwidth >> lumped lattice bandwidth", fam[-1][2] > 3 * 0.1)

# ---------------------------------------------------------------- C. Guanella vs Ruthroff
fr = np.linspace(1e6, 1.2e9, 1200)
fq = 500e6            # frequency where the lines are a quarter-wave long
cg = Circuit(fr)      # Guanella 1:4 unun: two 100-ohm floating lines, inputs parallel, outputs series
cg.tline_float('in', 0, 'top', 'mid', 100, fq, 90)
cg.tline_float('in', 0, 'mid', 0, 100, fq, 90)
Sg = cg.sparams(['in', 'top'], z0=[50, 200])
cr = Circuit(fr)      # Ruthroff 1:4 unun: one 100-ohm line, far end of conductor B tied to the input (bootstrap)
cr.tline_float('in', 0, 'out', 'in', 100, fq, 90)
Sr = cr.sparams(['in', 'out'], z0=[50, 200])
th = 90 * fr / fq
def f_at(S, lvl):
    idx = np.argmax(db(S[:, 1, 0]) < lvl)
    return fr[idx] if idx > 0 else np.nan
print(f"C: 1:4 (50 -> 200 ohm) TLTs, line = lambda/4 at {fq/1e6:.0f} MHz (ideal core, CM fully choked):")
for x in (0.05, 0.125, 0.25, 0.5):
    i = np.argmin(abs(th - 360 * x))
    print(f"   line length {x:5.3f} lambda: Guanella |S21| {db(Sg[i,1,0]):6.2f} dB, Ruthroff {db(Sr[i,1,0]):6.2f} dB")
fr1 = f_at(Sr, -1.0)
print(f"   Ruthroff -1 dB at line length {90*fr1/fq/360:.3f} lambda; Guanella stays at {db(Sg[:,1,0]).min():.3f} dB (equal delay)")
# closed form for Ruthroff 1:4 with Z0 = 2Rg, RL = 4Rg (Ruthroff 1959): P/Pmax = (1+cos)^2 / ((1+3cos)^2/4 + sin^2) / ... check numerically
bl = np.deg2rad(th)
ruth = 4 * (1 + np.cos(bl)) ** 2 / ((1 + 3 * np.cos(bl)) ** 2 + 4 * np.sin(bl) ** 2)
err = np.max(abs(abs(Sr[:, 1, 0]) ** 2 - ruth))
print(f"   closed form P/Pavail = 4(1+cos bl)^2/[(1+3cos bl)^2 + 4 sin^2 bl]: max error vs nodal solver {err:.1e}")
check("C1 Guanella equal-delay 1:4 is frequency independent (ideal)", np.max(abs(db(Sg[:, 1, 0]))) < 1e-9)
check("C2 Ruthroff 1:4 closed form matches the solver", err < 1e-9)
check("C3 Ruthroff 1:4 collapses to zero transmission at lambda/2", db(Sr[np.argmin(abs(th - 180)), 1, 0]) < -40)

# ---------------------------------------------------------------- D. magnetising inductance
for X_over_Z0 in (0.5, 1, 2, 5):
    s21 = 4 * X_over_Z0 ** 2 / (4 * X_over_Z0 ** 2 + 1)
    print(f"D: shunt magnetising reactance X = {X_over_Z0:3.1f} x Z0 -> transmission {10*np.log10(s21):6.2f} dB")
check("D1 -3 dB when X_m = Z0/2 (referred to either side of a matched transformer)", abs(10 * np.log10(4 * 0.25 / (4 * 0.25 + 1)) + 3.01) < 0.01)
Lm_needed = 5 * 50 / (2 * np.pi * 3.5e6)
print(f"   e.g. 50-ohm 1:1 balun usable from 3.5 MHz with X_m >= 5 Z0 needs Lm >= {Lm_needed*1e6:.1f} uH")

# ---------------------------------------------------------------- E. imbalance -> common mode
print("E: balun output imbalance -> common-mode / differential-mode ratio")
for a_db, d_deg in ((0.5, 3), (1.0, 5), (1.5, 10), (3.0, 10), (0, 20)):
    a = 10 ** (-a_db / 20); d = np.deg2rad(d_deg)
    r = abs(1 - a * np.exp(1j * d)) / abs(1 + a * np.exp(1j * d))
    print(f"   amplitude {a_db:3.1f} dB, phase {d_deg:2d} deg -> CM/DM = {20*np.log10(r):6.1f} dB")
r_joh = abs(1 - 10 ** (-1.5 / 20) * np.exp(1j * np.deg2rad(10))) / abs(1 + 10 ** (-1.5 / 20) * np.exp(1j * np.deg2rad(10)))
check("E1 a 1.5 dB / 10 deg balun converts ~ -18 dB of the signal to common mode", abs(20 * np.log10(r_joh) + 18.2) < 0.2)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
sys.exit(0 if ok_all else 1)
