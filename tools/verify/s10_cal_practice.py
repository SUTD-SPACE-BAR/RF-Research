#!/usr/bin/env python3
"""W5-S10 checks for 17/vna-fundamentals-calibration and 17/nanovna-librevna-practical
(calibration practice: DIY SOL standards, characterising them, the "calibrate with 73 Ohm" myth,
adapters after calibration, frequency-reference accuracy).

A. DIY load (two 0402 100 Ohm in parallel on an SMA) -> residual directivity vs frequency.
B. Characterising a DIY open/short against a trusted kit: offset delay from the short, C(f) fit
   (C0..C3) for the open; error of an ideal-definition DIY cal vs a characterised one.
C. Calibrating with a 73 Ohm resistor as "load" = renormalising to 73 Ohm (exact for ideal O/S/R);
   with real parasitics it is worse than a 50 Ohm cal + renormalisation.
D. A UHF (PL-259/SO-239) adapter added after calibration -> effective directivity vs frequency.
E. Frequency-reference error: Hz at 433/915 MHz, effect on a high-Q resonator and on cable phase.
"""
import numpy as np

ok_all = True
def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(("PASS " if cond else "FAIL ") + name)

Z0 = 50.0
c = 299792458.0
f = np.linspace(50e6, 3e9, 600)
w = 2 * np.pi * f
gam = lambda Z, z0=Z0: (Z - z0) / (Z + z0)

def open_std(f, tau, C):
    w = 2 * np.pi * f
    return np.exp(-2j * w * tau) * (1 - 1j * w * C * Z0) / (1 + 1j * w * C * Z0)

def short_std(f, tau, L):
    w = 2 * np.pi * f
    return -np.exp(-2j * w * tau) * (1 - 1j * w * L / Z0) / (1 + 1j * w * L / Z0) * -1 * -1

def sol_terms(mL, mO, mS, GL, GO, GS):
    """General 3-standard one-port solve (linear in e00, e11, De):  e00 + G*Gm*e11 - G*De = Gm"""
    e00 = np.zeros_like(mL); e11 = np.zeros_like(mL); De = np.zeros_like(mL)
    for i in range(len(mL)):
        A = np.array([[1, GL[i] * mL[i], -GL[i]], [1, GO[i] * mO[i], -GO[i]], [1, GS[i] * mS[i], -GS[i]]])
        b = np.array([mL[i], mO[i], mS[i]])
        e00[i], e11[i], De[i] = np.linalg.solve(A, b)
    return e00, e11, De

def measure(G, e00, e11, ert):
    return e00 + ert * G / (1 - e11 * G)

def correct(Gm, e00, e11, De):
    return (Gm - e00) / (Gm * e11 - De)

rng = np.random.default_rng(1)
# a plausible raw error box (smooth in f)
e00 = 0.05 * np.exp(-1j * w * 0.3e-9)
e11 = 0.08 * np.exp(-1j * w * 0.5e-9)
ert = 0.8 * np.exp(-2j * w * 1.2e-9)

# ---------------------------------------------------------------- A
print("A: DIY load = 2 x 100 Ohm 0402 in parallel; series parasitic L (mounting on an SMA)")
for L in [0.3e-9, 0.5e-9, 1.0e-9]:
    out = []
    for fx in [433e6, 915e6, 1575e6, 2450e6]:
        GL = gam(50 + 1j * 2 * np.pi * fx * L)
        out.append(f"{fx/1e6:.0f} MHz {-20*np.log10(abs(GL)):5.1f} dB")
    print(f"  L = {L*1e9:.1f} nH: residual directivity " + ", ".join(out))
d915 = -20 * np.log10(abs(gam(50 + 1j * 2 * np.pi * 915e6 * 0.5e-9)))
check("A1 0.5 nH load: ~31 dB at 915 MHz (good enough for a 20 dB RL antenna only with ~1 dB error)", 30 < d915 < 32)

# ---------------------------------------------------------------- B
print("\nB: characterising DIY open/short with a trusted (ideal-known) kit")
tau_d, C_d, L_d = 18e-12, 45e-15 + 2e-27 * f, 15e-12   # true DIY standards (illustrative)
GO_true = open_std(f, tau_d, C_d)
GS_true = -np.exp(-2j * w * tau_d) * (1 - 1j * w * L_d / Z0) / (1 + 1j * w * L_d / Z0) * -1
GS_true = -np.exp(-2j * w * tau_d) * ((1j * w * L_d - Z0) / (1j * w * L_d + Z0)) * -1
# (1) trusted cal (ideal O/S/L known) then measure DIY standards (with small noise)
noise = lambda: 1e-4 * (rng.standard_normal(f.size) + 1j * rng.standard_normal(f.size))
GO_meas = GO_true + noise(); GS_meas = GS_true + noise()
# (2) offset delay from the short's phase, assuming L small: phase = pi - 2 w tau
tau_fit = -np.polyfit(w, np.unwrap(np.angle(-GS_meas)), 1)[0] / 2
# (3) remove that delay from the open and solve for C(f), fit C0..C3
Gp = GO_meas * np.exp(2j * w * tau_fit)
Cf = ((1 - Gp) / (1j * w * Z0 * (1 + Gp))).real
p = np.polyfit(f, Cf, 1)[::-1]          # fit C0 + C1 f only: higher orders are ill-conditioned with noise
C0, C1 = p[0] / 1e-15, p[1] / 1e-27
print(f"  fitted offset delay {tau_fit*1e12:.1f} ps (true {tau_d*1e12:.0f} ps; short L absorbed into delay)")
print(f"  fitted C0 {C0:.1f} fF, C1 {C1:.1f} e-27 F/Hz (true 45 fF, 2 e-27; the 0.3 ps delay error is traded into C)")
check("B1 delay recovered within 1 ps (short inductance 15 pH ~ 0.15 ps of extra delay)", abs(tau_fit - tau_d) < 1e-12)
# (4) DUT accuracy: DIY cal with ideal definitions vs with fitted definitions
Gdut = gam(40 - 10j + 0 * f)                       # RL ~ 16 dB DUT
GL_true = gam(50 + 1j * w * 0.5e-9)                 # DIY load with 0.5 nH
mL, mO, mS = measure(GL_true, e00, e11, ert), measure(GO_true, e00, e11, ert), measure(GS_true, e00, e11, ert)
mD = measure(Gdut, e00, e11, ert)
ideal = sol_terms(mL, mO, mS, 0 * f, 1 + 0 * f, -1 + 0 * f)
fitted = sol_terms(mL, mO, mS, 0 * f, open_std(f, tau_fit, np.polyval(p[::-1], f)),
                   -np.exp(-2j * w * tau_fit) + 0 * f)
GL_meas = GL_true + noise()                          # the load measured on the trusted cal (data-based)
allfit = sol_terms(mL, mO, mS, GL_meas, open_std(f, tau_fit, np.polyval(p[::-1], f)),
                   -np.exp(-2j * w * tau_fit) + 0 * f)
err_ideal = np.abs(correct(mD, *ideal) - Gdut)
err_fit = np.abs(correct(mD, *fitted) - Gdut)
err_all = np.abs(correct(mD, *allfit) - Gdut)
for fx in [433e6, 915e6, 1575e6, 2450e6]:
    i = np.argmin(abs(f - fx))
    print(f"  {fx/1e6:6.0f} MHz: |dGamma| ideal definitions {err_ideal[i]:.4f}; O/S characterised {err_fit[i]:.4f}; "
          f"O/S/L characterised {err_all[i]:.4f}")
i915 = np.argmin(abs(f - 915e6)); i2450 = np.argmin(abs(f - 2450e6))
check("B2 characterising only O/S halves the 2.45 GHz error (the load's 0.5 nH then dominates)",
      0.4 < err_fit[i2450] / err_ideal[i2450] < 0.6)
check("B2b characterising the load too (data-based standard) brings it below 0.005 everywhere", np.max(err_all) < 0.005)
g16 = abs(Gdut[0])
lo, hi = -20 * np.log10(g16 + err_ideal[i915]), -20 * np.log10(g16 - err_ideal[i915])
print(f"  DUT RL {-20*np.log10(g16):.1f} dB read with the ideal-definition DIY kit at 915 MHz: anywhere {lo:.1f}-{hi:.1f} dB")
check("B2c a 16 dB-RL DUT reads ~13.3-20 dB at 915 MHz with an uncharacterised DIY kit", abs(lo - 13.3) < 0.3 and abs(hi - 20.0) < 0.4)
check("B3 at 433 MHz even the ideal-definition DIY kit is within |dGamma| < 0.03", err_ideal[np.argmin(abs(f - 433e6))] < 0.03)

# ---------------------------------------------------------------- C
print("\nC: 'calibrate with a 73 Ohm load' vs 50 Ohm cal + renormalisation")
Zd = 73.1 + 42.5j * (f - 0) / f          # constant illustrative DUT (a lambda/2 dipole at resonance-ish)
Zd = 70.0 + 5.0j + 0 * f
GD = gam(Zd)
mD = measure(GD, e00, e11, ert)
G73_ideal = gam(73.0 + 0 * f)
mO = measure(1 + 0 * f, e00, e11, ert); mS = measure(-1 + 0 * f, e00, e11, ert)
# cal 1: 73 Ohm resistor used as the "load" but the kit still says Gamma_load = 0
t73 = sol_terms(measure(G73_ideal, e00, e11, ert), mO, mS, 0 * f, 1 + 0 * f, -1 + 0 * f)
G_c73 = correct(mD, *t73)
G_renorm = gam(Zd, 73.0)
check("C1 ideal 73 Ohm 'load' cal == exact renormalisation to 73 Ohm (max diff < 1e-12)", np.max(abs(G_c73 - G_renorm)) < 1e-12)
# cal 2: real 73 Ohm part with 0.8 nH series and 0.1 pF shunt
Z73r = 1 / (1 / (73.0 + 1j * w * 0.8e-9) + 1j * w * 0.1e-12)
t73r = sol_terms(measure(gam(Z73r), e00, e11, ert), mO, mS, 0 * f, 1 + 0 * f, -1 + 0 * f)
err73 = np.abs(correct(mD, *t73r) - G_renorm)
for fx in [145e6, 433e6, 915e6]:
    i = np.argmin(abs(f - fx)) if fx >= f[0] else 0
    print(f"  {fx/1e6:5.0f} MHz: real 73 Ohm part -> |dGamma_73| = {err73[i]:.4f}; a 50 Ohm cal + renormalise -> 0 (math only)")
check("C2 a leaded/SMD 73 Ohm part (0.8 nH, 0.1 pF) errs by ~0.01 in Gamma at 915 MHz (a 40 dB-load-class error)",
      0.005 < err73[np.argmin(abs(f - 915e6))] < 0.02)
# readout trap: if the software still assumes Z0 = 50, Z = 50 (1+G)/(1-G) from G_73 is wrong
i = np.argmin(abs(f - 433e6))
Zwrong = 50 * (1 + G_c73[i]) / (1 - G_c73[i])
print(f"  impedance readout with Z0 left at 50 Ohm: {Zwrong:.1f} Ohm (true {Zd[i]:.1f})")
check("C3 leaving the readout at 50 Ohm reports ~48 Ohm for a 70 Ohm DUT", abs(Zwrong.real - 48) < 2)

# ---------------------------------------------------------------- D
print("\nD: UHF (SO-239/PL-259) adapter added after an SMA calibration (modelled as 25 mm of 35 Ohm, er 2.1)")
def line_in(ZL, Zl, length, er, fx):
    b = 2 * np.pi * fx * np.sqrt(er) / c
    t = np.tan(b * length)
    return Zl * (ZL + 1j * Zl * t) / (Zl + 1j * ZL * t)
for fx in [30e6, 145e6, 433e6, 915e6]:
    Gad = gam(line_in(50.0, 35.0, 0.025, 2.1, fx))
    print(f"  {fx/1e6:5.0f} MHz: adapter |Gamma| {abs(Gad):.3f} -> effective directivity {-20*np.log10(abs(Gad)):5.1f} dB")
d433 = -20 * np.log10(abs(gam(line_in(50.0, 35.0, 0.025, 2.1, 433e6))))
d30 = -20 * np.log10(abs(gam(line_in(50.0, 35.0, 0.025, 2.1, 30e6))))
check("D1 harmless at HF (> 35 dB at 30 MHz) but ~17-20 dB at 433 MHz", d30 > 35 and 15 < d433 < 21)

# ---------------------------------------------------------------- E
print("\nE: frequency-reference error")
for ppm in [2.5, 10, 20, 50]:
    print(f"  {ppm:4.1f} ppm: {433.92e6*ppm*1e-6/1e3:6.2f} kHz at 433.92 MHz, {915e6*ppm*1e-6/1e3:6.2f} kHz at 915 MHz")
Q = 10000; bw = 433.92e6 / Q
df = 433.92e6 * 20e-6
print(f"  433.92 MHz resonator, Q {Q}: 3 dB BW {bw/1e3:.1f} kHz; a 20 ppm VNA reference misplaces it by {df/bw*100:.0f} % of its BW")
tau_rt = 2 * 10 / (0.66 * c)
dphi = 360 * df * tau_rt
print(f"  10 m of v_f 0.66 coax (round trip {tau_rt*1e9:.0f} ns): phase error from 8.7 kHz = {dphi:.2f} deg")
check("E1 20 ppm = 8.68 kHz at 433.92 MHz", abs(df - 8678.4) < 1)
check("E2 phase error on a 10 m cable < 0.5 deg (irrelevant for antennas)", dphi < 0.5)
check("E3 but it is ~20 % of a Q-10000 resonator's bandwidth", 0.15 < df / bw < 0.25)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
