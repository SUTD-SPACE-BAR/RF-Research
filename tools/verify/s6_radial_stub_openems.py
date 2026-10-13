#!/usr/bin/env python3
"""s6_radial_stub_openems.py — openEMS (FDTD) check of the radial-stub model in s6_radial_stub.py
(task W5-S6, gap G-03-02; page kb/03-transmission-lines-matching/input-impedance-stubs-quarter-wave.md).

Structure: a 0.8 mm feed strip (~90 ohm) on h = 1.43 mm, er = 4.5 (JLC0216A core, lossless, PEC strip of
zero thickness) runs from the port to x = 0, where a 60-degree sector (r_i = 0.8 mm, so the chord at r_i
is the feed width; r_o = 9.70 mm) opens in +x.  Method as in e11_discontinuities_openems.py: a second run
on the identical mesh continues the feed into the PML (matched through line).  Then
    Gamma_meas = (V_stub - V_thru) / V_thru,  Gamma_0 = Gamma_meas * exp(+2j beta d),
    Z_in(x = 0) = Z_line (1 + Gamma_0)/(1 - Gamma_0)
with beta and Z_line from the through run.  Compared with model variants A-D of s6_radial_stub.py.

PRE-REGISTERED (printed by s6_radial_stub.py before this script was first run, 2026-10-13):
  model A 2.425 GHz, B 2.669 GHz, C 2.463 GHz, D 2.302 GHz;
  expect openEMS f_res within +-4 % of model C; A high by > 5 %; |Z_in| at 1.5 GHz within 15 % of model C.
  (NOTE: the 'A high by > 5 %' line was written carelessly — model A (2.425) is BELOW model C (2.463);
  it is kept as written and scored as stated.)

Run:  ~/opt/openEMS/venv/bin/python tools/verify/s6_radial_stub_openems.py      (~5-15 min)
Output: tools/verify/s6_radial_stub_openems_results.txt
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
from s6_radial_stub import zin_variant             # noqa: E402

H, ER = 1.43, 4.5
WF = 0.8
ALPHA = np.deg2rad(60.0)
RI = WF / (2 * np.sin(ALPHA / 2))
RO = 9.70
F_LO, F_HI = 0.5e9, 5.0e9
F = np.linspace(F_LO, F_HI, 181)
BC = ["PML_8", "PML_8", "PML_8", "PML_8", "PEC", "PML_8"]
OUT = os.path.join(HERE, "s6_radial_stub_openems_results.txt")


def _thirds(edge, fine, metal_side):
    s = 1.0 if metal_side < 0 else -1.0
    return [edge - s * fine / 3.0, edge + s * 2.0 * fine / 3.0]


def run(through, fine_div=6, sec_cell=0.25, tag="rs", shape="sector"):
    sim_path = os.path.join(tempfile.gettempdir(), f"rfkb_s6_{tag}_{'thru' if through else 'stub'}")
    FDTD = openEMS(NrTS=200000, EndCriteria=1e-4)
    FDTD.SetGaussExcite(0.5 * (F_LO + F_HI), 0.5 * (F_HI - F_LO))
    FDTD.SetBoundaryCond(BC)
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(1e-3)
    lam = C0 / (F_HI * np.sqrt(ER)) * 1e3
    res = lam / 30
    fine = WF / fine_div
    x0, xmax, xmeas = -50.0, RO + 12.0, -20.0
    xa = -RI * np.cos(ALPHA / 2)                    # sector apex (chord at r_i lies on x = 0)
    ymax_sec = RO * np.sin(ALPHA / 2)
    # x: fine at x = 0 junction, sector region at sec_cell, graded outward
    mesh.AddLine("x", np.arange(0.0, RO + 0.5, sec_cell).tolist() + [-1.0, -0.5])
    mesh.AddLine("x", [x0, xmax, xmeas])
    mesh.SmoothMeshLines("x", res, 1.3)
    ylines = [0.0] + _thirds(WF / 2, fine, -1) + _thirds(-WF / 2, fine, +1)
    ylines += np.arange(-ymax_sec - 0.5, ymax_sec + 0.5, sec_cell).tolist()
    mesh.AddLine("y", ylines)
    mesh.SmoothMeshLines("y", fine, 1.3)
    mesh.AddLine("y", [-25.0, 25.0])
    mesh.SmoothMeshLines("y", res, 1.3)
    mesh.AddLine("z", np.linspace(0, H, 5).tolist() + [20.0])
    mesh.SmoothMeshLines("z", res, 1.3)

    sub = CSX.AddMaterial("FR4", epsilon=ER)
    sub.AddBox([x0, -25.0, 0], [xmax, 25.0, H], priority=0)
    pec = CSX.AddMetal("strip")
    port = FDTD.AddMSLPort(1, pec, [x0, -WF / 2, H], [xmax if through else 0.0, WF / 2, 0], "x", "z",
                           excite=-1, FeedShift=10 * res, MeasPlaneShift=xmeas - x0, priority=10)
    if not through and shape == "line":
        # control case: the feed simply continues as a uniform open stub of length 12 mm
        pec.AddBox([0.0, -WF / 2, H], [12.0, WF / 2, H], priority=5)
    elif not through:
        th = np.linspace(-ALPHA / 2, ALPHA / 2, 61)
        arc = [(xa + RO * np.cos(t), RO * np.sin(t)) for t in th]
        pts = [(0.0, -WF / 2)] + arc + [(0.0, WF / 2)]
        pec.AddPolygon(np.array(pts).T, "z", H, priority=5)
    d = 0.0 - (x0 + port.measplane_shift)
    ncells = int(np.prod([len(mesh.GetLines(a)) for a in "xyz"]))
    t0 = time.time()
    FDTD.Run(sim_path, cleanup=True, verbose=0)
    dt = time.time() - t0
    port.CalcPort(sim_path, F)
    return dict(u=port.uf_tot.copy(), beta=np.real(port.beta.copy()), zl=np.real(port.Z_ref.copy()),
                d=d, ncells=ncells, time=dt)


def analyse(rs, rt):
    beta, d = rt["beta"], rs["d"]
    gam = (rs["u"] - rt["u"]) / rt["u"]
    g0 = gam * np.exp(2j * beta * d * 1e-3)
    return rt["zl"] * (1 + g0) / (1 - g0)


def fzero(f, x):
    i = np.where((x[:-1] < 0) & (x[1:] > 0))[0]
    if len(i) == 0:
        return np.nan
    i = i[0]
    return f[i] - x[i] * (f[i + 1] - f[i]) / (x[i + 1] - x[i])


def main():
    lines = [f"\n=== s6_radial_stub_openems run {time.strftime('%Y-%m-%d %H:%M')}"]
    results = {}
    for tag, kw in (("coarse", dict(fine_div=4, sec_cell=0.4)), ("fine", dict(fine_div=6, sec_cell=0.25))):
        rs = run(False, tag=tag, **kw)
        rt = run(True, tag=tag, **kw)
        Z = analyse(rs, rt)
        fr = fzero(F, Z.imag)
        results[tag] = (Z, fr)
        lines.append(f"{tag}: cells {rs['ncells']}, time {rs['time'] + rt['time']:.0f} s, Z_line(1 GHz) "
                     f"{np.interp(1e9, F, rt['zl']):.1f} ohm, eeff(1 GHz) "
                     f"{np.interp(1e9, F, (rt['beta'] * C0 / (2 * np.pi * F)) ** 2):.3f}, f_res {fr/1e9:.4f} GHz")
        print(lines[-1], flush=True)
    Z, fr = results["fine"]
    fr_c = results["coarse"][1]
    lines.append(f"mesh change in f_res coarse->fine: {(fr/fr_c - 1)*100:+.2f} %")
    for name in "ABCD":
        zm = np.array([zin_variant(f, RI * 1e-3, RO * 1e-3, ALPHA, H * 1e-3, ER, name) for f in F])
        frm = fzero(F, zm.imag)
        z15 = abs(np.interp(1.5e9, F, zm.imag))
        lines.append(f"model {name}: f_res {frm/1e9:.4f} GHz ({(frm/fr-1)*100:+.1f} % vs openEMS); "
                     f"|X(1.5 GHz)| {z15:.1f} ohm vs openEMS {abs(np.interp(1.5e9, F, Z.imag)):.1f} ohm")
    for fq in (1.0e9, 1.5e9, 2.0e9, 2.45e9, 3.0e9, 4.0e9):
        lines.append(f"  openEMS Z_in({fq/1e9:.2f} GHz) = {np.interp(fq, F, Z.real):7.2f} {np.interp(fq, F, Z.imag):+8.2f}j ohm")
    # scoring of the pre-registered expectations
    frC = fzero(F, np.array([zin_variant(f, RI*1e-3, RO*1e-3, ALPHA, H*1e-3, ER, 'C') for f in F]).imag)
    frA = fzero(F, np.array([zin_variant(f, RI*1e-3, RO*1e-3, ALPHA, H*1e-3, ER, 'A') for f in F]).imag)
    xC = abs(np.interp(1.5e9, F, np.array([zin_variant(f, RI*1e-3, RO*1e-3, ALPHA, H*1e-3, ER, 'C') for f in F]).imag))
    lines.append(f"PRE-REG 1 (f_res within +-4 % of C): {'MET' if abs(fr/frC-1) < 0.04 else 'MISSED'} ({(frC/fr-1)*100:+.1f} %)")
    lines.append(f"PRE-REG 2 (A high by > 5 %): {'MET' if frA/fr - 1 > 0.05 else 'MISSED'} ({(frA/fr-1)*100:+.1f} %)")
    lines.append(f"PRE-REG 3 (|X| at 1.5 GHz within 15 % of C): "
                 f"{'MET' if abs(xC/abs(np.interp(1.5e9, F, Z.imag))-1) < 0.15 else 'MISSED'}")
    with open(OUT, "a") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    np.savez(os.path.join(HERE, "data", "s6_radial_stub_openems.npz"), f=F, Z=Z)


if __name__ == "__main__":
    main()
