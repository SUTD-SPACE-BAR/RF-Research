#!/usr/bin/env python3
"""
s17_satellite_pass.py -- G-09-01 (W5-S17): numbers for
kb/09-propagation-link-budget/satellite-links-doppler-tracking.md

Sections
 1. Orbit classes (LEO 400/525/820 km, MEO GPS, GEO): period, speed, mean motion, slant range and
    Earth-central angle vs elevation, footprint, FSPL, max range rate (Doppler) and the closed-form
    upper bound v*R/(R+h).
 2. Pass simulation from Singapore (1.3521 N, 103.8198 E, 15 m, WGS-84) for an illustrative
    525 km sun-synchronous orbit (circular, two-body + J2 secular RAAN drift; NOT SGP4 - real
    tracking uses SGP4 on a current TLE, e.g. in Gpredict). 48 h propagated at 1 s; passes listed.
    For the highest pass and a ~30 deg pass: AOS/LOS (0 and 10 deg), duration, azimuths, min range,
    Doppler at 437 MHz, Doppler rate (analytic R'' = a_rel.rhat + v_perp^2/R vs finite difference),
    azimuth/elevation rates (rotator keyhole).
 3. Same for an 820 km SSO (Meteor-M class) at 137.9 MHz.
 4. Doppler on linear transponders (V/U inverting vs non-inverting) and 'full Doppler' uplink.
 5. Link budgets:  a) 437 MHz CubeSat 9k6 GMSK (1 W, 0 dBi) into a 12 dBic crossed Yagi + LNA and
    into an omni;  b) TinyGS-style LoRa SF10/125 at 22 dBm into a 2 dBi ground plane, plus the
    per-packet Doppler-drift check SF7..SF12 over the highest pass;  c) Meteor-M LRPT 137.9 MHz:
    G/T of a QFH vs site noise (P.372 man-made lines are valid here, < 250 MHz) and the EIRP
    needed to close;  d) GEO visibility from Singapore (QO-100 at 25.9 E) and FSPL.
Each section prints CHECK lines; the final line is ALL PASS or lists failures.
Run: python3 tools/verify/s17_satellite_pass.py
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from rfcalc.lora import time_on_air, sensitivity_dbm  # noqa: E402

C = 299_792_458.0
MU = 3.986004418e14
RE = 6378.137e3
F_WGS = 1 / 298.257223563
J2 = 1.08262668e-3
WE = 7.2921150e-5
K_DB = -228.6                     # 10 log10 k [dBW/K/Hz]
STN = dict(lat=1.3521, lon=103.8198, h=15.0)   # Singapore
FAIL = []


def check(name, cond):
    print(f"   CHECK {name}: {'PASS' if cond else 'FAIL'}")
    if not cond:
        FAIL.append(name)


def fspl(f_hz, d_m):
    return 20 * math.log10(4 * math.pi * d_m * f_hz / C)


def slant(h, el_deg, R=RE):
    e = math.radians(el_deg)
    return math.sqrt((R + h) ** 2 - (R * math.cos(e)) ** 2) - R * math.sin(e)


def central(h, el_deg, R=RE):
    e = math.radians(el_deg)
    return math.degrees(math.acos(R * math.cos(e) / (R + h)) - e)


# --------------------------------------------------------------------------- 1
def section1():
    print("=" * 96)
    print("1) Orbit classes")
    orbits = [("LEO ISS-like", 420e3), ("LEO CubeSat", 525e3), ("LEO Meteor-M", 820e3),
              ("MEO GPS", 20180e3), ("GEO", 35786e3)]
    for name, h in orbits:
        a = RE + h
        T = 2 * math.pi * math.sqrt(a ** 3 / MU)
        v = math.sqrt(MU / a)
        rmax0, rmax10 = slant(h, 0), slant(h, 10)
        lam0, lam10 = central(h, 0), central(h, 10)
        vr_bound = v * RE / a        # max range rate (orbit plane through observer, no Earth rotation)
        print(f"   {name:13s} h {h/1e3:7.0f} km: T {T/60:7.1f} min ({86400/T:5.2f} rev/day), v {v/1e3:5.2f} km/s; "
              f"slant @90/@10/@0 deg {h/1e3:6.0f}/{rmax10/1e3:6.0f}/{rmax0/1e3:6.0f} km; "
              f"footprint half-angle @0/@10 {lam0:5.1f}/{lam10:5.1f} deg; |rdot|max <= {vr_bound/1e3:5.2f} km/s")
        flist = {"MEO GPS": [(1575.42e6, "1575.42")], "GEO": [(10.489e9, "10489")]}.get(
            name, [(137.9e6, "137.9"), (437e6, "437")])
        for f, lab in flist:
            dop = "n/a (co-rotating)" if name == "GEO" else f"<= {f*vr_bound/C/1e3:6.2f} kHz"
            print(f"        FSPL @{lab} MHz: zenith {fspl(f, h):6.1f} dB, 10 deg {fspl(f, rmax10):6.1f} dB, "
                  f"horizon {fspl(f, rmax0):6.1f} dB; max Doppler {dop}")
        if name == "LEO CubeSat":
            check("525 km period ~95 min", 94 < T / 60 < 96)
            lam = math.radians(lam10)
            d_cos = math.sqrt(RE**2 + a**2 - 2 * RE * a * math.cos(lam))      # law of cosines cross-check
            check("525 km slant at 10 deg: closed form = law of cosines (1756 km)", abs(d_cos - rmax10) < 1.0 and 1.70e6 < rmax10 < 1.80e6)
        if name == "GEO":
            check("GEO period = sidereal day", abs(T - 86164.1) < 5)


# --------------------------------------------------------------------------- 2/3 propagation
def stn_ecef():
    lat, lon = math.radians(STN["lat"]), math.radians(STN["lon"])
    e2 = F_WGS * (2 - F_WGS)
    N = RE / math.sqrt(1 - e2 * math.sin(lat) ** 2)
    x = (N + STN["h"]) * math.cos(lat) * math.cos(lon)
    y = (N + STN["h"]) * math.cos(lat) * math.sin(lon)
    z = (N * (1 - e2) + STN["h"]) * math.sin(lat)
    return np.array([x, y, z]), lat, lon


def sso_incl(h):
    a = RE + h
    n = math.sqrt(MU / a ** 3)
    raan_dot = 2 * math.pi / (365.2422 * 86400)
    cosi = -raan_dot / (1.5 * n * J2 * (RE / a) ** 2)
    return math.degrees(math.acos(cosi))


def propagate(h, inc_deg, raan0_deg, u0_deg, t):
    """Circular orbit, J2 secular RAAN drift. Returns ECEF position, velocity, acceleration (rotating frame
    quantities computed from ECI then rotated; relative kinematics done in ECI)."""
    a = RE + h
    n = math.sqrt(MU / a ** 3)
    inc = math.radians(inc_deg)
    raan_dot = -1.5 * n * J2 * (RE / a) ** 2 * math.cos(inc)
    raan = math.radians(raan0_deg) + raan_dot * t
    u = math.radians(u0_deg) + n * t
    cu, su, cO, sO, ci, si = np.cos(u), np.sin(u), np.cos(raan), np.sin(raan), math.cos(inc), math.sin(inc)
    r = a * np.stack([cO * cu - sO * su * ci, sO * cu + cO * su * ci, su * si], axis=1)
    # velocity: d/dt of r (u and raan vary)
    drdu = a * np.stack([-cO * su - sO * cu * ci, -sO * su + cO * cu * ci, cu * si], axis=1)
    drdO = a * np.stack([-sO * cu - cO * su * ci, cO * cu - sO * su * ci, np.zeros_like(u)], axis=1)
    v = drdu * n + drdO * raan_dot
    acc = -MU * r / a ** 3
    return r, v, acc


def pass_geometry(h, inc, raan0, u0, f_c, t, label):
    rs_e, lat, lon = stn_ecef()
    th = WE * t
    c, s = np.cos(th), np.sin(th)
    # station in ECI (GMST = 0 at t = 0)
    rg = np.stack([c * rs_e[0] - s * rs_e[1], s * rs_e[0] + c * rs_e[1], np.full_like(t, rs_e[2])], axis=1)
    w = np.array([0, 0, WE])
    vg = np.cross(w, rg)
    ag = np.cross(w, vg)
    r, v, acc = propagate(h, inc, raan0, u0, t)
    d = r - rg
    R = np.linalg.norm(d, axis=1)
    rh = d / R[:, None]
    vrel = v - vg
    rdot = np.sum(vrel * rh, axis=1)
    rdd = np.sum((acc - ag) * rh, axis=1) + (np.sum(vrel * vrel, axis=1) - rdot ** 2) / R
    # ENU in ECEF
    de = np.stack([c * d[:, 0] + s * d[:, 1], -s * d[:, 0] + c * d[:, 1], d[:, 2]], axis=1)
    sl, cl, so, co = math.sin(lat), math.cos(lat), math.sin(lon), math.cos(lon)
    E = -so * de[:, 0] + co * de[:, 1]
    N = -sl * co * de[:, 0] - sl * so * de[:, 1] + cl * de[:, 2]
    U = cl * co * de[:, 0] + cl * so * de[:, 1] + sl * de[:, 2]
    el = np.degrees(np.arcsin(U / R))
    az = np.degrees(np.arctan2(E, N)) % 360
    return dict(t=t, R=R, rdot=rdot, rdd=rdd, el=el, az=az, fD=-rdot * f_c / C, fDdot=-rdd * f_c / C)


def find_passes(g, mask=0.0):
    up = g["el"] > mask
    edges = np.flatnonzero(np.diff(up.astype(int)))
    passes = []
    i = 0
    while i < len(edges) - 1:
        a, b = edges[i] + 1, edges[i + 1]
        if up[a]:
            passes.append((a, b))
            i += 2
        else:
            i += 1
    return passes


def describe(g, a, b, f_lab, f_c):
    t, el, az = g["t"], g["el"], g["az"]
    sl = slice(a, b + 1)
    k = a + np.argmax(el[sl])
    m10 = np.flatnonzero(el[sl] > 10)
    dur10 = (t[sl][m10[-1]] - t[sl][m10[0]]) if m10.size else 0
    azr = np.gradient(np.degrees(np.unwrap(np.radians(az[sl]))), t[sl])
    elr = np.gradient(el[sl], t[sl])
    # finite-difference check of the analytic range acceleration
    fd = np.gradient(np.gradient(g["R"][sl], t[sl]), t[sl])
    err = np.max(np.abs(fd[3:-3] - g["rdd"][sl][3:-3]))
    print(f"     pass T+{t[a]/3600:6.3f} h: max el {el[k]:5.1f} deg at az {az[k]:5.1f}; duration >0 deg "
          f"{(t[b]-t[a])/60:5.1f} min, >10 deg {dur10/60:5.1f} min; AOS az {az[a]:5.1f}, LOS az {az[b]:5.1f}")
    print(f"       range {g['R'][sl].min()/1e3:6.0f}-{g['R'][sl].max()/1e3:6.0f} km; Doppler @{f_lab} "
          f"{g['fD'][a]/1e3:+6.2f} -> {g['fD'][b]/1e3:+6.2f} kHz (max |fD| {np.abs(g['fD'][sl]).max()/1e3:5.2f} kHz); "
          f"max |dfD/dt| {np.abs(g['fDdot'][sl]).max():6.1f} Hz/s at el {el[a+np.argmax(np.abs(g['fDdot'][sl]))]:4.1f} deg")
    print(f"       max |R''| {np.abs(g['rdd'][sl]).max():6.1f} m/s^2 (analytic vs finite diff {err:.3f} m/s^2); "
          f"max az rate {np.abs(azr).max():6.2f} deg/s, max el rate {np.abs(elr).max():5.2f} deg/s")
    return dict(k=k, el_max=el[k], fd_max=np.abs(g['fD'][sl]).max(), fdd_max=np.abs(g['fDdot'][sl]).max(),
                azr=np.abs(azr).max(), err=err, sl=sl)


def section2_3():
    t = np.arange(0, 96 * 3600, 1.0)
    out = {}
    for label, h, f_c, f_lab in (("525 km SSO CubeSat", 525e3, 437e6, "437 MHz"),
                                 ("820 km SSO Meteor-M class", 820e3, 137.9e6, "137.9 MHz")):
        inc = sso_incl(h)
        print("=" * 96)
        print(f"{'2' if h < 6e5 else '3'}) {label}: i = {inc:.2f} deg (sun-synchronous), RAAN0 = 100 deg, u0 = 0, "
              f"96 h from Singapore (illustrative elements, two-body + J2 RAAN drift)")
        g = pass_geometry(h, inc, 100.0, 0.0, f_c, t, label)
        ps = find_passes(g, 0.0)
        maxels = [g["el"][a:b + 1].max() for a, b in ps]
        print(f"   {len(ps)} passes above 0 deg in 96 h; max elevations: " + ", ".join(f"{m:.0f}" for m in maxels))
        print(f"   passes above 10 deg max-el: {sum(m > 10 for m in maxels)}, above 30: {sum(m > 30 for m in maxels)}, "
              f"above 60: {sum(m > 60 for m in maxels)}")
        i_hi = int(np.argmax(maxels))
        i_30 = int(np.argmin([abs(m - 30) for m in maxels]))
        print("   Highest pass:")
        d_hi = describe(g, *ps[i_hi], f_lab, f_c)
        print("   Pass nearest 30 deg:")
        d_30 = describe(g, *ps[i_30], f_lab, f_c)
        check(f"{label}: analytic R'' matches finite difference (< 0.05 m/s^2)", max(d_hi["err"], d_30["err"]) < 0.05)
        out[label] = dict(g=g, ps=ps, hi=ps[i_hi], p30=ps[i_30], d_hi=d_hi)
        if h < 6e5:
            check("437 MHz LEO max Doppler 9-11 kHz", 9e3 < d_hi["fd_max"] < 11e3)
        else:
            check("137.9 MHz Meteor Doppler ~ +-3 kHz (14/recipes says 3.0)", 2.7e3 < d_hi["fd_max"] < 3.3e3)
    # keyhole: nudge RAAN until the highest 525 km pass goes (nearly) overhead
    print("   Keyhole demo (525 km): RAAN nudged so the highest pass goes overhead")
    a0, b0 = out["525 km SSO CubeSat"]["hi"]
    tw = np.arange(t[a0] - 900, t[b0] + 900, 0.5)
    best = None
    for raan in np.arange(98.0, 102.0, 0.02):
        g = pass_geometry(525e3, sso_incl(525e3), raan, 0.0, 437e6, tw, "")
        m = g["el"].max()
        if best is None or m > best[0]:
            best = (m, raan, g)
    m, raan, g = best
    ps = find_passes(g, 0.0)
    a, b = max(ps, key=lambda p: g["el"][p[0]:p[1] + 1].max())
    d = describe(g, a, b, "437 MHz", 437e6)
    print(f"     (RAAN0 {raan:.2f} deg) -> an az/el rotator limited to ~3-6 deg/s cannot follow {d['azr']:.0f} deg/s at TCA")
    check("near-overhead pass az rate >> 10 deg/s", d["el_max"] > 88 and d["azr"] > 10)
    return out


# --------------------------------------------------------------------------- 4 transponders
def section4(passes):
    print("=" * 96)
    print("4) Linear-transponder Doppler (V/U, uplink 145.9 MHz, downlink 435.9 MHz), worst |rdot| of the 525 km pass")
    g = passes["525 km SSO CubeSat"]["g"]
    sl = passes["525 km SSO CubeSat"]["d_hi"]["sl"]
    vr = np.abs(g["rdot"][sl]).max()
    fu, fdn = 145.9e6, 435.9e6
    beta = vr / C
    up = fu * beta
    inv = (fdn - fu) * beta
    noninv = (fdn + fu) * beta
    print(f"   |rdot|max {vr/1e3:.2f} km/s: uplink alone {up/1e3:.2f} kHz; downlink alone {fdn*beta/1e3:.2f} kHz")
    print(f"   heard through an INVERTING transponder: {inv/1e3:.2f} kHz (proportional to f_down - f_up)")
    print(f"   heard through a NON-inverting transponder: {noninv/1e3:.2f} kHz (proportional to f_down + f_up)")
    # exact check: f_sat_rx = fu(1-b); inverting: f_sat_tx = Cst - f_sat_rx with Cst = fu+fdn; f_gnd = f_sat_tx (1-b)
    b = beta
    exact_inv = ((fu + fdn) - fu * (1 - b)) * (1 - b) - fdn
    print(f"   exact (to 2nd order) inverting shift {exact_inv/1e3:+.3f} kHz")
    check("inverting first-order formula", abs(abs(exact_inv) - inv) / inv < 1e-3)


# --------------------------------------------------------------------------- 5 budgets
def tsys(ta, nf_db, loss_db=0.0, t_phys=290.0):
    """System temperature at the antenna terminal: antenna, feed loss (before LNA), receiver."""
    L = 10 ** (loss_db / 10)
    te = 290 * (10 ** (nf_db / 10) - 1)
    return ta + (L - 1) * t_phys + L * te


def section5(passes):
    print("=" * 96)
    print("5a) 437 MHz CubeSat downlink, 1 W into 0 dBi linear (3 dB pol. loss into CP), 9k6 GMSK")
    eirp_dbw = 0.0 + 0.0                       # 1 W, 0 dBi
    req_ebn0 = 12.0                            # non-coherent GMSK/FSK, BER ~1e-5 + margin for real demods (assumed)
    rb = 9600.0
    req_cn0 = req_ebn0 + 10 * math.log10(rb) + 2.0     # 2 dB implementation loss (assumed)
    stations = [("12 dBic crossed Yagi + masthead LNA NF 0.8 dB, 0.3 dB feed", 12.0, 0.8, 0.3,
                 {90: 49, 30: 60, 10: 101}),
                ("omni turnstile/eggbeater 0 dBic + LNA NF 0.8 dB", 0.0, 0.8, 0.3, {90: 150, 30: 150, 10: 150}),
                ("RTL-SDR (NF 6 dB) directly on 12 dBic Yagi, 5 m RG-58 (1.5 dB)", 12.0, 6.0, 1.5,
                 {90: 49, 30: 60, 10: 101})]
    print(f"   required C/N0 = {req_ebn0:.0f} + 10log(9600) + 2 = {req_cn0:.1f} dB-Hz")
    h = 525e3
    res = {}
    for name, g_dbi, nf, loss, ta in stations:
        print(f"   {name}:")
        for el in (90, 30, 10):
            d = slant(h, el)
            ts = tsys(ta[el], nf, loss)
            gt = g_dbi - 10 * math.log10(ts)   # G/T at the antenna terminal (feed loss is inside Tsys)
            cn0 = eirp_dbw - fspl(437e6, d) - 3.0 - 0.5 + gt - K_DB
            print(f"     el {el:2d}: R {d/1e3:5.0f} km, FSPL {fspl(437e6, d):6.1f} dB, Tsys {ts:6.0f} K, "
                  f"G/T {gt:6.1f} dB/K, C/N0 {cn0:5.1f} dB-Hz, margin {cn0-req_cn0:+5.1f} dB")
            res[(name[:4], el)] = cn0 - req_cn0
    check("Yagi+LNA closes 9k6 at 10 deg with > 10 dB", res[("12 d", 10)] > 10)

    print("5b) TinyGS-style LoRa: 22 dBm into 0 dBi on the satellite; ground 2 dBi ground plane, module NF 6 dB")
    for sf in (7, 10, 12):
        s = sensitivity_dbm(sf, 125e3, nf_db=6.0)
        row = []
        for el in (90, 30, 10):
            d = slant(h, el)
            pr = 22 + 0 - fspl(436.7e6, d) - 3.0 - 0.5 + 2.0
            row.append(f"el {el:2d}: Pr {pr:6.1f} dBm, margin {pr - s:+5.1f}")
        print(f"   SF{sf:2d}/125 sens {s:6.1f} dBm | " + " | ".join(row))
    s10 = sensitivity_dbm(10, 125e3, nf_db=6.0)
    check("SF10/125 closes at 30 deg with a ground plane", 22 - fspl(436.7e6, slant(h, 30)) - 3.5 + 2 > s10)
    print("   Per-packet Doppler drift over the highest 525 km pass at 436.7 MHz (32-byte packet), vs Semtech limit")
    g = passes["525 km SSO CubeSat"]["g"]
    sl = passes["525 km SSO CubeSat"]["d_hi"]["sl"]
    t = g["t"][sl]
    fd = g["fD"][sl] * 436.7e6 / 437e6
    for sf, bw in ((7, 125e3), (9, 125e3), (10, 125e3), (11, 125e3), (12, 125e3), (12, 250e3)):
        ldro = (2 ** sf / bw) >= 16.38e-3
        T = time_on_air(32, sf, bw, cr=1, npre=8, crc=True, explicit=True, ldro=ldro, chip="sx126x")
        lim = bw / (3 * 2 ** sf) * (16 if ldro else 1)
        fe = np.interp(t + T, t, fd)
        drift = np.abs(fe - fd)[t + T <= t[-1]]
        print(f"     SF{sf:2d}/{int(bw/1e3)}k{' LDRO' if ldro else '     '}: ToA {T*1e3:7.1f} ms, max drift {drift.max():7.1f} Hz, "
              f"limit {lim:6.1f} Hz -> {'FAIL near TCA' if drift.max() > lim else 'ok'}"
              f"{'' if drift.max() <= lim else f' ({100*np.mean(drift > lim):.0f} % of start times)'}")
    print("   Doppler offset window +-25 % BW: 125 kHz -> +-31.25 kHz vs max |fD| "
          f"{np.abs(fd).max()/1e3:.1f} kHz (static offset fine)")

    print("5c) Meteor-M LRPT 137.9 MHz (QPSK 72 kBd, r=1/2 K=7 + RS): G/T of a QFH and EIRP needed")
    # sky: Tb(408) cold 20 / typical 60 / plane 200 K scaled by f^-2.75 (07 page); QFH sees ~70 % sky, 30 % ground
    k = (137.9 / 408.0) ** -2.75
    sky = {"cold": 20 * k, "typical": 60 * k, "plane": 200 * k}
    print(f"   galactic sky at 137.9 MHz: cold {sky['cold']:.0f} K, typical {sky['typical']:.0f} K, plane {sky['plane']:.0f} K")
    mm = {"quiet rural": 53.6 - 28.6 * math.log10(137.9), "rural": 67.2 - 27.7 * math.log10(137.9),
          "residential": 72.5 - 27.7 * math.log10(137.9), "city": 76.8 - 27.7 * math.log10(137.9)}
    for kname, fa in mm.items():
        print(f"   P.372 man-made {kname:11s}: Fam {fa:5.1f} dB -> {290*10**(fa/10):7.0f} K (valid: f < 250 MHz)")
    # required C/N0: Eb/N0 (info) 2.5 dB for BER 1e-5 with r1/2 K7 + RS (textbook-level value), 72 kbit/s info,
    # 2 dB implementation
    req = 2.5 + 10 * math.log10(72e3) + 2.0
    print(f"   required C/N0 ~ 2.5 + 10log(72k) + 2 = {req:.1f} dB-Hz (assumed demodulator performance)")
    h = 820e3
    for site, ta in (("rural, typical sky", 0.7 * sky["typical"] + 0.3 * 290 + 290 * 10 ** (mm["rural"] / 10)),
                     ("residential", 0.7 * sky["typical"] + 0.3 * 290 + 290 * 10 ** (mm["residential"] / 10)),
                     ("city", 0.7 * sky["typical"] + 0.3 * 290 + 290 * 10 ** (mm["city"] / 10))):
        for nf, rx in ((6.0, "RTL-SDR NF 6 dB"), (1.0, "LNA NF 1 dB")):
            ts = tsys(ta, nf, 0.5)
            gt = 2.0 - 10 * math.log10(ts)
            need = [req - (gt - K_DB) + fspl(137.9e6, slant(h, el)) + 0.5 for el in (90, 30, 10)]
            print(f"   {site:19s} {rx:15s}: Tsys {ts:6.0f} K, G/T {gt:6.1f} dB/K (QFH 2 dBic); EIRP needed "
                  f"@90/30/10 deg {need[0]:5.1f}/{need[1]:5.1f}/{need[2]:5.1f} dBW")
    ts_r6 = tsys(0.7 * sky["typical"] + 0.3 * 290 + 290 * 10 ** (mm["residential"] / 10), 6.0, 0.5)
    ts_r1 = tsys(0.7 * sky["typical"] + 0.3 * 290 + 290 * 10 ** (mm["residential"] / 10), 1.0, 0.5)
    print(f"   LNA benefit in a residential site: {10*math.log10(ts_r6/ts_r1):.2f} dB")
    check("137 MHz residential: LNA buys < 1 dB (as 14/recipes says)", 10 * math.log10(ts_r6 / ts_r1) < 1.0)

    print("5d) GEO from Singapore")
    rs_e, lat, lon = stn_ecef()
    for name, slon in (("QO-100 / Es'hail-2 25.9 E", 25.9), ("sub-satellite 103.8 E", 103.8), ("Himawari 140.7 E", 140.7)):
        dl = math.radians(slon - STN["lon"])
        cg = math.cos(math.radians(STN["lat"])) * math.cos(dl)
        gam = math.acos(cg)
        rg = RE + 35786e3
        el = math.degrees(math.atan2(cg - RE / rg, math.sin(gam)))
        d = math.sqrt(RE ** 2 + rg ** 2 - 2 * RE * rg * cg)
        print(f"   {name:26s}: elevation {el:5.1f} deg, slant {d/1e3:7.0f} km, FSPL @10.489 GHz {fspl(10.489e9, d):6.1f} dB")
        if slon == 25.9:
            check("QO-100 barely above the horizon from Singapore (0-6 deg)", 0 < el < 6)


if __name__ == "__main__":
    section1()
    P = section2_3()
    section4(P)
    section5(P)
    print("=" * 96)
    print("ALL PASS" if not FAIL else f"FAILURES: {FAIL}")
