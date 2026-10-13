#!/usr/bin/env python3
"""sim2_openems_nosecone.py — openEMS (EC-FDTD) model of a quarter-wave whip on an aluminium bulkhead,
bare and inside a fibreglass nose cone, at 915 MHz (E220-900T30D, Avionics-C) and 433 MHz
(E22-400T33D, Avionics-B). W5-S11, gap G-16-01. Page: kb/16-simulation-tools/openems-workflow.md
("Run 3 — nose-cone detuning").

Team geometry is NOT recorded in the Space Bar notes, so the model uses the KB's representative cone
(kb/08-antennas/antennas-on-rockets.md Example 3): inner radius 50 mm, wall 3 mm, here as a 4:1 tangent
ogive (length 424 mm) with a 20 mm cylindrical shoulder; G10-class fibreglass er 4.7, tan d 0.02
(tools/verify/em_fresnel_radome.py); a 2 mm aluminium bulkhead disc of radius 50 mm at z = 0; a 2 x 2 mm
square PEC whip (equivalent round radius 0.59 x 2 = 1.18 mm) fed by a 50-ohm lumped port across a 1 mm gap
above the bulkhead. Whip lengths: 78 mm (the KB's bench-trimmed 915 MHz whip) and 165 mm (433 MHz).

PRE-REGISTERED EXPECTATIONS (written 2026-10-13 before any run; do not edit — add addenda below)
  P1  Detuning by the cone (G10, 3 mm, er 4.7) is DOWNWARD. Estimate by energy perturbation: the wall at
      r = 50-53 mm holds ~1-1.5 % of the near-field electric energy of a whip of radius ~1 mm (ln(53/50) /
      ln(r_nf/a), r_nf = lambda/2pi = 52 mm @ 915, 110 mm @ 433), weighted by (er-1)/er ~ 0.79 for a field
      normal to the wall and (er-1) ~ 3.7 for a tangential one.  =>  915 MHz: -0.5 % to -3 % (central -1.5 %);
      433 MHz: -0.3 % to -2 % (central -0.8 %).  The KB's qualitative claim is "a few percent".
  P2  Cone loss (tan d 0.02) costs < 0.2 dB of radiation efficiency at either band.
  P3  Mesh study (3 levels, fine-region cell 2.0 -> 1.4 -> 1.0 mm): the cone-induced SHIFT changes by
      < 0.3 percentage points between the two finest meshes, although the absolute resonance may move more.
  P4  A lower-permittivity hand-laid laminate (er 4.0) gives a proportionally smaller shift (~(er-1) scaling:
      ~0.8 x the er-4.7 shift).
  P5  The counterpoise matters more than the cone: replacing the bare 100 mm disc by a disc + 250 mm
      conductive avionics-bay tube (radius 45 mm) moves the resonance by more than the cone does (> 3 %).
  P6  Bare-whip resonance (X = 0) on the small disc: 915 MHz whip 0.88-0.97 GHz; R at resonance 15-35 ohm
      (small ground: below the 36 ohm of an infinite plane).

Run:  ~/opt/openEMS/venv/bin/python tools/verify/sim2_openems_nosecone.py [case ...]   (each case 1-12 min)
      cases: f915_bare_m{1,2,3}, f915_cone_m{1,2,3}, f915_cone_er4_m2, f915_bay_m2, f915_bay_cone_m2,
             f433_bare_m2, f433_cone_m2, f915_cone_pml_m2 ; no argument = all.
Results: appended to tools/verify/sim2_openems_results.txt (text) and sim2_openems_results.jsonl.
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
from openEMS.physical_constants import C0, EPS0    # noqa: E402

R_IN, WALL, SHOULDER = 50.0, 3.0, 20.0            # mm
R_OUT = R_IN + WALL
L_CONE = 4 * 2 * R_OUT                            # 4:1 tangent ogive, 424 mm
DISC_R, DISC_T = 50.0, 2.0
WIRE_HALF = 1.0                                    # 2 x 2 mm square whip
GAP = 1.0                                          # feed gap above the bulkhead
MESH = {1: 2.0, 2: 1.4, 3: 1.0}                    # fine-region cell (mm) per mesh level


def ogive_r(z, r_base=R_OUT, length=L_CONE):
    """Outer radius of a tangent ogive at height z above its base (z = 0 .. length)."""
    rho = (r_base ** 2 + length ** 2) / (2 * r_base)
    return np.sqrt(np.maximum(rho ** 2 - z ** 2, 0.0)) + r_base - rho


def cone_polygon(npts=60):
    """(r, z) polygon of the shell cross-section: shoulder + ogive, inner surface offset by WALL radially."""
    z = np.linspace(0, L_CONE, npts)
    ro = ogive_r(z)
    ri = np.maximum(ro - WALL, 0.0)
    keep = ri > 0.0
    r_outer = np.concatenate(([R_OUT], ro))
    z_outer = np.concatenate(([-SHOULDER], z))
    r_inner = np.concatenate((ri[keep][::-1], [R_IN]))
    z_inner = np.concatenate((z[keep][::-1], [-SHOULDER]))
    return np.array([np.concatenate((r_outer, r_inner)), np.concatenate((z_outer, z_inner))])


def fill_lines(fixed, res, merge=0.3):
    """Sorted fixed lines (points closer than merge*res merged), each gap split into ceil(gap/res) equal cells."""
    pts = []
    for v in sorted(float(x) for x in fixed):
        if not pts or v - pts[-1] > merge * res:
            pts.append(v)
    out = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(1, int(np.ceil((b - a) / res - 1e-9)))
        out += list(a + (b - a) * np.arange(1, n + 1) / n)
    return np.array(out)


CASES = {}
for band, f0, fc, L in (("f915", 0.9e9, 0.5e9, 78.0), ("f433", 0.44e9, 0.24e9, 165.0)):
    for m in (1, 2, 3):
        CASES[f"{band}_bare_m{m}"] = dict(f0=f0, fc=fc, L=L, cone=None, bay=False, mesh=m, bc="MUR")
        CASES[f"{band}_cone_m{m}"] = dict(f0=f0, fc=fc, L=L, cone=4.7, bay=False, mesh=m, bc="MUR")
    CASES[f"{band}_cone_er4_m2"] = dict(f0=f0, fc=fc, L=L, cone=4.0, bay=False, mesh=2, bc="MUR")
    CASES[f"{band}_bay_m2"] = dict(f0=f0, fc=fc, L=L, cone=None, bay=True, mesh=2, bc="MUR")
    CASES[f"{band}_bay_cone_m2"] = dict(f0=f0, fc=fc, L=L, cone=4.7, bay=True, mesh=2, bc="MUR")
    CASES[f"{band}_cone_pml_m2"] = dict(f0=f0, fc=fc, L=L, cone=4.7, bay=False, mesh=2, bc="PML_8")
    # boundary study (added 2026-10-13 after the MUR/PML directivity difference was seen): PML bare, and a
    # doubled air margin with MUR, both at mesh 2
    CASES[f"{band}_bare_pml_m2"] = dict(f0=f0, fc=fc, L=L, cone=None, bay=False, mesh=2, bc="PML_8")
    CASES[f"{band}_bare_big_m2"] = dict(f0=f0, fc=fc, L=L, cone=None, bay=False, mesh=2, bc="MUR", margin=2.0)
    CASES[f"{band}_cone_big_m2"] = dict(f0=f0, fc=fc, L=L, cone=4.7, bay=False, mesh=2, bc="MUR", margin=2.0)
DEFAULT = ["f915_bare_m1", "f915_cone_m1", "f915_bare_m2", "f915_cone_m2", "f915_bare_m3", "f915_cone_m3",
           "f915_cone_er4_m2", "f915_bay_m2", "f915_bay_cone_m2", "f433_bare_m2", "f433_cone_m2",
           "f915_cone_pml_m2"]


def run(name, c):
    sim_path = os.path.join(tempfile.gettempdir(), f"rfkb_nc_{name}")
    f0, fc, L = c["f0"], c["fc"], c["L"]
    fmin, fmax = f0 - fc, f0 + fc
    res_air = C0 / fmax / 1e-3 / 20                 # lambda_min/20 in air, mm
    res_f = MESH[c["mesh"]]
    lam_lo = C0 / (f0 - 0.5 * fc) / 1e-3           # margin rule: lambda/4 at the low end of the band of interest
    margin = lam_lo / 4 * c.get("margin", 1.0)
    xy = R_OUT + margin
    z_lo = -(250 + margin) if c["bay"] else -margin
    z_hi = L_CONE + margin

    FDTD = openEMS(NrTS=150000, EndCriteria=1e-4)
    FDTD.SetGaussExcite(f0, fc)
    FDTD.SetBoundaryCond([c["bc"]] * 6)
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(1e-3)

    # --- geometry ---
    whip = CSX.AddMetal("whip")
    bulk = CSX.AddMetal("bulkhead")
    if c.get("stl"):                                 # G-16-05 demo: same parts read from STL files
        for prop, fn in zip((whip, bulk), c["stl"]):
            if fn is None:                           # this part from the primitive instead
                if prop is bulk:
                    bulk.AddCylinder([0, 0, -DISC_T], [0, 0, 0], DISC_R, priority=10)
                continue
            prim = prop.AddPolyhedronReader(fn, priority=10)
            prim.ReadFile()
    else:
        whip.AddBox([-WIRE_HALF, -WIRE_HALF, GAP], [WIRE_HALF, WIRE_HALF, GAP + L], priority=10)
        bulk.AddCylinder([0, 0, -DISC_T], [0, 0, 0], DISC_R, priority=10)
    if c["bay"]:
        bay = CSX.AddMetal("avbay")                 # conductive av-bay / coax-shield counterpoise
        bay.AddCylinder([0, 0, -250], [0, 0, -DISC_T], 45.0, priority=10)
    if c["cone"] is not None:
        kappa = 2 * np.pi * f0 * EPS0 * c["cone"] * 0.02
        gl = CSX.AddMaterial("fibreglass", epsilon=c["cone"], kappa=kappa)
        gl.AddRotPoly(points=cone_polygon(), norm_dir="x", elevation=0, rot_axis="z",
                      angle=[0, 2 * np.pi], priority=1)
        if c["bay"]:                                 # fibreglass body tube around the bay
            gl.AddCylindricalShell([0, 0, -250], [0, 0, -SHOULDER], R_IN + WALL / 2, WALL, priority=1)
    port = FDTD.AddLumpedPort(1, 50, [-WIRE_HALF, -WIRE_HALF, 0], [WIRE_HALF, WIRE_HALF, GAP], "z", 1.0,
                              priority=5)

    # --- mesh: fixed lines merged (no slivers) and each gap split into equal cells <= res in the fine
    #     regions; graded to lambda/20 outside by SmoothMeshLines(ratio 1.4) ---
    for ax in "xy":
        mesh.AddLine(ax, fill_lines([-WIRE_HALF, WIRE_HALF, -R_IN, R_IN, -R_OUT, R_OUT, -R_OUT - 3, R_OUT + 3], res_f))
        mesh.AddLine(ax, [-xy, xy])
        mesh.SmoothMeshLines(ax, res_air, 1.4)
    z_fine_top = GAP + L + 8
    mesh.AddLine("z", fill_lines([-DISC_T - 6, -DISC_T, 0, GAP, GAP + L, z_fine_top], res_f))
    mesh.AddLine("z", fill_lines([z_fine_top, L_CONE], 3 * res_f)[1:])     # shell near-vertical: coarser in z
    mesh.AddLine("z", [z_lo, -SHOULDER, z_hi] + ([-250] if c["bay"] else []))
    mesh.SmoothMeshLines("z", res_air, 1.4)
    nf2ff = FDTD.CreateNF2FFBox()

    nx, ny, nz = (len(mesh.GetLines(a)) for a in "xyz")
    if os.environ.get("RFKB_DRY"):                  # recipe step 7: setup only + material/PEC dumps for ParaView
        FDTD.Run(sim_path, cleanup=True, setup_only=True, debug_material=True, debug_PEC=True, verbose=0)
        print(f"{name}: dry run, {nx}x{ny}x{nz} = {nx*ny*nz/1e6:.2f} M cells, dumps in {sim_path}")
        return None
    t0 = time.time()
    FDTD.Run(sim_path, cleanup=True, verbose=0, exact_endcriteria=True)
    dt = time.time() - t0

    f = np.linspace(fmin + 0.1 * fc, fmax - 0.1 * fc, 3001)
    port.CalcPort(sim_path, f)
    s11 = port.uf_ref / port.uf_inc
    zin = port.uf_tot / port.if_tot
    s11db = 20 * np.log10(np.abs(s11))
    # series resonance: X = 0 crossing from - to + nearest f0
    x = zin.imag
    idx = np.where((x[:-1] < 0) & (x[1:] >= 0))[0]
    if idx.size:
        i = idx[np.argmin(np.abs(f[idx] - f0))]
        fres = f[i] - x[i] * (f[i + 1] - f[i]) / (x[i + 1] - x[i])
    else:
        fres = float("nan")
    rres = float(np.interp(fres, f, zin.real)) if np.isfinite(fres) else float("nan")
    imin = int(np.argmin(s11db))
    out = dict(case=name, **{k: v for k, v in c.items()}, cells=nx * ny * nz, nx=nx, ny=ny, nz=nz,
               time_s=dt, f_res=fres, R_res=rres, f_s11min=float(f[imin]), s11min_db=float(s11db[imin]))
    # radiation efficiency and directivity at the resonance
    try:
        fr = fres if np.isfinite(fres) else float(f[imin])
        ff = nf2ff.CalcNF2FF(sim_path, fr, np.arange(0, 181, 3.0), [0.0, 90.0], center=[0, 0, GAP + L / 2])
        p_acc = float(np.interp(fr, f, port.P_acc))
        prad = float(np.atleast_1d(ff.Prad)[0])
        out.update(eff=prad / p_acc, D_dbi=float(10 * np.log10(np.atleast_1d(ff.Dmax)[0])))
    except Exception as e:                           # keep the S11 result even if NF2FF fails
        out.update(eff=float("nan"), D_dbi=float("nan"), nf2ff_error=str(e))
    return out


def fmt(r):
    return (f"{r['case']:18s} cells {r['cells']/1e6:5.2f} M ({r['nx']}x{r['ny']}x{r['nz']}), {r['time_s']:6.0f} s: "
            f"f_res(X=0) {r['f_res']/1e6:8.2f} MHz, R {r['R_res']:5.1f} ohm, S11min {r['s11min_db']:6.1f} dB @ "
            f"{r['f_s11min']/1e6:7.1f} MHz, e_rad {100*r['eff']:5.1f} %, D {r['D_dbi']:5.2f} dBi")


def main(names):
    names = names or DEFAULT
    for n in names:
        r = run(n, CASES[n])
        if r is None:
            continue
        line = fmt(r)
        print(line, flush=True)
        with open(os.path.join(HERE, "sim2_openems_results.txt"), "a") as fh:
            fh.write(f"[{time.strftime('%Y-%m-%d %H:%M')}] sim2_openems_nosecone {line}\n")
        with open(os.path.join(HERE, "sim2_openems_results.jsonl"), "a") as fh:
            fh.write(json.dumps({"script": "nosecone", **r}, default=float) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
