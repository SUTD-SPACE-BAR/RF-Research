#!/usr/bin/env python3
"""s6_trace_heating.py — RF power handling of PCB traces (task W5-S6, gaps G-03-04 and G-03-03) for
kb/03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md.

1. Line voltage/current at 2 W (E22-400T33D), 10 W and 25 W in 50 ohm, matched and at VSWR 3.
2. Loss split on the two canonical JLC stackups (KB widths: 0.359 mm on JLC04161H-7628, 2.692 mm on
   JLC0216A): conductor and dielectric heat per metre p' = 2 alpha P.
3. RF vs DC resistance per metre: R'_RF = 2 Z0 alpha_c  vs  R'_DC = rho/(W t).  -> the DC-equivalent current
   that a DC trace-heating rule (IPC-2221 / IPC-2152) must be fed with:  I_eq = sqrt(p'/R'_DC).
4. Temperature rise: (a) analytic two-resistor model (trace->plane through the dielectric, board->air as an
   efficient fin), (b) independent 2-D finite-volume conduction solver of the board cross-section with
   convection on both faces; (c) IPC-2221 external-layer formula fed with I_eq.
5. Peak voltage vs the Paschen minimum (air, any pressure).
6. Ground-plane sheet/surface resistance (G-03-03 numbers).
"""
import os
import sys

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tline_microstrip import ms_hj, ms_loss  # noqa: E402

MU0 = 4e-7 * np.pi
SIG = 5.80e7            # IACS (canonical)
RHO = 1 / SIG
K_CU, K_FR4 = 385.0, 0.30
H_CONV = 12.0           # W/m^2K per face: still-air natural convection ~6-8 + linearised radiation ~5 (assumption)
BOARD_W = 50e-3         # board width across the trace (m); edges adiabatic
PASS = []


def check(name, cond, detail=""):
    PASS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


STACKS = {
    # name: (W, h_to_ref, er, t_trace, layers bottom->top as (thickness, k, kind))
    "JLC04161H-7628 4-layer, 0.359 mm": dict(
        W=0.359e-3, h=0.2104e-3, er=4.4, t=35e-6,
        layers=[(35e-6, K_CU, "plane"), (0.2104e-3, K_FR4, "diel"), (17.5e-6, K_CU, "plane"),
                (1.065e-3, K_FR4, "diel"), (17.5e-6, K_CU, "plane"), (0.2104e-3, K_FR4, "diel_rf")]),
    "JLC0216A 2-layer, 2.692 mm": dict(
        W=2.692e-3, h=1.43e-3, er=4.5, t=30e-6,
        layers=[(30e-6, K_CU, "plane"), (1.43e-3, K_FR4, "diel_rf")]),
}


def fd_thermal(stack, pc, pd, n_trace=12):
    """2-D steady conduction, finite volumes on a graded grid. pc: W/m in the trace; pd: W/m in the
    dielectric directly below the trace within |x| < W/2 + h (the region holding most of the field energy).
    Convection H_CONV on top (board + trace surface) and bottom faces; ambient 0. Returns peak trace rise."""
    W, t = stack["W"], stack["t"]
    hrf = stack["h"]
    # z grid: each layer subdivided, then trace on top
    zs = [0.0]
    zkind = []
    for (th, k, kind) in stack["layers"]:
        n = 3 if k == K_CU else 8
        for i in range(n):
            zs.append(zs[-1] + th / n)
            zkind.append((k, kind))
    z_top_board = zs[-1]
    for i in range(3):
        zs.append(zs[-1] + t / 3)
        zkind.append((None, "trace"))
    dz = np.diff(zs)
    # x grid: symmetric, fine in the trace, graded out to BOARD_W/2 (half model, x >= 0, symmetry at 0)
    xs = list(np.linspace(0, W / 2, n_trace + 1))
    dx = W / 2 / n_trace
    while xs[-1] < BOARD_W / 2:
        dx = min(dx * 1.15, 1e-3)
        xs.append(min(xs[-1] + dx, BOARD_W / 2))
    xs = np.array(xs)
    ddx = np.diff(xs)
    xc = 0.5 * (xs[:-1] + xs[1:])
    nx, nz = len(ddx), len(dz)
    k = np.zeros((nx, nz))
    q = np.zeros((nx, nz))
    in_trace = xc < W / 2
    for j, (kk, kind) in enumerate(zkind):
        if kind == "trace":
            k[:, j] = np.where(in_trace, K_CU, 0.026)   # air beside the trace (conduction only, tiny)
        else:
            k[:, j] = kk
    # heat sources (half model gets half the heat)
    jt = [j for j, (_, kind) in enumerate(zkind) if kind == "trace"]
    area_t = np.sum(ddx[in_trace]) * np.sum(dz[jt])
    for j in jt:
        q[in_trace, j] = (pc / 2) / area_t
    jd = [j for j, (_, kind) in enumerate(zkind) if kind == "diel_rf"]
    reg = xc < W / 2 + hrf
    area_d = np.sum(ddx[reg]) * np.sum(dz[jd])
    for j in jd:
        q[reg, j] += (pd / 2) / area_d
    idx = np.arange(nx * nz).reshape(nx, nz)
    rows, cols, vals = [], [], []
    diag = np.zeros(nx * nz)
    b = (q * ddx[:, None] * dz[None, :]).ravel()

    def link(a, c, g):
        rows.extend([a, c]); cols.extend([c, a]); vals.extend([-g, -g])
        diag[a] += g; diag[c] += g

    for i in range(nx - 1):
        for j in range(nz):
            r = ddx[i] / 2 / k[i, j] + ddx[i + 1] / 2 / k[i + 1, j]
            link(idx[i, j], idx[i + 1, j], dz[j] / r)
    for i in range(nx):
        for j in range(nz - 1):
            r = dz[j] / 2 / k[i, j] + dz[j + 1] / 2 / k[i, j + 1]
            link(idx[i, j], idx[i, j + 1], ddx[i] / r)
    # convection: bottom face of row 0; top face = top of trace cells where trace, else top of board
    jtop_board = len(zkind) - 4
    for i in range(nx):
        diag[idx[i, 0]] += H_CONV * ddx[i] / (1 + H_CONV * dz[0] / 2 / k[i, 0])
        jt_i = nz - 1 if in_trace[i] else jtop_board
        diag[idx[i, jt_i]] += H_CONV * ddx[i] / (1 + H_CONV * dz[jt_i] / 2 / k[i, jt_i])
    A = sp.coo_matrix((vals + list(diag), (rows + list(range(nx * nz)), cols + list(range(nx * nz)))),
                      shape=(nx * nz, nx * nz)).tocsr()
    T = spla.spsolve(A.tocsc(), b).reshape(nx, nz)
    return T[0, jt].max(), T[:, 0].max(), T[-1, 0]


def analytic(stack, pc, pd):
    W, h = stack["W"], stack["h"]
    r_diel = h / (K_FR4 * (W + h))                     # trace -> plane, 45-deg spreading in the dielectric
    sum_kt = sum(th * kk for (th, kk, _) in stack["layers"])
    m = np.sqrt(2 * H_CONV / sum_kt)                   # board as a fin, both faces convecting
    L = BOARD_W / 2
    g_board = 2 * np.sqrt(2 * H_CONV * sum_kt) * np.tanh(m * L)   # two fins (either side of the trace)
    # conductor heat crosses the whole dielectric; dielectric heat is generated through its depth -> ~half
    return pc * (r_diel + 1 / g_board) + pd * (r_diel / 2 + 1 / g_board), r_diel, 1 / g_board


def ipc2221_dT(I, W, t):
    A_mil2 = (W / 25.4e-6) * (t / 25.4e-6)
    return (I / (0.048 * A_mil2 ** 0.725)) ** (1 / 0.44)


def main():
    print("=== 1. line voltage and current, 50 ohm")
    for P in (2.0, 10.0, 25.0):
        Irms = np.sqrt(P / 50); Vpk = np.sqrt(2 * P * 50)
        print(f"   {P:4.0f} W: I_rms {Irms:.3f} A, V_peak {Vpk:.1f} V; at VSWR 3 maxima "
              f"V_peak {Vpk*1.5:.1f} V, I_rms {Irms*1.5:.3f} A")
    check("2 W in 50 ohm = 14.1 V peak, 0.20 A rms", abs(np.sqrt(200) - 14.14) < 0.01)

    print("=== 2-4. loss split, RF/DC resistance, temperature rise (infinitely long trace, 50 mm wide board)")
    summary = {}
    for name, st in STACKS.items():
        z0, ee = ms_hj(st["W"], st["h"], st["er"], st["t"])
        print(f" -- {name}: Z0 {z0:.1f} ohm (H-J, bare, t {st['t']*1e6:.0f} um), eeff {ee:.2f}")
        Rdc = RHO / (st["W"] * st["t"])
        for f in (433e6, 915e6, 2.45e9):
            ac, ad = ms_loss(st["W"], st["h"], st["er"], 0.02, f, t=st["t"], rough=1e-6)
            acn, adn = ac / 8.686, ad / 8.686                      # Np/m
            Rrf = 2 * z0 * acn
            for P in (2.0, 25.0):
                pc, pd = 2 * acn * P, 2 * adn * P
                dT_fd, dT_plane, dT_edge = fd_thermal(st, pc, pd)
                dT_an, rd, rb = analytic(st, pc, pd)
                Ieq = np.sqrt((pc + pd) / Rdc)
                dT_ipc = ipc2221_dT(Ieq, st["W"], st["t"])
                summary[(name, f, P)] = (dT_fd, dT_an, dT_ipc)
                print(f"   {f/1e6:6.0f} MHz {P:4.0f} W: alpha_c {ac:5.2f} + alpha_d {ad:5.2f} dB/m -> "
                      f"p' {pc:6.2f} + {pd:6.2f} W/m; R'_RF/R'_DC = {Rrf:5.1f}/{Rdc:5.2f} = {Rrf/Rdc:4.1f}; "
                      f"I_rms {np.sqrt(P/50):.2f} A vs I_eq(DC) {Ieq:.2f} A | dT: FD {dT_fd:6.1f} K, "
                      f"analytic {dT_an:6.1f} K, IPC-2221(I_eq) {dT_ipc:6.1f} K")
        print(f"   analytic resistances: trace->plane {rd:.2f} K m/W, board->air {rb:.2f} K m/W")
    k7 = "JLC04161H-7628 4-layer, 0.359 mm"
    k2 = "JLC0216A 2-layer, 2.692 mm"
    fd_, an_, ipc_ = summary[(k7, 433e6, 2.0)]
    check("E22 2 W at 433 MHz on JLC-7628: long-line rise < 5 K (FD)", fd_ < 5, f"{fd_:.2f} K")
    worst = max(abs(v[1] / v[0] - 1) for v in summary.values())
    check("analytic two-resistor model within 25 % of the FD solver (all cases)", worst < 0.25, f"worst {worst*100:.0f} %")
    r7 = summary[(k7, 915e6, 2.0)]
    check("IPC-2221 fed with the DC-equivalent current is conservative by > 2x for a trace 0.21 mm above a plane",
          r7[2] / r7[0] > 2, f"{r7[2]/r7[0]:.1f}x")
    fd25, _, _ = summary[(k7, 2.45e9, 25.0)]
    check("25 W at 2.45 GHz on the thin-prepreg line: long-line rise > 50 K (a real limit)", fd25 > 50, f"{fd25:.0f} K")
    check("the 2-layer wide trace runs cooler than the 4-layer narrow one at 25 W, 915 MHz",
          summary[(k2, 915e6, 25.0)][0] < summary[(k7, 915e6, 25.0)][0])
    # dissipation in a short trace
    print("=== short traces: power dissipated = P (1 - 10^(-A/10))")
    for (name, f, L, P) in ((k7, 433e6, 0.03, 2.0), (k7, 2.45e9, 0.05, 25.0), (k2, 915e6, 0.05, 25.0)):
        st = STACKS[name]
        ac, ad = ms_loss(st["W"], st["h"], st["er"], 0.02, f, t=st["t"], rough=1e-6)
        A = (ac + ad) * L
        print(f"   {name}, {f/1e6:.0f} MHz, {L*100:.0f} cm at {P:.0f} W: loss {A:.3f} dB, "
              f"dissipated {P*(1-10**(-A/10))*1e3:.0f} mW")

    print("=== 5. peak voltage vs Paschen minimum (air, ~327 V)")
    for P, vswr in ((2, 1), (25, 1), (25, 3), (100, 3)):
        g = (vswr - 1) / (vswr + 1)
        vpk = np.sqrt(2 * P * 50) * (1 + g)
        print(f"   {P:4d} W, VSWR {vswr}: V_peak max {vpk:6.1f} V  ({'below' if vpk < 327 else 'ABOVE'} 327 V)")
    pmax = 327 ** 2 / (2 * 50)
    print(f"   matched 50-ohm power at 327 V peak: {pmax:.0f} W (at VSWR 3: {pmax/1.5**2:.0f} W)")
    check("25 W even at VSWR 3 stays < 1/4 of the Paschen minimum", np.sqrt(2500) * 1.5 < 327 / 4)

    print("=== 6. ground-plane resistance (G-03-03)")
    for t in (17.5e-6, 35e-6):
        print(f"   DC sheet resistance, {t*1e6:.1f} um Cu: {RHO/t*1e3:.3f} mOhm/sq")
    for f in (433e6, 915e6, 2.45e9):
        Rs = np.sqrt(np.pi * f * MU0 / SIG)
        print(f"   surface resistance at {f/1e6:6.0f} MHz: {Rs*1e3:.2f} mOhm/sq (|Zs| = {Rs*np.sqrt(2)*1e3:.2f} mOhm/sq)")
    check("surface resistance at 433 MHz ~ 5.4 mOhm/sq", abs(np.sqrt(np.pi * 433e6 * MU0 / SIG) * 1e3 - 5.43) < 0.05)
    print("\nALL PASS" if all(PASS) else "\nSOME CHECKS FAILED")


if __name__ == "__main__":
    main()
