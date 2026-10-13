#!/usr/bin/env python3
"""Verification for kb/14-sdr-dsp/fpga-for-sdr.md -- bit-true fixed-point models

Checks (PASS/FAIL):
 1. Bit-true FIR: 16-bit data x 18-bit coefficients into a 48-bit accumulator (DSP48-style):
    worst-case accumulator magnitude bound (sum|h| x max|x|) fits; output SNR vs float.
 2. Rounding modes when dropping LSBs: truncation (floor) biases by -1/2 LSB (a DC offset),
    round-half-up nearly unbiased, convergent (round-half-even) unbiased.
 3. Integer CORDIC (vectoring mode, 16 iterations, 18-bit datapath) as an FM discriminator
    (atan2 of x[n] x*[n-1]) vs float.
 4. Resource arithmetic: DSP slices needed for FIRs at SDR rates with and without symmetry
    folding and time-sharing, vs Zynq-7010 (Pluto) and Zynq-7020 DSP48E1 counts.
 5. Latency: FPGA pipeline latency of a 255-tap FIR at 61.44 MS/s vs USB round trip.
"""
import numpy as np
from scipy import signal

rng = np.random.default_rng(9)
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


# ------------------------------------------------------------ 1. bit-true FIR
Bx, Bh, Bacc = 16, 18, 48
h = signal.remez(83, [0, 62.5e3, 80e3, 250e3], [1, 0], weight=[1, 30], fs=500e3)
hq = np.round(h / np.max(np.abs(h)) * (2 ** (Bh - 1) - 1)).astype(np.int64)  # full-scale 18-bit taps
scale_h = np.max(np.abs(h)) / (2 ** (Bh - 1) - 1)
xmax = 2 ** (Bx - 1) - 1
worst = np.sum(np.abs(hq)) * xmax
bits_needed = int(np.ceil(np.log2(worst + 1))) + 1  # + sign
check("worst-case accumulator fits 48 bits", bits_needed <= Bacc, f"needs {bits_needed} bits (bound sum|h|*max|x|); naive Bx+Bh+log2N = {Bx+Bh+int(np.ceil(np.log2(83)))}")
x = rng.standard_normal(20000) * 0.25
xq = np.clip(np.round(x * xmax), -xmax - 1, xmax).astype(np.int64)
acc = np.convolve(xq, hq)  # exact integer MACs (int64 is exact here)
check("no accumulator overflow on test data", np.max(np.abs(acc)) < 2 ** (Bacc - 1))
# output: drop LSBs to 16 bits with rounding (shift chosen so the passband gain ~1)
shift = Bh - 1  # taps were scaled by 2^(Bh-1)/max|h|; SNR below is computed after a best-fit gain
y_int = (acc + (1 << (shift - 1))) >> shift
y_float = np.convolve(xq.astype(float), h)
gain = np.dot(y_int, y_float) / np.dot(y_int, y_int)
err = y_float - gain * y_int
snr = 10 * np.log10(np.mean(y_float ** 2) / np.mean(err ** 2))
check("bit-true FIR output SNR vs float > 80 dB", snr > 80, f"{snr:.1f} dB (16-bit in/out, 18-bit taps)")

# ------------------------------------------------------------ 2. rounding modes
v = rng.integers(-2 ** 20, 2 ** 20, 200000)
k = 6  # drop 6 LSBs
exact = v / 2 ** k
trunc = v >> k  # floor
rhu = (v + (1 << (k - 1))) >> k
conv = np.round(v / 2 ** k).astype(np.int64)  # numpy rounds half to even
b_t, b_r, b_c = np.mean(trunc - exact), np.mean(rhu - exact), np.mean(conv - exact)
check("truncation bias = -1/2 LSB (+1/2^(k+1))", abs(b_t - (-0.5 + 2 ** -(k + 1))) < 0.01, f"{b_t:+.4f} LSB")
check("round-half-up bias ~ +1/2^(k+1) LSB (tiny)", abs(b_r - 2 ** -(k + 1)) < 0.01, f"{b_r:+.4f} LSB")
check("convergent rounding unbiased", abs(b_c) < 0.01, f"{b_c:+.4f} LSB")
print(f"      a -1/2 LSB bias at 16-bit output = DC at {20*np.log10(0.5/2**15):.1f} dBFS -- a visible centre spike after long FFTs")


# ------------------------------------------------------------ 3. integer CORDIC FM discriminator
def cordic_vector_int(xi, yi, n_iter=16, frac=14):
    """Integer CORDIC vectoring: returns angle in units of pi/2^frac... (radians scaled by 2^frac)."""
    atan_tab = [int(round(np.arctan(2.0 ** -i) * 2 ** frac)) for i in range(n_iter)]
    x = xi.copy().astype(np.int64)
    y = yi.copy().astype(np.int64)
    z = np.zeros_like(x)
    # pre-rotate into right half-plane
    neg = x < 0
    z = np.where(neg & (y >= 0), int(round(np.pi * 2 ** frac)), z)
    z = np.where(neg & (y < 0), -int(round(np.pi * 2 ** frac)), z)
    x, y = np.where(neg, -x, x), np.where(neg, -y, y)
    for i in range(n_iter):
        d = np.where(y < 0, 1, -1)
        x, y = x - d * (y >> i), y + d * (x >> i)
        z = z - d * atan_tab[i]
    return z  # radians * 2^frac


fs = 240e3
n = np.arange(8000)
dev = 5e3
ph = 2 * np.pi * dev / fs * np.cumsum(np.cos(2 * np.pi * 1e3 * n / fs))
xc = np.exp(1j * ph) * 0.9
q17 = 2 ** 17 - 1
xi = np.round(xc.real * q17).astype(np.int64)
xq_ = np.round(xc.imag * q17).astype(np.int64)
# product x[n] conj(x[n-1]) in integers, rescaled to 18 bits
pr = xi[1:] * xi[:-1] + xq_[1:] * xq_[:-1]
pi_ = xq_[1:] * xi[:-1] - xi[1:] * xq_[:-1]
pr, pi_ = pr >> 17, pi_ >> 17
ang = cordic_vector_int(pr, pi_, n_iter=16, frac=14) / 2 ** 14
f_cordic = ang * fs / (2 * np.pi)
f_float = np.angle(xc[1:] * np.conj(xc[:-1])) * fs / (2 * np.pi)
e = np.max(np.abs(f_cordic - f_float))
check("16-iteration integer CORDIC discriminator matches float", e < 0.002 * dev, f"max err {e:.2f} Hz of {dev:.0f} Hz ({e/dev*100:.3f} %)")

# ------------------------------------------------------------ 4. resources
dsp = {"XC7Z010 (Pluto)": 80, "XC7Z020 (AntSDR/E310)": 220}
cases = [
    ("LoRa channel FIR 83 taps, complex, 500 kS/s", 83, 500e3, 2),
    ("255-tap complex FIR at 61.44 MS/s", 255, 61.44e6, 2),
    ("half-band 31 taps (17 non-zero) complex at 30.72 MS/s", 17, 30.72e6, 2),
]
fclk = 200e6
for name, taps, fs_, rails in cases:
    macs = taps * fs_ * rails
    folded = ((taps + 1) // 2) * fs_ * rails
    slices = folded / fclk
    print(f"      {name}: {macs/1e9:.3f} G MAC/s ({folded/1e9:.3f} G folded) -> {np.ceil(slices):.0f} DSP slices at {fclk/1e6:.0f} MHz")
need_255 = np.ceil(((255 + 1) // 2) * 61.44e6 * 2 / fclk)
check("255-tap complex FIR at 61.44 MS/s needs ~79 of Pluto's 80 DSP48E1 slices", need_255 == 79, f"{need_255:.0f}")
check("LoRa channel filter fits in one time-shared slice", ((83 + 1) // 2) * 500e3 * 2 / fclk < 1)

# ------------------------------------------------------------ 5. latency
lat_fir = (255 - 1) / 2 / 61.44e6 + 20 / fclk  # group delay + ~20 pipeline registers
print(f"      255-tap FIR latency at 61.44 MS/s: {lat_fir*1e6:.2f} us vs B210 USB3 round trip ~160 us")
check("FPGA FIR latency is ~2 us", abs(lat_fir * 1e6 - 2.17) < 0.05)

print("\nALL PASS" if ok_all else "\nSOME FAIL")
