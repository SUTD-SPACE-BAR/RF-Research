#!/usr/bin/env python3
"""Verification of numbers used in kb/00-math-foundations/decibels-and-log-units.md

Run: python3 tools/verify/math_decibels.py   -> prints each check and PASS/FAIL.
Every constant here is computed from first principles (SI values of k, c, eta0),
not copied from a table.
"""
import numpy as np
from scipy import integrate, constants as C

ok_all = True


def check(name, got, want, tol):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol})")


def dbm_to_w(p_dbm):
    return 1e-3 * 10 ** (p_dbm / 10)


def w_to_dbm(p_w):
    return 10 * np.log10(p_w / 1e-3)


R = 50.0
# --- dBm <-> voltage at 50 ohm ---------------------------------------------
vrms0 = np.sqrt(dbm_to_w(0) * R)
check("0 dBm Vrms @50ohm [V]", vrms0, 0.2236, 1e-4)
check("0 dBm Vpk  @50ohm [V]", vrms0 * np.sqrt(2), 0.3162, 1e-4)
check("0 dBm Vpp  @50ohm [V]", 2 * vrms0 * np.sqrt(2), 0.6325, 1e-4)
check("1 Vrms @50ohm in dBm", w_to_dbm(1.0 ** 2 / R), 13.01, 0.01)
check("0 dBm in dBuV @50ohm", 20 * np.log10(vrms0 / 1e-6), 106.99, 0.01)
check("0 dBm in dBmV @75ohm", 20 * np.log10(np.sqrt(1e-3 * 75) / 1e-3), 48.75, 0.01)
check("0 dBu reference 0.7746 V (1 mW in 600 ohm)", np.sqrt(1e-3 * 600), 0.7746, 1e-4)
# E22-400T33D module: 33 dBm (2 W) -> voltages at 50 ohm
v33 = np.sqrt(dbm_to_w(33) * R)
check("33 dBm Vrms @50ohm", v33, 9.99, 0.02)
check("33 dBm Vpk @50ohm", v33 * np.sqrt(2), 14.13, 0.02)
check("30 dBm (1 W) Vrms @50ohm", np.sqrt(1.0 * R), 7.071, 1e-3)

# --- thermal noise density ----------------------------------------------------
check("kT0 at 290 K [dBm/Hz]", w_to_dbm(C.k * 290), -173.98, 0.01)
check("kT at 293.15 K [dBm/Hz]", w_to_dbm(C.k * 293.15), -173.93, 0.01)
check("kT0 in dBW/Hz", 10 * np.log10(C.k * 290), -203.98, 0.01)
check("290 K in dBK", 10 * np.log10(290), 24.62, 0.01)
check("Noise in 125 kHz LoRa BW at 290 K [dBm]", w_to_dbm(C.k * 290 * 125e3), -123.01, 0.01)

# --- Neper --------------------------------------------------------------------
check("1 Np in dB (20/ln10)", 20 / np.log(10), 8.6859, 1e-4)
check("1 dB in Np", np.log(10) / 20, 0.115129, 1e-6)

# --- adding powers ------------------------------------------------------------
check("30 dBm + 30 dBm incoherent", w_to_dbm(2 * dbm_to_w(30)), 33.01, 0.01)
check("0 + 3 - 6 dBm (R&S 4.1 example)", w_to_dbm(dbm_to_w(0) + dbm_to_w(3) + dbm_to_w(-6)), 5.12, 0.01)
# coherent in-phase equal amplitudes: voltage doubles -> +6.02 dB
check("Two equal coherent in-phase [dB over one]", 20 * np.log10(2), 6.02, 0.01)
# power-addition correction table (R&S Table 6-2), spot checks
for d, corr in [(0, 3.01), (1, 2.54), (3, 1.76), (6, 0.97), (10, 0.41), (20, 0.04)]:
    check(f"power-sum correction for delta {d} dB", 10 * np.log10(1 + 10 ** (-d / 10)), corr, 0.006)
for d, corr in [(0, 6.02), (6, 3.53), (10, 2.39), (20, 0.83)]:
    check(f"in-phase voltage-sum correction for delta {d} dB", 20 * np.log10(1 + 10 ** (-d / 20)), corr, 0.006)
# signal below noise: subtract noise (R&S 4.2 example: -65 dBm total, -70 dBm noise)
check("signal = total - noise", w_to_dbm(dbm_to_w(-65) - dbm_to_w(-70)), -66.65, 0.01)

# coherent sum of two unit phasors vs phase difference: 0 deg +6 dB, 90 deg +3 dB, 120 deg 0 dB, 180 deg -inf
for phi, want in [(0, 6.02), (90, 3.01), (120, 0.0)]:
    v = abs(1 + np.exp(1j * np.deg2rad(phi)))
    check(f"coherent sum, phase {phi} deg [dB rel one]", 20 * np.log10(v), want, 0.01)
# average over uniformly random phase of |1+e^{j phi}|^2 = 2 -> +3.01 dB (incoherent limit)
phis = np.linspace(0, 2 * np.pi, 100001)
check("random-phase average power of two unit phasors", np.mean(abs(1 + np.exp(1j * phis)) ** 2), 2.0, 1e-3)

# --- percent asymmetry --------------------------------------------------------
check("+20% voltage in dB", 20 * np.log10(1.2), 1.584, 1e-3)
check("-20% voltage in dB", 20 * np.log10(0.8), -1.938, 1e-3)
check("1% of voltage in dB", 20 * np.log10(0.01), -40.0, 1e-9)
check("1% more voltage in dB", 20 * np.log10(1.01), 0.0864, 1e-4)
check("1% more power in dB", 10 * np.log10(1.01), 0.0432, 1e-4)
check("1 dB power ratio", 10 ** 0.1, 1.2589, 1e-4)
check("0.1 dB power ratio", 10 ** 0.01, 1.0233, 1e-4)
check("3 dB exact power ratio", 10 ** 0.3, 1.9953, 1e-4)
check("-3 dB voltage ratio (R&S table typo 0.798)", 10 ** (-3 / 20), 0.7079, 1e-4)

# --- mismatch --------------------------------------------------------------------
G = 0.1
check("Gamma 0.1 return loss [dB]", -20 * np.log10(G), 20.0, 1e-9)
check("Gamma 0.1 mismatch loss [dB]", -10 * np.log10(1 - G ** 2), 0.0436, 1e-4)
check("VSWR 2 -> Gamma", (2 - 1) / (2 + 1), 0.3333, 1e-4)
check("VSWR 2 mismatch loss [dB]", -10 * np.log10(1 - (1 / 3) ** 2), 0.5115, 1e-4)

# --- antenna units -------------------------------------------------------------
# half-wave dipole directivity by numerical integration of U(theta)=[cos(pi/2 cos t)/sin t]^2
U = lambda t: (np.cos(np.pi / 2 * np.cos(t)) / np.sin(t)) ** 2
Prad, _ = integrate.quad(lambda t: U(t) * np.sin(t), 1e-9, np.pi - 1e-9)
D = 4 * np.pi * 1.0 / (2 * np.pi * Prad)  # Umax = 1
check("half-wave dipole directivity (linear)", D, 1.641, 1e-3)
check("dBd offset: dipole in dBi", 10 * np.log10(D), 2.15, 0.01)

# --- field strength units ----------------------------------------------------------
eta0 = np.sqrt(C.mu_0 / C.epsilon_0)
check("eta0 [ohm]", eta0, 376.73, 0.01)
# E (dBuV/m) for S = 1 W/m^2
E1 = np.sqrt(eta0 * 1.0)
check("1 W/m^2 in dBuV/m", 20 * np.log10(E1 / 1e-6), 145.76, 0.01)
# received power from field: Pr = E^2/eta0 * lambda^2 G/(4 pi)
# Pr[dBm] = E[dBuV/m] + G[dBi] - 20 log10 f[MHz] - K ; find K
f = 433e6
lam = C.c / f
E = 1e-6 * 10 ** (40 / 20)  # 40 dBuV/m
Pr_dbm = w_to_dbm(E ** 2 / eta0 * lam ** 2 * 1.0 / (4 * np.pi))
K = 40 + 0 - 20 * np.log10(433) - Pr_dbm
check("constant K in Pr=E+G-20log f_MHz-K", K, 77.21, 0.01)
# antenna factor AF[dB/m] = 20 log f_MHz - G_dBi - 29.79 (50 ohm)
AF_lin = E / np.sqrt(dbm_to_w(Pr_dbm) * 50)  # E / V at 50 ohm
# exact c gives 29.77; the often-quoted 29.79 uses c = 3e8 m/s
check("AF 50 ohm constant (20log f_MHz - G - AF)", 20 * np.log10(433) - 0 - 20 * np.log10(AF_lin), 29.77, 0.01)
check("AF constant with c=3e8 (sources quote 29.77-29.79 by rounding)", -20 * np.log10(np.sqrt(4 * np.pi * eta0 / 50) / 300), 29.78, 0.005)
check("AF = 9.73/(lambda sqrt G)", AF_lin, 9.73 / lam, 0.01)

# --- RCS -------------------------------------------------------------------------
check("1 m^2 in dBsm", 10 * np.log10(1.0), 0.0, 1e-12)
check("0.01 m^2 in dBsm", 10 * np.log10(0.01), -20.0, 1e-12)

# --- C/N0 and SNR ------------------------------------------------------------------
# GPS L1 C/A: -130 dBm received, 290 K, NF 2 dB -> C/N0
cn0 = -130 - (w_to_dbm(C.k * 290) + 2)
check("GPS -130 dBm with NF 2 dB -> C/N0 [dB-Hz]", cn0, 41.98, 0.01)
check("SNR in 2 MHz from 45 dB-Hz", 45 - 10 * np.log10(2e6), -18.01, 0.01)

# --- ADC ---------------------------------------------------------------------------------
check("ideal 12-bit ADC SNR [dB]", 6.02 * 12 + 1.76, 74.0, 0.01)
check("6.02 = 20 log10 2", 20 * np.log10(2), 6.0206, 1e-4)
check("1.76 = 10 log10 1.5", 10 * np.log10(1.5), 1.7609, 1e-4)

# --- log-averaging bias for noise (spectrum analyser 'video averaging' of log values) ------
rng = np.random.default_rng(1)
x = rng.exponential(1.0, 2_000_000)  # power of complex Gaussian noise ~ exponential
bias = np.mean(10 * np.log10(x)) - 10 * np.log10(np.mean(x))
check("log-average bias of noise power [dB] (theory -10*gamma/ln10 = -2.507)", bias, -10 * np.euler_gamma / np.log(10), 0.01)

# --- crest factor --------------------------------------------------------------------------
check("sine crest factor (power) [dB]", 10 * np.log10(2), 3.01, 0.01)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
