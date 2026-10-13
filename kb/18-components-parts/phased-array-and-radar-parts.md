---
title: Phased-array and radar parts — beamformer ICs, phase shifters, mmWave radar SoCs (TI, Infineon, Acconeer), ADI 24 GHz chipset and radar modules (procurement guide)
domain: 18-components-parts
slug: phased-array-and-radar-parts
tags: [phased-array, beamformer, adar1000, adtr1107, adar2001, adar2004, anokiwave, awmf-0108, phase-shifter, hmc642, hmc647, hmc649, maps-010164, pe44820, adar4002, radar, fmcw, iwr6843, iwr6843aop, awr1843, iwrl6432, bgt60tr13c, bgt60ltr11aip, bgt24ltr11, a121, xm125, adf5901, adf5904, adf4159, adar7251, hb100, ipm-165, cdm324, hlk-ld2410, lcsc]
prerequisites:
  - ../12-phased-arrays/phase-shifters-ttd-components.md
  - ../11-radar/fmcw-radar.md
related:
  - ../12-phased-arrays/beamforming-architectures.md
  - ../12-phased-arrays/diy-phased-array-projects.md
  - ../12-phased-arrays/array-calibration.md
  - ../11-radar/diy-radar-hardware.md
  - ../11-radar/cw-and-doppler-radar.md
  - ../19-regulations-safety/singapore-imda-rules.md
  - mixers-plls-vcos-parts.md
  - adcs-dacs-for-sdr.md
  - rf-switches-attenuator-parts.md
  - pcb-substrates-parts.md
level: intermediate
confidence: medium
last_updated: 2026-10-02
---

# Phased-array and radar parts — procurement guide

> Theory and detailed device characterisation live in [phase shifters & TTD components](../12-phased-arrays/phase-shifters-ttd-components.md),
> [DIY phased-array projects](../12-phased-arrays/diy-phased-array-projects.md) and [DIY radar hardware](../11-radar/diy-radar-hardware.md).
> This page answers *which part number, where to buy it, what it costs, and what to avoid*.

## Questions this page answers
- Which radar chip or module should I buy to measure rail-exit velocity or range near the pad?
- Which mmWave radar SoCs (TI IWR/AWR, Infineon BGT60, Acconeer A121) are in LCSC stock, and are their bands legal in Singapore?
- What is in the ADI 24 GHz FMCW chipset (ADF4159 + ADF5901 + ADF5904 + ADAR7251)?
- Which beamformer or phase-shifter IC fits a 2.4/5.8/10 GHz array, and what does a channel cost?
- Are ADAR2001/ADAR2004 beamformers? (No — see below.)
- Which cheap radar modules (HB100, CDM324/IPM-165, HLK-LD2410) are worth playing with?

## TL;DR
- **mmWave radar SoCs = the best value "real" radar**: TI **IWR6843** (60–64 GHz, 4 GHz continuous BW, 3 TX / 4 RX, TX 12 dBm, 6-bit TX phase shifter, C674x DSP + Arm R4F; C2871887, 1.3k in LCSC stock, ~US$16) [1]; **IWR6843AOP** (antenna-on-package version) [2]; **AWR1843** (76–81 GHz, 12 dBm, RX NF 14–15 dB, phase noise −95/−93 dBc/Hz @ 1 MHz, automotive; C3178349-class stock thin) [3]; **IWRL6432** (57–64 GHz, 7 GHz BW, 11 dBm, NF 11 dB, low power) [4]. Infineon **BGT60TR13C** (58–63.5 GHz, 1 TX / 3 RX, 5.5 GHz BW → ~3 cm resolution, 12-bit 4 MS/s ADCs, AiP) [5]; **BGT60LTR11AIP** (61–61.5 GHz Doppler motion sensor, 10 dBm, C3606906, ~US$8) [6]; **Acconeer A121** (60 GHz pulsed coherent radar, AiP, mm-accuracy distance to ~20 m; XM125 module C5837899, ~US$30) [7].
- **Legal bands in Singapore** (per the 11/19 domain pages): 24.00–24.25 GHz ≤ 100 mW; **57–64 GHz ≤ 100 mW**; 76–77 GHz vehicle/infrastructure radar; **77–81 GHz is not in TS SRD but is licence-exempt as an Ultra-Wideband device** (Exemption Notification item 17; IMDA TS UWB 2016: mean e.i.r.p. density ≤ −3 dBm/MHz, peak ≤ 55 dBm/50 MHz, sweep ≥ 500 MHz, not a fixed outdoor installation) — a TI AWR/IWR18xx sweeping ≥ 1 GHz is typically 5–15 dB under the density limit ([DIY radar Example 4](../11-radar/diy-radar-hardware.md#worked-examples)); 60 GHz parts (IWR6843, BGT60, A121) remain the simplest choice under the plain 100 mW SRD rule [8]. (Corrected 2026-10-02 by W5-E1; the earlier "77–81 GHz not listed" applied to TS SRD only.)
- **ADI 24 GHz FMCW chipset**: **ADF4159** (13 GHz ramp PLL; C459155, ~US$9.4) + **ADF5901** (24–24.25 GHz 2-channel TX with VCO; C654718, 50 pcs, ~US$26) + **ADF5904** (24–24.25 GHz 4-channel RX: gain 22 dB, NF 10 dB, IIP3 +20 dBm listed, 170 mA; C654723, 15 pcs, ~US$14) + **ADAR7251** (4-channel 16-bit 1.8 MS/s radar AFE; C654357, 7 pcs, ~US$17) [9][10]. Needs a Rogers antenna board ([substrates](pcb-substrates-parts.md)).
- **Beamformers**: ADI **ADAR1000** (8–16 GHz, 4 ch, 360° in 2.8° steps, ≥ 31 dB gain range, RX NF 8 dB → pair with **ADTR1107** 6–18 GHz FEM) — used in the ADI Phaser (≈ US$2,875) [11]; Anokiwave (now **Qorvo**, acquisition completed 5 Feb 2024) **AWMF-0108** (27.5–30 GHz, 4 ch, 5-bit phase/gain, half duplex) [12][13]. **ADAR2001/ADAR2004 are not phase-shifting beamformers** — they are a mmWave body-scanner ×4-multiplier/4-PA transmitter (2.5–10 GHz in) and a 10–40 GHz 4-channel receive mixer (IF ≤ 800 MHz) [14].
- **Discrete phase shifters** (from the 12 domain, verified there): HMC647A 2.5–3.1 GHz, HMC649A 3–6 GHz, HMC642A 9–12.5 GHz (6-bit, 5.625° LSB), PE44820 1.7–2.2 GHz 8-bit, Qorvo QPC2108 2.5–4 GHz (~US$170), MACOM **MAPS-010164** (2.3–3.8 GHz; C5270800, 18 pcs, ~US$86), ADAR4002 TTD (0.5–19 GHz, 7-bit) [11]. Only MAPS-010164 was in the LCSC snapshot.
- **Cheap modules**: HB100 (10.525 GHz Doppler, EIRP 20 dBm, made in Singapore by ST Engineering), IPM-165/CDM324 (24.05–24.25 GHz Doppler, EIRP 16 dBm) [15]; **HLK-LD2410B** (24 GHz presence sensor, UART, 5 V 70 mA; C5183132, 785 pcs, ~US$4) [10]. Doppler at 24.125 GHz: 8.0 kHz for 50 m/s, 40 kHz for 250 m/s — audio-card range.
- **Channel cost reality**: US$100–300 per channel in parts at 2–6 GHz with discrete phase shifters; coherent SDRs (KrakenSDR ≈ US$750 for 5 ch ≤ 1.77 GHz) for digital beamforming below 1.8 GHz [11].

## Intuition (no math)
There are three ways to buy "radar" in 2026: (1) a **Doppler module** (a fixed oscillator, an antenna and one mixer — only speed, no range) for a few dollars; (2) a **radar SoC** (FMCW transmitter, multiple receivers, ADCs and a DSP on one chip, often with antennas in the package) that outputs point clouds or range–Doppler maps over UART/SPI; (3) a **chipset** (separate PLL, TX, RX, ADC) you integrate on your own RF board — maximum flexibility, maximum RF layout work. Phased arrays similarly go from buying an evaluation platform (ADI Phaser, KrakenSDR) to beamformer ICs (4 channels of phase + gain per chip) to discrete phase shifters, attenuators and LNAs per element.

For a rocket team the value of radar is **independent truth** for the flight computer's velocity/altitude estimate ([DIY radar hardware](../11-radar/diy-radar-hardware.md)); the value of an array is mostly **direction-finding for recovery** and high-rate links at 2.4/5.8 GHz ([DIY phased-array projects](../12-phased-arrays/diy-phased-array-projects.md)).

## The math — spec-to-performance relationships
### Level 1 — resolution and Doppler
Range resolution $\Delta R = c/(2B)$: 250 MHz (24 GHz ISM) → 0.60 m; 4 GHz (IWR6843) → 3.75 cm; 5.5 GHz (BGT60TR13C) → 2.7 cm; 7 GHz (IWRL6432) → 2.1 cm. Doppler $f_d = 2v f_c/c$: at 10.525 GHz, 50 m/s → 3.5 kHz (250 m/s → 17.5 kHz); at 24.125 GHz → 8.0 kHz (40.2 kHz); at 61 GHz → 20.3 kHz (102 kHz) (computed). The chirp design must keep the unambiguous velocity above the rocket's speed ([FMCW radar](../11-radar/fmcw-radar.md)).

### Level 2 — array errors from phase-shifter specs
For $N$ elements with independent rms phase error $\sigma_\phi$ (rad), directivity falls by $\approx e^{-\sigma_\phi^2}$ and the average far-sidelobe floor rises to $\approx \sigma_\phi^2/N$ relative to the peak (uniform illumination). With a 6-bit phase shifter of 4.5° rms error (HMC642A class): gain loss 0.027 dB, sidelobe floor ≈ −31 dB for $N$ = 8 (computed). The 5.625° LSB alone contributes $5.625°/\sqrt{12}$ = 1.6° rms. Amplitude/phase coupling (attenuator states shift phase) matters more — calibrate a 2-D table ([array calibration](../12-phased-arrays/array-calibration.md)).

### Level 3 — noise figure of a beamformer channel
A beamformer with NF 8 dB (ADAR1000 RX) is not an LNA: put an LNA with ≥ 15–20 dB gain before it (ADTR1107 gives channel NF ≈ 2.7 dB per the 12-domain script) — the same Friis logic as in [LNA parts](lna-pa-gain-block-mmics.md).

## Design equations & rules of thumb
| Rule | When valid | Typical values |
|---|---|---|
| $\Delta R=c/2B$ | FMCW/pulse | 4 GHz → 3.75 cm |
| $f_d=2vf_c/c$ | CW/Doppler | 24.125 GHz, 50 m/s → 8.0 kHz |
| Directivity loss ≈ $e^{-\sigma_\phi^2}$; SLL floor ≈ $\sigma_\phi^2/N$ | random phase error | 4.5° rms, N = 8 → 0.03 dB, −31 dB |
| Phase-quantisation rms = LSB/√12 | digital phase shifters | 6-bit: 1.6° |
| LNA before any phase shifter/beamformer | receive arrays | NF 8 dB → ≈ 2.7 dB with FEM |
| Use 60 GHz parts for SG experiments | IMDA SRD | 57–64 GHz ≤ 100 mW [8] |

## Comparison tables (LCSC data: 2026-04 snapshot [10]; US$ qty 1)
### A. mmWave radar SoCs and sensors
| Part | Band / BW | TX / RX | Key spec | Processing / output | Package | LCSC / stock / US$ |
|---|---|---|---|---|---|---|
| **TI IWR6843** | 60–64 GHz, 4 GHz | 3 / 4 | TX 12 dBm; 6-bit TX phase shifter [1] | C674x DSP, HWA, Arm R4F; 40 MHz crystal | FCBGA-180 | C2871887 / 1.3k / 16.11 |
| TI IWR6843AOP | 60–64 GHz, 4 GHz | 3 / 4 | antennas on package [2] | as IWR6843 | FCBGA | not in snapshot |
| TI IWR1443 / IWR1843 | 76–81 GHz | 3 / 4 | | IWR1843 adds DSP | FCBGA-161 | C1558318 / 23 / 21.82; C3178349 / 12 / 25.53 |
| TI AWR1843 / AWR1642 / AWR6843 / AWR2944 | 76–81 GHz (AWR6843 60–64) | 3/4 (AWR2944 4/4) | TX 12 dBm; NF 14–15 dB; PN −95/−93 dBc/Hz @ 1 MHz (AWR1843) [3] | automotive (AEC-Q100) | FCBGA / FCCSP | AWR1642 C1526158 / 10 / 40.75; AWR6843 C3178330 / 21 / 51.90; AWR2944 C49406819 / 10 / 67.50 |
| **TI IWRL6432** | 57–64 GHz, 7 GHz | (see DS) | 11 dBm, NF 11 dB, −89 dBc/Hz @ 1 MHz, 5 MHz IF, low-power modes [4] | Arm M4F + HWA | | not in snapshot |
| **Infineon BGT60TR13C** | 58–63.5 GHz, 5.5 GHz | 1 / 3 | 12-bit 4 MS/s ADCs, AiP, 1.8 V ~200 mA active, ≤ 5 mW duty-cycled [5] | raw IF data over SPI | AiP | not in snapshot |
| Infineon BGT60LTR11AIP | 61–61.5 GHz | 1 / 1 | 10 dBm, Doppler motion sensing, 128 mA TX [6] | autonomous motion/direction detect | BGA-42 AiP | C3606906 / 102 / 8.03 |
| Infineon BGT60UTR11AIP | 60 GHz | (see DS) | integrated antenna, PLL, temp sensor | SPI | BGA-28 | C21230524 / 19 / 11.39 |
| Infineon BGT24LTR11 | 24 GHz | 1 / 1 | TX ≈ 6 dBm typ. [16] | Doppler, I/Q IF | VQFN | not in snapshot |
| **Acconeer A121** (XM125 module) | 60 GHz pulsed coherent | 1 / 1 | mm-level distance accuracy, up to ~20 m, AiP, 29 mm² [7] | on-chip processing; module has MCU | 5.5 × 5.2 mm class | XM125 C5837899 / 7 / 29.87 (A121 chip listed at LCSC as C5828704) |
| HI-LINK **HLK-LD2410B** | 24 GHz | module | presence/motion, UART, 5 V 70 mA | module MCU | 35 × 7 mm | C5183132 / 785 / 4.04 |

### B. Radar chipset parts (build-your-own FMCW)
| Part | Function | Key spec | LCSC / stock / US$ |
|---|---|---|---|
| **ADI ADF4159** | 13 GHz fractional-N ramp PLL | sawtooth/triangle/parabolic ramps, 110 MHz PFD | C459155 / 11 / 9.36 |
| TI LMX2491 / LMX2492 | 6.4 / 14 GHz ramp PLL | 8-segment ramps | C2651213 / 51 / 8.27; C2664080 / 24 / 20.03 |
| **ADI ADF5901** | 24 GHz 2-ch TX + VCO | 24–24.25 GHz, 3.3 V | C654718 / 50 / 26.33 |
| **ADI ADF5904** | 24 GHz 4-ch RX (LNA + mixer) | gain 22 dB, NF 10 dB, IIP3 +20 dBm, P1dB −10 dBm, 170 mA (listing) | C654723 / 15 / 14.09 |
| **ADI ADAR7251** | 4-ch 16-bit 1.8 MS/s radar AFE | LNA/PGA/AAF/ADC per channel | C654357 / 7 / 16.67 |
| TI LMX2572 (ramp, integrated VCO to 6.4 GHz) | 5.8 GHz FMCW | [mixers/PLLs](mixers-plls-vcos-parts.md) | C2665711 / 996 / 9.58 |

### C. Beamformers, phase shifters and TTD
| Part | Band | Channels / bits | Key spec (source: [11] unless noted) | Availability |
|---|---|---|---|---|
| **ADI ADAR1000** | 8–16 GHz | 4 ch, 360° in 2.8° steps; ≥ 31 dB gain range | RX gain 10 dB, NF 8 dB, IIP3 −7 dBm; TX 21 dB, OP1dB 10 dBm; 121 beam states; 20 ns switching | Mouser/Digikey (not in LCSC snapshot) |
| ADI ADTR1107 | 6–18 GHz | FEM (PA + LNA + switch) | RX 18 dB, NF 2.5 dB; TX Psat 25 dBm | Mouser/Digikey |
| Anokiwave/Qorvo AWMF-0108 | 27.5–30 GHz | 4 ch, 5-bit phase & gain, half duplex [12] | 5G/satcom | Qorvo (request) |
| ADI ADAR2001 / ADAR2004 | 2.5–10 GHz in → ×4 TX; 10–40 GHz RX mixer | 4 ch | **body-scanner TX/RX, not phase shifters** [14] | ADI |
| ADI HMC647A / HMC649A / HMC642A | 2.5–3.1 / 3–6 / 9–12.5 GHz | 6-bit, 5.625° LSB | rms 1.5° / 4° / 4.5°; IL 7–10 dB (HMC642A) | Mouser/Digikey |
| pSemi PE44820 | 1.7–2.2 GHz | 8-bit, 1.4° steps | | Mouser/Digikey |
| Qorvo QPC2108 | 2.5–4 GHz | 6-bit | rms < 2.8°, ~US$170 | Mouser |
| MACOM MAPS-010164 | 2.3–3.8 GHz | digital phase shifter | ±3–5.5 V supplies (listing) | C5270800 / 18 / 85.93 |
| Mini-Circuits JSPHS-2484+ | 2.15–2.484 GHz | analog (varactor), ≥ 180° | 2 dB IL, 0–15 V control, nonlinear | Mini-Circuits |
| ADI ADAR4002 | 0.5–19 GHz | 7-bit TTD, 508 ps/4 ps or 254 ps/2 ps | | Mouser/Digikey |
| pSemi PE43711 / ADI HMC624A (amplitude weights) | to 6 GHz | 7-bit / 6-bit DSA | see [switches & DSAs](rf-switches-attenuator-parts.md) | LCSC C470929 / C662314 |

### D. Evaluation platforms (buy before you build)
| Platform | What it gives you | Price (approx.) |
|---|---|---|
| ADI Phaser (EVAL-CN0566-RPIZ) | 8-element 10–10.5 GHz RX array, 2 × ADAR1000, ADF4159 FMCW, Pluto + RPi, Python labs | ≈ US$2,875 [11] |
| TI IWR6843ISK / IWR6843AOPEVM / AWR1843BOOST | mmWave SoC EVMs with antennas, mmWave Studio/SDK | ~US$100–400 (unverified; check TI store) |
| Infineon DEMO BGT60TR13C / Distance2Go (BGT24LTR11) | radar kits with Python/Matlab SDKs | ~US$100–300 (unverified) |
| Acconeer XE125 / XM125 | A121 module + eval | XM125 ~US$30 at LCSC [10] |
| KrakenSDR | 5-ch coherent receiver ≤ 1.77 GHz for DF | ≈ US$750 [11] |
| HB100 / CDM324 / HLK-LD2410 modules | Doppler/presence modules | US$2–10 (marketplace; LD2410B US$4 at LCSC) |

## Worked examples
### 1. Rail-exit velocity measurement
Rocket leaves a 6 m rail at ~30–50 m/s; Doppler at 24.125 GHz = 4.8–8.0 kHz (at 10.525 GHz: 2.1–3.5 kHz). A CDM324/IPM-165 or HB100 + an audio-codec ADC (PCM1808, [ADC parts](adcs-dacs-for-sdr.md)) captures this; single-mixer modules give speed but not direction [15]. For range + velocity + angle up to ~100 m, an **IWR6843** EVM at 60–64 GHz (legal band, 3.75 cm resolution) is the step up; check its maximum unambiguous velocity for your chirp configuration.

### 2. How good must a phase shifter be for an 8-element 5.8 GHz array?
HMC649A-class 6-bit shifter with ≈ 4° rms error: directivity loss ≈ 0.02 dB and sidelobe floor ≈ −32 dB for $N$ = 8 (Level 2) — far better than FR-4 array tolerances and mutual coupling will allow. Spend the money on calibration and on a low-loss antenna board ([substrates](pcb-substrates-parts.md)), not on a 7-bit shifter.

### 3. Picking a 24 GHz chipset vs a 60 GHz SoC
ADF5901 + ADF5904 + ADF4159 + ADAR7251 ≈ US$66 in chips (LCSC singles) + a Rogers antenna board + weeks of RF layout, for 250 MHz of sweep (0.6 m). An IWR6843 (~US$16 chip, EVM ~US$100–400) gives 4 GHz (3.75 cm), 3 × 4 MIMO and a DSP. Unless the goal is learning RF chain design, the SoC wins.

### 4. Per-channel BOM for a 4-element 5.8 GHz analog receive array
| Function | Part (this domain) | Qty/ch | Price basis |
|---|---|---|---|
| LNA (0.7–6 GHz, NF 0.4 dB, 20 dB) | Qorvo TQP3M9037 (C415712) | 1 | ~US$2.36 LCSC [10] |
| Amplitude weight (7-bit DSA to 6 GHz) | pSemi PE43711 (C470929) | 1 | ~US$2.77 LCSC [10] |
| Phase shifter (3–6 GHz, 6-bit) | ADI HMC649A | 1 | distributor (price not captured) |
| Bias/decoupling, 0402 passives | JLC basic/preferred | ~15 | < US$0.10 |
| Combiner | 4-way Wilkinson on RO4350B | shared | board cost ([substrates](pcb-substrates-parts.md)) |
| Patch element | RO4350B 0.76 mm | 1 | board cost |
Chip cost excluding the phase shifter is ~US$5 per channel; the phase shifter and the Rogers board dominate, consistent with the 12-domain estimate of US$100–300 per channel for complete channels [11]. The LNA must come *before* the DSA and phase shifter (their ~6–10 dB of combined loss would otherwise add directly to NF — Level 3).

## Practical notes
- **Packages**: mmWave SoCs are FCBGA/AiP — design with the vendor's reference layout on the specified RF substrate or buy a module; antenna-on-package parts remove the hardest part (mmWave antenna feed).
- **Supply & thermal**: IWR6843-class parts draw watts during chirps; follow TI's PMIC reference designs (ripple directly degrades phase noise).
- **Software**: TI mmWave SDK / Industrial Toolbox; Infineon Radar SDK; Acconeer SDK (Exploration Tool). Budget time for configuration files and the host-side parser.
- **Regulation**: 24.00–24.25 GHz or 57–64 GHz (≤ 100 mW e.i.r.p.) are the plain SRD options in Singapore; 77–81 GHz is allowed only under the UWB exemption (mean ≤ −3 dBm/MHz, ≥ 500 MHz sweep, not fixed outdoors); power limits are EIRP (antenna gain counts) — [Singapore IMDA rules](../19-regulations-safety/singapore-imda-rules.md).
- **Stock**: most beamformer/phase-shifter ICs are not stocked at LCSC; Mouser/Digikey (SG delivery) and ADI's own store are the realistic sources; allow for export-control screening on some microwave parts (unverified per part).

## Recommended picks for Marcus's use cases
| Use case | Pick | Why |
|---|---|---|
| First radar (speed only) | CDM324/IPM-165 or HB100 + PCM1808 audio ADC | US$10, teaches Doppler |
| Pad-side range/velocity/angle | TI IWR6843 / IWR6843AOP EVM (60 GHz) | legal band, 4 GHz BW, DSP |
| Low-power presence / fine distance | Acconeer XM125 (A121), Infineon BGT60LTR11AIP | tiny, cheap, LCSC stock |
| Learning FMCW chain design | ADF4159 + ADF5901 + ADF5904 + ADAR7251 reference design | classic chipset |
| Learning beamforming | ADI Phaser; KrakenSDR for DF ≤ 1.77 GHz | complete, documented |
| Custom 2.4/5.8 GHz array | HMC649A/PE44820-class shifters + PE43711 DSAs + LNA per element, or ADAR1000 at X/Ku | see [12-domain](../12-phased-arrays/beamforming-architectures.md) |

## Parts to avoid (or use knowingly)
- **ADAR2001/2004 as "beamformers"** — wrong function [14].
- **77–81 GHz radars for field use in Singapore** without checking the UWB conditions (mean e.i.r.p. density ≤ −3 dBm/MHz, sweep ≥ 500 MHz, no fixed outdoor installation) [8].
- **Chip-down mmWave SoCs on FR-4 without the reference stackup** — antenna/feed performance collapses.
- **Doppler modules for rocket altitude** — no range; use GNSS/baro and treat radar as independent velocity truth near the pad.

## Common mistakes & misconceptions
- *"More bits of phase = better array."* Beyond 5–6 bits, calibration, coupling and amplitude errors dominate (example 2).
- *"A 24 GHz module measures distance."* Single-frequency CW modules measure radial speed only.
- *"Radar SoC TX power is the EIRP."* EIRP adds antenna gain; SRD limits apply to EIRP.

## How to simulate / verify
```python
import math
c = 3e8
dR = lambda B: c/(2*B); fd = lambda v, f: 2*v*f/c
print(dR(250e6), dR(4e9), fd(50, 24.125e9), fd(250, 61e9))
s = math.radians(4.5); N = 8
print(-10*math.log10(math.exp(-s*s)), 10*math.log10(s*s/N))     # 0.027 dB, -31 dB
```
- Array pattern with errors: Monte-Carlo the array factor with random phase errors ([array factor](../12-phased-arrays/array-factor-linear-arrays.md)); radar chirp design with the vendor sensing estimator (TI) or a Python FMCW simulation ([FMCW radar](../11-radar/fmcw-radar.md)).

## Open questions / gaps
- EVM prices (TI, Infineon) not verified; ADAR1000/ADTR1107 current distributor prices not captured.
- IWRL6432 TX/RX channel count and BGT24LTR11 details beyond TX power not verified here.
- A121 exact power figures not captured (datasheet not read).

## Sources
1. Texas Instruments, *IWR6843 single-chip 60–64 GHz mmWave sensor* datasheet, https://www.ti.com/lit/ds/symlink/iwr6843.pdf, p. 1. (datasheet)
2. Texas Instruments, *IWR6843AOP* datasheet, https://www.ti.com/lit/ds/symlink/iwr6843aop.pdf, p. 1. (datasheet)
3. Texas Instruments, *AWR1843 single-chip 76–81 GHz automotive radar sensor* datasheet, https://www.ti.com/lit/ds/symlink/awr1843.pdf, p. 1. (datasheet)
4. Texas Instruments, *IWRL6432 single-chip 57–64 GHz low-power mmWave sensor* datasheet, https://www.ti.com/lit/ds/symlink/iwrl6432.pdf, p. 1. (datasheet)
5. Infineon, *BGT60TR13C* data sheet v2.4.9 and product page (via search extract), https://www.infineon.com/part/BGT60TR13C. (datasheet, secondary extract)
6. LCSC listing for BGT60LTR11AIPE6327XUMA2 (61–61.5 GHz, 10 dBm, 128 mA TX), https://www.lcsc.com/product-detail/C3606906.html. (distributor data)
7. Acconeer, *A121 Pulsed Coherent Radar datasheet* v1.5 (Mouser mirror) and product pages (via search extract), https://www.mouser.com/datasheet/2/1126/A121_datasheet-3133196.pdf. (datasheet, secondary extract)
8. This KB: [DIY radar hardware](../11-radar/diy-radar-hardware.md) (IMDA TS SRD Sep 2023 radar bands; 77–81 GHz via IMDA TS UWB 2016) and [Singapore IMDA rules](../19-regulations-safety/singapore-imda-rules.md). (internal)
9. Analog Devices ADF4159 / ADF5901 / ADF5904 / ADAR7251 product information via LCSC parametrics and search extracts (ADI site not reachable by script). (manufacturer/distributor, secondary)
10. Local JLCPCB/LCSC parts database (jlcparts in-stock snapshot, newest record 2026-04-01) via `jlc-trawler`; LCSC product-page parametrics (fetched 2026-09-29). (distributor data)
11. This KB: [Phase shifters and TTD components](../12-phased-arrays/phase-shifters-ttd-components.md) and [DIY phased-array projects](../12-phased-arrays/diy-phased-array-projects.md) (W2-B5) — ADAR1000/ADTR1107, HMC64x, PE44820, QPC2108, ADAR4002, JSPHS-2484+, Phaser, KrakenSDR. (internal)
12. Anokiwave, *AWMF-0108 26–30 GHz single-pol quad beamformer IC* product page / Microwave Journal (2016) (via search extract), https://www.anokiwave.com/products/awmf-0108/. (manufacturer, secondary extract)
13. Qorvo, *Qorvo to Acquire Anokiwave* (press release, Jan 2024) and Qorvo FY2024 10-K (completion 5 Feb 2024, US$93.7 M), https://www.qorvo.com/newsroom/news/2024/qorvo-to-acquire-anokiwave. (corporate filing)
14. Analog Devices, *ADAR2001* and *ADAR2004* data sheets (via search extract), https://www.analog.com/media/en/technical-documentation/data-sheets/adar2001.pdf, …/adar2004.pdf. (datasheet, secondary extract)
15. This KB: [DIY radar hardware](../11-radar/diy-radar-hardware.md) — HB100 and IPM-165/CDM324 specifications. (internal)
16. Infineon, *BGT24LTR11* application note AN615 / product page (TX ≈ 6 dBm typ.) (via search extract). (application note, secondary extract)
