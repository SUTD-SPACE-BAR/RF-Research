#!/usr/bin/env python3
"""
s12_mutual_hallen.py -- W5-S12 (G-08-06): checks for the Pocklington/Hallen derivation and the induced-EMF mutual
impedance written on kb/08-antennas/antenna-simulation-nec-openems.md and dipoles-and-monopoles.md.

 1. Hallen's equation solved directly (pulse basis, point matching at segment centres plus the wire end, delta-gap
    source, reduced kernel with the 1/R part integrated analytically) -> Z_in of a centre-fed dipole; compared with
    the KB Galerkin mixed-potential MoM (ant_mom_wire.py, which is the weak form of Pocklington's equation) and NEC-2.
 2. The zeroth-order (Omega -> infinity) Hallen solution: current sin k(h-|z|) and the purely reactive
    Z0 = -j (eta/pi) ln(2h/a) cot(kh); compared with the full solutions for short dipoles.
 3. Induced-EMF mutual impedance of parallel lambda/2 dipoles: (a) closed form (Si/Ci) for side-by-side dipoles,
    (b) the same quantity by numerically integrating the exact near field of a sinusoidal current
    (E_z = -j 30 I_m [e^{-jkR1}/R1 + e^{-jkR2}/R2 - 2 cos(kh) e^{-jkr}/r]) against the second dipole's current,
    (c) two-port open-circuit Z21 from NEC-2 and from the KB MoM; also collinear and echelon geometries.
 4. Two coupled dipoles: driving-point impedance Z11 + Z12 (in-phase) and Z11 - Z12 (antiphase) vs NEC.
Run: python3 tools/verify/s12_mutual_hallen.py   (~1 min)
"""
import os
import sys
import numpy as np
from scipy.special import sici
from scipy.integrate import quad

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import PyNEC                                       # noqa: E402
from ant_mom_wire import Wire, solve as mom_solve  # noqa: E402

C0 = 299792458.0
MU0 = 4e-7 * np.pi
EPS0 = 1 / (MU0 * C0 ** 2)
ETA = np.sqrt(MU0 / EPS0)
results, misses = [], []
gx, gw = np.polynomial.legendre.leggauss(12)


def say(s=""):
    print(s); results.append(s)


def check(name, cond, detail=""):
    if not cond:
        misses.append(name)
    say(f"[{'PASS' if cond else 'MISS'}] {name} {detail}")


# ------------------------------------------------------------------------------------------- 1. Hallen solver
def hallen(L_l, a_l, N=101):
    """centre-fed dipole of length L (wavelengths), radius a (wavelengths), lambda = 1, V = 1. Returns Zin, z, I."""
    k = 2 * np.pi
    h = L_l / 2
    edges = np.linspace(-h, h, N + 1)
    zc = (edges[:-1] + edges[1:]) / 2
    zm = np.concatenate([zc, [h]])                   # N centres + the end point
    A = np.zeros((N + 1, N + 1), dtype=complex)
    for m, z in enumerate(zm):
        z1, z2 = edges[:-1], edges[1:]
        # analytic 1/R part
        A[m, :N] = (np.arcsinh((z2 - z) / a_l) - np.arcsinh((z1 - z) / a_l)) / (4 * np.pi)
        # smooth remainder (exp(-jkR)-1)/R by Gauss-Legendre per segment
        zq = (z1 + z2)[:, None] / 2 + (z2 - z1)[:, None] / 2 * gx[None, :]
        R = np.sqrt((z - zq) ** 2 + a_l ** 2)
        A[m, :N] += ((np.exp(-1j * k * R) - 1) / R * gw[None, :]).sum(axis=1) * (z2 - z1) / 2 / (4 * np.pi)
        A[m, N] = -np.cos(k * z)                     # unknown C1 (homogeneous solution)
    rhs = -1j / (2 * ETA) * np.sin(k * np.abs(zm))   # particular solution of (d2/dz2 + k^2) psi = -j w eps V delta(z)
    x = np.linalg.solve(A, rhs)
    I = x[:N]
    return 1.0 / I[N // 2], zc, I


def mom_dipole(L_l, a_l, nseg=100):
    wr = Wire(0, 0, -L_l / 2, L_l / 2, a_l, nseg)
    return mom_solve([wr], [(0, nseg // 2, 1.0)], C0)["Zin"][0]      # freq = c -> lambda = 1 m


def nec_dipole(L_l, a_l, nseg=41, ek=False):
    c = PyNEC.nec_context(); g = c.get_geometry()
    g.wire(1, nseg, 0, 0, -L_l / 2, 0, 0, L_l / 2, a_l, 1, 1)
    c.geometry_complete(0); c.gn_card(-1, 0, 0, 0, 0, 0, 0, 0)
    if ek:
        c.set_extended_thin_wire_kernel(True)
    c.ex_card(0, 1, nseg // 2 + 1, 0, 1.0, 0, 0, 0, 0, 0)
    c.fr_card(0, 1, C0 / 1e6, 0)
    c.xq_card(0)
    return complex(c.get_input_parameters(0).get_impedance()[0])


say("=== 1. Hallen point-matching vs Galerkin MoM (Pocklington, mixed potential) vs NEC-2: centre-fed dipole ===")
say("  L/lambda  a/lambda    Hallen N=101       Hallen N=201      KB MoM (100 seg)      NEC-2 (41 seg)")
H = {}
for L_l, a_l in ((0.5, 1e-4), (0.5, 1e-3), (0.47, 1e-3), (0.25, 1e-3), (0.1, 1e-3)):
    z1 = hallen(L_l, a_l, 101)[0]; z2 = hallen(L_l, a_l, 201)[0]
    zm = mom_dipole(L_l, a_l); zn = nec_dipole(L_l, a_l)
    H[(L_l, a_l)] = (z1, z2, zm, zn)
    say(f"   {L_l:.2f}    {a_l:.0e}   {z1.real:7.2f}{z1.imag:+8.2f}j  {z2.real:7.2f}{z2.imag:+8.2f}j  "
        f"{zm.real:7.2f}{zm.imag:+8.2f}j    {zn.real:7.2f}{zn.imag:+8.2f}j")
z2, zm = H[(0.5, 1e-4)][1], H[(0.5, 1e-4)][2]
# pre-registered: "N=201 within 3 ohm of the MoM" -- MISSED on the first run (X 51.0 vs 45.3): pulse-basis point-matched
# Hallen converges only ~1/N in reactance. Convergence study + Richardson extrapolation instead:
z4 = hallen(0.5, 1e-4, 401)[0]; z8 = hallen(0.5, 1e-4, 801)[0]
zinf = 2 * z8 - z4
say(f"  thin lambda/2 (a = 1e-4): Hallen N = 201/401/801: {z2:.2f} / {z4:.2f} / {z8:.2f}; Richardson (1/N) limit {zinf:.2f} ohm; "
    f"KB MoM {zm:.2f}; NEC {H[(0.5,1e-4)][3]:.2f}")
say("  [info] pre-registered 1a (N = 201 within 3 ohm) missed: reactance converges as ~1/N with pulse basis + point matching")
check("1a Hallen extrapolated to N -> infinity agrees with the KB Galerkin MoM within 1.5 ohm (R and X)",
      abs(zinf.real - zm.real) < 1.5 and abs(zinf.imag - zm.imag) < 1.5, f"({zinf:.1f} vs {zm:.1f})")
# resonant length from Hallen, a = 1e-4 lambda (KB MoM: 0.4838 lambda, 72.0 ohm)
from scipy.optimize import brentq
Lr = brentq(lambda L: hallen(L, 1e-4, 201)[0].imag, 0.46, 0.5, xtol=1e-5)
Rr = hallen(Lr, 1e-4, 201)[0].real
say(f"  Hallen resonance (a = 1e-4 lambda): L = {Lr:.4f} lambda, R = {Rr:.1f} ohm (KB MoM: 0.4838 lambda, 72.0 ohm)")
check("1b Hallen resonant length within 0.003 lambda and R within 2 ohm of the KB MoM", abs(Lr - 0.4838) < 0.003 and abs(Rr - 72.0) < 2)

# ------------------------------------------------------------------------------------------- 2. zeroth order
say("\n=== 2. Zeroth-order Hallen: Z0 = -j (eta/pi) ln(2h/a) cot(kh) (pure reactance) vs full solutions, a = 1e-3 lambda ===")
say("  (full solutions with segment length ~5a: the reduced kernel fails when segments get shorter than ~2-3 radii,")
say("   and the delta-gap capacitance makes short-dipole X drift with segment length)")
say("  L/lambda   Z0 (zeroth order)   TL -j120[ln(L/2a)-1]cot(kh)   Hallen (seg ~5a)    KB MoM (seg ~5a)   NEC-2 (seg ~5a)")
ZZ = {}
for L_l in (0.05, 0.1, 0.2, 0.3):
    a_l = 1e-3; h = L_l / 2; k = 2 * np.pi
    N = int(L_l / (5 * a_l)) | 1
    Z0 = -1j * ETA / np.pi * np.log(2 * h / a_l) / np.tan(k * h)
    Ztl = -1j * 120 * (np.log(L_l / (2 * a_l)) - 1) / np.tan(k * h)
    zh = hallen(L_l, a_l, N)[0]; zmm = mom_dipole(L_l, a_l, N + 1); znn = nec_dipole(L_l, a_l, N)
    ZZ[L_l] = (Z0, Ztl, zh, zmm, znn)
    say(f"   {L_l:.2f}       {Z0.imag:+9.1f}j          {Ztl.imag:+9.1f}j               {zh.real:5.2f}{zh.imag:+8.1f}j"
        f"     {zmm.real:5.2f}{zmm.imag:+8.1f}j     {znn.real:5.2f}{znn.imag:+8.1f}j")
Z0, Ztl, zh, zmm, znn = ZZ[0.1]
check("2a short dipole (0.1 lambda): TL form within 10 % of the full solutions; zeroth-order Hallen is crude (30-90 % high)",
      abs(Ztl.imag - zh.imag) / abs(zh.imag) < 0.10 and 0.3 < abs(Z0.imag) / abs(zh.imag) - 1 < 0.9,
      f"(Z0 {Z0.imag:.0f}, TL {Ztl.imag:.0f}, Hallen {zh.imag:.0f}, MoM {zmm.imag:.0f}, NEC {znn.imag:.0f} ohm)")
# current shape check
_, zc, I = hallen(0.5, 1e-4, 201)
sinus = np.sin(2 * np.pi * (0.25 - np.abs(zc)))
dev = np.max(np.abs(np.abs(I) / np.abs(I).max() - sinus))
say(f"  thin lambda/2 dipole (a = 1e-4 lambda): max deviation of |I(z)|/|I|max from sin k(h-|z|) = {dev:.3f}")
check("2b Hallen current of a thin lambda/2 dipole is within 0.08 of the sinusoid (zeroth-order solution)", dev < 0.08)


# ------------------------------------------------------------------------------------------- 3. mutual impedance
def z21_closed(d):
    k = 2 * np.pi; l = 0.5
    u0 = k * d; u1 = k * (np.sqrt(d ** 2 + l ** 2) + l); u2 = k * (np.sqrt(d ** 2 + l ** 2) - l)
    s0, c0 = sici(u0); s1, c1 = sici(u1); s2, c2 = sici(u2)
    return ETA / (4 * np.pi) * ((2 * c0 - c1 - c2) - 1j * (2 * s0 - s1 - s2))


def Ez_sin(rho, z, zc=0.0, h=0.25, Im=1.0):
    """exact E_z of a filament with I = Im sin k(h-|z'-zc|) (Schelkunoff closed form), lambda = 1"""
    k = 2 * np.pi
    R1 = np.sqrt(rho ** 2 + (z - zc - h) ** 2)
    R2 = np.sqrt(rho ** 2 + (z - zc + h) ** 2)
    r = np.sqrt(rho ** 2 + (z - zc) ** 2)
    return -1j * ETA * Im / (4 * np.pi) * (np.exp(-1j * k * R1) / R1 + np.exp(-1j * k * R2) / R2
                                          - 2 * np.cos(k * h) * np.exp(-1j * k * r) / r)


def z21_numeric(d, dz=0.0, h=0.25):
    """Z21 = -(1/Im^2) int E_z21(z) I2(z) dz over dipole 2 (axis at rho = d, centre at z = dz), referred to Im"""
    k = 2 * np.pi
    def f(z, part):
        v = Ez_sin(d, z) * np.sin(k * (h - np.abs(z - dz)))
        return -(v.real if part == 0 else v.imag)
    pts = [dz]
    re = quad(f, dz - h, dz + h, args=(0,), points=pts, limit=200)[0]
    im = quad(f, dz - h, dz + h, args=(1,), points=pts, limit=200)[0]
    return re + 1j * im


def nec_twoport(pos2, L1=0.5, L2=0.5, a=1e-4, nseg=41, ek=False):
    """open-circuit two-port Z of two parallel z-directed dipoles; dipole 2 centred at pos2 = (x, z)"""
    Y = np.zeros((2, 2), dtype=complex)
    for p in range(2):
        c = PyNEC.nec_context(); g = c.get_geometry()
        g.wire(1, nseg, 0, 0, -L1 / 2, 0, 0, L1 / 2, a, 1, 1)
        g.wire(2, nseg, pos2[0], 0, pos2[1] - L2 / 2, pos2[0], 0, pos2[1] + L2 / 2, a, 1, 1)
        c.geometry_complete(0); c.gn_card(-1, 0, 0, 0, 0, 0, 0, 0)
        c.ex_card(0, p + 1, nseg // 2 + 1, 0, 1.0, 0, 0, 0, 0, 0)
        c.fr_card(0, 1, C0 / 1e6, 0); c.xq_card(0)
        cur = np.array(c.get_structure_currents(0).get_current())
        Y[0, p] = cur[nseg // 2]
        Y[1, p] = cur[nseg + nseg // 2]
    return np.linalg.inv(Y)


def mom_twoport(pos2, a=1e-4, nseg=60):
    Y = np.zeros((2, 2), dtype=complex)
    for p in range(2):
        w = [Wire(0, 0, -0.25, 0.25, a, nseg), Wire(pos2[0], 0, pos2[1] - 0.25, pos2[1] + 0.25, a, nseg)]
        fd = [(0, nseg // 2, 1.0 if p == 0 else 0.0), (1, nseg // 2, 1.0 if p == 1 else 0.0)]
        sol = mom_solve(w, fd, C0)
        for q in range(2):
            idx = [i for i, (wi, j) in enumerate(sol["basis"]) if wi == q and j == nseg // 2][0]
            Y[q, p] = sol["I"][idx]
    return np.linalg.inv(Y)


say("\n=== 3. Mutual impedance of two parallel lambda/2 dipoles (referred to the current maxima = feed currents) ===")
say("  side-by-side d/lambda   closed form (Si/Ci)     numeric near-field integral     NEC-2 two-port Z21 (a=1e-4)    KB MoM two-port")
diffs = []
for d in (0.1, 0.25, 0.5, 1.0):
    zc_ = z21_closed(d); zn_ = z21_numeric(d)
    zN = nec_twoport((d, 0.0))[1, 0]; zM = mom_twoport((d, 0.0))[1, 0]
    diffs.append(abs(zc_ - zn_))
    say(f"   {d:4.2f}                  {zc_.real:6.2f}{zc_.imag:+7.2f}j          {zn_.real:6.2f}{zn_.imag:+7.2f}j"
        f"                {zN.real:6.2f}{zN.imag:+7.2f}j               {zM.real:6.2f}{zM.imag:+7.2f}j")
check("3a closed-form Si/Ci Z21 equals the numerically integrated induced-EMF Z21 (< 0.05 ohm)", max(diffs) < 0.05,
      f"(max {max(diffs):.2e} ohm)")
zself_num = z21_numeric(1e-4)        # self impedance by the same integral with rho = a (thin wire)
say(f"  same integral with rho = a = 1e-4 lambda (self impedance): {zself_num.real:.2f}{zself_num.imag:+.2f}j "
    f"(textbook 73.08 + j42.51)")
check("3b induced-EMF self impedance from the same integral = 73.1 + j42.5 ohm (+-0.3)",
      abs(zself_num - (73.08 + 42.51j)) < 0.3)
say("  collinear (end-to-end, centre spacing s) and echelon (side offset d, axial offset s):")
say("   geometry                  induced EMF (numeric)    NEC-2 two-port")
for (d, s, lab) in ((1e-4, 0.55, "collinear s = 0.55"), (1e-4, 0.75, "collinear s = 0.75"), (1e-4, 1.0, "collinear s = 1.00"),
                    (0.25, 0.25, "echelon d = 0.25, s = 0.25"), (0.5, 0.5, "echelon d = 0.5, s = 0.5")):
    zn_ = z21_numeric(d, dz=s)
    zN = nec_twoport((d, s))[1, 0]
    say(f"   {lab:26s}  {zn_.real:6.2f}{zn_.imag:+7.2f}j          {zN.real:6.2f}{zN.imag:+7.2f}j")

# ------------------------------------------------------------------------------------------- 4. coupled pair
say("\n=== 4. Driving-point impedance of a pair, d = 0.25 lambda, resonant-length dipoles (0.48 lambda, a = 1e-3 lambda) ===")
Zp = nec_twoport((0.25, 0.0), L1=0.48, L2=0.48, a=1e-3)
for lab, ratio in (("in phase (I2 = I1)", 1), ("antiphase (I2 = -I1)", -1), ("quadrature (I2 = -j I1)", -1j)):
    Zd = Zp[0, 0] + Zp[0, 1] * ratio
    say(f"  {lab:26s}: Z1 = Z11 + Z12 I2/I1 = {Zd.real:6.1f}{Zd.imag:+6.1f}j ohm  (Z11 = {Zp[0,0]:.1f}, Z12 = {Zp[0,1]:.1f})")
# verify against a direct NEC run with both dipoles driven by current-forcing voltages
V = Zp @ np.array([1.0, 1.0])
c = PyNEC.nec_context(); g = c.get_geometry()
g.wire(1, 41, 0, 0, -0.24, 0, 0, 0.24, 1e-3, 1, 1); g.wire(2, 41, 0.25, 0, -0.24, 0.25, 0, 0.24, 1e-3, 1, 1)
c.geometry_complete(0); c.gn_card(-1, 0, 0, 0, 0, 0, 0, 0)
c.ex_card(0, 1, 21, 0, V[0].real, V[0].imag, 0, 0, 0, 0); c.ex_card(0, 2, 21, 0, V[1].real, V[1].imag, 0, 0, 0, 0)
c.fr_card(0, 1, C0 / 1e6, 0); c.xq_card(0)
zdir = complex(c.get_input_parameters(0).get_impedance()[0])
check("4a two-port prediction of the in-phase driving-point impedance matches a direct two-source NEC run (< 0.5 ohm)",
      abs(zdir - (Zp[0, 0] + Zp[0, 1])) < 0.5, f"({zdir:.2f} vs {Zp[0,0]+Zp[0,1]:.2f})")

say("\nSUMMARY: " + ("ALL PASS" if not misses else f"{len(misses)} MISS: " + "; ".join(misses)))
with open(os.path.join(HERE, "s12_mutual_hallen_output.txt"), "w") as fh:
    fh.write("\n".join(results) + "\n")
