# 07-noise-linearity — Noise, linearity and receiver budgets

What limits a receiver at the bottom (noise) and at the top (distortion), and how to budget both through a chain of real stages. Covers thermal (Johnson–Nyquist) noise and noise temperature including antenna/sky/man-made noise (ITU-R P.372); noise figure and the Friis cascade, noise matching and mixer SSB/DSB figures; shot and flicker noise and why they matter in zero-IF receivers and oscillators; oscillator phase noise, jitter, reciprocal mixing and ADC clock limits; nonlinearity (compression, IP2/IP3, intermodulation, cross-modulation, AM–PM); dynamic range, SFDR, blocking, selectivity, ADC noise figure and AGC; full cascade budgets with a reusable Python tool; and sensitivity/MDS including LoRa's negative-SNR operation. Circuit design of LNAs, mixers, VCOs and PLLs lives in [06-rf-circuits](../06-rf-circuits/_index.md); LoRa PHY details in [15-lora-ism-radios](../15-lora-ism-radios/_index.md); BER/Eb/N0 theory in [10-comms-modulation](../10-comms-modulation/_index.md); noise-figure and phase-noise measurement in [17-test-measurement](../17-test-measurement/_index.md). Every numeric claim on these pages is reproduced by a script in `tools/verify/noise_*.py`.

## Reading order (beginner → advanced)
1. [Thermal noise and noise temperature](thermal-noise-and-noise-temperature.md) — kTB, −174 dBm/Hz, noise temperature, antenna temperature, P.372 external noise, lossy passives.
2. [Noise figure and the Friis cascade](noise-figure-and-friis.md) — F/NF/Te, cascade derivation, why the LNA goes first, SSB vs DSB, noise parameters and circles.
3. [Sensitivity and MDS](sensitivity-and-mds.md) — the sensitivity formula, LoRa's thresholds and Eb/N0, the bit-rate rule, the EBYTE datasheet contradiction, GNSS C/N0.
4. [Nonlinearity: P1dB, IP3, intermodulation](nonlinearity-p1db-ip3-intermod.md) — power series, two-tone products, 9.6 dB rule and its failures, cascaded IIP3, IM3 channel coincidences.
5. [Dynamic range, SFDR and blocking](dynamic-range-sfdr-blocking.md) — SFDR, blocking/ACR, desensitisation, ADC noise figure and processing gain, co-sited transmitters, AGC.
6. [Receiver cascade analysis](receiver-cascade-analysis.md) — full budgets and level diagrams for 915/433 MHz ground stations and a GNSS active antenna; `noise_cascade.py`.
7. [Phase noise and jitter](phase-noise-and-jitter.md) — L(f), integration to jitter, ADC SNR, Leeson, reciprocal mixing, PLL shaping, EVM, FMCW range correlation.
8. [Shot and flicker noise](shot-and-flicker-noise.md) — 2qI, 1/f corners, zero-IF penalty, oscillator up-conversion, Allan-deviation flicker floor.

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [thermal-noise-and-noise-temperature](thermal-noise-and-noise-temperature.md) | Nyquist derivation, Planck form, kTB table, v_n = √(4kTRB), Te, lossy passive Te = (L−1)Tp, antenna temperature integral, P.372 man-made/galactic noise vs f, noise bandwidth, Gaussian statistics, −2.5 dB log-average bias | mixed | high |
| [noise-figure-and-friis](noise-figure-and-friis.md) | IEEE noise factor, Friis 1944 derivation and assumptions, loss-before-LNA, SSB/DSB mixers, Rothe–Dahlke vn–in model, Fmin/Rn/Γopt, noise circles, noise vs conjugate match, P.372 operating noise factor | mixed | high |
| [sensitivity-and-mds](sensitivity-and-mds.md) | sensitivity/MDS definitions, SX126x table reproduction (NF ≈ 6 dB, Eb/N0 ≈ 6 dB), −2.5 dB/SF derivation, bit-rate floor, EBYTE −147 dBm claim refuted, FSK comparison, GNSS sensitivity ↔ C/N0 | mixed | high |
| [nonlinearity-p1db-ip3-intermod](nonlinearity-p1db-ip3-intermod.md) | power series, full two-tone product table, P1dB/IIP3/IIP2 closed forms, 9.64 dB and why it fails (tanh 8.96, sweet spot 13.5, no-cubic 5:1), cascaded IIP3, XMOD, blocking gain, AM–PM, harmonics (E22 3rd harmonic vs GPS L2), PIM | mixed | high |
| [dynamic-range-sfdr-blocking](dynamic-range-sfdr-blocking.md) | SFDR derivation, compression DR, SX1262 blocking/ACR/CCR reading, desense budget, ADC NF (MT-052 method), processing gain, gain before ADC, co-site transmitter, pre-selection, AGC | intermediate | high |
| [receiver-cascade-analysis](receiver-cascade-analysis.md) | per-stage recursion, assumptions, level diagram, 915 MHz A1–A3 and 433 MHz B1–B2 station chains, GNSS active antenna chain with C/N0, reusable Python API | intermediate | high |
| [phase-noise-and-jitter](phase-noise-and-jitter.md) | L(f) = Sφ/2, jitter integration (58 fs vs 170 fs example), SNR vs jitter, Leeson (and 6 dB variant), reciprocal mixing, SX1262 LO inference, PLL in-band floor, EVM, FMCW range correlation, vibration | mixed | high |
| [shot-and-flicker-noise](shot-and-flicker-noise.md) | Poisson derivation of 2qI, shot/thermal 50 mV crossover, BJT en, flicker models, per-decade integral, zero-IF penalty for LoRa BW125, oscillator 1/f³, Allan flicker floor, popcorn/g-r/avalanche noise | intermediate | high |
| [volterra-series-and-nonlinear-analysis](volterra-series-and-nonlinear-analysis.md) | Volterra kernels, 3/4 factor, method of nonlinear currents, IIP3 vs tone spacing (+3.5 → −12.6 dBm for a bypassed-RE BJT), IM3 asymmetry, sweet spot, truncation limits, AM–PM, Saleh/Rapp/memory polynomial, DPD | advanced | medium |

## Domain FAQ (top questions → page#section)
- *Where does −174 dBm/Hz come from?* → [thermal noise § Level 2](thermal-noise-and-noise-temperature.md#level-2--derivations)
- *How much noise is in a 125 kHz LoRa channel?* → [thermal noise § Worked example 1](thermal-noise-and-noise-temperature.md#worked-examples)
- *Why is receiver NF irrelevant at HF but vital for GNSS?* → [thermal noise § External noise: ITU-R P.372](thermal-noise-and-noise-temperature.md#external-noise-itu-r-p372)
- *Why must the LNA go at the antenna?* → [Friis § Level 2 (d)](noise-figure-and-friis.md#level-2--derivations) and [cascade § Example A](receiver-cascade-analysis.md#example-a--915-mhz-lora-ground-station-secondary-link-e220-900t30dsx1262-class-receiver)
- *What are Fmin, Rn and Γopt?* → [Friis § Level 3](noise-figure-and-friis.md#level-3--noise-parameters-noise-matching-and-circles)
- *Is the EBYTE "−147 dBm at 2.4 kbps" real?* → [sensitivity § Level 3](sensitivity-and-mds.md#level-3--the-ebyte-claim-error-criteria-and-gnss)
- *How can LoRa work below the noise floor?* → [sensitivity § Level 2](sensitivity-and-mds.md#level-2--loras-thresholds-and-the-bit-rate-rule)
- *Is IIP3 always P1dB + 9.6 dB?* → [nonlinearity § Level 3](nonlinearity-p1db-ip3-intermod.md#level-3--cascades-reality-and-limits-of-the-model)
- *Can two other transmitters create a signal on my channel?* → [nonlinearity § Worked example 1](nonlinearity-p1db-ip3-intermod.md#worked-examples)
- *What is SFDR and how does an LNA change it?* → [dynamic range § Worked example 1](dynamic-range-sfdr-blocking.md#worked-examples)
- *What is the noise figure of an ADC, and how much gain does an SDR need?* → [dynamic range § Level 2](dynamic-range-sfdr-blocking.md#level-2--derivations)
- *How do I convert a phase-noise plot to jitter?* → [phase noise § Level 2 (b)](phase-noise-and-jitter.md#level-2--derivations)
- *What is reciprocal mixing?* → [phase noise § Level 2 (e)](phase-noise-and-jitter.md#level-2--derivations)
- *Why do zero-IF receivers struggle with narrow channels?* → [shot and flicker § Level 3](shot-and-flicker-noise.md#level-3--where-each-matters-in-rf-and-limits)
- *What C/N0 should my GNSS active antenna give?* → [cascade § Example C](receiver-cascade-analysis.md#example-c--gnss-l1-active-antenna)

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
Pozar *Microwave Engineering* (ch. 10, 12); Razavi *RF Microelectronics* (ch. 2, 4, 8); Lee *The Design of CMOS RF ICs* (ch. 11–13, 18); Friis 1944; Johnson/Nyquist 1928; Leeson 1966; Haus et al. 1960 (IRE noise standard); ITU-R P.372; Keysight AN 57-1/57-2; ADI MT-008 and MT-052; Semtech SX1261/2 datasheet.

## Known gaps
- Effective NF, IIP3 and input P1dB of the EBYTE E22/E220 modules (with integrated LNA) are unpublished — measure (Y-factor, two-tone).
- EBYTE air-rate → SF/BW mapping unknown (so the "real" 2.4 kb/s sensitivity is a physics-based estimate, −127 to −129 dBm).
- Man-made noise at 433/868/915 MHz measured at modern launch sites and in Singapore; quiet-Sun ΔTa for tracking Yagis.
- ADI MT-008/MT-052 were cited but could not be re-fetched this session (server timeouts); formulas were independently derived and verified.
- Crystal g-sensitivity and vibration-induced phase noise on the flight computer (TCXO data needed).
- Real LNA/SAW part data for the example chains (domain 18).
