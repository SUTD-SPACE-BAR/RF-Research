#!/usr/bin/env python3
"""
prop_knife_edge.py — verification for kb/09-propagation-link-budget/diffraction-knife-edge.md

1. Fresnel–Kirchhoff knife-edge loss J(v) exact (Fresnel integrals, ITU-R P.526 eq. 30) vs the
   P.526 approximation J(v) = 6.9 + 20 log10( sqrt((v-0.1)^2 + 1) + v - 0.1 ) for v > -0.78,
   and the large-v asymptote J ~ 13 + 20 log10(v)  (from |F| -> 1/(pi v sqrt 2)).
2. v from geometry: v = h sqrt(2 (d1+d2)/(lambda d1 d2)) and the equivalent forms (Fresnel-zone ratio
   v = sqrt(2) h/R1).
3. Two-edge methods: Deygout (main edge + secondary), Epstein–Peterson, and Bullington (single
   equivalent edge) on the same profile — they disagree; that is the point.
4. Worked example: a landed rocket 6 km from the GS, a 25 m-high ridge (relative to the LOS line)
   1.5 km in front of the rocket, 433 MHz and 915 MHz.
"""
import numpy as np
from scipy.special import fresnel
c = 299792458.0

def J_exact(v):
    S, C = fresnel(v)   # scipy returns (S, C) with integrals of sin/cos(pi t^2/2)
    return -20*np.log10(np.sqrt((1 - C - S)**2 + (C - S)**2)/2)

def J_itu(v):
    v = np.asarray(v, float)
    out = 6.9 + 20*np.log10(np.sqrt((v - 0.1)**2 + 1) + v - 0.1)
    return np.where(v > -0.78, out, 0.0)

def v_param(h, d1, d2, lam):
    return h*np.sqrt(2*(d1 + d2)/(lam*d1*d2))

print("=== 1. J(v) exact vs ITU approximation ===")
for v in (-2.0, -1.0, -0.78, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.4, 3.0, 5.0, 10.0):
    print(f"  v={v:6.2f}: exact {J_exact(v):7.3f} dB, ITU approx {float(J_itu(v)):7.3f} dB, "
          f"asymptote 13+20log v = {13+20*np.log10(v) if v > 0 else float('nan'):7.3f}")
vv = np.linspace(-0.7, 10, 2000)
err = J_itu(vv) - J_exact(vv)
print(f"  max |approx - exact| on -0.7 <= v <= 10: {np.max(np.abs(err)):.3f} dB (at v = {vv[np.argmax(np.abs(err))]:.2f})")
vv = np.linspace(-3, -0.8, 500)
print(f"  for v < -0.78 exact J ranges {J_exact(vv).min():+.2f} .. {J_exact(vv).max():+.2f} dB (ripple around 0; approx returns 0)")
print(f"  grazing (v=0): exact {J_exact(0.0):.3f} dB (= 20 log10 2 = 6.02 dB)")

print("\n=== 2. v from geometry ===")
lam = c/433.125e6
d1, d2, h = 4.5e3, 1.5e3, 25.0
v = v_param(h, d1, d2, lam)
R1 = np.sqrt(lam*d1*d2/(d1 + d2))
print(f"  433 MHz, d1={d1/1e3} km, d2={d2/1e3} km, h={h} m: v = {v:.3f}; R1 = {R1:.2f} m; sqrt(2) h/R1 = {np.sqrt(2)*h/R1:.3f}")
print(f"  P.526 practical form v = 0.0316 h sqrt(2(d1+d2)/(lambda d1 d2)) with d in km: "
      f"{0.0316*h*np.sqrt(2*(d1+d2)/1e3/(lam*d1/1e3*d2/1e3)):.3f}")

print("\n=== 3/4. Multiple edges and the landed-rocket example ===")
# Profile: GS at x=0 (h_gs), rocket at x=D (h_r). Obstacles (x, height above a flat datum).
def edge_h(xe, he, xa, ha, xb, hb):
    """height of an edge above the straight line between a and b"""
    return he - (ha + (hb - ha)*(xe - xa)/(xb - xa))

def single(xe, he, xa, ha, xb, hb, lam):
    h = edge_h(xe, he, xa, ha, xb, hb)
    return v_param(h, xe - xa, xb - xe, lam)

def deygout(edges, xa, ha, xb, hb, lam):
    vs = [single(x, hh, xa, ha, xb, hb, lam) for x, hh in edges]
    i = int(np.argmax(vs)); L = float(J_itu(vs[i]))
    xm, hm = edges[i]
    left = [e for e in edges if e[0] < xm]; right = [e for e in edges if e[0] > xm]
    if left:
        L += deygout(left, xa, ha, xm, hm, lam)
    if right:
        L += deygout(right, xm, hm, xb, hb, lam)
    return L

def epstein_peterson(edges, xa, ha, xb, hb, lam):
    pts = [(xa, ha)] + sorted(edges) + [(xb, hb)]
    L = 0.0
    for k in range(1, len(pts) - 1):
        (x0, h0), (x1, h1), (x2, h2) = pts[k-1], pts[k], pts[k+1]
        L += float(J_itu(single(x1, h1, x0, h0, x2, h2, lam)))
    return L

def bullington(edges, xa, ha, xb, hb, lam):
    # steepest slopes from each terminal -> intersection = equivalent edge
    sa = max((h - ha)/(x - xa) for x, h in edges)
    sb = max((h - hb)/(xb - x) for x, h in edges)
    xe = (hb - ha + sb*xb)/(sa + sb) if (sa + sb) != 0 else 0.5*(xa + xb)
    xe = (ha - hb + sb*xb - sa*xa)/(sa + sb) if False else xe
    # solve ha + sa (x - xa) = hb + sb (xb - x)
    xe = (hb - ha + sa*xa + sb*xb)/(sa + sb)
    he = ha + sa*(xe - xa)
    return float(J_itu(single(xe, he, xa, ha, xb, hb, lam))), xe, he

D = 6e3; h_gs = 5.0; h_r = 0.3
for f in (433.125e6, 915e6):
    lam = c/f
    one = [(4.5e3, 25.0)]
    two = [(2.0e3, 18.0), (4.5e3, 25.0)]
    print(f"  f = {f/1e6:.1f} MHz, GS h={h_gs} m, rocket h={h_r} m, D={D/1e3} km")
    v1 = single(*one[0], 0, h_gs, D, h_r, lam)
    print(f"    single ridge (25 m at 4.5 km): v={v1:.2f}, J={float(J_itu(v1)):.1f} dB (exact {J_exact(v1):.1f})")
    print(f"    two edges: Deygout {deygout(two, 0, h_gs, D, h_r, lam):.1f} dB, "
          f"Epstein-Peterson {epstein_peterson(two, 0, h_gs, D, h_r, lam):.1f} dB, "
          f"Bullington {bullington(two, 0, h_gs, D, h_r, lam)[0]:.1f} dB")
    fs = 20*np.log10(4*np.pi*D/lam)
    print(f"    FSPL {fs:.1f} dB -> total (single ridge) ~ {fs + float(J_itu(v1)):.1f} dB "
          "(ground reflection on each sub-path ignored; see page)")
