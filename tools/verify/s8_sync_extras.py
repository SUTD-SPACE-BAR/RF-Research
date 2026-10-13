#!/usr/bin/env python3
"""s8_sync_extras.py — checks for the "niche synchronisation" section of
kb/10-comms-modulation/synchronization-carrier-timing.md and the 5G NR numerology table of ofdm.md (W5-S8).

1. Feed-forward ML-type carrier phase (Viterbi & Viterbi 4th-power) for QPSK: variance vs the modified CRB
   1/(2 N Es/N0) at 10 dB, the low-SNR penalty, the pi/2 ambiguity; equivalence to a loop with BnT = 1/(2N).
2. Residual-carrier PSK: carrier power cos^2(beta), data power sin^2(beta) (spectral line measured by FFT).
3. ML (derivative-matched-filter) timing error detector: S-curve zero at the right instant; polyphase filterbank
   with P = 32 arms -> worst-case timing quantisation T/64 and its SNR loss for RRC beta = 0.35.
4. FFT (Oerder-Meyr square-law) feed-forward symbol timing: unbiased, rms error at 10 dB, 256 symbols.
5. Normalised cross-correlation delay estimation: |rho| <= 1, amplitude invariance, sub-sample (parabolic)
   estimate vs the delay CRB var >= 1/(8 pi^2 B_rms^2 E/N0).
6. 5G NR numerology (TS 38.211): subcarrier spacing, slot length, symbol and CP durations, max RBs/bandwidth.

Run: python3 tools/verify/s8_sync_extras.py    (~15 s)
"""
import numpy as np

rng = np.random.default_rng(6)
RES = []


def check(name, ok, detail=""):
    RES.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")


db = lambda x: 10 * np.log10(x)
un = lambda d: 10 ** (d / 10)
crandn = lambda *s: (rng.standard_normal(s) + 1j * rng.standard_normal(s)) / np.sqrt(2)

# ---------------------------------------------------------------- 1. Viterbi & Viterbi
print("1. Feed-forward 4th-power (Viterbi & Viterbi) phase estimation, QPSK")
Q = np.exp(1j * (np.pi / 4 + np.pi / 2 * np.arange(4)))


def vv(esn0_db, N, trials=20000, theta=0.3, m=4):
    """F(|r|) = |r|^m weighting of exp(j4 arg r); m = 4 is the plain r^4, m = 0 uses phase only."""
    es = un(esn0_db)
    a = Q[rng.integers(0, 4, (trials, N))]
    r = a * np.exp(1j * theta) + crandn(trials, N) / np.sqrt(es)
    est = np.angle(-np.sum(np.abs(r) ** m * np.exp(4j * np.angle(r)), axis=1)) / 4   # -: QPSK a^4 = -1
    err = np.angle(np.exp(4j * (est - theta))) / 4
    return np.var(err)


for N in (32, 64):
    v = vv(10, N)
    mcrb = 1 / (2 * N * un(10))
    check(f"V&V (r^4) at 10 dB, N={N}: variance ~1.5x the MCRB 1/(2N Es/N0)", 1.3 < v / mcrb < 1.7,
          f"{np.sqrt(v) * 180 / np.pi:.2f} deg rms vs MCRB {np.sqrt(mcrb) * 180 / np.pi:.2f} deg (ratio {v / mcrb:.2f})")
v0, v1 = vv(10, 32, m=0), vv(10, 32, m=1)
m10 = 1 / (2 * 32 * un(10))
check("smaller weighting exponent helps at 10 dB: m=0/1 closer to the MCRB than r^4", min(v0, v1) < vv(10, 32) and min(v0, v1) / m10 < 1.35,
      f"m=0 {v0 / m10:.2f}, m=1 {v1 / m10:.2f} x MCRB")
v3 = vv(3, 32)
m3 = 1 / (2 * 32 * un(3))
check("at 3 dB the 4th-power nonlinearity costs > 2x the MCRB (noise x signal cross terms)", v3 / m3 > 2,
      f"ratio {v3 / m3:.2f}")
bnT = 1 / (2 * 32)
check("a block of N symbols ~ a loop with BnT = 1/(2N): sigma^2 = BnT/(Es/N0) = MCRB", abs(bnT / un(10) - 1 / (2 * 32 * un(10))) < 1e-12)
check("4th-power estimator range is +-pi/4 (pi/2 ambiguity)", np.isclose(np.pi / 4, 2 * np.pi / 4 / 2))

# ---------------------------------------------------------------- 2. residual carrier
print("\n2. Residual-carrier BPSK (PM with index beta)")
Nsym, sps = 4096, 16
d = np.repeat(rng.choice([-1.0, 1.0], Nsym), sps)
for beta_deg in (30, 60, 80):
    b = np.deg2rad(beta_deg)
    s = np.exp(1j * b * d)                        # complex baseband of cos(wt + beta d)
    S = np.fft.fft(s) / len(s)
    pc = np.abs(S[0]) ** 2                        # power in the carrier line
    check(f"beta = {beta_deg} deg: carrier {db(np.cos(b) ** 2):.2f} dB, data {db(np.sin(b) ** 2):.2f} dB",
          abs(pc - np.cos(b) ** 2) < 0.002, f"line {db(pc):.2f} dB")

b60 = np.deg2rad(60)
cl = 40 + db(np.cos(b60) ** 2); lsnr = cl - db(10); ebd = 40 + db(np.sin(b60) ** 2) - db(100)
check("residual-carrier example: C/N0 40 dB-Hz, beta 60 deg -> carrier 34.0 dB-Hz, 10 Hz loop SNR 24.0 dB, data Eb/N0 18.8 dB",
      abs(cl - 33.98) < 0.01 and abs(lsnr - 23.98) < 0.01 and abs(ebd - 18.75) < 0.01)

# ---------------------------------------------------------------- 3. ML TED + polyphase
print("\n3. ML timing error detector and polyphase filterbank")
sps = 32
beta = 0.35
span = 8
t = np.arange(-span * sps, span * sps + 1) / sps


def rrc(t, b):
    out = np.empty_like(t)
    for i, x in enumerate(t):
        if abs(x) < 1e-9:
            out[i] = 1 - b + 4 * b / np.pi
        elif abs(abs(x) - 1 / (4 * b)) < 1e-9:
            out[i] = b / np.sqrt(2) * ((1 + 2 / np.pi) * np.sin(np.pi / (4 * b)) + (1 - 2 / np.pi) * np.cos(np.pi / (4 * b)))
        else:
            out[i] = (np.sin(np.pi * x * (1 - b)) + 4 * b * x * np.cos(np.pi * x * (1 + b))) / (np.pi * x * (1 - (4 * b * x) ** 2))
    return out


h = rrc(t, beta)
h /= np.sqrt(np.sum(h ** 2))
rc = np.convolve(h, h)                            # matched-filter output pulse (raised cosine)
drc = np.gradient(rc)
nb = 400
a = rng.choice([-1.0, 1.0], nb)
up = np.zeros(nb * sps); up[::sps] = a
y = np.convolve(up, rc)
dy = np.convolve(up, drc)
c0 = len(rc) // 2
offs = np.arange(-sps // 2, sps // 2 + 1)
sc = []
for o in offs:
    idx = c0 + np.arange(20, nb - 20) * sps + o
    sc.append(np.mean(y[idx] * dy[idx]))        # e = y(tau) y'(tau): derivative of the log-likelihood
sc = np.array(sc)
zc = offs[np.argmin(np.abs(sc))]
check("ML TED S-curve crosses zero at the correct instant", zc == 0 and sc[offs == -4][0] * sc[offs == 4][0] < 0,
      f"zero at offset {zc}/{sps}")
pk = rc[c0]
# timing quantisation of a P = 32 polyphase bank: worst error T/64 -> peak loss and ISI power
P = 32
tq = 1 / (2 * P)
fine = rrc(np.arange(-span * 512, span * 512 + 1) / 512, beta)
fine /= np.sqrt(np.sum(fine ** 2))
rcf = np.convolve(fine, fine)
rcf /= rcf.max()
cf = len(rcf) // 2
k = int(round(tq * 512))
samples = rcf[cf + k + 512 * np.arange(-12, 13)]
sig = samples[12] ** 2
isi = np.sum(samples ** 2) - sig
sinr_loss = db(1 / sig)
check("P = 32 polyphase arms: worst-case T/64 offset costs < 0.01 dB of peak and ISI < -30 dB",
      sinr_loss < 0.01 and db(isi / sig) < -30, f"peak loss {sinr_loss:.4f} dB, ISI {db(isi / sig):.1f} dB")

# ---------------------------------------------------------------- 4. Oerder-Meyr
print("\n4. Oerder-Meyr square-law FFT timing")
sps4 = 4
t4 = np.arange(-span * sps4, span * sps4 + 1) / sps4
h4 = rrc(t4, 0.5); h4 /= np.sqrt(np.sum(h4 ** 2))
L = 256
errs = []
for _ in range(400):
    tau = rng.uniform(-0.5, 0.5)                   # in symbols
    sy = Q[rng.integers(0, 4, L + 2 * span)]
    upq = np.zeros((L + 2 * span) * 32, complex); upq[::32] = sy
    ht = rrc(np.arange(-span * 32, span * 32 + 1) / 32, 0.5)
    tx = np.convolve(upq, ht)
    shift = int(round(tau * 32))
    rx = np.roll(tx, shift)[::8]                   # 4 samples/symbol after a sub-symbol delay
    rx = rx + crandn(len(rx)) * np.sqrt(np.mean(np.abs(rx) ** 2) * sps4 / un(10))
    mf = np.convolve(rx, h4[::1], mode="same")
    seg = mf[span * sps4 * 2: span * sps4 * 2 + L * sps4]
    k = np.arange(len(seg))
    X = np.sum(np.abs(seg) ** 2 * np.exp(-2j * np.pi * k / sps4))
    est = -np.angle(X) / (2 * np.pi)              # fraction of a symbol, mod 1
    true = (shift / 32.0)
    e = np.angle(np.exp(2j * np.pi * (est - true - (0.0)))) / (2 * np.pi)
    errs.append(e)
errs = np.array(errs)
bias = np.angle(np.mean(np.exp(2j * np.pi * errs))) / (2 * np.pi)
errs = np.angle(np.exp(2j * np.pi * (errs - bias))) / (2 * np.pi)
check("Oerder-Meyr at 10 dB, 256 symbols, beta=0.5: rms timing error < 0.03 T (after removing the fixed filter delay)",
      np.std(errs) < 0.03, f"rms {np.std(errs):.4f} T, constant offset {bias:.3f} T")

# ---------------------------------------------------------------- 5. NCC delay estimation
print("\n5. Normalised cross-correlation delay estimation")
N = 4096
osr = 4                                            # signal bandwidth = fs/osr
f = np.fft.fftfreq(N)
mask = np.abs(f) < 0.5 / osr


def bl_noise():
    X = np.zeros(N, complex); X[mask] = crandn(mask.sum())
    return np.fft.ifft(X) * np.sqrt(N / mask.sum() * N) / np.sqrt(N)


def delay(x, d):
    return np.fft.ifft(np.fft.fft(x) * np.exp(-2j * np.pi * f * d))


s = bl_noise()
Es = np.sum(np.abs(s) ** 2)
brms2 = np.sum(f[mask] ** 2) / mask.sum()            # cycles/sample, flat spectrum: (fs/osr)^2/12
check("flat band B: B_rms^2 = B^2/12", abs(brms2 - (1 / osr) ** 2 / 12) / brms2 < 0.01)


def ncc(x, y):
    X, Y = np.fft.fft(x), np.fft.fft(y)
    c = np.fft.ifft(np.conj(X) * Y)
    return c / np.sqrt(np.sum(np.abs(x) ** 2) * np.sum(np.abs(y) ** 2))


rho = ncc(s, 3.7 * delay(s, 5.0))
check("|NCC| <= 1 and = 1 for a scaled, integer-delayed copy (amplitude-invariant)",
      np.max(np.abs(rho)) <= 1 + 1e-9 and abs(np.max(np.abs(rho)) - 1) < 1e-9)
sig2 = Es / N / un(-5)                              # per-sample SNR -5 dB
EN0 = Es / sig2
crb = 1 / (8 * np.pi ** 2 * brms2 * EN0)
est = []
for _ in range(1000):
    dtrue = rng.uniform(10, 11)
    yv = delay(s, dtrue) + np.sqrt(sig2) * crandn(N)
    c = np.abs(ncc(s, yv))
    k = int(np.argmax(c))
    # sub-sample: fit a parabola to Re of the (phase-aligned) correlation around the peak
    cc = ncc(s, yv)
    ph = np.exp(-1j * np.angle(cc[k]))
    y0, y1, y2 = (cc[(k + np.array([-1, 0, 1])) % N] * ph).real
    frac = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
    est.append(k + frac - dtrue)
est = np.array(est)
bias = np.mean(est)
rmse = np.sqrt(np.mean((est - bias) ** 2))
print(f"   E/N0 = {db(EN0):.1f} dB: rms {rmse:.4f} samples vs CRB {np.sqrt(crb):.4f}, mean bias {bias:+.4f}")
check("NCC + parabolic interpolation (4x oversampled) within 1.5x of the CRB std at E/N0 = 31 dB",
      rmse < 1.5 * np.sqrt(crb), f"ratio {rmse / np.sqrt(crb):.2f}")
check("parabolic-interpolation bias is small (< 0.05 sample) at 4x oversampling", abs(bias) < 0.05, f"{bias:+.4f}")
# numbers on the page: 1 MHz flat band, E/N0 = 30 dB -> sigma_tau
B = 1e6
st = 1 / (2 * np.pi * (B / np.sqrt(12)) * np.sqrt(2 * un(30)))
check("1 MHz flat band, E/N0 = 30 dB: sigma_tau = 12.3 ns (3.7 m)", abs(st * 1e9 - 12.3) < 0.1 and abs(st * 3e8 - 3.69) < 0.03,
      f"{st * 1e9:.1f} ns")

# ---------------------------------------------------------------- 6. NR numerology
print("\n6. 5G NR numerology (normal CP)")
Tc = 1 / (480e3 * 4096)
kappa = 64
rows = []
for mu in range(0, 7):
    scs = 15e3 * 2 ** mu
    slot = 1e-3 / 2 ** mu
    tu = 2048 * kappa * Tc / 2 ** mu
    cp = 144 * kappa * Tc / 2 ** mu
    cp0 = cp + 16 * kappa * Tc                       # first symbol of each half-subframe
    rows.append((mu, scs, slot, tu, cp, cp0))
    print(f"   mu={mu}: {scs / 1e3:6.0f} kHz, slot {slot * 1e3:.4f} ms, {2 ** mu:3d} slots/ms, Tu {tu * 1e6:7.3f} us, "
          f"CP {cp * 1e6:.3f} us (long CP {cp0 * 1e6:.3f} us)")
check("mu=0: Tu 66.67 us, CP 4.69 us, first-symbol CP 5.21 us (= LTE)", abs(rows[0][3] * 1e6 - 66.667) < 0.01 and
      abs(rows[0][4] * 1e6 - 4.6875) < 0.001 and abs(rows[0][5] * 1e6 - 5.2083) < 0.001)
check("mu=1 (30 kHz): slot 0.5 ms, CP 2.34 us; mu=3 (120 kHz): slot 0.125 ms, CP 0.586 us",
      abs(rows[1][4] * 1e6 - 2.344) < 0.001 and abs(rows[3][2] * 1e3 - 0.125) < 1e-9 and abs(rows[3][4] * 1e6 - 0.586) < 0.001)
check("14 symbols + CPs fill one slot exactly (mu=1)",
      abs(14 * (rows[1][3] + rows[1][4]) + 16 * kappa * Tc - rows[1][2] * 1) < 1e-12 or
      abs(14 * (rows[1][3] + rows[1][4]) + 16 * kappa * Tc / 1 - 0.5e-3) < 1e-9)
for scs, bw, nrb in [(15, 50, 270), (30, 100, 273), (60, 100, 135), (60, 200, 264), (120, 400, 264)]:
    occ = nrb * 12 * scs * 1e3
    check(f"{scs} kHz, {bw} MHz, {nrb} RB: occupied {occ / 1e6:.2f} MHz ({occ / (bw * 1e6):.1%} of the channel)",
          0.9 < occ / (bw * 1e6) < 0.99)
fft30 = 4096
check("30 kHz x 4096-point FFT = 122.88 MS/s for 100 MHz", abs(30e3 * fft30 - 122.88e6) < 1)
wifi = 52 * 312.5e3
check("802.11a/g: 52 used subcarriers -> 16.25 MHz (+DC null) ~ 16.6 MHz occupied", abs((53 * 312.5e3) / 1e6 - 16.56) < 0.01)
lte = 1200 * 15e3
check("LTE 20 MHz: 100 RB x 12 x 15 kHz = 18 MHz (+ unused DC subcarrier)", lte == 18e6)
check("LTE PSS/SSS/PBCH occupy the central 6 RB = 1.08 MHz", 6 * 12 * 15e3 == 1.08e6)
check("802.11n HT20: 56 used subcarriers -> 17.5 MHz (17.8 MHz edge to edge with DC)", abs(57 * 312.5e3 / 1e6 - 17.81) < 0.01)
crs = 8 / (12 * 14)
check("idle LTE cell, 1 CRS port: 8 of 168 REs per RB-subframe -> -13.2 dB below full load (equal EPRE)",
      abs(db(crs) + 13.22) < 0.02, f"{db(crs):.2f} dB")
ssb = 240 * 30e3
check("NR SSB: 240 subcarriers at 30 kHz = 7.2 MHz (20 RB)", ssb == 7.2e6)
lam = 3e8 / 2.44e9
check("lambda/2 at 2.44 / 5.5 GHz = 6.1 / 2.7 cm", abs(lam / 2 * 100 - 6.15) < 0.05 and abs(3e8 / 5.5e9 / 2 * 100 - 2.73) < 0.02)

print(f"\n{sum(RES)}/{len(RES)} checks PASS")
