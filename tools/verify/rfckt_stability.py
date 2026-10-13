#!/usr/bin/env python3
"""Verification for kb/06-rf-circuits/amplifier-stability-and-biasing.md

Checks
 A. Monte-Carlo: mu>1  <=>  mu'>1  <=>  (K>1 and |Delta|<1)  <=>  (K>1 and B1>0)
 B. Brute force: mu>1 <=> no passive Gamma_L gives |Gamma_in|>=1 and no passive Gamma_S gives |Gamma_out|>=1
 C. mu equals the distance from the Smith-chart centre to the nearest unstable Gamma_L (Edwards & Sinsky 1992)
 D. Stability-circle centre/radius formula vs brute-force boundary |Gamma_in| = 1
 E. Our K vs scikit-rf Network.stability; MSG/MAG vs the ATF-54143 data-sheet column
 F. ATF-54143 (3 V, 60 mA): K, mu over 0.1-10 GHz; stabilisation by output shunt R and by series R
 G. Extra common-source inductance (PCB via) degrades high-frequency stability
 H. Bias-network arithmetic for the data-sheet passive-bias example (R1, R2, R3)
Run:  python3 tools/verify/rfckt_stability.py
"""
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rfckt_atf54143_data import s_matrix_table, S_TABLE, interp_s

rng = np.random.default_rng(1)
ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


# ---------------------------------------------------------------- core formulas
def delta(S):
    return S[..., 0, 0] * S[..., 1, 1] - S[..., 0, 1] * S[..., 1, 0]


def K_factor(S):
    D = delta(S)
    return (1 - abs(S[..., 0, 0]) ** 2 - abs(S[..., 1, 1]) ** 2 + abs(D) ** 2) / (2 * abs(S[..., 0, 1] * S[..., 1, 0]))


def mu(S):
    D = delta(S)
    return (1 - abs(S[..., 0, 0]) ** 2) / (abs(S[..., 1, 1] - D * np.conj(S[..., 0, 0])) + abs(S[..., 0, 1] * S[..., 1, 0]))


def mu_p(S):
    D = delta(S)
    return (1 - abs(S[..., 1, 1]) ** 2) / (abs(S[..., 0, 0] - D * np.conj(S[..., 1, 1])) + abs(S[..., 0, 1] * S[..., 1, 0]))


def B1(S):
    return 1 + abs(S[..., 0, 0]) ** 2 - abs(S[..., 1, 1]) ** 2 - abs(delta(S)) ** 2


def load_circle(S):
    """Output (load-plane) stability circle: locus of Gamma_L giving |Gamma_in| = 1."""
    D = delta(S)
    den = abs(S[..., 1, 1]) ** 2 - abs(D) ** 2
    C = np.conj(S[..., 1, 1] - D * np.conj(S[..., 0, 0])) / den
    R = abs(S[..., 0, 1] * S[..., 1, 0] / den)
    return C, R


def source_circle(S):
    D = delta(S)
    den = abs(S[..., 0, 0]) ** 2 - abs(D) ** 2
    C = np.conj(S[..., 0, 0] - D * np.conj(S[..., 1, 1])) / den
    R = abs(S[..., 0, 1] * S[..., 1, 0] / den)
    return C, R


def gamma_in(S, GL):
    return S[0, 0] + S[0, 1] * S[1, 0] * GL / (1 - S[1, 1] * GL)


def gamma_out(S, GS):
    return S[1, 1] + S[0, 1] * S[1, 0] * GS / (1 - S[0, 0] * GS)


def msg_mag_db(S):
    k = K_factor(S)
    ratio = abs(S[..., 1, 0] / S[..., 0, 1])
    b1 = B1(S)
    with np.errstate(invalid='ignore'):
        mag = ratio * (k - np.sign(b1) * np.sqrt(np.maximum(k ** 2 - 1, 0)))
    return np.where(k > 1, 10 * np.log10(mag), 10 * np.log10(ratio))


def random_S(n):
    """Random 2-port S matrices, a mix of passive-ish and gainy devices."""
    S = np.zeros((n, 2, 2), complex)
    for (i, j), scale in {(0, 0): 1.1, (1, 1): 1.1, (0, 1): 0.6, (1, 0): 4.0}.items():
        S[:, i, j] = scale * rng.random(n) ** 0.7 * np.exp(2j * np.pi * rng.random(n))
    return S


# ---------------------------------------------------------------- A. equivalences
S = random_S(200000)
m, mp, k, dmag, b1 = mu(S), mu_p(S), K_factor(S), abs(delta(S)), B1(S)
margin = (abs(m - 1) > 1e-6) & (abs(k - 1) > 1e-6) & (abs(dmag - 1) > 1e-6) & (abs(mp - 1) > 1e-6)
c1 = (m > 1)[margin]
c2 = (mp > 1)[margin]
c3 = ((k > 1) & (dmag < 1))[margin]
c4 = ((k > 1) & (b1 > 0))[margin]
print(f"A: {margin.sum()} random 2-ports, {c1.sum()} unconditionally stable by mu")
check("A1 mu>1 <=> mu'>1", np.all(c1 == c2))
check("A2 mu>1 <=> K>1 & |Delta|<1", np.all(c1 == c3))
check("A3 mu>1 <=> K>1 & B1>0", np.all(c1 == c4))
# K>1 alone is NOT sufficient: count cases with K>1 but mu<1
print(f"   cases with K>1 but not unconditionally stable: {np.sum((k > 1) & ~(m > 1))}")
check("A4 K>1 alone is insufficient (counter-examples exist)", np.sum((k > 1) & ~(m > 1)) > 0)

# ---------------------------------------------------------------- B. brute force
r = np.sqrt(rng.random(4000)) * 0.99999
th = 2 * np.pi * rng.random(4000)
G = np.concatenate([r * np.exp(1j * th), 0.99999 * np.exp(1j * np.linspace(0, 2 * np.pi, 2000))])
Sb = random_S(3000)
agree = 0
for s in Sb:
    gi = abs(gamma_in(s, G)).max()
    go = abs(gamma_out(s, G)).max()
    brute_stable = (gi < 1) and (go < 1) and abs(s[0, 0]) < 1 and abs(s[1, 1]) < 1
    mu_stable = mu(s[None])[0] > 1
    if abs(mu(s[None])[0] - 1) < 2e-3:  # too close to the boundary for sampling
        agree += 1
        continue
    agree += (brute_stable == mu_stable)
check(f"B  brute-force unit-disk sweep agrees with mu test ({agree}/{len(Sb)})", agree == len(Sb))

# ---------------------------------------------------------------- C. geometric meaning of mu
worst = 0.0
for s in random_S(2000):
    mval = mu(s[None])[0]
    if not (abs(s[0, 0]) < 1):
        continue
    C, R = load_circle(s[None])
    C, R = C[0], R[0]
    # which side of the circle is unstable?  test a point just inside the circle
    test_in = C + 0.0 * R
    inside_unstable = abs(gamma_in(s, np.array([test_in])))[0] > 1
    if inside_unstable:
        dist = abs(C) - R          # origin is stable (|S11|<1) so it lies outside the circle
    else:
        dist = R - abs(C)          # unstable region is the exterior of the circle
    worst = max(worst, abs(dist - mval))
check(f"C  mu = distance(origin -> nearest unstable Gamma_L), max err {worst:.2e}", worst < 1e-9)

# ---------------------------------------------------------------- D. circle formula
worst = 0.0
for s in random_S(500):
    C, R = load_circle(s[None])
    pts = C[0] + R[0] * np.exp(1j * np.linspace(0, 2 * np.pi, 50))
    worst = max(worst, np.max(abs(abs(gamma_in(s, pts)) - 1)))
check(f"D  |Gamma_in| = 1 on the load stability circle, max err {worst:.2e}", worst < 1e-8)

# ---------------------------------------------------------------- E. skrf + datasheet MSG/MAG
import skrf as rf
f, Sd = s_matrix_table()
ntw = rf.Network(frequency=rf.Frequency.from_f(f, unit='hz'), s=Sd, z0=50)
check("E1 our K equals skrf Network.stability", np.allclose(ntw.stability, K_factor(Sd)))
mm = msg_mag_db(Sd)
err = mm - S_TABLE[:, 9]
print("   f_GHz  K      mu     |Delta|  MSG/MAG(ours)  datasheet  err")
for fi, ki, mi, di, a, b, e in zip(f / 1e9, K_factor(Sd), mu(Sd), abs(delta(Sd)), mm, S_TABLE[:, 9], err):
    print(f"   {fi:5.1f} {ki:6.3f} {mi:6.3f} {di:6.3f}   {a:7.2f}      {b:7.2f}  {e:+.2f}")
check("E2 MSG/MAG reproduces datasheet column within 0.6 dB (table rounding of |S12|)", np.max(abs(err)) < 0.6)

# ---------------------------------------------------------------- F. stabilisation of ATF-54143
fs = np.concatenate([np.linspace(0.1e9, 10e9, 400)])
Sf = interp_s(fs)
freq = rf.Frequency.from_f(fs, unit='hz')
dev = rf.Network(frequency=freq, s=Sf, z0=50)
line = rf.media.DefinedGammaZ0(frequency=freq, z0=50)
print(f"F: bare device  min K = {K_factor(Sf).min():.3f}, min mu = {mu(Sf).min():.3f} "
      f"(at {fs[np.argmin(mu(Sf))]/1e9:.2f} GHz)")


def shunt_R_out(R):
    return dev ** line.shunt_resistor(R)


def series_R_out(R):
    return dev ** line.resistor(R)


def series_R_in(R):
    return line.resistor(R) ** dev


results = {}
i433 = np.argmin(abs(fs - 433e6))
i1575 = np.argmin(abs(fs - 1575e6))
for lo in (0.4e9, 0.1e9):
    band = fs >= lo
    for name, fn, grid in [("shunt R at drain", shunt_R_out, np.arange(1000, 4, -1.0)),
                           ("series R at drain", series_R_out, np.arange(0, 400.1, 1.0)),
                           ("series R at gate", series_R_in, np.arange(0, 400.1, 1.0))]:
        found = None
        for R in grid:
            n = fn(R)
            if mu(n.s)[band].min() > 1.0:
                found = (R, n)
                break
        if found:
            R, n = found
            results[(lo, name)] = R
            print(f"   band {lo/1e9:.1f}-10 GHz, {name:18s}: R = {R:5.0f} ohm -> MAG 433 MHz "
                  f"{msg_mag_db(n.s)[i433]:.1f} dB (bare MSG {msg_mag_db(Sf)[i433]:.1f}), "
                  f"1575 MHz {msg_mag_db(n.s)[i1575]:.1f} dB (bare {msg_mag_db(Sf)[i1575]:.1f})")
        else:
            print(f"   band {lo/1e9:.1f}-10 GHz, {name:18s}: no single value works")
check("F1 device is only conditionally stable below ~ 3.7 GHz (mu<1)", mu(Sf).min() < 1)
check("F2 single-resistor stabilisation over 0.4-10 GHz needs heavy values (shunt <= 20 ohm)",
      results.get((0.4e9, "shunt R at drain"), 1e9) <= 20)

# Frequency-selective stabiliser: gate LF termination (100 ohm + 100 nH to ground),
# drain series 22 ohm, drain LF termination (47 ohm + 10 nH), drain HF loading (220 ohm + 2 pF)
from rfckt_noise2port import device, series_z, shunt_y, cascade, noise_params, abcd_to_s
from rfckt_atf54143_data import interp_noise
w = 2 * np.pi * fs
fmin_l, gopt, rn = interp_noise(fs)
dv = device(Sf, fmin_l, gopt, rn)
gate_sh = shunt_y(1 / (100 + 1j * w * 100e-9))
drn_ser = series_z(22 * np.ones_like(fs))
drn_lf = shunt_y(1 / (47 + 1j * w * 10e-9))
drn_hf = shunt_y(1 / (220 + 1 / (1j * w * 2e-12)))
net = cascade(gate_sh, dv, drn_ser, drn_lf, drn_hf)
Sst = abcd_to_s(net[0])
Fm0, _, _ = noise_params(dv[1])
Fm1, Zo1, _ = noise_params(net[1])
print(f"   frequency-selective network: min mu 0.1-10 GHz = {mu(Sst).min():.2f}; "
      f"MAG 433 = {msg_mag_db(Sst)[i433]:.1f} dB, 1575 = {msg_mag_db(Sst)[i1575]:.1f} dB")
print(f"   NFmin 433 MHz: bare {10*np.log10(Fm0[i433]):.2f} dB -> stabilised {10*np.log10(Fm1[i433]):.2f} dB; "
      f"1575 MHz: {10*np.log10(Fm0[i1575]):.2f} -> {10*np.log10(Fm1[i1575]):.2f} dB")
# compare: series gate resistor that stabilises 0.4-10 GHz
Rg = results.get((0.4e9, "series R at gate"))
netg = cascade(series_z(Rg * np.ones_like(fs)), dv)
Fmg, _, _ = noise_params(netg[1])
print(f"   series gate R = {Rg:.0f} ohm: NFmin 433 MHz = {10*np.log10(Fmg[i433]):.2f} dB, 1575 MHz = {10*np.log10(Fmg[i1575]):.2f} dB")
check("F3 frequency-selective network is unconditionally stable 0.1-10 GHz", mu(Sst).min() > 1)
check("F4 ...and costs far less NFmin than a stabilising series gate resistor",
      Fm1[i433] < Fmg[i433] and Fm1[i1575] < Fmg[i1575])

# ---------------------------------------------------------------- G. source-lead inductance
def add_common_lead_L(S, fhz, L):
    """Add series inductance L (H) in the common (source) lead of a 2-port (common-source S)."""
    z = rf.network.s2z(S, 50)
    zl = 1j * 2 * np.pi * fhz * L
    z2 = z + zl[:, None, None] * np.ones((1, 2, 2))
    return rf.network.z2s(z2, 50)


for L in [0.0, 0.2e-9, 0.5e-9, 1.0e-9]:
    S2 = add_common_lead_L(Sf, fs, L)
    band = fs > 3e9
    print(f"G: extra source L = {L*1e9:.1f} nH -> min mu (3-10 GHz) = {mu(S2)[band].min():.3f}; "
          f"|S11| at 1575 MHz = {abs(S2[np.argmin(abs(fs-1575e6)),0,0]):.3f}")
S05 = add_common_lead_L(Sf, fs, 0.5e-9)
check("G1 0.5 nH of extra source inductance lowers high-frequency mu", mu(S05)[fs > 3e9].min() < mu(Sf)[fs > 3e9].min())

# ---------------------------------------------------------------- H. bias arithmetic (data-sheet example)
VDD, Vds, Ids, Vgs, IBB = 5.0, 3.0, 0.060, 0.59, 0.002
R1 = Vgs / IBB
R2 = (Vds - Vgs) * R1 / Vgs
R3 = (VDD - Vds) / (Ids + IBB)
print(f"H: passive bias R1={R1:.0f} ohm R2={R2:.0f} ohm R3={R3:.1f} ohm (datasheet 295/1205/32.3)")
check("H1 passive bias values reproduce the ATF-54143 data-sheet example", abs(R1 - 295) < 1 and abs(R2 - 1205) < 2 and abs(R3 - 32.3) < 0.1)

# Drain-feedback sensitivity: d(Id)/d(Vth) for fixed-Vgs vs drain-fed divider
gm = 0.41  # S, data-sheet typ. transconductance
Rpar = R1 * R2 / (R1 + R2)
# with divider from the drain node: Vg = Vd*R1/(R1+R2); Vd = VDD - (Id+IBB)*R3
# linearise: dId = gm*(dVg - dVth), dVg = -(R1/(R1+R2))*R3*dId  ->  dId/dVth = -gm/(1+gm*R3*R1/(R1+R2))
sens_fixed = gm
sens_fb = gm / (1 + gm * R3 * R1 / (R1 + R2))
print(f"   |dId/dVth| fixed gate: {sens_fixed*1e3:.0f} mA/V; drain-fed divider: {sens_fb*1e3:.0f} mA/V "
      f"-> a 0.1 V threshold shift moves Id by {sens_fixed*100:.0f} mA vs {sens_fb*100:.1f} mA")
check("H2 drain-fed divider reduces bias sensitivity", sens_fb < sens_fixed / 2)

# ---------------------------------------------------------------- I. Rollett invariants
# K is invariant under lossless reciprocal port embeddings (matching networks cannot stabilise);
# MSG = |S21/S12| is invariant under ANY reciprocal port embedding (lossy too).
emb_in = m_in = line.shunt_capacitor(3e-12) ** line.inductor(8e-9) ** line.line(37, 'deg', z0=75)
emb_out = line.inductor(5e-9) ** line.shunt_capacitor(2e-12) ** line.line(20, 'deg', z0=35)
emb = emb_in ** dev ** emb_out
check("I1 K unchanged by lossless reciprocal embedding (Rollett invariant)",
      np.allclose(K_factor(emb.s), K_factor(dev.s), rtol=1e-9))
lossy = line.resistor(15) ** dev ** line.shunt_resistor(80)
check("I2 MSG=|S21/S12| unchanged by lossy reciprocal embedding",
      np.allclose(abs(lossy.s[:, 1, 0] / lossy.s[:, 0, 1]), abs(dev.s[:, 1, 0] / dev.s[:, 0, 1]), rtol=1e-9))
check("I3 ...but lossy embedding does change K (that is how resistors stabilise)",
      not np.allclose(K_factor(lossy.s), K_factor(dev.s)))

# ---------------------------------------------------------------- J. BJT bias sensitivity to beta
Vcc, Vce, Ic0, beta0, Vbe = 5.0, 3.0, 10e-3, 100, 0.8
RC = (Vcc - Vce) / (Ic0 + Ic0 / beta0)
RB = (Vce - Vbe) / (Ic0 / beta0)
RBfix = (Vcc - Vbe) / (Ic0 / beta0)                   # base resistor straight from Vcc
print(f"J: collector-feedback bias RC = {RC:.0f} ohm, RB = {RB/1e3:.1f} kohm; fixed-base RB = {RBfix/1e3:.0f} kohm")
for b in (50, 100, 200):
    ic_fb = b * (Vcc - Vbe) / (RB + (b + 1) * RC)
    ic_fx = b * (Vcc - Vbe) / RBfix
    print(f"   beta {b:3d}: Ic collector-feedback {ic_fb*1e3:5.2f} mA, fixed base {ic_fx*1e3:5.2f} mA")
ic50 = 50 * (Vcc - Vbe) / (RB + 51 * RC); ic200 = 200 * (Vcc - Vbe) / (RB + 201 * RC)
check("J1 collector feedback compresses a 4:1 beta spread to about 2:1 in Ic", ic200 / ic50 < 2.2)

# bias-tee choke / block rules: loss and return loss of a shunt reactance X across 50 ohm
for ratio in (3, 5, 10):
    X = ratio * 50
    s21 = 2 * 1j * X / (2 * 1j * X + 50)
    s11 = -50 / (2 * 1j * X + 50)
    print(f"   shunt choke X = {ratio:2d} x Z0: insertion loss {-20*np.log10(abs(s21)):.3f} dB, RL {-20*np.log10(abs(s11)):.1f} dB")
for ratio in (0.1, 0.3):
    X = ratio * 50
    s21 = 2 * 50 / (2 * 50 - 1j * X)
    print(f"   series block X = {ratio} x Z0: insertion loss {-20*np.log10(abs(s21)):.3f} dB")
L433 = 5 * 50 / (2 * np.pi * 433e6); C433 = 1 / (2 * np.pi * 433e6 * 5)
print(f"   433 MHz: choke for X = 250 ohm -> {L433*1e9:.0f} nH; block cap for X = 5 ohm -> {C433*1e12:.0f} pF")
fres = 1 / (2 * np.pi * np.sqrt(100e-9 * 100e-9))
print(f"   choke 100 nH + bypass 100 nF series resonance = {fres/1e6:.2f} MHz")

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
sys.exit(0 if ok_all else 1)
