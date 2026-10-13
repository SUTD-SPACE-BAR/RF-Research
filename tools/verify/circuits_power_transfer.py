#!/usr/bin/env python3
"""
Verification for kb/01-circuit-theory/network-theorems-max-power-transfer.md

Checks:
  1. Nodal analysis of a small network by matrix solve; Thevenin/Norton extraction; load power agrees.
  2. Superposition: two sources, sum of individual responses equals the full solution.
  3. Maximum power transfer for resistive and complex sources; efficiency = 50 % at match.
  4. Power-wave mismatch factor 1-|Gamma_p|^2 equals P_L/P_avail for arbitrary complex Zs, ZL.
  5. PA load-line example: why a 2 W PA is not conjugate matched.
  6. Noise-match vs gain-match illustration with the standard two-port noise equation (hypothetical device).
Run:  python3 tools/verify/circuits_power_transfer.py
"""
import numpy as np

print("=== 1. Nodal analysis + Thevenin/Norton ===")
# Network: Vs=10 V with Rs1=100 ohm into node 1; R12 = 50 ohm between node1 and node2;
# R1g = 200 ohm node1->gnd; load terminals at node 2 to ground; R2g = 300 ohm node2->gnd.
Vs, Rs1, R12, R1g, R2g = 10.0, 100.0, 50.0, 200.0, 300.0
def solve(RL=None, I_inj2=0.0):
    G = np.array([[1/Rs1 + 1/R12 + 1/R1g, -1/R12],
                  [-1/R12, 1/R12 + 1/R2g + (0 if RL is None else 1/RL)]])
    I = np.array([Vs/Rs1, I_inj2])
    return np.linalg.solve(G, I)
Voc = solve()[1]
# short-circuit current: RL -> tiny
Isc = solve(RL=1e-9)[1] / 1e-9
Rth = Voc / Isc
print(f"Voc = {Voc:.5f} V, Isc = {Isc*1e3:.5f} mA, Rth = {Rth:.4f} ohm")
# Rth by source-killing: node2 impedance with Vs shorted
Rth_kill = 1 / (1/R2g + 1/(R12 + 1/(1/Rs1 + 1/R1g)))
print(f"Rth by killing sources = {Rth_kill:.4f} ohm")
assert np.isclose(Rth, Rth_kill, rtol=1e-6)
for RL in [10, Rth, 500]:
    V2 = solve(RL=RL)[1]
    P_full = V2**2 / RL
    P_thev = (Voc * RL / (Rth + RL))**2 / RL
    print(f"RL={RL:8.3f}: P(full network)={P_full*1e3:.5f} mW, P(Thevenin)={P_thev*1e3:.5f} mW")
    assert np.isclose(P_full, P_thev, rtol=1e-6)

print("\n=== 2. Superposition ===")
I2 = 5e-3  # extra current source into node 2
v_both = solve(RL=75, I_inj2=I2)[1]
# Vs only
v_vs = solve(RL=75, I_inj2=0.0)[1]
# I only (set Vs=0)
Vs_save = Vs; Vs = 0.0
v_i = solve(RL=75, I_inj2=I2)[1]
Vs = Vs_save
print(f"V2(both)={v_both:.6f}, V2(Vs)+V2(I)={v_vs+v_i:.6f}")
assert np.isclose(v_both, v_vs + v_i)
# power does NOT superpose
p_both = v_both**2/75; p_sum = v_vs**2/75 + v_i**2/75
print(f"P(both)={p_both*1e3:.4f} mW vs P(Vs)+P(I)={p_sum*1e3:.4f} mW  -> power does not superpose")

print("\n=== 3. Maximum power transfer ===")
Vs_pk, Rs = 1.0, 50.0  # 1 V peak open-circuit source, 50 ohm
Pav = Vs_pk**2 / (8 * Rs)
print(f"available power = Vs^2/(8Rs) = {Pav*1e3:.3f} mW (peak phasor convention)")
for RL in [5, 25, 50, 100, 500]:
    I = Vs_pk / (Rs + RL)
    PL = 0.5 * abs(I)**2 * RL
    Ps = 0.5 * abs(I)**2 * Rs
    eta = PL / (PL + Ps)
    print(f"RL={RL:4d}: PL={PL*1e3:7.3f} mW ({PL/Pav*100:5.1f}% of Pav), efficiency={eta*100:5.1f}%")
# complex source
Zs = complex(10, 20)
best = None
for R in np.linspace(1, 40, 391):
    for X in np.linspace(-40, 0, 401):
        ZL = complex(R, X)
        I = Vs_pk / (Zs + ZL)
        PL = 0.5 * abs(I)**2 * ZL.real
        if best is None or PL > best[0]:
            best = (PL, ZL)
print(f"Zs={Zs}: brute-force optimum ZL = {best[1].real:.2f}{best[1].imag:+.2f}j (expect conj = 10-20j), "
      f"PL={best[0]*1e3:.4f} mW vs Pav=Vs^2/(8Re Zs)={Vs_pk**2/(8*Zs.real)*1e3:.4f} mW")

print("\n=== 4. Power-wave mismatch factor ===")
rng = np.random.default_rng(1)
for _ in range(5):
    Zs = complex(rng.uniform(1, 100), rng.uniform(-100, 100))
    ZL = complex(rng.uniform(1, 100), rng.uniform(-100, 100))
    I = 1.0 / (Zs + ZL)
    PL = 0.5 * abs(I)**2 * ZL.real
    Pav = 1.0 / (8 * Zs.real)
    Gp = (ZL - np.conj(Zs)) / (ZL + Zs)
    M = 1 - abs(Gp)**2
    # Kurokawa form of mismatch factor
    M2 = 4 * Zs.real * ZL.real / abs(Zs + ZL)**2
    print(f"Zs={Zs:.1f} ZL={ZL:.1f}: PL/Pav={PL/Pav:.6f}, 1-|Gp|^2={M:.6f}, 4RsRL/|Zs+ZL|^2={M2:.6f}")
    assert np.isclose(PL / Pav, M) and np.isclose(M, M2)

print("\n=== 5. PA load-line vs conjugate match ===")
Vdd, Vknee = 5.0, 0.5
Pout_target = 2.0  # W (33 dBm, like an E22-400T33D class module)
Ropt = (Vdd - Vknee)**2 / (2 * Pout_target)
Imax = 2 * (Vdd - Vknee) / Ropt  # class-A/B peak current for full swing
print(f"Vdd={Vdd} V, Vknee={Vknee} V, Pout=2 W -> Ropt=(Vdd-Vk)^2/(2P) = {Ropt:.2f} ohm, peak RF current ~ {(Vdd-Vknee)/Ropt:.2f} A")
Rout = 200.0  # assumed transistor output (small-signal) resistance
for RL in [Ropt, 50.0, Rout]:
    # voltage-limited or current-limited
    Ipk_lim = (Vdd - Vknee) / Ropt  # device current limit, set by Ropt design
    Vpk = min(Vdd - Vknee, Ipk_lim * RL)
    P = Vpk**2 / (2 * RL)
    print(f"  RL={RL:6.2f} ohm: max Pout={P:.3f} W ({10*np.log10(P*1e3):.1f} dBm)")
print("  -> conjugate matching to the 200 ohm output resistance gives ~50 mW, not 2 W.")
print(f"  50 ohm -> {Ropt:.2f} ohm transformation ratio = {50/Ropt:.1f}:1")

print("\n=== 6. Noise match vs gain match (hypothetical LNA) ===")
Z0 = 50.0
Fmin_dB, Rn = 0.5, 15.0
Gopt = 0.35 * np.exp(1j * np.radians(55))
S11 = 0.80 * np.exp(-1j * np.radians(40))
def F_of(Gs):
    Fmin = 10**(Fmin_dB / 10)
    return Fmin + 4 * Rn / Z0 * abs(Gs - Gopt)**2 / ((1 - abs(Gs)**2) * abs(1 + Gopt)**2)
for name, Gs in [("Gs = Gamma_opt (noise match)", Gopt), ("Gs = S11* (input conj match, unilateral)", np.conj(S11)),
                 ("Gs = 0 (plain 50 ohm)", 0)]:
    F = F_of(Gs)
    Min = (1 - abs(Gs)**2) * (1 - abs(S11)**2) / abs(1 - S11 * Gs)**2  # unilateral input mismatch factor
    print(f"  {name:42s}: NF = {10*np.log10(F):.2f} dB, input mismatch factor = {10*np.log10(Min):.2f} dB")
print("OK")
