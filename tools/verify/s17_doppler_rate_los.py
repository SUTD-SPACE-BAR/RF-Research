#!/usr/bin/env python3
"""
s17_doppler_rate_los.py -- G-15-03 (W5-S17): range acceleration seen by a ground station,
including the line-of-sight rotation term v_perp^2/R, and its effect on the LoRa Doppler-rate
(per-packet drift) check.

Used by: kb/15-lora-ism-radios/lora-impairments-doppler-drift-timing.md (Level 3 "Doppler rate
seen from the ground"), kb/09-propagation-link-budget/multipath-fading-doppler.md and
kb/09-propagation-link-budget/satellite-links-doppler-tracking.md.

1. Symbolic derivation (sympy): r = |p - s|, rdot = v.rhat, rddot = a.rhat + (|v|^2 - rdot^2)/r
   = a.rhat + v_perp^2/r, checked by differentiating |p(t) - s| for a generic p(t).
2. Numeric check on the 10 km reference trajectory of tools/verify/proj_lora_link.py
   (11.1 g peak kinematic acceleration): numeric d2r/dt2 vs a.rhat + v_perp^2/r, for stations
   at 0.5 km and 2 km cross-range (and 5 km), split into the two terms.
3. Per-packet drift check (32-byte frame, CR4/5, 8-symbol preamble, explicit header, CRC, as in
   the 15 page table) at 433.125 and 868.125 MHz for those stations vs Semtech's BW/(3*2^SF)
   (x16 LDRO), with the 'acceleration-only' estimate shown for comparison.

Run: python3 tools/verify/s17_doppler_rate_los.py
"""
import os
import sys

import numpy as np
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import proj_lora_link as P  # noqa: E402

C = 299_792_458.0
G0 = 9.80665


def section1():
    print("=" * 90)
    print("1) Symbolic: second derivative of the range r(t) = |p(t) - s|")
    t = sp.symbols("t", real=True)
    x, y, z = (sp.Function(n)(t) for n in "xyz")
    r = sp.sqrt(x**2 + y**2 + z**2)            # station at origin, WLOG
    rdd = sp.diff(r, t, 2)
    v2 = sp.diff(x, t)**2 + sp.diff(y, t)**2 + sp.diff(z, t)**2
    rdot = (x*sp.diff(x, t) + y*sp.diff(y, t) + z*sp.diff(z, t)) / r
    a_dot_rhat = (x*sp.diff(x, t, 2) + y*sp.diff(y, t, 2) + z*sp.diff(z, t, 2)) / r
    claim = a_dot_rhat + (v2 - rdot**2) / r
    ok = sp.simplify(rdd - claim) == 0
    print(f"   d2r/dt2 == a.rhat + (|v|^2 - rdot^2)/r :  {ok}")
    print("   and |v|^2 - rdot^2 = v_perp^2 (component of v across the line of sight) => term >= 0 always")
    # straight-line constant-speed pass: rddot max = v^2/R0 at closest approach
    v, R0, tt = sp.symbols("v R0 tau", positive=True)
    rr = sp.sqrt(R0**2 + (v*tt)**2)
    print(f"   straight pass at speed v, miss distance R0: rddot(t=0) = {sp.simplify(sp.diff(rr, tt, 2).subs(tt, 0))}")
    assert ok


def section2_3():
    print("=" * 90)
    print("2) Reference 10 km trajectory (proj_lora_link.tune_apogee)")
    tr = P.tune_apogee(10000.0)
    t = tr["t"]
    asc = tr["phase"] <= 1
    burn = t < tr["tb"]
    p = np.stack([tr["x"], np.zeros_like(t), tr["z"]], axis=1)
    v = np.stack([tr["vx"], np.zeros_like(t), tr["vz"]], axis=1)
    a = np.stack([tr["ax"], np.zeros_like(t), tr["az"]], axis=1)
    amag = np.linalg.norm(a, axis=1)
    print(f"   peak kinematic |a| (ascent) {amag[asc].max()/G0:.1f} g; burnout {tr['tb']:.2f} s; "
          f"apogee {tr['z'].max():.0f} m at {tr['t_apo']:.1f} s")
    stations = {"0.5 km cross-range": np.array([0.0, 500.0, 2.0]),
                "2 km cross-range": np.array([0.0, 2000.0, 2.0]),
                "5 km cross-range": np.array([0.0, 5000.0, 2.0])}
    win = asc & (t > 0.5) & (t < tr["t_apo"] - 1.0)
    res = {}
    for name, s in stations.items():
        d = p - s
        r = np.linalg.norm(d, axis=1)
        rhat = d / r[:, None]
        rdot = np.sum(v * rhat, axis=1)
        a_r = np.sum(a * rhat, axis=1)
        vperp2 = np.sum(v * v, axis=1) - rdot**2
        rot = vperp2 / r
        rdd_an = a_r + rot
        rdd_num = np.gradient(np.gradient(r, t), t)
        # exclude +-50 ms around the acceleration steps (rail exit, burnout), where finite differences spike
        jerk = np.abs(np.gradient(amag, t))
        steps = t[jerk > 50 * G0]
        smooth = win.copy()
        for ts in steps:
            smooth &= np.abs(t - ts) > 0.05
        err = np.max(np.abs(rdd_num[smooth][5:-5] - rdd_an[smooth][5:-5]))
        i = np.argmax(np.abs(rdd_an[win]))
        idx = np.flatnonzero(win)[i]
        print(f"   Station {name}:")
        print(f"     numeric vs analytic rddot max diff {err:.3f} m/s^2 (away from the rail-exit/burnout steps)")
        print(f"     max |rddot| {np.abs(rdd_an[win]).max()/G0:5.1f} g at t = {t[idx]:5.2f} s "
              f"(a.rhat {a_r[idx]/G0:5.1f} g + vperp^2/R {rot[idx]/G0:5.1f} g; R {r[idx]/1e3:.2f} km, "
              f"v {np.linalg.norm(v[idx]):.0f} m/s)")
        print(f"     max |a.rhat| alone {np.abs(a_r[win]).max()/G0:5.1f} g; max vperp^2/R alone "
              f"{rot[win].max()/G0:5.1f} g (t = {t[win][np.argmax(rot[win])]:.2f} s); "
              f"in burn: max |rddot| {np.abs(rdd_an[burn & win]).max()/G0:.1f} g")
        res[name] = dict(rdot=rdot, rdd=rdd_an, a_r=a_r)

    print("=" * 90)
    print("3) Per-packet Doppler drift, 32-byte frame (CR4/5, 8-sym preamble, CRC), ascent windows")
    print("   'full' = drift of the true Doppler over the packet; 'acc-only' = a.rhat integrated")
    combos = [(7, 125e3), (8, 125e3), (9, 125e3), (10, 125e3), (12, 125e3),
              (9, 250e3), (10, 250e3), (11, 250e3), (9, 500e3), (11, 500e3)]
    for fc in (433.125e6, 868.125e6):
        print(f"   f = {fc/1e6:.3f} MHz")
        for sf, bw in combos:
            ldro = (2 ** sf / bw) >= 16.38e-3
            T = P.toa(32, sf, bw, ldro=ldro)
            lim = P.drift_limit_hz(sf, bw, ldro)
            sel = asc & (t < tr["t_apo"] - 1.0 - T)
            out = []
            for name in stations:
                g = res[name]
                full = P.packet_drift_series(t[sel], g["rdot"][sel], fc, T).max()
                # acceleration-only: integrate a.rhat over the window
                vr_acc = np.concatenate([[0.0], np.cumsum(0.5 * (g["a_r"][1:] + g["a_r"][:-1]) * np.diff(t))])
                acc = P.packet_drift_series(t[sel], vr_acc[sel], fc, T).max()
                out.append(f"{name.split()[0]} km: {full:7.1f} ({acc:7.1f}) {'FAIL' if full > lim else 'ok  '}")
            print(f"     SF{sf:2d}/{int(bw/1e3):3d}k{' LDRO' if ldro else '     '} ToA {T*1e3:7.1f} ms "
                  f"limit {lim:6.1f} Hz | " + " | ".join(out))


if __name__ == "__main__":
    section1()
    section2_3()
