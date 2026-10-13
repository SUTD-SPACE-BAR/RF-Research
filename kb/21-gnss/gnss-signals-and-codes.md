---
title: GNSS signals and codes — GPS, Galileo, BeiDou, GLONASS, QZSS, NavIC; BPSK vs BOC; received power and processing gain
domain: 21-gnss
slug: gnss-signals-and-codes
tags: [gnss, gps, galileo, beidou, glonass, qzss, navic, sbas, l1, l2c, l5, l1c, e1, e5, b1i, b1c, b2a, c/a-code, gold-code, bpsk, boc, cboc, tmboc, altboc, fdma, cdma, navigation-message, c/n0, processing-gain, received-power]
prerequisites: [../10-comms-modulation/spread-spectrum-dsss-fhss-css.md, ../07-noise-linearity/thermal-noise-and-noise-temperature.md, ../09-propagation-link-budget/friis-free-space-path-loss.md]
related: [gnss-receiver-architecture-acquisition-tracking.md, ttff-agps-almanac-ephemeris.md, gnss-error-sources-dop.md, rtk-ppp-and-corrections.md, gnss-interference-jamming-spoofing.md, ../08-antennas/gnss-antennas.md, ../09-propagation-link-budget/ionospheric-hf-propagation.md, ../19-regulations-safety/spectrum-allocation-ism-bands.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# GNSS signals and codes

## Questions this page answers
- What signals do GPS, Galileo, BeiDou, GLONASS, QZSS and NavIC actually transmit, and on which frequencies?
- What is the difference between L1 C/A, L1C, L2C and L5, and which ones do the ZED-F9P and MAX-M10S use?
- Why is the GPS signal "below the noise floor" and how can a receiver still use it?
- What is a C/A code, and why is it 1023 chips long at 1.023 Mcps?
- What are BOC, CBOC and TMBOC modulations, and why did Galileo and modern GPS adopt them?
- How strong is a GNSS signal at the antenna, and what C/N0 should I expect?
- Why does GLONASS use different frequencies for each satellite?
- Which regional systems (QZSS, NavIC, SBAS) are useful in Singapore?
- What is in the navigation message and how fast is it sent?

## TL;DR
- Every GNSS satellite sends a **carrier** (L-band, 1.16–1.61 GHz) modulated by a **pseudo-random ranging code** (chip rate 0.511–10.23 Mcps) and a slow **navigation message** (25–500 b/s). The receiver measures *when* a known code chip arrives (pseudorange) and the carrier phase/Doppler.
- **GPS L1 C/A**: 1575.42 MHz, BPSK, 1023-chip Gold code at 1.023 Mcps (1 ms period, one chip = 293 m), 50 b/s LNAV message. Minimum received power **−158.5 dBW = −128.5 dBm** (3 dBi linear antenna) [1]. This is the signal every receiver (incl. MAX-M10S) uses first.
- The C/A power spread over its 2.046 MHz main lobe is **≈ 17.6 dB below kT₀**, but after correlation over 1 ms the **processing gain** (≈ 43 dB chip-to-bit) gives C/N₀ ≈ 45 dB-Hz with a 290 K system — a comfortable 28 dB E_b/N₀ for 50 b/s (verified by `tools/verify/gnss_signals_link.py`).
- **Modern signals** add a data-free **pilot** channel (long coherent integration, robust tracking), longer codes (10230 chips) and **BOC** subcarriers (spectrum split away from the C/A centre, sharper correlation peak). Examples: GPS L1C (TMBOC), L2C (CM+CL), L5 (10.23 Mcps); Galileo E1 (CBOC, 4 ms code), E5a/E5b (10.23 Mcps; AltBOC together); BeiDou B1C, B2a.
- **GLONASS L1OF/L2OF** are **FDMA**: each satellite on 1602 + k·0.5625 MHz (k = −7…+6), same 511-chip code for all [9].
- **ZED-F9P** (-01B…-05B) tracks L1C/A, L1OF, E1-B/C, B1I on L1 and **L2C, L2OF, E5b, B2I** on the second band (not L5; that is the -15B variant) [11]. **MAX-M10S** is L1-only: L1C/A, E1-B/C, L1OF, B1I *or* B1C; default GPS+Galileo+BeiDou B1I with QZSS and SBAS [12].
- In **Singapore**: BeiDou GEO/IGSO satellites are high in the sky (GEO at 110.5°E ≈ 82° elevation), QZSS GEO at 127°E ≈ 63° elevation (both computed), so multi-constellation reception roughly quadruples the satellites in view compared with GPS alone ([DOP page](gnss-error-sources-dop.md)).

## Intuition (no math)
Imagine each satellite reciting a long, fixed, random-looking string of +1/−1 "chips" a million times per second, perfectly timed by an atomic clock. You hold a copy of every satellite's string. To find a satellite you slide your copy against the noisy received signal until it lines up — at that point all the tiny contributions add up coherently while noise adds randomly. The amount you had to slide tells you the signal's travel time (to within a few metres with good tracking), and you can do it simultaneously for many satellites because their strings are nearly uncorrelated (CDMA).

The signal arrives far weaker than the receiver's own thermal noise. That's fine: noise is random and averages away over thousands of chips, while the code adds up. The price is that you must already know (or search for) the code alignment and the Doppler shift — that's acquisition.

On top of the code sits a very slow data stream (the navigation message) that tells you where the satellite is (ephemeris), how its clock is off, and the time. It is so slow (50 b/s for GPS) because it must be decodable at very low signal levels.

Newer signals add tricks: a **pilot** channel with no data (so you can integrate longer without data bit flips), a **subcarrier** (BOC) that pushes the energy to the sides of the band (to coexist with the old C/A signal and to sharpen the correlation peak), and higher chip rates (L5/E5 at 10.23 Mcps: 29 m chips, ten times finer timing, better multipath resistance).

## The math

### Level 1 — the signal and its numbers
A single civil component, in complex-baseband form:
$$s(t) = \sqrt{2C}\, d(t - \tau)\, c(t - \tau)\, \cos\!\big(2\pi (f_L + f_D) t + \phi\big)$$
- $C$ (W) carrier power at the antenna port; $c(t)$ ±1 spreading code at chip rate $R_c$ (chips/s); $d(t)$ ±1 data at $R_b$ (b/s); $\tau$ (s) travel time; $f_L$ (Hz) carrier frequency; $f_D$ (Hz) Doppler (≤ ±5 kHz for a static user at L1, up to a few kHz more on a rocket).
- Chip length in metres $= c_0/R_c$: 293.1 m (1.023 Mcps), 146.5 m (2.046 Mcps), 29.3 m (10.23 Mcps).
- **Carrier-to-noise density** $C/N_0$ (dB-Hz) $= P_r(\text{dBm}) + G_{ant} - 10\log_{10}(kT_{sys}\cdot 10^3)$.

**Signal summary** (minimum received powers from the ICDs; codes and rates verified in `gnss_signals_link.py`):

| System / signal | Centre (MHz) | Modulation | Chip rate | Primary code (chips / period) | Data | Min. power (dBW) | ZED-F9P | MAX-M10S |
|---|---|---|---|---|---|---|---|---|
| GPS L1 C/A | 1575.42 | BPSK(1) | 1.023 M | 1023 / 1 ms (Gold) | LNAV 50 b/s | −158.5 [1] | ✓ | ✓ |
| GPS L1C (D+P) | 1575.42 | BOC(1,1) data + TMBOC(6,1,4/33) pilot | 1.023 M | 10230 / 10 ms; pilot overlay 1800 / 18 s | CNAV-2 100 sps (LDPC) | −157.0 total [3] | – | – |
| GPS L2C (CM+CL) | 1227.60 | BPSK, CM/CL chip-multiplexed | 2 × 0.5115 M | CM 10230 / 20 ms; CL 767250 / 1.5 s | CNAV 25 b/s → 50 sps | −160.0 (IIR-M/IIF), −158.5 (III) [1] | ✓ | – |
| GPS L5 (I5+Q5) | 1176.45 | QPSK, BPSK(10) each | 10.23 M | 10230 / 1 ms + NH10/NH20 | 50 b/s → 100 sps | −157.9 each (IIF), −157.0 (III) [2] | -15B only | – |
| Galileo E1-B/C | 1575.42 | CBOC(6,1,1/11) | 1.023 M | 4092 / 4 ms; E1-C + 25-chip secondary (100 ms) | I/NAV 250 sps | −157.25 total [4] | ✓ | ✓ |
| Galileo E5a | 1176.45 | (part of AltBOC(15,10)) | 10.23 M | 10230 + 20/100 secondary | F/NAV 50 sps | −155.25 total [4] | – | – |
| Galileo E5b | 1207.14 | (part of AltBOC) | 10.23 M | 10230 + 4/100 secondary | I/NAV 250 sps | −155.25 total [4] | ✓ | – |
| Galileo E6 | 1278.75 | BPSK(5) | 5.115 M | (HAS/CS) | — | −155.25 [4] | – | – |
| BeiDou B1I | 1561.098 | BPSK(2) | 2.046 M | 2046 / 1 ms | D1 50 b/s (+NH20) / D2 500 b/s (GEO) | −163 [5] | ✓ | ✓ (default) |
| BeiDou B1C | 1575.42 | BOC(1,1) data + QMBOC(6,1,4/33) pilot | 1.023 M | 10230 / 10 ms; pilot secondary 1800 | B-CNAV1 100 sps | −159 MEO / −161 IGSO [6] | – | ✓ (option) |
| BeiDou B2I / B2a | 1207.14 / 1176.45 | BPSK(2) / BPSK(10) pair | 2.046 / 10.23 M | 2046 / 10230 | D1/D2; B-CNAV2 | — | B2I ✓ | – |
| GLONASS L1OF | 1602 + k·0.5625 | BPSK, FDMA | 0.511 M | 511 / 1 ms (m-seq.) | 50 b/s + 100 Hz meander | −161 [7] | ✓ | ✓ |
| GLONASS L2OF | 1246 + k·0.4375 | BPSK, FDMA | 0.511 M | 511 / 1 ms | 50 b/s | — | ✓ | – |
| QZSS L1C/A, L1S, L2C, L5, L6 | as GPS; L6 1278.75 | as GPS | | | L1S = SLAS; L6 = CLAS/MADOCA | ≈ GPS | L1C/A, L2C, L1S | L1C/A, L1S |
| SBAS (WAAS/EGNOS/MSAS/GAGAN/BDSBAS/KASS/SouthPAN) | 1575.42 (L1), 1176.45 (L5 DFMC) | BPSK(1) | 1.023 M | C/A-like PRN 120–158 | 250 b/s (500 sps) | ≈ −158.5 | ✓ | ✓ |
| NavIC | 1176.45 (L5), 2492.028 (S); L1 on NVS series | BPSK(1) SPS | 1.023 M | 1023 / 1 ms | 25 b/s → 50 sps | — | – | – |

Notes: GPS powers are specified at the output of a 3 dBi **linearly** polarized antenna (≈ a 0 dBic RHCP antenna), Galileo/BeiDou/QZSS at a 0 dBi RHCP antenna, both for elevation ≥ 5° [1][4][5]. Maximum expected C/A level is −153 dBW (individual components ≤ −150 dBW) [1]; Galileo recommends designing for 7 dB above minimum [4].

### Level 1½ — code phase is range, algebra only
- **One chip is a distance.** A chip lasts $1/R_c$, and light travels $c/R_c$ in that time: 293.1 m for C/A. Measuring where the code starts, in chips, measures the range in steps of 293 m.
- **The code repeats.** The C/A code repeats every 1 ms (1023 chips), i.e. every 299.8 km. Code phase alone gives the range modulo 300 km. The satellite is 20 200–25 800 km away (67–86 ms of travel time), so the receiver takes the whole number of milliseconds from the data bit edges and time of week, or from a rough position.
- **Correlation is the processing gain.** Adding up 1023 chips coherently gains 10 log 1023 = 30.1 dB. In SNR terms: the SNR in a bandwidth B is $C/N_0 - 10\log B$; after coherent integration over T it is $C/N_0 - 10\log(1/T)$.
- **Doppler is speed over wavelength.** $f_D = v_{LOS}/\lambda$. A GPS satellite moves at 3.87 km/s, but the part of that speed along the line of sight to a user on the ground is at most $v\,R_E/r$ ≈ 0.93 km/s (satellite on the horizon). That gives at most ≈ 4.9 kHz, hence the ±5 kHz search (Earth rotation and user motion add a little).

*Worked number (verified, `tools/verify/s18b_level15_numbers.py`).* A code phase of 512.3 chips is **150.1 km** (modulo 299.8 km). A signal at 45 dB-Hz is **−18.1 dB** in a 2.046 MHz bandwidth, below the noise, and **+15 dB** after a 1 ms correlation.

### Level 2 — correlation, processing gain and why "below the noise" works
**The code.** GPS C/A codes are Gold codes: two 10-stage LFSRs, $G_1 = 1+x^3+x^{10}$ and $G_2 = 1+x^2+x^3+x^6+x^8+x^9+x^{10}$, both starting all-ones; PRN *i* = $G_1 \oplus G_2$(delayed), implemented by XOR-ing two $G_2$ taps (PRN 1: taps 2 and 6) [1]. The script regenerates PRN 1–5 and matches the IS-GPS-200 "first 10 chips" octal values (1440, 1620, 1710, 1744, 1133). Periodic autocorrelation is 1023 at zero lag and only {−65, −1, 63} elsewhere; cross-correlation between PRNs takes the same three values — worst case **−23.9 dB** relative to the peak (verified). The derivation of Gold-code properties is on the [spread-spectrum page](../10-comms-modulation/spread-spectrum-dsss-fhss-css.md).

**Correlation gain.** Multiply the received samples by a replica aligned in code and carrier and sum for a coherent time $T$. Signal amplitudes add ($\propto T$), noise powers add ($\propto T$), so the post-correlation SNR is
$$\text{SNR}_{\text{post}} = \frac{C}{N_0}\,T \quad (\text{linear}),$$
e.g. 45 dB-Hz × 1 ms → 15 dB. Before correlation, in a bandwidth $B$, $\text{SNR}_{\text{pre}} = C/(N_0 B)$ = 45 − 63.1 = −18 dB for $B$ = 2.046 MHz. The ratio $B T$ (here 2046 ≈ 33 dB) is the **processing gain** of the 1 ms correlation; chip-rate-to-bit-rate gain $10\log_{10}(R_c/R_b)$ = 43.1 dB for C/A with 50 b/s data.

**Link budget at the antenna.** With $P_r$ = −128.5 dBm, $T_{sys}$ = 290 K ($-174$ dBm/Hz) and a 0 dBic antenna, $C/N_0$ = 45.5 dB-Hz; with a good active antenna ($T_{sys}$ ≈ 150 K) 48.3 dB-Hz. Typical open-sky measurements are 40–50 dB-Hz because real powers exceed the minimum by a few dB while antenna gain toward low satellites is negative. Small rocket antennas give less: DLR's sounding rocket receivers saw < 45 dB-Hz throughout flight "mainly due to the small size of the antennas" [13]. For the same −130 dBm input, u-blox quotes the thermal noise in 2 MHz as −111 dBm [11] (−174 + 63 = −111, verified).

**What receiver "sensitivity" numbers mean.** u-blox specifies −167 dBm tracking, −160 dBm reacquisition, −148 dBm cold start (with a good external LNA) [11][12]. With $T_{sys}$ ≈ 270 K these correspond to C/N₀ of only ≈ 7, 14 and 26 dB-Hz (script). Such figures rely on long integration and aiding in static conditions; on a vehicle with dynamics, practical tracking thresholds are 25–30 dB-Hz ([receiver page](gnss-receiver-architecture-acquisition-tracking.md)).

**Spectra: BPSK vs BOC.** BPSK($n$) with chip period $T_c = 1/(n\cdot1.023\text{ MHz})$ has PSD $T_c\,\mathrm{sinc}^2(fT_c)$ with nulls at ±$1/T_c$; 90.6 % of the power lies in the ±1.023 MHz main lobe for BPSK(1). A sine-phased BOC($m$,$n$) multiplies the code by a square-wave subcarrier at $m\cdot1.023$ MHz, giving (for $2m/n$ even)
$$G_{\text{BOC}}(f) = \frac{1}{T_c}\left[\frac{\sin(\pi f T_c)\tan(\pi f T_s)}{\pi f}\right]^2,\qquad T_s = \frac{1}{2m\cdot 1.023\text{ MHz}} .$$
For BOC(1,1) this reduces to $G \propto \sin^4(x/2)/x^2$, $x = \pi f/f_c$: zero at DC and peaks where $\tan u = 2u$, i.e. at **±0.76 MHz** (verified numerically and analytically). The Gabor (RMS) bandwidth, which sets code-tracking noise and multipath resolution, rises from 1.13 MHz (BPSK(1)) to 1.98 MHz (BOC(1,1)) and 2.53 MHz (MBOC(6,1,1/11), 10/11 BOC(1,1) + 1/11 BOC(6,1)) inside a ±12 MHz front end (script). That is why Galileo E1 and GPS L1C/BeiDou B1C share 1575.42 MHz with C/A yet track more precisely — *if* the receiver front end is wide enough (±12 MHz) to keep the BOC(6,1) part.

**FDMA (GLONASS).** All satellites use the same 511-chip code, separated in frequency: L1OF channel $k$ at 1602 + 0.5625k MHz (k = −7…+6; antipodal satellites share k), L2OF at 1246 + 0.4375k MHz [9]. Consequences: a wider RF passband (≈ 1598–1606 MHz), inter-frequency biases that complicate RTK (hence RTCM 1230 code-phase biases — [RTK page](rtk-ppp-and-corrections.md)), and no CDMA cross-correlation issue. New CDMA signals (L3OC at 1202.025 MHz, L1OC/L2OC) are being added [9].

### Level 3 — navigation messages, tiered codes, signal design trade-offs
**Navigation message structures** (details and their effect on TTFF are on the [TTFF page](ttff-agps-almanac-ephemeris.md)):

| Message | Rate | Structure | Ephemeris/clock found in | Repeat |
|---|---|---|---|---|
| GPS LNAV (L1 C/A) | 50 b/s | 300-bit subframes (6 s), 5 subframes = 1500-bit frame (30 s), 25 pages → 12.5 min | subframes 1–3 | every 30 s [1] |
| GPS CNAV (L2C/L5) | 25 b/s (L2C), 50 b/s (L5), FEC rate ½ | 12-s 300-bit messages, flexible order | message types 10, 11, 30-x | ≤ 48 s typ. |
| GPS CNAV-2 (L1C) | 100 sps, LDPC | 18-s frames (3 subframes) | subframe 2 | every 18 s [3] |
| Galileo I/NAV (E1-B, E5b-I) | 250 sps, FEC ½ | 2-s pages (even+odd), 30-s subframes, 720-s frame | word types 1–4 (+5) | every 30 s [4] |
| Galileo F/NAV (E5a-I) | 50 sps | 10-s pages, 50-s subframes | pages 2–4 | 50 s |
| BeiDou D1 (MEO/IGSO B1I) | 50 b/s + NH20 | 6-s subframes, 30-s frame, 12-min superframe | subframes 1–3 | 30 s [5] |
| BeiDou D2 (GEO B1I) | 500 b/s | 0.6-s subframes, 3-s frame | subframe 1 pages 1–10 | 30 s [5] |
| GLONASS (L1OF/L2OF) | 50 b/s + 100 Hz meander | 2-s strings, 15 strings = 30-s frame, 5 frames = 2.5-min superframe | strings 1–4 ("immediate data") | every 30 s; new set every 30 min [10] |
| SBAS | 250 b/s, FEC ½ | 1-s 250-bit messages | corrections & integrity | 6 s–5 min |

**Tiered (secondary/overlay) codes.** Long effective codes are built by modulating a short primary code with a slow secondary code: Galileo E1-C (4 ms × 25 = 100 ms), E5a-I (1 ms × 20), GPS L5 Neuman–Hoffman NH10/NH20, BeiDou D1 NH20 [2][4][5]. They improve cross-correlation and spectral line spacing and let the receiver find bit/symbol boundaries, but the acquisition engine must resolve (or square away) the secondary-code sign — one reason modern acquisition starts with the short primary code.

**Pilot vs data.** A pilot (E1-C, L1CP, L5-Q, B1C pilot) carries no data, so a true PLL (not Costas) can be used, tolerating ±180° instead of ±90° of phase error, and coherent integration can exceed the 20 ms data bit. L1C puts 75 % of its power in the pilot [3]; Galileo E1 and E5 split 50/50 [4]. For rockets, the pilot's wider PLL pull-in range and freedom from bit transitions matter during boost ([rocket page](gnss-on-rockets-dynamics-and-limits.md)).

**Why 10.23 Mcps for L5/E5/B2a.** Ten-times-shorter chips shrink thermal code noise (∝ √$T_c$ for a fixed fractional spacing) and limit multipath to reflections within 29 m of path delay. The price is 20 MHz of front-end bandwidth and ADC rate. Dual-frequency L1/L5 receivers (ZED-F9P-15B, ZED-X20P, most phones) exploit this; the standard ZED-F9P uses L2C/E5b/B2I instead.

**Frequency plan choices and receiver hardware.** L1 multi-GNSS reception needs ≈ 1559–1606 MHz (B1I to GLONASS G1) — about 47 MHz. That is why the MAX-M10S cannot combine B1I with GLONASS or B1C (footnote: "BeiDou B1I cannot be enabled simultaneously with BeiDou B1C or GLONASS L1OF") [12]: its front end covers either the low edge (B1I) or the high edge (G1) of L1 in addition to 1575.42 MHz.

## Design equations & rules of thumb

| Quantity | Equation | Typical value |
|---|---|---|
| Chip length | $c_0/R_c$ | 293 m (C/A), 29.3 m (L5) |
| C/N₀ | $P_r + G - 10\log(kT_{sys}) + 30$ (dBm units) | 40–50 dB-Hz open sky; 45.5 at −128.5 dBm, 290 K |
| PSD below kT | $P_r - 10\log B + 174$ | C/A ≈ 17.6 dB below kT₀ |
| Post-correlation SNR | $(C/N_0)\,T$ | 15 dB at 45 dB-Hz, 1 ms |
| Processing gain | $10\log(R_c/R_b)$ | 43.1 dB (C/A, 50 b/s) |
| Gold cross-corr | {−65, −1, 63}/1023 | −23.9 dB worst |
| L1 Doppler | $v_{LOS}/\lambda$, λ = 0.1903 m | ±5 kHz satellite (static user); 2.6 kHz per 500 m/s of user velocity |
| BOC(1,1) PSD peak | tan u = 2u | ±0.76 MHz |
| Sensitivity ↔ C/N₀ | $C/N_0 ≈ P + 174 - NF$ | −167 dBm ↔ ≈ 7 dB-Hz |

## Worked examples
**1 — What C/N₀ should the Avionics-C MAX-M10S see?** Minimum GPS power −128.5 dBm (0 dBic equivalent). A 25 mm passive patch at zenith ≈ +3 dBic → −125.5 dBm. System temperature with the M10S's integrated LNA (NF 1.5 dB [12] → 120 K) plus antenna temperature ≈ 100 K → 220 K → $10\log(kT)$ = −175.2 dBm/Hz. C/N₀ = −125.5 + 175.2 = **49.7 dB-Hz** at zenith, minimum-power satellite; at 15° elevation the patch gain falls by ~5–8 dB → ≈ 42–45 dB-Hz. If you measure < 35 dB-Hz on the bench with open sky, something is wrong (detuned patch, interference, or a ground plane far smaller than specified — [GNSS antennas](../08-antennas/gnss-antennas.md)).

**2 — Doppler and code Doppler on a rocket at burnout.** Vertical velocity 600 m/s, satellite at 60° elevation: LOS rate 520 m/s → carrier Doppler 520/0.1903 = **2.73 kHz** on top of the satellite's ±5 kHz; code Doppler = 2.73 kHz × (1.023 MHz/1575.42 MHz) = **1.77 chips/s**. In one second the code slides by 1.77 chips — a code loop not aided by the carrier would have to track that; carrier aiding removes it ([receiver page](gnss-receiver-architecture-acquisition-tracking.md)).

**3 — Which signals would an L1-only antenna on a ZED-F9P lose?** The ZED-F9P uses L2C/L2OF/E5b/B2I as its second band [11]. With the team's flown L1-only antenna it falls back to single-frequency operation: no ionosphere-free combination, slower and less reliable RTK ambiguity resolution, and the manual requires disabling the L2 signals consistently ([u-blox integration](gnss-receiver-integration-u-blox.md), [antennas example 2](../08-antennas/gnss-antennas.md#worked-examples)).

**4 — BeiDou B1I vs B1C on the MAX-M10S.** B1I minimum power is −163 dBW versus −159 dBW for B1C MEO [5][6]: B1C is 4 dB stronger and BOC-modulated (better multipath), but only BeiDou-3 satellites transmit it, whereas B1I is on BDS-2 and BDS-3 (including the GEO/IGSO satellites that are high above Singapore). u-blox's default is B1I; the single-GNSS sensitivity table shows B1C cold-start at −136 dBm vs −146 dBm for B1I [12] — B1I is the better acquisition signal for the M10.

## Practical notes
- **Which constellations to enable** on a rocket: all available (GPS+Galileo+BeiDou on the M10S; all four on the F9P) for availability and DOP, but check the receiver's maximum navigation rate falls as constellations are added (M10S: 10 Hz GPS+GAL, 6 Hz with GLO, 3 Hz with BDS B1I in default mode; 18–25 Hz single-GNSS [12]; F9P RTK 7 Hz with 4 GNSS, 20 Hz GPS-only [11]) — [integration page](gnss-receiver-integration-u-blox.md).
- **QZSS** is processed with GPS only (u-blox: QZSS can be enabled only with GPS) [11]; its L1S SLAS corrections are designed for Japan and are not useful in Singapore; CLAS (L6) needs a NEO-D9C and covers Japan [11].
- **SBAS in Singapore**: Singapore is outside the WAAS/EGNOS/MSAS/GAGAN/SouthPAN service areas; GEO SBAS satellites may be visible and u-blox receivers enable SBAS by default. Corrections from a distant SBAS describe a different ionosphere; consider restricting the SBAS PRN mask or disabling SBAS and compare logged accuracy (the F9P datasheet also notes SBAS reception degrades time accuracy) [11].
- **NavIC**: Singapore is ≈ 1260 km from India's Nicobar Islands (computed), i.e. inside the "India plus 1500 km" primary service radius, but neither the ZED-F9P nor the MAX-M10S supports NavIC [11][12]; legacy NavIC satellites transmit on L5 and S-band only.
- **Signal health and new satellites**: not all GPS satellites transmit L2C/L5 (IIR satellites have no civil L2) [1]; dual-frequency availability is therefore lower than satellite count.

## Common mistakes & misconceptions
- **"GPS works below the noise floor, so noise doesn't matter."** The *pre-correlation* SNR is negative, but C/N₀ is what counts; every dB of system noise temperature costs a dB of C/N₀ — keep the first LNA close to the antenna.
- **"All GNSS share one frequency."** L1/E1/B1C share 1575.42 MHz, but B1I (1561 MHz) and GLONASS (1598–1606 MHz) do not; a narrow 1575 MHz SAW or patch can silently drop them.
- **"BOC signals are just faster codes."** E1/L1C/B1C have the *same* 1.023 Mcps chip rate as C/A; the subcarrier changes the spectrum shape and correlation function (multiple peaks — risk of false lock to a side peak).
- **"−167 dBm sensitivity means I can track −167 dBm signals on my rocket."** It is a static lab figure ≈ 7 dB-Hz; dynamic tracking needs ≈ 25–30 dB-Hz.
- **"The ZED-F9P is an L1/L5 receiver."** The standard F9P is L1/L2 (L2C/E5b/B2I); only the -15B variant is L1/L5 [11] (an L1+L5 claim in [LNA parts](../18-components-parts/lna-pa-gain-block-mmics.md) was corrected on 2026-10-03).

## How to simulate / verify
- `python3 tools/verify/gnss_signals_link.py` — C/A code generation vs IS-GPS-200 octal table, auto/cross-correlation values, chip lengths, BPSK/BOC/MBOC spectra (power fractions, Gabor bandwidths, BOC(1,1) peak), C/N₀ table from minimum powers, sensitivity ↔ C/N₀. ALL PASS.
- `tools/verify/comms_spread_spectrum.py` (domain 10) — independent C/A code and SBAS PRN check.
- With an SDR: record L1 through an active antenna and look at the spectrum — no GNSS signal is visible above the noise (only the LNA/filter passband shape); the satellites appear only after correlation ([SDR page](sdr-gnss-and-diy-receivers.md)).

## Open questions / gaps
- GLONASS minimum power (−161 dBW) taken from a search-result summary of the GLONASS ICD Ed. 5.1, not re-read.
- NavIC SPS ICD and QZSS IS-QZSS-PNT were not read in this pass; their rows rely on secondary knowledge (marked).
- Exact u-blox front-end bandwidths per band are not published beyond the antenna band table on the [antennas page](../08-antennas/gnss-antennas.md).

## Sources
1. U.S. Space Force, *IS-GPS-200N*, NAVSTAR GPS Space Segment/Navigation User Interfaces, 1 Aug 2022 — §3.2.1.3 C/A code; L2 CM/CL codes (10230 / 767250 chips at 511.5 kcps); §3.3.1.6 Table 3-Va minimum received power (3 dBi linear antenna); §6.3.1 maximum levels; LNAV structure (300-bit subframes). https://www.navcen.uscg.gov/sites/default/files/pdf/gps/IS-GPS-200N.pdf (standard)
2. *IS-GPS-705J*, GPS L5 interfaces, 2022 — Table 3-III minimum power (−157.9 dBW IIF, −157.0 dBW III per component), 10.23 Mcps codes, NH10/NH20, 100 sps. https://www.navcen.uscg.gov/sites/default/files/pdf/gps/IS-GPS-705J.pdf (standard)
3. *IS-GPS-800J*, GPS L1C, 2022 — Table 3.2-1 (−157 dBW composite; L1CP −158.25, L1CD −163), BOC(1,1)/TMBOC, 10230-chip 10-ms codes, 18-s overlay, LDPC. https://www.navcen.uscg.gov/sites/default/files/pdf/gps/IS-GPS-800J.pdf (standard)
4. European Union, *Galileo OS SIS ICD Issue 2.1*, Nov 2023 — Tables 5, 9, 10, 12, 14 (chip/symbol rates, CBOC, min/max power, code lengths), AltBOC. https://www.gsc-europa.eu/sites/default/files/sites/all/files/Galileo_OS_SIS_ICD_v2.1.pdf (standard)
5. China Satellite Navigation Office, *BDS-SIS-ICD-B1I-3.0*, 2019 — −163 dBW, 2.046 Mcps/2046 chips, D1 50 b/s + NH20, D2 500 b/s. http://www.beidou.gov.cn/xt/gfxz/201902/P020190227593621142475.pdf (standard)
6. CSNO, *BDS-SIS-ICD-B1C-1.0*, 2017 — Table 4-4 (−159 dBW MEO, −161 IGSO), BOC(1,1)/QMBOC(6,1,4/33), 10230 chips, 1800-chip pilot secondary, 100 sps. http://en.beidou.gov.cn/SYSTEMS/ICD/ (standard)
7. Russian Institute of Space Device Engineering, *GLONASS ICD Edition 5.1*, 2008 — L1 minimum power −161 dBW (via search summary; not re-read). https://www.unavco.org/help/glossary/docs/ICD_GLONASS_5.1_(2008)_en.pdf (standard — secondary access)
8. E. D. Kaplan, C. J. Hegarty (eds.), *Understanding GPS/GNSS: Principles and Applications*, 3rd ed., Artech House, 2017 — ch. 4 (GPS signals), ch. 9–11 (other GNSS), BOC spectra. (textbook; general reference)
9. ESA Navipedia, "GLONASS Signal Plan" — FDMA formulas, k range, 511 chips, 50 b/s, 100 Hz meander, L3OC 1202.025 MHz. https://gssc.esa.int/navipedia/index.php/GLONASS_Signal_Plan (encyclopedia, ESA)
10. ESA Navipedia, "GLONASS Navigation Message" — 2-s strings, 30-s frames, 2.5-min superframe, immediate data in strings 1–4, new ephemeris every 30 min. https://gssc.esa.int/navipedia/index.php/GLONASS_Navigation_Message (encyclopedia, ESA)
11. u-blox, *ZED-F9P-04B Data sheet*, UBX-21044850 R05, 2024 — supported signals (Table 7), QZSS/SBAS/CLAS notes, sensitivity, max update rates, noise floor statement via [14]. https://content.u-blox.com/sites/default/files/ZED-F9P-04B_DataSheet_UBX-21044850.pdf (manufacturer)
12. u-blox, *MAX-M10S Data sheet*, UBX-20035208 R08 — signals (Table 4), B1I/B1C/GLONASS exclusivity footnote, defaults, sensitivity tables, NF 1.5 dB, update rates. https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf (manufacturer)
13. B. Braun, M. Markgraf, L. Rheinwald, S. Weiß, M. Hörschgen-Eggers, "First Test of a Multi-Constellation, Multi-Frequency GNSS Receiver on Board a Sounding Rocket," *Eng. Proc.* 126:39, 2026 (ENC 2025). https://doi.org/10.3390/engproc2026126039 (conference, open access)
14. u-blox, *ZED-F9P Integration manual*, UBX-18010802 R16 — §4.6.1 (−128 dBm signal vs −111 dBm noise). https://content.u-blox.com/sites/default/files/ZED-F9P_IntegrationManual_UBX-18010802.pdf (manufacturer)
15. P. Misra, P. Enge, *Global Positioning System: Signals, Measurements, and Performance*, 2nd ed., 2006 — ch. 9–10 (signal structure, correlation). (textbook; general reference)
