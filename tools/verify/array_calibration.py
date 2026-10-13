#!/usr/bin/env python3
"""
array_calibration.py — verification for kb/12-phased-arrays/array-calibration.md

  1. REV (rotating-element electric-field vector, Mano & Katagi 1982): power-only far-field calibration of an
     analog array. Derivation used: rotating element n by D changes the total field E = (E0-En) + En e^{jD};
     P(D) = A + B cos(D + psi) -> |E0-En|, |En| (two solutions; take |En| < |E0-En|) and relative phase.
     Recover all element excitations, correct, iterate; with power-measurement noise and phase-shifter state errors.
  2. Coherent receiver (KrakenSDR-style) calibration with a common noise source: integer + fractional sample
     delay and complex gain per channel by cross-correlation; phase-estimate error vs the formula
     var(phi) ~ (1/(2M)) (1/s1 + 1/s2 + 1/(s1 s2)), s = per-channel SNR of the injected noise.
  3. Mutual-coupling self-calibration (Aumann, Fenn, Willwerth 1989): M_mn = t_m c(|m-n|) r_n measured between
     element pairs; alternating least squares with translation invariance + reciprocity of c.
     Shows the residual gauge ambiguity (alternating +-1 "parity" pattern) and the bias from edge effects.
  4. Required calibration accuracy -> sidelobe floor (link to tapering formula) for 8 and 64 elements.
"""
import numpy as np

rng = np.random.default_rng(2026)


def af_db(w, u=np.linspace(-1, 1, 4001), d=0.5):
    N = len(w)
    x = np.arange(N) * d
    P = np.abs(np.exp(1j * 2 * np.pi * np.outer(u, x)) @ w) ** 2
    return 10 * np.log10(P / P.max() + 1e-30)


def peak_sll(w):
    P = af_db(w)
    i = np.argmax(P)
    r = i
    while r < len(P) - 1 and P[r + 1] < P[r]:
        r += 1
    l = i
    while l > 0 and P[l - 1] < P[l]:
        l -= 1
    m = np.ones_like(P, bool); m[l:r + 1] = False
    return P[m].max()


print("=" * 78)
print("1. REV calibration (8 elements, broadside beacon, Taylor-25 target taper)")
from scipy.signal.windows import taylor
N = 8
target = taylor(N, nbar=3, sll=25)
target = target / target.max()


def rev_measure(true_w, bits, snr_db, ps_err_deg, meas_per_state=1):
    """Return estimated complex excitations (relative to the total field) for each element."""
    states = np.arange(2 ** bits) * 2 * np.pi / 2 ** bits
    est = np.zeros(N, complex)
    E0 = np.sum(true_w)
    for n in range(N):
        Pm = []
        for D in states:
            Dact = D + np.radians(ps_err_deg) * rng.standard_normal()
            E = E0 - true_w[n] + true_w[n] * np.exp(1j * Dact)
            P = np.abs(E) ** 2
            noise = P * 10 ** (-snr_db / 10) * rng.standard_normal(meas_per_state).mean() if snr_db is not None else 0.0
            Pm.append(P + noise)
        Pm = np.array(Pm)
        # least-squares fit P = A + Bc cos D + Bs sin D
        G = np.c_[np.ones_like(states), np.cos(states), np.sin(states)]
        A, Bc, Bs = np.linalg.lstsq(G, Pm, rcond=None)[0]
        B = np.hypot(Bc, Bs)
        psi = np.arctan2(-Bs, Bc)  # B cos(D + psi) = B cosD cos psi - B sinD sin psi
        # |a|^2 + |b|^2 = A, 2|a||b| = B, a = E0 - En, b = En; choose |b| < |a|
        disc = np.sqrt(max(A ** 2 - B ** 2, 0))
        b2 = (A - disc) / 2
        a2 = (A + disc) / 2
        b_over_a = np.sqrt(b2 / a2) * np.exp(1j * psi)  # arg(b) - arg(a) = psi
        est[n] = b_over_a / (1 + b_over_a)  # En / E0
    return est


for bits, snr, pserr in ((6, None, 0.0), (6, 30, 0.0), (6, 20, 2.0), (4, 20, 4.0), (3, 20, 4.0)):
    # true channel errors: 1 dB rms amplitude, 20° rms phase
    err = 10 ** (1.0 * rng.standard_normal(N) / 20) * np.exp(1j * np.radians(20) * rng.standard_normal(N))
    cmd = target.astype(complex)  # commanded weights
    hist = []
    for it in range(3):
        true_w = cmd * err
        est = rev_measure(true_w, bits, snr, pserr)
        # estimated channel error relative to commanded (up to common complex factor)
        e_est = est / cmd
        e_est /= e_est[0]
        true_rel = err / err[0]
        resid = e_est / true_rel
        amp_rms = np.std(20 * np.log10(np.abs(resid)))
        ph_rms = np.degrees(np.std(np.angle(resid * np.conj(resid.mean()))))
        hist.append((amp_rms, ph_rms, peak_sll(true_w)))
        # correct: divide commanded weights by estimated error (keep max |w| = 1)
        # e_est estimates the channel error (up to a common factor): command target / e_est
        cmd = target / e_est
        cmd = cmd / np.max(np.abs(cmd))
        # after correction the new "error" relative to target:
    final_w = cmd * err
    s0 = peak_sll(target * err)
    s1 = peak_sll(final_w)
    print(f"  {bits}-bit states, SNR {str(snr):>4s} dB, PS state error {pserr}° rms: est. error after pass1 {hist[0][0]:.2f} dB / {hist[0][1]:.2f}°; "
          f"SLL uncalibrated {s0:6.2f} dB -> after 3 passes {s1:6.2f} dB (design {peak_sll(target):.2f})")
# measurement count
print(f"  measurements: N × 2^bits = {N} × 64 = {N*64} power readings for a 6-bit sweep; 3 states minimum per element ({3*N})")

print("=" * 78)
print("2. Noise-source channel calibration (complex gain + delay by cross-correlation)")
Mlist = (1024, 4096, 16384, 65536)
for snr_db in (10, 20, 30):
    s = 10 ** (snr_db / 10)
    for M in Mlist:
        errs = []
        for _ in range(400):
            src = (rng.standard_normal(M) + 1j * rng.standard_normal(M)) / np.sqrt(2)
            g = np.exp(1j * 0.7)  # channel-2 relative complex gain
            n1 = (rng.standard_normal(M) + 1j * rng.standard_normal(M)) / np.sqrt(2 * s)
            n2 = (rng.standard_normal(M) + 1j * rng.standard_normal(M)) / np.sqrt(2 * s)
            x1 = src + n1
            x2 = g * src + n2
            r = np.vdot(x1, x2)  # sum conj(x1) x2
            errs.append(np.angle(r * np.conj(g)))
        sd = np.degrees(np.std(errs))
        th = np.degrees(np.sqrt((1 / s + 1 / s + 1 / s ** 2) / (2 * M)))
        if M in (1024, 65536):
            print(f"  SNR {snr_db} dB, M = {M:6d} samples: phase std {sd:6.3f}° (formula {th:6.3f}°)")
# delay estimation: integer lag by xcorr peak, fractional by phase slope across frequency
M = 1 << 14
fs = 2.4e6
src = (rng.standard_normal(M + 64) + 1j * rng.standard_normal(M + 64)) / np.sqrt(2)
true_lag = 17
frac = 0.3  # samples
X = np.fft.fft(src[:M])
f = np.fft.fftfreq(M)
x1 = src[:M]
x2 = np.fft.ifft(X * np.exp(-1j * 2 * np.pi * f * (true_lag + frac))) * np.exp(1j * 1.1)
x2 = x2 + (rng.standard_normal(M) + 1j * rng.standard_normal(M)) / np.sqrt(2 * 100)
xc = np.fft.ifft(np.conj(np.fft.fft(x1)) * np.fft.fft(x2))
lag = int(np.argmax(np.abs(xc)))
lag = lag if lag < M // 2 else lag - M
X1 = np.fft.fft(x1); X2 = np.fft.fft(np.roll(x2, -lag))
cross = np.conj(X1) * X2
# robust phase-slope estimate: angle of the lag-1 autocorrelation of the cross-spectrum (no unwrapping)
cs = np.fft.fftshift(cross)[M // 8: 7 * M // 8]  # contiguous bins, away from the ±fs/2 wrap and band edges
Lb = M // 4  # correlate bins Lb apart: phase step 2π·τ·Lb/M ≫ estimator noise (adjacent bins are too noise-sensitive)
slope = np.angle(np.sum(cs[Lb:] * np.conj(cs[:-Lb]))) / (Lb / M)
frac_est = -slope / (2 * np.pi)
print(f"  delay: true {true_lag + frac:.3f} samples; integer lag {lag}, fractional {frac_est:.4f} -> {lag + frac_est:.4f} samples "
      f"({(lag+frac_est)/fs*1e6:.3f} µs at 2.4 MS/s)")
print(f"  uncorrected 0.3-sample skew at 2.4 MS/s = {0.3/fs*1e9:.0f} ns -> phase error {360*1e6*0.3/fs:.1f}° at a 1 MHz baseband offset")

print("=" * 78)
print("3. Mutual-coupling self-calibration, 8-element linear array")
N = 8
cdist = {1: 0.18 * np.exp(1j * 2.1), 2: 0.08 * np.exp(-1j * 0.4), 3: 0.04 * np.exp(1j * 1.9), 4: 0.025 * np.exp(-1j * 2.5),
         5: 0.017 * np.exp(1j * 0.3), 6: 0.012 * np.exp(-1j * 1.2), 7: 0.009 * np.exp(1j * 2.8)}


def simulate(edge_pert=0.0, noise=1e-4):
    t = 10 ** (1.0 * rng.standard_normal(N) / 20) * np.exp(1j * np.radians(25) * rng.standard_normal(N))
    r = 10 ** (1.0 * rng.standard_normal(N) / 20) * np.exp(1j * np.radians(25) * rng.standard_normal(N))
    M = np.zeros((N, N), complex)
    for m in range(N):
        for n in range(N):
            if m == n:
                continue
            c = cdist[abs(m - n)]
            if edge_pert and (m in (0, N - 1) or n in (0, N - 1)):
                c = c * (1 + edge_pert * (rng.standard_normal() + 1j * rng.standard_normal()) / np.sqrt(2))
            M[m, n] = t[m] * c * r[n] + noise * (rng.standard_normal() + 1j * rng.standard_normal())
    return t, r, M


def als(M, iters=300):
    tt = np.ones(N, complex); rr = np.ones(N, complex); cc = {k: 0.1 + 0j for k in range(1, N)}
    pairs = [(m, n) for m in range(N) for n in range(N) if m != n]
    for _ in range(iters):
        # update c (reciprocity + translation invariance: c depends on |m-n| only)
        for k in range(1, N):
            num = sum(np.conj(tt[m] * rr[n]) * M[m, n] for (m, n) in pairs if abs(m - n) == k)
            den = sum(abs(tt[m] * rr[n]) ** 2 for (m, n) in pairs if abs(m - n) == k)
            cc[k] = num / den
        for m in range(N):
            num = sum(np.conj(cc[abs(m - n)] * rr[n]) * M[m, n] for n in range(N) if n != m)
            den = sum(abs(cc[abs(m - n)] * rr[n]) ** 2 for n in range(N) if n != m)
            tt[m] = num / den
        for n in range(N):
            num = sum(np.conj(tt[m] * cc[abs(m - n)]) * M[m, n] for m in range(N) if m != n)
            den = sum(abs(tt[m] * cc[abs(m - n)]) ** 2 for m in range(N) if m != n)
            rr[n] = num / den
        s = rr[0]
        rr /= s; tt *= s
    return tt, rr


for edge in (0.0, 0.1, 0.3):
    res_amp, res_ph, parity = [], [], 0
    for trial in range(20):
        t, r, M = simulate(edge_pert=edge)
        tt, rr = als(M)
        rel = rr / (r / r[0])
        # parity ambiguity check: compare with alternating sign
        alt = (-1.0) ** np.arange(N)
        if np.mean(np.abs(np.angle(rel * alt))) < np.mean(np.abs(np.angle(rel))):
            parity += 1
            rel = rel * alt
        res_amp.append(np.std(20 * np.log10(np.abs(rel))))
        res_ph.append(np.degrees(np.std(np.angle(rel))))
    print(f"  edge-coupling perturbation {edge:.1f}: receive-channel residual {np.mean(res_amp):.3f} dB / {np.mean(res_ph):.2f}° rms "
          f"(true errors 1 dB / 25°); parity-flipped solutions {parity}/20")
# demonstrate the gauge: M is invariant under t_m -> t_m (-1)^m, r_n -> r_n (-1)^n, c_k -> c_k (-1)^k
t, r, M = simulate()
alt = (-1.0) ** np.arange(N)
M2 = np.zeros_like(M)
for m in range(N):
    for n in range(N):
        if m != n:
            M2[m, n] = (t[m] * alt[m]) * (cdist[abs(m - n)] * (-1) ** abs(m - n)) * (r[n] * alt[n])
print(f"  gauge check: max |M(t,r,c) - M(t(-1)^m, r(-1)^n, c(-1)^k)| (noise-free) = "
      f"{np.max(np.abs(M2 - np.array([[t[m]*cdist[abs(m-n)]*r[n] if m!=n else 0 for n in range(N)] for m in range(N)]))):.1e}")

print("=" * 78)
print("4. Calibration accuracy needed for a sidelobe floor 10 dB below design (uncorrelated residuals)")
for N, sll, eta in ((8, -25, 0.90), (16, -30, 0.853), (64, -30, 0.855), (64, -40, 0.769)):
    budget = N * eta * 10 ** ((sll - 10) / 10)  # sigma_a^2 + sigma_phi^2
    sig = np.sqrt(budget / 2)
    print(f"  N={N:2d}, design {sll} dB (η={eta}): σa²+σφ² ≤ {budget:.4f} -> equal split σa = {20*np.log10(1+sig):.2f} dB, σφ = {np.degrees(sig):.2f}°")
print("done")
