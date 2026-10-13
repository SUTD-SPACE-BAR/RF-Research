#!/usr/bin/env python3
"""W5-S15 / G-06-06 — coupling-matrix synthesis from polynomials (Cameron), extracted pole, linear phase,
SAW triple-transit ripple and YIG numbers, for kb/06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md
("Level 3b — synthesis from polynomials ...").

 A. Cameron recursion for a generalised Chebyshev filtering function with prescribed transmission zeros (TZs):
    F(w), P(w), eps; E(s) from the Feldtkeller equation E E* = F F* + P P*/eps^2 (LHP roots). Checks: equiripple
    return loss, TZ positions, |S11|^2 + |S21|^2 = 1.
 B. (N+2) transversal matrix from residues of y21, y22 (Cameron 2003); folded canonical form by similarity
    (Givens) rotations — each pivot is chosen so it zeroes the target element without refilling earlier zeros;
    response invariance checked. Comparison with the page's Example 6 quadruplet.
 C. GNSS 1559-1610 MHz preselector with a TZ placed on Iridium (1616-1626 MHz): asymmetric N = 5, finite-Qu sweep.
 D. Linear phase: a real-axis TZ pair (s = ±sigma) flattens group delay (N = 6) at a cost in selectivity.
 E. Trisection: N = 3 with one TZ -> folded N = 3 is the triplet (M13 != 0, asymmetric detunings).
 F. Extracted pole: a resonator hung on a non-resonating node (NRN) puts a TZ exactly at its own frequency.
 G. SAW triple-transit echo: ripple period 1/(2 tau), amplitude ±20log(1±a), delay ripple ≈ ±2 tau a.
 H. YIG sphere: f = gamma mu0 H0, lowest saturated frequency gamma 4piMs/3, Q ≈ f/(gamma ΔH).
Run: python3 tools/verify/s15_coupling_matrix.py   (a few seconds)
"""
import sys
import numpy as np
from scipy.optimize import brentq

P_ = np.polynomial.polynomial          # coefficient arrays, low -> high
ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


# ------------------------------------------------------------------ synthesis
def cameron(N, RL, tz):
    """Recursion for U_N (-> F) with prescribed TZs tz (normalised omega; real = on the jw axis,
    ±j*sigma = real-axis zeros in s). Zeros at infinity fill up to N. Returns F(w), P(w), eps (eps_R = 1)."""
    wk = list(tz) + [np.inf] * (N - len(tz))
    U = np.array([1.0 + 0j]); V = np.array([0.0 + 0j])
    w = np.array([0, 1.0 + 0j]); wp2 = np.array([-1.0, 0, 1.0 + 0j])     # omega and omega^2 - 1
    for k in range(N):
        inv = 0 if np.isinf(wk[k]) else 1 / wk[k]
        c = np.sqrt(1 - inv ** 2 + 0j)
        a = P_.polysub(w, [inv])
        U, V = P_.polyadd(P_.polymul(a, U), c * P_.polymul(wp2, V)), P_.polyadd(P_.polymul(a, V), c * U)
    F = U / U[-1]
    P = np.array([1.0 + 0j])
    for z in tz:
        P = P_.polymul(P, [-z, 1.0])
    eps = 1 / np.sqrt(10 ** (RL / 10) - 1) * abs(P_.polyval(1.0, P) / P_.polyval(1.0, F))
    return F, P, eps


def w2s(pw):                        # p(omega) -> p(s), omega = -j s
    return np.array([c * (-1j) ** k for k, c in enumerate(pw)])


def paraconj(ps):
    return np.array([np.conj(c) * (-1) ** k for k, c in enumerate(ps)])


def synth(N, RL, tz):
    F, P, eps = cameron(N, RL, tz)
    Fs = w2s(F); Ps = w2s(P)
    Ps = Ps / Ps[-1]                 # monic in s (w2s leaves a (-j)^nfz factor)
    if (N - len(tz)) % 2 == 0:
        Ps = 1j * Ps                 # Cameron's convention so that S11, S21 are orthogonal on the jw axis
    EE = P_.polyadd(P_.polymul(Fs, paraconj(Fs)), P_.polymul(Ps, paraconj(Ps)) / eps ** 2)
    r = P_.polyroots(EE); r = r[r.real < 0]
    assert len(r) == N
    Es = P_.polyfromroots(r); Es = Es / Es[-1]; Fs = Fs / Fs[-1]
    return Fs, Ps, Es, eps


def poly_resp(syn, lam):
    Fs, Ps, Es, eps = syn
    s = 1j * np.asarray(lam, complex)
    E = P_.polyval(s, Es)
    return P_.polyval(s, Ps) / (eps * E), P_.polyval(s, Fs) / E


def transversal(syn, N):
    Fs, Ps, Es, eps = syn
    ef = Es + np.pad(Fs, (0, len(Es) - len(Fs)))
    m1 = np.zeros(N + 1, complex); n1 = np.zeros(N + 1, complex)
    for k in range(N + 1):
        if k % 2 == 0:
            m1[k] = ef[k].real; n1[k] = 1j * ef[k].imag
        else:
            m1[k] = 1j * ef[k].imag; n1[k] = ef[k].real
    num22, den = (n1, m1) if N % 2 == 0 else (m1, n1)
    den = np.trim_zeros(den, 'b')
    poles = P_.polyroots(den); dpr = P_.polyder(den)
    r21 = P_.polyval(poles, Ps / eps) / P_.polyval(poles, dpr)
    r22 = P_.polyval(poles, num22) / P_.polyval(poles, dpr)
    M = np.zeros((N + 2, N + 2))
    for k in range(N):
        ML = np.sqrt(r22[k].real); MS = (r21[k] / np.sqrt(r22[k])).real
        M[k + 1, k + 1] = -(poles[k] / 1j).real
        M[0, k + 1] = M[k + 1, 0] = MS; M[N + 1, k + 1] = M[k + 1, N + 1] = ML
    return M


def cm_resp(M, lam, Qu_fbw=None):
    """S21, S11 of an (N+2) coupling matrix, A = lam*W - jR + M; finite Q: resonator diagonal gets -j/(FBW*Qu)."""
    n = M.shape[0]; R = np.zeros((n, n)); R[0, 0] = R[-1, -1] = 1; W = np.eye(n); W[0, 0] = W[-1, -1] = 0
    G = np.zeros((n, n)) if Qu_fbw is None else np.diag([0] + [1 / Qu_fbw] * (n - 2) + [0])
    s21 = np.empty(len(lam), complex); s11 = np.empty(len(lam), complex)
    for i, l in enumerate(lam):
        Ai = np.linalg.inv(l * W - 1j * R - 1j * G + M)
        s21[i] = -2j * Ai[-1, 0]; s11[i] = 1 + 2j * Ai[0, 0]
    return s21, s11


def rot(M, a, b, th):
    R = np.eye(M.shape[0]); c, s = np.cos(th), np.sin(th)
    R[a, a] = R[b, b] = c; R[a, b] = -s; R[b, a] = s
    return R @ M @ R.T


def fold(M, tol=1e-9):
    """Transversal -> folded form. Target nonzeros (inner 1..N): i = j, |i-j| = 1, i + j = N+1, i + j = N."""
    M = M.copy(); n = M.shape[0]; N = n - 2; S, L = 0, N + 1
    order = [(S, j) for j in range(N, 1, -1)] + [(i, L) for i in range(1, N)]
    allowed = lambda i, j: j == i + 1 or i + j == N + 1 or i + j == N or i == j
    for k in range(1, N // 2 + 1):
        order += [(k, j) for j in range(N, k, -1) if not allowed(k, j)]
        c = N + 1 - k
        order += [(i, c) for i in range(1, c) if not allowed(i, c) and (i, c) not in order]
    done, seq = [], []
    for (i, j) in order:
        if abs(M[i, j]) < tol:
            done.append((i, j)); continue
        found = False
        for a in range(1, N + 1):
            for b in range(a + 1, N + 1):
                if not ({i, j} & {a, b}):
                    continue
                f = lambda th: rot(M, a, b, th)[i, j]
                ths = np.linspace(-np.pi / 2, np.pi / 2, 721); v = [f(t) for t in ths]
                for t0, t1, v0, v1 in zip(ths[:-1], ths[1:], v[:-1], v[1:]):
                    if v0 * v1 < 0:
                        th = brentq(f, t0, t1, xtol=1e-15)
                        Mn = rot(M, a, b, th)
                        if all(abs(Mn[p, q]) < 1e-8 for p, q in done):
                            M, found = Mn, True; seq.append(((i, j), (a, b))); break
                if found:
                    break
            if found:
                break
        if not found:
            raise RuntimeError(f"cannot annihilate {(i, j)}")
        done.append((i, j))
    # sign normalisation: make S-1, main-line and N-L couplings positive (similarity with diag(±1))
    D = np.ones(n)
    for k in range(1, n):
        if M[k - 1, k] * D[k - 1] < 0:
            D[k] = -1
    M = np.diag(D) @ M @ np.diag(D)
    M[abs(M) < 1e-10] = 0
    return M, seq


def gdelay(s21, lam):
    ph = np.unwrap(np.angle(s21))
    return -np.gradient(ph, lam)


def fmt(M):
    N = M.shape[0] - 2
    lines = []
    for i in range(N + 2):
        for j in range(i, N + 2):
            if abs(M[i, j]) > 1e-9:
                lab = lambda k: "S" if k == 0 else ("L" if k == N + 1 else str(k))
                lines.append(f"M{lab(i)}{lab(j)} {M[i,j]:+.4f}")
    return ", ".join(lines)


# ================================================================ A, B. symmetric quadruplet
print("A/B: N = 4, 0.1 dB ripple (RL 16.43 dB), TZs at lambda = ±2.05 (as in the page's Example 6)")
RL01 = -10 * np.log10(1 - 10 ** (-0.1 / 10))
syn = synth(4, RL01, [-2.05, 2.05])
lam = np.linspace(-4, 4, 1601)
p21, p11 = poly_resp(syn, lam)
inb = abs(lam) <= 1
rl_in = -20 * np.log10(abs(p11[inb]).max()); il_rip = -20 * np.log10(abs(p21[inb]).min())
uni = np.max(abs(abs(p21) ** 2 + abs(p11) ** 2 - 1))
tz_found = [lam[np.argmin(abs(p21 - 0) + 1e3 * (lam > 0))], lam[np.argmin(abs(p21) + 1e3 * (lam < 0))]]
print(f"   polynomials: in-band RL {rl_in:.2f} dB (target {RL01:.2f}), ripple {il_rip:.3f} dB, max | |S11|^2+|S21|^2-1 | {uni:.1e}, "
      f"TZs at {tz_found[0]:+.2f}, {tz_found[1]:+.2f}")
check("A1 Cameron polynomials: equiripple RL as specified, TZs where prescribed, lossless", abs(rl_in - RL01) < 0.01 and uni < 1e-10
      and abs(abs(tz_found[0]) - 2.05) < 0.01)
MT = transversal(syn, 4)
t21, t11 = cm_resp(MT, lam)
MF, seq = fold(MT)
f21, f11 = cm_resp(MF, lam)
dev_t = np.max(abs(abs(t21) - abs(p21))); dev_f = np.max(abs(abs(f21) - abs(t21)))
print(f"   transversal (N+2) matrix reproduces the polynomials to {dev_t:.1e}; folded by {len(seq)} rotations, invariant to {dev_f:.1e}")
print(f"   folded: {fmt(MF)}")
check("B1 transversal = polynomial response; folding rotations leave the response unchanged; quadruplet pattern",
      dev_t < 1e-9 and dev_f < 1e-9 and abs(MF[1, 3]) < 1e-9 and abs(MF[2, 4]) < 1e-9 and MF[1, 4] < 0)
# compare with Example 6 (inline 0.1 dB Chebyshev values + M14 = -0.12, no re-optimisation)
g = [1.0, 1.1088, 1.3062, 1.7704, 0.8181, 1.3554]
Mex = np.zeros((6, 6))
Mex[0, 1] = Mex[1, 0] = 1 / np.sqrt(g[0] * g[1]); Mex[4, 5] = Mex[5, 4] = 1 / np.sqrt(g[4] * g[5])
for i in range(1, 4):
    Mex[i, i + 1] = Mex[i + 1, i] = 1 / np.sqrt(g[i] * g[i + 1])
Mex[1, 4] = Mex[4, 1] = -0.12
e21, e11 = cm_resp(Mex, lam)
rip_ex = -20 * np.log10(abs(e21[inb]).min()); rl_ex = -20 * np.log10(abs(e11[inb]).max())
print(f"   Example 6 (inline values + M14 = -0.12): in-band RL {rl_ex:.1f} dB, ripple {rip_ex:.2f} dB; synthesised: RL {rl_in:.2f} dB, "
      f"ripple {il_rip:.3f} dB (M_S1 {MF[0,1]:.4f} vs {Mex[0,1]:.4f}, M12 {MF[1,2]:.4f} vs {Mex[1,2]:.4f}, M23 {MF[2,3]:.4f} vs {Mex[2,3]:.4f})")
for lx in (1.6, 3.0):
    i = np.argmin(abs(lam - lx))
    print(f"      rejection at lambda {lx}: synthesised {20*np.log10(abs(f21[i])):.1f} dB, Example 6 {20*np.log10(abs(e21[i])):.1f} dB")

# ================================================================ C. GNSS with an Iridium zero
print("C: GNSS 1559-1610 MHz preselector, N = 5, RL 20 dB, one TZ on Iridium 1621 MHz")
f1, f2 = 1559e6, 1610e6; f0 = np.sqrt(f1 * f2); FBW = (f2 - f1) / f0
lamf = lambda f: (f / f0 - f0 / f) / FBW
lz = lamf(1621e6)
synG = synth(5, 20.0, [lz]); MG, _ = fold(transversal(synG, 5))
synC = synth(5, 20.0, [])
MC, _ = fold(transversal(synC, 5))
print(f"   f0 {f0/1e6:.1f} MHz, FBW {100*FBW:.2f} %, Iridium 1616/1621/1626 MHz -> lambda {lamf(1616e6):.3f}/{lz:.3f}/{lamf(1626e6):.3f}")
print(f"   folded matrix: {fmt(MG)}")
fI = np.linspace(1616e6, 1626e6, 101)
res = {}
for Qu in (None, 3000, 1000, 500):
    q = None if Qu is None else FBW * Qu
    a21, _ = cm_resp(MG, lamf(fI), q); c21, _ = cm_resp(MC, lamf(fI), q)
    m21, _ = cm_resp(MG, [0.0], q); z21, _ = cm_resp(MG, [lz], q)
    il = -20 * np.log10(abs(m21[0]))
    rejG = -20 * np.log10(abs(a21).max()) - il; rejC = -20 * np.log10(abs(c21).max()) - il
    null = min(-20 * np.log10(abs(z21[0]) + 1e-300), 300.0) - il
    res[Qu] = (rejG, rejC, il, null)
    print(f"   Qu {'inf' if Qu is None else Qu:>5}: centre IL {il:5.2f} dB; worst rejection re mid-band over 1616-1626 MHz: "
          f"with TZ {rejG:5.1f} dB, all-pole N=5 {rejC:5.1f} dB; null depth at 1621 MHz {null:5.1f} dB")
check("C1 the Iridium TZ adds ~10 dB over the all-pole filter at the 1616 MHz edge; finite Qu fills the null and costs passband loss",
      res[None][0] - res[None][1] > 9 and res[None][3] > 100 and res[500][3] < 60 and res[500][2] > 1.0)

# ================================================================ D. linear phase
print("D: N = 6, RL 20 dB: Chebyshev vs a real-axis TZ pair (s = ±1.2, i.e. omega = ±j1.2) for group-delay flattening")
lamD = np.linspace(-1, 1, 2001); lamW = np.linspace(-3, 3, 3001)
syn0 = synth(6, 20.0, []); synL = synth(6, 20.0, [1.2j, -1.2j])
M0, _ = fold(transversal(syn0, 6)); ML, _ = fold(transversal(synL, 6))
gd = {}
for lab, Mx, syx in (("Chebyshev", M0, syn0), ("real-axis pair", ML, synL)):
    s21, _ = cm_resp(Mx, lamD); p21, _ = poly_resp(syx, lamD)
    gd_ = gdelay(s21, lamD)
    core = abs(lamD) <= 0.8
    var = (gd_[core].max() - gd_[core].min()) / gd_[core].mean()
    w21, _ = cm_resp(Mx, np.array([1.5, 2.0]))
    gd[lab] = (var, -20 * np.log10(abs(w21)))
    print(f"   {lab:15s}: group-delay variation over |lambda| ≤ 0.8 = {100*var:5.1f} % of mean; rejection at lambda 1.5/2.0 = "
          f"{gd[lab][1][0]:.1f}/{gd[lab][1][1]:.1f} dB; matrix vs polynomial {np.max(abs(abs(s21)-abs(p21))):.1e}")
print(f"      folded linear-phase matrix: {fmt(ML)}")
check("D1 real-axis TZ pair flattens the group delay (less than half the variation) and costs selectivity",
      gd["real-axis pair"][0] < 0.5 * gd["Chebyshev"][0] and gd["real-axis pair"][1][1] < gd["Chebyshev"][1][1]
      and np.sign(ML[2, 5]) == np.sign(ML[1, 2]))

# ================================================================ E. trisection
print("E: N = 3, RL 20 dB, one TZ at lambda = +2.5 (trisection)")
synT = synth(3, 20.0, [2.5]); MTr, _ = fold(transversal(synT, 3))
s21, _ = cm_resp(MTr, lamW); p21, _ = poly_resp(synT, lamW)
iz = np.argmin(abs(s21))
print(f"   folded = triplet: {fmt(MTr)}; TZ at lambda {lamW[iz]:+.3f}; matrix vs polynomial {np.max(abs(abs(s21)-abs(p21))):.1e}")
check("E1 folded N = 3 with one TZ is a trisection (M13 != 0, detuned resonators) with its zero where prescribed",
      abs(MTr[1, 3]) > 1e-3 and abs(lamW[iz] - 2.5) < 0.01 and abs(MTr[2, 2]) > 1e-3)

# ================================================================ F. extracted pole
print("F: extracted pole — resonator r (self-coupling -lambda_z) hung on a non-resonating node (NRN, susceptance B_N)")
rng = np.random.default_rng(5)
okF = True
for trial in range(5):
    lz_ = rng.uniform(1.3, 3.0); B = rng.uniform(-1, 1); Mr = rng.uniform(0.5, 1.5); MSN = rng.uniform(0.8, 1.5)
    # nodes: S, NRN, r, 1, 2, 3, L  (NRN is frequency-independent: no lambda on its diagonal)
    n = 7; M = np.zeros((n, n))
    M[0, 1] = MSN; M[1, 2] = Mr; M[2, 2] = -lz_; M[1, 1] = B
    M[1, 3] = 0.9; M[3, 4] = 0.8; M[4, 5] = 0.8; M[5, 6] = 1.0
    M = M + M.T - np.diag(np.diag(M))
    R = np.zeros((n, n)); R[0, 0] = R[-1, -1] = 1; W = np.eye(n); W[0, 0] = W[-1, -1] = W[1, 1] = 0
    ll = np.linspace(1.0, 3.5, 25001)
    s21 = np.array([-2j * np.linalg.inv(l * W - 1j * R + M)[-1, 0] for l in ll])
    lzf = ll[np.argmin(abs(s21))]
    okF &= abs(lzf - lz_) < 2e-4
    if trial < 2:
        print(f"   lambda_z {lz_:.4f} (B_N {B:+.2f}, M_Nr {Mr:.2f}): |S21| null found at {lzf:.4f}")
print("   the zero sits at the hung resonator's own frequency whatever the other couplings: the pole is 'extracted' and tuned alone")
check("F1 extracted-pole TZ location = resonator frequency, independent of the NRN and main filter", okF)

# ================================================================ G. SAW triple-transit echo
print("G: SAW triple-transit echo (TTE): H = H0 e^{-jωτ} (1 + a e^{-j2ωτ})")
v = 3158.0                                           # ST-quartz Rayleigh velocity (m/s), typical
for Lc, a_db in ((3.16e-3, -30), (3.16e-3, -40), (1.0e-3, -30)):
    tau = Lc / v; a = 10 ** (a_db / 20)
    f = np.linspace(433e6, 435e6, 200001); w = 2 * np.pi * f
    H = np.exp(-1j * w * tau) * (1 + a * np.exp(-2j * w * tau))
    amp = 20 * np.log10(abs(H)); ph = np.unwrap(np.angle(H)); gdl = -np.gradient(ph, w)
    rip_pp = amp.max() - amp.min(); gd_pp = gdl.max() - gdl.min()
    print(f"   centre-to-centre {Lc*1e3:.2f} mm (τ {tau*1e9:.0f} ns), TTE {a_db} dB: ripple period {1/(2*tau)/1e3:.0f} kHz, "
          f"amplitude ripple {rip_pp:.3f} dB p-p (theory {20*np.log10((1+a)/(1-a)):.3f}), group-delay ripple {gd_pp*1e9:.1f} ns p-p "
          f"(≈ 4 τ a = {4*tau*a*1e9:.1f} ns)")
    if Lc == 3.16e-3 and a_db == -30:
        okG = abs(rip_pp - 20 * np.log10((1 + a) / (1 - a))) < 0.01 and abs(gd_pp - 4 * tau * a) / (4 * tau * a) < 0.1
check("G1 TTE ripple: period 1/(2τ), amplitude 20log((1+a)/(1-a)) p-p, delay ripple ≈ 4τa p-p", okG)

# ================================================================ H. YIG
print("H: YIG sphere (uniform-precession mode, internal demagnetisation cancels for a sphere)")
gam = 28.0e9                                          # Hz/T  (2.8 MHz/Oe)
for fz in (2e9, 8e9, 18e9):
    print(f"   f {fz/1e9:4.0f} GHz -> bias field mu0 H0 = {fz/gam*1e3:.0f} mT ({fz/gam*1e4:.0f} Oe)")
for lab, Ms_G in (("pure YIG", 1780.0), ("Ga-doped YIG", 600.0)):
    fmin = 2.8e6 * Ms_G / 3
    print(f"   {lab}: 4πMs {Ms_G:.0f} G -> lowest frequency with a saturated sphere ≈ γ·4πMs/3 = {fmin/1e9:.2f} GHz")
for dH in (0.3, 0.5, 1.0):
    print(f"   linewidth ΔH {dH} Oe: unloaded Q ≈ f/(γ ΔH) = {10e9/(2.8e6*dH):.0f} at 10 GHz, {3e9/(2.8e6*dH):.0f} at 3 GHz")
check("H1 YIG: f/H = 28 GHz/T, pure-YIG low limit ≈ 1.66 GHz", abs(2.8e6 * 1780 / 3 / 1e9 - 1.66) < 0.01 and abs(8e9 / gam - 0.2857) < 1e-3)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
sys.exit(0 if ok_all else 1)
