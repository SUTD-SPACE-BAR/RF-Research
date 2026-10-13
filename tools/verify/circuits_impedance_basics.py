#!/usr/bin/env python3
"""
Verification for kb/01-circuit-theory/lumped-elements-impedance-admittance.md

Checks:
  1. Reactance table of common RF values at the reader's bands (433, 868, 915, 1575.42, 2450 MHz).
  2. Series <-> parallel (impedance <-> admittance) conversion, exact and high-Q approximation.
  3. Worked examples used on the page (antenna-like load 30 - j40 ohm at 433 MHz, etc.).
  4. Element value that gives a target reactance (e.g. what C is 1 ohm at 433 MHz: DC-block rule).
Run:  python3 tools/verify/circuits_impedance_basics.py
"""
import numpy as np

TWO_PI = 2 * np.pi
bands = {"433 MHz": 433.92e6, "868 MHz": 868e6, "915 MHz": 915e6,
         "GPS L1": 1575.42e6, "2.45 GHz": 2450e6}


def XL(L, f):
    return TWO_PI * f * L


def XC(C, f):
    return 1.0 / (TWO_PI * f * C)


print("=== 1. Reactance table (ohms) ===")
Ls = [1e-9, 3.3e-9, 10e-9, 33e-9, 100e-9, 1e-6]
Cs = [0.5e-12, 1e-12, 3.3e-12, 10e-12, 33e-12, 100e-12, 1e-9, 100e-9]
hdr = "value".ljust(10) + "".join(k.rjust(11) for k in bands)
print(hdr)
for L in Ls:
    print(f"{L*1e9:6.1f} nH ".ljust(10) + "".join(f"{XL(L,f):11.2f}" for f in bands.values()))
for C in Cs:
    lab = f"{C*1e12:6.1f} pF " if C < 1e-9 else f"{C*1e9:6.0f} nF "
    print(lab.ljust(10) + "".join(f"{XC(C,f):11.3f}" for f in bands.values()))

print("\n=== 2. Element giving |X| = 50 ohm and 1 ohm at each band ===")
for k, f in bands.items():
    L50 = 50 / (TWO_PI * f)
    C50 = 1 / (TWO_PI * f * 50)
    C1 = 1 / (TWO_PI * f * 1.0)
    print(f"{k:9s}: L(50R)={L50*1e9:6.2f} nH  C(50R)={C50*1e12:6.2f} pF  C(|X|=1R)={C1*1e12:7.1f} pF")

print("\n=== 3. Series <-> parallel conversion ===")
def ser2par(R, X):
    Z = complex(R, X)
    Y = 1 / Z
    Rp = 1 / Y.real
    Xp = -1 / Y.imag if Y.imag != 0 else np.inf  # parallel reactance (X_p) such that 1/(jXp) = j*Im(Y)... sign handled below
    # Y = G + jB ; a parallel reactance X_p has admittance 1/(j X_p) = -j/X_p  => B = -1/X_p => X_p = -1/B
    return Rp, Xp, Y

for (R, X) in [(50, 30), (30, -40), (1, 100), (0.5, 50)]:
    Rp, Xp, Y = ser2par(R, X)
    Q = abs(X) / R
    print(f"Zs = {R}+j{X}: Y = {Y.real*1e3:.4f} + j{Y.imag*1e3:.4f} mS ; Rp = {Rp:.2f} ohm, Xp = {Xp:.3f} ohm ;"
          f" Q={Q:.2f}; high-Q approx Rp~R*Q^2={R*Q**2:.1f}, Xp~X={X}")
    # exact identities
    assert np.isclose(Rp, R * (1 + Q**2))
    assert np.isclose(Xp, X * (1 + 1 / Q**2))

print("\n=== 4. Worked example: Z = 30 - j40 ohm at 433.92 MHz (short monopole-like load) ===")
f = bands["433 MHz"]
Z = complex(30, -40)
Y = 1 / Z
print(f"|Z| = {abs(Z):.1f} ohm, angle = {np.degrees(np.angle(Z)):.2f} deg")
print(f"Y = {Y.real*1e3:.3f} mS + j{Y.imag*1e3:.3f} mS  (G = {Y.real*1e3:.2f} mS, B = {Y.imag*1e3:.2f} mS)")
C_eq = 1 / (TWO_PI * f * 40)
print(f"series-equivalent capacitance of -j40 at 433.92 MHz: {C_eq*1e12:.2f} pF")
L_cancel = 40 / (TWO_PI * f)
print(f"series inductor to cancel -j40: {L_cancel*1e9:.2f} nH -> leaves 30 ohm")
# parallel form
Rp, Xp, _ = ser2par(30, -40)
print(f"parallel form: Rp = {Rp:.2f} ohm || Xp = {Xp:.2f} ohm (C_par = {1/(TWO_PI*f*abs(Xp))*1e12:.2f} pF)")

print("\n=== 5. Series RLC and parallel RLC impedance at a few frequencies ===")
R, L, C = 2.0, 22e-9, 6.1e-12
f0 = 1 / (TWO_PI * np.sqrt(L * C))
print(f"series R={R} L=22nH C=6.1pF : f0 = {f0/1e6:.2f} MHz")
for fr in [0.5, 0.9, 1.0, 1.1, 2.0]:
    w = TWO_PI * f0 * fr
    Zs = R + 1j * w * L + 1 / (1j * w * C)
    print(f"  f/f0={fr:4.2f}: Zs = {Zs.real:.2f} + j{Zs.imag:.2f} ohm")

print("\n=== 6. Units sanity: 1 nH at 1 GHz = 6.283 ohm; 1 pF at 1 GHz = 159.15 ohm ===")
assert np.isclose(XL(1e-9, 1e9), 6.2832, atol=1e-3)
assert np.isclose(XC(1e-12, 1e9), 159.155, atol=1e-2)
print("OK")
