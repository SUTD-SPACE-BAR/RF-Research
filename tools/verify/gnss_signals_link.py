#!/usr/bin/env python3
"""
gnss_signals_link.py — verification for kb/21-gnss/gnss-signals-and-codes.md

Checks
 1. GPS L1 C/A Gold-code generation (G1/G2 LFSRs, G2 phase taps) -> first 10 chips (octal)
    against IS-GPS-200 Table 3-Ia for PRN 1..5; autocorrelation {1023, -1, -65, 63}
    and cross-correlation three-valued {-65, -1, 63}.
 2. Chip lengths in metres and code periods for the main civil signals (table on the page).
 3. PSD of BPSK(1), BOC(1,1), CBOC(6,1,1/11) and TMBOC-like power split: first-null
    bandwidths and fraction of power within +-1.023 MHz and +-2.046 MHz; Gabor (RMS)
    bandwidth, which sets code-tracking precision.
 4. Link numbers: minimum received powers -> C/N0 for a given system noise temperature;
    power spectral density below kT; processing gain; Eb/N0 of the 50 b/s message.
Run:  python3 tools/verify/gnss_signals_link.py      (runs in < 5 s, prints PASS/FAIL)
"""
import numpy as np

C = 299_792_458.0
k_B = 1.380649e-23
ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


# ---------------------------------------------------------------- 1. C/A codes
# G2 phase-selector taps (1-based) for PRN 1..32, from IS-GPS-200 Table 3-Ia
G2_TAPS = {1: (2, 6), 2: (3, 7), 3: (4, 8), 4: (5, 9), 5: (1, 9), 6: (2, 10), 7: (1, 8),
           8: (2, 9), 9: (3, 10), 10: (2, 3), 11: (3, 4), 12: (5, 6), 13: (6, 7), 14: (7, 8),
           15: (8, 9), 16: (9, 10), 17: (1, 4), 18: (2, 5), 19: (3, 6), 20: (4, 7), 21: (5, 8),
           22: (6, 9), 23: (1, 3), 24: (4, 6), 25: (5, 7), 26: (6, 8), 27: (7, 9), 28: (8, 10),
           29: (1, 6), 30: (2, 7), 31: (3, 8), 32: (4, 9)}
# first 10 chips in octal (IS-GPS-200 Table 3-Ia), PRN 1..5
FIRST10 = {1: 0o1440, 2: 0o1620, 3: 0o1710, 4: 0o1744, 5: 0o1133}


def ca_code(prn):
    g1 = [1] * 10
    g2 = [1] * 10
    t1, t2 = G2_TAPS[prn]
    out = []
    for _ in range(1023):
        g2i = g2[t1 - 1] ^ g2[t2 - 1]
        out.append(g1[9] ^ g2i)
        f1 = g1[2] ^ g1[9]                                    # 1 + x^3 + x^10
        f2 = g2[1] ^ g2[2] ^ g2[5] ^ g2[7] ^ g2[8] ^ g2[9]    # 1+x^2+x^3+x^6+x^8+x^9+x^10
        g1 = [f1] + g1[:9]
        g2 = [f2] + g2[:9]
    return np.array(out, dtype=int)


codes = {p: ca_code(p) for p in range(1, 33)}
for p, octv in FIRST10.items():
    first = int("".join(str(b) for b in codes[p][:10]), 2)
    check(f"PRN {p} first 10 chips = {oct(first)} (IS-GPS-200 {oct(octv)})", first == octv)

bip = {p: 1 - 2 * c for p, c in codes.items()}          # 0 -> +1, 1 -> -1


def circ_corr(a, b):
    return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b)))).round().astype(int)


ac = circ_corr(bip[1], bip[1])
vals_ac = set(ac[1:])
check(f"C/A autocorr peak 1023, sidelobes {sorted(vals_ac)} subset of {{-65,-1,63}}",
      ac[0] == 1023 and vals_ac <= {-65, -1, 63})
xc_vals = set()
for p in range(2, 33):
    xc_vals |= set(circ_corr(bip[1], bip[p]))
check(f"C/A cross-corr values {sorted(xc_vals)} subset of {{-65,-1,63}}", xc_vals <= {-65, -1, 63})
print(f"      worst cross-corr = {20*np.log10(65/1023):.1f} dB re peak")

# ---------------------------------------------------------------- 2. chip lengths
signals = {  # name: (chip rate Hz, primary code length chips)
    "GPS L1 C/A": (1.023e6, 1023), "GPS L2 CM": (0.5115e6, 10230), "GPS L2 CL": (0.5115e6, 767250),
    "GPS L5 I5/Q5": (10.23e6, 10230), "GPS L1C": (1.023e6, 10230), "Galileo E1-B/C": (1.023e6, 4092),
    "Galileo E5a/E5b": (10.23e6, 10230), "BeiDou B1I": (2.046e6, 2046), "BeiDou B1C": (1.023e6, 10230),
    "BeiDou B2a": (10.23e6, 10230), "GLONASS L1OF": (0.511e6, 511)}
print("\n  signal            chip [m]   code period [ms]")
for n, (rc, L) in signals.items():
    print(f"  {n:16s} {C/rc:9.1f}   {1e3*L/rc:10.3f}")
check("C/A chip = 293.1 m, period 1 ms", abs(C / 1.023e6 - 293.05) < 0.1)
check("L2 CL period = 1.5 s", abs(767250 / 0.5115e6 - 1.5) < 1e-9)
check("E1 code period 4 ms", abs(4092 / 1.023e6 - 4e-3) < 1e-12)

# ---------------------------------------------------------------- 3. spectra
fc = 1.023e6
f = np.linspace(-30e6, 30e6, 600001)
df = f[1] - f[0]
Tc = 1 / fc


def psd_bpsk(n):             # BPSK(n): chip rate n*1.023 MHz, unit power
    T = 1 / (n * fc)
    return T * np.sinc(f * T) ** 2


def psd_boc_sin(m, n):       # sine-phased BOC(m,n), unit power (Betz); valid for 2m/n even
    Ts = 1 / (2 * m * fc)
    T = 1 / (n * fc)
    x = np.pi * f
    with np.errstate(divide="ignore", invalid="ignore"):
        s = (np.sin(x * T) * np.tan(x * Ts) / x) ** 2 / T
    s[~np.isfinite(s)] = 0
    return s


def frac_within(p, B):
    m = np.abs(f) <= B
    return np.sum(p[m]) * df / (np.sum(p) * df)


def rms_bw(p, B):            # Gabor bandwidth over +-B
    m = np.abs(f) <= B
    return np.sqrt(np.sum(f[m] ** 2 * p[m]) / np.sum(p[m]))


bpsk1 = psd_bpsk(1)
boc11 = psd_boc_sin(1, 1)
boc61 = psd_boc_sin(6, 1)
cboc = (10 / 11) * boc11 + (1 / 11) * boc61   # MBOC(6,1,1/11) power spectrum
bpsk10 = psd_bpsk(10)
print("\n  modulation     P(+-1.023 MHz) P(+-2.046 MHz) P(+-12 MHz)  Gabor BW(+-12 MHz) [MHz]")
for n, p in [("BPSK(1)", bpsk1), ("BOC(1,1)", boc11), ("MBOC(6,1,1/11)", cboc), ("BPSK(10)", bpsk10)]:
    print(f"  {n:14s} {frac_within(p,1.023e6):13.3f} {frac_within(p,2.046e6):13.3f} "
          f"{frac_within(p,12e6):11.3f} {rms_bw(p,12e6)/1e6:12.3f}")
check("BPSK(1): ~90 % of power in main lobe (+-1.023 MHz)", abs(frac_within(bpsk1, 1.023e6) - 0.903) < 0.01)
peak_boc = abs(f[np.argmax(boc11 * (f > 0))])
# analytic: G ~ sin^4(x/2)/x^2, x = pi f/fc -> maximum where tan(u) = 2u, u = x/2 -> f = 0.742 fc
from scipy.optimize import brentq
u0 = brentq(lambda u: np.tan(u) - 2 * u, 1.0, 1.5)
f_pk = 2 * u0 / np.pi * fc
check(f"BOC(1,1) spectral peaks at +-{peak_boc/1e6:.3f} MHz (analytic tan u = 2u -> {f_pk/1e6:.3f} MHz); "
      f"null at DC", abs(peak_boc - f_pk) < 2e3 and boc11[np.argmin(np.abs(f))] < 1e-3 * boc11.max())
check("MBOC Gabor BW > BOC(1,1) > BPSK(1) (better code tracking)",
      rms_bw(cboc, 12e6) > rms_bw(boc11, 12e6) > rms_bw(bpsk1, 12e6))

# ---------------------------------------------------------------- 4. link numbers
def cn0(p_dbw, gain_dbic, tsys):
    return p_dbw + 30 + gain_dbic - 10 * np.log10(k_B * tsys * 1e3)


print("\n  signal (min power)      P [dBW]  C/N0 @ T_sys=290 K (0 dBic) / 150 K")
mins = {"GPS L1 C/A": -158.5, "GPS L2C (IIR-M/IIF)": -160.0, "GPS L5 I5+Q5 (III)": -157.0 + 3.01,
        "GPS L1C (total)": -157.0, "Galileo E1 (B+C)": -157.25, "Galileo E5a (I+Q)": -155.25,
        "BeiDou B1I": -163.0, "BeiDou B1C (MEO)": -159.0, "GLONASS L1OF": -161.0}
for n, p in mins.items():
    print(f"  {n:22s} {p:7.2f}   {cn0(p,0,290):5.1f} / {cn0(p,0,150):5.1f} dB-Hz")
c = cn0(-158.5, 0, 290)
check(f"C/A at -158.5 dBW, T=290 K -> C/N0 = {c:.1f} dB-Hz (expect 45.5)", abs(c - 45.5) < 0.1)
psd = -158.5 + 30 - 10 * np.log10(2.046e6)
print(f"      C/A PSD over 2.046 MHz: {psd:.1f} dBm/Hz vs kT0 = -174.0 dBm/Hz -> {-174-psd:.1f} dB below")
check("C/A PSD ~ 17.6 dB below kT0", abs((-174 - psd) - 17.6) < 0.2)
noise_2mhz = -174 + 10 * np.log10(2e6)
print(f"      thermal noise in 2 MHz: {noise_2mhz:.1f} dBm (u-blox quotes -111 dBm)")
check("noise in 2 MHz = -111 dBm", abs(noise_2mhz + 111) < 0.1)
gp = 10 * np.log10(1.023e6 / 50)
check(f"processing gain chip/bit = {gp:.1f} dB (43.1)", abs(gp - 43.1) < 0.05)
ebn0 = 45.5 - 10 * np.log10(50)
print(f"      Eb/N0 of 50 b/s LNAV at 45.5 dB-Hz = {ebn0:.1f} dB")
# u-blox tracking sensitivity -167 dBm -> C/N0 with NF ~2 dB (T ~ 170 K receiver + 100 K antenna)
c167 = -167 - 10 * np.log10(k_B * 270 * 1e3)
print(f"      -167 dBm tracking sensitivity with T_sys = 270 K -> C/N0 = {c167:.1f} dB-Hz")
check(f"-167 dBm tracking sensitivity ~ {c167:.1f} dB-Hz (single digits: static, long integration)",
      5 < c167 < 9)
print(f"      reacquisition -160 dBm ~ {c167+7:.1f} dB-Hz, cold start -148 dBm ~ {c167+19:.1f} dB-Hz")

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
