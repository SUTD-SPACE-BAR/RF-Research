#!/usr/bin/env python3
"""
gnss_tracking_loops.py — verification for
  kb/21-gnss/gnss-receiver-architecture-acquisition-tracking.md  (loop noise/threshold formulas)
  kb/21-gnss/gnss-on-rockets-dynamics-and-limits.md             (rocket boost dynamics)

 1. Thermal-noise jitter of PLL (Costas), FLL and DLL (Kaplan & Hegarty 3e, ch. 8 forms)
    and the resulting C/N0 thresholds for given B_n, T.
 2. Dynamic-stress errors: 2nd/3rd-order PLL steady-state error to acceleration/jerk
    (omega0 = Bn/0.53, Bn/0.7845), FLL error to jerk; Doppler and Doppler rate at L1.
 3. Oscillator effects: Allan-deviation jitter (3rd order: 160*sigmaA*fL/Bn deg),
    acceleration sensitivity (g-sensitivity) frequency shift, vibration-induced jitter.
 4. Time-domain simulation of a 3rd-order PLL (Kaplan loop-filter coefficients a3=1.1, b3=2.4)
    driven by a rocket ignition/boost/burnout LOS-phase profile plus thermal phase noise:
    peak phase error and cycle slips vs thrust rise time, acceleration and loop bandwidth.
Run: python3 tools/verify/gnss_tracking_loops.py   (~10 s)
"""
import numpy as np

C = 299_792_458.0
fL1 = 1575.42e6
lam = C / fL1
g0 = 9.80665
ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


def db2lin(x):
    return 10 ** (x / 10)


# ------------------------------------------------------------------ 1. thermal noise
def sigma_pll_deg(cn0_db, Bn, T):
    c = db2lin(cn0_db)
    return np.degrees(np.sqrt(Bn / c * (1 + 1 / (2 * T * c))))


def sigma_fll_hz(cn0_db, Bn, T, F=1):
    c = db2lin(cn0_db)
    return 1 / (2 * np.pi * T) * np.sqrt(4 * F * Bn / c * (1 + 1 / (T * c)))


def sigma_dll_chips(cn0_db, Bn, T, d=1.0):
    c = db2lin(cn0_db)
    return np.sqrt(Bn * d / (2 * c) * (1 + 2 / (T * c * (2 - d))))


print("1) thermal-noise jitter")
for cn0 in [45, 35, 28, 25]:
    print(f"  C/N0={cn0} dB-Hz: PLL(Bn=15,T=1ms) {sigma_pll_deg(cn0,15,1e-3):5.1f} deg | "
          f"PLL(Bn=10,T=20ms) {sigma_pll_deg(cn0,10,20e-3):5.1f} deg | FLL(Bn=10,T=1ms) {sigma_fll_hz(cn0,10,1e-3):5.1f} Hz | "
          f"DLL(Bn=2,T=1ms,d=1) {sigma_dll_chips(cn0,2,1e-3)*293.05:5.2f} m")
# Kaplan rule: 3 sigma_PLL <= 45 deg (Costas). Find threshold C/N0 for thermal noise only.
from scipy.optimize import brentq
thr15 = brentq(lambda c: 3 * sigma_pll_deg(c, 15, 1e-3) - 45, 10, 60)
thr10_20 = brentq(lambda c: 3 * sigma_pll_deg(c, 10, 20e-3) - 45, 10, 60)
thr2_20 = brentq(lambda c: 3 * sigma_pll_deg(c, 2, 20e-3) - 45, 5, 60)
print(f"  thermal-only Costas threshold (3 sigma = 45 deg): Bn=15 T=1ms {thr15:.1f} dB-Hz; "
      f"Bn=10 T=20ms {thr10_20:.1f}; Bn=2 T=20ms {thr2_20:.1f}")
check("PLL 3-sigma thermal threshold ~ 27-29 dB-Hz for Bn=15 Hz, T=1 ms", 26 < thr15 < 30)
check("narrow/long PLL (2 Hz, 20 ms) tracks to ~15-18 dB-Hz (static receivers)", 14 < thr2_20 < 19)
fll_thr = brentq(lambda c: 3 * sigma_fll_hz(c, 10, 1e-3, F=2) - 1 / (4 * 1e-3), 5, 60)
print(f"  FLL (Bn=10 Hz, T=1 ms) threshold 3 sigma = 1/(4T)=250 Hz: {fll_thr:.1f} dB-Hz")

# ------------------------------------------------------------------ 2. dynamics
def w0_2(Bn): return Bn / 0.53


def w0_3(Bn): return Bn / 0.7845


print("\n2) dynamics at L1 (lambda = %.4f m)" % lam)
for v in [300, 500, 600, 1000]:
    print(f"  LOS velocity {v:4d} m/s -> Doppler {v/lam/1e3:5.2f} kHz")
for a_g in [4, 10, 15, 20]:
    a = a_g * g0
    print(f"  LOS accel {a_g:2d} g -> Doppler rate {a/lam:6.0f} Hz/s ; 2nd-order PLL error "
          f"(Bn=15) {np.degrees(2*np.pi*a/lam/w0_2(15)**2):6.0f} deg")
e_acc_2nd = np.degrees(2 * np.pi * (4 * g0) / lam / w0_2(15) ** 2)
check(f"2nd-order PLL, Bn=15 Hz: 4 g gives {e_acc_2nd:.0f} deg steady error (> 45 deg: needs 3rd order)",
      e_acc_2nd > 45)
print("  3rd-order PLL steady error to constant jerk J: theta = 360*J/(lambda*w0^3)")
for J_gps in [10, 50, 150, 300]:
    J = J_gps * g0
    for Bn in [10, 15, 25]:
        th = 360 * J / (lam * w0_3(Bn) ** 3)
        print(f"    jerk {J_gps:3d} g/s, Bn={Bn:2d} Hz -> {th:7.1f} deg")
th_ref = 360 * (10 * g0) / (lam * w0_3(15) ** 3)
check(f"3rd-order Bn=15 Hz: 10 g/s of jerk already costs ~{th_ref:.0f} deg (over a 15 deg share of the budget)",
      20 < th_ref < 35)
Jmax15 = 15 * lam * w0_3(15) ** 3 / 360
Jmax25 = 15 * lam * w0_3(25) ** 3 / 360
print(f"  jerk giving 15 deg (1/3 of 45 deg budget): Bn=15 -> {Jmax15/g0:.1f} g/s ; Bn=25 -> {Jmax25/g0:.1f} g/s")

# ------------------------------------------------------------------ 3. oscillator
print("\n3) oscillator contributions")
for sa in [1e-11, 1e-10, 1e-9]:
    print(f"  Allan dev {sa:.0e} (tau=1/Bn), Bn=15, 3rd order -> {160*sa*fL1/15:6.2f} deg")
for gam in [0.5e-9, 1e-9, 2e-9]:
    print(f"  g-sensitivity {gam*1e9:.1f} ppb/g at 15 g -> {gam*15*fL1:5.1f} Hz at L1 (common-mode step)")
# vibration: flat 0.04 g^2/Hz 20-2000 Hz (~8.9 grms) and GEVS-like profile
fm = np.linspace(20, 2000, 20000)
def gevs(f):   # NASA GEVS qualification random vibe (14.1 grms) shape: +6 dB/oct 20-50, 0.16 50-800, -6 dB/oct 800-2000
    p = np.where(f < 50, 0.026 * (f / 20) ** 2, np.where(f <= 800, 0.16, 0.16 * (800 / f) ** 2))
    return p
grms = np.sqrt(np.trapezoid(gevs(fm), fm))
for gam in [1e-9]:
    for Bn in [0, 15]:
        m = fm > Bn
        sv = np.degrees(fL1 * np.sqrt(np.trapezoid(gam ** 2 * gevs(fm[m]) / fm[m] ** 2, fm[m])))
        print(f"  vibration {grms:.1f} grms (GEVS shape), Gamma=1 ppb/g -> phase jitter {sv:.1f} deg")
check("GEVS-like profile integrates to ~14 grms", abs(grms - 14.1) < 1.0)

# ------------------------------------------------------------------ 4. time-domain PLL on a rocket
def rocket_profile(a_boost_g=15.0, t_rise=0.1, t_burn=3.0, t_fall=0.2, elev_deg=60.0,
                   dt=1e-3, t_end=6.0, t_pad=0.5):
    """LOS range (m) along a vertical flight, satellite at elevation elev (LOS = v*sin(el)).
    net acceleration ramps 0 -> a in t_rise at ignition, holds, ramps down to -1.3 g (drag+g) in t_fall."""
    t = np.arange(0, t_end, dt)
    a = np.zeros_like(t)
    tb0 = t_pad
    for i, ti in enumerate(t):
        if ti < tb0:
            a[i] = 0.0
        elif ti < tb0 + t_rise:
            a[i] = a_boost_g * g0 * (ti - tb0) / t_rise
        elif ti < tb0 + t_burn:
            a[i] = a_boost_g * g0
        elif ti < tb0 + t_burn + t_fall:
            a[i] = a_boost_g * g0 + (-1.3 * g0 - a_boost_g * g0) * (ti - tb0 - t_burn) / t_fall
        else:
            a[i] = -1.3 * g0
    v = np.cumsum(a) * dt
    r = np.cumsum(v) * dt
    s = np.sin(np.radians(elev_deg))
    return t, r * s, v * s, a * s


def pll3_sim(los_range, dt, Bn, cn0_db, T=1e-3, gamma=0.0, accel=None, seed=0, Bn_fll=0.0):
    """3rd-order PLL (Kaplan: w0^3, a3=1.1 w0^2, b3=2.4 w0) updated every T=dt, optionally
    assisted by a 2nd-order FLL (Kaplan Fig. 8.26 structure: w0f^2 and a2=1.414 w0f terms).
    Input phase = -2 pi R/lambda (+ oscillator phase from g-sensitivity).
    Returns (true phase error array [rad], true frequency error array [Hz])."""
    rng = np.random.default_rng(seed)
    w0 = w0_3(Bn)
    wf = w0_2(Bn_fll) if Bn_fll > 0 else 0.0
    phi_in = -2 * np.pi * los_range / lam
    if gamma and accel is not None:
        dfo = gamma * fL1 * np.abs(accel) / np.sin(np.radians(60))   # oscillator sees total accel
        phi_in = phi_in + 2 * np.pi * np.cumsum(dfo) * dt
    w_in = np.gradient(phi_in, dt)
    sig = np.sqrt(1 / (2 * T * db2lin(cn0_db)))        # rad, thermal (per discriminator output)
    x1 = x2 = 0.0
    phi_nco = phi_in[0]
    w = 0.0
    err = np.zeros_like(phi_in)
    ferr = np.zeros_like(phi_in)
    e_prev_meas = 0.0
    for k in range(len(phi_in)):
        e_true = phi_in[k] - phi_nco
        err[k] = e_true
        ferr[k] = (w_in[k] - w) / (2 * np.pi)
        e_meas = e_true + sig * rng.standard_normal()
        ep = (e_meas + np.pi / 2) % np.pi - np.pi / 2           # Costas: pi-periodic
        ef = 0.0
        if wf > 0 and k > 0:                                    # FLL: atan(cross/dot), +-pi/2 per T
            dphi = e_meas - e_prev_meas
            ef = ((dphi + np.pi / 2) % np.pi - np.pi / 2) / T
        e_prev_meas = e_meas
        x1 += (w0 ** 3 * ep + wf ** 2 * ef) * dt
        x2 += (1.1 * w0 ** 2 * ep + 1.414 * wf * ef + x1) * dt
        w = 2.4 * w0 * ep + x2
        phi_nco += w * dt
    return err, ferr


def run_case(a_g, tr, Bn, Bn_fll=0.0, cn0=40, t_fall=0.2, seed=0):
    t, R, V, A = rocket_profile(a_g, tr, t_fall=t_fall)
    e, fe = pll3_sim(R, 1e-3, Bn, cn0, Bn_fll=Bn_fll, seed=seed)
    wrapped = np.abs(e - e[0]) > np.pi / 2               # a Costas half-cycle slip has occurred
    first = t[np.argmax(wrapped)] if wrapped.any() else None
    relock = abs(np.mean(fe[-500:])) < 5.0                # frequency error < 5 Hz at the end
    slips = int(np.round((e[-1] - e[0]) / np.pi))
    pk = np.degrees(np.max(np.abs(e[: np.argmax(wrapped)] if wrapped.any() else e)))
    return first, relock, slips, pk


print("\n4) 3rd-order PLL on a vertical boost (satellite at 60 deg elevation, C/N0 = 40 dB-Hz, T = 1 ms)")
print("   profile: pad 0.5 s, ignition ramp 0->a in t_rise, 3 s burn, burnout ramp to -1.3 g in 0.2 s")
print("   a[g] rise[s] Bn  | PLL only: 1st slip [s]  re-locked  peak err before slip [deg] | FLL(10 Hz)-assisted: slips  re-locked")
results = {}
for a_g in [5, 10, 15, 20]:
    for tr in [0.05, 0.2, 0.5]:
        for Bn in [10, 15, 25]:
            r_p = run_case(a_g, tr, Bn)
            r_f = run_case(a_g, tr, Bn, Bn_fll=10)
            results[(a_g, tr, Bn)] = (r_p, r_f)
            fs_ = f"{r_p[0]:.2f}" if r_p[0] is not None else "none"
            print(f"   {a_g:3d}  {tr:5.2f}  {Bn:3d} |   {fs_:>6s}        {str(r_p[1]):5s}      {r_p[3]:6.0f}"
                  f"                   |   {r_f[2]:+5d}   {str(r_f[1]):5s}")
check("gentle ignition (5 g in 0.5 s), Bn=25 Hz: 3rd-order PLL keeps lock (no slip) through boost and burnout",
      results[(5, 0.5, 25)][0][0] is None)
check("hard ignition (15 g in 50 ms), Bn=15 Hz: PLL alone slips and does not recover",
      results[(15, 0.05, 15)][0][0] is not None and not results[(15, 0.05, 15)][0][1])
check("FLL-assisted loop keeps frequency lock (re-locks) in the hard case 15 g / 50 ms, Bn=15",
      results[(15, 0.05, 15)][1][1])
check("wider PLL (25 Hz) survives cases that break 10 Hz (e.g. 10 g / 0.2 s)",
      results[(10, 0.2, 25)][0][0] is None and results[(10, 0.2, 10)][0][0] is not None)

t, R, V, A = rocket_profile(15, 0.2)
print(f"\n   15 g boost, el 60 deg: peak LOS vel {V.max():.0f} m/s -> Doppler {V.max()/lam:.0f} Hz; "
      f"Doppler rate {A.max()/lam:.0f} Hz/s; LOS jerk at ignition {np.max(np.diff(A))/1e-3/g0:.0f} g/s, "
      f"at burnout {np.min(np.diff(A))/1e-3/g0:.0f} g/s")

# FLL tolerance: 2nd-order FLL error to jerk f_e = J/(lambda w0^2); threshold 1/(4T)
for Bn in [2, 5, 10]:
    J_tol = (1 / (4e-3) / 3) * lam * w0_2(Bn) ** 2   # jerk for f_e = 1/(12T) (one third of budget)
    print(f"   2nd-order FLL Bn={Bn:2d} Hz, T=1 ms: jerk for f_e = 83 Hz -> {J_tol/g0:6.0f} g/s")
check("FLL tolerates far more jerk than a PLL of similar bandwidth (why receivers fall back to FLL)",
      (1 / (4e-3) / 3) * lam * w0_2(10) ** 2 > Jmax15 * 10)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
