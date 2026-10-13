#!/usr/bin/env python3
"""
s1_df_bearing.py — practical direction finding (DF) for recovering a landed rocket at 434 MHz.

Used by: kb/12-phased-arrays/adaptive-beamforming-doa.md, section "Practical direction finding for rocket recovery".

Sections
  §1  3-element handheld Yagi at 434.125 MHz (PyNEC): gain, HPBW, F/B, and the bearing error of
      three reading methods (peak, -3 dB edge bisection, rear null) for a given S-meter resolution.
  §2  Pseudo-Doppler (commutated circular array): Monte Carlo of the bearing error vs the derived
      formula sigma_alpha = lambda / (pi * D * sqrt(K * SNR)).
  §3  Watson-Watt / Adcock: octantal (spacing) error, exact vs the small-spacing result (u^2/24) sin 4θ.
  §4  Bearing-error budget (RSS) for three field methods.
  §5  Two-station triangulation: analytic covariance (GDOP) vs Monte Carlo, and a check against
      20/phased-array-starter-build (2 km baseline, target 5 km, 1° -> median 220 m).
  §6  Close-in hunt: received power vs distance (free space and flat-earth two-ray, landed antenna
      0.1 m, handheld 1.5 m) for the licence-exempt 10 mW e.r.p. and the licensed 2 W cases, and the
      attenuation needed to keep the receiver at or below -60 dBm.

Run:  python3 tools/verify/s1_df_bearing.py      (about 10 s)
"""
import math
import numpy as np

C = 299_792_458.0
F = 434.125e6            # E22 CH 24, the canonical Singapore channel
LAM = C / F
rng = np.random.default_rng(1)
checks = []


def check(name, ok):
    checks.append((name, bool(ok)))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")


# ---------------------------------------------------------------- §1 Yagi
print("=== §1 3-element handheld Yagi at 434.125 MHz (PyNEC) ===")
STEP = 0.25
ang = np.arange(-180, 180, STEP)          # angle off boresight (deg)
# elements in wavelengths (found by a small F/B search with gain > 7 dBi; 6 mm rod)
L = [0.525 * LAM, 0.47 * LAM, 0.42 * LAM]
X = [0.0, 0.15 * LAM, 0.27 * LAM]
try:
    from PyNEC import nec_context

    def yagi_cut(plane, a=0.003, seg=21):
        """Gain (dBi) vs angle off boresight. Elements along y, boom along +x.
        plane='E': cut in the x-y plane (the elements' plane: horizontal elements, azimuth swing);
        plane='H': cut in the x-z plane (elements vertical, azimuth swing)."""
        c = nec_context()
        g = c.get_geometry()
        for i, (l, x) in enumerate(zip(L, X)):
            g.wire(i + 1, seg, x, -l / 2, 0, x, l / 2, 0, a, 1, 1)
        c.geometry_complete(0)
        c.ex_card(0, 2, seg // 2 + 1, 0, 1.0, 0, 0, 0, 0, 0)
        c.fr_card(0, 1, F / 1e6, 0)
        n = int(round(360 / STEP))
        if plane == "E":
            c.rp_card(0, 1, n, 0, 0, 0, 0, 90, 0, 0, STEP, 0, 0)     # phi sweep, theta = 90
            G = np.array(c.get_radiation_pattern(0).get_gain()).flatten()
            off = np.arange(n) * STEP
        else:
            c.rp_card(0, n, 1, 0, 0, 0, 0, 0, 0, STEP, 0, 0, 0)      # theta sweep, phi = 0
            G = np.array(c.get_radiation_pattern(0).get_gain()).flatten()
            off = np.arange(n) * STEP - 90.0
        z = c.get_input_parameters(0).get_impedance()[0]
        off = (off + 180) % 360 - 180
        order = np.argsort(off)
        return np.interp(ang, off[order], G[order]), z

    GE, z = yagi_cut("E")
    GH, _ = yagi_cut("H")
except Exception as e:                                   # PyNEC missing: Gaussian-beam fallback
    print("  PyNEC not available (", e, ") -> Gaussian beam fallback")
    GE = np.maximum(7.3 - 12 * (ang / 66.0) ** 2, -40)
    GH = np.maximum(7.3 - 12 * (ang / 100.0) ** 2, -40)
    z = complex(50, 0)

r_db = 1.0        # S-meter / RSSI reading resolution (dB)
FLOOR = -25.0     # assumed fill-in of a null by reflections and receiver floor, relative to the peak


def crossings(rel, level, lo, hi):
    m = (ang >= lo) & (ang <= hi)
    a, r = ang[m], rel[m]
    idx = np.where(np.diff(np.sign(r - level)) != 0)[0]
    out = []
    for i in idx:
        x = a[i] + (a[i + 1] - a[i]) * (level - r[i]) / (r[i + 1] - r[i])
        out.append((x, abs(r[i + 1] - r[i]) / (a[i + 1] - a[i])))
    return out


def methods(G, name):
    rel = G - G.max()
    c3 = crossings(rel, -3.0, -120, 120)
    hpbw = c3[-1][0] - c3[0][0]
    s3 = np.mean([s for _, s in c3])
    w_peak = -crossings(rel, -r_db, -90, 0)[0][0]
    res = {"gain": G.max(), "hpbw": hpbw, "fb": rel[np.argmin(np.abs(ang - 179.75))] * -1,
           "peak": w_peak / math.sqrt(3), "bisect": r_db / s3 / math.sqrt(2), "slope3": s3}
    # nulls: deepest point outside the main beam, then the FLOOR crossings around it
    out = np.abs(ang) > hpbw
    nulls = []
    for centre in ([-90, 90] if name == "E" else [180]):
        if centre == 180:
            cr = crossings(rel, FLOOR, 120, 179.75) + crossings(rel, FLOOR, -179.75, -120)
        else:
            cr = crossings(rel, FLOOR, centre - 40, centre + 40)
        if len(cr) >= 2:
            nulls.append((centre, r_db / np.mean([s for _, s in cr]) / math.sqrt(2),
                          abs(cr[-1][0] - cr[0][0]) / 2 if centre != 180 else 180 - min(abs(x) for x, _ in cr)))
    res["nulls"] = nulls
    return res


print(f"  elements R/DE/D = 0.525/0.47/0.42 λ, spacings 0.15/0.12 λ (boom {0.27*LAM*100:.1f} cm), 6 mm rod; "
      f"Zin {z.real:.0f}{z.imag:+.0f}j Ω")
RES = {}
for nm, G in [("E", GE), ("H", GH)]:
    r = methods(G, nm)
    RES[nm] = r
    pol = "horizontal elements (E-plane swing)" if nm == "E" else "vertical elements (H-plane swing)"
    print(f"  {pol}: gain {r['gain']:.1f} dBi, HPBW {r['hpbw']:.0f}°, F/B {r['fb']:.0f} dB")
    print(f"     reading resolution {r_db:.0f} dB → peak σ ≈ {r['peak']:.0f}°, −3 dB-edge bisection σ ≈ {r['bisect']:.1f}°"
          f" (slope {r['slope3']:.2f} dB/°)")
    for c_, sn, w in r["nulls"]:
        print(f"     null at {c_:+.0f}°: bisect the {FLOOR:.0f} dB crossings (half-width {w:.0f}°) → σ ≈ {sn:.2f}°")
E_ = RES["E"]
check("edge bisection beats peak reading by > 2.5x (E-plane)", E_["peak"] / E_["bisect"] > 2.5)
check("E-plane side-null bisection finer than −3 dB bisection", min(s for _, s, _ in E_["nulls"]) < E_["bisect"])
check("Gaussian edge-slope rule 12/θ3 within 30 % of NEC (E-plane)", abs(12 / E_["hpbw"] / E_["slope3"] - 1) < 0.3)
sig_peak, sig_bisect = E_["peak"], E_["bisect"]
sig_null = min(s for _, s, _ in E_["nulls"])
YAGI_GAIN = E_["gain"]

# ---------------------------------------------------------------- §2 pseudo-Doppler
print("\n=== §2 Pseudo-Doppler: commutated 4- and 8-element circle ===")


def pdoppler_trial(alpha, D_l, n_el, n_rot, sps, snr_db):
    """One bearing estimate. Elements on a circle of diameter D (λ); the switch steps through
    elements; each element is sampled sps times per dwell. Phase of each sample = k R cos(phi_n - alpha)
    + carrier phase + noise. Estimate alpha from the first Fourier coefficient of the unwrapped phase."""
    R = D_l / 2
    phin = 2 * np.pi * np.arange(n_el) / n_el
    seq = np.tile(np.repeat(np.arange(n_el), sps), n_rot)
    ph = 2 * np.pi * R * np.cos(phin[seq] - alpha) + 0.7
    snr = 10 ** (snr_db / 10)
    noise = (rng.standard_normal(len(seq)) + 1j * rng.standard_normal(len(seq))) / math.sqrt(2 * snr)
    x = np.exp(1j * ph) + noise
    # remove the common phase, then project onto cos/sin of the element angle
    p = np.angle(x * np.exp(-1j * np.angle(np.mean(x))))
    a = np.sum(p * np.cos(phin[seq])); b = np.sum(p * np.sin(phin[seq]))
    return math.atan2(b, a)


for n_el, D_l in [(4, 0.25), (8, 0.4)]:
    for snr_db in [10, 20]:
        n_rot, sps = 50, 4
        K = n_rot * n_el * sps
        errs = []
        for _ in range(400):
            al = rng.uniform(0, 2 * np.pi)
            e = (pdoppler_trial(al, D_l, n_el, n_rot, sps, snr_db) - al + np.pi) % (2 * np.pi) - np.pi
            errs.append(e)
        mc = math.degrees(np.std(errs))
        th = math.degrees(1 / (math.pi * D_l * math.sqrt(K * 10 ** (snr_db / 10))))
        print(f"  N={n_el}, D={D_l}λ ({D_l*LAM*100:.0f} cm), SNR {snr_db} dB/sample, K={K}: "
              f"MC σ = {mc:.3f}°, formula λ/(πD√(K·SNR)) = {th:.3f}°")
        check(f"pseudo-Doppler formula within 35 % (N={n_el}, {snr_db} dB)", abs(mc / th - 1) < 0.35)
# commutation arithmetic for a LoRa packet
fr = 1000.0
D_l = 0.4
print(f"  rotation {fr:.0f} Hz on D = 0.4λ: peak Doppler deviation Δf = π D f_r/λ·λ = {math.pi*D_l*fr:.0f} Hz; "
      f"a 72 ms SF7/125 packet holds {0.072*fr:.0f} rotations")

# ---------------------------------------------------------------- §3 Adcock
print("\n=== §3 Watson-Watt / 4-element Adcock octantal error ===")
th = np.radians(np.arange(0, 360, 0.1))
for d_l in [0.1, 0.25, 0.5]:
    u = math.pi * d_l
    est = np.arctan2(np.sin(u * np.sin(th)), np.sin(u * np.cos(th)))
    err = np.degrees((est - th + np.pi) % (2 * np.pi) - np.pi)
    approx = math.degrees(u ** 2 / 24)
    print(f"  opposite-element spacing d = {d_l}λ: max octantal error exact {np.abs(err).max():.2f}°, "
          f"(πd/λ)²/24 = {approx:.2f}°")
    if d_l <= 0.25:
        check(f"octantal small-spacing formula within 10 % at d={d_l}λ", abs(np.abs(err).max() / approx - 1) < 0.1)

# ---------------------------------------------------------------- §4 budget
print("\n=== §4 Bearing-error budgets (1σ, degrees, RSS) ===")
budgets = {
    "handheld Yagi, -3 dB bisection": {"reading": sig_bisect, "multipath/terrain": 5, "operator/compass": 2, "declination/map": 1},
    "handheld Yagi, side/rear null": {"reading": sig_null, "multipath/terrain": 5, "operator/compass": 2, "declination/map": 1},
    "handheld Yagi, peak only": {"reading": sig_peak, "multipath/terrain": 5, "operator/compass": 2, "declination/map": 1},
    "KrakenSDR UCA (calibrated, -10 dB multipath)": {"noise+phase cal": 0.65, "coherent multipath": 2.5, "array heading": 1, "declination/map": 1},
    "pseudo-Doppler 4-el, 0.25λ": {"noise": 0.2, "multipath (sampling/aliasing)": 5, "array heading": 2, "declination/map": 1},
}
for k, v in budgets.items():
    tot = math.sqrt(sum(x * x for x in v.values()))
    print(f"  {k:46s} -> {tot:4.1f}°   ({', '.join(f'{a} {b:.1f}' for a, b in v.items())})")
check("bisection budget < 8°", math.sqrt(sum(x*x for x in budgets['handheld Yagi, -3 dB bisection'].values())) < 8)

# ---------------------------------------------------------------- §5 triangulation
print("\n=== §5 Two-station triangulation ===")


def tri_cov(stations, target, sig_deg):
    H = []
    W = []
    for s in stations:
        dx, dy = target - s
        r2 = dx * dx + dy * dy
        H.append([-dy / r2, dx / r2])          # d(bearing)/d(x,y)
        W.append(1 / math.radians(sig_deg) ** 2)
    H = np.array(H); Wm = np.diag(W)
    return np.linalg.inv(H.T @ Wm @ H)


def tri_mc(stations, target, sig_deg, n=4000):
    errs = []
    for _ in range(n):
        lines = []
        for s in stations:
            b = math.atan2(*(target - s)[::-1]) + math.radians(sig_deg) * rng.standard_normal()
            lines.append((s, np.array([math.cos(b), math.sin(b)])))
        (p1, u1), (p2, u2) = lines
        A = np.array([u1, -u2]).T
        try:
            t = np.linalg.solve(A, p2 - p1)
        except np.linalg.LinAlgError:
            continue
        errs.append(np.linalg.norm(p1 + t[0] * u1 - target))
    return np.median(errs), np.percentile(errs, 90)


st = [np.array([-1000.0, 0]), np.array([1000.0, 0])]
tg = np.array([0.0, 5000.0])
for sd in [1, 2, 5]:
    P = tri_cov(st, tg, sd)
    ev = np.sqrt(np.linalg.eigvalsh(P))
    med, p90 = tri_mc(st, tg, sd)
    print(f"  baseline 2 km, target 5 km broadside, σ = {sd}°: ellipse 1σ axes {ev[0]:.0f} m × {ev[1]:.0f} m; "
          f"MC median {med:.0f} m, 90 % {p90:.0f} m")
    if sd == 1:
        check("MC median within 15 % of recipe 220 m", abs(med / 220 - 1) < 0.15)
# better geometry: 90° crossing
st2 = [np.array([-5000.0, 0]), np.array([0.0, -5000.0])]
tg2 = np.array([0.0, 0.0])
P = tri_cov(st2, tg2, 1)
ev = np.sqrt(np.linalg.eigvalsh(P))
print(f"  same 1° but stations 5 km away at 90° to each other: axes {ev[0]:.0f} m × {ev[1]:.0f} m "
      f"(= R·σ = {5000*math.radians(1):.0f} m each)")
check("90° geometry gives R·σ per axis", abs(ev[1] - 5000 * math.radians(1)) < 2)

# ---------------------------------------------------------------- §6 close-in table
print("\n=== §6 Close-in hunt: received power at the handheld Yagi ===")
eirp = {"10 mW e.r.p. (licence-exempt)": 10 + 2.15, "2 W, 33 dBm, −0.5 dB, 2.15 dBi (licensed)": 33 - 0.5 + 2.15}
ht, hr = 0.1, 1.5          # landed antenna (canonical set) and hand height
gr = YAGI_GAIN
k = 2 * math.pi / LAM
print(f"  handheld Yagi {gr:.1f} dBi; two-ray: plane earth, Γ = −1, h_t = {ht} m, h_r = {hr} m; "
      f"target ≤ −60 dBm at the receiver")
dists = [5000, 2000, 1000, 300, 100, 30, 10, 3, 1]
for name, e in eirp.items():
    print(f"  {name}:")
    print("    d (m)   FSPL-only Pr   two-ray Pr   attenuation for ≤ −60 dBm (two-ray / free space)")
    for d in dists:
        fspl = 20 * math.log10(4 * math.pi * d / LAM)
        pr_fs = e + gr - fspl
        f2 = 2 * abs(math.sin(k * ht * hr / d))
        pr_2r = pr_fs + 20 * math.log10(max(f2, 1e-9))
        need = lambda p: max(0.0, p + 60)
        print(f"    {d:6.0f}   {pr_fs:8.1f} dBm   {pr_2r:8.1f} dBm   {need(pr_2r):5.0f} / {need(pr_fs):5.0f} dB")
pr1 = eirp["2 W, 33 dBm, −0.5 dB, 2.15 dBi (licensed)"] + gr - 20 * math.log10(4 * math.pi * 1 / LAM)
check("2 W at 1 m exceeds the SX126x +10 dBm abs-max at a 7 dBi Yagi", pr1 > 10)

print("\nSummary:", sum(ok for _, ok in checks), "of", len(checks), "checks pass")
