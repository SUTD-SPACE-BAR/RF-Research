#!/usr/bin/env python3
"""sim_openems_patch.py — openEMS model of the 2.45 GHz FR-4 probe-fed patch from
kb/08-antennas/patch-antennas.md (Example 1), used by kb/16-simulation-tools/openems-workflow.md.

Geometry (mm): patch L = 28.81 (resonant, x) x W = 37.23 (y) on FR-4 er = 4.4, tan(delta) = 0.02, h = 1.6,
PEC patch and ground (zero thickness), ground/substrate 80 x 80 (finite!). Probe feed = 50 ohm lumped port
from ground to patch at 8.3 mm inside the radiating edge (the cos^2 50-ohm point of the TL model).

Pre-registered expectation (TL/cavity model values from tools/verify/ant_patch.py, written before running):
  * resonance 2.45 GHz within +-3 % (TL model ignores the probe, the finite ground and fringing details)
  * VSWR-2 bandwidth ~2.6 %; Zin near 50 ohm at resonance (probe position from cos^2 law, +-30 %)
  * directivity ~6.1 dBi (two-slot model, infinite ground; finite 80 mm ground may raise/lower ~0.5-1 dB)
  * radiation efficiency ~40 % (dominated by tan(delta) = 0.02) -> realised gain ~2 dBi
  * mesh refinement (three levels, max cell ~3.1 -> 2.1 -> 1.4 mm; 4 -> 6 -> 8 substrate cells) moves f_res < 1 %

Run:  ~/opt/openEMS/venv/bin/python tools/verify/sim_openems_patch.py     (~2-10 min on an M-series Mac)
Results are appended to tools/verify/sim_openems_results.txt.
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

L_PATCH, W_PATCH = 28.81, 37.23     # mm
H, ER, TAND = 1.6, 4.4, 0.02
GND = 80.0                          # mm, square ground/substrate
F0, FC = 2.45e9, 1.0e9              # Gaussian centre / 20 dB corner
FEED_X = -(L_PATCH / 2 - 8.3)       # mm from the patch centre


def run(res_div=20, sub_cells=4, tag="coarse"):
    sim_path = os.path.join(tempfile.gettempdir(), f"rfkb_patch_{tag}")
    FDTD = openEMS(NrTS=60000, EndCriteria=1e-4)
    FDTD.SetGaussExcite(F0, FC)
    FDTD.SetBoundaryCond(["MUR"] * 6)
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(1e-3)
    res = C0 / (F0 + FC) / 1e-3 / res_div           # air resolution [mm]
    box = np.array([GND + 2 * 40, GND + 2 * 40, 90])   # >= lambda/4 (31 mm at 2.45 GHz) air margin
    mesh.AddLine("x", [-box[0] / 2, box[0] / 2])
    mesh.AddLine("y", [-box[1] / 2, box[1] / 2])
    mesh.AddLine("z", [-box[2] / 3, box[2] * 2 / 3])

    kappa = 2 * np.pi * F0 * EPS0 * ER * TAND       # loss tangent represented as conductivity at F0
    sub = CSX.AddMaterial("FR4", epsilon=ER, kappa=kappa)
    sub.AddBox([-GND / 2, -GND / 2, 0], [GND / 2, GND / 2, H], priority=0)
    mesh.AddLine("z", np.linspace(0, H, sub_cells + 1))

    patch = CSX.AddMetal("patch")
    patch.AddBox([-L_PATCH / 2, -W_PATCH / 2, H], [L_PATCH / 2, W_PATCH / 2, H], priority=10)
    FDTD.AddEdges2Grid(dirs="xy", properties=patch, metal_edge_res=res / 2)   # thirds-rule edge lines
    gnd = CSX.AddMetal("gnd")
    gnd.AddBox([-GND / 2, -GND / 2, 0], [GND / 2, GND / 2, 0], priority=10)
    FDTD.AddEdges2Grid(dirs="xy", properties=gnd)

    port = FDTD.AddLumpedPort(1, 50, [FEED_X, 0, 0], [FEED_X, 0, H], "z", 1.0, priority=5, edges2grid="xy")
    # finer mesh inside the dielectric: lambda_d = lambda0/sqrt(er)
    mesh.SmoothMeshLines("all", res / np.sqrt(ER) * 1.5, 1.4)
    nf2ff = FDTD.CreateNF2FFBox()

    n = len(mesh.GetLines("x")) * len(mesh.GetLines("y")) * len(mesh.GetLines("z"))
    t0 = time.time()
    FDTD.Run(sim_path, cleanup=True, verbose=0)
    dt = time.time() - t0

    f = np.linspace(2.0e9, 2.9e9, 901)
    port.CalcPort(sim_path, f)
    s11 = port.uf_ref / port.uf_inc
    zin = port.uf_tot / port.if_tot
    i0 = int(np.argmin(np.abs(s11)))
    fres = f[i0]
    s11db = 20 * np.log10(np.abs(s11))
    band = f[s11db <= -9.54]                        # VSWR <= 2
    bw = (band.max() - band.min()) / fres if band.size else 0.0
    ff = nf2ff.CalcNF2FF(sim_path, fres, np.arange(0, 181, 2.0), [0.0, 90.0], center=[0, 0, 1e-3])
    p_acc = float(np.interp(fres, f, port.P_acc))
    prad = float(np.atleast_1d(ff.Prad)[0])
    dmax = float(np.atleast_1d(ff.Dmax)[0])
    eff = prad / p_acc
    dmax_cell = max(np.max(np.diff(mesh.GetLines(a))) for a in "xyz")
    return dict(tag=tag, cells=n, time=dt, maxcell=dmax_cell, fres=fres, s11min=s11db[i0], zin=zin[i0], bw=bw,
                d_dbi=10 * np.log10(dmax), eff=eff, g_dbi=10 * np.log10(dmax * eff))


def main():
    out = [f"2.45 GHz FR-4 patch {L_PATCH}x{W_PATCH} mm, h {H} mm, er {ER}, tand {TAND}, ground {GND} mm, "
           f"probe {8.3} mm from edge"]
    res = []
    for tag, rd, sc in (("coarse", 20, 4), ("fine", 30, 6), ("finest", 45, 8)):
        r = run(rd, sc, tag)
        res.append(r)
        out.append(f"openEMS {tag} (res_div {rd}: max cell {r['maxcell']:.2f} mm, {sc} substrate cells, "
                   f"{r['cells']} cells, {r['time']:.0f} s): "
                   f"f_res {r['fres']/1e9:.4f} GHz ({100*(r['fres']-2.45e9)/2.45e9:+.2f} % vs TL design), "
                   f"S11min {r['s11min']:.1f} dB, Zin {r['zin'].real:.1f}{r['zin'].imag:+.1f}j ohm, "
                   f"BW(VSWR2) {100*r['bw']:.2f} %, D {r['d_dbi']:.2f} dBi, e_rad {100*r['eff']:.1f} %, "
                   f"G {r['g_dbi']:.2f} dBi")
    fr = [r["fres"] for r in res]
    out.append(f"Mesh convergence: f_res coarse->fine {100*(fr[1]-fr[0])/fr[2]:+.2f} %, fine->finest "
               f"{100*(fr[2]-fr[1])/fr[2]:+.2f} %; D coarse->finest {res[2]['d_dbi']-res[0]['d_dbi']:+.2f} dB "
               f"(frequency grid step 1 MHz = 0.04 %)")
    txt = "\n".join(out)
    print(txt)
    with open(os.path.join(HERE, "sim_openems_results.txt"), "a") as fh:
        fh.write(f"\n=== sim_openems_patch.py {time.strftime('%Y-%m-%d %H:%M')} ===\n{txt}\n")


if __name__ == "__main__":
    main()
