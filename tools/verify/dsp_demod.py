#!/usr/bin/env python3
"""Verification for kb/14-sdr-dsp/software-demodulation.md

Checks (PASS/FAIL):
 1. FM demodulators: arctan-of-conjugate-product (polar discriminator) and the
    derivative form (I dQ - Q dI)/(I^2+Q^2) recover the instantaneous frequency.
 2. FM broadcast-style demod: 75 kHz deviation tone -> correct audio amplitude; de-emphasis corner.
 3. AM: envelope detector recovers the message; synchronous detector too.
 4. SSB: phasing-method USB generation; demodulation by shift + real part; wrong sideband gives LSB mirror.
 5. Non-coherent BFSK (two correlators): BER vs theory 0.5 exp(-Eb/2N0).
 6. Discriminator detection of 2-FSK (h=1) and 2-GFSK (h=0.5, BT=0.5): BER vs Eb/N0 and the
    loss relative to ideal non-coherent orthogonal FSK at BER 1e-3 (closes a domain-10 gap).
 7. QPSK receiver: RRC matched filter + Gardner timing recovery + Costas loop; BER vs theory.
 8. LoRa dechirp + FFT demodulation: SER vs SNR matches the exact non-coherent M-FSK formula (SF7).
 9. LoRa CFO: an uncorrected CFO of one bin (BW/2^SF) shifts every symbol by one.
10. CRC check values (CCITT-FALSE 0x29B1; X-25/AX.25 0x906E) and end-to-end packet pipeline: GFSK telemetry frame (preamble, sync word, payload, CRC-16/CCITT)
    through CFO + timing offset + noise; receiver decodes and CRC-checks packets.
"""
import numpy as np
from scipy import signal, special, integrate

rng = np.random.default_rng(2026)
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def awgn(x, snr_db, sig_power=None):
    p = np.mean(np.abs(x) ** 2) if sig_power is None else sig_power
    n0 = p / 10 ** (snr_db / 10)
    return x + np.sqrt(n0 / 2) * (rng.standard_normal(len(x)) + 1j * rng.standard_normal(len(x)))


def fm_polar(x, fs):
    """Polar discriminator: angle(x[n] conj(x[n-1])) * fs / 2pi -> Hz."""
    return np.angle(x[1:] * np.conj(x[:-1])) * fs / (2 * np.pi)


def fm_deriv(x, fs):
    i, q = np.real(x), np.imag(x)
    di, dq = np.gradient(i), np.gradient(q)
    return (i * dq - q * di) / (i ** 2 + q ** 2) * fs / (2 * np.pi)


# ------------------------------------------------------------ 1. FM demodulators
fs = 240e3
n = np.arange(24000)
fm_mod = 1e3
dev = 5e3
phase = 2 * np.pi * dev / fs * np.cumsum(np.cos(2 * np.pi * fm_mod * n / fs))
x = np.exp(1j * phase)
inst = dev * np.cos(2 * np.pi * fm_mod * n / fs)
# the phase increment from n-1 to n is exactly 2 pi dev cos(w n)/fs, so the polar discriminator
# should return inst[n]; np.gradient (central difference) returns the mean of increments n and n+1
e1 = np.max(np.abs(fm_polar(x, fs) - inst[1:]))
e2 = np.max(np.abs(fm_deriv(x, fs)[5:-5] - (inst[5:-5] + inst[6:-4]) / 2))
check("polar discriminator recovers instantaneous frequency", e1 < 1e-6, f"max err {e1:.1e} Hz of {dev:.0f} Hz")
check("derivative discriminator (I dQ - Q dI)/|x|^2", e2 < 0.01 * dev, f"max err {e2:.1f} Hz (small-angle approx)")
xa = 3.7 * x  # amplitude independence
check("discriminator is amplitude independent", np.allclose(fm_polar(xa, fs), fm_polar(x, fs)))

# ------------------------------------------------------------ 2. broadcast FM
fs = 480e3
n = np.arange(96000)
dev = 75e3
aud = 0.5 * np.sin(2 * np.pi * 1e3 * n / fs)  # half of full deviation
x = np.exp(1j * 2 * np.pi * dev / fs * np.cumsum(aud))
d = fm_polar(x, fs) / dev
amp = np.sqrt(2) * np.std(d[1000:])
check("WBFM 75 kHz dev: audio amplitude recovered (0.5 of full scale)", abs(amp - 0.5) < 0.005, f"{amp:.4f}")
tau = 50e-6
fc = 1 / (2 * np.pi * tau)
b, a = signal.bilinear([1], [tau, 1], fs=48e3)
w, h = signal.freqz(b, a, worN=[fc], fs=48e3)
check("50 us de-emphasis (bilinear) is -3 dB near 3.18 kHz", abs(20 * np.log10(np.abs(h[0])) + 3.01) < 0.15, f"{20*np.log10(np.abs(h[0])):.2f} dB at {fc:.0f} Hz")

# ------------------------------------------------------------ 3. AM
fs = 48e3
n = np.arange(48000)
m = 0.6 * np.cos(2 * np.pi * 700 * n / fs)
x = (1 + m) * np.exp(1j * (2 * np.pi * 2.5e3 * n / fs + 0.7))  # AM with residual 2.5 kHz offset, phase
env = np.abs(x) - np.mean(np.abs(x))
check("AM envelope detector |x| recovers message", np.max(np.abs(env - m)) < 1e-9)
# synchronous: remove offset (assume carrier recovered), take real part
sync = np.real(x * np.exp(-1j * (2 * np.pi * 2.5e3 * n / fs + 0.7))) - 1
check("synchronous AM detector recovers message", np.max(np.abs(sync - m)) < 1e-9)

# ------------------------------------------------------------ 4. SSB
fs = 48e3
n = np.arange(2 ** 15)
a1, a2 = np.cos(2 * np.pi * 700 * n / fs), 0.5 * np.cos(2 * np.pi * 1900 * n / fs)
audio = a1 + a2
ana = signal.hilbert(audio)  # analytic = USB at complex baseband
fcar = 10e3
rf = np.real(ana * np.exp(2j * np.pi * fcar * n / fs))  # real USB signal at 10 kHz carrier


def tone_db(x, f, fs_):
    w = signal.windows.flattop(len(x), sym=False)
    nn = np.arange(len(x))
    return 20 * np.log10(np.abs(np.sum(x * w * np.exp(-2j * np.pi * f * nn / fs_))) / w.sum() + 1e-300)


check("phasing-method USB: lines at fc+700 and fc+1900 only", tone_db(rf, fcar + 700, fs) > -7 and tone_db(rf, fcar - 700, fs) < -100,
      f"USB {tone_db(rf, fcar+700, fs):.1f} dB, LSB {tone_db(rf, fcar-700, fs):.1f} dB")
bb = signal.hilbert(rf) * np.exp(-2j * np.pi * fcar * n / fs)
dem = np.real(bb)
mid = slice(len(n) // 4, 3 * len(n) // 4)
err_ssb = np.max(np.abs(dem[mid] - audio[mid])) / np.max(np.abs(audio))
check("USB demod (shift by carrier, real part) recovers audio", err_ssb < 0.01, f"max rel err {err_ssb:.1e} (FFT-Hilbert leakage)")
# demodulating with the carrier on the wrong side (fcar - offset) inverts/shifts audio:
bb2 = signal.hilbert(rf) * np.exp(-2j * np.pi * (fcar + 3000) * n / fs)  # tuned 3 kHz high (as if LSB)
dem2 = np.real(bb2)
check("mistuned/wrong-sideband SSB shifts audio (700 Hz -> |700-3000| = 2300 Hz)", tone_db(dem2, 2300, fs) > -10 and tone_db(dem2, 700, fs) < -60)


# ------------------------------------------------------------ 5-6. FSK BER
def fsk_mod(bits, sps, h, bt=None):
    """CPFSK/GFSK complex baseband at sps samples/bit, modulation index h (deviation = h/2 * Rb)."""
    nrz = np.repeat(2 * bits - 1, sps).astype(float)
    if bt is not None:
        tt = np.arange(-2 * sps, 2 * sps + 1) / sps
        g = np.sqrt(2 * np.pi / np.log(2)) * bt * np.exp(-2 * (np.pi * bt * tt) ** 2 / np.log(2))
        g /= g.sum()
        nrz = np.convolve(nrz, g, mode="same")
    ph = np.pi * h / sps * np.cumsum(nrz)
    return np.exp(1j * ph)


def ber_noncoh_corr(ebn0_db, nbits=40000, sps=8):
    bits = rng.integers(0, 2, nbits)
    x = fsk_mod(bits, sps, 1.0)  # h=1 orthogonal
    ebn0 = 10 ** (ebn0_db / 10)
    n0 = 1.0 * sps / ebn0  # Eb = sps (unit power x sps samples)
    y = x + np.sqrt(n0 / 2) * (rng.standard_normal(len(x)) + 1j * rng.standard_normal(len(x)))
    k = np.arange(sps)
    t1 = np.exp(1j * np.pi / sps * k)
    t0 = np.exp(-1j * np.pi / sps * k)
    Y = y.reshape(-1, sps)
    e1 = np.abs(Y @ np.conj(t1))
    e0 = np.abs(Y @ np.conj(t0))
    return np.mean((e1 > e0).astype(int) != bits)


for eb in (8.0, 10.0, 12.0):
    sim = ber_noncoh_corr(eb, nbits=200000 if eb > 11 else 60000)
    th = 0.5 * np.exp(-10 ** (eb / 10) / 2)
    check(f"non-coherent BFSK BER @ Eb/N0={eb} dB", abs(np.log10(sim) - np.log10(th)) < 0.12, f"sim {sim:.2e} vs theory {th:.2e}")


def ber_discriminator(ebn0_db, h, bt, nbits=60000, sps=8, prefilter_bw=None):
    """Discriminator detector: pre-detection LPF, polar discriminator, integrate over bit, sign."""
    bits = rng.integers(0, 2, nbits)
    x = fsk_mod(bits, sps, h, bt)
    ebn0 = 10 ** (ebn0_db / 10)
    n0 = sps / ebn0
    y = x + np.sqrt(n0 / 2) * (rng.standard_normal(len(x)) + 1j * rng.standard_normal(len(x)))
    # pre-detection filter: bandwidth ~ Carson (Rb*(h+1)) unless given (in units of Rb), fs = sps*Rb
    bw = prefilter_bw if prefilter_bw is not None else (h + 1.0)
    lp = signal.firwin(8 * sps + 1, bw / 2, fs=sps)
    yf = signal.lfilter(lp, 1, y)
    dly = (len(lp) - 1) // 2
    f = np.angle(yf[1:] * np.conj(yf[:-1]))
    f = np.concatenate([[0], f])[dly:]
    f = np.concatenate([f, np.zeros(dly)])
    # integrate-and-dump over the central part of each bit
    F = f[: nbits * sps].reshape(-1, sps)[:, 1:]
    dec = (F.sum(axis=1) > 0).astype(int)
    return np.mean(dec[10:-10] != bits[10:-10])


def req_ebn0(fun, target=1e-3, lo=4.0, hi=20.0):
    """Bisection on Eb/N0 (dB) for BER=target using a smooth fit of 5 points."""
    grid = np.linspace(lo, hi, 9)
    bers = np.array([max(fun(g), 1e-7) for g in grid])
    ok = (bers > 2e-5) & (bers < 0.2)
    p = np.polyfit(grid[ok], np.log10(bers[ok]), 2)
    roots = np.roots(p - np.array([0, 0, np.log10(target)]))
    roots = [r.real for r in roots if abs(r.imag) < 1e-9 and lo <= r.real <= hi]
    return min(roots) if roots else np.nan


th_nc = 2 * np.log(2 * 1e-3) * -1  # Eb/N0 (linear) for 0.5 exp(-x/2) = 1e-3 -> x = -2 ln(2e-3)
th_nc_db = 10 * np.log10(th_nc)
r_fsk = req_ebn0(lambda e: ber_discriminator(e, 1.0, None), lo=6, hi=16)
r_gfsk = req_ebn0(lambda e: ber_discriminator(e, 0.5, 0.5), lo=6, hi=18)
print(f"      Eb/N0 for BER 1e-3: ideal non-coherent orthogonal BFSK {th_nc_db:.2f} dB; "
      f"discriminator 2-FSK h=1: {r_fsk:.2f} dB; discriminator 2-GFSK h=0.5 BT=0.5: {r_gfsk:.2f} dB")
check("discriminator 2-FSK (h=1) within ~0-3 dB of ideal non-coherent", 0 <= r_fsk - th_nc_db < 3.0, f"loss {r_fsk-th_nc_db:+.2f} dB")
check("discriminator 2-GFSK (h=0.5, BT=0.5) needs more Eb/N0 than ideal non-coherent", r_gfsk > th_nc_db, f"loss {r_gfsk-th_nc_db:+.2f} dB")

# ------------------------------------------------------------ 7. QPSK receiver (RRC + Gardner + Costas)
def rrc(beta, sps, span):
    t = np.arange(-span * sps, span * sps + 1) / sps
    h = np.zeros_like(t)
    for i, ti in enumerate(t):
        if abs(ti) < 1e-12:
            h[i] = 1 + beta * (4 / np.pi - 1)
        elif abs(abs(ti) - 1 / (4 * beta)) < 1e-9:
            h[i] = beta / np.sqrt(2) * ((1 + 2 / np.pi) * np.sin(np.pi / (4 * beta)) + (1 - 2 / np.pi) * np.cos(np.pi / (4 * beta)))
        else:
            h[i] = (np.sin(np.pi * ti * (1 - beta)) + 4 * beta * ti * np.cos(np.pi * ti * (1 + beta))) / (np.pi * ti * (1 - (4 * beta * ti) ** 2))
    return h / np.sqrt(np.sum(h ** 2))


def cubic(x, t):
    i = int(np.floor(t))
    mu = t - i
    xm1, x0, x1, x2 = x[i - 1], x[i], x[i + 1], x[i + 2]
    # cubic Lagrange (Farrow form)
    c0 = x0
    c1 = -xm1 / 3 - x0 / 2 + x1 - x2 / 6
    c2 = xm1 / 2 - x0 + x1 / 2
    c3 = -xm1 / 6 + x0 / 2 - x1 / 2 + x2 / 6
    return ((c3 * mu + c2) * mu + c1) * mu + c0


def qpsk_receiver_ber(ebn0_db, nsym=24000, sps=4, beta=0.35, tau=0.37, cfo=0.0015, ph0=1.0):
    bits = rng.integers(0, 2, 2 * nsym)
    sym = ((1 - 2 * bits[0::2]) + 1j * (1 - 2 * bits[1::2])) / np.sqrt(2)
    h = rrc(beta, sps, 8)
    up = np.zeros(nsym * sps, dtype=complex)
    up[::sps] = sym
    tx = np.convolve(up, h)
    # channel: fractional delay (via FFT phase ramp), CFO, phase, AWGN
    Nf = len(tx)
    f = np.fft.fftfreq(Nf)
    tx = np.fft.ifft(np.fft.fft(tx) * np.exp(-2j * np.pi * f * tau))
    nn = np.arange(Nf)
    tx = tx * np.exp(1j * (2 * np.pi * cfo * nn + ph0))
    es = np.mean(np.abs(tx) ** 2) * sps  # energy per symbol
    n0 = es / 2 / 10 ** (ebn0_db / 10)  # Eb = Es/2
    rx = tx + np.sqrt(n0 / 2) * (rng.standard_normal(Nf) + 1j * rng.standard_normal(Nf))
    y = np.convolve(rx, h)
    y /= np.sqrt(np.mean(np.abs(y) ** 2) * sps)  # AGC: unit symbol energy -> |sym|^2 ~ 1
    # loops
    t = len(h) - 1.0  # first on-time index guess: two RRCs each delay (len(h)-1)/2
    kp_t, ki_t = 0.02, 0.0005
    integ_t = 0.0
    phase, freq = 0.0, 0.0
    kp_c, ki_c = 0.08, 0.002
    prev = 0
    out = []
    while t < len(y) - 4:
        on = cubic(y, t)
        mid = cubic(y, t - sps / 2)
        # Gardner TED: e = Re{conj(y_mid) (y_on - y_prev)}; with the opposite sign the loop
        # locks stably on the zero crossings (mid-symbol) instead -- a classic bug
        e_t = np.real(np.conj(mid) * (on - prev)) if len(out) else 0.0
        prev = on
        integ_t += ki_t * e_t
        z = on * np.exp(-1j * phase)
        e_c = np.sign(z.real) * z.imag - np.sign(z.imag) * z.real
        freq += ki_c * e_c
        phase += freq + kp_c * e_c
        out.append(z)
        t += sps - (kp_t * e_t + integ_t)
    out = np.array(out)
    skip = 3000
    best = 1.0
    for rot in range(4):  # resolve 90-degree ambiguity
        zz = out[skip:] * 1j ** rot
        b_hat = np.empty(2 * len(zz), dtype=int)
        b_hat[0::2] = (zz.real < 0).astype(int)
        b_hat[1::2] = (zz.imag < 0).astype(int)
        # align with transmitted bits (symbol index offset search)
        for off in range(skip - 40, skip + 40):
            ref = bits[2 * off: 2 * off + len(b_hat)]
            L = min(len(ref), len(b_hat))
            if L < 10000:
                continue
            be = np.mean(ref[:L] != b_hat[:L])
            best = min(best, be)
    return best


def q(x):
    return 0.5 * special.erfc(x / np.sqrt(2))


for eb in (5.0, 7.0):
    ber = qpsk_receiver_ber(eb)
    th = q(np.sqrt(2 * 10 ** (eb / 10)))
    check(f"QPSK receiver (Gardner+Costas, tau=0.37 samp, CFO 1.5e-3 cyc/samp) BER @ {eb} dB", ber < 1.6 * th and ber > 0.5 * th,
          f"sim {ber:.2e} vs theory {th:.2e}")


# ------------------------------------------------------------ 8. LoRa dechirp SER
def lora_symbols(syms, SF):
    N = 2 ** SF
    n = np.arange(N)
    out = [np.exp(2j * np.pi * (n ** 2 / (2 * N) + (s / N - 0.5) * n)) for s in syms]
    return np.concatenate(out)


def lora_demod(x, SF, cfo_bins=0.0):
    N = 2 ** SF
    n = np.arange(N)
    down = np.exp(-2j * np.pi * (n ** 2 / (2 * N) - 0.5 * n))
    X = x.reshape(-1, N) * down
    return np.argmax(np.abs(np.fft.fft(X, axis=1)), axis=1)


def ser_noncoh_mfsk(M, esn0_db):
    g = 10 ** (esn0_db / 10)
    sg = np.sqrt(g)
    f = lambda u: 2 * u * np.exp(-(u - sg) ** 2) * special.i0e(2 * u * sg) * (1 - np.exp(-u * u)) ** (M - 1)
    val, _ = integrate.quad(f, 0, sg + 12, limit=400, points=[sg])
    return 1 - val


SF = 7
N = 2 ** SF
for snr in (-6.0, -8.0, -10.0):
    ns = 6000
    syms = rng.integers(0, N, ns)
    x = lora_symbols(syms, SF)
    sig = 10 ** (-snr / 10)  # noise variance per sample for unit-power signal
    y = x + np.sqrt(sig / 2) * (rng.standard_normal(len(x)) + 1j * rng.standard_normal(len(x)))
    ser = np.mean(lora_demod(y, SF) != syms)
    th = ser_noncoh_mfsk(N, snr + 10 * np.log10(N))
    tol = 0.2 if th > 0.02 else 0.35
    check(f"LoRa SF7 dechirp SER @ SNR {snr} dB (in BW)", abs(np.log10(max(ser, 1e-5)) - np.log10(th)) < tol, f"sim {ser:.3e} vs exact M-FSK {th:.3e}")

# ------------------------------------------------------------ 9. LoRa CFO
syms = rng.integers(0, N, 200)
x = lora_symbols(syms, SF)
cfo = 1.0 / N  # one bin (= BW/2^SF Hz)
xc = x * np.exp(2j * np.pi * cfo * np.arange(len(x)))
d = lora_demod(xc, SF)
check("LoRa: CFO of one bin (BW/2^SF) shifts every symbol by +1", np.all((d - syms) % N == 1))
# estimate from 8 preamble upchirps (symbol 0) and correct
pre = lora_symbols([0] * 8, SF) * np.exp(2j * np.pi * (3.3 / N) * np.arange(8 * N))
nn = np.arange(N)
Xp = np.fft.fft(pre.reshape(-1, N) * np.exp(-2j * np.pi * (nn ** 2 / (2 * N) - 0.5 * nn)), 16 * N, axis=1)
est = np.argmax(np.mean(np.abs(Xp) ** 2, axis=0)) / 16
check("preamble-based CFO estimate (zero-padded dechirp FFT)", abs(est - 3.3) < 0.07, f"{est:.3f} bins (true 3.3)")

# ------------------------------------------------------------ 10. end-to-end GFSK packet pipeline
def crc16_ccitt_false(data):
    crc = 0xFFFF
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


check("CRC-16/CCITT-FALSE check value 0x29B1", crc16_ccitt_false(b"123456789") == 0x29B1)


def crc16_x25(data):
    """AX.25 FCS: reflected poly 0x8408 (0x1021 reversed), init 0xFFFF, final XOR 0xFFFF."""
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0x8408 if crc & 1 else crc >> 1
    return crc ^ 0xFFFF


check("CRC-16/X-25 (AX.25 FCS) check value 0x906E", crc16_x25(b"123456789") == 0x906E)


def bytes_to_bits(bs):
    return np.array([(b >> (7 - i)) & 1 for b in bs for i in range(8)], dtype=int)


def bits_to_bytes(bits):
    return bytes(int("".join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits) - 7, 8))


SYNC = bytes([0x2D, 0xD4])
Rb, spsb = 9600, 10
fsp = Rb * spsb
h_mod, BT = 1.0, 0.5


def make_packet(payload):
    body = bytes([len(payload)]) + payload
    crc = crc16_ccitt_false(body)
    frame = bytes([0xAA] * 4) + SYNC + body + bytes([crc >> 8, crc & 0xFF])
    return bytes_to_bits(frame)


def rx_packet(y):
    lp = signal.firwin(81, 14e3, fs=fsp)  # pre-detection filter (Carson ~ (h+1)Rb = 19.2 kHz + CFO margin)
    yf = signal.lfilter(lp, 1, y)[40:]
    f = np.angle(yf[1:] * np.conj(yf[:-1]))
    # burst detection by power, DC (CFO) removal using the burst mean
    pw = np.convolve(np.abs(yf[1:]) ** 2, np.ones(spsb * 8) / (spsb * 8), mode="same")
    on = pw > 0.5 * np.max(pw)
    idx = np.flatnonzero(on)
    # widen the detected burst: the power detector's edges are fuzzy, and cutting the tail
    # truncates the CRC (an actual bug found while writing this check)
    st0, en0 = max(idx[0] - 4 * spsb, 0), min(idx[-1] + 4 * spsb, len(f))
    f = f[st0:en0]
    # CFO: mean discriminator output over the 1010... preamble (balanced -> unbiased)
    f = f - np.mean(f[6 * spsb: 26 * spsb])
    mf = np.convolve(f, np.ones(spsb) / spsb, mode="same")  # integrate over a bit
    # timing: pick the sampling phase with the largest mean |eye| over the preamble
    ph = max(range(spsb), key=lambda k: np.mean(np.abs(mf[6 * spsb + k: 26 * spsb: spsb])))
    bits = (mf[ph::spsb] > 0).astype(int)
    sync_bits = bytes_to_bits(SYNC)
    for i in range(len(bits) - 16):
        if np.sum(bits[i:i + 16] != sync_bits) <= 1:
            st = i + 16
            L = int("".join(map(str, bits[st:st + 8])), 2)
            body_bits = bits[st: st + 8 * (L + 1)]
            crc_bits = bits[st + 8 * (L + 1): st + 8 * (L + 3)]
            if len(crc_bits) < 16:
                return None
            body = bits_to_bytes(body_bits)
            crc_rx = int("".join(map(str, crc_bits)), 2)
            return body[1:] if crc16_ccitt_false(body) == crc_rx else None
    return None


def run_link(ebn0_db, npk=40):
    good = 0
    for _ in range(npk):
        payload = bytes(rng.integers(0, 256, 20).tolist())
        bits = make_packet(payload)
        x = fsk_mod(bits, spsb, h_mod, BT)
        # channel: random start, fractional timing (via resampling offset), CFO 2 kHz, AWGN
        lead = int(rng.integers(200, 600))
        x = np.concatenate([np.zeros(lead), x, np.zeros(300)])
        tau = rng.uniform(0, 1)
        Nf = len(x)
        fr = np.fft.fftfreq(Nf)
        x = np.fft.ifft(np.fft.fft(x) * np.exp(-2j * np.pi * fr * tau * spsb / 2))
        x = x * np.exp(2j * np.pi * 2000 / fsp * np.arange(Nf) + 1j * rng.uniform(0, 6.28))
        n0 = spsb / 10 ** (ebn0_db / 10)
        y = x + np.sqrt(n0 / 2) * (rng.standard_normal(Nf) + 1j * rng.standard_normal(Nf))
        got = rx_packet(y)
        good += got == payload
    return 1 - good / npk


curve = {eb: run_link(eb, npk=60) for eb in (9.0, 11.0, 12.0, 13.0, 14.0)}
per14, per9 = curve[14.0], curve[9.0]
print("      GFSK telemetry frame (29 bytes, 9.6 kbit/s, h=1, BT=0.5, 2 kHz CFO), PER vs Eb/N0: " +
      ", ".join(f"{k:.0f} dB: {v:.2f}" for k, v in curve.items()))
check("end-to-end packet pipeline decodes and CRC-checks frames at 14 dB", per14 <= 0.05)
check("PER rises at 9 dB (sanity: the CRC catches errors)", per9 > per14)

print("\nALL PASS" if ok_all else "\nSOME FAIL")
