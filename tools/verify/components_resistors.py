#!/usr/bin/env python3
"""
Verification for kb/04-real-components-hf/resistors-at-rf.md

  1. Chip resistor model Z = (R + jwL) || (1/(jwC)): |Z|/R and phase vs frequency for several R;
     frequency where |Z| deviates 10 %; first-order flatness at R = sqrt(L/C).
  2. Vishay thin-film internal parasitics (0201/0402/0603) vs typical pad/mount parasitics.
  3. 50-ohm terminations: single 49.9 ohm vs 2 x 100 ohm in parallel, with a ground via; return loss.
  4. Attenuator pads (pi and T) for 3/6/10/20/30 dB at 50 ohm; power dissipated in each resistor at 2 W input.
  5. Power derating of thick-film chips (rated at 70 C, linear to 0 W at 155 C).
Run: python3 tools/verify/components_resistors.py
"""
import numpy as np
TP = 2 * np.pi

def zres(f, R, L, C):
    w = TP * f
    return 1 / (1 / (R + 1j * w * L) + 1j * w * C)

print("=== 1. Chip-resistor model: L = 0.4 nH, C = 0.05 pF (0402 incl. pads, order of magnitude) ===")
L, C = 0.4e-9, 0.05e-12
print(f"sqrt(L/C) = {np.sqrt(L/C):.1f} ohm")
f = np.logspace(7, 11, 40001)
for R in [5, 20, 50, 89.4, 200, 1000, 10000]:
    Z = zres(f, R, L, C)
    dev = np.abs(np.abs(Z) / R - 1)
    i10 = np.argmax(dev > 0.10)
    f10 = f[i10] if dev.max() > 0.10 else np.inf
    z433 = zres(433.92e6, R, L, C); z915 = zres(915e6, R, L, C); z24 = zres(2.45e9, R, L, C)
    print(f"  R={R:8.1f}: 10 % |Z| error above {f10/1e9:7.2f} GHz; Z(434M)={z433.real:8.2f}{z433.imag:+8.2f}j, "
          f"Z(915M)={z915.real:8.2f}{z915.imag:+8.2f}j, Z(2.45G)={z24.real:8.2f}{z24.imag:+8.2f}j")
# first-order flatness: Z ~ R (1 + jw(L/R - RC) + ...) -> zero first-order phase when R^2 = L/C
Ropt = np.sqrt(L / C)
for R in [0.5 * Ropt, Ropt, 2 * Ropt]:
    w = TP * 1e9
    Z = zres(1e9, R, L, C)
    print(f"  R={R:6.1f}: phase at 1 GHz = {np.degrees(np.angle(Z)):+.3f} deg (first-order term w(L/R-RC) = {np.degrees(w*(L/R-R*C)):+.3f} deg)")

print("\n=== 2. Vishay thin-film internal parasitics (tech note 60107) ===")
vishay = [("0201 flip", 0.0206e-12, 1.73e-5 * 1e-9), ("0402 flip", 0.0262e-12, 1.89e-3 * 1e-9),
          ("0402 wrap", 0.0392e-12, 0.1209e-9), ("0603 flip", 0.0403e-12, 0.0267e-9)]
for name, Ci, Li in vishay:
    for R in [50, 1000]:
        z = zres(2.45e9, R, Li, Ci)
        print(f"  {name}: internal C={Ci*1e15:.1f} fF, L={Li*1e12:.3f} pH; R={R}: Z(2.45 GHz) = {z.real:.2f}{z.imag:+.2f}j ohm")

print("\n=== 3. 50-ohm terminations to ground (via 0.3 nH, pad C 0.05 pF to ground) ===")
Z0 = 50.0
def term(f, parts, Lvia=0.3e-9, Cpad=0.05e-12):
    w = TP * f
    Ypar = sum(1 / zres(f, R, L, C) for R, L, C in parts)
    Zr = 1 / Ypar + 1j * w * Lvia
    return 1 / (1 / Zr + 1j * w * Cpad)
for label, parts in [("1 x 49.9 ohm 0402 (L 0.4 nH, C 0.03 pF)", [(49.9, 0.4e-9, 0.03e-12)]),
                     ("2 x 100 ohm 0402 in parallel", [(100, 0.4e-9, 0.03e-12)] * 2),
                     ("1 x 49.9 ohm 0603 (L 0.6 nH, C 0.04 pF)", [(49.9, 0.6e-9, 0.04e-12)])]:
    out = []
    for fx in [433.92e6, 915e6, 2.45e9, 5.8e9]:
        Zt = term(fx, parts)
        G = (Zt - Z0) / (Zt + Z0)
        out.append(f"{fx/1e9:.2f} GHz RL={-20*np.log10(abs(G)):5.1f} dB")
    print(f"  {label:40s}: " + "; ".join(out))

print("\n=== 4. Attenuator pads (50 ohm) ===")
for A in [3, 6, 10, 20, 30]:
    K = 10**(A / 20)
    Rsh = Z0 * (K + 1) / (K - 1); Rse = Z0 * (K**2 - 1) / (2 * K)        # pi
    Rt_se = Z0 * (K - 1) / (K + 1); Rt_sh = Z0 * 2 * K / (K**2 - 1)     # T
    # power split in pi pad with 2 W in, matched load
    Pin = 2.0
    Vin = np.sqrt(2 * Pin * Z0)
    Vout = Vin / K
    P_sh1 = Vin**2 / (2 * Rsh); P_se = (Vin - Vout)**2 / (2 * Rse); P_sh2 = Vout**2 / (2 * Rsh)
    Pout = Vout**2 / (2 * Z0)
    assert np.isclose(P_sh1 + P_se + P_sh2 + Pout, Pin)
    print(f"  {A:2d} dB: pi shunt {Rsh:7.2f} / series {Rse:7.2f} ohm; T series {Rt_se:6.2f} / shunt {Rt_sh:7.2f} ohm; "
          f"at 2 W in (pi): {P_sh1:.3f} W in input shunt, {P_se:.3f} W series, {P_sh2:.4f} W output shunt, {Pout*1e3:.1f} mW out")

print("\n=== 5. Thick-film chip power derating (70 C knee, 0 W at 155 C) ===")
for pkg, Prated in [("0402", 1 / 16), ("0603", 1 / 10), ("0805", 1 / 8), ("1206", 1 / 4)]:
    pw = [Prated * min(1, max(0, (155 - T) / (155 - 70))) for T in [70, 85, 100, 125]]
    print(f"  {pkg} rated {Prated*1e3:.1f} mW: allowed at 70/85/100/125 C = " + ", ".join(f"{p*1e3:.1f}" for p in pw) + " mW")
print("OK")
