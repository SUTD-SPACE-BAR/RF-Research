#!/usr/bin/env python3
"""
Verification for kb/03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md

Checks:
  1. Z0 = sqrt((R+jwL)/(G+jwC)) and gamma = sqrt((R+jwL)(G+jwC)) against scikit-rf
     (skrf.media.DefinedGammaZ0 cascade vs closed-form Zin of a lossy line).
  2. Low-loss approximations alpha ~ R/(2 Z0) + G Z0 / 2, beta ~ w sqrt(LC): error vs exact.
  3. Heaviside distortionless condition R/L = G/C gives frequency-independent alpha and vp.
  4. RG-58-like coax per-unit-length parameters from geometry (skin effect) and resulting
     attenuation vs the Belden 8240 datasheet (theory should undershoot: braid + tin + dielectric).
  5. Time-domain "ohmmeter" picture: step into an open-ended line; the source sees V/Z0 current
     until the reflection returns after 2*l/vp, then the current decays to zero.
  6. Low-frequency behaviour: Z0 becomes complex and large below the R = wL corner.

Run: python3 tools/verify/tline_telegrapher.py
"""
import numpy as np
import skrf as rf

c0 = 299_792_458.0
mu0 = 4e-7 * np.pi
eps0 = 1 / (mu0 * c0**2)
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def z0_gamma(R, L, G, C, f):
    w = 2 * np.pi * f
    Z = R + 1j * w * L
    Y = G + 1j * w * C
    return np.sqrt(Z / Y), np.sqrt(Z * Y)


# ---------------------------------------------------------------- 1. vs scikit-rf
f = np.linspace(1e6, 3e9, 301)
R, L, G, C = 2.0, 250e-9, 1e-5, 100e-12          # ohm/m, H/m, S/m, F/m
Z0, gam = z0_gamma(R, L, G, C, f)
freq = rf.Frequency.from_f(f, unit="Hz")
med = rf.media.DefinedGammaZ0(frequency=freq, gamma=gam, z0=Z0, z0_port=50)
length = 0.37  # m
ZL = 20 - 35j
line = med.line(length, unit="m")
load = rf.Network(frequency=freq, s=((ZL - 50) / (ZL + 50)) * np.ones(len(f)), z0=50)
# load defined as a 1-port with 50 ohm reference; line ports are also 50 ohm (z0_port=50)
ntw = line ** load
zin_skrf = ntw.z[:, 0, 0]
t = np.tanh(gam * length)
zin_formula = Z0 * (ZL + Z0 * t) / (Z0 + ZL * t)
err = np.max(np.abs(zin_skrf - zin_formula) / np.abs(zin_formula))
check("Zin of lossy RLGC line: closed form == skrf cascade", err < 1e-9, f"(max rel err {err:.2e})")

# ---------------------------------------------------------------- 2. low-loss approximations
w = 2 * np.pi * f
Z0_ll = np.sqrt(L / C)
alpha_ll = R / (2 * Z0_ll) + G * Z0_ll / 2
beta_ll = w * np.sqrt(L * C)
hi = f > 100e6
e_a = np.max(np.abs(gam.real[hi] - alpha_ll) / gam.real[hi])
e_b = np.max(np.abs(gam.imag[hi] - beta_ll[hi]) / gam.imag[hi])
check("low-loss alpha approx within 0.1% above 100 MHz", e_a < 1e-3, f"(max {e_a:.2e})")
check("low-loss beta approx within 0.01% above 100 MHz", e_b < 1e-4, f"(max {e_b:.2e})")
# where does the low-loss approximation break? (R = wL corner)
f_corner = R / (2 * np.pi * L)
print(f"      R = wL corner for R={R} ohm/m, L={L*1e9:.0f} nH/m: {f_corner/1e6:.2f} MHz")
# realistic dielectric: G = w C tan(delta) with tan(delta) = 2e-4 (PE)
f1k = np.array([1e3])
Z0_1k, _ = z0_gamma(R, L, 2 * np.pi * f1k * C * 2e-4, C, f1k)
print(f"      Z0 at 1 kHz (G = wC tand) = {Z0_1k[0]:.1f} ohm = {abs(Z0_1k[0]):.0f} ohm at "
      f"{np.angle(Z0_1k[0], deg=True):.1f} deg  (vs sqrt(L/C) = {Z0_ll:.1f} ohm)")
check("Z0 at 1 kHz is far from 50 ohm and ~ -45 deg (RC line: sqrt(R/jwC))",
      abs(Z0_1k[0]) > 500 and -46 < np.angle(Z0_1k[0], deg=True) < -40)

# ---------------------------------------------------------------- 3. distortionless line
Gd = R * C / L
Z0d, gamd = z0_gamma(R, L, Gd, C, f)
vp_d = w / gamd.imag
check("distortionless: alpha constant vs f", np.ptp(gamd.real) / gamd.real.mean() < 1e-9,
      f"(alpha = {gamd.real[0]:.5f} Np/m = sqrt(RG))")
check("distortionless: alpha == sqrt(R G)", np.allclose(gamd.real, np.sqrt(R * Gd)))
check("distortionless: vp constant and = 1/sqrt(LC)", np.allclose(vp_d, 1 / np.sqrt(L * C)))
check("distortionless: Z0 real and = sqrt(L/C)", np.allclose(Z0d, np.sqrt(L / C)))

# ---------------------------------------------------------------- 4. RG-58 from geometry
# Belden 8240: centre 0.033 in solid Cu, PE insulation 2.95 mm, VF 0.66, nominal 52 ohm (51.5 +/- 1.5)
a = 0.033 * 25.4e-3 / 2
b = 2.95e-3 / 2
er = 1 / 0.66**2          # from datasheet velocity factor
tand = 2e-4               # solid PE typical loss tangent (assumed)
sigma = 5.8e7
Z0_geo = 60 / np.sqrt(er) * np.log(b / a)
L_geo = mu0 / (2 * np.pi) * np.log(b / a)
C_geo = 2 * np.pi * eps0 * er / np.log(b / a)
print(f"      RG-58 geometry: Z0 = {Z0_geo:.1f} ohm, L = {L_geo*1e9:.0f} nH/m, "
      f"C = {C_geo*1e12:.1f} pF/m (Belden: 93.5 pF/m), vp = {1/np.sqrt(L_geo*C_geo)/c0:.3f} c")
# Datasheet self-consistency: Z0 = 1/(vp C) from Belden's own C and VF
Z0_from_ds = 1 / (0.66 * c0 * 93.5e-12)
print(f"      Belden's own numbers: 1/(vp*C) = {Z0_from_ds:.1f} ohm vs stated 52 (51.5 +/- 1.5) ohm;"
      f" geometry+VF gives {Z0_geo:.1f} ohm -> datasheet nominals agree only to ~5-8%")
check("RG-58 capacitance from geometry within 10% of Belden 93.5 pF/m (braid radius > insulation OD)",
      abs(C_geo * 1e12 - 93.5) / 93.5 < 0.10)
fb = np.array([1, 10, 50, 100, 200, 400, 700, 900, 1000]) * 1e6
belden_db100ft = np.array([0.3, 1.1, 2.5, 3.8, 5.6, 8.4, 11.7, 13.7, 14.5])
Rs = np.sqrt(np.pi * fb * mu0 / sigma)
Rpul = Rs / (2 * np.pi) * (1 / a + 1 / b)
Gpul = 2 * np.pi * fb * C_geo * tand
Z0b, gb = z0_gamma(Rpul, L_geo, Gpul, C_geo, fb)
theory_db100ft = gb.real * 8.686 * 30.48
print("      f(MHz)  theory(solid Cu, dB/100ft)  Belden 8240   ratio")
for fi, th, be in zip(fb / 1e6, theory_db100ft, belden_db100ft):
    print(f"      {fi:6.0f}  {th:10.2f}               {be:6.1f}      {be/th:5.2f}")
ratio = belden_db100ft[3:] / theory_db100ft[3:]
check("real RG-58 loss exceeds ideal smooth-solid-copper theory by 1.0-1.6x (100-1000 MHz)",
      np.all((ratio > 1.0) & (ratio < 1.6)), f"(ratios {np.round(ratio,2)})")

# ---------------------------------------------------------------- 5. ohmmeter / step response
# Lossless open-ended line of length l driven by a step through a source resistance Rs.
# Simulate with lattice (bounce) method: the source initially sees Z0.
Z0s, Rsrc, V = 50.0, 1e3, 1.0   # a multimeter-like high source resistance
vp = 0.66 * c0
l = 10.0
tau = l / vp
Gs = (Rsrc - Z0s) / (Rsrc + Z0s)
GL = 1.0   # open
# Current at source end as sum of bounces: i(t) steps each round trip 2*tau
n_trips = 400
i_src = []
v_inc = V * Z0s / (Z0s + Rsrc)
i_now = v_inc / Z0s
i_src.append(i_now)
wave = v_inc
for k in range(1, n_trips):
    # wave returns reflected by load then source
    back = wave * GL
    new_fwd = back * Gs
    # source current changes by (-back + new_fwd)/Z0
    i_now = i_now + (-back + new_fwd) / Z0s
    i_src.append(i_now)
    wave = new_fwd
i_src = np.array(i_src)
check("step into open line: initial current = V/(Rs+Z0)", abs(i_src[0] - V / (Rsrc + Z0s)) < 1e-12,
      f"({i_src[0]*1e3:.4f} mA, i.e. the line looks like {Z0s} ohm for 2l/vp = {2*tau*1e9:.0f} ns)")
check("step into open line: current decays to ~0 (ohmmeter reads open)", abs(i_src[-1]) < 1e-6 * i_src[0] + 1e-9,
      f"(after {n_trips} round trips: {i_src[-1]:.2e} A)")
# total charge delivered = C_total * V (line charges up like a capacitor)
q = np.sum(i_src) * 2 * tau
C_line = l / (Z0s * vp)
check("charge delivered equals C_line * V (line = capacitor at DC)", abs(q - C_line * V) / (C_line * V) < 1e-3,
      f"(q = {q*1e12:.1f} pC, C_line*V = {C_line*1e12:.1f} pC)")

# ---------------------------------------------------------------- 6. velocity factor examples
for name, erv in [("PE (solid)", 2.25), ("PTFE", 2.05), ("foam PE (LMR-400, VF 0.85)", 1 / 0.85**2)]:
    print(f"      {name:28s} er = {erv:.3f} -> VF = {1/np.sqrt(erv):.3f}, "
          f"lambda at 433 MHz = {c0/np.sqrt(erv)/433e6*100:.1f} cm")

# ---------------------------------------------------------------- 7. symbolic checks (sympy)
import sympy as sp
z, Rs_, Ls_, Gs_, Cs_, w_, Vp = sp.symbols("z R L G C omega V_p", positive=True)
Zs = Rs_ + sp.I * w_ * Ls_
Ys = Gs_ + sp.I * w_ * Cs_
g = sp.sqrt(Zs * Ys)
Zc = sp.sqrt(Zs / Ys)
V = Vp * sp.exp(-g * z)
I = Vp / Zc * sp.exp(-g * z)
# telegrapher: dV/dz = -Z I ; dI/dz = -Y V
r1 = sp.diff(V, z) + Zs * I
r2 = sp.diff(I, z) + Ys * V
vals = {Rs_: 2.0, Ls_: 250e-9, Gs_: 1e-5, Cs_: 100e-12, w_: 2 * np.pi * 1e8, Vp: 1.0, z: 0.3}
res = max(abs(complex(r1.subs(vals).evalf())), abs(complex(r2.subs(vals).evalf())))
# also the wave equation d2V/dz2 = gamma^2 V symbolically
r3 = sp.simplify(sp.diff(V, z, 2) - Zs * Ys * V)
check("sympy: V+ e^{-gz}, I = V/Z0 satisfies both telegrapher eqs and d2V/dz2 = ZY V",
      res < 1e-9 and r3 == 0, f"(numeric residual {res:.1e})")
# second-order low-loss beta: beta ~ w sqrt(LC) [1 + (R/wL - G/wC)^2 / 8]
fh = np.array([2e6, 5e6, 20e6])
wh = 2 * np.pi * fh
Gx = 2e-6
_, gx = z0_gamma(R, L, Gx, C, fh)
b2 = wh * np.sqrt(L * C) * (1 + (R / (wh * L) - Gx / (wh * C))**2 / 8)
b1 = wh * np.sqrt(L * C)
e1 = np.abs(gx.imag - b1) / gx.imag
e2 = np.abs(gx.imag - b2) / gx.imag
print(f"      beta error first-order {np.round(e1*100,3)} %, second-order {np.round(e2*100,4)} % at f = {fh/1e6} MHz")
check("second-order beta correction reduces error by >=8x at and above 1.5x the R = wL corner", np.all(e2 < e1 / 8))

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
