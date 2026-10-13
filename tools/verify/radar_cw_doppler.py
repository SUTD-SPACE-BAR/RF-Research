#!/usr/bin/env python3
"""Verification for kb/11-radar/cw-and-doppler-radar.md

Run:  python3 tools/verify/radar_cw_doppler.py      (~5 s)

Checks / computes:
  1. Two-way Doppler: exact (1+b)/(1-b) vs 2v/lambda for v up to 1000 m/s; Doppler-per-km/h table.
  2. Homodyne I/Q: sign of Doppler (approach/recede) recovered with I/Q; a single (real) channel
     gives a symmetric spectrum (no direction). Image rejection vs I/Q gain/phase imbalance:
     IRR = (1 + 2 g cos(phi) + g^2)/(1 - 2 g cos(phi) + g^2)  vs simulation.
  3. Micro-Doppler of a rotor: max Doppler 2 Omega r / lambda, blade-flash rate N_blades * rev/s;
     spectrogram peak frequency vs theory.
  4. Vital signs: chest displacement 4 mm @0.25 Hz + heart 0.3 mm @1.2 Hz at 24 GHz: arctangent
     (phase) demodulation recovers displacement; small-angle linear approximation fails (4 rad).
  5. Rocket velocity by CW Doppler: Doppler, Doppler rate for acceleration a, maximum coherent
     time sqrt(lambda/(2a)), range estimate for a small rocket with a 24 GHz module (+/- lens).
  6. Range correlation of oscillator phase noise for CW: suppression 4 sin^2(pi f tau).
  7. Two-frequency (FSK) CW ranging: R = c dphi/(4 pi df), unambiguous c/(2 df); simulation.
  8. Cosine effect for speed guns.
"""
import numpy as np
from scipy import signal

c = 299_792_458.0
k = 1.380649e-23
ok_all = True


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel else 1.0)
    ok = err <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol}{' rel' if rel else ''})")
    return ok


db = lambda x: 10 * np.log10(x)

print("=" * 78)
print("1. Doppler equation")
f0 = 24.125e9
for v in (1.0, 30.0, 300.0, 1000.0):
    b = v / c
    exact = f0 * ((1 + b) / (1 - b) - 1)
    approx = 2 * v * f0 / c
    print(f"    v = {v:6.0f} m/s: exact {exact:12.4f} Hz, 2v/lambda {approx:12.4f} Hz, rel diff {abs(exact-approx)/exact:.2e}")
check("relative error of 2v/lambda at 1000 m/s < 1e-5", abs(f0 * ((1 + 1000 / c) / (1 - 1000 / c) - 1) - 2 * 1000 * f0 / c) / (2 * 1000 * f0 / c), 0, 1e-5)
print("    Doppler per km/h and per m/s:")
for f in (2.45e9, 5.8e9, 10.525e9, 24.125e9, 60.5e9, 77e9):
    print(f"      {f/1e9:7.3f} GHz: {2*f/(3.6*c):7.2f} Hz per km/h, {2*f/c:8.2f} Hz per m/s")

print("=" * 78)
print("2. I/Q homodyne: direction and image rejection")
fs = 10e3
t = np.arange(8192) / fs
fd = 500.0
for sgn, lab in ((+1, "approaching"), (-1, "receding")):
    x = np.exp(1j * (2 * np.pi * sgn * fd * t + 0.3))
    X = np.fft.fftshift(np.abs(np.fft.fft(x)))
    fr = np.fft.fftshift(np.fft.fftfreq(len(t), 1 / fs))
    fpk = fr[np.argmax(X)]
    check(f"I/Q: {lab} target appears at {sgn*fd:+.0f} Hz", fpk, sgn * fd, fs / len(t) * 1.5)
xr = np.cos(2 * np.pi * fd * t + 0.3)
Xr = np.abs(np.fft.fft(xr))
fr2 = np.fft.fftfreq(len(t), 1 / fs)
pos = Xr[np.argmin(np.abs(fr2 - fd))]
neg = Xr[np.argmin(np.abs(fr2 + fd))]
check("single real channel: +fd and -fd lines equal (no direction)", pos / neg, 1.0, 1e-6)
for g_db, ph_deg in ((0.5, 3.0), (1.0, 5.0), (0.1, 1.0)):
    g = 10 ** (g_db / 20)
    ph = np.radians(ph_deg)
    # I = cos(wt), Q = g sin(wt + ph)
    I = np.cos(2 * np.pi * fd * t)
    Q = g * np.sin(2 * np.pi * fd * t + ph)
    Z = np.abs(np.fft.fft((I + 1j * Q) * np.hanning(len(t))))
    irr_sim = (Z[np.argmin(np.abs(fr2 - fd))] / Z[np.argmin(np.abs(fr2 + fd))]) ** 2
    irr_th = (1 + 2 * g * np.cos(ph) + g ** 2) / (1 - 2 * g * np.cos(ph) + g ** 2)
    check(f"IRR gain {g_db} dB / phase {ph_deg} deg (dB)", db(irr_sim), db(irr_th), 0.05)
    print(f"      -> IRR = {db(irr_th):.1f} dB")

print("=" * 78)
print("3. Rotor micro-Doppler")
lam = c / 24.125e9
r_tip = 0.12      # 24 cm propeller
rpm = 6000.0
Om = 2 * np.pi * rpm / 60
nb = 2
fdmax = 2 * Om * r_tip / lam
print(f"    tip speed {Om*r_tip:.1f} m/s -> max micro-Doppler +-{fdmax/1e3:.2f} kHz at 24 GHz; blade flash rate {nb*rpm/60:.0f} Hz")
fs = 100e3
t = np.arange(int(0.2 * fs)) / fs
x = np.zeros_like(t, complex)
# blade modelled as line of scatterers; return phase 4 pi/lam * r cos(Om t + blade angle); line-of-sight in blade plane
rs = np.linspace(0.02, r_tip, 30)
for bld in range(nb):
    th = Om * t + 2 * np.pi * bld / nb
    for r in rs:
        x += np.exp(-1j * 4 * np.pi / lam * r * np.cos(th))
x += 5.0  # body echo
f_sp, t_sp, Sxx = signal.spectrogram(x, fs, window="hann", nperseg=256, noverlap=192, return_onesided=False)
f_sp = np.fft.fftshift(f_sp)
Sxx = np.fft.fftshift(Sxx, axes=0)
# extent of micro-Doppler: exclude the body line, threshold -20 dB below the strongest non-body energy
nonbody = np.abs(f_sp) > 1e3
M = Sxx[nonbody].max()
fmax_obs = np.max(np.abs(f_sp[nonbody][np.any(Sxx[nonbody] > 1e-2 * M, axis=1)]))
check("rotor: highest micro-Doppler observed ~ 2 Omega r_tip/lambda (+ window width)", fmax_obs, fdmax, 0.06, rel=True)
# blade-flash periodicity: peaks of the high-|f| energy envelope
hi = np.sum(Sxx[np.abs(f_sp) > 0.5 * fdmax], axis=0)
pk, _ = signal.find_peaks(hi, height=0.5 * hi.max())
period = np.median(np.diff(t_sp[pk]))
check("rotor: blade-flash rate = N_blades * rev/s (even N)", 1 / period, nb * rpm / 60, 12)
print("=" * 78)
print("4. Vital signs (24 GHz), arctangent demodulation")
fs = 200.0
t = np.arange(int(30 * fs)) / fs
d = 4e-3 * np.sin(2 * np.pi * 0.25 * t) + 0.3e-3 * np.sin(2 * np.pi * 1.2 * t)
R0 = 1.0
rng = np.random.default_rng(1)
for s_n in (0.0005, 0.00005):
    x = 0.01 * np.exp(-1j * 4 * np.pi * (R0 + d) / lam) + 0.02 + s_n * (rng.standard_normal(len(t)) + 1j * rng.standard_normal(len(t)))
    # static clutter/leakage offset removed with a least-squares circle fit (centre of the I/Q arc)
    A = np.c_[2 * x.real, 2 * x.imag, np.ones(len(x))]
    bvec = x.real ** 2 + x.imag ** 2
    cx, cy, _ = np.linalg.lstsq(A, bvec, rcond=None)[0]
    xc = x - (cx + 1j * cy)
    phase = np.unwrap(np.angle(xc))
    d_est = -phase * lam / (4 * np.pi)
    d_est -= d_est.mean()
    err = np.sqrt(np.mean((d_est - (d - d.mean())) ** 2))
    pred = lam / (4 * np.pi) * s_n / 0.01          # phase noise ~ sigma_per_component / amplitude
    check(f"arctangent demod rms error = noise limit lambda/(4pi)*sigma/A (noise {s_n})", err, pred, 0.25, rel=True)
print(f"    phase swing 4 pi d/lambda = {4*np.pi*4e-3/lam:.2f} rad (>> 1: small-angle linear demod invalid)")
# heart component from spectrum
D = np.abs(np.fft.rfft((d_est - np.convolve(d_est, np.ones(400) / 400, 'same')) * np.hanning(len(d_est))))
fD = np.fft.rfftfreq(len(d_est), 1 / fs)
band = (fD > 0.8) & (fD < 2.0)
check("heartbeat line found at 1.2 Hz", fD[band][np.argmax(D[band])], 1.2, 0.05)

print("=" * 78)
print("5. Rocket velocity by CW Doppler")
for f in (10.525e9, 24.125e9):
    lamr = c / f
    v = 250.0
    a = 100.0     # 10 g
    fd = 2 * v / lamr
    fdot = 2 * a / lamr
    Tmax = np.sqrt(lamr / (2 * a))
    print(f"    {f/1e9:.3f} GHz: v 250 m/s -> fd {fd/1e3:.2f} kHz; a 100 m/s^2 -> Doppler rate {fdot/1e3:.2f} kHz/s; "
          f"max coherent time (1 bin of drift) {Tmax*1e3:.2f} ms; bin {1/Tmax:.0f} Hz ({lamr/(2*Tmax):.2f} m/s)")
lamr = c / 24.125e9
Tmax = np.sqrt(lamr / (2 * 100.0))
check("24 GHz, 10 g: T_max = sqrt(lambda/2a) (ms)", Tmax * 1e3, 7.88, 0.02)
EIRP = 10 ** (16 / 10) / 1000
Gr = 10 ** 0.95
sig = 0.01
snr = 10 ** 1.3
for NF_db, extra_db, lab in ((20, 0, "bare module, NF_eff 20 dB at ~40 kHz IF (assumed)"),
                              (20, 20, "+10 dB lens/horn on each of TX and RX (assumed)"),
                              (10, 20, "+ lens, and low-noise IF (NF 10 dB)")):
    R = (EIRP * Gr * 10 ** (extra_db / 10) * lamr ** 2 * sig * Tmax / ((4 * np.pi) ** 3 * k * 290 * 10 ** (NF_db / 10) * snr)) ** 0.25
    print(f"    sigma 0.01 m^2, T = {Tmax*1e3:.1f} ms, SNR 13 dB, {lab}: R ~ {R:.0f} m")

print("=" * 78)
print("6. Range correlation of phase noise (CW homodyne)")
for R in (0.05, 1.0, 10.0, 100.0):
    tau = 2 * R / c
    for f in (100.0, 10e3):
        supp = 4 * np.sin(np.pi * f * tau) ** 2
        print(f"    R = {R:6.2f} m, offset {f:7.0f} Hz: PN multiplied by {db(supp):7.1f} dB")
tau = 2 * 10 / c
check("small-offset approx (2 pi f tau)^2 at 10 m, 100 Hz", db(4 * np.sin(np.pi * 100 * tau) ** 2), db((2 * np.pi * 100 * tau) ** 2), 1e-3)

print("=" * 78)
print("7. Two-frequency (FSK) CW ranging")
df = 2.5e6    # InnoSenT FSK example step
Ru = c / (2 * df)
R_true = 37.3
v = -3.0
f1 = 24.125e9
fs = 2e3
n = np.arange(2048)
t = n / fs
ph1 = -4 * np.pi * f1 * (R_true + v * t) / c
ph2 = -4 * np.pi * (f1 + df) * (R_true + v * t) / c
rng = np.random.default_rng(2)
x1 = np.exp(1j * ph1) + 0.05 * (rng.standard_normal(len(t)) + 1j * rng.standard_normal(len(t)))
x2 = np.exp(1j * ph2) + 0.05 * (rng.standard_normal(len(t)) + 1j * rng.standard_normal(len(t)))
X1 = np.fft.fft(x1)
X2 = np.fft.fft(x2)
kk = np.argmax(np.abs(X1))
dphi = np.angle(X1[kk] * np.conj(X2[kk]))
R_est = c * (dphi % (2 * np.pi)) / (4 * np.pi * df)
print(f"    df = {df/1e6} MHz -> unambiguous range {Ru:.1f} m; true R {R_true} m -> estimate {R_est:.2f} m")
t_mid = t[-1] / 2
print(f"    (target moves {v*t[-1]:.2f} m during the record; estimate refers to mid-record range {R_true + v*t_mid:.2f} m)")
check("FSK range estimate = range at mid-record", R_est, R_true + v * t_mid, 0.1)

print("=" * 78)
print("8. Cosine effect")
for ang in (5, 10, 20, 45):
    print(f"    {ang:2d} deg off-axis: reads {np.cos(np.radians(ang))*100:.1f} % of true speed")
check("cos 10 deg", np.cos(np.radians(10)), 0.9848, 1e-4)

print("=" * 78)
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
