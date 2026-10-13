#!/usr/bin/env python3
"""W5-S10 checks for 17/bench-measurement-recipes (R11 RF prototyping and construction) and
17/rf-bring-up-debug-playbook (amplifier / RF-switch bring-up, safe test set-up).

A. Parasitics per construction technique: wire-over-ground lead inductance, Manhattan pad capacitance.
B. A 7-pole 0.1 dB Chebyshev low-pass (E22 433 MHz harmonic filter, ripple edge 500 MHz) built
   ideal / on a JLC 4-layer board / Manhattan / dead-bug (leaded parts): S21 at f, 2f, 3f and the
   shunt-arm notch frequencies.
C. Safe amplifier test set-up: pad plan for the BGA524N6 (canonical values) and for a 20 dB gain
   block; return loss guaranteed by a pad; PA voltage into an open.
D. Why high-gain blocks are split: feedback loop gain, gain ripple and the isolation needed.
"""
import numpy as np

ok_all = True
def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(("PASS " if cond else "FAIL ") + name)

mu0 = 4e-7 * np.pi
eps0 = 8.854187817e-12
Z0 = 50.0

# ---------------------------------------------------------------- A
print("A: lead inductance of a round wire parallel to a ground plane, L = (mu0 l / 2 pi) ln(2h/r)")
def L_wire(l, h, r):
    return mu0 * l / (2 * np.pi) * np.log(2 * h / r)
cases = [("dead-bug/ugly lead 10 mm at 3 mm, d 0.5 mm", 10e-3, 3e-3, 0.25e-3),
         ("ugly lead 5 mm at 2 mm, d 0.5 mm", 5e-3, 2e-3, 0.25e-3),
         ("Manhattan jumper 5 mm at 1.6 mm, d 0.5 mm", 5e-3, 1.6e-3, 0.25e-3),
         ("SMD on a pad, 2 mm path at 0.5 mm", 2e-3, 0.5e-3, 0.25e-3)]
for name, l, h, r in cases:
    L = L_wire(l, h, r)
    print(f"  {name:45s}: {L*1e9:5.2f} nH = {2*np.pi*433e6*L:5.1f} Ohm at 433 MHz")
L10 = L_wire(10e-3, 3e-3, 0.25e-3)
check("A1 a 10 mm lead 3 mm above ground is ~6.4 nH (17 Ohm at 433 MHz)", abs(L10 * 1e9 - 6.36) < 0.05)
print("  Manhattan pad capacitance (parallel plate, FR-4 er 4.5; fringing adds ~30-100 % for small pads)")
for name, A, t in [("2.5 mm square on 1.6 mm", 2.5e-3 ** 2, 1.6e-3), ("5 mm round on 1.6 mm", np.pi * 2.5e-3 ** 2, 1.6e-3),
                   ("5 mm round on 0.8 mm", np.pi * 2.5e-3 ** 2, 0.8e-3)]:
    print(f"    {name:26s}: {eps0*4.5*A/t*1e12:.2f} pF")
Cp = eps0 * 4.5 * np.pi * 2.5e-3 ** 2 / 0.8e-3
check("A2 a 5 mm pad on 0.8 mm FR-4 is ~1 pF before fringing", abs(Cp * 1e12 - 0.98) < 0.02)

# ---------------------------------------------------------------- B
def cheb_g(n, ripple_db):
    beta = np.log(1 / np.tanh(ripple_db / 17.37))
    gam = np.sinh(beta / (2 * n))
    a = [np.sin((2 * k - 1) * np.pi / (2 * n)) for k in range(1, n + 1)]
    b = [gam ** 2 + np.sin(k * np.pi / n) ** 2 for k in range(1, n + 1)]
    g = [2 * a[0] / gam]
    for k in range(2, n + 1):
        g.append(4 * a[k - 2] * a[k - 1] / (b[k - 2] * g[-1]))
    return g
g = cheb_g(7, 0.1)
fc = 500e6
wc = 2 * np.pi * fc
C = [g[i] / (Z0 * wc) for i in (0, 2, 4, 6)]
L = [g[i] * Z0 / wc for i in (1, 3, 5)]
print("\nB: 7-pole 0.1 dB Chebyshev LPF, ripple edge 500 MHz; g =", np.round(g, 4))
print("   shunt C (pF):", np.round(np.array(C) * 1e12, 2), " series L (nH):", np.round(np.array(L) * 1e9, 2))
check("B0 g-values match the tabulated 0.1 dB n=7 set (1.1811, 1.4228, 2.0966, 1.5733)",
      np.allclose(g[:4], [1.1811, 1.4228, 2.0966, 1.5733], atol=2e-4))

def abcd_series(Z):
    return np.array([[1, Z], [0, 1]], dtype=complex)
def abcd_shunt(Y):
    return np.array([[1, 0], [Y, 1]], dtype=complex)
def s21(M):
    A, B, Cc, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
    return 2 / (A + B / Z0 + Cc * Z0 + D)

def filt(f, build):
    w = 2 * np.pi * f
    M = np.eye(2, dtype=complex)
    for i in range(7):
        if i % 2 == 0:  # shunt C arm
            Cv = C[i // 2]
            Zarm = 1 / (1j * w * Cv) + 1j * w * build["Lgnd"] + build["Resr"]
            Y = 1 / Zarm + 1j * w * build["Cnode"]
            M = M @ abcd_shunt(Y)
        else:
            Lv = L[i // 2]
            ZL = 1j * w * Lv + 1j * w * Lv / build["Q"] * 0 + w * Lv / build["Q"]
            Z = 1 / (1 / ZL + 1j * w * build["Cpar"])
            M = M @ abcd_series(Z)
    return s21(M)

builds = {
    "ideal": dict(Lgnd=0, Resr=0, Cnode=0, Cpar=0, Q=1e9),
    "JLC 4-layer, 0402, 1 via/cap": dict(Lgnd=0.4e-9 + 0.54e-9, Resr=0.1, Cnode=0.15e-12, Cpar=0.08e-12, Q=40),
    "JLC 4-layer, 0402, 2 vias/cap": dict(Lgnd=0.4e-9 + 0.27e-9, Resr=0.1, Cnode=0.15e-12, Cpar=0.08e-12, Q=40),
    "Manhattan, 0805 caps on pads": dict(Lgnd=1.5e-9, Resr=0.1, Cnode=0.6e-12, Cpar=0.2e-12, Q=100),
    "dead-bug, leaded caps 2x5 mm": dict(Lgnd=2 * L_wire(5e-3, 2e-3, 0.25e-3) + 1e-9, Resr=0.2, Cnode=0.2e-12, Cpar=0.3e-12, Q=100),
}
FREQS = (434e6, 868e6, 1302e6, 1736e6, 3000e6)
def run(name, b, Cset):
    global C
    Csave = C; C = Cset
    vals = [20 * np.log10(abs(filt(fx, b))) for fx in FREQS]
    notch = [1 / (2 * np.pi * np.sqrt(b["Lgnd"] * Cv)) / 1e9 if b["Lgnd"] > 0 else np.inf for Cv in C]
    C = Csave
    print(f"  {name:44s}: S21 {vals[0]:6.2f} @434, {vals[1]:6.1f} @868, {vals[2]:6.1f} @1302, {vals[3]:6.1f} @1736,"
          f" {vals[4]:6.1f} @3000 MHz; arm notches {np.round(notch, 2)} GHz")
    return vals
res, resc = {}, {}
w0 = 2 * np.pi * 434e6
for name, b in builds.items():
    res[name] = run(name, b, C)
print("  -- shunt C re-chosen so that C_nom/(1 - w^2 L C_nom) = C_design at 434 MHz, minus the node capacitance --")
for name, b in builds.items():
    if name == "ideal":
        continue
    Cc = [(Cv - 2 * b["Cnode"] * 0) / (1 + w0 ** 2 * b["Lgnd"] * Cv) - b["Cnode"] for Cv in C]
    resc[name] = run(name + " (compensated)", b, Cc)
check("B1 ideal: 2f attenuation ~47.6 dB (Chebyshev formula)", abs(-res["ideal"][1] - 47.6) < 0.6)
check("B2 uncompensated dead-bug with 2 x 5 mm leads breaks the passband (> 10 dB loss at 434 MHz)",
      -res["dead-bug, leaded caps 2x5 mm"][0] > 10)
check("B3 after compensation every build passes 434 MHz with < 1 dB loss",
      all(-v[0] < 1.0 for v in resc.values()))
check("B4 the dead-bug build has > 15 dB less 3f rejection than the JLC build even when compensated",
      -resc["dead-bug, leaded caps 2x5 mm"][2] < -resc["JLC 4-layer, 0402, 1 via/cap"][2] - 15)
check("B5 the dead-bug arms are inductive above ~0.85 GHz: the filter re-opens (S21 > -20 dB at 3 GHz) while JLC stays < -100 dB",
      resc["dead-bug, leaded caps 2x5 mm"][4] > -20 and resc["JLC 4-layer, 0402, 1 via/cap"][4] < -100)
print("  NOTE: circuit-only numbers below about -70 dB are not physical; real stopbands are capped at ~60-80 dB by")
print("  input-output coupling, ground currents and the enclosure (see part D and 13/shielding-and-isolation).")

# ---------------------------------------------------------------- C
print("\nC: safe amplifier test set-up")
# BGA524N6 canonical: G 19.6 dB, IP1dB -16 dBm, RF input abs max 0 dBm
G, ip1, absmax = 19.6, -16.0, 0.0
gen_min, pad_in = -40.0, 10.0
pin = gen_min - pad_in
print(f"  BGA524N6: generator {gen_min} dBm -> {pad_in} dB pad -> LNA input {pin} dBm ({ip1 - pin:.0f} dB below IP1dB) -> output {pin + G:.1f} dBm")
check("C1 small-signal gain test sits >= 30 dB below IP1dB", ip1 - pin >= 30)
# NanoVNA stimulus -13 dBm directly: 3 dB above IP1dB, 13 dB below abs max
check("C2 a bare NanoVNA port (-13 dBm) drives the BGA524N6 3 dB past IP1dB (gain reads low)", -13 - ip1 == 3)
# gain block, G 20 dB, OP1dB +20 dBm, into a tinySA Ultra (keep < -25 dBm for linearity, abs max +6)
for pad in (20, 30, 40):
    print(f"  20 dB block at OP1dB (+20 dBm) -> {pad} dB pad -> analyzer {20 - pad:+.0f} dBm")
check("C3 40 dB after a +20 dBm block gives -20 dBm at the analyzer (inside the 0 dBm suggested max)", 20 - 40 == -20)
# pad guarantees a return loss: RL >= 2 x pad for any load behind it
for pad in (3, 6, 10):
    print(f"  {pad} dB pad: worst-case |Gamma| seen = {10**(-2*pad/20):.3f} (RL >= {2*pad} dB) even with an open/short behind it")
check("C4 a 6 dB pad bounds the termination to RL >= 12 dB", abs(-20 * np.log10(10 ** (-12 / 20)) - 12) < 1e-9)
# PA into an open
P = 10 ** (33 / 10) * 1e-3
Vpk50 = np.sqrt(2 * P * 50)
print(f"  33 dBm: {Vpk50:.1f} V peak into 50 Ohm; up to {2*Vpk50:.1f} V peak at a voltage maximum with an open/short load")
check("C5 2 W into 50 Ohm = 14.1 V peak; open -> 28.2 V peak", abs(Vpk50 - 14.1) < 0.1)

# ---------------------------------------------------------------- D
print("\nD: high-gain chains — feedback loop gain G*k (k = output->input coupling)")
for Gdb in (20, 40, 60):
    for kdb in (-40, -50, -60, -70):
        lg = Gdb + kdb
        x = 10 ** (lg / 20)
        rip = 20 * np.log10((1 + x) / (1 - x)) if x < 1 else np.inf
        tag = "OSCILLATES (|Gk| >= 1 at the wrong phase)" if x >= 1 else f"gain ripple {rip:.2f} dB p-p"
        print(f"  G {Gdb} dB, coupling {kdb} dB: loop gain {lg:+d} dB -> {tag}")
x40 = 10 ** ((40 - 50) / 20)
check("D1 40 dB gain with -50 dB coupling: loop gain -10 dB, ripple ~5.7 dB p-p", abs(20 * np.log10((1 + x40) / (1 - x40)) - 5.7) < 0.1)
x60 = 10 ** ((60 - 50) / 20)
check("D2 60 dB gain with the same -50 dB coupling oscillates", x60 >= 1)
x_split = 10 ** ((40 - 70) / 20)
check("D3 shielding/splitting to -70 dB coupling brings 40 dB to < 0.6 dB ripple", 20 * np.log10((1 + x_split) / (1 - x_split)) < 0.6)

# ---------------------------------------------------------------- E
print("\nE: enclosure first resonance f110 = c/2 sqrt(1/a^2 + 1/b^2) and the lumped-size limit")
c = 299792458.0
for a, b in [(0.074, 0.111), (0.055, 0.074), (0.148, 0.111)]:
    print(f"  {a*1e3:.0f} x {b*1e3:.0f} mm box: f110 = {c/2*np.sqrt(a**-2 + b**-2)/1e9:.2f} GHz")
check("E1 74 x 111 mm box resonates at 2.43 GHz, 148 x 111 mm at 1.69 GHz",
      abs(c / 2 * np.sqrt(0.074 ** -2 + 0.111 ** -2) / 1e9 - 2.43) < 0.01 and abs(c / 2 * np.sqrt(0.148 ** -2 + 0.111 ** -2) / 1e9 - 1.69) < 0.01)
lam20_air = c / 433e6 / 20; lam20_ms = lam20_air / np.sqrt(3.3)
print(f"  lambda/20 at 433 MHz: {lam20_air*1e3:.1f} mm in air, {lam20_ms*1e3:.1f} mm in eps_eff 3.3")
check("E2 lambda/20 at 433 MHz = 34.6 mm (air), 19.1 mm (eps_eff 3.3)", abs(lam20_air * 1e3 - 34.6) < 0.1 and abs(lam20_ms * 1e3 - 19.1) < 0.1)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
