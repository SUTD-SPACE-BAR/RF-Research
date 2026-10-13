#!/usr/bin/env python3
"""
Verification for kb/04-real-components-hf/package-parasitics-bondwires.md

  1. Bondwire inductance: isolated-wire formula vs length/diameter; wire over a ground plane (image);
     arc (loop height) effect; parallel bondwires with mutual coupling.
  2. Package lead inductance table (TI) -> reactance at 433.92 / 915 / 2450 MHz.
  3. QFN exposed-pad ground path: downbonds + EP via array, 2-layer vs 4-layer.
  4. Why RF ICs have many ground pins: source-degeneration gain loss and ground bounce from a PA current.
  5. DC resistance of a bondwire (TI SLVAEE1 check: Cu 1 mm x 50.8 um -> 8.6 mohm).
Run: python3 tools/verify/components_bondwire.py
"""
import numpy as np
MU0 = 4e-7 * np.pi
TP = 2 * np.pi

def L_wire(l, r):  # isolated straight wire, HF (no internal inductance)
    return MU0 * l / (2 * np.pi) * (np.log(2 * l / r) - 1 + r / l)

def M_par(l, s):
    return MU0 * l / (2 * np.pi) * (np.log(l / s + np.sqrt(1 + (l / s)**2)) - np.sqrt(1 + (s / l)**2) + s / l)

def L_over_plane(l, r, h):  # wire at height h over a ground plane (image method, per unit length times l)
    return MU0 * l / (2 * np.pi) * np.arccosh(h / r)

print("=== 1. Bondwires ===")
for d_um in [18, 25, 33, 50]:
    r = d_um * 1e-6 / 2
    vals = [L_wire(l * 1e-3, r) * 1e9 for l in [0.5, 1.0, 1.5, 2.0]]
    print(f"  {d_um} um wire, isolated: L(0.5/1/1.5/2 mm) = " + ", ".join(f"{v:.2f}" for v in vals) + " nH")
r = 12.5e-6
for h_um in [50, 100, 200, 400]:
    print(f"  1 mm of 25 um wire at height {h_um} um over a ground plane: loop L = {L_over_plane(1e-3, r, h_um*1e-6)*1e9:.3f} nH")
# arc: a 1 mm span with 150 um loop height -> approximate path as arc; length increases
span, hloop = 1.0e-3, 0.15e-3
# parabolic arc length approximation
arc = span * (1 + (8 / 3) * (hloop / span)**2)
print(f"  1 mm span, 150 um loop height: arc length ~ {arc*1e3:.3f} mm -> L = {L_wire(arc, r)*1e9:.3f} nH (straight: {L_wire(span, r)*1e9:.3f})")
# parallel bondwires
l = 1.0e-3
for s_um in [50, 100, 200, 500]:
    s = s_um * 1e-6
    L = L_wire(l, r); M = M_par(l, s)
    print(f"  2 parallel 1 mm wires, pitch {s_um} um: L_eff = (L+M)/2 = {(L+M)/2*1e9:.3f} nH (L/2 = {L/2*1e9:.3f})")

print("\n=== 2. Package lead inductance (TI QFN comparison tables, 20-pin) ===")
pk = [("SOIC-20", 5.012, 0.717), ("SSOP-20", 3.495, 0.420), ("TSSOP-20", 2.808, 0.317), ("TVSOP-20", 2.561, 0.342),
      ("QFN-20 (RGY)", 1.178, 0.252), ("QFN-16", 0.818, 0.236), ("QFN-14", 0.791, 0.226)]
for name, Lnh, Cpf in pk:
    x = [TP * f * Lnh * 1e-9 for f in (433.92e6, 915e6, 2450e6)]
    fr = 1 / (TP * np.sqrt(Lnh * 1e-9 * Cpf * 1e-12))
    print(f"  {name:13s}: L = {Lnh:.3f} nH, C = {Cpf:.3f} pF -> X_L = {x[0]:.1f} / {x[1]:.1f} / {x[2]:.1f} ohm at 434/915/2450 MHz;"
          f" L-C resonance {fr/1e9:.1f} GHz")

print("\n=== 3. QFN exposed-pad ground path ===")
def L_via_GP(h, r):
    return MU0 / (2 * np.pi) * (h * np.log((h + np.sqrt(h**2 + r**2)) / r) + 1.5 * (r - np.sqrt(r**2 + h**2)))
Ldown = L_wire(0.6e-3, 12.5e-6)   # die-to-paddle downbond ~0.6 mm
for ndown in [1, 4, 8]:
    Ld = Ldown / ndown * 1.3      # 1.3 factor for mutual coupling between downbonds (rough)
    for label, Lvias in [("2-layer 1.6 mm, 9 vias (coupled est.)", 0.198e-9), ("4-layer to L2, 9 vias", L_via_GP(0.2104e-3, 0.15e-3) / 9 * 2)]:
        Ltot = Ld + Lvias
        print(f"  {ndown} downbond(s) ({Ld*1e9:.3f} nH) + {label} ({Lvias*1e9:.3f} nH) = {Ltot*1e9:.3f} nH "
              f"-> {TP*915e6*Ltot:.2f} ohm at 915 MHz")

print("\n=== 4. Why many ground pins ===")
gm = 0.05
for Ls_nH in [0.25, 0.5, 1.0, 2.0]:
    out = []
    for f in (433.92e6, 915e6, 2450e6):
        k = TP * f * gm * Ls_nH * 1e-9
        out.append(f"{-20*np.log10(abs(1+1j*k)):.2f} dB")
    print(f"  CS stage gm=50 mS, common ground L = {Ls_nH} nH: gain change at 434/915/2450 MHz = {', '.join(out)}")
for Ig, Lg in [(0.5, 0.5e-9), (0.5, 0.1e-9), (1.0, 0.5e-9)]:
    for f in (433.92e6, 915e6):
        print(f"  ground bounce: {Ig} A RF current through {Lg*1e9:.1f} nH at {f/1e6:.0f} MHz = {Ig*TP*f*Lg:.2f} V peak")

print("\n=== 5. Bondwire DC resistance ===")
for mat, rho in [("Cu", 1.68e-8), ("Au", 2.44e-8)]:
    R = rho * 1e-3 / (np.pi * (50.8e-6 / 2)**2)
    print(f"  {mat} 1 mm x 50.8 um: R_dc = {R*1e3:.2f} mohm")
R25 = 2.44e-8 * 1e-3 / (np.pi * (12.5e-6)**2)
delta = np.sqrt(2.44e-8 / (np.pi * 915e6 * MU0))
Rac = 2.44e-8 * 1e-3 / (np.pi * 25e-6 * delta)
print(f"  Au 1 mm x 25 um: R_dc = {R25*1e3:.1f} mohm; skin depth @915 MHz = {delta*1e6:.2f} um -> R_ac ~ {Rac*1e3:.0f} mohm; "
      f"Q of the wire alone = {TP*915e6*L_wire(1e-3,12.5e-6)/Rac:.0f}")
print("OK")
