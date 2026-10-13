#!/usr/bin/env python3
"""e11_volterra.py — checks for kb/07-noise-linearity/volterra-series-and-nonlinear-analysis.md (W5-E11).

1. Wiener-Hammerstein block (filter A -> cubic polynomial -> filter B): third-order Volterra kernel
   H3(f1,f2,f3) = a3 A(f1)A(f2)A(f3) B(f1+f2+f3); IM3 = (3/4)|H3(f1,f1,-f2)| A^3 vs FFT of a simulation.
2. Method of nonlinear currents on a degenerated transconductor  i = g1 v + g2 v^2 + g3 v^3,
   v = vs - Z i, Z = R_E || C_E (bypassed emitter resistor). Predicts IM3 (and IIP3) vs tone spacing:
   effective cubic  g3,eff = g3 - (2/3) g2^2 [ sum over pairs Z(w_pair)/(1 + g1 Z(w_pair)) ]
   compared with a time-domain ODE simulation (RK4) + FFT at several tone spacings  -> memory effect.
3. Limits of the power series: exact tanh vs its 3rd-order Volterra/Taylor prediction near P1dB.
4. AM-PM from a complex H3 (single tone near the bias-network corner), checked against simulation.
5. Behavioural models: Rapp, Saleh (TWT parameters), memory polynomial fit to a Wiener-Hammerstein PA
   (NMSE memoryless vs memory), and indirect-learning DPD with/without memory (ACLR).

Run: python3 tools/verify/e11_volterra.py      (~30-60 s)
"""
import numpy as np
from scipy import signal

RES = []


def check(name, ok, detail=""):
    RES.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")


def tone_amp(x, fs, f):
    """Amplitude of the cosine component at frequency f (bin-exact signals)."""
    n = len(x)
    X = np.fft.rfft(x) / n * 2
    return np.abs(X[int(round(f * n / fs))])


# ------------------------------------------------------------------ 1. Wiener-Hammerstein
def part1():
    print("1. Wiener-Hammerstein third-order kernel")
    fs, n = 64.0, 2 ** 16
    t = np.arange(n) / fs
    f1, f2 = 4.0 + 0 * 1, 4.25
    A = 0.05
    x = A * np.cos(2 * np.pi * f1 * t) + A * np.cos(2 * np.pi * f2 * t)
    bA, aA = signal.butter(2, 6.0 / (fs / 2))          # input filter
    bB, aB = signal.butter(1, 5.0 / (fs / 2))          # output filter
    a1, a3 = 1.0, -2.0
    def Hz(b, a, f):
        return signal.freqz(b, a, worN=[2 * np.pi * f / fs])[1][0]
    # periodic steady state: run 3 periods, keep the last
    xx = np.tile(x, 3)
    u = signal.lfilter(bA, aA, xx)
    y = signal.lfilter(bB, aB, a1 * u + a3 * u ** 3)[-n:]
    fim = 2 * f1 - f2
    meas = tone_amp(y, fs, fim)
    H3 = a3 * Hz(bA, aA, f1) ** 2 * np.conj(Hz(bA, aA, f2)) * Hz(bB, aB, fim)
    pred = 0.75 * abs(H3) * A ** 3
    print(f"   IM3 at {fim} : simulated {meas:.4e}, Volterra (3/4)|H3|A^3 = {pred:.4e}")
    check("Wiener-Hammerstein IM3 matches the kernel prediction (< 0.5 %)", abs(meas / pred - 1) < 5e-3)
    # IM3 does NOT follow the memoryless rule when B(2f1-f2) != B(f1): output filter at the IM frequency
    H1 = a1 * Hz(bA, aA, f1) * Hz(bB, aB, f1)
    iip3_kernel = np.sqrt(4 / 3 * abs(H1 / H3))
    iip3_naive = np.sqrt(4 / 3 * abs(a1 / a3)) / abs(Hz(bA, aA, f1))
    print(f"   IIP3 amplitude from kernels {iip3_kernel:.4f} vs 'cubic after input filter' {iip3_naive:.4f}")


# ------------------------------------------------------------------ 2. nonlinear currents with memory
G1, G2, G3 = 0.04, 0.04 / (2 * 0.026), 0.04 / (6 * 0.026 ** 2)    # BJT exp expansion, Ic = 1 mA
RE = 25.0


def Zfun(f, fc):
    """Bypassed emitter resistor R_E || C_E with corner fc: Z = R_E/(1 + j f/fc)."""
    return RE / (1 + 1j * np.asarray(f, float) / fc)


def H3_transcond(fa, fb, fc_, fcorner):
    """Output-current kernel H3(fa,fb,fc) (A/V^3) of i = g1 v + g2 v^2 + g3 v^3, v = vs - Z i."""
    Hv = lambda f: 1 / (1 + G1 * Zfun(f, fcorner))
    pair = lambda f: Zfun(f, fcorner) / (1 + G1 * Zfun(f, fcorner))
    g3e = G3 - (2.0 / 3.0) * G2 ** 2 * (pair(fa + fb) + pair(fa + fc_) + pair(fb + fc_))
    return g3e * Hv(fa) * Hv(fb) * Hv(fc_) * Hv(fa + fb + fc_)


def H1_transcond(f, fcorner):
    return G1 / (1 + G1 * Zfun(f, fcorner))


def simulate_transcond(vs, dt, fcorner):
    """RK4 of C_E dvE/dt = i - vE/R_E, i = f(vs - vE). Returns i(t)."""
    CE = 1 / (2 * np.pi * fcorner * RE)
    gm = lambda v: G1 * v + G2 * v ** 2 + G3 * v ** 3
    vE = 0.0
    out = np.empty(len(vs))
    vs_mid = np.concatenate([0.5 * (vs[1:] + vs[:-1]), [vs[-1]]])
    for k in range(len(vs)):
        a, b = vs[k], vs_mid[k]
        c = vs[k + 1] if k + 1 < len(vs) else vs[k]
        f = lambda s, v: (gm(s - v) - v / RE) / CE
        k1 = f(a, vE); k2 = f(b, vE + dt / 2 * k1); k3 = f(b, vE + dt / 2 * k2); k4 = f(c, vE + dt * k3)
        out[k] = gm(a - vE)
        vE += dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return out


def part2():
    print("2. Method of nonlinear currents: IM3 vs tone spacing (bias-network memory)")
    fcorner = 1.0e6          # emitter bypass corner 1 MHz
    f1 = 20e6                # RF tones near 20 MHz (scaled-down for a fast time-domain check)
    A = 2e-3                 # 2 mV per tone at the base
    rows = []
    for df in (0.1e6, 0.5e6, 1e6, 2e6, 5e6):
        T = 20e-6 if df >= 0.5e6 else 40e-6          # integer number of cycles of everything
        fs = 64 * (f1 + df) * 1.0
        n = int(round(T * fs))
        fs = n / T
        t = np.arange(3 * n) / fs                      # 3 periods; keep last (transient decays)
        vs = A * np.cos(2 * np.pi * f1 * t) + A * np.cos(2 * np.pi * (f1 + df) * t)
        i = simulate_transcond(vs, 1 / fs, fcorner)[-n:]
        lo, up = 2 * f1 - (f1 + df), 2 * (f1 + df) - f1
        m_lo, m_up = tone_amp(i, fs, lo), tone_amp(i, fs, up)
        p_lo = 0.75 * abs(H3_transcond(f1, f1, -(f1 + df), fcorner)) * A ** 3
        p_up = 0.75 * abs(H3_transcond(f1 + df, f1 + df, -f1, fcorner)) * A ** 3
        fund = tone_amp(i, fs, f1)
        rows.append((df, m_lo, p_lo, m_up, p_up, fund))
        print(f"   df = {df/1e6:4.1f} MHz: IM3 lower sim {20*np.log10(m_lo/fund):6.2f} dBc, Volterra {20*np.log10(p_lo/fund):6.2f} dBc;"
              f" upper sim {20*np.log10(m_up/fund):6.2f}, Volterra {20*np.log10(p_up/fund):6.2f} dBc")
    err = max(max(abs(20 * np.log10(r[1] / r[2])), abs(20 * np.log10(r[3] / r[4]))) for r in rows)
    check("nonlinear-current Volterra IM3 matches time-domain simulation within 0.3 dB at all spacings", err < 0.3,
          f"worst {err:.2f} dB")
    span = 20 * np.log10(max(r[1] for r in rows) / min(r[1] for r in rows))
    check("IM3 depends on tone spacing by > 6 dB across 0.1-5 MHz (memory from the bias network)", span > 6,
          f"span {span:.1f} dB")
    asym = max(abs(20 * np.log10(r[1] / r[3])) for r in rows)
    print(f"   largest lower/upper IM3 asymmetry: {asym:.2f} dB")
    check("lower/upper IM3 asymmetry appears near the corner (> 0.5 dB)", asym > 0.5, f"{asym:.2f} dB")
    # IIP3 vs spacing (input-referred amplitude -> dBm in 50 ohm for illustration)
    print("   IIP3 (per-tone amplitude, Volterra) vs spacing:")
    for df in (1e3, 1e5, 1e6, 1e7, 1e8):
        H1 = H1_transcond(f1, fcorner)
        H3 = H3_transcond(f1, f1, -(f1 + df), fcorner)
        Aiip3 = np.sqrt(4 / 3 * abs(H1 / H3))
        print(f"     df = {df:9.0f} Hz: A_IIP3 = {Aiip3*1e3:7.2f} mV  ({10*np.log10(Aiip3**2/2/50/1e-3):6.2f} dBm in 50 ohm)")
    # undegenerated device: memoryless result A_IIP3 = sqrt(4/3 g1/g3) = 2*sqrt(2)*VT
    a0 = np.sqrt(4 / 3 * G1 / G3)
    check("bare BJT exponential: A_IIP3 = 2 sqrt(2) V_T = 73.5 mV", abs(a0 - 2 * np.sqrt(2) * 0.026) < 1e-6, f"{a0*1e3:.2f} mV")


# ------------------------------------------------------------------ 3. limits of the power series
def part3():
    print("3. Limits of the power series (tanh)")
    fs, n = 64.0, 2 ** 14
    t = np.arange(n) / fs
    # tanh(x) = x - x^3/3 + 2x^5/15 ...  a1 = 1, a3 = -1/3 -> A_1dB(cubic) = sqrt(0.145*3) = 0.66
    rows = []
    for A in (0.05, 0.1, 0.2, 0.3, 0.5, 0.7):
        x = A * np.cos(2 * np.pi * 4 * t) + A * np.cos(2 * np.pi * 4.5 * t)
        y = np.tanh(x)
        m = tone_amp(y, fs, 3.5)
        p = 0.75 * (1 / 3) * A ** 3
        rows.append((A, 20 * np.log10(m / p)))
        print(f"   A = {A:4.2f}: IM3 exact/cubic-prediction = {20*np.log10(m/p):+6.2f} dB")
    # single-tone 1 dB compression of tanh
    from scipy.optimize import brentq
    def comp(A):
        x = A * np.cos(2 * np.pi * 4 * t)
        return 20 * np.log10(tone_amp(np.tanh(x), fs, 4) / A) + 1
    a1db = brentq(comp, 0.1, 2.0)
    print(f"   tanh single-tone A_1dB = {a1db:.3f} (pure cubic predicts 0.660)")
    ok_small = abs(rows[0][1]) < 0.1
    big = [r for r in rows if r[0] >= 0.5][0][1]
    check("cubic (3rd-order Volterra) IM3 exact to < 0.1 dB at A = 0.05 (30 dB below A_1dB)", ok_small)
    check("cubic prediction off by > 1 dB at A = 0.5 (two tones near P1dB)", abs(big) > 1, f"{big:+.2f} dB")


# ------------------------------------------------------------------ 4. AM-PM from complex H3
def part4():
    print("4. AM-PM from a complex third-order kernel (single tone, bias corner near 2f)")
    fcorner = 30e6
    f0 = 20e6
    fs = 64 * f0
    T = 2e-6
    n = int(round(T * fs)); fs = n / T
    ph = []
    for A in (1e-3, 2e-3, 4e-3, 8e-3):
        t = np.arange(3 * n) / fs
        vs = A * np.cos(2 * np.pi * f0 * t)
        i = simulate_transcond(vs, 1 / fs, fcorner)[-n:]
        X = np.fft.rfft(i)[int(round(f0 * T))]
        ph.append(np.degrees(np.angle(X)))
    sim_dphi = ph[2] - ph[0]
    H1 = H1_transcond(f0, fcorner)
    def G(A):
        return H1 + 0.75 * H3_transcond(f0, f0, -f0, fcorner) * A ** 2
    pred = np.degrees(np.angle(G(4e-3)) - np.angle(G(1e-3)))
    print(f"   phase of fundamental rel. to small signal: sim {ph[1]-ph[0]:+.3f}, {ph[2]-ph[0]:+.3f}, {ph[3]-ph[0]:+.3f} deg"
          f" (A = 2, 4, 8 mV); Volterra predicts {pred:+.3f} deg at 4 mV")
    check("Volterra AM-PM matches simulation within 15 % at 4 mV", abs(sim_dphi - pred) < 0.15 * abs(pred) + 1e-3,
          f"sim {sim_dphi:.3f} vs {pred:.3f} deg")


# ------------------------------------------------------------------ 5. behavioural models and DPD
def saleh(x, aa=2.1587, ba=1.1517, ap=4.0033, bp=9.1040):
    r = np.abs(x)
    return aa * r / (1 + ba * r ** 2) * np.exp(1j * (np.angle(x) + ap * r ** 2 / (1 + bp * r ** 2)))


def rapp(x, G=1.0, asat=1.0, p=2.0):
    r = np.abs(x)
    return G * x / (1 + (G * r / asat) ** (2 * p)) ** (1 / (2 * p))


def mp_matrix(x, K, M):
    cols = []
    for m in range(M + 1):
        xm = np.concatenate([np.zeros(m, complex), x[:len(x) - m]])
        for k in range(1, K + 1, 2):
            cols.append(xm * np.abs(xm) ** (k - 1))
    return np.array(cols).T


def aclr(y, fs, bw):
    f, P = signal.welch(y, fs, nperseg=2048, return_onesided=False)
    f = np.fft.fftshift(f); P = np.fft.fftshift(P)
    main = P[np.abs(f) < bw / 2].sum()
    adj = P[(f > bw / 2 * 1.1) & (f < bw * 1.5)].sum()
    return 10 * np.log10(adj / main)


def part5():
    print("5. Behavioural models: Rapp, Saleh, memory polynomial, DPD")
    r_pk = 1 / np.sqrt(1.1517)
    a_pk = 2.1587 * r_pk / (1 + 1.1517 * r_pk ** 2)
    print(f"   Saleh TWT: saturation at input r = {r_pk:.4f}, output {a_pk:.4f}; AM-PM at saturation "
          f"{np.degrees(4.0033*r_pk**2/(1+9.104*r_pk**2)):.1f} deg")
    check("Saleh peak output = alpha_a/(2 sqrt(beta_a))", abs(a_pk - 2.1587 / (2 * np.sqrt(1.1517))) < 1e-12)
    # Rapp p -> infinity is an ideal limiter; p = 2 compression at 1 dB
    from scipy.optimize import brentq
    a1 = brentq(lambda a: 20 * np.log10(np.abs(rapp(np.array([a]), p=2.0))[0] / a) + 1, 0.1, 3)
    print(f"   Rapp p = 2: input 1 dB compression at {a1:.3f} x A_sat")
    # Wiener-Hammerstein PA: FIR (memory) -> Saleh-like -> FIR
    rng = np.random.default_rng(7)
    N = 2 ** 15
    sym = (rng.integers(0, 4, N // 8) * 2 - 3 + 1j * (rng.integers(0, 4, N // 8) * 2 - 3)) / np.sqrt(10)
    up = np.zeros(N, complex); up[::8] = sym
    rrc = signal.firwin(401, 1 / 8 * 1.25, window=('kaiser', 10))
    x = signal.lfilter(rrc, 1, up) * 8
    x = 0.22 * x / np.sqrt(np.mean(np.abs(x) ** 2))     # ~ 8 dB back-off from A_sat (PAPR of filtered 16-QAM ~ 6-7 dB)
    hA = np.array([1.0, 0.25 + 0.1j, -0.08]); hB = np.array([1.0, -0.15j, 0.05])
    pa = lambda s: signal.lfilter(hB, 1, rapp(signal.lfilter(hA, 1, s), G=1.0, asat=0.6, p=2.0) *
                                  np.exp(1j * 0.3 * np.abs(signal.lfilter(hA, 1, s)) ** 2))
    y = pa(x)
    def fit(K, M, u, v):
        Phi = mp_matrix(u, K, M)
        c = np.linalg.lstsq(Phi, v, rcond=None)[0]
        e = Phi @ c - v
        return c, 10 * np.log10(np.sum(np.abs(e) ** 2) / np.sum(np.abs(v) ** 2))
    _, nmse0 = fit(7, 0, x, y)
    _, nmse3 = fit(7, 3, x, y)
    print(f"   PA model NMSE: memoryless 7th-order poly {nmse0:.1f} dB, memory polynomial (K 7, M 3) {nmse3:.1f} dB")
    check("memory polynomial models a Wiener-Hammerstein PA > 15 dB better than a memoryless polynomial",
          nmse3 < nmse0 - 15, f"{nmse0:.1f} vs {nmse3:.1f} dB")
    # indirect-learning DPD
    G0 = np.mean(y * np.conj(x)) / np.mean(np.abs(x) ** 2)
    def dpd(M, iters=4):
        z = x.copy()
        c = None
        for _ in range(iters):
            yy = pa(z)
            Phi = mp_matrix(yy / G0, 7, M)
            c = np.linalg.lstsq(Phi, z, rcond=None)[0]
            z = mp_matrix(x, 7, M) @ c
        return pa(z)
    fs, bw = 8.0, 1.25
    a_none = aclr(y, fs, bw)
    a_ml = aclr(dpd(0), fs, bw)
    a_mp = aclr(dpd(3), fs, bw)
    a_lin = aclr(G0 * x, fs, bw)
    print(f"   ACLR: no DPD {a_none:.1f} dBc, memoryless DPD {a_ml:.1f} dBc, memory-polynomial DPD {a_mp:.1f} dBc"
          f" (ideal linear {a_lin:.1f} dBc)")
    check("memory-polynomial DPD beats memoryless DPD by > 5 dB ACLR on a PA with memory", a_mp < a_ml - 5,
          f"{a_ml:.1f} vs {a_mp:.1f} dBc")


if __name__ == "__main__":
    part1()
    part3()
    part5()
    part4()
    part2()
    print(f"\nSummary: {sum(RES)}/{len(RES)} checks passed")
