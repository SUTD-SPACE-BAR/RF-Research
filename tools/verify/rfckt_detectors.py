#!/usr/bin/env python3
"""Verification for kb/06-rf-circuits/detectors-and-power-meters.md

 A. Diode detector theory: open-circuit output v^2/(4 n VT), ideal voltage sensitivity 1/(2(Is+Ib)); effect of
    junction capacitance / series resistance / video load (HSMS-285x SPICE values) vs data-sheet 40 mV/uW
 B. Square-law -> linear transition (large-signal solve of the half-wave detector)
 C. Tangential sensitivity estimate from video noise (TSS ~ -57 dBm data sheet)
 D. Log-amp transfer (AD8307: 25 mV/dB, -84 dBm intercept) for a 433 MHz 2 W TX monitor via a coupler
 E. Waveform dependence: RMS vs peak vs log-average detectors for CW, QPSK, 16-QAM, Gaussian noise
    (log-average of Rayleigh envelope reads 2.51 dB low)
 F. Temperature drift of a zero-bias detector and a matched-diode compensation
Run: python3 tools/verify/rfckt_detectors.py
"""
import numpy as np, sys
from scipy.optimize import brentq
from scipy.special import i0e

ok_all = True
kB, q = 1.380649e-23, 1.602176634e-19


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


T = 298.0
Is, n, Rs, Cj0 = 3e-6, 1.06, 25.0, 0.18e-12      # HSMS-285x SPICE
nVT = n * kB * T / q
Rj = nVT / Is
# ---------------------------------------------------------------- A. sensitivity
gamma_ideal = Rj / (2 * nVT)          # = 1/(2 Is)
print(f"A: HSMS-285x: nVT = {nVT*1e3:.2f} mV, Rj = {Rj/1e3:.2f} kohm (datasheet formula 8.33e-5 nT/Is = {8.33e-5*n*T/Is/1e3:.2f} kohm)")
print(f"   ideal voltage sensitivity (all available power into Rj, open-circuit video): {gamma_ideal/1e3:.0f} mV/uW (= 1/(2 Is))")
check("A1 gamma_ideal = 1/(2 Is)", abs(gamma_ideal - 1 / (2 * Is)) / gamma_ideal < 1e-12)
f = 915e6; w = 2 * np.pi * f
Zj = 1 / (1 / Rj + 1j * w * Cj0)
frac_j = Zj.real / (Zj.real + Rs)       # with a lossless conjugate match, power splits between Rs and Re(Zj)
RL, Rv = 100e3, Rj + Rs
load = RL / (RL + Rv)
g_est = gamma_ideal * frac_j * load
print(f"   at 915 MHz: Re(Zj) = {Zj.real:.0f} ohm, fraction of power reaching Rj = {frac_j:.2f}; video load 100k vs Rv "
      f"{Rv/1e3:.1f}k -> {load:.2f}; estimate {g_est/1e3:.0f} mV/uW vs data sheet 40 mV/uW (matching-network loss, package)")
check("A2 junction/series/video losses reduce the ideal sensitivity by ~25 %", 0.6 < frac_j * load < 0.85)
f2 = 2.45e9; Zj2 = 1 / (1 / Rj + 1j * 2 * np.pi * f2 * Cj0)
print(f"   at 2.45 GHz: fraction reaching Rj = {Zj2.real/(Zj2.real+Rs):.2f} (Cj shunts the junction; sensitivity falls with f)")

# ---------------------------------------------------------------- B. square-law -> linear
def vout(Vp, RL=100e3):
    # half-wave detector, diode in series, C to ground, RL: DC balance Is*(exp(-Vo/nVT)*I0(Vp/nVT) - 1) = Vo/RL
    def fbal(Vo):
        x = Vp / nVT
        return Is * (np.exp(-Vo / nVT + x) * i0e(x) - 1) - Vo / RL
    return brentq(fbal, 0, Vp + 1)
Rin = Rj * RL / (Rj + RL)          # small-signal: approximate input resistance for the power mapping
Rin = 2 * Rj                        # (half-wave detector input R ~ 2 Rj at small signal for open video) -> use for mapping only
print("B: detector output vs input power (voltage-driven, P = Vp^2 / (2 * 2Rj) mapping; indicative):")
Ps, Vos = [], []
for Pdbm in np.arange(-60, 11, 5):
    P = 1e-3 * 10 ** (Pdbm / 10)
    Vp = np.sqrt(2 * P * Rin)
    Vo = vout(Vp)
    Ps.append(Pdbm); Vos.append(Vo)
Vos = np.array(Vos); Ps = np.array(Ps)
slope = np.diff(20 * np.log10(Vos)) / np.diff(Ps)
for p, v, s_ in zip(Ps[1:], Vos[1:], slope):
    if p % 10 == 0:
        print(f"   {p:+4.0f} dBm: Vout {v*1e3:9.3f} mV, local slope {s_:.2f} (dB of Vout per dB of Pin; 2 = square law, 1 = linear)")
check("B1 square law (slope ~2 in 20log Vout) at low power, ~1 (linear) at high power", slope[0] > 1.9 and slope[-1] < 1.3)
trans = Ps[1:][np.argmin(abs(slope - 1.5))]
print(f"   square-law/linear transition (slope 1.5) near {trans:.0f} dBm with this mapping (data sheet: small-signal < -20 dBm)")

# ---------------------------------------------------------------- C. TSS estimate
Bv = 2e6
vn = np.sqrt(4 * kB * 290 * 8e3 * Bv)            # video resistance noise
for amp_nf in (0, 3):
    vt = 2.5 * vn * 10 ** (amp_nf / 20)           # TSS ~ 8 dB SNR at the video output
    Ptss = vt / 40e-3 * 1e-6                       # 40 mV/uW
    print(f"C: video noise {vn*1e6:.1f} uV rms in 2 MHz; TSS (8 dB video SNR, video-amp NF {amp_nf} dB) ~ {10*np.log10(Ptss*1e3):.1f} dBm "
          f"(data sheet -57 dBm)")
Ptss0 = 2.5 * vn / 40e-3 * 1e-6
check("C1 TSS estimate within 5 dB of the -57 dBm data-sheet value", abs(10 * np.log10(Ptss0 * 1e3) + 57) < 5)

# ---------------------------------------------------------------- D. log amp
def ad8307(Pdbm):
    return 0.025 * (Pdbm + 84)
for P, lab in ((33 - 40, "+33 dBm TX via 40 dB coupler"), (-75, "bottom of range"), (17, "top of range")):
    print(f"D: AD8307 at {P:+.0f} dBm ({lab}): Vout = {ad8307(P):.3f} V")
check("D1 +33 dBm through a 40 dB coupler lands mid-range of a -75..+17 dBm log amp", -75 < -7 < 17)
print(f"   resolution with a 10-bit 3.3 V ADC: {3.3/1024/0.025:.2f} dB per LSB")

# ---------------------------------------------------------------- E. waveform dependence
rng = np.random.default_rng(11)
N = 400000
sigs = {}
t = np.arange(N)
sigs['CW'] = np.exp(1j * 2 * np.pi * 0.01 * t)
sym = rng.integers(0, 4, N // 20)
qpsk = np.exp(1j * (np.pi / 4 + np.pi / 2 * sym))
def shape(s, sps=20, beta=0.35):
    up = np.zeros(len(s) * sps, complex); up[::sps] = s
    tt = np.arange(-8 * sps, 8 * sps + 1) / sps
    h = np.sinc(tt) * np.cos(np.pi * beta * tt) / (1 - (2 * beta * tt) ** 2 + 1e-12)
    return np.convolve(up, h, 'same')
sigs['QPSK RC0.35'] = shape(qpsk)
q16 = ((rng.integers(0, 4, N // 20) * 2 - 3) + 1j * (rng.integers(0, 4, N // 20) * 2 - 3))
sigs['16QAM RC0.35'] = shape(q16)
sigs['Gaussian noise'] = rng.normal(size=N) + 1j * rng.normal(size=N)
print("E: detector reading relative to true RMS (same average power):   peak       log-average")
for k, s in sigs.items():
    s = s / np.sqrt(np.mean(abs(s) ** 2))
    pk = 20 * np.log10(np.max(abs(s)))
    logavg = np.mean(20 * np.log10(abs(s) + 1e-12))
    print(f"   {k:16s}                                     {pk:+6.2f} dB   {logavg:+6.2f} dB")
    if k == 'Gaussian noise':
        e_log = logavg
check("E1 log-average of a Rayleigh envelope reads 2.51 dB (Euler-gamma x 10/ln10) below RMS", abs(e_log + 0.5772 * 10 / np.log(10)) < 0.05)

# ---------------------------------------------------------------- F. temperature drift and compensation
# thermionic model Is(T) ~ T^2 exp(-q phiB / kT) with an assumed low barrier phiB = 0.25 eV (zero-bias Schottky);
# sensitivity with a finite video load: gamma = (1/(2 Is)) * RL/(RL + Rj)
phiB = 0.25
def Is_T(Tk):
    return Is * (Tk / T) ** 2 * np.exp(-q * phiB / kB * (1 / Tk - 1 / T))
g25 = None
out = []
for Tc in (-20, 0, 25, 50, 85):
    Tk = Tc + 273.15
    isT = Is_T(Tk); rj = n * kB * Tk / q / isT
    g = 1 / (2 * isT) * 100e3 / (100e3 + rj)
    out.append((Tc, isT, rj, g))
g25 = [o for o in out if o[0] == 25][0][3]
for Tc, isT, rj, g in out:
    print(f"F: {Tc:+4d} C: Is {isT*1e6:6.2f} uA, Rj {rj/1e3:6.1f} kohm, sensitivity (100k video load) "
          f"{g/1e3:6.0f} mV/uW ({20*np.log10(g/g25):+5.1f} dB)")
d_ln = 2 / T + q * phiB / (kB * T ** 2)
print(f"   Is doubles every {np.log(2)/d_ln:.0f} C (phiB 0.25 eV assumed) -> a bare zero-bias detector drifts several dB over "
      f"temperature; use a matched reference diode (HSMS-2852 pair, dVF <= 15 mV) for the DC offset, temperature-"
      f"calibrate the gain, or use log/RMS ICs specified to +-0.5..1 dB")
span = 20 * np.log10(max(o[3] for o in out) / min(o[3] for o in out))
check("F1 zero-bias detector sensitivity varies by several dB from -20 to +85 C in the model", span > 3)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
sys.exit(0 if ok_all else 1)
