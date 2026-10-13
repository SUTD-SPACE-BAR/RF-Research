#!/usr/bin/env python3
"""
e3_frontend.py -- numerical checks for kb/14-sdr-dsp/sdr-front-end-protection-and-filtering.md

1. Field strength -> available power into a dipole: P = E^2 lambda^2 G / (480 pi^2); cross-checked
   against tools/rfcalc.units.field_dbuvm_to_dbm.
2. Levels at a ground-station input from nearby transmitters (Friis, far field).
3. Receiver cascades at 433 MHz: SDR alone / LNA->SDR / SAW->LNA->SDR / LNA->SAW->SDR / pad->SDR:
   NF, IIP3, noise floor in 125 kHz, SFDR (tools/rfcalc.noise.cascade).
4. Two-tone IM3 from two strong signals and the preselector rejection needed to keep IM3 below the floor.
5. Band-pass prototype rejection (Butterworth/Chebyshev) at nearby blockers: why skirts matter.
6. Limiter leakage vs SDR maximum input; pad needed after a limiter.
7. TVS / ESD diode: RF voltage vs working voltage (incl. mismatch) and return loss of its capacitance.
8. Bias tee: choke and DC-block values, insertion loss, coax voltage drop, power into a DC-shorted antenna.
9. Overload test: an n-th-order product moves n dB per dB of attenuation (memoryless polynomial model).
10. Antenna-to-antenna isolation at a launch site (Friis) and the resulting blocker level.

Run: python3 tools/verify/e3_frontend.py   (PASS/FAIL per check, < 2 s)
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from rfcalc.noise import Stage, cascade          # noqa: E402
from rfcalc.units import field_dbuvm_to_dbm      # noqa: E402

C = 299_792_458.0
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")


def fspl(f, d):
    return 20 * np.log10(4 * np.pi * d * f / C)


# ---------------------------------------------------------------- 1. field strength -> dBm
print("=== 1. Field strength to available power (half-wave dipole, G = 2.15 dBi) ===")
for f, e in [(100e6, 1.0), (100e6, 0.1), (100e6, 0.01), (433e6, 0.1), (935e6, 1.0)]:
    lam = C / f
    g = 10 ** (2.15 / 10)
    p = e ** 2 * lam ** 2 * g / (480 * np.pi ** 2)
    pdbm = 10 * np.log10(p / 1e-3)
    ref = field_dbuvm_to_dbm(20 * np.log10(e / 1e-6), f, 2.15)
    print(f"  {f/1e6:6.0f} MHz, E = {e*1e3:7.1f} mV/m -> {pdbm:6.1f} dBm (rfcalc {ref:6.1f} dBm)")
    check(f"  formula vs rfcalc at {f/1e6:.0f} MHz", abs(pdbm - ref) < 0.05)

# broadcast site example: 10 kW ERP at 3 km -> field and dipole power
erp = 10e3
eirp = erp * 10 ** (2.15 / 10)
e3k = np.sqrt(30 * eirp) / 3000
p3k = 10 * np.log10(e3k ** 2 * (C / 100e6) ** 2 * 10 ** 0.215 / (480 * np.pi ** 2) / 1e-3)
print(f"  10 kW ERP FM at 3 km: E = sqrt(30 EIRP)/d = {e3k*1e3:.0f} mV/m -> {p3k:.1f} dBm into a 100 MHz dipole")
check("10 kW ERP at 3 km gives ~0.23 V/m and ~-8 dBm", abs(e3k - 0.234) < 0.005 and abs(p3k + 7.7) < 0.3)

# ---------------------------------------------------------------- 2. nearby transmitters
print("\n=== 2. Power at the ground-station connector from nearby transmitters ===")
cases = [
    ("own 433 MHz uplink 2 W, dipoles, 5 m", 33, 2.15, 2.15, 433e6, 5),
    ("own 433 MHz uplink 2 W, 20 m", 33, 2.15, 2.15, 433e6, 20),
    ("other team 915 MHz 1 W, 10 m (rx Yagi 10 dBi side-lobe -5 dBi)", 30, 2.15, -5, 915e6, 10),
    ("cell site 940 MHz, 60 dBm EIRP (assumed), 300 m, 0 dBi", 60, 0, 0, 940e6, 300),
    ("phone/Wi-Fi 2.44 GHz 20 dBm EIRP, 2 m", 20, 0, 0, 2.44e9, 2),
]
lv = {}
for name, pt, gt, gr, f, d in cases:
    pr = pt + gt + gr - fspl(f, d)
    lv[name] = pr
    print(f"  {name:62s}: FSPL {fspl(f, d):5.1f} dB -> {pr:6.1f} dBm")
check("2 W at 5 m (433 MHz, dipoles) delivers about -2 dBm",
      abs(lv["own 433 MHz uplink 2 W, dipoles, 5 m"] - (33 + 4.3 - fspl(433e6, 5))) < 1e-9
      and -3 < lv["own 433 MHz uplink 2 W, dipoles, 5 m"] < 0)

# ---------------------------------------------------------------- 3. cascades at 433 MHz
print("\n=== 3. Receive chains at 433 MHz (B = 125 kHz) ===")
# Assumptions (labelled on the page): RTL-SDR NF 5.4 dB (LSF measured at 437 MHz), IIP3 -10 dBm at
# a moderate gain (illustrative; not published); TQP3M9036-class LNA NF 0.45 dB, G 19.8 dB,
# OIP3 +36 dBm -> IIP3 +16.2 dBm; SAW B39431B3710U410 IL 2 dB, IIP3 +40 (passive, assumed high);
# 10 dB pad.
SDR = Stage("SDR", 0.0, nf=5.4, iip3=-10.0)
LNA = Stage("LNA", 19.8, nf=0.45, iip3=16.2)
SAW = Stage("SAW", -2.0, iip3=40.0)
PAD = Stage("pad10", -10.0, iip3=60.0)
COAX = Stage("coax 3 dB", -3.0, iip3=70.0)
B = 125e3
chains = {
    "SDR alone": [SDR],
    "coax -> SDR": [COAX, SDR],
    "LNA -> SAW -> coax -> SDR": [LNA, SAW, COAX, SDR],
    "SAW -> LNA -> coax -> SDR": [SAW, LNA, COAX, SDR],
    "LNA -> coax -> SDR (no filter)": [LNA, COAX, SDR],
    "10 dB pad -> SDR": [PAD, SDR],
}
out = {}
for name, st in chains.items():
    r = cascade(st)[-1]
    nf, iip3 = r["NF_cum_dB"], r["IIP3_cum_dBm"]
    floor = -174 + nf + 10 * np.log10(B)
    sfdr = 2 / 3 * (iip3 - floor)
    out[name] = (nf, iip3, floor, sfdr)
    print(f"  {name:32s}: NF {nf:5.2f} dB, IIP3 {iip3:6.1f} dBm, floor {floor:7.1f} dBm, SFDR {sfdr:5.1f} dB")
check("LNA at the antenna gives NF < 1 dB", out["LNA -> SAW -> coax -> SDR"][0] < 1.0)
check("LNA in front lowers system IIP3 by ~ its gain (SDR-dominated)",
      abs((out["SDR alone"][1] - out["LNA -> coax -> SDR (no filter)"][1]) - (19.8 - 3.0)) < 1.5)
check("SAW before LNA costs ~2 dB NF", 1.7 < out["SAW -> LNA -> coax -> SDR"][0] - out["LNA -> SAW -> coax -> SDR"][0] < 2.1)
check("pad lowers sensitivity 10 dB but raises IIP3 10 dB (SFDR unchanged within 0.3 dB)",
      abs(out["10 dB pad -> SDR"][3] - out["SDR alone"][3]) < 0.3)

# ---------------------------------------------------------------- 4. IM3 and rejection needed
print("\n=== 4. IM3 from two blockers and required preselector rejection ===")


def im3_in(p, iip3):
    return 3 * p - 2 * iip3


for name in ["SDR alone", "LNA -> coax -> SDR (no filter)", "LNA -> SAW -> coax -> SDR"]:
    nf, iip3, floor, _ = out[name]
    pmax = (2 * iip3 + floor) / 3          # each tone so that IM3 = floor
    print(f"  {name:32s}: two equal blockers may reach {pmax:6.1f} dBm each before IM3 hits the floor")
# FM broadcast example: two stations at -20 dBm each at the antenna, chain LNA (wideband) -> SDR
nf, iip3, floor, _ = out["LNA -> coax -> SDR (no filter)"]
pb = -20.0
pmax = (2 * iip3 + floor) / 3
rej = pb - pmax
print(f"  two FM stations at {pb} dBm into the unfiltered LNA chain: IM3 {im3_in(pb, iip3):.1f} dBm (input-referred) "
      f"vs floor {floor:.1f} dBm -> need >= {rej:.1f} dB of rejection AHEAD of the LNA")
check("required rejection = (Pb - Pmax) and IM3 then equals floor", abs(im3_in(pb - rej, iip3) - floor) < 1e-9)

# ---------------------------------------------------------------- 5. band-pass skirt rejection
print("\n=== 5. Band-pass prototype rejection at a nearby blocker ===")


def bpf_rejection(f, f0, bw, n, ripple_db=None):
    om = abs(f / f0 - f0 / f) / (bw / f0)
    if ripple_db is None:     # Butterworth (bw = 3 dB bandwidth)
        return 10 * np.log10(1 + om ** (2 * n))
    eps = np.sqrt(10 ** (ripple_db / 10) - 1)   # Chebyshev (bw = ripple bandwidth)
    t = np.cosh(n * np.arccosh(om)) if om >= 1 else np.cos(n * np.arccos(om))
    return 10 * np.log10(1 + (eps * t) ** 2)


for (f0, bw, fb, label) in [(915e6, 26e6, 940e6, "US 902-928 filter vs 940 MHz downlink"),
                            (921e6, 8e6, 935e6, "SG 917-925 filter vs 935 MHz"),
                            (921e6, 8e6, 927e6, "SG 917-925 filter vs 927 MHz"),
                            (433.92e6, 1.74e6, 446e6, "433 SRD filter vs 446 MHz PMR"),
                            (433.92e6, 10e6, 100e6, "433 MHz 10 MHz-wide BPF vs FM 100 MHz")]:
    row = [f"n={n}: {bpf_rejection(fb, f0, bw, n):5.1f}" for n in (3, 5, 7)]
    ch = bpf_rejection(fb, f0, bw, 5, 0.1)
    print(f"  {label:42s} Butterworth {', '.join(row)} dB; Chebyshev 0.1 dB n=5: {ch:5.1f} dB")
check("Butterworth n=5, 915/26 MHz at 940 MHz ~ 27-28 dB", 26.5 < bpf_rejection(940e6, 915e6, 26e6, 5) < 29)

# ---------------------------------------------------------------- 6. limiter leakage
print("\n=== 6. Limiter leakage vs SDR maximum input ===")
leak = 11.5            # VLM-33-S+ typical leakage, dBm (13.0 dBm at 415 MHz with +30 dBm in)
maxin = {"HackRF One": -5.0, "SDRplay RSPdx-R2": 0.0, "R820T/RTL-SDR (chip)": 10.0}
for k, v in maxin.items():
    pad = max(0.0, 13.0 - v + 3.0)     # worst-case 415 MHz leakage + 3 dB margin
    print(f"  {k:22s}: max {v:+5.1f} dBm -> pad after limiter >= {pad:4.1f} dB (worst leakage 13 dBm + 3 dB margin)")
check("HackRF needs >= 21 dB of pad after a VLM-33-class limiter", 13.0 - (-5.0) + 3.0 == 21.0)

# ---------------------------------------------------------------- 7. TVS / ESD diodes
print("\n=== 7. TVS/ESD diode on an RF line ===")
Z0 = 50.0


def vpk(p_dbm, gamma=0.0):
    return np.sqrt(2 * Z0 * 10 ** (p_dbm / 10) * 1e-3) * (1 + gamma)


for p, g in [(24.5, 0.0), (33.0, 0.0), (33.0, 0.5), (30.0, 0.5), (10.0, 0.0)]:
    print(f"  {p:4.1f} dBm, |Gamma| {g:.1f}: peak RF voltage {vpk(p, g):5.2f} V")
p_ok = 10 * np.log10((5.3 / (1 + 0.5)) ** 2 / (2 * Z0) / 1e-3)
print(f"  ESD0P2RF-class (5.3 V working): max power without conduction {10*np.log10(5.3**2/(2*Z0)/1e-3):.1f} dBm "
      f"matched, {p_ok:.1f} dBm at VSWR 3")
check("2 W at VSWR 3 reaches ~21 V peak", abs(vpk(33.0, 0.5) - 21.2) < 0.2)
for cpf in [0.2, 0.5, 1.5]:
    rl = []
    for f in [433e6, 915e6, 1575.42e6, 2.44e9]:
        y = 1j * 2 * np.pi * f * cpf * 1e-12
        gam = -y * Z0 / (2 + y * Z0)
        rl.append(f"{f/1e6:.0f}: RL {-20*np.log10(abs(gam)):4.1f} dB / IL {-20*np.log10(abs(2/(2+y*Z0))):.3f} dB")
    print(f"  shunt {cpf} pF: " + "; ".join(rl))
y = 1j * 2 * np.pi * 1575.42e6 * 1.5e-12
check("1.5 pF shunt at 1575 MHz gives RL < 20 dB (visible mismatch)", -20 * np.log10(abs(-y * Z0 / (2 + y * Z0))) < 20)

# ---------------------------------------------------------------- 8. bias tee
print("\n=== 8. Bias tee components and DC budget ===")
fmin, fmax = 400e6, 1700e6
L = 10 * Z0 / (2 * np.pi * fmin)
Cb = 1 / (2 * np.pi * fmin * Z0 / 10)
print(f"  choke for X_L >= 10 Z0 at {fmin/1e6:.0f} MHz: L >= {L*1e9:.0f} nH (needs SRF > {fmax/1e9:.1f} GHz)")
print(f"  DC block for X_C <= Z0/10 at {fmin/1e6:.0f} MHz: C >= {Cb*1e12:.0f} pF")
for xl in [5 * Z0, 10 * Z0, 20 * Z0]:
    yl = 1 / (1j * xl)
    print(f"  shunt choke X_L = {xl:.0f} ohm: insertion loss {-20*np.log10(abs(2/(2+yl*Z0))):.3f} dB, "
          f"RL {-20*np.log10(abs(-yl*Z0/(2+yl*Z0))):.1f} dB")
check("X_L = 10 Z0 shunt costs < 0.02 dB", -20 * np.log10(abs(2 / (2 + Z0 / (1j * 10 * Z0)))) < 0.02)
# DC drop: 4.5 V bias, 50 mA LNA, 20 m of coax with 0.06 ohm/m loop resistance (assumed RG-58-class)
for i_ma, length, r_loop in [(50, 20, 0.06), (180, 20, 0.06), (50, 30, 0.02)]:
    drop = i_ma * 1e-3 * length * r_loop
    print(f"  {i_ma} mA over {length} m at {r_loop} ohm/m loop: drop {drop:.3f} V -> {4.5-drop:.2f} V at the LNA")
check("50 mA over 20 m RG-58-class drops < 0.1 V", 0.05 * 20 * 0.06 < 0.1)
print("  DC-shorted antenna (folded dipole, J-pole, shunt-fed): bias tee sees a short -> current limit or damage")

# ---------------------------------------------------------------- 9. overload n dB per dB test
print("\n=== 9. Pad test: n-th order products move n dB per dB ===")
fs, n = 4096.0, 4096
t = np.arange(n) / fs
a = [1.0, 0.0, 0.05, 0.02, 0.01]       # y = x + a2 x^2 + a3 x^3 + a4 x^4 (memoryless)
f1 = 101.0


def harmonics(amp):
    x = amp * np.cos(2 * np.pi * f1 * t)
    y = x + a[2] * x ** 2 + a[3] * x ** 3 + a[4] * x ** 4
    Y = np.abs(np.fft.rfft(y)) / n * 2
    return [20 * np.log10(Y[int(k * f1)] + 1e-300) for k in (1, 2, 3, 4)]


h0, h1 = harmonics(0.3), harmonics(0.3 * 10 ** (-10 / 20))
for k in range(4):
    print(f"  order {k+1}: drops {h0[k]-h1[k]:5.2f} dB for a 10 dB pad")
check("2nd/3rd/4th harmonics drop ~20/30/40 dB", abs((h0[1] - h1[1]) - 20) < 1 and abs((h0[2] - h1[2]) - 30) < 1.5
      and abs((h0[3] - h1[3]) - 40) < 1.5)
print(f"  broadcast FM at 102.5 MHz: 4th harmonic at {4*102.5:.0f} MHz with 4 x 75 = {4*75} kHz deviation")

# ---------------------------------------------------------------- 10. antenna isolation
print("\n=== 10. Antenna-to-antenna isolation (far field, co-polar, main beams) ===")
for f, d in [(433e6, 2), (433e6, 10), (915e6, 2), (915e6, 10)]:
    iso = fspl(f, d) - 2 * 2.15
    rx = 33 - iso
    print(f"  {f/1e6:.0f} MHz, {d:2d} m, two dipoles: isolation {iso:5.1f} dB -> 2 W TX gives {rx:6.1f} dBm at the RX")
check("433 MHz, 10 m: isolation ~41 dB", abs((fspl(433e6, 10) - 4.3) - 41.0) < 0.5)
lam = C / 433e6
print(f"  far-field condition d >> lambda/2pi = {lam/2/np.pi*100:.0f} cm (near-field coupling is worse than Friis predicts)")

print(f"\n{sum(results)}/{len(results)} checks passed")
print("ALL PASS" if all(results) else "SOME FAILED")
