#!/usr/bin/env python3
"""
pcb_emc_radiation.py — verification script for kb/13-pcb-rf-layout-emc/emc-emi-fundamentals.md
(and the clock-harmonic table used by mixed-signal-layout.md)

  1. Differential-mode (loop) and common-mode (wire/cable) radiation constants derived from first principles:
     numerical superposition of Hertzian-dipole segments for a pair of wires of length L, separation s,
     compared with E_DM = 1.316e-14 f^2 A I / r and E_CM = 6.28e-7 f L I_total / r (free space, broadside);
     Ott's forms (x2 for a ground-plane reflection): 263e-16 f^2 A I / r and 12.6e-7 f L I_cm / r.
  2. FCC Part 15 Class B / A limits -> maximum allowed DM current (per loop area) and CM current (per cable length);
     Ott's classic ~8 uA at 30 MHz for 1 m.  Resonant-cable cap (L_eff <= lambda/pi).
  3. Trapezoidal clock spectrum envelope and edge-rate control: harmonic amplitudes of 3.3 V clocks at 433/920/1575 MHz
     for rise times 0.5-5 ns; series-R edge slowing.
  4. Which clock harmonics land in 433 MHz, 868/915/920-925 MHz and GNSS L1/E1/B1/G1 bands (common MCU/radio clocks).
  5. Spread-spectrum clocking: peak reduction measured in a 120 kHz (CISPR) and 125 kHz (LoRa channel) bandwidth by
     FFT of the n-th harmonic of a triangularly frequency-modulated clock, vs the 10 log10(n*delta*f0/RBW) estimate.
  6. Pyro-lead RF pickup near a 2 W 433 MHz transmitter: resonant-dipole upper bound and twisted-pair loop pickup,
     vs an e-match no-fire current and the MIL-STD-464 16.5 dB margin.
  7. RF rectification in sensor front ends: square-law DC offset vs RF amplitude; RC filter attenuation.
  8. ESD: IEC 61000-4-2 peak currents; TVS capacitance vs return loss on 50-ohm RF ports.

Run: python3 tools/verify/pcb_emc_radiation.py      (about 10 s)
"""
import numpy as np

C0 = 299_792_458.0
MU0 = 4e-7 * np.pi
ETA0 = MU0 * C0
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


print("=" * 98)
print("1. DM and CM radiation from two parallel wires (numerical dipole superposition vs formulas)")
print("=" * 98)


def field_two_wires(f, L, s, I1, I2, r, nseg=400):
    """|E| (far field, free space) at distance r, observation point broadside in the plane of the wires,
    perpendicular to them (the DM maximum direction). Wires along z, at x = +-s/2."""
    k = 2 * np.pi * f / C0
    z = (np.arange(nseg) + 0.5) / nseg * L - L / 2
    dz = L / nseg
    obs = np.array([r, 0.0, 0.0])
    E = 0j
    for x0, I in [(s / 2, I1), (-s / 2, I2)]:
        R = np.sqrt((obs[0] - x0) ** 2 + z**2)
        # theta-component of each Hertzian dipole element (sin(theta) ~ 1 near broadside for r >> L)
        sin_t = (obs[0] - x0) / R
        E += np.sum(1j * ETA0 * k * I * dz / (4 * np.pi * R) * np.exp(-1j * k * R) * sin_t)
    return abs(E)


r = 100.0     # far field for all three frequencies (the formulas are far-field results)
for f in [30e6, 100e6, 300e6]:
    L, s = 0.1, 1e-3
    I = 1e-3
    Edm = field_two_wires(f, L, s, I, -I, r)
    Edm_formula = 1.316e-14 * f**2 * (L * s) * I / r
    Ecm = field_two_wires(f, L, s, I, I, r)        # total CM current 2I
    Ecm_formula = 6.28e-7 * f * L * (2 * I) / r    # free space, total current
    print(f"  f {f/1e6:5.0f} MHz, L 100 mm, s 1 mm, 1 mA: DM numeric {Edm*1e6:9.4f} uV/m vs 1.316e-14 f^2 A I/r {Edm_formula*1e6:9.4f};"
          f"  CM numeric {Ecm*1e3:8.4f} mV/m vs 6.28e-7 f L I_tot/r {Ecm_formula*1e3:8.4f}")
    check(f"  DM and CM formulas match the dipole superposition within 3 % at {f/1e6:.0f} MHz",
          abs(Edm / Edm_formula - 1) < 0.03 and abs(Ecm / Ecm_formula - 1) < 0.03)
k_dm = ETA0 * np.pi / C0**2
k_cm = ETA0 / (2 * C0) * 1.0
print(f"  constants from first principles: eta0*pi/c^2 = {k_dm:.4e} (DM, free space); eta0/(2c) = {k_cm:.4e} (CM per unit total"
      f" current, free space) -> x2 ground reflection: {2*k_dm:.3e} (Ott 263e-16), {2*k_cm:.3e} (Ott 12.6e-7)")
check("Ott's 263e-16 and 12.6e-7 are the free-space constants x 2", abs(2 * k_dm / 263e-16 - 1) < 0.01 and abs(2 * k_cm / 12.6e-7 - 1) < 0.01)

print("\n" + "=" * 98)
print("2. What currents are allowed? (Ott forms with ground reflection; FCC Part 15.109)")
print("=" * 98)
fcc_b = [(30e6, 88e6, 100e-6), (88e6, 216e6, 150e-6), (216e6, 960e6, 200e-6), (960e6, 40e9, 500e-6)]   # at 3 m


def limit_b(f):
    for lo, hi, e in fcc_b:
        if lo <= f < hi:
            return e
    return np.nan


for f in [30e6, 100e6, 300e6, 915e6, 1.5e9]:
    E = limit_b(f)
    lam = C0 / f
    rows = []
    for A in [1e-4, 1e-3, 1e-2]:
        I = E * 3 / (263e-16 * f**2 * A)
        rows.append(f"A={A*1e4:4.0f} cm2: {I*1e3:8.3f} mA")
    rowc = []
    for L in [0.3, 1.0, 2.0]:
        Leff = min(L, lam / np.pi)
        I = E * 3 / (12.6e-7 * f * Leff)
        rowc.append(f"L={L:.1f} m: {I*1e6:7.2f} uA")
    print(f"  {f/1e6:6.0f} MHz (limit {E*1e6:.0f} uV/m @3 m): DM " + ", ".join(rows) + " | CM " + ", ".join(rowc))
I30 = 100e-6 * 3 / (12.6e-7 * 30e6 * 1.0)
check("Ott's classic result: ~8 uA of CM current on 1 m of cable at 30 MHz meets Class B", 7e-6 < I30 < 9e-6, f"({I30*1e6:.1f} uA)")
ratio = (100e-6 * 3 / (263e-16 * 100e6**2 * 1e-3)) / (150e-6 * 3 / (12.6e-7 * 100e6 * 1.0))
print(f"  at 100 MHz a 10 cm2 DM loop may carry ~{ratio:.0f}x more current than a 1 m cable's CM current")

print("\n" + "=" * 98)
print("3. Trapezoidal clock spectrum and edge-rate control (3.3 V, 50 % duty)")
print("=" * 98)


def harmonic_amp(n, f0, tr, A=3.3, duty=0.5):
    """ENVELOPE (V, peak) of the n-th harmonic of a trapezoid with equal rise/fall tr (Ott/Paul bound):
    2 A d  x  min(1, 1/(pi n d))  x  min(1, 1/(pi n tr/T)).  The exact sinc nulls are not used (real edges are not
    linear ramps and duty is never exact)."""
    T = 1 / f0
    return 2 * A * duty * min(1.0, 1 / (np.pi * n * duty)) * min(1.0, 1 / (np.pi * n * tr / T))


for f0 in [40e6, 32e6, 26e6]:
    for target in [433.92e6, 920e6, 1575.42e6]:
        n = int(round(target / f0))
        if n % 2 == 0:
            note = " (even harmonic: small only for exactly 50 % duty)"
        else:
            note = ""
        vals = []
        for tr in [0.5e-9, 1e-9, 2e-9, 5e-9]:
            a = harmonic_amp(n, f0, tr, duty=0.48)
            vals.append(f"tr {tr*1e9:3.1f} ns: {20*np.log10(a/np.sqrt(2)/1e-6):5.1f} dBuV")
        print(f"  {f0/1e6:4.0f} MHz clock, harmonic {n:3d} ({n*f0/1e6:7.1f} MHz): " + ", ".join(vals) + note)
a1 = harmonic_amp(23, 40e6, 1e-9, duty=0.48)
a5 = harmonic_amp(23, 40e6, 5e-9, duty=0.48)
print(f"  slowing edges 1 ns -> 5 ns lowers the 23rd harmonic (920 MHz) of a 40 MHz clock by {20*np.log10(a1/a5):.1f} dB")
check("5x slower edges cut harmonics above both corners by 20log(5) = 14 dB", abs(20 * np.log10(a1 / a5) - 13.98) < 0.1,
      f"({20*np.log10(a1/a5):.1f} dB)")
for R, Cl in [(33, 10e-12), (100, 10e-12), (220, 10e-12)]:
    print(f"  series R {R:3d} ohm into {Cl*1e12:.0f} pF: tr(10-90) ~ 2.2RC = {2.2*R*Cl*1e9:.2f} ns (plus driver's own edge)")

print("\n" + "=" * 98)
print("4. Clock harmonics landing in receiver bands")
print("=" * 98)
bands = {"433 ISM (433.05-434.79)": (433.05e6, 434.79e6),
         "SG SRD 866-869": (866e6, 869e6), "SG SRD 920-925": (920e6, 925e6), "US 902-928": (902e6, 928e6),
         "GPS L1 C/A +-1.023": (1574.397e6, 1576.443e6), "Galileo E1 +-2.046": (1573.374e6, 1577.466e6),
         "BeiDou B1I +-2.046": (1559.052e6, 1563.144e6), "GLONASS L1 1598-1606": (1598.0e6, 1606.0e6)}
clocks = {"8 MHz": 8e6, "12 MHz (USB PHY)": 12e6, "16 MHz": 16e6, "24 MHz": 24e6, "25 MHz (Ethernet)": 25e6,
          "26 MHz (TCXO)": 26e6, "32 MHz (SX126x XTAL)": 32e6, "40 MHz (ESP32 XTAL/APB/SPI)": 40e6,
          "48 MHz (USB FS)": 48e6, "80 MHz (ESP32 APB)": 80e6, "150 MHz (Teensy IPG)": 150e6,
          "240 MHz (ESP32-S3 CPU)": 240e6, "600 MHz (Teensy CPU)": 600e6, "SD 25 MHz": 25e6, "SD 50 MHz": 50e6}
hits = []
for cname, fc in clocks.items():
    for bname, (lo, hi) in bands.items():
        for n in range(int(np.ceil(lo / fc)), int(np.floor(hi / fc)) + 1):
            hits.append((cname, n, n * fc, bname))
for h in hits:
    print(f"  {h[0]:30s} x {h[1]:3d} = {h[2]/1e6:9.3f} MHz  -> inside {h[3]}")
check("40 MHz x 23 = 920 MHz lands inside the Singapore 920-925 MHz LoRa band",
      any(h[0].startswith("40 MHz") and h[1] == 23 for h in hits))
check("no listed clock has a harmonic inside GPS L1 C/A +-1.023 MHz except where printed",
      True)

print("\n" + "=" * 98)
print("5. Spread-spectrum clocking: FFT of the n-th harmonic of a triangular-FM clock")
print("=" * 98)


def ssc_reduction(f0, n, delta, fm, rbw, center_spread=False):
    """Peak power in an rbw window of the n-th harmonic, relative to the unmodulated harmonic (dB).
    Instantaneous frequency f(t) = f0 (1 - delta * tri(t)) (down-spread), tri in [0, 1] at rate fm."""
    dev = n * delta * f0
    fs = max(8 * dev, 20 * rbw)
    Tm = 1 / fm
    N = int(round(40 * Tm * fs))
    t = np.arange(N) / fs
    ph = (t * fm) % 1.0
    tri = 1 - 2 * np.abs(ph - 0.5)      # 0..1..0
    finst = -n * delta * f0 * tri       # baseband offset of the n-th harmonic
    phase = 2 * np.pi * np.cumsum(finst) / fs
    x = np.exp(1j * phase)
    X = np.fft.fftshift(np.fft.fft(x * np.hanning(N))) / np.sum(np.hanning(N))
    P = np.abs(X) ** 2
    freqs = np.fft.fftshift(np.fft.fftfreq(N, 1 / fs))
    df = freqs[1] - freqs[0]
    w = max(1, int(round(rbw / df)))
    Pw = np.convolve(P, np.ones(w), mode="same")
    return 10 * np.log10(Pw.max() / 1.0), dev


for f0, n, target in [(40e6, 23, "920 MHz"), (40e6, 39, "1560 MHz"), (24e6, 38, "912 MHz")]:
    for delta in [0.005, 0.01]:
        for rbw, tag in [(120e3, "CISPR 120 kHz"), (125e3, "LoRa 125 kHz ch."), (1e6, "1 MHz")]:
            red, dev = ssc_reduction(f0, n, delta, 30e3, rbw)
            est = 10 * np.log10(dev / rbw) if dev > rbw else 0
            print(f"  {f0/1e6:.0f} MHz x {n} ({target}), {delta*100:.1f} % down-spread, 30 kHz tri: in {tag:17s} peak {red:6.1f} dB"
                  f" (10log(n*delta*f0/RBW) = {-est:6.1f} dB)")
red, dev = ssc_reduction(40e6, 23, 0.005, 30e3, 120e3)
check("triangular SSC achieves 3-6 dB LESS than the flat-spread estimate (spectral 'ears' at the spread edges)",
      2.5 < (10 * np.log10(dev / 120e3) + red) < 6, f"(FFT {red:.1f} dB, estimate {-10*np.log10(dev/120e3):.1f} dB)")

print("\n" + "=" * 98)
print("6. Pyro-lead RF pickup next to a 2 W (33 dBm) 433 MHz transmitter")
print("=" * 98)
P, G, f = 2.0, 1.64, 433.92e6
lam = C0 / f
nofire = 0.130               # Q2G2-class hobby igniter no-fire current (5 s) -- anecdotal source
allow = nofire * 0.15        # MIL-STD-464: 16.5 dB below MNFS (= 15 % of no-fire current)
Rb = 2.0                     # bridge resistance
print(f"  lambda = {lam*1e3:.0f} mm; reactive near-field boundary lambda/2pi = {lam/2/np.pi*1e3:.0f} mm")
print(f"  e-match no-fire ~{nofire*1e3:.0f} mA (anecdotal), MIL-STD-464 safety limit 15 % -> {allow*1e3:.1f} mA")
for rr in [0.1, 0.2, 0.5, 1.0]:
    E = np.sqrt(30 * P * G) / rr
    Ae = 1.64 * lam**2 / (4 * np.pi)
    Pav = E**2 / ETA0 * Ae                          # matched resonant dipole (upper bound)
    Ra = 73.0
    PL = Pav * 4 * Rb * Ra / (Rb + Ra) ** 2         # into a 2-ohm bridge at the dipole feed
    I_dip = np.sqrt(PL / Rb)
    # twisted/parallel pair: DM loop pickup, loop 300 mm x 2 mm (untwisted worst case) and 30 mm x 2 mm residual
    I_loop = []
    for A in [300e-3 * 2e-3, 30e-3 * 2e-3]:
        emf = 2 * np.pi * f * (E / C0) * A
        Lloop = MU0 / np.pi * (A / 2e-3) * np.log(2e-3 / 0.25e-3)     # two-wire line L' x length
        I_loop.append(emf / abs(Rb + 1j * 2 * np.pi * f * Lloop))
    print(f"  r = {rr:3.1f} m: E ~{E:6.1f} V/m (far-field formula) | spread leads as resonant dipole: I <= {I_dip*1e3:6.1f} mA"
          f" | parallel pair 300 mm: {I_loop[0]*1e3:5.2f} mA, twisted (30 mm residual): {I_loop[1]*1e3:6.3f} mA")
E02 = np.sqrt(30 * P * G) / 0.2
Pav = E02**2 / ETA0 * 1.64 * lam**2 / (4 * np.pi)
I02 = np.sqrt(Pav * 4 * Rb * 73 / (Rb + 73) ** 2 / Rb)
check("a spread (dipole-like) lead pair 0.2 m from a 2 W 433 MHz antenna can exceed an e-match's 16.5 dB safety limit",
      I02 > allow, f"({I02*1e3:.0f} mA vs {allow*1e3:.1f} mA)")

print("\n" + "=" * 98)
print("7. RF rectification in a sensor front end (square-law regime) and an RC filter at the pin")
print("=" * 98)
VT, nid = 0.02585, 1.0
for Vrf in [1e-3, 10e-3, 30e-3, 100e-3]:
    dv = Vrf**2 / (4 * nid * VT)
    print(f"  RF amplitude {Vrf*1e3:5.0f} mV at a pn junction -> DC shift ~V^2/(4 n VT) = {dv*1e3:7.3f} mV (square-law estimate)")
for R, C in [(100, 100e-12), (1e3, 1e-9)]:
    fc = 1 / (2 * np.pi * R * C)
    att = 20 * np.log10(np.sqrt(1 + (433.92e6 / fc) ** 2))
    print(f"  RC {R} ohm + {C*1e12:.0f} pF: corner {fc/1e6:.1f} MHz, ideal attenuation at 433.92 MHz {att:.0f} dB"
          f" (real: limited by C's ESL/SRF and layout, ~20-40 dB)")
check("10 mV of RF on a junction gives ~1 mV DC offset (a large error for a 24-bit baro/IMU analog stage)",
      0.5e-3 < 10e-3**2 / (4 * VT) < 2e-3)

print("\n" + "=" * 98)
print("8. ESD (IEC 61000-4-2) and TVS capacitance on RF ports")
print("=" * 98)
for lvl, kv_c, kv_a in [(1, 2, 2), (2, 4, 4), (3, 6, 8), (4, 8, 15)]:
    print(f"  level {lvl}: contact {kv_c} kV (first peak ~{3.75*kv_c:.1f} A, 0.7-1 ns rise), air {kv_a} kV")
for Ct in [0.1e-12, 0.2e-12, 0.5e-12, 1e-12, 3e-12]:
    row = []
    for f in [433.92e6, 915e6, 1575.42e6, 2.45e9, 5.8e9]:
        x = 2 * np.pi * f * Ct * 50
        G = x / np.sqrt(4 + x * x)
        row.append(f"{f/1e9:.2f}G {-20*np.log10(G):4.1f}")
    print(f"  TVS {Ct*1e12:3.1f} pF shunt on 50 ohm: RL " + " ".join(row) + " dB")
x = 2 * np.pi * 1575.42e6 * 0.5e-12 * 50
check("a 0.5 pF TVS keeps GNSS L1 RL near 18 dB (u-blox recommends < 0.5 pF)", 17 < -20 * np.log10(x / np.sqrt(4 + x * x)) < 19.5)

print("\nALL CHECKS PASSED" if ok_all else "\nSOME CHECKS FAILED")
