#!/usr/bin/env python3
"""
ant_mom_wire.py -- a small, self-contained thin-wire Method-of-Moments solver for
arrays of PARALLEL straight wires (dipoles, Yagi-Uda arrays, collinear/stacked dipoles).

Purpose: independent numerical verification for kb/08-antennas (dipole resonant length vs
wire thickness, finite-radius dipole impedance, Yagi gain / F/B / feed impedance) without
needing NEC installed. It is NOT a replacement for NEC-2/4 or openEMS: it only handles
z-directed straight wires in free space, perfectly conducting, delta-gap feeds.

Formulation (own implementation, standard textbook method; see Balanis 4th ed. ch. 8,
Harrington "Field Computation by Moment Methods", Gibson "The Method of Moments in
Electromagnetics"):
  * Mixed-potential EFIE, Galerkin testing, triangle (piecewise-linear) basis functions on
    interior nodes (current forced to zero at wire ends).
      Z_mn = j w mu  <T_m, G * T_n>  +  (1 / (j w eps)) <T_m', G * T_n'>
  * Reduced (thin-wire) kernel G = exp(-jkR)/(4 pi R), R = sqrt((z-z')^2 + rho^2), with
    rho = a on the same wire and rho = axis-to-axis distance between different wires.
  * The 1/R part of each inner integral is done analytically (asinh), the smooth remainder
    (exp(-jkR)-1)/R by Gauss-Legendre; outer integrals by (sub-divided) Gauss-Legendre.
  * Delta-gap source at a node: V_m = V at the feed node.
  * Far field of z-directed currents: U = eta k^2 sin^2(theta) |N_z|^2 / (32 pi^2).
    Directivity from pattern integration; for PEC wires P_rad must equal P_in = 0.5 Re(V I*),
    which is printed as a self-consistency check (the "average gain test").

Run:  python3 tools/verify/ant_mom_wire.py      (self-test: dipoles)
Import: from ant_mom_wire import Wire, solve, far_field_U, directivity
"""
import numpy as np

C0 = 299792458.0
MU0 = 4e-7 * np.pi
EPS0 = 1.0 / (MU0 * C0 ** 2)
ETA0 = np.sqrt(MU0 / EPS0)

_gx8, _gw8 = np.polynomial.legendre.leggauss(8)
_trapz = getattr(np, "trapezoid", None) or np.trapz


class Wire:
    """Straight z-directed wire at (x, y) from z0 to z1, radius a, nseg segments (even
    number recommended so that a node sits at the centre for a centre feed)."""

    def __init__(self, x, y, z0, z1, a, nseg):
        self.x, self.y, self.z0, self.z1, self.a, self.nseg = x, y, z0, z1, a, nseg
        self.nodes = np.linspace(z0, z1, nseg + 1)


def _segments(wires):
    segs = []  # (wire index, za, zb)
    for wi, w in enumerate(wires):
        for j in range(w.nseg):
            segs.append((wi, w.nodes[j], w.nodes[j + 1]))
    return segs


def _pair_integrals_vec(k, za, zb, zc, zd, rho, nsub):
    """Vectorised over pairs. Outer segment [za,zb] (z), inner [zc,zd] (z'), axis offset rho.
    Returns J (P,2,2) with J[:,a,b] = int int phi_a(z) psi_b(z') G dz' dz and J0 (P,) = int int G.
    phi_0/psi_0 = falling shape (1 at left node), phi_1/psi_1 = rising shape."""
    P = za.shape[0]
    Dz = (zb - za)[:, None]
    Dp = (zd - zc)[:, None]
    t = np.linspace(0, 1, nsub + 1)
    left = za[:, None] + (zb - za)[:, None] * t[None, :-1]
    h = (zb - za)[:, None] / nsub
    zo = (left[:, :, None] + h[:, :, None] / 2 * (1 + _gx8[None, None, :])).reshape(P, -1)
    wo = np.broadcast_to((h / 2)[:, :, None] * _gw8[None, None, :], (P, nsub, 8)).reshape(P, -1)
    r = rho[:, None]
    uc = zc[:, None] - zo
    ud = zd[:, None] - zo
    Rc = np.sqrt(uc ** 2 + r ** 2)
    Rd = np.sqrt(ud ** 2 + r ** 2)
    ash = np.arcsinh(ud / r) - np.arcsinh(uc / r)
    S0 = ash / (4 * np.pi)
    S1 = ((Rd - Rc) + (zo - zc[:, None]) * ash) / (4 * np.pi) / Dp
    zi = (zc + zd)[:, None] / 2 + (zd - zc)[:, None] / 2 * _gx8[None, :]      # (P,8)
    wi = (zd - zc)[:, None] / 2 * _gw8[None, :]
    R = np.sqrt((zi[:, None, :] - zo[:, :, None]) ** 2 + r[:, :, None] ** 2)   # (P,no,8)
    with np.errstate(invalid="ignore", divide="ignore"):
        kern = np.where(R > 1e-15, (np.exp(-1j * k * R) - 1.0) / (4 * np.pi * R), -1j * k / (4 * np.pi))
    T0 = np.einsum("pij,pj->pi", kern, wi)
    T1 = np.einsum("pij,pj->pi", kern, wi * (zi - zc[:, None]) / Dp)
    A_rise = S1 + T1
    A_tot = S0 + T0
    A_fall = A_tot - A_rise
    phi1 = (zo - za[:, None]) / Dz
    phi0 = 1 - phi1
    J = np.empty((P, 2, 2), dtype=complex)
    J[:, 0, 0] = np.sum(wo * phi0 * A_fall, axis=1)
    J[:, 0, 1] = np.sum(wo * phi0 * A_rise, axis=1)
    J[:, 1, 0] = np.sum(wo * phi1 * A_fall, axis=1)
    J[:, 1, 1] = np.sum(wo * phi1 * A_rise, axis=1)
    J0 = np.sum(wo * A_tot, axis=1)
    return J, J0


def solve(wires, feeds, freq, chunk=20000):
    """wires: list of Wire. feeds: list of (wire_index, node_index, voltage).
    Returns dict with basis bookkeeping, currents I (at interior nodes), Zin per feed."""
    k = 2 * np.pi * freq / C0
    w = 2 * np.pi * freq
    segs = _segments(wires)
    ns = len(segs)
    sw = np.array([s[0] for s in segs])
    sa = np.array([s[1] for s in segs])
    sb = np.array([s[2] for s in segs])
    wx = np.array([wr.x for wr in wires])
    wy = np.array([wr.y for wr in wires])
    wa = np.array([wr.a for wr in wires])
    S, T = np.meshgrid(np.arange(ns), np.arange(ns), indexing="ij")
    S = S.ravel(); T = T.ravel()
    same = sw[S] == sw[T]
    rho = np.where(same, wa[sw[S]], np.hypot(wx[sw[S]] - wx[sw[T]], wy[sw[S]] - wy[sw[T]]))
    dzs = sb[S] - sa[S]
    near = (same & (np.abs((sa[S] + sb[S]) / 2 - (sa[T] + sb[T]) / 2) < 2.5 * dzs)) | (~same & (rho < 0.5 * dzs))
    Jm = np.empty((ns * ns, 2, 2), dtype=complex)
    J0m = np.empty(ns * ns, dtype=complex)
    for mask, nsub in ((near, 6), (~near, 1)):
        idx = np.where(mask)[0]
        for c in range(0, len(idx), chunk):
            ii = idx[c:c + chunk]
            J, J0 = _pair_integrals_vec(k, sa[S[ii]], sb[S[ii]], sa[T[ii]], sb[T[ii]], rho[ii], nsub)
            Jm[ii] = J
            J0m[ii] = J0
    Jm = Jm.reshape(ns, ns, 2, 2)
    J0m = J0m.reshape(ns, ns)
    basis, sr, sf, dr, df = [], [], [], [], []
    off = 0
    for wi, wr in enumerate(wires):
        for j in range(1, wr.nseg):
            basis.append((wi, j))
            sr.append(off + j - 1); sf.append(off + j)
            dr.append(wr.nodes[j] - wr.nodes[j - 1]); df.append(wr.nodes[j + 1] - wr.nodes[j])
        off += wr.nseg
    sr = np.array(sr); sf = np.array(sf); dr = np.array(dr); df = np.array(df)
    parts = ((sr, 1, 1.0 / dr), (sf, 0, -1.0 / df))
    nb = len(basis)
    Z = np.zeros((nb, nb), dtype=complex)
    for (sm, am, dm) in parts:
        for (sn, an, dn) in parts:
            Z += 1j * w * MU0 * Jm[np.ix_(sm, sn)][:, :, am, an] \
                 + np.outer(dm, dn) * J0m[np.ix_(sm, sn)] / (1j * w * EPS0)
    V = np.zeros(nb, dtype=complex)
    feed_idx = []
    for (wi, j, v) in feeds:
        idx = basis.index((wi, j))
        V[idx] = v
        feed_idx.append((idx, v))
    I = np.linalg.solve(Z, V)
    Zin = [v / I[idx] for (idx, v) in feed_idx]
    Pin = sum(0.5 * np.real(v * np.conj(I[idx])) for (idx, v) in feed_idx)
    return dict(k=k, basis=basis, I=I, Zin=Zin, Pin=Pin, wires=wires, Zmat=Z)


def far_field_U(sol, theta, phi):
    """Radiation intensity U(theta, phi) [W/sr] for arrays theta, phi (broadcastable)."""
    k = sol["k"]
    wires = sol["wires"]
    theta = np.asarray(theta, dtype=float)
    phi = np.asarray(phi, dtype=float)
    th, ph = np.broadcast_arrays(theta, phi)
    Nz = np.zeros(th.shape, dtype=complex)
    st, ct = np.sin(th), np.cos(th)
    for (wi, j), In in zip(sol["basis"], sol["I"]):
        wr = wires[wi]
        z = wr.nodes
        phase_xy = np.exp(1j * k * st * (wr.x * np.cos(ph) + wr.y * np.sin(ph)))
        # integral of triangle basis times exp(jk z' cos th): Gauss on both halves
        for (zl, zr, rising) in ((z[j - 1], z[j], True), (z[j], z[j + 1], False)):
            zq = (zl + zr) / 2 + (zr - zl) / 2 * _gx8
            wq = (zr - zl) / 2 * _gw8
            tri = (zq - zl) / (zr - zl) if rising else (zr - zq) / (zr - zl)
            Nz += In * phase_xy * np.tensordot(np.exp(1j * k * ct[..., None] * zq), wq * tri, axes=([-1], [0]))
    return ETA0 * k ** 2 * st ** 2 * np.abs(Nz) ** 2 / (32 * np.pi ** 2)


def directivity(sol, theta0=np.pi / 2, phi0=0.0, nth=181, nph=360):
    th = np.linspace(0, np.pi, nth)
    ph = np.linspace(0, 2 * np.pi, nph, endpoint=False)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    U = far_field_U(sol, TH, PH)
    # periodic rectangle rule in phi (exact for trig polynomials), trapezoid in theta
    Prad = _trapz(np.sum(U, axis=1) * (ph[1] - ph[0]) * np.sin(th), th)
    U0 = far_field_U(sol, np.array(theta0), np.array(phi0))
    return 4 * np.pi * float(U0) / Prad, Prad


def dipole(freq, length, a, nseg=40):
    wr = Wire(0, 0, -length / 2, length / 2, a, nseg)
    return solve([wr], [(0, nseg // 2, 1.0)], freq)


def resonant_length(freq, a, lo=0.42, hi=0.5, nseg=40):
    """Length (in wavelengths) at which the centre-fed dipole reactance crosses zero."""
    lam = C0 / freq
    from scipy.optimize import brentq
    f = lambda L: np.imag(dipole(freq, L * lam, a, nseg)["Zin"][0])
    return brentq(f, lo, hi, xtol=1e-5)


if __name__ == "__main__":
    f = 433e6
    lam = C0 / f
    print("Thin-wire MoM self-test (parallel-wire Pocklington/MPIE, Galerkin triangles)")
    print(f"f = {f/1e6} MHz, lambda = {lam*1000:.1f} mm")
    # 1. convergence of a half-wave dipole impedance with segmentation
    a = 1e-4 * lam
    for n in [20, 40, 60]:
        s = dipole(f, 0.5 * lam, a, n)
        print(f"  L = 0.5 lambda, a = 1e-4 lambda, N = {n:3d}:  Zin = {s['Zin'][0]:.2f} ohm")
    s = dipole(f, 0.5 * lam, a, 40)
    D, Prad = directivity(s)
    print(f"  directivity = {D:.3f} ({10*np.log10(D):.2f} dBi);  Prad/Pin = {Prad/s['Pin']:.4f} (should be 1)")
    # 2. resonant length vs thickness
    print("\nResonant (X=0) length of a centre-fed dipole vs wire radius:")
    for a_l in [1e-5, 1e-4, 5e-4, 1e-3, 2e-3, 5e-3]:
        Lr = resonant_length(f, a_l * lam)
        s = dipole(f, Lr * lam, a_l * lam, 40)
        print(f"  a/lambda = {a_l:7.0e} (lambda/d = {1/(2*a_l):7.0f}): L_res = {Lr:.4f} lambda "
              f"(K = {Lr/0.5:.3f}),  R_res = {s['Zin'][0].real:.1f} ohm")
    # 3. practical: 433 MHz with 2 mm wire, 915 MHz with 1.5 mm wire
    for (ff, d) in [(433e6, 2e-3), (915e6, 1.5e-3), (433e6, 6e-3)]:
        Lr = resonant_length(ff, d / 2)
        print(f"  {ff/1e6:.0f} MHz, d = {d*1000:.1f} mm: resonant dipole = {Lr*C0/ff*1000:.1f} mm total "
              f"({Lr:.4f} lambda)")
