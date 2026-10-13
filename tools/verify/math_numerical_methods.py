#!/usr/bin/env python3
"""Verification for kb/00-math-foundations/numerical-methods-overview.md

Small, self-contained demonstrations of each numerical method with known answers:
root finding (bisection/Newton/brentq iteration counts); quadrature (trapezoid vs Simpson vs
Gauss-Legendre on the half-wave-dipole radiation integral); FFT == DFT and O(N log N);
ODE solvers (forward-Euler stability limit, RK4 accuracy, energy drift in an LC tank);
finite-difference derivative error order; finite-difference Laplace solve for coax
capacitance (staircase error); 1-D FDTD (Yee) with Courant number 1 and 0.5, numerical
dispersion vs theory, instability for S > 1; MoM (pulse basis, point matching) for the
capacitance of a 1 m square plate (reference 0.3667874 * 4 pi eps0 m, Read 1997); 1-D FEM (linear
elements) for Poisson vs exact.
Run: python3 tools/verify/math_numerical_methods.py   (~10 s)
"""
import time
import numpy as np
from scipy import optimize, integrate, special, sparse
from scipy.sparse.linalg import spsolve

ok_all = True


def check(name, got, want, tol):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol})")


eps0 = 8.8541878128e-12
c0 = 299792458.0

# --- root finding: Eb/N0 for BPSK BER = 1e-5 -----------------------------------------------
Q = lambda x: 0.5 * special.erfc(x / np.sqrt(2))
g = lambda e: np.log10(Q(np.sqrt(2 * 10 ** (e / 10)))) + 5      # root at ~9.59 dB
a, b, nb = 0.0, 20.0, 0
while b - a > 1e-10:
    m = 0.5 * (a + b)
    a, b = (m, b) if g(a) * g(m) > 0 else (a, m)
    nb += 1
root_bis = 0.5 * (a + b)
x, nn = 8.0, 0
for _ in range(50):
    h = 1e-6
    dx = g(x) / ((g(x + h) - g(x - h)) / (2 * h))
    x -= dx
    nn += 1
    if abs(dx) < 1e-10:
        break
root_b = optimize.brentq(g, 0, 20, xtol=1e-12)
check("bisection root [dB]", root_bis, root_b, 1e-8)
check("Newton root [dB]", x, root_b, 1e-8)
print(f"      iterations to 1e-10: bisection {nb}, Newton {nn}")
check("Newton needs far fewer iterations than bisection", float(nn < nb / 4), 1.0, 0)

# --- quadrature on the dipole integral: int_0^pi cos^2(pi/2 cos t)/sin t dt = 1.21883 ------------
f = lambda t: np.cos(np.pi / 2 * np.cos(t)) ** 2 / np.sin(t)
ref, _ = integrate.quad(f, 0, np.pi, epsabs=1e-13, epsrel=1e-13, limit=200)
check("dipole integral reference (Cin(2pi)/2)", ref, 0.5 * (np.euler_gamma + np.log(2 * np.pi) - special.sici(2 * np.pi)[1]), 1e-10)
errs = {}
for N in [8, 32]:
    tt = np.linspace(1e-12, np.pi - 1e-12, N + 1)
    errs[("trap", N)] = abs(np.trapezoid(f(tt), tt) - ref)
    errs[("simp", N)] = abs(integrate.simpson(f(tt), x=tt) - ref)
    xg, wg = np.polynomial.legendre.leggauss(N)
    errs[("gauss", N)] = abs(np.sum(wg * f(np.pi / 2 * (xg + 1))) * np.pi / 2 - ref)
for k, v in errs.items():
    print(f"      {k[0]:5s} N={k[1]:3d}: error {v:.2e}")
check("Gauss-Legendre 32 pts error < 1e-12", float(errs[("gauss", 32)] < 1e-12), 1.0, 0)
check("dipole directivity from quadrature", 2 / ref, 1.6409, 1e-4)

# --- FFT vs DFT ---------------------------------------------------------------------------------
N = 1024
xr = np.random.default_rng(0).standard_normal(N)
n = np.arange(N)
Wm = np.exp(-2j * np.pi * np.outer(n, n) / N)
check("FFT == DFT matrix product", np.max(abs(Wm @ xr - np.fft.fft(xr))), 0, 1e-9)
t0 = time.perf_counter(); [Wm @ xr for _ in range(20)]; tdft = time.perf_counter() - t0
t0 = time.perf_counter(); [np.fft.fft(xr) for _ in range(20)]; tfft = time.perf_counter() - t0
print(f"      N=1024: DFT matmul {tdft/20*1e3:.3f} ms, FFT {tfft/20*1e3:.4f} ms")

# --- ODE solvers ----------------------------------------------------------------------------------
tau = 1e-6
for dt, stable in [(1.9e-6, True), (2.1e-6, False)]:
    y = 1.0
    for _ in range(200):
        y = y + dt * (-y / tau)
    check(f"forward Euler on RC, dt={dt/tau:.1f} tau: bounded={stable}", float(abs(y) < 1), float(stable), 0)
# RK4 accuracy on RC step
def rk4(fun, y, t, dt):
    k1 = fun(t, y); k2 = fun(t + dt / 2, y + dt / 2 * k1); k3 = fun(t + dt / 2, y + dt / 2 * k2); k4 = fun(t + dt, y + dt * k3)
    return y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
fun = lambda t, y: (1 - y) / tau
y, dt = 0.0, tau / 10
for i in range(50):
    y = rk4(fun, y, i * dt, dt)
check("RK4 (dt = tau/10) RC step at 5 tau", y, 1 - np.exp(-5), 1e-6)
# LC tank energy: explicit Euler grows, symplectic Euler bounded
L, C = 10e-9, 13.5e-12
w0 = 1 / np.sqrt(L * C)
dt = 0.02 / w0
v, i = 1.0, 0.0
for _ in range(5000):
    v, i = v + dt * (-i / C), i + dt * (v / L)
E_euler = 0.5 * C * v ** 2 + 0.5 * L * i ** 2
v, i = 1.0, 0.0
for _ in range(5000):
    i = i + dt * (v / L)
    v = v + dt * (-i / C)
E_symp = 0.5 * C * v ** 2 + 0.5 * L * i ** 2
E0 = 0.5 * C
check("explicit Euler LC energy grows (E/E0 > 2 after 5000 steps)", float(E_euler / E0 > 2), 1.0, 0)
check("symplectic Euler LC energy bounded (within 2%)", E_symp / E0, 1.0, 0.02)

# --- finite-difference derivative order ---------------------------------------------------------------
fx = np.sin
e1 = abs((fx(1 + 1e-2) - fx(1 - 1e-2)) / 2e-2 - np.cos(1))
e2 = abs((fx(1 + 5e-3) - fx(1 - 5e-3)) / 1e-2 - np.cos(1))
check("central difference error ratio for h/2 ~ 4 (2nd order)", e1 / e2, 4.0, 0.01)

# --- FD Laplace: coax capacitance per metre (b/a = 2.3, air) -------------------------------------------
def coax_fd(M):
    b = 1.0
    a_ = b / 2.3
    xs = np.linspace(-b, b, M)
    h = xs[1] - xs[0]
    X, Yg = np.meshgrid(xs, xs)
    Rg = np.hypot(X, Yg)
    inner = Rg <= a_
    outer = Rg >= b
    unknown = ~(inner | outer)
    idx = -np.ones(X.shape, dtype=int)
    idx[unknown] = np.arange(unknown.sum())
    rows, cols, vals, rhs = [], [], [], np.zeros(unknown.sum())
    for (r, cc) in zip(*np.nonzero(unknown)):
        k = idx[r, cc]
        rows.append(k); cols.append(k); vals.append(-4.0)
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, c2 = r + dr, cc + dc
            if unknown[rr, c2]:
                rows.append(k); cols.append(idx[rr, c2]); vals.append(1.0)
            elif inner[rr, c2]:
                rhs[k] -= 1.0          # inner conductor at 1 V
    A = sparse.csr_matrix((vals, (rows, cols)), shape=(unknown.sum(),) * 2)
    Vsol = spsolve(A, rhs)
    V = np.zeros(X.shape); V[inner] = 1.0; V[unknown] = Vsol
    gy, gx = np.gradient(V, h)
    W = 0.5 * eps0 * np.sum(gx ** 2 + gy ** 2) * h * h       # energy per metre for 1 V
    return 2 * W                                             # C' = 2W/V^2
Cexact = 2 * np.pi * eps0 / np.log(2.3)
C81, C161 = coax_fd(81), coax_fd(161)
print(f"      coax C': exact {Cexact*1e12:.2f} pF/m; FD 81x81 {C81*1e12:.2f}; 161x161 {C161*1e12:.2f}")
check("FD Laplace coax C' within 5% on 161x161 grid", abs(C161 / Cexact - 1), 0, 0.05)

# --- 1-D FDTD (Yee) ------------------------------------------------------------------------------------
def fdtd1d(S, Nz=4000, steps=3000, ppw=20, z1=400, z2=600):
    dz = 1.0 / ppw                         # wavelength = 1 m -> ppw cells per wavelength
    dt = S * dz / c0
    Ez = np.zeros(Nz); Hy = np.zeros(Nz - 1)
    mu0 = 4e-7 * np.pi
    f0 = c0 / 1.0
    src = 100
    acc = np.zeros(z2 - z1 + 1, dtype=complex)   # running DFT at f0 over the second half
    for nstep in range(steps):
        Hy += dt / (mu0 * dz) * (Ez[1:] - Ez[:-1])
        Ez[1:-1] += dt / (eps0 * dz) * (Hy[1:] - Hy[:-1])
        Ez[src] += np.sin(2 * np.pi * f0 * nstep * dt) * (1 - np.exp(-(nstep / 60) ** 2))
        if nstep >= steps // 2:
            acc += Ez[z1:z2 + 1] * np.exp(-2j * np.pi * f0 * nstep * dt)
        if not np.isfinite(Ez).all() or np.max(abs(Ez)) > 1e6:
            return None, dz, dt, Ez
    ph = np.unwrap(np.angle(acc))
    k_num = -np.polyfit(np.arange(z1, z2 + 1) * dz, ph, 1)[0]
    return 2 * np.pi * f0 / k_num, dz, dt, Ez
for S in [1.0, 0.5]:
    vp_num, dz, dt, _ = fdtd1d(S)
    f0 = c0
    k_th = 2 / dz * np.arcsin(dz / (c0 * dt) * np.sin(2 * np.pi * f0 * dt / 2))
    check(f"FDTD S={S}: numerical vp/c matches dispersion relation", vp_num / c0, 2 * np.pi * f0 / k_th / c0, 5e-4)
    if S == 1.0:
        check("FDTD S=1 (magic time step): vp = c", vp_num / c0, 1.0, 5e-4)
    else:
        print(f"      FDTD S=0.5, 20 cells/lambda: vp/c = {vp_num/c0:.5f} (theory {2*np.pi*f0/k_th/c0:.5f})")
vp_bad, _, _, Ebad = fdtd1d(1.05, steps=2000)
check("FDTD S=1.05 unstable (field blows up)", float(vp_bad is None), 1.0, 0)

# --- MoM: capacitance of a 1 m square plate ------------------------------------------------------------
def plate_cap(Nd, side=1.0):
    hcell = side / Nd
    cx = (np.arange(Nd) + 0.5) * hcell
    X, Yg = np.meshgrid(cx, cx)
    P = np.column_stack([X.ravel(), Yg.ravel()])
    D = np.hypot(P[:, None, 0] - P[None, :, 0], P[:, None, 1] - P[None, :, 1])
    np.fill_diagonal(D, 1.0)
    Zm = hcell ** 2 / (4 * np.pi * eps0 * D)                 # potential at i from unit sigma on cell j
    np.fill_diagonal(Zm, hcell * np.log(1 + np.sqrt(2)) / (np.pi * eps0))   # exact self term
    sigma = np.linalg.solve(Zm, np.ones(len(P)))             # plate at 1 V
    return np.sum(sigma) * hcell ** 2
Cref = 0.3667874 * 4 * np.pi * eps0          # Read (1997), J. Comput. Phys. 133:1-5
c20, c40 = plate_cap(20), plate_cap(40)
print(f"      square plate: ref {Cref*1e12:.2f} pF; MoM 20x20 {c20*1e12:.2f}; 40x40 {c40*1e12:.2f}")
check("MoM square plate 40x40 within 1% of reference", abs(c40 / Cref - 1), 0, 0.01)
check("MoM converges (40x40 closer than 20x20)", float(abs(c40 - Cref) < abs(c20 - Cref)), 1.0, 0)

# --- 1-D FEM: -u'' = 1 on (0,1), u(0)=u(1)=0; exact u = x(1-x)/2 ----------------------------------------
Ne = 16
xe = np.linspace(0, 1, Ne + 1)
he = np.diff(xe)
K = np.zeros((Ne + 1, Ne + 1)); F = np.zeros(Ne + 1)
for e in range(Ne):
    K[e:e + 2, e:e + 2] += np.array([[1, -1], [-1, 1]]) / he[e]
    F[e:e + 2] += he[e] / 2
u = np.zeros(Ne + 1)
u[1:-1] = np.linalg.solve(K[1:-1, 1:-1], F[1:-1])
check("1-D FEM (linear elements) nodal values exact for this problem", np.max(abs(u - xe * (1 - xe) / 2)), 0, 1e-12)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
