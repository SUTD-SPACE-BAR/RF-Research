#!/usr/bin/env python3
"""
e6_beginner_numbers.py -- numerical checks for the W5-E6 beginner pages:
  kb/00-math-foundations/rf-concepts-for-beginners.md
  kb/00-math-foundations/rf-learning-roadmap.md
  kb/20-projects-recipes/beginner-project-ladder.md
  kb/19-regulations-safety/rf-exposure-safety.md  (section "RF is non-ionising")
  kb/14-sdr-dsp/sdr-gain-staging-and-reception-recipes.md (Doppler / horizon numbers)

1. Photon energy E = h f (eV) from mains to X-rays; ratio to the ~10-12.4 eV ionisation scale;
   frequency of a 12.4 eV photon (100 nm); thermal energy kT at body temperature.
2. Wavelengths lambda = c/f for the bands used in the pages.
3. dB / dBm arithmetic used in the beginner page (2 W = 33 dBm, -100 dBm in volts at 50 ohm ...).
4. Half-wave dipole and quarter-wave whip lengths at 433.92 MHz, 137.5 MHz (V-dipole) and 1090 MHz.
5. Cable velocity factor from the open-circuit quarter-wave resonance (NanoVNA project).
6. Thermal noise floor kTB in common receiver bandwidths.
7. Radio horizon for ADS-B (4/3-earth): aircraft at 35 000 ft vs a 10 m antenna.
8. HB100 Doppler: f_d = 2 v f0 / c (Hz per m/s, per km/h, per mph).
9. LEO satellite Doppler at 137.9 MHz (Meteor-M, h ~ 830 km) and 145.8 MHz (ISS, h ~ 420 km).
10. Free-space path loss 433 MHz vs 2.45 GHz between isotropic antennas, and between fixed-area antennas.

Run: python3 tools/verify/e6_beginner_numbers.py   (PASS/FAIL per check, < 1 s)
"""
import numpy as np

C = 299_792_458.0          # m/s (exact)
H = 6.626_070_15e-34       # J s (exact, SI 2019)
QE = 1.602_176_634e-19     # C (exact) -> 1 eV in J
KB = 1.380_649e-23         # J/K (exact)
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")


def close(a, b, rel=1e-3):
    return abs(a - b) <= rel * abs(b)


# ---------------------------------------------------------------- 1. photon energies
print("\n§1 Photon energy E = h f")
cases = [
    ("mains 50 Hz", 50.0),
    ("AM broadcast 1 MHz", 1e6),
    ("LoRa 433.92 MHz", 433.92e6),
    ("LoRa 915 MHz", 915e6),
    ("GPS L1 1575.42 MHz", 1575.42e6),
    ("Wi-Fi / microwave oven 2.45 GHz", 2.45e9),
    ("5.8 GHz", 5.8e9),
    ("HB100 10.525 GHz", 10.525e9),
    ("automotive radar 77 GHz", 77e9),
    ("top of RF, 300 GHz", 300e9),
    ("red light 700 nm", C / 700e-9),
    ("green light 550 nm", C / 550e-9),
    ("UV-C lamp 254 nm", C / 254e-9),
    ("EU ionising boundary 100 nm", C / 100e-9),
    ("medical X-ray ~ 60 keV", 60e3 * QE / H),
]
E_ION = 12.4          # eV, photon energy at 100 nm (EURATOM 1996 definition boundary)
print(f"{'source':34s} {'f (Hz)':>11s} {'E (eV)':>11s} {'E / 12.4 eV':>12s}")
table = {}
for name, f in cases:
    e = H * f / QE
    table[name] = e
    print(f"{name:34s} {f:11.3e} {e:11.3e} {e / E_ION:12.3e}")
check("433.92 MHz photon = 1.79 micro-eV", close(table["LoRa 433.92 MHz"], 1.7946e-6, 1e-3),
      f"({table['LoRa 433.92 MHz']:.4e} eV)")
check("2.45 GHz photon = 1.01e-5 eV", close(table["Wi-Fi / microwave oven 2.45 GHz"], 1.0132e-5, 1e-3))
check("77 GHz photon = 0.318 meV", close(table["automotive radar 77 GHz"], 3.184e-4, 2e-3))
check("100 nm photon = 12.4 eV (hc = 1239.84 eV nm)", close(table["EU ionising boundary 100 nm"], 12.398, 1e-3))
f_100nm = C / 100e-9
check("100 nm <-> 3.0e15 Hz", close(f_100nm, 2.998e15, 1e-3), f"({f_100nm:.4e} Hz)")
ratio_433 = E_ION / table["LoRa 433.92 MHz"]
ratio_77 = E_ION / table["automotive radar 77 GHz"]
check("433 MHz photon is ~7 million times below 12.4 eV", 6.5e6 < ratio_433 < 7.5e6, f"(ratio {ratio_433:.3e})")
check("even 77 GHz is ~39 000 times below", 3.5e4 < ratio_77 < 4.3e4, f"(ratio {ratio_77:.3e})")
f_10eV = 10 * QE / H
check("10 eV photon is at 2.42e15 Hz (124 nm, far UV)", close(f_10eV, 2.418e15, 1e-3),
      f"({f_10eV:.4e} Hz, {C / f_10eV * 1e9:.1f} nm)")
kT_body = KB * 310.15 / QE
check("kT at 37 C = 26.7 meV", close(kT_body, 0.02673, 2e-3), f"({kT_body * 1e3:.2f} meV)")
check("433 MHz photon is ~15 000 x smaller than kT (thermal jiggling)", 1.4e4 < kT_body / table["LoRa 433.92 MHz"] < 1.6e4,
      f"(ratio {kT_body / table['LoRa 433.92 MHz']:.0f})")
check("visible green photon ~2.25 eV (a million times an RF photon, still below 12.4 eV)",
      close(table["green light 550 nm"], 2.254, 2e-3))
# Photon count: how many photons per second does a 2 W 433 MHz transmitter emit?
n_ph = 2.0 / (H * 433.92e6)
check("2 W at 433.92 MHz = 7.0e24 photons/s", close(n_ph, 6.956e24, 2e-3), f"({n_ph:.3e} /s)")

# ---------------------------------------------------------------- 2. wavelengths
print("\n§2 Wavelengths")
wl = {}
for name, f in [("ADS-B 1090 MHz", 1090e6), ("LoRa 433.92 MHz", 433.92e6), ("LoRa 868 MHz", 868e6),
                ("LoRa 915 MHz", 915e6), ("SG LoRa 923 MHz", 923e6), ("GPS L1", 1575.42e6),
                ("2.45 GHz", 2.45e9), ("HB100 10.525 GHz", 10.525e9), ("Meteor 137.9 MHz", 137.9e6),
                ("FM 100 MHz", 100e6), ("AM 1 MHz", 1e6), ("mains 50 Hz", 50.0)]:
    wl[name] = C / f
    print(f"  {name:20s} lambda = {C / f:12.5g} m")
check("433.92 MHz: lambda = 0.691 m", close(wl["LoRa 433.92 MHz"], 0.6909, 1e-3))
check("915 MHz: lambda = 0.328 m", close(wl["LoRa 915 MHz"], 0.3276, 1e-3))
check("2.45 GHz: lambda = 12.2 cm", close(wl["2.45 GHz"], 0.12236, 1e-3))
check("50 Hz: lambda = 6000 km", close(wl["mains 50 Hz"], 5.996e6, 1e-3))

# ---------------------------------------------------------------- 3. dB arithmetic
print("\n§3 dB / dBm")
dbm = lambda p_w: 10 * np.log10(p_w / 1e-3)
w_from_dbm = lambda d: 1e-3 * 10 ** (d / 10)
check("2 W = 33.0 dBm", close(dbm(2.0), 33.01, 1e-3), f"({dbm(2.0):.2f} dBm)")
check("10 mW = 10 dBm", close(dbm(0.01), 10.0, 1e-9))
check("+3 dB = x1.995 power", close(10 ** 0.3, 1.995, 1e-3))
check("-100 dBm = 0.1 pW", close(w_from_dbm(-100), 1e-13, 1e-9))
v_rms = np.sqrt(w_from_dbm(-100) * 50)
check("-100 dBm across 50 ohm = 2.24 uV rms", close(v_rms, 2.236e-6, 1e-3), f"({v_rms * 1e6:.3f} uV)")
v_33 = np.sqrt(2.0 * 50)
check("2 W across 50 ohm = 10 V rms", close(v_33, 10.0, 1e-9))
ratio_tx_rx = dbm(2.0) - (-120)
check("2 W TX vs -120 dBm RX = 153 dB = 2e15 power ratio", close(ratio_tx_rx, 153.0, 1e-3) and close(10 ** (ratio_tx_rx / 10), 2.0e15, 3e-3),
      f"({ratio_tx_rx:.1f} dB)")

# ---------------------------------------------------------------- 4. antenna lengths
print("\n§4 Antenna lengths")
half_433 = wl["LoRa 433.92 MHz"] / 2
check("433.92 MHz free-space lambda/2 = 345 mm", close(half_433, 0.34545, 1e-3), f"({half_433 * 1e3:.1f} mm)")
print(f"  practical thin-wire dipole ~0.95-0.97 x lambda/2 = {0.95 * half_433 * 1e3:.0f}-{0.97 * half_433 * 1e3:.0f} mm tip to tip")
q_433 = wl["LoRa 433.92 MHz"] / 4
check("433.92 MHz lambda/4 whip = 173 mm (before end-effect shortening)", close(q_433, 0.1727, 1e-3))
q_137 = C / 137.5e6 / 4
check("137.5 MHz lambda/4 = 545 mm; 9A4QV's 53.4 cm arms = 0.98 lambda/4", close(q_137, 0.5451, 1e-3) and 0.97 < 0.534 / q_137 < 0.99,
      f"({q_137 * 1e3:.0f} mm, ratio {0.534 / q_137:.3f})")
q_1090 = wl["ADS-B 1090 MHz"] / 4
check("1090 MHz lambda/4 ground-plane whip = 68.8 mm", close(q_1090, 0.06876, 1e-3), f"({q_1090 * 1e3:.1f} mm)")

# ---------------------------------------------------------------- 5. velocity factor from quarter-wave resonance
print("\n§5 Cable velocity factor (open stub, first S11 phase = -180 deg point)")
L = 2.000
for vf in (0.66, 0.695, 0.80, 0.85):
    f_q = vf * C / (4 * L)
    print(f"  L = {L} m, VF {vf}: quarter-wave resonance at {f_q / 1e6:.2f} MHz")
f_meas = 26.03e6
vf_back = 4 * L * f_meas / C
check("2.000 m cable resonant at 26.03 MHz -> VF 0.695 (PTFE, RG-316 class)", close(vf_back, 0.6946, 1e-3), f"(VF {vf_back:.4f})")
rl_open = 0.835
check("open-end return loss 0.835 dB -> one-way loss 0.42 dB", close(rl_open / 2, 0.4175, 1e-3))

# ---------------------------------------------------------------- 6. thermal noise floors
print("\n§6 kTB noise floor at 290 K")
kT0_dbm_hz = 10 * np.log10(KB * 290 / 1e-3)
check("kT0 = -173.98 dBm/Hz", close(kT0_dbm_hz, -173.98, 1e-4), f"({kT0_dbm_hz:.2f})")
for name, b in [("APRS/AIS 12.5 kHz", 12.5e3), ("LoRa 125 kHz", 125e3), ("Meteor LRPT 120 kHz", 120e3),
                ("FM broadcast 200 kHz", 200e3), ("ADS-B 2 MHz", 2e6), ("RTL-SDR full 2.4 MHz", 2.4e6)]:
    print(f"  {name:24s} kTB = {kT0_dbm_hz + 10 * np.log10(b):7.1f} dBm")
check("LoRa 125 kHz kTB = -123.0 dBm", close(kT0_dbm_hz + 10 * np.log10(125e3), -123.0, 1e-3))

# ---------------------------------------------------------------- 7. radio horizon (ADS-B)
print("\n§7 Radio horizon, 4/3 earth")
Re = 6371e3
k = 4 / 3


def horizon(h):
    return np.sqrt(2 * k * Re * h)


h_ac = 35000 * 0.3048
d = horizon(10.0) + horizon(h_ac)
check("ADS-B: 10 m antenna to 35 000 ft aircraft LOS = 439 km", close(d / 1e3, 439.0, 5e-3), f"({d / 1e3:.0f} km)")
d2 = horizon(2.0) + horizon(h_ac)
print(f"  same with a 2 m (window-sill) antenna: {d2 / 1e3:.0f} km")
check("rule of thumb d[km] = 4.12 (sqrt h1 + sqrt h2) [m]", close(4.12 * (np.sqrt(10) + np.sqrt(h_ac)), d / 1e3, 3e-3))

# ---------------------------------------------------------------- 8. HB100 Doppler
print("\n§8 Doppler, f_d = 2 v f0 / c")
f0 = 10.525e9
per_mps = 2 * 1.0 * f0 / C
per_kmh = 2 * (1 / 3.6) * f0 / C
per_mph = 2 * 0.44704 * f0 / C
check("HB100: 70.2 Hz per m/s", close(per_mps, 70.21, 1e-3), f"({per_mps:.2f})")
check("HB100: 19.5 Hz per km/h", close(per_kmh, 19.50, 2e-3), f"({per_kmh:.2f})")
check("HB100: 31.4 Hz per mph", close(per_mph, 31.39, 2e-3), f"({per_mph:.2f})")
print(f"  walking 1.4 m/s -> {1.4 * per_mps:.0f} Hz; car 50 km/h -> {50 * per_kmh:.0f} Hz; ball 30 m/s -> {30 * per_mps:.0f} Hz")
print(f"  sample rate for 120 km/h with margin (Nyquist x2.5): {2.5 * 120 * per_kmh:.0f} S/s")

# ---------------------------------------------------------------- 9. LEO satellite Doppler
print("\n§9 LEO Doppler for an overhead pass (circular orbit, non-rotating earth)")
MU = 3.986004418e14


def max_doppler(h, f, elev_min_deg=0.0):
    r = Re + h
    v = np.sqrt(MU / r)
    # overhead pass: satellite angle phi from zenith point; observer at (0, Re)
    phi = np.linspace(-0.5, 0.5, 200001)
    sx, sy = r * np.sin(phi), r * np.cos(phi)
    vx, vy = v * np.cos(phi), -v * np.sin(phi)
    dx, dy = sx, sy - Re
    rng = np.hypot(dx, dy)
    elev = np.degrees(np.arcsin(np.clip(dy / rng * 1.0, -1, 1)))  # observer's local vertical is +y
    rr = (dx * vx + dy * vy) / rng
    vis = elev >= elev_min_deg
    return np.max(np.abs(rr[vis])) * f / C, v


fd_met, v_met = max_doppler(830e3, 137.9e6)
fd_iss, v_iss = max_doppler(420e3, 145.8e6)
check("Meteor-M (830 km) at 137.9 MHz: max Doppler ~ +/-3.0 kHz at the horizon", 2.7e3 < fd_met < 3.3e3,
      f"(+/-{fd_met:.0f} Hz, v = {v_met:.0f} m/s)")
check("ISS (420 km) at 145.8 MHz: max Doppler ~ +/-3.5 kHz", 3.0e3 < fd_iss < 3.6e3, f"(+/-{fd_iss:.0f} Hz)")
fd_iss_437, _ = max_doppler(420e3, 437.8e6)
print(f"  ISS 437.80 MHz repeater downlink: +/-{fd_iss_437:.0f} Hz (tune during the pass)")

# ---------------------------------------------------------------- 10. "higher frequency loses more" (aperture effect)
print("\n§10 Free-space path loss at 1 km")


def fspl_db(f, dist):
    return 20 * np.log10(4 * np.pi * dist * f / C)


l433 = fspl_db(433.92e6, 1e3)
l2g4 = fspl_db(2.45e9, 1e3)
check("FSPL(1 km): 85.2 dB at 433.92 MHz, 100.2 dB at 2.45 GHz (isotropic antennas)",
      close(l433, 85.2, 2e-3) and close(l2g4, 100.2, 2e-3), f"({l433:.1f}, {l2g4:.1f} dB)")
# Same physical aperture A at both ends: G = 4 pi A / lambda^2 -> gain grows 20 log f per antenna, net link improves 20 log f
A = 0.05  # m^2 dish/patch-array area at both ends
g = lambda f: 10 * np.log10(4 * np.pi * A * f ** 2 / C ** 2)
link_433 = -l433 + 2 * max(g(433.92e6), 2.15)
link_2g4 = -l2g4 + 2 * g(2.45e9)
check("with equal 0.05 m^2 apertures the 2.45 GHz link is ~13 dB BETTER (aperture effect)", link_2g4 - link_433 > 10,
      f"({link_2g4 - link_433:+.1f} dB)")

# ---------------------------------------------------------------- 11. LoRa P2P range test prediction (two-ray)
print("\n§11 Ground-to-ground LoRa range test: two-ray prediction (ladder rung 7)")
lam433 = C / 433.92e6
h1 = h2 = 1.5
bp = 4 * h1 * h2 / lam433
check("two-ray breakpoint 4 h1 h2 / lambda for 1.5 m handheld heights at 433.92 MHz = 13 m", close(bp, 13.03, 5e-3),
      f"({bp:.1f} m; at 923 MHz {4 * h1 * h2 / (C / 923e6):.1f} m)")


def two_ray_loss(d, h1, h2):
    return 40 * np.log10(d) - 20 * np.log10(h1 * h2)


L1k = two_ray_loss(1000, h1, h2)
check("two-ray loss at 1 km, both ends 1.5 m: 113 dB (vs 85 dB free space)", close(L1k, 112.96, 1e-3), f"({L1k:.1f} dB)")
eirp = 10 + 2.15                       # dBm EIRP for 10 mW e.r.p. (SG 433 MHz exempt limit)
prx = eirp + 2.15 - L1k
sens = -129.5                          # SX1262 SF9/125 (15/lora-sensitivity-and-link-budget)
margin = prx - sens
fade = 10.0
d_max = 1000 * 10 ** ((margin - fade) / 40)
check("10 mW e.r.p., dipoles, SF9/125: -98.7 dBm at 1 km, 30.8 dB margin; ~3.3 km with 10 dB fade margin",
      close(prx, -98.66, 2e-3) and 3.0e3 < d_max < 3.6e3, f"(P_rx {prx:.1f} dBm, margin {margin:.1f} dB, d_max {d_max / 1e3:.2f} km)")
d_max_mast = 1000 * 10 ** ((margin - fade + 20 * np.log10(6.0 / 1.5)) / 40)
print(f"  raising one end to a 6 m mast: d_max ~ {d_max_mast / 1e3:.1f} km (+6 dB per doubling of one height)")

print(f"\n{sum(results)}/{len(results)} PASS")
print("ALL PASS" if all(results) else "SOME FAIL")
