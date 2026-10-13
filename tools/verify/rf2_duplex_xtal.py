#!/usr/bin/env python3
"""Verification for kb/06-rf-circuits/duplexers-diplexers-and-crystal-filters.md  (W5-E7)

 A. Complementary (singly-terminated Butterworth) diplexer: band split 1/(1+w^2n) -> why a 629 MHz crossover
    is weak for 433/915 MHz
 B. Trap diplexer 433 / 915 MHz (parallel-LC traps + series resonating elements), finite Q, optimised;
    insertion loss, cross-band rejection, port-to-port isolation, return loss
 C. Cavity notch (shunt series resonator with unloaded Q): notch depth vs coupling, pass loss at offset;
    repeater-duplexer isolation budget
 D. Crystal ladder (LSB ladder) 4-pole 0.1 dB Chebyshev from k-q values (Dishal method): coupling
    capacitors, end resistance, mesh tuning; simulation with and without C0; bandwidth correction;
    shape factor and C0-limited ultimate rejection; ngspice AC cross-check
 E. G3UUR motional-capacitance formula vs exact BVD load resonance
Run: python3 tools/verify/rf2_duplex_xtal.py   (runtime ~20 s; ngspice used in D)
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rf2_common import check, finish, ngspice, db20
from rfckt_netsolve import Circuit
from scipy.optimize import minimize, brentq

Z0 = 50.0

print("=== A. complementary Butterworth diplexer")
fx = np.sqrt(433.92e6 * 915e6)
for n in (3, 5, 7, 9):
    w = 915e6 / fx
    rej = 10 * np.log10(1 / (1 + w ** (2 * n)))
    print(f"  crossover {fx/1e6:.0f} MHz, order {n}: the 433 MHz arm passes 915 MHz at {rej:.1f} dB")
    if n == 5:
        rej5 = rej
check("5th-order complementary Butterworth gives only ~16 dB at 915 MHz", abs(rej5 + 16.4) < 0.3)

print("\n=== B. 433/915 MHz trap diplexer")
QL_, QC_ = 50.0, 300.0
bandA = np.linspace(433.05e6, 434.79e6, 11)
bandB = np.linspace(902e6, 928e6, 27)
fall = np.concatenate([bandA, bandB])


def build(x, f):
    L1, C1, Cs, L2, C2, Ls, Lt1, Ct1, Lt2, Ct2 = x
    c = Circuit(f)
    # 433 arm: common -> [L1||C1 trap @915] -> Cs -> A ; shunt trap Lt1-Ct1 (@915) at A
    c.L('com', 'a1', L1 * 1e-9, Q=QL_); c.C('com', 'a1', C1 * 1e-12, Q=QC_)
    c.C('a1', 'A', Cs * 1e-12, Q=QC_)
    c.L('A', 'at', Lt1 * 1e-9, Q=QL_); c.C('at', 0, Ct1 * 1e-12, Q=QC_)
    # 915 arm: common -> [L2||C2 trap @433] -> Ls -> B ; shunt trap Lt2-Ct2 (@433) at B
    c.L('com', 'b1', L2 * 1e-9, Q=QL_); c.C('com', 'b1', C2 * 1e-12, Q=QC_)
    c.L('b1', 'B', Ls * 1e-9, Q=QL_)
    c.L('B', 'bt', Lt2 * 1e-9, Q=QL_); c.C('bt', 0, Ct2 * 1e-12, Q=QC_)
    return c.sparams(['com', 'A', 'B'], z0=Z0)


w9, w4 = 2 * np.pi * 915e6, 2 * np.pi * 433.92e6
L1 = 6.8; C1 = 1 / (w9 ** 2 * L1 * 1e-9) * 1e12
XA = w4 * L1 * 1e-9 / (1 - (433.92 / 915) ** 2); Cs = 1 / (w4 * XA) * 1e12
L2 = 22.0; C2 = 1 / (w4 ** 2 * L2 * 1e-9) * 1e12
XB = w9 * L2 * 1e-9 / (1 - (915 / 433.92) ** 2); Ls = -XB / w9 * 1e9
Lt1 = 15.0; Ct1 = 1 / (w9 ** 2 * Lt1 * 1e-9) * 1e12
Lt2 = 39.0; Ct2 = 1 / (w4 ** 2 * Lt2 * 1e-9) * 1e12
x0 = np.array([L1, C1, Cs, L2, C2, Ls, Lt1, Ct1, Lt2, Ct2])
print("  starting values (nH/pF): " + ", ".join(f"{v:.2f}" for v in x0))


def metrics(x):
    S = build(x, fall)
    iA = slice(0, len(bandA)); iB = slice(len(bandA), None)
    return dict(ILA=-db20(S[iA, 1, 0]).max(), ILB=-db20(S[iB, 2, 0]).max(),
                RLA=-db20(S[iA, 0, 0]).min(), RLB=-db20(S[iB, 0, 0]).min(),
                rejA=-db20(S[iB, 1, 0]).min(), rejB=-db20(S[iA, 2, 0]).min(),
                isoA=-db20(S[iA, 2, 1]).min(), isoB=-db20(S[iB, 2, 1]).min())


def cost(lx):
    m = metrics(np.exp(lx))
    return (m['ILA'] + m['ILB']) + 0.2 * max(0, 18 - m['RLA']) + 0.2 * max(0, 18 - m['RLB']) \
        + 0.1 * max(0, 40 - m['rejA']) + 0.1 * max(0, 40 - m['rejB'])


m0 = metrics(x0)
print("  analytic start: " + ", ".join(f"{k} {v:.2f}" for k, v in m0.items()))
r = minimize(cost, np.log(x0), method='Nelder-Mead', options=dict(maxiter=4000, xatol=1e-4, fatol=1e-5))
xo = np.exp(r.x); mo = metrics(xo)
print("  optimised values (nH/pF): L1 %.2f C1 %.2f Cs %.2f | L2 %.2f C2 %.2f Ls %.2f | Lt1 %.2f Ct1 %.2f | Lt2 %.2f Ct2 %.2f" % tuple(xo))
print("  optimised: " + ", ".join(f"{k} {v:.2f}" for k, v in mo.items()) + " dB")
check("trap diplexer: IL < 1.2 dB both bands with Q_L = 50", mo['ILA'] < 1.2 and mo['ILB'] < 1.2)
check("trap diplexer: cross-band rejection > 35 dB and port isolation > 35 dB", min(mo['rejA'], mo['rejB'], mo['isoA'], mo['isoB']) > 35)
check("trap diplexer: common-port return loss > 15 dB in both bands", mo['RLA'] > 15 and mo['RLB'] > 15)
# sensitivity: 5 % component tolerance Monte Carlo
rng = np.random.default_rng(3)
worst = []
for _ in range(200):
    mm = metrics(xo * (1 + 0.05 * rng.uniform(-1, 1, len(xo))))
    worst.append((mm['ILA'], mm['ILB'], min(mm['rejA'], mm['rejB']), min(mm['RLA'], mm['RLB'])))
worst = np.array(worst)
print(f"  ±5 % Monte Carlo (200): 95th-pct IL433 {np.percentile(worst[:,0],95):.2f} dB, IL915 {np.percentile(worst[:,1],95):.2f} dB,"
      f" 5th-pct rejection {np.percentile(worst[:,2],5):.1f} dB, 5th-pct RL {np.percentile(worst[:,3],5):.1f} dB")

print("\n=== C. cavity notch and repeater duplexer budget")
f_n = 434.5e6


def notch_design(Qu, df, pass_loss_db=0.3):
    """Shunt series-resonant cavity on a Z0 line: choose the smallest coupling reactance slope that keeps
    the loss at offset df <= pass_loss_db; return (L, notch depth dB, loss at df)."""
    Xmin = (Z0 / 2) / np.sqrt(10 ** (pass_loss_db / 10) - 1)
    L = Xmin / (2 * 2 * np.pi * df)
    C = 1 / ((2 * np.pi * f_n) ** 2 * L); R = 2 * np.pi * f_n * L / Qu
    f = np.array([f_n, f_n - df])
    Zs = R + 1j * 2 * np.pi * f * L + 1 / (1j * 2 * np.pi * f * C)
    S21 = 2 * Zs / (2 * Zs + Z0)
    return L, db20(S21[0]), db20(S21[1]), R


for df in (5e6, 0.58e6):
    for Qu in (300, 3000, 10000):
        L, dn, dl, R = notch_design(Qu, df)
        R_formula = Z0 / 2 / np.sqrt(10 ** 0.03 - 1) * f_n / (2 * Qu * df)
        print(f"  pass {df/1e6:.2f} MHz away at <= 0.3 dB, Qu {Qu:5d}: L {L*1e9:7.0f} nH, R {R:.2f} ohm (formula {R_formula:.2f}),"
              f" single-cavity notch {dn:6.1f} dB (loss at offset {dl:.2f} dB)")
        if Qu == 3000 and df == 5e6:
            notch3000 = dn; rf_ok = abs(R / R_formula - 1) < 1e-6
        if Qu == 3000 and df == 0.58e6:
            notch_close = dn
check("Qu 3000, 5 MHz split, 0.3 dB pass loss: one cavity notches ~26 dB (three cavities ~75 dB)", -28 < notch3000 < -24 and rf_ok)
check("the same cavity cannot notch a signal 0.58 MHz away by more than ~10 dB at 0.3 dB pass loss", notch_close > -10)
# repeater budget: 25 W TX, RX NF 6 dB in 12.5 kHz, TX noise -155 dBc/Hz at 5 MHz (assumed), RX blocking -30 dBm (assumed)
Ptx = 10 * np.log10(25 / 1e-3)
floor = -174 + 6 + 10 * np.log10(12.5e3)
noise_tx = Ptx - 155 + 10 * np.log10(12.5e3)
need_noise = noise_tx - (floor - 10)
need_carrier = Ptx - (-30)
print(f"  25 W repeater: TX noise in RX channel {noise_tx:.1f} dBm vs RX floor {floor:.1f} dBm -> isolation at f_RX >= {need_noise:.1f} dB;"
      f" carrier to keep RX below -30 dBm -> isolation at f_TX >= {need_carrier:.1f} dB")
check("repeater budget needs ~70-75 dB each way (consistent with 75-80 dB commercial duplexers)", 65 < need_noise < 80 and 70 < need_carrier < 80)

print("\n=== D. 4-pole crystal ladder filter (LSB ladder, Dishal k-q method)")
f0 = 10.0e6; Lm = 12e-3; Qx = 75000.0; C0x = 4.5e-12
Cm = 1 / ((2 * np.pi * f0) ** 2 * Lm); Rm = 2 * np.pi * f0 * Lm / Qx
print(f"  crystal: fs 10 MHz, Lm {Lm*1e3:.0f} mH, Cm {Cm*1e15:.2f} fF, Rm {Rm:.1f} ohm (Q {Qx:.0f}), C0 {C0x*1e12:.1f} pF")


def cheb_g(n, ripple_db):
    beta = np.log(1 / np.tanh(ripple_db / 17.37)); gam = np.sinh(beta / (2 * n))
    a = [np.sin((2 * k - 1) * np.pi / (2 * n)) for k in range(1, n + 1)]
    b = [gam ** 2 + np.sin(k * np.pi / n) ** 2 for k in range(1, n + 1)]
    g = [2 * a[0] / gam]
    for k in range(1, n):
        g.append(4 * a[k - 1] * a[k] / (b[k - 1] * g[k - 1]))
    gl = 1.0 if n % 2 else 1 / np.tanh(beta / 4) ** 2
    return np.array(g), gl


g, gl = cheb_g(4, 0.1)
check("0.1 dB Chebyshev g-values (n=4) = 1.1088, 1.3061, 1.7703, 0.8180, 1.3554",
      np.allclose(np.r_[g, gl], [1.1088, 1.3061, 1.7703, 0.8180, 1.3554], atol=2e-4))
q1 = g[0]; qn = g[-1] * gl
k12, k23, k34 = [1 / np.sqrt(g[i] * g[i + 1]) for i in range(3)]
print(f"  k-q: q1 {q1:.4f}, q4 {qn:.4f}, k12 {k12:.4f}, k23 {k23:.4f}, k34 {k34:.4f}")


def design(BW):
    """BW = equiripple (0.1 dB) bandwidth; the 3 dB bandwidth is ~1.21x wider for n = 4."""
    QF = f0 / BW
    C12, C23, C34 = Cm * QF / k12, Cm * QF / k23, Cm * QF / k34
    Rend = 2 * np.pi * Lm * BW / q1
    # mesh frequencies (crystal series arm + capacitors in the loop, termination R has no C)
    def mesh(Cs_list):
        Ct = 1 / (1 / Cm + sum(1 / c for c in Cs_list))
        return 1 / (2 * np.pi * np.sqrt(Lm * Ct))
    fm = [mesh([C12]), mesh([C12, C23]), mesh([C23, C34]), mesh([C34])]
    fhi = max(fm)
    # add series tuning capacitors to lower-frequency meshes so all equal fhi
    Ct_need = 1 / ((2 * np.pi * fhi) ** 2 * Lm)
    extra = []
    loops = [[C12], [C12, C23], [C23, C34], [C34]]
    for lp in loops:
        inv = 1 / Ct_need - 1 / Cm - sum(1 / c for c in lp)
        extra.append(1 / inv if inv > 1e-3 / Cm * 1e-6 else np.inf)
    return dict(C12=C12, C23=C23, C34=C34, Rend=Rend, fm=fm, extra=extra, fhi=fhi)


def simulate(d, f, with_C0=True):
    c = Circuit(f)
    names = ['n1', 'n2', 'n3', 'n4', 'n5']        # n1 = after end tuning cap; n2..n4 = shunt nodes; n5 = before end cap

    def xtal(a, b, tag):
        c.L(a, tag + 'x', Lm); c.C(tag + 'x', tag + 'y', Cm); c.R(tag + 'y', b, Rm)
        if with_C0:
            c.C(a, b, C0x)

    e = d['extra']
    if np.isfinite(e[0]):
        c.C('in', 'n1', e[0])
    else:
        c.R('in', 'n1', 1e-6)
    xtal('n1', 'n2', 'a')
    c.C('n2', 0, d['C12'])
    if np.isfinite(e[1]):
        xtal('n2', 'm2', 'b'); c.C('m2', 'n3', e[1])
    else:
        xtal('n2', 'n3', 'b')
    c.C('n3', 0, d['C23'])
    if np.isfinite(e[2]):
        xtal('n3', 'm3', 'c'); c.C('m3', 'n4', e[2])
    else:
        xtal('n3', 'n4', 'c')
    c.C('n4', 0, d['C34'])
    xtal('n4', 'n5', 'd')
    if np.isfinite(e[3]):
        c.C('n5', 'out', e[3])
    else:
        c.R('n5', 'out', 1e-6)
    return c.sparams(['in', 'out'], z0=d['Rend'])


def bw3(f, s21):
    a = db20(s21); pk = a.max(); m = a >= pk - 3
    idx = np.where(m)[0]
    return f[idx[-1]] - f[idx[0]], pk, f[idx].mean()


BWt = 2400.0
d = design(BWt)
print(f"  design BW {BWt:.0f} Hz: C12 {d['C12']*1e12:.1f} pF, C23 {d['C23']*1e12:.1f} pF, R_end {d['Rend']:.1f} ohm;"
      f" mesh offsets above fs: " + ", ".join(f"{(x-f0):.0f}" for x in d['fm']) + " Hz; tuning caps: "
      + ", ".join("none" if not np.isfinite(x) else f"{x*1e12:.1f} pF" for x in d['extra']))
f = np.linspace(f0 - 6e3, f0 + 10e3, 8001)
S_noC0 = simulate(d, f, with_C0=False); S_C0 = simulate(d, f, with_C0=True)
b1, p1, c1 = bw3(f, S_noC0[:, 1, 0]); b2, p2, c2 = bw3(f, S_C0[:, 1, 0])
print(f"  without C0: 3 dB BW {b1:.0f} Hz, IL {-p1:.2f} dB, centre fs+{c1-f0:.0f} Hz")
print(f"  with C0 = 4.5 pF: 3 dB BW {b2:.0f} Hz, IL {-p2:.2f} dB, centre fs+{c2-f0:.0f} Hz")
eps_r = np.sqrt(10 ** (0.1 / 10) - 1)
r3 = np.cosh(np.arccosh(1 / eps_r) / 4)
print(f"  0.1 dB Chebyshev n=4: 3 dB bandwidth = {r3:.3f} x ripple bandwidth -> expected {r3*BWt:.0f} Hz")
check("series-resonator design (C0 ignored) gives a 3 dB BW within 5 % of 1.21 x the design ripple BW", abs(b1 / (r3 * BWt) - 1) < 0.05)
check("C0 narrows the filter (as Hayward reports)", b2 < 0.97 * b1)
# iterate the design bandwidth to correct for C0
BWd = BWt
for it in range(6):
    dd = design(BWd); bb, pp, cc = bw3(f, simulate(dd, f, True)[:, 1, 0])
    BWd *= BWt / bb
dd = design(BWd); SS = simulate(dd, f, True); bb, pp, cc = bw3(f, SS[:, 1, 0])
a = db20(SS[:, 1, 0])
inb = (f > cc - 0.4 * bb) & (f < cc + 0.4 * bb)
ripple = a[inb].max() - a[inb].min()
print(f"  corrected (target 3 dB BW 2400 Hz): design ripple BW {BWd:.0f} Hz -> realised {bb:.0f} Hz with C0; IL {-pp:.2f} dB; passband ripple (central 80 %) {ripple:.2f} dB;"
      f" C12 {dd['C12']*1e12:.1f} pF, C23 {dd['C23']*1e12:.1f} pF, R_end {dd['Rend']:.1f} ohm")
check("re-designed filter realises 2.4 kHz within 2 % including C0", abs(bb / BWt - 1) < 0.02)
check("insertion loss with Q 75k crystals < 3 dB", -pp < 3)
# shape factor 60/6 dB
fw = np.linspace(f0 - 40e3, f0 + 40e3, 40001)
aw = db20(simulate(dd, fw, True)[:, 1, 0]); pk = aw.max()
def width(level):
    idx = np.where(aw >= pk - level)[0]; return fw[idx[-1]] - fw[idx[0]]
sf = width(60) / width(6)
lo_rej = pk - aw[np.argmin(np.abs(fw - (f0 - 30e3)))]; hi_rej = pk - aw[np.argmin(np.abs(fw - (f0 + 30e3)))]
print(f"  shape factor 60/6 dB = {sf:.2f}; rejection 30 kHz below {lo_rej:.0f} dB, 30 kHz above {hi_rej:.0f} dB (LSB-ladder asymmetry)")
check("LSB ladder: steeper/higher rejection on the high side than the low side", hi_rej > lo_rej)
fu = np.array([f0 - 2e6, f0 + 2e6])
Su = simulate(dd, fu, True)
print(f"  ultimate rejection +-2 MHz (C0-bridged): {pk - db20(Su[0,1,0]):.0f} / {pk - db20(Su[1,1,0]):.0f} dB")
# ngspice cross-check of the final design
e = dd['extra']
def ce(name, a_, b_, val):
    return f"{name} {a_} {b_} {val}\n" if np.isfinite(val) else f"{name} {a_} {b_} 1e-6\n"
net = f"V1 src 0 AC 2\nRS src in {dd['Rend']}\n"
net += (f"CE1 in n1 {e[0]}\n" if np.isfinite(e[0]) else "RE1 in n1 1e-6\n")
def xt(tag, a_, b_):
    return f"L{tag} {a_} {tag}x {Lm}\nC{tag} {tag}x {tag}y {Cm}\nR{tag} {tag}y {b_} {Rm}\nCP{tag} {a_} {b_} {C0x}\n"
net += xt('a', 'n1', 'n2') + f"C12 n2 0 {dd['C12']}\n"
net += (xt('b', 'n2', 'm2') + f"CT2 m2 n3 {e[1]}\n") if np.isfinite(e[1]) else xt('b', 'n2', 'n3')
net += f"C23 n3 0 {dd['C23']}\n"
net += (xt('c', 'n3', 'm3') + f"CT3 m3 n4 {e[2]}\n") if np.isfinite(e[2]) else xt('c', 'n3', 'n4')
net += f"C34 n4 0 {dd['C34']}\n" + xt('d', 'n4', 'n5')
net += (f"CE2 n5 out {e[3]}\n" if np.isfinite(e[3]) else "RE2 n5 out 1e-6\n") + f"RL out 0 {dd['Rend']}\n"
fs_, (vo,) = ngspice(net, f".ac lin 4001 {f0-6e3} {f0+10e3}", ["v(out)"])
s21_spice = vo  # source 2 V behind Rend into matched Rend -> v(out) = S21
s21_py = simulate(dd, fs_, True)[:, 1, 0]
dev = np.max(np.abs(db20(s21_spice) - db20(s21_py))[db20(s21_py) > -40])
print(f"  ngspice vs Python nodal solver: max |dS21| {dev:.3f} dB over the passband/skirts")
check("ngspice AC agrees with the nodal solver within 0.05 dB (above -40 dB)", dev < 0.05)

print("\n=== E. G3UUR motional-capacitance measurement")
for Cs in (33e-12, 100e-12):
    def Xtot(fq):
        w = 2 * np.pi * fq
        Zarm = 1j * w * Lm + 1 / (1j * w * Cm)
        Zx = Zarm * (1 / (1j * w * C0x)) / (Zarm + 1 / (1j * w * C0x))
        return (Zx + 1 / (1j * w * Cs)).imag
    fp = f0 * (1 + Cm / (2 * C0x)); fL = brentq(Xtot, f0 + 1, f0 + 0.5 * (fp - f0))
    df = fL - f0
    Cm_est = 2 * df * (C0x + Cs) / f0
    print(f"  series C {Cs*1e12:.0f} pF: load resonance +{df:.1f} Hz -> Cm estimate {Cm_est*1e15:.3f} fF (true {Cm*1e15:.3f})")
    if Cs == 33e-12:
        err = Cm_est / Cm - 1
check("Cm = 2 df (C0 + Cs) / f is within 0.5 % of the true value", abs(err) < 0.005)

finish()
