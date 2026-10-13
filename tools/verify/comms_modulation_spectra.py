#!/usr/bin/env python3
"""Verification for kb/10-comms-modulation/digital-modulation-psk-qam-fsk.md

Run:  python3 tools/verify/comms_modulation_spectra.py      (~30 s)

Checks:
  1. Tone orthogonality: coherent (real inner product) zero at spacing 1/(2T);
     non-coherent (complex inner product) zero only at spacing k/T.
  2. 99 % occupied bandwidth (two-sided, in units of bit rate Rb) of rectangular BPSK, QPSK,
     MSK and GMSK (BT = 0.5, 0.3, 0.25) from averaged periodograms of simulated complex-baseband
     signals; compared with analytic PSD integrals and the ITU-R SM.328 K-factors quoted in
     NTIA Annex J (MSK 1.28?, GMSK 1.03/0.91/0.86).
  3. PAPR: constellation peak-to-average (16-QAM 2.55 dB, 64-QAM 3.68 dB), and CCDF of
     RRC-filtered (beta = 0.35) QPSK/16-QAM instantaneous power, plus constant envelope of GMSK.
  4. EVM <-> SNR: EVM_rms = 1/sqrt(SNR) for a noise-limited ideal receiver.
  5. OQPSK / pi/4-QPSK avoid zero crossings (max phase jump 90 / 135 degrees) vs QPSK (180).
"""
import numpy as np
from scipy import special, signal, integrate

rng = np.random.default_rng(11)
ok_all = True


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel else 1.0)
    ok = err <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.5g}, expected {want:.5g} (tol {tol}{' rel' if rel else ''})")

# ------------------------------------------------------------------------------------ 1
T = 1.0
t = np.linspace(0, T, 20001)
for df, want_coh, want_nc in ((0.5, 0.0, None), (1.0, 0.0, 0.0)):
    c = np.trapezoid(np.cos(2 * np.pi * 10 * t) * np.cos(2 * np.pi * (10 + df) * t), t) / (T / 2)
    nc = abs(np.trapezoid(np.exp(2j * np.pi * df * t), t)) / T
    check(f"coherent correlation, spacing {df}/T", c, want_coh, 1e-3)
    if want_nc is not None:
        check(f"non-coherent |correlation|, spacing {df}/T", nc, want_nc, 1e-3)
nc_half = abs(np.trapezoid(np.exp(2j * np.pi * 0.5 * t), t)) / T
check("non-coherent |corr| at 1/(2T) is 2/pi (NOT orthogonal)", nc_half, 2 / np.pi, 1e-3)

# ------------------------------------------------------------------------------------ 2
sps = 32
nbits = 40000


def obw99(x, fs):
    f, P = signal.welch(x, fs=fs, nperseg=4096, return_onesided=False, window="hann")
    idx = np.argsort(f)
    f, P = f[idx], P[idx]
    c = np.cumsum(P) / np.sum(P)
    lo = np.interp(0.005, c, f)
    hi = np.interp(0.995, c, f)
    return hi - lo


def gaussian_pulse_phase(bt, sps, span=4):
    # frequency pulse g(t) = rect conv gaussian; phase increment normalised to h*pi per bit
    tt = np.arange(-span * sps, span * sps + 1) / sps
    sig = np.sqrt(np.log(2)) / (2 * np.pi * bt)
    g = 0.5 * (special.erf((tt + 0.5) / (np.sqrt(2) * sig)) - special.erf((tt - 0.5) / (np.sqrt(2) * sig)))
    return g / g.sum()


def cpfsk(bits, h, sps, bt=None):
    a = 2 * bits - 1.0
    up = np.zeros(len(a) * sps)
    up[::sps] = a
    if bt is None:
        g = np.ones(sps) / sps
    else:
        g = gaussian_pulse_phase(bt, sps)
    freq = np.convolve(up, g)                   # sum per bit = a_k
    phase = np.pi * h * np.cumsum(freq)
    return np.exp(1j * phase)


fs = sps * 1.0   # Rb = 1
bits = rng.integers(0, 2, nbits)
bpsk = np.repeat(2 * bits - 1.0, sps)
q = rng.integers(0, 4, nbits // 2)
qpsk = np.repeat(np.exp(1j * (np.pi / 4 + np.pi / 2 * q)), 2 * sps)  # Rs = Rb/2
res = {}
# (rectangular BPSK/QPSK are not simulated: their sinc^2 tails alias at any practical sps,
#  so their 99 % bandwidths are computed analytically below)
res["MSK"] = obw99(cpfsk(bits, 0.5, sps), fs)
for bt in (0.5, 0.3, 0.25):
    res[f"GMSK BT={bt}"] = obw99(cpfsk(bits, 0.5, sps, bt), fs)
res["CPFSK h=0.7 (rect)"] = obw99(cpfsk(bits, 0.7, sps), fs)
for k, v in res.items():
    print(f"  99% occupied BW (two-sided) {k:20s}: {v:6.2f} x Rb")

# analytic 99% for rectangular BPSK: PSD sinc^2(f T), find B with 99% power
def frac_sinc2(B):
    return integrate.quad(lambda f: np.sinc(f) ** 2, -B / 2, B / 2, limit=2000)[0]
from scipy.optimize import brentq
b_bpsk = brentq(lambda B: frac_sinc2(B) - 0.99, 1, 40)
print(f"  analytic 99% BW rect BPSK: {b_bpsk:.2f} x Rb")
check("rect BPSK 99% BW analytic ~ 20.6 Rb", b_bpsk, 20.6, 0.3)
# MSK analytic PSD: S(f) ~ [cos(2 pi f T)/(1 - 16 f^2 T^2)]^2 (T = bit time)
msk_psd = lambda f: (np.cos(2 * np.pi * f) / (1 - 16 * f ** 2 + 1e-15)) ** 2
tot = integrate.quad(msk_psd, -60, 60, limit=4000, points=[-0.25, 0.25])[0]
b_msk = brentq(lambda B: integrate.quad(msk_psd, -B / 2, B / 2, limit=2000, points=[-0.25, 0.25])[0] / tot - 0.99, 0.5, 5)
print(f"  analytic 99% BW MSK: {b_msk:.3f} x Rb")
check("MSK 99% BW analytic ~ 1.18 Rb (Pasupathy/Sklar)", b_msk, 1.18, 0.02)
check("MSK 99% BW simulated vs analytic", res["MSK"], b_msk, 0.05, rel=True)
check("GMSK BT=0.5 99% BW vs ITU-R SM.328 K=1.03", res["GMSK BT=0.5"], 1.03, 0.06, rel=True)
check("GMSK BT=0.3 99% BW vs ITU-R SM.328 K=0.91", res["GMSK BT=0.3"], 0.91, 0.06, rel=True)
check("GMSK BT=0.25 99% BW vs ITU-R SM.328 K=0.86", res["GMSK BT=0.25"], 0.86, 0.06, rel=True)
print(f"  analytic 99% BW rect QPSK (Rs = Rb/2): {b_bpsk/2:.2f} x Rb")
fnull = brentq(lambda B: frac_sinc2(B) - 0.90, 0.5, 5)
print(f"  rect BPSK: 90% of power within {fnull:.2f} x Rb (two-sided); null-to-null = 2 Rb holds {frac_sinc2(2.0)*100:.1f}%")
check("rect BPSK power inside main lobe (null-to-null) = 90.3%", frac_sinc2(2.0), 0.903, 0.002)
print("  NOTE: NTIA Annex J lists K=1.28 for 'MSK (unfiltered)'; analytic 99% is 1.18 Rb -> recorded as a discrepancy.")

# ------------------------------------------------------------------------------------ 3
def papr_const(points):
    p = np.abs(points) ** 2
    return 10 * np.log10(p.max() / p.mean())


lev4 = np.array([-3, -1, 1, 3.0])
qam16 = (lev4[:, None] + 1j * lev4[None, :]).ravel()
lev8 = np.arange(-7, 8, 2.0)
qam64 = (lev8[:, None] + 1j * lev8[None, :]).ravel()
check("16-QAM constellation PAPR [dB]", papr_const(qam16), 2.553, 0.01)
check("64-QAM constellation PAPR [dB]", papr_const(qam64), 3.680, 0.01)


def rrc(beta, sps, span):
    tt = np.arange(-span * sps, span * sps + 1) / sps
    h = np.zeros_like(tt)
    for i, x in enumerate(tt):
        if abs(x) < 1e-9:
            h[i] = 1 - beta + 4 * beta / np.pi
        elif abs(abs(x) - 1 / (4 * beta)) < 1e-9:
            h[i] = beta / np.sqrt(2) * ((1 + 2 / np.pi) * np.sin(np.pi / (4 * beta)) + (1 - 2 / np.pi) * np.cos(np.pi / (4 * beta)))
        else:
            h[i] = (np.sin(np.pi * x * (1 - beta)) + 4 * beta * x * np.cos(np.pi * x * (1 + beta))) / (np.pi * x * (1 - (4 * beta * x) ** 2))
    return h / np.sqrt(np.sum(h ** 2))


sps2 = 8
h = rrc(0.35, sps2, 8)


def shaped(syms):
    up = np.zeros(len(syms) * sps2, complex)
    up[::sps2] = syms
    return np.convolve(up, h)[len(h):-len(h)]


def papr_ccdf(x, p=1e-4):
    pw = np.abs(x) ** 2 / np.mean(np.abs(x) ** 2)
    return 10 * np.log10(np.quantile(pw, 1 - p))


nsym = 200000
qp = shaped(np.exp(1j * (np.pi / 4 + np.pi / 2 * rng.integers(0, 4, nsym))))
q16 = shaped(qam16[rng.integers(0, 16, nsym)])
papr_q = papr_ccdf(qp)
papr_16 = papr_ccdf(q16)
print(f"  RRC beta=0.35 QPSK: PAPR exceeded 1e-4 of the time = {papr_q:.2f} dB")
print(f"  RRC beta=0.35 16-QAM: PAPR exceeded 1e-4 of the time = {papr_16:.2f} dB")
ok = 3.0 < papr_q < 5.5 and papr_16 > papr_q + 1.0
ok_all &= ok
print(f"[{'PASS' if ok else 'FAIL'}] RRC-shaped QPSK PAPR in 3-5.5 dB and 16-QAM > QPSK + 1 dB")
g = cpfsk(bits[:5000], 0.5, 8, 0.3)
check("GMSK constant envelope PAPR [dB]", 10 * np.log10(np.max(np.abs(g) ** 2) / np.mean(np.abs(g) ** 2)), 0.0, 1e-6)
for beta in (0.2, 0.5):
    h = rrc(beta, sps2, 8)
    print(f"  RRC beta={beta} QPSK PAPR@1e-4: {papr_ccdf(shaped(np.exp(1j*(np.pi/4+np.pi/2*rng.integers(0,4,nsym))))):.2f} dB")

# ------------------------------------------------------------------------------------ 4
for snr_db in (20.0, 30.0):
    n = 200000
    s = qam16[rng.integers(0, 16, n)] / np.sqrt(10)
    snr = 10 ** (snr_db / 10)
    r = s + np.sqrt(1 / snr / 2) * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    evm = np.sqrt(np.mean(np.abs(r - s) ** 2) / np.mean(np.abs(s) ** 2))
    check(f"EVM_rms at SNR {snr_db} dB = 1/sqrt(SNR)", evm, 1 / np.sqrt(snr), 0.02, rel=True)

# ------------------------------------------------------------------------------------ 5
qs = np.pi / 4 + np.pi / 2 * rng.integers(0, 4, 20000)
jumps_qpsk = np.max(np.abs(np.angle(np.exp(1j * np.diff(qs)))))
check("QPSK max phase jump [deg]", np.degrees(jumps_qpsk), 180.0, 1e-6)
d = np.array([np.pi / 4, 3 * np.pi / 4, -3 * np.pi / 4, -np.pi / 4])[rng.integers(0, 4, 20000)]
p4 = np.cumsum(d)
check("pi/4-DQPSK max phase jump [deg]", np.degrees(np.max(np.abs(np.angle(np.exp(1j * np.diff(p4)))))), 135.0, 1e-6)
# OQPSK: I and Q transitions offset by half a symbol -> only one rail changes at a time -> max 90 deg
I = 2 * rng.integers(0, 2, 20000) - 1
Qr = 2 * rng.integers(0, 2, 20000) - 1
seq = []
for k in range(len(I) - 1):
    seq.append(I[k] + 1j * Qr[k])
    seq.append(I[k + 1] + 1j * Qr[k])     # I changes first, half a symbol later Q changes
seq = np.array(seq)
check("OQPSK max phase jump [deg]", np.degrees(np.max(np.abs(np.angle(seq[1:] / seq[:-1])))), 90.0, 1e-6)

print("\nOVERALL:", "PASS" if ok_all else "FAIL")
