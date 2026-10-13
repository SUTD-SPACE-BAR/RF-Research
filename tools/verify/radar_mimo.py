#!/usr/bin/env python3
"""Verification for kb/11-radar/mimo-radar-virtual-arrays.md

Run:  python3 tools/verify/radar_mimo.py      (~10 s)

Checks:
  1. Virtual array = all sums p_m + q_n (TI SWRA554): AWR1843BOOST-like layout (3 TX / 4 RX,
     TX1-TX3 2 lambda apart in azimuth, TX2 raised lambda/2): 8 azimuth + 4 elevated virtual elements.
  2. Angle resolution: 2/N rad rule vs measured -3 dB beamwidth (~0.886*2/N) and Rayleigh null 2/N
     for N = 4, 8, 12, 86 (TI 4-chip cascade: 86 uniform virtual azimuth elements, ~1.4 deg).
  3. TDM-MIMO: velocity-induced phase between TX slots -> angle bias if uncorrected; Doppler-
     compensation removes it; unambiguous velocity reduced by N_TX.
  4. BPM (Hadamard) MIMO: decoding recovers per-TX channels; SNR advantage 10 log10(N_TX) over TDM
     (same per-TX power, same frame time).
  5. DDM-MIMO: per-TX slow-time phase ramps put each TX at its own Doppler offset; with one empty
     sub-band ("empty-band DDM") the TX signals are separated and the angle is estimated correctly.
  6. Calibration: random channel gain/phase errors (1 dB, 10 deg rms) raise the sidelobes; a
     boresight corner-reflector calibration restores them.
"""
import numpy as np

ok_all = True
rng = np.random.default_rng(5)


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel else 1.0)
    ok = err <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol}{' rel' if rel else ''})")
    return ok


c = 299_792_458.0
lam = c / 77e9

print("=" * 78)
print("1. Virtual array construction")
# units of lambda/2 in azimuth (x) and lambda/2 in elevation (z)
rx = [(0, 0), (1, 0), (2, 0), (3, 0)]
tx = [(0, 0), (2, 1), (4, 0)]        # TX1, TX2 (raised by lambda/2, offset lambda), TX3 (2 lambda)
virt = [(t[0] + r[0], t[1] + r[1]) for t in tx for r in rx]
az = sorted(v[0] for v in virt if v[1] == 0)
el = sorted(v[0] for v in virt if v[1] == 1)
print(f"    virtual azimuth row (units lambda/2): {az}; elevated row: {el}")
check("8 contiguous azimuth virtual elements", float(az == list(range(8))), 1.0, 0)
check("4 elevated virtual elements (elevation capability)", len(el), 4, 0)

print("=" * 78)
print("2. Angle resolution of an N-element lambda/2 ULA")


def beam(N, u, w=None):
    n = np.arange(N)
    w = np.ones(N) if w is None else w
    return np.abs(np.exp(1j * np.pi * np.outer(u, n)) @ w) / np.sum(w)


u = np.linspace(-1, 1, 400001)       # u = sin(theta)
for N in (4, 8, 12, 86):
    b = beam(N, u)
    above = u[b >= 10 ** (-3 / 20)]
    bw3 = 2 * np.arcsin(above.max())  # rad (symmetric around 0)
    rule = 2 / N
    # first null at u = 2/N
    print(f"    N={N:3d}: 2/N rule {np.degrees(rule):6.2f} deg; -3 dB beamwidth {np.degrees(bw3):6.2f} deg "
          f"(ratio {bw3/rule:.3f}); first null at {np.degrees(np.arcsin(2/N)):.2f} deg")
    check(f"N={N}: -3 dB width ~0.886 x 2/N (small-angle)", bw3 / rule, 0.886, 0.04 if N > 4 else 0.08)
check("TI cascade 86 elements: 2/N = 1.33 deg (TI quotes ~1.4 deg)", np.degrees(2 / 86), 1.33, 0.01)

print("=" * 78)
print("3. TDM-MIMO velocity-induced phase and compensation (2 TX x 4 RX)")
Ntx, Nrx = 2, 4
Tc = 40e-6
Nchirp = 64                      # per TX
theta = np.radians(15.0)
v = 8.0                          # m/s receding (range increasing)
d_ph = lambda k: np.pi * k * np.sin(theta)       # spatial phase for virtual index k (lambda/2 spacing)
# slot s of block b: time t = (b*Ntx + s) * Tc ; phase 4 pi v t / lam (IF=TX*conj(RX): receding -> increasing)
data = np.zeros((Ntx * Nrx, Nchirp), complex)
for s_ in range(Ntx):
    for r in range(Nrx):
        k = s_ * Nrx + r
        tt = (np.arange(Nchirp) * Ntx + s_) * Tc
        data[k] = np.exp(1j * (d_ph(k) + 4 * np.pi * v * tt / lam))
data += 0.01 * (rng.standard_normal(data.shape) + 1j * rng.standard_normal(data.shape))
D = np.fft.fft(data, axis=1)
kd = np.argmax(np.sum(np.abs(D) ** 2, axis=0))
snap = D[:, kd]


def est_angle(sv):
    A = np.fft.fftshift(np.fft.fft(sv, 4096))
    om = (np.arange(4096) - 2048) * 2 * np.pi / 4096
    return np.degrees(np.arcsin(om[np.argmax(np.abs(A))] / np.pi))


th_raw = est_angle(snap)
# Doppler phase per chirp slot: omega_d estimated from the per-TX Doppler bin (sampling Ntx*Tc)
fd_bins = np.fft.fftfreq(Nchirp, Ntx * Tc)
phi_slot = 2 * np.pi * fd_bins[kd] * Tc          # phase advance per slot
comp = snap.copy()
for s_ in range(Ntx):
    comp[s_ * Nrx:(s_ + 1) * Nrx] *= np.exp(-1j * phi_slot * s_)
th_comp = est_angle(comp)
bias_pred = np.degrees(np.arcsin(np.sin(theta) + (4 * np.pi * v * Tc / lam) / (np.pi * Nrx)))  # heuristic: phase jump spread over Nrx
print(f"    v = {v} m/s, Tc = {Tc*1e6:.0f} us: slot phase 4 pi v Tc/lambda = {np.degrees(4*np.pi*v*Tc/lam):.1f} deg")
print(f"    angle estimate without compensation {th_raw:.2f} deg, with compensation {th_comp:.2f} deg (true 15)")
check("TDM: uncompensated angle is biased (> 2 deg)", float(abs(th_raw - 15) > 2), 1.0, 0)
check("TDM: Doppler-compensated angle correct", th_comp, 15.0, 0.3)
vmax_simo = lam / (4 * Tc)
print(f"    v_max: single TX {vmax_simo:.2f} m/s; TDM with {Ntx} TX {vmax_simo/Ntx:.2f} m/s; with 3 TX {vmax_simo/3:.2f} m/s")

print("=" * 78)
print("4. BPM (Hadamard) MIMO vs TDM: SNR")
Ntx = 2
H = np.array([[1, 1], [1, -1]])
trials = 20000
sigma = 1.0
h_true = np.array([1.0 + 0.5j, -0.3 + 0.8j])      # channel of TX1, TX2 at one RX
# TDM: each TX transmits alone in one of two slots
y_tdm = h_true[None, :] + sigma / np.sqrt(2) * (rng.standard_normal((trials, 2)) + 1j * rng.standard_normal((trials, 2)))
# BPM: slot a: TX1+TX2, slot b: TX1-TX2
ya = h_true[0] + h_true[1] + sigma / np.sqrt(2) * (rng.standard_normal(trials) + 1j * rng.standard_normal(trials))
yb = h_true[0] - h_true[1] + sigma / np.sqrt(2) * (rng.standard_normal(trials) + 1j * rng.standard_normal(trials))
h1 = (ya + yb) / 2
h2 = (ya - yb) / 2
err_tdm = np.var(y_tdm[:, 0] - h_true[0])
err_bpm = np.var(h1 - h_true[0])
check("BPM decode unbiased (mean of h2)", np.abs(np.mean(h2) - h_true[1]), 0.0, 0.02)
check("BPM SNR gain over TDM = 10log10(Ntx) dB", 10 * np.log10(err_tdm / err_bpm), 10 * np.log10(Ntx), 0.1)

print("=" * 78)
print("5. DDM-MIMO with an empty Doppler sub-band")
Ntx, Nrx = 3, 4
Nsub = 4                      # 4 sub-bands, 3 used, 1 empty
Nchirp = 256
Tc = 30e-6
theta = np.radians(-12.0)
v = 5.0
phase_code = [2 * np.pi * m / Nsub for m in range(Ntx)]    # per-chirp phase increment for TX m
x = np.zeros((Nrx, Nchirp), complex)
n = np.arange(Nchirp)
# virtual index k = m*Nrx + r (TX spaced Nrx * lambda/2)
for m in range(Ntx):
    for r in range(Nrx):
        k = m * Nrx + r
        x[r] += np.exp(1j * (np.pi * k * np.sin(theta) + 4 * np.pi * v * n * Tc / lam + phase_code[m] * n))
x += 0.02 * (rng.standard_normal(x.shape) + 1j * rng.standard_normal(x.shape))
X = np.fft.fft(x, axis=1)
P = np.sum(np.abs(X) ** 2, axis=0)
# peaks: target Doppler bin + m*Nchirp/Nsub
k0 = None
peaks = np.sort(np.argsort(P)[-3:])
# identify the empty band: the TX with code 0 is the one followed (cyclically) by the empty sub-band
step = Nchirp // Nsub
cand = []
for kk in peaks:
    others = sorted(((kk + m * step) % Nchirp) for m in range(Ntx))
    if all(o in peaks for o in others):
        cand.append(kk)
check("DDM: three TX peaks spaced Nchirp/Nsub bins", float(len(cand) >= 1), 1.0, 0)
k0 = cand[0]
snap = np.concatenate([X[:, (k0 + m * step) % Nchirp] for m in range(Ntx)])
th_ddm = est_angle(snap)
fd_est = np.fft.fftfreq(Nchirp, Tc)[k0]
print(f"    target Doppler bin {k0} -> v = {fd_est*lam/2:.2f} m/s (true {v}); angle {th_ddm:.2f} deg (true -12)")
check("DDM angle estimate", th_ddm, -12.0, 0.3)
print(f"    DDM unambiguous velocity: +-lambda/(4 Tc Nsub) = {lam/(4*Tc*Nsub):.2f} m/s (all TX transmit every chirp: full power)")

print("=" * 78)
print("6. Channel calibration")
N = 12
w = np.hamming(N)
g_err = 10 ** (rng.normal(0, 1.0, N) / 20) * np.exp(1j * np.radians(rng.normal(0, 10, N)))
u = np.linspace(-1, 1, 20001)


def pattern_with(errs, w):
    n = np.arange(N)
    return np.abs(np.exp(1j * np.pi * np.outer(u, n)) @ (w * errs)) / np.abs(np.sum(w * errs))


def psl_db(p):
    k = np.argmax(p)
    # find first nulls around peak
    i = k
    while i > 0 and p[i - 1] < p[i]:
        i -= 1
    j = k
    while j < len(p) - 1 and p[j + 1] < p[j]:
        j += 1
    side = np.r_[p[:i], p[j + 1:]]
    return 20 * np.log10(side.max() / p[k])


p_ideal = pattern_with(np.ones(N), w)
p_err = pattern_with(g_err, w)
cal = 1 / g_err                                # boresight corner reflector measures g_err directly
p_cal = pattern_with(g_err * cal, w)
print(f"    Hamming 12-el PSL: ideal {psl_db(p_ideal):.1f} dB, with 1 dB/10 deg errors {psl_db(p_err):.1f} dB, after calibration {psl_db(p_cal):.1f} dB")
check("calibration restores ideal sidelobes", psl_db(p_cal), psl_db(p_ideal), 0.1)
check("errors raise sidelobes by > 5 dB", float(psl_db(p_err) > psl_db(p_ideal) + 5), 1.0, 0)

print("=" * 78)
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
