#!/usr/bin/env python3
"""Verification for kb/14-sdr-dsp/multirate-dsp-decimation-cic.md

Checks (PASS/FAIL):
 1. Decimation without filtering aliases; with an anti-alias FIR it does not.
 2. Polyphase decimator == filter-then-downsample (noble identity), M x fewer MACs.
 3. Interpolation: zero-stuffing creates L-1 images; interpolation filter (gain L) removes them.
 4. Half-band FIR: every other tap zero, centre tap 1/2, response symmetric about fs/4.
 5. CIC: bit-exact integer implementation (with two's-complement WRAP in the integrators)
    equals the exact result and the formula |sin(pi f R M)/sin(pi f)|^N; gain (RM)^N;
    register growth N log2(RM) bits (Hogenauer 1981).
 6. CIC droop and alias rejection numbers (N=4, M=1).
 7. CIC droop compensation FIR flattens the pass-band.
 8. Worked chain: LoRa BW125 at 433.92 MHz with an RTL-SDR:
      (a) 2.0 MS/s, offset tune, single /4 FIR (alias-protect only) + 83-tap channel filter
      (b) 2.4 MS/s, rational resampler 5/24 -> 500 kS/s
    alias rejection measured with test tones; MAC/s compared with a brute-force filter.
 9. fs/4 real-to-complex conversion (1,-j,-1,j mixing + half-band + /2) == ideal.
10. Critically-sampled polyphase FFT channeliser (M=8): tone in channel k appears in output k.
"""
import numpy as np
from scipy import signal

rng = np.random.default_rng(11)
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def tone_level_db(x, f, fs):
    """Amplitude (dB re 1) of complex tone at f in x, flat-top windowed."""
    N = len(x)
    w = signal.windows.flattop(N, sym=False)
    n = np.arange(N)
    return 20 * np.log10(np.abs(np.sum(x * w * np.exp(-2j * np.pi * f * n / fs))) / w.sum() + 1e-300)


# ------------------------------------------------------------ 1. decimation aliasing
fs = 1e6
M = 4
N = 2 ** 16
n = np.arange(N)
f_int = 300e3  # above fs/(2M)=125 kHz -> aliases to 300-250 = +50 kHz at 250 kS/s
x = np.exp(2j * np.pi * f_int * n / fs)
y_bad = x[::M]
alias_f = ((f_int + fs / M / 2) % (fs / M)) - fs / M / 2
lvl_bad = tone_level_db(y_bad, alias_f, fs / M)
h = signal.remez(63, [0, 100e3, 150e3, fs / 2], [1, 0], weight=[1, 30], fs=fs)
y_good = signal.lfilter(h, 1, x)[::M]
lvl_good = tone_level_db(y_good[100:], alias_f, fs / M)
check("unfiltered /4 decimation: 300 kHz tone aliases at full level", lvl_bad > -0.1, f"alias at {alias_f/1e3:.0f} kHz, {lvl_bad:.1f} dB")
check("with anti-alias FIR the alias is suppressed", lvl_good < -55, f"{lvl_good:.1f} dB")

# ------------------------------------------------------------ 2. polyphase decimator
xr = rng.standard_normal(4000) + 1j * rng.standard_normal(4000)
ref = signal.lfilter(h, 1, xr)[::M]
# polyphase: E_k[m] = h[mM+k]; y[m] = sum_k (E_k * x_k)[m], x_k[m] = x[mM-k]
L = int(np.ceil(len(h) / M)) * M
hp = np.concatenate([h, np.zeros(L - len(h))])
out = np.zeros(len(ref), dtype=complex)
for k in range(M):
    ek = hp[k::M]
    xk = np.concatenate([np.zeros(k), xr])[: len(xr)][::M]  # x[mM - k]
    out += signal.lfilter(ek, 1, xk)[: len(ref)]
check("polyphase decimator == filter-then-downsample", np.allclose(out, ref), f"max err {np.max(np.abs(out-ref)):.1e}")
print(f"      MACs per output: direct {len(h)*M} (computes discarded outputs) vs polyphase {len(h)}")

# ------------------------------------------------------------ 3. interpolation images
Lx = 4
fs_in = 250e3
xin = np.exp(2j * np.pi * 40e3 * np.arange(8192) / fs_in)
up = np.zeros(len(xin) * Lx, dtype=complex)
up[::Lx] = xin
fs_up = fs_in * Lx
imgs = [tone_level_db(up, 40e3 + k * fs_in, fs_up) for k in range(1, Lx)]
check("zero-stuffing x4 creates 3 equal images", all(abs(i - imgs[0]) < 0.1 for i in imgs), f"images at {[round(i,1) for i in imgs]} dB (re original -12 dB each)")
hi = Lx * signal.remez(95, [0, 100e3, 150e3, fs_up / 2], [1, 0], weight=[1, 30], fs=fs_up)
yi = signal.lfilter(hi, 1, up)[200:]
lv_main = tone_level_db(yi, 40e3, fs_up)
lv_img = max(tone_level_db(yi, 40e3 + k * fs_in, fs_up) for k in range(1, Lx))
check("interpolation filter with gain L restores level and removes images", abs(lv_main) < 0.2 and lv_img < -55, f"main {lv_main:.2f} dB, worst image {lv_img:.1f} dB")

# ------------------------------------------------------------ 4. half-band
fp_hb = 0.2  # passband edge (x fs); stop-band from 0.3 -> symmetric about 0.25
hb = signal.remez(31, [0, fp_hb, 0.5 - fp_hb, 0.5], [1, 0], fs=1)
c = len(hb) // 2
odd_off = hb[c + 2::2]  # taps at even distance from centre (>0)
check("half-band: taps at even offsets from centre ~ 0", np.max(np.abs(odd_off)) < 1e-4, f"max {np.max(np.abs(odd_off)):.1e}")
check("half-band: centre tap = 1/2", abs(hb[c] - 0.5) < 1e-4, f"{hb[c]:.5f}")
fq = np.array([0.05, 0.1, 0.15])
_, H1 = signal.freqz(hb, 1, worN=fq, fs=1)
_, H2 = signal.freqz(hb, 1, worN=0.5 - fq, fs=1)
A1 = np.real(H1 * np.exp(2j * np.pi * fq * c))  # zero-phase (signed) amplitude
A2 = np.real(H2 * np.exp(2j * np.pi * (0.5 - fq) * c))
check("half-band: A(f) + A(0.5-f) = 1 (zero-phase amplitude symmetric about fs/4)",
      np.allclose(A1 + A2, 1, atol=1e-4), f"sums {np.round(A1+A2, 6)}")
nz = np.sum(np.abs(hb) > 1e-4)
print(f"      31-tap half-band has {nz} non-zero taps ({(nz+1)//2} multiplies/output with symmetry, centre tap is a shift)")


# ------------------------------------------------------------ 5. CIC bit-exact
def cic_decimate_int(x, R, Mdiff, Nst, Bout):
    """Integer CIC with Bout-bit two's-complement wrap in every register."""
    mod = 1 << Bout

    def wrap(v):
        v = v % mod
        return np.where(v >= mod // 2, v - mod, v)

    v = x.astype(object)
    for _ in range(Nst):  # integrators at input rate
        acc = 0
        out = []
        for s_ in v:
            acc = int(wrap(np.array([acc + int(s_)], dtype=object))[0])
            out.append(acc)
        v = np.array(out, dtype=object)
    v = v[R - 1::R]  # decimate
    for _ in range(Nst):  # combs at output rate
        d = np.concatenate([np.zeros(Mdiff, dtype=object), v[:-Mdiff]])
        v = np.array([int(wrap(np.array([int(a) - int(b)], dtype=object))[0]) for a, b in zip(v, d)], dtype=object)
    return np.array(v, dtype=np.int64)


R, Md, Ns = 8, 1, 4
Bin = 12
Bgrow = int(np.ceil(Ns * np.log2(R * Md)))
Bout = Bin + Bgrow
xin = rng.integers(-(2 ** (Bin - 1)), 2 ** (Bin - 1), 3000)
y_int = cic_decimate_int(xin, R, Md, Ns, Bout)
# exact reference: convolve with boxcar^N then decimate, in float64 (exact for these sizes)
box = np.ones(R * Md)
hcic = box
for _ in range(Ns - 1):
    hcic = np.convolve(hcic, box)
y_ref = np.convolve(xin.astype(float), hcic)[: len(xin)][R - 1::R]
check("integer CIC with wrap-around == exact result", np.array_equal(y_int[5:], y_ref[5:len(y_int)].astype(np.int64)),
      f"register width {Bout} bits = {Bin} + N log2(RM) = {Bin}+{Bgrow}")
check("CIC DC gain = (RM)^N", abs(hcic.sum() - (R * Md) ** Ns) < 1e-9, f"{int(hcic.sum())}")
# too few bits -> wrong
y_short = cic_decimate_int(xin, R, Md, Ns, Bout - 2)
check("with 2 bits fewer the output is wrong", not np.array_equal(y_short[5:], y_ref[5:len(y_short)].astype(np.int64)))
# formula vs freqz of equivalent FIR
f = np.linspace(1e-4, 0.5, 2000)
_, Hc = signal.freqz(hcic, 1, worN=f, fs=1)
Hf = np.abs(np.sin(np.pi * f * R * Md) / np.sin(np.pi * f)) ** Ns
check("CIC magnitude = |sin(pi f RM)/sin(pi f)|^N", np.allclose(np.abs(Hc), Hf, rtol=1e-6, atol=1e-6))

# ------------------------------------------------------------ 6. droop and alias rejection
def cic_resp_out(nu, R, Md, Ns):
    """Normalised CIC response at output-rate frequency nu (cycles/output sample)."""
    f_in = nu / R
    return np.abs(np.sin(np.pi * f_in * R * Md) / (R * Md * np.sin(np.pi * f_in))) ** Ns


for nu_p in (0.125, 0.25):
    droop = -20 * np.log10(cic_resp_out(nu_p, 64, 1, 4))
    alias = -20 * np.log10(cic_resp_out(1 - nu_p, 64, 1, 4))
    print(f"      N=4,M=1,R=64: passband edge {nu_p} fs_out: droop {droop:.2f} dB, first-alias rejection {alias:.1f} dB")
d125 = -20 * np.log10(cic_resp_out(0.125, 64, 1, 4))
a125 = -20 * np.log10(cic_resp_out(0.875, 64, 1, 4))
check("N=4 CIC, band fs_out/8: droop 0.90 dB, alias rejection ~68 dB", abs(d125 - 0.90) < 0.02 and abs(a125 - 68.5) < 0.5, f"{d125:.2f} dB / {a125:.1f} dB")
sinc_approx = -20 * np.log10(np.abs(np.sinc(0.125)) ** 4)
check("large-R approximation |sinc(M nu)|^N", abs(sinc_approx - d125) < 0.01)

# ------------------------------------------------------------ 7. droop compensation
Rc, Nc = 16, 4
nu = np.linspace(0, 0.5, 512)
target = np.ones_like(nu)
pb = nu <= 0.2
droop_c = cic_resp_out(np.maximum(nu, 1e-9), Rc, 1, Nc)
des = np.where(pb, 1 / droop_c, 0)
# frequency-sampling least-squares compensator (at output rate)
Ncomp = 31
bands, desired = [], []
grid = np.linspace(0, 0.2, 40)
bands_f = []
for i in range(len(grid) - 1):
    bands_f += [grid[i], grid[i + 1]]
    desired += [1 / cic_resp_out(max(grid[i], 1e-9), Rc, 1, Nc), 1 / cic_resp_out(grid[i + 1], Rc, 1, Nc)]
bands_f += [0.3, 0.5]
desired += [0, 0]
hcomp = signal.firls(Ncomp, bands_f, desired, fs=1)
wv, Hcomp = signal.freqz(hcomp, 1, worN=nu[pb], fs=1)
total = np.abs(Hcomp) * cic_resp_out(np.maximum(nu[pb], 1e-9), Rc, 1, Nc)
ripple_before = -20 * np.log10(cic_resp_out(0.2, Rc, 1, Nc))
ripple_after = 20 * np.log10(total.max() / total.min())
check("31-tap compensator flattens N=4 CIC pass-band (0-0.2 fs_out)", ripple_after < 0.1, f"droop {ripple_before:.2f} dB -> ripple {ripple_after:.3f} dB")

# ------------------------------------------------------------ 8. LoRa chain on RTL-SDR
print("\n-- LoRa BW125 at 433.92 MHz on an RTL-SDR")
fs_a = 2.0e6
f_off = 400e3  # offset tuning: channel at +400 kHz
Ns_ = 2 ** 17
n = np.arange(Ns_)
# decimator only needs to protect 0..+-80 kHz after /4 (alias band starts at 500k-80k = 420 kHz)
M1 = 4
fs_b = fs_a / M1
hd = signal.remez(23, [0, 80e3, 420e3, fs_a / 2], [1, 0], weight=[1, 20], fs=fs_a)
att_d = -20 * np.log10(np.max(np.abs(signal.freqz(hd, 1, worN=np.linspace(420e3, 1e6, 2000), fs=fs_a)[1])))
hch = signal.remez(83, [0, 62.5e3, 80e3, fs_b / 2], [1, 0], weight=[1, 1 / (10 ** (-60 / 20)) * ((10 ** (0.1 / 20) - 1) / (10 ** (0.1 / 20) + 1))], fs=fs_b)
# test: wanted chirp-like wideband band + interferers that would alias
want = signal.lfilter(signal.firwin(301, 60e3, fs=fs_a), 1, rng.standard_normal(Ns_) + 1j * rng.standard_normal(Ns_))
want = want / np.std(want) * np.exp(2j * np.pi * f_off * n / fs_a)
interf_f = [f_off + 450e3, f_off - 520e3, f_off + 300e3]  # land (after shift & /4) near the channel
# leakage is measured on the interferers alone (the wanted band would otherwise add to the
# in-channel tone measurement); the wanted band is run separately to check it passes intact
xi = sum(10 * np.exp(2j * np.pi * fi * n / fs_a) for fi in interf_f)  # +20 dB interferers
bb = xi * np.exp(-2j * np.pi * f_off * n / fs_a)
y1 = signal.lfilter(hd, 1, bb)[::M1]
y2 = signal.lfilter(hch, 1, y1)[200:]
yw = signal.lfilter(hch, 1, signal.lfilter(hd, 1, want * np.exp(-2j * np.pi * f_off * n / fs_a))[::M1])[200:]
p_w = np.mean(np.abs(yw) ** 2)
check("chain (a): wanted 120 kHz-wide band passes with < 0.2 dB loss", abs(10 * np.log10(p_w)) < 0.2, f"{10*np.log10(p_w):+.2f} dB")
worst = -np.inf
for fi in interf_f:
    fa = ((fi - f_off + fs_b / 2) % fs_b) - fs_b / 2
    worst = max(worst, tone_level_db(y2, fa, fs_b) - 20)  # relative to the interferer's input level (+20 dB)
check("chain (a): interferers (two alias INTO the channel) suppressed >= 60 dB", worst < -60, f"worst {worst:.1f} dB rel. input interferer; /4 FIR stop-band {att_d:.1f} dB with 23 taps")
mac_a = len(hd) * fs_b + len(hch) * fs_b  # polyphase: taps per output sample x output rate
mac_brute = 374 * 2.4e6
print(f"      MAC/s (a): {mac_a/1e6:.1f} M per rail  vs brute-force 374-tap filter at 2.4 MS/s: {mac_brute/1e6:.0f} M")
check("multistage chain is >= 10x cheaper than brute force", mac_brute / mac_a > 10, f"{mac_brute/mac_a:.0f}x")

# (b) 2.4 MS/s -> 500 kS/s rational 5/24 with resample_poly
fs_c = 2.4e6
Nc_ = 240000
n = np.arange(Nc_)
tone_f = 50e3
x = np.exp(2j * np.pi * (f_off + tone_f) * n / fs_c) + 10 * np.exp(2j * np.pi * (f_off + 700e3) * n / fs_c)
bb = x * np.exp(-2j * np.pi * f_off * n / fs_c)
y = signal.resample_poly(bb, 5, 24, window=("kaiser", 9.0))
lv_t = tone_level_db(y[500:-500], tone_f, 500e3)
fa = ((700e3 + 250e3) % 500e3) - 250e3
lv_i = tone_level_db(y[500:-500], fa, 500e3) - 20
check("chain (b): resample_poly 5/24 keeps wanted tone, rejects 700 kHz interferer", abs(lv_t) < 0.1 and lv_i < -60,
      f"tone {lv_t:.2f} dB; interferer alias at {fa/1e3:.0f} kHz {lv_i:.1f} dB")

# ------------------------------------------------------------ 9. fs/4 real -> complex
fs = 4e6
Nr = 2 ** 15
n = np.arange(Nr)
f_if = fs / 4  # real IF at fs/4 carrying a complex baseband tone at +100 kHz
bbt = np.exp(2j * np.pi * 100e3 * n / fs)
real_if = np.real(bbt * np.exp(2j * np.pi * f_if * n / fs))
mix = real_if * np.array([1, -1j, -1, 1j])[n % 4]  # multiplier-free e^{-j pi n/2}
hb2 = signal.remez(47, [0, 0.2, 0.3, 0.5], [1, 0], weight=[1, 10], fs=1) * 2  # gain 2 restores amplitude
yc = signal.lfilter(hb2, 1, mix)[::2]
lv = tone_level_db(yc[100:], 100e3, fs / 2)
lv_img = tone_level_db(yc[100:], -100e3, fs / 2)
check("fs/4 mixing (1,-j,-1,j) + half-band /2 recovers complex baseband", abs(lv) < 0.1 and lv_img < -50, f"tone {lv:.2f} dB, image {lv_img:.1f} dB")

# ------------------------------------------------------------ 10. PFB channeliser
Mch = 8
fs = 1.0
P = 12  # taps per branch
proto = signal.firwin(Mch * P, 0.5 / Mch * 1.0, window=("kaiser", 9), fs=1) * Mch
Ntot = Mch * 4096
n = np.arange(Ntot)
test_ch = 3
x = np.exp(2j * np.pi * (test_ch / Mch + 0.2 / Mch) * n)  # tone inside channel 3
# critically sampled analysis PFB, derived from y_k[m] = sum_n h[n] x[mM-n] e^{+j2pi k n/M}:
# with n = pM+q:  y_k[m] = sum_q e^{j2pi kq/M} (E_q * x_q)[m],  E_q[p] = h[pM+q],  x_q[m] = x[mM-q]
# i.e. commutate, filter each branch with its polyphase component, then an M-point IDFT (xM).
v = []
for q_ in range(Mch):
    xq = np.concatenate([np.zeros(q_, dtype=complex), x])[: len(x)][::Mch]
    v.append(signal.lfilter(proto[q_::Mch], 1, xq))
v = np.array(v)
Y = np.fft.ifft(v, axis=0) * Mch  # row k = channel centred at k/M
# reference: brute-force mix-filter-decimate for channel test_ch
yref = signal.lfilter(proto, 1, x * np.exp(-2j * np.pi * test_ch * n / Mch))[::Mch]
check("PFB channel output == brute-force mix+filter+decimate", np.allclose(Y[test_ch], yref, atol=1e-9), f"max err {np.max(np.abs(Y[test_ch]-yref)):.1e}")
pw = 10 * np.log10(np.mean(np.abs(Y[:, 50:]) ** 2, axis=1) + 1e-300)
pw -= pw.max()
others = np.delete(pw, test_ch)
check("PFB channeliser: tone appears in its own channel", np.argmax(pw) == test_ch and others.max() < -40,
      f"channel powers (dB) {np.round(pw,1)}")
print(f"      cost: {Mch}-channel PFB = {Mch*P} MACs + one {Mch}-pt FFT per {Mch} input samples,"
      f" vs {Mch} separate DDC+FIRs = {Mch}x({Mch*P}) MACs per {Mch} samples")

print("\nALL PASS" if ok_all else "\nSOME FAIL")
