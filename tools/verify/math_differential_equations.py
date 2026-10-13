#!/usr/bin/env python3
"""Verification for kb/00-math-foundations/differential-equations-circuits-waves.md

Checks: RC step response; energy lost charging a capacitor through any R = CV^2/2;
series RLC zeta/Q/wd from ODE simulation (ringing frequency and decay); critical damping
R = 2 sqrt(L/C); decoupling-cap resonance example; driven steady state matches phasor;
1-D wave equation: d'Alembert travelling pulse speed from finite-difference solution;
string/line standing-wave mode frequencies; telegrapher velocity 1/sqrt(L'C');
separation of variables in a rectangular waveguide (TE10 cutoff); low-loss line attenuation
alpha = R'/(2 Z0) + G' Z0/2 vs exact.
Run: python3 tools/verify/math_differential_equations.py
"""
import numpy as np
from scipy.integrate import solve_ivp

ok_all = True


def check(name, got, want, tol):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol})")


# --- RC step ---------------------------------------------------------------------------
R, C, V = 1e3, 1e-6, 3.3
sol = solve_ivp(lambda t, v: [(V - v[0]) / (R * C)], [0, 5e-3], [0.0], dense_output=True, rtol=1e-10, atol=1e-12)
check("RC: v(tau) = V(1 - 1/e)", sol.sol(R * C)[0], V * (1 - np.exp(-1)), 1e-6)
# energy dissipated in R while charging: integral i^2 R dt
for Rx in [1.0, 1e3, 1e6]:
    tau = Rx * C
    t = np.linspace(0, 40 * tau, 400001)
    i = V / Rx * np.exp(-t / tau)
    E_R = np.trapezoid(i ** 2 * Rx, t)
    check(f"energy lost charging C through R={Rx:g} ohm = CV^2/2", E_R, 0.5 * C * V ** 2, 1e-4 * 0.5 * C * V ** 2)

# --- series RLC natural response --------------------------------------------------------------
L, C = 1e-6, 1e-9
w0 = 1 / np.sqrt(L * C)
for zeta_target in [0.05, 0.3]:
    R = 2 * zeta_target * np.sqrt(L / C)
    def rhs(t, y):
        q, i = y
        return [i, (-R * i - q / C) / L]
    T0 = 2 * np.pi / w0
    t = np.linspace(0, 30 * T0, 300001)
    s = solve_ivp(rhs, [0, t[-1]], [C * 1.0, 0.0], t_eval=t, rtol=1e-10, atol=1e-18, max_step=T0 / 100)
    vC = s.y[0] / C
    # zero crossings -> ringing frequency
    zc = t[np.where(np.diff(np.sign(vC)) != 0)[0]]
    wd_meas = np.pi / np.mean(np.diff(zc[:10]))
    check(f"RLC zeta={zeta_target}: ringing freq wd = w0 sqrt(1-zeta^2)", wd_meas / w0, np.sqrt(1 - zeta_target ** 2), 2e-3)
    # envelope decay: fit ln |peaks|
    from scipy.signal import find_peaks
    pk, _ = find_peaks(vC)
    alpha_meas = -np.polyfit(t[pk[:8]], np.log(vC[pk[:8]]), 1)[0]
    check(f"RLC zeta={zeta_target}: decay rate alpha = R/(2L)", alpha_meas, R / (2 * L), 1e-3 * R / (2 * L))
    check(f"RLC zeta={zeta_target}: Q = (1/R) sqrt(L/C) = 1/(2 zeta)", (1 / R) * np.sqrt(L / C), 1 / (2 * zeta_target), 1e-9)
check("critical damping R = 2 sqrt(L/C) [ohm]", 2 * np.sqrt(L / C), 63.2456, 1e-3)

# --- decoupling capacitor resonance example ----------------------------------------------------
Lp, Cd, ESR = 5e-9, 100e-9, 0.01
check("5 nH + 100 nF resonance [MHz]", 1 / (2 * np.pi * np.sqrt(Lp * Cd)) / 1e6, 7.118, 1e-3)
check("its Q = sqrt(L/C)/ESR", np.sqrt(Lp / Cd) / ESR, 22.36, 0.01)

# --- driven RLC steady state vs phasor (amplitude) --------------------------------------------------
R = 20.0
w = 0.8 * w0
def rhs(t, y):
    q, i = y
    return [i, (np.cos(w * t) - R * i - q / C) / L]
Tw = 2 * np.pi / w
t_end = 60 * 2 * L / R
t = np.linspace(t_end - 3 * Tw, t_end, 3001)
s = solve_ivp(rhs, [0, t_end], [0, 0], t_eval=t, rtol=1e-10, atol=1e-18, max_step=Tw / 100)
amp = (s.y[1].max() - s.y[1].min()) / 2
Z = R + 1j * (w * L - 1 / (w * C))
check("driven RLC: steady-state current amplitude = 1/|Z|", amp, 1 / abs(Z), 1e-4 / abs(Z) * 10)

# --- 1-D wave equation: finite-difference, pulse speed ------------------------------------------------
v = 2.0e8            # m/s (coax with eps_r = 2.25)
Lx = 10.0
Nx = 4001
dx = Lx / (Nx - 1)
dt = dx / v          # Courant number 1 -> exact for 1-D
x = np.linspace(0, Lx, Nx)
u0 = np.exp(-((x - 2.0) / 0.1) ** 2)
u_prev = u0.copy()
u = np.roll(u0, 1)   # pulse moving +x: u(x, dt) = u0(x - v dt)
u[0] = 0
steps = int(round(5.0 / (v * dt)))   # travel 5 m
for _ in range(steps - 1):
    u_next = np.zeros_like(u)
    u_next[1:-1] = 2 * u[1:-1] - u_prev[1:-1] + (v * dt / dx) ** 2 * (u[2:] - 2 * u[1:-1] + u[:-2])
    u_prev, u = u, u_next
check("wave eq. FD: pulse centre after 25 ns at 2e8 m/s [m]", x[np.argmax(u)], 7.0, 2 * dx)
check("wave eq. FD: pulse shape preserved (peak)", u.max(), 1.0, 1e-6)

# --- standing waves / modes -------------------------------------------------------------------------------
c = 299792458.0
check("open-open line / string mode n=1: f = v/(2L) for 0.5 m at vf 0.66 [MHz]", 0.66 * c / (2 * 0.5) / 1e6, 197.86, 0.01)
check("quarter-wave at 433 MHz in coax vf 0.66 [mm]", 0.66 * c / 433e6 / 4 * 1e3, 114.24, 0.01)

# --- telegrapher velocity -----------------------------------------------------------------------------------
Lp_, Cp_ = 258.5e-9, 96.84e-12
check("telegrapher v = 1/sqrt(L'C') / c", 1 / np.sqrt(Lp_ * Cp_) / c, 1 / 1.5, 1e-3)

# --- waveguide by separation of variables: kc = sqrt((m pi/a)^2 + (n pi/b)^2) ---------------------------------
a, b = 22.86e-3, 10.16e-3
fc = lambda m, n: c / (2 * np.pi) * np.sqrt((m * np.pi / a) ** 2 + (n * np.pi / b) ** 2)
check("WR-90 TE10 cutoff [GHz]", fc(1, 0) / 1e9, 6.557, 1e-3)
check("WR-90 TE20 cutoff [GHz]", fc(2, 0) / 1e9, 13.114, 1e-3)
check("WR-90 TE01 cutoff [GHz]", fc(0, 1) / 1e9, 14.753, 1e-3)

# --- low-loss line attenuation -------------------------------------------------------------------------------
Rp, Gp = 0.5, 1e-5          # ohm/m, S/m
w = 2 * np.pi * 433e6
gamma = np.sqrt((Rp + 1j * w * Lp_) * (Gp + 1j * w * Cp_))
Z0 = np.sqrt(Lp_ / Cp_)
check("low-loss alpha = R'/(2Z0) + G'Z0/2 vs exact [Np/m]", gamma.real, Rp / (2 * Z0) + Gp * Z0 / 2, 1e-3 * gamma.real)

# --- skin depth from the diffusion equation -------------------------------------------------------------------
mu0 = 4e-7 * np.pi
sigma_cu = 5.8e7
check("copper skin depth at 433 MHz [um]", np.sqrt(2 / (2 * np.pi * 433e6 * mu0 * sigma_cu)) * 1e6, 3.18, 0.01)
check("critical damping for 5 nH / 100 nF [ohm]", 2 * np.sqrt(5e-9 / 100e-9), 0.447, 1e-3)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
