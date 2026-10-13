#!/usr/bin/env python3
"""
s16_precompliance.py — conducted and radiated pre-compliance numbers for
kb/13-pcb-rf-layout-emc/emc-emi-fundamentals.md ("Conducted and radiated pre-compliance") and
kb/19-regulations-safety/certification-fcc-ce-imda.md.

  1. LISN impedance seen by the EUT: 50 uH network (CISPR 16 / MIL-STD-461 style: 50 uH line, 0.1 uF + 50 ohm port,
     1 uF + 5 ohm on the supply side) and 5 uH network (CISPR 25 / DO-160 style), 10 kHz - 108 MHz.
  2. Buck-converter differential-mode conducted emission at a LISN (8.4 V -> 3.3 V, 1 A, 2 MHz) without and with
     an LC input filter, against CISPR 32 Class B average limits (0.5-5 MHz 46 dBuV, 5-30 MHz 50 dBuV).
     Filter damping (R-C across the filter capacitor) and the undamped filter's resonance peak.
  3. Antenna factor AF = 20 log f_MHz - G_dBi - 29.77 (50 ohm) for an LPDA; reading -> field; FCC 15.109 Class B
     at 3 m and CISPR 32 Class B 10 m limits scaled to 3 m (+20 log(10/3)); RBW correction.
  4. Fixed-height pre-scan error over a ground plane: two-ray field vs receive-antenna height (1 m fixed vs 1-4 m scan).
  5. Common-mode current-probe reading -> predicted field at 3 m with the page's CM formula.

Run: python3 tools/verify/s16_precompliance.py     (instant)
"""
import numpy as np

ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def db20(x):
    return 20 * np.log10(np.abs(x))


print("=" * 96)
print("1. LISN impedance seen by the EUT (port terminated in the 50 ohm receiver)")
print("=" * 96)


def z_lisn(f, Lline, Cport=0.1e-6, Rport=50.0, Csup=1e-6, Rsup=5.0):
    w = 2 * np.pi * f
    z_port = 1 / (1j * w * Cport) + Rport
    z_line = 1j * w * Lline + (Rsup + 1 / (1j * w * Csup))
    return z_port * z_line / (z_port + z_line)


freqs = [10e3, 150e3, 500e3, 1e6, 5e6, 30e6, 108e6]
for f in freqs:
    z50 = abs(z_lisn(f, 50e-6))
    z5 = abs(z_lisn(f, 5e-6))
    print(f"  {f/1e6:8.3f} MHz: |Z| 50 uH LISN {z50:5.1f} ohm, 5 uH AN {z5:5.1f} ohm")
check("50 uH LISN within 40-52 ohm from 1 to 30 MHz", all(40 < abs(z_lisn(f, 50e-6)) < 52 for f in (1e6, 5e6, 30e6)))
check("5 uH AN is < 15 ohm at 150 kHz (low-impedance battery model)", abs(z_lisn(150e3, 5e-6)) < 15)

print()
print("=" * 96)
print("2. Buck converter DM conducted emission (8.4 V -> 3.3 V, 1 A, 2 MHz, D = 0.39), 50 uH LISN")
print("=" * 96)
fsw, D, Iout = 2e6, 3.3 / 8.4, 1.0
Cin, esr, esl = 5e-6, 5e-3, 0.5e-9       # 10 uF 0805 X7R at bias ~ 5 uF


def zc(f, C, R, L):
    w = 2 * np.pi * f
    return R + 1j * w * L + 1 / (1j * w * C)


def cispr32_b_avg(f):
    if f < 0.5e6:
        return 56 - 10 * np.log10(f / 0.15e6) / np.log10(0.5 / 0.15)
    if f < 5e6:
        return 46.0
    return 50.0


def emission(n, filt=None):
    f = n * fsw
    In = 2 * Iout / (n * np.pi) * abs(np.sin(n * np.pi * D))      # harmonic amplitude of the pulsed input current
    Zc = zc(f, Cin, esr, esl)
    ZL = z_lisn(f, 50e-6)
    if filt is None:
        Iline = In * Zc / (Zc + ZL)
    else:
        Lf, Cf, Rd, Cd = filt
        w = 2 * np.pi * f
        Zf = 1 / (1 / zc(f, Cf, 3e-3, 0.4e-9) + (0 if Rd is None else 1 / (Rd + 1 / (1j * w * Cd))))
        # current divider: In splits into Cin and (L + (Cf || (LISN)))
        Zright = 1j * w * Lf + Zf * ZL / (Zf + ZL)
        Iright = In * Zc / (Zc + Zright)
        Iline = Iright * Zf / (Zf + ZL)
    # receiver voltage: line current through the LISN, port voltage = I * Z_LISN * (fraction into the 50 ohm port)
    w = 2 * np.pi * f
    z_port = 1 / (1j * w * 0.1e-6) + 50
    Vport = Iline * ZL * 50 / z_port
    return f, In, db20(Vport / 1e-6)


over_max = -999
for n in (1, 2, 3, 5, 10):
    f, In, dbuv = emission(n)
    lim = cispr32_b_avg(f) if f <= 30e6 else np.nan
    over_max = max(over_max, dbuv - lim)
    print(f"  n={n:2d} {f/1e6:5.1f} MHz: I_in harmonic {In*1e3:6.1f} mA -> {dbuv:5.1f} dBuV at the LISN port "
          f"(Class B AV limit {lim:.0f}; {dbuv-lim:+.1f} dB)")
check("bare buck fails Class B conducted by > 20 dB", over_max > 20)
filt = (1.0e-6, 10e-6, None, None)
filt_d = (1.0e-6, 10e-6, 0.5, 47e-6)
f_res = 1 / (2 * np.pi * np.sqrt(1e-6 * 10e-6))
print(f"  LC input filter 1.0 uH + 10 uF (resonance {f_res/1e3:.0f} kHz), and with R-C damping 0.5 ohm + 47 uF:")
worst = -999
for n in (1, 2, 3, 5, 10):
    f, In, dbuv = emission(n, filt)
    _, _, dbuv_d = emission(n, filt_d)
    lim = cispr32_b_avg(f) if f <= 30e6 else np.nan
    worst = max(worst, dbuv - lim)
    print(f"  n={n:2d} {f/1e6:5.1f} MHz: {dbuv:5.1f} dBuV undamped / {dbuv_d:5.1f} dBuV damped ({dbuv-lim:+.1f} dB vs limit)")
check("filtered buck passes Class B average", worst < -6)
# output impedance peak of the filter seen by the converter (Middlebrook): undamped vs damped
fs = np.logspace(4, 7, 3000)
w = 2 * np.pi * fs


def zout(Rd, Cd):
    Zcf = zc(fs, 10e-6, 3e-3, 0.4e-9)
    if Rd is not None:
        Zcf = 1 / (1 / Zcf + 1 / (Rd + 1 / (1j * w * Cd)))
    Zl = 1j * w * 1e-6 + 0.02        # source side: battery ~ 0.02 ohm
    return np.abs(Zl * Zcf / (Zl + Zcf))


zu, zd = zout(None, None).max(), zout(0.5, 47e-6).max()
Rin_neg = 3.3**2 / 3.3 / (0.9) * 0 + (8.4**2) / (3.3 * 1.0 / 0.9)
print(f"  filter output-impedance peak: {zu:.2f} ohm undamped, {zd:.2f} ohm damped; converter |negative input R| ="
      f" V^2/P = {Rin_neg:.1f} ohm -> keep the peak well below it (Middlebrook)")
check("damping lowers the filter Z peak by > 5x", zu / zd > 5)

print()
print("=" * 96)
print("3. LPDA antenna factor and a radiated pre-scan reading")
print("=" * 96)


def af(f_mhz, g_dbi):
    return 20 * np.log10(f_mhz) - g_dbi - 29.77


k = np.sqrt(4 * np.pi * 376.730 / 50) / 299.792458
check("AF constant: 20 log(sqrt(4 pi eta0/50)/c[Mm/s]) = -29.77 dB", abs(20 * np.log10(k) + 29.77) < 0.01,
      f"({20*np.log10(k):.3f})")
for f in (300, 433, 1000):
    print(f"  {f} MHz, 6 dBi LPDA: AF = {af(f, 6):.1f} dB/m; 0 dBi: {af(f, 0):.1f} dB/m")
read_dbm, cable = -85.0, 1.0
dbuv = read_dbm + 107
E = dbuv + af(400, 6) + cable
fcc = 20 * np.log10(200)          # 216-960 MHz, 200 uV/m at 3 m
cispr3 = 37 + 20 * np.log10(10 / 3)
print(f"  reading {read_dbm} dBm (= {dbuv:.0f} dBuV) at 400 MHz, AF {af(400,6):.1f} dB/m, cable {cable} dB -> E = {E:.1f} dBuV/m at 3 m")
print(f"  FCC 15.109 Class B 3 m (216-960 MHz): {fcc:.1f} dBuV/m -> margin {fcc-E:.1f} dB; CISPR 32 Class B 37 dBuV/m @10 m"
      f" scaled to 3 m: {cispr3:.1f} dBuV/m -> margin {cispr3-E:.1f} dB")
print(f"  RBW correction, noise-like emission, 100 kHz analyser vs 120 kHz CISPR: +{10*np.log10(1.2):.1f} dB; "
      f"impulsive (coherent) noise: +{20*np.log10(1.2):.1f} dB; CW harmonics: 0 dB")

print()
print("=" * 96)
print("4. Fixed-height pre-scan error over a conducting ground (horizontal polarisation, EUT at 0.8 m, d = 3 m)")
print("=" * 96)
h_e, d = 0.8, 3.0
hs = np.linspace(1.0, 4.0, 601)


def field(hr, kk):
    r1 = np.hypot(d, hr - h_e)
    r2 = np.hypot(d, hr + h_e)
    return np.abs(np.exp(-1j * kk * r1) / r1 - np.exp(-1j * kk * r2) / r2)   # horizontal pol: Gamma = -1


errs = []
for f in (100e6, 150e6, 200e6, 300e6, 500e6, 900e6):
    kk = 2 * np.pi * f / 299.792458e6
    e = db20(field(1.0, kk) / field(hs, kk).max())
    errs.append(e)
    print(f"  {f/1e6:4.0f} MHz: a 1 m fixed antenna reads {e:+.1f} dB vs the 1-4 m height-scan maximum")
check("fixed height under-reads by > 3 dB at some frequency", min(errs) < -3)

print()
print("=" * 96)
print("5. Current-probe reading -> field at 3 m (CM formula E = 1.26e-6 f L I / r, L capped at lambda/pi)")
print("=" * 96)
for f, rd, zt in ((30e6, 20.0, -5.0), (100e6, 10.0, 0.0), (200e6, 5.0, 3.0)):
    I = 10 ** ((rd - zt) / 20) * 1e-6
    Lc = min(1.0, 299.792458e6 / f / np.pi)
    Ef = 1.26e-6 * f * Lc * I / 3
    lim = 100 if f < 88e6 else (150 if f < 216e6 else 200)
    print(f"  {f/1e6:4.0f} MHz: probe {rd:.0f} dBuV, Zt {zt:+.0f} dBohm -> I_cm {db20(I/1e-6):.1f} dBuA ({I*1e6:.2f} uA) on 1 m ->"
          f" E(3 m) {db20(Ef/1e-6):.1f} dBuV/m vs FCC B {db20(lim):.1f}")

print()
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
