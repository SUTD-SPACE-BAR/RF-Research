#!/usr/bin/env python3
"""
em_waveguides.py — checks for kb/02-electromagnetics/waveguides-and-cavity-resonators.md

1. Rectangular waveguide cutoff frequencies (WR-90, WR-430, WR-650, WR-975, WR-2300); mode ordering.
2. beta, lambda_g, v_p, v_g, Z_TE, Z_TM vs f for WR-90; check v_p v_g = c^2.
3. TE10 conductor attenuation (Pozar closed form) vs a numeric perturbation integral; copper WR-90 and
   WR-430.
4. Circular waveguide cutoffs from Bessel zeros (TE11, TM01, TE21, TE01).
5. Below-cutoff attenuation: dB per width (rectangular TE10) and per diameter (circular TE11) —
   'waveguide-beyond-cutoff' vents.
6. Rectangular cavity TE101: f0 and conductor Q (Pozar), dielectric Q = 1/tan d; 1/Q = 1/Qc + 1/Qd.
   Also numeric check of Qc by energy/loss integration.
7. PCB power/ground plane cavity resonances for a 100 x 50 mm FR-4 board.
8. SIW equivalent width (Cassivi/Deslandes-Wu) and cutoff on RO4003C.
"""
import numpy as np
from scipy import special, integrate

c = 299_792_458.0
mu0 = 1.25663706127e-6
eps0 = 1 / (mu0 * c**2)
eta0 = mu0 * c
inch = 25.4e-3

def fc_rect(a, b, m, n, er=1.0):
    return c / (2 * np.pi * np.sqrt(er)) * np.sqrt((m * np.pi / a)**2 + (n * np.pi / b)**2)

print("=== 1. rectangular waveguide cutoffs ===")
guides = {"WR-90": (0.900 * inch, 0.400 * inch), "WR-430": (4.300 * inch, 2.150 * inch),
          "WR-650": (6.500 * inch, 3.250 * inch), "WR-975": (9.750 * inch, 4.875 * inch),
          "WR-2300": (23.0 * inch, 11.5 * inch)}
for name, (a, b) in guides.items():
    modes = sorted([(fc_rect(a, b, m, n), f"TE{m}{n}" + ("/TM" + f"{m}{n}" if m and n else ""))
                    for m in range(0, 3) for n in range(0, 3) if (m, n) != (0, 0)])[:5]
    f10 = fc_rect(a, b, 1, 0)
    print(f"  {name}: a={a*1e3:.2f} mm b={b*1e3:.2f} mm; fc(TE10)={f10/1e9:.4f} GHz; "
          f"recommended band ~1.25-1.9 fc = {1.25*f10/1e9:.3f}-{1.9*f10/1e9:.3f} GHz; first modes: "
          + ", ".join(f"{m} {f/1e9:.3f}" for f, m in modes))

print("\n=== 2. WR-90 TE10 dispersion ===")
a, b = guides["WR-90"]
f10 = fc_rect(a, b, 1, 0)
for f in (7e9, 8e9, 10e9, 12e9):
    k = 2 * np.pi * f / c
    kc = np.pi / a
    beta = np.sqrt(k**2 - kc**2)
    lg = 2 * np.pi / beta
    vp = 2 * np.pi * f / beta
    vg = c**2 / vp
    ZTE = eta0 * k / beta
    ZTM = eta0 * beta / k
    # numeric group velocity
    df = 1e3
    b2 = np.sqrt((2 * np.pi * (f + df) / c)**2 - kc**2)
    vg_num = 2 * np.pi * df / (b2 - beta)
    print(f"  f={f/1e9:5.1f} GHz: lambda_g={lg*1e3:6.2f} mm (lambda0 {c/f*1e3:.2f}), vp/c={vp/c:.4f}, vg/c={vg/c:.4f} "
          f"(numeric {vg_num/c:.4f}), Z_TE={ZTE:.1f} ohm, Z_TM(same beta)={ZTM:.1f} ohm")
    assert abs(vg - vg_num) / vg < 1e-3

print("\n=== 3. TE10 conductor attenuation ===")
def alpha_c_TE10(f, a, b, sigma=5.8e7):
    k = 2 * np.pi * f / c
    beta = np.sqrt(k**2 - (np.pi / a)**2)
    Rs = np.sqrt(np.pi * f * mu0 / sigma)
    return Rs / (a**3 * b * beta * k * eta0) * (2 * b * np.pi**2 + a**3 * k**2)   # Pozar eq. (3.96)
def alpha_c_numeric(f, a, b, sigma=5.8e7):
    """perturbation: alpha = P_loss'/(2P); TE10 fields with amplitude A: Ey = A sin(pi x/a),
    Hx = -(beta/(w mu)) A sin(pi x/a), Hz = j (pi/(a w mu)) A cos(pi x/a)."""
    w = 2 * np.pi * f; k = w / c
    beta = np.sqrt(k**2 - (np.pi / a)**2)
    Rs = np.sqrt(np.pi * f * mu0 / sigma)
    A = 1.0
    Hx = lambda x: beta / (w * mu0) * A * np.sin(np.pi * x / a)
    Hz = lambda x: np.pi / (a * w * mu0) * A * np.cos(np.pi * x / a)
    P = 0.5 * integrate.quad(lambda x: (A * np.sin(np.pi * x / a)) * Hx(x), 0, a)[0] * b
    # walls: top & bottom (y=0,b): tangential Hx and Hz; side walls (x=0,a): tangential Hz (Hy=0)
    Ptop = 2 * 0.5 * Rs * integrate.quad(lambda x: Hx(x)**2 + Hz(x)**2, 0, a)[0]
    Pside = 2 * 0.5 * Rs * Hz(0)**2 * b
    return (Ptop + Pside) / (2 * P)
for name in ("WR-90", "WR-430"):
    a, b = guides[name]
    for f in ((8e9, 10e9, 12e9) if name == "WR-90" else (1.8e9, 2.45e9, 2.6e9)):
        ac = alpha_c_TE10(f, a, b); an = alpha_c_numeric(f, a, b)
        print(f"  {name} Cu f={f/1e9:5.2f} GHz: alpha_c = {ac*8.686:.4f} dB/m (numeric {an*8.686:.4f}) = {ac*8.686*0.3048:.4f} dB/ft")
        assert abs(ac - an) / ac < 1e-6
# compare with coax at 10 GHz: RG-402 semi-rigid ~ 1.2-1.4 dB/m? (not asserted)

print("\n=== 4. circular waveguide cutoffs (radius 10 mm) ===")
R = 10e-3
jp = {"TE11": special.jnp_zeros(1, 1)[0], "TM01": special.jn_zeros(0, 1)[0], "TE21": special.jnp_zeros(2, 1)[0],
      "TE01": special.jnp_zeros(0, 1)[0], "TM11": special.jn_zeros(1, 1)[0]}
for m, x in sorted(jp.items(), key=lambda t: t[1]):
    print(f"  {m}: p = {x:.4f}, fc = {c*x/(2*np.pi*R)/1e9:.3f} GHz")

print("\n=== 5. below-cutoff attenuation (f << fc) ===")
print(f"  rectangular TE10: alpha ~ pi/a -> {8.686*np.pi:.2f} dB per length equal to width a")
print(f"  circular TE11: alpha ~ 1.8412/R -> {8.686*1.8412*2:.2f} dB per length equal to diameter")
for f_over_fc in (0.1, 0.3, 0.5, 0.8):
    print(f"   at f/fc = {f_over_fc}: attenuation reduced by factor sqrt(1-(f/fc)^2) = {np.sqrt(1-f_over_fc**2):.3f}")
# vent example: 5 mm hole, 10 mm long, at 2.45 GHz
Dh, Lh, f = 5e-3, 10e-3, 2.45e9
fc = c * 1.8412 / (2 * np.pi * Dh / 2)
alpha = 2 * np.pi / c * np.sqrt(fc**2 - f**2)
print(f"  5 mm dia hole, 10 mm deep: fc(TE11) = {fc/1e9:.1f} GHz; attenuation at 2.45 GHz = {8.686*alpha*Lh:.1f} dB")

print("\n=== 6. rectangular cavity TE101 ===")
def cavity_TE101(a, b, d, sigma=5.8e7, er=1.0, tand=0.0):
    f0 = c / (2 * np.sqrt(er)) * np.sqrt((1 / a)**2 + (1 / d)**2)
    k = 2 * np.pi * f0 * np.sqrt(er) / c
    eta = eta0 / np.sqrt(er)
    Rs = np.sqrt(np.pi * f0 * mu0 / sigma)
    Qc = (k * a * d)**3 * b * eta / (2 * np.pi**2 * Rs) / (2 * a**3 * b + 2 * b * d**3 + a**3 * d + a * d**3)
    Qd = 1 / tand if tand > 0 else np.inf
    Q = 1 / (1 / Qc + 1 / Qd)
    return f0, Qc, Qd, Q
for (a, b, d, er, td, label) in ((22.86e-3, 10.16e-3, 22.2e-3, 1.0, 0, "WR-90 section, air"),
                                  (0.0866, 0.04, 0.0866, 1.0, 0, "2.45 GHz cube-ish air cavity (a=d=86.6 mm, b=40 mm)"),
                                  (0.0866, 0.04, 0.0866, 1.0, 1e-4, "same with a PTFE-like loss tan 1e-4 (filled? no, illustrative)")):
    f0, Qc, Qd, Q = cavity_TE101(a, b, d, er=er, tand=td)
    print(f"  {label}: f0={f0/1e9:.4f} GHz, Qc={Qc:.0f}, Qd={Qd:.0f}, Q={Q:.0f}")
# numeric Qc check via stored energy/loss for a=d cube-ish
def Qc_numeric(a, b, d, sigma=5.8e7):
    f0 = c / 2 * np.sqrt((1 / a)**2 + (1 / d)**2); w = 2 * np.pi * f0; k = w / c
    Rs = np.sqrt(np.pi * f0 * mu0 / sigma)
    E0 = 1.0
    # fields: Ey = E0 sin(pi x/a) sin(pi z/d); Hx = -j E0/(Z_TE) sin(pi x/a) cos(pi z/d); Hz = j pi E0/(k eta a) cos(pi x/a) sin(pi z/d)
    beta = np.pi / d; ZTE = k * eta0 / beta
    Hx0 = E0 / ZTE; Hz0 = np.pi * E0 / (k * eta0 * a)
    We = eps0 / 4 * E0**2 * a * b * d / 4
    Wtot = 2 * We
    # losses: walls z=0,d (Hx), x=0,a (Hz), y=0,b (Hx and Hz)
    Pz = 2 * Rs / 2 * Hx0**2 * integrate.quad(lambda x: np.sin(np.pi * x / a)**2, 0, a)[0] * b
    Px = 2 * Rs / 2 * Hz0**2 * integrate.quad(lambda z: np.sin(np.pi * z / d)**2, 0, d)[0] * b
    Py = 2 * Rs / 2 * integrate.dblquad(lambda z, x: Hx0**2 * np.sin(np.pi * x / a)**2 * np.cos(np.pi * z / d)**2 +
                                        Hz0**2 * np.cos(np.pi * x / a)**2 * np.sin(np.pi * z / d)**2, 0, a, 0, d)[0]
    return w * Wtot / (Pz + Px + Py)
a, b, d = 0.0866, 0.04, 0.0866
qn = Qc_numeric(a, b, d); qa = cavity_TE101(a, b, d)[1]
print(f"  numeric Qc check: {qn:.1f} vs closed form {qa:.1f}")
assert abs(qn - qa) / qa < 1e-6

print("\n=== 7. PCB plane-pair cavity resonances (100 x 50 mm, FR-4 er 4.4) ===")
A_, B_ = 0.100, 0.050
modes = sorted([(c / (2 * np.sqrt(4.4)) * np.sqrt((m / A_)**2 + (n / B_)**2), m, n) for m in range(0, 4) for n in range(0, 3) if (m, n) != (0, 0)])[:6]
for f, m, n in modes:
    print(f"  TM{m}{n}z: {f/1e6:.0f} MHz")
# Q of a plane pair: 1/Q = tan d + delta/h (conductor); h = 0.2 mm, Cu, at 715 MHz
h = 0.2e-3; f = modes[0][0]
delta = 1 / np.sqrt(np.pi * f * mu0 * 5.8e7)
Q = 1 / (0.02 + delta / h)
print(f"  plane-pair Q (h=0.2 mm, tan d 0.02, no radiation) at {f/1e6:.0f} MHz: {Q:.1f} (Qd=50, Qc={h/delta:.0f})")

print("\n=== 8. SIW equivalent width (RO4003C, er 3.55) ===")
for (w_, d_, s_) in ((20e-3, 1.0e-3, 1.8e-3), (15e-3, 0.8e-3, 1.4e-3)):
    a_eff = w_ - d_**2 / (0.95 * s_)
    fc = c / (2 * a_eff * np.sqrt(3.55))
    print(f"  via-row spacing w={w_*1e3} mm, via d={d_*1e3} mm, pitch s={s_*1e3} mm: a_eff = {a_eff*1e3:.2f} mm; fc(TE10) = {fc/1e9:.3f} GHz;"
          f" rules: s/d = {s_/d_:.2f} (<= 2), d/lambda_c... ")
print("\nAll checks passed.")
