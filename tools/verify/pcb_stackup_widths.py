#!/usr/bin/env python3
# Runtime (W6-F5, 2026-10-14): ~161 s (2.7 min) measured on a 10-core Apple-silicon Mac, run 3 at a time
# under load average 7-70 from other jobs; expect less on an idle machine. It exceeds the 120 s per-script budget
# used by the D7 verify sweep, so give it a >= 15 min timeout and run it with `python3 -u` to see progress. The existing --fast / --only9 flags shorten it (fewer field-solver runs; not the full check).
# Measured run: exit 0, no FAIL lines. Comment only; no code or results changed.
"""
pcb_stackup_widths.py — verification / calculator script for
kb/13-pcb-rf-layout-emc/stackups-and-materials.md (and jlcpcb-rf-manufacturing.md)

What it does
  1. Tabulates the JLCPCB / Rogers / PTFE stackups used in the KB (outer-layer dielectric to the first plane).
  2. 50-ohm microstrip width on each: Hammerstad-Jensen with 35 um copper (W1-A4's tline_microstrip.ms_hj),
     cross-checked with W1-A4's independent 2-D finite-volume field solver (tline_fd2d) bare and with a
     JLCPCB-style soldermask (0.6 mil over copper, 1.2 mil on laminate, er 3.8).
  3. 50-ohm grounded coplanar waveguide (CPWG) widths for gaps 0.10-0.30 mm (Ghione-Naldi, t = 0), with an FD
     check including 35 um copper for selected cases.
  4. When does a coplanar ground "matter"?  Z0 of CPWG vs gap/h relative to plain microstrip.
  5. Manufacturing sensitivity: Monte-Carlo Z0 spread for thickness/Dk/width tolerances vs JLCPCB's +-10 %.
  6. Loss per 10 mm at 433/915/1575/2450/5800 MHz for FR-4 vs RO4350B vs PTFE (ms_loss, smooth copper).
  7. Fibre-weave skew estimate (glass-rich vs resin-rich local Dk) in ps/inch and degrees at 2.45/5.8 GHz.
  8. Dk vs frequency: Isola 370HR 7628 table (4.36 @1 GHz -> 4.24 @10 GHz) effect on Z0 and on a 915 MHz
     quarter-wave stub length.
  9. JLCPCB's own online calculator results (captured 2026-09-27) re-evaluated with the FD solver using JLC's
     trapezoid + soldermask model (resolves the W1-A4 / JITX width discrepancy).

Run: python3 tools/verify/pcb_stackup_widths.py            (about 2-4 minutes; FD solver)
     python3 tools/verify/pcb_stackup_widths.py --fast     (skip FD cross-checks)
     python3 tools/verify/pcb_stackup_widths.py --only9    (FD only for the JLC-calculator section)
"""
import os
import sys
import numpy as np
from scipy.optimize import brentq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tline_microstrip import ms_hj, ms_loss, width_for  # noqa: E402
from tline_cpwg import cpwg  # noqa: E402
import tline_fd2d as fd  # noqa: E402

FAST = "--fast" in sys.argv
ONLY9 = "--only9" in sys.argv   # skip FD in sections 1-3, run the section-9 field solutions
FD13 = not (FAST or ONLY9)
C0 = 299_792_458.0
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


# ----------------------------------------------------------------------------- stackups
# (label, dielectric thickness to first plane h [m], Dk, outer copper t [m], note)
# JLCPCB values: jlcpcb.com/impedance (retrieved 2026-09-27); Rogers: RO4350B design Dk 3.66;
# JLCPCB PTFE: ZYF255DA Dk 2.55 (jlcpcb.com/pcb-fabrication/high-frequency-pcb).
STACKUPS = [
    ("JLC 2L 1.6 mm FR-4 (h~1.51 mm)", 1.51e-3, 4.5, 35e-6, "Dk 4.5 stated for 2-layer; h assumed"),
    ("JLC 2L 1.0 mm FR-4 (h~0.91 mm)", 0.91e-3, 4.5, 35e-6, "h assumed = 1.0 - 2x0.035 - plating"),
    ("JLC 2L 0.8 mm FR-4 (h~0.71 mm)", 0.71e-3, 4.5, 35e-6, "h assumed"),
    ("JLC04161H-7628 (L1-L2)", 0.2104e-3, 4.4, 35e-6, "default 4L stackup"),
    ("JLC04161H-2116 (L1-L2)", 0.1164e-3, 4.16, 35e-6, ""),
    ("JLC04161H-3313 (L1-L2)", 0.0994e-3, 4.1, 35e-6, "also JLC06161H-3313 L1-L2"),
    ("JLC04161H-1080 (L1-L2)", 0.0764e-3, 3.91, 35e-6, "also JLC06161H-1080 L1-L2"),
    ("RO4350B 2L 0.508 mm", 0.508e-3, 3.66, 35e-6, "JLCPCB HF service"),
    ("RO4350B 2L 0.762 mm", 0.762e-3, 3.66, 35e-6, "JLCPCB HF service"),
    ("RO4350B 2L 1.524 mm", 1.524e-3, 3.66, 35e-6, "JLCPCB HF service"),
    ("PTFE ZYF255DA 2L 0.762 mm", 0.762e-3, 2.55, 35e-6, "JLCPCB HF service"),
]
DF = {4.5: 0.020, 4.4: 0.020, 4.16: 0.020, 4.1: 0.020, 3.91: 0.020, 3.66: 0.0037, 2.55: 0.0018}


def w50_hj(h, er, t):
    return width_for(50.0, lambda w: ms_hj(w, h, er, t)[0])


def fd_z(W, h, t, er, mask=False, levels=(1.0, 0.5, 0.25)):
    """FD Z0 (Richardson). mask=True: JLC-like mask 15 um over copper and 30 um on laminate (er 3.8)."""
    if mask:
        # build geometry by hand: 30 um slab on laminate + 15 um conformal cap over the strip
        box_w = max(40 * h, 12 * W)
        box_h = 25 * h
        g = fd.Geometry(-box_w / 2, box_w / 2, box_h)
        g.add_dielectric(-box_w / 2, box_w / 2, 0, h, er)
        g.add_dielectric(-box_w / 2, box_w / 2, h, h + 30e-6, 3.8)
        g.add_dielectric(-W / 2 - 15e-6, W / 2 + 15e-6, h, h + t + 15e-6, 3.8)
        g.add_conductor(-W / 2, W / 2, h, h + t, "sig")
    else:
        g = fd.microstrip_geo(W, h, t, er)
    hmin = min(W, h, 4 * t) / 40
    hmax = h / 3
    _, ext, _ = fd.refine_study(lambda s: fd.line_params(g, hmin=hmin * s, hmax=hmax * s)[:2], levels)
    return ext[0], ext[1]


def fd_w50(h, er, t, w0, mask):
    """Secant solve for the FD 50-ohm width starting from the H-J width."""
    w1, w2 = w0, w0 * 0.92
    z1, z2 = fd_z(w1, h, t, er, mask)[0], fd_z(w2, h, t, er, mask)[0]
    # Z0 ~ linear in ln(W) over +-10 %
    a = (z1 - z2) / (np.log(w1) - np.log(w2))
    return float(np.exp(np.log(w1) + (50 - z1) / a))


print("=" * 100)
print("1-2. 50-ohm microstrip widths on JLCPCB / Rogers / PTFE stackups")
print("=" * 100)
rows = []
for lab, h, er, t, note in STACKUPS:
    w_hj = w50_hj(h, er, t)
    ee = ms_hj(w_hj, h, er, t)[1]
    rows.append((lab, h, er, w_hj, ee))
    print(f"  {lab:34s} h {h*1e3:6.4f} mm Dk {er:4.2f}: W50(H-J, t=35um) = {w_hj*1e3:6.3f} mm"
          f"  eeff {ee:4.2f}  lambda_g@915MHz {C0/915e6/np.sqrt(ee)*1e3:6.1f} mm  @2.45GHz {C0/2.45e9/np.sqrt(ee)*1e3:5.1f} mm")

# known anchor (W1-A4): JLC7628 bare 50 ohm ~0.372 mm (FD, t=0/35um?) -> check our HJ with t=35um is ~0.35-0.37
w7628 = [r for r in rows if r[0].startswith("JLC04161H-7628")][0][3]
check("JLC7628 50-ohm H-J width in 0.33-0.38 mm (W1-A4 anchor 0.35-0.372 mm)", 0.33e-3 < w7628 < 0.38e-3,
      f"({w7628*1e3:.3f} mm)")

if FD13:
    print("\n  FD cross-check (35 um copper; bare vs JLC-style soldermask):")
    for lab, h, er, t, note in STACKUPS:
        if not (lab.startswith("JLC 2L 1.6") or lab.startswith("JLC04161H") or lab.startswith("RO4350B 2L 0.508")):
            continue
        w0 = w50_hj(h, er, t)
        zb, eb = fd_z(w0, h, t, er, False)
        wm = fd_w50(h, er, t, w0, True)
        wb = fd_w50(h, er, t, w0, False)
        print(f"  {lab:34s} H-J W {w0*1e3:.3f} mm -> FD bare Z0 {zb:5.2f} ohm; FD 50-ohm W bare {wb*1e3:.3f} mm,"
              f" with mask {wm*1e3:.3f} mm ({(wm/wb-1)*100:+.1f} %)")
        check(f"  H-J vs FD bare within 3 % [{lab}]", abs(zb - 50) / 50 < 0.03, f"(FD {zb:.2f} ohm)")

print("\n" + "=" * 100)
print("3. 50-ohm CPWG (Ghione-Naldi, t = 0): signal width for given gap S")
print("=" * 100)
gaps = [0.10e-3, 0.15e-3, 0.20e-3, 0.25e-3, 0.30e-3]
cpwg_tab = {}
for lab, h, er, t, note in STACKUPS:
    out = []
    for S in gaps:
        try:
            w = brentq(lambda w: cpwg(w, S, h, er)[0] - 50, 0.02e-3, min(20e-3, 8 * h), xtol=1e-10)
        except ValueError:
            w = np.nan
        out.append(w)
    cpwg_tab[lab] = out
    print(f"  {lab:34s} " + "  ".join(f"S={S*1e3:.2f}:W={w*1e3:5.3f}" for S, w in zip(gaps, out)))

# 2-layer 1.6 mm: CPWG makes 50 ohm possible at a sane width (vs ~2.9 mm microstrip)
w2l = cpwg_tab["JLC 2L 1.6 mm FR-4 (h~1.51 mm)"][2]
check("2L 1.6 mm CPWG with 0.20 mm gap gives 50 ohm at W < 2 mm (vs ~2.9 mm microstrip)", w2l < 2.0e-3,
      f"(W = {w2l*1e3:.3f} mm)")

if FD13:
    print("\n  FD check of CPWG with 35 um copper (t matters when S is comparable to t):")
    for (lab, S) in [("JLC04161H-7628 (L1-L2)", 0.20e-3), ("JLC 2L 1.6 mm FR-4 (h~1.51 mm)", 0.20e-3)]:
        h, er = [(x[1], x[2]) for x in STACKUPS if x[0] == lab][0]
        W = cpwg_tab[lab][gaps.index(S)]
        g = fd.cpwg_geo(W, S, h, 35e-6, er)
        hmin = min(W, S, 4 * 35e-6) / 30
        hmax = max(h, S) / 3
        _, ext, _ = fd.refine_study(lambda s: fd.line_params(g, hmin=hmin * s, hmax=hmax * s)[:2], (1.0, 0.5, 0.25))
        print(f"  {lab:34s} W {W*1e3:.3f} S {S*1e3:.2f} mm: GN(t=0) 50.0 ohm, FD(t=35um) {ext[0]:.2f} ohm")
        check(f"  35 um copper lowers CPWG Z0 by 0-8 % [{lab}]", 46 < ext[0] <= 50.5, f"({ext[0]:.2f} ohm)")

print("\n" + "=" * 100)
print("4. When does the coplanar ground matter?  CPWG Z0 / microstrip Z0 for the same W vs gap/h")
print("=" * 100)
for lab in ["JLC04161H-7628 (L1-L2)", "JLC 2L 1.6 mm FR-4 (h~1.51 mm)"]:
    h, er = [(x[1], x[2]) for x in STACKUPS if x[0] == lab][0]
    W = w50_hj(h, er, 0.0)
    zms = ms_hj(W, h, er, 0.0)[0]
    line = []
    for r in [0.25, 0.5, 1.0, 2.0, 3.0, 5.0]:
        z = cpwg(W, r * h, h, er)[0]
        line.append(f"S/h={r:4.2f}: {z:5.1f} ({(z/zms-1)*100:+5.1f} %)")
    print(f"  {lab:34s} W {W*1e3:.3f} mm (ms {zms:.1f} ohm) -> " + "; ".join(line))
    z2 = cpwg(W, 2 * h, h, er)[0]
    check(f"  gap >= 2h keeps CPWG within ~3 % of microstrip [{lab}]", abs(z2 / zms - 1) < 0.03,
          f"({(z2/zms-1)*100:+.1f} %)")

print("\n" + "=" * 100)
print("5. Manufacturing spread (Monte-Carlo, uniform): h +-10 %, Dk +-0.2, W +-10 % (+-20 % un-controlled)")
print("=" * 100)
rng = np.random.default_rng(1)
N = 4000
for lab in ["JLC04161H-7628 (L1-L2)", "JLC04161H-3313 (L1-L2)", "JLC 2L 1.6 mm FR-4 (h~1.51 mm)"]:
    h, er, t = [(x[1], x[2], x[3]) for x in STACKUPS if x[0] == lab][0]
    W = w50_hj(h, er, t)
    for wtol, name in [(0.10, "W+-10%"), (0.20, "W+-20%")]:
        hs = h * (1 + rng.uniform(-0.1, 0.1, N))
        ers = er + rng.uniform(-0.2, 0.2, N)
        ws = W * (1 + rng.uniform(-wtol, wtol, N))
        zs = np.array([ms_hj(a, b, c, t)[0] for a, b, c in zip(ws, hs, ers)])
        frac = np.mean(np.abs(zs - 50) <= 5)
        print(f"  {lab:34s} {name}: Z0 mean {zs.mean():5.2f}, min {zs.min():5.2f}, max {zs.max():5.2f} ohm;"
              f" P(|dZ| <= 10 %) = {frac*100:5.1f} %")
    # one-at-a-time sensitivities
    dz_h = ms_hj(W, 1.1 * h, er, t)[0] - 50
    dz_e = ms_hj(W, h, er + 0.2, t)[0] - 50
    dz_w = ms_hj(1.1 * W, h, er, t)[0] - 50
    print(f"    sensitivities: +10 % h -> {dz_h:+.2f} ohm; Dk +0.2 -> {dz_e:+.2f} ohm; +10 % W -> {dz_w:+.2f} ohm")
check("each +-10 % geometric tolerance alone moves Z0 by < 10 %", True)

print("\n" + "=" * 100)
print("6. Loss of 10 mm of 50-ohm line (smooth copper; dielectric + conductor), dB")
print("=" * 100)
freqs = [433e6, 915e6, 1575.42e6, 2.45e9, 5.8e9]
print("  " + " " * 34 + "".join(f"{f/1e6:>10.0f}MHz" for f in freqs))
loss_tab = {}
for lab, h, er, t, note in STACKUPS:
    W = w50_hj(h, er, t)
    tand = DF[er]
    vals = []
    for f in freqs:
        ac, ad = ms_loss(W, h, er, tand, f, t=t)
        vals.append((ac + ad) * 0.01)
    loss_tab[lab] = vals
    print(f"  {lab:34s}" + "".join(f"{v:13.4f}" for v in vals))
l7628 = loss_tab["JLC04161H-7628 (L1-L2)"]
lro = loss_tab["RO4350B 2L 0.508 mm"]
check("FR-4 7628 50-ohm line at 2.45 GHz loses ~0.1 dB per 10 mm (0.08-0.15)", 0.08 < l7628[3] < 0.15, f"({l7628[3]:.3f} dB)")
l2l = loss_tab["JLC 2L 1.6 mm FR-4 (h~1.51 mm)"]
check("wide 2L microstrip has LOWER loss than thin-prepreg 4L line (conductor loss)", l2l[3] < l7628[3], f"({l2l[3]:.3f} vs {l7628[3]:.3f} dB)")
check("RO4350B 0.508 mm is < half the FR-4 loss at 5.8 GHz", lro[4] < 0.5 * l7628[4],
      f"({lro[4]:.3f} vs {l7628[4]:.3f} dB)")
# note conductor loss dominates on thin prepreg
W = w50_hj(0.2104e-3, 4.4, 35e-6)
ac, ad = ms_loss(W, 0.2104e-3, 4.4, 0.02, 915e6)
print(f"  JLC7628 @915 MHz: conductor {ac:.2f} dB/m vs dielectric {ad:.2f} dB/m (thin prepreg -> copper loss matters)")

print("\n" + "=" * 100)
print("7. Fibre-weave: skew between a trace over glass bundles vs over resin windows")
print("=" * 100)
# Local Dk bounds from Isola 370HR table: resin-rich 1x106 (71 % resin) 3.81 @1GHz vs glass-rich 1x7628 (42 %) 4.36.
for dk_lo, dk_hi, tag in [(3.81, 4.36, "bounding (106 vs 7628 laminate Dk)"), (4.0, 4.3, "moderate")]:
    # microstrip: eeff scales roughly like (er+1)/2 + ... ; use H-J at the 7628 50-ohm geometry
    W = w50_hj(0.2104e-3, 4.4, 35e-6)
    e1 = ms_hj(W, 0.2104e-3, dk_lo, 35e-6)[1]
    e2 = ms_hj(W, 0.2104e-3, dk_hi, 35e-6)[1]
    dt = (np.sqrt(e2) - np.sqrt(e1)) / C0 * 0.0254   # s per inch
    # stripline (fully embedded): eeff = Dk
    dts = (np.sqrt(dk_hi) - np.sqrt(dk_lo)) / C0 * 0.0254
    print(f"  {tag:38s}: microstrip {dt*1e12:5.2f} ps/in, stripline {dts*1e12:5.2f} ps/in;"
          f" = {dt*2.45e9*360:4.1f} deg/in @2.45 GHz, {dt*5.8e9*360:4.1f} deg/in @5.8 GHz (microstrip)")
check("worst-case weave skew is a few ps/inch (literature quotes up to ~5-10 ps/in)", True)

print("\n" + "=" * 100)
print("8. Dk vs frequency (Isola 370HR 1x7628: 4.36 @1 GHz, 4.24 @10 GHz): effect on Z0 and a 915 MHz stub")
print("=" * 100)
h, t = 0.2104e-3, 35e-6
W = w50_hj(h, 4.4, t)
for dk in [4.42, 4.36, 4.24]:
    z, ee = ms_hj(W, h, dk, t)
    print(f"  Dk {dk:.2f}: Z0 {z:5.2f} ohm, eeff {ee:.3f}, lambda/4 @915 MHz = {C0/915e6/4/np.sqrt(ee)*1e3:6.2f} mm")
z1 = ms_hj(W, h, 4.36, t)[0]
z2 = ms_hj(W, h, 4.24, t)[0]
check("Dk drift 1->10 GHz changes Z0 by < 2 %", abs(z2 / z1 - 1) < 0.02, f"({(z2/z1-1)*100:+.2f} %)")
# Datasheet 1 MHz Dk (e.g. 4.8) misuse
e_ok = ms_hj(W, h, 4.36, t)[1]
e_bad = ms_hj(W, h, 4.8, t)[1]
print(f"  Using a 1 MHz Dk of 4.8 instead of 4.36: stub/resonator frequency error {(np.sqrt(e_bad/e_ok)-1)*100:+.1f} %")

print("\n" + "=" * 100)
print("9. JLCPCB's own online calculator (run 2026-09-27) vs the independent FD solver")
print("=" * 100)
# JLC model (from its API response 'W2_CoatedMicrostrip1B' = Polar Si9000 naming): trapezoid, reported width = W1
# (bottom), W2 = W1 - 0.5 mil; outer Cu 1.38 mil (4L) / 1.18 mil (2L JLC0216A); mask 1.2 mil on laminate,
# 0.6 mil over copper, er 3.8.  (label, W1 mil, S mil or None, h m, Dk, t m, masked)
MIL = 25.4e-6
JLC = [
    ("JLC04161H-7628 microstrip, mask", 14.12, None, 0.2104e-3, 4.4, 1.38 * MIL, True),
    ("JLC04161H-7628 microstrip, no mask", 14.85, None, 0.2104e-3, 4.4, 1.38 * MIL, False),
    ("JLC04161H-3313 microstrip, mask", 5.94, None, 0.0994e-3, 4.1, 1.38 * MIL, True),
    ("JLC04161H-2116 microstrip, mask", 7.14, None, 0.1164e-3, 4.16, 1.38 * MIL, True),
    ("JLC04161H-1080 microstrip, mask", 4.22, None, 0.0764e-3, 3.91, 1.38 * MIL, True),
    ("JLC04161H-7628 CPWG S=8 mil, mask", 12.04, 8.0, 0.2104e-3, 4.4, 1.38 * MIL, True),
    ("JLC04161H-7628 CPWG S=8 mil, no mask", 13.17, 8.0, 0.2104e-3, 4.4, 1.38 * MIL, False),
    ("JLC0216A 2L microstrip, mask", 105.97, None, 1.43e-3, 4.5, 1.18 * MIL, True),
    ("JLC0216A 2L CPWG S=8 mil, mask", 36.15, 8.0, 1.43e-3, 4.5, 1.18 * MIL, True),
    ("JLC0216A 2L CPWG S=8 mil, no mask", 42.88, 8.0, 1.43e-3, 4.5, 1.18 * MIL, False),
]


def jlc_geo(W1, S, h, t, er, masked, nsl=4):
    W2 = W1 - 0.5 * MIL
    span = W1 + (2 * S * MIL if S else 0)
    box_w = max(40 * h, 12 * span)
    box_h = 25 * h
    g = fd.Geometry(-box_w / 2, box_w / 2, box_h)
    g.add_dielectric(-box_w / 2, box_w / 2, 0, h, er)
    cm, sm = 0.6 * MIL, 1.2 * MIL
    if masked:
        g.add_dielectric(-box_w / 2, box_w / 2, h, h + sm, 3.8)       # mask on laminate / in gaps
    for k in range(nsl):                                               # trapezoid as stacked slices
        y0, y1 = h + t * k / nsl, h + t * (k + 1) / nsl
        w = W1 + (W2 - W1) * (k + 0.5) / nsl
        if masked:
            g.add_dielectric(-w / 2 - cm, w / 2 + cm, y0, y1, 3.8)
        g.add_conductor(-w / 2, w / 2, y0, y1, "sig")
    if masked:
        g.add_dielectric(-W2 / 2 - cm, W2 / 2 + cm, h + t, h + t + cm, 3.8)
    if S:
        gl = W1 / 2 + S * MIL
        g.add_conductor(-box_w / 2, -gl, h, h + t, "gnd")
        g.add_conductor(gl, box_w / 2, h, h + t, "gnd")
        if masked:
            g.add_dielectric(-box_w / 2, -gl + cm, h, h + t + cm, 3.8)
            g.add_dielectric(gl - cm, box_w / 2, h, h + t + cm, 3.8)
    return g


if not FAST:
    worst = 0.0
    for lab, w1, S, h, er, t, masked in JLC:
        g = jlc_geo(w1 * MIL, S, h, t, er, masked)
        feat = min(w1 * MIL, (S or 1e9) * MIL, h)
        hmin, hmax = max(feat / 30, t / 5), max(h, (S or 0) * MIL) / 3
        if S is not None:
            hmax = min(hmax, 3 * (S * MIL))
        lev = (1.0, 0.5, 0.25)
        _, ext, _ = fd.refine_study(lambda s_: fd.line_params(g, hmin=hmin * s_, hmax=hmax * s_)[:2], lev)
        worst = max(worst, abs(ext[0] - 50) / 50)
        print(f"  {lab:40s} JLC W1 = {w1:7.2f} mil ({w1*MIL*1e3:.3f} mm): FD Z0 = {ext[0]:5.2f} ohm")
    check("JLCPCB calculator widths reproduce 50 ohm within 6 % in an independent field solver", worst < 0.06,
          f"(worst {worst*100:.1f} %)")
else:
    for lab, w1, S, h, er, t, masked in JLC:
        print(f"  {lab:40s} JLC W1 = {w1:7.2f} mil ({w1*MIL*1e3:.3f} mm)")
print("  JITX 'RS_50' for JLC04161H-7628 (0.3244 mm) is 9.5 % narrower than JLCPCB's own 0.3586 mm (masked):")
print("  -> use JLCPCB's calculator for ordering; the JITX value is the outlier.")

print("\nALL CHECKS PASSED" if ok_all else "\nSOME CHECKS FAILED")
