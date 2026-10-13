#!/usr/bin/env python3
"""Verification for kb/10-comms-modulation/pulse-shaping-isi.md

Run:  python3 tools/verify/comms_pulse_shaping.py      (~20 s)

Checks:
  1. Raised-cosine (RC) impulse response has zeros at every nonzero multiple of T (Nyquist ISI
     criterion), for beta = 0 ... 1; the folded spectrum sum_k P(f - k/T) is flat.
  2. RRC (*) RRC == RC: cascade of two truncated RRC filters gives ISI below -40 dB at span 8.
  3. Occupied bandwidth: RC spectrum is exactly zero beyond (1+beta)/(2T) (one-sided baseband);
     truncation of RRC to +-L symbols raises out-of-band power (quantified).
  4. Eye opening vs sampling offset for beta = 0.2, 0.35, 0.5 (worst-case, binary).
  5. ISI from a two-path channel and equalisers: no EQ vs zero-forcing (ZF) linear FIR vs MMSE
     linear FIR vs decision-feedback (DFE), BPSK, symbol-spaced.
"""
import numpy as np
from scipy import special

rng = np.random.default_rng(5)
ok_all = True


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel else 1.0)
    ok = err <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.5g}, expected {want:.5g} (tol {tol}{' rel' if rel else ''})")


def rc(t, beta):
    t = np.asarray(t, float)
    out = np.sinc(t) * np.ones_like(t)
    if beta > 0:
        den = 1 - (2 * beta * t) ** 2
        sing = np.abs(den) < 1e-10
        out = np.where(sing, np.pi / 4 * np.sinc(1 / (2 * beta)), np.sinc(t) * np.cos(np.pi * beta * t) / np.where(sing, 1, den))
    return out


def rrc(t, beta):
    t = np.asarray(t, float)
    h = np.empty_like(t)
    for i, x in enumerate(t):
        if abs(x) < 1e-12:
            h[i] = 1 - beta + 4 * beta / np.pi
        elif beta > 0 and abs(abs(x) - 1 / (4 * beta)) < 1e-12:
            h[i] = beta / np.sqrt(2) * ((1 + 2 / np.pi) * np.sin(np.pi / (4 * beta)) + (1 - 2 / np.pi) * np.cos(np.pi / (4 * beta)))
        else:
            h[i] = (np.sin(np.pi * x * (1 - beta)) + 4 * beta * x * np.cos(np.pi * x * (1 + beta))) / (np.pi * x * (1 - (4 * beta * x) ** 2))
    return h


def rc_spectrum(f, beta):
    f = np.abs(np.asarray(f, float))
    f1 = (1 - beta) / 2
    f2 = (1 + beta) / 2
    return np.where(f <= f1, 1.0, np.where(f <= f2, 0.5 * (1 + np.cos(np.pi / max(beta, 1e-12) * (f - f1))), 0.0))

# ------------------------------------------------------------------------------ 1
n = np.arange(-20, 21)
for beta in (0.0, 0.2, 0.35, 0.5, 1.0):
    v = rc(n, beta)
    isi = np.max(np.abs(v[n != 0]))
    check(f"RC beta={beta}: max |p(nT)|, n!=0", isi, 0.0, 1e-12)
    f = np.linspace(-0.5, 0.5, 1001)[1:-1]   # open interval (band-edge points are measure-zero)
    fold = sum(rc_spectrum(f - k, beta) for k in range(-3, 4))
    check(f"RC beta={beta}: folded spectrum flat (max dev)", np.max(np.abs(fold - 1)), 0.0, 1e-9)
check("RC beta=0.35 spectrum zero beyond (1+b)/2T", float(rc_spectrum(0.6751, 0.35)), 0.0, 1e-12)

# ------------------------------------------------------------------------------ 2
sps = 16
for span in (4, 8, 16):
    tt = np.arange(-span * sps, span * sps + 1) / sps
    h = rrc(tt, 0.35)
    h /= np.sqrt(np.sum(h ** 2))
    c = np.convolve(h, h)
    mid = len(c) // 2
    samples = c[mid::sps][1:]
    samples = np.concatenate((c[mid::-sps][1:], samples))
    isi_db = 10 * np.log10(np.sum(samples ** 2) / c[mid] ** 2)
    # out-of-band power of one truncated RRC relative to total (beyond (1+b)/2 * 1.05)
    H = np.fft.fftshift(np.abs(np.fft.fft(h, 65536)) ** 2)
    fr = np.fft.fftshift(np.fft.fftfreq(65536, 1 / sps))
    oob = 10 * np.log10(np.sum(H[np.abs(fr) > 0.675 * 1.05]) / np.sum(H))
    print(f"  RRC beta=0.35, span +-{span} symbols: RRC*RRC ISI power {isi_db:6.1f} dB, one-filter out-of-band power {oob:6.1f} dB")
    if span == 8:
        ok = isi_db < -40
        ok_all &= ok
        print(f"[{'PASS' if ok else 'FAIL'}] span 8 -> ISI < -40 dB")

# ------------------------------------------------------------------------------ 4
bits = rng.integers(0, 2, 4000) * 2 - 1.0
print("  worst-case eye opening (binary, RC pulse) vs sampling offset:")
for beta in (0.2, 0.35, 0.5, 1.0):
    row = []
    for off in (0.0, 0.1, 0.2, 0.3):
        k = np.arange(-30, 31)
        p = rc(k + off, beta)
        opening = p[k == 0][0] - np.sum(np.abs(p[k != 0]))    # worst-case over all data patterns
        row.append(opening)
    print(f"    beta={beta:4.2f}: " + "  ".join(f"off {o:.1f}T -> {v:6.3f}" for o, v in zip((0, .1, .2, .3), row)))
    if beta == 0.35:
        eye35 = row
check("RC beta=0.35 eye fully open at ideal sampling", eye35[0], 1.0, 1e-9)
ok = eye35[1] > 0.5 and eye35[3] < eye35[1]
ok_all &= ok
print(f"[{'PASS' if ok else 'FAIL'}] eye closes monotonically with offset for beta=0.35")

# ------------------------------------------------------------------------------ 5
chan = np.array([1.0, 0.0, 0.6])   # two-path, echo 2 symbols later at -4.4 dB
chan /= np.linalg.norm(chan)
nb = 400_000
ebn0_db = 10.0
g = 10 ** (ebn0_db / 10)
sigma = np.sqrt(1 / (2 * g))
b = rng.integers(0, 2, nb) * 2 - 1.0
x = np.convolve(b, chan)[:nb]
y = x + sigma * rng.standard_normal(nb)


def ber(dec, delay=0):
    return np.mean(np.sign(dec[delay:nb]) != b[:nb - delay])


pb_awgn = 0.5 * special.erfc(np.sqrt(g))
# no equaliser: slice directly (main tap is first)
ber_none = ber(y)
# linear equalisers, Ntap taps, decision delay D
Ntap, D = 21, 10
Hm = np.zeros((Ntap, Ntap + len(chan) - 1))
for i in range(Ntap):
    Hm[i, i:i + len(chan)] = chan[::-1]
Hm = Hm[:, ::-1][::-1]           # convolution matrix: y_vec = Hm @ b_vec (time-reversed stacking)
# build explicitly for clarity: y[n-i] = sum_j chan[j] b[n-i-j]
L = Ntap + len(chan) - 1
Hc = np.zeros((Ntap, L))
for i in range(Ntap):
    for j, cj in enumerate(chan):
        Hc[i, i + j] = cj
e_D = np.zeros(L)
e_D[D] = 1
w_zf = np.linalg.lstsq(Hc.T, e_D, rcond=None)[0]                  # least-squares ZF
w_mmse = np.linalg.solve(Hc @ Hc.T + sigma ** 2 * np.eye(Ntap), Hc @ e_D)
Y = np.lib.stride_tricks.sliding_window_view(y, Ntap)[:, ::-1]   # rows: [y[n], y[n-1], ...]
z_zf = Y @ w_zf
z_mmse = Y @ w_mmse
# align: output index m corresponds to n = m + Ntap - 1; estimates b[n - D]
bz = b[Ntap - 1 - D: Ntap - 1 - D + len(z_zf)]
ber_zf = np.mean(np.sign(z_zf) != bz)
ber_mmse = np.mean(np.sign(z_mmse) != bz)
noise_enh_zf = 10 * np.log10(np.sum(w_zf ** 2) / (w_zf @ Hc[:, D]) ** 2)
# DFE: feed-forward = 1 tap (main path first), feedback cancels post-cursor ISI with past decisions
dec = np.zeros(nb)
for n_ in range(nb):
    fb = sum(chan[j] * dec[n_ - j] for j in range(1, len(chan)) if n_ - j >= 0)
    dec[n_] = 1.0 if (y[n_] - fb) >= 0 else -1.0
ber_dfe = np.mean(dec != b)
print(f"  two-path channel {chan.round(3)}, Eb/N0 = {ebn0_db} dB (AWGN BPSK would give {pb_awgn:.2e}):")
print(f"    no EQ {ber_none:.2e} | ZF-21 {ber_zf:.2e} (noise enhancement {noise_enh_zf:.2f} dB) | MMSE-21 {ber_mmse:.2e} | DFE {ber_dfe:.2e}")
ok = ber_none > 5 * ber_mmse and ber_mmse <= ber_zf * 1.05 and ber_dfe < ber_zf
ok_all &= ok
print(f"[{'PASS' if ok else 'FAIL'}] EQ ordering: none >> MMSE <= ZF, DFE < ZF")
# matched-filter bound for this channel: all energy collected -> AWGN BPSK at same Eb/N0 (||chan||=1)
print(f"    matched-filter bound (energy of both paths collected) = AWGN BPSK {pb_awgn:.2e}")

print("\nOVERALL:", "PASS" if ok_all else "FAIL")
