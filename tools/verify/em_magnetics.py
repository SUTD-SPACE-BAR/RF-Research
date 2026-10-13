#!/usr/bin/env python3
"""
em_magnetics.py — checks for kb/02-electromagnetics/magnetic-materials-permeability.md

1. Snoek's limit (mu_i - 1) f_r = (2/3)(gamma/2pi) mu0 Ms  (SI), for NiZn (Fair-Rite 43/61 class),
   MnZn, YIG; predicted gyromagnetic roll-off frequency for given mu_i.
2. Single-pole (Debye-like relaxation) permeability model mu(f) = 1 + (mu_i - 1)/(1 + j f/f_r) and a
   damped-resonance (Lorentz) model; the resulting ferrite-bead impedance Z = j w L0 mu(f).
3. Polder tensor of a magnetised ferrite: mu, kappa, circular permeabilities mu+-,
   FMR frequency (Kittel, infinite medium and thin film / sphere), Faraday rotation.
4. Dimensional resonance in MnZn ferrite (high eps and mu -> short internal wavelength).
"""
import numpy as np

c = 299_792_458.0
mu0 = 1.25663706127e-6
eps0 = 1 / (mu0 * c**2)
gamma_2pi = 28.0249514242e9   # Hz/T, electron g ~ 2.0023 (CODATA gamma_e/2pi = 28.0249514242 GHz/T)
gamma = 2 * np.pi * gamma_2pi

print("=== 1. Snoek's limit ===")
mats = {
    "NiZn (4piMs ~ 3500 G, e.g. Fair-Rite 43 B@10Oe)": 0.35,
    "NiZn higher-Ms (5000 G)": 0.50,
    "MnZn (4piMs ~ 4800 G)": 0.48,
    "YIG garnet (4piMs ~ 1780 G)": 0.178,
}
for name, B in mats.items():
    snoek = 2 / 3 * gamma_2pi * B       # Hz, = (mu_i - 1) f_r
    print(f"  {name:50s} (mu_i-1) f_r = {snoek/1e9:6.2f} GHz")
    for mui in (40, 125, 800, 1500, 5000):
        print(f"      mu_i = {mui:5d} -> f_r <~ {snoek/(mui-1)/1e6:9.2f} MHz")
# Gaussian check: (2/3) * 2.80 MHz/Oe * 4piMs[G]
print(f"  Gaussian form check: (2/3)*2.8025 MHz/Oe*3500 G = {2/3*2.8025e6*3500/1e9:.3f} GHz")
# equivalently gamma*mu0Ms/(3 pi)
print(f"  gamma*mu0Ms/(3pi) for 0.35 T = {gamma*0.35/(3*np.pi)/1e9:.3f} GHz (same thing)")

print("\n=== 2. ferrite bead model ===")
def mu_relax(f, mui, fr):
    return 1 + (mui - 1) / (1 + 1j * f / fr)
def mu_lorentz(f, mui, fr, damping=0.5):
    x = f / fr
    return 1 + (mui - 1) / (1 - x**2 + 1j * damping * x)
# toroid/bead geometry: L0 = mu0 * h/(2pi) ln(OD/ID) per turn
OD, ID, h = 3.5e-3, 1.3e-3, 6.0e-3    # small bead-on-lead size (illustrative)
L0 = mu0 * h / (2 * np.pi) * np.log(OD / ID)
print(f"  bead geometry OD {OD*1e3} ID {ID*1e3} h {h*1e3} mm, 1 turn: L0 (air) = {L0*1e9:.3f} nH")
mui, fr = 800, 8e6
for f in (1e6, 5e6, 10e6, 30e6, 100e6, 300e6, 1e9):
    for model, mu in (("relax", mu_relax(f, mui, fr)), ("lorentz", mu_lorentz(f, mui, fr))):
        Z = 1j * 2 * np.pi * f * L0 * mu     # Z = j w L0 (mu' - j mu'') = w L0 mu'' + j w L0 mu'
        print(f"  f={f/1e6:7.1f} MHz {model:7s}: mu'={mu.real:8.2f} mu''={-mu.imag:8.2f}  "
              f"Z = {Z.real:6.1f} + j{Z.imag:6.1f} ohm |Z|={abs(Z):6.1f}")
# check causality sense: mu'' >= 0 for passive material in e^{jwt} convention (mu = mu' - j mu'')
assert all(-mu_relax(f, 800, 8e6).imag >= 0 for f in np.logspace(4, 10, 50))

print("\n=== 3. Polder tensor, FMR, Faraday rotation ===")
def polder(f, H0, Ms, alpha=0.0):
    """H0 internal bias field (A/m), Ms (A/m); returns mu, kappa (relative) with Gilbert-type damping"""
    w = 2 * np.pi * f
    w0 = gamma * mu0 * H0 + 1j * alpha * w
    wm = gamma * mu0 * Ms
    mu = 1 + w0 * wm / (w0**2 - w**2)
    kappa = w * wm / (w0**2 - w**2)
    return mu, kappa
Ms = 0.178 / mu0   # YIG
for B0 in (0.05, 0.1, 0.2):
    H0 = B0 / mu0
    f0 = gamma_2pi * B0
    print(f"  YIG, internal bias mu0H0 = {B0} T: FMR (infinite medium) f0 = {f0/1e9:.2f} GHz; "
          f"sphere (Kittel, H0 applied) same; thin film in-plane: {gamma_2pi*np.sqrt(B0*(B0+0.178))/1e9:.2f} GHz")
f = 10e9; B0 = 0.2
mu, kap = polder(f, B0 / mu0, Ms)
mu_p, mu_m = mu + kap, mu - kap
print(f"  at 10 GHz, 0.2 T, YIG: mu = {mu.real:.3f}, kappa = {kap.real:.3f}, mu+ = {mu_p.real:.3f}, mu- = {mu_m.real:.3f}")
# check mu+- = 1 + wm/(w0 -+ w)
w = 2 * np.pi * f; w0 = gamma * B0; wm = gamma * 0.178
assert abs(mu_p - (1 + wm / (w0 - w))) < 1e-9 and abs(mu_m - (1 + wm / (w0 + w))) < 1e-9
# Faraday rotation per length for a wave along bias in ferrite with eps_r 15 (YIG)
er = 15
beta_p = w * np.sqrt(mu0 * mu_p.real * eps0 * er + 0j)
beta_m = w * np.sqrt(mu0 * mu_m.real * eps0 * er + 0j)
rot = (beta_p - beta_m) / 2
print(f"  Faraday rotation (eps_r 15): {np.degrees(rot.real)/100:.2f} deg/cm (beta+ {beta_p:.1f}, beta- {beta_m:.1f} rad/m); "
      f"note mu+ < 0 -> + wave evanescent" if mu_p.real < 0 else f"  Faraday rotation: {np.degrees(rot.real)/100:.2f} deg/cm")
# below resonance example: 10 GHz, bias 0.1 T -> w > w0 (above resonance operation)
for B0 in (0.05, 0.1, 0.5):
    mu, kap = polder(10e9, B0 / mu0, Ms)
    print(f"  10 GHz, mu0H0 {B0} T: mu+ = {(mu+kap).real:.3f}, mu- = {(mu-kap).real:.3f}")

print("\n=== 4. dimensional resonance in MnZn ===")
for mu_r, eps_r in ((2000, 1e5), (2000, 1e4), (5000, 5e4)):
    for f in (0.5e6, 1e6, 2e6):
        lam = c / f / np.sqrt(mu_r * eps_r)
        print(f"  MnZn mu {mu_r}, eps {eps_r:.0e}, f={f/1e6} MHz: internal wavelength = {lam*100:.2f} cm; half-wave = {lam/2*100:.2f} cm")
print("\nAll checks passed.")
