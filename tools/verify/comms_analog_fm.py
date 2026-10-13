#!/usr/bin/env python3
"""Verification for kb/10-comms-modulation/analog-modulation-am-fm-pm-ssb.md

Run:  python3 tools/verify/comms_analog_fm.py      (~10 s)

Checks:
  1. FM/PM line spectrum = Bessel coefficients J_n(beta); power conservation sum J_n^2 = 1;
     carrier nulls at beta = 2.405, 5.520, 8.654; fraction of power inside Carson's bandwidth
     2(beta+1) f_m for beta = 0.2 ... 10.
  2. FM discriminator output SNR above threshold = (3/2) beta^2 SNR_C (tone modulation) by
     complex-baseband simulation, and the collapse below ~10 dB CNR in the Carson bandwidth
     (threshold effect).
  3. AM figures of merit: envelope detection of full-carrier AM = mu^2/(2+mu^2) (1/3 at mu=1);
     coherent DSB-SC = 1.
  4. Pre-emphasis/de-emphasis SNR improvement for 75 us and 50 us with W = 15 kHz
     (closed form, checked by numerical integration).
  5. Capture effect: discriminator output SIR vs input D/U ratio for two co-channel FM signals.
  6. NBFM/Carson numbers used on the page (APRS/voice).
"""
import numpy as np
from scipy import special, integrate

rng = np.random.default_rng(21)
ok_all = True


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel else 1.0)
    ok = err <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.5g}, expected {want:.5g} (tol {tol}{' rel' if rel else ''})")

# ------------------------------------------------------------------------------------ 1
fs = 1_000_000.0
fm = 1000.0
t = np.arange(int(fs * 0.1)) / fs            # 0.1 s -> 10 Hz bins, fm on a bin
for beta in (0.5, 2.405, 5.0):
    x = np.exp(1j * beta * np.sin(2 * np.pi * fm * t))
    X = np.fft.fft(x) / len(x)
    for nidx in (0, 1, 2, 3):
        k = int(round(nidx * fm * 0.1))
        check(f"FM line n={nidx}, beta={beta}: |X| = |J_n(beta)|", abs(X[k]), abs(special.jv(nidx, beta)), 1e-6)
for b in (0.5, 3.0, 10.0):
    n = np.arange(-60, 61)
    check(f"sum J_n^2 = 1 at beta={b}", np.sum(special.jv(n, b) ** 2), 1.0, 1e-12)
zeros = special.jn_zeros(0, 3)
for z, want in zip(zeros, (2.405, 5.520, 8.654)):
    check("carrier null beta", z, want, 1e-3)
print("  power fraction inside Carson bandwidth 2(beta+1)fm (lines |n| <= beta+1):")
for b in (0.2, 0.5, 1, 2, 5, 10):
    nmax = int(np.floor(b + 1))
    n = np.arange(-nmax, nmax + 1)
    frac = np.sum(special.jv(n, b) ** 2)
    print(f"    beta={b:5.1f}: {100*frac:6.2f} %")
    if b >= 1:
        ok = frac > 0.97
        ok_all &= ok
check("Carson (|n|<=2) contains 99.9 % at beta=1", np.sum(special.jv(np.arange(-2, 3), 1.0) ** 2), 0.9992, 1e-3)

# ------------------------------------------------------------------------------------ 2


def brickwall(x, fs, bw_two_sided):
    X = np.fft.fft(x)
    f = np.fft.fftfreq(len(x), 1 / fs)
    X[np.abs(f) > bw_two_sided / 2] = 0
    return np.fft.ifft(X)


def fm_output_snr(cnr_db, dev=5000.0, fmod=1000.0, W=1250.0, fs=400_000.0, dur=2.0, carson_if=True):
    n = int(fs * dur)
    tt = np.arange(n) / fs
    A = 1.0
    phase = dev / fmod * np.sin(2 * np.pi * fmod * tt)          # beta = dev/fm (rad)
    s = A * np.exp(1j * phase)
    BT = 2 * (dev + W)
    Npsd = A ** 2 / (10 ** (cnr_db / 10) * BT)            # complex noise PSD (W/Hz)
    noise = np.sqrt(Npsd * fs / 2) * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    r = s + noise
    if carson_if:
        r = brickwall(r, fs, BT)
    inst_f = np.diff(np.unwrap(np.angle(r))) * fs / (2 * np.pi)
    out = np.real(brickwall(inst_f, fs, 2 * W))
    ref = dev * np.cos(2 * np.pi * fmod * tt[1:] - np.pi * fmod / fs)   # half-sample delay of diff
    a = np.dot(out, ref) / np.dot(ref, ref)
    err = out - a * ref
    snr_o = np.mean((a * ref) ** 2) / np.mean(err ** 2)
    snr_c = A ** 2 / (Npsd * W)                         # channel SNR in message bandwidth
    return 10 * np.log10(snr_o), 10 * np.log10(snr_c)


dev, W = 5000.0, 1250.0
beta = dev / W
print(f"  FM discriminator, tone, deviation {dev:.0f} Hz, W = {W:.0f} Hz (beta = {beta:.1f}), IF = Carson {2*(dev+W):.0f} Hz:")
for cnr in (25.0, 18.0, 13.0, 10.0, 7.0, 4.0):
    so, sc = fm_output_snr(cnr)
    th = sc + 10 * np.log10(1.5 * beta ** 2)
    print(f"    CNR(Carson) {cnr:5.1f} dB: SNR_C {sc:5.1f} dB, output SNR {so:5.1f} dB, theory {th:5.1f} dB, shortfall {th - so:5.1f} dB")
    if cnr == 25.0:
        check("FM output SNR = 1.5 beta^2 SNR_C at CNR 25 dB", so, th, 0.5)
    if cnr == 18.0:
        check("FM output SNR above threshold at CNR 18 dB", so, th, 0.8)
    if cnr == 4.0:
        ok = th - so > 6
        ok_all &= ok
        print(f"[{'PASS' if ok else 'FAIL'}] below threshold (CNR 4 dB) output SNR collapses (> 6 dB short)")

# ------------------------------------------------------------------------------------ 3
fs3 = 100_000.0
n = int(fs3 * 4)
tt = np.arange(n) / fs3
Wm = 3000.0
fmod = 1000.0
for mu in (0.8, 0.5):   # (mu = 1 approaches the formula only slowly: envelope touches zero)
    A = 1.0
    x = A * (1 + mu * np.cos(2 * np.pi * fmod * tt))
    Npsd = 1e-8
    noise = np.sqrt(Npsd * fs3 / 2) * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    r = brickwall(x + noise, fs3, 2 * Wm)
    env = np.abs(r)
    out = np.real(brickwall(env - np.mean(env), fs3, 2 * Wm))
    ref = mu * A * np.cos(2 * np.pi * fmod * tt)
    a = np.dot(out, ref) / np.dot(ref, ref)
    snr_o = np.mean((a * ref) ** 2) / np.mean((out - a * ref) ** 2)
    snr_c = A ** 2 * (1 + mu ** 2 / 2) / (Npsd * Wm)
    check(f"AM envelope detector figure of merit, mu={mu}", snr_o / snr_c, mu ** 2 / (2 + mu ** 2), 0.05, rel=True)
# DSB-SC coherent
x = np.cos(2 * np.pi * fmod * tt)
noise = np.sqrt(Npsd * fs3 / 2) * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
r = brickwall(x + noise, fs3, 2 * Wm)
out = np.real(r)
snr_o = np.mean(x ** 2) / np.mean((out - x) ** 2)
snr_c = np.mean(x ** 2) / (Npsd * Wm)
check("DSB-SC coherent figure of merit", snr_o / snr_c, 1.0, 0.05, rel=True)

# ------------------------------------------------------------------------------------ 4


def emphasis_gain(tau, Wa):
    f1 = 1 / (2 * np.pi * tau)
    r = Wa / f1
    closed = r ** 3 / (3 * (r - np.arctan(r)))
    num = integrate.quad(lambda f: f ** 2, 0, Wa)[0]
    den = integrate.quad(lambda f: f ** 2 / (1 + (f / f1) ** 2), 0, Wa)[0]
    return 10 * np.log10(closed), 10 * np.log10(num / den)


for tau, want in ((75e-6, 13.2), (50e-6, 10.2)):
    c, nmr = emphasis_gain(tau, 15e3)
    check(f"de-emphasis improvement {tau*1e6:.0f} us, W=15 kHz (closed form) [dB]", c, want, 0.1)
    check(f"  closed form == numerical integral ({tau*1e6:.0f} us)", c, nmr, 1e-6)

# ------------------------------------------------------------------------------------ 5
fs5 = 200_000.0
n = int(fs5 * 1)
tt = np.arange(n) / fs5
s1 = np.exp(1j * 3000 / 700 * np.sin(2 * np.pi * 700 * tt))       # wanted: 700 Hz tone, 3 kHz dev
print("  capture effect: two co-channel FM signals (wanted 700 Hz tone, interferer 1100 Hz tone, both 3 kHz dev)")
res5 = {}
for du_db in (1.0, 3.0, 6.0, 10.0):
    a2 = 10 ** (-du_db / 20)
    s2 = a2 * np.exp(1j * (3000 / 1100 * np.sin(2 * np.pi * 1100 * tt) + 1.0))
    r = s1 + s2
    fi = np.diff(np.unwrap(np.angle(r))) * fs5 / (2 * np.pi)
    out = np.real(brickwall(fi, fs5, 2 * 3000))
    ref1 = 3000 * np.cos(2 * np.pi * 700 * tt[1:])
    a = np.dot(out, ref1) / np.dot(ref1, ref1)
    sir_out = 10 * np.log10(np.mean((a * ref1) ** 2) / np.mean((out - a * ref1) ** 2))
    res5[du_db] = sir_out
    print(f"    input D/U {du_db:4.1f} dB -> output SIR {sir_out:5.1f} dB")
ok = res5[10.0] > 10.0 + 8 and res5[6.0] > 6.0 + 5
ok_all &= ok
print(f"[{'PASS' if ok else 'FAIL'}] FM capture: output SIR exceeds input D/U by > 5-8 dB once D/U >= 6 dB")

# ------------------------------------------------------------------------------------ 6
check("NBFM Carson, 5 kHz dev, 3 kHz audio [kHz]", 2 * (5 + 3), 16, 0)
check("NBFM Carson, 2.5 kHz dev, 3 kHz audio [kHz] (NTIA 11K0F3E)", 2 * (2.5 + 3), 11, 0)
check("Broadcast FM Carson 75 kHz dev, 15 kHz [kHz] (NTIA 180KF3E)", 2 * (75 + 15), 180, 0)
check("FM figure of merit broadcast mono beta=5 [dB]", 10 * np.log10(1.5 * 25), 15.74, 0.01)

print("\nOVERALL:", "PASS" if ok_all else "FAIL")
