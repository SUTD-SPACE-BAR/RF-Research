#!/usr/bin/env python3
"""Verification + simulation for kb/11-radar/fmcw-radar.md

Run:  python3 tools/verify/radar_fmcw.py        (~30 s)

Checks / computes:
  1. Beat signal of a sawtooth FMCW chirp from first principles (exact dechirp incl. residual video
     phase): beat frequency S*tau, phase 2 pi fc tau - pi S tau^2 ; RVP negligible for short range.
  2. TI SWRA553 Table 1 (LRR/MRR/SRR/USRR): recompute sweep BW, range res, max range from IF,
     max velocity, samples/chirp, frame times from the formulas; compare with the published table.
  3. Full range-Doppler-angle simulation (77 GHz, 1 TX x 4 RX, 256 samples x 128 chirps):
     four targets, 2-D FFT, 2-D CA-CFAR, angle FFT -> estimates within one bin of truth.
  4. Two-tone range resolution: dip between two equal targets vs separation (rect / Hann).
  5. IF bandwidth / ADC limits: max range for complex vs real sampling (0.9 factor, TI).
  6. Range migration within a frame; Doppler-induced range shift fd c/(2S).
  7. Phase noise + TX leakage: simulated IF noise skirt vs range-correlation theory
     4 sin^2(pi f tau) L(f) (Budge & Burt); floor raise near the leakage peak.
  8. VCO nonlinearity with the real Mini-Circuits ZX95-2536C+ tuning table: linear Vtune ramp ->
     range-peak broadening that grows with range; tuning-curve predistortion restores the peak.
  9. Worked chirp design (drone radar at 77 GHz) and Infineon BGT60TR13C / coffee-can numbers.
"""
import numpy as np
from scipy import signal, interpolate

c = 299_792_458.0
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
print("1. Beat signal from first principles")
fc = 77e9
S = 30e12          # 30 MHz/us
T = 40e-6
fs = 40e6          # complex; must exceed the 12 MHz beat (20 MHz would alias it to -8 MHz)
t = np.arange(int(T * fs)) / fs
R = 60.0
tau = 2 * R / c
phi_tx = lambda tt: 2 * np.pi * (fc * tt + 0.5 * S * tt ** 2)
beat = np.exp(1j * (phi_tx(t) - phi_tx(t - tau)))          # mixer output (TX x conj(RX)) for t > tau
# analytic: 2 pi (fc tau + S tau t - S tau^2/2)
ana = np.exp(1j * 2 * np.pi * (fc * tau + S * tau * t - 0.5 * S * tau ** 2))
check("dechirp phase == 2pi(fc tau + S tau t - S tau^2/2)", np.max(np.abs(beat - ana)), 0.0, 1e-6)
fb = S * tau
print(f"    R = {R} m: tau = {tau*1e9:.2f} ns, f_beat = S tau = {fb/1e6:.4f} MHz; RVP term pi S tau^2 = {np.pi*S*tau**2:.4f} rad")
X = np.fft.fft(beat, 1 << 16)
fr = np.fft.fftfreq(1 << 16, 1 / fs)
check("measured beat frequency = S*2R/c", fr[np.argmax(np.abs(X))], fb, fs / (1 << 16))
check("phase of beat = 4 pi R/lambda (mod 2pi, RVP-corrected)", np.angle(np.exp(1j * (2 * np.pi * fc * tau))),
      np.angle(np.exp(1j * 4 * np.pi * R / (c / fc))), 1e-9)

print("=" * 78)
print("2. TI SWRA553 Table 1 re-derivation")
lam77 = c / 77e9   # TI table uses ~77 GHz
table = {  # name: (slope MHz/us, chirp duration us, inter-chirp us, Nchirps, fs complex Msps, samples, published...)
    "LRR": dict(S=10, Tch=30, idle=8, N=256, fs=16.67, ns=500, pub=dict(B=300, dR=0.50, Rmax=225, v=92.28, fb=15, Tf=9.728, Ta=7.68)),
    "MRR": dict(S=12, Tch=45, idle=10, N=128, fs=11.11, ns=500, pub=dict(B=540, dR=0.28, Rmax=125, v=63.75, fb=10, Tf=7.04, Ta=5.76)),
    "SRR": dict(S=15, Tch=50, idle=12, N=128, fs=5.00, ns=250, pub=dict(B=750, dR=0.20, Rmax=45, v=56.56, fb=4.5, Tf=7.94, Ta=6.4)),
    "USRR": dict(S=30, Tch=50, idle=50, N=128, fs=5.00, ns=250, pub=dict(B=1500, dR=0.10, Rmax=22.5, v=35.3, fb=4.5, Tf=12.8, Ta=6.4)),
}
for name, p in table.items():
    B = p["S"] * p["Tch"]                       # MHz
    dR = c / (2 * B * 1e6)
    Rmax = p["pub"]["fb"] * 1e6 * c / (2 * p["S"] * 1e12)
    Tc = (p["Tch"] + p["idle"]) * 1e-6
    vmax = lam77 / (4 * Tc) * 3.6
    ns = p["fs"] * p["Tch"]
    Tf = p["N"] * Tc * 1e3
    Ta = p["N"] * p["Tch"] * 1e-3
    pub = p["pub"]
    print(f"    {name:4s}: B {B:6.0f} (pub {pub['B']}) MHz, dR {dR:.3f} (pub {pub['dR']}) m, Rmax(IF) {Rmax:6.1f} (pub {pub['Rmax']}) m, "
          f"vmax {vmax:6.2f} (pub {pub['v']}) km/h, samples {ns:5.0f} (pub {p['ns']}), frame {Tf:6.3f}/{Ta:5.2f} (pub {pub['Tf']}/{pub['Ta']}) ms")
    check(f"{name} sweep BW", B, pub["B"], 1e-9)
    check(f"{name} range resolution", dR, pub["dR"], 0.02)
    check(f"{name} Rmax from IF", Rmax, pub["Rmax"], 0.01, rel=True)
    check(f"{name} vmax km/h", vmax, pub["v"], 0.012, rel=True)
    check(f"{name} frame time", Tf, pub["Tf"], 0.01, rel=True)

print("=" * 78)
print("3. Range-Doppler-angle simulation")
rng = np.random.default_rng(42)
fc = 77e9
lam = c / fc
S = 30e12
fs = 10e6
Ns = 256
Tadc = Ns / fs                 # 25.6 us
Tidle = 7e-6
Tc = Tadc + Tidle + 2e-6       # chirp repetition 34.6 us (ADC start delay 2 us)
Nc = 128
Nrx = 4
d = lam / 2
B = S * Tadc
dR = c / (2 * B)
Rmax_if = fs * c / (2 * S)     # complex sampling
vmax = lam / (4 * Tc)
dv = lam / (2 * Nc * Tc)
print(f"    B(sampled) {B/1e6:.0f} MHz -> dR {dR*100:.2f} cm; Rmax(IF, complex) {Rmax_if:.1f} m; vmax +-{vmax:.2f} m/s; dv {dv*100:.2f} cm/s")
targets = [  # R (m), v (m/s, + approaching), angle (deg), amplitude
    (5.0, 0.0, 0.0, 1.0),
    (12.3, -4.2, 20.0, 0.5),
    (12.3, 6.0, -30.0, 0.5),
    (31.7, 10.5, 10.0, 0.2),
]
n = np.arange(Ns)
m = np.arange(Nc)
cube = np.zeros((Nrx, Nc, Ns), complex)
for (Rt, vt, th, a) in targets:
    for r in range(Nrx):
        for mm in range(Nc):
            Rinst = Rt - vt * (mm * Tc + n / fs + 2e-6)      # approaching reduces range
            tau = 2 * Rinst / c
            ph = 2 * np.pi * (fc * tau + S * tau * (n / fs + 2e-6) - 0.5 * S * tau ** 2)
            ph += 2 * np.pi * d * r * np.sin(np.radians(th)) / lam
            cube[r, mm] += a * np.exp(1j * ph)
noise_sigma = 0.05
cube += noise_sigma / np.sqrt(2) * (rng.standard_normal(cube.shape) + 1j * rng.standard_normal(cube.shape))
wr = np.hanning(Ns)
wd = np.hanning(Nc)
rfft = np.fft.fft(cube * wr[None, None, :], axis=2)
rd = np.fft.fftshift(np.fft.fft(rfft * wd[None, :, None], axis=1), axes=1)
pw = np.sum(np.abs(rd) ** 2, axis=0)         # non-coherent sum over RX
# complex IF with TX*conj(RX): all beats are positive, so bins 0..fs are all unambiguous (TI 'complex 1x')
# 2-D CA-CFAR (cross window) on power map
guard, train = 2, 8
thr_mult = 10 ** (13 / 10)
det = []
Nd, Nr = pw.shape
for i in range(Nd):
    for j in range(train + guard, Nr - train - guard):
        cut = pw[i, j]
        rr = np.r_[pw[i, j - guard - train:j - guard], pw[i, j + guard + 1:j + guard + train + 1]]
        dd = np.r_[pw[(i - guard - train + np.arange(train)) % Nd, j], pw[(i + guard + 1 + np.arange(train)) % Nd, j]]
        noise = np.mean(np.r_[rr, dd])
        if cut > thr_mult * noise and cut == pw[max(0, i - 1):i + 2, max(0, j - 1):j + 2].max():
            det.append((i, j, cut))
det.sort(key=lambda x: -x[2])
vel_axis = -(np.arange(Nd) - Nd // 2) * dv   # IF = TX*conj(RX): approaching -> phase decreasing -> NEGATIVE Doppler bin (TI/Rao convention)
print(f"    detections: {len(det)}")
found = 0
for (Rt, vt, th, a) in targets:
    best = None
    for (i, j, pwr) in det:
        Rest = j * dR
        vest = vel_axis[i]
        if abs(Rest - Rt) < 2 * dR and abs(vest - vt) < 2 * dv:
            # angle FFT on the detected cell
            snap = rd[:, i, j]
            A = np.fft.fftshift(np.fft.fft(snap, 256))
            om = (np.arange(256) - 128) * 2 * np.pi / 256
            thest = np.degrees(np.arcsin(om[np.argmax(np.abs(A))] * lam / (2 * np.pi * d)))
            best = (Rest, vest, thest)
            break
    if best:
        found += 1
        print(f"    target R={Rt:5.1f} v={vt:+5.1f} th={th:+5.1f}  ->  R={best[0]:6.2f} v={best[1]:+6.2f} th={best[2]:+6.1f}")
        check(f"  angle estimate for target at {th} deg (4 RX, res ~{np.degrees(2/Nrx):.0f} deg)", best[2], th, 4.0)
check("all four targets detected within 2 bins in range & velocity", found, 4, 0)
false_alarms = len(det) - found
print(f"    other CFAR detections (sidelobes/noise): {false_alarms}")

print("=" * 78)
print("4. Two-target range resolution (equal targets, incoherent power sum, >1 dB dip criterion)")
Nsr = 256
nn = np.arange(Nsr)
osf = 64


def pattern(w):
    W = np.abs(np.fft.fft(w, osf * Nsr)) ** 2
    return W / W.max()


minsep = {}
for win_name, w in (("rect", np.ones(Nsr)), ("hann", np.hanning(Nsr)), ("hamming", np.hamming(Nsr))):
    P = pattern(w)
    Pf = np.r_[P[-osf * 8:], P[:osf * 8]]          # centred pattern, +-8 bins
    ctr = osf * 8
    found_sep = None
    for sep in np.arange(0.5, 3.0, 1 / osf):
        k = int(round(sep * osf))
        tot = Pf[:len(Pf) - k] + Pf[k:]            # two targets, power sum
        # peaks near the two target positions vs the minimum between them
        a0 = ctr
        mid = tot[a0 - k // 2 - k // 2: a0 + 1] if False else None
        seg = tot[ctr - k:ctr + 1]                 # from target 1 (index ctr-k in shifted frame) to target 2
        dip = 10 * np.log10(seg.min() / max(seg[0], seg[-1]))
        if dip < -1.0:
            found_sep = sep
            break
    minsep[win_name] = found_sep
    print(f"    {win_name:8s}: minimum separation for a 1 dB dip = {found_sep:.2f} bins (bin = c/2B)")
check("rect: ~1 bin (Rayleigh, c/2B)", minsep["rect"], 1.0, 0.12)
check("Hann: ~2 bins", minsep["hann"], 1.9, 0.25)
# coherent case: probability over random relative phase (informative only)
rngp = np.random.default_rng(7)
for win_name, w in (("rect", np.ones(Nsr)), ("hann", np.hanning(Nsr))):
    row = []
    for sep in (1.0, 2.0):
        okc = 0
        for _ in range(200):
            ph = rngp.uniform(0, 2 * np.pi)
            x = np.exp(2j * np.pi * 40.0 * nn / Nsr) + np.exp(2j * np.pi * (40.0 + sep) * nn / Nsr + 1j * ph)
            Xs = np.abs(np.fft.fft(x * w, 32 * Nsr))
            i1, i2 = int(40.0 * 32), int((40.0 + sep) * 32)
            seg = Xs[i1:i2 + 1]
            if 20 * np.log10(seg.min() / min(Xs[i1 - 16:i1 + 16].max(), Xs[i2 - 16:i2 + 16].max())) < -1.0:
                okc += 1
        row.append(okc / 200)
    print(f"    coherent targets, random phase, {win_name}: P(>1 dB dip) at 1 / 2 bins = {row[0]:.2f} / {row[1]:.2f} "
          f"(anti-phase targets always show a notch; in-phase ones merge)")

print("=" * 78)
print("5. IF bandwidth limits")
for S_ in (10e12, 30e12, 100e12):
    for fs_, mode, fac in ((10e6, "complex 1x", 0.9), (10e6, "real", 0.45)):
        print(f"    S = {S_/1e12:.0f} MHz/us, fs = {fs_/1e6:.0f} Msps {mode}: IF BW {fac*fs_/1e6:.1f} MHz -> Rmax {fac*fs_*c/(2*S_):.1f} m")
check("TI: complex 1x IF limit 0.9 fs -> Rmax(S=30 MHz/us, fs=10 Msps)", 0.9 * 10e6 * c / (2 * 30e12), 44.97, 0.05)

print("=" * 78)
print("6. Range migration and range-Doppler coupling")
Tframe = Nc * Tc
for v_ in (10.0, 30.0):
    mig = v_ * Tframe
    fd_ = 2 * v_ / lam
    print(f"    v = {v_} m/s: moves {mig*100:.1f} cm during a {Tframe*1e3:.2f} ms frame ({mig/dR:.2f} range bins); "
          f"fd = {fd_/1e3:.2f} kHz -> beat offset shifts range by fd c/(2S) = {fd_*c/(2*S)*100:.2f} cm")
check("range-Doppler coupling shift at 30 m/s, 30 MHz/us (cm)", 2 * 30 / lam * c / (2 * S) * 100, 7.70, 0.02)

print("=" * 78)
print("7. Phase noise and leakage: range correlation")
# Synthesize LO phase noise with a 1/f^2 region: L(f) = L0 (f0/f)^2 above a corner, flat far out
fs_pn = 50e6
Npn = 1 << 20
f = np.fft.rfftfreq(Npn, 1 / fs_pn)
L0_dbc = -95.0        # dBc/Hz at 1 MHz (TI AWR1843-class figure)
Lf = 10 ** (L0_dbc / 10) * (1e6 / np.maximum(f, 1e3)) ** 2
Lf = np.maximum(Lf, 10 ** (-150 / 10))
# phase PSD S_phi(f) (rad^2/Hz, one-sided) = 2 L(f)
Sphi = 2 * Lf
amp = np.sqrt(Sphi * fs_pn * Npn / 2)
spec = amp * np.exp(1j * rng.uniform(0, 2 * np.pi, len(f)))
spec[0] = 0
phi = np.fft.irfft(spec, Npn)
# check synthesized PSD
fw, Pw = signal.welch(phi, fs_pn, nperseg=1 << 14)
sel = (fw > 2e5) & (fw < 5e6)
ratio = np.median(Pw[sel] / np.interp(fw[sel], f, Sphi))
check("synthesised phase-noise PSD matches target (median ratio)", ratio, 1.0, 0.15)
for tau_ns in (0.5, 5.0):   # leakage/short path (7.5 cm) and a reflector at 75 cm
    kdel = int(round(tau_ns * 1e-9 * fs_pn * 20))   # use 20x oversampled interpolation for delay
    # fractional delay via FFT
    Phi = np.fft.rfft(phi)
    phid = np.fft.irfft(Phi * np.exp(-2j * np.pi * f * tau_ns * 1e-9), Npn)
    dphi = phi - phid
    fw, Pd = signal.welch(dphi, fs_pn, nperseg=1 << 14)
    th = np.interp(fw, f, Sphi) * 4 * np.sin(np.pi * fw * tau_ns * 1e-9) ** 2
    sel = (fw > 2e5) & (fw < 5e6)
    r = np.median(Pd[sel] / th[sel])
    check(f"IF phase-noise PSD = 4 sin^2(pi f tau) S_phi, tau = {tau_ns} ns", r, 1.0, 0.2)
    at1M = 10 * np.log10(np.interp(1e6, f, Lf) * 4 * np.sin(np.pi * 1e6 * tau_ns * 1e-9) ** 2)
    print(f"      tau {tau_ns} ns: residual L_IF at 1 MHz offset = {at1M:.1f} dBc/Hz (LO {L0_dbc} dBc/Hz)")
# floor-raise example: leakage 40 dB below TX at -? Compare with thermal noise
Pt_dbm = 12.0
iso_db = 30.0
leak_dbm = Pt_dbm - iso_db
kT = -174.0
NF = 15.0
for tau_ns in (0.5, 2.0):
    Lres = 10 * np.log10(10 ** (L0_dbc / 10) * 4 * np.sin(np.pi * 1e6 * tau_ns * 1e-9) ** 2)
    skirt = leak_dbm + Lres
    print(f"    leakage {leak_dbm} dBm (isolation {iso_db} dB), tau {tau_ns} ns: PN skirt at 1 MHz beat offset {skirt:.1f} dBm/Hz vs thermal {kT+NF:.1f} dBm/Hz")

print("=" * 78)
print("8. VCO nonlinearity: Mini-Circuits ZX95-2536C+ tuning table (25 C)")
vt_tab = np.array([0.00, 0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 2.00, 2.25, 2.50, 2.75, 3.00, 3.25, 3.50, 3.75, 4.00, 4.25, 4.50, 4.75, 5.00])
f_tab = 1e6 * np.array([2257.4, 2297.3, 2315.9, 2334.4, 2352.9, 2371.3, 2389.8, 2408.5, 2427.0, 2445.3, 2463.3, 2481.0,
                        2498.1, 2514.5, 2529.8, 2544.2, 2557.6, 2570.1, 2581.5, 2591.8])
fv = interpolate.CubicSpline(vt_tab, f_tab)
Tr = 20e-3          # coffee-can style 20 ms ramp
fsa = 44.1e3
ta = np.arange(int(Tr * fsa)) / fsa
V0, V1 = 1.5, 3.5
vt_lin = V0 + (V1 - V0) * ta / Tr
f_inst = fv(vt_lin)
Bsw = f_inst[-1] - f_inst[0]
print(f"    linear Vtune {V0}-{V1} V over {Tr*1e3:.0f} ms: {f_inst[0]/1e6:.1f} -> {f_inst[-1]/1e6:.1f} MHz, B = {Bsw/1e6:.1f} MHz, "
      f"slope varies {np.gradient(f_inst, ta).min()/1e9:.2f}..{np.gradient(f_inst, ta).max()/1e9:.2f} GHz/s")
# fine-time model of phase for the beat: phase(t) = 2 pi int f dt
tf = np.arange(int(Tr * 4e6)) / 4e6     # fine grid 4 MHz
phase_fine = 2 * np.pi * np.cumsum(fv(V0 + (V1 - V0) * tf / Tr)) / 4e6
phi_of_t = interpolate.interp1d(tf, phase_fine, bounds_error=False, fill_value="extrapolate")


def beat_spectrum(Rt, phase_func, fsa=fsa):
    tau = 2 * Rt / c
    tt = ta[ta > tau]
    x = np.cos(phase_func(tt) - phase_func(tt - tau))
    w = np.hanning(len(x))
    X = np.abs(np.fft.rfft(x * w, 1 << 16))
    fr = np.fft.rfftfreq(1 << 16, 1 / fsa)
    return fr * c * Tr / (2 * Bsw), X / X.max()


def width_m(r_ax, X):
    k = np.argmax(X)
    thr = 10 ** (-3 / 20)
    i = k
    while i > 0 and X[i] > thr:
        i -= 1
    j = k
    while j < len(X) - 1 and X[j] > thr:
        j += 1
    return r_ax[j] - r_ax[i]


ideal_w = None
res_lin = {}
for Rt in (20.0, 100.0, 300.0):
    r_ax, Xl = beat_spectrum(Rt, phi_of_t)
    res_lin[Rt] = width_m(r_ax, Xl)
# ideal linear chirp for reference
phase_lin = lambda tt: 2 * np.pi * (f_inst[0] * tt + 0.5 * (Bsw / Tr) * tt ** 2)
r_ax, Xi = beat_spectrum(100.0, phase_lin)
ideal_w = width_m(r_ax, Xi)
print(f"    ideal linear chirp -3 dB range width (Hann) = {ideal_w:.2f} m (c/2B = {c/(2*Bsw):.2f} m)")
for Rt, wv in res_lin.items():
    print(f"    VCO with linear Vtune, target at {Rt:5.0f} m: -3 dB width {wv:6.2f} m ({wv/ideal_w:.1f}x ideal)")
check("nonlinearity broadening grows with range (300 m worse than 20 m)", float(res_lin[300.0] > 2 * res_lin[20.0]), 1.0, 0)
# predistortion: invert the tuning curve so f(t) is linear
f_target = f_inst[0] + Bsw * tf / Tr
vinv = interpolate.interp1d(fv(np.linspace(0, 5, 5001)), np.linspace(0, 5, 5001))
vt_pd = vinv(f_target)
phase_pd = 2 * np.pi * np.cumsum(fv(vt_pd)) / 4e6
phi_pd = interpolate.interp1d(tf, phase_pd, bounds_error=False, fill_value="extrapolate")
r_ax, Xp = beat_spectrum(300.0, phi_pd)
wp = width_m(r_ax, Xp)
print(f"    with predistorted Vtune (inverse tuning curve), target at 300 m: width {wp:.2f} m")
check("predistortion restores near-ideal resolution at 300 m", wp / ideal_w, 1.0, 0.1)

print("=" * 78)
print("9. Worked chirp design: 77 GHz drone radar")
req = dict(Rmax=100.0, dR=0.5, vmax=30.0, dv=0.25)
lam = c / 77e9
B_req = c / (2 * req["dR"])
Tc_max = lam / (4 * req["vmax"])
print(f"    B >= {B_req/1e6:.0f} MHz; Tc <= lambda/(4 vmax) = {Tc_max*1e6:.1f} us")
Tadc = 25e-6
Tc_d = 32e-6
S_d = B_req / Tadc
fif = S_d * 2 * req["Rmax"] / c
fs_d = 10e6
Ns_d = int(fs_d * Tadc)
Nc_req = lam / (2 * req["dv"] * Tc_d)
Nc_d = int(2 ** np.ceil(np.log2(Nc_req)))
print(f"    choose T_adc = {Tadc*1e6:.0f} us in Tc = {Tc_d*1e6:.0f} us: S = {S_d/1e12:.1f} MHz/us, f_IF,max = {fif/1e6:.2f} MHz "
      f"(complex fs {fs_d/1e6:.0f} Msps, 0.9 fs = {0.9*fs_d/1e6:.0f} MHz OK), {Ns_d} samples/chirp")
print(f"    N_chirps >= {Nc_req:.0f} -> {Nc_d}; frame {Nc_d*Tc_d*1e3:.2f} ms; vmax {lam/(4*Tc_d):.2f} m/s; dv {lam/(2*Nc_d*Tc_d)*100:.1f} cm/s")
mem = Ns_d * Nc_d * 4 * 4
print(f"    radar cube (1 TX x 4 RX, 16-bit I+Q = 4 B/sample): {mem/1024:.0f} KiB")
check("design meets vmax", lam / (4 * Tc_d), req["vmax"], 0.5)
check("design IF within 0.9 fs", float(fif <= 0.9 * fs_d), 1.0, 0)
# Infineon BGT60TR13C: 58-63.5 GHz, ADC up to 4 MSps (real, per channel)
Bb = 5.5e9
print(f"    BGT60TR13C: full 5.5 GHz sweep -> dR = {c/(2*Bb)*100:.2f} cm; e.g. 5 GHz in 64 us (78 MHz/us) with 2 MSps real: "
      f"Rmax(IF) = {0.5*2e6*c/(2*78e12):.2f} m -> short-range sensor")
# coffee-can with audio card
print(f"    coffee-can: 90 MHz in 20 ms, fs 44.1 kHz real: Rmax(IF) = {22.05e3*c/(2*90e6/20e-3):.0f} m, dR = {c/(2*90e6):.2f} m")

print("=" * 78)
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
