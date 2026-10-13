#!/usr/bin/env python3
"""
array_architecture.py — verification for kb/12-phased-arrays/beamforming-architectures.md

  1. Digital beamforming: SNR improvement 10logN with independent channel noise (thermal + ADC quantisation);
     uncorrelated spurs (random phase per channel) improve 10logN relative to the beamformed signal;
     correlated spurs (same phase in all channels, e.g. shared clock/LO leakage) appear as a broadside source.
  2. Nonlinear products in a digital array: the 2nd/3rd harmonic of a signal arriving from theta0 has phase
     progression 2x/3x -> it "arrives" from a different apparent direction and is spatially filtered.
  3. LO phase noise: shared LO (fully correlated) vs independent LOs (uncorrelated): beamformed carrier-to-
     phase-noise ratio improves 10logN only for uncorrelated LOs; mixture with correlation rho.
  4. Butler matrix as a spatial DFT: beam directions u_m = (m - 1/2) lambda/(N d), orthogonality, crossover level
     vs N (-3.70 dB N=4, -3.87 N=8 -> -3.92 dB), comparison with a glossary claim (-3.0 dB for N=8).
  5. Analog RF combining noise cascade: element LNA + lossy phase shifter + ideal N:1 combiner + receiver,
     array SNR vs per-element SNR; importance of LNA gain before the beamformer loss.
  6. Synchronisation numbers: sample-clock skew -> phase error at baseband offset; LO frequency offset between
     free-running receivers; ADC aperture-jitter SNR; digital-array data rates.
"""
import numpy as np

rng = np.random.default_rng(5)
c0 = 299792458.0

print("=" * 78)
print("1. Digital beamforming: noise, quantisation, spurs")
fs = 1.0
M = 1 << 16
t = np.arange(M)
for N in (2, 4, 8, 16):
    d = 0.5
    th0 = np.radians(20)
    ph = 2 * np.pi * d * np.arange(N) * np.sin(th0)  # arrival phase
    f0 = 0.1234
    s = np.exp(1j * (2 * np.pi * f0 * t[:, None] + ph[None, :]))  # unit tone
    snr_in_db = 10.0
    sig_n = 10 ** (-snr_in_db / 20)
    noise = sig_n * (rng.standard_normal((M, N)) + 1j * rng.standard_normal((M, N))) / np.sqrt(2)
    # ADC quantisation (8-bit-ish on I and Q, full scale 2)
    x = s + noise
    q = 2 / 2 ** 8
    xq = np.round(x.real / q) * q + 1j * np.round(x.imag / q) * q
    # uncorrelated spur: tone at f_sp with random phase per channel, -40 dBc
    f_sp = 0.3011
    spur_unc = 10 ** (-40 / 20) * np.exp(1j * (2 * np.pi * f_sp * t[:, None] + rng.uniform(0, 2 * np.pi, N)[None, :]))
    # correlated spur: same phase on all channels (e.g. clock leakage), -40 dBc, at f_c
    f_c = 0.4017
    spur_cor = 10 ** (-40 / 20) * np.exp(1j * 2 * np.pi * f_c * t)[:, None] * np.ones(N)[None, :]
    y = xq + spur_unc + spur_cor
    w = np.exp(-1j * ph) / N
    b = y @ w
    win = np.hanning(M)
    Y = np.fft.fft(b * win)
    Y1 = np.fft.fft(y[:, 0] * win)
    fr = np.fft.fftfreq(M)
    def lvl(Z, f):
        k = int(np.round(f * M)) % M
        return 20 * np.log10(np.max(np.abs(Z[k - 2:k + 3])))
    def nfloor(Z):
        mask = np.ones(M, bool)
        for f in (f0, f_sp, f_c):
            k = int(np.round(f * M)) % M
            mask[max(0, k - 50):k + 50] = False
        return 10 * np.log10(np.mean(np.abs(Z[mask]) ** 2))
    c1, cN = lvl(Y1, f0), lvl(Y, f0)
    impr = (nfloor(Y1) - c1) - (nfloor(Y) - cN)
    # uncorrelated spur: expected beamformed power over many random-phase draws = 1/N of a coherent one
    draws = np.exp(1j * rng.uniform(0, 2 * np.pi, (4000, N)))
    unc = 10 * np.log10(np.mean(np.abs(draws @ w) ** 2))  # relative to a unit coherent signal (|w^H v| = 1)
    AFbs = 20 * np.log10(abs(np.sum(w)))  # correlated (zero-phase-ramp) spur through the 20° beam
    print(f"  N={N:2d}: noise-floor improvement {impr:5.2f} dB (10logN = {10*np.log10(N):.2f}); "
          f"uncorrelated spur (mean of 4000 phase draws) {unc:6.2f} dB rel. single-channel level; "
          f"correlated spur through a 20° beam {AFbs:6.2f} dB (= AF toward broadside)")
    # repeat with beam at broadside: correlated spur not suppressed
    if N == 8:
        w0 = np.ones(N) / N
        th0b = 0.0
        s0 = np.exp(1j * 2 * np.pi * f0 * t)[:, None] * np.ones(N)[None, :]
        y0 = s0 + noise + spur_cor + spur_unc
        Y0 = np.fft.fft((y0 @ w0) * win)
        print(f"      beam at broadside (signal also broadside): correlated spur {lvl(Y0,f_c)-lvl(Y0,f0):6.1f} dBc (no array suppression)")

print("=" * 78)
print("2. Harmonics in a digital array are steered elsewhere (N=8, d=λ/2 at the fundamental)")
N = 8
x = np.arange(N) * 0.5
for th0d in (10, 20, 30):
    u0 = np.sin(np.radians(th0d))
    for h in (2, 3):
        # element-level harmonic has phase h * (k x u0); beamformer weights for the fundamental steer to u0 at the harmonic's frequency?
        # In a digital (baseband) beamformer the harmonic appears at baseband frequency h*f; weights are frequency-independent phases.
        # gain of beam (steered to u0 with phases -k x u0) for a component with phase progression h*k x u0:
        g = np.abs(np.sum(np.exp(1j * 2 * np.pi * x * (h - 1) * u0))) / N
        # apparent direction of the harmonic's phase progression (at fundamental-λ spacing): sin = h u0 (mod aliasing)
        app = (h * u0 + 1) % 2 - 1
        print(f"  θ0={th0d}°: H{h} relative array gain in the beam = {20*np.log10(max(g,1e-12)):7.2f} dB; apparent sinθ of H{h} phase ramp = {app:+.3f}")

print("=" * 78)
print("3. LO phase noise: shared vs independent LOs (Monte Carlo)")
M = 1 << 15
for N in (4, 8, 16):
    for rho in (1.0, 0.0, 0.5):
        # phase noise: common part sqrt(rho) + independent part sqrt(1-rho), small-angle, white-ish (filtered)
        sig = 0.05
        common = sig * rng.standard_normal(M)
        indep = sig * rng.standard_normal((M, N))
        phi = np.sqrt(rho) * common[:, None] + np.sqrt(1 - rho) * indep
        y = np.exp(1j * phi)  # carrier at DC after mixing, steering already removed
        b = y.mean(axis=1)
        # carrier-to-phase-noise: carrier power |mean(b)|^2, noise = var(b)
        cpn1 = np.abs(np.mean(y[:, 0])) ** 2 / np.var(y[:, 0])
        cpnN = np.abs(np.mean(b)) ** 2 / np.var(b)
        print(f"  N={N:2d} ρ={rho:.1f}: carrier/phase-noise improvement {10*np.log10(cpnN/cpn1):6.2f} dB "
              f"(theory 10log(N/(1+(N-1)ρ)) = {10*np.log10(N/(1+(N-1)*rho)):6.2f} dB)")

print("=" * 78)
print("4. Butler matrix = spatial DFT")
for N in (4, 8, 16, 64):
    d = 0.5
    x = np.arange(N) * d
    # Butler beam m: progressive phase (2m-1)pi/N  -> u_m = (2m-1)/(2 N d) * lambda  (lambda = 1)
    ms = np.arange(-N // 2 + 1, N // 2 + 1)
    um = (2 * ms - 1) / (2 * N * d)
    W = np.exp(-1j * 2 * np.pi * np.outer(um, x)) / np.sqrt(N)  # rows = beam weight vectors
    orth = np.max(np.abs(W @ W.conj().T - np.eye(N)))
    # crossover between adjacent beams
    uc = (um[N // 2 - 1] + um[N // 2]) / 2
    AF = np.abs(np.sum(np.exp(1j * 2 * np.pi * x * (uc - um[N // 2])))) / N
    beams_deg = np.degrees(np.arcsin(np.clip(um, -1, 1)))
    print(f"  N={N:2d}: max|W W^H - I| = {orth:.1e}; crossover {20*np.log10(AF):6.2f} dB; "
          f"beam directions (deg) {np.round(beams_deg[:min(N,8)],1)}{' ...' if N>8 else ''}")
print(f"  large-N limit 20log(2/π) = {20*np.log10(2/np.pi):.2f} dB (glossary claim of -3.0 dB for N=8 is not reproduced by the array factor)")

print("=" * 78)
print("5. Analog RF beamformer noise cascade (per-element LNA -> phase shifter/VGA -> N:1 combiner -> receiver)")


def cascade_nf(stages):
    """stages: list of (gain_dB, nf_dB); returns total NF dB (Friis)."""
    F = 1.0
    G = 1.0
    for i, (g, nf) in enumerate(stages):
        f = 10 ** (nf / 10)
        F = f if i == 0 else F + (f - 1) / G
        G *= 10 ** (g / 10)
    return 10 * np.log10(F)


for N in (4, 8, 16, 64):
    for lna_gain in (0, 15, 25):
        # element path: LNA (G, NF 1.5 dB) if gain>0; beamformer channel loss 8 dB (NF 8 dB)
        # ideal combiner: coherent signal gain N (power) relative to one channel's output; uncorrelated noise adds.
        # Post-combiner receiver NF 10 dB. Compute array output SNR relative to single element input SNR.
        kT = 1.0
        P_s_in = 1.0  # per element signal power
        chain = ([(lna_gain, 1.5)] if lna_gain > 0 else []) + [(-8.0, 8.0)]
        g_el = 10 ** (sum(g for g, _ in chain) / 10)
        F_el = 10 ** (cascade_nf(chain) / 10)
        # noise at combiner output from elements: N * kT F_el g_el / N? For a lossless N:1 (Wilkinson) combiner, each input
        # couples with 1/N power: signal (coherent) out = N * P_s g_el ; noise out = N * (kT F_el g_el) / N = kT F_el g_el
        sig_out = N * P_s_in * g_el
        noise_out = kT * F_el * g_el
        # receiver after combiner, NF 10 dB referred to its input: adds kT (F_rx - 1)
        noise_out += kT * (10 ** (10 / 10) - 1)
        snr_gain = (sig_out / noise_out) / (P_s_in / kT)
        print(f"  N={N:2d}, element LNA gain {lna_gain:2d} dB: array SNR / element-input SNR = {10*np.log10(snr_gain):6.2f} dB "
              f"(ideal 10logN = {10*np.log10(N):5.2f} dB); element-chain NF {cascade_nf(chain):5.2f} dB")

print("=" * 78)
print("6. Synchronisation and data-rate numbers")
for skew_ps, fbb in ((100, 1e6), (100, 20e6), (1000, 20e6), (10000, 1e6)):
    print(f"  sample-time skew {skew_ps} ps at baseband offset {fbb/1e6:.0f} MHz -> phase error {360*fbb*skew_ps*1e-12:.3f}°")
for f in (433e6, 915e6, 2.44e9, 5.8e9):
    for ppm in (1, 20):
        print(f"  free-running LOs, {ppm} ppm apart at {f/1e6:.0f} MHz: beat {f*ppm*1e-6:9.0f} Hz -> relative phase rotates 360° every {1e3/(f*ppm*1e-6):.3f} ms")
for fin, jit in ((10e6, 1e-12), (100e6, 1e-12), (1e9, 100e-15), (2.4e9, 50e-15)):
    print(f"  ADC aperture jitter {jit*1e15:.0f} fs at {fin/1e6:.0f} MHz: SNR limit {-20*np.log10(2*np.pi*fin*jit):.1f} dB")
for name, Nch, fs_, bits in (("KrakenSDR", 5, 2.4e6, 8), ("Phaser/Pluto (2 ch)", 2, 30.72e6, 12), ("8 ch AD9361-class", 8, 61.44e6, 12),
                            ("64 ch digital array", 64, 250e6, 14)):
    rate = Nch * fs_ * 2 * bits
    print(f"  {name:22s}: {Nch} ch × {fs_/1e6:.2f} MS/s × 2 (IQ) × {bits} bit = {rate/1e9:.3f} Gb/s raw")
print("done")
