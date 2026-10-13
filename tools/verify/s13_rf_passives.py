#!/usr/bin/env python3
"""
s13_rf_passives.py - verification for kb/18-components-parts/rf-passives-and-support-parts.md

 1. 3-pole Butterworth pi low-pass (C-L-C), fc = 500 MHz, Z0 = 50 ohm: ideal values, nearest
    JLC-stocked values (6.8 pF preferred C0G, 33 nH), insertion loss at 434.125 MHz and
    rejection at 2f/3f, for (a) ideal parts, (b) wire-wound L (Q 40) + C0G (Q 400),
    (c) multilayer L (Q ~ 17 at 434 MHz, SRF 1.3 GHz modelled as a parallel C).
 2. Multilayer-inductor Q extrapolation Q(f) ~ Q(100 MHz) * sqrt(f/100 MHz) vs a datasheet point.
 3. Shunt capacitance of an ESD diode on a 50 ohm line: return loss / insertion loss at 434 MHz,
    1575 MHz, 2.45 GHz for 0.2, 0.4, 0.7 pF and for an 80 pF general-purpose TVS.
 4. Chip termination: 49.9 ohm + series L (0.4 nH part + 0.3 nH via) return loss vs frequency;
    two 100 ohm in parallel (L halves).
 5. DC block: series C with 0402 ESL 0.4 nH - series-resonant C for 434/915/1575/2450 MHz and the
    loss of a 100 pF block at each.
 6. Bias-tee choke: shunt 47 nH (SRF 2.9 GHz) at 1575.42 MHz -> |Z| and through loss.
 7. Circulator/isolator protecting a PA: worst-case |Gamma| seen by the PA for 20 dB isolation,
    20 dB port return loss and a 49.9 ohm chip load (RL from section 4).
 8. Mini-Circuits ADE-1 harmonics (m x n) table (REV X2 graphs file): LO-harmonic responses vs an
    ideal switching mixer (1/n for odd n), and the (m-1) dB-per-dB rule for RF-harmonic products
    between the -14 dBm and -4 dBm tables; half-IF rejection extrapolated to -34 dBm.
 9. JLC fee arithmetic: economic vs standard PCBA for a 433 MHz filter section.

Pre-registered expectations (2026-10-13, before the first run):
  R1 ideal Butterworth C = 6.37 pF, L = 31.8 nH (+-0.1).
  R2 rejection at 868.25 MHz >= 13 dB and at 1302.4 MHz >= 23 dB with ideal parts; IL at
     434.125 MHz < 0.3 dB with Q_L 40.
  R3 multilayer Q extrapolated to 900 MHz within 25 % of the 29 quoted for LQG15HS10N.
  R4 0.4 pF ESD at 1575 MHz: RL >= 19 dB; 80 pF TVS at 434 MHz: IL > 15 dB.
  R5 ADE-1 (1,3) response within 2 dB of 20 log 3 = 9.5 dB; slope rule within 3 dB for (2,1)
     and (3,3).
Run: python3 tools/verify/s13_rf_passives.py
"""
import numpy as np

ok_all = True
Z0 = 50.0


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


def prereg(name, cond):
    """Pre-registered prediction: reported as HIT/MISSED, never edited, does not fail the run."""
    print(f"[{'HIT ' if cond else 'MISSED'}] pre-registered: {name}")


def db(x):
    return 20 * np.log10(np.abs(x))


def abcd_series(Z):
    return np.array([[1, Z], [0, 1]], dtype=complex)


def abcd_shunt(Y):
    return np.array([[1, 0], [Y, 1]], dtype=complex)


def s21(M):
    A, B, Cc, D = M.ravel()
    return 2 / (A + B / Z0 + Cc * Z0 + D)


def s11(M):
    A, B, Cc, D = M.ravel()
    return (A + B / Z0 - Cc * Z0 - D) / (A + B / Z0 + Cc * Z0 + D)


def zC(C, f, Q=np.inf, esl=0.0):
    w = 2 * np.pi * f
    Xc = 1 / (w * C)
    return Xc / Q + 1j * (w * esl - Xc)


def zL(L, f, Q=np.inf, srf=None):
    w = 2 * np.pi * f
    Zs = w * L / Q + 1j * w * L
    if srf is not None:
        Cp = 1 / ((2 * np.pi * srf) ** 2 * L)
        Zs = 1 / (1 / Zs + 1j * w * Cp)
    return Zs


print("=== 1. 3-pole Butterworth pi LPF, fc 500 MHz ===")
fc = 500e6
Cid = 1 / (2 * np.pi * fc * Z0)          # g1 = g3 = 1
Lid = 2 * Z0 / (2 * np.pi * fc)          # g2 = 2
print(f"ideal C = {Cid*1e12:.2f} pF, L = {Lid*1e9:.2f} nH")
prereg("R1 ideal values 6.37 pF / 31.8 nH", abs(Cid * 1e12 - 6.37) < 0.1 and abs(Lid * 1e9 - 31.8) < 0.1)
f0, f2, f3 = 434.125e6, 868.25e6, 1302.375e6


def lpf(f, C, L, QL=np.inf, QC=np.inf, srf=None, esl=0.0):
    M = abcd_shunt(1 / zC(C, f, QC, esl)) @ abcd_series(zL(L, f, QL, srf)) @ abcd_shunt(1 / zC(C, f, QC, esl))
    return M


cases = [("ideal values, ideal parts", Cid, Lid, np.inf, np.inf, None, 0.0),
         ("6.8 pF / 33 nH, ideal", 6.8e-12, 33e-9, np.inf, np.inf, None, 0.0),
         ("6.8 pF C0G Q400 / 33 nH wire-wound Q40", 6.8e-12, 33e-9, 40, 400, None, 0.4e-9),
         ("6.8 pF C0G / 33 nH multilayer Q17, SRF 1.3 GHz", 6.8e-12, 33e-9, 17, 400, 1.3e9, 0.4e-9)]
res = {}
for name, C, L, QL, QC, srf, esl in cases:
    il = -db(s21(lpf(f0, C, L, QL, QC, srf, esl)))
    rl = -db(s11(lpf(f0, C, L, QL, QC, srf, esl)))
    r2 = -db(s21(lpf(f2, C, L, QL, QC, srf, esl)))
    r3 = -db(s21(lpf(f3, C, L, QL, QC, srf, esl)))
    res[name] = (il, rl, r2, r3)
    print(f"{name:48s}: IL(434) {il:.2f} dB, RL {rl:.1f} dB, rej 2f {r2:.1f} dB, 3f {r3:.1f} dB")
il, rl, r2, r3 = res["ideal values, ideal parts"]
prereg(f"R2 ideal rejection 2f {r2:.1f} >= 13 dB and 3f {r3:.1f} >= 23 dB", r2 >= 13 and r3 >= 23)
prereg(f"R2 IL at 434 MHz with Q_L 40: {res['6.8 pF C0G Q400 / 33 nH wire-wound Q40'][0]:.2f} dB < 0.3 dB",
      res['6.8 pF C0G Q400 / 33 nH wire-wound Q40'][0] < 0.3)
# the Butterworth response itself: |S21|^2 = 1/(1+(f/fc)^6)
bw = 10 * np.log10(1 + (f0 / fc) ** 6)
check(f"ideal-part IL {il:.2f} dB equals the Butterworth formula {bw:.2f} dB (f/fc = {f0/fc:.3f})", abs(il - bw) < 0.01)
# 1b. corrected design: 5-pole 0.1 dB Chebyshev, ripple bandwidth 500 MHz, E12 values
g = [1.1468, 1.3712, 1.9750, 1.3712, 1.1468]
w = 2 * np.pi * fc
vals = [g[0] / (w * Z0), g[1] * Z0 / w, g[2] / (w * Z0), g[3] * Z0 / w, g[4] / (w * Z0)]
print("5-pole 0.1 dB Chebyshev (C-L-C-L-C) ideal: " + ", ".join(
    f"{v*1e12:.2f} pF" if k % 2 == 0 else f"{v*1e9:.2f} nH" for k, v in enumerate(vals)))


def cheb(f, Cs, Ls, QL=40, QC=400, esl=0.4e-9, srf=None):
    M = abcd_shunt(1 / zC(Cs[0], f, QC, esl))
    M = M @ abcd_series(zL(Ls[0], f, QL, srf)) @ abcd_shunt(1 / zC(Cs[1], f, QC, esl))
    M = M @ abcd_series(zL(Ls[1], f, QL, srf)) @ abcd_shunt(1 / zC(Cs[2], f, QC, esl))
    return M


for lab, Cs, Ls, QL, esl in (("ideal values, lossless", (vals[0], vals[2], vals[4]), (vals[1], vals[3]), np.inf, 0.0),
                             ("E12 6.8/22/12/22/6.8, Q_L 40, ESL 0.4 nH", (6.8e-12, 12e-12, 6.8e-12), (22e-9, 22e-9), 40, 0.4e-9)):
    M0, M2, M3 = cheb(f0, Cs, Ls, QL, 400, esl), cheb(f2, Cs, Ls, QL, 400, esl), cheb(f3, Cs, Ls, QL, 400, esl)
    print(f"  {lab:42s}: IL(434) {-db(s21(M0)):.2f} dB, RL {-db(s11(M0)):.1f} dB, rej 2f {-db(s21(M2)):.1f} dB, 3f {-db(s21(M3)):.1f} dB")
Ce = cheb(f0, (6.8e-12, 12e-12, 6.8e-12), (22e-9, 22e-9), 40, 400, 0.4e-9)
print(f"  corrected E12 Chebyshev IL at 434 MHz = {-db(s21(Ce)):.2f} dB (reported, not tested; see the finite-Q split below)")
check(f"corrected E12 Chebyshev: RL(434) {-db(s11(Ce)):.1f} dB > 15 dB and 2f rejection > 25 dB",
      -db(s11(Ce)) > 15 and -db(s21(cheb(f2, (6.8e-12, 12e-12, 6.8e-12), (22e-9, 22e-9), 40, 400, 0.4e-9))) > 25)
Cn = cheb(f0, (6.8e-12, 12e-12, 6.8e-12), (22e-9, 22e-9), np.inf, np.inf, 0.4e-9)
print(f"  same E12 values lossless: IL {-db(s21(Cn)):.2f} dB -> loss from finite Q = {-db(s21(Ce))+db(s21(Cn)):.2f} dB")
# 3f with SRF near 3f: sweep SRF
print("3f rejection vs inductor SRF (33 nH, Q 40):", end=" ")
for srf in (1.0e9, 1.3e9, 1.6e9, 2.5e9, 5e9):
    print(f"SRF {srf/1e9:.1f} GHz -> {-db(s21(lpf(f3, 6.8e-12, 33e-9, 40, 400, srf, 0.4e-9))):.1f} dB;", end=" ")
print()

print("\n=== 2. Multilayer inductor Q extrapolation ===")
q100 = 8.0
q900 = q100 * np.sqrt(900 / 100)
print(f"Q 8 @ 100 MHz -> sqrt-f model {q900:.1f} @ 900 MHz (04/inductors-at-rf quotes 29 for LQG15HS10N), "
      f"{q100*np.sqrt(434.125/100):.1f} @ 434 MHz")
prereg("R3 within 25 % of 29", abs(q900 - 29) / 29 < 0.25)

print("\n=== 3. ESD capacitance on a 50 ohm line ===")
tab = {}
for Cesd in (0.2e-12, 0.4e-12, 0.7e-12, 80e-12):
    row = []
    for f in (434.125e6, 1575.42e6, 2.45e9):
        M = abcd_shunt(2j * np.pi * f * Cesd)
        row.append((-db(s11(M)), -db(s21(M))))
    tab[Cesd] = row
    print(f"C = {Cesd*1e12:5.1f} pF: " + "; ".join(f"{f/1e6:.0f} MHz RL {r:.1f} dB IL {i:.3f} dB"
                                            for f, (r, i) in zip((434.125e6, 1575.42e6, 2.45e9), row)))
prereg(f"R4 0.4 pF at 1575 MHz RL {tab[0.4e-12][1][0]:.1f} dB >= 19 dB", tab[0.4e-12][1][0] >= 19)
prereg(f"R4 80 pF at 434 MHz IL {tab[80e-12][0][1]:.1f} dB > 15 dB", tab[80e-12][0][1] > 15)

print("\n=== 4. Chip termination return loss ===")
for label, R, L in (("49.9 ohm, 0.4 nH + 0.3 nH via", 49.9, 0.7e-9), ("2 x 100 ohm parallel (0.2 + 0.3 nH)", 50.0, 0.5e-9),
                    ("49.9 ohm, part only 0.4 nH", 49.9, 0.4e-9)):
    out = []
    for f in (434.125e6, 915e6, 1575.42e6, 2.45e9):
        Z = R + 2j * np.pi * f * L
        out.append(-db((Z - Z0) / (Z + Z0)))
    print(f"{label:38s}: RL " + ", ".join(f"{v:.1f}" for v in out) + " dB at 434/915/1575/2450 MHz")
RL_term = -db(((49.9 + 2j * np.pi * 434.125e6 * 0.7e-9) - Z0) / ((49.9 + 2j * np.pi * 434.125e6 * 0.7e-9) + Z0))

print("\n=== 5. DC blocks (0402 ESL 0.4 nH) ===")
for f in (434.125e6, 915e6, 1575.42e6, 2.45e9):
    Cres = 1 / ((2 * np.pi * f) ** 2 * 0.4e-9)
    Z100 = zC(100e-12, f, Q=300, esl=0.4e-9)
    il100 = -db(s21(abcd_series(Z100)))
    print(f"{f/1e6:7.1f} MHz: series-resonant C = {Cres*1e12:.1f} pF; 100 pF block |Z| = {abs(Z100):.2f} ohm, IL {il100:.3f} dB")
Cg = 1 / ((2 * np.pi * 1575.42e6) ** 2 * 0.4e-9)
check(f"GNSS DC-block resonant value {Cg*1e12:.1f} pF lies in 22-33 pF", 22 < Cg * 1e12 < 33)

print("\n=== 6. Bias-tee choke at L1 ===")
Zch = zL(47e-9, 1575.42e6, Q=30, srf=2.9e9)
il_ch = -db(s21(abcd_shunt(1 / Zch)))
print(f"47 nH (SRF 2.9 GHz, Q 30) at 1575.42 MHz: |Z| = {abs(Zch):.0f} ohm (vs wL {2*np.pi*1575.42e6*47e-9:.0f} ohm); shunt loss {il_ch:.3f} dB")
check("choke loss < 0.1 dB", il_ch < 0.1)
Zch2 = zL(47e-9, 1575.42e6, Q=30, srf=1.6e9)
print(f"same choke if SRF were 1.6 GHz: |Z| = {abs(Zch2):.0f} ohm (near SRF: real and large) - the problem is just above SRF, where it turns capacitive")

print("\n=== 7. Isolator protecting a PA ===")
iso_db, rl_db = 20.0, 20.0
b = 10 ** (-iso_db / 20)
r = 10 ** (-rl_db / 20)
gT = 10 ** (-RL_term / 20)
a = 10 ** (-0.35 / 20)
g_worst = r + b + a ** 2 * gT
print(f"termination RL {RL_term:.1f} dB -> |Gamma_T| {gT:.3f}; worst |Gamma| at PA = {r:.2f} + {b:.2f} + {a**2*gT:.3f} = {g_worst:.3f} "
      f"(VSWR {(1+g_worst)/(1-g_worst):.2f}) with an open/short antenna")
check("VSWR < 1.7 (06/circulators gives 1.63 for a 30 dB-RL load)", (1 + g_worst) / (1 - g_worst) < 1.7)
for P in (0.1, 0.5, 2.0):
    print(f"   {P} W PA, antenna open: termination dissipates ~{P*a**2:.2f} W -> load rating (0402 is 62.5 mW!)")

print("\n=== 8. ADE-1 spur (m x n) table ===")
# rows m = RF harmonic order 0..3 (subset), columns n = LO harmonic order 0..5; dBc below the IF output
t14 = {(0, 1): 16, (0, 2): 37, (0, 3): 12, (1, 0): 18, (1, 1): 0, (1, 2): 25, (1, 3): 11, (1, 4): 38, (1, 5): 22,
       (2, 0): 73, (2, 1): 51, (2, 2): 79, (2, 3): 52, (3, 1): 63, (3, 2): 74, (3, 3): 62}
t4 = {(0, 1): 24, (0, 2): 51, (0, 3): 23, (1, 0): 19, (1, 1): 0, (1, 2): 27, (1, 3): 12, (1, 4): 41, (1, 5): 24,
      (2, 0): 63, (2, 1): 43, (2, 2): 71, (2, 3): 45, (3, 1): 42, (3, 2): 47, (3, 3): 44}
for n in (3, 5):
    print(f"(1,{n}) response: table {t14[(1, n)]} dBc vs ideal switching mixer 20 log {n} = {20*np.log10(n):.1f} dB")
prereg("R5 (1,3) within 2 dB of 9.5 dB", abs(t14[(1, 3)] - 20 * np.log10(3)) <= 2)
print(f"(1,2), (1,4) even-order LO responses {t14[(1,2)]}, {t14[(1,4)]} dBc: set by balun/diode balance, not by the 1/n law")
for m, n in ((2, 1), (2, 2), (2, 3), (3, 1), (3, 3)):
    d = t14[(m, n)] - t4[(m, n)]
    print(f"({m},{n}): {t14[(m,n)]} dBc at -14 dBm, {t4[(m,n)]} dBc at -4 dBm -> {d} dB per 10 dB (rule: {10*(m-1)})")
prereg("R5 slope rule within 3 dB for (2,1)", abs((t14[(2, 1)] - t4[(2, 1)]) - 10) <= 3)
prereg("R5 slope rule within 3 dB for (3,3)", abs((t14[(3, 3)] - t4[(3, 3)]) - 20) <= 3)
hi = t14[(2, 2)] + (2 - 1) * 20
print(f"half-IF (2,2) rejection extrapolated to -34 dBm input: {t14[(2,2)]} + 1 x 20 = {hi} dBc")
# example plan: 433.92 MHz RX, low-side LO, IF 10.7 MHz -> where do interferers produce 10.7 MHz?
frf, fif = 433.92e6, 10.7e6
flo = frf - fif
print(f"Plan: RF {frf/1e6:.2f} MHz, LO {flo/1e6:.2f} MHz (low side), IF {fif/1e6:.1f} MHz; responses m f_RF - n f_LO = +-IF:")
for m in (1, 2, 3):
    for n in (1, 2, 3):
        for sgn in (+1, -1):
            f = (n * flo + sgn * fif) / m
            if 300e6 < f < 600e6 and not (m == 1 and n == 1 and sgn == 1):
                print(f"   ({m},{n}) {'+' if sgn>0 else '-'}IF: interferer at {f/1e6:.3f} MHz; ADE-1 rejection (-14 dBm table) {t14.get((m,n),'n/a')} dBc")

print("\n=== 9. JLC assembly fees for a 433 MHz pi filter + DC block + ESD ===")
lines = [("6.8 pF C0G (C1576)", "preferred"), ("33 nH LQW15AN33NG00D (C113114)", "extended"),
         ("100 pF C0G DC block (C1546)", "basic"), ("PESD5V0F1BL ESD (C45961)", "extended")]
ext = sum(1 for _, k in lines if k == "extended")
print(f"{ext} extended lines -> economic PCBA US${3*ext} extra (preferred/basic exempt); standard PCBA charges every unique line the same")
check("fee arithmetic: 2 extended lines -> US$6", ext == 2)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
