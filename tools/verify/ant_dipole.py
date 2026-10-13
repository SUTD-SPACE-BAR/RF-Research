#!/usr/bin/env python3
"""
ant_dipole.py -- verification of classical linear-antenna results used in kb/08-antennas.

Checks (all with an assumed sinusoidal current distribution, thin wire, free space):
  1. Directivity of the Hertzian (uniform-current) dipole, short (triangular-current) dipole,
     half-wave, full-wave and 1.25-wavelength dipoles by numerical integration of the pattern.
  2. Radiation resistance of a centre-fed dipole of arbitrary length two ways:
       (a) numerical integration of the far-field Poynting flux,
       (b) the closed-form Si/Ci (induced-EMF) expression (Balanis 4th ed. eqs 4-70, 4-71,
           Kraus & Marhefka ch. 6 / Orfanidis EWA ch. 22 give equivalent forms),
     and the induced-EMF reactance, giving 73.1 + j42.5 ohm for l = lambda/2.
  3. Half-power beamwidths (78 deg for lambda/2, 90 deg for the short dipole).
  4. Monopole-over-perfect-ground values (half the dipole impedance, directivity doubled).
  5. Short-dipole radiation resistance formulas 80 pi^2 (l/lambda)^2 (uniform current) and
     20 pi^2 (l/lambda)^2 (triangular current).

Run:  python3 tools/verify/ant_dipole.py
"""
import numpy as np
from scipy.special import sici
from scipy.integrate import quad

ETA = 376.730313668  # free-space wave impedance, ohm
_trapz = getattr(np, "trapezoid", None) or np.trapz
C0 = 299792458.0


def pattern_F(theta, kl):
    """Far-field pattern factor of a centre-fed dipole of total length l (kl = k*l),
    sinusoidal current with maximum I0 (current referred to the current maximum)."""
    s = np.sin(theta)
    s = np.where(np.abs(s) < 1e-12, 1e-12, s)
    return (np.cos(kl / 2 * np.cos(theta)) - np.cos(kl / 2)) / s


def prad_over_I0sq(kl):
    """P_rad / |I0|^2 for the dipole. U = eta |I0|^2 F^2 / (8 pi^2)."""
    f = lambda th: pattern_F(th, kl) ** 2 * np.sin(th)
    val, _ = quad(f, 0, np.pi, limit=400)
    return ETA / (8 * np.pi ** 2) * 2 * np.pi * val


def directivity_numeric(kl):
    th = np.linspace(1e-6, np.pi - 1e-6, 200001)
    F2 = pattern_F(th, kl) ** 2
    Umax = F2.max()
    integral = _trapz(F2 * np.sin(th), th) * 2 * np.pi
    return 4 * np.pi * Umax / integral


def Rr_closed_form(kl):
    """Radiation resistance referred to current maximum, induced-EMF closed form.
    Balanis (4-70): Rr = eta/(2 pi) { C + ln(kl) - Ci(kl) + 1/2 sin(kl)[Si(2kl) - 2 Si(kl)]
                      + 1/2 cos(kl)[C + ln(kl/2) + Ci(2kl) - 2 Ci(kl)] }"""
    Cg = 0.5772156649015329
    Si1, Ci1 = sici(kl)
    Si2, Ci2 = sici(2 * kl)
    return ETA / (2 * np.pi) * (Cg + np.log(kl) - Ci1 + 0.5 * np.sin(kl) * (Si2 - 2 * Si1)
                                + 0.5 * np.cos(kl) * (Cg + np.log(kl / 2) + Ci2 - 2 * Ci1))


def Xm_closed_form(kl, ka_over_kl_term):
    """Induced-EMF reactance referred to current maximum (Balanis 4-71).
    ka_over_kl_term = 2 k a^2 / l  (argument of the last Ci term)."""
    Si1, Ci1 = sici(kl)
    Si2, Ci2 = sici(2 * kl)
    _, Ci3 = sici(ka_over_kl_term)
    return ETA / (4 * np.pi) * (2 * Si1 + np.cos(kl) * (2 * Si1 - Si2)
                                - np.sin(kl) * (2 * Ci1 - Ci2 - Ci3))


def hpbw_deg(kl):
    th = np.linspace(1e-6, np.pi / 2, 400001)
    F2 = pattern_F(th, kl) ** 2
    F2 /= F2.max()
    # dipole maximum is at 90 deg for l <= lambda; find the half-power angle below 90 deg
    idx = np.where(F2 >= 0.5)[0][0]
    return 2 * (90 - np.degrees(th[idx]))


def main():
    print("=== 1. Directivity by numerical integration ===")
    # Hertzian dipole: F = sin(theta)
    th = np.linspace(0, np.pi, 200001)
    D_hz = 4 * np.pi * 1 / (2 * np.pi * _trapz(np.sin(th) ** 3, th))
    print(f"Hertzian/short dipole  D = {D_hz:.4f} ({10*np.log10(D_hz):.2f} dBi)  [expect 1.5, 1.76 dBi]")
    for frac in [0.5, 1.0, 1.25]:
        kl = 2 * np.pi * frac
        D = directivity_numeric(kl)
        print(f"l = {frac:4.2f} lambda      D = {D:.4f} ({10*np.log10(D):.2f} dBi)")
    print("  expect 1.643 (2.15 dBi), 2.41 (3.82 dBi), 3.28 (5.16 dBi)\n")

    print("=== 2. Radiation resistance: numeric flux vs Si/Ci closed form ===")
    for frac in [0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5]:
        kl = 2 * np.pi * frac
        Rn = 2 * prad_over_I0sq(kl)
        Rc = Rr_closed_form(kl)
        s2 = np.sin(kl / 2) ** 2
        Rin = Rn / s2 if s2 > 1e-9 else np.inf
        print(f"l = {frac:4.2f} lambda  Rr(I_max) numeric = {Rn:8.3f}  closed = {Rc:8.3f} ohm  "
              f"Rin(feed) = {Rin:9.2f} ohm")
    kl = np.pi
    a = 1e-4  # radius in wavelengths (thin); last Ci term vanishes as a -> 0 for l = lambda/2
    Xm = Xm_closed_form(kl, 2 * (2 * np.pi) * a ** 2 / 0.5)
    print(f"\nHalf-wave dipole: Z = {Rr_closed_form(kl):.2f} + j{Xm:.2f} ohm  [expect 73.08 + j42.5]")
    print(f"Quarter-wave monopole on infinite PEC ground: Z = {Rr_closed_form(kl)/2:.2f} + j{Xm/2:.2f} ohm")
    print(f"  monopole directivity = 2 x {directivity_numeric(kl):.3f} = {2*directivity_numeric(kl):.3f} "
          f"({10*np.log10(2*directivity_numeric(kl)):.2f} dBi)\n")

    print("=== 3. Half-power beamwidth ===")
    print(f"lambda/2 dipole HPBW = {hpbw_deg(np.pi):.1f} deg [expect ~78]")
    thh = np.degrees(np.arcsin(np.sqrt(0.5)))
    print(f"short dipole HPBW    = {2*(90-thh):.1f} deg [expect 90]")
    print(f"full-wave dipole     = {hpbw_deg(2*np.pi):.1f} deg [expect ~47.8]\n")

    print("=== 5. Short dipoles ===")
    for lf in [0.01, 0.05, 0.1]:
        kl = 2 * np.pi * lf
        # numeric: sinusoidal current approx triangular for short l; Rin at feed
        Rin_num = 2 * prad_over_I0sq(kl) / np.sin(kl / 2) ** 2
        print(f"l = {lf} lambda: Rin(sinusoidal, numeric) = {Rin_num:.4f} ohm;"
              f"  20 pi^2 (l/lam)^2 = {20*np.pi**2*lf**2:.4f};  80 pi^2 (l/lam)^2 (uniform) = {80*np.pi**2*lf**2:.4f}")

    print("\n=== Physical lengths at reader frequencies (free-space, before end-effect shortening) ===")
    for f in [433.0e6, 868e6, 915e6, 1575.42e6, 2450e6]:
        lam = C0 / f
        print(f"{f/1e6:8.2f} MHz: lambda = {lam*1000:7.1f} mm, lambda/2 = {lam*500:6.1f} mm, lambda/4 = {lam*250:6.1f} mm")


if __name__ == "__main__":
    main()
