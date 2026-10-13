#!/usr/bin/env python3
"""
e10_radar_apps.py — numbers for kb/11-radar/radar-applications-gpr-through-wall-sensing.md (W5-E10).

 1. GPR: wave speed and attenuation of geological materials (Davis & Annan 1989 table as reproduced by
    UBC GPG) from the exact lossy-medium formula; checks the low-loss shortcut 1636 sigma/sqrt(er) dB/m.
 2. GPR depth for a given system performance (dB) — planar reflector, two-way spreading + absorption.
 3. GPR resolution: vertical v/(2B) and lambda/4, horizontal first-Fresnel radius sqrt(lambda d / 2).
 4. Through-wall: the "flash" vs a human echo (Wi-Vi wall-loss table, Adib & Katabi 2013).
 5. Harmonic radar range law: square-law diode -> P_r ~ P_t^2 / R^6 (verified numerically);
    linear (saturated) regime -> R^-4.
 6. Doppler / phase numbers: RCWL-0516 at 3.181 GHz, 24 GHz, 60 GHz (vital signs).
 7. Range resolution c/(2B) for LD2410 (0.75 m), automotive 76-81 GHz (4 GHz), Wi-Fi CSI path c/B.
 8. Hobby weather radar: rain echo vs noise for a 10 GHz FMCW with a dish.

Run:  python3 tools/verify/e10_radar_apps.py
"""
import math

C = 299792458.0
EPS0 = 8.8541878128e-12
MU0 = 4e-7 * math.pi
FAIL = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAIL.append(name)


def alpha_np(f, er, sigma):
    """Exact attenuation constant [Np/m] of a lossy non-magnetic medium (conduction loss only)."""
    w = 2 * math.pi * f
    eps = er * EPS0
    lt = sigma / (w * eps)
    return w * math.sqrt(MU0 * eps / 2) * math.sqrt(math.sqrt(1 + lt ** 2) - 1)


def beta(f, er, sigma):
    w = 2 * math.pi * f
    eps = er * EPS0
    lt = sigma / (w * eps)
    return w * math.sqrt(MU0 * eps / 2) * math.sqrt(math.sqrt(1 + lt ** 2) + 1)


# ------------------------------------------------------------------ 1. materials
# (name, er (mid of range), sigma S/m (mid/log-mid of range), table velocity m/ns)
MATS = [
    ("Ice", 3.5, 0.01e-3, 0.16),
    ("Dry sand", 4.0, 0.01e-3, 0.15),
    ("Granite", 5.0, 0.1e-3, 0.13),
    ("Limestone", 6.0, 1.0e-3, 0.12),
    ("Fresh water", 80.0, 0.5e-3, 0.033),
    ("Saturated sand", 25.0, 0.3e-3, 0.06),
    ("Silt", 15.0, 10e-3, 0.07),
    ("Clay (moist)", 20.0, 50e-3, 0.06),
    ("Clay (wet, saline)", 30.0, 500e-3, 0.06),
    ("Sea water", 80.0, 3.0, 0.01),
]
print("1. Attenuation (dB/m) from conductivity alone, exact formula; v = c/sqrt(er)")
print(f"{'material':20s} {'er':>5s} {'sig mS/m':>9s} {'v m/ns':>7s} {'tbl':>5s} "
      f"{'100 MHz':>8s} {'400 MHz':>8s} {'1 GHz':>8s} {'lowloss':>8s} {'skin d@400M m':>13s}")
for name, er, sig, vt in MATS:
    v = C / math.sqrt(er) / 1e9
    a = [8.686 * alpha_np(f, er, sig) for f in (100e6, 400e6, 1e9)]
    ll = 1636 * sig / math.sqrt(er)
    depth = 1 / alpha_np(400e6, er, sig)
    print(f"{name:20s} {er:5.1f} {sig*1e3:9.2f} {v:7.3f} {vt:5.3f} {a[0]:8.3f} {a[1]:8.3f} {a[2]:8.3f} "
          f"{ll:8.3f} {depth:13.2f}")
check("low-loss shortcut 1636 sigma/sqrt(er) matches exact for dry sand",
      abs(8.686 * alpha_np(400e6, 4, 0.01e-3) - 1636 * 0.01e-3 / 2) / (1636 * 0.01e-3 / 2) < 0.01)
check("low-loss shortcut breaks for sea water (exact much lower at 100 MHz)",
      8.686 * alpha_np(100e6, 80, 3.0) < 0.6 * 1636 * 3.0 / math.sqrt(80))
check("velocity in dry sand 0.15 m/ns", abs(C / 2 / 1e9 - 0.15) < 0.001)
check("velocity in water 0.033 m/ns", abs(C / math.sqrt(80) / 1e9 - 0.0335) < 0.001)
check("1636 = 8.686 * 188.4 / 1 (= 8.686 * eta0/2)", abs(8.686 * 376.73 / 2 - 1636) < 1)


# water dielectric relaxation adds loss rising ~ f^2 below ~17 GHz (single Debye, 20 C, approx. ITU-R P.527)
print("\n1b. Pure-water Debye loss as an effective conductivity (eps_s 80.1, eps_inf 5.8, f_rel 17 GHz)")
for f in (100e6, 400e6, 1e9, 2.45e9):
    wt = f / 17e9
    epp = (80.1 - 5.8) * wt / (1 + wt ** 2)
    sig_eff = 2 * math.pi * f * EPS0 * epp
    print(f"  {f/1e6:6.0f} MHz: eps'' {epp:6.3f}, sigma_eff {sig_eff*1e3:8.2f} mS/m, "
          f"attenuation in water {1636*sig_eff/math.sqrt(80):7.2f} dB/m")
wt = 1e9 / 17e9
sig1g = 2 * math.pi * 1e9 * EPS0 * (74.3 * wt / (1 + wt ** 2))
check("water relaxation at 1 GHz ~ 0.24 S/m effective", 0.2 < sig1g < 0.3)

# ------------------------------------------------------------------ 2. depth
print("\n2. Max depth of a planar reflector for a given system performance Q (dB)")
print("   loss(d) = 2*alpha*d + 20log10(2d/1m) (image-source spreading) + 20log10(1/|Gamma|) + 10 dB coupling")


def max_depth(Q, a_db_m, gamma=0.3, coupling=10.0):
    lo, hi = 0.01, 200.0
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        loss = 2 * a_db_m * mid + 20 * math.log10(2 * mid) + 20 * math.log10(1 / gamma) + coupling
        if loss < Q:
            lo = mid
        else:
            hi = mid
    return lo


for name, er, sig, _ in MATS[:9]:
    a400 = 8.686 * alpha_np(400e6, er, sig)
    a100 = 8.686 * alpha_np(100e6, er, sig)
    d1, d2 = max_depth(100, a400), max_depth(120, a100)
    s1 = f"{d1:6.1f} m" if d1 < 199 else "  >200 m"
    s2 = f"{d2:6.1f} m" if d2 < 199 else "  >200 m"
    print(f"  {name:20s}: 400 MHz Q=100 dB -> {s1};   100 MHz Q=120 dB -> {s2}")
check("wet saline clay limits 400 MHz GPR to < 1 m", max_depth(100, 8.686 * alpha_np(400e6, 30, 0.5)) < 1.0)
check("dry sand allows > 10 m at 400 MHz with 100 dB", max_depth(100, 8.686 * alpha_np(400e6, 4, 1e-5)) > 10)

# ------------------------------------------------------------------ 3. resolution
print("\n3. GPR resolution")
for fc, er in ((400e6, 9.0), (1.6e9, 9.0), (100e6, 9.0)):
    v = C / math.sqrt(er)
    lam = v / fc
    B = fc  # typical impulse GPR: bandwidth ~ centre frequency
    dz = v / (2 * B)
    rf = math.sqrt(lam * 1.0 / 2)
    print(f"  fc {fc/1e6:6.0f} MHz, er {er}: lambda {lam:.3f} m, v/(2B) {dz:.3f} m, lambda/4 {lam/4:.3f} m, "
          f"Fresnel radius at 1 m {rf:.2f} m")
check("400 MHz in er=9: v/(2B) = 0.125 m", abs(C / 3 / (2 * 400e6) - 0.1249) < 1e-3)

# ------------------------------------------------------------------ 4. through-wall
print("\n4. Through-wall: flash vs human echo (2.4 GHz)")
lam = C / 2.44e9
Gt = Gr = 10 ** (6 / 10)  # 6 dBi patches
for wall, L1 in (("hollow 6 in", 9), ("concrete 8 in (est.)", 12), ("concrete 18 in", 18), ("reinforced", 40)):
    # wall reflection at 1 m, |Gamma|^2 ~ -6 dB treated as a large flat mirror: image at 2 m
    p_flash = Gt * Gr * lam ** 2 / (4 * math.pi * 2.0) ** 2 * 10 ** (-6 / 10)
    sigma_h = 0.5  # m^2 human at microwave (order of magnitude)
    R = 5.0
    p_h = Gt * Gr * lam ** 2 * sigma_h / ((4 * math.pi) ** 3 * R ** 4) * 10 ** (-2 * L1 / 10)
    ratio = 10 * math.log10(p_flash / p_h)
    print(f"  {wall:22s}: one-way {L1:2d} dB -> flash is {ratio:5.1f} dB above a person at 5 m")
    if wall == "concrete 18 in":
        r18 = ratio
check("flash exceeds human echo by > 40 dB behind 18-inch concrete", r18 > 40)

# ------------------------------------------------------------------ 5. harmonic radar
print("\n5. Harmonic radar range law (square-law diode tag)")


def harmonic_rx(Pt, R, k2=1.0, G=1.0, lam1=0.327, lam2=0.1635):
    S = Pt * G / (4 * math.pi * R ** 2)
    Pinc = S * G * lam1 ** 2 / (4 * math.pi)
    P2 = k2 * Pinc ** 2          # square-law conversion
    return P2 * G / (4 * math.pi * R ** 2) * G * lam2 ** 2 / (4 * math.pi)


r1 = harmonic_rx(1.0, 10.0)
r2 = harmonic_rx(1.0, 20.0)
slope = 10 * math.log10(r1 / r2) / (10 * math.log10(2))
p1 = harmonic_rx(2.0, 10.0)
print(f"  doubling range costs {10*math.log10(r1/r2):.1f} dB (R^-{slope:.1f}); doubling Pt gains "
      f"{10*math.log10(p1/r1):.1f} dB")
check("square-law harmonic radar ~ R^-6", abs(slope - 6) < 1e-6)
check("square-law harmonic radar ~ Pt^2", abs(10 * math.log10(p1 / r1) - 6.02) < 0.01)
print("  range vs TX power: R ~ Pt^(1/3): x10 power -> x%.2f range (linear radar: x%.2f)"
      % (10 ** (1 / 3), 10 ** 0.25))

# ------------------------------------------------------------------ 6. Doppler/phase
print("\n6. Doppler and phase sensitivity")
for f, lab in ((3.181e9, "RCWL-0516"), (10.525e9, "HB100"), (24.125e9, "24 GHz"), (60.5e9, "60 GHz")):
    lam = C / f
    print(f"  {lab:10s}: lambda {lam*1e3:6.1f} mm, {2/lam:6.1f} Hz per m/s, "
          f"breathing 5 mm -> {4*math.pi*5e-3/lam:5.2f} rad, heartbeat 0.3 mm -> {4*math.pi*0.3e-3/lam:5.3f} rad")
check("RCWL-0516 Doppler 21.2 Hz per m/s", abs(2 * 3.181e9 / C - 21.22) < 0.02)

# ------------------------------------------------------------------ 7. resolution
print("\n7. Range resolution")
for lab, B in (("LD2410 (24.0-24.25 GHz)", 250e6), ("LD2410 stated 0.75 m ->B", C / (2 * 0.75)),
               ("automotive 77-81 GHz", 4e9), ("Wi-Fi 20 MHz", 20e6), ("Wi-Fi 160 MHz", 160e6),
               ("UWB 500 MHz", 500e6)):
    print(f"  {lab:26s}: B {B/1e6:7.1f} MHz -> monostatic c/2B {C/(2*B):7.3f} m; bistatic path c/B {C/B:7.3f} m")
check("LD2410 0.75 m implies 200 MHz", abs(C / (2 * 0.75) / 1e6 - 199.9) < 0.2)
check("4 GHz -> 3.75 cm", abs(C / (2 * 4e9) - 0.0375) < 1e-4)

# ------------------------------------------------------------------ 8. hobby weather radar
print("\n8. Hobby 10 GHz FMCW weather radar: rain echo SNR")
f = 10.0e9
lam = C / f
Pt = 0.1  # 20 dBm
D = 0.6  # dish diameter m
G = 0.55 * (math.pi * D / lam) ** 2
theta = 70 * lam / D * math.pi / 180  # 3 dB beamwidth rad
dR = 30.0
eta = 10 ** (-55 / 10)  # 10 mm/h at 10 GHz (KB clutter page)
NF = 10 ** (6 / 10)
k = 1.380649e-23
T0 = 290
Tint = 0.1  # 100 ms dwell
for R in (500.0, 1000.0, 2000.0, 5000.0):
    V = math.pi * R ** 2 * theta * theta * dR / (8 * math.log(2))
    sig = eta * V
    Pr = Pt * G ** 2 * lam ** 2 * sig / ((4 * math.pi) ** 3 * R ** 4)
    N = k * T0 * NF / Tint
    print(f"  R {R/1e3:4.1f} km: G {10*math.log10(G):.1f} dBi, beam {math.degrees(theta):.2f} deg, "
          f"V {V:9.0f} m^3, sigma {10*math.log10(sig):6.1f} dBsm, SNR {10*math.log10(Pr/N):6.1f} dB")
    snr5 = 10 * math.log10(Pr / N)
check("10 GHz 20 dBm 0.6 m dish sees 10 mm/h rain at 5 km with > 10 dB SNR (100 ms)", snr5 > 10)

print("\nRESULT:", "ALL PASS" if not FAIL else f"{len(FAIL)} FAIL: {FAIL}")
