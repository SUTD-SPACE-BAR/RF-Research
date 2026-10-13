#!/usr/bin/env python3
"""
Verification for kb/01-circuit-theory/transformers-coupled-inductors.md

  1. Coupled-inductor equations vs T-equivalent (L1-M, L2-M, M) and vs the "cantilever" model
     (leakage L1(1-k^2) + magnetising k^2 L1 + ideal n_eff = k sqrt(L1/L2)).
  2. Ideal-transformer limit: Zin -> n^2 ZL as k->1, L->inf.
  3. Wideband RF transformer example (1:4 impedance) - low/high frequency -3 dB limits.
  4. Capacitive divider (tapped-C) impedance transformation: exact vs R(1+C2/C1)^2 approximation.
  5. Tapped inductor (autotransformer) transformation, tight vs loose coupling.
  6. Two coupled resonators: split frequencies and k = (fh^2 - fl^2)/(fh^2 + fl^2).
Run: python3 tools/verify/circuits_transformers.py
"""
import numpy as np
TP = 2 * np.pi

def zin_coupled(L1, L2, k, ZL, w, R1=0.0, R2=0.0):
    M = k * np.sqrt(L1 * L2)
    Z11 = R1 + 1j * w * L1; Z22 = R2 + 1j * w * L2; Z12 = 1j * w * M
    return Z11 - Z12**2 / (Z22 + ZL)

print("=== 1. Coupled inductors: three equivalent models ===")
L1, L2, k = 1e-6, 4e-6, 0.95
M = k * np.sqrt(L1 * L2)
ZL = 200.0
for f in [1e6, 10e6, 100e6]:
    w = TP * f
    z_c = zin_coupled(L1, L2, k, ZL, w)
    # T-equivalent
    zT = 1j * w * (L1 - M) + 1 / (1 / (1j * w * M) + 1 / (1j * w * (L2 - M) + ZL))
    # cantilever: leakage + (magnetising || ideal transformer with n_eff)
    neff = k * np.sqrt(L1 / L2)
    Lleak = L1 * (1 - k**2); Lm = k**2 * L1
    zC = 1j * w * Lleak + 1 / (1 / (1j * w * Lm) + 1 / (neff**2 * ZL))
    print(f"f={f/1e6:6.1f} MHz: coupled {z_c:.3f}, T-equiv {zT:.3f}, cantilever {zC:.3f}")
    assert np.isclose(z_c, zT) and np.isclose(z_c, zC)
print(f"n_eff = k*sqrt(L1/L2) = {k*np.sqrt(L1/L2):.4f} (turns ratio 1:2 would be 0.5)")

print("\n=== 2. Ideal transformer limit ===")
for kk, scale in [(0.9, 1), (0.99, 10), (0.999, 100), (0.99999, 1000)]:
    z = zin_coupled(L1 * scale, L2 * scale, kk, ZL, TP * 10e6)
    print(f"k={kk}, L x{scale}: Zin = {z:.3f}  (n^2 ZL = {(0.5**2)*ZL:.1f})")

print("\n=== 3. 1:4 wideband transformer (1:2 turns) between 50 and 200 ohm ===")
L1 = 2.0e-6; L2 = 4 * L1; k = 0.995; Rs = 50.0; RL = 200.0
f = np.logspace(4, 9, 5001); w = TP * f
Zin = zin_coupled(L1, L2, k, RL, w)
G = (Zin - Rs) / (Zin + Rs)
T = 1 - np.abs(G)**2
TdB = 10 * np.log10(T)
band = f[TdB > -3.0103]
Lm = k**2 * L1; Lleak = L1 * (1 - k**2)
R_par = 1 / (1 / Rs + 1 / (RL / 4))  # source in parallel with reflected load (both 50)
fL_est = R_par / (TP * Lm)
fH_est = (Rs + RL / 4) / (TP * Lleak)
print(f"Lm = {Lm*1e6:.3f} uH, Lleak = {Lleak*1e9:.2f} nH")
print(f"numerical -3 dB band: {band[0]/1e3:.1f} kHz .. {band[-1]/1e6:.1f} MHz")
print(f"estimates: f_low = (Rs||RL')/(2 pi Lm) = {fL_est/1e3:.1f} kHz ; f_high = (Rs+RL')/(2 pi Lleak) = {fH_est/1e6:.1f} MHz")

print("\n=== 4. Capacitive divider (tapped C) ===")
f0 = 433.92e6; w0 = TP * f0
C1, C2 = 2.0e-12, 20.0e-12      # top (C1) and bottom (C2); load R across C2
R = 50.0
Y = 1 / (1 / (1j * w0 * C1) + 1 / (1j * w0 * C2 + 1 / R))
Rp_exact = 1 / Y.real
Cp_exact = Y.imag / w0
Rp_approx = R * (1 + C2 / C1)**2
Ceq = C1 * C2 / (C1 + C2)
QR = w0 * C2 * R
print(f"C1={C1*1e12} pF, C2={C2*1e12} pF, R={R}: Q of (C2||R) = {QR:.2f}")
print(f"  exact: Rp = {Rp_exact:.1f} ohm, Cp = {Cp_exact*1e12:.3f} pF ; approx R(1+C2/C1)^2 = {Rp_approx:.1f} ohm, Ceq = {Ceq*1e12:.3f} pF")
C1b, C2b = 1.0e-12, 30e-12
Y = 1 / (1 / (1j * w0 * C1b) + 1 / (1j * w0 * C2b + 1 / R))
print(f"  C1=1 pF, C2=30 pF (Q={w0*C2b*R:.2f}): exact Rp = {1/Y.real:.1f} vs approx {R*(1+C2b/C1b)**2:.1f} ohm")

print("\n=== 5. Tapped inductor (autotransformer) ===")
Ltot = 100e-9; tap = 0.2   # tap at 20 % of turns from ground
for kk in [0.999, 0.8, 0.5]:
    La = Ltot * tap**2 / (tap**2 + (1 - tap)**2 + 2 * kk * tap * (1 - tap))   # placeholder, recomputed below
    # sections: bottom (tap) winding Lb and top winding Lt with mutual coupling k; for a uniformly wound
    # tightly coupled coil L ~ N^2, so Lb = tap^2 * L0, Lt = (1-tap)^2 * L0, with total Ltot = Lb+Lt+2M
    L0 = Ltot / (tap**2 + (1 - tap)**2 + 2 * kk * tap * (1 - tap))
    Lb = tap**2 * L0; Lt = (1 - tap)**2 * L0; Mbt = kk * np.sqrt(Lb * Lt)
    Rload = 50.0
    w = TP * 100e6
    # load across bottom section (tap to ground); look into top of coil (top to ground)
    # port1: top-to-ground current I1 flows through Lt then Lb ; port2: load across Lb
    # Z-matrix: Z11 = jw(Lt+Lb+2M), Z12 = Z21 = jw(Lb+M), Z22 = jw Lb
    Z11 = 1j * w * (Lt + Lb + 2 * Mbt); Z12 = 1j * w * (Lb + Mbt); Z22 = 1j * w * Lb
    Zin = Z11 - Z12**2 / (Z22 + Rload)
    # parallel equivalent
    Rp = 1 / (1 / Zin).real
    print(f"  k={kk}: Lb={Lb*1e9:.2f} nH, Lt={Lt*1e9:.2f} nH -> Rp seen at top = {Rp:.0f} ohm (ideal (1/tap)^2*R = {Rload/tap**2:.0f})")

print("\n=== 6. Coupled resonators: mode splitting ===")
L = 22e-9; C = 1 / ((TP * 433.92e6)**2 * L)
for kk in [0.01, 0.05, 0.1]:
    Mm = kk * L
    # symmetric pair: even/odd modes at 1/sqrt((L +/- M) C)
    fe = 1 / (TP * np.sqrt((L + Mm) * C)); fo = 1 / (TP * np.sqrt((L - Mm) * C))
    # numerically: eigenfrequencies of [L M; M L] C system
    Lmat = np.array([[L, Mm], [Mm, L]])
    ev = np.linalg.eigvals(np.linalg.inv(Lmat) / C)
    fnum = np.sort(np.sqrt(ev.real)) / TP
    kest = (fo**2 - fe**2) / (fo**2 + fe**2)
    print(f"  k={kk}: modes {fnum[0]/1e6:.2f} / {fnum[1]/1e6:.2f} MHz (formula {fe/1e6:.2f}/{fo/1e6:.2f}); k from split = {kest:.4f}")
    assert np.isclose(kest, kk)
print("OK")
