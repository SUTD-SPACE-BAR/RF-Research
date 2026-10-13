#!/usr/bin/env python3
"""
em_skin_depth.py — checks for kb/02-electromagnetics/skin-effect-conductor-loss-roughness.md

1. Skin depth and surface resistance table for Ag, Cu, Au, Al, Ni (CRC 293 K resistivities) and
   annealed-copper IACS, 1 MHz - 100 GHz; exact good-conductor formula vs full lossy-medium gamma.
2. Round wire internal impedance: exact Bessel solution vs DC and high-frequency asymptotes.
3. Two-wire proximity-effect factor.
4. Roughness correction factors: Hammerstad, Groiss, Huray (snowball), Cannonball-Huray.
5. Layered-conductor surface impedance: ENIG (Au / Ni-P / Cu), immersion silver, immersion tin,
   with notes on which microstrip faces are plated.
6. Microstrip loss orders of magnitude at 915 MHz on FR-4 (conductor vs dielectric).
7. Litz strand diameter guidance.
"""
import numpy as np
from scipy import special

c = 299_792_458.0
mu0 = 1.25663706127e-6
eps0 = 1 / (mu0 * c**2)
eta0 = mu0 * c

# resistivities in ohm*m at 293 K, CRC Handbook "Electrical resistivity of pure metals"
rho = {
    "Ag": 1.587e-8,
    "Cu": 1.678e-8,
    "Cu (IACS annealed std)": 1.7241e-8,
    "Au": 2.214e-8,
    "Al": 2.650e-8,
    "Ni (mu_r=1)": 6.93e-8,
}
freqs = [1e6, 10e6, 100e6, 433e6, 915e6, 1e9, 1.57542e9, 2.45e9, 5.8e9, 10e9, 24e9, 77e9, 100e9]


def delta(f, sigma, mur=1.0):
    return 1 / np.sqrt(np.pi * f * mu0 * mur * sigma)


def Rs(f, sigma, mur=1.0):
    return np.sqrt(np.pi * f * mu0 * mur / sigma)


print("=== 1. skin depth (um) ===")
hdr = "metal".ljust(24) + "".join(f"{(f/1e9 if f>=1e9 else f/1e6):>9.4g}{'G' if f>=1e9 else 'M'}" for f in freqs)
print(hdr)
for m, r in rho.items():
    s = 1 / r
    print(m.ljust(24) + "".join(f"{delta(f, s)*1e6:10.3f}" for f in freqs))
print("\nNi with mu_r = 100 (illustrative, below FMR):".ljust(24))
print("Ni (mu_r=100)".ljust(24) + "".join(f"{delta(f, 1/6.93e-8, 100)*1e6:10.3f}" for f in freqs))

print("\n=== 1b. surface resistance Rs (mOhm/sq) ===")
print(hdr)
for m, r in rho.items():
    s = 1 / r
    print(m.ljust(24) + "".join(f"{Rs(f, s)*1e3:10.3f}" for f in freqs))

# exact vs approximation: full gamma
for m in ("Cu", "Ni (mu_r=1)"):
    s = 1 / rho[m]
    for f in (1e6, 100e9):
        w = 2 * np.pi * f
        g = np.sqrt(1j * w * mu0 * (s + 1j * w * eps0))
        err = abs(1 / g.real - delta(f, s)) / delta(f, s)
        assert err < 1e-6, err
print("\ngood-conductor approximation vs exact gamma: error < 1e-6 for Cu/Ni at 1 MHz-100 GHz. OK")
print(f"Cu 433 MHz: delta = {delta(433e6, 1/rho['Cu'])*1e6:.3f} um (CRC pure) / "
      f"{delta(433e6, 1/rho['Cu (IACS annealed std)'])*1e6:.3f} um (IACS)")

# ---------- 2. round wire exact ----------
print("\n=== 2. round wire internal impedance (exact Bessel) ===")
def wire_Zint(f, a, sigma, mur=1.0):
    w = 2 * np.pi * f
    k = np.sqrt(-1j * w * mu0 * mur * sigma)       # J'' + J'/r + k^2 J = 0, e^{jwt}
    ka = k * a
    return k / (2 * np.pi * a * sigma) * special.jv(0, ka) / special.jv(1, ka)
a = 0.5e-3; s = 5.8e7
Rdc = 1 / (np.pi * a**2 * s)
print(f"Cu wire r = {a*1e3} mm (d = 1 mm, ~AWG18): Rdc = {Rdc*1e3:.3f} mOhm/m")
for f in (1e3, 10e3, 100e3, 1e6, 10e6, 100e6, 433e6, 1e9):
    Z = wire_Zint(f, a, s)
    d = delta(f, s)
    approx = Rs(f, s) / (2 * np.pi * a)                       # thin-skin asymptote
    approx2 = Rdc * (a / (2 * d) + 0.25)                      # improved asymptote
    print(f"  f={f:9.3e}: a/delta={a/d:8.2f}  Rac/Rdc(exact)={Z.real/Rdc:8.3f}  Rs/(2 pi a)/Rdc={approx/Rdc:8.3f}"
          f"  (a/2d+1/4)={approx2/Rdc:8.3f}  wLi/R={Z.imag/Z.real:6.3f}")

# ---------- 3. proximity effect ----------
print("\n=== 3. two-wire line proximity factor R/R_isolated = (D/2a)/sqrt((D/2a)^2-1) ===")
for ratio in (1.1, 1.25, 1.5, 2, 3, 5, 10):
    print(f"  D/2a = {ratio:5.2f}: factor {ratio/np.sqrt(ratio**2-1):.3f}")

# ---------- 4. roughness ----------
print("\n=== 4. roughness correction factors K = Rrough/Rsmooth for copper ===")
def K_hammerstad(f, rms, sigma=5.8e7):
    d = delta(f, sigma)
    return 1 + 2 / np.pi * np.arctan(1.4 * (rms / d)**2)
def K_groiss(f, rms, sigma=5.8e7):
    d = delta(f, sigma)
    return 1 + np.exp(-(d / (2 * rms))**1.6)
def K_huray(f, r, SR, sigma=5.8e7):
    """SR = N 4 pi r^2 / A_hex (Hall-Huray surface ratio)."""
    d = delta(f, sigma)
    return 1 + 1.5 * SR / (1 + d / r + d**2 / (2 * r**2))
def K_cannonball(f, Rz, sigma=5.8e7):
    r = 0.06 * Rz
    return K_huray(f, r, 4.887, sigma)   # RF fixed 8.33 -> SR = (8.33-1)*2/3 = 4.887

fr = [100e6, 433e6, 915e6, 2.45e9, 5.8e9, 10e9, 24e9, 50e9, 77e9]
print("f (GHz)                 " + "".join(f"{f/1e9:8.3f}" for f in fr))
print("delta Cu (um)           " + "".join(f"{delta(f,5.8e7)*1e6:8.3f}" for f in fr))
for rms in (0.3, 1.0, 2.0):
    print(f"Hammerstad rms={rms} um   " + "".join(f"{K_hammerstad(f, rms*1e-6):8.3f}" for f in fr))
for rms in (0.3, 1.0, 2.0):
    print(f"Groiss rms={rms} um       " + "".join(f"{K_groiss(f, rms*1e-6):8.3f}" for f in fr))
for r_, SR in ((0.5, 1.0), (0.5, 2.0), (0.5, 4.887)):
    print(f"Huray r={r_} SR={SR:5.3f}    " + "".join(f"{K_huray(f, r_*1e-6, SR):8.3f}" for f in fr))
for Rz in (2.0, 5.0, 8.0):
    print(f"Cannonball Rz={Rz} um     " + "".join(f"{K_cannonball(f, Rz*1e-6):8.3f}" for f in fr))
# Huray paper case: 79 spheres r=0.5um on hexagon of 'base' 9.4 um: try hex side 9.4/2 and 9.4 to show ambiguity
for side in (9.4e-6 / 2, 9.4e-6 / np.sqrt(3), 9.4e-6):
    Ahex = 3 * np.sqrt(3) / 2 * side**2
    SR = 79 * 4 * np.pi * (0.5e-6)**2 / Ahex
    print(f"  Huray 2010 example (79 x 0.5 um spheres) with hex side {side*1e6:.2f} um: A_hex={Ahex*1e12:.1f} um^2, SR={SR:.2f}, K_max={1+1.5*SR:.2f}")

# ---------- 5. layered conductor surface impedance ----------
print("\n=== 5. plated surfaces: surface resistance relative to smooth bare Cu ===")
def eta_metal(f, sigma, mur=1.0):
    w = 2 * np.pi * f
    return np.sqrt(1j * w * mu0 * mur / sigma)
def gamma_metal(f, sigma, mur=1.0):
    w = 2 * np.pi * f
    return np.sqrt(1j * w * mu0 * mur * sigma)
def Zs_layers(f, layers, sigma_base=5.8e7, mur_base=1.0):
    """layers from outermost (field side) to innermost: list of (sigma, mur, thickness). Base is semi-infinite."""
    Z = eta_metal(f, sigma_base, mur_base)
    for sigma, mur, t in reversed(layers):
        e = eta_metal(f, sigma, mur); g = gamma_metal(f, sigma, mur)
        th = np.tanh(g * t)
        Z = e * (Z + e * th) / (e + Z * th)
    return Z
sig_NiP = 1 / 60e-8        # mid-phos electroless Ni-P ~ 60 uOhm cm (medium confidence)
sig_Ni = 1 / 6.93e-8       # pure Ni (CRC)
sig_Au = 1 / 2.214e-8
sig_Ag = 1 / 1.587e-8
sig_Sn = 1 / 11.5e-8       # CRC Sn at 273 K ~ 11.5 uOhm cm
cases = {
    "ENIG: 0.08um Au / 5um NiP(60uOhmcm, mu_r 1) / Cu": [(sig_Au, 1, 0.08e-6), (sig_NiP, 1, 5e-6)],
    "ENIG w/ magnetic Ni: 0.08um Au / 5um Ni(7uOhmcm, mu_r 20) / Cu": [(sig_Au, 1, 0.08e-6), (sig_Ni, 20, 5e-6)],
    "ENEPIG thin-Ni: 0.05um Au/0.1um Pd/0.1um NiP / Cu": [(sig_Au, 1, 0.05e-6), (1/10.54e-8, 1, 0.1e-6), (sig_NiP, 1, 0.1e-6)],
    "Immersion Ag 0.2 um / Cu": [(sig_Ag, 1, 0.2e-6)],
    "Immersion Sn 1 um / Cu": [(sig_Sn, 1, 1e-6)],
    "Bulk NiP (for reference)": [(sig_NiP, 1, 1.0)],
}
fr2 = [100e6, 433e6, 915e6, 2.45e9, 5.8e9, 10e9, 25e9, 50e9]
print("f (GHz)".ljust(64) + "".join(f"{f/1e9:7.3f}" for f in fr2))
for name, lay in cases.items():
    ratios = [Zs_layers(f, lay).real / Rs(f, 5.8e7) for f in fr2]
    print(name.ljust(64) + "".join(f"{r:7.2f}" for r in ratios))
print("delta NiP (um)".ljust(64) + "".join(f"{delta(f, sig_NiP)*1e6:7.2f}" for f in fr2))

# ---------- 6. microstrip order of magnitude ----------
print("\n=== 6. 50-ohm microstrip, 1.6 mm FR-4 (er 4.4, tand 0.02), w ~ 3.0 mm, 915 MHz ===")
f = 915e6; w = 3.0e-3; Z0 = 50.0; er = 4.4; td = 0.02
eeff = (er + 1) / 2 + (er - 1) / 2 / np.sqrt(1 + 12 * 1.6e-3 / w)
alpha_c = Rs(f, 5.8e7) / (Z0 * w)                 # Pozar approx (strip + ground ~ Rs/(Z0 w))
lam0 = c / f
alpha_d = (2 * np.pi / lam0) * er * (eeff - 1) * td / (2 * np.sqrt(eeff) * (er - 1))
print(f"  eps_eff = {eeff:.3f}; alpha_c ~ {alpha_c*8.686:.3f} dB/m; alpha_d = {alpha_d*8.686:.3f} dB/m "
      f"(conductor x roughness K~1.3 -> {alpha_c*8.686*1.3:.3f} dB/m)")

# ---------- 7. Litz ----------
print("\n=== 7. Litz: strand diameter ~ delta rule ===")
for f in (20e3, 100e3, 500e3, 1e6, 3e6, 10e6):
    d = delta(f, 5.8e7)
    print(f"  f={f/1e3:7.0f} kHz: delta_Cu = {d*1e6:6.1f} um -> strand dia <~ {d*1e6:6.1f} um "
          f"(AWG ~ {(-39*np.log(d*1e3/0.127)/np.log(92) + 36):.0f})")
print("\nAll checks passed.")
