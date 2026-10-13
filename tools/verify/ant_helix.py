#!/usr/bin/env python3
"""
ant_helix.py -- axial-mode helix gain: Kraus vs King & Wong (1980) vs Emerson (1995).

Kraus (1947/1988):  G = 15 (C/lam)^2 N S/lam      (linear, "directive gain")
                    HPBW = 52 / ((C/lam) sqrt(N S/lam)) deg,  R_in ~ 140 (C/lam) ohm,
                    AR = (2N + 1)/(2N)
King & Wong (IEEE TAP AP-28, 1980), measured, 12 < alpha < 15 deg, 3/4 < C/lam < 4/3, N > 3:
                    Gp = 8.3 (pi D/lam_p)^(sqrt(N+2) - 1) (N S/lam_p)^0.8 [tan 12.5 / tan alpha]^(sqrt(N)/2)
                    (lam_p = wavelength of peak gain; peak at C/lam_p ~ 1.07-1.16)
Emerson (ARRL Antenna Compendium 4, 1995), ~10^4 NEC-2 runs, L = axial length 2..7 lam:
                    Gmax(dBi) = 10.25 + 1.22 L - 0.0726 L^2,
                    optimum radius R/lam = 0.2025 - 0.0079 L + 0.000515 L^2

Also: design dimensions for 433 MHz and 2.45 GHz ground-station helices, and the Kraus
gain-beamwidth product vs King & Wong's measured G*HPBW^2 = 24000-31500.

Run: python3 tools/verify/ant_helix.py
"""
import numpy as np

C0 = 299792458.0


def kraus_G(C_l, S_l, N):
    return 15 * C_l ** 2 * N * S_l


def kraus_hpbw(C_l, S_l, N):
    return 52 / (C_l * np.sqrt(N * S_l))


def king_wong_G(C_l, alpha_deg, N):
    S_l = C_l * np.tan(np.radians(alpha_deg))
    return 8.3 * C_l ** (np.sqrt(N + 2) - 1) * (N * S_l) ** 0.8 * \
        (np.tan(np.radians(12.5)) / np.tan(np.radians(alpha_deg))) ** (np.sqrt(N) / 2)


def emerson_G_dB(L_l):
    return 10.25 + 1.22 * L_l - 0.0726 * L_l ** 2


def emerson_R(L_l):
    return 0.2025 - 0.0079 * L_l + 0.000515 * L_l ** 2


def main():
    alpha = 12.8
    print("Gain comparison, pitch angle 12.8 deg (S = C tan alpha), C/lam = 1.10 for Kraus & King-Wong:")
    print(f"{'N':>4s} {'L/lam':>6s} {'Kraus dBi':>10s} {'KingWong':>9s} {'Emerson':>8s} {'K-KW dB':>8s} {'K-E dB':>7s} {'KrausHPBW':>9s}")
    for N in [5, 8, 10, 12, 15, 20, 25, 30]:
        C_l = 1.10
        S_l = C_l * np.tan(np.radians(alpha))
        L_l = N * S_l
        gk = 10 * np.log10(kraus_G(C_l, S_l, N))
        gkw = 10 * np.log10(king_wong_G(C_l, alpha, N))
        ge = emerson_G_dB(L_l) if 2 <= L_l <= 7 else np.nan
        print(f"{N:4d} {L_l:6.2f} {gk:10.2f} {gkw:9.2f} {ge:8.2f} {gk-gkw:8.2f} {gk-ge:7.2f} {kraus_hpbw(C_l,S_l,N):9.1f}")
    print("\nKraus gain-beamwidth product 15 C^2 NS * (52/(C sqrt(NS)))^2 = 15*2704 =", 15 * 52 ** 2,
          "(vs 41253 ideal, 24000-31500 measured by King & Wong)")

    print("\nEmerson optimum circumference C/lam = 2 pi R/lam:")
    for L in [2, 3, 4, 5, 6, 7]:
        print(f"   L = {L} lam: R = {emerson_R(L):.4f} lam -> C = {2*np.pi*emerson_R(L):.3f} lam, Gmax = {emerson_G_dB(L):.2f} dBi")

    print("\nDesign examples (C = 1.1 lam, S = 0.25 lam, ground plane >= 0.5 lam square or cup):")
    for (name, f, N) in [("435 MHz ground station", 435e6, 10), ("435 MHz ground station", 435e6, 6),
                         ("2.45 GHz", 2.45e9, 12), ("1.27 GHz (L-band uplink)", 1.27e9, 10)]:
        lam = C0 / f
        C = 1.1 * lam
        D = C / np.pi
        S = 0.25 * lam
        L = N * S
        gkw = 10 * np.log10(king_wong_G(1.1, np.degrees(np.arctan(0.25 / 1.1)), N))
        ge = emerson_G_dB(L / lam) if L / lam >= 2 else np.nan
        print(f"   {name:26s} N = {N:2d}: D = {D*1000:6.1f} mm, S = {S*1000:6.1f} mm, L = {L*1000:6.0f} mm "
              f"({L/lam:.2f} lam), Kraus = {10*np.log10(kraus_G(1.1,0.25,N)):.1f}, King-Wong = {gkw:.1f}, Emerson = {ge:.1f} dBi, "
              f"R_in ~ {140*1.1:.0f} ohm")


if __name__ == "__main__":
    main()
