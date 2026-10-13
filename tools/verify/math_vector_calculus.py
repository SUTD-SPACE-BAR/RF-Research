#!/usr/bin/env python3
"""Verification for kb/00-math-foundations/vector-calculus-for-em.md

Symbolic (sympy) checks of vector identities, curvilinear-coordinate operators, and
EM phasor field results; numeric checks of the divergence and Stokes theorems.
Run: python3 tools/verify/math_vector_calculus.py
"""
import numpy as np
import sympy as sp
from sympy.vector import CoordSys3D, gradient, divergence, curl
from scipy import integrate

ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


def checkn(name, got, want, tol):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol})")


# ---------- Cartesian identities -----------------------------------------------
N = CoordSys3D('N')
x, y, z = N.x, N.y, N.z
f = x ** 2 * sp.sin(y) * sp.exp(z)
F = (x * y * z) * N.i + (y ** 2 * sp.cos(x)) * N.j + (sp.exp(x * z)) * N.k
check("curl(grad f) = 0", sp.simplify(curl(gradient(f)).to_matrix(N)) == sp.zeros(3, 1))
check("div(curl F) = 0", sp.simplify(divergence(curl(F))) == 0)
lap = lambda g: divergence(gradient(g))
vec_lap = lambda G: sum((lap(G.dot(e)) * e for e in (N.i, N.j, N.k)), sp.vector.Vector.zero)
lhs = curl(curl(F)).to_matrix(N)
rhs = (gradient(divergence(F)) - vec_lap(F)).to_matrix(N)
check("curl curl F = grad div F - Laplacian F (Cartesian)", sp.simplify(lhs - rhs) == sp.zeros(3, 1))

# ---------- spherical and cylindrical operators ------------------------------------
S = CoordSys3D('S', transformation='spherical', variable_names=('r', 'theta', 'phi'))
r, th, ph = S.r, S.theta, S.phi
check("Laplacian(1/r) = 0 for r != 0 (spherical)", sp.simplify(divergence(gradient(1 / r))) == 0)
check("div(r_hat / r^2) = 0 for r != 0", sp.simplify(divergence((1 / r ** 2) * S.i)) == 0)
k = sp.symbols('k', positive=True)
psi = sp.exp(-sp.I * k * r) / r
check("e^{-jkr}/r solves Helmholtz: Lap psi + k^2 psi = 0 (r != 0)", sp.simplify(divergence(gradient(psi)) + k ** 2 * psi) == 0)
Cy = CoordSys3D('C', transformation='cylindrical', variable_names=('rho', 'phi', 'z'))
rho = Cy.rho
I0 = sp.symbols('I0', positive=True)
Hwire = I0 / (2 * sp.pi * rho) * Cy.j   # phi-hat
check("wire field H = I/(2 pi rho) phi_hat: curl = 0 off axis", sp.simplify(curl(Hwire).to_matrix(Cy)) == sp.zeros(3, 1))
check("wire field: div = 0", sp.simplify(divergence(Hwire)) == 0)
circ = sp.integrate((I0 / (2 * sp.pi * rho)) * rho, (Cy.phi, 0, 2 * sp.pi))
check("Ampere: circulation of H around wire = I", sp.simplify(circ - I0) == 0)
flux = sp.integrate(sp.integrate((1 / r ** 2) * r ** 2 * sp.sin(th), (th, 0, sp.pi)), (ph, 0, 2 * sp.pi))
check("Gauss: flux of r_hat/r^2 through sphere = 4 pi", sp.simplify(flux - 4 * sp.pi) == 0)

# ---------- plane-wave phasor: curl E = -j w mu H ------------------------------------
w, mu, eps0, E0 = sp.symbols('omega mu epsilon E0', positive=True)
kk = w * sp.sqrt(mu * eps0)
E = E0 * sp.exp(-sp.I * kk * z) * N.i
H = curl(E) / (-sp.I * w * mu)
eta = sp.sqrt(mu / eps0)
check("plane wave: H = y_hat E0/eta e^{-jkz}", sp.simplify((H - (E0 / eta) * sp.exp(-sp.I * kk * z) * N.j).to_matrix(N)) == sp.zeros(3, 1))
check("plane wave: curl H = j w eps E", sp.simplify((curl(H) - sp.I * w * eps0 * E).to_matrix(N)) == sp.zeros(3, 1))
check("plane wave: div E = 0", sp.simplify(divergence(E)) == 0)

# ---------- Hertzian dipole from vector potential (spherical) ------------------------
Il = sp.symbols('Il', positive=True)
Az = mu * Il * sp.exp(-sp.I * k * r) / (4 * sp.pi * r)
A = Az * sp.cos(th) * S.i - Az * sp.sin(th) * S.j      # z_hat = cos(th) r_hat - sin(th) theta_hat
Hd = curl(A) / mu
Hphi_expected = sp.I * k * Il * sp.sin(th) / (4 * sp.pi * r) * (1 + 1 / (sp.I * k * r)) * sp.exp(-sp.I * k * r)
check("Hertzian dipole H_phi from curl A", sp.simplify(Hd.dot(S.k) - Hphi_expected) == 0)
check("Hertzian dipole H_r = H_theta = 0", sp.simplify(Hd.dot(S.i)) == 0 and sp.simplify(Hd.dot(S.j)) == 0)

# ---------- numeric divergence theorem on unit cube ---------------------------------------
Fn = lambda X, Y, Z: np.array([X ** 2 * Y, np.sin(Y) * Z, X * Z ** 2])
divF = lambda X, Y, Z: 2 * X * Y + np.cos(Y) * Z + 2 * X * Z
vol, _ = integrate.tplquad(lambda Z, Y, X: divF(X, Y, Z), 0, 1, 0, 1, 0, 1)
# outward flux through the 6 faces
fx1, _ = integrate.dblquad(lambda Z, Y: Fn(1, Y, Z)[0], 0, 1, 0, 1)
fx0, _ = integrate.dblquad(lambda Z, Y: Fn(0, Y, Z)[0], 0, 1, 0, 1)
fy1, _ = integrate.dblquad(lambda Z, X: Fn(X, 1, Z)[1], 0, 1, 0, 1)
fy0, _ = integrate.dblquad(lambda Z, X: Fn(X, 0, Z)[1], 0, 1, 0, 1)
fz1, _ = integrate.dblquad(lambda Y, X: Fn(X, Y, 1)[2], 0, 1, 0, 1)
fz0, _ = integrate.dblquad(lambda Y, X: Fn(X, Y, 0)[2], 0, 1, 0, 1)
checkn("divergence theorem on unit cube", fx1 - fx0 + fy1 - fy0 + fz1 - fz0, vol, 1e-8)

# ---------- numeric Stokes on unit disk in xy plane ---------------------------------------------
G = lambda X, Y: np.array([-Y ** 3, X ** 3, 0.0])
curlz = lambda X, Y: 3 * X ** 2 + 3 * Y ** 2
surf, _ = integrate.dblquad(lambda rr, t: curlz(rr * np.cos(t), rr * np.sin(t)) * rr, 0, 2 * np.pi, 0, 1)
line, _ = integrate.quad(lambda t: np.dot(G(np.cos(t), np.sin(t)), [-np.sin(t), np.cos(t), 0]), 0, 2 * np.pi)
checkn("Stokes theorem on unit disk", line, surf, 1e-9)
checkn("Stokes value = 3 pi / 2", line, 1.5 * np.pi, 1e-9)

# ---------- numbers used on the page ----------------------------------------------------------------
checkn("H at 1 cm from 1 A wire [A/m]", 1 / (2 * np.pi * 0.01), 15.915, 1e-3)
c = 299792458.0
checkn("k at 433 MHz [rad/m]", 2 * np.pi * 433e6 / c, 9.075, 1e-3)
checkn("kr = 1 radius at 433 MHz [m] (lambda/2pi)", c / 433e6 / (2 * np.pi), 0.1102, 1e-4)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
