#!/usr/bin/env python3
"""sim_harmonic_balance.py — a minimal harmonic-balance (HB) solver vs brute-force transient simulation,
for kb/16-simulation-tools/rf-circuit-simulators-harmonic-balance.md.

Circuit (a transconductance frequency tripler, own example):
    an ideal cubic transconductor driven by vin = A cos(w t) injects i_inj = gm3 vin^3 into an output node
    loaded by a parallel tank (L, C tuned to 3w, unloaded Q = 50 via Rp) and by a compressive output
    nonlinearity i_o = go3 v^3 (which makes the problem nonlinear in the unknown node voltage).
KCL at the output node:  C dv/dt + v/Rp + i_L + go3 v^3 = gm3 vin(t)^3,   L di_L/dt = v.
(vin^3 = A^3 [3/4 cos wt + 1/4 cos 3wt]: the tank picks out the 3rd harmonic.)

HB: v(t) = sum_k V_k e^{jk w t}. The linear part is solved per harmonic (admittance Y(k w)), the nonlinear
current is evaluated in the time domain on N samples and transformed back with an FFT; Newton-type root
finding (scipy.optimize.root) drives the harmonic KCL residual to zero.
Transient: scipy solve_ivp (Radau, tight tolerances) for enough drive cycles to reach steady state, then an
FFT over an integer number of cycles.

Pre-registered expectation: harmonic amplitudes |V1|, |V3|, |V5| from HB and from the settled transient agree
within 0.5 %; HB needs one nonlinear solve, the transient must integrate > 5 tank time constants
(2 Q / w0 each) before the waveform is periodic.
Run: python3 tools/verify/sim_harmonic_balance.py   (~1 min; the transient part dominates)
"""
import math
import time

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import root

f0 = 100e6                  # drive frequency
w = 2 * math.pi * f0
A = 1.0                     # drive amplitude [V]
L = 10e-9
C = 1 / ((3 * w) ** 2 * L)  # tank at 300 MHz (28.1 pF)
Q = 50.0
Rp = Q * 3 * w * L          # parallel loss for Q = 50 (942 ohm)
gm3 = 0.02                  # cubic transconductance [A/V^3] -> 5 mA injected at 3w
go3 = 2e-4                  # compressive output nonlinearity [A/V^3]
K = 15                      # highest harmonic kept
N = 128                     # time samples per period for the nonlinear evaluation

ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


# ------------------------------------------------------------------ harmonic balance
def y_lin(k):
    """Admittance of the tank (C, L, Rp) at harmonic k (k >= 1)."""
    s = 1j * k * w
    return s * C + 1 / (s * L) + 1 / Rp


def hb_residual(x):
    Vk = x[:K] + 1j * x[K:]                       # V_1..V_K (V_0 = 0: the inductor shorts DC)
    spec = np.zeros(N // 2 + 1, dtype=complex)
    spec[1:K + 1] = Vk * N / 2                    # one-sided spectrum -> real time signal via irfft
    v = np.fft.irfft(spec, N)
    inl = go3 * v ** 3
    Ik = np.fft.rfft(inl)[1:K + 1] * 2 / N        # phasor amplitudes of the nonlinear current
    Isrc = np.zeros(K, dtype=complex)
    Isrc[0] = 0.75 * gm3 * A ** 3                 # injected current phasors (cos -> real)
    Isrc[2] = 0.25 * gm3 * A ** 3
    r = np.array([y_lin(k) for k in range(1, K + 1)]) * Vk + Ik - Isrc
    return np.concatenate([r.real, r.imag])


def solve_hb():
    x0 = np.zeros(2 * K)
    lin = np.array([0.75, 0, 0.25]) * gm3 * A ** 3 / np.array([y_lin(1), 1, y_lin(3)])
    x0[0], x0[2] = lin[0].real, lin[2].real       # linear (go3 = 0) first guess
    x0[K], x0[K + 2] = lin[0].imag, lin[2].imag
    t0 = time.perf_counter()
    sol = root(hb_residual, x0, method="hybr", tol=1e-13)
    dt = time.perf_counter() - t0
    Vk = sol.x[:K] + 1j * sol.x[K:]
    return Vk, sol, dt


# ------------------------------------------------------------------ transient
def solve_transient(ncyc=80, nlast=20):
    def rhs(t, y):
        v, iL = y
        vin = A * math.cos(w * t)
        dv = (gm3 * vin ** 3 - v / Rp - iL - go3 * v ** 3) / C
        return [dv, v / L]
    T = 1 / f0
    t_eval = np.linspace((ncyc - nlast) * T, ncyc * T, nlast * N, endpoint=False)
    t0 = time.perf_counter()
    r = solve_ivp(rhs, (0, ncyc * T), [0.0, 0.0], method="Radau", t_eval=t_eval, rtol=1e-10, atol=1e-13,
                  max_step=T / 200)
    dt = time.perf_counter() - t0
    v = r.y[0]
    spec = np.fft.rfft(v) * 2 / len(v)
    Vk = np.array([spec[k * nlast] for k in range(1, K + 1)])
    return Vk, dt, r


def main():
    tau = 2 * Q / (3 * w)
    print(f"Tripler: drive {f0/1e6:.0f} MHz, tank {3*f0/1e6:.0f} MHz (L {L*1e9:.1f} nH, C {C*1e12:.2f} pF, "
          f"Rp {Rp:.0f} ohm, Q {Q:.0f}); amplitude time constant 2Q/w0 = {tau*1e9:.1f} ns = {tau*f0:.1f} drive cycles")
    print(f"   linear (go3 = 0) estimate |V3| = gm3 A^3/4 * Rp = {0.25*gm3*A**3*Rp:.3f} V")
    Vhb, sol, t_hb = solve_hb()
    print(f"HB: K = {K} harmonics, N = {N} samples, converged = {sol.success}, residual "
          f"{np.max(abs(hb_residual(sol.x))):.1e} A, {sol.nfev} residual evaluations, {t_hb*1e3:.1f} ms")
    Vtr, t_tr, _ = solve_transient()
    print(f"Transient: 80 drive cycles (FFT of the last 20), Radau rtol 1e-10, {t_tr:.1f} s")
    worst = 0.0
    for k in (1, 3, 5, 7):
        a, b = abs(Vhb[k - 1]), abs(Vtr[k - 1])
        err = abs(a - b) / b
        if k <= 5:
            worst = max(worst, err)
        print(f"   |V{k}|: HB {a*1e3:9.4f} mV   transient {b*1e3:9.4f} mV   ({100*err:+.4f} %)")
    check("HB and settled transient agree within 0.5 % for V1, V3, V5", worst < 5e-3, f"(worst {100*worst:.4f} %)")
    # how long must the transient run? error of V3 vs number of cycles
    print("   transient V3 error vs simulated length (FFT of the last 10 cycles):")
    for ncyc in (15, 20, 30, 40, 60):
        Vt, _, _ = solve_transient(ncyc, 10)
        print(f"     {ncyc:3d} cycles: |V3| error {100*abs(abs(Vt[2]) - abs(Vhb[2]))/abs(Vhb[2]):7.3f} %")
    print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")


if __name__ == "__main__":
    main()
