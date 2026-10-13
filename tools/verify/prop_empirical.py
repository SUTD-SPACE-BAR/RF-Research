#!/usr/bin/env python3
"""
prop_empirical.py — verification / comparison for kb/09-propagation-link-budget/empirical-path-loss-models.md

Models (all return basic transmission loss in dB between the stated antenna types):
  * free space (isotropic)
  * plane earth 40 log d - 20 log(h1 h2)      (isotropic; d, h in m; valid beyond the breakpoint)
  * log-distance  L = L(d0) + 10 n log10(d/d0)  (+ lognormal shadowing sigma)
  * Okumura-Hata (Hata 1980): urban (small/medium and large city), suburban, open.
      Validity: f 150-1500 MHz, hb 30-200 m, hm 1-10 m, d 1-20 km. Antennas: Hata's formulas are
      for the median field; conventionally interpreted as loss between isotropic antennas (see page).
  * COST-231 Hata: f 1500-2000 MHz (medium city/suburban Cm = 0 dB, metropolitan 3 dB)
  * Egli (1957): ratio form Pr/Pt = Gb Gm (hb hm/d^2)^2 (40/f_MHz)^2  -> dB constant 88.0 for isotropic
    gains (hm >= 10 m); widely quoted dB forms use 76.3 - 10 log hm (hm < 10 m) and 83.9 or 85.9 - 20 log hm.
All out-of-range inputs are flagged — not silently extrapolated.
"""
import numpy as np
c = 299792458.0

def fspl(f_mhz, d_km):
    return 32.4478 + 20*np.log10(f_mhz) + 20*np.log10(d_km)

def plane_earth(d_km, h1, h2):
    return 40*np.log10(d_km*1e3) - 20*np.log10(h1*h2)

def hata(f, hb, hm, d, area='urban', city='medium', warn=True):
    msgs = []
    if not (150 <= f <= 1500): msgs.append(f"f={f} MHz outside 150-1500")
    if not (30 <= hb <= 200): msgs.append(f"hb={hb} m outside 30-200")
    if not (1 <= hm <= 10): msgs.append(f"hm={hm} m outside 1-10")
    if not (1 <= d <= 20): msgs.append(f"d={d} km outside 1-20")
    lf = np.log10(f)
    if city == 'large':
        a = 8.29*np.log10(1.54*hm)**2 - 1.1 if f <= 200 else 3.2*np.log10(11.75*hm)**2 - 4.97
    else:
        a = (1.1*lf - 0.7)*hm - (1.56*lf - 0.8)
    L = 69.55 + 26.16*lf - 13.82*np.log10(hb) - a + (44.9 - 6.55*np.log10(hb))*np.log10(d)
    if area == 'suburban':
        L -= 2*np.log10(f/28)**2 + 5.4
    elif area == 'open':
        L -= 4.78*lf**2 - 18.33*lf + 40.94
    return L, msgs

def cost231(f, hb, hm, d, metro=False):
    msgs = []
    if not (1500 <= f <= 2000): msgs.append(f"f={f} MHz outside 1500-2000")
    lf = np.log10(f)
    a = (1.1*lf - 0.7)*hm - (1.56*lf - 0.8)
    L = 46.3 + 33.9*lf - 13.82*np.log10(hb) - a + (44.9 - 6.55*np.log10(hb))*np.log10(d) + (3 if metro else 0)
    return L, msgs

def egli_ratio(f, hb, hm, d_km):
    """Egli (1957) ratio form, isotropic gains: L = 40 log d - 20 log(hb hm) + 20 log(f/40)."""
    return 40*np.log10(d_km*1e3) - 20*np.log10(hb*hm) + 20*np.log10(f/40.0)

def egli_quoted(f, hb, hm, d_km, const_hi=85.9):
    if hm < 10:
        return 20*np.log10(f) + 40*np.log10(d_km) - 20*np.log10(hb) + 76.3 - 10*np.log10(hm)
    return 20*np.log10(f) + 40*np.log10(d_km) - 20*np.log10(hb) + const_hi - 20*np.log10(hm)

def log_distance(d_km, L0, n, d0_km=1.0):
    return L0 + 10*n*np.log10(d_km/d0_km)

if __name__ == "__main__":
    print("=== Egli constant check ===")
    print(f"  ratio form constant (d km, isotropic): 120 - 20 log10(40) = {120 - 20*np.log10(40):.2f} dB; "
          f"with dipole-referenced gains (-2x2.15 dB): {120 - 20*np.log10(40) - 4.3:.2f} dB")
    print(f"  continuity of quoted forms at hm = 10 m: 76.3-10 = {76.3-10:.1f}; 85.9-20 = {85.9-20:.1f}; 83.9-20 = {83.9-20:.1f}")

    print("\n=== Model comparison: GS / base at 30 m, mobile at 1.5 m ===")
    for f in (433.125, 915.0):
        print(f"  f = {f} MHz")
        print(f"   {'d km':>5s} {'FSPL':>7s} {'PlaneE':>7s} {'Hata-U':>7s} {'Hata-S':>7s} {'Hata-O':>7s} {'Egli(r)':>8s} {'Egli(q)':>8s}")
        for d in (1, 2, 5, 10, 20):
            hu, _ = hata(f, 30, 1.5, d, 'urban'); hs, _ = hata(f, 30, 1.5, d, 'suburban'); ho, _ = hata(f, 30, 1.5, d, 'open')
            print(f"   {d:5.0f} {fspl(f,d):7.1f} {plane_earth(d,30,1.5):7.1f} {hu:7.1f} {hs:7.1f} {ho:7.1f} "
                  f"{egli_ratio(f,30,1.5,d):8.1f} {egli_quoted(f,30,1.5,d):8.1f}")
    print("\n=== Out-of-validity example (ground-level LoRa: both antennas 2 m) ===")
    L, msgs = hata(915, 2, 2, 3, 'suburban')
    print(f"  Hata(915 MHz, hb=2 m, hm=2 m, 3 km) = {L:.1f} dB  <- INVALID: {'; '.join(msgs)}")
    print(f"  plane-earth (2 m, 2 m, 3 km) = {plane_earth(3,2,2):.1f} dB; FSPL = {fspl(915,3):.1f} dB")
    print("\n=== Log-distance fits (reference 1 km FSPL) ===")
    for n in (2.0, 2.7, 3.5, 4.0):
        vals = [log_distance(d, fspl(915, 1.0), n) for d in (1, 2, 5, 10)]
        print(f"  n={n}: L(1,2,5,10 km) = " + " ".join(f"{v:6.1f}" for v in vals))
    print("\n=== COST-231 at 1800 MHz (hb 30 m, hm 1.5 m) ===")
    for d in (1, 5):
        L, m = cost231(1800, 30, 1.5, d)
        print(f"  d={d} km: {L:.1f} dB")
