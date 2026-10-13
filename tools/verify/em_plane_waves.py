#!/usr/bin/env python3
"""
em_plane_waves.py — checks for kb/02-electromagnetics/wave-equation-plane-waves-polarization.md
and poynting-vector-power-flow.md

1. gamma = alpha + j beta = sqrt(j w mu (sigma + j w eps)) and eta = sqrt(j w mu/(sigma + j w eps))
   for several media; compare with low-loss and good-conductor approximations.
2. ITU-R P.527 penetration-depth formula (eq. 4) == 1/alpha.
3. Polarization: axial ratio, tilt, handedness (IEEE) from Ex, Ey phasors; numeric check by
   tracing the E vector in time at a fixed point.
4. Poynting / field-strength numbers: 2 W at 1 km, 1 W EIRP at 10 km, E=sqrt(eta S).
"""
import numpy as np

c = 299_792_458.0
mu0 = 1.25663706127e-6
eps0 = 1 / (mu0 * c**2)
eta0 = mu0 * c


def gamma_eta(f, er, sigma=0.0, tand=0.0, mur=1.0):
    w = 2 * np.pi * f
    eps_c = eps0 * er * (1 - 1j * tand) - 1j * sigma / w
    mu = mu0 * mur
    g = np.sqrt(1j * w * mu * 1j * w * eps_c)      # = j w sqrt(mu eps_c)
    if g.real < 0:
        g = -g
    eta = np.sqrt(mu / eps_c)
    return g, eta


print("=== 1. propagation constant and intrinsic impedance ===")
cases = [
    ("air/vacuum 433 MHz", 433e6, 1.0, 0, 0),
    ("FR-4 er=4.4 tand=0.02 @915 MHz", 915e6, 4.4, 0, 0.02),
    ("RO4003C er=3.55 tand=0.0027 @2.45 GHz", 2.45e9, 3.55, 0, 0.0027),
    ("fibreglass/G10 er=4.8 tand=0.02 @915 MHz", 915e6, 4.8, 0, 0.02),
    ("sea water er=70 s=5 @433 MHz", 433e6, 70, 5.0, 0),
    ("sea water er=70 s=5 @2.45 GHz", 2.45e9, 70, 5.0, 0),
    ("fresh water er=80 s=0.01 @433 MHz", 433e6, 80, 0.01, 0),
    ("copper s=5.8e7 @433 MHz", 433e6, 1, 5.8e7, 0),
]
for name, f, er, s, td in cases:
    g, eta = gamma_eta(f, er, s, td)
    a, b = g.real, g.imag
    lam = 2 * np.pi / b
    vp = 2 * np.pi * f / b
    print(f"{name:42s} alpha={a:10.4g} Np/m ({8.686*a:10.4g} dB/m) beta={b:10.4g} rad/m "
          f"lambda={lam*100:9.4g} cm vp/c={vp/c:7.4f} |eta|={abs(eta):9.4g} ohm "
          f"ang={np.degrees(np.angle(eta)):6.2f} deg  1/alpha={1/a if a>0 else np.inf:9.4g} m")

# low-loss approximation check (FR-4)
f, er, td = 915e6, 4.4, 0.02
g, eta = gamma_eta(f, er, 0, td)
a_approx = np.pi * f * np.sqrt(er) / c * td          # alpha ~ (beta/2) tan d
print(f"\nFR-4 low-loss approx alpha = (beta0 sqrt(er) tand)/2 = {a_approx:.5f} Np/m vs exact {g.real:.5f}")
assert abs(a_approx - g.real) / g.real < 1e-3
# dB per wavelength shortcut: 27.3 * sqrt(er)*tand dB/lambda0
print(f"  -> dielectric loss = 27.29*tand dB per guided wavelength = {27.29*td:.3f} dB/lambda_g; "
      f"check {8.686*g.real*(2*np.pi/g.imag):.3f}")

# good conductor approx (copper)
f, s = 433e6, 5.8e7
g, eta = gamma_eta(f, 1, s)
delta = 1 / np.sqrt(np.pi * f * mu0 * s)
print(f"Cu 433 MHz: skin depth approx {delta*1e6:.4f} um vs exact 1/alpha {1/g.real*1e6:.4f} um;"
      f" eta = {eta:.6e} ohm, Rs=1/(sigma delta)={1/(s*delta)*1e3:.4f} mOhm, angle {np.degrees(np.angle(eta)):.3f} deg")
assert abs(delta - 1 / g.real) / delta < 1e-6

print("\n=== 2. ITU-R P.527 penetration depth formula vs 1/alpha ===")
for name, f, er, s in (("sea 433M", 433e6, 70, 5.0), ("sea 2.45G", 2.45e9, 70, 5.0), ("fresh 433M", 433e6, 80, 0.01)):
    w = 2 * np.pi * f
    epp = s / (w * eps0)
    lam0 = c / f
    d_itu = lam0 / (2 * np.pi) * np.sqrt(2) / np.sqrt(np.sqrt(er**2 + epp**2) - er)
    g, _ = gamma_eta(f, er, s)
    print(f"{name}: ITU {d_itu*100:.3f} cm, 1/alpha {100/g.real:.3f} cm")
    assert abs(d_itu - 1 / g.real) / d_itu < 1e-9

print("\n=== 3. polarization (IEEE handedness, e^{jwt}, propagation +z) ===")
def pol_params(Ex, Ey):
    """Return axial ratio (>=1), tilt angle (deg, from x), handedness (IEEE) for wave along +z."""
    # Stokes parameters
    S0 = abs(Ex)**2 + abs(Ey)**2
    S1 = abs(Ex)**2 - abs(Ey)**2
    S2 = 2 * np.real(Ex * np.conj(Ey))
    S3 = 2 * np.imag(Ex * np.conj(Ey))    # sign chosen so S3>0 <=> IEEE RHCP for e^{jwt}, +z (checked by time trace)
    chi = 0.5 * np.arcsin(np.clip(S3 / S0, -1, 1))
    psi = 0.5 * np.arctan2(S2, S1)
    AR = np.inf if abs(np.tan(chi)) < 1e-15 else 1 / abs(np.tan(chi))
    hand = "linear" if abs(S3) < 1e-12 * S0 else ("RHCP/RH (IEEE)" if S3 > 0 else "LHCP/LH (IEEE)")
    return AR, np.degrees(psi), hand


def traced_rotation(Ex, Ey):
    """Numerically trace E(t) at z=0 and report rotation sense seen looking along +z (from behind)."""
    t = np.linspace(0, 1, 2001)
    ex = np.real(Ex * np.exp(1j * 2 * np.pi * t))
    ey = np.real(Ey * np.exp(1j * 2 * np.pi * t))
    # z-component of r x dr/dt: >0 means counter-clockwise in the xy-plane with z pointing toward viewer
    cross = np.mean(ex[:-1] * np.diff(ey) - ey[:-1] * np.diff(ex))
    # looking along +z (wave receding from viewer), the viewer sees the xy-plane from the -z side,
    # so a counter-clockwise (+z) rotation appears CLOCKWISE to them -> IEEE right-handed
    if abs(cross) < 1e-9:
        return "linear"
    return "clockwise seen from behind (IEEE RH)" if cross > 0 else "counter-clockwise seen from behind (IEEE LH)"


tests = {
    "Ex=1, Ey=-j (Ey lags 90)": (1, -1j),
    "Ex=1, Ey=+j (Ey leads 90)": (1, 1j),
    "Ex=1, Ey=1": (1, 1),
    "Ex=1, Ey=-0.5j": (1, -0.5j),
    "Ex=1, Ey=0.8 e^{-j60deg}": (1, 0.8 * np.exp(-1j * np.pi / 3)),
}
for name, (Ex, Ey) in tests.items():
    AR, tilt, hand = pol_params(Ex, Ey)
    ARdB = 20 * np.log10(AR) if np.isfinite(AR) else np.inf
    print(f"{name:28s} AR={AR:8.3f} ({ARdB:6.2f} dB) tilt={tilt:7.2f} deg  {hand:16s} | trace: {traced_rotation(Ex, Ey)}")
# consistency: Stokes handedness must agree with the time trace
for name, (Ex, Ey) in tests.items():
    _, _, hand = pol_params(Ex, Ey)
    tr = traced_rotation(Ex, Ey)
    if hand.startswith("RH"):
        assert "IEEE RH" in tr
    elif hand.startswith("LH"):
        assert "IEEE LH" in tr

# polarization mismatch between RHCP wave and linear antenna, and between AR-limited antennas
def pol_mismatch_dB(AR1_dB, AR2_dB, same_sense=True, dtheta_deg=0.0):
    """Polarization loss between two elliptical polarizations (standard formula, e.g. Balanis/ Milligan)."""
    r1 = 10 ** (AR1_dB / 20); r2 = 10 ** (AR2_dB / 20)
    if not same_sense:
        r2 = -r2
    th = np.radians(dtheta_deg)
    num = (1 + r1**2) * (1 + r2**2) + 4 * r1 * r2 + (1 - r1**2) * (1 - r2**2) * np.cos(2 * th)
    den = 2 * (1 + r1**2) * (1 + r2**2)
    return 10 * np.log10(num / den)
print(f"\nRHCP (0 dB AR) vs linear (inf AR): {pol_mismatch_dB(0, 60):.2f} dB")
print(f"RHCP 3 dB AR vs RHCP 3 dB AR, aligned: {pol_mismatch_dB(3, 3, True, 0):.3f} dB; crossed 90deg: {pol_mismatch_dB(3, 3, True, 90):.3f} dB")
print(f"RHCP 0 dB vs LHCP 0 dB: {pol_mismatch_dB(0, 0.0001, False):.1f} dB (cross-pol, -> -inf)")

print("\n=== 4. field strength from EIRP ===")
for P, G_dBi, r in ((2.0, 0.0, 1000), (2.0, 2.15, 1000), (1.0, 0.0, 10000), (2.0, 2.15, 30000)):
    EIRP = P * 10 ** (G_dBi / 10)
    S = EIRP / (4 * np.pi * r**2)
    E = np.sqrt(eta0 * S)
    print(f"P={P} W, G={G_dBi} dBi, r={r/1000:g} km: S={S:.3e} W/m^2, E_rms={E*1e3:.3f} mV/m "
          f"({20*np.log10(E/1e-6):.1f} dBuV/m), H={E/eta0*1e6:.3f} uA/m; sqrt(30 EIRP)/r = {np.sqrt(30*EIRP)/r*1e3:.3f} mV/m")
print("\nAll checks passed.")
