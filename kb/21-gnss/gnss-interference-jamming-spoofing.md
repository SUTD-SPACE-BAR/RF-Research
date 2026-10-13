---
title: GNSS interference, jamming and spoofing — in-band vs out-of-band, self-interference from on-board radios and clocks, J/S tolerance, detection and mitigation
domain: 21-gnss
slug: gnss-interference-jamming-spoofing
tags: [gnss, interference, jamming, spoofing, meaconing, desense, blocking, intermodulation, harmonics, clock-harmonics, self-interference, lora, e22, e220, esp32, wifi, saw-filter, notch, j/s, spectral-separation, agc, cw-suppression, osnma, u-blox, mon-rf, sec-sig, max-m10s, zed-f9p, radio-horizon]
prerequisites: [gnss-receiver-architecture-acquisition-tracking.md, ../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md, ../07-noise-linearity/dynamic-range-sfdr-blocking.md]
related: [gnss-receiver-integration-u-blox.md, gnss-on-rockets-dynamics-and-limits.md, ../08-antennas/gnss-antennas.md, ../08-antennas/antennas-on-rockets.md, ../15-lora-ism-radios/rocket-telemetry-radio-design.md, ../13-pcb-rf-layout-emc/emc-emi-fundamentals.md, ../13-pcb-rf-layout-emc/shielding-and-isolation.md, ../18-components-parts/filter-parts-saw-ceramic-ltcc.md, ../19-regulations-safety/spectrum-allocation-ism-bands.md, sdr-gnss-and-diy-receivers.md]
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# GNSS interference, jamming and spoofing

## Questions this page answers
- Why does my GNSS lose satellites when the LoRa transmitter keys up?
- Can harmonics of my 433/868/915 MHz radio, or my MCU's crystal, land in a GNSS band?
- How strong does an interferer have to be to break GNSS tracking?
- What is the difference between in-band and out-of-band interference, blocking and desensitisation?
- How much isolation do I need between a 2 W telemetry antenna and a MAX-M10S?
- What is spoofing, how do receivers detect it, and does u-blox report jamming/spoofing?
- Are GNSS jammers or repeaters legal? Can I test with one?
- Why do sounding rockets see jamming at high altitude?

## TL;DR
- GNSS arrives at ≈ −130 dBm; a **wideband in-band interferer of only ≈ −95 dBm** at the antenna drops C/N₀ from 45 to 28 dB-Hz (J/S ≈ 35 dB; narrowband ≈ −98 dBm) (Kaplan–Hegarty model, `tools/verify/gnss_self_interference.py`). A 10 mW in-band jammer breaks tracking out to ≈ 2.7 km in free space; a −30 dBm spur (the regulatory spurious limit above 1 GHz) within ≈ 27 m.
- **Out-of-band** signals (your 433/868/915 MHz and 2.4 GHz radios) must be kept below the receiver's **blocking immunity**: MAX-M10S ≈ −15 dBm at 400–500 MHz, −17 dBm at 915 MHz, −18 dBm at 2.44 GHz, but **−35 dBm near 525 and 787 MHz** where LNA harmonics fall in-band (u-blox) [1]. A 2 W E22 at 433 MHz therefore needs ≈ **48 dB** of isolation to the M10S RF input (antenna coupling + GNSS antenna/filter rejection). The M10S front end is LNA-then-SAW, so u-blox recommends an **external SAW in front** when other radios are present [1].
- **Self-interference hits found** (script): crystal/clock harmonics **25 MHz × 63 = 1575.0 MHz** and **8 MHz × 197 = 1576 MHz** inside the C/A main lobe; **24 MHz (Teensy 4.1) × 65 and 40 MHz (ESP32) × 39 = 1560 MHz** inside BeiDou B1I (the M10S default); 40/50/80 MHz × n = 1600 MHz inside GLONASS G1; 40 MHz × 30 = 1200 MHz in E5b/B2I (F9P second band). **E22 channels 0–3 (410.125–413.125 MHz) put the 3rd harmonic in the GPS L2 band and CH 5–6 (415–416 MHz) in GLONASS G2 — both tracked by the ZED-F9P**; CH 10–22 hit Galileo E6; the default CH 23 and CH 24 are clean. **Avoid CH 0–9 (CH 4 and 7–9 are edge/filter-skirt cases) and use CH 24 = 434.125 MHz**, which also satisfies the Singapore band-edge rule at any LoRa bandwidth. No harmonic of 863–928 MHz lands in any GNSS band. **Intermod**: Wi-Fi/BLE (≈ 2437–2442 MHz) − 868 MHz (2nd order) and Wi-Fi − 2 × 433 MHz (3rd order) land in L1/E1.
- **Detection (u-blox)**: `UBX-MON-RF` (AGC count, CW-suppression level, noise per ms, antenna status), `UBX-SEC-SIG` / `SEC-SIGLOG` (jamming and spoofing states; spoofing can only be detected when the receiver *transitions* from genuine to spoofed signals) [2][3]; Galileo **OSNMA** authentication is supported on recent F9P firmware [2].
- **Never transmit in GNSS bands**: jammers and re-radiators are not permitted as SRDs anywhere reviewed ([spectrum allocation](../19-regulations-safety/spectrum-allocation-ism-bands.md)); test conducted (cabled, attenuated) or in a shielded enclosure only ([SDR page](sdr-gnss-and-diy-receivers.md)).

## Intuition (no math)
The GNSS receiver's front end is a very sensitive amplifier that must pass a signal 20 dB below its own noise while sitting centimetres from a 2 W transmitter. Two different things can go wrong:
1. **In-band interference** — energy *at* GNSS frequencies (a clock harmonic, a transmitter spur, a jammer). No filter can remove it without removing the satellites; it simply adds noise or a false signal. Only prevention (don't generate it, shield it, keep it away) helps.
2. **Out-of-band interference** — a strong signal at another frequency (433 MHz). It shouldn't matter, but the front end isn't perfectly linear: a strong blocker compresses the LNA (desensitisation), mixes with other signals or with itself (harmonics, intermodulation) to create in-band products, or simply overloads the ADC/AGC. Filters before the first nonlinear stage, and distance, solve this.

Spoofing is different: a fake but plausible GNSS signal, stronger than the real one, that the receiver locks onto and then drags to a false position or time. Defences check for physical consistency (all satellites the same power, sudden jumps, clock inconsistencies, angle of arrival) or cryptographic authentication (Galileo OSNMA).

## The math

### Level 1 — interference-to-signal arithmetic
Equivalent carrier-to-noise density with an interferer of power $J$ (W) against signal $S$ (Kaplan–Hegarty) [4]:
$$\left(\frac{C}{N_0}\right)_{eq} = \left[\frac{1}{C/N_0} + \frac{J/S}{Q\,R_c}\right]^{-1}$$
$R_c$ = chip rate (1.023 × 10⁶ for C/A); $Q$ = spectral separation factor: ≈ 1 narrowband at a spectral peak, 1.5 matched-spectrum BPSK, 2 wideband noise. Solving for the J/S that brings 45 dB-Hz down to a requirement:

| Interferer type | 45 → 35 dB-Hz | 45 → 28 dB-Hz | J for S = −130 dBm (28 dB-Hz case) |
|---|---|---|---|
| Narrowband (Q ≈ 1) | 24.6 dB | 32.0 dB | −98 dBm |
| Matched BPSK (Q = 1.5) | 26.4 dB | 33.8 dB | −96 dBm |
| Wideband (Q = 2) | 27.7 dB | 35.0 dB | −95 dBm |

(script). Free-space distance at which an EIRP $P_J$ reaches $J$: $d = 10^{(P_J - J - 20\log_{10}f + 147.55)/20}$ m. For J = −95 dBm at L1: −30 dBm spur → 27 m; 10 mW → 2.7 km; 1 W → 27 km.

### Level 2 — the front end under strong signals
**Blocking and desense.** A blocker of power $P_B$ at the LNA input compresses gain once $P_B$ approaches the LNA's input P1dB; before that, it raises the noise figure through reciprocal mixing (LO phase noise) and gain compression of the wanted signal; the AGC also turns down, wasting ADC range. Manufacturers summarise this as an "out-of-band immunity" level — the power at RF_IN that causes no degradation. MAX-M10S, low-gain mode, 64QAM 10 MHz test signal [1]:

| f (MHz) | 400–500 | ~525 | ~640 | ~787 | 915 | 1460 | 1710–1980 | 2350–2690 |
|---|---|---|---|---|---|---|---|---|
| Immunity (dBm) | −15 | −35 | −25 | −35 | −17 | −30 | −25 | −18 |

The dips at ≈ 525 MHz (×3 = 1575) and ≈ 787 MHz (×2 = 1575, LTE Band 13/14 uplink territory) come from harmonics generated at the LNA input; an external SAW in front suppresses them [1]. This is also why u-blox integrates an LTE B13 notch.

**Required isolation** (conducted TX power to GNSS RF_IN): $I_{req} = P_{TX} - P_{immunity}$ (dB), to be supplied by antenna-to-antenna coupling, the GNSS antenna's own out-of-band rejection (a 1575 MHz patch is badly mismatched at 433 MHz) and any SAW. u-blox notes practical antenna isolation of 15–20 dB, or 6–10 dB in very small devices [1]; for the ZED-F9P's active antenna u-blox asks for ≥ 40 dB out-of-band rejection in the antenna ([antennas page](../08-antennas/gnss-antennas.md)).

**Harmonics and intermodulation.** A nonlinearity $y = a_1x + a_2x^2 + a_3x^3$ driven by tones $f_a, f_b$ produces $m f_a + n f_b$ products; second-order products scale 2 dB per dB of input, third-order 3 dB/dB ([intermod](../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md)). In-band products are generated **either in the transmitter** (its own harmonics/spurs, radiated by its antenna) or **in the GNSS front end** (from two strong out-of-band signals).

*Harmonics of the Space Bar radio bands* (n = 2–5 against the GNSS signal bands incl. main lobes; L1/E1/B1C 1563.1–1587.7, B1I 1559.1–1563.1, G1 1597.6–1605.9, GPS L2 allocation 1215–1240 with the u-blox L2C band 1223–1231, G2 1242.4–1249.1, E5b/B2I 1196.9–1217.4, L5/E5a/B2a 1166.2–1186.7, E6 1258.3–1299.2 MHz; `gnss_self_interference.py` §2b):

| Radio band | Harmonic that lands in a GNSS band | Frequencies that do it |
|---|---|---|
| E22-400T33D tuning range 410.125–493.125 MHz (f = 410.125 + CH × 1 MHz, CH 0–83, default CH 23 = 433.125 MHz [9]) | 3rd → GPS L2 allocation | 410.125–413.33 MHz (**CH 0–3**: 1230.4, 1233.4, 1236.4, 1239.4 MHz; CH 0 is inside the u-blox L2C band) |
| | 3rd → GLONASS G2 | 414.13–416.37 MHz (**CH 5–6**: 1245.4, 1248.4 MHz; CH 4 = 1242.4 MHz sits on the G2 lower edge) |
| | 3rd → Galileo E6 | 419.4–433.07 MHz (CH 10–22; matters only for E6 receivers such as the ZED-X20P, not the F9P/M10S) |
| | 2nd, 4th, 5th | none in GNSS bands (4 × 410 = 1640 MHz is above L1) |
| Singapore/EU SRD 433.05–434.79 MHz | 3rd → E6 edge only for 433.05–433.07 MHz | CH 23 → 1299.375 MHz (0.17 MHz above E6); **CH 24 (434.125) → 1302.4 MHz, above the 1215–1300 MHz RNSS allocation** |
| EU 863–870, US 902–928, AS923 917–925, E220 850.125–930.125 MHz | none for n = 2–5 | 2nd harmonics 1700–1860 MHz fall between L1 and nothing |

With exact band edges: **E22 channels 0–3 put the 3rd harmonic into the GPS L2 band and channels 5–6 into GLONASS L2 — both tracked by the ZED-F9P** (CH 4 is marginal at the G2 edge; CH 7–9, 1251–1257 MHz, are clear of the signals but still close to the F9P's L2-block front-end filter skirts — avoid them too). The default CH 23 and CH 24 are clean for L1/L2/L5 receivers; CH 24 is the cleanest for any receiver. **Use CH 24 (434.125 MHz); use CH 23 only with BW ≤ 125 kHz** (the whole channel, $f_c \pm BW/2$, must lie inside 433.05–434.79 MHz: CH 23 at 250 kHz spans 433.000–433.250 MHz, below the band edge; at 125 kHz it starts at 433.0625 MHz, only just inside).

*How much harmonic suppression would an in-band harmonic need?* With +33 dBm conducted, 25 dB antenna-to-antenna coupling at 1.2 GHz (estimate) and a ≈ −98 dBm narrowband tracking-loss level, the 3rd harmonic must be ≤ −106 dBc. EBYTE does not publish harmonic levels for the E22-400T33D (its user manual has no spurious specification [9]); a vendor page for the similar E22-400T30D-V2 claims spurious ≤ −60 dBc [10] — ≈ **45 dB short**. A low-pass filter after the module (≥ 45–50 dB rejection at 1.2–1.25 GHz with < 0.5 dB loss at 433 MHz, e.g. a 7th-order Chebyshev or a commercial LTCC 433 MHz LPF — [filter parts](../18-components-parts/filter-parts-saw-ceramic-ltcc.md)) could close it, but **channel selection is free and complete**: stay on CH 23/24.

*Intermodulation* products $|m|+|n| \le 5$ between E22, E220 and 2.4 GHz Wi-Fi/BLE channels:

| Product | Example | Lands in | Generated where |
|---|---|---|---|
| 2.4 GHz − 868 MHz (2nd order) | 2442 − 868.125 = 1573.9 MHz | L1/E1 | GNSS LNA (both signals present) |
| 2.4 GHz − 2 × 433 MHz (3rd order) | 2442 − 2 × 433.125 = 1575.75 MHz | L1 C/A main lobe | GNSS LNA |
| Wi-Fi ch 6 − 2 × 434.125 MHz (3rd order; E22 CH 24, the KB default channel) | 2437 − 868.25 = 1568.75 MHz; the ±11 MHz Wi-Fi channel spreads it over ≈ 1558–1580 MHz | **GPS L1** (covers the C/A main lobe 1574.4–1576.4 MHz) and E1/B1C | GNSS LNA |
| Wi-Fi ch 11 − 2 × 434.125 MHz (3rd order) | 2462 − 868.25 = 1593.75 MHz; spread ≈ 1583–1605 MHz | **GLONASS G1** (1597.5–1605.9 MHz); misses the GPS L1 C/A main lobe | GNSS LNA |
| 2.4 GHz − 915 MHz | 2480 − 915.125 = 1564.9 MHz | E1/B1C | GNSS LNA |
| 4 × 915 − 2.4 GHz (5th order) | 4 × 915.125 − 2437 = 1223.5 MHz | F9P L2 band | GNSS front end (weak) |
| 433 + 915, 2 × 915 − 433, 3 × 433 + … | 1348, 1397 MHz … | no GNSS band | — |

The two CH 24 rows (finding from W5-E7, checked in `tools/verify/s13_gnss_ephemeris.py` §7) are a **frequency check only**: the level of the product was not computed for them. It depends on the isolation of each path and on the LNA's IIP3, as in Example 3 below. Moving the LoRa link to CH 24 therefore does not remove the Wi-Fi intermod problem; it only moves the product. Only switching the Wi-Fi off in flight removes it, or a SAW ahead of the LNA reduces it.

**Clock harmonics.** A square-ish clock of frequency $f_{clk}$ has harmonics at $nf_{clk}$ falling roughly as 1/n (then faster above the edge-rate corner); at n ≈ 40–200 they are weak, but the GNSS signal is weaker still and near-field coupling from a trace or crystal to the antenna or RF line is easily −120 dBm. Hits found by the script include 25 MHz (×63 → 1575.000, 0.42 MHz from L1), 8 MHz (×197 → 1576.0), 12 MHz (×131 → 1572), 16/32/48 MHz (×n → 1568/1584, inside E1/B1C ±12 MHz), 24/26/40/120 MHz (→ 1560, inside B1I), 16/40/50/64/80 MHz (→ 1600, inside GLONASS G1), 40/48/50/240/600 MHz (→ 1200, E5b/B2I). A narrowband CW harmonic hurts most when it coincides with one of the C/A code's spectral lines (1 kHz spacing); receivers' CW-suppression filters (u-blox reports `cwSuppression` in MON-RF [3]) notch it.

### Level 3 — spoofing, authentication, adaptive antennas, jamming at altitude
**Spoofing taxonomy.** (1) *Meaconing* — re-broadcasting the real signal with delay (moves the solution to the re-radiator's antenna, delays time). (2) *Simulator spoofing* — transmitting synthetic signals (gps-sdr-sim class) starting from a different position/time; a cold-starting receiver simply believes it. (3) *Receiver–spoofer* — a spoofer that tracks the real signals, aligns its fake signals in code and carrier with them, raises its power and then drags the receiver off — the hardest to detect.

**Detection metrics**: absolute C/N₀ too high and too uniform across satellites (all at the same power from one transmitter); AGC gain dropping while C/N₀ rises (more power in band); sudden position/time jumps or clock-drift steps; inconsistency between constellations or frequencies (a single-system spoofer); signal angle-of-arrival all identical (needs antenna arrays or rotating antennas); disagreement with an IMU or barometer. u-blox evaluates "implausible changes or inconsistencies", needs multiple constellations for best results and cannot detect spoofing present from start-up [2].

**Authentication.** Galileo OSNMA (Open Service Navigation Message Authentication) appends TESLA-chain MACs to I/NAV so a receiver can verify the navigation data came from Galileo; it authenticates *data*, not signal timing, so meaconing remains possible. The ZED-F9P manual documents OSNMA support (§3.14.5) [2].

**Adaptive antennas** (CRPA, null steering) suppress jammers spatially by 20–40+ dB; note that receivers "specially designed to employ anti-jam features (e.g., null steering antenna)" for airborne use fall under EAR 7A105.b.3 and antenna arrays with adaptive nulls under USML XI(c)(10) — export-controlled [5].

**Jamming at altitude.** A rocket's radio horizon to ground emitters is ≈ $\sqrt{2kR_eh}$ (k = 4/3): ≈ 650 km at 25 km altitude. DLR observed L1 jamming on sounding rockets from northern Scandinavia above ≈ 25 km since 2022: L1 C/N₀ dropped ≈ 5 dB at onset and 4–5 dB more later, GPS L1 C/A tracking was lost immediately, L2C/L5 and BeiDou were less affected, and a multi-frequency multi-constellation receiver kept navigating [6]. The spectrogram showed 1–2 MHz-wide power on 1561.10 and 1575.42 MHz and broadband power across GLONASS G1 — classic multi-band jammers [6].

## Design equations & rules of thumb

| Rule | Value | Source |
|---|---|---|
| Wideband in-band J that breaks tracking (45 → 28 dB-Hz) | ≈ −95 dBm at antenna | script, [4] |
| Spur at GNSS frequency from an on-board TX | must be ≪ −100 dBm at GNSS input | derived |
| MAX-M10S immunity | −15 dBm (433), −17 (915), −18 (2.44 GHz); −35 at 525/787 MHz | [1] |
| Isolation for 2 W at 433 MHz (M10S) | ≈ 48 dB | script |
| Antenna-to-antenna isolation achievable | 15–20 dB typical, 6–10 dB tiny devices | [1] |
| F9P active antenna out-of-band rejection | ≥ 40 dB (antenna spec) | [antennas page] |
| E22 channels to avoid (F9P L2/G2) | CH 0–9 (410.125–419.125 MHz); use CH 24 (CH 23 only at BW ≤ 125 kHz: Singapore band edge) | script |
| Harmonic suppression needed if in-band | ≈ 106 dBc (vs ≈ 60 dBc typical) | script |
| Avoid co-active Wi-Fi/BLE with 433/868 MHz TX near GNSS | IM2/IM3 → L1 | script |

## Worked examples
**1 — Avionics-C: MAX-M10S next to a 1 W E220 at 915 MHz.** Required: 30 dBm − (−17 dBm) = 47 dB. Suppose the antennas are 30 cm apart (≈ 25 dB coupling, estimate) and the GNSS patch rejects 915 MHz by ≈ 15 dB (mismatch + pattern; estimate): 40 dB → 7 dB short. Add a SAW (e.g. ≥ 30 dB rejection at 915 MHz) in front of RF_IN — the "SAW–notch–LNA–SAW" arrangement u-blox recommends [1] — and measure C/N₀ with the transmitter keyed continuously on the bench ([antennas page example 5](../08-antennas/gnss-antennas.md#worked-examples)).

**2 — Choosing the Avionics-B E22 channel.** The ZED-F9P's second band covers 1223–1231 MHz (L2C) and 1242–1249 MHz (G2) [antennas page band table]. E22 CH 0–3 (410.125–413.125 MHz) and CH 5–6 (415.125–416.125 MHz) put the 2 W transmitter's 3rd harmonic at 1230.4–1239.4 and 1245.4–1248.4 MHz. At an assumed −60 dBc (−27 dBm) with 25 dB coupling, that is −52 dBm at the GNSS antenna — ≈ 45 dB above the ≈ −98 dBm tracking-loss level. Use **CH 24 (434.125 MHz)**, or CH 23 (433.125 MHz) only with BW ≤ 125 kHz, so that the whole LoRa channel stays inside the Singapore 433.05–434.79 MHz SRD band ([Singapore rules](../19-regulations-safety/singapore-imda-rules.md); at 250 kHz CH 23's lower edge is 433.000 MHz) — and verify with a spectrum analyser that the module's harmonics and broadband noise near 1.2 and 1.57 GHz are below the analyser floor at the GNSS antenna position.

**3 — An ESP32 with Wi-Fi on during flight.** Wi-Fi channel 7 (2442 MHz) at +20 dBm and the E22 at +33 dBm both reach the GNSS LNA. Assume 40 dB of total isolation/rejection for 433 MHz and 35 dB for 2.4 GHz (estimates): −7 dBm and −15 dBm at the LNA input. The third-order product 2442 − 2 × 433.125 = 1575.75 MHz (0.33 MHz from L1), referred to the input with an LNA IIP3 of ≈ −5 dBm (typical of small GNSS LNAs — [LNA parts](../18-components-parts/lna-pa-gain-block-mmics.md)): $P_{IM3} = 2P_{433} + P_{2.4} - 2\,IIP3 = -14 - 15 + 10 = -19$ dBm — 76 dB above the −95 dBm tracking-loss level (and the LNA is near compression anyway). Even with 20 dB more isolation on both paths: −54 − 35 + 10 = −79 dBm, still 16 dB too much. Conclusion: **never let Wi-Fi/BLE and the 433 MHz transmitter run simultaneously near the GNSS antenna** (or near an LNA without a SAW in front) — turn the ESP32 radio off in flight.

**4 — A cheap MCU board with a 25 MHz Ethernet/USB crystal.** Its 63rd harmonic sits 0.42 MHz from L1. With the GNSS patch 5 cm above the board, a few µW of 25 MHz edge energy couples at maybe −120 to −110 dBm at 1575 MHz — enough to cost several dB of C/N₀ on L1 (J/S of −10 to 0 dB for a CW line coinciding with a C/A spectral line is significant for that satellite). Shield/spread-spectrum the clock, move the antenna, or pick crystal frequencies whose harmonics miss the bands (the script prints the full table for common frequencies).

## Practical notes
- **Measure, don't guess**: (1) log `MON-RF` (AGC, cwSuppression, noisePerMS) and `NAV-SAT` C/N₀ with every transmitter and the flight computer running in each mode; (2) use u-center's spectrum view (`MON-SPAN`) [1]; (3) sniff the RF line with an SDR/spectrum analyser through a DC block (beware the active antenna bias).
- **Board design**: GNSS antenna and RF line far from MCU, SD card, switching regulators, displays and their clocks; ground fences and shield cans (30–40 dB practical); filter I/O lines; avoid clock frequencies with in-band harmonics or use spread-spectrum clocking ([EMC](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md), [shielding](../13-pcb-rf-layout-emc/shielding-and-isolation.md)).
- **Transmitters**: add a low-pass/harmonic filter after the PA if the module allows; keep LoRa antennas at the opposite end of the vehicle; transmit with gaps (TDMA) if GNSS performance during bursts matters.
- **Pulsed interferers**: high-peak, low-duty bursts (GSM-like, LoRa packets) can do damage disproportionate to their average power (u-blox caution) [2].
- **Legality**: GNSS jammers are illegal to use (and generally to sell/possess) in Singapore, the US and the EU; GNSS repeaters need specific authorization. Conducted testing only.
- **Specifying a GNSS preselector that also notches Iridium** (one printed zero gives only ≈ 15 dB at 1616 MHz): [06 RF filters § Example 7](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md#example-7--specifying-a-gnss-preselector-that-also-notches-iridium). On-board coexistence with Wi-Fi (the third-order product of Wi-Fi channel 6 and the 434 MHz downlink lands on GPS L1) is in [06 co-site § Example 4](../06-rf-circuits/co-site-interference-and-transmitter-intermod.md#example-4--esp32-wi-fi-and-gps-on-one-avionics-bay).

## Common mistakes & misconceptions
- **"A SAW filter fixes interference."** Only out-of-band interference; in-band spurs pass straight through.
- **"433 MHz is nowhere near 1575 MHz."** Its 3rd harmonic is near L2/E6, and it can mix with 2.4 GHz into L1.
- **"Low duty cycle = harmless."** Pulsed blockers can saturate the LNA/AGC each burst.
- **"My receiver would tell me if it were spoofed."** Only if it saw the transition; a spoofer present at power-up is invisible to u-blox's detector [2].
- **"Turning the transmitter down to 'legal' levels makes it compatible."** Regulatory spurious limits (−30 dBm above 1 GHz) are ~65 dB too high for a GNSS receiver centimetres away.

## How to simulate / verify
- `python3 tools/verify/gnss_self_interference.py` — clock-harmonic and radio-harmonic/IM tables vs GNSS passbands, J/S tolerance, jammer distances, M10S isolation budget. ALL PASS.
- Bench: GNSS simulator or live sky + the transmitter at full power into its antenna; plot C/N₀ vs TX on/off; sweep E22 channels.
- RF: measure transmitter harmonics with a spectrum analyser and a directional coupler/attenuator; measure antenna isolation (S21) with a VNA on a mock-up (u-blox procedure) [1].

## Open questions / gaps
- E22-400T33D / E220-900T30D harmonic and spurious levels are not published; must be measured.
- No source found on GNSS interference incidents around Singapore/Southeast Asia; not researched.
- The ZED-F9P's out-of-band immunity curve (equivalent of the M10S Figure 27) was not found in its integration manual.

## Sources
1. u-blox, *MAX-M10S Integration manual*, UBX-20053088 R05 — §4.3 RF front-end (DC block, LTE B13 notch, LNA, SAW; external SAW recommendation), §4.3.1 LNA modes, §4.3.2 out-of-band immunity (Fig. 27, Table 43), §4.3.3 antenna isolation and VNA measurement, spectrum analyser note. https://content.u-blox.com/sites/default/files/MAX-M10S_IntegrationManual_UBX-20053088.pdf (manufacturer)
2. u-blox, *ZED-F9P Integration manual*, UBX-18010802 R16 — §3.14 spoofing/jamming detection (SEC-SIG, SEC-SIGLOG, JAMDET sensitivity), OSNMA §3.14.5, §4.6 EMI on I/O lines, in-band/out-of-band mitigation, pulsed-interference caution. https://content.u-blox.com/sites/default/files/ZED-F9P_IntegrationManual_UBX-18010802.pdf (manufacturer)
3. u-blox, *u-blox F9 HPG 1.32 Interface Description*, UBX-22008968 — UBX-MON-RF fields (jammingState deprecated, agcCnt, cwSuppression, noisePerMS, antStatus). https://content.u-blox.com/sites/default/files/documents/u-blox-F9-HPG-1.32_InterfaceDescription_UBX-22008968.pdf (manufacturer)
4. E. D. Kaplan, C. J. Hegarty (eds.), *Understanding GPS/GNSS*, 3rd ed., Artech House, 2017 — ch. 9 (interference: equivalent C/N₀, spectral separation coefficients, J/S tolerance), spoofing. (textbook)
5. J. Y. Kim, U.S. Office of Space Commerce, "U.S. Export Controls on GPS/GNSS Equipment," 2022 — EAR 7A105.b.3 anti-jam, USML XI(c)(10) adaptive antennas. https://www.space.commerce.gov/wp-content/uploads/2022-03-US-export-controls-GPS-GNSS-equipment.pdf (government summary)
6. B. Braun et al., "First Test of a Multi-Constellation, Multi-Frequency GNSS Receiver on Board a Sounding Rocket," *Eng. Proc.* 126:39, 2026 — jamming above 25 km, C/N₀ drops, spectrogram. https://doi.org/10.3390/engproc2026126039 (conference, open access)
7. u-blox, *MAX-M10S Data sheet*, UBX-20035208 R08 — anti-jamming/anti-spoofing feature list, RF_IN 0 dBm. https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf (manufacturer)
8. Space Bar avionics knowledge base (user's notes) — E22-400T33D 2 W 433 MHz (primary), E220-900T30D 1 W 900 MHz (secondary), ESP32-S3, Teensy 4.1. (internal)
9. EBYTE, *E22-400T33D/T33S User Manual* v1.5 — frequency = 410.125 + CH × 1 MHz, CH 0–83 (410.125–493.125 MHz), default 433.125 MHz; no harmonic/spurious specification. https://robu.in/wp-content/uploads/2024/07/E22-400T33X_UserManual_EN_v1.5-1.pdf (manufacturer manual, distributor mirror)
10. EBYTE product page, E22-400T30D-V2 — "spurious emissions ≤ −60 dBc" (via search summary; different variant). https://ebyteiot.com/products/sx1268-433mhz-lora-rf-module-ebyte-e22-400t30d-wireless-transmitter-receiver-uart-dip-30dbm-1w-8km-long-range-sma-k-antenna (vendor — unverified)
