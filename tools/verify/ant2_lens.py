#!/usr/bin/env python3
"""ant2_lens.py -- checks for kb/08-antennas/lens-and-reflectarray-antennas.md (W5-E2).

Pre-registered expectations (written before the first run):
 1. Hyperbolic plano-convex lens r(th) = (n-1)F/(n cos th - 1): every ray from the focus has the same
    electrical path to the flat exit plane (to < 1e-9 lambda).
 2. Luneburg lens n = sqrt(2 - (r/R)^2): numerically traced rays from a point on the surface leave parallel
    to the axis (angle error < 0.1 deg), entry heights spanning the aperture.
 3. Lens gain e_ap (pi D/lambda)^2 with e_ap ~ 0.5-0.6: 50 mm lens at 77 GHz ~ 29-30 dBi; 100 mm PLA lens at
    24 GHz ~ 24-25 dBi minus ~1 dB dielectric loss for tan d = 0.01-0.02.
 4. Phase quantisation of reflectarray/transmitarray elements: 1/2/3-bit loss = -3.9/-0.9/-0.2 dB.
 5. Reflectarray spatial-phase-delay bandwidth: D = 30 cm, F/D = 0.8 at 10 GHz loses < 1 dB over +-5 %
    (element response ignored).
Run: python3 tools/verify/ant2_lens.py     (~10 s)
"""
import numpy as np
from scipy.integrate import solve_ivp

C0 = 299792458.0
ok = True


def check(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(f"[{'PASS' if cond else 'MISS'}] {name} {detail}")


print("=== 1. Hyperbolic lens: equal path from the focus to the exit plane ===")
n, F = np.sqrt(2.6), 100.0          # PLA-like n, focal length (mm)
th_max = np.arccos(1 / n) * 0.75    # stay inside the hyperbola's asymptote
th = np.linspace(0, th_max, 200)
r = (n - 1) * F / (n * np.cos(th) - 1)
z = r * np.cos(th)                  # surface point (axial coordinate from the focus)
rho = r * np.sin(th)
z_exit = z.max() + 5.0              # flat back face beyond the thickest point
path = r + n * (z_exit - z)         # air path to the surface + glass path to the exit plane (axial ray inside)
print(f"  n = {n:.3f}, F = {F} mm: aperture radius at th_max = {rho.max():.1f} mm, vertex at z = {z[0]:.1f} mm")
print(f"  path spread over the aperture = {np.ptp(path):.2e} mm")
check("equal electrical path (hyperbola)", np.ptp(path) < 1e-9)


def lens_dims(D, F, n):
    """centre thickness of a plano-convex hyperbolic lens of diameter D, focal length F (vertex distance)."""
    a = D / 2
    # solve rho(th) = a
    from scipy.optimize import brentq
    f = lambda t: (n - 1) * F / (n * np.cos(t) - 1) * np.sin(t) - a
    t = brentq(f, 1e-6, np.arccos(1 / n) - 1e-6)
    r_e = (n - 1) * F / (n * np.cos(t) - 1)
    z_edge = r_e * np.cos(t)
    return z_edge - F, np.degrees(t)          # thickness at the centre above the edge (convex height)


print("\n=== 3. Lens gain and dielectric loss ===")
for (name, f, D, Fd, er, tand, rho_m) in (("77 GHz, PTFE", 77e9, 50.0, 1.0, 2.1, 3e-4, 2.2),
                                    ("77 GHz, printed PLA", 77e9, 50.0, 1.0, 2.6, 0.015, 1.24),
                                    ("24 GHz, printed PLA", 24e9, 100.0, 1.0, 2.6, 0.015, 1.24),
                                    ("24 GHz, printed ABS", 24e9, 100.0, 1.0, 2.57, 0.0047, 1.05),
                                    ("10 GHz, PTFE", 10e9, 200.0, 1.0, 2.1, 3e-4, 2.2),
                                    ("433 MHz, PTFE (why not)", 433e6, 5 * 692.0, 1.0, 2.1, 3e-4, 2.2)):
    lam = C0 / f * 1e3
    n_ = np.sqrt(er)
    t, half_angle = lens_dims(D, Fd * D, n_)
    loss_db = 8.686 * np.pi * n_ * tand * t / lam * 0.5     # average thickness ~ t/2 over the aperture
    refl_db = -10 * np.log10(1 - ((n_ - 1) / (n_ + 1)) ** 2) * 2
    G = 0.55 * (np.pi * D / lam) ** 2
    vol = np.pi * (D / 2) ** 2 * t / 2 * 1e-9                 # paraboloid-cap volume ~ half the cylinder (m^3)
    print(f"  {name:22s}: D = {D:6.0f} mm = {D/lam:5.1f} lambda, F/D {Fd}: convex height {t:6.1f} mm "
          f"(edge ray {half_angle:.0f} deg), G(e_ap 0.55) = {10*np.log10(G):5.1f} dBi, HPBW ~ {70*lam/D:4.1f} deg, "
          f"dielectric loss ~ {loss_db:.2f} dB, 2-face reflection loss ~ {refl_db:.2f} dB, "
          f"convex-cap volume ~ {vol*1e6:.0f} cm^3 -> {vol*1e3*rho_m:.2f} kg (density {rho_m} g/cm^3, excl. base)")
# zoning depth
for er in (2.1, 2.6):
    print(f"  zone step lambda/(n-1) for er {er}: {1/(np.sqrt(er)-1):.2f} lambda (24 GHz: {12.49/(np.sqrt(er)-1):.1f} mm)")

print("\n=== 2. Luneburg lens ray trace (R = 1, source on the surface at z = -1) ===")


def rhs(s, y):
    # ray equation d/ds (n dr/ds) = grad n, written with p = n dr/ds; n^2 = 2 - r^2 -> grad(n^2)/2 = -r
    x, z_, px, pz = y
    nn = np.sqrt(max(2 - (x * x + z_ * z_), 1e-12))
    return [px / nn, pz / nn, -x / nn, -z_ / nn]


def hit_surface(s, y):
    return y[0] ** 2 + y[1] ** 2 - 1.0 - 1e-9
hit_surface.terminal = True
hit_surface.direction = 1

errs = []
for a0 in np.radians(np.arange(5, 86, 10)):
    # start at (0, -1) on the surface where n = 1, direction a0 from the axis
    y0 = [0.0 + 1e-9 * np.sin(a0), -1.0 + 1e-9 * np.cos(a0), np.sin(a0), np.cos(a0)]
    sol = solve_ivp(rhs, [0, 10], y0, events=hit_surface, rtol=1e-10, atol=1e-12, max_step=0.01)
    x, z_, px, pz = sol.y[:, -1]
    ang = np.degrees(np.arctan2(px, pz))
    errs.append(abs(ang))
    print(f"  launch {np.degrees(a0):4.0f} deg: exits at x = {x:+.4f}, z = {z_:+.4f}, direction {ang:+.4f} deg from axis")
check("Luneburg: all exit rays parallel to the axis (< 0.1 deg)", max(errs) < 0.1, f"(max {max(errs):.2e} deg)")

print("\n=== 4. Phase quantisation loss (uniform aperture, random phases) ===")
rng = np.random.default_rng(1)
phi = rng.uniform(0, 2 * np.pi, 200000)
for b in (1, 2, 3, 4):
    step = 2 * np.pi / 2 ** b
    q = np.round(phi / step) * step
    gain = abs(np.mean(np.exp(1j * (q - phi)))) ** 2
    theory = np.sinc(1 / 2 ** b) ** 2
    print(f"  {b}-bit: simulated {10*np.log10(gain):6.2f} dB, theory sinc^2(1/2^b) = {10*np.log10(theory):6.2f} dB")
    if b == 1:
        q1 = 10 * np.log10(theory)
check("1-bit loss = -3.92 dB", abs(q1 + 3.92) < 0.01)

print("\n=== 5. Reflectarray bandwidth from the spatial phase delay (centre-fed, element response ignored) ===")
f0 = 10e9
lam0 = C0 / f0
for D in (0.30, 1.0, 3.0):
  FD = 0.8
  Fl = FD * D
  N = 61 if D < 0.5 else 241
  xs = np.linspace(-D / 2, D / 2, N)
  X, Y = np.meshgrid(xs, xs)
  mask = X ** 2 + Y ** 2 <= (D / 2) ** 2
  R = np.sqrt(Fl ** 2 + X ** 2 + Y ** 2)
  taper = (Fl / R) ** 3                          # cos^q feed (q ~ 2) x 1/R spreading, rough
  phi_el = np.mod(2 * np.pi / lam0 * R, 2 * np.pi)   # element phase set at f0 (wrapped, frequency independent)
  G0 = None
  print(f"  D = {D*100:.0f} cm ({D/lam0:.0f} lambda), F/D = {FD}; edge-centre path difference = "
        f"{(np.sqrt(Fl**2+(D/2)**2)-Fl)/lam0:.2f} lambda")
  for df in (-0.10, -0.05, 0.0, 0.05, 0.10):
      f = f0 * (1 + df)
      k = 2 * np.pi * f / C0
      field = np.sum((taper * np.exp(-1j * k * R) * np.exp(1j * phi_el))[mask])
      ideal = np.sum(taper[mask])
      g = abs(field / ideal) ** 2
      print(f"   f = {f/1e9:5.2f} GHz ({100*df:+.0f} %): boresight gain change from spatial phase delay = {10*np.log10(g):6.2f} dB")
      if abs(df - 0.05) < 1e-9:
          g5 = 10 * np.log10(g)
  if abs(D - 0.30) < 1e-9:
    g5_30 = g5
check("reflectarray (30 cm) loses < 1 dB at +5 % (spatial delay only)", g5_30 > -1.0, f"({g5_30:.2f} dB)")
# compare with a 'true time delay' (unwrapped) design: no loss by construction
print("  (a real reflectarray's bandwidth is usually limited first by the element phase-vs-frequency slope)")

print("\nALL PASS" if ok else "\nSOME MISSES (see above)")
