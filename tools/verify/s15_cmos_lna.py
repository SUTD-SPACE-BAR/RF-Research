#!/usr/bin/env python3
"""W5-S15 / G-06-10 — CMOS LNA depth for kb/06-rf-circuits/lna-design.md ("Level 3b — CMOS LNA noise ...").

 A. MOSFET two-port noise with induced gate noise (van der Ziel model as used by Shaeffer & Lee):
    i_d^2 = 4kT γ g_d0, i_g^2 = 4kT δ g_g, g_g = ω²C_gs²/(5 g_d0), correlation c = E[i_g i_d*]/√(..) = 0.395j.
    Numerically minimise F over Y_s and compare with F_min = 1 + (2/√5)(ω/ω_T)√(γδ(1-|c|²)) and the
    closed-form G_opt, B_opt.
 B. Power-constrained noise optimisation of the inductively degenerated LNA (fixed I_D, vary W; square law,
    long-channel α = 1): full nodal noise solve with gate noise and correlation -> W_opt, Q_L,opt, F_min,P;
    compare with the quoted 1 + 2.4(γ/α)(ω0/ω_T) and with the unconstrained F_min of the same device.
 C. CG-CS noise-cancelling (balun) LNA: nodal analysis; the matching (CG) device's noise vanishes when
    g_m2 R_2 = R_1/R_s; NF vs CS scaling n (g_m2 = n g_m1, R_2 = R_1/n) vs plain CG (F ≥ 1 + γ/α).
Run: python3 tools/verify/s15_cmos_lna.py   (≈ 2 s)
"""
import sys
import numpy as np
from scipy.optimize import minimize, minimize_scalar

ok_all = True
kB, T0 = 1.380649e-23, 290.0
kT4 = 4 * kB * T0


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


# Orientation used here: i_g taken OUT of the gate node (g -> s), i_d flowing drain -> source. In these directions
# c = -0.395j reproduces Lee's published B_opt = -ωC_gs(1 + α|c|√(δ/5γ)) (Lee 1998 eq. 22, his c = +j0.395 in his
# reference directions). The opposite sign is reported as a sensitivity case in B.
gam, dlt, cc, alpha = 2 / 3, 4 / 3, -0.395j, 1.0

# ================================================================ A. two-port noise parameters
print("A: intrinsic MOSFET with induced gate noise, γ = 2/3, δ = 4/3, |c| = 0.395 (Lee convention), α = 1")
gm = 50e-3; f = 1.575e9; w = 2 * np.pi * f
okA = True
for wt_ratio in (0.05, 0.1, 0.2):
    Cgs = gm / (w / wt_ratio)                      # ω/ω_T = wt_ratio
    gd0 = gm / alpha
    Sd = kT4 * gam * gd0
    gg = w ** 2 * Cgs ** 2 / (5 * gd0); Sg = kT4 * dlt * gg
    Sgd = cc * np.sqrt(Sg * Sd)

    def F(Ys):
        Yp = Ys + 1j * w * Cgs
        num = Sg + Sd * abs(Yp) ** 2 / gm ** 2 - 2 * np.real(np.conj(Yp) * Sgd / gm)
        return 1 + num / (kT4 * Ys.real)

    res = minimize(lambda p: F(p[0] + 1j * p[1]), x0=[1e-3, -w * Cgs], method='Nelder-Mead',
                   options=dict(xatol=1e-12, fatol=1e-14, maxiter=20000))
    Gopt_n, Bopt_n = res.x; Fmin_n = res.fun
    Fmin_cf = 1 + (2 / np.sqrt(5)) * wt_ratio * np.sqrt(gam * dlt * (1 - abs(cc) ** 2))
    Gopt_cf = alpha * w * Cgs * np.sqrt(dlt * (1 - abs(cc) ** 2) / (5 * gam))
    Bopt_a = -w * Cgs * (1 + alpha * abs(cc) * np.sqrt(dlt / (5 * gam)))
    Bopt_b = -w * Cgs * (1 - alpha * abs(cc) * np.sqrt(dlt / (5 * gam)))
    Rn = gam / (alpha * gm)
    okA &= abs(Fmin_n - Fmin_cf) < 1e-6 and abs(Gopt_n / Gopt_cf - 1) < 1e-3
    print(f"   ω/ω_T {wt_ratio}: F_min numeric {10*np.log10(Fmin_n):.4f} dB vs closed form {10*np.log10(Fmin_cf):.4f} dB; "
          f"G_opt {Gopt_n*1e3:.3f} vs {Gopt_cf*1e3:.3f} mS; B_opt {Bopt_n*1e3:.3f} mS vs -ωC(1 ± α|c|√(δ/5γ)) = "
          f"{Bopt_a*1e3:.3f} / {Bopt_b*1e3:.3f} mS; R_n = γ/(α g_m) = {Rn:.1f} ohm")
    if wt_ratio == 0.1:
        Bsel = "+" if abs(Bopt_n - Bopt_a) < abs(Bopt_n - Bopt_b) else "-"
        Bok = min(abs(Bopt_n - Bopt_a), abs(Bopt_n - Bopt_b)) / abs(Bopt_n) < 1e-3
print(f"   B_opt matches the '{Bsel}' form, i.e. Lee's eq. 22 B_opt = -ωC_gs(1 + α|c|√(δ/5γ)) (inductive, beyond resonating C_gs)")
check("A1 F_min = 1 + (2/√5)(ω/ω_T)√(γδ(1-|c|²)), G_opt and Lee's B_opt reproduced by brute-force minimisation", okA and Bok and Bsel == "+")

# ================================================================ B. power-constrained optimisation
print("B: power-constrained inductively degenerated LNA, 1575.42 MHz, R_s 50 ohm, long-channel square law (α = 1)")
f0 = 1575.42e6; w0 = 2 * np.pi * f0; Rs = 50.0
L_ch = 0.18e-6; Cox = 8.6e-3; mu = 0.03                 # 0.18 um, Cox 8.6 fF/um^2, mu_eff 300 cm^2/Vs (illustrative)


def lna_F(W, ID, with_gate=True, Qind=None):
    Cgs = 2 / 3 * W * L_ch * Cox
    gm_ = np.sqrt(2 * mu * Cox * (W / L_ch) * ID)
    gd0 = gm_ / alpha; wT = gm_ / Cgs
    Ls = Rs / wT; Lg = 1 / (w0 ** 2 * Cgs) - Ls
    if Lg <= 0:
        return np.inf, None
    RLg = 0 if Qind is None else w0 * Lg / Qind
    Zg = Rs + RLg + 1j * w0 * Lg
    Y_C = 1j * w0 * Cgs; Y_L = 1 / (1j * w0 * Ls)
    # unknowns v_g, v_s ; sources: v_src (series with Zg), i_g (g->s), i_d (d->s); output i_out = gm v_gs + i_d
    A = np.array([[1 / Zg + Y_C, -Y_C], [-(Y_C + gm_), Y_C + gm_ + Y_L]])
    def out(vsrc, ig, idn):
        b = np.array([vsrc / Zg - ig, ig + idn])
        vg, vs = np.linalg.solve(A, b)
        return gm_ * (vg - vs) + idn
    Hs, Hg, Hd = out(1, 0, 0), out(0, 1, 0), out(0, 0, 1)
    Sd = kT4 * gam * gd0
    Sg = kT4 * dlt * w0 ** 2 * Cgs ** 2 / (5 * gd0) if with_gate else 0.0
    Sgd = cc * np.sqrt(Sg * Sd)
    Nsrc = abs(Hs) ** 2 * kT4 * Rs
    Nint = abs(Hg) ** 2 * Sg + abs(Hd) ** 2 * Sd + 2 * np.real(Hg * np.conj(Hd) * Sgd)
    NLg = abs(Hs) ** 2 * kT4 * RLg
    Fv = 1 + (Nint + NLg) / Nsrc
    QL = 1 / (w0 * Cgs * Rs)
    return Fv, dict(Cgs=Cgs, gm=gm_, wT=wT, Ls=Ls, Lg=Lg, QL=QL, Zin=None)


okB = True
for ID in (2e-3, 5e-3, 10e-3):
    r = minimize_scalar(lambda lw: lna_F(10 ** lw, ID)[0], bounds=(-6, -2.5), method='bounded', options=dict(xatol=1e-6))
    Wopt = 10 ** r.x; Fp, d = lna_F(Wopt, ID)
    quoted = 1 + 2.4 * (gam / alpha) * (w0 / d['wT'])
    # unconstrained F_min of the SAME device at its optimum width (two-port bound)
    Fmin_dev = 1 + (2 / np.sqrt(5)) * (w0 / d['wT']) * np.sqrt(gam * dlt * (1 - abs(cc) ** 2))
    Fng, _ = lna_F(Wopt, ID, with_gate=False)
    print(f"   I_D {ID*1e3:4.1f} mA: W_opt {Wopt*1e6:6.1f} um, Q_L = 1/(ω0 C_gs R_s) {d['QL']:.2f}, f_T {d['wT']/2/np.pi/1e9:5.1f} GHz, "
          f"L_s {d['Ls']*1e9:.2f} nH, L_g {d['Lg']*1e9:.1f} nH: NF {10*np.log10(Fp):.3f} dB "
          f"(quoted 1+2.4(γ/α)(ω0/ω_T) -> {10*np.log10(quoted):.3f} dB; device F_min {10*np.log10(Fmin_dev):.3f} dB; "
          f"without gate noise {10*np.log10(Fng):.3f} dB)")
    ratio = (Fp - 1) / ((gam / alpha) * (w0 / d['wT']))
    W_lee = 1 / (3 * w0 * L_ch * Cox * Rs)
    print(f"      exact (F-1)/((γ/α)(ω0/ω_T)) = {ratio:.2f} (quoted 2.4); Lee's W_opt ≈ 1/(3 ω L C_ox R_s) = {W_lee*1e6:.0f} um")
    okB &= 3.0 < d['QL'] < 5.0 and 1.8 < ratio < 2.6 and Fp > Fmin_dev and 0.5 < Wopt / W_lee < 2
# NF vs W at 5 mA, to show the shallow optimum
ID = 5e-3
for Wx in (50e-6, 100e-6, 200e-6, 400e-6, 800e-6):
    Fx, dx = lna_F(Wx, ID)
    print(f"      I_D 5 mA, W {Wx*1e6:5.0f} um: Q_L {dx['QL']:5.2f}, NF {10*np.log10(Fx):.3f} dB")
FQ, dQ = lna_F(10 ** minimize_scalar(lambda lw: lna_F(10 ** lw, ID)[0], bounds=(-6, -2.5), method='bounded').x, ID, Qind=20)
print(f"   with a Q = 20 gate inductor at the 5 mA optimum: NF {10*np.log10(FQ):.2f} dB (L_g {dQ['Lg']*1e9:.1f} nH) — "
      "the passive loss dominates, as in Example 4")
check("B1 power-constrained optimum: Q_L in Lee's 3-5 range, W near 1/(3ωLC_oxR_s), (F-1) ≈ 2.0 (γ/α)(ω0/ω_T) (quoted 2.4)", okB)
# sensitivity: the opposite correlation sign
cc_save = cc
cc = +0.395j
r = minimize_scalar(lambda lw: lna_F(10 ** lw, 5e-3)[0], bounds=(-6, -2.5), method='bounded', options=dict(xatol=1e-7))
Fs_, ds_ = lna_F(10 ** r.x, 5e-3)
print(f"   sensitivity — opposite correlation sign (c = +0.395j in this orientation): Q_L,opt {ds_['QL']:.2f}, NF {10*np.log10(Fs_):.3f} dB "
      f"(factor {(Fs_-1)/((gam/alpha)*(w0/ds_['wT'])):.2f}) — the sign convention matters by ~0.06 dB and ~30 % in W")
cc = cc_save

# ================================================================ C. CG-CS noise cancelling
print("C: CG-CS noise-cancelling (balun) LNA, R_s 50 ohm, g_m1 = 1/R_s (input match), R_1 = 500 ohm, output v_a - v_b")


def cgcs(gm1, R1, gm2, R2, cancel_check=False):
    # unknowns v_x, v_a, v_b ; sources: vsrc, i_n1 (M1 d->s), i_n2 (M2 d->s), i_R1, i_R2 (into ground from node)
    def solve(vsrc, in1, in2, iR1, iR2):
        vx = (vsrc / Rs + in1) / (1 / Rs + gm1)
        va = -R1 * (-gm1 * vx + in1 + iR1)
        vb = -R2 * (gm2 * vx + in2 + iR2)
        return va - vb
    Hs = solve(1, 0, 0, 0, 0); H1 = solve(0, 1, 0, 0, 0); H2 = solve(0, 0, 1, 0, 0)
    HR1 = solve(0, 0, 0, 1, 0); HR2 = solve(0, 0, 0, 0, 1)
    Ns = abs(Hs) ** 2 * kT4 * Rs
    N1 = abs(H1) ** 2 * kT4 * gam * gm1 / alpha
    N2 = abs(H2) ** 2 * kT4 * gam * gm2 / alpha
    NR = abs(HR1) ** 2 * kT4 / R1 + abs(HR2) ** 2 * kT4 / R2
    return 1 + (N1 + N2 + NR) / Ns, N1 / Ns, abs(Hs)


gm1, R1 = 1 / Rs, 500.0
# plain CG (single-ended output v_a only) for reference


def cg_only(gm1, R1):
    vxn = lambda vsrc, in1: (vsrc / Rs + in1) / (1 / Rs + gm1)
    Hs = -R1 * (-gm1 * vxn(1, 0)); H1 = -R1 * (-gm1 * vxn(0, 1) + 1); HR = -R1
    return 1 + (abs(H1) ** 2 * kT4 * gam * gm1 / alpha + HR ** 2 * kT4 / R1) / (abs(Hs) ** 2 * kT4 * Rs)


Fcg = cg_only(gm1, R1)
print(f"   plain CG (g_m1 R_s = 1, R_1 500): NF {10*np.log10(Fcg):.2f} dB  (bound 1 + γ/α -> {10*np.log10(1+gam/alpha):.2f} dB, + R_1 noise)")
okC = True
for n in (1, 2, 4):
    gm2 = n * gm1; R2 = R1 / n                     # g_m2 R_2 = g_m1 R_1 = R_1/R_s  -> cancellation condition
    Fv, f1, Hs = cgcs(gm1, R1, gm2, R2)
    Fo, f1o, _ = cgcs(gm1, R1, gm2 * 0.8, R2)       # 20 % off the cancellation condition
    print(f"   CS scaled n = {n} (g_m2 {gm2*1e3:.0f} mS, R_2 {R2:.0f} ohm, current ×{1+n}): NF {10*np.log10(Fv):.2f} dB, "
          f"M1 share of F-1 {f1:.1e}; with g_m2 20 % low: NF {10*np.log10(Fo):.2f} dB (M1 share {f1o:.3f}); "
          f"gain |v_out/v_src| {20*np.log10(Hs):.1f} dB")
    okC &= f1 < 1e-20 and f1o > 1e-3
    if n == 4:
        F4 = Fv
print("   residual NF ≈ 1 + γ/(α n) + R-noise terms: the CS device's noise is NOT cancelled, so NF falls as its g_m (power) rises")
check("C1 CG noise cancels exactly at g_m2 R_2 = R_1/R_s; NF beats the plain CG and the 1 + γ/α bound for n ≥ 2",
      okC and F4 < Fcg and F4 < 1 + gam / alpha)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
sys.exit(0 if ok_all else 1)
