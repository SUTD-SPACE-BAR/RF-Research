#!/usr/bin/env python3
"""W5-S15 / G-06-04 — broadband transformer splitters, multicouplers and broadband PAs (ngspice).
Pages: kb/06-rf-circuits/couplers-dividers-combiners.md ("Level 3 — broadband transformer hybrids ...")
       kb/06-rf-circuits/power-amplifiers.md ("Level 3 — broadband PAs: feedback and transformer-coupled push-pull")

 A. 0-degree 2-way transformer splitter (Mini-Circuits style): T1 50->25 ohm autotransformer + centre-tapped
    hybrid T2 with 100 ohm between the outputs. The hybrid is a DISCRETISED BIFILAR WINDING on ferrite
    (self L, mutual kL, inter-conductor C, N sections): k -> 1 with no C is a flux-coupled transformer;
    finite k with C makes the differential (even-split) path a transmission line of
    Z_dm = sqrt(2L(1-k)/C) (= a TLT). A1 ideal response; A2 low edge from magnetising/common-mode L;
    A3 high edge from leakage (flux-coupled) vs line impedance/length (TLT); best Z_dm.
 B. 180-degree hybrid transformer: add a Delta winding (L = 2 x half winding); the 0-deg splitter's 100 ohm
    resistor IS the terminated Delta port.
 C. Receiver multicoupler cascade (LNA then 4-way split) vs passive split: NF, IIP3, port-to-port leakage.
 D. Shunt-series feedback broadband amplifier: R_f R_E = Z0^2 -> S11 = S22 = 0, S21 = (Z0 - R_f)/Z0 exact
    (VCCS) and ngspice with a BJT model.
 E. Transformer-coupled push-pull PA: R_cc = 2(V-Vk)^2/P, even-harmonic cancellation vs imbalance.
Run: python3 tools/verify/s15_tlt_splitter.py   (needs ngspice; about 20 s)
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rf2_common import ngspice, check, finish, db20

Z0 = 50.0


# ------------------------------------------------------------------ netlist builders
def bifilar(name, a_x, a_y, b_x, b_y, L, k, C, nsec=24):
    """two coupled conductors a (a_x->a_y) and b (b_x->b_y) wound together, dots at the x ends.
    Total self inductance L each, mutual k L, total inter-conductor capacitance C (split along length)."""
    out = []
    na = [a_x] + [f"{name}a{i}" for i in range(1, nsec)] + [a_y]
    nb = [b_x] + [f"{name}b{i}" for i in range(1, nsec)] + [b_y]
    Ls = L / nsec
    for i in range(nsec):
        out.append(f"L{name}a{i} {na[i]} {na[i+1]} {Ls:.6e}")
        out.append(f"L{name}b{i} {nb[i]} {nb[i+1]} {Ls:.6e}")
        out.append(f"K{name}{i} L{name}a{i} L{name}b{i} {k:.6f}")
        if C > 0:
            c = C / nsec
            out.append(f"C{name}m{i} {na[i+1]} {nb[i+1]} {c:.6e}")
    # NOTE: mutual coupling between different sections is neglected (sections on the same core are in reality
    # all coupled); this keeps the line model local. Even/odd checks below use the lumped limit to cross-check.
    return out


def ports(nodes, drive):
    """50-ohm ports; 'drive' index gets a 2 V AC source behind 50 ohm (incident wave 1 V)."""
    out = []
    for i, n in enumerate(nodes):
        if i == drive:
            out.append(f"V{i} s{i} 0 AC 2")
            out.append(f"R{i} s{i} {n} {Z0}")
        else:
            out.append(f"R{i} {n} 0 {Z0}")
    return out


def autotransformer(inp, tap, Lt, k):
    """50 -> 25 ohm: input across full winding, output at the 1/sqrt2 tap. Lt = full-winding inductance."""
    n = 1 / np.sqrt(2)
    La = Lt * n ** 2; Lb = Lt * (1 - n) ** 2
    return [f"LT1a {tap} 0 {La:.6e}", f"LT1b {inp} {tap} {Lb:.6e}", f"KT1 LT1a LT1b {k:.6f}"]


def splitter_S(hyb, t1=(3.2e-6, 0.9995), f=(1e5, 3e9), lumped=False):
    """S-parameters of the 0-degree splitter: port 1 = input, 2/3 = outputs. hyb = dict(L,k,C)."""
    Lt, kt = t1
    body_common = autotransformer("p1", "c", Lt, kt)
    if lumped:   # single lumped coupled pair (no distributed C): flux-coupled centre-tapped hybrid
        body_common += [f"LH1 p2 c {hyb['L']:.6e}", f"LH2 c p3 {hyb['L']:.6e}", f"KH LH1 LH2 {hyb['k']:.6f}"]
    else:
        # conductor a: p2 (x) -> c (y); conductor b: c (x) -> p3 (y)  => winding p2-c-p3, series aiding
        body_common += bifilar("H", "p2", "c", "c", "p3", hyb['L'], hyb['k'], hyb['C'])
    body_common += [f"RISO p2 p3 {2*Z0}"]
    S = {}
    an = f".ac dec 60 {f[0]} {f[1]}"
    fr = None
    for d in (0, 1):
        body = "\n".join(body_common + ports(["p1", "p2", "p3"], d))
        fr, (v1, v2, v3) = ngspice(body, an, ["v(p1)", "v(p2)", "v(p3)"])
        v = [v1, v2, v3]
        for i in range(3):
            S[(i + 1, d + 1)] = v[i] - (1 if i == d else 0)
    return fr, S


def band(fr, ok):
    """longest contiguous frequency span where ok is True"""
    best = (np.nan, np.nan); run = None
    for i, o in enumerate(ok):
        if o and run is None:
            run = i
        if (not o or i == len(ok) - 1) and run is not None:
            j = i if o else i - 1
            if np.isnan(best[0]) or fr[j] / fr[run] > best[1] / best[0]:
                best = (fr[run], fr[j])
            run = None
    return best


def splitter_metrics(fr, S, il_tol=0.5, rl=15.0, iso=20.0):
    s21 = db20(S[(2, 1)]); s31 = db20(S[(3, 1)])
    ok = (abs(s21 + 3.01) < il_tol) & (abs(s31 + 3.01) < il_tol) & (db20(S[(1, 1)]) < -rl) \
         & (db20(S[(2, 2)]) < -rl) & (db20(S[(3, 2)]) < -iso)
    return band(fr, ok)


# ================================================================ A. 0-degree splitter
print("A: 0-deg transformer splitter, T1 50->25 ohm autotransformer + centre-tapped hybrid T2 + 100 ohm")
# A1 near-ideal: tight lumped coupling
fr, S = splitter_S(dict(L=1.6e-6, k=0.99995, C=0), lumped=True, t1=(3.2e-6, 0.99995))
i100 = np.argmin(abs(fr - 100e6))
print(f"   near-ideal (k = 0.99995): at 100 MHz S21 {db20(S[(2,1)][i100]):.3f} dB, S31 {db20(S[(3,1)][i100]):.3f} dB, "
      f"phase S21-S31 {np.degrees(np.angle(S[(2,1)][i100]/S[(3,1)][i100])):.2f} deg, S11 {db20(S[(1,1)][i100]):.1f} dB, "
      f"S22 {db20(S[(2,2)][i100]):.1f} dB, isolation S32 {db20(S[(3,2)][i100]):.1f} dB")
check("A1 ideal transformer splitter: -3.01 dB in phase, matched, isolated (like a Wilkinson)",
      abs(db20(S[(2, 1)][i100]) + 3.01) < 0.02 and db20(S[(1, 1)][i100]) < -30 and db20(S[(3, 2)][i100]) < -40)
lo = splitter_metrics(fr, S)
print(f"   band (|IL-3.01| < 0.5 dB, RL > 15 dB, isolation > 20 dB): {lo[0]/1e6:.2f} - {lo[1]/1e6:.0f} MHz")
# A2 low-frequency edge vs hybrid magnetising inductance
print("   A2 low edge vs hybrid half-winding inductance (T1 kept large):")
lows = {}
for Lh in (0.4e-6, 1.6e-6, 6.4e-6):
    fr2, S2 = splitter_S(dict(L=Lh, k=0.99995, C=0), lumped=True, t1=(30e-6, 0.99995), f=(1e4, 1e9))
    b = splitter_metrics(fr2, S2); lows[Lh] = b[0]
    # odd mode sees the full winding 4 Lh (k~1) in parallel with R/2 per side -> isolation edge when 2*pi*f*4Lh ~ R_iso
    print(f"      L_half {Lh*1e6:4.1f} uH: lower band edge {b[0]/1e6:6.3f} MHz; "
          f"(2 pi f_L x 4 L_half)/100 ohm = {2*np.pi*b[0]*4*Lh/100:.2f}")
check("A2 low edge scales as 1/L (x4 L -> /4 f_L within 15 %)", abs(lows[0.4e-6] / lows[1.6e-6] / 4 - 1) < 0.15
      and abs(lows[1.6e-6] / lows[6.4e-6] / 4 - 1) < 0.15)
# A3 high edge: flux-coupled leakage vs TLT line
print("   A3 high edge — flux-coupled (no inter-winding C) vs transmission-line (bifilar) hybrid, L_half 1.6 uH:")
hi = {}
for k in (0.99, 0.999):
    fr3, S3 = splitter_S(dict(L=1.6e-6, k=k, C=0), lumped=True)
    b = splitter_metrics(fr3, S3); hi[("flux", k)] = b[1]
    print(f"      flux-coupled k = {k}: leakage 2(1-k)L = {2*(1-k)*1.6e-6*1e9:5.1f} nH -> upper edge {b[1]/1e6:7.1f} MHz")
L = 1.6e-6
print("      TLT: fixed line delay (physical length), sweep line impedance Z_dm (L_dm = Z td, C = td/Z):")
for td in (64e-12, 200e-12):
    for Zdm in (25.0, 35.4, 50.0, 70.7, 100.0):
        Ldm = Zdm * td; C = td / Zdm; k = 1 - Ldm / (2 * L)
        fr3, S3 = splitter_S(dict(L=L, k=k, C=C))
        b = splitter_metrics(fr3, S3); hi[("tlt", td, Zdm)] = b[1]
        print(f"      td {td*1e12:4.0f} ps, Z_dm {Zdm:5.1f} ohm (k {k:.5f}, C {C*1e12:5.2f} pF): upper edge {b[1]/1e6:7.1f} MHz "
              f"= {b[1]*td:.3f}/td (line {360*b[1]*td:.0f} deg)")
best = {td: max((v, key[2]) for key, v in hi.items() if key[0] == "tlt" and key[1] == td) for td in (64e-12, 200e-12)}
for td, (v, z) in best.items():
    print(f"   -> td {td*1e12:.0f} ps: best Z_dm = {z} ohm, f_hi = {v/1e6:.0f} MHz, i.e. line ≈ {360*v*td:.0f} deg long at the top edge")
check("A3 TLT hybrid: at fixed line length the best line impedance is ~50-71 ohm; f_hi*td ~ 0.04-0.08 (line ~15-30 deg)",
      all(z in (50.0, 70.7) for v, z in best.values()) and all(0.03 < v * td < 0.09 for td, (v, z) in best.items()))

# ================================================================ B. 180-degree hybrid
print("B: 180-deg transformer hybrid: Sigma port via T1 at the centre tap, Delta winding (L = 2 L_half) — no resistor")
Lh, k = 1.6e-6, 0.99995
body0 = autotransformer("p1", "c", 3.2e-6, k) + [
    f"LH1 p2 c {Lh:.6e}", f"LH2 c p3 {Lh:.6e}", f"LH3 p4 0 {2*Lh:.6e}",
    f"KH12 LH1 LH2 {k}", f"KH13 LH1 LH3 {k}", f"KH23 LH2 LH3 {k}"]
SB = {}
for d in (0, 1, 3):
    body = "\n".join(body0 + ports(["p1", "p2", "p3", "p4"], d))
    frb, vs = ngspice(body, ".ac dec 40 1e6 1e9", ["v(p1)", "v(p2)", "v(p3)", "v(p4)"])
    for i in range(4):
        SB[(i + 1, d + 1)] = vs[i] - (1 if i == d else 0)
j = np.argmin(abs(frb - 100e6))
ph24 = np.degrees(np.angle(SB[(2, 4)][j] / SB[(3, 4)][j]))
print(f"   at 100 MHz: Sigma->2,3 {db20(SB[(2,1)][j]):.2f}/{db20(SB[(3,1)][j]):.2f} dB (phase diff "
      f"{np.degrees(np.angle(SB[(2,1)][j]/SB[(3,1)][j])):.2f} deg); Delta->2,3 {db20(SB[(2,4)][j]):.2f}/{db20(SB[(3,4)][j]):.2f} dB "
      f"(phase diff {ph24:.2f} deg); Sigma-Delta isolation {db20(SB[(4,1)][j]):.1f} dB; output isolation {db20(SB[(3,2)][j]):.1f} dB; "
      f"S44 {db20(SB[(4,4)][j]):.1f} dB")
check("B1 180-deg hybrid: in-phase from Sigma, anti-phase from Delta, Sigma/Delta and output ports isolated",
      abs(abs(ph24) - 180) < 1 and abs(db20(SB[(2, 1)][j]) + 3.01) < 0.05 and db20(SB[(4, 1)][j]) < -40
      and db20(SB[(3, 2)][j]) < -40 and db20(SB[(4, 4)][j]) < -30)

# ================================================================ C. multicoupler
print("C: 433 MHz receiver multicoupler — 4 receivers (NF 6 dB, IIP3 -10 dBm) from one antenna")


def cascade(stages):
    """stages: list of (gain_dB, NF_dB, IIP3_dBm or None); returns NF_dB, IIP3_dBm"""
    F = 1.0; G = 1.0; inv_iip3 = 0.0
    for g_db, nf_db, iip3 in stages:
        F += (10 ** (nf_db / 10) - 1) / G
        if iip3 is not None:
            inv_iip3 += G / (1e-3 * 10 ** (iip3 / 10))
        G *= 10 ** (g_db / 10)
    return 10 * np.log10(F), 10 * np.log10(1 / inv_iip3 / 1e-3)


split = (-6.5, 6.5, None)            # 4-way splitter: 6.02 dB division + 0.5 dB excess (passive: NF = loss)
rx = (0.0, 6.0, -10.0)
nf_p, ip_p = cascade([split, rx])
lna = (20.0, 1.0, -5.0)              # e.g. 1 dB NF, 20 dB gain, OIP3 +15 dBm LNA
nf_a, ip_a = cascade([lna, split, rx])
lna2 = (12.0, 1.0, 10.0)             # lower-gain, high-IP3 multicoupler amplifier (OIP3 +22 dBm)
nf_b, ip_b = cascade([lna2, split, rx])
print(f"   passive 4-way split: NF {nf_p:.1f} dB, IIP3 {ip_p:+.1f} dBm")
print(f"   LNA 20 dB / NF 1 / OIP3 +15 then split: NF {nf_a:.2f} dB, IIP3 {ip_a:+.1f} dBm")
print(f"   LNA 12 dB / NF 1 / OIP3 +22 then split: NF {nf_b:.2f} dB, IIP3 {ip_b:+.1f} dBm  (gain just covers the split)")
leak = -50.0; iso = 25.0
print(f"   port-to-port: a receiver radiating LO {leak:.0f} dBm into its port reaches its neighbours at {leak-iso:.0f} dBm "
      f"through {iso:.0f} dB splitter isolation (resistive star: {leak-6:.0f} dBm)")
check("C1 20 dB LNA before the split restores ~LNA-limited NF; 12 dB LNA trades 2 dB NF for 8 dB IIP3; passive split costs 6.5 dB",
      nf_p > 12 and nf_a < 1.6 and nf_b < 4 and ip_b > ip_a)

# ================================================================ D. feedback amplifier
print("D: shunt-series feedback broadband amplifier, R_f R_E = Z0^2")


def fb_amp_S(Rf, gm, RE, extra=""):
    S = {}
    for d in (0, 1):
        # VCCS with emitter degeneration: i = gm/(1+gm RE) * v_in
        geff = gm / (1 + gm * RE)
        body = [f"G1 out 0 in 0 {geff:.6e}", f"RF in out {Rf}"] + ([extra] if extra else []) + ports(["in", "out"], d)
        f, (v1, v2) = ngspice("\n".join(body), ".ac dec 10 1e6 1e9", ["v(in)", "v(out)"])
        S[(1, d + 1)] = v1 - (1 if d == 0 else 0); S[(2, d + 1)] = v2 - (1 if d == 1 else 0)
    return f, S


for Rf in (250.0, 500.0, 1000.0):
    RE_ideal = Z0 ** 2 / Rf
    gm = 2.0                                          # ~ 50 mA collector current
    RE = 1 / (Rf / Z0 ** 2) - 1 / gm                  # so that gm/(1+gm RE) = Rf/Z0^2 exactly
    f, S = fb_amp_S(Rf, gm, RE)
    print(f"   R_f {Rf:6.0f} ohm, R_E(total) {RE_ideal:5.2f} ohm (external {RE:5.2f} + 1/gm): S21 {db20(S[(2,1)][0]):6.2f} dB "
          f"(theory 20log|(Z0-Rf)/Z0| = {20*np.log10(abs((Z0-Rf)/Z0)):6.2f}), S11 {db20(S[(1,1)][0]):.0f} dB, "
          f"S22 {db20(S[(2,2)][0]):.0f} dB, S12 {db20(S[(1,2)][0]):.1f} dB")
check("D1 R_f R_E = Z0^2 gives S11 = S22 = 0 and S21 = (Z0 - R_f)/Z0 exactly (VCCS model)",
      abs(db20(S[(2, 1)][0]) - 20 * np.log10(abs((Z0 - 1000) / Z0))) < 0.01 and db20(S[(1, 1)][0]) < -60)
# with a BJT (2N5109-class guess: fT ~ 1.2 GHz at 50 mA) and DC bias: 12 V, collector choke, R_f via DC block
bjt = """
.model QX NPN(IS=2e-14 BF=60 VAF=60 CJE=8p CJC=3p TF=110p RB=4 RE=0.1 RC=1)
VCC vcc 0 12
LCH vcc col 10u
CO col out 100n
CIN in base 100n
RB1 vcc base 3.3k
RB2 base 0 300
Q1 col base em QX
RE1 em 0 {RE}
RF base fbx {RF}
CF fbx col 100n
"""
Sb = {}
RFv, REv = 500.0, 4.5
for d in (0, 1):
    body = bjt.replace("{RE}", str(REv)).replace("{RF}", str(RFv)) + "\n".join(ports(["in", "out"], d))
    fb, (v1, v2) = ngspice(body, ".ac dec 40 1e5 2e9", ["v(in)", "v(out)"])
    Sb[(1, d + 1)] = v1 - (1 if d == 0 else 0); Sb[(2, d + 1)] = v2 - (1 if d == 1 else 0)
_, (icc,) = ngspice(bjt.replace("{RE}", str(REv)).replace("{RF}", str(RFv)) + "\n".join(ports(["in", "out"], 0)),
                     ".tran 1n 20n", ["i(VCC)"])
Icc = -icc[-1]
s21 = db20(Sb[(2, 1)]); i10 = np.argmin(abs(fb - 10e6))
f1db = fb[np.where((fb > 10e6) & (s21 < s21[i10] - 1))[0][0]]
flo = fb[np.where((fb < 10e6) & (s21 > s21[i10] - 1))[0][0]]
print(f"   BJT version (R_f 500, R_E 4.5 + r_e, 12 V, I_C ≈ {Icc*1e3:.0f} mA): S21 {s21[i10]:.1f} dB at 10 MHz "
      f"(ideal 19.1 dB), -1 dB band {flo/1e6:.2f}-{f1db/1e6:.0f} MHz, S11 {db20(Sb[(1,1)][i10]):.1f} dB, "
      f"S22 {db20(Sb[(2,2)][i10]):.1f} dB at 10 MHz; class-A output limit ~ I_C^2 (R_L||R_f)/2 = "
      f"{10*np.log10(Icc**2*(Z0*RFv/(Z0+RFv))/2/1e-3):.1f} dBm")
check("D2 BJT feedback amplifier: within 2.5 dB of the 19.1 dB ideal (finite beta, fT), multi-octave (> 3 octaves within 1 dB), |S11|,|S22| < -10 dB in band",
      abs(s21[i10] - 19.1) < 2.5 and f1db / flo > 8 and db20(Sb[(1, 1)][i10]) < -10 and db20(Sb[(2, 2)][i10]) < -10)

# ================================================================ E. push-pull transformer PA
print("E: transformer-coupled push-pull PA")
for V, Vk, P in ((12.5, 1.0, 20.0), (13.8, 1.0, 50.0), (28.0, 2.0, 100.0)):
    Rcc = 2 * (V - Vk) ** 2 / P
    print(f"   V {V:4.1f} V, knee {Vk} V, P {P:5.0f} W: collector-to-collector R_cc = 2(V-Vk)^2/P = {Rcc:5.2f} ohm "
          f"-> 50 ohm needs 1:{50/Rcc:.2f} impedance (turns 1:{np.sqrt(50/Rcc):.2f})")
# even harmonic cancellation: each side delivers a half-sine current; outputs subtract through the transformer
th = np.linspace(0, 2 * np.pi, 4096, endpoint=False)


def push_pull_h2(dg_db, dphi_deg):
    g = 10 ** (dg_db / 20); ph = np.radians(dphi_deg)
    i1 = np.maximum(np.cos(th), 0)
    i2 = g * np.maximum(np.cos(th - np.pi - ph), 0)
    out = i1 - i2                                     # centre-tapped primary: flux ~ i1 - i2
    X = np.fft.rfft(out) / len(th)
    single = np.fft.rfft(i1) / len(th)
    return 20 * np.log10(abs(X[2]) / abs(X[1])), 20 * np.log10(abs(single[2]) / abs(single[1]))


h_bal, h_single = push_pull_h2(0, 0)
for dg, dp in ((0.1, 1.0), (0.5, 5.0), (1.0, 10.0)):
    h, _ = push_pull_h2(dg, dp)
    print(f"   imbalance {dg} dB / {dp} deg: 2nd harmonic {h:6.1f} dBc (single-ended class B {h_single:.1f} dBc; balanced {h_bal:.0f})")
h_mid, _ = push_pull_h2(0.5, 5.0)
check("E1 balanced push-pull cancels the 2nd harmonic; 0.5 dB/5 deg imbalance leaves it ~ 16-20 dB below single-ended",
      h_bal < -100 and 14 < (h_single - h_mid) < 24)
finish()
