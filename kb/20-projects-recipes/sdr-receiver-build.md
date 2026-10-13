---
title: Recipe — SDR ground receiver, recorder and spectrum monitor for LoRa rocket telemetry (RTL-SDR / Pluto, gr-lora_sdr, front-end filtering, gain staging)
domain: 20-projects-recipes
slug: sdr-receiver-build
tags: [recipe, sdr, rtl-sdr, pluto, airspy, gr-lora_sdr, gnu-radio, sigmf, iq-recording, gain-staging, dynamic-range, offset-tuning, dc-spike, iq-image, doppler-measurement, spectrum-monitor, rtl_power, lora, pre-registration]
prerequisites:
  - ../14-sdr-dsp/sdr-hardware-survey.md
  - ../14-sdr-dsp/gnu-radio-and-software-stack.md
  - ../14-sdr-dsp/iq-complex-baseband.md
  - ground-station-tracking-yagi.md
related:
  - ../14-sdr-dsp/software-demodulation.md
  - ../14-sdr-dsp/multirate-dsp-decimation-cic.md
  - ../14-sdr-dsp/fft-spectral-analysis-windows.md
  - ../17-test-measurement/sdr-as-test-equipment.md
  - ../15-lora-ism-radios/ground-station-design.md
  - ../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md
  - lora-rocket-telemetry-link.md
  - beginner-project-ladder.md
level: intermediate
confidence: medium
last_updated: 2026-10-02
---

# Recipe — SDR receiver, recorder and spectrum monitor for the rocket downlinks

The software-defined part of the [ground station](ground-station-tracking-yagi.md): record the raw IQ of both
LoRa downlinks for the whole flight, decode them offline (and optionally live) with **gr-lora_sdr**, measure
every packet's carrier frequency (Doppler and drift), and watch the band for interference. It also answers the
EBYTE air-rate question (which SF/BW the modules really use). Numbers: `python3 tools/verify/proj_sdr_receiver.py`.
First-time SDR users: start with the [beginner project ladder](beginner-project-ladder.md).

## Questions this page answers
- Which SDR should record my LoRa telemetry, and is an RTL-SDR good enough?
- Where should I tune so the DC spike and the IQ image don't sit on my signal?
- What sample rate does gr-lora_sdr need, and how do I decimate to it?
- How much SDR gain should I use behind a masthead LNA?
- Why does a single RTL-SDR clip on the pad and early in the flight, and what do I do about it?
- How big are the recordings, and how do I timestamp them well enough to line up with the flight log?
- Can I measure the rocket's Doppler with an SDR whose own clock is off by 1 ppm?
- How do I find the SF/BW/CR hidden behind the EBYTE "air data rate" setting?
- How do I run a spectrum monitor for interference on launch day?

## TL;DR
- **Hardware**: one **RTL-SDR Blog V3/V4L per band** (≈ US$35–40, 8-bit, ≤ 2.4 MS/s, measured NF ≈ 5.4 dB at 437 MHz) behind the masthead LNA chain is enough to record and decode; a 12-bit SDR (Pluto, Airspy) adds ≈ 26 dB of in-channel dynamic range ([SDR survey](../14-sdr-dsp/sdr-hardware-survey.md)).
- **Tuning**: sample at 1.024 MS/s (≤ 250 kHz LoRa) or 2.048 MS/s (500 kHz) and **tune the LO fs/4 below the channel** (433.125 → LO 432.869 MHz at 1.024 MS/s): the DC spike sits 256 kHz away and the IQ image at 432.613 MHz, both outside the channel; decimate to 4 × BW (1 MS/s for 250 kHz) for gr-lora_sdr.
- **Gain staging**: behind LNA (19.8 dB) → SAW → 15 m LMR-240 → 2-way split, an RTL-SDR adds only ≈ 14 % to the system noise (system NF 1.34 dB at 433 MHz); the right SDR gain is the lowest that makes the noise floor rise **≥ 6–10 dB** when you connect the chain instead of a 50 Ω load — more gain only costs headroom.
- **Dynamic range is the binding limit**: an 8-bit RTL-SDR holds ≈ 54 dB in a 250 kHz channel; with the noise set 6 dB above the ADC floor it clips at ≈ **−71 dBm at the LNA input**. The flight spans −10 dBm (pad, 30 m) and −58…−67 dBm (lift-off/apogee from 5 km at 2 W) to −107…−126 dBm (15 km worst case, sensitivity) — **≈ 100 dB**. Use **two SDRs per band from the splitter, one with a 30 dB pad** ("low" channel), or a 12-bit SDR (clips ≈ −45 dBm).
- **Recording**: 1.024 MS/s cu8 = 2.05 MB/s = 7.4 GB/h per SDR; write SigMF (`cu8` + JSON metadata with sample rate, centre frequency, start time). A 1 ppm sample clock drifts 1.8 ms in 30 min — fine against 41 ms packets; log a GNSS-PPS-disciplined start time.
- **Doppler**: the SDR's own 1 ppm clock error (433 Hz at 433 MHz, 868 Hz at 868 MHz) is as large as the flight Doppler (477 / 956 Hz peak from a 5 km cross-range station) — **record the rocket's carrier on the pad for ≥ 1 min as the zero-Doppler reference**; the difference cancels both crystals' static offsets.
- **Spectrum monitor**: rtl_power-style hops cover 400–450 MHz in ≈ 1.3–1.5 s and 850–930 MHz in ≈ 2.0–2.4 s at 1–10 kHz bins — run it for an hour on site before choosing channels.

## Intuition (no math)
An SDR is a radio that turns a slice of spectrum into a stream of numbers (I and Q samples) and leaves all the decisions to software. That makes it a perfect *recorder*: it keeps everything — packets the module decoded, packets it missed, interference, the exact frequency of every chirp — so you can re-listen after the flight with better tools. Its weaknesses are a cheap front end (noisy, easily overloaded, with self-made artefacts like the DC spike and mirror images) and a small number of bits, so it cannot hear a whisper and a shout at the same time. The recipe puts a good LNA and filter in front, tunes so that the artefacts fall next to the signal rather than on it, and uses two SDRs set for whispers and shouts.

## Requirements
| ID | Requirement | Value |
|---|---|---|
| S1 | Bands | 433.05–434.79 MHz; 866–869 MHz (SG) or 902–928 MHz (IREC) |
| S2 | Signals | LoRa SF5–12, BW 125/250/500 kHz; also capture EBYTE preamble for air-rate identification |
| S3 | Decoding | offline gr-lora_sdr on 100 % of recorded flight time; live decode optional |
| S4 | Dynamic range | no clipping on the far-field "high" channel for P ≤ −75 dBm; the "low" channel covers to ≈ −40 dBm |
| S5 | Timing | packet times to ≤ 5 ms against GNSS time |
| S6 | Frequency | per-packet carrier estimate to ≤ 20 Hz after pad calibration |
| S7 | Storage | ≥ 1 h per SDR on the ground laptop SSD |

## Architecture options and trade study
| Option | ADC | Bandwidth | NF (board) | In-channel DR (250 kHz) | Cost | Verdict |
|---|---|---|---|---|---|---|
| **RTL-SDR Blog V3/V4L ×2 per band** | 8-bit | 2.4 MS/s | 5.4 dB @ 437 MHz (meas.) | ≈ 54 dB each; ≈ 84 dB as a high/low pair | ≈ US$75 per band | **chosen** |
| Airspy Mini / R2 | 12-bit | 6 / 10 MS/s | 7.0–7.9 dB (meas.) | ≈ 80 dB | US$100–170 | single-SDR alternative |
| ADALM-Pluto | 12-bit | ≤ 4 MS/s sustained | ≈ 6 dB | ≈ 80 dB | ≈ US$250 | also a test transmitter (conducted only) |
| HackRF One | 8-bit | 20 MS/s | ≈ 11 dB | ≈ 54 dB | ≈ US$340 | worst receiver here |
| KrakenSDR (5 coherent channels) | 8-bit | 2.4 MS/s | — | — | ≈ US$750 | DOA/array work ([phased-array starter](phased-array-starter-build.md)) |

## The math — design calculations

### Level 1 — frequency plan
- Sample rate $f_s$ shows $[-f_s/2, +f_s/2]$ around the LO; zero-IF tuners put a **DC spike** at 0 Hz and an **image** of every signal at $-f$ (IQ imbalance: 0.5 dB / 3° → image only 28 dB down) ([IQ & complex baseband](../14-sdr-dsp/iq-complex-baseband.md), [SDR as test equipment](../17-test-measurement/sdr-as-test-equipment.md)).
- Offset tuning: put the channel at $+f_s/4$; its image lands at $-f_s/4$ where nothing of interest is.

| Link | $f_s$ | LO | Channel at | Image at | Decimate to (4 × BW) |
|---|---|---|---|---|---|
| 433.125 MHz, BW 250 kHz | 1.024 MS/s | 432.8690 MHz | +256 kHz | 432.6130 MHz | 1.0 MS/s (≈ ÷1) |
| same | 2.048 MS/s | 432.6130 MHz | +512 kHz | 432.1010 MHz | ÷2.05 |
| 868.125 MHz, BW 250 kHz | 1.024 MS/s | 867.8690 MHz | +256 kHz | 867.6130 MHz | ≈ ÷1 |
| 905 MHz, BW 500 kHz (IREC) | 2.048 MS/s | 904.4880 MHz | +512 kHz | 903.9760 MHz | 2.0 MS/s |
(Shift with an NCO, low-pass/decimate with a half-band or polyphase filter — [multirate DSP](../14-sdr-dsp/multirate-dsp-decimation-cic.md), [NCO/DDC](../14-sdr-dsp/nco-ddc-duc.md).)

### Level 2 — noise and gain staging
Cascade at 433 MHz: LNA 0.45 dB / 19.8 dB → SAW 2.5 dB → 15 m LMR-240 2.6 dB → splitter → SDR:

| SDR (board NF) | 2-way split (3.5 dB): system NF / SDR share of noise | 4-way split (7 dB) |
|---|---|---|
| RTL-SDR V3 (5.4 dB) | **1.34 dB / 14 %** | 2.27 dB / 25 % |
| Pluto (≈ 6.1 dB) | 1.51 dB / 17 % | 2.57 dB / 30 % |
| Airspy Mini (7.4 dB) | 1.83 dB / 23 % | 3.13 dB / 38 % |
| HackRF (11 dB) | 3.17 dB / 43 % | 5.17 dB / 61 % |

"Noise rise" test: connecting the LNA chain (with the antenna or a 50 Ω load at the LNA input) instead of terminating the SDR input should raise the displayed floor by ≈ 8.6 dB (RTL, 2-way) — if it rises less, the SDR gain is too low or the chain gain too small.

### Level 2 — dynamic range
With system NF 1.34 dB the noise in 250 kHz is −118.7 dBm at the antenna terminals (SF7/250 sensitivity −126.2 dBm). Link events from the [telemetry recipe](lora-rocket-telemetry-link.md):

| Event | Level at LNA input | In-channel SNR |
|---|---|---|
| rocket on the pad, 30 m, main lobe | −9.6 dBm | 109 dB |
| lift-off, station C, 2 W | −58.5 dBm | 60 dB |
| apogee, station C, 2 W | −66.7 dBm | 52 dB |
| apogee, station C, 10 mW e.r.p. | −89.2 dBm | 29.5 dB |
| 15 km tail-null worst case, 10 mW e.r.p. | −106.7 dBm | 12 dB |
| SF7/250 sensitivity | −126.2 dBm | −7.5 dB |

8-bit in-channel dynamic range ≈ 54 dB at 250 kHz (56.7 dB at 125 kHz, [SDR survey](../14-sdr-dsp/sdr-hardware-survey.md)); with the noise placed 6 dB (10 dB) above the quantisation floor the RTL-SDR clips at in-channel SNR ≈ 48 dB (44 dB), i.e. **−71 dBm (−75 dBm) at the LNA input**. 12-bit SDRs clip at ≈ −45 dBm (−49 dBm). A constant-envelope LoRa chirp survives mild clipping, but clipping intermodulates every other signal in the band and corrupts frequency estimates — design so that the "high" channel never clips during the far part of the flight and the "low" channel (30 dB pad) covers the near part (to ≈ −41 dBm).

### Level 3 — timing and frequency
- **Timestamps** from the sample count: error = clock ppm × elapsed time: 1 ppm → 0.6 ms in 10 min, 1.8 ms in 30 min; 10 ppm (crystal) → 18 ms in 30 min (half a SF7/250 packet). Use the TCXO SDRs and a GNSS-disciplined start time, or inject the PPS edge into a spare SDR channel.
- **Frequency**: SDR clock error × carrier: 1 ppm = 433 Hz at 433 MHz, 868 Hz at 868 MHz — the same size as the peak flight Doppler from a 5 km cross-range station (477 Hz at 433 MHz, 956 Hz at 868 MHz for 330 m/s radial). Calibrate on the pad: the rocket's static carrier measured for ≥ 1 min gives (TX offset + RX offset); subtracting it during flight leaves Doppler + TX thermal drift (separate them with the downlinked GNSS velocity).
- **Per-packet carrier estimate**: gr-lora_sdr's fractional-CFO estimate from the preamble resolves a small fraction of a bin ($BW/2^{SF}$ = 1.95 kHz at SF7/250) — averaging over the 8 preamble chirps typically gives tens of Hz; that is the S6 target, to be verified on recorded pad data.

## Design equations & rules of thumb
| Rule | Value |
|---|---|
| Offset tuning | channel at $+f_s/4$ (≥ 256 kHz at 1.024 MS/s) |
| gr-lora_sdr input rate | 2–8 × BW; 4 × BW robust |
| SDR gain | minimum that gives ≥ 6–10 dB noise rise with the chain connected |
| 8-bit in-channel DR | ≈ 50 dB + 10 log($f_s$/BW) − implementation loss → ≈ 54 dB at 250 kHz |
| High/low channel pad | ≈ (flight dynamic range − SDR DR) ≈ 30 dB |
| Storage | $2 f_s \times$ bytes per component: 2.05 MB/s at 1.024 MS/s cu8 |
| Timestamp drift | ppm × duration |
| Doppler | $f_D = -\dot r f_c/c$: 1.1 Hz per m/s at 433 MHz, 2.9 Hz per m/s at 868 MHz |

## Worked examples

### 1. The recording rig (one band; duplicate for the other)
```
 masthead chain (LNA->SAW) --15 m LMR-240-- bias-tee -- 4-way splitter --+-- EBYTE module rx (live telemetry)
                                                                          +-- SX126x dev board (RadioLib: SNR, FEI)
                                                                          +-- RTL-SDR "high"  (gain set by noise-rise test)
                                                                          +-- 30 dB pad -- RTL-SDR "low"
 laptop: rtl_sdr / SoapySDR -> SigMF writer (cu8) per SDR, filenames with GNSS-UTC start time; NTP/GNSS-disciplined clock
```
With a 4-way splitter the system NF rises to 2.27 dB for the RTL "high" channel (vs 1.34 dB with a 2-way) — still within the [ground-station](ground-station-tracking-yagi.md) G3 requirement.

### 2. Identifying the EBYTE air-rate settings (closes the open question of [LoRa modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md))
1. Module transmits into a 40 dB attenuator; RTL-SDR at 2.048 MS/s via a further 30–40 dB pad (never > −20 dBm at the SDR input; HackRF max −5 dBm).
2. Waterfall: preamble chirp **sweep width = BW**, **chirp period = T_s**, $SF = \log_2(T_s \cdot BW)$.
3. gr-lora_sdr receive with that SF/BW, try CR 4/5…4/8 and implicit/explicit header; the explicit header reveals CR and length.
4. Repeat for every air-rate code (2.4k, 4.8k, 9.6k, 19.2k, 38.4k, 62.5k) on both E22 and E220; record SF/BW/CR, preamble length, sync word in the KB.

### 3. Launch-day spectrum survey
rtl_power-style sweep 400–450 MHz (25 hops of 2 MHz, ≈ 1.3–1.5 s revisit) and 850–930 MHz (40 hops, ≈ 2.0–2.4 s) for an hour; plot the max-hold and 95th-percentile per bin; pick the quietest legal channel and agree it with other teams ([spectrum analysers](../17-test-measurement/spectrum-analyzers.md), [FFT scaling](../14-sdr-dsp/fft-spectral-analysis-windows.md)).

## Part selection
| Item | Choice | Price (est., USD) | Notes |
|---|---|---|---|
| SDR | RTL-SDR Blog V3 or V4L (TCXO 1 ppm) ×2 per band | 35–40 each | V4 end of line |
| 12-bit alternative | Airspy Mini / ADALM-Pluto | 100 / 250 | Pluto also a conducted test source |
| Pad for the "low" channel | 30 dB SMA attenuator (≥ 0.5 W) | 10 | |
| Splitter | 4-way Wilkinson 400–1000 MHz | 20 | |
| Laptop storage | NVMe SSD ≥ 256 GB free | — | 4 SDRs × 7.4 GB/h |
| Timing | GNSS receiver with PPS + `chrony` | 20 | disciplines the laptop clock |
| Software | GNU Radio 3.10, gr-lora_sdr, SoapySDR, SigMF tools, SDR++ | free | GNU Radio 4.0 still RC ([GNU Radio stack](../14-sdr-dsp/gnu-radio-and-software-stack.md)) |

## Block diagram (signal processing)
```
 cu8 IQ @1.024 MS/s --(u-127.5)/127.5--> complex --NCO shift -256 kHz--> LPF/decimate (os 4)
   --> gr-lora_sdr: frame sync (preamble, CFO/STO) -> FFT demod -> gray demap -> deinterleave -> Hamming -> dewhiten -> CRC
   --> per packet: UTC (sample index + start time), CFO (Hz), SNR, payload bytes  --> CSV + parsed telemetry (same protocol definition as flight)
```

## Layout notes
Not a PCB project; the RF "layout" is cabling: SMA torque, short pigtails, a DC block on every SDR input when a bias-tee is on the line, ferrite on USB cables near the antenna feed, SDRs inside a metal box (laptop and USB noise rise the floor at 433 MHz), separate USB controllers/hubs for each SDR to avoid sample drops ([GNU Radio stack](../14-sdr-dsp/gnu-radio-and-software-stack.md)).

## Simulation plan
| Step | Tool | Pass |
|---|---|---|
| Frequency plan, cascade, DR, storage | `proj_sdr_receiver.py` | S1–S7 met on paper |
| Synthetic LoRa through the chain | `tools/verify/lora_css_sim.py`-style generator → add noise, clipping at the 8-bit level, CFO/drift → gr-lora_sdr | decode at −7.5 dB SNR (SF7) and through 10 dB of clipping overdrive |
| Decimation filters | `dsp_multirate_cic.py` patterns | image/alias rejection ≥ 60 dB at the LoRa band edges |

## Build, bring-up and test plan (pass/fail fixed in advance)
| # | Test | Method | Pass |
|---|---|---|---|
| R1 | Sample integrity | 30 min recording per SDR at 1.024 MS/s; count samples vs wall-clock | 0 dropped samples; drift within the TCXO ppm |
| R2 | Noise-rise gain setting | per SDR: floor with 50 Ω at SDR input vs chain connected | rise 6–10 dB at the chosen gain |
| R3 | Clip level | signal generator (or module through calibrated attenuators) stepped up; watch ADC histogram/clipping counter | "high" channel clips within ±3 dB of −71 dBm (LNA-input referred) |
| R4 | Sensitivity | module through attenuators (or the radiated test of the link recipe) | gr-lora_sdr decodes ≥ 99 % at the module's PER = 1 % level ± 2 dB (implementation loss) |
| R5 | Air-rate identification | worked example 2 | SF/BW/CR identified for every EBYTE air-rate code |
| R6 | Frequency calibration | 10 min pad recording | per-packet CFO standard deviation ≤ 20 Hz |
| R7 | Full rehearsal | drone or car carrying a 10 mW beacon, two stations recording | every packet received by any receiver is also in the IQ decode |

## Regulatory check
Receive-only; no licence needed in Singapore ([IMDA](../19-regulations-safety/singapore-imda-rules.md)). The Pluto/HackRF as a *transmitter* (test source) is a radio transmitter: conducted only (cables + attenuators), or within SRD limits on a legal band; never in GNSS bands. Recording other users' transmissions for interference analysis is fine; do not decode/publish others' content.

## Pre-registered predictions
| ID | Prediction | Tolerance | If outside |
|---|---|---|---|
| D1 | RTL "high" channel system NF 1.3 dB (2-way) / 2.3 dB (4-way) at 433 MHz | ±0.7 dB | SDR NF differs from the 5.4 dB measurement |
| D2 | Clip level of the "high" channel ≈ −71 dBm at the LNA input | ±3 dB | ENOB/implementation loss different |
| D3 | gr-lora_sdr decodes within 2 dB of the module's sensitivity | — | implementation loss larger than reported in the gr-lora_sdr paper; check os_factor and CFO estimation |
| D4 | Pad-referenced Doppler during ascent matches $-\dot r f_c/c$ from GNSS to ≤ 50 Hz RMS | — | thermal drift of the rocket crystal under PA heating (see impairments page) |
| D5 | EBYTE "2.4k" decodes as one of SF9/125, SF10/250, SF11/500 | — | EBYTE uses non-standard settings — document them |

## Risks and common failure modes
| Failure | Symptom | Fix |
|---|---|---|
| Signal on the DC spike / image | decode fails, spurious lines | offset tuning ($+f_s/4$) |
| Silent sample drops | gaps, time slips | separate USB controllers, lower rate, R1 check |
| Clipping near the pad | garbage spectra, wrong CFO | low channel with pad; don't trust high-channel data < −71 dBm |
| Wrong unsigned-byte conversion | −45 dBFS DC spike, offset | $(u - 127.5)/127.5$ ([GNU Radio stack](../14-sdr-dsp/gnu-radio-and-software-stack.md)) |
| Bias-tee DC into an SDR | dead SDR | DC block |
| Laptop clock not disciplined | timestamps off by seconds | chrony + GNSS PPS, log offset |
| Overloading the SDR with the bench transmitter | damaged front end | ≥ 70 dB of attenuation from a 2 W module; never connect a transmitter directly |

## Cost estimate
| Item | Cost (USD, est.) |
|---|---|
| 4 × RTL-SDR (two bands × high/low) | ≈ 150 |
| Pads, splitters, DC blocks, cables | ≈ 60 |
| GNSS PPS receiver | ≈ 20 |
| Shielded box for the SDRs | ≈ 15 |
| **Total** | **≈ 245** (excludes the masthead chain from the ground-station recipe) |

## Practical notes
- Name every recording with the station ID, band, gain, pad, LO and UTC start; write the same into the SigMF metadata — "a filename is a claim; the metadata is evidence" (team ethos).
- Keep a 10 s calibration recording with the 50 Ω load at the start and end of each session (noise floor, gain stability).
- For live decoding, run gr-lora_sdr on the *recorded* file in near-real time (tail the file) rather than on the device stream, so a crashing decoder never stops the recording.

## Common mistakes & misconceptions
- **"More SDR gain = more sensitivity."** Behind a masthead LNA the SDR contributes ≈ 14 % of the noise; extra gain only lowers the clip point.
- **"An 8-bit SDR has 48 dB of dynamic range, so it can't decode weak LoRa."** LoRa's processing gain works below the noise; the problem is strong signals, not weak ones.
- **"The SDR measures Doppler directly."** Its own 1 ppm clock error is as large as the Doppler; difference against the pad reference.
- **"Tune right on the channel."** That puts the signal on the DC spike of a zero-IF tuner.
- **"Record after the decode works."** Record first; decode later.

## How to simulate / verify
- `python3 tools/verify/proj_sdr_receiver.py` — frequency plan, cascades, dynamic range, storage, timing, Doppler calibration, sweep times.
- `python3 tools/verify/dsp_sdr_hardware.py`, `dsp_host_stack.py`, `dsp_demod.py` (domain 14) — SDR numbers, SigMF round trip, LoRa/FSK demodulators.
- Bench: R1–R7.

## Open questions / gaps
- gr-lora_sdr implementation loss vs Semtech silicon not quantified in the KB (domain 14 gap); D3 will measure it.
- RTL-SDR V4L NF and clip level at 868/905 MHz not measured.
- EBYTE air-rate mapping (R5).

## Sources
1. This KB, [SDR hardware survey](../14-sdr-dsp/sdr-hardware-survey.md) — RTL-SDR/Airspy/Pluto/HackRF specs, measured NFs (Libre Space Foundation, Rowetel), in-channel dynamic range. (internal)
2. This KB, [GNU Radio and the software stack](../14-sdr-dsp/gnu-radio-and-software-stack.md) — GNU Radio 3.10/4.0 status, SigMF, RTL-SDR byte format, overflow handling. (internal)
3. This KB, [Software demodulation](../14-sdr-dsp/software-demodulation.md) and [multirate DSP](../14-sdr-dsp/multirate-dsp-decimation-cic.md) — LoRa demodulation, gr-lora_sdr oversampling. (internal)
4. This KB, [SDR as test equipment](../17-test-measurement/sdr-as-test-equipment.md) — IQ image, calibration, max input levels. (internal)
5. J. Tapparel, O. Afisiadis, P. Mayoraz, A. Balatsoukas-Stimming, A. Burg, "An open-source LoRa physical layer prototype on GNU Radio," IEEE SPAWC 2020, arXiv:2002.08208; https://github.com/tapparelj/gr-lora_sdr. (peer-reviewed + code)
6. SigMF specification v1.2 — https://github.com/sigmf/SigMF (standard, via [2]).
7. This KB, [LoRa ground-station design](../15-lora-ism-radios/ground-station-design.md), [telemetry recipe](lora-rocket-telemetry-link.md), [ground-station recipe](ground-station-tracking-yagi.md). (internal)
