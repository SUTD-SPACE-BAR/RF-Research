#!/usr/bin/env python3
"""Leeson prefactor check: FkT/(2Ps), not 2FkT/Ps.  (W5-E9, 2026-10-02; fixes D6 issue #1 in
kb/05-analog-electronics/oscillators.md)

  1. Monte Carlo, real passband: carrier A cos(w0 t) plus white Gaussian noise with one-sided PSD N0 (W/Hz,
     1-ohm normalisation, Ps = A^2/2). Extract phase and amplitude with the analytic signal and estimate their
     one-sided PSDs with Welch. Expect S_phi = N0/Ps (rad^2/Hz), the fractional-AM PSD also N0/Ps (the additive
     noise splits equally into AM and PM), and L = S_phi/2 = N0/(2 Ps) (IEEE Std 1139 definition).
  2. With N0 = F k T0 (T0 = 290 K), F = 1, Ps = 1 mW: L_floor = -177.0 dBc/Hz.  The old 05 form 2FkT/Ps gives
     -171.0 dBc/Hz, i.e. 6.02 dB high (that form is Lee & Hajimiri's, with Psig = power dissipated in the tank).
  3. Recompute the 05/oscillators.md examples with FkT0/(2Ps) (433 MHz LC VCO QL = 20 and 40; 32 MHz crystal).
Run: python3 tools/verify/fix_leeson_prefactor.py  -> ALL PASS
"""
import numpy as np
from scipy import signal

k = 1.380649e-23
T0 = 290.0
rng = np.random.default_rng(1)
ok = True


def check(name, cond):
    global ok
    ok &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


print("=== 1. Monte Carlo: additive white noise -> phase and amplitude PSDs ===")
fs = 1.0                  # normalised sample rate
f0 = fs / 4               # carrier at fs/4 so offsets up to fs/4 are clean
N = 2**22
A = 1.0
Ps = A**2 / 2
N0 = 1e-6                 # one-sided PSD of the additive noise, W/Hz (1 ohm)
t = np.arange(N) / fs
x = A * np.cos(2 * np.pi * f0 * t) + rng.normal(0, np.sqrt(N0 * fs / 2), N)
z = signal.hilbert(x) * np.exp(-2j * np.pi * f0 * t)
phi = np.unwrap(np.angle(z))
amp = np.abs(z) / A - 1
f, Sphi = signal.welch(phi, fs=fs, nperseg=2**14, return_onesided=True, detrend="constant")
_, Sa = signal.welch(amp, fs=fs, nperseg=2**14, return_onesided=True, detrend="constant")
band = (f > 0.02 * fs) & (f < 0.2 * fs)
Sphi_m, Sa_m = Sphi[band].mean(), Sa[band].mean()
print(f"S_phi measured {Sphi_m:.4e} rad^2/Hz; N0/Ps = {N0/Ps:.4e}; ratio {Sphi_m/(N0/Ps):.4f}")
print(f"S_AM  measured {Sa_m:.4e} 1/Hz;     N0/Ps = {N0/Ps:.4e}; ratio {Sa_m/(N0/Ps):.4f}")
check("S_phi = N0/Ps within 2 %", abs(Sphi_m / (N0 / Ps) - 1) < 0.02)
check("AM and PM get equal halves (S_AM = S_phi within 2 %)", abs(Sa_m / Sphi_m - 1) < 0.02)
Lmc = 10 * np.log10(Sphi_m / 2)
print(f"L = S_phi/2 = {Lmc:.2f} dBc/Hz vs 10log(N0/(2Ps)) = {10*np.log10(N0/(2*Ps)):.2f}; 10log(2N0/Ps) = {10*np.log10(2*N0/Ps):.2f}")
check("L = N0/(2Ps) within 0.1 dB", abs(Lmc - 10 * np.log10(N0 / (2 * Ps))) < 0.1)

print("\n=== 2. White phase floor at F = 1, Ps = 0 dBm, T0 = 290 K ===")
Lnew = 10 * np.log10(k * T0 / (2 * 1e-3))
Lold = 10 * np.log10(2 * k * T0 / 1e-3)
print(f"FkT0/(2Ps) = {Lnew:.2f} dBc/Hz ; 2FkT0/Ps = {Lold:.2f} dBc/Hz ; difference {Lold-Lnew:.2f} dB")
check("floor = -177.0 dBc/Hz", abs(Lnew + 177.0) < 0.05)
check("old form is 6.02 dB high", abs(Lold - Lnew - 10 * np.log10(4)) < 1e-9)


print("\n=== 3. 05/oscillators.md examples with FkT0/(2Ps) ===")
def leeson(df, f0, QL, Ps, F, fc):
    return 10 * np.log10((F * k * T0 / (2 * Ps)) * (1 + (f0 / (2 * QL * df))**2) * (1 + fc / df))


cases = {
    "433 MHz LC VCO, QL 20, 0 dBm, F 2, fc 10 kHz": (433e6, 20, 1e-3, 2, 10e3, {1e4: -110.3, 1e5: -132.9, 1e6: -153.2}),
    "433 MHz LC VCO, QL 40": (433e6, 40, 1e-3, 2, 10e3, {1e4: -116.3, 1e5: -138.9, 1e6: -159.1}),
    "32 MHz crystal, QL 5e4, -10 dBm, F 2, fc 1 kHz": (32e6, 5e4, 1e-4, 2, 1e3, {1e3: -160.5, 1e8: -164.0}),
}
for name, (f0_, QL, Ps_, F, fc, expect) in cases.items():
    got = {df: leeson(df, f0_, QL, Ps_, F, fc) for df in expect}
    print(name + ": " + ", ".join(f"{df/1e3:g} kHz {v:.1f}" for df, v in got.items()))
    check(f"{name} matches page values (±0.1 dB)", all(abs(got[df] - v) < 0.1 for df, v in expect.items()))

print("\nALL PASS" if ok else "\nSOME CHECKS FAILED")
