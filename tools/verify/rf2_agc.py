#!/usr/bin/env python3
"""Verification for kb/06-rf-circuits/agc-loops-and-receiver-gain-control.md  (W5-E7)

 A. dB-linear VGA + log detector + integrator: first-order loop in the dB domain, tau = 1/(Kv Kd KI)
    independent of input level (time-domain simulation of 10/40/60 dB steps)
 B. linear-gain VGA + linear envelope detector: tau inversely proportional to signal amplitude
 C. detector ripple filter -> second-order loop, zeta = 0.5 sqrt(tau/tau_f); overshoot vs formula
 D. attack/decay asymmetry; settling time t_s = tau ln(dP/eps); LoRa preamble budget; AM pumping
 E. digital AGC in dB with loop delay D: stability bound mu < 2 sin(pi/(2(2D+1)))
 F. gain-control policy for a receiver cascade: NF and IIP3 vs input level, "IF first, RF late"
 G. RSSI: SX127x packet-strength formulas; exact S = P_tot + SNR - 10log(1+SNR) vs Semtech approx;
    RSSI averaging statistics (dB std of an N-sample noise power estimate)
 H. DSP features: noise blanker (impulses before the narrow filter), LMS adaptive line enhancer (NR)
    and LMS auto-notch (ANF)
Run: python3 tools/verify/rf2_agc.py   (runtime ~15 s)
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rf2_common import check, finish
from scipy import signal

rng = np.random.default_rng(7)

print("=== A. dB-linear (exponential) VGA + log detector")
Kv = 20.0         # dB per volt (VGA gain slope)
Kd = 0.025        # V per dB (log detector slope, AD8307-like 25 mV/dB)
KI = 400.0        # 1/s integrator gain (V/s per V of error)
tau = 1 / (Kv * Kd * KI)
print(f"  Kv={Kv} dB/V, Kd={Kd*1e3:.0f} mV/dB, KI={KI}/s -> tau = {tau*1e3:.2f} ms")
dt = 1e-6


def sim_db_loop(step_db, T=0.03, Pin0=-60.0, target=-10.0):
    n = int(T / dt)
    Pin = np.full(n, Pin0); Pin[n // 5:] += step_db
    Vc = (target - Pin0 - 0.0) / Kv          # settled for initial level (G0 = 0 dB)
    Pout = np.empty(n)
    for k in range(n):
        Pout[k] = Pin[k] + Kv * Vc
        Vdet = Kd * (Pout[k] - target)
        Vc += -KI * Vdet * dt
    return Pout, n // 5


taus = []
for step in (10, 40, 60):
    Pout, k0 = sim_db_loop(step)
    err = Pout[k0:] - (-10)
    k63 = np.argmax(err <= step * np.exp(-1))
    taus.append(k63 * dt)
    print(f"  step +{step} dB: 1/e time {k63*dt*1e3:.3f} ms; settle to 1 dB in {np.argmax(err <= 1)*dt*1e3:.2f} ms "
          f"(formula tau ln(step/1) = {tau*np.log(step)*1e3:.2f} ms)")
check("dB-domain loop: same time constant for 10/40/60 dB steps (level-independent)",
      max(taus) / min(taus) < 1.01 and abs(taus[0] / tau - 1) < 0.01)

print("\n=== B. linear-gain VGA + envelope detector (loop gain ~ signal)")
a = 1.0; K = 2000.0; r = 0.316       # gain = a*Vc, detector = |y|, reference amplitude r


def sim_lin(x0, x1):
    tau1 = 1 / (a * K * x1); dtl = tau1 / 2000; n = int(8 * tau1 / dtl)
    x = np.full(n, x0); x[n // 5:] = x1
    Vc = r / (a * x0); y = np.empty(n)
    for k in range(n):
        y[k] = a * Vc * x[k]
        Vc += K * (r - y[k]) * dtl
        Vc = max(Vc, 0)
    return y, n // 5, dtl


for x0, x1 in [(1e-3, 0.5e-3), (1e-1, 0.5e-1)]:
    y, k0, dtl = sim_lin(x0, x1)
    e = r - y[k0:]
    kk = np.argmax(e <= (r - r / 2) * np.exp(-1))
    print(f"  amplitude {x0:g} -> {x1:g} (-6 dB): time constant {kk*dtl*1e3:.3f} ms; theory 1/(aKx1) = {1/(a*K*x1)*1e3:.3f} ms")
    if x0 == 1e-3:
        t_small = kk * dtl
    else:
        t_big = kk * dtl
check("linear VGA loop: 40 dB higher signal -> ~100x faster loop", 80 < t_small / t_big < 120, f"ratio {t_small/t_big:.1f}")

print("\n=== C. detector ripple filter -> second-order loop")
for tau_f_ratio in (0.125, 0.5, 2.0):
    tau_f = tau * tau_f_ratio
    zeta = 0.5 * np.sqrt(tau / tau_f)
    n = int(0.03 / dt); Pin = np.full(n, -60.0); Pin[n // 5:] += 20
    Vc = 50 / Kv; Vf = 0.0; Pout = np.empty(n)
    for k in range(n):
        Pout[k] = Pin[k] + Kv * Vc
        Vdet = Kd * (Pout[k] + 10)
        Vf += (Vdet - Vf) * dt / tau_f
        Vc += -KI * Vf * dt
    resp = -(Pout[n // 5:] + 10) / 20 + 1          # normalised: 0 -> 1 (error decays)
    # step response of the *error* in dB: e(t)/20, overshoot = min below zero
    e = (Pout[n // 5:] + 10) / 20
    ovs = max(0.0, -e.min())
    ovs_th = np.exp(-np.pi * zeta / np.sqrt(1 - zeta ** 2)) if zeta < 1 else 0.0
    print(f"  tau_f/tau = {tau_f_ratio}: zeta = {zeta:.3f}, undershoot of the dB error {ovs*100:.1f} % (2nd-order theory {ovs_th*100:.1f} %)")
    if tau_f_ratio == 0.5:
        ok_c = abs(ovs - ovs_th) < 0.01
check("ripple-filter pole: zeta = 0.5 sqrt(tau/tau_f) predicts the overshoot (tau_f = tau/2 -> zeta 0.707, 4.3 %)", ok_c)
# ripple attenuation of a 1-pole filter at 2 f_IF and its gain-modulation consequence
fif = 455e3; tau_f = tau / 2
att = 20 * np.log10(1 / np.sqrt(1 + (2 * np.pi * 2 * fif * tau_f) ** 2))
print(f"  ripple at 2 x 455 kHz through tau_f = {tau_f*1e3:.2f} ms: {att:.0f} dB")

print("\n=== D. attack / decay and burst budgets")
# LoRa SF7 BW125: preamble 8 symbols + 4.25; symbol = 2^SF/BW
for SF in (7, 9, 12):
    Ts = 2 ** SF / 125e3
    t_pre = 8 * Ts
    tau_max = t_pre / 4 / np.log(40 / 1)       # settle 40 dB to 1 dB within a quarter of the preamble
    print(f"  SF{SF}/125 kHz: symbol {Ts*1e3:.3f} ms, 8-symbol preamble {t_pre*1e3:.2f} ms ->"
          f" attack tau <= {tau_max*1e3:.3f} ms to settle 40 dB within 1 dB in a quarter of it")
    if SF == 7:
        tau_sf7 = tau_max
check("SF7 needs attack tau <= ~0.56 ms (40 dB -> 1 dB in 2 ms)", abs(tau_sf7 * 1e3 - 0.555) < 0.01)
# AM pumping: a loop of bandwidth f_L = 1/(2 pi tau) partly removes AM at f_m: residual modulation |H(f)|,
# high-pass  H = j w tau / (1 + j w tau) in the dB domain
for tau_x, fm in [(1e-3, 300.0), (50e-3, 300.0)]:
    H = abs(1j * 2 * np.pi * fm * tau_x / (1 + 1j * 2 * np.pi * fm * tau_x))
    print(f"  AM at {fm:.0f} Hz through an AGC with tau = {tau_x*1e3:.0f} ms keeps {20*np.log10(H):.1f} dB of its depth")
    if tau_x == 1e-3:
        H1 = H
check("fast AGC (1 ms) strips ~1 dB of a 300 Hz AM envelope; slow AGC (50 ms) keeps it", 20 * np.log10(H1) < -0.5)
# asymmetric attack/decay on a burst: attack 1 ms, decay 300 ms: gain recovers slowly after a strong burst
ta, td = 1e-3, 0.3
n = int(2.0 / 1e-4); dtt = 1e-4
Pin = np.full(n, -100.0); Pin[int(0.1 / dtt):int(0.15 / dtt)] = -40.0      # 50 ms strong burst
g = 90.0; out = np.empty(n)
for k in range(n):
    out[k] = Pin[k] + g
    e = out[k] - (-10)
    g -= e * dtt / (ta if e > 0 else td)
k_after = int(0.15 / dtt)
rec = np.argmax(out[k_after:] >= -10 - 3) * dtt
print(f"  after a 50 ms burst 60 dB above the wanted signal: output recovers to within 3 dB of target after {rec*1e3:.0f} ms"
      f" (formula td ln(60/3) = {td*np.log(60/3)*1e3:.0f} ms)")
check("decay recovery time = t_d ln(dP/eps)", abs(rec / (td * np.log(60 / 3)) - 1) < 0.03)

print("\n=== E. digital AGC with loop delay")
for D in (0, 1, 2, 4, 8):
    mu_th = 2 * np.sin(np.pi / (2 * (2 * D + 1)))
    # numerical: largest mu with all roots of z^{D+1} - z^D + mu inside unit circle
    mus = np.linspace(0.001, 2.2, 4000)
    mmax = 0
    for mu in mus:
        coeffs = np.zeros(D + 2); coeffs[0] = 1; coeffs[1] = -1; coeffs[-1] += mu
        if np.all(np.abs(np.roots(coeffs)) < 1):
            mmax = mu
        else:
            break
    print(f"  delay D={D}: mu_max numerical {mmax:.4f}, formula 2 sin(pi/(2(2D+1))) = {mu_th:.4f}")
    if D == 4:
        ok_e = abs(mmax - mu_th) < 2e-3
check("digital AGC stability bound with delay matches 2 sin(pi/(2(2D+1)))", ok_e)

print("\n=== F. where to take the gain out (cascade policy)")
# stages: LNA (G 18, NF 1.2, IIP3 -8 dBm) with a 20 dB bypass step (G -2? use G -2 dB, NF 2, IIP3 +20 in bypass)
# mixer (G 8, NF 9, IIP3 +12), IF VGA 0..50 dB (NF 6 at max gain, NF rises 1 dB per dB of reduction, IIP3 -5 dBm at max,
# rising 1 dB per dB of reduction), ADC: full scale -5 dBm, NF 28 dB (in channel)
def cascade(stages):
    F = 1.0; G = 1.0; inv_ip3 = 0.0
    for (g, nf, iip3) in stages:
        F += (10 ** (nf / 10) - 1) / G
        inv_ip3 += G / (10 ** (iip3 / 10))
        G *= 10 ** (g / 10)
    return 10 * np.log10(G), 10 * np.log10(F), -10 * np.log10(inv_ip3)


def chain(lna_on, if_red):
    lna = (18, 1.2, -8) if lna_on else (-2, 2.0, 20)
    mix = (8, 9, 12)
    vga = (50 - if_red, 6 + if_red, -5 + if_red)
    adc = (0, 28, 25)
    return cascade([lna, mix, vga, adc])


target = -15.0            # signal power at the ADC (dBm), 10 dB below full scale
res = {}
G_on, G_byp = chain(True, 0)[0], chain(False, 0)[0]
for policy in ("IF first, LNA step late", "LNA step first"):
    rows = []
    for Pin in (-110, -80, -60, -50, -40, -30):
        red_on = G_on + Pin - target
        if policy.startswith("IF"):
            if red_on <= 50:
                best = (True, max(red_on, 0.0))
            else:
                best = (False, min(max(G_byp + Pin - target, 0.0), 50.0))
        else:   # bypass the LNA as soon as any gain reduction is needed
            if red_on <= 0:
                best = (True, 0.0)
            else:
                best = (False, min(max(G_byp + Pin - target, 0.0), 50.0))
        G, NF, IIP3 = chain(*best)
        rows.append((Pin, best[0], best[1], NF, IIP3))
    res[policy] = rows
    print(f"  policy: {policy}")
    for Pin, lon, red, NF, IIP3 in rows:
        print(f"    Pin {Pin:5d} dBm: LNA {'on ' if lon else 'byp'}, IF reduction {red:5.1f} dB -> NF {NF:5.1f} dB, IIP3 {IIP3:6.1f} dBm,"
              f" IIP3 - Pin = {IIP3-Pin:5.1f} dB")
rA = {r[0]: r for r in res["IF first, LNA step late"]}
check("IF-first policy keeps NF within 0.5 dB of best up to -80 dBm input", rA[-80][3] < rA[-110][3] + 0.5)
check("at -30 dBm the policy still leaves IIP3 >= 15 dB above the signal", rA[-30][4] - (-30) >= 15)
rB = {r[0]: r for r in res["LNA step first"]}
check("RF-first policy pays >= 5 dB more NF at a moderate -80 dBm signal", rB[-80][3] - rA[-80][3] >= 5)

print("\n=== G. RSSI arithmetic")
# SX127x LoRa HF port: Packet Strength = -157 + PacketRssi (+ PacketSnr*0.25 when SNR<0, PacketSnr in 0.25 dB units)
pr, psnr = 40, -40
ps = -157 + pr + (psnr * 0.25 if psnr < 0 else 0)
print(f"  PacketRssi=40, PacketSnr reg=-40 (-10 dB): Packet Strength = {ps} dBm (in-band total power -117 dBm)")
check("Semtech formula example gives -127 dBm", ps == -127)
for snr_db in (-15, -10, -5, 0, 5):
    snr = 10 ** (snr_db / 10)
    Ptot = -117.0
    S_exact = Ptot + snr_db - 10 * np.log10(1 + snr)
    S_semtech = Ptot + (snr_db if snr_db < 0 else 0)
    print(f"  SNR {snr_db:+3d} dB: exact signal {S_exact:7.2f} dBm, Semtech rule {S_semtech:7.2f} dBm, error {S_semtech-S_exact:+.2f} dB")
    if snr_db == -10:
        err10 = S_semtech - S_exact
    if snr_db == 0:
        err0 = S_semtech - S_exact
check("Semtech SNR<0 rule is within 0.5 dB below -10 dB SNR, off by ~3 dB at SNR = 0 dB", abs(err10) < 0.5 and abs(err0 - 3.0) < 0.1)
# averaging: power estimate from N independent complex Gaussian samples -> std in dB
for N in (2, 16, 256):
    x = (rng.standard_normal((20000, N)) + 1j * rng.standard_normal((20000, N))) / np.sqrt(2)
    est = 10 * np.log10(np.mean(np.abs(x) ** 2, axis=1))
    print(f"  N={N:3d}: RSSI std {np.std(est):.2f} dB (approx 4.34/sqrt(N) = {4.34/np.sqrt(N):.2f}); Semtech table ±6/±3/±1.1 dB")
    if N == 16:
        s16 = np.std(est)
check("noise-power estimate std ~ 4.34/sqrt(N) dB (N=16 -> ~1.1 dB)", abs(s16 - 4.34 / 4) < 0.1)
# FSK RSSI response time 2^(RssiSmoothing+1)/(4 RxBw[kHz]) ms
for sm, bw in ((3, 10.4), (3, 125.0), (7, 10.4)):
    print(f"  SX127x FSK: RssiSmoothing={sm} ({2**(sm+1)} samples), RxBw {bw} kHz -> response {2**(sm+1)/(4*bw):.3f} ms")

print("\n=== H. receiver DSP features")
fs = 48000.0
t = np.arange(int(2.0 * fs)) / fs
# --- noise blanker: wanted CW tone 1 kHz weak, white noise, impulses 100/s of 0.1 ms, very strong
tone = 0.01 * np.cos(2 * np.pi * 1000 * t)
noise = 0.003 * rng.standard_normal(len(t))
imp = np.zeros(len(t))
for k0 in np.arange(0, len(t), int(fs / 100)):
    w = int(0.0001 * fs) + 1
    imp[k0:k0 + w] = 2.0 * np.sign(rng.standard_normal())
x = tone + noise + imp
b, a_ = signal.butter(4, [900 / (fs / 2), 1100 / (fs / 2)], btype="band")


def snr_tone(y, f=1000.0):
    Y = np.fft.rfft(y * np.hanning(len(y)))
    fr = np.fft.rfftfreq(len(y), 1 / fs)
    sig = np.sum(np.abs(Y[(fr > f - 5) & (fr < f + 5)]) ** 2)
    nb = np.sum(np.abs(Y[(fr > 900) & (fr < 1100) & ((fr < f - 20) | (fr > f + 20))]) ** 2)
    nbw = np.sum((fr > 900) & (fr < 1100) & ((fr < f - 20) | (fr > f + 20)))
    return 10 * np.log10(sig / (nb / nbw * np.sum((fr > f - 5) & (fr < f + 5))))


y_plain = signal.lfilter(b, a_, x)
thr = 6 * np.std(tone + noise)
gate = np.abs(x) > thr
gate = np.convolve(gate, np.ones(9), mode="same") > 0          # widen the blanking window slightly
xb = np.where(gate, 0.0, x)
y_nb = signal.lfilter(b, a_, xb)
y_ref = signal.lfilter(b, a_, tone + noise)
s_plain, s_nb, s_ref = snr_tone(y_plain), snr_tone(y_nb), snr_tone(y_ref)
print(f"  CW tone SNR in a 200 Hz filter: no impulses {s_ref:.1f} dB; impulses, no blanker {s_plain:.1f} dB;"
      f" blanked before the filter {s_nb:.1f} dB (blanked {100*gate.mean():.1f} % of samples)")
check("noise blanker ahead of the narrow filter recovers > 20 dB", s_nb - s_plain > 20)
# blanking after the narrow filter does not work: impulses are already stretched to ~1/B and below threshold
y_late = np.where(np.abs(y_plain) > 6 * np.std(y_ref), 0.0, y_plain)
s_late = snr_tone(y_late)
print(f"  blanking after the 200 Hz filter instead: {s_late:.1f} dB")
check("blanking after the narrow filter is much worse than before it", s_nb - s_late > 10)

# --- LMS adaptive line enhancer (NR) and auto-notch (ANF)


def lms(xin, D, Ntap, mu):
    w = np.zeros(Ntap); y = np.zeros(len(xin)); e = np.zeros(len(xin))
    buf = np.zeros(Ntap)
    for n in range(D + Ntap, len(xin)):
        buf = xin[n - D - Ntap + 1:n - D + 1][::-1]
        y[n] = w @ buf
        e[n] = xin[n] - y[n]
        w += 2 * mu * e[n] * buf / (buf @ buf + 1e-9)        # normalised LMS
    return y, e


tone_ale = 0.05 * np.cos(2 * np.pi * 700 * t[:48000])
wn = 0.1 * rng.standard_normal(48000)
y_ale, e_ale = lms(tone_ale + wn, D=4, Ntap=64, mu=0.002)
seg = slice(24000, 48000)


def band_snr(y, f0, ref_tone):
    # SNR of a tone: projection on the known tone vs residual in a 0-4 kHz band
    yy = y[seg]; tt = ref_tone[seg]
    g = (yy @ tt) / (tt @ tt)
    resid = yy - g * tt
    bb, aa = signal.butter(6, 4000 / (fs / 2))
    resid = signal.lfilter(bb, aa, resid)
    return 10 * np.log10((g * g * (tt @ tt)) / (resid @ resid))


snr_in = band_snr(tone_ale + wn, 700, tone_ale)
snr_out = band_snr(y_ale, 700, tone_ale)
print(f"  LMS line enhancer (64 taps, delay 4): tone SNR in 0-4 kHz {snr_in:.1f} dB -> {snr_out:.1f} dB")
check("ALE improves SNR of a periodic signal in white noise by > 6 dB", snr_out - snr_in > 6)
# ANF: strong heterodyne at 1.5 kHz on top of broadband 'speech-like' noise; error output removes the tone
het = 0.5 * np.cos(2 * np.pi * 1500 * t[:48000])
speech = signal.lfilter(*signal.butter(4, [300 / (fs / 2), 3000 / (fs / 2)], btype="band"), rng.standard_normal(48000)) * 0.1
y_anf, e_anf = lms(het + speech, D=48, Ntap=128, mu=0.002)
g_in = (het[seg] @ (het + speech)[seg]) / (het[seg] @ het[seg])
g_out = (het[seg] @ e_anf[seg]) / (het[seg] @ het[seg])
supp = 20 * np.log10(abs(g_out) / abs(g_in))
keep = 10 * np.log10(np.var(e_anf[seg] - g_out * het[seg]) / np.var(speech[seg]))
print(f"  LMS auto-notch: 1.5 kHz heterodyne suppressed by {-supp:.1f} dB; broadband signal power change {keep:+.1f} dB")
check("ANF removes the tone by > 20 dB while passing the broadband signal within 1.5 dB", supp < -20 and abs(keep) < 1.5)
print("  (decorrelation delay 48 samples = 1 ms, longer than the broadband signal's correlation time)")

finish()
