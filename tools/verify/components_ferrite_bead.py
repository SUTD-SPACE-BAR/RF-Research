#!/usr/bin/env python3
"""
Verification for kb/04-real-components-hf/ferrites-and-beads.md

  1. Ferrite-bead circuit model (Burket, Analog Dialogue 2016; Tyco BMB2A1000LN2 fit):
     Rdc + (L || Cpar || Rac). R, X, |Z| vs frequency; inductive/resistive/capacitive regions.
  2. Bead + decoupling capacitor low-pass: resonance frequency, peaking, and the three damping methods
     (A: series R with the cap, B: R across the bead, C: extra large cap with series R).
  3. DC-bias collapse: if L drops to 10-30 % the resonance moves up and the 100 MHz impedance falls.
  4. Fair-Rite field-strength rule H = 1.256 N I / l_m (oersted) and N^2 scaling of core impedance.
  5. Common-mode choke: differential vs common-mode impedance with coupling k.
Run: python3 tools/verify/components_ferrite_bead.py
"""
import numpy as np
from scipy.signal import find_peaks
TP = 2 * np.pi

L0, Cpar, Rdc, Rac = 1.208e-6, 1.678e-12, 0.300, 1082.0

def zbead(f, L=L0, C=Cpar, Rd=Rdc, Ra=Rac):
    w = TP * f
    Y = 1 / (1j * w * L) + 1j * w * C + 1 / Ra
    return Rd + 1 / Y

print("=== 1. Bead model impedance ===")
f = np.logspace(5, 10, 50001)
Z = zbead(f)
i_pk = np.argmax(np.abs(Z))
print(f"peak |Z| = {abs(Z[i_pk]):.0f} ohm at {f[i_pk]/1e6:.1f} MHz (parallel resonance of L and Cpar: "
      f"{1/(TP*np.sqrt(L0*Cpar))/1e6:.1f} MHz)")
cross = np.where(np.diff(np.sign(Z.real - np.abs(Z.imag))))[0]
print("frequencies where R = |X|: " + ", ".join(f"{f[i]/1e6:.1f} MHz" for i in cross))
for fx in [1e6, 10e6, 30.7e6, 100e6, 433.92e6, 803e6, 915e6, 2.45e9]:
    z = zbead(fx)
    print(f"  f={fx/1e6:8.2f} MHz: Z = {z.real:8.1f} + j{z.imag:8.1f} ohm, |Z| = {abs(z):7.1f}")

print("\n=== 2. Bead + capacitor LC low-pass: resonance and damping ===")
Rs = 0.05          # supply (regulator) output impedance
Rload = 1e4        # light load (uA-range currents)
def transfer(f, Cf, ESR, ESL=0.5e-9, extra=None, bead_scale=1.0):
    w = TP * f
    Zb = zbead(f, L=L0 * bead_scale)
    Zc = ESR + 1j * w * ESL + 1 / (1j * w * Cf)
    Zsh = 1 / (1 / Zc + 1 / Rload)
    if extra == "B":          # resistor across the bead
        Zb = 1 / (1 / Zb + 1 / 10.0)
    if extra == "C":          # extra 1 uF with 2 ohm in series in parallel with Cf
        Zd = 2.0 + 1 / (1j * w * 1e-6) + 1j * w * 1e-9
        Zsh = 1 / (1 / Zsh + 1 / Zd)
    if extra == "A":          # series resistor with the capacitor
        Zc2 = Zc + 2.0
        Zsh = 1 / (1 / Zc2 + 1 / Rload)
    return Zsh / (Rs + Zb + Zsh)
fr = np.logspace(4, 9, 60001)
for label, kw in [("bead + 10 nF (ESR 10 mohm)", dict(Cf=10e-9, ESR=0.01)),
                  ("A: + 2 ohm in series with the 10 nF", dict(Cf=10e-9, ESR=0.01, extra="A")),
                  ("B: 10 ohm across the bead", dict(Cf=10e-9, ESR=0.01, extra="B")),
                  ("C: + (1 uF + 2 ohm) damping branch", dict(Cf=10e-9, ESR=0.01, extra="C")),
                  ("bead + 1 uF (ESR 5 mohm)", dict(Cf=1e-6, ESR=0.005))]:
    H = transfer(fr, **kw)
    HdB = 20 * np.log10(np.abs(H))
    i = np.argmax(HdB)
    a100 = HdB[np.argmin(np.abs(fr - 100e6))]
    print(f"  {label:38s}: peak {HdB[i]:+6.1f} dB at {fr[i]/1e6:7.3f} MHz; at 100 MHz {a100:6.1f} dB")
Cf = 10e-9
print(f"  resonance estimate 1/(2 pi sqrt(L C)) = {1/(TP*np.sqrt(L0*Cf))/1e6:.3f} MHz; sqrt(L/C) = {np.sqrt(L0/Cf):.1f} ohm; "
      f"undamped Q ~ sqrt(L/C)/(Rs+Rdc+ESR) = {np.sqrt(L0/Cf)/(Rs+Rdc+0.01):.0f}")

print("\n=== 3. DC-bias collapse (L scaled to 30 % and 10 %) ===")
for sc in [1.0, 0.3, 0.1]:
    z100 = zbead(100e6, L=L0 * sc)
    H = transfer(fr, Cf=10e-9, ESR=0.01, bead_scale=sc)
    HdB = 20 * np.log10(np.abs(H)); i = np.argmax(HdB)
    print(f"  L = {sc*100:3.0f} %: |Z(100 MHz)| = {abs(z100):6.1f} ohm; bead+10nF peak {HdB[i]:+5.1f} dB at {fr[i]/1e6:.2f} MHz; "
          f"atten at 10 MHz {HdB[np.argmin(np.abs(fr-10e6))]:.1f} dB")

print("\n=== 4. Fair-Rite field strength and N^2 scaling ===")
for lm_cm, I in [(0.5, 0.2), (0.5, 1.0), (2.5, 1.0)]:
    H = 1.256 * 1 * I / lm_cm
    print(f"  single turn, l_m = {lm_cm} cm, I = {I} A: H = {H:.2f} Oe ({H*79.577:.0f} A/m)")
print("  impedance of a core scales as N^2 (below the winding-capacitance region): 1 t -> 2 t = x4, 3 t = x9")

print("\n=== 5. Common-mode choke ===")
Lw, k = 10e-6, 0.995
for fx in [1e6, 10e6, 100e6]:
    w = TP * fx
    Zcm = 1j * w * Lw * (1 + k) / 2 * 2 / 2   # both windings in parallel for CM current split... see below
    # CM: equal currents in same direction in both windings: each winding V = jw(L+M) I_half; total CM current 2*I_half
    Zcm = 1j * w * (Lw + k * Lw) / 2
    # DM: opposite currents: loop impedance = 2 * jw (L - M)
    Zdm = 2 * 1j * w * (Lw - k * Lw)
    print(f"  f={fx/1e6:6.1f} MHz: |Z_CM| (both lines together) = {abs(Zcm):8.1f} ohm, |Z_DM| (loop) = {abs(Zdm):7.2f} ohm")
print("OK")
