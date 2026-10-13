#!/usr/bin/env python3
"""
em_inductance.py — checks for kb/02-electromagnetics/inductance-capacitance-from-fields.md

1. TEM line L', C' closed forms (coax, two-wire, wire over ground, parallel plate) and L'C' = mu eps.
2. Partial inductance (Rosa/Grover/Ruehli) of straight round wires and mutual partial inductance of
   parallel filaments; loop inductance = sum of partials; long-loop limit -> two-wire L'.
3. Independent check: Neumann double integral for a rectangular loop of round wire (numeric).
4. Via inductance: Rosa-type partial ln(4h/d) - 1 vs the commonly quoted Johnson & Graham ln(4h/d) + 1.
5. 2-D finite-difference Laplace solver for a zero-thickness strip over ground (air and on FR-4):
   C per length, fringing factor vs parallel-plate, Z0 and eps_eff vs Hammerstad-Jensen formulas.
6. Mutual inductance of two coaxial circular loops: elliptic-integral formula vs numeric Neumann.
7. Isolated sphere capacitance, and energy-definition check for coax (W_m, W_e).
"""
import numpy as np
from scipy import integrate, special, sparse
from scipy.sparse.linalg import spsolve

c = 299_792_458.0
mu0 = 1.25663706127e-6
eps0 = 1 / (mu0 * c**2)
eta0 = mu0 * c

print("=== 1. TEM line parameters ===")
def coax(a, b, er=1.0):
    return mu0 / (2 * np.pi) * np.log(b / a), 2 * np.pi * eps0 * er / np.log(b / a)
def two_wire(a, D, er=1.0):
    x = np.arccosh(D / (2 * a))
    return mu0 / np.pi * x, np.pi * eps0 * er / x
def wire_over_ground(a, h, er=1.0):
    x = np.arccosh(h / a)
    return mu0 / (2 * np.pi) * x, 2 * np.pi * eps0 * er / x
def parallel_plate(w, d, er=1.0):
    return mu0 * d / w, eps0 * er * w / d
cases = {"coax RG-58-like a=0.45 b=1.47 mm, PE": coax(0.45e-3, 1.47e-3, 2.25),
         "two-wire 1 mm dia, 10 mm spacing, air": two_wire(0.5e-3, 10e-3),
         "wire 1 mm dia, 10 mm above ground, air": wire_over_ground(0.5e-3, 10e-3),
         "parallel plate w=3 mm, d=1.6 mm, er 4.4 (no fringing)": parallel_plate(3e-3, 1.6e-3, 4.4)}
for name, (L, C) in cases.items():
    er_implied = L * C / (mu0 * eps0)
    Z0 = np.sqrt(L / C)
    print(f"  {name:55s} L'={L*1e9:7.2f} nH/m  C'={C*1e12:7.2f} pF/m  Z0={Z0:7.2f} ohm  L'C'/(mu0 eps0)={er_implied:.3f}")

print("\n=== 2. partial inductances (round wire radius a, length l) ===")
def Lp_wire(l, a, uniform_current=False):
    """Rosa/Grover exact-ish for a cylindrical surface current: (mu0/2pi)[l ln((l+sqrt(l^2+a^2))/a) - sqrt(l^2+a^2) + a];
    uniform (DC) current adds internal inductance mu0 l/(8 pi)."""
    L = mu0 / (2 * np.pi) * (l * np.log((l + np.sqrt(l**2 + a**2)) / a) - np.sqrt(l**2 + a**2) + a)
    if uniform_current:
        L += mu0 * l / (8 * np.pi)
    return L
def Mp_par(l, d):
    """mutual partial inductance of two parallel filaments of length l, spacing d (aligned)."""
    return mu0 / (2 * np.pi) * (l * np.log((l + np.sqrt(l**2 + d**2)) / d) - np.sqrt(l**2 + d**2) + d)
for l, a in ((10e-3, 0.125e-3), (10e-3, 0.0125e-3), (1.6e-3, 0.15e-3), (100e-3, 0.5e-3)):
    Lp = Lp_wire(l, a)
    approx = mu0 * l / (2 * np.pi) * (np.log(2 * l / a) - 1)
    print(f"  l={l*1e3:6.1f} mm, a={a*1e3:6.4f} mm: Lp={Lp*1e9:7.3f} nH ({Lp/l*1e6:.3f} nH/mm), thin-wire approx {approx*1e9:7.3f} nH;"
          f" DC (uniform I) {Lp_wire(l, a, True)*1e9:7.3f} nH")
# loop from partials: two parallel wires length l, spacing D, plus short ends (neglected for l >> D)
a, D = 0.5e-3, 10e-3
for l in (0.05, 0.2, 1.0, 5.0):
    Lloop = 2 * Lp_wire(l, a) - 2 * Mp_par(l, D)
    Lline = two_wire(a, D)[0] * l
    print(f"  two parallel wires l={l} m, D={D*1e3} mm: 2Lp - 2Mp = {Lloop*1e9:8.2f} nH vs two-wire L' l = {Lline*1e9:8.2f} nH (ratio {Lloop/Lline:.4f})")

print("\n=== 3. rectangular loop: partial sum vs Neumann double integral ===")
def rect_loop_partial(A, B, a):
    # four sides: 2 of length A, 2 of length B. Perpendicular sides have zero mutual. Opposite sides: mutual with sign -.
    return 2 * Lp_wire(A, a) + 2 * Lp_wire(B, a) - 2 * Mp_par(A, B) - 2 * Mp_par(B, A)
def rect_loop_neumann(A, B, a, n=4000):
    """numeric Neumann on the loop's centre line vs a parallel path displaced by the wire radius
    (standard trick for self-inductance of a thin wire loop; external inductance)."""
    # path 1: centre line; path 2: inner edge at offset a (loop shrunk by a)
    def path(A_, B_, off, n):
        pts = []
        A2, B2 = A_ - 2 * off, B_ - 2 * off
        x0, y0 = off, off
        s = np.linspace(0, 1, n, endpoint=False)
        for (xa, ya, xb, yb) in ((x0, y0, x0 + A2, y0), (x0 + A2, y0, x0 + A2, y0 + B2), (x0 + A2, y0 + B2, x0, y0 + B2), (x0, y0 + B2, x0, y0)):
            pts.append(np.stack([xa + (xb - xa) * s, ya + (yb - ya) * s], 1))
        P = np.concatenate(pts)
        dP = np.roll(P, -1, axis=0) - P
        return P + dP / 2, dP
    P1, d1 = path(A, B, 0.0, n)
    P2, d2 = path(A, B, a, n)
    M = 0.0
    for i in range(len(P1)):
        R = np.sqrt(((P2 - P1[i])**2).sum(1))
        M += (d2 @ d1[i] / R).sum()
    return mu0 / (4 * np.pi) * M
for (A, B, a) in ((0.05, 0.05, 0.5e-3), (0.10, 0.02, 0.25e-3)):
    Lp_sum = rect_loop_partial(A, B, a)
    Ln = rect_loop_neumann(A, B, a, n=1500)
    print(f"  loop {A*100:.0f} x {B*100:.0f} cm, wire radius {a*1e3} mm: partial sum {Lp_sum*1e9:7.2f} nH, Neumann {Ln*1e9:7.2f} nH (diff {(Ln/Lp_sum-1)*100:+.2f} %)")
    assert abs(Ln / Lp_sum - 1) < 0.03

print("\n=== 4. via inductance ===")
for h, d in ((1.6e-3, 0.3e-3), (1.6e-3, 0.6e-3), (0.8e-3, 0.3e-3), (0.2e-3, 0.2e-3)):
    rosa = Lp_wire(h, d / 2)
    rosa_approx = mu0 * h / (2 * np.pi) * (np.log(4 * h / d) - 1)
    johnson = mu0 * h / (2 * np.pi) * (np.log(4 * h / d) + 1)     # = 5.08 h[in] (ln(4h/d)+1) nH
    print(f"  via h={h*1e3} mm d={d*1e3} mm: partial (exact cyl.) {rosa*1e12:6.0f} pH, thin approx {rosa_approx*1e12:6.0f} pH, "
          f"Johnson&Graham form {johnson*1e12:6.0f} pH")
# via + return via loop: two vias length h, radius r, centre spacing s -> L_loop = 2(Lp - Mp)
for s_ in (1.0e-3, 2.0e-3, 5.0e-3):
    h, r = 1.6e-3, 0.15e-3
    Lloop = 2 * (Lp_wire(h, r) - Mp_par(h, s_))
    print(f"  signal via + return via 1.6 mm long, 0.3 mm dia, spacing {s_*1e3} mm: loop L = {Lloop*1e12:.0f} pH (per-via share {Lloop/2*1e12:.0f} pH)")

print("\n=== 5. 2-D FD Laplace: strip over ground ===")
def strip_capacitance(w, h, er, cells_per_h=20, margin_h=12, top_h=15):
    dlt = h / cells_per_h
    X = w / 2 + margin_h * h
    Y = h + top_h * h
    nx = int(round(2 * X / dlt)) + 1
    ny = int(round(Y / dlt)) + 1
    xs = np.linspace(-X, X, nx); ys = np.linspace(0, Y, ny)
    jh = int(round(h / dlt))
    # eps on vertical faces between (i,j) and (i,j+1): j < jh -> er
    def eps_v(j):   # face between row j and j+1
        return er if j < jh else 1.0
    def eps_h(j):   # face between (i,j) and (i+1,j) at row j
        if j < jh: return er
        if j == jh: return (er + 1) / 2
        return 1.0
    strip = (np.abs(xs) <= w / 2 + 1e-9)            # nodes spanning exactly the strip width
    idx = -np.ones((nx, ny), dtype=int)
    fixed = np.zeros((nx, ny), dtype=bool); Vfix = np.zeros((nx, ny))
    fixed[:, 0] = True; fixed[0, :] = True; fixed[-1, :] = True; fixed[:, -1] = True
    fixed[strip, jh] = True; Vfix[strip, jh] = 1.0
    unknown = np.argwhere(~fixed)
    idx[unknown[:, 0], unknown[:, 1]] = np.arange(len(unknown))
    rows, cols, vals = [], [], []
    b = np.zeros(len(unknown))
    for k, (i, j) in enumerate(unknown):
        nbrs = ((i - 1, j, eps_h(j)), (i + 1, j, eps_h(j)), (i, j - 1, eps_v(j - 1)), (i, j + 1, eps_v(j)))
        diag = 0.0
        for (ii, jj, e) in nbrs:
            diag += e
            if fixed[ii, jj]:
                b[k] += e * Vfix[ii, jj]
            else:
                rows.append(k); cols.append(idx[ii, jj]); vals.append(-e)
        rows.append(k); cols.append(k); vals.append(diag)
    Am = sparse.csr_matrix((vals, (rows, cols)), shape=(len(unknown), len(unknown)))
    sol = spsolve(Am, b)
    V = Vfix.copy()
    V[unknown[:, 0], unknown[:, 1]] = sol
    # energy: sum over faces eps (dV)^2 ; C = eps0 * sum
    W = 0.0
    dVx = np.diff(V, axis=0)       # faces between i,i+1 at row j
    for j in range(ny):
        W += eps_h(j) * np.sum(dVx[:, j]**2)
    dVy = np.diff(V, axis=1)
    for j in range(ny - 1):
        W += eps_v(j) * np.sum(dVy[:, j]**2)
    return eps0 * W      # F/m for V = 1 (C = 2 W_e / V^2 with W_e = eps0/2 * sum)

def hammerstad_jensen(w, h, er):
    u = w / h
    f = 6 + (2 * np.pi - 6) * np.exp(-(30.666 / u)**0.7528)
    Z01 = eta0 / (2 * np.pi) * np.log(f / u + np.sqrt(1 + (2 / u)**2))
    a = 1 + np.log((u**4 + (u / 52)**2) / (u**4 + 0.432)) / 49 + np.log(1 + (u / 18.1)**3) / 18.7
    bb = 0.564 * ((er - 0.9) / (er + 3))**0.053
    eeff = (er + 1) / 2 + (er - 1) / 2 * (1 + 10 / u)**(-a * bb)
    return Z01 / np.sqrt(eeff), eeff
def strip_C_extrap(w, h, er):
    """zero-thickness strip edges converge ~linearly in grid step: Richardson-extrapolate 20 & 30 cells/h"""
    C20 = strip_capacitance(w, h, er, 20); C30 = strip_capacitance(w, h, er, 30)
    d20, d30 = 1 / 20, 1 / 30
    return C30 + (C30 - C20) * d30 / (d20 - d30), C20, C30
for u in (0.5, 1.0, 1.9, 3.0):
    h = 1.0; w = u * h
    C0, C0a, C0b = strip_C_extrap(w, h, 1.0)
    C1, C1a, C1b = strip_C_extrap(w, h, 4.4)
    Z0 = 1 / (c * np.sqrt(C0 * C1)); eeff = C1 / C0
    Z0raw = 1 / (c * np.sqrt(C0b * C1b))
    Zhj, ehj = hammerstad_jensen(w, h, 4.4)
    Cpp = eps0 * w / h
    print(f"  w/h={u:4.1f}: C_air={C0*1e12:6.2f} pF/m (parallel-plate {Cpp*1e12:6.2f}, fringing factor {C0/Cpp:5.2f}); "
          f"FR-4: Z0={Z0:6.2f} ohm (raw 30 cells/h {Z0raw:6.2f}), eps_eff={eeff:5.3f} | Hammerstad-Jensen Z0={Zhj:6.2f}, eps_eff={ehj:5.3f}")
    assert abs(Z0 / Zhj - 1) < 0.01 and abs(eeff / ehj - 1) < 0.01
# microstrip per-length L', C' for a 50-ohm line on 1.6 mm FR-4
Z0t, eet = hammerstad_jensen(3.0e-3, 1.6e-3, 4.4)
print(f"  50-ohm-ish microstrip w=3.0 mm h=1.6 mm FR-4: Z0={Z0t:.2f}, eps_eff={eet:.3f}; L'={Z0t*np.sqrt(eet)/c*1e9/1e3:.3f} nH/mm, "
      f"C'={np.sqrt(eet)/(Z0t*c)*1e12/1e3:.4f} pF/mm")

print("\n=== 6. coaxial loops mutual inductance ===")
def M_coax_loops(r1, r2, d):
    k2 = 4 * r1 * r2 / ((r1 + r2)**2 + d**2)
    k = np.sqrt(k2)
    K = special.ellipk(k2); E = special.ellipe(k2)
    return mu0 * np.sqrt(r1 * r2) * ((2 / k - k) * K - 2 / k * E)
def M_neumann_loops(r1, r2, d, n=4000):
    ph = np.linspace(0, 2 * np.pi, n, endpoint=False)
    dph = 2 * np.pi / n
    tot = 0.0
    for p1 in ph[::4]:
        R = np.sqrt(r1**2 + r2**2 - 2 * r1 * r2 * np.cos(ph - p1) + d**2)
        tot += np.sum(r1 * r2 * np.cos(ph - p1) / R) * dph * (dph * 4)
    return mu0 / (4 * np.pi) * tot
for (r1, r2, d) in ((0.05, 0.05, 0.05), (0.05, 0.05, 0.2), (0.02, 0.05, 0.03)):
    Me = M_coax_loops(r1, r2, d); Mn = M_neumann_loops(r1, r2, d)
    far = mu0 * np.pi * r1**2 * r2**2 / (2 * d**3)
    print(f"  r1={r1*100} cm r2={r2*100} cm d={d*100} cm: M (elliptic) = {Me*1e9:.3f} nH, Neumann {Mn*1e9:.3f} nH, far-field dipole approx {far*1e9:.3f} nH")
    assert abs(Me / Mn - 1) < 1e-3

print("\n=== 7. sphere capacitance & coax energy check ===")
for R in (0.01, 0.1, 1.0):
    print(f"  isolated sphere R={R} m: C = 4 pi eps0 R = {4*np.pi*eps0*R*1e12:.2f} pF")
a, b = 0.45e-3, 1.47e-3; I = 1.0; V = 1.0
Wm = integrate.quad(lambda r: 0.5 * mu0 * (I / (2 * np.pi * r))**2 * 2 * np.pi * r, a, b)[0]
We = integrate.quad(lambda r: 0.5 * eps0 * 2.25 * (V / (r * np.log(b / a)))**2 * 2 * np.pi * r, a, b)[0]
L, C = coax(a, b, 2.25)
print(f"  coax: 2 Wm/I^2 = {2*Wm/I**2*1e9:.3f} nH/m vs L' {L*1e9:.3f}; 2 We/V^2 = {2*We/V**2*1e12:.3f} pF/m vs C' {C*1e12:.3f}")
print(f"  coax internal inductance of inner conductor at DC (uniform I): mu0/(8 pi) = {mu0/(8*np.pi)*1e9:.1f} nH/m -> L_DC = {(L+mu0/(8*np.pi))*1e9:.1f} nH/m")
print("\nAll checks passed.")
