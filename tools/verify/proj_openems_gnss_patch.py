#!/usr/bin/env python3
"""
proj_openems_gnss_patch.py -- openEMS (EC-FDTD) verification for
kb/20-projects-recipes/patch-antenna-design-walkthrough.md

Truncated-corner square patch for GPS L1 (1575.42 MHz) on JLCPCB 2-layer FR-4 (er 4.5, tan d 0.02,
dielectric 1.51 mm), 80 x 80 mm ground/substrate, coaxial probe modelled as a 50-ohm lumped port on the
x axis. Corners at (+x,+y) and (-x,-y) truncated by right isosceles triangles of leg a.

Pre-registered expectations (from tools/verify/proj_patch_gnss.py, written BEFORE the first run):
  * square side 44.88 mm resonates (linear, a = 0) within +-3 % of 1575.42 MHz (TL model ignores probe,
    finite ground; the kb/16 2.45 GHz FR-4 run came out 2.2 % LOW)
  * CP needs a mode split of f0/Q ~ 45 MHz; dS/S = 1/(2Q) -> a ~ 5.4 mm gives an AR minimum < 3 dB
  * AR <= 3 dB bandwidth ~ 1 % (~15 MHz); input R at the AR minimum ~ half the single-mode R at the probe
  * realised RHCP gain on boresight ~ 0 dBic (radiation efficiency 25-45 %)
Results are appended to the end of this file's docstring by hand (never overwrite earlier runs).

Results log (append-only):
  2026-09-29 quick #1 (feed sliver-cell mesh, dt 3.7e-13 s): linear 44.88 mm, probe 9.41 mm from centre:
             S11 min -19.7 dB at 1558.5 MHz (-1.07 %), Z 41.3+3.8j, VSWR2 BW 29.5 MHz. CP run killed (no result).
  2026-10-02 quick #2 (sliver fixed, dt 1.08e-12 s, 448 844 cells): linear: -19.6 dB at 1558.5 MHz, Z 41.3+3.9j,
             BW 29.8 MHz (74 s) -> mesh change did not move f_res.
             CP a=5.36 mm, probe 15.0 mm from centre, corners (+,+)/(-,-): AR min 1.80 dB at 1572.5 MHz, **LHCP**;
             AR<=3 dB BW 10.0 MHz; Z at AR-min 54.7+13.4j (S11 -17.4 dB); at L1 AR 2.24 dB, S11 -18.3 dB;
             S11 min -21.8 dB at 1587.0 MHz, VSWR2 BW 61 MHz (103 s).
             vs pre-registration: AR<3 dB yes; AR BW 10 vs ~15 MHz predicted (-35 %); R at AR-min ~ R/2 yes;
             sense came out LHCP for this corner choice -> mirror the truncation for RHCP.
  2026-10-02 design sweep (mirrored corners (+x,-y)/(-x,+y) -> RHCP confirmed), side 44.88 mm:
             a 4.8, xf 15.0: AR min 4.53 dB at 1567.5 MHz (under-split), at L1 5.73 dB
             a 5.36, xf 13.5: AR min 1.76 dB at 1572.5 MHz, Z 47.5+13.0j, at L1 AR 2.22 dB / S11 -18.4 dB
             a 5.9, xf 15.0: AR min 0.77 dB at 1577.5 MHz, AR<=3 dB BW 15.0 MHz, Z 42.1+13.5j; at L1 AR 0.95 dB, S11 -15.7 dB
             -> optimum leg ~5.9 mm = 1.10 x the dS/S = 1/(2Q) prediction (5.36 mm); final: side 44.94 mm (x 1577.5/1575.42).
  2026-10-02 final 44.94/5.9/15: coarse (0.8 mm, 448 844 cells): AR 0.72 dB at 1575.0 MHz, D_RHCP 6.30 dBic, X-pol -21.2,
             e 35.6 %, G_RHCP 1.81 dBic, HPBW 96 deg.  FINE (0.5 mm, 6 substrate cells, 1.36 M cells, 295 s): AR min 1.33 dB at
             **1545.0 MHz** (-1.9 %), at L1 AR 10.2 dB, S11 min -30.3 dB at 1573.2 MHz -> NOT CONVERGED.
             Diagnosis: the patch edges were not mesh lines (free uniform grid), so the staircased patch size changed with
             the mesh by up to one cell (0.8 mm ~ 28 MHz). Fix: edge-locked lines with the thirds rule ("edges" mode).
             All earlier sweep numbers are therefore mesh-quantised; rerun pending.
  2026-10-02 edge-locked mesh (thirds rule), side 44.94: coarse AR min 0.65 dB at 1567.5 MHz (fine run killed by pause).
  2026-10-02 edge-locked, side 44.71 mm (= 44.94 x 1567.5/1575.42), a 5.9, probe 15.0, mirrored (RHCP):
             coarse (444 400 cells, 87 s): AR min 1.01 dB at 1577.5 MHz; at L1 AR 1.04 dB, S11 -15.1 dB; D_RHCP 6.29 dBic,
                    D_LHCP -18.6 dBic, e 35.5 %, G_RHCP 1.80 dBic; AR<=3 dB BW 12.5 MHz
             fine (1 279 016 cells, 355 s): AR min 0.23 dB at **1575.0 MHz**; at L1 AR 0.35 dB, S11 -15.6 dB (Z 44.7+15.1j);
                    AR<=3 dB BW 15.0 MHz; S11 min -25.7 dB at 1599.0 MHz; D_RHCP 6.29 dBic, D_LHCP -28.3 dBic, e_rad 35.6 %,
                    G_RHCP 1.81 dBic (mismatch 0.12 dB -> 1.69 dBic realised); HPBW 96 deg; AR 0.3/0.5/0.8/1.1/1.5/1.9 dB
                    at theta 0/30/45/60/75/90 deg.
             -> coarse vs fine AR-minimum frequency differ by 2.5 MHz (0.16 %): CONVERGED (criterion <= 0.3 %). FINAL DESIGN.

Run:  ~/opt/openEMS/venv/bin/python tools/verify/proj_openems_gnss_patch.py [quick|design|final]
"""
import os
import sys
import tempfile
import time

import numpy as np
from CSXCAD import ContinuousStructure            # noqa: E402
from openEMS import openEMS                        # noqa: E402
from openEMS.physical_constants import C0, EPS0    # noqa: E402

ER, TAND, H = 4.5, 0.02, 1.51       # mm
GND = 80.0
F0, FC = 1.575e9, 0.5e9
F_L1 = 1575.42e6


def run(Lp, a, xf, res_div=25, tag="run", sub_cells=4, patch_res=0.8, fcalc=None, full_pattern=False, mirror=False):
    """Lp: square side [mm]; a: truncation leg [mm] (0 = linear); xf: probe distance from centre along -x [mm]."""
    sim_path = os.path.join(tempfile.gettempdir(), f"rfkb_gnss_{tag}")
    FDTD = openEMS(NrTS=120000, EndCriteria=1e-4)
    FDTD.SetGaussExcite(F0, FC)
    FDTD.SetBoundaryCond(["MUR"] * 6)
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(1e-3)
    res = C0 / (F0 + FC) / 1e-3 / res_div
    margin = 50.0                                     # >= lambda/4 at 1.5 GHz
    box = [GND + 2 * margin, GND + 2 * margin]
    mesh.AddLine("x", [-box[0] / 2, box[0] / 2])
    mesh.AddLine("y", [-box[1] / 2, box[1] / 2])
    mesh.AddLine("z", [-margin, H + margin + 20])
    kappa = 2 * np.pi * F0 * EPS0 * ER * TAND
    sub = CSX.AddMaterial("FR4", epsilon=ER, kappa=kappa)
    sub.AddBox([-GND / 2, -GND / 2, 0], [GND / 2, GND / 2, H], priority=0)
    mesh.AddLine("z", np.linspace(0, H, sub_cells + 1))
    # patch polygon (truncated corners at +x+y and -x-y)
    h2 = Lp / 2
    if a > 0 and not mirror:      # corners (+x,+y), (-x,-y) cut  -> LHCP with feed on -x (first run)
        pts = [(-h2 + a, -h2), (h2, -h2), (h2, h2 - a), (h2 - a, h2), (-h2, h2), (-h2, -h2 + a)]
    elif a > 0:                   # corners (+x,-y), (-x,+y) cut  -> opposite sense
        pts = [(-h2, -h2), (h2 - a, -h2), (h2, -h2 + a), (h2, h2), (-h2 + a, h2), (-h2, h2 - a)]
    else:
        pts = [(-h2, -h2), (h2, -h2), (h2, h2), (-h2, h2)]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    patch = CSX.AddMetal("patch")
    patch.AddPolygon([xs, ys], "z", H, priority=10)
    gnd = CSX.AddMetal("gnd")
    gnd.AddBox([-GND / 2, -GND / 2, 0], [GND / 2, GND / 2, 0], priority=10)
    # fine uniform mesh over the patch (staircases the 45-deg truncation edges), plus patch edge lines
    # mesh lines locked to the patch edges with the thirds rule (1/3 cell inside, 2/3 outside each edge);
    # the first version used a free uniform grid, which quantised the patch size by up to one cell
    r = patch_res
    nin = int(np.round((Lp - 2 * r / 3) / r))
    inner = np.linspace(-h2 + r / 3, h2 - r / 3, nin + 1)
    outer = np.array([-h2 - 2 * r / 3, h2 + 2 * r / 3, -h2 - 2 * r / 3 - r, h2 + 2 * r / 3 + r])
    fine = np.sort(np.concatenate([inner, outer]))
    finex = np.concatenate([fine[np.abs(fine + xf) > 0.45 * patch_res], [-xf]])   # no sliver cells at the feed
    finey = np.concatenate([fine[np.abs(fine) > 0.45 * patch_res], [0.0]])
    mesh.AddLine("x", finex)
    mesh.AddLine("y", finey)
    mesh.AddLine("x", [-GND / 2, GND / 2])
    mesh.AddLine("y", [-GND / 2, GND / 2])
    port = FDTD.AddLumpedPort(1, 50, [-xf, 0, 0], [-xf, 0, H], "z", 1.0, priority=5)
    mesh.SmoothMeshLines("all", res / np.sqrt(ER) * 1.5, 1.4)
    nf2ff = FDTD.CreateNF2FFBox()
    n = len(mesh.GetLines("x")) * len(mesh.GetLines("y")) * len(mesh.GetLines("z"))
    t0 = time.time()
    FDTD.Run(sim_path, cleanup=True, verbose=0)
    dt = time.time() - t0

    f = np.linspace(1.45e9, 1.70e9, 1001)
    port.CalcPort(sim_path, f)
    s11 = port.uf_ref / port.uf_inc
    zin = port.uf_tot / port.if_tot
    s11db = 20 * np.log10(np.abs(s11))
    i0 = int(np.argmin(s11db))
    fr = np.linspace(1.50e9, 1.65e9, 61) if fcalc is None else np.asarray(fcalc)
    ff = nf2ff.CalcNF2FF(sim_path, fr, [0.0], [0.0], center=[0, 0, 1e-3])
    Er = np.array([np.abs(ff.E_cprh[k][0, 0]) for k in range(len(fr))])
    El = np.array([np.abs(ff.E_cplh[k][0, 0]) for k in range(len(fr))])
    ar = 20 * np.log10((Er + El) / np.maximum(np.abs(Er - El), 1e-30))
    k_ar = int(np.argmin(ar))
    sense = "RHCP" if Er[k_ar] > El[k_ar] else "LHCP"
    out = dict(tag=tag, cells=n, time=dt, f=f, s11db=s11db, zin=zin, fres=f[i0], s11min=s11db[i0], zres=zin[i0],
               fr=fr, ar=ar, f_ar=fr[k_ar], ar_min=ar[k_ar], sense=sense, Er=Er, El=El)
    band = f[s11db <= -9.54]
    out["bw"] = (band.max() - band.min()) if band.size else 0.0
    arb = fr[ar <= 3.0]
    out["ar_bw"] = (arb.max() - arb.min()) if arb.size else 0.0
    out["z_at_ar"] = np.interp(fr[k_ar], f, zin.real) + 1j * np.interp(fr[k_ar], f, zin.imag)
    out["s11_at_ar"] = np.interp(fr[k_ar], f, s11db)
    out["s11_at_L1"] = np.interp(F_L1, f, s11db)
    out["ar_at_L1"] = np.interp(F_L1, fr, ar)
    if full_pattern:
        fp = F_L1
        ffp = nf2ff.CalcNF2FF(sim_path, [fp], np.arange(0, 181, 3.0), [0.0, 45.0, 90.0, 135.0], center=[0, 0, 1e-3])
        p_acc = float(np.interp(fp, f, port.P_acc))
        prad = float(np.atleast_1d(ffp.Prad)[0])
        dmax = float(np.atleast_1d(ffp.Dmax)[0])
        eff = prad / p_acc
        # RHCP directivity on boresight: D_R = 4 pi r^2 |E_R|^2 / (2 eta0 Prad)
        eta0 = 376.730313
        ER0 = np.abs(ffp.E_cprh[0][0, 0])
        EL0 = np.abs(ffp.E_cplh[0][0, 0])
        r = 1.0
        dr = 4 * np.pi * r ** 2 * ER0 ** 2 / (2 * eta0) / prad
        dl = 4 * np.pi * r ** 2 * EL0 ** 2 / (2 * eta0) / prad
        out.update(dmax_dbi=10 * np.log10(dmax), eff=eff, drhcp_dbic=10 * np.log10(dr), dlhcp=10 * np.log10(dl),
                   g_rhcp_dbic=10 * np.log10(dr * eff),
                   mismatch_db=-10 * np.log10(1 - 10 ** (np.interp(fp, f, s11db) / 10)))
        # 3 dB beamwidth of total field in the phi = 0 cut (theta from 0..90)
        En = ffp.E_norm[0][:, 0]
        th = np.arange(0, 181, 3.0)
        u = (En / En[0]) ** 2
        idx = np.where(u < 0.5)[0]
        out["hpbw_phi0"] = 2 * th[idx[0]] if idx.size else 180.0
        # AR vs elevation in phi=0 cut
        Ert = np.abs(ffp.E_cprh[0][:, 0])
        Elt = np.abs(ffp.E_cplh[0][:, 0])
        out["ar_theta"] = (th, 20 * np.log10((Ert + Elt) / np.maximum(np.abs(Ert - Elt), 1e-30)))
    return out


def show(r):
    s = (f"[{r['tag']}] cells {r['cells']}, {r['time']:.0f} s: S11 min {r['s11min']:.1f} dB at {r['fres']/1e6:.1f} MHz "
         f"(Z {r['zres'].real:.1f}{r['zres'].imag:+.1f}j), VSWR2 BW {r['bw']/1e6:.1f} MHz; "
         f"AR min {r['ar_min']:.2f} dB ({r['sense']}) at {r['f_ar']/1e6:.1f} MHz, AR<=3 dB BW {r['ar_bw']/1e6:.1f} MHz, "
         f"Z at AR-min {r['z_at_ar'].real:.1f}{r['z_at_ar'].imag:+.1f}j, S11 there {r['s11_at_ar']:.1f} dB; "
         f"at L1: AR {r['ar_at_L1']:.2f} dB, S11 {r['s11_at_L1']:.1f} dB")
    if "eff" in r:
        s += (f"\n      pattern @L1: Dmax {r['dmax_dbi']:.2f} dBi, e_rad {100*r['eff']:.1f} %, D_RHCP(boresight) "
              f"{r['drhcp_dbic']:.2f} dBic, D_LHCP {r['dlhcp']:.2f} dBic, realised G_RHCP {r['g_rhcp_dbic']:.2f} dBic "
              f"(before mismatch {r['mismatch_db']:.2f} dB), HPBW(phi=0) {r['hpbw_phi0']:.0f} deg")
        th, art = r["ar_theta"]
        s += "\n      AR vs theta (phi=0): " + ", ".join(f"{int(t)}:{v:.1f}" for t, v in zip(th, art) if t in (0, 30, 45, 60, 75, 90))
    print(s, flush=True)
    return s


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "quick"
    lines = []
    if mode == "edges":      # re-check after the mesh fix: final geometry on two meshes
        Lp, a, xf = [float(v) for v in sys.argv[2:5]]
        lines.append(show(run(Lp, a, xf, tag="edges_coarse", mirror=True, full_pattern=True)))
        lines.append(show(run(Lp, a, xf, tag="edges_fine", res_div=35, sub_cells=6, patch_res=0.5, mirror=True,
                              full_pattern=True)))
    elif mode == "quick":
        # 1) linear square patch: resonance check of the TL design
        lines.append(show(run(44.88, 0.0, 9.41, tag="lin_nominal")))
        # 2) CP with the predicted truncation; probe where the single-mode R ~ 100 ohm (CP input R ~ R/2)
        lines.append(show(run(44.88, 5.36, 15.0, tag="cp_pred")))
    elif mode == "design":
        # sweep truncation leg and feed position around the prediction, mirrored geometry (RHCP check)
        for Lp, a, xf in [(44.88, 4.8, 15.0), (44.88, 5.9, 15.0), (44.88, 5.36, 13.5)]:
            lines.append(show(run(Lp, a, xf, tag=f"cp_L{Lp}_a{a}_x{xf}", mirror=True)))
    elif mode == "final":
        Lp, a, xf = [float(v) for v in sys.argv[2:5]]
        lines.append(show(run(Lp, a, xf, tag="final", full_pattern=True, mirror=True)))
        lines.append(show(run(Lp, a, xf, tag="final_fine", res_div=35, sub_cells=6, patch_res=0.5,
                              full_pattern=True, mirror=True)))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
