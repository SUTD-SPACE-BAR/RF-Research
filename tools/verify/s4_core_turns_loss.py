#!/usr/bin/env python3
"""
W5-S4 verification: iron-powder vs ferrite cores, A_L -> turns, gapped cores, EFHW 49:1 transformer
loss/heating and compensation capacitor, and a 433 MHz coax common-mode choke.

Pages: kb/04-real-components-hf/ferrites-and-beads.md (#iron-powder-vs-ferrite-cores-...)
       kb/02-electromagnetics/magnetic-materials-permeability.md (#level-2--powdered-iron-...)

Data (read from tools/verify/data/, downloaded 2026-10-13):
  fairrite_mu_{31,43,52,61}.csv   Fair-Rite complex permeability mu_s', mu_s'' vs f (18/10/6 mm toroid, 25 C)
  fairrite_61_Pv_vs_B_25C.csv     Fair-Rite 61 large-signal core loss fits Pv = k * B[mT]^n (mW/cm^3)
Datasheet constants typed in below (Fair-Rite material/toroid pages; Micrometals 2019 RF catalogue and
T-core datasheets).  Run: python3 tools/verify/s4_core_turns_loss.py
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MU0 = 1.25663706127e-6
TP = 2 * np.pi


def load_mu(mix):
    a = np.loadtxt(os.path.join(HERE, "data", f"fairrite_mu_{mix}.csv"), delimiter=",", comments="#", skiprows=2)
    return a


MU = {m: load_mu(m) for m in ("31", "43", "52", "61")}


def mu_at(mix, f):
    a = MU[mix]
    lf = np.log10(a[:, 0])
    return np.interp(np.log10(f), lf, a[:, 1]), np.interp(np.log10(f), lf, a[:, 2])


# ---------------------------------------------------------------- 1. mix table
print("=== 1. Mix data (datasheets) and complex permeability at the bands we use (Fair-Rite CSV) ===")
fr = {  # mix: (type, mu_i, tempco %/C 20-70C, Tc C, rho ohm-cm)
    "31": ("MnZn", 1500, 1.3, ">130", "3e3"), "43": ("NiZn", 800, 1.25, ">130", "1e5"),
    "52": ("NiZn", 250, 0.8, ">250", "1e9"), "61": ("NiZn", 125, 0.10, ">300", "1e8")}
mm = {  # Micrometals carbonyl iron: (mu, tempco +ppm/C, max f MHz, colour)
    "-2": (10, 95, 45, "red"), "-6": (8.5, 35, 55, "yellow"), "-10": (6, 150, 83, "black"),
    "-17": (4, 50, 170, "blue/yellow")}
for k, v in fr.items():
    print(f"Fair-Rite {k}: {v[0]} mu_i {v[1]}, tempco {v[2]} %/C, Tc {v[3]} C, rho {v[4]} ohm-cm")
for k, v in mm.items():
    print(f"Micrometals {k}: mu {v[0]}, tempco +{v[1]} ppm/C, max f {v[2]} MHz, {v[3]}")
bands = [1.8e6, 3.6e6, 7.1e6, 14.2e6, 28.5e6, 100e6, 433.92e6, 915e6]
print("f (MHz)   " + "   ".join(f"{m}: mu' / mu'' (Q)      " for m in MU))
for f in bands:
    row = []
    for m in MU:
        a, b = mu_at(m, f)
        q = a / b if b > 0 else np.inf
        row.append(f"{a:7.1f} / {b:6.1f} ({q:6.2f})")
    print(f"{f/1e6:7.2f}  " + "  ".join(row))

# ---------------------------------------------------------------- 2. iron-powder Q from the loss formula
print("\n=== 2. Mix-2 / mix-6 core Q from the Micrometals eddy-current term d*B^2*f^2 ===")
# P[mW/cm^3] = f/(a/B^3 + b/B^2.3 + c/B^1.65) + d*B^2*f^2  (B in gauss, f in Hz)
# eddy term: p[W/m^3] = d*1e3*(1e4*B_T)^2 f^2 = d*1e11*B_T^2 f^2 ;  material: p = pi f B^2 mu''/(mu0 mu'^2)
for mix, mu, d in (("-2", 10, 9.6e-16), ("-6", 8.5, 8.9e-16)):
    for f in (3.6e6, 7.1e6, 14.2e6, 28.5e6):
        mupp = d * 1e11 * f * MU0 * mu**2 / np.pi
        print(f"mix {mix} f {f/1e6:5.1f} MHz: mu''_eddy = {mupp:.4f}  ->  Q_core = mu'/mu'' = {mu/mupp:5.0f}")
a2, b2, c2, d2 = 4.0e9, 3.0e8, 2.7e6, 9.6e-16
def pv_mm(Bg, f):
    return f / (a2 / Bg**3 + b2 / Bg**2.3 + c2 / Bg**1.65) + d2 * Bg**2 * f**2
for Bg in (10, 50, 200):
    print(f"mix -2 at 7.1 MHz, B = {Bg} G: total {pv_mm(Bg, 7.1e6):8.2f} mW/cm^3, eddy part {d2*Bg**2*7.1e6**2:8.2f}")
print("(43 at 7.1 MHz: Q = 1.0; 61 at 7.1 MHz: Q =", f"{mu_at('61',7.1e6)[0]/mu_at('61',7.1e6)[1]:.0f})")

# ---------------------------------------------------------------- 3. temperature stability of a tuned circuit
print("\n=== 3. Tuned-circuit drift over a 40 C swing (all inductance in the core, f ~ 1/sqrt(L)) ===")
for name, tc_ppm in (("-6", 35), ("-2", 95), ("61", 1000), ("52", 8000), ("43", 12500)):
    dmu = tc_ppm * 1e-6 * 40
    df = 0.5 * dmu
    print(f"{name:>3}: dmu/mu = {100*dmu:6.2f} %  ->  df/f = {100*df:6.3f} %  = {df*7.1e6/1e3:7.1f} kHz at 7.1 MHz")

# ---------------------------------------------------------------- 4. A_L -> turns
print("\n=== 4. A_L -> turns,  N = sqrt(L / A_L) ===")
cores = {"T37-2": 4.0, "T50-2": 4.9, "T50-6": 4.0, "T68-2": 5.7, "T68-6": 4.7, "T106-2": 13.5,
         "T130-2": 11.0, "T200-2": 12.0, "T200-6": 10.4, "FT140-43": 885.0, "FT240-43": 1075.0, "FT240-61": 170.0}
for core, L_uH in (("T50-2", 1.0), ("T68-6", 2.0), ("T68-2", 4.7), ("T200-2", 5.7), ("FT240-61", 10.0), ("FT240-43", 4.3)):
    al = cores[core]
    n = np.sqrt(L_uH * 1e3 / al)
    print(f"{L_uH:5.1f} uH on {core:9s} (A_L {al:6.1f} nH/N^2): N = {n:5.1f} turns")
# FT240-43 A_L is a 10 kHz value: inductance of 2 turns at RF uses mu'(f)
L0p = MU0 * 1.58e-4 / 0.145  # per turn^2, air
print(f"FT240-43 air L0/N^2 from Ae/le = {L0p*1e9:.3f} nH  -> A_L(10 kHz) = {800*L0p*1e9:.0f} nH (datasheet 1075 +-20 %)")
for f in (3.6e6, 7.1e6, 28.5e6):
    mp, mpp = mu_at("43", f)
    print(f"  2 turns at {f/1e6:4.1f} MHz: L_s = {4*L0p*mp*1e6:5.2f} uH, R_s = {TP*f*4*L0p*mpp:6.1f} ohm (A_L says {4*1.075:.2f} uH)")

# ---------------------------------------------------------------- 5. gapped cores
print("\n=== 5. Gapped core: mu_e = mu/(1 + mu g/le); tempco and tan(delta) dilute by mu_e/mu ===")
le = 145.0  # mm, FT240
for g in (0.0, 0.1, 0.5, 1.0, 3.4):
    mue = 800 / (1 + 800 * g / le)
    print(f"43 FT240, gap {g:4.1f} mm: mu_e = {mue:6.1f}; tempco {1.25*mue/800*1e4:7.0f} ppm/C; "
          f"tan(d) at 7.1 MHz {1.0*mue/800:.3f} (Q {800/mue:5.1f})")
# required gap for mu_e = 40
print(f"gap for mu_e 40: {le*(800/40-1)/800:.2f} mm")

# ---------------------------------------------------------------- 6. EFHW 49:1
print("\n=== 6. EFHW 49:1 (1:7 turns) on FT240-43: magnetising-branch loss at 100 W ===")
Ae, le_m, area = 1.58e-4, 0.145, None
OD, ID, H = 6.10, 3.555, 1.27  # cm
area = 2 * np.pi / 4 * (OD**2 - ID**2) + np.pi * (OD + ID) * H
print(f"FT240 outer surface (geometry) = {area:.1f} cm^2 per core")
R = 50.0
P = 100.0
Vrms = np.sqrt(P * R)

def zm(f, n1, ncore=1, mix="43", scale=1.0):
    mp, mpp = mu_at(mix, f)
    return 1j * TP * f * n1**2 * MU0 * ncore * Ae / le_m * (mp - 1j * mpp) * scale

def dT(p_w, ncore=1):
    return (1e3 * p_w / (area * ncore)) ** 0.833

print("Config        f MHz  |Zm| ohm  loss %  loss dB  Bpk mT  Pcore@100W cont  dT cont  dT SSB(20%)  dT FT8(50%)")
for label, n1, nc in (("2:14 x1", 2, 1), ("3:21 x1", 3, 1), ("2:14 x2", 2, 2), ("3:21 x2", 3, 2)):
    for f in (3.6e6, 7.1e6, 14.2e6, 28.5e6):
        Z = zm(f, n1, nc)
        frac = R * (1 / Z).real / (1 + R * (1 / Z).real)   # core shunt G vs load G (input power basis)
        Bpk = np.sqrt(2) * Vrms / (TP * f * n1 * nc * Ae) * 1e3
        pc = P * frac
        print(f"{label:9s} {f/1e6:6.1f} {abs(Z):9.1f} {100*frac:7.1f} {-10*np.log10(1-frac):7.2f} {Bpk:7.1f} "
              f"{pc:12.1f} W {dT(pc, nc):8.0f} {dT(0.2*pc, nc):10.0f} {dT(0.5*pc, nc):11.0f}")
# ON5UK comparison (older 43 data): 2 turns, 3.6 MHz |Z| 64.5 ohm, Q 2.10 ; 7.1 MHz |Z| 98.3, Q 1.46
for f, zabs, q in ((3.6e6, 64.5, 2.10), (7.1e6, 98.3, 1.46)):
    phi = np.arctan(q)
    Z = zabs * (np.cos(phi) + 1j * np.sin(phi))
    frac = R * (1 / Z).real / (1 + R * (1 / Z).real)
    print(f"ON5UK data 2:14 at {f/1e6:.1f} MHz: |Zm| {zabs} ohm, Q {q} -> loss {100*frac:.1f} %")
# continuous-power limit for 25 C rise (Amidon rule inverted)
for label, n1, nc in (("2:14 x1", 2, 1), ("3:21 x1", 3, 1), ("2:14 x2", 2, 2)):
    for f in (3.6e6, 7.1e6):
        Z = zm(f, n1, nc)
        frac = R * (1 / Z).real / (1 + R * (1 / Z).real)
        pc_max = (25 ** (1 / 0.833)) * area * nc / 1e3
        print(f"{label} {f/1e6:.1f} MHz: 25 C rise allows Pcore {pc_max:.1f} W -> {pc_max/frac:.0f} W average input")

print("\n--- large-signal correction from Fair-Rite 61 B-Pv data (proxy for NiZn above ~7 mT) ---")
fits = {2e6: (0.1035, 2.6545), 5e6: (0.3018, 2.7423), 7e6: (0.4589, 2.7988), 10e6: (2.0960, 2.5473),
        15e6: (4.6529, 2.6294), 20e6: (17.4360, 2.3241)}
for f, (k, n) in fits.items():
    mp, mpp = mu_at("61", f)
    for BmT in (3.0, 7.0, 14.0):
        pss = TP * f * (BmT * 1e-3) ** 2 * mpp / (2 * MU0 * (mp**2 + mpp**2)) / 1e3  # mW/cm^3
        pm = k * BmT**n
        print(f"61 {f/1e6:4.0f} MHz B {BmT:4.1f} mT: small-signal {pss:8.1f}  measured fit {pm:8.1f} mW/cm^3  ratio {pm/pss:5.2f}")

print("\n--- iron powder for the same job: turns needed for |Xm| >= 250 ohm at 3.6 MHz ---")
for core in ("T200-2", "T130-2"):
    L = 250 / (TP * 3.6e6)
    n = np.sqrt(L / (cores[core] * 1e-9))
    print(f"{core}: L {L*1e6:.1f} uH -> primary {n:.0f} turns, secondary {7*n:.0f} turns (impractical: self-resonance)")

print("\n--- compensation capacitor: pi low-pass C_comp - L_lk - C_s' (ILLUSTRATIVE parasitics) ---")
Llk, Cs_ref = 0.25e-6, 100e-12   # leakage referred to primary; secondary self-C (~2 pF) x 49
def vswr(f, Cc, n1=2, nc=1):
    w = TP * f
    zl = 1 / (1 / R + 1j * w * Cs_ref)
    z = zl + 1j * w * Llk
    y = 1 / z + 1 / zm(f, n1, nc) + 1j * w * Cc
    zin = 1 / y
    g = abs((zin - R) / (zin + R))
    return (1 + g) / (1 - g), zin
for Cc in (0, 50e-12, 100e-12, 150e-12, 200e-12):
    s = [vswr(f, Cc)[0] for f in (7.1e6, 14.2e6, 21.2e6, 28.5e6)]
    print(f"C_comp {Cc*1e12:5.0f} pF: VSWR 7/14/21/28 MHz = " + " / ".join(f"{x:.2f}" for x in s))
print(f"sqrt(L_lk/C_s') = {np.sqrt(Llk/Cs_ref):.0f} ohm -> symmetric pi needs C_comp ~ C_s' = {Cs_ref*1e12:.0f} pF")
Ic = Vrms * TP * 28.5e6 * 100e-12
print(f"100 pF at 28.5 MHz, 100 W: I_C = {Ic:.2f} A rms, V = {Vrms:.1f} V rms ({Vrms*np.sqrt(2):.0f} V pk); "
      f"secondary {7*Vrms:.0f} V rms ({7*Vrms*np.sqrt(2):.0f} V pk) at VSWR 1")

# ---------------------------------------------------------------- 7. 433 MHz coax CM choke
print("\n=== 7. 433.92 MHz common-mode choke: slip-on beads on RG-316, 2 W transmitter ===")
od, idd, h = 7.5e-3, 3.0e-3, 10e-3
L0b = MU0 * h * np.log(od / idd) / TP
for mix in ("31", "43", "52", "61"):
    mp, mpp = mu_at(mix, 433.92e6)
    Z = 1j * TP * 433.92e6 * L0b * (mp - 1j * mpp)
    print(f"mix {mix}: mu' {mp:5.1f} mu'' {mpp:5.1f} -> Z per bead = {Z.real:6.1f} {Z.imag:+6.1f}j ohm")
mp, mpp = mu_at("61", 433.92e6)
Zb = 1j * TP * 433.92e6 * L0b * (mp - 1j * mpp)
R5 = 5 * Zb.real
Vf = np.sqrt(2.0 * 50)
print(f"L0 per bead = {L0b*1e9:.2f} nH; 5 beads R = {R5:.0f} ohm; feed V = {Vf:.1f} V rms")
print(f"worst-case dissipation if the full feed voltage drives the shield path: V^2/R = {Vf**2/R5*1e3:.0f} mW "
      f"({100*Vf**2/R5/2.0:.1f} % of 2 W), {Vf**2/R5/5*1e3:.0f} mW per bead")
sa = 2 * np.pi / 4 * ((od * 100) ** 2 - (idd * 100) ** 2) + np.pi * (od + idd) * 100 * h * 100
print(f"bead surface {sa:.2f} cm^2 -> dT = {(Vf**2/R5/5*1e3/sa)**0.833:.1f} C per bead (Amidon rule)")
print(f"lambda/4 at 433.92 MHz in air = {299.792458/433.92/4*100:.1f} cm (sleeve-balun alternative)")

# ---------------------------------------------------------------- 8. why iron powder has mu ~ 10 and low eddy loss
print("\n=== 8. Iron-powder physics: packing fraction -> mu_e (Maxwell Garnett, mu_particle -> inf), eddy loss ===")
rho_fe = 7.87
for dens, label in ((5.0, "-2/-6 (5.0 g/cm3)"), (6.4, "-1/-15 (6.4 g/cm3)"), (6.5, "-3/-8 (6.5 g/cm3)")):
    p = dens / rho_fe
    mu_mg = (1 + 2 * p) / (1 - p)
    print(f"{label}: fill p = {p:.2f} -> Maxwell-Garnett mu_e = {mu_mg:.1f} (catalogue: 10/8.5, 20/25, 35/35)")
sig_fe, mur_fe = 1.0e7, 100.0
for f in (1e6, 10e6, 30e6):
    dlt = 1 / np.sqrt(np.pi * f * MU0 * mur_fe * sig_fe)
    print(f"iron skin depth at {f/1e6:4.0f} MHz (sigma 1e7, mu_r 100 assumed) = {dlt*1e6:5.1f} um")
for d_um in (3.0, 5.0, 8.0):
    k_sphere = sig_fe * (np.pi * d_um * 1e-6) ** 2 / 20   # W/m^3 per (T^2 Hz^2), uniform B in a sphere
    print(f"sphere d = {d_um} um: eddy coefficient {k_sphere:.2e} W/m^3/(T^2 Hz^2) vs Micrometals -2 d*1e11 = {9.6e-16*1e11:.2e}")
# gap: ampere-turns to saturation scale by mu/mu_e
print(f"gap raises NI to reach a given B by mu/mu_e: 43 with mu_e 40 -> x{800/40.5:.0f}")
