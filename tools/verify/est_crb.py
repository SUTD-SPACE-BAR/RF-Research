#!/usr/bin/env python3
"""Verification for kb/00-math-foundations/estimation-theory-ml-map-crb.md

Monte-Carlo checks of estimator properties against Cramer-Rao bounds (CRB):
 1. Sample mean: unbiased, variance sigma^2/N = CRB (efficient).
 2. Variance estimation: ML (1/N) is biased but has lower MSE than the unbiased (1/(N-1));
    CRB for sigma^2 is 2 sigma^4/N.
 3. Linear model / least squares: straight-line fit h = h0 + v t (barometric velocity) --
    covariance sigma^2 (H^T H)^-1, var(v) = 12 sigma^2 fs^2/(N(N^2-1)); WLS with unequal noise.
 4. Gaussian prior x Gaussian likelihood: MAP = MMSE = precision-weighted mean; posterior variance
    1/(1/s0^2 + N/s^2) -- the scalar Kalman update.
 5. Complex tone (A, w, phi unknown): ML (FFT + refinement) vs CRB for frequency 6/(SNR N(N^2-1)),
    phase (2N-1)/(SNR N(N+1)) referenced to n = 0 and 1/(2 N SNR) referenced to block centre,
    amplitude sigma^2/(2N); threshold effect at low SNR.
 6. Time delay: ML (fractional-delay correlation search) vs CRB 1/((2 pi B_rms)^2 2 SNR) for a
    Gaussian pulse; nuisance amplitude/phase decouple (FIM is block diagonal).
 7. Carrier-phase ranging: Fisher information with known carrier phase uses (f_c^2 + B_rms^2).
9. GNSS DOP for a 4-satellite geometry (MC); recursive LS = KF with F = I, Q = 0.
 8. Worked numbers: GPS C/A rms bandwidth in a +-1.023 MHz front end, pseudorange CRB at
    45 dB-Hz vs DLL formula; LoRa SF7/125 kHz preamble timing CRB; radar 10 MHz chirp.
Run: python3 tools/verify/est_crb.py
"""
import numpy as np
from scipy import optimize, integrate

ok_all = True
rng = np.random.default_rng(42)
C0 = 299792458.0


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel and want != 0 else 1.0)
    ok = err <= tol
    ok_all &= bool(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol}{' rel' if rel else ''})")


print("== 1. sample mean ==")
N, sig, mu = 25, 2.0, 3.0
M = 200000
X = mu + sig * rng.standard_normal((M, N))
m_hat = X.mean(axis=1)
check("bias of sample mean", m_hat.mean() - mu, 0.0, 0.003)
check("var(sample mean)/CRB (sigma^2/N)", m_hat.var() / (sig ** 2 / N), 1.0, 0.01, rel=True)

print("\n== 2. variance estimation: bias vs MSE ==")
N2 = 10
X2 = sig * rng.standard_normal((M, N2))
dev = X2 - X2.mean(axis=1, keepdims=True)
v_ml = (dev ** 2).sum(axis=1) / N2
v_ub = (dev ** 2).sum(axis=1) / (N2 - 1)
check("E[ML variance] = (N-1)/N sigma^2", v_ml.mean(), (N2 - 1) / N2 * sig ** 2, 0.01, rel=True)
check("E[unbiased variance] = sigma^2", v_ub.mean(), sig ** 2, 0.01, rel=True)
mse_ml = np.mean((v_ml - sig ** 2) ** 2)
mse_ub = np.mean((v_ub - sig ** 2) ** 2)
check("MSE(unbiased) = 2 sigma^4/(N-1)", mse_ub, 2 * sig ** 4 / (N2 - 1), 0.02, rel=True)
check("MSE(ML) = (2N-1) sigma^4/N^2", mse_ml, (2 * N2 - 1) * sig ** 4 / N2 ** 2, 0.02, rel=True)
check("MSE(ML) < MSE(unbiased) (ratio)", mse_ml / mse_ub, (2 * N2 - 1) * (N2 - 1) / (2 * N2 ** 2), 0.02, rel=True)
print(f"    CRB for sigma^2 with known mean = 2 sigma^4/N = {2*sig**4/N2:.3f}; unbiased (unknown mean) MSE {mse_ub:.3f}")

print("\n== 3. least squares: line fit (baro velocity) ==")
fs, sig_h, Nl = 100.0, 0.5, 50
t = np.arange(Nl) / fs
H = np.column_stack([np.ones(Nl), t])
cov_theory = sig_h ** 2 * np.linalg.inv(H.T @ H)
var_v_formula = 12 * sig_h ** 2 * fs ** 2 / (Nl * (Nl ** 2 - 1))
check("var(v) closed form vs sigma^2 (H^T H)^-1", cov_theory[1, 1], var_v_formula, 1e-9, rel=True)
h_true = 1000 + 30 * t
Y = h_true + sig_h * rng.standard_normal((100000, Nl))
th = np.linalg.lstsq(H, Y.T, rcond=None)[0]
check("MC var(v_hat) / formula", th[1].var() / var_v_formula, 1.0, 0.02, rel=True)
check("sigma_v for sigma_h = 0.5 m, 100 Hz, N = 50 [m/s]", np.sqrt(var_v_formula), 0.49002, 1e-4)
check("sigma_v for N = 100 (1 s window) [m/s]", np.sqrt(12 * sig_h ** 2 * fs ** 2 / (100 * (100 ** 2 - 1))), 0.17321, 1e-4)
# WLS: half the samples have 4x the noise std
sig_vec = np.where(np.arange(Nl) % 2 == 0, 0.5, 2.0)
W = np.diag(1 / sig_vec ** 2)
cov_wls = np.linalg.inv(H.T @ W @ H)
Hp = np.linalg.pinv(H)
cov_ols = Hp @ np.diag(sig_vec ** 2) @ Hp.T
Yw = h_true + sig_vec * rng.standard_normal((100000, Nl))
Hw = H / sig_vec[:, None]
th_w = np.linalg.lstsq(Hw, (Yw / sig_vec).T, rcond=None)[0]
check("WLS MC var(v) / (H^T W H)^-1", th_w[1].var() / cov_wls[1, 1], 1.0, 0.02, rel=True)
print(f"    WLS vs OLS var(v) ratio = {cov_wls[1,1]/cov_ols[1,1]:.3f} (WLS better)")
check("WLS better than OLS (ratio < 1)", float(cov_wls[1, 1] < cov_ols[1, 1]), 1.0, 0)

print("\n== 4. Gaussian MAP/MMSE (scalar Kalman update) ==")
m0, s0, s_meas, Nb = 100.0, 5.0, 2.0, 4
theta = m0 + s0 * rng.standard_normal(400000)
Z = theta[:, None] + s_meas * rng.standard_normal((400000, Nb))
post_var = 1 / (1 / s0 ** 2 + Nb / s_meas ** 2)
post_mean = post_var * (m0 / s0 ** 2 + Z.sum(axis=1) / s_meas ** 2)
check("Bayesian MSE of posterior mean = posterior variance", np.mean((post_mean - theta) ** 2), post_var, 0.01, rel=True)
ml = Z.mean(axis=1)
check("ML (ignores prior) MSE = s^2/N > posterior var", np.mean((ml - theta) ** 2), s_meas ** 2 / Nb, 0.01, rel=True)
# Kalman-gain form
K = s0 ** 2 / (s0 ** 2 + s_meas ** 2 / Nb)
check("gain form: m0 + K(zbar - m0) equals precision form", np.max(np.abs(m0 + K * (ml - m0) - post_mean)), 0.0, 1e-9)
check("posterior variance (1-K) s0^2", (1 - K) * s0 ** 2, post_var, 1e-12)
print(f"    posterior std {np.sqrt(post_var):.4f} (prior {s0}, data-only {s_meas/np.sqrt(Nb):.4f})")

print("\n== 5. complex tone: frequency / phase / amplitude CRB ==")
Nt = 64
nn = np.arange(Nt)


def tone_ml(x, nfft=4096):
    Xf = np.fft.fft(x, nfft)
    k = np.argmax(np.abs(Xf))
    w0 = 2 * np.pi * k / nfft
    f = lambda w: -np.abs(np.sum(x * np.exp(-1j * w * nn)))
    res = optimize.minimize_scalar(f, bounds=(w0 - 2 * np.pi / nfft, w0 + 2 * np.pi / nfft), method='bounded',
                                   options={'xatol': 1e-12})
    w = res.x
    c = np.sum(x * np.exp(-1j * w * nn)) / Nt
    return w, np.angle(c), np.abs(c)


def tone_mc(snr_db, trials, A=1.0, w_true=0.7, phi=0.4):
    snr = 10 ** (snr_db / 10)
    s2 = A ** 2 / snr
    ests = []
    for _ in range(trials):
        x = A * np.exp(1j * (w_true * nn + phi)) + np.sqrt(s2 / 2) * (rng.standard_normal(Nt) + 1j * rng.standard_normal(Nt))
        ests.append(tone_ml(x))
    e = np.array(ests)
    dw = e[:, 0] - w_true
    dphi = np.angle(np.exp(1j * (e[:, 1] - phi)))
    dA = e[:, 2] - A
    return snr, s2, dw, dphi, dA


snr, s2, dw, dphi, dA = tone_mc(10, 4000)
crb_w = 6 / (snr * Nt * (Nt ** 2 - 1))
crb_phi0 = (2 * Nt - 1) / (snr * Nt * (Nt + 1))
crb_A = s2 / (2 * Nt)
check("freq MSE / CRB at 10 dB, N = 64", np.mean(dw ** 2) / crb_w, 1.0, 0.08, rel=True)
check("phase(n=0) MSE / CRB (2N-1)/(SNR N(N+1))", np.mean(dphi ** 2) / crb_phi0, 1.0, 0.08, rel=True)
check("amplitude MSE / CRB sigma^2/(2N)", np.mean(dA ** 2) / crb_A, 1.0, 0.08, rel=True)
# phase referenced to block centre: phi_c = phi + w (N-1)/2
dphi_c = np.angle(np.exp(1j * (dphi + dw * (Nt - 1) / 2)))
check("phase(centre) MSE / CRB 1/(2 N SNR)", np.mean(dphi_c ** 2) / (1 / (2 * Nt * snr)), 1.0, 0.08, rel=True)
check("ratio phase CRB n=0 vs centre (=4(2N-1)N/(N+1)/2N ~ 4)", crb_phi0 / (1 / (2 * Nt * snr)), 2 * (2 * Nt - 1) / (Nt + 1), 1e-12)
# threshold effect
print("    threshold sweep (N = 64): SNR dB -> freq MSE/CRB")
ratios = {}
for sdb in (-12, -9, -6, -3, 0, 5):
    sn, _, dwi, _, _ = tone_mc(sdb, 1500)
    ratios[sdb] = np.mean(dwi ** 2) / (6 / (sn * Nt * (Nt ** 2 - 1)))
    print(f"      {sdb:4d} dB: {ratios[sdb]:.3g}")
check("above threshold (0 dB per sample, N=64): MSE/CRB ~ 1", ratios[0], 1.0, 0.15, rel=True)
check("below threshold (-12 dB per sample): MSE/CRB >> 1 (log10 ratio > 1)", float(np.log10(ratios[-12]) > 1), 1.0, 0)

print("\n== 6. time-delay estimation: Gaussian pulse ==")
Nd, fsd = 512, 1.0
tg = np.arange(Nd) - Nd / 2
sigp = 4.0                                      # pulse std in samples
s_pulse = np.exp(-tg ** 2 / (2 * sigp ** 2)).astype(complex)
S = np.fft.fft(s_pulse)
fk = np.fft.fftfreq(Nd)
# rms bandwidth (cycles/sample) of the sampled pulse
Brms = np.sqrt(np.sum(fk ** 2 * np.abs(S) ** 2) / np.sum(np.abs(S) ** 2))
check("Gaussian pulse B_rms = 1/(2 sqrt(2) pi sigma_t)  [1/sample]", Brms, 1 / (2 * np.sqrt(2) * np.pi * sigp), 1e-6, rel=True)


def shift(sig_f, tau):
    return np.fft.ifft(sig_f * np.exp(-2j * np.pi * fk * tau))


def delay_ml(x):
    Xf = np.fft.fft(x)
    corr = lambda tau: -np.abs(np.sum(Xf * np.conj(S) * np.exp(2j * np.pi * fk * tau)))
    c_int = np.fft.ifft(Xf * np.conj(S))
    k = np.argmax(np.abs(c_int))
    k = k if k < Nd / 2 else k - Nd
    r = optimize.minimize_scalar(corr, bounds=(k - 1, k + 1), method='bounded', options={'xatol': 1e-10})
    return r.x


tau0 = 3.37
x_clean = shift(S, tau0)
Es = np.sum(np.abs(s_pulse) ** 2)
dres = {}
for snr_db in (10.0, 13.0, 16.0, 20.0):
    snr_int = 10 ** (snr_db / 10)                  # integrated (matched-filter) SNR = |a|^2 E/sigma^2
    s2d = Es / snr_int
    errs = []
    for _ in range(3000):
        a = np.exp(1j * rng.uniform(0, 2 * np.pi))  # unknown carrier phase (nuisance)
        x = a * x_clean + np.sqrt(s2d / 2) * (rng.standard_normal(Nd) + 1j * rng.standard_normal(Nd))
        errs.append(delay_ml(x) - tau0)
    errs = np.array(errs)
    crb_tau = 1 / ((2 * np.pi * Brms) ** 2 * 2 * snr_int)
    outl = np.mean(np.abs(errs) > 6 * sigp)
    dres[snr_db] = (np.mean(errs ** 2) / crb_tau, outl)
    print(f"    integrated SNR {snr_db:.0f} dB: MSE/CRB = {dres[snr_db][0]:.3g}, outliers (|err| > 6 sigma_t) = {outl:.4f}, sqrt(CRB) = {np.sqrt(crb_tau):.4f} samples")
check("delay MSE / CRB at integrated SNR 20 dB", dres[20.0][0], 1.0, 0.08, rel=True)
check("delay MSE / CRB at integrated SNR 16 dB", dres[16.0][0], 1.0, 0.10, rel=True)
check("threshold: at 10 dB integrated SNR over 512 cells, MSE >> CRB (outliers > 1 %)", float(dres[10.0][1] > 0.01 and dres[10.0][0] > 10), 1.0, 0)
# FIM block structure for (tau, Re a, Im a): cross-terms vanish for a symmetric (real) pulse spectrum
ds = np.fft.ifft(S * (-2j * np.pi * fk))          # d/dtau of s(t - tau) at tau = 0 (= -s')
J_tau_phase = 2 * np.real(np.sum(np.conj(ds) * 1j * s_pulse))
J_tau_amp = 2 * np.real(np.sum(np.conj(ds) * s_pulse))
check("FIM cross-term delay x phase ~ 0 (symmetric spectrum)", abs(J_tau_phase) / np.sum(np.abs(ds) ** 2), 0.0, 1e-9)
check("FIM cross-term delay x amplitude ~ 0", abs(J_tau_amp) / np.sum(np.abs(ds) ** 2), 0.0, 1e-9)

print("\n== 7. carrier-phase ranging information ==")
# passband-equivalent: s(t-tau) e^{-j 2 pi fc tau}; with phase known, d/dtau adds -j 2 pi fc s
fc_norm = 0.2                                     # carrier in cycles/sample (illustrative)
ds_c = ds - 2j * np.pi * fc_norm * s_pulse
J_code = np.sum(np.abs(ds) ** 2)
J_carrier = np.sum(np.abs(ds_c) ** 2)
check("J(known phase)/J(unknown) = 1 + (fc/B_rms)^2", J_carrier / J_code, 1 + (fc_norm / Brms) ** 2, 1e-6, rel=True)

print("\n== 8. worked numbers: GNSS, LoRa, radar ==")
Rc = 1.023e6
num = integrate.quad(lambda f: f ** 2 * np.sinc(f / Rc) ** 2, -Rc, Rc, limit=200)[0]
den = integrate.quad(lambda f: np.sinc(f / Rc) ** 2, -Rc, Rc, limit=200)[0]
Brms_ca = np.sqrt(num / den)
check("GPS C/A B_rms in +-1.023 MHz front end [kHz]", Brms_ca / 1e3, 342.7, 0.5)
cn0 = 10 ** 4.5
Bn = 2.0
two_E_N0 = cn0 / Bn                                # 2E/N0 with T_eq = 1/(2 Bn)
sig_tau = 1 / (2 * np.pi * Brms_ca * np.sqrt(two_E_N0))
check("pseudorange CRB at 45 dB-Hz, Bn = 2 Hz [m]", sig_tau * C0, 1.106, 0.01)
d, Tco = 1.0, 1e-3
sig_dll_chips = np.sqrt(Bn * d / (2 * cn0) * (1 + 2 / (Tco * cn0 * (2 - d))))
check("DLL (d = 1, T = 1 ms) jitter [m] (KB formula)", sig_dll_chips * C0 / Rc, 1.70, 0.01)
print(f"    DLL/CRB ratio = {sig_dll_chips*C0/Rc/(sig_tau*C0):.2f} (wide correlator, band-limited)")
# LoRa: SF7, BW 125 kHz, 8 up-chirps preamble, chip-rate complex samples
BW = 125e3
Nchips = 8 * 2 ** 7
Brms_lora = BW / np.sqrt(12)
for snr_chip_db, want_m in ((-7.5, 69.2), (10.0, 9.24)):
    snr_int = Nchips * 10 ** (snr_chip_db / 10)
    st = 1 / (2 * np.pi * Brms_lora * np.sqrt(2 * snr_int))
    check(f"LoRa SF7 preamble timing CRB at {snr_chip_db} dB/chip -> range [m]", st * C0, want_m, 0.1)
# radar 10 MHz chirp, 20 dB: sigma_R = c/2 * 1/(2 pi B/sqrt12 sqrt(2 SNR))
Br = 10e6 / np.sqrt(12)
sr = C0 / 2 / (2 * np.pi * Br * np.sqrt(2 * 100))
check("radar 10 MHz chirp, 20 dB: range CRB [m] (11-radar ambiguity page: ~0.5 m class)", sr, 0.585, 0.005)

print("\n== 9. GNSS linearised LS: DOP for a 4-satellite geometry; RLS = KF with F=I, Q=0 ==")
els = np.radians([90, 30, 30, 30]); azs = np.radians([0, 0, 120, 240])
u = np.column_stack([np.cos(els) * np.sin(azs), np.cos(els) * np.cos(azs), np.sin(els)])   # ENU line of sight
Hg = np.column_stack([-u, np.ones(4)])
Dg = np.linalg.inv(Hg.T @ Hg)
hdop = np.sqrt(Dg[0, 0] + Dg[1, 1]); vdop = np.sqrt(Dg[2, 2]); tdop = np.sqrt(Dg[3, 3]); pdop = np.sqrt(np.trace(Dg[:3, :3]))
print(f"    HDOP {hdop:.3f}  VDOP {vdop:.3f}  PDOP {pdop:.3f}  TDOP {tdop:.3f}  GDOP {np.sqrt(np.trace(Dg)):.3f}")
# analytic: horizontal block of H^T H = 1.125 I -> HDOP = sqrt(2/1.125) = 4/3;
# vertical/clock block [[1.75, -2.5], [-2.5, 4]], det 0.75 -> VDOP = sqrt(4/0.75), TDOP = sqrt(1.75/0.75)
check("HDOP (zenith + 3 at 30 deg el, 120 deg apart) = 4/3", hdop, 4 / 3, 1e-9)
check("VDOP same geometry = 4/sqrt(3)", vdop, 4 / np.sqrt(3), 1e-9)
check("TDOP same geometry = sqrt(7/3)", tdop, np.sqrt(7 / 3), 1e-9)
# MC: position error std = DOP * sigma_UERE
sigU = 3.0
Zg = sigU * rng.standard_normal((200000, 4))
est = Zg @ np.linalg.pinv(Hg).T
check("MC vertical error std / (VDOP sigma_UERE)", est[:, 2].std() / (vdop * sigU), 1.0, 0.01, rel=True)
# recursive least squares on a constant = Kalman filter with F = I, Q = 0
zr = 5.0 + 2.0 * rng.standard_normal(50)
xh, P = 0.0, 1e9
for zk in zr:
    Kk = P / (P + 4.0)
    xh = xh + Kk * (zk - xh)
    P = (1 - Kk) * P
check("RLS (KF with Q=0) of a constant = batch mean", abs(xh - zr.mean()), 0.0, 1e-6)
check("RLS posterior variance = sigma^2/N", P, 4.0 / 50, 1e-6, rel=True)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
