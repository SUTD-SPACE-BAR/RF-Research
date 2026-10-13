#!/usr/bin/env python3
"""
W5-S4 verification for kb/04-real-components-hf/capacitors-at-rf-mlcc.md (#capacitor-families-beyond-mlcc-...):
  1. |Z|(f), ESR(f) and SRF of representative bulk and RF capacitor families with a
     series model  Z = ESR(f) + j w ESL + 1/(j w C),  ESR(f) = R_metal(f) + D/(w C)
     (D = dielectric loss tangent, R_metal = electrode/electrolyte/lead resistance, skin-effect where relevant).
  2. Loss split in film capacitors: dielectric (D/wC, falls as 1/f) vs conductor (leads/terminations,
     rises as sqrt f) -> crossover frequency for polypropylene vs polyester, and the "skin effect in film
     capacitors" exam statement.
  3. Electrolytic in the cold: impedance-ratio spec and what it does to a supply's bulk capacitor.
  4. Q at RF for mica / C0G / film.
Representative values (see page for sources): NIC NACZ 100 uF 16 V (Z <= 0.44 ohm @100 kHz, tan d 0.16 @120 Hz,
Z(-40)/Z(20) <= 2 @120 Hz); KEMET T495D 100 uF (ESR 100 mOhm, part-number code), T520D 100 uF (40 mOhm);
WIMA MKP tan d <= 5e-4, MKT <= 8e-3 at 1 kHz. ESL values and mica tan d are typical-class assumptions.
Run: python3 tools/verify/s4_cap_families.py
"""
import numpy as np

TP = 2 * np.pi
MU0 = 1.25663706127e-6
SIG_CU = 5.80e7

def lead_R(f, length=2 * 10e-3, d=0.6e-3):
    """resistance of round copper leads (total length) with skin effect (simple asymptote blend)."""
    rdc = length / (SIG_CU * np.pi * d**2 / 4)
    delta = 1 / np.sqrt(np.pi * f * MU0 * SIG_CU)
    rac = length / (SIG_CU * np.pi * d * delta)
    return np.sqrt(rdc**2 + rac**2)

parts = {
    # name: (C [F], ESL [H], Rmetal(f) callable, D dielectric tan d)
    "Al electrolytic 100uF/16V SMD (NACZ class)": (100e-6, 4e-9, lambda f: 0.30 + 0 * f, 0.137),
    "Ta MnO2 100uF D-case (T495 class, 100 mOhm)": (100e-6, 2.5e-9, lambda f: 0.10 + 0 * f, 0.06),
    "Ta polymer 100uF D-case (T520 class, 40 mOhm)": (100e-6, 2.5e-9, lambda f: 0.040 + 0 * f, 0.06),
    "X5R MLCC 22uF 1206 (~10uF left at 5 V)": (10e-6, 1.2e-9, lambda f: 0.003 + 0 * f, 0.05),
    "PP film 100nF leaded (MKP class)": (100e-9, 6e-9, lambda f: 0.005 + lead_R(f), 5e-4),
    "PET film 100nF leaded (MKT class)": (100e-9, 6e-9, lambda f: 0.005 + lead_R(f), 8e-3),
    "Silver mica 100pF leaded": (100e-12, 5e-9, lambda f: 0.02 + lead_R(f), 3e-4),
    "C0G MLCC 100pF 0402 (mounted)": (100e-12, 0.4e-9, lambda f: 0.1 * np.sqrt(f / 1e9) + 0.02, 1e-4),
}

def Z(part, f):
    C, L, Rm, D = part
    w = TP * f
    esr = Rm(f) + D / (w * C)
    return esr + 1j * (w * L - 1 / (w * C)), esr

print("=== 1. |Z| (ohm) vs frequency, and SRF ===")
freqs = [120, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 433.92e6]
print(f"{'part':48s}" + "".join(f"{(f/1e6 if f>=1e6 else f/1e3):>9.3g}{'M' if f>=1e6 else 'k'}" for f in freqs) + "    SRF")
for name, p in parts.items():
    row = "".join(f"{abs(Z(p, f)[0]):10.3g}" for f in freqs)
    srf = 1 / (TP * np.sqrt(p[0] * p[1]))
    print(f"{name:48s}{row}   {srf/1e6:8.3g} MHz")
print("(columns: 120 Hz, 1 kHz, 10 kHz, 100 kHz, 1 MHz, 10 MHz, 100 MHz, 433.92 MHz)")
print("check NACZ: |Z|(100 kHz) model vs datasheet max 0.44 ohm:",
      f"{abs(Z(parts['Al electrolytic 100uF/16V SMD (NACZ class)'], 1e5)[0]):.3f}",
      "; tan d at 120 Hz model:", f"{Z(parts['Al electrolytic 100uF/16V SMD (NACZ class)'], 120)[1]*TP*120*100e-6:.3f} (spec 0.16)")
print("\nminimum |Z| = ESR at SRF; above SRF every part is ESL: 4 nH -> "
      f"{TP*433.92e6*4e-9:.1f} ohm at 433.92 MHz, 2.5 nH -> {TP*433.92e6*2.5e-9:.1f}, 1.2 nH -> {TP*433.92e6*1.2e-9:.1f}, 0.4 nH -> {TP*433.92e6*0.4e-9:.2f} ohm")

print("\n=== 2. Film-capacitor loss split: dielectric D/(wC) vs conductor (leads + metallisation) ===")
for name, D in (("PP (tan d 5e-4)", 5e-4), ("PET (tan d 8e-3)", 8e-3), ("PP 1 nF", 5e-4)):
    C = 1e-9 if "1 nF" in name else 100e-9
    fs = np.logspace(3, 9, 6001)
    rd = D / (TP * fs * C)
    rc = 0.005 + lead_R(fs)
    i = np.argmin(np.abs(rd - rc))
    print(f"{name:18s} C {C*1e9:5.0f} nF: crossover {fs[i]/1e6:8.3f} MHz (ESR there {2*rc[i]*1e3:6.1f} mOhm);"
          f" at 10 MHz dielectric {D/(TP*1e7*C)*1e3:7.2f} mOhm vs conductor {(0.005+lead_R(1e7))*1e3:6.2f} mOhm")
for f in (1e6, 10e6, 100e6):
    d = 1 / np.sqrt(np.pi * f * MU0 * SIG_CU)
    dal = 1 / np.sqrt(np.pi * f * MU0 * 3.5e7)
    print(f"skin depth at {f/1e6:5.0f} MHz: Cu {d*1e6:6.1f} um (0.6 mm lead -> R_ac/R_dc {lead_R(f)/lead_R(1.0):5.1f}),"
          f" Al {dal*1e6:6.1f} um vs metallisation 0.02-0.05 um and film-foil 5-9 um")

print("\n=== 3. Electrolytic in the cold ===")
C, L, Rm, D = parts["Al electrolytic 100uF/16V SMD (NACZ class)"]
for ratio in (1, 2, 3, 10):
    esr100k = 0.30 * ratio
    print(f"ESR x{ratio:<3d} (100 kHz {esr100k:.2f} ohm): a 1 A load step through ESR -> {esr100k*1.0:.2f} V dip")
print("datasheet (NACZ 16 V): Z(-40)/Z(+20) <= 2 at 120 Hz; the 100 kHz ESR ratio is usually larger (check curves)")

print("\n=== 4. Q at RF (Q = |X|/ESR) ===")
for name in ("Silver mica 100pF leaded", "C0G MLCC 100pF 0402 (mounted)", "PP film 100nF leaded (MKP class)"):
    p = parts[name]
    out = []
    fl = (1e4, 1e5, 1e6, 3e6) if "film" in name else (1e6, 7e6, 30e6, 100e6)
    for f in fl:
        z, esr = Z(p, f)
        out.append(f"{f/1e6:6.2f} MHz Q {abs(z.imag)/esr:8.0f}")
    print(f"{name:34s}: " + "; ".join(out))
print("(Q is meaningless near SRF, where X -> 0; mica tan d 3e-4 and C0G 1e-4 are assumed typical values)")
