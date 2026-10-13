#!/usr/bin/env python3
"""W5-S15 / G-06-02 — PLL dynamics checks for kb/06-rf-circuits/vco-and-pll-synthesizers.md
("Level 3b — PLL dynamics, sampling limits and special architectures").

 A. Sampled-loop (Gardner) stability of a series-RC charge-pump PLL:
    A1 linear map  e[n+1] = (1-a-b) e[n] - u[n], u[n+1] = u[n] + b e[n]  ->  z^2-(2-a-b)z+(1-a); Jury -> 2a+b<4
       == Gardner 1980 omega_n^2 < omega_i^2/[pi(pi+omega_i tau2)];  zeta=0.707 -> omega_n T < 1.035
    A2 EXACT event-driven tri-state-PFD / charge-pump simulation arbitrates Gardner (2a+b<4) vs the exact
       piecewise-smooth result of Kuznetsov et al. 2021 (b<4, a<1 = no VCO overload)
    A3 standard 3rd-order loop (C1 || R2+C2): phase margin with sampling (alias sum of G) vs continuous,
       and step overshoot: continuous model vs impulse-invariant model vs exact event simulation
 B. Lock time: linear model vs exact PFD simulation (cycle slips for large hops) vs slew estimate
 C. Bench loop-bandwidth measurement: closed-loop -3 dB, peaking, hump frequency, step-response fit
 D. Two-point modulation: response H + g(1-H); error (g-1)(1-H); FSK single-point vs two-point
 E. FMCW ramp through a type-2 loop: static phase error 2 pi R A0/(K_phi K_v), chirp-start transient
 F. Offset (translation) PLL vs direct PLL in-band floor
 G. Charge-pump up/down mismatch folds Sigma-Delta noise in band (linear + |x| model); offset-current cure
 H. PLL vs DLL: jitter accumulation (1st-order loop) vs no accumulation in a delay line
Run: python3 tools/verify/s15_pll_dynamics.py      (about 30-60 s)
"""
import sys
import numpy as np
from scipy import signal
from scipy.linalg import expm
from scipy.optimize import brentq

ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


# --- copied from tools/verify/rfckt_pll.py (importing it would run its checks) -------------------
def design_2nd_order(fc, pm_deg, Icp, Kv_hz, N):
    wc = 2 * np.pi * fc; phi = np.deg2rad(pm_deg)
    Kphi = Icp / (2 * np.pi); Kv = 2 * np.pi * Kv_hz
    T1 = (1 / np.cos(phi) - np.tan(phi)) / wc
    T2 = 1 / (wc ** 2 * T1)
    A0 = Kphi * Kv / (N * wc ** 2) * np.sqrt((1 + (wc * T2) ** 2) / (1 + (wc * T1) ** 2))
    C1 = A0 * T1 / T2; C2 = A0 - C1; R2 = T2 / C2
    return C1, C2, R2


def Zfilt(f, C1, C2, R2):
    s = 2j * np.pi * f
    return 1 / (s * C1 + 1 / (R2 + 1 / (s * C2)))


def G_open(f, C1, C2, R2, Icp, Kv_hz, N):
    s = 2j * np.pi * f
    return (Icp / (2 * np.pi)) * (2 * np.pi * Kv_hz) * Zfilt(f, C1, C2, R2) / (N * s)


# ADF4351 example of the page (433.92 MHz = 3471.36 MHz / 8, fPFD 25 MHz, Icp 2.5 mA, Kv 40 MHz/V)
fPFD = 25e6; fVCO = 3471.36e6; N = fVCO / fPFD; Icp = 2.5e-3; Kv = 40e6; fc0, PM0 = 50e3, 50.0
C1, C2, R2 = design_2nd_order(fc0, PM0, Icp, Kv, N)
A0 = C1 + C2; T2 = R2 * C2; T1 = R2 * C1 * C2 / A0
Kphi = Icp / (2 * np.pi); Kvr = 2 * np.pi * Kv


def cl_tf(C1_, C2_, R2_, Icp_=Icp, Kv_=Kv, N_=N):
    """continuous closed loop H = G/(1+G) (ref phase -> divided phase), and G num/den"""
    A0_ = C1_ + C2_; T2_ = R2_ * C2_; T1_ = R2_ * C1_ * C2_ / A0_
    num = (Icp_ / (2 * np.pi)) * (2 * np.pi * Kv_) / N_ * np.array([T2_, 1.0])
    den = np.array([A0_ * T1_, A0_, 0.0, 0.0])
    return num, den, np.polyadd(den, num)


# ================================================================ exact event-driven PFD/CP simulator
class EventPLL:
    """Tri-state PFD + ideal charge pump + linear loop filter (state space, current input) + VCO.
    theta = divided VCO phase in cycles; reference edges at t = k*T. Divided frequency = f0 + Kd*v (Hz),
    Kd = Kv/N (Hz/V).  Between edges the current is constant, so the state is propagated EXACTLY with a
    matrix exponential of the augmented system [x, theta, 1]; divider edges are found by root finding."""

    def __init__(self, A, B, Cv, D, Kd, f0, T, Icp_):
        self.n = A.shape[0]; self.A, self.B, self.Cv, self.D = A, B, Cv, D
        self.Kd, self.f0, self.T, self.I = Kd, f0, T, Icp_
        self._cache = {}

    def M(self, s):
        n = self.n; i = s * self.I
        M = np.zeros((n + 2, n + 2))
        M[:n, :n] = self.A; M[:n, n + 1] = self.B * i
        M[n, :n] = self.Kd * self.Cv; M[n, n + 1] = self.f0 + self.Kd * self.D * i
        return M

    def prop(self, z, tau, s):
        return expm(self.M(s) * tau) @ z

    def run(self, x0, n_cycles, theta0=0.0, f0_after=None):
        n = self.n
        z = np.concatenate([np.asarray(x0, float), [theta0, 1.0]])
        if f0_after is not None:
            self.f0 = f0_after
        t = 0.0; s = 0; edges = int(np.floor(theta0 + 1e-12)); kref = 0; slips = 0
        rec_t, rec_x, rec_e, rec_s = [], [], [], []
        while kref < n_cycles:
            t_ref = (kref + 1) * self.T
            tau_r = t_ref - t
            zr = self.prop(z, tau_r, s)
            target = edges + 1
            if zr[n] >= target:                      # divider edge before next reference edge
                f = lambda tau: self.prop(z, tau, s)[n] - target
                tau_v = brentq(f, 0.0, tau_r, xtol=self.T * 1e-9, rtol=1e-12)
                z = self.prop(z, tau_v, s); t += tau_v; edges += 1
                s = max(s - 1, -1)
            else:
                z = zr; t = t_ref; kref += 1
                if s == 1:
                    slips += 1                       # ref edge while already UP: a cycle slip
                s = min(s + 1, 1)
                rec_t.append(t); rec_x.append(z[:n].copy()); rec_e.append(kref - z[n]); rec_s.append(s)
        return np.array(rec_t), np.array(rec_x), np.array(rec_e), slips


# ================================================================ A. sampled-loop stability
print("A1: series-RC CP-PLL linear sampled map, a = K T R, b = K T^2/C (K = Icp Kv/(2 pi N), Kv in rad/s/V)")
for zeta in (0.5, 0.707, 1.0):
    x_lim = 2 * (np.sqrt(zeta ** 2 + 1) - zeta)                  # omega_n T limit from 4 zeta x + x^2 = 4
    ok = True
    for fac, want_stable in ((0.99, True), (1.01, False)):
        x = x_lim * fac; a = 2 * zeta * x; b = x ** 2
        ev = np.linalg.eigvals(np.array([[1 - a - b, -1.0], [b, 1.0]]))
        ok &= (max(abs(ev)) < 1) == want_stable
    # Gardner's form: omega_n^2 < omega_i^2/[pi(pi + omega_i tau2)], tau2 = 2 zeta/omega_n, omega_i = 2 pi/T
    T = 1.0; wi = 2 * np.pi / T; wn = x_lim / T; tau2 = 2 * zeta / wn
    gard = wi ** 2 / (np.pi * (np.pi + wi * tau2))
    print(f"   zeta {zeta:5.3f}: omega_n T < {x_lim:.4f}  (f_n < {x_lim/(2*np.pi):.4f} f_ref); Gardner RHS/omega_n^2 = {gard/wn**2:.6f}")
    check(f"A1 zeta={zeta}: Jury limit 2a+b=4 is the eigenvalue boundary and equals Gardner's formula", ok and abs(gard / wn ** 2 - 1) < 1e-9)

# A2 exact simulation, normalised: T = 1, N = 1, Icp = 1, Kd = 1 Hz/V -> a = R, b = 1/C
print("A2: exact event-driven simulation of the series-RC CP-PLL (N = 1, T = 1); u0 = 1e-3 frequency kick")


def series_rc_growth(a, b, ncyc=300, u0=1e-7):
    R = a; C = 1.0 / b
    sim = EventPLL(np.array([[0.0]]), np.array([1.0 / C]), np.array([1.0]), R, 1.0, 1.0, 1.0, 1.0)
    _, _, e, _ = sim.run([u0], ncyc)
    e0 = np.sqrt(np.mean(e[2:12] ** 2)); e1 = np.sqrt(np.mean(e[-20:] ** 2))
    return e1 / max(e0, 1e-30)


cases = [(0.3, 2.0), (0.3, 3.6), (0.3, 3.9), (0.3, 4.3), (0.7, 2.0), (0.9, 2.4), (0.3, 3.0)]
res = {}
for a, b in cases:
    g = series_rc_growth(a, b)
    res[(a, b)] = g
    gard = 2 * a + b < 4; kuz = (b < 4) and (a < 1)
    print(f"   a {a:.1f}, b {b:.1f}: Gardner {'stable' if gard else 'UNSTABLE'}, exact-theory {'stable' if kuz else 'UNSTABLE'}"
          f" -> simulated rms phase-error ratio (last 20 / first 10 of 300 cycles) {g:.3g}")
print("   (b = 3, i.e. beta = 3/2 in Kuznetsov's notation, is their degenerate point where period-3 cycles merge with lock: decay is slow)")
check("A2 simulation: b<4 (a<1) decays even where Gardner's 2a+b<4 is violated; b>4 grows",
      res[(0.3, 3.6)] < 0.1 and res[(0.3, 3.9)] < 0.1 and res[(0.9, 2.4)] < 0.1 and res[(0.3, 4.3)] > 10 and res[(0.3, 2.0)] < 0.1
      and res[(0.7, 2.0)] < 0.1)
zeta = 0.707
x_k = min(2.0, 1 / (2 * zeta))      # b<4 -> x<2 ; a<1 -> 2 zeta x < 1
print(f"   -> for zeta = 0.707 the binding exact limit is VCO overload a < 1: omega_n T < {x_k:.3f} (f_n < {x_k/(2*np.pi):.3f} f_ref)"
      f" vs Gardner {2*(np.sqrt(zeta**2+1)-zeta):.3f}; both >> the f_c <= f_ref/10 design rule")

# A3: standard 3rd-order loop, sampled vs continuous
print("A3: Banerjee 50-deg 3rd-order loop at fc/fref = 1/100 ... 1/4: phase margin and step overshoot")


def pm_sampled(fc_ratio, pm=50.0, kmax=4000):
    fr = 1.0; fc = fc_ratio * fr
    c1, c2, r2 = design_2nd_order(fc, pm, 1.0, 1.0, 1.0)
    ff = np.logspace(np.log10(fc / 5), np.log10(min(5 * fc, 0.499)), 1500)
    k = np.arange(-kmax, kmax + 1)
    Gs = np.array([np.sum(G_open(fx + k * fr, c1, c2, r2, 1.0, 1.0, 1.0)) for fx in ff])
    i = np.argmin(abs(abs(Gs) - 1))
    Gc = G_open(ff, c1, c2, r2, 1.0, 1.0, 1.0); ic = np.argmin(abs(abs(Gc) - 1))
    return 180 + np.degrees(np.angle(Gs[i])), ff[i] / fc, 180 + np.degrees(np.angle(Gc[ic])), (c1, c2, r2)


def overshoots(fc_ratio, filt, ncyc):
    """overshoot of the cycle-averaged divided frequency, (1 - Δe/df) — v sampled at the edges carries a
    per-cycle sawtooth from the R2/C1 proportional path, so it is not a fair metric."""
    c1, c2, r2 = filt; T = 1.0
    A = np.array([[-1 / (r2 * c1), 1 / (r2 * c1)], [1 / (r2 * c2), -1 / (r2 * c2)]])
    B = np.array([1 / c1, 0.0]); Cv = np.array([1.0, 0.0])
    df = 2e-4 * fc_ratio * 2 * np.pi
    sim = EventPLL(A, B, Cv, 0.0, 1.0, 1.0, T, 1.0)
    _, _, e_ev, _ = sim.run([0.0, 0.0], ncyc, f0_after=1.0 - df)
    f_ev = 1 - np.diff(np.concatenate([[0.0], e_ev])) / df
    M0 = np.zeros((4, 4)); M0[:2, :2] = A; M0[2, :2] = Cv; M0[2, 3] = 1.0 - df
    P = expm(M0 * T); z = np.array([0.0, 0.0, 0.0, 1.0]); e_ii = []
    for k in range(ncyc):
        z = P @ z; e = (k + 1) - z[2]
        z[:2] += B * e * T; e_ii.append(e)
    f_ii = 1 - np.diff(np.concatenate([[0.0], e_ii])) / df
    num, den, cden = cl_tf(c1, c2, r2, 1.0, 1.0, 1.0)
    tt = np.linspace(0, ncyc * T, 20 * ncyc)
    _, y = signal.step((num, cden), T=tt)
    return f_ev.max() - 1, f_ii.max() - 1, y.max() - 1


pm_tab = {}
for r in (1 / 100, 1 / 30, 1 / 10, 1 / 5, 1 / 4):
    pms, fr_c, pmc, filt = pm_sampled(r)
    ncyc = int(12 / r)
    o_ev, o_ii, o_ct = overshoots(r, filt, ncyc)
    pm_tab[r] = (pms, o_ev, o_ii, o_ct)
    print(f"   fc = fref/{1/r:5.1f}: PM continuous {pmc:5.1f} deg, with sampling {pms:5.1f} deg (crossover x{fr_c:.2f}); "
          f"overshoot continuous {100*o_ct:5.1f} %, impulse-invariant {100*o_ii:5.1f} %, exact PFD sim {100*o_ev:5.1f} %")
check("A3 sampling costs < 2 deg at fref/100 and > 15 deg at fref/5; exact sim tracks impulse-invariant model",
      50 - pm_tab[1 / 100][0] < 2 and 50 - pm_tab[1 / 5][0] > 15 and
      all(abs(v[1] - v[2]) < 0.03 for v in pm_tab.values()) and pm_tab[1 / 5][1] > pm_tab[1 / 100][1] + 0.1)

# ================================================================ B. lock time
print("B: ADF4351 50 kHz/50 deg loop (no R3/C3), lock time to |f_VCO error| < 1 kHz (VCO-referred)")
Ab = np.array([[-1 / (R2 * C1), 1 / (R2 * C1)], [1 / (R2 * C2), -1 / (R2 * C2)]])
Bb = np.array([1 / C1, 0.0]); Cb = np.array([1.0, 0.0])
num, den, cden = cl_tf(C1, C2, R2)


def lin_lock(dF, tol=1e3, tf=None):
    tf = tf or (num, cden)
    t = np.linspace(0, 1e-3, 100001)
    _, y = signal.step(tf, T=t)
    err = abs(1 - y) * dF
    return t[np.where(err > tol)[0][-1] + 1]


def ev_lock(dF, filt=(C1, C2, R2), tol=1e3, tmax=150e-6):
    c1, c2, r2 = filt
    A = np.array([[-1 / (r2 * c1), 1 / (r2 * c1)], [1 / (r2 * c2), -1 / (r2 * c2)]]); B = np.array([1 / c1, 0.0])
    tmax = tmax + 2.0 * dF / (Kv * Icp / (c1 + c2))
    N1 = (fVCO + dF) / fPFD
    sim = EventPLL(A, B, np.array([1.0, 0.0]), 0.0, Kv / N1, fVCO / N1, 1 / fPFD, Icp)
    t, x, e, slips = sim.run([0.0, 0.0], int(tmax * fPFD))
    # cycle-averaged VCO frequency error (Hz) from the PFD phase-error sequence
    ferr = -np.diff(np.concatenate([[0.0], e])) * fPFD * N1
    bad = np.where(abs(ferr) > tol)[0]
    return (t[bad[-1] + 1] if len(bad) and bad[-1] + 1 < len(t) else np.nan), slips


slew = Kv * Icp / A0          # Hz/s at the VCO with the pump saturated
lock = {}
for dF in (1e6, 10e6, 30e6, 60e6):
    tl = lin_lock(dF); te, sl = ev_lock(dF)
    lock[dF] = (tl, te, sl)
    print(f"   50 kHz loop, hop {dF/1e6:4.0f} MHz: linear model {tl*1e6:6.1f} us, exact PFD sim {te*1e6:6.1f} us, cycle slips {sl:4d}")
print(f"   (pump-saturated slew rate Kv*Icp/(C1+C2) = {slew/1e12:.2f} MHz/us)")
f10 = design_2nd_order(10e3, PM0, Icp, Kv, N)
n10, d10, c10 = cl_tf(*f10)
for dF in (3e6, 10e6, 30e6):
    tl = lin_lock(dF, tf=(n10, c10)); te, sl = ev_lock(dF, filt=f10, tmax=700e-6)
    lock[("10k", dF)] = (tl, te, sl)
    print(f"   10 kHz loop, hop {dF/1e6:4.0f} MHz: linear model {tl*1e6:6.1f} us, exact PFD sim {te*1e6:6.1f} us, cycle slips {sl:4d}")
check("B1 small hop: exact PFD sim matches the linear model within 10 %", abs(lock[1e6][1] / lock[1e6][0] - 1) < 0.10)
check("B2 large hop in a narrow loop: cycle slips appear and lock takes longer than the linear prediction",
      lock[("10k", 30e6)][2] > 0 and lock[("10k", 30e6)][1] > 1.2 * lock[("10k", 30e6)][0])

# ================================================================ C. bench loop-bandwidth measurement
print("C: what to expect when measuring the 50 kHz / 50 deg loop on the bench")
ff = np.logspace(3, 7, 40001)
G = G_open(ff, C1, C2, R2, Icp, Kv, N)
H = G / (1 + G); E = 1 / (1 + G)
f3 = ff[np.where(abs(H) >= 1 / np.sqrt(2))[0][-1]]
pk_H = 20 * np.log10(abs(H).max()); f_pkH = ff[np.argmax(abs(H))]
pk_E = 20 * np.log10(abs(E).max()); f_pkE = ff[np.argmax(abs(E))]
print(f"   closed loop |H| (= reference-FM transfer): -3 dB at {f3/1e3:.1f} kHz = {f3/fc0:.2f} x fc; peaking {pk_H:.2f} dB at {f_pkH/1e3:.1f} kHz")
print(f"   VCO-noise transfer |1/(1+G)| (the 'hump' on a phase-noise plot): max {pk_E:.2f} dB at {f_pkE/1e3:.1f} kHz = {f_pkE/fc0:.2f} x fc")
# step method: overshoot and ringing period of a frequency step, as a function of PM, for this 3rd-order loop
t = np.linspace(0, 400e-6, 80001)


def step_signature(fc_, pm_):
    c1, c2, r2 = design_2nd_order(fc_, pm_, Icp, Kv, N)
    nm, dn, cd = cl_tf(c1, c2, r2)
    ts = t * 50e3 / fc_
    _, y = signal.step((nm, cd), T=ts)
    tpk = ts[np.argmax(y)]
    g = G_open(ff, c1, c2, r2, Icp, Kv, N); h = abs(g / (1 + g))
    return y.max() - 1, tpk * fc_, ff[np.where(h >= 1 / np.sqrt(2))[0][-1]] / fc_, 20 * np.log10(h.max())


sig = {}
for pm_ in (40.0, 50.0, 60.0):
    sig[pm_] = step_signature(50e3, pm_)
    print(f"   PM {pm_:.0f} deg: step overshoot {100*sig[pm_][0]:4.1f} %, time-to-peak x fc = {sig[pm_][1]:.3f}, "
          f"f_3dB = {sig[pm_][2]:.2f} fc, closed-loop peaking {sig[pm_][3]:.2f} dB")
s20 = step_signature(20e3, 50.0)
# the textbook 2nd-order type-2 fit misreads a 3rd-order loop
ov = sig[50.0][0]; tpk = sig[50.0][1] / fc0


def type2_sig(z):
    tt = np.linspace(0, 40, 40001)
    _, yy = signal.step(([2 * z, 1.0], [1, 2 * z, 1.0]), T=tt)
    return yy.max() - 1, tt[np.argmax(yy)]          # overshoot, time-to-peak x omega_n


zfit = brentq(lambda z: type2_sig(z)[0] - ov, 0.2, 1.5)
wnfit = type2_sig(zfit)[1] / tpk
f3_fit = wnfit / (2 * np.pi) * np.sqrt(1 + 2 * zfit ** 2 + np.sqrt((1 + 2 * zfit ** 2) ** 2 + 1))
print(f"   pitfall: fitting the 2nd-order type-2 formulas to the 50-deg step (overshoot {100*ov:.1f} %, peak at {tpk*1e6:.1f} us) gives "
      f"zeta {zfit:.2f}, f_n {wnfit/2/np.pi/1e3:.1f} kHz, f_3dB {f3_fit/1e3:.1f} kHz — true f_3dB {f3/1e3:.1f} kHz")
check("C1 f_3dB = 1.4-1.9 fc for 40-60 deg; time-to-peak x fc is scale-invariant",
      all(1.4 < v[2] < 1.9 for v in sig.values()) and abs(s20[1] / sig[50.0][1] - 1) < 0.01)

# ================================================================ D. two-point modulation
print("D: two-point modulation (divider/ΣΔ path low-passed by H, VCO-tune path high-passed by 1-H)")
fm = np.logspace(2, 7, 5001)
Gm = G_open(fm, C1, C2, R2, Icp, Kv, N); Hm = Gm / (1 + Gm)
for g in (1.0, 1.05, 0.90):
    resp = Hm + g * (1 - Hm)
    print(f"   VCO-path gain g = {g:.2f}: flatness {20*np.log10(abs(resp).min()):+.2f} / {20*np.log10(abs(resp).max()):+.2f} dB "
          f"(error -> (g-1)(1-H): {20*np.log10(abs(g-1)+1e-12):.0f} dB above the loop BW)")
check("D1 matched two-point response is flat; mismatch g leaves (g-1) error only above the loop bandwidth",
      np.allclose(abs(Hm + (1 - Hm)), 1) and abs(abs((Hm + 1.05 * (1 - Hm))[-1]) - 1.05) < 1e-3
      and abs(abs((Hm + 1.05 * (1 - Hm))[0]) - 1) < 1e-3)
# FSK eye: 2-FSK 100 kbit/s, ±25 kHz deviation (at the output), NRZ (no Gaussian filter, worst case)
rng = np.random.default_rng(1)
bits = rng.integers(0, 2, 400) * 2 - 1; Rb = 100e3; sps = 200
tt = np.arange(len(bits) * sps) / (Rb * sps); dev = np.repeat(bits, sps).astype(float)
_, ysp, _ = signal.lsim((num, cden), dev, tt)
Hn, Hd = num, cden
one_minus = (np.polysub(Hd, np.pad(Hn, (len(Hd) - len(Hn), 0))), Hd)
_, yhp, _ = signal.lsim(one_minus, dev, tt)
mid = np.arange(20, len(bits)) * sps + sps // 2
eye_sp = np.min(abs(ysp[mid])); eye_tp = np.min(abs((ysp + yhp)[mid])); eye_tp5 = np.min(abs((ysp + 1.05 * yhp)[mid]))
print(f"   2-FSK 100 kbit/s through a 50 kHz loop: worst bit-centre deviation single-point {100*eye_sp:.0f} % of nominal, "
      f"two-point matched {100*eye_tp:.1f} %, two-point g = 1.05 {100*eye_tp5:.1f} %")
check("D2 single-point modulation above the loop BW partly closes the eye (< 80 %); two-point restores it", eye_sp < 0.8 and eye_tp > 0.999 and eye_tp5 > 0.95)

# ================================================================ E. FMCW ramp
print("E: FMCW ramp through the type-2 loop (ramp made by stepping N, i.e. a ΣΔ ramp)")
Rr = 100e6 / 1e-3                     # 100 MHz per ms at the VCO
e_ss = 2 * np.pi * Rr * A0 / (Kphi * Kvr)
tt = np.linspace(0, 200e-6, 20001)
# divided-phase input for a VCO ramp: theta_in(t) = 2 pi (Rr/N) t^2/2 ; error = theta_in - theta_out
thin = 2 * np.pi * (Rr / N) * tt ** 2 / 2
_, thout, _ = signal.lsim((num, cden), thin, tt)
err = thin - thout
ferr = np.gradient(err, tt) / (2 * np.pi) * N        # VCO-referred frequency error (Hz)
i_set = np.where(abs(ferr) > 1e3)[0][-1]
print(f"   ramp {Rr/1e9:.0f} MHz/ms: steady-state phase error (divider-referred) {err[-1]:.4f} rad (formula 2 pi R A0/(Kphi Kv) = {e_ss:.4f} rad); "
      f"chirp-start frequency error peak {abs(ferr).max()/1e3:.1f} kHz, < 1 kHz after {tt[i_set]*1e6:.0f} us")
check("E1 type-2 loop: constant phase error = 2 pi R A0/(Kphi Kv), frequency error -> 0", abs(err[-1] / e_ss - 1) < 0.01 and abs(ferr[-1]) < 10)

# ================================================================ F. offset PLL
print("F: offset (translation) PLL vs direct PLL, in-band PLL-chip floor only (PN_SYNTH = -221 dBc/Hz)")
PN = -221.0
L_direct_vco = PN + 10 * np.log10(fPFD) + 20 * np.log10(N); L_direct_out = L_direct_vco - 20 * np.log10(8)
f_if = 23.92e6     # 433.92 MHz VCO mixed with a fixed 410 MHz LO; the 23.92 MHz IF is phase-locked with N = 1
L_offset = PN + 10 * np.log10(f_if) + 20 * np.log10(1)
print(f"   direct (ADF4351, ÷8): {L_direct_out:.1f} dBc/Hz at 433.92 MHz; offset loop with N = 1 at a 23.92 MHz IF: {L_offset:.1f} dBc/Hz "
      f"(+ the fixed offset LO's noise 1:1 and the reference x 20log(f_IF/f_ref))")
check("F1 offset loop removes the 20 log N multiplication of the PFD floor (> 20 dB better here)", L_direct_out - L_offset > 20)

# ================================================================ G. charge-pump mismatch -> folded ΣΔ noise
print("G: CP up/down mismatch delta on a MASH 1-1-1 divider sequence (fPFD 25 MHz), VCO-referred, before loop filtering")


def mash111(frac, n, bits=24):
    M = 1 << bits; X = int(round(frac * M)); a1 = a2 = a3 = 0; out = np.zeros(n)
    pc2 = pc3 = ppc3 = 0
    for k in range(n):
        a1 += X; c1 = a1 >> bits; a1 &= M - 1
        a2 += a1; c2 = a2 >> bits; a2 &= M - 1
        a3 += a2; c3 = a3 >> bits; a3 &= M - 1
        out[k] = c1 + (c2 - pc2) + (c3 - 2 * pc3 + ppc3)
        pc2 = c2; ppc3 = pc3; pc3 = c3
    return out


nG = 1 << 17
frac = 0.8544 + 1e-7 * np.pi
yv = mash111(frac, nG)
S = np.cumsum(yv - frac)           # divider-edge time error in VCO cycles (phase error in VCO cycles)
S -= S.mean()


def inband(phi, f_lo=10e3, f_hi=100e3):
    fw, P = signal.welch(phi, fs=fPFD, nperseg=1 << 14, detrend='constant')
    sel = (fw > f_lo) & (fw < f_hi)
    return 10 * np.log10(np.median(P[sel]) / 2)


L_lin = inband(2 * np.pi * S)
print(f"   ideal CP: shaped ΣΔ noise 10-100 kHz = {L_lin:.1f} dBc/Hz (VCO-referred, open loop)")
fold = {}
for d in (0.01, 0.05, 0.10):
    q = S + (d / 2) * np.abs(S)                       # charge ∝ dt (1 ± d/2): linear + |x| term
    fold[d] = inband(2 * np.pi * q)
    t_off = np.abs(S).max() * 1.2                     # bleed/offset current: every pulse is UP, CP stays in one region
    q_off = (S + t_off) * (1 + d / 2)
    L_off = inband(2 * np.pi * (q_off - q_off.mean()))
    print(f"   mismatch {100*d:4.0f} %: in-band 10-100 kHz {fold[d]:6.1f} dBc/Hz (+{fold[d]-L_lin:.0f} dB);"
          f" with offset (bleed) current {L_off:6.1f} dBc/Hz; at 433.92 MHz subtract 18 dB")
check("G1 mismatch folds ΣΔ noise in band (≥ 20 dB rise at 5 %), offset current removes it", fold[0.05] - L_lin > 20 and L_off - L_lin < 2)
print(f"   compare: ADF4351 in-band floor at the VCO {L_direct_vco:.1f} dBc/Hz -> 5 % folded noise {fold[0.05]:.1f} dBc/Hz "
      f"{'exceeds' if fold[0.05] > L_direct_vco else 'is below'} it")

# ================================================================ H. PLL vs DLL jitter accumulation
print("H: jitter accumulation — VCO in a 1st-order PLL vs a DLL delay line (same per-period random jitter)")
rng = np.random.default_rng(7); n = 200000; sig = 1.0
w = rng.normal(0, sig, n)
for frac_bw in (1 / 20, 1 / 100):
    beta = 2 * np.pi * frac_bw                       # per-cycle loop correction fraction (1st-order loop, fc = frac_bw*fref)
    e = signal.lfilter([1.0], [1.0, -(1 - beta)], w)
    pred = sig / np.sqrt(1 - (1 - beta) ** 2)
    print(f"   PLL fc = fref/{1/frac_bw:.0f}: RMS edge error {e[1000:].std():.2f} sigma (theory 1/sqrt(2b-b^2) = {pred:.2f}); "
          f"DLL: {sig:.2f} sigma (each edge = reference edge + one pass through the line; no memory)")
check("H1 PLL accumulates VCO jitter up to ~1/sqrt(2*2 pi fc/fref) x; DLL does not", e[1000:].std() > 2 * sig)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
sys.exit(0 if ok_all else 1)
