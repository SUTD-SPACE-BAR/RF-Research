#!/usr/bin/env python3
"""
s13_gnss_ephemeris.py - verification for kb/21-gnss/gnss-error-sources-dop.md
  (section "Coordinate frames, satellite positions from the broadcast ephemeris, and integrity (RAIM)")
  and for the Wi-Fi/LoRa IMD row of kb/21-gnss/gnss-interference-jamming-spoofing.md.

 1. WGS-84 geodetic <-> ECEF (closed form forward, Bowring/iterative inverse); round trip and an
    independent cross-check against astropy's EarthLocation (WGS84).
 2. ECEF -> local ENU rotation, azimuth/elevation/range of a satellite.
 3. Satellite ECEF position from a broadcast Keplerian ephemeris (IS-GPS-200 Table 20-IV;
    Galileo OS SIS ICD 5.1.1 uses the same algorithm with mu = 3.986004418e14): a real GPS
    record (G01, toe 2026-10-05 12:00 GPST) and a real Galileo I/NAV record (E19) embedded below,
    plus the satellite clock polynomial with the relativistic term.
 4. Optional (needs files, see RUN): a whole day of broadcast ephemerides (BKG BRDC merged RINEX 3
    nav, 2026-10-05) compared with the IGS rapid orbit (SP3, IGS0OPSRAP 2026-278) every 15 min:
    radial / along / cross-track differences per system.  Then the real GPS and GPS+Galileo sky
    over Singapore for 24 h: satellites in view and HDOP/VDOP (compare the synthetic numbers on
    the page).
 5. Pseudorange simulation with light time and Earth rotation (Sagnac) -> Gauss-Newton LS
    recovers the receiver position and clock (checks the whole transform chain).
 6. RAIM: least-squares residual chi-square fault detection; theoretical P_d vs Monte Carlo;
    per-satellite slope and the horizontal protection level (HPL); exclusion by largest
    normalised residual.
 7. Frequencies only: 3rd-order products 2*f_LoRa - f_WiFi and f_WiFi - 2*f_LoRa for Wi-Fi ch 6/11
    and LoRa 434.125 MHz -> GPS L1 / GLONASS G1 overlap (no product LEVEL is computed).

Pre-registered expectations (written before the first run, 2026-10-13):
  P1 geodetic round trip < 1 mm; astropy agreement < 1 mm.
  P2 GPS broadcast vs IGS rapid: along- and cross-track RMS < 2 m, 3-D RMS < 5 m;
     Galileo along/cross RMS < 1 m.  (Radial carries the antenna phase-centre offset, because the
     broadcast orbit refers to the antenna and SP3 to the centre of mass; reported, not tested.)
  P3 LS from simulated pseudoranges recovers position < 1 mm and clock < 1 mm.
  P4 real-constellation 24 h medians (10 deg mask, GPS only) within 0.3 of the page's synthetic
     HDOP 0.89 and within 0.5 of VDOP 1.70.
  P5 RAIM Monte Carlo P_d within 0.02 of the non-central chi-square value.

RUN:  python3 tools/verify/s13_gnss_ephemeris.py                      (sections 1-3, 5-7, offline)
      python3 tools/verify/s13_gnss_ephemeris.py BRDC.rnx IGS.SP3     (adds section 4)
      files used for the page: BRDC00WRD_S_20262780000_01D_MN.rnx and
      IGS0OPSRAP_20262780000_01D_15M_ORB.SP3 from https://igs.bkg.bund.de/root_ftp/IGS/
"""
import sys
import numpy as np
from scipy import stats

ok_all = True
A_WGS = 6378137.0
F_WGS = 1 / 298.257223563
E2 = F_WGS * (2 - F_WGS)
OMEGA_E = 7.2921151467e-5
MU_GPS = 3.986005e14
MU_GAL = 3.986004418e14
C = 299792458.0
F_REL = -4.442807633e-10          # s / sqrt(m)


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


# ---------------------------------------------------------------- 1. geodetic <-> ECEF
def geod2ecef(lat, lon, h):
    N = A_WGS / np.sqrt(1 - E2 * np.sin(lat) ** 2)
    return np.array([(N + h) * np.cos(lat) * np.cos(lon), (N + h) * np.cos(lat) * np.sin(lon),
                     (N * (1 - E2) + h) * np.sin(lat)])


def ecef2geod(r):
    x, y, z = r
    lon = np.arctan2(y, x)
    p = np.hypot(x, y)
    lat = np.arctan2(z, p * (1 - E2))
    for _ in range(10):
        N = A_WGS / np.sqrt(1 - E2 * np.sin(lat) ** 2)
        h = p / np.cos(lat) - N
        lat = np.arctan2(z, p * (1 - E2 * N / (N + h)))
    N = A_WGS / np.sqrt(1 - E2 * np.sin(lat) ** 2)
    h = p / np.cos(lat) - N
    return lat, lon, h


def enu_matrix(lat, lon):
    sl, cl, sp, cp = np.sin(lon), np.cos(lon), np.sin(lat), np.cos(lat)
    return np.array([[-sl, cl, 0], [-sp * cl, -sp * sl, cp], [cp * cl, cp * sl, sp]])


def azel(r_sat, r_rx, lat, lon):
    d = enu_matrix(lat, lon) @ (r_sat - r_rx)
    rng = np.linalg.norm(d)
    return np.arctan2(d[0], d[1]) % (2 * np.pi), np.arcsin(d[2] / rng), rng


print("=== 1. WGS-84 geodetic <-> ECEF ===")
SG = (np.radians(1.3521), np.radians(103.8198), 15.0)       # Singapore, 15 m ellipsoidal height
r_sg = geod2ecef(*SG)
print(f"Singapore 1.3521N 103.8198E h 15 m -> ECEF = {r_sg.round(3)} m")
lat2, lon2, h2 = ecef2geod(r_sg)
err = np.linalg.norm(geod2ecef(lat2, lon2, h2) - r_sg)
check(f"round trip (incl. h = 15 m): {err*1e3:.2e} mm < 1 mm", err < 1e-3)
worst = 0
for latd in (-89.9, -45, 0.0, 30, 60, 89.9):
    for h in (-100, 0, 1e4, 1e5, 2.02e7):
        g = geod2ecef(np.radians(latd), 0.7, h)
        la, lo, hh = ecef2geod(g)
        worst = max(worst, abs(hh - h), abs(la - np.radians(latd)) * A_WGS)
check(f"inverse over lat +-89.9 deg, h -100 m ... 20 200 km: worst {worst*1e3:.2e} mm", worst < 1e-3)
try:
    from astropy.coordinates import EarthLocation
    import astropy.units as u
    el_ = EarthLocation.from_geodetic(lon=103.8198 * u.deg, lat=1.3521 * u.deg, height=15 * u.m,
                                      ellipsoid='WGS84')
    ra = np.array([el_.x.to_value(u.m), el_.y.to_value(u.m), el_.z.to_value(u.m)])
    check(f"astropy EarthLocation agrees: {np.linalg.norm(ra-r_sg)*1e3:.3f} mm", np.linalg.norm(ra - r_sg) < 1e-3)
except Exception as exc:                                     # pragma: no cover
    print("astropy cross-check skipped:", exc)
# meridian radius / 1 deg of latitude at the equator
M0 = A_WGS * (1 - E2)
print(f"1 deg latitude at the equator = {np.radians(1)*M0:.1f} m; 1 deg longitude = {np.radians(1)*A_WGS:.1f} m")

# ---------------------------------------------------------------- 3. broadcast ephemeris
G01 = """G01 2026 10 05 12 00 00 1.566307619214e-04-8.640199666843e-12 0.000000000000e+00
     1.800000000000e+01 4.675000000000e+01 4.441613582463e-09-4.600051527410e-01
     2.497807145119e-06 2.030315692537e-03 9.216368198395e-06 5.153749500275e+03
     1.296000000000e+05 4.097819328308e-08-7.488339216300e-01-1.490116119385e-08
     9.563254956869e-01 2.008437500000e+02 1.579440937941e-01-8.057835641198e-09
    -4.143029716675e-11 1.000000000000e+00 2.439000000000e+03 0.000000000000e+00
     2.000000000000e+00 0.000000000000e+00-8.847564458847e-09 7.860000000000e+02
     9.999000000000e+08"""
E19 = """E19 2026 10 05 12 00 00 3.250845358707e-03 1.956834694283e-11 0.000000000000e+00
     8.900000000000e+01-1.429687500000e+02 3.089771558530e-09 2.797154032419e+00
    -6.660819053650e-06 1.287974882871e-04 5.366280674934e-06 5.440630691528e+03
     1.296000000000e+05 1.862645149231e-09 1.499023519204e+00-1.061707735062e-07
     9.748172322505e-01 2.288437500000e+02 7.617909592626e-01-5.744524996810e-09
    -2.342954736326e-10 5.170000000000e+02 2.439000000000e+03 0.000000000000e+00
     3.120000000000e+00 0.000000000000e+00-4.190951585770e-09-4.423782229424e-09
     9.999000000000e+08"""


def parse_record(lines):
    """RINEX 3 GPS/Galileo nav record (8 lines) -> dict."""
    l0 = lines[0]
    sv = l0[:3]
    y, mo, d, hh, mi, ss = (int(l0[4:8]), int(l0[9:11]), int(l0[12:14]), int(l0[15:17]),
                            int(l0[18:20]), int(l0[21:23]))
    vals = [float(l0[23 + 19 * k: 42 + 19 * k].replace('D', 'e')) for k in range(3)]
    for ln in lines[1:]:
        ln = ln.rstrip('\n').ljust(80)
        for k in range(4):
            s = ln[4 + 19 * k: 23 + 19 * k].strip()
            vals.append(float(s.replace('D', 'e')) if s else 0.0)
    keys = ['af0', 'af1', 'af2', 'iode', 'crs', 'dn', 'm0', 'cuc', 'e', 'cus', 'sqrta', 'toe', 'cic',
            'omega0', 'cis', 'i0', 'crc', 'omega', 'omegadot', 'idot', 'codes', 'week', 'l2p',
            'acc', 'health', 'tgd', 'iodc', 'ttm', 'fit']
    eph = dict(zip(keys, vals))
    eph['sv'] = sv
    # time of clock as GPS seconds of week (both GPST and GST weeks start Sunday 00:00)
    import datetime as _dt
    t = _dt.datetime(y, mo, d, hh, mi, ss)
    wd = (t.weekday() + 1) % 7
    eph['toc'] = wd * 86400 + hh * 3600 + mi * 60 + ss
    return eph


def kepler_pos(eph, t, mu):
    """ECEF position (m) at GPS second-of-week t; returns (r, Ek, tk)."""
    A = eph['sqrta'] ** 2
    tk = t - eph['toe']
    tk -= 604800 * np.round(tk / 604800)
    n = np.sqrt(mu / A ** 3) + eph['dn']
    M = eph['m0'] + n * tk
    E = M
    for _ in range(30):
        E = E - (E - eph['e'] * np.sin(E) - M) / (1 - eph['e'] * np.cos(E))
    nu = np.arctan2(np.sqrt(1 - eph['e'] ** 2) * np.sin(E), np.cos(E) - eph['e'])
    phi = nu + eph['omega']
    s2, c2 = np.sin(2 * phi), np.cos(2 * phi)
    uk = phi + eph['cus'] * s2 + eph['cuc'] * c2
    rk = A * (1 - eph['e'] * np.cos(E)) + eph['crs'] * s2 + eph['crc'] * c2
    ik = eph['i0'] + eph['cis'] * s2 + eph['cic'] * c2 + eph['idot'] * tk
    xp, yp = rk * np.cos(uk), rk * np.sin(uk)
    Om = eph['omega0'] + (eph['omegadot'] - OMEGA_E) * tk - OMEGA_E * eph['toe']
    return np.array([xp * np.cos(Om) - yp * np.cos(ik) * np.sin(Om),
                     xp * np.sin(Om) + yp * np.cos(ik) * np.cos(Om),
                     yp * np.sin(ik)]), E, tk


def sat_clock(eph, t, E):
    dt = t - eph['toc']
    dt -= 604800 * np.round(dt / 604800)
    rel = F_REL * eph['e'] * eph['sqrta'] * np.sin(E)
    return eph['af0'] + eph['af1'] * dt + eph['af2'] * dt ** 2 + rel, rel


print("\n=== 3. Satellite position from a real broadcast ephemeris ===")
g01 = parse_record(G01.splitlines())
e19 = parse_record(E19.splitlines())
t_ex = 1 * 86400 + 12 * 3600         # Monday 2026-10-05 12:00:00 GPST (= toe, 20:00 SGT)
for eph, mu, name in ((g01, MU_GPS, 'G01'), (e19, MU_GAL, 'E19')):
    r, E, tk = kepler_pos(eph, t_ex, mu)
    dts, rel = sat_clock(eph, t_ex, E)
    A = eph['sqrta'] ** 2
    print(f"{name}: a = {A/1e3:.1f} km, e = {eph['e']:.5f}, i0 = {np.degrees(eph['i0']):.2f} deg, "
          f"tk = {tk:.0f} s, E = {np.degrees(E):.3f} deg")
    print(f"     ECEF at 12:00 GPST = ({r[0]/1e3:.3f}, {r[1]/1e3:.3f}, {r[2]/1e3:.3f}) km, |r| = {np.linalg.norm(r)/1e3:.3f} km")
    print(f"     sat clock = {dts*1e6:.4f} us (relativistic part {rel*1e9:.2f} ns = {rel*C:.2f} m)")
    az, el, rng = azel(r, r_sg, SG[0], SG[1])
    print(f"     from Singapore: az {np.degrees(az):.2f} deg, el {np.degrees(el):.2f} deg, range {rng/1e3:.1f} km")
    check(f"{name}: |r| within [a(1-e), a(1+e)] + 2 km", A * (1 - eph['e']) - 2e3 < np.linalg.norm(r) < A * (1 + eph['e']) + 2e3)
# orbital period
for eph, mu, name in ((g01, MU_GPS, 'GPS'), (e19, MU_GAL, 'Galileo')):
    A = eph['sqrta'] ** 2
    T = 2 * np.pi * np.sqrt(A ** 3 / mu)
    print(f"{name} period {T/3600:.4f} h ({T/86164.0905*2:.4f} x half sidereal day)")
# velocity by finite difference vs vis-viva (inertial speed needs Earth-rotation term)
r1, _, _ = kepler_pos(g01, t_ex - 0.5, MU_GPS)
r2, _, _ = kepler_pos(g01, t_ex + 0.5, MU_GPS)
v_ecef = r2 - r1
rm, _, _ = kepler_pos(g01, t_ex, MU_GPS)
v_in = v_ecef + np.cross([0, 0, OMEGA_E], rm)
A = g01['sqrta'] ** 2
vv = np.sqrt(MU_GPS * (2 / np.linalg.norm(rm) - 1 / A))
check(f"G01 inertial speed {np.linalg.norm(v_in):.2f} m/s vs vis-viva {vv:.2f} m/s (< 1 m/s; harmonics in the Cxx terms)",
      abs(np.linalg.norm(v_in) - vv) < 1.0)
print(f"G01 ECEF speed {np.linalg.norm(v_ecef):.1f} m/s; inertial {np.linalg.norm(v_in):.1f} m/s")

# ---------------------------------------------------------------- 4. day of ephemerides vs SP3
GAL_MED = None


def read_nav(path):
    out = {}
    with open(path) as f:
        lines = f.readlines()
    i = next(k for k, l in enumerate(lines) if 'END OF HEADER' in l) + 1
    while i < len(lines):
        l = lines[i]
        sysc = l[0]
        if sysc in 'GE':
            rec = lines[i:i + 8]
            try:
                eph = parse_record(rec)
                if int(eph['health']) == 0:
                    out.setdefault(eph['sv'], []).append(eph)
            except Exception:
                pass
            i += 8
        elif sysc in 'RSJIC':
            n = {'R': 4, 'S': 4}.get(sysc, 8)
            i += n
        else:
            i += 1
    return out


def read_sp3(path):
    pos = {}
    t = None
    with open(path) as f:
        for l in f:
            if l.startswith('*'):
                p = l.split()
                hh, mi, ss = int(p[4]), int(p[5]), float(p[6])
                t = 86400 + hh * 3600 + mi * 60 + ss          # file is 2026-10-05 (Monday)
            elif l.startswith('P') and t is not None:
                sv = l[1:4]
                x, y, z = (float(l[4:18]), float(l[18:32]), float(l[32:46]))
                if abs(x) > 1e-3:
                    pos.setdefault(sv, {})[t] = np.array([x, y, z]) * 1e3
    return pos


def best_eph(lst, t):
    cands = [e for e in lst if abs(t - e['toe']) <= 2 * 3600 + 600]   # 4 h fit interval centred on toe
    if not cands:
        return None
    return min(cands, key=lambda e: abs(t - e['toe']))


if len(sys.argv) >= 3:
    print("\n=== 4. Broadcast vs IGS rapid orbit, 2026-10-05, every 15 min ===")
    nav = read_nav(sys.argv[1])
    sp3 = read_sp3(sys.argv[2])
    res = {'G': [], 'E': []}
    per_sat_radial = {}
    for sv, tab in sp3.items():
        if sv[0] not in 'GE' or sv not in nav:
            continue
        mu = MU_GPS if sv[0] == 'G' else MU_GAL
        for t, rp in tab.items():
            eph = best_eph(nav[sv], t)
            if eph is None:
                continue
            rb, _, _ = kepler_pos(eph, t, mu)
            # RAC frame from the precise state (velocity by finite difference of broadcast)
            rb2, _, _ = kepler_pos(eph, t + 1, mu)
            v = rb2 - rb + np.cross([0, 0, OMEGA_E], rb)
            eR = rp / np.linalg.norm(rp)
            eC = np.cross(rp, v); eC /= np.linalg.norm(eC)
            eA = np.cross(eC, eR)
            d = rb - rp
            dr = np.array([d @ eR, d @ eA, d @ eC])
            if np.linalg.norm(d) > 100:         # stale/bad record guard
                continue
            res[sv[0]].append(dr)
            per_sat_radial.setdefault(sv, []).append(dr[0])
    if 'G01' in sp3 and t_ex in sp3['G01']:
        rb, _, _ = kepler_pos(g01, t_ex, MU_GPS)
        print(f"G01 12:00 GPST: SP3 {(sp3['G01'][t_ex]/1e3).round(3)} km; broadcast - SP3 = {(rb-sp3['G01'][t_ex]).round(2)} m (|d| {np.linalg.norm(rb-sp3['G01'][t_ex]):.2f} m)")
    for s, name in (('G', 'GPS'), ('E', 'Galileo')):
        a = np.array(res[s])
        if a.size == 0:
            print(f"{name}: no precise orbits in this SP3 (IGS rapid is GPS-only) - P2 for {name} NOT TESTED")
            continue
        rms = np.sqrt(np.mean(a ** 2, axis=0))
        rms3 = np.sqrt(np.mean(np.sum(a ** 2, axis=1)))
        nsat = len({k for k in per_sat_radial if k[0] == s})
        print(f"{name}: {len(a)} epochs x sats ({nsat} sats); RMS radial {rms[0]:.2f} m, along {rms[1]:.2f} m, "
              f"cross {rms[2]:.2f} m, 3-D {rms3:.2f} m; median radial {np.median(a[:,0]):+.2f} m")
        scat = np.sqrt(np.mean([np.var(v) for k, v in per_sat_radial.items() if k[0] == s]))
        print(f"   radial scatter about each satellite's daily mean (removes the constant antenna offset): {scat:.2f} m")
        if s == 'G':
            check(f"P2 GPS along {rms[1]:.2f} m and cross {rms[2]:.2f} m < 2 m", rms[1] < 2 and rms[2] < 2)
            check(f"P2 GPS 3-D RMS {rms3:.2f} m < 5 m", rms3 < 5)
        else:
            check(f"P2 Galileo along {rms[1]:.2f} m and cross {rms[2]:.2f} m < 1 m", rms[1] < 1 and rms[2] < 1)

    print("\n--- real sky over Singapore, 2026-10-05, 10 deg mask, every 10 min ---")
    def sky(systems, t):
        az_l, el_l = [], []
        for sv, lst in nav.items():
            if sv[0] not in systems:
                continue
            eph = best_eph(lst, t)
            if eph is None:
                continue
            r, _, _ = kepler_pos(eph, t, MU_GPS if sv[0] == 'G' else MU_GAL)
            az, el, _ = azel(r, r_sg, SG[0], SG[1])
            if el > np.radians(10):
                az_l.append(az); el_l.append(el)
        return np.array(az_l), np.array(el_l)

    def dops(az, el, nclk=1, sysidx=None):
        ce = np.cos(el)
        G = np.column_stack([-ce * np.sin(az), -ce * np.cos(az), -np.sin(el)])
        if nclk == 1:
            G = np.column_stack([G, np.ones_like(el)])
        else:
            G = np.column_stack([G, (sysidx == 0).astype(float), (sysidx == 1).astype(float)])
        H = np.linalg.inv(G.T @ G)
        return np.sqrt(H[0, 0] + H[1, 1]), np.sqrt(H[2, 2])

    out = {'G': [], 'GE1': [], 'GE2': []}
    for t in np.arange(86400, 2 * 86400, 600):
        az, el = sky('G', t)
        if len(az) < 4:
            continue
        out['G'].append((len(az),) + dops(az, el))
        azg, elg = sky('G', t); aze, ele = sky('E', t)
        az2 = np.r_[azg, aze]; el2 = np.r_[elg, ele]
        idx = np.r_[np.zeros(len(azg)), np.ones(len(aze))]
        out['GE1'].append((len(az2),) + dops(az2, el2))
        out['GE2'].append((len(az2),) + dops(az2, el2, nclk=2, sysidx=idx))
    for k, lab in (('G', 'GPS only'), ('GE1', 'GPS+GAL, one clock (GGTO known)'),
                   ('GE2', 'GPS+GAL, two clocks')):
        a = np.array(out[k])
        print(f"{lab:34s}: sats median {np.median(a[:,0]):.1f} (min {a[:,0].min():.0f}); HDOP median {np.median(a[:,1]):.2f} "
              f"(max {a[:,1].max():.2f}); VDOP median {np.median(a[:,2]):.2f} (max {a[:,2].max():.2f})")
    a = np.array(out['G'])
    check(f"P4 GPS-only median HDOP {np.median(a[:,1]):.2f} within 0.3 of synthetic 0.89", abs(np.median(a[:, 1]) - 0.89) < 0.3)
    check(f"P4 GPS-only median VDOP {np.median(a[:,2]):.2f} within 0.5 of synthetic 1.70", abs(np.median(a[:, 2]) - 1.70) < 0.5)
    print(f"GPS satellites healthy in file: {len([k for k in nav if k[0]=='G'])}; Galileo: {len([k for k in nav if k[0]=='E'])}")
else:
    print("\n(section 4 skipped: pass BRDC nav and SP3 paths to run it)")

# ---------------------------------------------------------------- 5. pseudorange LS with Sagnac
print("\n=== 5. Simulated pseudoranges (light time + Earth rotation) -> least squares ===")
# Build a geometry from the two real satellites plus synthetic ones placed by rotating G01's orbit.
rng_ = np.random.default_rng(1)
sats_eph = []
for p_ in range(6):                    # a GPS-like 6-plane x 6-slot constellation built from G01's elements
    for k in range(6):
        e = dict(g01)
        e['omega0'] = g01['omega0'] + 2 * np.pi * p_ / 6
        e['m0'] = g01['m0'] + 2 * np.pi * k / 6 + 0.5 * p_
        sats_eph.append(e)
t_rx = t_ex
b_true = 3.0e-4 * C          # 300 us receiver clock bias -> 89.9 km
rx_true = geod2ecef(SG[0], SG[1], 3000.0)      # a rocket at 3 km
obs = []
for e in sats_eph:
    tau = 0.075
    for _ in range(10):
        rs, _, _ = kepler_pos(e, t_rx - tau, MU_GPS)
        th = OMEGA_E * tau
        Rz = np.array([[np.cos(th), np.sin(th), 0], [-np.sin(th), np.cos(th), 0], [0, 0, 1]])
        rs_rot = Rz @ rs
        tau = np.linalg.norm(rs_rot - rx_true) / C
    az, el, _ = azel(rs_rot, rx_true, SG[0], SG[1])
    if el > np.radians(5):
        obs.append((e, np.linalg.norm(rs_rot - rx_true) + b_true))
print(f"{len(obs)} satellites above 5 deg in the synthetic set")
x = np.zeros(4)
for it in range(10):
    Gm, dr = [], []
    for e, pr in obs:
        tau = (pr - x[3]) / C
        rs, _, _ = kepler_pos(e, t_rx - tau, MU_GPS)
        th = OMEGA_E * tau
        Rz = np.array([[np.cos(th), np.sin(th), 0], [-np.sin(th), np.cos(th), 0], [0, 0, 1]])
        rs = Rz @ rs
        rho = np.linalg.norm(rs - x[:3])
        Gm.append(np.r_[-(rs - x[:3]) / rho, 1.0])
        dr.append(pr - rho - x[3])
    dx = np.linalg.lstsq(np.array(Gm), np.array(dr), rcond=None)[0]
    x += dx
    if np.linalg.norm(dx) < 1e-6:
        break
perr = np.linalg.norm(x[:3] - rx_true)
check(f"P3 LS from the Earth's centre in {it+1} iterations: position error {perr*1e3:.3f} mm, clock error {abs(x[3]-b_true)*1e3:.3f} mm",
      perr < 1e-3 and abs(x[3] - b_true) < 1e-3)
# Sagnac size if ignored
sag = []
for e, pr in obs:
    rs, _, _ = kepler_pos(e, t_rx - 0.075, MU_GPS)
    sag.append(OMEGA_E / C * (rs[0] * rx_true[1] - rs[1] * rx_true[0]))
print(f"Sagnac range term omega_E (x_s y_r - y_s x_r)/c for these satellites: {min(sag):.1f} ... {max(sag):.1f} m")

# ---------------------------------------------------------------- 6. RAIM
print("\n=== 6. RAIM (snapshot least-squares residual test) ===")
# geometry: GPS-only-like, 8 satellites
az = np.radians([10, 60, 115, 170, 220, 265, 310, 0])
el = np.radians([15, 40, 25, 60, 20, 35, 50, 85])
ce = np.cos(el)
G = np.column_stack([-ce * np.sin(az), -ce * np.cos(az), -np.sin(el), np.ones_like(el)])
n = len(el)
sigma = 3.0
Amat = np.linalg.inv(G.T @ G) @ G.T
S = np.eye(n) - G @ Amat
pfa, pmd = 3.33e-7, 1e-3            # RTCA DO-229-style per-sample allocations
dof = n - 4
TD = stats.chi2.isf(pfa, dof)
# non-centrality giving P_md
lam = __import__('scipy.optimize', fromlist=['brentq']).brentq(
    lambda L: stats.ncx2.cdf(TD, dof, L) - pmd, 1, 500)
slope = np.sqrt((Amat[0] ** 2 + Amat[1] ** 2) / np.diag(S))
hpl = slope.max() * sigma * np.sqrt(lam)
hd = np.sqrt(np.trace(np.linalg.inv(G.T @ G)[:2, :2]))
print(f"n = {n}, dof = {dof}, threshold T_D = {TD:.2f} (chi2, Pfa {pfa:g}); lambda for Pmd {pmd:g} = {lam:.1f}")
print(f"slopes = {slope.round(2)}; HDOP {hd:.2f}; HPL = max slope x sigma x sqrt(lambda) = {hpl:.1f} m (sigma {sigma} m)")
# Monte Carlo at a bias giving Pd 0.9 on the worst-slope satellite
iw = int(slope.argmax())
lam90 = __import__('scipy.optimize', fromlist=['brentq']).brentq(
    lambda L: stats.ncx2.sf(TD, dof, L) - 0.9, 1, 500)
bias = sigma * np.sqrt(lam90 / S[iw, iw])
N = 40000
eps = rng_.normal(0, sigma, (N, n))
eps[:, iw] += bias
r = eps @ S.T
T = np.sum(r ** 2, axis=1) / sigma ** 2
pd_mc = np.mean(T > TD)
check(f"P5 bias {bias:.1f} m on sat {iw}: P_d MC {pd_mc:.3f} vs theory 0.900", abs(pd_mc - 0.9) < 0.02)
eps0 = rng_.normal(0, sigma, (N, n))
pfa_mc = np.mean(np.sum((eps0 @ S.T) ** 2, axis=1) / sigma ** 2 > stats.chi2.isf(1e-2, dof))
check(f"false-alarm MC at Pfa 1e-2 threshold: {pfa_mc:.4f}", abs(pfa_mc - 1e-2) < 3e-3)
herr = np.hypot((eps @ Amat.T)[:, 0], (eps @ Amat.T)[:, 1])
print(f"with that bias: horizontal error median {np.median(herr):.1f} m; undetected cases' max {herr[T<=TD].max():.1f} m (HPL {hpl:.1f} m)")
# exclusion
wn = np.abs(r) / (sigma * np.sqrt(np.diag(S)))
for mult in (1.0, 2.0):
    eps = rng_.normal(0, sigma, (N, n)); eps[:, iw] += mult * bias
    rr = eps @ S.T
    hit = np.mean(np.argmax(np.abs(rr) / (sigma * np.sqrt(np.diag(S))), axis=1) == iw)
    print(f"exclusion by largest normalised residual, bias {mult*bias:.0f} m: correct satellite {hit*100:.1f} %")
rho_corr = np.abs(S / np.sqrt(np.outer(np.diag(S), np.diag(S))))
np.fill_diagonal(rho_corr, 0)
print(f"largest residual correlation between satellites: {rho_corr.max():.2f} (limits exclusion)")

# ---------------------------------------------------------------- 7. Wi-Fi / LoRa IMD frequencies
print("\n=== 7. 3rd-order IMD frequencies: Wi-Fi ch 6/11 and LoRa 434.125 MHz (frequencies only) ===")
f_lora = 434.125
for ch in (1, 6, 11, 13):
    fw = 2412 + 5 * (ch - 1)
    lo, hi = fw - 11 - 2 * (f_lora + 0.0625), fw + 11 - 2 * (f_lora - 0.0625)
    print(f"ch {ch:2d} ({fw} MHz, +-11 MHz): f_WiFi - 2 f_LoRa = {fw-2*f_lora:.2f} MHz, span {lo:.2f} ... {hi:.2f} MHz;"
          f" 2 f_LoRa - f_WiFi < 0 (no product)")
l1 = (1575.42 - 1.023, 1575.42 + 1.023)
g1 = (1602 - 7 * 0.5625 - 0.511, 1602 + 6 * 0.5625 + 0.511)
f6 = (2437 - 11 - 2 * 434.1875, 2437 + 11 - 2 * 434.0625)
f11 = (2462 - 11 - 2 * 434.1875, 2462 + 11 - 2 * 434.0625)
check(f"ch 6 product {f6[0]:.2f}-{f6[1]:.2f} MHz covers GPS L1 C/A {l1[0]:.2f}-{l1[1]:.2f}", f6[0] < l1[0] and f6[1] > l1[1])
check(f"ch 11 product {f11[0]:.2f}-{f11[1]:.2f} MHz overlaps GLONASS G1 {g1[0]:.2f}-{g1[1]:.2f}", f11[0] < g1[1] and f11[1] > g1[0])
check("ch 11 product misses GPS L1 C/A main lobe", f11[0] > l1[1])
f1 = (2412 - 11 - 2 * 434.1875, 2412 + 11 - 2 * 434.0625)
print(f"ch 1 product {f1[0]:.2f}-{f1[1]:.2f} MHz (BeiDou B1I 1561.098 MHz +-2.046 inside: {f1[0] < 1559.05 and f1[1] > 1563.14})")

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
