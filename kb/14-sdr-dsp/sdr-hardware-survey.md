---
title: SDR hardware survey — RTL-SDR, Airspy, SDRplay, HackRF, Pluto, LimeSDR, bladeRF, USRP, KrakenSDR, AntSDR, RX888 — and how to choose
domain: 14-sdr-dsp
slug: sdr-hardware-survey
tags: [sdr, hardware, rtl-sdr, r820t2, r828d, airspy, sdrplay, hackrf, pluto, ad9361, ad9363, ad9364, limesdr, lms7002m, bladerf, usrp, b210, krakensdr, antsdr, rx888, noise-figure, dynamic-range, coherent, full-duplex, selection]
prerequisites: [sampling-aliasing-bandpass-sampling.md, iq-complex-baseband.md, ../07-noise-linearity/noise-figure-and-friis.md, ../07-noise-linearity/dynamic-range-sfdr-blocking.md]
related: [gnu-radio-and-software-stack.md, fpga-for-sdr.md, multirate-dsp-decimation-cic.md, nco-ddc-duc.md, software-demodulation.md, ../15-lora-ism-radios/ground-station-design.md, ../17-test-measurement/sdr-as-test-equipment.md, ../18-components-parts/adcs-dacs-for-sdr.md, ../18-components-parts/rf-transceiver-ics.md, ../11-radar/diy-radar-hardware.md, ../12-phased-arrays/adaptive-beamforming-doa.md, ../12-phased-arrays/diy-phased-array-projects.md, ../06-rf-circuits/receiver-architectures.md]
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# SDR hardware survey — and how to choose one

## Questions this page answers
- Which SDR should I buy to monitor my rocket's 433 MHz LoRa telemetry, record a flight, or build a ground station?
- What do the specs mean — "14-bit", "10 MHz bandwidth", "NF 3.5 dB" — and which ones are marketing?
- Which SDRs can transmit, which are full duplex, and which have phase-coherent multiple channels?
- Can a Pluto really do 70 MHz–6 GHz? Is the hack safe?
- What SDR do I need for an FMCW radar, direction finding (DOA), or a small phased array?
- Why is my RTL-SDR V4 hard to buy now, and what replaced it?
- How much USB bandwidth / disk do I need for recording?
- Does the SDR's noise figure matter if I put an LNA in front?

## TL;DR
- **Receive-only, cheap (LoRa monitoring, recording, GNSS L1 experiments)**: **RTL-SDR Blog V3 or V4L** (~US$35–40; 8-bit, 2.4 MS/s stable — up to ≈ 2.56 MS/s without drops; measured NF 5.4 dB at 437 MHz on a V3 [1]). The V4 (R828D) is **end of line**; its successor **V4L** uses the R828S with less front-end filtering (better sensitivity, V3-like two-tone behaviour) [6], [7]. Put an LNA + SAW filter at the antenna: system NF ≈ 1–3 dB regardless of the SDR (script).
- **Better receivers**: Airspy R2/Mini (12-bit ADC, 10/6 MHz; *vendor* NF 3.5 dB vs *measured* 7.0–7.9 dB at 435 MHz [2], [1]); SDRplay RSPdx-R2/RSP1B/RSPduo (1 kHz–2 GHz, 10 MHz, many preselection filters; "14-bit" only at ≤ 6.048 MS/s); Airspy HF+ Discovery (HF/VHF, very high dynamic range, 660 kHz span); RX888 MkII (16-bit direct HF sampling to 64 MHz).
- **Transmit + receive**: HackRF One/Pro (1 MHz/100 kHz–6 GHz, 20 MS/s, 8-bit, **half duplex**, NF ≈ 11 dB at 435 MHz without an LNA [2]); **ADALM-Pluto** (AD9363, 325–3800 MHz, 20 MHz, 12-bit, full duplex, ~US$250; USB 2 limits sustained streaming to ≈ 4–12 MS/s depending on host); LimeSDR Mini 2.0 (LMS7002M); bladeRF 2.0 micro (AD9361, 2×2, 47 MHz–6 GHz, 56 MHz, USB 3); **USRP B200/B210** (AD9364/AD9361, 70 MHz–6 GHz, 56 MHz, B210 2×2 coherent, GPSDO option; US$1.5k/2.4k); AntSDR E200 (AD9363/AD9361 + Zynq, Gigabit Ethernet).
- **Coherent multichannel for DOA**: KrakenSDR (5 × R820T2 on one clock with a built-in noise source for automatic phase calibration, ~US$750); B210 (2 ch); bladeRF 2.0 (2 ch); Pluto Rev C/D second channel (not production-tested).
- **Radar**: needs full duplex with good TX–RX isolation and wide bandwidth: range resolution $c/2B$ = 7.5 m at 20 MHz (Pluto stock), 2.7 m at 56 MHz (AD9361-class). HackRF (half duplex) cannot do CW/FMCW radar alone.
- **Datasheet vs measured**: always prefer independent measurements (Libre Space Foundation evaluation [1], Rowetel [2], KA7OEI [16]). Chip datasheet NFs (AD9361 2 dB at 800 MHz; LMS7002M 2 dB at 0.95 GHz) are *at the chip pins at maximum gain*; board-level measured NFs are typically 4–7 dB.

Derived numbers verified by `tools/verify/dsp_sdr_hardware.py` (all PASS). Specs and prices are as fetched on 2026-09-27 and change often — check the vendor before buying.

## Intuition (no math)
Every SDR is the same three boxes: an **RF front end** (filters, LNA, mixer or tuner) that decides what frequencies it can hear and how well it resists strong neighbours, an **ADC** (and DAC) whose resolution and rate decide how much spectrum you capture at once and how large a range of signal strengths you can hold at the same time, and a **link to the computer** (USB 2/3, Ethernet, PCIe) that decides how many of those samples you can actually keep. A cheap SDR skimps on all three; an expensive one mainly buys dynamic range (strong and weak signals together), bandwidth, transmit capability, multiple synchronised channels and calibration.

For a LoRa ground station, the most important "SDR spec" is often not the SDR at all: a good LNA and filter at the antenna set the noise figure, and the SDR only has to survive the strong signals the filter lets through. For radar and direction finding, what matters is transmit/receive at the same time (full duplex), bandwidth (range resolution), and several receivers sharing one clock (phase coherence).

## The math

### Level 1 — what each spec means
- **Tuning range**: LO range of the tuner/transceiver. Below it, some SDRs use *direct sampling* (RTL-SDR V3 Q-branch 0.5–28.8 MHz) or an *upconverter* (RTL-SDR V4/V4L, SA612 mixer +28.8 MHz) [5], [6].
- **Sample rate vs bandwidth**: complex sampling at $f_s$ gives $f_s$ of span; the usable flat part is ~80 % ([sampling](sampling-aliasing-bandpass-sampling.md)). "Analog bandwidth" (e.g. AD9361 < 200 kHz–56 MHz) is the baseband filter setting.
- **ADC bits vs ENOB**: dynamic range at the ADC is $6.02\,\mathrm{ENOB} + 1.76$ dB, plus processing gain $10\log_{10}(f_s/B)$ in a channel $B$ (complex IQ samples at $f_s$; use $f_s/2B$ for a real ADC — [sampling](sampling-aliasing-bandpass-sampling.md#level-3--the-real-sampler-jitter-aperture-reconstruction-and-edge-cases)) ([dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)). RTL2832U: 8-bit output, ENOB ≈ 7 [3]; "14-bit" SDRplay modes use oversampling/decimation and exist only at ≤ 6.048 MS/s [9].
- **Noise figure (NF)**: noise added by the receiver referred to its input, at a stated gain and frequency ([noise figure](../07-noise-linearity/noise-figure-and-friis.md)).
- **IIP3 / blocking dynamic range**: how strong an interferer can be before intermodulation or desensitisation matters ([nonlinearity](../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md)).
- **Duplex**: *half* = TX or RX at a time (HackRF); *full* = both simultaneously (AD936x, LMS7002M).
- **Coherent channels**: several RX (or TX) paths sharing one LO and one sample clock, so their relative phase is stable (B210, bladeRF 2.0, KrakenSDR).
- **Reference**: TCXO ppm (frequency accuracy and drift), external 10 MHz/PPS inputs (lock to GPSDO for timing and multi-device coherence).

### Level 2 — comparing receivers quantitatively
**Noise figure of the chain.** By Friis, the system NF with an LNA of gain $G_1$ in front is $F = F_1 + (F_{SDR}-1)/G_1$. Script §1, 433 MHz with an RTL-SDR (NF 5.4 dB measured at 437 MHz [1]), LNA NF 0.8 dB/20 dB gain, SAW filter 2 dB loss:

| Chain | System NF |
|---|---|
| SDR alone | 5.40 dB |
| SAW → SDR | 7.40 dB |
| LNA → SAW → SDR | **0.96 dB** |
| SAW → LNA → SDR (better against strong out-of-band signals) | 2.89 dB |

With ≥ 20 dB of low-noise gain in front, the SDR's own NF hardly matters — spend money on the masthead LNA and filter ([ground station](../15-lora-ism-radios/ground-station-design.md), [LNA design](../06-rf-circuits/lna-design.md)). What still matters is the SDR's **linearity and ADC headroom**, because the LNA's gain raises every interferer too.

**In-channel dynamic range (ADC-limited).** Script §2: RTL-SDR (ENOB ≈ 7, 2.4 MS/s) → 43.9 dB + 12.8 dB processing gain (complex, 2.4 MS/s) to 125 kHz = **56.7 dB**; Airspy R2 (vendor ENOB 10.4, 10 MS/s) → 83.4 dB; AD936x-class (ENOB ≈ 11 assumed) at 4 MS/s → 83 dB. These are upper bounds set by the converter; tuner compression, AGC and reciprocal mixing (LO phase noise) reduce them. The tuner gain setting slides this window up and down in absolute power ([dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md) Example 3).

**Measured noise figures (independent, lowest NF over gain settings)** — Libre Space Foundation evaluation [1] at 145 / 437 / 1280 MHz (and 2.25 / 2.425 / 5.83 GHz where supported), Rowetel [2] at 435 MHz:

| SDR | NF (dB) [1] | NF at 435 MHz [2] (no LNA → with 1 dB-NF, 20 dB LNA) |
|---|---|---|
| RTL-SDR V3 | 5.8 / 5.4 / 11.9 | — |
| Airspy Mini | 7.1 / 7.4 / 10.7 | 7.9 → 2.0–2.2 |
| Airspy R2 | — | 7.0 → 1.7 |
| SDRplay RSPduo | 2.1 / 2.5 / 5.4 | — |
| HackRF One | — | 11.1 → 2.6–3.4 |
| ADALM-Pluto | 6.2 / 6.1 / 4.1 / 4.7 / 5.0 / 9.3 | — |
| USRP B210 | 5.5 / 4.4 / 5.7 / 4.8 / 6.3 / 9.6 | — |
| bladeRF 2.0 micro | 5.0 / 4.9 / 7.4 / 9.0 / 9.5 / 15.8 | — |
| LimeSDR Mini (v1) | 11.1 / 13.8 / 15.6 (unit possibly damaged [1]) | — |

Rowetel notes that a different USB port or a loose connector shifted results by ≥ 1 dB [2] — measurement setup matters as much as the device.

### Level 3 — architecture consequences
- **Tuner-based receivers** (RTL-SDR, Airspy, SDRplay, KrakenSDR): a TV-tuner or broadcast-tuner IC (R820T2/R828D/R828S, Mirics MSi001) + a single ADC; low-IF or zero-IF ([IQ](iq-complex-baseband.md)). The R820T datasheet quotes NF 3.5 dB, image rejection 65 dBc, max input +10 dBm and 42–1002 MHz nominal range (extended in practice) [4]. Front-end filtering (RTL-SDR V4's triplexer and broadcast notches; SDRplay's 11–12 band filters) is the main difference between models [6], [9], [10].
- **Integrated transceivers** (AD9361/3/4, LMS7002M): zero-IF RF-to-bits chips with 12-bit converters, full duplex, programmable analogue filters and digital decimation chains ([multirate Example 3](multirate-dsp-decimation-cic.md)). AD9361 datasheet (Rev E) at maximum gain: NF 2 dB / IIP3 −18 dBm / IIP2 40 dBm at 800 MHz; 3 dB / −14 dBm / 45 dBm at 2.4 GHz; 3.8 dB / −17 dBm / 42 dBm at 5.5 GHz; TX up to 8 / 7.5 / 6.5 dBm with EVM ≤ −40 dB [11]. AD9363 = the same family limited to 325–3800 MHz and 20 MHz (NF 3 dB, EVM −34 dB); AD9364 = 1×1 AD9361 [12], [13]. LMS7002M: 100 kHz–3.8 GHz, NF 2.0/2.5/3.5 dB at 0.95/2/3.8 GHz, IIP3 +4 dBm (out-of-band two-tone at ~50 dB gain) [14].
- **HackRF** is a superheterodyne-plus-zero-IF hybrid: RFFC5072 mixer/synthesiser to a 2.3–2.7 GHz IF, MAX2837 (MAX2839 on r9) zero-IF transceiver, MAX5864 8-bit converters [15]. Its MAX2837 baseband filter has a 1.75 MHz minimum bandwidth with only ≈ 33 dB rejection at ±2 MHz, so sample at ≥ 8 MS/s and decimate in software to avoid aliasing [Common mistakes 5]. HackRF Pro (2025) replaces the CPLD with an FPGA, adds a TCXO and USB-C, extends coverage to 100 kHz–6 GHz (tunable 0–7.1 GHz), removes the DC spike, and offers a 16-bit low-rate mode (ENOB 9–11) and a 4-bit mode to 40 MS/s [15].
- **Direct-sampling HF** (RX888 MkII: LTC2208 16-bit at up to 130 MS/s, HF to 64 MHz, plus an R828D tuner above): noise floor ≈ −155 dBm/Hz with +20 dB gain (clipping at −18 dBm) or −140 dBm/Hz at 0 dB (clipping +3 dBm) [16] — i.e. ≈ 19 dB system NF at high gain (script §6), fine at HF where atmospheric noise dominates; spurs at 8/16/24 MHz, needs an external low-pass filter, driver support described as poor [17].
- **Host link**: bytes per complex sample: cu8/sc8 = 2, sc16 = 4, fc32 = 8. Script §3: RTL-SDR 2.4 MS/s = 4.8 MB/s (17.3 GB/h); HackRF 20 MS/s = 40 MB/s (the practical USB 2 limit); Pluto sc16 at 4 MS/s = 16 MB/s; 61.44 MS/s sc16 = 246 MB/s (USB 3 or Ethernet/PCIe only). The Pluto streaming limit is disputed: ADI's wiki says up to 4 MS/s without drops [18], PySDR ≈ 5 MS/s continuous, the LSF evaluation 7.5–12 MS/s depending on host [1] — test on *your* computer ([software stack](gnu-radio-and-software-stack.md)).
- **Clocking and coherence**: TCXO accuracy RTL-SDR Blog 1 ppm (2 ppm initial) [8]; Airspy/SDRplay 0.5 ppm; Pluto 25 ppm XO [1] (Rev C/D add external clock in/out); B200/B210 ±2 ppm, GPSDO option (< 1 ppb locked), external 10 MHz + PPS [19]. A coherent array needs shared LO *and* ADC clock plus a phase-calibration method (KrakenSDR's switched noise source) — see [array calibration](../12-phased-arrays/array-calibration.md).

## Design equations & rules of thumb

| Rule | When valid | Typical values |
|---|---|---|
| $F_{sys} = F_{LNA} + (F_{SDR}-1)/G_{LNA}$ | LNA ahead of SDR | 0.8 dB LNA + 20 dB → ≈ 1 dB |
| In-channel DR ≈ $6.02\,\mathrm{ENOB}+1.76+10\log_{10}(f_s/B)$ | ADC-limited, complex IQ at $f_s$ (real ADC: $f_s/2B$) | RTL 57 dB, 12-bit ~83 dB at 125 kHz |
| Data rate = $f_s\times$ bytes/sample | host link, disk | cu8 2, sc16 4, fc32 8 B |
| USB 2 practical ≈ 35–40 MB/s | streaming | HackRF 20 MS/s × 2 B |
| $\Delta R = c/2B$ | FMCW/pulse radar | 20 MHz: 7.5 m; 56 MHz: 2.7 m |
| Stay ≤ ~2.56 MS/s on RTL-SDR | avoid dropped samples | 3.2 MS/s max "unstable" [3] |
| HackRF: sample ≥ 8 MS/s, decimate | MAX2837 filter ≥ 1.75 MHz | [15] |
| Prefer measured NF over datasheet | board vs chip | chip 2–3 dB; boards 4–7 dB |

## Device tables

**Receive-only** (specs from manufacturer pages unless marked; prices as of 2026-09):

| Device | Coverage | Span / rate | ADC | Front end | NF | Clock | Link | Price (USD) |
|---|---|---|---|---|---|---|---|---|
| RTL-SDR Blog V3 [5], [8] | 0.5–1766 MHz (HF by direct sampling) | 2.4 MS/s (3.2 max, ~2.56 stable) | RTL2832U 8-bit (ENOB ~7) | R820T2 low-IF | 5.4 dB @437 MHz [1] | 1 ppm TCXO | USB 2 | 35–40 |
| RTL-SDR Blog V4 [6], [7] | 0.5–1766 MHz (HF upconverter) | same | same | R828D, triplexer, AM/FM/DAB notches | "2–3 dB less sensitive on some bands" than V3 [6] | 1 ppm | USB 2 | EOL (was 30–45) |
| RTL-SDR Blog V4L (2026) [7] | same as V4 | same | same | R828S, diplexer, no notches | better than V4; two-tone ≈ V3 | 1 ppm | USB 2 | 38 |
| Airspy R2 [20] | 24–1700 MHz | 10 MS/s (9 MHz alias-free) | 12-bit @ 20 MS/s | R820T2/R860 | vendor 3.5 dB; 7.0 dB measured [2] | 0.5 ppm, ext. ref | USB 2 | 169 |
| Airspy Mini [20] | 24–1700 MHz | 3/6/10 MS/s (6 MHz) | 12-bit | R820T2 | 7.1–10.7 dB [1] | 0.5 ppm | USB 2 | 99 |
| Airspy HF+ Discovery [20] | 0.5 kHz–31 MHz, 64–260 MHz | 768 kS/s (660 kHz) | 2 × ΣΔ @ 36 MS/s, 18-bit DDC | polyphase harmonic-rejection | MDS −140 dBm/500 Hz (vendor) | 0.5 ppm | USB | 169 |
| SDRplay RSP1B / RSPdx-R2 [9], [10] | 1 kHz–2 GHz | ≤ 10 MHz | "14-bit" ≤ 6.048 MS/s, 12 ≤ 8.064, 10 ≤ 9.216, 8 above | 11–12 preselection filters | RSPdx-R2 typ. 2.6/2.1/6.0/3.1/4.4 dB @ 100/200/340/660/1500 MHz [10] | 0.5 ppm | USB 2 | ~135 (£106 ex-VAT, converted) / 240 |
| SDRplay RSPduo [9] | 1 kHz–2 GHz, 2 tuners | 10 MHz (1 tuner) | same | dual tuner | 2.1/2.5/5.4 dB [1] (best in test; weak close-in blocking) | 24 MHz ref in/out | USB 2 | ~270 (£214 ex-VAT, converted) |
| KrakenSDR [21] | 24–1766 MHz | 2.56 MHz/ch × 5 | 5 × RTL2832U | 5 × R820T2, common clock, noise-source cal | ≈ RTL-SDR | 1 ppm | USB-C (hub), Pi 4/5 | 749–775 |
| RX888 MkII [16], [17] | HF direct to 64 MHz; R828D to ~1.8 GHz | 64 MHz (HF) | LTC2208 16-bit 130 MS/s | attenuator + VGA | ≈ 19 dB at +20 dB gain (derived) | ext. 27 MHz ref | USB 3 | ~170 |
| FobosSDR [22] | 100 kHz–6 GHz | 50 MHz | 14-bit | RFFC5072 + MAX2830 | — | clock in/out | USB 3 | 395 |

**Transceivers**:

| Device | Coverage | BW / rate | Converters | RF chip | TX power | Channels / duplex | Clock | Link | Price (USD) |
|---|---|---|---|---|---|---|---|---|---|
| HackRF One [15] | 1 MHz–6 GHz | 2–20 MS/s | 8-bit | RFFC5072 + MAX2837/2839 | 5–15 dBm ≤ 2170 MHz; 0–5 dBm 2.74–4 GHz; −10–0 dBm 4–6 GHz | 1, half | 10 MHz in/out | USB 2 | 340 |
| HackRF Pro (2025) [15] | 100 kHz–6 GHz | 20 MS/s (4-bit to 40) | 8-bit; 16-bit low-rate | FPGA, no DC spike | — | 1, half | TCXO | USB-C (HS) | 400 |
| ADALM-Pluto [18] | 325–3800 MHz (AD9364 hack 70–6000) | ≤ 20 MHz; 65.1 kS/s–61.44 MS/s | 12-bit | AD9363 + Zynq-7010 | 3.7–8.4 dBm measured [1] | 1T1R (2T2R on Rev C/D, untested), full | 25 ppm; Rev C/D ext. clock | USB 2 | 250 |
| LimeSDR Mini 2.0 [23] | 10 MHz–3.5 GHz | 30.72 MS/s | 12-bit | LMS7002M + ECP5 | ≤ 10 dBm | 1T1R, full | ±1 ppm initial | USB 3 | 600 |
| LimeSDR USB [23] | 100 kHz–3.8 GHz | 61.44 MS/s | 12-bit | LMS7002M | 0–10 dBm | 2×2, full | ±1 ppm | USB 3 | 699 |
| bladeRF 2.0 micro xA4/xA9 [24] | 47 MHz–6 GHz | 56 MHz, 61.44 MS/s (122.88 MS/s 8-bit mode, out of chip spec [25]) | 12-bit | AD9361 + Cyclone V | +8 dBm claimed | 2×2, full | VCTCXO, PLL tame | USB 3 | 540 / 860 |
| USRP B200 / B210 [19] | 70 MHz–6 GHz | 56 MHz (1×1), 30.72 MHz (2×2), 61.44 MS/s | 12-bit | AD9364 / AD9361 | > 10 dBm spec | 1×1 / 2×2 coherent, full | ±2 ppm; GPSDO; 10 MHz + PPS | USB 3 | 1462 / 2387 |
| AntSDR E200 [26] | AD9363 or AD9361 ranges | 61.44 MS/s | 12-bit | AD936x + Zynq-7020 | — | 2×2, full | ±2 ppm VCXO, 10 MHz/PPS in | GbE (libiio + UHD firmware) | 449–729 |
| USRP X310 / N310 / N320 / X410 [27] | up to DC–7.2 GHz | 160–400 MHz/ch | 12–16-bit | daughterboards / AD9371 / RFSoC ZU28DR | — | 2–4 ch | GPSDO, 10 MHz/PPS | 10/100 GbE, PCIe | 11k–33k |

Notes: Pluto's AD9364 "hack" (`fw_setenv attr_val ad9364`) usually works but ADI states there are no specifications outside 325–3800 MHz / 20 MHz and it is not guaranteed on every unit; TX is weaker at the extremes [28]. Clones (Pluto+, LibreSDR) use AD9363 or AD9361 with Ethernet and faster streaming; quality varies [29]. USRP N210 is end of life [27].

## Worked examples

**1 — LoRa ground station at 433.92 MHz (receive and record).** Masthead LNA (NF 0.8 dB, 20 dB) + 433 MHz SAW, coax down, RTL-SDR Blog V3 or V4L at 1–2 MS/s. System NF ≈ 1–3 dB (table above) → noise density ≈ −172 dBm/Hz; for LoRa BW125 the noise floor is −172 + 51 = −121 dBm, so an SF12 packet at −20 dB SNR decodes near −141 dBm (before implementation loss). The SDR's 57 dB in-channel window must hold both that floor and the strongest in-band signal — a nearby 433 MHz SRD or your own ground transmitter can overload it: set RTL-SDR gain manually, below the level where intermodulation appears ([dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)). Recording: 1 MS/s cu8 = 2 MB/s = 7.2 GB/h. Decoding: gr-lora_sdr ([software demod](software-demodulation.md)). For 868/915 MHz, same design with the matching SAW. Upgrade path: Airspy R2 or SDRplay for more dynamic range; a dedicated SX1262 receiver in parallel for live decoding.

**2 — FMCW radar at 2.4 GHz with a Pluto.** Stock AD9363: 20 MHz → $\Delta R$ = 7.5 m; with the AD9364 setting and 56 MHz: 2.7 m (script §4) — but the full rate cannot be streamed over USB 2; generate the chirp from a buffer (DDS/cyclic TX buffer) and capture bursts, or do the dechirp in the FPGA (e.g. Maia SDR-style firmware, [FPGA](fpga-for-sdr.md)). TX–RX leakage on the same board limits sensitivity; use separate antennas with isolation and a high-pass filter on the beat signal ([FMCW radar](../11-radar/fmcw-radar.md), [DIY radar](../11-radar/diy-radar-hardware.md)). ADI's CN0566 "Phaser" kit combines a Pluto with a 10 GHz 8-element beamformer board for exactly this kind of experiment (cited from general knowledge; check ADI's page) — see [phased-array projects](../12-phased-arrays/diy-phased-array-projects.md).

**3 — Direction finding a lost rocket's 433 MHz beacon.** KrakenSDR with a 5-element uniform circular array: at 433.92 MHz, λ/2 = 0.345 m and a chord of λ/2 needs a radius of 0.294 m (script §5). The KrakenSDR's noise source calibrates the five channels' phases at start-up; its software runs MUSIC/Bartlett DOA on a Raspberry Pi ([DOA](../12-phased-arrays/adaptive-beamforming-doa.md)). A cheaper alternative for a single hunter: one RTL-SDR with a Yagi and signal-strength bearings, or a pseudo-Doppler antenna switcher.

**4 — Testing your own LoRa/FSK transmitter's spectrum.** A HackRF or Pluto can *record* your flight radio's output (through a ≥ 40 dB attenuator!) to check deviation, CFO and spurious emissions at a coarse level; it is not a calibrated spectrum analyser (spurs, image, DC spike, uncalibrated amplitude) — see [SDR as test equipment](../17-test-measurement/sdr-as-test-equipment.md).

**5 — Budget ladder for a student lab (2026 prices).** US$40 RTL-SDR V4L (RX, LoRa/ADS-B/GNSS experiments) → US$100–170 Airspy Mini/R2 or SDRplay (better RX) → US$250 Pluto (TX/RX, full duplex, labs, radar demos) → US$340–400 HackRF One/Pro (widest coverage, half duplex) → US$540–860 bladeRF 2.0 / US$750 KrakenSDR (2×2 or 5-ch coherent) → US$1.5–2.4k USRP B200/B210 (reference-grade, GPSDO, UHD ecosystem).

## Practical notes
- **Buy genuine**: counterfeit "V4" RTL-SDRs are V3 clones in V4-style cases [7]; buy from the official store or authorised resellers.
- **RTL-SDR gain**: set manual tuner gain; the RTL2832U digital AGC and tuner AGC are designed for DVB-T and are rarely helpful [30]. V4/V4L need the RTL-SDR Blog driver (or recent Osmocom librtlsdr); direct-sampling mode does nothing on V4 [6].
- **Bias tee**: RTL-SDR Blog (4.5 V, up to 180 mA continuous [6]), Airspy, SDRplay and HackRF can power a masthead LNA over the coax — check current and don't short it.
- **Heat and clocks**: the Pluto's 25 ppm XO drifts as it warms (tens of kHz at 2.4 GHz) — lock it to an external reference (Rev C/D) or correct in software ([NCO](nco-ddc-duc.md)).
- **Maximum input**: HackRF RX −5 dBm; SDRplay RSPdx-R2 0 dBm continuous; R820T +10 dBm (chip) — never connect a transmitter directly; use attenuators and a limiter.
- **Shielding and USB noise**: USB 3 ports radiate around 2.4 GHz; use short shielded cables, ferrites, or USB 2 mode where possible.
- **Know the architecture's artefacts**: zero-IF → DC spike and images ([IQ](iq-complex-baseband.md)); low-IF tuners → images 2×IF away (R820T 65 dBc [4]); 8-bit ADCs → easy overload.
- **SoftRock-class (Tayloe/N-path) receivers:** how the 4-path sampling mixer works and its harmonic responses and noise folding are in [06 mixers § N-path](../06-rf-circuits/mixers.md#level-3--lptv-analysis-conversion-matrices-noise-folding-and-n-path-tayloe-mixers).

## Common mistakes & misconceptions
1. **"More bits = better receiver."** Front-end filtering, LO phase noise and gain distribution often dominate; a well-filtered 8-bit receiver behind an LNA can beat a poorly filtered 12-bit one near strong signals.
2. **"The datasheet NF is what I get."** Chip-level NFs (2–3 dB) are at maximum gain at the chip; measured board NFs are 4–11 dB. Put an LNA in front for weak signals.
3. **"Pluto does 70 MHz–6 GHz."** Only with the unsupported AD9364 setting, with no performance guarantee [28].
4. **"HackRF can do radar."** It's half duplex; CW/FMCW radar needs simultaneous TX/RX (or two devices sharing a clock).
5. **Sampling a HackRF at 2 MS/s** — its analogue filter can't go below 1.75 MHz, so strong signals just outside the span alias in; sample at 8+ MS/s and decimate [15].
6. **Expecting 61.44 MS/s over USB 2** — Pluto streams a few MS/s continuously; use bursts or on-board processing.
7. **Assuming multiple cheap SDRs are coherent** — separate crystals drift; you need a shared clock and calibration (KrakenSDR solves both).
8. **Believing "14-bit" at any rate** (SDRplay) — only at ≤ 6.048 MS/s [9].

## How to simulate / verify
- `python3 tools/verify/dsp_sdr_hardware.py`: Friis cascades for the ground-station chain, ADC-limited in-channel dynamic range, host data rates, FMCW resolution, KrakenSDR geometry, RX888 implied NF. All PASS.
- **Measure your own SDR** (domain 17): NF with a noise source (Y-factor) or a calibrated generator at MDS; two-tone IIP3 with two generators and a combiner; image rejection with a CW tone and its mirror ([IQ](iq-complex-baseband.md)); dropped-sample test by streaming a counter or checking driver overflow counts ([software stack](gnu-radio-and-software-stack.md)).

## Open questions / gaps
- No independent IIP3/blocking numbers were found for most SDRs (the LSF report gives blocking only as plots [1]); dynamic-range comparisons here rely on ADC ENOB and qualitative reports.
- SDRplay RSP1B/RSPdx-R2 chip set and exact ADC behaviour at each rate: from vendor pages; the RSP1B datasheet link was dead.
- HackRF One IF (2.3–2.7 GHz) and crystal accuracy, Pluto+ and LibreSDR performance, RX888 VCXO accuracy: unverified.
- The RTL-SDR V4 end-of-line post's date was not confirmed in the fetched copy (the V4L went on sale around Aug 2026).
- Prices change quickly; figures are snapshots from vendor pages (2026-09).

## Sources
1. A. Csete, S. Christiansen (Libre Space Foundation), "Evaluation of SDR Boards and Toolchains," v1.0 (2020-03-20), https://gitlab.com/librespacefoundation/sdrmakerspace/sdreval/-/raw/master/Report/pdf/Evaluation_of_SDR_Boards-1.0.pdf. (independent measurement report) — NF by MDS and Y-factor; Pluto/B210/bladeRF/Lime/RTL/Airspy/RSPduo; Pluto throughput, TX power, clock ppm.
2. D. Rowe, "Measuring SDR Noise Figure in Real Time," Rowetel blog (2018-03-12), https://www.rowetel.com/wordpress/?p=5867. (independent measurement) — NF at 435 MHz with and without LNA.
3. RTL-SDR.com, "About RTL-SDR," https://www.rtl-sdr.com/about-rtl-sdr/ (manufacturer/community) — 3.2 MS/s max, 2.56 MS/s without drops, ENOB ~7.
4. Rafael Micro, R820T preliminary datasheet (2011; copy hosted by rtl-sdr.com), https://rtl-sdr.com/wp-content/uploads/2013/04/R820T_datasheet-Non_R-20111130_unlocked.pdf. (datasheet, unofficial copy) — 42–1002 MHz, NF 3.5 dB, 65 dBc image rejection, +10 dBm max input, 3.57/4.57 MHz IF.
5. RTL-SDR Blog, "RTL-SDR Blog V3 dongles user guide," https://www.rtl-sdr.com/rtl-sdr-blog-v-3-dongles-user-guide/ (manufacturer) — direct sampling 0.5–28.8 MHz, bias tee.
6. RTL-SDR Blog, "RTL-SDR Blog V4 dongle initial release" (2023-08), https://www.rtl-sdr.com/rtl-sdr-blog-v4-dongle-initial-release/ and https://www.rtl-sdr.com/v4/ (manufacturer) — R828D, triplexer, notches, upconverter, 28–43 dB better out-of-band isolation, 2–3 dB less sensitivity on some bands, driver notes, bias tee 180 mA.
7. RTL-SDR Blog, "RTL-SDR Blog V4 end of line," https://www.rtl-sdr.com/rtl-sdr-blog-v4-end-of-line/ and "RTL-SDR Blog V4L (Lite) now available" (≈ Aug 2026), https://www.rtl-sdr.com/rtl-sdr-blog-v4l-lite-now-available-for-purchase/ (manufacturer; both fetched 2026-09-29) — R828D exhausted, counterfeits, V4L with R828S, diplexed input, two-tone ≈ V3, Osmocom support.
8. RTL-SDR Blog, buy page, https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/ (manufacturer) — 1 ppm TCXO (2 ppm initial), prices.
9. SDRplay, RSP1B and RSPduo product pages, https://www.sdrplay.com/rsp1b/, https://www.sdrplay.com/rspduo/; RTL-SDR.com, "SDRplay release the RSP1A…" (2017) (manufacturer + review) — coverage, filters, bit-depth vs rate, MSi2500 "14-bit" via oversampling.
10. SDRplay, RSPdx-R2 datasheet V1.1 (2026-06), https://sdrplay.com/wp-content/uploads/2026/06/RSPdxR2_Datasheet.pdf (datasheet) — typical NF vs frequency, 0 dBm max input, 0.5 ppm TCXO.
11. Analog Devices, AD9361 datasheet Rev E (mirror https://www.farnell.com/datasheets/2150817.pdf). (datasheet)
12. Analog Devices, AD9363 datasheet Rev D (mirror https://www.radiolocman.com/datasheet/pdf.html?di=169339). (datasheet)
13. Analog Devices, AD9364 datasheet (mirror https://www.farnell.com/datasheets/1859536.pdf). (datasheet)
14. Lime Microsystems, LMS7002M datasheet, https://wiki.myriadrf.org/LimeMicro:LMS7002M_Datasheet (datasheet).
15. Great Scott Gadgets, HackRF documentation (hackrf_one, hardware_components, sampling_rate, setting_gain, gateware), https://hackrf.readthedocs.io, and HackRF Pro page https://greatscottgadgets.com/hackrf/pro/ (fetched 2026-09-29). (manufacturer docs)
16. C. (KA7OEI), "Measuring signal dynamics of the RX-888 Mk2" (2023-09), http://ka7oei.blogspot.com/2023/09/measuring-signal-dynamics-of-rx-888-mk2.html. (independent measurement)
17. RX-888 vendor page https://www.rx-888.com/rx/ and reseller/review notes (via helper research). (vendor/review)
18. Analog Devices, ADALM-PLUTO specifications and customising pages, https://wiki.analog.com/university/tools/pluto/devs/specs (manufacturer wiki) — ranges, 4 MS/s streaming statement, AD9364 setting, Rev D second channel not production-tested.
19. Ettus Research, B200/B210 spec sheet, https://www.ettus.com/wp-content/uploads/2019/01/b200-b210_spec_sheet.pdf, and UHD manual B200 page (manufacturer) — NF < 8 dB, IIP3 −20 dBm, SFDR 78 dBc, TX > 10 dBm, ±2 ppm, GPSDO.
20. Airspy product pages (R2, Mini, HF+ Discovery), https://airspy.com (manufacturer); 2026 prices via RTL-SDR.com sale notice. (manufacturer/reseller)
21. KrakenRF, KrakenSDR documentation and Crowd Supply page, https://github.com/krakenrf/krakensdr_docs/wiki, https://www.crowdsupply.com/krakenrf/krakensdr (manufacturer).
22. RTL-SDR.com, "FobosSDR…" (2024-04), https://www.rtl-sdr.com/fobossdr-a-new-sdr-receiver-with-100-khz-to-6-ghz-tuning-range-and-50-mhz-bandwidth-for-395/ (news/review).
23. Lime Microsystems, Crowd Supply pages for LimeSDR and LimeSDR Mini 2.0, https://www.crowdsupply.com/lime-micro (manufacturer).
24. Nuand, bladeRF 2.0 micro page and "2023.02 release: 122.88 MHz bandwidth," https://www.nuand.com (manufacturer).
25. D. Estévez, "Running the AD9361 at 122.88 Msps" (2023-02), https://destevez.net/2023/02/running-the-ad9361-at-122-88-msps/ (independent technical analysis).
26. MicroPhase, AntSDR E200 Crowd Supply page, https://www.crowdsupply.com/microphase-technology/antsdr-e200; antsdr_uhd firmware https://github.com/MicroPhase/antsdr_uhd (manufacturer).
27. Ettus Research product pages (X310, N310, N320, X410) and NI end-of-life notice for N210 (2025) (manufacturer).
28. RTL-SDR.com, "ADALM-PLUTO SDR hack: tune 70 MHz to 6 GHz…" and "Some further tests with the ADALM-PLUTO SDR," https://www.rtl-sdr.com (review; includes ADI engineer's statement that there are no specifications outside the stock range).
29. SDRstore, "Pluto Plus SDR review" (2026), https://www.sdrstore.eu/pluto-plus-sdr-review-ad9363-2t2r-ethernet-70mhz-6ghz/; LibreSDR firmware repo https://github.com/hz12opensource/libresdr (reseller review / community).
30. RTL-SDR.com, "SDRSharp users guide," https://www.rtl-sdr.com/sdrsharp-users-guide/ (community) — RTL AGC rarely used.
