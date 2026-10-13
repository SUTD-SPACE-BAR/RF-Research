#!/usr/bin/env python3
"""
Verification for kb/03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md

Checks / computes:
  1. L-network for real loads: Q = sqrt(Rh/Rl - 1), X_series = Q*Rl, X_shunt = Rh/Q -> exact match (skrf).
  2. L-network for complex loads (Pozar sec. 5.1 closed forms), both solutions, both regions.
  3. Pi and T networks via a virtual resistance; loaded-Q vs bandwidth (brute-force sweep).
  4. Insertion loss of an L-network with finite component Q vs the estimate IL ~ 10log10(1 + Qn/Qu).
  5. Single shunt-stub tuning (open and short) closed forms vs skrf.
  6. Binomial N-section transformer: impedances, bandwidth formula vs exact cascade.
  7. Chebyshev N-section transformer: synthesis from small-reflection theory; ripple vs exact cascade.
  8. Klopfenstein taper: own implementation vs skrf.taper.Klopfenstein; passband |Gamma| <= Gamma_m.
  9. Worked examples at 433, 915, 2450 MHz used on the page.

Run: python3 tools/verify/tline_matching.py
"""
import warnings
import numpy as np
import skrf as rf
from math import comb
from scipy.special import i1
from scipy.integrate import quad

warnings.filterwarnings("ignore", category=DeprecationWarning)
c0 = 299_792_458.0
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


# ---------------- ABCD helpers ----------------
def ser(Z):
    Z = np.atleast_1d(Z)
    A = np.zeros((len(Z), 2, 2), complex)
    A[:, 0, 0] = 1; A[:, 1, 1] = 1; A[:, 0, 1] = Z
    return A


def shu(Y):
    Y = np.atleast_1d(Y)
    A = np.zeros((len(Y), 2, 2), complex)
    A[:, 0, 0] = 1; A[:, 1, 1] = 1; A[:, 1, 0] = Y
    return A


def tl(Zc, th):
    th = np.atleast_1d(th)
    A = np.zeros((len(th), 2, 2), complex)
    A[:, 0, 0] = np.cos(th); A[:, 1, 1] = np.cos(th)
    A[:, 0, 1] = 1j * Zc * np.sin(th); A[:, 1, 0] = 1j * np.sin(th) / Zc
    return A


def casc(*mats):
    out = mats[0]
    for m in mats[1:]:
        out = np.einsum("fij,fjk->fik", out, m)
    return out


def zin(A, ZL):
    return (A[:, 0, 0] * ZL + A[:, 0, 1]) / (A[:, 1, 0] * ZL + A[:, 1, 1])


def gam(Z, Z0=50.0):
    return (Z - Z0) / (Z + Z0)


def Lval(X, f):
    return X / (2 * np.pi * f)


def Cval(X, f):
    return -1 / (2 * np.pi * f * X)


# ---------------------------------------------------------------- 1. L-network, real loads
def lnet_real(Rs, RL):
    """return (Q, Xseries, Xshunt) with series element on the low-R side, shunt on the high-R side
    (low-pass version: series L, shunt C)"""
    Rh, Rl = max(Rs, RL), min(Rs, RL)
    Q = np.sqrt(Rh / Rl - 1)
    return Q, Q * Rl, -Rh / Q


f433 = 433e6
Q, Xs, Xp = lnet_real(50, 12.5)
# network from 50-ohm source: shunt C at 50 side (high), series L toward the 12.5 ohm load
A = casc(shu(np.array([1 / (1j * Xp)])), ser(np.array([1j * Xs])))
Zi = zin(A, 12.5)[0]
check("L-net 12.5 -> 50 ohm: Q = sqrt(3), exact match", abs(Q - np.sqrt(3)) < 1e-12 and abs(Zi - 50) < 1e-9,
      f"(series L = {Lval(Xs, f433)*1e9:.2f} nH, shunt C = {Cval(Xp, f433)*1e12:.2f} pF at 433 MHz)")
# independent: skrf media elements
freq = rf.Frequency(433, 433, 1, unit="MHz")
fs = rf.media.DefinedGammaZ0(frequency=freq, z0=50)
net = fs.shunt_capacitor(Cval(Xp, f433)) ** fs.inductor(Lval(Xs, f433)) ** \
    rf.Network(frequency=freq, s=np.array([gam(12.5)]), z0=50)
check("skrf cascade of the same L-net gives |S11| ~ 0", abs(net.s[0, 0, 0]) < 1e-9)


# ---------------------------------------------------------------- 2. L-network, complex loads (Pozar 5.1)
def lnet_complex(ZL, Z0=50.0):
    """Return list of (topology, X_series, B_shunt). Pozar sec. 5.1.
    topology 'shunt-at-load' (RL > Z0): shunt B across load, then series X toward source.
    topology 'series-at-load' (RL < Z0): series X at load, then shunt B toward source."""
    RL, XL = ZL.real, ZL.imag
    sols = []
    if RL > Z0:
        for s in (+1, -1):
            B = (XL + s * np.sqrt(RL / Z0) * np.sqrt(RL**2 + XL**2 - Z0 * RL)) / (RL**2 + XL**2)
            X = 1 / B + XL * Z0 / RL - Z0 / (B * RL)
            sols.append(("shunt-at-load", X, B))
    else:
        for s in (+1, -1):
            X = s * np.sqrt(RL * (Z0 - RL)) - XL
            B = s * np.sqrt((Z0 - RL) / RL) / Z0
            sols.append(("series-at-load", X, B))
    return sols


for ZL in [200 - 100j, 100 + 80j, 20 + 10j, 18 - 35j, 32.1 - 18.5j]:
    for topo, X, B in lnet_complex(ZL):
        if topo == "shunt-at-load":
            Zx = 1 / (1 / ZL + 1j * B) + 1j * X
        else:
            Zx = 1 / (1 / (ZL + 1j * X) + 1j * B)
        check(f"complex L-net {ZL} ({topo}, X={X:+.2f}, B={B*1e3:+.3f} mS) -> 50 ohm", abs(Zx - 50) < 1e-9)


# ---------------------------------------------------------------- 3. Pi / T networks and bandwidth
def pi_net(Rs, RL, Q):
    """Pi (shunt-series-shunt), low-pass form, loaded-Q set by the higher-R side: Rv = Rh/(Q^2+1)."""
    Rh = max(Rs, RL)
    Rv = Rh / (Q**2 + 1)
    assert Rv < min(Rs, RL), "Q too low for a Pi"
    Q1 = np.sqrt(Rs / Rv - 1)
    Q2 = np.sqrt(RL / Rv - 1)
    Xp1, Xs1 = -Rs / Q1, Q1 * Rv
    Xs2, Xp2 = Q2 * Rv, -RL / Q2
    return Rv, Q1, Q2, Xp1, Xs1 + Xs2, Xp2


def sweep_bw(Aof, ZL, f0, rl_db=10.0, span=0.9):
    f = f0 * np.linspace(1 - span, 1 + span, 36001)
    G = np.abs(gam(zin(Aof(f), ZL)))
    ok = f[G <= 10 ** (-rl_db / 20)]
    # contiguous band around f0
    return (ok.max() - ok.min()) / f0 if ok.size else 0.0


f0 = 915e6
Rs, RL = 50.0, 10.0
print("      50 -> 10 ohm at 915 MHz: fractional bandwidth for RL > 10 dB (VSWR < 1.92)")
Qn_L = np.sqrt(50 / 10 - 1)


def A_L(f):
    w = 2 * np.pi * f
    Q, Xs, Xp = lnet_real(Rs, RL)
    Lh = Xs / (2 * np.pi * f0); Cp = -1 / (2 * np.pi * f0 * Xp)
    return casc(shu(1j * w * Cp), ser(1j * w * Lh))


bwL = sweep_bw(A_L, RL, f0)
print(f"        L-network (Q = {Qn_L:.2f}): {bwL*100:.1f} %")
bws = []
for Qp in [3, 5, 8, 12]:
    Rv, Q1, Q2, Xp1, Xs, Xp2 = pi_net(Rs, RL, Qp)
    C1 = -1 / (2 * np.pi * f0 * Xp1); Ls = Xs / (2 * np.pi * f0); C2 = -1 / (2 * np.pi * f0 * Xp2)

    def A_pi(f, C1=C1, Ls=Ls, C2=C2):
        w = 2 * np.pi * f
        return casc(shu(1j * w * C1), ser(1j * w * Ls), shu(1j * w * C2))

    Zc = zin(A_pi(np.array([f0])), RL)[0]
    bw = sweep_bw(A_pi, RL, f0)
    bws.append(bw)
    print(f"        Pi (Q = {Qp:>2}, Rv = {Rv:.2f} ohm): C1 = {C1*1e12:.2f} pF, L = {Ls*1e9:.2f} nH, "
          f"C2 = {C2*1e12:.2f} pF -> {bw*100:.1f} %   (Zin at f0 = {Zc:.3f})")
check("Pi networks match exactly at f0 and bandwidth falls as Q rises", np.all(np.diff(bws) < 0) and bwL > bws[0])


# T network (series-shunt-series) with virtual R above both
def t_net(Rs, RL, Q):
    Rl_ = min(Rs, RL)
    Rv = Rl_ * (Q**2 + 1)
    Q1 = np.sqrt(Rv / Rs - 1); Q2 = np.sqrt(Rv / RL - 1)
    Xs1, Xp1 = Q1 * Rs, -Rv / Q1
    Xp2, Xs2 = -Rv / Q2, Q2 * RL
    Xp = 1 / (1 / Xp1 + 1 / Xp2)
    return Rv, Xs1, Xp, Xs2


Rv, Xs1, Xp, Xs2 = t_net(50, 10, 5)
A = casc(ser(np.array([1j * Xs1])), shu(np.array([1 / (1j * Xp)])), ser(np.array([1j * Xs2])))
check("T network (Q = 5 on low side, Rv = 260 ohm) matches 10 -> 50 ohm", abs(zin(A, 10.0)[0] - 50) < 1e-9)

# ---------------------------------------------------------------- 4. finite-Q loss
print("      L-network loss with finite inductor Q (capacitor Q = 300):")
for Rl_, Qu in [(12.5, 40), (5.0, 40), (5.0, 20), (2.0, 30), (25.0, 30)]:
    Q, Xs, Xp = lnet_real(50, Rl_)
    Rser = Xs / Qu                       # inductor ESR
    Gsh = 1 / (abs(Xp) * 300)            # capacitor ESR modelled as shunt conductance ~ 1/(Q |X|)
    A = casc(shu(np.array([1 / (1j * Xp) + Gsh])), ser(np.array([1j * Xs + Rser])))
    # power delivered to Rl from a 50 ohm 1 W-available source
    S = rf.a2s(A, z0=[50, Rl_]) if hasattr(rf, "a2s") else None
    # direct calc: V at load
    Vs = 2 * np.sqrt(2 * 50)            # EMF for 1 W available
    ZinA = zin(A, Rl_)[0]
    Iin = Vs / (50 + ZinA)
    Vin = Iin * ZinA
    # propagate: [Vin, Iin] = A [VL, IL]
    VL, IL = np.linalg.solve(A[0], np.array([Vin, Iin]))
    PL = 0.5 * abs(VL) ** 2 / Rl_
    IL_db = -10 * np.log10(PL)
    est = 10 * np.log10(1 + Q / Qu + Q / 300)
    print(f"        {Rl_:>5} -> 50 ohm, Qn = {Q:.2f}, QL = {Qu}: IL = {IL_db:.3f} dB (estimate 10log(1+Qn/QL+Qn/QC) = {est:.3f} dB)")
    check(f"  finite-Q loss estimate within 15% ({Rl_} ohm, QL {Qu})", abs(IL_db - est) / IL_db < 0.15)


# ---------------------------------------------------------------- 5. single shunt stub
def shunt_stub(ZL, Z0=50.0):
    """Pozar 5.2: distance d (as t = tan(beta d)) and stub lengths. Returns list of (d/lambda, lo/lambda, ls/lambda)."""
    RL, XL = ZL.real, ZL.imag
    out = []
    if abs(RL - Z0) < 1e-12:
        ts = [-XL / (2 * Z0)]
    else:
        root = np.sqrt(RL * ((Z0 - RL) ** 2 + XL**2) / Z0)
        ts = [(XL + root) / (RL - Z0), (XL - root) / (RL - Z0)]
    for t in ts:
        d = (np.arctan(t) / (2 * np.pi)) % 0.5
        G = RL * (1 + t**2) / (RL**2 + (XL + Z0 * t) ** 2)
        B = (RL**2 * t - (Z0 - XL * t) * (XL + Z0 * t)) / (Z0 * (RL**2 + (XL + Z0 * t) ** 2))
        lo = (np.arctan(-B * Z0) / (2 * np.pi)) % 0.5        # open stub: Y = j tan(bl)/Z0 = -jB
        ls = (np.arctan(1 / (B * Z0)) / (2 * np.pi)) % 0.5    # short stub: Y = -j cot(bl)/Z0 = -jB
        out.append((d, lo, ls, G * Z0))
    return out


ZL = 60 - 80j
f2 = rf.Frequency(2450, 2450, 1, unit="MHz")
air = rf.media.DefinedGammaZ0(frequency=f2, z0=50, gamma=1j * 2 * np.pi * f2.f / c0)  # NB default gamma is 1j rad/m!
lam = c0 / 2.45e9
for d, lo, ls, gn in shunt_stub(ZL):
    load = rf.Network(frequency=f2, s=np.array([gam(ZL)]), z0=50)
    line = air.line(d * lam, unit="m")
    stub_o = air.line(lo * lam, unit="m") ** air.open()
    stub_s = air.line(ls * lam, unit="m") ** air.short()
    m_o = air.shunt(stub_o) ** line ** load
    m_s = air.shunt(stub_s) ** line ** load
    check(f"shunt stub for {ZL}: d = {d:.4f} lam, open {lo:.4f} lam / short {ls:.4f} lam -> matched (skrf)",
          abs(m_o.s[0, 0, 0]) < 1e-9 and abs(m_s.s[0, 0, 0]) < 1e-9 and abs(gn - 1) < 1e-9)


# ---------------------------------------------------------------- 6. binomial transformer
def binomial(Z0, ZL, N):
    Zs = [Z0]
    for n in range(N):
        Zs.append(Zs[-1] * np.exp(2.0**-N * comb(N, n) * np.log(ZL / Z0)))
    return np.array(Zs[1:])  # section impedances (the recurrence ends at ZL)


def multisection_A(Zsecs, fnorm):
    th = np.pi / 2 * fnorm
    mats = [tl(Z, th) for Z in Zsecs]
    return casc(*mats)


Gm = 0.05
fn = np.linspace(0.01, 1.99, 19801)


def binomial_sections(Z0, ZL, N):
    """Pozar eq. (5.63): ln(Z_{n+1}/Z_n) = 2^-N C(N,n) ln(ZL/Z0), n = 0..N; sections are Z_1..Z_N."""
    Z = [Z0]
    for n in range(N + 1):
        Z.append(Z[-1] * np.exp(2.0**-N * comb(N, n) * np.log(ZL / Z0)))
    return np.array(Z[1:N + 1]), Z[-1]


def bw_of(secs, Z0, ZL, Gm):
    G = np.abs(gam(zin(multisection_A(secs, fn), ZL), Z0))
    band = fn[G <= Gm]
    return band.max() - band.min(), G


binom_err = {}
for ZL_ in [25.0, 10.0]:
    for N in [2, 3, 4]:
        secs, Zend = binomial_sections(50.0, ZL_, N)
        bw_sweep, _ = bw_of(secs, 50.0, ZL_, Gm)
        Aconst = 2.0**-N * abs((ZL_ - 50.0) / (ZL_ + 50.0))
        bw_formula = 2 - 4 / np.pi * np.arccos(0.5 * (Gm / Aconst) ** (1 / N))
        binom_err[(ZL_, N)] = bw_formula - bw_sweep
        print(f"      binomial 50->{ZL_:.0f} N={N}: sections {np.round(secs,2)}; BW(|G|<0.05) formula "
              f"{bw_formula*100:.1f} %, exact cascade {bw_sweep*100:.1f} %")
        check(f"binomial 50->{ZL_:.0f} N={N}: recursion ends at ZL", abs(Zend - ZL_) < 1e-9)
check("binomial BW formula accurate (<2 points, slightly optimistic) for 2:1 ratio",
      all(0 < binom_err[(25.0, N)] < 0.02 for N in [2, 3, 4]))
check("binomial BW formula OVERestimates by 4-7 points for 5:1 ratio (small-reflection theory limit)",
      all(0.03 < binom_err[(10.0, N)] < 0.08 for N in [2, 3, 4]))


# ---------------------------------------------------------------- 7. Chebyshev transformer
def cheb_T(n, x):
    x = np.asarray(x, dtype=float)
    out = np.where(np.abs(x) <= 1, np.cos(n * np.arccos(np.clip(x, -1, 1))),
                   np.cosh(n * np.arccosh(np.maximum(np.abs(x), 1))) * np.where(x < 0, (-1) ** n, 1))
    return out


def chebyshev(Z0, ZL, N, Gm):
    """Synthesis via small-reflection theory with the log (Collin) form:
       Gamma(theta) = sum_n Gamma_n e^{-2jn theta}, Gamma_n symmetric, = A e^{-jN theta} T_N(sec(theta_m) cos theta)
       with A = Gm and A*T_N(sec theta_m) = 0.5 ln(ZL/Z0) (theta = 0)."""
    L = 0.5 * np.log(ZL / Z0)
    sec_m = np.cosh(np.arccosh(abs(L) / Gm) / N)
    # expand A T_N(sec_m cos th) e^{-jN th} into a cosine series: sample and fit coefficients
    th = np.linspace(0, np.pi, 4 * N + 7)
    target = Gm * np.sign(L) * cheb_T(N, sec_m * np.cos(th))
    # Gamma(th) e^{jN th} = sum_{n=0}^{N} Gamma_n e^{j(N-2n) th} -> symmetric => sum 2 Gamma_n cos((N-2n) th) (+ middle)
    M = np.zeros((len(th), N + 1))
    for n in range(N + 1):
        M[:, n] = np.cos((N - 2 * n) * th)
    Gn = np.linalg.lstsq(M, target, rcond=None)[0]
    # ln(Z_{n+1}/Z_n) = 2 Gamma_n (log form)
    Z = [Z0]
    for n in range(N + 1):
        Z.append(Z[-1] * np.exp(2 * Gn[n]))
    return np.array(Z[1:N + 1]), Z[-1], np.arccos(1 / sec_m)


from scipy.optimize import minimize

for ZL_ in [25.0, 10.0]:
    for N in [2, 3, 4]:
        secs, Zend, thm = chebyshev(50.0, ZL_, N, Gm)
        f_lo = thm / (np.pi / 2)
        inb = (fn >= f_lo) & (fn <= 2 - f_lo)
        G = np.abs(gam(zin(multisection_A(secs, fn), ZL_), 50.0))
        ripple = G[inb].max()
        bw_cheb = 2 - 4 * thm / np.pi
        # minimax refinement of the exact response over the same band
        fb = fn[inb][::10]

        def cost(lz):
            return np.max(np.abs(gam(zin(multisection_A(np.exp(lz), fb), ZL_), 50.0)))

        r = minimize(cost, np.log(secs), method="Nelder-Mead", options=dict(xatol=1e-7, fatol=1e-9, maxiter=20000))
        secs_r = np.exp(r.x)
        print(f"      Chebyshev 50->{ZL_:.0f} N={N}: small-reflection design {np.round(secs,2)} gives in-band max |G| "
              f"{ripple:.4f} over design BW {bw_cheb*100:.1f} %; minimax-refined {np.round(secs_r,2)} -> {r.fun:.4f}")
        if ZL_ == 25.0:
            check(f"Chebyshev 50->25 N={N}: small-reflection synthesis meets ripple within 10%", ripple < 1.10 * Gm)
        else:
            check(f"Chebyshev 50->10 N={N}: synthesis overshoots ripple (20-40%); exact minimax over the same band "
                  f"is ~11% above Gm (small-reflection BW is optimistic)",
                  1.1 * Gm < ripple < 1.45 * Gm and Gm < r.fun < 1.15 * Gm)
        # binomial comparison
        sb, _ = binomial_sections(50.0, ZL_, N)
        bwb, _ = bw_of(sb, 50.0, ZL_, Gm)
        if ZL_ == 10.0:
            print(f"        N={N}: binomial BW {100*bwb:.1f} %  vs  Chebyshev design BW {100*bw_cheb:.1f} %")


# ---------------------------------------------------------------- 8. Klopfenstein
def phi_k(x, A):
    if abs(x) < 1e-15:
        return 0.0
    f = lambda y: i1(A * np.sqrt(1 - y * y)) / (A * np.sqrt(1 - y * y)) if A * np.sqrt(1 - y * y) > 1e-12 else 0.5
    return quad(f, 0, x, limit=200)[0]


def klopf_profile(Z1, Z2, Gm, npts):
    G0 = 0.5 * np.log(Z2 / Z1)
    A = np.arccosh(abs(G0) / Gm)
    x = np.linspace(-1, 1, npts)
    lnZ = 0.5 * np.log(Z1 * Z2) + G0 / np.cosh(A) * A**2 * np.array([phi_k(xi, A) for xi in x])
    return np.exp(lnZ), A, G0


Z1, Z2, Gmk = 50.0, 10.0, 0.02
Zk, Ak, G0k = klopf_profile(Z1, Z2, Gmk, 401)
check("Klopfenstein identity A^2 phi(1,A) = cosh(A) - 1", abs(Ak**2 * phi_k(1, Ak) - (np.cosh(Ak) - 1)) < 1e-9)
print(f"      Klopfenstein 50->10 ohm, Gm = {Gmk}: A = {Ak:.4f}; end impedances {Zk[0]:.3f} / {Zk[-1]:.3f} ohm "
      f"(steps to {Z1}/{Z2} at the ends: |G| = {abs(gam(Zk[0], Z1)):.4f}, {abs(gam(Z2, Zk[-1])):.4f})")
# exact cascade of many short sections, TEM, lengths normalised: beta*L
nseg = 400
Zmid = np.sqrt(Zk[:-1] * Zk[1:])
bl = np.linspace(0.2, 12, 1200)            # beta*L
Gk = []
for b in bl:
    th = b / nseg
    A = np.eye(2, dtype=complex)[None]
    for Zc in Zmid:
        A = np.einsum("fij,fjk->fik", A, tl(Zc, np.array([th])))
    Gk.append(abs(gam(zin(A, Z2)[0], Z1)))
Gk = np.array(Gk)
pb = bl >= Ak * 1.02
check("Klopfenstein 50->10: exact passband |Gamma| overshoots Gm by ~30% (5:1 ratio, small-refl. theory)", Gk[pb].max() < 1.35 * Gmk,
      f"(max passband |G| = {Gk[pb].max():.4f}, passband starts at beta*L = A = {Ak:.3f}, "
      f"i.e. L = {Ak/(2*np.pi):.3f} lambda)")
# versus scikit-rf's Klopfenstein taper
fk = rf.Frequency(0.1, 12, 600, unit="GHz")
L_len = 0.1  # m, air
tap = rf.taper.Klopfenstein(med=rf.media.DefinedGammaZ0, param="z0", start=Z1, stop=Z2, n_sections=nseg,
                            length=L_len, f_kw={"rmax": Gmk / abs(G0k)},
                            med_kw={"frequency": fk, "gamma": 1j * 2 * np.pi * fk.f / c0, "z0_port": 50})
nt = tap.network
nt_load = nt ** rf.Network(frequency=fk, s=gam(Z2) * np.ones(fk.npoints), z0=50)
blk = 2 * np.pi * fk.f / c0 * L_len
ours = np.interp(blk, bl, Gk)
sel = (blk > 0.5) & (blk < 11.5)
diff = np.max(np.abs(np.abs(nt_load.s[sel, 0, 0]) - ours[sel]))
check("own Klopfenstein cascade ~ scikit-rf taper.Klopfenstein (differs only by end-step handling)", diff < 0.012,
      f"(max |d|G|| = {diff:.4f}; skrf passband max {np.abs(nt_load.s[sel & (blk > Ak*1.02), 0, 0]).max():.4f})")
# smaller ratio: 50 -> 25 ohm
Zk2, Ak2, _ = klopf_profile(50.0, 25.0, Gmk, 401)
Zmid2 = np.sqrt(Zk2[:-1] * Zk2[1:])
Gk2 = []
for b in bl:
    A = np.eye(2, dtype=complex)[None]
    for Zc in Zmid2:
        A = np.einsum("fij,fjk->fik", A, tl(Zc, np.array([b / nseg])))
    Gk2.append(abs(gam(zin(A, 25.0)[0], 50.0)))
Gk2 = np.array(Gk2)
check("Klopfenstein 50->25: passband |Gamma| within 10% of Gm (small-reflection theory good at 2:1)",
      Gk2[bl >= Ak2 * 1.02].max() < 1.10 * Gmk, f"(max {Gk2[bl >= Ak2*1.02].max():.4f}, A = {Ak2:.3f})")

# ---------------------------------------------------------------- 9. worked examples
print("\n      --- worked examples ---")
# (a) 433 MHz: 12.5 ohm PA output -> 50 ohm, L-net low-pass
Q, Xs, Xp = lnet_real(50, 12.5)
print(f"      433 MHz 12.5->50: series L {Lval(Xs,433e6)*1e9:.2f} nH, shunt C {Cval(Xp,433e6)*1e12:.2f} pF, Q {Q:.3f}")
# (b) 915 MHz chip antenna 18 - j35 ohm -> 50 ohm (series-at-load, R < 50)
for topo, X, B in lnet_complex(18 - 35j):
    comp_s = f"series L {Lval(X,915e6)*1e9:.2f} nH" if X > 0 else f"series C {Cval(X,915e6)*1e12:.2f} pF"
    comp_p = f"shunt C {B/(2*np.pi*915e6)*1e12:.2f} pF" if B > 0 else f"shunt L {-1/(2*np.pi*915e6*B)*1e9:.2f} nH"
    # bandwidth 902-928 MHz check with ideal parts
    fb = np.linspace(902e6, 928e6, 27)
    w = 2 * np.pi * fb
    if X > 0:
        Zs_ = 1j * w * (X / (2 * np.pi * 915e6))
    else:
        Zs_ = 1 / (1j * w * (-1 / (2 * np.pi * 915e6 * X)))
    if B > 0:
        Yp = 1j * w * (B / (2 * np.pi * 915e6))
    else:
        Yp = 1 / (1j * w * (-1 / (2 * np.pi * 915e6 * B)))
    # antenna modelled as series R + C with the same Z at 915 MHz (crude)
    Cant = -1 / (2 * np.pi * 915e6 * (-35))
    Zant = 18 + 1 / (1j * w * Cant)
    Zin_b = 1 / (1 / (Zant + Zs_) + Yp)
    worst = np.max(np.abs(gam(Zin_b)))
    print(f"      915 MHz 18-j35: {comp_s} then {comp_p}; worst RL over 902-928 MHz = {-20*np.log10(worst):.1f} dB")
# (c) 2450 MHz: shunt open stub on microstrip (JLC04161H-7628, h = 0.2104 mm, er 4.4) for ZL = 60 - j80
f24 = rf.Frequency(2450, 2450, 1, unit="MHz")
ms = rf.media.MLine(frequency=f24, w=0.36e-3, h=0.2104e-3, t=35e-6, ep_r=4.4, tand=0.02, rough=0,
                    disp="kirschningjansen", model="hammerstadjensen", z0_port=50)
lam_g = 2 * np.pi / ms.gamma[0].imag
print(f"      2450 MHz microstrip w = 0.36 mm on 0.2104 mm (er 4.4): Z0 = {ms.z0[0].real:.2f} ohm, "
      f"eeff = {ms.ep_reff_f[0].real:.3f}, lambda_g = {lam_g*1e3:.2f} mm")
for d, lo, ls, gn in shunt_stub(60 - 80j):
    print(f"        stub solution: d = {d:.4f} lam_g = {d*lam_g*1e3:.2f} mm, open stub {lo:.4f} lam_g = {lo*lam_g*1e3:.2f} mm, "
          f"short stub {ls:.4f} lam_g = {ls*lam_g*1e3:.2f} mm")

# (d) 433 MHz chip antenna 32.1 - j18.5 ohm: ideal vs E-series values vs finite Q (pi-pad: series L, shunt C)
f0d = 433e6
w0d = 2 * np.pi * f0d
Za = 32.1 - 18.5j
fb = np.linspace(425e6, 441e6, 161)
wb = 2 * np.pi * fb
# crude antenna model: series R-L-C resonant somewhere above 433 MHz with the right Z at 433 (Q_ant ~ 10)
Qa = 10.0
Ra = Za.real
# choose La, Ca: X(w0) = w0 La - 1/(w0 Ca) = -18.5 and w0 La = Qa*Ra (antenna reactance slope)
La = Qa * Ra / w0d
Ca = 1 / (w0d * (w0d * La - Za.imag))
Zant = Ra + 1j * wb * La + 1 / (1j * wb * Ca)


def rl_series_shunt(Lh, Cp, QL=None, QC=None):
    Zs = 1j * wb * Lh + (wb * Lh / QL if QL else 0)
    Yp = 1j * wb * Cp + (wb * Cp / QC if QC else 0)
    Zin_ = 1 / (1 / (Zant + Zs) + Yp)
    return -20 * np.log10(np.abs(gam(Zin_))), Zin_


rl_i, _ = rl_series_shunt(15.61e-9, 5.49e-12)
rl_e, _ = rl_series_shunt(15e-9, 5.6e-12)
rl_q, Zq = rl_series_shunt(15e-9, 5.6e-12, QL=30, QC=200)
k = np.argmin(abs(fb - f0d))
# loss: power into antenna R vs available
Vs = 2 * np.sqrt(2 * 50)
Zs_q = 1j * wb * 15e-9 + wb * 15e-9 / 30
Yp_q = 1j * wb * 5.6e-12 + wb * 5.6e-12 / 200
Zin_q = 1 / (1 / (Zant + Zs_q) + Yp_q)
Iin = Vs / (50 + Zin_q)
Vin = Iin * Zin_q
Iant = Vin / (Zant + Zs_q)
P_ant = 0.5 * np.abs(Iant) ** 2 * Ra
print(f"      433 MHz chip-antenna example: RL at 433 MHz ideal (15.61 nH, 5.49 pF) {rl_i[k]:.1f} dB; "
      f"E-series (15 nH, 5.6 pF) {rl_e[k]:.1f} dB; with Q_L = 30, Q_C = 200: {rl_q[k]:.1f} dB, "
      f"power to antenna R = {P_ant[k]:.3f} W of 1 W avail ({10*np.log10(P_ant[k]):.2f} dB)")
bw_band = fb[rl_q >= 10]
print(f"        RL >= 10 dB band with real parts: {bw_band.min()/1e6:.1f}-{bw_band.max()/1e6:.1f} MHz "
      f"(ISM 433.05-434.79 MHz)")
check("433 MHz example: E-series + finite-Q match still better than 15 dB RL at 433 MHz", rl_q[k] > 15)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
