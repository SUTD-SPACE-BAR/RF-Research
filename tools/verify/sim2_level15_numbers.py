#!/usr/bin/env python3
"""sim2_level15_numbers.py — checks the worked numbers of the Level 1½ (algebra-only) rungs added by W5-S11 on
kb/16-simulation-tools/em-solvers-fdtd-mom-fem.md and rf-circuit-simulators-harmonic-balance.md.

1. FDTD bookkeeping: wavelength and λ/20 cell in FR-4 at 2.45 GHz, 1-D and 3-D Courant limits for 1 mm cells,
   steps per period, cell count of a 100 x 100 x 20 mm box, and a 1-D leapfrog run whose pulse speed matches c.
2. Harmonic balance, one diode at two harmonics: source 50 mV cos(wt) through 1 kOhm into a diode
   i = Is (exp(v/Vt) - 1), Is = 5 uA, Vt = 25.85 mV. Unknowns V0, V1, V2 (5 real numbers). Solved by Newton on the
   harmonic KCL residuals, compared with a long transient (time-stepping) solution.
Run: python3 tools/verify/sim2_level15_numbers.py   (~2 s; prints PASS/FAIL)
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve

C0 = 299792458.0
ok = True


def check(name, cond, detail):
    global ok
    ok &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}: {detail}")


# ---------------------------------------------------------------- 1. FDTD bookkeeping
f, er = 2.45e9, 4.4
lam = C0 / f / np.sqrt(er) * 1e3
check("lambda in FR-4 at 2.45 GHz", abs(lam - 58.4) < 0.1, f"{lam:.1f} mm, lambda/20 = {lam/20:.2f} mm")
dx = 1e-3
dt1 = dx / C0
dt3 = dx / (C0 * np.sqrt(3))
check("Courant 1-D / 3-D for 1 mm cells", abs(dt1 * 1e12 - 3.34) < 0.01 and abs(dt3 * 1e12 - 1.93) < 0.01,
      f"{dt1*1e12:.2f} ps / {dt3*1e12:.2f} ps; steps per 2.45 GHz period (3-D) {1/f/dt3:.0f}")
n = 100 * 100 * 20
check("cells in 100 x 100 x 20 mm at 1 mm", n == 200000, f"{n} cells")
# 1-D leapfrog in vacuum: Gaussian pulse; measure speed
N, S = 2000, 0.99                       # Courant number S = c dt / dz
dz = 1e-3
dtl = S * dz / C0
E = np.zeros(N)
Hf = np.zeros(N - 1)
z = np.arange(N) * dz
E[:] = np.exp(-((z - 0.3) / 0.02) ** 2)
Hf[:] = np.exp(-((z[:-1] + dz / 2 - 0.3 + C0 * dtl / 2) / 0.02) ** 2) / 376.730     # +z-going: Hy = Ex/eta, half step earlier
steps = 800
for _ in range(steps):
    Hf -= (E[1:] - E[:-1]) * dtl / (4e-7 * np.pi * dz)          # dHy/dt = -(1/mu) dEx/dz
    E[1:-1] -= (Hf[1:] - Hf[:-1]) * dtl / (8.8541878128e-12 * dz)  # dEx/dt = -(1/eps) dHy/dz
peak = z[np.argmax(E)]
print(f"     pulse peak {E.max():.3f} (1.0 = no split) at z = {peak*1e3:.1f} mm")
v = (peak - 0.3) / (steps * dtl)
check("1-D leapfrog pulse speed", abs(v / C0 - 1) < 0.01, f"v/c = {v/C0:.4f} at Courant number {S}")

# ---------------------------------------------------------------- 2. HB, one diode, two harmonics
Is, Vt, R, A = 5e-6, 25.85e-3, 1000.0, 0.05
K, M = 2, 64
w = 2 * np.pi * 1.0                     # normalised frequency (memoryless circuit: result independent of f)
t = np.arange(M) / M


def diode_harmonics(x):
    v0, v1r, v1i, v2r, v2i = x
    vt = v0 + np.real((v1r + 1j * v1i) * np.exp(1j * 2 * np.pi * t)) + np.real((v2r + 1j * v2i) * np.exp(2j * 2 * np.pi * t))
    i = Is * (np.exp(vt / Vt) - 1)
    Ik = np.fft.fft(i) / M
    return Ik[0].real, 2 * Ik[1], 2 * Ik[2]


def residual(x):
    v0, v1r, v1i, v2r, v2i = x
    I0, I1, I2 = diode_harmonics(x)
    # KCL at the diode node, per harmonic: (Vsrc_k - V_k)/R = I_diode_k
    r0 = (0 - v0) / R - I0
    r1 = (A - (v1r + 1j * v1i)) / R - I1
    r2 = (0 - (v2r + 1j * v2i)) / R - I2
    return [r0, r1.real, r1.imag, r2.real, r2.imag]


x = fsolve(residual, [0, A / 2, 0, 0, 0], xtol=1e-13)
v0, v1, v2 = x[0], abs(x[1] + 1j * x[2]), abs(x[3] + 1j * x[4])
print(f"     HB (K = 2, 5 real unknowns): V0 = {v0*1e3:.3f} mV, |V1| = {v1*1e3:.3f} mV, |V2| = {v2*1e3:.3f} mV")


# transient reference (memoryless: solve v from (A cos - v)/R = Is(exp(v/Vt)-1) at each instant, then FFT)
def vinst(vs):
    from scipy.optimize import brentq
    return brentq(lambda v: (vs - v) / R - Is * (np.exp(v / Vt) - 1), -1, 1)


tt = np.arange(4096) / 4096
vv = np.array([vinst(A * np.cos(2 * np.pi * x_)) for x_ in tt])
Vk = np.fft.fft(vv) / tt.size
r0, r1, r2 = Vk[0].real, 2 * abs(Vk[1]), 2 * abs(Vk[2])
print(f"     exact (point-by-point + FFT): V0 = {r0*1e3:.3f} mV, |V1| = {r1*1e3:.3f} mV, |V2| = {r2*1e3:.3f} mV, "
      f"|V3| = {2*abs(Vk[3])*1e3:.3f} mV")
check("HB with only 2 harmonics vs exact", abs(v0 - r0) < 0.05e-3 and abs(v1 - r1) < 0.05e-3,
      f"V0 error {abs(v0-r0)*1e6:.1f} uV, V1 error {abs(v1-r1)*1e6:.1f} uV (truncation: V3 ignored)")
print("ALL PASS" if ok else "SOME FAIL")
