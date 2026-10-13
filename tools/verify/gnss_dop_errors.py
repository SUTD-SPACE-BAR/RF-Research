#!/usr/bin/env python3
"""
gnss_dop_errors.py — verification for kb/21-gnss/gnss-error-sources-dop.md
                     (and the positioning maths in gnss-receiver-architecture-acquisition-tracking.md)

 1. DOP from the geometry matrix G (rows [-u_E, -u_N, -u_U, 1]); analytic check for
    one satellite at zenith + three at elevation e spaced 120 deg in azimuth.
 2. Least-squares pseudorange solution (Gauss-Newton) with a receiver clock bias; converges from
    Earth's centre; position error ~ PDOP * sigma_UERE (Monte Carlo).
 3. Synthetic multi-GNSS constellations (circular Walker-type orbits: GPS 24/6, Galileo 24/3,
    BDS-3 24/3 MEO + 3 IGSO + 3 GEO, GLONASS 24/3, QZSS 1 GEO + 3 IGSO) seen from Singapore
    over 24 h: satellites in view and HDOP/VDOP/PDOP for GPS, GPS+GAL, GPS+GAL+BDS, all.
    NOTE: synthetic, not a real almanac - for relative comparisons only.
 4. Rocket-specific sky masks: antenna tilted / pointing sideways under a parachute.
 5. Troposphere (Saastamoinen zenith hydrostatic + wet delay for Singapore-like conditions),
    ionosphere (0.162 m/TECU at L1), iono-free noise amplification, and the code-multipath
    error envelope of an early-late DLL for spacing d = 1 and d = 0.1 chip.
Run: python3 tools/verify/gnss_dop_errors.py   (~10 s)
"""
import numpy as np

ok_all = True
RE = 6378137.0
OMEGA_E = 7.2921151467e-5
MU = 3.986004418e14


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


def dops(az, el):
    """az, el in rad -> (GDOP, PDOP, HDOP, VDOP, TDOP)"""
    ce = np.cos(el)
    G = np.column_stack([-ce * np.sin(az), -ce * np.cos(az), -np.sin(el), np.ones_like(el)])
    H = np.linalg.inv(G.T @ G)
    return (np.sqrt(np.trace(H)), np.sqrt(H[0, 0] + H[1, 1] + H[2, 2]), np.sqrt(H[0, 0] + H[1, 1]),
            np.sqrt(H[2, 2]), np.sqrt(H[3, 3]))


# ---------------------------------------------------------------- 1. analytic geometry
def analytic_zenith_plus_three(e):
    # G^T G for 1 zenith + 3 at elevation e, azimuths 0,120,240 (derived by hand):
    # E,N diagonal: 1.5 cos^2 e each; U: 1 + 3 sin^2 e; clock: 4; U-clock cross: -(1 + 3 sin e)
    c, s = np.cos(e), np.sin(e)
    M = np.array([[1.5 * c * c, 0, 0, 0], [0, 1.5 * c * c, 0, 0],
                  [0, 0, 1 + 3 * s * s, -(1 + 3 * s)], [0, 0, -(1 + 3 * s), 4]])
    H = np.linalg.inv(M)
    return np.sqrt(H[0, 0] + H[1, 1]), np.sqrt(H[2, 2])


for e_deg in [10, 30, 60]:
    e = np.radians(e_deg)
    az = np.radians([0, 0, 120, 240]); el = np.array([np.pi / 2, e, e, e])
    g, p, h, v, t = dops(az, el)
    ha, va = analytic_zenith_plus_three(e)
    print(f"  zenith + 3 at {e_deg:2d} deg: HDOP {h:.3f} (analytic {ha:.3f})  VDOP {v:.3f} (analytic {va:.3f})")
    check(f"analytic DOP matches numeric at e={e_deg}", abs(h - ha) < 1e-9 and abs(v - va) < 1e-9)
# closed form for HDOP: sqrt(2/(1.5 cos^2 e)) = 1.1547/cos e
check("HDOP(zenith+3) = 1.1547/cos(e)", abs(dops(np.radians([0, 0, 120, 240]),
      np.array([np.pi/2]+[np.radians(30)]*3))[2] - 1.1547/np.cos(np.radians(30))) < 1e-3)

# ---------------------------------------------------------------- 2. least squares
def llh2ecef(lat, lon, h):
    a, f = 6378137.0, 1 / 298.257223563
    e2 = f * (2 - f)
    N = a / np.sqrt(1 - e2 * np.sin(lat) ** 2)
    return np.array([(N + h) * np.cos(lat) * np.cos(lon), (N + h) * np.cos(lat) * np.sin(lon),
                     (N * (1 - e2) + h) * np.sin(lat)])


def enu_matrix(lat, lon):
    return np.array([[-np.sin(lon), np.cos(lon), 0],
                     [-np.sin(lat) * np.cos(lon), -np.sin(lat) * np.sin(lon), np.cos(lat)],
                     [np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)]])


lat0, lon0 = np.radians(1.35), np.radians(103.82)       # Singapore
r0 = llh2ecef(lat0, lon0, 20.0)
Renu = enu_matrix(lat0, lon0)
rng = np.random.default_rng(3)
# 8 satellites at random az/el above 10 deg, range from a 26 560 km orbit
az = rng.uniform(0, 2 * np.pi, 8); el = np.radians(rng.uniform(10, 85, 8))
u_enu = np.column_stack([np.cos(el) * np.sin(az), np.cos(el) * np.cos(az), np.sin(el)])
u_ecef = u_enu @ Renu
rs = 26_560e3
d = -r0 @ u_ecef.T + np.sqrt((r0 @ u_ecef.T) ** 2 - (r0 @ r0 - rs ** 2))
sats = r0 + (u_ecef.T * d).T
clk = 1.2e-4 * 299792458.0          # 120 us receiver clock bias -> 36 km


def solve(pr, sats, iters=10, x0=None):
    x = np.zeros(4) if x0 is None else x0.copy()
    for _ in range(iters):
        rho = np.linalg.norm(sats - x[:3], axis=1)
        H = np.column_stack([-(sats - x[:3]) / rho[:, None], np.ones(len(pr))])
        dx = np.linalg.lstsq(H, pr - (rho + x[3]), rcond=None)[0]
        x += dx
    return x


pr_true = np.linalg.norm(sats - r0, axis=1) + clk
x = solve(pr_true, sats)
check(f"Gauss-Newton LSQ converges from Earth's centre: |dpos| = {np.linalg.norm(x[:3]-r0):.2e} m, "
      f"clock {x[3]/299792458*1e6:.1f} us", np.linalg.norm(x[:3] - r0) < 1e-3 and abs(x[3] - clk) < 1e-3)
_, pdop, hdop, vdop, _ = dops(az, el)
errs = []
for _ in range(2000):
    xx = solve(pr_true + rng.normal(0, 1.0, 8), sats, iters=3, x0=x)
    errs.append(Renu @ (xx[:3] - r0))
errs = np.array(errs)
h_rms = np.sqrt(np.mean(errs[:, 0] ** 2 + errs[:, 1] ** 2)); v_rms = np.sqrt(np.mean(errs[:, 2] ** 2))
print(f"  Monte Carlo sigma_UERE = 1 m: horizontal rms {h_rms:.2f} m (HDOP {hdop:.2f}), vertical {v_rms:.2f} m (VDOP {vdop:.2f})")
check("rms error = DOP x sigma_UERE (within 5 %)", abs(h_rms / hdop - 1) < 0.05 and abs(v_rms / vdop - 1) < 0.05)

# ---------------------------------------------------------------- 3. synthetic constellations
def circ_orbit_ecef(a, inc, raan, u0, t):
    n = np.sqrt(MU / a ** 3)
    u = u0 + n * t
    x_orb = a * np.cos(u); y_orb = a * np.sin(u)
    # to inertial
    X = x_orb * np.cos(raan) - y_orb * np.cos(inc) * np.sin(raan)
    Y = x_orb * np.sin(raan) + y_orb * np.cos(inc) * np.cos(raan)
    Z = y_orb * np.sin(inc)
    th = OMEGA_E * t
    return np.array([X * np.cos(th) + Y * np.sin(th), -X * np.sin(th) + Y * np.cos(th), Z])


def walker(T, P, F, a, inc_deg, raan0=0.0):
    sats = []
    S = T // P
    for p in range(P):
        for s_ in range(S):
            raan = raan0 + 2 * np.pi * p / P
            u0 = 2 * np.pi * s_ / S + 2 * np.pi * F * p / T
            sats.append((a, np.radians(inc_deg), raan, u0))
    return sats


def geo(lon_deg):
    a = (MU / OMEGA_E ** 2) ** (1 / 3)              # geostationary radius ~42 164 km
    return [(a, 0.0, np.radians(lon_deg), 0.0)]     # ECEF longitude = raan + u0 (constant)


def igso(lon_deg, inc_deg, n=3):
    """n satellites on one repeating figure-8 ground track, 24h/n apart:
    RAAN_k = lon + 360k/n, u0_k = -360k/n (sidereal-day geosynchronous orbit)"""
    a = (MU / OMEGA_E ** 2) ** (1 / 3)
    return [(a, np.radians(inc_deg), np.radians(lon_deg) + 2 * np.pi * k / n, -2 * np.pi * k / n)
            for k in range(n)]


const = {
    "GPS": walker(24, 6, 1, 26_559.7e3, 55),
    "GAL": walker(24, 3, 1, 29_600e3, 56),
    "BDS": walker(24, 3, 1, 27_906e3, 55) + geo(80) + geo(110.5) + geo(140) + igso(118, 55),
    "GLO": walker(24, 3, 1, 25_510e3, 64.8),
    "QZS": geo(127) + igso(139, 41),
}


def visible(sats, t, mask_fn):
    azs, els = [], []
    for (a, inc, raan, u0) in sats:
        rs = circ_orbit_ecef(a, inc, raan, u0, t)
        los = Renu @ (rs - r0)
        rho = np.linalg.norm(los)
        e = np.arcsin(los[2] / rho); z = np.arctan2(los[0], los[1])
        if mask_fn(z, e):
            azs.append(z); els.append(e)
    return np.array(azs), np.array(els)


def horizon_mask(z, e, m=np.radians(10)):
    return e > m


def run(combo, mask_fn=horizon_mask, hours=24, step=300):
    stats_ = []
    for t in np.arange(0, hours * 3600, step):
        az_all, el_all = [], []
        for cname in combo:
            a_, e_ = visible(const[cname], t, mask_fn)
            az_all += list(a_); el_all += list(e_)
        az_all, el_all = np.array(az_all), np.array(el_all)
        if len(el_all) >= 4:
            g, p, h, v, tt = dops(az_all, el_all)
        else:
            g = p = h = v = tt = np.inf
        stats_.append((len(el_all), h, v, p))
    s = np.array(stats_)
    fin = np.isfinite(s[:, 3])
    return s[:, 0].mean(), s[:, 0].min(), np.median(s[fin, 1]), np.median(s[fin, 2]), np.max(s[:, 3]), fin.mean()


print("\n  synthetic constellations seen from Singapore, 10 deg mask, 24 h (median DOPs)")
print("  combo                 n_mean n_min  HDOP   VDOP  PDOPmax  avail(>=4)")
res = {}
for combo in [("GPS",), ("GPS", "GAL"), ("GPS", "GAL", "BDS"), ("GPS", "GAL", "BDS", "GLO", "QZS")]:
    r = run(combo)
    res[combo] = r
    print(f"  {'+'.join(combo):20s} {r[0]:6.1f} {r[1]:5.0f} {r[2]:6.2f} {r[3]:6.2f} {r[4]:7.2f}  {r[5]:6.2f}")
check("multi-GNSS roughly doubles-to-quadruples satellites in view vs GPS alone",
      res[("GPS", "GAL", "BDS", "GLO", "QZS")][0] > 2.5 * res[("GPS",)][0])
check("VDOP > HDOP (no satellites below the horizon)", all(r[3] > r[2] for r in res.values()))
check("BeiDou GEO/IGSO help strongly over Singapore (GPS+GAL+BDS n_mean > 1.6x GPS+GAL)",
      res[("GPS", "GAL", "BDS")][0] > 1.6 * res[("GPS", "GAL")][0] * 0.9)


# ---------------------------------------------------------------- 4. rocket sky masks
def tilted_mask(tilt_deg, az_tilt_deg=0.0, cutoff_deg=80.0):
    """antenna boresight tilted from zenith by tilt toward az_tilt; accept sats within cutoff of boresight"""
    tb = np.radians(tilt_deg); ab = np.radians(az_tilt_deg)
    b = np.array([np.sin(tb) * np.sin(ab), np.sin(tb) * np.cos(ab), np.cos(tb)])

    def f(z, e):
        u = np.array([np.cos(e) * np.sin(z), np.cos(e) * np.cos(z), np.sin(e)])
        return (e > np.radians(5)) and (np.degrees(np.arccos(np.clip(u @ b, -1, 1))) < cutoff_deg)
    return f


combo = ("GPS", "GAL", "BDS")
print("\n  rocket antenna attitude vs GPS+GAL+BDS (M10S default) geometry, 6 h sample")
for tilt in [0, 30, 60, 90]:
    r = run(combo, tilted_mask(tilt), hours=6, step=600)
    print(f"  boresight {tilt:2d} deg from zenith: n_mean {r[0]:5.1f}  median HDOP {r[2]:6.2f}  VDOP {r[3]:6.2f}  avail {r[5]:.2f}")
    res[("tilt", tilt)] = r
check("antenna pointing sideways (90 deg) loses ~half the sky and inflates DOP",
      res[("tilt", 90)][0] < 0.75 * res[("tilt", 0)][0] and res[("tilt", 90)][2] > res[("tilt", 0)][2])

# ---------------------------------------------------------------- 5. atmosphere & multipath
P_hPa, T_K, RH, lat, h_km = 1010.0, 301.0, 0.80, np.radians(1.35), 0.02
zhd = 0.0022768 * P_hPa / (1 - 0.00266 * np.cos(2 * lat) - 0.00028 * h_km)
es = 6.11 * 10 ** (7.5 * (T_K - 273.15) / (237.3 + T_K - 273.15))
zwd = 0.002277 * (1255 / T_K + 0.05) * RH * es
print(f"\n  Saastamoinen: ZHD {zhd:.3f} m, ZWD {zwd:.3f} m (T {T_K-273.15:.0f} C, RH {RH*100:.0f} %, e {RH*es:.1f} hPa)")
check("ZHD ~ 2.3 m at sea level", 2.25 < zhd < 2.35)
check("tropical ZWD ~ 0.25-0.35 m", 0.25 < zwd < 0.35)
for e_deg in [90, 30, 10, 5]:
    print(f"    slant tropo at {e_deg:2d} deg elevation (1/sin mapping): {(zhd+zwd)/np.sin(np.radians(e_deg)):.1f} m")
for tec in [10, 50, 100]:
    print(f"  vertical TEC {tec:3d} TECU -> L1 delay {0.162*tec:5.1f} m, L2 {0.162*tec*(1575.42/1227.6)**2:5.1f} m")
f1, f2 = 1575.42, 1227.6
g1 = f1 ** 2 / (f1 ** 2 - f2 ** 2); g2 = -f2 ** 2 / (f1 ** 2 - f2 ** 2)
amp = np.sqrt(g1 ** 2 + g2 ** 2)
check(f"iono-free L1/L2 coefficients {g1:.4f}, {g2:.4f}; noise x{amp:.2f}", abs(g1 - 2.5457) < 1e-3 and abs(amp - 2.98) < 0.01)
f5 = 1176.45
amp15 = np.sqrt((f1**2/(f1**2-f5**2))**2 + (f5**2/(f1**2-f5**2))**2)
print(f"  iono-free L1/L5 noise amplification x{amp15:.2f}")


def tri(x):
    return np.clip(1 - np.abs(x), 0, None)


def mp_error(alpha, delay_chips, d, phase):
    """zero-crossing of E-L (coherent) discriminator with direct + reflected BPSK(1) correlation"""
    taus = np.linspace(-0.6, 0.6 + delay_chips, 24001)
    R = lambda t: tri(t) + alpha * np.cos(phase) * tri(t - delay_chips)
    D = R(taus - d / 2) - R(taus + d / 2)
    # find zero crossing closest to 0 with negative slope in -D convention
    idx = np.where(np.sign(D[:-1]) != np.sign(D[1:]))[0]
    zc = taus[idx]
    return zc[np.argmin(np.abs(zc))] if len(zc) else np.nan


print("\n  code-multipath error envelope, alpha = 0.5 (reflection -6 dB), in metres (1 chip = 293 m)")
print("  delay[chip]   d=1.0 in-phase  out-of-phase | d=0.1 in-phase  out-of-phase")
env = {}
for dly in [0.05, 0.1, 0.25, 0.5, 1.0, 1.2]:
    row = []
    for d in [1.0, 0.1]:
        for ph in [0, np.pi]:
            row.append(mp_error(0.5, dly, d, ph) * 293.05)
    env[dly] = row
    print(f"  {dly:8.2f}      {row[0]:8.1f}     {row[1]:8.1f}    |  {row[2]:8.1f}     {row[3]:8.1f}")
check("narrow correlator (d=0.1) has much smaller worst multipath error at 0.5 chip delay",
      abs(env[0.5][2]) < 0.3 * abs(env[0.5][0]))
check("wide correlator: in-phase error at small delay ~ alpha*delay/(1+alpha) (0.1 chip -> ~9.8 m)",
      abs(env[0.1][0] - 0.5 * 0.1 / 1.5 * 293.05) < 2.0)
check("reflections delayed > 1 + d/2 chips cause ~no error", abs(env[1.2][2]) < 1.0)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
