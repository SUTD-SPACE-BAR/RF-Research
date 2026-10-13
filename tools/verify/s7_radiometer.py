#!/usr/bin/env python3
"""S7 (W5-S7) radiometry checks for kb/07-noise-linearity/thermal-noise-and-noise-temperature.md
"Radiometry" section.

 §1 total-power radiometer: sigma_T = Tsys/sqrt(B tau)   (Monte Carlo)
 §2 Dicke-switched radiometer: sigma_T = 2 Tsys/sqrt(B tau) (Monte Carlo)
 §3 gain fluctuations: sigma_T = Tsys*sqrt(1/(B tau) + (dG/G)^2); Dicke switching removes slow drift
 §4 Sun at 433.92 MHz with an 11 dBi Yagi: T_A = A_e S / (2k)  (unpolarised source, one polarisation)
 §5 SDR sun-drift worked example: Y-factor with/without LNA, integration time, gain-drift limit
 §6 beam efficiency bookkeeping
 §7 two-element interferometer: fringe spacing, fringe period for a drifting Sun,
    correlation sensitivity sigma = sqrt((T1 T2 + Ts^2)/(2N))  (Monte Carlo)
Run: python3 tools/verify/s7_radiometer.py   (≈ 5 s)
"""
import numpy as np

rng = np.random.default_rng(7)
k = 1.380649e-23
c = 299792458.0
ok = True


def check(name, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")


def cnoise(n, T):
    """complex baseband noise samples with E|x|^2 = T (power in 'kelvin' units)"""
    return np.sqrt(T / 2) * (rng.standard_normal(n) + 1j * rng.standard_normal(n))


print("§1 Total-power radiometer (complex sampling at fs = B: B tau independent samples)")
Tsys = 200.0
for Btau in (100, 1000, 10000):
    trials = 4000
    est = np.array([np.mean(np.abs(cnoise(Btau, Tsys)) ** 2) for _ in range(trials)])
    sim = est.std()
    th = Tsys / np.sqrt(Btau)
    print(f"  B*tau={Btau:6d}: sigma_T sim {sim:7.3f} K, theory Tsys/sqrt(B tau) {th:7.3f} K")
    check(f"total-power B*tau={Btau}", abs(sim / th - 1) < 0.05)

print("§2 Dicke radiometer (half time on antenna, half on reference; output = difference)")
Ta, Tref, Trx = 150.0, 150.0, 50.0  # balanced
for Btau in (1000, 10000):
    trials = 3000
    n2 = Btau // 2
    d = np.array([np.mean(np.abs(cnoise(n2, Ta + Trx)) ** 2) - np.mean(np.abs(cnoise(n2, Tref + Trx)) ** 2)
                  for _ in range(trials)])
    th = 2 * (Ta + Trx) / np.sqrt(Btau)
    print(f"  B*tau={Btau}: sigma sim {d.std():.3f} K, theory 2Tsys/sqrt(B tau) {th:.3f} K")
    check(f"Dicke factor 2 at B*tau={Btau}", abs(d.std() / th - 1) < 0.05)

print("§3 Gain fluctuations")
# formula
B, tau = 2e6, 1.0
for dGdB in (0.001, 0.01, 0.05):
    g = 10 ** (dGdB / 10) - 1
    s = Tsys * np.sqrt(1 / (B * tau) + g ** 2)
    print(f"  Tsys {Tsys:.0f} K, B 2 MHz, tau 1 s, gain wander {dGdB} dB rms -> sigma_T {s:.3f} K "
          f"(noise-only {Tsys/np.sqrt(B*tau):.3f} K)")
# MC: slow gain drift (random walk) on a total-power vs Dicke receiver, 200 records
blocks, nb = 200, 2000            # 200 integration blocks each of 2000 samples
G = 1 + 0.03 * np.sin(2 * np.pi * np.arange(blocks) / blocks)  # slow wander, 2.1 % rms
tp, dk = [], []
for b in range(blocks):
    tp.append(G[b] * np.mean(np.abs(cnoise(nb, Tsys)) ** 2))
    dk.append(G[b] * (np.mean(np.abs(cnoise(nb // 2, Tsys)) ** 2) - np.mean(np.abs(cnoise(nb // 2, Tsys)) ** 2)))
tp, dk = np.array(tp), np.array(dk)
print(f"  MC with ~{100*G.std():.2f} % rms gain wander: total-power output std {tp.std():.2f} K "
      f"(noise alone {Tsys/np.sqrt(nb):.2f}); Dicke std {dk.std():.2f} K (noise alone {2*Tsys/np.sqrt(nb):.2f})")
pred = np.sqrt((Tsys / np.sqrt(nb)) ** 2 + (Tsys * G.std()) ** 2)
print(f"  total-power prediction sqrt(noise^2 + (Tsys dG/G)^2) = {pred:.2f} K")
check("total power includes gain term", abs(tp.std() / pred - 1) < 0.15 and tp.std() > 1.2 * Tsys / np.sqrt(nb))
check("Dicke output unaffected by gain wander", abs(dk.std() / (2 * Tsys / np.sqrt(nb)) - 1) < 0.15)

print("§4 Sun in an 11 dBi Yagi at 433.92 MHz")
f = 433.92e6
lam = c / f
G = 10 ** (11 / 10)
Ae = G * lam ** 2 / (4 * np.pi)
sfu = 1e-22
for S in (25, 35, 50):
    TA = Ae * S * sfu / (2 * k)
    print(f"  S = {S} sfu: A_e = {Ae:.3f} m^2, Delta T_A = {TA:.1f} K")
TA35 = Ae * 35 * sfu / (2 * k)
check("Sun 35 sfu -> ~60 K in 11 dBi Yagi", 55 < TA35 < 65)
beam = np.degrees(np.sqrt(4 * np.pi / G))  # crude equivalent cone width (rad->deg) of a pencil beam
print(f"  crude beam width sqrt(4pi/G) = {beam:.0f} deg >> Sun's ~0.5-1 deg radio disc -> point source")

print("§5 SDR sun-drift measurement (Y-factor), B = 2 MHz")
Tsky_ground = 150.0                 # T_A off-Sun (sky + ground in sidelobes), engineering estimate
Te_rtl = 290 * (10 ** (5.4 / 10) - 1)    # RTL-SDR V3 NF 5.4 dB at 437 MHz (canonical)
Te_lna = 290 * (10 ** (0.6 / 10) - 1)    # LNA NF 0.6 dB
coax_L = 10 ** (0.5 / 10)                # 0.5 dB jumper after the LNA (negligible), none before
cases = {"RTL-SDR alone": Te_rtl, "LNA (NF 0.6 dB, 20 dB) + RTL-SDR": Te_lna + Te_rtl / 100}
for name, Te in cases.items():
    Toff = Tsky_ground + Te
    Ton = Toff + TA35
    Y = 10 * np.log10(Ton / Toff)
    s1 = Toff / np.sqrt(2e6 * 1.0)
    print(f"  {name}: Te {Te:.0f} K, Tsys off {Toff:.0f} K, on {Ton:.0f} K -> Y = {Y:.2f} dB; "
          f"radiometer sigma (1 s) {s1:.2f} K; 0.05 dB gain drift = {Toff*(10**0.005-1):.1f} K")
Y_rtl = 10 * np.log10((Tsky_ground + Te_rtl + TA35) / (Tsky_ground + Te_rtl))
Y_lna = 10 * np.log10((Tsky_ground + Te_lna + Te_rtl / 100 + TA35) / (Tsky_ground + Te_lna + Te_rtl / 100))
check("Y-factor RTL alone ~0.2-0.3 dB", 0.15 < Y_rtl < 0.35)
check("Y-factor with LNA ~1-1.4 dB", 0.9 < Y_lna < 1.4)
# hot-cold calibration: load (295 K) vs sky reading gives T_A off-Sun
Tload = 295.0
Te = Te_lna + Te_rtl / 100
P_load, P_sky = Tload + Te, Tsky_ground + Te
Y_ls = P_load / P_sky
TA_back = (Tload + Te) / Y_ls - Te
print(f"  load/sky Y = {10*np.log10(Y_ls):.2f} dB -> recovered T_A = {TA_back:.1f} K (needs Te known)")
check("load/sky inversion", abs(TA_back - Tsky_ground) < 1e-9)

Yl = 10 ** (Y_lna / 10)
GT = 8 * np.pi * k * (Yl - 1) / (35 * sfu * lam ** 2)
print(f"  Sun-noise G/T from Y = {Y_lna:.2f} dB at 35 sfu: {10*np.log10(GT):.1f} dB/K "
      f"(direct: 11 dBi - 10log({Tsky_ground + Te_lna + Te_rtl/100:.0f} K) = {11-10*np.log10(Tsky_ground + Te_lna + Te_rtl/100):.1f})")
check("Sun-noise G/T inversion", abs(10*np.log10(GT) - (11-10*np.log10(Tsky_ground + Te_lna + Te_rtl/100))) < 0.01)

print("§6 Beam efficiency")
for etaB, Tmb, Tsl in ((0.7, 60, 290), (0.85, 60, 290)):
    print(f"  eta_B {etaB}: T_A = eta_B*T_MB + (1-eta_B)*T_SL = {etaB*Tmb+(1-etaB)*Tsl:.0f} K "
          f"(main beam on 60 K sky, sidelobes on 290 K ground)")

print("§7 Two-element interferometer")
we = 7.2921159e-5
for b in (5.0, 10.0, 20.0):
    bl = b / lam
    spacing = np.degrees(1 / bl)
    period = 1 / (bl * we)  # E-W baseline, source on the celestial equator near transit
    print(f"  baseline {b:4.0f} m = {bl:5.2f} lambda: fringe spacing {spacing:5.2f} deg, "
          f"fringe period {period/60:5.1f} min (dec 0, near transit)")
period10 = 1 / ((10 / lam) * we) / 60
check("10 m at 434 MHz -> ~16 min fringes", 15 < period10 < 17)
# correlation sensitivity
Ts, T1, T2, N = 20.0, 400.0, 500.0, 20000
trials = 1500
s = []
for _ in range(trials):
    src = cnoise(N, Ts)
    x = src + cnoise(N, T1 - Ts)
    y = src + cnoise(N, T2 - Ts)
    s.append(np.mean(x * np.conj(y)).real)
s = np.array(s)
th_sd = np.sqrt((T1 * T2 + Ts ** 2) / (2 * N))
print(f"  correlator: mean {s.mean():.2f} K (true {Ts}), std {s.std():.3f} vs theory {th_sd:.3f} K; "
      f"total-power on one antenna would be {T1/np.sqrt(N):.3f} K and biased by receiver-noise drift")
check("correlator unbiased", abs(s.mean() - Ts) < 4 * th_sd / np.sqrt(trials))
check("correlator std formula", abs(s.std() / th_sd - 1) < 0.06)

print("\nALL PASS" if ok else "\nSOME FAILED")
