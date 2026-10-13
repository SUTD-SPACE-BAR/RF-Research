#!/usr/bin/env python3
"""Verification for the "Linearisation beyond DPD" section of kb/06-rf-circuits/power-amplifiers.md (W5-E7)

Complex-baseband two-tone simulations on a Rapp AM/AM + AM/PM PA model.
 A. Feedforward: loop-2 cancellation C = |1 - g e^{j phi}| sets the IM3 improvement; efficiency penalty
 B. Cartesian feedback: IM3 reduction ~ |1/(1+L(j w))| at the IM offset; stability vs loop phase
    misalignment (unstable beyond 90 deg for a first-order loop)
 C. LINC / outphasing: exact decomposition; Wilkinson-combiner efficiency = 1/PAPR on a 16-QAM signal
 D. EER (Kahn): IM3 vs envelope-path delay and envelope bandwidth
 E. Envelope (amplitude-only) feedback: removes AM/AM but leaves AM/PM -> limited IM3 improvement
Run: python3 tools/verify/rf2_pa_linearisation.py   (runtime ~10 s)
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rf2_common import check, finish
from scipy import signal

fs = 1.0e6; N = 2 ** 15; t = np.arange(N) / fs
k1, k2 = 1000, 1100                         # two-tone bins
f1, f2 = k1 * fs / N, k2 * fs / N
df = f2 - f1


def two_tone(a=0.5):
    return a * (np.exp(2j * np.pi * (f1 - (f1 + f2) / 2) * t) + np.exp(2j * np.pi * (f2 - (f1 + f2) / 2) * t))


def pa(x, p=2.0, Asat=1.0, ampm_deg=15.0):
    r = np.abs(x)
    g = 1 / (1 + (r / Asat) ** (2 * p)) ** (1 / (2 * p))
    ph = np.radians(ampm_deg) * (r / Asat) ** 2 / (1 + (r / Asat) ** 2)
    return x * g * np.exp(1j * ph)


def im3_dbc(y):
    Y = np.fft.fft(y) / N
    fr = np.fft.fftfreq(N, 1 / fs)
    c = (f1 + f2) / 2
    def P(f):
        return np.abs(Y[np.argmin(np.abs(fr - (f - c)))]) ** 2
    tone = max(P(f1), P(f2)); im = max(P(2 * f1 - f2), P(2 * f2 - f1))
    return 10 * np.log10(im / tone)


x = two_tone(0.45)
y0 = pa(x)
im_open = im3_dbc(y0)
print(f"=== reference: Rapp PA (p=2, 15 deg AM/PM), two tones at 0.45: IM3 = {im_open:.1f} dBc")

print("\n=== A. feedforward")
G = 1.0                                     # PA small-signal gain (normalised)
res_ff = []
for gdb, phd in ((0.0, 0.0), (0.1, 1.0), (0.3, 3.0), (1.0, 10.0)):
    main = pa(x)
    err = main / G - x                      # loop 1: perfect carrier cancellation (ideal loop 1)
    gerr = 10 ** (gdb / 20) * np.exp(1j * np.radians(phd))
    out = main - gerr * err * G             # loop 2: subtract amplified error with gain/phase mismatch
    imp = im_open - im3_dbc(out)
    C = -20 * np.log10(abs(1 - gerr)) if (gdb, phd) != (0.0, 0.0) else np.inf
    print(f"  loop-2 error {gdb} dB / {phd} deg: IM3 {im3_dbc(out):7.1f} dBc, improvement {imp:6.1f} dB, cancellation formula {C:6.1f} dB")
    res_ff.append((gdb, phd, imp, C))
check("feedforward IM3 improvement equals the loop-2 cancellation |1 - g e^{j phi}| (within 1 dB)",
      all(abs(r[2] - r[3]) < 1.0 for r in res_ff[1:]))
# efficiency penalty: 10 dB couplers at output (main path loss 0.46 dB) + delay line 0.5 dB, error amp at ~ -20 dB
main_loss = -10 * np.log10(1 - 10 ** (-10 / 10)) + 0.5
print(f"  output 10 dB coupler + 0.5 dB delay line: main-path loss {main_loss:.2f} dB -> main-PA efficiency x {10**(-main_loss/10):.2f};"
      f" plus the class-A error amplifier")
check("feedforward output-path loss ~1 dB (10 dB coupler + delay line)", abs(main_loss - 0.96) < 0.02)

print("\n=== B. Cartesian feedback")
xs = two_tone(0.30)                          # peaks 0.6: inside the PA's correctable range
im_open_s = im3_dbc(pa(xs))
print(f"  open loop at 0.30 per tone: IM3 {im_open_s:.1f} dBc")


def cartesian(K, theta_deg, x, pa_fn=pa):
    dt = 1 / fs
    u = 0j; y = np.zeros_like(x); rot = np.exp(-1j * np.radians(theta_deg))
    for n in range(len(x)):
        yn = pa_fn(np.array([u]))[0]
        y[n] = yn
        u = u + K * dt * (x[n] - rot * yn)
        if abs(u) > 1e3:
            return None
    return y


fc_loop = 50e3                              # loop crossover (Hz) ~ K/(2 pi)
K = 2 * np.pi * fc_loop
y_cf = cartesian(K, 0.0, xs)
im_cf = im3_dbc(y_cf)
f_im = 1.5 * df                              # IM3 offset from centre
pred = 20 * np.log10(abs(1j * f_im / (fc_loop + 1j * f_im)))
print(f"  loop crossover {fc_loop/1e3:.0f} kHz, IM3 offset {f_im/1e3:.2f} kHz: IM3 {im_cf:.1f} dBc, improvement {im_open_s-im_cf:.1f} dB"
      f" (|1/(1+L)| at the IM offset = {-pred:.1f} dB)")
check("Cartesian loop IM3 reduction ~ loop gain at the IM offset (within 4 dB)", abs((im_open_s - im_cf) - (-pred)) < 4)
y_hot = cartesian(K, 0.0, x)
print(f"  same loop at 0.45 per tone (peaks past the PA's saturation): IM3 {im3_dbc(y_hot):.1f} dBc vs open {im_open:.1f} -"
      f" a feedback loop cannot create power the PA does not have")
linpa = lambda u: u * 1.0                     # small-signal (linear) PA for the stability test
for th in (45.0, 80.0, 100.0):
    yy = cartesian(K, th, 0.01 * xs, pa_fn=linpa)
    print(f"  loop phase misalignment {th:.0f} deg (small-signal): " + ("UNSTABLE (diverged)" if yy is None else "stable"))
    if th == 80.0:
        st80 = yy is not None
    if th == 100.0:
        st100 = yy is None
check("first-order Cartesian loop stable at 80 deg misalignment, unstable at 100 deg", st80 and st100)

print("\n=== C. LINC / outphasing")
rng = np.random.default_rng(2)
sym = (rng.integers(0, 4, 4000) * 2 - 3 + 1j * (rng.integers(0, 4, 4000) * 2 - 3)) / np.sqrt(10)
sps = 8
up = np.zeros(len(sym) * sps, complex); up[::sps] = sym
h = signal.firwin(8 * sps + 1, 1 / sps * 1.25)          # crude raised-cosine-like low-pass
s = np.convolve(up, h, mode="same")
Amax = np.max(np.abs(s))
phi = np.angle(s); th_ = np.arccos(np.clip(np.abs(s) / Amax, 0, 1))
s1 = Amax * np.exp(1j * (phi + th_)); s2 = Amax * np.exp(1j * (phi - th_))
recon = (s1 + s2) / 2
check("LINC decomposition reconstructs the signal exactly", np.max(np.abs(recon - s)) < 1e-9)
papr = np.max(np.abs(s) ** 2) / np.mean(np.abs(s) ** 2)
eta_comb = np.mean(np.abs(recon) ** 2) / np.mean((np.abs(s1) ** 2 + np.abs(s2) ** 2) / 2)
print(f"  16-QAM, PAPR {10*np.log10(papr):.1f} dB: Wilkinson-combiner efficiency {eta_comb*100:.1f} % (= 1/PAPR {100/papr:.1f} %)")
check("matched (Wilkinson) LINC combining efficiency = 1/PAPR", abs(eta_comb - 1 / papr) < 1e-6)
for A in (1.0, 0.5, 0.25):
    print(f"  outphasing at A/Amax = {A}: Wilkinson combiner passes {A**2*100:.0f} % of the PA power (rest heats the resistor)")

print("\n=== D. EER (Kahn) envelope path")
base = two_tone(0.45)
env = np.abs(base); ph = np.exp(1j * np.angle(base))
res_d = {}
for tau_us in (0.0, 0.5, 2.0):
    for B in (None, 10 * df, 3 * df):
        e = env.copy()
        if B is not None:
            b, a = signal.butter(1, B / (fs / 2)); e = signal.lfilter(b, a, np.r_[env, env])[N:]
        e = np.roll(e, int(round(tau_us * 1e-6 * fs)))
        y = e * ph
        im = im3_dbc(y)
        res_d[(tau_us, None if B is None else round(B / df))] = im
        print(f"  envelope delay {tau_us:.1f} us ({tau_us*1e-6*df*360:.1f} deg of the {df/1e3:.2f} kHz envelope),"
              f" envelope BW {'inf' if B is None else f'{B/df:.0f}x tone spacing'}: IM3 {im:6.1f} dBc")
check("EER: zero delay and unlimited envelope bandwidth -> IM3 < -100 dBc (ideal reconstruction)", res_d[(0.0, None)] < -100)
check("EER: more delay or less envelope bandwidth -> worse IM3", res_d[(2.0, None)] > res_d[(0.5, None)] and res_d[(0.0, 3)] > res_d[(0.0, 10)])

print("\n=== E. envelope (amplitude-only) feedback")
# ideal amplitude correction: drive so |PA(u)| = |x| exactly (invert AM/AM), phase uncorrected
r_in = np.abs(xs)
rr = np.linspace(0, 0.999, 5000)
r_out = np.abs(pa(rr + 0j))
inv = np.interp(np.clip(r_in, 0, r_out.max() * 0.999), r_out, rr)
u = inv * np.exp(1j * np.angle(xs))
y_env = pa(u)
im_env = im3_dbc(y_env)
y_noampm = pa(u, ampm_deg=0.0)
print(f"  amplitude-only correction: IM3 {im_env:.1f} dBc (open loop {im_open_s:.1f}); with AM/PM = 0 it would be {im3_dbc(y_noampm):.1f} dBc")
check("envelope feedback leaves an AM/PM-limited IM3 floor (> -60 dBc with 15 deg AM/PM)", im_env > -60 and im3_dbc(y_noampm) < -80)

finish()
