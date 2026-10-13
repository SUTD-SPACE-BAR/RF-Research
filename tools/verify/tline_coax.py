#!/usr/bin/env python3
"""
Verification for kb/03-transmission-lines-matching/coax-and-cables.md

Checks / computes:
  1. Z0 = (60/sqrt(er)) ln(D/d) and L, C vs scikit-rf Coaxial; datasheet geometries -> Z0 and VF consistency.
  2. Optimum diameter ratios for fixed outer diameter: min conductor loss (b/a = 3.591, 76.7 ohm air),
     max power at breakdown field (b/a = sqrt(e), 30.0 ohm), max voltage (b/a = e, 60 ohm);
     the same with PE/PTFE dielectric.
  3. Datasheet attenuation tables fitted to A(f) = k1 sqrt(f) + k2 f; interpolation to 433/868/915/1575/2450/5800 MHz.
  4. Theory (smooth copper + tan-delta) vs datasheet for solid-conductor cables.
  5. TE11 cutoff from geometry vs datasheet maximum frequency.
  6. Average-power rating x attenuation ~ constant (thermal limit) for LMR-400 / LMR-240.
  7. Ground-station and flight-harness examples (loss budgets).

Run: python3 tools/verify/tline_coax.py
"""
import numpy as np
from scipy.optimize import minimize_scalar, least_squares
import skrf as rf
import warnings

warnings.filterwarnings("ignore")
C0 = 299_792_458.0
MU0 = 4e-7 * np.pi
EPS0 = 1 / (MU0 * C0**2)
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def z0_coax(d, D, er):
    return 60 / np.sqrt(er) * np.log(D / d)


# ---------------------------------------------------------------- 1. formula vs skrf and datasheets
f = rf.Frequency(1, 1, 1, unit="GHz")
cx = rf.media.Coaxial(frequency=f, Dint=0.91e-3, Dout=3.0e-3, epsilon_r=2.07, tan_delta=0, sigma=1e20, z0_port=50)
check("Z0 = 60/sqrt(er) ln(D/d) == skrf Coaxial within 0.1 % (60 approximates eta0/2pi = 59.96)",
      abs(cx.z0[0].real - z0_coax(0.91, 3.0, 2.07)) / cx.z0[0].real < 1e-3,
      f"(formula {z0_coax(0.91, 3.0, 2.07):.3f} ohm, skrf {cx.z0[0].real:.3f} ohm)")
# datasheet geometries: (name, inner dia mm, dielectric OD mm, VF, stated Z0, stated C pF/m)
cables = [
    ("LMR-400", 2.74, 7.24, 0.85, 50, 78.41),
    ("LMR-240", 1.42, 3.81, 0.84, 50, 79.4),
    ("LMR-195", 0.94, 2.79, 0.80, 50, 83.33),
    ("RG-58 (Belden 8240)", 0.838, 2.95, 0.66, 52, 93.5),
    ("RG-174 (Fairview)", 0.48, 1.52, 0.66, 50, 101.97),
    ("RG-316 (Fairview)", 0.51, 1.52, 0.69, 50, 96.46),
    ("RG-402 (Pasternack)", 0.91, 2.98, 0.695, 50, None),
    ("RG-405 (Pasternack)", 0.51, 1.68, 0.695, 50, None),
]
print("   cable                 d(mm) D(mm)  VF    er     Z0(geom)  C(geom) pF/m  1/(vp C_ds)  stated")
for name, d, D, vf, zs, cds in cables:
    er = 1 / vf**2
    z = z0_coax(d, D, er)
    Cg = 2 * np.pi * EPS0 * er / np.log(D / d)
    zc = 1 / (vf * C0 * cds * 1e-12) if cds else float("nan")
    print(f"   {name:21s} {d:5.3f} {D:5.2f}  {vf:.3f} {er:.3f}  {z:7.2f}   {Cg*1e12:7.1f}        {zc:6.2f}      {zs}")
z_lmr = z0_coax(2.74, 7.24, 1 / 0.85**2)
check("LMR-400 geometry + VF reproduce ~50 ohm (within 2 %)", abs(z_lmr - 50) < 1.0, f"({z_lmr:.2f} ohm)")
# RG-402 D is not in the fetched datasheet excerpt: 0.141" OD semi-rigid has a 0.1175" (2.98 mm) dielectric (MIL-DTL-17)

# ---------------------------------------------------------------- 2. optimum ratios
x_loss = minimize_scalar(lambda x: (1 + x) / np.log(x), bounds=(1.1, 20), method="bounded").x
x_pow = minimize_scalar(lambda x: -np.log(x) / x**2, bounds=(1.01, 20), method="bounded").x
x_volt = minimize_scalar(lambda x: -np.log(x) / x, bounds=(1.01, 20), method="bounded").x
print(f"   min conductor loss: b/a = {x_loss:.4f} -> Z0(air) = {60*np.log(x_loss):.2f} ohm; "
      f"PE (2.25): {60*np.log(x_loss)/1.5:.2f}; PTFE (2.07): {60*np.log(x_loss)/np.sqrt(2.07):.2f}")
print(f"   max power at breakdown: b/a = {x_pow:.4f} -> Z0(air) = {60*np.log(x_pow):.2f} ohm")
print(f"   max voltage at breakdown: b/a = {x_volt:.4f} -> Z0(air) = {60*np.log(x_volt):.2f} ohm")
check("min-loss ratio 3.591 (ln x = 1 + 1/x), Z0 = 76.7 ohm in air", abs(x_loss - 3.5911) < 1e-3 and abs(60 * np.log(x_loss) - 76.7) < 0.1)
check("max-power ratio sqrt(e), Z0 = 30.0 ohm in air", abs(x_pow - np.sqrt(np.e)) < 1e-3 and abs(60 * np.log(x_pow) - 30.0) < 0.05)
check("max-voltage ratio e, Z0 = 60.0 ohm in air", abs(x_volt - np.e) < 1e-3)
# how flat is the loss optimum? loss at 50 ohm (air) relative to optimum
rel = lambda z: ((1 + np.exp(z / 60)) / np.log(np.exp(z / 60))) / ((1 + x_loss) / np.log(x_loss))
print(f"   conductor loss penalty (air line, fixed D): 50 ohm {100*(rel(50)-1):.1f} %, 60 ohm {100*(rel(60)-1):.1f} %,"
      f" 93 ohm {100*(rel(93)-1):.1f} %; power-handling at 50 vs 30 ohm: "
      f"{(np.log(np.exp(50/60))/np.exp(50/60)**2)/(np.log(np.sqrt(np.e))/np.e):.3f}")
check("50-ohm air line loses only ~10 % more than the 77-ohm optimum", 0.05 < rel(50) - 1 < 0.15)
# PE-filled: loss optimum is still b/a = 3.591 (-> 51 ohm), which is one reason 50-52 ohm PE cables are 'natural'
check("with solid PE the min-loss geometry is ~51 ohm", abs(60 * np.log(x_loss) / 1.5 - 51.1) < 0.2)

# ---------------------------------------------------------------- 3. datasheet fits
# attenuation data: dB/100 m vs MHz (from datasheets fetched 2026-09-27)
data = {
    "LMR-400": ([50, 150, 220, 450, 900, 1500, 1800, 2000, 2500, 5800],
                [2.95, 4.92, 6.23, 8.86, 12.8, 16.73, 18.7, 19.69, 22.31, 35.43]),
    "LMR-240": ([50, 150, 220, 450, 900, 1500, 1800, 2000, 2500, 5800],
                [5.58, 9.84, 12.14, 17.39, 24.93, 32.48, 35.76, 37.73, 42.32, 66.93]),
    "LMR-195": ([50, 150, 220, 450, 900, 1500, 1800, 2000, 2500, 5800],
                [8.2, 14.44, 17.72, 25.59, 36.42, 47.57, 52.49, 55.45, 62.34, 98.1]),
    "RG-58 (Belden 8240)": ([10, 50, 100, 200, 400, 700, 900, 1000],
                            [3.61, 8.20, 12.47, 18.37, 27.56, 38.39, 44.95, 47.57]),
    "RG-174 (Fairview)": ([100, 400, 1000], [27.56, 62.34, 104.99]),
    "RG-316 (Fairview)": ([50, 100, 400, 1000, 3000], [24.61, 36.09, 68.9, 124.67, 190.29]),
    "RG-402 (Pasternack)": ([500, 1000, 10000, 18000], [24.93, 36.42, 142.39, 208.66]),
    "RG-405 (Pasternack)": ([1000, 10000, 20000], [72.18, 262.47, 393.7]),
    "U.FL 1.13 mm (Hirose)": ([3000, 6000], [373.0, 544.0]),
}
fits = {}
print("   fitted A(f) = k1 sqrt(f) + k2 f  [dB/100 m, f in MHz]; interpolated dB/100 m at:")
print("   cable                   k1       k2        433    868    915   1575   2450   5800   max fit err")
for name, (fm, a) in data.items():
    fm, a = np.array(fm, float), np.array(a, float)
    A = np.vstack([np.sqrt(fm), fm]).T
    (k1, k2), *_ = np.linalg.lstsq(A, a, rcond=None)
    k2 = max(k2, 0.0)
    fits[name] = (k1, k2)
    pred = k1 * np.sqrt(fm) + k2 * fm
    err = np.max(np.abs(pred - a) / a)
    row = [k1 * np.sqrt(x) + k2 * x for x in [433, 868, 915, 1575, 2450, 5800]]
    print(f"   {name:22s} {k1:7.4f}  {k2:8.5f}  " + "  ".join(f"{v:5.1f}" for v in row) + f"    {err*100:4.1f} %")
fit_err = {n: np.max(np.abs(fits[n][0] * np.sqrt(np.array(d[0])) + fits[n][1] * np.array(d[0]) - np.array(d[1])) / np.array(d[1]))
           for n, d in data.items() if len(d[0]) > 2}
check("k1 sqrt(f) + k2 f fits every multi-point table to < 5 % except RG-316 (Fairview)",
      all(v < 0.05 for n, v in fit_err.items() if not n.startswith("RG-316")))
check("RG-316 (Fairview) table is NOT consistent with k1 sqrt(f) + k2 f (3 GHz point rises slower than sqrt f) -> flag",
      fit_err["RG-316 (Fairview)"] > 0.08, f"(fit error {fit_err['RG-316 (Fairview)']*100:.1f} %; 1->3 GHz ratio "
      f"{190.29/124.67:.2f} vs sqrt(3) = 1.73)")
# for the inconsistent RG-316 table use piecewise log-log interpolation instead of the fitted law
fr316, a316 = np.array(data["RG-316 (Fairview)"][0], float), np.array(data["RG-316 (Fairview)"][1], float)
loglog = lambda fx: np.exp(np.interp(np.log(fx), np.log(fr316), np.log(a316)))
print("   RG-316 (Fairview) piecewise log-log interpolation, dB/100 m: " +
      ", ".join(f"{x:.0f} MHz {loglog(x):.1f}" for x in [433, 868, 915, 1575, 2450]))
# Times Microwave's own LMR-400 equation (k1 = 0.12229, k2 = 0.00026 in dB/100 ft, f in MHz)
lmr_eq = lambda fmhz: (0.122290 * np.sqrt(fmhz) + 0.000260 * fmhz) * 100 / 30.48
check("Times LMR-400 equation reproduces its own table within 3 %",
      np.max(np.abs(lmr_eq(np.array(data['LMR-400'][0])) - np.array(data['LMR-400'][1])) / np.array(data['LMR-400'][1])) < 0.03)

# ---------------------------------------------------------------- 4. theory vs datasheet (solid copper, smooth)
def theory_db100m(d, D, er, tand, fmhz, sigma=5.8e7):
    fhz = fmhz * 1e6
    Rs = np.sqrt(np.pi * fhz * MU0 / sigma)
    R = Rs / (2 * np.pi) * (2 / (d * 1e-3) + 2 / (D * 1e-3))
    z = z0_coax(d, D, er)
    ac = R / (2 * z)
    ad = np.pi * np.sqrt(er) * tand * fhz / C0
    return (ac + ad) * 20 / np.log(10) * 100


ratios = []
for name, d, D, er, tand in [("LMR-400", 2.74, 7.24, 1 / 0.85**2, 1e-4), ("RG-402 (Pasternack)", 0.91, 2.98, 2.07, 2e-4)]:
    fm = np.array(data[name][0], float)
    th = theory_db100m(d, D, er, tand, fm)
    ratio = np.array(data[name][1]) / th
    ratios += list(ratio)
    print(f"   {name}: datasheet/theory(smooth Cu, assumed tand) ratio = {np.round(ratio, 2)}")
check("foil/solid-shield cables (LMR-400, RG-402) are within 0-20 % of smooth-copper theory",
      min(ratios) > 0.98 and max(ratios) < 1.2, f"(range {min(ratios):.2f}-{max(ratios):.2f}; braided RG-58: 1.10-1.26, see telegrapher script)")

# ---------------------------------------------------------------- 5. TE11 cutoff
for name, d, D, vf, fmax in [("LMR-400", 2.74, 7.24, 0.85, 6e9), ("RG-402 (Pasternack)", 0.91, 2.98, 0.695, 34e9),
                             ("RG-405 (Pasternack)", 0.51, 1.68, 0.695, 40e9), ("RG-316 (Fairview)", 0.51, 1.52, 0.69, 3e9)]:
    er = 1 / vf**2
    fc = C0 / (np.pi * np.sqrt(er) * (d + D) / 2 * 1e-3)
    print(f"   {name}: TE11 cutoff ~ {fc/1e9:.1f} GHz (datasheet max {fmax/1e9:.0f} GHz)")
fc400 = C0 / (np.pi * 0.85**-1 * (2.74 + 7.24) / 2e3)
check("LMR-400 TE11 estimate ~16.3 GHz vs datasheet 16.2 GHz", abs(fc400 / 1e9 - 16.2) < 0.3, f"({fc400/1e9:.2f} GHz)")

# ---------------------------------------------------------------- 6. power x attenuation ~ const
p400 = np.array([2570, 1470, 1200, 830, 580, 440, 400, 370, 330, 210])
a400 = np.array(data["LMR-400"][1])
prod = p400 * a400
print(f"   LMR-400 P_avg x alpha (W dB/100 m): {np.round(prod).astype(int)}")
check("LMR-400: average-power rating x attenuation constant within 10 % (thermal limit)",
      np.ptp(prod) / prod.mean() < 0.10, f"(mean {prod.mean():.0f} W dB/100 m -> {prod.mean()/100:.1f} W dB/m dissipated)")
p240 = np.array([1150, 660, 540, 380, 260, 200, 180, 170, 150, 100])
prod240 = p240 * np.array(data["LMR-240"][1])
check("LMR-240: same thermal-limit behaviour", np.ptp(prod240) / prod240.mean() < 0.12, f"(mean {prod240.mean():.0f})")

# ---------------------------------------------------------------- 7. examples
def loss_db(name, fmhz, length_m):
    if name.startswith("RG-316"):
        return loglog(fmhz) / 100 * length_m
    k1, k2 = fits[name]
    return (k1 * np.sqrt(fmhz) + k2 * fmhz) / 100 * length_m


print("   Ground-station feeder, 10 m and 20 m:")
for fmhz in [433, 915]:
    for name in ["LMR-400", "LMR-240", "LMR-195", "RG-58 (Belden 8240)"]:
        l10, l20 = loss_db(name, fmhz, 10), loss_db(name, fmhz, 20)
        print(f"     {fmhz} MHz {name:21s}: 10 m {l10:4.2f} dB (range x{10**(-l10/20):.2f}), 20 m {l20:4.2f} dB")
print("   Flight harness / pigtails:")
for name, L in [("U.FL 1.13 mm (Hirose)", 0.10), ("U.FL 1.13 mm (Hirose)", 0.20), ("RG-316 (Fairview)", 0.30), ("RG-174 (Fairview)", 0.30)]:
    for fmhz in [433, 915, 1575.42]:
        print(f"     {name:22s} {L*100:4.0f} cm @ {fmhz:7.2f} MHz: {loss_db(name, fmhz, L):.3f} dB")
check("10 cm of 1.13 mm micro-coax at 1575 MHz costs ~0.25-0.3 dB", 0.2 < loss_db("U.FL 1.13 mm (Hirose)", 1575.42, 0.1) < 0.32)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
