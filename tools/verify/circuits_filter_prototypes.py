#!/usr/bin/env python3
"""
Verification for kb/01-circuit-theory/passive-filter-design-prototypes.md

  1. Butterworth and Chebyshev g-values from closed-form formulas vs published table values.
  2. Ladder simulation (ABCD) of the prototypes: Butterworth -3.01 dB at w=1, Chebyshev ripple.
  3. Bessel (maximally-flat delay) table values: verify flat delay and compare with scipy's Bessel.
  4. Elliptic (Cauer) 5th-order ladder: element values fitted so the ladder reproduces scipy's
     elliptic magnitude response (transmission zeros fixed by the scipy design).
  5. Group delay comparison (Butterworth / Chebyshev / Bessel, N = 5).
  6. Worked example A: 433.92 MHz harmonic low-pass (Chebyshev 0.1 dB N=5, and elliptic N=5),
     with finite component Q; attenuation at 2f and 3f.
  7. Worked example B: 915 MHz band-pass (3-pole Chebyshev 0.1 dB) by (i) the textbook LP->BP
     transform and (ii) capacitively-coupled shunt resonators (J-inverters); finite Q; IL estimate
     4.343*sum(g)/(FBW*Qu) vs simulation. Also the narrow 902-928 MHz case.
  8. scikit-rf cross-check of example A.
Run: python3 tools/verify/circuits_filter_prototypes.py
"""
import numpy as np
from scipy import signal, optimize

TP = 2 * np.pi

# ---------------------------------------------------------------- helpers
def g_butter(N):
    g = [1.0] + [2 * np.sin((2 * k - 1) * np.pi / (2 * N)) for k in range(1, N + 1)] + [1.0]
    return np.array(g)

def g_cheby(N, ripple_db):
    beta = np.log(1 / np.tanh(ripple_db / 17.37))
    gam = np.sinh(beta / (2 * N))
    a = [np.sin((2 * k - 1) * np.pi / (2 * N)) for k in range(1, N + 1)]
    b = [gam**2 + np.sin(k * np.pi / N)**2 for k in range(1, N + 1)]
    g = [1.0, 2 * a[0] / gam]
    for k in range(2, N + 1):
        g.append(4 * a[k - 2] * a[k - 1] / (b[k - 2] * g[k - 1]))
    g.append(1.0 if N % 2 else 1 / np.tanh(beta / 4)**2)
    return np.array(g)

def abcd_series(Z):
    n = np.size(Z); M = np.zeros((n, 2, 2), complex)
    M[:, 0, 0] = 1; M[:, 0, 1] = Z; M[:, 1, 1] = 1
    return M

def abcd_shunt(Y):
    n = np.size(Y); M = np.zeros((n, 2, 2), complex)
    M[:, 0, 0] = 1; M[:, 1, 0] = Y; M[:, 1, 1] = 1
    return M

def cascade(mats):
    out = mats[0]
    for m in mats[1:]:
        out = out @ m
    return out

def gain_T(M, Rs, RL):
    """transducer power gain for ABCD M between source Rs and load RL"""
    A, B, C, D = M[:, 0, 0], M[:, 0, 1], M[:, 1, 0], M[:, 1, 1]
    H = 1 / (A + B / RL + Rs * C + Rs * D / RL)   # V2/Vs
    return 4 * Rs / RL * np.abs(H)**2, H

def prototype_ladder(g, w, first="shunt"):
    """lowpass prototype with g0=1 source; returns ABCD and load resistance."""
    N = len(g) - 2
    mats = []
    kind = first
    for k in range(1, N + 1):
        if kind == "shunt":
            mats.append(abcd_shunt(1j * w * g[k]))
            kind = "series"
        else:
            mats.append(abcd_series(1j * w * g[k]))
            kind = "shunt"
    last_was_shunt = (first == "shunt") == (N % 2 == 1)
    RL = g[N + 1] if last_was_shunt else 1 / g[N + 1]
    return cascade(mats), RL

def group_delay(H, w):
    ph = np.unwrap(np.angle(H))
    return -np.gradient(ph, w)

# ---------------------------------------------------------------- 1. g-values vs tables
print("=== 1. g-values ===")
# Published tables (Matthaei/Young/Jones Tables 4.05-1, 4.05-2; also Pozar Tables 8.3, 8.4)
tables = {
    ("butter", 3): [1.0, 2.0, 1.0, 1.0],
    ("butter", 5): [0.6180, 1.6180, 2.0000, 1.6180, 0.6180, 1.0],
    ("cheb0.1", 3): [1.0316, 1.1474, 1.0316, 1.0],
    ("cheb0.1", 5): [1.1468, 1.3712, 1.9750, 1.3712, 1.1468, 1.0],
    ("cheb0.5", 3): [1.5963, 1.0967, 1.5963, 1.0],
    ("cheb0.5", 5): [1.7058, 1.2296, 2.5408, 1.2296, 1.7058, 1.0],
    ("cheb0.5", 4): [1.6703, 1.1926, 2.3661, 0.8419, 1.9841],
    ("cheb3.0", 3): [3.3487, 0.7117, 3.3487, 1.0],
}
for (kind, N), ref in tables.items():
    g = g_butter(N) if kind == "butter" else g_cheby(N, float(kind[4:]))
    got = g[1:]
    err = np.max(np.abs(got - np.array(ref)))
    print(f"{kind:8s} N={N}: computed {np.round(got,4)}  max|diff| vs table = {err:.1e}")
    assert err < 6e-4

# ---------------------------------------------------------------- 2. prototype responses
print("\n=== 2. Prototype responses (ladder simulation) ===")
w = np.array([0.5, 0.9, 1.0, 1.5, 2.0, 3.0])
for label, g in [("Butterworth N=5", g_butter(5)), ("Chebyshev 0.1dB N=5", g_cheby(5, 0.1)),
                 ("Chebyshev 0.5dB N=5", g_cheby(5, 0.5))]:
    M, RL = prototype_ladder(g, w)
    GT, _ = gain_T(M, 1.0, RL)
    print(f"{label:22s} IL(dB) at w={list(w)}: {np.round(-10*np.log10(GT),3)}")
# check Butterworth closed form and Chebyshev ripple
M, RL = prototype_ladder(g_butter(5), w)
GT, _ = gain_T(M, 1, RL)
assert np.allclose(GT, 1 / (1 + w**10))
wf = np.linspace(0, 1, 2001)
M, RL = prototype_ladder(g_cheby(5, 0.5), wf)
GT, _ = gain_T(M, 1, RL)
print(f"Chebyshev 0.5 dB N=5: max passband IL = {(-10*np.log10(GT)).max():.4f} dB (expect 0.5)")
assert abs((-10 * np.log10(GT)).max() - 0.5) < 2e-3
# attenuation rule: Chebyshev L_A(w) = 10log10(1 + eps^2 T_N^2(w))
eps2 = 10**(0.5 / 10) - 1
for ww in [1.5, 2.0, 3.0]:
    TN = np.cosh(5 * np.arccosh(ww))
    M, RL = prototype_ladder(g_cheby(5, 0.5), np.array([ww])); GT, _ = gain_T(M, 1, RL)
    print(f"   w={ww}: formula {10*np.log10(1+eps2*TN**2):.3f} dB, ladder {-10*np.log10(GT[0]):.3f} dB")

# ---------------------------------------------------------------- 3. Bessel
print("\n=== 3. Bessel (max-flat delay) ladder values, delay-normalised (tau(0)=1 s) ===")
bessel_tab = {3: [1.2550, 0.5528, 0.1922, 1.0], 5: [0.9303, 0.4577, 0.3312, 0.2090, 0.0718, 1.0]}
for N, vals in bessel_tab.items():
    g = np.array([1.0] + vals)
    wv = np.linspace(1e-4, 3, 30001)
    M, RL = prototype_ladder(g, wv, first="series")
    GT, H = gain_T(M, 1, RL)
    tau = group_delay(H, wv)
    b, a = signal.bessel(N, 1, analog=True, norm="delay")
    _, Hs = signal.freqs(b, a, worN=wv)
    taus = group_delay(Hs, wv)
    w3 = wv[np.argmin(np.abs(-10 * np.log10(GT) - 3.0103))]
    print(f"N={N}: ladder tau(0)={tau[5]:.4f} s, tau(1)={np.interp(1,wv,tau):.4f}, tau(2)={np.interp(2,wv,tau):.4f};"
          f" scipy Bessel tau(1)={np.interp(1,wv,taus):.4f}, tau(2)={np.interp(2,wv,taus):.4f}; ladder 3-dB w = {w3:.3f} rad/s")
    # magnitude comparison with scipy (normalised to DC)
    mag_l = np.sqrt(GT); mag_s = np.abs(Hs)
    print(f"      max |mag difference| ladder vs scipy over 0..3 rad/s = {np.max(np.abs(mag_l-mag_s)):.4f}")

# ---------------------------------------------------------------- 4. Elliptic fit
print("\n=== 4. Elliptic 5th order (0.1 dB ripple, 50 dB stopband) doubly-terminated ladder ===")
b, a = signal.ellip(5, 0.1, 50, 1.0, analog=True)
zeros = np.sort(np.abs(np.imag(np.roots(b))))[::2]   # the two finite transmission-zero frequencies
wz1, wz2 = zeros
print(f"scipy elliptic transmission zeros at w = {wz1:.4f}, {wz2:.4f} rad/s")
wfit = np.concatenate([np.linspace(0.01, 1.0, 300), np.linspace(1.0, 4, 300)])
_, Href = signal.freqs(b, a, worN=wfit)
Gref = np.abs(Href)**2 / np.abs(Href[0])**2       # normalise DC to 1 (odd order, equal terminations)
def elliptic_ladder(p, w):
    C1, C2, C3, C4, C5 = p
    L2 = 1 / (wz1**2 * C2); L4 = 1 / (wz2**2 * C4)
    Z2 = 1 / (1 / (1j * w * L2) + 1j * w * C2)
    Z4 = 1 / (1 / (1j * w * L4) + 1j * w * C4)
    M = cascade([abcd_shunt(1j * w * C1), abcd_series(Z2), abcd_shunt(1j * w * C3),
                 abcd_series(Z4), abcd_shunt(1j * w * C5)])
    return M
def resid(p):
    M = elliptic_ladder(p, wfit)
    GT, _ = gain_T(M, 1, 1)
    return 10 * np.log10(GT + 1e-12) - 10 * np.log10(Gref + 1e-12)
p0 = [1.1, 0.1, 1.9, 0.3, 1.0]
sol = optimize.least_squares(resid, p0, bounds=(1e-4, 10))
C1, C2, C3, C4, C5 = sol.x
L2 = 1 / (wz1**2 * C2); L4 = 1 / (wz2**2 * C4)
print(f"fitted (shunt C1, series L2||C2, shunt C3, series L4||C4, shunt C5): C1={C1:.4f} L2={L2:.4f} C2={C2:.4f} "
      f"C3={C3:.4f} L4={L4:.4f} C4={C4:.4f} C5={C5:.4f}; max fit error = {np.max(np.abs(sol.fun)):.3f} dB")
ELLIP = dict(C1=C1, L2=L2, C2=C2, C3=C3, L4=L4, C4=C4, C5=C5)

# ---------------------------------------------------------------- 5. Group delay comparison
print("\n=== 5. Group delay (prototype, seconds) at w = 0, 0.5, 0.9 of cutoff ===")
wv = np.linspace(1e-4, 1.2, 12001)
for label, g in [("Butterworth N=5", g_butter(5)), ("Chebyshev 0.5 dB N=5", g_cheby(5, 0.5))]:
    M, RL = prototype_ladder(g, wv); _, H = gain_T(M, 1, RL); tau = group_delay(H, wv)
    print(f"{label:22s}: tau(0)={tau[2]:.3f}, tau(0.5)={np.interp(0.5,wv,tau):.3f}, tau(0.9)={np.interp(0.9,wv,tau):.3f}, "
          f"tau(1.0)={np.interp(1.0,wv,tau):.3f}")

# ---------------------------------------------------------------- 6. 433.92 MHz harmonic LPF
print("\n=== 6. 433.92 MHz harmonic low-pass filter (50 ohm) ===")
Z0 = 50.0
fc = 520e6       # ripple-band edge chosen ~20 % above 433.92 MHz
wc = TP * fc
def lpf_from_proto(g):
    N = len(g) - 2; parts = []
    kind = "shunt"
    for k in range(1, N + 1):
        if kind == "shunt":
            parts.append(("C", g[k] / (Z0 * wc))); kind = "series"
        else:
            parts.append(("L", g[k] * Z0 / wc)); kind = "shunt"
    return parts
def build(parts, f, QL=None, QC=None):
    w = TP * f; mats = []
    for typ, val in parts:
        if typ == "C":
            Y = 1j * w * val
            if QC: Y = Y + (w * val) / QC  # G = wC/Q
            mats.append(abcd_shunt(Y))
        elif typ == "L":
            Zs = 1j * w * val
            if QL: Zs = Zs + (w * val) / QL * 1  # R = wL/Q (Q taken constant)
            mats.append(abcd_series(Zs))
        elif typ == "LCpar":          # series branch: L || C (elliptic)
            Lv, Cv = val
            ZL = 1j * w * Lv + ((w * Lv) / QL if QL else 0)
            YC = 1j * w * Cv + ((w * Cv) / QC if QC else 0)
            mats.append(abcd_series(1 / (1 / ZL + YC)))
        elif typ == "Cs":
            Zc = 1 / (1j * w * val) + ((1 / (w * val)) / QC if QC else 0)
            mats.append(abcd_series(Zc))
        elif typ == "Lsh":
            Yl = 1 / (1j * w * val + ((w * val) / QL if QL else 0))
            mats.append(abcd_shunt(Yl))
    return cascade(mats)
fr = np.array([433.92e6, 868e6, 1301.76e6, 1735.68e6])
cheb = lpf_from_proto(g_cheby(5, 0.1))
print("Chebyshev 0.1 dB N=5, fc = 520 MHz:", ", ".join(f"{t}={v*1e12:.2f} pF" if t == "C" else f"{t}={v*1e9:.2f} nH" for t, v in cheb))
for label, QL, QC in [("ideal", None, None), ("Q_L=40, Q_C=300", 40, 300)]:
    M = build(cheb, fr, QL, QC); GT, _ = gain_T(M, Z0, Z0)
    print(f"  {label:16s}: IL at f0 = {-10*np.log10(GT[0]):.3f} dB; atten at 2f,3f,4f = {np.round(-10*np.log10(GT[1:]),1)} dB")
# elliptic scaled
ellp = [("C", ELLIP["C1"] / (Z0 * wc)), ("LCpar", (ELLIP["L2"] * Z0 / wc, ELLIP["C2"] / (Z0 * wc))),
        ("C", ELLIP["C3"] / (Z0 * wc)), ("LCpar", (ELLIP["L4"] * Z0 / wc, ELLIP["C4"] / (Z0 * wc))),
        ("C", ELLIP["C5"] / (Z0 * wc))]
print("Elliptic 0.1 dB/50 dB N=5, fc=520 MHz: C1={:.2f} pF, L2={:.2f} nH||C2={:.3f} pF (zero {:.0f} MHz), C3={:.2f} pF, "
      "L4={:.2f} nH||C4={:.3f} pF (zero {:.0f} MHz), C5={:.2f} pF".format(
        ellp[0][1]*1e12, ellp[1][1][0]*1e9, ellp[1][1][1]*1e12, fc*wz1/1e6, ellp[2][1]*1e12,
        ellp[3][1][0]*1e9, ellp[3][1][1]*1e12, fc*wz2/1e6, ellp[4][1]*1e12))
for label, QL, QC in [("ideal", None, None), ("Q_L=40, Q_C=300", 40, 300)]:
    M = build(ellp, fr, QL, QC); GT, _ = gain_T(M, Z0, Z0)
    print(f"  {label:16s}: IL at f0 = {-10*np.log10(GT[0]):.3f} dB; atten at 2f,3f,4f = {np.round(-10*np.log10(GT[1:]),1)} dB")
# Chebyshev N=7 at the same cutoff
cheb7 = lpf_from_proto(g_cheby(7, 0.1))
print("Chebyshev 0.1 dB N=7, fc = 520 MHz:", ", ".join(f"{t}={v*1e12:.2f} pF" if t == "C" else f"{t}={v*1e9:.2f} nH" for t, v in cheb7))
for label, QL, QC in [("ideal", None, None), ("Q_L=40, Q_C=300", 40, 300)]:
    M = build(cheb7, fr, QL, QC); GT, _ = gain_T(M, Z0, Z0)
    print(f"  {label:16s}: IL at f0 = {-10*np.log10(GT[0]):.3f} dB; atten at 2f,3f,4f = {np.round(-10*np.log10(GT[1:]),1)} dB")
# elliptic re-scaled so its first transmission zero sits on the 2nd harmonic
fc2 = 867.84e6 / wz1
wc2 = TP * fc2
ellp2 = [("C", ELLIP["C1"] / (Z0 * wc2)), ("LCpar", (ELLIP["L2"] * Z0 / wc2, ELLIP["C2"] / (Z0 * wc2))),
         ("C", ELLIP["C3"] / (Z0 * wc2)), ("LCpar", (ELLIP["L4"] * Z0 / wc2, ELLIP["C4"] / (Z0 * wc2))),
         ("C", ELLIP["C5"] / (Z0 * wc2))]
print("Elliptic re-scaled (fc = {:.1f} MHz, zeros at {:.1f} and {:.1f} MHz): C1={:.2f} pF, L2={:.2f} nH||C2={:.3f} pF, C3={:.2f} pF, "
      "L4={:.2f} nH||C4={:.3f} pF, C5={:.2f} pF".format(fc2/1e6, fc2*wz1/1e6, fc2*wz2/1e6,
        ellp2[0][1]*1e12, ellp2[1][1][0]*1e9, ellp2[1][1][1]*1e12, ellp2[2][1]*1e12,
        ellp2[3][1][0]*1e9, ellp2[3][1][1]*1e12, ellp2[4][1]*1e12))
for label, QL, QC in [("ideal", None, None), ("Q_L=40, Q_C=300", 40, 300)]:
    M = build(ellp2, fr, QL, QC); GT, _ = gain_T(M, Z0, Z0)
    print(f"  {label:16s}: IL at f0 = {-10*np.log10(GT[0]):.3f} dB; atten at 2f,3f,4f = {np.round(-10*np.log10(GT[1:]),1)} dB")
# return loss in band for ideal Chebyshev
fb = np.linspace(400e6, 470e6, 71)
M = build(cheb, fb); A, B, C, D = M[:, 0, 0], M[:, 0, 1], M[:, 1, 0], M[:, 1, 1]
S11 = (A + B / Z0 - C * Z0 - D) / (A + B / Z0 + C * Z0 + D)
print(f"  Chebyshev 0.1 dB ideal: worst return loss 400-470 MHz = {-20*np.log10(np.abs(S11).max()):.1f} dB")

# delay-loss rule: uniform element Q in a low-pass -> dL(dB) ~= 8.686 * (w/Q) * tau_g(w)
print("  delay-loss rule check (Chebyshev N=5 LPF, uniform Q on every element):")
fdl = np.linspace(50e6, 515e6, 4000)
M0 = build(cheb, fdl); GT0, H0 = gain_T(M0, Z0, Z0); taug = group_delay(H0, TP * fdl)
for Qd in [40, 100]:
    Mq = build(cheb, fdl, Qd, Qd); GTq, _ = gain_T(Mq, Z0, Z0)
    for ftest in [200e6, 433.92e6]:
        i = np.argmin(np.abs(fdl - ftest))
        dLsim = -10 * np.log10(GTq[i] / GT0[i]); dLrule = 8.686 * TP * fdl[i] / Qd * taug[i]
        print(f"    Q={Qd}, f={ftest/1e6:.0f} MHz: simulated extra loss {dLsim:.3f} dB, 8.686*(w/Q)*tau = {dLrule:.3f} dB")
        assert abs(dLsim - dLrule) / dLsim < 0.05

# ---------------------------------------------------------------- 7. 915 MHz band-pass
print("\n=== 7. 915 MHz band-pass, 3-pole Chebyshev 0.1 dB ===")
g = g_cheby(3, 0.1)
f0 = 915e6; w0 = TP * f0
for FBW, tag in [(0.10, "FBW 10 % (~870-960 MHz)"), (26 / 915, "FBW 2.84 % (902-928 MHz)")]:
    print(f"-- {tag}")
    # (i) textbook LP->BP: shunt C_k -> shunt L||C ; series L_k -> series L-C
    Lsh1 = Z0 * FBW / (w0 * g[1]); Csh1 = g[1] / (Z0 * w0 * FBW)
    Lse2 = g[2] * Z0 / (w0 * FBW); Cse2 = FBW / (w0 * g[2] * Z0)
    print(f"   (i) direct transform: shunt resonators {Lsh1*1e9:.3f} nH || {Csh1*1e12:.2f} pF; "
          f"series resonator {Lse2*1e9:.1f} nH + {Cse2*1e12:.3f} pF  <- impractical values")
    # (ii) capacitively coupled shunt resonators, J-inverters (Matthaei ch. 8)
    Lr = 3.3e-9
    Cr = 1 / (w0**2 * Lr)
    bslope = w0 * Cr
    Y0 = 1 / Z0
    J01 = np.sqrt(Y0 * bslope * FBW / (g[0] * g[1]))
    J12 = FBW * bslope / np.sqrt(g[1] * g[2])
    J23 = FBW * bslope / np.sqrt(g[2] * g[3])
    J34 = np.sqrt(Y0 * bslope * FBW / (g[3] * g[4]))
    C01 = J01 / (w0 * np.sqrt(1 - (J01 / Y0)**2)); C34 = J34 / (w0 * np.sqrt(1 - (J34 / Y0)**2))
    C12 = J12 / w0; C23 = J23 / w0
    Ce01 = C01 / (1 + (w0 * C01 * Z0)**2); Ce34 = C34 / (1 + (w0 * C34 * Z0)**2)
    C1 = Cr - Ce01 - C12; C2 = Cr - C12 - C23; C3 = Cr - C23 - Ce34
    print(f"   (ii) coupled resonators, Lr = 3.3 nH: C01={C01*1e12:.3f} pF, C12={C12*1e12:.3f} pF, C23={C23*1e12:.3f} pF, "
          f"C34={C34*1e12:.3f} pF; shunt C1={C1*1e12:.3f}, C2={C2*1e12:.3f}, C3={C3*1e12:.3f} pF")
    parts = [("Cs", C01), ("Lsh", Lr), ("C", C1), ("Cs", C12), ("Lsh", Lr), ("C", C2), ("Cs", C23),
             ("Lsh", Lr), ("C", C3), ("Cs", C34)]
    ff = np.linspace(700e6, 1150e6, 45001)
    for label, QLq, QCq in [("ideal", None, None), ("Q_L=60, Q_C=400", 60, 400)]:
        M = build(parts, ff, QLq, QCq); GT, _ = gain_T(M, Z0, Z0)
        ILdb = -10 * np.log10(GT)
        i0 = np.argmin(np.abs(ff - f0))
        ok = np.where(ILdb <= ILdb.min() + 3.0103)[0]
        bw3 = ff[ok[-1]] - ff[ok[0]]
        fc_sim = 0.5 * (ff[ok[-1]] + ff[ok[0]])
        est = 4.343 * np.sum(g[1:4]) / (FBW * (1 / (1 / QLq + 1 / QCq))) if QLq else 0.0
        extra = f", estimate 4.343*sum(g)/(FBW*Qu) = {est:.2f} dB" if QLq else ""
        print(f"      {label:16s}: IL(915) = {ILdb[i0]:.2f} dB, min IL = {ILdb.min():.2f} dB, 3-dB BW = {bw3/1e6:.1f} MHz "
              f"centred {fc_sim/1e6:.1f} MHz{extra}")
    # re-centre: scale every capacitor by k^2 so the simulated centre lands on 915 MHz
    kfac = (fc_sim / f0)**2
    parts_rc = [(t, v * kfac) if t in ("C", "Cs") else (t, v) for t, v in parts]
    M = build(parts_rc, ff, 60, 400); GT, _ = gain_T(M, Z0, Z0); ILdb = -10 * np.log10(GT)
    ok = np.where(ILdb <= ILdb.min() + 3.0103)[0]
    print(f"      re-centred (all C x {kfac:.4f}): centre {0.5*(ff[ok[-1]]+ff[ok[0]])/1e6:.1f} MHz, IL(915) = {ILdb[np.argmin(np.abs(ff-f0))]:.2f} dB")
    M = build(parts, np.array([433.92e6, 1830e6, 2745e6]), 60, 400); GT, _ = gain_T(M, Z0, Z0)
    print(f"      atten at 433.92 MHz, 2x915, 3x915 = {np.round(-10*np.log10(GT),1)} dB")

# ---------------------------------------------------------------- 8. scikit-rf cross-check
print("\n=== 8. scikit-rf cross-check of the 433.92 MHz Chebyshev LPF ===")
try:
    import skrf as rf
    freq = rf.Frequency(300, 2000, 1701, unit="MHz")
    med = rf.media.DefinedGammaZ0(frequency=freq, z0_port=50)
    net = None
    for t, v in cheb:
        el = med.shunt_capacitor(v) if t == "C" else med.inductor(v)
        net = el if net is None else net ** el
    s21_skrf = net.s[:, 1, 0]
    M = build(cheb, freq.f)
    A, B, C, D = M[:, 0, 0], M[:, 0, 1], M[:, 1, 0], M[:, 1, 1]
    s21_mine = 2 / (A + B / Z0 + C * Z0 + D)
    print(f"max |S21 difference| scikit-rf vs ABCD code = {np.max(np.abs(s21_skrf - s21_mine)):.2e}")
    assert np.max(np.abs(s21_skrf - s21_mine)) < 1e-9
    i = np.argmin(np.abs(freq.f - 868e6))
    print(f"scikit-rf |S21| at 868 MHz = {20*np.log10(abs(s21_skrf[i])):.2f} dB")
except Exception as e:  # pragma: no cover
    print("scikit-rf check skipped:", e)
print("\nALL CHECKS PASSED")
