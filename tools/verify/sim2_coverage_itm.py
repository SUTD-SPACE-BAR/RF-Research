#!/usr/bin/env python3
"""sim2_coverage_itm.py — terrain-based coverage prediction with the ITM (Longley-Rice) port in tools/rfcalc,
run on a real launch-range terrain profile, compared with the KB's flat-earth two-ray / plane-earth numbers;
and a simulation of why "mapper" coverage data (TTN-Mapper style: only received packets are logged) are
censored and bias path-loss fits. W5-S11, gap G-16-02. Page: kb/16-simulation-tools/tool-landscape-overview.md
("Terrain coverage: ITM on a real profile" and "Why mapper data lie").

PROFILE: 100 SRTM 90 m (srtm90m) elevations along latitude 32.9900 N from 106.97000 W to 106.81000 W
(14.92 km, spacing 150.7 m on a 6371 km sphere), from the OpenTopoData public API (api.opentopodata.org, queried 2026-10-13).
This is the desert plain east of Spaceport America, New Mexico (the Spaceport America Cup / IREC range used by
many university teams). It is an EXAMPLE site — the Space Bar notes do not record the team's launch sites.
Ground station at the west end (5 m mast), landed rocket at distance d to the east.

PRE-REGISTERED EXPECTATIONS (written 2026-10-13 before the first run; addenda only below)
  T1  Flat profile (all elevations equal), h 5 m / 0.5 m, 433.92 MHz, H-pol, medium-dry ground: the ITM median
      basic transmission loss is within +-6 dB of the flat-earth two-ray model over 2-15 km (ITM's line-of-sight
      region is an empirical blend of two-ray and diffraction; its effective heights also differ).
  T2  On the real profile (gentle rise of ~150 m over 15 km, small delta_h), ITM differs from the flat-profile ITM
      by less than 6 dB at every distance (no ridge blocks the path).
  T3  ITM refuses the canonical 0.1 m rocket antenna (hard error below 0.5 m; warning below 1 m): the KB's
      canonical landed case cannot be run in ITM at all; 0.5 m is the closest allowed height.
  T4  With the canonical budget (33 dBm, 0 dBi rocket, 11 dBic Yagi, -3 dB polarisation, -1 dB feeder;
      2.4 kb/s sensitivity -128 dBm), ITM on the real profile with the rocket antenna at 0.5 m keeps positive
      margin over the whole 15 km profile; two-ray at 0.5 m also does (canonical 0.1 m two-ray: zero margin at
      11.5 km).
  C1  Mapper censoring: path loss PL = PL(1 m) + 10 n log10(d) + X, n = 3.5, sigma = 8 dB, receiver threshold
      fixed; logging only received packets and fitting OLS gives n_hat LOW by > 0.5 and sigma_hat low by > 2 dB.
  C2  A censored (Tobit) maximum-likelihood fit using the failed attempts (positions known, level unknown)
      recovers n within 0.15 and sigma within 0.7 dB; a truncated-regression MLE using only the received
      packets plus the known threshold recovers n within 0.3.
  C3  The naive fit's "range at the threshold" is optimistic by > 25 %.

ADDENDUM 1 (2026-10-13, after run 1). T2 MISSED by a wide margin: on the real profile ITM's loss at 10-15 km is
  ~50 dB BELOW the flat-profile ITM (near free space). Cause: the profile is concave (dips to 1386 m, rises to
  1552 m); ITM's effective heights are taken above a least-squares line through the terrain, so both terminals
  get tens of metres of effective height (delta_h 92 m) and the two-ray cancellation that dominates the flat
  case disappears. This is ITM's documented heuristic, applied here to a 0.5 m antenna outside its validated
  range (RX-height warning). To show the sign can reverse, a post-hoc CONVEX control (the same profile mirrored
  top-to-bottom, i.e. a 160 m hump between the stations) is added below; it was not pre-registered.
  C1 MISSED narrowly (sigma low by 1.92 dB, threshold 2); C2 MISSED for the truncated-regression MLE (n +0.82):
  with only 20 % of packets received, all at short range, truncation alone identifies n poorly.

Run: python3 tools/verify/sim2_coverage_itm.py      (~10 s)   -> sim2_coverage_results.txt
"""
import os
import sys

import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from rfcalc import itm                  # noqa: E402
from prop_two_ray import two_ray_loss   # noqa: E402

ELEV_SRTM90 = [1401.0, 1401.0, 1397.0, 1402.0, 1399.0, 1397.0, 1397.0, 1394.0, 1396.0, 1398.0, 1401.0, 1394.0,
               1394.0, 1394.0, 1389.0, 1389.0, 1390.0, 1386.0, 1389.0, 1389.0, 1392.0, 1391.0, 1392.0, 1395.0,
               1397.0, 1400.0, 1397.0, 1396.0, 1400.0, 1400.0, 1400.0, 1404.0, 1402.0, 1403.0, 1404.0, 1406.0,
               1407.0, 1411.0, 1412.0, 1413.0, 1415.0, 1415.0, 1418.0, 1416.0, 1417.0, 1423.0, 1422.0, 1426.0,
               1425.0, 1430.0, 1429.0, 1433.0, 1436.0, 1438.0, 1439.0, 1443.0, 1444.0, 1448.0, 1449.0, 1453.0,
               1454.0, 1455.0, 1458.0, 1464.0, 1464.0, 1467.0, 1470.0, 1473.0, 1473.0, 1476.0, 1480.0, 1482.0,
               1484.0, 1489.0, 1489.0, 1490.0, 1492.0, 1495.0, 1499.0, 1501.0, 1503.0, 1505.0, 1506.0, 1509.0,
               1511.0, 1515.0, 1518.0, 1519.0, 1522.0, 1526.0, 1531.0, 1533.0, 1537.0, 1540.0, 1541.0, 1544.0,
               1545.0, 1547.0, 1549.0, 1552.0]
LAT = 32.99
SPACING = (0.16 * np.pi / 180) * 6371e3 * np.cos(np.radians(LAT)) / 99      # m
F = 433.92e6
H_GS, H_ROCKET = 5.0, 0.5
ER, SIG = 15.0, 1e-3
BUDGET = 33 + 0 + 11 - 3 - 1          # dBm + dBi + dBic - pol - feeder  (canonical set, 09 Example E)
SENS = -128.0
OUT = []


def p(s):
    print(s)
    OUT.append(s)


def itm_loss(elev, n_pts):
    pfl = itm.profile_from_elevations(elev[:n_pts], SPACING)
    r = itm.itm_p2p_tls(H_GS, H_ROCKET, pfl, climate=4, N_0=301, f_mhz=F / 1e6, pol=0, epsilon=ER, sigma=SIG,
                        mdvar=12, time_pct=50, location_pct=50, situation_pct=50)
    return r


def part_terrain():
    p(f"Profile: {len(ELEV_SRTM90)} SRTM90 points, spacing {SPACING:.1f} m, length {SPACING*99/1e3:.2f} km, "
      f"elevation {min(ELEV_SRTM90):.0f}-{max(ELEV_SRTM90):.0f} m")
    elev = np.array(ELEV_SRTM90)
    flat = np.full_like(elev, elev[0])
    p(f"{'d km':>6} | {'FSPL':>6} | {'2-ray 0.5m':>10} | {'2-ray 0.1m':>10} | {'ITM flat':>8} | {'ITM real':>8} "
      f"| {'mode':>11} | {'dh m':>5} | margin ITM-real / 2-ray 0.5 m (dB)")
    t1, t2, t4 = [], [], []
    for n_pts in (8, 14, 21, 34, 47, 67, 87, 100):
        d = SPACING * (n_pts - 1)
        fs = 20 * np.log10(4 * np.pi * d * F / 299792458.0)
        tr = float(two_ray_loss(d, H_GS, H_ROCKET, F, ER, SIG, "H"))
        tr01 = float(two_ray_loss(d, H_GS, 0.1, F, ER, SIG, "H"))
        rf = itm_loss(flat, n_pts)
        rr = itm_loss(elev, n_pts)
        m_itm, m_tr = BUDGET - rr["A_db"] - SENS, BUDGET - tr - SENS
        p(f"{d/1e3:6.2f} | {fs:6.1f} | {tr:10.1f} | {tr01:10.1f} | {rf['A_db']:8.1f} | {rr['A_db']:8.1f} | "
          f"{rr['mode_name']:>11} | {rr['delta_h_m']:5.1f} | {m_itm:+6.1f} / {m_tr:+6.1f}"
          + (f"  [{', '.join(rr['warning_names'])}]" if rr["warning_names"] else ""))
        if d >= 2e3:
            t1.append(rf["A_db"] - tr)
        t2.append(rr["A_db"] - rf["A_db"])
        t4.append((m_itm, m_tr))
    p(f"T1 {'PASS' if max(abs(x) for x in t1) <= 6 else 'MISS'}: ITM(flat) - two-ray over 2-15 km: "
      f"{min(t1):+.1f} ... {max(t1):+.1f} dB")
    p(f"T2 {'PASS' if max(abs(x) for x in t2) <= 6 else 'MISS'}: ITM(real) - ITM(flat): "
      f"{min(t2):+.1f} ... {max(t2):+.1f} dB")
    try:
        itm.itm_p2p_tls(H_GS, 0.1, itm.profile_from_elevations(elev[:30], SPACING), 4, 301, F / 1e6, 0, ER, SIG, 12,
                        50, 50, 50)
        p("T3 MISS: ITM accepted a 0.1 m antenna")
    except ValueError as e:
        p(f"T3 PASS: ITM rejects h = 0.1 m ({e})")
    ok = all(a > 0 and b > 0 for a, b in t4)
    p(f"T4 {'PASS' if ok else 'MISS'}: margins at 15 km: ITM {t4[-1][0]:+.1f} dB, two-ray(0.5 m) {t4[-1][1]:+.1f} dB")
    # POST-HOC convex control (addendum 1): mirrored profile = hump between the stations
    conv = elev.max() + elev.min() - elev
    for n_pts in (34, 67, 100):
        d = SPACING * (n_pts - 1)
        rc = itm_loss(conv, n_pts)
        p(f"   post-hoc convex control at {d/1e3:5.2f} km: ITM {rc['A_db']:.1f} dB ({rc['mode_name']}), vs flat "
          f"{itm_loss(flat, n_pts)['A_db']:.1f} dB")
    # area mode with the profile's delta_h, for comparison
    rr = itm_loss(elev, 100)
    ra = itm.itm_area_tls(H_GS, H_ROCKET, 0, 0, SPACING * 99 / 1e3, rr["delta_h_m"], 4, 301, F / 1e6, 0, ER, SIG, 12,
                          50, 50, 50)
    p(f"Area mode at 14.94 km with the profile's delta_h {rr['delta_h_m']:.1f} m: {ra['A_db']:.1f} dB "
      f"(p2p {rr['A_db']:.1f} dB); area mode with delta_h 90 m (ITM default 'average terrain'): "
      f"{itm.itm_area_tls(H_GS, H_ROCKET, 0, 0, 14.94, 90, 4, 301, F/1e6, 0, ER, SIG, 12, 50, 50, 50)['A_db']:.1f} dB")
    # variability: 90 % location / 90 % time on the full path
    for t, l_ in ((50, 50), (90, 50), (50, 90), (90, 90)):
        r = itm.itm_p2p_tls(H_GS, H_ROCKET, itm.profile_from_elevations(elev, SPACING), 4, 301, F / 1e6, 0, ER, SIG,
                            2, t, l_, 50)
        p(f"   mobile-mode variability, time {t} % / location {l_} %: A = {r['A_db']:.1f} dB")


def part_censoring(seed=5):
    rng = np.random.default_rng(seed)
    n_true, sig_true, pl0 = 3.5, 8.0, 40.0
    eirp, thr = 14.0, -120.0                      # dBm: a 25 mW node and a gateway threshold
    d = 10 ** rng.uniform(np.log10(200), np.log10(20e3), 4000)
    x = 10 * np.log10(d)
    pl = pl0 + n_true * x + sig_true * rng.standard_normal(d.size)
    pr = eirp - pl
    got = pr > thr
    p(f"Mapper simulation: {d.size} attempts 0.2-20 km, n = {n_true}, sigma = {sig_true} dB, threshold {thr} dBm: "
      f"{got.sum()} received ({100*got.mean():.0f} %)")
    # naive OLS on received only
    A = np.vstack([np.ones(got.sum()), x[got]]).T
    coef, *_ = np.linalg.lstsq(A, pl[got], rcond=None)
    resid = pl[got] - A @ coef
    n_ols, s_ols = coef[1], resid.std(ddof=2)
    # Tobit (censored): received -> density; failed -> P(PL > eirp - thr)
    plmax = eirp - thr

    def nll_tobit(th):
        a, n, ls = th
        s = np.exp(ls)
        mu = a + n * x
        ll = norm.logpdf(pl[got], mu[got], s).sum() + norm.logsf(plmax, mu[~got], s).sum()
        return -ll

    def nll_trunc(th):
        a, n, ls = th
        s = np.exp(ls)
        mu = a + n * x[got]
        return -(norm.logpdf(pl[got], mu, s) - norm.logcdf(plmax, mu, s)).sum()

    tb = minimize(nll_tobit, [coef[0], coef[1], np.log(s_ols)], method="Nelder-Mead",
                  options=dict(maxiter=20000, xatol=1e-6, fatol=1e-6))
    tr = minimize(nll_trunc, [coef[0], coef[1], np.log(s_ols)], method="Nelder-Mead",
                  options=dict(maxiter=20000, xatol=1e-6, fatol=1e-6))
    n_tb, s_tb = tb.x[1], np.exp(tb.x[2])
    n_tr, s_tr = tr.x[1], np.exp(tr.x[2])
    p(f"  naive OLS on received packets: n {n_ols:.2f}, sigma {s_ols:.2f} dB, PL(1 m) {coef[0]:.1f} dB")
    p(f"  Tobit MLE (failed attempts' positions known): n {n_tb:.2f}, sigma {s_tb:.2f} dB, PL(1 m) {tb.x[0]:.1f} dB")
    p(f"  truncated MLE (received only + known threshold): n {n_tr:.2f}, sigma {s_tr:.2f} dB, PL(1 m) {tr.x[0]:.1f} dB")
    p(f"C1 {'PASS' if (n_true - n_ols) > 0.5 and (sig_true - s_ols) > 2 else 'MISS'}: naive n low by "
      f"{n_true-n_ols:.2f}, sigma low by {sig_true-s_ols:.2f} dB")
    p(f"C2 {'PASS' if abs(n_tb-n_true) <= 0.15 and abs(s_tb-sig_true) <= 0.7 and abs(n_tr-n_true) <= 0.3 else 'MISS'}: "
      f"Tobit n error {n_tb-n_true:+.2f}, sigma error {s_tb-sig_true:+.2f} dB; truncated n error {n_tr-n_true:+.2f}")
    # median range at the threshold
    r_true = 10 ** ((plmax - pl0) / (10 * n_true))
    r_ols = 10 ** ((plmax - coef[0]) / (10 * n_ols))
    p(f"C3 {'PASS' if r_ols / r_true - 1 > 0.25 else 'MISS'}: median range where PL = {plmax:.0f} dB: true "
      f"{r_true/1e3:.2f} km, naive fit {r_ols/1e3:.2f} km ({100*(r_ols/r_true-1):+.0f} %), Tobit "
      f"{10**((plmax-tb.x[0])/(10*n_tb))/1e3:.2f} km")
    # where are the received packets? the fraction received in the outer decade
    far = d > 5e3
    p(f"  received fraction beyond 5 km: {100*got[far].mean():.0f} % — the far points that ARE logged are the lucky "
      f"(low-loss) tail, so a map of logged points shows coverage where the median link fails")


def main():
    p("=== Part 1: ITM on a real launch-range profile vs flat-earth models (433.92 MHz, H-pol, GS 5 m, rocket 0.5 m) ===")
    part_terrain()
    p("=== Part 2: censored mapper data ===")
    part_censoring()
    with open(os.path.join(HERE, "sim2_coverage_results.txt"), "w") as fh:
        fh.write("\n".join(OUT) + "\n")


if __name__ == "__main__":
    main()
