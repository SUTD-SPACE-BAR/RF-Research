#!/usr/bin/env python3
"""
pcb_cavity_modes.py — verification script for kb/13-pcb-rf-layout-emc/shielding-and-isolation.md

  1. Resonant modes of a shield can over a PCB ground plane (rectangular cavity a x b x d):
     f_mnp = (c / 2 sqrt(eps_eff)) sqrt((m/a)^2 + (n/b)^2 + (p/d)^2); thin cans (d << a, b): lowest modes are
     TM_mn0 (E vertical), m, n >= 1.  Checked against a brute-force 2-D finite-difference eigen-solution of the
     transverse Helmholtz problem (Dirichlet walls) for one box, and against the 02-page 50 x 40 x 10 mm example.
     Loading by the PCB prepreg under the can (layered dielectric, E vertical: series mix).
  2. Q of a can mode: wall loss (tin-plated steel / nickel silver), dielectric floor, and with an absorber sheet;
     what Q means for coupling at resonance.
  3. Leakage through apertures and seams: slot SE ~ 20 log10(lambda / (2 l)) for l < lambda/2, multiple apertures,
     holes as waveguides below cutoff (circular TE11: ~32 dB per unit depth/diameter); solder-point spacing.
  4. Filtering where a wire leaves a can: shunt C, series ferrite bead, and C-bead-C (pi) insertion loss in a
     50-ohm system with real ESL and a bead model, at 433 / 915 / 1575 / 2450 MHz.
  5. Isolation budget example: 2 W 433 MHz downlink and a GNSS receiver on the same flight computer.

Run: python3 tools/verify/pcb_cavity_modes.py    (about 10 s)
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

C0 = 299_792_458.0
MU0 = 4e-7 * np.pi
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def modes(a, b, d, eps=1.0, n=6):
    out = []
    for m in range(0, 4):
        for nn in range(0, 4):
            for p in range(0, 3):
                # TM_mnp (to z) needs m,n>=1 ; TE_mnp needs p>=1 and (m,n) not both 0
                if (m >= 1 and nn >= 1) or (p >= 1 and (m + nn) >= 1):
                    f = C0 / (2 * np.sqrt(eps)) * np.sqrt((m / a) ** 2 + (nn / b) ** 2 + (p / d) ** 2)
                    out.append((f, m, nn, p))
    return sorted(out)[:n]


print("=" * 96)
print("1. Shield-can cavity modes (air-filled, PEC walls)")
print("=" * 96)
for (a, b, d) in [(10e-3, 10e-3, 2e-3), (20e-3, 15e-3, 2.5e-3), (30e-3, 20e-3, 3e-3), (50e-3, 40e-3, 4e-3),
                  (50e-3, 40e-3, 10e-3), (80e-3, 50e-3, 5e-3), (100e-3, 60e-3, 20e-3)]:
    ms = modes(a, b, d)
    print(f"  {a*1e3:4.0f} x {b*1e3:3.0f} x {d*1e3:4.1f} mm: " + ", ".join(f"{f/1e9:5.2f} GHz ({m}{n}{p})" for f, m, n, p in ms[:4]))
f110 = C0 / 2 * np.sqrt(1 / 0.05**2 + 1 / 0.04**2)
check("50 x 40 mm can: first mode 4.80 GHz (matches the 02-electromagnetics cavity page)", abs(f110 / 1e9 - 4.80) < 0.01,
      f"({f110/1e9:.3f} GHz)")

# FD eigen check of the transverse problem: -lap(Ez) = kc^2 Ez, Ez = 0 on walls (TM_mn0 modes)
a, b, N = 0.030, 0.020, 150
hx, hy = a / N, b / int(N * b / a)
nx, ny = N - 1, int(N * b / a) - 1
Dx = sp.diags([1, -2, 1], [-1, 0, 1], shape=(nx, nx)) / hx**2
Dy = sp.diags([1, -2, 1], [-1, 0, 1], shape=(ny, ny)) / hy**2
Lap = sp.kron(Dx, sp.eye(ny)) + sp.kron(sp.eye(nx), Dy)
vals = np.sort(spla.eigsh(-Lap.tocsc(), k=4, sigma=0, which="LM")[0])
fd_f = C0 * np.sqrt(vals) / (2 * np.pi)
an = sorted([C0 / 2 * np.sqrt((m / a) ** 2 + (n / b) ** 2) for m in range(1, 4) for n in range(1, 4)])[:4]
print("  FD eigenvalues 30 x 20 mm (TM_mn0): " + ", ".join(f"{x/1e9:.3f}" for x in fd_f) + " GHz; analytic "
      + ", ".join(f"{x/1e9:.3f}" for x in an))
check("FD eigen-solution matches the analytic cavity formula within 0.3 %", np.max(abs(fd_f - an) / an) < 0.003,
      f"(worst {np.max(abs(fd_f-an)/an)*100:.3f} %)")

# dielectric loading by the PCB floor (prepreg between top copper and L2 plane) - E vertical -> series mix
print("  Loading by the FR-4 floor (can over L2; prepreg 0.21 mm, er 4.4) and by components (effective):")
for d in [2e-3, 3e-3, 5e-3]:
    hs = 0.2104e-3
    eeff = (d + hs) / (d / 1.0 + hs / 4.4)
    print(f"    can height {d*1e3:.0f} mm: eps_eff {eeff:.3f} -> modes lowered by {(1-1/np.sqrt(eeff))*100:.1f} %")
check("a thin prepreg floor lowers can modes by only a few %", (1 - 1 / np.sqrt((2e-3 + 0.21e-3) / (2e-3 + 0.21e-3 / 4.4))) < 0.06)

print("\n" + "=" * 96)
print("2. Q of the first can mode")
print("=" * 96)


def rs(f, sigma):
    return np.sqrt(np.pi * f * MU0 / sigma)


# TM110 of an a x b x d box: exact wall-loss Q (standard result, e.g. Balanis/Pozar style derivation):
# Q_c = (eta / (2 Rs)) * ( (kc^2) * a*b*d ) / ( ... )  -> use the general expression for TM_mn0:
def q_tm110(a, b, d, f, sigma):
    """Wall-loss Q of TM110 in an a x b x d PEC-approx box (top/bottom walls z=0,d; side walls).
    Q = omega mu0 * (energy integral) / (Rs * surface H^2 integral). Closed form for TM110:
    Q = (eta0/Rs) * (a b d (a^2+b^2)^(3/2)) / (2 [a b (a^2+b^2)^... ]) -> computed numerically here."""
    kx, ky = np.pi / a, np.pi / b
    kc2 = kx**2 + ky**2
    w = 2 * np.pi * f
    # fields: Ez = E0 sin(kx x) sin(ky y); Hx ~ (ky/(j w mu)) sin(kx x) cos(ky y) ; Hy ~ -(kx/(j w mu)) cos sin
    # time-avg stored energy W = eps0/4 * E0^2 * a b d /4 * 2 (E and H equal at resonance) -> W = eps0 E0^2 a b d / 8
    W = 8.854e-12 * a * b * d / 8
    # |H|^2 integrals (E0 = 1): |Hx|^2 = ky^2/(w mu)^2 sin^2 cos^2, |Hy|^2 = kx^2/(w mu)^2 cos^2 sin^2
    wm2 = (w * MU0) ** 2
    top_bottom = 2 * (ky**2 + kx**2) / wm2 * (a * b / 4)
    side_x = 2 * (ky**2 / wm2) * (b / 2) * d * 0 + 2 * (kx**2 / wm2) * (b / 2) * d   # walls x=0,a: tangential Hy (cos^2(0)=1)
    side_y = 2 * (ky**2 / wm2) * (a / 2) * d                                        # walls y=0,b: tangential Hx
    P = rs(f, sigma) / 2 * (top_bottom + side_x + side_y)
    return w * W / P


for a, b, d in [(30e-3, 20e-3, 3e-3), (50e-3, 40e-3, 4e-3)]:
    f = C0 / 2 * np.sqrt(1 / a**2 + 1 / b**2)
    for mat, sig in [("copper 5.8e7", 5.8e7), ("nickel silver ~3.5e6", 3.5e6), ("tin-plated steel ~(tin) 8.7e6", 8.7e6)]:
        qc = q_tm110(a, b, d, f, sig)
        fill = 0.2104e-3 / (d + 0.2104e-3)
        qd = 1 / (fill * 0.02)
        qt = 1 / (1 / qc + 1 / qd)
        print(f"  {a*1e3:.0f}x{b*1e3:.0f}x{d*1e3:.0f} mm TM110 {f/1e9:.2f} GHz, walls {mat:30s}: Q_walls {qc:6.0f}, Q_FR4-floor {qd:5.0f},"
              f" Q_total {qt:5.0f}")
qc_cu = q_tm110(0.03, 0.02, 3e-3, C0 / 2 * np.sqrt(1 / 0.03**2 + 1 / 0.02**2), 5.8e7)
# sanity: thin cavity with dominant top/bottom loss -> Q ~ d / delta_s (x ~1)
f0 = C0 / 2 * np.sqrt(1 / 0.03**2 + 1 / 0.02**2)
ds = 1 / np.sqrt(np.pi * f0 * MU0 * 5.8e7)
print(f"  sanity: d/delta_s = {3e-3/ds:.0f} vs Q_walls(Cu) {qc_cu:.0f} (thin box: Q ~ d/delta_s, reduced by side walls)")
check("thin-box wall Q is of order d/delta_s", 0.4 < qc_cu / (3e-3 / ds) < 1.0, f"(ratio {qc_cu/(3e-3/ds):.2f})")
print("  A lossy absorber sheet (magnetic-loaded silicone) typically drops Q to ~5-30: coupling at resonance falls by"
      " the same factor as Q (e.g. Q 200 -> 20 = -20 dB).")

print("\n" + "=" * 96)
print("3. Apertures and seams")
print("=" * 96)
for f in [433e6, 915e6, 1575e6, 2.45e9, 5.8e9]:
    lam = C0 / f
    row = []
    for l in [1e-3, 3e-3, 5e-3, 10e-3, 20e-3]:
        se = 20 * np.log10(lam / (2 * l)) if l < lam / 2 else 0.0
        row.append(f"{l*1e3:4.0f}mm {se:5.1f}")
    print(f"  {f/1e9:5.3f} GHz single-slot SE (dB) by slot length: " + "; ".join(row))
for dh, t in [(1e-3, 0.2e-3), (2e-3, 0.2e-3), (3e-3, 0.3e-3)]:
    print(f"  circular hole {dh*1e3:.0f} mm in a {t*1e3:.1f} mm wall: extra below-cutoff attenuation 32*t/d = {32*t/dh:4.1f} dB"
          f" (TE11 cutoff {1.841*C0/(np.pi*dh)/1e9:.0f} GHz)")
n = 20
print(f"  N equal apertures close together: SE falls by ~20 log10(sqrt N) to 20 log10 N; N = {n}: {10*np.log10(n):.0f}-{20*np.log10(n):.0f} dB")
se_seam = 20 * np.log10((C0 / 2.45e9) / (2 * 5e-3))
check("solder points 5 mm apart leave only ~22 dB at 2.45 GHz", 20 < se_seam < 24, f"({se_seam:.1f} dB)")

print("\n" + "=" * 96)
print("4. Filtering a wire that leaves a can (50-ohm source/load; C with ESL 0.4 nH, ESR 0.1 ohm; bead model)")
print("=" * 96)


def zc(f, C, L=0.4e-9, R=0.1):
    w = 2 * np.pi * f
    return R + 1j * w * L + 1 / (1j * w * C)


def zbead(f, R0=600.0, f0=100e6, fpk=800e6):
    """crude 600 ohm@100 MHz bead: series R-L || C (peak ~fpk). L chosen for ~0.8*R0 at f0."""
    w = 2 * np.pi * f
    L = 0.9 * R0 / (2 * np.pi * f0)
    Cp = 1 / ((2 * np.pi * fpk) ** 2 * L)
    Rp = 1.2 * R0
    Y = 1 / (1j * w * L) + 1j * w * Cp + 1 / Rp
    return 1 / Y


def il_db(Zser=None, Zsh1=None, Zsh2=None, f=None, z0=50.0):
    M = np.eye(2, dtype=complex)
    if Zsh1 is not None:
        M = M @ np.array([[1, 0], [1 / Zsh1, 1]])
    if Zser is not None:
        M = M @ np.array([[1, Zser], [0, 1]])
    if Zsh2 is not None:
        M = M @ np.array([[1, 0], [1 / Zsh2, 1]])
    A, B, Cc, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
    s21 = 2 / (A + B / z0 + Cc * z0 + D)
    return -20 * np.log10(abs(s21))


fl = [100e6, 433e6, 915e6, 1575e6, 2.45e9]
print("  " + " " * 34 + "".join(f"{f/1e6:>9.0f}M" for f in fl))
rows = {
    "shunt 100 pF": [il_db(Zsh1=zc(f, 100e-12), f=f) for f in fl],
    "shunt 10 pF": [il_db(Zsh1=zc(f, 10e-12), f=f) for f in fl],
    "series bead 600R@100MHz": [il_db(Zser=zbead(f), f=f) for f in fl],
    "pi: 100 pF - bead - 100 pF": [il_db(Zser=zbead(f), Zsh1=zc(f, 100e-12), Zsh2=zc(f, 100e-12), f=f) for f in fl],
    "pi: 10 pF - bead - 10 pF": [il_db(Zser=zbead(f), Zsh1=zc(f, 10e-12), Zsh2=zc(f, 10e-12), f=f) for f in fl],
    "pi: (100p||10p) - bead - (100p||10p)": [il_db(Zser=zbead(f), Zsh1=1 / (1 / zc(f, 100e-12) + 1 / zc(f, 10e-12)),
                                              Zsh2=1 / (1 / zc(f, 100e-12) + 1 / zc(f, 10e-12)), f=f) for f in fl],
}
for k, v in rows.items():
    print(f"  {k:34s}" + "".join(f"{x:10.1f}" for x in v) + "  dB")
check("a C-bead-C pi gives > 25 dB at 915 MHz in 50 ohm", rows["pi: 100 pF - bead - 100 pF"][2] > 25,
      f"({rows['pi: 100 pF - bead - 100 pF'][2]:.1f} dB)")
print("  NB: lumped-model values above ~50-60 dB are not achievable in practice - stray coupling around the filter,")
print("  ground-via inductance and can-wall leakage cap real feedthrough filtering at roughly 40-60 dB.")
print("  (in a real can the source/load impedances are not 50 ohm: a low-impedance supply line gains less from a"
      " series bead, a high-impedance signal line gains less from a shunt cap)")

print("\n" + "=" * 96)
print("5. Isolation budget: 2 W (33 dBm) 433 MHz downlink vs a GNSS receiver on the same board")
print("=" * 96)
P_tx = 33.0
ant_iso = 20.0          # antenna-to-antenna coupling on a small airframe (u-blox: ~20 dB achievable in handhelds)
saw_rej = 40.0          # GNSS front-end SAW/notch rejection at 433 MHz (assumed; check module data)
lna_p1db_in = -10.0     # typical GNSS LNA input P1dB order of magnitude (assumed)
at_lna = P_tx - ant_iso
after_saw = at_lna - saw_rej
print(f"  433 MHz at the GNSS antenna port: {at_lna:.0f} dBm; after {saw_rej:.0f} dB of front-end rejection: {after_saw:.0f} dBm"
      f" vs LNA P1dB ~{lna_p1db_in:.0f} dBm -> margin {lna_p1db_in-after_saw:.0f} dB")
# harmonics landing near GNSS L1? 433.125 x n
for fc in [433.125e6, 868e6, 915e6, 920.125e6]:
    near = [(n, n * fc) for n in range(2, 8) if abs(n * fc - 1575.42e6) < 60e6]
    print(f"  carrier {fc/1e6:8.3f} MHz: harmonics within 60 MHz of L1: {near if near else 'none'}")
check("with 20 dB antenna isolation and 40 dB front-end rejection a 2 W 433 MHz TX stays > 10 dB below GNSS LNA P1dB",
      lna_p1db_in - after_saw > 10)

print("\nALL CHECKS PASSED" if ok_all else "\nSOME CHECKS FAILED")
