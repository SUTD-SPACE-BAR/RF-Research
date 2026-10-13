#!/usr/bin/env python3
"""
tline_fd2d.py — a small, independent 2-D quasi-static field solver for TEM / quasi-TEM transmission lines.

Method: finite-volume (5-point) discretisation of div(eps grad phi) = 0 on a graded, non-uniform
rectangular grid inside a grounded rectangular box.  Conductors are rectangles (zero thickness allowed)
held at fixed potentials; dielectrics are rectangles of relative permittivity.  The capacitance per unit
length follows from the stored energy:  W = (eps0/2) * sum_edges g * (dphi)^2 ,  C = 2W / V^2.
Z0 and eps_eff follow from the capacitance with and without dielectric:
        Z0 = 1 / (c0 * sqrt(C * C_air)),   eps_eff = C / C_air.
Coupled lines: even/odd-mode per-strip capacitances from energies with (+1,+1) and (+1,-1) excitation.

This is used by tools/verify/tline_microstrip.py and tools/verify/tline_cpwg.py to validate closed-form
formulas (Hammerstad-Jensen, Wheeler, Cohn, Ghione-Naldi, IPC-2141 ...) independently of scikit-rf.

Self-test (run this file): zero-thickness centred stripline vs Cohn's exact elliptic-integral formula,
with a mesh-refinement study.
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

EPS0 = 8.8541878128e-12
C0 = 299_792_458.0


def graded_axis(keys, lo, hi, hmin, hmax, ratio=1.25):
    """Grid coordinates in [lo, hi] that include every key point, with spacing hmin at key points growing
    geometrically (by `ratio`) up to hmax in between."""
    keys = np.unique(np.clip(np.concatenate([[lo, hi], np.asarray(keys, float)]), lo, hi))
    pts = [keys[0]]
    for a, b in zip(keys[:-1], keys[1:]):
        L = b - a
        if L <= 0:
            continue
        # build a symmetric graded spacing from both ends
        steps = []
        h = hmin
        tot = 0.0
        left = []
        while tot + h < L / 2:
            left.append(h)
            tot += h
            h = min(h * ratio, hmax)
        rem = L - 2 * tot
        seq = left + ([rem] if rem > 1e-15 else []) + left[::-1]
        # rem may be larger than hmax: split it
        out = []
        for s_ in seq:
            if s_ > hmax * 1.0001:
                n = int(np.ceil(s_ / hmax))
                out += [s_ / n] * n
            else:
                out.append(s_)
        x = a
        for s_ in out:
            x += s_
            pts.append(x)
        pts[-1] = b
    return np.unique(np.round(np.array(pts), 15))


class Geometry:
    def __init__(self, xmin, xmax, ymax):
        self.xmin, self.xmax, self.ymax = xmin, xmax, ymax
        self.diel = []      # (x0, x1, y0, y1, er)
        self.cond = []      # (x0, x1, y0, y1, name)
        self.keysx, self.keysy = [], []

    def add_dielectric(self, x0, x1, y0, y1, er):
        self.diel.append((x0, x1, y0, y1, er))
        self.keysx += [x0, x1]
        self.keysy += [y0, y1]

    def add_conductor(self, x0, x1, y0, y1, name):
        self.cond.append((x0, x1, y0, y1, name))
        self.keysx += [x0, x1]
        self.keysy += [y0, y1]


def solve_energy(geo, potentials, hmin, hmax, ratio=1.25, with_dielectric=True, return_grid=False):
    """potentials: dict name -> volts (conductors not listed and the box walls are at 0 V).
    Returns stored energy per unit length W (J/m)."""
    x = graded_axis(geo.keysx, geo.xmin, geo.xmax, hmin, hmax, ratio)
    y = graded_axis(geo.keysy, 0.0, geo.ymax, hmin, hmax, ratio)
    nx, ny = len(x), len(y)
    dx, dy = np.diff(x), np.diff(y)
    xc = 0.5 * (x[:-1] + x[1:])
    yc = 0.5 * (y[:-1] + y[1:])
    eps = np.ones((nx - 1, ny - 1))
    if with_dielectric:
        for (x0, x1, y0, y1, er) in geo.diel:
            mi = (xc > x0) & (xc < x1)
            mj = (yc > y0) & (yc < y1)
            eps[np.ix_(mi, mj)] = er
    idx = np.arange(nx * ny).reshape(nx, ny)
    # fixed nodes: box walls (0 V) and conductors
    phi = np.zeros((nx, ny))
    fixed = np.zeros((nx, ny), bool)
    fixed[0, :] = fixed[-1, :] = fixed[:, 0] = fixed[:, -1] = True
    tol = 1e-12
    for (x0, x1, y0, y1, name) in geo.cond:
        mi = (x >= x0 - tol) & (x <= x1 + tol)
        mj = (y >= y0 - tol) & (y <= y1 + tol)
        fixed[np.ix_(mi, mj)] = True
        phi[np.ix_(mi, mj)] = potentials.get(name, 0.0)
    rows, cols, vals = [], [], []
    # horizontal edges (i,j)-(i+1,j)
    epad = np.zeros((nx + 1, ny + 1))
    epad[1:nx, 1:ny] = eps   # epad[i+1, j+1] = eps[i, j]; zero outside
    dyp = np.concatenate([[0], dy, [0]])
    dxp = np.concatenate([[0], dx, [0]])
    I, J = np.meshgrid(np.arange(nx - 1), np.arange(ny), indexing="ij")
    gh = (epad[I + 1, J] * dyp[J] / 2 + epad[I + 1, J + 1] * dyp[J + 1] / 2) / dx[I]
    a_h = idx[I, J].ravel(); b_h = idx[I + 1, J].ravel(); g_h = gh.ravel()
    I, J = np.meshgrid(np.arange(nx), np.arange(ny - 1), indexing="ij")
    gv = (epad[I, J + 1] * dxp[I] / 2 + epad[I + 1, J + 1] * dxp[I + 1] / 2) / dy[J]
    a_v = idx[I, J].ravel(); b_v = idx[I, J + 1].ravel(); g_v = gv.ravel()
    a = np.concatenate([a_h, a_v]); b = np.concatenate([b_h, b_v]); g = np.concatenate([g_h, g_v])
    N = nx * ny
    Lm = sp.coo_matrix((np.concatenate([g, g, -g, -g]),
                        (np.concatenate([a, b, a, b]), np.concatenate([a, b, b, a]))), shape=(N, N)).tocsr()
    fx = fixed.ravel()
    free = ~fx
    ph = phi.ravel().copy()
    Lff = Lm[free][:, free]
    rhs = -Lm[free][:, fx] @ ph[fx]
    ph[free] = spla.spsolve(Lff.tocsc(), rhs)
    W = 0.5 * EPS0 * np.sum(g * (ph[a] - ph[b]) ** 2)
    if return_grid:
        return W, (nx, ny)
    return W


def line_params(geo, signal="sig", hmin=None, hmax=None, ratio=1.25):
    """Single signal conductor at 1 V; returns (Z0, eps_eff, C [F/m])."""
    Wd = solve_energy(geo, {signal: 1.0}, hmin, hmax, ratio, True)
    Wa = solve_energy(geo, {signal: 1.0}, hmin, hmax, ratio, False)
    C, Ca = 2 * Wd, 2 * Wa
    return 1 / (C0 * np.sqrt(C * Ca)), C / Ca, C


def coupled_params(geo, s1="s1", s2="s2", hmin=None, hmax=None, ratio=1.25):
    """Symmetric coupled pair: returns (Z_even, Z_odd, eeff_even, eeff_odd); per-strip capacitances = energy."""
    Ce = solve_energy(geo, {s1: 1.0, s2: 1.0}, hmin, hmax, ratio, True)
    Cea = solve_energy(geo, {s1: 1.0, s2: 1.0}, hmin, hmax, ratio, False)
    Co = solve_energy(geo, {s1: 1.0, s2: -1.0}, hmin, hmax, ratio, True)
    Coa = solve_energy(geo, {s1: 1.0, s2: -1.0}, hmin, hmax, ratio, False)
    Ze = 1 / (C0 * np.sqrt(Ce * Cea))
    Zo = 1 / (C0 * np.sqrt(Co * Coa))
    return Ze, Zo, Ce / Cea, Co / Coa


# ------------------------------------------------------------------ canned geometries
def microstrip_geo(W, h, t, er, box_w=None, box_h=None, mask_t=0.0, mask_er=3.8, mask_fill=False):
    """mask models: conformal (default): mask_t on the substrate and mask_t over the strip;
    mask_fill=True: a slab from the substrate up to mask_t above the copper top (fills gaps completely)."""
    box_w = box_w or max(40 * h, 12 * W)
    box_h = box_h or 25 * h
    g = Geometry(-box_w / 2, box_w / 2, box_h)
    g.add_dielectric(-box_w / 2, box_w / 2, 0, h, er)
    if mask_t > 0 and mask_fill:
        g.add_dielectric(-box_w / 2, box_w / 2, h, h + t + mask_t, mask_er)
    elif mask_t > 0:
        # conformal-ish mask: a layer of thickness mask_t on the substrate and over the strip (rectangular approx.)
        g.add_dielectric(-box_w / 2, box_w / 2, h, h + mask_t, mask_er)
        g.add_dielectric(-W / 2 - mask_t, W / 2 + mask_t, h, h + t + mask_t, mask_er)
    g.add_conductor(-W / 2, W / 2, h, h + t, "sig")
    return g


def stripline_geo(W, b, t, er, box_w=None):
    box_w = box_w or max(30 * b, 10 * W)
    g = Geometry(-box_w / 2, box_w / 2, b)
    g.add_dielectric(-box_w / 2, box_w / 2, 0, b, er)
    g.add_conductor(-W / 2, W / 2, b / 2 - t / 2, b / 2 + t / 2, "sig")
    return g


def cpwg_geo(W, S, h, t, er, box_w=None, box_h=None, mask_t=0.0, mask_er=3.8):
    box_w = box_w or max(30 * h, 20 * (W + 2 * S))
    box_h = box_h or 20 * h
    g = Geometry(-box_w / 2, box_w / 2, box_h)
    g.add_dielectric(-box_w / 2, box_w / 2, 0, h, er)
    if mask_t > 0:
        g.add_dielectric(-box_w / 2, box_w / 2, h, h + t + mask_t, mask_er)
    g.add_conductor(-W / 2, W / 2, h, h + t, "sig")
    g.add_conductor(-box_w / 2, -W / 2 - S, h, h + t, "gnd")
    g.add_conductor(W / 2 + S, box_w / 2, h, h + t, "gnd")
    return g


def coupled_microstrip_geo(W, s, h, t, er, box_w=None, box_h=None, mask_t=0.0, mask_er=3.8):
    """mask_t > 0: gap-filling soldermask slab from the substrate to mask_t above the copper top."""
    box_w = box_w or max(40 * h, 16 * (2 * W + s))
    box_h = box_h or 25 * h
    g = Geometry(-box_w / 2, box_w / 2, box_h)
    g.add_dielectric(-box_w / 2, box_w / 2, 0, h, er)
    if mask_t > 0:
        g.add_dielectric(-box_w / 2, box_w / 2, h, h + t + mask_t, mask_er)
    g.add_conductor(-s / 2 - W, -s / 2, h, h + t, "s1")
    g.add_conductor(s / 2, s / 2 + W, h, h + t, "s2")
    return g


def _richardson(v1, v2, v3):
    try:
        p = np.log(abs((v1 - v2) / (v2 - v3))) / np.log(2)
        p = float(np.clip(p, 0.5, 2.5))
    except Exception:
        p = 1.0
    if not np.isfinite(p):
        p = 1.0
    return v3 + (v3 - v2) / (2**p - 1), p


def refine_study(fun, levels=(0.5, 0.25, 0.125)):
    """fun(scale) -> value or tuple of values; three mesh levels (each halving the spacing); returns
    (values, extrapolated, observed order) using generalized Richardson extrapolation (edge singularities
    give orders ~0.5-1)."""
    vals = [fun(s) for s in levels]
    if np.ndim(vals[0]) == 0:
        ext, p = _richardson(*vals)
        return vals, ext, p
    vals = np.array(vals)
    out = [_richardson(*vals[:, k]) for k in range(vals.shape[1])]
    return vals, np.array([o[0] for o in out]), np.array([o[1] for o in out])


if __name__ == "__main__":
    from scipy.special import ellipk
    ok = True

    def cohn(W, b, er):
        k = 1 / np.cosh(np.pi * W / (2 * b))
        kp = np.sqrt(1 - k * k)
        return 30 * np.pi / np.sqrt(er) * ellipk(k * k) / ellipk(kp * kp)

    print("Self-test: zero-thickness centred stripline vs Cohn exact (er = 4.4)")
    for W, b in [(0.3e-3, 0.6e-3), (1.0e-3, 1.0e-3), (0.15e-3, 1.0e-3)]:
        exact = cohn(W, b, 4.4)
        geo = stripline_geo(W, b, 0.0, 4.4)
        vals, ext, p = refine_study(lambda s: line_params(geo, hmin=W / 40 * s, hmax=b / 6 * s)[0])
        err = (ext - exact) / exact
        print(f"   W = {W*1e3:.2f} mm, b = {b*1e3:.2f} mm: Cohn {exact:.3f} ohm; FD {', '.join(f'{v:.3f}' for v in vals)}"
              f" -> extrapolated {ext:.3f} (order {p:.2f}), error {err*100:+.3f} %")
        ok &= abs(err) < 0.003
    print("[PASS]" if ok else "[FAIL]", "FD solver reproduces Cohn's exact stripline within 0.3 % after extrapolation")
