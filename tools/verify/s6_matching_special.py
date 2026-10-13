#!/usr/bin/env python3
"""s6_matching_special.py — matching special topics and the double-stub forbidden region
(task W5-S6, gaps G-03-06 and G-03-08) for kb/03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md.

A. Energy / bounce view of a lossless L-match (12.5 -> 50 ohm at 433 MHz): partial sums of the multiple-
   reflection series, forward and reflected power at the load plane, stored energy = Q_n.
B. Negative elements in extracted models: over-de-embedded line (-1 mm) and the coupled-inductor T model.
C. Using an IC's impedance data: conjugate-match an input S11; the cost of conjugating a PA's Z_opt.
D. Differential half-circuit: 30 - j60 ohm differential load to a 100 ohm differential port.
E. High-impedance detector (HSMS-2850-like: Rs 25 ohm, Rv 9.1 kohm, Cj 0.18 pF) at 915 MHz: reactive match vs
   a 50 ohm shunt resistor; sensitivity gain and bandwidth with Q_L = 40.
F. Interstage PA match: 3 - j2 ohm gate to a 25 ohm driver load, direct vs via 50 ohm.
G. Double-stub tuner: forbidden region g > 1/sin^2(beta d), closed-form stub susceptances, skrf check.
"""
import numpy as np
import skrf as rf

PASS = []
C0 = 299792458.0


def check(name, cond, detail=""):
    PASS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def abcd_series(Z):
    return np.array([[1, Z], [0, 1]], dtype=complex)


def abcd_shunt(Y):
    return np.array([[1, 0], [Y, 1]], dtype=complex)


def abcd_line(Z0, theta):
    return np.array([[np.cos(theta), 1j * Z0 * np.sin(theta)], [1j * np.sin(theta) / Z0, np.cos(theta)]])


def zin(M, ZL):
    return (M[0, 0] * ZL + M[0, 1]) / (M[1, 0] * ZL + M[1, 1])


def s_from_abcd(M, z0=50.0):
    A, B, C, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
    den = A + B / z0 + C * z0 + D
    return np.array([[(A + B / z0 - C * z0 - D) / den, 2 * (A * D - B * C) / den],
                     [2 / den, (-A + B / z0 - C * z0 + D) / den]])


def lmatch_low_r(RL, XL, Z0, sign=+1):
    """series element at the load (R_L < Z0), shunt toward the source (Pozar 5.1). returns (X_series, B_shunt)"""
    X = sign * np.sqrt(RL * (Z0 - RL)) - XL
    B = sign * np.sqrt((Z0 - RL) / RL) / Z0
    return X, B


def main():
    w433 = 2 * np.pi * 433e6
    print("=== A. bounce series and energy in a lossless L-match, 12.5 -> 50 ohm, 433 MHz")
    Q = np.sqrt(50 / 12.5 - 1)
    L = Q * 12.5 / w433; Cs = Q / (50 * w433)
    M = abcd_shunt(1j * w433 * Cs) @ abcd_series(1j * w433 * L)
    S = s_from_abcd(M)
    GL = (12.5 - 50) / (12.5 + 50)
    partial = [S[0, 0]]
    term = S[0, 1] * S[1, 0] * GL
    acc = S[0, 0]
    for n in range(60):
        acc = acc + term * (S[1, 1] * GL) ** n
        partial.append(acc)
    print("   |partial sums of Gamma_in| after 0,1,2,3,5,10,40 bounces: " +
          ", ".join(f"{abs(partial[k]):.3f}" for k in (0, 1, 2, 3, 5, 10, 40)))
    check("bounce series converges to Gamma_in = 0", abs(partial[-1]) < 1e-6, f"|S11| alone = {abs(S[0,0]):.3f}")
    aL = S[1, 0] / (1 - S[1, 1] * GL)          # wave toward the load per unit incident wave (50-ohm reference)
    print(f"   forward power at load plane {abs(aL)**2:.4f}, reflected {abs(aL*GL)**2:.4f}, delivered "
          f"{abs(aL)**2*(1-GL**2):.4f} (per watt available)")
    check("forward power at the load = 1/(1-|GL|^2) = 1.5625", abs(abs(aL) ** 2 - 1 / (1 - GL ** 2)) < 1e-9)
    # stored energy: peak phasors, 1 W delivered to 12.5 ohm
    I = np.sqrt(2 * 1.0 / 12.5)
    V50 = I * (12.5 + 1j * w433 * L)
    WL = L * abs(I) ** 2 / 4; WC = Cs * abs(V50) ** 2 / 4
    check("omega*(W_L+W_C)/P equals Q_n", abs(w433 * (WL + WC) / 1.0 - Q) < 1e-6, f"{w433*(WL+WC):.4f} vs Q_n {Q:.4f}")

    print("=== B. negative elements in extracted models")
    f = 2.45e9; ee = 3.18; Z0 = 50.0; ell = 1e-3
    beta = 2 * np.pi * f * np.sqrt(ee) / C0
    Lneg = -Z0 * ell * np.sqrt(ee) / C0; Cneg = -ell * np.sqrt(ee) / (Z0 * C0)
    w = 2 * np.pi * f
    Mline = abcd_line(Z0, -beta * ell)
    MT = abcd_series(1j * w * Lneg / 2) @ abcd_shunt(1j * w * Cneg) @ abcd_series(1j * w * Lneg / 2)
    err = np.max(np.abs(Mline - MT))
    print(f"   -1 mm of 50-ohm microstrip (eeff 3.18) at 2.45 GHz == T of L = {Lneg*1e9:.3f} nH, C = {Cneg*1e12:.3f} pF")
    check("over-de-embedding by 1 mm == negative-L/negative-C T network (error O((beta l)^2))", err < (beta * ell) ** 2,
          f"max ABCD error {err:.1e}, beta*l = {beta*ell:.3f} rad")
    L1, L2, k = 10e-9, 40e-9, 0.8
    Mm = k * np.sqrt(L1 * L2)
    Zcoupled = 1j * w * np.array([[L1, Mm], [Mm, L2]])
    ZT = 1j * w * np.array([[(L1 - Mm) + Mm, Mm], [Mm, (L2 - Mm) + Mm]])
    check("coupled-inductor T: L1 - M negative and exact", (L1 - Mm) < 0 and np.allclose(Zcoupled, ZT),
          f"L1 - M = {(L1-Mm)*1e9:.1f} nH")

    print("=== C. using an IC's impedance data (illustrative numbers, not a real part)")
    G = 0.62 * np.exp(-1j * np.deg2rad(120))
    Zic = 50 * (1 + G) / (1 - G)
    print(f"   input S11 = 0.62 /-120 deg -> Z_in = {Zic.real:.1f} {Zic.imag:+.1f}j ohm; conjugate match presents "
          f"{Zic.real:.1f} {-Zic.imag:+.1f}j")
    w915 = 2 * np.pi * 915e6
    # match: network output must present conj(Zic) to the IC; equivalently network transforms Zic to 50
    if Zic.real < 50:
        X, B = lmatch_low_r(Zic.real, Zic.imag, 50, +1)
        M = abcd_shunt(1j * B) @ abcd_series(1j * X)
    else:
        raise RuntimeError
    zz = zin(M, Zic)
    check("L-match from the S11 data gives 50 ohm", abs(zz - 50) < 1e-6, f"X {X:.2f} ohm, B {B*1e3:.2f} mS")
    Zopt = 8 + 6j
    for Zp, lab in ((Zopt, "Z_opt (correct)"), (np.conj(Zopt), "conj(Z_opt) (wrong)")):
        gp = (Zp - Zopt) / (Zp + np.conj(Zopt))
        print(f"   PA wants Z_opt = 8+6j; presenting {lab}: power-wave |Gamma| vs Z_opt = {abs(gp):.2f}")
    gw = abs((np.conj(Zopt) - Zopt) / (np.conj(Zopt) + np.conj(Zopt)))
    check("conjugating a load-pull Z_opt by mistake = |Gamma| 0.6 (VSWR 4) error", abs(gw - 0.6) < 1e-9)

    print("=== D. differential half-circuit, Zd = 30 - j60 ohm to 100 ohm differential, 915 MHz")
    Zd = 30 - 60j
    X, B = lmatch_low_r(Zd.real / 2, Zd.imag / 2, 50.0, +1)
    Lleg = X / w915; Ch = B / w915
    Cacross = Ch / 2
    Zfull = 1 / (1j * w915 * Cacross + 1 / (2 * 1j * X + Zd))
    print(f"   half circuit 15 - j30 -> 50: series +{X:.2f} ohm ({Lleg*1e9:.2f} nH per leg), shunt {Ch*1e12:.2f} pF to "
          f"virtual ground -> one {Cacross*1e12:.2f} pF across the pair")
    check("full differential network presents 100 ohm", abs(Zfull - 100) < 1e-6, f"{Zfull:.3f}")
    Lh = 50e-9
    Zacross_L = 2 * 1j * w915 * Lh
    Zh = 1j * w915 * Lh
    check("shunt L in the half circuit -> 2L across the pair", np.isclose(Zacross_L / 2, Zh))

    print("=== E. high-impedance detector match (HSMS-2850-like) at 915 MHz")
    Rs, Rv, Cj = 25.0, 9.1e3, 0.18e-12
    QL, QC = 40.0, 300.0
    fs = np.linspace(800e6, 1030e6, 2301)

    def zd(f):
        return Rs + Rv / (1 + 1j * 2 * np.pi * f * Rv * Cj)

    Zd0 = zd(915e6)
    # topology: series L at the diode (cancels the large -jX and sets R), shunt C toward the 50-ohm source
    # Zd0.real ~ 120 ohm > 50 -> use shunt-then-series? Use Pozar R_L > Z0 form (shunt at load, series toward source).
    RL, XL = Zd0.real, Zd0.imag
    Bsh = (XL + np.sqrt(RL / 50) * np.sqrt(RL ** 2 + XL ** 2 - 50 * RL)) / (RL ** 2 + XL ** 2)
    Xse = 1 / Bsh + XL * 50 / RL - 50 / (Bsh * RL)
    print(f"   diode Z at 915 MHz = {RL:.1f} {XL:+.1f}j ohm; shunt B {Bsh*1e3:.3f} mS, series X {Xse:.1f} ohm")

    def p_rv(f, matched, lossy=True):
        w_ = 2 * np.pi * f
        Zl = zd(f)
        if matched:
            # shunt element across the diode (B>0: capacitor; B<0: inductor), then series element
            if Bsh > 0:
                Csh = Bsh / (2 * np.pi * 915e6); Ysh = 1j * w_ * Csh * (1 - 1j / QC if lossy else 1)
            else:
                Lsh = -1 / (Bsh * 2 * np.pi * 915e6); Ysh = 1 / (1j * w_ * Lsh * (1 - 1j / QL if lossy else 1))
            if Xse > 0:
                Lse = Xse / (2 * np.pi * 915e6); Zse = 1j * w_ * Lse * (1 - 1j / QL if lossy else 1)
            else:
                Cse = -1 / (Xse * 2 * np.pi * 915e6); Zse = 1 / (1j * w_ * Cse * (1 - 1j / QC if lossy else 1))
            M = abcd_series(Zse) @ abcd_shunt(Ysh)
        else:
            M = abcd_shunt(1 / 50.0)                 # broadband 50-ohm shunt termination
        # source 1 V-peak-equivalent with 50 ohm: available power 1/(8*50) W; solve node voltages
        Vs = 1.0
        A, B_, Cc, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
        Zin_ = (A * Zl + B_) / (Cc * Zl + D)
        Vin = Vs * Zin_ / (Zin_ + 50)
        Iin = Vin / Zin_
        # output voltage at load: [V2; I2] = inv(M) [V1; I1]
        V2, I2 = np.linalg.solve(M, np.array([Vin, Iin]))
        Vj = V2 * (Rv / (1 + 1j * w_ * Rv * Cj)) / Zl
        return abs(Vj) ** 2 / (2 * Rv) / (Vs ** 2 / (8 * 50))

    pm = np.array([p_rv(f, True) for f in fs]); pr = np.array([p_rv(f, False) for f in fs])
    pm_ideal = p_rv(915e6, True, lossy=False)
    gain_db = 10 * np.log10(pm.max() / pr[np.argmin(abs(fs - 915e6))])
    band = fs[pm > pm.max() / 2]
    print(f"   fraction of available power reaching Rv: resistive {pr[np.argmin(abs(fs-915e6))]:.4f}, "
          f"matched ideal {pm_ideal:.3f}, matched Q_L 40 {pm.max():.3f}")
    print(f"   sensitivity gain of the reactive match {gain_db:.1f} dB (ideal limit 10log(Rv/50 x ...) ), "
          f"-3 dB bandwidth {(band.max()-band.min())/1e6:.0f} MHz")
    check("reactive match gains > 15 dB of detector sensitivity over a 50-ohm termination", gain_db > 15,
          f"{gain_db:.1f} dB")
    bwf = (band.max() - band.min()) / 915e6
    check("faithful: with Rs = 25 ohm and Q_L 40 the -3 dB band is 10-30 % (covers 902-928 MHz easily)",
          0.10 < bwf < 0.30, f"{bwf*100:.1f} %")
    check("finite inductor Q costs > 1 dB of the ideal match", 10 * np.log10(pm_ideal / pm.max()) > 1.0,
          f"{10*np.log10(pm_ideal/pm.max()):.2f} dB")

    print("=== F. interstage: 3 - j2 ohm final-stage input to a 25 ohm driver load, 433 MHz")
    Zg = 3 - 2j

    def lossy_l(Zload, R0, QL_=40.0, QC_=300.0):
        X, B = lmatch_low_r(Zload.real, Zload.imag, R0, +1)
        Ls = X / w433; Cp = B / w433
        Ms = abcd_shunt(1j * w433 * Cp * (1 - 1j / QC_)) @ abcd_series(1j * w433 * Ls * (1 - 1j / QL_))
        return Ms, np.sqrt(R0 / Zload.real - 1)

    def eff(M, Zload, Rsrc):
        Zi = zin(M, Zload)
        V1 = 1.0; I1 = V1 / Zi
        V2, I2 = np.linalg.solve(M, np.array([V1, I1]))
        return (abs(I2) ** 2 * Zload.real) / (abs(I1) ** 2 * Zi.real), Zi

    Md, qd = lossy_l(Zg, 25.0)
    ed, zid = eff(Md, Zg, 25)
    M1, q1 = lossy_l(Zg, 50.0)
    # second section 50 -> 25: R_L = 50 > 25, shunt at the 50-ohm side... use low-R form from 25 viewed backwards:
    # network seen from the driver: series element at the 25-ohm (driver) side, shunt at the 50-ohm node.
    Q2 = np.sqrt(50 / 25 - 1)
    Xs2 = Q2 * 25; Bp2 = Q2 / 50
    M2 = abcd_series(1j * Xs2 * (1 - 1j / 40)) @ abcd_shunt(1j * Bp2 * (1 - 1j / 300))
    Mv = M2 @ M1
    ev, ziv = eff(Mv, Zg, 25)
    print(f"   direct: Q_n {qd:.2f}, Z seen by driver {zid:.2f}, efficiency {ed*100:.1f} % ({10*np.log10(ed):.2f} dB)")
    print(f"   via 50 ohm: Q {q1:.2f} then {Q2:.2f}, Z seen {ziv:.2f}, efficiency {ev*100:.1f} % ({10*np.log10(ev):.2f} dB)")
    check("direct interstage match is less lossy than going through 50 ohm", ed > ev)

    print("=== G. double-stub tuner: forbidden region and solution")
    rng = np.random.default_rng(1)
    for d_l in (1 / 8, 3 / 16, 3 / 8):
        t = np.tan(2 * np.pi * d_l)
        gmax = (1 + t ** 2) / t ** 2
        ok = True
        for _ in range(300):
            g = rng.uniform(0.05, 6); b = rng.uniform(-4, 4)
            b1s = np.linspace(-60, 60, 24001)
            y1 = g + 1j * (b + b1s)
            y2 = (y1 + 1j * t) / (1 + 1j * t * y1)
            reachable = np.any(np.diff(np.sign(y2.real - 1)) != 0)
            if reachable != (g <= gmax):
                if abs(g - gmax) > 0.02:
                    ok = False
        check(f"d = {d_l:.4f} lambda: matchable iff g <= 1/sin^2(beta d) = {gmax:.3f} (brute force, 300 loads)", ok)
    # closed-form solution at d = lambda/8 for y = 0.4 - j0.8 (matchable) and skrf check
    d_l = 1 / 8; t = np.tan(2 * np.pi * d_l)
    g, b = 0.4, -0.8
    root = np.sqrt((1 + t ** 2) * g - g ** 2 * t ** 2)
    b1 = -b + (1 + root) / t
    b2 = (root + g) / (g * t)
    y1 = g + 1j * (b + b1)
    y2 = (y1 + 1j * t) / (1 + 1j * t * y1)
    print(f"   y_L = {g} {b:+}j at stub 1, d = lambda/8: b1 = {b1:.4f}, b2 = {b2:.4f}; y after stub 2 = {y2 + 1j*b2:.6f}")
    check("Pozar-form double-stub solution matches (y = 1)", abs(y2 + 1j * b2 - 1) < 1e-9)
    # skrf: 2.45 GHz, ideal 50 ohm lines, open stubs
    freq = rf.Frequency(2.45, 2.45, 1, unit="GHz")
    med = rf.media.DefinedGammaZ0(frequency=freq, z0=50, gamma=1j * 2 * np.pi * 2.45e9 / C0)
    lam = C0 / 2.45e9
    yl = (g + 1j * b) / 50
    load = med.load((1 / yl - 50) / (1 / yl + 50))

    def open_stub_len(bn):
        L_ = np.arctan(bn) / (2 * np.pi) * lam
        return L_ if L_ > 0 else L_ + lam / 2

    net = med.shunt(med.line(open_stub_len(b2), "m") ** med.open()) ** med.line(d_l * lam, "m") ** \
        med.shunt(med.line(open_stub_len(b1), "m") ** med.open()) ** load
    check("skrf cascade of the double-stub design: |S11| < 1e-6", abs(net.s[0, 0, 0]) < 1e-6,
          f"{abs(net.s[0,0,0]):.1e}")
    # escape: g = 3 at d = lambda/8 is forbidden; add lambda/8 of line between load and stub 1
    yb = 3.0 + 0.0j
    yb2 = (yb + 1j * 1.0) / (1 + 1j * 1.0 * yb)     # lambda/8 line: t = 1
    check("forbidden load g = 3 becomes matchable after lambda/8 of extra line", yb2.real <= 2.0,
          f"g -> {yb2.real:.2f}")
    print("\nALL PASS" if all(PASS) else "\nSOME CHECKS FAILED")


if __name__ == "__main__":
    main()
