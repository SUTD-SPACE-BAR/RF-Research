#!/usr/bin/env python3
"""
Verification for kb/01-circuit-theory/resonance-and-q.md

Checks:
  1. Series/parallel RLC: f0, Q, -3 dB bandwidth = f0/Q (numerically), energy definition of Q.
  2. Unloaded / external / loaded Q: 1/QL = 1/Qu + 1/Qe.
  3. Insertion loss of a single doubly-terminated resonator at resonance: IL = -20 log10(1 - QL/Qu).
  4. Component-limited Qu of an LC tank: 1/Qu = 1/Q_L + 1/Q_C.
  5. L-section matching Q: Q = sqrt(Rhi/Rlo - 1) and its bandwidth.
  6. Group delay of a single resonator at centre: tau = 2 QL / w0.
Run: python3 tools/verify/circuits_resonance_q.py
"""
import numpy as np

TP = 2 * np.pi

print("=== 1. Series RLC: 22 nH, C for 433.92 MHz, R = 1.2 ohm ===")
L = 22e-9
f0 = 433.92e6
w0 = TP * f0
C = 1 / (w0**2 * L)
R = 1.2
Q_formula = w0 * L / R
print(f"C = {C*1e12:.4f} pF, X0 = {w0*L:.3f} ohm, Q = w0L/R = {Q_formula:.2f}, Z0char = sqrt(L/C) = {np.sqrt(L/C):.3f} ohm")
f = np.linspace(0.8 * f0, 1.2 * f0, 400001)
w = TP * f
# drive with voltage source through the series RLC (current ~ 1/Z); -3 dB of |I|^2
Z = R + 1j * w * L + 1 / (1j * w * C)
P = 1 / np.abs(Z)**2
Pn = P / P.max()
idx = np.where(Pn >= 0.5)[0]
bw = f[idx[-1]] - f[idx[0]]
print(f"numerical -3 dB BW = {bw/1e6:.4f} MHz; f0/Q = {f0/Q_formula/1e6:.4f} MHz")
assert np.isclose(bw, f0 / Q_formula, rtol=2e-3)
# energy definition: Q = w0 * (peak stored energy) / (average power loss)
I_pk = 1.0
W_stored = 0.5 * L * I_pk**2   # at resonance total stored energy is constant = peak inductor energy
P_loss = 0.5 * I_pk**2 * R
print(f"energy Q = w0*W/P = {w0*W_stored/P_loss:.2f}")
assert np.isclose(w0 * W_stored / P_loss, Q_formula)

print("\n=== 2. Parallel RLC, loaded Q ===")
Qu_ind = 50.0
X0 = w0 * L
Rp_tank = Qu_ind * X0          # parallel loss resistance representing inductor loss
Rsrc = Rload = 1000.0           # effective (e.g. tapped/transformed) source and load resistances
Rext = 1 / (1/Rsrc + 1/Rload)
Qu = Rp_tank / X0
Qe = Rext / X0
QL = 1 / (1/Qu + 1/Qe)
Rtot = 1 / (1/Rp_tank + 1/Rext)
print(f"Rp(tank) = {Rp_tank:.1f} ohm, Qu = {Qu:.2f}, Qe = {Qe:.3f}, QL = {QL:.3f}, check Rtot/X0 = {Rtot/X0:.3f}")
assert np.isclose(QL, Rtot / X0)
# numerical BW of the parallel resonator between Rsrc and Rload
Ytank = 1/Rp_tank + 1/(1j*w*L) + 1j*w*C
Zp = 1 / (Ytank + 1/Rload)
Vl = Zp / (Rsrc + Zp)          # source EMF = 1
PL = np.abs(Vl)**2 / Rload
Pav = 1 / (4 * Rsrc)
T = PL / Pav
idx = np.where(T >= T.max() / 2)[0]
bwp = f[idx[-1]] - f[idx[0]]
print(f"parallel: numerical BW = {bwp/1e6:.3f} MHz vs f0/QL = {f0/QL/1e6:.3f} MHz")
assert np.isclose(bwp, f0 / QL, rtol=5e-3)

print("\n=== 3. Insertion loss at resonance vs QL/Qu ===")
IL_num = -10 * np.log10(T.max())
IL_formula = -20 * np.log10(1 - QL / Qu)
print(f"IL numerical = {IL_num:.4f} dB, -20log10(1-QL/Qu) = {IL_formula:.4f} dB")
assert np.isclose(IL_num, IL_formula, atol=1e-3)
print("  table of IL for a single resonator:")
for ratio in [0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5]:
    print(f"   QL/Qu = {ratio:4.2f}: IL = {-20*np.log10(1-ratio):.3f} dB")

print("\n=== 4. Component-limited tank Q ===")
for QLind, QCap in [(50, 500), (50, 100), (30, 1000), (100, 300)]:
    print(f"  Q_inductor={QLind}, Q_capacitor={QCap}: Qu = {1/(1/QLind + 1/QCap):.1f}")

print("\n=== 5. L-section matching Q ===")
for Rhi, Rlo in [(50, 5.06), (50, 12.5), (200, 50), (50, 25)]:
    Qm = np.sqrt(Rhi / Rlo - 1)
    print(f"  {Rhi} -> {Rlo} ohm: Q = {Qm:.3f}, approx fractional BW ~ 1/Q ... 2/Q (doubly loaded) = {1/Qm*100:.0f}% .. {2/Qm*100:.0f}%")

print("\n=== 6. Group delay of the resonator at f0 ===")
H = Vl
phase = np.unwrap(np.angle(H))
tau = -np.gradient(phase, w)
i0 = np.argmin(np.abs(f - f0))
print(f"  numerical tau(f0) = {tau[i0]*1e9:.3f} ns; 2QL/w0 = {2*QL/w0*1e9:.3f} ns")
assert np.isclose(tau[i0], 2 * QL / w0, rtol=1e-3)

print("\n=== 7. Series->parallel conversion reminder (Q = 50 inductor at 433.92 MHz) ===")
Rs = X0 / 50
print(f"  Rs = {Rs:.3f} ohm -> Rp = Rs(1+Q^2) = {Rs*(1+2500):.1f} ohm")
print("OK")

print("\n=== 8. L-match bandwidth check: loaded Q ~ Qn/2 -> fractional BW ~ 2/Qn ===")
f0 = 433.92e6; w0 = TP * f0
for Rhi, Rlo in [(50.0, 5.0), (50.0, 2.0), (50.0, 0.5)]:
    Qn = np.sqrt(Rhi / Rlo - 1)
    Xs = Qn * Rlo            # series inductor on low side
    Xp = Rhi / Qn            # shunt capacitor on high side
    Ls = Xs / w0; Cp = 1 / (w0 * Xp)
    f = np.linspace(0.2 * f0, 1.8 * f0, 200001); w = TP * f
    # source Rhi, shunt Cp at source node, series Ls to load Rlo
    Zload = Rlo + 1j * w * Ls
    Zin = 1 / (1j * w * Cp + 1 / Zload)
    G = (Zin - Rhi) / (Zin + Rhi)
    T = 1 - np.abs(G)**2      # lossless network -> transmitted fraction
    idx = np.where(T >= 0.5)[0]
    fbw = (f[idx[-1]] - f[idx[0]]) / f0
    print(f"  {Rhi}->{Rlo} ohm: Qn = {Qn:.2f}, numerical 3-dB fractional BW = {fbw*100:.1f}%, 2/Qn = {2/Qn*100:.1f}%")
print("OK (L-match)")
