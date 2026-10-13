#!/usr/bin/env python3
"""
noise_phase_jitter.py — verification for kb/07-noise-linearity/phase-noise-and-jitter.md

1. Integrate a piecewise-linear (in log-log) SSB phase-noise profile L(f) [dBc/Hz] exactly
   (each segment is a power law) -> integrated phase noise A (dBc), RMS phase jitter
   sigma_phi = sqrt(2 * 10^(A/10)) rad (factor 2: L(f) is single-sideband, phase PSD S_phi = 2 L),
   RMS time jitter sigma_t = sigma_phi/(2 pi f0).  Cross-checked against brute-force numerical integration
   and against a time-domain synthesis (random phase process with the same PSD).
2. ADC SNR limited by aperture/clock jitter: SNR = -20 log10(2 pi f_in sigma_t), combined with ideal
   quantisation SNR 6.02N + 1.76 dB.
3. Leeson model shapes (1/f^3, 1/f^2, floor) and the effect of loaded Q and signal power.
4. Reciprocal mixing: in-channel noise from a blocker = P_b + L(df) + 10 log10(B);
   inferred LO phase-noise requirement from the SX1262 blocking spec (88 dB at 1 MHz, SF12/BW125).
5. Frequency multiplication: L rises by 20 log10(N).
6. Small-angle EVM from phase noise, and FMCW range-correlation suppression factor 4 sin^2(pi f tau).

Run: python3 noise_phase_jitter.py
"""
import numpy as np

def integrate_L(fpts, Lpts, f_lo, f_hi):
    """Exact integral of 10^(L/10) over [f_lo, f_hi] with L piecewise linear in log10(f)."""
    fpts = np.asarray(fpts, float); Lpts = np.asarray(Lpts, float)
    total = 0.0
    for i in range(len(fpts)-1):
        fa, fb = fpts[i], fpts[i+1]
        a, b = max(fa, f_lo), min(fb, f_hi)
        if b <= a:
            continue
        slope = (Lpts[i+1]-Lpts[i])/np.log10(fb/fa)          # dB/decade
        La = Lpts[i] + slope*np.log10(a/fa)
        n = slope/10.0                                         # power-law exponent: S ~ f^n
        c = 10**(La/10)/a**n
        if abs(n+1) < 1e-12:
            total += c*np.log(b/a)
        else:
            total += c*(b**(n+1) - a**(n+1))/(n+1)
    return total

def jitter(f0, fpts, Lpts, f_lo, f_hi):
    P = integrate_L(fpts, Lpts, f_lo, f_hi)
    A_dBc = 10*np.log10(P)
    sphi = np.sqrt(2*P)
    return A_dBc, sphi, sphi/(2*np.pi*f0)

print("=== 1. Integrating phase noise ===")
f0 = 100e6
fpts = [100, 1e3, 1e4, 1e5, 1e6, 2e7]
Lpts = [-100, -130, -150, -160, -165, -165]
for lo, hi in ((12e3, 20e6), (1e3, 20e6), (100, 20e6)):
    A, sphi, st = jitter(f0, fpts, Lpts, lo, hi)
    # brute-force numeric check
    ff = np.logspace(np.log10(lo), np.log10(hi), 200001)
    LL = np.interp(np.log10(ff), np.log10(fpts), Lpts)
    Pn = np.trapezoid(10**(LL/10), ff)
    print(f"  f0=100 MHz XO, band {lo:>8.0f} Hz-{hi/1e6:.0f} MHz: A={A:7.2f} dBc, sigma_phi={np.degrees(sphi)*1e3:8.3f} mdeg "
          f"= {sphi*1e6:8.2f} urad, sigma_t={st*1e15:8.2f} fs  (numeric A={10*np.log10(Pn):7.2f} dBc)")

# time-domain synthesis check: generate phase with PSD S_phi(f) = 2 L(f) and measure rms
rng = np.random.default_rng(3)
fs = 50e6; N = 1 << 22
f = np.fft.rfftfreq(N, 1/fs)
Lf = np.interp(np.log10(np.maximum(f, 1)), np.log10(fpts), Lpts)
Sphi = 2*10**(Lf/10)                      # one-sided phase PSD, rad^2/Hz
band = (f >= 12e3) & (f <= 20e6)
df = fs/N
spec = np.zeros(len(f), complex)
spec[band] = np.sqrt(Sphi[band]*df/4)*(rng.standard_normal(band.sum()) + 1j*rng.standard_normal(band.sum()))
phi = np.fft.irfft(spec, n=N)*N          # real series: each bin -> 2Re(c e^jwt), var = 2E|c|^2 = S df
print(f"  time-domain synthesis rms phase (12 kHz-20 MHz) = {np.std(phi)*1e6:.2f} urad (expected ~ analytic value above)")

print("\n=== 2. Jitter-limited ADC SNR ===")
for st in (50e-15, 100e-15, 200e-15, 1e-12, 10e-12):
    row = []
    for fin in (10e6, 70e6, 433e6):
        row.append(-20*np.log10(2*np.pi*fin*st))
    print(f"  sigma_t={st*1e15:7.0f} fs: SNR at 10/70/433 MHz = " + ", ".join(f"{x:6.1f} dB" for x in row))
def combined_snr(nbits, fin, st, extra_noise_dB=None):
    snr_q = 6.02*nbits + 1.76
    snr_j = -20*np.log10(2*np.pi*fin*st)
    tot = -10*np.log10(10**(-snr_q/10) + 10**(-snr_j/10))
    return snr_q, snr_j, tot
for nb in (12, 14, 16):
    q, j, t = combined_snr(nb, 70e6, 150e-15)
    print(f"  {nb}-bit ideal ADC at 70 MHz, 150 fs clock: SNR_q={q:.1f}, SNR_j={j:.1f}, total={t:.1f} dB")

print("\n=== 3. Leeson model ===")
kT = 1.380649e-23*290
def leeson(fm, f0, QL, F_dB, Ps_dBm, fc, variant='leeson'):
    F = 10**(F_dB/10); Ps = 1e-3*10**(Ps_dBm/10)
    base = F*kT/Ps
    shape = (1 + (f0/(2*QL*fm))**2)*(1 + fc/fm)
    k = 0.5 if variant == 'leeson' else 2.0     # 'lee' variant: 2FkT/Ps (Lee & Hajimiri tank formulation)
    return 10*np.log10(k*base*shape)
for fm in (1e2, 1e3, 1e4, 1e5, 1e6, 1e7):
    print(f"  433 MHz VCO QL=20 F=10 dB Ps=0 dBm fc=10 kHz: L({fm:>9.0f} Hz) = {leeson(fm,433e6,20,10,0,1e4):7.1f} dBc/Hz"
          f"  [Lee-Hajimiri 2FkT/Ps variant: {leeson(fm,433e6,20,10,0,1e4,'lee'):7.1f}]")
for QL in (10, 50, 1e4):
    print(f"  QL={QL:>6.0f}: L(100 kHz) = {leeson(1e5,433e6,QL,10,0,1e4):7.1f} dBc/Hz (each x10 in Q -> -20 dB in 1/f^2 region)")
print(f"  Leeson corner f0/(2QL) for QL=20 at 433 MHz: {433e6/40/1e6:.2f} MHz (beyond it: flat floor)")

print("\n=== 4. Reciprocal mixing ===")
def recip(Pb_dBm, L_dBc, B):
    return Pb_dBm + L_dBc + 10*np.log10(B)
B = 125e3
NF = 6.0
N = -173.98 + 10*np.log10(B) + NF
print(f"  Receiver noise floor (NF 6 dB, 125 kHz) = {N:.1f} dBm")
for L in (-110, -120, -130, -140):
    print(f"  blocker -40 dBm at offset where L={L} dBc/Hz -> reciprocal-mixing noise {recip(-40, L, B):7.1f} dBm "
          f"({recip(-40, L, B) - N:+5.1f} dB rel. thermal floor)")
# infer SX1262 LO requirement from blocking spec
sens = -137.0; wanted = sens + 3.0; BI = 88.0
Pb = wanted + BI
# allowed interference = thermal noise (-> ~3 dB desense) ; solve L
L_req = N - Pb - 10*np.log10(B)
print(f"  SX1262 blocking 88 dB @1 MHz (SF12/BW125): blocker = {Pb:.0f} dBm; if reciprocal mixing alone caused the "
      f"3 dB desense, L(1 MHz) would be {L_req:.0f} dBc/Hz (upper bound on the LO phase noise; inference, not a spec)")

print("\n=== 5. Multiplication ===")
for Nm in (2, 4, 10, 100):
    print(f"  x{Nm}: phase noise +{20*np.log10(Nm):.1f} dB")

print("\n=== 6. EVM and FMCW range correlation ===")
for sdeg in (0.5, 1.0, 2.0, 5.0):
    s = np.radians(sdeg)
    evm = np.sqrt(2*(1-np.exp(-s**2/2)))     # exact for Gaussian phase error on constant-modulus point
    print(f"  sigma_phi={sdeg:3.1f} deg: EVM ~ {evm*100:5.2f} % = {20*np.log10(evm):6.1f} dB (small-angle: {s*100:5.2f} %)")
c = 299792458.0
for R in (1.0, 10.0, 100.0):
    tau = 2*R/c
    for fb in (1e3, 100e3, 1e6):
        sup = 10*np.log10(4*np.sin(np.pi*fb*tau)**2)
        print(f"  FMCW target at {R:5.1f} m (tau={tau*1e9:6.2f} ns): residual phase-noise factor at {fb/1e3:7.1f} kHz = {sup:7.1f} dB")
print("\nDone.")

print("\n=== 7. PLL in-band phase noise from a normalised floor ===")
# L_inband = L_norm + 10log10(f_PFD) + 20log10(N); L_norm ~ -220..-230 dBc/Hz for modern PLLs (datasheet figure of merit)
for Lnorm in (-220.0, -225.0, -230.0):
    for fout, fpfd in ((433.125e6, 32e6), (915e6, 32e6), (24e9, 100e6)):
        N = fout/fpfd
        L = Lnorm + 10*np.log10(fpfd) + 20*np.log10(N)
        print(f"  L_norm {Lnorm:.0f}: f_out {fout/1e6:8.1f} MHz, f_PFD {fpfd/1e6:5.0f} MHz (N={N:6.2f}) -> in-band floor {L:7.1f} dBc/Hz")
print("  Inside the loop bandwidth the output follows reference*N (+20logN) and this floor; outside, the free-running VCO.")
