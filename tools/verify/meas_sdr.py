#!/usr/bin/env python3
"""
meas_sdr.py -- numerical checks for kb/17-test-measurement/sdr-as-test-equipment.md

1. ADC resolution vs instantaneous dynamic range: ideal SNR and per-bin noise floor for
   RTL-SDR (8 bit), HackRF (8 bit), Pluto (12 bit), SDRplay/Airspy (12-14 bit) at their sample rates.
2. IQ imbalance -> image rejection ratio: IRR = 10 log[(1 + 2g cos(phi) + g^2)/(1 - 2g cos(phi) + g^2)],
   checked against a simulated complex tone with gain/phase error.
3. Using an SDR as a power meter: synthetic dBFS-vs-dBm curve (noise floor + compression),
   two-point calibration, linear range, and error outside it.
4. Sweeping an SDR as a spectrum analyzer: hops, usable fraction of each capture (edges and DC spike),
   sweep time for rtl_power-style operation.
5. Measuring a carrier's power in an FFT: bin power summed over the window's main lobe
   (Hann: +/-2 bins) recovers the tone power regardless of bin offset (scalloping fixed).

Run: python3 tools/verify/meas_sdr.py
"""
import numpy as np

rng = np.random.default_rng(11)


def dbp(x):
    return 10 * np.log10(x)


# ---------------------------------------------------------------- 1. ADC and dynamic range
print("=== 1. Instantaneous dynamic range of common SDRs (ideal ADC numbers; real ENOB lower) ===")
for name, bits, fs in [("RTL-SDR (RTL2832U)", 8, 2.4e6), ("HackRF One", 8, 20e6), ("ADALM-Pluto (AD9363)", 12, 4e6),
                       ("Airspy R2 / SDRplay", 12, 10e6), ("SDRplay RSPdx (14-bit)", 14, 2e6)]:
    snr = 6.02 * bits + 1.76
    print(f"  {name:24s}: {bits:2d} bits -> full-scale SNR {snr:5.1f} dB over {fs/1e6:4.1f} MHz; per-Hz floor "
          f"{-snr - dbp(fs/2):6.1f} dBFS/Hz; 1024-pt FFT bin floor {-snr - dbp(512):6.1f} dBFS")
print("  -> in practice spurs, the DC offset and the tuner's own compression limit an 8-bit SDR to ~45-50 dB SFDR")

# ---------------------------------------------------------------- 2. IQ imbalance image rejection
print("\n=== 2. IQ gain/phase imbalance -> image ===")
def irr_db(g_db, phi_deg):
    g = 10 ** (g_db / 20)
    ph = np.radians(phi_deg)
    return 10 * np.log10((1 + 2 * g * np.cos(ph) + g ** 2) / (1 - 2 * g * np.cos(ph) + g ** 2))
n = 4096
t = np.arange(n)
for g_db, ph in [(0.1, 1.0), (0.5, 3.0), (1.0, 5.0)]:
    g = 10 ** (g_db / 20)
    I = np.cos(2 * np.pi * 300 / n * t)
    Q = g * np.sin(2 * np.pi * 300 / n * t + np.radians(ph))
    X = np.fft.fft(I + 1j * Q)
    sim = dbp(np.abs(X[300]) ** 2 / np.abs(X[-300]) ** 2)
    print(f"  gain error {g_db} dB, phase error {ph} deg: IRR formula {irr_db(g_db, ph):5.1f} dB, simulated {sim:5.1f} dB")
print("  -> uncorrected zero-IF SDRs show a mirror image of strong signals ~25-40 dB down at -f; software IQ"
      " correction or offset tuning moves it out of the way")

# ---------------------------------------------------------------- 3. SDR as a power meter
print("\n=== 3. SDR as a power meter: calibration curve at fixed gain ===")
p_in = np.arange(-120, 1, 5.0)
floor_dbfs = -95.0          # noise in the measurement bandwidth
offset = 25.0               # dBFS = dBm + offset in the linear region (gain dependent)
p_sat = -3.0                # dBFS: soft compression knee
def dbfs(p):
    lin = p + offset
    sig = 10 ** (lin / 10)
    comp = sig / (1 + (sig / 10 ** (p_sat / 10)) ** 2) ** 0.5       # soft compression
    return dbp(comp + 10 ** (floor_dbfs / 10))
cal_pts = (-80.0, -50.0)
m = (dbfs(cal_pts[1]) - dbfs(cal_pts[0])) / (cal_pts[1] - cal_pts[0])
c = dbfs(cal_pts[0]) - m * cal_pts[0]
for p in [-125, -120, -110, -100, -80, -60, -40, -35, -30, -25]:
    est = (dbfs(p) - c) / m
    print(f"  input {p:5.0f} dBm: reads {dbfs(p):6.1f} dBFS -> calibrated {est:7.2f} dBm (error {est-p:+.2f} dB)")
lin_ok = [p for p in p_in if abs((dbfs(p) - c) / m - p) < 0.5]
print(f"  +/-0.5 dB range with a 2-point cal at -80/-50 dBm: {min(lin_ok):.0f} to {max(lin_ok):.0f} dBm "
      f"({max(lin_ok)-min(lin_ok):.0f} dB) at this gain; changing gain/frequency/temperature needs a new cal")

# ---------------------------------------------------------------- 4. sweeping
print("\n=== 4. SDR sweep (rtl_power / hackrf_sweep style) ===")
for name, fs, usable, t_hop in [("RTL-SDR", 2.4e6, 0.75, 0.02), ("HackRF (hackrf_sweep)", 20e6, 0.75, 0.0015),
                                ("Pluto (USB 4 MS/s)", 4e6, 0.8, 0.02)]:
    span = 100e6
    hops = np.ceil(span / (fs * usable))
    print(f"  {name:22s}: {fs/1e6:4.1f} MS/s, keep {usable*100:.0f} % of each capture -> {hops:.0f} hops per 100 MHz; "
          f"~{hops*t_hop*1000:.0f} ms per sweep (retune+capture {t_hop*1000:.1f} ms/hop, assumed)")
print("  (hop time depends strongly on driver/firmware; hackrf_sweep is designed for fast sweeps)")

# ---------------------------------------------------------------- 5. tone power from an FFT
print("\n=== 5. Tone power from FFT bins (Hann window) ===")
n = 8192
w = np.hanning(n)
for frac in [0.0, 0.25, 0.5]:
    k0 = 1000 + frac
    x = np.sqrt(2) * np.cos(2 * np.pi * k0 / n * np.arange(n))     # 0 dB (unit power) tone, real
    X = np.fft.rfft(x * w)
    psd = np.abs(X) ** 2 / (np.sum(w) ** 2) * 2       # power per bin, sine-calibrated
    peak = dbp(psd.max())
    band = dbp(np.sum(np.abs(X[1000 - 3:1000 + 4]) ** 2) / np.sum(w ** 2) / n * 2)
    print(f"  tone {frac:.2f} bin off-centre: peak-bin reading {peak:+6.2f} dB (scalloping), "
          f"summed +/-3 bins with ENBW correction {band:+6.2f} dB (true 0.00)")
