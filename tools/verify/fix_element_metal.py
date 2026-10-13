#!/usr/bin/env python3
"""Myth check: "aluminium vs copper changes a dipole's resonant length".  (W5-E1, 2026-10-02)

For a good conductor the metal enters only through the surface impedance Zs = (1+j) Rs,
Rs = sqrt(pi f mu0 mu_r / sigma). Per unit length of round wire (radius a, skin depth << a):
  R' = X'_int = Rs / (2 pi a)     ->  internal inductance L'_int = Rs / (2 pi a w)
The external (geometric) inductance of a thin dipole wire is roughly L'_ext ~ (mu0/2pi)(ln(2h/a) - 1).
The extra internal inductance slows the wave by ~ L'_int/(2 L'_ext), shortening the resonant length
by that fraction. Loss resistance of a half-wave dipole (sinusoidal current, referred to the feed):
  R_loss ~ R' * L / 2.
Material constants: Cu 5.8e7, Al 3.5e7, brass 1.6e7, stainless 1.4e6 S/m (non-magnetic); mu_r = 1.
Run: python3 tools/verify/fix_element_metal.py  -> ALL PASS
"""
import math

MU0 = 4e-7 * math.pi
METALS = {"copper": 5.8e7, "aluminium": 3.5e7, "brass": 1.6e7, "stainless (304)": 1.4e6}


def analyse(f, a, L, sigma, mu_r=1.0, R_rad=72.0):
    w = 2 * math.pi * f
    Rs = math.sqrt(math.pi * f * MU0 * mu_r / sigma)
    Rp = Rs / (2 * math.pi * a)
    Lint = Rp / w
    h = L / 2
    Lext = MU0 / (2 * math.pi) * (math.log(2 * h / a) - 1)
    shorten = Lint / (2 * Lext)            # fractional shortening of resonant length
    Rloss = Rp * L / 2
    eff = R_rad / (R_rad + Rloss)
    return Rs, shorten, Rloss, eff


def main():
    f, a, L = 433.92e6, 1.0e-3, 0.328     # 2 mm wire dipole resonant at ~328 mm (08/dipoles page)
    print(f"433.92 MHz half-wave dipole, 2 mm wire, L = {L*1000:.0f} mm")
    res = {}
    for m, s in METALS.items():
        Rs, sh, Rl, eff = analyse(f, a, L, s)
        res[m] = (sh, Rl, eff)
        print(f"  {m:16s} Rs={Rs*1e3:6.2f} mOhm  length shift {-sh*100:7.4f} % ({-sh*L*1e3:6.3f} mm)  "
              f"R_loss={Rl:5.2f} Ohm  efficiency {eff*100:6.2f} % ({10*math.log10(eff):6.3f} dB)")
    d_mm = (res["copper"][0] - res["aluminium"][0]) * L * 1e3
    print(f"Cu vs Al resonant-length difference: {abs(d_mm)*1000:.0f} um (cutting tolerance is ~1 mm)")
    assert abs(d_mm) < 0.05                                    # < 50 um on 328 mm
    assert 10 * math.log10(res["aluminium"][2]) > -0.02        # Al costs < 0.02 dB
    assert 10 * math.log10(res["stainless (304)"][2]) > -0.1   # even stainless costs < 0.1 dB
    # geometry matters far more: thickness factor K from 08/dipoles (lambda/d 5000 -> 100: 0.968 -> 0.930)
    assert (0.968 - 0.930) > 100 * abs(res["copper"][0] - res["aluminium"][0])
    print("ALL PASS")


if __name__ == "__main__":
    main()
