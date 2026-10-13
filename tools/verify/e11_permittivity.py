#!/usr/bin/env python3
"""e11_permittivity.py — checks for
kb/17-test-measurement/resonator-and-cavity-perturbation-permittivity-measurement.md (task W5-E11).

1. Cavity perturbation: thin dielectric rod along E at the centre of a rectangular TE101 cavity.
   Perturbation formulas  (f0 - fs)/f0 = 2 (er' - 1) Vs/V,   1/Qs - 1/Q0 = 4 er'' Vs/V
   versus an exact-enough 2-D finite-difference eigen-solution (the TE10p family of a cavity uniform
   in the E direction is a scalar Helmholtz problem in the x-z plane), for growing rod size and er.
2. Resonator coupling: series-capacitor-coupled parallel RLC between 50-ohm ports.
   Transmission method Q0 = QL/(1 - |S21(f0)|) (equal coupling), reflection method Q0 = QL (1 + beta),
   beta from |S11| at resonance with the under/over-coupling ambiguity resolved by the Smith-chart loop.
3. Microstrip ring resonator on 2-layer FR-4 with gap coupling (Kirschning gap model from
   e11_discontinuities.py; dispersive line from tline_microstrip.py): extract eeff_n from the resonance
   peaks f_n = n c/(L sqrt(eeff)), invert to er, and extract tan(delta) from Q0 after removing conductor Q.
   Shows the gap-loading bias and why weak coupling is used.
4. Two-line (differential-length) method with identical, unknown connectors: eigenvalues of
   A2 A1^-1 give exp(+-gamma dL) independent of the connectors.
5. Free-space transmission through a flat fibreglass panel (nose-cone witness coupon): full slab
   (Fabry-Perot) model fitted to noisy S21 2-6 GHz; sensitivity to thickness error.

Run: python3 tools/verify/e11_permittivity.py     (~1-2 min; the FD eigen-solves dominate)
"""
import os
import sys

import numpy as np
import scipy.sparse as sps
import scipy.sparse.linalg as spla
from scipy import optimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tline_microstrip import ms_kj, ms_hj, ms_loss, width_for   # noqa: E402
from e11_discontinuities import gap_kirschning                   # noqa: E402

C0 = 299792458.0
RES = []


def check(name, ok, detail=""):
    RES.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")


# ---------------------------------------------------------------- 1. cavity perturbation
def cavity_eig(a, d, N, rod_r=0.0, er=1.0 + 0j, sub=6):
    """Lowest eigenvalue of -lap E = k0^2 er(x,z) E, E = 0 on the walls of [0,a]x[0,d]; N x N interior nodes.
    Returns complex k0 (rad/m). er averaged over each node's control cell by sub x sub sampling."""
    hx, hz = a / (N + 1), d / (N + 1)
    x = hx * np.arange(1, N + 1)
    z = hz * np.arange(1, N + 1)
    X, Z = np.meshgrid(x, z, indexing="ij")
    eps = np.ones((N, N), complex)
    if rod_r > 0:
        s = (np.arange(sub) + 0.5) / sub - 0.5
        frac = np.zeros((N, N))
        for sx in s:
            for sz in s:
                frac += ((X + sx * hx - a / 2) ** 2 + (Z + sz * hz - d / 2) ** 2 < rod_r ** 2)
        frac /= sub * sub
        eps = 1 + (er - 1) * frac
    ex = np.ones(N)
    Dx = sps.diags([ex[:-1], -2 * ex, ex[:-1]], [-1, 0, 1]) / hx ** 2
    Dz = sps.diags([ex[:-1], -2 * ex, ex[:-1]], [-1, 0, 1]) / hz ** 2
    Lap = sps.kron(Dx, sps.eye(N)) + sps.kron(sps.eye(N), Dz)
    B = sps.diags(eps.ravel())
    k_guess = np.pi * np.sqrt(1 / a ** 2 + 1 / d ** 2)
    vals = spla.eigs((-Lap).tocsc().astype(complex), k=1, M=B.tocsc(), sigma=k_guess ** 2 * 0.98, which="LM")[0]
    return np.sqrt(vals[0])


def part1():
    print("1. Cavity perturbation vs 2-D FD eigen-solution (a = d = 100 mm, TE101)")
    a = d = 0.100
    N = 299                                    # h = 0.33 mm
    k_empty = cavity_eig(a, d, N)
    f_empty = k_empty.real * C0 / (2 * np.pi)
    f_exact = C0 / 2 * np.sqrt(1 / a ** 2 + 1 / d ** 2)
    print(f"   empty cavity: FD {f_empty/1e9:.5f} GHz vs analytic {f_exact/1e9:.5f} GHz")
    check("FD empty-cavity TE101 within 0.01 % of analytic", abs(f_empty / f_exact - 1) < 1e-4)
    rows = []
    for r, er in ((0.75e-3, 4.4 - 0.088j), (1.5e-3, 4.4 - 0.088j), (3e-3, 4.4 - 0.088j), (6e-3, 4.4 - 0.088j),
                  (1.5e-3, 10.0 - 0.2j)):
        k = cavity_eig(a, d, N, r, er)
        fs = k.real * C0 / (2 * np.pi)
        # Q from the complex eigenvalue: k0 complex -> omega complex; Q = Re/(2|Im|)
        Q = k.real / (2 * abs(k.imag))
        vr = np.pi * r ** 2 / (a * d)              # Vs/V for a full-height rod
        df_fd = (f_empty - fs) / f_empty
        df_pt = 2 * (er.real - 1) * vr
        dq_fd = 1 / Q
        dq_pt = 4 * (-er.imag) * vr
        # invert the perturbation formula on the 'measured' FD data (what a user would do)
        er_rec = 1 + df_fd / (2 * vr)
        tand_rec = dq_fd / (4 * vr) / er_rec
        rows.append((r, er, df_fd, df_pt, dq_fd, dq_pt, er_rec, tand_rec))
        print(f"   rod r = {r*1e3:.2f} mm, er = {er.real:.1f}-j{-er.imag:.3f}: Vs/V = {vr:.2e}; df/f FD {df_fd:.4e} vs "
              f"pert {df_pt:.4e} ({100*(df_pt/df_fd-1):+.1f} %); 1/Q FD {dq_fd:.3e} vs pert {dq_pt:.3e}; "
              f"recovered er' = {er_rec:.3f}, tan d = {tand_rec:.4f}")
    check("perturbation er' error < 2 % for a 1.5 mm-radius FR-4 rod (df/f < 1 %)", abs(rows[1][6] / 4.4 - 1) < 0.02,
          f"{rows[1][6]:.3f}")
    check("perturbation tan d error < 5 % for the same rod", abs(rows[1][7] / 0.02 - 1) < 0.05, f"{rows[1][7]:.4f}")
    check("rod-parallel-to-E perturbation stays within 3 % in er' for every resolved rod (r >= 1.5 mm) with df/f < 2 %",
          all(abs(r[6] / r[1].real - 1) < 0.03 for r in rows if r[2] < 0.02 and r[0] >= 1.5e-3))
    print("   (the r = 0.75 mm rod is only ~4.5 cells across at h = 0.33 mm: its +1.8 % is FD discretisation, not theory)")
    check("loss-tangent recovery degrades as the rod grows (r = 6 mm worse than 1.5 mm)",
          abs(rows[3][7] / 0.02 - 1) > abs(rows[1][7] / 0.02 - 1), f"{rows[3][7]:.4f} vs {rows[1][7]:.4f}")


# ---------------------------------------------------------------- 2. coupling and Q0
def coupled_rlc(f, f0=1e9, Q0=500, R=5e3, Cc=0.25e-12, two_port=True, Z0=50.0):
    w = 2 * np.pi * f
    L = R / (2 * np.pi * f0 * Q0)
    C = 1 / ((2 * np.pi * f0) ** 2 * L)
    Yr = 1 / R + 1j * w * C + 1 / (1j * w * L)
    Zc = 1 / (1j * w * Cc)
    if two_port:
        # port1 - Cc - shunt resonator - Cc - port2 (ABCD)
        def ser(Z):
            return np.array([[np.ones_like(Z), Z], [np.zeros_like(Z), np.ones_like(Z)]])
        def sh(Y):
            return np.array([[np.ones_like(Y), np.zeros_like(Y)], [Y, np.ones_like(Y)]])
        M = np.einsum("ij...,jk...->ik...", np.einsum("ij...,jk...->ik...", ser(Zc), sh(Yr)), ser(Zc))
        A, B, Cm, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
        den = A + B / Z0 + Cm * Z0 + D
        return 2 / den, (A + B / Z0 - Cm * Z0 - D) / den
    Zin = Zc + 1 / Yr
    return None, (Zin - Z0) / (Zin + Z0)


def lorentz_q(f, p):
    """f0 and QL from the half-power width of a power-like Lorentzian p(f) (peak)."""
    i = int(np.argmax(p))
    half = p[i] / 2
    lo = np.interp(half, p[:i + 1], f[:i + 1])
    hi = np.interp(-half, -p[i:], f[i:])
    return f[i], f[i] / (hi - lo)


def part2():
    print("2. Resonator coupling: extracting Q0 from QL")
    f = np.linspace(0.80e9, 1.02e9, 600001)
    # "true" unloaded Q at the coupling-shifted resonance: the coupling capacitors add stored energy but no
    # loss, so Q0' = omega0' C_tot R = R/(omega0' L) = 500 f0/f0'.
    for Cc in (0.15e-12, 0.4e-12, 1.0e-12):
        s21, s11 = coupled_rlc(f, Cc=Cc)
        f0, QL = lorentz_q(f, np.abs(s21) ** 2)
        s21m = np.max(np.abs(s21))
        Q0 = QL / (1 - s21m)
        qt = 500 * 1e9 / f0
        print(f"   two-port, Cc = {Cc*1e12:.2f} pF: f0 = {f0/1e9:.5f} GHz, QL = {QL:.1f}, |S21|max = {s21m:.3f} "
              f"({20*np.log10(s21m):.1f} dB) -> Q0 = {Q0:.1f} (true {qt:.1f})")
        check(f"transmission method recovers Q0 within 1 % (Cc {Cc*1e12:.2f} pF)", abs(Q0 / qt - 1) < 0.01)
    for Cc in (0.3e-12, 0.6e-12, 1.2e-12):
        _, s11 = coupled_rlc(f, Cc=Cc, two_port=False)
        p = 1 - np.abs(s11) ** 2
        f0, QL = lorentz_q(f, p)
        i = int(np.argmax(p))
        g = abs(s11[i])
        # ambiguity: over-coupled if the S11 circle encloses the origin of the (de-embedded) Smith chart:
        # test with the phase swing of S11 across resonance (~360 deg if over-coupled, < 180 if under)
        sw = np.ptp(np.unwrap(np.angle(s11 * np.exp(-1j * np.angle(s11[0])))))
        over = sw > np.pi
        beta = (1 + g) / (1 - g) if over else (1 - g) / (1 + g)
        Q0 = QL * (1 + beta)
        qt = 500 * 1e9 / f0
        print(f"   one-port, Cc = {Cc*1e12:.2f} pF: f0 = {f0/1e9:.5f} GHz, QL = {QL:.1f}, |S11|min = {g:.3f}, phase swing "
              f"{np.degrees(sw):.0f} deg -> {'over' if over else 'under'}-coupled, beta = {beta:.3f}, Q0 = {Q0:.1f} (true {qt:.1f})")
        check(f"reflection method recovers Q0 within 1 % (Cc {Cc*1e12:.2f} pF)", abs(Q0 / qt - 1) < 0.01)


# ---------------------------------------------------------------- 3. ring resonator
def line_abcd(f, l, W, h, er, tand, t=35e-6):
    z, ee = ms_kj(W, h, er, f, 0.0)
    a_db = ms_loss(W, h, er, tand, f, t=t)            # dB/m: (conductor, dielectric) or total
    a_np = np.sum(np.atleast_1d(a_db)) / 8.686
    beta = 2 * np.pi * f * np.sqrt(ee) / C0
    g = a_np + 1j * beta
    return np.array([[np.cosh(g * l), z * np.sinh(g * l)], [np.sinh(g * l) / z, np.cosh(g * l)]]), z, ee


def ring_s21(f, Lmean, W, h, er, tand, s_gap):
    """Port - gap - node A; ring = two parallel paths of Lmean/2 between A and B; node B - gap - port."""
    out = np.zeros(len(f), complex)
    for i, fi in enumerate(f):
        M, z, ee = line_abcd(fi, Lmean / 2, W, h, er, tand)
        A, B, C, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
        Yl = np.array([[D / B, -1 / B], [-1 / B, A / B]])      # Y of one half-ring (reciprocal)
        Yring = 2 * Yl                                          # two halves in parallel
        cs, cp1, cp2 = gap_kirschning(W, W, s_gap, h, er, fi)
        w = 2 * np.pi * fi
        # 4 nodes: P1, A, B, P2. Gap pi-network between P1-A and B-P2.
        Y = np.zeros((4, 4), complex)
        def add_pi(n1, n2):
            Y[n1, n1] += 1j * w * (cp1 + cs); Y[n2, n2] += 1j * w * (cp2 + cs)
            Y[n1, n2] -= 1j * w * cs; Y[n2, n1] -= 1j * w * cs
        add_pi(0, 1); add_pi(3, 2)
        Y[1:3, 1:3] += Yring
        # reduce to ports 0, 3 (Kron)
        p, q = [0, 3], [1, 2]
        Yp = Y[np.ix_(p, p)] - Y[np.ix_(p, q)] @ np.linalg.solve(Y[np.ix_(q, q)], Y[np.ix_(q, p)])
        Yn = Yp * 50.0
        S = (np.eye(2) - Yn) @ np.linalg.inv(np.eye(2) + Yn)
        out[i] = S[1, 0]
    return out


def part3():
    print("3. Ring resonator on 2-layer FR-4 (h 1.51 mm, true er 4.35, tan d 0.018)")
    h, er, tand = 1.51e-3, 4.35, 0.018
    W = width_for(50.0, lambda w: ms_hj(w, h, er, 0.0)[0])
    f1 = 1.0e9
    ee1 = ms_kj(W, h, er, f1, 0.0)[1]
    Lmean = C0 / (f1 * np.sqrt(ee1))
    print(f"   W = {W*1e3:.2f} mm, mean circumference {Lmean*1e3:.1f} mm (mean radius {Lmean/(2*np.pi)*1e3:.1f} mm), n = 1 at ~1 GHz")
    err_tight = 1.0
    for s_gap in (0.25e-3, 1.0e-3):
        recs = []
        for n in (1, 2, 3, 4):
            fn0 = n * f1
            fz = np.linspace(fn0 * 0.93, fn0 * 1.04, 2201)
            s = ring_s21(fz, Lmean, W, h, er, tand, s_gap)
            fn, QL = lorentz_q(fz, np.abs(s) ** 2)
            s21m = np.max(np.abs(s))
            Q0 = QL / (1 - s21m)
            eef = (n * C0 / (Lmean * fn)) ** 2
            er_x = optimize.brentq(lambda e: ms_kj(W, h, e, fn, 0.0)[1] - eef, 2.0, 8.0)
            # loss tangent: remove conductor Q, then undo the filling factor
            z, ee = ms_kj(W, h, er_x, fn, 0.0)
            ac, ad = ms_loss(W, h, er_x, tand, fn)
            beta = 2 * np.pi * fn * np.sqrt(ee) / C0
            Qc = beta / (2 * ac / 8.686)
            Qd = 1 / (1 / Q0 - 1 / Qc)
            q = (ee - 1) * er_x / ((er_x - 1) * ee)
            tand_x = 1 / (Qd * q)
            recs.append((n, fn, eef, er_x, QL, Q0, tand_x, 20 * np.log10(s21m)))
            print(f"   gap {s_gap*1e3:.2f} mm, n = {n}: f_n = {fn/1e9:.4f} GHz, |S21| = {20*np.log10(s21m):6.1f} dB, QL = {QL:6.1f}, "
                  f"Q0 = {Q0:6.1f}; eeff = {eef:.4f} -> er = {er_x:.3f}, tan d = {tand_x:.4f}")
        err = max(abs(r[3] / er - 1) for r in recs)
        print(f"   gap {s_gap*1e3:.2f} mm: worst uncorrected er error {100*err:+.2f} % (gap shunt/series C load the ring)")
        if s_gap == 1.0e-3:
            check("ring, 1 mm gaps: uncorrected er bias < 2.5 % and smaller than with 0.25 mm gaps", err < 0.025 and err < err_tight,
                  f"{100*err:.2f} % vs {100*err_tight:.2f} %")
            check("ring recovers tan d within 15 % (after conductor-Q removal)",
                  max(abs(r[6] / tand - 1) for r in recs) < 0.15,
                  f"worst {100*max(abs(r[6]/tand-1) for r in recs):.1f} %")
            # model-based correction: fit er so that the *full* ring model (with gap model) reproduces f_1
            fmeas = recs[0][1]
            def f1_model(e):
                fz = np.linspace(fmeas * 0.97, fmeas * 1.03, 1201)
                return fz[int(np.argmax(abs(ring_s21(fz, Lmean, W, h, e, tand, s_gap))))]
            e_fit = optimize.brentq(lambda e: f1_model(e) - fmeas, 4.0, 4.7, xtol=1e-4)
            check("model-based extraction (gap model included) removes the bias (< 0.2 %)", abs(e_fit / er - 1) < 2e-3,
                  f"er = {e_fit:.4f}")
        else:
            err_tight = err


# ---------------------------------------------------------------- 4. two-line method
def part4():
    print("4. Two-line method with unknown identical connectors (2-layer FR-4, true er 4.35)")
    h, er, tand = 1.51e-3, 4.35, 0.018
    W = width_for(50.0, lambda w: ms_hj(w, h, er, 0.0)[0])
    L1, L2 = 0.030, 0.130
    rng = np.random.default_rng(3)
    ok = []
    for f in (0.5e9, 1.0e9, 2.45e9, 4.0e9):
        w = 2 * np.pi * f
        # connector/launch error box: series 0.6 nH, shunt 0.35 pF, a 2 mm 60-ohm neck
        def box():
            Ls = np.array([[1, 1j * w * 0.6e-9], [0, 1]])
            Cp = np.array([[1, 0], [1j * w * 0.35e-12, 1]])
            bn = w * np.sqrt(3.0) / C0 * 2e-3
            Nk = np.array([[np.cos(bn), 1j * 60 * np.sin(bn)], [1j * np.sin(bn) / 60, np.cos(bn)]])
            return Ls @ Cp @ Nk
        X = box()
        Y = np.linalg.inv(box())[::-1, ::-1].T   # some different right box (any invertible 2x2 works)
        A1 = X @ line_abcd(f, L1, W, h, er, tand)[0] @ Y
        A2 = X @ line_abcd(f, L2, W, h, er, tand)[0] @ Y
        ev = np.linalg.eigvals(A2 @ np.linalg.inv(A1))
        lam = ev[np.argmax(abs(ev))]                       # e^{+gamma dL}
        g = np.log(lam) / (L2 - L1)
        beta = g.imag
        # phase ambiguity: choose branch with eeff in a sensible range
        dl = L2 - L1
        cands = [(g.imag + 2 * np.pi * m / dl) for m in range(-3, 4)]
        beta = min(cands, key=lambda b: abs((b * C0 / w) ** 2 - 3.3))
        eef = (beta * C0 / w) ** 2
        er_x = optimize.brentq(lambda e: ms_kj(W, h, e, f, 0.0)[1] - eef, 2.0, 8.0)
        alpha = g.real
        ac, ad = ms_loss(W, h, er_x, tand, f)
        ad_x = alpha * 8.686 - ac
        # dielectric loss formula inversion: ad = (pi/lam0) er (ee-1)/(sqrt(ee)(er-1)) tan d   [Np/m] *8.686
        k = ms_loss(W, h, er_x, 1.0, f)[1]          # dB/m per unit tan d (same filling-factor formula)
        tand_x = ad_x / k
        ok.append(abs(er_x / er - 1) < 2e-3 and abs(tand_x / tand - 1) < 0.02)
        print(f"   f = {f/1e9:4.2f} GHz: eeff = {eef:.4f} -> er = {er_x:.4f}, tan d = {tand_x:.4f}")
    check("two-line eigenvalue method recovers er (0.2 %) and tan d (2 %) despite the connector boxes", all(ok))


# ---------------------------------------------------------------- 5. free-space slab
def slab_s21(f, er, t):
    k0 = 2 * np.pi * f / C0
    n = np.sqrt(er + 0j)
    G = (1 - n) / (1 + n)
    P = np.exp(-1j * k0 * n * t)
    T = (1 - G ** 2) * P / (1 - G ** 2 * P ** 2)
    return T * np.exp(1j * k0 * t)          # normalised to the empty (air) path of the same thickness


def part5():
    print("5. Free-space transmission through a flat fibreglass coupon (nose-cone witness panel)")
    t, er_true = 2.0e-3, 4.4 - 0.07j
    f = np.linspace(2e9, 6e9, 81)
    rng = np.random.default_rng(1)
    meas = slab_s21(f, er_true, t) * (1 + 0.003 * rng.standard_normal(len(f))) * np.exp(1j * np.radians(0.5) * rng.standard_normal(len(f)))
    print(f"   2 mm panel, er 4.4 - j0.07 (tan d 0.016): insertion phase at 2.45 / 5.8 GHz = "
          f"{np.degrees(np.angle(slab_s21(np.array([2.45e9]), er_true, t))[0]):.1f} / "
          f"{np.degrees(np.angle(slab_s21(np.array([5.8e9]), er_true, t))[0]):.1f} deg; |S21| = "
          f"{20*np.log10(abs(slab_s21(np.array([5.8e9]), er_true, t))[0]):.2f} dB at 5.8 GHz")
    def fit(tt):
        def res(p):
            d = slab_s21(f, p[0] - 1j * p[1], tt) - meas
            return np.concatenate([d.real, d.imag])
        return optimize.least_squares(res, [4.0, 0.05]).x
    p = fit(t)
    print(f"   fitted er' = {p[0]:.3f}, er'' = {p[1]:.4f} (tan d {p[1]/p[0]:.4f}) with the correct thickness")
    check("free-space slab fit recovers er' within 1 % (0.5 deg / 0.3 % noise)", abs(p[0] / 4.4 - 1) < 0.01, f"{p[0]:.3f}")
    for dt in (0.05e-3, 0.1e-3):
        pt = fit(t + dt)
        print(f"   thickness error +{dt*1e3:.2f} mm -> er' = {pt[0]:.3f} ({100*(pt[0]/4.4-1):+.1f} %)")
    pt = fit(t + 0.1e-3)
    check("a +0.1 mm (5 %) thickness error biases er' by more than 3 % (thickness dominates)", abs(pt[0] / 4.4 - 1) > 0.03,
          f"{100*(pt[0]/4.4-1):+.1f} %")
    # mixing-rule estimate for hand-laid glass/epoxy (Lichtenecker logarithmic)
    for vg in (0.30, 0.40, 0.50):
        for vv in (0.0, 0.03):
            ve = 1 - vg - vv
            e = np.exp(vg * np.log(6.3) + ve * np.log(3.4) + vv * np.log(1.0))
            print(f"   Lichtenecker estimate: glass {vg:.2f}, voids {vv:.2f} -> er ~ {e:.2f}")


if __name__ == "__main__":
    part2()
    part4()
    part5()
    part3()
    part1()
    print(f"\nSummary: {sum(RES)}/{len(RES)} checks passed")
