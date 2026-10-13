#!/usr/bin/env python3
"""
pcb_return_current.py — verification script for kb/13-pcb-rf-layout-emc/grounding-and-return-paths.md

Checks / calculations
  1. Image theory: return-current density in a ground plane under a filament at height h,
     K(x) = (I/pi) h/(h^2 + x^2); fraction within +-x = (2/pi) atan(x/h); tabulated for JLC stackups.
  2. Independent numerical check: 2-D finite-difference Laplace solution of an air-filled strip over a plane;
     the induced surface charge on the plane (proportional to the TEM return-current density) vs the formula,
     for a thin strip (W = 0.1 h) and a 50-ohm-like strip (W = 1.8 h).
  3. Effective width of the return path (for plane resistance): R' = R_sq * integral(K^2)/I^2 = R_sq/(2 pi h).
  4. Low-frequency crossover: when does the return stop taking the lowest-resistance path and start following
     the trace?  Two-branch R-L model for a U-shaped trace; f_c ~ dR / (2 pi dL).
  5. Crosstalk to a neighbouring trace through the shared plane / fringing field ~ 1/(1+(D/h)^2) (Johnson & Graham).
  6. Crossing a slot: series inductance (slotline estimate, as in 04 page), return loss of a 50-ohm line,
     and the voltage the slot develops across the two plane halves (a common-mode source) with an EMC estimate.
  7. Layer change: loop inductance added by a return (stitching) via at distance s from a signal via through the
     JLC-7628 core, and by relying on a decoupling capacitor instead (plane-to-plane return).
  9. Cross-hatched reference plane: Z0 over hatch lines vs gaps (2-D FD).
  8. "Star ground" wires at RF: inductance and reactance of 10-50 mm ground wires/traces vs a plane; quarter-wave
     resonance lengths.

Run: python3 tools/verify/pcb_return_current.py      (about 30-60 s)
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

MU0 = 4e-7 * np.pi
C0 = 299_792_458.0
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def frac_within(x, h):
    return 2 / np.pi * np.arctan(x / h)


print("=" * 96)
print("1. Filament over a plane: K(x) = I h / (pi (h^2 + x^2))")
print("=" * 96)
for n in [0.5, 1, 2, 3, 5, 10, 20]:
    print(f"  fraction of return current within +-{n:>4} h : {frac_within(n, 1)*100:6.2f} %")
check("50 % of the return current lies within +-h", abs(frac_within(1, 1) - 0.5) < 1e-12)
for lab, h in [("JLC04161H-7628 (L1-L2 0.2104 mm)", 0.2104e-3), ("JLC04161H-3313 (0.0994 mm)", 0.0994e-3),
               ("2-layer 1.6 mm (h ~1.43-1.51 mm)", 1.51e-3)]:
    x90 = h * np.tan(0.9 * np.pi / 2)
    x99 = h * np.tan(0.99 * np.pi / 2)
    print(f"  {lab:34s}: 90 % within +-{x90*1e3:6.2f} mm, 99 % within +-{x99*1e3:6.1f} mm")

print("\n" + "=" * 96)
print("2. Independent 2-D FD Laplace check (air-filled strip over plane, induced charge on the plane)")
print("=" * 96)


def fd_plane_charge(W, h=1.0, box_w=60.0, box_h=30.0, d=0.02):
    """Uniform-grid 5-point Laplace; strip (zero thickness) at y=h, |x|<=W/2, at 1 V; box walls and y=0 at 0 V.
    Returns x (cell centres along the plane) and sigma(x) (normalised so integral = 1)."""
    nx = int(round(box_w / d)) + 1
    ny = int(round(box_h / d)) + 1
    x = np.linspace(-box_w / 2, box_w / 2, nx)
    y = np.linspace(0, box_h, ny)
    idx = -np.ones((nx, ny), int)
    fixed = np.zeros((nx, ny), bool)
    val = np.zeros((nx, ny))
    fixed[0, :] = fixed[-1, :] = fixed[:, 0] = fixed[:, -1] = True
    js = int(round(h / d))
    strip = np.abs(x) <= W / 2 + 1e-12
    fixed[strip, js] = True
    val[strip, js] = 1.0
    free = ~fixed
    idx[free] = np.arange(free.sum())
    N = free.sum()
    rows, cols, data = [], [], []
    b = np.zeros(N)
    I, J = np.nonzero(free)
    k = idx[I, J]
    rows.append(k); cols.append(k); data.append(np.full(k.size, -4.0))
    for di, dj in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        I2, J2 = I + di, J + dj
        nb_free = free[I2, J2]
        rows.append(k[nb_free]); cols.append(idx[I2[nb_free], J2[nb_free]]); data.append(np.ones(nb_free.sum()))
        np.add.at(b, k[~nb_free], -val[I2[~nb_free], J2[~nb_free]])
    A = sp.csr_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))), shape=(N, N))
    phi = np.zeros((nx, ny))
    phi[fixed] = val[fixed]
    phi[free] = spla.spsolve(A.tocsc(), b)
    sigma = phi[:, 1] / d          # E_y at the plane (eps0 omitted)
    sigma /= np.trapezoid(sigma, x) if hasattr(np, "trapezoid") else np.trapz(sigma, x)
    return x, sigma


def frac_num(x, s, X):
    m = np.abs(x) <= X
    integ = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    return integ(s[m], x[m])


for W, tag in [(0.1, "thin strip W = 0.1 h"), (1.8, "50-ohm-like strip W = 1.8 h (FR-4 microstrip)")]:
    x, s = fd_plane_charge(W, d=0.04)
    # normalise both FD and formula to the charge within +-20 h (removes the grounded-box truncation)
    tot = frac_num(x, s, 20.0)
    ftot = frac_within(20.0, 1)
    print(f"  {tag}:")
    errs = []
    for X in [0.5, 1, 2, 3, 5, 10]:
        a_, b_ = frac_num(x, s, X) / tot, frac_within(X, 1) / ftot
        errs.append(abs(a_ - b_))
        print(f"    within +-{X:>4} h (of the charge within +-20 h): FD {a_*100:6.2f} %   filament formula {b_*100:6.2f} %")
    i0 = np.argmin(abs(x))
    shape = [(X, s[np.argmin(abs(x - X))] / s[i0], 1 / (1 + X**2)) for X in [0.5, 1, 2, 3]]
    print("    density ratio K(x)/K(0): " + ", ".join(f"x={X}h FD {a_:.3f} vs {b_:.3f}" for X, a_, b_ in shape))
    if W < 0.5:
        check("thin strip: FD return distribution matches (2/pi)atan(x/h) within 1.5 % points", max(errs) < 0.015,
              f"(worst {max(errs)*100:.2f} points)")
    else:
        f3 = frac_num(x, s, 3) / tot
        print(f"    peak density FD {s[i0]*tot:.3f}/h vs filament 1/pi = {1/np.pi:.3f}/h (wide strip is flatter)")
        check("50-ohm strip: ~80 % of return within +-3h (broadened only near the centre)", 0.75 < f3 < 0.9,
              f"({f3*100:.1f} %)")

print("\n" + "=" * 96)
print("3. Effective width of the return path: R' = R_sq/(2 pi h)")
print("=" * 96)
from scipy.integrate import quad  # noqa: E402
hh = 1.0
integral = quad(lambda x: (hh / (np.pi * (hh**2 + x**2))) ** 2, -np.inf, np.inf)[0]
check("integral of K^2 = 1/(2 pi h)", abs(integral - 1 / (2 * np.pi * hh)) < 1e-9, f"({integral:.6f} vs {1/(2*np.pi):.6f})")
rho = 1.72e-8
for lab, h, tcu in [("JLC7628, L2 0.5 oz (15.2 um)", 0.2104e-3, 15.2e-6), ("2-layer 1.6 mm, 1 oz (35 um)", 1.51e-3, 35e-6)]:
    rsq = rho / tcu
    print(f"  {lab:32s}: R_sq {rsq*1e3:.2f} mOhm/sq, effective return width 2*pi*h = {2*np.pi*h*1e3:.2f} mm,"
          f" plane R' = {rsq/(2*np.pi*h):.3f} Ohm/m (DC value; skin effect raises it at RF)")

print("\n" + "=" * 96)
print("4. Low-frequency crossover (two-branch model, U-shaped trace 3 x 50 mm, ends 50 mm apart)")
print("=" * 96)


def loop_square_L(a, r):
    """Inductance of a square loop of side a, wire radius r (Grover): (2 mu0 a / pi)(ln(a/r) - 0.774)."""
    return 2 * MU0 * a / np.pi * (np.log(a / r) - 0.774)


a = 0.05
L_big = loop_square_L(a, 0.1e-3)          # trace + direct (short-cut) return through the plane
for lab, h, tcu in [("JLC7628 inner plane 15 um", 0.2104e-3, 15.2e-6), ("2-layer 1.6 mm, 35 um plane", 1.51e-3, 35e-6)]:
    rsq = rho / tcu
    L_under = 0.33e-9 / 1e-3 * 3 * a * (h / 0.2104e-3) ** 0.0  # microstrip loop L' ~0.31-0.33 nH/mm (04 page)
    if h > 1e-3:
        L_under = 0.31e-9 / 1e-3 * 3 * a
    R_under = rsq / (2 * np.pi * h) * 3 * a     # return confined under the 150 mm trace
    R_direct = rsq * 2.0                        # a few squares across the plane (order of magnitude)
    fc = (R_under - R_direct) / (2 * np.pi * (L_big - L_under))
    print(f"  {lab}: R_under {R_under*1e3:.1f} mOhm, R_direct {R_direct*1e3:.2f} mOhm, L_under-loop {L_under*1e9:.0f} nH,"
          f" L_direct-loop {L_big*1e9:.0f} nH -> crossover f_c ~ dR/(2 pi dL) = {fc/1e3:.1f} kHz")
    check(f"  crossover lies between 1 kHz and 1 MHz [{lab}]", 1e3 < fc < 1e6, f"({fc/1e3:.1f} kHz)")
print("  (a lumped two-branch divider without mutual inductance cannot give the high-frequency limit; the field")
print("   solution of section 2 shows that once inductance dominates, the return concentrates under the trace.)")

print("\n" + "=" * 96)
print("5. Crosstalk through fringing field: relative coupling 1/(1+(D/h)^2)")
print("=" * 96)
for lab, h in [("JLC7628 h=0.21 mm", 0.2104e-3), ("2L h=1.5 mm", 1.51e-3)]:
    vals = [(D, 1 / (1 + (D / h) ** 2)) for D in [0.5e-3, 1e-3, 2e-3, 5e-3]]
    print(f"  {lab:18s}: " + ", ".join(f"D={D*1e3:.1f} mm: {20*np.log10(v):6.1f} dB" for D, v in vals))
k1 = 1 / (1 + (1e-3 / 0.2104e-3) ** 2)
k2 = 1 / (1 + (1e-3 / 1.51e-3) ** 2)
check("same 1 mm spacing couples ~16 dB less on 0.21 mm prepreg than on 1.5 mm", 20 * np.log10(k2 / k1) > 14,
      f"({20*np.log10(k2/k1):.1f} dB)")

print("\n" + "=" * 96)
print("6. Crossing a slot in the reference plane")
print("=" * 96)
Zslot = 100.0
vs = C0 / np.sqrt((4.4 + 1) / 2)
for ls in [5e-3, 10e-3, 20e-3, 40e-3]:
    for f in [100e6, 915e6, 2.45e9]:
        bl = 2 * np.pi * f / vs * ls / 2
        X = Zslot / 2 * np.tan(bl) if bl < np.pi / 2 else np.inf
        G = abs(1j * X / (2 * 50 + 1j * X)) if np.isfinite(X) else 1.0
        rl = -20 * np.log10(G) if G > 0 else np.inf
        print(f"  slot {ls*1e3:4.0f} mm @ {f/1e6:6.0f} MHz: X = {X:7.2f} Ohm, |Gamma| {G:.3f}, RL {rl:5.1f} dB")
Lslot20 = Zslot * 20e-3 / (4 * vs)
print(f"  20 mm slot, low-frequency inductance Z_slot*l/(4v) = {Lslot20*1e9:.2f} nH; lambda/2 resonance of slot at"
      f" {vs/(2*0.02)/1e9:.2f} GHz; a 915 MHz resonant slot is {vs/(2*915e6)*1e3:.0f} mm long")
# common-mode voltage developed across the slot by a digital harmonic crossing it
I_h, f_h = 10e-3, 100e6
V_slot = I_h * 2 * np.pi * f_h * Lslot20
Icm_lo, Icm_hi = V_slot / 300, V_slot / 150
E = 1.257e-6 * f_h * 1.0 * np.array([Icm_lo, Icm_hi]) / 3
print(f"  10 mA harmonic at 100 MHz across it: V_slot = {V_slot*1e3:.1f} mV; driving a 1 m cable (Z_cm 150-300 Ohm) ->"
      f" I_cm {Icm_lo*1e6:.0f}-{Icm_hi*1e6:.0f} uA -> E(3 m) = {E[0]*1e6:.0f}-{E[1]*1e6:.0f} uV/m vs FCC B 150 uV/m"
      f" ({20*np.log10(E[0]/150e-6):.0f} to {20*np.log10(E[1]/150e-6):.0f} dB over)")
check("a 20 mm slot under a 100 MHz, 10 mA harmonic can push a cable 20+ dB over Class B", E[0] > 10 * 150e-6)

print("\n" + "=" * 96)
print("7. Changing reference layer: return via / stitching capacitor")
print("=" * 96)
h_core = 1.065e-3 + 2 * 0.2104e-3   # L1->L4 through-via length between L2 and L3 planes is the core ~1.065 mm
hc = 1.065e-3
r = 0.15e-3
for s in [0.6e-3, 1e-3, 2e-3, 5e-3, 10e-3]:
    L = MU0 / np.pi * hc * np.log(s / r)
    print(f"  return (GND-GND stitching) via at {s*1e3:4.1f} mm: loop L {L*1e9:5.2f} nH -> {2*np.pi*915e6*L:5.2f} Ohm @915 MHz,"
          f" {2*np.pi*2.45e9*L:5.2f} Ohm @2.45 GHz")
L1mm = MU0 / np.pi * hc * np.log(1e-3 / r)
check("a stitching via 1 mm from the signal via adds < 1 nH through the JLC 1.065 mm core", L1mm < 1e-9,
      f"({L1mm*1e9:.2f} nH)")
# relying on a decoupling cap between L2 (GND) and L3 (PWR) instead: ESL + mounting ~ 0.7-1.5 nH
for Lcap in [0.7e-9, 1.5e-9]:
    print(f"  via a GND-PWR decoupling cap (ESL+mount {Lcap*1e9:.1f} nH): {2*np.pi*915e6*Lcap:5.2f} Ohm @915 MHz, plus"
          f" the distance to the cap (plane-pair spreading inductance)")

print("\n" + "=" * 96)
print("8. 'Star ground' wires at RF")
print("=" * 96)


def wire_L(l, r):
    return MU0 * l / (2 * np.pi) * (np.log(2 * l / r) - 1)


for l in [10e-3, 30e-3, 50e-3]:
    L = wire_L(l, 0.15e-3)    # 0.3 mm wide trace ~ r 0.15 mm, far from a plane
    print(f"  {l*1e3:3.0f} mm ground trace (no plane): L ~ {L*1e9:5.1f} nH -> {2*np.pi*433e6*L:6.1f} Ohm @433 MHz,"
          f" {2*np.pi*915e6*L:6.1f} Ohm @915 MHz; quarter-wave (air/FR-4 eeff 3) at 915 MHz = "
          f"{C0/915e6/4*1e3:.0f}/{C0/915e6/4/np.sqrt(3)*1e3:.0f} mm")
L30 = wire_L(30e-3, 0.15e-3)
check("a 30 mm 'star' ground trace is > 100 Ohm at 915 MHz (i.e. not a ground)", 2 * np.pi * 915e6 * L30 > 100,
      f"({2*np.pi*915e6*L30:.0f} Ohm)")

print("\n" + "=" * 96)
print("9. Cross-hatched reference plane (flex-style): Z0 of a trace over hatch lines vs gaps (2-D FD, hatch lines")
print("   parallel to the trace = worst case; polyimide h = 0.1 mm, er 3.3, W = 0.2 mm, 18 um copper)")
print("=" * 96)
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import tline_fd2d as fd  # noqa: E402


def hatch_geo(W, h, er, t, wl, pitch, offset, solid=False):
    drop = 6 * h
    box_w = max(40 * h, 8 * pitch)
    g = fd.Geometry(-box_w / 2, box_w / 2, drop + 15 * h)
    g.add_dielectric(-box_w / 2, box_w / 2, drop, drop + h, er)
    if solid:
        g.add_conductor(-box_w / 2, box_w / 2, drop - t, drop, "gnd")
    else:
        n = int(box_w / 2 / pitch) + 1
        for k in range(-n, n + 1):
            xc = k * pitch + offset
            if abs(xc) + wl / 2 < box_w / 2:
                g.add_conductor(xc - wl / 2, xc + wl / 2, drop - t, drop, "gnd")
    g.add_conductor(-W / 2, W / 2, drop + h, drop + h + t, "sig")
    return g


def z_fd(g, W, h):
    hmin, hmax = min(W, h) / 8, h / 1.5
    _, ext, _ = fd.refine_study(lambda s_: fd.line_params(g, hmin=hmin * s_, hmax=hmax * s_)[:2], (1.0, 0.5, 0.25))
    return ext[0]


Wt, ht, ert, tt = 0.2e-3, 0.1e-3, 3.3, 18e-6
zs = z_fd(hatch_geo(Wt, ht, ert, tt, 0, 0.0, 0, True), Wt, ht)
print(f"  solid plane: Z0 = {zs:.1f} ohm")
hz = {}
for wl, pch in [(0.2e-3, 0.6e-3), (0.2e-3, 1.0e-3)]:
    for off, tag in [(0.0, "over a hatch line"), (pch / 2, "over a gap")]:
        z = z_fd(hatch_geo(Wt, ht, ert, tt, wl, pch, off), Wt, ht)
        hz[(pch, tag)] = z
        print(f"  hatch {wl*1e3:.1f} mm lines at {pch*1e3:.1f} mm pitch, trace {tag:17s}: Z0 = {z:6.1f} ohm ({(z/zs-1)*100:+.0f} %)")
check("a hatched reference raises Z0 and makes it depend on lateral position (over-gap > over-line > solid)",
      hz[(1.0e-3, "over a gap")] > hz[(1.0e-3, "over a hatch line")] > zs)

print("\nALL CHECKS PASSED" if ok_all else "\nSOME CHECKS FAILED")
