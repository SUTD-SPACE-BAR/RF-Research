#!/usr/bin/env python3
"""
pcb_via_fence.py — verification script for kb/13-pcb-rf-layout-emc/vias-stitching-fencing.md

  1. Via inductance to ground (Goldfarb-Pucel) for JLCPCB geometries (L1->L2 0.2104 mm, L1->L3 1.275 mm,
     through 1.6 mm), drills 0.2/0.3/0.4 mm; reactance at 433/915/1575/2450/5800 MHz.
  2. Transmission of a parallel-plate (TEM, E parallel to the vias) wave through a single row of vias:
     thin-post-grating shunt reactance  X/eta = (a/lambda) ln(a / (2 pi r))  (Marcuvitz / Collin, leading term).
     INDEPENDENT CHECK: 2-D finite-difference frequency-domain (FDFD) solution of the scalar Helmholtz equation
     (Ez polarisation) in one periodic cell with PMLs, PEC posts staircased on the grid.
  3. Isolation of one and two rows of 0.3 mm vias vs pitch at 915 MHz / 2.45 GHz / 5.8 GHz / 10 GHz in FR-4,
     and what the lambda/10, lambda/20 and "gap < lambda/4" (Southwest Microwave) rules correspond to.
  4. Resonances of un-stitched copper: a coplanar ground strip between two stitching vias (lambda/2 between
     shorts), a floating copper island (lambda/2 open-open), and a ground finger stitched at one end (lambda/4).
  5. Via stub resonance f = c / (4 L_stub sqrt(eps)) for JLC 4- and 6-layer boards; when backdrilling matters.
  6. Thermal resistance of plated vias (20-25 um wall) and via arrays under an exposed pad; epoxy vs copper fill.

Run: python3 tools/verify/pcb_via_fence.py       (about 1-3 min; FDFD)
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

MU0 = 4e-7 * np.pi
C0 = 299_792_458.0
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def L_via_GP(h, r):
    """Goldfarb & Pucel (1991) via-to-ground inductance."""
    return MU0 / (2 * np.pi) * (h * np.log((h + np.sqrt(h**2 + r**2)) / r) + 1.5 * (r - np.sqrt(r**2 + h**2)))


print("=" * 100)
print("1. Via-to-ground inductance for JLCPCB geometries (Goldfarb-Pucel)")
print("=" * 100)
freqs = [433e6, 915e6, 1575.42e6, 2.45e9, 5.8e9]
print("  " + " " * 44 + "".join(f"{f/1e6:>9.0f}M" for f in freqs))
for lab, h in [("L1->L2, JLC04161H-7628 (0.2104 mm)", 0.2104e-3), ("L1->L2, JLC04161H-3313 (0.0994 mm)", 0.0994e-3),
               ("L1->L3, JLC04161H-7628 (1.275 mm)", 1.2754e-3), ("through 1.6 mm (2-layer)", 1.6e-3)]:
    for d in [0.2e-3, 0.3e-3, 0.4e-3]:
        L = L_via_GP(h, d / 2)
        print(f"  {lab:36s} drill {d*1e3:.1f}: {L*1e9:6.3f} nH  X =" + "".join(f"{2*np.pi*f*L:9.2f}" for f in freqs) + " Ohm")
L22 = L_via_GP(0.2104e-3, 0.15e-3)
check("L1->L2 via on JLC-7628 is < 0.03 nH (negligible vs 0402 ESL ~0.3-0.5 nH)", L22 < 0.03e-9, f"({L22*1e12:.1f} pH)")

print("\n" + "=" * 100)
print("2. Single via row as a shunt-inductive grating: formula vs independent FDFD")
print("=" * 100)


def x_grating(a_over_lam, r_over_a):
    """normalised shunt reactance X/eta of a thin-post grating, E parallel to posts, normal incidence."""
    return a_over_lam * np.log(1 / (2 * np.pi * r_over_a))


def T_shunt(x):
    return 2j * x / (1 + 2j * x)


def fdfd_T(a_over_lam, r_over_a, ny=48):
    """Scalar Helmholtz (Ez) in one periodic cell (period a = 1 in y), PML at both x ends, line source,
    PEC post centred at x = 0. Returns complex transmission T = <E>_with / <E>_without at a downstream probe."""
    a = 1.0
    lam = a / a_over_lam
    k = 2 * np.pi / lam
    d = a / ny
    Lpml = max(0.5 * lam, 20 * d)
    Lphys = 1.5 * lam
    nx = int(np.ceil((Lphys + 2 * Lpml) / d))
    x = (np.arange(nx) - nx / 2) * d
    y = (np.arange(ny) + 0.5) * d - a / 2
    xmin, xmax = x[0], x[-1]

    def sx(xx):
        dd = np.maximum(0, np.maximum((xmin + Lpml) - xx, xx - (xmax - Lpml))) / Lpml
        sig = 3 * np.log(1e8) / (2 * k * Lpml)      # dimensionless per unit k
        return 1 - 1j * sig * dd**2 * 1.0

    s_n = sx(x)
    s_h = sx(x + d / 2)       # at i+1/2
    xs = xmin + Lpml + 0.1 * lam           # source plane
    xp = 0.5 * lam                          # probe plane (downstream)
    isrc = int(np.argmin(abs(x - xs)))
    ipr = int(np.argmin(abs(x - xp)))

    def solve(with_post):
        N = nx * ny
        idx = np.arange(N).reshape(nx, ny)
        rows, cols, vals = [], [], []
        diag = np.full((nx, ny), k**2 + 0j)
        # x-derivative (1/s) d/dx (1/s d/dx)
        for i in range(nx):
            cm = 1 / (s_n[i] * s_h[i - 1] * d * d) if i > 0 else 0
            cp = 1 / (s_n[i] * s_h[i] * d * d) if i < nx - 1 else 0
            diag[i, :] -= (cm + cp) if (0 < i < nx - 1) else (cm + cp)
            if i > 0:
                rows.append(idx[i, :]); cols.append(idx[i - 1, :]); vals.append(np.full(ny, cm))
            if i < nx - 1:
                rows.append(idx[i, :]); cols.append(idx[i + 1, :]); vals.append(np.full(ny, cp))
        # y-derivative, periodic
        cy = 1 / (d * d)
        diag -= 2 * cy
        for jj in range(ny):
            rows.append(idx[:, jj]); cols.append(idx[:, (jj + 1) % ny]); vals.append(np.full(nx, cy))
            rows.append(idx[:, jj]); cols.append(idx[:, (jj - 1) % ny]); vals.append(np.full(nx, cy))
        rows.append(idx.ravel()); cols.append(idx.ravel()); vals.append(diag.ravel())
        A = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(N, N)).tolil()
        b = np.zeros(N, complex)
        b[idx[isrc, :]] = 1.0 / d
        if with_post:
            X, Y = np.meshgrid(x, y, indexing="ij")
            pec = (X**2 + Y**2) <= (r_over_a * a) ** 2
            for n in idx[pec]:
                A.rows[n] = [n]
                A.data[n] = [1.0]
                b[n] = 0
        E = spla.spsolve(A.tocsc(), b).reshape(nx, ny)
        return E[ipr, :].mean()

    return solve(True) / solve(False)


def log_term_fdfd(r_over_a, a_over_lam=0.05, ny=128):
    """Effective 'log term' Lambda = x/(a/lambda) of a post grating from the FDFD transmission."""
    Tn = abs(fdfd_T(a_over_lam, r_over_a, ny=ny))
    return Tn / (2 * np.sqrt(1 - Tn**2)) / a_over_lam, Tn


print("  (a) thin posts, a/lambda = 0.1: leading-term formula vs FDFD with mesh refinement")
res = {}
for r_over_a in [0.02, 0.05]:
    Tf = abs(T_shunt(x_grating(0.1, r_over_a)))
    for ny in [64, 128]:
        Tn = abs(fdfd_T(0.1, r_over_a, ny=ny))
        res[(r_over_a, ny)] = 20 * np.log10(Tn) - 20 * np.log10(Tf)
        print(f"    r/a {r_over_a:.2f}, ny {ny:3d} ({r_over_a*ny:4.1f} cells/radius): formula {20*np.log10(Tf):7.2f} dB,"
              f" FDFD {20*np.log10(Tn):7.2f} dB (diff {res[(r_over_a, ny)]:+.2f} dB)")
check("thin posts (r/a = 0.05): FDFD converges to the formula within 1 dB", abs(res[(0.05, 128)]) < 1.0,
      f"({res[(0.05, 128)]:+.2f} dB; staircasing leaves a small residual)")
check("refinement moves FDFD toward the formula", abs(res[(0.05, 128)]) < abs(res[(0.05, 64)]))

print("  (b) thick posts (typical PCB vias: r/a = 0.05-0.15): FDFD 'log term' Lambda vs the thin-post formula")
LAM = {}
for r_over_a in [0.05, 0.075, 0.1, 0.15]:
    Lf, Tn = log_term_fdfd(r_over_a)
    LAM[r_over_a] = Lf
    Tf = abs(T_shunt(x_grating(0.05, r_over_a)))
    print(f"    r/a {r_over_a:5.3f}: FDFD Lambda {Lf:.3f} vs ln(a/2 pi r) {np.log(1/(2*np.pi*r_over_a)):.3f};"
          f" isolation at a = lambda/20: FDFD {-20*np.log10(Tn):5.1f} dB, thin-post formula {-20*np.log10(Tf):5.1f} dB")
check("thin-post formula over-predicts isolation for fat vias (r/a = 0.15) by > 5 dB -> use FDFD values",
      -20 * np.log10(abs(T_shunt(x_grating(0.05, 0.15)))) - (-20 * np.log10(abs(T_shunt(0.05 * LAM[0.15])))) > 5)


def Lambda(r_over_a):
    """log term: FDFD-interpolated for 0.05 <= r/a <= 0.15, thin-post formula (+0.09 FDFD offset) below."""
    ks = sorted(LAM)
    if r_over_a < ks[0]:
        return np.log(1 / (2 * np.pi * r_over_a)) + (LAM[ks[0]] - np.log(1 / (2 * np.pi * ks[0])))
    return float(np.interp(r_over_a, ks, [LAM[k] for k in ks]))


print("\n" + "=" * 100)
print("3. Isolation of via rows (0.3 mm drill -> r = 0.15 mm) between two planes, FR-4 er 4.4")
print("   single row / two rows 1.5 mm apart; Lambda from section 2(b)")
print("=" * 100)
er = 4.4
for f in [915e6, 2.45e9, 5.8e9, 10e9]:
    lam = C0 / f / np.sqrt(er)
    line = []
    for p in [1e-3, 2e-3, 3e-3, 5e-3, 10e-3]:
        x1 = (p / lam) * Lambda(0.15e-3 / p)
        T1 = abs(T_shunt(x1))
        Y = 1 / (1j * x1)
        bl = 2 * np.pi / lam * 1.5e-3
        Msh = np.array([[1, 0], [Y, 1]])
        Mln = np.array([[np.cos(bl), 1j * np.sin(bl)], [1j * np.sin(bl), np.cos(bl)]])
        M = Msh @ Mln @ Msh
        T2 = abs(2 / (M[0, 0] + M[0, 1] + M[1, 0] + M[1, 1]))
        line.append(f"p={p*1e3:4.1f}mm (lam/{lam/p:5.1f}): {-20*np.log10(T1):5.1f}/{-20*np.log10(T2):5.1f} dB")
    print(f"  {f/1e9:5.2f} GHz (lambda_d {lam*1e3:6.1f} mm): " + "; ".join(line))
lam24 = C0 / 2.45e9 / np.sqrt(er)
iso20 = -20 * np.log10(abs(T_shunt((1 / 20) * Lambda(0.15e-3 / (lam24 / 20)))))
iso10 = -20 * np.log10(abs(T_shunt((1 / 10) * Lambda(0.15e-3 / (lam24 / 10)))))
print(f"  single row at 2.45 GHz: lambda/20 pitch ({lam24/20*1e3:.1f} mm) -> {iso20:.1f} dB, lambda/10 -> {iso10:.1f} dB")
check("lambda/20 pitch gives ~15-25 dB per row; lambda/10 gives < 15 dB", 15 < iso20 < 25 and iso10 < 15,
      f"({iso20:.1f}, {iso10:.1f} dB)")
gap = 0.029 * 25.4e-3
fq = C0 / (4 * gap * np.sqrt(3.66))
print(f"  Southwest Microwave criterion: edge-to-edge gap 0.029 in = {gap*1e3:.3f} mm is lambda/4 at {fq/1e9:.1f} GHz in er 3.66"
      f" (their quoted 53 GHz). NB the summary's '0.020 in vias on 0.040 in centres' would give a 0.020 in gap -"
      f" internally inconsistent; only the gap criterion is used here.")
check("SWM gap/lambda-4 arithmetic reproduces ~53 GHz", abs(fq / 1e9 - 53) < 2, f"({fq/1e9:.1f} GHz)")

print("\n" + "=" * 100)
print("4. Resonances of un-stitched copper (eeff ~ 2.7 for top-layer copper over FR-4 plane, ~er between planes)")
print("=" * 100)
ee = 2.7
for L in [5e-3, 10e-3, 20e-3, 30e-3, 50e-3]:
    f_half = C0 / (2 * L * np.sqrt(ee))
    f_quarter = C0 / (4 * L * np.sqrt(ee))
    print(f"  {L*1e3:4.0f} mm: lambda/2 (shorted-shorted strip between vias, or open-open floating island) {f_half/1e9:6.2f} GHz;"
          f" lambda/4 (finger with one via) {f_quarter/1e9:6.2f} GHz")
f10 = C0 / (4 * 10e-3 * np.sqrt(ee))
check("a 10 mm GND finger with one via at its root resonates near 4.6 GHz (5.8 GHz band hazard)", 4e9 < f10 < 5e9,
      f"({f10/1e9:.2f} GHz)")
for f in [915e6, 2.45e9, 5.8e9]:
    lam = C0 / f / np.sqrt(ee)
    print(f"  stitching pitch for {f/1e9:.3f} GHz (top copper): lambda/10 = {lam/10*1e3:5.1f} mm, lambda/20 = {lam/20*1e3:5.1f} mm;"
          f"  between planes (er 4.4): lambda/20 = {C0/f/np.sqrt(4.4)/20*1e3:5.1f} mm")

print("\n" + "=" * 100)
print("5. Via stubs (through via used L1->L2): quarter-wave stub resonance")
print("=" * 100)
for lab, stub in [("JLC 4L 1.6 mm, L1->L2 via, stub to L4", 1.6e-3 - 0.035e-3 - 0.2104e-3),
                  ("JLC 4L 1.6 mm, L1->L3 via, stub to L4", 0.2104e-3 + 0.035e-3),
                  ("JLC 6L 1.6 mm, L1->L2 via, stub", 1.6e-3 - 0.13e-3), ("3.2 mm backplane, L1->L2", 3.1e-3)]:
    fs = C0 / (4 * stub * np.sqrt(4.4))
    print(f"  {lab:40s}: stub {stub*1e3:.2f} mm -> f_stub ~ {fs/1e9:6.1f} GHz (keep operating f < f_stub/3)")
fs16 = C0 / (4 * 1.35e-3 * np.sqrt(4.4))
check("a 1.35 mm stub resonates > 20 GHz: backdrilling irrelevant below ~6 GHz on 1.6 mm boards", fs16 > 20e9,
      f"({fs16/1e9:.1f} GHz)")

print("\n" + "=" * 100)
print("6. Thermal resistance of plated vias (k_Cu 385 W/mK) and arrays")
print("=" * 100)
kcu = 385.0
for drill in [0.2e-3, 0.3e-3, 0.4e-3]:
    for tpl in [20e-6, 25e-6]:
        A = np.pi * ((drill / 2) ** 2 - (drill / 2 - tpl) ** 2)
        R = 1.6e-3 / (kcu * A)
        Rfill = 1.6e-3 / (kcu * A + 0.3 * np.pi * (drill / 2 - tpl) ** 2)       # epoxy fill k ~0.3
        Rcu = 1.6e-3 / (kcu * np.pi * (drill / 2) ** 2)                          # solid copper fill
        print(f"  drill {drill*1e3:.1f} mm, wall {tpl*1e6:.0f} um, 1.6 mm long: {R:6.1f} K/W"
              f" (epoxy-filled {Rfill:6.1f}; if copper-filled {Rcu:5.1f})")
A = np.pi * (0.15e-3**2 - 0.13e-3**2)
Rv = 1.6e-3 / (kcu * A)
for n in [1, 4, 9, 16, 25]:
    print(f"  {n:2d} x 0.3 mm vias in parallel (20 um wall): {Rv/n:6.1f} K/W  (ignores spreading in the planes)")
check("one 0.3 mm/20 um via through 1.6 mm is ~200-250 K/W; 9 vias ~25 K/W", 180 < Rv < 260 and Rv / 9 < 30,
      f"({Rv:.0f} K/W, 9 -> {Rv/9:.1f})")
# through a 0.21 mm prepreg only (to L2): short via
Rs = 0.21e-3 / (kcu * A)
print(f"  L1->L2 only (0.21 mm): {Rs:.1f} K/W per via — heat reaches the L2 plane easily; spreading then dominates")

print("\nALL CHECKS PASSED" if ok_all else "\nSOME CHECKS FAILED")
