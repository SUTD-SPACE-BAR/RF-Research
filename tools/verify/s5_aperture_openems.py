#!/usr/bin/env python3
"""
s5_aperture_openems.py — openEMS FDTD of an open-ended WR-90 guide in a square PEC flange at 10 GHz,
to test the equivalence-principle aperture model of s5_aperture_equivalence.py §3 (task W5-S5, G-02-01).

Model: WR-90 (22.86 x 10.16 mm) PEC guide along z, fed by a TE10 waveguide port, ending at z = 0 in a
square PEC flange (side F, 1 mm thick); radiation into air; PML_8 on all faces (the guide runs into
the -z PML, which absorbs the backward TE10 wave). NF2FF box without its -z face (the guide passes
through it), so back radiation behind the flange is ignored.

Pre-registered (written 2026-10-13, before the first run; also in s5_aperture_equivalence.py §6):
  * H-plane pattern within 1.0 dB of the equivalence model for |theta| <= 60 deg,
  * E-plane within 2.0 dB for |theta| <= 45 deg (the E-plane field grazes the flange, so the finite
    flange edges diffract strongly there),
  * Dmax within 1.0 dB of the hemisphere-integrated equivalence value (6.31 dBi).
  * Two flange sizes (F = 90 and 150 mm); differences between them show the finite-flange effect.
Added after the first three runs failed the H-plane/Dmax tolerances (2026-10-13): F = 240 mm, and runs
with a CLOSED NF2FF box whose -z face lies behind the flange ("closed"), to separate the finite-flange
effect from the open-box (missing back face) truncation. Not pre-registered; reported as exploration.

Run: ~/opt/openEMS/venv/bin/python tools/verify/s5_aperture_openems.py   (a few minutes)
Results appended (one JSON line per run) to tools/verify/s5_aperture_openems_results.txt.
"""
import json
import os
import sys
import tempfile
import time

import numpy as np
from CSXCAD import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import C0

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "s5_aperture_openems_results.txt")
unit = 1e-3
a, b, t = 22.86, 10.16, 1.0
f0, fmin, fmax = 10e9, 8e9, 12e9


def run(F, res_div=20, label="", back_face=False):
    sim = os.path.join(tempfile.gettempdir(), f"s5_wr90_F{int(F)}_r{res_div}")
    FDTD = openEMS(EndCriteria=1e-5)
    FDTD.SetGaussExcite(0.5 * (fmin + fmax), 0.5 * (fmax - fmin))
    FDTD.SetBoundaryCond(["PML_8"] * 6)
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(unit)
    res = C0 / fmax / unit / res_div
    lam0 = C0 / f0 / unit
    pml = 8 * res + 1
    xmax = F / 2 + lam0 / 2 + pml
    zmin = -(25 + pml)
    zmax = lam0 / 2 + pml
    metal = CSX.AddMetal("pec")
    air = CSX.AddMaterial("air", epsilon=1.0)
    # guide outer block + flange, then carve the air interior with higher priority
    metal.AddBox(priority=10, start=[-a / 2 - t, -b / 2 - t, zmin], stop=[a / 2 + t, b / 2 + t, 0])
    metal.AddBox(priority=10, start=[-F / 2, -F / 2, -t], stop=[F / 2, F / 2, 0])
    air.AddBox(priority=20, start=[-a / 2, -b / 2, zmin], stop=[a / 2, b / 2, 0])
    mesh.AddLine("x", [-xmax, -F / 2, -a / 2 - t, -a / 2, 0, a / 2, a / 2 + t, F / 2, xmax])
    mesh.AddLine("y", [-xmax, -F / 2, -b / 2 - t, -b / 2, 0, b / 2, b / 2 + t, F / 2, xmax])
    zp = -18.0
    mesh.AddLine("z", [zmin, zp - 2 * res, zp, -t, 0, zmax])
    port = FDTD.AddRectWaveGuidePort(0, [-a / 2, -b / 2, zp - 2 * res], [a / 2, b / 2, zp], "z",
                                     a * unit, b * unit, "TE10", 1)
    mesh.SmoothMeshLines("all", res, 1.4)
    if back_face:
        # closed box whose -z face sits behind the flange (z = -6 mm); the feed guide pierces it
        lines = [mesh.GetLines(d) for d in "xyz"]
        st = [lines[0][9], lines[1][9], -6.0]
        sp = [lines[0][-10], lines[1][-10], lines[2][-10]]
        nf2ff = FDTD.CreateNF2FFBox(start=st, stop=sp)
    else:
        nf2ff = FDTD.CreateNF2FFBox(directions=[1, 1, 1, 1, 0, 1])
    ncell = len(mesh.GetLines("x")) * len(mesh.GetLines("y")) * len(mesh.GetLines("z"))
    print(f"[{label}] F = {F} mm, res = lam/{res_div} @ 12 GHz ({res:.2f} mm), cells = {ncell/1e6:.2f} M", flush=True)
    t0 = time.time()
    FDTD.Run(sim, cleanup=True, verbose=0)
    wall = time.time() - t0
    freq = np.linspace(fmin, fmax, 81)
    port.CalcPort(sim, freq)
    s11 = port.uf_ref / port.uf_inc
    s11_10 = 20 * np.log10(np.abs(np.interp(f0, freq, np.abs(s11))))
    theta = np.arange(-90.0, 90.1, 1.0)
    ff = nf2ff.CalcNF2FF(sim, f0, theta, [0.0, 90.0])
    Dmax = 10 * np.log10(ff.Dmax[0])
    En = 20 * np.log10(ff.E_norm[0] / np.max(ff.E_norm[0])) + Dmax
    # openEMS phi = 0 is the xz-plane = H-plane here (E is along y); phi = 90 is the E-plane
    rec = dict(label=label, flange_mm=F, res_div=res_div, back_face=back_face, cells=ncell, wall_s=round(wall, 1),
               Dmax_dBi=float(Dmax), S11_dB_10GHz=float(s11_10), theta_deg=theta.tolist(),
               H_plane_dBi=En[:, 0].tolist(), E_plane_dBi=En[:, 1].tolist(),
               date=time.strftime("%Y-%m-%d %H:%M"))
    with open(OUT, "a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(f"[{label}] done in {wall:.0f} s: Dmax {Dmax:.2f} dBi, |S11(10 GHz)| {s11_10:.1f} dB", flush=True)
    return rec


if __name__ == "__main__":
    which = sys.argv[1:] or ["F90", "F150", "F90fine"]
    if "F90" in which:
        run(90.0, 20, "F90")
    if "F150" in which:
        run(150.0, 20, "F150")
    if "F90fine" in which:
        run(90.0, 30, "F90fine")
    if "F240" in which:
        run(240.0, 20, "F240")
    for F in (90, 150, 240):
        if f"F{F}closed" in which:
            run(float(F), 20, f"F{F}closed", back_face=True)
