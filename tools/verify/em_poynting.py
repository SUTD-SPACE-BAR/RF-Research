#!/usr/bin/env python3
"""
em_poynting.py — checks for kb/02-electromagnetics/poynting-vector-power-flow.md

1. Coax (TEM): integrate the time-average Poynting vector over the annulus and compare with V I / 2.
   Fraction of power flowing within radius r (it is concentrated near the inner conductor).
2. Resistive DC wire: Poynting vector at the wire surface points radially inward;
   flux into a length L equals I^2 R.
3. Two-wire DC line (Boulé 2024 geometry): fraction of transported power that flows inside a
   circle of radius R around the pair -> shows energy flows in the space around/between wires.
4. Complex Poynting theorem for a series RLC: P + 2j w (Wm - We) = (1/2) Z |I|^2.
5. RF-exposure style numbers: S at 20 cm from a 2 W transmitter with 2.15 dBi antenna (far-field
   formula, flagged as invalid in the reactive near field) vs ICNIRP 2020 general-public reference level.
"""
import numpy as np
from scipy import integrate

c = 299_792_458.0
mu0 = 1.25663706127e-6
eps0 = 1 / (mu0 * c**2)
eta0 = mu0 * c

# ---------- 1. coax ----------
a, b, er = 0.45e-3, 1.47e-3, 2.25       # RG-58-like (solid PE), inner radius, outer radius
Z0 = eta0 / (2 * np.pi * np.sqrt(er)) * np.log(b / a)
P = 1.0                                  # W average
V = np.sqrt(2 * P * Z0)                  # peak phasor voltage
I = V / Z0
E = lambda r: V / (r * np.log(b / a))    # radial E (peak)
H = lambda r: I / (2 * np.pi * r)        # azimuthal H (peak)
Pint, _ = integrate.quad(lambda r: 0.5 * E(r) * H(r) * 2 * np.pi * r, a, b)
print(f"1. coax a={a*1e3} mm b={b*1e3} mm er={er}: Z0={Z0:.2f} ohm; V_pk={V:.3f} V; "
      f"integral of S over annulus = {Pint:.6f} W (expect {P})")
assert abs(Pint - P) < 1e-9
for rr in (1.2 * a, 2 * a, (a + b) / 2):
    frac, _ = integrate.quad(lambda r: 0.5 * E(r) * H(r) * 2 * np.pi * r, a, rr)
    print(f"   fraction of power within r = {rr*1e3:.3f} mm: {frac:.3f}")
print(f"   peak E at inner conductor for 1 W: {E(a)/1e3:.2f} kV/m; for 100 W: {E(a)*10/1e3:.1f} kV/m")

# ---------- 2. resistive wire ----------
sigma = 5.8e7; rw = 0.5e-3; L = 1.0; Idc = 10.0
R = L / (sigma * np.pi * rw**2)
Ez = Idc / (sigma * np.pi * rw**2)       # E inside and (tangentially) at the surface
Hphi = Idc / (2 * np.pi * rw)
S_in = Ez * Hphi                           # |E x H| radial, pointing inward
Pin = S_in * 2 * np.pi * rw * L
print(f"\n2. DC wire r={rw*1e3} mm, 1 m, 10 A: R={R*1e3:.3f} mOhm, I^2R={Idc**2*R:.4f} W; "
      f"surface Poynting flux in = {Pin:.4f} W; S = {S_in:.3f} W/m^2 inward")
assert abs(Pin - Idc**2 * R) < 1e-9

# ---------- 3. two-wire DC line power distribution ----------
# Thin-wire idealisation: wires at x = +-d/2 carry +-I, potentials +-V/2 (line charge +-q).
# Power density S_z = Ex*Hy - Ey*Hx. Integrate over disc radius Rc; compare with V*I.
d = 0.02; rwire = 0.5e-3; Vdc, Idc2 = 10.0, 1.0
q = np.pi * eps0 * Vdc / np.arccosh(d / (2 * rwire))   # line charge for voltage V between wires
def fields(x, y):
    Ex = Ey = Hx = Hy = 0.0
    for sgn, x0 in ((+1, d / 2), (-1, -d / 2)):
        dx, dy = x - x0, y
        r2 = dx * dx + dy * dy
        Ex += sgn * q / (2 * np.pi * eps0) * dx / r2
        Ey += sgn * q / (2 * np.pi * eps0) * dy / r2
        # current +z in +wire: H = I/(2 pi r) phi_hat, phi_hat = (-dy, dx)/r
        Hx += sgn * Idc2 / (2 * np.pi) * (-dy) / r2
        Hy += sgn * Idc2 / (2 * np.pi) * dx / r2
    return Ex * Hy - Ey * Hx
def power_within(Rc, n=1500):
    xs = np.linspace(-Rc, Rc, n); ys = np.linspace(-Rc, Rc, n)
    X, Y = np.meshgrid(xs, ys)
    Sz = fields(X, Y)
    inside = (X**2 + Y**2 <= Rc**2)
    for x0 in (d / 2, -d / 2):
        inside &= ((X - x0)**2 + Y**2 > rwire**2)
    dA = (xs[1] - xs[0]) * (ys[1] - ys[0])
    return np.sum(Sz[inside]) * dA
print(f"\n3. two-wire DC line, spacing {d*100:.0f} cm, V={Vdc} V, I={Idc2} A (VI = {Vdc*Idc2} W):")
for Rc in (0.6 * d, d, 2 * d, 5 * d):
    print(f"   power flowing within radius {Rc*100:5.1f} cm of the line centre: {power_within(Rc):.2f} W")

# ---------- 4. complex Poynting theorem for series RLC ----------
Rr, Ll, Cc, w, Ipk = 10.0, 100e-9, 10e-12, 2 * np.pi * 150e6, 0.1
Z = Rr + 1j * w * Ll + 1 / (1j * w * Cc)
Wm = 0.25 * Ll * Ipk**2
Vc = Ipk / (w * Cc)
We = 0.25 * Cc * Vc**2
lhs = 0.5 * Rr * Ipk**2 + 2j * w * (Wm - We)
rhs = 0.5 * Z * Ipk**2
print(f"\n4. complex Poynting (series RLC @150 MHz): P+2jw(Wm-We) = {lhs:.5f}; Z|I|^2/2 = {rhs:.5f}")
assert abs(lhs - rhs) < 1e-12

# ---------- 5. exposure-style numbers ----------
Pt, G = 2.0, 10 ** (2.15 / 10)
for r in (0.2, 0.5, 1.0, 2.0):
    S = Pt * G / (4 * np.pi * r**2)
    print(f"5. 2 W, 2.15 dBi at {r} m: far-field-formula S = {S:.3f} W/m^2 = {S/10:.4f} mW/cm^2; "
          f"E = {np.sqrt(eta0*S):.2f} V/m; r/(lambda/2pi) at 433 MHz = {r/(c/433e6/(2*np.pi)):.2f}")
print(f"   ICNIRP 2020 general-public whole-body reference level 400-2000 MHz: f/200 W/m^2 -> 433 MHz: {433/200:.2f} W/m^2; 915 MHz: {915/200:.2f} W/m^2")
print("\nAll checks passed.")
