#!/usr/bin/env python3
# Runtime (W6-F5, 2026-10-14): ~684 s (11.4 min) measured on a 10-core Apple-silicon Mac, run 3 at a time
# under load average 7-70 from other jobs; expect less on an idle machine. It exceeds the 120 s per-script budget
# used by the D7 verify sweep, so give it a >= 15 min timeout and run it with `python3 -u` to see progress.
# Measured run: exit 0, no FAIL lines. Comment only; no code or results changed.
"""
ant_yagi.py -- Yagi-Uda and LPDA design checks for kb/08-antennas/yagi-uda-and-log-periodic.md

1. Validates the parallel-wire MoM (ant_mom_wire.py) against the classical induced-EMF mutual
   impedance of two side-by-side half-wave dipoles (Balanis 4th ed. eq. 8-68/8-69 form).
2. Implements the DL6WU long-Yagi algorithm as published in the G3SEK/KY4Z/W6NBI program
   DL6WU.BAS (Hoch, "Extremely Long Yagi Antennas", VHF Communications 3/1982): element
   spacings from DL6WU's table, director lengths from the curve fit
       l_n = (K1 - K2 ln n)(1 - K3 exp(-K4 n))   [wavelengths],  (K1..K4 interpolated in d/lambda)
   reflector from DL6WU's length-reactance formula with X = +20 ohm, boom correction
       BC = [733 BD (0.055 - BD) - 504 BD (0.03 - BD)] * BD  (bonded through-boom; half if insulated)
   and gain estimate G = 9.2 + 3.39 ln(boom/lambda) dBd.
3. Evaluates the resulting 433 MHz and 915 MHz designs with the MoM (plain dipole driven element,
   re-resonated), reporting gain, F/B, feed impedance, and compares with the DL6WU estimate.
4. A short 3-element Yagi optimised numerically (handheld ground-station/RDF size).
5. LPDA (Carrel) design equations for a 400-1000 MHz example.

Run: python3 tools/verify/ant_yagi.py        (takes ~1-2 minutes)
"""
import sys, os
import numpy as np
from scipy.special import sici
from scipy.optimize import brentq, minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ant_mom_wire import Wire, solve, far_field_U, directivity, C0, ETA0

# ------------------------------------------------------------------ 1. mutual impedance check
def z12_induced_emf(d_l, l_l=0.5):
    k = 2 * np.pi
    d, l = d_l, l_l
    u0 = k * d
    u1 = k * (np.sqrt(d ** 2 + l ** 2) + l)
    u2 = k * (np.sqrt(d ** 2 + l ** 2) - l)
    S0, C0_ = sici(u0); S1, C1 = sici(u1); S2, C2 = sici(u2)
    R12 = ETA0 / (4 * np.pi) * (2 * C0_ - C1 - C2)
    X12 = -ETA0 / (4 * np.pi) * (2 * S0 - S1 - S2)
    return R12 + 1j * X12


def z12_mom(d_l, f=433e6, a_l=1e-4, nseg=30):
    lam = C0 / f
    w1 = Wire(0, 0, -lam / 4, lam / 4, a_l * lam, nseg)
    w2 = Wire(d_l * lam, 0, -lam / 4, lam / 4, a_l * lam, nseg)
    s1 = solve([w1, w2], [(0, nseg // 2, 1.0), (1, nseg // 2, 0.0)], f)
    s2 = solve([w1, w2], [(0, nseg // 2, 0.0), (1, nseg // 2, 1.0)], f)
    i1 = s1["basis"].index((0, nseg // 2)); i2 = s1["basis"].index((1, nseg // 2))
    Y = np.array([[s1["I"][i1], s2["I"][i1]], [s1["I"][i2], s2["I"][i2]]])
    Z = np.linalg.inv(Y)
    return Z[0, 1]


# ------------------------------------------------------------------ 2. DL6WU algorithm
DL6WU_SPACING = [0.075, 0.180, 0.215, 0.250, 0.280, 0.300, 0.315,
                 0.330, 0.345, 0.360, 0.375, 0.390, 0.400, 0.400]
DL6WU_K = np.array([  # d/lambda, K1, K2, K3, K4
    [.001, .4711, .018, .08398, .965],
    [.003, .462, .01941, .08543, .9697],
    [.005, .4538, .02117, .0951, 1.007],
    [.007, .4491, .02274, .08801, .9004],
    [.010, .4421, .02396, .1027, 1.038],
    [.015, .4358, .02558, .1149, 1.034],
    [.020, .4268, .02614, .1112, 1.036]])


def dl6wu_design(boom_lambda, d_par_lambda, d_de_lambda, boom_diam_lambda=0.0, bonded=True):
    """Returns dict of lengths (wavelengths) and positions from reflector (wavelengths)."""
    # spacings
    pos = [0.0, 0.2]
    avail = boom_lambda
    n = 0
    while True:
        s = DL6WU_SPACING[n] if n < len(DL6WU_SPACING) else DL6WU_SPACING[-1]
        if avail - s < 0:
            break
        avail -= s
        pos.append(pos[-1] + s)
        n += 1
    ndir = n
    # boom correction (fraction of boom diameter), then absolute in wavelengths
    BD = boom_diam_lambda
    bc1 = 733 * BD * (.055 - BD) - 504 * BD * (.03 - BD) if BD > 0 else 0.0
    if BD > 0 and not bonded:
        bc1 /= 2
    BC = bc1 * BD
    # director lengths: interpolate K in element diameter
    d = d_par_lambda
    kk = np.array([np.interp(d, DL6WU_K[:, 0], DL6WU_K[:, i]) for i in range(1, 5)])
    nn = np.arange(1, ndir + 1)
    # DL6WU.BAS interpolates the *lengths* between bracketing rows; interpolating K is close enough
    lo = np.searchsorted(DL6WU_K[:, 0], d) - 1
    lo = np.clip(lo, 0, len(DL6WU_K) - 2)
    KL, KH = DL6WU_K[lo], DL6WU_K[lo + 1]
    J = (d - KL[0]) / (KH[0] - KL[0])
    Ll = (KL[1] - KL[2] * np.log(nn)) * (1 - KL[3] * np.exp(-KL[4] * nn))
    Lh = (KH[1] - KH[2] * np.log(nn)) * (1 - KH[3] * np.exp(-KH[4] * nn))
    dirs = Ll + J * (Lh - Ll) + BC
    XR = 20.0
    refl = (((XR - 40) / (186.8769 * np.log(2 / d) - 320)) + 1) / 2 + BC
    DD = d_de_lambda
    de_folded = 1.02 * (.4777 - (1.0522 * DD) + (.43363 * (DD ** -.014891))) / 2
    boom_used = pos[-1]
    G_dBd = 9.2 + 3.39 * np.log(boom_used)
    return dict(pos=np.array(pos), refl=refl, de_folded=de_folded, dirs=dirs,
                boom=boom_used, G_dBd=G_dBd, ndir=ndir, BC=BC)


def yagi_wires(lengths_m, pos_m, a_m, nseg_per_lambda=60, lam=1.0):
    wires = []
    for L, x in zip(lengths_m, pos_m):
        nseg = max(10, int(np.ceil(L / lam * nseg_per_lambda / 2)) * 2)
        wires.append(Wire(x, 0.0, -L / 2, L / 2, a_m, nseg))
    return wires


def evaluate_yagi(lengths_m, pos_m, a_m, f, de_index=1, resonate_de=True):
    lam = C0 / f
    lengths_m = list(lengths_m)
    def run(Lde):
        L2 = lengths_m.copy(); L2[de_index] = Lde
        ws = yagi_wires(L2, pos_m, a_m, lam=lam)
        sol = solve(ws, [(de_index, ws[de_index].nseg // 2, 1.0)], f)
        return sol, L2
    if resonate_de:
        g = lambda Lde: np.imag(run(Lde)[0]["Zin"][0])
        L0 = lengths_m[de_index]
        try:
            Lres = brentq(g, 0.85 * L0, 1.1 * L0, xtol=1e-5 * lam)
        except ValueError:
            Lres = L0
        sol, L2 = run(Lres)
    else:
        sol, L2 = run(lengths_m[de_index])
    D, Prad = directivity(sol, np.pi / 2, 0.0, nth=91, nph=180)
    Uf = far_field_U(sol, np.array(np.pi / 2), np.array(0.0))
    Ub = far_field_U(sol, np.array(np.pi / 2), np.array(np.pi))
    # E-plane (phi sweep in theta=90 plane, elements along z -> this is the H-plane of each dipole)
    ph = np.linspace(-np.pi, np.pi, 3601)
    Uh = far_field_U(sol, np.full_like(ph, np.pi / 2), ph)
    Uh /= Uh.max()
    hp = ph[Uh >= 0.5]
    bw_h = np.degrees(hp.max() - hp.min())
    th = np.linspace(0, np.pi, 1801)
    Ue = far_field_U(sol, th, np.zeros_like(th))
    Ue /= Ue.max()
    he = th[Ue >= 0.5]
    bw_e = np.degrees(he.max() - he.min())
    return dict(D=D, Zin=sol["Zin"][0], FB=10 * np.log10(float(Uf) / float(Ub)),
                Lde=L2[de_index], bw_plane_perp=bw_h, bw_plane_elem=bw_e, PradPin=Prad / sol["Pin"])


def main():
    print("=== 1. MoM mutual impedance vs induced-EMF (two parallel lambda/2 dipoles) ===")
    for d in [0.1, 0.25, 0.5, 1.0]:
        zi = z12_induced_emf(d)
        zm = z12_mom(d)
        print(f"  d = {d:4.2f} lambda: induced EMF Z12 = {zi.real:7.2f}{zi.imag:+7.2f}j   "
              f"MoM Z12 = {zm.real:7.2f}{zm.imag:+7.2f}j ohm")

    print("\n=== 2/3. DL6WU designs evaluated with MoM ===")
    cases = [
        ("433 MHz, 6 mm elements, insulated/non-metal boom, ~2.3 lambda boom", 433e6, 6e-3, 2.3),
        ("433 MHz, 6 mm elements, ~4.0 lambda boom", 433e6, 6e-3, 4.0),
        ("915 MHz, 4 mm elements, ~2.3 lambda boom", 915e6, 4e-3, 2.3),
        ("915 MHz, 4 mm elements, ~4.5 lambda boom", 915e6, 4e-3, 4.5),
    ]
    for (name, f, dia, BL) in cases:
        lam = C0 / f
        des = dl6wu_design(BL, dia / lam, dia / lam)
        # driven element for MoM: plain dipole starting at ~0.47 lambda, re-resonated
        lengths = [des["refl"], 0.47] + list(des["dirs"])
        lengths_m = [L * lam for L in lengths]
        pos_m = des["pos"] * lam
        res = evaluate_yagi(lengths_m, pos_m, dia / 2, f)
        print(f"\n  {name}")
        print(f"    elements = {2 + des['ndir']}, electrical boom = {des['boom']:.3f} lambda = {des['boom']*lam*1000:.0f} mm")
        print(f"    reflector = {des['refl']*lam*1000:.1f} mm ({des['refl']:.4f} lam); DE(folded, DL6WU) = {des['de_folded']*lam*1000:.1f} mm; "
              f"DE(plain dipole, resonated in MoM) = {res['Lde']*1000:.1f} mm")
        ds = ", ".join(f"{L*lam*1000:.1f}" for L in des["dirs"])
        ps = ", ".join(f"{p*lam*1000:.0f}" for p in des["pos"])
        print(f"    directors (mm) = {ds}")
        print(f"    positions from reflector (mm) = {ps}")
        print(f"    DL6WU estimate G = {des['G_dBd']:.2f} dBd = {des['G_dBd']+2.15:.2f} dBi")
        print(f"    MoM: D = {10*np.log10(res['D']):.2f} dBi, F/B = {res['FB']:.1f} dB, Zin(plain dipole DE) = "
              f"{res['Zin'].real:.1f}{res['Zin'].imag:+.1f}j ohm, HPBW (plane containing elements) = "
              f"{res['bw_plane_elem']:.1f} deg, HPBW (perpendicular plane) = {res['bw_plane_perp']:.1f} deg, "
              f"Prad/Pin = {res['PradPin']:.3f}")

    print("\n=== 4. Short 3-element Yagi, optimised for gain with F/B > 15 dB (433 MHz, 6 mm) ===")
    f = 433e6; lam = C0 / f; a = 3e-3
    def cost(p):
        Lr, Ld, s1, s2 = p
        lengths = [Lr * lam, 0.47 * lam, Ld * lam]
        pos = [0, s1 * lam, (s1 + s2) * lam]
        r = evaluate_yagi(lengths, pos, a, f)
        pen = max(0, 15 - r["FB"]) * 0.3
        return -10 * np.log10(r["D"]) + pen, r
    best = None
    for Lr in [0.49, 0.50]:
        for Ld in [0.44, 0.45]:
            for s1 in [0.15, 0.2]:
                for s2 in [0.15, 0.2]:
                    c, r = cost([Lr, Ld, s1, s2])
                    if best is None or c < best[0]:
                        best = (c, [Lr, Ld, s1, s2], r)
    opt = minimize(lambda p: cost(p)[0], best[1], method="Nelder-Mead",
                   options=dict(maxiter=60, xatol=1e-3, fatol=1e-3))
    c, r = cost(opt.x)
    Lr, Ld, s1, s2 = opt.x
    print(f"  refl = {Lr*lam*1000:.1f} mm, DE(res.) = {r['Lde']*1000:.1f} mm, dir = {Ld*lam*1000:.1f} mm, "
          f"R-DE = {s1*lam*1000:.0f} mm, DE-D1 = {s2*lam*1000:.0f} mm (boom {(s1+s2)*lam*1000:.0f} mm)")
    print(f"  D = {10*np.log10(r['D']):.2f} dBi, F/B = {r['FB']:.1f} dB, Zin = {r['Zin'].real:.1f}{r['Zin'].imag:+.1f}j ohm, "
          f"HPBW = {r['bw_plane_elem']:.0f} / {r['bw_plane_perp']:.0f} deg")

    print("\n=== 5. LPDA (Carrel) example: 400-1000 MHz, tau = 0.90, sigma = sigma_opt ===")
    f1, fn, tau = 400e6, 1000e6, 0.90
    sigma = 0.243 * tau - 0.051
    cot_a = 4 * sigma / (1 - tau)
    alpha = np.degrees(np.arctan(1 / cot_a))
    B = fn / f1
    Bar = 1.1 + 7.7 * (1 - tau) ** 2 * cot_a
    Bs = B * Bar
    N = 1 + np.log(Bs) / np.log(1 / tau)
    lam_max = C0 / f1
    L1 = lam_max / 2 * Bar ** 0  # longest element ~ lambda_max/2 (hamwaves convention uses f1 of structure)
    lam_long = C0 / f1 * Bar / 1.0  # structure must extend to lambda_max_s = lambda_max * (Bs/B)... see page
    Lmax = (C0 / f1) / 2
    boom = (Lmax / 2) * (1 - 1 / Bs) * cot_a
    print(f"  sigma_opt = {sigma:.4f}, cot(alpha) = {cot_a:.3f}, half apex angle alpha = {alpha:.2f} deg")
    print(f"  B = {B:.2f}, B_ar = {Bar:.3f}, B_s = {Bs:.3f}, N = {N:.1f} -> {int(np.ceil(N))} elements")
    print(f"  longest element ~ lambda(f1)/2 = {Lmax*1000:.0f} mm; boom ~ (lambda_max/4)(1-1/Bs)cot(alpha) = {boom*1000:.0f} mm")


if __name__ == "__main__":
    main()
