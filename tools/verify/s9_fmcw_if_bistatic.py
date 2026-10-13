#!/usr/bin/env python3
"""W5-S9 checks for kb/11-radar/fmcw-radar.md section
"Choosing a waveform: pulsed vs FMCW, real vs complex IF, bistatic FMCW".

Run:  python3 tools/verify/s9_fmcw_if_bistatic.py   (~3 s)

1. Real vs complex (I/Q) IF: Monte Carlo of the image-noise penalty (3.01 dB when RF noise dominates)
   and the reduced advantage when IF-stage noise is significant: advantage = 2(1+r)/(1+2r).
2. I/Q imbalance: image-rejection ratio formula vs simulation (ghost target at -f_b).
3. Real IF keeps the velocity sign in fast-chirp FMCW (complex range-FFT bin -> Doppler FFT).
4. Pulsed vs FMCW at equal peak power: energy per CPI, SNR, blind range, ADC rate (decision-table numbers).
5. Bistatic FMCW: range-sum bias from oscillator offset c*df/S and timing offset c*dt; recovery by
   direct-path referencing; loss of range correlation of phase noise; bistatic resolution c/(2B cos(beta/2)).
"""
import numpy as np

c = 299_792_458.0
kT0_dbm = -173.98
rng = np.random.default_rng(9)
ok_all = True
db = lambda x: 10 * np.log10(x)


def check(name, got, want, tol):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.4g}, expected {want:.4g} (tol {tol})")


print("=" * 78)
print("1. Real vs complex IF: image-band noise fold-back")
N, trials, A, sigma = 256, 4000, 1.0, 4.0
fb_bin = 37
t = np.arange(N)
s = A * np.exp(2j * np.pi * fb_bin * t / N)      # dechirped echo: one-sided (positive) beat only


def snr_bins(r):
    """r = IF-stage noise power relative to the RF noise power seen at a real IF output."""
    sr, sc = [], []
    for _ in range(trials // 8):
        n = sigma / np.sqrt(2) * (rng.standard_normal((8, N)) + 1j * rng.standard_normal((8, N)))
        x = s + n                                   # complex envelope at RF, referred to the LO
        sw = np.sqrt(r * sigma**2 / 2)
        # real mixer: Re{x} plus IF noise
        y = x.real + sw * rng.standard_normal((8, N))
        # quadrature mixer: RF split in two (1/sqrt2 each), each path adds the same IF noise
        z = x / np.sqrt(2) + sw * (rng.standard_normal((8, N)) + 1j * rng.standard_normal((8, N)))
        Y, Z = np.fft.fft(y, axis=1), np.fft.fft(z, axis=1)
        sr.append((np.abs(Y[:, fb_bin]) ** 2, np.mean(np.abs(Y[:, 60:120]) ** 2, axis=1)))
        sc.append((np.abs(Z[:, fb_bin]) ** 2, np.mean(np.abs(Z[:, 60:120]) ** 2, axis=1)))
    pr = np.mean([a for a, _ in sr]); nr = np.mean([b for _, b in sr])
    pc = np.mean([a for a, _ in sc]); nc = np.mean([b for _, b in sc])
    # (signal+noise) bin minus noise -> signal power
    return db((pr - nr) / nr), db((pc - nc) / nc)


for r in (0.0, 0.25, 1.0, 4.0):
    s_r, s_c = snr_bins(r)
    theory = db(2 * (1 + r) / (1 + 2 * r))
    print(f"    IF/RF noise ratio r = {r:4.2f}: real {s_r:6.2f} dB, complex {s_c:6.2f} dB, advantage {s_c - s_r:5.2f} dB (theory {theory:5.2f})")
    check(f"complex-IF advantage r={r}", s_c - s_r, theory, 0.25)

print("=" * 78)
print("2. I/Q gain/phase imbalance -> image ghost at -f_b")


def irr_db(eps_db, phi_deg):
    g = 10 ** (eps_db / 20); p = np.radians(phi_deg)
    return db((1 + 2 * g * np.cos(p) + g**2) / (1 - 2 * g * np.cos(p) + g**2))


for eps, ph in ((0.1, 1.0), (0.5, 5.0), (1.0, 10.0)):
    g = 10 ** (eps / 20); p = np.radians(ph)
    x = np.exp(2j * np.pi * fb_bin * t / N)
    z = x.real + 1j * g * (np.sin(2 * np.pi * fb_bin * t / N + p))  # Q path with gain/phase error
    Z = np.fft.fft(z)
    sim = db(np.abs(Z[fb_bin]) ** 2 / np.abs(Z[-fb_bin]) ** 2)
    print(f"    {eps} dB / {ph} deg: IRR formula {irr_db(eps, ph):5.1f} dB, simulated {sim:5.1f} dB")
    check(f"IRR {eps} dB/{ph} deg", sim, irr_db(eps, ph), 0.05)

print("=" * 78)
print("3. Real IF still gives the velocity sign in a fast-chirp radar")
fc, B, Tc, Ns, Nch = 77e9, 300e6, 30e-6, 256, 64
lam = c / fc; S = B / Tc; fs = Ns / Tc
R0 = 20.0
for v in (+5.0, -5.0):                      # + = receding (range increasing)
    cube = np.zeros((Nch, Ns))
    tt = np.arange(Ns) / fs
    for m in range(Nch):
        R = R0 + v * m * Tc
        tau = 2 * R / c
        cube[m] = np.cos(2 * np.pi * (S * tau * tt + fc * tau))   # real IF, TX x RX product phase
    rf = np.fft.fft(cube, axis=1)[:, : Ns // 2]
    k = np.argmax(np.abs(rf[0]))
    dop = np.fft.fftshift(np.fft.fft(rf[:, k]))
    vbins = np.fft.fftshift(np.fft.fftfreq(Nch, Tc)) * lam / 2
    vest = vbins[np.argmax(np.abs(dop))]
    print(f"    true v = {v:+.1f} m/s (receding +): Doppler-FFT peak at {vest:+.2f} m/s")
    check(f"velocity sign real IF v={v}", np.sign(vest), np.sign(v), 0)

print("=" * 78)
print("4. Pulsed vs FMCW at the same 100 mW peak (5.8 GHz, 0.01 m^2 drone at 1 km)")
f = 5.8e9; lam = c / f; Pt = 0.1; G = 10 ** (20 / 10); sig = 0.01; R = 1000.0
NF, L, T_cpi = 6.0, 6.0, 10e-3
Pr = Pt * G**2 * lam**2 * sig / ((4 * np.pi) ** 3 * R**4)
for name, duty in (("pulsed 1 us, PRF 10 kHz (1 % duty)", 0.01), ("FMCW (100 % duty)", 1.0)):
    E = Pr * duty * T_cpi
    EN0 = db(E) + 30 - (kT0_dbm + NF) - L
    print(f"    {name:36s}: E/N0 over {T_cpi*1e3:.0f} ms = {EN0:6.1f} dB (need 13.2 dB for Pd 0.9 / Pfa 1e-6)")
    if duty == 1.0:
        en_fmcw = EN0
    else:
        en_pul = EN0
check("FMCW minus pulsed E/N0 = -10log(duty)", en_fmcw - en_pul, 20.0, 1e-9)
Tneed = T_cpi * 10 ** ((13.2 - en_fmcw) / 10)
print(f"    FMCW needs a {Tneed*1e3:.0f} ms coherent dwell for 13.2 dB; the 1 % pulsed radar would need {Tneed*100:.1f} s (or 100x peak power)")
check("FMCW dwell for 13.2 dB (ms)", Tneed * 1e3, 97.7, 1.0)
print(f"    blind range of a 1 us pulse c*tau/2 = {c*1e-6/2:.0f} m; of a 10 us coded pulse = {c*10e-6/2:.0f} m")
print(f"    ADC: pulsed B = 150 MHz (1 m) needs >= 150 MS/s complex; FMCW 150 MHz in 1 ms to 1.5 km: f_b = {2*(150e6/1e-3)*1500/c/1e6:.2f} MHz")
check("FMCW beat at 1.5 km (MHz)", 2 * (150e6 / 1e-3) * 1500 / c / 1e6, 1.50, 0.01)
leak = 20 - 60                                   # 100 mW (20 dBm), 60 dB isolation
print(f"    FMCW leakage with 60 dB isolation: {leak} dBm vs echo {db(Pr)+30:.1f} dBm -> {leak-(db(Pr)+30):.0f} dB dynamic range needed at the IF")

print("=" * 78)
print("5. Bistatic FMCW")
for fc_, ppm, S_, lab in ((24.125e9, 1.0, 250e6 / 1e-3, "24 GHz slow ramp 250 MHz/1 ms"),
                          (24.125e9, 1.0, 10e12, "24 GHz fast chirp 10 MHz/us"),
                          (77e9, 0.1, 30e12, "77 GHz, 0.1 ppm GPSDO-class, 30 MHz/us")):
    df = fc_ * ppm * 1e-6
    print(f"    {lab:42s}: df = {df/1e3:7.2f} kHz -> range-sum bias c*df/S = {c*df/S_:8.2f} m")
check("24 GHz 1 ppm slow ramp bias (m)", c * 24.125e3 / 2.5e11, 28.93, 0.01)
print(f"    chirp-start timing offset 1 us -> range-sum bias c*dt = {c*1e-6:.0f} m; 10 ns -> {c*10e-9:.2f} m")
# direct-path referencing simulation
fs, Tch, B_ = 2e6, 1e-3, 250e6
S_ = B_ / Tch; tt = np.arange(int(fs * Tch)) / fs
Lb, Rsum, df, dt = 30.0, 110.0, 24e3, 0.37e-6   # baseline, target range sum, osc offset, timing offset
beat = lambda path: np.exp(2j * np.pi * ((S_ * (path / c + dt) + df) * tt))
x = beat(Lb) + 0.1 * beat(Rsum)
X = np.abs(np.fft.fft(x, 1 << 20)); fr = np.fft.fftfreq(1 << 20, 1 / fs)
pk = sorted(fr[np.argsort(X)[-1:]].tolist())
# find two peaks: strongest = direct, second away from it
idx = np.argsort(X)[::-1]; f1 = fr[idx[0]]
f2 = next(fr[i] for i in idx if abs(fr[i] - f1) > 20e3)
naive = f2 * c / S_
ref = Lb + (f2 - f1) * c / S_
print(f"    simulated: target range sum {Rsum} m, baseline {Lb} m, df 24 kHz, dt 0.37 us")
print(f"      naive (no reference) range sum {naive:7.2f} m; direct-path referenced {ref:7.2f} m")
check("direct-path-referenced range sum (m)", ref, Rsum, 0.3)
for tau_ns in (2, 10, 100, 300):
    tau = tau_ns * 1e-9
    corr = db(4 * np.sin(np.pi * 1e6 * tau) ** 2)
    print(f"    phase noise at 1 MHz offset, monostatic delay {tau_ns:5d} ns: 4sin^2(pi f tau) = {corr:6.1f} dB; bistatic, two free oscillators: +3.0 dB (sum of both)")
for beta in (0, 60, 90, 120):
    print(f"    bistatic angle {beta:3d} deg: range resolution c/(2B cos(b/2)) at B = 250 MHz = {c/(2*250e6*np.cos(np.radians(beta/2))):.2f} m")
check("bistatic 90 deg resolution (m)", c / (2 * 250e6 * np.cos(np.radians(45))), 0.848, 0.002)

print("=" * 78)
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
