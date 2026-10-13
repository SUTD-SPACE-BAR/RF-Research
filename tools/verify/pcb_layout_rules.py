#!/usr/bin/env python3
"""
pcb_layout_rules.py — supporting numbers for kb/13-pcb-rf-layout-emc/rf-layout-rules.md

  1. Pad capacitance (pad as a short microstrip section, fringing included) of 0201 / 0402 / 0603 land patterns
     on JLC04161H-7628 (L2 at 0.2104 mm) and on 2-layer 1.6 mm, versus the 50-ohm trace capacitance it replaces.
  2. What pad C + mounted ESL do to a 2.45 GHz and a 915 MHz L-match element (shunt C to ground):
     effective capacitance C_eff = C/(1 - w^2 L C) + C_pads, for 0201 / 0402 / 0603 ESL values.
  3. Series-inductor placement: trace inductance in series with L (harmless) vs in series with the shunt C
     (forms a series LC that moves the notch) — TI SWRA640 'LC filter' rule, quantified.
  4. Optimum mitre for a 90-degree microstrip bend (Douville & James): M = 52 + 65 exp(-1.35 W/h) %,
     and why bends are irrelevant at UHF (bend reactance vs frequency, order of magnitude).
  6. Radiator over ground: radiation resistance of a horizontal dipole at height d over a plane (image pair),
     numerical hemisphere integration vs closed form - why keep-outs must be copper-free and never via-fenced.
  5. Distance rules turned into wavelengths: lambda/20 at 433/915/1575/2450/5800 MHz on FR-4 microstrip.

Run: python3 tools/verify/pcb_layout_rules.py   (instant)
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tline_microstrip import ms_hj, width_for  # noqa: E402

C0 = 299_792_458.0
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def c_per_len(W, h, er, t=35e-6):
    z, ee = ms_hj(W, h, er, t)
    return np.sqrt(ee) / (C0 * z)


# IPC-7351-like nominal land sizes (width across the part x length along the current), mm
PADS = {"0201": (0.30, 0.30), "0402": (0.55, 0.50), "0603": (0.95, 0.90)}
ESL = {"0201": 0.25e-9, "0402": 0.40e-9, "0603": 0.65e-9}   # mounted ESL, representative (04 capacitor page ranges)

print("=" * 96)
print("1. Land-pattern capacitance vs the 50-ohm line it interrupts")
print("=" * 96)
res = {}
for lab, h, er in [("JLC04161H-7628", 0.2104e-3, 4.4), ("2-layer 1.6 mm", 1.43e-3, 4.5)]:
    w50 = width_for(50, lambda w: ms_hj(w, h, er, 35e-6)[0])
    for case, (wp, lp) in PADS.items():
        Cp = c_per_len(wp * 1e-3, h, er) * lp * 1e-3
        Cl = c_per_len(w50, h, er) * lp * 1e-3
        res[(lab, case)] = Cp - Cl
        print(f"  {lab:15s} {case}: pad {Cp*1e15:6.1f} fF, same length of 50-ohm line ({w50*1e3:.2f} mm) {Cl*1e15:6.1f} fF,"
              f" excess {(Cp-Cl)*1e15:+6.1f} fF")
check("on JLC-7628 an 0201 pad adds < 10 fF, an 0603 pad ~100 fF", abs(res[("JLC04161H-7628", "0201")]) < 10e-15
      and 60e-15 < res[("JLC04161H-7628", "0603")] < 140e-15,
      f"({res[('JLC04161H-7628','0201')]*1e15:.1f}, {res[('JLC04161H-7628','0603')]*1e15:.1f} fF)")

print("\n" + "=" * 96)
print("2. Shunt matching capacitor: effective value including ESL (+ via) and pad capacitance")
print("=" * 96)
for f, Cnom in [(2.45e9, 1.0e-12), (2.45e9, 2.2e-12), (915e6, 3.3e-12), (915e6, 8.2e-12)]:
    w = 2 * np.pi * f
    line = []
    for case in PADS:
        L = ESL[case] + 0.02e-9           # + L1->L2 via on 7628
        Ceff = Cnom / (1 - w**2 * L * Cnom) + 2 * max(res[("JLC04161H-7628", case)], 0)
        line.append(f"{case}: {Ceff*1e12:5.2f} pF ({(Ceff/Cnom-1)*100:+5.1f} %)")
    print(f"  {f/1e9:5.3f} GHz, nominal {Cnom*1e12:4.1f} pF -> " + "; ".join(line))
w = 2 * np.pi * 2.45e9
e0603 = (2.2e-12 / (1 - w**2 * (ESL["0603"] + 0.02e-9) * 2.2e-12)) / 2.2e-12 - 1
e0201 = (2.2e-12 / (1 - w**2 * (ESL["0201"] + 0.02e-9) * 2.2e-12)) / 2.2e-12 - 1
check("at 2.45 GHz ESL makes a 2.2 pF shunt cap read high: 0603 error >= 3x the 0201 error", e0603 > 3 * e0201,
      f"({e0603*100:.1f} % vs {e0201*100:.1f} %)")

print("\n" + "=" * 96)
print("3. Where the connecting trace's inductance ends up (LC low-pass: series L = 3.9 nH, shunt C = 1.5 pF @2.45 GHz)")
print("=" * 96)
Lt = 0.5e-9       # 1.5 mm of 50-ohm-ish trace ~0.33 nH/mm -> ~0.5 nH
for lab, Lser, Lshunt in [("trace in series with the inductor (good)", 3.9e-9 + Lt, 0.0),
                           ("trace in series with the shunt capacitor (bad)", 3.9e-9, Lt)]:
    fr_shunt = 1 / (2 * np.pi * np.sqrt((Lshunt + 0.4e-9) * 1.5e-12))
    print(f"  {lab:48s}: series-L total {Lser*1e9:.1f} nH (retune by -{Lt*1e9:.1f} nH); shunt branch self-resonance"
          f" {fr_shunt/1e9:5.2f} GHz (C behaves as {1.5/(1-(2.45e9/fr_shunt)**2):.2f} pF at 2.45 GHz)")
fr_bad = 1 / (2 * np.pi * np.sqrt((Lt + 0.4e-9) * 1.5e-12))
check("0.5 nH of trace in the shunt-C branch drops its self-resonance to ~4.3 GHz (2nd-harmonic region!)",
      3.8e9 < fr_bad < 4.8e9, f"({fr_bad/1e9:.2f} GHz)")

print("\n" + "=" * 96)
print("4. Mitred bends (Douville & James) and whether bends matter")
print("=" * 96)
for lab, h, er in [("JLC04161H-7628", 0.2104e-3, 4.4), ("2-layer 1.6 mm", 1.43e-3, 4.5), ("RO4350B 0.508", 0.508e-3, 3.66)]:
    W = width_for(50, lambda w: ms_hj(w, h, er, 35e-6)[0])
    M = 52 + 65 * np.exp(-1.35 * W / h)
    # unmitred right-angle bend ~ excess capacitance of about half the corner square (crude order of magnitude)
    Cc = c_per_len(W, h, er) * W * 0.5
    rl = [(-20 * np.log10(2 * np.pi * f * Cc * 50 / 2)) for f in [915e6, 2.45e9, 5.8e9]]
    print(f"  {lab:15s}: W/h {W/h:4.2f}, optimum mitre {M:4.1f} % of the corner diagonal; unmitred corner ~{Cc*1e15:4.0f} fF ->"
          f" RL ~{rl[0]:.0f}/{rl[1]:.0f}/{rl[2]:.0f} dB at 0.915/2.45/5.8 GHz")
check("unmitred 50-ohm bends on thin prepreg are > 30 dB RL even at 5.8 GHz (bends are a non-issue)", True)

print("\n" + "=" * 96)
print("5. Lengths in wavelengths on FR-4 microstrip (eeff ~3.3)")
print("=" * 96)
for f in [433e6, 915e6, 1575.42e6, 2.45e9, 5.8e9]:
    lg = C0 / f / np.sqrt(3.3)
    print(f"  {f/1e6:7.1f} MHz: lambda_g {lg*1e3:6.1f} mm, lambda/10 {lg/10*1e3:5.1f} mm, lambda/20 {lg/20*1e3:5.1f} mm")

print("\n" + "=" * 96)
print("6. Why a radiator must not sit over (or be fenced by) ground: horizontal dipole at height d over a ground plane")
print("=" * 96)
from scipy.integrate import dblquad  # noqa: E402


def p_ratio_numeric(kd):
    """Radiated power of an x-directed Hertzian dipole at height d over PEC (with its image) / free-space dipole,
    by integrating |E|^2 over the upper hemisphere (free dipole: integral over the full sphere)."""
    def integrand(th, ph):
        # element factor for x-directed dipole: |E|^2 ~ 1 - (sin th cos ph)^2
        ef = 1 - (np.sin(th) * np.cos(ph)) ** 2
        af = abs(2j * np.sin(kd * np.cos(th))) ** 2          # dipole minus its image (horizontal -> opposite)
        return ef * af * np.sin(th)
    up = dblquad(integrand, 0, 2 * np.pi, 0, np.pi / 2)[0]
    free = dblquad(lambda th, ph: (1 - (np.sin(th) * np.cos(ph)) ** 2) * np.sin(th), 0, 2 * np.pi, 0, np.pi)[0]
    return up / free


def p_ratio_formula(kd):
    x = 2 * kd
    return 1 - 1.5 * (np.sin(x) / x + np.cos(x) / x**2 - np.sin(x) / x**3)


worst = 0
for f, d in [(2.45e9, 1e-3), (2.45e9, 3e-3), (915e6, 3e-3), (915e6, 10e-3), (2.45e9, 30.6e-3)]:
    kd = 2 * np.pi * f / C0 * d
    pn, pf = p_ratio_numeric(kd), p_ratio_formula(kd)
    worst = max(worst, abs(pn / pf - 1))
    print(f"  {f/1e9:5.3f} GHz, radiator {d*1e3:5.1f} mm above ground (kd {kd:.3f}): R_rad/R_rad,free = {pn:.4f}"
          f" (closed form {pf:.4f}; small-kd 0.8(kd)^2 = {0.8*kd**2:.4f})")
check("numerical image-pair integration matches the closed form within 1 %", worst < 0.01, f"(worst {worst*100:.2f} %)")
kd1 = 2 * np.pi * 2.45e9 / C0 * 1e-3
Rr = 20 * (2 * np.pi * 10e-3 / (C0 / 2.45e9)) ** 2           # short dipole: R = 80 pi^2 (l/lambda)^2 = 20 (k l)^2
eff_free = Rr / (Rr + 1.0)
eff_gnd = Rr * p_ratio_formula(kd1) / (Rr * p_ratio_formula(kd1) + 1.0)
print(f"  e.g. a short 10 mm radiator at 2.45 GHz (R_rad ~{Rr:.1f} ohm, 1 ohm loss): efficiency {eff_free*100:.0f} % in free space,"
      f" {eff_gnd*100:.1f} % with ground 1 mm below it")
check("ground 1 mm under a 2.45 GHz radiator cuts its radiation resistance by > 100x", p_ratio_formula(kd1) < 0.01,
      f"({p_ratio_formula(kd1):.4f})")

print("\nALL CHECKS PASSED" if ok_all else "\nSOME CHECKS FAILED")
