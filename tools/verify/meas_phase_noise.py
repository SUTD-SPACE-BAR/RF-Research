#!/usr/bin/env python3
"""
meas_phase_noise.py -- numerical checks for kb/17-test-measurement/phase-noise-measurement.md

1. Direct spectrum-analyzer method on a synthetic oscillator with known L(f):
   simulate phase noise, compute a log-averaged spectrum with a Gaussian RBW, apply
   L = P_offset - P_carrier - 10 log(ENBW) + 2.51 dB, compare with the truth.
2. Analyzer LO phase-noise floor: reading error when the DUT is only X dB above the analyzer.
3. Delay-line frequency discriminator: transfer |H|^2 = 4 sin^2(pi f tau) relative to a
   phase detector; nulls at f = n/tau; close-in sensitivity loss.
4. Two-channel cross-correlation: averaging m cross-spectra lowers the uncorrelated background
   as ~5 log10(m) dB (Rubiola & Vernotte); simulated.
5. Frequency multiplication: L at N*f0 = L(f0) + 20 log N (e.g. 32 MHz TCXO -> 915 MHz PLL).
6. RBW / offset rule: how close to the carrier a given RBW can measure (Gaussian skirt).

Run: python3 tools/verify/meas_phase_noise.py
"""
import numpy as np

rng = np.random.default_rng(3)


def dbp(x):
    return 10 * np.log10(x)


# ---------------------------------------------------------------- 1. direct SA method
print("=== 1. Direct SA method on a synthetic oscillator ===")
fs = 2.048e6
n = 2 ** 22
f = np.fft.rfftfreq(n, 1 / fs)
# target single-sideband L(f): -90 dBc/Hz at 10 kHz, 1/f^2 (-20 dB/dec) between 300 Hz and the -135 dBc/Hz floor
L_true = lambda ff: 10 * np.log10(10 ** ((-90 - 20 * np.log10(np.maximum(ff, 300) / 1e4)) / 10) + 10 ** (-135 / 10))
S_phi = 2 * 10 ** (L_true(f) / 10)            # rad^2/Hz, S_phi = 2 L (small angle)
S_phi[0] = 0
# synthesize phi(t) with one-sided PSD S_phi: amplitude per bin
amp = np.sqrt(S_phi * fs * n / 2)
spec = amp * np.exp(1j * rng.uniform(0, 2 * np.pi, len(f)))
phi = np.fft.irfft(spec, n=n)
v = np.exp(1j * phi)                            # carrier at baseband (0 Hz), unit power
V = np.fft.fft(v * np.hanning(n)) / np.sqrt(np.sum(np.hanning(n) ** 2))
P = np.abs(V) ** 2 / fs                         # PSD (per Hz), two-sided
fx = np.fft.fftfreq(n, 1 / fs)
order = np.argsort(fx)
fx, P = fx[order], P[order]
df = fx[1] - fx[0]
print(f"rms phase deviation of the synthetic signal: {np.std(phi):.4f} rad (small-angle OK if << 1)")
for rbw, offs in [(100.0, [1e3, 3e3]), (1e3, [1e4, 3e4, 1e5]), (10e3, [3e5])]:
    H2 = lambda d: np.exp(-4 * np.log(2) * (d / rbw) ** 2)
    enbw = rbw * np.sqrt(np.pi / (4 * np.log(2)))
    for off in offs:
        # RBW-filtered power at the offset: average over random realisations of the noise -> use neighbouring bins
        idx = np.abs(fx - off) < 3 * rbw
        p_rbw = np.sum(P[idx] * H2(fx[idx] - off)) * df
        # carrier power
        pc = np.sum(P[np.abs(fx) < 3 * rbw] * H2(fx[np.abs(fx) < 3 * rbw])) * df
        L_meas_power = dbp(p_rbw) - dbp(pc) - dbp(enbw)
        print(f"  RBW {rbw:6.0f} Hz, offset {off/1e3:6.1f} kHz: L_meas = {L_meas_power:7.2f} dBc/Hz, true {L_true(off):7.2f}"
              f" (error {L_meas_power-L_true(off):+.2f} dB)")
print("  (with a log-averaged trace the raw reading is 2.51 dB lower -> add it back; the analyzer's noise marker does)")

# ---------------------------------------------------------------- 2. analyzer floor
print("\n=== 2. DUT phase noise only X dB above the analyzer's own ===")
for x in [0, 3, 6, 10, 15, 20]:
    err = dbp(1 + 10 ** (-x / 10))
    print(f"  DUT {x:2d} dB above analyzer: reading high by {err:.2f} dB")
print("  e.g. SSA3021X Plus -98 dBc/Hz @10 kHz (1 GHz); tinySA Ultra -108 @100 kHz (30 MHz); a TCXO-derived 915 MHz"
      " PLL is typically far better -> the SA measures itself")

# ---------------------------------------------------------------- 3. delay-line discriminator
print("\n=== 3. Delay-line discriminator sensitivity |H|^2 = 4 sin^2(pi f tau) ===")
for tau in [50e-9, 200e-9, 1e-6]:
    row = []
    for off in [1e2, 1e3, 1e4, 1e5, 1e6]:
        h2 = 4 * np.sin(np.pi * off * tau) ** 2
        row.append(f"{off:>8.0e}: {dbp(h2):6.1f} dB")
    print(f"  tau = {tau*1e9:6.0f} ns (first null at {1/tau/1e6:.1f} MHz): " + " | ".join(row))
print(f"  -> relative to a quadrature phase detector (|H|^2 = 1), a 200 ns line is {-dbp(4*np.sin(np.pi*1e3*200e-9)**2):.0f} dB"
      " less sensitive at 1 kHz offset: fine for noisy free-running VCOs; longer tau helps close in but moves the nulls in")
# coax loss for 200 ns
for tau in [50e-9, 200e-9, 1e-6]:
    L_m = tau * 0.66 * 3e8
    print(f"  tau {tau*1e9:.0f} ns in vf 0.66 coax = {L_m:.1f} m; RG-58 at 900 MHz ~0.45 dB/m -> {0.45*L_m:.0f} dB loss")

# ---------------------------------------------------------------- 4. cross-correlation
print("\n=== 4. Two-channel cross-correlation: background vs number of averages m ===")
nfft = 256
dut_level = 0.1          # DUT PSD 10 dB below each channel's own background (=1)
for m in [1, 10, 100, 1000, 10000]:
    acc = np.zeros(nfft, complex)
    for _ in range(m):
        c = np.sqrt(dut_level) * (rng.standard_normal(nfft) + 1j * rng.standard_normal(nfft)) / np.sqrt(2)
        a = (rng.standard_normal(nfft) + 1j * rng.standard_normal(nfft)) / np.sqrt(2)
        b = (rng.standard_normal(nfft) + 1j * rng.standard_normal(nfft)) / np.sqrt(2)
        acc += (c + a) * np.conj(c + b)
    Syx = acc / m
    resid = np.mean(np.abs(Syx - dut_level))
    print(f"  m = {m:5d}: mean |<Syx> - S_dut| = {dbp(resid):6.1f} dB rel. single-channel background "
          f"(5 log m predicts {-5*np.log10(m):6.1f} dB); mean Re<Syx> = {dbp(np.mean(Syx.real)):6.1f} dB (DUT = -10.0)")

# ---------------------------------------------------------------- 5. multiplication
print("\n=== 5. Phase noise scales as 20 log N under frequency multiplication ===")
for f0, f1 in [(32e6, 915e6), (32e6, 433e6), (26e6, 1575.42e6), (10e6, 5.8e9)]:
    print(f"  {f0/1e6:.0f} MHz -> {f1/1e6:.1f} MHz: +{20*np.log10(f1/f0):.1f} dB (inside the PLL loop bandwidth)")

# ---------------------------------------------------------------- 6. RBW skirt vs offset
print("\n=== 6. Gaussian RBW skirt at the offset (carrier leakage into the offset measurement) ===")
for rbw in [100, 1e3, 10e3]:
    out = []
    for ratio in [1.5, 2, 3]:
        skirt = -4 * np.log(2) * ratio ** 2 * 10 / np.log(10)      # dB of |H|^2 at offset = ratio*RBW
        out.append(f"offset {ratio}xRBW: {skirt:6.1f} dB")
    print(f"  RBW {rbw:>6.0f} Hz: " + "; ".join(out))
print("  -> an ideal Gaussian skirt is < -100 dB by 3xRBW; real analog RBW filters (60:3 dB shape factor ~4-15) are far"
      " worse, so keep offset >= 5-10x RBW and check by halving RBW (the dBc/Hz value must not change)")
