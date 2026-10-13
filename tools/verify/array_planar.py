#!/usr/bin/env python3
"""
array_planar.py — verification for kb/12-phased-arrays/planar-arrays-element-pattern-coupling.md

Part A (analytic/numeric array factor):
  A1. Grating-lobe-free scan cone for square vs equilateral-triangular lattices; element-count saving
      (expected 1 - sqrt(3)/2 = 13.4 %), checked by brute-force 2-D array-factor search.
  A2. Directivity of an 8x8 planar array at lambda/2: isotropic elements vs cos(theta) element vs Hannan
      4*pi*A/lambda^2 (A = N dx dy), and vs scan angle.
  A3. Hannan asymptote for embedded element efficiency e = pi dx dy / lambda^2 (Kildal 2015 eq. 2).
Part B (full-wave coupling with the thin-wire MoM of tools/verify/ant_mom_wire.py):
  B1. N-port admittance/impedance/S matrices of an 8-element H-plane array of resonant lambda/2 dipoles at
      d = lambda/2, free space and over a PEC reflector (image theory).
  B2. Active reflection coefficient / active impedance vs scan angle (centre and edge element).
  B3. Embedded element patterns (one port driven, all others terminated in Z0): centre vs edge element,
      embedded element efficiency 1 - sum_i |S_im|^2 vs radiated-power integration.
  B4. Exact array pattern = superposition of embedded patterns; compare with isolated-element pattern x AF.
  B5. Realized gain vs scan (all ports driven) vs cos(theta) and vs mismatch factor.
Part C (scan blindness estimate for printed arrays):
  C1. TM0 surface-wave propagation constant of a grounded dielectric slab (FR-4 1.6 mm, RO4350B 0.762 mm,
      3.2 mm FR-4) and the Floquet phase-matching blindness angle sin(theta_b) = lambda/d - beta_sw/k0
      (E-plane scan), vs the grating-lobe onset sin(theta_GL) = lambda/d - 1.
"""
import os
import sys
import numpy as np
from scipy.optimize import brentq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ant_mom_wire as mw  # noqa: E402

C0 = 299792458.0
rng = np.random.default_rng(3)

# ---------------------------------------------------------------- Part A
print("=" * 78)
print("A1. Grating-lobe-free scan cone: square vs equilateral triangular lattice")
for thm in (30, 45, 60, 70):
    s = np.sin(np.radians(thm))
    d_sq = 1 / (1 + s)
    b_tri = 2 / (np.sqrt(3) * (1 + s))  # nearest-neighbour spacing
    A_sq = d_sq ** 2
    A_tri = np.sqrt(3) / 2 * b_tri ** 2
    print(f"  cone ±{thm}°: square d ≤ {d_sq:.3f}λ (cell {A_sq:.3f}λ²); triangular b ≤ {b_tri:.3f}λ (cell {A_tri:.3f}λ²); "
          f"elements saved {100*(1-A_sq/A_tri):.1f}%")


def gl_free_cone_bruteforce(lattice, spacing):
    """Largest cone half-angle such that no reciprocal-lattice replica of any beam inside the cone falls in
    the visible circle. Reciprocal lattice points (u,v) = m*b1 + n*b2."""
    if lattice == "square":
        b1 = np.array([1 / spacing, 0]); b2 = np.array([0, 1 / spacing])
    else:  # equilateral triangular with nearest-neighbour spacing 'spacing' (rows offset)
        a1 = np.array([spacing, 0]); a2 = np.array([spacing / 2, spacing * np.sqrt(3) / 2])
        A = np.array([a1, a2]).T
        B = np.linalg.inv(A).T  # reciprocal (without 2pi) so that a_i . b_j = delta_ij
        b1, b2 = B[:, 0], B[:, 1]
    pts = [m * b1 + n * b2 for m in range(-3, 4) for n in range(-3, 4) if (m, n) != (0, 0)]
    dmin = min(np.linalg.norm(p) for p in pts)
    # beam at radius s in any direction; replica at beam + p; need |beam + p| > 1 for all -> s <= dmin - 1
    s = dmin - 1
    return np.degrees(np.arcsin(min(1, s))) if s > 0 else 0.0


for thm in (30, 45, 60):
    s = np.sin(np.radians(thm))
    print(f"    brute force: square d={1/(1+s):.3f} -> cone {gl_free_cone_bruteforce('square', 1/(1+s)):.1f}°; "
          f"triangular b={2/(np.sqrt(3)*(1+s)):.3f} -> cone {gl_free_cone_bruteforce('tri', 2/(np.sqrt(3)*(1+s))):.1f}°")

print("=" * 78)
print("A2. 8x8 planar array directivity (numeric sphere integration)")


def planar_D(xy, w, el=None, th0=0.0, ph0=0.0, nth=361, nph=360):
    th = np.linspace(0, np.pi, nth)
    ph = np.linspace(0, 2 * np.pi, nph, endpoint=False)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    u = np.sin(TH) * np.cos(PH); v = np.sin(TH) * np.sin(PH)
    k = 2 * np.pi
    AF = np.exp(1j * k * (u[..., None] * xy[:, 0] + v[..., None] * xy[:, 1])) @ w
    U = np.abs(AF) ** 2
    if el is not None:
        U = U * el(TH)
    wts = np.ones(nth); wts[0] = wts[-1] = 0.5
    P = np.sum(U * np.sin(TH) * wts[:, None]) * (th[1] - th[0]) * (ph[1] - ph[0])
    u0 = np.sin(th0) * np.cos(ph0); v0 = np.sin(th0) * np.sin(ph0)
    AF0 = np.exp(1j * k * (u0 * xy[:, 0] + v0 * xy[:, 1])) @ w
    U0 = np.abs(AF0) ** 2 * (el(np.array(th0)) if el is not None else 1)
    return 4 * np.pi * U0 / P


M = 8
g = np.arange(M) * 0.5
X, Y = np.meshgrid(g, g)
xy = np.c_[X.ravel(), Y.ravel()]
Ncell = M * M
A = Ncell * 0.25
cosel = lambda TH: np.where(TH < np.pi / 2, np.cos(TH), 0.0)
for th0d in (0, 30, 45, 60):
    th0 = np.radians(th0d)
    w = np.exp(-1j * 2 * np.pi * np.sin(th0) * xy[:, 0])
    Di = planar_D(xy, w, None, th0)
    Dc = planar_D(xy, w, cosel, th0)
    print(f"  θ0={th0d:2d}° (E/x-plane): isotropic D={10*np.log10(Di):5.2f} dBi, cosθ element D={10*np.log10(Dc):5.2f} dBi, "
          f"Hannan 4πA cosθ0/λ² = {10*np.log10(4*np.pi*A*np.cos(th0)):5.2f} dBi, N·D_el(θ0)=10log(64·4cosθ0) {10*np.log10(64*4*np.cos(th0)):5.2f}")

print("=" * 78)
print("A3. Hannan asymptote e_emb = π dx dy/λ² (valid for dx,dy < 1/√π λ = 0.564λ)")
for dx in (0.2, 0.3, 0.4, 0.5, 0.56):
    e = np.pi * dx * dx
    print(f"  dx=dy={dx}λ: e_emb ≤ {e:.3f} ({10*np.log10(e):6.2f} dB)")

# ---------------------------------------------------------------- Part B
print("=" * 78)
print("B. MoM: 8 resonant λ/2 dipoles side by side (H-plane array), d = λ/2")
f = 1.0e9
lam = C0 / f
a = lam * 1e-3  # wire radius 0.001 λ
nseg = 20
Lres = mw.resonant_length(f, a, nseg=nseg) * lam
print(f"  resonant length {Lres/lam:.4f} λ")


def build(N, d_l, reflector_h=None):
    wires = []
    for i in range(N):
        wires.append(mw.Wire(i * d_l * lam, 0.0, -Lres / 2, Lres / 2, a, nseg))
    if reflector_h is not None:
        for i in range(N):
            wires.append(mw.Wire(i * d_l * lam, -2 * reflector_h * lam, -Lres / 2, Lres / 2, a, nseg))
    return wires


def port_solutions(N, d_l, reflector_h=None):
    wires = build(N, d_l, reflector_h)
    sols = []
    Y = np.zeros((N, N), dtype=complex)
    for j in range(N):
        feeds = [(j, nseg // 2, 1.0)]
        if reflector_h is not None:
            feeds.append((N + j, nseg // 2, -1.0))  # image driven antiphase
        sol = mw.solve(wires, feeds, f)
        sols.append(sol)
        for i in range(N):
            idx = sol["basis"].index((i, nseg // 2))
            Y[i, j] = sol["I"][idx]
    return wires, sols, Y


def combine(sols, V):
    """Superpose short-circuit solutions with port voltages V -> solution dict usable by far_field_U."""
    base = dict(sols[0])
    base["I"] = sum(v * s["I"] for v, s in zip(V, sols))
    return base


def far_U(sol, th, ph):
    return mw.far_field_U(sol, th, ph)


def prad(sol, half=False, nth=91, nph=180):
    th = np.linspace(0, np.pi, nth)
    ph = np.linspace(0, 2 * np.pi, nph, endpoint=False)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    U = far_U(sol, TH, PH)
    if half:
        U = U * (np.sin(PH) > 0)  # y > 0 half-space (reflector case, image fields are fictitious for y<-h)
    wts = np.ones(nth); wts[0] = wts[-1] = 0.5
    return np.sum(U * np.sin(TH) * wts[:, None]) * (th[1] - th[0]) * (ph[1] - ph[0])


for label, refl in (("free space", None), ("over PEC reflector at λ/4", 0.25)):
    N = 8
    wires, sols, Y = port_solutions(N, 0.5, refl)
    Z = np.linalg.inv(Y)
    Ziso = np.linalg.inv(port_solutions(1, 0.5, refl)[2])[0, 0]
    Z0 = 50.0 if refl is None else 50.0
    # reference impedance: use real part of isolated element impedance (matched isolated element)
    Z0 = np.real(Ziso)
    S = (Z - Z0 * np.eye(N)) @ np.linalg.inv(Z + Z0 * np.eye(N))
    print(f"  --- {label}: isolated element Zin = {Ziso.real:.1f}{Ziso.imag:+.1f}j Ω ; Z0 = {Z0:.1f} Ω")
    print(f"      Z12 = {Z[3,4].real:.1f}{Z[3,4].imag:+.1f}j Ω, |S21| (neighbours) = {20*np.log10(abs(S[3,4])):.1f} dB, |S31| = {20*np.log10(abs(S[3,5])):.1f} dB")
    # B2 active reflection vs scan
    # scanning in the x-y plane (H-plane of z-dipoles); broadside direction is +y (phi = 90 deg)
    # direction phi measured from x axis: u_x = cos(phi); broadside phi=90. Scan angle from broadside: th_s = 90 - phi.
    x = np.arange(N) * 0.5
    print("      scan(°)  Γa centre   Γa edge   Za centre (Ω)        realized-gain(scan) - G(broadside)   cos(θ)")
    GR = {}
    for ths in (0, 15, 30, 45, 60, 75):
        us = np.sin(np.radians(ths))
        a_n = np.exp(-1j * 2 * np.pi * x * us)
        Ga = (S @ a_n) / a_n
        Za = Z0 * (1 + Ga) / (1 - Ga)
        # all ports driven by sources Vs=a_n with internal Z0: V = (I + Z0 Y)^-1 Vs
        V = np.linalg.solve(np.eye(N) + Z0 * Y, a_n)
        sol = combine(sols, V)
        phs = np.radians(90 - ths)
        U = far_U(sol, np.array(np.pi / 2), np.array(phs))
        Pavail = np.sum(np.abs(a_n) ** 2) / (8 * Z0)
        GR[ths] = 4 * np.pi * float(U) / Pavail
        print(f"      {ths:5d}   {abs(Ga[3]):.3f}      {abs(Ga[0]):.3f}    {Za[3].real:6.1f}{Za[3].imag:+6.1f}j        "
              f"{10*np.log10(GR[ths]/GR.get(0,GR[ths])):+6.2f} dB                        {10*np.log10(np.cos(np.radians(ths))):+6.2f} dB")
    print(f"      broadside realized gain {10*np.log10(GR[0]):.2f} dBi")
    # B3 embedded element patterns & efficiency
    for m, name in ((3, "centre (#4)"), (0, "edge (#1)")):
        Vs = np.zeros(N, dtype=complex); Vs[m] = 1.0
        V = np.linalg.solve(np.eye(N) + Z0 * Y, Vs)
        sol = combine(sols, V)
        Pav = 1 / (8 * Z0)
        Pr = prad(sol, half=refl is not None)
        e_s = 1 - np.sum(np.abs(S[:, m]) ** 2)
        phis = np.radians(np.array([90, 60, 30, 0.1]))
        Ue = far_U(sol, np.full(4, np.pi / 2), phis)
        Ge = 4 * np.pi * Ue / Pav
        print(f"      embedded {name}: e_emb from S = {e_s:.3f}, from pattern integral = {Pr/Pav:.3f}; "
              f"embedded realized gain at scan 0/30/60/90° = " + ", ".join(f"{10*np.log10(max(g_,1e-12)):.2f}" for g_ in Ge) + " dBi")
    # B4 superposition vs pattern multiplication at 30 deg scan
    ths = 30
    us = np.sin(np.radians(ths))
    a_n = np.exp(-1j * 2 * np.pi * x * us)
    V = np.linalg.solve(np.eye(N) + Z0 * Y, a_n)
    sol = combine(sols, V)
    phs = np.radians(np.linspace(0.5, 179.5, 359))
    Uarr = far_U(sol, np.full(phs.shape, np.pi / 2), phs)
    # isolated element pattern x AF
    wi, si, Yi = port_solutions(1, 0.5, refl)
    sol1 = combine(si, [1.0])
    U1 = far_U(sol1, np.full(phs.shape, np.pi / 2), phs)
    uu = np.cos(phs)  # direction cosine along x
    AFv = np.exp(1j * 2 * np.pi * np.outer(uu, x)) @ a_n
    Upm = U1 * np.abs(AFv) ** 2
    A_db = 10 * np.log10(Uarr / Uarr.max()); P_db = 10 * np.log10(Upm / Upm.max())
    mask = (A_db > -30)
    print(f"      30° scan: peak direction MoM {90-np.degrees(phs[np.argmax(Uarr)]):.1f}° vs pattern-mult {90-np.degrees(phs[np.argmax(Upm)]):.1f}°; "
          f"max sidelobe MoM {np.sort(A_db[np.r_[False, (A_db[1:-1]>A_db[:-2])&(A_db[1:-1]>A_db[2:]), False]])[-2]:.1f} dB vs pattern-mult "
          f"{np.sort(P_db[np.r_[False, (P_db[1:-1]>P_db[:-2])&(P_db[1:-1]>P_db[2:]), False]])[-2]:.1f} dB")

# ---------------------------------------------------------------- Part C
print("=" * 78)
print("C1. Surface-wave (TM0) scan-blindness estimate for printed arrays (E-plane scan)")


def tm0_beta(er, h, f):
    k0 = 2 * np.pi * f / C0
    # TM even mode of grounded slab: kc tan(kc h) = er * alpha, kc^2 = er k0^2 - beta^2, alpha^2 = beta^2 - k0^2
    def F(beta):
        kc = np.sqrt(er * k0 ** 2 - beta ** 2)
        al = np.sqrt(beta ** 2 - k0 ** 2)
        return kc * np.tan(kc * h) - er * al
    lo = k0 * (1 + 1e-12)
    hi = min(np.sqrt(er) * k0 * (1 - 1e-12), np.sqrt(k0 ** 2 * er - (np.pi / (2 * h)) ** 2 * 0.999999) if (np.pi / (2 * h)) ** 2 < er * k0 ** 2 else np.sqrt(er) * k0 * (1 - 1e-12))
    return brentq(F, lo, hi) / k0


for (name, er, h) in (("FR-4 1.6 mm (εr 4.4)", 4.4, 1.6e-3), ("FR-4 3.2 mm", 4.4, 3.2e-3), ("RO4350B 0.762 mm (εr 3.66)", 3.66, 0.762e-3),
                      ("RO4003C 1.524 mm (εr 3.55)", 3.55, 1.524e-3), ("εr 10.2, 1.27 mm", 10.2, 1.27e-3)):
    for f in (2.45e9, 5.8e9, 10.25e9):
        bk = tm0_beta(er, h, f)
        row = []
        for dl in (0.5, 0.55, 0.6):
            sb = 1 / dl - bk
            sg = 1 / dl - 1
            tb = np.degrees(np.arcsin(sb)) if sb < 1 else 90.0
            tg = np.degrees(np.arcsin(sg)) if sg < 1 else 90.0
            row.append(f"d={dl}λ: blind≈{tb:5.1f}° (GL {tg:5.1f}°)")
        print(f"  {name:28s} {f/1e9:5.2f} GHz: h/λ0={h*f/C0:.4f} β_TM0/k0={bk:.4f} | " + " | ".join(row))
print("done")
