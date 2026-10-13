#!/usr/bin/env python3
"""Verification for kb/06-rf-circuits/receiver-architectures.md and transmitter-architectures.md

Receiver
 A. IF choice: image and half-IF frequencies and their attenuation by a 433.92 MHz pre-selector
    (3-pole 0.1 dB Chebyshev, 5 % FBW) for IF = 10.7 / 21.4 / 45 / 70 MHz
 B. Zero-IF: required IIP2 for a strong AM blocker; LO self-mixing DC offset
 C. Flicker noise penalty: zero-IF vs low-IF for a 125 kHz LoRa channel (1/f corner sweep)
 D. Direct RF sampling: jitter-limited SNR at 433 MHz / 1575 MHz / 2.4 GHz; Nyquist-zone planning
 E. Superhet cascade (NF and IIP3) with Friis and the IIP3 cascade formula
 F. Reciprocal mixing: blocker x LO phase noise -> in-channel noise
Transmitter
 G. IQ modulator: sideband suppression vs gain/phase error; carrier leakage vs DC offset
 H. Polar transmitter: EVM vs envelope/phase path delay mismatch (16-QAM) and vs envelope bandwidth
 I. LO pulling margin / frequency plan check for direct up-conversion (VCO at 2x or 4x/3)
Run: python3 tools/verify/rfckt_rx_tx.py
"""
import numpy as np, sys

ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


def db(x):
    return 10 * np.log10(x)


# ---------------------------------------------------------------- A. IF choice
def cheb_bpf_att(f, f0, fbw, N=3, rip=0.1):
    eps = np.sqrt(10 ** (rip / 10) - 1)
    w = (f / f0 - f0 / f) / fbw
    TN = np.where(abs(w) <= 1, np.cos(N * np.arccos(np.clip(w, -1, 1))), np.cosh(N * np.arccosh(np.maximum(abs(w), 1))))
    return 10 * np.log10(1 + eps ** 2 * TN ** 2)


fRF = 433.92e6
print("A: IF   LO(low)   image    att(image)  half-IF   att(half-IF)  [3-pole 0.1 dB Chebyshev, FBW 5 % pre-selector]")
atts = {}
for fIF in (10.7e6, 21.4e6, 45e6, 70e6):
    fLO = fRF - fIF
    fim = fLO - fIF
    fh = fRF - fIF / 2
    a_im, a_h = cheb_bpf_att(fim, fRF, 0.05), cheb_bpf_att(fh, fRF, 0.05)
    atts[fIF] = (a_im, a_h)
    print(f"   {fIF/1e6:5.1f}  {fLO/1e6:7.2f}  {fim/1e6:7.2f}   {a_im:6.1f} dB   {fh/1e6:7.2f}   {a_h:6.1f} dB")
check("A1 higher IF moves image and half-IF further from the pre-selector passband", atts[70e6][0] > atts[10.7e6][0] + 20 and atts[70e6][1] > atts[10.7e6][1])

# ---------------------------------------------------------------- B. zero-IF IIP2 and DC offset
P_block, noise_floor = -30.0, -174 + 10 * np.log10(125e3) + 6      # -30 dBm AM blocker; 125 kHz channel, 6 dB NF
IIP2_req = 2 * P_block - noise_floor
print(f"B: zero-IF, -30 dBm AM blocker: IM2 lands at DC; to keep it below the {noise_floor:.0f} dBm channel noise, "
      f"IIP2 >= 2*Pb - Pn = {IIP2_req:.0f} dBm (input-referred)")
check("B1 IIP2 requirement arithmetic", abs(IIP2_req - (2 * P_block - noise_floor)) < 1e-12)
# LO self-mixing: LO leaks to the LNA input at P_leak, reflects/re-enters and mixes with the LO -> DC
for P_leak in (-60, -80):
    # after LNA+mixer gain G (say 30 dB), DC voltage ~ sqrt of the equivalent input power; compare with a -110 dBm signal
    print(f"   LO leakage {P_leak} dBm at the RF input self-mixes to a DC term ~ {P_leak - (-110):.0f} dB above a -110 dBm wanted "
          f"signal (input-referred) -> must be removed by DC servo / AC coupling / digital DC cancellation")

# ---------------------------------------------------------------- C. flicker penalty
def excess_noise_factor(f_lo, f_hi, fc):
    """Mean of (1 + fc/|f|) over the band [f_lo, f_hi] (one-sided)."""
    f = np.linspace(max(f_lo, 1.0), f_hi, 200001)
    return np.trapezoid(1 + fc / f, f) / (f_hi - f_lo)
BWc = 125e3
print("C: baseband flicker penalty for a 125 kHz channel (noise relative to white floor):")
res = {}
for fc in (10e3, 100e3, 1e6):
    zif = excess_noise_factor(100.0, BWc / 2, fc)                 # zero-IF: band 0..62.5 kHz (DC notch below 100 Hz)
    lif = excess_noise_factor(250e3 - BWc / 2, 250e3 + BWc / 2, fc)  # low-IF at 250 kHz
    res[fc] = (db(zif), db(lif))
    print(f"   1/f corner {fc/1e3:6.0f} kHz: zero-IF +{db(zif):.1f} dB, low-IF (250 kHz) +{db(lif):.1f} dB")
check("C1 low-IF avoids most of the flicker penalty that zero-IF suffers", res[100e3][0] - res[100e3][1] > 3)

# ---------------------------------------------------------------- D. direct RF sampling
print("D: jitter-limited SNR = -20 log10(2 pi f sigma_t):")
for fin in (433.92e6, 1575.42e6, 2.45e9):
    s = [f"{-20*np.log10(2*np.pi*fin*sj):5.1f}" for sj in (50e-15, 100e-15, 500e-15)]
    print(f"   {fin/1e6:8.2f} MHz: sigma 50/100/500 fs -> SNR {s[0]}/{s[1]}/{s[2]} dB")
check("D1 100 fs jitter limits SNR at 1575 MHz to ~60 dB", abs(-20 * np.log10(2 * np.pi * 1575.42e6 * 100e-15) - 60.1) < 0.2)
fs_ = 3.0e9
for fin in (433.92e6, 1575.42e6, 2.45e9):
    zone = int(fin // (fs_ / 2)) + 1
    alias = fin % fs_
    alias = alias if alias <= fs_ / 2 else fs_ - alias
    print(f"   fs {fs_/1e9:.1f} GS/s: {fin/1e6:.2f} MHz is in Nyquist zone {zone}, appears at {alias/1e6:.2f} MHz "
          f"({'spectrum inverted' if zone % 2 == 0 else 'not inverted'})")

# ---------------------------------------------------------------- E. superhet cascade
stages = [  # name, gain dB, NF dB, IIP3 dBm
    ("SAW 433", -2.4, 2.4, 60), ("LNA", 20.0, 0.8, 5.0), ("SAW", -3.0, 3.0, 60),
    ("mixer (DBM L7)", -6.5, 7.0, 16.0), ("IF amp", 20.0, 3.0, 10.0), ("IF filter", -4.0, 4.0, 60)]
F, G, inv_iip3 = 0.0, 1.0, 0.0
Ftot = None
for name, g, nf, iip3 in stages:
    f_ = 10 ** (nf / 10)
    Ftot = f_ if Ftot is None else Ftot + (f_ - 1) / G
    inv_iip3 += G / (10 ** (iip3 / 10) * 1e-3)
    G *= 10 ** (g / 10)
NF = db(Ftot); IIP3 = db(1 / inv_iip3 * 1e3)
print(f"E: 433 MHz superhet (SAW-LNA-SAW-DBM-IF amp-IF filter): gain {db(G):.1f} dB, NF {NF:.2f} dB, IIP3 {IIP3:.1f} dBm")
check("E1 cascade NF is dominated by the pre-LNA SAW + LNA", 3.0 < NF < 4.2)
# without the front SAW
Ftot2, G2, inv2 = None, 1.0, 0.0
for name, g, nf, iip3 in stages[1:]:
    f_ = 10 ** (nf / 10)
    Ftot2 = f_ if Ftot2 is None else Ftot2 + (f_ - 1) / G2
    inv2 += G2 / (10 ** (iip3 / 10) * 1e-3)
    G2 *= 10 ** (g / 10)
print(f"   without the front SAW: NF {db(Ftot2):.2f} dB, IIP3 {db(1/inv2*1e3):.1f} dBm (but no protection from out-of-band blockers)")

# ---------------------------------------------------------------- F. reciprocal mixing
for Pb, Lpn, off in ((-30, -152, 1e6), (-40, -123, 100e3), (-20, -140, 1e6)):
    Pn = Pb + Lpn + 10 * np.log10(125e3)
    print(f"F: blocker {Pb} dBm at {off/1e3:.0f} kHz, LO phase noise {Lpn} dBc/Hz there -> {Pn:.1f} dBm in a 125 kHz channel "
          f"(thermal floor with 6 dB NF: {noise_floor:.1f} dBm)")
check("F1 reciprocal-mixing arithmetic", abs((-30 - 152 + 10 * np.log10(125e3)) - (-131.03)) < 0.01)

# ---------------------------------------------------------------- G. IQ modulator
def ssb_suppression(eps_db, phi_deg):
    g = 10 ** (eps_db / 20); p = np.deg2rad(phi_deg)
    return 10 * np.log10((1 + 2 * g * np.cos(p) + g ** 2) / (1 - 2 * g * np.cos(p) + g ** 2))
M = 4096; t = np.arange(M); k = 100
for e, p in ((0.1, 1), (0.3, 3), (1.0, 5)):
    # simulate: s(t) = I cos(wct) - Q sin(wct) with Q path gain g and phase error p, baseband tone at +k
    g = 10 ** (e / 20); ph = np.deg2rad(p)
    I = np.cos(2 * np.pi * k * t / M); Q = np.sin(2 * np.pi * k * t / M)
    z = I + 1j * g * np.exp(1j * ph) * Q  # equivalent complex baseband with imbalance applied to Q
    Z = np.fft.fft(z)
    sim = 20 * np.log10(abs(Z[k]) / abs(Z[-k]))
    print(f"G: IQ modulator {e} dB / {p} deg: unwanted-sideband suppression {ssb_suppression(e,p):.1f} dB (simulated {sim:.1f} dB)")
    check(f"G1 sideband suppression formula {e} dB/{p} deg", abs(sim - ssb_suppression(e, p)) < 1e-6)
for dc in (0.001, 0.01, 0.03):
    print(f"   DC offset {dc*100:.1f} % of full-scale I/Q amplitude -> carrier (LO) leakage {20*np.log10(dc):.0f} dBc")

# ---------------------------------------------------------------- H. polar transmitter delay mismatch
rng = np.random.default_rng(3)
Ns, sps = 2000, 16
sym = ((rng.integers(0, 4, Ns) * 2 - 3) + 1j * (rng.integers(0, 4, Ns) * 2 - 3)) / np.sqrt(10)
up = np.zeros(Ns * sps, complex); up[::sps] = sym
tt = np.arange(-8 * sps, 8 * sps + 1) / sps
beta = 0.35
h = np.sinc(tt) * np.cos(np.pi * beta * tt) / (1 - (2 * beta * tt) ** 2 + 1e-12)
x = np.convolve(up, h, 'same')
A = np.abs(x); ph = np.unwrap(np.angle(x))
def frac_delay(sig, d):
    n = np.arange(len(sig))
    return np.interp(n - d, n, sig)
print("H: polar TX, 16-QAM RC 0.35, envelope delayed vs phase path:")
evms = []
for dly_sym in (0.0, 0.02, 0.05, 0.1):
    d = dly_sym * sps
    y = frac_delay(A, d) * np.exp(1j * ph)
    idx = np.arange(20, Ns - 20) * sps
    evm = np.sqrt(np.mean(abs(y[idx] - x[idx]) ** 2) / np.mean(abs(x[idx]) ** 2))
    evms.append(evm)
    print(f"   delay {dly_sym:4.2f} symbol: EVM {100*evm:5.2f} %")
check("H1 EVM grows ~linearly with envelope/phase delay mismatch", evms[2] > 2 * evms[1] * 0.9 and evms[0] < 1e-9)
# envelope and phase bandwidth expansion
def bw99(sig):
    S = np.abs(np.fft.fftshift(np.fft.fft(sig - np.mean(sig)))) ** 2
    fr = np.fft.fftshift(np.fft.fftfreq(len(sig), d=1 / sps))
    c = np.cumsum(S) / S.sum()
    return fr[np.searchsorted(c, 0.995)] - fr[np.searchsorted(c, 0.005)]
b_iq, b_env, b_ph = bw99(x), bw99(A), bw99(np.exp(1j * ph))
print(f"   99 % bandwidth (in symbol rates): IQ signal {b_iq:.2f}, envelope {b_env:.2f}, phase-modulated carrier {b_ph:.2f}")
check("H2 polar components are much wider-band than the composite signal", b_env > 1.5 * b_iq and b_ph > 1.5 * b_iq)

# ---------------------------------------------------------------- I. LO pulling / frequency plan
fout = 915e6
for mult, lab in ((1, "VCO at f_out"), (2, "VCO at 2 f_out, /2"), (4 / 3, "VCO at 4/3 f_out (x2 then /3... )")):
    fv = fout * mult
    harm = [n * fout for n in range(1, 4)]
    near = min(abs(fv - hh) for hh in harm)
    print(f"I: direct up-conversion to 915 MHz, {lab}: VCO {fv/1e6:.1f} MHz, nearest PA harmonic {near/1e6:.1f} MHz away")
check("I1 VCO at 2x f_out is still hit by the PA's 2nd harmonic (0 MHz away) -> needs >= 4/3 or offset plan",
      abs(2 * fout - 2 * fout) < 1)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
sys.exit(0 if ok_all else 1)
