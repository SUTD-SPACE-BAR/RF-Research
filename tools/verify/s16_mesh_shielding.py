#!/usr/bin/env python3
"""
s16_mesh_shielding.py — shielding beyond the board, for kb/13-pcb-rf-layout-emc/shielding-and-isolation.md
("Enclosures, doors, meshes and fabrics").

  1. Wire mesh as an inductive shunt sheet (plane wave, normal incidence, mesh pitch a << lambda, wire radius r << a):
       X/eta0 = (a/lambda) ln(a / 2 pi r)  ->  |T| = 2X/|eta0 + 2jX| ~ 2 (a/lambda) ln(a/2 pi r)
     cross-checked against Marcuvitz's strip-grating reactance X/eta0 = (a/lambda) ln csc(pi w / 2a) with w = 4r,
     and compared with the single-aperture rule 20 log(lambda/2g) used elsewhere in the KB.
  2. Thin conductive sheet / fabric (t << skin depth): SE = 20 log(1 + eta0 / 2 R_s); and aluminium foil with the full
     Schelkunoff R + A (+B) terms -> material SE is never the limit; seams are.
  3. Seams between screws / contact points: SE ~ 20 log(lambda / 2 s) for s < lambda/2, 0 above.
  4. Faraday-box phone budget: attenuation needed to block a cellular downlink vs SE of a cookie-tin lid seam.
  5. SDR cage-test dynamic range: CW source inside, SDR outside at 1 m, attenuator substitution; FFT-bin noise floor.

Run: python3 tools/verify/s16_mesh_shielding.py     (instant)
"""
import numpy as np

ok_all = True
ETA0 = 376.730
C = 299_792_458.0


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def db(x):
    return 20 * np.log10(np.abs(x))


freqs = [100e6, 433e6, 915e6, 1800e6, 2450e6, 5800e6]
print("=" * 100)
print("1. Wire-mesh shielding (plane wave, normal incidence)")
print("=" * 100)
meshes = [("window insect screen (18x16, 0.28 mm wire)", 1.5e-3, 0.14e-3),
          ("hardware cloth 1/4 in (6.35 mm), 0.64 mm wire", 6.35e-3, 0.32e-3),
          ("chicken wire ~25 mm, 0.7 mm wire", 25e-3, 0.35e-3),
          ("fine brass mesh 100/in (0.25 mm pitch, 0.1 mm wire)", 0.254e-3, 0.05e-3)]
print("  mesh                                              " + "".join(f"{f/1e6:>8.0f}" for f in freqs) + "  MHz")
for name, a, r in meshes:
    row = []
    for f in freqs:
        lam = C / f
        X = ETA0 * (a / lam) * np.log(a / (2 * np.pi * r))
        T = 2j * X / (ETA0 + 2j * X)
        Xm = ETA0 * (a / lam) * np.log(1 / np.sin(np.pi * 4 * r / (2 * a)))
        Tm = 2j * Xm / (ETA0 + 2j * Xm)
        row.append((-db(T), -db(Tm)))
    note = "  dB (log form)" if a / (2 * np.pi * r) > 1.5 else "  dB (log form INVALID here: a/2πr < 1.5, use csc form)"
    print(f"  {name:50s}" + "".join(f"{v[0]:8.1f}" for v in row) + note)
    print(f"  {'':50s}" + "".join(f"{v[1]:8.1f}" for v in row) + "  dB (Marcuvitz csc form)")
    if name.startswith("window"):
        check("log and csc forms agree within 1.5 dB for the insect screen", max(abs(v[0] - v[1]) for v in row) < 1.5)
g = 1.5e-3 - 0.28e-3
print("  single-aperture rule 20 log(lambda/2g) for the insect-screen opening g = 1.22 mm: " +
      ", ".join(f"{20*np.log10(C/f/(2*g)):.0f}" for f in freqs) + " dB  (one hole; a whole sheet of holes leaks more)")
# 20 dB/decade check
a, r = 1.5e-3, 0.14e-3
se = [-db(2j * ETA0 * (a / (C / f)) * np.log(a / (2 * np.pi * r)) / (ETA0 + 2j * ETA0 * (a / (C / f)) * np.log(a / (2 * np.pi * r))))
      for f in (100e6, 1000e6)]
check("mesh SE falls ~20 dB/decade", abs((se[0] - se[1]) - 20) < 1.0, f"({se[0]-se[1]:.1f} dB)")

print()
print("=" * 100)
print("2. Conductive fabrics and foil (far field)")
print("=" * 100)
for Rs in (0.01, 0.05, 0.1, 0.5, 1.0, 10.0):
    print(f"  sheet resistance {Rs:5.2f} ohm/sq: SE = 20 log(1 + eta0/2Rs) = {db(1 + ETA0/(2*Rs)):.1f} dB (frequency-independent while t << delta)")
sig_al, t_al = 3.5e7, 16e-6
for f in (433e6, 915e6, 2450e6):
    delta = 1 / np.sqrt(np.pi * f * 4e-7 * np.pi * sig_al)
    A = 8.686 * t_al / delta
    Zs = (1 + 1j) / (sig_al * delta)
    R = db(ETA0 / (4 * np.abs(Zs)))
    print(f"  16 um kitchen foil at {f/1e6:.0f} MHz: delta {delta*1e6:.2f} um, absorption A {A:.0f} dB, reflection R {R:.0f} dB"
          f" -> material SE > {A+R:.0f} dB")
check("1 ohm/sq fabric gives > 40 dB", db(1 + ETA0 / 2) > 40)

print()
print("=" * 100)
print("3. Seams: unbonded length s between screws / contact points, SE ~ 20 log(lambda/2s)")
print("=" * 100)
for s in (5e-3, 25e-3, 50e-3, 100e-3):
    vals = []
    for f in freqs:
        lam = C / f
        vals.append(max(0.0, 20 * np.log10(lam / (2 * s))))
    print(f"  s = {s*1e3:5.0f} mm: " + ", ".join(f"{f/1e6:.0f} MHz {v:.0f} dB" for f, v in zip(freqs, vals)))

print()
print("=" * 100)
print("4. Why a phone in a home-made Faraday box still rings")
print("=" * 100)
floor = -124.0     # assumed RSRP at which a phone loses LTE service (handset-dependent, -120...-130 dBm)
for rsrp in (-60.0, -80.0, -100.0):
    print(f"  downlink RSRP {rsrp:.0f} dBm outside: need > {rsrp-floor:.0f} dB (+10 dB margin -> {rsrp-floor+10:.0f} dB) to block")
for f in (700e6, 1800e6, 2600e6):
    lam = C / f
    for s in (30e-3, 60e-3):
        se = max(0, 20 * np.log10(lam / (2 * s)))
        print(f"  cookie-tin lid touching every {s*1e3:.0f} mm, {f/1e6:.0f} MHz: seam SE ~ {se:.0f} dB (many such gaps: less)")
check("a 60 mm-contact lid gives < 10 dB at 1800 MHz", 20 * np.log10(C / 1800e6 / 0.12) < 10)

print()
print("=" * 100)
print("5. SDR cage test: dynamic range budget (CW source inside, RTL-SDR outside at 1 m, 433.92 MHz)")
print("=" * 100)
Ptx = 0.0            # dBm CW, e.g. an SX126x in continuous-wave test mode at 0 dBm (inside the box, legal)
fspl = 32.45 + 20 * np.log10(433.92) + 20 * np.log10(1e-3)
Pref = Ptx - fspl
nf = 5.4             # RTL-SDR Blog V3 at 437 MHz (canonical, 00/canonical §D)
pad = 30.0
for bin_hz in (1000.0, 100.0, 10.0):
    nfl = -174 + 10 * np.log10(bin_hz) + nf
    dr = Pref - (nfl + 10)
    print(f"  FFT bin {bin_hz:6.0f} Hz: noise floor {nfl:.1f} dBm -> measurable SE (10 dB SNR) up to {dr:.0f} dB")
print(f"  reference (lid open) arrives at {Pref:.1f} dBm: above an RTL-SDR's ~ -40 dBm overload -> take the reference"
      f" through a {pad:.0f} dB pad ({Pref-pad:.1f} dBm), remove the pad for the closed-lid reading, SE = closed-lid drop + {pad:.0f} dB")
print(f"  RTL-SDR TCXO 1 ppm = {433.92e6*1e-6:.0f} Hz drift: use a 100 Hz-1 kHz bin with peak-hold, not 10 Hz")
check("100 Hz bin gives > 100 dB measurable SE", Pref - (-174 + 20 + nf + 10) > 100)

print()
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
