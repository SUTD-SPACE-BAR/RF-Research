#!/usr/bin/env python3
"""
s5_waveguide_extras.py — checks for the W5-S5 additions (gap G-02-03) to
kb/02-electromagnetics/waveguides-and-cavity-resonators.md, section "Level 3b".

Sections
  §1  Circular guide: cutoffs from Bessel zeros (TE11, TM01, TE21, TE01/TM11); conductor attenuation
      of TE11, TM01 and TE01 — closed forms vs numerical wall-loss / power-flow integrals of the mode
      fields; a 90 mm copper and a tinplate can at 2.45 GHz.
  §2  Modal voltage and current of TE10: power-voltage, power-current and voltage-current "impedances"
      (2b/a, pi^2 b/8a, pi b/2a times Z_TE) from the fields.
  §3  Parallel-plate guide: TEM + TE_n/TM_n cutoffs; PCB plane pair and a 1.6 mm board.
  §4  Transverse resonance: (a) TM0/TE1 surface waves of a grounded slab (JLC 1.43 mm core and the
      KB's 1.51/1.6 mm cases, compared with e11_greens.py and 12/planar-arrays numbers); (b) a WR-90
      partly filled with a dielectric slab — transverse resonance vs a 1-D finite-difference eigen-solver.
  §5  Cylindrical cavity: TM010 frequency and Q_c closed form vs numerical energy/loss; TE011.
  §6  Probe excitation from mode orthogonality: R_in = 2 sin^2(beta l) |int e.I dl|^2 / (I0^2 P_n);
      rectangular closed form vs numeric; cantenna (90 mm can, 2.45 GHz) probe length for 50 ohm.

Run:  python3 tools/verify/s5_waveguide_extras.py    (about 5 s)
"""
import numpy as np
from scipy import integrate, optimize, special, linalg

C0 = 299_792_458.0
MU0 = 1.25663706127e-6
EPS0 = 8.8541878188e-12
ETA0 = np.sqrt(MU0 / EPS0)
SIG_CU = 5.80e7
SIG_SN = 9.17e6          # tin (CRC, 20 C) — tinplate can surface
checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}  {detail}")


def Rs(f, sig):
    return np.sqrt(np.pi * f * MU0 / sig)


# ---------------------------------------------------------------- §1 circular guide
def circ_alpha_numeric(kind, n, p, R, f, sig):
    """Numerical alpha_c (Np/m) of circular TE_nm / TM_nm from the mode fields."""
    w = 2 * np.pi * f
    k = w / C0
    kc = p / R
    beta = np.sqrt(k ** 2 - kc ** 2)
    rho = np.linspace(1e-9, R, 4001)
    phi = np.linspace(0, 2 * np.pi, 721)
    RHO, PHI = np.meshgrid(rho, phi, indexing="ij")
    Jn = special.jv(n, kc * RHO)
    dJn = special.jvp(n, kc * RHO)
    if kind == "TE":
        # h_z = Jn(kc rho) cos(n phi); H_t = -(j beta/kc^2) grad_t h_z ; E_t = -Z_TE z x H_t
        Hr = -1j * beta / kc ** 2 * kc * dJn * np.cos(n * PHI)
        Hp = -1j * beta / kc ** 2 * (-n / RHO) * Jn * np.sin(n * PHI)
        Z = w * MU0 / beta
        Sz = 0.5 * Z * (np.abs(Hr) ** 2 + np.abs(Hp) ** 2)
        Hz_w = special.jv(n, p) * np.cos(n * phi)
        Hp_w = -1j * beta / kc ** 2 * (-n / R) * special.jv(n, p) * np.sin(n * phi)
        Htan2 = np.abs(Hz_w) ** 2 + np.abs(Hp_w) ** 2
    else:
        # e_z = Jn(kc rho) cos(n phi); E_t = -(j beta/kc^2) grad_t e_z ; H_t = z x E_t / Z_TM
        Er = -1j * beta / kc ** 2 * kc * dJn * np.cos(n * PHI)
        Ep = -1j * beta / kc ** 2 * (-n / RHO) * Jn * np.sin(n * PHI)
        Z = beta / (w * EPS0)
        Sz = 0.5 * (np.abs(Er) ** 2 + np.abs(Ep) ** 2) / Z
        # at the wall E_phi = 0 (Jn(p) = 0), H_phi = E_rho / Z
        Er_w = -1j * beta / kc * special.jvp(n, p) * np.cos(n * phi)
        Htan2 = np.abs(Er_w / Z) ** 2
    P = integrate.trapezoid(integrate.trapezoid(Sz * RHO, phi, axis=1), rho)
    Pl = 0.5 * Rs(f, sig) * integrate.trapezoid(Htan2 * R, phi)
    return Pl / (2 * P)


def circ_alpha_closed(kind, n, p, R, f, sig):
    k = 2 * np.pi * f / C0
    kc = p / R
    beta = np.sqrt(k ** 2 - kc ** 2)
    rs = Rs(f, sig)
    if kind == "TE":
        return rs / (R * k * ETA0 * beta) * (kc ** 2 + k ** 2 * n ** 2 / (p ** 2 - n ** 2))
    return rs * k / (R * ETA0 * beta)


def part1():
    print("§1 circular waveguide")
    zeros = {"TE11": special.jnp_zeros(1, 1)[0], "TM01": special.jn_zeros(0, 1)[0],
             "TE21": special.jnp_zeros(2, 1)[0], "TE01": special.jnp_zeros(0, 2)[1] if False else special.jnp_zeros(0, 1)[0],
             "TM11": special.jn_zeros(1, 1)[0]}
    print("     p values: " + ", ".join(f"{m} {v:.4f}" for m, v in zeros.items()))
    check("TE11 1.8412, TM01 2.4048, TE21 3.0542, TE01 = TM11 3.8317",
          abs(zeros["TE11"] - 1.8412) < 1e-4 and abs(zeros["TM01"] - 2.4048) < 1e-4 and abs(zeros["TE21"] - 3.0542) < 1e-4
          and abs(zeros["TE01"] - 3.8317) < 1e-4 and abs(zeros["TM11"] - 3.8317) < 1e-4)
    R = 0.045
    f = 2.45e9
    for m in ["TE11", "TM01", "TE21", "TE01"]:
        print(f"     90 mm can: f_c({m}) = {zeros[m]*C0/(2*np.pi*R)/1e9:.3f} GHz")
    worst = 0
    for kind, n, p, ff, RR in [("TE", 1, zeros["TE11"], 2.45e9, 0.045), ("TE", 1, zeros["TE11"], 10e9, 0.0127),
                               ("TM", 0, zeros["TM01"], 3.5e9, 0.045), ("TE", 0, zeros["TE01"], 6e9, 0.045),
                               ("TE", 2, zeros["TE21"], 4e9, 0.045)]:
        an = circ_alpha_numeric(kind, n, p, RR, ff, SIG_CU)
        ac = circ_alpha_closed(kind, n, p, RR, ff, SIG_CU)
        worst = max(worst, abs(an / ac - 1))
    check("alpha_c closed forms (TE_nm with n^2/(p'^2-n^2) term; TM_nm) = numerical wall-loss integral",
          worst < 2e-3, f"max rel. diff {worst:.1e}")
    a11 = circ_alpha_closed("TE", 1, zeros["TE11"], 0.045, 2.45e9, SIG_CU) * 8.686
    a11sn = circ_alpha_closed("TE", 1, zeros["TE11"], 0.045, 2.45e9, SIG_SN) * 8.686
    print(f"     90 mm can TE11 at 2.45 GHz: copper {a11:.4f} dB/m, tin {a11sn:.4f} dB/m")
    # TE01 falls with frequency
    a01 = [circ_alpha_closed("TE", 0, zeros["TE01"], 0.025, ff, SIG_CU) * 8.686 for ff in [8e9, 16e9, 32e9, 64e9]]
    check("TE01 attenuation falls monotonically with frequency (R = 25 mm: 8 -> 64 GHz)",
          all(np.diff(a01) < 0), "dB/m: " + ", ".join(f"{x:.4f}" for x in a01))
    lam = C0 / f
    fc = zeros["TE11"] * C0 / (2 * np.pi * R)
    lg = lam / np.sqrt(1 - (fc / f) ** 2)
    print(f"     90 mm can at 2.45 GHz: f_c TE11 {fc/1e9:.3f} GHz, lambda_g {lg*1e3:.1f} mm, lambda_g/4 {lg/4*1e3:.1f} mm")
    check("90 mm can: lambda_g = 202.5 mm (matches 08/horn page)", abs(lg * 1e3 - 202.5) < 0.6, f"{lg*1e3:.1f} mm")
    return dict(fc=fc, lg=lg, a11=a11, a11sn=a11sn)


# ---------------------------------------------------------------- §2 modal V and I
def part2():
    print("§2 TE10 modal voltage/current definitions")
    a, b, f = 22.86e-3, 10.16e-3, 10e9
    k = 2 * np.pi * f / C0
    beta = np.sqrt(k ** 2 - (np.pi / a) ** 2)
    Zte = k * ETA0 / beta
    E0 = 1.0
    x = np.linspace(0, a, 20001)
    Ey = E0 * np.sin(np.pi * x / a)
    Hx = -Ey / Zte
    P = 0.5 * integrate.trapezoid(Ey ** 2 / Zte, x) * b
    V = E0 * b                                          # int E_y dy at x = a/2
    I = integrate.trapezoid(np.abs(Hx), x)             # longitudinal current on the broad wall = int |H_x| dx
    Zpv = V ** 2 / (2 * P)
    Zpi = 2 * P / I ** 2
    Zvi = V / I
    ok = (abs(Zpv / (2 * b / a * Zte) - 1) < 1e-6 and abs(Zpi / (np.pi ** 2 * b / (8 * a) * Zte) - 1) < 1e-6
          and abs(Zvi / (np.pi * b / (2 * a) * Zte) - 1) < 1e-6)
    print(f"     WR-90 @ 10 GHz: Z_TE {Zte:.1f}, Z_PV {Zpv:.1f}, Z_PI {Zpi:.1f}, Z_VI {Zvi:.1f} ohm")
    check("Z_PV = (2b/a) Z_TE, Z_PI = (pi^2 b/8a) Z_TE, Z_VI = (pi b/2a) Z_TE (from the fields)", ok)
    return dict(Zte=Zte, Zpv=Zpv, Zpi=Zpi, Zvi=Zvi)


# ---------------------------------------------------------------- §3 parallel plate
def part3():
    print("§3 parallel-plate guide")
    for name, d, er in [("PCB plane pair 0.2 mm FR-4", 0.2e-3, 4.4), ("1.6 mm board", 1.6e-3, 4.4),
                        ("10 mm air gap", 10e-3, 1.0)]:
        fc1 = C0 / (2 * d * np.sqrt(er))
        print(f"     {name}: TE1/TM1 cutoff {fc1/1e9:.1f} GHz (TEM has none)")
    check("0.2 mm FR-4 plane pair: first higher mode at ~357 GHz (only TEM below)", abs(C0 / (2 * 0.2e-3 * np.sqrt(4.4)) / 1e9 - 357.3) < 1)
    # TEM conductor loss of parallel plates: alpha = Rs / (eta d) Np/m (both plates)
    f, d = 915e6, 0.2e-3
    a_tem = Rs(f, SIG_CU) / (ETA0 / np.sqrt(4.4) * d) * 8.686
    print(f"     TEM conductor loss, 0.2 mm FR-4 plane pair at 915 MHz: {a_tem:.2f} dB/m (plus tan-delta loss {np.pi*f*np.sqrt(4.4)/C0*0.02*8.686:.2f} dB/m)")


# ---------------------------------------------------------------- §4 transverse resonance
def surface_wave_beta(f, h, er, mode="TM0"):
    k0 = 2 * np.pi * f / C0

    def tm(b):
        kd = np.sqrt(er * k0 ** 2 - b ** 2)
        al = np.sqrt(b ** 2 - k0 ** 2)
        return kd * np.tan(kd * h) - er * al          # Z_up + Z_down = 0 for TM to z

    def te(b):
        kd = np.sqrt(er * k0 ** 2 - b ** 2)
        al = np.sqrt(b ** 2 - k0 ** 2)
        return kd / np.tan(kd * h) + al                # -kd cot(kd h) = al

    lo, hi = k0 * (1 + 1e-12), k0 * np.sqrt(er) * (1 - 1e-12)
    if mode == "TM0":
        # TM0 root has 0 < kd h < pi/2, i.e. beta^2 > er k0^2 - (pi/2h)^2 (a lower bound on beta)
        if er * k0 ** 2 > (np.pi / (2 * h)) ** 2:
            lo = max(lo, np.sqrt(er * k0 ** 2 - (np.pi / (2 * h)) ** 2) * (1 + 1e-12))
        return optimize.brentq(tm, lo, hi, xtol=1e-14 * k0) / k0
    fc = C0 / (4 * h * np.sqrt(er - 1))
    if f <= fc:
        return np.nan
    hi2 = np.sqrt(er * k0 ** 2 - (np.pi / (2 * h)) ** 2)   # kd h = pi/2 at the TE1 limit
    return optimize.brentq(te, lo, hi2 * (1 - 1e-12), xtol=1e-14 * k0) / k0


def slab_guide_fd(a, t, er, f, N=2000):
    """beta of the lowest TE_m0-like mode (E_y only) of a rectangular guide whose region 0 < x < t is
    filled with er: 1-D FD eigenproblem E'' + (er(x) k0^2) E = beta^2 E, E(0) = E(a) = 0."""
    k0 = 2 * np.pi * f / C0
    x = np.linspace(0, a, N + 2)[1:-1]
    dx = a / (N + 1)
    erx = np.where(x < t, er, 1.0)
    # treat the cell containing the interface by averaging (second order is enough here)
    main = -2 / dx ** 2 + erx * k0 ** 2
    off = np.ones(N - 1) / dx ** 2
    w = linalg.eigh_tridiagonal(main, off, eigvals_only=True)
    return np.sqrt(w.max())


def slab_guide_trn(a, t, er, f):
    k0 = 2 * np.pi * f / C0

    def fn(b):
        kd = np.sqrt(er * k0 ** 2 - b ** 2 + 0j)
        ka = np.sqrt(k0 ** 2 - b ** 2 + 0j)
        # shorted lines in x: Y_d cot + Y_a cot = 0 with Y_i = k_xi/(w mu)  -> kd cot(kd t) + ka cot(ka (a-t)) = 0
        return np.real(kd / np.tan(kd * t) + ka / np.tan(ka * (a - t)))

    bs = np.linspace(k0 * 0.01, k0 * np.sqrt(er) * 0.9999, 20000)
    v = np.array([fn(b) for b in bs])
    idx = np.where(np.sign(v[:-1]) != np.sign(v[1:]))[0]
    roots = []
    for i in idx:
        try:
            r = optimize.brentq(fn, bs[i], bs[i + 1])
            if abs(fn(r)) < 1e-3 * k0:
                roots.append(r)
        except ValueError:
            pass
    return max(roots)


def part4():
    print("§4 transverse resonance")
    # (a) grounded slab
    rows = []
    for (h, er, tag) in [(1.43e-3, 4.5, "JLC 2-layer core 1.43 mm, er 4.5"), (1.51e-3, 4.5, "1.51 mm, er 4.5 (e11 case)"),
                         (1.6e-3, 4.4, "1.6 mm, er 4.4 (12/planar-arrays case)")]:
        vals = {f: surface_wave_beta(f, h, er) for f in [433.92e6, 915e6, 2.45e9, 5.8e9, 10e9, 24e9]}
        fte1 = C0 / (4 * h * np.sqrt(er - 1))
        print(f"     {tag}: TM0 beta/k0 = " + ", ".join(f"{f/1e9:g} GHz {v:.6f}" for f, v in vals.items())
              + f"; TE1 onset {fte1/1e9:.1f} GHz")
        rows.append((tag, vals, fte1))
    v151 = rows[1][1]
    check("1.51 mm er 4.5 TM0 matches e11_greens.py (1.000057 / 1.00025 / 1.0018 / 1.011 / 1.037 / 1.39)",
          abs(v151[433.92e6] - 1.000057) < 3e-6 and abs(v151[915e6] - 1.00025) < 2e-5 and abs(v151[2.45e9] - 1.0018) < 1e-4
          and abs(v151[5.8e9] - 1.011) < 1e-3 and abs(v151[10e9] - 1.037) < 1e-3 and abs(v151[24e9] - 1.39) < 0.01)
    v16 = rows[2][1]
    check("1.6 mm er 4.4 TM0 matches 12/planar-arrays (1.0020 @ 2.45, 1.0121 @ 5.8 GHz)",
          abs(v16[2.45e9] - 1.0020) < 1e-4 and abs(v16[5.8e9] - 1.0121) < 1e-4, f"{v16[2.45e9]:.4f}, {v16[5.8e9]:.4f}")
    # thin-slab asymptote beta/k0 - 1 ~ (k0 h)^2 (1 - 1/er)^2 / 2
    h, er = 1.43e-3, 4.5
    f = 433.92e6
    k0h = 2 * np.pi * f / C0 * h
    approx = 1 + 0.5 * (k0h * (1 - 1 / er)) ** 2
    exact = surface_wave_beta(f, h, er)
    check("thin-slab TM0 asymptote beta/k0 = 1 + (k0 h (1 - 1/er))^2 / 2", abs((exact - 1) / (approx - 1) - 1) < 0.01,
          f"exact-1 {exact-1:.3e}, approx-1 {approx-1:.3e}")
    te = surface_wave_beta(30e9, 1.43e-3, 4.5, "TE1")
    print(f"     TE1 at 30 GHz on 1.43 mm: beta/k0 = {te:.4f}")
    # (b) slab-loaded WR-90
    a = 22.86e-3
    worst = 0
    for t, er, f in [(5e-3, 2.2, 8e9), (5e-3, 4.4, 10e9), (11.43e-3, 2.2, 7e9)]:
        b_fd = [slab_guide_fd(a, t, er, f, N) for N in (1000, 2000, 4000)]
        b_ext = b_fd[2] + (b_fd[2] - b_fd[1]) / 3            # Richardson (2nd order)
        b_tr = slab_guide_trn(a, t, er, f)
        worst = max(worst, abs(b_tr / b_ext - 1))
        print(f"     WR-90 with {t*1e3:.2f} mm slab er {er} at {f/1e9:g} GHz: TRN beta {b_tr:.3f}, FD {b_ext:.3f} rad/m")
    check("slab-loaded guide: transverse-resonance beta = finite-difference eigenvalue", worst < 1e-3, f"max rel. diff {worst:.1e}")
    return rows


# ---------------------------------------------------------------- §5 cylindrical cavity
def part5():
    print("§5 cylindrical cavity")
    R, d = 0.045, 0.06
    p01 = special.jn_zeros(0, 1)[0]
    f010 = p01 * C0 / (2 * np.pi * R)
    rs = Rs(f010, SIG_CU)
    Q_cf = ETA0 * p01 / (2 * rs) / (1 + R / d)
    k = p01 / R
    rho = np.linspace(0, R, 20001)
    Ez = special.j0(k * rho)
    Hp = special.j1(k * rho) / ETA0                      # |H_phi| for E_z = J0(k rho), lossless
    W = 2 * (EPS0 / 4) * integrate.trapezoid(Ez ** 2 * 2 * np.pi * rho, rho) * d   # 2 x electric energy
    Pl = 0.5 * rs * (2 * np.pi * R * d * Hp[-1] ** 2 + 2 * integrate.trapezoid(Hp ** 2 * 2 * np.pi * rho, rho))
    Q_num = 2 * np.pi * f010 * W / Pl
    print(f"     R 45 mm, d 60 mm copper: TM010 {f010/1e9:.4f} GHz, Q_c closed {Q_cf:.0f}, numeric {Q_num:.0f}")
    check("TM010 Q_c = (eta p01 / 2Rs) / (1 + R/d) equals energy/loss integration", abs(Q_num / Q_cf - 1) < 1e-4)
    p01p = special.jnp_zeros(0, 1)[0]
    f011 = C0 / (2 * np.pi) * np.sqrt((p01p / R) ** 2 + (np.pi / d) ** 2)
    print(f"     TE011 of the same cavity: {f011/1e9:.4f} GHz;  TM010 independent of d")
    # TE011 Q numerically: h_z = J0(kc rho) sin(pi z/d)
    kc = p01p / R
    beta = np.pi / d
    k011 = np.sqrt(kc ** 2 + beta ** 2)
    w = k011 * C0
    rs1 = Rs(f011, SIG_CU)
    z = np.linspace(0, d, 2001)
    RHO, Z = np.meshgrid(rho, z, indexing="ij")
    Hz = special.j0(kc * RHO) * np.sin(beta * Z)
    Hr = (beta / kc) * special.j1(kc * RHO) * np.cos(beta * Z)       # from H_rho = (1/kc^2) d2Hz/(drho dz)
    Ephi = (w * MU0 / kc) * special.j1(kc * RHO) * np.sin(beta * Z)
    We = 0.25 * EPS0 * integrate.trapezoid(integrate.trapezoid(np.abs(Ephi) ** 2 * 2 * np.pi * RHO, z, axis=1), rho)
    Wm = 0.25 * MU0 * integrate.trapezoid(integrate.trapezoid((Hz ** 2 + Hr ** 2) * 2 * np.pi * RHO, z, axis=1), rho)
    side = 2 * np.pi * R * integrate.trapezoid(Hz[-1, :] ** 2, z)
    ends = 2 * integrate.trapezoid(Hr[:, 0] ** 2 * 2 * np.pi * rho, rho)
    Pl1 = 0.5 * rs1 * (side + ends)
    Q011 = w * (We + Wm) / Pl1
    check("TE011 field check: electric = magnetic stored energy at resonance", abs(We / Wm - 1) < 1e-3, f"We/Wm {We/Wm:.5f}")
    print(f"     TE011 Q_c (copper, numeric) {Q011:.0f}  (higher than TM010: no wall currents cross the corners)")
    return dict(f010=f010, Q010=Q_cf, f011=f011, Q011=Q011)


# ---------------------------------------------------------------- §6 probe excitation
def part6(c1):
    print("§6 probe excitation by modal orthogonality")
    # rectangular, uniform current d: R = 2 Z_TE d^2 sin^2(beta l)/(a b)
    a, b, f = 22.86e-3, 10.16e-3, 10e9
    k = 2 * np.pi * f / C0
    beta = np.sqrt(k ** 2 - (np.pi / a) ** 2)
    Zte = k * ETA0 / beta
    dprobe = 5e-3
    l = np.pi / (2 * beta)
    y = np.linspace(0, dprobe, 2001)
    proj = integrate.trapezoid(np.sin(np.pi * (a / 2) / a) * np.ones_like(y), y)
    Pn = 2 * (1 / Zte) * (a / 2) * b
    R_num = 2 * np.sin(beta * l) ** 2 * proj ** 2 / Pn
    R_cf = 2 * Zte * dprobe ** 2 / (a * b)
    check("rectangular probe: modal-orthogonality R = closed form 2 Z_TE d^2 sin^2(beta l)/(ab)", abs(R_num / R_cf - 1) < 1e-9,
          f"{R_num:.1f} ohm (uniform current, 5 mm)")
    # sinusoidal current (open tip): effective length
    def Rrect(h):
        s = np.linspace(0, h, 2001)
        I = np.sin(k * (h - s)) / np.sin(k * h)
        return 2 * Zte * integrate.trapezoid(I, s) ** 2 / (a * b)
    hs = np.linspace(1e-3, 9.5e-3, 200)
    Rr = np.array([Rrect(h) for h in hs])
    h50 = np.interp(50, Rr, hs) if Rr.max() > 50 else np.nan
    print(f"     WR-90 at 10 GHz, back short lambda_g/4, sinusoidal probe current: R = 50 ohm at h = {h50*1e3:.2f} mm (b = 10.16 mm)")
    # cantenna: radial probe at phi = 90 deg from the wall, TE11
    R = 0.045
    f = 2.45e9
    k = 2 * np.pi * f / C0
    p = special.jnp_zeros(1, 1)[0]
    kc = p / R
    beta = np.sqrt(k ** 2 - kc ** 2)
    Z = 2 * np.pi * f * MU0 / beta
    rho = np.linspace(1e-9, R, 4001)
    phi = np.linspace(0, 2 * np.pi, 1441)
    RHO, PHI = np.meshgrid(rho, phi, indexing="ij")
    Hr = -1j * beta / kc * special.jvp(1, kc * RHO) * np.cos(PHI)
    Hp = 1j * beta / kc ** 2 / RHO * special.jv(1, kc * RHO) * np.sin(PHI)
    Pn = 2 * integrate.trapezoid(integrate.trapezoid(Z * (np.abs(Hr) ** 2 + np.abs(Hp) ** 2) * RHO, phi, axis=1), rho)
    # e_rho = Z H_phi on the line phi = 90 deg
    def e_rho(r):
        return np.abs(Z * beta / kc ** 2 / r * special.jv(1, kc * r))

    def Rcan(h):
        s = np.linspace(0, h, 3001)                 # distance from the wall
        I = np.sin(k * (h - s)) / np.sin(k * h)
        proj = integrate.trapezoid(e_rho(R - s) * I, s)
        return 2 * proj ** 2 / Pn                    # back short at lambda_g/4 -> sin^2 = 1
    hs = np.linspace(5e-3, 34e-3, 300)
    Rc = np.array([Rcan(h) for h in hs])
    h50c = np.interp(50, Rc, hs)
    lam = C0 / f
    print(f"     cantenna 90 mm, 2.45 GHz, short at lambda_g/4: R(h) = " +
          ", ".join(f"{h*1e3:.0f} mm {Rcan(h):.0f}" for h in [10e-3, 20e-3, 25e-3, 30.6e-3]) + " ohm")
    print(f"     R = 50 ohm at h = {h50c*1e3:.1f} mm (lambda0/4 = {lam/4*1e3:.1f} mm)")
    check("cantenna radial probe of ~lambda0/4 gives R_in of order 50 ohm (20-120 ohm at 30.6 mm)",
          20 < Rcan(30.6e-3) < 120, f"R(30.6 mm) = {Rcan(30.6e-3):.0f} ohm")
    return dict(h50_wr90=h50, h50_can=h50c, R306=Rcan(30.6e-3))


if __name__ == "__main__":
    c1 = part1()
    part2()
    part3()
    part4()
    part5()
    part6(c1)
    print(f"\n{sum(checks)}/{len(checks)} checks passed")
