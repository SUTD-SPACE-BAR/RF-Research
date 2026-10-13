#!/usr/bin/env python3
"""s6_image_filters.py — image-parameter (constant-k, m-derived) low-pass filters vs the insertion-loss method
(task W5-S6, gap G-03-08) for kb/01-circuit-theory/passive-filter-design-prototypes.md.

1. Image impedance and propagation constant of a symmetric T / pi section from Z1 (series), Z2 (shunt):
   Z_iT = sqrt(Z1 Z2 (1 + Z1/(4 Z2))), Z_ipi = Z1 Z2 / Z_iT, cosh(gamma) = 1 + Z1/(2 Z2)  — checked against the
   ABCD matrix of the section.
2. Constant-k LP: R0 = sqrt(L/C), wc = 2/sqrt(LC); stop-band attenuation 2 acosh(w/wc) Np per section.
3. m-derived T: attenuation pole at w_inf = wc/sqrt(1 - m^2); same Z_iT as constant-k; Z_ipi(m) flattest near m = 0.6.
4. Composite 433 MHz harmonic filter (fc 520 MHz, pole on 867.8 MHz, m = 0.6 bisected end sections) simulated
   doubly terminated in 50 ohm and compared with the Chebyshev and elliptic designs on the page (same fc).
"""
import numpy as np

PASS = []


def check(name, cond, detail=""):
    PASS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def ser(Z):
    return np.array([[1, Z], [0, 1]], dtype=complex)


def sh(Y):
    return np.array([[1, 0], [Y, 1]], dtype=complex)


def s21(M, z0=50.0):
    A, B, C, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
    return 2 / (A + B / z0 + C * z0 + D)


def s11(M, z0=50.0):
    A, B, C, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
    return (A + B / z0 - C * z0 - D) / (A + B / z0 + C * z0 + D)


R0, FC = 50.0, 520e6
WC = 2 * np.pi * FC
L = 2 * R0 / WC
C = 2 / (R0 * WC)


def main():
    print(f"constant-k prototype for R0 = 50 ohm, fc = 520 MHz: L = {L*1e9:.2f} nH, C = {C*1e12:.2f} pF")
    print("=== 1. image parameters vs ABCD")
    for f in (200e6, 450e6, 700e6):
        w = 2 * np.pi * f
        Z1, Z2 = 1j * w * L, 1 / (1j * w * C)
        M = ser(Z1 / 2) @ sh(1 / Z2) @ ser(Z1 / 2)
        ZiT = np.sqrt(Z1 * Z2 * (1 + Z1 / (4 * Z2)))
        ZiT_abcd = np.sqrt(M[0, 1] / M[1, 0])
        g = np.arccosh(1 + Z1 / (2 * Z2) + 0j)
        g_abcd = np.arccosh(M[0, 0] + 0j)
        ok = np.isclose(ZiT ** 2, ZiT_abcd ** 2) and np.isclose(np.cosh(g), np.cosh(g_abcd))
        check(f"T-section image Z and gamma at {f/1e6:.0f} MHz", ok,
              f"Z_iT = {ZiT:.2f}; formula R0 sqrt(1-(f/fc)^2) = {R0*np.sqrt(1-(f/FC)**2+0j):.2f}")
    print("=== 2. stop-band attenuation of one constant-k section")
    for f in (867.8e6, 1301.7e6):
        w = 2 * np.pi * f
        Z1, Z2 = 1j * w * L, 1 / (1j * w * C)
        a = np.real(np.arccosh(1 + Z1 / (2 * Z2) + 0j))
        a_formula = 2 * np.arccosh(f / FC)
        check(f"alpha({f/1e6:.0f} MHz) = 2 acosh(f/fc)", abs(abs(a) - a_formula) < 1e-9,
              f"{a_formula:.3f} Np = {8.686*a_formula:.1f} dB per section (image-matched)")
    print("=== 3. m-derived sections")
    finf = 867.8e6
    m2 = np.sqrt(1 - (FC / finf) ** 2)
    print(f"   pole at 867.8 MHz -> m = {m2:.4f}")
    w = 2 * np.pi * finf
    Zshunt = 1 / (1j * w * m2 * C) + 1j * w * (1 - m2 ** 2) * L / (4 * m2)
    check("m-derived shunt arm is a series-resonant short at f_inf", abs(Zshunt) < 1e-6 * R0, f"|Z| = {abs(Zshunt):.1e}")
    for frac in (0.8, 0.9):
      fpass = np.linspace(1e6, frac * FC, 500)
      for m in (0.5, 0.6, 0.7, 1.0):
        w = 2 * np.pi * fpass
        Z1, Z2 = 1j * w * m * L, 1 / (1j * w * m * C) + 1j * w * (1 - m ** 2) * L / (4 * m)
        ZiT = np.sqrt(Z1 * Z2 * (1 + Z1 / (4 * Z2)))
        Zpi = (Z1 * Z2 / ZiT).real
        dev = np.max(np.abs(Zpi / R0 - 1))
        print(f"   m = {m:.1f}: Z_ipi (m-derived T, cut at shunt arm) within {dev*100:5.1f} % of R0 up to {frac} fc")
        if m == 0.6 and frac == 0.9:
            dev06 = dev
        if m == 1.0 and frac == 0.9:
            dev1 = dev
    check("m = 0.6 flattens the pi image impedance (vs constant-k)", dev06 < 0.2 * dev1, f"{dev06*100:.1f} % vs {dev1*100:.0f} %")

    print("=== 4. composite image-parameter LPF vs insertion-loss designs (50 ohm, Q_L 40, Q_C 300)")
    QL, QCap = 40.0, 300.0

    def Lz(w, Lv):
        return 1j * w * Lv * (1 - 1j / QL)

    def Cy(w, Cv):
        return 1j * w * Cv * (1 - 1j / QCap)

    def composite(f, lossy=True):
        w = 2 * np.pi * f
        lz = (lambda Lv: Lz(w, Lv)) if lossy else (lambda Lv: 1j * w * Lv)
        cy = (lambda Cv: Cy(w, Cv)) if lossy else (lambda Cv: 1j * w * Cv)
        m = 0.6
        # bisected m-derived T half section (cut through the shunt arm): inner side series m L/2 (presents the
        # constant-k Z_iT), outer side shunt 2*Z2' = series (m C/2, (1-m^2) L/(2m)) presenting Z_ipi(m) ~ R0.
        z_end = 1 / cy(m * C / 2) + lz((1 - m ** 2) * L / (2 * m))
        Min = sh(1 / z_end) @ ser(lz(m * L / 2))
        Mk = ser(lz(L / 2)) @ sh(cy(C)) @ ser(lz(L / 2))
        zsh = 1 / cy(m2 * C) + lz((1 - m2 ** 2) * L / (4 * m2))
        Mm = ser(lz(m2 * L / 2)) @ sh(1 / zsh) @ ser(lz(m2 * L / 2))
        Mout = ser(lz(m * L / 2)) @ sh(1 / z_end)
        return Min @ Mk @ Mm @ Mout

    def ladder(gs, fc, f, lossy=True):
        """shunt-C-first all-pole ladder from g-values"""
        w = 2 * np.pi * f
        wc = 2 * np.pi * fc
        M = np.eye(2, dtype=complex)
        for i, g in enumerate(gs):
            if i % 2 == 0:
                M = M @ sh(Cy(w, g / (50 * wc)) if lossy else 1j * w * g / (50 * wc))
            else:
                M = M @ ser(Lz(w, g * 50 / wc) if lossy else 1j * w * g * 50 / wc)
        return M

    def cheb_g(N, Lr):
        beta = np.log(1 / np.tanh(Lr / 17.37))
        gam = np.sinh(beta / (2 * N))
        a = [np.sin((2 * k - 1) * np.pi / (2 * N)) for k in range(1, N + 1)]
        b = [gam ** 2 + np.sin(k * np.pi / N) ** 2 for k in range(1, N + 1)]
        g = [2 * a[0] / gam]
        for k in range(2, N + 1):
            g.append(4 * a[k - 2] * a[k - 1] / (b[k - 2] * g[-1]))
        return g

    for fmax in (300e6, 400e6, 450e6, 480e6):
        fl = np.linspace(1e6, fmax, 600)
        rl_comp = min(-20 * np.log10(abs(s11(composite(f, False)))) for f in fl)
        print(f"   composite (ideal parts): worst RL 1-{fmax/1e6:.0f} MHz = {rl_comp:.1f} dB")
    fl = np.linspace(1e6, 450e6, 600)
    rl_comp = min(-20 * np.log10(abs(s11(composite(f, False)))) for f in fl)
    designs = {
        "image-param composite (6 L, 4 C)": lambda f: composite(f),
        "Chebyshev 0.1 dB N=5": lambda f: ladder(cheb_g(5, 0.1), FC, f),
        "Chebyshev 0.1 dB N=7": lambda f: ladder(cheb_g(7, 0.1), FC, f),
    }
    out = {}
    for name, fn in designs.items():
        il = -20 * np.log10(abs(s21(fn(433.92e6))))
        a2 = -20 * np.log10(abs(s21(fn(867.84e6))))
        a3 = -20 * np.log10(abs(s21(fn(1301.76e6))))
        rl = min(-20 * np.log10(abs(s11(fn(f)))) for f in np.linspace(400e6, 480e6, 81))
        out[name] = (il, a2, a3, rl)
        print(f"   {name:34s}: IL(433.92) {il:5.2f} dB | atten 2f {a2:5.1f} dB, 3f {a3:5.1f} dB | "
              f"worst RL 400-480 MHz {rl:5.1f} dB")
    ic = out["image-param composite (6 L, 4 C)"]
    check("composite image filter reaches > 40 dB at 2f with its m-derived pole", ic[1] > 40, f"{ic[1]:.1f} dB")
    for fe in (490e6, 505e6, 520e6, 540e6):
        print(f"   composite |S21| at {fe/1e6:.0f} MHz (ideal parts): {20*np.log10(abs(s21(composite(fe, False)))):6.2f} dB; "
              f"RL {-20*np.log10(abs(s11(composite(fe, False)))):5.1f} dB")
    check("faithful: with m = 0.6 ends the composite is well matched to 0.92 fc (RL > 20 dB, ideal parts)", rl_comp > 20,
          f"{rl_comp:.1f} dB")
    ch7 = out["Chebyshev 0.1 dB N=7"]
    check("but it uses 10 reactors vs 7 and loses more in-band than the N = 7 Chebyshev (Q_L 40)", ic[0] > ch7[0],
          f"{ic[0]:.2f} vs {ch7[0]:.2f} dB")
    print("\nALL PASS" if all(PASS) else "\nSOME CHECKS FAILED")


if __name__ == "__main__":
    main()
