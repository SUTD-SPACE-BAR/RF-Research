#!/usr/bin/env python3
"""W5-S14 checks for 06/mixers#N-path / Tayloe section (LPTV view of a 4-path sampling mixer).

Model: an ideal 4-path (25 % duty) quadrature sampling detector (QSD, "Tayloe detector").
A source EMF v_s(t) with series resistance R feeds a commutator that connects capacitor k
(k = 0..3) to the RF node during the k-th quarter of each LO period. Ideal switches.
Baseband outputs: I = v0 - v2, Q = v1 - v3, complex z = I - jQ (sign chosen so that an RF
input above the LO gives a positive baseband frequency).

A. Conversion: cap baseband amplitude = A*sinc(pi/4) = 0.9003 A (A = source EMF amplitude);
   differential I = 1.80 A.
B. Baseband pole f_p = 1/(2 pi N R C) (RF bandwidth 2 f_p); Tayloe's 7 MHz example.
C. Harmonic responses: only k = 1 (mod 4): 3LO at 1/3 (-9.5 dB) MIRRORED, 5LO at 1/5 (-14 dB)
   upright; 0, 2LO and 4LO cancelled.
D. Noise folding: F = sum_k |H_k|^2 / |H_1|^2 from deterministic harmonic transfer functions,
   vs closed form 1/sinc^2(pi/N) (N = 4: 0.91 dB; N = 8: 0.23 dB); Monte Carlo white-noise check.
E. In-band input impedance (fundamental) ~ R*s/(1-s), s = sinc^2(pi/4): 4.27 R.
F. ngspice transient cross-check of A/B at 7 MHz (R = 50 ohm, C = 10 nF, offset 10 kHz).
Ends with ALL PASS.
"""
import numpy as np, subprocess, tempfile, os, shutil
from scipy.signal import lfilter

ok_all = True
def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(("PASS " if cond else "FAIL ") + name)

sinc = lambda x: np.sin(x) / x
db10 = lambda x: 10 * np.log10(x)

def qsd(vs, M, N, tau):
    """vs: source EMF samples (M per LO period, value held over each step). tau = R*C in
    LO periods. Returns cap values sampled at the end of each cap's window: array (P, N)."""
    dt = 1.0 / M
    a = np.exp(-dt / tau)
    P = len(vs) // M
    vs = vs[:P * M].reshape(P, M)
    W = M // N
    caps = np.zeros((P, N))
    node = np.zeros((P, M))
    for k in range(N):
        x = vs[:, k * W:(k + 1) * W].ravel()        # concatenated active samples of path k
        y = lfilter([1 - a], [1, -a], x)            # exact RC update for a held input
        node[:, k * W:(k + 1) * W] = y.reshape(P, W)
        caps[:, k] = y.reshape(P, W)[:, -1]
    return caps, node.ravel()

def zout(caps):
    return (caps[:, 0] - caps[:, 2]) - 1j * (caps[:, 1] - caps[:, 3])

def tone(f, M, P, phase=0.0):
    t = (np.arange(P * M) + 0.5) / M                # mid-step sampling
    return np.cos(2 * np.pi * f * t + phase)

def snap(delta, P, settle):
    """choose delta so that the projection window holds an integer number of beat cycles"""
    L = P - settle
    return max(1, round(delta * L)) / L

def proj(z, delta, settle):
    """complex amplitude of z at baseband frequency delta (z sampled once per period)."""
    p = np.arange(len(z))[settle:]
    return np.mean(z[settle:] * np.exp(-2j * np.pi * delta * p))

N = 4
s1 = sinc(np.pi / 4)
print(f"sinc(pi/4) = {s1:.5f}; sinc^2 = {s1**2:.5f}")

# ---------------------------------------------------------------- A
print("\nA: conversion gain, tone at f_LO + delta, large RC")
M, tau, P = 256, 50.0, 6000
fp = 1 / (2 * np.pi * N * tau)
delta = snap(fp / 20, P, 2000)
caps, _ = qsd(tone(1 + delta, M, P), M, N, tau)
H = 1 / np.sqrt(1 + (delta / fp) ** 2)
amp_cap = abs(proj(caps[:, 0], delta, 2000)) * 2   # real cap beat cos -> amplitude
print(f"  cap amplitude {amp_cap:.4f} (expect sinc(pi/4)*H = {s1*H:.4f}); differential I {2*amp_cap:.3f}")
check("A1 cap amplitude = sinc(pi/4) within 0.5 %", abs(amp_cap / (s1 * H) - 1) < 0.005)
z = zout(caps)
zp, zm = proj(z, delta, 2000), proj(z, -delta, 2000)
print(f"  |z| at +delta {abs(zp):.4f}, at -delta {abs(zm):.2e} (USB input -> positive baseband)")
check("A2 complex output: tone above LO appears at +delta only (> 60 dB)", abs(zm) < 1e-3 * abs(zp))
check("A3 |z| = 2 sinc(pi/4) A", abs(abs(zp) / (2 * s1 * H) - 1) < 0.005)

# ---------------------------------------------------------------- B
print("\nB: baseband bandwidth f_p = 1/(2 pi N R C)")
tau, P, M = 5.0, 3000, 128
fp = 1 / (2 * np.pi * N * tau)
g = []
for d in [snap(fp / 50, P, 500), snap(fp, P, 500)]:
    caps, _ = qsd(tone(1 + d, M, P), M, N, tau)
    g.append(abs(proj(zout(caps), d, 500)))
d1, d2 = snap(fp / 50, P, 500), snap(fp, P, 500)
r = g[1] / g[0]
r_pred = np.sqrt((1 + (d1 / fp) ** 2) / (1 + (d2 / fp) ** 2))
print(f"  f_p = {fp:.5f} f_LO: gain at {d2/fp:.3f} f_p relative to near-centre = {20*np.log10(r):.2f} dB "
      f"(single-pole prediction {20*np.log10(r_pred):.2f} dB)")
check("B1 single-pole response with f_p = 1/(2 pi N R C) (within 0.15 dB)", abs(20 * np.log10(r / r_pred)) < 0.15)
R, B3 = 50.0, 1e3
C = 1 / (2 * np.pi * N * R * B3)
print(f"  Tayloe example: R = 50 ohm, 1 kHz baseband -3 dB -> C = {C*1e6:.3f} uF; RF BW 2 kHz at 7 MHz -> Q = {7e6/2e3:.0f}")
check("B2 C = 0.796 uF for 1 kHz with 50 ohm, Q = 3500", abs(C - 0.796e-6) < 0.002e-6)

# ---------------------------------------------------------------- C
print("\nC: harmonic responses (tone at k*f_LO + delta)")
tau, P, M = 5.0, 2000, 256
fp = 1 / (2 * np.pi * N * tau)
d = snap(fp / 20, P, 400)
ref = None
res = {}
for k in [1, 0, 2, 3, 4, 5, 7]:
    caps, _ = qsd(tone(k + d, M, P), M, N, tau)
    z = zout(caps)
    res[k] = (abs(proj(z, d, 400)), abs(proj(z, -d, 400)))
ref = res[1][0]
for k, (up, dn) in res.items():
    print(f"  k={k}: at +delta {20*np.log10(max(up,1e-12)/ref):7.2f} dB, at -delta {20*np.log10(max(dn,1e-12)/ref):7.2f} dB")
check("C1 3LO response 1/3 (-9.54 dB) and mirrored", abs(20*np.log10(res[3][1]/ref) + 9.54) < 0.1 and res[3][0] < 1e-3*ref)
check("C2 5LO response 1/5 (-13.98 dB), upright", abs(20*np.log10(res[5][0]/ref) + 13.98) < 0.15 and res[5][1] < 1e-3*ref)
check("C3 7LO response 1/7 mirrored", abs(20*np.log10(res[7][1]/ref) + 16.90) < 0.25)
check("C4 DC, 2LO, 4LO responses cancelled (< -60 dB)", all(max(res[k]) < 1e-3*ref for k in (0, 2, 4)))

# ---------------------------------------------------------------- D
print("\nD: noise folding — sum of |H_k|^2 over every band that lands on the output bin")
def F_det(N, M, tau=5.0, P=1200):
    fp = 1 / (2 * np.pi * N * tau)
    d = snap(fp / 10, P, 300)
    tot, h1 = 0.0, None
    for m in range(0, M // 2):
        for f in ([m + d, m - d] if m > 0 else [d]):
            caps, _ = qsd(tone(f, M, P), M, N, tau)
            Nn = N // 2
            z = sum(caps[:, k] * np.exp(-2j*np.pi*k/N) for k in range(N))  # N-path complex output
            h = abs(proj(z, d, 300))
            tot += h ** 2
            if abs(f - (1 + d)) < 1e-12:
                h1 = h
    return tot / h1 ** 2

# discrete-time prediction (window sum of W samples; harmonics up to M/2)
def F_disc(N, M):
    W = M // N
    n = np.arange(W) + 0.5
    D = lambda k: abs(np.sum(np.exp(-2j*np.pi*k*n/M)))
    ks = [k for k in range(-M//2 + 1, M//2 + 1) if (k - 1) % N == 0]
    return sum(D(k)**2 for k in ks) / D(1)**2

for Nn, Mm in [(4, 64), (8, 64)]:
    Fd = F_det(Nn, Mm)
    Fc = 1 / sinc(np.pi / Nn) ** 2
    print(f"  N={Nn}, M={Mm}: F from H_k = {Fd:.4f} ({db10(Fd):.3f} dB); discrete prediction {F_disc(Nn,Mm):.4f}; "
          f"continuous 1/sinc^2(pi/N) = {Fc:.4f} ({db10(Fc):.3f} dB)")
    check(f"D1 N={Nn}: deterministic F matches 1/sinc^2(pi/N) within 1 %", abs(Fd / Fc - 1) < 0.01)
# identity check: sum over k = 1 mod 4 of sinc^2(k pi/4) = 1
kk = np.arange(-200001, 200002)
kk = kk[(kk - 1) % 4 == 0]
S = np.sum(sinc(kk * np.pi / 4) ** 2)
check(f"D2 sum sinc^2(k pi/4), k=1 mod 4 = {S:.5f} = 1", abs(S - 1) < 1e-4)
print(f"  closed forms: N=4 {db10(1/s1**2):.2f} dB, N=8 {db10(1/sinc(np.pi/8)**2):.2f} dB, "
      f"N=2 (50 % SSB complex-pair limit) {db10(1/sinc(np.pi/2)**2):.2f} dB")
check("D3 N=4: 0.91 dB; N=8: 0.23 dB", abs(db10(1/s1**2) - 0.912) < 0.005 and abs(db10(1/sinc(np.pi/8)**2) - 0.227) < 0.005)

# Monte Carlo: white EMF noise vs a tone
rng = np.random.default_rng(14)
M, tau, P = 64, 2.0, 2 ** 17
fp = 1 / (2 * np.pi * N * tau)
sig2 = 1.0
vs = rng.normal(0, np.sqrt(sig2), P * M)
caps, _ = qsd(vs, M, N, tau)
z = zout(caps)
dlo, dhi = 0.1 * fp, 0.4 * fp
seg = 4096
nseg = len(z) // seg
Z = np.fft.fft((z[:nseg*seg].reshape(nseg, seg)) * np.hanning(seg), axis=1)
psd = np.mean(abs(Z) ** 2, axis=0) / np.sum(np.hanning(seg) ** 2)   # two-sided, fs = 1
fr = np.fft.fftfreq(seg)
sel = (fr > dlo) & (fr < dhi)
# deterministic gain^2 at the same bins (tone runs)
gains = []
for dd in np.linspace(dlo, dhi, 7):
    c2, _ = qsd(tone(1 + dd, M, 1500), M, N, tau)
    gains.append((dd, abs(proj(zout(c2), dd, 300))))
gd = np.interp(fr[sel], [g_[0] for g_ in gains], [g_[1] for g_ in gains])
S_one = 2 * sig2 / M                        # one-sided PSD of the held white EMF (per LO-normalised Hz)
Fmc = np.mean(psd[sel] / (2 * gd ** 2 * S_one))
Fd64 = F_disc(4, 64)
print(f"  Monte Carlo (2^17 periods): F = {Fmc:.3f} vs discrete prediction {Fd64:.3f} "
      f"(held-noise spectrum slightly differs from white; tolerance 6 %)")
check("D4 Monte Carlo F within 6 % of prediction", abs(Fmc / Fd64 - 1) < 0.06)

# ---------------------------------------------------------------- E
print("\nE: in-band input impedance (fundamental) of the 4-path at the LO frequency")
M, tau, P = 256, 50.0, 3000
v = tone(1.0, M, P)
caps, node = qsd(v, M, N, tau)
t = (np.arange(P * M) + 0.5) / M
last = slice((P - 200) * M, P * M)
Vn = 2 * np.mean(node[last] * np.exp(-2j * np.pi * t[last]))
Vs = 2 * np.mean(v[last] * np.exp(-2j * np.pi * t[last]))
Zin = Vn / (Vs - Vn)          # in units of R
print(f"  node fundamental / EMF = {abs(Vn/Vs):.4f} (expect sinc^2 = {s1**2:.4f}); Z_in = {Zin.real:.3f} {Zin.imag:+.3f}j x R "
      f"(expect {s1**2/(1-s1**2):.3f} R)")
check("E1 Z_in ~ 4.28 R, real", abs(Zin.real - s1**2/(1-s1**2)) < 0.05 and abs(Zin.imag) < 0.05)
Gam = (4.28 - 1) / (4.28 + 1)
print(f"  so a 50 ohm source sees ~214 ohm in band: |Gamma| = {Gam:.2f} (RL {-20*np.log10(Gam):.1f} dB) — a QSD is not matched by itself")

# ---------------------------------------------------------------- F
print("\nF: ngspice transient (7 MHz LO, R 50 ohm, C 10 nF, RF 7.010 MHz, 1 V EMF)")
if shutil.which("ngspice"):
    TLO = 1 / 7e6
    W = TLO / 4
    deck = ["* s14 4-path QSD", "VS in 0 SIN(0 1 7.01e6)", "RS in rf 50",
            ".model SW1 SW(Ron=0.5 Roff=1e9 Vt=0.5 Vh=0)"]
    for k in range(4):
        deck += [f"VC{k} g{k} 0 PULSE(0 1 {k*W:.6e} 0.2n 0.2n {W-0.4e-9:.6e} {TLO:.6e})",
                 f"S{k} rf c{k} g{k} 0 SW1", f"C{k} c{k} 0 10n IC=0"]
    tmp = tempfile.mkdtemp()
    out = os.path.join(tmp, "q.txt")
    deck += [".tran 2n 300u 0 2n UIC", ".control", "run",
             f"wrdata {out} v(c0) v(c1) v(c2) v(c3)", "quit", ".endc", ".end"]
    ck = os.path.join(tmp, "q.cir")
    open(ck, "w").write("\n".join(deck))
    subprocess.run(["ngspice", "-b", ck], capture_output=True, text=True, timeout=600)
    dat = np.loadtxt(out)
    tt, c0 = dat[:, 0], dat[:, 1]
    m = tt > 100e-6
    # average over each LO period to remove the RF ripple, then fit the 10 kHz beat
    tg = np.arange(100e-6, 300e-6, TLO)
    c0g = np.interp(tg, tt[m], c0[m])
    ph = np.exp(-2j * np.pi * 10e3 * tg)
    amp = 2 * abs(np.mean(c0g * ph))
    fp = 1 / (2 * np.pi * 4 * 50.5 * 10e-9)   # R + Ron
    exp_amp = s1 / np.sqrt(1 + (10e3 / fp) ** 2)
    print(f"  ngspice cap beat amplitude {amp:.4f} V; LPTV prediction {exp_amp:.4f} V (f_p = {fp/1e3:.1f} kHz)")
    check("F1 ngspice within 2 % of sinc(pi/4)/sqrt(1+(df/fp)^2)", abs(amp / exp_amp - 1) < 0.02)
    shutil.rmtree(tmp)
else:
    print("  ngspice not found — skipped")

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
