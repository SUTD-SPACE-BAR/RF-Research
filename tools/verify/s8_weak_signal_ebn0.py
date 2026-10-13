#!/usr/bin/env python3
"""s8_weak_signal_ebn0.py — checks for kb/10-comms-modulation/weak-signal-digital-modes.md (W5-S8).

1. Mode table: SNR in 2500 Hz -> C/N0 -> Eb/N0 (total energy incl. sync) and Es/N0 per channel symbol,
   from the WSJT-X 2.5 User Guide Table 7 and the FT4/FT8 QEX paper (Franke, Somerville, Taylor 2020).
2. Why FT8 decodes at -21 dB: the same number in its own 50 Hz and in a 6.25 Hz symbol bandwidth.
3. Constrained capacity of non-coherent orthogonal M-FSK (Monte Carlo of the mutual information with the
   ideal I0 envelope likelihood) -> the lowest Eb/N0 any code could reach at each mode's rate.
   Dispersion -> normal-approximation penalty for FT8's 58-symbol block at 50 % and 90 % decode probability.
4. Shannon (unconstrained) bound at each mode's spectral efficiency, and the finite-k energy-limited bound.
5. LoRa SF12 vs FT8 for the same 77-80-bit message: preamble + header overhead, Eb/N0 including all
   transmitted energy, and the SNR in 2500 Hz LoRa would need at FT8's bit rate.

Run: python3 tools/verify/s8_weak_signal_ebn0.py   (~20 s)
"""
import numpy as np
from scipy import special, optimize, stats

rng = np.random.default_rng(8)
RES = []


def check(name, ok, detail=""):
    RES.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")


db = lambda x: 10 * np.log10(x)
B_REF = 2500.0

# ---------------------------------------------------------------- 1. mode table
# name: (info bits, Tx duration s, symbol time s, total symbols, data symbols, M, threshold dB in 2500 Hz, bandwidth Hz)
modes = {
    "FT8":       (77, 79 * 0.160, 0.160, 79, 58, 8, -20.8, 50.0),     # QEX Table 5/6 (BP+OSD, no AP, AWGN)
    "FT4":       (77, 105 * 0.048, 0.048, 105, 87, 4, -17.5, 83.3),   # QEX Table 6
    "JT65A":     (72, 46.8, 0.3715, 126, 63, 64, -25.0, 177.6),       # Guide Table 7
    "JT9A":      (72, 49.0, 0.576, 85, 69, 8, -26.0, 15.6),
    "JT4A":      (72, 47.1, 1 / 4.375, 206, 206, 2, -23.0, 17.5),
    "Q65-15A":   (77, 12.8, 0.15, 85, 63, 64, -22.0, 433.0),
    "Q65-60A":   (77, 51.0, 0.6, 85, 63, 64, -27.0, 108.0),
    "Q65-300A":  (77, 293.8, 1 / 0.289, 85, 63, 64, -33.0, 19.0),
    "FST4-60":   (77, 51.8, 1 / 3.09, 160, 120, 4, -28.0, 12.4),
    "WSPR":      (50, 110.6, 1 / 1.4648, 162, 162, 2, -31.0, 5.9),   # data bit picks 1 of 2 tones (sync known)
    "FST4W-120": (50, 109.3, 1 / 1.46, 160, 120, 4, -32.0, 5.9),
}
print("1. Mode table (Eb/N0 counts ALL transmitted energy, sync included)")
print(f"{'mode':10s} {'Rb b/s':>8s} {'SNR2500':>8s} {'C/N0':>7s} {'Eb/N0':>6s} {'Es/N0':>6s} {'eta b/s/Hz':>10s}")
EB = {}
for m, (k, T, Ts, ns, nd, M, snr, bw) in modes.items():
    Rb = k / T
    cn0 = snr + db(B_REF)
    ebn0 = cn0 - db(Rb)
    esn0 = cn0 + db(Ts)
    EB[m] = ebn0
    print(f"{m:10s} {Rb:8.3f} {snr:8.1f} {cn0:7.2f} {ebn0:6.2f} {esn0:6.2f} {Rb / bw:10.4f}")
check("FT8 Rb = 77/12.64 s = 6.09 b/s", abs(77 / 12.64 - 6.09) < 0.01, f"{77 / 12.64:.3f}")
check("FT8 Eb/N0 at -20.8 dB ~ 5.3 dB", abs(EB["FT8"] - 5.33) < 0.05, f"{EB['FT8']:.2f}")
check("FT4 Eb/N0 at -17.5 dB ~ 4.6 dB", abs(EB["FT4"] - 4.64) < 0.05, f"{EB['FT4']:.2f}")
check("WSPR Eb/N0 at -31 dB ~ 6.4 dB (3.4 dB if half the energy is called sync)", abs(EB["WSPR"] - 6.43) < 0.05,
      f"{EB['WSPR']:.2f}")
check("JT65A Eb/N0 at -25 dB ~ 7.1 dB", abs(EB["JT65A"] - 7.11) < 0.05, f"{EB['JT65A']:.2f}")
new = [EB[m] for m in ("FT8", "FT4", "Q65-15A", "Q65-60A", "FST4-60", "FST4W-120")]
old = [EB[m] for m in ("JT65A", "JT9A", "JT4A", "WSPR")]
check("LDPC/QRA modes (FT8, FT4, Q65, FST4/W) cluster at 4.2-5.4 dB Eb/N0", 4.1 < min(new) and max(new) < 5.5,
      f"{min(new):.2f}..{max(new):.2f} dB")
check("older RS/convolutional modes (JT65, JT9, JT4, WSPR) need 6.3-9.1 dB", min(old) > 6.2 and max(old) < 9.2,
      f"{min(old):.2f}..{max(old):.2f} dB")
# PA3FWM table for non-WSJT modes (no FEC): RTTY -5 dB at 32 b/s; PSK31 -10 dB at 31 b/s
for nm, s, rb, ref in [("RTTY", -5, 32, 14), ("PSK31", -10, 31, 9)]:
    e = s + db(B_REF) - db(rb)
    check(f"{nm}: SNR {s} dB @ {rb} b/s -> Eb/N0 ~ {ref} dB (PA3FWM)", abs(e - ref) < 0.6, f"{e:.1f}")

# ---------------------------------------------------------------- 2. why -21 dB
print("\n2. FT8 at -21 dB in 2500 Hz")
snr = -21.0
in50 = snr + db(2500 / 50)
in_sym = snr + db(2500 / 6.25)
check("-21 dB in 2500 Hz = -4.0 dB in the 50 Hz occupied band", abs(in50 - (-4.0)) < 0.05, f"{in50:.2f}")
check("= +5.0 dB Es/N0 in each 6.25 Hz symbol (26.0 dB 'processing gain')", abs(in_sym - 5.02) < 0.05, f"{in_sym:.2f}")


# ---------------------------------------------------------------- 3. NC M-FSK capacity
def ncfsk_info_density(M, esn0, n=200_000):
    """Samples of the information density (bits) of non-coherent orthogonal M-FSK with ideal soft
    (I0) metrics; complex noise variance N0 = 1 per branch, signal amplitude sqrt(Es)."""
    a = np.sqrt(esn0)
    r = (rng.standard_normal((n, M)) + 1j * rng.standard_normal((n, M))) / np.sqrt(2)
    r[:, 0] += a * np.exp(1j * rng.uniform(0, 2 * np.pi, n))
    x = 2 * a * np.abs(r)                       # argument of I0(2 sqrt(Es)|r|/N0)
    logi0 = np.log(special.i0e(x)) + x          # log I0
    lse = special.logsumexp(logi0, axis=1)
    return (np.log(M) - (lse - logi0[:, 0])) / np.log(2)


def cfsk_info_density(M, esn0, n=200_000):
    """Same for COHERENT orthogonal M-FSK (phase known): metric exp(2 sqrt(Es) Re r_j / N0)."""
    a = np.sqrt(esn0)
    r = (rng.standard_normal((n, M)) + 1j * rng.standard_normal((n, M))) / np.sqrt(2)
    r[:, 0] += a
    x = 2 * a * r.real
    return (np.log(M) - (special.logsumexp(x, axis=1) - x[:, 0])) / np.log(2)


def es_for_rate(M, rate, lo=-10, hi=20, fn=None, n=60_000):
    fn = fn or ncfsk_info_density
    f = lambda e_db: fn(M, 10 ** (e_db / 10), n).mean() - rate
    return optimize.brentq(f, lo, hi, xtol=0.02)


print("\n3. Non-coherent M-FSK constrained-capacity limits")
check("NC-BFSK MI tends to 1 bit at high SNR", abs(ncfsk_info_density(2, 100).mean() - 1) < 0.01)
lim, limc = {}, {}
for m, M, k, nd, ns in [("FT8", 8, 77, 58, 79), ("FT4", 4, 77, 87, 105), ("JT65A", 64, 72, 63, 126),
                        ("WSPR", 2, 50, 162, 162), ("Q65-60A", 64, 77, 63, 85)]:
    rate = k / nd                                  # info bits per data symbol
    es = es_for_rate(M, rate)
    eb_lim = es + db(ns / k)                       # all symbols' energy over the info bits
    lim[m] = eb_lim
    ebc = es_for_rate(M, rate, fn=cfsk_info_density) + db(ns / k)
    limc[m] = ebc
    print(f"   {m:8s} M={M:2d} rate {rate:.3f} b/sym: NC Es/N0 >= {es:5.2f} dB -> Eb/N0 >= {eb_lim:5.2f} dB; "
          f"coherent Eb/N0 >= {ebc:5.2f} dB (achieved {EB[m]:5.2f})")
check("FT8 limit (single-symbol NC 8-FSK, sync counted) ~ 3.6-4.2 dB", 3.4 < lim["FT8"] < 4.4, f"{lim['FT8']:.2f}")
check("FT8 sits within ~2 dB of its own constrained limit", EB["FT8"] - lim["FT8"] < 2.0,
      f"gap {EB['FT8'] - lim['FT8']:.2f} dB")
check("FT4 and WSPR beat the single-symbol NC limit (multi-symbol block detection uses phase continuity) "
      "but stay above the coherent limit", EB["FT4"] < lim["FT4"] and EB["WSPR"] < lim["WSPR"]
      and EB["FT4"] > limc["FT4"] and EB["WSPR"] > limc["WSPR"])
ft4_n1 = -15.3 + db(B_REF) - db(77 / 5.04)
check("FT4 with single-symbol detection + BP only (-15.3 dB, QEX Table 5) is above the NC limit", ft4_n1 > lim["FT4"],
      f"{ft4_n1:.2f} vs {lim['FT4']:.2f} dB")
# finite length: normal approximation n C - sqrt(n V) Qinv(eps) = k
es_ft8 = 10 ** ((EB["FT8"] - db(79 / 77)) / 10)
i = ncfsk_info_density(8, es_ft8, 400_000)
C, V = i.mean(), i.var()
print(f"   FT8 at threshold: C = {C:.3f} b/sym (needs 77/58 = {77 / 58:.3f}), V = {V:.3f}")
for eps in (0.5, 0.1):
    def g(e_db):
        ii = ncfsk_info_density(8, 10 ** (e_db / 10), 100_000)
        return 58 * ii.mean() - np.sqrt(58 * ii.var()) * stats.norm.isf(eps) - 77
    e_req = optimize.brentq(g, 0, 12, xtol=0.02)
    print(f"   normal approx., decode prob {1 - eps:.0%}: Es/N0 >= {e_req:.2f} dB -> Eb/N0 >= {e_req + db(79 / 77):.2f} dB")
    if eps == 0.5:
        check("at 50 % decode probability the finite-length penalty vanishes (Q^-1(0.5)=0)",
              abs(e_req + db(79 / 77) - lim["FT8"]) < 0.25)
    else:
        e90 = e_req + db(79 / 77)
        check("90 % decode needs ~0.5-1.5 dB more than 50 % (58-symbol block)", 0.4 < e90 - lim["FT8"] < 1.6,
              f"+{e90 - lim['FT8']:.2f} dB")

# ---------------------------------------------------------------- 4. Shannon bounds
print("\n4. Unconstrained bounds")
for m in ("FT8", "WSPR", "JT65A"):
    k, T, Ts, ns, nd, M, snr, bw = modes[m]
    eta = k / T / bw
    eb = db((2 ** eta - 1) / eta)
    print(f"   {m:6s} eta = {eta:.4f} b/s/Hz -> Shannon Eb/N0 >= {eb:.2f} dB (achieved {EB[m]:.2f})")
    if m == "FT8":
        check("FT8 Shannon bound at eta=0.12 is ~ -1.4 dB", abs(eb + 1.42) < 0.05, f"{eb:.2f}")


def kbits_energy(k, eps):
    """Energy-limited finite-k bound (bandwidth unlimited), normal approx.: k ln2 = E/N0 - sqrt(2E/N0) Qinv(eps)."""
    q = stats.norm.isf(eps)
    s = (q * np.sqrt(2) + np.sqrt(2 * q * q + 4 * k * np.log(2))) / 2
    return db(s * s / k)


e50, e90 = kbits_energy(77, 0.5), kbits_energy(77, 0.1)
check("77 bits, unlimited bandwidth: 50 % -> -1.59 dB; 90 % -> ~ -0.5 dB", abs(e50 + 1.59) < 0.01 and abs(e90 + 0.51) < 0.1,
      f"{e50:.2f}, {e90:.2f} dB")

# ---------------------------------------------------------------- 5. LoRa SF12 vs FT8
print("\n5. LoRa SF12/125 kHz (CR 4/5, LDRO, explicit header, CRC) carrying a 10-byte message")


def lora_nsym(PL, SF, CR=1, H=0, DE=1, CRC=1):
    return 8 + max(int(np.ceil((8 * PL - 4 * SF + 28 + 16 * CRC - 20 * H) / (4 * (SF - 2 * DE)))) * (CR + 4), 0)


SF, PL = 12, 10
npay = lora_nsym(PL, SF)
npre = 8 + 4.25
check("10-byte payload at SF12 LDRO = 18 payload symbols", npay == 18, f"{npay}")


def nc_ser(M, esn0):
    """Exact SER of NC orthogonal M-FSK by numerical integration over the Rician envelope."""
    r = np.linspace(0, np.sqrt(esn0) + 12, 20000)
    a = np.sqrt(esn0)
    pr = 2 * r * np.exp(-(r - a) ** 2) * special.i0e(2 * r * a)
    return 1 - np.trapezoid(pr * (1 - np.exp(-r * r)) ** (M - 1), r)


M = 2 ** SF
for per in (0.5, 0.1, 0.01):
    ser = 1 - (1 - per) ** (1 / npay)
    es = optimize.brentq(lambda e: nc_ser(M, 10 ** (e / 10)) - ser, 0, 30)
    eb_all = es + db((npay + npre) / (8 * PL))
    print(f"   PER {per:5.0%}: SER {ser:.4f} -> Es/N0 {es:5.2f} dB -> Eb/N0 (all energy, 80 info bits) {eb_all:5.2f} dB")
    if per == 0.5:
        lora50 = eb_all
check("ideal LoRa needs ~2.5-4 dB more Eb/N0 than FT8 for a short (80-bit) message at 50 %", 2.5 < lora50 - EB["FT8"] < 4.0,
      f"{lora50 - EB['FT8']:.2f} dB")
# datasheet criterion check against canonical page: -20 dB SNR in 125 kHz at SF12
rb12 = SF * 125e3 / 2 ** SF * 4 / 5
eb_ds = -20 + db(125e3) - db(rb12)
check("canonical LoRa SF12 -20 dB in 125 kHz -> Eb/N0 6.3 dB (293 b/s, no LDRO)", abs(eb_ds - 6.3) < 0.05, f"{eb_ds:.2f}")
snr2500_lora = -20 + db(125e3 / 2500)
check("LoRa SF12/125 kHz threshold expressed in 2500 Hz = -3.0 dB", abs(snr2500_lora + 3.0) < 0.05, f"{snr2500_lora:.2f}")
need = lora50 + db(77 / 12.64 / 2500)
print(f"   LoRa-style signalling at FT8's 6.09 b/s would need SNR2500 = {need:.1f} dB (FT8: -20.8 dB)")
rb78 = SF * 7812.5 / 2 ** SF * 4 / 5 * 10 / 12      # BW 7.8 kHz with LDRO (10 bits/symbol)
check("SX127x SF12/7.8 kHz with LDRO: 15.3 b/s; -20 dB in 7.8 kHz = -15.0 dB in 2500 Hz",
      abs(rb78 - 15.26) < 0.05 and abs(-20 + db(7812.5 / 2500) + 15.05) < 0.05, f"{rb78:.2f} b/s")

es_l = es_for_rate(4096, 8.0, lo=0, hi=25, n=6000)          # LDRO + CR 4/5: 8 info bits per 4096-ary symbol
print(f"   NC 4096-FSK capacity at 8 b/sym: Es/N0 >= {es_l:.2f} dB -> Eb/N0 >= {es_l - db(8):.2f} dB per payload bit")
check("LoRa SF12's own NC-4096-FSK limit at 8 b/sym is ~0 dB Eb/N0, so the datasheet 6.3 dB leaves ~6 dB unused",
      -0.6 < es_l - db(8) < 0.6 and 5.5 < eb_ds - (es_l - db(8)) < 7.0, f"{es_l - db(8):.2f} dB")

# ---------------------------------------------------------------- 6. worked-example numbers
print("\n6. Worked examples")
NF = 6.0
s_ft8 = -174 + NF + (-20.8 + db(B_REF))
s_lora = -174 + NF + db(125e3) - 20
check("FT8-style sensitivity with NF 6 dB = -154.8 dBm", abs(s_ft8 + 154.8) < 0.05, f"{s_ft8:.1f} dBm")
check("LoRa SF12/125 kHz sensitivity with NF 6 dB = -137.0 dBm", abs(s_lora + 137.0) < 0.05, f"{s_lora:.1f} dBm")
check("difference 17.8 dB = 16.8 dB of bit-rate ratio (293 vs 6.09 b/s) + ~1 dB Eb/N0",
      abs((s_lora - s_ft8) - (db(rb12 / (77 / 12.64)) + (eb_ds - EB['FT8']))) < 0.05,
      f"{s_lora - s_ft8:.2f} = {db(rb12 / (77 / 12.64)):.2f} + {eb_ds - EB['FT8']:.2f}")
ppm = 6.25 / 433e6 * 1e6
check("one FT8 tone spacing at 433 MHz = 0.0144 ppm", abs(ppm - 0.0144) < 0.0002, f"{ppm:.4f} ppm")
fdr = 9.80665 * 10 * 433e6 / 299792458.0
check("10 g at 433 MHz = 142 Hz/s: 22.7 Hz (3.6 spacings) per FT8 symbol, ~1.8 kHz per transmission",
      abs(fdr - 141.6) < 0.5 and abs(fdr * 0.16 - 22.7) < 0.1 and abs(fdr * 12.64 / 1000 - 1.79) < 0.02,
      f"{fdr:.1f} Hz/s")
check("0.1 ppm at 433 MHz = 43 Hz", abs(0.1e-6 * 433e6 - 43.3) < 0.01)
rpt = -15 + db(B_REF) - 174 + NF
check("an FT8 report of -15 dB with NF 6 dB means ~ -149 dBm received", abs(rpt + 149.0) < 0.05, f"{rpt:.1f} dBm")
fspl_margin = s_lora - s_ft8
check("17.8 dB is a range factor of 7.8 in free space", abs(10 ** (fspl_margin / 20) - 7.76) < 0.05,
      f"{10 ** (fspl_margin / 20):.2f}")

print(f"\n{sum(RES)}/{len(RES)} checks PASS")
