#!/usr/bin/env python3
"""
proj_lora_link.py -- design calculations for kb/20-projects-recipes/lora-rocket-telemetry-link.md

Scenario: ~10 km apogee rocket, design slant range 15 km, primary 433 MHz (EBYTE E22-400T33D /
SX1268) and secondary 868/905/920 MHz (EBYTE E220-900T30D / LLCC68) downlinks.

Sections
 1. Point-mass 2-D trajectory tuned to a 10 km apogee (thrust, drag with Cd(M), ISA density),
    drogue/main descent with wind drift.
 2. Geometry seen from two ground stations: slant range, radial velocity/acceleration,
    Doppler shift and rate, look angle from the aft axis, elevation rate, plume-cone flag.
 3. Doppler-RATE check per SF/BW: change of Doppler across every possible packet window during
    boost/coast vs Semtech's per-packet drift limit BW/(3*2^SF) (x16 with LDRO).
 4. Air-time budget: frame schedule occupancy per SF/BW and per legal duty-cycle regime.
 5. Ground receive chain (Friis) and sensitivity per setting.
 6. Static worst-case link budgets at 15 km for legal and licensed powers.
 7. Time-series received power along the trajectory (axial dipole pattern, CP ground antenna).
 8. Landed (two-ray) range.
 9. Range-test (attenuator method) design numbers.
10. Dual-band spur check and near-pad levels.
11. Pre-registered predictions (printed as a table).

Reuses: tools/rfcalc (lora.time_on_air, lora.sensitivity_dbm, link.fspl_db, noise.cascade).
Pattern formula as tools/verify/ant_rocket.py. Drift rule as tools/verify/lora_doppler.py.

Run: python3 tools/verify/proj_lora_link.py
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from rfcalc.lora import time_on_air, sensitivity_dbm, t_sym  # noqa: E402
from rfcalc.link import fspl_db  # noqa: E402
from rfcalc.noise import Stage, cascade  # noqa: E402

C = 299_792_458.0
G0 = 9.80665

# ----------------------------------------------------------------------------- 1. trajectory
ROCKET = dict(m_dry=20.0, m_prop=12.0, isp=210.0, diam=0.130, rail_tilt_deg=3.0,
              drogue_rate=30.0, main_alt=450.0, main_rate=6.0, wind=8.0)


def isa(z):
    """ISA temperature [K] and density [kg/m^3] (troposphere + isothermal to 20 km)."""
    z = max(z, 0.0)
    if z < 11000:
        T = 288.15 - 0.0065 * z
        p = 101325 * (T / 288.15) ** 5.2559
    else:
        T = 216.65
        p = 22632 * math.exp(-G0 * (z - 11000) / (287.05 * T))
    return T, p / (287.05 * T)


def cd_of_mach(M):
    """Crude Cd(M) for a slender amateur rocket (subsonic 0.45, transonic peak 0.65, 0.5 at M>=2)."""
    pts = [(0, 0.45), (0.8, 0.45), (1.05, 0.65), (1.3, 0.60), (2.0, 0.50), (5.0, 0.40)]
    for (m0, c0), (m1, c1) in zip(pts[:-1], pts[1:]):
        if M <= m1:
            return c0 + (c1 - c0) * (M - m0) / (m1 - m0)
    return pts[-1][1]


def fly(thrust, dt=1e-3, R=ROCKET):
    """Integrate ascent (thrust + drag + gravity) then parachute descent. Returns dict of arrays."""
    A = math.pi * (R["diam"] / 2) ** 2
    mdot = thrust / (R["isp"] * G0)
    tb = R["m_prop"] / mdot
    th = math.radians(R["rail_tilt_deg"])
    x, z, vx, vz = 0.0, 0.0, 0.0, 0.0
    t = 0.0
    out = {k: [] for k in ("t", "x", "z", "vx", "vz", "ax", "az", "phase")}
    # ascent
    while True:
        m = R["m_dry"] + R["m_prop"] - mdot * min(t, tb)
        v = math.hypot(vx, vz)
        T, rho = isa(z)
        a_snd = math.sqrt(1.4 * 287.05 * T)
        D = 0.5 * rho * v * v * cd_of_mach(v / a_snd) * A
        if v < 1.0:          # on the rail: thrust along the rail
            ux, uz = math.sin(th), math.cos(th)
        else:
            ux, uz = vx / v, vz / v
        F = thrust if t < tb else 0.0
        ax = (F - D) * ux / m
        az = (F - D) * uz / m - G0
        if t > 0.5 and vz <= 0:   # apogee
            break
        for k, val in zip(("t", "x", "z", "vx", "vz", "ax", "az", "phase"),
                          (t, x, z, vx, vz, ax, az, 0 if t < tb else 1)):
            out[k].append(val)
        vx += ax * dt
        vz += az * dt
        x += vx * dt
        z += vz * dt
        t += dt
    t_apo = t
    # descent (quasi-steady): drogue then main, horizontal velocity = wind
    dtd = 0.05
    while z > 0:
        rate = R["drogue_rate"] if z > R["main_alt"] else R["main_rate"]
        vx, vz = R["wind"], -rate
        for k, val in zip(("t", "x", "z", "vx", "vz", "ax", "az", "phase"),
                          (t, x, z, vx, vz, 0.0, 0.0, 2 if z > R["main_alt"] else 3)):
            out[k].append(val)
        x += vx * dtd
        z += vz * dtd
        t += dtd
    res = {k: np.array(v) for k, v in out.items()}
    res.update(tb=tb, t_apo=t_apo, thrust=thrust)
    return res


def tune_apogee(target=10000.0, thrust=3500.0):
    """Bisect the propellant mass at fixed average thrust until the apogee equals target."""
    lo, hi = 4.0, 30.0
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        ROCKET["m_prop"] = mid
        tr = fly(thrust, dt=2e-3)
        if tr["z"].max() > target:
            hi = mid
        else:
            lo = mid
    ROCKET["m_prop"] = 0.5 * (lo + hi)
    return fly(thrust)


# ----------------------------------------------------------------------------- 2. geometry
STATIONS = {"A (2 km cross-range)": np.array([0.0, 2000.0, 2.0]),
            "B (5 km up-range)": np.array([-5000.0, 0.0, 2.0]),
            "C (5 km cross-range)": np.array([0.0, 5000.0, 2.0]),
            "D (5 km down-range)": np.array([5000.0, 0.0, 2.0])}


def geometry(tr, st):
    p = np.stack([tr["x"], np.zeros_like(tr["x"]), tr["z"]], axis=1)
    d = p - st
    r = np.linalg.norm(d, axis=1)
    asc = tr["phase"] <= 1
    t = tr["t"]
    rdot = np.gradient(r, t)
    rddot = np.gradient(rdot, t)
    # aft axis during ascent = -velocity direction
    v = np.stack([tr["vx"], np.zeros_like(tr["vx"]), tr["vz"]], axis=1)
    vn = np.linalg.norm(v, axis=1, keepdims=True)
    vn[vn < 1e-6] = 1e-6
    aft = -v / vn
    los = -d / r[:, None]          # rocket -> station
    cos_look = np.sum(aft * los, axis=1)
    look = np.degrees(np.arccos(np.clip(cos_look, -1, 1)))
    horiz = np.hypot(d[:, 0], d[:, 1])
    elev = np.degrees(np.arctan2(d[:, 2], horiz))
    elev_rate = np.gradient(elev, t)
    return dict(r=r, rdot=rdot, rddot=rddot, look=look, elev=elev, elev_rate=elev_rate, asc=asc)


def dipole_gain_dbi(look_deg, floor_dbi=-20.0):
    """Axial half-wave dipole gain [dBi] vs angle from the axis; floor models null filling."""
    th = np.radians(np.asarray(look_deg, float))
    s = np.where(np.abs(np.sin(th)) < 1e-9, 1e-9, np.sin(th))
    F = np.cos(np.pi / 2 * np.cos(th)) / s
    g = 2.15 + 20 * np.log10(np.maximum(np.abs(F), 1e-9))
    return np.maximum(g, floor_dbi)


# ----------------------------------------------------------------------------- 3. drift check
def drift_limit_hz(sf, bw, ldro):
    return bw / (3 * 2 ** sf) * (16 if ldro else 1)


def packet_drift_series(t, rdot, f_c, T_pkt):
    """|Doppler change| over a packet starting at each t (Hz)."""
    fd = -rdot * f_c / C
    t_end = t + T_pkt
    fd_end = np.interp(t_end, t, fd)
    return np.abs(fd_end - fd)


# ----------------------------------------------------------------------------- helpers
def toa(pl, sf, bw, chip="sx126x", ldro=None):
    if ldro is None:
        ldro = (2 ** sf / bw) >= 16.38e-3
    return time_on_air(pl, sf, bw, cr=1, npre=8, crc=True, explicit=True, ldro=ldro, chip=chip)


def main():
    np.set_printoptions(precision=2, suppress=True)
    print("=" * 100)
    print("1) Trajectory (point mass, tuned to 10 km apogee)")
    tr = tune_apogee(10000.0)
    asc = tr["phase"] <= 1
    t = tr["t"]
    a_axial = np.hypot(tr["ax"], tr["az"] + G0)   # sensed (specific force) magnitude
    v = np.hypot(tr["vx"], tr["vz"])
    i_bo = np.searchsorted(t, tr["tb"])
    print(f"   thrust {tr['thrust']:.0f} N, burn {tr['tb']:.2f} s, Isp {ROCKET['isp']} s, "
          f"m_prop {ROCKET['m_prop']:.2f} kg, m0 {ROCKET['m_dry']+ROCKET['m_prop']:.1f} kg")
    print(f"   burnout: t={tr['tb']:.2f} s, v={v[i_bo]:.0f} m/s, z={tr['z'][i_bo]:.0f} m; "
          f"apogee {tr['z'].max():.0f} m at t={tr['t_apo']:.1f} s, x={tr['x'][asc][-1]:.0f} m")
    print(f"   peak kinematic accel during burn {np.max(np.hypot(tr['ax'], tr['az'])[asc])/G0:.1f} g; "
          f"peak drag decel after burnout {np.max(-(tr['ax']*tr['vx']+tr['az']*tr['vz'])[asc][i_bo:]/np.maximum(v[asc][i_bo:],1))/G0:.1f} g "
          f"(along-track, incl. gravity)")
    land = ~asc
    print(f"   landing at t={t[-1]:.0f} s, x={tr['x'][-1]:.0f} m downrange (drogue {ROCKET['drogue_rate']} m/s, "
          f"main {ROCKET['main_rate']} m/s at {ROCKET['main_alt']} m, wind {ROCKET['wind']} m/s)")
    vmax = v[asc].max()
    print(f"   max speed {vmax:.0f} m/s (Mach {vmax/340:.2f} at sea-level sound speed)")

    print("\n2) Geometry from each station")
    geo = {}
    for name, st in STATIONS.items():
        g = geometry(tr, st)
        geo[name] = g
        a = g["asc"]
        burn = t < tr["tb"]
        iapo = np.argmax(tr["z"])
        print(f"   Station {name}:")
        print(f"     max slant range ascent {g['r'][a].max()/1e3:.2f} km, whole flight {g['r'].max()/1e3:.2f} km, "
              f"at landing {g['r'][-1]/1e3:.2f} km")
        print(f"     max |radial accel| in burn {np.max(np.abs(g['rddot'][burn]))/G0:.1f} g, "
              f"ascent 1 s..apogee-1 s {np.max(np.abs(g['rddot'][(t > 1) & (t < tr['t_apo'] - 1)]))/G0:.1f} g")
        print(f"     max |radial vel| {np.max(np.abs(g['rdot'][a])):.0f} m/s -> Doppler "
              f"{np.max(np.abs(g['rdot'][a]))*433.125e6/C/1e3:.2f} kHz @433, "
              f"{np.max(np.abs(g['rdot'][a]))*920e6/C/1e3:.2f} kHz @920")
        print(f"     look angle from aft axis at apogee-1s {g['look'][iapo-1000]:.1f} deg; "
              f"min over coast {g['look'][a][i_bo:].min():.1f} deg")
        coast = a & (t >= tr["tb"]) & (t < tr["t_apo"] - 2.0)
        ilk = np.argmin(np.where(coast, g["look"], 999.0))
        print(f"     look angle < 20 deg for {np.sum(coast & (g['look'] < 20.0))*1e-3:.1f} s of the coast; "
              f"minimum {g['look'][ilk]:.1f} deg at t={t[ilk]:.1f} s (z={tr['z'][ilk]:.0f} m)")
        plume = burn & (g["look"] < 22.0)
        print(f"     time in 22-deg plume cone during burn: {plume.sum()*1e-3:.2f} s of {tr['tb']:.2f} s")
        print(f"     max elevation rate {np.max(np.abs(g['elev_rate'][a][100:])):.1f} deg/s")

    print("\n3) Doppler-rate check: fraction of packet start times in burn+coast whose Doppler change")
    print("   across the packet exceeds Semtech's BW/(3*2^SF) (x16 LDRO); 40-byte frame, CR4/5, 8-sym preamble")
    PL = 40
    combos = [(7, 125e3), (8, 125e3), (9, 125e3), (10, 125e3), (12, 125e3),
              (7, 250e3), (8, 250e3), (9, 250e3), (10, 250e3), (7, 500e3), (8, 500e3), (9, 500e3),
              (11, 500e3)]
    worst = "A (2 km cross-range)"
    # also a worst-case 'station under the flight path' = full along-track acceleration
    for band, fc in (("433.125", 433.125e6), ("868.125", 868.125e6), ("905.0", 905.0e6)):
        print(f"   f = {band} MHz")
        for sf, bw in combos:
            ldro = (2 ** sf / bw) >= 16.38e-3
            T = toa(PL, sf, bw, ldro=ldro)
            lim = drift_limit_hz(sf, bw, ldro)
            row = []
            for name in STATIONS:
                g = geo[name]
                sel = asc & (t < tr["t_apo"] - 1.0 - T)
                dfx = packet_drift_series(t[sel], g["rdot"][sel], fc, T)
                row.append((dfx.max(), 100 * np.mean(dfx > lim)))
            # 'AT' = along-track: radial acceleration = full along-track acceleration (station under the track)
            sel = asc & (t < tr["t_apo"] - 1.0 - T)
            vv = v[sel]
            dfw = packet_drift_series(t[sel], vv, fc, T)
            row.append((dfw.max(), 100 * np.mean(dfw > lim)))
            a_allow = lim / T * C / fc / G0
            print(f"     SF{sf:2d}/{int(bw/1e3):3d}k ToA {T*1e3:7.1f} ms lim {lim:7.1f} Hz (a_allow {a_allow:7.1f} g)  "
                  + "  ".join(f"{nm.split()[0]}: max {m:6.1f} Hz, {fr:5.1f}% fail" for nm, (m, fr) in
                              zip(list(STATIONS) + ["AT"], row)))

    print("\n4) Air-time budget: schedule state 40 B @10 Hz + GNSS 32 B @2 Hz + health 16 B @1 Hz")
    sched = [(40, 10.0), (32, 2.0), (16, 1.0)]
    for sf, bw in [(7, 125e3), (7, 250e3), (7, 500e3), (8, 250e3), (8, 500e3), (9, 125e3), (9, 500e3)]:
        occ = sum(rate * toa(pl, sf, bw) for pl, rate in sched)
        t48 = toa(48, sf, bw)
        print(f"   SF{sf}/{int(bw/1e3)}k: schedule occupancy {100*occ:6.1f} %;  one combined 48-B frame "
              f"(state+GNSS+health) ToA {t48*1e3:6.1f} ms -> max rate {0.7/t48:5.1f} Hz (70 % cap), "
              f"{0.10/t48:5.2f} Hz (10 % duty), {0.01/t48:5.3f} Hz (1 % duty)")
    # 1 h window interpretation for 10 % duty
    for sf, bw in [(7, 500e3), (7, 250e3)]:
        flight_s = 600.0
        occ = sum(rate * toa(pl, sf, bw) for pl, rate in sched)
        pad_occ = 1 * toa(16, sf, bw) + 1 * toa(32, sf, bw)
        avg = (occ * flight_s + pad_occ * (3600 - flight_s)) / 3600
        print(f"   1-h-window view SF{sf}/{int(bw/1e3)}k: 10 min at {100*occ:.1f} % + 50 min pad at "
              f"{100*pad_occ:.2f} % -> hourly mean {100*avg:.2f} % (interpretation; TS SRD defines no window)")

    print("\n5) Ground receive chain (Friis) -> system NF")
    # coax loss fits A = k1 sqrt(f_MHz) + k2 f_MHz  [dB/100 m] from kb/03 coax-and-cables.md
    def coax_db(kind, f_mhz, length_m):
        k = {"LMR-400": (0.403, 0.00082), "LMR-240": (0.796, 0.00109), "LMR-195": (1.169, 0.00157),
             "RG-58": (1.123, 0.0123), "RG-174": (2.63, 0.0220)}[kind]
        return (k[0] * math.sqrt(f_mhz) + k[1] * f_mhz) * length_m / 100.0
    l_rg58 = coax_db("RG-58", 433.125, 15.0)
    l_lmr240 = coax_db("LMR-240", 433.125, 15.0)
    print(f"   15 m RG-58 at 433 MHz: {l_rg58:.2f} dB; 15 m LMR-240: {l_lmr240:.2f} dB (kb/03 fits)")
    chains = {
        "module direct, 1 m jumper": [Stage("jumper", -0.3), Stage("module", 0, nf=6.0)],
        "module after 15 m RG-58": [Stage("RG58", -l_rg58), Stage("module", 0, nf=6.0)],
        "LNA(0.8 dB,18 dB)->SAW(2 dB)->15 m LMR-240->splitter(3.5)->module":
            [Stage("LNA", 18, nf=0.8), Stage("SAW", -2.0), Stage("LMR240", -l_lmr240),
             Stage("split", -3.5), Stage("module", 0, nf=6.0)],
        "SAW(2)->LNA->15 m LMR-240->splitter->module":
            [Stage("SAW", -2.0), Stage("LNA", 18, nf=0.8), Stage("LMR240", -l_lmr240),
             Stage("split", -3.5), Stage("module", 0, nf=6.0)],
    }
    nf_sys = {}
    for k, st in chains.items():
        nf = cascade(st)[-1]["NF_cum_dB"]
        nf_sys[k] = nf
        print(f"   {k:78s} NF = {nf:5.2f} dB")
    NF_GS = nf_sys["LNA(0.8 dB,18 dB)->SAW(2 dB)->15 m LMR-240->splitter(3.5)->module"]
    # external noise: effective NF including antenna temperature Ta (Tsys = Ta + Te; ref 290 K)
    te = 290 * (10 ** (NF_GS / 10) - 1)
    for ta in (100.0, 290.0, 1150.0):
        eff = 10 * math.log10((ta + te) / 290)
        print(f"   Ta = {ta:6.0f} K: Tsys = {ta+te:6.0f} K -> effective NF (vs 290 K ref) {eff:5.2f} dB")

    print("\n   Sensitivity (NF_eff) per setting  [S = -174 + 10log BW + NF + SNRreq]")
    for sf, bw in [(7, 125e3), (7, 250e3), (7, 500e3), (8, 250e3), (9, 125e3), (9, 500e3), (10, 125e3),
                   (11, 125e3), (12, 125e3)]:
        s_mod = sensitivity_dbm(sf, bw, nf_db=6.0 + (1.5 if bw >= 500e3 else 0))
        s_gs = sensitivity_dbm(sf, bw, nf_db=NF_GS + (1.5 if bw >= 500e3 else 0))
        print(f"   SF{sf:2d}/{int(bw/1e3):3d}k: bare module {s_mod:7.1f} dBm; with masthead LNA chain "
              f"{s_gs:7.1f} dBm  (500 kHz rows include +1.5 dB datasheet penalty)")

    print("\n6) Static worst-case budgets at 15 km slant (rocket gain -14 dBi = axial dipole 11 deg off"
          " the tail; CP ground antenna -3 dB; pointing -1 dB; rocket feed -0.5; GS feed in NF)")
    configs = [
        # name, f, Pcond_dBm, Grx_dBic, sf, bw, legal note
        ("SG 433 26a 10 mW erp (dipole)", 433.125e6, 10.5, 10.0, 7, 250e3, "10 % duty"),
        ("SG 433 26b 1 mW erp", 433.125e6, 0.5, 10.0, 7, 250e3, "no duty limit"),
        ("SG 433 26a 10 mW erp, SF9/125", 433.125e6, 10.5, 10.0, 9, 125e3, "10 % duty"),
        ("Amateur 70 cm E22 33 dBm", 433.125e6, 33.0, 10.0, 7, 250e3, "licence + IMDA consent"),
        ("Amateur 70 cm E22 33 dBm SF7/500", 433.125e6, 33.0, 10.0, 7, 500e3, "licence"),
        ("SG 868 sub-band 29 E220 24 dBm", 868.125e6, 24.0, 12.0, 7, 250e3, "500 mW erp, no duty"),
        ("SG 920 30c E220 20 dBm", 920.125e6, 20.0, 12.0, 7, 250e3, "100 mW erp, 1 % duty"),
        ("IREC Mode A E220 30 dBm SF7/500", 905.0e6, 30.0, 12.0, 7, 500e3, "Part 15 DTS, TX ant <= 6 dBi"),
        ("Temp permit 920 E220 30 dBm", 920.125e6, 30.0, 12.0, 7, 250e3, "IMDA permit"),
    ]
    rows6 = []
    for name, f, p, grx, sf, bw, note in configs:
        L = fspl_db(f, 15e3)
        prx = p - 0.5 - 14.0 - L - 3.0 - 1.0 + grx
        pen = 1.5 if bw >= 500e3 else 0.0
        s = sensitivity_dbm(sf, bw, nf_db=NF_GS + pen)
        s_bare = sensitivity_dbm(sf, bw, nf_db=6.0 + 0.3 + pen)
        rows6.append((name, prx, prx - s, prx - s_bare))
        print(f"   {name:36s} FSPL {L:6.1f}  Prx {prx:7.1f} dBm  margin(LNA) {prx-s:6.1f} dB  "
              f"margin(bare) {prx-s_bare:6.1f} dB  [{note}]")

    print("\n7) Time series along the trajectory (CP 10 dBic at 433 / 12 dBic at 868; axial dipole with"
          " -20 dBi null floor; linear->CP -3 dB; pointing -1 dB)")
    for stn in ("C (5 km cross-range)", "A (2 km cross-range)", "B (5 km up-range)"):
        g = geo[stn]
        a = g["asc"]
        print(f"   --- station {stn}")
        for label, f, p, grx, sf, bw in [("433 amateur 33 dBm SF7/250", 433.125e6, 33.0, 10.0, 7, 250e3),
                                         ("433 SG-legal 10.5 dBm SF7/250", 433.125e6, 10.5, 10.0, 7, 250e3),
                                         ("868 SG-legal 24 dBm SF7/250", 868.125e6, 24.0, 12.0, 7, 250e3)]:
            gt = dipole_gain_dbi(g["look"])
            prx = p - 0.5 + gt - fspl_db(f, g["r"]) - 3.0 - 1.0 + grx
            s = sensitivity_dbm(sf, bw, nf_db=NF_GS)
            marg = prx - s
            ta = np.array([2, 5, 10, 20, 30, tr["t_apo"] - 1])
            idx = np.searchsorted(t, ta)
            m = a & (t > 1) & (t < tr["t_apo"] - 1)
            imin = np.argmin(np.where(m, marg, 1e9))
            print(f"   {label}: S {s:.1f} dBm; Prx at apogee-1 s {prx[idx[-1]]:.1f} dBm; min ascent margin "
                  f"{marg[imin]:.1f} dB at t={t[imin]:.1f} s (look {g['look'][imin]:.1f} deg, R {g['r'][imin]/1e3:.1f} km)")
            if stn.startswith("C"):
                for tt, ii in zip(ta, idx):
                    print(f"      t={tt:5.1f} s  z={tr['z'][ii]:6.0f} m  R={g['r'][ii]/1e3:5.2f} km  look={g['look'][ii]:5.1f} deg  "
                          f"Gt={gt[ii]:6.1f} dBi  Prx={prx[ii]:7.1f} dBm  margin={marg[ii]:5.1f} dB")

    print("\n8) Landed rocket (two-ray, antenna 0.2 m, station mast 2/6 m), SF9/125 & SF11/125 with LNA chain")
    for f, p, lab in [(433.125e6, 33.0, "433 33 dBm"), (433.125e6, 10.5, "433 10 mW erp"),
                      (868.125e6, 24.0, "868 24 dBm")]:
        for sf in (9, 11):
            if f > 800e6 and sf > 9:
                continue   # LLCC68: SF<=9 at 125 kHz
            s = sensitivity_dbm(sf, 125e3, nf_db=NF_GS)
            for hr in (2.0, 6.0):
                # budget: P - 0.5 + 0 dBi (lying rocket, avg) + Grx(10) - 3 (pol) - 10 (fade/terrain) - S
                mapl = p - 0.5 + 0.0 + 10.0 - 3.0 - 10.0 - s
                d = 10 ** ((mapl + 20 * math.log10(0.2 * hr)) / 40)
                lam = C / f
                dbrk = 4 * 0.2 * hr / lam
                print(f"   {lab:14s} SF{sf}/125 mast {hr:.0f} m: MAPL {mapl:6.1f} dB -> two-ray range "
                      f"{d/1e3:6.2f} km (breakpoint {dbrk:5.1f} m)")

    print("   cross-check with kb/15 / fix_legal_vs_licensed_link_budgets.py assumptions (bare module NF 6 dB, 1 dB cable,"
          " EIRP at the legal limit with a dipole, 13 dB pol+fade, 10 dBi Yagi, 2 m mast):")
    for lab, eirp in (("433 2 W (32.5 dBm EIRP)", 32.5), ("433 10 mW e.r.p. (12.15 dBm EIRP)", 12.15)):
        mapl = eirp + 10.0 - 1.0 - sensitivity_dbm(9, 125e3, nf_db=6.0) - 13.0
        d = 10 ** ((mapl + 20 * math.log10(0.2 * 2.0)) / 40)
        print(f"      {lab}: MAPL {mapl:.1f} dB -> {d/1e3:.2f} km")

    print("\n9) Range test by the attenuator method")
    f = 433.125e6
    lam = C / f
    for d_test in (300.0, 500.0, 1000.0, 2000.0):
        r1 = math.sqrt(lam * d_test / 4)
        extra = fspl_db(f, 15e3) - fspl_db(f, d_test)
        print(f"   d_test {d_test:6.0f} m: FSPL {fspl_db(f, d_test):5.1f} dB; mid-path Fresnel r1 {r1:4.1f} m "
              f"(60 % clearance needs h >= {0.6*r1:4.1f} m); 15-km-equivalent extra loss {extra:5.1f} dB")
    for p_set in (33.0, 24.0):
        att_min = p_set - 0.5 + 2.15 - 12.15
        print(f"   E22 set to {p_set:.0f} dBm: TX-side pad needed for <= 10 mW erp: >= {att_min:.1f} dB; "
              f"first pad dissipates {10**(p_set/10)/1e3:.2f} W")
    # (a) conducted ladder
    print("   (a) conducted sensitivity ladder (both ends in shielded boxes): 24 dBm - pads -> RX")
    for sf, bw in [(7, 250e3), (7, 500e3), (9, 125e3)]:
        s_mod = sensitivity_dbm(sf, bw, nf_db=6.0 + (1.5 if bw >= 500e3 else 0))
        print(f"       SF{sf}/{int(bw/1e3)}k: predicted module-only S = {s_mod:6.1f} dBm -> total pad at PER 1 % = "
              f"{24.0 - s_mod:6.1f} dB (a {24.0 - s_mod:.0f} dB path needs box isolation >= {24.0 - s_mod + 20:.0f} dB)")
    # (b) radiated equivalent-range test at legal power
    print("   (b) radiated 15-km-equivalent test at 10 mW erp, RX-side step attenuator, 10 dBic CP Yagi, LNA chain")
    for d_test in (1000.0, 2000.0):
        eirp = 12.15
        prx0 = eirp - fspl_db(f, d_test) - 3.0 + 10.0
        a_eq = (fspl_db(f, 15e3) - fspl_db(f, d_test)) + 16.2
        for sf, bw in [(7, 250e3), (9, 125e3)]:
            s = sensitivity_dbm(sf, bw, nf_db=NF_GS)
            print(f"       d={d_test/1e3:.0f} km SF{sf}/{int(bw/1e3)}k: Prx(0 dB) {prx0:6.1f} dBm (free space; "
                  f"MEASURE it); A_eq = {a_eq:5.1f} dB -> Prx {prx0-a_eq:6.1f} dBm, predicted margin "
                  f"{prx0-a_eq-s:5.1f} dB; A_fail = {prx0-s:5.1f} dB; RX box isolation needed >= {prx0-s+10:4.0f} dB")
    print("   SNR method (bare SX126x receiver): margin = SNR_meas - SNR_req(SF) when SNR_meas < ~+5 dB")

    print("\n10) Dual-band spur and near-pad checks")
    f1 = 433.125e6
    for ch in (16, 17, 18):
        f2 = (850.125 + ch) * 1e6
        print(f"   E22 2nd harmonic {2*f1/1e6:.3f} MHz vs E220 CH{ch} {f2/1e6:.3f} MHz: offset "
              f"{(f2-2*f1)/1e6:+.3f} MHz")
    for n in (2, 3, 4):
        print(f"   433.125 MHz harmonic {n}: {n*f1/1e6:8.3f} MHz; 868.125 harmonic {n}: {n*868.125:8.3f} MHz; "
              f"905 harmonic {n}: {n*905.0:8.3f} MHz")
    # IMD products near GNSS L1 1575.42
    fl1 = 1575.42
    best = []
    for m in range(-4, 5):
        for n in range(-4, 5):
            if m == 0 and n == 0:
                continue
            for fb in (868.125, 905.0, 920.125):
                fp = m * 433.125 + n * fb
                if abs(m) + abs(n) <= 5 and fp > 0:
                    best.append((abs(fp - fl1), m, n, fb, fp))
    for dd, m, n, fb, fp in sorted(best)[:6]:
        print(f"   IMD {m:+d}x433.125 {n:+d}x{fb}: {fp:8.3f} MHz ({dd:5.2f} MHz from L1), order {abs(m)+abs(n)}")
    # E22 channel harmonics vs GNSS bands (main-lobe edges; W5-E1 finding: CH 0-6 3rd harmonic in L2)
    gnss = {"GPS L5/Gal E5a/BDS B2a": (1166.22, 1186.68), "Gal E5b/BDS B2I": (1196.91, 1217.37),
            "GPS L2": (1217.37, 1237.83), "GLONASS L2 (FDMA)": (1242.42, 1249.14),
            "BDS B3I": (1258.29, 1278.75), "Galileo E6": (1258.29, 1299.21),
            "GPS L1 / Gal E1 / BDS B1C (+-10.23)": (1565.19, 1585.65), "BDS B1I": (1559.05, 1563.14),
            "GLONASS L1 (FDMA)": (1597.55, 1605.89)}
    print("   E22-400 channel n-th harmonics inside GNSS bands (f = 410.125 + CH MHz):")
    for ch in range(0, 84):
        f = 410.125 + ch
        hits = []
        for n in (2, 3, 4, 5):
            for nm, (lo, hi) in gnss.items():
                if lo <= n * f <= hi:
                    hits.append(f"{n}f={n*f:.3f} in {nm}")
        if hits and (ch <= 25 or ch % 10 == 0):
            print(f"      CH{ch:2d} {f:8.3f} MHz: " + "; ".join(hits))
    print("   CH23 433.125 MHz: 3f = 1299.375 MHz = 0.165 MHz above the Galileo E6 main-lobe edge (1299.21) -> marginal for E6 receivers")
    print("   IREC 70 cm SRAD 420.6-438.0 MHz -> 3f 1261.8-1314 MHz overlaps BDS B3I / Galileo E6 below 433.07 MHz")
    for ch in range(0, 81):
        f = 850.125 + ch
        for n in (2, 3):
            for nm, (lo, hi) in gnss.items():
                if lo <= n * f <= hi:
                    print(f"      E220 CH{ch} {f:.3f} MHz: {n}f in {nm}")
    for d in (1.0, 10.0, 30.0, 100.0):
        prx = 33.0 - 0.5 + 2.15 - fspl_db(433.125e6, d) + 10.0
        print(f"   near pad: 33 dBm dipole -> 10 dBi Yagi at {d:5.0f} m: {prx:6.1f} dBm "
              f"(EBYTE damage rating +10 dBm; LNA P1dB-in typ -10..0 dBm)")

    print("\n11) Pre-registered predictions summary printed in the page (numbers above).")


if __name__ == "__main__":
    main()
