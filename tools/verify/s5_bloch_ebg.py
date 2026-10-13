#!/usr/bin/env python3
"""
s5_bloch_ebg.py — periodic structures: Floquet/Bloch analysis, slow-wave and Bragg lines, leaky-wave
scan, grounded-slab surface waves, mushroom EBG / AMC and CRLH lines.

Used by: kb/03-transmission-lines-matching/periodic-structures-ebg.md (task W5-S5, gap G-03-01).

Sections
  §1  Capacitively loaded line (symmetric cell: d/2 line, shunt C, d/2 line): cos(beta d) = (A+D)/2;
      ABCD eigenvalues = exp(+-gamma d); Bloch impedance Z_B = B/sqrt(A^2 - 1) terminates any number of
      cells reflectionlessly; light-loading slow-wave factor and Z_B; N-cell |S21| in the pass/stop band.
      Example: 50 ohm JLC 2-layer microstrip (eeff 3.40) loaded with 1 pF every 10 mm.
  §2  Bragg (stepped-impedance) line of quarter-wave Z1/Z2 sections: stop-band centre and fractional
      width (4/pi) asin(|Z1-Z2|/(Z1+Z2)) vs the Bloch condition; harmonic-suppression example.
  §3  Space harmonics and leaky-wave scan: beta_n = beta_0 + 2 pi n/p; sin(theta) = beta_-1/k0 for a
      periodic microstrip leaky-wave antenna at 5.8 GHz.
  §4  Grounded-slab surface waves (JLC 1.43 mm core, er 4.5): TM0 beta(f); horizontal-dipole surface-
      wave efficiency by an exact spectral (transverse-network) calculation vs the Jackson-Alexopoulos
      closed form; the 08/patch-antennas er = 10.8, h = 0.02 lambda case.
  §5  Mushroom (Sievenpiper) surface: L = mu0 h, C = w eps0 (1+er) acosh(a/g)/pi; f0, reflection
      phase, +-90 deg bandwidth vs sqrt(L/C)/eta0 (= k0 h at resonance); designs at 2.45 and 5.8 GHz on
      1.43 mm FR-4; exact grounded-slab impedance vs the jw mu0 h approximation.
  §6  CRLH (composite right/left-handed) line: dispersion, balanced condition closes the gap,
      backward-wave (left-handed) band, Bloch impedance at the transition.

Run:  python3 tools/verify/s5_bloch_ebg.py     (about 5 s)
"""
import numpy as np
from scipy import optimize
from scipy.special import roots_legendre

C0 = 299_792_458.0
MU0 = 1.25663706127e-6
EPS0 = 8.8541878188e-12
ETA0 = np.sqrt(MU0 / EPS0)
checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}  {detail}")


def tl_abcd(Z0, theta):
    return np.array([[np.cos(theta), 1j * Z0 * np.sin(theta)], [1j * np.sin(theta) / Z0, np.cos(theta)]])


def shunt(Y):
    return np.array([[1, 0], [Y, 1]], complex)


def s21_from_abcd(M, Z0=50.0):
    A, B, C, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
    return 2 / (A + B / Z0 + C * Z0 + D)


def zin(M, ZL):
    return (M[0, 0] * ZL + M[0, 1]) / (M[1, 0] * ZL + M[1, 1])


# ---------------------------------------------------------------- §1 loaded line
def loaded_cell(f, Z0, eeff, d, Cl):
    th = 2 * np.pi * f * np.sqrt(eeff) / C0 * d
    return tl_abcd(Z0, th / 2) @ shunt(1j * 2 * np.pi * f * Cl) @ tl_abcd(Z0, th / 2)


def part1():
    print("§1 capacitively loaded line (Bloch analysis)")
    Z0, eeff, d, Cl = 50.0, 3.40, 10e-3, 1e-12
    f = 433.92e6
    M = loaded_cell(f, Z0, eeff, d, Cl)
    A, B, D = M[0, 0], M[0, 1], M[1, 1]
    cosbd = (A + D) / 2
    th = 2 * np.pi * f * np.sqrt(eeff) / C0 * d
    bZ = 2 * np.pi * f * Cl * Z0
    check("cos(beta d) = (A+D)/2 = cos(theta) - (b/2) sin(theta), b = w C Z0", abs(cosbd - (np.cos(th) - bZ / 2 * np.sin(th))) < 1e-12)
    ev = np.linalg.eigvals(M)
    bd = np.arccos(cosbd.real)
    check("ABCD eigenvalues = exp(-+j beta d) (Floquet multipliers, |lambda| = 1 in a pass band)",
          np.allclose(sorted(np.angle(ev)), sorted([-bd, bd]), atol=1e-12) and np.allclose(np.abs(ev), 1, atol=1e-12))
    ZB = B / np.sqrt(A ** 2 - 1 + 0j)
    ZB = ZB if ZB.real > 0 else -ZB
    errs = []
    for N in (1, 3, 10, 37):
        MN = np.linalg.matrix_power(M, N)
        errs.append(abs(zin(MN, ZB) / ZB - 1))
    check("Z_B = B/sqrt(A^2-1) terminates 1, 3, 10, 37 cells with Zin = Z_B", max(errs) < 1e-10, f"Z_B = {ZB.real:.3f} ohm")
    # light-loading (quasi-static) approximation
    Cp = np.sqrt(eeff) / (C0 * Z0)                 # line capacitance per metre
    sw = np.sqrt(1 + Cl / (Cp * d))
    ZB_ls = Z0 / sw
    sw_exact = bd / th
    print(f"     433.92 MHz: theta = {np.degrees(th):.2f} deg/cell, beta d = {np.degrees(bd):.2f} deg;"
          f" slow-wave factor {sw_exact:.4f} (light-loading {sw:.4f}); Z_B {ZB.real:.2f} ohm (light-loading {ZB_ls:.2f})")
    check("light-loading formulas sqrt(1 + C/(C'd)) and Z0/sqrt(...) within 0.5 % at 433 MHz",
          abs(sw_exact / sw - 1) < 5e-3 and abs(ZB.real / ZB_ls - 1) < 5e-3)
    # first stop band
    fs = np.linspace(0.1e9, 20e9, 40000)
    cb = np.array([np.real(np.trace(loaded_cell(ff, Z0, eeff, d, Cl))) / 2 for ff in fs])
    stop = np.abs(cb) > 1
    edges = fs[np.where(np.diff(stop.astype(int)) != 0)[0]]
    print(f"     first stop band {edges[0]/1e9:.3f}-{edges[1]/1e9:.3f} GHz (unloaded Bragg frequency c/(2 d sqrt(eeff)) = "
          f"{C0/(2*d*np.sqrt(eeff))/1e9:.3f} GHz)")
    # N-cell transmission
    s21_pass = abs(s21_from_abcd(np.linalg.matrix_power(loaded_cell(1e9, Z0, eeff, d, Cl), 20)))
    fmid = 0.5 * (edges[0] + edges[1])
    s21_stop = abs(s21_from_abcd(np.linalg.matrix_power(loaded_cell(fmid, Z0, eeff, d, Cl), 20)))
    Mmid = loaded_cell(fmid, Z0, eeff, d, Cl)
    alpha_d = np.arccosh(abs(np.real(np.trace(Mmid)) / 2))
    print(f"     20 cells: |S21| at 1 GHz {20*np.log10(s21_pass):.2f} dB; at {fmid/1e9:.2f} GHz {20*np.log10(s21_stop):.1f} dB"
          f" (Bloch attenuation 20 x {alpha_d*8.686:.2f} = {20*alpha_d*8.686:.1f} dB)")
    s21_10 = abs(s21_from_abcd(np.linalg.matrix_power(Mmid, 10)))
    slope = 20 * np.log10(s21_10 / s21_stop) / 10
    print(f"     stop-band slope from 10 -> 20 cells: {slope:.3f} dB/cell vs alpha d = {alpha_d*8.686:.3f} dB/cell"
          f" (the constant offset {(-20*np.log10(s21_stop) - 20*alpha_d*8.686):+.1f} dB is the end mismatch to 50 ohm)")
    check("stop-band |S21| falls by alpha*d per added cell (Bloch attenuation), within 0.01 dB/cell",
          abs(slope - alpha_d * 8.686) < 0.01)
    return dict(ZB=ZB.real, sw=sw_exact, edges=edges)


# ---------------------------------------------------------------- §2 Bragg line
def part2():
    print("§2 Bragg (stepped-impedance) line")
    Z1, Z2, f0, eeff = 30.0, 80.0, 1.0e9, 3.40
    lam_g = C0 / (f0 * np.sqrt(eeff))
    def cell(f):
        th = np.pi / 2 * f / f0
        return tl_abcd(Z1, th) @ tl_abcd(Z2, th)
    fs = np.linspace(0.3e9, 1.7e9, 140001)
    cb = np.array([np.real(np.trace(cell(ff))) / 2 for ff in fs])
    stop = np.abs(cb) > 1
    idx = np.where(np.diff(stop.astype(int)) != 0)[0]
    lo, hi = fs[idx[0]], fs[idx[1]]
    fbw = (hi - lo) / f0
    pred = 4 / np.pi * np.arcsin(abs(Z1 - Z2) / (Z1 + Z2))
    print(f"     30/80 ohm quarter-wave cells at 1 GHz: stop band {lo/1e9:.4f}-{hi/1e9:.4f} GHz, FBW {fbw:.4f}; formula {pred:.4f}")
    check("Bragg stop-band FBW = (4/pi) asin(|Z1-Z2|/(Z1+Z2))", abs(fbw / pred - 1) < 1e-3)
    s = abs(s21_from_abcd(np.linalg.matrix_power(cell(f0), 6)))
    print(f"     6 cells ({6*lam_g/2*1e3:.0f} mm of line on eeff 3.40): |S21(f0)| = {20*np.log10(s):.1f} dB")
    return dict(fbw=fbw, s6=20 * np.log10(s))


# ---------------------------------------------------------------- §3 leaky-wave scan
def part3():
    print("§3 space harmonics and leaky-wave scan")
    eeff = 3.40
    f0 = 5.8e9
    lam0 = C0 / f0
    p = lam0 / np.sqrt(eeff)            # broadside at f0 (beta_-1 = 0)
    rows = []
    for f in [5.4e9, 5.6e9, 5.8e9, 6.0e9, 6.2e9]:
        k0 = 2 * np.pi * f / C0
        b0 = k0 * np.sqrt(eeff)
        bm1 = b0 - 2 * np.pi / p
        s = bm1 / k0
        rows.append((f, np.degrees(np.arcsin(s)) if abs(s) <= 1 else np.nan))
    print(f"     period for broadside at 5.8 GHz: p = lambda_g = {p*1e3:.2f} mm;  theta(f): " +
          ", ".join(f"{f/1e9:.1f} GHz {th:+.1f} deg" for f, th in rows))
    # frequency scan rate near broadside: d theta/df = sqrt(eeff)/(f0 cos 0) rad per unit df/f0 -> deg per 100 MHz
    rate = np.degrees(np.sqrt(eeff) * 0.1e9 / f0)
    check("scan rate near broadside = sqrt(eeff) * (df/f0) rad (about 1.8 deg per 100 MHz)",
          abs((rows[3][1] - rows[2][1]) / 2 - rate) < 0.1, f"{rate:.2f} deg/100 MHz")
    return dict(p=p, rows=rows)


# ---------------------------------------------------------------- §4 surface waves
def tm0_beta(f, h, er):
    k0 = 2 * np.pi * f / C0
    fn = lambda b: np.sqrt(er * k0 ** 2 - b ** 2) * np.tan(np.sqrt(er * k0 ** 2 - b ** 2) * h) - er * np.sqrt(b ** 2 - k0 ** 2)
    lo = k0 * (1 + 1e-13)
    if er * k0 ** 2 > (np.pi / (2 * h)) ** 2:
        lo = max(lo, np.sqrt(er * k0 ** 2 - (np.pi / (2 * h)) ** 2) * (1 + 1e-12))
    return optimize.brentq(fn, lo, k0 * np.sqrt(er) * (1 - 1e-13), xtol=1e-15 * k0)


def hed_powers(f, h, er, n=2000):
    """Space-wave and TM0 surface-wave power of a horizontal electric dipole on top of a grounded slab
    (unit Il), from P = (1/8pi) Re int k_rho (V_TM + V_TE) dk_rho (transverse equivalent network)."""
    w = 2 * np.pi * f
    k0 = w / C0

    def V(kr):
        kz0 = np.sqrt(k0 ** 2 - kr ** 2 + 0j)
        kz0 = np.where(kz0.imag > 0, -kz0, kz0)
        kz1 = np.sqrt(er * k0 ** 2 - kr ** 2 + 0j)
        Yu_tm, Yu_te = w * EPS0 / kz0, kz0 / (w * MU0)
        Z1_tm, Z1_te = kz1 / (w * EPS0 * er), w * MU0 / kz1
        t = np.tan(kz1 * h)
        Yd_tm, Yd_te = 1 / (1j * Z1_tm * t), 1 / (1j * Z1_te * t)
        return 1 / (Yu_tm + Yd_tm), 1 / (Yu_te + Yd_te)

    x, wx = roots_legendre(n)
    tt = (x + 1) * np.pi / 4
    wt = wx * np.pi / 4
    kr = k0 * np.sin(tt)
    Vtm, Vte = V(kr)
    Psp = (1 / (8 * np.pi)) * np.sum(wt * k0 * np.cos(tt) * kr * np.real(Vtm + Vte))
    beta = tm0_beta(f, h, er)

    def B(kr_):                       # Y_TM(kr) = j B(kr) for k0 < kr < sqrt(er) k0
        kz0 = -1j * np.sqrt(kr_ ** 2 - k0 ** 2)
        kz1 = np.sqrt(er * k0 ** 2 - kr_ ** 2)
        Y = w * EPS0 / kz0 + 1 / (1j * kz1 / (w * EPS0 * er) * np.tan(kz1 * h))
        return (Y / 1j).real
    dk = (beta - k0) * 1e-3          # well inside the gap between the pole and the branch point
    dB = (B(beta + dk) - B(beta - dk)) / (2 * dk)
    Psw = (1 / (8 * np.pi)) * np.pi * beta / abs(dB)
    return Psp, Psw, beta / k0


def ja_ratio(f, h, er):
    k0h = 2 * np.pi * f / C0 * h
    n2 = er
    c1 = 1 - 1 / n2 + 2 / (5 * n2 ** 2)
    return 0.75 * np.pi * k0h * (1 - 1 / n2) ** 3 / c1          # P_sw / P_sp (HED, thin substrate)


def part4():
    print("§4 grounded-slab surface waves")
    h, er = 1.43e-3, 4.5
    # free-space normalisation check of the spectral power formula: unit Il radiates eta k^2/(12 pi)
    k = 2 * np.pi * 1e9 / C0
    x, wx = roots_legendre(4000)
    tt = (x + 1) * np.pi / 4
    wt = wx * np.pi / 4
    kr = k * np.sin(tt)
    kz = k * np.cos(tt)
    w = 2 * np.pi * 1e9
    Vtm = 0.5 * kz / (w * EPS0)
    Vte = 0.5 * w * MU0 / kz
    P = (1 / (8 * np.pi)) * np.sum(wt * k * np.cos(tt) * kr * (Vtm + Vte))
    check("spectral power formula reproduces the free-space dipole power eta k^2/(12 pi)", abs(P / (ETA0 * k ** 2 / (12 * np.pi)) - 1) < 1e-9)
    rows = []
    for f in [433.92e6, 915e6, 2.45e9, 5.8e9, 10e9]:
        Psp, Psw, bk = hed_powers(f, h, er)
        e_ex = Psp / (Psp + Psw)
        e_ja = 1 / (1 + ja_ratio(f, h, er))
        rows.append((f, bk, e_ex, e_ja))
        print(f"     {f/1e9:6.3f} GHz (h/lam0 = {h*f/C0:.4f}): TM0 beta/k0 {bk:.6f}; HED space-wave efficiency exact {e_ex*100:.2f} %,"
              f" Jackson-Alexopoulos {e_ja*100:.2f} %")
    # The first version of this check (written before running) also demanded <= 3 points up to 10 GHz;
    # it FAILED there (J-A 70.6 % vs exact 65.0 % at h/lam0 = 0.048): J-A is a thin-substrate formula.
    ok = all(abs(r[2] - r[3]) < 0.01 for r in rows if r[0] <= 2.45e9)
    check("J-A closed form within 1 point of the exact HED efficiency for h/lam0 <= 0.012 (1.43 mm FR-4 to 2.45 GHz)", ok,
          "errors " + ", ".join(f"{(r[3]-r[2])*100:+.2f}" for r in rows) + " points")
    # thin-substrate limit: ratio of surface- to space-wave power -> J-A as h -> 0
    rat = []
    for hh in [0.4e-3, 0.1e-3, 0.025e-3]:
        Psp, Psw, _ = hed_powers(2.45e9, hh, er)
        rat.append((Psw / Psp) / ja_ratio(2.45e9, hh, er))
    check("P_sw/P_sp (exact) / J-A -> 1 as h -> 0 (0.4, 0.1, 0.025 mm)", abs(rat[-1] - 1) < 2e-3 and abs(rat[-1] - 1) < abs(rat[0] - 1),
          ", ".join(f"{x:.4f}" for x in rat))
    # the 08/patch case: er 10.8, h = 0.02 lambda0
    f = 2.45e9
    hh = 0.02 * C0 / f
    Psp, Psw, _ = hed_powers(f, hh, 10.8)
    e_ex = Psp / (Psp + Psw)
    print(f"     er 10.8, h = 0.02 lam0: exact e_sw = {e_ex*100:.1f} %, J-A {100/(1+ja_ratio(f, hh, 10.8)):.1f} % (08/patch page: ~80 %)")
    check("er 10.8, h = 0.02 lam0 -> about 20 % of the HED power in surface waves (08/patch page)", 0.75 < e_ex < 0.85,
          f"{(1-e_ex)*100:.1f} %")
    return rows


# ---------------------------------------------------------------- §5 mushroom EBG
def mushroom(f, a, g, h, er, exact_slab=True):
    w_ = 2 * np.pi * f
    wpatch = a - g
    C = wpatch * EPS0 * (1 + er) / np.pi * np.arccosh(a / g)
    if exact_slab:
        kd = w_ * np.sqrt(er) / C0
        Zslab = 1j * ETA0 / np.sqrt(er) * np.tan(kd * h)       # shorted dielectric line, normal incidence
    else:
        Zslab = 1j * w_ * MU0 * h
    Zc = 1 / (1j * w_ * C)
    Zs = Zslab * Zc / (Zslab + Zc)
    G = (Zs - ETA0) / (Zs + ETA0)
    return G, C


def design_mushroom(f0, h, er, ratio_ag=20.0):
    L = MU0 * h
    C = 1 / ((2 * np.pi * f0) ** 2 * L)
    # w acosh(a/g) eps0 (1+er)/pi = C with a = w + g, a/g = ratio
    w = C * np.pi / (EPS0 * (1 + er) * np.arccosh(ratio_ag))
    g = w / (ratio_ag - 1)
    return w + g, g, L, C


def part5():
    print("§5 mushroom (Sievenpiper) high-impedance surface")
    h, er = 1.43e-3, 4.5
    out = {}
    for f0 in [2.45e9, 5.8e9]:
        a, g, L, C = design_mushroom(f0, h, er)
        fs = np.linspace(0.5 * f0, 1.5 * f0, 200001)
        Gs = mushroom(fs, a, g, h, er, exact_slab=False)[0]
        ph = np.degrees(np.angle(Gs))
        i0 = np.argmin(np.abs(ph))
        band = fs[np.abs(ph) <= 90]
        bw = (band.max() - band.min()) / fs[i0]
        bw_formula = np.sqrt(L / C) / ETA0
        k0h = 2 * np.pi * f0 / C0 * h
        Ge = mushroom(fs, a, g, h, er, exact_slab=True)[0]
        phe = np.degrees(np.angle(Ge))
        f0e = fs[np.argmin(np.abs(phe))]
        print(f"     f0 {f0/1e9:.2f} GHz on 1.43 mm FR-4: L {L*1e9:.3f} nH, C {C*1e12:.3f} pF -> a = {a*1e3:.2f} mm, g = {g*1e3:.3f} mm"
              f" (a/lam0 = {a*f0/C0:.3f}); +-90 deg BW {bw*100:.2f} % (sqrt(L/C)/eta0 = {bw_formula*100:.2f} %, k0h = {k0h*100:.2f} %);"
              f" exact-slab f0 = {f0e/1e9:.3f} GHz")
        out[f0] = dict(a=a, g=g, L=L, C=C, bw=bw, f0e=f0e, a_lam=a * f0 / C0)
        check(f"  {f0/1e9:.2f} GHz: reflection phase 0 at 1/(2 pi sqrt(LC)); +-90 deg BW = sqrt(L/C)/eta0 = k0 h (within 2 %)",
              abs(fs[i0] / f0 - 1) < 1e-4 and abs(bw / bw_formula - 1) < 0.02 and abs(bw_formula / k0h - 1) < 1e-9)
    # 433.92 MHz on the same board: the capacitance a plain-gap patch would need, and the bandwidth
    f4 = 433.92e6
    L4 = MU0 * h
    C4 = 1 / ((2 * np.pi * f4) ** 2 * L4)
    w_acosh = C4 * np.pi / (EPS0 * (1 + er))
    print(f"     433.92 MHz on 1.43 mm FR-4: C = {C4*1e12:.1f} pF per cell -> w*acosh(a/g) = {w_acosh:.2f} m (impossible with a"
          f" printed gap; needs chip capacitors), BW = k0 h = {2*np.pi*f4/C0*h*100:.2f} % = {2*np.pi*f4/C0*h*f4/1e6:.1f} MHz")
    check("433.92 MHz AMC on 1.43 mm: bandwidth k0 h ~ 1.3 % (5.6 MHz)", abs(2 * np.pi * f4 / C0 * h - 0.0130) < 2e-4)
    # surface-wave (effective medium) dispersion: TM bound below f0 (inductive), TE above (capacitive)
    a, g, L, C = out[2.45e9]["a"], out[2.45e9]["g"], out[2.45e9]["L"], out[2.45e9]["C"]
    f = 2.0e9
    Zs = 1j * 2 * np.pi * f * L / (1 - (2 * np.pi * f) ** 2 * L * C)
    bTM = np.sqrt(1 + (Zs.imag / ETA0) ** 2)
    print(f"     effective-medium TM surface wave at 2.0 GHz (inductive, X = {Zs.imag:.0f} ohm): beta/k0 = {bTM:.4f};"
          f" zone edge pi/a reached when beta/k0 = {C0/(2*f*a):.2f}")
    return out


# ---------------------------------------------------------------- §6 CRLH
def part6():
    print("§6 CRLH line")
    # per-cell values, balanced: LR CL = LL CR, transition at 2.45 GHz, Bloch impedance 50 ohm
    f0, Zc = 2.45e9, 50.0
    w0 = 2 * np.pi * f0
    # balanced: wse = wsh = w0; LR/CR = LL/CL = Zc^2. choose wR = 1/sqrt(LR CR) = 2 w0 (right-handed resonance scale)
    wR = 2.0 * w0
    LR, CR = Zc / wR, 1 / (Zc * wR)
    wL = w0 ** 2 / wR
    LL, CL = Zc / wL, 1 / (Zc * wL)

    def cos_bp(w, LR=LR, CR=CR, LL=LL, CL=CL):
        Z = 1j * (w * LR - 1 / (w * CL))
        Y = 1j * (w * CR - 1 / (w * LL))
        return 1 + Z * Y / 2

    ws = np.linspace(0.3 * w0, 1.8 * w0, 30001)
    cb = np.array([cos_bp(w).real for w in ws])
    check("balanced CRLH: no stop band at the transition frequency (|cos beta p| <= 1 around w0)",
          np.all(np.abs(cb[np.abs(ws - w0) < 0.1 * w0]) <= 1 + 1e-12))
    # unbalanced: LL 1.5x -> gap between w_se and w_sh
    cb_u = np.array([cos_bp(w, LL=1.5 * LL).real for w in ws])
    gap = ws[np.abs(cb_u) > 1]
    gap = gap[(gap > 0.7 * w0) & (gap < 1.3 * w0)]
    wse, wsh = 1 / np.sqrt(LR * CL), 1 / np.sqrt(1.5 * LL * CR)
    print(f"     element values: LR {LR*1e9:.3f} nH, CR {CR*1e12:.3f} pF, LL {LL*1e9:.3f} nH, CL {CL*1e12:.3f} pF")
    print(f"     unbalanced (LL x 1.5): gap {gap.min()/2/np.pi/1e9:.3f}-{gap.max()/2/np.pi/1e9:.3f} GHz"
          f" (w_sh {wsh/2/np.pi/1e9:.3f}, w_se {wse/2/np.pi/1e9:.3f} GHz)")
    check("unbalanced gap edges = series and shunt resonances 1/sqrt(LR CL), 1/sqrt(LL CR)",
          abs(gap.min() - min(wse, wsh)) / w0 < 2e-3 and abs(gap.max() - max(wse, wsh)) / w0 < 2e-3)
    # left-handed band: beta < 0 (phase advance) where Z and Y are both capacitive/inductive-negative
    w = 0.7 * w0
    Z = 1j * (w * LR - 1 / (w * CL))
    Y = 1j * (w * CR - 1 / (w * LL))
    gamma_p = np.arccosh(1 + Z * Y / 2 + 0j)
    # choose root with forward power flow: propagation constant sign from the sign of Im(Z) (series reactance)
    beta_sign = np.sign(Z.imag)
    w2 = 0.71 * w0
    bp1 = np.arccos(cos_bp(w).real) * np.sign((1j * (w * LR - 1 / (w * CL))).imag)
    bp2 = np.arccos(cos_bp(w2).real) * np.sign((1j * (w2 * LR - 1 / (w2 * CL))).imag)
    vg_sign = np.sign((w2 - w) / (bp2 - bp1))
    vp_sign = np.sign(w / bp1)
    print(f"     at 0.7 f0: beta p = {bp1:+.3f} rad (series reactance {Z.imag:+.1f} ohm), group/phase velocity signs {vg_sign:+.0f}/{vp_sign:+.0f}")
    check("left-handed band below f0: phase and group velocities antiparallel (backward wave)", vg_sign * vp_sign < 0)
    return dict(LR=LR, CR=CR, LL=LL, CL=CL)


if __name__ == "__main__":
    part1()
    part2()
    part3()
    part4()
    part5()
    part6()
    print(f"\n{sum(checks)}/{len(checks)} checks passed")
