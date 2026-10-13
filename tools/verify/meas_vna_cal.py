#!/usr/bin/env python3
"""
meas_vna_cal.py -- numerical checks for kb/17-test-measurement/vna-fundamentals-calibration.md
(and parts of nanovna-librevna-practical.md / fixtures-and-deembedding.md)

 1. One-port 3-term model: closed-form SOL solution derived in the page
    e00 = G_L ; e11 = (A+B)/(A-B) ; e10e01 = -2AB/(A-B), A = G_O - e00, B = G_S - e00
    vs the general 3x3 linear solve (Rytting's linear form) vs scikit-rf OnePort.
 2. What happens if the open's offset delay / fringing C (cal-kit definition) is ignored:
    error in a 915 MHz antenna impedance measured on an SMA-type kit.
 3. Imperfect load (finite return loss) -> residual directivity; error on a DUT.
 4. Two-port: SOLT (12/8-term) with random error boxes -> exact DUT recovery (scikit-rf).
 5. TRL with scikit-rf, and the 20-160 degree line rule: noise amplification vs line phase.
 6. Unknown-thru (SOLR) with an arbitrary reciprocal thru -> exact recovery.
 7. Port extension (delay + loss only) vs full de-embedding of a U.FL pigtail with a
    connector discontinuity.
 8. Adapter after calibration: VSWR 1.5 -> effective directivity ~14 dB (AN 1287-3).
 9. Re-computation of the AN 1287-3 worked uncertainty example (8753D, 1 dB / 16 dB RL filter).
10. IF bandwidth / averaging: noise floor vs IFBW and N.

Run: python3 tools/verify/meas_vna_cal.py
"""
import numpy as np
import skrf as rf
from skrf.media import DefinedGammaZ0
from skrf.calibration import OnePort, SOLT, TRL, UnknownThru
from skrf.network import two_port_reflect

rng = np.random.default_rng(1)
C0 = 299792458.0
Z0 = 50.0


def db(x):
    return 20 * np.log10(np.abs(x))


def gamma_of(z):
    return (z - Z0) / (z + Z0)


def z_of(g):
    return Z0 * (1 + g) / (1 - g)


# ---------------------------------------------------------------- 1. one-port 3-term
print("=== 1. One-port 3-term model: closed-form SOL vs linear solve vs scikit-rf ===")
e00 = 0.05 * np.exp(1j * 0.7)          # directivity  (-26 dB raw)
e11 = 0.15 * np.exp(-1j * 1.9)         # source match (-16.5 dB raw)
e10e01 = 0.8 * np.exp(-1j * 2.4)       # reflection tracking


def measure_1p(G):
    return e00 + e10e01 * G / (1 - e11 * G)


GS, GO, GL = -1.0, 1.0, 0.0
mS, mO, mL = measure_1p(GS), measure_1p(GO), measure_1p(GL)
e00_hat = mL
A, B = mO - e00_hat, mS - e00_hat
e11_hat = (A + B) / (A - B)
t_hat = -2 * A * B / (A - B)
print(f"closed form : e00 err {abs(e00_hat-e00):.1e}, e11 err {abs(e11_hat-e11):.1e}, e10e01 err {abs(t_hat-e10e01):.1e}")

# general linear form: e00 + G*Gm*e11 - G*De = Gm, De = e00 e11 - e10e01
M = np.array([[1, G * m, -G] for G, m in [(GS, mS), (GO, mO), (GL, mL)]], dtype=complex)
v = np.array([mS, mO, mL])
x = np.linalg.solve(M, v)
t_lin = x[0] * x[1] - x[2]
print(f"linear solve: e00 err {abs(x[0]-e00):.1e}, e11 err {abs(x[1]-e11):.1e}, e10e01 err {abs(t_lin-e10e01):.1e}")

# correction formula: G = (Gm - e00)/(Gm e11 - De)
G_dut = 0.3 - 0.4j
mD = measure_1p(G_dut)
De = e00 * e11 - e10e01
G_corr = (mD - e00_hat) / (mD * e11_hat - (e00_hat * e11_hat - t_hat))
print(f"corrected DUT {G_corr:.6f} (true {G_dut})")

# scikit-rf OnePort
freq = rf.Frequency(0.1, 3, 291, 'GHz')
med = DefinedGammaZ0(freq, z0=50)
ideals = [med.short(), med.open(), med.match()]
err = rf.Network(frequency=freq, s=np.tile(np.array([[e00, np.sqrt(e10e01)], [np.sqrt(e10e01), e11]]), (len(freq), 1, 1)))
meas = [err ** s for s in ideals]
cal = OnePort(measured=meas, ideals=ideals)
cal.run()
dut = med.load(G_dut)
print(f"scikit-rf OnePort corrected DUT max err: {np.max(np.abs(cal.apply_cal(err ** dut).s[:,0,0]-G_dut)):.1e}")

# ---------------------------------------------------------------- 2. cal-kit definition matters
print("\n=== 2. Ignoring the open/short offset delay and fringing C ===")
f = 915e6
w = 2 * np.pi * f
for tau_ps, c0_fF in [(0, 0), (0, 50), (15, 50), (30, 50), (50, 80)]:
    tau = tau_ps * 1e-12
    zc = 1 / (1j * w * c0_fF * 1e-15) if c0_fF > 0 else np.inf
    Gopen = (1 if np.isinf(zc) else gamma_of(zc)) * np.exp(-2j * w * tau)
    Gshort = -1 * np.exp(-2j * w * tau)
    # actual standards measured, but the cal assumes ideal O=+1, S=-1
    m_S, m_O, m_L = measure_1p(Gshort), measure_1p(Gopen), measure_1p(0.0)
    a_, b_ = m_O - m_L, m_S - m_L
    e11h = (a_ + b_) / (a_ - b_)
    th = -2 * a_ * b_ / (a_ - b_)
    Zant = 35 - 20j
    Ga = gamma_of(Zant)
    mA = measure_1p(Ga)
    Gc = (mA - m_L) / (mA * e11h - (m_L * e11h - th))
    print(f"offset {tau_ps:3d} ps, C0 {c0_fF:3d} fF: open phase {np.degrees(np.angle(Gopen)):7.2f} deg -> "
          f"Z_meas {z_of(Gc):.2f} ohm (true 35-20j), |dGamma| {abs(Gc-Ga):.3f}")
print("  (a uniform offset on O and S acts like a reference-plane shift: the result rotates on the Smith chart)")

# ---------------------------------------------------------------- 3. imperfect load
print("\n=== 3. Imperfect load -> residual directivity ===")
for rl in [20, 30, 40]:
    GL_true = 10 ** (-rl / 20) * np.exp(1j * 0.3)
    m_S, m_O, m_L = measure_1p(-1.0), measure_1p(1.0), measure_1p(GL_true)
    a_, b_ = m_O - m_L, m_S - m_L
    e11h = (a_ + b_) / (a_ - b_)
    th = -2 * a_ * b_ / (a_ - b_)
    worst = 0
    for G in [0.0, 0.1, 0.316, 1.0]:
        for ph in np.linspace(0, 2 * np.pi, 13):
            Gd = G * np.exp(1j * ph)
            mA = measure_1p(Gd)
            Gc = (mA - m_L) / (mA * e11h - (m_L * e11h - th))
            if G == 0.0:
                resid = abs(Gc)
            worst = max(worst, abs(Gc - Gd)) if G == 0.1 else worst
    print(f"load RL {rl} dB: residual directivity {db(resid):.1f} dB; worst |dGamma| on a 20 dB-RL DUT {worst:.4f}"
          f" -> RL reads between {-db(0.1+worst):.1f} and {min(-db(max(0.1-worst,1e-9)),60):.1f} dB (60 = 'perfect')")

# ---------------------------------------------------------------- 4. SOLT
print("\n=== 4. Two-port SOLT with random error boxes (scikit-rf) ===")
def tl(fr, z, deg):
    """Line of characteristic impedance z, ports referenced to 50 ohm (mismatched line)."""
    return DefinedGammaZ0(fr, z0_port=50, z0=z).line(deg, 'deg')


def rand_box(n):
    s = (rng.uniform(0.05, 0.3, (n, 2, 2)) * np.exp(1j * rng.uniform(0, 2 * np.pi, (n, 2, 2))))
    s[:, 1, 0] = s[:, 0, 1] = rng.uniform(0.7, 0.95, n) * np.exp(1j * rng.uniform(0, 2 * np.pi, n))
    return rf.Network(frequency=freq, s=s)


X, Y = rand_box(len(freq)), rand_box(len(freq))
thru = med.thru()
short2, open2, load2 = [two_port_reflect(s, s) for s in (med.short(), med.open(), med.match())]
ideals2 = [short2, open2, load2, thru]
meas2 = [X ** s ** Y for s in ideals2]
solt = SOLT(measured=meas2, ideals=ideals2)
solt.run()
# DUT: a lossy mismatched line + series capacitor (filter-like)
dut2 = tl(freq, 65, 40) ** med.shunt_capacitor(1.5e-12) ** tl(freq, 40, 25)
corr = solt.apply_cal(X ** dut2 ** Y)
print(f"SOLT: max |S_corr - S_true| = {np.max(np.abs(corr.s - dut2.s)):.1e}")

# ---------------------------------------------------------------- 5. TRL and the 20-160 deg rule
print("\n=== 5. TRL (scikit-rf) and noise sensitivity vs line phase ===")
f0 = 1.0e9
lam0 = C0 / f0
freq = rf.Frequency(0.02, 1.99, 198, 'GHz')     # avoid the exact 180-deg point (singular)
med = DefinedGammaZ0(freq, z0=50)
X, Y = rand_box(len(freq)), rand_box(len(freq))
thru = med.thru()
short2, open2, load2 = [two_port_reflect(s, s) for s in (med.short(), med.open(), med.match())]
dut2 = tl(freq, 65, 40) ** med.shunt_capacitor(1.5e-12) ** tl(freq, 40, 25)
# line of electrical length 90 deg at 1 GHz on an air (vf = 1) medium: physical length lam0/4
med_tl = DefinedGammaZ0(freq, z0=50, gamma=1j * 2 * np.pi * freq.f / C0)
line = med_tl.line(lam0 / 4, 'm')
reflect = two_port_reflect(med.short(), med.short())
trl = TRL(measured=[X ** thru ** Y, X ** reflect ** Y, X ** line ** Y],
          ideals=None)          # classic TRL: flush thru, unknown reflect (~short), matched line
trl.run()
corr = trl.apply_cal(X ** dut2 ** Y)
phase = np.degrees(2 * np.pi * freq.f / C0 * lam0 / 4)
ok = (phase > 20) & (phase < 160)
print(f"TRL (noise-free): max err inside 20-160 deg band = {np.max(np.abs(corr.s[ok]-dut2.s[ok])):.1e}")
# noise sensitivity: add complex noise of 1e-3 (-60 dB) to raw measurements and see DUT S21 error vs phase
errs = []
for trial in range(100):
    def noisy(n):
        m = n.copy()
        m.s = m.s + 1e-3 * (rng.standard_normal(m.s.shape) + 1j * rng.standard_normal(m.s.shape)) / np.sqrt(2)
        return m
    trl_n = TRL(measured=[noisy(X ** thru ** Y), noisy(X ** reflect ** Y), noisy(X ** line ** Y)],
                ideals=None)
    trl_n.run()
    c = trl_n.apply_cal(noisy(X ** dut2 ** Y))
    errs.append(np.abs(c.s[:, 1, 0] - dut2.s[:, 1, 0]))
errs = np.sqrt(np.mean(np.array(errs) ** 2, axis=0))
i90 = np.argmin(np.abs(phase - 90))
for ph_target in [5, 10, 20, 45, 90, 135, 160, 170, 178]:
    i = np.argmin(np.abs(phase - ph_target))
    print(f"  line phase {phase[i]:6.1f} deg : rms |dS21| = {errs[i]:.4f}  ({errs[i]/errs[i90]:4.1f}x the 90-deg value)")
print("  -> within 20-160 deg the noise-induced error stays within ~2x of its 90-deg value;")
print("     it blows up toward 0/180 deg (line indistinguishable from thru). 20-160 deg = 8:1 frequency span.")

# ---------------------------------------------------------------- 6. unknown thru
print("\n=== 6. Unknown-thru (SOLR) with an arbitrary reciprocal thru ===")
mt_vf = DefinedGammaZ0(freq, z0_port=50, z0=55, gamma=1j * 2 * np.pi * freq.f / (0.7 * C0))
thru_unknown = med.attenuator(-1) ** mt_vf.line(0.030, 'm') ** med.shunt_capacitor(0.3e-12)   # 143 ps, 55 ohm, lossy, 0.3 pF
tau_true = 0.030 / (0.7 * C0)
meas_ut = [X ** s ** Y for s in [short2, open2, load2, thru_unknown]]
for label, est in [("estimate = flush thru (0 ps)", thru),
                   ("estimate = 120 ps line (16% low)",
                    DefinedGammaZ0(freq, z0=50, gamma=1j * 2 * np.pi * freq.f / C0).line(120e-12 * C0, 'm'))]:
    ut = UnknownThru(measured=meas_ut, ideals=[short2, open2, load2, est])
    ut.run()
    corr = ut.apply_cal(X ** dut2 ** Y)
    e = np.max(np.abs(corr.s - dut2.s), axis=(1, 2))
    bad = freq.f[e > 1e-6]
    fb = f"{bad.min()/1e9:.2f} GHz" if bad.size else "none"
    print(f"  {label:36s}: max |err| = {np.max(e):.1e}; first failing freq {fb}")
f90 = 1 / (4 * tau_true)
print(f"  true thru delay {tau_true*1e12:.0f} ps -> 90 deg of thru phase at {f90/1e9:.2f} GHz: a flush-thru guess picks the wrong root above it")
print("  (the thru S21 is found only to +/- sign; the estimate must be within +/-90 deg of the true phase)")

# ---------------------------------------------------------------- 7. port extension vs de-embedding
print("\n=== 7. Port extension vs de-embedding of a U.FL pigtail ===")
for fc, c_ufl in [(915e6, 0.0), (915e6, 0.15e-12), (2.45e9, 0.15e-12)]:
    fr = rf.Frequency(fc / 1e9 * 0.9, fc / 1e9 * 1.1, 201, 'GHz')
    # 1.13 mm micro-coax: ~2.5 dB/m at 1 GHz scaled sqrt(f); vf 0.70; length 100 mm
    alpha_db_m = 2.5 * np.sqrt(fr.f / 1e9)
    m9 = DefinedGammaZ0(fr, z0=50, gamma=alpha_db_m / 8.686 + 1j * 2 * np.pi * fr.f / (0.70 * C0))
    cable = m9.line(0.10, 'm')
    fixture = cable ** DefinedGammaZ0(fr, z0=50).shunt_capacitor(c_ufl) if c_ufl > 0 else cable
    Zant = 35 - 20j
    ant = DefinedGammaZ0(fr, z0=50).load(gamma_of(Zant))
    meas = fixture ** ant
    k = np.argmin(np.abs(fr.f - fc))
    tau = 0.10 / (0.70 * C0)
    one_way_db = 2.5 * np.sqrt(fc / 1e9) * 0.10
    rot = np.exp(2j * 2 * np.pi * fr.f[k] * tau)
    g_pe0 = meas.s[k, 0, 0] * rot
    g_pe = g_pe0 * 10 ** (2 * one_way_db / 20)
    g_de = (fixture.inv ** meas).s[k, 0, 0]
    print(f"  f = {fc/1e6:.0f} MHz, U.FL shunt {c_ufl*1e12:.2f} pF (cable one-way loss {one_way_db:.2f} dB):")
    print(f"    raw at cable input   : Z = {z_of(meas.s[k,0,0]):.2f}")
    print(f"    port ext, delay only : Z = {z_of(g_pe0):.2f}")
    print(f"    port ext, delay+loss : Z = {z_of(g_pe):.2f}")
    print(f"    full de-embedding    : Z = {z_of(g_de):.2f}   (true {Zant})")
    print(f"    RL raw {-db(meas.s[k,0,0]):.2f} dB vs true {-db(gamma_of(Zant)):.2f} dB")


print("\n=== 8. Adapter added after calibration ===")
for vswr in [1.05, 1.1, 1.2, 1.5]:
    g = (vswr - 1) / (vswr + 1)
    print(f"adapter VSWR {vswr}: |Gamma| {g:.3f} -> effective directivity {-db(g):.1f} dB")

# ---------------------------------------------------------------- 9. AN 1287-3 uncertainty example
print("\n=== 9. AN 1287-3 worked example (8753D type-N, 1.3-3 GHz) ===")
ED, ES, EL = 10 ** (-47 / 20), 10 ** (-36 / 20), 10 ** (-47 / 20)
ERT = 1 - 10 ** (-0.019 / 20)
ETT = 1 - 10 ** (-0.026 / 20)
EI = 10 ** (-100 / 20)
S11 = 10 ** (-16 / 20)
S21 = 10 ** (-1 / 20)
dS11 = ED + S11 ** 2 * ES + S21 * S21 * EL + S11 * ERT
print(f"reflection: 0.158 +/- {dS11:.4f} -> RL 16 dB reads {-db(S11+dS11):.2f} to {-db(S11-dS11):.2f} dB "
      f"(-{db(S11+dS11)-db(S11):.2f}/+{db(S11)-db(S11-dS11):.2f} dB; AN 1287-3 prints +0.53/-0.44)")
dS21 = S21 * (EI / S21 + S11 * ES + S21 * S21 * ES * EL + S11 * EL + ETT)
print(f"transmission: +/- {dS21:.4f} -> +/- {db(S21+dS21)-db(S21):.3f} dB")

# ---------------------------------------------------------------- 10. IFBW / averaging
print("\n=== 10. IF bandwidth and averaging ===")
for ifbw in [10e3, 1e3, 100, 10]:
    print(f"IFBW {ifbw:>7.0f} Hz: noise floor change vs 10 kHz = {10*np.log10(ifbw/10e3):6.1f} dB; "
          f"sweep time per point ~ {1/ifbw*1e3:.2f} ms (settling ~1/IFBW)")
for n in [4, 16, 64]:
    print(f"vector (complex) averaging N={n}: noise floor -{10*np.log10(n):.1f} dB (same as IFBW / {n})")

# ---------------------------------------------------------------- 11. 12-term correction formula (page, Level 2)
print("\n=== 11. Explicit 12-term correction formula vs truth ===")
from skrf.calibration import TwelveTerm
freq = rf.Frequency(0.1, 3, 31, 'GHz')
med = DefinedGammaZ0(freq, z0=50)
X, Y = rand_box(len(freq)), rand_box(len(freq))
short2, open2, load2 = [two_port_reflect(s, s) for s in (med.short(), med.open(), med.match())]
ideals12 = [short2, open2, load2, med.thru()]
tt = TwelveTerm(measured=[X ** s ** Y for s in ideals12], ideals=ideals12)
tt.run()
k_ = tt.coefs
dut = tl(freq, 65, 40) ** med.shunt_capacitor(1.5e-12) ** tl(freq, 40, 25)
M = (X ** dut ** Y).s
n11 = (M[:, 0, 0] - k_['forward directivity']) / k_['forward reflection tracking']
n21 = (M[:, 1, 0] - k_['forward isolation']) / k_['forward transmission tracking']
n12 = (M[:, 0, 1] - k_['reverse isolation']) / k_['reverse transmission tracking']
n22 = (M[:, 1, 1] - k_['reverse directivity']) / k_['reverse reflection tracking']
ESF, ELF = k_['forward source match'], k_['forward load match']
ESR, ELR = k_['reverse source match'], k_['reverse load match']
D = (1 + n11 * ESF) * (1 + n22 * ESR) - n21 * n12 * ELF * ELR
S11 = (n11 * (1 + n22 * ESR) - ELF * n21 * n12) / D
S21 = n21 * (1 + n22 * (ESR - ELF)) / D
S12 = n12 * (1 + n11 * (ESF - ELR)) / D
S22 = (n22 * (1 + n11 * ESF) - ELR * n21 * n12) / D
err = max(np.max(np.abs(S11 - dut.s[:, 0, 0])), np.max(np.abs(S21 - dut.s[:, 1, 0])),
          np.max(np.abs(S12 - dut.s[:, 0, 1])), np.max(np.abs(S22 - dut.s[:, 1, 1])))
print(f"explicit formula max error = {err:.1e}")

# ---------------------------------------------------------------- 12. NanoVNA-class residuals: antenna RL uncertainty
print("\n=== 12. Reflection uncertainty with low-cost-kit residuals (1-port, worst case) ===")
for label, ed, es, ert_db in [("good SMA kit (load 40 dB, src match 35 dB, 0.05 dB)", 40, 35, 0.05),
                              ("cheap kit    (load 30 dB, src match 25 dB, 0.2 dB)", 30, 25, 0.2),
                              ("cal at SMA, then 1.5 VSWR adapter added", 14, 14, 0.2)]:
    Ed, Es, Ert = 10 ** (-ed / 20), 10 ** (-es / 20), 1 - 10 ** (-ert_db / 20)
    out = []
    for rl in [6, 10, 15, 20, 30]:
        g = 10 ** (-rl / 20)
        dg = Ed + Ert * g + Es * g * g
        lo = -db(g + dg)
        hi = -db(g - dg) if g > dg else np.inf
        out.append(f"RL{rl}:{lo:.1f}..{'inf' if np.isinf(hi) else f'{hi:.1f}'}")
    print(f"  {label}: " + "  ".join(out))

# ---------------------------------------------------------------- 13. 1.5-port VNA: uncorrected load match on S21
print("\n=== 13. 1.5-port (S11/S21-only) VNA: CH1 load match not corrected ===")
for ch1_rl, pad in [(15, 0), (15, 10), (20, 6)]:
    g_ch1 = 10 ** (-ch1_rl / 20)
    g_eff = g_ch1 * 10 ** (-2 * pad / 20)     # a pad of A dB improves the match by 2A dB (pad itself ~ -35 dB)
    g_eff = np.hypot(g_eff, 10 ** (-35 / 20)) if pad else g_eff
    for dut_s22_rl in [10, 20]:
        s22 = 10 ** (-dut_s22_rl / 20)
        ripple = 20 * np.log10(1 + s22 * g_eff), 20 * np.log10(1 - s22 * g_eff)
        print(f"  CH1 RL {ch1_rl} dB, pad {pad:2d} dB (eff. match {-db(g_eff):.0f} dB), DUT S22 RL {dut_s22_rl} dB:"
              f" S21 error {ripple[0]:+.2f}/{ripple[1]:+.2f} dB")
