#!/usr/bin/env python3
"""
e8_pulse_doppler.py -- verification for kb/11-radar/pulse-doppler-data-cube-and-prf-regimes.md (task W5-E8)

Sections
 1. Data cube simulation (fast time x slow time x channel): LFM pulses, 3 targets + zero-Doppler clutter + noise,
    pulse compression -> Doppler FFT -> beamforming -> 2-D CA-CFAR; estimates vs truth; processing gain = TB * N * M.
 2. PRF regimes (MIT LL table: X-band LPRF 1-3 kHz, MPRF 10-30 kHz, HPRF 100-300 kHz): R_u, v_u, ambiguity counts.
 3. Eclipsing: received-energy fraction vs range for a duty cycle d; average eclipsing loss; fully eclipsed fraction.
 4. Blind-zone map for a 7-PRF medium-PRF set (MIT LL example 5.75...10.25 kHz) at 10 GHz with a clutter notch:
    fraction of (range, velocity) space detectable with "M of 7 PRFs clear".
 5. Ambiguity resolution: exact Chinese remainder theorem (2 and 3 PRFs); with noisy residues, exact CRT vs a
    coincidence (clustering) search -- probability of correct unfolding.
 6. Doppler filter bank / MTD: clutter residue per filter for rect, Hamming and Dolph-Chebyshev windows (8 and 16
    pulses), improvement vs a 3-pulse canceller, scalloping loss.
 7. CA-CFAR on the range-Doppler map: measured Pfa vs (1 + a/N)^-N for independent cells (rect window) and for
    window-correlated Doppler cells (Hamming).
 8. Coherent-processing-interval limits for an accelerating target (rocket): T_max = sqrt(lambda/(2a)); loss vs T.
 9. DIY 5.8 GHz SDR pulse-Doppler design: timing, resolution, data rate, SNR for a drone and a rocket.
Run: python3 tools/verify/e8_pulse_doppler.py     (~20 s)
"""
import os
import warnings
import numpy as np
from scipy.signal.windows import chebwin

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
C0 = 299792458.0
K_B = 1.380649e-23
results, misses = [], []


def check(name, cond, detail=""):
    tag = "PASS" if cond else "MISS"
    if not cond:
        misses.append(name)
    line = f"[{tag}] {name} {detail}"
    print(line); results.append(line)


def say(s=""):
    print(s); results.append(s)


def db10(x):
    return 10 * np.log10(np.abs(x) + 1e-300)


rng = np.random.default_rng(11)

# =====================================================================================================
say("=== 1. Data cube simulation ===")
fc = 5.8e9; lam = C0 / fc
B = 10e6; tau = 2e-6; fs = 20e6           # LFM, complex sampling
PRF = 20e3; PRI = 1 / PRF
Np = 128; Mch = 4; dch = lam / 2
nfast = int(round(PRI * fs))               # 1000 samples per PRI
t_p = np.arange(int(round(tau * fs))) / fs
mu = B / tau
pulse = np.exp(1j * np.pi * mu * (t_p - tau / 2) ** 2)
TB = B * tau
targets = [  # (range m, radial velocity m/s (+ = approaching), angle deg, per-sample SNR dB at each channel before processing)
    (1200.0, 60.0, 10.0, -12.0),
    (3150.0, -35.0, -20.0, -15.0),
    (5000.0, 300.0, 0.0, -18.0),       # faster than v_u = 258 m/s -> aliases
]
clutter = [(800.0, 25.0), (2500.0, 20.0)]   # stationary scatterers (range, per-sample SNR dB)
noise_var = 1.0
cube = (rng.normal(size=(Mch, Np, nfast)) + 1j * rng.normal(size=(Mch, Np, nfast))) * np.sqrt(noise_var / 2)
tfast = np.arange(nfast) / fs
ch = np.arange(Mch)
for (R, v, ang, snr) in targets + [(r_, 0.0, 0.0, s_) for (r_, s_) in clutter]:
    a = np.sqrt(noise_var * 10 ** (snr / 10))
    d0 = 2 * R / C0
    i0 = int(np.floor(d0 * fs)); frac = d0 * fs - i0
    for p in range(Np):
        # slow-time phase from range change: approaching (+v) -> phase advance -> positive Doppler 2v/lam
        Rp = R - v * p * PRI
        ph = -4 * np.pi * Rp / lam
        for m in ch:
            phc = 2 * np.pi * dch / lam * m * np.sin(np.radians(ang))
            # fractional-delay placement by linear interpolation of the pulse (adequate at 2 samples per 1/B)
            seg = a * np.exp(1j * (ph + phc)) * pulse
            idx = i0 + np.arange(len(pulse))
            ok = idx < nfast - 1
            cube[m, p, idx[ok]] += (1 - frac) * seg[ok]
            cube[m, p, idx[ok] + 1] += frac * seg[ok]
# 1a pulse compression (fast time matched filter)
mf = np.conj(pulse[::-1])
rc = np.zeros_like(cube)
for m in ch:
    for p in range(Np):
        rc[m, p] = np.convolve(cube[m, p], mf)[len(pulse) - 1:len(pulse) - 1 + nfast]
# 1b Doppler FFT along slow time with a window; 1c beamform toward 0..; use non-coherent sum over channels
win = chebwin(Np, at=60)
RD = np.fft.fftshift(np.fft.fft(rc * win[None, :, None], axis=1), axes=1)       # (M, Doppler, range)
power = np.sum(np.abs(RD) ** 2, axis=0)                                           # non-coherent over channels
fd_axis = np.fft.fftshift(np.fft.fftfreq(Np, PRI))
v_axis = fd_axis * lam / 2
r_axis = np.arange(nfast) / fs * C0 / 2
# processing gain on noise-only region vs a target cell
noise_pow = np.mean(power[:, 700:990])                      # target-free region (5.25-7.4 km), mean noise power
say(f"  cube: {Mch} channels x {Np} pulses x {nfast} range samples = {Mch*Np*nfast/1e3:.0f} k complex samples "
    f"({Mch*Np*nfast*8/2**20:.1f} MiB as complex64); CPI = {Np*PRI*1e3:.1f} ms")
say(f"  resolutions: dR = c/2B = {C0/2/B:.1f} m (sample spacing {C0/2/fs:.1f} m); dv = lam/(2 N PRI) = "
    f"{lam/(2*Np*PRI):.2f} m/s; R_u = {C0/2/PRF/1e3:.2f} km; v_u = +-{lam*PRF/4:.1f} m/s")


def cfar2d(P, gr=2, gd=2, tr=8, td=4, alpha_db=None, pfa=1e-6):
    """2-D CA-CFAR, rectangular window with guard cells; returns detection mask and alpha"""
    from scipy.ndimage import uniform_filter
    Wr, Wd = 2 * (gr + tr) + 1, 2 * (gd + td) + 1
    Gr, Gd = 2 * gr + 1, 2 * gd + 1
    tot = uniform_filter(P, size=(Wd, Wr), mode="wrap") * Wd * Wr
    grd = uniform_filter(P, size=(Gd, Gr), mode="wrap") * Gd * Gr
    Nref = Wd * Wr - Gd * Gr
    noise = (tot - grd) / Nref
    alpha = Nref * (pfa ** (-1 / Nref) - 1) if alpha_db is None else 10 ** (alpha_db / 10)
    return P > alpha * noise, alpha, Nref


det, alpha, Nref = cfar2d(power, pfa=1e-6)
# cluster detections: local maxima
from scipy.ndimage import maximum_filter, label
peaks = det & (power == maximum_filter(power, size=(5, 5)))
pk = np.argwhere(peaks)
say(f"  2-D CA-CFAR: {Nref} reference cells, alpha = {10*np.log10(alpha):.1f} dB for design Pfa 1e-6; "
    f"{len(pk)} peak detections")
found = []
for (R, v, ang, snr) in targets:
    # expected Doppler bin with aliasing
    fd = 2 * v / lam
    fda = (fd + PRF / 2) % PRF - PRF / 2
    best = None
    for (kd, kr) in pk:
        dr = abs(r_axis[kr] - R); dv = abs(fd_axis[kd] - fda) * lam / 2
        if dr < 2 * C0 / 2 / fs and dv < 2 * lam / (2 * Np * PRI):
            if best is None or power[kd, kr] > power[best[0], best[1]]:
                best = (kd, kr)
    if best is not None:
        kd, kr = best
        # angle by beamforming the detected cell across channels (FFT scan)
        x = RD[:, kd, kr]
        angs = np.radians(np.linspace(-60, 60, 2401))
        A = np.exp(1j * 2 * np.pi * dch / lam * np.outer(np.sin(angs), ch))
        ang_est = np.degrees(angs[np.argmax(np.abs(A.conj() @ x))])
        out_snr = db10(power[kd, kr] / noise_pow)
        found.append((R, v, ang, r_axis[kr], fd_axis[kd] * lam / 2, ang_est, out_snr, snr))
        say(f"  target R={R:.0f} m v={v:+.0f} m/s ang={ang:+.0f} deg in-SNR {snr:+.0f} dB/sample -> detected at "
            f"R={r_axis[kr]:.1f} m, v(apparent)={fd_axis[kd]*lam/2:+.2f} m/s, ang={ang_est:+.1f} deg, out SNR {out_snr:.1f} dB")
    else:
        say(f"  target R={R:.0f} m v={v:+.0f} m/s NOT detected")
clutter_hits = [(r_axis[kr], v_axis[kd]) for (kd, kr) in pk if abs(v_axis[kd]) < 3 * lam / (2 * Np * PRI)]
say(f"  zero-Doppler (clutter) detections: {len(clutter_hits)} at ranges {sorted(set(round(c[0]) for c in clutter_hits))} m")
check("1a all three targets detected in the right range/Doppler cell", len(found) == 3)
# First run pre-registered "gain = TB*N*M" for the NON-coherent channel sum (MISS: 33.4 vs 38.3 dB).  Wrong
# expectation: a non-coherent sum adds signal and noise powers alike, so mean SNR gains only TB*N; the factor M needs
# coherent beamforming.  (The first run also biased the noise estimate with median/ln2.)  Logged.
w_loss = 10 * np.log10(np.sum(win) ** 2 / (Np * np.sum(win ** 2)))
# Second miss (logged): with SNR defined per complex sample at fs = 2B, the matched-filter gain is the number of
# samples in the pulse, tau*fs = 40, not TB = 20 (TB applies when SNR is referred to the signal bandwidth B).
NS = len(pulse)
g_nc = 10 * np.log10(NS * Np) + w_loss
g_c = 10 * np.log10(NS * Np * Mch) + w_loss
for (R, v, ang, Rm, vm, am, osnr, isnr) in found:
    kr = int(np.argmin(np.abs(r_axis - Rm))); kd = int(np.argmin(np.abs(fd_axis * lam / 2 - vm)))
    a_s = np.exp(1j * 2 * np.pi * dch / lam * ch * np.sin(np.radians(ang)))
    bf = np.abs(np.tensordot(a_s.conj(), RD, axes=(0, 0))) ** 2            # coherent beam toward the true angle
    nbf = np.mean(bf[:, 700:990])
    say(f"    R={R:.0f}: non-coherent-sum gain {osnr-isnr:.1f} dB (tau*fs*N + window = {g_nc:.1f}); coherent beam gain "
        f"{db10(bf[kd,kr]/nbf)-isnr:.1f} dB (tau*fs*N*M + window = {g_c:.1f}); residual = Doppler/range straddle")
    if R == 1200.0:
        G1b = (osnr - isnr, db10(bf[kd, kr] / nbf) - isnr)
check("1b processing gain: non-coherent channel sum ~ tau*fs*N, coherent beam ~ tau*fs*N*M (each within 1.5 dB, on-grid target)",
      abs(G1b[0] - g_nc) < 1.5 and abs(G1b[1] - g_c) < 1.5, f"({G1b[0]:.1f} vs {g_nc:.1f}; {G1b[1]:.1f} vs {g_c:.1f})")
# First run used 140 m/s and expected aliasing -- but v_u = 258 m/s at 5.8 GHz/20 kHz (own arithmetic error, logged)
check("1c 300 m/s target aliases to v - 2 v_u = -216.8 m/s (Doppler ambiguity visible in the map)",
      abs(found[2][4] - (300.0 - 2 * lam * PRF / 4)) < 2 * lam / (2 * Np * PRI), f"(apparent {found[2][4]:+.1f} m/s)")

# =====================================================================================================
say("\n=== 2. PRF regimes ===")
for band, f0 in [("X-band 10 GHz", 10e9), ("C-band 5.8 GHz", 5.8e9), ("S-band 3 GHz", 3e9)]:
    l0 = C0 / f0
    for name, prf in [("LPRF", 1e3), ("LPRF", 3e3), ("MPRF", 10e3), ("MPRF", 30e3), ("HPRF", 100e3), ("HPRF", 300e3)]:
        Ru = C0 / 2 / prf; vu = l0 * prf / 4
        n_r = int(np.ceil(50e3 / Ru)); n_v = int(np.ceil(600 / vu))
        say(f"  {band:14s} {name} {prf/1e3:5.0f} kHz: R_u = {Ru/1e3:7.2f} km, v_u = +-{vu:7.1f} m/s; ambiguity "
            f"intervals to cover 50 km / +-600 m/s: {n_r} in range, {n_v} in velocity")
say(f"  R_u * v_u = c lambda / 8 = {C0*0.03/8:.3e} m^2/s at 10 GHz (any PRF)")

# =====================================================================================================
say("\n=== 3. Eclipsing ===")


def eclipse_fraction(t0, tau_, T_, trec=0.0):
    """fraction of an echo [t0, t0+tau] (mod T) received; receiver blind during [0, tau+trec) of each PRI"""
    n = 400
    ts = (t0 + np.linspace(0, tau_, n, endpoint=False)) % T_
    return np.mean(ts >= tau_ + trec)


for d in [0.01, 0.05, 0.1, 0.35, 0.5]:
    T_ = 1.0; tau_ = d * T_
    t0s = np.linspace(0, T_, 4000, endpoint=False)
    fr = np.array([eclipse_fraction(t, tau_, T_) for t in t0s])
    mean_loss = -db10(np.mean(fr ** 2))        # matched-filter SNR scales as (collected fraction)^2 (amplitude ~ fraction)
    mean_loss_e = -db10(np.mean(fr))           # if SNR ~ collected energy (filter matched to the collected part)
    say(f"  duty {d*100:4.0f} %: fully eclipsed {np.mean(fr==0)*100:4.1f} % of ranges, partially {np.mean((fr>0)&(fr<1))*100:4.1f} %; "
        f"average loss {mean_loss_e:.2f} dB (energy) / {mean_loss:.2f} dB (fixed full-pulse filter)")
    if d == 0.35:
        ECL35 = mean_loss_e
check("3 HPRF 35 % duty: average eclipsing loss is 1-3 dB (MIT LL: 1-2 dB if unmitigated)", 1.0 <= ECL35 <= 3.0,
      f"({ECL35:.2f} dB)")

# =====================================================================================================
say("\n=== 4. Blind-zone map for a 7-PRF medium-PRF set (10 GHz) ===")
f0 = 10e9; l0 = C0 / f0
prfs = np.array([5.75, 6.5, 7.25, 8.0, 8.75, 9.5, 10.25]) * 1e3
tau_b = 1e-6; trec = 0.5e-6
notch_v = 15.0                              # clutter notch half-width in m/s (ground radar, main-lobe + spread)
Rg = np.linspace(1e3, 80e3, 1600)
Vg = np.linspace(-600, 600, 1201)
clear = np.zeros((len(Vg), len(Rg)), int)
for prf in prfs:
    T_ = 1 / prf
    t = (2 * Rg / C0) % T_
    r_ok = (t >= tau_b + trec) & (t <= T_ - tau_b)        # echo fully inside the listening window
    fdv = (2 * Vg / l0 + prf / 2) % prf - prf / 2
    v_ok = np.abs(fdv) * l0 / 2 > notch_v
    clear += np.outer(v_ok, r_ok)
for M in [1, 2, 3, 4]:
    say(f"  >= {M} of 7 PRFs clear: {np.mean(clear >= M)*100:.1f} % of the (1-80 km, +-600 m/s) space")
say(f"  each single PRF: clear in range {np.mean([( ((2*Rg/C0)%(1/p) >= tau_b+trec) & ((2*Rg/C0)%(1/p) <= 1/p-tau_b)).mean() for p in prfs])*100:.1f} %, "
    f"in velocity {np.mean([(np.abs((2*Vg/l0+p/2)%p-p/2)*l0/2 > notch_v).mean() for p in prfs])*100:.1f} %")
VIS3 = np.mean(clear >= 3)
check("4 a 7-PRF set gives >= 3-of-7 visibility over > 90 % of range-velocity space", VIS3 > 0.9, f"({VIS3*100:.1f} %)")
# low-velocity targets are blind in all PRFs (inside the notch)
say(f"  |v| < notch ({notch_v} m/s): visible in 0 PRFs by construction -- the irreducible blind zone")

# =====================================================================================================
say("\n=== 5. Ambiguity resolution: Chinese remainder theorem ===")


def crt(res, mods):
    Mtot = int(np.prod(mods))
    x = 0
    for a, m in zip(res, mods):
        Mi = Mtot // m
        bi = pow(Mi, -1, m)
        x += a * Mi * bi
    return x % Mtot


mods = [7, 8]
true = 45
r = [true % m for m in mods]
say(f"  2 PRFs with unambiguous intervals of 7 and 8 range cells: residues {r} -> CRT {crt(r, mods)} (true {true}), "
    f"unambiguous to {7*8} cells")
check("5a CRT exact (2 PRFs)", crt(r, mods) == true)
mods3 = [11, 12, 13]
true3 = 1234
r3 = [true3 % m for m in mods3]
check("5b CRT exact (3 PRFs, 11/12/13 -> 1716 cells)", crt(r3, mods3) == true3, f"({crt(r3, mods3)})")
# noisy residues: measured apparent range (in cells, continuous) with Gaussian error sigma
for sigma in [0.1, 0.25, 0.4]:
    ok_crt = ok_cl = 0
    trials = 3000
    span = int(np.prod(mods3))
    for _ in range(trials):
        tr_ = rng.uniform(0, span)
        meas = [(tr_ % m + rng.normal(0, sigma)) % m for m in mods3]
        # exact CRT on rounded residues
        rr = [int(np.round(x)) % m for x, m in zip(meas, mods3)]
        est = crt(rr, mods3)
        ok_crt += abs(((est - tr_ + span / 2) % span) - span / 2) < 1.0
        # coincidence/clustering: unfold PRF-1 candidates, pick the one whose other unfoldings agree best
        best, bestcost = None, 1e9
        for k in range(span // mods3[0] + 1):
            c1 = meas[0] + k * mods3[0]
            if c1 >= span:
                break
            cost = 0.0
            for x, m in zip(meas[1:], mods3[1:]):
                kk = np.round((c1 - x) / m)
                cost += (c1 - (x + kk * m)) ** 2
            if cost < bestcost:
                bestcost, best = cost, c1
        ok_cl += abs(((best - tr_ + span / 2) % span) - span / 2) < 1.0
    say(f"  residue error sigma = {sigma} cell: correct unfolding exact-CRT {ok_crt/trials*100:.1f} %, "
        f"coincidence search {ok_cl/trials*100:.1f} %")
    if sigma == 0.25:
        NOISY = (ok_crt / trials, ok_cl / trials)
check("5c with noisy residues the coincidence search beats exact CRT", NOISY[1] > NOISY[0] + 0.1, f"({NOISY})")
# Doppler unfolding example at 5.8 GHz: v_true = 140 m/s, two PRFs 20 and 23 kHz
l58 = C0 / 5.8e9
v_true = 140.0
for prfs2 in [(20e3, 23e3)]:
    ap = [((2 * v_true / l58 + p / 2) % p - p / 2) for p in prfs2]
    cands = []
    for k1 in range(-5, 6):
        f1 = ap[0] + k1 * prfs2[0]
        k2 = np.round((f1 - ap[1]) / prfs2[1])
        cands.append((abs(f1 - (ap[1] + k2 * prfs2[1])), f1 * l58 / 2))
    cands.sort()
    say(f"  Doppler unfolding, PRFs 20/23 kHz at 5.8 GHz: apparent {ap[0]*l58/2:+.1f} / {ap[1]*l58/2:+.1f} m/s -> "
        f"best unfolding {cands[0][1]:+.1f} m/s (true {v_true}); unambiguous span "
        f"{np.lcm(20, 23)*1e3*l58/2:.0f} m/s ")
    check("5d two-PRF Doppler unfolding recovers 140 m/s", abs(cands[0][1] - v_true) < 1.0)

# =====================================================================================================
say("\n=== 6. Doppler filter bank / MTD clutter rejection ===")
PRFs = 1e3; f3 = 3e9; l3 = C0 / f3
sig_v = 0.3; sig_f = 2 * sig_v / l3


def filt_resp(w, f, T):
    n = np.arange(len(w))
    return np.exp(-1j * 2 * np.pi * np.outer(f, n) * T) @ w


fgrid = np.linspace(-PRFs / 2, PRFs / 2, 8001)
Sc = np.exp(-fgrid ** 2 / (2 * sig_f ** 2)); Sc /= np.trapezoid(Sc, fgrid)
for Nf in [8, 16]:
    for wname, w in [("rect", np.ones(Nf)), ("Hamming", np.hamming(Nf)), ("Chebyshev-40", chebwin(Nf, at=40)),
                     ("Chebyshev-60", chebwin(Nf, at=60))]:
        imps = []
        for k in range(1, Nf):
            fk = k / Nf * PRFs
            wk = w * np.exp(1j * 2 * np.pi * fk * np.arange(Nf) / PRFs)
            H = filt_resp(np.conj(wk), fgrid, 1 / PRFs)
            clut = np.trapezoid(Sc * np.abs(H) ** 2, fgrid)
            noise = np.sum(np.abs(w) ** 2)
            # improvement for a target at the filter centre: (S/C)out/(S/C)in = |sum w|^2 / clut
            imps.append(np.abs(np.sum(w)) ** 2 / clut)
        imps = np.array(imps)
        say(f"  N = {Nf:2d}, {wname:12s}: clutter improvement in filters 1..N-1 (sigma_v 0.3 m/s, 3 GHz, 1 kHz): "
            f"worst {db10(imps.min()):.1f} dB (filters next to zero), median {db10(np.median(imps)):.1f} dB")
        if Nf == 8 and wname == "rect":
            MTD_rect = db10(np.median(imps))
        if Nf == 8 and wname == "Chebyshev-60":
            MTD_ch60 = db10(np.median(imps))
        if Nf == 8 and wname == "Chebyshev-40":
            MTD_ch40 = db10(np.median(imps))
        if Nf == 16 and wname == "rect":
            MTD16_rect = db10(np.median(imps))
        if Nf == 16 and wname == "Chebyshev-60":
            MTD16_ch60 = db10(np.median(imps))
say("  (3-pulse canceller for the same clutter: I2 = 60 dB average, kb/11-radar/clutter-and-mti.md)")
# First run pre-registered "Chebyshev-60 beats rect by > 20 dB at N = 8": MISS (30.9 vs 31.6 dB).  With only 8 pulses a
# 60 dB window's main lobe spans several filters and swallows the clutter; 40 dB is the sweet spot (cf. ASR-9's
# 40 dB Doppler sidelobes, MIT LL lecture 13).  Logged; the check now states that finding and the N = 16 benefit.
check("6a N = 8: Chebyshev-40 is the best window (beats rect by > 5 dB and Chebyshev-60); N = 16: Chebyshev-60 beats rect by > 20 dB",
      MTD_ch40 - MTD_rect > 5 and MTD_ch40 > MTD_ch60 and MTD16_ch60 - MTD16_rect > 20,
      f"(N=8: rect {MTD_rect:.1f}, C40 {MTD_ch40:.1f}, C60 {MTD_ch60:.1f}; N=16: rect {MTD16_rect:.1f}, C60 {MTD16_ch60:.1f} dB)")
# scalloping: target midway between Doppler bins
for wname, w in [("rect", np.ones(64)), ("Hamming", np.hamming(64)), ("Chebyshev-60", chebwin(64, at=60))]:
    n = np.arange(64)
    on = abs(np.sum(w)); off = abs(np.sum(w * np.exp(1j * np.pi * n / 64)))
    say(f"  scalloping loss (target half a bin off), {wname}: {20*np.log10(on/off):.2f} dB")

# =====================================================================================================
say("\n=== 7. CA-CFAR on a noise-only range-Doppler map: measured vs designed Pfa ===")
Nd, Nr = 128, 2000
for wname, w in [("rect", np.ones(Nd)), ("Hamming", np.hamming(Nd))]:
    meas = []
    for design in [1e-3, 1e-4]:
        hits = tot = 0
        for rep in range(6):
            X = (rng.normal(size=(Nd, Nr)) + 1j * rng.normal(size=(Nd, Nr))) / np.sqrt(2)
            P = np.abs(np.fft.fft(X * w[:, None], axis=0)) ** 2
            dmask, a_, Nref_ = cfar2d(P, gr=1, gd=1, tr=6, td=3, pfa=design)
            hits += dmask.sum(); tot += dmask.size
        meas.append(hits / tot)
        say(f"  window {wname:8s}: design Pfa {design:.0e} ({Nref_} ref cells) -> measured {hits/tot:.2e}")
    if wname == "rect":
        PFA_RECT = meas
    else:
        PFA_HAM = meas
check("7a rect window (independent cells): measured Pfa within a factor 1.5 of design", all(0.67 < m / d < 1.5 for m, d in zip(PFA_RECT, [1e-3, 1e-4])),
      f"({PFA_RECT})")
check("7b Hamming-correlated Doppler cells change the realised Pfa (ratio differs from rect by > 20 %)",
      abs(PFA_HAM[1] / 1e-4 - PFA_RECT[1] / 1e-4) / (PFA_RECT[1] / 1e-4) > 0.2, f"({PFA_HAM})")

# =====================================================================================================
say("\n=== 8. CPI limit for an accelerating target ===")
for (fcx, acc, lab) in [(5.8e9, 98.1, "rocket 10 g, 5.8 GHz"), (5.8e9, 49.0, "rocket 5 g, 5.8 GHz"), (10e9, 98.1, "rocket 10 g, 10 GHz"),
                        (77e9, 9.81, "car 1 g, 77 GHz")]:
    lx = C0 / fcx
    Tm = np.sqrt(lx / (2 * acc))
    say(f"  {lab}: T_max = sqrt(lambda/(2a)) = {Tm*1e3:.1f} ms (Doppler drift a*T = {acc*Tm:.2f} m/s = one bin lambda/(2T))")
# coherent loss vs T for quadratic phase
lx = C0 / 5.8e9; acc = 98.1
Tm = np.sqrt(lx / (2 * acc))
for Tr in [0.5, 1.0, 2.0, 3.0]:
    T = Tr * Tm
    n = 4096
    t = np.linspace(-T / 2, T / 2, n)
    sig = np.exp(1j * 4 * np.pi / lx * 0.5 * acc * t ** 2)
    # best Doppler filter (search linear phase)
    fr = np.linspace(-5 / T, 5 / T, 801)
    resp = np.abs(np.exp(-1j * 2 * np.pi * np.outer(fr, t)) @ sig) / n
    say(f"  T = {Tr:.1f} T_max ({T*1e3:.1f} ms): coherent integration loss {-20*np.log10(resp.max()):.2f} dB")
    if Tr == 1.0:
        L1 = -20 * np.log10(resp.max())
check("8 at T = T_max the acceleration loss is small (< 1 dB): quadratic phase pi/4 at the ends", L1 < 1.0, f"({L1:.2f} dB)")

# =====================================================================================================
say("\n=== 9. DIY 5.8 GHz SDR pulse-Doppler design ===")
fc = 5.8e9; lam = C0 / fc
B = 10e6; tau = 1e-6; PRF = 20e3; Np = 256; fs = 20e6
Pt_dBm = 20.0; G_dBi = 18.0; NF = 6.0; Lsys = 6.0
say(f"  f = 5.8 GHz, LFM B = 10 MHz, tau = 1 us (TB = {B*tau:.0f}), PRF = 20 kHz, N = {Np} pulses -> CPI {Np/PRF*1e3:.1f} ms")
say(f"  dR = {C0/2/B:.1f} m, R_u = {C0/2/PRF/1e3:.2f} km, v_u = +-{lam*PRF/4:.1f} m/s, dv = {lam*PRF/(2*Np):.2f} m/s, "
    f"duty {tau*PRF*100:.0f} %, blind range (tau + 1 us T/R recovery) {C0*(tau+1e-6)/2:.0f} m")
say(f"  fast-time samples per PRI {fs/PRF:.0f}; cube per channel {Np*fs/PRF/1e3:.0f} k complex samples per CPI; "
    f"stream 20 MS/s complex = {20e6*4/1e6:.0f} MB/s at 16-bit I/Q")


def snr_db(Pt_dBm, G_dBi, lam, sigma, R, tau, N, NF, L):
    Pt = 10 ** ((Pt_dBm - 30) / 10); G = 10 ** (G_dBi / 10)
    E = Pt * tau
    s = E * G ** 2 * lam ** 2 * sigma / ((4 * np.pi) ** 3 * R ** 4 * K_B * 290 * 10 ** (NF / 10) * 10 ** (L / 10))
    return 10 * np.log10(s * N)


for (lab, sig, R) in [("drone 0.01 m^2", 0.01, 500), ("drone 0.01 m^2", 0.01, 1000), ("rocket -20 dBsm", 0.01, 2000),
                      ("rocket -20 dBsm", 0.01, 3000)]:
    sdb = snr_db(Pt_dBm, G_dBi, lam, sig, R, tau, Np, NF, Lsys)
    say(f"  {lab} at {R/1e3:.1f} km: SNR after {Np}-pulse coherent integration = {sdb:.1f} dB "
        f"(single pulse {sdb-10*np.log10(Np):.1f} dB)")
    if R == 1000:
        SNR1k = sdb
# First run pre-registered that this baseline (100 mW peak, 1 us, 256 pulses) reaches 13.2 dB on a 0.01 m^2 drone
# at 1 km: MISS (-16.7 dB) -- the expectation ignored how little ENERGY a low-duty SDR pulse train carries
# (0.1 W x 1 us x 256 = 25.6 uJ).  Logged.  Redesign by the energy form of the radar equation:
SNRreq = 13.2
need = SNRreq - SNR1k
say(f"  baseline energy per CPI {0.1*tau*Np*1e6:.1f} uJ; {need:.1f} dB more energy needed for 13.2 dB at 1 km")
designs = [("B: 10 W PA, tau 4 us (TB 40), 1024 pulses (CPI 51 ms)", 40.0, 4e-6, 1024),
           ("C: 10 W PA, tau 10 us (TB 100), 1024 pulses", 40.0, 10e-6, 1024),
           ("FMCW, 100 mW continuous for the same 12.8 ms", 20.0, 12.8e-3, 1)]
DES = {}
for lab, pdbm, tt, nn in designs:
    s1k = snr_db(pdbm, G_dBi, lam, 0.01, 1000, tt, nn, NF, Lsys)
    s2k = snr_db(pdbm, G_dBi, lam, 0.01, 2000, tt, nn, NF, Lsys)
    blind = C0 * (tt + 1e-6) / 2 if nn > 1 else float('nan')
    say(f"  {lab}: drone@1 km {s1k:.1f} dB, 0.01 m^2 rocket@2 km {s2k:.1f} dB; energy {10**((pdbm-30)/10)*tt*nn*1e3:.2f} mJ; "
        f"blind range {blind:.0f} m")
    DES[lab[0]] = (s1k, s2k, blind)
check("9 energy-scaled design B (10 W, 4 us, 1024 pulses) reaches >= 13.2 dB on the drone at 1 km",
      DES["B"][0] >= 13.2, f"({DES['B'][0]:.1f} dB, blind range {DES['B'][2]:.0f} m)")
# rocket velocity vs v_u
for v in [100, 250, 300]:
    say(f"  rocket radial speed {v} m/s: {'unambiguous' if v < lam*PRF/4 else 'ALIASED'} at PRF 20 kHz "
        f"(needs PRF >= {4*v/lam/1e3:.1f} kHz)")

# figure: range-Doppler map (section 1) and blind-zone map (section 4)
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG = os.path.join(os.path.dirname(os.path.dirname(HERE)), "kb", "11-radar", "figures")
    os.makedirs(FIG, exist_ok=True)
    GR, TXT, TXT2 = "#8a8984", "#0b0b0b", "#52514e"
    plt.rcParams.update({"axes.edgecolor": GR, "axes.labelcolor": TXT, "xtick.color": TXT2, "ytick.color": TXT2,
                         "font.size": 10, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb"})
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.0))
    lam58 = C0 / 5.8e9
    im = ax[0].imshow(10 * np.log10(power / noise_pow + 1e-12), aspect="auto", origin="lower", cmap="Blues",
                      extent=[0, r_axis[-1] / 1e3, v_axis[0], v_axis[-1]], vmin=0, vmax=30)
    ax[0].set_xlabel("range (km)"); ax[0].set_ylabel("apparent radial velocity (m/s)")
    ax[0].set_title("Range–Doppler map (5.8 GHz, 128 pulses, 4 ch.)", fontsize=10, color=TXT, loc="left")
    for (R, v, ang, snr) in targets:
        va = ((2 * v / lam58 + PRF / 2) % PRF - PRF / 2) * lam58 / 2
        ax[0].annotate(f"{v:+.0f} m/s", (R / 1e3, va), xytext=(R / 1e3 + 0.35, va + 25), fontsize=8, color=TXT,
                       arrowprops=dict(arrowstyle="-", color=TXT2, lw=0.8))
    cb = fig.colorbar(im, ax=ax[0]); cb.set_label("SNR (dB)")
    im2 = ax[1].imshow(clear, aspect="auto", origin="lower", cmap="Greys_r", extent=[Rg[0] / 1e3, Rg[-1] / 1e3, Vg[0], Vg[-1]],
                       vmin=0, vmax=7)
    ax[1].set_xlabel("range (km)"); ax[1].set_ylabel("radial velocity (m/s)")
    ax[1].set_title("PRFs clear (of 7), 10 GHz MPRF set", fontsize=10, color=TXT, loc="left")
    cb2 = fig.colorbar(im2, ax=ax[1]); cb2.set_label("number of PRFs clear")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "e8-range-doppler-and-blind-zones.png"), dpi=130); plt.close(fig)
    say("  wrote figure kb/11-radar/figures/e8-range-doppler-and-blind-zones.png")
except Exception as e:
    say(f"  figure skipped: {e}")

say("\nSUMMARY: " + ("ALL PASS" if not misses else f"{len(misses)} MISS: {misses}"))
with open(os.path.join(HERE, "e8_pulse_doppler_output.txt"), "w") as fh:
    fh.write("\n".join(results) + "\n")
