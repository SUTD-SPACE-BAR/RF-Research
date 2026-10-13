#!/usr/bin/env python3
"""
em_maxwell.py — checks used by kb/02-electromagnetics/maxwells-equations.md

1. Symbolic: div(curl H) = 0  =>  Ampere-Maxwell + Gauss imply the continuity equation.
2. Symbolic: a uniform plane wave E = x E0 cos(wt - kz), H = y (E0/eta) cos(wt - kz) satisfies
   all four source-free Maxwell equations iff k = w sqrt(mu eps) and eta = sqrt(mu/eps).
3. Numeric: conduction/displacement current ratio sigma/(w eps) and charge-relaxation time eps/sigma
   for copper, sea water, fresh water, wet ground, FR-4 at 433 MHz / 915 MHz / 2.45 GHz.
4. Numeric: displacement current through a 10 pF capacitor at 433 MHz, 1 V rms.
5. Numeric: Faraday EMF in a small loop next to a wire (KVL "violation" example).
"""
import math
import sympy as sp

# ---------- 1. continuity from Maxwell ----------
x, y, z, t = sp.symbols('x y z t', real=True)
Hx, Hy, Hz = [sp.Function(n)(x, y, z, t) for n in ('Hx', 'Hy', 'Hz')]
curlH = sp.Matrix([sp.diff(Hz, y) - sp.diff(Hy, z),
                   sp.diff(Hx, z) - sp.diff(Hz, x),
                   sp.diff(Hy, x) - sp.diff(Hx, y)])
div_curlH = sp.simplify(sp.diff(curlH[0], x) + sp.diff(curlH[1], y) + sp.diff(curlH[2], z))
assert div_curlH == 0
print("1. div(curl H) = 0 symbolically -> div J + d(rho)/dt = 0 follows from Ampere-Maxwell + Gauss. OK")

# ---------- 2. plane wave satisfies Maxwell ----------
E0, w, k, mu, eps, eta = sp.symbols('E0 omega k mu epsilon eta', positive=True)
phase = w * t - k * z
E = sp.Matrix([E0 * sp.cos(phase), 0, 0])
H = sp.Matrix([0, E0 / eta * sp.cos(phase), 0])
def curl(F):
    return sp.Matrix([sp.diff(F[2], y) - sp.diff(F[1], z),
                      sp.diff(F[0], z) - sp.diff(F[2], x),
                      sp.diff(F[1], x) - sp.diff(F[0], y)])
faraday = sp.simplify(curl(E) + mu * sp.diff(H, t))          # should vanish
ampere = sp.simplify(curl(H) - eps * sp.diff(E, t))          # should vanish
sol = sp.solve([faraday[1], ampere[0]], [k, eta], dict=True)
print("2. plane-wave conditions from Faraday & Ampere:", sol)
assert any(sp.simplify(s[k] - w * sp.sqrt(mu * eps)) == 0 and sp.simplify(s[eta] - sp.sqrt(mu / eps)) == 0 for s in sol)
print("   k = w sqrt(mu eps), eta = sqrt(mu/eps). OK")

# ---------- 3. conduction vs displacement ----------
eps0 = 8.8541878188e-12
materials = {
    # name: (eps_r, sigma S/m)  -- sources in maxwells-equations.md
    "copper (annealed)": (1.0, 5.80e7),
    "sea water (ITU-R P.368: 70, 5 S/m)": (70.0, 5.0),
    "wet ground (30, 0.01 S/m, ITU-R P.527-3 typ.)": (30.0, 0.01),
    "medium dry ground (15, 0.001 S/m)": (15.0, 1e-3),
    "fresh water (80, ~0.01 S/m)": (80.0, 0.01),
    "FR-4 (4.4, tan d 0.02 -> equiv sigma @1GHz)": (4.4, 2 * math.pi * 1e9 * 4.4 * eps0 * 0.02),
}
print("\n3. sigma/(omega eps) and relaxation time tau = eps/sigma")
for name, (er, sig) in materials.items():
    tau = er * eps0 / sig
    ratios = [sig / (2 * math.pi * f * er * eps0) for f in (433e6, 915e6, 2.45e9)]
    ftrans = sig / (2 * math.pi * er * eps0)
    print(f"   {name:48s} tau = {tau:9.3e} s, f(sigma=w eps) = {ftrans:9.3e} Hz, "
          f"ratio @433M/915M/2.45G = {ratios[0]:.3g} / {ratios[1]:.3g} / {ratios[2]:.3g}")

# ---------- 4. displacement current in a capacitor ----------
C, V, f = 10e-12, 1.0, 433e6
I = 2 * math.pi * f * C * V
print(f"\n4. 10 pF, 1 V rms, 433 MHz: I_displacement = {I*1e3:.2f} mA rms (Xc = {1/(2*math.pi*f*C):.2f} ohm)")

# ---------- 5. Faraday EMF in a loop near a wire ----------
mu0 = 1.25663706127e-6
I_w, f_w = 0.1, 100e6            # 100 mA rms at 100 MHz in a long straight wire
d1, d2, L = 2e-3, 12e-3, 20e-3    # rectangular loop from 2 mm to 12 mm away, 20 mm long
flux_per_A = mu0 * L / (2 * math.pi) * math.log(d2 / d1)   # mutual inductance M
emf = 2 * math.pi * f_w * flux_per_A * I_w
print(f"5. M = {flux_per_A*1e9:.3f} nH; EMF = {emf*1e3:.1f} mV rms around the loop (so KVL 'fails' by this much)")
print("\nAll checks passed.")
