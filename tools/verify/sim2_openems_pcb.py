#!/usr/bin/env python3
"""sim2_openems_pcb.py — openEMS models of flight-computer PCB features that the KB gave only as
"representative" numbers. W5-S11, gap G-16-01 (parts B-D). Page: kb/16-simulation-tools/openems-workflow.md.

B  ifa_*   915 MHz printed inverted-F antenna at the end of a 100 x 40 mm, 1.6 mm FR-4 board (er 4.5,
           tan d 0.02; top-layer ground pour 80 x 40 mm; 1 mm traces; arm path = 9 mm shorting leg, 36 mm along
           the board end, 9 mm up the long edge, then back along the far edge as needed), free and inside a
           fibreglass body tube (er 4.7, tan d 0.02, inner radius 50 mm, wall 3 mm, axis along the board).
           Assumed geometry — the team's boards use modules with external antennas; this is the "could we put
           the antenna on the board" case.
C  slot_*  50-ohm microstrip (W 2.691 mm, h 1.43 mm, er 4.5 = JLC 2-layer core) crossing a 1 mm wide slot in
           its ground plane, slot length 0 (reference) / 10 / 20 / 40 / 60 mm; MSL ports; air above and below.
D  pad_*   SMA edge-launch signal pad 1.3 x 3.0 mm on JLC04161H-7628 (L1-L2 prepreg 0.2104 mm er 4.4;
           L2-L3 core 1.065 mm er 4.55), 50-ohm feed 0.403 mm (t = 0), pad as a section between two 50-ohm
           lines (the connector taken as a matched continuation), L2 intact vs L2 voided 0.4 mm beyond the
           pad (L3 solid, four L2-L3 stitching vias around the void).

PRE-REGISTERED EXPECTATIONS (written 2026-10-13 before any run; addenda only below)
  I0  (design step, not a test) a 3-length sweep on mesh 1 locates the arm length for 915 MHz.
  I1  tuned free-board IFA: R at resonance 10-60 ohm; VSWR-2 bandwidth (re 50 ohm, only if S11 < -10 dB)
      1.5-6 %; radiation efficiency 50-85 %; directivity 1.8-3.0 dBi.
  I2  in the tube the resonance moves DOWN by 0.8-3 % (central -1.5 %): the arm is ~32 mm from the wall,
      closer than the nose-cone whip (50 mm, -1.2 % in sim2_openems_nosecone.py).
  I3  the tube shift changes by < 0.3 percentage points between mesh 2 and mesh 3.
  S1  slot: series-inductance behaviour at low frequency with L = Z_slot l /(4 v) (13/grounding-and-return-
      paths), v = c/sqrt((er+1)/2); fitted Z_slot within 50-150 ohm (the page assumes 100 ohm).
  S2  slot resonance (|S21| minimum) at l = lambda_slot/2, lambda_slot = c/(f sqrt((er+1)/2)):
      60 mm -> 1.51 GHz, 40 mm -> 2.26 GHz (+-15 %); 10/20 mm: no resonance below 3 GHz.
  S3  |S21| at 915 MHz: 10 mm slot > -0.3 dB, 60 mm slot < -3 dB.
  P1  pad, L2 intact: RL 10-14 dB at 2.45 GHz, 5-8 dB at 5.8 GHz (1-D section model in tools/verify/pcb_launch.py:
      12 and 6 dB; 3-D fringing adds capacitance -> slightly worse).
  P2  pad, L2 voided: RL 17-25 dB at 2.45 GHz, 11-17 dB at 5.8 GHz (1-D model: 21 / 14 dB).
  P3  mesh refinement changes RL at 2.45 GHz by < 1 dB (pad) and the slot resonance by < 2 %.

ADDENDUM 1 (2026-10-13): the first pad series put the MSL feed (1.2 mm) and measurement plane (4 mm) inside the
  8-cell PML (~5.4 mm) — the port-in-PML fault — and gave mesh-inconsistent RL (solid 2.45 GHz: 13.3, 10.5, 10.8 dB;
  void m1 21.6-22.4 dB). Those rows in the results file are superseded. Fixed: 50 mm line, feed 9 mm, plane 14 mm in.
  Void cases also need PML y-walls and a bounded NrTS (a static field stays between L2 and L3).
  IFA: the 3-length sweep fell short (75 mm -> 1037 MHz); a 5th path segment and ifa_sweep2 (82/87/92 mm) were added
  (design step I0); 88 mm tuned to 914.9 MHz. NF2FF switched to a full 5 x 10 deg sphere for the IFA.

Run: ~/opt/openEMS/venv/bin/python tools/verify/sim2_openems_pcb.py <case> [...]   e.g. ifa_sweep, ifa,
     slot, pad   (each group 2-20 min). Results append to tools/verify/sim2_openems_results.txt/.jsonl.
"""
import json
import os
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from CSXCAD import ContinuousStructure            # noqa: E402
from openEMS import openEMS                        # noqa: E402
from openEMS.physical_constants import C0, EPS0    # noqa: E402
from sim2_openems_nosecone import fill_lines       # noqa: E402

LOG = []


def log(s, rec=None):
    print(s, flush=True)
    with open(os.path.join(HERE, "sim2_openems_results.txt"), "a") as fh:
        fh.write(f"[{time.strftime('%Y-%m-%d %H:%M')}] sim2_openems_pcb {s}\n")
    if rec is not None:
        with open(os.path.join(HERE, "sim2_openems_results.jsonl"), "a") as fh:
            fh.write(json.dumps({"script": "pcb", **rec}, default=lambda o: str(o)) + "\n")


# ============================================================== B. IFA
IFA_MESH = {1: 0.7, 2: 0.5, 3: 0.35}          # antenna-region cell (mm)
TUBE_MESH = {1: 2.0, 2: 1.5, 3: 1.0}          # tube-wall region cell (mm)


def ifa_path(l_tot, x_g=30.0, hs=9.0, w=1.0):
    """Boxes (x0,y0,x1,y1) of the 1-mm IFA trace following the fixed path; total centre-line length l_tot."""
    boxes = []
    rem = l_tot
    xa = x_g + hs                               # arm centre-line x = 39 - 0.5
    # shorting leg (x_g .. xa) at y = -17.5
    seg = min(rem, hs)
    boxes.append((x_g, -18.0, x_g + seg, -17.0)); rem -= seg
    if rem > 0:                                 # arm along +y at x = xa-1..xa
        seg = min(rem, 36.0)
        boxes.append((xa - 1, -18.0, xa, -18.0 + seg + 1)); rem -= seg
    if rem > 0:                                 # up the long edge along +x at y = 17..18
        seg = min(rem, 9.0)
        boxes.append((xa - 1, 17.0, xa + seg, 18.0)); rem -= seg
    if rem > 0:                                 # back along -y at x = 47..48 (to y = -16 at most)
        seg = min(rem, 33.0)
        boxes.append((xa + 8, 18.0 - seg - 1, xa + 9, 18.0)); rem -= seg
    if rem > 0:                                 # added 2026-10-13: back along -x at y = -16..-15 (x 47 -> 42)
        seg = min(rem, 5.0)
        boxes.append((xa + 9 - seg - 1, -16.0, xa + 9, -15.0)); rem -= seg
    if rem > 1e-9:
        raise ValueError("arm too long for the clearance area")
    return boxes


def ifa_run(name, l_tot, tube=False, m=2, f0=0.95e9, fc=0.45e9):
    sim_path = os.path.join(tempfile.gettempdir(), f"rfkb_ifa_{name}")
    H, ER, TD = 1.6, 4.5, 0.02
    res_air = C0 / (f0 + fc) / 1e-3 / 20
    margin = 100.0
    FDTD = openEMS(NrTS=200000, EndCriteria=1e-4)
    FDTD.SetGaussExcite(f0, fc)
    FDTD.SetBoundaryCond([os.environ.get("RFKB_BC", "MUR")] * 6)    # RFKB_BC=PML_8: boundary diagnostic
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(1e-3)
    fr4 = CSX.AddMaterial("FR4", epsilon=ER, kappa=2 * np.pi * f0 * EPS0 * ER * TD)
    fr4.AddBox([-50, -20, 0], [50, 20, H], priority=0)
    cu = CSX.AddMetal("copper")
    cu.AddBox([-50, -20, H], [30, 20, H], priority=10)                     # ground pour
    for (x0, y0, x1, y1) in ifa_path(l_tot):
        cu.AddBox([x0, y0, H], [x1, y1, H], priority=10)
    cu.AddBox([31, -12, H], [39, -11, H], priority=10)                     # feed leg to the arm
    port = FDTD.AddLumpedPort(1, 50, [30, -12, H], [31, -11, H], "x", 1.0, priority=5)
    if tube:
        gl = CSX.AddMaterial("fibreglass", epsilon=4.7, kappa=2 * np.pi * f0 * EPS0 * 4.7 * 0.02)
        gl.AddCylindricalShell([-150, 0, H / 2], [150, 0, H / 2], 51.5, 3.0, priority=1)
    ra, rt = IFA_MESH[m], TUBE_MESH[m]
    # x: antenna region fine, board 2 mm
    xs = [29.0, 30, 31, 39 - 1, 39, 42, 47, 48, 50, 50.5]      # antenna region only (fixed 2026-10-13: the first
    mesh.AddLine("x", fill_lines(xs, ra))                  # version also filled the board at ra -> 0.017 mm slivers)
    mesh.AddLine("x", fill_lines([-50, 29.0], 2.0))
    mesh.AddLine("x", [-150, 150])
    ys = [-20, -18, -17, -16, -15, -12, -11, 17, 18, 20]
    mesh.AddLine("y", fill_lines(ys, ra))
    mesh.AddLine("y", fill_lines([-56, -50, -20], rt))
    mesh.AddLine("y", fill_lines([20, 50, 56], rt))
    mesh.AddLine("y", [-50 - margin - 5, 50 + margin + 5])
    zs = list(np.linspace(0, H, 5))
    mesh.AddLine("z", zs)
    mesh.AddLine("z", fill_lines([-56 + H / 2, -50 + H / 2, -3], rt))
    mesh.AddLine("z", fill_lines([H + 3, 50 + H / 2, 56 + H / 2], rt))
    mesh.AddLine("z", [-155, 155])
    for ax in "xyz":
        mesh.SmoothMeshLines(ax, res_air, 1.4)
    nf2ff = FDTD.CreateNF2FFBox()
    n = np.prod([len(mesh.GetLines(a)) for a in "xyz"])
    t0 = time.time()
    FDTD.Run(sim_path, cleanup=True, verbose=0, exact_endcriteria=True)
    dt = time.time() - t0
    f = np.linspace(f0 - 0.9 * fc, f0 + 0.9 * fc, 3001)
    port.CalcPort(sim_path, f)
    s11 = port.uf_ref / port.uf_inc
    zin = port.uf_tot / port.if_tot
    s11db = 20 * np.log10(np.abs(s11))
    i = int(np.argmin(s11db))
    # resonance: R maximum? use X = 0 crossing nearest the S11 minimum
    x = zin.imag
    idx = np.where(np.sign(x[:-1]) != np.sign(x[1:]))[0]
    fres = float(f[i])
    if idx.size:
        k = idx[np.argmin(np.abs(f[idx] - f[i]))]
        fres = float(f[k] - x[k] * (f[k + 1] - f[k]) / (x[k + 1] - x[k]))
    band = f[s11db <= -9.54]
    bw = float((band.max() - band.min()) / f[i]) if band.size and s11db[i] < -10 else float("nan")
    # full sphere (5 x 10 deg) so that Dmax is not limited to two cuts (Prad is the box flux either way)
    ff = nf2ff.CalcNF2FF(sim_path, f[i], np.arange(0, 181, 5.0), np.arange(0, 360, 10.0), center=[40, 0, H])
    eff = float(np.atleast_1d(ff.Prad)[0] / np.interp(f[i], f, port.P_acc))
    d = float(10 * np.log10(np.atleast_1d(ff.Dmax)[0]))
    rec = dict(case=name, l_tot=l_tot, tube=tube, mesh=m, cells=int(n), time_s=dt, f_res=fres,
               f_s11min=float(f[i]), s11min=float(s11db[i]), zin_at_min=[float(zin[i].real), float(zin[i].imag)],
               R_res=float(np.interp(fres, f, zin.real)), bw=bw, eff=eff, D_dbi=d)
    log(f"{name:16s} L_arm {l_tot:5.1f} mm, tube {tube!s:5s}, mesh {m}: {n/1e6:.2f} M cells, {dt:4.0f} s | "
        f"f(X=0) {fres/1e6:7.2f} MHz, R {rec['R_res']:5.1f} ohm, S11min {s11db[i]:6.1f} dB @ {f[i]/1e6:7.2f} MHz "
        f"(Z {zin[i].real:.1f}{zin[i].imag:+.1f}j), BW {100*bw:.2f} %, e_rad {100*eff:.1f} %, D {d:.2f} dBi", rec)
    return rec


# ============================================================== C. slot under microstrip
SLOT_RES = {1: 0.5, 2: 0.25}


def slot_run(name, l_slot, m=1):
    sim_path = os.path.join(tempfile.gettempdir(), f"rfkb_slot_{name}")
    W, H, ER, LL = 2.691, 1.43, 4.5, 120.0
    FDTD = openEMS(NrTS=200000, EndCriteria=1e-4)
    FDTD.SetGaussExcite(1.6e9, 1.4e9)
    FDTD.SetBoundaryCond(["PML_8", "PML_8", "MUR", "MUR", "MUR", "MUR"])
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(1e-3)
    res = C0 / (3e9 * np.sqrt(ER)) / 1e-3 / 30
    rf = SLOT_RES[m]
    sub = CSX.AddMaterial("FR4", epsilon=ER)
    sub.AddBox([-LL / 2, -45, 0], [LL / 2, 45, H], priority=0)
    gnd = CSX.AddMetal("gnd")
    ws = 1.0
    if l_slot > 0:
        gnd.AddBox([-LL / 2, -45, 0], [-ws / 2, 45, 0], priority=10)
        gnd.AddBox([ws / 2, -45, 0], [LL / 2, 45, 0], priority=10)
        gnd.AddBox([-ws / 2, -45, 0], [ws / 2, -l_slot / 2, 0], priority=10)
        gnd.AddBox([-ws / 2, l_slot / 2, 0], [ws / 2, 45, 0], priority=10)
    else:
        gnd.AddBox([-LL / 2, -45, 0], [LL / 2, 45, 0], priority=10)
    strip = CSX.AddMetal("strip")
    third = np.array([2 * rf / 3, -rf / 3])
    mesh.AddLine("x", [-LL / 2, LL / 2] + list(fill_lines([-ws / 2 - 3, -ws / 2, ws / 2, ws / 2 + 3], rf)))
    mesh.AddLine("y", [0.0] + list(W / 2 + third) + list(-W / 2 - third) + [-45, 45])
    if l_slot > 0:
        mesh.AddLine("y", [l_slot / 2 - rf / 3, l_slot / 2 + 2 * rf / 3, -l_slot / 2 + rf / 3, -l_slot / 2 - 2 * rf / 3])
    mesh.AddLine("z", list(np.linspace(0, H, 5)) + [-25, 25])
    for ax in "xyz":
        mesh.SmoothMeshLines(ax, res if ax != "y" else res, 1.4)
    # MSL ports need the mesh first (>= 5 lines along the port)
    p1 = FDTD.AddMSLPort(1, strip, [-LL / 2, -W / 2, H], [0, W / 2, 0], "x", "z", excite=-1,
                         FeedShift=10 * res, MeasPlaneShift=LL / 4, priority=10)
    p2 = FDTD.AddMSLPort(2, strip, [LL / 2, -W / 2, H], [0, W / 2, 0], "x", "z", MeasPlaneShift=LL / 4, priority=10)
    n = np.prod([len(mesh.GetLines(a)) for a in "xyz"])
    t0 = time.time()
    FDTD.Run(sim_path, cleanup=True, verbose=0, exact_endcriteria=True)
    dt = time.time() - t0
    f = np.linspace(0.2e9, 3.0e9, 2801)
    p1.CalcPort(sim_path, f)
    z = np.real(p1.Z_ref.copy())
    p1.CalcPort(sim_path, f, ref_impedance=z)
    p2.CalcPort(sim_path, f, ref_impedance=z)
    s21 = p2.uf_ref / p1.uf_inc
    s11 = p1.uf_ref / p1.uf_inc
    s21db = 20 * np.log10(np.abs(s21))
    pts = {fe: float(np.interp(fe, f, s21db)) for fe in (433e6, 915e6, 1575e6, 2450e6)}
    imin = int(np.argmin(s21db))
    # fit a series inductance to |S21| at low frequency (< 0.5 * first-resonance or < 1 GHz)
    zl = 50.0
    sel = (f <= min(1.0e9, 0.5 * f[imin] if s21db[imin] < -3 else 1.0e9))
    # |S21|^2 = 1/(1+(wL/2Z0)^2) (ideal series L between equal lines) -> L = 2Z0/w * sqrt(1/|S21|^2 - 1)
    with np.errstate(invalid="ignore"):
        lfit = 2 * zl / (2 * np.pi * f[sel]) * np.sqrt(np.maximum(1 / np.abs(s21[sel]) ** 2 - 1, 0))
    lfit = float(np.median(lfit[np.isfinite(lfit)])) if l_slot > 0 else 0.0
    v = C0 / np.sqrt((ER + 1) / 2)
    zslot = 4 * v * lfit / (l_slot * 1e-3) if l_slot > 0 else float("nan")
    rec = dict(case=name, l_slot=l_slot, mesh=m, cells=int(n), time_s=dt, s21_at=pts, f_s21min=float(f[imin]),
               s21min=float(s21db[imin]), L_fit_nH=lfit * 1e9, Z_slot_fit=zslot,
               s11max=float(20 * np.log10(np.abs(s11)).max()))
    log(f"{name:10s} slot {l_slot:4.0f} mm, mesh {m}: {n/1e6:.2f} M cells, {dt:4.0f} s | S21 433/915/1575/2450 MHz "
        + " / ".join(f"{pts[k]:6.2f}" for k in sorted(pts)) + f" dB | S21 min {s21db[imin]:6.2f} dB @ {f[imin]/1e9:.3f} "
        f"GHz | L_fit {lfit*1e9:.2f} nH -> Z_slot {zslot:.0f} ohm", rec)
    return rec


# ============================================================== D. SMA pad, L2 intact vs voided
PAD_RES = {1: 0.10, 2: 0.06, 3: 0.035}       # level 3 added 2026-10-13 (levels 1->2 not converged)


def pad_run(name, void, m=1):
    sim_path = os.path.join(tempfile.gettempdir(), f"rfkb_pad_{name}")
    HP, ERP, HC, ERC = 0.2104, 4.4, 1.065, 4.55
    W, WP, LP, LL = 0.4027, 1.3, 3.0, 50.0       # LL 30 -> 50 mm (2026-10-13 fix, see below)
    g = 0.4                                        # void margin beyond the pad
    # NrTS bounded: with the void, a static (non-radiating) field stays in the L2-L3 region and the energy never
    # falls below ~-9 dB, so the end criterion cannot trigger; 12 ns is >> the RF transients of a 50 mm line.
    FDTD = openEMS(NrTS=300000 if not void else int(12e-9 / (0.1e-12 if m == 1 else 0.05e-12)), EndCriteria=1e-4)
    FDTD.SetGaussExcite(3.7e9, 3.3e9)              # 0.4-7 GHz
    # z-min PEC = L3. y: PML_8 (added 2026-10-13: with MUR on y the L2-L3 parallel-plate mode excited through
    # the void stayed trapped, energy stuck at -9.4 dB)
    FDTD.SetBoundaryCond(["PML_8", "PML_8", "PML_8" if void else "MUR", "PML_8" if void else "MUR", "PEC", "MUR"])
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(1e-3)
    rf = PAD_RES[m]
    yb = 6.0
    core = CSX.AddMaterial("core", epsilon=ERC)
    core.AddBox([-LL / 2, -yb, -HC], [LL / 2, yb, 0], priority=0)
    prep = CSX.AddMaterial("prepreg", epsilon=ERP)
    prep.AddBox([-LL / 2, -yb, 0], [LL / 2, yb, HP], priority=0)
    l2 = CSX.AddMetal("L2")
    vx, vy = LP / 2 + g, WP / 2 + g
    if void:
        l2.AddBox([-LL / 2, -yb, 0], [-vx, yb, 0], priority=10)
        l2.AddBox([vx, -yb, 0], [LL / 2, yb, 0], priority=10)
        l2.AddBox([-vx, -yb, 0], [vx, -vy, 0], priority=10)
        l2.AddBox([-vx, vy, 0], [vx, yb, 0], priority=10)
        via = CSX.AddMetal("vias")
        for sx in (-1, 1):
            for sy in (-1, 1):
                cx, cy = sx * (vx + 0.4), sy * (vy + 0.4)
                via.AddBox([cx - 0.15, cy - 0.15, -HC], [cx + 0.15, cy + 0.15, 0], priority=10)
    else:
        l2.AddBox([-LL / 2, -yb, 0], [LL / 2, yb, 0], priority=10)
    top = CSX.AddMetal("top")
    top.AddBox([-LP / 2, -WP / 2, HP], [LP / 2, WP / 2, HP], priority=10)
    res = C0 / (7e9 * np.sqrt(ERP)) / 1e-3 / 30
    # merged fixed lines -> no slivers (2026-10-13: the first version had 0.02 mm cells, dt 0.03 ps)
    vxl = [-vx, vx, -(vx + 0.25), -(vx + 0.55), vx + 0.25, vx + 0.55] if void else []
    vyl = [-vy, vy, -(vy + 0.25), -(vy + 0.55), vy + 0.25, vy + 0.55] if void else []
    mesh.AddLine("x", [-LL / 2, LL / 2])
    mesh.AddLine("x", fill_lines([-LP / 2 - 1.5, -LP / 2, LP / 2, LP / 2 + 1.5] + vxl, rf))
    third = np.array([2 * rf / 3, -rf / 3])
    ylines = [0.0] + list(W / 2 + third) + list(-W / 2 - third) + list(WP / 2 + third) + list(-WP / 2 - third) + vyl
    mesh.AddLine("y", fill_lines(ylines + [-(WP / 2 + 1.0), WP / 2 + 1.0] + ([-(vy + 1.0), vy + 1.0] if void else []), rf))
    mesh.AddLine("y", [-yb, yb])
    nzp = 8 if m == 3 else 4
    mesh.AddLine("z", list(np.linspace(0, HP, nzp + 1)) + list(np.linspace(-HC, 0, 9)) + [HP + 3.0])
    mesh.SmoothMeshLines("x", res, 1.4)
    mesh.SmoothMeshLines("y", min(res, 0.5), 1.4)
    mesh.SmoothMeshLines("z", res, 1.4)
    # FIX 2026-10-13: the first version fed the port 1.2 mm from the line end and measured 4 mm in — both INSIDE
    # the PML_8 layer (8 cells x ~0.7 mm = 5.4 mm): the "port in PML" fault of sim2_openems_broken.py.
    p1 = FDTD.AddMSLPort(1, top, [-LL / 2, -W / 2, HP], [-LP / 2, W / 2, 0], "x", "z", excite=-1,
                         FeedShift=9.0, MeasPlaneShift=14.0, priority=10)
    p2 = FDTD.AddMSLPort(2, top, [LL / 2, -W / 2, HP], [LP / 2, W / 2, 0], "x", "z", MeasPlaneShift=14.0, priority=10)
    n = np.prod([len(mesh.GetLines(a)) for a in "xyz"])
    t0 = time.time()
    FDTD.Run(sim_path, cleanup=True, verbose=0, exact_endcriteria=True)
    dt = time.time() - t0
    f = np.linspace(0.4e9, 7.0e9, 3301)
    p1.CalcPort(sim_path, f)
    z = np.real(p1.Z_ref.copy())
    zline = float(np.interp(1e9, f, z))
    p1.CalcPort(sim_path, f, ref_impedance=50)
    s11db = 20 * np.log10(np.abs(p1.uf_ref / p1.uf_inc))
    rl = {fe: float(-np.interp(fe, f, s11db)) for fe in (915e6, 1575e6, 2450e6, 5800e6)}
    rec = dict(case=name, void=void, mesh=m, cells=int(n), time_s=dt, RL_at=rl, Z_line_1GHz=zline)
    log(f"{name:10s} void {void!s:5s}, mesh {m}: {n/1e6:.2f} M cells, {dt:4.0f} s | feed-line Z0 (port) "
        f"{zline:.1f} ohm | RL re 50 ohm at 0.915/1.575/2.45/5.8 GHz: "
        + " / ".join(f"{rl[k]:5.1f}" for k in sorted(rl)) + " dB", rec)
    return rec


def main(args):
    for a in args:
        if a == "ifa_sweep":
            for L in (50.0, 62.0, 75.0):
                ifa_run(f"ifa_L{L:.0f}_m1", L, False, 1)
        elif a == "ifa_sweep2":                     # added 2026-10-13: 75 mm resonated at 1037 MHz
            for L in (82.0, 87.0, 92.0):
                ifa_run(f"ifa_L{L:.0f}_m1", L, False, 1)
        elif a.startswith("ifa_L"):                 # ifa_L<len>_<free|tube>_m<k>
            parts = a.split("_")
            ifa_run(a, float(parts[1][1:]), parts[2] == "tube", int(parts[3][1:]))
        elif a == "slot":
            for ls in (0, 10, 20, 40, 60):
                slot_run(f"slot{ls}_m1", ls, 1)
            for ls in (0, 60):
                slot_run(f"slot{ls}_m2", ls, 2)
        elif a == "pad":
            for v in (False, True):
                for m in (1, 2):
                    pad_run(f"pad_{'void' if v else 'solid'}_m{m}", v, m)
        elif a.startswith("pad_"):                  # pad_<solid|void>_m<k>
            parts = a.split("_")
            pad_run(a, parts[1] == "void", int(parts[2][1:]))
        else:
            raise SystemExit(f"unknown case {a}")


if __name__ == "__main__":
    main(sys.argv[1:])
