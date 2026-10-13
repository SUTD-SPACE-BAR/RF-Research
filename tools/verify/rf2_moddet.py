#!/usr/bin/env python3
"""Verification for kb/06-rf-circuits/modulator-and-detector-circuits.md  (W5-E7)

 A. Varactor FM modulator: f(V), K_v, deviation linearity for abrupt (gamma 0.5) vs hyperabrupt (gamma 2)
    junctions, 2nd-harmonic distortion of the modulation
 B. Reactance modulator: Y = (1 + gm R)/(R + 1/jwC) -> C_eq ~ (1 + gm R) C; and a PM modulator
    (varactor-tuned tuned amplifier): dphi = atan(2Q df0/f0) ~ Q dC/C
 C. Balanced modulator (DSB-SC): carrier suppression vs baseband offset/imbalance; phasing-SSB
    opposite-sideband suppression vs gain/phase error
 D. Envelope detector (ngspice transient, Schottky diode): ripple vs diagonal clipping,
    RC <= sqrt(1-mu^2)/(mu w_m); THD of the recovered tone for RC inside/outside the limit
 E. Product / synchronous detection: phase error -> cos(theta); AM with a faded carrier: envelope
    detector distorts, synchronous detector does not
 F. FM discriminators: quadrature detector S-curve sin(atan(2Q df/f0)); Foster-Seeley and ratio
    detector S-curves; AM rejection of the ratio detector; PLL demodulator output = df/Kv
Run: python3 tools/verify/rf2_moddet.py   (runtime ~15 s; ngspice used in D)
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rf2_common import check, finish, ngspice
from scipy import signal


def thd(x, fs, f0, nh=6):
    X = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    fr = np.fft.rfftfreq(len(x), 1 / fs)
    def amp(f):
        i = np.argmin(np.abs(fr - f)); return np.sqrt(np.sum(X[max(i - 3, 0):i + 4] ** 2))
    a1 = amp(f0)
    return np.sqrt(sum(amp(k * f0) ** 2 for k in range(2, nh + 1))) / a1


print("=== A. varactor FM modulator")
f0 = 433.92e6


def vco(gam, Cj0, phi, Vb, Cfix):
    Cv = lambda V: Cj0 / (1 + V / phi) ** gam
    L = 1 / ((2 * np.pi * f0) ** 2 * (Cfix + Cv(Vb)))
    return lambda V: 1 / (2 * np.pi * np.sqrt(L * (Cfix + Cv(V))))


for gam, Cj0, Cfix, name in [(0.5, 10e-12, 3e-12, "abrupt (gamma 0.5)"), (2.0, 60e-12, 0.0, "hyperabrupt (gamma 2), varactor only")]:
    fV = vco(gam, Cj0, 0.7, 4.0, Cfix)
    Kv = (fV(4.001) - fV(3.999)) / 0.002
    tt = np.arange(8192) / 8192.0
    Vmod = 4.0 + 0.5 * np.sin(2 * np.pi * 16 * tt)
    finst = fV(Vmod) - f0
    h = thd(finst - finst.mean(), 8192, 16)
    print(f"  {name}: K_v = {Kv/1e6:.2f} MHz/V at 4 V; +-0.5 V tone -> peak deviation {(finst.max()-finst.min())/2/1e6:.2f} MHz,"
          f" modulation THD {h*100:.2f} %")
    if gam == 0.5:
        thd_ab = h
    else:
        thd_hy = h
check("hyperabrupt gamma = 2 varactor alone gives (near-)linear f(V): THD << abrupt junction", thd_hy < 0.2 * thd_ab)

print("\n=== B. reactance and phase modulators")
w = 2 * np.pi * 10.7e6
C, R = 2e-12, 100.0
for gm in (5e-3, 20e-3, 50e-3):
    Y = (1 + gm * R) / (R + 1 / (1j * w * C))
    Ceq = Y.imag / w; Geq = Y.real
    print(f"  gm {gm*1e3:.0f} mS: C_eq {Ceq*1e12:.2f} pF (approx (1+gm R) C = {(1+gm*R)*C*1e12:.2f}), parallel loss R {1/Geq/1e3:.1f} kohm")
    if gm == 20e-3:
        okB = abs(Ceq / ((1 + gm * R) * C) - 1) < 0.01
check("reactance modulator C_eq = (1 + gm R) C when wRC << 1", okB)
Qt = 20.0
for dCrel in (0.005, 0.02, 0.05):
    df0 = -f0 * dCrel / 2
    dphi = np.degrees(np.arctan(2 * Qt * df0 / f0))
    print(f"  PM: tuned stage Q {Qt:.0f}, dC/C = {dCrel*100:.1f} % -> phase shift {dphi:.1f} deg (linear approx Q dC/C = {-np.degrees(Qt*dCrel):.1f})")
check("PM modulator linear for small dC/C (0.5 %: within 1 %)", abs(np.arctan(2 * Qt * (-0.0025)) / (-Qt * 0.005) - 1) < 0.01)

print("\n=== C. balanced modulator and phasing SSB")
fs = 1e6; t = np.arange(200000) / fs; fc = 100e3; fm = 1e3
for delta in (0.0, 0.01, 0.003):
    lo = np.sign(np.cos(2 * np.pi * fc * t))
    y = lo * (np.cos(2 * np.pi * fm * t) + delta)
    Y = np.abs(np.fft.rfft(y * np.hanning(len(y)))); fr = np.fft.rfftfreq(len(y), 1 / fs)
    amp = lambda f: Y[np.argmin(np.abs(fr - f))]
    cs = 20 * np.log10(amp(fc) / amp(fc + fm) + 1e-12)
    print(f"  baseband offset {delta*100:.1f} % of modulation peak: carrier {cs:.1f} dB relative to one sideband (theory {20*np.log10(max(2*delta,1e-12)):.1f})")
    if delta == 0.01:
        cs1 = cs
check("DSB-SC carrier leak = 2 x offset ratio (1 % offset -> -34 dB re one sideband)", abs(cs1 - 20 * np.log10(0.02)) < 0.5)
for g, ph in ((1.0, 1.0), (1.01, 0.0), (1.02, 2.0)):
    p = np.radians(ph)
    supp = 10 * np.log10((1 + g ** 2 + 2 * g * np.cos(p)) / (1 + g ** 2 - 2 * g * np.cos(p)))
    # time-domain phasing modulator check
    I = np.cos(2 * np.pi * fm * t); Q = g * np.sin(2 * np.pi * fm * t + p)
    s = I * np.cos(2 * np.pi * fc * t) - Q * np.sin(2 * np.pi * fc * t)
    S = np.abs(np.fft.rfft(s * np.hanning(len(s))))
    usb = S[np.argmin(np.abs(fr - (fc + fm)))]; lsb = S[np.argmin(np.abs(fr - (fc - fm)))]
    print(f"  phasing SSB, gain {g}, phase error {ph} deg: unwanted sideband {20*np.log10(lsb/usb):.1f} dB (formula {-supp:.1f})")
    if ph == 2.0:
        okC = abs(20 * np.log10(lsb / usb) + supp) < 0.3
check("phasing-SSB suppression formula matches simulation", okC)

# high-level (collector/drain) AM of a saturated PA: P_out ~ Vdd^2 -> average (1 + mu^2/2) P0; audio supplies mu^2/2 P0
for mu_ in (0.5, 1.0):
    th_ = np.linspace(0, 2 * np.pi, 100001)
    pav = np.mean((1 + mu_ * np.cos(th_)) ** 2)
    print(f"  collector AM, mu {mu_}: average RF power {pav:.4f} x carrier; modulator must supply {pav-1:.4f} x the DC input")
check("high-level AM: modulator audio power = mu^2/2 of the DC input (mu=1 -> 50 %)", abs(np.mean((1 + np.cos(np.linspace(0, 2*np.pi, 100001))) ** 2) - 1.5) < 1e-4)

print("\n=== D. envelope detector (ngspice)")
fcar = 455e3; fmod = 3e3; mu = 0.8
RC_lim = np.sqrt(1 - mu ** 2) / (mu * 2 * np.pi * fmod)
print(f"  mu = {mu}, f_m = {fmod/1e3:.0f} kHz: diagonal-clipping limit RC <= {RC_lim*1e6:.1f} us; ripple needs RC >> 1/f_c = {1e6/fcar:.2f} us")
res_d = {}
for RCv in (5e-6, 20e-6, 100e-6):
    Rl = 10e3; Cl = RCv / Rl
    net = (f"VS a 0 SIN(0 2 {fcar} 0 0 0)\n"
           f"BMOD b 0 V = v(a) * (1 + {mu} * sin(2*3.14159265*{fmod}*time))\n"
           f"RS b c 50\nD1 c out DSCH\nRL out 0 {Rl}\nCL out 0 {Cl}\n"
           ".model DSCH D(IS=3e-8 N=1.06 RS=25 CJO=0.18p)\n")
    T = 12 / fmod
    tt, (vo,) = ngspice(net, f".tran 0.1u {T} 0 0.1u", ["v(out)"])
    m = tt > 4 / fmod
    tu = np.linspace(tt[m][0], tt[m][-1], 2 ** 16); vu = np.interp(tu, tt[m], vo[m])
    b, a = signal.butter(4, 20e3 / (0.5 / (tu[1] - tu[0])))
    va = signal.filtfilt(b, a, vu)
    h = thd(va - va.mean(), 1 / (tu[1] - tu[0]), fmod)
    res_d[RCv] = h
    print(f"  RC = {RCv*1e6:.0f} us: recovered-tone THD {h*100:.1f} % ({'inside' if RCv <= RC_lim else 'outside'} the clipping limit)")
check("RC beyond the diagonal-clipping limit distorts much more (100 us vs 20 us)", res_d[100e-6] > 3 * res_d[20e-6])
check("RC = 20 us (inside the limit) recovers the tone with THD < 5 %", res_d[20e-6] < 0.05)

print("\n=== E. product and synchronous detection")
fs = 400e3; t = np.arange(int(0.1 * fs)) / fs; fc = 50e3; fm = 1e3
m_t = np.cos(2 * np.pi * fm * t)
dsb = m_t * np.cos(2 * np.pi * fc * t)
bl, al = signal.butter(5, 5e3 / (fs / 2))
for th in (0, 45, 90):
    out = signal.filtfilt(bl, al, dsb * np.cos(2 * np.pi * fc * t + np.radians(th)) * 2)
    g = np.std(out) / np.std(m_t)
    print(f"  DSB-SC product detection, LO phase error {th} deg: output gain {g:.3f} (cos theta = {np.cos(np.radians(th)):.3f})")
    if th == 45:
        okE1 = abs(g - np.cos(np.radians(45))) < 0.01
check("coherent detector output scales as cos(theta)", okE1)
# AM with carrier selectively faded by 10 dB (sidebands intact): effective modulation index > 1
mu0 = 0.7; cf = 10 ** (-10 / 20)
am_faded = (cf + mu0 * m_t) * np.cos(2 * np.pi * fc * t)
env = signal.filtfilt(bl, al, np.abs(signal.hilbert(am_faded)))
syn = signal.filtfilt(bl, al, am_faded * np.cos(2 * np.pi * fc * t) * 2)
h_env, h_syn = thd(env - env.mean(), fs, fm), thd(syn - syn.mean(), fs, fm)
print(f"  AM (mu 0.7) with the carrier faded 10 dB: envelope detector THD {h_env*100:.1f} %, synchronous detector THD {h_syn*100:.2f} %")
check("selective carrier fading: synchronous AM detection stays clean, envelope detection distorts", h_syn < 0.01 and h_env > 0.1)

print("\n=== F. FM discriminators")
x = np.linspace(-3, 3, 601)                                   # x = 2 Q df / f0
quad = np.sin(np.arctan(x))
lin_lim = np.sqrt(1 / 0.95 ** 2 - 1)        # sin(atan x)/x = 1/sqrt(1+x^2) >= 0.95
print(f"  quadrature detector S-curve sin(atan(2Q df/f0)): linear within 5 % for |2Q df/f0| < {abs(lin_lim):.2f}")
# time-domain quadrature detector: FM at IF 10.7 MHz -> phase network = parallel tank Q driven via a small series C
fs = 200e6; N = 2 ** 17; t = np.arange(N) / fs; fif = 10.7e6; Qq = 20.0
devs = np.array([-150e3, -75e3, 0, 75e3, 150e3])
outs = []
w0 = 2 * np.pi * fif
b_bp, a_bp = signal.iirpeak(fif / (fs / 2), Qq)                # resonator (tank) response
for d in devs:
    s = np.sign(np.cos(2 * np.pi * (fif + d) * t))               # limited IF
    sq = signal.lfilter(b_bp, a_bp, s)
    # 90-degree coupling: differentiate-ish via the quadrature (Hilbert) of the tank output
    sq90 = np.imag(signal.hilbert(sq))
    prod = s * sq90
    outs.append(np.mean(prod[N // 2:]))
outs = np.array(outs); outs /= np.max(np.abs(outs))
theory = np.sin(np.arctan(2 * Qq * devs / fif)); theory /= np.max(np.abs(theory))
print("  simulated quadrature-detector output (normalised) at -150/-75/0/+75/+150 kHz: " + ", ".join(f"{v:+.3f}" for v in outs)
      + "; theory " + ", ".join(f"{v:+.3f}" for v in theory))
check("quadrature detector: odd S-curve through zero at f0, monotone, matching theory within 0.15",
      abs(outs[2]) < 0.05 and np.all(np.diff(np.sign(devs) * 0 + outs) * np.sign(outs[-1] - outs[0]) > 0) and np.max(np.abs(np.abs(outs) - np.abs(theory))) < 0.15)
# Foster-Seeley / ratio detector with coupled tuned circuits (critical coupling kQ = 1)
xx = np.linspace(-4, 4, 801); kQ = 1.0
V2 = 1j * kQ / (1 + 1j * xx)          # secondary voltage relative to primary (normalised)
A = np.abs(1 + V2 / 2); B = np.abs(1 - V2 / 2)
fsd = A - B
ratio = (A - B) / (A + B)
zero = abs(np.interp(0, xx, fsd)) < 1e-12
pk = xx[np.argmax(fsd)]
print(f"  Foster-Seeley (kQ = 1): S-curve zero at f0 {zero}, peaks at 2Q df/f0 = {pk:+.2f}")
check("Foster-Seeley S-curve is odd with zero at the centre frequency", zero and np.allclose(fsd, -fsd[::-1], atol=1e-12))
# AM rejection: scale input amplitude by 1.2
fsd_am = 1.2 * A - 1.2 * B; ratio_am = (1.2 * A - 1.2 * B) / (1.2 * A + 1.2 * B)
print(f"  20 % AM on the input: Foster-Seeley output changes {np.max(np.abs(fsd_am - fsd))/np.max(np.abs(fsd))*100:.0f} % of full scale;"
      f" ratio detector {np.max(np.abs(ratio_am - ratio))*100:.1e} %")
check("ratio detector output is independent of input amplitude (AM rejection)", np.max(np.abs(ratio_am - ratio)) < 1e-12)
# PLL demodulator
fs = 1e6; t = np.arange(int(0.05 * fs)) / fs; fdev = 5e3; fm = 1e3; Kv = 10e3      # Hz/V
phi_in = (fdev / fm) * np.sin(2 * np.pi * fm * t)            # beta = df/fm
wn = 2 * np.pi * 20e3; zeta = 0.707
Kp = 2 * zeta * wn; Ki = wn ** 2
th = 0.0; integ = 0.0; vout = np.zeros_like(t); dt = 1 / fs
for k in range(len(t)):
    e = np.sin(phi_in[k] - th)
    integ += Ki * e * dt
    fr_rad = Kp * e + integ                      # rad/s
    th += fr_rad * dt
    vout[k] = fr_rad / (2 * np.pi) / Kv          # control voltage
seg = vout[len(t) // 2:]
amp_pll = (seg.max() - seg.min()) / 2
print(f"  PLL demod (BW ~20 kHz): recovered amplitude {amp_pll:.3f} V vs df/Kv = {fdev/Kv:.3f} V; THD {thd(seg-seg.mean(), fs, fm)*100:.2f} %")
check("PLL FM demodulator output = deviation / K_v within 3 %, THD < 1 %", abs(amp_pll / (fdev / Kv) - 1) < 0.03 and thd(seg - seg.mean(), fs, fm) < 0.01)

finish()
