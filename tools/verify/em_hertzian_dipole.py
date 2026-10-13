#!/usr/bin/env python3
"""
em_hertzian_dipole.py — checks for radiation-from-currents-hertzian-dipole.md and near-field-far-field.md

1. Symbolic (sympy): from A = mu I l e^{-jkr}/(4 pi r) z_hat derive H = curl A / mu and
   E = curl H/(j w eps); compare with the textbook closed forms (1/r, 1/r^2, 1/r^3 terms).
2. Radiated power by integrating the far-field Poynting vector -> R_rad = (2 pi/3) eta (l/lambda)^2;
   compare 80 pi^2 (l/lambda)^2 (uses eta = 120 pi) with the CODATA eta0.
3. Larmor formula equivalence: P = q^2 a^2/(6 pi eps0 c^3)  <->  (1/2) I^2 R_rad with I l = j w p.
4. Complex power through a sphere of radius r: reactive part grows as 1/(kr)^3 (stored near-field energy).
5. Wave impedance |E_theta/H_phi| vs kr for electric dipole, and the dual (magnetic dipole / loop).
6. Small loop radiation resistance 20 pi^2 (C/lambda)^4 and EMC DM/CM radiation formulas (Paul/Ott form):
   E_DM = 1.316e-14 f^2 A I / r ;  E_CM = 1.257e-6 f I_C L / r (I_C per wire, 2 wires).
"""
import numpy as np
import sympy as sp

c = 299_792_458.0
mu0 = 1.25663706127e-6
eps0 = 1 / (mu0 * c**2)
eta0 = mu0 * c

# ---------- 1. symbolic fields ----------
r, th, ph = sp.symbols('r theta phi', positive=True)
k, I, l, w, mu, eps = sp.symbols('k I l omega mu epsilon', positive=True)
eta = sp.sqrt(mu / eps)
Az = mu * I * l * sp.exp(-sp.I * k * r) / (4 * sp.pi * r)
# spherical components of z_hat Az
Ar = Az * sp.cos(th)
Ath = -Az * sp.sin(th)
Aph = 0
def curl_sph(Fr, Fth, Fph):
    cr = (sp.diff(sp.sin(th) * Fph, th) - sp.diff(Fth, ph)) / (r * sp.sin(th))
    cth = (sp.diff(Fr, ph) / sp.sin(th) - sp.diff(r * Fph, r)) / r
    cph = (sp.diff(r * Fth, r) - sp.diff(Fr, th)) / r
    return cr, cth, cph
Hr, Hth, Hph = [sp.simplify(x / mu) for x in curl_sph(Ar, Ath, Aph)]
Er, Eth, Eph = [sp.simplify(x / (sp.I * w * eps)) for x in curl_sph(Hr, Hth, Hph)]
# substitute w = k / sqrt(mu eps)
Er = sp.simplify(Er.subs(w, k / sp.sqrt(mu * eps)))
Eth = sp.simplify(Eth.subs(w, k / sp.sqrt(mu * eps)))
Hph_book = sp.I * k * I * l * sp.sin(th) / (4 * sp.pi * r) * (1 + 1 / (sp.I * k * r)) * sp.exp(-sp.I * k * r)
Er_book = eta * I * l * sp.cos(th) / (2 * sp.pi * r**2) * (1 + 1 / (sp.I * k * r)) * sp.exp(-sp.I * k * r)
Eth_book = sp.I * eta * k * I * l * sp.sin(th) / (4 * sp.pi * r) * (1 + 1 / (sp.I * k * r) - 1 / (k * r)**2) * sp.exp(-sp.I * k * r)
assert sp.simplify(Hph - Hph_book) == 0
assert sp.simplify(Er - Er_book) == 0
assert sp.simplify(Eth - Eth_book) == 0
assert Hr == 0 and Hth == 0
print("1. Hertzian dipole fields from vector potential match textbook forms (H_phi, E_r, E_theta). OK")

# ---------- 2. radiated power ----------
Eth_ff = sp.I * eta * k * I * l * sp.sin(th) / (4 * sp.pi * r)
Hph_ff = Eth_ff / eta
S = sp.Rational(1, 2) * sp.re(Eth_ff * sp.conjugate(Hph_ff))
P = sp.integrate(sp.integrate(sp.simplify(S) * r**2 * sp.sin(th), (th, 0, sp.pi)), (ph, 0, 2 * sp.pi))
P = sp.simplify(P)
lam = sp.symbols('lambda', positive=True)
Rrad = sp.simplify((2 * P / I**2).subs(k, 2 * sp.pi / lam))
print("2. R_rad =", Rrad, " (expect 2 pi eta l^2 / (3 lambda^2))")
assert sp.simplify(Rrad - 2 * sp.pi * eta * l**2 / (3 * lam**2)) == 0
print(f"   (2pi/3) eta0 = {2*np.pi/3*eta0:.3f} ohm  vs 80 pi^2 = {80*np.pi**2:.3f} ohm (diff {(80*np.pi**2/(2*np.pi/3*eta0)-1)*100:.3f} %)")
print(f"   directivity: 4 pi U_max / P = 1.5 -> {10*np.log10(1.5):.3f} dBi")

# ---------- 3. Larmor ----------
q = 1e-9; f = 433e6; wv = 2 * np.pi * f; x0 = 0.01   # 1 nC oscillating with 1 cm amplitude
p = q * x0                       # peak dipole moment
a_pk = wv**2 * x0
P_larmor_avg = q**2 * a_pk**2 / (6 * np.pi * eps0 * c**3) / 2     # time-average of a^2 = a_pk^2/2
Il = wv * p                      # |I l| peak
lam_n = c / f
P_rad = 0.5 * (2 * np.pi / 3 * eta0 * (1 / lam_n)**2) * Il**2      # (1/2)|Il|^2 * (2pi/3) eta / lambda^2
print(f"3. Larmor avg power {P_larmor_avg:.6e} W vs dipole (1/2) I^2 R_rad {P_rad:.6e} W")
assert abs(P_larmor_avg - P_rad) / P_rad < 1e-9

# ---------- 4. complex power through sphere of radius r ----------
def complex_power(kr):
    # closed form: P = (eta pi/3)(Il/lambda)^2 [1 - j/(kr)^3]  (Balanis 4.2)
    return 1 - 1j / kr**3
print("4. normalised complex power through sphere vs kr: ", ", ".join(f"kr={x}: {complex_power(x):.3f}" for x in (0.1, 0.5, 1, 2, 10)))
# numeric check of the closed form by integrating (1/2) E x H* over the sphere
kk = 2 * np.pi / 1.0; Il_ = 1.0; etan = eta0
for kr in (0.3, 1.0, 3.0):
    rr = kr / kk
    thg = np.linspace(0, np.pi, 4001)
    Eth_n = 1j * etan * kk * Il_ * np.sin(thg) / (4 * np.pi * rr) * (1 + 1 / (1j * kr) - 1 / kr**2) * np.exp(-1j * kr)
    Hph_n = 1j * kk * Il_ * np.sin(thg) / (4 * np.pi * rr) * (1 + 1 / (1j * kr)) * np.exp(-1j * kr)
    Sr = 0.5 * Eth_n * np.conj(Hph_n)
    Pc = np.trapezoid(Sr * 2 * np.pi * rr**2 * np.sin(thg), thg)
    P0 = etan * np.pi / 3 * (Il_ / 1.0)**2
    print(f"   kr={kr}: numeric {Pc/P0:.4f}, closed form {complex_power(kr):.4f}")
    assert abs(Pc / P0 - complex_power(kr)) < 1e-4

# ---------- 5. wave impedance vs kr ----------
print("5. |Z_w|/eta0 at theta=90 deg: electric dipole (E_theta/H_phi) and magnetic dipole (dual)")
for kr in (0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0):
    num = 1 + 1 / (1j * kr) - 1 / kr**2
    den = 1 + 1 / (1j * kr)
    Ze = num / den
    Zm = den / num
    r_over_lam = kr / (2 * np.pi)
    print(f"   kr={kr:6.2f} (r = {r_over_lam:6.3f} lambda): |Z_E| = {abs(Ze)*eta0:9.1f} ohm, |Z_M| = {abs(Zm)*eta0:8.2f} ohm")
# asymptote: |Z_E| ~ eta/(kr) for kr<<1
assert abs(abs((1 + 1/(1j*0.01) - 1/0.01**2)/(1 + 1/(1j*0.01))) - 1/0.01) / (1/0.01) < 1e-3

# ---------- 6. small loop and EMC formulas ----------
print("6. small loop R_rad = 20 pi^2 (C/lambda)^4 = 320 pi^4 A^2/lambda^4")
for f in (433e6, 915e6):
    lam_n = c / f
    for dia in (0.01, 0.03, 0.05):
        A = np.pi * (dia / 2)**2
        C = np.pi * dia
        R1 = 20 * np.pi**2 * (C / lam_n)**4
        R2 = 320 * np.pi**4 * A**2 / lam_n**4
        assert abs(R1 - R2) / R1 < 1e-12
        print(f"   f={f/1e6:.0f} MHz, loop dia {dia*100:.0f} cm: R_rad = {R1*1e3:.3f} mOhm")
kDM = eta0 * np.pi / c**2
kCM = eta0 / (2 * c) * 2   # two wires each carrying I_C
print(f"   E_DM = {kDM:.4e} f^2 A I / r  (Paul: 1.316e-14);  E_CM = {kCM:.4e} f I_C L / r (Paul: 1.257e-6)")
assert abs(kDM - 1.316e-14) / 1.316e-14 < 2e-3 and abs(kCM - 1.257e-6) / 1.257e-6 < 2e-3
# example: CM current allowed at 100 MHz for 150 uV/m at 3 m (FCC class B 88-216 MHz), 1 m cable
E_lim, d, f, L = 150e-6, 3.0, 100e6, 1.0
print(f"   CM current on 1 m cable giving 150 uV/m at 3 m, 100 MHz: {E_lim*d/(kCM*f*L)*1e6:.2f} uA (per wire)")
print(f"   DM current in 1 cm^2 loop giving 150 uV/m at 3 m, 100 MHz: {E_lim*d/(kDM*f**2*1e-4)*1e3:.1f} mA")
print("\nAll checks passed.")
