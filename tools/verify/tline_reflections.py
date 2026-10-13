#!/usr/bin/env python3
"""
Verification for kb/03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md

Checks:
  1. Gamma / VSWR / return loss / mismatch loss / transmitted-power conversion table.
  2. |Gamma(z)| is constant along a lossless line (so true SWR doesn't depend on where you look),
     and the standing-wave Vmax/Vmin ratio equals the VSWR; position of first minimum.
  3. Lossy line masks SWR: RL_in = RL_load + 2*A (A = matched one-way loss in dB);
     example: open-ended 10 m RG-58 at 433 MHz.
  4. Total loss of a mismatched lossy line (ARRL formula) vs scikit-rf zl_2_total_loss and vs
     a direct power calculation.
  5. "Reflected power is dissipated in the source": show it is NOT true for a Thevenin source
     (dissipation depends on the phase of Gamma), and power delivered = P_avail (1-|Gamma|^2)
     for a Z0 source.
  6. Voltage stress: peak voltage on the line for P_fwd and |Gamma| (2 W E22 module example).
  7. For a real resistive load, VSWR = max(R/Z0, Z0/R).

Run: python3 tools/verify/tline_reflections.py
"""
import numpy as np
import skrf as rf
import skrf.tlineFunctions as tlf

ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def gamma_from_z(Z, Z0=50.0):
    return (Z - Z0) / (Z + Z0)


def vswr(G):
    G = np.abs(G)
    return (1 + G) / (1 - G)


def rl_db(G):
    return -20 * np.log10(np.abs(G))


def ml_db(G):
    return -10 * np.log10(1 - np.abs(G) ** 2)


# ---------------------------------------------------------------- 1. conversion table
print("  VSWR   |Gamma|   RL(dB)  refl.pwr%  ML(dB)   Ptrans%")
table = []
for s in [1.01, 1.05, 1.1, 1.2, 1.25, 1.5, 1.92, 2.0, 2.5, 3.0, 4.0, 5.0, 10.0]:
    G = (s - 1) / (s + 1)
    row = (s, G, rl_db(G), 100 * G**2, ml_db(G), 100 * (1 - G**2))
    table.append(row)
    print("  {:5.2f}  {:6.4f}  {:7.2f}   {:7.3f}  {:6.3f}   {:6.2f}".format(*row))
# spot values against well-known table entries
check("VSWR 2.0 -> RL 9.54 dB, ML 0.51 dB, 11.1% reflected",
      abs(rl_db(1 / 3) - 9.542) < 1e-3 and abs(ml_db(1 / 3) - 0.512) < 1e-3)
check("RL 10 dB -> VSWR 1.925", abs(vswr(10 ** (-10 / 20)) - 1.925) < 1e-3)
check("VSWR 1.5 -> RL 13.98 dB, ML 0.177 dB",
      abs(rl_db(0.2) - 13.979) < 1e-3 and abs(ml_db(0.2) - 0.177) < 1e-3)
check("skrf Gamma0_2_swr agrees", np.isclose(tlf.Gamma0_2_swr(0.2), 1.5))

# ---------------------------------------------------------------- 2. standing waves, lossless
Z0 = 50.0
ZL = 25 + 40j
GL = gamma_from_z(ZL, Z0)
beta = 2 * np.pi / 1.0  # lambda = 1 m (normalised)
d = np.linspace(0, 1.0, 20001)  # distance from load toward generator
Gd = GL * np.exp(-2j * beta * d)
check("|Gamma(d)| constant on lossless line", np.ptp(np.abs(Gd)) < 1e-12)
V = 1 * (np.exp(1j * beta * d) + GL * np.exp(-1j * beta * d))  # V+ = 1
ratio = np.abs(V).max() / np.abs(V).min()
check("Vmax/Vmin == VSWR", abs(ratio - vswr(GL)) < 1e-4, f"({ratio:.4f} vs {vswr(GL):.4f})")
dmin = d[np.argmin(np.abs(V[: len(d) // 2]))]
phiL = np.angle(GL)
dmin_theory = ((phiL + np.pi) / (2 * beta)) % 0.5
check("first voltage minimum at d = (phi_L + pi)/(2 beta)", abs(dmin - dmin_theory) < 1e-4,
      f"({dmin:.4f} vs {dmin_theory:.4f} wavelengths)")
# Vmax / Vmin separated by lambda/4
dmax = d[np.argmax(np.abs(V[: len(d) // 2]))]
check("voltage max and min are lambda/4 apart", abs(abs(dmax - dmin) - 0.25) < 1e-3)

# ---------------------------------------------------------------- 3. lossy line masks SWR
freq = rf.Frequency(433, 433, 1, unit="MHz")
# RG-58: 8.4 dB/100ft @ 400 MHz scaled by sqrt(f) (conductor-dominated) -> 433 MHz
a_db_per_m = 8.4 / 30.48 * np.sqrt(433 / 400)
A = a_db_per_m * 10.0  # 10 m
print(f"      RG-58 matched loss at 433 MHz ~ {a_db_per_m:.3f} dB/m -> 10 m: {A:.2f} dB")
NP2DB = 20 / np.log(10)  # 8.6859 dB per neper
alpha = a_db_per_m / NP2DB
beta433 = 2 * np.pi * 433e6 / (0.66 * 299792458)
cx = rf.media.DefinedGammaZ0(frequency=freq, gamma=alpha + 1j * beta433, z0=50)
line = cx.line(10.0, unit="m")
open_ = cx.open()
short = cx.short()
for name, ld, rl_load in [("open", open_, 0.0), ("short", short, 0.0)]:
    ntw = line ** ld
    rl_in = -ntw.s_db[0, 0, 0]
    check(f"10 m RG-58 + {name}: RL_in = RL_load + 2A", abs(rl_in - (rl_load + 2 * A)) < 1e-6,
          f"(RL_in = {rl_in:.2f} dB -> VSWR at radio = {vswr(10**(-rl_in/20)):.2f} with a {name} at the far end!)")
# a real antenna with VSWR 3 at the load
G3 = 0.5
ld3 = cx.load(G3)
rl3 = -(line ** ld3).s_db[0, 0, 0]
check("VSWR 3.0 antenna seen through 10 m RG-58", abs(rl3 - (rl_db(G3) + 2 * A)) < 1e-6,
      f"(radio sees RL {rl3:.2f} dB = VSWR {vswr(10**(-rl3/20)):.2f})")

# ---------------------------------------------------------------- 4. total loss with mismatch
def total_loss_db(A_db, GLmag):
    a = 10 ** (A_db / 10)
    return 10 * np.log10((a**2 - GLmag**2) / (a * (1 - GLmag**2)))


tl = total_loss_db(A, G3)
# direct: power into line / power into load, with V+ at load = 1
Vp_load = 1.0
P_load = (abs(Vp_load) ** 2) * (1 - G3**2) / (2 * Z0)
# at input the forward wave is larger by e^{alpha l}, the reflected smaller by e^{-alpha l}
Pin = (np.exp(2 * alpha * 10) - G3**2 * np.exp(-2 * alpha * 10)) / (2 * Z0)
tl_direct = 10 * np.log10(Pin / P_load)
check("ARRL mismatched-line loss formula == direct power bookkeeping", abs(tl - tl_direct) < 1e-9,
      f"({tl:.3f} dB vs matched {A:.3f} dB; extra {tl - A:.3f} dB)")
# scikit-rf's tlineFunctions.zl_2_total_loss (uses the same bookkeeping)
ZL3 = Z0 * (1 + G3) / (1 - G3)
tl_skrf = tlf.zl_2_total_loss(z0=Z0, zl=ZL3, theta=(alpha + 1j * beta433) * 10.0)
tl_skrf_db = 10 * np.log10(float(np.real(tl_skrf)))
check("scikit-rf zl_2_total_loss (Stearns K6OIK form) agrees", abs(tl_skrf_db - tl) < 1e-6,
      f"(skrf {tl_skrf_db:.3f} dB)")
# the extra loss depends only on |Gamma_L| and A, not on line phase: vary the load phase
tls = []
for ph in np.linspace(0, 2 * np.pi, 13)[:-1]:
    Zx = Z0 * (1 + G3 * np.exp(1j * ph)) / (1 - G3 * np.exp(1j * ph))
    tls.append(10 * np.log10(float(np.real(tlf.zl_2_total_loss(z0=Z0, zl=Zx, theta=(alpha + 1j * beta433) * 10.0)))))
check("mismatched-line total loss independent of load phase (real Z0)", np.ptp(tls) < 1e-9)

# ---------------------------------------------------------------- 5. where does "reflected power" go?
Vs = 2 * np.sqrt(2 * Z0)  # source EMF (peak) giving P_avail = |Vs|^2/(8 R) = 1 W
Rs = Z0
P_av = abs(Vs) ** 2 / (8 * Rs)
print(f"      Thevenin source Vs={Vs:.2f} V pk, Rs = {Rs} ohm, P_avail = {P_av:.3f} W")
print("      load             |G|   P_load   P_refl=|G|^2 P_av   P_diss_in_Rs")
res = []
for Zl in [50, 0.0, 1e12, 150, 50 / 3, 50 + 50j, 50 - 50j]:
    Zl = complex(Zl)
    I = Vs / (Rs + Zl)
    P_load = 0.5 * abs(I) ** 2 * Zl.real
    P_rs = 0.5 * abs(I) ** 2 * Rs
    G = gamma_from_z(Zl, Z0) if abs(Zl) < 1e11 else 1.0
    res.append((Zl, abs(G), P_load, abs(G) ** 2 * P_av, P_rs))
    print(f"      {str(np.round(Zl,1)):16s} {abs(G):.3f}  {P_load:6.3f}   {abs(G)**2*P_av:6.3f}            {P_rs:6.3f}")
check("P_load = P_avail (1 - |Gamma|^2) for Z0 source (all loads)",
      all(abs(r[2] - P_av * (1 - r[1] ** 2)) < 1e-9 for r in res))
# same |Gamma| = 0.5 (150 ohm vs 16.7 ohm) but different source dissipation:
r150 = [r for r in res if abs(r[0] - 150) < 1e-9][0]
r17 = [r for r in res if abs(r[0] - 50 / 3) < 1e-6][0]
check("same |Gamma|, different source dissipation (reflected power is not simply 'absorbed by the PA')",
      abs(r150[1] - r17[1]) < 1e-9 and abs(r150[4] - r17[4]) > 0.5,
      f"(150 ohm: {r150[4]:.3f} W, 16.7 ohm: {r17[4]:.3f} W)")

# ---------------------------------------------------------------- 6. voltage stress
P_fwd = 2.0  # W, E22-400T33D class
Vfwd = np.sqrt(2 * P_fwd * Z0)
for Gm in [0.0, 0.2, 0.5, 1.0]:
    print(f"      P_fwd = 2 W, |Gamma| = {Gm}: V+ = {Vfwd:.2f} V pk, Vmax = {Vfwd*(1+Gm):.2f} V pk, "
          f"Imax = {Vfwd/Z0*(1+Gm)*1e3:.0f} mA pk")
check("2 W into 50 ohm is 14.14 V peak", abs(Vfwd - 14.142) < 1e-3)

# ---------------------------------------------------------------- 7. resistive loads
for R in [12.5, 25, 100, 200]:
    check(f"R = {R} ohm: VSWR = max(R/Z0, Z0/R)", abs(vswr(gamma_from_z(R)) - max(R / 50, 50 / R)) < 1e-12)

# ---------------------------------------------------------------- 8. meter reference != line Z0
# A 50-ohm-referenced SWR meter/VNA looking into a lossless 75 ohm line (or 52 ohm RG-58) terminated
# in a 50 ohm load: the *measured* SWR varies with line length (period lambda/2), even though
# nothing about the load changed.
Zl = 50.0
for Zc in [75.0, 52.0]:
    th = np.linspace(0, np.pi, 721)
    Zin = Zc * (Zl + 1j * Zc * np.tan(th)) / (Zc + 1j * Zl * np.tan(th))
    sw = vswr(gamma_from_z(Zin, 50.0))
    print(f"      {Zc:.0f} ohm line into 50 ohm load, 50 ohm meter: measured SWR ranges {sw.min():.3f} .. {sw.max():.3f}")
    check(f"{Zc:.0f} ohm line: measured SWR swings with length and peaks at (Zc/50)^2 at lambda/4",
          abs(sw.max() - (Zc / 50) ** 2) < 1e-3 and abs(sw.min() - 1) < 1e-6)

# ---------------------------------------------------------------- 9. 915 MHz example
# E220-900T30D (1 W) -> 3 m RG-58 -> antenna with VSWR 2.5.  RG-58 at 915 MHz ~ 13.8 dB/100 ft
a915 = (13.7 + (14.5 - 13.7) * 15 / 100) / 30.48   # interpolate Belden 900 -> 1000 MHz
A915 = a915 * 3
Gant = (2.5 - 1) / 3.5
rl_radio = rl_db(Gant) + 2 * A915
tl915 = total_loss_db(A915, Gant)
P_ant = 1.0 * 10 ** (-tl915 / 10)
print(f"      915 MHz: 3 m RG-58 matched loss {A915:.2f} dB; antenna VSWR 2.5 (RL {rl_db(Gant):.2f} dB);"
      f" radio sees RL {rl_radio:.2f} dB = VSWR {vswr(10**(-rl_radio/20)):.2f};"
      f" total loss {tl915:.2f} dB; mismatch loss {ml_db(Gant):.2f} dB; radiated (if 100% eff) {P_ant:.3f} W")
Gin = 10 ** (-rl_radio / 20)
P_ant_true = 1.0 * (1 - Gin**2) * 10 ** (-tl915 / 10)     # 50-ohm radio, no tuner
P_ant_alt = 1.0 * 10 ** (-A915 / 10) * (1 - Gant**2)       # |S21|^2 (1-|GL|^2) for a matched line
print(f"      power reaching a 1 W-available radio's antenna: {P_ant_true:.3f} W "
      f"({10*np.log10(P_ant_true):.2f} dB); cross-check |S21|^2(1-|GL|^2) = {P_ant_alt:.3f} W")
check("915 MHz example: radio-side VSWR better than antenna VSWR", vswr(Gin) < 2.5)
check("915 MHz example: two power bookkeepings agree", abs(P_ant_true - P_ant_alt) < 1e-9)
# range change for a dB change in free space: d ~ 10^(dB/20)
print(f"      0.5 dB less EIRP -> free-space range x {10**(-0.5/20):.3f}; 3 dB -> x {10**(-3/20):.3f}")

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
