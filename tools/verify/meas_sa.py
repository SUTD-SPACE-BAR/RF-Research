#!/usr/bin/env python3
"""
meas_sa.py -- numerical checks for kb/17-test-measurement/spectrum-analyzers.md

1. Detector / averaging bias for Gaussian noise (Monte Carlo):
   power (rms) average = truth; linear-voltage (envelope) average = -1.05 dB;
   log (dB) average = -2.51 dB = -10*gamma_Euler/ln(10).
2. Equivalent noise bandwidth (ENBW) / 3-dB bandwidth for Gaussian and n-pole
   synchronously-tuned RBW filters (AN 150 quotes 1.05-1.13).
3. DANL scales as 10 log(RBW): simulated noise through Gaussian RBW filters of 1/10/100 kHz.
4. DANL <-> noise figure, applied to tinySA / tinySA Ultra / Siglent SSA3021X Plus specs.
5. Swept-analyzer sweep time ST = k * span / RBW^2 (k = 2..3).
6. Measuring a signal close to the noise floor: power-domain correction.
7. LoRa chirp (BW 125 kHz, SF7) measured with a swept SA:
   (a) peak (max-hold) reading vs RBW for a constant-envelope chirp,
   (b) channel-power integration of a PSD trace recovers the true power,
   (c) 99 % occupied bandwidth.
8. Attenuator chain for a 1 W LoRa transmitter into a tinySA Ultra.

Run: python3 tools/verify/meas_sa.py
"""
import numpy as np
from scipy import special, signal

rng = np.random.default_rng(7)


def dbp(x):
    return 10 * np.log10(x)


# ---------------------------------------------------------------- 1. averaging bias
print("=== 1. Averaging/detector bias for Gaussian noise ===")
N = 2_000_000
z = (rng.standard_normal(N) + 1j * rng.standard_normal(N)) / np.sqrt(2)   # unit mean power
env = np.abs(z)
p = env ** 2
true = dbp(np.mean(p))
lin = 20 * np.log10(np.mean(env)) - 20 * np.log10(np.sqrt(np.mean(p)))    # voltage average, read as rms
logavg = np.mean(10 * np.log10(p))
print(f"power (rms) average      : {true:+.3f} dB")
print(f"voltage (envelope) avg   : {lin:+.3f} dB   (theory 20log(sqrt(pi)/2) = {20*np.log10(np.sqrt(np.pi)/2):+.3f} dB)")
print(f"log (dB) average         : {logavg-true:+.3f} dB   (theory -10*gamma/ln10 = {-10*np.euler_gamma/np.log(10):+.3f} dB)")
# AN 150 bookkeeping: an analyzer calibrated for sine rms shows mean Rayleigh as 0.886 sigma (-1.05 dB)
print("  -> add +1.05 dB (voltage avg) or +2.51 dB (log avg) to read true noise power; rms/power detector needs 0 dB")

# ---------------------------------------------------------------- 2. ENBW
print("\n=== 2. Noise bandwidth / 3-dB bandwidth of RBW filters ===")
# Gaussian: |H|^2 = exp(-(f/a)^2 ln2 * 4 / B3^2 ...) -> ENBW/B3 = sqrt(pi/(4 ln2))
print(f"Gaussian filter           : ENBW/B3dB = {np.sqrt(np.pi/(4*np.log(2))):.4f}")
for n in [2, 3, 4, 5]:
    # n identical single-pole (synchronously tuned) stages: |H|^2 = (1+(f/a)^2)^-n
    f3 = np.sqrt(2 ** (1 / n) - 1)              # in units of a
    enbw = np.sqrt(np.pi) * special.gamma(n - 0.5) / special.gamma(n)   # integral over -inf..inf, units of a
    print(f"{n}-pole synchronously tuned: ENBW/B3dB = {enbw/(2*f3):.4f}")
print("  -> AN 150: 1.05-1.13 for Keysight near-Gaussian filters; 10 log(1.065) = 0.27 dB, 10 log(1.128) = 0.52 dB")

# ---------------------------------------------------------------- 3. DANL vs RBW (simulation)
print("\n=== 3. Displayed noise vs RBW (simulated white noise, Gaussian RBW, log averaging) ===")
fs = 2e6
n = 2 ** 21
x = (rng.standard_normal(n) + 1j * rng.standard_normal(n)) / np.sqrt(2)   # PSD = 1/fs per Hz (unit power over fs)
X = np.fft.fft(x)
f = np.fft.fftfreq(n, 1 / fs)
res = []
for rbw in [1e3, 10e3, 100e3]:
    a = rbw / (2 * np.sqrt(np.log(2)))           # Gaussian |H| = exp(-(f/a)^2/2)? choose |H|^2 = exp(-(f/a)^2 ...)
    H2 = np.exp(-4 * np.log(2) * (f / rbw) ** 2)  # |H|^2, 3 dB full width = rbw
    y = np.fft.ifft(X * np.sqrt(H2))
    pw = np.abs(y[5000:-5000]) ** 2
    res.append((rbw, dbp(np.mean(pw)), np.mean(dbp(pw))))
for rbw, pwr, lg in res:
    print(f"RBW {rbw/1e3:6.0f} kHz: power-avg {pwr:7.2f} dB, log-avg {lg:7.2f} dB (rel. units)")
print(f"  slope per decade: {res[1][1]-res[0][1]:.2f} dB, {res[2][1]-res[1][1]:.2f} dB (theory 10.00); "
      f"log-avg offset {res[0][2]-res[0][1]:.2f} dB")
enbw_g = np.sqrt(np.pi / (4 * np.log(2)))
print(f"  absolute check: power in 1 kHz RBW should be 10log(ENBW/fs) = {dbp(1e3*enbw_g/fs):.2f} dB; got {res[0][1]:.2f}")

# ---------------------------------------------------------------- 4. DANL <-> NF
print("\n=== 4. Analyzer noise figure from DANL specs ===")
def nf_from_danl(danl_dbm, rbw_hz, log_avg=True, enbw_ratio=1.0):
    # DANL (display, log averaged, sine-calibrated) = -174 + NF + 10log(RBW*enbw) - 2.51 (if log avg)
    return danl_dbm + 174 - dbp(rbw_hz * enbw_ratio) + (2.51 if log_avg else 0)
cases = [("tinySA (low input) 30 kHz RBW, -102 dBm", -102, 30e3),
         ("tinySA high input 30 kHz RBW, -115 dBm", -115, 30e3),
         ("tinySA Ultra with LNA, 200 Hz RBW, -145 dBm", -145, 200),
         ("Siglent SSA3021X Plus, 10-200 MHz, preamp on, -161 dBm/Hz typ", -161, 1),
         ("Siglent SSA3021X Plus, 0.2-1.5 GHz, preamp on, -158 dBm/Hz typ", -158, 1),
         ("Siglent SSA3021X Plus, 0.2-1.5 GHz, preamp off, -139 dBm/Hz typ", -139, 1)]
for name, danl, rbw in cases:
    print(f"{name:66s}: NF ~ {nf_from_danl(danl, rbw, False):5.1f} dB (no log corr.) / {nf_from_danl(danl, rbw, True):5.1f} dB (log-avg corr.)")

# ---------------------------------------------------------------- 5. sweep time
print("\n=== 5. Swept-analyzer sweep time ST = k*span/RBW^2 ===")
for span, rbw in [(10e6, 100e3), (10e6, 10e3), (10e6, 3e3), (1e9, 1e6), (200e3, 1e3), (200e3, 100)]:
    print(f"span {span/1e6:7.3f} MHz, RBW {rbw/1e3:7.1f} kHz: ST = {2*span/rbw**2:9.4f} s (k=2) .. {3*span/rbw**2:9.4f} s (k=3)")
print("  (FFT/digital-RBW analyzers and the tinySA's point-by-point scheme beat this; tinySA quotes >1000 pts/s at wide RBW)")

# ---------------------------------------------------------------- 6. signal near noise
print("\n=== 6. Correcting a CW reading for the noise underneath (power detector) ===")
for snr in [3, 6, 10, 20]:
    corr = dbp(1 + 10 ** (-snr / 10))
    print(f"reading {snr:2d} dB above the noise-only floor -> true signal is {dbp(10**(snr/10)-1) if snr>0 else -np.inf:+6.2f} dB rel. floor"
          f" (subtract {dbp(10**(snr/10))-dbp(10**(snr/10)-1) if snr>0 else np.inf:.2f} dB)")

# ---------------------------------------------------------------- 7. LoRa chirp on a swept SA
print("\n=== 7. LoRa chirp (BW 125 kHz, SF7) seen by a spectrum analyzer ===")
BW, SF = 125e3, 7
Ts = 2 ** SF / BW
fs = 4e6
t = np.arange(int(Ts * fs * 8)) / fs                 # 8 up-chirps (preamble-like)
tm = np.mod(t, Ts)
inst_f = -BW / 2 + BW * tm / Ts
phase = 2 * np.pi * np.cumsum(inst_f) / fs
s = np.exp(1j * phase)                               # unit power, constant envelope
P_true = dbp(np.mean(np.abs(s) ** 2))
Xs = np.fft.fft(s)
fx = np.fft.fftfreq(len(s), 1 / fs)
print(f"true power = {P_true:.2f} dB (0 dB = 'carrier power'); chirp rate = {BW/Ts:.3g} Hz/s")
for rbw in [3e3, 10e3, 30e3, 100e3, 300e3, 600e3]:
    best = -99
    for fc in np.linspace(-BW / 2 * 0.8, BW / 2 * 0.8, 5):
        H = np.exp(-2 * np.log(2) * ((fx - fc) / rbw) ** 2)     # |H| with 3-dB full width rbw
        y = np.fft.ifft(Xs * H)
        best = max(best, dbp(np.max(np.abs(y[len(y)//8:-len(y)//8]) ** 2)))
    print(f"  RBW {rbw/1e3:5.0f} kHz, peak detector + max hold: {best:6.2f} dB rel. true power "
          f"(naive PSD guess 10log(RBW/BW) = {dbp(min(rbw,BW)/BW):6.2f} dB)")
# channel power from a PSD (Welch, RMS detector equivalent)
f_w, Pxx = signal.welch(s, fs=fs, nperseg=4096, return_onesided=False, scaling='density')
order = np.argsort(f_w)
f_w, Pxx = f_w[order], Pxx[order]
df = f_w[1] - f_w[0]
inband = np.abs(f_w) <= 100e3
print(f"  channel power integrated over +/-100 kHz from PSD: {dbp(np.sum(Pxx[inband])*df):.2f} dB (true {P_true:.2f})")
cum = np.cumsum(Pxx) / np.sum(Pxx)
lo, hi = f_w[np.searchsorted(cum, 0.005)], f_w[np.searchsorted(cum, 0.995)]
print(f"  99 % occupied bandwidth = {(hi-lo)/1e3:.1f} kHz (LoRa BW setting 125 kHz)")

# ---------------------------------------------------------------- 8. attenuator chain
print("\n=== 8. 1 W (30 dBm) LoRa module into a tinySA Ultra ===")
p_tx = 30.0
for chain in [(10,), (20,), (30,), (30, 10), (40,), (30, 20)]:
    att = sum(chain)
    p_in = p_tx - att
    p_first = p_tx          # the first pad sees full power
    p_dissip_first = 10 ** (p_tx / 10) * (1 - 10 ** (-chain[0] / 10)) / 1000
    verdict = ("DAMAGE (> +6 dBm abs max)" if p_in > 6 else
               "at the 'suggested max' 0 dBm -> marginal, no margin for a hot module" if p_in > -3 else
               "OK (below -25 dBm is best-linearity)" if p_in <= -25 else "OK")
    print(f"  pads {'+'.join(str(c) for c in chain):>6} dB: tinySA input {p_in:+5.1f} dBm; first pad dissipates "
          f"{p_dissip_first:.2f} W (CW) -> {verdict}")
print("  harmonic check at 2f/3f: with 40 dB of pads the fundamental is -10 dBm; a -50 dBc harmonic is -60 dBm, well above"
      " the tinySA floor; verify it is not internal by adding 10 dB more attenuation (a real harmonic drops exactly 10 dB)")
