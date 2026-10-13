# 11-radar — Radar systems, waveforms, signal processing and DIY radar

How radars detect, range, measure velocity and angle, and image — from the radar range equation and radar cross section, through detection theory and CFAR, pulsed radar and pulse compression, the ambiguity function, CW/Doppler and FMCW radar, MIMO virtual arrays, clutter and MTI, to SAR/ISAR imaging and practical hobby hardware (Doppler modules, the MIT coffee-can radar, TI/Infineon/Acconeer radar chips, the ADI Phaser, SDR radar, passive radar) and the specific problem of measuring or tracking a hobby rocket. Written for the builder: every page has derivations in levels, worked numbers at 10.525/24/60/77 GHz and S-band, and a verification script. Phased-array theory and beamforming live in [12-phased-arrays](../12-phased-arrays/_index.md); antennas in [08-antennas](../08-antennas/_index.md); the matched filter and basic detection in [10-comms-modulation](../10-comms-modulation/matched-filter-detection.md); FFT/window/IQ fundamentals in [14-sdr-dsp](../14-sdr-dsp/_index.md) and [00-math-foundations](../00-math-foundations/_index.md); propagation and rain/gas loss in [09-propagation-link-budget](../09-propagation-link-budget/_index.md); phase noise in [07-noise-linearity](../07-noise-linearity/phase-noise-and-jitter.md); legal bands in [19-regulations-safety](../19-regulations-safety/_index.md). Every numeric claim is reproduced by a script in `tools/verify/radar_*.py` (all **ALL PASS**; the tracking page uses `tools/verify/est_radar_tracking.py`).

## Reading order (beginner → advanced)
1. [Radar range equation](radar-range-equation.md) — why R⁴, the energy form, losses, search/track/bistatic forms; 24/77 GHz, coffee-can and S-band examples.
2. [Radar cross section](radar-cross-section.md) — what σ means, sphere/plate/cylinder/corner reflectors (build a calibration target), people/drones/cars/birds/rockets, Swerling statistics.
3. [CW and Doppler radar](cw-and-doppler-radar.md) — Doppler equation, homodyne I/Q, HB100/CDM324, micro-Doppler, vital signs, rocket velocity at the pad.
4. [Detection theory and CFAR](detection-theory-cfar.md) — Pd/Pfa, required SNR, Swerling models, Albersheim/Shnidman, integration gain, CA/OS/GO/SO-CFAR.
5. [FMCW radar](fmcw-radar.md) — beat frequency, resolutions, chirp design (TI SWRA553), range–Doppler–angle processing, phase noise and leakage, VCO nonlinearity.
6. [Pulsed radar and pulse compression](pulsed-radar-and-pulse-compression.md) — PRF and ambiguities, LFM, Barker and polyphase codes, sidelobes and weighting, Doppler tolerance.
7. [MIMO radar and virtual arrays](mimo-radar-virtual-arrays.md) — virtual arrays, TDM/BPM/DDM, angle resolution, cascades, calibration.
8. [Clutter and MTI](clutter-and-mti.md) — σ⁰, rain reflectivity, MTI cancellers, blind speeds, staggered PRF, pulse-Doppler, STAP.
9. [Ambiguity function and waveforms](ambiguity-function-waveforms.md) — AF properties, ridge/thumbtack/bed-of-nails, Costas, accuracy vs resolution, passive-radar CAF.
10. [SAR and imaging](sar-and-imaging.md) — synthetic aperture, D/2, backprojection, ω-k, ISAR, DIY and mm-wave near-field SAR.
11. [DIY radar hardware](diy-radar-hardware.md) — what to buy/build, SDR and passive-radar budgets, rocket-tracking geometry, Singapore bands.
12. [Radar tracking — monopulse, gates, trackers, association](radar-tracking-monopulse-and-trackers.md) — lobing/conical scan/monopulse with slope and accuracy, range/Doppler gates, α-β/Kalman trackers, gating/NN/PDA, rocket radar tracking and GNSS-cued Yagi pointing.
13. [Pulse-Doppler data cube and PRF regimes](pulse-doppler-data-cube-and-prf-regimes.md) — fast/slow-time cube, range–Doppler processing gains, low/medium/high PRF, eclipsing, blind zones, CRT vs coincidence unfolding, MTD windows, CFAR on RD maps, CPI limit for accelerating rockets, DIY SDR pulse-Doppler energy budget.

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [radar-range-equation](radar-range-equation.md) | 4-step derivation, energy form (pulsed = FMCW = TI SWRA553 Eq. 2), Ts cascade, bistatic (Cassini ovals), search (power–aperture) vs track, loss table (Harris windows, straddle, beam-shape 1.6–1.7 dB, CFAR, atmosphere/rain from 09), propagation factor, examples: IPM-165 person, AWR1843-class car/person/drone/rocket, coffee-can, 3 GHz rocket tracker, X-band search, FM passive | mixed | high |
| [radar-cross-section](radar-cross-section.md) | definition/dBsm, Mie sphere (Rayleigh 9πa²(ka)⁴, peak 3.65πa², optical πa²), PO plate/cylinder/sphere, ray-traced trihedral/dihedral effective areas, reflector design table, water-sphere birds (P.840), measured human/drone/vehicle RCS, rocket RCS estimate, scatterer statistics, RAM/shaping, substitution measurement | mixed | medium |
| [detection-theory-cfar](detection-theory-cfar.md) | Neyman–Pearson/LRT, Rayleigh/Rice, Marcum Q, Swerling 0–4 exact vs MC, SW1 closed form, coherent N vs non-coherent N^α (α 0.72–0.84), Albersheim (≤0.3 dB) and Shnidman (≤0.82 dB) accuracy maps, CA/OS/GO/SO-CFAR Pfa formulas, CFAR-loss table, masking, M-of-N, false-alarm rates | mixed | high |
| [pulsed-radar-and-pulse-compression](pulsed-radar-and-pulse-compression.md) | c/2B, R_u, v_u, R_u·v_u = cλ/8, duty/blind range, compression ratio TB, LFM (0.88/B, −13.4 dB), Hamming/Taylor weighting and losses, stretch processing = FMCW, Barker 2–13, Frank/P4, Golay, Doppler-loss table, range–Doppler coupling, straddle loss, CRT ambiguity resolution | mixed | high |
| [ambiguity-function-waveforms](ambiguity-function-waveforms.md) | AF definition and conventions, max at origin, volume invariance (verified), rect and LFM closed forms, pulse-train bed of nails, Costas (Welch) thumbtack, delay CRLB σ_τ = 1/(2πB_rms√(2SNR)) vs MC, passive-radar CAF, waveform-choice table | advanced | high |
| [cw-and-doppler-radar](cw-and-doppler-radar.md) | Doppler derivation (exact vs 2v/λ), Hz per km/h table, homodyne I/Q and image rejection, HB100/IPM-165 modules and IF amplifier design, rotor micro-Doppler and blade flash, arctangent vital-sign demodulation, rocket Doppler rate and coherent time, range correlation, FSK ranging, cosine effect, IMDA bands | mixed | high |
| [fmcw-radar](fmcw-radar.md) | dechirp with RVP, c/2B, IF-limited R_max (0.9/0.45 f_s), v_max/Δv/angle, radar cube and 2-D CFAR simulation, Doppler sign convention, two-target resolution (rect 1.0/Hamming 1.5/Hann 1.66 bins), TI Table 1 re-derived, timing parameters, leakage + phase-noise skirt (simulated), ZX95 VCO nonlinearity + predistortion, migration, interference, chirp-design recipe, BGT60/Phaser/TI devices | mixed | high |
| [mimo-radar-virtual-arrays](mimo-radar-virtual-arrays.md) | p_m+q_n virtual arrays, AWR1843-style az+el layout, 2/N vs −3 dB beamwidth, TDM Doppler-phase error and compensation, BPM +10logN_TX, DDM with empty sub-band, TI 4-chip cascade (86 elements, ~1.4°), calibration effect on sidelobes | intermediate | high |
| [clutter-and-mti](clutter-and-mti.md) | surface/volume clutter scaling, constant-γ σ⁰, Marshall–Palmer Z and Rayleigh-vs-Mie rain η (3–77 GHz), cell sizes and SCR examples, MTI cancellers, blind speeds, improvement factors (MC-verified), staggered PRF, pulse-Doppler, FMCW static-clutter removal, STAP and RMB | mixed | medium |
| [sar-and-imaging](sar-and-imaging.md) | phase history, λR/2L and stripmap D/2 (triangle PSF), sampling ≤ λ/4 and grating ghosts, backprojection (simulated), RDA, ω-k/Stolt, range migration, autofocus tolerance λ/8, ISAR, coffee-can and Forstén DIY SAR, TI near-field mm-wave imaging | mixed | high |
| [diy-radar-hardware](diy-radar-hardware.md) | platform comparison table (HB100, IPM-165/CDM324, coffee-can, TI IWR6843/AWR1843/AWR2944, BGT60TR13C, Acconeer A121, ADI Phaser, Pluto/B210/HackRF, KrakenSDR), SDR leakage budget, stepped frequency, passive-radar DPI budget, rocket-tracking geometry and options, radar altimeter by image theory, Singapore IMDA limits | intro | medium |
| [radar-tracking-monopulse-and-trackers](radar-tracking-monopulse-and-trackers.md) | sequential lobing & conical scan (modulation depth, crossover loss, fluctuation sensitivity), amplitude monopulse (Gaussian-beam Δ/Σ = tanh, k_m vs squint, optimum 0.425 θ_b), phase monopulse = 2-element CRB, σ_θ = θ/(k_m√(2SNR)), split-gate S-curve, Doppler gates, servo, α-β/Kalman in polar/Cartesian, converted-measurement covariance and bias, gating, NN vs PDAF in clutter (MC), M-of-N, rocket tracking geometry, GNSS-cued antenna pointing with latency prediction, RSSI step-track | mixed | high |
| [pulse-doppler-data-cube-and-prf-regimes](pulse-doppler-data-cube-and-prf-regimes.md) | data cube x[m,p,n], gains τf_s·N·M (coherent) vs no mean gain non-coherent (simulated 4×128×1000 cube, CFAR detections, aliased 300 m/s target), MIT LL PRF classes, R_u v_u = cλ/8, eclipsing −10log(1−d), 7-PRF blind-zone map (≥3-of-7 over 97.5%), CRT (exact) vs coincidence search with noisy residues, MTD window choice (40 dB at N = 8), CA-CFAR Pfa with windowed cells, T_max = √(λ/2a), DIY 5.8 GHz SDR design (25.6 µJ baseline fails; 10 W/4 µs/1024 pulses) | mixed | high |
| [radar-applications-gpr-through-wall-sensing](radar-applications-gpr-through-wall-sensing.md) | GPR (1636σ/√εr, water relaxation, depth budget table, resolution), through-wall flash and MIMO nulling (Wi-Vi, WiTrack), Wi-Fi CSI limits and 802.11bf, harmonic radar R⁻⁶ law (RECCO, insect tags), NLJD, RCWL-0516 self-oscillating mixer, LD2410, hobby weather radar, possible-vs-hype table | mixed | medium |

## Domain FAQ (top questions → page#section)
- *How far can my radar see a drone/person/car?* → [range equation § Worked examples](radar-range-equation.md#worked-examples)
- *Why does range only grow with the fourth root of power?* → [range equation § Intuition](radar-range-equation.md#intuition-no-math)
- *How big a corner reflector do I need to calibrate my 24/77 GHz radar?* → [RCS § design table](radar-cross-section.md#design-equations--rules-of-thumb)
- *What RCS should I assume for a person, drone or rocket?* → [RCS § TL;DR and Level 3](radar-cross-section.md#level-3--real-targets-statistics-limits)
- *What SNR do I need for Pd 0.9, Pfa 10⁻⁶?* → [detection § TL;DR](detection-theory-cfar.md#tldr)
- *Is non-coherent integration gain √N?* → [detection § Level 2](detection-theory-cfar.md#level-2--derivations)
- *How do I set a CFAR threshold multiplier?* → [detection § Level 3](detection-theory-cfar.md#level-3--closed-form-approximations-cfar-and-limits)
- *What sets FMCW range resolution and maximum range?* → [FMCW § Level 2](fmcw-radar.md#level-2--derivations)
- *How do I design chirp parameters for a TI radar?* → [FMCW § Design equations](fmcw-radar.md#design-equations--rules-of-thumb) and [Worked example 1](fmcw-radar.md#worked-examples)
- *Why are approaching targets at negative Doppler in TI data?* → [FMCW § TL;DR](fmcw-radar.md#tldr)
- *What does VCO nonlinearity do to my range profile?* → [FMCW § Level 3](fmcw-radar.md#level-3--what-limits-real-fmcw-radars)
- *Why does my HB100 see nothing?* → [CW § Common mistakes](cw-and-doppler-radar.md#common-mistakes--misconceptions)
- *Can I measure rocket velocity off the pad with a Doppler module?* → [CW § Worked example 2](cw-and-doppler-radar.md#worked-examples)
- *What is micro-Doppler and how do I see a drone's propellers?* → [CW § Level 2](cw-and-doppler-radar.md#level-2--derivations-and-receiver-details)
- *Why can't I have both unambiguous range and velocity in a pulsed radar?* → [pulsed § Level 1](pulsed-radar-and-pulse-compression.md#level-1--timing-resolution-and-ambiguity)
- *What does a Hamming window cost in pulse compression?* → [pulsed § Level 2](pulsed-radar-and-pulse-compression.md#level-2--the-matched-filter-and-the-chirp)
- *How does a 3TX×4RX chip get 12 virtual channels, and what's the catch?* → [MIMO § Level 2](mimo-radar-virtual-arrays.md#level-2--derivations-and-multiplexing-schemes)
- *What is a blind speed and how does staggered PRF fix it?* → [clutter § Level 2](clutter-and-mti.md#level-2--derivations)
- *Does the weather-radar dBZ formula work at 77 GHz?* → [clutter § rain table](clutter-and-mti.md#level-2--derivations)
- *Why is stripmap SAR resolution D/2?* → [SAR § Level 2](sar-and-imaging.md#level-2--derivations)
- *How accurately can a radar measure range compared with its resolution?* → [ambiguity § Level 3](ambiguity-function-waveforms.md#level-3--codes-thumbtacks-accuracy-cross-ambiguity)
- *Can an SDR be a radar? Can a KrakenSDR do passive radar?* → [DIY § Level 2](diy-radar-hardware.md#level-2--the-budgets-that-decide-feasibility)
- *Can a DIY radar track my rocket?* → [DIY § rocket tracking](diy-radar-hardware.md#level-3--platform-details-and-gotchas) and [range equation Example D](radar-range-equation.md#worked-examples)
- *Which radar bands are legal in Singapore?* → [DIY § TL;DR](diy-radar-hardware.md#tldr)
- *How does monopulse measure angle finer than the beamwidth, and how accurately?* → [tracking § Level 2](radar-tracking-monopulse-and-trackers.md#the-math)
- *Nearest neighbour or PDA in clutter?* → [tracking § Level 3](radar-tracking-monopulse-and-trackers.md#the-math)
- *How do I point my telemetry Yagi from the rocket's GNSS, and does latency matter?* → [tracking § Worked example 6](radar-tracking-monopulse-and-trackers.md#worked-examples)
- *What are fast time and slow time, and what is the radar data cube?* → [pulse-Doppler § Level 1](pulse-doppler-data-cube-and-prf-regimes.md#the-math)
- *Low, medium or high PRF — which and why?* → [pulse-Doppler § Level 1 table](pulse-doppler-data-cube-and-prf-regimes.md#level-1--the-cube-and-the-regimes)
- *How does the Chinese remainder theorem resolve range ambiguity, and why does it fail with noise?* → [pulse-Doppler § Level 2 (e)](pulse-doppler-data-cube-and-prf-regimes.md#level-2--derivations)
- *How long can I integrate coherently on an accelerating rocket?* → [pulse-Doppler § Level 2 (b)](pulse-doppler-data-cube-and-prf-regimes.md#level-2--derivations)
- *Can an SDR be a pulse-Doppler radar?* → [pulse-Doppler § Example 4](pulse-doppler-data-cube-and-prf-regimes.md#worked-examples)
- *Should my radar be pulsed or FMCW, and do I need a complex (IQ) IF?* → [FMCW § choosing a waveform](fmcw-radar.md#choosing-a-waveform-pulsed-vs-fmcw-real-vs-complex-if-bistatic-fmcw)
- *How accurate is an FMCW radio altimeter on a rocket or recovery system?* → [FMCW § altimeter error budget](fmcw-radar.md#fmcw-radio-altimeters-error-budget)
- *What do fast time, slow time, CPI, A-scope and PPI mean?* → [FMCW § timing and display vocabulary](fmcw-radar.md#radar-timing-and-display-vocabulary)
- *Can I use a microwave-oven magnetron or a TWT, and how is it pulsed?* → [DIY hardware § tubes and pulse modulators](diy-radar-hardware.md#microwave-tubes-and-pulse-modulators) (hazards: [19 lab safety](../19-regulations-safety/lab-safety-esd-high-power.md))
- *How sharp an image can a real-beam radar, DBS or an "RF camera" give?* → [SAR § real-beam imaging limits](sar-and-imaging.md#real-beam-imaging-limits-doppler-beam-sharpening-rf-cameras-mechanical-scanning-and-aperture-outlines)

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
Skolnik *Introduction to Radar Systems* 3e; Richards *Fundamentals of Radar Signal Processing* 2e; Richards–Scheer–Holm *Principles of Modern Radar*; Levanon & Mozeson *Radar Signals*; Mahafza *Radar Systems Analysis and Design Using MATLAB*; Knott *Radar Cross Section*; Stimson *Introduction to Airborne Radar*; Soumekh and Cumming & Wong (SAR); Griffiths & Baker (passive radar); Albersheim 1981, Shnidman 2002, Rohling 1983, Swerling 1960, Marcum 1960; TI SWRA553/SWRA554 and Rao's FMCW training; Dürr et al. 2019 (range correlation); MIT IAP coffee-can radar course; module datasheets (HB100, IPM-165, ZX95-2536C+); IMDA TS SRD 2023.

## Known gaps
- No measured RCS of hobby-scale rockets (fibreglass vs carbon) — estimate only; a turntable ISAR measurement would fill it.
- Effective audio-IF noise figure of Doppler modules unmeasured (inferred ~30–35 dB from vendor range claims).
- Clutter σ⁰ and spectral-width numbers are textbook-level; no specific measured land/sea data sets summarised (Billingsley, NRL model).
- Singapore status of 77–81 GHz: resolved 2026-09-29 (W5-E1) — absent from TS SRD but licence-exempt as an Ultra-Wideband device (Exemption Notification item 17; IMDA TS UWB 2016: mean ≤ −3 dBm/MHz, peak ≤ 55 dBm/50 MHz); see [DIY radar](diy-radar-hardware.md).
- ADI Phaser FMCW ramp parameters, KrakenSDR maximum sample rate, AWR2944 DDMA details not confirmed from primary documents.
- Not implemented numerically: ω-k/RDA SAR, autofocus, non-Gaussian clutter CFARs, interference mitigation, NLFM design, mismatched sidelobe-suppression filters, wideband ambiguity function.
- Radar tracking and monopulse now covered by [radar-tracking-monopulse-and-trackers](radar-tracking-monopulse-and-trackers.md) (W5-E5); IMM, JPDA/MHT, low-angle multipath and glint are described but not simulated, and no real monopulse feed has been measured.

- Pulse-Doppler/data cube now covered by [pulse-doppler-data-cube-and-prf-regimes](pulse-doppler-data-cube-and-prf-regimes.md) (W5-E8); airborne clutter folding, HPRF FM-ranging, PRF-set optimisation and MTD clutter maps described but not simulated; no measured DIY pulse-Doppler data.