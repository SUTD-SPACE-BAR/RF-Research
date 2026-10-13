#!/usr/bin/env python3
"""
noise_thermal.py — verification for kb/07-noise-linearity/thermal-noise-and-noise-temperature.md

Checks:
  1. kT0 in dBm/Hz (-173.975 -> "-174 dBm/Hz") and kTB for common bandwidths.
  2. Planck (quantum) vs Rayleigh-Jeans (classical) available noise power per Hz:
     ratio x/(e^x - 1), x = hf/kT, at RF/mm-wave/THz and at cryogenic temperature.
     Also the zero-point term hf/2 (Callen-Welton) for reference.
  3. Open-circuit noise voltage of resistors (sqrt(4kTRB)).
  4. Lossy passive at physical temperature Tp: Te = (L-1)Tp, F = 1 + (L-1)Tp/T0; F = L at Tp = T0.
     Verified against a brute-force "attenuator = cascade of many thin slices" model.
  5. Antenna temperature seen through a lossy feeder: T_out = Ta/L + Tp(1 - 1/L).
  6. ITU-R P.372 median external noise figure Fam = c - d log10(f_MHz) (Table 1) and Ta = T0*10^(Fa/10),
     tabulated for 30...250 MHz, plus measured 425 MHz values (P.372-13 Table 3), galactic Tb scaling f^-2.75.
  7. System noise temperature and effective noise figure for a receiver with an external antenna temperature.

Run:  python3 noise_thermal.py
"""
import numpy as np

k = 1.380649e-23      # J/K (exact, SI 2019)
h = 6.62607015e-34    # J s (exact)
T0 = 290.0            # K reference temperature (IEEE/ITU)

def dbm(p_w):
    return 10*np.log10(p_w/1e-3)

print("=== 1. kT0 and kTB ===")
kT0 = k*T0
print(f"kT0 = {kT0:.4e} W/Hz = {dbm(kT0):.3f} dBm/Hz  (rounded: -174 dBm/Hz)")
print(f"10log10(kT0) = {10*np.log10(kT0):.3f} dBW/Hz (ITU-R P.372 uses -204 dBW)")
for B, name in [(1, '1 Hz'), (1e3, '1 kHz'), (10.4e3, 'LoRa 10.4 kHz'), (125e3, 'LoRa 125 kHz'),
                (250e3, 'LoRa 250 kHz'), (500e3, 'LoRa 500 kHz'), (1e6, '1 MHz'),
                (2.046e6, 'GPS C/A main lobe 2.046 MHz'), (20e6, '20 MHz (Wi-Fi)'), (1e9, '1 GHz (radar)')]:
    print(f"  kT0B, B = {name:28s}: {dbm(kT0*B):8.2f} dBm")

print("\n=== 2. Planck vs Rayleigh-Jeans ===")
def planck_ratio(f, T):
    x = h*f/(k*T)
    return x/np.expm1(x)
for T in (290.0, 77.0, 4.0):
    for f in (433e6, 1.57542e9, 10e9, 77e9, 300e9, 1e12, 6e12):
        r = planck_ratio(f, T)
        print(f"  T={T:6.1f} K f={f/1e9:9.4f} GHz: hf/kT={h*f/(k*T):.3e}  P_planck/P_RJ = {r:.6f} "
              f"({10*np.log10(r):+.4f} dB)")
# frequency where Planck is 1 dB (factor 0.794) below RJ at 290 K
from scipy.optimize import brentq
f1dB = brentq(lambda f: planck_ratio(f, 290.0) - 10**(-0.1), 1e9, 1e14)
print(f"  At 290 K, quantum correction reaches -1 dB at f = {f1dB/1e12:.2f} THz")
f1dB_4K = brentq(lambda f: planck_ratio(f, 4.0) - 10**(-0.1), 1e6, 1e13)
print(f"  At 4 K,   quantum correction reaches -1 dB at f = {f1dB_4K/1e9:.1f} GHz")
# quantum-limit noise temperature hf/k for amplifiers (phase-insensitive amplifier minimum ~ hf/(2k)... hf/k)
for f in (433e6, 1.57542e9, 10e9, 100e9):
    print(f"  hf/k at {f/1e9:.4g} GHz = {h*f/k*1e3:.3f} mK (quantum-limit scale)")

print("\n=== 3. Resistor open-circuit noise voltage ===")
for R in (50.0, 1e3, 1e6):
    for B in (1.0, 125e3, 1e6):
        vn = np.sqrt(4*k*T0*R*B)
        print(f"  R={R:9.0f} ohm, B={B:9.0f} Hz: vn,rms = {vn*1e9:10.3f} nV   ({vn/np.sqrt(B)*1e9:.3f} nV/rtHz)")
print("  Available power into matched load = vn^2/(4R) = kTB, independent of R (check):",
      np.isclose((np.sqrt(4*k*T0*50*1e6))**2/(4*50), k*T0*1e6))

print("\n=== 4. Lossy passive at physical temperature Tp ===")
def lossy_Te(L_dB, Tp=T0):
    L = 10**(L_dB/10)
    return (L-1)*Tp
def slice_model(L_dB, Tp=T0, n=2000):
    """Attenuator as n thin slices each of loss l = L^(1/n), each adding kTp(1-1/l) of noise
    (a matched attenuator in equilibrium must output kTp). Propagate noise temperature through slices
    with an input source at 0 K; the output noise temperature referred to input gives Te."""
    L = 10**(L_dB/10)
    l = L**(1/n)
    Tout = 0.0
    for _ in range(n):
        Tout = Tout/l + Tp*(1 - 1/l)
    return Tout*L   # refer to input
for L_dB in (0.5, 1, 2, 3, 6, 10):
    Te = lossy_Te(L_dB)
    F = 1 + Te/T0
    print(f"  L={L_dB:4.1f} dB: Te={Te:8.2f} K, NF = {10*np.log10(F):.3f} dB (== L at Tp=T0), slice model Te={slice_model(L_dB):8.2f} K")
# cold / hot feeder
for Tp in (250.0, 290.0, 330.0):
    Te = lossy_Te(2.0, Tp)
    print(f"  2 dB cable at Tp={Tp:.0f} K: Te={Te:.1f} K, NF={10*np.log10(1+Te/T0):.3f} dB")

print("\n=== 5. Antenna temperature through a lossy feeder ===")
def t_through_loss(Ta, L_dB, Tp=T0):
    L = 10**(L_dB/10)
    return Ta/L + Tp*(1-1/L)
for Ta in (10.0, 50.0, 150.0, 290.0, 1000.0):
    print(f"  Ta={Ta:6.1f} K through 1 dB feeder -> {t_through_loss(Ta,1.0):6.1f} K at receiver input")

print("\n=== 6. ITU-R P.372 man-made / galactic noise ===")
tab1 = {'city': (76.8, 27.7), 'residential': (72.5, 27.7), 'rural': (67.2, 27.7),
        'quiet rural': (53.6, 28.6), 'galactic': (52.0, 23.0)}
print("  Fam (dB above kT0b) and Ta (K); Table 1 valid 0.3-250 MHz (quiet rural/galactic narrower)")
print("  f(MHz)  " + "  ".join(f"{n:>18s}" for n in tab1))
for f in (3.0, 10.0, 30.0, 50.0, 100.0, 144.0, 250.0):
    row = []
    for n, (c, d) in tab1.items():
        Fa = c - d*np.log10(f)
        row.append(f"{Fa:6.1f} dB/{T0*10**(Fa/10):9.0f} K")
    print(f"  {f:6.1f}  " + "  ".join(f"{r:>18s}" for r in row))
print("  Extrapolation of Table 1 to 433 MHz (OUT OF STATED RANGE):",
      {n: round(c - d*np.log10(433.0), 1) for n, (c, d) in tab1.items()})
print("  Measured (P.372-13 Table 3, Europe outdoor, 425 MHz): city 6 dB, residential 4 dB, rural 3 dB")
for Fa in (6, 4, 3):
    print(f"    Fa={Fa} dB -> Ta = {T0*10**(Fa/10):.0f} K")
# galactic scaling (P.372 eq. 15)
Tb408 = np.array([20.0, 60.0, 200.0])  # K, cold sky / typical / galactic plane at 408 MHz (illustrative)
for f in (433.0, 915.0, 1575.42):
    Tb = Tb408*(f/408.0)**-2.75 + 2.7
    print(f"  Galactic sky Tb at {f:7.2f} MHz from Tb(408)={Tb408} K: {np.round(Tb,1)} K")
print("  Check P.372 example: Tb(408)=200 K -> 1 GHz:", round(200*(1000/408)**-2.75 + 2.7, 1), "K (P.372 says 19.7 K)")

print("\n=== 7. System noise temperature with external antenna noise ===")
def sys_noise(Ta, NF_dB, B):
    Te = T0*(10**(NF_dB/10) - 1)
    Tsys = Ta + Te
    N = k*Tsys*B
    return Te, Tsys, dbm(N)
for Ta in (50.0, 150.0, 290.0, 580.0, 2000.0):
    Te, Tsys, N = sys_noise(Ta, 6.0, 125e3)
    Nspec = dbm(k*T0*10**(0.6)*125e3)
    print(f"  Ta={Ta:6.0f} K, NF=6 dB (Te={Te:.0f} K): Tsys={Tsys:7.0f} K, N(125 kHz)={N:7.2f} dBm, "
          f"vs datasheet assumption (Ta=T0) {Nspec:7.2f} dBm -> delta {N-Nspec:+.2f} dB")
# low-noise GNSS chain: sky-pointing patch
for Ta in (50.0, 100.0, 150.0):
    for NF in (0.5, 1.0, 2.0):
        Te, Tsys, N = sys_noise(Ta, NF, 1.0)
        print(f"  GNSS: Ta={Ta:5.0f} K, NF={NF} dB -> Tsys={Tsys:6.1f} K, N0 = {N:.2f} dBm/Hz")
print("\nAll checks printed. Key numbers: -173.98 dBm/Hz; Planck correction negligible below ~100 GHz at 290 K.")

print("\n=== 8. Statistics and bandwidth helpers ===")
rng = np.random.default_rng(0)
x = rng.exponential(1.0, 2_000_000)          # detected power of Gaussian noise (Rayleigh envelope)
print(f"  mean of 10log10(power) for Gaussian noise = {np.mean(10*np.log10(x)):.3f} dB "
      f"(theory -10 log10(e) * EulerGamma = {-10*np.log10(np.e)*0.5772156649:.3f} dB) -> log-averaged SA traces read ~2.5 dB low")
# equivalent noise bandwidth of a one-pole RC low-pass and of n-pole Butterworth
from scipy.integrate import quad
for n in (1, 2, 3, 5):
    Bn, _ = quad(lambda f: 1/(1 + f**(2*n)), 0, np.inf)
    print(f"  {n}-pole Butterworth low-pass: noise bandwidth = {Bn:.4f} x f_3dB" + ("  (= pi/2 for RC)" if n == 1 else ""))
Bg, _ = quad(lambda f: np.exp(-np.log(2)*(2*f)**2*1.0), -np.inf, np.inf)   # Gaussian |H|^2 with -3 dB at f=+-0.5
print(f"  Gaussian filter: noise bandwidth = {Bg:.4f} x (3 dB bandwidth)")
# peak/rms of Gaussian noise
v = rng.standard_normal(2_000_000)
for p in (1e-2, 1e-4, 1e-6):
    thr = np.sqrt(2)*__import__('scipy').special.erfcinv(p)
    print(f"  Gaussian noise exceeds {thr:.2f} x rms with probability {p:g} (crest factor {20*np.log10(thr):.1f} dB)")
