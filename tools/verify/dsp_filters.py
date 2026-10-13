#!/usr/bin/env python3
"""Verification for kb/14-sdr-dsp/digital-filters-fir-iir.md

Checks (PASS/FAIL):
 1. Kaiser window FIR: kaiserord length/beta formulas; achieved stop-band >= spec.
 2. FIR length estimates (Kaiser, Bellanger, harris A/(22 dF)) vs the true minimum
    Parks-McClellan (remez) length for several specs.
 3. Least-squares (firls) vs equiripple (remez): LS has lower stop-band energy, higher peak.
 4. Linear phase: symmetric FIR has constant group delay (N-1)/2.
 5. Bilinear transform with prewarping puts the -3 dB edge exactly where specified;
    without prewarping it is off by the tan() warp.
 6. IIR order comparison (Butterworth / Chebyshev I / II / elliptic) for one spec.
 7. Stability & coefficient quantisation: 16-bit direct-form (tf) high-order elliptic
    vs second-order sections (SOS).
 8. FIR coefficient quantisation: stop-band floor vs coefficient bits (~6 dB/bit).
 9. IIR group delay is not constant (Butterworth) — peak near the band edge.
10. Worked example: LoRa BW125 channel filter at 500 kS/s after decimation.
"""
import numpy as np
from scipy import signal

ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def fir_resp(h, fs, n=2 ** 16):
    w, H = signal.freqz(h, 1, worN=n, fs=fs)
    return w, 20 * np.log10(np.abs(H) + 1e-15)


def stop_att(h, fs, fstop):
    w, HdB = fir_resp(h, fs)
    return -HdB[w >= fstop].max()


def pass_ripple(h, fs, fpass):
    w, HdB = fir_resp(h, fs)
    band = HdB[w <= fpass]
    return band.max() - band.min()


# ------------------------------------------------------------ 1. Kaiser window FIR
fs = 1.0
fp, fst, A = 0.20, 0.25, 70.0
dF = fst - fp
N_k, beta = signal.kaiserord(A, dF / (fs / 2))  # width normalised to Nyquist
N_formula = int(np.ceil((A - 7.95) / (2.285 * 2 * np.pi * dF / fs))) + 1
beta_formula = 0.1102 * (A - 8.7)
check("kaiserord == Kaiser formulas", abs(N_k - N_formula) <= 1 and abs(beta - beta_formula) < 1e-9,
      f"N {N_k} vs {N_formula}, beta {beta:.3f}")
h = signal.firwin(N_k, (fp + fst) / 2, window=("kaiser", beta), fs=fs)
att = stop_att(h, fs, fst)
check("Kaiser-window FIR lands within 2 dB of spec (formula is approximate)", att > A - 2.0, f"{att:.1f} dB with N={N_k}")
# beta (not N) sets the sidelobe level, so the fix is to design for a small margin in A
N_m, beta_m = signal.kaiserord(A + 2, dF / (fs / 2))
h4 = signal.firwin(N_m, (fp + fst) / 2, window=("kaiser", beta_m), fs=fs)
check("designing for A+2 dB meets the spec", stop_att(h4, fs, fst) >= A, f"{stop_att(h4, fs, fst):.1f} dB with N={N_m}, beta={beta_m:.2f}")


# ------------------------------------------------------------ 2. length estimates vs remez minimum
def remez_min_len(fp, fst, rp_db, A, fs=1.0, nmax=1500):
    d1 = (10 ** (rp_db / 20) - 1) / (10 ** (rp_db / 20) + 1)
    d2 = 10 ** (-A / 20)
    for N in range(11, nmax, 2):  # odd lengths (type I)
        try:
            h = signal.remez(N, [0, fp, fst, fs / 2], [1, 0], weight=[1 / d1, 1 / d2], fs=fs, maxiter=100)
        except Exception:
            continue
        if stop_att(h, fs, fst) >= A and pass_ripple(h, fs, fp) <= rp_db * 1.001:
            return N, h
    return None, None


specs = [(0.20, 0.25, 0.1, 60), (0.10, 0.12, 0.1, 80), (0.40, 0.45, 0.5, 50), (0.05, 0.07, 0.05, 90)]
print("   spec (fp, fs_edge, ripple dB, A dB) | remez min | Kaiser-est(PM) | Bellanger | harris A/(22dF) | Kaiser-window N")
for fp_, fst_, rp, A_ in specs:
    dF = fst_ - fp_
    d1 = (10 ** (rp / 20) - 1) / (10 ** (rp / 20) + 1)
    d2 = 10 ** (-A_ / 20)
    Nmin, _ = remez_min_len(fp_, fst_, rp, A_)
    kaiser_pm = (-20 * np.log10(np.sqrt(d1 * d2)) - 13) / (14.6 * dF) + 1  # Kaiser's estimate for equiripple
    bell = 2 / 3 * np.log10(1 / (10 * d1 * d2)) / dF
    harris = A_ / (22 * dF)
    kw, _ = signal.kaiserord(A_, dF / 0.5)
    print(f"   ({fp_}, {fst_}, {rp}, {A_}) | {Nmin} | {kaiser_pm:.0f} | {bell:.0f} | {harris:.0f} | {kw}")
    check(f"PM-length estimates within 15 % of true min (spec {fp_}/{fst_}/{A_} dB)",
          abs(kaiser_pm - Nmin) / Nmin < 0.15 and abs(bell - Nmin) / Nmin < 0.15,
          f"true {Nmin}, Kaiser {kaiser_pm:.0f}, Bellanger {bell:.0f}")
    check(f"harris A/(22 dF) is a usable first guess (within 25 %)", abs(harris - Nmin) / Nmin < 0.25, f"{harris:.0f} vs {Nmin}")
    check(f"Kaiser-window design needs more taps than equiripple", kw >= Nmin, f"{kw} vs {Nmin}")

# ------------------------------------------------------------ 3. LS vs equiripple
N = 61
fp_, fst_ = 0.2, 0.25
h_pm = signal.remez(N, [0, fp_, fst_, 0.5], [1, 0], weight=[1, 10], fs=1)
h_ls = signal.firls(N, [0, fp_, fst_, 0.5], [1, 1, 0, 0], weight=[1, 10], fs=1)
w, Hpm = signal.freqz(h_pm, 1, worN=2 ** 15, fs=1)
_, Hls = signal.freqz(h_ls, 1, worN=2 ** 15, fs=1)
sb = w >= fst_
pb = w <= fp_
# LS minimises the TOTAL weighted squared error (passband + 10^2 x stop-band here)
e_pm = np.sum((np.abs(Hpm[pb]) - 1) ** 2) + 100 * np.sum(np.abs(Hpm[sb]) ** 2)
e_ls = np.sum((np.abs(Hls[pb]) - 1) ** 2) + 100 * np.sum(np.abs(Hls[sb]) ** 2)
pk_pm = 20 * np.log10(np.abs(Hpm[sb]).max())
pk_ls = 20 * np.log10(np.abs(Hls[sb]).max())
check("LS: lower total weighted squared error than equiripple", e_ls < e_pm, f"ratio {10*np.log10(e_ls/e_pm):.1f} dB")
check("equiripple: lower stop-band PEAK than LS", pk_pm < pk_ls, f"peak PM {pk_pm:.1f} dB vs LS {pk_ls:.1f} dB")

# ------------------------------------------------------------ 4. linear phase
w, gd = signal.group_delay((h_pm, 1), w=np.linspace(0.01, 0.19, 200), fs=1)
check("symmetric FIR: constant group delay (N-1)/2", np.allclose(gd, (N - 1) / 2, atol=1e-6), f"{gd.mean():.3f} samples")
check("taps symmetric", np.allclose(h_pm, h_pm[::-1]))

# ------------------------------------------------------------ 5. bilinear + prewarp
fs = 48e3
fc = 15e3  # a high edge so warping is significant
b, a = signal.butter(4, 2 * np.pi * fc, analog=True)
bz, az = signal.bilinear(b, a, fs=fs)  # no prewarp
Wc = 2 * fs * np.tan(np.pi * fc / fs)  # prewarped analog edge
b2, a2 = signal.butter(4, Wc, analog=True)
bz2, az2 = signal.bilinear(b2, a2, fs=fs)
f = np.linspace(1, fs / 2 - 1, 200000)
_, H1 = signal.freqz(bz, az, worN=f, fs=fs)
_, H2 = signal.freqz(bz2, az2, worN=f, fs=fs)
f3_1 = f[np.argmax(np.abs(H1) < 1 / np.sqrt(2))]
f3_2 = f[np.argmax(np.abs(H2) < 1 / np.sqrt(2))]
f_pred_nowarp = fs / np.pi * np.arctan(np.pi * fc / fs)
check("bilinear WITH prewarp: -3 dB at spec", abs(f3_2 - fc) < 5, f"{f3_2:.0f} Hz (spec {fc:.0f})")
check("bilinear WITHOUT prewarp: edge moves to (fs/pi)atan(pi fc/fs)", abs(f3_1 - f_pred_nowarp) < 5, f"{f3_1:.0f} Hz (pred {f_pred_nowarp:.0f})")
bd, ad = signal.butter(4, fc, fs=fs)  # scipy prewarps internally
_, H3 = signal.freqz(bd, ad, worN=f, fs=fs)
check("scipy.signal.butter(fs=...) prewarps automatically", abs(f[np.argmax(np.abs(H3) < 1 / np.sqrt(2))] - fc) < 5)

# ------------------------------------------------------------ 6. IIR orders
fs = 1.0
wp, ws, gpass, gstop = 0.20, 0.24, 0.5, 60
orders = {
    "Butterworth": signal.buttord(wp, ws, gpass, gstop, fs=fs)[0],
    "Chebyshev I": signal.cheb1ord(wp, ws, gpass, gstop, fs=fs)[0],
    "Chebyshev II": signal.cheb2ord(wp, ws, gpass, gstop, fs=fs)[0],
    "Elliptic": signal.ellipord(wp, ws, gpass, gstop, fs=fs)[0],
}
Nfir, _ = remez_min_len(wp, ws, gpass, gstop)
print("   IIR orders for passband 0.20, stopband 0.24 (x fs), 0.5 dB ripple, 60 dB:", orders, "| equiripple FIR length", Nfir)
check("order ranking: elliptic < Cheby < Butterworth", orders["Elliptic"] < orders["Chebyshev I"] < orders["Butterworth"])
# verify elliptic meets spec
sos = signal.ellip(orders["Elliptic"], gpass, gstop, wp, fs=fs, output="sos")
w, H = signal.sosfreqz(sos, worN=2 ** 15, fs=fs)
HdB = 20 * np.log10(np.abs(H) + 1e-15)
check("elliptic design meets spec", HdB[w >= ws].max() <= -gstop + 0.01 and HdB[w <= wp].min() >= -gpass - 0.01,
      f"stop {-HdB[w>=ws].max():.1f} dB, pass ripple {-HdB[w<=wp].min():.2f} dB")
mults_iir = 5 * len(sos)  # ~5 multiplies per biquad
check("multiply count: elliptic IIR << FIR", mults_iir < (Nfir + 1) / 2, f"IIR ~{mults_iir} mult/sample vs FIR {(Nfir+1)//2} (folded)")

# ------------------------------------------------------------ 7. quantisation: tf vs sos
sos = signal.ellip(10, 0.5, 80, 0.05, output="sos")  # narrow low-pass (edge 0.025 fs)
b, a = signal.sos2tf(sos)


def q(x, bits, maxabs=None):
    maxabs = maxabs or np.max(np.abs(x))
    scale = 2 ** (bits - 1) / (2 ** np.ceil(np.log2(maxabs)))
    return np.round(x * scale) / scale


bq, aq = q(b, 16), q(a, 16)
poles_q = np.roots(aq)
sosq = sos.copy()
sosq[:, :3] = np.array([q(r, 16, 2) for r in sos[:, :3]])
sosq[:, 3:] = np.array([q(r, 16, 2) for r in sos[:, 3:]])
poles_sos = np.concatenate([np.roots(r[3:]) for r in sosq])
unstable_tf = np.max(np.abs(poles_q)) >= 1
w, Hs = signal.sosfreqz(sos, worN=4096)
_, Hsq = signal.sosfreqz(sosq, worN=4096)
err_sos = np.max(np.abs(20 * np.log10(np.abs(Hsq[w < 0.04 * np.pi]) + 1e-12) - 20 * np.log10(np.abs(Hs[w < 0.04 * np.pi]) + 1e-12)))
print(f"      10th-order elliptic, 16-bit coeffs: direct-form max|pole| = {np.max(np.abs(poles_q)):.5f}; SOS max|pole| = {np.max(np.abs(poles_sos)):.5f}")
if not unstable_tf:
    _, Hq = signal.freqz(bq, aq, worN=4096)
    err_tf = np.max(np.abs(20 * np.log10(np.abs(Hq[w < 0.04 * np.pi]) + 1e-12) - 20 * np.log10(np.abs(Hs[w < 0.04 * np.pi]) + 1e-12)))
else:
    err_tf = np.inf
check("16-bit direct-form high-order IIR is broken (unstable or grossly wrong)", unstable_tf or err_tf > 3,
      f"unstable={unstable_tf}, passband err {err_tf:.1f} dB")
check("16-bit SOS version stays stable and accurate", np.max(np.abs(poles_sos)) < 1 and err_sos < 0.1, f"passband err {err_sos:.3f} dB")

# ------------------------------------------------------------ 8. FIR coefficient bits
N90, h90 = remez_min_len(0.1, 0.13, 0.1, 100)
print(f"      100 dB reference FIR: N={N90}")
res = []
for bits in (8, 10, 12, 14, 16, 18):
    hq = q(h90, bits)
    res.append((bits, stop_att(hq, 1.0, 0.13)))
print("      coefficient bits -> stop-band (dB):", [(b_, round(a_, 1)) for b_, a_ in res])
slope = np.polyfit([r[0] for r in res[:4]], [r[1] for r in res[:4]], 1)[0]
check("stop-band floor improves ~5-6 dB per coefficient bit until the design limit", 4.5 < slope < 7.0, f"{slope:.2f} dB/bit")

# ------------------------------------------------------------ 9. IIR group delay
b, a = signal.butter(6, 0.2, fs=1)
w, gd = signal.group_delay((b, a), w=np.linspace(0.001, 0.25, 2000), fs=1)
check("Butterworth group delay peaks near the band edge", 0.15 < w[np.argmax(gd)] < 0.21 and gd.max() > 1.5 * gd[0],
      f"DC {gd[0]:.1f} samples, peak {gd.max():.1f} at {w[np.argmax(gd)]:.3f} fs")

# ------------------------------------------------------------ 10. LoRa BW125 channel filter
fs = 500e3
fp_, fst_ = 62.5e3, 80e3
Nl, hl = remez_min_len(fp_ / fs, fst_ / fs, 0.1, 60)
check("LoRa BW125 channel filter @500 kS/s (62.5/80 kHz, 60 dB) feasible", Nl is not None and Nl < 120, f"N = {Nl} taps, delay {(Nl-1)/2/fs*1e6:.0f} us")
print(f"      harris estimate: {60/(22*(fst_-fp_)/fs):.0f} taps")

print("\nALL PASS" if ok_all else "\nSOME FAIL")
