#!/usr/bin/env python3
"""ant2_slot_openems.py -- openEMS (FDTD) checks for kb/08-antennas/slot-antennas.md (W5-E2).

Case A (Babinet check): a thin slot, w = 2.45 mm (lambda/50 at 2.45 GHz), length L = 57.0 mm, cut in a
  PEC sheet that runs into the PML on all four sides (emulates an infinite screen); centre-fed by a
  lumped port across the slot. Complementary strip dipole (own MoM, tools/verify/ant2_slot.py) resonates
  at 2.45 GHz with R = 74.9 ohm, so Babinet predicts:
     resonance (X = 0) at 2.45 GHz +-3 %, R_res = eta^2/(4*74.9) = 474 ohm +-10 %,
     and X > 0 (inductive) below resonance, X < 0 above (opposite to the dipole).
Case B (PCB slot): the same slot in the copper of an 'infinite' 1.6 mm FR-4 board (er 4.4, tan d 0.02;
  substrate also into the PML).  Pre-registered expectation: resonance falls by a factor between
  sqrt((er+1)/2) = 1.64 (thick-substrate limit) and ~1.2 (thin board, most field in air); R_res lower
  than case A (the dielectric side loads the slot).
Case C (realistic board): the same PCB slot on a finite 90 x 60 mm FR-4 board (slot along the 90 mm side).
  [first run had the board 60 mm along the slot, leaving 1.5 mm of copper at each slot end -- discarded] Expectation: resonance
  within a few % of case B; bidirectional pattern, D ~ 3-5 dBi; radiation efficiency 70-95 % (field mostly
  in air, low stored energy in FR-4).
Case D: slot shortened to 43.5 mm (scaled by 1.858/2.45 from case B) on the 90 x 60 board -> resonance
  near 2.45 GHz expected (+-4 %).
Case E: case D fed at x = L/4 from the centre -> sinusoidal-slot-voltage model predicts R_res ~ R_c cos^2(pi/4)
  = 0.5 R_c(D) at the same resonant frequency.
Case F: open-ended quarter-wave "notch" slot, 57 x 2 mm, cut in from the edge of an 80 x 100 mm FR-4 board,
  50-ohm feed 4 mm from the closed end (915 MHz candidate for a flight-computer board edge). Expectation:
  resonance near 0.70 x lambda0/4 -> ~0.92 GHz +-10 %, match within VSWR 2 somewhere in 0.8-1.05 GHz.
  (Pass e.g. "F57,4" = length 57 mm, feed 4 mm from the closed end.)
Run: ~/opt/openEMS/venv/bin/python tools/verify/ant2_slot_openems.py [A|B|C ...]   (~2-6 min per case)
Results are appended to tools/verify/ant2_slot_openems_results.txt.
"""
import os
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
from CSXCAD import ContinuousStructure            # noqa: E402
from openEMS import openEMS                        # noqa: E402
from openEMS.physical_constants import C0, EPS0    # noqa: E402

W_SLOT, L_SLOT = 2.45, 57.0          # mm
H, ER, TAND = 1.6, 4.4, 0.02
F0, FC = 2.2e9, 1.4e9                # excitation 0.8-3.6 GHz


def run(case):
    L_SLOT = 43.5 if case in ("D", "E") else 57.0
    XP = L_SLOT / 4 if case == "E" else 0.0          # feed offset from the slot centre
    sim_path = os.path.join(tempfile.gettempdir(), f"rfkb_slot_{case}")
    FDTD = openEMS(NrTS=120000, EndCriteria=1e-4)
    FDTD.SetGaussExcite(F0, FC)
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(1e-3)
    lam_min = C0 / (F0 + FC) / 1e-3
    res_air = lam_min / 20
    if case in ("A", "B"):
        X, Y, Z = 360.0, 360.0, 240.0              # domain; sheet and substrate run into the PML
        FDTD.SetBoundaryCond(["PML_8"] * 6)
        sx, sy = X / 2 + 10, Y / 2 + 10
    else:
        X, Y, Z = 90 + 2 * 60.0, 60 + 2 * 60.0, 1.6 + 2 * 60.0
        FDTD.SetBoundaryCond(["MUR"] * 6)
        sx, sy = 45.0, 30.0                         # finite 90 x 60 mm board, slot along the long side
    mesh.AddLine("x", [-X / 2, X / 2])
    mesh.AddLine("y", [-Y / 2, Y / 2])
    mesh.AddLine("z", [-Z / 2, Z / 2])
    cu = CSX.AddMetal("sheet")
    # sheet at z = 0 with a rectangular hole: build from four boxes around the slot
    xs, ys = L_SLOT / 2, W_SLOT / 2
    cu.AddBox([-sx, ys, 0], [sx, sy, 0], priority=10)
    cu.AddBox([-sx, -sy, 0], [sx, -ys, 0], priority=10)
    cu.AddBox([xs, -ys, 0], [sx, ys, 0], priority=10)
    cu.AddBox([-sx, -ys, 0], [-xs, ys, 0], priority=10)
    if case in ("B", "C", "D", "E"):
        kappa = 2 * np.pi * 2.0e9 * EPS0 * ER * TAND
        sub = CSX.AddMaterial("FR4", epsilon=ER, kappa=kappa)
        sub.AddBox([-sx, -sy, -H], [sx, sy, 0], priority=0)
        mesh.AddLine("z", np.linspace(-H, 0, 5))
    # fine mesh around the slot (thirds rule on the slot edges)
    d = 0.6
    mesh.AddLine("y", [-ys - d / 3, -ys + 2 * d / 3, 0, ys - 2 * d / 3, ys + d / 3])
    mesh.AddLine("x", [-xs - d / 3, -xs + 2 * d / 3, xs - 2 * d / 3, xs + d / 3])
    mesh.AddLine("x", np.arange(-xs + 2, xs - 1.9, 1.0))
    mesh.AddLine("z", [-0.6, 0, 0.6])
    if case in ("C", "D", "E"):
        mesh.AddLine("x", [-sx - 0.2, -sx + 0.4, sx - 0.4, sx + 0.2])
        mesh.AddLine("y", [-sy - 0.2, -sy + 0.4, sy - 0.4, sy + 0.2])
    port = FDTD.AddLumpedPort(1, 300, [XP - 0.5, -ys, 0], [XP + 0.5, ys, 0], "y", 1.0, priority=5)
    mesh.AddLine("x", [XP - 0.5, XP + 0.5])
    mesh.SmoothMeshLines("all", res_air, 1.35)
    nf2ff = FDTD.CreateNF2FFBox() if case in ("C", "D") else None
    ncell = len(mesh.GetLines("x")) * len(mesh.GetLines("y")) * len(mesh.GetLines("z"))
    t0 = time.time()
    FDTD.Run(sim_path, cleanup=True, verbose=0)
    dt = time.time() - t0
    f = np.linspace(1.0e9, 3.4e9, 2401)
    port.CalcPort(sim_path, f)
    zin = port.uf_tot / port.if_tot
    # resonance = zero crossing of X from + to - (slot: inductive below, capacitive above)
    X_ = zin.imag
    idx = np.where((X_[:-1] > 0) & (X_[1:] <= 0))[0]
    out = dict(case=case, cells=ncell, time=dt, f=f, zin=zin, L=L_SLOT, xp=XP)
    if idx.size:
        i = idx[np.argmax(zin.real[idx])]
        fr = f[i] - X_[i] * (f[i + 1] - f[i]) / (X_[i + 1] - X_[i])
        out["fres"] = fr
        out["Rres"] = float(np.interp(fr, f, zin.real))
    ipk = int(np.argmax(zin.real))
    out["fRmax"], out["Rmax"] = f[ipk], zin.real[ipk]
    if nf2ff is not None and "fres" in out:
        ff = nf2ff.CalcNF2FF(sim_path, out["fres"], np.arange(0, 181, 2.0), [0.0, 90.0])
        p_acc = float(np.interp(out["fres"], f, port.P_acc))
        out["D"] = 10 * np.log10(float(np.atleast_1d(ff.Dmax)[0]))
        out["eff"] = float(np.atleast_1d(ff.Prad)[0]) / p_acc
    return out


def run_notch(L=57.0, xf=4.0, w=2.0, bx=80.0, by=100.0, tag="F"):
    """Case F: open-ended (quarter-wave 'notch') slot cut inward from the edge of a small FR-4 board,
    fed across the slot xf mm from its closed end by a 50-ohm lumped port (915 MHz band)."""
    sim_path = os.path.join(tempfile.gettempdir(), f"rfkb_slot_{tag}")
    f0, fc = 1.0e9, 0.5e9
    FDTD = openEMS(NrTS=150000, EndCriteria=1e-4)
    FDTD.SetGaussExcite(f0, fc)
    FDTD.SetBoundaryCond(["MUR"] * 6)
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(1e-3)
    res_air = C0 / (f0 + fc) / 1e-3 / 20
    m = 110.0
    mesh.AddLine("x", [-bx / 2 - m, bx / 2 + m])
    mesh.AddLine("y", [-by / 2 - m, by / 2 + m])
    mesh.AddLine("z", [-m, m])
    sx, sy = bx / 2, by / 2
    x_closed = sx - L
    ys = w / 2
    cu = CSX.AddMetal("sheet")
    cu.AddBox([-sx, ys, 0], [sx, sy, 0], priority=10)
    cu.AddBox([-sx, -sy, 0], [sx, -ys, 0], priority=10)
    cu.AddBox([-sx, -ys, 0], [x_closed, ys, 0], priority=10)
    kappa = 2 * np.pi * 0.915e9 * EPS0 * ER * TAND
    sub = CSX.AddMaterial("FR4", epsilon=ER, kappa=kappa)
    sub.AddBox([-sx, -sy, -H], [sx, sy, 0], priority=0)
    mesh.AddLine("z", np.linspace(-H, 0, 5))
    d = 0.6
    mesh.AddLine("y", [-ys - d / 3, -ys + 2 * d / 3, 0, ys - 2 * d / 3, ys + d / 3])
    mesh.AddLine("x", [x_closed - d / 3, x_closed + 2 * d / 3])
    mesh.AddLine("x", np.arange(x_closed + 2, sx, 1.5))
    mesh.AddLine("z", [-0.6, 0, 0.6])
    mesh.AddLine("x", [-sx - 0.2, -sx + 0.4, sx - 0.4, sx + 0.2])
    mesh.AddLine("y", [-sy - 0.2, -sy + 0.4, sy - 0.4, sy + 0.2])
    xp = x_closed + xf
    port = FDTD.AddLumpedPort(1, 50, [xp - 0.5, -ys, 0], [xp + 0.5, ys, 0], "y", 1.0, priority=5)
    mesh.AddLine("x", [xp - 0.5, xp + 0.5])
    mesh.SmoothMeshLines("all", res_air, 1.35)
    nf2ff = FDTD.CreateNF2FFBox()
    ncell = len(mesh.GetLines("x")) * len(mesh.GetLines("y")) * len(mesh.GetLines("z"))
    t0 = time.time()
    FDTD.Run(sim_path, cleanup=True, verbose=0)
    dt = time.time() - t0
    f = np.linspace(0.6e9, 1.4e9, 1601)
    port.CalcPort(sim_path, f)
    zin = port.uf_tot / port.if_tot
    s11 = (zin - 50) / (zin + 50)
    i = int(np.argmin(np.abs(s11)))
    band = f[20 * np.log10(np.abs(s11)) <= -9.54]
    ff = nf2ff.CalcNF2FF(sim_path, f[i], np.arange(0, 181, 2.0), [0.0, 90.0])
    p_acc = float(np.interp(f[i], f, port.P_acc))
    D = 10 * np.log10(float(np.atleast_1d(ff.Dmax)[0]))
    eff = float(np.atleast_1d(ff.Prad)[0]) / p_acc
    j915 = int(np.argmin(np.abs(f - 0.915e9)))
    s = (f"case {tag} (open-ended notch slot {L} x {w} mm from the edge of a {bx:.0f} x {by:.0f} mm FR-4 board, "
         f"50-ohm feed {xf} mm from the closed end): {ncell} cells, {dt:.0f} s; best match {f[i]/1e9:.4f} GHz, "
         f"S11 {20*np.log10(abs(s11[i])):.1f} dB, Z {zin[i].real:.1f}{zin[i].imag:+.1f}j; "
         f"VSWR-2 band {band.min()/1e9 if band.size else 0:.3f}-{band.max()/1e9 if band.size else 0:.3f} GHz; "
         f"D {D:.2f} dBi, e_rad {100*eff:.1f} %; Z(915 MHz) {zin[j915].real:.1f}{zin[j915].imag:+.1f}j; "
         f"L/(lambda0/4) at best match = {L/(C0/f[i]*1e3/4):.3f}")
    return s


def main():
    cases = sys.argv[1:] or ["A", "B", "C", "D", "E"]
    lines = []
    for c in cases:
        if c.startswith("F"):
            s = run_notch(*[float(v) for v in c[1:].split(",")] if len(c) > 1 else [])
            print(s, flush=True)
            lines.append(s)
            continue
        r = run(c)
        s = f"case {c} (slot {r['L']} x {W_SLOT} mm, feed offset {r['xp']:.2f} mm): {r['cells']} cells, {r['time']:.0f} s; "
        if "fres" in r:
            s += (f"X=0 (ind->cap) at {r['fres']/1e9:.4f} GHz (L/(lambda/2) = {r['L']/(C0/r['fres']*1e3/2):.3f}), "
                  f"R there = {r['Rres']:.0f} ohm; ")
        s += f"R max {r['Rmax']:.0f} ohm at {r['fRmax']/1e9:.3f} GHz"
        if "D" in r:
            s += f"; D = {r['D']:.2f} dBi, radiation efficiency = {100*r['eff']:.1f} %"
        for fr in (0.9, 0.95, 1.0, 1.05, 1.1):
            ff = r.get("fres", 2.45e9) * fr
            z = complex(np.interp(ff, r["f"], r["zin"].real), np.interp(ff, r["f"], r["zin"].imag))
            s += f"\n    f = {ff/1e9:.3f} GHz: Z = {z.real:6.1f}{z.imag:+7.1f}j ohm"
        print(s, flush=True)
        lines.append(s)
    with open(os.path.join(HERE, "ant2_slot_openems_results.txt"), "a") as fh:
        fh.write(f"\n=== ant2_slot_openems.py {time.strftime('%Y-%m-%d %H:%M')} ===\n"
                 + "\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
