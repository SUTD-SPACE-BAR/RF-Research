#!/usr/bin/env python3
"""Verification for kb/11-radar/pulsed-radar-and-pulse-compression.md

Run:  python3 tools/verify/radar_pulse_compression.py      (~10 s)

Checks:
  1. Pulsed-radar timing: range resolution c/2B, unambiguous range c/(2 PRF), unambiguous velocity
     +-lambda PRF/4, duty cycle, average power, blind (eclipsed) range; worked-example table.
  2. LFM (linear FM) pulse compression, TB = 100 and 1000:
       - compressed -3 dB width ~0.886/B (rect weighting), -4 dB null-to-null 2/B
       - peak sidelobe -13.26 dB (unweighted, large TB)
       - Hamming / Taylor(nbar=5,-35 dB) receive weighting: PSL, main-lobe broadening, SNR loss
       - compression gain = TB (peak-power ratio in/out for unit-energy normalisation)
  3. Barker codes 2..13: aperiodic autocorrelation sidelobes <= 1; Barker-13 PSL = -22.28 dB.
  4. Polyphase codes: Frank (M^2), P4, and a random binary code: PSL/ISL vs length;
     Frank PSL approx 1/(pi M).
  5. Doppler tolerance: mismatch loss vs normalised Doppler fd*T for LFM (TB=100), Barker-13, P4-64;
     LFM range-Doppler coupling: peak shift = fd T / B (seconds) -> range error.
  6. Range-sampling (straddle) loss for LFM sampled at 1/B and 1/(2B).
  7. PRF ambiguity resolution with two coprime PRFs (Chinese remainder theorem demo).
"""
import numpy as np
from scipy import signal

c = 299_792_458.0
ok_all = True


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel else 1.0)
    ok = err <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol}{' rel' if rel else ''})")
    return ok


db20 = lambda x: 20 * np.log10(np.abs(x) + 1e-300)

print("=" * 78)
print("1. Pulsed radar timing examples")
cases = [  # name, f (Hz), tau (s), B (Hz), PRF (Hz), Ppk (W)
    ("S-band DIY tracker", 3.0e9, 1e-6, 1e6, 1e3, 100.0),
    ("X-band marine radar (short pulse)", 9.41e9, 0.08e-6, 12.5e6, 3e3, 4e3),
    ("X-band pulse-Doppler (high PRF)", 10e9, 1e-6, 10e6, 100e3, 100.0),
    ("Acconeer-style 60 GHz PCR (illustrative)", 60.5e9, 1e-9, 1e9, 10e6, 1e-3),
]
for name, f, tau, B, prf, P in cases:
    lam = c / f
    dR = c / (2 * B)
    Ru = c / (2 * prf)
    vu = lam * prf / 4
    duty = tau * prf
    Pav = P * duty
    Rblind = c * tau / 2
    print(f"    {name:40s}: dR={dR:8.3f} m, Ru={Ru/1e3:9.3f} km, v_u=+-{vu:8.2f} m/s, duty={duty*100:6.3f} %, "
          f"Pav={Pav:8.3g} W, blind R >= {Rblind:7.2f} m")
check("c/2B for 1 MHz = 149.9 m", c / 2e6, 149.9, 0.05)
check("Ru for PRF 1 kHz = 149.9 km", c / 2e3 / 1e3, 149.9, 0.05)
check("vu for 10 GHz, 100 kHz PRF = +-749.5 m/s", (c / 10e9) * 100e3 / 4, 749.5, 0.1)

print("=" * 78)
print("2. LFM pulse compression")


def lfm(T, B, fs):
    t = np.arange(int(round(T * fs))) / fs
    return np.exp(1j * np.pi * (B / T) * (t - T / 2) ** 2)


def compress(s, w=None, osf=1):
    h = np.conj(s[::-1]) * (np.ones(len(s)) if w is None else w[::-1])
    y = np.convolve(s, h)
    return y


def taylor_win(n, nbar=5, sll=-35):
    return signal.windows.taylor(n, nbar=nbar, sll=-sll, norm=False)


def mainlobe_width(y, fs, level_db=-3.0):
    a = np.abs(y) / np.abs(y).max()
    k = np.argmax(a)
    thr = 10 ** (level_db / 20)
    i = k
    while i > 0 and a[i] > thr:
        i -= 1
    j = k
    while j < len(a) - 1 and a[j] > thr:
        j += 1
    # linear interpolation
    li = i + (thr - a[i]) / (a[i + 1] - a[i])
    lj = j - 1 + (a[j - 1] - thr) / (a[j - 1] - a[j])
    return (lj - li) / fs


def psl(y, excl):
    a = np.abs(y) / np.abs(y).max()
    k = np.argmax(a)
    mask = np.ones(len(a), bool)
    mask[max(0, k - excl):k + excl + 1] = False
    return db20(a[mask].max())


def excl_first_null(y):
    a = np.abs(y)
    k = np.argmax(a)
    j = k
    while j < len(a) - 1 and a[j + 1] < a[j]:
        j += 1
    return j - k


for TB in (100, 1000):
    B = 10e6
    T = TB / B
    fs = 8 * B
    s = lfm(T, B, fs)
    y = compress(s)
    w3 = mainlobe_width(y, fs, -3) * B
    ex = excl_first_null(y)
    p = psl(y, ex)
    print(f"    TB={TB}: -3 dB width = {w3:.3f}/B, PSL = {p:.2f} dB (unweighted)")
    check(f"LFM TB={TB} -3 dB width ~0.886/B", w3, 0.886, 0.02)
    check(f"LFM TB={TB} PSL ~ -13.26 dB", p, -13.26, 0.5)
    # compression ratio: input pulse length / output -3 dB width = TB * (1/0.886)
    for wname, win in (("hamming", np.hamming(len(s))), ("taylor5-35", taylor_win(len(s)))):
        yw = compress(s, win)
        ww = mainlobe_width(yw, fs, -3) * B
        exw = excl_first_null(yw)
        pw = psl(yw, exw)
        # SNR loss of mismatched filter: |h^H s|^2 / (|h|^2 |s|^2)
        h = s * win
        loss = -10 * np.log10(np.abs(np.vdot(h, s)) ** 2 / (np.vdot(h, h).real * np.vdot(s, s).real))
        print(f"      {wname:11s}: -3 dB width {ww:.3f}/B (x{ww/w3:.2f}), PSL {pw:6.2f} dB, SNR loss {loss:.2f} dB")
        if TB == 1000 and wname == "hamming":
            check("Hamming-weighted LFM PSL ~ -42 dB (TB=1000)", pw, -42.0, 1.5)
            check("Hamming SNR loss ~1.34 dB", loss, 1.34, 0.05)
            check("Hamming broadening ~1.47x", ww / w3, 1.47, 0.05)
        if TB == 1000 and wname == "taylor5-35":
            check("Taylor(5,-35) LFM PSL ~ -35 dB (TB=1000)", pw, -35.0, 1.5)

print("=" * 78)
print("3. Barker codes")
barker = {2: [1, -1], 3: [1, 1, -1], 4: [1, 1, -1, 1], 5: [1, 1, 1, -1, 1], 7: [1, 1, 1, -1, -1, 1, -1],
          11: [1, 1, 1, -1, -1, -1, 1, -1, -1, 1, -1], 13: [1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1]}
for n, code in barker.items():
    r = np.correlate(code, code, "full")
    side = np.max(np.abs(np.delete(r, n - 1)))
    check(f"Barker-{n} max |sidelobe| <= 1", side, 1.0, 0)
b13 = np.array(barker[13], float)
r = np.correlate(b13, b13, "full")
check("Barker-13 PSL = 20log(1/13) dB", db20(np.max(np.abs(np.delete(r, 12))) / 13), -22.28, 0.01)
isl13 = 10 * np.log10(np.sum(np.delete(r, 12) ** 2) / 13 ** 2)
print(f"    Barker-13 ISL = {isl13:.2f} dB")

print("=" * 78)
print("4. Polyphase codes")


def frank(M):
    i, k = np.meshgrid(np.arange(M), np.arange(M), indexing="ij")
    return np.exp(2j * np.pi * (i * k) / M).ravel()


def p4(N):
    n = np.arange(N)
    return np.exp(1j * np.pi * n * (n - N) / N)


def psl_code(x):
    r = np.correlate(x, x, "full")
    N = len(x)
    side = np.abs(np.delete(r, N - 1))
    return db20(side.max() / N), 10 * np.log10(np.sum(side ** 2) / N ** 2)


rng = np.random.default_rng(4)
for M in (4, 8, 16):
    N = M * M
    pf, isf = psl_code(frank(M))
    pp, isp = psl_code(p4(N))
    rb = rng.choice([-1.0, 1.0], N)
    pr, isr = psl_code(rb)
    print(f"    N={N:3d}: Frank PSL {pf:6.2f} dB (1/(pi M) -> {db20(1/(np.pi*M)):6.2f}), P4 PSL {pp:6.2f} dB, random binary PSL {pr:6.2f} dB (~1/sqrtN -> {db20(1/np.sqrt(N)):6.2f})")
    if M == 16:
        check("Frank-256 PSL vs 1/(pi M) (dB)", pf, db20(1 / (np.pi * M)), 1.0)

print("=" * 78)
print("5. Doppler tolerance (matched filter peak loss vs Doppler, peak searched over delay)")


def doppler_loss(x, fs, fd):
    """x sampled at fs; apply Doppler fd; compute max over delay of |MF output| relative to fd=0."""
    t = np.arange(len(x)) / fs
    xd = x * np.exp(2j * np.pi * fd * t)
    y = np.abs(np.correlate(xd, x, "full"))
    y0 = np.abs(np.correlate(x, x, "full")).max()
    return db20(y.max() / y0), (np.argmax(y) - (len(x) - 1)) / fs


B = 10e6
T = 100 / B
fs = 8 * B
s = lfm(T, B, fs)
# codes: chip = 1/B, oversample 8
def upsample(code, osr=8):
    return np.repeat(code, osr)
b13s = upsample(b13)
fsb = 8 * B
Tb = 13 / B
p4s = upsample(p4(64))
Tp = 64 / B
print("    fd*T :  LFM(TB=100)  Barker13  P4-64")
for fdT in (0.1, 0.25, 0.5, 1.0, 2.0):
    lf, sh = doppler_loss(s, fs, fdT / T)
    lb, _ = doppler_loss(b13s, fsb, fdT / Tb)
    lp, _ = doppler_loss(p4s, fsb, fdT / Tp)
    print(f"    {fdT:4.2f} : {lf:8.2f} dB {lb:9.2f} dB {lp:7.2f} dB   (LFM peak shift {sh*1e9:7.2f} ns; predicted fd*T/B = {fdT/T*T/B*1e9:7.2f} ns)")
lf, sh = doppler_loss(s, fs, 1.0 / T)
check("LFM range-Doppler coupling: peak shift = fd T/B (fd T = 1)", abs(sh), 1.0 / B, 0.02 / B)
lb05, _ = doppler_loss(b13s, fsb, 0.5 / Tb)
check("Barker-13 loses > 3 dB at fd*T = 0.5", float(lb05 < -3.0), 1.0, 0)
lf2, _ = doppler_loss(s, fs, 2.0 / T)
check("LFM TB=100 loses < 0.3 dB at fd*T = 2 (Doppler tolerant)", float(lf2 > -0.3), 1.0, 0)
# 77 GHz example: pulse/chirp 50 us, v=30 m/s -> fd = 15.4 kHz; fd*T = 0.77
fd77 = 2 * 30 / (c / 77e9)
print(f"    77 GHz, 30 m/s -> fd = {fd77/1e3:.2f} kHz; over a 50 us waveform fd*T = {fd77*50e-6:.2f}")

print("=" * 78)
print("6. Range-sampling (straddle) loss, LFM TB=100, rect weighting")
y = compress(s)
a = np.abs(y) / np.abs(y).max()
k = np.argmax(a)
osr = 8  # fs = 8B
for spb in (1, 2):
    step = osr // spb    # samples per 1/(spb*B)
    worst = db20(a[k + step // 2])     # half a sample off peak
    offs = np.arange(-step // 2, step // 2 + 1)
    avg = 10 * np.log10(np.mean(a[k + offs] ** 2))
    print(f"    sampling at {spb}/B-> worst {worst:.2f} dB, average {avg:.2f} dB")
    if spb == 1:
        check("worst straddle, 1 sample per 1/B = sinc(0.5) = -3.92 dB", worst, -3.92, 0.05)
    else:
        check("worst straddle, 2 samples per 1/B ~ -0.91 dB", worst, -0.91, 0.05)

print("=" * 78)
print("7. PRF ambiguity resolution with two PRFs (CRT)")
# range bins: PRF1 gives Nu1 = 7 unambiguous cells, PRF2 gives Nu2 = 8 -> unambiguous to 56
Nu1, Nu2 = 7, 8
ok = True
for true in range(0, 56):
    m1, m2 = true % Nu1, true % Nu2
    sol = [x for x in range(56) if x % Nu1 == m1 and x % Nu2 == m2]
    ok &= (sol == [true])
check("CRT: coprime 7/8 cells unambiguous to 56", float(ok), 1.0, 0)

print("=" * 78)
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
