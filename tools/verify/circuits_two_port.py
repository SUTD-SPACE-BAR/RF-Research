#!/usr/bin/env python3
"""
Verification for kb/01-circuit-theory/two-port-networks-zyh-abcd.md

  1. Z <-> Y <-> h <-> ABCD conversion formulas (as written on the page) vs scikit-rf, on random networks.
  2. Cascading: ABCD product == scikit-rf cascade; T-matrix product (scikit-rf convention).
  3. Property tests: reciprocity (Z12=Z21, AD-BC=1, S12=S21), symmetry (Z11=Z22, A=D),
     losslessness (Re Z = 0 for all entries; S^H S = I).
  4. Worked examples: 3 dB pi attenuator; series-L/shunt-C L-section at 433.92 MHz;
     common-emitter hybrid parameters -> Z, Y, input impedance and voltage gain.
Run: python3 tools/verify/circuits_two_port.py
"""
import numpy as np
import skrf as rf
from skrf import network as nw

rng = np.random.default_rng(7)
Z0 = 50.0

# ------------------------------------------------------------ conversions from the page
def z2y(Z): return np.linalg.inv(Z)
def z2abcd(Z):
    z11, z12, z21, z22 = Z[0, 0], Z[0, 1], Z[1, 0], Z[1, 1]
    dZ = z11 * z22 - z12 * z21
    return np.array([[z11 / z21, dZ / z21], [1 / z21, z22 / z21]])
def abcd2z(M):
    A, B, C, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
    return np.array([[A / C, (A * D - B * C) / C], [1 / C, D / C]])
def z2h(Z):
    z11, z12, z21, z22 = Z[0, 0], Z[0, 1], Z[1, 0], Z[1, 1]
    dZ = z11 * z22 - z12 * z21
    return np.array([[dZ / z22, z12 / z22], [-z21 / z22, 1 / z22]])
def h2z(H):
    h11, h12, h21, h22 = H[0, 0], H[0, 1], H[1, 0], H[1, 1]
    dH = h11 * h22 - h12 * h21
    return np.array([[dH / h22, h12 / h22], [-h21 / h22, 1 / h22]])
def abcd2s(M, z0=Z0):
    A, B, C, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
    den = A + B / z0 + C * z0 + D
    return np.array([[(A + B / z0 - C * z0 - D) / den, 2 * (A * D - B * C) / den],
                     [2 / den, (-A + B / z0 - C * z0 + D) / den]])

print("=== 1. Conversions vs scikit-rf (random complex networks) ===")
maxerr = 0
for _ in range(200):
    Z = rng.normal(0, 50, (2, 2)) + 1j * rng.normal(0, 50, (2, 2))
    Z[0, 0] += 60; Z[1, 1] += 60
    S = nw.z2s(Z[None], z0=Z0)
    maxerr = max(maxerr,
                 np.max(np.abs(z2y(Z) - nw.s2y(S, z0=Z0)[0])) / np.max(np.abs(z2y(Z))),
                 np.max(np.abs(z2abcd(Z) - nw.s2a(S, z0=Z0)[0])) / np.max(np.abs(z2abcd(Z))),
                 np.max(np.abs(z2h(Z) - nw.s2h(S, z0=Z0)[0])) / np.max(np.abs(z2h(Z))),
                 np.max(np.abs(abcd2z(z2abcd(Z)) - Z)) / np.max(np.abs(Z)),
                 np.max(np.abs(h2z(z2h(Z)) - Z)) / np.max(np.abs(Z)),
                 np.max(np.abs(abcd2s(z2abcd(Z)) - S[0])))
print(f"max relative error over 200 random networks = {maxerr:.2e}")
assert maxerr < 1e-9

# remaining table entries: ABCD<->h, ABCD->Y, h->Y, and Pi/T ABCD closed forms
for _ in range(50):
    Z = rng.normal(0, 50, (2, 2)) + 1j * rng.normal(0, 50, (2, 2)); Z[0, 0] += 60; Z[1, 1] += 60
    M = z2abcd(Z); H = z2h(Z); Y = z2y(Z)
    A, B, C, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]; dA = A * D - B * C
    h11, h12, h21, h22 = H[0, 0], H[0, 1], H[1, 0], H[1, 1]; dH = h11 * h22 - h12 * h21
    assert np.allclose(M, np.array([[-dH, -h11], [-h22, -1]]) / h21)
    assert np.allclose(H, np.array([[B, dA], [-1, C]]) / D)
    assert np.allclose(Y, np.array([[D, -dA], [-1, A]]) / B)
    assert np.allclose(Y, np.array([[1, -h12], [h21, dH]]) / h11)
    Y1, Y2, Z3 = rng.normal(size=3) + 1j * rng.normal(size=3)
    Pi = np.array([[1, 0], [Y1, 1]]) @ np.array([[1, Z3], [0, 1]]) @ np.array([[1, 0], [Y2, 1]])
    assert np.allclose(Pi, [[1 + Y2 * Z3, Z3], [Y1 + Y2 + Y1 * Y2 * Z3, 1 + Y1 * Z3]])
    Z1, Z2, Y3 = rng.normal(size=3) + 1j * rng.normal(size=3)
    Tn = np.array([[1, Z1], [0, 1]]) @ np.array([[1, 0], [Y3, 1]]) @ np.array([[1, Z2], [0, 1]])
    assert np.allclose(Tn, [[1 + Z1 * Y3, Z1 + Z2 + Z1 * Z2 * Y3], [Y3, 1 + Z2 * Y3]])
print("table entries ABCD<->h, ABCD->Y, h->Y, Pi and T closed forms: verified")

print("\n=== 2. Cascading ===")
freq = rf.Frequency(433.92, 433.92, 1, unit="MHz")
def random_net():
    Z = rng.normal(0, 40, (2, 2)) + 1j * rng.normal(0, 40, (2, 2)); Z[0, 0] += 70; Z[1, 1] += 70
    return rf.Network(frequency=freq, s=nw.z2s(Z[None], z0=Z0), z0=Z0)
n1, n2, n3 = random_net(), random_net(), random_net()
casc = n1 ** n2 ** n3
A_prod = nw.s2a(n1.s, Z0)[0] @ nw.s2a(n2.s, Z0)[0] @ nw.s2a(n3.s, Z0)[0]
print(f"|ABCD(cascade) - ABCD1*ABCD2*ABCD3| = {np.max(np.abs(nw.s2a(casc.s, Z0)[0] - A_prod)):.2e}")
assert np.allclose(nw.s2a(casc.s, Z0)[0], A_prod)
T_prod = nw.s2t(n1.s)[0] @ nw.s2t(n2.s)[0] @ nw.s2t(n3.s)[0]
print(f"|T(cascade) - T1*T2*T3| (scikit-rf T convention) = {np.max(np.abs(nw.s2t(casc.s)[0] - T_prod)):.2e}")
assert np.allclose(nw.s2t(casc.s)[0], T_prod)

print("\n=== 3. Properties ===")
# reciprocal: symmetric Z
Zr = np.array([[30 + 10j, 12 - 5j], [12 - 5j, 45 + 2j]])
M = z2abcd(Zr); S = abcd2s(M)
print(f"reciprocal: AD-BC = {M[0,0]*M[1,1]-M[0,1]*M[1,0]:.6f}, S12-S21 = {abs(S[0,1]-S[1,0]):.2e}")
# lossless reactive network: series jX1, shunt jB
w = 2 * np.pi * 433.92e6
L, C = 22e-9, 6.1e-12
Ml = np.array([[1, 1j * w * L], [0, 1]]) @ np.array([[1, 0], [1j * w * C, 1]])
Sl = abcd2s(Ml); Zl = abcd2z(Ml)
print(f"lossless L-section: max|Re Z| = {np.max(np.abs(Zl.real)):.2e}; ||S^H S - I|| = {np.linalg.norm(Sl.conj().T@Sl-np.eye(2)):.2e}")
print(f"  A = {Ml[0,0]:.4f} (real), B = {Ml[0,1]:.4f} (imag), C = {Ml[1,0]:.6f} (imag), D = {Ml[1,1]:.4f} (real)")
assert np.allclose(Sl.conj().T @ Sl, np.eye(2))
ZL = 50.0
Zin = (Ml[0, 0] * ZL + Ml[0, 1]) / (Ml[1, 0] * ZL + Ml[1, 1])
Zin2 = Zl[0, 0] - Zl[0, 1] * Zl[1, 0] / (Zl[1, 1] + ZL)
print(f"  Zin with 50 ohm load: (A ZL + B)/(C ZL + D) = {Zin:.3f}; Z11 - Z12Z21/(Z22+ZL) = {Zin2:.3f}")
assert np.isclose(Zin, Zin2)

print("\n=== 4a. 3 dB pi attenuator (50 ohm) ===")
K = 10**(3 / 20)
Rsh = Z0 * (K + 1) / (K - 1); Rse = Z0 * (K**2 - 1) / (2 * K)
Mp = np.array([[1, 0], [1 / Rsh, 1]]) @ np.array([[1, Rse], [0, 1]]) @ np.array([[1, 0], [1 / Rsh, 1]])
Sp = abcd2s(Mp)
print(f"Rshunt = {Rsh:.2f} ohm, Rseries = {Rse:.2f} ohm; A=D? {np.isclose(Mp[0,0],Mp[1,1])}; AD-BC={np.linalg.det(Mp):.6f}")
print(f"S11 = {abs(Sp[0,0]):.2e}, S21 = {20*np.log10(abs(Sp[1,0])):.3f} dB; image impedance sqrt(B/C) = {np.sqrt(Mp[0,1]/Mp[1,0]).real:.3f} ohm")

print("\n=== 4b. Common-emitter hybrid parameters ===")
H = np.array([[2500.0, 2e-4], [100.0, 20e-6]])   # hie, hre ; hfe, hoe
Zh = h2z(H)
Yh = np.linalg.inv(Zh)
print(f"Z = {np.round(Zh,2)}")
print(f"Y (mS) = {np.round(Yh*1e3,5)}")
RL = 2000.0
# voltage gain Av = -hfe RL / (hie + (hie hoe - hfe hre) RL)
dH = H[0, 0] * H[1, 1] - H[0, 1] * H[1, 0]
Av = -H[1, 0] * RL / (H[0, 0] + dH * RL)
Zin_h = H[0, 0] - H[0, 1] * H[1, 0] * RL / (1 + H[1, 1] * RL)
Zin_z = Zh[0, 0] - Zh[0, 1] * Zh[1, 0] / (Zh[1, 1] + RL)
print(f"RL = 2 kohm: Av = {Av:.2f}, Zin(h) = {Zin_h:.2f} ohm, Zin(z) = {Zin_z:.2f} ohm; non-reciprocal: Z12 != Z21 ({Zh[0,1]:.2f} vs {Zh[1,0]:.0f})")
assert np.isclose(Zin_h, Zin_z)
print("OK")
