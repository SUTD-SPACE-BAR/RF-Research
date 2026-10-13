---
title: Beamforming architectures — analog RF/IF/LO phase shifting, digital, hybrid/subarrays, Butler matrix, Rotman lens, dynamic range and synchronisation
domain: 12-phased-arrays
slug: beamforming-architectures
tags: [analog-beamforming, digital-beamforming, hybrid-beamforming, subarray, LO-phase-shifting, IF-beamforming, butler-matrix, rotman-lens, multiple-beams, dynamic-range, 10logN, phase-noise-correlation, spurious-decorrelation, synchronisation, coherent-receivers, JESD204B, data-rate, noise-figure, starlink, leo-user-terminal, ku-band, triangular-lattice, rfic-beamformer, scan-loss, case-study]
prerequisites: [array-factor-linear-arrays.md, beam-steering-grating-lobes.md, ../07-noise-linearity/noise-figure-and-friis.md]
related: [phase-shifters-ttd-components.md, array-calibration.md, adaptive-beamforming-doa.md, diy-phased-array-projects.md, tapering-sidelobe-control.md, ../06-rf-circuits/receiver-architectures.md, ../06-rf-circuits/vco-and-pll-synthesizers.md, ../06-rf-circuits/couplers-dividers-combiners.md, ../07-noise-linearity/phase-noise-and-jitter.md, ../07-noise-linearity/dynamic-range-sfdr-blocking.md, ../05-analog-electronics/data-converters-adc-dac.md, ../14-sdr-dsp/sdr-hardware-survey.md, ../14-sdr-dsp/fpga-for-sdr.md, ../11-radar/mimo-radar-virtual-arrays.md]
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# Beamforming architectures

## Questions this page answers
- What are the different ways to build a phased array — RF, IF, LO, digital, hybrid — and what does each cost me?
- Where should the phase shifting happen?
- Do I need a separate receiver (ADC) behind every antenna?
- How many beams can I form at once with each architecture?
- What is a Butler matrix or a Rotman lens and when would I use one?
- Why does "10·log N" dynamic-range improvement apply to noise and some spurs but not others?
- Does a strong interferer in a sidelobe still hit every ADC at full strength in a digital array?
- Why must all channels share an LO/reference? Are two SDRs locked to the same 10 MHz reference coherent?
- Does LO phase noise average out across the channels?
- What data rate does a digital array generate, and where must the beamforming be done?
- Why do I need an LNA *before* the beamformer?
- What is the right architecture for a student DOA array, a tracking ground station, or a small radar?
- How is a Starlink user terminal built (elements, lattice, beamformer chips), and do its published numbers add up?

## TL;DR
- **Analog (RF) beamforming**: phase shifter + gain control per element, one combiner, one receiver. Cheapest per element, one beam per combiner, squints with frequency, and each element needs an LNA *before* the lossy beamformer or the array's SNR advantage evaporates (8 elements: +7.0 dB with a 25 dB LNA, −9 dB with none — script §5).
- **LO or IF phase shifting**: a mixer per element, phase applied to the LO (or at IF); keeps phase-shifter loss out of the RF path; still one beam per combiner.
- **Digital beamforming (DBF)**: one receiver/ADC per element, weights applied in DSP: any number of simultaneous beams, adaptive nulling, digital true-time delay, per-element calibration. Costs power, data (8 ch × 61.44 MS/s × 12-bit IQ = 11.8 Gb/s) and synchronisation effort. Noise, quantisation and **uncorrelated** spurs improve by **10 log N** relative to the beamformed signal (verified); **correlated** spurs and **common-LO phase noise do not**.
- **Hybrid/subarray**: analog beamforming within subarrays of M elements, digital across subarrays. N/M ADCs; squint limited to the (wider) subarray beam; digital scanning limited to the subarray beam, otherwise subarray-lattice grating lobes appear.
- **Butler matrix** = a hardware spatial FFT: N orthogonal fixed beams at sinθ_m = (m − ½)λ/(Nd), adjacent beams crossing at **−3.7 dB (N = 4), −3.9 dB (large N)** (verified); narrowband. **Rotman lens** = a TTD multi-beam lens: wideband, no squint.
- **Coherence requires three things**: a common frequency reference, a *known* phase relationship (common LO, or calibration after every retune), and aligned sample timing. Two SDRs 1 ppm apart at 433 MHz rotate their relative phase every 2.3 ms; locked to one 10 MHz reference they stop rotating but land at a random phase after every retune (fractional-N PLLs) — hence KrakenSDR's automatic noise-source recalibration.
- **Phase noise**: beamformed carrier-to-phase-noise improves by 10 log(N/(1 + (N−1)ρ)) for LO correlation ρ — 0 dB for a shared LO, 10 log N for independent LOs (Monte Carlo verified). ADI's system model: close-in reference noise is correlated; far-out VCO noise of distributed PLLs improves as 10 log N [5].
- **A digital array does not protect its ADCs**: spatial filtering happens after digitisation, so every ADC must handle the full-strength interferer arriving through its element pattern. Analog beamforming protects the ADC but not the per-element LNAs.

- **Case study — Starlink-class LEO terminal:** Ku-band (Rx 10.7–12.7, Tx 14.0–14.5 GHz), 1,280 elements (Gen1, teardown) on a triangular lattice ≈ 13–14 mm driven by 80 × 16-channel RFIC beamformers; filed EIRP 38.2 dBW = 4.06 W + 32.0 dBi (3 mW per element); 2.6 dB scan loss ↔ ±55° FoV ↔ Tx grating-lobe limit 52–56° ([case study](#case-study-starlink-class-leo-user-terminal)).

## Intuition (no math)

**Where you do the "adding up" decides almost everything.** A phased array is (1) delaying/phasing each element and (2) adding. If you add *before* digitising (analog beamforming), you need only one receiver, but you get only one beam per adder and whatever you threw away (other directions) is gone forever. If you digitise *every* element first (digital beamforming), you keep all the information: you can add it up in as many different ways as you like, simultaneously, and change your mind later (adaptive nulling, direction finding). The price is N receivers, N ADCs, a torrent of data and the need to keep all those receivers in lock-step.

**Hybrid is the practical middle.** Group elements into small subarrays, beamform each group in analog, then digitise the groups. The group beams are wide (few elements), so their squint and their pointing errors matter little; the digital stage does the fine, wideband, multi-beam work across groups.

**Why sharing an oscillator matters.** Beamforming is adding *phases*. Each receiver measures phase relative to its own local oscillator. If the oscillators aren't the same, every receiver measures against a different, drifting ruler — the relative phase rotates at the frequency difference (hundreds of Hz at 433 MHz for 1 ppm). Locking all oscillators to one reference stops the rotation, but each PLL still locks at an arbitrary phase offset; that offset must be measured (calibration) or avoided (literally sharing one LO signal).

**What averages out and what doesn't.** Adding N channels steered at a signal adds the signal coherently (×N in amplitude) and adds anything *independent* in each channel incoherently (×√N in amplitude). Thermal noise, ADC quantisation noise, randomly phased spurs and independent oscillator phase noise are independent — they fall by 10 log N relative to the signal. Anything *identical* in every channel (a spur from a shared clock, phase noise of a shared LO) adds just like a signal — no improvement, and it looks like a source at broadside.

**Why the LNA must come first.** A per-element phase shifter and combiner can have 5–10 dB of loss. Loss in front of the first amplifier adds directly to the noise figure. If you put the loss first, the array's 10 log N gain is spent on overcoming its own feed loss. With an LNA per element in front, the feed loss is "behind the gain" and barely matters (the Friis cascade, [noise figure](../07-noise-linearity/noise-figure-and-friis.md)).

## The math

### Level 1 — the architecture menu

| Architecture | Phase/delay applied at | Receivers/ADCs | Simultaneous beams | Squint | Main costs |
|---|---|---|---|---|---|
| Passive RF (one PA/LNA, corporate feed + phase shifters) | RF | 1 | 1 | yes | feed + PS loss before LNA/after PA |
| Active analog (LNA/PA + PS per element) | RF | 1 | 1 per combiner | yes | T/R per element |
| LO phase shifting | LO | 1 (mixer per element) | 1 per combiner | yes | mixer + LO distribution per element |
| IF beamforming | IF | 1 | 1 per combiner | yes (unless IF TTD) | mixer per element |
| Digital (element-level) | DSP | N | unlimited (DSP-limited) | none (digital TTD) | N ADCs, data rate, power, sync |
| Hybrid (M-element analog subarrays) | RF + DSP | N/M | many within subarray beam | subarray-limited | both, plus subarray grating lobes |
| Butler matrix | fixed passive network | 1 per beam port (or switch) | N fixed, orthogonal | yes | fixed beams, crossover loss |
| Rotman lens | fixed TTD lens | 1 per beam port | many fixed | none | size, lens loss |

Key scaling (N elements, uncorrelated per-channel impairments): beamformed SNR = N × per-channel SNR; uncorrelated spur level falls 10 log N relative to the beamformed signal; correlated terms don't fall.

### Level 2 — derivations

**(a) Phase at RF, LO or IF are equivalent (narrowband).** Element signal s(t)e^{jω_c t}e^{jφ_n} (φ_n from geometry). Mixing with an LO e^{−j(ω_L t + β_n)} gives s(t)e^{j(ω_c−ω_L)t}e^{j(φ_n − β_n)}: a phase β_n on the LO appears one-for-one on the IF signal. So a phase shifter can sit in the RF path, the LO path, or the IF path with the same beam — but the *impairments* differ: an RF phase shifter's loss and nonlinearity sit in the signal path; an LO phase shifter only needs to handle a constant-amplitude LO (a mixer is insensitive to LO amplitude variation, [mixers](../06-rf-circuits/mixers.md)); IF phase shifters work at a lower frequency. Only true delays (not phases) are equivalent at all frequencies, and a delay at IF equals a delay at RF only if the LO phase is also shifted by ω_L·τ.

**(b) Digital beamforming.** With element outputs x(t) ∈ ℂ^N, beam k is y_k = w_kᴴx; K beams are a matrix product Y = Wᴴx computed in an FPGA/GPU. Wideband: split into frequency bins (FFT/polyphase channeliser) and use a per-bin steering vector w(f) = a(θ₀, f)/N, or fractional-delay FIR filters per channel — digital TTD without squint. Adaptive weights (MVDR, nulling) and DOA estimation need exactly this access to all channels ([adaptive beamforming & DOA](adaptive-beamforming-doa.md)).

**(c) Noise, spurs and dynamic range.** Channel n output: v_n·s + e_n, where e_n collects thermal noise, quantisation noise, spurs and phase-noise products. With w = v/N, the beamformed signal power is |s|² and the error power is (1/N²)Σ_mΣ_n E[e_m e_n*]. If the e_n are uncorrelated with equal power σ², that is σ²/N — **a 10 log N improvement**. If they are fully correlated (identical in every channel), it is σ²|Σw_n|² ≈ σ²·|AF toward the error's apparent direction|² — no improvement if the error "looks like" it comes from the beam direction. Script §1 (tone at 20°, 8-bit quantisation, −40 dBc spurs): noise floor improves 3.03 / 5.94 / 9.02 / 12.00 dB for N = 2 / 4 / 8 / 16 (10 log N = 3.01 / 6.02 / 9.03 / 12.04); a randomly phased spur falls by the same amounts on average; a spur with identical phase in every channel (shared-clock leakage) is suppressed only by the array factor toward broadside (−13 dB for 8 elements when the beam is at 20°) and not at all when the beam is at broadside. ADI summarise the design goal as "correlation coefficient 0" for all RF impairments, to get the 10 log N improvement in both noise and spurs [4].
- **Nonlinear products are steered elsewhere.** The h-th harmonic (or an intermod product) generated in channel n inherits h× the element phase, i.e. a phase ramp that points it at a *different* apparent direction; the beam steered to θ₀ then suppresses it by the array factor at that offset (8 elements, θ₀ = 20°: H2 −13.0 dB, H3 −19.6 dB; θ₀ = 30°: exact nulls) — script §2. Frequency planning plus **forced decorrelation** (offsetting each channel's LO by a small amount and removing it with the NCO, so spurs land with pseudo-random phases) makes the remaining spurs uncorrelated [4].
- **The ADC sees the full interferer.** Spatial filtering happens *after* digitisation in DBF: an interferer 30 dB stronger than the signal arriving in a sidelobe is 30 dB stronger in every ADC. The array's sidelobe suppression does not raise each ADC's clipping level. So DBF needs per-channel dynamic range at least that of a single-antenna receiver; the array then adds 10 log N on top. Analog beamforming before the ADC reduces the interferer by the sidelobe level at the ADC — but not at the per-element LNAs.

**(d) Phase noise: shared vs independent LOs.** Let channel n's LO phase be φ_n(t) = √ρ·φ_c(t) + √(1−ρ)·φ_i,n(t) (common part φ_c, independent parts φ_i,n, equal variance). For small phase noise the beamformed phase-noise power is proportional to var(Σφ_n/N) = σ²(ρ + (1−ρ)/N), so relative to one channel
$$\text{improvement} = 10\log_{10}\frac{N}{1+(N-1)\rho}.$$
ρ = 1 (one LO split to all channels): 0 dB; ρ = 0 (independent synthesizers): 10 log N; ρ = 0.5: at most 3 dB (Monte Carlo agrees within 0.1 dB, script §3). In a real array with one reference and a PLL per channel, ρ is a function of offset frequency: close-in (inside the PLL bandwidth) the reference dominates and is correlated; far-out the VCOs dominate and are uncorrelated, improving 10 log N [5]. Correlated LO phase noise is not *worse* than one channel's — it is simply not improved, and it still causes reciprocal mixing of strong interferers ([phase noise](../07-noise-linearity/phase-noise-and-jitter.md)).

**(e) What "coherent" requires.** For receivers n = 1…N:
1. *Frequency coherence*: all LOs and sample clocks derived from one reference. Otherwise relative phases rotate at Δf = f·Δppm: 433 MHz, 1 ppm → 433 Hz (full turn every 2.3 ms); 5.8 GHz, 20 ppm → 116 kHz (script §6).
2. *Phase determinism*: even with a shared reference, each integer-N or fractional-N PLL locks at an arbitrary phase after each tune (and RTL-SDR-class tuners also have per-chip offsets). Either share a single LO signal (Pluto's two RX channels, B210, AD9361/ADRV9009 multi-chip sync), or **calibrate after every retune** by injecting a common signal (KrakenSDR's built-in noise source; [calibration](array-calibration.md)).
3. *Time alignment*: sample streams must be aligned to a fraction of the inverse bandwidth. A skew Δt is a delay error: phase error 2πf_bb·Δt at baseband offset f_bb (100 ps at 20 MHz → 0.72°; 10 ns at 1 MHz → 3.6°). High-speed converters use JESD204B/C subclass 1 with a shared SYSREF for deterministic latency; USB SDR arrays align by cross-correlating the calibration signal (KrakenSDR's DAQ firmware estimates sample delays this way).
4. *Clock jitter* limits each ADC's SNR as −20 log(2πf_in·σ_j) (1 ps at 100 MHz → 64 dB; 50 fs at 2.4 GHz direct sampling → 62.5 dB) — uncorrelated jitter improves 10 log N across the array, correlated (shared-clock) jitter does not ([data converters](../05-analog-electronics/data-converters-adc-dac.md)).

**(f) Analog beamformer noise cascade.** Element chain: LNA (gain G, NF 1.5 dB) → beamformer channel (8 dB loss) → ideal N-way combiner → receiver (NF 10 dB). A lossless combiner passes coherent signals with power gain N relative to one input and passes uncorrelated noise at the *average* input level. Script §5 (array SNR relative to one ideal element's input SNR): N = 8 → +7.0 dB with G = 25 dB, +3.8 dB with G = 15 dB, **−9.0 dB with no LNA** (ideal +9.0 dB). N = 64, no LNA: +0.1 dB instead of +18 dB. The 8 dB beamformer loss must sit behind ≳ 20 dB of LNA gain. This is why beamformer ICs are paired with per-element LNA/PA front-end modules.

**(g) Butler matrix.** For N = 2^n elements, a network of (N/2)log₂N 90° hybrids plus fixed phase shifters (and crossovers) connects each of N beam ports to all N elements with equal amplitude and progressive phase (2m − 1)π/N — it is the FFT butterfly implemented in transmission lines [8]. Beam m points at sinθ_m = (m − ½)λ/(Nd): for N = 4 at λ/2, ±14.5° and ±48.6°; for N = 8: ±7.2°, ±22.0°, ±38.7°, ±61.0° (script §4). The beams are orthogonal (W Wᴴ = I to 1e−15), which is why a lossless network can form them all at once; adjacent beams cross at 1/(N sin(π/2N)) → **−3.70 dB (N = 4), −3.87 dB (N = 8), −3.92 dB (N → ∞)**. (A glossary-level web source quoting −3.0 dB for N = 8 is not reproduced by the array factor [11].) Because the phases are fixed, the beams squint with frequency like any phase-steered array. Uses: switched-beam receivers (one receiver + SP4T switch), multi-beam base stations, beam-space processing.

**(h) Rotman lens.** A parallel-plate (or microstrip/stripline) region with beam ports on one curved contour and array ports on another; the path lengths from each beam port to each array element are designed to equal the geometric delays for that beam's direction (three perfect focal points in the classic design) [9]. It is therefore **true-time-delay**: beams do not squint, and bandwidths of an octave or more are possible. Costs: size (several λ), spillover/port-matching losses, and fixed beams. A Rotman lens on Rogers substrate is a feasible student project at 5.8–24 GHz.

### Level 3 — advanced considerations

- **Multiple-beam networks and the Stein limit**: a lossless passive network can only form simultaneous beams without loss if the beams are orthogonal; non-orthogonal (closely spaced, overlapping) beams from one aperture must waste power (Stein 1962 [13]). Digital beamforming sidesteps this because each extra beam is just more arithmetic after the (already noisy) LNAs.
- **Subarray grating lobes**: in a hybrid array, digital steering across subarrays of pitch D_s = Md is a "sparse" array of pitch D_s; its grating lobes (spacing λ/D_s in u) are suppressed only by the subarray pattern. Digital scanning therefore stays within about ±½ subarray beamwidth unless the analog subarray beam is re-steered too; overlapped subarrays shape the subarray pattern into a flat-topped sector to push this further (Mailloux ch. 8 [1]).
- **Element-level direct RF sampling** (RF-sampling ADCs/DACs, RFSoC-class devices) removes mixers and LOs altogether; synchronisation reduces to clock distribution and SYSREF.
- **MIMO radar** uses N_t transmitters × N_r receivers to synthesise a virtual array of N_t·N_r elements; the receive side is a DBF array ([MIMO radar](../11-radar/mimo-radar-virtual-arrays.md)).
- **Photonic TTD, time-modulated arrays** (switching elements on/off in time to create harmonics beams) and lens/reflectarray hybrids exist for special needs.

## Design equations & rules of thumb

| Rule | Validity | Value |
|---|---|---|
| DBF SNR gain = 10 log N | uncorrelated channel noise | 8 ch: 9.0 dB |
| Uncorrelated spur improvement = 10 log N | random spur phases | forced decorrelation helps |
| Correlated spur improvement = −20 log\|AF(spur direction)\| | identical-phase spurs | 0 dB at broadside |
| Phase-noise improvement = 10 log(N/(1+(N−1)ρ)) | LO correlation ρ | shared LO: 0 dB |
| Relative phase drift = 360°·f·Δppm per second | free-running LOs | 433 MHz, 1 ppm: 1 turn / 2.3 ms |
| Skew phase error = 360°·f_bb·Δt | sample-time misalignment | 100 ps @ 20 MHz: 0.72° |
| Jitter SNR = −20 log(2πf_inσ_j) | per ADC | 1 ps @ 100 MHz: 64 dB |
| Raw data rate = N·f_s·2·bits | complex baseband | 8 × 61.44 MS/s × 12 b: 11.8 Gb/s |
| LNA gain before beamformer ≳ loss + 15 dB | analog beamformers | 8 dB loss → ≥ 23 dB LNA |
| Butler beams: sinθ_m = (m−½)λ/(Nd); crossover −3.7…−3.9 dB | N = 2^n | N = 4 λ/2: ±14.5°, ±48.6° |
| Hybrid digital scan ≲ ±½ subarray beamwidth | subarray pitch > λ/2 | else subarray grating lobes |

## Worked examples

**Example 1 — four ways to build a 4-element 2.4 GHz receive array.**
1. *Passive analog*: four patches → four digital phase shifters (≈5–6 dB loss each) → Wilkinson 4:1 → LNA → one SDR. Cheapest, but the ≈6 dB phase-shifter loss plus ≈0.5 dB combiner loss sits before the LNA: the array SNR advantage (6 dB) is cancelled. Don't.
2. *Active analog*: LNA per element (≥ 20 dB gain) → phase shifter → Wilkinson → one SDR: ≈ +5 dB of the ideal +6 dB (script §5 scaling), one steerable beam.
3. *Butler 4×4 + SP4T switch + one SDR*: four fixed beams at ±14.5°, ±48.6°, crossovers −3.7 dB; zero phase-shifter control, cheap "electronic tracking" with a scalloping loss of up to 3.7 dB between beams.
4. *Digital*: four coherent receivers (two 2-channel SDRs sharing a reference and calibrated, or a multi-channel coherent SDR — KrakenSDR only covers 24–1766 MHz [10], so not at 2.4 GHz), full DOA/MVDR capability, 4 × ADC data. See [DIY projects](diy-phased-array-projects.md).

**Example 2 — why the 433 MHz "two RTL-SDRs" array fails, and how to fix it.** Two dongles with independent 28.8 MHz crystals 1 ppm apart: the relative phase at 433 MHz rotates 433 turns per second, so no stable beam exists. Drive both from one crystal (KerberosSDR/KrakenSDR approach): rotation stops, but each tuner's PLL locks at an arbitrary phase and the USB sample streams start at arbitrary times. Inject one noise source into both inputs, cross-correlate to find the sample offset and the phase difference, correct, and repeat after every retune [10]. Now it is a coherent 2-element interferometer.

**Example 3 — ADI Phaser as a hybrid array.** CN0566: 8 elements → two 4-channel ADAR1000 analog beamformers → each summed output downconverted (LTC5548 mixer, ADF4159 LO) to ≈2 GHz IF → Pluto's two coherent RX channels [6]. It is a 2-subarray hybrid: analog steering within each half, and the two digital channels allow monopulse-style Σ/Δ processing or a 2-element digital interferometer on top.

**Example 4 — data-rate budget.** KrakenSDR: 5 × 2.4 MS/s × 2 × 8 bit = 192 Mb/s (fits USB 2 aggregates, processed on a Raspberry Pi-class host). An 8-channel AD9361-class array at 61.44 MS/s, 12-bit: 11.8 Gb/s — must beamform/decimate in an FPGA before it reaches a PC. A 64-element 250 MS/s 14-bit direct-sampling array: 448 Gb/s — beamforming must be in the FPGA fabric next to the ADCs ([FPGA for SDR](../14-sdr-dsp/fpga-for-sdr.md)).

**Example 5 — does the array reduce phase noise?** Eight channels on one shared LO: the beamformed carrier's phase-noise-to-carrier ratio is unchanged (ρ = 1 → 0 dB). With eight independent synthesizers from a common reference, far-out VCO noise (outside the PLL loop bandwidth) improves ≈9 dB, while close-in noise (reference-dominated) doesn't [5]. For FMCW radar range sidelobes, the close-in phase noise of the shared reference/ramp generator is what matters, so the array doesn't help there.

## Practical notes
- **LO distribution** for LO-phase-shifted or multi-mixer arrays: use a tree of equal-length lines/buffers; LO amplitude differences matter little (mixers are LO-saturated) but phase differences are calibration terms. Temperature gradients along long LO lines drift the phases.
- **Shared-reference SDRs** (USRPs, bladeRF, Plutos with external clock): frequency-locked but phase-random per retune, and some chips' internal dividers wake up in random states — plan for calibration at every tune.
- **Put gain control after the LNA** and phase control where its loss is behind gain.
- **Beamformer ICs** (4-channel ADAR1000-class, 8–16 channel mmWave ICs) integrate phase shifter, VGA and T/R switching; their per-channel loss/NF sets how much LNA gain you need ([components](phase-shifters-ttd-components.md)).
- **Thermal**: N receivers dissipate N× the power; a 16-channel digital array can easily be 20–50 W — heat changes phase. Calibrate at operating temperature.
- **For DOA and adaptive nulling you need DBF** (or at least several digital channels): an analog single-beam array can only scan and look for the maximum.

## Case study: Starlink-class LEO user terminal

*Added 2026-10-13 (W5-S9, gap G-12-02). Cross-checks by `tools/verify/s9_leo_terminal.py` (ALL PASS). Regulatory-filing and spec-sheet numbers are primary. Element and chip counts come from teardowns reported second-hand (medium–low confidence). Everything marked "inferred" is our arithmetic, not a SpaceX statement.*

**Why it is the reference design.** It is the first mass-produced electronically steered array: millions of Ku-band flat panels that track 550 km satellites crossing the sky in minutes. Almost every topic on this page appears in it: element-level analog beamforming in RFICs, a front-end per element, a triangular lattice, scan loss, and a mechanical tilt to keep scan angles modest.

**Public facts.**

| Item | Value | Source (confidence) |
|---|---|---|
| Bands | Rx 10.7–12.7 GHz; Tx 14.0–14.5 GHz; uplink carriers up to 60 MHz (60M0D7W), up to 64QAM | FCC STA narratives [14] (high) |
| Elevation mask | satellites above 25° only | [14] (high) |
| Tx power and EIRP | 0.76 W / 33.4 dBW at boresight; 4.06 W / 38.2 dBW at maximum slant (power raised to hold a constant level at the satellite) | [14] (high) |
| Gain | Rx 33.2 dBi, Tx 34.6 dBi at boresight; 30.6 / 32.0 dBi at maximum slant | [14] (high) |
| Size, field of view | Gen1 round ≈ 0.59 m; Standard 594 × 383 mm, 75–100 W; Mini 298.5 × 259 mm, 25–40 W; FoV **110°** (±55°) | Starlink spec sheets [15] (high); Gen1 size [16] (medium) |
| Elements, lattice | Gen1: **1,280** elements in a hexagonal (triangular) honeycomb, ≈ 500–540 mm active diameter, stacked patches with dummy edge elements | teardown write-ups [16] (medium–low) |
| Beamformer chips | Gen1: 80 large + 640 small RF ICs. Each large IC plus its surrounding small chips forms a 16-channel module. ST digitally controlled beamformer "Shiraz" (a 16-channel die) with front-end modules "Pulsar" (Rx and Tx paths) | [16], [17]; Wouters (DEF CON 30) [18] (medium) |
| Later revisions | rev4 Standard ≈ 1,536 elements; Mini ≈ 571 elements with 2 beamformers; "rev5" ≈ 820 elements, 2 beamformers | Kutkov as reported by mezha.ua [19] (low: second-hand, pre-release) |

*Contradiction recorded:* the Signal Path X-ray of a Gen1 board shows 8 small chips per 16-channel beamformer (two channels per FEM). Wouters describes 16 FEMs per beamformer. These may be different revisions; neither source states a revision.

**Architecture, read through this page.** 80 beamformers × 16 channels = 1,280: **one RFIC channel (phase, gain, T/R) per element, analog RF combining**, i.e. the "active analog" row of the Level 1 table, with per-element FEMs supplying the LNA/PA in front of the beamformer loss, as §(f) requires. Full digital beamforming is out of reach: 1,280 elements × 240 MS/s × 16 bit ≈ **4.9 Tb/s**, versus the 11.8 Gb/s of an 8-channel SDR array (Example 4). Later revisions put more channels into each beamformer IC (the Mini's two beamformers serve ≈ 571 elements), which cuts parts count and cost. That is the commercial direction for hobby-scale designs too ([components](phase-shifters-ttd-components.md)).

**Cross-checks against the formulas in this domain** (script):
1. **EIRP = flange power + gain:** 4.06 W (+6.09 dBW) + 32.0 dBi = 38.09 dBW (filed 38.2); 0.76 W + 34.6 = 33.41 (filed 33.4). If all elements transmit, each element radiates only **3.2 mW (5 dBm)**. Element-level arrays need many tiny PAs, not one big one.
2. **Lattice (inferred).** 1,280 elements in a 500–540 mm circle on a triangular lattice imply a spacing of **13.3–14.4 mm**: 0.52–0.56 λ at 11.7 GHz but 0.63–0.68 λ at 14.25 GHz. The rev4 and Mini outlines give ≤ 13.1 and ≤ 12.5 mm. Grating-lobe-free scan for an equilateral triangular lattice, $d/\lambda \le 2/(\sqrt3(1+\sin\theta_{max}))$ (brute-force reciprocal-lattice check agrees to 0.02°): with 13.3 mm, unlimited across the Rx band but **55.6° at 14.25 GHz and 52.5° at 14.5 GHz**, matching the ±55° field of view. The triangular lattice allows 2/√3 = 1.155× the area per element of a square lattice for the same scan, **13.4 % fewer elements** ([planar arrays](planar-arrays-element-pattern-coupling.md), [beam steering](beam-steering-grating-lobes.md)).
3. **Aperture efficiency.** $4\pi A/\lambda^2$ is 35.7–36.4 dBi at 11.7 GHz and 37.5–38.1 dBi at 14.25 GHz. The filed gains are 2.5–3.5 dB lower (aperture efficiency ≈ 45–55 %), which is plausible once taper, element and radome losses and a gain reference at the "antenna flange" are counted.
4. **Scan loss.** Boresight → maximum slant costs 2.6 dB on both Rx and Tx. Under a $\cos\theta$ projected-area law that is a 56.7° scan (51° for cos^1.3), consistent with ±55°. A flat, zenith-facing panel would have to scan 65° to reach 25° elevation (−3.7 dB, and past the Tx grating-lobe limit). That is why the panels tilt (actuated Gen1, kickstands) towards the part of the sky the satellites occupy.
5. **Geometry and path loss.** For the 550 km shell the slant range is 1,123 km at 25° elevation versus 550 km overhead. FSPL is 174.8 / 176.5 dB at 11.7 / 14.25 GHz (168.6 / 170.3 overhead), a **6.2 dB** span. The filed EIRP span is 4.8 dB; the 1.4 dB difference presumably sits in the satellite's receive pattern (not stated).
6. **Uplink.** $C/N_0 = 38.2 - 176.5 + G/T_{sat} + 228.6$ = 90.3 dB-Hz + $G/T_{sat}$. In 60 MHz that is **C/N = 12.5 dB for a satellite G/T of 0 dB/K** (7.5 / 17.5 dB for −5 / +5 dB/K). Satellite G/T is not public, so this only shows why adaptive modulation up to 64QAM is credible.
7. **Downlink G/T (assumed $T_{sys}$).** $G/T = 33.2 - 10\log T_{sys}$: 11.4 / 9.2 / 7.2 dB/K for 150 / 250 / 400 K at boresight, and 2.6 dB lower at maximum slant.

**Lessons for a student array.** Put the LNA/PA at the element and the beamforming in an RFIC. Use a triangular lattice sized for the *highest* frequency and the largest scan you really need. Tilt the panel mechanically so electronic scan stays within about ±50°. Budget DC power and heat per channel (75–100 W for the Standard, with snow-melt included). Calibrate in production ([calibration](array-calibration.md)). At 10 GHz an ADAR1000-class RFIC (4 channels) plus FEMs is the hobby analogue ([DIY projects](diy-phased-array-projects.md)).

## Common mistakes & misconceptions
- **"A phased array can scan to the horizon for free."** Scan loss (≈ 2.6 dB at the Starlink terminal's ±55°) and grating lobes at the top of the band set the usable field of view; production terminals tilt mechanically to avoid extreme scan angles.
- **"Digital beamforming is always better."** It gives flexibility; it costs N receivers' power and cost, huge data, strict synchronisation, and each ADC gets no protection from out-of-beam interferers.
- **"Two SDRs locked to the same GPSDO are coherent."** They are frequency-locked; phase is random after every retune and sample timing is unaligned. Calibrate.
- **"The array averages out phase noise."** Only uncorrelated phase noise; a shared LO's phase noise passes straight through.
- **"The beamformer's loss doesn't matter because I have array gain."** It adds to the noise figure unless there is LNA gain in front (8 elements, no LNA: −9 dB instead of +9 dB).
- **"A Butler matrix can steer anywhere."** It forms N fixed beams; between them you lose up to ≈3.9 dB unless you switch/combine ports.
- **"Hybrid arrays have no squint."** Within each analog subarray they do, and digital steering beyond the subarray beam produces subarray grating lobes.
- **"Harmonics add coherently in a digital array."** They are steered to other directions (or spread, with forced decorrelation); what adds coherently is anything common to all channels.

## How to simulate / verify
- `tools/verify/array_architecture.py` (<1 s): Monte Carlo of DBF noise/quantisation improvement, averaged uncorrelated vs correlated spurs, harmonic steering, LO phase-noise correlation formula, Butler matrix beams/orthogonality/crossover, analog noise cascade, synchronisation, jitter and data-rate numbers.
- GNU Radio: build a 2-channel coherent receiver (one Pluto or B210) with a shared LO and apply complex weights; compare with two independent SDRs to *see* the phase rotation ([GNU Radio](../14-sdr-dsp/gnu-radio-and-software-stack.md)).
- `tools/verify/s9_leo_terminal.py` (< 1 s, **ALL PASS**): LEO terminal EIRP, lattice spacing and triangular-lattice grating-lobe limit (brute-force check), aperture efficiency, scan loss, 550 km slant/FSPL, uplink C/N, G/T.
- For analog designs, a spreadsheet Friis cascade per channel plus the combiner (the script's §5 function) is enough to size the LNA.

## Open questions / gaps
- ADI's "Hybrid beamforming receiver dynamic range — theory to practice" article (analog.com) timed out twice and was not read; the hybrid dynamic-range statements rely on the ADI LO-phase-noise and forced-decorrelation articles plus our own derivation.
- No measured per-element power/cost figures for DIY-scale digital vs analog arrays have been compiled here; see [components](phase-shifters-ttd-components.md) and [DIY projects](diy-phased-array-projects.md).
- Rotman-lens design equations (focal arcs, three-focal-point solution) are only described qualitatively.
- Starlink terminal: element counts, lattice and chip counts are second-hand teardown figures (8 vs 16 FEMs per beamformer conflict); the element spacing is inferred; satellite G/T and downlink EIRP are not public, so only the uplink and G/T are budgeted.

## Sources
1. R. J. Mailloux, *Phased Array Antenna Handbook*, 2nd ed., Artech House, 2005, ch. 8 "Special array feeds for limited field-of-view and wideband arrays" (subarrays, time delay, overlapped subarrays) and ch. 1. (textbook)
2. R. C. Hansen, *Phased Array Antennas*, 2nd ed., Wiley, 2009 — feeds, multiple-beam networks (Butler, Blass, Rotman), subarrays. (textbook)
3. P. Delos, B. Broughton, J. Kraft, "Phased Array Antenna Patterns — Part 2," *Analog Dialogue* 54(2), 2020 — hybrid beamforming mitigates squint; DBF implements TTD in DSP. (app note)
4. P. Delos, M. Jones, M. Robertson, "RF transceivers enable forced spurious decorrelation in digital beamforming phased arrays," Analog Devices technical article / *Microwave Journal*, 2018 — 10 log N for uncorrelated noise and spurs; correlated spurs; LO offset + NCO compensation (ADRV9009). (app note; summary via search)
5. P. Delos, "System-level LO phase noise model for phased arrays with distributed phase-locked loops," Analog Devices technical article, Nov. 2018 (reprinted by Embedded Computing Design) — reference noise correlated, distributed PLL/VCO noise uncorrelated and reduced 10 log N. (app note)
6. M. Lichtman, *PySDR*, "Hands-on with Phaser" — CN0566 signal chain (2 × ADAR1000, LTC5548, ADF4159, Pluto). (tutorial)
7. H. L. Van Trees, *Optimum Array Processing*, Wiley, 2002, ch. 2–3 — beam-space processing, broadband beamformers (FFT/tapped-delay-line). (textbook)
8. J. Butler, R. Lowe, "Beam-forming matrix simplifies design of electronically scanned antennas," *Electronic Design* 9:170–173, 1961. (trade journal; cited from standard texts, not read)
9. W. Rotman, R. F. Turner, "Wide-angle microwave lens for line source applications," *IEEE Trans. Antennas Propag.* 11(6):623–632, 1963. (peer-reviewed; cited from standard texts, not read)
10. KrakenRF, *KrakenSDR documentation wiki* (Home; Antenna Array Setup; Web Interface), github.com/krakenrf/krakensdr_docs/wiki — 5 × R820T2/RTL2832U, shared clock, 24–1766 MHz, 2.56 MHz BW, noise-source coherence calibration. (vendor docs)
11. RF Essentials, "Beamforming network | Butler matrix & Rotman lens" glossary page, rfessentials.com — Butler/Rotman qualitative description; its −3.0 dB (N = 8) crossover figure is contradicted by our computation. (web glossary — low reliability)
12. `tools/verify/array_architecture.py` — all numbers marked "script". (own verification)
13. S. Stein, "On cross coupling in multiple-beam antennas," *IRE Trans. Antennas Propag.* 10(5):548–557, 1962 — orthogonality condition for lossless multiple-beam networks. (peer-reviewed; cited from standard texts, not read)
14. SpaceX Services, FCC experimental STA narratives: maritime user-terminal STA (ELS GetAtt id 259301, 2020) and STA 1169-EX-ST-2022 (Starship) — 14.0–14.5 / 10.7–12.7 GHz, 25° minimum elevation, 0.76–4.06 W, 33.4–38.2 dBW, gains 33.2/34.6 and 30.6/32.0 dBi, 60M0D7W. https://apps.fcc.gov/els/GetAtt.html?id=259301 (regulatory filing; read in full)
15. Starlink, *Specification sheet — Standard* and *— Mini* (starlink.com/public-files, accessed 2026-10-13) — dimensions, "electronic phased array", FoV 110°, power. (manufacturer)
16. Teardown write-ups of the Gen1 dish: Hackaday, "Literally tearing apart a SpaceX Starlink antenna" (2020-11-25, K. Keiter teardown) and "Starlink satellite dish X-rayed to unlock RF magic inside" (2021, The Signal Path X-ray: 1 large IC + 8 chips = 16-channel module); secondary summaries (radiowalkietalkie.com teardown article; C. Arnold, LinkedIn) — 1,280 elements, hexagonal, 500–540 mm, 80 + 640 RF chips. (secondary / blog — medium–low)
17. STMicroelectronics newsroom, "STMicroelectronics and SpaceX celebrate a decade-long partnership key to Starlink global connectivity" (newsroom.st.com) — ST supplies Starlink terminal ICs. (press release; context only, seen via search)
18. L. Wouters, "Glitched on Earth by humans: a black-box security evaluation of the SpaceX Starlink user terminal," DEF CON 30, 2022 (transcript) — ST digital beamformer "Shiraz", 16 channels, front-end modules "Pulsar" with Rx and Tx paths. (conference talk)
19. mezha.ua (2026), report of O. Kutkov's analysis — rev4 1,536 elements, Mini 571, rev5 820 with two beamformers, FEM "Pez". (news report of expert blog — low; pre-release)
20. `tools/verify/s9_leo_terminal.py` — case-study numbers. (own verification)
