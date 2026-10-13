#!/usr/bin/env python3
"""sim_openems_msl.py — openEMS (EC-FDTD) microstrip-line check for kb/16-simulation-tools/openems-workflow.md

What it does
  A straight 50-ohm-class microstrip on the JLCPCB 2-layer stack (h = 1.51 mm dielectric, er = 4.5,
  lossless, zero-thickness PEC strip, W = 2.80 mm) is simulated in openEMS with two MSL ports.
  The MSL port's voltage/current probes give the line's characteristic impedance Z0(f) and propagation
  constant beta(f) directly (openEMS ports.py: Z = sqrt(E dE/(H dH)), beta = sqrt(-dE dH/(E H))).
  eps_eff = (beta c0 / omega)^2.

Pre-registered expectation (written before the first run)
  * Z0 within 2 % of the Hammerstad-Jensen / Kirschning-Jansen value for t = 0 (50.4 ohm, eps_eff 3.39
    quasi-static) and of the independent 2-D FD solver tools/verify/tline_fd2d.py (t = 0).
  * eps_eff(f) rising slowly with frequency (K-J: ~+1.5 % at 2.45 GHz on a 1.6 mm board).
  * Mesh refinement (lambda/30 -> lambda/50 in x, 4 -> 8 cells through the substrate) changes Z0 by < 1 %.
  * |S21| ~ 0 dB and |S11| < -25 dB (a uniform line between matched ports, reference = port Z0).

Run (needs openEMS + CSXCAD Python, see kb/16-simulation-tools/installing-tools-macos.md):
    ~/opt/openEMS/venv/bin/python tools/verify/sim_openems_msl.py          # ~1-3 min on an M-series Mac
Results are appended to tools/verify/sim_openems_results.txt.
"""
import os
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))           # tools/ -> import rfcalc
sys.path.insert(0, HERE)                            # tools/verify -> tline_fd2d

from CSXCAD import ContinuousStructure            # noqa: E402
from openEMS import openEMS                        # noqa: E402
from openEMS.physical_constants import C0          # noqa: E402

from rfcalc.tline import microstrip_hj, microstrip_kj   # noqa: E402

W, H, ER = 2.80, 1.51, 4.5          # mm, mm, -
L_LINE = 100.0                      # mm, total line length (two 50 mm MSL ports meeting at x = 0)
F_MAX = 3.0e9
F_EVAL = np.array([0.433e9, 0.915e9, 1.575e9, 2.45e9])
# openEMS evaluates the end criterion only at its ~4 s wall-clock progress reports unless --exact-endcriteria
# is given (openems.cpp); set RFKB_EXACT_EC=1 to request deterministic, Nyquist-interval checks.
EXACT_EC = os.environ.get("RFKB_EXACT_EC", "0") == "1"


def run(res_div=30, sub_cells=4, tag="coarse"):
    sim_path = os.path.join(tempfile.gettempdir(), f"rfkb_msl_{tag}")
    unit = 1e-3
    FDTD = openEMS(NrTS=200000, EndCriteria=1e-4)
    FDTD.SetGaussExcite(1.6e9, 1.4e9)       # 0.2-3.0 GHz band, negligible DC content
    # x = propagation: PML absorbs the line ends; z-min PEC = ground plane
    FDTD.SetBoundaryCond(["PML_8", "PML_8", "MUR", "MUR", "PEC", "MUR"])
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(unit)

    lam_min = C0 / (F_MAX * np.sqrt(ER)) / unit      # mm
    res = lam_min / res_div
    third = np.array([2 * res / 3, -res / 3]) / 4    # thirds rule at strip edges (fine cell = res/4)

    mesh.AddLine("x", [-L_LINE / 2, L_LINE / 2])
    mesh.SmoothMeshLines("x", res)
    mesh.AddLine("y", [0.0])
    mesh.AddLine("y", W / 2 + third)
    mesh.AddLine("y", -W / 2 - third)
    mesh.SmoothMeshLines("y", res / 4)
    mesh.AddLine("y", [-25.0, 25.0])
    mesh.SmoothMeshLines("y", res)
    mesh.AddLine("z", np.linspace(0, H, sub_cells + 1))
    mesh.AddLine("z", [20.0])
    mesh.SmoothMeshLines("z", res)

    sub = CSX.AddMaterial("FR4", epsilon=ER)
    sub.AddBox([-L_LINE / 2, -25.0, 0], [L_LINE / 2, 25.0, H], priority=0)

    # two MSL ports meeting at x = 0 (as in the openEMS MSL tutorials); the feed sits ~10 cells in from
    # the PML, the V/I probes MeasPlaneShift from each outer end
    pec = CSX.AddMetal("strip")
    p1 = FDTD.AddMSLPort(1, pec, [-L_LINE / 2, -W / 2, H], [0, W / 2, 0], "x", "z",
                         excite=-1, FeedShift=10 * res, MeasPlaneShift=L_LINE / 3, priority=10)
    p2 = FDTD.AddMSLPort(2, pec, [L_LINE / 2, -W / 2, H], [0, W / 2, 0], "x", "z",
                         MeasPlaneShift=L_LINE / 3, priority=10)

    ncells = len(mesh.GetLines("x")) * len(mesh.GetLines("y")) * len(mesh.GetLines("z"))
    t0 = time.time()
    FDTD.Run(sim_path, cleanup=True, verbose=0, **({"exact_endcriteria": True} if EXACT_EC else {}))
    dt = time.time() - t0

    f = np.linspace(0.2e9, F_MAX, 141)
    p1.CalcPort(sim_path, f)          # Z_ref = measured line impedance
    z_line = p1.Z_ref.copy()
    beta = p1.beta.copy()
    ee = (np.real(beta) * C0 / (2 * np.pi * f)) ** 2
    p1.CalcPort(sim_path, f, ref_impedance=np.real(z_line))
    p2.CalcPort(sim_path, f, ref_impedance=np.real(z_line))
    s11 = p1.uf_ref / p1.uf_inc
    s21 = p2.uf_ref / p1.uf_inc
    return dict(f=f, z=z_line, ee=ee, s11=s11, s21=s21, ncells=ncells, time=dt)


def main():
    out = []
    zhj, eehj = microstrip_hj(W * 1e-3, H * 1e-3, ER, 0.0)
    try:
        import tline_fd2d as fd
        geo = fd.microstrip_geo(W * 1e-3, H * 1e-3, 0.0, ER)
        hmin, hmax = min(W, H) * 1e-3 / 40, H * 1e-3 / 3     # as fd_ms() in tline_microstrip.py
        _, ext, _ = fd.refine_study(lambda sc: fd.line_params(geo, hmin=hmin * sc, hmax=hmax * sc)[:2],
                                    (1.0, 0.5, 0.25))
        z_fd, ee_fd = float(ext[0]), float(ext[1])
    except Exception as e:                       # FD solver optional
        z_fd, ee_fd = float("nan"), float("nan")
        out.append(f"(FD solver unavailable: {e})")
    out.append(f"Microstrip W={W} mm h={H} mm er={ER}, t=0: H-J Z0={zhj:.2f} ohm eps_eff={eehj:.3f}; "
               f"FD solver Z0={z_fd:.2f} ohm eps_eff={ee_fd:.3f}")
    results = {}
    for tag, rd, sc in (("coarse", 30, 4), ("fine", 50, 8)):
        r = run(rd, sc, tag)
        results[tag] = r
        out.append(f"openEMS {tag}: lambda/{rd}, {sc} substrate cells, {r['ncells']} cells, {r['time']:.0f} s")
        for fe in F_EVAL:
            i = np.argmin(abs(r["f"] - fe))
            zkj, eekj = microstrip_kj(W * 1e-3, H * 1e-3, ER, r["f"][i], 0.0)
            out.append(f"   f={r['f'][i]/1e9:5.3f} GHz: Z0={np.real(r['z'][i]):6.2f} ohm (K-J {zkj:6.2f}), "
                       f"eps_eff={r['ee'][i]:.3f} (K-J {eekj:.3f}), |S11|={20*np.log10(abs(r['s11'][i])):6.1f} dB, "
                       f"|S21|={20*np.log10(abs(r['s21'][i])):6.2f} dB")
    i1 = np.argmin(abs(results["fine"]["f"] - 1e9))
    zc = np.real(results["coarse"]["z"][i1])
    zf = np.real(results["fine"]["z"][i1])
    out.append(f"Mesh convergence at 1 GHz: Z0 coarse {zc:.2f} -> fine {zf:.2f} ohm ({100*(zc-zf)/zf:+.2f} %); "
               f"vs H-J {100*(zf-zhj)/zhj:+.2f} %, vs FD {100*(zf-z_fd)/z_fd:+.2f} %")
    txt = "\n".join(out)
    print(txt)
    with open(os.path.join(HERE, "sim_openems_results.txt"), "a") as fh:
        fh.write(f"\n=== sim_openems_msl.py {time.strftime('%Y-%m-%d %H:%M')} ===\n{txt}\n")


if __name__ == "__main__":
    main()
