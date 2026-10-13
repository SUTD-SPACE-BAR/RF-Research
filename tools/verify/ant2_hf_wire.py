#!/usr/bin/env python3
"""ant2_hf_wire.py -- NEC-2 (PyNEC) + analytic checks for
kb/08-antennas/wire-antennas-hf-random-wire-fan-dipole.md (W5-E2).

Pre-registered expectations (written before the first run):
 1. End-fed wire against a short counterpoise: |Z| peaks (kOhm) where L ~ n lambda/2 and dips (tens of ohm)
    near odd lambda/4; a 20.1 m wire is bad on 40/20/15/10 m (all near n*lambda/2); a 'recommended' 71 ft
    (21.6 m) wire is not within ~5 % of a half-wave multiple on any band.  Own length search recovers lengths
    close to the VE3EED list for 80-10 m.
 2. Fan dipole 40 m + 20 m joined at one feed: each keeps a resonance near its own band but the 20 m element
    resonance shifts by a few percent (interaction); the 40 m wire's own 3rd harmonic near 21 MHz remains.
 3. Inverted-V: feed R falls from ~70 ohm (flat) toward ~50 ohm at 120 deg and ~35-40 ohm at 90 deg apex
    (free space); resonant length increases slightly (less end capacitance coupling? -> sign to be found).
 4. OCF: R at fundamental ~ R_c / cos^2(k z) for feed offset z; at 33 % feed, moderate R (100-300 ohm) on
    f1, 2f1, 4f1 but very high on 3f1.
 5. G5RV (31.1 m top, 10.36 m electrical of 450 ohm line): VSWR on 50 ohm ~1.5-2.5 on 20 m only; > 5 elsewhere.
 6. NVIS: horizontal dipole over average ground (er 13, sigma 5 mS/m) at 0.1-0.25 lambda radiates its maximum
    straight up; at 0.5 lambda the zenith becomes a null-ish dip and the lobe goes to ~30 deg.
 7. Trap dipole (W3DZZ-like): two resonances near 3.7 and 7.05 MHz with traps resonant at 7.05 MHz.
 8. Vertical with elevated radials over real ground: space-wave fraction rises with radial count.
Run: python3 tools/verify/ant2_hf_wire.py      (~1-3 min)
"""
import numpy as np
import PyNEC

C0 = 299792458.0
BANDS = {"160": (1.8, 2.0), "80": (3.5, 4.0), "60": (5.3305, 5.4065), "40": (7.0, 7.3), "30": (10.1, 10.15),
         "20": (14.0, 14.35), "17": (18.068, 18.168), "15": (21.0, 21.45), "12": (24.89, 24.99), "10": (28.0, 29.7)}
EPS_G, SIG_G = 13.0, 0.005           # 'average' ground
ok = True


def check(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(f"[{'PASS' if cond else 'MISS'}] {name} {detail}")


def nec(wires, f_mhz, feed, ground=None, loads=(), pattern=None, tl=None):
    """wires: list of (p0, p1, radius, nseg). feed: (wire_index, seg 1-based). ground None | 'som' | 'pec'.
    loads: list of (ldtyp, wire_index, seg, R, L, C). pattern: (nth, nph, th0, dth, dph) -> returns gains."""
    c = PyNEC.nec_context()
    g = c.get_geometry()
    for i, (p0, p1, a, ns) in enumerate(wires):
        g.wire(i + 1, ns, p0[0], p0[1], p0[2], p1[0], p1[1], p1[2], a, 1.0, 1.0)
    c.geometry_complete(1 if ground == "pec" else 0)
    if ground == "som":
        c.gn_card(2, 0, EPS_G, SIG_G, 0, 0, 0, 0)
    elif ground == "pec":
        c.gn_card(1, 0, 0, 0, 0, 0, 0, 0)
    else:
        c.gn_card(-1, 0, 0, 0, 0, 0, 0, 0)
    for (lt, wi, sg, R, L, Cc) in loads:
        c.ld_card(lt, wi + 1, sg, sg, R, L, Cc)
    c.ex_card(0, feed[0] + 1, feed[1], 0, 1.0, 0, 0, 0, 0, 0)
    fl = np.atleast_1d(f_mhz)
    out = []
    for fm in fl:
        c.fr_card(0, 1, float(fm), 0)
        if pattern is None:
            c.xq_card(0)
            out.append(complex(c.get_input_parameters(len(out)).get_impedance()[0]))
        else:
            nth, nph, th0, dth, dph = pattern
            c.rp_card(0, nth, nph, 0, 0, 0, 0, th0, 0.0, dth, dph, 0, 0)
            rp = c.get_radiation_pattern(len(out))
            out.append((complex(c.get_input_parameters(len(out)).get_impedance()[0]),
                        np.array(rp.get_gain()), np.array(rp.get_theta_angles())))
    return out if np.ndim(f_mhz) else out[0]


def zin_line(ZL, Z0, bl):
    t = np.tan(bl)
    return Z0 * (ZL + 1j * Z0 * t) / (Z0 + 1j * ZL * t)


def vswr(Z, Z0=50.0):
    G = abs((Z - Z0) / (Z + Z0))
    return (1 + G) / (1 - G) if G < 1 else np.inf


# ------------------------------------------------------------------ 1. random / end-fed wire
print("=== 1. End-fed wire (free space) against a 2.5 m counterpoise; impedance per band ===")
a = 0.8e-3


def endfed(L, f, cp=2.5):
    ns = max(9, int(np.ceil(L / 0.4)) | 1)
    w = [((0, 0, 0), (L, 0, 0), a, ns), ((0, 0, 0), (-cp, 0, 0), a, max(3, int(cp / 0.4)))]
    # feed on the first segment of the long wire (next to the junction)
    return nec(w, f, (0, 1))


for L in (20.1, 21.6, 12.5):
    print(f"  L = {L} m ({L/0.3048:.1f} ft):")
    for b, (f1, f2) in BANDS.items():
        if b in ("160", "60"):
            continue
        fm = 0.5 * (f1 + f2)
        z = endfed(L, fm)
        z9 = z / 9
        nhalf = L / (C0 / (fm * 1e6) / 2)
        print(f"    {b:>3} m ({fm:6.3f} MHz): L = {nhalf:4.2f} x lambda/2, Z = {z.real:7.0f}{z.imag:+8.0f}j ohm, "
              f"|Z| = {abs(z):6.0f}; after 9:1 unun Z/9 -> VSWR(50) {vswr(z9):6.1f}")
z201 = [abs(endfed(20.1, 0.5 * sum(BANDS[b]))) for b in ("40", "20", "15", "10")]
z216 = [abs(endfed(21.6, 0.5 * sum(BANDS[b]))) for b in ("80", "40", "30", "20", "17", "15", "12", "10")]
check("20.1 m wire: |Z| > 1.5 kOhm on 40/20/15/10 m", min(z201) > 1500, f"(min {min(z201):.0f}) -- pre-registered; "
      "a MISS means the counterpoise and end effects move the antiresonances (reported, not tuned)")
print(f"  21.6 m (71 ft) wire: max |Z| over 80-10 m = {max(z216):.0f} ohm")

print("\n  Length search: physical L whose half-wave multiples avoid every band by the largest margin")


def clearance(L, bands=("80", "40", "30", "20", "17", "15", "12", "10"), K=0.97):
    """min over bands of the relative distance from the band to the nearest n*lambda/2 resonance
    (resonances at f_n = n K c / (2 L)); K = end-effect/velocity factor of a thin HF wire."""
    worst = 1.0
    for b in bands:
        f1, f2 = BANDS[b]
        f1, f2 = f1 * 1e6, f2 * 1e6
        f0 = K * C0 / (2 * L)
        n = np.arange(1, 80)
        fn = n * f0
        # distance of fn from the band [f1, f2] relative to band centre
        d = np.where(fn < f1, f1 - fn, np.where(fn > f2, fn - f2, 0.0)) / (0.5 * (f1 + f2))
        worst = min(worst, d.min())
    return worst


Ls = np.arange(8.0, 60.0, 0.05)
cl = np.array([clearance(L) for L in Ls])
# local maxima
best = [(Ls[i], cl[i]) for i in range(1, len(Ls) - 1) if cl[i] >= cl[i - 1] and cl[i] >= cl[i + 1] and cl[i] > 0.035]
print("    80-10 m, K = 0.97: lengths with >= 3.5 % clearance (m / ft / clearance):")
print("     " + ", ".join(f"{L:.2f} m/{L/0.3048:.0f} ft/{100*c:.1f}%" for L, c in best))
ve3eed_ft = [29, 35.5, 41, 58, 71, 84, 107, 119, 148]
print("    VE3EED list evaluated with the same metric (80-10 m; 29-41 ft are too short for 80 m but are scored anyway):")
print("     " + ", ".join(f"{x} ft: {100*clearance(x*0.3048):.1f}%" for x in ve3eed_ft))
print(f"    bad example 66 ft (20.1 m): {100*clearance(20.1):.1f}%; 33 ft (10.06 m): {100*clearance(10.06):.1f}%")
check("71 ft has >= 3 % clearance on 80-10 m", clearance(71 * 0.3048) >= 0.03, f"({100*clearance(71*0.3048):.1f}%)")

print("\n  NEC-based check of 'good lengths': worst-band VSWR(50) behind an ideal 9:1 unun and number of band")
print("  points (40-10 m, edges + centre = 21 points) with |Z| > 2 kOhm, for three installations:")
pts = np.array([x for bnd in ("40", "30", "20", "17", "15", "12", "10")
                for x in (BANDS[bnd][0], 0.5 * sum(BANDS[bnd]), BANDS[bnd][1])])


def invL(L, f, hv=6.0):
    hv = min(hv, L)
    w = [((0, 0, 0.0), (0, 0, hv), a, max(3, int(hv / 0.4))), ((0, 0, hv), (L - hv, 0, hv), a, max(3, int((L - hv) / 0.4)))]
    return np.array(nec(w, list(f), (0, 1), ground="pec"))


def endfed_cp(L, f, cp):
    w = [((0, 0, 0), (L, 0, 0), a, max(9, int(L / 0.4))), ((0, 0, 0), (-cp, 0, 0), a, max(3, int(cp / 0.4)))]
    return np.array(nec(w, list(f), (0, 1)))


def metrics(z):
    zz = z / 9
    G = np.abs((zz - 50) / (zz + 50))
    return ((1 + G) / (1 - G)).max(), int(np.sum(np.abs(z) > 2000))


models = (("inverted-L over perfect ground (6 m vertical)", lambda L: invL(L, pts)),
          ("end-fed, free space, 7.5 m counterpoise", lambda L: endfed_cp(L, pts, 7.5)),
          ("end-fed, free space, 2.5 m counterpoise", lambda L: endfed_cp(L, pts, 2.5)))
Lgrid = np.arange(8.0, 45.01, 0.25)
for name, fun in models:
    res = [metrics(fun(L)) for L in Lgrid]
    vs = np.array([r[0] for r in res]); nh = np.array([r[1] for r in res])
    o = np.argsort(vs)
    print(f"   {name}: median worst VSWR {np.median(vs):.1f}; best lengths "
          + ", ".join(f"{Lgrid[i]:.2f} m/{Lgrid[i]/0.3048:.0f} ft (VSWR {vs[i]:.1f}, {nh[i]} pts >2k)" for i in o[:3])
          + f"; {100*np.mean(nh == 0):.0f} % of lengths have no point > 2 kOhm")
    print("     VE3EED: " + ", ".join(f"{x} ft {metrics(fun(x*0.3048))[0]:.0f}/{metrics(fun(x*0.3048))[1]}"
                                    for x in (29, 35.5, 41, 58, 71, 84, 107, 119))
          + "   'bad': " + ", ".join(f"{x} m {metrics(fun(x))[0]:.0f}/{metrics(fun(x))[1]}" for x in (10.06, 20.1, 40.6))
          + "   (worst VSWR / points > 2 kOhm)")
# width of the high-|Z| region around the first antiresonance of a 20 m wire
fs = np.linspace(5.0, 10.0, 201)
zz = np.array([abs(endfed(20.0, x)) for x in fs])
hi = fs[zz > 1500]
print(f"  20.0 m wire: |Z| > 1.5 kOhm from {hi.min():.2f} to {hi.max():.2f} MHz around the first antiresonance "
      f"(peak {zz.max():.0f} ohm at {fs[np.argmax(zz)]:.2f} MHz): +-{50*(hi.max()-hi.min())/fs[np.argmax(zz)]:.0f} %")

# ------------------------------------------------------------------ 2. fan dipole
print("\n=== 2. Fan dipole: 40 m and 20 m dipoles on one feed (free space) ===")
aw = 1e-3


def dipole_w(Lh, ns, z=0.0, ang=0.0):
    """two arms from the origin, half-length Lh, in the x-z plane at angle 'ang' below the x axis (droop)."""
    dx, dz = Lh * np.cos(np.radians(ang)), -Lh * np.sin(np.radians(ang))
    return [((0, 0, z), (dx, 0, z + dz), aw, ns), ((0, 0, z), (-dx, 0, z + dz), aw, ns)]


def feedgap_dipole(L, f, ns=21):
    w = [((-L / 2, 0, 0), (L / 2, 0, 0), aw, ns)]
    return nec(w, f, (0, ns // 2 + 1))


def resonance(fun, lo, hi, n=161):
    fs = np.linspace(lo, hi, n)
    zs = np.array(fun(fs))
    X = zs.imag
    idx = np.where((X[:-1] < 0) & (X[1:] >= 0))[0]
    res = []
    for i in idx:
        fr = fs[i] - X[i] * (fs[i + 1] - fs[i]) / (X[i + 1] - X[i])
        res.append((fr, float(np.interp(fr, fs, zs.real))))
    return res


L40, L20 = 20.30, 10.10
r40 = resonance(lambda f: feedgap_dipole(L40, f, 41), 6.0, 8.0)
r20 = resonance(lambda f: feedgap_dipole(L20, f, 21), 12.5, 15.5)
print(f"  40 m alone (L = {L40} m): resonance {r40[0][0]:.3f} MHz, R = {r40[0][1]:.1f} ohm")
print(f"  20 m alone (L = {L20} m): resonance {r20[0][0]:.3f} MHz, R = {r20[0][1]:.1f} ohm")


def fan(f, spread_deg):
    # both dipoles share a 0.1 m centre 'feed wire' along y so a single source drives both
    feedw = ((0, -0.05, 0), (0, 0.05, 0), aw, 1)
    s = np.radians(spread_deg)
    w = [feedw,
         ((0, 0.05, 0), (L40 / 2, 0.05, 0), aw, 21), ((0, -0.05, 0), (-L40 / 2, -0.05, 0), aw, 21),
         ((0, 0.05, 0), (L20 / 2 * np.cos(s), 0.05, -L20 / 2 * np.sin(s)), aw, 11),
         ((0, -0.05, 0), (-L20 / 2 * np.cos(s), -0.05, -L20 / 2 * np.sin(s)), aw, 11)]
    return nec(w, f, (0, 1))


for spread in (10.0, 30.0):
    rr = resonance(lambda f: fan(f, spread), 6.0, 16.0, 401)
    print(f"  fan, 20 m wires drooping {spread:.0f} deg below the 40 m wires (vertical fan): resonances "
          + ", ".join(f"{fr:.3f} MHz (R {R:.0f} ohm)" for fr, R in rr))


def crossed(f, az_deg):
    feedw = ((0, -0.05, 0), (0, 0.05, 0), aw, 1)
    az = np.radians(az_deg)
    u = np.array([np.cos(az), np.sin(az), 0.0]) * L20 / 2
    p1, p2 = np.array([0, 0.05, 0]), np.array([0, -0.05, 0])
    w = [feedw,
         (tuple(p1), (L40 / 2, 0.05, 0), aw, 21), (tuple(p2), (-L40 / 2, -0.05, 0), aw, 21),
         (tuple(p1), tuple(p1 + u), aw, 11), (tuple(p2), tuple(p2 - u), aw, 11)]
    return nec(w, f, (0, 1))


for az in (30.0, 90.0):
    rr = resonance(lambda f: crossed(f, az), 6.0, 16.0, 401)
    print(f"  crossed: 20 m dipole rotated {az:.0f} deg in azimuth from the 40 m dipole: resonances "
          + ", ".join(f"{fr:.3f} MHz (R {R:.0f} ohm)" for fr, R in rr))
rr = resonance(lambda f: fan(f, 30.0), 6.0, 16.0, 401)
f20 = [fr for fr, R in rr if 12.5 < fr < 15.5]
check("fan: a resonance remains in 12.5-15.5 MHz", len(f20) > 0)
if f20:
    print(f"    shift of the 20 m resonance by the 40 m wire (30 deg spread): {100*(f20[0]/r20[0][0]-1):+.1f} %")

# ------------------------------------------------------------------ 3. inverted V
print("\n=== 3. Inverted-V (7.1 MHz, free space and over average ground at 12 m apex) ===")
f = 7.1
lam = C0 / (f * 1e6)
for apex in (180, 150, 120, 90):
    droop = (180 - apex) / 2

    from scipy.optimize import brentq

    def build(Lh, droop=droop):
        dx, dz = Lh * np.cos(np.radians(droop)), Lh * np.sin(np.radians(droop))
        return [((-0.1, 0, 12.0), (0.1, 0, 12.0), aw, 1),
                ((0.1, 0, 12.0), (0.1 + dx, 0, 12.0 - dz), aw, 21),
                ((-0.1, 0, 12.0), (-0.1 - dx, 0, 12.0 - dz), aw, 21)]
    res = {}
    for gnd in (None, "som"):
        g = lambda Lh: nec(build(Lh), f, (0, 1), ground=gnd).imag
        Lh = brentq(g, 0.21 * lam, 0.26 * lam, xtol=1e-3)
        res[gnd] = (Lh, nec(build(Lh), f, (0, 1), ground=gnd).real)
    print(f"  apex {apex:3d} deg: free space: resonant arm {res[None][0]:.2f} m, R = {res[None][1]:.1f} ohm; "
          f"over ground (apex 12 m): arm {res['som'][0]:.2f} m, R = {res['som'][1]:.1f} ohm")
    if apex == 180:
        R_flat = res[None][1]
    if apex == 90:
        R_90 = res[None][1]
check("inverted-V 90 deg R well below flat dipole R (free space)", R_90 < 0.75 * R_flat, f"({R_90:.0f} vs {R_flat:.0f})")

# ------------------------------------------------------------------ 4. OCF
print("\n=== 4. Off-centre-fed dipole, 41.0 m wire (80 m half wave), free space ===")
Lw, ns = 41.0, 205


def ocf(frac, f):
    w = [((0, 0, 0), (Lw, 0, 0), aw, ns)]
    seg = int(round(frac * ns)) + 1
    return nec(w, f, (0, seg))


r80 = resonance(lambda f: ocf(0.5, f), 3.0, 4.0)
f1 = r80[0][0]
print(f"  centre-fed resonance f1 = {f1:.3f} MHz, R = {r80[0][1]:.1f} ohm")
for frac in (0.5, 0.4, 0.33, 0.25):
    zz = [ocf(frac, n * f1) for n in (1, 2, 3, 4)]
    zc = r80[0][1] / np.cos(np.pi * (0.5 - frac)) ** 2
    print(f"  feed at {frac:.2f} L: Z(f1) = {zz[0].real:6.0f}{zz[0].imag:+6.0f}j (R_c/cos^2 kz = {zc:5.0f}), "
          f"Z(2f1) = {zz[1].real:6.0f}{zz[1].imag:+6.0f}j, Z(3f1) = {zz[2].real:6.0f}{zz[2].imag:+6.0f}j, "
          f"Z(4f1) = {zz[3].real:6.0f}{zz[3].imag:+6.0f}j")
for hgt in (12.0, 20.0):
    w = lambda: [((0, 0, hgt), (Lw, 0, hgt), aw, ns)]
    zz = [nec(w(), n * f1, (0, int(round(0.33 * ns)) + 1), ground="som") for n in (1, 2, 3, 4)]
    print(f"  33 % feed, {hgt:.0f} m over average ground: " + ", ".join(f"Z({n}f1) = {z.real:.0f}{z.imag:+.0f}j" for n, z in zip((1, 2, 3, 4), zz)))
z33 = [abs(ocf(0.33, n * f1)) for n in (1, 2, 3, 4)]
check("33 % OCF: |Z(3 f1)| much higher than at f1, 2f1, 4f1", z33[2] > 3 * max(z33[0], z33[1], z33[3]),
      f"({[round(x) for x in z33]})")

# ------------------------------------------------------------------ 5. G5RV
print("\n=== 5. G5RV: 31.1 m top at 10.4 m over average ground, 10.36 m (electrical) of 450 ohm line ===")
Ltop, h = 31.1, 10.4


def g5rv_top(f):
    ns = 63
    w = [((-Ltop / 2, 0, h), (Ltop / 2, 0, h), aw, ns)]
    return nec(w, f, (0, ns // 2 + 1), ground="som")


for b in ("80", "40", "30", "20", "17", "15", "12", "10"):
    fm = 0.5 * sum(BANDS[b])
    zt = g5rv_top(fm)
    bl = 2 * np.pi * fm * 1e6 / C0 * 10.36
    zb = zin_line(zt, 450.0, bl)
    print(f"  {b:>3} m ({fm:6.3f} MHz): top Z = {zt.real:6.0f}{zt.imag:+6.0f}j, after line Z = {zb.real:7.1f}{zb.imag:+7.1f}j, "
          f"VSWR(50) = {vswr(zb):6.1f}")
z20 = zin_line(g5rv_top(14.175), 450.0, 2 * np.pi * 14.175e6 / C0 * 10.36)
fs = np.linspace(13.0, 15.5, 101)
for Z0, Lm in ((450.0, 10.36), (300.0, 10.36)):
    vs = [vswr(zin_line(g5rv_top(x), Z0, 2 * np.pi * x * 1e6 / C0 * Lm)) for x in fs]
    i = int(np.argmin(vs))
    print(f"  sweep 13-15.5 MHz, Z0 = {Z0:.0f} ohm: min VSWR(50) {vs[i]:.2f} at {fs[i]:.2f} MHz; "
          f"VSWR at 14.0/14.175/14.35 MHz = {np.interp(14.0, fs, vs):.2f}/{np.interp(14.175, fs, vs):.2f}/{np.interp(14.35, fs, vs):.2f}")
check("G5RV 20 m VSWR(50) < 2.5", vswr(z20) < 2.5, f"({vswr(z20):.2f}; Varney quotes ~1.8 -- pre-registered, reported)")

# ------------------------------------------------------------------ 6. NVIS
print("\n=== 6. NVIS: horizontal half-wave dipole at 5.3 MHz over average ground vs height ===")
f = 5.3
lam = C0 / (f * 1e6)
Ld = 0.48 * lam
for hl in (0.05, 0.1, 0.15, 0.25, 0.5):
    w = [((-Ld / 2, 0, hl * lam), (Ld / 2, 0, hl * lam), aw, 41)]
    # elevation pattern in the plane broadside to the wire (phi = 90): theta 0..90
    z, gdb, th = nec(w, f, (0, 21), ground="som", pattern=(91, 1, 0.0, 1.0, 0.0))
    # rp_card uses phi0 = 0 -> wire along x, phi = 0 plane is the E-plane; use phi = 90 plane:
    c = PyNEC.nec_context(); gg = c.get_geometry()
    gg.wire(1, 41, -Ld / 2, 0, hl * lam, Ld / 2, 0, hl * lam, aw, 1, 1)
    c.geometry_complete(0); c.gn_card(2, 0, EPS_G, SIG_G, 0, 0, 0, 0)
    c.ex_card(0, 1, 21, 0, 1.0, 0, 0, 0, 0, 0); c.fr_card(0, 1, f, 0)
    c.rp_card(0, 91, 1, 0, 0, 0, 0, 0.0, 90.0, 1.0, 0.0, 0, 0)
    G = np.array(c.get_radiation_pattern(0).get_gain()).ravel()
    th = np.arange(91)
    el = 90 - th
    imax = int(np.argmax(G))
    print(f"  h = {hl:.2f} lambda ({hl*lam:5.1f} m): Z = {z.real:5.1f}{z.imag:+6.1f}j ohm; zenith gain {G[0]:5.2f} dBi, "
          f"max {G.max():5.2f} dBi at elevation {el[imax]:2d} deg, gain at 30 deg elev {G[60]:5.2f} dBi")
    if hl == 0.15:
        el015 = el[imax]
    if hl == 0.5:
        el05, gz05, gm05 = el[imax], G[0], G.max()
check("NVIS: 0.15 lambda dipole peaks within 15 deg of zenith", el015 >= 75, f"(peak at {el015} deg)")
check("0.5 lambda dipole: peak away from zenith", el05 < 60, f"(peak at {el05} deg)")

# ------------------------------------------------------------------ 7. trap dipole
print("\n=== 7. Trap dipole (W3DZZ-like 80/40 m): traps 8.2 uH || C resonant at 7.05 MHz, Q_L = 200 ===")
Lt = 8.2e-6
Ct = 1 / ((2 * np.pi * 7.05e6) ** 2 * Lt)
inner, outer = 10.06, 6.8
print(f"  trap C = {Ct*1e12:.1f} pF; X_L at 7.05 MHz = {2*np.pi*7.05e6*Lt:.0f} ohm")


def trap_dipole(f, QL=200.0, inner=inner, outer=outer):
    ns_i, ns_o = 25, 17
    w = [((-0.05, 0, 0), (0.05, 0, 0), aw, 1),
         ((0.05, 0, 0), (0.05 + inner, 0, 0), aw, ns_i), ((0.05 + inner, 0, 0), (0.15 + inner, 0, 0), aw, 1),
         ((0.15 + inner, 0, 0), (0.15 + inner + outer, 0, 0), aw, ns_o),
         ((-0.05, 0, 0), (-0.05 - inner, 0, 0), aw, ns_i), ((-0.05 - inner, 0, 0), (-0.15 - inner, 0, 0), aw, 1),
         ((-0.15 - inner, 0, 0), (-0.15 - inner - outer, 0, 0), aw, ns_o)]
    Rs = 2 * np.pi * 7.05e6 * Lt / QL                 # series loss of the trap coil
    # parallel RLC in NEC (LDTYP 1) is ideal R || L || C: equivalent parallel R of the lossy coil at resonance
    Rp = (2 * np.pi * 7.05e6 * Lt) ** 2 / Rs
    loads = [(1, 2, 1, Rp, Lt, Ct), (1, 5, 1, Rp, Lt, Ct)]
    return nec(w, f, (0, 1), loads=loads)


rr = resonance(lambda f: trap_dipole(f), 3.0, 8.0, 301)
print("  resonances: " + ", ".join(f"{fr:.3f} MHz (R {R:.1f} ohm)" for fr, R in rr))
check("trap dipole: one resonance in 3.4-4.1 MHz and one in 6.7-7.5 MHz",
      any(3.4 < fr < 4.1 for fr, _ in rr) and any(6.7 < fr < 7.5 for fr, _ in rr))
for fm in (3.75, 7.1):
    z_lossy = trap_dipole(fm, 200.0)
    z_ideal = trap_dipole(fm, 1e6)
    print(f"  at {fm} MHz: Z (Q 200) = {z_lossy.real:.1f}{z_lossy.imag:+.1f}j, Z (lossless) = {z_ideal.real:.1f}{z_ideal.imag:+.1f}j"
          f" -> trap-loss efficiency ~ {100*z_ideal.real/z_lossy.real:.0f} % (R_rad/R_in, same current)")

# ------------------------------------------------------------------ 8. vertical + elevated radials
print("\n=== 8. lambda/4 vertical at 7.1 MHz, base 2 m up, N elevated lambda/4 radials, average ground ===")
f = 7.1
lam = C0 / (f * 1e6)
hb = 2.0
for nr in (1, 2, 4, 8):
    w = [((0, 0, hb), (0, 0, hb + 0.25 * lam), aw, 21)]
    for i in range(nr):
        ph = 2 * np.pi * i / nr
        w.append(((0, 0, hb), (0.25 * lam * np.cos(ph), 0.25 * lam * np.sin(ph), hb), aw, 21))
    c = PyNEC.nec_context(); gg = c.get_geometry()
    for i, (p0, p1, aa, nsg) in enumerate(w):
        gg.wire(i + 1, nsg, *p0, *p1, aa, 1, 1)
    c.geometry_complete(0); c.gn_card(2, 0, EPS_G, SIG_G, 0, 0, 0, 0)
    c.ex_card(0, 1, 1, 0, 1.0, 0, 0, 0, 0, 0); c.fr_card(0, 1, f, 0)
    c.rp_card(0, 46, 36, 0, 0, 0, 0, 0.0, 0.0, 2.0, 10.0, 0, 0)
    rp = c.get_radiation_pattern(0)
    G = 10 ** (np.array(rp.get_gain()) / 10)        # (46, 36), theta 0..90
    th = np.radians(np.arange(0, 91, 2.0))
    sky = np.trapezoid(G.mean(axis=1) * 2 * np.pi * np.sin(th), th) / (4 * np.pi)
    z = complex(c.get_input_parameters(0).get_impedance()[0])
    g10 = 10 * np.log10(G[40].mean())             # theta = 80 deg -> 10 deg elevation
    print(f"  {nr} radial(s): Z = {z.real:5.1f}{z.imag:+6.1f}j ohm, mean gain at 10 deg elevation {g10:5.2f} dBi, "
          f"fraction of input power radiated into the sky hemisphere = {100*sky:4.1f} %")

c = PyNEC.nec_context(); gg = c.get_geometry()
Ld = 0.48 * lam
gg.wire(1, 41, -Ld / 2, 0, 0.5 * lam, Ld / 2, 0, 0.5 * lam, aw, 1, 1)
c.geometry_complete(0); c.gn_card(2, 0, EPS_G, SIG_G, 0, 0, 0, 0)
c.ex_card(0, 1, 21, 0, 1.0, 0, 0, 0, 0, 0); c.fr_card(0, 1, f, 0)
c.rp_card(0, 46, 36, 0, 0, 0, 0, 0.0, 0.0, 2.0, 10.0, 0, 0)
G = 10 ** (np.array(c.get_radiation_pattern(0).get_gain()) / 10)
sky = np.trapezoid(G.mean(axis=1) * 2 * np.pi * np.sin(th), th) / (4 * np.pi)
print(f"  reference: horizontal dipole at 0.5 lambda over the same ground: sky-hemisphere fraction {100*sky:.1f} %")
c = PyNEC.nec_context(); gg = c.get_geometry()
gg.wire(1, 21, 0, 0, 0.0, 0, 0, 0.25 * lam, aw, 1, 1)
c.geometry_complete(1); c.gn_card(1, 0, 0, 0, 0, 0, 0, 0)
c.ex_card(0, 1, 1, 0, 1.0, 0, 0, 0, 0, 0); c.fr_card(0, 1, f, 0)
c.rp_card(0, 46, 36, 0, 0, 0, 0, 0.0, 0.0, 2.0, 10.0, 0, 0)
G = 10 ** (np.array(c.get_radiation_pattern(0).get_gain()) / 10)
sky = np.trapezoid(G.mean(axis=1) * 2 * np.pi * np.sin(th), th) / (4 * np.pi)
print(f"  reference: same vertical on a perfect ground: sky-hemisphere fraction {100*sky:.1f} % (should be ~100 %), "
      f"Z = {complex(c.get_input_parameters(0).get_impedance()[0]):.1f}")

print("\nALL PASS" if ok else "\nSOME MISSES (see above)")
