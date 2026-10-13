#!/usr/bin/env python3
"""Verification for kb/00-math-foundations/kalman-filter-and-state-estimation.md

 1. KF of a random constant == batch least squares (estimate and covariance).
 2. Constant-velocity tracker with DWNA process noise: NEES (MC) and NIS consistency against
    chi-square 95 % bands; innovation whiteness; mis-tuned Q (x0.01, x100) detected.
 3. Joseph form gives the true covariance for a suboptimal gain; the short form does not.
 4. Steady-state Riccati (DARE) gains vs Kalata tracking-index closed forms (alpha-beta, alpha);
    alpha-beta stability triangle; Benedict-Bordner relation compared; alpha-beta-gamma gains
    from DARE and the relation checked.
 5. CWNA vs DWNA Q matrices; DWNA q from manoeuvre acceleration.
 6. Complementary-filter property of the steady-state baro+accel filter: noiseless, consistent
    inputs are reproduced exactly; baro path is low-pass, accel path high-pass; crossover.
 7. 1-D rocket: truth with thrust + drag; accel (bias + noise) as control input, baro altitude
    measurement; state [h, v, b]. Compare KF vs baro-EMA-difference vs accel dead-reckoning;
    apogee-time error; NEES over MC runs.
 8. EKF vs UKF: coast-phase ballistic-coefficient estimation from baro altitude (nonlinear drag);
    apogee prediction; NEES.
Run: python3 tools/verify/est_kalman.py   (about 30-60 s)
"""
import numpy as np
from scipy import linalg, stats, signal

ok_all = True
rng = np.random.default_rng(7)


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel and want != 0 else 1.0)
    ok = err <= tol
    ok_all &= bool(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol}{' rel' if rel else ''})")


def check_true(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


def kf_step(x, P, z, F, Q, H, R, u=None, B=None):
    xp = F @ x + (B @ u if B is not None else 0)
    Pp = F @ P @ F.T + Q
    nu = z - H @ xp
    S = H @ Pp @ H.T + R
    K = Pp @ H.T @ np.linalg.inv(S)
    xn = xp + K @ nu
    IKH = np.eye(len(x)) - K @ H
    Pn = IKH @ Pp @ IKH.T + K @ R @ K.T          # Joseph form
    return xn, Pn, nu, S, K


print("== 1. KF of a random constant == batch LS ==")
zc = 3.0 + 1.5 * rng.standard_normal(40)
x = np.array([0.0]); P = np.array([[1e8]])
for zk in zc:
    x, P, *_ = kf_step(x, P, np.array([zk]), np.eye(1), np.zeros((1, 1)), np.eye(1), np.array([[2.25]]))
check("KF estimate = sample mean", abs(x[0] - zc.mean()), 0.0, 1e-6)
check("KF variance = sigma^2/N", P[0, 0], 2.25 / 40, 1e-6, rel=True)

print("\n== 2. CV tracker, DWNA: NEES / NIS consistency ==")
T, sw, sv = 0.1, 2.0, 5.0                       # 10 Hz, accel std 2 m/s^2, position noise 5 m
F = np.array([[1, T], [0, 1]])
G = np.array([[T ** 2 / 2], [T]])
Qd = G @ G.T * sw ** 2
H = np.array([[1.0, 0.0]])
R = np.array([[sv ** 2]])
Kst, M = 200, 100


def run_cv(Qf, Mruns=M, seed=0):
    """Vectorised over Monte-Carlo runs (the filter's P is the same for every run)."""
    r = np.random.default_rng(seed)
    xt = np.tile([0.0, 50.0], (Mruns, 1))
    x = np.column_stack([r.normal(0, 10, Mruns), 50 + r.normal(0, 5, Mruns)]); P = np.diag([100.0, 25.0])
    nees = np.zeros((Mruns, Kst)); nis = np.zeros((Mruns, Kst)); innov = np.zeros((Mruns, Kst))
    for k in range(Kst):
        xt = xt @ F.T + G.ravel()[None, :] * sw * r.standard_normal((Mruns, 1))
        z = xt[:, 0] + sv * r.standard_normal(Mruns)
        xp = x @ F.T; Pp = F @ P @ F.T + Qf
        S = Pp[0, 0] + R[0, 0]; Kg = Pp[:, 0] / S
        nu = z - xp[:, 0]
        x = xp + np.outer(nu, Kg)
        IKH = np.eye(2) - np.outer(Kg, [1.0, 0.0]); P = IKH @ Pp @ IKH.T + np.outer(Kg, Kg) * R[0, 0]
        e = xt - x
        nees[:, k] = np.einsum('mi,ij,mj->m', e, np.linalg.inv(P), e)
        nis[:, k] = nu ** 2 / S
        innov[:, k] = nu / np.sqrt(S)
    return nees, nis, innov


M = 1000
nees, nis, innov = run_cv(Qd, Mruns=M)
lo2, hi2 = stats.chi2.ppf([0.025, 0.975], 2 * M) / M
lo1, hi1 = stats.chi2.ppf([0.025, 0.975], 1 * M) / M
anees = nees.mean(axis=0); anis = nis.mean(axis=0)
print(f"    95% band for run-averaged NEES (n=2, M={M}): [{lo2:.3f}, {hi2:.3f}];  NIS (n=1): [{lo1:.3f}, {hi1:.3f}]")
check("time-and-run average NEES ~ n = 2", anees.mean(), 2.0, 0.03, rel=True)
check("time-and-run average NIS ~ m = 1", anis.mean(), 1.0, 0.03, rel=True)
frac_in = np.mean((anees > lo2) & (anees < hi2))
check("fraction of time steps with run-averaged NEES in 95% band", frac_in, 0.95, 0.06)
# single-run test (what you can do on real data, no truth): time-averaged NIS of ONE run
lo_t, hi_t = stats.chi2.ppf([0.025, 0.975], Kst) / Kst
frac_run_ok = np.mean((nis.mean(axis=1) > lo_t) & (nis.mean(axis=1) < hi_t))
check("single-run time-averaged NIS inside its 95% band (fraction of runs)", frac_run_ok, 0.95, 0.03)
# innovation whiteness: lag-1 normalised autocorrelation, per run, averaged
rho1 = np.mean(np.sum(innov[:, 1:] * innov[:, :-1], axis=1) / np.sum(innov ** 2, axis=1))
check("innovation lag-1 autocorrelation ~ 0", rho1, 0.0, 3 / np.sqrt(Kst * M))
for fac, label in ((0.01, "Q x 0.01 (overconfident)"), (100.0, "Q x 100 (conservative)")):
    ne, ni, inn = run_cv(Qd * fac, Mruns=300, seed=1)
    r1 = np.mean(np.sum(inn[:, 1:] * inn[:, :-1], axis=1) / np.sum(inn ** 2, axis=1))
    print(f"    {label}: avg NEES {ne[:, 50:].mean():.2f}, avg NIS {ni[:, 50:].mean():.2f}, innovation lag-1 corr {r1:+.3f}")
    if fac < 1:
        check_true(f"{label}: NEES far above n (> 5)", ne[:, 50:].mean() > 5)
        check_true(f"{label}: innovations positively correlated (> 0.1) -- visible without truth", r1 > 0.1)
    else:
        check_true(f"{label}: NEES below band (< 1.5)", ne[:, 50:].mean() < 1.5)
        check_true(f"{label}: innovations negatively correlated (< -0.05)", r1 < -0.05)

print("\n== 3. Joseph form vs short form for a suboptimal gain ==")
Pp = np.array([[30.0, 8.0], [8.0, 6.0]])
Ksub = np.array([[0.3], [0.05]])               # not the optimal gain
IKH = np.eye(2) - Ksub @ H
P_jos = IKH @ Pp @ IKH.T + Ksub @ R @ Ksub.T
P_short = IKH @ Pp
xe = rng.multivariate_normal([0, 0], Pp, 400000)
vn = sv * rng.standard_normal(400000)
e_post = xe - (Ksub @ (xe @ H.T + vn[:, None]).T).T
P_mc = np.cov(e_post.T)
check("Joseph form = MC covariance (P11)", P_jos[0, 0], P_mc[0, 0], 0.01, rel=True)
check_true("short form (I-KH)P is wrong for suboptimal K (P11 differs by > 10 %)",
           abs(P_short[0, 0] - P_mc[0, 0]) / P_mc[0, 0] > 0.10)

print("\n== 4. steady-state gains: DARE vs Kalata closed forms ==")


def ss_gain(Fm, Qm, Hm, Rm):
    Pp = linalg.solve_discrete_are(Fm.T, Hm.T, Qm, Rm)        # prediction covariance
    K = Pp @ Hm.T @ np.linalg.inv(Hm @ Pp @ Hm.T + Rm)
    return K, Pp


for lam in (0.05, 0.5, 2.0):
    swl = lam * sv / T ** 2
    K, _ = ss_gain(F, G @ G.T * swl ** 2, H, R)
    a_d, b_d = K[0, 0], K[1, 0] * T
    r_ = (4 + lam - np.sqrt(8 * lam + lam ** 2)) / 4
    a_k = 1 - r_ ** 2
    b_k = 2 * (2 - a_k) - 4 * np.sqrt(1 - a_k)
    check(f"lambda={lam}: alpha (DARE) vs Kalata", a_d, a_k, 1e-8)
    check(f"lambda={lam}: beta (DARE) vs 2(2-a)-4sqrt(1-a)", b_d, b_k, 1e-8)
    check(f"lambda={lam}: tracking index identity lambda^2 = beta^2/(1-alpha)", b_d ** 2 / (1 - a_d), lam ** 2, 1e-8, rel=True)
    if lam == 0.5:
        a05, b05 = a_d, b_d
        bb = a_d ** 2 / (2 - a_d)
        print(f"    lambda 0.5: alpha {a_d:.4f}, beta {b_d:.4f}; Benedict-Bordner beta for same alpha = {bb:.4f}")
# alpha filter (random-walk position, measurement of position)
for lam in (0.1, 1.0):
    # random-walk position, per-step process variance q; steady state alpha^2/(1-alpha) = q/r
    q_rw = (lam * sv) ** 2
    Ka, _ = ss_gain(np.eye(1), np.array([[q_rw]]), np.eye(1), R)
    check(f"alpha filter: alpha^2/(1-alpha) = q/r (lambda={lam})", Ka[0, 0] ** 2 / (1 - Ka[0, 0]), lam ** 2, 1e-8, rel=True)
    check(f"alpha filter: alpha = (-l^2+sqrt(l^4+4 l^2))/2 with l^2 = q/r", Ka[0, 0], (-lam ** 2 + np.sqrt(lam ** 4 + 4 * lam ** 2)) / 2, 1e-8)
    # Kalata/Wikipedia form uses Lambda = sigma_w T^2/sigma_v with step std sigma_w T^2/2  (q/r = Lambda^2/4)
    Lam = 2 * lam
    check(f"alpha filter: Kalata form (-L^2+sqrt(L^4+16L^2))/8 with L = 2 l", Ka[0, 0], (-Lam ** 2 + np.sqrt(Lam ** 4 + 16 * Lam ** 2)) / 8, 1e-8)
# stability triangle of alpha-beta: char poly of (I-KH)F
for (al, be, want) in ((0.5, 0.2, True), (1.5, 0.9, True), (1.5, 1.2, False), (0.5, 3.1, False)):
    Kab = np.array([[al], [be / T]])
    eig = np.abs(np.linalg.eigvals((np.eye(2) - Kab @ H) @ F))
    stable = np.all(eig < 1)
    tri = (0 < al < 2) and (0 < be < 4 - 2 * al)
    check_true(f"alpha={al}, beta={be}: eigen-stable={stable} == triangle={tri} == expected {want}", stable == tri == want)
# alpha-beta-gamma: CA model with DWPA (piecewise-constant acceleration increment)
F3 = np.array([[1, T, T ** 2 / 2], [0, 1, T], [0, 0, 1]])
G3 = np.array([[T ** 2 / 2], [T], [1.0]])
H3 = np.array([[1.0, 0, 0]])
for lam in (0.1, 1.0):
    sj = lam * sv / T ** 2
    K3, _ = ss_gain(F3, G3 @ G3.T * sj ** 2, H3, R)
    a3, b3, g3 = K3[0, 0], K3[1, 0] * T, K3[2, 0] * 2 * T ** 2
    print(f"    alpha-beta-gamma lambda={lam}: alpha {a3:.4f} beta {b3:.4f} gamma {g3:.4f}; beta^2/(2 alpha) = {b3**2/(2*a3):.4f}")
    # with K = [alpha, beta/T, gamma/(2T^2)] the DARE gains satisfy gamma = beta^2/alpha;
    # writing the third gain as gamma'/T^2 (gamma' = gamma/2) this is gamma' = beta^2/(2 alpha)
    check(f"abg lambda={lam}: gamma = beta^2/alpha  (K3 = gamma/(2T^2))", g3, b3 ** 2 / a3, 1e-6, rel=True)
    check(f"abg lambda={lam}: tracking index lambda^2 = gamma^2/(4(1-alpha))", g3 ** 2 / (4 * (1 - a3)), lam ** 2, 1e-6, rel=True)

print("\n== 5. CWNA vs DWNA ==")
qt = 4.0
Qc = qt * np.array([[T ** 3 / 3, T ** 2 / 2], [T ** 2 / 2, T]])
# exact discretisation of continuous white acceleration via Van Loan
A = np.array([[0, 1], [0, 0]]); Lc = np.array([[0], [1]])
Mvl = np.block([[-A, Lc @ Lc.T * qt], [np.zeros((2, 2)), A.T]]) * T
EM = linalg.expm(Mvl)
Qvl = EM[2:, 2:].T @ EM[:2, 2:]
check("Van Loan Q = CWNA closed form (max err)", np.max(np.abs(Qvl - Qc)), 0.0, 1e-12)
# DWNA with sigma_w^2 = qt/T has the same velocity variance per step as CWNA
Qdw = G @ G.T * (qt / T)
check("DWNA(sigma_w^2 = q/T) Q22 = CWNA Q22 = qT", Qdw[1, 1], Qc[1, 1], 1e-12)
check("DWNA Q11/CWNA Q11 = 3/4 (different position term)", Qdw[0, 0] / Qc[0, 0], 0.75, 1e-12)

print("\n== 6. complementary-filter property (baro + accel) ==")
Tb = 0.01
Fb = np.array([[1, Tb], [0, 1]]); Bb = np.array([[Tb ** 2 / 2], [Tb]]); Hb = np.array([[1.0, 0]])
sa, sb = 0.1, 0.5                                # accel noise (m/s^2), baro noise (m)
Qb = Bb @ Bb.T * sa ** 2
Rb = np.array([[sb ** 2]])
Kb, _ = ss_gain(Fb, Qb, Hb, Rb)
# noiseless consistent data: h(t) arbitrary smooth, a = h''
tt = np.arange(0, 20, Tb)
htrue = 50 * np.sin(0.3 * tt) + 2 * tt ** 1.5
vtrue = 15 * np.cos(0.3 * tt) + 3 * np.sqrt(tt)
# discrete-consistent acceleration: choose a_k so that the discrete model reproduces h exactly
# h[k+1] = h[k] + T v[k] + T^2/2 a[k], v[k+1] = v[k] + T a[k]  -> generate h, v from a
a_in = -4.5 * np.sin(0.3 * tt) + 1.5 / np.sqrt(tt + 1e-3)
hk = np.zeros_like(tt); vk = np.zeros_like(tt); hk[0], vk[0] = 0.0, 15.0
for k in range(len(tt) - 1):
    hk[k + 1] = hk[k] + Tb * vk[k] + Tb ** 2 / 2 * a_in[k]
    vk[k + 1] = vk[k] + Tb * a_in[k]
x = np.array([hk[0], vk[0]])
err = []
for k in range(len(tt) - 1):
    xp = Fb @ x + (Bb * a_in[k]).ravel()
    x = xp + (Kb @ (np.array([hk[k + 1]]) - Hb @ xp)).ravel()
    err.append(x - np.array([hk[k + 1], vk[k + 1]]))
check("steady-state fused filter reproduces noiseless truth (max |h err|)", np.max(np.abs(np.array(err)[:, 0])), 0.0, 1e-8)
# transfer functions: baro -> h_hat and (accel as h'') -> h_hat sum to 1 (complementary)
Acl = (np.eye(2) - Kb @ Hb) @ Fb
# x[k+1] = Acl x[k] + (I-KH) B a[k] + K z[k+1]
w = np.logspace(-4, np.log10(np.pi * 0.99), 2000)
zz = np.exp(1j * w)
Hbaro = np.array([(np.array([[1.0, 0]]) @ np.linalg.solve(z * np.eye(2) - Acl, Kb * z))[0, 0] for z in zz])
Bacc = (np.eye(2) - Kb @ Hb) @ Bb
Hacc = np.array([(np.array([[1.0, 0]]) @ np.linalg.solve(z * np.eye(2) - Acl, Bacc))[0, 0] for z in zz])
# double integrator from a to h in the same discretisation: h(z)/a(z) = T^2 (z+1) / (2 (z-1)^2)
Dint = Tb ** 2 * (zz + 1) / (2 * (zz - 1) ** 2)
comp = Hbaro + Hacc / Dint
check("complementary: H_baro + H_acc / D_int = 1 (max dev)", np.max(np.abs(comp - 1)), 0.0, 1e-8)
fcross = w[np.argmin(np.abs(np.abs(Hbaro) - np.abs(1 - Hbaro)))] / (2 * np.pi * Tb)
print(f"    steady-state gains K = [{Kb[0,0]:.5f}, {Kb[1,0]:.4f}] ; |H_baro| = |1-H_baro| crossover ~ {fcross:.3f} Hz")
# continuous-time analogue: accel PSD q = sa^2 T (m^2/s^3), baro PSD r = sb^2 T (m^2 s);
# steady-state 2nd-order complementary filter has omega_n = (q/r)^(1/4), zeta = 1/sqrt(2)
wn_c = (sa ** 2 * Tb / (sb ** 2 * Tb)) ** 0.25
print(f"    continuous-limit natural frequency (q/r)^(1/4) = {wn_c:.4f} rad/s = {wn_c/2/np.pi:.4f} Hz")
# |H_L| = |1 - H_L| for H_L = (2 z wn s + wn^2)/(s^2 + 2 z wn s + wn^2), zeta = 1/sqrt2 -> w = wn sqrt(1 + sqrt2)
check("crossover |H_baro| = |H_accel path| at wn*sqrt(1+sqrt2) [Hz]", fcross, wn_c * np.sqrt(1 + np.sqrt(2)) / (2 * np.pi), 0.02, rel=True)
Kc1 = np.sqrt(2) * wn_c * Tb; Kc2 = wn_c ** 2 * Tb
check("K1 ~ sqrt(2) wn T (continuous-limit gain)", Kb[0, 0], Kc1, 0.05, rel=True)
check("K2 ~ wn^2 T", Kb[1, 0], Kc2, 0.05, rel=True)

print("\n== 7. 1-D rocket: baro + accelerometer fusion ==")
dt_true = 0.001
fs_imu, fs_baro = 100.0, 50.0
g = 9.80665
tb_end, a_boost = 2.5, 60.0                      # net 60 m/s^2 above gravity for 2.5 s
kdrag = 0.0012                                   # 1/m, drag decel = k v|v|


def truth():
    ts = np.arange(0, 22, dt_true)
    h = np.zeros_like(ts); v = np.zeros_like(ts); a = np.zeros_like(ts)
    for i in range(len(ts) - 1):
        thrust = a_boost + g if ts[i] < tb_end else 0.0
        a[i] = thrust - g - kdrag * v[i] * abs(v[i])
        v[i + 1] = v[i] + a[i] * dt_true
        h[i + 1] = h[i] + v[i] * dt_true + 0.5 * a[i] * dt_true ** 2
    a[-1] = a[-2]
    return ts, h, v, a


ts, ht, vt, at = truth()
i_apo = np.argmax(ht)
t_apo, h_apo = ts[i_apo], ht[i_apo]
print(f"    truth: burnout v = {vt[int(tb_end/dt_true)]:.1f} m/s, apogee {h_apo:.1f} m at t = {t_apo:.3f} s")
T7 = 1 / fs_imu
F7 = np.array([[1, T7, -T7 ** 2 / 2], [0, 1, -T7], [0, 0, 1]])
B7 = np.array([[T7 ** 2 / 2], [T7], [0]])
H7 = np.array([[1.0, 0, 0]])
sig_acc, bias_acc, sig_baro = 0.3, 0.4, 0.8
q_bias = 1e-4                                    # bias random-walk std per sqrt(s)
Q7 = B7 @ B7.T * sig_acc ** 2 + np.diag([0, 0, q_bias ** 2 * T7])
R7 = np.array([[sig_baro ** 2]])
idx = (np.arange(0, ts[-1], T7) / dt_true).round().astype(int)
idx = idx[idx < len(ts)]
t_s = ts[idx]


# accelerometer output per step: average acceleration over [t_{k-1}, t_k] (delta-velocity / T, what an
# IMU with an integrating anti-alias filter delivers) or a point sample at t_{k-1} (naive)
a_avg = np.array([np.mean(at[idx[k - 1]:idx[k]]) if k > 0 else at[0] for k in range(len(idx))])
a_pt = np.array([at[idx[k - 1]] if k > 0 else at[0] for k in range(len(idx))])


def run_rocket(seed, sensor="avg", baro_lag=0):
    r = np.random.default_rng(seed)
    a_used = a_avg if sensor == "avg" else a_pt
    f_meas = a_used + g + bias_acc + sig_acc * r.standard_normal(len(idx))   # specific force over step k-1 -> k
    hb = ht[np.maximum(idx - baro_lag * int(T7 / dt_true), 0)]   # baro_lag: stale samples (timestamp bug)
    baro = hb + sig_baro * r.standard_normal(len(idx))
    x = np.array([baro[0], 0.0, 0.0]); P = np.diag([sig_baro ** 2, 0.01, 1.0])
    xs = np.zeros((len(idx), 3)); Ps = np.zeros((len(idx), 3, 3))
    xs[0], Ps[0] = x, P
    nb = int(fs_imu / fs_baro)
    for k in range(1, len(idx)):
        u = np.array([f_meas[k] - g])            # remove gravity; bias stays in the state model
        xp = F7 @ x + (B7 @ u).ravel()
        Pp = F7 @ P @ F7.T + Q7
        if k % nb == 0:
            nu = baro[k] - xp[0]
            S = Pp[0, 0] + R7[0, 0]
            K = Pp[:, 0] / S
            x = xp + K * nu
            IKH = np.eye(3) - np.outer(K, H7)
            P = IKH @ Pp @ IKH.T + np.outer(K, K) * R7[0, 0]
        else:
            x, P = xp, Pp
        xs[k], Ps[k] = x, P
    # baro-only: EMA + differencing
    ema = np.zeros(len(idx)); ema[0] = baro[0]; al = 0.1
    for k in range(1, len(idx)):
        ema[k] = ema[k - 1] + al * (baro[k] - ema[k - 1])
    v_ema = np.gradient(ema, T7)
    # accel-only dead reckoning (no bias knowledge)
    v_dr = np.concatenate([[0.0], np.cumsum(f_meas[1:] - g) * T7])
    return xs, Ps, v_ema, v_dr


xs, Ps, v_ema, v_dr = run_rocket(11)
vtr = vt[idx]
rms_kf = np.sqrt(np.mean((xs[:, 1] - vtr) ** 2))
rms_ema = np.sqrt(np.mean((v_ema - vtr) ** 2))
err_dr_end = abs(v_dr[int(t_apo / T7)] - vtr[int(t_apo / T7)])


def zero_cross(tv, v):
    k = np.where((v[:-1] > 0) & (v[1:] <= 0))[0]
    k = k[tv[k] > tb_end + 1][0]
    return tv[k] + v[k] / (v[k] - v[k + 1]) * (tv[k + 1] - tv[k])


t_apo_kf = zero_cross(t_s, xs[:, 1])
t_apo_ema = zero_cross(t_s, v_ema)
t_apo_dr = zero_cross(t_s, v_dr)
print(f"    velocity RMS error: KF {rms_kf:.3f} m/s, baro EMA+diff {rms_ema:.2f} m/s; dead-reckoning error at apogee {err_dr_end:.2f} m/s")
print(f"    apogee-time error: KF {1e3*(t_apo_kf-t_apo):+.0f} ms, EMA {1e3*(t_apo_ema-t_apo):+.0f} ms, dead-reckoning {1e3*(t_apo_dr-t_apo):+.0f} ms")
print(f"    final bias estimate {xs[-1,2]:.3f} m/s^2 (true {bias_acc}), 1-sigma {np.sqrt(Ps[-1,2,2]):.3f}")
check_true("KF velocity RMS < 1/3 of baro-EMA-difference RMS", rms_kf < rms_ema / 3)
check("KF apogee-time error [s] small (|err| < 0.1 s)", abs(t_apo_kf - t_apo), 0.0, 0.1)
check("KF accelerometer-bias estimate within 3 sigma", abs(xs[-1, 2] - bias_acc) / np.sqrt(Ps[-1, 2, 2]), 0.0, 3.0)
check("dead-reckoning apogee-time error ~ bias * t_apo / g [s]", t_apo_dr - t_apo, bias_acc * t_apo / g, 0.2, rel=True)
# MC NEES: consistent with the delta-velocity sensor; point-sampled accel exposes a modelling error
Mr = 40
lo3, hi3 = stats.chi2.ppf([0.025, 0.975], 3 * Mr) / Mr
nees_mean = {}
for sensor, lag in (("avg", 0), ("pt", 0), ("avg", 2)):
    neesr = np.zeros((Mr, len(idx)))
    for m in range(Mr):
        xs_m, Ps_m, *_ = run_rocket(100 + m, sensor, lag)
        e = np.column_stack([xs_m[:, 0] - ht[idx], xs_m[:, 1] - vtr, xs_m[:, 2] - bias_acc])
        neesr[m] = np.einsum('ki,kij,kj->k', e, np.linalg.inv(Ps_m), e)
    avg = neesr[:, 200:].mean(axis=0)
    nees_mean[(sensor, lag)] = avg.mean()
    print(f"    rocket NEES, accel={sensor}, baro lag {lag} samples (n=3, M={Mr}): mean {avg.mean():.2f}, band [{lo3:.2f}, {hi3:.2f}], fraction of steps in band {np.mean((avg>lo3)&(avg<hi3)):.2f}")
check("rocket filter mean NEES ~ 3 (delta-v accelerometer model)", nees_mean[("avg", 0)], 3.0, 0.15, rel=True)
check_true("point-sampled accel at 100 Hz: still nearly consistent (NEES < 3.81)", nees_mean[("pt", 0)] < hi3)
check_true("baro 20 ms stale (timestamp bug): NEES inflated > 3x -> consistency test catches it", nees_mean[("avg", 2)] > 3 * nees_mean[("avg", 0)])

print("\n== 8. EKF vs UKF: coast-phase ballistic coefficient ==")
# state [h, v, k]; dv/dt = -g - k v|v|; measurement baro h; 50 Hz; start at burnout
T8 = 0.02
k_true = kdrag
i0 = int(tb_end / dt_true)
h0, v0 = ht[i0], vt[i0]
sub = int(T8 / dt_true)
idx8 = np.arange(i0, i_apo, sub)
sig_b8 = 0.8


def f8(x, dt=T8, n=4):
    h, v, k = x
    for _ in range(n):                           # RK sub-steps
        hdt = dt / n
        def d(hh, vv):
            return vv, -g - k * vv * abs(vv)
        k1 = d(h, v); k2 = d(h + hdt / 2 * k1[0], v + hdt / 2 * k1[1])
        k3 = d(h + hdt / 2 * k2[0], v + hdt / 2 * k2[1]); k4 = d(h + hdt * k3[0], v + hdt * k3[1])
        h = h + hdt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        v = v + hdt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
    return np.array([h, v, k])


def jac_f(x, eps=1e-6):
    J = np.zeros((3, 3))
    for i in range(3):
        d = np.zeros(3); d[i] = eps * max(1.0, abs(x[i]))
        J[:, i] = (f8(x + d) - f8(x - d)) / (2 * d[i])
    return J


Q8 = np.diag([1e-9, 1e-7, 1e-16])   # small: truth is deterministic (only integrator mismatch)
R8 = sig_b8 ** 2
x0m = np.array([h0, v0, 0.0006])
P0 = np.diag([1.0, 4.0, 0.0006 ** 2])


def ekf(z):
    x, P = x0m.copy(), P0.copy(); out = []; Pout = []
    for zk in z:
        Fj = jac_f(x); x = f8(x); P = Fj @ P @ Fj.T + Q8
        S = P[0, 0] + R8; K = P[:, 0] / S; x = x + K * (zk - x[0])
        IKH = np.eye(3) - np.outer(K, [1, 0, 0]); P = IKH @ P @ IKH.T + np.outer(K, K) * R8
        out.append(x.copy()); Pout.append(P.copy())
    return np.array(out), np.array(Pout)


def ukf(z, alpha=1.0, beta=2.0, kappa=0.0):
    n = 3; lam = alpha ** 2 * (n + kappa) - n
    Wm = np.full(2 * n + 1, 1 / (2 * (n + lam))); Wc = Wm.copy()
    Wm[0] = lam / (n + lam); Wc[0] = lam / (n + lam) + (1 - alpha ** 2 + beta)
    x, P = x0m.copy(), P0.copy(); out = []; Pout = []
    for zk in z:
        Ls = linalg.cholesky((n + lam) * P, lower=True)
        X = np.vstack([x, x + Ls.T, x - Ls.T])
        Xp = np.array([f8(xi) for xi in X])
        x = Wm @ Xp
        dX = Xp - x
        P = (Wc[:, None] * dX).T @ dX + Q8
        Ls = linalg.cholesky((n + lam) * P, lower=True)
        X = np.vstack([x, x + Ls.T, x - Ls.T])
        Zs = X[:, 0]
        zm = Wm @ Zs
        S = Wc @ (Zs - zm) ** 2 + R8
        Pxz = (Wc[:, None] * (X - x)).T @ (Zs - zm)
        K = Pxz / S
        x = x + K * (zk - zm)
        P = P - np.outer(K, K) * S
        out.append(x.copy()); Pout.append(P.copy())
    return np.array(out), np.array(Pout)


Mr8 = 30
res = {"EKF": [], "UKF": []}
nees8 = {"EKF": [], "UKF": []}
apo_pred = {"EKF": [], "UKF": []}


def predict_apogee(x):
    h, v, k = x
    # closed form for quadratic drag + gravity ascent: dh = ln(1 + k v^2 / g) / (2k)
    return h + np.log(1 + k * v ** 2 / g) / (2 * k)


for m in range(Mr8):
    r = np.random.default_rng(500 + m)
    z = ht[idx8[1:]] + sig_b8 * r.standard_normal(len(idx8) - 1)
    xt = np.column_stack([ht[idx8[1:]], vt[idx8[1:]], np.full(len(idx8) - 1, k_true)])
    for name, fn in (("EKF", ekf), ("UKF", ukf)):
        xe, Pe = fn(z)
        e = xe - xt
        res[name].append(e)
        nees8[name].append(np.einsum('ki,kij,kj->k', e, np.linalg.inv(Pe), e))
        kk = int(2.0 / T8)                       # 2 s after burnout
        apo_pred[name].append(predict_apogee(xe[kk]) - h_apo)
check("closed-form apogee from burnout state (truth k)", predict_apogee(np.array([h0, v0, k_true])), h_apo, 1.0)
for name in ("EKF", "UKF"):
    e = np.array(res[name])
    rms_k_end = np.sqrt(np.mean(e[:, -1, 2] ** 2))
    ne = np.array(nees8[name])[:, 50:].mean()
    ap = np.array(apo_pred[name])
    print(f"    {name}: k RMS error at apogee {rms_k_end:.2e} (true {k_true:.1e}); mean NEES {ne:.2f} (n=3); "
          f"apogee predicted 2 s after burnout: bias {ap.mean():+.2f} m, std {ap.std():.2f} m")
    check(f"{name}: final k error < 10 % of k", rms_k_end / k_true, 0.0, 0.10)
    check(f"{name}: mean NEES ~ n = 3 (consistent within 2-4)", ne, 3.0, 1.0)
    check(f"{name}: apogee prediction 2 s after burnout within 5 m rms", np.sqrt(np.mean(ap ** 2)), 0.0, 5.0)

print("\n== 9. worked-example numbers: alpha-beta lag, complementary design from datasheet ==")
lam9 = 2.0 * 0.1 ** 2 / 5.0
r9 = (4 + lam9 - np.sqrt(8 * lam9 + lam9 ** 2)) / 4
a9 = 1 - r9 ** 2
b9 = 2 * (2 - a9) - 4 * np.sqrt(1 - a9)
print(f"    lambda {lam9}: alpha {a9:.5f}, beta {b9:.6f}, beta/T {b9/0.1:.5f} 1/s")
# steady-state bias to a constant acceleration: predicted a T^2/beta, filtered (1-alpha) a T^2/beta
acc = 4.0
Kab = np.array([a9, b9 / 0.1])
xt = np.array([0.0, 0.0]); xe = np.array([0.0, 0.0])
for k in range(20000):
    xt = np.array([xt[0] + 0.1 * xt[1] + 0.5 * acc * 0.01, xt[1] + acc * 0.1])
    xp = F @ xe
    xe = xp + Kab * (xt[0] - xp[0])
lag_f = xt[0] - xe[0]
check("alpha-beta filtered lag to 4 m/s^2 = (1-alpha) a T^2/beta [m]", lag_f, (1 - a9) * acc * 0.01 / b9, 1e-6, rel=True)
xt_next = np.array([xt[0] + 0.1 * xt[1] + 0.5 * acc * 0.01, xt[1] + acc * 0.1])
check("alpha-beta predicted (one-step) lag = a T^2/beta [m]", xt_next[0] - (F @ xe)[0], acc * 0.01 / b9, 1e-6, rel=True)
print(f"    lag: filtered {lag_f:.2f} m, predicted {acc*0.01/b9:.2f} m")
# complementary design: ASD 150 ug/rtHz -> q = ASD^2/2 ; baro 0.5 m rms at 100 Hz -> r = sigma^2 T
asd = 150e-6 * 9.80665
q9 = asd ** 2 / 2
r9b = 0.5 ** 2 * 0.01
wn9 = (q9 / r9b) ** 0.25
print(f"    q_a = {q9:.3e} m^2/s^3, r_b = {r9b:.2e} m^2 s, wn = {wn9:.4f} rad/s = {wn9/2/np.pi:.4f} Hz")
check("datasheet complementary wn [rad/s]", wn9, 0.1442, 2e-3)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
