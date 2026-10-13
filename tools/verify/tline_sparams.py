#!/usr/bin/env python3
"""
Verification for kb/03-transmission-lines-matching/s-parameters.md

Checks:
  1. Own S<->Z<->Y<->ABCD conversion formulas (real z0) vs scikit-rf.
  2. Power waves (Kurokawa) vs pseudo-waves (Marks & Williams) for a COMPLEX reference impedance:
     |a|^2 - |b|^2 equals delivered power only for power waves; S matrices differ; skrf s_def options.
  3. Reciprocity (S = S^T) and losslessness (S^H S = I) for an LC/line network; passivity of a lossy one
     (eigenvalues of I - S^H S >= 0).
  4. Renormalisation 50 -> 75 ohm: closed-form 1-port and 2-port vs skrf renormalize.
  5. Mixed-mode S-parameters: two uncoupled 50-ohm lines with skew -> |Sdd21| = |cos(dth/2)|, |Scd21| = |sin(dth/2)|;
     Zdiff reference = 100 ohm, Zcomm = 25 ohm.
  6. T-parameters: cascade by matrix product == skrf '**' cascade; de-embedding by T inverse.
  7. Group delay of a line from S21 phase slope = l/vp.
  8. Touchstone write/read round trip (and the header format).
  9. Power gains: G_T, G_A, G_P formulas; G_T = |S21|^2 with 50 ohm terminations; G_T <= G_A, G_T <= G_P.
 10. Stability: K, |Delta|, mu, mu' consistency.

Run: python3 tools/verify/tline_sparams.py
"""
import os
import tempfile
import warnings
import numpy as np
import skrf as rf
from skrf import network as nw

warnings.filterwarnings("ignore", category=DeprecationWarning)
c0 = 299_792_458.0
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


# a generic test 2-port: series L, shunt C, line section (lossy), series R
freq = rf.Frequency(100, 3000, 59, unit="MHz")
w = freq.w
med = rf.media.DefinedGammaZ0(frequency=freq, z0=50, gamma=0.2 + 1j * w / (0.7 * c0))
ntw = med.inductor(8e-9) ** med.shunt_capacitor(2.2e-12) ** med.line(0.05, unit="m") ** med.resistor(3.0)
S = ntw.s
Z0 = 50.0
I2 = np.eye(2)

# ---------------------------------------------------------------- 1. conversions
def s2z_own(S, z0):
    return np.array([z0 * (I2 + s) @ np.linalg.inv(I2 - s) for s in S])


def s2y_own(S, z0):
    return np.array([np.linalg.inv(z0 * (I2 + s) @ np.linalg.inv(I2 - s)) for s in S])


def s2abcd_own(S, z0):
    out = []
    for s in S:
        s11, s12, s21, s22 = s[0, 0], s[0, 1], s[1, 0], s[1, 1]
        A = ((1 + s11) * (1 - s22) + s12 * s21) / (2 * s21)
        B = z0 * ((1 + s11) * (1 + s22) - s12 * s21) / (2 * s21)
        C = ((1 - s11) * (1 - s22) - s12 * s21) / (2 * s21 * z0)
        D = ((1 - s11) * (1 + s22) + s12 * s21) / (2 * s21)
        out.append([[A, B], [C, D]])
    return np.array(out)


check("S->Z (Z = z0 (I+S)(I-S)^-1) == skrf", np.allclose(s2z_own(S, Z0), ntw.z))
check("S->Y == skrf", np.allclose(s2y_own(S, Z0), ntw.y))
check("S->ABCD (Pozar table 4.2) == skrf", np.allclose(s2abcd_own(S, Z0), ntw.a))
check("ABCD of cascade == product of ABCDs", np.allclose(
    ntw.a, np.einsum("fij,fjk->fik", np.einsum("fij,fjk->fik", med.inductor(8e-9).a, med.shunt_capacitor(2.2e-12).a),
                     np.einsum("fij,fjk->fik", med.line(0.05, unit="m").a, med.resistor(3.0).a))))

# ---------------------------------------------------------------- 2. power waves vs pseudo-waves (complex ref)
Zr = 40 - 25j                     # complex reference impedance
ZL = 30 + 60j
V, I = 1.0 + 0.3j, None
I = V / ZL
# Kurokawa power waves
a_p = (V + Zr * I) / (2 * np.sqrt(Zr.real))
b_p = (V - np.conj(Zr) * I) / (2 * np.sqrt(Zr.real))
# Marks-Williams pseudo-waves (their normalisation)
k = np.sqrt(Zr.real) / (2 * abs(Zr))
a_ps = k * (V + Zr * I)
b_ps = k * (V - Zr * I)
P = 0.5 * np.real(V * np.conj(I))
check("power waves: (|a|^2 - |b|^2)/2 = delivered power (any complex Zref)", abs(0.5 * (abs(a_p)**2 - abs(b_p)**2) - P) < 1e-12)
cross = 0.5 * (abs(a_ps)**2 - abs(b_ps)**2)
check("pseudo-waves: (|a|^2 - |b|^2)/2 != delivered power when Zref complex", abs(cross - P) > 1e-4,
      f"(pseudo {cross:.5f} vs P {P:.5f})")
G_pw = b_p / a_p
G_ps = b_ps / a_ps
check("power-wave Gamma = (ZL - Zr*)/(ZL + Zr)", abs(G_pw - (ZL - np.conj(Zr)) / (ZL + Zr)) < 1e-12)
check("pseudo-wave Gamma = (ZL - Zr)/(ZL + Zr)", abs(G_ps - (ZL - Zr) / (ZL + Zr)) < 1e-12)
check("conjugate-matched load (ZL = Zr*) has zero POWER-wave reflection", abs((np.conj(Zr) - np.conj(Zr)) / (np.conj(Zr) + Zr)) < 1e-15)
# skrf s_def variants
zc = np.array([Zr, Zr])
Zmat = ntw.z
S_pw = nw.z2s(Zmat, zc, s_def="power")
S_ps = nw.z2s(Zmat, zc, s_def="pseudo")
S_tr = nw.z2s(Zmat, zc, s_def="traveling")
check("skrf: power vs pseudo S differ for complex z0", not np.allclose(S_pw, S_ps))
check("skrf: power, pseudo, traveling identical for real z0",
      np.allclose(nw.z2s(Zmat, 50, "power"), nw.z2s(Zmat, 50, "pseudo")) and
      np.allclose(nw.z2s(Zmat, 50, "power"), nw.z2s(Zmat, 50, "traveling")))
# power waves: 1 - |S11|^2 is fraction of available power delivered into port (for a 1-port)
Zs = Zr
Vs = 1.0
Iin = Vs / (Zs + ZL)
Pdel = 0.5 * abs(Iin) ** 2 * ZL.real
Pav = abs(Vs) ** 2 / (8 * Zs.real)
check("power waves: P_del = P_avail (1 - |Gamma_p|^2) with source Zs = Zref", abs(Pdel - Pav * (1 - abs(G_pw) ** 2)) < 1e-12)

# ---------------------------------------------------------------- 3. reciprocity / losslessness / passivity
medL = rf.media.DefinedGammaZ0(frequency=freq, z0=50, gamma=1j * w / (0.7 * c0))
lossless = medL.inductor(8e-9) ** medL.shunt_capacitor(2.2e-12) ** medL.line(0.05, unit="m", z0=75)
Sl = lossless.s
unit = np.max(np.abs(np.einsum("fji,fjk->fik", Sl.conj(), Sl) - I2))
check("lossless network: S^H S = I (unitary)", unit < 1e-12, f"(max dev {unit:.1e})")
check("reciprocal network: S = S^T", np.allclose(Sl, np.transpose(Sl, (0, 2, 1))))
ev = np.linalg.eigvalsh(np.array([I2 - s.conj().T @ s for s in S]))
check("lossy passive network: eigenvalues of I - S^H S >= 0 (passivity)", ev.min() > -1e-12,
      f"(min eig {ev.min():.3e}; max dissipated fraction {ev.max():.3f})")
check("lossless 2-port: |S11| = |S22| and |S11|^2 + |S21|^2 = 1",
      np.allclose(abs(Sl[:, 0, 0]), abs(Sl[:, 1, 1])) and np.allclose(abs(Sl[:, 0, 0])**2 + abs(Sl[:, 1, 0])**2, 1))

# ---------------------------------------------------------------- 4. renormalisation
G50 = gam = (ZL - 50) / (ZL + 50)
r = (75 - 50) / (75 + 50)
G75_formula = (G50 - r) / (1 - r * G50)
check("1-port renormalisation 50->75: G' = (G - r)/(1 - r G), r = (75-50)/(75+50)",
      abs(G75_formula - (ZL - 75) / (ZL + 75)) < 1e-12)
S75 = nw.renormalize_s(S, 50, 75)
S75_direct = nw.z2s(ntw.z, 75)
check("2-port renormalisation (skrf renormalize_s) == z2s at new z0", np.allclose(S75, S75_direct))

# ---------------------------------------------------------------- 5. mixed mode
# 4-port: port1->port3 line A, port2->port4 line B (skrf se2gmm with p=2 expects ports [1,2] in, [3,4] out)
fmm = rf.Frequency(1, 3, 21, unit="GHz")
mm = rf.media.DefinedGammaZ0(frequency=fmm, z0=50, gamma=1j * fmm.w / c0)
la = mm.line(0.100, unit="m")
dl = 0.006
lb = mm.line(0.100 + dl, unit="m")
S4 = np.zeros((fmm.npoints, 4, 4), complex)
# ordering: 1,2 = inputs of line A,B ; 3,4 = outputs of line A,B
S4[:, 0, 2] = S4[:, 2, 0] = la.s[:, 1, 0]
S4[:, 1, 3] = S4[:, 3, 1] = lb.s[:, 1, 0]
n4 = rf.Network(frequency=fmm, s=S4, z0=50)
n4.se2gmm(p=2)
# mixed-mode order after se2gmm: [d1, d2, c1, c2]
Sdd21 = n4.s[:, 1, 0]
Scd21 = n4.s[:, 3, 0]
dth = 2 * np.pi * fmm.f / c0 * dl
check("mixed-mode, skewed pair: |Sdd21| = |cos(dth/2)|", np.allclose(abs(Sdd21), abs(np.cos(dth / 2)), atol=1e-12))
check("mixed-mode, skewed pair: |Scd21| = |sin(dth/2)| (diff->common conversion)",
      np.allclose(abs(Scd21), abs(np.sin(dth / 2)), atol=1e-12),
      f"(at 2.4 GHz and 6 mm skew in air: {abs(np.sin(2*np.pi*2.4e9/c0*dl/2)):.3f} = {20*np.log10(abs(np.sin(2*np.pi*2.4e9/c0*dl/2))):.1f} dB)")
check("mixed-mode reference impedances: Zdiff = 100 ohm, Zcomm = 25 ohm", np.allclose(n4.z0[0], [100, 100, 25, 25]))

# ---------------------------------------------------------------- 6. T-parameters, cascade, de-embedding
A1 = med.inductor(5e-9) ** med.line(0.03, unit="m")
B1 = med.shunt_capacitor(1.5e-12) ** med.resistor(10.0)
T_prod = np.einsum("fij,fjk->fik", nw.s2t(A1.s), nw.s2t(B1.s))
check("T-parameters: T(A**B) = T(A) T(B)", np.allclose(nw.t2s(T_prod), (A1 ** B1).s))
# explicit 2-port formula used by skrf: [b1, a1]^T = T [a2, b2]^T
s11, s12, s21, s22 = A1.s[5, 0, 0], A1.s[5, 0, 1], A1.s[5, 1, 0], A1.s[5, 1, 1]
T_formula = np.array([[s12 - s11 * s22 / s21, s11 / s21], [-s22 / s21, 1 / s21]])
check("skrf T convention: T = [[S12 - S11 S22/S21, S11/S21], [-S22/S21, 1/S21]]", np.allclose(T_formula, nw.s2t(A1.s)[5]))
# de-embed fixture A1 from measurement A1**DUT
DUT = med.inductor(12e-9) ** med.shunt_capacitor(0.8e-12)
meas = A1 ** DUT
T_dut = np.einsum("fij,fjk->fik", np.linalg.inv(nw.s2t(A1.s)), nw.s2t(meas.s))
check("de-embedding with T^-1 recovers the DUT", np.allclose(nw.t2s(T_dut), DUT.s))
check("skrf inv operator does the same: A1.inv ** meas == DUT", np.allclose((A1.inv ** meas).s, DUT.s))

# ---------------------------------------------------------------- 7. group delay
fgd = rf.Frequency(100, 3000, 2901, unit="MHz")
mgd = rf.media.DefinedGammaZ0(frequency=fgd, z0=50, gamma=1j * fgd.w / (0.66 * c0))
ln = mgd.line(1.0, unit="m")
tau_theory = 1.0 / (0.66 * c0)
phase = np.unwrap(np.angle(ln.s[:, 1, 0]))
tau_own = -np.gradient(phase, fgd.w)
check("group delay -dphi/dw of 1 m VF0.66 line = 5.054 ns", np.allclose(tau_own, tau_theory, rtol=1e-6),
      f"({tau_own.mean()*1e9:.4f} ns)")
check("skrf group_delay agrees", np.allclose(ln.group_delay[:, 1, 0].real, tau_theory, rtol=1e-6))

# ---------------------------------------------------------------- 8. Touchstone round trip
with tempfile.TemporaryDirectory() as td:
    ntw.write_touchstone(os.path.join(td, "dut"), form="ma")
    txt = open(os.path.join(td, "dut.s2p")).read().splitlines()
    header = [l for l in txt if l.startswith("#")][0]
    back = rf.Network(os.path.join(td, "dut.s2p"))
    check("Touchstone .s2p write/read round trip", np.allclose(back.s, ntw.s, atol=1e-9), f"(header: '{header.strip()}')")
    # the order of 2-port data on each line is S11 S21 S12 S22 (a well-known Touchstone quirk)
    first = [l for l in txt if l and not l.startswith(("!", "#"))][0].split()
    vals = np.array(first[1:], float).reshape(4, 2)
    s_first = ntw.s[0]
    order = [s_first[0, 0], s_first[1, 0], s_first[0, 1], s_first[1, 1]]
    check("Touchstone 2-port column order is S11, S21, S12, S22", np.allclose(vals[:, 0], np.abs(order), rtol=1e-6))

# ---------------------------------------------------------------- 9. power gains
S11, S12, S21, S22 = 0.55 * np.exp(-1j * np.radians(150)), 0.06 * np.exp(1j * np.radians(40)), \
    3.2 * np.exp(1j * np.radians(75)), 0.45 * np.exp(-1j * np.radians(35))    # illustrative device
Dl = S11 * S22 - S12 * S21


def gin(GL):
    return S11 + S12 * S21 * GL / (1 - S22 * GL)


def gout(GS):
    return S22 + S12 * S21 * GS / (1 - S11 * GS)


def GT(GS, GL):
    return (1 - abs(GS)**2) * abs(S21)**2 * (1 - abs(GL)**2) / abs((1 - GS * gin(GL)) * (1 - S22 * GL))**2


def GA(GS):
    return (1 - abs(GS)**2) * abs(S21)**2 / (abs(1 - S11 * GS)**2 * (1 - abs(gout(GS))**2))


def GP(GL):
    return abs(S21)**2 * (1 - abs(GL)**2) / ((1 - abs(gin(GL))**2) * abs(1 - S22 * GL)**2)


check("G_T = |S21|^2 with 50-ohm source and load", abs(GT(0, 0) - abs(S21)**2) < 1e-12)
rng = np.random.default_rng(5)
okg = True
for _ in range(500):
    GS = 0.6 * np.sqrt(rng.uniform()) * np.exp(2j * np.pi * rng.uniform())
    GL = 0.6 * np.sqrt(rng.uniform()) * np.exp(2j * np.pi * rng.uniform())
    if abs(gin(GL)) < 1 and abs(gout(GS)) < 1:
        okg &= GT(GS, GL) <= GA(GS) * (1 + 1e-9) and GT(GS, GL) <= GP(GL) * (1 + 1e-9)
        # equality G_T = G_A when load conjugately matched to Gamma_out
        GLc = np.conj(gout(GS))
        okg &= abs(GT(GS, GLc) - GA(GS)) < 1e-9 * GA(GS)
check("G_T <= G_A, G_T <= G_P; G_T = G_A when GL = Gamma_out* (500 random terminations)", okg)

# ---------------------------------------------------------------- 10. stability
K = (1 - abs(S11)**2 - abs(S22)**2 + abs(Dl)**2) / (2 * abs(S12 * S21))
mu = (1 - abs(S11)**2) / (abs(S22 - Dl * np.conj(S11)) + abs(S12 * S21))
mup = (1 - abs(S22)**2) / (abs(S11 - Dl * np.conj(S22)) + abs(S12 * S21))
print(f"      illustrative device: K = {K:.3f}, |Delta| = {abs(Dl):.3f}, mu = {mu:.3f}, mu' = {mup:.3f}, "
      f"|S21|^2 = {20*np.log10(abs(S21)):.1f} dB")
check("stability tests consistent: (K>1 and |D|<1) <=> mu>1 <=> mu'>1", ((K > 1) and (abs(Dl) < 1)) == (mu > 1) == (mup > 1))
if K > 1 and abs(Dl) < 1:
    B1c = 1 + abs(S11)**2 - abs(S22)**2 - abs(Dl)**2
    MAG = abs(S21 / S12) * (K - np.sqrt(K**2 - 1))
    print(f"      unconditionally stable: MAG = {10*np.log10(MAG):.2f} dB, MSG = {10*np.log10(abs(S21/S12)):.2f} dB")
    # simultaneous conjugate match
    C1 = S11 - Dl * np.conj(S22)
    GSm = (B1c - np.sqrt(B1c**2 - 4 * abs(C1)**2)) / (2 * C1)
    B2 = 1 + abs(S22)**2 - abs(S11)**2 - abs(Dl)**2
    C2 = S22 - Dl * np.conj(S11)
    GLm = (B2 - np.sqrt(B2**2 - 4 * abs(C2)**2)) / (2 * C2)
    check("simultaneous conjugate match: G_T(GSm, GLm) = MAG", abs(GT(GSm, GLm) - MAG) < 1e-9 * MAG)
else:
    print(f"      potentially unstable: MSG = {10*np.log10(abs(S21/S12)):.2f} dB")

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
