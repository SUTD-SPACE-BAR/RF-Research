---
title: Decibels and logarithmic units
domain: 00-math-foundations
slug: decibels-and-log-units
tags: [decibel, dBm, dBi, dBc, dBFS, neper, link-budget, units, logarithm]
prerequisites: []
related:
  - complex-numbers-and-phasors.md
  - probability-random-processes-and-psd.md
  - ../07-noise-linearity/thermal-noise-and-noise-temperature.md
  - ../07-noise-linearity/phase-noise-and-jitter.md
  - ../09-propagation-link-budget/link-budget-methodology.md
  - ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md
  - ../08-antennas/antenna-fundamentals.md
  - ../11-radar/radar-cross-section.md
  - ../05-analog-electronics/data-converters-adc-dac.md
level: mixed
confidence: high
last_updated: 2026-10-03
---

# Decibels and logarithmic units

## Questions this page answers
- Why do we use 10 log for power but 20 log for voltage?
- What exactly is a dBm, and how many volts is 0 dBm (or 33 dBm) into 50 Ω?
- Is 30 dBm + 30 dBm = 60 dBm? How do I add two signals given in dBm?
- When do two signals add to +3 dB and when to +6 dB?
- What is the difference between dB, dBm, dBW, dBi, dBd, dBic, dBc, dBc/Hz, dBFS, dB-Hz, dBsm and dBK?
- How do I convert dBµV/m field strength into received power in dBm?
- Why is thermal noise −174 dBm/Hz, and why does the spectrum-analyser noise floor move when I change RBW but my carrier does not?
- Why does 1 % sometimes mean −40 dB and sometimes 0.04 dB?
- What is a neper and why does it appear in transmission-line attenuation?
- How can I do dB arithmetic in my head?

## TL;DR
- A decibel is always ten times the base-10 log of a **power ratio**: $10\log_{10}(P_1/P_2)$. For amplitudes (V, I, E, H, $|\Gamma|$, $|S_{21}|$) the same number is $20\log_{10}(V_1/V_2)$ **only when both are across the same impedance**, because $P\propto V^2$.
- Suffixes fix the reference: dBm (1 mW), dBW (1 W, = dBm − 30), dBµV (1 µV; 0 dBm into 50 Ω = 107 dBµV), dBi (isotropic), dBd (half-wave dipole; dBd = dBi − 2.15), dBc (relative to carrier), dBFS (converter full scale), dB-Hz (ratio of something to 1 Hz, e.g. C/N₀), dBsm (1 m²), dBK (1 K).
- dB + dB = dB (cascade gains); dBm + dB = dBm (level after a gain); dBm − dBm = dB (ratio). **dBm + dBm is meaningless** — convert to mW, add, convert back: 30 dBm ⊕ 30 dBm = 33 dBm (uncorrelated).
- Uncorrelated signals add in power (+3 dB for two equal). Coherent in-phase signals add in voltage (+6 dB for two equal); in anti-phase they cancel. On average over random phase coherent sums revert to power addition.
- 50 Ω landmarks: 0 dBm = 224 mV rms = 632 mV p-p; +13 dBm ≈ 1 V rms; +30 dBm = 7.07 V rms; +33 dBm (the 2 W E22 module) ≈ 10 V rms, 28 V p-p.
- Thermal noise $kT_0$ at 290 K = −173.98 dBm/Hz; in 125 kHz (a LoRa channel) it is −123 dBm. Noise scales with $10\log_{10}B$; a CW tone does not.
- Mental math: 3 dB ≈ ×2, 10 dB = ×10, 1 dB ≈ +26 % power, 0.1 dB ≈ +2.3 % power, 6 dB ≈ ×4 power = ×2 voltage, 7 dB ≈ ×5.
- 1 Np = 8.686 dB. Nepers come from natural logs and appear naturally in $e^{-\alpha z}$ line attenuation.

## Intuition (no math)
RF signals span absurd ranges. A 2 W rocket transmitter and a −137 dBm signal at the edge of LoRa reception differ by a factor of $10^{17}$. Writing numbers like that is error-prone, and in a radio chain you mostly *multiply*: an amplifier multiplies power by its gain, a cable multiplies it by a fraction, free space multiplies it by a tiny number. Logarithms turn multiplication into addition, so a whole link budget becomes a column of numbers you add and subtract.

A decibel is a *ratio* on a log scale. By itself it has no absolute size: "20 dB" just means "100 times more power". The moment you attach a reference — dB**m** means "relative to 1 milliwatt" — it becomes an absolute *level*, like a height above sea level. That is why you can add a dB gain to a dBm level (raise the level) but cannot add two levels (adding two heights above sea level does not give a height).

Why the "10 vs 20"? The decibel was defined for power. Voltage is like the side of a square whose area is power: double the side, quadruple the area. So a voltage ratio of 2 is a power ratio of 4, which is 6 dB, and 6 = 20 log 2. The "20" is just "10 × 2" from the square. It is the *same decibel*, not a second kind — which is why it only works if both voltages are across the same resistance.

Adding signals: if two signals are unrelated (two different transmitters, noise from two resistors), their instantaneous voltages sometimes help and sometimes fight, and on average their *powers* add. If they are copies of the same waveform in step (two array elements pointed the same way), the *voltages* add: double voltage, four times power, +6 dB. If they are out of step they can cancel completely. This is the whole basis of beamforming, multipath fading and noise averaging.

## The math

### Level 1 — definitions and algebra

**Power ratio in decibels.** For powers $P_1$ and $P_2$ (W):
$$G_{\rm dB} = 10\log_{10}\frac{P_1}{P_2}\qquad\Longleftrightarrow\qquad \frac{P_1}{P_2}=10^{G_{\rm dB}/10}$$
The bel is $\log_{10}(P_1/P_2)$; the decibel is one tenth of a bel, hence the factor 10 [1 §2.1].

**Power level relative to a reference.** Fix $P_2=P_{\rm ref}$:
$$L = 10\log_{10}\frac{P}{P_{\rm ref}}\;[\text{dB re }P_{\rm ref}]$$
With $P_{\rm ref}=1$ mW this is dBm; with 1 W it is dBW. Therefore $L_{\rm dBW}=L_{\rm dBm}-30$.

**Amplitude ("root-power" or "field") quantities.** Voltage $V$, current $I$, electric field $E$, magnetic field $H$, reflection coefficient $|\Gamma|$ and S-parameter magnitudes $|S_{ij}|$ are amplitudes whose *square* is proportional to power. Their levels are
$$L_V = 20\log_{10}\frac{V}{V_{\rm ref}}\qquad (V = V_{\rm ref}\,10^{L_V/20})$$
Power-like quantities (use 10 log): power, energy, power spectral density, power flux density (W/m²), noise factor, noise temperature, radar cross-section (m²), antenna gain/directivity, bandwidth ratios. Amplitude quantities (use 20 log): V, I, E, H, $|\Gamma|$, $|S|$, EVM (an error *vector*), ADC codes [1 §2.4, §5.6, §5.12].

**Arithmetic rules.**

| Operation | Result | Example |
|---|---|---|
| dB + dB | dB | cascade: −0.7 + 12 − 7 + 23 = 27.3 dB gain |
| dBm + dB | dBm | 33 dBm into a 20 dB attenuator → 13 dBm |
| dBm − dBm | dB | −60 dBm signal over −100 dBm noise → 40 dB SNR |
| dBm + dBm | *meaningless* (units of mW²) | convert to mW first |
| dBm/Hz + 10 log₁₀(B/1 Hz) | dBm | −174 dBm/Hz + 51 dB (125 kHz) = −123 dBm |

**Neper.** Using natural logarithms, the level of a field quantity is $L_F=\ln(F/F_0)$ Np and the level of a power quantity is $L_P=\tfrac12\ln(P/P_0)$ Np, so both give the same number for the same physical change [2 §8.7]. Hence
$$1\ \text{Np} = \frac{20}{\ln 10}\ \text{dB} = 8.686\ \text{dB},\qquad 1\ \text{dB}=0.1151\ \text{Np}.$$

**Voltage at 50 Ω from dBm.** $P = V_{\rm rms}^2/R$, so
$$V_{\rm rms}=\sqrt{R\cdot 10^{-3}\cdot 10^{L_{\rm dBm}/10}},\qquad V_{\rm pk}=\sqrt2\,V_{\rm rms},\qquad V_{\rm pp}=2\sqrt2\,V_{\rm rms}$$
(the peak relations hold for a sine only). For $R=50$ Ω, 0 dBm = 0.2236 V rms. In dBµV: $L_{\rm dB\mu V} = L_{\rm dBm} + 10\log_{10}(R\cdot10^{-3}/10^{-12}) = L_{\rm dBm}+106.99$ at 50 Ω (and +108.75 at 75 Ω).

### Level 2 — why 20 log, impedance changes, adding signals, statistics

**Deriving 20 log.** Take $P_1 = V_1^2/R_1$ and $P_2=V_2^2/R_2$. Then
$$10\log_{10}\frac{P_1}{P_2} = 20\log_{10}\frac{V_1}{V_2} - 10\log_{10}\frac{R_1}{R_2}.$$
The familiar $20\log(V_1/V_2)$ is exact only if $R_1=R_2$ [1 §2.3]. Example: an ideal lossless 75 Ω → 50 Ω transformer has output voltage $\sqrt{50/75}=0.816$ × input, a *voltage* ratio of −1.76 dB; but because the output impedance is lower, the *power* ratio is $-1.76 - 10\log_{10}(50/75) = -1.76+1.76 = 0$ dB — no loss, as it must be. (A resistive minimum-loss 75→50 Ω pad, by contrast, really does dissipate 5.7 dB.) Voltage gains of op-amp stages with high-Z inputs are routinely quoted in "dB" using 20 log with unequal impedances: that is a voltage-gain convention, not a power gain.

**Complex ratios.** For a complex transfer function $H(j\omega)=|H|e^{j\phi}$,
$$\ln H = \ln|H| + j\phi$$
The real part is the gain in nepers and the imaginary part is the phase in radians. So "attenuation constant α in Np/m" and "phase constant β in rad/m" in $\gamma=\alpha+j\beta$ of a transmission line are literally the real and imaginary parts of one complex logarithm per metre. To convert line loss: α [dB/m] = 8.686 × α [Np/m]. See [complex numbers](complex-numbers-and-phasors.md) and [telegrapher equations](../03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md).

**Adding two signals — general case.** Let $v(t)=A_1\cos(\omega t)+A_2\cos(\omega t+\varphi)$ across $R$. With phasors (see [phasors](complex-numbers-and-phasors.md)) the total amplitude is $|A_1+A_2e^{j\varphi}|$, so the average power is
$$P = \frac{A_1^2 + A_2^2 + 2A_1A_2\cos\varphi}{2R}=P_1+P_2+2\sqrt{P_1P_2}\cos\varphi.$$
- $\varphi=0$ (coherent, in phase): $P=(\sqrt{P_1}+\sqrt{P_2})^2$; equal signals give 4× → **+6.02 dB**.
- $\varphi=90°$: $P=P_1+P_2$ → +3.01 dB for equal signals.
- $\varphi=120°$ (equal amplitudes): 0 dB change. $\varphi=180°$: $P=(\sqrt{P_1}-\sqrt{P_2})^2$, zero for equal amplitudes.
- $\varphi$ random and uniformly distributed: the cross term averages to zero, $\overline{P}=P_1+P_2$ → **+3.01 dB**. This is "uncorrelated" or "incoherent" addition; it is what happens for noise, for signals at different frequencies, and for independent transmitters [1 §4.1, §4.3].

For $N$ equal signals: coherent → $N^2 P_1$ ($+20\log_{10}N$ dB); incoherent → $N P_1$ ($+10\log_{10}N$ dB). A coherent combiner of $N$ antennas with independent noise therefore improves SNR by $10\log_{10}N$ — the array gain (see [phased arrays](../12-phased-arrays/array-factor-linear-arrays.md)).

**Power-sum correction rule.** For two uncorrelated levels $L_1\ge L_2$ with difference $\Delta=L_1-L_2$:
$$L_{\rm sum}=L_1+10\log_{10}\left(1+10^{-\Delta/10}\right).$$

| Δ (dB) | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 10 | 13 | 15 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| add to larger, uncorrelated (dB) | 3.01 | 2.54 | 2.12 | 1.76 | 1.46 | 1.19 | 0.97 | 0.79 | 0.64 | 0.41 | 0.21 | 0.14 | 0.04 |
| add to larger, coherent in-phase (dB) | 6.02 | 5.53 | 5.08 | 4.65 | 4.25 | 3.88 | 3.53 | 3.21 | 2.91 | 2.39 | 1.75 | 1.42 | 0.83 |
| worst-case anti-phase (dB) | −∞ | −19.3 | −13.7 | −10.7 | −8.7 | −7.2 | −6.0 | −5.1 | −4.4 | −3.3 | −2.2 | −1.7 | −0.9 |

(Computed; agrees with R&S Table 6-2 [1 §6.2]; verified by `tools/verify/math_decibels.py`.) The anti-phase row is the depth of a two-path multipath fade, and also the "mismatch uncertainty" range when two reflections of unknown phase combine.

**Subtracting a known noise floor.** If an instrument shows noise $L_n$ with the signal off and $L_t$ with it on, the signal alone is $10\log_{10}(10^{L_t/10}-10^{L_n/10})$. Example [1 §4.2]: −65 dBm total, −70 dBm noise → −66.65 dBm; reading the display directly errs by 1.65 dB. Requires an RMS (power) detector.

**Averaging in dB is biased.** If you average log values (e.g. a spectrum analyser with log display and video averaging) instead of averaging power, you under-read noise. For complex Gaussian noise the power is exponentially distributed, and
$$\mathbb E[10\log_{10}X]-10\log_{10}\mathbb E[X]=-\frac{10\,\gamma_{\rm E}}{\ln10}=-2.51\ \text{dB}$$
where $\gamma_E=0.5772$ is Euler's constant. Monte-Carlo check in the verify script gives −2.51 dB. That is why analysers offer an RMS detector and why noise markers add ≈2.5 dB correction when using log averaging [1 §5.3], [7]. See [probability](probability-random-processes-and-psd.md).

**Percent vs dB.** "x % of" and "x % more/less" are different questions [1 §3]:
- 1 % of a voltage: $20\log 0.01 = -40$ dB. 1 % of a power: −20 dB.
- 1 % *more* voltage: $20\log 1.01 = +0.086$ dB. 1 % more power: $10\log1.01=+0.043$ dB.
- Asymmetry: +20 % voltage = +1.58 dB but −20 % = −1.94 dB. For small $x$, $10\log_{10}(1+x)\approx4.34\,x$ dB (because $10/\ln10 = 4.343$), so 1 % power ≈ 0.043 dB and 1 % voltage ≈ 0.087 dB.

### Level 3 — the whole zoo of log units, and where the rules bend

**Standards view.** ISO 80000-3 / IEC 60027-3 and NIST SP 811 §8.7 treat the neper and bel as units of *level* and require the reference to be stated, e.g. $L_P$ (re 1 mW) = 10 dB. Strictly, the SI rules forbid attaching the reference to the unit symbol, so "dBm" is non-SI shorthand [2 §8.7]. ITU and all of industry use dBm, dBW, dBµV etc.; the KB uses them too, but always make the reference explicit when it is unusual.

**Absolute power and voltage levels**

| Unit | Reference | Quantity type | Notes |
|---|---|---|---|
| dBW | 1 W | power | dBW = dBm − 30 |
| dBm | 1 mW | power | the RF default; *assumes nothing about impedance* |
| dBµV | 1 µV | amplitude | impedance must be known to convert to dBm: +107 dB at 50 Ω |
| dBmV | 1 mV | amplitude | cable TV (75 Ω): 0 dBmV = −48.75 dBm |
| dBV | 1 V | amplitude | audio/instrumentation |
| dBu | 0.7746 V | amplitude | = voltage of 1 mW into 600 Ω; used in audio regardless of actual impedance |
| dBFS | converter full scale | amplitude (usually) | 0 dBFS = full-scale sine (convention varies: some define full-scale *square* = 0 dBFS, making a full-scale sine −3 dBFS) |
| dBr | arbitrary stated reference | either | "relative"; always say to what |

**Relative (ratio) units**

| Unit | Meaning | Where used |
|---|---|---|
| dB | pure ratio | gain, loss, SNR, return loss |
| dBc | relative to the carrier power | harmonics, spurs, intermod, ACPR |
| dBc/Hz | power in 1 Hz at an offset, relative to the carrier | single-sideband phase noise $\mathcal L(f)$ [1 §5.5] |
| dBi | antenna gain relative to an isotropic radiator (same polarisation) | antennas, EIRP |
| dBd | gain relative to a lossless half-wave dipole | ERP; dBd = dBi − 2.15 (dipole directivity 1.641 = 2.15 dBi, verified numerically) |
| dBic | gain relative to an isotropic *circularly* polarised radiator | GNSS patches, helices |
| dBil | relative to isotropic linear (= ordinary dBi) | used to disambiguate from dBic |

**Density and "per Hertz" units — two different ideas.**
1. *Spectral density*: dBm/Hz, dBW/Hz, dBFS/Hz, dBc/Hz. The quantity is power per unit bandwidth. To get power in bandwidth $B$: $L = L_{/\rm Hz}+10\log_{10}(B/1\,\text{Hz})$ — valid for noise-like (flat) spectra only.
2. *dB-Hz* (e.g. C/N₀): the quantity itself has units of Hz, because it is a power divided by a power density: $C/N_0 = C/(N/B)$ has units W/(W/Hz) = Hz. So $C/N_0 = 45$ dB-Hz means $3.2\times10^4$ Hz. SNR in bandwidth $B$ is then $C/N_0 - 10\log_{10}B$ [3]. GPS L1 C/A receivers typically report 40–50 dB-Hz under open sky (≥ 45 dB-Hz for a healthy install, 35–40 marginal or obstructed, < 35 a fault); with a 4 MHz front end that is an SNR of about −26 to −16 dB before despreading (−31 dB at 35 dB-Hz) [3].

**Other engineering log units**

| Unit | Reference | Type | Example |
|---|---|---|---|
| dBsm (dBm²) | 1 m² | power-like (area) | radar cross-section; a 1 cm² target is −40 dBsm |
| dBK | 1 K | power-like (noise temperature ∝ power) | 290 K = 24.6 dBK; satellite G/T in dB/K = antenna gain (dBi) − system temperature (dBK) |
| dB(W/m²), dB(mW/m²) | power flux density | power | 1 W/m² ↔ 145.8 dBµV/m in free space |
| dBµV/m | 1 µV/m field | amplitude | EMC limits; dB(V/m) + 120 = dBµV/m |
| dBµA/m | 1 µA/m | amplitude | magnetic field in H-field EMC tests |
| dB SPL, dB(A) | 20 µPa | amplitude (pressure) | acoustics; not RF — mentioned because people mix it in |

**Field strength ↔ received power.** In the far field of a plane wave, power density $S = E^2/\eta_0$ with $\eta_0 = \sqrt{\mu_0/\varepsilon_0}=376.73$ Ω. An antenna of gain $G$ (linear, matched, polarisation-matched) has effective aperture $A_e = G\lambda^2/(4\pi)$ and delivers $P_r = S A_e$. Combining and converting ($f$ in MHz, $\lambda = c/f$):
$$P_r[\text{dBm}] = E[\text{dB}\mu\text{V/m}] + G[\text{dBi}] - 20\log_{10}f_{\rm MHz} - 77.2$$
The **antenna factor** (EMC), the ratio of incident field to voltage at a 50 Ω port, is $AF = E/V = \sqrt{4\pi\eta_0/(50\,G)}/\lambda = 9.73/(\lambda\sqrt G)$ m⁻¹, i.e.
$$AF[\text{dB/m}] = 20\log_{10}f_{\rm MHz} - G[\text{dBi}] - 29.77$$
(29.78–29.79 appears in references that use $c = 3\times10^8$ m/s or $\eta_0=120\pi$; the difference is rounding) [4], verified by the script. The antenna page owns the aperture derivation: [antenna fundamentals](../08-antennas/antenna-fundamentals.md).

**Thermal noise.** Available noise power from a resistor at temperature $T$ in bandwidth $B$ is $kTB$. At the IEEE reference $T_0=290$ K, $kT_0 = 4.00\times10^{-21}$ W/Hz = −173.98 dBm/Hz = −203.98 dBW/Hz. The R&S note uses 20 °C (293 K) and gets −173.93 dBm/Hz [1 §5.2]; both round to −174. The *available* noise power does not depend on the resistance value, which is why the same −174 dBm/Hz applies in 50 Ω and 75 Ω systems. Details and noise figure: [thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md).

**ADC dynamic range.** For an ideal $N$-bit quantiser driven by a full-scale sine, SNR $=6.02N+1.76$ dB, where $6.02 = 20\log_{10}2$ (each bit doubles the amplitude range) and $1.76=10\log_{10}1.5$ (the ratio of sine power to uniform quantisation-noise power, after the factor-of-2 scaling) [5], [1 §5.13]. Derivation belongs to [data converters](../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md).

**Crest factor and PAPR.** Crest factor = peak amplitude/rms amplitude; in dB, $20\log_{10}$(peak/rms) = $10\log_{10}$(peak power / average power). A sine is 3.01 dB. A constant-envelope FM/FSK/LoRa-chirp signal has 0 dB *envelope* PAPR — one reason LoRa and FSK modules can run their PAs in saturation. Noise-like multi-carrier signals (OFDM) are ~10–12 dB in practice [1 §5.10].

**Where dB arithmetic breaks.**
- Anything that *adds* (signals, noise, interferers) must be done in linear units.
- Averaging a dB quantity is a geometric mean of the linear quantity — fine for averaging *gains* of a cascade, wrong for averaging noise power (bias above).
- $\log 0$ is $-\infty$: a perfect match ($\Gamma=0$) has infinite return loss; numerical code needs a floor (e.g. `10*log10(max(x,1e-30))`).
- dB of a negative or complex number is undefined; take the magnitude (and keep the phase separately).
- Uncertainty: ±0.5 dB means +12.2 %/−10.9 % in power, not ±11.5 %. Combine *independent* dB uncertainties by root-sum-square only when they are small (≲1 dB) where the log is nearly linear.

## Design equations & rules of thumb

| Equation / rule | When valid | Typical values |
|---|---|---|
| $G_{\rm dB}=10\log_{10}(P_2/P_1)$ | always (power) | |
| $20\log_{10}(V_2/V_1)$ | same impedance at both ports | |
| $L_{\rm dBW}=L_{\rm dBm}-30$ | always | 33 dBm = 3 dBW |
| $V_{\rm rms}=\sqrt{50\times10^{(L_{\rm dBm}-30)/10}}$ | 50 Ω, sine or any signal (rms) | 0 dBm = 0.224 V |
| $L_{\rm dB\mu V}=L_{\rm dBm}+107$ | 50 Ω | −107 dBm = 0 dBµV = 1 µV |
| $L_{\rm dBmV}=L_{\rm dBm}+48.75$ | 75 Ω | |
| $N=-174+10\log_{10}B+NF$ [dBm] | 290 K, $B$ in Hz | 125 kHz: −123 dBm + NF |
| dBd = dBi − 2.15; ERP = EIRP − 2.15 dB | lossless λ/2 dipole reference | |
| dBic vs dBi(linear) | a CP antenna received by a linear antenna loses 3 dB | 5 dBic patch ≈ 2 dBil for a linear source |
| $P_r=E_{\rm dB\mu V/m}+G_{\rm dBi}-20\log f_{\rm MHz}-77.2$ | far field, matched, polarisation-matched | 40 dBµV/m at 433 MHz, 0 dBi → −90 dBm |
| $AF=20\log f_{\rm MHz}-G_{\rm dBi}-29.77$ dB/m | 50 Ω | |
| $1\,{\rm W/m^2}\leftrightarrow145.8$ dBµV/m | free-space plane wave | |
| $C/N_0-10\log_{10}B=$ SNR | noise flat over $B$ | |
| $6.02N+1.76$ dB | ideal ADC, full-scale sine, Nyquist bandwidth | 12 bit → 74 dB |
| 1 Np = 8.686 dB | | |
| Small change: $x$ % power ≈ $0.0434x$ dB | $|x|\lesssim 10$ % | |

**Mental math kit.** Memorise: 1 dB = 1.26×, 2 dB = 1.58×, 3 dB = 2.00×, 4 dB = 2.51×, 5 dB = 3.16×, 6 dB = 3.98×, 7 dB = 5.01×, 8 dB = 6.31×, 9 dB = 7.94×, 10 dB = 10× (power). Build others: 13 dB = 10 dB + 3 dB = 20×; 17 dB = 20 dB − 3 dB = 50×; 27 dB = 500×; 36 dB = 4000×; −9 dB = 1/8. Voltage ratios: take half the dB (6 dB → ×2 V, 20 dB → ×10 V, 14 dB → ×5 V). The 3 dB ≈ 2 approximation is off by 0.23 %, so ten "3 dB = 2×" steps accumulate 2.3 % (0.1 dB) error — negligible in link budgets.

| dB | power ratio | voltage ratio | | dB | power ratio | voltage ratio |
|---|---|---|---|---|---|---|
| 0.1 | 1.023 | 1.012 | | 7 | 5.012 | 2.239 |
| 0.5 | 1.122 | 1.059 | | 8 | 6.310 | 2.512 |
| 1 | 1.259 | 1.122 | | 9 | 7.943 | 2.818 |
| 2 | 1.585 | 1.259 | | 10 | 10 | 3.162 |
| 3 | 1.995 | 1.413 | | 20 | 100 | 10 |
| 4 | 2.512 | 1.585 | | 30 | 1000 | 31.62 |
| 5 | 3.162 | 1.778 | | 40 | 10⁴ | 100 |
| 6 | 3.981 | 1.995 | | 60 | 10⁶ | 1000 |

For negative dB take reciprocals (−3 dB = 0.501 power, 0.708 voltage).

**dBm ↔ power ↔ voltage at 50 Ω (sine for Vpk/Vpp)**

| dBm | power | V rms | V pk | V p-p | context |
|---|---|---|---|---|---|
| −174 | 4.0 zW | 0.45 nV | 0.63 nV | 1.3 nV | kT₀ in 1 Hz |
| −137 | 20 aW | 31.6 nV | 44.7 nV | 89 nV | ~LoRa SF12/125 kHz sensitivity |
| −120 | 1 fW | 0.224 µV | 0.316 µV | 0.63 µV | |
| −100 | 0.1 pW | 2.24 µV | 3.16 µV | 6.3 µV | |
| −80 | 10 pW | 22.4 µV | 31.6 µV | 63 µV | |
| −60 | 1 nW | 224 µV | 316 µV | 632 µV | |
| −40 | 100 nW | 2.24 mV | 3.16 mV | 6.3 mV | |
| −20 | 10 µW | 22.4 mV | 31.6 mV | 63 mV | |
| −10 | 100 µW | 70.7 mV | 100 mV | 200 mV | |
| 0 | 1 mW | 224 mV | 316 mV | 632 mV | |
| +10 | 10 mW | 707 mV | 1.00 V | 2.00 V | |
| +13 | 20 mW | 1.00 V | 1.41 V | 2.83 V | typical mixer LO |
| +20 | 100 mW | 2.24 V | 3.16 V | 6.3 V | |
| +27 | 0.5 W | 5.0 V | 7.1 V | 14.2 V | |
| +30 | 1 W | 7.07 V | 10.0 V | 20.0 V | E220-900T30D |
| +33 | 2 W | 9.99 V | 14.1 V | 28.3 V | E22-400T33D |
| +40 | 10 W | 22.4 V | 31.6 V | 63 V | |
| +50 | 100 W | 70.7 V | 100 V | 200 V | |

(All computed; verified by `tools/verify/math_decibels.py`.)

## Worked examples

**1. From module datasheet to EIRP (433 MHz rocket downlink).** An EBYTE E22-400T33D is rated 33 dBm. Feed it through 1.0 m of RG-316 (≈0.72 dB/m at 433 MHz, from the 03 [coax and cables](../03-transmission-lines-matching/coax-and-cables.md) table — look up your actual cable) plus an SMA adapter (0.1 dB), into a quarter-wave monopole on the airframe with 1.5 dBi realised gain.
- Power at antenna: 33 − 0.72 − 0.1 = 32.2 dBm → $10^{3.218}$ mW = 1.65 W.
- EIRP = 32.2 + 1.5 = 33.7 dBm = 2.33 W EIRP. ERP = 33.7 − 2.15 = 31.5 dBm = 1.42 W ERP. (Regulators quote limits in these units: Singapore's licence-exempt 433 MHz limit is 10 mW e.r.p. = 10 dBm ERP, so this configuration is 21.5 dB over it and needs an amateur licence or permit — [19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md).)
- Voltage at the module's 50 Ω port: $V_{\rm rms} = \sqrt{50\times2} = 10.0$ V, $V_{\rm pk}=14.1$ V. A probe or ESD diode on that line must survive ±14 V (more under mismatch: with VSWR 3, $|\Gamma|=0.5$, the standing-wave voltage maximum is $1.5\times14.1=21$ V).

**2. Is my SNR good enough? (LoRa noise floor).** Channel bandwidth 125 kHz, receiver noise figure 6 dB.
- $10\log_{10}(125\,000) = 50.97$ dB.
- Noise floor $N = -173.98 + 50.97 + 6 = -117.0$ dBm.
- LoRa SF12 can demodulate at about SNR = −20 dB (Semtech demodulator limit; see [LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md)), so sensitivity ≈ −117 − 20 = −137 dBm. At 50 Ω that is 31.6 nV rms — the table row above.
- A received signal of −110 dBm has SNR = −110 − (−117) = +7 dB. Note "dBm − dBm = dB".

**3. Adding interferers (the "dBm + dBm" trap).** Two uncorrelated interferers arrive at −95 dBm and −101 dBm. Δ = 6 dB → add 0.97 dB → −94.0 dBm total. Check linearly: $10^{-9.5}+10^{-10.1} = 3.162\times10^{-10}+0.794\times10^{-10}=3.956\times10^{-10}$ mW → −94.03 dBm. The wrong answer "−196 dBm" (adding the dB numbers) is off by a factor of $10^{10}$.

**4. Coherent combining (4-element array).** Four identical receive elements, each delivering signal −120 dBm and independent noise −125 dBm (SNR 5 dB each). Phase-aligned sum:
- Signal voltages add: amplitude ×4 → power ×16 → −120 + 12.04 = −107.96 dBm.
- Noise powers add: ×4 → −125 + 6.02 = −118.98 dBm.
- Output SNR = 11.02 dB, an improvement of $10\log_{10}4=6.02$ dB (array gain). If the element signals were mis-phased at random you would get only −113.98 dBm signal on average and no SNR gain.

**5. Field strength to received power (433 MHz).** An EMC scan shows 40 dBµV/m at 433 MHz from your flight computer; how much reaches a 0 dBi receive antenna?
- $20\log_{10}433 = 52.73$.
- $P_r = 40 + 0 - 52.73 - 77.2 = -89.9$ dBm. Antenna factor at 433 MHz for 0 dBi: $52.73-0-29.77=22.96$ dB/m, so the 50 Ω port voltage is $40-22.96=17.0$ dBµV = 7.1 µV → $17.0-107 = -90$ dBm. ✓ Two routes agree.

**6. The "1 %" puzzle.** A reflection coefficient $|\Gamma|$ of 1 % (0.01) is a return loss of 40 dB. The *mismatch loss* it causes is $-10\log_{10}(1-0.01^2) = 0.0004$ dB. A 1 % *increase* in voltage is +0.086 dB, and a 1 % increase in power is +0.043 dB. Four different numbers, all "1 %"; always ask "1 % of what, and of or more?" [1 §3]. At $|\Gamma|=0.1$ (RL 20 dB, VSWR 1.22) mismatch loss is 0.044 dB; at VSWR 2 it is 0.51 dB.

**7. GNSS C/N₀.** A GPS L1 signal arrives at −130 dBm; front-end noise figure 2 dB. $N_0 = -173.98+2 = -171.98$ dBm/Hz. $C/N_0 = -130 - (-171.98) = 42.0$ dB-Hz, within the clear-sky range [3] (this assumes a 290 K antenna; a sky-pointing antenna with $T_a$ ≈ 100 K gives $T_{sys}$ ≈ 270 K and ≈ 44 dB-Hz, ≈ 46 dB-Hz at the −128.5 dBm IS-GPS-200 minimum; KB canonical open-sky range 40–50 dB-Hz, ≥ 45 healthy, < 35 fault — [conventions](canonical-values-and-conventions.md)). In a 2 MHz bandwidth the pre-correlation SNR is $42.0-63.0 = -21$ dB: the signal is below the noise until the spreading-code correlation adds its processing gain (see [spread spectrum](../10-comms-modulation/spread-spectrum-dsss-fhss-css.md)).

**8. Measuring near the noise floor.** Your SDR shows −98.0 dBm in a channel with the transmitter off and −95.5 dBm with it on (RMS detector). Signal alone: $10\log_{10}(10^{-9.55}-10^{-9.80}) = 10\log_{10}(2.818-1.585)\times10^{-10}$ mW = −99.1 dBm. The signal is actually *below* the displayed noise floor; the naive reading was 3.6 dB high.

## Practical notes
- **dBm is a power, not a voltage.** An oscilloscope at 1 MΩ measures volts; converting to dBm requires you to assume a load. A 50 Ω source driving a 1 MΩ scope shows *twice* the voltage it would deliver into 50 Ω (+6 dB) because the source's internal 50 Ω no longer divides it. Terminate in 50 Ω (feed-through terminator or 50 Ω input) before reading dBm.
- **Signal generators** are calibrated as "power delivered into a matched 50 Ω load". Into an open circuit the voltage doubles.
- **Spectrum analysers**: a CW tone reads the same power for any RBW wider than the tone; noise reads $10\log_{10}$(RBW) higher per decade of RBW. Noise-marker functions normalise to dBm/Hz and correct for the log-averaging bias and the RBW filter's noise bandwidth [7]. See [spectrum analysers](../17-test-measurement/spectrum-analyzers.md).
- **Datasheets mix units**: module TX power in dBm *conducted*; antenna gain may be dBi or (in marketing) dBd or even "dB"; regulatory limits may be ERP (dBd reference, e.g. EU 868 MHz: 25 mW ERP) or EIRP. Always normalise to dBm and dBi before comparing. Rules: [ISM band plans](../15-lora-ism-radios/ism-band-plans-duty-cycle.md), [IMDA rules](../19-regulations-safety/singapore-imda-rules.md).
- **Precision**: quoting more than 2 decimals of dB is usually meaningless: 0.01 dB is 0.23 % in power [1 §6.5].
- **S-parameters in dB** use 20 log |S|: $|S_{21}| = 0.5$ is −6.02 dB, i.e. a quarter of the power gets through.
- **Phase noise in dBc/Hz** is a density; to get total integrated phase noise or jitter you integrate the *linear* density over offset frequency (see [phase noise](../07-noise-linearity/phase-noise-and-jitter.md)).

## Common mistakes & misconceptions
1. **"30 dBm + 30 dBm = 60 dBm."** Wrong — adding logs multiplies the powers (units of mW²). Two uncorrelated 1 W signals make 2 W = 33 dBm [1 §4.1]; two coherent in-phase copies make 4 W peak-combined (36 dBm) — but only if their phases are locked.
2. **"There are power decibels and voltage decibels."** There is one decibel, defined on power. 20 log is a shortcut valid only for equal impedances [1 §2.3].
3. **Using 20 log for a power quantity** such as antenna gain, noise figure, RCS or PSD (or 10 log for |S21|, |Γ|, EVM). Rule: if the quantity squared is proportional to power, use 20.
4. **"The −3 dB point is where the voltage halves."** At −3 dB the *power* halves and the voltage is 0.708. The voltage halves at −6 dB.
5. **Forgetting the minus sign convention.** "A loss of −3 dB" and "a gain of −3 dB" mean the same thing to some people and opposite things to others. State "3 dB loss" or "S21 = −3 dB".
6. **dBi vs dBd vs "dB"** — a "5 dB" antenna may be 5 dBd = 7.15 dBi. A 2.15 dB error in a link budget is ~28 % in range.
7. **dBic vs dBi** — a circularly polarised antenna rated in dBic gives 3 dB less when received by (or receiving) a linearly polarised antenna. Relevant to linearly polarised LoRa whips talking to a ground-station helix: budget the 3 dB polarisation loss (see [polarisation mismatch](../09-propagation-link-budget/polarization-mismatch-loss.md)).
8. **dBm/Hz vs dBm.** A noise density must be multiplied by a bandwidth (added $10\log B$) before comparing to a signal power. A spectrum-analyser noise floor "−110 dBm" is meaningless without the RBW.
9. **Confusing dB-Hz with dB/Hz.** C/N₀ in dB-Hz is a ratio with units of Hz; dBm/Hz is a density.
10. **Averaging dB readings of noise** — gives a 2.5 dB low answer. Average in linear power.
11. **dBµV vs dBµV/m** — the first is a voltage at a port, the second a field in space; the antenna factor connects them.
12. **Believing −174 dBm/Hz depends on impedance.** It is the *available* noise power, independent of R [1 §5.2].
13. **Treating percent changes symmetrically** — +10 % then −10 % is not back to the start (−0.04 dB power); ±20 % are +0.79/−0.97 dB in power.
14. **Adding VSWRs or return losses of cascaded parts in dB.** Reflections combine as complex voltages with unknown phases; the best you can do without phase is the worst-case/best-case range from the anti-phase/in-phase rows of the correction table.
15. **Reading a dBFS number as absolute.** dBFS is relative to the converter's full scale, which depends on its reference voltage and front-end gain.
16. **Factor-of-2 (3 dB) convention traps.** 𝓛(f) = S_φ/2; E/N0 vs 2E/N0; real ($f_s/2B$) vs complex ($f_s/B$) processing gain; ERP vs EIRP (2.15 dB); dBi vs dBic; peak vs RMS phasors; mean vs median fade margins. Each page is right in its own convention — the KB's choices are listed in [canonical values and conventions](canonical-values-and-conventions.md).

## How to simulate / verify
- `python3 tools/verify/math_decibels.py` — recomputes every number on this page (dBm↔V, kT, Neper, correction table, coherent sums, dipole 2.15 dBi by numerical integration, field-strength constants 145.8/77.2/29.77, log-averaging bias by Monte Carlo). All checks print PASS.
- Quick Python helpers (paste into a REPL):
```python
import numpy as np
dbm2w = lambda d: 1e-3*10**(d/10);  w2dbm = lambda w: 10*np.log10(w/1e-3)
psum  = lambda *d: w2dbm(sum(dbm2w(x) for x in d))       # uncorrelated sum of levels
vrms  = lambda d, R=50: np.sqrt(dbm2w(d)*R)
```
- scikit-rf: `rf.mag_2_db(x)` (20 log) and `rf.db_2_mag`; `Network.s_db` is 20 log|S|.
- For the log-average bias, simulate exponential noise powers and compare `mean(10*log10(x))` with `10*log10(mean(x))`.

## Open questions / gaps
- dBFS full-scale convention (sine vs square) varies between ADC vendors; the converter pages (14-sdr-dsp) should record which convention each part family uses.
- The exact spectrum-analyser corrections (log-average 2.51 dB plus RBW-filter noise-bandwidth factor ~0.5–1 dB) are instrument-specific; 17-test-measurement should record the values for the analyser Marcus uses.
- LoRa demodulator SNR limits quoted here (−20 dB at SF12) should be cross-checked against the Semtech datasheet in 15-lora-ism-radios.

## Sources
1. A. Winter, *dB or not dB? Everything you ever wanted to know about decibels but were afraid to ask…*, Rohde & Schwarz Application Note 1MA98, v12e (2015); current v14e (2024). §2.1–2.5 definitions and levels; §3 percent conversions; §4.1–4.4 adding powers/voltages; §5.2 noise; §5.3 log averaging; §5.5 phase noise; §5.7 VSWR; §5.8 field strength; §5.10 crest factor; §5.13 ADC; §6 tables. http://courses.ece.ubc.ca/elec391/1MA98_12e.pdf ; https://www.rohde-schwarz.com/appnote/1MA98 (app note). Note: Table 6-1's −3 dB voltage entry "0.798" is a typo for 0.708; the §5.8 example has a swapped unit label.
2. B. N. Taylor, A. Thompson, *Guide for the Use of the International System of Units (SI)*, NIST SP 811 (2008), §8.7 "Logarithmic quantities and units: level, neper, bel". https://www.nist.gov/pml/special-publication-811/nist-guide-si-chapter-8 (standard) — neper/bel definitions, 1 dB = 0.1151 Np, reference must be stated.
3. "GNSS Solutions: Measuring GNSS signal strength", *Inside GNSS*, Nov/Dec 2010. https://insidegnss.com/measuring-gnss-signal-strength/ (trade magazine, technical column) — C/N₀ vs SNR relation, typical 37–45 dB-Hz.
4. A.H. Systems, "Antenna factor calculations and deviations" (also Interference Technology). https://www.ahsystems.com/resources/articles/antenna-factor-calculations ; and TDK "Antenna paper part 3: antenna factor" https://www.tti.com/content/dam/ttiinc/manufacturers/tdk/PDF/antenna_paper_part3.pdf (app notes) — $AF = 9.73/(\lambda\sqrt G)$; constant re-derived here.
5. W. Kester, *MT-001: Taking the mystery out of the infamous formula "SNR = 6.02N + 1.76 dB"*, Analog Devices (2009). https://www.analog.com/media/en/training-seminars/tutorials/MT-001.pdf (app note).
6. W. Kester, *MT-003: Understand SINAD, ENOB, SNR, THD, THD+N and SFDR*, Analog Devices. https://www.analog.com/media/en/training-seminars/tutorials/MT-003.pdf (app note) — dBFS vs dBc specification of SFDR.
7. Keysight Technologies, *Spectrum Analyzers: Noise and Sensitivity* (white paper 3123-1734). https://www.keysight.com/us/en/assets/3123-1734/white-papers/Spectrum-Analyzers-Noise-and-Sensitivity.pdf (app note) — noise floor vs RBW, noise-marker normalisation.
8. Forum evidence for common mistakes (anecdotal, used only to choose topics): Physics Forums "Confusion with dB equation — 10 or 20?" https://www.physicsforums.com/threads/confusion-with-db-equation-10-or-20.641850/ ; All About Circuits "dB level of summation of two sounds of unequal level" https://forum.allaboutcircuits.com/threads/db-level-of-summation-of-two-sounds-of-unequal-level.206535/ ; EDAboard "how to calculate EIRP with antenna gain in dBiC" https://www.edaboard.com/threads/how-to-calculate-eirp-with-antenna-gain-in-dbic.286680/ (forum — anecdotal).
