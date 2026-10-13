#!/usr/bin/env python3
"""Myth check: "zeroing FFT bins is a good (brick-wall) filter".  (W5-E1, 2026-09-29)

Demonstrates numerically why block-FFT -> zero bins -> IFFT is a poor filter, and what to do instead.
Setup: fs = 1 (normalised), N = 1024-point blocks, keep bins |k| <= 200 (cutoff 0.195 fs).

  1. Integer-bin test tones are rejected perfectly  -> why the trick *looks* perfect in toy tests.
  2. A real (off-bin) interferer 100 bins beyond the cutoff is rejected by only ~30-35 dB, because the
     rectangular block window smears it over every bin (Dirichlet leakage ~ 1/(pi*m)), and the leaked
     part in the kept bins survives.
  3. Equivalent response: bin-zeroing is a *time-varying* operation (circular convolution with a periodic
     sinc within each block); for off-bin tones the swept "stopband" is only about -20 dB just past the
     edge, -27 dB 50 bins away and -31 dB 100 bins away (worst-case half-bin offsets).
  4. Streaming block-by-block creates discontinuities at every block boundary (error concentrated at the
     edges), i.e. spurs at multiples of fs/N.
  5. The correct FFT-domain filter: design a linear-phase FIR (Kaiser window) and apply it by overlap-save
     (fast convolution).  Same FFT machinery, > 80 dB stopband, no block-edge artefacts, and it matches
     direct convolution to ~1e-12.
Run: python3 tools/verify/fix_fft_bin_zeroing.py  -> ALL PASS
"""
import numpy as np
from scipy import signal

N = 1024
KEEP = 200                                   # keep bins 0..200 and N-200..N-1 (real low-pass)
FC = KEEP / N                                # 0.1953 cycles/sample


def zero_bins_block(x):
    X = np.fft.fft(x)
    X[KEEP + 1:N - KEEP] = 0.0
    return np.fft.ifft(X).real


def stream_zero_bins(x):
    y = np.zeros_like(x)
    for i in range(0, len(x) - N + 1, N):
        y[i:i + N] = zero_bins_block(x[i:i + N])
    return y


def db(p):
    return 10 * np.log10(p)


def tone(fbin, n, phase=0.3):
    t = np.arange(n)
    return np.cos(2 * np.pi * fbin / N * t + phase)


def main():
    ok = True
    # 1. integer-bin interferer: perfect rejection (the misleading demo)
    x = tone(300.0, N)
    y = zero_bins_block(x)
    rej_int = db(np.mean(x ** 2) / max(np.mean(y ** 2), 1e-300))
    print(f"1. interferer at bin 300.0 (on a bin centre): rejection {rej_int:.0f} dB  <- looks 'brick-wall'")
    assert rej_int > 200

    # 2. off-bin interferer 100 bins past the cutoff
    x = tone(300.5, N)
    y = zero_bins_block(x)
    rej_off = db(np.mean(x ** 2) / np.mean(y ** 2))
    print(f"2. interferer at bin 300.5 (half-bin offset): rejection only {rej_off:.1f} dB")
    assert 25 < rej_off < 40

    # 3. swept-tone response of bin-zeroing (single block, average over random phases)
    rng = np.random.default_rng(1)
    fb = np.arange(150.0, 260.0, 0.25)
    resp = []
    for f in fb:
        acc = []
        for ph in rng.uniform(0, 2 * np.pi, 8):
            xin = tone(f, N, ph)
            acc.append(np.mean(zero_bins_block(xin) ** 2) / np.mean(xin ** 2))
        resp.append(db(np.mean(acc)))
    resp = np.array(resp)
    pb = resp[fb <= 190]
    sb10 = resp[(fb >= 210) & (fb % 1 == 0.5)]
    sb50 = resp[(fb >= 250) & (fb % 1 == 0.5)]
    print(f"3. swept response: passband ripple {pb.max() - pb.min():.2f} dB (bins 150-190); "
          f"stopband 10-15 bins past edge {sb10[:20].max():.1f} dB; 50 bins past edge {sb50.max():.1f} dB")
    assert sb10[:20].max() > -30      # only ~ -20..-25 dB just past the edge
    assert sb50.max() > -45

    # 4. streaming: block-edge discontinuities for an in-band off-bin tone
    L = 16 * N
    x = tone(50.37, L)
    y = stream_zero_bins(x)
    err = np.abs(y - x)
    edge = np.concatenate([err[i - 8:i + 8] for i in range(N, L - N, N)])
    mid = np.concatenate([err[i + N // 2 - 8:i + N // 2 + 8] for i in range(0, L - N, N)])
    ratio_edge_mid = edge.max() / mid.max()
    print(f"4. streaming an in-band tone (bin 50.37): max error at block edges {edge.max():.3f} vs mid-block "
          f"{mid.max():.4f} (x{ratio_edge_mid:.0f}) -> spurs at multiples of fs/N")
    assert ratio_edge_mid > 5

    # 5. the right way: Kaiser FIR + overlap-save with the same FFT size
    ntaps = 255
    h = signal.firwin(ntaps, cutoff=2 * (FC + 0.011), window=("kaiser", 8.6))  # pass edge ~FC, stop from ~FC+0.022
    # overlap-save
    M = ntaps
    step = N - (M - 1)
    H = np.fft.fft(h, N)
    L2 = 40 * N
    rng = np.random.default_rng(2)
    xs = tone(120.3, L2) + 1.0 * tone(300.5, L2, 1.1) + 0.01 * rng.standard_normal(L2)
    xpad = np.concatenate([np.zeros(M - 1), xs])
    out = []
    for i in range(0, len(xpad) - N + 1, step):
        yb = np.fft.ifft(np.fft.fft(xpad[i:i + N]) * H).real
        out.append(yb[M - 1:])
    yos = np.concatenate(out)[:L2 - N]
    ydirect = signal.lfilter(h, 1.0, xs)[:len(yos)]
    agree = np.max(np.abs(yos - ydirect))
    w, Hf = signal.freqz(h, worN=8192)
    fnorm = w / (2 * np.pi)
    stop = 20 * np.log10(np.abs(Hf[fnorm >= FC + 0.023]) + 1e-15).max()
    pas = 20 * np.log10(np.abs(Hf[fnorm <= FC - 0.001]))
    pripple = pas.max() - pas.min()
    rej_fir = -20 * np.log10(np.abs(Hf[np.argmin(np.abs(fnorm - 300.5 / N))]))
    print(f"5. Kaiser FIR ({ntaps} taps) via overlap-save: passband ripple {pripple:.4f} dB, stopband <= {stop:.1f} dB, rejection at bin 300.5 "
          f"{rej_fir:.0f} dB; overlap-save vs direct convolution max diff {agree:.1e}")
    assert stop < -80 and rej_fir > 80 and agree < 1e-9 and pripple < 0.01

    print("\nSummary: bin-zeroing gives ~%.0f dB against a real off-bin interferer 100 bins away; a proper FIR "
          "applied with the same FFTs gives > 80 dB." % rej_off)
    print("ALL PASS" if ok else "FAIL")


if __name__ == "__main__":
    main()
