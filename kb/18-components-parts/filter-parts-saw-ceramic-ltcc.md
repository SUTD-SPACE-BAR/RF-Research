---
title: Filter parts — SAW, LTCC/ceramic, chip low-pass, baluns-with-filter, cavity and lumped filters for 433/868/915 MHz, GNSS and 2.4 GHz (selection guide)
domain: 18-components-parts
slug: filter-parts-saw-ceramic-ltcc
tags: [filter, saw, ltcc, ceramic, b39431b3710u410, b39871b3744h110, b39921b3728u410, saffb1g56kb0f0ar1x, ta1575ig, lfcn-490, lfcn-1000, lfcn-1575, lfcg-900, hfcn, bfcn-1560, dea160960lt, 0915lp15b026e, lfl21902, balf-spi2, harmonic-filter, cavity-filter, gnss, lcsc]
prerequisites:
  - ../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md
  - ../01-circuit-theory/passive-filter-design-prototypes.md
related:
  - ../07-noise-linearity/dynamic-range-sfdr-blocking.md
  - ../15-lora-ism-radios/ground-station-design.md
  - ../15-lora-ism-radios/ism-band-plans-duty-cycle.md
  - ../08-antennas/gnss-antennas.md
  - ../04-real-components-hf/inductors-at-rf.md
  - ../04-real-components-hf/capacitors-at-rf-mlcc.md
  - lna-pa-gain-block-mmics.md
  - rf-transceiver-ics.md
level: intermediate
confidence: medium
last_updated: 2026-10-13
---

# Filter parts — SAW, LTCC/ceramic, chip low-pass, cavity and lumped (selection guide)

## Questions this page answers
- Which SAW filter do I put in front of my 433 / 868 / 915 MHz receiver or my GNSS LNA, and which are in LCSC stock?
- Which low-pass filter kills the harmonics of a 1 W PA well enough to be legal?
- Are Mini-Circuits LTCC filters (LFCN/HFCN/BFCN) worth US$2–5 when a TDK chip filter costs US$0.07?
- Can I put a SAW filter after my PA?
- When should I buy a cavity or helical filter for the ground station instead of a SAW?
- When is designing my own LC filter better than any off-the-shelf part?

## TL;DR
- **What matters**: passband insertion loss (adds directly to NF if before the LNA), bandwidth vs your legal band, rejection at the specific interferers/harmonics you care about (not just "40 dB"), power handling (SAW: receive-level only; LTCC: watts), in/out impedance (50 Ω single-ended vs balanced), temperature drift (SAW ≈ tens of ppm/°C), package and footprint. Theory: [RF filters — technologies](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md), [LC prototypes](../01-circuit-theory/passive-filter-design-prototypes.md).
- **ISM SAWs in LCSC stock (2026-04 snapshot)**: **433.92 MHz** Qualcomm/RF360 **B39431B3710U410** (IL 2 dB, ~1.7 MHz BW, 3×3 mm, 9k pcs, ~US$0.98, C2649317); **868.3 MHz** B39871B3744H110 (IL 3 dB, C2650980, 8.7k pcs, ~US$1.29); **915 MHz** B39921B3728U410 (IL 2.2 dB, 26 MHz BW, C2650953, ~US$1.92), TST TA0281A (915 MHz, 26 MHz, 2.2 dB, C596627, ~US$0.93), B39921B2671P810 (1.9 dB, 1.1×0.9 mm), Abracon AFS14A26-915 (3.1 dB) [1].
- **GNSS L1 SAWs**: Murata **SAFFB1G56KB0F0AR1X** (1575.42 MHz, IL 1.6 dB, 88k in stock at ~US$0.06, C91647); TST TA1575IG (2 dB, 3×3 mm); multi-constellation TST TA1267E (1588.655 MHz, 34.47 MHz BW — GPS + GLONASS) [1].
- **Harmonic low-pass filters (TX side, watts OK)**: Mini-Circuits **LFCN-490+** (DC–490 MHz, IL ≤ 1.2 dB, 40 dB typ. rejection 880–2500 MHz, 8.5 W) for **433 MHz**; **LFCN-1000+** (DC–1000 MHz, IL ≤ 1.0 dB, only **30 dB** typ. at 1900–5000 MHz, 10 W) for 868/915; LFCN-1575+ for GNSS-band TX; LFCG-900+ (0805, DC–850 MHz, 50 dB typ., 4.5 W) [2]. Cheap chip LPFs: TDK DEA160960LT-5059A1 (698–960 MHz, IL 0.28 dB, 23.6 dB, US$0.07), Johanson 0915LP15B026E (IL 0.5 dB, 30 dB), Murata LFL21902MTC1A018 (902.5 MHz, 0.6 dB, 30 dB) [1].
- **Neither LTCC nor chip LPFs alone give the 44 dB at 2f a +30 dBm FEM with −22 dBc 2nd harmonic needs** (SE2435L example) — a 7-pole LC Chebyshev (fc ≈ 1.05 GHz) gives ≈ 48 dB at 1830 MHz in theory; real parts reach 40–60 dB depending on Q/SRF and layout.
- **Baluns with integrated filter for chip radios**: ST BALF-SPI2-02D3 (433 MHz, 2.2 dB) and -01D3 (860–930 MHz, 1.6 dB) for S2-LP/SPIRIT; many chip vendors have matching IPDs [1].
- **Ground-station preselectors**: cavity/helical filters (< 1 dB loss, high power, big) beat SAWs (2–3 dB) when the filter must precede the LNA and blockers are strong ([ground station design](../15-lora-ism-radios/ground-station-design.md)).

## Intuition (no math)
- **SAW** (surface acoustic wave): the RF is converted to a sound wave on a piezoelectric crystal and back; the interdigital finger geometry makes a sharp, narrow filter in a 1–3 mm package. Steep skirts, 1.5–3 dB loss, small power handling, fixed centre frequency set at the factory. The standard "clean up the receiver input" part.
- **LTCC / ceramic multilayer**: tiny inductors and capacitors buried in a fired ceramic stack — really a lumped LC filter in a chip. Low loss, handles watts, gentle skirts; ideal for harmonic low-pass filters and wide band-pass filters (2.4 GHz). Mini-Circuits LTCC parts come with full S-parameter data; TDK/Murata/Walsin chip parts are cheaper handset parts with less published data.
- **Ceramic coaxial / dielectric resonator** filters: quarter-wave resonators in high-εr ceramic blocks — lower loss than SAW at similar selectivity, larger.
- **Cavity / helical** filters: metal resonators; lowest loss and highest power, big and expensive; ground-station and repeater use.
- **Your own LC or microstrip filter**: cheapest and fully custom, performance limited by component Q/SRF and layout.

## The math — what the numbers mean for your system
### Level 1 — loss before the LNA is noise figure
A filter with passband loss $L$ at temperature $T_0$ has $NF = L$ ([Friis](../07-noise-linearity/noise-figure-and-friis.md)). A 2 dB SAW in front of a 1 dB LNA gives ≈ 3 dB; the same SAW after an LNA with 18 dB gain costs ≈ 0.05 dB. The trade-off is blocker protection (see [LNA parts](lna-pa-gain-block-mmics.md) worked examples).

### Level 2 — required rejection
At an interferer or harmonic of power $P_{int}$ that must be reduced to $P_{max}$ (e.g. an LNA's safe input, or a regulatory spurious limit):
$$R_{req} = P_{int} - P_{max} + \text{margin}\quad[\text{dB}]$$
For a PA harmonic: $P_{int} = P_{out} - (\text{harmonic dBc})$. Example: +30 dBm with −22 dBc 2nd harmonic and a −36 dBm limit → $R_{req}$ = 44 dB (+ margin).

### Level 3 — prototype attenuation of an LC low-pass
An $n$-pole Chebyshev low-pass with passband ripple $r$ dB ($\varepsilon^2=10^{r/10}-1$) attenuates, at normalised frequency $x=f/f_c>1$,
$$A(x) = 10\log_{10}\left[1+\varepsilon^2\cosh^2(n\,\mathrm{arccosh}\,x)\right]$$
(lossless components; real stopband is limited by capacitor ESL/inductor SRF and layout coupling). 7-pole, 0.1 dB ripple: $f_c$ = 500 MHz → 47.5 dB at 868 MHz, 75.6 dB at 1302 MHz; $f_c$ = 1050 MHz → 47.8 dB at 1830 MHz (computed; see script). Component selection: [inductors at RF](../04-real-components-hf/inductors-at-rf.md), [MLCCs at RF](../04-real-components-hf/capacitors-at-rf-mlcc.md).

## Design equations & rules of thumb
| Rule | When valid | Typical values |
|---|---|---|
| Filter IL before LNA adds to NF dB-for-dB | passive, room temperature | SAW 1.6–3 dB; LTCC LPF 0.3–1.2 dB; cavity 0.3–1 dB |
| $R_{req}=P_{out}-\text{dBc}_{2f}-P_{limit}$ + margin | TX harmonic filtering | +30 dBm, −22 dBc, −36 dBm → 44 dB |
| LTCC stopband specs start well above $f_c$ | Mini-Circuits LFCN | LFCN-1000+: 30 dB only from 1900 MHz [2] |
| SAW ≈ receive-level only | most ISM/GNSS SAWs | keep input ≲ +10 dBm unless the datasheet says otherwise (unverified typical) |
| SAW centre drifts with temperature | quartz/LiTaO₃ SAW | −20…−40 ppm/°C class (typ.; check datasheet) → ±50 °C ≈ 1–2 MHz at 915 MHz |
| Balanced ports must be matched per datasheet | SAW with 100/200 Ω balanced outputs | use the recommended matching network |

## Comparison tables (LCSC data: 2026-04 snapshot [1]; US$ qty 1)
### A. SAW filters for ISM bands
| Band | Part | Centre / BW | IL | Rejection (listing) | Package | LCSC / stock / US$ | Notes |
|---|---|---|---|---|---|---|---|
| 433.92 MHz | **Qualcomm (RF360/TDK) B39431B3710U410** | 433.92 MHz / ~1.7 MHz | 2 dB | 33–60 dB (points) | 3×3 mm, 6-pad | C2649317 / 9.0k / 0.98 | BW ≈ the whole 433.05–434.79 MHz SRD band |
| ~440 MHz | TST TA0411A | 440 MHz | 2.8 dB | 56–57 dB | 5×5 mm | C692400 / 1.0k / 1.49 | check passband vs 433 MHz |
| 868.3 MHz | **Qualcomm B39871B3744H110** | 868.3 MHz | 3 dB | 10 dB (listing incomplete) | 3×3 mm | C2650980 / 8.7k / 1.29 | EU SRD 868 |
| 915 MHz | **Qualcomm B39921B3728U410** | 915 MHz / 26 MHz | 2.2 dB | 22–53 dB | 3×3 mm | C2650953 / 131 / 1.92 | 902–928 MHz; covers SG 920–925 |
| 915 MHz | TST TA0281A | 915 MHz / 26 MHz | 2.2 dB | — | 3×3 mm | C596627 / 634 / 0.93 | cheaper second source |
| 914.5 MHz | TST TA1163A | 914.5 MHz | 3 dB | 20–46 dB | 3×3 mm | C596645 / 2.6k / 1.33 | |
| 915 MHz | Qualcomm B39921B2671P810 | 915 MHz | 1.9 dB | 26–44 dB | 1.1×0.9 mm | C3283551 / 15 / 1.59 | tiny, machine-only |
| 915 MHz | Abracon AFS14A26-915.00-T3 | 915 MHz / 26 MHz | 3.1 dB | 36–53 dB | 1.4×1.1 mm | C2650957 / 79 / 0.81 | |
| 2.4 GHz | Qualcomm B39242B8328P810, B39242B4360P810 | 2.442 GHz | 2.1–2.5 dB | | 1.4×1.1 / 1.1×0.9 | C7218430 / 69 / 1.33 | for 2.4 GHz coexistence |
"Rejection (listing)" is the set of attenuation numbers LCSC publishes at unspecified offsets — read the datasheet's frequency table before relying on them.

### B. GNSS SAW filters (L1 ~1559–1610 MHz)
| Part | Centre / BW | IL | Rejection | Package | LCSC / stock / US$ |
|---|---|---|---|---|---|
| **Murata SAFFB1G56KB0F0AR1X** | 1575.42 MHz | 1.6 dB | 35 dB (listing) | 1.1×0.9 mm class | C91647 / 88k / 0.058 |
| TST TA1575IG | 1575.42 MHz | 2 dB | 30 dB | 3×3 mm | C498206 / 902 / 1.10 |
| HCI SF33M6-1575.420 | 1575.42 MHz | | | 3×3 mm | C19186002 / 268 / 0.81 |
| TST TA1267E / TA1267A | 1588.655 MHz / 34.47 MHz (≈ 1571–1606 MHz: GPS/Galileo + GLONASS) | 2.5 dB | 34–37 dB | 1.4×1.1 mm | C18221406 / 2.9k / 0.34 |
| TST TA0676A | 1592.5 MHz / 43 MHz | 2.6 dB | | 3×3 mm | C596624 / 1.4k / 1.24 |
| TST TA1500A | 1590.155 MHz / 31.47 MHz | 1.3 dB | | 1.4×1.1 mm | C2961683 / 2.9k / 0.19 |
BeiDou B1I (1561.098 MHz) needs a filter whose passband extends down to ~1559 MHz — check before using a 1588/1592 MHz-centred part. Dual-band (L1+L5) receivers need a second path or a diplexer ([GNSS antennas](../08-antennas/gnss-antennas.md)).

### C. Low-pass (harmonic) filters for transmitters
| Part | Passband | IL | Stopband | Power | Package | LCSC / stock / US$ |
|---|---|---|---|---|---|---|
| **Mini-Circuits LFCN-490+** | DC–490 MHz (f₃dB 650 MHz) | ≤ 1.2 dB | 40 dB typ. 880–2500 MHz | 8.5 W | 1206 (3.2×1.6 mm) | C3008205 / 172 / 3.07 [2] |
| Mini-Circuits LFCN-400+ | DC–400 MHz (f₃dB 560 MHz) | ≤ 1.0 dB | 40 dB typ. 680–3000 MHz | 8.5 W | 1206 | C879882 / 366 / 2.97 [2] — 433 MHz is *above* its specified passband |
| **Mini-Circuits LFCN-1000+** | DC–1000 MHz (f₃dB 1300 MHz) | ≤ 1.0 dB | **30 dB** typ. 1900–5000 MHz | 10 W | 1206 | C879868 / 1.7k / 2.07 [2] |
| Mini-Circuits LFCN-1200+ / 1400+ | DC–1200 / 1400 MHz | ~1 dB | | | 1206 | C879869 / 579 / 2.56; C879889 / 191 / 3.15 |
| Mini-Circuits LFCN-1575+ | DC–1575 MHz (f₃dB 1875 MHz) | ≤ 1.0 dB | 30 dB typ. 2225–6800 MHz | 10 W | 1206 | C4989723 / 8 / 4.36 [2] |
| Mini-Circuits LFCG-900+ | DC–850 MHz | 1.3 dB typ. | 50 dB typ., stopband to 11 GHz | 4.5 W | 0805 | C879873 / 7 / 4.63 [2] |
| Mini-Circuits LFCG-1000+ / LFCG-490+ | DC–1000 / 490 MHz class | | high rejection (G-series) | | 0805 | C4989745 / 155 / 4.54; C3034233 / 6 / 4.41 |
| TDK DEA160960LT-5059A1 | 698–960 MHz | 0.28 dB | 23.6 dB (listing) | handset PA level | 1.6×0.8 mm | C695578 / 13.9k / 0.072 |
| TDK DEA100915LT-6319A1 | 915 MHz band | 0.5 dB | 17–24.6 dB | | 1.0×0.5 mm | C415312 / 7.8k / 0.148 |
| Johanson 0915LP15B026E | 915 MHz band | 0.5 dB | 30 dB | | 2.0×1.25 mm | C2655446 / 382 / 0.45 |
| Murata LFL21902MTC1A018 | 902.5 ± 12.5 MHz | 0.6 dB | 30 dB | | 2.0×1.25 mm | C882501 / 85 / 0.47 |
| Walsin RFLPF16080G9D9T | 690–960 MHz | 0.9 dB | 20–45 dB | | 1.6×0.8 mm | C474017 / 786 / 0.061 |
| Johanson 2450LP14B100T; TDK DEA162500LT-1217A1 | 2.4–2.5 GHz | 0.35 dB (TDK) | 50 dB (TDK) | | 0603-size | C3155792 / 100 / 0.26; C76721 / 3.8k / 0.06 |

### D. Band-pass / high-pass LTCC and baluns
| Part | Type / band | IL | Notes | LCSC / stock / US$ |
|---|---|---|---|---|
| Mini-Circuits BFCN-1560+ | BPF 1500–1620 MHz | (see DS) | 30 dB typ. rejection, 1.5 W, 1206 [2] | not in snapshot |
| Mini-Circuits BFCN-2450+ | BPF 2.4 GHz | | 1206 | C4989905 / 30 / 7.30 |
| Mini-Circuits HFCN-1100+ | HPF (passband 1500–3900 MHz) | | 7 W, DC block, sub-harmonic rejection [2] | C3008196 / 61 / 3.04 |
| Mini-Circuits HFCN-1300+/2275+/3100+ | HPF | | removes LO leakage/sub-harmonics | C5757062; C4989532; C3008194 |
| Murata LFD21868MMF1D386 | BPF 868–915 MHz (LTCC) | 3.3 dB | 35 dB (listing), 2.0×1.25 mm | C910735 / 5.9k / 0.37 |
| Murata LFB152G45CB2D320 | BPF 2.4–2.5 GHz | 1.7 dB | 1.0×0.5 mm, 110k in stock | C2650940 / 110k / 0.093 |
| ST BALF-SPI2-02D3 | balun + filter, 433 MHz | 2.2 dB | matched to ST S2-LP/SPIRIT1 | C2688704 / 503 / 0.36 |
| ST BALF-SPI2-01D3 | balun + filter, 860–930 MHz | 1.6 dB | 1.6 dB amplitude, 8° phase balance | C2688705 / 10k / 0.39 |

### E. Ground-station preselectors (not PCB parts)
| Type | Typical loss / selectivity | Source | Notes |
|---|---|---|---|
| Cavity band-pass (coax connectorised) 433 / 915 MHz | 0.5–1.5 dB, 20–60 dB at ±10–30 MHz (typical ranges, unverified) | marketplace (unbranded), professional (K&L, Lorch, Mini-Circuits coaxial) | measure S21 before use; marketplace units are rarely characterised (anecdotal) |
| Helical filters | 1–3 dB | Toko-style parts (mostly obsolete), ham kits | good at 144/433 MHz |
| Coaxial SMA LTCC filters (Mini-Circuits VLF/VBF/ZX75) | 1 dB | Mini-Circuits | bench/ground use |

## Worked examples
### 1. 433 MHz, +30 dBm transmitter — which low-pass?
Assume PA 2nd harmonic −25 dBc (check your PA); limit −36 dBm (use the Singapore figure from 19-regulations): $R_{req}$ = 30 − 25 + 36 = **41 dB** at 868 MHz. LFCN-490+ guarantees 40 dB typ. only from 880 MHz [2] — 868 MHz is just outside, so expect somewhat less; it is close but not a guaranteed pass. A 7-pole 0.1 dB Chebyshev LC with $f_c$ = 500 MHz gives 47.5 dB at 868 MHz and 75.6 dB at 1302 MHz in theory (0.08 dB ripple at 434 MHz) — use it, or cascade the LFCN-490+ with a series-resonant notch at 868 MHz. Verify with a spectrum analyser.

### 2. 915 MHz, SE2435L at +30 dBm
2f = 1830 MHz at +8 dBm (−22 dBc [LNA/PA parts](lna-pa-gain-block-mmics.md)); need 44 dB. LFCN-1000+ gives 30 dB typ. only above 1900 MHz → insufficient. TDK DEA160960LT (23.6 dB) or Johanson 0915LP (30 dB) → insufficient alone. A 7-pole Chebyshev with $f_c$ = 1050 MHz gives 47.8 dB (ideal) at 1830 MHz, 75.9 dB at 2745 MHz; alternatively cascade two chip LPFs (≈ 50 dB, ~1 dB total loss). Pick high-Q 0402/0603 wire-wound or thin-film inductors with SRF > 2.5 GHz.

### 3. GNSS on a rocket with a 915 MHz +30 dBm downlink
Antenna-to-antenna coupling on a small airframe of, say, −20 dB (assumption) puts +10 dBm of 915 MHz at the GNSS antenna port. BGA524N6 in-band input P1dB is −16 dBm (data-sheet table; the feature list says −12 dBm) [LNA parts] → required rejection before the LNA ≈ 10 − (−16) + 10 dB margin = **36 dB at 915 MHz**. A GNSS SAW with 35 dB listed rejection (SAFFB1G56KB0F0AR1X) is therefore **1 dB short on its own**: add antenna separation or a second filter (e.g. a simple LC high-pass before the SAW), confirm the datasheet value *at 915 MHz* (SAW far-out rejection often degrades), and keep antennas apart. (Using the in-band P1dB for a 915 MHz blocker is conservative: the out-of-band IIP3 is −5 dBm, but no out-of-band P1dB is specified.) ([antennas on rockets](../08-antennas/antennas-on-rockets.md)).

## Practical notes
- **Footprints**: SAW land patterns are specific (ground pads, sometimes 5 or 6 pads with two grounds); copy the vendor pattern and put ground vias directly at the ground pads. Mis-grounded SAWs lose 10–20 dB of stopband.
- **Stopband leakage around the filter**: at 30–60 dB rejection, PCB coupling from input trace to output trace bypasses the filter. Keep input and output on opposite sides of the part, route with CPWG and via fences ([planar lines](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md)).
- **Balanced vs single-ended**: some SAWs have 100/150/200 Ω balanced outputs for chip radios — match per datasheet.
- **Temperature and aging**: SAWs drift in frequency with temperature; narrow SAWs (≈ 1.7 MHz at 433 MHz) can shift a band-edge channel into the skirt over a rocket's temperature range — prefer channels near centre.
- **Power**: SAW filters are for receive paths and low-level TX (after the radio, before a PA). LTCC LPFs handle watts (LFCN: 8.5–10 W [2]).
- **Data**: Mini-Circuits and Murata/TDK publish S-parameters — load them into scikit-rf/Qucs-S with your matching network ([component models](../04-real-components-hf/component-models-s2p-spice.md)).
- **Marketplace filter boards**: many are unbranded and uncharacterised; no specific documented "fake SAW" case was found in this pass, but measure S21/S11 with a VNA before trusting any unbranded filter (general caution).
- **Diplexers, ceramic IF filters (10.7 MHz, 455 kHz) and crystal filters:** design and part choice are in [06 duplexers, diplexers and crystal filters](../06-rf-circuits/duplexers-diplexers-and-crystal-filters.md#level-2--derivations).

## Recommended picks for Marcus's use cases
| Use case | Pick | Why |
|---|---|---|
| 433 MHz receiver front end (flight or ground) | B39431B3710U410 SAW | 2 dB, band-matched, 9k in stock |
| 915/923 MHz receiver front end | B39921B3728U410 (or TA0281A) | 26 MHz covers 902–928 incl. SG 920–925 |
| GNSS passive-patch front end | SAFFB1G56KB0F0AR1X (US$0.06) or TA1267E (GPS+GLONASS) | cheap, tiny |
| 433 MHz PA harmonic filter | 7-pole LC Chebyshev fc ≈ 500 MHz (or LFCN-490+ + 868 MHz notch) | LTCC spec ends at 880 MHz |
| 868/915 MHz PA harmonic filter | 7-pole LC Chebyshev fc ≈ 1.05 GHz, or 2 cascaded chip LPFs | LFCN-1000+ gives only 30 dB above 1.9 GHz |
| Ground-station preselector | cavity filter < 1 dB before the LNA | blockers on launch fields |
| 2.4 GHz coexistence | Murata LFB152G45CB2D320 | 110k stock, US$0.09 |

## Parts to avoid (or use knowingly)
- **SAW filters after a PA** — power handling far below watts.
- **LFCN-400+ for 433 MHz** — 433 MHz lies above its specified DC–400 MHz passband (loss rises toward its 560 MHz cut-off) [2].
- **Assuming "40 dB rejection" applies at your harmonic** — Mini-Circuits specify stopband ranges starting well above cut-off.
- **Unbranded cavity/SAW boards without data** for flight hardware.

## Common mistakes & misconceptions
- *"A sharper filter is always better."* Sharper = more loss and more group-delay variation; for a LoRa receiver, 2 dB of SAW loss before the LNA may cost more range than the blockers it removes.
- *"The filter defines the channel."* The radio's IF/digital filters define the channel; the RF filter only protects against strong out-of-band signals and image/harmonic responses.
- *"LTCC and SAW are interchangeable."* LTCC is a low-loss, gentle, power-tolerant LC filter; SAW is a sharp, lossier, low-power acoustic filter.
- *"Harmonic filtering is optional because the module is certified."* Only the module as certified is; adding an external PA voids that ([rf-modules](rf-modules.md), 19-regulations).

## How to simulate / verify
```python
import math
def cheb_att(n, ripple_db, x):          # ideal Chebyshev low-pass attenuation at x = f/fc
    e2 = 10**(ripple_db/10) - 1
    C = math.cosh(n*math.acosh(x)) if x >= 1 else math.cos(n*math.acos(x))
    return 10*math.log10(1 + e2*C*C)
print([round(cheb_att(7, 0.1, f/500), 1) for f in (867.8, 1301.8)])   # 433 MHz PA, fc 500 MHz
print([round(cheb_att(7, 0.1, f/1050), 1) for f in (1830, 2745)])     # 915 MHz PA, fc 1.05 GHz
req = lambda pout, dbc, limit, margin=0: pout - dbc - limit + margin   # dBm, dB below carrier (positive)
print(req(30, 22, -36), req(30, 25, -36))                              # 44, 41 dB
```
- Design the LC filter in Qucs-S/LTspice with vendor S-parameter models of the actual inductors/capacitors; then measure with a NanoVNA/LibreVNA ([17-test-measurement](../17-test-measurement/nanovna-librevna-practical.md), planned). Harmonics: spectrum analyser or a calibrated SDR with an attenuator.

## Open questions / gaps
- SAW datasheets (RF360/TST/Murata) were not read — IL/BW/rejection are from LCSC listings; the frequency points for the "rejection" figures are unknown.
- SAW power handling and temperature coefficient values are typical-class statements, not verified per part.
- No measured comparison of B39431 vs a cavity filter as a 433 MHz ground-station preselector — a useful bench test.
- Singapore spurious-emission limit to use in examples 1–2 must come from 19-regulations (−36 dBm used as a placeholder).

## Sources
1. Local JLCPCB/LCSC parts database (jlcparts in-stock snapshot, newest record 2026-04-01) via `jlc-trawler`; LCSC product-page parametrics (fetched 2026-09-29) for SAW/LTCC/chip filters and baluns. (distributor data)
2. Mini-Circuits datasheets LFCN-400+, LFCN-490+, LFCN-1000+, LFCN-1575+, LFCG-900+, HFCN-1100+, BFCN-1560+, https://www.minicircuits.com/pdfs/<model>.pdf (fetched 2026-09-27), p. 1 tables. (datasheet)
3. This KB: [RF filters — technologies and microstrip design](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md); [Passive LC filter design from low-pass prototypes](../01-circuit-theory/passive-filter-design-prototypes.md) (Chebyshev formula). (internal)
4. NanoVNA V2 forum (nanorfe.com) threads on narrowband/UHF frequency accuracy — relevant to measuring SAW filters with low-cost VNAs. (forum — anecdotal)
