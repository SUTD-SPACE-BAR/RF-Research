#!/usr/bin/env python3
"""
prop_polarization.py — verification for kb/09-propagation-link-budget/polarization-mismatch-loss.md

1. PLF from Jones vectors vs the closed-form axial-ratio mismatch formula
       PLF = 1/2 + [ s*4 AR_w AR_a + (AR_w^2 - 1)(AR_a^2 - 1) cos(2 dtau) ] / [ 2 (AR_w^2 + 1)(AR_a^2 + 1) ]
   (AR >= 1 as voltage ratio, s = +1 same hand, -1 opposite hand; linear: AR -> inf).
   Random-tilt Monte Carlo confirms it, and min/max PLF for a CP antenna with finite axial ratio.
2. Special cases: linear-linear cos^2, linear-circular 1/2 (3.01 dB), co-/cross-circular.
3. Rocket attitude geometry: a dipole along the rocket axis, ground station at the origin.
   Gain toward the GS ~ sin^2(psi) (psi = angle between axis and line of sight) and the polarisation
   delivered to a vertical-linear vs a circular ground antenna, for a few flight geometries.
"""
import numpy as np
rng = np.random.default_rng(5)

def jones(AR_db, tau_deg, hand=+1):
    """Unit Jones vector (x,y) of an elliptical polarisation: AR in dB (>=0; inf = linear), tilt tau,
    hand +1/-1. Both wave and antenna are described as the wave polarisation they radiate/accept,
    in one common frame looking along the propagation direction."""
    if np.isinf(AR_db):
        eps = 0.0
    else:
        AR = 10**(AR_db/20)
        eps = hand*np.arctan(1/AR)
    t = np.radians(tau_deg)
    v = np.array([np.cos(eps), 1j*np.sin(eps)])
    R = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    return R @ v

def plf_jones(w, a):
    return np.abs(np.vdot(a, w))**2/(np.vdot(w, w).real*np.vdot(a, a).real)

def plf_formula(ARw_db, ARa_db, dtau_deg, same_hand=True):
    s = 1 if same_hand else -1
    def prod_terms(ARdb):
        if np.isinf(ARdb):
            return None
        return 10**(ARdb/20)
    Aw, Aa = prod_terms(ARw_db), prod_terms(ARa_db)
    c2 = np.cos(2*np.radians(dtau_deg))
    if Aw is None and Aa is None:
        return 0.5 + 0.5*c2
    if Aw is None:
        return 0.5 + (Aa**2 - 1)*c2/(2*(Aa**2 + 1))
    if Aa is None:
        return 0.5 + (Aw**2 - 1)*c2/(2*(Aw**2 + 1))
    return 0.5 + (s*4*Aw*Aa + (Aw**2 - 1)*(Aa**2 - 1)*c2)/(2*(Aw**2 + 1)*(Aa**2 + 1))

db = lambda x: 10*np.log10(max(x, 1e-12))

print("=== 1. Jones vs closed form ===")
worst = 0.0
for _ in range(20000):
    ARw = rng.uniform(0, 20); ARa = rng.uniform(0, 20)
    tw = rng.uniform(0, 180); ta = rng.uniform(0, 180)
    same = rng.random() < 0.5
    hw = +1; ha = +1 if same else -1
    pj = plf_jones(jones(ARw, tw, hw), jones(ARa, ta, ha))
    pf = plf_formula(ARw, ARa, tw - ta, same)
    worst = max(worst, abs(pj - pf))
print(f"  max |Jones - formula| over 20000 random cases: {worst:.2e}")

print("\n=== 2. Special cases ===")
for dt in (0, 15, 30, 45, 60, 75, 85, 89, 90):
    print(f"  linear-linear misalignment {dt:2d} deg: PLF = {db(plf_formula(np.inf, np.inf, dt)):7.2f} dB")
print(f"  linear -> ideal circular: {db(plf_formula(np.inf, 0.0, 0)):.2f} dB (any tilt)")
print(f"  RHCP -> RHCP: {db(plf_formula(0.0, 0.0, 0, True)):.2f} dB;  RHCP -> LHCP: {db(plf_formula(0.0, 0.0, 0, False)):.1f} dB (ideal)")
for ARa in (1.0, 3.0, 6.0):
    pmax = plf_formula(np.inf, ARa, 0); pmin = plf_formula(np.inf, ARa, 90)
    print(f"  linear wave -> CP antenna with AR {ARa} dB: PLF between {db(pmin):.2f} and {db(pmax):.2f} dB (depends on tilt)")
for ARw, ARa in ((3.0, 3.0), (1.0, 1.0), (6.0, 3.0)):
    same = [plf_formula(ARw, ARa, t, True) for t in (0, 90)]
    opp = [plf_formula(ARw, ARa, t, False) for t in (0, 90)]
    print(f"  AR_w={ARw} dB, AR_a={ARa} dB: co-hand PLF {db(min(same)):.2f}..{db(max(same)):.2f} dB; "
          f"cross-hand {db(min(opp)):.1f}..{db(max(opp)):.1f} dB")

print("\n=== 3. Rocket attitude: axial dipole seen from the ground station ===")
def rocket_case(D, h, pitch_deg=0.0, az_deg=0.0):
    """GS at origin (antenna vertical-linear or CP, pointed at rocket). Rocket at ground distance D along +x,
    altitude h. Rocket axis: from vertical, tilted by pitch toward azimuth az (0 = away from GS)."""
    r = np.array([D, 0.0, h])
    u = -r/np.linalg.norm(r)                     # propagation direction rocket -> GS
    p = np.radians(pitch_deg); a = np.radians(az_deg)
    ax = np.array([np.sin(p)*np.cos(a), np.sin(p)*np.sin(a), np.cos(p)])
    cospsi = np.dot(ax, u)
    sinpsi2 = 1 - cospsi**2
    E = ax - cospsi*u                            # radiated E direction (perpendicular to u)
    nE = np.linalg.norm(E)
    Eh = E/nE if nE > 1e-12 else np.array([0, 1.0, 0])
    z = np.array([0, 0, 1.0])
    V = z - np.dot(z, u)*u; V = V/np.linalg.norm(V)          # GS 'vertical' linear, projected
    plf_v = np.dot(Eh, V)**2
    g_db = db(sinpsi2)                                       # relative to broadside (dipole 2.15 dBi)
    return np.degrees(np.arccos(np.clip(abs(cospsi), 0, 1))), g_db, db(plf_v)

print("  psi = angle between rocket axis and LOS; pattern term 10log(sin^2 psi) relative to broadside")
for (D, h, pitch, az, lab) in ((500.0, 3000.0, 0, 0, "GS 0.5 km from pad, vertical ascent to 3 km"),
                               (2000.0, 3000.0, 5, 0, "GS 2 km, 5 deg pitch away"),
                               (10e3, 3000.0, 5, 0, "GS 10 km, 5 deg pitch away"),
                               (10e3, 10e3, 20, 90, "GS 10 km, 20 deg pitch sideways"),
                               (20e3, 1000.0, 60, 180, "descent under chute swinging 60 deg"),
                               (5e3, 30.0, 90, 0, "near landing, body horizontal pointing away"),
                               (5e3, 30.0, 90, 90, "near landing, body horizontal broadside")):
        psi, g, pv = rocket_case(D, h, pitch, az)
        print(f"  {lab:46s}: psi={psi:6.1f} deg, pattern {g:7.1f} dB, vertical-linear GS PLF {pv:7.1f} dB, CP GS PLF -3.0 dB")
