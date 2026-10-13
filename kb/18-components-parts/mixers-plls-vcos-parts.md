---
title: Mixers, IQ modulators/demodulators, PLL synthesizers, VCOs, clock generators, TCXOs and DDS — part selection guide
domain: 18-components-parts
slug: mixers-plls-vcos-parts
tags: [mixer, ade-1, adex-10l, sym-25dhw, ltc5562, adl5801, adl5350, iq-modulator, adl5375, trf3705, iq-demodulator, adl5380, adl5387, pll, adf4351, adf4371, adf4159, lmx2594, lmx2572, lmx2491, lmx2571, lmx2820, max2870, max2871, hmc830, hmc833, si5351, ms5351m, si5341, lmk04828, cdce913, lmk61e2, tcxo, dds, ad9850, ad9833, ad9910, fmcw]
prerequisites:
  - ../07-noise-linearity/phase-noise-and-jitter.md
  - ../05-analog-electronics/oscillators.md
  - ../04-real-components-hf/crystals-and-resonators.md
related:
  - ../14-sdr-dsp/iq-complex-baseband.md
  - ../05-analog-electronics/data-converters-adc-dac.md
  - ../11-radar/detection-theory-cfar.md
  - rf-transceiver-ics.md
  - phased-array-and-radar-parts.md
  - adcs-dacs-for-sdr.md
  - lna-pa-gain-block-mmics.md
level: intermediate
confidence: medium
last_updated: 2026-10-13
---

# Mixers, IQ modulators/demodulators, PLLs, VCOs, clocks, TCXOs and DDS — part selection guide

## Questions this page answers
- Which synthesizer should I use as the LO for a home-made 433 MHz / 2.4 GHz / 5.8 GHz / 24 GHz radio or radar?
- Which PLL can generate FMCW chirps (ramps) by itself?
- Is the ADF4351 board from AliExpress good enough, and why does its spectrum look dirty?
- Should I use a passive diode mixer (ADE-1) or an active Gilbert-cell mixer (ADL5801, LTC5562)?
- What IQ modulator/demodulator gives me a direct-conversion transmitter or receiver without an AD9361?
- Si5351 vs a "real" clock chip: how much jitter can my ADC clock tolerate?
- Which TCXO part numbers work with SX126x/AT86RF215/CC1200 and are in LCSC stock?
- When is a DDS (AD9850/AD9910) better than a PLL?

## TL;DR
- **Wideband PLL+VCO, sub-6 GHz, cheap**: **ADF4351** (35 MHz–4.4 GHz; VCO 2.2–4.4 GHz with ÷1…÷64) [2]; **MAX2870/MAX2871** (23.5 MHz–6 GHz; VCOs 3–6 GHz, ÷1…÷128) [2]; **LMX2572** (12.5 MHz–6.4 GHz, 75 mA, FOM −232 dBc/Hz, ramp/chirp + direct FSK) [3]; **HMC833** (to 6 GHz) / HMC830 (to 3 GHz) [1]. LCSC stock is best for LMX2572 (996 pcs, ~US$9.6) and MAX2871 (977, ~US$9.5) [1].
- **Microwave**: **LMX2594** (10 MHz–15 GHz, −110 dBc/Hz @ 100 kHz at 15 GHz, 45 fs jitter, FOM −236, 2-segment ramp generator) [4]; **LMX2820** (45 MHz–22.6 GHz, 36 fs, 2.5 µs VCO cal) [5]; **ADF4371** (62.5 MHz–32 GHz via doubler/quadrupler) [2].
- **FMCW chirp PLLs (external VCO)**: **ADF4159** (13 GHz PFD input, sawtooth/triangle/parabolic ramps, 110 MHz PFD, 25-bit modulus) [6]; **LMX2491** (500 MHz–6.4 GHz, 8-segment piecewise-linear ramps, 200 MHz PFD, −227 dBc/Hz normalised) [7]. These are the parts behind most 5.8/10/24 GHz DIY radars (see [phased-array & radar parts](phased-array-and-radar-parts.md)).
- **Narrowband low-noise synth for UHF radios**: **LMX2571** (10–1344 MHz, −123 dBc/Hz @ 12.5 kHz and −145 dBc/Hz @ 1 MHz at 480 MHz, 39 mA, built-in 2/4/8-level FSK and a TX/RX output switch; C440388, ~US$3.8) [8].
- **Mixers**: passive diode rings for linearity and simplicity — ADE-1+ (0.5–500 MHz, 5 dB loss, IIP3 +15 dBm, LO +7 dBm), ADEX-10L+ (10–1000 MHz, LO +4 dBm, 7.2 dB), SYM-25DHW+ (80–2500 MHz, LO +17 dBm, IP3 +30 dBm) [9]; active — ADL5801 (10 MHz–6 GHz, 1.8 dB gain, IIP3 +28.5 dBm), LTC5562 (to 7 GHz, 2×2 mm, 3.3 V), ADL5350 (to 4 GHz, 2.7–3.5 V) [1]. The classic **SA612/NE602** Gilbert cell is not in LCSC stock and marketplace units are often clones.
- **IQ modulator / demodulator**: ADL5375 (0.4–6 GHz, noise floor −160.5 dBm/Hz), **TRF3705** (0.3–4 GHz, OIP3 +30 dBm, −160 dBm/Hz, 3.3 V) [10]; ADL5380 (0.4–6 GHz, IIP3 +30 dBm), ADL5387 (30 MHz–2 GHz) [1].
- **Clocks**: **Si5351A** (2.5 kHz–200 MHz, 3 outputs, I²C, MSOP-10, ~US$1.06, 70 ps p-p jitter) fine for LOs of simple receivers and MCU clocks, not for high-IF ADC sampling [11]; **MS5351M** is a pin-compatible clone (~8 mA more current, reaches ~300 MHz in tests) [12]. Low-jitter: **Si5341** (90 fs), **LMK04828** (88 fs, JESD204B), **LMK61E2** (90 fs programmable XO), CDCE913/925 (cheap EEPROM clock, ±150 ppm VCXO pull) [1][13].
- **TCXOs in LCSC stock**: 32 MHz ±1.5 ppm KDS 1XXD32000MBA (C253694, 13k pcs, ~US$0.74) for SX126x; 26 MHz ±0.5 ppm Huaxin 2T026000VY (C19725361) or KDS 1XXD26000MAA ±1.5 ppm (C135223) for AT86RF215/GNSS; 40 MHz ±0.5 ppm HCI 8132S (C19674261) for CC1200/CC1125; 10 MHz TCXOs for GPSDO/SDR references [1].
- **DDS**: AD9850 (125 MHz clock, 32-bit tuning word, 0.0291 Hz steps, ~US$18), AD9833 (25 MHz clock, 10-bit, ~US$7.6), **AD9910** (1 GS/s, 14-bit, to 400 MHz, sweep engine, ~US$83) [14]. Use a DDS for fast, phase-continuous, fine-resolution hopping/chirps at HF–VHF, or as a PLL reference.

## Intuition (no math)
A **mixer** multiplies two signals so their frequencies add and subtract; it moves your signal between RF and IF/baseband. **Passive** mixers (diode rings, FET switches) are driven hard by the LO, have loss (5–8 dB) and excellent linearity; **active** (Gilbert-cell) mixers have gain, need less LO, and use more supply current. An **IQ modulator/demodulator** is two mixers driven by LOs 90° apart, which lets you shape any modulation in software ([IQ & complex baseband](../14-sdr-dsp/iq-complex-baseband.md)).

A **PLL synthesizer** makes a clean, programmable frequency by locking a noisy VCO to a stable reference crystal. Inside the loop bandwidth the output inherits the reference and phase-detector noise (scaled up by the multiplication factor N); outside it the VCO's own noise dominates. A **fractional-N** PLL can step in tiny increments but creates spurs near integer multiples of the reference ("integer-boundary spurs"). A **ramp/chirp generator** inside the PLL changes N linearly with time — exactly the linear frequency sweep an FMCW radar needs.

A **DDS** builds the waveform numerically (phase accumulator → sine table → DAC). It hops instantly with sub-Hz resolution but its output is limited to < 0.4 × clock and has images and spurs from the DAC.

The **reference oscillator** (crystal, TCXO, OCXO, GPSDO) sets frequency accuracy and close-in phase noise of everything downstream ([crystals & resonators](../04-real-components-hf/crystals-and-resonators.md)).

## The math — how synthesizer specs map to system performance
### Level 1 — in-band phase noise from the PLL figure of merit
Datasheets quote a normalised PLL noise floor or figure of merit $FOM$ (dBc/Hz). The flat in-band phase noise at the output is approximately
$$\mathcal{L}_{in\text{-}band} \approx FOM + 10\log_{10}f_{PD} + 20\log_{10}N,\qquad N = f_{out}/f_{PD}$$
(plus a 1/f term near the carrier). Check: LMX2594 with $FOM=-236$, $f_{PD}$ = 100 MHz, $f_{out}$ = 10 GHz → −116 dBc/Hz; scaling to 15 GHz (+3.5 dB) gives −112.5 dBc/Hz, consistent with the −110 dBc/Hz @ 100 kHz datasheet headline [4]. High phase-detector frequency and low N are the levers ([phase noise & jitter](../07-noise-linearity/phase-noise-and-jitter.md)).

### Level 2 — reciprocal mixing sets the LO phase-noise requirement
A blocker of power $P_B$ at offset $\Delta f$ mixes with LO phase noise into your channel of bandwidth $B$: $P_{noise} \approx P_B + \mathcal{L}(\Delta f) + 10\log_{10}B$. To keep this below the thermal floor $-174 + 10\log_{10}B + NF$:
$$\mathcal{L}(\Delta f) < -174 + NF - P_B$$
(the bandwidth cancels). Example: NF 6 dB, blocker −40 dBm at 1 MHz → $\mathcal{L}(1\text{ MHz}) < -128$ dBc/Hz. LMX2571 (−145 dBc/Hz @ 1 MHz at 480 MHz) passes with 17 dB margin [8].

### Level 3 — clock jitter and ADC SNR; FMCW parameters
Sampling a sine at $f_{in}$ with rms jitter $\sigma_t$ limits SNR to $SNR_{jitter} = -20\log_{10}(2\pi f_{in}\sigma_t)$ ([data converters](../05-analog-electronics/data-converters-adc-dac.md)): 10 ps rms at 100 MHz → 44 dB (≈ 7 bits); 1 ps → 64 dB; 100 fs → 84 dB. For FMCW with sweep bandwidth $B$ over chirp time $T$: range resolution $\Delta R = c/(2B)$ and beat frequency $f_b = 2RB/(cT)$ — 150 MHz (5.725–5.875 GHz) gives 1.0 m, 250 MHz (24.0–24.25 GHz) gives 0.6 m; a 100 m target with $B$ = 150 MHz and $T$ = 1 ms beats at 100 kHz. Ramp **linearity** and **settling** matter as much as phase noise: non-linear sweeps smear the range FFT.

## Design equations & rules of thumb
| Rule | When valid | Typical values |
|---|---|---|
| $\mathcal{L}_{in} ≈ FOM + 10\log f_{PD} + 20\log N$ | inside loop BW, above 1/f corner | −232 FOM, 32 MHz PFD, 433 MHz → −134 dBc/Hz |
| $\mathcal{L}(\Delta f) < -174 + NF - P_B$ | reciprocal-mixing budget | −128 dBc/Hz @ 1 MHz for a −40 dBm blocker |
| $SNR_{jitter}=-20\log(2\pi f\sigma_t)$ | ADC clock | 1 ps @ 100 MHz → 64 dB |
| Diode mixer IIP3 ≈ LO power + 5…10 dB | level-7/17 diode rings | ADE-1 (L7): +15 dBm; SYM-25DHW (L17): +30 dBm |
| DDS resolution $= f_{clk}/2^{32}$; usable output < 0.4 $f_{clk}$ | 32-bit accumulators | AD9850 0.029 Hz; AD9910 0.23 Hz |
| TCXO error at RF $= f\cdot\Delta_{ppm}$ | frequency budget | 915 MHz × 2.5 ppm = 2.3 kHz; × 0.5 ppm = 458 Hz |
| Loop bandwidth ≈ $f_{PD}/10$…$/20$ max | charge-pump PLL stability | use the vendor loop-filter tool (ADIsimPLL, TI PLLatinum Sim) |

## Comparison tables (LCSC data: 2026-04 snapshot [1]; US$ qty 1)
### A. PLL synthesizers with integrated VCO
| Part | Output range | Noise headline | Features | Supply / package | LCSC / stock / US$ |
|---|---|---|---|---|---|
| **ADI ADF4351** | 35 MHz–4.4 GHz (VCO 2.2–4.4 GHz, ÷1…64) | — (see DS) | frac/int-N, 2 outputs, mute | 3.3 V, LFCSP-32 5×5 | C71362 / 296 / 14.40 [2] |
| ADI ADF4350 | 137.5 MHz–4.4 GHz (unverified lower edge) | | predecessor of ADF4351 | LFCSP-32 | C98705 / 1.3k / 9.20 |
| **Maxim MAX2871** (MAX2870) | 23.5 MHz–6 GHz (VCOs 3–6 GHz, ÷1…128) | | frac/int-N, 2 outputs | 3.3 V, TQFN-32 5×5 | C7458627 / 977 / 9.45 [2] |
| **TI LMX2572** | 12.5 MHz–6.4 GHz | −106 dBc/Hz @ 100 kHz at 6.4 GHz; FOM −232 | ramp/chirp, direct digital FSK, phase sync, 75 mA | 3.3 V, VQFN-40 6×6 | C2665711 / 996 / 9.58 [3] |
| TI LMX2571 | 10–1344 MHz | −123 dBc/Hz @ 12.5 kHz, −145 @ 1 MHz (480 MHz); FOM −231 | 2/4/8-level or arbitrary FSK, TX/RX switch, 39 mA | 3.3 V, QFN-36 6×6 | C440388 / 365 / 3.77 [8] |
| ADI HMC830 / HMC833 | 25 MHz–3 GHz / 25 MHz–6 GHz | 180 fs jitter (listing) | frac-N | 3.3/5 V, 6×6 QFN-40 | C461530 / 175 / 9.65; C514408 / 191 / 14.82 [1] |
| ADI ADF4360-7 | to 1.8 GHz (band set by external L) | | integer-N, older | LFCSP-24 | C654698 / 385 / 6.65 |
| **TI LMX2594** | 10 MHz–15 GHz | −110 dBc/Hz @ 100 kHz at 15 GHz; 45 fs (7.5 GHz); FOM −236 | 2-segment ramp, SYSREF, <20 µs VCO cal, +7 dBm at 15 GHz | 3.3 V, VQFN-40 6×6 | C2862572 / 11 / 23.14 [4] |
| TI LMX2595 | to 19 GHz (unverified) | | LMX2594 sibling | VQFN-40 | C5215036 / 20 / 54.68 |
| TI LMX2820 | 45 MHz–22.6 GHz | 36 fs (12 kHz–95 MHz) at 6 GHz; FOM −236 | 2.5 µs VCO cal, mute pin, external VCO input | VQFN-48 7×7 | C5215031 / 85 / 78.35 [5] |
| ADI ADF4371 | 62.5 MHz–32 GHz (VCO 4–8 GHz, ×2, ×4 outputs) | | frac/int-N | LGA | not in snapshot [2] |

### B. PLLs without VCO (external VCO/VCXO) — ramp and reference-cleaning parts
| Part | Input range | Ramp | Key spec | Package | LCSC / stock / US$ |
|---|---|---|---|---|---|
| **ADI ADF4159** | to 13 GHz | sawtooth, triangle, parabolic; ramp + FSK; fast/slow | PFD ≤ 110 MHz; 25-bit modulus; −224 dBc/Hz normalised floor | LFCSP-24 4×4 | C459155 / 11 / 9.36 [6] |
| **TI LMX2491** | 500 MHz–6.4 GHz | up to 8 piecewise-linear segments; FSK/PSK pin | PFD ≤ 200 MHz; −227 dBc/Hz normalised; 3.15–5.25 V charge pump | WQFN-24 4×4 | C2651213 / 51 / 8.27 [7] |
| TI LMX2492 | to 14 GHz (unverified) | as LMX2491 | | WQFN-24 | C2664080 / 24 / 20.03 |
| ADI ADF4002 | to 400 MHz | — | integer-N; cleans a VCXO onto a 10 MHz GPS reference | LFCSP-20 | C207536 / 219 / 8.76 |
| ADI ADF4001 | to 200 MHz (unverified) | — | TSSOP-16, hand-solderable | TSSOP-16 | C654567 / 102 / 5.88 |

### C. Mixers
| Part | Type | RF/LO range | Conv. gain / loss | IIP3 | LO drive / supply | Package | LCSC / stock / US$ |
|---|---|---|---|---|---|---|---|
| **Mini-Circuits ADE-1+** | diode ring (level 7) | 0.5–500 MHz | −5.0 dB | +15 dBm; P1dB +1 dBm; L-R 55 dB | +7 dBm LO | SMD-6 7.9×5.6 | C2942210 / 196 / 5.82 [9] |
| Mini-Circuits ADEX-10L+ | diode (level 4) | 10–1000 MHz (usable to 1.5 GHz) | −7.2 dB | — ; L-R 60 dB | +4 dBm LO | SMD-6 | C118997 / 1.1k / 5.71 [9] |
| Mini-Circuits SYM-25DHW+ | diode (level 17) | 80–2500 MHz | −6.4 dB | +30 dBm; P1dB +14 dBm | +17 dBm LO | SMD | not in snapshot [9] |
| Mini-Circuits ADE-2+, ADE-42MH+ | diode | 5 MHz–1 GHz; 5 MHz–4.2 GHz | ~−6.5 / ~−7 dB | | L7 / L13 (unverified) | SMD-6 | C3176642 / 57 / 6.44; C2683459 / 27 / 17.44 |
| **ADI ADL5801** | active, double-balanced | 10 MHz–6 GHz | +1.8 dB | +28.5 dBm; NF 9.75 dB | 5 V, 130 mA | LFCSP-24 4×4 | C496495 / 327 / 13.93 [1] |
| ADI ADL5350 | active, single-ended | RF 0.5–2 GHz (listing: 30–380 MHz IF) | | +25 dBm | 2.7–3.5 V, 19 mA | DFN-8 2×3 | C206667 / 2.7k / 5.38 [1] |
| ADI LTC5562 | active, 2×2 mm | LO 0–7 GHz | +1 dB | +21 dBm; NF 13.5 dB | 3.3 V | QFN-10 2×2 | C688676 / 124 / 11.82 [1] |
| ADI LTC5567 | active downconverter | 0.3–4 GHz | +1.9 dB | +26.9 dBm | 3.3 V | QFN-16 | C688684 / 483 / 5.08 |
| ADI LT5560 | active, low power | to ~4 GHz (unverified) | +2.4 dB | +9.3 dBm | 2.7–5.3 V, 13 mA | DFN-8 3×3 | C462645 / 186 / 5.52 |
| Maxim MAX2682 | SiGe downconverter | RF/LO 0.4–2.5 GHz, IF 10–500 MHz | +14.7 dB | +3.2 dBm; NF 6.5 dB | 2.7–5.5 V, 15 mA | SOT-23-6 | C242518 / 39 / 3.00 [1] |
| ADI HMC219B / HMC787A / HMC525A | GaAs passive | 2.5–7 / 3–10 / 4–8.5 GHz | ~−8 dB | +18…+24 dBm | +11…+17 dBm LO | MSOP-8 / QFN | C1526031 / 53 / 13.49; C662745 / 21 / 31.94; C662356 / 41 / 62.06 |
| NXP SA612A (NE602) | Gilbert cell + oscillator | to ~500 MHz | 17 dB typ. (14 dB min), NF 5.0 dB at 45 MHz | IIP3 −13 dBm (dynamic table; text says −15 typ.) | 4.5–8 V, 2.4 mA | SO-8 | not in snapshot | HF/VHF classic; clone risk; data sheet Rev. 3 read by W5-S14 — see [06 baluns § SA612](../06-rf-circuits/baluns-and-rf-transformers.md#balun-practicalities-footprints-dots-placement-and-the-sa612) |

### D. IQ modulators and demodulators
| Part | Function | Range | Key spec | Supply | Package | LCSC / stock / US$ |
|---|---|---|---|---|---|---|
| **TI TRF3705** | IQ modulator | 300 MHz–4 GHz | OIP3 +30 dBm @ 1850 MHz; noise floor −160 dBm/Hz; unadjusted carrier −40 dBm, sideband −45 dBc | 3.3 V | VQFN-24 | not in snapshot [10] |
| ADI ADL5375 | IQ modulator | 400 MHz–6 GHz | noise floor −160.5 dBm/Hz; P1dB +10 dBm | 5 V | QFN-24 4×4 | C579150 / 78 / 13.78 [1] |
| ADI ADL5380 | IQ demodulator | 400 MHz–6 GHz | IIP3 +30 dBm; gain 6.9 dB; 245 mA | 5 V | QFN-24 4×4 | C579152 / 22 / 15.00 [1] |
| ADI ADL5387 | IQ demodulator | 30 MHz–2 GHz | IIP3 +32.8 dBm; 180 mA | 5 V | QFN-24 4×4 | C579155 / 24 / 11.63 [1] |
| ADI ADL5382 | IQ demodulator | 700 MHz–2.7 GHz (unverified) | | 5 V | QFN-24 | C579153 / 10 / 17.69 |
| ADI LTC5594 / LTC5585 | wideband IQ demod | 300 MHz–9 GHz / 0.7–3 GHz (unverified) | | | QFN | not in snapshot |

### E. Clock generators, jitter cleaners and programmable oscillators
| Part | Outputs / range | Jitter | Notes | Package | LCSC / stock / US$ |
|---|---|---|---|---|---|
| **SiLabs/Skyworks Si5351A** | 3 outputs, 2.5 kHz–200 MHz (8 kHz–160 MHz in early DS) | 70 ps p-p (listing) | I²C, 25/27 MHz XTAL, integer/fractional dividers; ham-radio LO favourite | MSOP-10 | C504891 / 13.8k / 1.06 [11] |
| Hangzhou Ruimeng MS5351M | Si5351A clone, 3 outputs | 60 ps p-p (listing) | pin-compatible, ~8 mA more current, reaches ~300 MHz in QRP-Labs tests | MSOP-10 | C1509083 / 1.2k / 0.82 [12] |
| TI CDCE913 / CDCE925 | 3 / 5 outputs ≤ 230 MHz | — | EEPROM, 8–32 MHz crystal, on-chip VCXO ±150 ppm pull | TSSOP-14/16 | C553157 / 95 / 3.62 (Q1); C544467 / 1.9k / 4.36 [13] |
| SiLabs Si5341 / Si5340 | 10 / 4 outputs ≤ 350 MHz (listing) | 90 fs | multi-input, hitless switching, DSPLL | QFN-64 / QFN-44 | C1519876 / 29 / 25.39; C1519877 / 13 / 21.25 [1] |
| TI LMK04828 | 14 device clocks ≤ 3.1 GHz, 7 SYSREF | 88 fs (12 kHz–20 MHz) | dual-loop, JESD204B | WQFN-64 9×9 | C478068 / 174 / 20.66 [13] |
| TI LMK61E2 | programmable XO ≤ 1 GHz (LVPECL) | 90 fs | ±50 ppm total, I²C EEPROM, PSRR −70 dBc | QFM-6 5×7 | C2666995 / 30 / 12.07 [13] |
| TI LMK03328 | 8 outputs | (unverified) | dual PLL, EEPROM | WQFN-48 | C544831 / 126 / 8.61 |
| ADI HMC7044 | 14 outputs to 3.2 GHz (unverified) | ~40–50 fs (unverified) | JESD204B/C | LFCSP-68 | C514403 / 208 / 36.29 |

### F. TCXOs for radios (LCSC stock; "clipped sine" outputs need a DC-block into most radios)
| Frequency | Use | Part (LCSC) | Stability / package / supply | Stock / US$ |
|---|---|---|---|---|
| 32 MHz | SX126x / LLCC68 / LR11xx (via DIO3), SX1280 (52 MHz — check) | KDS **1XXD32000MBA** (C253694) | ±1.5 ppm, 2016, 3.3 V, 2 mA | 13k / 0.74 |
| 32 MHz | same, 1.8 V TCXO supply from DIO3 | HCI 8121S-32.000NN18DTL (C19674249) | ±1 ppm, clipped sine, 2016-6P, 1.8 V | 460 / 1.42 |
| 26 MHz | AT86RF215, GNSS modules, MAX2769 (16.368 MHz typical there) | Huaxin 2T026000VY (C19725361); KDS 1XXD26000MAA (C135223) | ±0.5 / ±1.5 ppm, 2520 / 2016, 1.8–3.3 V | 2.7k / 0.35; 17.9k / 0.40 |
| 40 MHz | CC1200 / CC1125 / Si446x at 30 MHz (check) | HCI 8132S-40.000NQ33FTL (C19674261) | ±0.5 ppm, 3225, 3.3 V | 1.7k / 1.51 |
| 38.4 MHz | Nordic/EFR32/cellular | Epson TG2016SMN 38.4 MHz (C1987359) | ±0.5 ppm, 2016 | 2.6k / 0.46 |
| 10 MHz | SDR/PLL reference, GPSDO VCXO | HCI 8132S-10.000NQ33DTL (C19674256) ±0.5 ppm; KDS 1XTV10000MDA (C253701) ±1.5 ppm | 3225, 3.3 V | 159 / 2.45; 822 / 0.97 |
Stability figures are the LCSC listing values (usually over −30/−40…+85 °C); confirm the datasheet's definition (initial vs over temperature vs aging) — see [crystals & resonators](../04-real-components-hf/crystals-and-resonators.md) for the LoRa frequency budget.

### G. DDS
| Part | Clock | DAC | Output | Features | Package | LCSC / stock / US$ |
|---|---|---|---|---|---|---|
| ADI AD9833 / AD9837 | 25 / 16 MHz | 10-bit | to ~10 MHz | sine/triangle/square, SPI, 12 mW-class | MSOP-10 / LFCSP-10 | C9652 / 3.0k / 7.57; C138562 / 730 / 5.76 |
| ADI AD9834 | 75 MHz | 10-bit | to ~30 MHz | FSK/PSK pins | TSSOP-20 | C116589 / 1.2k / 9.42 |
| **ADI AD9850** | 125 MHz | 10-bit + comparator | to ~40 MHz practical (Nyquist 62.5) | 32-bit FTW, 0.0291 Hz steps, 23 M updates/s [14] | SSOP-28 | C480623 / 98 / 17.81 |
| ADI AD9851 | 180 MHz (×6 REFCLK) | 10-bit | to ~70 MHz | | SSOP-28 | C408275 / 172 / 39.84 |
| ADI AD9954 | 400 MS/s | 14-bit | to ~160 MHz | linear sweep, RAM | TQFP-48 | C496484 / 1.05k / 18.99 |
| **ADI AD9910** | 1 GS/s | 14-bit | to 400 MHz | sweep engine, RAM, 32-bit FTW (0.23 Hz), integrated PLL [14] | TQFP-100 | C578893 / 34 / 83.31 |
| ADI AD9959 / AD9912 | 500 MS/s ×4 ch / 1 GS/s 48-bit | 10 / 14-bit | | 4-channel phase-coherent (AD9959) | LFCSP | C653947 / 9 / 61.10; C33095 / 35 / 49.32 |

## Worked examples
### 1. LO for a 433 MHz receiver with a −40 dBm blocker 1 MHz away
Requirement from Level 2: $\mathcal{L}(1\text{ MHz}) < -128$ dBc/Hz (NF 6 dB). Candidates: LMX2571 −145 dBc/Hz @ 1 MHz at 480 MHz [8] → 17 dB margin; LMX2572 in-band estimate with 32 MHz PFD: $-232 + 75.1 + 22.6 = -134$ dBc/Hz (in-band floor; the far-out VCO noise at 1 MHz must be read from the datasheet plot). An Si5351-derived LO has no guaranteed phase-noise specification — adequate for a hobby HF receiver, risky next to a pad transmitter.

### 2. A 5.8 GHz FMCW radar chirp
Band 5.725–5.875 GHz (150 MHz; check Singapore SRD rules) → $\Delta R$ = 1.0 m. Architecture: LMX2572 in ramp mode (12.5 MHz–6.4 GHz, integrated VCO) directly, or LMX2491 + external 5.8 GHz VCO for a cleaner sweep [3][7]. Chirp 1 ms, target at 100 m → $f_b$ = 100 kHz: an audio-class ADC or codec suffices ([adcs-dacs-for-sdr](adcs-dacs-for-sdr.md)). For 24 GHz, the ADF4159 drives the ADF5901's VCO (divided feedback) — see [phased-array & radar parts](phased-array-and-radar-parts.md).

### 3. Can the Si5351 clock an ADC digitising a 21.4 MHz IF?
Assume the 70 ps peak-to-peak jitter corresponds to roughly 10 ps rms (Gaussian ≈ p-p/7; an assumption) → $SNR = -20\log_{10}(2\pi\cdot21.4\times10^6\cdot10^{-11}) \approx 57$ dB ≈ 9.2 bits: acceptable for an 8–10-bit SDR ADC, wasteful for a 14-bit LTC2208 ([adcs-dacs-for-sdr](adcs-dacs-for-sdr.md)). For 100 MHz inputs with 14-bit converters use Si5341/LMK61E2/LMK04828-class clocks (≤ 100 fs → ≥ 84 dB).

### 4. Why an AliExpress ADF4351 board looks "dirty"
The ADF4351 generates frequencies below 2.2 GHz by dividing the VCO; its outputs are square-ish (strong odd harmonics), fractional-N spurs appear near integer boundaries, and cheap boards often use a 25 MHz crystal oscillator with poor phase noise and a minimal loop filter. Remedies: a clean TCXO reference, a loop filter designed with ADIsimPLL for your PFD/charge-pump settings, integer-N mode where the channel plan allows, a low-pass filter on the output, and avoiding frequencies near $k\cdot f_{PD}$ (forum reports; anecdotal).

## Practical notes
- **Loop filter & simulation**: use the vendor tools (TI PLLatinum Sim, ADIsimPLL) — they model VCO, reference and charge-pump noise and give component values; copy the EVM loop filter if your PFD and charge-pump current match.
- **Reference quality dominates close-in noise**: a clean 10–100 MHz TCXO/OCXO (or GPS-disciplined oscillator) is worth more than a better PLL. Clipped-sine TCXOs need AC coupling; CMOS TCXOs can drive MCU clocks too.
- **VCO calibration**: integrated-VCO PLLs recalibrate on every frequency change (LMX2594 < 20 µs, LMX2820 2.5 µs [4][5]); budget this in hopping/chirp schedules.
- **Output drive & harmonics**: most PLL outputs are differential CML/LVPECL-like; use a balun or take one side with the other terminated; add a low-pass filter for LO harmonics before a mixer ([filter parts](filter-parts-saw-ceramic-ltcc.md), [baluns](../06-rf-circuits/baluns-and-rf-transformers.md)).
- **Diode mixer LO drive**: a level-7 mixer needs +7 dBm of clean LO — a PLL output (+0…+7 dBm) often needs a gain block (GALI/ERA, [LNA/gain-block parts](lna-pa-gain-block-mmics.md)) and a 3–6 dB pad to present a good termination.
- **Packages**: QFN-24…40 at 0.5 mm pitch; AD9910 TQFP-100 with exposed pad (hand-solderable with care); LMX2820/ADF4371 LGA-style packages need JLC assembly.
- **Supply noise**: VCO and charge-pump supplies need low-noise LDOs (the LMX parts integrate some regulation); switcher ripple shows up as spurs at the switching frequency offsets ([power supplies for RF](../05-analog-electronics/power-supplies-for-rf-and-analog.md)).

## Recommended picks for Marcus's use cases
| Use case | Pick | Why |
|---|---|---|
| Programmable LO / signal source 35 MHz–6 GHz for bench tests | MAX2871 or ADF4351 board with a TCXO; LMX2572 for new PCBs | cheap, well documented |
| FMCW radar chirp ≤ 6.4 GHz | LMX2572 (integrated VCO) or LMX2491 + VCO | on-chip ramp generation |
| FMCW 24 GHz | ADF4159 + ADF5901/ADF5904 chipset | reference design exists |
| Microwave LO to 15/22 GHz | LMX2594 / LMX2820 | lowest jitter, ramp support |
| UHF narrowband FSK transmitter without a transceiver IC | LMX2571 (direct FSK) + PA | built-in FSK and T/R switch |
| Clock for SDR ADC (≥ 12-bit, ≥ 50 MHz IF) | LMK61E2 / Si5341 / LMK04828 | ≤ 100 fs |
| MCU/radio clocks, simple receiver LO | Si5351A (or MS5351M) | US$1, 3 outputs |
| Radio TCXOs | KDS 1XXD32000MBA (32 MHz), Huaxin 2T026000VY (26 MHz), HCI 8132S (40 MHz) | LCSC stock, ≤ ±1.5 ppm |
| HF–VHF agile source, test chirps | AD9850 (cheap) / AD9910 (serious) | sub-Hz steps, instant hops |

## Parts to avoid (or use knowingly)
- **Si5351 for ADC clocks above a few MHz input** — jitter-limited SNR (example 3).
- **ADF4351 boards as-is** for anything spectrally sensitive — spurs/harmonics; clean them up or use MAX2871/LMX2572 on your own PCB.
- **SA612/NE602 from marketplaces** — clone risk and not stocked by LCSC; for new designs use ADL5801/LTC5562-class active mixers or ADE-series diode mixers.
- **HMC-series GaAs mixers/PLLs above US$30** for a first radar — start with ADF4159/ADF5901 or a TI mmWave SoC ([radar parts](phased-array-and-radar-parts.md)).
- **"Ultra-stable" TCXOs with no datasheet** from marketplace listings — the ppm figure often excludes temperature range or aging.

## Common mistakes & misconceptions
- *"A 32-bit fractional-N PLL gives me spur-free 1 Hz steps."* Fractional spurs and integer-boundary spurs exist; many parts include spur-mitigation modes, but plan the channel grid.
- *"Phase noise at 100 kHz is the only number."* Reciprocal mixing depends on the offset of your *blockers*; radar needs the close-in noise at the beat-frequency offsets; ADC clocks need integrated jitter.
- *"Passive mixers are noisy because they have loss."* A passive mixer's NF ≈ its conversion loss; place gain before it and it is rarely the limit, while its linearity is excellent.
- *"DDS output is clean to Nyquist."* Images at $f_{clk}\pm f_{out}$ and sinc roll-off require a reconstruction filter; usable output is ≈ 40 % of the clock.
- *"TCXO ±0.5 ppm means my LoRa link needs no AFC."* Add aging (±1 ppm/year typical class), soldering shift, and Doppler ([LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)).

## How to simulate / verify
```python
import math
L_inband = lambda fom, fpd, fout: fom + 10*math.log10(fpd) + 20*math.log10(fout/fpd)
print(L_inband(-236, 100e6, 10e9), L_inband(-232, 32e6, 433e6))     # -116, -134 dBc/Hz
recip_req = lambda nf, pblock: -174 + nf - pblock                    # dBc/Hz
print(recip_req(6, -40))                                             # -128
snr_jit = lambda f, sig: -20*math.log10(2*math.pi*f*sig)
print(snr_jit(21.4e6, 10e-12), snr_jit(100e6, 100e-15))              # ~57 dB, 84 dB
c = 3e8; print(c/(2*150e6), 2*100*150e6/(c*1e-3))                    # 1.0 m, 100 kHz
```
- Phase noise: measure with a spectrum analyser (noise-marker method) or an SDR with a clean reference ([17-test-measurement](../17-test-measurement/phase-noise-measurement.md), planned).
- Loop-filter design: ADIsimPLL (ADF/HMC/MAX parts), TI PLLatinum Sim (LMX parts).

## Open questions / gaps
- ADI part specs (ADF4351 phase noise, MAX2871 noise, HMC830/833, LTC5594, ADF4371 packaging) were taken from search extracts and LCSC listings, not re-read from the datasheets (ADI site unreachable to scripts).
- Si5351 rms jitter/phase noise is not specified by the vendor in a form usable for the jitter formula; the 10 ps rms assumption in example 3 is illustrative.
- SA612A lifecycle status unverified.

## Sources
1. Local JLCPCB/LCSC parts database (jlcparts in-stock snapshot, newest record 2026-04-01) via `jlc-trawler`, and LCSC product-page parametrics (fetched 2026-09-29). (distributor data)
2. Analog Devices product pages/datasheets — ADF4351 (Rev A), ADF4371, MAX2870 — via search extracts: https://www.analog.com/en/products/adf4351.html, https://www.analog.com/en/products/adf4371.html, https://www.analog.com/en/products/MAX2870.html. (datasheet, secondary extract)
3. Texas Instruments, *LMX2572 6.4-GHz low-power wideband RF synthesizer* datasheet SNAS740B (2019), https://www.ti.com/lit/ds/symlink/lmx2572.pdf, p. 1. (datasheet)
4. Texas Instruments, *LMX2594 15-GHz wideband PLLatinum RF synthesizer* datasheet SNAS696C, https://www.ti.com/lit/ds/symlink/lmx2594.pdf, p. 1. (datasheet)
5. Texas Instruments, *LMX2820 22.6-GHz wideband PLLatinum RF synthesizer* datasheet, https://www.ti.com/lit/ds/symlink/lmx2820.pdf, p. 1. (datasheet)
6. Analog Devices, *ADF4159 Direct Modulation/Fast Waveform Generating 13 GHz Fractional-N Frequency Synthesizer* datasheet, https://www.analog.com/media/en/technical-documentation/data-sheets/adf4159.pdf (features via search extract). (datasheet, secondary extract)
7. Texas Instruments, *LMX2491 6.4-GHz low-noise RF PLL with ramp/chirp generation* datasheet SNAS711A, https://www.ti.com/lit/ds/symlink/lmx2491.pdf, p. 1. (datasheet)
8. Texas Instruments, *LMX2571 low-power, high-performance PLLatinum RF synthesizer with FSK modulation* datasheet, https://www.ti.com/lit/ds/symlink/lmx2571.pdf, p. 1. (datasheet)
9. Mini-Circuits datasheets ADE-1+, ADEX-10L+, SYM-25DHW+, https://www.minicircuits.com/pdfs/ADE-1+.pdf etc. (fetched 2026-09-27). (datasheet)
10. Texas Instruments, *TRF3705 300-MHz to 4-GHz quadrature modulator* datasheet SLWS223B, https://www.ti.com/lit/ds/symlink/trf3705.pdf, p. 1. (datasheet)
11. Silicon Labs, *Si5351A/B/C-B* datasheet Rev 1.3 (2020), mirror https://download.mikroe.com/documents/datasheets/Si5351-datasheet.pdf (range change 8 kHz–160 MHz → 2.5 kHz–200 MHz via search extract). (datasheet, secondary extract)
12. QRP Labs, *MS5351M performance*, https://qrp-labs.com/synth/ms5351m.html; xiaolaba, *MS5351_Si5351_testing*, https://github.com/xiaolaba/MS5351_Si5351_testing. (hobbyist measurement — anecdotal but quantitative)
13. Texas Instruments datasheets: LMK04828 (SNAS605AS), CDCE913 (SCAS849I, 2024), LMK61E2 (SNAS674C), https://www.ti.com/lit/ds/symlink/<part>.pdf, p. 1. (datasheet)
14. Analog Devices, *AD9850 CMOS 125 MHz complete DDS synthesizer* (Rev H) and *AD9910 1 GSPS 14-bit DDS* (Rev E) datasheets — features via search extract: https://www.analog.com/media/en/technical-documentation/data-sheets/AD9850.pdf, https://www.analog.com/media/en/technical-documentation/data-sheets/AD9910.pdf. (datasheet, secondary extract)
15. This KB: [Phase noise and jitter](../07-noise-linearity/phase-noise-and-jitter.md), [Oscillators](../05-analog-electronics/oscillators.md), [Crystals and resonators](../04-real-components-hf/crystals-and-resonators.md). (internal)
