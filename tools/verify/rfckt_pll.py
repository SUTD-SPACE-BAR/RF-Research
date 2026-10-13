#!/usr/bin/env python3
"""Verification for kb/06-rf-circuits/vco-and-pll-synthesizers.md

 A. Banerjee 2nd-order passive loop filter (3rd-order PLL): synthesis from (fc, PM, Icp, Kvco, N);
    check open-loop crossover = fc and phase margin; ADF4351 at 433.92 MHz example
 B. Closed-loop phase-noise budget: reference, PLL floor (PN_SYNTH) + flicker (PN1_f), R2 thermal noise,
    VCO (data-sheet open-loop table); integrated jitter vs loop bandwidth (optimum)
 C. Lock time (linear model) for a frequency step
 D. MASH 1-1-1 sigma-delta modulator: simulated quantisation phase noise vs closed form
 E. Reference-spur estimate from charge-pump leakage (narrow-band FM)
 F. DDS: frequency resolution, phase-truncation spur bound (-6.02 P dBc), sinc roll-off
 G. Si5351-style fractional synthesis (VCO 600-900 MHz, multisynth a+b/c): exact frequency error
 H. Leeson's model: VCO phase noise vs Q
Run: python3 tools/verify/rfckt_pll.py
"""
import numpy as np, sys
from scipy import signal
from fractions import Fraction

ok_all = True
kB, T0 = 1.380649e-23, 290.0


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


# ---------------------------------------------------------------- A. loop filter
def design_2nd_order(fc, pm_deg, Icp, Kv_hz, N):
    wc = 2 * np.pi * fc; phi = np.deg2rad(pm_deg)
    Kphi = Icp / (2 * np.pi); Kv = 2 * np.pi * Kv_hz
    T1 = (1 / np.cos(phi) - np.tan(phi)) / wc
    T2 = 1 / (wc ** 2 * T1)
    A0 = Kphi * Kv / (N * wc ** 2) * np.sqrt((1 + (wc * T2) ** 2) / (1 + (wc * T1) ** 2))
    C1 = A0 * T1 / T2; C2 = A0 - C1; R2 = T2 / C2
    return C1, C2, R2


def Zfilt(f, C1, C2, R2, R3=0.0, C3=0.0):
    s = 2j * np.pi * f
    Z = 1 / (s * C1 + 1 / (R2 + 1 / (s * C2)))
    if R3 > 0:
        # third pole: R3 series then C3 shunt at the VCO input (voltage divider on the C1 node)
        Zc3 = 1 / (s * C3)
        Zin = 1 / (s * C1 + 1 / (R2 + 1 / (s * C2)) + 1 / (R3 + Zc3))
        return Zin * Zc3 / (R3 + Zc3)
    return Z


def G_open(f, C1, C2, R2, Icp, Kv_hz, N, **kw):
    s = 2j * np.pi * f
    return (Icp / (2 * np.pi)) * (2 * np.pi * Kv_hz) * Zfilt(f, C1, C2, R2, **kw) / (N * s)


fRF = 433.92e6; div_out = 8; fVCO = fRF * div_out          # 3471.36 MHz (ADF4351 VCO range 2.2-4.4 GHz)
fREF = 25e6; fPFD = 25e6; N = fVCO / fPFD                   # 138.8544 -> fractional-N
Icp, Kv = 2.5e-3, 40e6                                      # ADF4351: ICP up to 5 mA (RSET 5.1k), KV 40 MHz/V
fc, PM = 50e3, 50.0
C1, C2, R2 = design_2nd_order(fc, PM, Icp, Kv, N)
f = np.logspace(2, 8, 4001)
G = G_open(f, C1, C2, R2, Icp, Kv, N)
i_c = np.argmin(abs(abs(G) - 1))
pm_meas = 180 + np.degrees(np.angle(G[i_c]))
print(f"A: ADF4351 @ {fRF/1e6:.2f} MHz (VCO {fVCO/1e6:.2f} MHz / {div_out}), fPFD 25 MHz, N = {N:.4f}, Icp {Icp*1e3} mA, "
      f"Kv 40 MHz/V, target fc {fc/1e3:.0f} kHz PM {PM} deg")
print(f"   C1 = {C1*1e9:.3f} nF, C2 = {C2*1e9:.2f} nF, R2 = {R2:.0f} ohm -> crossover {f[i_c]/1e3:.1f} kHz, PM {pm_meas:.2f} deg")
check("A1 synthesised filter meets crossover and phase margin", abs(f[i_c] / fc - 1) < 0.01 and abs(pm_meas - PM) < 0.2)
# E-series rounding + 3rd pole (R3,C3) for spur attenuation: T3 ~ T1/4 -> small PM loss
C1r, C2r, R2r = 1.0e-9 * round(C1 / 1e-9, 1), 1e-9 * round(C2 / 1e-9, 0), 10 * round(R2 / 10)
T1 = R2 * C1 * C2 / (C1 + C2)
R3, C3 = 2 * R2r, None
C3 = (T1 / 4) / R3
G3 = G_open(f, C1r, C2r, R2r, Icp, Kv, N, R3=R3, C3=C3)
i3 = np.argmin(abs(abs(G3) - 1)); pm3 = 180 + np.degrees(np.angle(G3[i3]))
print(f"   rounded C1 {C1r*1e9:.1f} nF, C2 {C2r*1e9:.0f} nF, R2 {R2r:.0f} ohm + 3rd pole R3 {R3:.0f} ohm, C3 {C3*1e12:.0f} pF: "
      f"fc {f[i3]/1e3:.1f} kHz, PM {pm3:.1f} deg")
att_2 = 20 * np.log10(abs(Zfilt(np.array([fPFD]), C1r, C2r, R2r))[0] / abs(Zfilt(np.array([fc]), C1r, C2r, R2r))[0])
att_3 = 20 * np.log10(abs(Zfilt(np.array([fPFD]), C1r, C2r, R2r, R3=R3, C3=C3))[0] / abs(Zfilt(np.array([fc]), C1r, C2r, R2r, R3=R3, C3=C3))[0])
print(f"   filter attenuation at fPFD relative to fc: 2nd-order {att_2:.1f} dB, with 3rd pole {att_3:.1f} dB")
check("A2 3rd pole adds > 20 dB at fPFD for < 8 deg of phase margin", att_3 < att_2 - 20 and PM - pm3 < 8)

# ---------------------------------------------------------------- B. phase-noise budget
def closed_loop(fc_):
    C1_, C2_, R2_ = design_2nd_order(fc_, PM, Icp, Kv, N)
    T1_ = R2_ * C1_ * C2_ / (C1_ + C2_)
    R3_ = 2 * R2_; C3_ = (T1_ / 4) / R3_
    G_ = G_open(f, C1_, C2_, R2_, Icp, Kv, N, R3=R3_, C3=C3_)
    return G_, (C1_, C2_, R2_, R3_, C3_)


def interp_db(fx, fpts, dbpts):
    return np.interp(np.log10(fx), np.log10(fpts), dbpts)


PN_SYNTH, PN1f = -221.0, -118.0                  # ADF4351 (ABP 3 ns): normalised floor and 1/f (10 kHz, 1 GHz)
vco_f = np.array([1e3, 1e4, 1e5, 1e6, 5e6, 1e8])
vco_pn = np.array([-56, -86, -111, -134, -145, -165])   # 3.3 GHz open-loop table (10k..5M), extrapolated 1k (30 dB/dec) & floor
ref_f = np.array([10, 100, 1e3, 1e4, 1e5, 1e8]); ref_pn = np.array([-100, -125, -140, -150, -155, -155])   # assumed 25 MHz TCXO


def budget(fc_, verbose=False):
    G_, (C1_, C2_, R2_, R3_, C3_) = closed_loop(fc_)
    H = G_ / (1 + G_)          # closed-loop (normalised: multiply by N for ref/PFD referred noise)
    E = 1 / (1 + G_)           # VCO noise transfer
    L_floor = PN_SYNTH + 10 * np.log10(fPFD) + 20 * np.log10(N)
    L_flick = PN1f + 10 * np.log10(1e4 / f) + 20 * np.log10(fVCO / 1e9)
    L_chip = 10 * np.log10(10 ** (L_floor / 10) + 10 ** (L_flick / 10))
    L_ref = interp_db(f, ref_f, ref_pn) + 20 * np.log10(fVCO / fREF)
    L_vco = interp_db(f, vco_f, vco_pn)
    # R2 thermal noise -> VCO tuning voltage (charge pump = current source)
    s = 2j * np.pi * f
    Zc1 = 1 / (s * C1_); Zc2 = 1 / (s * C2_); Zc3 = 1 / (s * C3_)
    Zr3 = R3_ + Zc3
    Zpar = 1 / (1 / Zc1 + 1 / Zr3)
    v_node = np.sqrt(4 * kB * T0 * R2_) * Zpar / (Zpar + R2_ + Zc2)
    v_vco = v_node * Zc3 / Zr3
    L_R2 = 10 * np.log10(0.5 * (Kv * abs(v_vco) / f) ** 2)
    comps = {
        'reference': L_ref + 20 * np.log10(abs(H)),
        'PLL chip': L_chip + 20 * np.log10(abs(H)),
        'loop-filter R': L_R2 + 20 * np.log10(abs(E)),
        'VCO': L_vco + 20 * np.log10(abs(E)),
    }
    tot = 10 * np.log10(sum(10 ** (v / 10) for v in comps.values()))
    band = (f >= 1e3) & (f <= 10e6)
    sig2 = 2 * np.trapezoid(10 ** (tot[band] / 10), f[band])          # rad^2 (VCO)
    jit = np.sqrt(sig2) / (2 * np.pi * fVCO)
    return comps, tot, jit, (C1_, C2_, R2_, R3_, C3_)


print("B: ADF4351 closed-loop phase-noise budget at the 433.92 MHz output (VCO noise - 20log8 = -18.1 dB):")
jits = {}
for fc_ in (10e3, 20e3, 50e3, 100e3, 200e3, 400e3):
    comps, tot, jit, _ = budget(fc_)
    jits[fc_] = jit
    at = lambda fo: tot[np.argmin(abs(f - fo))] - 20 * np.log10(div_out)
    print(f"   fc {fc_/1e3:5.0f} kHz: L(1k) {at(1e3):6.1f}, L(10k) {at(1e4):6.1f}, L(100k) {at(1e5):6.1f}, L(1M) {at(1e6):6.1f} dBc/Hz; "
          f"RMS jitter (1 kHz-10 MHz) {jit*1e15:6.0f} fs")
best = min(jits, key=jits.get)
print(f"   -> jitter-optimal loop bandwidth ~ {best/1e3:.0f} kHz (where in-band PLL/reference noise meets the VCO noise)")
comps, tot, jit, _ = budget(50e3)
for k, v in comps.items():
    print(f"      50 kHz loop, contributor '{k}': at 10 kHz {v[np.argmin(abs(f-1e4))]-18.06:6.1f}, at 100 kHz "
          f"{v[np.argmin(abs(f-1e5))]-18.06:6.1f}, at 1 MHz {v[np.argmin(abs(f-1e6))]-18.06:6.1f} dBc/Hz (433.92 MHz output)")
check("B1 an intermediate loop bandwidth minimises jitter", best not in (10e3, 400e3))
L_floor = PN_SYNTH + 10 * np.log10(fPFD) + 20 * np.log10(N)
print(f"   in-band floor at VCO: PN_SYNTH + 10log fPFD + 20log N = {L_floor:.1f} dBc/Hz -> at 433.92 MHz {L_floor-18.06:.1f} dBc/Hz")
check("B2 in-band floor arithmetic (ADF4351 formula)", abs(L_floor - (-221 + 73.98 + 42.85)) < 0.05)

# ---------------------------------------------------------------- C. lock time (linear)
G_, (C1_, C2_, R2_, R3_, C3_) = closed_loop(50e3)
Kphi = Icp / (2 * np.pi); Kvr = 2 * np.pi * Kv
# Build G(s) as rational: Z(s) for 2nd-order + pole: use numeric fit via signal.freqs? Use state-space by sympy-free route:
# Z(s) = (1 + s T2) / (s A0 (1 + s T1)) * 1/(1 + s T3)  (approximately, R3 loading small)
A0 = C1_ + C2_; T2 = R2_ * C2_; T1 = R2_ * C1_ * C2_ / A0; T3 = R3_ * C3_
num = Kphi * Kvr / N * np.array([T2, 1.0])
den = np.polymul(np.polymul([A0 * T1, A0, 0.0], [T3, 1.0]), [1.0, 0.0])       # s^2 * A0 (1+sT1)(1+sT3)
cl_num = num; cl_den = np.polyadd(den, num)
t = np.linspace(0, 400e-6, 40001)
_, y = signal.step((cl_num, cl_den), T=t)
step_hz = 1e6                                   # 1 MHz VCO frequency step
err = abs(1 - y) * step_hz
settle = t[np.where(err > 1e3)[0][-1] + 1]      # last time error exceeded 1 kHz
print(f"C: 50 kHz loop: a 1 MHz VCO frequency jump settles to within 1 kHz in {settle*1e6:.0f} us "
      f"(order-of-magnitude 4/fc = {4/50e3*1e6:.0f} us); overshoot {100*(y.max()-1):.0f} % (PM ~43 deg with 3rd pole)")
check("C1 linear lock time is tens of microseconds for a 50 kHz loop", 20e-6 < settle < 200e-6)

# ---------------------------------------------------------------- D. MASH 1-1-1
def mash111(frac, n, bits=24):
    M = 1 << bits; X = int(round(frac * M))
    a1 = a2 = a3 = 0
    y = np.zeros(n); c1p = c2p = 0; d2 = d3 = d3b = 0
    c2_hist = [0, 0]; c3_hist = [0, 0, 0]
    out = np.zeros(n, dtype=float)
    # standard MASH 1-1-1 error-feedback structure
    e1 = e2 = 0
    prev_c2 = 0; prev_c3 = 0; prev2_c3 = 0
    for k in range(n):
        a1 += X; c1 = a1 >> bits; a1 &= M - 1
        a2 += a1; c2 = a2 >> bits; a2 &= M - 1
        a3 += a2; c3 = a3 >> bits; a3 &= M - 1
        out[k] = c1 + (c2 - prev_c2) + (c3 - 2 * prev_c3 + prev2_c3)
        prev_c2 = c2; prev2_c3 = prev_c3; prev_c3 = c3
    return out


n = 1 << 17
frac = 0.8544 + 1e-7 * np.pi
yv = mash111(frac, n)
print(f"D: MASH 1-1-1 mean output {yv.mean():.6f} (target {frac:.6f}), output range {yv.min():.0f}..{yv.max():.0f}")
phi = 2 * np.pi * np.cumsum(yv - frac)                 # VCO-referred phase error (rad), sampled at fPFD
fw, P = signal.welch(phi, fs=fPFD, nperseg=1 << 13, return_onesided=True, detrend='constant')
L_sim = 10 * np.log10(P / 2)                            # one-sided S_phi -> L(f) = S_phi/2
L_th = 10 * np.log10((2 * np.pi) ** 2 / (12 * fPFD) * (2 * np.sin(np.pi * np.maximum(fw, 1.0) / fPFD)) ** 4)
sel = (fw > 5e5) & (fw < 5e6)
dev = np.median(L_sim[sel] - L_th[sel])
print(f"   open-loop SD phase noise: simulated vs (2pi)^2/(12 fPFD)*(2 sin(pi f/fPFD))^4 : median deviation {dev:+.2f} dB "
      f"(0.5-5 MHz); e.g. at 1 MHz theory {L_th[np.argmin(abs(fw-1e6))]:.1f} dBc/Hz")
check("D1 MASH-3 quantisation noise matches closed form within 1 dB", abs(dev) < 1.0 and abs(yv.mean() - frac) < 1e-4)
Hc = abs(G_ / (1 + G_))
L_sd_closed = 10 * np.log10((2 * np.pi) ** 2 / (12 * fPFD) * (2 * np.sin(np.pi * f / fPFD)) ** 4) + 20 * np.log10(Hc) - 18.06
print(f"   after the 50 kHz loop (with 3rd pole) at 433.92 MHz: {L_sd_closed[np.argmin(abs(f-1e5))]:.1f} dBc/Hz @100 kHz, "
      f"{L_sd_closed[np.argmin(abs(f-1e6))]:.1f} @1 MHz, {L_sd_closed[np.argmin(abs(f-3e6))]:.1f} @3 MHz")

# ---------------------------------------------------------------- E. reference spur from leakage
# A leakage current I_leak drains the filter continuously; the charge pump replaces Q = I_leak/fPFD in a short
# pulse every cycle. The pulse train's fundamental current is 2*I_leak -> tuning ripple v1 = 2 I_leak |Z(fPFD)|,
# narrow-band FM index beta = Kv*v1/fPFD, spur (dBc) = 20 log(beta/2).
def leak_spur(I_leak, fpfd, fc_, Nn, R3fac=None):
    C1_, C2_, R2_ = design_2nd_order(fc_, PM, Icp, Kv, Nn)
    kw = {}
    if R3fac:
        T1_ = R2_ * C1_ * C2_ / (C1_ + C2_); R3_ = R3fac * R2_; kw = dict(R3=R3_, C3=(T1_ / 4) / R3_)
    Zp = abs(Zfilt(np.array([fpfd]), C1_, C2_, R2_, **kw))[0]
    beta = Kv * 2 * I_leak * Zp / fpfd
    return 20 * np.log10(beta / 2), Zp
for (IL, fp, fcl, lab) in ((1e-9, 25e6, 50e3, "frac-N, fPFD 25 MHz, 50 kHz loop"),
                           (10e-9, 200e3, 10e3, "integer-N, fPFD 200 kHz, 10 kHz loop"),
                           (100e-9, 200e3, 10e3, "integer-N, fPFD 200 kHz, 10 kHz loop")):
    Nn = fVCO / fp
    s2, Z2 = leak_spur(IL, fp, fcl, Nn)
    s3, Z3 = leak_spur(IL, fp, fcl, Nn, R3fac=2)
    print(f"E: {IL*1e9:5.0f} nA leakage, {lab}: |Z(fPFD)| {Z2:8.2f} ohm -> spur {s2:6.1f} dBc (2nd-order), "
          f"{s3:6.1f} dBc with 3rd pole (at the VCO; -18 dB at 433.92 MHz)")
s_hi, _ = leak_spur(1e-9, 25e6, 50e3, fVCO / 25e6)
s_lo, _ = leak_spur(10e-9, 200e3, 10e3, fVCO / 200e3)
print("   -> with a high PFD frequency, leakage spurs are negligible; measured PFD spurs (ADF4351: -80 dBc typ) come from "
      "charge-pump mismatch, dead-zone pulses and supply/substrate coupling")
check("E1 low PFD frequency makes leakage spurs far worse (>60 dB)", s_lo - s_hi > 60)

# ---------------------------------------------------------------- F. DDS
fclk, Nacc = 125e6, 32
print(f"F: DDS 32-bit accumulator at 125 MHz: resolution {fclk/2**Nacc*1e3:.1f} mHz; FTW for 10.7 MHz = {round(10.7e6*2**Nacc/fclk)}")
for fo in (0.1, 0.25, 0.4):
    print(f"   sinc (ZOH) roll-off at {fo:.2f} fclk: {20*np.log10(np.sinc(fo)):.2f} dB")
Nt, P = 20, 8
L = 1 << Nt
worst = -999
for ftw in (0x12345 | 1, 0x0ABCD | 1, (1 << (Nt - P - 1)) + (1 << (Nt - 2)) + 1, 0x7F001):
    acc = (np.arange(L, dtype=np.int64) * ftw) % L
    ph = (acc >> (Nt - P)) / (1 << P)
    x = np.sin(2 * np.pi * ph)
    X = np.abs(np.fft.rfft(x)) / L
    k0 = int(np.argmax(X))
    Xs = X.copy(); Xs[max(0, k0 - 1):k0 + 2] = 0
    sp = 20 * np.log10(Xs.max() / X[k0])
    worst = max(worst, sp)
    print(f"   {Nt}-bit acc, {P}-bit phase, FTW {ftw:#x}: worst spur {sp:.1f} dBc (bound -6.02P = {-6.02*P:.1f} dBc)")
check("F1 phase-truncation spurs obey the -6.02*P dBc bound", worst <= -6.02 * P + 0.2)

# ---------------------------------------------------------------- G. Si5351-style synthesis
xtal = 25e6
target = 10.7e6
best = None
for a_pll in range(24, 37):                       # VCO = xtal*(a + b/c) within 600-900 MHz
    fv = xtal * a_pll
    if not 600e6 <= fv <= 900e6:
        continue
    div = Fraction(int(fv), int(target)).limit_denominator(1048575)
    if 8 <= float(div) <= 900:
        err = fv / float(div) - target
        best = (fv, div, err) if best is None or abs(err) < abs(best[2]) else best
fv, div, err = best
a = div.numerator // div.denominator; b = div.numerator % div.denominator; c = div.denominator
print(f"G: Si5351-style: VCO {fv/1e6:.0f} MHz (integer PLL), multisynth = {a} + {b}/{c} -> {fv/float(div):.6f} Hz "
      f"(error {err:.2e} Hz)")
check("G1 fractional multisynth reaches 10.7 MHz essentially exactly", abs(err) < 1e-3)

# ---------------------------------------------------------------- H. Leeson
def leeson(fm, f0, QL, F_db=6, Ps_dbm=0, fcorner=10e3):
    F = 10 ** (F_db / 10); Ps = 1e-3 * 10 ** (Ps_dbm / 10)
    return 10 * np.log10(0.5 * (1 + (f0 / (2 * QL * fm)) ** 2) * (1 + fcorner / fm) * F * kB * T0 / Ps)
for QL in (10, 30, 100):
    print(f"H: Leeson, 3.5 GHz VCO, QL {QL:3d}, F 6 dB, Ps 0 dBm, 10 kHz flicker corner: L(100 kHz) = {leeson(1e5, 3.5e9, QL):.1f}, "
          f"L(1 MHz) = {leeson(1e6, 3.5e9, QL):.1f} dBc/Hz")
check("H1 Leeson: doubling loaded Q lowers close-in phase noise by 6 dB",
      abs(leeson(1e5, 3.5e9, 20) - leeson(1e5, 3.5e9, 40) - 6.0) < 0.1)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
sys.exit(0 if ok_all else 1)
