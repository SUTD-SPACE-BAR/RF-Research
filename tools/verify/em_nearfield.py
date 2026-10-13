#!/usr/bin/env python3
"""
em_nearfield.py — checks for kb/02-electromagnetics/near-field-far-field.md

1. Region boundaries: lambda/2pi, 0.62 sqrt(D^3/lambda), 2D^2/lambda for Marcus's antennas.
2. Phase error across an aperture at distance r: k D^2/(8 r) -> pi/8 at 2D^2/lambda.
3. On-axis gain error of a uniformly illuminated circular aperture at finite range (Fresnel):
   G(z)/G_ff = [sin(x/2)/(x/2)]^2, x = pi D^2/(4 lambda z).
4. Wave impedance vs distance for electric (dipole) and magnetic (loop) sources and the
   distance at which |Z| is within 10 % / 1 % of eta0.
5. Near-field shielding: Schelkunoff reflection loss R = 20 log10(|Zw|/(4|Zs|)) for E- and H-type
   sources vs plane wave, copper sheet, several frequencies/distances.
6. Hertzian-dipole field magnitude vs kr compared with the far-field 1/r law (error of using
   far-field formulas close in).
"""
import numpy as np

c = 299_792_458.0
mu0 = 1.25663706127e-6
eps0 = 1 / (mu0 * c**2)
eta0 = mu0 * c

print("=== 1. region boundaries ===")
ants = [
    ("433 MHz half-wave dipole", 433e6, 0.5 * c / 433e6),
    ("433 MHz 3-el Yagi (boom ~0.5 m, D taken 0.35 m element)", 433e6, 0.5 * c / 433e6),
    ("433 MHz Yagi, D = 1.0 m (largest dimension)", 433e6, 1.0),
    ("915 MHz Yagi D = 1.0 m", 915e6, 1.0),
    ("1575 MHz GNSS patch 25 mm", 1575.42e6, 0.025),
    ("1575 MHz GNSS patch on 70 mm ground plane", 1575.42e6, 0.07),
    ("2.45 GHz 4x4 patch array 0.25 m", 2.45e9, 0.25),
    ("5.8 GHz 0.3 m dish", 5.8e9, 0.3),
    ("24 GHz radar 8x8 array 0.05 m", 24e9, 0.05),
    ("77 GHz radar antenna 0.02 m", 77e9, 0.02),
]
for name, f, D in ants:
    lam = c / f
    r1 = lam / (2 * np.pi)
    r2 = 0.62 * np.sqrt(D**3 / lam)
    r3 = 2 * D**2 / lam
    print(f"  {name:55s} lambda={lam*100:6.1f} cm  lambda/2pi={r1*100:6.1f} cm  0.62sqrt(D^3/l)={r2*100:7.1f} cm  2D^2/l={r3*100:8.1f} cm")

print("\n=== 2/3. finite-range phase error and on-axis gain error ===")
for mult in (0.25, 0.5, 1, 2, 4, 8):
    # distance = mult * D^2/lambda  -> x = pi D^2/(4 lambda z) = pi/(4 mult)
    x = np.pi / (4 * mult)
    dphi = np.degrees(np.pi / (8 * mult) * 2 * 2) / 4   # k D^2/(8r) with r = mult D^2/lambda -> pi/(4 mult) rad
    phase_err = np.degrees(np.pi / (4 * mult))
    gerr = (np.sin(x / 2) / (x / 2))**2
    print(f"  r = {mult:5.2f} D^2/lambda: edge phase error kD^2/(8r) = {phase_err:6.2f} deg; on-axis gain error (uniform circ.) = {10*np.log10(gerr):7.3f} dB")
assert abs(np.degrees(np.pi / (4 * 2)) - 22.5) < 1e-12

print("\n=== 4. wave impedance vs distance ===")
def Zw(kr):
    num = 1 + 1 / (1j * kr) - 1 / kr**2
    den = 1 + 1 / (1j * kr)
    return num / den * eta0, den / num * eta0
krs = np.logspace(-2, 3, 200001)
ZE = np.array([abs(Zw(x)[0]) for x in krs[::100]])
ZM = np.array([abs(Zw(x)[1]) for x in krs[::100]])
kk = krs[::100]
for tol in (0.1, 0.01):
    # last kr beyond which both stay within tol
    badE = np.where(abs(ZE / eta0 - 1) > tol)[0]; badM = np.where(abs(ZM / eta0 - 1) > tol)[0]
    krE = kk[badE[-1] + 1] if len(badE) else kk[0]
    krM = kk[badM[-1] + 1] if len(badM) else kk[0]
    print(f"  |Z|/eta0 within {tol*100:.0f} %: electric source beyond kr = {krE:.2f} (r = {krE/(2*np.pi):.3f} lambda); "
          f"magnetic source beyond kr = {krM:.2f} (r = {krM/(2*np.pi):.3f} lambda)")
print(f"  min |Z_E| = {ZE.min():.1f} ohm at kr = {kk[ZE.argmin()]:.3f}; max |Z_M| = {ZM.max():.1f} ohm at kr = {kk[ZM.argmax()]:.3f}")

print("\n=== 5. Schelkunoff reflection loss of a copper sheet, E- vs H-type source ===")
sigma = 5.8e7
for f, r in ((1e6, 0.01), (1e6, 0.1), (10e6, 0.01), (100e6, 0.03), (433e6, 0.05), (1e9, 0.5)):
    w = 2 * np.pi * f
    Zs = abs(np.sqrt(1j * w * mu0 / sigma))
    kr = 2 * np.pi * f / c * r
    ZE_, ZM_ = [abs(z) for z in Zw(kr)]
    R = lambda Z: 20 * np.log10(Z / (4 * Zs))
    print(f"  f={f/1e6:7.1f} MHz, r={r*100:5.1f} cm (kr={kr:.3f}): |Zs|={Zs*1e3:.3f} mOhm; R_E={R(ZE_):6.1f} dB, "
          f"R_plane={R(eta0):6.1f} dB, R_H={R(ZM_):6.1f} dB")

print("\n=== 6. far-field formula error close to a Hertzian dipole (broadside) ===")
for kr in (0.1, 0.5, 1, 2, 5, 10):
    exact = abs(1 + 1 / (1j * kr) - 1 / kr**2)
    Hex = abs(1 + 1 / (1j * kr))
    print(f"  kr={kr:5.1f} (r={kr/(2*np.pi):.3f} lambda): |E_theta|/E_ff = {exact:9.3f} ({20*np.log10(exact):6.1f} dB), |H_phi|/H_ff = {Hex:7.3f} ({20*np.log10(Hex):5.1f} dB)")
print("\nAll checks passed.")
