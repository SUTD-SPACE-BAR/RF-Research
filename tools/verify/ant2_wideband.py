#!/usr/bin/env python3
"""ant2_wideband.py -- checks for kb/08-antennas/multiband-and-wideband-antennas.md (W5-E2).

Pre-registered expectations (written before the first run):
 1. Infinite monocone over ground Z0 = 60 ln cot(theta/2): 50 ohm at theta = 47.0 deg (Stearns QEX 2007);
    biconical dipole Z0 = 120 ln cot(theta/2): 50 ohm at ~67 deg, 100 ohm at ~47 deg.
 2. Infinite planar bow-tie Z = eta0 K(k)/K(k'), k = tan^2(pi/4 - alpha/4): alpha = 90 deg (self-complementary)
    gives eta0/2 = 188.4 ohm; 50 ohm needs a flare angle close to 180 deg (planar bow-ties are high-Z).
 3. NEC-2 wire-cage discone (16 + 16 rods, theta = 30 deg, first resonance 70 MHz rule, Nail R/L = 0.72 sin theta):
    VSWR(50) < 2.5 over most of 100-700 MHz (> 5:1 range), rising steeply below ~80 MHz; peak gain 0-4 dBi with
    the beam tilting below the horizon at the top of the range.
 4. Receive-only noise-limited operation (P.372 factors): a -30 dB efficient antenna costs < 1 dB SNR at 7 MHz
    residential, but a -3 dB loss costs > 2 dB SNR at 433 MHz with a 3 dB NF receiver.
Run: python3 tools/verify/ant2_wideband.py     (~1-3 min)
"""
import numpy as np
import PyNEC
from scipy.special import ellipk

C0 = 299792458.0
ETA0 = 376.730313
ok = True


def check(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(f"[{'PASS' if cond else 'MISS'}] {name} {detail}")


print("=== 1. Conical antennas: characteristic impedance vs half-angle (from the axis) ===")
for th in (10, 20, 30, 39, 47, 60, 66.8, 70):
    t = np.radians(th)
    print(f"  theta = {th:5.1f} deg: monocone {60*np.log(1/np.tan(t/2)):6.1f} ohm, bicone {120*np.log(1/np.tan(t/2)):6.1f} ohm")
th50 = np.degrees(2 * np.arctan(np.exp(-50 / 60)))
th50b = np.degrees(2 * np.arctan(np.exp(-50 / 120)))
th100b = np.degrees(2 * np.arctan(np.exp(-100 / 120)))
print(f"  50-ohm monocone: {th50:.2f} deg; 50-ohm bicone: {th50b:.1f} deg; 100-ohm bicone {th100b:.1f} deg; "
      f"300-ohm bicone {np.degrees(2*np.arctan(np.exp(-300/120))):.1f} deg")
check("50-ohm monocone at 47.0 deg", abs(th50 - 47.0) < 0.1)

print("\n=== 2. Infinite planar bow-tie: Z = eta0 K(k)/K(k'), k = tan^2(pi/4 - alpha/4) ===")


def bowtie(alpha_deg):
    k = np.tan(np.pi / 4 - np.radians(alpha_deg) / 4) ** 2
    m, m1 = k * k, 1 - k * k                    # scipy ellipk takes m = k^2
    return ETA0 * ellipk(m) / ellipk(m1)


for al in (30, 60, 90, 120, 150, 170, 175):
    print(f"  flare angle {al:3d} deg: Z = {bowtie(al):6.1f} ohm")
check("90-deg bow-tie = eta0/2 (self-complementary)", abs(bowtie(90) - ETA0 / 2) < 0.05, f"({bowtie(90):.2f})")
check("Z(alpha) Z(180-alpha) = eta0^2/4 (Babinet)", abs(bowtie(60) * bowtie(120) - ETA0 ** 2 / 4) < 1.0)
from scipy.optimize import brentq
a50 = brentq(lambda a: bowtie(a) - 50, 90, 179.9)
a100 = brentq(lambda a: bowtie(a) - 100, 90, 179.9)
print(f"  50 ohm needs alpha = {a50:.1f} deg, 100 ohm alpha = {a100:.1f} deg")

print("\n=== 3. NEC-2 discone: 16 + 16 rods, theta = 30 deg, f_low design 100 MHz ===")
f_res1 = 0.7 * 100e6
lam1 = C0 / f_res1
th = np.radians(30.0)
RL = 0.72 * np.sin(th)            # Nail: disc radius / cone slant length
Lc = lam1 / 2 / (1 + RL)
Rd = RL * Lc
gap, a_rod, nw = 0.015, 1.5e-3, 16
print(f"  first resonance {f_res1/1e6:.0f} MHz -> R + L = lambda/2 = {lam1/2:.3f} m; R/L = {RL:.2f}: "
      f"cone slant {Lc:.3f} m, disc radius {Rd:.3f} m, cone base diameter {2*Lc*np.sin(th):.3f} m, "
      f"height {Lc*np.cos(th)+gap:.3f} m")


def discone(freqs, fmax=700e6, pattern_at=()):
    dl = C0 / fmax / 20
    c = PyNEC.nec_context()
    g = c.get_geometry()
    tag = 1
    g.wire(tag, 1, 0, 0, -gap, 0, 0, 0, a_rod, 1, 1)      # feed wire (1 segment) apex -> disc centre
    for i in range(nw):
        ph = 2 * np.pi * i / nw
        tag += 1
        g.wire(tag, max(3, int(np.ceil(Rd / dl))), 0, 0, 0, Rd * np.cos(ph), Rd * np.sin(ph), 0, a_rod, 1, 1)
        tag += 1
        g.wire(tag, max(3, int(np.ceil(Lc / dl))), 0, 0, -gap, Lc * np.sin(th) * np.cos(ph),
               Lc * np.sin(th) * np.sin(ph), -gap - Lc * np.cos(th), a_rod, 1, 1)
    c.geometry_complete(0)
    c.gn_card(-1, 0, 0, 0, 0, 0, 0, 0)
    c.ex_card(0, 1, 1, 0, 1.0, 0, 0, 0, 0, 0)
    Z = []
    pats = {}
    k = 0
    kr = 0
    for fm in freqs:
        c.fr_card(0, 1, fm / 1e6, 0)
        if any(abs(fm - p) < 1 for p in pattern_at):
            c.rp_card(0, 181, 1, 0, 0, 0, 0, 0.0, 0.0, 1.0, 0.0, 0, 0)
            pats[fm] = np.array(c.get_radiation_pattern(kr).get_gain()).ravel()
            kr += 1
        else:
            c.xq_card(0)
        Z.append(complex(c.get_input_parameters(k).get_impedance()[0]))
        k += 1
    return np.array(Z), pats


fs = np.concatenate([np.arange(40e6, 100e6, 5e6), np.arange(100e6, 701e6, 20e6)])
pat_f = (100e6, 300e6, 500e6, 700e6)
fs = np.unique(np.concatenate([fs, pat_f]))
Z, pats = discone(fs, pattern_at=pat_f)
G = np.abs((Z - 50) / (Z + 50))
V = (1 + G) / (1 - G)
for fm, z, v in zip(fs, Z, V):
    if fm in pat_f or abs(fm / 1e6 % 60) < 1 or fm < 100e6:
        extra = ""
        if fm in pats:
            gp = pats[fm]
            el = 90 - np.arange(181)
            extra = (f"; gain at horizon {gp[90]:5.2f} dBi, peak {gp.max():5.2f} dBi at elevation {el[np.argmax(gp)]:+d} deg")
        print(f"   {fm/1e6:5.0f} MHz: Z = {z.real:6.1f}{z.imag:+7.1f}j ohm, VSWR {v:5.2f}{extra}")
band = fs[(V < 2.5)]
inband = (fs >= 100e6) & (fs <= 700e6)
frac = np.mean(V[inband] < 2.5)
print(f"  VSWR < 2.5 at {100*frac:.0f} % of the 100-700 MHz points; VSWR < 2.5 from {band.min()/1e6:.0f} MHz upward "
      f"(max VSWR 100-700 MHz = {V[inband].max():.2f}); VSWR at 50 MHz = {np.interp(50e6, fs, V):.1f}")
check("discone VSWR < 2.5 on >= 80 % of 100-700 MHz", frac >= 0.8)
pf = np.arange(100e6, 701e6, 50e6)
_, pp = discone(pf, pattern_at=tuple(pf))
el = 90 - np.arange(181)
print("  horizon gain / gain at +10 deg / peak (elevation) vs frequency:")
for fm in pf:
    gp = pp[fm]
    print(f"    {fm/1e6:4.0f} MHz: {gp[90]:6.2f} / {gp[80]:6.2f} dBi / {gp.max():5.2f} dBi at {el[np.argmax(gp)]:+d} deg")
check("discone VSWR > 4 at 50 MHz (below first resonance)", np.interp(50e6, fs, V) > 4)

print("\n=== 4. Receive-only: SNR penalty of an inefficient antenna (ITU-R P.372 external noise) ===")
# f_sys referred to the antenna = fa + (lc - 1) + lc (fr - 1)  (antenna loss lc at T0, receiver noise factor fr)
cases = (("7 MHz, residential", 72.5 - 27.7 * np.log10(7.0), 10.0),
         ("14 MHz, quiet rural", 53.6 - 28.6 * np.log10(14.0), 10.0),
         ("100 MHz FM band, residential", 72.5 - 27.7 * np.log10(100.0), 6.0),
         ("144 MHz, rural", 67.2 - 27.7 * np.log10(144.0), 3.0),
         ("433 MHz, residential (P.372 Table 3: 4 dB)", 4.0, 3.0),
         ("915 MHz, sky only (Fa ~ -10 dB)", -10.0, 3.0),
         ("1575 MHz GNSS, sky (Fa ~ -16 dB)", -16.0, 1.5))
for name, Fa, NF in cases:
    fa, fr = 10 ** (Fa / 10), 10 ** (NF / 10)
    base = fa + fr - 1
    row = []
    for eff_db in (-1, -3, -10, -20, -30):
        lc = 10 ** (-eff_db / 10)
        row.append(10 * np.log10((fa + (lc - 1) + lc * (fr - 1)) / base))
    print(f"  {name:45s} Fa = {Fa:5.1f} dB, NF {NF:4.1f} dB: SNR loss for efficiency -1/-3/-10/-20/-30 dB = "
          + "/".join(f"{x:.1f}" for x in row) + " dB")
fa7 = 10 ** ((72.5 - 27.7 * np.log10(7.0)) / 10)
loss7 = 10 * np.log10((fa7 + 999 + 1000 * 9) / (fa7 + 9))
fa433, fr433 = 10 ** 0.4, 10 ** 0.3
loss433 = 10 * np.log10((fa433 + 1 + 2 * (fr433 - 1)) / (fa433 + fr433 - 1))
check("-30 dB efficiency costs < 1 dB at 7 MHz residential", loss7 < 1.0, f"({loss7:.2f} dB)")
check("-3 dB efficiency costs > 2 dB at 433 MHz (NF 3 dB, Fa 4 dB)", loss433 > 2.0, f"({loss433:.2f} dB)")

print("\n=== 5. Frequency-independent antennas: band limits ===")
for Dout, din in ((0.15, 0.01), (0.30, 0.012)):
    print(f"  spiral D_out = {Dout*100:.0f} cm, feed-region d_in = {din*1000:.0f} mm: f_low ~ c/(pi D_out) = "
          f"{C0/(np.pi*Dout)/1e9:.2f} GHz, f_high ~ c/(pi d_in) = {C0/(np.pi*din)/1e9:.1f} GHz "
          f"({C0/(np.pi*din)/(C0/(np.pi*Dout)):.0f}:1)")
for flo in (1e9, 2e9, 3e9):
    W = C0 / flo / 2
    print(f"  Vivaldi f_low {flo/1e9:.0f} GHz: aperture width ~ lambda0/2 = {W*1e3:.0f} mm "
          f"(on FR-4 with eps_eff ~ 1.5-2: {W/np.sqrt(2)*1e3:.0f}-{W/np.sqrt(1.5)*1e3:.0f} mm)")
# exponential taper y(x) = +-(w/2) exp(R x), from slot width w at x=0 to aperture W at x = Lt
for (w, W, Lt) in ((0.5e-3, 75e-3, 100e-3),):
    R = np.log(W / w) / Lt
    xs = np.linspace(0, Lt, 6)
    print(f"  taper w = {w*1e3} mm -> W = {W*1e3:.0f} mm over L = {Lt*1e3:.0f} mm: opening rate R = {R:.1f} 1/m; "
          "half-width at x = " + ", ".join(f"{x*1e3:.0f} mm: {w/2*np.exp(R*x)*1e3:.2f}" for x in xs))

print("\nALL PASS" if ok else "\nSOME MISSES (see above)")
