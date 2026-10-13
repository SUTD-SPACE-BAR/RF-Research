#!/usr/bin/env python3
"""e11_discontinuities_openems.py — openEMS (FDTD) checks of microstrip discontinuity models
for kb/03-transmission-lines-matching/microstrip-discontinuities.md (task W5-E11).

Two discontinuities are simulated full-wave and compared with the closed-form models in
tools/verify/e11_discontinuities.py:

  A. OPEN END. One MSL port drives a straight strip that ends at x = 0. The reflection
     coefficient measured at a reference plane d = 20 mm before the end is moved to the end with
     the port's own measured beta: Gamma_end = Gamma_meas * exp(+2j beta d). An ideal open would
     give Gamma_end = 1; the fringing field makes Gamma_end = exp(-2j beta dl), so the equivalent
     length extension is dl = -angle(Gamma_end)/(2 beta).  |Gamma_end| < 1 measures the power
     radiated by the open end.
  B. 90-DEGREE BEND, square corner and mitred corners (M = 50 %, Douville-James optimum, 75 %).
     Two MSL ports; |S11| is independent of where the reference planes are (the ports are
     normalised to the measured line impedance), so it can be compared directly with the
     Kirschning-Jansen-Koster (1983) and Gupta et al. equivalent circuits.

Board: the KB's illustrative 2-layer case, h = 1.51 mm, er = 4.5 (lossless), zero-thickness PEC
strip, W = 2.80 mm (50 ohm). A second, narrow open end (W = 0.75 mm, ~90 ohm) tests the width trend.

Pre-registered expectations (written before the first run, 2026-10-03):
  * Open end, W/h = 1.85: dl within +-10 % of Kirschning-Jansen-Koster (0.60 mm at low f), with the
    fine mesh changing dl by < 5 % relative to the coarse mesh. dl rises slowly with frequency.
  * |Gamma_end| > 0.98 below 3 GHz (open-end radiation is small on 1.5 mm FR-4 at UHF).
  * Square bend: |S11| within 3 dB of the Kirschning corner model from 1 to 6 GHz (about -19 dB
    at 2.45 GHz); the optimum mitre lowers |S11| to below -25 dB up to at least 4 GHz; the 50 %
    and 75 % mitres are worse than the optimum at the upper end of the band.

Run (needs openEMS + CSXCAD Python, see kb/16-simulation-tools/installing-tools-macos.md):
    ~/opt/openEMS/venv/bin/python tools/verify/e11_discontinuities_openems.py      # ~10-25 min
Results: tools/verify/e11_discontinuities_openems_results.txt (appended) and
         tools/verify/data/e11_openems_discontinuities.npz (curves for e11_discontinuities.py).
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
from openEMS.physical_constants import C0          # noqa: E402

H, ER = 1.51, 4.5           # mm, -
F_MAX = 6.0e9
F = np.linspace(0.3e9, F_MAX, 115)
BC = ["PML_8", "PML_8", "PML_8", "PML_8", "PEC", "PML_8"]   # x-, x+, y-, y+, ground, top
EXACT_EC = os.environ.get("RFKB_EXACT_EC", "0") == "1"
OUT_TXT = os.path.join(HERE, "e11_discontinuities_openems_results.txt")
OUT_NPZ = os.path.join(HERE, "data", "e11_openems_discontinuities.npz")


def _thirds(edge, fine, metal_side):
    """openEMS 'thirds rule' around a PEC edge: one line fine/3 inside the metal, one 2fine/3 outside."""
    s = 1.0 if metal_side < 0 else -1.0       # metal on the negative side -> inside = edge - fine/3
    return [edge - s * fine / 3.0, edge + s * 2.0 * fine / 3.0]


def _run(FDTD, sim_path):
    t0 = time.time()
    FDTD.Run(sim_path, cleanup=True, verbose=0, **({"exact_endcriteria": True} if EXACT_EC else {}))
    return time.time() - t0


# ----------------------------------------------------------------------------- A. open end
def _open_end_run(W, res_div, fine_div, sub_cells, tag, through):
    """through=False: strip ends at x = 0 (open end). through=True: identical mesh, strip continues into the
    x-max PML (matched line) -> clean incident wave and clean beta at the same reference plane."""
    sim_path = os.path.join(tempfile.gettempdir(), f"rfkb_e11_{tag}")
    FDTD = openEMS(NrTS=150000, EndCriteria=1e-4)
    FDTD.SetGaussExcite(0.5 * (0.3e9 + F_MAX), 0.5 * (F_MAX - 0.3e9))
    FDTD.SetBoundaryCond(BC)
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(1e-3)
    lam = C0 / (F_MAX * np.sqrt(ER)) * 1e3            # mm
    res = lam / res_div
    fine = min(W, H) / fine_div                       # cell near the strip edges / end
    x0, xend, xmax, xmeas = -60.0, 0.0, 25.0, -20.0
    # x: thirds rule at the open end, a fine zone of +-3W around it, then graded out to res
    mesh.AddLine("x", _thirds(xend, fine, metal_side=-1) + [-3 * W, 3 * W])
    mesh.SmoothMeshLines("x", fine, 1.3)
    mesh.AddLine("x", [x0, xmax, xmeas])
    mesh.SmoothMeshLines("x", res, 1.3)
    mesh.AddLine("y", [0.0] + _thirds(W / 2, fine, metal_side=-1) + _thirds(-W / 2, fine, metal_side=+1))
    mesh.SmoothMeshLines("y", fine, 1.3)
    mesh.AddLine("y", [-30.0, 30.0])
    mesh.SmoothMeshLines("y", res, 1.3)
    mesh.AddLine("z", np.linspace(0, H, sub_cells + 1).tolist() + [20.0])
    mesh.SmoothMeshLines("z", res, 1.3)

    sub = CSX.AddMaterial("FR4", epsilon=ER)
    sub.AddBox([x0, -30.0, 0], [xmax, 30.0, H], priority=0)
    pec = CSX.AddMetal("strip")
    p1 = FDTD.AddMSLPort(1, pec, [x0, -W / 2, H], [xmax if through else xend, W / 2, 0], "x", "z",
                         excite=-1, FeedShift=12 * res, MeasPlaneShift=xmeas - x0, priority=10)
    d = xend - (x0 + p1.measplane_shift)              # mm, meas plane -> open end (after snapping)
    ncells = np.prod([len(mesh.GetLines(a)) for a in "xyz"])
    dt = _run(FDTD, sim_path)
    p1.CalcPort(sim_path, F)
    return dict(u=p1.uf_tot.copy(), beta=np.real(p1.beta.copy()), zl=np.real(p1.Z_ref.copy()), d=d,
                ncells=ncells, time=dt, fine=fine, res=res)


def open_end(W, res_div=30, fine_div=6, sub_cells=4, tag="oe"):
    """Reference subtraction: V_meas(open) = V_inc + V_ref and V_meas(through) = V_inc on the same mesh, so
    Gamma_meas = (V_open - V_thru)/V_thru without relying on the port's Z/beta extraction inside a standing
    wave (which is ill-conditioned near voltage nodes). beta comes from the matched through-line run."""
    ro = _open_end_run(W, res_div, fine_div, sub_cells, tag + "_open", through=False)
    rt = _open_end_run(W, res_div, fine_div, sub_cells, tag + "_thru", through=True)
    beta, d = rt["beta"], ro["d"]
    gam = (ro["u"] - rt["u"]) / rt["u"]
    gam_end = gam * np.exp(2j * beta * d * 1e-3)
    ph = np.unwrap(np.angle(gam_end))
    ph -= 2 * np.pi * np.round(ph[0] / (2 * np.pi))   # small negative angle at low f
    dl = -ph / (2 * beta) * 1e3                       # mm
    ee = (beta * C0 / (2 * np.pi * F)) ** 2
    return dict(f=F, dl=dl, mag=np.abs(gam_end), zl=rt["zl"], ee=ee, d=d, ncells=ro["ncells"],
                time=ro["time"] + rt["time"], fine=ro["fine"], res=ro["res"])


# ----------------------------------------------------------------------------- B. bend
def bend(W, mitre, res_div=30, fine_div=6, sub_cells=4, tag="bend"):
    """Horizontal arm from x = -L to the corner, vertical arm from the corner to y = +L.
    Corner square [-W/2, W/2]^2; outer corner at (+W/2, -W/2). Mitre fraction M = x/d with d = W*sqrt(2)
    (Douville-James definition): the cut removes a right isosceles triangle with legs 2*M*W."""
    sim_path = os.path.join(tempfile.gettempdir(), f"rfkb_e11_{tag}")
    L = 45.0
    FDTD = openEMS(NrTS=150000, EndCriteria=1e-4)
    FDTD.SetGaussExcite(0.5 * (0.3e9 + F_MAX), 0.5 * (F_MAX - 0.3e9))
    FDTD.SetBoundaryCond(BC)
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(1e-3)
    lam = C0 / (F_MAX * np.sqrt(ER)) * 1e3
    res = lam / res_div
    fine = min(W, H) / fine_div
    xm, xp, ym, yp = -L, 18.0, -18.0, L
    for ax, lo, hi in (("x", xm, xp), ("y", ym, yp)):
        mesh.AddLine(ax, _thirds(W / 2, fine, -1) + _thirds(-W / 2, fine, +1) + [-2.5 * W, 2.5 * W])
        mesh.SmoothMeshLines(ax, fine, 1.3)                  # fine corner zone (staircases the mitre)
        mesh.AddLine(ax, [lo, hi])
        mesh.SmoothMeshLines(ax, res, 1.3)
    mesh.AddLine("z", np.linspace(0, H, sub_cells + 1).tolist() + [20.0])
    mesh.SmoothMeshLines("z", res, 1.3)
    sub = CSX.AddMaterial("FR4", epsilon=ER)
    sub.AddBox([xm, ym, 0], [xp, yp, H], priority=0)
    pec = CSX.AddMetal("strip")
    leg = 2 * mitre * W
    # L-shaped strip with the outer corner cut (polygon in the z = H plane)
    pts = [(-L + 30.0, -W / 2), (W / 2 - leg, -W / 2), (W / 2, -W / 2 + leg), (W / 2, L - 30.0),
           (-W / 2, L - 30.0), (-W / 2, W / 2), (-L + 30.0, W / 2)]
    if mitre <= 0:
        pts = [(-L + 30.0, -W / 2), (W / 2, -W / 2), (W / 2, L - 30.0), (-W / 2, L - 30.0),
               (-W / 2, W / 2), (-L + 30.0, W / 2)]
    pts = np.array(pts).T
    pec.AddPolygon(pts, "z", H, priority=5)
    # MSL ports on the outer 30 mm of each arm (port metal overlaps the polygon ends)
    p1 = FDTD.AddMSLPort(1, pec, [-L, -W / 2, H], [-L + 30.0, W / 2, 0], "x", "z", excite=-1,
                         FeedShift=10 * res, MeasPlaneShift=20.0, priority=10)
    p2 = FDTD.AddMSLPort(2, pec, [-W / 2, L, H], [W / 2, L - 30.0, 0], "y", "z",
                         MeasPlaneShift=20.0, priority=10)
    ncells = np.prod([len(mesh.GetLines(a)) for a in "xyz"])
    dt = _run(FDTD, sim_path)
    p1.CalcPort(sim_path, F)
    zl = p1.Z_ref.copy()
    p1.CalcPort(sim_path, F, ref_impedance=zl)
    p2.CalcPort(sim_path, F, ref_impedance=zl)
    s11 = p1.uf_ref / p1.uf_inc
    s21 = p2.uf_ref / p1.uf_inc
    return dict(f=F, s11=s11, s21=s21, zl=np.real(zl), ncells=ncells, time=dt, mitre=mitre)


def main():
    out, npz = [], {}
    stamp = time.strftime("%Y-%m-%d %H:%M")
    fe = [0.915e9, 2.45e9, 4.0e9, 5.8e9]
    # A. open ends
    for W, tag, divs in ((2.80, "oe50", ((30, 4, 4), (45, 8, 6))), (0.75, "oe90", ((45, 8, 6),))):
        for rd, fdv, sc in divs:
            r = open_end(W, rd, fdv, sc, tag=f"{tag}_{rd}")
            key = f"open_W{W:.2f}_r{rd}"
            npz.update({key + "_f": r["f"], key + "_dl": r["dl"], key + "_mag": r["mag"], key + "_ee": r["ee"]})
            out.append(f"OPEN END W={W} mm h={H} er={ER}: mesh lambda/{rd}, fine {r['fine']:.3f} mm, {sc} substrate "
                       f"cells, {r['ncells']} cells, {r['time']:.0f} s, ref plane {r['d']:.3f} mm before end")
            for f0 in fe:
                i = int(np.argmin(abs(r["f"] - f0)))
                out.append(f"   f={r['f'][i]/1e9:5.3f} GHz  Z={r['zl'][i]:6.2f} ohm  eeff={r['ee'][i]:.3f}  "
                           f"dl={r['dl'][i]:.4f} mm (dl/h={r['dl'][i]/H:.4f})  |G_end|={r['mag'][i]:.4f}")
            print("\n".join(out[-5:]), flush=True)
            os.makedirs(os.path.dirname(OUT_NPZ), exist_ok=True)
            np.savez(OUT_NPZ, **npz)              # incremental save (crash/pause safety)
    # B. bends
    md = 0.52 + 0.65 * np.exp(-1.35 * 2.80 / H)
    cases = [("sq_r30", 0.0, 30, 4, 4), ("sq", 0.0, 45, 8, 6), ("m50", 0.50, 45, 8, 6),
             ("mDJ", md, 45, 8, 6), ("m75", 0.75, 45, 8, 6)]
    for tag, m, rd, fdv, sc in cases:
        r = bend(2.80, m, rd, fdv, sc, tag=f"bend_{tag}")
        key = f"bend_{tag}"
        npz.update({key + "_f": r["f"], key + "_s11": r["s11"], key + "_s21": r["s21"]})
        out.append(f"BEND W=2.80 mm mitre M={100*m:.1f} % ({tag}): mesh lambda/{rd}, {r['ncells']} cells, "
                   f"{r['time']:.0f} s")
        for f0 in fe:
            i = int(np.argmin(abs(r["f"] - f0)))
            out.append(f"   f={r['f'][i]/1e9:5.3f} GHz  Z={r['zl'][i]:6.2f} ohm  |S11|={20*np.log10(abs(r['s11'][i])):6.1f} dB"
                       f"  |S21|={20*np.log10(abs(r['s21'][i])):6.3f} dB")
        print("\n".join(out[-5:]), flush=True)
        np.savez(OUT_NPZ, **npz)
    os.makedirs(os.path.dirname(OUT_NPZ), exist_ok=True)
    np.savez(OUT_NPZ, **npz)
    txt = "\n".join(out)
    with open(OUT_TXT, "a") as fh:
        fh.write(f"\n=== e11_discontinuities_openems.py {stamp} ===\n{txt}\n")
    print("saved", OUT_NPZ)


if __name__ == "__main__":
    main()
