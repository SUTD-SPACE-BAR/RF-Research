#!/usr/bin/env python3
"""Verification for kb/00-math-foundations/z-transform-and-discrete-time-systems.md

Checks (all numbers quoted on the page are printed here):
 1. z-transform pairs by direct (truncated) summation inside the ROC; causal vs anti-causal
    sequences sharing one algebraic X(z) but different ROCs.
 2. Partial-fraction inverse (scipy residuez) reproduces the impulse response from lfilter.
 3. Stability <-> poles inside the unit circle (sum |h| finite / divergent).
 4. Unilateral z-transform with an initial condition (y[-1] != 0) vs direct recursion.
 5. Final-value theorem for a step into a first-order IIR.
 6. Frequency response on the unit circle = DTFT of the impulse response.
 7. First-order IIR / exponential moving average (EMA): pole, time constant, -3 dB frequency,
    DC group delay, white-noise variance reduction alpha/(2-alpha) -- worked example values.
 8. Bilinear transform: j-Omega axis -> unit circle, LHP -> inside disc, warping, prewarp;
    manual substitution equals scipy.signal.bilinear.
 9. Impulse invariance: h[n] = T h_a(nT), pole e^{-aT}, aliasing error vs bilinear warping for
    an RC low-pass; matched-z.
10. z = e^{sT}: damping/natural frequency of a discrete second-order section recovered from its
    poles.
11. Digital PLL (PI loop filter + NCO accumulator): closed-loop poles vs e^{sT} of the analogue
    design, zero steady-state phase error to a frequency step (type 2), noise bandwidth B_n T.
12. First-order and second-order sigma-delta modulators: exact identity Y = z^-1 X + (1-z^-1) E,
    in-band noise vs the pi^2/(3 OSR^3) and pi^4/(5 OSR^5) formulas, 9 and 15 dB/octave.
13. CIC decimator: ((1-z^-R)/(1-z^-1))^N equals N cascaded moving sums; DC gain R^N.
14. Linear-phase FIR group delay (N-1)/2.
15. Second-order stability triangle (Jury) vs root test; forward/backward Euler mappings.
16. Resonator -3 dB width ~ 2(1-r) rad/sample; discrete state-space poles eig(e^{AT}) = e^{eig(A)T}.
Run: python3 tools/verify/est_ztransform.py
"""
import numpy as np
from scipy import signal

ok_all = True
rng = np.random.default_rng(20261002)


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel and want != 0 else 1.0)
    ok = err <= tol
    ok_all &= bool(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol}{' rel' if rel else ''})")


def check_true(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


print("== 1. z-transform pairs by direct summation ==")
a = 0.8
z0 = 1.1 * np.exp(1j * 0.7)            # |z0| = 1.1 > |a|: inside ROC of causal a^n u[n]
n = np.arange(0, 2000)
X_sum = np.sum(a ** n * z0 ** (-n))
X_formula = 1 / (1 - a / z0)
check("a^n u[n] summed at |z|=1.1 vs 1/(1-a z^-1) (abs err)", abs(X_sum - X_formula), 0.0, 1e-10)
# anti-causal -a^n u[-n-1], ROC |z| < |a|
z1 = 0.5 * np.exp(1j * 0.3)
m = np.arange(1, 2000)                  # n = -m
X_anti = np.sum(-(a ** (-m)) * z1 ** m)
check("-a^n u[-n-1] summed at |z|=0.5 vs same 1/(1-a z^-1)", abs(X_anti - 1 / (1 - a / z1)), 0.0, 1e-10)
# n a^n u[n] <-> a z^-1/(1-a z^-1)^2
X_sum2 = np.sum(n * a ** n * z0 ** (-n))
check("n a^n u[n] vs a z^-1/(1-a z^-1)^2", abs(X_sum2 - (a / z0) / (1 - a / z0) ** 2), 0.0, 1e-9)
# r^n cos(w0 n) u[n] <-> (1 - r cos w0 z^-1)/(1 - 2 r cos w0 z^-1 + r^2 z^-2)
r, w0 = 0.95, 0.4
X_sum3 = np.sum(r ** n * np.cos(w0 * n) * z0 ** (-n))
zi = 1 / z0
X_f3 = (1 - r * np.cos(w0) * zi) / (1 - 2 * r * np.cos(w0) * zi + r ** 2 * zi ** 2)
check("r^n cos(w0 n) u[n] pair", abs(X_sum3 - X_f3), 0.0, 1e-9)

print("\n== 2. partial-fraction inverse ==")
b = [1.0, 0.5]
den = np.convolve([1, -0.9], [1, 0.4])            # poles 0.9, -0.4
rr, pp, kk = signal.residuez(b, den)
imp = np.zeros(60); imp[0] = 1
h_lf = signal.lfilter(b, den, imp)
nn = np.arange(60)
h_pf = np.real(sum(rr[i] * pp[i] ** nn for i in range(len(rr))))
if len(kk):
    h_pf[:len(kk)] += np.real(kk)
check("residuez reconstruction max error", np.max(np.abs(h_pf - h_lf)), 0.0, 1e-12)
print(f"    residues {np.round(rr.real, 6)} at poles {np.round(pp.real, 6)}")

print("\n== 3. stability <-> poles inside unit circle ==")
imp = np.zeros(5000); imp[0] = 1
h_st = signal.lfilter([1], [1, -1.6, 0.81], imp)    # poles 0.9 e^{+-j...}, |p| = 0.9
h_un = signal.lfilter([1], [1, -1.6, 1.05], imp[:400])  # |p| = sqrt(1.05) > 1
check("stable section: sum|h| converges (finite, < 1e3)", float(np.sum(np.abs(h_st)) < 1e3), 1.0, 0)
check("|p| of [1,-1.6,0.81] = 0.9", np.max(np.abs(np.roots([1, -1.6, 0.81]))), 0.9, 1e-12)
check_true("unstable section (|p|=1.025) grows: |h[399]| > 1e3", abs(h_un[-1]) > 1e3)

print("\n== 4. unilateral z-transform with initial condition ==")
# y[n] - a y[n-1] = x[n], y[-1] = y0, x = u[n]  ->  Y(z) = (X(z) + a y0)/(1 - a z^-1)
a4, y0 = 0.7, 2.0
N4 = 40
y = np.zeros(N4); prev = y0
for k in range(N4):
    y[k] = a4 * prev + 1.0
    prev = y[k]
# inverse of (1/(1-z^-1) + a y0)/(1-a z^-1): step response + a*y0*a^n
k = np.arange(N4)
y_formula = (1 - a4 ** (k + 1)) / (1 - a4) + a4 * y0 * a4 ** k
check("IC response max error", np.max(np.abs(y - y_formula)), 0.0, 1e-12)

print("\n== 5. final-value theorem ==")
# step into H(z) = 0.2/(1 - 0.8 z^-1): lim (1 - z^-1) Y(z) at z->1 = H(1) = 1
ystep = signal.lfilter([0.2], [1, -0.8], np.ones(400))
check("FVT: step response final value = H(1) = 1", ystep[-1], 1.0, 1e-9)

print("\n== 6. frequency response on unit circle = DTFT of h ==")
bb, aa = signal.butter(3, 0.2)
w, H = signal.freqz(bb, aa, worN=512)
imp = np.zeros(4000); imp[0] = 1
hh = signal.lfilter(bb, aa, imp)
H_dtft = np.array([np.sum(hh * np.exp(-1j * wk * np.arange(len(hh)))) for wk in w[::32]])
check("freqz vs DTFT of impulse response (max abs err)", np.max(np.abs(H_dtft - H[::32])), 0.0, 1e-9)

print("\n== 7. first-order IIR (EMA) worked example: fs = 100 Hz, alpha = 0.1 ==")
fs, alpha = 100.0, 0.1
T = 1 / fs
p = 1 - alpha
tau = -T / np.log(p)
check("pole = 1 - alpha", p, 0.9, 1e-15)
check("time constant tau = -T/ln(1-alpha) [s]", tau, 0.0949122, 1e-6)
check("T/alpha approximation [s]", T / alpha, 0.1, 1e-12)
# -3 dB: |H|^2 = alpha^2/(1 - 2p cos w + p^2) = 1/2  ->  cos w = (1 + p^2 - 2 alpha^2)/(2p)
cw = (1 + p ** 2 - 2 * alpha ** 2) / (2 * p)
f3 = np.arccos(cw) / (2 * np.pi) * fs
w3, H3 = signal.freqz([alpha], [1, -p], worN=[2 * np.pi * f3 / fs])
check("-3 dB frequency [Hz] (closed form)", f3, 1.67842, 1e-4)
check("|H| at that frequency = -3.0103 dB", 20 * np.log10(abs(H3[0])), -3.0103, 1e-3)
check("analogue estimate 1/(2 pi tau) [Hz]", 1 / (2 * np.pi * tau), 1.6769, 1e-3)
gd = p / alpha                                   # DC group delay in samples: p/(1-p)
wg, gdel = signal.group_delay(([alpha], [1, -p]), w=[1e-6])
check("DC group delay = (1-alpha)/alpha samples", gdel[0], gd, 1e-6)
check("DC group delay [ms]", gd * T * 1e3, 90.0, 1e-9)
vr = alpha / (2 - alpha)
x = rng.standard_normal(400000)
yv = signal.lfilter([alpha], [1, -p], x)[1000:]
check("white-noise variance ratio alpha/(2-alpha)", np.var(yv), vr, 0.02, rel=True)
check("noise std reduction factor sqrt(alpha/(2-alpha))", np.sqrt(vr), 0.229416, 1e-6)
# ENBW in Hz (one-sided) = (fs/2) * vr / |H(0)|^2 * ... : variance ratio = 2*ENBW/fs
check("ENBW [Hz] = vr*fs/2", vr * fs / 2, 2.631579, 1e-5)
check("ENBW / f3dB (vs pi/2 = 1.571 for analogue RC)", vr * fs / 2 / f3, 1.5696, 2e-3)

print("\n== 8. bilinear transform ==")
Tb = 1e-4
Om = np.array([10.0, 1e3, 1e4, 1e5])
zz = (1 + 1j * Om * Tb / 2) / (1 - 1j * Om * Tb / 2)
check("j-axis maps to |z| = 1 (max dev)", np.max(np.abs(np.abs(zz) - 1)), 0.0, 1e-14)
s_lhp = -500 + 2e3j
z_lhp = (1 + s_lhp * Tb / 2) / (1 - s_lhp * Tb / 2)
check_true("LHP point maps inside unit disc", abs(z_lhp) < 1)
# warping: omega = 2 arctan(Omega T/2)
wd = 2 * np.arctan(Om * Tb / 2)
check("digital freq of Omega=1e4 rad/s at T=1e-4 (rad/sample)", wd[2], 2 * np.arctan(0.5), 1e-15)
# manual vs scipy for H(s) = wc/(s+wc), RC with fc = 1 kHz, fs = 10 kHz
fs8, fc = 10000.0, 1000.0
wc = 2 * np.pi * fc
bz, az = signal.bilinear([wc], [1, wc], fs=fs8)
K = 2 * fs8
b_man = np.array([wc, wc]) / (K + wc)
a_man = np.array([1, (wc - K) / (K + wc)])
check("bilinear manual vs scipy (b)", np.max(np.abs(bz - b_man)), 0.0, 1e-12)
check("bilinear manual vs scipy (a)", np.max(np.abs(az - a_man)), 0.0, 1e-12)
_, Hb = signal.freqz(bz, az, worN=[2 * np.pi * fc / fs8])
check("unwarped bilinear |H| at 1 kHz [dB] (not -3.01: warping)", 20 * np.log10(abs(Hb[0])), -3.15902, 1e-4)
wcp = 2 * fs8 * np.tan(np.pi * fc / fs8)
bp, ap = signal.bilinear([wcp], [1, wcp], fs=fs8)
_, Hp = signal.freqz(bp, ap, worN=[2 * np.pi * fc / fs8])
check("prewarped bilinear |H| at 1 kHz [dB]", 20 * np.log10(abs(Hp[0])), -3.0103, 1e-4)
check("prewarped analogue corner [Hz]", wcp / (2 * np.pi), 1034.25, 0.01)
# nyquist: bilinear has a zero at z=-1 (|H|=0 at fs/2)
_, Hn = signal.freqz(bz, az, worN=[np.pi])
check("bilinear RC: |H(fs/2)| = 0 (zero at z=-1)", abs(Hn[0]), 0.0, 1e-12)

print("\n== 9. impulse invariance and matched-z ==")
aI = wc                                          # h_a(t) = wc e^{-wc t}
bi = [Tb * 0 + 1 / fs8 * aI]
ai = [1, -np.exp(-aI / fs8)]
imp = np.zeros(50); imp[0] = 1
hI = signal.lfilter(bi, ai, imp)
nI = np.arange(50)
check("impulse invariance: h[n] = T h_a(nT)", np.max(np.abs(hI - aI / fs8 * np.exp(-aI * nI / fs8))), 0.0, 1e-14)
check("impulse-invariant pole e^{-wc T}", np.exp(-aI / fs8), 0.533488, 1e-6)
_, HI0 = signal.freqz(bi, ai, worN=[1e-9])
check("impulse-invariant DC gain wcT/(1-e^-wcT) (aliasing: not 1)", abs(HI0[0]), 0.2 * np.pi / (1 - np.exp(-0.2 * np.pi)), 1e-6)
_, HIn = signal.freqz(bi, ai, worN=[np.pi])
check("impulse-invariant |H(fs/2)| [dB] (aliased floor, analogue -14.2 dB)", 20 * np.log10(abs(HIn[0])), 20 * np.log10(0.2 * np.pi / (1 + np.exp(-0.2 * np.pi))), 1e-6)
# analogue |H| at 5 kHz
check("analogue RC |H| at 5 kHz [dB]", 20 * np.log10(1 / np.sqrt(1 + 25)), -14.1497, 1e-3)
# matched-z: pole at e^{-wc T}, zero at z=-1 for strictly-proper -> here keep DC gain = 1
pm = np.exp(-wc / fs8)
bm = [(1 - pm)]
am = [1, -pm]
_, Hm = signal.freqz(bm, am, worN=[1e-9])
check("matched-z (DC-normalised) DC gain", abs(Hm[0]), 1.0, 1e-9)

print("\n== 10. z = e^{sT} for a second-order section ==")
zeta, fn, fs10 = 0.3, 50.0, 1000.0
wn = 2 * np.pi * fn
s_p = -zeta * wn + 1j * wn * np.sqrt(1 - zeta ** 2)
zp = np.exp(s_p / fs10)
den10 = np.real(np.poly([zp, np.conj(zp)]))
pz = np.roots(den10)[0]
s_back = np.log(pz) * fs10
wn_back = abs(s_back)
zeta_back = -np.real(s_back) / wn_back
check("recovered natural frequency [Hz]", wn_back / (2 * np.pi), 50.0, 1e-9)
check("recovered damping ratio", zeta_back, 0.3, 1e-12)
check("pole radius e^{-zeta wn T}", abs(zp), np.exp(-zeta * wn / fs10), 1e-14)

print("\n== 11. digital PLL (PI filter + NCO) ==")
# Phase detector gain Kd = 1 rad/rad, NCO: theta[n+1] = theta[n] + K0 * v[n]  (K0 = 1)
# Loop filter F(z) = Kp + Ki/(1 - z^-1). Gains from B_n T and zeta (standard design, e.g. M. Rice App. C).
BnT, zeta11 = 0.01, 1 / np.sqrt(2)
th = BnT / (zeta11 + 1 / (4 * zeta11))
den_g = 1 + 2 * zeta11 * th + th ** 2
Kp = 4 * zeta11 * th / den_g
Ki = 4 * th ** 2 / den_g
# Open loop: L(z) = (Kp + Ki/(1-z^-1)) * z^-1/(1-z^-1)
# Closed loop char. poly: (1 - z^-1)^2 + z^-1 (Kp(1-z^-1) + Ki) = 0
#  -> z^2 + (Kp + Ki - 2) z + (1 - Kp) = 0
cp = [1, Kp + Ki - 2, 1 - Kp]
poles = np.roots(cp)
check_true("PLL closed-loop poles inside unit circle", np.all(np.abs(poles) < 1))
# analogue equivalent: wn T = 2 th/(1 ... ) approx; compare pole with e^{sT} of 2nd-order analogue loop
# analogue type-2 loop: B_n = wn (zeta + 1/(4 zeta))/2  -> wn T = 2 B_n T/(zeta + 1/(4 zeta))
wnT = 2 * BnT / (zeta11 + 1 / (4 * zeta11))
s_an = (-zeta11 + 1j * np.sqrt(1 - zeta11 ** 2)) * wnT
z_an = np.exp(s_an)
p_up = poles[np.argmax(poles.imag)]
check("PLL pole vs e^{sT} of analogue loop (abs dist)", abs(p_up - z_an), 0.0, 2e-3)
# simulate frequency step: input phase ramp
Nsim = 3000
dw = 0.01                                  # rad/sample frequency step at n = 0
phi_in = dw * np.arange(Nsim)
theta = 0.0; integ = 0.0; err = np.zeros(Nsim)
for k in range(Nsim):
    e = phi_in[k] - theta
    err[k] = e
    integ += Ki * e
    v = Kp * e + integ
    theta += v
check("type-2 PLL: steady-state phase error to frequency step ~ 0", abs(err[-1]), 0.0, 1e-8)
# noise bandwidth: B_n T = (1/2pi) * integral |H_cl|^2 dw over (-pi, pi) / 2  (one-sided, Hz*T)
# closed loop H(z) = z^-1 F(z) /(1 - z^-1 + z^-1 F(z)) * (1-z^-1)/(1-z^-1)
wgrid = np.linspace(-np.pi, np.pi, 200001)
zg = np.exp(1j * wgrid)
F = Kp + Ki / (1 - 1 / zg)
Lz = F * (1 / zg) / (1 - 1 / zg)
Hcl = Lz / (1 + Lz)
BnT_num = np.trapezoid(np.abs(Hcl) ** 2, wgrid) / (2 * np.pi) / 2
check("PLL one-sided noise bandwidth B_n T (numeric)", BnT_num, BnT, 0.03, rel=True)
print(f"    Kp = {Kp:.6f}, Ki = {Ki:.3e}, |poles| = {np.abs(poles)}")

print("\n== 12. sigma-delta modulators ==")


def sdm1(x):
    v = 0.0; y = np.zeros_like(x); e = np.zeros_like(x)
    for k in range(len(x)):
        v += x[k] - (y[k - 1] if k else 0.0)
        y[k] = 1.0 if v >= 0 else -1.0
        e[k] = y[k] - v
    return y, e


def sdm2(x):
    v1 = v2 = 0.0; y = np.zeros_like(x); yprev = 0.0
    for k in range(len(x)):
        v1 += x[k] - yprev
        v2 += v1 - yprev
        y[k] = 1.0 if v2 >= 0 else -1.0
        yprev = y[k]
    return y


Ns = 2 ** 17
nS = np.arange(Ns)
xs = 0.5 * np.sin(2 * np.pi * 37 / Ns * nS) + 0.0 * nS
y1, e1 = sdm1(xs)
# identity: y[n] = x[n-1] + e[n] - e[n-1]  where v[n] = v[n-1] + x[n] - y[n-1], e = y - v
# derive: v[n] = sum_{k<=n} x[k] - sum_{k<n} y[k]; y[n] = v[n] + e[n] -> check Y = z^-1 X + (1 - z^-1) E form on v-recursion
lhs = y1[1:]
rhs = xs[1:] + e1[1:] - e1[:-1]           # with this integrator placement STF = 1 (no delay)
check("first-order SDM exact identity y = x + (1 - z^-1) e  (max err)", np.max(np.abs(lhs - rhs)), 0.0, 1e-12)


def inband_noise(y, x, osr):
    win = np.hanning(len(y))
    Y = np.fft.rfft((y - x) * win)
    P = np.abs(Y) ** 2 / np.sum(win ** 2)        # per-bin power, two-sided-equivalent units
    nb = int(len(y) / (2 * osr))
    return 2 * np.sum(P[1:nb]) / len(y)          # in-band noise power (approx.)


delta2_12 = (2.0) ** 2 / 12                         # 1-bit quantiser levels +-1 -> step 2
res1 = {}
res2 = {}
y2 = sdm2(xs)
for osr in (32, 64, 128):
    res1[osr] = inband_noise(y1, xs, osr)
    res2[osr] = inband_noise(y2, xs, osr)
th1 = {o: delta2_12 * np.pi ** 2 / (3 * o ** 3) for o in res1}
th2 = {o: delta2_12 * np.pi ** 4 / (5 * o ** 5) for o in res2}
for o in (32, 64, 128):
    print(f"    OSR {o}: 1st-order in-band noise {10*np.log10(res1[o]):.1f} dB (theory {10*np.log10(th1[o]):.1f}); "
          f"2nd-order {10*np.log10(res2[o]):.1f} dB (theory {10*np.log10(th2[o]):.1f})")
slope1 = 10 * np.log10(res1[32] / res1[128]) / 2
slope2 = 10 * np.log10(res2[32] / res2[128]) / 2
check("1st-order SDM: in-band noise falls ~9 dB per octave of OSR", slope1, 9.03, 2.0)
check("2nd-order SDM: in-band noise falls ~15 dB per octave of OSR", slope2, 15.05, 2.5)
check("1st-order in-band noise at OSR 64 vs pi^2/(3 OSR^3) model [dB]", 10 * np.log10(res1[64] / th1[64]), 0.0, 3.0)
check("2nd-order in-band noise at OSR 64 vs pi^4/(5 OSR^5) model [dB]", 10 * np.log10(res2[64] / th2[64]), 0.0, 4.0)
# NTF magnitude at w: |1 - e^{-jw}| = 2 sin(w/2)
check("|NTF1| at fs/4 = sqrt(2)", abs(1 - np.exp(-1j * np.pi / 2)), np.sqrt(2), 1e-12)

print("\n== 13. CIC decimator ==")
R, Nst = 8, 3
xc = rng.standard_normal(500)
bc = np.ones(R)
yc = xc.copy()
for _ in range(Nst):
    yc = np.convolve(yc, bc)[:len(xc)]
# recursive form: N integrators then N combs (1 - z^-R)
yr = xc.copy()
for _ in range(Nst):
    yr = np.cumsum(yr)
for _ in range(Nst):
    yr = yr - np.concatenate([np.zeros(R), yr[:-R]])
check("CIC: integrator-comb == cascaded moving sums (max err)", np.max(np.abs(yr - yc)), 0.0, 1e-8)
check("CIC DC gain R^N", float(np.polyval(np.ones(R), 1) ** Nst), R ** Nst, 0)

print("\n== 14. linear-phase FIR group delay ==")
hf = signal.firwin(31, 0.2)
_, gdf = signal.group_delay((hf, [1]), w=np.linspace(0.01, 0.15, 10) * np.pi)
check("31-tap symmetric FIR group delay = 15 samples", np.max(np.abs(gdf - 15)), 0.0, 1e-6)

print("\n== 15. second-order stability triangle and Euler mappings ==")
# z^2 + a1 z + a2 stable  <=>  |a2| < 1 and |a1| < 1 + a2
A = rng.uniform(-2.5, 2.5, size=(20000, 2))
tri = (np.abs(A[:, 1]) < 1) & (np.abs(A[:, 0]) < 1 + A[:, 1])
rts = np.array([np.max(np.abs(np.roots([1, a1, a2]))) < 1 for a1, a2 in A])
check("stability triangle agrees with root test (fraction mismatched)", np.mean(tri != rts), 0.0, 0)
# forward Euler s=(z-1)/T: stable s=-a maps to z = 1 - aT, unstable if aT > 2
check_true("forward Euler: s=-3e4 at T=1e-4 -> z=-2 (outside: unstable)", abs(1 - 3e4 * 1e-4) > 1)
# backward Euler s=(1-z^-1)/T -> z = 1/(1 - sT): LHP maps inside circle |z - 1/2| = 1/2
sl = -np.abs(rng.normal(size=1000)) * 1e4 + 1j * rng.normal(size=1000) * 1e4
zb = 1 / (1 - sl * 1e-4)
check_true("backward Euler: LHP lands inside |z-1/2|<1/2", np.all(np.abs(zb - 0.5) < 0.5))

print("\n== 16. resonator bandwidth vs pole radius; state-space poles ==")
from scipy.linalg import expm
r16, th16 = 0.99, 0.5
w16 = np.linspace(th16 - 0.1, th16 + 0.1, 400001)
_, H16 = signal.freqz([1], [1, -2 * r16 * np.cos(th16), r16 ** 2], worN=w16)
P16 = np.abs(H16) ** 2
above = w16[P16 >= P16.max() / 2]
check("resonator -3 dB width [rad/sample] vs 2(1-r)", above[-1] - above[0], 2 * (1 - r16), 0.01, rel=True)
Ac = np.array([[0, 1], [-wn ** 2, -2 * zeta * wn]])
Fd = expm(Ac / fs10)
ev = np.sort_complex(np.linalg.eigvals(Fd))
evc = np.sort_complex(np.exp(np.linalg.eigvals(Ac) / fs10))
check("eig(expm(A T)) = exp(eig(A) T) (max err)", np.max(np.abs(ev - evc)), 0.0, 1e-12)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
