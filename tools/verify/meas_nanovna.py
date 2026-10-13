#!/usr/bin/env python3
"""
meas_nanovna.py -- numerical checks for kb/17-test-measurement/nanovna-librevna-practical.md

1. TDR (VNA time-domain transform) resolution and alias-free range for NanoVNA-H/H4,
   LiteVNA, LibreVNA using Keysight AN 1287-12 Table 1-3 factors
   (low-pass step 10-90 %: 0.45/0.99/1.48 / span; low-pass impulse: 0.60/0.98/1.39 / span;
   bandpass impulse 1.20/1.95/2.77 / span) and range = v / df.
   Plus a synthetic low-pass TDR of a cable with a 75-ohm section, done with numpy.
2. Component measurement: reflection, series-through and shunt-through methods,
   Z = Z0 (1+G)/(1-G), Z = 2 Z0 (1/S21 - 1), Z = Z0 S21 / (2 (1 - S21));
   relative error of |Z| for a fixed S-parameter error, vs |Z| -> which method for which Z.
3. Cable velocity factor from the first quarter-wave resonance of an open stub, and cable loss
   from the open-ended return loss (loss = RL/2), with scikit-rf.
4. L-network / pi-network match of a measured chip-antenna impedance at 915 MHz, checked with
   scikit-rf, and the sensitivity to 0402 component tolerance (+/-2 % L, +/-0.1 pF C).
5. S21 of a filter with a 1.5-port VNA at -13 dBm output: headroom for measuring an LNA.

Run: python3 tools/verify/meas_nanovna.py
"""
import numpy as np
import skrf as rf
from skrf.media import DefinedGammaZ0

C0 = 299792458.0
Z0 = 50.0


def db(x):
    return 20 * np.log10(np.abs(x))


# ---------------------------------------------------------------- 1. TDR resolution and range
print("=== 1. VNA time-domain (TDR) resolution and alias-free range ===")
instruments = [("NanoVNA-H, 101 pts, 0.05-900 MHz", 50e3, 900e6, 101),
               ("NanoVNA-H4, 401 pts, 0.05-1500 MHz", 50e3, 1.5e9, 401),
               ("LiteVNA, 1001 pts, 0.05-6300 MHz", 50e3, 6.3e9, 1001),
               ("LibreVNA, 4501 pts, 0.1-6000 MHz", 100e3, 6e9, 4501)]
vf = 0.66      # RG-58/RG-316-like solid PE
for name, f1, f2, n in instruments:
    span = f2 - f1
    df = span / (n - 1)
    t_step_norm = 0.99 / span          # low-pass step 10-90 % rise, normal window
    t_step_min = 0.45 / span
    t_imp_norm = 0.98 / span
    rng_t = 1 / df                     # alias-free time range (round trip for reflection)
    print(f"{name}: df = {df/1e6:.2f} MHz; step rise (normal/min window) {t_step_norm*1e12:.0f}/{t_step_min*1e12:.0f} ps"
          f" -> resolvable separation in vf={vf} coax (reflection, /2) {t_imp_norm*C0*vf/2*1000:.0f} mm;"
          f" alias-free one-way length {rng_t*C0*vf/2:.1f} m")

# synthetic low-pass step TDR: 1 m 50-ohm coax, 0.3 m of 75-ohm, then 50-ohm, then open, 0.66 vf
f = np.linspace(0, 1.5e9, 401)
f[0] = 1e3
fr = rf.Frequency.from_f(f, unit='Hz')
m50 = DefinedGammaZ0(fr, z0=50, gamma=1j * 2 * np.pi * f / (vf * C0))
m75 = DefinedGammaZ0(fr, z0_port=50, z0=75, gamma=1j * 2 * np.pi * f / (vf * C0))
net = m50.line(1.0, 'm') ** m75.line(0.3, 'm') ** m50.line(0.5, 'm') ** m50.open()
G = net.s[:, 0, 0].copy()
G[0] = G[0].real  # DC point (extrapolated) should be real
# hermitian extension, Kaiser window (beta 6 ~ 'normal'), step = cumulative sum of impulse
w = np.kaiser(2 * len(f) - 1, 6)[len(f) - 1:]
spec = G * w
imp = np.fft.irfft(spec, n=8192)
dt = 1 / (2 * f[-1]) * (2 * (len(f) - 1)) / 8192
step = np.cumsum(imp)
t = np.arange(len(step)) * dt
dist = t * vf * C0 / 2
z_step = 50 * (1 + step) / (1 - step)
for d_probe in [0.5, 1.15, 1.5, 1.6]:
    i = np.argmin(np.abs(dist - d_probe))
    print(f"  synthetic TDR: impedance at {d_probe:.2f} m = {z_step[i]:.1f} ohm")
print("  (75-ohm section between 1.0 and 1.3 m should read ~75 ohm; open at 1.8 m -> very high)")

# ---------------------------------------------------------------- 2. component methods
print("\n=== 2. Which impedance method for which |Z|? ===")
print("error model: reflection |dG| = E_D + E_RT|G| + E_S|G|^2 with E_D = 0.005 (-46 dB), E_RT = 0.005, E_S = 0.01;")
print("             transmission |dS21| = 1e-4 (noise/isolation, -80 dB) + 0.005|S21| + 0.01|S21| (match terms)")
print(f"{'|Z| ohm':>8} {'reflection':>11} {'series-thru':>12} {'shunt-thru':>11}   (worst relative error of |Z|)")
def fmt(x):
    return f"{100*x:10.1f}%" if x < 1 else "     >100%"
for Zm in [0.05, 0.2, 1, 5, 20, 50, 200, 1000, 5000, 20000, 100000]:
    worst = {'refl': 0, 'ser': 0, 'shu': 0}
    for ang in np.linspace(-np.pi / 2, np.pi / 2, 7):      # reactive to resistive
        Z = Zm * np.exp(1j * ang)
        Gm = (Z - Z0) / (Z + Z0)
        S21s = 2 * Z0 / (2 * Z0 + Z)
        S21p = 2 * Z / (2 * Z + Z0)
        eR = 0.005 + 0.005 * abs(Gm) + 0.01 * abs(Gm) ** 2
        eS = 1e-4 + 0.015 * abs(S21s)
        eP = 1e-4 + 0.015 * abs(S21p)
        for ph in np.linspace(0, 2 * np.pi, 16, endpoint=False):
            u = np.exp(1j * ph)
            Zr = Z0 * (1 + Gm + eR * u) / (1 - Gm - eR * u)
            Zs = 2 * Z0 * (1 / (S21s + eS * u) - 1)
            Zp = Z0 * (S21p + eP * u) / (2 * (1 - S21p - eP * u))
            worst['refl'] = max(worst['refl'], abs(Zr - Z) / abs(Z))
            worst['ser'] = max(worst['ser'], abs(Zs - Z) / abs(Z))
            worst['shu'] = max(worst['shu'], abs(Zp - Z) / abs(Z))
    print(f"{Zm:8g} {fmt(worst['refl']):>11} {fmt(worst['ser']):>12} {fmt(worst['shu']):>11}")
print("  -> reflection best ~5 ohm-1 kohm; series-thru for high Z (kohm-100 kohm, e.g. chokes, small C);")
print("     shunt-thru for low Z (< ~2 ohm: ESR, large C, decoupling). Both thru methods are limited by S21 noise floor.")

# ---------------------------------------------------------------- 3. VF and cable loss
print("\n=== 3. Velocity factor and loss of a cable from S11 ===")
L_cable = 2.00       # m
vf_true = 0.695      # e.g. foam/solid mix
alpha_db_per_m_1g = 0.66   # RG-58-ish ~0.66 dB/m at 1 GHz (scaled sqrt f)
f = np.linspace(1e6, 200e6, 4000)
fr = rf.Frequency.from_f(f, unit='Hz')
mc = DefinedGammaZ0(fr, z0=50, gamma=(alpha_db_per_m_1g * np.sqrt(f / 1e9)) / 8.686 + 1j * 2 * np.pi * f / (vf_true * C0))
s11 = (mc.line(L_cable, 'm') ** mc.open()).s[:, 0, 0]
# first quarter-wave resonance of open stub: input looks like a short -> phase of S11 crosses 180 deg
ph = np.unwrap(np.angle(s11))
i = np.argmin(np.abs(ph + np.pi))     # phase = -180 deg (first time)
f_q = f[i]
vf_est = 4 * L_cable * f_q / C0
print(f"open stub L = {L_cable} m: first S11 phase = -180 deg at {f_q/1e6:.2f} MHz -> VF = 4 L f / c = {vf_est:.4f} (true {vf_true})")
k = np.argmin(np.abs(f - 100e6))
print(f"cable loss at 100 MHz: RL of open-ended cable = {-db(s11[k]):.3f} dB -> one-way loss = RL/2 = {-db(s11[k])/2:.3f} dB"
      f" (true {alpha_db_per_m_1g*np.sqrt(0.1)*L_cable:.3f} dB)")
# group delay method
gd = -np.gradient(ph, 2 * np.pi * f)
print(f"group delay of S11 (round trip) = {np.median(gd)*1e9:.3f} ns -> VF = 2L/(c*tau) = {2*L_cable/(C0*np.median(gd)):.4f}")

# ---------------------------------------------------------------- 4. matching a chip antenna
print("\n=== 4. L-match of a measured chip antenna at 915 MHz ===")
f0 = 915e6
w0 = 2 * np.pi * f0
# antenna as a series RLC: Z(915 MHz) = 18 - j32 ohm, Q_L = 8 (small antenna on a small ground)
Ra = 18.0
La = 8 * Ra / w0
Ca = 1 / (w0 * (w0 * La + 32))
def z_ant(fq):
    wq = 2 * np.pi * fq
    return Ra + 1j * (wq * La - 1 / (wq * Ca))
Zant = z_ant(f0)
Q = np.sqrt(Z0 / Ra - 1)
X1 = Q * Ra - Zant.imag
B2 = Q / Z0
Ls, Cp = X1 / w0, B2 / w0
print(f"Zant(915) = {Zant:.2f} ohm (series R {Ra} ohm, L {La*1e9:.1f} nH, C {Ca*1e12:.3f} pF); L-match Q = {Q:.3f}")
print(f"  topology port -- shunt C -- series L -- antenna: L = {Ls*1e9:.2f} nH (X = {X1:.1f} ohm), C = {Cp*1e12:.2f} pF")
fr = rf.Frequency(800, 1030, 461, 'MHz')
med = DefinedGammaZ0(fr, z0=50)
zf = z_ant(fr.f)
ant = rf.Network(frequency=fr, s=((zf - Z0) / (zf + Z0)).reshape(-1, 1, 1))
def match_net(Lv, Cv, cpad=0.0):
    n = med.shunt_capacitor(Cv + cpad) ** med.inductor(Lv)
    if cpad:
        n = n ** med.shunt_capacitor(cpad)
    return n ** ant
k0 = np.argmin(np.abs(fr.f - f0))
def bw10(n):
    ok = db(n.s[:, 0, 0]) < -10
    return (fr.f[ok][0] / 1e6, fr.f[ok][-1] / 1e6) if ok.any() else (np.nan, np.nan)
m = match_net(Ls, Cp)
print(f"  exact values: |S11(915)| = {db(m.s[k0,0,0]):.1f} dB; -10 dB band {bw10(m)[0]:.0f}-{bw10(m)[1]:.0f} MHz")
cands_L = np.array([10, 11, 12, 13, 15, 16, 18, 20, 22, 24, 27]) * 1e-9
cands_C = np.array([1.5, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1]) * 1e-12
best = min(((abs(match_net(Lc, Cc).s[k0, 0, 0]), Lc, Cc) for Lc in cands_L for Cc in cands_C))
print(f"  nearest standard values: L = {best[1]*1e9:.0f} nH, C = {best[2]*1e12:.1f} pF -> |S11(915)| = {db(best[0]):.1f} dB")
worst = -1e9
for dl in (-0.02, 0.02):
    for dc in (-0.1e-12, 0.1e-12):
        worst = max(worst, db(match_net(best[1] * (1 + dl), best[2] + dc).s[k0, 0, 0]))
print(f"  with +/-2 % L and +/-0.1 pF C tolerance: worst |S11(915)| = {worst:.1f} dB")
m_par = match_net(best[1], best[2], cpad=0.15e-12)
fmin = fr.f[np.argmin(np.abs(m_par.s[:, 0, 0]))] / 1e6
print(f"  + 0.15 pF pad/trace capacitance at both nodes: |S11(915)| = {db(m_par.s[k0,0,0]):.1f} dB, best match moves to {fmin:.0f} MHz")
print("  -> compute the first guess, solder it, re-measure, and nudge one part at a time")

# ---------------------------------------------------------------- 5. LNA headroom
print("\n=== 5. Measuring an LNA with a NanoVNA ===")
p_out_vna = -13.0     # dBm below 300 MHz (nVhelp measurements: -12 to -15 dBm)
for gain in [15, 20, 30]:
    for pad in [0, 20]:
        pin = p_out_vna - pad
        pout = pin + gain
        print(f"LNA gain {gain} dB, input pad {pad} dB: LNA input {pin:.0f} dBm, output {pout:.0f} dBm into CH1")
print("  -> a typical LNA with OP1dB ~ +10..+20 dBm is fine at -13 dBm in, but a 30 dB LNA puts +17 dBm into CH1;"
      " pad the INPUT (or reduce power) so the LNA is linear and CH1 below ~ -10 dBm")
