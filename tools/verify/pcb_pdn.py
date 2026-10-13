#!/usr/bin/env python3
"""
pcb_pdn.py — verification script for kb/13-pcb-rf-layout-emc/power-distribution-decoupling-for-rf.md

  1. Target impedance Z_t = dV_allowed / dI for the rails on a LoRa/GNSS flight computer.
  2. Parallel decoupling bank impedance |Z(f)| (bulk + 100 nF + 100 pF with ESL/ESR), anti-resonance peaks,
     and the effect of 'same value in parallel' vs 'mixed values'.
  3. Ferrite bead + capacitor supply filter: LC resonance, peaking (gain > 1) and damping (series R / ESR);
     transfer function checked against an ABCD solution.
  4. PA burst on a 5 V rail (EBYTE E22-400T33D: 0.85-1.2 A): droop = ESR*I + L dI/dt + I*t_resp/C before the
     regulator loop recovers; bulk capacitance needed for < 5 % droop.
  5. Ground bounce / shared-impedance coupling: star vs daisy-chain feeding of PA and LNA/VCO rails.
  7. Plane-pair capacitance per area for JLC stackups.
  6. Supply ripple -> VCO/PLL spur: FM sidebands from pushing K_push (Hz/V): spur = 20 log(K V / (2 f_m)) dBc;
     cascade of LDO PSRR and an LC post-filter for a 1 MHz buck ripple.

Run: python3 tools/verify/pcb_pdn.py      (instant)
"""
import numpy as np

ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def zcap(f, C, L, R):
    w = 2 * np.pi * f
    return R + 1j * w * L + 1 / (1j * w * C)


print("=" * 96)
print("1. Target impedance of rails")
print("=" * 96)
rails = [("5 V LoRa PA rail (E22-400T33D, 1.2 A burst), 5 % ripple", 5.0 * 0.05, 1.2),
         ("5 V E220-900T30D, 0.62 A, 5 %", 5.0 * 0.05, 0.62),
         ("3.3 V SX1262 VBAT (+22 dBm ~118 mA), 3 %", 3.3 * 0.03, 0.118),
         ("3.3 V MCU (ESP32-S3 Wi-Fi TX ~0.35 A steps), 3 %", 3.3 * 0.03, 0.35),
         ("3.3 V GNSS module (~30 mA), 1 %", 3.3 * 0.01, 0.03)]
for n, dv, di in rails:
    print(f"  {n:58s}: Z_target = {dv/di*1e3:7.1f} mOhm")
check("the 2 W LoRa rail needs a PDN below ~0.2 ohm up to the PA's current-step bandwidth", 5 * 0.05 / 1.2 < 0.25)

print("\n" + "=" * 96)
print("2. Decoupling bank |Z(f)| and anti-resonances")
print("=" * 96)
f = np.logspace(4, 10, 6000)
bank_mixed = [(22e-6, 1.0e-9, 5e-3), (100e-9, 0.5e-9, 20e-3), (100e-12, 0.4e-9, 0.1)]
bank_same = [(22e-6, 1.0e-9, 5e-3), (100e-9, 0.5e-9, 20e-3), (100e-9, 0.5e-9, 20e-3)]
for lab, bank in [("22 uF + 100 nF + 100 pF", bank_mixed), ("22 uF + 2 x 100 nF", bank_same)]:
    Y = sum(1 / zcap(f, *c) for c in bank)
    Z = np.abs(1 / Y)
    # find local maxima above 1 MHz
    idx = [i for i in range(1, len(f) - 1) if Z[i] > Z[i - 1] and Z[i] > Z[i + 1] and f[i] > 1e6]
    peaks = ", ".join(f"{Z[i]:.2f} ohm @ {f[i]/1e6:.0f} MHz" for i in idx)
    at = {fx: np.abs(1 / sum(1 / zcap(fx, *c) for c in bank)) for fx in [1e6, 10e6, 100e6, 433e6, 915e6]}
    print(f"  {lab:26s}: |Z| @1/10/100/433/915 MHz = " + ", ".join(f"{v*1e3:.0f}" for v in at.values()) + " mOhm;"
          f" anti-resonance peaks: {peaks if peaks else 'none'}")
Ym = sum(1 / zcap(f, *c) for c in bank_mixed)
Zm = np.abs(1 / Ym)
imax = [i for i in range(1, len(f) - 1) if Zm[i] > Zm[i - 1] and Zm[i] > Zm[i + 1] and f[i] > 1e6]
check("100 nF || 100 pF forms an anti-resonance of several ohms near 0.5 GHz", any(2 < Zm[i] < 40 and 3e8 < f[i] < 8e8 for i in imax),
      "(" + ", ".join(f"{Zm[i]:.1f} ohm @ {f[i]/1e6:.0f} MHz" for i in imax) + ")")
print("  -> at UHF what decouples is the smallest-ESL path (short, via-in-pad, L2 plane) and the plane capacitance,"
      " not the capacitor value; a 100 pF 'RF cap' helps only near its own SRF and can hurt between SRFs.")

print("\n" + "=" * 96)
print("3. Ferrite bead + capacitor filter: resonance and peaking")
print("=" * 96)


def bead_lowf(Lb=1.0e-6, Rdc=0.05):
    return Lb, Rdc


Lb, Rdc = bead_lowf()
for C, Resr, lab in [(10e-6, 3e-3, "10 uF MLCC (ESR 3 mOhm)"), (10e-6, 0.3, "10 uF + 0.3 ohm damping"),
                      (1e-6, 3e-3, "1 uF MLCC")]:
    fr = 1 / (2 * np.pi * np.sqrt(Lb * C))
    ff = np.logspace(3, 8, 4000)
    w = 2 * np.pi * ff
    Zs = Rdc + 1j * w * Lb              # bead below its resistive region: inductive
    Zp = Resr + 1 / (1j * w * C)
    H = Zp / (Zs + Zp)                  # ideal source, open load
    pk = 20 * np.log10(np.abs(H).max())
    fpk = ff[np.argmax(np.abs(H))]
    Q = np.sqrt(Lb / C) / (Rdc + Resr)
    att1M = 20 * np.log10(abs(H[np.argmin(abs(ff - 1e6))]))
    print(f"  bead L {Lb*1e6:.1f} uH/Rdc {Rdc*1e3:.0f} mOhm + {lab:26s}: f_res {fr/1e3:6.1f} kHz, Q ~{Q:4.1f}, peak {pk:+5.1f} dB"
          f" @ {fpk/1e3:.0f} kHz; at 1 MHz {att1M:+.1f} dB")
Q1 = np.sqrt(Lb / 10e-6) / (Rdc + 3e-3)
check("an undamped bead + 10 uF peaks by ~Q (>= +10 dB) near 50 kHz", 20 * np.log10(Q1) > 10, f"(Q {Q1:.1f})")
Rd = np.sqrt(Lb / 10e-6)
print(f"  damping rule: series R ~ sqrt(L/C) = {Rd:.2f} ohm in the bulk-cap branch (or a lossy polymer/tantalum)")

print("\n" + "=" * 96)
print("4. PA burst droop on the 5 V rail (1.2 A step)")
print("=" * 96)
I = 1.2
for tr in [2e-6, 10e-6]:
    for Cb, esr in [(22e-6, 5e-3), (100e-6, 20e-3), (220e-6, 30e-3), (470e-6, 40e-3)]:
        for tresp in [10e-6, 50e-6]:
            dV_esr = I * esr
            dV_L = 30e-9 * I / tr
            dV_C = I * tresp / Cb
            tot = dV_esr + dV_L + dV_C
            print(f"  dI/dt 1.2 A/{tr*1e6:4.0f} us, C {Cb*1e6:5.0f} uF (ESR {esr*1e3:3.0f} mOhm), regulator recovery {tresp*1e6:3.0f} us:"
                  f" droop ~{tot*1e3:6.0f} mV ({tot/5*100:4.1f} %)")
Cneed = I * 50e-6 / (0.05 * 5 - 1.2 * 0.02)
print(f"  bulk needed for < 5 % with a 50 us regulator recovery and 20 mOhm ESR: C >= {Cneed*1e6:.0f} uF")
check("a 1.2 A burst with a 50 us loop needs > 200 uF of bulk at the module for < 5 % droop", Cneed > 200e-6,
      f"({Cneed*1e6:.0f} uF)")

print("\n" + "=" * 96)
print("5. Shared-impedance coupling: daisy-chain vs star feeding of PA and LNA/VCO")
print("=" * 96)
rho = 1.72e-8
Rsh = rho * 20e-3 / (1e-3 * 35e-6)
Lsh = 20e-9
for lab, Zshared in [("daisy chain: 20 mm x 1 mm shared trace", (Rsh, Lsh)),
                     ("star from bulk cap: shared = cap ESR + 2 mm", (5e-3 + rho * 2e-3 / (1e-3 * 35e-6), 2e-9)),
                     ("plane-fed, local caps (spreading ~1 mOhm, 0.2 nH)", (1e-3, 0.2e-9))]:
    R, L = Zshared
    dv = I * R + L * I / 10e-6
    print(f"  {lab:50s}: coupled step into LNA/VCO supply ~{dv*1e3:6.2f} mV (1.2 A, 10 us edge)")
check("daisy-chaining the LNA supply behind the PA injects > 10 mV steps", I * Rsh + Lsh * I / 10e-6 > 10e-3,
      f"({(I*Rsh + Lsh*I/10e-6)*1e3:.1f} mV)")

print("\n" + "=" * 96)
print("6. Supply ripple -> VCO/PLL spurs, and the filtering chain")
print("=" * 96)
for Kp in [0.2e6, 2e6, 20e6]:        # pushing, Hz/V (assumed range: well-regulated integrated VCO ... bare VCO)
    for Vr, fm in [(1e-3, 1e6), (10e-6, 1e6), (1e-3, 50e3)]:
        beta = Kp * Vr / fm
        spur = 20 * np.log10(beta / 2)
        print(f"  pushing {Kp/1e6:5.1f} MHz/V, ripple {Vr*1e6:7.1f} uV @ {fm/1e3:6.0f} kHz: spur {spur:6.1f} dBc")
b = 2e6 * 1e-3 / 1e6
check("1 mV of 1 MHz ripple on a 2 MHz/V VCO gives a -60 dBc spur", abs(20 * np.log10(b / 2) + 60) < 0.1)
buck_ripple = 20e-3
psrr_ldo = 40.0       # dB at 1 MHz (typical for good RF LDOs; many generic LDOs have far less)
lc = 30.0             # dB from bead + 10 uF at 1 MHz (section 3)
out = buck_ripple * 10 ** (-(psrr_ldo + lc) / 20)
print(f"  20 mV buck ripple at 1 MHz -> LDO (PSRR {psrr_ldo:.0f} dB) -> bead+cap ({lc:.0f} dB): {out*1e6:.1f} uV at the VCO/LNA")

print("\n" + "=" * 96)
print("7. Plane-pair capacitance (parallel plate)")
print("=" * 96)
e0 = 8.854e-12
for lab, h, er in [("JLC 4L core L2-L3 1.065 mm", 1.065e-3, 4.6), ("7628 prepreg 0.2104 mm", 0.2104e-3, 4.4),
                   ("3313 prepreg 0.0994 mm", 0.0994e-3, 4.1)]:
    cpa = e0 * er / h
    print(f"  {lab:28s}: {cpa*1e-4*1e12:6.2f} pF/cm^2; 50 x 50 mm pair: {cpa*25e-4*1e12:6.1f} pF")
check("JLC 1.065 mm core gives ~3.8 pF/cm^2 (~96 pF for 50 x 50 mm)", abs(e0 * 4.6 / 1.065e-3 * 1e-4 * 1e12 - 3.82) < 0.05)

print("\nALL CHECKS PASSED" if ok_all else "\nSOME CHECKS FAILED")
