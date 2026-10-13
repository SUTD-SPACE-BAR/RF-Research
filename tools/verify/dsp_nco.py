#!/usr/bin/env python3
"""Verification for kb/14-sdr-dsp/nco-ddc-duc.md

Checks (PASS/FAIL):
 1. Phase-accumulator NCO: f = FTW fs / 2^N; resolution; worst-case frequency error fs/2^(N+1).
 2. Phase-truncation spurs: worst-case SFDR vs number of phase bits P (the ~6.02 dB/bit rule),
    measured by simulation with a worst-case tuning word.
 3. Amplitude (LUT word) quantisation: SNR ~ 6.02 A + 1.76 dB.
 4. Phase dithering converts truncation spurs into noise (SFDR improves, floor rises).
 5. Quarter-wave LUT symmetry reproduces the full sine exactly.
 6. CORDIC rotation mode: gain K = prod sqrt(1+2^-2i) -> 1.64676; ~1 bit (6 dB) per iteration.
 7. Direct-sampling DDC chain (real 64 MS/s ADC -> NCO -> CIC(R=64,N=5) -> 121-tap compensating FIR /4 -> 250 kS/s):
    wanted tone lands at the right offset; a strong out-of-band tone is rejected.
 8. DUC: complex baseband -> interpolate -> NCO -> real DAC: single sideband, no image.
 9. Phase-continuous FSK from an NCO: no phase jumps at symbol boundaries.
10. ppm correction example numbers.
"""
import numpy as np
from scipy import signal

rng = np.random.default_rng(5)
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def sfdr_db(x, exclude_bins=3):
    N = len(x)
    X = np.abs(np.fft.fft(x * signal.windows.blackmanharris(N, sym=False))) ** 2
    k0 = np.argmax(X)
    Xs = X.copy()
    for d in range(-exclude_bins, exclude_bins + 1):
        Xs[(k0 + d) % N] = 0
    return 10 * np.log10(X[k0] / Xs.max())


# ------------------------------------------------------------ 1. accumulator basics
for Nacc, fs in [(32, 61.44e6), (48, 5e9), (24, 28.8e6)]:
    res = fs / 2 ** Nacc
    print(f"      {Nacc}-bit accumulator at {fs/1e6:g} MHz: resolution {res:.3g} Hz")
fs = 61.44e6
Nacc = 32
f_want = 12.3456789e6
ftw = round(f_want / fs * 2 ** Nacc)
f_act = ftw * fs / 2 ** Nacc
check("FTW rounding error <= fs/2^(N+1)", abs(f_act - f_want) <= fs / 2 ** (Nacc + 1), f"error {abs(f_act-f_want)*1e3:.3f} mHz (bound {fs/2**(Nacc+1)*1e3:.3f} mHz)")


# ------------------------------------------------------------ 2. phase truncation spurs
def nco(ftw, Nacc, P, A=None, n=2 ** 16, dither=False):
    acc = (np.arange(n, dtype=np.int64) * ftw) % (1 << Nacc)
    if dither:
        acc = (acc + rng.integers(0, 1 << (Nacc - P), n)) % (1 << Nacc)
    ph = acc >> (Nacc - P)  # truncate to P bits
    theta = 2 * np.pi * ph / 2 ** P
    y = np.exp(1j * theta)
    if A is not None:
        s = 2 ** (A - 1) - 1
        y = (np.round(np.real(y) * s) + 1j * np.round(np.imag(y) * s)) / s
    return y


Nacc = 24
rows = []
for P in (6, 8, 10, 12):
    # worst case: the truncated fraction has the longest period with largest error ->
    # tuning word whose discarded bits = 2^(Nacc-P-1)+... choose ftw with LSB pattern 1 at bit (Nacc-P-1)
    ftw = (1 << (Nacc - P - 1)) + (37 << (Nacc - P))  # frac part = 1/2 LSB of the P-bit phase
    n = 2 ** 16
    s_w = sfdr_db(nco(ftw, Nacc, P, n=n))
    # a "typical" random tuning word
    s_r = np.median([sfdr_db(nco(int(rng.integers(1, 1 << (Nacc - 2))) | 1, Nacc, P, n=n)) for _ in range(5)])
    rows.append((P, s_w, s_r))
    print(f"      P={P:2d} phase bits: worst-case-type FTW SFDR {s_w:6.2f} dB; random odd FTW median {s_r:6.2f} dB; 6.02P = {6.02*P:6.2f}")
slope = np.polyfit([r[0] for r in rows], [r[1] for r in rows], 1)[0]
check("phase-truncation SFDR grows ~6.02 dB per phase bit", abs(slope - 6.02) < 0.3, f"fitted slope {slope:.2f} dB/bit")
# Finding: the worst case is 6.02P - 3.92 dB (3.92 dB = -20log10 sinc(1/2)), i.e. Nicholas & Samueli's
# result; the popular "6.02 dB per bit" figure is the typical (random tuning word) value.
check("worst-case phase-truncation SFDR = 6.02P - 3.92 dB", all(abs(r[1] - (6.02 * r[0] - 3.92)) < 0.1 for r in rows),
      " / ".join(f"P={r[0]}: {r[1]:.2f} vs {6.02*r[0]-3.92:.2f}" for r in rows))
check("typical (random FTW) SFDR ~ 6.02P dB", all(abs(r[2] - 6.02 * r[0]) < 0.5 for r in rows))
check("random tuning words are no worse than worst case", all(r[2] >= r[1] - 0.5 for r in rows))
# Nicholas & Samueli modification: force the accumulator LSB to 1 (odd FTW) -> worst case becomes 6.02P
mod = []
for P in (8, 10, 12):
    ftw = ((1 << (Nacc - P - 1)) + (37 << (Nacc - P))) | 1
    mod.append((P, sfdr_db(nco(ftw, Nacc, P, n=2 ** 18))))
check("odd-FTW (Nicholas-Samueli) modification: worst case -> 6.02P dB", all(abs(v_ - 6.02 * P_) < 0.3 for P_, v_ in mod),
      " / ".join(f"P={P_}: {v_:.2f}" for P_, v_ in mod))

# ------------------------------------------------------------ 3. amplitude quantisation
for A in (8, 12, 16):
    y = nco(int(0.1234567 * 2 ** 32) | 1, 32, 20, A=A, n=2 ** 16)
    ideal = np.exp(1j * 2 * np.pi * (((np.arange(2 ** 16, dtype=np.int64) * (int(0.1234567 * 2 ** 32) | 1)) % (1 << 32)) >> 12) / 2 ** 20)
    snr = 10 * np.log10(np.mean(np.abs(ideal) ** 2) / np.mean(np.abs(y - ideal) ** 2))
    # complex: noise on both I and Q, signal power 1 (amplitude 1 on each) -> 6.02A+1.76 per rail
    check(f"{A}-bit LUT amplitude SNR ~ 6.02A+1.76", abs(snr - (6.02 * A + 1.76)) < 1.0, f"{snr:.2f} vs {6.02*A+1.76:.2f} dB")

# ------------------------------------------------------------ 4. dithering
P = 10
ftw = (1 << (Nacc - P - 1)) + (37 << (Nacc - P))
s_plain = sfdr_db(nco(ftw, Nacc, P, n=2 ** 16))
s_dith = sfdr_db(nco(ftw, Nacc, P, n=2 ** 16, dither=True))
check("phase dither improves SFDR (spurs -> noise)", s_dith > s_plain + 10, f"{s_plain:.1f} dB -> {s_dith:.1f} dB (P=10)")

# ------------------------------------------------------------ 5. quarter-wave LUT
P = 10
Q = 2 ** (P - 2)
lut = np.sin(2 * np.pi * (np.arange(Q) + 0.5) / 2 ** P)  # half-LSB offset makes symmetry exact


def sin_qw(ph):
    quad = ph >> (P - 2)
    idx = ph & (Q - 1)
    v = np.where(quad % 2 == 0, lut[idx], lut[Q - 1 - idx])
    return np.where(quad < 2, v, -v)


ph = np.arange(2 ** P)
full = np.sin(2 * np.pi * (ph + 0.5) / 2 ** P)
check("quarter-wave LUT (1/4 memory) reproduces full sine", np.allclose(sin_qw(ph), full))


# ------------------------------------------------------------ 6. CORDIC
def cordic_rotate(theta, n_iter):
    """Rotation mode, |theta| <= pi/2. Returns (cos, sin) with gain removed."""
    x, y, z = 1.0, 0.0, theta
    for i in range(n_iter):
        d = 1.0 if z >= 0 else -1.0
        x, y = x - d * y * 2 ** -i, y + d * x * 2 ** -i
        z -= d * np.arctan(2 ** -i)
    K = np.prod([np.sqrt(1 + 2 ** (-2 * i)) for i in range(n_iter)])
    return x / K, y / K, K


_, _, K = cordic_rotate(0.3, 30)
check("CORDIC gain -> 1.64676", abs(K - 1.646760258) < 1e-8, f"K = {K:.9f}")
errs = []
thetas = rng.uniform(-np.pi / 2, np.pi / 2, 400)
for n_it in (8, 12, 16, 20):
    e = max(max(abs(cordic_rotate(t, n_it)[0] - np.cos(t)), abs(cordic_rotate(t, n_it)[1] - np.sin(t))) for t in thetas)
    errs.append((n_it, e))
print("      CORDIC max error vs iterations:", [(n_, f"{e:.1e}") for n_, e in errs])
sl = -np.polyfit([e[0] for e in errs], [20 * np.log10(e[1]) for e in errs], 1)[0]
check("CORDIC accuracy ~6 dB (1 bit) per iteration", 5.0 < sl < 7.0, f"{sl:.2f} dB/iteration")

# ------------------------------------------------------------ 7. direct-sampling DDC
fs = 64e6
Ns = 2 ** 21
n = np.arange(Ns)
f_nco = 7.1e6  # tune to 40 m band
f_sig = 7.1e6 + 12e3  # wanted CW 12 kHz above
f_blk = 7.1e6 + 600e3  # strong out-of-channel signal (+40 dB)
adc = 1e-3 * np.cos(2 * np.pi * f_sig * n / fs) + 1e-1 * np.cos(2 * np.pi * f_blk * n / fs)
adc_i = np.round(adc * 2 ** 15).astype(np.int64)  # 16-bit ADC codes
ftw = round(f_nco / fs * 2 ** 32)
acc = (n.astype(np.int64) * ftw) % (1 << 32)
theta = 2 * np.pi * (acc >> 12) / 2 ** 20  # 20-bit phase to LUT
lo_i = np.round(np.cos(theta) * (2 ** 15 - 1)).astype(np.int64)  # 16-bit LUT, cos (I)
lo_q = -np.round(np.sin(theta) * (2 ** 15 - 1)).astype(np.int64)  # e^{-j theta} (Q)
bb_i = adc_i * lo_i  # 31-bit products
bb_q = adc_i * lo_q
R, Nst = 64, 5


def cic_int(v, R, Nst):
    """Bit-true integer CIC; numpy int64 arithmetic wraps modulo 2^64 (allowed, Hogenauer).
    Register need: 31 + 5*log2(64) = 61 bits < 64."""
    v = v.astype(np.int64)
    for _ in range(Nst):
        v = np.cumsum(v, dtype=np.int64)
    v = v[R - 1::R]
    for _ in range(Nst):
        v = v - np.concatenate([np.zeros(1, dtype=np.int64), v[:-1]])
    return v


with np.errstate(over="ignore"):
    vi = cic_int(bb_i, R, Nst)
    vq = cic_int(bb_q, R, Nst)
scale = (R ** Nst) * 2.0 ** 15 * (2 ** 15 - 1)
v = (vi + 1j * vq) / scale
# pitfall demo: the same CIC with float64 cumsum over 2^21 samples
vf = (adc_i * np.exp(-1j * theta)).astype(complex)
for _ in range(Nst):
    vf = np.cumsum(vf)
vf = vf[R - 1::R]
for _ in range(Nst):
    vf = vf - np.concatenate([np.zeros(1), vf[:-1]])
vf = vf / (R ** Nst * 2.0 ** 15)
err_float = np.max(np.abs(vf[100:] - v[100:])) / np.max(np.abs(v[100:]))
check("float64-cumsum CIC over 2^21 samples is badly wrong (why CICs are integer)", err_float > 1e-4, f"relative error {err_float:.1e}")
fs1 = fs / R  # 1 MS/s
# droop-compensating FIR (least squares): pass-band 1/|sinc|^5 to 100 kHz, stop-band from 150 kHz
# (= fs2 - 100 kHz, alias protection for the /4 that follows), 121 taps -> ~104 dB stop-band
grid = np.linspace(0, 100e3, 21)
bands_f, des_f = [], []
for i in range(len(grid) - 1):
    bands_f += [grid[i], grid[i + 1]]
    des_f += [1 / np.abs(np.sinc(grid[i] / fs1)) ** Nst, 1 / np.abs(np.sinc(grid[i + 1] / fs1)) ** Nst]
bands_f += [150e3, fs1 / 2]
des_f += [0, 0]
hc = signal.firls(121, bands_f, des_f, weight=[1] * (len(grid) - 1) + [3000], fs=fs1)
y = signal.lfilter(hc, 1, v)[::4]
fs2 = fs1 / 4
y = y[200:]
N2 = len(y)
w = signal.windows.flattop(N2, sym=False)


def lvl(x, f, fs_):
    nn = np.arange(len(x))
    return 20 * np.log10(np.abs(np.sum(x * w * np.exp(-2j * np.pi * f * nn / fs_))) / w.sum() + 1e-300)


l_sig = lvl(y, 12e3, fs2)
exp_sig = 20 * np.log10(0.5e-3)  # real cos amplitude 1e-3 -> complex 0.5e-3
f_blk_alias = ((600e3 + fs2 / 2) % fs2) - fs2 / 2
l_blk = lvl(y, f_blk_alias, fs2) - 20 * np.log10(0.05)
check("DDC: wanted CW at +12 kHz, correct level", abs(l_sig - exp_sig) < 0.3, f"{l_sig:.2f} dB (expected {exp_sig:.2f}); output {fs2/1e3:.0f} kS/s")
wv, Hc_ = signal.freqz(hc, 1, worN=np.array([12e3, 90e3]), fs=fs1)
flat = 20 * np.log10(np.abs(Hc_) * np.abs(np.sinc(np.array([12e3, 90e3]) / fs1)) ** Nst)
check("CIC + compensator pass-band flat (12 vs 90 kHz)", abs(flat[0] - flat[1]) < 0.05, f"{flat[0]-flat[1]:+.3f} dB (uncompensated droop at 90 kHz: {-20*Nst*np.log10(np.sinc(0.09)):.2f} dB)")
check("DDC (bit-true integer CIC): +40 dB blocker 600 kHz away rejected > 90 dB", l_blk < -90, f"{l_blk:.1f} dB rel. its input level (aliases to {f_blk_alias/1e3:.0f} kHz)")

# ------------------------------------------------------------ 8. DUC single sideband
fsb = 1e6
L = 16
fsd = fsb * L
nb = np.arange(16384)
xb = np.exp(2j * np.pi * 50e3 * nb / fsb)
up = np.zeros(len(xb) * L, dtype=complex)
up[::L] = xb
hi = L * signal.remez(255, [0, 100e3, 400e3, fsd / 2], [1, 0], weight=[1, 30], fs=fsd)
xi = signal.lfilter(hi, 1, up)[1000:]
nd = np.arange(len(xi))
f_c = 3e6
dac = np.real(xi * np.exp(2j * np.pi * f_c * nd / fsd))
wd = signal.windows.flattop(len(dac), sym=False)
L_usb = 20 * np.log10(np.abs(np.sum(dac * wd * np.exp(-2j * np.pi * (f_c + 50e3) * nd / fsd))) / wd.sum())
L_lsb = 20 * np.log10(np.abs(np.sum(dac * wd * np.exp(-2j * np.pi * (f_c - 50e3) * nd / fsd))) / wd.sum() + 1e-300)
check("DUC: +50 kHz baseband tone appears only at fc+50 kHz", L_usb > -6.1 and L_lsb < L_usb - 80, f"USB {L_usb:.2f} dB, LSB {L_lsb:.1f} dB")

# ------------------------------------------------------------ 9. phase-continuous FSK
fs = 1e6
sps = 100
bits = rng.integers(0, 2, 200)
dev = 4.8e3
freqs = np.repeat(np.where(bits == 1, dev, -dev), sps)
ftws = np.round(freqs / fs * 2 ** 32).astype(np.int64)
acc = np.cumsum(ftws) % (1 << 32)
ph = 2 * np.pi * acc / 2 ** 32
dph = np.angle(np.exp(1j * np.diff(ph)))
check("NCO-generated FSK is phase-continuous (max phase step = 2 pi f_max/fs)", np.max(np.abs(dph)) <= 2 * np.pi * dev / fs * 1.0001,
      f"max step {np.max(np.abs(dph)):.4f} rad")

# ------------------------------------------------------------ 10. ppm correction
f_c = 433.92e6
for ppm in (-12.5, 1.0):
    print(f"      {ppm:+} ppm at 433.92 MHz -> retune NCO by {-f_c*ppm*1e-6:+.1f} Hz")
check("12.5 ppm at 433.92 MHz = 5424 Hz", abs(f_c * 12.5e-6 - 5424) < 1)

print("\nALL PASS" if ok_all else "\nSOME FAIL")
