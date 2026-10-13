#!/usr/bin/env python3
"""
s5_aperture_equivalence.py — equivalence principle, duality, reciprocity and aperture radiation.

Used by: kb/02-electromagnetics/greens-functions-and-integral-equations.md, sections
"Level 3b — magnetic currents, equivalence, reciprocity and aperture radiation" and the worked examples
that follow it (task W5-S5, gap G-02-01).

Sections
  §1  Duality: a magnetic current element K*l = j*w*mu0*I*A radiates exactly the field of a small
      electric loop of area A (all near- and far-field terms, numerically at several points).
  §2  Love's equivalence principle, numerically: put J_s = n x H and M_s = -n x E (fields of a
      Hertzian dipole) on a sphere around the dipole and integrate their radiation. Outside the
      sphere the surface currents reproduce the dipole field; inside they give ZERO (extinction).
  §3  Aperture in a PEC ground plane (Schelkunoff form, M_s = -2 n x E_a by image theory): TE10
      open-ended WR-90 flange at 10 GHz. Closed-form E- and H-plane patterns vs a direct numerical
      radiation integral; directivity by hemisphere integration vs the large-aperture formula
      D = (32/pi) a b / lambda^2; half-power beamwidths.
  §4  Lorentz reciprocity: reaction <1,2> = <2,1> for random electric dipoles with the free-space
      dyadic Green's function and with the PEC half-space (image) Green's function; a mixed
      electric/magnetic pair (<E1,J2> - <H1,M2> form); S-matrix symmetry of a reciprocal 2-port and
      its failure for a gyrator.
  §5  Bethe small-hole transmission: cross-section 64 k^4 r^6 / (27 pi) re-derived from the
      polarisabilities (alpha_m = 4 r^3/3) and image doubling; numbers for vent holes.
  §6  If tools/verify/s5_aperture_openems_results.txt exists (written by s5_aperture_openems.py,
      openEMS FDTD of the same flanged guide), compare its patterns with §3.

Run:  python3 tools/verify/s5_aperture_equivalence.py      (about 10 s)
"""
import json
import os

import numpy as np
from scipy import integrate
from scipy.special import roots_legendre

C0 = 299_792_458.0
MU0 = 1.25663706127e-6
EPS0 = 8.8541878188e-12
ETA0 = np.sqrt(MU0 / EPS0)            # 376.730 ohm (canonical)
HERE = os.path.dirname(os.path.abspath(__file__))
checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}  {detail}")


# ---------------------------------------------------------------- field kernels
def g_and_grad(r, rp, k):
    """g = exp(-jkR)/(4 pi R) and grad_r g (observation gradient). r: (3,), rp: (N,3)."""
    d = r[None, :] - rp
    R = np.linalg.norm(d, axis=1)
    g = np.exp(-1j * k * R) / (4 * np.pi * R)
    grad = (-(1j * k + 1 / R) * g / R)[:, None] * d
    return g, grad, R, d


def dyadic_dot(r, rp, k, J):
    """sum over sources of G(r,r') . J(r') with G = [I + grad grad / k^2] g (explicit form)."""
    g, _, R, d = g_and_grad(r, rp, k)
    Rh = d / R[:, None]
    kR = k * R
    a = 1 - 1j / kR - 1 / kR ** 2
    b = -1 + 3j / kR + 3 / kR ** 2
    RdotJ = np.sum(Rh * J, axis=1)
    return np.sum(g[:, None] * (a[:, None] * J + b[:, None] * RdotJ[:, None] * Rh), axis=0)


def fields_from_currents(r, rp, k, w, J=None, M=None, dS=None):
    """E and H at r radiated by electric (J) and magnetic (M) currents at points rp with weights dS.
    E = -j w mu G.J - grad g x M ;  H = grad g x J - j w eps G.M   (e^{jwt}, free space)."""
    E = np.zeros(3, complex)
    H = np.zeros(3, complex)
    _, grad, _, _ = g_and_grad(r, rp, k)
    if J is not None:
        Jw = J * dS[:, None]
        E += -1j * w * MU0 * dyadic_dot(r, rp, k, Jw)
        H += np.sum(np.cross(grad, Jw), axis=0)
    if M is not None:
        Mw = M * dS[:, None]
        E += -np.sum(np.cross(grad, Mw), axis=0)
        H += -1j * w * EPS0 * dyadic_dot(r, rp, k, Mw)
    return E, H


def hertzian_fields(r, k, w, Il):
    """Exact E, H of a z-directed electric current element Il at the origin (point evaluation)."""
    rp = np.zeros((1, 3))
    return fields_from_currents(r, rp, k, w, J=np.array([[0, 0, Il]], complex), dS=np.ones(1))


# ---------------------------------------------------------------- §1 duality
def part1():
    print("§1 duality: magnetic current element vs small electric loop")
    f = 433.92e6
    w = 2 * np.pi * f
    k = w / C0
    I, A = 1.0, (0.0005) ** 2 * np.pi     # 1 A in a 0.5 mm-radius loop (finite-size error ~ (a/r)^2)
    a = np.sqrt(A / np.pi)
    Kl = 1j * w * MU0 * I * A            # equivalent magnetic current moment (V*m)
    # numerical loop: 720 short segments of current I in the xy-plane
    N = 720
    ph = (np.arange(N) + 0.5) * 2 * np.pi / N
    rp = np.c_[a * np.cos(ph), a * np.sin(ph), np.zeros(N)]
    J = I * np.c_[-np.sin(ph), np.cos(ph), np.zeros(N)]
    dl = np.full(N, 2 * np.pi * a / N)
    worst = 0
    for r in [np.array([0.05, 0.02, 0.03]), np.array([0.3, -0.1, 0.4]), np.array([2.0, 1.0, -0.5])]:
        Eloop, Hloop = fields_from_currents(r, rp, k, w, J=J, dS=dl)
        Emag, Hmag = fields_from_currents(r, np.zeros((1, 3)), k, w, M=np.array([[0, 0, Kl]]), dS=np.ones(1))
        err = max(np.linalg.norm(Eloop - Emag) / np.linalg.norm(Eloop), np.linalg.norm(Hloop - Hmag) / np.linalg.norm(Hloop))
        worst = max(worst, err)
    check("loop (I*A) == magnetic dipole K*l = j w mu0 I A, near and far (kr 0.5-21)", worst < 1e-3, f"max rel. error {worst:.1e}")


# ---------------------------------------------------------------- §2 Love equivalence
def sphere_grid(R0, nth=48, nph=96):
    x, wq = np.polynomial.legendre.leggauss(nth)       # x = cos(theta)
    th = np.arccos(x)
    ph = (np.arange(nph) + 0.5) * 2 * np.pi / nph
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    W = np.repeat(wq[:, None], nph, axis=1) * (2 * np.pi / nph) * R0 ** 2
    n = np.c_[(np.sin(TH) * np.cos(PH)).ravel(), (np.sin(TH) * np.sin(PH)).ravel(), np.cos(TH).ravel()]
    return R0 * n, n, W.ravel()


def part2():
    print("§2 Love's equivalence principle on a sphere around a Hertzian dipole")
    f = 915e6
    w = 2 * np.pi * f
    k = w / C0
    lam = C0 / f
    Il = 1e-3 * 0.01
    R0 = 0.3 * lam
    rp, n, dS = sphere_grid(R0)
    Es = np.zeros((len(rp), 3), complex)
    Hs = np.zeros((len(rp), 3), complex)
    for i, p in enumerate(rp):
        Es[i], Hs[i] = hertzian_fields(p, k, w, Il)
    Js = np.cross(n, Hs)            # J_s = n x H
    Ms = -np.cross(n, Es)           # M_s = -n x E
    res = {}
    for label, r in [("outside 0.8 lam", np.array([0.5, 0.3, 0.55]) * lam),
                     ("outside 3 lam", np.array([2.0, -1.5, 1.6]) * lam),
                     ("inside 0.15 lam", np.array([0.1, 0.05, -0.1]) * lam)]:
        Eeq, Heq = fields_from_currents(r, rp, k, w, J=Js, M=Ms, dS=dS)
        Etrue, _ = hertzian_fields(r, k, w, Il)
        res[label] = (Eeq, Etrue)
    for label in ["outside 0.8 lam", "outside 3 lam"]:
        Eeq, Etrue = res[label]
        err = np.linalg.norm(Eeq - Etrue) / np.linalg.norm(Etrue)
        check(f"equivalent currents reproduce the dipole field {label}", err < 1e-4, f"rel. error {err:.1e}")
    Eeq, Etrue = res["inside 0.15 lam"]
    ratio = np.linalg.norm(Eeq) / np.linalg.norm(Etrue)
    check("inside the surface the equivalent currents give zero field (extinction)", ratio < 1e-4,
          f"|E_eq|/|E_dipole| = {ratio:.1e}")
    # half the currents only (J alone): wrong outside, and it radiates inside -> shows why both are needed
    Eeq, _ = fields_from_currents(np.array([2.0, -1.5, 1.6]) * lam, rp, k, w, J=Js, dS=dS)
    Etrue = res["outside 3 lam"][1]
    errJ = np.linalg.norm(Eeq - Etrue) / np.linalg.norm(Etrue)
    check("J_s alone (no M_s) does NOT reproduce the field (error ~ 50 % or more)", errJ > 0.3, f"rel. error {errJ:.2f}")


# ---------------------------------------------------------------- §3 aperture in a ground plane
def te10_aperture_pattern(th, ph, a, b, k):
    """|E| pattern (unnormalised) of a TE10 aperture (E_y = cos(pi x / a)) in an infinite PEC
    ground plane, from M_s = -2 n x E_a. Returns (E_theta, E_phi) without the common factor."""
    X = 0.5 * k * a * np.sin(th) * np.cos(ph)
    Y = 0.5 * k * b * np.sin(th) * np.sin(ph)
    with np.errstate(divide="ignore", invalid="ignore"):
        Fx = np.where(np.abs(np.abs(X) - np.pi / 2) < 1e-9, a / 2 * np.ones_like(X),
                      (np.pi * a / 2) * np.cos(X) / ((np.pi / 2) ** 2 - X ** 2))
    Fy = b * np.sinc(Y / np.pi)
    Lx = 2 * Fx * Fy                 # L_x = int 2 E_a e^{jk r.r'} dS (E0 = 1)
    # E_theta = -jk/(4 pi r) L_phi, E_phi = +jk/(4 pi r) L_theta; L_theta = Lx cos th cos ph, L_phi = -Lx sin ph
    return Lx * np.sin(ph), Lx * np.cos(th) * np.cos(ph)


def aperture_numeric_Lx(th, ph, a, b, k, n=200):
    x, wx = np.polynomial.legendre.leggauss(n)
    x = x * a / 2
    wx = wx * a / 2
    y, wy = np.polynomial.legendre.leggauss(60)
    y = y * b / 2
    wy = wy * b / 2
    kx = k * np.sin(th) * np.cos(ph)
    ky = k * np.sin(th) * np.sin(ph)
    Ix = np.sum(wx * np.cos(np.pi * x / a) * np.exp(1j * kx * x))
    Iy = np.sum(wy * np.exp(1j * ky * y))
    return 2 * Ix * Iy


def directivity(a, b, k, nth=400, nph=400):
    th = np.linspace(0, np.pi / 2, nth)
    ph = np.linspace(0, 2 * np.pi, nph)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    Et, Ep = te10_aperture_pattern(TH, PH, a, b, k)
    U = np.abs(Et) ** 2 + np.abs(Ep) ** 2
    P = integrate.trapezoid(integrate.trapezoid(U * np.sin(TH), ph, axis=1), th)
    return 4 * np.pi * U.max() / P


def hpbw(pattern_fn, th):
    p = pattern_fn(th)
    p = np.abs(p) / np.abs(p).max()
    i = np.where(p >= 1 / np.sqrt(2))[0].max()
    if i >= len(th) - 1:
        return float("nan")             # never falls 3 dB in the visible half-space (> 180 deg)
    return 2 * np.degrees(np.interp(1 / np.sqrt(2), [p[i + 1], p[i]], [th[i + 1], th[i]]))


def aperture_admittance(a, b, f, umax=7.0, nt=400, nu=3000, nph=400):
    """Single-mode variational (Galerkin) admittance of a TE10 aperture in an infinite PEC flange,
    normalised to the TE10 mode admittance: y = P_aperture / P_mode for the same aperture field
    E_y = E0 cos(pi x/a). P_aperture = half the complex power of 2M (M = E_y x_hat) in free space,
    from the spectral form P = (1/(16 pi^2 eta k)) int int (k^2 - kx^2) |K~|^2 / kz dkx dky."""
    k = 2 * np.pi * f / C0
    beta = np.sqrt(k ** 2 - (np.pi / a) ** 2)
    Zte = k * ETA0 / beta

    def K2(kx, ky):
        X = kx * a / 2
        Fx = (np.pi * a / 2) * np.cos(X) / ((np.pi / 2) ** 2 - X ** 2)
        Fy = b * np.sinc(ky * b / 2 / np.pi)
        return np.abs(2 * Fx * Fy) ** 2

    ph, wph = roots_legendre(nph)
    ph = (ph + 1) * np.pi / 4
    wph = wph * np.pi / 4                       # 0..pi/2, x4 by symmetry
    # visible: k_rho = k sin t
    t, wt = roots_legendre(nt)
    t = (t + 1) * np.pi / 4
    wt = wt * np.pi / 4
    T, PH = np.meshgrid(t, ph, indexing="ij")
    kr = k * np.sin(T)
    kx, ky = kr * np.cos(PH), kr * np.sin(PH)
    Ivis = 4 * np.sum(wt[:, None] * wph[None, :] * (k ** 2 - kx ** 2) * K2(kx, ky) * k * np.sin(T))
    # invisible: k_rho = k cosh u, 1/kz = j/|kz|
    u, wu = roots_legendre(nu)
    u = (u + 1) * umax / 2
    wu = wu * umax / 2
    U, PH = np.meshgrid(u, ph, indexing="ij")
    kr = k * np.cosh(U)
    kx, ky = kr * np.cos(PH), kr * np.sin(PH)
    Iinv = 4 * np.sum(wu[:, None] * wph[None, :] * (k ** 2 - kx ** 2) * K2(kx, ky) * k * np.cosh(U))
    P_tot = (Ivis + 1j * Iinv) / (16 * np.pi ** 2 * ETA0 * k)       # E0 = 1
    P_ap = 0.5 * P_tot
    P_mode = (a * b / 4) / Zte
    y = P_ap / P_mode
    G = (1 - y) / (1 + y)
    return y, G


def part3():
    print("§3 TE10 aperture in a PEC ground plane (open-ended WR-90 with an infinite flange)")
    f = 10e9
    k = 2 * np.pi * f / C0
    lam = C0 / f
    a, b = 22.86e-3, 10.16e-3
    out = {}
    worst = 0
    for th in np.radians([0, 20, 45, 70, 89]):
        for ph in np.radians([0, 30, 90]):
            Et, Ep = te10_aperture_pattern(np.array(th), np.array(ph), a, b, k)
            Lx = aperture_numeric_Lx(th, ph, a, b, k)
            Et2, Ep2 = Lx * np.sin(ph), Lx * np.cos(th) * np.cos(ph)
            worst = max(worst, abs(Et - Et2) + abs(Ep - Ep2))
    check("closed-form L_x = numerical radiation integral of M_s (all angles)", worst < 1e-9, f"max abs diff {worst:.1e}")
    th = np.radians(np.linspace(0, 90, 9001))
    E_e = lambda t: te10_aperture_pattern(t, np.full_like(t, np.pi / 2), a, b, k)[0]
    E_h = lambda t: te10_aperture_pattern(t, np.zeros_like(t), a, b, k)[1]
    hp_e, hp_h = hpbw(E_e, th), hpbw(E_h, th)
    D = directivity(a, b, k)
    D_large = 32 / np.pi * a * b / lam ** 2
    print(f"     WR-90 @ 10 GHz: a = {a/lam:.3f} lam, b = {b/lam:.3f} lam")
    print(f"     E-plane HPBW {hp_e:.1f} deg, H-plane HPBW {hp_h:.1f} deg")
    print(f"     E-plane level at 90 deg: {20*np.log10(abs(E_e(np.array([np.pi/2])))[0]/abs(E_e(np.array([0.0])))[0]):.2f} dB;"
          f" H-plane at 60 deg: {20*np.log10(abs(E_h(np.array([np.radians(60)])))[0]/abs(E_h(np.array([0.0])))[0]):.2f} dB")
    print(f"     directivity (hemisphere integral) {D:.3f} = {10*np.log10(D):.2f} dBi;"
          f" large-aperture formula (32/pi)ab/lam^2 = {D_large:.3f} = {10*np.log10(D_large):.2f} dBi")
    check("WR-90 flanged-aperture directivity: hemisphere integral 6-7 dBi; the large-aperture formula is ~2 dB low",
          6.0 < 10 * np.log10(D) < 7.0 and 1.5 < 10 * np.log10(D / D_large) < 2.8,
          f"{10*np.log10(D):.2f} vs {10*np.log10(D_large):.2f} dBi")
    # large aperture: the two must converge
    a2, b2 = 10 * lam, 5 * lam
    D2 = directivity(a2, b2, k, nth=2500, nph=1200)
    D2_large = 32 / np.pi * a2 * b2 / lam ** 2
    check("10 x 5 lam aperture: hemisphere directivity -> (32/pi)ab/lam^2 (within 0.2 dB)",
          abs(10 * np.log10(D2 / D2_large)) < 0.2, f"{10*np.log10(D2):.2f} vs {10*np.log10(D2_large):.2f} dBi")
    # 2.45 GHz WR-430 and 24 GHz WR-42 for the page
    for name, aa, bb, ff in [("WR-430 @ 2.45 GHz", 109.22e-3, 54.61e-3, 2.45e9), ("WR-42 @ 24 GHz", 10.668e-3, 4.318e-3, 24e9)]:
        kk = 2 * np.pi * ff / C0
        ll = C0 / ff
        Dd = directivity(aa, bb, kk)
        the = np.radians(np.linspace(0, 90, 9001))
        he = hpbw(lambda t: te10_aperture_pattern(t, np.full_like(t, np.pi / 2), aa, bb, kk)[0], the)
        hh = hpbw(lambda t: te10_aperture_pattern(t, np.zeros_like(t), aa, bb, kk)[1], the)
        print(f"     {name}: D = {10*np.log10(Dd):.2f} dBi (formula {10*np.log10(32/np.pi*aa*bb/ll**2):.2f}), HPBW E {he:.0f} / H {hh:.0f} deg")
        out[name] = (10 * np.log10(Dd), he, hh)
    # aperture admittance (single-mode variational). Pre-registered 2026-10-13 before computing:
    # |S11| within 2 dB of the openEMS flanged-guide result (-10.7 dB coarse / -11.8 dB fine mesh).
    y, G = aperture_admittance(a, b, f)
    y2, _ = aperture_admittance(a, b, f, umax=8.0, nu=5000)
    print(f"     aperture admittance y = G + jB = {y.real:.4f} {y.imag:+.4f}j (umax 8: {y2.real:.4f} {y2.imag:+.4f}j);"
          f" |Gamma| = {abs(G):.3f} = {20*np.log10(abs(G)):.1f} dB")
    check("variational aperture |S11| of flanged WR-90 within 2 dB of openEMS (-10.7 to -11.8 dB)",
          -13.8 <= 20 * np.log10(abs(G)) <= -8.7 and abs(y2 - y) < 0.01, f"{20*np.log10(abs(G)):.1f} dB")
    for ff in [8.2e9, 12.4e9]:
        yy, GG = aperture_admittance(a, b, ff)
        print(f"     {ff/1e9:.1f} GHz: y = {yy.real:.3f} {yy.imag:+.3f}j, |Gamma| {20*np.log10(abs(GG)):.1f} dB")
    out["WR-90 y"] = y
    out["WR-90"] = dict(D_dBi=10 * np.log10(D), hpbw_e=hp_e, hpbw_h=hp_h)
    return out


# ---------------------------------------------------------------- §4 reciprocity
def part4():
    print("§4 Lorentz reciprocity")
    rng = np.random.default_rng(5)
    f = 433.92e6
    w = 2 * np.pi * f
    k = w / C0
    worst = 0
    worst_img = 0
    for _ in range(20):
        r1, r2 = rng.normal(size=3), rng.normal(size=3)
        r1[2], r2[2] = abs(r1[2]) + 0.05, abs(r2[2]) + 0.05     # keep above z = 0 for the image case
        J1, J2 = rng.normal(size=3) + 1j * rng.normal(size=3), rng.normal(size=3) + 1j * rng.normal(size=3)
        E12, _ = fields_from_currents(r2, r1[None, :], k, w, J=J1[None, :], dS=np.ones(1))   # field of 1 at 2
        E21, _ = fields_from_currents(r1, r2[None, :], k, w, J=J2[None, :], dS=np.ones(1))
        worst = max(worst, abs(np.dot(E12, J2) - np.dot(E21, J1)) / abs(np.dot(E12, J2)))

        # PEC ground at z = 0: image of J is (-Jx, -Jy, +Jz) at (x, y, -z)
        def Epec(r_obs, r_src, J):
            Ei, _ = fields_from_currents(r_obs, r_src[None, :], k, w, J=J[None, :], dS=np.ones(1))
            ri = r_src * np.array([1, 1, -1])
            Ji = J * np.array([-1, -1, 1])
            Eim, _ = fields_from_currents(r_obs, ri[None, :], k, w, J=Ji[None, :], dS=np.ones(1))
            return Ei + Eim
        a12 = np.dot(Epec(r2, r1, J1), J2)
        a21 = np.dot(Epec(r1, r2, J2), J1)
        worst_img = max(worst_img, abs(a12 - a21) / abs(a12))
    check("<E1, J2> = <E2, J1>, free space, 20 random dipole pairs", worst < 1e-12, f"max rel. diff {worst:.1e}")
    check("<E1, J2> = <E2, J1> over a PEC ground plane (image Green's function)", worst_img < 1e-12, f"{worst_img:.1e}")
    # mixed: electric source 1, magnetic source 2. Reaction <a,b> = int (E_a.J_b - H_a.M_b)
    r1, r2 = np.array([0.1, 0.2, 0.3]), np.array([-0.4, 0.5, 0.2])
    J1 = np.array([0.3, -1.0, 0.5], complex)
    M2 = np.array([1.0, 0.2, -0.7], complex)
    E1, H1 = fields_from_currents(r2, r1[None, :], k, w, J=J1[None, :], dS=np.ones(1))
    E2, H2 = fields_from_currents(r1, r2[None, :], k, w, M=M2[None, :], dS=np.ones(1))
    lhs = -np.dot(H1, M2)              # <1,2> = E1.J2 - H1.M2 with J2 = 0
    rhs = np.dot(E2, J1)               # <2,1> = E2.J1 - H2.M1 with M1 = 0
    check("mixed reaction: -H1.M2 = E2.J1 (electric source vs magnetic source)", abs(lhs - rhs) / abs(lhs) < 1e-12,
          f"{lhs:.4e} vs {rhs:.4e}")
    # networks
    Z = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
    Z = Z + Z.T                         # reciprocal: Z symmetric
    Z0 = 50
    S = (Z - Z0 * np.eye(2)) @ np.linalg.inv(Z + Z0 * np.eye(2))
    Zg = np.array([[0, -50], [50, 0]], complex)   # ideal gyrator, R = 50 ohm
    Sg = (Zg - Z0 * np.eye(2)) @ np.linalg.inv(Zg + Z0 * np.eye(2))
    check("symmetric Z -> S12 = S21 (reciprocal 2-port)", abs(S[0, 1] - S[1, 0]) < 1e-12)
    check("ideal gyrator: S21 = -S12 (non-reciprocal, needs a magnetised ferrite or active device)",
          abs(Sg[0, 1] + Sg[1, 0]) < 1e-12 and abs(Sg[0, 1]) > 0.99, f"S12 {Sg[0,1]:.2f}, S21 {Sg[1,0]:.2f}")


# ---------------------------------------------------------------- §5 Bethe hole
def part5():
    print("§5 Bethe small-hole transmission")
    # magnetic dipole moment of the hole (shadow side), Bethe: m = -(4 r^3/3) H_sc, with H_sc = 2 H_inc on the screen.
    # On the shadow side it radiates with its (same-sign) image: field of 2m in free space, into a half-space.
    r0 = 1.0
    k = 0.05
    H0 = 1.0
    m = (4 * r0 ** 3 / 3) * 2 * H0
    P_full_2m = ETA0 * k ** 4 * (2 * m) ** 2 / (12 * np.pi)       # magnetic dipole power, free space
    P = 0.5 * P_full_2m                                            # half-space
    S_inc = 0.5 * ETA0 * H0 ** 2
    sigma = P / S_inc
    sigma_bethe = 64 * k ** 4 * r0 ** 6 / (27 * np.pi)
    check("transmission cross-section from alpha_m = 4r^3/3 and imaging = 64 k^4 r^6/(27 pi)",
          abs(sigma / sigma_bethe - 1) < 1e-12, f"{sigma:.4e} vs {sigma_bethe:.4e}")
    rows = []
    for d_mm in [3, 5, 10]:
        for f in [433.92e6, 915e6, 2.45e9]:
            r = d_mm / 2 * 1e-3
            kk = 2 * np.pi * f / C0
            T = 64 / (27 * np.pi ** 2) * (kk * r) ** 4                 # sigma / (pi r^2)
            rows.append((d_mm, f / 1e9, kk * r, 10 * np.log10(T)))
            print(f"     hole d = {d_mm:2d} mm, {f/1e9:.3f} GHz: k r = {kk*r:.4f}, sigma/(pi r^2) = {10*np.log10(T):6.1f} dB")
    # Babinet/Booker: complementary slot in an infinite thin screen, Z_slot Z_dipole = eta0^2/4
    Zd = 73.1 + 42.5j
    Zs = ETA0 ** 2 / (4 * Zd)
    print(f"     Booker: half-wave dipole {Zd:.1f} ohm -> complementary half-wave slot {Zs.real:.1f} {Zs.imag:+.1f}j ohm")
    check("Booker relation: lambda/2 slot = eta0^2/(4 Z_dipole) ~ 363 - j211 ohm", abs(Zs - (362.7 - 210.9j)) < 1.0)
    return rows


def part6(ref):
    path = os.path.join(HERE, "s5_aperture_openems_results.txt")
    print("§6 openEMS comparison")
    if not os.path.exists(path):
        print("     (no openEMS results file; run s5_aperture_openems.py with the openEMS venv)")
        return
    runs = [json.loads(l) for l in open(path) if l.strip().startswith("{")]
    f = 10e9
    k = 2 * np.pi * f / C0
    a, b = 22.86e-3, 10.16e-3
    for run in runs:
        if not np.isfinite(run["Dmax_dBi"]):
            print(f"     run '{run['label']}': NF2FF returned NaN (closed-box variant mis-set; ignored)")
            continue
        th = np.radians(np.array(run["theta_deg"]))
        Ee = np.array(run["E_plane_dBi"])
        Eh = np.array(run["H_plane_dBi"])
        D_eq = ref["WR-90"]["D_dBi"]
        pe = 20 * np.log10(np.abs(te10_aperture_pattern(th, np.full_like(th, np.pi / 2), a, b, k)[0]) /
                           np.abs(te10_aperture_pattern(np.array([0.0]), np.array([np.pi / 2]), a, b, k)[0]))
        ph_ = 20 * np.log10(np.abs(te10_aperture_pattern(th, np.zeros_like(th), a, b, k)[1]) /
                            np.abs(te10_aperture_pattern(np.array([0.0]), np.array([0.0]), a, b, k)[1]))
        Ee_n = Ee - Ee[np.argmin(np.abs(th))]
        Eh_n = Eh - Eh[np.argmin(np.abs(th))]
        m_e = np.abs(np.degrees(th)) <= 45
        m_h = np.abs(np.degrees(th)) <= 60
        de = np.max(np.abs(Ee_n[m_e] - pe[m_e]))
        dh = np.max(np.abs(Eh_n[m_h] - ph_[m_h]))
        print(f"     run '{run['label']}': flange {run['flange_mm']} mm, Dmax {run['Dmax_dBi']:.2f} dBi (equivalence {D_eq:.2f}),"
              f" |S11| {run['S11_dB_10GHz']:.1f} dB; max pattern dev. E-plane(|th|<=45) {de:.2f} dB, H-plane(|th|<=60) {dh:.2f} dB")
        # pre-registered (written before the first openEMS run): H-plane within 1.0 dB to 60 deg,
        # E-plane within 2.0 dB to 45 deg, Dmax within 1.0 dB of the equivalence-principle value.
        if run["label"] not in ("F90", "F150", "F90fine"):
            continue                    # exploratory run (not pre-registered): printed, not graded
        check(f"openEMS '{run['label']}' vs equivalence: H-plane <= 1 dB (|th|<=60), E-plane <= 2 dB (|th|<=45), Dmax <= 1 dB",
              dh <= 1.0 and de <= 2.0 and abs(run["Dmax_dBi"] - D_eq) <= 1.0,
              f"dH {dh:.2f}, dE {de:.2f}, dD {run['Dmax_dBi'] - D_eq:+.2f} dB")


if __name__ == "__main__":
    part1()
    part2()
    ref = part3()
    part4()
    part5()
    part6(ref)
    print(f"\n{sum(checks)}/{len(checks)} checks passed")
