#!/usr/bin/env python3
"""
Verification for kb/03-transmission-lines-matching/input-impedance-stubs-quarter-wave.md

Checks:
  1. Zin = Z0 (ZL + j Z0 tan bl)/(Z0 + j ZL tan bl) (lossless) and the tanh form (lossy) vs skrf.
  2. Quarter-wave: Zin = Z0^2/ZL; half-wave repeats ZL.
  3. Stubs: short -> j Z0 tan(bl) (inductive below lambda/4), open -> -j Z0 cot(bl) (capacitive);
     equivalent L and C; short-stub limits L ~ L' l, C ~ C' l.
  4. Resonant stubs: shorted lambda/4 == parallel LC with C = pi/(4 w0 Z0), L = 4 Z0/(pi w0) near f0;
     Q of a resonant line = beta/(2 alpha).
  5. Harmonic behaviour: shorted lambda/4 stub at f0 is a short at 2 f0 (even-harmonic trap).
  6. Zoc*Zsc = Z0^2 (cable measurement method).
  7. Quarter-wave transformer fractional bandwidth formula (Pozar 5.4) vs brute-force sweep.
  8. Pi-equivalent of a line section: series j Z0 sin(theta), shunt Y = j tan(theta/2)/Z0.
  9. Microstrip example used on the telegrapher page: 0.5 mm trace on 1.6 mm FR-4 at 433 MHz.

Run: python3 tools/verify/tline_input_impedance.py
"""
import numpy as np
import skrf as rf

c0 = 299_792_458.0
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def zin_lossless(Z0, ZL, bl):
    t = np.tan(bl)
    return Z0 * (ZL + 1j * Z0 * t) / (Z0 + 1j * ZL * t)


def zin_lossy(Z0, ZL, gl):
    t = np.tanh(gl)
    return Z0 * (ZL + Z0 * t) / (Z0 + ZL * t)


# ---------------------------------------------------------------- 1. vs skrf
freq = rf.Frequency(100, 3000, 291, unit="MHz")
Z0 = 75.0
ZL = 30 - 20j
air = rf.media.DefinedGammaZ0(frequency=freq, gamma=1j * 2 * np.pi * freq.f / (0.7 * c0), z0=Z0, z0_port=50)
L = 0.123
ntw = air.line(L, unit="m") ** rf.Network(frequency=freq, s=((ZL - 50) / (ZL + 50)) * np.ones(freq.npoints), z0=50)
bl = 2 * np.pi * freq.f / (0.7 * c0) * L
err = np.max(np.abs(ntw.z[:, 0, 0] - zin_lossless(Z0, ZL, bl)))
check("lossless Zin formula == skrf cascade (75 ohm line, 50 ohm ports)", err < 1e-9, f"(max abs err {err:.1e} ohm)")
gam = 0.3 + 1j * 2 * np.pi * freq.f / (0.7 * c0)
lossy = rf.media.DefinedGammaZ0(frequency=freq, gamma=gam, z0=Z0, z0_port=50)
ntw2 = lossy.line(L, unit="m") ** rf.Network(frequency=freq, s=((ZL - 50) / (ZL + 50)) * np.ones(freq.npoints), z0=50)
err2 = np.max(np.abs(ntw2.z[:, 0, 0] - zin_lossy(Z0, ZL, gam * L)))
check("lossy tanh Zin formula == skrf cascade", err2 < 1e-9, f"(max abs err {err2:.1e} ohm)")

# ---------------------------------------------------------------- 2. lambda/4 and lambda/2
for ZLx in [12.5, 200, 30 - 40j, 1e-9 + 0j]:
    zq = zin_lossless(50, ZLx, np.pi / 2 - 1e-12)
    zh = zin_lossless(50, ZLx, np.pi)
    okq = abs(zq - 2500 / ZLx) / abs(2500 / ZLx) < 1e-6 if abs(ZLx) > 1e-6 else abs(zq) > 1e6
    check(f"lambda/4 inverts {ZLx}: Zin = Z0^2/ZL", okq)
    check(f"lambda/2 repeats {ZLx}", abs(zh - ZLx) < 1e-6)

# ---------------------------------------------------------------- 3. stubs as L and C
f0 = 433e6
w0 = 2 * np.pi * f0
vp = 0.66 * c0
lam = vp / f0
Z0 = 50.0
for frac in [0.02, 0.05, 0.1, 0.2]:
    l = frac * lam
    b = 2 * np.pi / lam
    Zsc = 1j * Z0 * np.tan(b * l)
    Zoc = -1j * Z0 / np.tan(b * l)
    Leq = Zsc.imag / w0
    Ceq = -1 / (w0 * Zoc.imag)
    L_naive = Z0 / vp * l
    C_naive = l / (Z0 * vp)
    print(f"      l = {frac:.2f} lambda ({l*1000:.1f} mm of VF0.66 50-ohm coax at 433 MHz): "
          f"short -> L = {Leq*1e9:.2f} nH (L'l = {L_naive*1e9:.2f}), open -> C = {Ceq*1e12:.2f} pF (C'l = {C_naive*1e12:.2f})")
check("short stub << lambda: L -> L' l (within 1.4% at 0.02 lambda)",
      abs(Z0 * np.tan(2 * np.pi * 0.02) / w0 - Z0 / vp * 0.02 * lam) / (Z0 / vp * 0.02 * lam) < 0.014)

# ---------------------------------------------------------------- 4. resonant stub == parallel LC; Q
Cp = np.pi / (4 * w0 * Z0)
Lp = 4 * Z0 / (np.pi * w0)
check("parallel-LC equivalent resonates at f0", abs(1 / (2 * np.pi * np.sqrt(Lp * Cp)) - f0) / f0 < 1e-12)
fs = f0 * np.linspace(0.97, 1.03, 601)
bls = np.pi / 2 * fs / f0
Y_stub = 1 / (1j * Z0 * np.tan(bls))
Y_lc = 1j * 2 * np.pi * fs * Cp + 1 / (1j * 2 * np.pi * fs * Lp)
rel = np.max(np.abs(Y_stub - Y_lc)) / (w0 * Cp)
check("shorted lambda/4 stub admittance == parallel LC within +/-3% of f0 (error < 0.2% of w0C)",
      rel < 2e-3, f"(max |dY|/(w0 C) = {rel:.1e})")
# Q of a resonant line with loss alpha: Q = beta/(2 alpha)
alpha = 0.02  # Np/m
beta0 = 2 * np.pi / lam
l4 = lam / 4
fq = f0 * np.linspace(0.9, 1.1, 200001)
g = alpha + 1j * 2 * np.pi * fq / vp
Zs = Z0 * np.tanh(g * l4)       # shorted stub
mag = np.abs(Zs)
pk = mag.max()
above = fq[mag >= pk / np.sqrt(2)]
Q_meas = f0 / (above.max() - above.min())
Q_th = beta0 / (2 * alpha)
check("Q of shorted lambda/4 line = beta/(2 alpha)", abs(Q_meas - Q_th) / Q_th < 0.01,
      f"(Q_sweep = {Q_meas:.1f}, beta/2alpha = {Q_th:.1f})")
R_peak = Z0 / (alpha * l4)
check("shorted lambda/4 peak impedance = Z0/(alpha l)", abs(pk - R_peak) / R_peak < 0.01,
      f"({pk:.0f} ohm vs {R_peak:.0f} ohm)")
# RG-58 at 433 MHz: alpha from 0.287 dB/m
a58 = 0.287 / (20 / np.log(10))
print(f"      RG-58 lambda/4 stub at 433 MHz: Q = {beta0/(2*a58):.0f}, R_peak = {Z0/(a58*l4):.0f} ohm")

# ---------------------------------------------------------------- 5. harmonics
Zs2 = 1j * Z0 * np.tan(np.pi / 2 * 2)   # 2 f0 -> electrical length pi
Zs3 = 1j * Z0 * np.tan(np.pi / 2 * 3)
check("shorted lambda/4 at f0 is a short at 2 f0 (even-harmonic trap)", abs(Zs2) < 1e-9)
check("... and an open again at 3 f0 (odd harmonics pass)", abs(Zs3) > 1e9)

# ---------------------------------------------------------------- 6. Zoc Zsc
for gl in [0.1 + 0.7j, 0.05 + 2.2j]:
    Zc = 51.3 - 0.8j
    zoc = Zc / np.tanh(gl)
    zsc = Zc * np.tanh(gl)
    check(f"Z0 = sqrt(Zoc Zsc) recovers {Zc}", abs(np.sqrt(zoc * zsc) - Zc) < 1e-9)
    check("tanh(gl) = sqrt(Zsc/Zoc)", abs(np.sqrt(zsc / zoc) - np.tanh(gl)) < 1e-9)

# ---------------------------------------------------------------- 7. lambda/4 transformer bandwidth
def qw_bw(Z0_, ZL_, Gm):
    # Pozar eq. (5.52), TEM line
    return 2 - 4 / np.pi * np.arccos(Gm / np.sqrt(1 - Gm**2) * 2 * np.sqrt(Z0_ * ZL_) / abs(ZL_ - Z0_))


Z0_, ZL_ = 50.0, 12.5
Z1 = np.sqrt(Z0_ * ZL_)
Gm = 0.2  # VSWR 1.5
ff = np.linspace(0.3, 1.7, 140001)
zin = zin_lossless(Z1, ZL_, np.pi / 2 * ff)
G = np.abs((zin - Z0_) / (zin + Z0_))
inband = ff[G <= Gm]
bw_sweep = inband.max() - inband.min()
bw_formula = qw_bw(Z0_, ZL_, Gm)
check("lambda/4 transformer 12.5->50 ohm, VSWR<1.5 fractional BW formula == sweep",
      abs(bw_sweep - bw_formula) < 1e-3, f"({bw_formula*100:.1f} % vs {bw_sweep*100:.1f} %)")
print(f"      Z1 = {Z1:.1f} ohm; at 433 MHz that is {bw_formula*433:.0f} MHz of VSWR<1.5 bandwidth")
for ZLx in [25.0, 100.0, 5.0]:
    print(f"      50 -> {ZLx} ohm: VSWR<1.5 BW = {qw_bw(50, ZLx, 0.2)*100:.1f} %")

# ---------------------------------------------------------------- 8. pi-equivalent of a line section
th = 0.6
Zc = 90.0
A = np.array([[np.cos(th), 1j * Zc * np.sin(th)], [1j * np.sin(th) / Zc, np.cos(th)]])
Zser = 1j * Zc * np.sin(th)
Ysh = 1j * np.tan(th / 2) / Zc
Pi = np.array([[1, 0], [Ysh, 1]]) @ np.array([[1, Zser], [0, 1]]) @ np.array([[1, 0], [Ysh, 1]])
check("line section == Pi(series jZ0 sin th, shunt j tan(th/2)/Z0)", np.allclose(A, Pi))
# small theta: high-Z line ~ series L = Z0 th/w; low-Z line ~ shunt C = th/(Z0 w)
print(f"      e.g. 90 ohm line, theta = {np.degrees(th):.0f} deg: series X = {Zser.imag:.1f} ohm, "
      f"each shunt B = {Ysh.imag*1e3:.2f} mS")

# ---------------------------------------------------------------- 9. microstrip example
f433 = rf.Frequency(433, 433, 1, unit="MHz")
ms = rf.media.MLine(frequency=f433, w=0.5e-3, h=1.6e-3, t=35e-6, ep_r=4.5, tand=0.02, rough=0,
                    disp="kirschningjansen", model="hammerstadjensen", z0_port=50)
Zms = ms.z0[0].real
th25 = ms.gamma[0].imag * 25e-3
zin_ms = zin_lossless(Zms, 50.0, th25)
check("0.5 mm microstrip on 1.6 mm FR-4 ~108 ohm; 25 mm transforms 50 ohm -> ~56.5+j33.9",
      abs(Zms - 108) < 1.5 and abs(zin_ms - (56.5 + 33.9j)) < 1.0,
      f"(Z0 = {Zms:.1f}, theta = {np.degrees(th25):.1f} deg, Zin = {zin_ms:.1f})")

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
