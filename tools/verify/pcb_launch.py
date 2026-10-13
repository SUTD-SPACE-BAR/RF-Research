#!/usr/bin/env python3
"""
pcb_launch.py — verification script for kb/13-pcb-rf-layout-emc/connectors-and-launches.md

  1. Return loss of a shunt capacitance on a 50-ohm line (pads, connector pins): exact vs omega*C*Z0/2.
  2. SMA edge-launch signal pad on JLC04161H-7628: the pad as a short line section, with the L2 plane intact,
     with L2 voided under the pad (reference L3), and with L2+L3 voided (reference L4); RL 0.4-6 GHz.
  3. U.FL signal pad on JLC-7628 and on 2-layer 1.6 mm (microstrip vs CPWG feed).
  4. Pin/pad series inductance compensated by pad capacitance: a low-pass L-C-L "matched" when sqrt(L/C) = 50.
  5. Vertical (through-board) launch as a coaxial via: Z = (60/sqrt(er)) ln(D/d); antipad for 50 ohm.
  6. Return-loss budget: worst-case vs RSS cascade of connector + launch + line + pad reflections;
     mismatch loss; and U.FL 1.13 mm pigtail loss per 100 mm (Hirose data, sqrt(f) scaling).

Run: python3 tools/verify/pcb_launch.py     (a few seconds)
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tline_microstrip import ms_hj  # noqa: E402

C0 = 299_792_458.0
MU0 = 4e-7 * np.pi
Z0 = 50.0
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def rl_db(G):
    return -20 * np.log10(np.maximum(abs(G), 1e-12))


def abcd_line(Z, ee, l, f):
    bl = 2 * np.pi * f * np.sqrt(ee) / C0 * l
    return np.array([[np.cos(bl), 1j * Z * np.sin(bl)], [1j * np.sin(bl) / Z, np.cos(bl)]])


def s11_from_abcd(M, z0=Z0):
    A, B, C, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
    return (A + B / z0 - C * z0 - D) / (A + B / z0 + C * z0 + D)


print("=" * 96)
print("1. Shunt C on a 50-ohm line: |Gamma| = wCZ0 / sqrt(4 + (wCZ0)^2)")
print("=" * 96)
for C in [0.05e-12, 0.1e-12, 0.3e-12, 0.65e-12, 1.0e-12]:
    row = []
    for f in [433e6, 915e6, 1575e6, 2.45e9, 5.8e9]:
        w = 2 * np.pi * f
        M = np.array([[1, 0], [1j * w * C, 1]])
        G = s11_from_abcd(M)
        approx = w * C * Z0 / 2
        row.append(f"{f/1e9:.2f}G: RL {rl_db(G):5.1f} dB")
        assert abs(abs(G) - w * C * Z0 / np.sqrt(4 + (w * C * Z0) ** 2)) < 1e-12
    print(f"  C = {C*1e12:4.2f} pF: " + "; ".join(row))
G65 = abs(s11_from_abcd(np.array([[1, 0], [1j * 2 * np.pi * 2.45e9 * 0.65e-12, 1]])))
check("0.65 pF excess pad capacitance limits RL to ~12 dB at 2.45 GHz", 11 < rl_db(G65) < 14, f"({rl_db(G65):.1f} dB)")

print("\n" + "=" * 96)
print("2. SMA edge-launch pad (1.3 mm wide x 3.0 mm long) on JLC04161H-7628, t = 35 um")
print("=" * 96)
Wp, Lp, t = 1.3e-3, 3.0e-3, 35e-6
refs = [("L2 intact (h = 0.2104 mm, Dk 4.4)", 0.2104e-3, 4.4),
        ("L2 voided -> L3 (h = 0.2104+0.0152+1.065 mm, Dk ~4.55)", 0.2104e-3 + 0.0152e-3 + 1.065e-3, 4.55),
        ("L2+L3 voided -> L4 (h ~1.52 mm)", 1.52e-3, 4.5)]
freqs = [0.433e9, 0.915e9, 1.575e9, 2.45e9, 3.5e9, 5.8e9]
res2 = {}
for lab, h, er in refs:
    Zp, ep = ms_hj(Wp, h, er, t)
    row = []
    for f in freqs:
        G = s11_from_abcd(abcd_line(Zp, ep, Lp, f))
        row.append(rl_db(G))
    res2[lab] = row
    print(f"  {lab:52s}: Z_pad {Zp:5.1f} Ohm | " + " ".join(f"{f/1e9:.2f}G {r:4.1f}" for f, r in zip(freqs, row)) + " dB")
k_intact, k_void = list(res2)[0], list(res2)[1]
check("voiding L2 under the SMA pad lifts RL at 2.45 GHz above 20 dB (from < 12 dB)",
      res2[k_void][3] > 20 and res2[k_intact][3] < 12, f"({res2[k_intact][3]:.1f} -> {res2[k_void][3]:.1f} dB)")

print("\n" + "=" * 96)
print("3. U.FL signal pad (~1.0 x 1.0 mm) as a line section")
print("=" * 96)
for lab, h, er in [("JLC-7628, L2 under pad", 0.2104e-3, 4.4), ("JLC-7628, L2 voided (ref L3)", 1.29e-3, 4.55),
                   ("2-layer 1.6 mm (h 1.43 mm)", 1.43e-3, 4.5)]:
    Zp, ep = ms_hj(1.0e-3, h, er, t)
    row = [rl_db(s11_from_abcd(abcd_line(Zp, ep, 1.0e-3, f))) for f in freqs]
    print(f"  {lab:32s}: Z_pad {Zp:5.1f} Ohm | " + " ".join(f"{f/1e9:.2f}G {r:4.1f}" for f, r in zip(freqs, row)) + " dB")
Zp, ep = ms_hj(1.0e-3, 0.2104e-3, 4.4, t)
rl_uf = rl_db(s11_from_abcd(abcd_line(Zp, ep, 1.0e-3, 0.915e9)))
check("a U.FL pad on JLC-7628 with L2 intact is still > 25 dB RL at 915 MHz (small pad)", rl_uf > 25, f"({rl_uf:.1f} dB)")

print("\n" + "=" * 96)
print("4. Pin inductance compensated by pad capacitance (L-C-L low-pass 'artificial line')")
print("=" * 96)


def L_wire(l, r):
    return MU0 * l / (2 * np.pi) * (np.log(2 * l / r) - 1)


Lwire1 = L_wire(1.0e-3, 0.38e-3)
print(f"  1 mm of 0.76 mm-diameter pin alone (isolated-wire partial L): {Lwire1*1e9:.2f} nH; the transition loop"
      f" (pin + solder + gap where the return leaves the connector body for the board ground) is typically a few"
      f" tenths of nH -> use 0.5 nH as a representative value")
Lpin = 0.5e-9
Copt = 2 * Lpin / Z0**2            # T-section L/2 - C - L/2 matched when sqrt(L/C) = Z0 -> C = L/Z0^2 with L total
Copt = Lpin / Z0**2
for C in [0.0, Copt, 2 * Copt]:
    row = []
    for f in freqs:
        w = 2 * np.pi * f
        M = np.array([[1, 1j * w * Lpin / 2], [0, 1]]) @ np.array([[1, 0], [1j * w * C, 1]]) @ \
            np.array([[1, 1j * w * Lpin / 2], [0, 1]])
        row.append(min(rl_db(s11_from_abcd(M)), 60.0))
    print(f"  pad C = {C*1e12:4.2f} pF (RL capped at 60): " + " ".join(f"{f/1e9:.2f}G {r:4.1f}" for f, r in zip(freqs, row)) + " dB")
fc = 1 / (np.pi * np.sqrt(Lpin * Copt))
print(f"  sqrt(L/C) = 50 Ohm for C = L/Z0^2 = {Copt*1e12:.2f} pF; the compensated section's cutoff ~ {fc/1e9:.0f} GHz")
M = np.array([[1, 1j * 2 * np.pi * 5.8e9 * Lpin / 2], [0, 1]]) @ np.array([[1, 0], [1j * 2 * np.pi * 5.8e9 * Copt, 1]]) @ \
    np.array([[1, 1j * 2 * np.pi * 5.8e9 * Lpin / 2], [0, 1]])
M0 = np.array([[1, 1j * 2 * np.pi * 5.8e9 * Lpin], [0, 1]])
check("adding the matching pad capacitance improves RL at 5.8 GHz", rl_db(s11_from_abcd(M)) > rl_db(s11_from_abcd(M0)) + 10,
      f"({rl_db(s11_from_abcd(M0)):.1f} -> {rl_db(s11_from_abcd(M)):.1f} dB)")

print("\n" + "=" * 96)
print("5. Vertical launch: signal barrel inside a ring of ground vias / antipad (coaxial approximation)")
print("=" * 96)
for er in [4.4, 3.66]:
    for d in [0.5e-3, 0.9e-3, 1.3e-3]:
        D50 = d * np.exp(50 * np.sqrt(er) / 60)
        print(f"  er {er}: barrel {d*1e3:.1f} mm -> 50-ohm ground-ring/antipad diameter {D50*1e3:.2f} mm")
Zt = 60 / np.sqrt(4.4) * np.log(2.0 / 0.9)
print(f"  a 0.9 mm barrel with a 2.0 mm antipad: Z ~ {Zt:.0f} Ohm (capacitive) — typical of un-optimised vertical SMAs")
check("a 0.9 mm barrel needs a ~5 mm ground ring for 50 ohm in FR-4", 4.5e-3 < 0.9e-3 * np.exp(50 * np.sqrt(4.4) / 60) < 5.5e-3)

print("\n" + "=" * 96)
print("6. Return-loss budget for an RF path: connector + launch + line + component pads")
print("=" * 96)
parts = [("U.FL mated pair (VSWR 1.3 max <= 3 GHz)", (1.3 - 1) / (1.3 + 1)),
         ("launch pad, compensated", 10 ** (-25 / 20)),
         ("line impedance +10 % (55 ohm)", abs((55 - 50) / (55 + 50))),
         ("series 0402 DC-block pads", 10 ** (-30 / 20))]
for n, g in parts:
    print(f"  {n:42s}: |Gamma| {g:.3f} (RL {rl_db(g):4.1f} dB)")
gw = sum(g for _, g in parts)
gr = np.sqrt(sum(g * g for _, g in parts))
for lab, g in [("worst case (all in phase)", gw), ("RSS (random phases)", gr)]:
    vswr = (1 + g) / (1 - g)
    ml = -10 * np.log10(1 - g * g)
    print(f"  {lab:28s}: |Gamma| {g:.3f}, RL {rl_db(g):4.1f} dB, VSWR {vswr:.2f}, mismatch loss {ml:.3f} dB")
check("even worst-case stacking of these reflections costs < 0.35 dB mismatch loss (RSS ~0.1 dB)", -10 * np.log10(1 - gw**2) < 0.35)
for f in [0.433e9, 0.915e9, 1.575e9, 2.45e9, 5.8e9]:
    a3 = 3.73 * np.sqrt(f / 3e9)    # dB/m, Hirose 1.13 mm cable 3.73 dB/m @ 3 GHz, sqrt(f) scaling (conductor-dominated)
    print(f"  U.FL 1.13 mm cable @ {f/1e9:5.3f} GHz: ~{a3:.2f} dB/m -> {a3*0.1:.2f} dB per 100 mm pigtail")
a6 = 3.73 * np.sqrt(6 / 3)
print(f"  check vs Hirose 6 GHz value 5.44 dB/m: sqrt-f scaling gives {a6:.2f} dB/m")
check("sqrt(f) scaling of Hirose 3 GHz loss predicts the 6 GHz value within 10 %", abs(a6 - 5.44) / 5.44 < 0.1)

print("\nALL CHECKS PASSED" if ok_all else "\nSOME CHECKS FAILED")
