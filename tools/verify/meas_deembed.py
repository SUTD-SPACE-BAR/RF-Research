#!/usr/bin/env python3
"""
meas_deembed.py -- numerical checks for kb/17-test-measurement/fixtures-and-deembedding.md

1. 2x-thru de-embedding (IEEE P370, scikit-rf IEEEP370_SE_NZC_2xThru) of a symmetric SMA-launch +
   microstrip fixture; DUT = 0402 inductor model. Compare: raw, port extension (delay only),
   exact T-matrix de-embedding with the true fixture, and 2x-thru de-embedding.
2. Sensitivity of 2x-thru to fixture asymmetry (left launch != right launch).
3. One-port open/short compensation (LCR-meter style) for a part soldered at the end of a pigtail:
   Z_dut = (Z_m - Z_s) / (1 - (Z_m - Z_s) Y_o) -- exact for a series-Z_s/shunt-Y_o residual model.
4. TRL line plan for a JLCPCB fixture: lambda/4 lines covering 20-160 deg, multiline plan for 0.3-6 GHz.

Run: python3 tools/verify/meas_deembed.py
"""
import numpy as np
import skrf as rf
from skrf.media import DefinedGammaZ0
from skrf.calibration.deembedding import IEEEP370_SE_NZC_2xThru

C0 = 299792458.0
Z0 = 50.0
freq = rf.Frequency(0.01, 6.0, 600, 'GHz')     # P370 needs a uniform grid starting near DC
med = DefinedGammaZ0(freq, z0=50)
f = freq.f


def ms_line(length_m, z=50.0, eeff=3.3, loss_db_m_1ghz=3.0):
    alpha = loss_db_m_1ghz * np.sqrt(f / 1e9) / 8.686
    beta = 2 * np.pi * f * np.sqrt(eeff) / C0
    return DefinedGammaZ0(freq, z0_port=50, z0=z, gamma=alpha + 1j * beta).line(length_m, 'm')


def launch(c_pf=0.25, l_nh=0.3):
    return med.shunt_capacitor(c_pf * 1e-12) ** med.inductor(l_nh * 1e-9)


def db(x):
    return 20 * np.log10(np.abs(x))


# fixture half: SMA launch (0.25 pF shunt + 0.3 nH) + 15 mm of 50-ohm microstrip
fixL = launch() ** ms_line(0.015)
fixR = ms_line(0.015) ** launch()
# DUT: 0402 10 nH inductor, series R 1 ohm, parallel C 0.08 pF (SRF ~ 5.6 GHz), mounted in series
def series_inductor_model(L=10e-9, R=1.0, Cp=0.08e-12):
    w = 2 * np.pi * f
    zl = R + 1j * w * L
    zc = 1 / (1j * w * Cp)
    z = zl * zc / (zl + zc)
    s = np.zeros((len(f), 2, 2), complex)
    s[:, 0, 0] = s[:, 1, 1] = z / (z + 2 * Z0)
    s[:, 0, 1] = s[:, 1, 0] = 2 * Z0 / (z + 2 * Z0)
    return rf.Network(frequency=freq, s=s), z
dut, z_true = series_inductor_model()
meas = fixL ** dut ** fixR
thru2x = fixL ** fixR

def z_series(n):
    s21 = n.s[:, 1, 0]
    return 2 * Z0 * (1 / s21 - 1)

print("=== 1. De-embedding a series 0402 inductor from a symmetric fixture ===")
dm = IEEEP370_SE_NZC_2xThru(dummy_2xthru=thru2x, name='2x')
dut_p370 = dm.deembed(meas)
dut_exact = fixL.inv ** meas ** fixR.inv
# port extension: remove only the delay of each half (line + launch approximated as delay)
tau = 0.015 * np.sqrt(3.3) / C0
pe = meas.copy()
pe.s = meas.s * np.exp(1j * 2 * np.pi * f * tau * 2)[:, None, None]   # rough: remove 2 x one-way delay on S21
for fq in [0.433e9, 0.915e9, 2.45e9, 5.0e9]:
    k = np.argmin(np.abs(f - fq))
    L_of = lambda z: np.imag(z) / (2 * np.pi * f[k]) * 1e9
    print(f"  {fq/1e9:5.3f} GHz: true X/w = {L_of(z_true[k]):6.2f} nH | raw {L_of(z_series(meas)[k]):6.2f} | "
          f"port-ext {L_of(z_series(pe)[k]):6.2f} | P370 2x-thru {L_of(z_series(dut_p370)[k]):6.2f} | exact {L_of(z_series(dut_exact)[k]):6.2f}")
err = np.max(np.abs(dut_p370.s[f < 5e9] - dut.s[f < 5e9]))
print(f"  P370 2x-thru: max |S_err| below 5 GHz = {err:.2e}")

print("\n=== 2. 2x-thru with an asymmetric fixture (right launch 0.35 pF instead of 0.25 pF) ===")
fixR_bad = ms_line(0.015) ** launch(c_pf=0.35)
meas_bad = fixL ** dut ** fixR_bad
thru_bad = fixL ** fixR_bad
dm_bad = IEEEP370_SE_NZC_2xThru(dummy_2xthru=thru_bad, name='2x-asym')
dut_bad = dm_bad.deembed(meas_bad)
for fq in [0.915e9, 2.45e9, 5.0e9]:
    k = np.argmin(np.abs(f - fq))
    print(f"  {fq/1e9:5.3f} GHz: |S11| true {db(dut.s[k,0,0]):6.2f} dB, de-embedded {db(dut_bad.s[k,0,0]):6.2f} dB; "
          f"L {np.imag(z_series(dut_bad)[k])/(2*np.pi*f[k])*1e9:6.2f} nH (true {np.imag(z_true[k])/(2*np.pi*f[k])*1e9:.2f})")
print("  -> 2x-thru assumes FIX-1 = mirror(FIX-2); verify symmetry (TDR of the 2x-thru) or use TRL")

print("\n=== 3. One-port open/short compensation at the end of a pigtail ===")
# residual model: series Z_s (pad/lead: 0.3 ohm + 0.8 nH) then shunt Y_o (0.12 pF pad capacitance) in front of DUT
w = 2 * np.pi * np.array([433e6, 915e6, 1575e6])
Zs = 0.3 + 1j * w * 0.8e-9
Yo = 1j * w * 0.12e-12
for name, zd in [("47 ohm resistor", 47 + 0j * w), ("2.2 pF cap", 1 / (1j * w * 2.2e-12)), ("8.2 nH ind", 1j * w * 8.2e-9)]:
    zd = zd * np.ones_like(w)
    zm = Zs + 1 / (Yo + 1 / zd)                     # what the (calibrated) VNA sees at the pigtail end
    z_short = Zs                                    # measure with the pads shorted
    y_open = 1 / (Zs + 1 / Yo)                      # measure with nothing mounted
    # compensation assuming 'Zs then Yo' (short measured first-order): LCR-meter formula
    zc = (zm - z_short) / (1 - (zm - z_short) * (y_open))
    zc_simple = zm - z_short
    out = []
    for i, fq in enumerate([433, 915, 1575]):
        out.append(f"{fq} MHz: raw {abs(zm[i]):7.2f}, short-only {abs(zc_simple[i]):7.2f}, open+short {abs(zc[i]):7.2f} (true {abs(zd[i]):7.2f}) ohm")
    print(f"  {name}: " + " | ".join(out))

print("\n=== 4. TRL line plan for a JLCPCB 50-ohm microstrip fixture ===")
for eeff in [3.3, 3.0]:
    print(f"  eps_eff = {eeff}:")
    for f_lo, f_hi in [(0.3e9, 2.4e9), (0.75e9, 6.0e9), (0.1e9, 0.8e9)]:
        fc = f_lo / (20 / 90)
        fc = min(fc, f_hi / (160 / 90))
        dl = C0 / (4 * fc * np.sqrt(eeff))
        print(f"    band {f_lo/1e9:4.2f}-{f_hi/1e9:4.2f} GHz: centre {fc/1e9:5.2f} GHz, line longer than thru by {dl*1000:6.1f} mm"
              f" (covers {fc*20/90/1e9:.2f}-{fc*160/90/1e9:.2f} GHz)")
print("  -> two lines (~31 mm and ~12 mm at eps_eff 3.3) + match cover ~0.1-6 GHz; long low-frequency lines get lossy/big")

print("\n=== 5. P370 variants: NZC (no impedance correction) vs ZC (impedance-corrected, needs FIX-DUT-FIX) ===")
from skrf.calibration.deembedding import IEEEP370_SE_ZC_2xThru
try:
    dm_zc = IEEEP370_SE_ZC_2xThru(dummy_2xthru=thru2x, dummy_fix_dut_fix=meas, bandwidth_limit=6e9, name='zc')
    dut_zc = dm_zc.deembed(meas)
    for fq in [0.433e9, 0.915e9, 2.45e9]:
        k = np.argmin(np.abs(f - fq))
        print(f"  {fq/1e9:5.3f} GHz: NZC {np.imag(z_series(dut_p370)[k])/(2*np.pi*f[k])*1e9:6.2f} nH, "
              f"ZC {np.imag(z_series(dut_zc)[k])/(2*np.pi*f[k])*1e9:6.2f} nH (true {np.imag(z_true[k])/(2*np.pi*f[k])*1e9:.2f})")
    print(f"  ZC max |S_err| below 5 GHz = {np.max(np.abs(dut_zc.s[f < 5e9] - dut.s[f < 5e9])):.2e}")
except Exception as e:
    print("  ZC variant failed:", e)
