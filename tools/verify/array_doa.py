#!/usr/bin/env python3
"""
array_doa.py — verification for kb/12-phased-arrays/adaptive-beamforming-doa.md

Synthetic narrowband data, ULA (N elements, d = lambda/2 unless stated), x(t) = A s(t) + n(t).
  1. Single-source RMSE vs SNR of Bartlett (delay-and-sum peak), MVDR/Capon, MUSIC, Root-MUSIC, ESPRIT
     against the deterministic and stochastic Cramer-Rao bounds (closed form for one source on a ULA).
  2. Two-source resolution probability vs SNR (separation 0.5 and 0.3 of the Rayleigh beamwidth).
  3. Coherent sources (multipath): MUSIC fails; forward and forward-backward spatial smoothing.
  4. Adaptive beamforming: MVDR/MPDR output SINR vs snapshots (Reed–Mallett–Brennan: K = 2N -> -3 dB),
     signal cancellation with steering mismatch when the desired signal is in the training data, and
     recovery with diagonal loading. LCMV with an explicit null.
  5. Source-number estimation with MDL (Wax & Kailath 1985) vs SNR and snapshots.
  6. Uniform circular array (5 elements, KrakenSDR-like) vs ULA: 360° azimuth, no mirror ambiguity.
"""
import numpy as np

rng = np.random.default_rng(42)
d0 = 0.5


def steer(N, u, d=d0):
    n = np.arange(N)[:, None]
    return np.exp(1j * 2 * np.pi * d * n * np.atleast_1d(u)[None, :])  # N x len(u)


def snapshots(N, us, snr_db, K, coherent=False, d=d0, powers=None):
    A = steer(N, np.array(us), d)
    M = len(us)
    p = np.ones(M) if powers is None else np.asarray(powers)
    if coherent:
        s0 = (rng.standard_normal(K) + 1j * rng.standard_normal(K)) / np.sqrt(2)
        S = np.vstack([s0 * np.exp(1j * rng.uniform(0, 2 * np.pi)) for _ in range(M)]) * np.sqrt(p)[:, None]
    else:
        S = (rng.standard_normal((M, K)) + 1j * rng.standard_normal((M, K))) / np.sqrt(2) * np.sqrt(p)[:, None]
    sig2 = 10 ** (-snr_db / 10)
    Nn = (rng.standard_normal((N, K)) + 1j * rng.standard_normal((N, K))) * np.sqrt(sig2 / 2)
    return A @ S + Nn


UG = np.linspace(-1, 1, 8001)


def spectra(R, N, M):
    a = steer(N, UG)
    Pb = np.real(np.sum(np.conj(a) * (R @ a), axis=0))
    Ri = np.linalg.inv(R)
    Pc = 1 / np.real(np.sum(np.conj(a) * (Ri @ a), axis=0))
    w, V = np.linalg.eigh(R)
    En = V[:, : N - M]
    Pm = 1 / np.real(np.sum(np.abs(En.conj().T @ a) ** 2, axis=0))
    return Pb, Pc, Pm, En, V[:, N - M:]


def peaks(P, M):
    idx = [i for i in range(1, len(P) - 1) if P[i] >= P[i - 1] and P[i] > P[i + 1]]
    idx = sorted(idx, key=lambda i: P[i], reverse=True)[:M]
    # parabolic refinement
    out = []
    for i in idx:
        y0, y1, y2 = np.log(P[i - 1]), np.log(P[i]), np.log(P[i + 1])
        den = y0 - 2 * y1 + y2
        delta = 0.5 * (y0 - y2) / den if den != 0 else 0.0
        out.append(UG[i] + delta * (UG[1] - UG[0]))
    return np.sort(np.array(out))


def root_music(En, M, d=d0):
    N = En.shape[0]
    C = En @ En.conj().T
    coeffs = np.array([np.trace(C, offset=k) for k in range(N - 1, -N, -1)])
    roots = np.roots(coeffs)
    roots = roots[np.abs(roots) < 1]
    roots = roots[np.argsort(np.abs(np.abs(roots) - 1))][:M]
    return np.sort(np.angle(roots) / (2 * np.pi * d))


def esprit(Es, d=d0):
    E1, E2 = Es[:-1], Es[1:]
    # total least squares ESPRIT
    Mh = Es.shape[1]
    U, s, Vh = np.linalg.svd(np.hstack([E1, E2]), full_matrices=False)
    V = Vh.conj().T
    V12 = V[:Mh, Mh:]
    V22 = V[Mh:, Mh:]
    Psi = -V12 @ np.linalg.inv(V22)
    ev = np.linalg.eigvals(Psi)
    return np.sort(np.angle(ev) / (2 * np.pi * d))


def crb_single(N, K, snr, d=d0):
    k = 2 * np.pi
    det = 6 / (K * snr * (k * d) ** 2 * N * (N ** 2 - 1))
    sto = det * (1 + 1 / (N * snr))
    return det, sto


print("=" * 78)
print("1. Single source, N=8, K=100, u=0.2: RMSE (in u) vs SNR, and CRB")
N, K, u0 = 8, 100, 0.2
for snr_db in (-10, -5, 0, 10, 20):
    errs = {k: [] for k in ("Bartlett", "MVDR", "MUSIC", "RootMUSIC", "ESPRIT")}
    for _ in range(300):
        X = snapshots(N, [u0], snr_db, K)
        R = X @ X.conj().T / K
        Pb, Pc, Pm, En, Es = spectra(R, N, 1)
        errs["Bartlett"].append(peaks(Pb, 1)[0] - u0)
        errs["MVDR"].append(peaks(Pc, 1)[0] - u0)
        errs["MUSIC"].append(peaks(Pm, 1)[0] - u0)
        errs["RootMUSIC"].append(root_music(En, 1)[0] - u0)
        errs["ESPRIT"].append(esprit(Es)[0] - u0)
    det, sto = crb_single(N, K, 10 ** (snr_db / 10))
    row = "  ".join(f"{k} {np.sqrt(np.mean(np.square(v))):.2e}" for k, v in errs.items())
    print(f"  SNR {snr_db:+3d} dB: {row} | √CRB det {np.sqrt(det):.2e} sto {np.sqrt(sto):.2e} "
          f"(= {np.degrees(np.sqrt(sto)/np.cos(np.arcsin(u0))):.3f}° at 11.5°)")

print("=" * 78)
print("2. Two equal uncorrelated sources, N=8, K=100: resolution probability")
beam_u = 2 / (N * d0)  # null-to-null width in u = 2 lambda/(N d); Rayleigh = half of that
ray = 1 / (N * d0)
for frac in (1.0, 0.5, 0.3):
    sep = frac * ray
    us = [0.1, 0.1 + sep]
    for snr_db in (0, 10, 20, 30):
        ok = {"Bartlett": 0, "MVDR": 0, "MUSIC": 0, "RootMUSIC": 0, "ESPRIT": 0}
        T = 150
        for _ in range(T):
            X = snapshots(N, us, snr_db, K)
            R = X @ X.conj().T / K
            Pb, Pc, Pm, En, Es = spectra(R, N, 2)
            ests = {"Bartlett": peaks(Pb, 2), "MVDR": peaks(Pc, 2), "MUSIC": peaks(Pm, 2),
                    "RootMUSIC": root_music(En, 2), "ESPRIT": esprit(Es)}
            for k, e in ests.items():
                if len(e) == 2 and np.all(np.abs(np.sort(e) - np.array(us)) < sep / 2):
                    ok[k] += 1
        print(f"  sep {frac:.1f}×Rayleigh (Δu={sep:.3f}, ≈{np.degrees(np.arcsin(0.1+sep)-np.arcsin(0.1)):.2f}°), SNR {snr_db:2d} dB: " +
              "  ".join(f"{k} {100*v/T:5.1f}%" for k, v in ok.items()))

print("=" * 78)
print("3. Coherent sources (direct + reflected, same waveform), N=8, u = -0.2 and 0.25, SNR 20 dB, K=200")


def smooth(R, L, fb=False):
    N = R.shape[0]
    P = N - L + 1
    Rs = sum(R[p:p + L, p:p + L] for p in range(P)) / P
    if fb:
        J = np.eye(L)[::-1]
        Rs = 0.5 * (Rs + J @ Rs.conj() @ J)
    return Rs


us = [-0.2, 0.25]
for label, L, fb in (("no smoothing", 8, False), ("FSS L=6", 6, False), ("FSS L=5", 5, False), ("FBSS L=6", 6, True), ("FB only (L=8)", 8, True)):
    succ = 0
    errs = []
    for _ in range(100):
        X = snapshots(N, us, 20, 200, coherent=True)
        R = X @ X.conj().T / 200
        Rs = smooth(R, L, fb)
        Pb, Pc, Pm, En, Es = spectra(Rs, L, 2)
        e = peaks(Pm, 2)
        if len(e) == 2 and np.all(np.abs(e - np.array(us)) < 0.05):
            succ += 1
            errs.append(np.max(np.abs(e - np.array(us))))
    print(f"  {label:14s}: MUSIC success {succ}%  (max error when successful {np.mean(errs) if errs else np.nan:.4f} in u)")
print("  (eigenvalues of R for coherent pair without smoothing: one large, one ≈ noise → rank-1 signal subspace)")
X = snapshots(N, us, 20, 2000, coherent=True)
R = X @ X.conj().T / 2000
print("   eig(R) top 3:", np.round(np.sort(np.linalg.eigvalsh(R))[::-1][:3], 3), "; eig(FBSS L=6) top 3:",
      np.round(np.sort(np.linalg.eigvalsh(smooth(R, 6, True)))[::-1][:3], 3))

print("=" * 78)
print("4. Adaptive beamforming (N=8): MVDR SINR vs snapshots, signal cancellation, diagonal loading, LCMV")
N = 8
u_s, u_j = 0.0, 0.45
INR = 30.0  # dB jammer
sig2 = 1.0
a_s = steer(N, u_s)[:, 0]
a_j = steer(N, u_j)[:, 0]
Rin = 10 ** (INR / 10) * np.outer(a_j, a_j.conj()) + sig2 * np.eye(N)
snr_el = 0.0  # dB desired per element (for SINR computation)
ps = 10 ** (snr_el / 10)


def sinr(w):
    return ps * np.abs(w.conj() @ a_s) ** 2 / np.real(w.conj() @ Rin @ w)


w_opt = np.linalg.solve(Rin, a_s)
sinr_opt = sinr(w_opt)
print(f"  optimum SINR {10*np.log10(sinr_opt):.2f} dB (N·SNR = {10*np.log10(N*ps):.2f} dB); conventional (DAS) SINR {10*np.log10(sinr(a_s)):.2f} dB")
for K in (8, 12, 16, 24, 32, 64, 160):
    loss = []
    for _ in range(400):
        Xn = np.sqrt(10 ** (INR / 10)) * np.outer(a_j, (rng.standard_normal(K) + 1j * rng.standard_normal(K)) / np.sqrt(2)) + \
             (rng.standard_normal((N, K)) + 1j * rng.standard_normal((N, K))) / np.sqrt(2)
        Rh = Xn @ Xn.conj().T / K
        w = np.linalg.solve(Rh + 1e-9 * np.eye(N), a_s)
        loss.append(sinr(w) / sinr_opt)
    rho = (K + 2 - N) / (K + 1)
    print(f"  SMI K={K:3d} (noise+jammer only training): mean SINR loss {10*np.log10(np.mean(loss)):6.2f} dB; RMB E[ρ]=(K+2−N)/(K+1) → {10*np.log10(rho):6.2f} dB")
# signal in training (MPDR) with steering mismatch
print("  MPDR (desired signal present in training, K=200) with pointing error Δu and diagonal loading LNR:")
K = 200
for snr_db in (0, 10, 20):
    for du in (0.0, 0.02, 0.05):
        res = []
        for lnr in (None, 10, 20):
            vals = []
            for _ in range(100):
                s = np.sqrt(10 ** (snr_db / 10)) * (rng.standard_normal(K) + 1j * rng.standard_normal(K)) / np.sqrt(2)
                Xj = np.sqrt(10 ** (INR / 10)) * np.outer(a_j, (rng.standard_normal(K) + 1j * rng.standard_normal(K)) / np.sqrt(2))
                Xn = (rng.standard_normal((N, K)) + 1j * rng.standard_normal((N, K))) / np.sqrt(2)
                X = np.outer(a_s, s) + Xj + Xn
                Rh = X @ X.conj().T / K
                if lnr is not None:
                    Rh = Rh + 10 ** (lnr / 10) * np.eye(N)
                a_assumed = steer(N, u_s + du)[:, 0]
                w = np.linalg.solve(Rh, a_assumed)
                # true output SINR (signal through true a_s)
                pss = 10 ** (snr_db / 10)
                vals.append(pss * np.abs(w.conj() @ a_s) ** 2 / np.real(w.conj() @ Rin @ w))
            res.append(10 * np.log10(np.mean(vals)))
        print(f"    SNR {snr_db:2d} dB, Δu={du:.2f}: SINR no loading {res[0]:6.2f} dB, LNR 10 dB {res[1]:6.2f}, LNR 20 dB {res[2]:6.2f} (optimum {10*np.log10(N*10**(snr_db/10)):.2f})")
# LCMV: unit gain at u_s, null at u_j2 (a second, predicted interferer), minimise output power under Rin
u_j2 = -0.3
C = np.c_[a_s, steer(N, u_j2)[:, 0]]
f = np.array([1.0, 0.0])
Ri = np.linalg.inv(Rin)
w_l = Ri @ C @ np.linalg.solve(C.conj().T @ Ri @ C, f)
uu = np.linspace(-1, 1, 4001)
pat = 20 * np.log10(np.abs(steer(N, uu).conj().T @ w_l) + 1e-15)
pat -= 20 * np.log10(np.abs(w_l.conj() @ a_s))
print(f"  LCMV: response at u_s {20*np.log10(abs(w_l.conj()@a_s)):.2f} dB, at constrained null u={u_j2}: {pat[np.argmin(abs(uu-u_j2))]:.1f} dB, "
      f"at jammer u={u_j}: {pat[np.argmin(abs(uu-u_j))]:.1f} dB")

print("=" * 78)
print("5. MDL source-number estimation (N=8, two sources at u=0.1, 0.35)")


def mdl(ev, K):
    ev = np.sort(ev)[::-1]
    N = len(ev)
    vals = []
    for k in range(N):
        tail = ev[k:]
        g = np.exp(np.mean(np.log(tail)))
        a = np.mean(tail)
        L = -K * (N - k) * np.log(g / a)
        vals.append(L + 0.5 * k * (2 * N - k) * np.log(K))
    return int(np.argmin(vals))


for K in (20, 100, 500):
    row = []
    for snr_db in (-10, -5, 0, 5):
        c = 0
        for _ in range(200):
            X = snapshots(N, [0.1, 0.35], snr_db, K)
            R = X @ X.conj().T / K
            c += mdl(np.linalg.eigvalsh(R), K) == 2
        row.append(f"SNR {snr_db:+d} dB: {100*c/200:5.1f}%")
    print(f"  K={K:3d}: " + "  ".join(row))

print("=" * 78)
print("6. 5-element UCA (KrakenSDR-like), spacing 0.4λ between neighbours, MUSIC over 0..360°")
Nc = 5
s_mult = 0.4
r = s_mult / np.sqrt(2 * (1 - np.cos(2 * np.pi / Nc)))  # KrakenSDR wiki radius formula (in λ)
print(f"  radius = {r:.4f} λ (= s/(2 sin(π/n)) = {s_mult/(2*np.sin(np.pi/Nc)):.4f} λ); at 433 MHz: {r*299.792458/433*100:.1f} cm")
phi_e = 2 * np.pi * np.arange(Nc) / Nc
az = np.radians(np.arange(0, 360, 0.25))


def a_uca(phi):
    return np.exp(1j * 2 * np.pi * r * np.cos(np.atleast_1d(phi)[None, :] - phi_e[:, None]))


for true_deg in (30, 150, 250):
    errs = []
    for _ in range(100):
        s = (rng.standard_normal(200) + 1j * rng.standard_normal(200)) / np.sqrt(2)
        X = np.outer(a_uca(np.radians(true_deg))[:, 0], s) + (rng.standard_normal((Nc, 200)) + 1j * rng.standard_normal((Nc, 200))) * np.sqrt(0.1 / 2)
        R = X @ X.conj().T / 200
        w, V = np.linalg.eigh(R)
        En = V[:, :Nc - 1]
        A = a_uca(az)
        P = 1 / np.sum(np.abs(En.conj().T @ A) ** 2, axis=0)
        est = np.degrees(az[np.argmax(P)])
        errs.append((est - true_deg + 180) % 360 - 180)
    print(f"  true az {true_deg:3d}° @ 10 dB SNR, 200 snapshots: RMSE {np.sqrt(np.mean(np.square(errs))):.3f}°, max |err| {np.max(np.abs(errs)):.2f}°")
# ULA mirror ambiguity: a source at azimuth phi and at 180-phi give identical ULA steering vectors
aL = lambda phi: steer(4, np.cos(np.radians(phi)))[:, 0]
print(f"  ULA (4 el, axis = 0°): |a(30°)^H a(-30°)|/N = {abs(aL(30).conj()@aL(-30))/4:.3f} (identical → front/back ambiguity); "
      f"UCA: |a(30°)^H a(-30°)|/N = {abs(a_uca(np.radians(30))[:,0].conj()@a_uca(np.radians(-30))[:,0])/Nc:.3f}")
print("done")
