#!/usr/bin/env python3
"""
W5-S4 verification for everyday-EM folklore (G-02-02):
  1. Thin metal film transmission: sheet law T = 2/(2 + eta0/R_sq) vs exact conducting-slab formula.
  2. R_sq -> shielding table (space blanket, low-e glass, ITO, conductive paints, kitchen foil).
  3. Drude metals (Au, Ag; Ordal et al. 1983 parameters): conductivity, skin depth and the
     kinetic-inductance ratio from RF to optical -> why antennas still work at optical frequencies
     but scale differently.
  4. Magnets: electron gyrofrequency in 0.1-1 T; copper magnetoresistance estimate (mu_e B)^2.
  5. Dental fillings: AM broadcast field strength near a 50 kW station and open-circuit pick-up.
Pages: kb/02-electromagnetics/boundary-conditions-reflection-refraction.md (thin films, optical),
       kb/02-electromagnetics/skin-effect-conductor-loss-roughness.md (thin films, optical Drude),
       kb/02-electromagnetics/magnetic-materials-permeability.md (magnets).
Run: python3 tools/verify/s4_thin_film.py
"""
import numpy as np

MU0 = 1.25663706127e-6
EPS0 = 8.8541878188e-12
C0 = 299792458.0
ETA0 = np.sqrt(MU0 / EPS0)
TP = 2 * np.pi
print(f"eta0 = {ETA0:.2f} ohm")


def slab_T(f, sigma, t, eps_r=1.0):
    """Exact normal-incidence field transmission of a conducting slab in air (e^{jwt})."""
    w = TP * f
    eps = EPS0 * eps_r - 1j * sigma / w
    k = w * np.sqrt(MU0 * eps)
    if k.imag > 0:
        k = -k
    eta = np.sqrt(MU0 / eps)
    return 1 / (np.cos(k * t) + 0.5j * (eta / ETA0 + ETA0 / eta) * np.sin(k * t))


def sheet_T(Rsq):
    return 2 / (2 + ETA0 / Rsq)


def skin(f, sigma, mur=1.0):
    return 1 / np.sqrt(np.pi * f * MU0 * mur * sigma)


print("\n=== 1. Sheet law vs exact slab, aluminium (sigma 3.5e7 S/m bulk) and copper (5.80e7) ===")
for name, sig in (("Al", 3.5e7), ("Cu", 5.80e7)):
    for f in (433.92e6, 2.45e9):
        d = skin(f, sig)
        print(f"{name} at {f/1e6:7.2f} MHz: skin depth {d*1e6:.2f} um")
        for t in (10e-9, 40e-9, 100e-9, 1e-6, 3e-6, 10e-6, 16e-6):
            Te = abs(slab_T(f, sig, t))
            Ts = abs(sheet_T(1 / (sig * t)))
            print(f"   t = {t*1e6:7.3f} um (t/delta {t/d:6.3f}): exact {20*np.log10(Te):8.1f} dB, sheet law {20*np.log10(Ts):8.1f} dB")

print("\n=== 2. Sheet resistance -> transmission (frequency independent while t << delta, t << lambda) ===")
cases = [("conductive Ag EMI paint, 25 um (~0.02 ohm/sq)", 0.02),
         ("conductive Cu/Ni EMI paint (~0.1-1 ohm/sq)", 0.3),
         ("space blanket / aluminised PET, ~30-50 nm Al (thin-film sigma ~ half bulk) ~1.5 ohm/sq", 1.5),
         ("low-e window coating (silver stack) ~3-10 ohm/sq", 5.0),
         ("ITO touch/heater glass ~10-100 ohm/sq", 30.0),
         ("antistatic coating ~1e6 ohm/sq", 1e6),
         ("decorative metallic-flake car paint (flakes isolated in binder; effectively > 1e6 ohm/sq at DC)", 1e7)]
for name, R in cases:
    T = sheet_T(R)
    print(f"R_sq {R:10.3g} ohm/sq: transmission {20*np.log10(abs(T)):7.1f} dB  ({name})")
print("rule: SE = 20 log10(1 + eta0/(2 R_sq)); 1 ohm/sq -> "
      f"{20*np.log10(1+ETA0/2):.1f} dB, 10 -> {20*np.log10(1+ETA0/20):.1f} dB, 100 -> {20*np.log10(1+ETA0/200):.1f} dB")

print("\n=== 3. Drude metals from RF to optical (Ordal 1983: Au wp 7.28e4 cm^-1, wt 215 cm^-1; Ag 7.25e4, 145) ===")
def drude(nu_p_cm, nu_t_cm):
    wp = TP * C0 * 100 * nu_p_cm
    g = TP * C0 * 100 * nu_t_cm
    return wp, g
for name, (npc, ntc) in (("Au", (7.28e4, 215.0)), ("Ag", (7.25e4, 145.0))):
    wp, g = drude(npc, ntc)
    sdc = EPS0 * wp**2 / g
    print(f"{name}: wp = {wp:.3e} rad/s ({wp/TP/1e12:.0f} THz, lambda_p {TP*C0/wp*1e9:.0f} nm), gamma = {g:.3e} 1/s, "
          f"sigma_DC = {sdc:.3e} S/m, c/wp = {C0/wp*1e9:.1f} nm")
    for lab, f in (("433 MHz", 433.92e6), ("10 GHz", 10e9), ("1 THz", 1e12), ("10 um (30 THz)", 30e12),
                   ("1550 nm", C0 / 1550e-9), ("600 nm", C0 / 600e-9)):
        w = TP * f
        sig = EPS0 * wp**2 / (g + 1j * w)
        eps = 1 - wp**2 / (w * (w - 1j * g))
        n = np.sqrt(eps)
        if n.imag > 0:
            n = np.conj(n)
        dE = C0 / (w * abs(n.imag))          # field 1/e depth
        ratio = w / g                         # kinetic reactance / resistance  (X_k/R = w/gamma)
        print(f"   {lab:15s}: sigma = {sig.real:9.3e} {sig.imag:+9.3e}j S/m, |eps'| {abs(eps.real):9.3e}, "
              f"field depth {dE*1e9:9.1f} nm, wL_kin/R = {ratio:8.3g}")

print("\n=== 4. Magnets ===")
for B in (0.1, 0.5, 1.0):
    print(f"B = {B} T: electron gyrofrequency eB/(2 pi m) = {1.602176634e-19*B/(TP*9.1093837e-31)/1e9:.2f} GHz")
mu_e_cu = 4.3e-3  # m^2/Vs, room-temperature Cu electron mobility (order of magnitude)
for B in (0.1, 0.5):
    print(f"Cu magnetoresistance order (mu_e B)^2 at {B} T: {(mu_e_cu*B)**2:.1e}")
print("43 ferrite B at 10 Oe = 0.35 T: a NdFeB surface field 0.3-0.5 T drives it near saturation (mu collapses)")
fe = 1.602176634e-19 * 50e-6 / (TP * 9.1093837e-31)
print(f"Earth field 50 uT: ionospheric electron gyrofrequency {fe/1e6:.2f} MHz")

print("\n=== 5. Dental fillings near an AM broadcast station ===")
for P, d in ((50e3, 1000.0), (50e3, 300.0), (10e3, 1000.0), (50e3, 10e3)):
    E = np.sqrt(30 * P * 3.28) / d   # short monopole over perfect ground: directivity 3.28 (5.16 dBi)
    print(f"P {P/1e3:.0f} kW, d {d/1e3:.1f} km: E = {E:.2f} V/m (-> {E*0.1:.3f} V open-circuit on a 0.1 m effective height)")
print("compare: an AM station's city-grade service contour is of order 5 mV/m (FCC principal-community contour; from knowledge)")
print(f"ratio 2.22 V/m : 5 mV/m = {20*np.log10(2.22/5e-3):.0f} dB")
