#!/usr/bin/env python3
# Runtime (W6-F5, 2026-10-14): ~220 s (3.7 min) measured on a 10-core Apple-silicon Mac, run 3 at a time
# under load average 7-70 from other jobs; expect less on an idle machine. It exceeds the 120 s per-script budget
# used by the D7 verify sweep, so give it a >= 15 min timeout and run it with `python3 -u` to see progress.
# Measured run: exit 0, no FAIL lines. Comment only; no code or results changed.
"""Verification + worked designs for kb/06-rf-circuits/lna-design.md

 A. Power-gain definitions G_T, G_A, G_P: check against direct wave computation; G_T <= G_A, G_P
 B. Simultaneous conjugate match (SCM) formulas; G_T(SCM) = MAG
 C. Noise-circle formula vs brute-force F(Gamma_s); available-gain circle formula
 D. Unilateral figure of merit bounds
 E. Inductive source degeneration (CMOS): Re Zin = wT*Ls, F = 1 + gamma*gd0*Rs*(w0/wT)^2, gate-inductor loss
 F. Worked ATF-54143 LNAs at 433 MHz and 1575.42 MHz (realistic high-pass topology with
    resistive LF terminations in the bias feeds), optimised for NF with stability/return-loss
    constraints, rounded to E12 values, re-evaluated with finite component Q
 G. Input-limiter / damage budget for a rocket-telemetry ground station
Run: python3 tools/verify/rfckt_lna.py   (takes ~1-2 min: differential evolution)
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rfckt_atf54143_data import interp_s, interp_noise
from rfckt_noise2port import (device, series_z, shunt_y, cascade, noise_factor, noise_params,
                              abcd_to_s, s_to_abcd, parallel_feedback)
from scipy.optimize import differential_evolution

rng = np.random.default_rng(7)
ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


def delta(S):
    return S[..., 0, 0] * S[..., 1, 1] - S[..., 0, 1] * S[..., 1, 0]


def Kf(S):
    return (1 - abs(S[..., 0, 0]) ** 2 - abs(S[..., 1, 1]) ** 2 + abs(delta(S)) ** 2) / (2 * abs(S[..., 0, 1] * S[..., 1, 0]))


def mu(S):
    D = delta(S)
    return (1 - abs(S[..., 0, 0]) ** 2) / (abs(S[..., 1, 1] - D * np.conj(S[..., 0, 0])) + abs(S[..., 0, 1] * S[..., 1, 0]))


def gin(S, GL):
    return S[0, 0] + S[0, 1] * S[1, 0] * GL / (1 - S[1, 1] * GL)


def gout(S, GS):
    return S[1, 1] + S[0, 1] * S[1, 0] * GS / (1 - S[0, 0] * GS)


def GT(S, GS, GL):
    return (1 - abs(GS) ** 2) * abs(S[1, 0]) ** 2 * (1 - abs(GL) ** 2) / abs((1 - S[0, 0] * GS) * (1 - S[1, 1] * GL) - S[0, 1] * S[1, 0] * GS * GL) ** 2


def GA(S, GS):
    Go = gout(S, GS)
    return (1 - abs(GS) ** 2) * abs(S[1, 0]) ** 2 / (abs(1 - S[0, 0] * GS) ** 2 * (1 - abs(Go) ** 2))


def GP(S, GL):
    Gi = gin(S, GL)
    return abs(S[1, 0]) ** 2 * (1 - abs(GL) ** 2) / ((1 - abs(Gi) ** 2) * abs(1 - S[1, 1] * GL) ** 2)


def random_stable_S():
    while True:
        S = np.array([[0.6 * rng.random() * np.exp(2j * np.pi * rng.random()), 0.1 * rng.random() * np.exp(2j * np.pi * rng.random())],
                      [5 * rng.random() * np.exp(2j * np.pi * rng.random()), 0.6 * rng.random() * np.exp(2j * np.pi * rng.random())]])
        if mu(S[None])[0] > 1.02:
            return S


# ---------------------------------------------------------------- A. gain definitions
worst = 0
order_ok = True
for _ in range(2000):
    S = random_stable_S()
    GS = 0.9 * rng.random() * np.exp(2j * np.pi * rng.random())
    GL = 0.9 * rng.random() * np.exp(2j * np.pi * rng.random())
    # direct: source wave bs with |bs|^2 = P_avs*(1-|GS|^2); a1 = bs/(1 - GS*Gin)
    Gi = gin(S, GL)
    bs = 1.0
    Pavs = abs(bs) ** 2 / (1 - abs(GS) ** 2)
    a1 = bs / (1 - GS * Gi)
    b2 = S[1, 0] * a1 / (1 - S[1, 1] * GL)
    PL = abs(b2) ** 2 * (1 - abs(GL) ** 2)
    worst = max(worst, abs(PL / Pavs - GT(S, GS, GL)) / GT(S, GS, GL))
    order_ok &= GT(S, GS, GL) <= GA(S, GS) * (1 + 1e-12) and GT(S, GS, GL) <= GP(S, GL) * (1 + 1e-12)
check(f"A1 G_T formula equals P_L/P_avs from wave analysis (rel err {worst:.1e})", worst < 1e-10)
check("A2 G_T <= G_A and G_T <= G_P for passive terminations", order_ok)

# ---------------------------------------------------------------- B. simultaneous conjugate match
worst = 0
for _ in range(500):
    S = random_stable_S()
    D = delta(S[None])[0]
    B1 = 1 + abs(S[0, 0]) ** 2 - abs(S[1, 1]) ** 2 - abs(D) ** 2
    B2 = 1 + abs(S[1, 1]) ** 2 - abs(S[0, 0]) ** 2 - abs(D) ** 2
    C1 = S[0, 0] - D * np.conj(S[1, 1])
    C2 = S[1, 1] - D * np.conj(S[0, 0])
    GMs = (B1 - np.sqrt(B1 ** 2 - 4 * abs(C1) ** 2 + 0j)) / (2 * C1)
    GMl = (B2 - np.sqrt(B2 ** 2 - 4 * abs(C2) ** 2 + 0j)) / (2 * C2)
    k = Kf(S[None])[0]
    MAG = abs(S[1, 0] / S[0, 1]) * (k - np.sqrt(k ** 2 - 1))
    e = max(abs(gin(S, GMl) - np.conj(GMs)), abs(gout(S, GMs) - np.conj(GMl)), abs(GT(S, GMs, GMl) / MAG - 1))
    worst = max(worst, e)
check(f"B1 SCM: Gin(GML)=GMS*, Gout(GMS)=GML*, G_T=MAG (max err {worst:.1e})", worst < 1e-5)

# ---------------------------------------------------------------- C. noise and gain circles
S = np.array([[0.64 * np.exp(-1j * np.deg2rad(149.8)), 0.05 * np.exp(1j * np.deg2rad(36.1))],
              [9.34 * np.exp(1j * np.deg2rad(86.1)), 0.21 * np.exp(-1j * np.deg2rad(105.2))]])  # ATF 1.5 GHz
Fmin, Gopt, Rn = 10 ** (0.35 / 10), 0.30 * np.exp(1j * np.deg2rad(90)), 2.0
A, Cm = device(S[None], np.array([Fmin]), np.array([Gopt]), np.array([Rn]))
worst = 0
for NFdb in (0.5, 0.8, 1.5):
    Fi = 10 ** (NFdb / 10)
    N = (Fi - Fmin) / (4 * Rn / 50) * abs(1 + Gopt) ** 2
    CF = Gopt / (N + 1)
    RF = np.sqrt(N * (N + 1 - abs(Gopt) ** 2)) / (N + 1)
    pts = CF + RF * np.exp(1j * np.linspace(0, 2 * np.pi, 72))
    Zs = 50 * (1 + pts) / (1 - pts)
    Fpts = noise_factor(np.repeat(Cm, len(pts), axis=0), Zs)
    worst = max(worst, np.max(abs(Fpts - Fi)))
check(f"C1 noise circle (Pozar) matches brute-force F on circle (max err {worst:.1e})", worst < 1e-9)
# available-gain circle: ga = GA/|S21|^2
ga_target = 10 ** (20 / 10) / abs(S[1, 0]) ** 2
D = delta(S[None])[0]
C1c = S[0, 0] - D * np.conj(S[1, 1])
den = 1 + ga_target * (abs(S[0, 0]) ** 2 - abs(D) ** 2)
CA = ga_target * np.conj(C1c) / den
k = Kf(S[None])[0]
RA = np.sqrt(1 - 2 * k * abs(S[0, 1] * S[1, 0]) * ga_target + abs(S[0, 1] * S[1, 0]) ** 2 * ga_target ** 2) / abs(den)
pts = CA + RA * np.exp(1j * np.linspace(0, 2 * np.pi, 72))
gerr = np.max(abs(10 * np.log10(np.array([GA(S, p) for p in pts])) - 20))
check(f"C2 available-gain circle formula (max err {gerr:.1e} dB)", gerr < 1e-8)

# ---------------------------------------------------------------- D. unilateral figure of merit
S = interp_s(np.array([1575.42e6]))[0]
U = abs(S[0, 0] * S[0, 1] * S[1, 0] * S[1, 1]) / ((1 - abs(S[0, 0]) ** 2) * (1 - abs(S[1, 1]) ** 2))
lo, hi = 10 * np.log10(1 / (1 + U) ** 2), 10 * np.log10(1 / (1 - U) ** 2)
print(f"D: ATF-54143 @1575 MHz: U = {U:.3f} -> unilateral-approximation error bounds {lo:+.2f} .. {hi:+.2f} dB")
check("D1 U-bounds are finite (U<1)", U < 1)

# ---------------------------------------------------------------- E. inductive source degeneration
Cgs, gm, gamma, Rs = 200e-15, 40e-3, 2 / 3, 50.0
wT = gm / Cgs
f0 = 1575.42e6
w0 = 2 * np.pi * f0
Ls = Rs / wT
Lg = 1 / (w0 ** 2 * Cgs) - Ls
# direct circuit solve at w0 (see derivation in page)
w = w0
def solve(vs, i_d):
    # unknown ig; vs = ig*(Rs + jw(Lg+Ls) + 1/(jwCgs) + gm*Ls/Cgs) + jw*Ls*i_d
    Zloop = Rs + 1j * w * (Lg + Ls) + 1 / (1j * w * Cgs) + gm * Ls / Cgs
    ig = (vs - 1j * w * Ls * i_d) / Zloop
    return gm * ig / (1j * w * Cgs) + i_d
Zin = 1j * w * (Lg + Ls) + 1 / (1j * w * Cgs) + gm * Ls / Cgs
Hv = solve(1.0, 0.0)
Hi = solve(0.0, 1.0)
F_direct = 1 + abs(Hi) ** 2 * gamma * gm / (abs(Hv) ** 2 * Rs)   # <id^2>=4kT*gamma*gd0, <vs^2>=4kT*Rs, gd0=gm
F_formula = 1 + gamma * gm * Rs * (w0 / wT) ** 2
print(f"E: fT = {wT/2/np.pi/1e9:.1f} GHz, Ls = {Ls*1e9:.3f} nH, Lg = {Lg*1e9:.1f} nH, Zin = {Zin:.2f} ohm, "
      f"Q_in = {1/(w0*Cgs*2*Rs):.2f}, Gm = {abs(Hv)*1e3:.0f} mS (wT/(2 w0 Rs) = {wT/(2*w0*Rs)*1e3:.0f} mS)")
print(f"   channel-noise-only NF: direct {10*np.log10(F_direct):.3f} dB, formula {10*np.log10(F_formula):.3f} dB; "
      f"noise current at output halved: |H_id| = {abs(Hi):.3f}")
QLg = 20
RLg = w0 * Lg / QLg
F_withL = F_formula + RLg / Rs
print(f"   with Lg Q = {QLg}: R_Lg = {RLg:.1f} ohm -> NF = {10*np.log10(F_withL):.2f} dB (inductor loss dominates)")
check("E1 Re(Zin) = wT*Ls = Rs at resonance", abs(Zin - Rs) < 1e-6)
check("E2 channel-noise F from circuit solve equals 1 + gamma*gd0*Rs*(w0/wT)^2", abs(F_direct - F_formula) < 1e-12)
check("E3 effective Gm = wT/(2 w0 Rs)", abs(abs(Hv) - wT / (2 * w0 * Rs)) < 1e-9)

# ---------------------------------------------------------------- F. worked ATF-54143 LNAs
FSWEEP = np.unique(np.concatenate([np.geomspace(0.1e9, 10e9, 220), [433e6, 1575.42e6]]))
E12 = np.array([1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2])


def e12(x):
    dec = 10 ** np.floor(np.log10(x))
    cand = np.concatenate([E12 * dec / 10, E12 * dec, E12 * dec * 10])
    return cand[np.argmin(abs(np.log(cand / x)))]


VDD, VDS, IDS, IBB = 5.0, 3.0, 0.060, 0.002
RDC = (VDD - VDS) / (IDS + IBB)          # total DC resistance allowed in the drain feed (32.3 ohm)


def build(p, f, real=False, QL=40, QC=400, ESL=0.4e-9, CPAR=0.12e-12):
    """p = [C1, L1, C2, R4, Rd, L4, C5, C4, Rf, Cf]; R3 = RDC - Rd (DC constraint, 5 V supply).
    Rf + Cf in series form an optional drain-to-gate (shunt-shunt) feedback branch.

    real=False: ideal L and C.  real=True: inductors with Q=QL and parallel CPAR (0603 wire-wound
    class: 100 nH -> SRF 1.45 GHz), capacitors with ESR from QC and series ESL (0402 class).
    Returns (S, CA) of the complete amplifier between 50-ohm connectors.
    """
    C1, L1, C2, R4, Rd, L4, C5, C4, Rf, Cf = p
    R3 = max(RDC - Rd, 0.0)
    w = 2 * np.pi * f
    def zL(L):
        if not real:
            return 1j * w * L
        z = 1j * w * L + w * L / QL
        return 1 / (1 / z + 1j * w * CPAR)
    def zC(C):
        if not real:
            return 1 / (1j * w * C)
        return 1 / (1j * w * C) + 1 / (w * C) / QC + 1j * w * ESL
    C3 = C6 = 100e-9
    zA = 1 / (1 / zC(C2) + 1 / (R4 + zC(C3)))       # node A: RF bypass || (R4 + big bypass)
    zB = 1 / (1 / zC(C5) + 1 / (R3 + zC(C6)))       # node B: RF bypass || (R3 + big bypass)
    fmin, gopt, rn = interp_noise(f)
    dv = device(interp_s(f), fmin, gopt, rn)
    if Rf < 9.9e3:
        dv = parallel_feedback(dv, 1 / (Rf + zC(Cf)))
    net = cascade(series_z(zC(C1)), shunt_y(1 / (zL(L1) + zA)), dv,
                  series_z(Rd * np.ones_like(f)), shunt_y(1 / (zL(L4) + zB)), series_z(zC(C4)))
    return abcd_to_s(net[0]), net[1]


def metrics(p, f0, real=False, f=FSWEEP, **kw):
    S, C = build(p, f, real, **kw)
    i0 = np.argmin(abs(f - f0))
    F = noise_factor(C)
    return dict(NF=10 * np.log10(F[i0]), G=20 * np.log10(abs(S[i0, 1, 0])),
                S11=20 * np.log10(abs(S[i0, 0, 0])), S22=20 * np.log10(abs(S[i0, 1, 1])),
                mu_min=mu(S).min(), f_mu=f[np.argmin(mu(S))], S=S, F=F)


bounds_log = [(0.5e-12, 100e-12), (1e-9, 100e-9), (0.5e-12, 150e-12), (10, 470),
              (0.01, 22), (1e-9, 100e-9), (0.5e-12, 150e-12), (0.5e-12, 100e-12),
              (100, 1e4), (0.5e-12, 100e-12)]
lb = np.log10([b[0] for b in bounds_log]); ub = np.log10([b[1] for b in bounds_log])


def cost(x, f0):
    p = 10 ** x
    fl = np.unique(np.concatenate([np.geomspace(0.1e9, 10e9, 90), [f0]]))
    mr = metrics(p, f0, real=True, f=fl)
    mi = metrics(p, f0, real=False, f=fl)
    mq = metrics(p, f0, real=True, f=fl, QL=100, QC=1000)
    c = mr['NF']
    c += 5 * max(0, 1.08 - min(mr['mu_min'], mi['mu_min'], mq['mu_min']))   # stable: ideal, Q=40, Q=100
    c += 0.2 * max(0, mr['S11'] + 9)                # input return loss >= 9 dB
    c += 0.2 * max(0, mr['S22'] + 14)               # output return loss >= 14 dB
    c += 0.2 * max(0, 16 - mr['G'])                 # gain >= 16 dB
    return c


designs = {}
for f0, tag in [(433e6, '433 MHz'), (1575.42e6, '1575.42 MHz')]:
    res = differential_evolution(cost, list(zip(lb, ub)), args=(f0,), seed=3, maxiter=250, popsize=25,
                                 tol=1e-7, polish=True, updating='deferred', workers=1)
    p_opt = 10 ** res.x
    p_e12 = np.array([e12(v) for v in p_opt])
    if p_opt[8] > 5e3:
        p_e12[8] = 1e4   # feedback not used
    fmin, gopt, rn = interp_noise(np.array([f0]))
    print(f"\nF: ATF-54143 LNA at {tag}: device NFmin = {10*np.log10(fmin[0]):.2f} dB, "
          f"Gamma_opt = {abs(gopt[0]):.2f} @ {np.degrees(np.angle(gopt[0])):.0f} deg")
    names = ['C1', 'L1', 'C2', 'R4', 'Rd', 'L4', 'C5', 'C4', 'Rf', 'Cf']
    units = ['pF', 'nH', 'pF', 'ohm', 'ohm', 'nH', 'pF', 'pF', 'ohm', 'pF']
    scale = [1e12, 1e9, 1e12, 1, 1, 1e9, 1e12, 1e12, 1, 1e12]
    print("   component   optimum    E12")
    for n, u, sc, a, b in zip(names, units, scale, p_opt, p_e12):
        print(f"   {n:4s} {a*sc:10.2f} {b*sc:9.2f} {u}")
    print(f"   R3 (drain feed, from DC constraint) = {RDC - p_e12[4]:.1f} ohm")
    for lab, p, real, kw in [('optimum, real parts', p_opt, True, {}),
                             ('E12, ideal parts', p_e12, False, {}),
                             ('E12, real parts Q=40', p_e12, True, {}),
                             ('E12, real parts Q=25', p_e12, True, dict(QL=25, QC=200)),
                             ('E12, real, Q=80', p_e12, True, dict(QL=80, QC=800))]:
        m = metrics(p, f0, real, **kw)
        print(f"   {lab:22s}: NF {m['NF']:.2f} dB  G_T {m['G']:.1f} dB  S11 {m['S11']:.1f} dB  "
              f"S22 {m['S22']:.1f} dB  mu_min {m['mu_min']:.2f} (at {m['f_mu']/1e9:.2f} GHz)")
    designs[tag] = (f0, p_e12, metrics(p_e12, f0, True), metrics(p_e12, f0, False))

m433 = designs['433 MHz'][2]
m1575 = designs['1575.42 MHz'][2]
i433, i1575 = designs['433 MHz'][3], designs['1575.42 MHz'][3]
check("F1 433 MHz design: NF < 1.0 dB, G_T > 16 dB, mu>1 0.1-10 GHz with real AND ideal parts",
      m433['NF'] < 1.0 and m433['G'] > 16 and m433['mu_min'] > 1.0 and i433['mu_min'] > 1.0)
check("F2 1575 MHz design: NF < 1.0 dB, G_T > 15 dB, mu>1 0.1-10 GHz with real AND ideal parts",
      m1575['NF'] < 1.0 and m1575['G'] > 15 and m1575['mu_min'] > 1.0 and i1575['mu_min'] > 1.0)
# out-of-band gain (why the 433 MHz LNA still needs a filter)
for tag in designs:
    f0, p, m, _ = designs[tag]
    S = m['S']
    for fo in (0.1e9, 0.9e9, 1.575e9, 2.4e9, 5.8e9):
        i = np.argmin(abs(FSWEEP - fo))
        print(f"   {tag} amp: |S21| at {FSWEEP[i]/1e9:5.2f} GHz = {20*np.log10(abs(S[i,1,0])):6.1f} dB")

# ---------------------------------------------------------------- H. noise circles of the bare device
for f0 in (433e6, 1575.42e6):
    fm, go, rn_ = interp_noise(np.array([f0]))
    fm, go, rn_ = fm[0], go[0], rn_[0]
    line = f"H: {f0/1e6:.0f} MHz noise circles (Fmin {10*np.log10(fm):.2f} dB, Rn {rn_:.1f} ohm):"
    for NFdb in (0.3, 0.5, 1.0):
        Fi = 10 ** (NFdb / 10)
        if Fi <= fm:
            continue
        N = (Fi - fm) / (4 * rn_ / 50) * abs(1 + go) ** 2
        CF, RF = go / (N + 1), np.sqrt(N * (N + 1 - abs(go) ** 2)) / (N + 1)
        line += f"  {NFdb} dB: C={abs(CF):.2f}@{np.degrees(np.angle(CF)):.0f}deg r={RF:.2f};"
    # NF of the bare device with a plain 50-ohm source
    F50 = fm + rn_ / 0.02 * abs(0.02 - (1 - go) / (1 + go) / 50) ** 2
    print(line + f"  NF(Zs=50) = {10*np.log10(F50):.2f} dB")

# ---------------------------------------------------------------- I. tolerance Monte Carlo
for tag in designs:
    f0, p, _, _ = designs[tag]
    NFs, mus, Gs = [], [], []
    for _ in range(300):
        q = p.copy()
        tol = np.array([0.05, 0.05, 0.05, 0.01, 0.01, 0.05, 0.05, 0.05, 0.01, 0.05])
        q = q * (1 + tol * rng.uniform(-1, 1, len(q)))
        QL = rng.uniform(25, 80)
        m = metrics(q, f0, True, QL=QL, QC=10 * QL)
        NFs.append(m['NF']); mus.append(m['mu_min']); Gs.append(m['G'])
    NFs, mus, Gs = map(np.array, (NFs, mus, Gs))
    print(f"I: {tag}: 300 trials (+-5% L/C, +-1% R, Q 25-80): NF {NFs.mean():.2f} dB "
          f"(max {NFs.max():.2f}), G {Gs.mean():.1f}+-{Gs.std():.1f} dB, mu>1 in {100*np.mean(mus>1):.0f}% "
          f"(min mu {mus.min():.2f})")
    check(f"I1 {tag}: >= 90% of tolerance trials remain unconditionally stable", np.mean(mus > 1) >= 0.9)

# ---------------------------------------------------------------- J. series (source) inductive feedback
def abcd_to_z(A):
    a, b, c, d = A[:, 0, 0], A[:, 0, 1], A[:, 1, 0], A[:, 1, 1]
    Z = np.zeros_like(A)
    Z[:, 0, 0] = a / c; Z[:, 0, 1] = (a * d - b * c) / c; Z[:, 1, 0] = 1 / c; Z[:, 1, 1] = d / c
    return Z


def z_to_abcd(Z):
    z11, z12, z21, z22 = Z[:, 0, 0], Z[:, 0, 1], Z[:, 1, 0], Z[:, 1, 1]
    dZ = z11 * z22 - z12 * z21
    A = np.zeros_like(Z)
    A[:, 0, 0] = z11 / z21; A[:, 0, 1] = dZ / z21; A[:, 1, 0] = 1 / z21; A[:, 1, 1] = z22 / z21
    return A


def series_feedback(el, Zfb):
    """Common-lead impedance Zfb (lossless here) added to a 2-port (series-series feedback)."""
    A, CA = el
    Z = abcd_to_z(A)
    T = np.zeros_like(A); T[:, 0, 0] = 1; T[:, 0, 1] = -Z[:, 0, 0]; T[:, 1, 1] = -Z[:, 1, 0]
    CZ = T @ CA @ np.conj(np.transpose(T, (0, 2, 1)))
    M = np.ones((2, 2), complex)
    Z2 = Z + np.asarray(Zfb)[:, None, None] * M
    CZ2 = CZ + np.asarray(Zfb).real[:, None, None] * M
    A2 = z_to_abcd(Z2)
    T2 = np.zeros_like(A2); T2[:, 0, 0] = 1; T2[:, 0, 1] = -A2[:, 0, 0]; T2[:, 1, 1] = -A2[:, 1, 0]
    return A2, T2 @ CZ2 @ np.conj(np.transpose(T2, (0, 2, 1)))


fj = np.array([1575.42e6])
fm, go, rn_ = interp_noise(fj)
base = device(interp_s(fj), fm, go, rn_)
print("J: source inductance at 1575.42 MHz (ATF-54143):  Ls   NFmin   Gamma_opt        S11*")
for Ls in (0.0, 0.2e-9, 0.5e-9):
    el = series_feedback(base, 1j * 2 * np.pi * fj * Ls) if Ls > 0 else base
    Fm_, Zo_, Rn_ = noise_params(el[1])
    Go_ = (Zo_ - 50) / (Zo_ + 50)
    S_ = abcd_to_s(el[0])
    print(f"   {Ls*1e9:4.1f} nH  {10*np.log10(Fm_[0]):.3f} dB  {abs(Go_[0]):.2f}@{np.degrees(np.angle(Go_[0])):5.0f}deg  "
          f"{abs(S_[0,0,0]):.2f}@{np.degrees(np.angle(np.conj(S_[0,0,0]))):5.0f}deg  "
          f"|Gopt - S11*| = {abs(Go_[0]-np.conj(S_[0,0,0])):.2f}")
# consistency with the S-parameter-only route in rfckt_stability.py (Z-matrix add)
el = series_feedback(base, 1j * 2 * np.pi * fj * 0.5e-9)
import skrf as rf
z = rf.network.s2z(interp_s(fj), 50) + 1j * 2 * np.pi * fj[0] * 0.5e-9
check("J1 series-feedback S-parameters agree with direct Z-matrix addition",
      np.allclose(abcd_to_s(el[0]), rf.network.z2s(z, 50), atol=1e-9))
Fm0 = noise_params(base[1])[0][0]; Fm5 = noise_params(el[1])[0][0]
check("J2 lossless source inductance changes NFmin by < 0.05 dB while moving S11* toward Gamma_opt",
      abs(10 * np.log10(Fm5 / Fm0)) < 0.05)

# ---------------------------------------------------------------- K. does a LoRa ground station need an LNA?
def db2lin(x): return 10 ** (x / 10)
NF_rx = -137 + 174 - 10 * np.log10(125e3) + 20          # SX126x SF12/BW125 sensitivity -> implied NF
L_cab = 3.0                                              # ~10 m RG-58 at 433 MHz
F_lna, G_lna = db2lin(0.38), db2lin(22.1)
F_A = db2lin(L_cab) * db2lin(NF_rx)                                   # no LNA
F_B = db2lin(L_cab) * (F_lna + (db2lin(NF_rx) - 1) / G_lna)           # LNA at the radio
F_C = F_lna + (db2lin(L_cab) - 1) / G_lna + (db2lin(NF_rx) - 1) / (G_lna / db2lin(L_cab))  # masthead
print(f"K: implied SX126x NF = {NF_rx:.1f} dB; system NF: no LNA {10*np.log10(F_A):.2f} dB, "
      f"LNA at radio {10*np.log10(F_B):.2f} dB, masthead LNA {10*np.log10(F_C):.2f} dB")
for Tant in (290, 1000):
    TA, TC = Tant + 290 * (F_A - 1), Tant + 290 * (F_C - 1)
    print(f"   T_ant = {Tant:4d} K: T_sys {TA:.0f} K -> {TC:.0f} K, SNR gain {10*np.log10(TA/TC):.1f} dB, "
          f"free-space range x{np.sqrt(TA/TC):.2f}")
check("K1 masthead LNA beats LNA-at-radio when cable loss precedes the radio", F_C < F_B < F_A)

# ---------------------------------------------------------------- G. damage budget
Ptx, Gtx, Grx = 33.0, 2.15, 10.0      # E22-400T33D 2 W, dipole, ground-station Yagi
lam = 3e8 / 433e6
for d in (1, 3, 10, 30, 100):
    Prx = Ptx + Gtx + Grx - 20 * np.log10(4 * np.pi * d / lam)
    print(f"G: rocket TX 2 W at {d:4d} m -> {Prx:6.1f} dBm at LNA input (far-field Friis; <~2 m is near-field, indicative)")
Prx3 = Ptx + Gtx + Grx - 20 * np.log10(4 * np.pi * 3 / lam)
check("G1 a 2 W transmitter a few metres from a 10 dBi Yagi exceeds a 0 dBm LNA rating", Prx3 > 0)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
sys.exit(0 if ok_all else 1)
