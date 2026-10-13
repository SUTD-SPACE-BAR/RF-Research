#!/usr/bin/env python3
"""
Verification for kb/03-transmission-lines-matching/signal-flow-graphs-mason.md

Checks:
  1. A general Mason's-gain-rule implementation (forward paths, loops, non-touching loop sets) equals the
     direct linear solution of the node equations for random graphs.
  2. Symbolic (sympy): Mason gives Gamma_in = S11 + S12 S21 GL / (1 - S22 GL) and the transducer gain.
  3. Power delivered from a mismatched source: P_L = P_av (1-|GS|^2)(1-|GL|^2)/|1-GS GL|^2; maximum at GL = GS*.
  4. Mismatch uncertainty of a power measurement: limits 20 log10(1 +- |GS||GL|) and Monte-Carlo distribution
     (arcsine-shaped), RSS vs worst case for several terms.
  5. Reflection measurement with finite coupler directivity: VSWR reading limits for a perfect load.
  6. Insertion-loss ripple from two mismatches separated by a line.

Run: python3 tools/verify/tline_mason.py
"""
import itertools
import numpy as np
import sympy as sp

ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


# ---------------------------------------------------------------- Mason implementation
def simple_paths(edges, src, dst):
    """edges: dict (u, v) -> gain. Returns list of node lists for all simple paths src -> dst."""
    adj = {}
    for (u, v) in edges:
        adj.setdefault(u, []).append(v)
    out = []

    def dfs(node, path):
        if node == dst:
            out.append(path[:])
            return
        for nxt in adj.get(node, []):
            if nxt not in path:
                path.append(nxt)
                dfs(nxt, path)
                path.pop()
    dfs(src, [src])
    return out


def simple_cycles(edges):
    nodes = sorted({n for e in edges for n in e}, key=str)
    adj = {}
    for (u, v) in edges:
        adj.setdefault(u, []).append(v)
    cycles = []
    for start_i, s in enumerate(nodes):
        allowed = set(nodes[start_i:])

        def dfs(node, path):
            for nxt in adj.get(node, []):
                if nxt == s:
                    cycles.append(path[:])
                elif nxt in allowed and nxt not in path:
                    path.append(nxt)
                    dfs(nxt, path)
                    path.pop()
        dfs(s, [s])
    return cycles


def path_gain(edges, nodes, closed=False):
    g = 1
    seq = nodes + ([nodes[0]] if closed else [])
    for u, v in zip(seq[:-1], seq[1:]):
        g = g * edges[(u, v)]
    return g


def delta(loops, gains, exclude=frozenset()):
    """Graph determinant over loops not touching `exclude` nodes."""
    L = [(frozenset(l), g) for l, g in zip(loops, gains) if not (frozenset(l) & exclude)]
    D = 1
    n = len(L)
    for k in range(1, n + 1):
        term = 0
        for combo in itertools.combinations(range(n), k):
            sets = [L[i][0] for i in combo]
            if all(not (a & b) for a, b in itertools.combinations(sets, 2)):
                prod = 1
                for i in combo:
                    prod = prod * L[i][1]
                term = term + prod
        if term == 0 and k > 1:
            # no more non-touching sets of this size -> larger sizes impossible too
            pass
        D = D + (-1) ** k * term
    return D


def mason(edges, src, dst):
    loops = simple_cycles(edges)
    lg = [path_gain(edges, l, closed=True) for l in loops]
    D = delta(loops, lg)
    num = 0
    for p in simple_paths(edges, src, dst):
        num = num + path_gain(edges, p) * delta(loops, lg, frozenset(p))
    return num / D


def direct(edges, src, dst):
    """Solve x = A x + e_src (unit injection at src) -> x[dst]."""
    nodes = sorted({n for e in edges for n in e}, key=str)
    idx = {n: i for i, n in enumerate(nodes)}
    N = len(nodes)
    A = np.zeros((N, N), complex)
    for (u, v), g in edges.items():
        A[idx[v], idx[u]] += g
    b = np.zeros(N, complex)
    b[idx[src]] = 1
    x = np.linalg.solve(np.eye(N) - A, b)
    return x[idx[dst]]


# ---------------------------------------------------------------- 1. random graphs
rng = np.random.default_rng(7)
maxerr = 0
for trial in range(40):
    n = rng.integers(4, 7)
    nodes = list(range(n))
    edges = {}
    for u in nodes:
        for v in nodes:
            if u != v and rng.uniform() < 0.35 and v != 0 and u != n - 1:
                edges[(u, v)] = complex(rng.normal(0, 0.4), rng.normal(0, 0.4))
    if not simple_paths(edges, 0, n - 1):
        continue
    m = mason(edges, 0, n - 1)
    d = direct(edges, 0, n - 1)
    maxerr = max(maxerr, abs(m - d) / max(abs(d), 1e-12))
check("Mason's rule == direct solution of node equations (random graphs)", maxerr < 1e-9, f"(max rel err {maxerr:.1e})")

# ---------------------------------------------------------------- 2. symbolic two-port
S11, S12, S21, S22, GS, GL, bs = sp.symbols("S11 S12 S21 S22 Gamma_S Gamma_L b_s")
# nodes: a1, b1, a2, b2 ; source injects b_s into a1 ; load reflects b2 -> a2
E = {("a1", "b1"): S11, ("a1", "b2"): S21, ("a2", "b2"): S22, ("a2", "b1"): S12, ("b2", "a2"): GL}
Gin = sp.simplify(mason(E, "a1", "b1"))
check("sympy/Mason: Gamma_in = S11 + S12 S21 GL/(1 - S22 GL)",
      sp.simplify(Gin - (S11 + S12 * S21 * GL / (1 - S22 * GL))) == 0, f"({Gin})")
E2 = dict(E)
E2[("b1", "a1")] = GS
E2[("src", "a1")] = 1
b2_over = sp.simplify(mason(E2, "src", "b2"))
expected = S21 / ((1 - S11 * GS) * (1 - S22 * GL) - S12 * S21 * GS * GL)
check("sympy/Mason: b2/b_s = S21 / [(1-S11 GS)(1-S22 GL) - S12 S21 GS GL]", sp.simplify(b2_over - expected) == 0)
# transducer gain: P_L = |b2|^2 (1-|GL|^2), P_av = |bs|^2/(1-|GS|^2)  ->  G_T formula of the s-parameters page
num = lambda **kw: complex(sp.N(b2_over.subs(kw)))
vals = dict(S11=0.3 - 0.2j, S12=0.05 + 0.02j, S21=2.1 + 1.0j, S22=0.4 + 0.1j, Gamma_S=0.2 - 0.3j, Gamma_L=-0.25 + 0.1j)
b2v = complex(b2_over.subs({S11: vals["S11"], S12: vals["S12"], S21: vals["S21"], S22: vals["S22"], GS: vals["Gamma_S"], GL: vals["Gamma_L"]}))
GT_mason = abs(b2v) ** 2 * (1 - abs(vals["Gamma_L"]) ** 2) * (1 - abs(vals["Gamma_S"]) ** 2)
s11, s12, s21, s22, gs, gl = [vals[k] for k in ["S11", "S12", "S21", "S22", "Gamma_S", "Gamma_L"]]
gin = s11 + s12 * s21 * gl / (1 - s22 * gl)
GT_formula = (1 - abs(gs) ** 2) * abs(s21) ** 2 * (1 - abs(gl) ** 2) / abs((1 - gs * gin) * (1 - s22 * gl)) ** 2
check("Mason-derived transducer gain == Pozar G_T formula (numeric)", abs(GT_mason - GT_formula) < 1e-12)

# ---------------------------------------------------------------- 3. mismatched source -> load
def PL(GSv, GLv, Pav=1.0):
    return Pav * (1 - abs(GSv) ** 2) * (1 - abs(GLv) ** 2) / abs(1 - GSv * GLv) ** 2


GSv = 0.3 * np.exp(1j * 0.7)
check("P_L = P_av exactly when GL = GS* (conjugate match)", abs(PL(GSv, np.conj(GSv)) - 1) < 1e-12)
check("with a mismatched source, a 50-ohm load (GL=0) gets P_av (1-|GS|^2)", abs(PL(GSv, 0) - (1 - 0.09)) < 1e-12)
grid = [PL(GSv, r * np.exp(1j * p)) for r in np.linspace(0, 0.95, 60) for p in np.linspace(0, 2 * np.pi, 120)]
check("no passive load beats P_av; conjugate load beats the 50-ohm load", max(grid) <= 1 + 1e-12 and PL(GSv, np.conj(GSv)) > PL(GSv, 0))
# equivalence with the circuit picture
ZS = 50 * (1 + GSv) / (1 - GSv)
ZL = 50 * (1 + 0.4j) / (1 - 0.4j)
I = 1.0 / (ZS + ZL)
P_circ = 0.5 * abs(I) ** 2 * ZL.real
Pav_c = 1.0 / (8 * ZS.real)
check("flow-graph P_L formula == Thevenin circuit calculation", abs(P_circ / Pav_c - PL(GSv, 0.4j)) < 1e-12)

# ---------------------------------------------------------------- 4. mismatch uncertainty
print("   Mismatch uncertainty limits 20log10(1 +- |GS||GL|):")
cases = [("signal generator VSWR 1.5 / power sensor VSWR 1.2", 0.2, (1.2 - 1) / 2.2),
         ("LoRa module (~VSWR 2) / cheap sensor VSWR 1.5", 1 / 3, 0.2),
         ("NanoVNA port (~VSWR 1.3 uncorrected) / VSWR 2 DUT", 0.3 / 2.3, 1 / 3)]
for name, a, b in cases:
    up, dn = -20 * np.log10(1 - a * b), -20 * np.log10(1 + a * b)   # error in dB of the measured power
    ph = rng.uniform(0, 2 * np.pi, 200000)
    mc = -20 * np.log10(np.abs(1 - a * b * np.exp(1j * ph)))
    print(f"      {name}: |GS||GL| = {a*b:.4f} -> +{up:.3f} / {dn:.3f} dB; MC std {mc.std():.3f} dB "
          f"(worst/sqrt2 = {up/np.sqrt(2):.3f})")
a, b = 0.2, 0.2 / 2.2
ph = rng.uniform(0, 2 * np.pi, 400000)
mc = -20 * np.log10(np.abs(1 - a * b * np.exp(1j * ph)))
check("Monte-Carlo extremes of -20log10|1 - GS GL| are -20log10(1 -+ |GS||GL|)",
      abs(mc.max() + 20 * np.log10(1 - a * b)) < 1e-3 and abs(mc.min() + 20 * np.log10(1 + a * b)) < 1e-3,
      f"(+{mc.max():.3f} / {mc.min():.3f} dB)")
check("uniform-phase mismatch term has std ~ worst-case / sqrt(2) (U-shaped distribution)",
      abs(mc.std() - 20 * np.log10(1 + a * b) / np.sqrt(2)) / mc.std() < 0.03)
hist, _ = np.histogram(mc, bins=20)
check("distribution is U-shaped (edges more populated than the centre)", hist[0] > hist[10] and hist[-1] > hist[10])

# ---------------------------------------------------------------- 5. directivity-limited reflection measurement
D = 10 ** (-20 / 20)       # 20 dB directivity
for Gtrue in [0.0, 0.05, 0.1]:
    lo, hi = max(Gtrue - D, 0), Gtrue + D
    sw = lambda g: (1 + g) / (1 - g)
    print(f"      20 dB directivity, true |G| {Gtrue:.2f} (VSWR {sw(Gtrue):.3f}): reads |G| {lo:.3f}..{hi:.3f} "
          f"(VSWR {sw(lo):.3f}..{sw(hi):.3f})")
check("perfect load read through a 20 dB-directivity bridge can show VSWR up to 1.222", abs((1 + D) / (1 - D) - 1.2222) < 1e-3)

# ---------------------------------------------------------------- 6. ripple from two separated mismatches
# lossless 50-ohm line of length l between two reflections G1, G2 (e.g. an SMA launch and a U.FL)
G1, G2 = 0.1, 0.15
f = np.linspace(0.1e9, 3e9, 20001)
th = 2 * np.pi * f * 0.10 / (0.7 * 299792458)       # 10 cm, VF 0.7
S21 = (1 - G1**2) ** 0.5 * (1 - G2**2) ** 0.5 * np.exp(-1j * th) / (1 - G1 * G2 * np.exp(-2j * th))
ripple = 20 * np.log10(np.abs(S21))
pp = ripple.max() - ripple.min()
pred = 20 * np.log10((1 + G1 * G2) / (1 - G1 * G2))
check("insertion-loss ripple p-p = 20log10[(1+|G1G2|)/(1-|G1G2|)] with period vp/(2l)", abs(pp - pred) < 1e-3,
      f"({pp:.3f} dB p-p; period {0.7*299792458/(2*0.10)/1e6:.0f} MHz)")

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
