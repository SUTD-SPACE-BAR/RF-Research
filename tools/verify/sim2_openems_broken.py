#!/usr/bin/env python3
"""sim2_openems_broken.py — openEMS practicalities by deliberately breaking a model whose answer is known.
W5-S11, gap G-16-05. Page: kb/16-simulation-tools/openems-workflow.md ("Practicalities: dumps, STL/curved
geometry, graded meshes, and a deliberately broken model") and simulation-validation.md.

Reference model = Run 1 of openems-workflow (validated): microstrip W 2.80 mm on h 1.51 mm, er 4.5, t = 0,
100 mm long, two MSL ports, PML_8 on the line ends (lambda/30 mesh, 4 substrate cells): |S11| < -53 dB.
Each case changes ONE thing:
  ref        the validated set-up (+ a time-domain E-field dump in the substrate mid-plane for ParaView)
  pec_box    the line, now terminated in two 50-ohm LUMPED ports at its ends, inside a closed PEC box
             (x 100, y 100, z 21.5 mm) — a shielded enclosure: box resonances appear as narrow spikes
  port_pml   the MSL feed placed inside the PML (FeedShift 0, MeasPlaneShift 2 cells) — the classic port error
  ungraded   x mesh jumps from 0.25 mm to 4 mm at x = 0 (ratio 16, rule <= 1.5)
  stl        not a microstrip case: the 915 MHz bare whip of sim2_openems_nosecone (mesh 1) with the whip and
             bulkhead read from STL files written here, vs the same model from AddBox/AddCylinder
  patch_ec   the 2.45 GHz FR-4 patch (sim_openems_patch coarse) with EndCriteria 1e-2, 1e-3 and 1e-5

PRE-REGISTERED EXPECTATIONS (written 2026-10-13 before any run; addenda only below)
  B1 ref: |S11| < -50 dB over 0.4-2.9 GHz (as Run 1).
  B2 pec_box: spikes (|S11| local maxima > -20 dB, i.e. > 30 dB above the reference floor) near the TE_mn0
     resonances of the box, f_mn0 = (c/2) sqrt((m/a)^2 + (n/b)^2) with a = b = 100 mm: f_110 = 2.12 GHz
     (dielectric partial fill (1.51 of 21.5 mm, er 4.5) lowers it by 2-8 %). The odd/even selection depends on
     the line's position (centre line: modes with an E-field maximum at y = 0, i.e. n odd).
  B3 port_pml: the simulation does not reach -40 dB within 30 000 steps, or S11 is unphysical (|S11| > 0 dB
     somewhere or < -20 dB nowhere useful): "garbage".
  B4 ungraded: a mesh step of 16x reflects: |S11| rises to -35 ... -20 dB (numerical impedance step from the
     different dispersion of the 0.25 mm and 4 mm cells).
  B5 stl: the STL whip/bulkhead gives the same f_res as the primitives within 0.2 % (same voxelisation up to
     the polyhedron's facetting of the disc, 64 facets).
  B6 patch_ec: EndCriteria 1e-2 (-20 dB) truncates the ring-down: f_res within 0.5 % but the VSWR-2 bandwidth
     and S11 depth wrong by > 10 %, with ripple; 1e-3 within 2 % of 1e-5; 1e-4 vs 1e-5 within 0.5 %.

ADDENDUM 1 (2026-10-13, after run 1): B1 PASS (-53.7 dB). B2 could not be tested as designed: the lumped ports
  touched the PEC wall, so their excitation edges lay on the wall and were SHORTED (|S11| = 0 dB at all f) — itself
  a classic set-up error, kept as finding "pec_box". A corrected case "pec_box2" (ports 5 mm inside the walls, mesh
  from fill_lines so no sliver cells) is added to test B2 as written. B3 PASS (S11 -11 dB, S21 -17.7 dB: garbage).
  B4 MISS (smaller than predicted: max -38.9 dB, median -47.9 dB vs the -35...-20 dB window). B5 MISS: the STL
  whip + bulkhead resonated at 919.64 MHz vs 932.87 MHz with primitives (-1.42 %) and set-up took 474 s vs 13 s;
  case "stl_whip" (STL whip, primitive disc) is added to isolate which part differs.
  stl_whip (STL whip, primitive disc): 832.32 MHz (-10.8 %), and the PEC dump has 10 381 PEC edges vs 10 508
  with primitives: the STL faces lie exactly ON mesh lines and the polyhedron inside-test drops edges on its own
  surface. Post-hoc case "stl_whip_eps" moves the STL faces 0.01 mm off the lines to confirm.
  B6 first run: all four EndCriteria gave the same 8 s run and nearly the same answer (BW 2.18/2.18/2.14/2.14 %)
  because sim_openems_patch.run() does not pass exact_endcriteria — the criterion is then only checked at the
  ~4 s wall-clock progress report (the trap documented on openems-workflow). Case "patch_ecx" repeats it with
  exact_endcriteria forced on.

Run: ~/opt/openEMS/venv/bin/python tools/verify/sim2_openems_broken.py [case ...]   (all: ~5-10 min)
Results: appended to tools/verify/sim2_openems_results.txt.
"""
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

W, H, ER, L_LINE = 2.80, 1.51, 4.5, 100.0
F_MAX = 3.0e9
LOG = []


def log(s):
    print(s, flush=True)
    LOG.append(s)


def msl(case, res_div=30, sub_cells=4):
    sim_path = os.path.join(tempfile.gettempdir(), f"rfkb_broken_{case}")
    nrts = 30000 if case == "port_pml" else 200000
    FDTD = openEMS(NrTS=nrts, EndCriteria=1e-4)
    FDTD.SetGaussExcite(1.6e9, 1.4e9)
    if case in ("pec_box", "pec_box2"):
        FDTD.SetBoundaryCond(["PEC"] * 6)
    else:
        FDTD.SetBoundaryCond(["PML_8", "PML_8", "MUR", "MUR", "PEC", "MUR"])
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(1e-3)
    res = C0 / (F_MAX * np.sqrt(ER)) / 1e-3 / res_div
    third = np.array([2 * res / 3, -res / 3]) / 4
    yb = 50.0 if case.startswith("pec_box") else 25.0
    ztop = 21.5 if case.startswith("pec_box") else 20.0
    if case == "ungraded":
        mesh.AddLine("x", np.concatenate((np.arange(-L_LINE / 2, 0, 0.25), np.arange(0, L_LINE / 2 + 1e-9, 4.0))))
    else:
        mesh.AddLine("x", [-L_LINE / 2, L_LINE / 2])
        mesh.SmoothMeshLines("x", res)
    mesh.AddLine("y", [0.0])
    mesh.AddLine("y", W / 2 + third)
    mesh.AddLine("y", -W / 2 - third)
    mesh.SmoothMeshLines("y", res / 4)
    mesh.AddLine("y", [-yb, yb])
    mesh.SmoothMeshLines("y", res)
    mesh.AddLine("z", np.linspace(0, H, sub_cells + 1))
    mesh.AddLine("z", [ztop])
    mesh.SmoothMeshLines("z", res)
    sub = CSX.AddMaterial("FR4", epsilon=ER)
    sub.AddBox([-L_LINE / 2, -yb, 0], [L_LINE / 2, yb, H], priority=0)
    pec = CSX.AddMetal("strip")
    if case == "pec_box2":
        from sim2_openems_nosecone import fill_lines
        xa, xb = -45.0, 45.0
        pec.AddBox([xa + 1, -W / 2, H], [xb - 1, W / 2, H], priority=10)
        p1 = FDTD.AddLumpedPort(1, 50, [xa, -W / 2, 0], [xa + 1, W / 2, H], "z", 1.0, priority=5)
        p2 = FDTD.AddLumpedPort(2, 50, [xb - 1, -W / 2, 0], [xb, W / 2, H], "z", 0, priority=5)
        mesh.SetLines("x", fill_lines([-L_LINE / 2, xa, xa + 1, xb - 1, xb, L_LINE / 2], res))
    elif case == "pec_box":
        pec.AddBox([-L_LINE / 2 + res, -W / 2, H], [L_LINE / 2 - res, W / 2, H], priority=10)
        xa, xb = -L_LINE / 2, L_LINE / 2
        mesh.AddLine("x", [xa + res, xb - res])
        p1 = FDTD.AddLumpedPort(1, 50, [xa, -W / 2, 0], [xa + res, W / 2, H], "z", 1.0, priority=5)
        p2 = FDTD.AddLumpedPort(2, 50, [xb - res, -W / 2, 0], [xb, W / 2, H], "z", 0, priority=5)
        mesh.SmoothMeshLines("x", res)
    else:
        fs, mps = (0.0, 2 * res) if case == "port_pml" else (10 * res, L_LINE / 3)
        p1 = FDTD.AddMSLPort(1, pec, [-L_LINE / 2, -W / 2, H], [0, W / 2, 0], "x", "z", excite=-1,
                             FeedShift=fs, MeasPlaneShift=mps, priority=10)
        p2 = FDTD.AddMSLPort(2, pec, [L_LINE / 2, -W / 2, H], [0, W / 2, 0], "x", "z", MeasPlaneShift=L_LINE / 3,
                             priority=10)
    if case == "ref":                                   # time-domain E dump, substrate mid-plane, VTK
        et = CSX.AddDump("Et_midplane", dump_type=0, file_type=0, sub_sampling=[2, 2, 1])
        et.AddBox([-L_LINE / 2, -yb, H / 2], [L_LINE / 2, yb, H / 2])
    n = len(mesh.GetLines("x")) * len(mesh.GetLines("y")) * len(mesh.GetLines("z"))
    t0 = time.time()
    FDTD.Run(sim_path, cleanup=True, verbose=0, exact_endcriteria=True)
    dt = time.time() - t0
    f = np.linspace(0.2e9, F_MAX, 2801)
    if case.startswith("pec_box"):
        p1.CalcPort(sim_path, f)
        p2.CalcPort(sim_path, f)
    else:
        p1.CalcPort(sim_path, f)
        z = np.real(p1.Z_ref.copy())
        p1.CalcPort(sim_path, f, ref_impedance=z)
        p2.CalcPort(sim_path, f, ref_impedance=z)
    s11 = 20 * np.log10(np.abs(p1.uf_ref / p1.uf_inc))
    s21 = 20 * np.log10(np.abs(p2.uf_ref / p1.uf_inc))
    nts = None
    try:                                                # number of time steps actually run
        import h5py  # noqa: F401
    except Exception:
        pass
    ndump = 0
    if case == "ref":
        ndump = len([fn for fn in os.listdir(sim_path) if fn.startswith("Et_midplane")])
    return dict(f=f, s11=s11, s21=s21, cells=n, time=dt, ndump=ndump, path=sim_path, nts=nts)


def report_msl(case, r):
    band = (r["f"] >= 0.4e9) & (r["f"] <= 2.9e9)
    s = r["s11"][band]
    fb = r["f"][band]
    log(f"{case:9s}: {r['cells']} cells, {r['time']:.0f} s; |S11| max {s.max():6.1f} dB @ {fb[np.argmax(s)]/1e9:.3f} GHz,"
        f" median {np.median(s):6.1f} dB; |S21| min {r['s21'][band].min():6.2f} dB"
        + (f"; {r['ndump']} VTK dump files in {r['path']}" if r["ndump"] else ""))
    if case.startswith("pec_box"):
        # local maxima of S11 above -20 dB
        pk = [i for i in range(1, s.size - 1) if s[i] > s[i - 1] and s[i] >= s[i + 1] and s[i] > -20]
        log("           spikes > -20 dB at: " + ", ".join(f"{fb[i]/1e9:.3f} GHz ({s[i]:.1f} dB)" for i in pk[:12]))
        for m, nn in ((1, 1), (2, 1), (1, 2), (3, 1), (2, 2), (1, 3)):
            log(f"           empty-box TE_{m}{nn}0 {C0/2*np.sqrt((m/0.1)**2+(nn/0.1)**2)/1e9:.3f} GHz")


def write_stl_box(fn, lo, hi):
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    v = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                  [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]])
    faces = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4),
             (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    _write_stl(fn, v, faces)


def write_stl_cylinder(fn, r, z0, z1, nf=64):
    a = np.linspace(0, 2 * np.pi, nf, endpoint=False)
    v = [[0, 0, z0], [0, 0, z1]]
    v += [[r * np.cos(t), r * np.sin(t), z0] for t in a]
    v += [[r * np.cos(t), r * np.sin(t), z1] for t in a]
    faces = []
    for k in range(nf):
        b0, b1 = 2 + k, 2 + (k + 1) % nf
        t0, t1 = b0 + nf, b1 + nf
        faces += [(0, b1, b0), (1, t0, t1), (b0, b1, t1), (b0, t1, t0)]
    _write_stl(fn, np.array(v), faces)


def _write_stl(fn, v, faces):
    with open(fn, "w") as fh:
        fh.write("solid s\n")
        for a, b, c in faces:
            nrm = np.cross(v[b] - v[a], v[c] - v[a])
            nrm = nrm / (np.linalg.norm(nrm) or 1)
            fh.write(f" facet normal {nrm[0]:e} {nrm[1]:e} {nrm[2]:e}\n  outer loop\n")
            for k in (a, b, c):
                fh.write(f"   vertex {v[k][0]:e} {v[k][1]:e} {v[k][2]:e}\n")
            fh.write("  endloop\n endfacet\n")
        fh.write("endsolid s\n")


def stl_case(whip_only=False, eps=0.0):
    import sim2_openems_nosecone as nc
    tmp = tempfile.mkdtemp(prefix="rfkb_stl_")
    whip_fn, disc_fn = os.path.join(tmp, "whip.stl"), os.path.join(tmp, "bulkhead.stl")
    # eps > 0 moves the STL faces just outside the mesh lines (x, y, top) and just below the feed-gap line
    write_stl_box(whip_fn, [-nc.WIRE_HALF - eps, -nc.WIRE_HALF - eps, nc.GAP - eps],
                  [nc.WIRE_HALF + eps, nc.WIRE_HALF + eps, nc.GAP + 78.0 + eps])
    write_stl_cylinder(disc_fn, nc.DISC_R, -nc.DISC_T, 0.0)
    c = dict(nc.CASES["f915_bare_m1"])
    c["stl"] = (whip_fn, None) if whip_only else (whip_fn, disc_fn)
    r_stl = nc.run("stl_f915_bare_m1", c)
    log(f"stl{'_whip' if whip_only else '     '}{f' eps {eps} mm' if eps else ''} : {'whip only' if whip_only else 'whip + bulkhead'} from STL (AddPolyhedronReader): f_res {r_stl['f_res']/1e6:.2f} MHz, "
        f"R {r_stl['R_res']:.1f} ohm, {r_stl['time_s']:.0f} s  (primitives, same mesh: see f915_bare_m1)")
    return r_stl


def patch_case(exact=False):
    import sim_openems_patch as sp
    from openEMS import openEMS as OE

    class OEx(OE):                                      # force deterministic end-criterion checks
        def Run(self, *a, **k):
            k["exact_endcriteria"] = True
            return super().Run(*a, **k)

    cls = OEx if exact else OE
    rows = []
    for ec in (1e-2, 1e-3, 1e-4, 1e-5):
        orig = sp.openEMS
        sp.openEMS = lambda NrTS=60000, EndCriteria=1e-4, _ec=ec: cls(NrTS=NrTS, EndCriteria=_ec)
        try:
            r = sp.run(20, 4, f"ec{ec:g}")
        finally:
            sp.openEMS = orig
        rows.append((ec, r))
        log(f"patch_ec{'x' if exact else ' '}: EndCriteria {ec:g}{' (exact_endcriteria)' if exact else ''}: f_res {r['fres']/1e9:.4f} GHz, S11min {r['s11min']:.1f} dB, "
            f"BW(VSWR2) {100*r['bw']:.2f} %, e_rad {100*r['eff']:.1f} %, {r['time']:.0f} s")
    return rows


def main(cases):
    cases = cases or ["ref", "pec_box", "port_pml", "ungraded", "stl", "patch_ec"]
    for c in cases:
        if c == "stl":
            stl_case()
        elif c == "stl_whip":
            stl_case(whip_only=True)
        elif c == "stl_whip_eps":
            stl_case(whip_only=True, eps=0.01)
        elif c == "patch_ec":
            patch_case()
        elif c == "patch_ecx":
            patch_case(exact=True)
        else:
            report_msl(c, msl(c))
    with open(os.path.join(HERE, "sim2_openems_results.txt"), "a") as fh:
        for line in LOG:
            fh.write(f"[{time.strftime('%Y-%m-%d %H:%M')}] sim2_openems_broken {line}\n")


if __name__ == "__main__":
    main(sys.argv[1:])
