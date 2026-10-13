#!/usr/bin/env python3
"""Verification for kb/11-radar/radar-tracking-monopulse-and-trackers.md

 1. Amplitude-comparison monopulse with Gaussian squinted beams: Delta/Sigma = tanh(4 ln2 theta
    theta_s/theta_b^2) (closed form), normalised slope k_m vs squint, sum-beam width, crossover loss;
    Monte-Carlo angle noise vs theta_3S/(k_m sqrt(2 SNR)); "10:1 beam splitting at 13 dB".
 2. Phase-comparison monopulse: Delta/Sigma = j tan(k d sin(theta)/2); MC vs the 2-element CRB.
 3. Sequential lobing / conical scan: modulation depth = monopulse slope; target amplitude
    fluctuation corrupts conical scan but not monopulse (MC).
 4. Split-gate (early-late) range discriminator on a triangular matched-filter output: S-curve
    (L-E)/(L+E) = 2 eps/T for |eps| < T/2.
 5. Polar -> Cartesian measurement covariance J R J^T vs MC; conversion bias r sigma_theta^2/2.
 6. Gating volume and expected false measurements; NN vs PDAF tracking in clutter (MC).
 7. Ground-station antenna pointing from GNSS telemetry: Gaussian-beam pointing loss
    12.04 (eps/theta3)^2 dB; latency compensation (raw vs extrapolated vs Kalman-predicted az/el)
    for a simulated rocket ascent; RSSI step-track (sequential lobing) accuracy.
 8. Worked numbers: DIY S-band 1.2 m dish (5.8 deg) monopulse accuracy at 15 dB; angular rate
    geometry v d/(d^2+h^2).
Run: python3 tools/verify/est_radar_tracking.py   (about 30 s)
"""
import numpy as np
from scipy import stats, optimize

ok_all = True
rng = np.random.default_rng(1234)
LN2 = np.log(2)


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


def vbeam(theta, tb=1.0):
    """Gaussian voltage pattern with half-power (3 dB) beamwidth tb."""
    return np.exp(-2 * LN2 * (theta / tb) ** 2)


print("== 1. amplitude-comparison monopulse ==")
tb = 1.0                      # individual beam 3 dB width (normalised)
th = np.linspace(-0.3, 0.3, 601)
for ts in (0.3, 0.4, 0.5):
    v1, v2 = vbeam(th - ts), vbeam(th + ts)
    ratio = (v1 - v2) / (v1 + v2)
    closed = np.tanh(4 * LN2 * th * ts / tb ** 2)
    check(f"squint {ts}: Delta/Sigma = tanh(4 ln2 theta theta_s/theta_b^2) (max err)", np.max(np.abs(ratio - closed)), 0.0, 1e-12)
# sum-beam 3 dB width and k_m for squint 0.4
ts = 0.4
f = lambda t: (vbeam(t - ts) + vbeam(t + ts)) / (2 * vbeam(ts)) - 1 / np.sqrt(2)
t3S = 2 * optimize.brentq(f, 0.01, 2.0)
k_slope = 4 * LN2 * ts / tb ** 2                       # d(Delta/Sigma)/d theta at 0, per unit of theta_b
km = k_slope * t3S                                      # per sum-beam beamwidth
cross_loss_db = -20 * np.log10(vbeam(ts))               # one-way gain loss on boresight vs beam peak
print(f"    squint 0.4 theta_b: sum-beam width {t3S:.4f} theta_b, k_m = {km:.4f} (per sum beamwidth), crossover loss {cross_loss_db:.2f} dB one-way")
check("crossover loss one-way 12.04 (theta_s/theta_b)^2 dB", cross_loss_db, 12.0412 * ts ** 2, 1e-3)
# numeric slope of Delta/Sigma at boresight vs closed form 4 ln2 theta_s/theta_b^2
hh = 1e-6
num_slope = (np.tanh(4 * LN2 * hh * ts) - np.tanh(-4 * LN2 * hh * ts)) / (2 * hh)
v1n = lambda t_: vbeam(t_ - ts); v2n = lambda t_: vbeam(t_ + ts)
num_slope2 = (((v1n(hh) - v2n(hh)) / (v1n(hh) + v2n(hh))) - ((v1n(-hh) - v2n(-hh)) / (v1n(-hh) + v2n(-hh)))) / (2 * hh)
check("boresight slope of Delta/Sigma = 4 ln2 theta_s/theta_b^2", num_slope2, k_slope, 1e-6, rel=True)
print("    Gaussian beams: squint/theta_b -> sum-beam width, k_m (per sum beamwidth), crossover loss (one-way):")
for tsq in (0.3, 0.4, 0.5, 0.6):
    fq = lambda t_: (vbeam(t_ - tsq) + vbeam(t_ + tsq)) / (2 * vbeam(tsq)) - 1 / np.sqrt(2)
    w3 = 2 * optimize.brentq(fq, 0.01, 3.0)
    print(f"      {tsq:.1f}: {w3:.3f} theta_b, k_m = {4*LN2*tsq*w3:.3f}, {12.0412*tsq**2:.2f} dB")
check("k_m at squint 0.4 (Gaussian beams, per sum-beam width)", km, 1.4435, 1e-3)
# optimum squint when Sigma is used on transmit and receive: sigma_theta ~ 1/(slope * |Sigma(0)|^2)
# FOM(theta_s) = theta_s * exp(-4 ln2 theta_s^2)  -> max at 1/sqrt(8 ln2)
fom = lambda q: q * np.exp(-4 * LN2 * q ** 2)
q_opt = optimize.minimize_scalar(lambda q: -fom(q), bounds=(0.1, 1.0), method='bounded').x
check("optimum squint (two-way Sigma) = 1/sqrt(8 ln2) theta_b", q_opt, 1 / np.sqrt(8 * LN2), 1e-4)
print(f"    FOM relative to optimum: 0.4 -> {20*np.log10(fom(0.4)/fom(q_opt)):+.2f} dB, 0.5 -> {20*np.log10(fom(0.5)/fom(q_opt)):+.2f} dB")
# MC angle noise at SNR_Sigma = 20 dB, target at 0.05
snr_db = 20.0
theta_t = 0.05
sig1, sig2 = vbeam(theta_t - ts), vbeam(theta_t + ts)
S_sig = (sig1 + sig2) / np.sqrt(2)
snr = 10 ** (snr_db / 10)
sigma_n = abs(S_sig) / np.sqrt(snr)                     # noise std (complex) per hybrid output
Mm = 200000
n1 = sigma_n / np.sqrt(2) * (rng.standard_normal(Mm) + 1j * rng.standard_normal(Mm))
n2 = sigma_n / np.sqrt(2) * (rng.standard_normal(Mm) + 1j * rng.standard_normal(Mm))
ph = np.exp(1j * rng.uniform(0, 2 * np.pi, Mm))        # unknown echo phase
x1, x2 = sig1 * ph + n1, sig2 * ph + n2
Sg = (x1 + x2) / np.sqrt(2); Dl = (x1 - x2) / np.sqrt(2)
r_meas = np.real(Dl / Sg)
theta_hat = np.arctanh(np.clip(r_meas, -0.999, 0.999)) / (4 * LN2 * ts)
sig_th = np.std(theta_hat)
pred = t3S / (km * np.sqrt(2 * snr))
check("monopulse angle noise / [theta_3S/(k_m sqrt(2 SNR))] at 20 dB", sig_th / pred, 1.0, 0.03, rel=True)
check("mean angle estimate unbiased (target 0.05)", np.mean(theta_hat), theta_t, 5e-4)
sp13 = 1 / (km * np.sqrt(2 * 10 ** 1.3))
print(f"    beam splitting at 13 dB: sigma/theta_3S = {sp13:.3f} (~1/{1/sp13:.1f})")
check("~10:1 beam splitting at 13 dB (here k_m = 1.44)", 1 / sp13, 10.0, 1.5)

print("\n== 2. phase-comparison monopulse ==")
lam = 1.0; d = 2.0 * lam; kk = 2 * np.pi / lam
thp = np.radians(np.linspace(-5, 5, 101))
a1, a2 = np.exp(1j * kk * d * np.sin(thp) / 2), np.exp(-1j * kk * d * np.sin(thp) / 2)
rat = (a1 - a2) / (a1 + a2)
check("Delta/Sigma = j tan(k d sin(theta)/2) (max err)", np.max(np.abs(rat - 1j * np.tan(kk * d * np.sin(thp) / 2))), 0.0, 1e-12)
snr_e = 10 ** (17 / 10)                                 # per-element SNR
th0 = np.radians(1.0)
s1 = np.exp(1j * kk * d * np.sin(th0) / 2); s2 = np.conj(s1)
e1 = np.sqrt(1 / snr_e / 2) * (rng.standard_normal(Mm) + 1j * rng.standard_normal(Mm))
e2 = np.sqrt(1 / snr_e / 2) * (rng.standard_normal(Mm) + 1j * rng.standard_normal(Mm))
phd = np.angle((s1 * ph + e1) * np.conj(s2 * ph + e2))
th_hat = np.arcsin(phd / (kk * d))
crb_u = 1 / (snr_e * (kk * d) ** 2)                      # 12-phased-arrays CRB for N = 2, K = 1
check("phase-monopulse var(u) / CRB (N=2: 1/(SNR_e (kd)^2))", np.var(np.sin(th_hat)) / crb_u, 1.0, 0.05, rel=True)

print("\n== 3. sequential lobing / conical scan and amplitude fluctuation ==")
eps, phi_t = 0.05, np.radians(30)
nscan = 8
phis = 2 * np.pi * np.arange(nscan) / nscan
# squinted beam pointing at (ts cos phi, ts sin phi); target at (eps cos phi_t, eps sin phi_t)
def cs_amp(eps, phi_t, phis):
    dx = eps * np.cos(phi_t) - ts * np.cos(phis); dy = eps * np.sin(phi_t) - ts * np.sin(phis)
    return vbeam(np.hypot(dx, dy))
A = cs_amp(eps, phi_t, phis)
c1 = 2 * np.mean(A * np.exp(1j * phis)) / np.mean(A)  # first-harmonic modulation (complex)
m_pred = 4 * LN2 * ts * eps / tb ** 2
check("conical-scan modulation depth = 4 ln2 theta_s eps/theta_b^2 (small eps)", abs(c1), m_pred, 0.02, rel=True)
check("conical-scan modulation phase = target direction [deg]", np.degrees(np.angle(c1)), 30.0, 0.5)
# fluctuation: independent 20 % rms amplitude per pulse (no noise) -> error std
fl = 0.2
Mc = 20000
err_cs = []; err_mp = []
for _ in range(Mc):
    g = 1 + fl * rng.standard_normal(nscan)
    Ai = A * g
    c = 2 * np.mean(Ai * np.exp(1j * phis)) / np.mean(Ai)
    err_cs.append(abs(c) / (4 * LN2 * ts) - eps)
    # monopulse: both beams see the same fluctuation in one pulse -> ratio unchanged
    gg = 1 + fl * rng.standard_normal()
    r = ((vbeam(eps - ts) - vbeam(eps + ts)) * gg) / ((vbeam(eps - ts) + vbeam(eps + ts)) * gg)
    err_mp.append(np.arctanh(r) / (4 * LN2 * ts) - eps)
print(f"    20 % pulse-to-pulse fluctuation: conical-scan angle error std {np.std(err_cs):.4f} theta_b, monopulse {np.std(err_mp):.1e}")
check_true("fluctuation corrupts conical scan (> 0.02 theta_b) but not monopulse (< 1e-9)", np.std(err_cs) > 0.02 and np.std(err_mp) < 1e-9)

print("\n== 4. split-gate range discriminator ==")
Tp = 1.0
tri = lambda t: np.maximum(0, 1 - np.abs(t) / Tp)        # matched-filter output of a rect pulse
for e_ in (-0.3, -0.1, 0.0, 0.2, 0.45):
    E = tri(-Tp / 2 - e_); L = tri(Tp / 2 - e_)
    check(f"S-curve (L-E)/(L+E) at eps = {e_}", (L - E) / (L + E), 2 * e_ / Tp, 1e-12)

print("\n== 5. polar -> Cartesian measurement conversion ==")
r0, az0 = 10000.0, np.radians(35.0)
sr, sa = 5.0, 2e-3
Mp = 400000
rr = r0 + sr * rng.standard_normal(Mp); aa = az0 + sa * rng.standard_normal(Mp)
xy = np.column_stack([rr * np.sin(aa), rr * np.cos(aa)])  # x east, y north (az from north)
J = np.array([[np.sin(az0), r0 * np.cos(az0)], [np.cos(az0), -r0 * np.sin(az0)]])
Rxy = J @ np.diag([sr ** 2, sa ** 2]) @ J.T
Cmc = np.cov(xy.T)
check("converted covariance J R J^T vs MC (max rel err)", np.max(np.abs(Cmc - Rxy) / np.max(np.abs(Rxy))), 0.0, 0.01)
check("cross-range sigma = r sigma_theta [m]", np.sqrt(np.linalg.eigvalsh(Rxy)).max(), r0 * sa, 1e-6, rel=True)
bias = r0 - np.mean(r0 * np.cos(aa - az0))           # angle-induced part only (range noise excluded)
check("conversion bias along range ~ r sigma^2/2 [m]", bias, r0 * sa ** 2 / 2, 0.002)

print("\n== 6. gating, NN vs PDAF in clutter ==")
gamma = stats.chi2.ppf(0.99, 2)
check("gate threshold for P_G = 0.99, m = 2", gamma, 9.2103, 1e-3)
Sx = np.array([[400.0, 50.0], [50.0, 300.0]])
Vg = np.pi * gamma * np.sqrt(np.linalg.det(Sx))
print(f"    gate area for S above: {Vg:.0f} m^2")
# MC
T6 = 1.0; sw6 = 0.5; sv6 = 10.0; PD = 0.9; PG = 0.99
F6 = np.kron(np.eye(2), np.array([[1, T6], [0, 1]]))
G6 = np.kron(np.eye(2), np.array([[T6 ** 2 / 2], [T6]]))
Q6 = G6 @ G6.T * sw6 ** 2
H6 = np.array([[1.0, 0, 0, 0], [0, 0, 1.0, 0]])
R6 = np.eye(2) * sv6 ** 2


def track(method, lam_c, seed, K=60):
    r = np.random.default_rng(seed)
    xt = np.array([0, 20.0, 0, 10.0])
    x = xt + np.array([r.normal(0, 10), r.normal(0, 2), r.normal(0, 10), r.normal(0, 2)])
    P = np.diag([100, 4, 100, 4.0])
    errs = []
    for k in range(K):
        xt = F6 @ xt + (G6 @ (sw6 * r.standard_normal(2)))
        xp = F6 @ x; Pp = F6 @ P @ F6.T + Q6
        S = H6 @ Pp @ H6.T + R6; Si = np.linalg.inv(S); Kg = Pp @ H6.T @ Si
        zp = H6 @ xp
        half = 4 * np.sqrt(np.max(np.diag(S)))
        A_reg = (2 * half) ** 2
        nc = r.poisson(lam_c * A_reg)
        Z = list(zp + r.uniform(-half, half, (nc, 2)))
        if r.random() < PD:
            Z.append(H6 @ xt + sv6 * r.standard_normal(2))
        Z = np.array(Z) if len(Z) else np.zeros((0, 2))
        nus = Z - zp
        d2 = np.einsum('ij,jk,ik->i', nus, Si, nus) if len(Z) else np.zeros(0)
        val = nus[d2 < gamma]; dv = d2[d2 < gamma]
        if method == "NN":
            if len(val):
                nu = val[np.argmin(dv)]
                x = xp + Kg @ nu
                IKH = np.eye(4) - Kg @ H6
                P = IKH @ Pp @ IKH.T + Kg @ R6 @ Kg.T
            else:
                x, P = xp, Pp
        else:  # PDAF
            if len(val):
                e = np.exp(-dv / 2)
                b = lam_c * np.sqrt(np.linalg.det(2 * np.pi * S)) * (1 - PD * PG) / PD
                beta = e / (b + e.sum()); b0 = b / (b + e.sum())
                nu = beta @ val
                x = xp + Kg @ nu
                Pc = (np.eye(4) - Kg @ H6) @ Pp
                spread = Kg @ ((val.T * beta) @ val - np.outer(nu, nu)) @ Kg.T
                P = b0 * Pp + (1 - b0) * Pc + spread
            else:
                x, P = xp, Pp
        errs.append(np.hypot(*(H6 @ (x - xt))))
    return np.array(errs)


# steady-state innovation covariance of this tracker (nearest-neighbour ideal, PD = 1) -> gate area
from scipy import linalg as _la
Pss = _la.solve_discrete_are(F6.T, H6.T, Q6, R6)
Sss = H6 @ Pss @ H6.T + R6
Vss = np.pi * gamma * np.sqrt(np.linalg.det(Sss))
print(f"    steady-state gate area {Vss:.0f} m^2 -> expected false measurements per gate: "
      + ", ".join(f"{lc:.0e}/m^2: {lc*Vss:.2f}" for lc in (2e-5, 2e-4, 1e-3)))
res6 = {}
for lam_c in (2e-5, 2e-4, 1e-3):
    for method in ("NN", "PDAF"):
        E = np.array([track(method, lam_c, 9000 + s) for s in range(300)])
        lost = np.mean(E[:, -1] > 100)
        rms_ok = np.sqrt(np.mean(E[E[:, -1] <= 100][:, 20:] ** 2)) if np.any(E[:, -1] <= 100) else np.nan
        res6[(lam_c, method)] = (lost, rms_ok)
        print(f"    clutter {lam_c:.0e}/m^2, {method}: track loss {lost:.3f}, rms position error (kept tracks) {rms_ok:.1f} m")
check_true("PDAF loses fewer tracks than NN at 2e-4 and 1e-3 /m^2", res6[(2e-4, "PDAF")][0] < res6[(2e-4, "NN")][0] and res6[(1e-3, "PDAF")][0] < res6[(1e-3, "NN")][0])
check_true("light clutter (2e-5 /m^2, ~0.2 false per gate): both track (loss < 5 %)", res6[(2e-5, "NN")][0] < 0.05 and res6[(2e-5, "PDAF")][0] < 0.05)

print("\n== 7. ground-station pointing from GNSS telemetry ==")
for eps_rel in (0.1, 0.25, 0.5):
    check(f"Gaussian pointing loss at eps = {eps_rel} theta3 [dB] = 12.04 (eps/theta3)^2",
          -20 * np.log10(vbeam(eps_rel)), 12.0412 * eps_rel ** 2, 1e-3)
# rocket ascent seen from a station 5 km cross-range: vertical boost + coast, 10 m/s horizontal drift
g = 9.80665; dt = 0.01
t = np.arange(0, 25, dt)
h = np.zeros_like(t); v = np.zeros_like(t); a = np.zeros_like(t)
for i in range(len(t) - 1):
    a[i] = (60.0 if t[i] < 2.5 else -g) - (0.0012 * v[i] * abs(v[i]) if t[i] >= 2.5 else 0.0)
    v[i + 1] = v[i] + a[i] * dt; h[i + 1] = h[i] + v[i] * dt + 0.5 * a[i] * dt ** 2
a[-1] = a[-2]
iapo = np.argmax(h)
pos = np.column_stack([10.0 * t, np.zeros_like(t), h])          # ENU-ish: drift east
vel = np.column_stack([np.full_like(t, 10.0), np.zeros_like(t), v])
def pointing_case(dist):
    stn = np.array([0.0, -dist, 0.0])                              # station dist south of pad


    def azel(p, stn=stn):
        dlt = p - stn
        return np.degrees(np.arctan2(dlt[..., 0], dlt[..., 1])), np.degrees(np.arctan2(dlt[..., 2], np.hypot(dlt[..., 0], dlt[..., 1])))


    az_t, el_t = azel(pos)
    rate_el = np.max(np.abs(np.gradient(el_t, dt)[:iapo]))
    # telemetry: 5 Hz GNSS pos (3 m) / vel (0.3 m/s), latency 0.6 s; pointing computed at 20 Hz
    tel_dt, lat = 0.2, 0.6
    r7 = np.random.default_rng(77)
    tel_idx = np.arange(0, iapo, int(tel_dt / dt))
    tel_pos = pos[tel_idx] + 3.0 * r7.standard_normal((len(tel_idx), 3))
    tel_vel = vel[tel_idx] + 0.3 * r7.standard_normal((len(tel_idx), 3))
    cmd_idx = np.arange(int((lat + 0.5) / dt), iapo, int(0.05 / dt))


    def ang_err(p_cmd, k, stn=stn):
        u1 = p_cmd - stn; u2 = pos[k] - stn
        return np.degrees(np.arccos(np.clip(u1 @ u2 / np.linalg.norm(u1) / np.linalg.norm(u2), -1, 1)))


    errs = {"raw": [], "extrap": [], "kf": []}
    # simple per-axis CA Kalman on telemetry (pos + vel measured), predict to now
    Fk = lambda T: np.array([[1, T, T ** 2 / 2], [0, 1, T], [0, 0, 1]])
    Hk = np.array([[1.0, 0, 0], [0, 1.0, 0]])
    Rk = np.diag([9.0, 0.09])
    qj = 50.0                                                       # jerk PSD (m^2/s^5): boost/burnout transients
    def Qca(T):
        return qj * np.array([[T ** 5 / 20, T ** 4 / 8, T ** 3 / 6], [T ** 4 / 8, T ** 3 / 3, T ** 2 / 2], [T ** 3 / 6, T ** 2 / 2, T]])
    kf_states = []
    xs = [np.array([tel_pos[0, j], tel_vel[0, j], 0.0]) for j in range(3)]
    Ps = [np.diag([9.0, 0.09, 100.0]) for _ in range(3)]
    for n in range(len(tel_idx)):
        if n > 0:
            for j in range(3):
                Fm = Fk(tel_dt); xs[j] = Fm @ xs[j]; Ps[j] = Fm @ Ps[j] @ Fm.T + Qca(tel_dt)
                zj = np.array([tel_pos[n, j], tel_vel[n, j]])
                Sj = Hk @ Ps[j] @ Hk.T + Rk; Kj = Ps[j] @ Hk.T @ np.linalg.inv(Sj)
                xs[j] = xs[j] + Kj @ (zj - Hk @ xs[j]); Ps[j] = (np.eye(3) - Kj @ Hk) @ Ps[j]
        kf_states.append([x.copy() for x in xs])
    for k in cmd_idx:
        tnow = t[k]
        avail = np.where(t[tel_idx] + lat <= tnow)[0]
        if len(avail) == 0:
            continue
        n = avail[-1]; age = tnow - t[tel_idx[n]]
        errs["raw"].append(ang_err(tel_pos[n], k))
        errs["extrap"].append(ang_err(tel_pos[n] + tel_vel[n] * age, k))
        pk = np.array([Fk(age)[0] @ kf_states[n][j] for j in range(3)])
        errs["kf"].append(ang_err(pk, k))
    return rate_el, {k_: np.array(v_) for k_, v_ in errs.items()}


print(f"    rocket: apogee {h[iapo]:.0f} m at {t[iapo]:.2f} s, 10 m/s drift; telemetry 5 Hz, latency 0.6 s")
for dist in (1000.0, 5000.0):
    rate_el, errs = pointing_case(dist)
    print(f"    station {dist/1000:.0f} km: peak elevation rate {rate_el:.2f} deg/s")
    for kname in errs:
        e = errs[kname]
        print(f"      pointing error ({kname}): p95 {np.percentile(e, 95):.2f} deg, max {e.max():.2f} deg")
    check_true(f"{dist/1000:.0f} km: velocity extrapolation beats raw last-fix pointing (p95)", np.percentile(errs["extrap"], 95) < np.percentile(errs["raw"], 95))
    check_true(f"{dist/1000:.0f} km: CA Kalman prediction <= 1.05 x extrapolation (p95)", np.percentile(errs["kf"], 95) <= np.percentile(errs["extrap"], 95) * 1.05)
    check_true(f"{dist/1000:.0f} km: KF-predicted pointing max error < 5 deg (< 0.2 dB for a 40 deg Yagi)", np.max(errs["kf"]) < 5.0)
# RSSI step-track (sequential lobing with packet RSSI)
th3 = 40.0; delta = th3 / 4; s_rssi = 1.5
sig_eps = np.sqrt(2) * s_rssi * th3 ** 2 / (4 * 12.0412 * delta)
print(f"    RSSI step-track, theta3 40 deg, offsets +-{delta} deg, 1.5 dB RSSI noise: sigma_eps = {sig_eps:.1f} deg per pair")
# verify the dB-difference slope numerically
eps0 = 3.0
ddb = (-20 * np.log10(vbeam(eps0 - delta, th3))) - (-20 * np.log10(vbeam(eps0 + delta, th3)))
C_db = 40 * LN2 / np.log(10)
check("RSSI pair difference = 4 C eps delta/theta3^2 dB, C = 40 ln2/ln10 = 12.04", -ddb, 4 * C_db * eps0 * delta / th3 ** 2, 1e-9, rel=True)

print("\n== 8. worked numbers ==")
th3d = 5.8; snr15 = 10 ** 1.5
km_use = 1.6
s_ang = th3d / (km_use * np.sqrt(2 * snr15))
check("S-band 5.8 deg dish, 15 dB, k_m 1.6: sigma_theta [deg]", s_ang, 0.456, 0.002)
check("  -> cross-range at 1 km [m]", np.radians(s_ang) * 1000, 7.96, 0.05)
for d_, v_, want in ((500.0, 250.0, 28.65), (5000.0, 250.0, 2.865)):
    check(f"peak elevation rate v/d at d = {d_:.0f} m, v = {v_:.0f} m/s [deg/s]", np.degrees(v_ / d_), want, 0.01)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
