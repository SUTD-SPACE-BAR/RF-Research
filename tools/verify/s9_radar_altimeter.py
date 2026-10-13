#!/usr/bin/env python3
"""W5-S9 checks for kb/11-radar/fmcw-radar.md section "FMCW radio altimeters: error budget".

Run:  python3 tools/verify/s9_radar_altimeter.py   (~2 s)

1. Triangular-FMCW cycle counter: f_b = 4*dF*f_m*h/c, N = f_b/f_m cycles per period -> h = c*N/(4 dF);
   the step (fixed, quantisation) error is c/(4 dF). Simulated zero-crossing counter shows the staircase.
2. Single-ramp Doppler bias h_err = f_D*c/(2S) and its cancellation by averaging up and down ramps.
3. FFT altimeter: bin c/(2B), CRB of a peak-interpolated estimate sigma = (c/2B)*sqrt(6/SNR)/(2 pi) (SNR post-FFT).
4. Geometry: tilt of a narrow beam (h/cos), wide-beam leading edge vs spectrum centroid bias.
5. Installation delay from cables; double-bounce line at 2h.
6. Ground-return power vs height for a 24 GHz, 100 mW e.i.r.p. recovery altimeter (sigma0 assumption).
"""
import numpy as np

c = 299_792_458.0
kT0_dbm = -173.98
ok_all = True
db = lambda x: 10 * np.log10(x)


def check(name, got, want, tol):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.5g}, expected {want:.5g} (tol {tol})")


print("=" * 78)
print("1. Cycle-counting altimeter: step error c/(4 dF)")
for band, dF in (("4.2-4.4 GHz aero, dF = 100 MHz", 100e6), ("4.2-4.4 GHz, dF = 150 MHz", 150e6),
                 ("24.00-24.25 GHz, dF = 250 MHz", 250e6)):
    print(f"    {band:32s}: step = c/(4 dF) = {c/(4*dF):.3f} m")
check("step error 24 GHz 250 MHz (m)", c / (4 * 250e6), 0.2998, 1e-3)
# zero-crossing counter simulation: triangular sweep, real beat, count rising zero crossings per period
dF, fm, fs = 250e6, 200.0, 20e6
Tm = 1 / fm
t = np.arange(int(fs * Tm)) / fs


def tri_phase(tt):
    """TX phase of a triangular sweep 0..dF..0 over Tm (baseband, Hz -> rad)."""
    S = 2 * dF * fm
    up = tt % Tm < Tm / 2
    tr = tt % Tm
    f_inst = np.where(up, S * tr, dF - S * (tr - Tm / 2))
    return 2 * np.pi * np.cumsum(f_inst) / fs


ph_tx = tri_phase(np.concatenate([t - Tm, t]))  # include a previous period so the delayed copy is defined
heights = np.linspace(10.0, 12.0, 41)
counts = []
for h in heights:
    d = int(round(2 * h / c * fs * 1000)) / 1000.0   # fractional-sample delay via interpolation
    tau = 2 * h / c
    tt_full = np.concatenate([t - Tm, t])
    ph_rx = np.interp(tt_full - tau, tt_full, ph_tx)
    beat = np.cos(ph_tx - ph_rx)[len(t):]
    zc = np.sum((beat[:-1] < 0) & (beat[1:] >= 0))
    counts.append(zc)
counts = np.array(counts)
h_read = c * counts / (4 * dF)
steps = np.unique(np.round(np.diff(h_read[np.nonzero(np.diff(h_read))]), 3))
print(f"    simulated counter over h = 10-12 m: readings {sorted(set(np.round(h_read,2)))} m")
print(f"    staircase step(s) {steps} m (theory {c/(4*dF):.3f} m); max |error| {np.max(np.abs(h_read-heights)):.3f} m")
check("simulated step (m)", float(np.median(np.diff(sorted(set(h_read))))), c / (4 * dF), 0.002)

print("=" * 78)
print("2. Doppler bias of a single ramp and up/down cancellation (24.125 GHz)")
lam = c / 24.125e9
S = 2 * dF * 500.0                      # 250 MHz in 1 ms ramps (f_m = 500 Hz)
for v, lab in ((6.0, "main parachute 6 m/s"), (25.0, "drogue 25 m/s"), (60.0, "ballistic/early 60 m/s")):
    fD = 2 * v / lam
    bias = fD * c / (2 * S)
    print(f"    {lab:24s}: f_D = {fD/1e3:5.2f} kHz -> single-ramp height bias {bias:5.2f} m (up ramp -, down ramp +); average of both: 0")
check("drogue single-ramp bias (m)", 2 * 25.0 / lam * c / (2 * S), 2.41, 0.01)
fd = 2 * 25 / lam; h = 50.0
f_up = 2 * S * h / c - fd; f_dn = 2 * S * h / c + fd
check("up/down average height (m)", (f_up + f_dn) / 2 * c / (2 * S), 50.0, 1e-9)
check("up/down difference velocity (m/s)", (f_dn - f_up) / 2 * lam / 2, 25.0, 1e-9)
print(f"    fast chirp 30 MHz/us (TI-class): drogue bias = {fd*c/(2*30e12)*100:.1f} cm")

print("=" * 78)
print("3. FFT altimeter accuracy (one 250 MHz ramp)")
B = 250e6
for snr_db in (10, 20, 30):
    snr = 10 ** (snr_db / 10)
    sig = c / (2 * B) * np.sqrt(6 / snr) / (2 * np.pi)
    print(f"    post-FFT SNR {snr_db} dB: bin {c/(2*B):.2f} m, CRB sigma_h = {sig*100:.1f} cm")
# Monte Carlo check of the interpolated-peak estimator at 20 dB
rng = np.random.default_rng(1)
N = 512; est = []
f0 = 100.3
for _ in range(2000):
    n = np.arange(N)
    x = np.exp(2j * np.pi * f0 * n / N) + np.sqrt(N / 100) * (rng.standard_normal(N) + 1j * rng.standard_normal(N)) / np.sqrt(2)
    X = np.fft.fft(x, 16 * N)
    k = np.argmax(np.abs(X)); kk = k + 0.5 * (np.abs(X[k-1]) - np.abs(X[k+1])) / (np.abs(X[k-1]) - 2*np.abs(X[k]) + np.abs(X[k+1]))
    est.append(kk / 16)
sd_bins = np.std(est)
crb_bins = np.sqrt(6 / 100) / (2 * np.pi)
print(f"    Monte Carlo (SNR_post 20 dB): std = {sd_bins:.4f} bins vs CRB {crb_bins:.4f} bins")
check("estimator within 15 % of CRB", sd_bins / crb_bins, 1.0, 0.15)

print("=" * 78)
print("4. Geometry: tilt, beamwidth and the leading edge")
for tilt in (5, 10, 15, 20):
    print(f"    narrow beam tilted {tilt:2d} deg: reads h/cos = +{(1/np.cos(np.radians(tilt))-1)*100:.1f} % ; at 50 m: +{50*(1/np.cos(np.radians(tilt))-1):.2f} m")
check("15 deg tilt error at 50 m (m)", 50 * (1 / np.cos(np.radians(15)) - 1), 1.764, 0.002)
# wide beam over flat ground, Lambert-ish sigma0 ~ cos^2: echo spectrum from h (nadir) to h/cos(theta_b/2)
for bw in (30, 60, 80):
    th = np.linspace(0, np.radians(bw / 2), 4001)
    Rng = 1 / np.cos(th)                         # range / h
    w = np.sin(th) * np.cos(th) ** 2 * np.cos(th) ** 4 / Rng ** 4 * Rng ** 2  # ring area * sigma0 * pattern / R^4 (approx)
    centroid = np.sum(w * Rng) / np.sum(w)
    print(f"    {bw:2d} deg beam, flat ground: echo spread h..{1/np.cos(np.radians(bw/2)):.3f}h; power-centroid reads {centroid:.4f} h (+{(centroid-1)*100:.2f} %), leading edge reads h")
print("    -> track the leading edge (first range bin above threshold), not the centroid")

print("=" * 78)
print("5. Installation delay and double bounce")
for Ltx, Lrx, vf in ((0.3, 0.3, 0.70), (1.0, 1.0, 0.66)):
    off = (Ltx + Lrx) / (2 * vf)
    print(f"    cables {Ltx}+{Lrx} m, vf {vf}: apparent height offset (Ltx+Lrx)/(2 vf) = {off:.2f} m -> calibrate zero on the ground")
check("cable offset 0.3+0.3 m vf 0.7", (0.3 + 0.3) / (2 * 0.7), 0.4286, 1e-3)
print("    double bounce (ground -> vehicle -> ground): line at 2h, weaker by the vehicle's reflection and extra 1/(2h)^2 spreading")

print("=" * 78)
print("6. Ground-return budget, 24.125 GHz, 100 mW e.i.r.p. (SG TS SRD limit), G_rx = 15 dBi")
EIRP_dbm, Gr, NF, sigma0_db = 20.0, 15.0, 12.0, -10.0
bw = 30.0
for hh in (2, 10, 50, 100, 300):
    A = np.pi * (hh * np.tan(np.radians(bw / 2))) ** 2       # footprint
    sig = 10 ** (sigma0_db / 10) * A
    Pr = EIRP_dbm + Gr + db(lam ** 2 * sig / ((4 * np.pi) ** 3 * hh ** 4))
    T = 1e-3
    EN0 = Pr - (kT0_dbm + NF) + db(T)
    print(f"    h = {hh:4d} m: footprint {A:9.1f} m^2, P_r = {Pr:6.1f} dBm, E/N0 in one 1 ms ramp = {EN0:5.1f} dB")
    if hh == 100:
        en100 = EN0
check("E/N0 at 100 m (dB), hand calc 35-38.1+23.5-33.0-80+162-30", en100, 39.4, 0.1)
print("    (beam-limited diffuse return falls 20 dB/decade, like the specular image-theory case)")

print("=" * 78)
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
