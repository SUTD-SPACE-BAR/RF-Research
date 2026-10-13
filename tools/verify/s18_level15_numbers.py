"""W5-S18: checks every number quoted in the "Level 1½" rungs added by the S18 quality pass.
Run: python3 tools/verify/s18_level15_numbers.py   (prints each value; ALL PASS at the end)."""
import numpy as np
c = 299792458.0
ok = True
def chk(name, val, ref, tol):
    global ok
    good = abs(val - ref) <= tol
    ok &= good
    print(f"{'PASS' if good else 'FAIL'}  {name}: {val:.6g} (page {ref})")

# 11/ambiguity: 10 GHz pulsed LFM, B 10 MHz, T 10 us, target 300 m/s
lam = c / 10e9; B = 10e6; T = 10e-6
chk("ambig range res m", c / (2 * B), 15.0, 0.02)
chk("ambig doppler res kHz", 1 / T / 1e3, 100, 1e-9)
chk("ambig velocity res m/s", lam / (2 * T), 1499, 1)
fd = 2 * 300 / lam
chk("ambig fd kHz", fd / 1e3, 20.0, 0.02)
tau = fd * T / B
chk("ambig delay shift ns", tau * 1e9, 20.0, 0.05)
chk("ambig range bias m", c * tau / 2, 3.0, 0.01)
chk("ambig peak loss dB", -20 * np.log10(1 - tau / T), 0.017, 0.001)

# 12/adaptive: 433.92 MHz, d = lambda/2, 60 deg phase step, 5 deg error, null at 30 deg
th = np.degrees(np.arcsin(60 / 180))
chk("doa angle deg", th, 19.47, 0.01)
dth = np.radians(5) / (np.pi * np.cos(np.radians(th)))
chk("doa angle error deg", np.degrees(dth), 1.69, 0.01)
psi_i = np.pi * np.sin(np.radians(30))
w = np.array([1, -np.exp(-1j * psi_i)])
y_int = w[0] + w[1] * np.exp(1j * psi_i)
y_des = abs(w[0] + w[1])
chk("null residual", abs(y_int), 0, 1e-12)
chk("desired loss dB vs plain sum", 20 * np.log10(y_des / 2), -3.01, 0.01)
chk("averaging 100 snapshots error deg", np.degrees(dth) / 10, 0.17, 0.005)

# 03/bode-fano: 50 ohm || 3 pF; antenna Q 30
R, C = 50, 3e-12
bud = 1 / (2 * R * C)
chk("BF df*ln budget GHz", bud / 1e9, 3.33, 0.005)
chk("BF df at RL20 GHz", bud / np.log(10) / 1e9, 1.45, 0.005)
chk("BF df at RL10 GHz", bud / np.log(1 / 10 ** (-10 / 20)) / 1e9, 2.90, 0.005)
fbw = (928 - 863) / np.sqrt(863 * 928)
chk("BF FBW 863-928", fbw, 0.0726, 0.0005)
gm = np.exp(-np.pi / (30 * fbw))
chk("BF Gamma_m Q30", gm, 0.236, 0.002)
chk("BF RL dB", -20 * np.log10(gm), 12.5, 0.05)
chk("BF mismatch loss dB", -10 * np.log10(1 - gm ** 2), 0.25, 0.01)

# 14/digital filters: 4-tap MA at 1 kHz; EMA alpha 0.1 at 100 Hz
f, fs, N = 100, 1000, 4
g = abs(np.sin(N * np.pi * f / fs) / (N * np.sin(np.pi * f / fs)))
chk("MA gain 100 Hz", g, 0.769, 0.001)
chk("MA gain dB", 20 * np.log10(g), -2.28, 0.01)
x = np.cos(2 * np.pi * 250 * np.arange(64) / fs)
y = np.convolve(x, np.ones(4) / 4, mode="valid")
chk("MA output at 250 Hz", np.max(abs(y)), 0, 1e-12)
a = 0.1; fs2 = 100
chk("EMA tau s exact", -1 / fs2 / np.log(1 - a), 0.0949, 0.0001)
cw = (1 + (1 - a) ** 2 - 2 * a ** 2) / (2 * (1 - a))
f3 = np.arccos(cw) * fs2 / (2 * np.pi)
chk("EMA f3dB Hz", f3, 1.68, 0.005)
chk("EMA analog approx Hz", a * fs2 / (2 * np.pi), 1.59, 0.005)

# 14/fft: 1 MS/s, N 1000, tone 100.4 kHz
chk("FFT scallop 0.4 bin dB", 20 * np.log10(np.sinc(0.4)), -2.42, 0.01)
chk("FFT scallop 0.5 bin dB", 20 * np.log10(np.sinc(0.5)), -3.92, 0.01)
n = np.arange(1000); xt = np.exp(2j * np.pi * 100e3 * n / 1e6)
chk("FFT |X| complex tone", abs(np.fft.fft(xt)[100]), 1000, 1e-6)
rng = np.random.default_rng(1)
nz = (rng.standard_normal((400, 1000)) + 1j * rng.standard_normal((400, 1000))) / np.sqrt(2)
chk("FFT noise bin power / N", np.mean(abs(np.fft.fft(nz, axis=1)) ** 2) / 1000, 1.0, 0.02)

# 11/detection: Pfa 1e-6, Albersheim N=1 Pd 0.9, CA-CFAR N=16, false alarms per second
chk("thr dB", 10 * np.log10(np.log(1e6)), 11.40, 0.01)
A = np.log(0.62 / 1e-6); Bb = np.log(0.9 / 0.1)
snr = -5 * np.log10(1) + (6.2 + 4.54 / np.sqrt(1.44)) * np.log10(A + 0.12 * A * Bb + 1.7 * Bb)
chk("Albersheim SNR dB", snr, 13.1, 0.05)
al = 16 * (1e-6 ** (-1 / 16) - 1)
chk("CA-CFAR alpha", al, 21.9, 0.05)
chk("CA-CFAR alpha dB", 10 * np.log10(al), 13.41, 0.01)
cells = 256 * 128 * 20
chk("cells per s", cells, 655360, 0)
chk("false alarms per s", cells * 1e-6, 0.66, 0.005)

# 12/array-calibration: 8 ch, 10 deg rms phase error
s = np.radians(10)
chk("cal gain loss dB", 10 * np.log10(np.exp(-s ** 2)), -0.13, 0.005)
chk("cal floor dB (8 el, uniform)", 10 * np.log10(s ** 2 / 8), -24.2, 0.05)
chk("cal 2 deg floor dB", 10 * np.log10(np.radians(2) ** 2 / 8), -38.2, 0.05)
# Monte-Carlo check of the average sidelobe floor
Nn = 8; trials = 20000
u = 0.6  # a direction in a sidelobe null region? use average over random errors at a fixed off-beam u
k = np.pi  # kd for d = lambda/2
ph = rng.normal(0, s, (trials, Nn))
af = np.abs(np.exp(1j * ph) @ np.exp(1j * k * np.arange(Nn) * u)) ** 2 / Nn ** 2
af0 = np.abs(np.sum(np.exp(1j * k * np.arange(Nn) * u))) ** 2 / Nn ** 2
chk("cal MC floor (excess) dB", 10 * np.log10(np.mean(af) - af0 * np.exp(-s**2)), -24.2, 0.3)

# 12/planar: 5.8 GHz 8x8 lambda/2
lam = c / 5.8e9; d = lam / 2
G = 4 * np.pi * (8 * d) ** 2 / lam ** 2
chk("planar G dBi", 10 * np.log10(G), 23.0, 0.05)
chk("planar 45 deg dBi", 10 * np.log10(G * np.cos(np.radians(45))), 21.5, 0.05)
chk("planar d mm", d * 1e3, 25.8, 0.05)
chk("planar dmax 60 mm", lam / (1 + np.sin(np.radians(60))) * 1e3, 27.7, 0.05)

# 12/conformal: 98 mm tube at 2450 MHz
lam = c / 2.45e9; Cc = np.pi * 0.098
chk("conformal C/lambda", Cc / lam, 2.52, 0.005)
chk("conformal Nmin", 2 * Cc / lam, 5.03, 0.005)
chk("conformal spacing mm (6)", Cc / 6 * 1e3, 51.3, 0.05)
chk("conformal spacing lambda", Cc / 6 / lam, 0.42, 0.005)

# 12/synthesis: two elements d = lambda/4, w = [1, -j]
z = lambda uu: np.exp(1j * (np.pi / 2) * uu)
chk("cardioid back null", abs(1 + (-1j) * z(-1)), 0, 1e-12)
chk("cardioid front", abs(1 + (-1j) * z(1)), 2, 1e-12)
chk("cardioid broadside", abs(1 + (-1j) * z(0)), np.sqrt(2), 1e-12)
chk("Woodward spacing (N=8, d=l/2)", 1 / (8 * 0.5), 0.25, 0)

# 07/volterra: a1 = 10, a3 = -4/3 V^-2, 50 ohm
a1, a3 = 10.0, -4 / 3
Aip3 = np.sqrt(4 / 3 * abs(a1 / a3))
chk("IIP3 amplitude V", Aip3, 3.162, 0.001)
chk("IIP3 dBm (50 ohm)", 10 * np.log10(Aip3 ** 2 / 100 / 1e-3), 20.0, 0.01)
Ain = 0.1
chk("Pin dBm", 10 * np.log10(Ain ** 2 / 100 / 1e-3), -10.0, 0.01)
chk("IM3 dBc", 20 * np.log10(0.75 * abs(a3 / a1) * Ain ** 2), -60.0, 0.01)
# direct two-tone check
t = np.arange(4096) / 4096
xx = Ain * np.cos(2 * np.pi * 100 * t) + Ain * np.cos(2 * np.pi * 110 * t)
yy = a1 * xx + a3 * xx ** 3
Y = np.abs(np.fft.rfft(yy)) / 2048
chk("two-tone IM3 dBc (FFT)", 20 * np.log10(Y[90] / Y[100]), -60.0, 0.05)
chk("asymmetry 1.2x dB", 20 * np.log10(1.2), 1.58, 0.01)

# 06/ltv-isf: Leeson 433 MHz, QL 20, F 2, Ps 1 mW, fm 100 kHz; ISF kick
kT = 1.380649e-23 * 290
floor = 10 * np.log10(2 * kT / (2 * 1e-3))
chk("Leeson floor dBc/Hz", floor, -174.0, 0.05)
fL = 433e6 / 40
chk("Leeson fL MHz", fL / 1e6, 10.825, 0.001)
L100 = 10 * np.log10(2 * kT / 2e-3 * (1 + (fL / 1e5) ** 2))
chk("Leeson L(100k)", L100, -133.3, 0.05)
chk("Leeson with 10 kHz corner", 10 * np.log10(2 * kT / 2e-3 * (1 + (fL / 1e5) ** 2) * 1.1), -132.9, 0.05)
qmax = 10e-12
chk("ISF kick rad", 1 * 1e-15 / qmax, 1e-4, 1e-12)
Lisf = 0.5 * 1e-24 / (2 * qmax ** 2 * (2 * np.pi * 1e5) ** 2)
chk("ISF L dBc/Hz", 10 * np.log10(Lisf), -142.0, 0.05)

# 08/MoM: 433 MHz dipole 0.33 m, 21 segments
lam = c / 433e6
chk("seg mm", 330 / 21, 15.7, 0.05)
chk("seg in lambda (1/x)", lam / 0.33 * 21, 44, 0.5)
chk("Z entries", 21 ** 2, 441, 0)

print("ALL PASS" if ok else "SOME FAILED")
