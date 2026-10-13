"""W5-S18b: checks every number quoted in the "Level 1½" rungs added by the S18b quality pass
(the pages S18 deferred because other slices owned them).
Run: python3 tools/verify/s18b_level15_numbers.py   (prints each value; ALL PASS at the end)."""
import numpy as np
from scipy.special import erfc

c = 299792458.0
g = 9.80665
k_dBm = 10 * np.log10(1.380649e-23 * 1e3)   # dBm/Hz/K
ok = True


def chk(name, val, ref, tol):
    global ok
    good = abs(val - ref) <= tol
    ok &= good
    print(f"{'PASS' if good else 'FAIL'}  {name}: {val:.6g} (page {ref})")


def Q(x):
    return 0.5 * erfc(x / np.sqrt(2))


# ---- 10/synchronization-carrier-timing: 433.92 MHz, 9600 baud, crystals at each end
T = 1 / 9600
df10 = 2 * 10e-6 * 433.92e6
chk("sync 2x10 ppm offset kHz", df10 / 1e3, 8.68, 0.005)
chk("sync rotation per symbol deg (10 ppm)", 360 * df10 * T, 325, 0.5)
df2 = 2 * 2e-6 * 433.92e6
chk("sync 2x2 ppm offset kHz", df2 / 1e3, 1.74, 0.005)
chk("sync rotation per symbol deg (2 ppm)", 360 * df2 * T, 65, 0.5)
chk("sync correlation loss dB (2 ppm)", -20 * np.log10(np.sinc(df2 * T)), 0.47, 0.005)
chk("sync symbols to slip one symbol at 100 ppm", 1 / 100e-6, 10000, 1e-6)

# ---- 10/matched-filter-detection: 16 samples, per-sample SNR -6 dB (A = 1, sigma = 2)
A, sig, N = 1.0, 2.0, 16
chk("MF per-sample SNR dB", 10 * np.log10(A**2 / sig**2), -6.02, 0.01)
snr_out = (N * A) ** 2 / (N * sig**2)
chk("MF output SNR (linear)", snr_out, 4.0, 1e-12)
chk("MF output SNR dB", 10 * np.log10(snr_out), 6.02, 0.01)
chk("MF gain dB = 10 log N", 10 * np.log10(N), 12.04, 0.01)
snr_long = (N * A) ** 2 / (2 * N * sig**2)          # window twice the pulse length
chk("MF window 2x pulse loss dB", 10 * np.log10(snr_out / snr_long), 3.01, 0.01)
# discrete identity: N A^2 / sigma^2 = 2E/N0 with E = N A^2/fs and sigma^2 = (N0/2) fs
fs = 1e6; N0 = 2 * sig**2 / fs; E = N * A**2 / fs
chk("MF identity N A^2/sigma^2 = 2E/N0", 2 * E / N0, snr_out, 1e-12)
# Monte Carlo of the correlator
rng = np.random.default_rng(1)
trials = 200000
noise = rng.normal(0, sig, (trials, N)).sum(axis=1)
chk("MF Monte Carlo output SNR", (N * A) ** 2 / noise.var(), 4.0, 0.05)

# ---- 10/ber-ebn0-and-shannon: -120 dBm, NF 6 dB, 9600 b/s BPSK
N0d = -174 + 6
cn0 = -120 - N0d
chk("BER C/N0 dB-Hz", cn0, 48.0, 1e-9)
ebn0 = cn0 - 10 * np.log10(9600)
chk("BER Eb/N0 dB", ebn0, 8.18, 0.005)
chk("BER BPSK Pb", Q(np.sqrt(2 * 10 ** (ebn0 / 10))) * 1e4, 1.44, 0.01)   # x 1e-4
chk("BER Eb/N0 for 1e-5 dB (Q(4.265))", 10 * np.log10(4.265**2 / 2), 9.59, 0.005)
chk("BER required C/N0 for 1e-5 at 9600 b/s", 10 * np.log10(4.265**2 / 2) + 10 * np.log10(9600), 49.4, 0.02)

# ---- 10/digital-modulation-psk-qam-fsk: 9600 b/s QPSK, rate 1/2, RRC 0.35; GFSK h 0.5
Rs = 9600 / (2 * 0.5)
chk("DM QPSK r=1/2 symbol rate baud", Rs, 9600, 1e-9)
chk("DM RRC bandwidth kHz", 1.35 * Rs / 1e3, 12.96, 1e-9)
chk("DM spectral efficiency b/s/Hz", 9600 / (1.35 * Rs), 0.74, 0.001)
chk("DM GFSK Carson kHz", 9600 * 1.5 / 1e3, 14.4, 1e-9)
t = np.linspace(0, 2 * np.pi, 360001)
s = 1 * np.cos(t) - (-1) * np.sin(t)          # I = +1, Q = -1
chk("DM IQ amplitude", s.max(), np.sqrt(2), 1e-6)
chk("DM IQ phase of peak deg (cos(wt-45))", np.degrees(t[s.argmax()]), 45.0, 0.01)

# ---- 21/gnss-signals-and-codes
chip = c / 1.023e6
chk("GNSS C/A chip m", chip, 293.1, 0.05)
chk("GNSS code period km", chip * 1023 / 1e3, 299.8, 0.05)
chk("GNSS code phase 512.3 chips km", 512.3 * chip / 1e3, 150.1, 0.05)
chk("GNSS processing gain per period dB", 10 * np.log10(1023), 30.1, 0.01)
chk("GNSS SNR in 2.046 MHz at 45 dB-Hz", 45 - 10 * np.log10(2.046e6), -18.1, 0.01)
chk("GNSS SNR after 1 ms coherent", 45 - 10 * np.log10(1e3), 15.0, 1e-9)
lam = c / 1575.42e6
rs, re = 26560e3, 6371e3
vs = np.sqrt(3.986004418e14 / rs)
chk("GNSS satellite speed km/s", vs / 1e3, 3.87, 0.005)
vlos = vs * re / rs
chk("GNSS max LOS speed m/s", vlos, 929, 1)
chk("GNSS max Doppler kHz", vlos / lam / 1e3, 4.9, 0.02)
chk("GNSS zenith travel time ms", (rs - re) / c * 1e3, 67, 0.5)
chk("GNSS horizon travel time ms", np.sqrt(rs**2 - re**2) / c * 1e3, 86, 0.5)

# ---- 21/sdr-gnss-and-diy-receivers
Tl = 290 * (10 ** (0.8 / 10) - 1); Tsdr = 290 * (10 ** (6 / 10) - 1)
chk("SDR LNA noise temp K", Tl, 58.7, 0.05)
chk("SDR SDR noise temp K", Tsdr, 865, 0.5)
Tsys = 100 + Tl + Tsdr / 100
chk("SDR Tsys with LNA K", Tsys, 167.3, 0.05)
chk("SDR C/N0 with LNA", -125.5 - (k_dBm + 10 * np.log10(Tsys)), 50.9, 0.05)
Tsys0 = 100 + Tsdr
chk("SDR C/N0 without LNA", -125.5 - (k_dBm + 10 * np.log10(Tsys0)), 43.3, 0.05)
span = 2 * (5e3 + 1e-6 * 1575.42e6)
chk("SDR search span kHz", span / 1e3, 13.2, 0.05)
chk("SDR Doppler bins (500 Hz)", np.ceil(span / 500), 27, 0)
chk("SDR search cells", np.ceil(span / 500) * 2046, 55242, 0)

# ---- 21/gnss-on-rockets-dynamics-and-limits
chk("ROCKET Hz per m/s", 1 / lam, 5.26, 0.01)
chk("ROCKET Hz/s per g", g / lam, 51.5, 0.05)
chk("ROCKET 500 m/s Doppler kHz", 500 / lam / 1e3, 2.63, 0.005)
w0 = 15 / 0.53
chk("ROCKET 2nd-order 15 Hz error at 10 g deg", 360 * 10 * g / (lam * w0**2), 232, 0.5)
chk("ROCKET accel for 45 deg budget g", 45 * lam * w0**2 / 360 / g, 1.9, 0.05)

# ---- 15/lora-impairments: SF12/125 kHz at 433.125 MHz
fb = 125e3 / 2**12
chk("LORA bin Hz", fb, 30.5, 0.02)
fe = 4e-6 * 433.125e6
chk("LORA 2x2 ppm offset kHz", fe / 1e3, 1.73, 0.005)
chk("LORA offset in bins", fe / fb, 57, 0.5)
chk("LORA static window bins", 0.25 * 125e3 / fb, 1024, 1e-9)
chk("LORA Mach 1 Doppler bins", 343 * 433.125e6 / c / fb, 16, 0.5)
chk("LORA drift limit Hz", 125e3 / (3 * 2**12), 10.2, 0.05)
chk("LORA drift limit LDRO Hz", 16 * 125e3 / (3 * 2**12), 163, 0.5)
for a, ref in [(3, 77), (6, 154), (10, 256)]:
    chk(f"LORA {a} g sweep over 1.81 s Hz", a * g * 433.125e6 / c * 1.81, ref, 1)
chk("LORA half-bin loss dB", -20 * np.log10(np.sinc(0.5)), 3.9, 0.03)

# ---- 06/vco-and-pll-synthesizers: ADF4351 plan (25 MHz ref, VCO 3471.36 MHz, /8)
chk("PLL Kphi uA per degree (2.5 mA)", 2.5e-3 / (2 * np.pi) * np.radians(1) * 1e6, 6.94, 0.005)
chk("PLL tuning mV per MHz (40 MHz/V)", 1e3 / 40, 25, 1e-9)
chk("PLL 20 log N VCO", 20 * np.log10(3471.36 / 25), 42.9, 0.05)
chk("PLL 20 log 8", 20 * np.log10(8), 18.1, 0.05)
chk("PLL TCXO-only at 433.92 MHz", -140 + 20 * np.log10(433.92 / 25), -115.2, 0.05)

# ---- 06/baluns-and-rf-transformers
def cmdm(adb, deg):
    a = 10 ** (adb / 20); d = np.radians(deg)
    return 20 * np.log10(abs((1 - a * np.exp(1j * d)) / (1 + a * np.exp(1j * d))))
chk("BALUN 0.5 dB / 5 deg CM/DM dB", cmdm(0.5, 5), -25.6, 0.05)
a = 10 ** (0.5 / 20) - 1; d = np.radians(5)
chk("BALUN small-error approx dB", 20 * np.log10(0.5 * np.sqrt(a**2 + d**2)), -25.6, 0.05)
chk("BALUN 0 dB / 10 deg", cmdm(0, 10), -21.2, 0.05)
chk("BALUN 1 dB / 0 deg", cmdm(1, 0), -24.8, 0.05)
chk("BALUN 1.5 dB / 10 deg (TL;DR)", cmdm(1.5, 10), -18.2, 0.05)

# ---- 02/maxwells-equations: 433.92 MHz displacement current
eps0 = 8.8541878188e-12; mu0 = 1.25663706127e-6; eta0 = 376.730
w = 2 * np.pi * 433.92e6
chk("MAX 1 pF 1 V displacement current mA", w * 1e-12 * 1.0 * 1e3, 2.73, 0.005)
chk("MAX seawater wε/σ (εr 81, σ 4)", w * 81 * eps0 / 4, 0.49, 0.005)
chk("MAX copper wε0/σ", w * eps0 / 5.8e7, 4.2e-10, 0.05e-10)
chk("MAX FR-4 conduction/displacement = tanδ", 0.02, 0.02, 0)
chk("MAX EMF 1 cm² loop, 1 µT peak, V", w * 1e-6 * 1e-4, 0.273, 0.001)

# ---- 02/radiation-from-currents-hertzian-dipole: 5 cm wire at 433 MHz
lam433 = c / 433e6
chk("HD lambda m", lam433, 0.692, 0.0005)
chk("HD l/lambda", 0.05 / lam433, 0.0722, 0.0001)
R_u = 80 * np.pi**2 * (0.05 / lam433) ** 2
chk("HD R uniform ohm", R_u, 4.12, 0.01)
chk("HD R triangular ohm", R_u / 4, 1.03, 0.005)
E = eta0 * (2 * np.pi / lam433) * 0.01 * 0.05 / (4 * np.pi * 1000)
chk("HD far field 10 mA, 1 km, uV/m peak", E * 1e6, 136, 0.5)
chk("HD delay 1 km us", 1000 / c * 1e6, 3.34, 0.005)
chk("HD cycles in 1 km", 1000 / c * 433e6, 1444, 1)
chk("HD radiated power 10 mA uniform mW", 0.5 * 0.01**2 * R_u * 1e3, 0.206, 0.001)

# ---- 02/poynting-vector-power-flow: 1 W EIRP at 1 km
S = 1 / (4 * np.pi * 1000**2)
chk("PV S nW/m2", S * 1e9, 79.6, 0.05)
Erms = np.sqrt(eta0 * S)
chk("PV E rms mV/m", Erms * 1e3, 5.48, 0.005)
chk("PV sqrt(30 EIRP)/r mV/m", np.sqrt(30) / 1000 * 1e3, 5.48, 0.005)
chk("PV H rms uA/m", Erms / eta0 * 1e6, 14.5, 0.05)
chk("PV dBuV/m", 20 * np.log10(Erms * 1e6), 74.8, 0.05)
Ae = lam433**2 / (4 * np.pi)
chk("PV Ae isotropic 433 MHz m2", Ae, 0.0381, 0.0002)
chk("PV received dBm", 10 * np.log10(S * Ae * 1e3), -55.2, 0.05)
chk("PV FSPL check dBm", 30 - (32.45 + 20 * np.log10(433) + 0), -55.2, 0.05)

# ---- 02/wave-equation: bulk FR-4 at 433 MHz (εr 4.4, tanδ 0.02)
n = np.sqrt(4.4)
chk("WE lambda in FR-4 m", lam433 / n, 0.330, 0.0005)
beta = 2 * np.pi / (lam433 / n)
chk("WE beta rad/m", beta, 19.05, 0.02)
alpha = beta * 0.02 / 2
chk("WE alpha Np/m", alpha, 0.190, 0.001)
chk("WE alpha dB/m", 8.686 * alpha, 1.65, 0.01)
gam = np.sqrt(1j * w * mu0 * (1j * w * eps0 * 4.4 * (1 - 0.02j)))
chk("WE exact alpha dB/m", 8.686 * gam.real, 1.65, 0.01)
chk("WE eta in FR-4 ohm", eta0 / n, 179.6, 0.1)

# ---- 14/iq-complex-baseband: tone at +150 kHz, 1 ppm at 433 MHz, IQ imbalance 1 % / 1 deg
t = np.arange(0, 20e-6, 1 / 2.4e6)
x = np.exp(1j * 2 * np.pi * 150e3 * t)
dth = np.unwrap(np.angle(x))
chk("IQ +150 kHz phase rotates counter-clockwise (rad/s / 2pi kHz)", np.polyfit(t, dth, 1)[0] / (2 * np.pi) / 1e3, 150, 1e-6)
chk("IQ -150 kHz = conjugate rotates clockwise", np.polyfit(t, np.unwrap(np.angle(np.conj(x))), 1)[0] / (2 * np.pi) / 1e3, -150, 1e-6)
chk("IQ 1 ppm at 433 MHz Hz", 433e6 * 1e-6, 433, 1e-9)
chk("IQ deg per sample at 2.4 MS/s", 360 * 433 / 2.4e6, 0.065, 0.0005)
chk("IQ ms per turn", 1e3 / 433, 2.31, 0.005)
gq, ph = 1.01, np.radians(1)
irr = 10 * np.log10((1 + 2 * gq * np.cos(ph) + gq**2) / (1 - 2 * gq * np.cos(ph) + gq**2))
chk("IQ IRR exact 1 % / 1 deg dB", irr, 40.0, 0.05)
chk("IQ IRR approx 4/(e^2+phi^2) dB", 10 * np.log10(4 / ((gq - 1) ** 2 + ph**2)), 40.0, 0.06)
chk("IQ IRR phase only 1 deg dB", 10 * np.log10((2 + 2 * np.cos(ph)) / (2 - 2 * np.cos(ph))), 41.2, 0.05)

print("ALL PASS" if ok else "SOME FAIL")
