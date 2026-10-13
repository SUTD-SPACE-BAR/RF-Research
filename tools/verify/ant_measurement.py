#!/usr/bin/env python3
"""
ant_measurement.py -- numerical checks for kb/08-antennas/antenna-measurement.md

1. Far-field criterion: path-length (phase) error across an aperture of size D at range R,
   dphi = k (sqrt(R^2 + (D/2)^2) - R) ~ pi D^2 / (4 lambda R); at R = 2D^2/lambda -> pi/8 (22.5 deg).
   Gain error of a uniform square aperture vs range (quadratic phase error), numerically.
2. Three-antenna method: recover G_A, G_B, G_C (dBi) from three pairwise Friis measurements,
   with a simulated +/-0.2 dB measurement noise.
3. Gain-transfer (comparison) method.
4. Wheeler-cap efficiency from R_free and R_cap (series-resonant model) incl. sensitivity.
5. Ground-reflection error on an outdoor range: interference ripple for a given reflection
   coefficient and path difference; required antenna height for a specular point outside a
   given pattern level (flat-earth two-ray).
6. SDR/RSSI pattern measurement: averaging needed for +/-0.5 dB with Rayleigh-like fluctuations
   (statistical), and linearity check reminder.

Run: python3 tools/verify/ant_measurement.py
"""
import numpy as np

C0 = 299792458.0


def phase_error_deg(D, lam, R):
    return np.degrees(2 * np.pi / lam * (np.sqrt(R ** 2 + (D / 2) ** 2) - R))


def aperture_gain_loss_dB(D_l, R_over_ff, n=201):
    """Uniform square aperture D x D (in wavelengths) observed on axis at range R; relative
    on-axis received power vs infinite range (quadratic + exact phase)."""
    lam = 1.0
    D = D_l
    R = R_over_ff * 2 * D ** 2 / lam
    x = np.linspace(-D / 2, D / 2, n)
    X, Y = np.meshgrid(x, x)
    r = np.sqrt(R ** 2 + X ** 2 + Y ** 2)
    field = np.sum(np.exp(-1j * 2 * np.pi / lam * (r - R)) * (R / r)) / n ** 2
    return 20 * np.log10(abs(field))


def three_antenna(PAB, PBC, PAC):
    """Inputs: path gains in dB, P_r/P_t - FSPL-corrected sums G_i + G_j (dB). Returns G_A,G_B,G_C."""
    GA = (PAB + PAC - PBC) / 2
    GB = (PAB + PBC - PAC) / 2
    GC = (PAC + PBC - PAB) / 2
    return GA, GB, GC


def fspl(R, f):
    return 20 * np.log10(4 * np.pi * R * f / C0)


def main():
    print("=== 1. Far-field criterion ===")
    for (name, D, f) in [("11-el 433 MHz Yagi (1.72 m)", 1.72, 433e6), ("25 mm GNSS patch", 0.025, 1575.42e6),
                         ("1.2 m dish @5.8 GHz", 1.2, 5.8e9)]:
        lam = C0 / f
        R = 2 * D ** 2 / lam
        print(f"  {name}: 2D^2/lam = {R:.2f} m -> phase error at edge = {phase_error_deg(D, lam, R):.1f} deg")
    for Dl in [4.0, 10.0]:
        for k in [0.5, 1.0, 2.0, 4.0]:
            print(f"  uniform {Dl} lam square aperture at R = {k} x 2D^2/lam: on-axis gain error = {aperture_gain_loss_dB(Dl, k):+.3f} dB")

    print("\n=== 2. Three-antenna method (simulated) ===")
    rng = np.random.default_rng(3)
    Gtrue = dict(A=9.15, B=2.15, C=14.2)
    f, R = 433e6, 20.0
    meas = {}
    for (i, j) in [("A", "B"), ("B", "C"), ("A", "C")]:
        Pr_Pt = Gtrue[i] + Gtrue[j] - fspl(R, f) + rng.normal(0, 0.2)
        meas[i + j] = Pr_Pt + fspl(R, f)
    GA, GB, GC = three_antenna(meas["AB"], meas["BC"], meas["AC"])
    print(f"  true A/B/C = {Gtrue['A']}/{Gtrue['B']}/{Gtrue['C']} dBi; recovered = {GA:.2f}/{GB:.2f}/{GC:.2f} dBi "
          f"(each pair measured with 0.2 dB rms error; FSPL at 20 m, 433 MHz = {fspl(R,f):.2f} dB)")
    errs = []
    for _ in range(20000):
        m = {k: Gtrue[k[0]] + Gtrue[k[1]] + rng.normal(0, 0.2) for k in ("AB", "BC", "AC")}
        ga, gb, gc = three_antenna(m["AB"], m["BC"], m["AC"])
        errs.append(ga - Gtrue["A"])
    print(f"  Monte Carlo: std of recovered gain = {np.std(errs):.3f} dB (theory sqrt(3)/2 x 0.2 = {np.sqrt(3)/2*0.2:.3f} dB)")

    print("\n=== 3. Gain transfer ===")
    Gref = 2.15
    P_ref, P_aut = -41.3, -34.5   # dBm received, same setup
    print(f"  reference dipole {Gref} dBi gives {P_ref} dBm; AUT gives {P_aut} dBm -> G_AUT = {Gref + P_aut - P_ref:.2f} dBi")

    print("\n=== 4. Wheeler cap ===")
    for (Rf, Rc) in [(12.0, 1.5), (3.0, 1.8), (0.9, 0.6)]:
        eta = (Rf - Rc) / Rf
        # sensitivity to 0.1 ohm error in R_cap
        eta2 = (Rf - (Rc + 0.1)) / Rf
        print(f"  R_free = {Rf} ohm, R_cap = {Rc} ohm -> eta = {eta*100:.1f} % ({10*np.log10(eta):.2f} dB); "
              f"+0.1 ohm error in R_cap -> {eta2*100:.1f} %")
    for f in [433e6, 915e6, 1575.42e6, 2.45e9]:
        print(f"  radiansphere radius lambda/2pi at {f/1e6:.0f} MHz = {C0/f/(2*np.pi)*1000:.0f} mm (min cap radius)")

    print("\n=== 5. Outdoor range ground reflection ===")
    for Gamma_dB in [-10, -20, -30]:
        g = 10 ** (Gamma_dB / 20)
        print(f"  reflected/direct = {Gamma_dB} dB -> received ripple = +{20*np.log10(1+g):.2f} / {20*np.log10(1-g):.2f} dB")
    f = 433e6; lam = C0 / f
    for (h, R) in [(1.5, 10), (3.0, 10), (5.0, 20)]:
        ang = np.degrees(np.arctan(2 * h / R))   # angle below boresight toward the specular point (equal heights)
        dpath = np.sqrt(R ** 2 + (2 * h) ** 2) - R
        print(f"  equal heights {h} m, range {R} m: specular point {ang:.1f} deg below boresight, path difference = {dpath:.2f} m "
              f"({dpath/lam:.2f} lambda)")

    print("\n=== 6. Averaging RSSI samples ===")
    for sigma in [1.0, 2.0, 4.0]:
        n = int(np.ceil((sigma / 0.5) ** 2))
        print(f"  sample std {sigma} dB -> N >= {n} samples per angle for +/-0.5 dB (1 sigma) on the mean")


if __name__ == "__main__":
    main()
