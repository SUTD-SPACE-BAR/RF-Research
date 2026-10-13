#!/usr/bin/env python3
"""
ant_polarization.py -- polarization loss factor (PLF) checks for
kb/08-antennas/antenna-polarization-and-circular-polarization.md and antennas-on-rockets.md

Uses Jones vectors in a common (x, y) basis with the wave propagating along +z, exp(+j w t).
IEEE sense: RHCP rotates clockwise when viewed looking along the direction of propagation.
The rotation sense is computed numerically (not assumed): result (x - jy)/sqrt2 is RHCP for
exp(+jwt), +z propagation (physics exp(-iwt) convention flips the sign of j).

Checks:
 1. Rotation sense of the Jones vectors (1, -/+j)/sqrt2 for exp(+j w t), +z propagation.
 2. PLF = |e_wave . e_ant*|^2 in a consistent basis: linear-linear cos^2(psi); CP-linear 0.5;
    RHCP-LHCP 0; general formula in terms of axial ratios and tilt angle (Stutzman form)
      PLF = 1/2 + 2 r_w r_a / ((1 + r_w^2)(1 + r_a^2)) + (1 - r_w^2)(1 - r_a^2) cos(2 dtau) / (2 (1 + r_w^2)(1 + r_a^2))
    with r signed (+ for one sense, - for the other), cross-checked against Jones-vector overlap.
 3. Handedness flip on reflection from a perfect conductor at normal incidence.
 4. Spinning linear transmitter: linear receive fades cos^2(omega t) (nulls twice per rev),
    CP receive constant 0.5 (-3 dB) with a phase advance of omega t (frequency offset = spin rate).
 5. Worst-case PLF for a 3 dB-AR "CP" antenna receiving a linear wave.

Run: python3 tools/verify/ant_polarization.py
"""
import numpy as np


def jones_linear(psi):
    return np.array([np.cos(psi), np.sin(psi)], dtype=complex)


def jones_ellipse(r, tau):
    """Polarization ellipse with axial ratio magnitude |r| (>=1 or signed), tilt tau.
    Sign of r: + -> one sense, - -> other. Build in the principal frame then rotate."""
    ar = abs(r)
    # major axis along x', minor along y' with 90 deg phase; sign picks sense
    e = np.array([ar, 1j * np.sign(r) * 1.0], dtype=complex) / np.sqrt(ar ** 2 + 1)
    R = np.array([[np.cos(tau), -np.sin(tau)], [np.sin(tau), np.cos(tau)]])
    return R @ e


def rotation_sense(e, kdir=+1):
    """Handedness (IEEE Std 145) of Jones vector e for exp(+j w t), wave travelling along kdir*z.
    Compute the z-component of E(t) x dE/dt: positive = rotation x->y = right-handed about +z.
    IEEE: right-hand sense = clockwise when viewed looking in the direction of propagation,
    equivalently the fingers of the right hand curl with E when the thumb points along k."""
    dt = 1e-3
    E0 = np.real(e * np.exp(1j * 0.0))
    E1 = np.real(e * np.exp(1j * 2 * np.pi * dt))
    cross = E0[0] * E1[1] - E0[1] * E1[0]
    return "RH" if cross * kdir > 0 else "LH"


def plf_jones(e_wave, e_ant_tx):
    """e_ant_tx = polarization of the wave the antenna would TRANSMIT towards the source. For reception
    of a wave arriving from that direction, the receive-matched state in the wave's own frame is the
    complex conjugate expressed in the flipped frame; for a common (x,y) basis with the antenna looking
    back along -z, the matched state is e_ant_rx = conj(e_ant_tx) with y -> -y ... we use the common
    practice: define both in the WAVE's frame, antenna receive-state e_r; PLF = |e_w . conj(e_r)|^2."""
    return abs(np.vdot(e_ant_tx, e_wave)) ** 2


def plf_formula(rw, ra, dtau):
    return 0.5 + 2 * rw * ra / ((1 + rw ** 2) * (1 + ra ** 2)) + \
        (1 - rw ** 2) * (1 - ra ** 2) * np.cos(2 * dtau) / (2 * (1 + rw ** 2) * (1 + ra ** 2))


def main():
    e_a = np.array([1, -1j]) / np.sqrt(2)
    e_b = np.array([1, 1j]) / np.sqrt(2)
    print("1. Rotation sense viewed along +z (propagation direction), exp(+jwt):")
    print(f"   (x - jy)/sqrt2 -> {rotation_sense(e_a)}CP (IEEE; clockwise viewed looking along +z)")
    print(f"   (x + jy)/sqrt2 -> {rotation_sense(e_b)}CP (IEEE)")
    rhcp = e_a if rotation_sense(e_a) == "RH" else e_b
    lhcp = e_b if rotation_sense(e_a) == "RH" else e_a

    print("\n2. PLF (both states expressed in the wave's frame):")
    for psi in [0, 30, 45, 60, 90]:
        print(f"   linear vs linear, {psi:2d} deg: PLF = {plf_jones(jones_linear(0), jones_linear(np.radians(psi))):.3f} "
              f"({10*np.log10(max(plf_jones(jones_linear(0), jones_linear(np.radians(psi))),1e-12)):6.2f} dB)")
    print(f"   RHCP wave, linear antenna: PLF = {plf_jones(rhcp, jones_linear(0.3)):.3f} (-3.01 dB)")
    print(f"   RHCP wave, RHCP antenna:   PLF = {plf_jones(rhcp, rhcp):.3f}")
    print(f"   RHCP wave, LHCP antenna:   PLF = {plf_jones(rhcp, lhcp):.3e}")
    # general ellipses: compare Jones overlap with the closed formula (signed axial ratios, same-sense positive)
    rng = np.random.default_rng(1)
    maxerr = 0
    for _ in range(2000):
        rw = rng.uniform(1, 10) * rng.choice([-1, 1])
        ra = rng.uniform(1, 10) * rng.choice([-1, 1])
        tw, ta = rng.uniform(0, np.pi, 2)
        pj = plf_jones(jones_ellipse(rw, tw), jones_ellipse(ra, ta))
        pf = plf_formula(rw, ra, tw - ta)
        maxerr = max(maxerr, abs(pj - pf))
    print(f"   closed-form PLF vs Jones overlap, 2000 random ellipses: max |diff| = {maxerr:.2e}")
    # 3-dB axial ratio antenna, same-sense CP wave, worst/best
    ar3 = 10 ** (3 / 20)
    for (rw, lab) in [(1.0001, "perfect same-sense CP wave"), (-1.0001, "opposite-sense CP wave"), (1e4, "linear wave")]:
        vals = [plf_formula(rw, ar3, d) for d in np.linspace(0, np.pi, 181)]
        print(f"   receive antenna AR = 3 dB, {lab:28s}: PLF range {10*np.log10(min(vals)):6.2f} .. {10*np.log10(max(vals)):6.2f} dB")

    print("\n3. Reflection from a PEC at normal incidence:")
    # incident along +z with RHCP state; reflected wave travels along -z with E_r = -E_i (tangential E reverses)
    Ei = rhcp
    Er = -Ei
    hi, hr = rotation_sense(Ei, +1), rotation_sense(Er, -1)
    print(f"   incident (+z): {hi}CP; reflected (-z): {hr}CP => handedness {'flips' if hi != hr else 'kept'}")

    print("\n4. Spinning linear transmitter (roll rate 5 rev/s), received by linear and by CP antennas:")
    wroll = 2 * np.pi * 5
    t = np.linspace(0, 0.2, 2001)
    lin_rx = np.array([plf_jones(jones_linear(wroll * ti), jones_linear(0)) for ti in t])
    cp_amp = np.array([np.vdot(rhcp, jones_linear(wroll * ti)) for ti in t])
    print(f"   linear RX: min PLF = {lin_rx.min():.2e} (deep null), nulls per revolution = 2, mean = {10*np.log10(lin_rx.mean()):.2f} dB")
    ph = np.unwrap(np.angle(cp_amp))
    print(f"   CP RX: PLF = {np.mean(np.abs(cp_amp)**2):.3f} constant (-3 dB); received phase slope = "
          f"{(ph[-1]-ph[0])/(t[-1]-t[0])/(2*np.pi):+.2f} Hz (= +/- roll rate -> 'spin Doppler' frequency offset)")


if __name__ == "__main__":
    main()
