#!/usr/bin/env python3
"""
s12_yagi_tant.py -- W5-S12 (G-08-02): antenna temperature and G/T of the 433 MHz ground-station Yagi vs elevation,
over real ground, from NEC-2 patterns.

Model: the KB's 11-element DL6WU Yagi (6 mm elements, 1.72 m boom; kb/08-antennas/yagi-uda-and-log-periodic.md ex. 1),
boom centre 3 m above "average" ground (er 13, sigma 5 mS/m), tilted to elevation EL, horizontal or vertical polarisation.

Method A (rigorous for a lossless antenna, by detailed balance): NEC with Sommerfeld/Norton ground gives the gain G(Omega)
over the upper hemisphere, already containing the coherent ground reflection. The fraction of transmitted power that
reaches the sky is eta_up = (1/4pi) int_up G dOmega; the rest is absorbed by the ground. By reciprocity and Kirchhoff's
law the antenna temperature is
        T_A = (1/4pi) int_up G(Omega) T_sky(el) dOmega + (1 - eta_up) T_ground .
Method B (cross-check, incoherent): free-space pattern; directions below the horizon see the ground's emission
(1-|Gamma|^2) T_g plus the specularly reflected sky |Gamma|^2 T_sky, with Fresnel Gamma for E_theta (TM) and E_phi (TE).

Sky: T_sky(el) = T_bg 10^(-A(el)/10) + T_m (1 - 10^(-A(el)/10)); T_bg from ITU-R P.372 galactic noise
Fa = 52 - 23 log10 f(MHz) (median, ~40 K at 433 MHz); atmosphere A(el) = A_zenith * airmass (Kasten-Young), A_zenith
0.033 dB, T_m = 275 K. Ground physical temperature 290 K. Man-made noise is NOT in the model (reported separately).
Run: python3 tools/verify/s12_yagi_tant.py   (~3-6 min)
"""
import os
import sys
import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import PyNEC                                     # noqa: E402
from ant_yagi import dl6wu_design                # noqa: E402

C0 = 299792458.0
F = 433e6
LAM = C0 / F
DIA = 6e-3
NSEG = 13
H = 3.0
EPS_G, SIG_G = 13.0, 0.005
T_G = 290.0
T_M = 275.0
A_Z = 0.033
results, misses = [], []


def say(s=""):
    print(s); results.append(s)


def check(name, cond, detail=""):
    if not cond:
        misses.append(name)
    say(f"[{'PASS' if cond else 'MISS'}] {name} {detail}")


def T_bg(fmhz):
    return 290.0 * 10 ** ((52.0 - 23.0 * np.log10(fmhz)) / 10)


def airmass(el_deg):
    el = np.maximum(el_deg, 0.0)
    return 1.0 / (np.sin(np.radians(el)) + 0.50572 * (el + 6.07995) ** -1.6364)


def T_sky(el_deg, fmhz=F / 1e6):
    A = A_Z * airmass(el_deg)
    t = 10 ** (-A / 10)
    return T_bg(fmhz) * t + T_M * (1 - t)


DES = dl6wu_design(2.3, DIA / LAM, DIA / LAM)
POS = DES["pos"] * LAM
BASE = [DES["refl"] * LAM, 0.47 * LAM] + list(DES["dirs"] * LAM)


def geom(lengths, el_deg, pol, h):
    """boom along local x', elements along y' (H) or z' (V); rotate up by el about y; boom centre at height h"""
    e = np.radians(el_deg)
    bx = np.array([np.cos(e), 0, np.sin(e)])
    ed = np.array([0, 1.0, 0]) if pol == "H" else np.array([-np.sin(e), 0, np.cos(e)])
    c0 = np.array([0, 0, h]) - bx * POS[-1] / 2
    w = []
    for L, x in zip(lengths, POS):
        c = c0 + bx * x
        w.append((c - ed * L / 2, c + ed * L / 2))
    return w


def run(lengths, el, pol, ground, dth=0.5, dph=3.0, pattern=True, h=H):
    c = PyNEC.nec_context(); g = c.get_geometry()
    for i, (p0, p1) in enumerate(geom(lengths, el, pol, h)):
        g.wire(i + 1, NSEG, *p0, *p1, DIA / 2, 1.0, 1.0)
    c.geometry_complete(0)
    if ground == "som":
        c.gn_card(2, 0, EPS_G, SIG_G, 0, 0, 0, 0)
    elif ground == "rc":
        c.gn_card(0, 0, EPS_G, SIG_G, 0, 0, 0, 0)
    else:
        c.gn_card(-1, 0, 0, 0, 0, 0, 0, 0)
    c.ex_card(0, 2, NSEG // 2 + 1, 0, 1.0, 0, 0, 0, 0, 0)
    c.fr_card(0, 1, F / 1e6, 0)
    if not pattern:
        c.xq_card(0)
        return complex(c.get_input_parameters(0).get_impedance()[0])
    nth = int(round((90 if ground else 180) / dth)) + 1
    nph = int(round(360 / dph))
    c.rp_card(0, nth, nph, 0, 0, 0, 0, 0.0, dph / 2, dth, dph, 0, 0)
    rp = c.get_radiation_pattern(0)
    G = 10 ** (np.array(rp.get_gain()) / 10)
    et = np.array(rp.get_e_theta()).reshape(nph, nth).T
    ep = np.array(rp.get_e_phi()).reshape(nph, nth).T
    th = np.arange(nth) * dth
    ph = dph / 2 + np.arange(nph) * dph
    return dict(G=G, th=th, ph=ph, et=et, ep=ep, dth=dth, dph=dph,
                Z=complex(c.get_input_parameters(0).get_impedance()[0]))


def sph_int(r, f=None):
    """(1/4pi) int G * f dOmega over the computed theta range (trapezoid in theta, periodic in phi)"""
    th = np.radians(r["th"]); G = r["G"] if f is None else r["G"] * f
    w = np.full(len(th), np.radians(r["dth"])); w[0] = w[-1] = np.radians(r["dth"]) / 2
    return float(np.sum(G.sum(axis=1) * np.radians(r["dph"]) * np.sin(th) * w) / (4 * np.pi))


def boresight_gain(r, el):
    """gain toward the boom direction (phi = 0 side)"""
    i = int(np.argmin(np.abs(r["th"] - (90 - el))))
    j = int(np.argmin(np.abs(((r["ph"] + 180) % 360) - 180)))
    return 10 * np.log10(r["G"][i, j])


def peak_gain(r):
    return 10 * np.log10(r["G"].max()), 90 - r["th"][np.unravel_index(r["G"].argmax(), r["G"].shape)[0]]


def fresnel(psi, pol):
    """reflection coefficient at grazing angle psi (rad) for TM ('V') or TE ('H')"""
    ec = EPS_G - 1j * SIG_G / (2 * np.pi * F * 8.8541878e-12)
    s, co = np.sin(psi), np.cos(psi)
    root = np.sqrt(ec - co ** 2)
    if pol == "V":
        return (ec * s - root) / (ec * s + root)
    return (s - root) / (s + root)


# ---------------------------------------------------------------------------------------- 0. Yagi and sky model
say("=== 0. Yagi, sky and ground model ===")
def xde(L):
    LL = BASE.copy(); LL[1] = L
    return run(LL, 0, "H", None, pattern=False).imag
LDE = brentq(xde, 0.44 * LAM, 0.50 * LAM, xtol=1e-6)
LEN = BASE.copy(); LEN[1] = LDE
rf = run(LEN, 0, "H", None, dth=1.0, dph=2.0)
G_fs = boresight_gain(rf, 0)
say(f"  11-el DL6WU, boom {POS[-1]*1000:.0f} mm, DE {LDE*1000:.1f} mm; free space: boresight {G_fs:.2f} dBi, "
    f"Z {rf['Z']:.1f}, average gain {sph_int(rf):.3f}")
check("0a free-space gain within 0.4 dB of the KB value 14.2 dBi and AGT 0.98-1.02",
      abs(G_fs - 14.2) < 0.4 and abs(sph_int(rf) - 1) < 0.02, f"({G_fs:.2f} dBi)")
say(f"  sky model at 433 MHz: T_bg (P.372 galactic median) = {T_bg(433):.1f} K (915 MHz: {T_bg(915):.1f} K); "
    + ", ".join(f"T_sky({e:.0f} deg) = {T_sky(e):.1f} K" for e in (90, 30, 10, 5, 2, 0)))
say("  man-made noise (P.372 Fa = c - 27.7 log f, defined to 250 MHz, extrapolated here): "
    + ", ".join(f"{n} {290*10**((c-27.7*np.log10(433))/10):.0f} K" for n, c in (("city", 76.8), ("residential", 72.5), ("rural", 67.2)))
    + f", quiet rural {290*10**((53.6-28.6*np.log10(433))/10):.0f} K")

# ---------------------------------------------------------------------------------------- 1. method A vs elevation
ELS = (0, 2, 5, 10, 20, 30, 45, 60, 90)
TAB = {}
for pol in ("H", "V"):
    say(f"\n=== 1{pol}. {pol}-pol Yagi, boom centre {H:.0f} m over average ground (NEC Sommerfeld): method A ===")
    say("   el   G_bore dBi  peak dBi @el   eta_up   T_sky-part K   T_ground-part K   T_A K   Z_in")
    for el in ELS:
        r = run(LEN, el, pol, "som")
        eta = sph_int(r)
        el_grid = 90 - r["th"]
        Ts = T_sky(el_grid)[:, None] * np.ones_like(r["G"])
        tsky = sph_int(r, Ts)
        tgnd = (1 - eta) * T_G
        TA = tsky + tgnd
        gb = boresight_gain(r, el)
        gp, elp = peak_gain(r)
        TAB[(pol, el)] = dict(TA=TA, G=gb, Gp=gp, elp=elp, eta=eta, r=r)
        say(f"  {el:3d}    {gb:6.2f}     {gp:6.2f} @{elp:4.1f}    {eta:.3f}      {tsky:6.1f}          {tgnd:6.1f}       "
            f"{TA:6.1f}   {r['Z'].real:.1f}{r['Z'].imag:+.1f}j")
check("1a T_A at 90 deg elevation (H-pol) between 40 and 80 K (sky ~40 K + back/side-lobe ground spill)",
      40 < TAB[("H", 90)]["TA"] < 80, f"({TAB[('H',90)]['TA']:.1f} K)")
check("1b T_A at 0 deg elevation is the largest (half the main beam on the ground/horizon)",
      all(TAB[(p, 0)]["TA"] >= max(TAB[(p, e)]["TA"] for e in ELS) - 1e-9 for p in ("H", "V")))

# ---------------------------------------------------------------------------------------- 2. cross-checks
say("\n=== 2. Cross-checks ===")
r_rc = run(LEN, 10, "H", "rc")
eta_rc = sph_int(r_rc)
TA_rc = sph_int(r_rc, T_sky(90 - r_rc["th"])[:, None] * np.ones_like(r_rc["G"])) + (1 - eta_rc) * T_G
say(f"  H-pol, el 10 deg: Sommerfeld T_A = {TAB[('H',10)]['TA']:.1f} K vs reflection-coefficient ground (GN 0) {TA_rc:.1f} K")
check("2a GN 0 (reflection-coefficient) and Sommerfeld T_A agree within 3 K at 3 m (4.3 lambda) height",
      abs(TA_rc - TAB[("H", 10)]["TA"]) < 3)


def method_B(el, pol):
    r = run(LEN, el, pol, None, dth=0.5, dph=3.0)
    th = r["th"]; elg = 90 - th
    pt = np.abs(r["et"]) ** 2; pp = np.abs(r["ep"]) ** 2
    ftheta = pt / (pt + pp + 1e-300); fphi = 1 - ftheta
    Tb = np.zeros_like(r["G"])
    up = elg >= 0
    Tb[up] = T_sky(elg[up])[:, None]
    psi = np.radians(-elg[~up])
    gV = np.abs(fresnel(psi, "V")) ** 2; gH = np.abs(fresnel(psi, "H")) ** 2
    Tr = T_sky(-elg[~up])
    TbV = gV * Tr + (1 - gV) * T_G
    TbH = gH * Tr + (1 - gH) * T_G
    Tb[~up] = ftheta[~up] * TbV[:, None] + fphi[~up] * TbH[:, None]
    return sph_int(r, Tb)


say("   el  pol   T_A method A (NEC ground)   T_A method B (free-space pattern + Fresnel, incoherent)")
diffs = []
for pol in ("H", "V"):
    for el in (0, 10, 30, 90):
        tb = method_B(el, pol)
        diffs.append(abs(tb - TAB[(pol, el)]["TA"]))
        say(f"  {el:3d}   {pol}        {TAB[(pol, el)]['TA']:6.1f}                      {tb:6.1f}")
check("2b methods A and B agree within 10 K at every tested elevation", max(diffs) < 10, f"(max diff {max(diffs):.1f} K)")

# ---------------------------------------------------------------------------------------- 3. G/T
say("\n=== 3. G/T vs elevation (G = free-space boresight gain; the NEC-over-ground boresight gain, which adds the coherent "
    "ground-reflection lobing at low elevation, is shown separately; T_sys = T_A + T_rx at the antenna terminals) ===")
T_LNA = 290 * (10 ** 0.05 - 1)
def trx_module():
    Lc = 10 ** 0.1
    return (Lc - 1) * 290 + Lc * 290 * (10 ** 0.6 - 1)       # 1 dB coax then NF 6 dB, referred to the antenna terminals
say(f"  T_rx: masthead LNA NF 0.5 dB -> {T_LNA:.0f} K; module NF 6 dB behind 1 dB of coax -> {trx_module():.0f} K")
say("   el  pol  G_fs   G_over_ground   T_A K   G/T LNA dB/K   G/T module dB/K   G/T LNA + rural man-made 76 K")
GT = {}
for pol in ("H", "V"):
    for el in ELS:
        d = TAB[(pol, el)]
        g1 = G_fs - 10 * np.log10(d["TA"] + T_LNA)
        g2 = G_fs - 10 * np.log10(d["TA"] + trx_module())
        g3 = G_fs - 10 * np.log10(d["TA"] + 76 + T_LNA)
        GT[(pol, el)] = (g1, g2)
        gg = f"{d['G']:6.2f}" if el > 0 else "  (0) "
        say(f"  {el:3d}   {pol}   {G_fs:5.2f}   {gg}        {d['TA']:6.1f}     {g1:6.2f}          {g2:6.2f}            {g3:6.2f}")
d1 = GT[("V", 5)][0] - GT[("V", 90)][0]; d2 = GT[("V", 5)][1] - GT[("V", 90)][1]
say(f"  V-pol, 5 deg vs 90 deg elevation: G/T worse by {-d1:.2f} dB with the LNA, {-d2:.2f} dB with the module alone")
check("3a antenna temperature matters only with an LNA: module-only G/T varies < 0.5 dB over 5-90 deg (V-pol), "
      "LNA G/T varies > 2 dB", abs(d2) < 0.5 and abs(d1) > 2, f"(module {d2:+.2f}, LNA {d1:+.2f} dB)")
say("\nSUMMARY: " + ("ALL PASS" if not misses else f"{len(misses)} MISS: " + "; ".join(misses)))
with open(os.path.join(HERE, "s12_yagi_tant_output.txt"), "w") as fh:
    fh.write("\n".join(results) + "\n")
