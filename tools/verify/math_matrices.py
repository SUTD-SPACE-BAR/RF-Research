#!/usr/bin/env python3
"""Verification for kb/00-math-foundations/matrices-and-linear-algebra-for-networks.md

Checks: DC nodal analysis Y V = I; MNA with a voltage source; AC nodal analysis of an
L-network match at 433 MHz; Z -> S conversion vs scikit-rf; reciprocity (S = S^T) and
losslessness (S^H S = I) of an LC network; ABCD cascade vs scikit-rf; coupled-resonator
eigenfrequencies f0/sqrt(1 +/- k); state-space eigenvalues = RLC poles; MIMO capacity via
SVD (and water-filling); MVDR beamformer null; 3-term one-port VNA calibration by
(least-squares) linear solve; conditioning of polynomial fits (centering/scaling).
Run: python3 tools/verify/math_matrices.py
"""
import numpy as np
import warnings

ok_all = True


def check(name, got, want, tol):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol})")


# --- DC nodal analysis -----------------------------------------------------------------
# 1 mA into node 1; R1 = 1k (n1-gnd), R2 = 2k (n1-n2), R3 = 3k (n2-gnd)
G1, G2, G3 = 1 / 1e3, 1 / 2e3, 1 / 3e3
Y = np.array([[G1 + G2, -G2], [-G2, G2 + G3]])
V = np.linalg.solve(Y, [1e-3, 0])
Rin = 1e3 * 5e3 / 6e3
check("nodal: V1 = I * (R1 || (R2+R3))", V[0], 1e-3 * Rin, 1e-12)
check("nodal: V2 = V1 * R3/(R2+R3)", V[1], V[0] * 3 / 5, 1e-12)
check("Y matrix symmetric (reciprocal network)", np.max(abs(Y - Y.T)), 0, 0)

# --- MNA with a voltage source: 5 V source at node1, R 1k to node2, 1k to ground ------
# unknowns [V1, V2, I_src]
A = np.array([[1 / 1e3, -1 / 1e3, 1],
              [-1 / 1e3, 2 / 1e3, 0],
              [1, 0, 0]])
x = np.linalg.solve(A, [0, 0, 5.0])
check("MNA: divider output 2.5 V", x[1], 2.5, 1e-12)
check("MNA: source current -2.5 mA (into + terminal convention)", x[2], -2.5e-3, 1e-12)

# --- AC nodal: L-network matching 10 ohm load to 50 ohm at 433 MHz ---------------------
f = 433e6
w = 2 * np.pi * f
RL, R0 = 10.0, 50.0
Qm = np.sqrt(R0 / RL - 1)                     # 2
Xs = Qm * RL                                  # series L reactance 20 ohm
Xp = R0 / Qm                                  # shunt C reactance 25 ohm (at 50-ohm side)
Lser = Xs / w
Csh = 1 / (w * Xp)
# nodes: 1 = input (shunt C to gnd), 2 = load (RL to gnd); series L between 1 and 2
yC, yL, yR = 1j * w * Csh, 1 / (1j * w * Lser), 1 / RL
Yac = np.array([[yC + yL, -yL], [-yL, yL + yR]])
Zin = np.linalg.inv(Yac)[0, 0]
check("L-match at 433 MHz: Re Zin = 50 ohm", Zin.real, 50.0, 1e-9)
check("L-match at 433 MHz: Im Zin = 0", Zin.imag, 0.0, 1e-9)
print(f"      L = {Lser*1e9:.2f} nH, C = {Csh*1e12:.2f} pF")

# --- Z -> S, reciprocity, losslessness ------------------------------------------------------
import skrf as rf
Z0 = 50.0
# lossless T-network: series jX1, shunt jX2, series jX3
X1, X2, X3 = 30.0, -40.0, 15.0
Zt = np.array([[1j * (X1 + X2), 1j * X2], [1j * X2, 1j * (X2 + X3)]])
I2 = np.eye(2)
S = (Zt - Z0 * I2) @ np.linalg.inv(Zt + Z0 * I2)
from skrf.network import z2s
S_skrf = z2s(Zt[None, :, :], z0=Z0)[0]
check("S = (Z - Z0)(Z + Z0)^-1 matches scikit-rf z2s", np.max(abs(S - S_skrf)), 0, 1e-12)
check("reciprocal: S = S^T", np.max(abs(S - S.T)), 0, 1e-12)
check("lossless: S^H S = I", np.max(abs(S.conj().T @ S - I2)), 0, 1e-12)
# add loss -> eigenvalues of I - S^H S in [0, 1] (passive)
Zl = Zt + np.diag([5.0, 5.0])
Sl = (Zl - Z0 * I2) @ np.linalg.inv(Zl + Z0 * I2)
ev = np.linalg.eigvalsh(I2 - Sl.conj().T @ Sl)
check("lossy passive: min eig(I - S^H S) >= 0", float(ev.min() >= 0), 1.0, 0)

# --- ABCD cascade --------------------------------------------------------------------------------
freq = rf.Frequency(433, 433, 1, unit='MHz')
line = rf.media.DefinedGammaZ0(freq, z0_port=50, z0=50)
a = line.line(30, 'deg')
b = line.shunt_capacitor(3e-12)
casc = a ** b
abcd = a.a[0] @ b.a[0]
check("ABCD of cascade = product of ABCDs (vs scikit-rf **)", np.max(abs(abcd - casc.a[0])), 0, 1e-9)

# --- coupled resonators: generalized eigenproblem --------------------------------------------------
L0, C0, k = 10e-9, 13.5e-12, 0.05
M = k * L0
Lmat = np.array([[L0, M], [M, L0]])
Cinv = np.eye(2) / C0
# L d2i/dt2 + C^-1 i = 0  ->  w^2 L v = C^-1 v
w2 = np.sort(np.real(np.linalg.eigvals(np.linalg.solve(Lmat, Cinv))))
f0 = 1 / (2 * np.pi * np.sqrt(L0 * C0))
check("coupled resonators: lower mode f0/sqrt(1+k)", np.sqrt(w2[0]) / (2 * np.pi), f0 / np.sqrt(1 + k), 1e-3)
check("coupled resonators: upper mode f0/sqrt(1-k)", np.sqrt(w2[1]) / (2 * np.pi), f0 / np.sqrt(1 - k), 1e-3)
check("mode splitting / f0 ~ k", (np.sqrt(w2[1]) - np.sqrt(w2[0])) / (2 * np.pi) / f0, k, 2e-3)

# --- state-space eigenvalues = RLC poles -------------------------------------------------------------
R, L, C = 20.0, 1e-6, 1e-9
Ass = np.array([[0, 1 / C], [-1 / L, -R / L]])   # x = [vC, iL]
poles = np.sort_complex(np.linalg.eigvals(Ass))
p_exact = np.sort_complex(np.roots([L * C, R * C, 1]))
check("state-space eig = roots of LCs^2+RCs+1", np.max(abs(poles - p_exact)) / abs(p_exact[0]), 0, 1e-12)

# --- MIMO capacity via SVD ---------------------------------------------------------------------------------
rng = np.random.default_rng(7)
H = (rng.standard_normal((2, 2)) + 1j * rng.standard_normal((2, 2))) / np.sqrt(2)
snr = 10 ** (20 / 10)
sv = np.linalg.svd(H, compute_uv=False)
C_svd = np.sum(np.log2(1 + snr / 2 * sv ** 2))
C_det = np.log2(np.real(np.linalg.det(np.eye(2) + snr / 2 * H @ H.conj().T)))
check("MIMO capacity: sum log2(1+SNR s_i^2/Nt) = log2 det(I + SNR/Nt H H^H)", C_svd, C_det, 1e-9)
# water-filling >= equal power
def waterfill(g, P):
    g = np.sort(g)[::-1]
    for m in range(len(g), 0, -1):
        mu = (P + np.sum(1 / g[:m])) / m
        p = mu - 1 / g[:m]
        if np.all(p > 0):
            return np.sum(np.log2(1 + p * g[:m]))
C_wf = waterfill(snr * sv ** 2, 1.0)
check("water-filling capacity >= equal-power capacity", float(C_wf >= C_svd - 1e-12), 1.0, 0)
# rank-1 (pure LOS, closely spaced) channel: only one eigenmode
Hlos = np.ones((2, 2))
sv1 = np.linalg.svd(Hlos, compute_uv=False)
check("rank-1 LOS channel: second singular value = 0", sv1[1], 0, 1e-12)
check("rank-1: capacity = log2(1 + SNR * 4/2) (array gain, no multiplexing)", np.sum(np.log2(1 + snr / 2 * sv1 ** 2)), np.log2(1 + snr * 2), 1e-9)

# --- MVDR beamformer ---------------------------------------------------------------------------------------------
Nel = 8
d = 0.5
steer = lambda th: np.exp(1j * 2 * np.pi * d * np.arange(Nel) * np.sin(np.radians(th)))
a0, ai = steer(0), steer(30)
Rcov = 100 * np.outer(ai, ai.conj()) + np.eye(Nel)        # strong interferer at 30 deg + unit noise
wm = np.linalg.solve(Rcov, a0)
wm /= (a0.conj() @ wm)
check("MVDR: unit gain towards 0 deg", abs(wm.conj() @ a0), 1.0, 1e-12)
check("MVDR: interferer at 30 deg suppressed (< -35 dB)", float(20 * np.log10(abs(wm.conj() @ ai)) < -35), 1.0, 0)
evals = np.sort(np.linalg.eigvalsh(Rcov))[::-1]
check("covariance: one large eigenvalue (signal subspace dim = 1)", evals[0], 100 * Nel + 1, 1e-6)
check("covariance: remaining eigenvalues = noise power", evals[1], 1.0, 1e-9)

# --- 3-term one-port VNA calibration as a linear solve ------------------------------------------------------------
# model: Gm = e00 + e01e10 Ga / (1 - e11 Ga)  <=>  Gm = e00 + Ga Gm e11 - Ga (e00 e11 - e01e10)
e00, e11, e0110 = 0.05 + 0.02j, 0.10 - 0.05j, 0.90 * np.exp(-1j * 0.6)
meas = lambda Ga: e00 + e0110 * Ga / (1 - e11 * Ga)
stds = np.array([1.0, -1.0, 0.0])                   # ideal open, short, load
Gm = meas(stds)
Amat = np.column_stack([np.ones(3), stds * Gm, -stds])
sol = np.linalg.solve(Amat, Gm)                     # [e00, e11, delta_e]
check("OSL cal recovers e00", abs(sol[0] - e00), 0, 1e-12)
check("OSL cal recovers e11", abs(sol[1] - e11), 0, 1e-12)
check("OSL cal recovers e01e10", abs((sol[0] * sol[1] - sol[2]) - e0110), 0, 1e-12)
# overdetermined with noise (5 standards) -> least squares
stds5 = np.array([1.0, -1.0, 0.0, 1j, -1j])
Gm5 = meas(stds5) + 1e-3 * (rng.standard_normal(5) + 1j * rng.standard_normal(5))
A5 = np.column_stack([np.ones(5), stds5 * Gm5, -stds5])
sol5, *_ = np.linalg.lstsq(A5, Gm5, rcond=None)
check("5-standard LS cal: e00 error small (< 3e-3)", float(abs(sol5[0] - e00) < 3e-3), 1.0, 0)
# correct a DUT
Gdut = 0.3 + 0.4j
Gm_dut = meas(Gdut)
Gcorr = (Gm_dut - sol[0]) / (sol[1] * (Gm_dut - sol[0]) + (sol[0] * sol[1] - sol[2]))
check("corrected DUT reflection", abs(Gcorr - Gdut), 0, 1e-12)

# --- conditioning of polynomial fits ---------------------------------------------------------------------------------
T = np.linspace(-20, 85, 50)          # temperature, C
ppm = 0.03 * (T - 25) ** 2 - 0.0005 * (T - 25) ** 3
V_raw = np.vander(T + 273.15, 4)      # fitting in kelvin, raw
Ts = (T - T.mean()) / T.std()
V_sc = np.vander(Ts, 4)
cr, cs = np.linalg.cond(V_raw), np.linalg.cond(V_sc)
print(f"      cond(Vandermonde, raw K) = {cr:.3g}; centred/scaled = {cs:.3g}")
check("centering/scaling reduces condition number by > 1e6", float(cr / cs > 1e6), 1.0, 0)

# --- L-match bandwidth (page example 2) ------------------------------------------------------------------------------
fsw = np.linspace(100e6, 1000e6, 90001)
wsw = 2 * np.pi * fsw
Zin_sw = 1 / (1j * wsw * Csh + 1 / (RL + 1j * wsw * Lser))
Gsw = abs((Zin_sw - 50) / (Zin_sw + 50))
ok10 = fsw[Gsw < 10 ** (-10 / 20)]
check("L-match RL>10 dB lower edge [MHz]", ok10.min() / 1e6, 343.0, 0.5)
check("L-match RL>10 dB upper edge [MHz]", ok10.max() / 1e6, 507.4, 0.5)
# --- passivity example (page example 3) -------------------------------------------------------------------------------
Sx = np.array([[0.05, 0.5], [0.5, 0.05]])
check("example S: min eig(I - S^H S)", np.linalg.eigvalsh(np.eye(2) - Sx.T @ Sx).min(), 0.6975, 1e-9)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
