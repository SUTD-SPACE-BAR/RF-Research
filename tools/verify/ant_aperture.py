#!/usr/bin/env python3
"""
ant_aperture.py -- checks for antenna-fundamentals.md and horn-reflector-aperture-antennas.md

1. Effective aperture A_e = lambda^2 G / (4 pi) for dipole / patch / Yagi / dish at reader bands.
2. Beamwidth-directivity approximations (Kraus 41253/(t1 t2), Tai-Pereira 72815/(t1^2 + t2^2),
   and the practical 26000-32000/(t1 t2) range) vs exact directivity of cos^n patterns.
3. Uniform rectangular aperture: D = 4 pi A / lambda^2 exactly (numerical far-field integration).
4. Parabolic reflector with a cos^q(theta') feed: taper, spillover and aperture efficiency vs
   f/D (Silver/Balanis formulation), optimum edge taper; dish gain eta (pi D / lambda)^2.
5. Optimum-gain pyramidal horn: aperture efficiency ~0.51; design at 5.8 GHz / 10 GHz,
   solving Balanis' horn design equation for chi.
6. Far-field distances 2 D^2/lambda.

Run: python3 tools/verify/ant_aperture.py
"""
import numpy as np
from scipy.optimize import brentq
from scipy.integrate import quad

C0 = 299792458.0
_trapz = getattr(np, "trapezoid", None) or np.trapz


def Ae(G_dBi, f):
    lam = C0 / f
    return lam ** 2 * 10 ** (G_dBi / 10) / (4 * np.pi)


def cosn_directivity(n):
    """U = cos^n(theta) for theta < 90 deg, 0 behind. Exact D = 2(n+1)."""
    return 2 * (n + 1)


def cosn_hpbw(n):
    return 2 * np.degrees(np.arccos(0.5 ** (1 / n)))


def uniform_aperture_D(a_l, b_l):
    """a x b (wavelengths) uniform, in-phase aperture, x-polarised: far field ~ (1+cos th)/2 obliquity
    (Huygens source) times the 2-D sinc. Integrate numerically."""
    k = 2 * np.pi
    th = np.linspace(0, np.pi, 3001)
    ph = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    X = k * a_l / 2 * np.sin(TH) * np.cos(PH)
    Y = k * b_l / 2 * np.sin(TH) * np.sin(PH)
    sx = np.sinc(X / np.pi); sy = np.sinc(Y / np.pi)
    U = ((1 + np.cos(TH)) / 2) ** 2 * (sx * sy) ** 2
    P = _trapz(np.sum(U, axis=1) * (ph[1] - ph[0]) * np.sin(th), th)
    return 4 * np.pi * U[0, 0] / P


def dish_efficiency(q, f_over_D):
    """Feed power pattern G_f(t) = 2(2q+1) cos^(2q)(t) for t < 90 deg (Balanis 15.4 style).
    Returns (taper eff, spillover eff, aperture eff, edge taper dB incl. space loss)."""
    th0 = 2 * np.arctan(1 / (4 * f_over_D))    # half angle subtended by the rim
    Gf = lambda t: 2 * (2 * q + 1) * np.cos(t) ** (2 * q)
    # spillover: fraction of feed power intercepted
    num, _ = quad(lambda t: Gf(t) * np.sin(t), 0, th0)
    den, _ = quad(lambda t: Gf(t) * np.sin(t), 0, np.pi / 2)
    e_s = num / den
    # aperture efficiency (Silver): eps_ap = cot^2(th0/2) |int_0^th0 sqrt(Gf) tan(t/2) dt|^2
    I, _ = quad(lambda t: np.sqrt(Gf(t)) * np.tan(t / 2), 0, th0)
    e_ap = (1 / np.tan(th0 / 2)) ** 2 * I ** 2
    e_t = e_ap / e_s
    # edge taper: feed pattern at th0 relative to boresight, plus spherical spreading (cos^2(th0/2))
    edge = 10 * np.log10(np.cos(th0) ** (2 * q)) + 20 * np.log10(np.cos(th0 / 2) ** 2)
    return e_t, e_s, e_ap, edge, np.degrees(th0)


def optimum_horn(G_dBi, f, a, b):
    """Balanis 4th ed. sec. 13.4.3 design of an optimum-gain pyramidal horn fed by a x b waveguide.
    Solves (sqrt(2chi)-b/lam)^2 (2chi-1) = (G/(2pi) sqrt(3/(2pi)) 1/sqrt(chi) - a/lam)^2 (G^2/(6 pi^3) 1/chi - 1)."""
    lam = C0 / f
    G = 10 ** (G_dBi / 10)
    A_, B_ = a / lam, b / lam
    def eq(chi):
        lhs = (np.sqrt(2 * chi) - B_) ** 2 * (2 * chi - 1)
        rhs = (G / (2 * np.pi) * np.sqrt(3 / (2 * np.pi)) / np.sqrt(chi) - A_) ** 2 * (G ** 2 / (6 * np.pi ** 3) / chi - 1)
        return lhs - rhs
    chi1 = G / (2 * np.pi * np.sqrt(2 * np.pi))  # Balanis' first trial value
    chi = brentq(eq, 0.3 * chi1, 3 * chi1)
    rho_e = chi * lam
    rho_h = G ** 2 / (8 * np.pi ** 3) / chi * lam
    a1 = np.sqrt(3 * lam * rho_h)
    b1 = np.sqrt(2 * lam * rho_e)
    pe = (b1 - b) * np.sqrt((rho_e / b1) ** 2 - 0.25)
    ph = (a1 - a) * np.sqrt((rho_h / a1) ** 2 - 0.25)
    e_ap = G / (4 * np.pi * a1 * b1 / lam ** 2)
    return dict(a1=a1, b1=b1, rho_e=rho_e, rho_h=rho_h, pe=pe, ph=ph, e_ap=e_ap)


def main():
    print("=== 1. Effective aperture ===")
    for (name, G, f) in [("isotropic @ 433 MHz", 0.0, 433e6), ("lambda/2 dipole @ 433 MHz", 2.15, 433e6),
                         ("lambda/2 dipole @ 915 MHz", 2.15, 915e6), ("lambda/2 dipole @ 2.45 GHz", 2.15, 2.45e9),
                         ("GNSS patch 3 dBic @ 1575 MHz", 3.0, 1575.42e6), ("11-el Yagi 14.2 dBi @ 433 MHz", 14.2, 433e6),
                         ("1.2 m dish 60% @ 2.45 GHz", 10 * np.log10(0.6 * (np.pi * 1.2 * 2.45e9 / C0) ** 2), 2.45e9)]:
        print(f"  {name:32s} G = {G:5.2f} dBi  Ae = {Ae(G, f)*1e4:9.2f} cm^2")

    print("\n=== 2. Beamwidth-directivity approximations vs exact (U = cos^n, forward hemisphere) ===")
    print(f"  {'n':>4s} {'HPBW':>7s} {'exact D':>8s} {'Kraus':>8s} {'Tai-Pereira':>11s} {'32400/bw^2':>10s}")
    for n in [1, 2, 4, 10, 20, 50, 100]:
        bw = cosn_hpbw(n)
        D = cosn_directivity(n)
        k = 41253 / bw ** 2
        tp = 72815 / (2 * bw ** 2)
        print(f"  {n:4d} {bw:7.1f} {10*np.log10(D):8.2f} {10*np.log10(k):8.2f} {10*np.log10(tp):11.2f} {10*np.log10(32400/bw**2):10.2f}  dB")

    print("\n=== 3. Uniform aperture directivity vs 4 pi A / lambda^2 ===")
    for (a_l, b_l) in [(2, 2), (4, 3), (6, 6)]:
        D = uniform_aperture_D(a_l, b_l)
        print(f"  {a_l} x {b_l} lambda: numeric D = {10*np.log10(D):.2f} dBi, 4 pi A/lam^2 = {10*np.log10(4*np.pi*a_l*b_l):.2f} dBi")

    print("\n=== 4. Parabolic reflector with cos^q feed ===")
    for fd in [0.3, 0.4, 0.5, 0.6]:
        best = None
        for q in np.arange(0.5, 12.01, 0.25):
            et, es, ea, edge, th0 = dish_efficiency(q, fd)
            if best is None or ea > best[2]:
                best = (q, et, ea, es, edge, th0)
        q, et, ea, es, edge, th0 = best
        print(f"  f/D = {fd}: rim half-angle {th0:.1f} deg, best feed q = {q:.2f}: taper eff = {et:.3f}, "
              f"spillover eff = {es:.3f}, aperture eff = {ea:.3f}, edge illumination = {edge:.1f} dB")
    for (D, f) in [(0.6, 1.575e9), (1.2, 2.45e9), (1.2, 5.8e9), (3.0, 1.42e9)]:
        G = 0.60 * (np.pi * D * f / C0) ** 2
        bw = 70 * (C0 / f) / D
        print(f"  dish {D} m @ {f/1e9:.3f} GHz, eta = 0.60: G = {10*np.log10(G):.1f} dBi, HPBW ~ 70 lam/D = {bw:.1f} deg")

    print("\n=== 5. Optimum-gain pyramidal horn (Balanis design method) ===")
    for (G, f, a, b, wg) in [(15.0, 5.8e9, 40.39e-3, 20.19e-3, "WR-159"), (20.0, 10.0e9, 22.86e-3, 10.16e-3, "WR-90"),
                             (14.0, 2.45e9, 86.36e-3, 43.18e-3, "WR-340")]:
        r = optimum_horn(G, f, a, b)
        print(f"  {G} dBi @ {f/1e9} GHz ({wg}): aperture {r['a1']*1e3:.1f} x {r['b1']*1e3:.1f} mm, "
              f"pe = {r['pe']*1e3:.1f} mm, ph = {r['ph']*1e3:.1f} mm (should match), aperture eff = {r['e_ap']:.3f}")

    print("\n=== 6. Far-field distance 2 D^2 / lambda ===")
    for (name, D, f) in [("lambda/2 dipole 433 MHz (use max(2D^2/lam, few lam))", 0.33, 433e6),
                         ("11-el 433 MHz Yagi (boom 1.72 m)", 1.72, 433e6), ("GNSS patch 25 mm", 0.025, 1575.42e6),
                         ("2.45 GHz 4x4 patch array 0.25 m", 0.25, 2.45e9), ("1.2 m dish 5.8 GHz", 1.2, 5.8e9)]:
        lam = C0 / f
        print(f"  {name:52s} 2D^2/lam = {2*D**2/lam:7.2f} m, lam = {lam:.3f} m")


if __name__ == "__main__":
    main()
