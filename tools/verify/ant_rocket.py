#!/usr/bin/env python3
"""
ant_rocket.py -- geometry and link checks for kb/08-antennas/antennas-on-rockets.md

1. Look angle from the rocket axis (aft direction) to the ground station vs altitude and
   horizontal range, and the resulting pattern loss of an axially-mounted dipole/monopole
   (sin^2 pattern of a lambda/2 dipole: [cos(pi/2 cos t)/sin t]^2).
2. Free-space path loss and received power for the reader's radios (433 MHz 2 W, 915 MHz 1 W),
   with the pattern and polarization terms, vs a SX1262/SX1276-class LoRa sensitivity.
3. Plume-blockage cone: fraction of the boost where the line of sight lies within 22 deg of the
   aft axis (Kinefuchi et al. 2015 reported strong attenuation below ~22 deg for M-V).

Run: python3 tools/verify/ant_rocket.py
"""
import numpy as np

C0 = 299792458.0


def dipole_pattern_dB(theta):
    s = np.sin(theta)
    s = np.where(np.abs(s) < 1e-9, 1e-9, s)
    F = np.cos(np.pi / 2 * np.cos(theta)) / s
    return 20 * np.log10(np.maximum(np.abs(F), 1e-6))   # relative to broadside (0 dB)


def fspl_dB(d, f):
    return 20 * np.log10(4 * np.pi * d * f / C0)


def main():
    print("=== 1. Look angle from aft axis (vertical rocket) and axial-dipole pattern loss ===")
    print(f"{'alt km':>7s} {'range km':>9s} {'slant km':>9s} {'angle from aft':>15s} {'dipole loss dB':>15s}")
    for h in [1, 3, 10, 30]:
        for d in [0.5, 2, 5, 15]:
            ang = np.arctan2(d, h)          # angle between downward axis and LOS
            loss = -dipole_pattern_dB(ang)
            print(f"{h:7.1f} {d:9.1f} {np.hypot(h,d):9.2f} {np.degrees(ang):14.1f}° {loss:15.1f}")

    print("\n=== 2. Link budget at apogee (vertical rocket, axial dipole on rocket, ground antenna gain Gr) ===")
    cases = [("E22-400T33D 433 MHz, 33 dBm", 433e6, 33.0), ("E220-900T30D 915 MHz, 30 dBm", 915e6, 30.0)]
    sens = {"SF7/125k": -124.0, "SF9/125k": -129.0, "SF12/125k": -137.0}   # Semtech SX126x class, typical datasheet values
    for (name, f, Pt) in cases:
        for (h, d) in [(3, 1), (10, 2), (10, 10), (30, 5)]:
            R = np.hypot(h, d) * 1e3
            ang = np.arctan2(d, h)
            Gt = 2.15 + dipole_pattern_dB(ang)
            for (lab, Gr, plf) in [("linear 3-el Yagi 9 dBi, aligned", 9.0, 0.0),
                                   ("CP helix/crossed-Yagi 9 dBic (-3 dB PLF)", 9.0, -3.0)]:
                Pr = Pt + Gt + Gr + plf - fspl_dB(R, f) - 2.0   # 2 dB cable/misc loss
                print(f"  {name}: h = {h} km, d = {d} km, slant {R/1e3:.1f} km, angle {np.degrees(ang):4.1f}°, "
                      f"Gt = {Gt:6.1f} dBi, RX {lab}: Pr = {Pr:6.1f} dBm, margin vs SF9 = {Pr-sens['SF9/125k']:5.1f} dB")
    print("  NOTE: linear-linear 'aligned' is optimistic; roll and pendulum motion add fades to -20 dB or worse.")

    print("\n=== 3. Plume cone (LOS within 22 deg of aft axis) during a vertical boost ===")
    for d in [0.5, 1, 2, 5]:
        # LOS within 22 deg of aft axis when atan(d/h) < 22 deg -> h > d / tan(22 deg)
        hmin = d / np.tan(np.radians(22))
        print(f"  ground station {d} km from pad: LOS inside 22° cone once altitude > {hmin:.2f} km")



if __name__ == "__main__":
    main()
