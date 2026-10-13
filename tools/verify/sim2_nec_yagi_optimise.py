#!/usr/bin/env python3
# Runtime (W5-S11, 2026-10-14): ~141 s measured on a 10-core Apple-silicon Mac (132 s in W6-F5's timing run); single-threaded PyNEC, ~26 000 NEC evaluations; it exceeds the 120 s per-script budget
"""sim2_nec_yagi_optimise.py — optimiser-driven antenna design with PyNEC (NEC-2): a 3-element 433 MHz
Yagi for a hand-held ground-station antenna, designed by Nelder–Mead (5 random starts), differential
evolution and a particle-swarm optimiser, then a build-tolerance Monte Carlo. W5-S11, gap G-16-04.
Page: kb/16-simulation-tools/nec-antenna-modelling.md ("Example 5 — letting an optimiser design the Yagi").

Model: three straight 4 mm (a = 2 mm) aluminium-rod elements on a non-conducting boom, free space, 21
segments each (Delta/a ~ 8, thin kernel inside the rule), driven element fed at its centre segment, 50-ohm
direct feed (no matching network). Band: Singapore 433.05–434.79 MHz, evaluated at 433.05 / 433.92 / 434.79.

Variables x = [L_ref, L_drv, L_dir, s_ref, s_dir] (m): element lengths and reflector->driven, driven->director
spacings. Bounds: L_ref 0.47–0.53 lam, L_drv 0.42–0.50 lam, L_dir 0.40–0.48 lam, s 0.08–0.30 lam (boom <= 0.6 lam).
Objective (minimise):  J = -G_min + 1.0*max(0, 15 - FB_min) + 10*max(0, VSWR_max - 1.5)
  G_min = smallest boresight gain over the band (dBi), FB_min = smallest front-to-back (180 deg) over the band,
  VSWR_max = worst VSWR re 50 ohm over the band.

PRE-REGISTERED EXPECTATIONS (written 2026-10-13 before the first run; addenda only below)
  Y1  Unconstrained gain of a 3-element Yagi with boom <= 0.6 lam: 7.5–8.5 dBi. With F/B >= 15 dB and
      VSWR <= 1.5 on a direct 50-ohm feed, the optimum costs 0.5–1.5 dB: G_min 6.5–7.8 dBi.
  Y2  DE and PSO reach the same J within 0.1 dB; at least one of five Nelder–Mead starts ends >= 0.3 dB worse
      (local optima / penalty kinks).
  Y3  DE and PSO need >= 10x the function evaluations of one Nelder–Mead run.
  Y4  Build tolerance (lengths +-1 mm, spacings +-2 mm, uniform, 500 draws) on the DE optimum: 95th-percentile
      gain loss < 0.2 dB; worst-case VSWR stays < 2.0 in >= 95 % of builds.
  Y5  The KB's "3-element hand-held Yagi, 9 dBi" (08/antennas-on-rockets Example 1) is above what an optimiser
      finds for 3 elements even without constraints (cross-domain note, not an edit to 08).

ADDENDUM 1 (2026-10-13, after run 1): Y1 MISSED high on both counts (unconstrained 9.90 dBi = a superdirective
  close-spaced design, s_ref at the 0.08 lam bound, Z = 3.8 + j56 ohm; constrained 8.55 dBi), Y3 MISSED for PSO
  (5.5x, DE 29.6x), Y5 MISSED as worded (the unconstrained optimum exceeds 9 dBi). A post-hoc AGT + aluminium
  loss check was added to see whether the supergain survives real conductor loss. Expectations unchanged.

Run: python3 tools/verify/sim2_nec_yagi_optimise.py      (~1–3 min)  -> sim2_nec_yagi_results.txt
"""
import os
import time

import numpy as np
import PyNEC
from scipy.optimize import differential_evolution, minimize

HERE = os.path.dirname(os.path.abspath(__file__))
C0 = 299792458.0
F_BAND = (433.05e6, 433.92e6, 434.79e6)
LAM = C0 / 433.92e6
A_WIRE = 0.002
NSEG = 21
LB = np.array([0.47, 0.42, 0.40, 0.08, 0.08]) * LAM
UB = np.array([0.53, 0.50, 0.48, 0.30, 0.30]) * LAM
COUNT = {"n": 0}


def nec_eval(x, f):
    L_ref, L_drv, L_dir, s_ref, s_dir = x
    c = PyNEC.nec_context()
    g = c.get_geometry()
    for tag, (xp, L) in enumerate(((-s_ref, L_ref), (0.0, L_drv), (s_dir, L_dir)), start=1):
        g.wire(tag, NSEG, xp, 0, -L / 2, xp, 0, L / 2, A_WIRE, 1.0, 1.0)
    c.geometry_complete(0)
    c.gn_card(-1, 0, 0, 0, 0, 0, 0, 0)
    c.ex_card(0, 2, NSEG // 2 + 1, 0, 1.0, 0, 0, 0, 0, 0)
    c.fr_card(0, 1, f / 1e6, 0)
    c.rp_card(0, 1, 2, 0, 0, 0, 0, 90.0, 0.0, 0.0, 180.0, 0.0, 0.0)     # boresight (+x) and back (-x)
    gg = np.array(c.get_radiation_pattern(0).get_gain()).ravel()
    z = complex(c.get_input_parameters(0).get_impedance()[0])
    return float(gg[0]), float(gg[0] - gg[1]), z


def posthoc(x, sigma=None, f=433.92e6):
    """POST-HOC diagnostic (added after the first run): full-sphere average gain (AGT) and the effect of
    aluminium conductivity (LD 5, sigma = 3.5e7 S/m) on boresight gain."""
    L_ref, L_drv, L_dir, s_ref, s_dir = x
    c = PyNEC.nec_context()
    g = c.get_geometry()
    for tag, (xp, L) in enumerate(((-s_ref, L_ref), (0.0, L_drv), (s_dir, L_dir)), start=1):
        g.wire(tag, NSEG, xp, 0, -L / 2, xp, 0, L / 2, A_WIRE, 1.0, 1.0)
    c.geometry_complete(0)
    if sigma:
        c.ld_card(5, 0, 0, 0, sigma, 0, 0)
    c.gn_card(-1, 0, 0, 0, 0, 0, 0, 0)
    c.ex_card(0, 2, NSEG // 2 + 1, 0, 1.0, 0, 0, 0, 0, 0)
    c.fr_card(0, 1, f / 1e6, 0)
    c.rp_card(0, 91, 180, 0, 0, 0, 1, 0.0, 1.0, 2.0, 2.0, 0.0, 0.0)   # phi grid offset 1 deg from the beam
    rp = c.get_radiation_pattern(0)
    gdb = np.array(rp.get_gain())
    th = np.radians(np.array(rp.get_theta_angles()))
    G = 10 ** (gdb / 10)
    agt = np.trapezoid(G.sum(axis=1) * np.radians(2.0) * np.sin(th), th) / (4 * np.pi)
    return float(gdb.max()), float(agt)


def metrics(x):
    gs, fbs, vs = [], [], []
    for f in F_BAND:
        gdb, fb, z = nec_eval(x, f)
        gam = abs((z - 50) / (z + 50))
        gs.append(gdb)
        fbs.append(fb)
        vs.append((1 + gam) / (1 - gam))
    return min(gs), min(fbs), max(vs)


def objective(x, constrained=True):
    COUNT["n"] += 1
    x = np.clip(x, LB, UB)
    g, fb, v = metrics(x)
    if not constrained:
        return -g
    return -g + 1.0 * max(0.0, 15 - fb) + 10.0 * max(0.0, v - 1.5)


def pso(fun, n_particles=30, iters=120, seed=0, w=0.72, c1=1.49, c2=1.49):
    """Plain global-best PSO with inertia weight (Clerc-Kennedy constants), bounds by clipping."""
    rng = np.random.default_rng(seed)
    d = LB.size
    xs = LB + (UB - LB) * rng.random((n_particles, d))
    vs = 0.1 * (UB - LB) * (rng.random((n_particles, d)) - 0.5)
    pbest = xs.copy()
    pval = np.array([fun(x) for x in xs])
    gi = int(np.argmin(pval))
    gbest, gval = pbest[gi].copy(), pval[gi]
    for _ in range(iters):
        r1, r2 = rng.random((n_particles, d)), rng.random((n_particles, d))
        vs = w * vs + c1 * r1 * (pbest - xs) + c2 * r2 * (gbest - xs)
        xs = np.clip(xs + vs, LB, UB)
        val = np.array([fun(x) for x in xs])
        better = val < pval
        pbest[better], pval[better] = xs[better], val[better]
        gi = int(np.argmin(pval))
        if pval[gi] < gval:
            gbest, gval = pbest[gi].copy(), pval[gi]
    return gbest, gval


def describe(x):
    g, fb, v = metrics(x)
    _, _, z = nec_eval(x, 433.92e6)
    mm = 1e3 * np.asarray(x)
    return (f"L_ref {mm[0]:.1f}, L_drv {mm[1]:.1f}, L_dir {mm[2]:.1f} mm, s_ref {mm[3]:.1f}, s_dir {mm[4]:.1f} mm "
            f"(boom {(mm[3]+mm[4])/1e3/LAM:.3f} lam) | G_min {g:.2f} dBi, FB_min {fb:.1f} dB, VSWR_max {v:.2f}, "
            f"Z(433.92) {z.real:.1f}{z.imag:+.1f}j"), g, fb, v


def main():
    t0 = time.time()
    out = [f"3-element 433 MHz Yagi, 4 mm rod, {NSEG} seg/element, free space, 50-ohm direct feed; "
           f"band {F_BAND[0]/1e6:.2f}-{F_BAND[-1]/1e6:.2f} MHz"]
    rng = np.random.default_rng(42)

    # unconstrained gain (DE) for Y1
    COUNT["n"] = 0
    r = differential_evolution(lambda x: objective(x, False), list(zip(LB, UB)), seed=1, tol=1e-7, maxiter=300,
                               polish=True)
    d, g_unc, _, _ = describe(r.x)
    out.append(f"Unconstrained max-gain (DE, {COUNT['n']} evals): {d}")

    # constrained: Nelder–Mead x5, DE, PSO
    res = {}
    nm = []
    for k in range(5):
        x0 = LB + (UB - LB) * rng.random(LB.size)
        COUNT["n"] = 0
        rr = minimize(objective, x0, method="Nelder-Mead", options=dict(xatol=1e-5, fatol=1e-4, maxfev=4000))
        nm.append((rr.fun, COUNT["n"], np.clip(rr.x, LB, UB)))
        out.append(f"Nelder-Mead start {k+1}: J {rr.fun:.3f}, {COUNT['n']} evals | {describe(np.clip(rr.x, LB, UB))[0]}")
    COUNT["n"] = 0
    rd = differential_evolution(objective, list(zip(LB, UB)), seed=2, tol=1e-7, maxiter=300, polish=True)
    res["DE"] = (rd.fun, COUNT["n"], rd.x)
    out.append(f"Differential evolution: J {rd.fun:.3f}, {COUNT['n']} evals | {describe(rd.x)[0]}")
    COUNT["n"] = 0
    xp, jp = pso(objective, seed=3)
    res["PSO"] = (jp, COUNT["n"], xp)
    out.append(f"Particle swarm: J {jp:.3f}, {COUNT['n']} evals | {describe(xp)[0]}")

    d, g_c, fb_c, v_c = describe(rd.x)
    j_best = min(rd.fun, jp)
    nm_j = np.array([a for a, _, _ in nm])
    nm_ev = np.mean([b for _, b, _ in nm])
    out.append("--- pre-registered checks ---")
    out.append(f"Y1 {'PASS' if 7.5 <= g_unc <= 8.5 else 'MISS'}: unconstrained G {g_unc:.2f} dBi (expect 7.5-8.5); "
               f"{'PASS' if 6.5 <= g_c <= 7.8 else 'MISS'}: constrained G_min {g_c:.2f} dBi (expect 6.5-7.8), "
               f"cost of constraints {g_unc-g_c:.2f} dB")
    out.append(f"Y2 {'PASS' if abs(rd.fun-jp) <= 0.1 and np.any(nm_j - j_best >= 0.3) else 'MISS'}: DE J {rd.fun:.3f} "
               f"vs PSO {jp:.3f}; NM J = {', '.join(f'{v:.3f}' for v in nm_j)} "
               f"({int(np.sum(nm_j - j_best >= 0.3))} of 5 starts >= 0.3 worse)")
    ratio_de, ratio_pso = res["DE"][1] / nm_ev, res["PSO"][1] / nm_ev
    out.append(f"Y3 {'PASS' if min(ratio_de, ratio_pso) >= 10 else 'MISS'}: evals DE {res['DE'][1]}, PSO "
               f"{res['PSO'][1]}, NM mean {nm_ev:.0f} (ratios {ratio_de:.1f}x, {ratio_pso:.1f}x)")

    # build tolerance
    xs = rd.x
    tol = np.array([1e-3, 1e-3, 1e-3, 2e-3, 2e-3])
    gl, vv = [], []
    for _ in range(500):
        xt = xs + tol * (2 * rng.random(5) - 1)
        g, fb, v = metrics(xt)
        gl.append(g_c - g)
        vv.append(v)
    gl, vv = np.array(gl), np.array(vv)
    out.append(f"Y4 {'PASS' if np.percentile(gl, 95) < 0.2 and np.mean(vv < 2.0) >= 0.95 else 'MISS'}: 500 builds "
               f"(+-1 mm lengths, +-2 mm spacings): gain loss p95 {np.percentile(gl, 95):.3f} dB (max "
               f"{gl.max():.3f}); VSWR_max median {np.median(vv):.2f}, p95 {np.percentile(vv, 95):.2f}, "
               f"< 2.0 in {100*np.mean(vv < 2.0):.1f} % of builds")
    out.append(f"Y5 {'PASS' if g_unc < 9.0 else 'MISS'}: 3-element optimum {g_unc:.2f} dBi vs the 9 dBi assumed in "
               f"08/antennas-on-rockets Example 1 (9 dBi minus optimum = {9.0-g_unc:+.2f} dB; practical constrained optimum {g_c:.2f} dBi)")
    out.append("--- POST-HOC diagnostics (added after the first run; not pre-registered) ---")
    for name, xx in (("unconstrained optimum", r.x), ("constrained DE optimum", rd.x)):
        g0, a0 = posthoc(xx)
        g1, a1 = posthoc(xx, sigma=3.5e7)
        out.append(f"{name}: lossless G {g0:.2f} dBi, AGT {a0:.3f}; aluminium (3.5e7 S/m) G {g1:.2f} dBi "
                   f"(AGT = efficiency {a1:.3f}, {10*np.log10(a1):.2f} dB)")
    out.append(f"runtime {time.time()-t0:.0f} s")
    txt = "\n".join(out)
    print(txt)
    with open(os.path.join(HERE, "sim2_nec_yagi_results.txt"), "w") as fh:
        fh.write(f"=== sim2_nec_yagi_optimise.py {time.strftime('%Y-%m-%d %H:%M')} (PyNEC {PyNEC.__name__}) ===\n{txt}\n")


if __name__ == "__main__":
    main()
