#!/usr/bin/env python3
# Runtime (W6-F5, 2026-10-14): ~606 s (10.1 min) measured on a 10-core Apple-silicon Mac, run 3 at a time
# under load average 7-70 from other jobs; expect less on an idle machine. It exceeds the 120 s per-script budget
# used by the D7 verify sweep, so give it a >= 15 min timeout and run it with `python3 -u` to see progress.
# Measured run: exit 0, no FAIL lines. Comment only; no code or results changed.
"""Verification for kb/06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md

 A. Richards' transformation and the Kuroda identity (derived form) checked with ABCD matrices
 B. Quasi-static 2-D finite-difference Laplace solver for (coupled) microstrip; validated against
    Hammerstad-Jensen (scikit-rf MLine) and used to check Garg-Bahl coupled-line formulas
 C. Stepped-impedance microstrip LPF, fc = 3 GHz, on 0.8 mm FR-4 (skrf MLine incl. dispersion + loss)
 D. Parallel-coupled-line BPF at 2.45 GHz: J-inverter design (Z0e, Z0o), ideal-TEM response,
    physical widths/gaps (Garg-Bahl), and the effect of unequal even/odd phase velocity
 E. Coupled-resonator (Hong & Lancaster) method: k and Qe from g-values; coupling-coefficient extraction
    from split resonances; Qe from reflection group delay; 433 MHz top-C-coupled 3-pole LC BPF
 F. Finite-Q insertion loss (Cohn's formula) vs simulation; why a 1.7 MHz-wide 433 MHz LC filter is impossible
 G. General coupling-matrix response; inline Chebyshev = prototype; cross-coupled quadruplet zeros
 H. Unloaded Q of resonator technologies: microstrip (FR-4 vs RO4350B), coaxial cavity, helical
Run: python3 tools/verify/rfckt_filters.py
"""
import numpy as np, sys
import skrf as rf
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.special import ellipk
from scipy.optimize import brentq, minimize

ok_all = True
c0 = 299792458.0
eps0 = 8.8541878128e-12
mu0 = 4e-7 * np.pi


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


def ue(Z, t):
    t = np.asarray(t, complex)
    k = 1 / np.sqrt(1 + t ** 2)
    M = np.zeros((len(t), 2, 2), complex)
    M[:, 0, 0] = k; M[:, 0, 1] = 1j * Z * t * k; M[:, 1, 0] = 1j * t / Z * k; M[:, 1, 1] = k
    return M


def ser(Z):
    Z = np.atleast_1d(Z).astype(complex)
    M = np.tile(np.eye(2, dtype=complex), (len(Z), 1, 1)); M[:, 0, 1] = Z
    return M


def shu(Y):
    Y = np.atleast_1d(Y).astype(complex)
    M = np.tile(np.eye(2, dtype=complex), (len(Y), 1, 1)); M[:, 1, 0] = Y
    return M


def s21_of(M, Z0=50.0):
    a, b, c, d = M[:, 0, 0], M[:, 0, 1], M[:, 1, 0], M[:, 1, 1]
    return 2 / (a + b / Z0 + c * Z0 + d)


def s11_of(M, Z0=50.0):
    a, b, c, d = M[:, 0, 0], M[:, 0, 1], M[:, 1, 0], M[:, 1, 1]
    return (a + b / Z0 - c * Z0 - d) / (a + b / Z0 + c * Z0 + d)


def chain(*Ms):
    out = Ms[0]
    for M in Ms[1:]:
        out = out @ M
    return out


def g_cheb(N, rip):
    beta = np.log(1 / np.tanh(rip / (40 / np.log(10))))
    gam = np.sinh(beta / (2 * N))
    a = [np.sin((2 * k - 1) * np.pi / (2 * N)) for k in range(1, N + 1)]
    b = [gam ** 2 + np.sin(k * np.pi / N) ** 2 for k in range(1, N + 1)]
    g = [1.0, 2 * a[0] / gam]
    for k in range(2, N + 1):
        g.append(4 * a[k - 2] * a[k - 1] / (b[k - 2] * g[-1]))
    g.append(1.0 if N % 2 else 1 / np.tanh(beta / 4) ** 2)
    return np.array(g)


# ---------------------------------------------------------------- A. Richards / Kuroda
t = np.tan(np.linspace(0.05, 1.4, 50))
Za, Zb = 70.0, 40.0
left = chain(ser(1j * Za * t), ue(Zb, t))                              # series short stub Za, then UE Zb
right = chain(ue(Za + Zb, t), shu(1j * t / (Zb * (Za + Zb) / Za)))     # UE (Za+Zb), then shunt open stub
check("A1 Kuroda: series stub Za + UE Zb == UE (Za+Zb) + shunt stub Zb(Za+Zb)/Za", np.allclose(left, right))
# Richards: an inductor L at cutoff wc maps to a short stub of Z = wc L (lambda/8 at wc)
wc = 2 * np.pi * 3e9; L = 3e-9
f = np.linspace(0.3e9, 2.9e9, 20)
Zlump = 1j * 2 * np.pi * f * L
Zstub = 1j * wc * L * np.tan(np.pi / 4 * f / 3e9)
err = np.max(abs(Zstub - Zlump) / abs(Zlump))
print(f"A: Richards stub vs inductor below cutoff: max deviation {err*100:.1f} % (exact at fc, stub is periodic)")
check("A2 Richards stub equals the lumped reactance at f = fc", np.isclose(1j * wc * L * np.tan(np.pi / 4), 1j * wc * L))


# ---------------------------------------------------------------- B. 2-D FD Laplace microstrip solver
def fd_microstrip(ws, gap, h, er, box_w=None, box_h=None, d=None, volts=(1.0,)):
    """Zero-thickness strips on a substrate (height h, eps er) over ground. Returns charge per strip (C/m)
    for the given strip voltages; ws = width of each strip (list, 1 or 2 strips), gap between them."""
    ws = list(ws)
    tot = sum(ws) + (gap if len(ws) == 2 else 0)
    d = d or min(h, min(ws)) / 32
    box_w = box_w or tot + 30 * h
    box_h = box_h or 20 * h
    nx, ny = int(round(box_w / d)) + 1, int(round(box_h / d)) + 1
    x = np.linspace(-box_w / 2, box_w / 2, nx); y = np.linspace(0, box_h, ny)
    jh = int(round(h / d))
    # strip masks on row jh
    fixed = np.zeros((ny, nx), bool); V = np.zeros((ny, nx))
    fixed[0, :] = fixed[-1, :] = True; fixed[:, 0] = fixed[:, -1] = True
    x0 = -tot / 2
    strips = []
    for k, w in enumerate(ws):
        xs = x0 if k == 0 else x0 + ws[0] + gap
        m = (x >= xs - 1e-12) & (x <= xs + w + 1e-12)
        strips.append(m)
        fixed[jh, m] = True
        V[jh, m] = volts[k]
    # permittivity per cell (cell (j,i) between nodes j..j+1, i..i+1)
    epc = np.ones((ny - 1, nx - 1)); epc[:jh, :] = er
    idx = -np.ones((ny, nx), int); free = ~fixed
    idx[free] = np.arange(free.sum())
    rows, cols, vals = [], [], []; rhs = np.zeros(free.sum())
    J, I = np.nonzero(free)
    for j, i in zip(J, I):
        # coefficient for each neighbour = average permittivity of the two cells adjacent to that link
        eE = 0.5 * (epc[j - 1, i] + epc[j, i]); eW = 0.5 * (epc[j - 1, i - 1] + epc[j, i - 1])
        eN = 0.5 * (epc[j, i - 1] + epc[j, i]); eS = 0.5 * (epc[j - 1, i - 1] + epc[j - 1, i])
        p = idx[j, i]; diag = 0.0
        for (jj, ii, e) in ((j, i + 1, eE), (j, i - 1, eW), (j + 1, i, eN), (j - 1, i, eS)):
            diag += e
            if fixed[jj, ii]:
                rhs[p] += e * V[jj, ii]
            else:
                rows.append(p); cols.append(idx[jj, ii]); vals.append(-e)
        rows.append(p); cols.append(p); vals.append(diag)
    A = sp.csr_matrix((vals, (rows, cols)), shape=(free.sum(), free.sum()))
    V[free] = spla.spsolve(A, rhs)
    # charge on each strip: sum of eps*E over the links leaving the strip nodes (Gauss)
    Q = []
    for m in strips:
        q = 0.0
        for i in np.nonzero(m)[0]:
            j = jh
            for (jj, ii, e) in ((j + 1, i, 0.5 * (epc[j, i - 1] + epc[j, i])), (j - 1, i, 0.5 * (epc[j - 1, i - 1] + epc[j - 1, i]))):
                if not (m[ii] and jj == jh):
                    q += e * (V[j, i] - V[jj, ii])
            for ii in (i - 1, i + 1):
                if not m[ii]:
                    e = 0.5 * (epc[j - 1, min(i, ii)] + epc[j, min(i, ii)])
                    q += e * (V[j, i] - V[j, ii])
        Q.append(q * eps0)
    return Q


def fd_z0(w, h, er, **kw):
    C = fd_microstrip([w], 0, h, er, **kw)[0]
    Ca = fd_microstrip([w], 0, h, 1.0, **kw)[0]
    return 1 / (c0 * np.sqrt(C * Ca)), C / Ca


def fd_coupled(w, s, h, er, **kw):
    Ce = fd_microstrip([w, w], s, h, er, volts=(1, 1), **kw)[0]
    Cea = fd_microstrip([w, w], s, h, 1.0, volts=(1, 1), **kw)[0]
    Co = fd_microstrip([w, w], s, h, er, volts=(1, -1), **kw)[0]
    Coa = fd_microstrip([w, w], s, h, 1.0, volts=(1, -1), **kw)[0]
    return 1 / (c0 * np.sqrt(Ce * Cea)), 1 / (c0 * np.sqrt(Co * Coa)), Ce / Cea, Co / Coa


def hj_z0(w, h, er):
    """Hammerstad-Jensen static (zero thickness)."""
    u = w / h
    a = 1 + np.log((u ** 4 + (u / 52) ** 2) / (u ** 4 + 0.432)) / 49 + np.log(1 + (u / 18.1) ** 3) / 18.7
    b = 0.564 * ((er - 0.9) / (er + 3)) ** 0.053
    ee = (er + 1) / 2 + (er - 1) / 2 * (1 + 10 / u) ** (-a * b)
    fu = 6 + (2 * np.pi - 6) * np.exp(-(30.666 / u) ** 0.7528)
    z01 = 60 * np.log(fu / u + np.sqrt(1 + (2 / u) ** 2))
    return z01 / np.sqrt(ee), ee


def garg_bahl(w, s, h, er):
    """Garg & Bahl (1979) static even/odd impedances of coupled microstrip (zero thickness)."""
    z0, ee = hj_z0(w, h, er)
    z0a, _ = hj_z0(w, h, 1.0)
    def caps(er_, z0_, ee_):
        Cp = eps0 * er_ * w / h
        Cf = 0.5 * (np.sqrt(ee_) / (c0 * z0_) - Cp)
        A = np.exp(-0.1 * np.exp(2.33 - 2.53 * w / h))
        Cf2 = Cf / (1 + A * (h / s) * np.tanh(8 * s / h)) * np.sqrt(er_ / ee_)
        k = (s / h) / (s / h + 2 * w / h); kp = np.sqrt(1 - k ** 2)
        # K(k')/K(k) with scipy's parameter m = k^2
        Cga = eps0 * ellipk(kp ** 2) / ellipk(k ** 2)
        Cgd = eps0 * er_ / np.pi * np.log(1 / np.tanh(np.pi * s / (4 * h))) + 0.65 * Cf * (0.02 * np.sqrt(er_) / (s / h) + 1 - 1 / er_ ** 2)
        return Cp + Cf + Cf2, Cp + Cf + Cga + Cgd
    Ce, Co = caps(er, z0, ee)
    Cea, Coa = caps(1.0, z0a, 1.0)
    return 1 / (c0 * np.sqrt(Ce * Cea)), 1 / (c0 * np.sqrt(Co * Coa)), Ce / Cea, Co / Coa


h, er = 0.8e-3, 4.4
print("B: single microstrip, h 0.8 mm, er 4.4:   W(mm)  Z0 FD   Z0 H-J   eeff FD  eeff H-J")
worst = 0
for w in (0.3e-3, 1.5e-3, 5.0e-3):
    zf, ef = fd_z0(w, h, er)
    zh, eh = hj_z0(w, h, er)
    worst = max(worst, abs(zf / zh - 1))
    print(f"                                          {w*1e3:4.1f}   {zf:6.2f}  {zh:6.2f}   {ef:6.3f}   {eh:6.3f}")
check(f"B1 FD Laplace solver agrees with Hammerstad-Jensen within 1.5 % (max {worst*100:.1f} %)", worst < 0.015)
print("   coupled microstrip:  W, S (mm) | Z0e FD / G-B | Z0o FD / G-B | ee_e FD/G-B | ee_o FD/G-B")
worst = 0
for w, s in ((1.2e-3, 0.2e-3), (1.4e-3, 0.6e-3), (1.5e-3, 1.5e-3)):
    fe, fo, fee, feo = fd_coupled(w, s, h, er)
    ge, go, gee, geo = garg_bahl(w, s, h, er)
    worst = max(worst, abs(fe / ge - 1), abs(fo / go - 1))
    print(f"                        {w*1e3:.1f}, {s*1e3:.1f}  | {fe:6.2f}/{ge:6.2f} | {fo:6.2f}/{go:6.2f} | "
          f"{fee:.3f}/{gee:.3f} | {feo:.3f}/{geo:.3f}")
check(f"B2 Garg-Bahl coupled-line formulas agree with FD solver within 5 % (max {worst*100:.1f} %)", worst < 0.05)

# ---------------------------------------------------------------- C. stepped-impedance LPF
fc = 3.0e9
g = g_cheb(7, 0.1)
Zh, Zl, Z0 = 110.0, 20.0, 50.0


def width_for(Z, h, er):
    return brentq(lambda w: hj_z0(w, h, er)[0] - Z, 1e-5, 50e-3)


wH, wL, w50 = width_for(Zh, h, er), width_for(Zl, h, er), width_for(Z0, h, er)
fr = rf.Frequency(0.3, 9, 871, unit='GHz')
def mline(w, tand=0.02):
    return rf.media.MLine(frequency=fr, w=w, h=h, t=35e-6, ep_r=er, tand=tand, rho=1.72e-8, rough=0.5e-6,
                          z0_port=50, disp='kirschningjansen', diel='djordjevicsvensson', f_epr_tand=1e9)
mH, mL = mline(wH), mline(wL)
beta_c = lambda m: np.interp(fc, fr.f, m.beta)          # rad/m at fc (dispersive)
lens = []
ntw = None
for k, gk in enumerate(g[1:-1]):
    if k % 2 == 0:   # shunt C first (low-Z line)
        bl = gk * Zl / Z0
        l = bl / beta_c(mL); el = mL.line(l, 'm')
    else:            # series L (high-Z line)
        bl = gk * Z0 / Zh
        l = bl / beta_c(mH); el = mH.line(l, 'm')
    lens.append(l)
    ntw = el if ntw is None else ntw ** el
ntw_ideal_loss = ntw
# lossless version
mH0, mL0 = mline(wH, 0), mline(wL, 0)
s21 = 20 * np.log10(abs(ntw.s[:, 1, 0]))
at = lambda F: s21[np.argmin(abs(fr.f - F))]
print(f"C: 7-pole 0.1 dB Chebyshev stepped-impedance LPF fc 3 GHz on 0.8 mm FR-4: W(110 ohm) = {wH*1e3:.2f} mm, "
      f"W(20 ohm) = {wL*1e3:.2f} mm, W(50) = {w50*1e3:.2f} mm")
print("   section lengths (mm):", np.round(np.array(lens) * 1e3, 2), f"total {sum(lens)*1e3:.1f} mm")
print(f"   |S21|: 2.45 GHz {at(2.45e9):.2f} dB, 3.0 GHz {at(3.0e9):.2f} dB, 4.9 GHz {at(4.9e9):.1f} dB, "
      f"7.35 GHz {at(7.35e9):.1f} dB; min |S21| 5-9 GHz {s21[fr.f>5e9].min():.1f}/max {s21[fr.f>5e9].max():.1f} dB")
# lumped prototype at the same fc for comparison
f_ = fr.f; w_ = 2 * np.pi * f_
Ml = None
for k, gk in enumerate(g[1:-1]):
    el = shu(1j * w_ * gk / (Z0 * 2 * np.pi * fc)) if k % 2 == 0 else ser(1j * w_ * gk * Z0 / (2 * np.pi * fc))
    Ml = el if Ml is None else Ml @ el
s21l = 20 * np.log10(abs(s21_of(Ml)))
print(f"   lumped prototype: 4.9 GHz {s21l[np.argmin(abs(f_-4.9e9))]:.1f} dB (stepped-impedance gives less "
      f"stopband: the short lines only approximate L and C)")
ntw0 = None
for k, l in enumerate(lens):
    el = (mL0 if k % 2 == 0 else mH0).line(l, 'm')
    ntw0 = el if ntw0 is None else ntw0 ** el
s21_0 = 20 * np.log10(abs(ntw0.s[:, 1, 0]))
print(f"   lossless version: 2.45 GHz {s21_0[np.argmin(abs(fr.f-2.45e9))]:.2f} dB -> FR-4 dielectric/conductor loss "
      f"costs {s21_0[np.argmin(abs(fr.f-2.45e9))]-at(2.45e9):.2f} dB; -3 dB point {fr.f[np.argmax(s21_0 < -3)]/1e9:.2f} GHz (design fc 3.0)")
check("C1 stepped-impedance LPF passes 2.45 GHz with < 1 dB loss on FR-4", at(2.45e9) > -1.0)
check("C2 ...and rejects the 2nd harmonic (4.9 GHz) by > 25 dB", at(4.9e9) < -25)

# ---------------------------------------------------------------- D. coupled-line BPF
f0 = 2.45e9; FBW = 0.06; N = 3; rip = 0.5
gb = g_cheb(N, rip)
J = np.zeros(N + 1)
J[0] = np.sqrt(np.pi * FBW / (2 * gb[0] * gb[1]))
for k in range(1, N):
    J[k] = np.pi * FBW / (2 * np.sqrt(gb[k] * gb[k + 1]))
J[N] = np.sqrt(np.pi * FBW / (2 * gb[N] * gb[N + 1]))
Z0e = Z0 * (1 + J + J ** 2); Z0o = Z0 * (1 - J + J ** 2)
print(f"D: coupled-line BPF 2.45 GHz, N={N}, {rip} dB ripple, FBW {FBW}: g = {np.round(gb,4)}")
for k in range(N + 1):
    print(f"   section {k+1}: J*Z0 = {J[k]:.4f}, Z0e = {Z0e[k]:.2f} ohm, Z0o = {Z0o[k]:.2f} ohm")


def coupled_section(Ze, Zo, th_e, th_o):
    """ABCD of a coupled-line section with ports 1 and 4 used, ports 2,3 open (bandpass section).
    Built from even/odd modes: Z-matrix of 4-port then reduced.  th_e/th_o electrical lengths."""
    # open-circuit impedance parameters of the 4-port (Pozar 8.8 notation), generalised to th_e != th_o
    ze = -1j * Ze / np.tan(th_e); zo = -1j * Zo / np.tan(th_o)
    ze_s = -1j * Ze / np.sin(th_e); zo_s = -1j * Zo / np.sin(th_o)
    Z11 = 0.5 * (ze + zo); Z12 = 0.5 * (ze - zo); Z13 = 0.5 * (ze_s - zo_s); Z14 = 0.5 * (ze_s + zo_s)
    # two-port between port 1 and port 3 with 2 and 4 open (the "open-ended" BPF section):
    Za, Zb = Z11, Z13
    A = Za / Zb; B = (Za ** 2 - Zb ** 2) / Zb; C = 1 / Zb; D = Za / Zb
    M = np.zeros((len(np.atleast_1d(th_e)), 2, 2), complex)
    M[:, 0, 0] = A; M[:, 0, 1] = B; M[:, 1, 0] = C; M[:, 1, 1] = D
    return M


fb = np.linspace(1.5e9, 5.5e9, 2001)
th = np.pi / 2 * fb / f0
Mb = None
for k in range(N + 1):
    el = coupled_section(Z0e[k], Z0o[k], th, th)
    Mb = el if Mb is None else Mb @ el
S21b = 20 * np.log10(abs(s21_of(Mb))); S11b = 20 * np.log10(abs(s11_of(Mb)))
band = (fb > f0 * (1 - FBW / 2)) & (fb < f0 * (1 + FBW / 2))
print(f"   ideal TEM: passband ripple {-(S21b[band].min()):.2f} dB (design {rip}), worst S11 in band {S11b[band].max():.1f} dB, "
      f"|S21| at 2.2/2.7 GHz = {S21b[np.argmin(abs(fb-2.2e9))]:.1f}/{S21b[np.argmin(abs(fb-2.7e9))]:.1f} dB, "
      f"at 2f0 {S21b[np.argmin(abs(fb-2*f0))]:.1f} dB")
check("D1 ideal coupled-line BPF shows the designed ripple (within 0.15 dB)", abs(-S21b[band].min() - rip) < 0.15)
# physical dimensions from Garg-Bahl (solve w,s for each Z0e/Z0o)
dims = []
for k in range(N + 1):
    def res(p):
        w_, s_ = np.exp(p)
        ze, zo, _, _ = garg_bahl(w_, s_, h, er)
        return (ze - Z0e[k]) ** 2 + (zo - Z0o[k]) ** 2
    best = minimize(res, np.log([1.3e-3, 0.4e-3]), method='Nelder-Mead', options=dict(xatol=1e-8, fatol=1e-10, maxiter=4000))
    w_, s_ = np.exp(best.x)
    ze, zo, ee_e, ee_o = garg_bahl(w_, s_, h, er)
    le = c0 / (4 * f0 * np.sqrt((ee_e + ee_o) / 2))
    dims.append((w_, s_, le, ee_e, ee_o))
    print(f"   section {k+1}: W = {w_*1e3:.3f} mm, S = {s_*1e3:.3f} mm, eeff even/odd = {ee_e:.3f}/{ee_o:.3f}, "
          f"quarter-wave length (mean) = {le*1e3:.2f} mm")
# response with inhomogeneous (unequal) phase velocities
Mi = None
for k in range(N + 1):
    w_, s_, le, ee_e, ee_o = dims[k]
    th_e = 2 * np.pi * fb * np.sqrt(ee_e) / c0 * le
    th_o = 2 * np.pi * fb * np.sqrt(ee_o) / c0 * le
    el = coupled_section(Z0e[k], Z0o[k], th_e, th_o)
    Mi = el if Mi is None else Mi @ el
S21i = 20 * np.log10(abs(s21_of(Mi)))
fpk = fb[np.argmax(S21i[(fb < 3e9)])]
print(f"   with microstrip even/odd velocity difference: |S21| at 2f0 = {S21i[np.argmin(abs(fb-2*f0))]:.1f} dB "
      f"(ideal TEM {S21b[np.argmin(abs(fb-2*f0))]:.1f} dB) -> spurious 2f0 passband appears; centre ~ {fpk/1e9:.3f} GHz")
check("D2 unequal even/odd phase velocity creates a spurious response near 2f0 (> 20 dB worse)",
      S21i[np.argmin(abs(fb - 2 * f0))] > S21b[np.argmin(abs(fb - 2 * f0))] + 20)
check("D3 smallest gap is manufacturable at JLCPCB-class 0.1 mm rules", min(d[1] for d in dims) > 0.1e-3)

# ---------------------------------------------------------------- E. coupled-resonator method at 433 MHz
f0l = 433.92e6; w0 = 2 * np.pi * f0l; FBWl = 0.10; Nl = 3
gl = g_cheb(Nl, 0.1)
k12 = FBWl / np.sqrt(gl[1] * gl[2]); k23 = FBWl / np.sqrt(gl[2] * gl[3])
Qe1 = gl[0] * gl[1] / FBWl; Qe3 = gl[3] * gl[4] / FBWl
print(f"E: 433.92 MHz, 3-pole 0.1 dB Chebyshev, FBW {FBWl}: k12 = {k12:.4f}, k23 = {k23:.4f}, Qe = {Qe1:.3f}")
Lr = 22e-9
Ct = 1 / (w0 ** 2 * Lr)                                       # total node capacitance of each resonator
# coupling capacitors (series between resonator nodes): k ~ Cc/(Ct)   (Ct includes Cc loading)
Cc12 = k12 * Ct; Cc23 = k23 * Ct
# external coupling by a series capacitor Ce from 50 ohm: Qe = w0*Ct*Rp, Rp = R0*(1 + 1/(w0 Ce R0)^2)
R0 = 50.0
Rp_req = Qe1 / (w0 * Ct)
Ce = 1 / (w0 * R0 * np.sqrt(Rp_req / R0 - 1))
Cp_e = Ce / (1 + (w0 * Ce * R0) ** 2)                          # parallel-equivalent C of the series R0-Ce
C1 = Ct - Cp_e - Cc12; C2 = Ct - Cc12 - Cc23; C3 = Ct - Cc23 - Cp_e
print(f"   L = {Lr*1e9:.0f} nH each, node C total {Ct*1e12:.2f} pF; Cc12 = Cc23 = {Cc12*1e12:.2f} pF; "
      f"Ce = {Ce*1e12:.2f} pF (Rp {Rp_req:.0f} ohm); resonator C1 = C3 = {C1*1e12:.2f} pF, C2 = {C2*1e12:.2f} pF")


def lc_bpf(fq, QL=None, QC=None, vals=None):
    Ce_, Cc12_, Cc23_, C1_, C2_, C3_ = vals if vals is not None else (Ce, Cc12, Cc23, C1, C2, C3)
    w = 2 * np.pi * fq
    def zc(C):
        return 1 / (1j * w * C) + ((1 / (w * C)) / QC if QC else 0)
    def yres(C):
        zl = 1j * w * Lr + ((w * Lr) / QL if QL else 0)
        return 1 / zl + 1 / zc(C)
    return chain(ser(zc(Ce_)), shu(yres(C1_)), ser(zc(Cc12_)), shu(yres(C2_)), ser(zc(Cc23_)), shu(yres(C3_)), ser(zc(Ce_)))


fl = np.linspace(300e6, 600e6, 3001)
S21l = 20 * np.log10(abs(s21_of(lc_bpf(fl))))
bandl = (fl > f0l * (1 - FBWl / 2)) & (fl < f0l * (1 + FBWl / 2))
print(f"   first-cut (ideal parts): in-band min |S21| {S21l[bandl].min():.2f} dB; centre of -3 dB band "
      f"{np.mean(fl[S21l > -3])/1e6:.1f} MHz; -3 dB BW {np.ptp(fl[S21l > -3])/1e6:.1f} MHz")
check("E1 coupled-resonator first cut lands within 2 % of centre frequency", abs(np.mean(fl[S21l > -3]) / f0l - 1) < 0.02)
# coupling extraction from split resonances (even/odd of two identical resonators coupled by Cc)
fe_ = 1 / (2 * np.pi * np.sqrt(Lr * Ct)); fo_ = 1 / (2 * np.pi * np.sqrt(Lr * (Ct + Cc12)))
# (with node capacitance Ct - Cc (resonator) + Cc (coupling to grounded twin) in the even mode = Ct - Cc + 0?)
Cres = Ct - Cc12
fe_ = 1 / (2 * np.pi * np.sqrt(Lr * Cres))              # magnetic wall: Cc carries no current
fo_ = 1 / (2 * np.pi * np.sqrt(Lr * (Cres + 2 * Cc12)))  # electric wall: Cc -> 2Cc to ground
k_ext = (fe_ ** 2 - fo_ ** 2) / (fe_ ** 2 + fo_ ** 2)
print(f"   split-resonance extraction: f_even {fe_/1e6:.2f} MHz, f_odd {fo_/1e6:.2f} MHz -> k = {k_ext:.4f} "
      f"(exact Cc/(Cres+Cc) = {Cc12/(Cres+Cc12):.4f}; design k12 {k12:.4f})")
check("E2 split-resonance formula k = (fe^2-fo^2)/(fe^2+fo^2) equals Cc/(Cres+Cc)", abs(k_ext - Cc12 / (Cres + Cc12)) < 1e-12)
# Qe from S11 group delay of the singly loaded first resonator (other side open)
fg = np.linspace(f0l * 0.9, f0l * 1.1, 20001)
wg = 2 * np.pi * fg
Zin_q = 1 / (1j * wg * Ce) + 1 / (1 / (1j * wg * Lr) + 1j * wg * (Ct - Cp_e))   # far side open
S11q = (Zin_q - R0) / (Zin_q + R0)
ph = np.unwrap(np.angle(S11q)); tau = -np.gradient(ph, wg)
i0 = np.argmax(tau); Qe_gd = wg[i0] * tau[i0] / 4
print(f"   Qe from reflection group delay: {Qe_gd:.3f} (design {Qe1:.3f}) at {fg[i0]/1e6:.2f} MHz")
check("E3 Qe = w0*tau(w0)/4 recovers the design external Q (within 3 %)", abs(Qe_gd / Qe1 - 1) < 0.03)

# ---------------------------------------------------------------- F. finite-Q loss
for Qu in (40, 60, 100, 300):
    s = 20 * np.log10(abs(s21_of(lc_bpf(np.array([f0l]), QL=Qu, QC=1e9))))[0]
    cohn = 4.343 * gl[1:Nl + 1].sum() / (FBWl * Qu)
    print(f"F: Qu = {Qu:3d}: simulated mid-band IL {-s:.2f} dB, Cohn estimate 4.343*sum(g)/(FBW*Qu) = {cohn:.2f} dB")
s60 = -20 * np.log10(abs(s21_of(lc_bpf(np.array([f0l]), QL=60, QC=1e9))))[0]
check("F1 Cohn's loss formula within 25 % of simulation at Qu=60", abs(4.343 * gl[1:4].sum() / (0.1 * 60) / s60 - 1) < 0.25)
for fbw, Qu in ((1.74 / 433.92, 60), (1.74 / 433.92, 4000), (0.10, 60)):
    print(f"   FBW {fbw*100:5.2f} %, Qu {Qu:5d}: Cohn IL estimate {4.343*gl[1:4].sum()/(fbw*Qu):6.1f} dB")

# ---------------------------------------------------------------- G. coupling matrix
def cm_response(M, R1, Rn, lam):
    n = M.shape[0]
    R = np.zeros((n, n)); R[0, 0] = R1; R[-1, -1] = Rn
    S21 = np.zeros(len(lam), complex); S11 = np.zeros(len(lam), complex)
    for i, l in enumerate(lam):
        A = l * np.eye(n) - 1j * R + M
        Ai = np.linalg.inv(A)
        S21[i] = -2j * np.sqrt(R1 * Rn) * Ai[-1, 0]
        S11[i] = 1 + 2j * R1 * Ai[0, 0]
    return S21, S11


g4 = g_cheb(4, 0.1)
M4 = np.zeros((4, 4))
for i in range(3):
    M4[i, i + 1] = M4[i + 1, i] = 1 / np.sqrt(g4[i + 1] * g4[i + 2])
R1 = 1 / (g4[0] * g4[1]); Rn = 1 / (g4[4] * g4[5])
lam = np.linspace(-3, 3, 1201)
S21m, S11m = cm_response(M4, R1, Rn, lam)
eps = np.sqrt(10 ** (0.1 / 10) - 1)
T4 = np.cosh(4 * np.arccosh(np.abs(lam) + 0j)).real * np.where(abs(lam) <= 1, 1, 1)
T4 = np.where(abs(lam) <= 1, np.cos(4 * np.arccos(np.clip(lam, -1, 1))), np.cosh(4 * np.arccosh(np.maximum(abs(lam), 1))))
ref = 1 / (1 + eps ** 2 * T4 ** 2)
e_cm = np.max(abs(abs(S21m) ** 2 - ref))
print(f"G: inline 4-pole coupling matrix vs Chebyshev |S21|^2: max err {e_cm:.1e}; energy conservation err "
      f"{np.max(abs(abs(S21m)**2+abs(S11m)**2-1)):.1e}")
check("G1 inline coupling-matrix response equals the Chebyshev prototype", e_cm < 1e-9)
Mq4 = M4.copy(); Mq4[0, 3] = Mq4[3, 0] = -0.12            # negative cross coupling in a quadruplet
S21q, _ = cm_response(Mq4, R1, Rn, lam)
zs = lam[np.where((np.diff(np.sign(np.diff(abs(S21q)))) > 0))[0] + 1]
zs = zs[abs(zs) > 1.05]
print(f"   quadruplet with M14 = -0.12: |S21| minima (transmission zeros) near lambda = {np.round(zs,2)}; "
      f"rejection at lambda=+-1.6: {20*np.log10(abs(S21q[np.argmin(abs(lam-1.6))])):.1f} dB vs inline "
      f"{20*np.log10(abs(S21m[np.argmin(abs(lam-1.6))])):.1f} dB")
check("G2 negative cross-coupling creates a symmetric pair of transmission zeros", len(zs) >= 2 and np.isclose(zs.min(), -zs.max(), atol=0.02))

# ---------------------------------------------------------------- H. resonator Q
for name, w_, hh, er_, tand in (("FR-4 0.8 mm, 50 ohm", w50, 0.8e-3, 4.4, 0.02),
                                ("RO4350B 0.508 mm", None, 0.508e-3, 3.66, 0.0037)):
    if w_ is None:
        w_ = brentq(lambda w: hj_z0(w, hh, er_)[0] - 50, 1e-5, 20e-3)
    frq = rf.Frequency(2.45, 2.45, 1, unit='GHz')
    m = rf.media.MLine(frequency=frq, w=w_, h=hh, t=35e-6, ep_r=er_, tand=tand, rho=1.72e-8, rough=0.5e-6,
                       z0_port=50, f_epr_tand=1e9)
    gam = m.gamma[0]
    Qm = gam.imag / (2 * gam.real)
    print(f"H: microstrip lambda/2 resonator Qu at 2.45 GHz ({name}, W {w_*1e3:.2f} mm): {Qm:.0f}  (radiation not included)")
    if 'FR-4' in name:
        Q_fr4 = Qm
    else:
        Q_ro = Qm
# coaxial cavity (lambda/4, air, copper) at 433 MHz: Qc = beta / (2 alpha_c)
sig = 5.8e7; fq = 433.92e6
Rs = np.sqrt(np.pi * fq * mu0 / sig)
for b_, a_ in ((25e-3, 7e-3), (40e-3, 11e-3)):
    alpha = Rs * (1 / a_ + 1 / b_) / (2 * 376.73 * np.log(b_ / a_))
    Qc = (2 * np.pi * fq / c0) / (2 * alpha)
    print(f"   433 MHz coaxial cavity, outer radius {b_*1e3:.0f} mm / inner {a_*1e3:.0f} mm (b/a = {b_/a_:.2f}): "
          f"Qc ~ {Qc:.0f} (line loss only; end/short losses lower it)")
# helical resonator (Macalpine & Schildknecht empirical): Qu ~ 50 * S[inch] * sqrt(f[MHz])
for S_in in (0.5, 1.0):
    print(f"   helical resonator, shield {S_in} in: Qu ~ {50*S_in*np.sqrt(433.92):.0f} (empirical formula)")
check("H1 FR-4 microstrip resonator Q is dielectric-limited (< 60) and RO4350B is > 2x higher", Q_fr4 < 60 and Q_ro > 2 * Q_fr4)
print(f"   => 2.45 GHz coupled-line BPF (FBW 6 %) Cohn IL estimate: FR-4 {4.343*gb[1:4].sum()/(FBW*Q_fr4):.1f} dB, "
      f"RO4350B {4.343*gb[1:4].sum()/(FBW*Q_ro):.1f} dB")

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
sys.exit(0 if ok_all else 1)
