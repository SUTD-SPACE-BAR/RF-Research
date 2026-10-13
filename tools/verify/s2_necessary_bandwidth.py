#!/usr/bin/env python3
"""
s2_necessary_bandwidth.py — necessary bandwidth, emission designators, band names and the
out-of-band / spurious boundary (gap slice S2, W5-S2).

Used by: kb/19-regulations-safety/spectrum-allocation-ism-bands.md (band names, emission designators,
         OoB vs spurious domains); kb/10-comms-modulation/analog-modulation-am-fm-pm-ssb.md
         (necessary-bandwidth table, CW efficiency).

Sources transcribed (numbers re-typed, not copied text):
  ITU RR Appendix 1 (Rev. WRC-12) §2: Bn as three numerals + one letter (H/K/M/G at the decimal point)
      and its footnote examples (0.002 Hz = H002 ... 180.5 kHz = 181K, 5.65 GHz = 5G65).
  Rec. ITU-R SM.1138-3 (10/2019) Annex 1: formulas and sample calculations (100HA1A, 2K10A2A, 6K00A3E,
      3K00H3E, 2K70J3E, 8K00A3E, 304HF1B, 16K0F3E, 180KF3E, 3M00P0N, 16M6W7D).
  NTIA Manual Annex J (Jan 2021 rev 1/2023): telegraphy B ~= 0.8 x WPM; 2K80J3E (M 2.7 kHz, Ml 350 Hz);
      11K0F3E; FSK telegraphy Bn = B + 2KD.
  Rec. ITU-R SM.329-13 (09/2024) §2.3: spurious domain >= 250 % of Bn from the centre frequency.
  Rec. ITU-R SM.1539-2 (09/2024) Table: narrow-band threshold BL and wideband threshold BU per range.
  Rec. ITU-R V.431-8 (08/2015) Table 1: band N = 0.3e N ... 3e N Hz (lower exclusive, upper inclusive).

Run:  python3 tools/verify/s2_necessary_bandwidth.py      (≈ 5 s; ALL PASS expected)
"""
import math
import numpy as np

FAILS = []


def check(name, got, want, tol=0.0):
    ok = (got == want) if isinstance(want, str) else abs(got - want) <= tol
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: got {got!r}, want {want!r}" + ("" if isinstance(want, str) else f" ±{tol}"))
    if not ok:
        FAILS.append(name)


# ---------------------------------------------------------------- 1. RR Appendix 1 notation
def bn_code(hz):
    """Format a necessary bandwidth in hertz the RR Appendix 1 way: three significant figures,
    unit letter in place of the decimal point. Rounding is half-up (180.5 kHz -> 181K)."""
    for unit, scale in (("G", 1e9), ("M", 1e6), ("K", 1e3), ("H", 1.0)):
        v = hz / scale
        if v >= 1.0 or unit == "H":
            break
    if unit == "H" and v < 1.0:                  # 0.001-0.999 Hz -> H in the first position
        digits = int(math.floor(v * 1000 + 0.5 + 1e-9))
        return f"H{digits:03d}"
    # three significant figures, half-up
    exp = int(math.floor(math.log10(v)))          # 0, 1 or 2
    scaled = int(math.floor(v * 10 ** (2 - exp) + 0.5 + 1e-9))
    if scaled >= 1000:                             # e.g. 999.6 kHz rounds up to 1M00
        if exp < 2:
            exp += 1
            scaled = 100
        else:
            return bn_code(1000 * scale)
    s = f"{scaled:03d}"
    pos = exp + 1                                  # number of digits before the decimal point
    return s[:pos] + unit + s[pos:] if pos < 3 else s + unit


print("1. RR Appendix 1 notation (footnote examples)")
for hz, code in [(0.002, "H002"), (0.1, "H100"), (25.3, "25H3"), (400, "400H"), (2400, "2K40"),
                 (6e3, "6K00"), (12.5e3, "12K5"), (180.4e3, "180K"), (180.5e3, "181K"), (180.7e3, "181K"),
                 (1.25e6, "1M25"), (2e6, "2M00"), (10e6, "10M0"), (202e6, "202M"), (5.65e9, "5G65")]:
    check(f"{hz:g} Hz", bn_code(hz), code)

# ---------------------------------------------------------------- 2. SM.1138 / NTIA formulas
print("\n2. Necessary-bandwidth formulas vs SM.1138-3 / NTIA Annex J sample calculations")


def bn_cw(B, K=5):            # A1A: Bn = B K   (K = 5 fading, 3 non-fading)
    return B * K


def bn_mcw(B, M, K=5):        # A2A: Bn = B K + 2M
    return B * K + 2 * M


def bn_dsb(M):                # A3E: 2M
    return 2 * M


def bn_ssb_fc(M):             # H3E: M
    return M


def bn_ssb_sc(M, Ml):         # J3E: M - lowest modulation frequency
    return M - Ml


def bn_fm(M, D, K=1.0):       # F3E (Carson): 2M + 2DK
    return 2 * M + 2 * D * K


def bn_fsk(B, D, K=1.2):      # F1B: 2M + 2DK with M = B/2  ->  B + 2DK
    return bn_fm(B / 2, D, K)


cases = [
    ("A1A Morse 25 WPM (B=20 Bd, K=5)", bn_cw(20), "100H", "100HA1A"),
    ("A2A tone-keyed Morse (B=20, M=1000)", bn_mcw(20, 1000), "2K10", "2K10A2A"),
    ("A3E telephony M=3000", bn_dsb(3000), "6K00", "6K00A3E"),
    ("H3E SSB full carrier M=3000", bn_ssb_fc(3000), "3K00", "3K00H3E"),
    ("J3E SSB-SC 300-3000 Hz", bn_ssb_sc(3000, 300), "2K70", "2K70J3E"),
    ("J3E NTIA 350-2700 Hz", bn_ssb_sc(2700, 350), "2K35", "(NTIA lists 2K80J3E — authorised, not computed)"),
    ("A3E sound bcast M=4000", bn_dsb(4000), "8K00", "8K00A3E"),
    ("F1B FSK 100 Bd, 170 Hz shift", bn_fsk(100, 85), "304H", "304HF1B"),
    ("F3E NBFM D=5 kHz M=3 kHz", bn_fm(3000, 5000), "16K0", "16K0F3E"),
    ("F3E NBFM D=2.5 kHz M=3 kHz", bn_fm(3000, 2500), "11K0", "11K0F3E"),
    ("F3E broadcast D=75 kHz M=15 kHz", bn_fm(15000, 75000), "180K", "180KF3E"),
    ("P0N radar 1 us pulse, K=1.5: 2K/t", 2 * 1.5 / 1e-6, "3M00", "3M00P0N"),
    ("W7D OFDM 53 x 312.5 kHz", 53 * 312.5e3, "16M6", "16M6W7D"),
]
for name, bn, code, desig in cases:
    check(f"{name} -> {desig}", bn_code(bn), code)

print("\n   NTIA: manual telegraphy baud ~= 0.8 x WPM; Bn = 5B (fading)")
for wpm, want in [(13, 52.0), (25, 100.0)]:
    check(f"   {wpm} WPM -> Bn", bn_cw(0.8 * wpm), want, 1e-9)

print("\n   CW vs SSB noise bandwidth advantage at equal power (receiver filter = Bn or typical CW filter)")
for bw in (100, 250, 500):
    print(f"     CW filter {bw:4d} Hz vs SSB 2.7 kHz: {10*math.log10(2700/bw):5.1f} dB less noise")
check("   100 Hz vs 2.7 kHz advantage (dB)", 10 * math.log10(2700 / 100), 14.31, 0.01)

# ---------------------------------------------------------------- 3. LoRa 99 % OBW and designator
print("\n3. LoRa: 99 % occupied bandwidth by simulation (random symbols, complex baseband)")


def lora_waveform(sf, bw, nsym, osr, rng):
    N = 2 ** sf
    fs = bw * osr
    ns = N * osr
    t = np.arange(ns) / fs
    Ts = N / bw
    out = []
    phase0 = 0.0
    for _ in range(nsym):
        k = rng.integers(0, N)
        # instantaneous frequency: -bw/2 + bw*((t/Ts + k/N) mod 1)
        f = -bw / 2 + bw * np.mod(t / Ts + k / N, 1.0)
        ph = phase0 + 2 * np.pi * np.cumsum(f) / fs
        out.append(np.exp(1j * ph))
        phase0 = ph[-1]
    return np.concatenate(out), fs


def obw99(x, fs, nfft=1 << 14):
    from scipy.signal import welch
    f, p = welch(x, fs=fs, nperseg=nfft, return_onesided=False, window="hann")
    idx = np.argsort(f)
    f, p = f[idx], p[idx]
    c = np.cumsum(p) / np.sum(p)
    lo = f[np.searchsorted(c, 0.005)]
    hi = f[np.searchsorted(c, 0.995)]
    return hi - lo


rng = np.random.default_rng(1)
res = {}
for sf, bw in [(7, 125e3), (9, 125e3), (12, 125e3), (7, 250e3), (7, 500e3)]:
    nsym = max(40, int(4000 / 2 ** (sf - 7)))
    x, fs = lora_waveform(sf, bw, min(nsym, 400), 8, rng)
    ob = obw99(x, fs)
    res[(sf, bw)] = ob
    print(f"     SF{sf:2d} BW {bw/1e3:5.0f} kHz: 99 % OBW = {ob/1e3:6.1f} kHz = {ob/bw:5.3f} x BW -> {bn_code(ob)}F1D"
          f"  (nominal-BW designator {bn_code(bw)}F1D)")
check("SF7/125 99 % OBW within 1.02-1.12 x BW (canonical ≈ 133 kHz)", float(1.02 <= res[(7, 125e3)] / 125e3 <= 1.12), 1.0)

# ---------------------------------------------------------------- 4. OoB / spurious boundary
print("\n4. Out-of-band vs spurious domain boundary (SM.329 §2.3 + SM.1539 Table)")
SM1539 = [  # (f_lo, f_hi, BL, BU)
    (9e3, 150e3, 250, 10e3), (150e3, 30e6, 4e3, 100e3), (30e6, 1e9, 25e3, 10e6),
    (1e9, 3e9, 100e3, 50e6), (3e9, 10e9, 100e3, 100e6), (10e9, 15e9, 300e3, 250e6),
    (15e9, 26e9, 500e3, 500e6), (26e9, 1e15, 1e6, 500e6)]


def spurious_offset(fc, bn):
    for lo, hi, BL, BU in SM1539:
        if lo < fc <= hi:
            if bn < BL:
                return 2.5 * BL
            if bn > BU:
                return BU + 1.5 * bn
            return 2.5 * bn
    raise ValueError


for fc, bn, label in [(434.125e6, 125e3, "E22 CH24, LoRa 125 kHz"), (434.125e6, 133e3, "E22 CH24, 99 % OBW 133 kHz"),
                      (434.125e6, 500e3, "E22 CH24, LoRa 500 kHz"), (868.125e6, 125e3, "E220 CH18, 125 kHz"),
                      (145e6, 11e3, "2 m NBFM 11K0F3E"), (14.2e6, 2.7e3, "20 m SSB 2K70J3E"),
                      (24.125e9, 250e6, "24 GHz FMCW 250 MHz sweep")]:
    off = spurious_offset(fc, bn)
    print(f"     {label:30s}: OoB domain {bn/2e3:8.2f} … {off/1e3:9.1f} kHz from centre; spurious beyond "
          f"{(fc-off)/1e6:.4f} / {(fc+off)/1e6:.4f} MHz")
check("SM.1539 Example 1 (26 MHz, Bn 1.8 kHz -> 2.5 BL = 10 kHz)", spurious_offset(26e6, 1.8e3), 10e3, 1e-6)
check("E22 CH24 at 125 kHz: spurious from 312.5 kHz", spurious_offset(434.125e6, 125e3), 312.5e3, 1e-6)
check("2 m NBFM 11 kHz < BL: spurious from 62.5 kHz", spurious_offset(145e6, 11e3), 62.5e3, 1e-6)

# ---------------------------------------------------------------- 5. ITU band numbers
print("\n5. ITU band number N: 0.3e N < f <= 3e N Hz (V.431-8 Table 1)")
NAMES = {3: "ULF", 4: "VLF", 5: "LF", 6: "MF", 7: "HF", 8: "VHF", 9: "UHF", 10: "SHF", 11: "EHF", 12: "(none)"}


def band_number(f):
    return math.ceil(math.log10(f / 3.0))   # f <= 3e N  ->  N >= log10(f/3)


for f, want in [(27.12e6, 7), (30e6, 7), (30.000001e6, 8), (144e6, 8), (300e6, 8), (433.92e6, 9), (915e6, 9),
                (1575.42e6, 9), (2.45e9, 9), (3e9, 9), (5.8e9, 10), (24.125e9, 10), (60e9, 11), (77e9, 11), (122.5e9, 11)]:
    n = band_number(f)
    check(f"{f/1e6:12.6f} MHz -> band {n} {NAMES.get(n,'')}", n, want, 0)

print("\nALL PASS" if not FAILS else f"\nFAILED: {FAILS}")
