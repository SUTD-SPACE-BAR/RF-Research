---
title: Phase noise and jitter
domain: 07-noise-linearity
slug: phase-noise-and-jitter
tags: [phase-noise, jitter, leeson, dBc/Hz, reciprocal-mixing, ADC-aperture-jitter, EVM, PLL, oscillator, FMCW, range-correlation]
prerequisites: [thermal-noise-and-noise-temperature.md, shot-and-flicker-noise.md, ../00-math-foundations/probability-random-processes-and-psd.md, ../00-math-foundations/fourier-series-and-transform.md]
related: [dynamic-range-sfdr-blocking.md, receiver-cascade-analysis.md, ../06-rf-circuits/vco-and-pll-synthesizers.md, ../05-analog-electronics/oscillators.md, ../05-analog-electronics/data-converters-adc-dac.md, ../04-real-components-hf/crystals-and-resonators.md, ../11-radar/fmcw-radar.md, ../10-comms-modulation/ofdm.md, ../17-test-measurement/phase-noise-measurement.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Phase noise and jitter

## Questions this page answers
- What does "−120 dBc/Hz at 100 kHz offset" actually mean?
- How do I convert an oscillator's phase-noise plot into RMS jitter in femtoseconds?
- What limits the SNR of an ADC sampling a 70 MHz or 433 MHz signal — and why is clock jitter the culprit?
- What is Leeson's model, and why does oscillator phase noise fall at 30, then 20 dB/decade, then flatten?
- What is reciprocal mixing, and how does a strong nearby transmitter "deafen" my LoRa receiver through the LO?
- Why does multiplying a frequency by N raise phase noise by 20 log N?
- How does a PLL shape phase noise?
- How much does phase noise hurt OFDM EVM and FMCW radar?

## TL;DR
- $\mathcal{L}(f)$ (dBc/Hz) is the single-sideband phase-noise density at offset $f$ from the carrier, relative to the carrier: formally $\mathcal{L}(f) = \tfrac12 S_\varphi(f)$, where $S_\varphi$ is the one-sided PSD of phase fluctuations (rad²/Hz) (IEEE Std 1139 [5]).
- **Jitter from phase noise:** integrate $\mathcal{L}(f)$ over the band of interest to get $A$ (dBc); then $\sigma_\varphi = \sqrt{2\cdot10^{A/10}}$ rad and $\sigma_t = \sigma_\varphi/(2\pi f_0)$. Example: a 100 MHz XO profile integrated 12 kHz–20 MHz gives A = −91.8 dBc, 36.5 µrad, **58 fs**; from 100 Hz the same oscillator gives 170 fs — the lower limit matters (`tools/verify/noise_phase_jitter.py`).
- **ADC:** jitter-limited SNR = $-20\log_{10}(2\pi f_\text{in}\sigma_t)$: 100 fs gives 87 dB at 70 MHz but only 71 dB at 433 MHz (direct RF sampling needs very clean clocks) [2].
- **Leeson (1966):** $\mathcal{L}(f_m) = 10\log_{10}\!\left[\frac{FkT}{2P_s}\left(1+\left(\frac{f_0}{2Q_Lf_m}\right)^2\right)\left(1+\frac{f_c}{f_m}\right)\right]$ — slopes −30 dB/dec (below flicker corner $f_c$), −20 dB/dec (inside the resonator half-bandwidth $f_0/2Q_L$), flat floor beyond. Each ×10 in loaded Q buys 20 dB in the $1/f^2$ region.
- **Reciprocal mixing:** a blocker $P_b$ at offset $\Delta f$ adds in-channel noise $P_b + \mathcal{L}(\Delta f) + 10\log_{10}B$. A −40 dBm blocker 1 MHz away needs $\mathcal{L}$(1 MHz) ≲ −130 dBc/Hz to keep a 125 kHz LoRa channel within 2 dB of its thermal floor.
- **Frequency multiplication by N adds $20\log_{10}N$ dB**; a PLL output inside its loop bandwidth follows the reference ×N plus a normalised floor: $\mathcal{L}_\text{in-band} \approx \mathcal{L}_\text{norm} + 10\log f_\text{PFD} + 20\log N$ (−127 dBc/Hz for 433 MHz from a 32 MHz PFD at $\mathcal{L}_\text{norm}$ = −225 dBc/Hz).

## Intuition (no math)
A perfect oscillator is a single spectral line. A real one wobbles: its zero-crossings arrive a little early or late (jitter in time), which is the same thing as its phase wandering around the ideal (phase noise). In the frequency domain that wobble spreads the line into "skirts" either side of the carrier. Slow wander (low offset frequency) is large; fast wobble is small — so the skirts fall steeply with offset.

Why it matters depends on the job:
- **Receivers:** the LO multiplies every incoming signal. A strong unwanted signal a channel or two away, multiplied by the LO's skirt, lands smeared *inside* your IF channel — noise that no filter after the mixer can remove (reciprocal mixing).
- **Transmitters:** the same skirts leak power into neighbouring channels (adjacent-channel leakage) and blur constellations (EVM).
- **ADCs and DACs:** sampling a fast-changing signal at a slightly wrong instant produces a voltage error proportional to the signal's slope — high input frequencies turn clock jitter into noise.
- **Radar:** a huge clutter return carries the transmitter's phase noise with it; a faint target nearby in Doppler or range can drown in that skirt.

Leeson's picture of an oscillator: an amplifier with a resonator in a feedback loop. The amplifier adds white noise (the flat floor far from the carrier). The resonator only lets through frequencies close to $f_0$; inside its bandwidth, noise perturbations circulate and accumulate as random phase — the random walk of phase gives the $1/f^2$ region. Slow (1/f) fluctuations of the transistor modulate the phase too, giving $1/f^3$ closest in. A high-Q resonator (crystal, SAW, ceramic, dielectric resonator) narrows the region where noise accumulates: that is why crystal oscillators are orders of magnitude quieter than LC VCOs.

## The math

### Level 1 — definitions
- Real oscillator: $v(t) = A[1+\alpha(t)]\cos(2\pi f_0t + \varphi(t))$, with small amplitude noise $\alpha$ and phase noise $\varphi$ (rad).
- $S_\varphi(f)$ = one-sided PSD of $\varphi(t)$ (rad²/Hz). **$\mathcal{L}(f) = \tfrac12 S_\varphi(f)$**, expressed in dBc/Hz. (Older definition: SSB noise power in 1 Hz at offset $f$ divided by carrier power — equivalent for small phase deviations and negligible AM noise.)
- Integrated phase noise over $[f_1, f_2]$: $A = 10\log_{10}\int_{f_1}^{f_2}10^{\mathcal{L}(f)/10}df$ (dBc).
- RMS phase jitter: $\sigma_\varphi = \sqrt{2\int\mathcal{L}\,df}$ rad (the 2 converts SSB to both sidebands). RMS time jitter $\sigma_t = \sigma_\varphi/(2\pi f_0)$.
- Jitter-limited SNR of a sampled sinusoid at $f_\text{in}$: $\text{SNR}_j = -20\log_{10}(2\pi f_\text{in}\sigma_t)$ dB.
- Frequency multiplication by $N$: $\varphi \to N\varphi$, so $\mathcal{L} \to \mathcal{L} + 20\log_{10}N$. Division by $N$: $-20\log_{10}N$ (down to the divider's own floor).

### Level 2 — derivations
**(a) Why $\mathcal{L} = S_\varphi/2$.** For small $\varphi$, $\cos(\omega_0t + \varphi) \approx \cos\omega_0t - \varphi(t)\sin\omega_0t$. The phase noise appears as a quadrature term; its two-sided spectrum sits symmetrically around $\pm f_0$. The power at offset $+f$ in 1 Hz, relative to the carrier power $A^2/2$, is $(A^2/2)\cdot S_\varphi(f)/2 \big/ (A^2/2) = S_\varphi(f)/2$ — half of the phase PSD goes to each sideband.

**(b) Jitter integration.** $\sigma_\varphi^2 = \int_{f_1}^{f_2}S_\varphi\,df = 2\int\mathcal{L}\,df$. For a straight-line segment on a log–log plot (a power law $S \propto f^n$), the integral is analytic: $\int_a^b cf^n df = c(b^{n+1}-a^{n+1})/(n+1)$ (or $c\ln(b/a)$ for $n = -1$). The script integrates a piecewise profile this way, checks it against brute-force numerical integration and against a synthesised random phase process with the same PSD (36.46 µrad synthesised vs 36.48 µrad analytic). This is the method of ADI MT-008 [2].

**(c) Sampling with a jittery clock.** Sampling $V\sin(2\pi f_\text{in}t)$ at $t + \delta t$ gives an error $\approx 2\pi f_\text{in}V\cos(\cdot)\,\delta t$. Its mean-square is $(2\pi f_\text{in}V\sigma_t)^2/2$ while the signal power is $V^2/2$; the ratio gives $\text{SNR}_j = -20\log_{10}(2\pi f_\text{in}\sigma_t)$. Combined with quantisation, total SNR $= -10\log_{10}(10^{-\text{SNR}_q/10} + 10^{-\text{SNR}_j/10})$: a 14-bit ADC (86 dB ideal) at 70 MHz with a 150 fs clock delivers 81.6 dB; a 16-bit part is capped at 83.5 dB by the clock (script §2). Note the jitter that matters is the *total* aperture jitter — the ADC's own internal aperture jitter adds in RMS with the clock's.

**(d) Leeson's model [1].** Oscillator = amplifier (noise factor $F$, input signal power $P_s$) + resonator of loaded quality factor $Q_L$ in positive feedback. The amplifier's additive white noise $FkT$ produces, relative to $P_s$, a phase-noise floor $FkT/(2P_s)$ (half of the additive noise is in phase quadrature). The loop filter's phase slope $d\phi/df = 2Q_L/f_0$ converts phase perturbations inside the resonator half-bandwidth $f_0/(2Q_L)$ into frequency fluctuations; frequency noise that is white integrates into phase noise falling as $1/f_m^2$. Flicker noise of the device adds the $(1 + f_c/f_m)$ factor:
$$\mathcal{L}(f_m) = 10\log_{10}\!\left[\frac{FkT}{2P_s}\left(1 + \left(\frac{f_0}{2Q_Lf_m}\right)^2\right)\left(1+\frac{f_c}{f_m}\right)\right].$$
Worked with $f_0$ = 433 MHz, $Q_L$ = 20, $F$ = 10 dB, $P_s$ = 0 dBm, $f_c$ = 10 kHz: −103 dBc/Hz at 10 kHz, −126 at 100 kHz, −146 at 1 MHz, −163.6 ≈ −164 dBc/Hz at 10 MHz, and an asymptotic floor of **−167 dBc/Hz** ($FkT/2P_s$ = $-174+10-3$; −166.9 at 100 MHz). The corner $f_0/2Q_L$ is 10.8 MHz (script §3). The 10 MHz value is **not** the floor. Because 10 MHz lies just inside the 10.8 MHz corner, the $(f_0/2Q_Lf_m)^2$ term (1.17) still adds 3.4 dB there: $-167 + 10\log_{10}(2.17) = -163.6$. Read off a plot, the floor is only reached above ≈ 30 MHz (re-checked by W5-S17, `s17_leeson_check.py`). Raising $Q_L$ to 50 improves the 100 kHz figure to −134 dBc/Hz.

*Variants and limits.* Leeson's expression is semi-empirical: $F$ and $f_c$ are fitting parameters in practice, not the amplifier's small-signal NF and 1/f corner. Textbooks write the leading factor differently — Leeson's $FkT/(2P_s)$, while the tank-resistor derivation in Lee & Hajimiri's treatment gives $2FkT/P_s$ with $P_s$ the power dissipated in the tank — a 6 dB difference that comes from different definitions of $P_s$ and $F$, not a contradiction in physics (both variants are printed by the script). The Hajimiri–Lee impulse-sensitivity-function (ISF) theory [4] replaces the empirical factors with a time-varying model that also predicts how flicker noise up-converts (the $1/f^3$ corner can differ from the device $f_c$).

**(e) Reciprocal mixing.** A receiver LO with phase-noise skirt $\mathcal{L}(f)$ mixes an interferer at $f_\text{LO} + f_\text{IF} + \Delta f$ into the IF channel with the skirt value at offset $\Delta f$. The in-channel noise power is
$$N_\text{RM} = P_b + \mathcal{L}(\Delta f) + 10\log_{10}B\quad(\text{dBm}),$$
assuming $\mathcal{L}$ roughly constant across the channel bandwidth $B$. For a −40 dBm blocker: $\mathcal{L}$ = −110 dBc/Hz gives −99 dBm in 125 kHz (18 dB above a NF-6 dB thermal floor of −117 dBm); −130 dBc/Hz gives −119 dBm (2 dB below the floor). Working backwards from the SX1262 blocking figure (88 dB at 1 MHz offset, SF12/BW125, referred to sensitivity + 3 dB), *if* reciprocal mixing alone caused the 3 dB desensitisation, the LO would be about −122 dBc/Hz at 1 MHz — an inferred upper bound, not a Semtech specification (script §4).

### Level 3 — PLLs, systems and measurement subtleties
**PLL noise shaping (overview; full treatment in [06-rf-circuits/vco-and-pll-synthesizers](../06-rf-circuits/vco-and-pll-synthesizers.md)).** In a phase-locked loop with loop bandwidth $f_{BW}$:
- *inside* $f_{BW}$ the output tracks the reference: $\mathcal{L}_\text{out} \approx \mathcal{L}_\text{ref} + 20\log_{10}(f_\text{out}/f_\text{ref})$, plus the PFD/charge-pump/divider noise, conveniently summarised by a normalised floor $\mathcal{L}_\text{norm}$ (datasheet figure, typically −220 to −230 dBc/Hz for modern parts): $\mathcal{L}_\text{in-band} = \mathcal{L}_\text{norm} + 10\log_{10}f_\text{PFD} + 20\log_{10}N$. For 433.125 MHz from a 32 MHz PFD ($N$ = 13.5): −122/−127/−132 dBc/Hz for $\mathcal{L}_\text{norm}$ = −220/−225/−230; at 24 GHz from 100 MHz ($N$ = 240): −92 to −102 dBc/Hz (script §7).
- *outside* $f_{BW}$ the VCO's own noise is left (high-pass filtered by the loop), with a hump near $f_{BW}$ if the loop is under-damped.
- The optimum loop bandwidth for integrated jitter is near where the scaled reference/PFD noise and the free-running VCO noise cross. Fractional-N synthesis adds $\Sigma\Delta$ quantisation noise at larger offsets that the loop filter must suppress.

**Phase noise from tuning-line noise (FM noise).** A VCO with tuning gain $K_v$ (Hz/V) turns a noise voltage density $v_n(f_m)$ (V/√Hz) on its tuning (or supply, via pushing) line into frequency noise $S_{\Delta f}(f_m) = K_v^2v_n^2$ (Hz²/Hz). Phase is the integral of frequency, so $S_\varphi(f_m) = S_{\Delta f}/f_m^2$ and, for small modulation, $\mathcal{L}(f_m) \approx \tfrac12 S_\varphi = \dfrac{(K_vv_n)^2}{2f_m^2}$ — a −20 dB/decade slope. Example: $K_v$ = 50 MHz/V and a 10 nV/√Hz tuning-line source (a typical op-amp or LDO output) give $K_vv_n$ = 0.5 Hz/√Hz → $\mathcal{L}$ = −69 / −89 / −109 dBc/Hz at 1 / 10 / 100 kHz — far worse than a good LC VCO's intrinsic −120 dBc/Hz at 100 kHz. Inside a PLL's bandwidth the loop suppresses it (VCO-noise transfer $1/(1+G)$, [VCO & PLL](../06-rf-circuits/vco-and-pll-synthesizers.md)); outside it, the loop-filter resistors' thermal noise and any op-amp in an active filter add directly by this formula. Hence: low $K_v$ (band-switched VCOs), passive loop filters with small resistors, and an RC filter plus a quiet supply on the tuning node. (Added by W5-E1 from W2-B1's cross-domain note; standard narrowband-FM result.)

**Consequences for Marcus's radios.** LoRa demodulation (dechirp + FFT) is robust to moderate phase noise because symbol decisions depend on the FFT bin of a long chirp; its practical frequency concerns are static offset and drift (see [09-propagation-link-budget/multipath-fading-doppler](../09-propagation-link-budget/multipath-fading-doppler.md)). Phase noise matters for LoRa mostly through **reciprocal mixing and blocking** when a strong transmitter (another team's 433 MHz telemetry, your own 900 MHz link on the same mast, a range radar) is nearby. GNSS receivers care about the TCXO's close-in phase noise and short-term stability (Allan deviation over the coherent integration time) because carrier tracking loops integrate for milliseconds to seconds; vibration-induced phase noise (g-sensitivity of the crystal, ~1 ppb/g typical order) matters on a rocket — see Practical notes.

**OFDM / high-order QAM EVM.** For small random phase error of RMS $\sigma_\varphi$ (after any common-phase-error correction), a constellation point suffers EVM ≈ $\sigma_\varphi$ (rad): 1° RMS → 1.75 % (−35.2 dB), 2° → 3.5 % (−29.1 dB), 5° → 8.7 % (script §6). 256-QAM typically needs EVM better than about −30 dB, which limits the integrated phase noise of Wi-Fi/5G synthesisers to under ~1° RMS. In OFDM, phase noise at offsets much smaller than the subcarrier spacing appears as a common rotation (correctable by pilots); noise at offsets comparable to or above the spacing causes inter-carrier interference (not correctable). See [10-comms-modulation/ofdm](../10-comms-modulation/ofdm.md).

**Radar: the range-correlation effect.** In an FMCW or CW radar the same oscillator transmits and serves as the receive LO. The returned signal is a copy delayed by $\tau = 2R/c$, so the phase noise partly cancels: the residual phase-noise PSD is multiplied by $4\sin^2(\pi f\tau)$ ≈ $(2\pi f\tau)^2$ for small $f\tau$. For a target at 1 m, the suppression at 100 kHz offset is −48 dB; at 100 m the factor at 1 MHz is +4.8 dB (no suppression) (script §6). Close-in clutter (bumper, radome) is therefore much less damaging than distant clutter, and radar synthesisers are specified at offsets corresponding to the beat frequencies of interest. See [11-radar/fmcw-radar](../11-radar/fmcw-radar.md).

**Measurement subtleties.** A spectrum analyzer reading of "sideband power in 1 Hz" includes AM noise and the analyzer's own LO phase noise; at small offsets use a dedicated phase-noise analyzer (PLL/cross-correlation method) — see [17-test-measurement/phase-noise-measurement](../17-test-measurement/phase-noise-measurement.md). $\mathcal{L}(f)$ is only meaningful where the integrated phase deviation beyond $f$ is ≪ 1 rad; very close to the carrier (inside the linewidth) the small-angle definition breaks down.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $\mathcal{L}(f) = S_\varphi(f)/2$ | small phase deviation | dBc/Hz |
| $\sigma_t = \sqrt{2\int\mathcal{L}\,df}/(2\pi f_0)$ | absolute (TIE) jitter in a stated band | 100 MHz XO, 12 kHz–20 MHz: 58 fs |
| $\text{SNR}_j = -20\log(2\pi f_\text{in}\sigma_t)$ | sampled sinusoid, Gaussian jitter | 100 fs: 87 dB @70 MHz, 71 dB @433 MHz |
| $+20\log_{10}N$ | ×N multiplier/PLL in-band | ×4 → +12 dB; ×100 → +40 dB |
| Leeson | single-resonator feedback oscillators | LC VCO 433 MHz ~−120..−130 dBc/Hz @100 kHz |
| $N_\text{RM} = P_b + \mathcal{L}(\Delta f) + 10\log B$ | blocker much stronger than wanted | −40 dBm, −130 dBc/Hz, 125 kHz → −119 dBm |
| $\mathcal{L}_\text{in-band} = \mathcal{L}_\text{norm} + 10\log f_\text{PFD} + 20\log N$ | inside PLL bandwidth | 433 MHz/32 MHz: ≈ −127 dBc/Hz |
| EVM ≈ $\sigma_\varphi$ | small uncorrected phase error | 1° → 1.75 % (−35 dB) |
| FMCW residual $\times4\sin^2(\pi f\tau)$ | shared Tx/LO oscillator | 1 m, 100 kHz: −48 dB |

## Worked examples
**1 — Is this clock good enough for direct RF sampling of 433 MHz?** Target: 12-bit-class SNR ≥ 70 dB at $f_\text{in}$ = 433 MHz. Need $\sigma_t \le 10^{-70/20}/(2\pi\cdot433\times10^6) = 116$ fs total. The 100 MHz XO above integrates to 58 fs (12 kHz–20 MHz) — but if the application integrates from 100 Hz (e.g. long FFTs), 170 fs gives only 66.7 dB. Choose integration limits that match how the data are used: the lower limit ≈ 1/(observation time); the upper ≈ the ADC's sampling bandwidth or clock-filter bandwidth.

**2 — Reciprocal mixing at a shared ground station.** The 900 MHz and 433 MHz links are far apart, but suppose another team transmits 1 W at 434.0 MHz, 5 km away, while you receive at 433.125 MHz (offset ≈ 0.9 MHz). Free-space path loss at 5 km ≈ 99 dB; with 11 dBi of Yagi gain toward it (worst case), $P_b$ ≈ 30 − 99 + 11 = −58 dBm. If your LO has −122 dBc/Hz at 0.9 MHz, reciprocal-mixing noise in 125 kHz is −58 − 122 + 51 = −129 dBm — 12 dB *below* a −117 dBm floor: no harm. Pointing the Yagi away and a SAW bandpass filter help further. At 1 km with the same beam alignment, $P_b$ ≈ −44 dBm → −115 dBm reciprocal-mixing noise: 2 dB above the floor, i.e. ~4 dB desense.

**3 — Why a ×N multiplier chain degrades a mmWave radar LO.** A 100 MHz OCXO at −160 dBc/Hz (10 kHz offset) multiplied to 24 GHz (N = 240) becomes −160 + 47.6 = −112.4 dBc/Hz — about the same as a good integrated 24 GHz PLL's in-band floor (script §7 shows −92 to −102 dBc/Hz for $\mathcal{L}_\text{norm}$ −220 to −230 dBc/Hz at 100 MHz PFD), which is why low-phase-noise mmWave sources use high PFD frequencies or multiply from quiet references.

**4 — Leeson sanity check of a VCO datasheet.** A 433 MHz LC VCO claims −120 dBc/Hz at 100 kHz. With $F$ = 10 dB and $P_s$ = 0 dBm, Leeson needs $Q_L \approx 10$ (script §3: $Q_L$ = 10 → −119.9 dBc/Hz) — consistent with on-chip LC tanks. A claim of −140 dBc/Hz at 100 kHz would need $Q_L$ ≈ 100 or much higher signal power: plausible only for ceramic/SAW-stabilised oscillators.

## Practical notes
- **Vibration and acceleration** modulate a crystal's frequency (g-sensitivity, commonly of order 10⁻⁹/g for ordinary quartz, lower for "low-g" SC-cut parts). On a rocket, random vibration of several g RMS during boost produces vibration-induced phase-noise sidebands at the vibration frequencies (tens of Hz to kHz). For LoRa this is mostly irrelevant; for GNSS carrier tracking it can cause loss of lock. (Figure given as an order of magnitude; see Open questions.)
- **TX heating drifts the crystal.** Semtech warns that SX126x self-heating in high-power transmission can pull an XTAL and recommends a TCXO when LDRO is unusable [3]. On the E22-400T33D with a 2 W PA the thermal gradient near the reference is significant.
- **Power-supply noise** couples into VCO tuning and PA supply lines; ripple at switching frequencies (hundreds of kHz to MHz) shows up as discrete spurs at that offset — keep buck converters away from VCO/PLL supplies or post-regulate with an LDO.
- **Spurs vs noise:** discrete spurs (fractional-N, reference leakage, switching supplies) integrate as $10\log_{10}$(spur power) each, not per Hz; include them separately when computing jitter.
- **Why oscillators have the noise they have** (ISF/LTV theory, 1/f³ corner, vibration-induced phase noise): see [06 oscillator phase noise (ISF)](../06-rf-circuits/oscillator-phase-noise-ltv-isf.md#level-2--derivations).

## Common mistakes & misconceptions
- **Forgetting the factor 2** when converting integrated SSB phase noise to RMS phase ($\sigma_\varphi = \sqrt{2\cdot10^{A/10}}$), or double-counting it.
- **Quoting jitter without the integration band.** "58 fs" and "170 fs" can be the same oscillator (12 kHz vs 100 Hz lower limit).
- **Adding dBc/Hz numbers of different oscillators.** Convert to linear and add powers; after a mixer, the LO and RF phase noises add (uncorrelated).
- **"Dividing a frequency always improves phase noise by 20 log N."** Only down to the divider's own noise floor.
- **Using a spectrum analyzer's noise-like skirt near the carrier as phase noise** without checking that the analyzer's own LO is better — the reading may be the analyzer.
- **Believing LoRa needs an ultra-low-phase-noise LO.** Its demodulator tolerates ordinary PLL phase noise; frequency *offset and drift* over the packet are the real constraints.
- **Ignoring reciprocal mixing when computing blocking.** A receiver with excellent linearity can still be desensitised by LO phase noise.

## How to simulate / verify
- `tools/verify/noise_phase_jitter.py` — exact piecewise integration of $\mathcal{L}(f)$, brute-force and time-domain synthesis checks, ADC SNR, Leeson (both variants), reciprocal mixing and the SX1262 inference, multiplication, EVM, FMCW range correlation, PLL in-band floor.
- Phase-noise-to-jitter web calculators exist, but they differ in whether they include the factor 2 and spurs; cross-check with the script.
- Harmonic-balance / PSS-pnoise simulation for oscillator phase noise; PLL loop simulators (e.g. ADIsimPLL, PLL designer tools, or a Python linear model) for noise shaping ([16-simulation-tools](../16-simulation-tools/rf-circuit-simulators-harmonic-balance.md)).
- Measure with an SDR: record a clean tone from a signal generator through your receiver chain, compute the phase of the downconverted tone, and estimate $S_\varphi$ by FFT — this measures the *combined* phase noise of the source and the SDR's LO.

## Open questions / gaps
- The original MT-008 PDF (ADI) could not be retrieved during this session (server timeouts); the integration method and SNR formula are standard and were re-derived and numerically verified here, but the page's reference to specific MT-008 examples is by citation, not direct reading.
- Quartz g-sensitivity numbers for the TCXOs used in EBYTE modules and u-blox receivers are not available; the flight vibration spectrum × g-sensitivity budget is a gap (cross-domain: 04 crystals, 15, 20).
- LO phase noise of SX126x/LLCC68 is not specified by Semtech; the −122 dBc/Hz at 1 MHz here is an inference from the blocking spec.

## Sources
1. D. B. Leeson, "A simple model of feedback oscillator noise spectrum," *Proc. IEEE* 54(2), 329–330 (1966), doi:10.1109/PROC.1966.4682. (peer-reviewed) — Leeson's model.
2. W. Kester, "Converting Oscillator Phase Noise to Time Jitter," Analog Devices Tutorial MT-008 (2008/2009), https://www.analog.com/media/en/training-seminars/tutorials/MT-008.pdf; and W. Kester (ed.), *Data Conversion Handbook*, Newnes 2005, ch. 2 (aperture jitter and SNR). (app note / textbook) — integration method, SNR vs jitter. *Cited, not re-read this session (fetch timed out).*
3. Semtech, *SX1261/2 Data Sheet*, Rev 1.2 (2019) Table 3-8 (blocking 88/90/99 dB at 1/2/10 MHz, SF12/BW125) and Rev 2.2 (2024) §4.1.2 (frequency drift, TCXO recommendation). (datasheet)
4. A. Hajimiri and T. H. Lee, "A general theory of phase noise in electrical oscillators," *IEEE J. Solid-State Circuits* 33(2), 179–194 (1998). (peer-reviewed) — ISF model, flicker up-conversion.
5. IEEE Std 1139-2008, *IEEE Standard Definitions of Physical Quantities for Fundamental Frequency and Time Metrology — Random Instabilities*. (standard) — $\mathcal{L}(f) = S_\varphi(f)/2$ definition.
6. B. Razavi, *RF Microelectronics*, 2nd ed., 2011, §8.7 (phase noise, reciprocal mixing) and ch. 9–10 (PLLs). (textbook)
7. T. H. Lee, *The Design of CMOS Radio-Frequency Integrated Circuits*, 2nd ed., 2004, ch. 18 (phase noise). (textbook)
8. `tools/verify/noise_phase_jitter.py` (this KB).
