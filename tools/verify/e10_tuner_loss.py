#!/usr/bin/env python3
"""
e10_tuner_loss.py — numbers for kb/03-transmission-lines-matching/antenna-tuners-and-atus.md (W5-E10).

 1. Total loss of a mismatched lossy line: TL = 10 log[(a^2 - |G|^2) / (a (1 - |G|^2))], a = 10^(A/10)
    (same formula as 03/reflections; cross-checked here by exact transmission-line bookkeeping).
    Cases: 30 m of RG-58, LMR-400 and 450-ohm ladder line at 3.6/7/14/28 MHz with SWR 1.5/3/10/20 at
    the antenna -> "tuner at the rig" vs "tuner at the antenna".
 2. What the transmitter-end tuner hides: the SWR at the rig end of a lossy line (return loss
    + 2A), i.e. why a "great SWR" can coexist with most power going into the coax.
 3. Lossy-component matching networks (ABCD, exact): L-network, high-pass T (C-L-C) and Pi (C-L-C)
    efficiency vs load impedance for inductor Q_u = 100/200/300, capacitor Q 1000.
    The T-network's free parameter (series input C) is swept to show the loss of a small-C setting.
 4. Rule of thumb check: L-network loss ~ Q_n/Q_u (Q_n = sqrt(Rh/Rl - 1)).
 5. Auto-tuner state count (7 L x 7 C relays, C before/after L) and search-time estimate.

Run:  python3 tools/verify/e10_tuner_loss.py
"""
import cmath
import math

import numpy as np
from scipy.optimize import brentq

FAIL = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAIL.append(name)


# ------------------------------------------------------------------ cable models (dB per 100 m)
def a_rg58(fm):   # Belden 8240 fit from 03/coax-and-cables (k1, k2), extrapolated to HF
    return 1.123 * math.sqrt(fm) + 0.0123 * fm


def a_lmr400(fm):  # Times equation 0.12229 sqrt f + 0.00026 f dB/100 ft
    return (0.12229 * math.sqrt(fm) + 0.00026 * fm) * 3.2808


def a_ladder(fm):  # 450-ohm window line, ASSUMED 0.2 dB/100 ft at 14 MHz dry, scaling sqrt(f)
    return 0.2 * 3.2808 * math.sqrt(fm / 14.0)


CABLES = [("RG-58", a_rg58, 50.0), ("LMR-400", a_lmr400, 50.0), ("450-ohm ladder (dry, assumed)", a_ladder, 450.0)]


def total_loss_db(A_db, gamma_mag):
    a = 10 ** (A_db / 10)
    g2 = gamma_mag ** 2
    return 10 * math.log10((a * a - g2) / (a * (1 - g2)))


def gamma_from_swr(s):
    return (s - 1) / (s + 1)


# exact cross-check: lossy line Z0 real, gamma = alpha + j beta, load ZL
def exact_line_loss(A_db, ZL, Z0, beta_l=1.234):
    alpha_l = A_db / 8.686
    gl = (ZL - Z0) / (ZL + Z0)
    # voltages at load (z=0) and input (z=-l): V(z) = V+ (e^{-gz} + G e^{gz}); evaluate with z = -l at input
    g = complex(alpha_l, beta_l)
    Vin = cmath.exp(g) + gl * cmath.exp(-g)
    Iin = (cmath.exp(g) - gl * cmath.exp(-g)) / Z0
    VL = 1 + gl
    IL = (1 - gl) / Z0
    Pin = (Vin * Iin.conjugate()).real
    PL = (VL * IL.conjugate()).real
    return 10 * math.log10(Pin / PL)


print("1. Mismatched-line total loss, 30 m of line (formula; exact bookkeeping check)")
A = a_rg58(14) * 0.30
for s in (3.0, 10.0):
    g = gamma_from_swr(s)
    ZL = 50 * s  # resistive load at the high-impedance side
    tf = total_loss_db(A, g)
    te = exact_line_loss(A, ZL, 50.0)
    print(f"  RG-58 14 MHz A={A:.2f} dB, SWR {s}: formula {tf:.3f} dB, exact {te:.3f} dB")
    check(f"formula == exact (SWR {s})", abs(tf - te) < 0.01)

print(f"\n  {'cable':30s} {'f MHz':>5s} {'matched dB':>10s} " + " ".join(f"{'SWR '+str(s):>8s}" for s in (1.5, 3, 10, 20)))
table = {}
for name, fn, z0 in CABLES:
    for f in (3.6, 7.0, 14.0, 28.0):
        A = fn(f) * 0.30
        row = []
        for s in (1.5, 3, 10, 20):
            tl = total_loss_db(A, gamma_from_swr(s))
            row.append(tl)
            table[(name, f, s)] = tl
        print(f"  {name:30s} {f:5.1f} {A:10.2f} " + " ".join(f"{x:8.2f}" for x in row))
check("RG-58 30 m at 28 MHz with SWR 10 loses > 4 dB", table[("RG-58", 28.0, 10)] > 4)
check("ladder line 30 m at 28 MHz with SWR 10 loses < 1.5 dB (RG-58: > 4 dB)", table[("450-ohm ladder (dry, assumed)", 28.0, 10)] < 1.5)
print("  (SWR for ladder line is referred to its own 450 ohm, so the same antenna gives a different SWR"
      " on each line; see the page)")

# a concrete antenna: a 7 MHz half-wave dipole used on 3.6 MHz (Z ~ 10 - j400 ohm, order of magnitude)
print("\n1b. Same antenna (Z = 10 - j400 ohm at 3.6 MHz; 2000 + j500 ohm at 14 MHz) on each line, 30 m")
for f, ZL in ((3.6, complex(10, -400)), (14.0, complex(2000, 500))):
    for name, fn, z0 in CABLES:
        A = fn(f) * 0.30
        g = abs((ZL - z0) / (ZL + z0))
        swr = (1 + g) / (1 - g)
        tl = total_loss_db(A, g)
        print(f"  {f:4.1f} MHz {name:30s}: SWR on line {swr:7.1f}, total loss {tl:6.2f} dB "
              f"({100*10**(-tl/10):5.1f} % reaches antenna)")
A = a_rg58(3.6) * 0.30
g = abs((complex(10, -400) - 50) / (complex(10, -400) + 50))
check("dipole off-band on RG-58 at 3.6 MHz loses > 6 dB", total_loss_db(A, g) > 6)

# ------------------------------------------------------------------ 2. SWR seen at the rig
print("\n2. SWR the rig sees vs SWR at the antenna (RL_in = RL_load + 2A)")
for name, fn, z0 in CABLES[:1]:
    for f in (7.0, 28.0):
        A = fn(f) * 0.30
        for s in (10, 20, 1000):
            g = gamma_from_swr(s)
            gin = g * 10 ** (-A / 10)
            sin = (1 + gin) / (1 - gin)
            print(f"  {name} {f:4.1f} MHz (A={A:.2f} dB): SWR {s:5d} at antenna -> {sin:5.2f} at rig")
A28 = a_rg58(28) * 0.30
gin = 10 ** (-A28 / 10)
check("an OPEN at the end of 30 m RG-58 at 28 MHz reads below 5:1 at the rig",
      (1 + gin) / (1 - gin) < 5.0)

# ------------------------------------------------------------------ 3. matching networks
print("\n3. Matching-network efficiency with lossy parts (exact ABCD, R_s = 50 ohm)")


def abcd_series(Z):
    return np.array([[1, Z], [0, 1]], dtype=complex)


def abcd_shunt(Y):
    return np.array([[1, 0], [Y, 1]], dtype=complex)


def efficiency(M, ZL):
    """Power into ZL / power into the network input, for any input drive."""
    A_, B_, C_, D_ = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
    V2, I2 = 1.0, 1.0 / ZL
    V1 = A_ * V2 + B_ * I2
    I1 = C_ * V2 + D_ * I2
    return (V2 * np.conj(I2)).real / (V1 * np.conj(I1)).real, V1 / I1


def lossy_L(X, Q):   # inductor reactance X>0 with series R = X/Q
    return complex(X / Q, X)


def lossy_C(X, Q):   # capacitor reactance X<0 (Z = jX) with series R = |X|/Q
    return complex(abs(X) / Q, X)


def match_L(ZL, QL, QC=1000.0):
    """Lossless design of an L-network (series L, shunt C on the high side), then lossy evaluation.
    Tries both orientations and both signs, returns best efficiency of a valid lowpass-type solution."""
    best = None
    R0 = 50.0
    RL, XL = ZL.real, ZL.imag
    # case A: shunt element across load (load side high R): Y = 1/ZL + jB ; need Re{1/Y} = 50
    YL = 1 / ZL
    G = YL.real
    if 1 / G > R0:  # load conductance small -> shunt at load side
        for sgn in (1, -1):
            Bt = sgn * math.sqrt(G / R0 - G * G)   # total susceptance so that Re{1/(G+jBt)} = R0
            Bsh = Bt - YL.imag
            Zp = 1 / complex(G, Bt)
            Xs = -Zp.imag
            # components: shunt Bsh (C if >0, L if <0), series Xs (L if >0, C if <0)
            Zsh = 1 / complex(0, Bsh)
            Zsh_l = lossy_C(Zsh.imag, QC) if Zsh.imag < 0 else lossy_L(Zsh.imag, QL)
            Zs_l = lossy_L(Xs, QL) if Xs > 0 else lossy_C(Xs, QC)
            M = abcd_series(Zs_l) @ abcd_shunt(1 / Zsh_l)
            eta, zin = efficiency(M, ZL)
            if best is None or eta > best[0]:
                best = (eta, zin, Xs, Bsh)
    # case B: series element next to load, shunt at the 50-ohm side
    if RL < R0:
        for sgn in (1, -1):
            Xt = sgn * math.sqrt(RL * R0 - RL * RL)  # total series X so shunt can finish match
            Xs = Xt - XL
            Zt = complex(RL, Xt)
            Yt = 1 / Zt
            Bsh = -Yt.imag
            Zsh = 1 / complex(0, Bsh)
            Zsh_l = lossy_C(Zsh.imag, QC) if Zsh.imag < 0 else lossy_L(Zsh.imag, QL)
            Zs_l = lossy_L(Xs, QL) if Xs > 0 else lossy_C(Xs, QC)
            M = abcd_shunt(1 / Zsh_l) @ abcd_series(Zs_l)
            eta, zin = efficiency(M, ZL)
            if best is None or eta > best[0]:
                best = (eta, zin, Xs, Bsh)
    return best


def match_T(ZL, X1, QL, QC=1000.0):
    """High-pass T: series C (X1<0) at input, shunt L, series C (X2) at load. Lossless design for a
    given X1, lossy evaluation. Returns (eta, zin) or None if no high-pass solution."""
    R0 = 50.0
    Zt_in = complex(R0, -X1)        # what the shunt-L || (jX2 + ZL) must look like
    Yt = 1 / Zt_in
    Gt = Yt.real
    RL = ZL.real
    disc = RL / Gt - RL * RL
    if disc < 0:
        return None
    best = None
    for sgn in (1, -1):
        Xtot = sgn * math.sqrt(disc)
        X2 = Xtot - ZL.imag
        if X2 >= 0:
            continue  # need a capacitor
        Yb = 1 / complex(RL, Xtot)
        Bsh = Yt.imag - Yb.imag
        if Bsh >= 0:
            continue  # need an inductor (negative susceptance)
        XLsh = -1 / Bsh
        M = abcd_series(lossy_C(X1, QC)) @ abcd_shunt(1 / lossy_L(XLsh, QL)) @ abcd_series(lossy_C(X2, QC))
        eta, zin = efficiency(M, ZL)
        if best is None or eta > best[0]:
            best = (eta, zin, XLsh)
    return best


loads = [("5 - j500 (short HF whip)", complex(5, -500)), ("10 - j400 (dipole at 1/2 f)", complex(10, -400)),
         ("12.5 + j0", complex(12.5, 0)), ("25 + j25", complex(25, 25)), ("200 + j0", complex(200, 0)),
         ("2000 + j500 (EFHW-ish)", complex(2000, 500))]
print(f"  {'load':28s} {'Q_u':>4s} {'L-net loss dB':>13s} {'T best dB':>10s} {'T small-C dB':>13s} {'Q_n':>6s}")
lres = {}
for lab, ZL in loads:
    for Q in (100, 200, 300):
        bl = match_L(ZL, Q)
        l_loss = -10 * math.log10(bl[0]) if bl else float("nan")
        # sweep T input capacitor reactance from -10 to -2000 ohm
        tlosses = []
        for X1 in np.linspace(-2000, -5, 400):
            r = match_T(ZL, X1, Q)
            if r:
                tlosses.append((-10 * math.log10(r[0]), X1))
        tbest = min(tlosses)[0] if tlosses else float("nan")
        # "small C" = most negative X1 that still solves (large reactance -> small capacitance)
        tsmall = [t for t in tlosses if t[1] < -1000]
        tsm = max(tsmall)[0] if tsmall else float("nan")
        Rh, Rl = max(abs(ZL), 50.0), min(ZL.real, 50.0)
        qn = math.sqrt(max(Rh / Rl - 1, 0))
        lres[(lab, Q)] = l_loss
        print(f"  {lab:28s} {Q:4d} {l_loss:13.2f} {tbest:10.2f} {tsm:13.2f} {qn:6.1f}")
check("L-network into 12.5 ohm with Q_u 200 loses < 0.1 dB", lres[("12.5 + j0", 200)] < 0.1)
check("matching a 5 - j500 whip loses > 1 dB even with Q_u 300 (loading-coil loss)", lres[("5 - j500 (short HF whip)", 300)] > 1)

# ------------------------------------------------------------------ 4. Q_n / Q_u rule
print("\n4. L-network rule of thumb: loss fraction ~ Q_n/Q_u (series-element loss, resistive loads)")
for R in (12.5, 5.0, 2.0):
    for Q in (100, 300):
        b = match_L(complex(R, 0), Q, QC=1e9)
        exact = 1 - b[0]
        qn = math.sqrt(50 / R - 1)
        print(f"  R {R:5.1f} ohm, Q_u {Q}: exact loss fraction {exact:.4f}, Q_n/Q_u {qn/Q:.4f}")
        check(f"rule within 20 % (R={R}, Q={Q})", abs(exact - qn / Q) / (qn / Q) < 0.2)

# ------------------------------------------------------------------ 5. auto-tuner
print("\n5. Relay auto-tuner state space")
nL, nC = 7, 7
states = 2 ** nL * 2 ** nC * 2
print(f"  7 L x 7 C relays + C-side relay: {states} states; at ~5 ms relay settle + measure, exhaustive "
      f"= {states*5e-3:.0f} s; coarse-fine search (e.g. 2 x (16 + 16) steps per axis pass) ~ "
      f"{(2*(2**4+2**4)+2*2*8)*5e-3:.2f} s")
check("state count 32768", states == 32768)

print("\nRESULT:", "ALL PASS" if not FAIL else f"{len(FAIL)} FAIL: {FAIL}")
