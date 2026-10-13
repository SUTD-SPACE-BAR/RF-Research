#!/usr/bin/env python3
"""e11_greens.py — checks for kb/02-electromagnetics/greens-functions-and-integral-equations.md (W5-E11).

1. Scalar free-space Green's function g = exp(-jkR)/(4 pi R): satisfies the homogeneous Helmholtz
   equation for R > 0 and has unit delta strength (flux of grad g through a small sphere = -1).
2. Dyadic Green's function E = -j w mu (I + grad grad / k^2) g . (I l z): reproduces the full
   Hertzian-dipole fields of 02/radiation-from-currents-hertzian-dipole.md (sympy).
3. Method of moments, electrostatic: charged square plate (Harrington's classic first example),
   pulse basis + point matching, Richardson extrapolation -> C/(4 pi eps0 a) ~ 0.36.
4. Hallen's integral equation for a centre-fed dipole (pulse basis, point matching, reduced kernel)
   compared with the KB's Galerkin mixed-potential MoM (tools/verify/ant_mom_wire.py) and with the
   classical 73 + j42.5 ohm infinitely-thin half-wave value.
5. Sommerfeld identity exp(-jkR)/R = int_0^inf J0(k_rho rho) exp(-j k_z |z|) k_rho/(j k_z) dk_rho,
   checked by numerical quadrature (slightly lossy medium, engineering e^{jwt} branch Im k_z < 0).
6. Surface-wave pole of the grounded slab (the pole that makes layered-media Green's functions hard):
   TM0 beta/k0 on 1.51 mm FR-4 vs frequency; TE1 onset vs the 03 planar-lines estimate.

Run: python3 tools/verify/e11_greens.py      (~20-40 s)
"""
import os
import sys

import numpy as np
import sympy as sp
from scipy import integrate, optimize, special

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
EPS0 = 8.8541878128e-12
MU0 = 4e-7 * np.pi
C0 = 299792458.0
ETA0 = np.sqrt(MU0 / EPS0)
RES = []


def check(name, ok, detail=""):
    RES.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")


def part1_scalar():
    print("1. scalar Green's function")
    R, k = sp.symbols("R k", positive=True)
    g = sp.exp(-sp.I * k * R) / (4 * sp.pi * R)
    lap = sp.diff(R ** 2 * sp.diff(g, R), R) / R ** 2          # spherical Laplacian, radial
    check("(lap + k^2) g = 0 for R > 0", sp.simplify(lap + k ** 2 * g) == 0)
    flux = sp.limit(4 * sp.pi * R ** 2 * sp.diff(g, R), R, 0)
    check("flux of grad g through a vanishing sphere = -1 (delta strength)", sp.simplify(flux + 1) == 0, f"{flux}")
    # outgoing-wave (Sommerfeld radiation) condition: R (dg/dR + j k g) -> 0
    rc = sp.simplify(R * (sp.diff(g, R) + sp.I * k * g))      # = -exp(-jkR)/(4 pi R): magnitude 1/(4 pi R) -> 0
    check("radiation condition R(dg/dR + jkg) = -g -> 0", sp.simplify(rc + g) == 0, f"{rc}")


def part2_dyadic():
    print("2. dyadic Green's function -> Hertzian dipole fields")
    x, y, z = sp.symbols("x y z", real=True)
    k, w, mu, Il = sp.symbols("k omega mu Il", positive=True)
    r = sp.sqrt(x ** 2 + y ** 2 + z ** 2)
    g = sp.exp(-sp.I * k * r) / (4 * sp.pi * r)
    # E = -j w mu [ z_hat g + (1/k^2) grad(dg/dz) ] Il
    Ex = -sp.I * w * mu * Il * sp.diff(g, z, x) / k ** 2
    Ez = -sp.I * w * mu * Il * (g + sp.diff(g, z, z) / k ** 2)
    # evaluate on the x-z plane at a point (r, theta): compare with E_r, E_theta of the dipole page
    rr, th = sp.Rational(7, 5), sp.Rational(3, 5)       # arbitrary point (k r = 1.4 k, theta 0.6 rad)
    sub = {x: rr * sp.sin(th), y: 0, z: rr * sp.cos(th)}
    exv, ezv = sp.N(Ex.subs(sub)), sp.N(Ez.subs(sub))
    Er = exv * sp.sin(th) + ezv * sp.cos(th)
    Et = exv * sp.cos(th) - ezv * sp.sin(th)
    eta = w * mu / k                                     # eta = w mu / k
    Er_ref = eta * Il * sp.cos(th) / (2 * sp.pi * rr ** 2) * (1 + 1 / (sp.I * k * rr)) * sp.exp(-sp.I * k * rr)
    Et_ref = (sp.I * eta * k * Il * sp.sin(th) / (4 * sp.pi * rr)
              * (1 + 1 / (sp.I * k * rr) - 1 / (k * rr) ** 2) * sp.exp(-sp.I * k * rr))
    vals = {k: 2.1, w: 3.0, mu: 1.3, Il: 1.0}
    e1 = complex(sp.N((Er - Er_ref).subs(vals)))
    e2 = complex(sp.N((Et - Et_ref).subs(vals)))
    # explicit closed form of the dyadic: G = g[(1 - j/kR - 1/(kR)^2) I + (-1 + 3j/kR + 3/(kR)^2) RR]
    xs = {x: sp.Rational(3, 7), y: sp.Rational(-2, 5), z: sp.Rational(9, 10)}
    rv = sp.sqrt(sum(v ** 2 for v in xs.values()))
    kv = sp.Rational(17, 10)
    worst = 0.0
    for i, a in enumerate((x, y, z)):
        for j, b in enumerate((x, y, z)):
            num = ((1 if i == j else 0) * g + sp.diff(g, a, b) / k ** 2).subs(xs).subs(k, kv)
            gv = g.subs(xs).subs(k, kv)
            kr = kv * rv
            rh = [xs[x] / rv, xs[y] / rv, xs[z] / rv]
            cf = ((1 - sp.I / kr - 1 / kr ** 2) * (1 if i == j else 0) + (-1 + 3 * sp.I / kr + 3 / kr ** 2) * rh[i] * rh[j]) * gv
            worst = max(worst, abs(complex(sp.N(num - cf))))
    check("explicit dyadic closed form matches (I + grad grad/k^2) g", worst < 1e-12, f"max residual {worst:.1e}")
    check("dyadic G reproduces E_r and E_theta of the Hertzian dipole", abs(e1) < 1e-12 and abs(e2) < 1e-12,
          f"residuals {abs(e1):.1e}, {abs(e2):.1e}")


def _F(x, y):
    """Antiderivative of 1/sqrt(x^2+y^2) dx dy: x ln(y + r) + y ln(x + r)."""
    r = np.sqrt(x * x + y * y)
    with np.errstate(divide="ignore", invalid="ignore"):
        a = np.where(np.abs(x) > 0, x * np.log(np.abs(y + r) + 1e-300), 0.0)
        b = np.where(np.abs(y) > 0, y * np.log(np.abs(x + r) + 1e-300), 0.0)
    return a + b


def plate_capacitance(n, a=1.0):
    """Square plate side a at 1 V, n x n pulse basis (uniform charge per cell), point matching at the cell
    centres. Matrix entries are the EXACT potential of a uniformly charged square cell (closed-form panel
    integral), so the only error is the piecewise-constant charge model (edge singularity ~ rho^-1/2)."""
    d = a / n
    c = (np.arange(n) + 0.5) * d - a / 2
    X, Y = np.meshgrid(c, c, indexing="ij")
    X, Y = X.ravel(), Y.ravel()
    dx = X[:, None] - X[None, :]
    dy = Y[:, None] - Y[None, :]
    x1, x2, y1, y2 = dx - d / 2, dx + d / 2, dy - d / 2, dy + d / 2
    I = _F(x2, y2) - _F(x1, y2) - _F(x2, y1) + _F(x1, y1)
    A = I / (4 * np.pi * EPS0)
    sigma = np.linalg.solve(A, np.ones(n * n))
    return np.sum(sigma) * d * d


def part3_plate():
    print("3. MoM: capacitance of a 1 m square plate (pulse basis, point matching)")
    ns = [12, 24, 48]
    Cs = [plate_capacitance(n) for n in ns]
    for n, c in zip(ns, Cs):
        print(f"   N = {n*n:5d}: C = {c*1e12:.3f} pF  (C/4pi eps0 a = {c/(4*np.pi*EPS0):.4f})")
    # Richardson with observed order
    p = np.log(abs((Cs[0] - Cs[1]) / (Cs[1] - Cs[2]))) / np.log(2)
    Cx = Cs[2] + (Cs[2] - Cs[1]) / (2 ** p - 1)
    print(f"   extrapolated (order {p:.2f}): C = {Cx*1e12:.3f} pF, C/4pi eps0 a = {Cx/(4*np.pi*EPS0):.4f}")
    check("square plate C/(4 pi eps0 a) within 0.36 +- 0.01 (Hwang & Mascagni 2004)", abs(Cx / (4 * np.pi * EPS0) - 0.36) < 0.01)
    check("pulse-basis MoM converges monotonically (edge singularity -> order ~1)", Cs[0] < Cs[1] < Cs[2] and 0.5 < p < 1.6,
          f"order {p:.2f}")
    return Cx


def hallen_dipole(L_lam=0.5, a_lam=1e-4, N=101):
    """Hallen's equation for a centre-fed dipole (delta gap, V = 1), lengths in wavelengths:
        int_{-L/2}^{L/2} I(z') K(z - z') dz' = -(j/eta) [ C1 cos kz + (V/2) sin k|z| ],
    reduced kernel K = exp(-jkR)/(4 pi R), R = sqrt((z-z')^2 + a^2). Pulse basis on N segments, point
    matching at the N segment centres AND at the wire end z = L/2 (N + 1 equations for N currents + C1;
    by symmetry the other end is then satisfied). The 1/R part of each segment integral is done
    analytically (asinh), the smooth remainder by 8-point Gauss."""
    k = 2 * np.pi
    L, a = L_lam, a_lam
    dz = L / N
    zc = -L / 2 + (np.arange(N) + 0.5) * dz
    zm = np.concatenate([zc, [L / 2]])
    gx, gw = np.polynomial.legendre.leggauss(8)
    Z = np.zeros((N + 1, N), complex)
    for n in range(N):
        u1, u2 = zm - (zc[n] - dz / 2), zm - (zc[n] + dz / 2)
        sing = (np.arcsinh(u1 / a) - np.arcsinh(u2 / a)) / (4 * np.pi)
        zp = zc[n] + gx * dz / 2
        Rm = np.sqrt((zm[:, None] - zp[None, :]) ** 2 + a * a)
        smooth = np.sum(gw[None, :] * dz / 2 * (np.exp(-1j * k * Rm) - 1) / (4 * np.pi * Rm), axis=1)
        Z[:, n] = sing + smooth
    A = np.zeros((N + 1, N + 1), complex)
    A[:, :N] = Z
    A[:, N] = 1j / ETA0 * np.cos(k * zm)
    b = -1j / ETA0 * 0.5 * np.sin(k * np.abs(zm))
    x = np.linalg.solve(A, b)
    I = x[:N]
    Iin = 0.5 * (I[N // 2 - 1] + I[N // 2]) if N % 2 == 0 else I[N // 2]
    return 1.0 / Iin, zc, I


def part4_hallen():
    print("4. Hallen equation vs Galerkin MoM (ant_mom_wire.py), half-wave dipole")
    import ant_mom_wire as mw
    lam = C0 / 300e6
    for a_l in (1e-4, 1e-3):
        zg = complex(mw.dipole(300e6, lam / 2, lam * a_l, nseg=60)["Zin"][0])
        zs = {}
        for N in (51, 101, 201):
            zs[N] = hallen_dipole(0.5, a_l, N)[0]
            print(f"   a = {a_l:g} lambda, Hallen N = {N:3d} (dz/a = {0.5/N/a_l:6.1f}): Zin = {zs[N].real:7.2f} {zs[N].imag:+7.2f}j ohm")
        print(f"   a = {a_l:g} lambda, Galerkin MPIE (ant_mom_wire, 60 seg):        Zin = {zg.real:7.2f} {zg.imag:+7.2f}j ohm")
        zx = 2 * zs[201] - zs[101]                 # Richardson, observed order ~1 (pulse basis + delta gap)
        print(f"   a = {a_l:g} lambda, Hallen Richardson-extrapolated (101, 201): Zin = {zx.real:7.2f} {zx.imag:+7.2f}j ohm")
        if a_l == 1e-4:
            check("Hallen (extrapolated) vs Galerkin MPIE: R within 1 %, X within 1.5 ohm (a = 1e-4 lambda)",
                  abs(zx.real / zg.real - 1) < 0.01 and abs(zx.imag - zg.imag) < 1.5, f"{zx:.2f} vs {zg:.2f}")
            check("Hallen error halves when N doubles (first-order convergence of X)",
                  0.35 < abs(zs[201].imag - zs[101].imag) / abs(zs[101].imag - zs[51].imag) < 0.65)
            print("   (classical induced-EMF value 73.1 + j42.5 ohm assumes a sinusoidal current; the full solution"
                  " of the integral equation gives ~80 + j45 ohm for this exact half-wave length)")
    # reduced-kernel trouble: segments much shorter than the radius
    z1 = hallen_dipole(0.5, 1e-2, 25)[0]
    z2 = hallen_dipole(0.5, 1e-2, 400)[0]
    print(f"   thick wire a = lambda/100: N = 25 (dz/a = 2): {z1:.1f};  N = 400 (dz/a = 0.125): {z2:.1f}")
    check("reduced kernel misbehaves when dz << a (thick wire, fine mesh: |dZ| > 5 ohm)", abs(z2 - z1) > 5,
          f"|dZ| = {abs(z2-z1):.1f} ohm")


def part5_sommerfeld():
    print("5. Sommerfeld identity")
    k = 2 * np.pi * (1 - 0.02j)            # lossy medium, lambda = 1
    for rho, z in ((0.3, 0.2), (1.0, 0.05), (2.0, 0.5)):
        def kz(kr):
            v = np.sqrt(k * k - kr * kr + 0j)
            return np.where(v.imag > 0, -v, v)           # Im kz < 0 (decaying for e^{jwt})
        def integrand(kr):
            q = kz(kr)
            return special.j0(kr * rho) * np.exp(-1j * q * abs(z)) * kr / (1j * q)
        lim = 60.0 / max(abs(z), 0.05)
        re = integrate.quad(lambda t: integrand(t).real, 0, lim, limit=2000, points=[k.real])[0]
        im = integrate.quad(lambda t: integrand(t).imag, 0, lim, limit=2000, points=[k.real])[0]
        R = np.hypot(rho, z)
        exact = np.exp(-1j * k * R) / R
        err = abs(re + 1j * im - exact) / abs(exact)
        check(f"Sommerfeld identity rho={rho}, z={z}", err < 2e-3, f"rel. error {err:.1e}")


def part6_surface_wave():
    print("6. Grounded-slab surface waves (1.51 mm FR-4, er 4.5)")
    h, er = 1.51e-3, 4.5
    out = []
    for f in (0.433e9, 0.915e9, 2.45e9, 5.8e9, 10e9, 24e9):
        k0 = 2 * np.pi * f / C0
        def tm(b):
            kz1 = np.sqrt(er * k0 ** 2 - b ** 2)
            al = np.sqrt(b ** 2 - k0 ** 2)
            return er * al - kz1 * np.tan(kz1 * h)
        lo = max(k0, np.sqrt(max(er * k0 ** 2 - (np.pi / (2 * h)) ** 2, 0.0))) * (1 + 1e-12)
        b = optimize.brentq(tm, lo, np.sqrt(er) * k0 * (1 - 1e-12))
        out.append((f, b / k0))
        print(f"   f = {f/1e9:6.3f} GHz: TM0 beta/k0 = {b/k0:.6f}")
    check("TM0 surface-wave pole sits just above k0 at UHF (beta/k0 - 1 < 1e-3 at 915 MHz)", out[1][1] - 1 < 1e-3,
          f"{out[1][1]-1:.2e}")
    fte1 = C0 / (4 * h * np.sqrt(er - 1))
    check("TE1 onset c/(4h sqrt(er-1)) = 26 GHz (03 planar-lines value)", abs(fte1 / 1e9 - 26) < 1, f"{fte1/1e9:.1f} GHz")


if __name__ == "__main__":
    part1_scalar()
    part2_dyadic()
    part3_plate()
    part4_hallen()
    part5_sommerfeld()
    part6_surface_wave()
    print(f"\nSummary: {sum(RES)}/{len(RES)} checks passed")
