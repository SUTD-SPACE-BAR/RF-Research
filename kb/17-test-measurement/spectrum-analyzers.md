---
title: Spectrum analyzers — superheterodyne architecture, RBW/VBW, sweep time, DANL, detectors and the −2.51 dB log-averaging bias, noise and channel power, internal distortion checks, tinySA and budget analyzers, and measuring a LoRa transmitter safely
domain: 17-test-measurement
slug: spectrum-analyzers
tags: [spectrum-analyzer, rbw, vbw, danl, detector, log-average, rms, noise-marker, channel-power, occupied-bandwidth, harmonics, attenuator, preamplifier, image, phase-noise, tinysa, siglent, rigol, lora, transmitter-test]
prerequisites: [../00-math-foundations/decibels-and-log-units.md, ../00-math-foundations/probability-random-processes-and-psd.md, ../07-noise-linearity/thermal-noise-and-noise-temperature.md, ../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md]
related: [rf-power-measurement.md, noise-figure-measurement.md, phase-noise-measurement.md, sdr-as-test-equipment.md, signal-generators-and-sources.md, lab-setup-by-budget.md, rf-bring-up-debug-playbook.md, ../15-lora-ism-radios/lora-phy-css-math.md, ../15-lora-ism-radios/ism-band-plans-duty-cycle.md, ../19-regulations-safety/certification-fcc-ce-imda.md, ../14-sdr-dsp/fft-spectral-analysis-windows.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Spectrum analyzers

## Questions this page answers
- How does a swept spectrum analyzer work, and what do RBW and VBW actually do?
- Why does the noise floor drop 10 dB when I reduce RBW by 10×, but my CW signal stays the same?
- Why does the analyzer read noise 2.5 dB too low, and which detector should I use for noise, LoRa and CW?
- How do I measure channel power and occupied bandwidth correctly?
- Is that spur real, or is my analyzer making it?
- How do I measure a 1 W LoRa module's power and harmonics without destroying my tinySA?
- What can a tinySA / tinySA Ultra do, and when do I need a Siglent/Rigol-class analyzer?
- Why does my SA say −60 dBc/Hz phase noise when the TCXO datasheet says −130?
- Why does the noise floor jump up at certain frequencies (band edges) on a microwave analyzer?
- What is the big signal at 0 Hz, and why can't I measure low frequencies with my SA?
- How do I measure gain and phase below 100 kHz, and why are my milliohm PDN readings wrong there?

## TL;DR
- A swept SA is a **superheterodyne receiver** tuned across the span: attenuator → (preamp) → mixer + swept LO → IF gain → **RBW filter** → envelope/log detector → **VBW filter** (video smoothing) → display detector per trace point [1].
- **RBW** sets resolution *and* noise: displayed noise changes by 10 log(RBW₂/RBW₁) while a CW tone stays put (verified: 10.0 dB/decade). **Sweep time** ST ≈ k·span/RBW², k ≈ 2–3 for analog filters [1] (10 MHz span at 3 kHz RBW → 2.2–3.3 s).
- **DANL** (dBm) ≈ −174 + NF_SA + 10 log(RBW) − 2.5 (log-averaged display). A tinySA's −102 dBm at 30 kHz RBW means NF ≈ 27–30 dB; the Ultra's LNA brings it to ≈ 6–8 dB; a Siglent SSA3021X Plus with preamp ≈ 13–19 dB (script).
- **Detectors and averaging**: for *noise*, log (dB) averaging reads **2.51 dB low** (= 10γ/ln 10), voltage averaging **1.05 dB low**; RMS/power averaging reads true. The RBW's noise bandwidth is 1.065× (Gaussian) to 1.13× (4-pole) its 3 dB width [1] — noise markers correct for all of this; manual readings must.
- **Channel power** = integrate the PSD with an RMS detector; **occupied bandwidth** = the band holding 99 % of the power. A LoRa SF7/125 kHz chirp has a 99 % OBW of ≈ 133 kHz (simulated).
- **Constant-envelope chirps fool your intuition**: with peak detect + max hold, a LoRa chirp reads its full power even with RBW = 10 kHz (−0.55 dB) — because the chirp dwells in each RBW long enough; an RMS/average trace reads the *density* instead (≈ 10 log(RBW/125 kHz)).
- **Is it real?** Add 10 dB of input attenuation: real signals stay (the display compensates); analyzer-generated 2nd-order products drop 10 dB and 3rd-order 20 dB [1]. Images move the wrong way when you shift the centre frequency; the tinySA has a spur-suppression mode [2].
- **Band edges and low frequencies** (Level 3b): harmonic-mixing bands raise DANL and phase noise (20 log N) and add band-switch uncertainty — N9020B DANL −151 dBm/Hz below 2.1 GHz but −136 at 20–26.5 GHz (N = 4); the 0 Hz line is LO feedthrough, and DANL is 20 dB worse below 1 MHz. Gain–phase work below 100 kHz needs a gain-phase analyzer; cable-shield ground loops corrupt milliohm shunt-thru readings (≈ 20 % at 100 kHz in the model).
- **1 W LoRa into a tinySA Ultra**: absolute max input +6 dBm, suggested ≤ 0 dBm, best linearity below −25 dBm [2] → use **≥ 40 dB of attenuation**, first pad rated ≥ 2 W.

## Intuition (no math)
A spectrum analyzer is a radio receiver with a very accurate volume meter that is slowly tuned from one end of the span to the other, drawing the meter reading as it goes. The RBW is the width of the receiver's IF filter: a narrow filter can separate two close tones and lets in less noise, but it takes longer to "ring up", so you must tune more slowly. The detector decides what single number to draw for each screen pixel (the biggest value seen, a random sample, the average…). Because the analyzer is calibrated to read *sine waves* correctly, anything that is not a sine wave — noise, a digitally modulated signal, a chirp, a burst — needs you to think about what the detector and averaging are doing to it.

The analyzer also has a front end with a mixer, and mixers are nonlinear. Hit it too hard and it invents harmonics, intermodulation and images that look exactly like real signals. Much of good SA practice is about keeping the mixer level low enough and checking that what you see is real.

## The math

### Level 1 — the core relations
- **CW tone**: displayed level = input power (calibrated), independent of RBW (as long as RBW ≪ spacing to other signals).
- **Noise with power density N₀ (dBm/Hz)**: displayed power ≈ N₀ + 10 log(ENBW), ENBW = 1.065 × RBW (Gaussian filter).
- **DANL and analyzer noise figure** (AN 150 [1]): with a sine-calibrated, log-averaged display,
  $$\text{DANL} \approx -174\ \text{dBm/Hz} + NF_{SA} + 10\log_{10}(\text{RBW}/1\,\text{Hz}) - 2.5\ \text{dB}.$$
  Keysight defines NF_SA for noise signals as DANL − 10 log RBW + 174 + 2.5 dB (their example: −110 dBm in 10 kHz → 26.5 dB) [1].
- **Sweep time**: ST = k·span/RBW², k ≈ 2–3 [1].
- **Channel power**: P_ch = Σ PSD(f_i)·Δf over the channel (RMS detector, trace in dBm/Hz or corrected by bin width/ENBW).
- **Signal near the noise floor** (power detector): if a reading is S dB above the noise-only floor, the true tone is 10 log(10^{S/10} − 1) dB above it — subtract 3.02 dB at S = 3, 1.26 dB at 6, 0.46 dB at 10, 0.04 dB at 20 dB.

### Level 2 — where the noise corrections come from
Band-limited Gaussian noise at the IF has a Rayleigh-distributed envelope r with mean power E[r²] = 2σ². The power (exponential distribution) has mean 2σ², but:
- **Voltage (envelope) averaging**: E[r] = σ√(π/2) = 1.2533σ; an analyzer calibrated to show a sine's rms displays E[r]/√2 = 0.886σ, i.e. 20 log(√π/2) = **−1.05 dB** below the true rms √2σ/√2 = σ [1].
- **Log averaging**: E[10 log₁₀ P] − 10 log₁₀ E[P] = −10γ/ln 10 = **−2.507 dB** (γ = 0.5772, Euler's constant), because for exponentially distributed P, E[ln P] = ln E[P] − γ. Monte Carlo (2 × 10⁶ samples): −1.050 dB and −2.511 dB.
- **RBW noise bandwidth**: Gaussian |H|² = exp(−4 ln2 f²/B²) gives ENBW = √(π/(4 ln 2))·B = 1.0645 B; n synchronously-tuned single poles give 1.220 (n = 2), 1.155 (3), 1.128 (4), 1.114 (5). AN 150 quotes 1.05–1.13 for Keysight near-Gaussian filters and uses 0.5 dB as a compromise, so the total correction for log-averaged noise read on the marker is +2.5 − 0.5 = **+2.0 dB**, for voltage averaging +0.55 dB and for power averaging −0.5 dB (to normalise to a 1 Hz noise-power bandwidth, subtract a further 10 log RBW) [1].

**Why DANL falls 10 dB/decade of RBW**: displayed noise power ∝ ENBW ∝ RBW; our simulation (white noise through 1/10/100 kHz Gaussian filters) gives slopes of 10.09 and 9.99 dB/decade and an absolute level within 0.07 dB of 10 log(ENBW/f_s).

### Level 3 — dynamic range, mixer level and phase noise
- **Internal distortion**: a mixer-generated 2nd harmonic changes 2 dB per dB of mixer level, a 3rd-order product 3 dB per dB. With second-harmonic intercept SHI and third-order intercept TOI referred to the mixer, internal distortion (dBc) = −(SHI − P_mix) for 2nd order and −2(TOI − P_mix) for 3rd order [1]. Siglent's SSA3000X Plus specifies SHI +45 dBm and TOI +14 dBm (typ, most models; +10 dBm for the 1.5 GHz model) at 0 dB attenuation [3]; the tinySA IIP3 is +15 dBm (low input, 0 dB attenuation) and −5 dBm (high input) [2].
- **Optimum mixer level**: lowering P_mix by 1 dB lowers 3rd-order distortion 2 dB relative to the signal but raises noise relative to the signal by 1 dB; the best dynamic range occurs where the two are equal: DR₃ = ⅔(TOI − DANL). E.g. TOI +14 dBm and DANL −139 dBm/Hz + 10 log(1 kHz) = −109 dBm in a 1 kHz RBW → DR₃ ≈ ⅔(14 + 109) = 82 dB at a mixer level of (2·14 − 109)/3 = −27 dBm.
- **Phase noise**: the analyzer's own LO phase noise sets a floor for measuring close-in noise of your signal: SSB phase noise of the SSA3021X Plus at 1 GHz is ≤ −95 (typ −98) dBc/Hz at 10 kHz, ≤ −115 (typ −117) at 1 MHz [3]; tinySA Ultra −108 dBc/Hz at 100 kHz, −115 at 1 MHz (30 MHz carrier) [2]; LibreVNA's SA mode −103 dBc/Hz at 10 kHz (1 GHz) [4]. A good TCXO is −130 to −150 dBc/Hz at those offsets — far below any of these. Details: [phase-noise measurement](phase-noise-measurement.md).
- **Preamplifier**: an internal/external preamp lowers NF (e.g. SSA3021X Plus 200 MHz–1.5 GHz DANL −139 → −158 dBm/Hz typ [3]) but also lowers the compression/TOI referred to the input by roughly its gain — use it only for weak signals, never with strong out-of-band signals present.
- **Images and multiple responses**: a mixer responds to f_LO ± f_IF and harmonics n·f_LO ± f_IF; preselected (YIG-tracked) microwave analyzers reject them; low-cost analyzers and SDRs rely on fixed filters and high first IFs, and show images at predictable offsets (2 × IF). The tinySA's spur suppression re-measures with a different LO/IF combination and keeps only responses that do not move [2].

### Level 3b — band edges, harmonic mixing, the 0 Hz response and low-frequency limits
**Harmonic-mixing bands.** Microwave analyzers extend their range by mixing with the N-th harmonic of the first LO (or switching to a different LO/IF path). Mixer conversion loss rises with N, the analyzer raises its IF gain to keep the amplitude calibration, and the displayed noise therefore rises with it: DANL steps up at band edges (older analyzers show a clear "stair step"; modern image-enhanced harmonic mixers give a gentler slope) [1]. The LO's phase noise also rises by **20 log N** (+6 dB for N = 2, +12 dB for N = 4) [1], and each band has its own frequency-response and, on some analyzers, a **band-switching uncertainty** (AN 150's 8563EC example: ±1.0 dB for a harmonic measured in another band) [1]. Example — Keysight N9020B MXA (specification, 1 Hz RBW, log averaging, 0 dB attenuation) [8]; NF ≈ DANL + 174 + 2.5 dB (`s10_rx_tracing.py` §E):

| Range | Band (LO multiple N) | DANL (dBm/Hz) | ≈ NF (dB) |
|---|---|---|---|
| 9 kHz–1 MHz | 0 (1) | −130 (typ) | 46.5 |
| 1–10 MHz | 0 (1) | −150 | 26.5 |
| 10 MHz–2.1 GHz | 0 (1) | −151 | 25.5 |
| 2.1–3.6 GHz | 0 (1) | −149 | 27.5 |
| 3.6–8.4 GHz | 1 (1) | −149 | 27.5 |
| 8.3–13.6 GHz | 2 (2) | −148 | 28.5 |
| 13.5–17.1 GHz | 3 (2) | −144 | 32.5 |
| 17.0–20.0 / 20.0–26.5 GHz | 4 (4) | −143 / −136 | 33.5 / 40.5 |

Consequences: (1) a harmonic or spur that falls in a higher band (e.g. the 3rd–5th harmonics of a 5.8 GHz video transmitter) is measured with less sensitivity and a separate amplitude error — compare levels across a band edge only with the band-switch uncertainty included; (2) budget analyzers have the same effect in a different form: the tinySA Ultra's "ultra" mode above 800 MHz has its own accuracy and spurious behaviour [2], and low-cost analyzers that use LO harmonics show images and multiple responses near band boundaries — confirm a suspicious line with the attenuator test and by shifting the centre frequency.

**The 0 Hz response (LO feedthrough).** Tuning a superheterodyne analyzer to 0 Hz puts its first LO exactly at the first IF; the LO's leakage through the mixer then appears as a large "signal" at 0 Hz [1]. It is normal (and a handy frequency marker), but its skirt and the LO's phase noise raise the floor near 0 Hz, which is why analyzers specify DANL that worsens rapidly at low frequency (N9020B: −95 dBm/Hz at 10 Hz, −120 at 1 kHz, −130 at 9 kHz–1 MHz vs −151 above 10 MHz [8]) and why some do not display 0 Hz at all [1]. AC-coupled inputs (DC blocks) and low-frequency transformer baluns add further lower limits (typically 9–100 kHz); the basic tinySA is specified from 100 kHz ("with some limitations down to 10 kHz") [2]. For audio-frequency or sub-100 kHz work use a DC-coupled FFT analyzer, a sound card or a scope FFT instead.

**Gain–phase measurements below ~100 kHz.** VNAs start at 50–100 kHz (NanoVNA 50 kHz, LibreVNA 100 kHz) and an SA + tracking generator gives magnitude only. Below that, and for loop-gain, PDN and filter work at audio/IF frequencies, use a gain-phase (frequency-response) analyzer — a dedicated instrument, a VNA with a low-frequency gain-phase port (Keysight E5061B: 5 Hz–30 MHz [9]) or a scope with a Bode-plot function. The trap is the **test-cable ground loop**: below the cable-shield cut-off frequency $f_c=R_{sh}/(2\pi L_{sh})$ (≈ 2 kHz for RG-58-class coax [10]) the source's return current divides between its own shield and the receiver cable's shield, and the receiver measures the drop $I\,R_{sh}$ in series with the DUT. A simple model gives an error impedance $Z_{err}\approx R_{sh}/(2+jf/f_c)$: with 10 mΩ shields, **5 mΩ at DC, 0.2 mΩ at 100 kHz, 0.02 mΩ at 1 MHz** — 500 %, 20 % and 2 % of a 1 mΩ PDN impedance, but negligible for a 50 Ω filter (`s10_rx_tracing.py` §F; model and shield values illustrative). Keysight notes the same low-frequency dynamic-range loss for shunt-through measurements even on its own S-parameter ports and recommends magnetic cores or isolation transformers on the cables, or a gain-phase port whose receivers break the loop [9].

## Design equations & rules of thumb

| Quantity | Relation / value | Notes |
|---|---|---|
| Displayed noise vs RBW | Δ = 10 log(RBW₂/RBW₁) | CW unchanged |
| DANL ↔ NF | DANL = −174 + NF + 10 log RBW − 2.5 | log-avg display |
| Log-avg noise bias | −2.51 dB | 10γ/ln 10 |
| Voltage-avg noise bias | −1.05 dB | 20 log(√π/2) |
| ENBW/RBW | 1.065 (Gaussian), 1.13 (4-pole) | |
| Sweep time | ST ≈ 2–3 × span/RBW² | swept analog RBW |
| VBW | VBW ≤ RBW/10 smooths noise (doesn't change mean for power avg) | VBW ≥ 3×RBW for pulses |
| Near-noise correction | true = reading + 10 log(1 − 10^{−S/10}) | S = reading − noise-only floor (dB) |
| 2nd-order internal | changes 2 dB/dB of mixer level | add 10 dB att → drops 10 dB rel. |
| 3rd-order internal | changes 3 dB/dB | add 10 dB att → drops 20 dB rel. |
| Best 3rd-order DR | ⅔(TOI − DANL_RBW) | at P_mix = (2 TOI + DANL)/3 |
| LoRa 125 kHz OBW (99 %) | ≈ 133 kHz (SF7, simulated) | |
| Harmonic-mixing phase noise | +20 log N | N = 2: +6 dB, N = 4: +12 dB [1] |
| Shield ground-loop error | $Z_{err}\approx R_{sh}/(2+jf/f_c)$ | 10 mΩ shields, f_c 2 kHz: 0.2 mΩ at 100 kHz |
| Safe level into tinySA Ultra | < 0 dBm (abs max +6 dBm at 0 dB att) [2] | < −25 dBm for best linearity |

## Worked examples

**Example 1 — reading the noise floor correctly.** An SA with RBW 10 kHz shows a flat −110 dBm floor with log averaging. Noise density = −110 − 10 log(10 000 × 1.065) + 2.51 = −110 − 40.3 + 2.5 = −147.8 dBm/Hz. If that floor is your LNA's output with 20 dB gain, the input-referred density is −167.8 dBm/Hz, i.e. 6.2 dB above kT₀ (−174) — a first estimate of the chain's noise figure *only if* the analyzer's own contribution is negligible (check by terminating the LNA input: the floor must rise ≥ 10 dB above the analyzer-alone floor; see [noise-figure measurement](noise-figure-measurement.md)).

**Example 2 — analyzer NF from datasheets (script §4).** tinySA low-input mode: "lowest discernible signal" −102 dBm in 30 kHz → NF ≈ 27–30 dB. tinySA high-input mode −115 dBm in 30 kHz → 14–17 dB. tinySA Ultra with its 20 dB LNA: −145 dBm in 200 Hz → 6–8.5 dB (vendor NF 5 dB). Siglent SSA3021X Plus 0.2–1.5 GHz: −139 dBm/Hz preamp off → 35–37 dB; −158 dBm/Hz preamp on → 16–18.5 dB. Hence: to see a −120 dBm LoRa signal at all you need a preamp or narrow RBW; to measure noise figures you need an external low-NF preamp.

**Example 3 — sweep time budget.** Looking for spurs across 10 MHz at RBW 3 kHz: ST ≈ 2.2–3.3 s per sweep on a swept analog-filter analyzer; at RBW 100 Hz across 200 kHz: 40–60 s. Digital/FFT analyzers (and SDRs) do much better; the tinySA scans > 1000 points/s at wide RBW but slows below 30 kHz RBW [2].

**Example 4 — LoRa transmitter power, OBW and harmonics (E220-900T30D, or any 30 dBm SX126x/LLCC68 module, at 915 MHz).**
1. *Attenuation* (script §8): 10 or 20 dB pads alone would put +20/+10 dBm into the tinySA Ultra (damage). 30 dB gives 0 dBm (the suggested maximum — no margin). Use 40 dB (30 dB 2 W + 10 dB) → −10 dBm; the first pad dissipates ≈ 1 W while transmitting, so it must be rated ≥ 2 W (LoRa duty cycle helps, but a stuck-on TX does not).
2. *Power*: zero span at 915 MHz, RBW ≥ 300 kHz (≥ 2× the 125 kHz LoRa BW; tinySA offers up to 600/850 kHz [2]), peak or RMS detector — the chirp is constant-envelope, so both read the carrier power. Add back the calibrated attenuation (measure the pads' actual loss at 915 MHz with a VNA; a nominal 30 dB pad may be 30.4 dB). Alternatively channel power over 200 kHz with an RMS detector: our simulated integration recovers the power within 0.06 dB.
3. *OBW*: 99 % power bandwidth ≈ 133 kHz for SF7/125 kHz (simulated) — the regulatory channel must contain it ([ISM band plans](../15-lora-ism-radios/ism-band-plans-duty-cycle.md)).
4. *Harmonics* at 1830 and 2745 MHz: the tinySA Ultra needs its "ultra" mode above 800 MHz (±2 dB to 5.3 GHz [2]); the original tinySA cannot go above 960 MHz at all. Put a high-pass filter (e.g. > 1.2 GHz) before the analyzer to remove the fundamental — that removes the analyzer-generated harmonics and lets you drop the attenuation for sensitivity. Then check "real vs internal" with the 10 dB attenuator test.

**Example 5 — which detector for a LoRa chirp? (script §7).** With peak detection and max hold, the reading relative to the true power is −7.8 dB at RBW 3 kHz, −0.55 dB at 10 kHz, −0.01 dB at ≥ 30 kHz: the SF7 chirp sweeps at 1.2 × 10⁸ Hz/s, and an RBW filter of bandwidth B keeps up when B² ≳ sweep rate (B ≳ 11 kHz). An RMS/average detector instead reads the density ≈ 10 log(RBW/125 kHz) (−11 dB at 10 kHz). A naive user who reads "−11 dB" off an average trace and calls it the power is wrong by 11 dB; one who reads "−7.8 dB" off a 3 kHz max-hold trace is wrong by 7.8 dB.

**Example 6 — dynamic range for a two-tone IP3 test** on a Siglent-class analyzer (TOI +14 dBm; DANL −139 dBm/Hz → −109 dBm in 1 kHz RBW): the optimum mixer level is (2·14 − 109)/3 = −27 dBm, giving a best 3rd-order dynamic range of ⅔(14 + 109) = 82 dB. An LNA with OIP3 = +25 dBm driven to −20 dBm per output tone has IM3 = −2(OIP3 − P_out) = −90 dBc — *more* than the analyzer's 82 dB, so it cannot be measured at that level: fed straight in, the analyzer's own IM3 at −20 dBm mixer level is −2(14 + 20) = −68 dBc and swamps the DUT's. Instead raise the DUT drive (P_out = 0 dBm → IM3 = −50 dBc, attenuate 20 dB before the analyzer so its own IM3 is −2(14 + 20) = −68 dBc relative, 18 dB below the DUT's) and confirm with the attenuator test; then extrapolate at 3:1 slope ([nonlinearity](../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md)).

## Practical notes
- **Protect the input**: know the absolute maximum (tinySA Ultra +6 dBm at 0 dB attenuation, +20 dBm short-term peak with 30 dB attenuation, ±5 V DC [2]; SSA3000X Plus max average +30 dBm with att > 20 dB, damage +33 dBm [3]). Use a DC block if there is any bias on the line and always start with maximum attenuation and a pad.
- **Use the right mode on a tinySA**: basic tinySA: low input 0.1–350 MHz (50 Ω with ≥ 10 dB attenuation), high input 240–960 MHz (input not 50 Ω, no band filter — strong out-of-band signals distort in-band ones) [2]. tinySA Ultra: 100 kHz–800 MHz normal, up to 6 GHz in ultra mode (wide signals > 600 kHz can appear at wrong frequencies in ultra mode), optional 20 dB LNA (5 dB NF; attenuator disabled when on) [2]. The MCU radiates at 48 MHz harmonics — beware when using the telescopic antenna at low RBW [2].
- **Level accuracy**: tinySA ±2 dB after level calibration [2]; Siglent SSA3000X Plus ±0.7 dB (±0.4 dB typ) absolute at 50 MHz, frequency response ±0.8 dB [3]. For better than ±0.5 dB use a power meter ([RF power](rf-power-measurement.md)).
- **VBW and averaging**: VBW smooths the trace; with log scale and video filtering, the mean of noise is biased by −2.5 dB. Prefer RMS detector + trace averaging in power for noise and digitally modulated signals.
- **Bursts (LoRa packets)**: use zero span with a trigger, or max hold over several packets; the tinySA Ultra needs bursts ≥ 50 µs at 850 kHz RBW for correct level [2] (LoRa packets are ms long — fine).
- **Reference**: lock the SA to a 10 MHz GPSDO if you care about frequency (LoRa crystal offsets are measured in ppm; see [LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)).
- **Near-field sniffing**: an SA plus an H-field loop probe is the fastest way to find where a spur or harmonic comes from on a board ([oscilloscopes & probing](oscilloscopes-and-probing-for-rf.md)).
- **Recognising LTE, Wi-Fi and 5G NR on the screen:** see [10 OFDM § Level 3b](../10-comms-modulation/ofdm.md#level-3b--consumer-systems-5g-nr-numerology-what-lte-and-wi-fi-look-like-on-an-analyser-router-mimo-antennas-w5-s8).

## Common mistakes & misconceptions
- **"The noise floor is −95 dBm, so I can't see signals below −95 dBm."** Reduce RBW: each 10× gives 10 dB (at 10× the sweep time).
- **"The average trace shows the power of my LoRa signal."** It shows power per RBW. Use channel power or a wide-RBW zero-span measurement.
- **Reading noise with log averaging and not adding 2.5 dB** (or the ENBW correction). Noise markers do it for you — manual readings don't.
- **Connecting a transmitter directly** (even "just for a second"): a 1 W LoRa module exceeds the tinySA Ultra's absolute maximum by 24 dB.
- **Trusting a harmonic or IMD reading without the attenuator test** — the analyzer's own mixer is often the culprit.
- **Measuring phase noise with a tinySA and blaming the TCXO.** The SA's LO is 30–50 dB noisier.
- **Comparing two harmonics in different analyzer bands without the band-switch uncertainty**, or blaming the DUT for a noise-floor step at a band edge.
- **Treating the 0 Hz line as a fault** — it is the analyzer's own LO.
- **Measuring a milliohm PDN or loop gain below 100 kHz with ordinary coax on a VNA/SA** — the cable-shield ground loop adds milliohms.
- **Using the preamp with a strong signal present** — overload products appear everywhere.
- **Forgetting the pad's real loss and VSWR**; a mismatched pad and SA input cause ±0.2–0.5 dB mismatch uncertainty ([RF power](rf-power-measurement.md)).

## How to simulate / verify
- `python3 tools/verify/meas_sa.py` — (1) −1.05/−2.51 dB detector biases by Monte Carlo; (2) ENBW factors; (3) DANL slope 10 dB/decade by simulation; (4) NF from DANL specs; (5) sweep times; (6) near-noise correction; (7) LoRa chirp: peak vs RBW, channel-power integration, 99 % OBW; (8) attenuator chain for a 1 W module.
- `python3 tools/verify/s10_rx_tracing.py` §E–F — N9020B DANL → NF per band, 20 log N, and the shunt-thru ground-loop error model (ALL PASS).
- A quick bench check of your own SA: feed a known −30 dBm CW from a generator through a calibrated pad; change RBW (level must not change), then disconnect and terminate (floor must move 10 dB per decade of RBW).

## Open questions / gaps
- The detector used for the Siglent DANL spec ("sample detector, trace average > 50") is ambiguous about log vs power averaging; NF estimates are therefore given as a range.
- The tinySA "lowest discernible signal" is treated as DANL; the tinySA wiki does not state the averaging used.
- Real-time/FFT analyzers (Rigol RSA, Siglent SSA5000, SDR-based) have different sweep-time and detector behaviour; only noted here — see [SDR as test equipment](sdr-as-test-equipment.md).

## Sources
1. Keysight AN 150, *Spectrum Analysis Basics*, 5952-0292 (2016 ed.) — architecture, RBW/sweep time (ST = k·span/RBW², k 2–3), detectors, noise as a signal (Rayleigh, 1.05 dB, 2.5 dB, ENBW 1.05–1.13, total corrections), DANL/NF definitions, dynamic range and internal distortion, preselection; LO feedthrough at 0 Hz (ch. 2), harmonic-mixing conversion loss, DANL stair step and 20 log N phase noise (ch. 7), band-switching uncertainty (ch. 4 example). (app note; read; 2015 ed. via pdftotext)
2. tinySA wiki (Erik Kaashoek), "Specification" (tinySA and tinySA Ultra), "Limitations," tinysa.org, accessed 2026-09-27. (vendor docs; read)
3. Siglent, *SSA3000X Plus Spectrum Analyzer Data Sheet* DS0703P-E04B — DANL tables, phase noise, SHI/TOI/P1dB, level accuracy, max input. (datasheet; read)
4. LibreVNA Preliminary Specifications — SA mode −103 dBc/Hz at 1 GHz, 10 kHz. (vendor; read)
5. C. Rauscher, V. Janssen, R. Minihold, *Fundamentals of Spectrum Analysis*, Rohde & Schwarz, 2001 (and later editions) — detectors, noise corrections, dynamic range. (textbook/primer; cited)
6. Keysight AN 1303, "Spectrum and Signal Analyzer Measurements and Noise," 5966-4008E — noise measurement techniques, noise markers. (app note; cited)
7. This repository: `tools/verify/meas_sa.py`, `tools/verify/s10_rx_tracing.py`. (verification)
8. Keysight, *N9020B MXA X-Series Signal Analyzer, Multi-touch — Data Sheet* 5992-1255 — band/LO-multiple table (N = 1, 1, 2, 2, 4, 4, 8), DANL vs frequency incl. 10 Hz–1 MHz, frequency-reference accuracy terms. https://www.keysight.com/content/dam/keysight/en/doc/ungate/data-sheets/5992-1255.pdf (datasheet; read via pdftotext)
9. Keysight, *E5061B Network Analyzer — Technical Overview* 5990-4390 — test-cable ground-loop error in low-frequency shunt-through measurements, magnetic-core workaround, gain-phase port 5 Hz–30 MHz. (tech overview; search summary)
10. H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley, 2009, ch. 2 — cable-shield cut-off frequency (≈ 2 kHz for RG-58-class coax) and shield current division. (textbook; cited from memory, not re-read; chapter confirmed by W5-S18, 2026-10-13: ch. 2 is the cabling chapter, §2.3–2.5 inductive coupling and the shield's effect on it, per the Wiley ToC in gaps/D4-curriculum.md §3.5; the ≈ 2 kHz value is not re-checked)
