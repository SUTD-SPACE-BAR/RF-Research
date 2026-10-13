#!/usr/bin/env python3
"""
ant_small_limits.py -- checks for kb/08-antennas/small-antenna-limits.md and loop-antennas.md

1. Radiation Q of the TM01 (electric-dipole) spherical mode outside a sphere of radius a,
   computed by numerically integrating the non-propagating stored energy
   (Collin & Rothschild 1964 / McLean 1996 method), compared with
       McLean:  Q = 1/(ka)^3 + 1/(ka)
       Hansen's form of Chu's result: Q = (1 + 3(ka)^2) / ((ka)^3 (1 + (ka)^2))
   and the energy stored in Chu's TM1 equivalent circuit (series C = eps a, shunt L = mu a, R = eta).
2. Circularly polarised (TE01 + TM01) bound  Q = 1/2 [1/(ka)^3 + 2/(ka)].
3. Q -> matched fractional bandwidth:  FBW(VSWR <= s) = (s - 1)/(Q sqrt(s))  (Yaghjian & Best 2005),
   and the efficiency-bandwidth trade (Q_total = eta_rad Q_rad for a lossy antenna).
4. Worked limits for the reader's bands (433, 868/915 MHz, 1575 MHz, 2.45 GHz).
5. Small loops: Rr = 20 pi^2 (C/lambda)^4 = 31171 (N A / lambda^2)^2, skin-effect loss, efficiency;
   ferrite-rod loop Rr scaling with mu_eff^2.

Run: python3 tools/verify/ant_small_limits.py
"""
import numpy as np
from scipy.special import spherical_jn, spherical_yn
from scipy.integrate import quad

C0 = 299792458.0
MU0 = 4e-7 * np.pi
EPS0 = 1 / (MU0 * C0 ** 2)
ETA0 = np.sqrt(MU0 / EPS0)


def h1(x):
    return spherical_jn(1, x) - 1j * spherical_yn(1, x)   # outgoing for exp(+j w t)


def dxh1(x):
    # d/dx [x h1(x)] = h1 + x h1'
    hp = spherical_jn(1, x, derivative=True) - 1j * spherical_yn(1, x, derivative=True)
    return h1(x) + x * hp


def q_tm01_energy(ka):
    """Q from stored (non-propagating) energy of H_phi = h1(kr) sin(theta), r > a. Units: set k = 1,
    omega = 1, so eps = 1/eta, mu = eta (with c = 1). All overall constants cancel in Q."""
    eta = 1.0
    eps, mu, w = 1 / eta, eta, 1.0
    # per unit dr (x = kr = r): angular integrals  int cos^2 = 4pi/3, int sin^2 = 8pi/3
    def We(r):
        Er2 = (4 / (w ** 2 * eps ** 2 * r ** 2)) * abs(h1(r)) ** 2 * (4 * np.pi / 3)
        Et2 = (1 / (w ** 2 * eps ** 2 * r ** 2)) * abs(dxh1(r)) ** 2 * (8 * np.pi / 3)
        return eps / 4 * (Er2 + Et2) * r ** 2
    def Wm(r):
        return mu / 4 * abs(h1(r)) ** 2 * (8 * np.pi / 3) * r ** 2
    r0 = 50.0
    P = 0.5 * np.real((-1 / (1j * w * eps * r0)) * dxh1(r0) * np.conj(h1(r0))) * r0 ** 2 * (8 * np.pi / 3)
    wrad = P / 2   # propagating energy per unit radius, per field type (c = 1)
    Ie, _ = quad(lambda r: We(r) - wrad, ka, np.inf, limit=500)
    Im, _ = quad(lambda r: Wm(r) - wrad, ka, np.inf, limit=500)
    return 2 * w * max(Ie, Im) / P, 2 * w * Ie / P, 2 * w * Im / P


def q_mclean(ka):
    return 1 / ka ** 3 + 1 / ka


def q_hansen_chu(ka):
    return (1 + 3 * ka ** 2) / (ka ** 3 * (1 + ka ** 2))


def q_circuit(ka):
    # series C = eps a, shunt L = mu a, load eta. Normalise V=1 across (L || R), R = 1.
    Ic2 = 1 + 1 / ka ** 2
    wWe = Ic2 * (1 / ka) / 4          # (1/(wC)) |Ic|^2 / 4 with 1/(wC R) = 1/ka
    wWm = (1 / ka) / 4                # wL |IL|^2 / 4 with wL/R = ka, |IL|^2 = 1/ka^2
    P = 0.5
    return 2 * max(wWe, wWm) / P


def q_cp(ka):
    return 0.5 * (1 / ka ** 3 + 2 / ka)


def fbw(Q, s=2.0):
    return (s - 1) / (Q * np.sqrt(s))


def main():
    print("=== 1. TM01 radiation Q: numeric stored-energy integral vs formulas ===")
    print(f"{'ka':>6s} {'numeric':>10s} {'McLean':>10s} {'Hansen/Chu':>11s} {'circuit':>10s} {'CP bound':>9s}")
    for ka in [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]:
        qn, qe, qm = q_tm01_energy(ka)
        print(f"{ka:6.2f} {qn:10.3f} {q_mclean(ka):10.3f} {q_hansen_chu(ka):11.3f} {q_circuit(ka):10.3f} {q_cp(ka):9.3f}")

    print("\n=== 3/4. Bandwidth limits for small antennas in the reader's bands ===")
    print("(a = radius of the smallest sphere enclosing the antenna AND the currents on its ground plane)")
    rows = [
        ("433 MHz, a = 20 mm (stubby/chip + tiny board)", 433.9e6, 0.020, 1.74e6),
        ("433 MHz, a = 50 mm", 433.9e6, 0.050, 1.74e6),
        ("433 MHz, a = 86 mm (~ lambda/8)", 433.9e6, 0.086, 1.74e6),
        ("868 MHz, a = 15 mm", 868.3e6, 0.015, 7.0e6),
        ("915 MHz, a = 15 mm", 915e6, 0.015, 26e6),
        ("915 MHz, a = 30 mm", 915e6, 0.030, 26e6),
        ("1575.42 MHz, a = 10 mm", 1575.42e6, 0.010, 2.046e6),
        ("2.45 GHz, a = 6 mm", 2.44e9, 0.006, 83.5e6),
    ]
    for (name, f, a, need) in rows:
        ka = 2 * np.pi * f / C0 * a
        Q = q_mclean(ka)
        bw = fbw(Q) * f
        eta_max_needed = min(1.0, bw / need)
        print(f"  {name:48s} ka = {ka:5.3f}  Qmin = {Q:8.1f}  max VSWR-2 BW at 100% eff = {bw/1e6:7.2f} MHz "
              f"(band needs {need/1e6:.2f} MHz -> needs eta <= {eta_max_needed*100:5.1f}% if limit-bound)")
    print("  Note: real antennas sit well above the bound (Q typically 1.5-3x Chu-McLean for wire/planar shapes).")

    print("\n=== 5. Small loop antennas ===")
    def loop(f, D, d_wire, N=1, sigma=5.8e7):
        lam = C0 / f
        A = np.pi * (D / 2) ** 2
        Rr = 31171 * (N * A / lam ** 2) ** 2      # = 20 pi^2 (C/lambda)^4 N^2
        Rs = np.sqrt(np.pi * f * MU0 / sigma)
        Rl = N * (np.pi * D) / (np.pi * d_wire) * Rs   # skin-effect, no proximity effect
        eff = Rr / (Rr + Rl)
        L = N ** 2 * MU0 * (D / 2) * (np.log(8 * D / d_wire) - 2)
        X = 2 * np.pi * f * L
        Q = X / (Rr + Rl)
        return Rr, Rl, eff, L, Q
    for (name, f, D, dw, N) in [("433 MHz, 30 mm dia, 1 mm wire", 433e6, 0.030, 1e-3, 1),
                                ("433 MHz, 80 mm dia, 6 mm tube", 433e6, 0.080, 6e-3, 1),
                                ("14.2 MHz magnetic loop, 1.0 m dia, 22 mm tube", 14.2e6, 1.0, 22e-3, 1),
                                ("7.1 MHz magnetic loop, 1.0 m dia, 22 mm tube", 7.1e6, 1.0, 22e-3, 1)]:
        Rr, Rl, eff, L, Q = loop(f, D, dw, N)
        print(f"  {name:48s} Rr = {Rr:.4g} ohm, Rloss = {Rl:.4g} ohm, eff = {eff*100:5.1f}% ({10*np.log10(eff):.1f} dB), "
              f"L = {L*1e9:.0f} nH, Q = {Q:.0f}, BW(3dB) = {f/Q/1e3:.1f} kHz")
    # check Rr formula equivalence
    C_l = 0.1
    print(f"  identity check: 20 pi^2 (C/lam)^4 = {20*np.pi**2*C_l**4:.6e}, "
          f"31171 (A/lam^2)^2 = {31171*(np.pi*(C_l/(2*np.pi))**2)**2:.6e}")
    # ferrite rod (receive): 1 MHz, 10 mm x 100 mm rod, mu_eff ~ 100 (rod demagnetisation-limited), 50 turns
    f, N, dr, mue = 1e6, 50, 10e-3, 100
    lam = C0 / f
    A = np.pi * (dr / 2) ** 2
    Rr = 31171 * (N * mue * A / lam ** 2) ** 2
    print(f"  ferrite rod 1 MHz, 10 mm dia, 50 turns, mu_eff = {mue}: Rr = {Rr:.3g} ohm (receive-only; external noise dominates at MF)")


if __name__ == "__main__":
    main()
