---
title: ADCs, DACs and audio codecs for DIY SDRs and radars — LTC2208, AD9226, ADS42LB69, ADS4249, ADC3664, AD9680/AD9208, ADC12DJ3200, MAX19506, AD9708/AD9767, PCM1808, ADAR7251, RFSoC (selection guide)
domain: 18-components-parts
slug: adcs-dacs-for-sdr
tags: [adc, dac, sdr, radar, enob, sfdr, nsd, ltc2208, ad9226, ad9280, ad9288, ads42lb69, ads4249, adc3664, ad9680, ad9208, adc12dj3200, afe7950, max19506, ad9708, ad9767, dac5672, dac904, pcm1808, tlv320aic3204, adar7251, ad7768, rfsoc, red-pitaya, fpga, jesd204b, lvds, lcsc]
prerequisites:
  - ../05-analog-electronics/data-converters-adc-dac.md
  - ../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md
related:
  - ../14-sdr-dsp/sdr-hardware-survey.md
  - ../14-sdr-dsp/fpga-for-sdr.md
  - ../14-sdr-dsp/iq-complex-baseband.md
  - ../11-radar/fmcw-radar.md
  - ../11-radar/diy-radar-hardware.md
  - ../07-noise-linearity/dynamic-range-sfdr-blocking.md
  - mixers-plls-vcos-parts.md
  - rf-transceiver-ics.md
  - phased-array-and-radar-parts.md
level: intermediate
confidence: medium
last_updated: 2026-10-03
---

# ADCs, DACs and audio codecs for DIY SDRs and radars — selection guide

## Questions this page answers
- Which ADC should I use for a direct-sampling HF/VHF receiver, an IF-sampling SDR, or an FMCW radar's beat signal?
- How do SNR, ENOB, SFDR and noise spectral density (NSD) of a converter translate into receiver dynamic range?
- Can I use an audio codec as the ADC for a radar? When is that enough?
- What are the cheap AD9226/AD9280/AD9708 FPGA modules good for?
- When does a GSPS JESD204B converter or an RFSoC make sense, and what does it cost?
- Which of these converters are in LCSC stock, and what clock/driver do they need?

## TL;DR
- **Figures that matter**: SNR (dBFS) or NSD (dBFS/Hz) sets the noise floor; SFDR/HD2/HD3 set spur-limited dynamic range; input bandwidth sets which Nyquist zone you can undersample; clock-jitter sensitivity ($SNR_j=-20\log_{10}2\pi f_{in}\sigma_t$); interface (parallel CMOS, LVDS, JESD204B/C) sets the FPGA you need; power. Theory: [data converters](../05-analog-electronics/data-converters-adc-dac.md), [sampling](../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md).
- **HF/VHF direct sampling and IF sampling (≤ 130 MS/s)**: **LTC2208** (16-bit 130 MS/s, 78 dBFS noise floor → ENOB ≈ 12.7, 100 dB SFDR, inputs to 700 MHz, 70 fs aperture jitter) [1] — the classic high-end HPSDR-class part (not in LCSC stock); **ADC3664** (14-bit 125 MS/s dual, NSD −156.9 dBFS/Hz, SNR 77.5 dBFS, 100 mW/ch, 1.4 GHz input BW) [2]; **ADS4249** (14-bit 250 MS/s dual, 71.7 dBFS SNR / 80 dBc SFDR at 170 MHz, 560 mW total) [3]; **ADS42LB69** (16-bit 250 MS/s dual, 73.2–74.9 dBFS SNR at 170 MHz, 820 mW/ch) [4].
- **Cheap/learning**: AD9226 modules (12-bit 65 MS/s; marketplace boards ~US$13–19) [5]; AD9280 (8-bit 32 MS/s, C130297, ~US$6.6) + AD9708 (8-bit 125 MS/s DAC) pairs on Chinese FPGA add-on boards; **MAX19506** (dual 8-bit 100 MS/s, 49.8 dBFS SNR, 69 dBc SFDR, 57 mW/ch) [6]; AD9288 (dual 8-bit 80–100 MS/s, C514284, ~US$8.2).
- **GSPS / RF sampling** (needs JESD204B/C FPGA transceivers): **AD9680** (dual 14-bit up to 1.25 GS/s, signals to 2 GHz, DDCs) [7]; **AD9208** (dual 14-bit 3 GS/s, 9 GHz −3 dB BW) [7]; **ADC12DJ3200** (12-bit 6.4 GS/s single / 3.2 GS/s dual, NSD −151.8/−154.6 dBFS/Hz, 8 GHz BW) [8]; **AFE7950** (4T6R RF-sampling AFE, 12 GS/s DACs, 3 GS/s ADCs, 0.6–12 GHz) [9]. Or buy an **RFSoC 4x2** board (ZU48DR: four 5 GS/s ADCs, two 14-bit 9.85 GS/s DACs, academic US$2,499) [10].
- **DACs**: AD9767 (dual 14-bit 125 MS/s, C653820, ~US$10.4), AD9764/AD9744 (14-bit 125 MS/s), DAC904 (14-bit 165 MS/s, C2679883, ~US$5.1), **DAC5672** (dual 14-bit 275 MS/s, 84 dBc SFDR at 5 MHz, 79 dBc IMD3) [11], AD9708 (8-bit 125 MS/s).
- **Radar beat-signal / low-IF ADCs**: **ADAR7251** (4-ch 16-bit 1.8 MS/s, designed for FMCW radar; C654357, ~US$16.7), AD7768-4 (4-ch 24-bit Σ-Δ, ~US$20.7); audio codecs **PCM1808** (24-bit stereo, 99 dB SNR, C55513, 6.5k stock, ~US$0.63), TLV320AIC3204 (93 dB ADC SNR, C24109, ~US$1.60), ES7243E (~US$0.52), CS4272 (~US$3.75), AK5572 (~US$11.3) [1][12].
- **Most chips here are thin in LCSC stock or absent** (LTC2208, AD9226 bare chip, ADS42LB69, AD9680, AD9208, MAX19506 not in the snapshot) — plan on Mouser/Digikey or a finished board ([sdr-hardware survey](../14-sdr-dsp/sdr-hardware-survey.md)).

## Intuition (no math)
An SDR's ADC is the point where "radio" becomes "numbers". Two numbers matter most: how quiet it is (its noise floor per hertz) and how clean it is (how big its self-generated spurs are). A fast ADC spreads its quantisation and thermal noise over a wide band, so when you later filter down to a 125 kHz LoRa channel or a 500 Hz CW signal, most of that noise is discarded — this *processing gain* is why a "12-bit" ADC can behave like a 20-bit one in a narrow channel. Spurs, however, do not average away: a −90 dBc spur stays at −90 dBc in any bandwidth.

For an **FMCW radar** the ADC digitises the *beat* frequency (kHz–MHz), not the RF — so a high-resolution, low-rate converter (even an audio codec) is often better than a GSPS part. For **direct RF sampling**, the ADC is the receiver and must handle the full RF bandwidth, jitter and input power — expensive and power-hungry.

## The math
### Level 1 — SNR, ENOB and NSD
Ideal N-bit quantisation of a full-scale sine: $SNR = 6.02N + 1.76$ dB. Real parts: $ENOB = (SNR - 1.76)/6.02$. Noise spectral density for a Nyquist-sampled ADC:
$$NSD = -SNR - 10\log_{10}(f_s/2)\quad[\text{dBFS/Hz}]$$
LTC2208: 78 dBFS at 130 MS/s → NSD ≈ −156.1 dBFS/Hz; ADC3664 quotes −156.9 dBFS/Hz directly [2].

### Level 2 — dynamic range in your channel
In a channel of bandwidth $B$ after digital filtering: $DR_B = SNR + 10\log_{10}\!\left(\frac{f_s/2}{B}\right)$ (noise-limited), capped by SFDR for spurs. LTC2208 at 122.88 MS/s in a 500 Hz CW channel: $78 + 50.9 ≈ 129$ dB noise-limited, but a 100 dB SFDR spur still limits spur-free range to ≈ 100 dB ([dynamic range & SFDR](../07-noise-linearity/dynamic-range-sfdr-blocking.md)). To use the ADC's range you still need analog gain so that the ADC noise floor sits below the antenna noise floor, and an AGC/attenuator to avoid clipping.

### Level 3 — jitter, interface and FMCW sample rate
- **Clock jitter**: to keep $SNR_j$ ≥ 78 dB at 70 MHz input, $\sigma_t \le 10^{-78/20}/(2\pi\cdot70\times10^6) = 0.29$ ps rms — a clock-cleaner (LMK/Si534x class, [mixers/PLLs/clocks](mixers-plls-vcos-parts.md)), not an MCU PLL.
- **Data rate**: dual 14-bit at 250 MS/s = 7 Gb/s over DDR LVDS → Artix-7/ECP5-class FPGA pins; GSPS parts need JESD204B/C SERDES (Zynq UltraScale+, Kintex) ([FPGA for SDR](../14-sdr-dsp/fpga-for-sdr.md)).
- **FMCW beat frequency**: $f_b = 2RB/(cT)$. With $B$ = 250 MHz, $T$ = 1 ms, $R$ = 100 m → 167 kHz: needs a ≥ 400 kS/s ADC (ADAR7251 at 1.8 MS/s fits); an audio codec with 48 kHz Nyquist limits $R_{max}$ to 28.8 m for that chirp, or you slow the chirp to ≈ 4.2 ms to reach 100 m at 40 kHz ([FMCW radar](../11-radar/fmcw-radar.md)).

## Design equations & rules of thumb
| Rule | When valid | Typical values |
|---|---|---|
| $ENOB=(SNR-1.76)/6.02$ | any ADC | 78 dB → 12.7 bits |
| $NSD=-SNR-10\log_{10}(f_s/2)$ | Nyquist ADC | LTC2208 −156 dBFS/Hz |
| $DR_B = SNR + 10\log_{10}(f_s/2B)$ (≤ SFDR for spurs) | channelised SDR, real ADC (complex IQ at $f_s$: $f_s/B$) | 129 dB in 500 Hz |
| $\sigma_t \le 10^{-SNR/20}/(2\pi f_{in})$ | clock design | 0.29 ps for 78 dB @ 70 MHz |
| Real FMCW ADC rate ≥ 2.2 × $f_{b,max}$ | anti-alias margin | 167 kHz beat → ≥ 370 kS/s |
| Differential driver with ≥ 2× input BW, low distortion | pipelined ADCs | ADA4930/ADA4932/THS4541, or a balun + pad |
| Input full scale 1–2.5 V_pp diff ≈ +4…+10 dBm into 50–200 Ω | IF-sampling front ends | set gain so max signal ≈ −3…−6 dBFS |

## Comparison tables (LCSC data: 2026-04 snapshot [12]; US$ qty 1)
### A. ADCs for SDRs (≤ 250 MS/s)
| Part | Bits / rate / ch | SNR / SFDR (condition) | ENOB | Power | Interface | LCSC / stock / US$ |
|---|---|---|---|---|---|---|
| **ADI LTC2208** | 16 / 130 MS/s / 1 | 78 dBFS floor; 100 dB SFDR; inputs to 700 MHz [1] | 12.7 | ~1.25 W (unverified) | CMOS/LVDS | not in snapshot |
| ADI LTC2145-14 | 14 / 125 MS/s / 2 | (see DS) | | low | CMOS/LVDS | not checked — in Red Pitaya STEMlab 125-14 [10] |
| **TI ADC3664** | 14 / 125 MS/s / 2 | NSD −156.9 dBFS/Hz; SNR 77.5 dBFS [2] | 12.6 | 100 mW/ch | serial LVDS | not in snapshot |
| **TI ADS4249** | 14 / 250 MS/s / 2 | 71.7 dBFS SNR, 80 dBc SFDR @ 170 MHz [3] | 11.6 | 560 mW total, 1.8 V | DDR LVDS / CMOS | not in snapshot (ADS4149 C2670820 / 5 / 76.55) |
| TI ADS42LB69 | 16 / 250 MS/s / 2 | 73.2 dBFS (2 V_pp), 74.9 (2.5 V_pp) @ 170 MHz [4] | 11.9–12.2 | 820 mW/ch | DDR/QDR LVDS | not in snapshot |
| ADI AD9649 | 14 / 20–80 MS/s / 1 | (see DS) | | low | CMOS | C69599 / 503 / 27.85 (-20) |
| ADI AD9629 | 12 / 20–80 MS/s / 1 | | | low | CMOS | C653641 / 240 / 12.04 (-40) |
| ADI AD9235 | 12 / 20–65 MS/s / 1 | | | | CMOS | C653327 / 231 / 10.60 (-40) |
| ADI AD9643 | 14 / 250 MS/s / 2 | | | | LVDS | C653687 / 70 / 92.71 |
| ADI AD9226 | 12 / 65 MS/s / 1 | (see DS; module boards common) | ~11 (unverified) | ~475 mW (unverified) | CMOS parallel | chip not in snapshot; modules US$13–19 [5] |
| **ADI AD9280** | 8 / 32 MS/s / 1 | | | | CMOS | C130297 / 85 / 6.59 |
| ADI AD9288 | 8 / 40–100 MS/s / 2 | | | | CMOS | C514284 / 135 / 8.21 (-80) |
| ADI/Maxim **MAX19506** | 8 / 100 MS/s / 2 | 49.8 dBFS / 69 dBc @ 70 MHz [6] | 8.0 | 57 mW/ch analog | CMOS | not in snapshot |
| TI ADC08060 / ADC10080 | 8 / 60 MS/s; 10 / 80 MS/s | | | | CMOS | C701580 / 806 / 4.96; C544415 / 9 / 10.76 |

### B. GSPS / RF-sampling converters (JESD204B/C)
| Part | Spec | Notes | Availability |
|---|---|---|---|
| ADI AD9680 | dual 14-bit, 500 MS/s–1.25 GS/s, signals to 2 GHz, 2 DDCs/ch, JESD204B [7] | used on many ADI FMC boards | Mouser/Digikey |
| ADI AD9208 | dual 14-bit 3 GS/s, 9 GHz −3 dB BW, direct sampling to 5 GHz [7] | | Mouser/Digikey |
| TI ADC12DJ3200 | 12-bit, 6.4 GS/s (1 ch) / 3.2 GS/s (2 ch); NSD −154.6/−151.8 dBFS/Hz; HD2/HD3 −65 dBc to 3 GHz; 8 GHz BW [8] | radar, SDR, scopes | Mouser/Digikey |
| TI AFE7950 | 4T6R: 12 GS/s DACs, 3 GS/s ADCs, RF 0.6–12 GHz, 1.2 GHz RX BW, TX DSA 40 dB in 0.125 dB [9] | full data sheet on request | TI (restricted) |
| AMD Zynq UltraScale+ RFSoC (ZU48DR etc.) | integrated 14-bit 5 GS/s ADCs + 9.85 GS/s DACs + FPGA + ARM | RFSoC 4x2 academic US$2,499 [10]; XCZU2CG (non-RF MPSoC) C3228798 ~US$89 | boards only for hobby use |

### C. DACs
| Part | Bits / rate / ch | Key spec | Interface | LCSC / stock / US$ |
|---|---|---|---|---|
| **TI DAC5672** | 14 / 275 MS/s / 2 | SFDR 84 dBc @ 5 MHz; IMD3 79 dBc; WCDMA ACLR 73 dB [11] | 2 × 14-bit parallel | C2679527 / 10 / 17.57 |
| ADI AD9767 | 14 / 125 MS/s / 2 | (see DS) | parallel | C653820 / 175 / 10.41 |
| ADI AD9764 / AD9744 | 14 / 125 MS/s / 1 | | parallel | C515886 / 338 / 10.62; C461519 / 158 / 10.62 |
| TI DAC904 | 14 / 165 MS/s / 1 | | parallel | C2679883 / 187 / 5.08 |
| ADI AD9708 | 8 / 125 MS/s / 1 | | parallel | C653732 / 48 / 13.41 |
| TI DAC5675 / DAC3174 | 14-bit 400 MS/s / dual 14-bit 500 MS/s (unverified) | | LVDS | C1554516 / 79 / 80.83; C2679421 / 7 / 39.79 |
| ADI AD9957 (DDS + DAC + IQ modulator) | 14-bit 1 GS/s quadrature digital upconverter (unverified detail) | | parallel/serial | C514308 / 206 / 34.11 |

### D. Low-rate, high-resolution converters for radar beat signals and low-IF receivers
| Part | Channels / rate / bits | Key spec | Notes | LCSC / stock / US$ |
|---|---|---|---|---|
| **ADI ADAR7251** | 4 / 1.8 MS/s / 16 | FMCW-radar AFE (LNA + PGA + anti-alias + ADC) | pairs with ADF4159/ADF5901/ADF5904 | C654357 / 7 / 16.67 |
| ADI AD7768-4 | 4 / up to 256 kS/s / 24 (Σ-Δ, unverified rate) | precision | | C2670735 / 264 / 20.71 |
| TI ADS1675 | 1 / 4 MS/s / 24 (unverified) | | | C2670711 / 28 / 28.92 |
| **TI PCM1808** | 2 / 96 kHz / 24 | SNR 99 dB, THD+N −93 dB, 0.91 Hz HPF (at 48 kHz) [12] | I²S; the cheapest decent radar/beat ADC | C55513 / 6.5k / 0.63 |
| TI TLV320AIC3204 | 2 ADC + 2 DAC / 192 kHz (unverified) / 24 | ADC SNR 93 dB, DAC 100 dB; 6.1 mW ADC | codec with PGA and mic bias | C24109 / 3.8k / 1.60 |
| TI PCM1802 / PCM1804 / PCM1865 | 2 / 96–192 kHz / 24 | | PCM1865 has PGA + mux (4 inputs) | C2866894 / 151 / 2.02; C62360 / 215 / 2.14; C181312 / 444 / 3.83 |
| Cirrus CS4272 / CS5381 / WM8731 | codec / ADC / codec | | | C2151111 / 1.1k / 3.75; C5382102 / 41 / 7.30; C41511 / 979 / 12.58 |
| Everest ES7243E / ES8388 | 2-ch ADC / codec | cheap (ESP32-audio ecosystem) | | C2929446 / 4.7k / 0.52; C365736 / 2.3k / 0.98 |
| AKM AK5572 / AK5558 | 2 / 8 ch high-end ADC | | | C5451857 / 82 / 11.31; C2655448 / 25 / 17.13 |

### E. ADC drivers and FPGA hosts
| Part | Role | LCSC / stock / US$ |
|---|---|---|
| ADI ADA4930-1 / ADA4932-1, TI THS4541, AD8138 | differential ADC drivers | C578938 / 1.3k / 9.17; C206666 / 979 / 6.23; C2057378 / 1.8k / 4.15; C652359 / 1.2k / 9.29 |
| ADI AD8351, ADL5565, TI LMH6881 | RF/IF differential amplifiers | C208238 / 44 / 8.87; C579166 / 6 / 17.21; C701929 / 45 / 13.95 |
| Lattice iCE40UP5K / ECP5 LFE5U-25F | small FPGAs (AT86RF215 IQ, parallel ADCs) | C2678152 / 424 / 5.93; C1550762 / 547 / 10.38 |
| AMD XC7A35T / XC7Z010 / XC7Z020 | Artix-7 / Zynq-7000 (LVDS ADCs, Pluto/Red Pitaya class) | C1521698 / 495 / 25.10; C2840993 / 599 / 21.73; C569043 / 1.8k / 27.52 |

## Worked examples
### 1. Direct-sampling HF receiver (0–30 MHz) with LTC2208
$f_s$ = 122.88 MS/s (Nyquist 61.44 MHz, generous anti-alias margin above 30 MHz). Noise-limited DR in 500 Hz = 78 + 50.9 ≈ **129 dB**; SFDR-limited ≈ 100 dB [1]. Atmospheric noise at HF is high, so the ADC noise floor ($-156$ dBFS/Hz) only needs a few dB of preamp gain to sit below the band noise. Clock: ≤ 0.67 ps rms at a 30 MHz input for full SNR ($10^{-78/20}/(2\pi\cdot30\times10^6)$ = 0.67 ps), ≤ 0.29 ps if you also undersample a 70 MHz IF. Data: 16 bits × 122.88 MS/s ≈ 2 Gb/s → FPGA (ECP5/Artix-7), decimate in DDCs ([NCO/DDC](../14-sdr-dsp/nco-ddc-duc.md)).

### 2. 24 GHz FMCW radar back end: codec or ADAR7251?
Chirp 24.00–24.25 GHz (B = 250 MHz) in T = 1 ms. Target to 100 m → $f_b$ = 167 kHz. PCM1808 (Nyquist 48 kHz at 96 kHz) → $R_{max}$ ≈ 28.8 m at this chirp; lengthening T to ≈ 4.2 ms restores 100 m at 40 kHz but lowers the update rate and raises phase-noise/Doppler smearing. ADAR7251 (1.8 MS/s, 4 channels) handles 167 kHz with margin and gives 4 coherent RX channels for angle estimation — the reference-design route with ADF4159/ADF5901/ADF5904 ([phased-array & radar parts](phased-array-and-radar-parts.md)).

### 3. A low-cost IF-sampling SDR on an FPGA board
Receiver: LNA → SAW → mixer to 10.7 MHz IF → AD9226 at 40 MS/s (or AD9235) → FPGA DDC. The 12-bit ADC gives SNR ≈ 65–69 dB (unverified for these modules) → in a 125 kHz LoRa channel ≈ 65 + 10·log₁₀(20 MHz/125 kHz) ≈ **87 dB** dynamic range. Good enough for experiments; module layout quality, clock and ground noise usually limit real performance (anecdotal) — compare with a cheap RTL-SDR plus a good front end before building ([sdr-hardware survey](../14-sdr-dsp/sdr-hardware-survey.md)).

## Practical notes
- **Clocking**: use a low-jitter oscillator or clock cleaner (LMK61E2, Si5341, LMK04828 — [mixers/PLLs/clocks](mixers-plls-vcos-parts.md)); route the clock differentially, away from digital outputs.
- **Front end**: pipelined ADC inputs are switched-capacitor loads — use the datasheet's recommended RC/balun network or a differential driver; add an anti-alias (or bandpass for undersampling) filter.
- **Digital outputs**: parallel CMOS outputs at > 50 MS/s radiate and inject noise into the analog input; use LVDS parts for > 100 MS/s, series resistors on CMOS outputs, and a split-but-connected ground strategy per the datasheet ([mixed-signal layout](../13-pcb-rf-layout-emc/mixed-signal-layout.md), planned).
- **Power**: 0.5–1.6 W per high-speed ADC; thermal pads need vias; separate low-noise LDOs for AVDD.
- **JESD204B/C**: requires FPGA SERDES, deterministic latency (SYSREF) and substantial HDL; use vendor reference designs (ADI HDL, TI JESD IP) or buy an FMC board.
- **Audio codecs as radar ADCs**: most have DC-blocking high-pass filters (PCM1808 0.91 Hz at 48 kHz) and anti-alias filters tailored to audio; check the HPF (low-range targets appear at low beat frequencies) and use a codec with a bypassable HPF when needed.
- **Buy vs build**: for general SDR work, boards (Red Pitaya 125-14, PlutoSDR, bladeRF, USRP, RFSoC 4x2) beat a first home-made high-speed ADC board on cost and time ([sdr-hardware survey](../14-sdr-dsp/sdr-hardware-survey.md)).

## Recommended picks for Marcus's use cases
| Use case | Pick | Why |
|---|---|---|
| Learning FPGA-SDR cheaply | AD9226/AD9280 modules + small FPGA board | US$15–50 total; accept limited performance |
| Serious IF-sampling receiver (≤ 60 MHz IF) | ADC3664 (dual 14-bit 125 MS/s, 100 mW/ch) or LTC2208 | low noise, low power |
| Wide IF / multi-channel | ADS4249 (dual 14-bit 250 MS/s) | 560 mW total |
| FMCW radar beat ADC | ADAR7251 (4 ch) or PCM1808 (stereo, US$0.63) for slow chirps | matched to kHz–MHz beats |
| Waveform generation for radar/SDR TX | DAC5672 or AD9767 + IQ modulator (TRF3705/ADL5375) | dual, clean |
| GHz direct sampling / phased-array digital beamforming | RFSoC 4x2 board | integrated ADC/DAC/FPGA; avoid chip-down JESD designs early |

## Parts to avoid (or use knowingly)
- **8-bit ADCs for weak-signal receivers** without strong AGC and filtering (49.8 dBFS SNR on MAX19506 [6]).
- **Chip-down GSPS JESD204 converters** on a first project — power, clocking, SERDES and HDL effort dominate.
- **Parallel-CMOS ADCs at > 100 MS/s** on 2-layer boards — noise coupling.
- **Marketplace "AD9226" modules** assumed to meet datasheet SNR — measure with a clean tone (FFT SNR/SFDR) before use.

## Common mistakes & misconceptions
- *"A 16-bit ADC has 96 dB SNR."* LTC2208 is 78 dBFS; ENOB ≈ 12.7.
- *"More bits always help."* With a noisy clock or a poor front end, jitter and driver distortion dominate.
- *"SFDR improves with processing gain like SNR."* It does not (spurs are coherent).
- *"Radar needs a GSPS ADC."* FMCW radars digitise kHz–MHz beat signals; audio-class converters are often enough.

## How to simulate / verify
```python
import math
enob = lambda snr: (snr - 1.76)/6.02
nsd  = lambda snr, fs: -snr - 10*math.log10(fs/2)
dr_b = lambda snr, fs, B: snr + 10*math.log10(fs/2/B)
jit  = lambda snr, fin: 10**(-snr/20)/(2*math.pi*fin)
print(enob(78), nsd(78, 130e6), dr_b(78, 122.88e6, 500), jit(78, 70e6))
fb = lambda R, B, T: 2*R*B/(3e8*T)
print(fb(100, 250e6, 1e-3))          # 167 kHz
```
- Bench: inject a clean, filtered tone (signal generator + bandpass filter), capture ≥ 16k samples, FFT with a Blackman–Harris window, compute SNR/SFDR/ENOB ([FFT & windows](../14-sdr-dsp/fft-spectral-analysis-windows.md)).

## Open questions / gaps
- AD9226, LTC2145, AD9649/AD9629 and AD7768 performance figures not verified from datasheets (ADI site blocked for scripts).
- Whether HPSDR Hermes-class boards still use LTC2208 was not re-verified.
- No measurement of marketplace AD9226/AD9280 modules in this KB.

## Sources
1. Analog Devices, *LTC2208 16-Bit, 130 Msps ADC* data sheet (2208fc), https://www.analog.com/media/en/technical-documentation/data-sheets/2208fc.pdf — 78 dBFS noise floor, 100 dB SFDR, 700 MHz inputs, 70 fs jitter (via search extract). (datasheet, secondary extract)
2. Texas Instruments, *ADC3664 14-bit 125 MSPS dual ADC* data sheet, https://www.ti.com/lit/ds/symlink/adc3664.pdf, p. 1 — NSD −156.9 dBFS/Hz, SNR 77.5 dBFS, 100 mW/ch, 1.4 GHz BW. (datasheet)
3. Texas Instruments, *ADS4249 dual 14-bit 250 MSPS ultralow-power ADC* SBAS534E, https://www.ti.com/lit/ds/symlink/ads4249.pdf, p. 1. (datasheet)
4. Texas Instruments, *ADS42LBx9 14/16-bit 250 MSPS ADCs* data sheet, https://www.ti.com/lit/ds/symlink/ads42lb69.pdf, p. 1. (datasheet)
5. Analog Devices AD9226 product page (12-bit 65 MSPS, via search extract); AliExpress AD9226 module listings (prices). (manufacturer / marketplace)
6. Analog Devices/Maxim, *MAX19506 dual 8-bit 100 Msps ADC* data sheet, https://www.analog.com/media/en/technical-documentation/data-sheets/max19506.pdf — 49.8 dBFS, 69 dBc, 57 mW/ch (via search extract). (datasheet, secondary extract)
7. Analog Devices, *AD9680* and *AD9208* data sheets / product pages (via search extracts): https://www.analog.com/en/products/ad9680.html, https://www.analog.com/media/en/technical-documentation/data-sheets/AD9208.pdf. (datasheet, secondary extract)
8. Texas Instruments, *ADC12DJ3200 6.4 GSPS single / 3.2 GSPS dual 12-bit RF-sampling ADC*, https://www.ti.com/lit/ds/symlink/adc12dj3200.pdf, p. 1. (datasheet)
9. Texas Instruments, *AFE7950 4T6R RF sampling AFE* SBASA41E (2025), https://www.ti.com/lit/ds/symlink/afe7950.pdf, p. 1. (datasheet)
10. Real Digital, *RFSoC 4x2* (ZU48DR, 4 × 5 GS/s ADC, 2 × 14-bit 9.85 GS/s DAC, academic US$2,499), https://www.realdigital.org/hardware/rfsoc-4x2; Red Pitaya documentation (STEMlab 125-14: LTC2145-14, Zynq 7010), https://redpitaya.readthedocs.io (via search extracts). (vendor)
11. Texas Instruments, *DAC5672 14-bit 275 MSPS DAC* SLAS440D, https://www.ti.com/lit/ds/symlink/dac5672.pdf, p. 1. (datasheet)
12. Texas Instruments PCM1808 and TLV320AIC3204 data sheets p. 1 (https://www.ti.com/lit/ds/symlink/pcm1808.pdf, …/tlv320aic3204.pdf); local JLCPCB/LCSC parts database (jlcparts in-stock snapshot, newest record 2026-04-01) via `jlc-trawler`. (datasheet; distributor data)
