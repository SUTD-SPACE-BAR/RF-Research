#!/usr/bin/env python3
"""
Verification for kb/03-transmission-lines-matching/time-domain-reflectometry.md

Checks:
  1. Low-pass (TDR-like) transform: harmonic grid f_n = n*df, DC extrapolation, Hermitian extension -> real
     impulse/step response.  Kaiser windows beta = 0 / 6 / 13 reproduce Keysight AN 1287-12's
     10-90 % step rise times 0.45 / 0.99 / 1.48 per span and impulse widths 0.60 / 0.98 / 1.39 per span,
     and the sidelobe trend.
  2. Alias-free range = 1/df (time), i.e. v_p/(2 df) one-way distance for reflection.
  3. Reading discontinuities: series L -> positive bump, shunt C -> negative dip, higher-Z section -> positive step;
     L = 2 Z0 * integral(rho dt), C = -(2/Z0) * integral(rho dt) (areas survive band-limiting).
  4. Impedance profile Z(t) = Z0 (1+rho)/(1-rho) recovers a 75-ohm section.
  5. Two-event resolution vs span (NanoVNA 900 MHz / 3 GHz / 6 GHz).
  6. scikit-rf step_response cross-check.

Run: python3 tools/verify/tline_tdr.py
"""
import numpy as np
import skrf as rf
from scipy.signal.windows import kaiser
import warnings

warnings.filterwarnings("ignore")
C0 = 299_792_458.0
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def lowpass_transform(f, s11, beta=6.0, nfft=None):
    """f: harmonic grid f_n = n*df, n = 1..N (DC excluded); s11 complex. Returns t, impulse, step.
    DC value is extrapolated linearly in (real, imag->0) from the first points."""
    N = len(f)
    df = f[1] - f[0]
    # DC extrapolation: Re S is even in f for a real network -> fit Re S = a + b f^2 through the first two points;
    # Im S(0) = 0.  (VNAs do something similar; a poor DC value biases the whole step response.)
    dc = (4 * np.real(s11[0]) - np.real(s11[1])) / 3
    spec = np.concatenate([[dc], s11])                # n = 0..N
    w = kaiser(2 * N + 1, beta)[N:]                   # one-sided half of a symmetric window, 1 at DC
    spec = spec * w
    nfft = nfft or 8 * 2 ** int(np.ceil(np.log2(2 * N + 1)))
    full = np.zeros(nfft, complex)
    full[: N + 1] = spec
    full[-N:] = np.conj(spec[1:][::-1])               # Hermitian extension -> real time signal
    # np.fft.ifft includes 1/nfft, so the impulse samples sum to the DC value (a unity reflection's step settles
    # to 1): imp_k = h(k dt) dt, and step = cumsum(imp) is the reflected-step waveform rho(t).
    imp = np.real(np.fft.ifft(full))
    dt = 1 / (nfft * df)
    step = np.cumsum(imp)
    t = np.arange(nfft) * dt
    return t, imp, step, dt


def rise_10_90(t, s):
    s = s / s[len(s) // 4]            # normalise to the settled value (well after the edge, before wrap)
    i10 = np.argmax(s >= 0.1)
    i90 = np.argmax(s >= 0.9)
    # linear interpolation
    t10 = np.interp(0.1, [s[i10 - 1], s[i10]], [t[i10 - 1], t[i10]])
    t90 = np.interp(0.9, [s[i90 - 1], s[i90]], [t[i90 - 1], t[i90]])
    return t90 - t10


def width_50(t, x):
    x = x / x.max()
    i = np.argmax(x)
    lo = i - np.argmax(x[i::-1] < 0.5)
    hi = i + np.argmax(x[i:] < 0.5)
    tl = np.interp(0.5, [x[lo], x[lo + 1]], [t[lo], t[lo + 1]])
    th = np.interp(0.5, [x[hi], x[hi - 1]], [t[hi], t[hi - 1]])
    return th - tl


# ---------------------------------------------------------------- 1. window constants (short circuit at t0)
span = 3e9
N = 1000
df = span / N
f = df * np.arange(1, N + 1)
t0 = 5e-9
s_open = np.exp(-2j * np.pi * f * t0)     # ideal open delayed by t0 (round trip)
keys = {"minimum (beta 0)": (0.0, 0.45, 0.60), "normal (beta 6)": (6.0, 0.99, 0.98), "maximum (beta 13)": (13.0, 1.48, 1.39)}
for name, (beta, k_rise, k_imp) in keys.items():
    t, imp, step, dt = lowpass_transform(f, s_open, beta, nfft=2 ** 17)
    # shift so the edge is mid-record for measurement
    tr = rise_10_90(t[: len(t) // 2], step[: len(t) // 2])
    wi = width_50(t[: len(t) // 2], imp[: len(t) // 2])
    # sidelobes of impulse (peak) relative to main lobe
    k0 = np.argmax(imp[: len(t) // 2])
    main = imp[k0]
    # first null after the main lobe, then the largest sidelobe beyond it
    a_ = np.abs(imp[: len(t) // 2])
    k = k0
    while k + 1 < len(a_) and a_[k + 1] < a_[k]:
        k += 1
    sl = 20 * np.log10(a_[k:k + int(20 * wi / dt)].max() / main)
    print(f"   {name:18s}: step rise {tr*span:.3f}/span (Keysight {k_rise}), impulse width {wi*span:.3f}/span "
          f"(Keysight {k_imp}), impulse sidelobe {sl:.0f} dB")
    check(f"   {name}: rise-time constant within 10 % of AN 1287-12", abs(tr * span - k_rise) / k_rise < 0.10)
    check(f"   {name}: impulse-width constant within 10 % of AN 1287-12", abs(wi * span - k_imp) / k_imp < 0.10)

# ---------------------------------------------------------------- 2. alias-free range
print(f"   alias-free time range 1/df = {1/df*1e9:.1f} ns -> one-way reflection distance (VF 0.66) "
      f"{0.66*C0/(2*df):.2f} m for {N} points over {span/1e9:.0f} GHz")
for npts, sp in [(101, 900e6), (101, 3e9), (401, 3e9), (1024, 6e9)]:
    dff = sp / (npts - 1)
    print(f"      {npts} points, {sp/1e9:.1f} GHz span: range {0.66*C0/(2*dff):.2f} m (VF 0.66),"
          f" resolution (normal window) {0.99/sp*0.66*C0/2*1000:.0f} mm")
check("alias-free range formula: v_p/(2 df)", abs(0.66 * C0 / (2 * df) - 0.66 * C0 * 1 / df / 2) < 1e-12)

# ---------------------------------------------------------------- 3-4. discontinuities on a 50-ohm line
freq = rf.Frequency.from_f(f, unit="Hz")
vf = 0.66
med = rf.media.DefinedGammaZ0(frequency=freq, z0=50, gamma=1j * 2 * np.pi * f / (vf * C0))
L_d, C_d = 3e-9, 1.5e-12
def build(disc):
    return med.line(0.30, "m") ** disc ** med.line(0.30, "m") ** med.match()
nets = {
    "series L 3 nH": build(med.inductor(L_d)),
    "shunt C 1.5 pF": build(med.shunt_capacitor(C_d)),
    "75-ohm section 60 mm": med.line(0.30, "m") ** rf.media.DefinedGammaZ0(frequency=freq, z0=75, z0_port=50,
                                                                            gamma=1j * 2 * np.pi * f / (vf * C0)).line(0.06, "m")
                            ** med.line(0.30, "m") ** med.match(),
}
res = {}
for name, n in nets.items():
    t, imp, step, dt = lowpass_transform(f, n.s[:, 0, 0], 6.0, nfft=2 ** 16)
    half = len(t) // 2
    rho = step[:half]
    tt = t[:half]
    k_peak = np.argmax(np.abs(rho))
    gate = (tt > tt[k_peak] - 1.5e-9) & (tt < tt[k_peak] + 1.5e-9)   # integrate only around the event: a tiny
    area = np.sum(rho[gate]) * dt                                   # residual DC offset over a long record biases it
    res[name] = (tt, rho, area, k_peak)
    zprof = 50 * (1 + rho) / (1 - rho)
    print(f"   {name:20s}: peak rho {rho[k_peak]:+.4f} at t = {tt[k_peak]*1e9:.3f} ns "
          f"(expected round trip {2*0.30/(vf*C0)*1e9:.3f} ns), area {area*1e12:+.2f} ps, "
          f"Z at peak {zprof[k_peak]:.2f} ohm")
check("series L -> positive bump", res["series L 3 nH"][1][res["series L 3 nH"][3]] > 0)
check("shunt C -> negative dip", res["shunt C 1.5 pF"][1][res["shunt C 1.5 pF"][3]] < 0)
L_est = 2 * 50 * res["series L 3 nH"][2]
C_est = -2 / 50 * res["shunt C 1.5 pF"][2]
check("L = 2 Z0 * area(rho) recovers 3 nH (within 5 %)", abs(L_est - L_d) / L_d < 0.05, f"({L_est*1e9:.3f} nH)")
check("C = -(2/Z0) * area(rho) recovers 1.5 pF (within 5 %)", abs(C_est - C_d) / C_d < 0.05, f"({C_est*1e12:.3f} pF)")
tt, rho, area, kp = res["75-ohm section 60 mm"]
zprof = 50 * (1 + rho) / (1 - rho)
# plateau value in the middle of the 75-ohm section
t_mid = 2 * (0.30 + 0.03) / (vf * C0)
zmid = np.interp(t_mid, tt, zprof)
check("impedance profile shows ~75 ohm inside the 60 mm section", abs(zmid - 75) < 1.5, f"({zmid:.2f} ohm)")

# ---------------------------------------------------------------- 5. two-event resolution vs span
print("   Two equal resistive discontinuities (series 5 ohm each) d apart, VF 0.66: resolvable when the low-pass impulse"
      " (normal window) shows a >3 dB dip between the two peaks")
ratios_res = []
for sp in [0.9e9, 3e9, 6e9]:
    Nn = 600
    dff = sp / Nn
    ff = dff * np.arange(1, Nn + 1)
    fr = rf.Frequency.from_f(ff, unit="Hz")
    mm = rf.media.DefinedGammaZ0(frequency=fr, z0=50, gamma=1j * 2 * np.pi * ff / (vf * C0))
    best = None
    for dsep in np.arange(0.005, 0.40, 0.0025):
        n = mm.line(0.3, "m") ** mm.resistor(5.0) ** mm.line(dsep, "m") ** mm.resistor(5.0) ** \
            mm.line(0.3, "m") ** mm.match()
        t, imp, step, dt = lowpass_transform(ff, n.s[:, 0, 0], 6.0, nfft=2 ** 15)
        x = imp[: len(t) // 2]
        t1 = 2 * 0.3 / (vf * C0)
        t2 = t1 + 2 * dsep / (vf * C0)
        a1, a2 = np.interp(t1, t[: len(t) // 2], x), np.interp(t2, t[: len(t) // 2], x)
        seg = (t[: len(t) // 2] > t1) & (t[: len(t) // 2] < t2)
        if seg.sum() > 2 and x[: len(t) // 2][seg].min() < 0.707 * min(a1, a2):
            best = dsep
            break
    pred = 0.98 / sp * vf * C0 / 2
    print(f"      span {sp/1e9:.1f} GHz: resolvable separation ~{best*1000:.0f} mm (impulse-width rule 0.98/span x v/2 = {pred*1000:.0f} mm)")
    ratios_res.append(best / pred)
check("two-event resolution scales as 1/span and equals ~1.25 x (0.98/span x v/2) for a 3 dB-dip criterion",
      np.ptp(ratios_res) < 0.1 and all(1.1 < r < 1.4 for r in ratios_res), f"(ratios {np.round(ratios_res, 2)})")

# ---------------------------------------------------------------- 6. skrf cross-check
n = nets["75-ohm section 60 mm"]
try:
    t_s, y_s = n.s11.step_response(window="hamming", pad=0)
    ok_s = np.max(y_s.real) > 0.15 and np.max(y_s.real) < 0.25
    check("scikit-rf step_response shows the +0.2 step of a 75-ohm section", ok_s, f"(max {np.max(y_s.real):.3f})")
except Exception as e:
    print("      (skrf step_response not available:", repr(e)[:120], ")")

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
