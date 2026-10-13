#!/usr/bin/env python3
"""sim2_openems_array_blindness.py — scan blindness of a printed FR-4 patch array seen in openEMS WITHOUT
Floquet boundaries: the embedded (active) element pattern of the centre element of a finite E-plane row.
W5-S11, gap G-16-01 part G (W2-B5 request). Page: kb/16-simulation-tools/openems-workflow.md.

Why this route: openEMS (v0.37) offers PEC, PMC, MUR and PML boundaries only — no phase-shifted periodic
(Floquet/Bloch) boundary — so the textbook infinite-array unit cell cannot be scanned (checked in the source:
SetBoundaryCond types; a broadside cell between PEC/PMC walls is possible, scanned cells are not). For a
large array the centre element's embedded pattern equals the scan gain of the array divided by N (Hannan),
G_emb(theta) ~ (4 pi A_cell / lambda^2) (1 - |Gamma_a(theta)|^2) cos(theta), so a scan blindness shows up as a
DIP in the embedded pattern at the blind angle. One run (centre port excited, all others 50-ohm loads) gives it.

Model: 1.6 mm FR-4 (er 4.4, lossless here to isolate the surface wave), PEC ground = z-min boundary, substrate
running into PML on x and y (an "infinite" slab), N = 15 probe-fed patches in one row along x (E-plane),
W 15.74 x L 11.75 mm (TL-model design for 5.8 GHz), probe 3.4 mm inside the radiating edge, element spacing
d = 0.586 lambda (30.3 mm, the "+-45 deg grating-lobe limit") and d = 0.5 lambda (25.8 mm) at 5.8 GHz.

PRE-REGISTERED EXPECTATIONS (written 2026-10-13 before any run; addenda only below)
  A1  d = 0.586 lambda: the E-plane embedded pattern of the centre element has a dip >= 3 dB below a smooth
      cos^q(theta) fit of its neighbours within 38-50 deg (Floquet phase-matching estimate 44 deg from
      kb/12-phased-arrays/planar-arrays-element-pattern-coupling.md: sin(theta_b) = lambda/d - beta_TM0/k0,
      beta/k0 = 1.012). A 15-element row is finite and one-dimensional, so the dip is shallower than the
      infinite-array |Gamma_a| -> 1 null.
  A2  d = 0.5 lambda: no dip >= 3 dB within 0-70 deg (estimate 81 deg).
  A3  The H-plane embedded pattern shows no dip in either case (TM0 is phase-matched in the E-plane only).

ADDENDUM 1 (2026-10-13, after the d0586 run): the centre element's S11 minimum sat at 5.16 GHz, 11 % below the
  5.8 GHz TL design, and the E-plane pattern showed only a shallow local minimum (-4.3 dB at 50-55 deg, recovering
  to -2.3 dB at 65 deg; fit residual -1.6 dB at 53 deg) -> A1 MISS. Diagnostic cases added (not pre-registered):
  "single" (one isolated patch, same mesh) and "single_fine"/"d0586_fine" (fine-region cell x 0.5) to separate
  a mesh/model error from array coupling.

Run: ~/opt/openEMS/venv/bin/python tools/verify/sim2_openems_array_blindness.py [d0586] [d05]   (~5-15 min each)
"""
import json
import os
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
from CSXCAD import ContinuousStructure            # noqa: E402
from openEMS import openEMS                        # noqa: E402
from openEMS.physical_constants import C0          # noqa: E402

F0 = 5.8e9
LAM = C0 / F0 * 1e3                                 # mm
H, ER = 1.6, 4.4
WP, LP, FEED = 15.74, 11.75, 3.4
N = 15


def run(tag, d_lam, n_el=N, mf=1.2):
    d = d_lam * LAM
    sim_path = os.path.join(tempfile.gettempdir(), f"rfkb_blind_{tag}")
    FDTD = openEMS(NrTS=200000, EndCriteria=1e-4)
    FDTD.SetGaussExcite(F0, 1.5e9)
    FDTD.SetBoundaryCond(["PML_8", "PML_8", "PML_8", "PML_8", "PEC", "PML_8"])
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(1e-3)
    xs = (np.arange(n_el) - (n_el - 1) / 2) * d
    xb = xs[-1] + d / 2 + 30
    yb = 45.0
    sub = CSX.AddMaterial("FR4", epsilon=ER)
    sub.AddBox([-xb - 20, -yb - 20, 0], [xb + 20, yb + 20, H], priority=0)
    patch = CSX.AddMetal("patch")
    ports = []
    res = C0 / (F0 + 1.5e9) / 1e-3 / 20
    resd = res / np.sqrt(ER)
    for k, x0 in enumerate(xs):
        patch.AddBox([x0 - LP / 2, -WP / 2, H], [x0 + LP / 2, WP / 2, H], priority=10)
        xf = x0 - LP / 2 + FEED
        ports.append(FDTD.AddLumpedPort(k + 1, 50, [xf, 0, 0], [xf, 0, H], "z", 1.0 if k == n_el // 2 else 0,
                                        priority=5))
        mesh.AddLine("x", [x0 - LP / 2 - resd / 6, x0 - LP / 2 + resd / 3, x0 + LP / 2 - resd / 3,
                           x0 + LP / 2 + resd / 6, xf])
    mesh.AddLine("y", [-WP / 2 - resd / 6, -WP / 2 + resd / 3, WP / 2 - resd / 3, WP / 2 + resd / 6, 0.0])
    mesh.AddLine("x", [-xb, xb])
    mesh.AddLine("y", [-yb, yb])
    mesh.AddLine("z", list(np.linspace(0, H, 5)) + [H + 25.0])
    mesh.SmoothMeshLines("x", resd * mf, 1.4)
    mesh.SmoothMeshLines("y", resd * mf, 1.4)
    mesh.SmoothMeshLines("z", res, 1.4)
    nf2ff = FDTD.CreateNF2FFBox()
    n = np.prod([len(mesh.GetLines(a)) for a in "xyz"])
    t0 = time.time()
    FDTD.Run(sim_path, cleanup=True, verbose=0, exact_endcriteria=True)
    dt = time.time() - t0
    f = np.linspace(F0 - 1.0e9, F0 + 1.0e9, 801)
    pc = ports[n_el // 2]
    pc.CalcPort(sim_path, f)
    s11 = 20 * np.log10(np.abs(pc.uf_ref / pc.uf_inc))
    fres = float(f[np.argmin(s11)])
    th = np.arange(-89, 90, 1.0)
    out = dict(tag=tag, d_lam=d_lam, d_mm=d, cells=int(n), time_s=dt, f_s11min=fres, s11min=float(s11.min()))
    for fe in (F0, fres):
        ff = nf2ff.CalcNF2FF(sim_path, fe, th, [0.0, 90.0], center=[0, 0, H])
        e = np.abs(ff.E_norm[0])                     # shape (theta, phi)
        g = 20 * np.log10(e / e.max() + 1e-12)
        out[f"Eplane_{fe/1e9:.3f}"] = g[:, 0].tolist()
        out[f"Hplane_{fe/1e9:.3f}"] = g[:, 1].tolist()
    out["theta"] = th.tolist()
    return out


def dip_analysis(th, g, lo=5, hi=75):
    """Largest negative residual of g (dB) from a smooth cos^q fit over |theta| in [lo, hi] (both sides averaged)."""
    th = np.asarray(th)
    g = np.asarray(g)
    pos = (th >= lo) & (th <= hi)
    gs = 0.5 * (g[pos] + np.interp(-th[pos], th, g))           # symmetrise +-theta
    t = th[pos]
    # robust fit of q: least squares of gs ~ c + 10 q log10(cos t)
    A = np.vstack([np.ones_like(t), 10 * np.log10(np.cos(np.radians(t)))]).T
    w = np.ones_like(t)
    for _ in range(5):                                          # iteratively down-weight dips
        coef, *_ = np.linalg.lstsq(A * w[:, None], gs * w, rcond=None)
        r = gs - A @ coef
        w = np.where(r < -1.0, 0.1, 1.0)
    r = gs - A @ coef
    i = int(np.argmin(r))
    return float(t[i]), float(r[i]), float(coef[1])


def main(args):
    args = args or ["d0586", "d05"]
    for a in args:
        d_lam, n_el, mf = {"d0586": (0.586, N, 1.2), "d05": (0.5, N, 1.2), "single": (0.586, 1, 1.2),
                           "single_fine": (0.586, 1, 0.6), "d0586_fine": (0.586, N, 0.6)}[a]
        r = run(a, d_lam, n_el, mf)
        lam_res = C0 / r["f_s11min"] * 1e3
        lines = [f"array_blindness {a}: d {r['d_mm']:.1f} mm ({d_lam} lambda @ 5.8 GHz), {r['cells']/1e6:.2f} M cells, "
                 f"{r['time_s']:.0f} s; centre element S11 min {r['s11min']:.1f} dB @ {r['f_s11min']/1e9:.3f} GHz"]
        for key in [k for k in r if k.startswith("Eplane") or k.startswith("Hplane")]:
            fe = float(key.split("_")[1]) * 1e9
            tb, depth, q = dip_analysis(r["theta"], r[key])
            est = np.degrees(np.arcsin(min(1.0, C0 / fe * 1e3 / r["d_mm"] - 1.012)))
            lines.append(f"   {key[:6]} at {fe/1e9:.3f} GHz: deepest residual {depth:+.1f} dB at {tb:.0f} deg "
                         f"(cos^q fit q = {q:.2f}); Floquet estimate theta_b = {est:.1f} deg")
        txt = "\n".join(lines)
        print(txt, flush=True)
        with open(os.path.join(HERE, "sim2_openems_results.txt"), "a") as fh:
            for line in lines:
                fh.write(f"[{time.strftime('%Y-%m-%d %H:%M')}] sim2_openems_array_blindness {line}\n")
        with open(os.path.join(HERE, "sim2_openems_results.jsonl"), "a") as fh:
            fh.write(json.dumps({"script": "array_blindness", **r}) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
