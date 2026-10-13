#!/usr/bin/env python3
"""
prop2_ccir.py — ITU-R P.1239 (CCIR Oslo 1966) numerical maps of foF2, M(3000)F2 and foEs, plus the
ITU-R P.533-14 basic-MUF machinery, implemented from the Recommendations (own code) and validated against the
official ITU-R SG3 reference program ITURHFProp (P.533 v14.2) example outputs.

Data: tools/verify/data/p1239_maps.npz, extracted (build_npz) from the ITU-R SG3 P.533 data files
COEFF01W.txt ... COEFF12W.txt (github.com/ITU-R-Study-Group-3/ITU-R-HF, P533/Data; arrays xf2(13,76,2),
xfm3(9,49,2), xes/xesu/xesl foEs median/upper/lower decile; index 2 = R12 0 and 100). The same foF2/M3000
coefficients ship with IRI as ccirNN.asc (max difference 1.5e-4 — rounding).

Map evaluation (P.1239 eqs 1-4 and Table 1; same algorithm as IRI GAMMA1):
  T = 15*UT - 180 (deg); for each spatial index k: c_k = U[0,k] + sum_j U[2j-1,k] sin(jT) + U[2j,k] cos(jT)
  Omega = sum_k c_k G_k(X, lat, lon), G_k = sin^q X (main latitude terms) and sin^q X cos^m(lat) {cos, sin}(m lon)
  X = modified dip = atan(I / sqrt(cos lat)), I from a 1960 field model (here IGRF-1960 truncated to n = 6) at 300 km.
Solar dependence: linear in R12 between the R12 = 0 and 100 maps, R12 capped at 160 (P.1239 §3.1).
"""
import os, re
import numpy as np
import prop2_igrf as igrf

HERE = os.path.dirname(os.path.abspath(__file__))
NPZ = os.path.join(HERE, "data", "p1239_maps.npz")
R0 = 6371.0


def build_npz(coeff_dir):
    out = {}
    for mo in range(1, 13):
        txt = open(os.path.join(coeff_dir, f"COEFF{mo:02d}W.txt")).read().replace("\r", "")
        lines = txt.split("\n")
        hdr = [i for i, l in enumerate(lines) if re.match(r"^[a-z]+\d*\(", l)]
        blocks = {}
        for a, b in zip(hdr, hdr[1:] + [len(lines)]):
            name = lines[a].split("(")[0]
            dims = tuple(int(x) for x in lines[a].split("(")[1].rstrip(")").split(","))
            nums = " ".join(lines[a + 1:b]).split()
            arr = np.array([float(x) for x in nums[:int(np.prod(dims))]])
            blocks[name] = arr.reshape(dims[::-1]).T if len(dims) > 1 else arr  # Fortran order
        for key in ("xf2", "xfm3", "xes", "xesu", "xesl"):
            out[f"{key}_{mo:02d}"] = blocks[key]
        for key in ("if2", "ifm3", "ies", "iesu", "iesl"):
            out[key] = blocks[key].astype(int)
    np.savez_compressed(NPZ, **out)
    return NPZ


_maps = None
def maps():
    global _maps
    if _maps is None:
        _maps = dict(np.load(NPZ))
    return _maps


def _nq_from_k(kseq):
    k = list(kseq[:-1]); H = int(kseq[-1])
    nq = [k[0]] + [(k[i] - k[i - 1] - 2) // 2 for i in range(1, len(k))]
    while nq and nq[-1] < 0:
        nq.pop()
    return nq, H


def eval_map(U, kseq, modip_deg, lat_deg, lon_deg, ut_h):
    """U: array (2H+1, M) for one solar level. Returns the mapped value."""
    nq, H = _nq_from_k(kseq)
    T = np.radians(15.0 * ut_h - 180.0)
    j = np.arange(1, H + 1)
    s, c = np.sin(j * T), np.cos(j * T)
    coef = U[0, :] + (U[1::2, :][:H].T @ s) + (U[2::2, :][:H].T @ c)
    sx = np.sin(np.radians(modip_deg))
    total = 0.0; idx = 0
    for q in range(nq[0] + 1):
        total += coef[idx] * sx ** q; idx += 1
    cl = np.cos(np.radians(lat_deg)); lon = np.radians(lon_deg)
    for m in range(1, len(nq)):
        for q in range(nq[m] + 1):
            base = sx ** q * cl ** m
            total += coef[idx] * base * np.cos(m * lon); idx += 1
            total += coef[idx] * base * np.sin(m * lon); idx += 1
    assert idx == U.shape[1], (idx, U.shape)
    return total


def modip1960(lat, lon):
    I = np.radians(igrf_dip_1960(lat, lon))
    return np.degrees(np.arctan(I / np.sqrt(np.cos(np.radians(lat)))))


def igrf_dip_1960(lat, lon):
    X, Y, Z = igrf.field(lat, lon, 300.0, 1960.0, nmax=6)
    return np.degrees(np.arctan2(Z, np.hypot(X, Y)))


def _two_level(name, kname, month, lat, lon, ut, R12, cap=160.0):
    m = maps(); A = m[f"{name}_{month:02d}"]           # shape (MM, M, 2)
    X = modip1960(lat, lon)
    v0 = eval_map(A[:, :, 0], m[kname], X, lat, lon % 360.0, ut)
    v1 = eval_map(A[:, :, 1], m[kname], X, lat, lon % 360.0, ut)
    R = min(R12, cap)
    return v0 + (v1 - v0) * R / 100.0


def foF2(lat, lon, month, ut, R12):
    return _two_level("xf2", "if2", month, lat, lon, ut, R12)


def M3000(lat, lon, month, ut, R12):
    return _two_level("xfm3", "ifm3", month, lat, lon, ut, R12)


def foEs(lat, lon, month, ut, R12, which="xes"):
    kname = {"xes": "ies", "xesu": "iesu", "xesl": "iesl"}[which]
    return _two_level(which, kname, month, lat, lon, ut, R12)


# ---------------- solar geometry and foE (P.1239-4 §4) ----------------
SUBSOLAR = [-21.2, -12.7, -2.2, 9.7, 18.8, 23.3, 21.6, 14.1, 3.1, -8.4, -18.4, -23.3]  # P.533 Table 4


def zenith(lat, lon, month, ut, decl=None):
    d = np.radians(SUBSOLAR[month - 1] if decl is None else decl)
    ha = np.radians((ut - 12.0) * 15.0 + lon)     # hour angle (no equation of time)
    la = np.radians(lat)
    cz = np.sin(la) * np.sin(d) + np.cos(la) * np.cos(d) * np.cos(ha)
    return np.degrees(np.arccos(np.clip(cz, -1, 1)))


def phi_from_R(R):
    return 63.7 + 0.728 * R + 0.00089 * R * R


def foE(lat, chi_deg, decl_deg, phi, hours_after_sunset=None):
    Afac = 1 + 0.0094 * (phi - 66)
    alat = abs(lat)
    if alat <= 32:
        m = -1.93 + 1.92 * np.cos(np.radians(lat)); X, Y = 23, 116
    else:
        m = 0.11 - 0.49 * np.cos(np.radians(lat)); X, Y = 92, 35
    N = lat - decl_deg if abs(lat - decl_deg) < 80 else 80.0
    B = np.cos(np.radians(N)) ** m
    C = X + Y * np.cos(np.radians(lat))
    p = 1.31 if alat <= 12 else 1.20
    chi = chi_deg
    if chi <= 73:
        D = np.cos(np.radians(chi)) ** p
    elif chi < 90:
        dchi = 6.27e-13 * (chi - 50) ** 8
        D = np.cos(np.radians(chi - dchi)) ** p
    else:
        h = hours_after_sunset if hours_after_sunset is not None else 6.0
        D = max(0.072 ** p * np.exp(-1.4 * h), 0.072 ** p * np.exp(25.2 - 0.28 * chi))
    val = (Afac * B * C * D) ** 0.25
    fmin = (0.004 * (1 + 0.021 * phi) ** 2) ** 0.25
    return max(val, fmin)


# ---------------- P.533-14 geometry and basic MUF ----------------
def gc_distance(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2); dl = np.radians(lon2 - lon1)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R0 * np.arcsin(np.sqrt(a))


def gc_point(lat1, lon1, lat2, lon2, frac):
    p1, l1, p2, l2 = map(np.radians, (lat1, lon1, lat2, lon2))
    d = 2 * np.arcsin(np.sqrt(np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin((l2 - l1) / 2) ** 2))
    A = np.sin((1 - frac) * d) / np.sin(d); B = np.sin(frac * d) / np.sin(d)
    x = A * np.cos(p1) * np.cos(l1) + B * np.cos(p2) * np.cos(l2)
    y = A * np.cos(p1) * np.sin(l1) + B * np.cos(p2) * np.sin(l2)
    z = A * np.sin(p1) + B * np.sin(p2)
    return np.degrees(np.arctan2(z, np.hypot(x, y))), np.degrees(np.arctan2(y, x))


def elevation(d_km, hr_km):
    """P.533 eq. (13): elevation angle (rad) for hop length d and mirror height hr."""
    th = d_km / (2 * R0)
    return np.arctan(1 / np.tan(th) - R0 / (R0 + hr_km) / np.sin(th))


def incidence(elev_rad, hr_km):
    return np.arcsin(R0 * np.cos(elev_rad) / (R0 + hr_km))


def max_hop(hr_km, min_elev_deg=3.0):
    e = np.radians(min_elev_deg)
    i = incidence(e, hr_km)
    return min((np.pi - i - (np.pi / 2 + e)) * R0 * 2, 4000.0)


def calcB(M, x):
    return M - 0.124 + (M * M - 4) * (0.0215 + 0.005 * np.sin(7.854 / x - 1.9635))


def calc_dmax(M, x):
    B = calcB(M, x)
    return 4780 + (12610 + 2140 / x**2 - 49720 / x**4 + 688900 / x**6) * (1 / B - 0.303)


def Cd(d, dmax):
    Z = 1 - 2 * d / dmax
    return 0.74 - 0.591 * Z - 0.424 * Z**2 - 0.090 * Z**3 + 0.088 * Z**4 + 0.181 * Z**5 + 0.096 * Z**6


def f2dmuf(foF2_, M, foE_, fH, d, dmax):
    x = max(foF2_ / foE_ if foE_ > 0 else 2.0, 2.0)
    B = calcB(M, x)
    return (1 + Cd(d, dmax) / Cd(3000.0, dmax) * (B - 1)) * foF2_ + fH / 2 * (1 - d / dmax)


def cp_params(lat, lon, month, ut, R12, solar_ut_offset=0.0):
    phi = phi_from_R(R12)
    chi = zenith(lat, lon, month, ut + solar_ut_offset)
    fe = foE(lat, chi, SUBSOLAR[month - 1], phi)
    return dict(lat=lat, lon=lon, foF2=foF2(lat, lon, month, ut, R12), M=M3000(lat, lon, month, ut, R12),
                foE=fe, fH=igrf.gyrofrequency(lat, lon, 300.0, 1960.0), chi=chi)


def basic_muf(tx, rx, month, ut, R12, nmodes=6, solar_ut_offset=0.0):
    """Return dict with distance, lowest F2 order n0 (1-based), path F2 basic MUF and per-mode basic MUFs (P.533-14
    §3.5 as coded in the ITU reference program), plus the E-layer basic MUF for D < 4000 km."""
    D = gc_distance(*tx, *rx)
    mp = cp_params(*gc_point(*tx, *rx, 0.5), month, ut, R12, solar_ut_offset)
    hr = min(1490.0 / mp["M"] - 176.0, 500.0)
    dh = max_hop(hr)
    n0 = next(n for n in range(1, 20) if dh > D / n)
    x_mp = max(mp["foF2"] / mp["foE"], 2.0)
    dmax = min(calc_dmax(mp["M"], x_mp), 4000.0)
    res = dict(D=D, hr=hr, n0=n0, dmax=dmax, mp=mp, modes={})
    if D <= dmax:
        for n in range(n0, n0 + nmodes):
            res["modes"][n] = f2dmuf(mp["foF2"], mp["M"], mp["foE"], mp["fH"], D / n, dmax)
        res["BMUF_F2"] = res["modes"][n0]
    else:
        cps = [cp_params(*gc_point(*tx, *rx, f), month, ut, R12, solar_ut_offset) for f in (1 / (2 * n0), 1 - 1 / (2 * n0))]
        res["cps"] = cps
        muf0 = [f2dmuf(c["foF2"], c["M"], c["foE"], c["fH"], D / n0, dmax) for c in cps]
        res["BMUF_F2"] = min(muf0)
        res["modes"][n0] = res["BMUF_F2"]
        dm = [calc_dmax(c["M"], max(c["foF2"] / c["foE"], 2.0)) for c in cps]
        Mn0 = [f2dmuf(c["foF2"], c["M"], c["foE"], c["fH"], D / n0, dm[i]) for i, c in enumerate(cps)]
        for n in range(n0 + 1, n0 + nmodes):
            Mn = [f2dmuf(c["foF2"], c["M"], c["foE"], c["fH"], D / n, dm[i]) for i, c in enumerate(cps)]
            res["modes"][n] = res["BMUF_F2"] * min(Mn[0] / Mn0[0], Mn[1] / Mn0[1])
    res["elev_n0_deg"] = np.degrees(elevation(D / n0, hr))
    # E modes (P.533 §3.3): lowest order with 3-deg elevation limit at 110 km, up to 4000 km
    if D < 4000:
        dhE = max_hop(110.0)
        nE = next(n for n in range(1, 10) if dhE > D / n)
        i110 = incidence(elevation(min(D / nE, 4000.0), 110.0), 110.0)
        if D < 2000:
            fe = mp["foE"]
        else:
            fe = min(cp_params(*gc_point(*tx, *rx, f), month, ut, R12, solar_ut_offset)["foE"]
                     for f in (1000 / D, 1 - 1000 / D))
        res["nE"] = nE; res["BMUF_E"] = fe / np.cos(i110)
    return res


def mode_elevations(res, hr_km=300.0):
    """Take-off elevation (deg) of each F2 mode for a fixed equivalent mirror height (P.533 eq. 13).
    NOTE: P.533 §5.1 eqs (14)-(16) give a frequency/distance-dependent hr; my transcription of those equations
    gave ~185 km for the Kranji-Beijing reference case whereas the ITU reference program's printed elevations
    imply hr = 305.8 km for every mode, so the detailed hr is NOT implemented here (unresolved; see log)."""
    return {n: np.degrees(elevation(res["D"] / n, hr_km)) for n in res["modes"]}


if __name__ == "__main__":
    import sys
    if not os.path.exists(NPZ):
        if len(sys.argv) < 2:
            sys.exit("p1239_maps.npz missing: run  python3 prop2_ccir.py <dir with COEFFmmW.txt>")
        print("built", build_npz(sys.argv[1]))
    ok = True
    def check(name, val, ref, tol):
        global ok
        good = abs(val - ref) <= tol
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] {name}: {val:.3f} (reference {ref}, tol {tol})")

    print("=== Validation against ITURHFProp (P.533 v14.2) reference outputs ===")
    print(" Kranji -> Beijing, Jan, SSN 140, input hour 2 (the reference prints the CP time as 01:00; the maps match UT = 2)")
    ref = [((10.100, 106.096), 12.023, 2.467, 2.997), ((11.135, 106.384), 12.461, 2.495, 2.986),
           ((20.824, 109.223), 13.994, 2.828, 2.953), ((30.461, 112.455), 11.763, 3.075, 2.824),
           ((31.483, 112.835), 11.596, 3.091, 2.810)]
    for ut in (1.0, 2.0):
        errs = [foF2(la, lo, 1, ut, 140) - f for (la, lo), f, M, e in ref]
        print(f"  UT {ut:.0f}: foF2 errors vs reference = {np.round(errs, 3)}")
    for (la, lo), f, M, e in ref:
        check(f"foF2 ({la},{lo})", foF2(la, lo, 1, 2.0, 140), f, 0.15)
        check(f"M3000 ({la},{lo})", M3000(la, lo, 1, 2.0, 140), M, 0.03)
    print(" Sydney example, May, SSN 10, input hour 12")
    for (la, lo), f, M in (((-23.482, 142.682), 3.590, 3.185), ((30.630, 107.344), 7.452, 3.288),
                           ((57.954, 18.467), 4.793, 3.074), ((-29.326, 147.192), 3.48, 3.144)):
        check(f"foF2 ({la},{lo})", foF2(la, lo, 5, 12.0, 10), f, 0.15)
        check(f"M3000 ({la},{lo})", M3000(la, lo, 5, 12.0, 10), M, 0.03)
    print(" foE (P.1239) at the Sydney-example midpoint: chi 83.309, decl 18.66, SSN 10")
    check("foE midpoint", foE(30.630, 83.309, 18.66, phi_from_R(10)), 1.841, 0.005)
    check("foE night minimum", foE(-29.3, 136.2, 18.66, phi_from_R(10)), 0.397, 0.005)
    print(" Basic MUF Kranji (1.42 N, 103.73 E) -> Beijing (39.95 N, 116.45 E), Jan, UT 2, SSN 140")
    r = basic_muf((1.42, 103.73), (39.95, 116.45), 1, 2.0, 140)
    print(f"  D = {r['D']:.1f} km (ref 4477.0), n0 = {r['n0']} (ref 2), dmax = {r['dmax']:.0f}, hr = {r['hr']:.1f} km (ref 350.8)")
    for n, v in r["modes"].items():
        print(f"   {n}F2 basic MUF = {v:6.2f} MHz")
    check("distance (km) [reference uses a slightly different Earth model]", r["D"], 4477.0, 6.0)
    check("path basic MUF (2F) MHz", r["BMUF_F2"], 27.770, 0.3)
    check("3F basic MUF MHz", r["modes"][3], 21.650, 0.4)
    check("hr (km)", r["hr"], 350.848, 3.0)
    print("  (elevation from the eq.(2) mirror height = %.2f deg)" % r["elev_n0_deg"])
    print("  Reference prints 2F..6F elevations 9.884/18.454/25.578/31.707/37.018 deg = eq.(13) with hr = 305.8 km:")
    el = mode_elevations(r, 305.8)
    for n, refel in ((2, 9.884), (3, 18.454), (4, 25.578), (5, 31.707), (6, 37.018)):
        check(f"{n}F elevation, eq.(13) with hr = 305.8 km (deg)", el[n], refel, 0.15)
    print(" Reference program quirk: it evaluates the maps at UT = input hour but the solar geometry (foE) at hour - 1.")
    chi_ref = 70.719
    check("foE at Kranji-Beijing midpoint with the reference's chi = 70.719 deg", foE(20.824, chi_ref, -21.2, phi_from_R(140)), 2.953, 0.03)
    r2 = basic_muf((1.42, 103.73), (39.95, 116.45), 1, 2.0, 140, solar_ut_offset=-1.0)
    check("path basic MUF reproducing that quirk (MHz) [residual = reference's 1.5-deg grid interpolation of foF2]", r2["BMUF_F2"], 27.770, 0.25)
    # eq. (3) fed with the reference program's own control-point values (T + d0/2): must reproduce 27.770 exactly
    v = f2dmuf(12.461, 2.495, 2.986, 0.982, 4477.003 / 2, 4000.0)
    check("eq.(3) with the reference CP values (T+d0/2)", v, 27.770, 0.01)
    print("\nALL PASS" if ok else "\nSOME CHECKS FAILED")
