#!/usr/bin/env python3
"""
ant_mom_general.py -- general thin-wire MoM for arbitrary polyline wires with junctions
(free space, PEC wires, optional lumped loads). Own implementation for verification of
kb/08-antennas pages (monopole radials, folded dipole, small loops, axial-mode helix, QFH).

Formulation: mixed-potential EFIE, Galerkin testing, triangle basis functions on every
interior polyline vertex and at wire-to-wire junctions (N-1 basis functions for an N-wire
junction, all sharing the first wire-end). Reduced kernel R = sqrt(|r - r'|^2 + a^2).
Inner integrals: analytic 1/R along the straight source segment + Gauss-Legendre for the
smooth remainder; outer integrals Gauss-Legendre (sub-divided for near pairs).

Infinite PEC ground: mirror the geometry about z = 0 and put the feed gap in a vertical
wire at z = 0 (by symmetry the solution then satisfies the image conditions); halve Z_in and
double the directivity (radiation only into the upper half space).

Z_mn = j w mu  sum_pq (s_p . s_q) <f_p, G f_q>  +  1/(j w eps) sum_pq <f_p', G f_q'>

Run:  python3 tools/verify/ant_mom_general.py      (self-tests; ~1-3 min)
"""
import numpy as np

C0 = 299792458.0
MU0 = 4e-7 * np.pi
EPS0 = 1.0 / (MU0 * C0 ** 2)
ETA0 = np.sqrt(MU0 / EPS0)
_gx, _gw = np.polynomial.legendre.leggauss(8)


class Structure:
    def __init__(self):
        self.wires = []   # list of (points (n,3), radius)

    def add_polyline(self, pts, a):
        pts = np.asarray(pts, dtype=float)
        self.wires.append((pts, a))
        return len(self.wires) - 1

    def add_line(self, p0, p1, a, nseg):
        p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
        t = np.linspace(0, 1, nseg + 1)[:, None]
        return self.add_polyline(p0 + t * (p1 - p0), a)

    def build(self, tol=1e-9):
        seg_A, seg_B, seg_a, seg_w = [], [], [], []
        first_seg = []
        for wi, (pts, a) in enumerate(self.wires):
            first_seg.append(len(seg_A))
            for j in range(len(pts) - 1):
                seg_A.append(pts[j]); seg_B.append(pts[j + 1]); seg_a.append(a); seg_w.append(wi)
        self.A = np.array(seg_A); self.B = np.array(seg_B)
        self.a = np.array(seg_a); self.segw = np.array(seg_w)
        d = self.B - self.A
        self.L = np.linalg.norm(d, axis=1)
        self.s = d / self.L[:, None]
        self.first_seg = first_seg
        # basis halves: list of lists of (seg, shape, sign); shape 1 = rise (0 at A -> 1 at B), 0 = fall
        basis = []
        self.basis_tag = []
        for wi, (pts, a) in enumerate(self.wires):
            fs = first_seg[wi]
            for j in range(1, len(pts) - 1):
                basis.append([(fs + j - 1, 1, +1.0), (fs + j, 0, +1.0)])
                self.basis_tag.append(("int", wi, j))
        # junctions
        ends = []
        for wi, (pts, a) in enumerate(self.wires):
            fs = first_seg[wi]
            nsg = len(pts) - 1
            ends.append((pts[0], wi, "start", fs))
            ends.append((pts[-1], wi, "end", fs + nsg - 1))
        used = [False] * len(ends)
        self.junctions = []
        for i, (p, wi, which, sg) in enumerate(ends):
            if used[i]:
                continue
            group = [i]
            for j in range(i + 1, len(ends)):
                if not used[j] and np.linalg.norm(ends[j][0] - p) < tol:
                    group.append(j)
            if len(group) > 1:
                for g in group:
                    used[g] = True
                self.junctions.append((p, group))
                e0 = ends[group[0]]
                # half toward the junction on e0's segment
                h0 = (e0[3], 1, +1.0) if e0[2] == "end" else (e0[3], 0, -1.0)
                for g in group[1:]:
                    ek = ends[g]
                    hk = (ek[3], 0, +1.0) if ek[2] == "start" else (ek[3], 1, -1.0)
                    basis.append([h0, hk])
                    self.basis_tag.append(("junc", tuple(p), e0[1], ek[1]))
        self.basis = basis
        return self

    def basis_at_point(self, p, tol=1e-9):
        """Indices of basis functions whose shared node is at point p (interior vertex or junction)."""
        p = np.asarray(p, float)
        out = []
        for n, tag in enumerate(self.basis_tag):
            if tag[0] == "int":
                wi, j = tag[1], tag[2]
                if np.linalg.norm(self.wires[wi][0][j] - p) < tol:
                    out.append(n)
            else:
                if np.linalg.norm(np.array(tag[1]) - p) < tol:
                    out.append(n)
        return out


def _pair_block(k, Ao, so, Lo, Ai, si, Li, ai, nsub):
    """Vectorised over pairs P: outer segments (Ao, so, Lo), inner (Ai, si, Li, ai).
    Returns J (P,2,2) shape integrals and J0 (P,)."""
    P = Ao.shape[0]
    t = np.linspace(0, 1, nsub + 1)
    h = Lo[:, None] / nsub
    left = Lo[:, None] * t[None, :-1]
    uo = (left[:, :, None] + h[:, :, None] / 2 * (1 + _gx[None, None, :])).reshape(P, -1)   # (P,no)
    wo = np.broadcast_to((h / 2)[:, :, None] * _gw[None, None, :], (P, nsub, 8)).reshape(P, -1)
    ro = Ao[:, None, :] + uo[:, :, None] * so[:, None, :]            # (P,no,3)
    dv = ro - Ai[:, None, :]
    t0 = np.einsum("pnk,pk->pn", dv, si)                              # projection on inner line
    rho2 = np.maximum(np.einsum("pnk,pnk->pn", dv, dv) - t0 ** 2, 0.0) + ai[:, None] ** 2
    rho = np.sqrt(rho2)
    Lb = Li[:, None]
    ash = np.arcsinh((Lb - t0) / rho) - np.arcsinh((-t0) / rho)
    R_L = np.sqrt((Lb - t0) ** 2 + rho2)
    R_0 = np.sqrt(t0 ** 2 + rho2)
    S0 = ash / (4 * np.pi)
    S1 = ((R_L - R_0) + t0 * ash) / (4 * np.pi) / Lb
    # smooth remainder
    ui = Li[:, None] / 2 * (1 + _gx[None, :])                         # (P,8)
    wi = Li[:, None] / 2 * _gw[None, :]
    ri = Ai[:, None, :] + ui[:, :, None] * si[:, None, :]             # (P,8,3)
    diff = ro[:, :, None, :] - ri[:, None, :, :]                      # (P,no,8,3)
    R = np.sqrt(np.einsum("pnmk,pnmk->pnm", diff, diff) + ai[:, None, None] ** 2)
    kern = (np.exp(-1j * k * R) - 1.0) / (4 * np.pi * R)
    T0 = np.einsum("pnm,pm->pn", kern, wi)
    T1 = np.einsum("pnm,pm->pn", kern, wi * ui / Li[:, None])
    A_rise = S1 + T1
    A_tot = S0 + T0
    A_fall = A_tot - A_rise
    phi1 = uo / Lo[:, None]
    phi0 = 1 - phi1
    J = np.empty((P, 2, 2), dtype=complex)
    J[:, 0, 0] = np.sum(wo * phi0 * A_fall, 1)
    J[:, 0, 1] = np.sum(wo * phi0 * A_rise, 1)
    J[:, 1, 0] = np.sum(wo * phi1 * A_fall, 1)
    J[:, 1, 1] = np.sum(wo * phi1 * A_rise, 1)
    return J, np.sum(wo * A_tot, 1)


def solve(st, freq, feeds, loads=(), chunk=6000):
    """feeds: list of (list_of_basis_indices, V). The same V is applied to each listed basis
    (a gap at a junction node that all listed bases cross on the same side).
    loads: list of (list_of_basis_indices, Z) series loads (added to Z_mm)."""
    k = 2 * np.pi * freq / C0
    w = 2 * np.pi * freq
    ns = len(st.L)
    S, T = np.meshgrid(np.arange(ns), np.arange(ns), indexing="ij")
    S = S.ravel(); T = T.ravel()
    cs = (st.A + st.B) / 2
    dist = np.linalg.norm(cs[S] - cs[T], axis=1)
    near = dist < 1.5 * (st.L[S] + st.L[T])
    Jm = np.empty((ns * ns, 2, 2), dtype=complex)
    J0m = np.empty(ns * ns, dtype=complex)
    for mask, nsub in ((near, 6), (~near, 1)):
        idx = np.where(mask)[0]
        step = chunk if nsub == 1 else max(500, chunk // 6)
        for c in range(0, len(idx), step):
            ii = idx[c:c + step]
            J, J0 = _pair_block(k, st.A[S[ii]], st.s[S[ii]], st.L[S[ii]],
                                st.A[T[ii]], st.s[T[ii]], st.L[T[ii]], st.a[T[ii]], nsub)
            Jm[ii] = J; J0m[ii] = J0
    Jm = Jm.reshape(ns, ns, 2, 2); J0m = J0m.reshape(ns, ns)
    SS = st.s @ st.s.T
    nb = len(st.basis)
    # each basis has exactly two halves -> vectorise over half-index (0/1)
    seg = np.array([[h[0] for h in b] for b in st.basis])
    shp = np.array([[h[1] for h in b] for b in st.basis])
    sgn = np.array([[h[2] for h in b] for b in st.basis])
    der = sgn * np.where(shp == 1, 1.0, -1.0) / st.L[seg]
    Z = np.zeros((nb, nb), dtype=complex)
    for p in range(2):
        for q in range(2):
            sp, sq = seg[:, p], seg[:, q]
            Jpq = Jm[np.ix_(sp, sq)]
            shape_term = Jpq[np.arange(nb)[:, None], np.arange(nb)[None, :], shp[:, p][:, None], shp[:, q][None, :]]
            Z += 1j * w * MU0 * (sgn[:, p][:, None] * sgn[:, q][None, :]) * SS[np.ix_(sp, sq)] * shape_term \
                 + np.outer(der[:, p], der[:, q]) * J0m[np.ix_(sp, sq)] / (1j * w * EPS0)
    for (bl, Zl) in loads:
        for b in bl:
            Z[b, b] += Zl
    V = np.zeros(nb, dtype=complex)
    for (bl, v) in feeds:
        for b in bl:
            V[b] += v
    I = np.linalg.solve(Z, V)
    Zin = []
    Pin = 0.0
    for (bl, v) in feeds:
        Itot = np.sum(I[bl])
        Zin.append(v / Itot)
        Pin += 0.5 * np.real(v * np.conj(Itot))
    Ploss = sum(0.5 * np.real(Zl) * np.sum(np.abs(I[bl]) ** 2) for (bl, Zl) in loads)
    return dict(k=k, I=I, Zin=Zin, Pin=Pin, Ploss=Ploss, st=st, seg=seg, shp=shp, sgn=sgn)


def far_field(sol, th, ph):
    """Returns (E_theta, E_phi) far-field pattern vectors (arbitrary common scale: N components)."""
    st = sol["st"]; k = sol["k"]
    th = np.asarray(th, float); ph = np.asarray(ph, float)
    th, ph = np.broadcast_arrays(th, ph)
    rhat = np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)], -1)
    that = np.stack([np.cos(th) * np.cos(ph), np.cos(th) * np.sin(ph), -np.sin(th)], -1)
    phat = np.stack([-np.sin(ph), np.cos(ph), np.zeros_like(ph)], -1)
    N = np.zeros(th.shape + (3,), dtype=complex)
    # accumulate per segment: sum over halves of I_n * sgn * int shape * exp(jk rhat.r') s ds
    ns = len(st.L)
    coef = np.zeros((ns, 2), dtype=complex)   # coefficient for (fall, rise) shape on each segment
    for n in range(len(st.basis)):
        for p in range(2):
            coef[sol["seg"][n, p], sol["shp"][n, p]] += sol["I"][n] * sol["sgn"][n, p]
    u = (1 + _gx) / 2
    for sgi in range(ns):
        if not np.any(coef[sgi]):
            continue
        rq = st.A[sgi][None, :] + (u * st.L[sgi])[:, None] * st.s[sgi][None, :]   # (8,3)
        wq = st.L[sgi] / 2 * _gw
        f = coef[sgi, 0] * (1 - u) + coef[sgi, 1] * u
        ph_ = np.exp(1j * k * np.tensordot(rhat, rq, axes=([-1], [1])))            # (...,8)
        N += np.tensordot(ph_, wq * f, axes=([-1], [0]))[..., None] * st.s[sgi]
    Nt = np.einsum("...k,...k->...", N, that)
    Np = np.einsum("...k,...k->...", N, phat)
    return Nt, Np


def U_components(sol, th, ph):
    Nt, Np = far_field(sol, th, ph)
    c = ETA0 * sol["k"] ** 2 / (32 * np.pi ** 2)
    ER = (Nt + 1j * Np) / np.sqrt(2)     # RHCP component for exp(+jwt) (theta, phi, r right-handed)
    EL = (Nt - 1j * Np) / np.sqrt(2)
    return c * np.abs(Nt) ** 2, c * np.abs(Np) ** 2, c * np.abs(ER) ** 2, c * np.abs(EL) ** 2


def prad(sol, nth=91, nph=144, upper_only=False):
    th = np.linspace(0, np.pi / 2 if upper_only else np.pi, nth)
    ph = np.linspace(0, 2 * np.pi, nph, endpoint=False)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    Ut, Up, _, _ = U_components(sol, TH, PH)
    U = Ut + Up
    tz = getattr(np, "trapezoid", None) or np.trapz
    return tz(np.sum(U, 1) * (ph[1] - ph[0]) * np.sin(th), th)


# ----------------------------------------------------------------------------- self tests
def test_dipole(f=433e6):
    lam = C0 / f
    st = Structure(); st.add_line([0, 0, -0.25 * lam], [0, 0, 0.25 * lam], 1e-4 * lam, 40); st.build()
    b = st.basis_at_point([0, 0, 0])
    sol = solve(st, f, [(b, 1.0)])
    P = prad(sol)
    Ut, Up, _, _ = U_components(sol, np.array(np.pi / 2), np.array(0.0))
    D = 4 * np.pi * float(Ut + Up) / P
    print(f"  dipole 0.5 lam, a=1e-4 lam: Zin = {sol['Zin'][0]:.2f} ohm (parallel-wire solver: 80.07+44.60j), "
          f"D = {10*np.log10(D):.2f} dBi, Prad/Pin = {P/sol['Pin']:.4f}")


def ground_plane_antenna(f, h_l, rad_l, droop_deg, nrad=4, a_l=2e-3, nseg_v=16, nseg_r=16):
    lam = C0 / f
    st = Structure()
    st.add_line([0, 0, 0], [0, 0, h_l * lam], a_l * lam, nseg_v)
    for i in range(nrad):
        phi = 2 * np.pi * i / nrad
        dr = np.radians(droop_deg)
        end = rad_l * lam * np.array([np.cos(dr) * np.cos(phi), np.cos(dr) * np.sin(phi), -np.sin(dr)])
        st.add_line([0, 0, 0], end, a_l * lam, nseg_r)
    st.build()
    # the vertical wire is wire 0 = first wire-end in the junction group -> all junction bases cross the gap
    b = st.basis_at_point([0, 0, 0])
    return st, solve(st, f, [(b, 1.0)])


def test_ground_plane(f=433e6):
    from scipy.optimize import brentq
    lam = C0 / f
    print("  quarter-wave ground-plane antenna, 4 radials of 0.25 lam, a = 2e-3 lam (resonated vertical):")
    for droop in [0, 30, 45, 60]:
        g = lambda h: np.imag(ground_plane_antenna(f, h, 0.25, droop)[1]["Zin"][0])
        try:
            hr = brentq(g, 0.20, 0.27, xtol=1e-4)
        except ValueError:
            hr = 0.24
        st, sol = ground_plane_antenna(f, hr, 0.25, droop)
        P = prad(sol)
        th = np.linspace(0, np.pi, 181)
        Ut, Up, _, _ = U_components(sol, th, np.zeros_like(th))
        U = Ut + Up
        D = 4 * np.pi * U.max() / P
        el = 90 - np.degrees(th[np.argmax(U)])
        print(f"    radial droop {droop:2d} deg: resonant vertical h = {hr:.4f} lam, Zin = {sol['Zin'][0].real:5.1f} ohm, "
              f"peak D = {10*np.log10(D):.2f} dBi at elevation {el:+.0f} deg, Prad/Pin = {P/sol['Pin']:.3f}")


def test_monopole_image(f=433e6):
    lam = C0 / f
    st = Structure(); st.add_line([0, 0, -0.25 * lam], [0, 0, 0.25 * lam], 1e-3 * lam, 40); st.build()
    sol = solve(st, f, [(st.basis_at_point([0, 0, 0]), 1.0)])
    P = prad(sol)
    Ut, Up, _, _ = U_components(sol, np.array(np.pi / 2), np.array(0.0))
    D = 4 * np.pi * float(Ut + Up) / P
    print(f"  monopole 0.25 lam on infinite PEC (image): Zin = {sol['Zin'][0]/2:.2f} ohm, D = {10*np.log10(2*D):.2f} dBi")


def folded_dipole(f, L_l, s_l, a1_l, a2_l, nseg=30):
    lam = C0 / f
    st = Structure()
    L, s = L_l * lam, s_l * lam
    # fed conductor on x = 0 split at centre; second conductor at x = s; end connectors
    st.add_line([0, 0, -L / 2], [0, 0, 0], a1_l * lam, nseg // 2)
    st.add_line([0, 0, 0], [0, 0, L / 2], a1_l * lam, nseg // 2)
    st.add_line([s, 0, -L / 2], [s, 0, L / 2], a2_l * lam, nseg)
    st.add_line([0, 0, L / 2], [s, 0, L / 2], min(a1_l, a2_l) * lam, 2)
    st.add_line([0, 0, -L / 2], [s, 0, -L / 2], min(a1_l, a2_l) * lam, 2)
    st.build()
    return st, solve(st, f, [(st.basis_at_point([0, 0, 0]), 1.0)])


def test_folded(f=433e6):
    from scipy.optimize import brentq
    lam = C0 / f
    s_l = 0.02
    for (a1, a2) in [(1e-3, 1e-3), (1e-3, 3e-3), (3e-3, 1e-3)]:
        g = lambda L: np.imag(folded_dipole(f, L, s_l, a1, a2)[1]["Zin"][0])
        try:
            Lr = brentq(g, 0.40, 0.50, xtol=1e-4)
        except ValueError:
            Lr = 0.47
        st, sol = folded_dipole(f, Lr, s_l, a1, a2)
        ratio_formula = (1 + np.log(s_l / a1) / np.log(s_l / a2)) ** 2
        print(f"    folded dipole s = {s_l} lam, a_fed = {a1}, a_other = {a2} lam: resonant L = {Lr:.4f} lam, "
              f"Zin = {sol['Zin'][0].real:.0f} ohm; step-up formula (1+ln(s/a1)/ln(s/a2))^2 = {ratio_formula:.2f} "
              f"-> {ratio_formula*72:.0f} ohm for a 72-ohm dipole")


def small_loop(f, D, a, nside=16):
    lam = C0 / f
    st = Structure()
    ang = np.linspace(0, 2 * np.pi, nside + 1)
    pts = np.stack([D / 2 * np.cos(ang), D / 2 * np.sin(ang), np.zeros_like(ang)], 1)
    # split into one polyline that starts and ends at the feed point (closed loop -> junction)
    st.add_polyline(pts, a)
    st.build()
    b = st.basis_at_point(pts[0])
    return st, solve(st, f, [(b, 1.0)])


def test_loop(f=433e6):
    lam = C0 / f
    for D in [0.030, 0.050, 0.080]:
        st, sol = small_loop(f, D, 0.5e-3, nside=24)
        C = np.pi * D
        Rr_formula = 20 * np.pi ** 2 * (C / lam) ** 4
        P = prad(sol)
        print(f"    loop D = {D*1e3:.0f} mm (C = {C/lam:.3f} lam): MoM Rin = {sol['Zin'][0].real:.4f} ohm, X = {sol['Zin'][0].imag:.1f} ohm, "
              f"small-loop formula Rr = {Rr_formula:.4f} ohm, Prad/Pin = {P/sol['Pin']:.3f}")


def helix_over_ground(f, N, C_l, S_l, a_l=0.005, seg_per_turn=16, feed_h_l=0.02, handed="R"):
    """Axial-mode helix above an infinite PEC ground (image method). handed = 'R' or 'L' winding."""
    lam = C0 / f
    R = C_l * lam / (2 * np.pi)
    S = S_l * lam
    h0 = feed_h_l * lam
    sgn = 1 if handed == "R" else -1
    nseg = N * seg_per_turn
    t = np.linspace(0, N, nseg + 1)
    top = np.stack([R * np.cos(sgn * 2 * np.pi * t), R * np.sin(sgn * 2 * np.pi * t), h0 + S * t], 1)
    bot = top.copy(); bot[:, 2] *= -1
    st = Structure()
    st.add_line([R, 0, -h0], [R, 0, 0], a_l * lam, 2)
    st.add_line([R, 0, 0], [R, 0, h0], a_l * lam, 2)
    st.add_polyline(top, a_l * lam)
    st.add_polyline(bot, a_l * lam)
    st.build()
    b = st.basis_at_point([R, 0, 0])
    sol = solve(st, f, [(b, 1.0)])
    return st, sol


def test_helix(f=435e6):
    import time
    print("  axial-mode helix over infinite PEC ground (image), pitch 12.8 deg:")
    for (N, C_l) in [(6, 1.10), (10, 1.10), (10, 1.00)]:
        S_l = C_l * np.tan(np.radians(12.8))
        t0 = time.time()
        st, sol = helix_over_ground(f, N, C_l, S_l)
        P = prad(sol, nth=91, nph=144)   # full sphere of mirrored structure = 2x upper half power
        Ut, Up, UR, UL = U_components(sol, np.array(1e-6), np.array(0.0))
        # directivity of the real (upper half) problem: D_upper = 4 pi U / (P/2)
        DR = 4 * np.pi * float(UR) / (P / 2)
        DL = 4 * np.pi * float(UL) / (P / 2)
        from ant_helix import kraus_G, king_wong_G, emerson_G_dB
        L_l = N * S_l
        print(f"    N = {N:2d}, C = {C_l:.2f} lam, L = {L_l:.2f} lam: Zin = {sol['Zin'][0]/2:.0f} ohm, "
              f"axial D_RHCP = {10*np.log10(DR):.2f} dBic, D_LHCP = {10*np.log10(max(DL,1e-9)):.1f} dBic; "
              f"Kraus {10*np.log10(kraus_G(C_l,S_l,N)):.1f}, King-Wong {10*np.log10(king_wong_G(C_l,12.8,N)):.1f}, "
              f"Emerson(max over C) {emerson_G_dB(L_l) if L_l>=2 else float('nan'):.1f} dBi  [{time.time()-t0:.0f} s]")


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    print("General thin-wire MoM self-tests")
    test_dipole()
    test_monopole_image()
    test_ground_plane()
    print("  folded dipoles (433 MHz):")
    test_folded()
    print("  small loops (433 MHz, 1 mm wire):")
    test_loop()
    test_helix()
