#!/usr/bin/env python3
"""
em_quasistatic.py — checks for kb/02-electromagnetics/quasi-static-vs-full-wave.md

1. Error of a lumped L or C model of a short transmission-line stub vs exact tan/cot: (beta l)^2/3 rule.
2. Error of a lumped series-L/shunt-C (single pi or T section) model of a matched line: phase and |S11|.
3. Radiation resistance of a short straight wire and a small loop vs electrical size (how 'lumped'
   circuits start to radiate).
4. Electrical lengths for Marcus's bands on FR-4 microstrip; rise-time critical lengths using
   different published rules (t_r/6, t_r/5, t_r/2 per t_pd).
5. Haus & Melcher time constants: tau_em = l/c, tau_e = eps/sigma, tau_m = mu sigma l^2,
   and identity tau_em^2 = tau_e * tau_m.
"""
import numpy as np

c = 299_792_458.0
mu0 = 1.25663706127e-6
eps0 = 1 / (mu0 * c**2)
eta0 = mu0 * c

print("=== 1. short stub: lumped vs exact reactance ===")
for frac in (1/50, 1/20, 1/10, 1/8, 1/6):
    bl = 2 * np.pi * frac
    err_short = (np.tan(bl) - bl) / np.tan(bl)       # lumped L underestimates
    err_open = (1 / np.tan(bl) - 1 / bl) / (1 / np.tan(bl))  # lumped C
    print(f"  l = lambda/{1/frac:4.0f} (beta l = {np.degrees(bl):5.1f} deg): shorted-stub L error {err_short*100:6.2f} %, "
          f"open-stub C error {abs(err_open)*100:6.2f} %, (beta l)^2/3 = {bl**2/3*100:6.2f} %")

print("\n=== 2. matched line modelled as one LC pi-section ===")
Z0 = 50.0
for frac in (1/50, 1/20, 1/10, 1/5):
    bl = 2 * np.pi * frac
    # exact ABCD of line
    A = np.cos(bl); B = 1j * Z0 * np.sin(bl); C = 1j * np.sin(bl) / Z0; D = A
    # pi: shunt C/2, series L, shunt C/2 with L = Z0*bl/w, C = bl/(w Z0) -> use normalised: X_L = Z0 bl, B_C = bl/Z0
    XL = Z0 * bl; Bc = bl / Z0
    Ysh = 1j * Bc / 2
    M = np.array([[1, 0], [Ysh, 1]]) @ np.array([[1, 1j * XL], [0, 1]]) @ np.array([[1, 0], [Ysh, 1]])
    def s21_s11(M):
        A_, B_, C_, D_ = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
        den = A_ + B_ / Z0 + C_ * Z0 + D_
        return 2 / den, (A_ + B_ / Z0 - C_ * Z0 - D_) / den
    s21e, s11e = s21_s11(np.array([[A, B], [C, D]]))
    s21p, s11p = s21_s11(M)
    print(f"  l = lambda/{1/frac:3.0f}: exact phase {np.degrees(np.angle(s21e)):7.2f} deg, pi-model {np.degrees(np.angle(s21p)):7.2f} deg, "
          f"pi-model |S11| = {abs(s11p):.4f} ({20*np.log10(abs(s11p)+1e-15):6.1f} dB)")

print("\n=== 3. radiation resistance vs electrical size ===")
for frac in (1/100, 1/50, 1/20, 1/10):
    Rdip = 80 * np.pi**2 * frac**2              # short dipole, uniform current (Hertzian)
    Rdip_tri = 20 * np.pi**2 * frac**2          # short dipole, triangular current (open ends)
    # small loop of circumference C = frac*lambda: R = 20 pi^2 (C/lambda)^4
    Rloop = 20 * np.pi**2 * frac**4
    print(f"  size = lambda/{1/frac:4.0f}: Hertzian dipole (uniform I) {Rdip:8.4f} ohm; short dipole (triangular I) {Rdip_tri:8.4f} ohm; "
          f"loop of circumference lambda/{1/frac:.0f}: {Rloop:.3e} ohm")

print("\n=== 4. electrical lengths on FR-4 microstrip (eps_eff ~ 3.3) and stripline (4.4) ===")
for f in (13.56e6, 100e6, 433e6, 915e6, 1.57542e9, 2.45e9, 5.8e9):
    lam_ms = c / f / np.sqrt(3.3); lam_sl = c / f / np.sqrt(4.4)
    print(f"  f={f/1e6:8.2f} MHz: lambda0={c/f*100:8.2f} cm; microstrip lambda_g={lam_ms*100:7.2f} cm -> lambda/10 {lam_ms*100:6.1f} mm, lambda/20 {lam_ms*50:6.1f} mm; "
          f"stripline lambda/10 {lam_sl*100:6.1f} mm")
tpd_ms = np.sqrt(3.3) / c           # s/m
tpd_sl = np.sqrt(4.4) / c
print(f"  t_pd microstrip = {tpd_ms*1e12/1e3:.2f} ps/mm; stripline = {tpd_sl*1e12/1e3:.2f} ps/mm")
for tr in (0.1e-9, 0.5e-9, 1e-9, 2e-9, 5e-9):
    l6 = tr / (6 * tpd_ms); l5 = tr / (5 * tpd_ms); l2 = tr / (2 * tpd_ms)
    print(f"  t_r = {tr*1e9:4.1f} ns: lumped if l < t_r/(6 t_pd) = {l6*1e3:6.1f} mm | t_r/(5 t_pd) = {l5*1e3:6.1f} mm | "
          f"'critical length' t_r/(2 t_pd) = {l2*1e3:6.1f} mm; f_knee=0.5/t_r={0.5/tr/1e6:7.0f} MHz, BW 0.35/t_r={0.35/tr/1e6:7.0f} MHz")

print("\n=== 5. Haus & Melcher quasistatic time constants ===")
for name, sigma, er, l in (("copper, 10 cm", 5.8e7, 1, 0.1), ("sea water, 1 m", 5.0, 70, 1.0), ("FR-4 (sigma~1e-12), 10 cm", 1e-12, 4.4, 0.1),
                           ("human body (sigma~0.5, er~50), 0.3 m", 0.5, 50, 0.3)):
    eps = er * eps0
    tau_em = l * np.sqrt(mu0 * eps)
    tau_e = eps / sigma
    tau_m = mu0 * sigma * l**2
    print(f"  {name:36s}: tau_em={tau_em:.2e} s, tau_e={tau_e:.2e} s, tau_m={tau_m:.2e} s; sqrt(tau_e tau_m)={np.sqrt(tau_e*tau_m):.2e}")
    assert abs(np.sqrt(tau_e * tau_m) - tau_em) / tau_em < 1e-12
print("\nAll checks passed.")
