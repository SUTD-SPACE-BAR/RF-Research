#!/usr/bin/env python3
"""
prop_doppler_fading.py — verification for kb/09-propagation-link-budget/multipath-fading-doppler.md

1. Doppler shift f_d = f v_r / c for a rocket (Mach 1-5) at 433 / 915 / 1575.42 MHz, vs LoRa's static
   offset tolerance (+-25 % of BW, SX126x datasheet) and crystal error.
2. Doppler RATE df/dt = f a_r / c during boost vs the SX126x drift limit over a packet:
   Freq_drift_max = BW/(3 * 2^SF) (LDRO off), 16x that with LowDataRateOptimize on.
3. Rayleigh and Rician fading: outage P(SNR < threshold) vs fade margin, analytic
   (Rayleigh 1 - exp(-1/M); Rician via Marcum Q = noncentral chi-square) and Monte-Carlo check.
4. Level-crossing rate and average fade duration for Clarke/Jakes Rayleigh fading.
5. Coherence time (0.423/f_d) and coherence bandwidth (1/(5 sigma_tau), 1/(50 sigma_tau)).
6. Selection / maximal-ratio diversity outage in Rayleigh fading (M branches).
"""
import numpy as np
from scipy import stats, special
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from noise_sensitivity import lora_toa

c = 299792458.0
a_sound = 343.0   # m/s at sea level, 20 C (lower aloft: ~295 m/s at 11 km)

print("=== 1. Doppler shift ===")
for M in (1, 2, 3, 5):
    v = M*a_sound
    row = [f*v/c for f in (433.125e6, 915e6, 1575.42e6)]
    print(f"  Mach {M} ({v:6.0f} m/s radial): f_d = {row[0]:7.0f} Hz @433, {row[1]:7.0f} Hz @915, {row[2]:7.0f} Hz @L1")
for BW in (62.5e3, 125e3, 250e3, 500e3):
    print(f"  LoRa static offset tolerance +-25% BW = +-{0.25*BW/1e3:.1f} kHz at BW {BW/1e3} kHz")
for ppm in (2.0, 10.0, 20.0):
    print(f"  crystal error {ppm:4.1f} ppm at 433 MHz = {433.125e6*ppm*1e-6/1e3:.2f} kHz; at 915 MHz = {915e6*ppm*1e-6/1e3:.2f} kHz "
          f"(Tx+Rx errors add)")

print("\n=== 2. Doppler rate during boost vs SX126x drift limit ===")
print("  Freq_drift_max = BW/(3 * 2^SF) over the whole packet (x16 with LDRO). 30-byte payload, CR 4/5, 8-symbol preamble.")
for f in (433.125e6, 915e6):
    for acc_g in (5.0, 10.0, 20.0, 50.0):
        rate = f*acc_g*9.80665/c
        out = []
        for SF, BW in ((7, 125e3), (9, 125e3), (10, 125e3), (11, 125e3), (12, 125e3), (11, 250e3), (12, 250e3)):
            Ts = 2**SF/BW
            ldro = Ts > 16e-3
            toa = lora_toa(30, SF, BW, ldro=ldro)
            drift = rate*toa
            lim = BW/(3*2**SF)*(16 if ldro else 1)
            out.append(f"SF{SF}/{int(BW/1e3)}k:{drift:6.0f}/{lim:5.0f}{'!' if drift > lim else ' '}")
        print(f"  {f/1e6:6.1f} MHz, {acc_g:4.0f} g radial -> {rate:6.0f} Hz/s | drift/limit (Hz): " + " ".join(out))
print("  '!' = drift over the packet exceeds the datasheet limit (expect sensitivity loss / CRC failures)")
# LDRO forced on for SF10 (optional in the chip)
f = 433.125e6; rate = f*10*9.80665/c
toa = lora_toa(30, 10, 125e3, ldro=True)
print(f"  SF10/125k with LDRO forced ON: ToA {toa*1e3:.0f} ms, drift {rate*toa:.0f} Hz vs limit {125e3/(3*1024)*16:.0f} Hz")

print("\n=== 3. Outage vs fade margin ===")
rng = np.random.default_rng(7)
def rician_outage(K, margin_db):
    """P(|h|^2 < 1/M) with E|h|^2 = 1, Rician K (linear). CDF via noncentral chi-square (2 dof)."""
    M = 10**(margin_db/10)
    x = 1.0/M
    # |h|^2 = (s^2 + ...)/... : 2(K+1)|h|^2 ~ ncx2(df=2, nc=2K)
    return stats.ncx2.cdf(2*(K + 1)*x, df=2, nc=2*K) if K > 0 else 1 - np.exp(-x)
print("  margin(dB)  Rayleigh(analytic)  Rayleigh(MC)  Rician K=3 dB  K=6 dB  K=10 dB  K=15 dB")
N = 2_000_000
h_ray = (rng.standard_normal(N) + 1j*rng.standard_normal(N))/np.sqrt(2)
for m in (0, 5, 10, 15, 20, 30):
    Mlin = 10**(m/10)
    pa = 1 - np.exp(-1/Mlin)
    pmc = np.mean(np.abs(h_ray)**2 < 1/Mlin)
    rs = [rician_outage(10**(K/10), m) for K in (3, 6, 10, 15)]
    print(f"  {m:6d}      {pa:10.2e}        {pmc:10.2e}   " + "  ".join(f"{r:8.2e}" for r in rs))
# MC check of Rician
K = 10**(6/10)
los = np.sqrt(K/(K+1)); sc = np.sqrt(1/(K+1))
h = los + sc*(rng.standard_normal(N) + 1j*rng.standard_normal(N))/np.sqrt(2)
print(f"  Rician K=6 dB, margin 10 dB: analytic {rician_outage(K, 10):.3e}, MC {np.mean(np.abs(h)**2 < 0.1):.3e}")
print("  Rule: Rayleigh needs ~10 dB per decade of outage (1% -> 20 dB, 0.1% -> 30 dB).")

print("\n=== 4. Level crossing rate and average fade duration (Rayleigh, Clarke) ===")
for fd in (1.0, 10.0, 100.0):
    for m in (10.0, 20.0):
        rho = 10**(-m/20)
        lcr = np.sqrt(2*np.pi)*fd*rho*np.exp(-rho**2)
        afd = (np.exp(rho**2) - 1)/(rho*fd*np.sqrt(2*np.pi))
        print(f"  f_d={fd:6.1f} Hz, threshold {m:.0f} dB below rms: LCR={lcr:8.3f} /s, AFD={afd*1e3:8.2f} ms")

print("\n=== 5. Coherence time and bandwidth ===")
for fd in (1.0, 50.0, 1500.0):
    print(f"  f_d={fd:7.1f} Hz: Tc(0.423/f_d)={0.423/fd*1e3:8.2f} ms; (9/(16 pi f_d))={9/(16*np.pi*fd)*1e3:8.2f} ms")
for st in (50e-9, 200e-9, 1e-6, 5e-6):
    print(f"  sigma_tau={st*1e9:6.0f} ns: Bc(50% corr ~1/(5 s))={1/(5*st)/1e3:8.1f} kHz; Bc(90% ~1/(50 s))={1/(50*st)/1e3:8.1f} kHz")

print("\n=== 6. Diversity in Rayleigh fading ===")
for M in (1, 2, 3, 4):
    for m in (10.0, 20.0):
        g = 10**(-m/10)
        sel = (1 - np.exp(-g))**M
        mrc = special.gammainc(M, g)          # P(sum of M unit-mean exponentials < g)
        print(f"  M={M}, margin {m:.0f} dB: selection outage {sel:.2e}, MRC outage {mrc:.2e}")
# margin needed for 1e-3 outage
for M in (1, 2, 4):
    g = -np.log(1 - 1e-3**(1/M))
    print(f"  M={M}: margin for 0.1 % outage (selection) = {-10*np.log10(g):.1f} dB")
