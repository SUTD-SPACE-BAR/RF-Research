#!/usr/bin/env python3
"""
Verification for kb/01-circuit-theory/energy-storage-and-reactive-power.md

  1. Complex power S = 1/2 V I* = P + jQ; Tellegen-style balance (sum of element complex powers = source).
  2. Reactive power Q = 2 w (W_m - W_e); stored energies in L and C.
  3. Element stresses in a 2 W, 433.92 MHz L-match (50 -> 5 ohm) and a 1 W 915 MHz match.
  4. Element voltages/currents inside the 5th-order elliptic harmonic LPF at 2 W (from the filter page).
  5. Small-loop antenna tuning capacitor voltage at 2 W (why "high-Q" means "high voltage").
Run: python3 tools/verify/circuits_reactive_power.py
"""
import numpy as np
TP = 2 * np.pi

print("=== 1. Complex power bookkeeping ===")
f = 433.92e6; w = TP * f
R, L, C = 30.0, 20e-9, 5e-12
Vs = 10.0  # peak
Z = R + 1j * w * L + 1 / (1j * w * C)
I = Vs / Z
S_src = 0.5 * Vs * np.conj(I)
S_R = 0.5 * abs(I)**2 * R
S_L = 0.5 * abs(I)**2 * (1j * w * L)
S_C = 0.5 * abs(I)**2 * (1 / (1j * w * C))
print(f"S_source = {S_src:.5f} VA ; S_R + S_L + S_C = {S_R + S_L + S_C:.5f} VA")
assert np.isclose(S_src, S_R + S_L + S_C)
PF = S_src.real / abs(S_src)
print(f"P = {S_src.real*1e3:.2f} mW, Q = {S_src.imag*1e3:.2f} mvar, PF = {PF:.3f}")

print("\n=== 2. Q = 2 w (Wm - We) ===")
Wm = 0.25 * L * abs(I)**2          # time-average magnetic energy (peak phasor): (1/4) L |I|^2
VC = I / (1j * w * C)
We = 0.25 * C * abs(VC)**2
print(f"Wm = {Wm*1e12:.4f} pJ, We = {We*1e12:.4f} pJ, 2w(Wm-We) = {2*w*(Wm-We)*1e3:.3f} mvar vs Q = {S_src.imag*1e3:.3f}")
assert np.isclose(2 * w * (Wm - We), S_src.imag)

print("\n=== 3. L-match element stress ===")
def lmatch(Rhi, Rlo, f, Pout):
    w = TP * f
    Qn = np.sqrt(Rhi / Rlo - 1)
    Xs = Qn * Rlo; Xp = Rhi / Qn
    Ls = Xs / w; Cp = 1 / (w * Xp)
    # power delivered to Rlo side? here: PA at Rlo side (low impedance), antenna at Rhi (50 ohm)
    I_lo = np.sqrt(2 * Pout / Rlo)          # peak current through Rlo and the series L
    V_hi = np.sqrt(2 * Pout * Rhi)          # peak voltage across the 50-ohm side / shunt C
    I_Cp = V_hi / Xp
    Q_L = 0.5 * I_lo**2 * Xs; Q_C = 0.5 * V_hi**2 / Xp
    return Qn, Ls, Cp, I_lo, V_hi, I_Cp, Q_L, Q_C
for (Rhi, Rlo, fq, P, tag) in [(50, 5.06, 433.92e6, 2.0, "2 W @ 433.92 MHz, 50->5.06 ohm"),
                              (50, 12.5, 915e6, 1.0, "1 W @ 915 MHz, 50->12.5 ohm"),
                              (50, 0.5, 433.92e6, 20.0, "20 W @ 433.92 MHz, 50->0.5 ohm")]:
    Qn, Ls, Cp, I_lo, V_hi, I_Cp, QLv, QCv = lmatch(Rhi, Rlo, fq, P)
    print(f"{tag}: Qn={Qn:.2f}, Ls={Ls*1e9:.2f} nH (I_pk={I_lo:.2f} A, I_rms={I_lo/np.sqrt(2):.2f} A), "
          f"Cp={Cp*1e12:.2f} pF (V_pk={V_hi:.1f} V, I_pk={I_Cp:.2f} A); reactive power L={QLv:.2f} var, C={QCv:.2f} var "
          f"(= Qn*P = {Qn*P:.2f})")
    assert np.isclose(QLv, Qn * P) and np.isclose(QCv, Qn * P)

print("\n=== 4. Element stress in the elliptic 433.92 MHz LPF at 2 W ===")
# element values from circuits_filter_prototypes.py (elliptic re-scaled, zero on 2f)
C1, L2, C2, C3, L4, C4, C5 = 5.77e-12, 16.72e-9, 2.012e-12, 11.02e-12, 20.20e-9, 0.714e-12, 6.81e-12
Z0 = 50.0; P = 2.0
w = TP * 433.92e6
# work backwards from the load: V_load for 2 W into 50 ohm
V = np.sqrt(2 * P * Z0) + 0j; I = V / Z0
rep = []
def shunt(Cv, V, I, name):
    Ic = 1j * w * Cv * V
    rep.append((name, abs(V), abs(Ic)))
    return V, I + Ic
def series_par(Lv, Cv, V, I, name):
    Zb = 1 / (1 / (1j * w * Lv) + 1j * w * Cv)
    Vb = I * Zb
    IL = Vb / (1j * w * Lv); IC = Vb * 1j * w * Cv
    rep.append((name + " (L||C branch)", abs(Vb), max(abs(IL), abs(IC))))
    rep.append((name + "   inductor current", abs(Vb), abs(IL)))
    rep.append((name + "   capacitor current", abs(Vb), abs(IC)))
    return V + Vb, I
V, I = shunt(C5, V, I, "C5")
V, I = series_par(L4, C4, V, I, "L4||C4")
V, I = shunt(C3, V, I, "C3")
V, I = series_par(L2, C2, V, I, "L2||C2")
V, I = shunt(C1, V, I, "C1")
for name, v, i in rep:
    print(f"  {name:28s}: |V| = {v:6.2f} V peak, |I| = {i:5.3f} A peak")
Zin = V / I
print(f"  input impedance at 433.92 MHz = {Zin:.2f} ohm; input voltage {abs(V):.2f} V peak")

print("\n=== 5. Small loop antenna tuning capacitor at 2 W, 433.92 MHz ===")
Lloop = 50e-9; Rrad = 0.1; Rloss = 0.4; P = 2.0
w = TP * 433.92e6
X = w * Lloop
Iloop = np.sqrt(2 * P / (Rrad + Rloss))
Vcap = Iloop * X
Ctune = 1 / (w * X)
Qant = X / (Rrad + Rloss)
print(f"X_L = {X:.1f} ohm, Q = {Qant:.0f}, loop current {Iloop:.2f} A peak, tuning C = {Ctune*1e12:.2f} pF, "
      f"capacitor voltage = {Vcap:.0f} V peak ; efficiency = {Rrad/(Rrad+Rloss)*100:.0f} %")
print("OK")
