#!/usr/bin/env python3
"""
s5_mushroom_openems.py — openEMS check of the Sievenpiper LC model for a mushroom high-impedance
surface (task W5-S5, gap G-03-01; page kb/03-transmission-lines-matching/periodic-structures-ebg.md).

Unit cell of an infinite mushroom array at normal incidence: square patch (a = 7.71 mm period,
g = 0.386 mm gap, the 5.8 GHz design of s5_bloch_ebg.py §5) on 1.43 mm FR-4 (er 4.5, lossless here),
0.3 mm via to the ground. Side walls: PMC on the x faces and PEC on the y faces (E along y), which
images the cell into an infinite array lit by a normally incident plane wave. A TEM "waveguide" port
(E_y, H_x uniform) sits 25 mm above the surface; a second run with the patch layer replaced by a solid
metal sheet at z = h gives the reference Gamma = -1, so Gamma_surface = -S11 / S11_ref (port offsets cancel).

Pre-registered (2026-10-13, before the first run):
  * zero-reflection-phase frequency within +-10 % of the LC model (5.80 GHz simple, 5.67 GHz with the
    exact grounded-slab impedance);
  * +-90 deg bandwidth within +-30 % of sqrt(L/C)/eta0 = 17.4 %;
  * |Gamma| > 0.98 everywhere (lossless model: tests the port/boundary set-up).

Run: ~/opt/openEMS/venv/bin/python tools/verify/s5_mushroom_openems.py    (~1-3 min)
     add the argument "lossy" for one extra run with FR-4 tan d = 0.02 (exploratory, not pre-registered):
     the |Gamma| dip at resonance shows how much an FR-4 AMC absorbs.
Results appended to tools/verify/s5_mushroom_openems_results.txt (JSON line).
"""
import json
import os
import tempfile
import time

import numpy as np
from CSXCAD import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import C0

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "s5_mushroom_openems_results.txt")
unit = 1e-3
a, g, h, er, rv = 7.71, 0.386, 1.43, 4.5, 0.15
w = a - g
fmin, fmax = 3e9, 9e9


def run(reference=False, res_scale=1.0, tand=0.0):
    tag = "ref" if reference else "mush"
    sim = os.path.join(tempfile.gettempdir(), f"s5_mush_{tag}_{res_scale}_{tand}")
    FDTD = openEMS(EndCriteria=1e-5)
    FDTD.SetGaussExcite(0.5 * (fmin + fmax), 0.5 * (fmax - fmin))
    # x faces PMC (1), y faces PEC (0), z-min PEC (ground), z-max PML
    FDTD.SetBoundaryCond([1, 1, 0, 0, 0, "PML_8"])
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(unit)
    lam_min = C0 / fmax / unit
    res = lam_min / 30 * res_scale
    zp = h + 25.0
    ztop = zp + 12.0 + 8 * res
    kappa = 2 * np.pi * 5.8e9 * 8.8541878188e-12 * er * tand      # loss tangent fixed at 5.8 GHz
    sub = CSX.AddMaterial("fr4", epsilon=er, kappa=kappa)
    sub.AddBox(priority=1, start=[-a / 2, -a / 2, 0], stop=[a / 2, a / 2, h])
    metal = CSX.AddMetal("pec")
    if reference:
        metal.AddBox(priority=10, start=[-a / 2, -a / 2, h], stop=[a / 2, a / 2, h])
    else:
        metal.AddBox(priority=10, start=[-w / 2, -w / 2, h], stop=[w / 2, w / 2, h])
        metal.AddCylinder(priority=10, start=[0, 0, 0], stop=[0, 0, h], radius=rv)
    fine = 0.08 * res_scale
    xl = [-a / 2, a / 2, -w / 2, w / 2, -rv, rv, 0]
    xl += list(np.arange(-w / 2 - g / 2 * 0, -w / 2 + 3 * fine, fine)) + list(np.arange(w / 2 - 3 * fine, w / 2 + 1e-9, fine))
    mesh.AddLine("x", xl)
    mesh.AddLine("y", xl)
    mesh.AddLine("z", list(np.linspace(0, h, 7)) + [zp, zp - 2 * res, ztop])
    mesh.SmoothMeshLines("all", res, 1.3)
    port = FDTD.AddWaveGuidePort(0, [-a / 2, -a / 2, zp], [a / 2, a / 2, zp - 2 * res], "z",
                                 E_func=["0", "1", "0"], H_func=["-1", "0", "0"], kc=0.0, excite=1)
    t0 = time.time()
    FDTD.Run(sim, cleanup=True, verbose=0)
    freq = np.linspace(fmin, fmax, 601)
    port.CalcPort(sim, freq)
    s11 = port.uf_ref / port.uf_inc
    ncell = len(mesh.GetLines("x")) * len(mesh.GetLines("y")) * len(mesh.GetLines("z"))
    print(f"[{tag}] cells {ncell}, {time.time()-t0:.0f} s", flush=True)
    return freq, s11


if __name__ == "__main__":
    import sys
    cases = [(1.0, 0.0), (0.7, 0.0)] if "lossy" not in sys.argv else [(1.0, 0.02)]
    for rs, tand in cases:
        f, sm = run(False, rs, tand)
        _, sr = run(True, rs, tand)
        G = -sm / sr
        ph = np.degrees(np.angle(G))
        # zero crossing of the phase (either sign: the port's inc/ref labelling only conjugates Gamma,
        # which flips the phase sign but not the crossing frequency or the +-90 deg band)
        idx = np.where((np.sign(ph[:-1]) != np.sign(ph[1:])) & (np.abs(ph[:-1]) < 90))[0]
        f0 = (f[idx[0]] - ph[idx[0]] * (f[idx[0] + 1] - f[idx[0]]) / (ph[idx[0] + 1] - ph[idx[0]])) if len(idx) else np.nan
        band = f[np.abs(ph) <= 90]
        # contiguous band around f0
        if np.isfinite(f0):
            i0 = np.argmin(np.abs(f - f0))
            lo = i0
            while lo > 0 and abs(ph[lo - 1]) <= 90:
                lo -= 1
            hi = i0
            while hi < len(f) - 1 and abs(ph[hi + 1]) <= 90:
                hi += 1
            bw = (f[hi] - f[lo]) / f0
        else:
            bw = np.nan
        rec = dict(res_scale=rs, tand=tand, f0_GHz=float(f0 / 1e9), bw_pct=float(bw * 100), min_absG=float(np.min(np.abs(G))),
                   max_absG=float(np.max(np.abs(G))), date=time.strftime("%Y-%m-%d %H:%M"),
                   f_GHz=(f[::10] / 1e9).tolist(), phase_deg=ph[::10].tolist())
        with open(OUT, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        if tand > 0:
            print(f"lossy (tan d {tand} at 5.8 GHz): min |Gamma| {np.min(np.abs(G)):.3f} at {f[np.argmin(np.abs(G))]/1e9:.3f} GHz"
                  f" ({20*np.log10(np.min(np.abs(G))):.1f} dB)")
        print(f"res x{rs}: zero-phase f0 = {f0/1e9:.3f} GHz, +-90 deg BW = {bw*100:.1f} %, |Gamma| {np.min(np.abs(G)):.3f}-{np.max(np.abs(G)):.3f}")
        print(f"   pre-registered: f0 within 10 % of 5.80/5.67 GHz -> {'PASS' if 0.9*5.67 <= f0/1e9 <= 1.1*5.80 else 'FAIL'};"
              f" BW within 30 % of 17.4 % -> {'PASS' if 0.7*17.4 <= bw*100 <= 1.3*17.4 else 'FAIL'};"
              f" |Gamma| > 0.98 -> {'PASS' if np.min(np.abs(G)) > 0.98 else 'FAIL'}")
