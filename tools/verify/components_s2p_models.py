#!/usr/bin/env python3
"""
Verification for kb/04-real-components-hf/component-models-s2p-spice.md

  1. Build a component (capacitor C-ESL-ESR) as a two-port in series-thru and shunt-thru configurations,
     write/read Touchstone (.s2p), and extract impedance back from S21 (both formulas).
  2. Measurement sensitivity: impedance error from a small S21 error (0.01 dB / 0.1 deg) in series vs shunt
     fixtures, for |Z| from 10 mohm to 10 kohm -> why vendors measure bypass caps in shunt, inductors in series.
  3. Pad/via mounting effect: de-embedded 10 nH inductor model (Cp 0.115 pF) vs same part on 0402 pads with
     pad capacitance and a ground-referenced microstrip; SRF shift.
  4. Reference-plane error: 1 mm of unaccounted 50 ohm line at 915 MHz and 2.45 GHz.
  5. Passivity/reciprocity checks on data (scikit-rf is_passive / is_reciprocal) incl. a corrupted file.
  6. Print an equivalent SPICE subcircuit for the capacitor and a frequency-dependent-loss inductor.
Run: python3 tools/verify/components_s2p_models.py
"""
import os, tempfile
import numpy as np
import skrf as rf

Z0 = 50.0
freq = rf.Frequency(10, 6000, 5991, unit="MHz")
w = 2 * np.pi * freq.f
med = rf.media.DefinedGammaZ0(frequency=freq, z0_port=Z0)

print("=== 1. Series-thru and shunt-thru two-ports, Touchstone round trip ===")
C, ESL, ESR = 100e-12, 0.4e-9, 0.1
Zc = ESR + 1j * w * ESL + 1 / (1j * w * C)
def series_2port(Z):
    s = np.zeros((len(Z), 2, 2), complex)
    s[:, 0, 0] = s[:, 1, 1] = Z / (Z + 2 * Z0)
    s[:, 0, 1] = s[:, 1, 0] = 2 * Z0 / (Z + 2 * Z0)
    return rf.Network(frequency=freq, s=s, z0=Z0, name="series")
def shunt_2port(Z):
    s = np.zeros((len(Z), 2, 2), complex)
    s[:, 0, 0] = s[:, 1, 1] = -Z0 / (2 * Z + Z0)
    s[:, 0, 1] = s[:, 1, 0] = 2 * Z / (2 * Z + Z0)
    return rf.Network(frequency=freq, s=s, z0=Z0, name="shunt")
ser = series_2port(Zc); sh = shunt_2port(Zc)
tmp = tempfile.mkdtemp()
ser.write_touchstone(os.path.join(tmp, "cap_series"))
back = rf.Network(os.path.join(tmp, "cap_series.s2p"))
print(f"Touchstone round-trip max |dS| = {np.max(np.abs(back.s - ser.s)):.2e} (file: {os.path.join(tmp,'cap_series.s2p')})")
Z_from_series = 2 * Z0 * (1 / ser.s[:, 1, 0] - 1)
Z_from_shunt = Z0 / 2 * sh.s[:, 1, 0] / (1 - sh.s[:, 1, 0])
print(f"extraction errors: series {np.max(np.abs(Z_from_series-Zc)/np.abs(Zc)):.1e}, shunt {np.max(np.abs(Z_from_shunt-Zc)/np.abs(Zc)):.1e}")
i = np.argmin(np.abs(Zc))
print(f"SRF from model: {freq.f[i]/1e6:.0f} MHz (1/(2 pi sqrt(LC)) = {1/(2*np.pi*np.sqrt(ESL*C))/1e6:.0f} MHz), |Z|min = {abs(Zc[i]):.3f} ohm")

print("\n=== 2. Fixture sensitivity: |Z| error for a 0.01 dB / 0.1 deg S21 error ===")
dS = 10**(0.01 / 20) * np.exp(1j * np.radians(0.1)) - 1   # relative perturbation of S21
for Zmag in [0.01, 0.1, 1, 10, 100, 1000, 10000]:
    Z = Zmag + 0j
    s21_ser = 2 * Z0 / (Z + 2 * Z0); s21_sh = 2 * Z / (2 * Z + Z0)
    Zs_err = abs(2 * Z0 * (1 / (s21_ser * (1 + dS)) - 1) - Z) / Zmag
    s = s21_sh * (1 + dS)
    Zsh_err = abs(Z0 / 2 * s / (1 - s) - Z) / Zmag
    print(f"  |Z| = {Zmag:8.2f} ohm: relative error series-thru {Zs_err*100:9.2f} %, shunt-thru {Zsh_err*100:9.2f} %")

print("\n=== 3. Mounting: de-embedded inductor model vs on pads ===")
L, Rs, Cp = 10e-9, 0.6, 0.115e-12   # Cp from datasheet SRF 4.7 GHz (0402HP-10N)
Zl = 1 / (1 / (Rs + 1j * w * L) + 1j * w * Cp)
def srf_series(Z):
    ph = np.angle(Z)
    idx = np.where((ph[:-1] > 0) & (ph[1:] <= 0))[0]
    return freq.f[idx[0]] if len(idx) else np.nan
print(f"  de-embedded model SRF = {srf_series(Zl)/1e9:.2f} GHz")
for Cpad in [0.05e-12, 0.1e-12, 0.2e-12]:
    # pads add capacitance across the part (pad-to-pad through the body/fringe) ~ Cpad/4 and to ground Cpad each end
    Zm = 1 / (1 / Zl + 1j * w * Cpad / 4)
    net = med.shunt_capacitor(Cpad) ** series_2port(Zm) ** med.shunt_capacitor(Cpad)
    # effective series reactance seen between the ports: derive from ABCD B-parameter (series branch)
    B = net.a[:, 0, 1]
    f_res = srf_series(B)
    print(f"  pads {Cpad*1e12:.2f} pF to ground each end (+{Cpad/4*1e15:.0f} fF across): series-branch SRF = {f_res/1e9:.2f} GHz; "
          f"|S21| at 2.45 GHz = {20*np.log10(abs(net.s[np.argmin(np.abs(freq.f-2.45e9)),1,0])):.2f} dB")

print("\n=== 4. Reference-plane error ===")
for f in [433.92e6, 915e6, 2.45e9, 5.8e9]:
    eeff = 3.3
    ph = 360 * f * np.sqrt(eeff) / 299792458.0 * 1e-3
    print(f"  1 mm of microstrip (eeff 3.3) at {f/1e9:.2f} GHz = {ph:.2f} deg of S21 phase ({2*ph:.2f} deg on S11)")

print("\n=== 5. Passivity / reciprocity checks ===")
print(f"  model series cap: is_passive = {ser.is_passive()}, is_reciprocal = {ser.is_reciprocal()}")
bad = ser.copy(); bad.s[:, 1, 0] *= 1.02   # corrupted S21 (+0.17 dB), e.g. bad normalisation
print(f"  corrupted copy (+0.17 dB on S21): is_passive = {bad.is_passive()}, is_reciprocal = {bad.is_reciprocal()}")
pv = bad.passivity
print(f"  max eigenvalue of S^H S in corrupted file = {np.max(np.abs(np.linalg.eigvals(np.conj(np.transpose(bad.s,(0,2,1))) @ bad.s))):.4f} (>1 => non-passive)")

print("\n=== 6. SPICE equivalents ===")
print("""* 100 pF C0G 0402 series model (C-ESL-ESR)
.subckt CAP100P 1 2
C1 1 n1 100p
L1 n1 n2 0.4n
R1 n2 2 0.1
.ends
* 10 nH wirewound inductor with skin-effect-like loss: R0 in series, Rp across L for rising R(f), Cp shunt
.subckt IND10N 1 2
L1 1 n1 10n
R0 n1 2 0.1
Rsk 1 n1 20k      ; parallel R makes effective series R rise ~ (wL)^2/Rsk with frequency
Cp 1 2 0.115p
.ends""")
print("OK")
