---
title: RF detectors and power meters (diode square-law detectors, log amps, RMS detectors, temperature effects)
domain: 06-rf-circuits
slug: detectors-and-power-meters
tags: [detector, diode-detector, schottky, zero-bias, square-law, voltage-sensitivity, tss, log-amplifier, ad8307, ad8318, rms-detector, ltc5582, crest-factor, temperature-compensation, power-monitor, vswr-monitor]
prerequisites:
  - ../05-analog-electronics/diodes-schottky-pin-varactor.md
  - ../00-math-foundations/decibels-and-log-units.md
related:
  - couplers-dividers-combiners.md
  - power-amplifiers.md
  - rf-switches-attenuators-limiters.md
  - ../17-test-measurement/rf-power-measurement.md
  - ../07-noise-linearity/thermal-noise-and-noise-temperature.md
  - ../10-comms-modulation/digital-modulation-psk-qam-fsk.md
level: mixed
confidence: medium
last_updated: 2026-09-27
---

# RF detectors and power meters

## Questions this page answers
- How does a Schottky diode turn RF into a DC voltage, and why is it "square-law" at low power?
- What is voltage sensitivity (mV/µW) and tangential signal sensitivity (TSS)?
- Where does the detector change from square-law to linear (peak) detection?
- How do log amplifiers (AD8307, AD8318) and RMS detectors (LTC5582) differ, and which should I use for a PA power/VSWR monitor?
- Why does my detector read differently for QPSK, 16-QAM or noise than for a CW tone of the same power?
- Why do diode detectors drift with temperature, and how are they compensated?

## TL;DR
- A diode biased at (or near) zero with RF voltage $v$ across its junction produces an open-circuit DC output $\Delta V=v^2/(4nV_T)$ (square law, output ∝ power). With all available power delivered to the junction resistance $R_j=nV_T/(I_s+I_b)$, the **ideal voltage sensitivity is $1/[2(I_s+I_b)]$** — 167 mV/µW for the HSMS-285x zero-bias Schottky ($I_s$ = 3 µA, $R_j$ ≈ 9 kΩ). Junction capacitance, series resistance and video loading cut this to ≈ 123 mV/µW in a lossless-match model at 915 MHz; the data sheet quotes **40 mV/µW at 915 MHz** (100 kΩ load) and **TSS −57 dBm** (2 MHz video bandwidth) [1] — matching-network and package losses explain the rest (see gaps).
- Square law holds only at low power; the output slope in dB changes from 2 dB/dB (square law, $V\propto P$) to 1 dB/dB (linear, $V\propto\sqrt P$) around −35 to −20 dBm (model; data sheet treats < −20 dBm as small-signal [1]).
- TSS follows from video noise: $\sqrt{4kTR_VB}$ = 16 µV in 2 MHz for $R_V$ = 8 kΩ → TSS ≈ −60/−58.5 dBm (with a 0/3 dB NF video amplifier) vs −57 dBm data sheet (verified).
- **Log amps** compress progressively and output volts per dB: AD8307 DC–500 MHz, 92 dB (−75 to +17 dBm), 25 mV/dB, intercept −84 dBm [2]; AD8318 1 MHz–8 GHz, ≈ 60 dB within ±1 dB, −25 mV/dB, 10 ns response [3]. Ideal for wide-range RSSI and PA power control; with a 10-bit 3.3 V ADC, 0.13 dB/LSB.
- **RMS detectors** (LTC5582: 40 MHz–10 GHz, up to 57 dB linear-in-dB range, −60 to +2 dBm depending on frequency, ±0.5 dB over temperature, 90 ns rise) read true power regardless of modulation [4].
- **Waveform error** (computed): relative to RMS, a peak detector reads +5.0 dB (QPSK RC 0.35), +7.0 dB (16-QAM), +11.5 dB (Gaussian noise); a log-average detector reads −1.0, −1.6 and −2.51 dB (the last is exactly $-\gamma_E\cdot10/\ln10$ for a Rayleigh envelope). For LoRa/FSK (constant envelope) all detectors agree.
- **Temperature**: zero-bias Schottky sensitivity tracks $I_s(T)$ (≈ doubling every 18 °C for a 0.25 eV barrier) → several dB drift; use a matched reference diode (e.g. HSMS-2852 pair, ΔV_F ≤ 15 mV [1]) and calibration, or an IC detector with specified temperature stability.

## Intuition (no math)
A diode conducts a little more on the positive half-cycle than it resists on the negative one, so an RF voltage across it produces a small net DC current — rectification. For tiny signals, the diode's I–V curve is a smooth exponential, and the net DC is proportional to the *square* of the RF voltage — to the RF power. That is the square-law region, where a diode is a true power meter (for any waveform). For bigger signals the diode starts to follow the peaks: the output becomes proportional to the peak voltage, as in an AM radio's envelope detector.

A log amplifier is a chain of limiting amplifiers each with its own detector; small signals are detected by the last (most amplified) stages, big signals by the first, and summing all the detector outputs gives a voltage proportional to the logarithm of the input — decibels directly, over 60–90 dB. Because each stage responds to the envelope, a log amp measures the average of the log of the envelope — for signals with varying envelopes that is less than the log of the average power, so it reads low.

An RMS detector squares the signal (e.g. with a translinear circuit or by matching a heater's temperature) and averages, so it reads true power for any modulation — at the cost of a slower response and often less dynamic range.

## The math

### Level 1 — definitions
- Voltage sensitivity $\gamma=\Delta V_{out}/P_{in}$ (mV/µW) in the square-law region; current sensitivity $\beta_i=\Delta I/P$ (A/W).
- Video resistance $R_V=R_j+R_s$; junction resistance $R_j=nV_T/(I_s+I_b)$ (the HSMS-285x data sheet writes $8.33\times10^{-5}\,nT/(I_s+I_b)$ [1]).
- Tangential sensitivity (TSS): input power at which the detected pulse sits "tangentially" on the noise — ≈ 8 dB video SNR by convention.
- Log-amp law: $V_{out}=V_{slope}(P_{in}-P_{intercept})$.

### Level 2 — derivations

**(a) Square-law output.** With $i=I_s(e^{v/nV_T}-1)$, bias current $I_b$ and a small RF voltage $V_p\cos\omega t$ across the junction, the average current increases by $(I_s+I_b)\,\overline{(V_p\cos\omega t)^2}/(2(nV_T)^2)=(I_s+I_b)V_p^2/(4(nV_T)^2)$ (from the second-order term of the exponential). Into an open circuit this is balanced by a DC voltage $\Delta V=\Delta I\,R_j=V_p^2/(4nV_T)$. The RF power absorbed by $R_j$ is $V_p^2/(2R_j)$, so
$$\gamma=\frac{\Delta V}{P}=\frac{R_j}{2nV_T}=\frac{1}{2(I_s+I_b)}.$$
Bias current lowers $R_j$ (easier to match, faster video response, less temperature sensitivity) but lowers γ. Zero-bias diodes use a low barrier (large $I_s$) so that $R_j$ is manageable (kΩ rather than MΩ) without bias [1][5].

**(b) Parasitics.** The junction capacitance $C_j$ shunts $R_j$: $\mathrm{Re}\{R_j\|(1/j\omega C_j)\}\approx1/(\omega^2C_j^2R_j)$ when $\omega C_jR_j\gg1$. The series resistance $R_s$ then takes a fraction $R_s/(R_s+\mathrm{Re}Z_j)$ of the matched power: 20 % at 915 MHz, 64 % at 2.45 GHz for the HSMS-285x (0.18 pF, 25 Ω) — sensitivity falls with frequency. A finite video load $R_L$ divides the output by $R_L/(R_L+R_V)$.

**(c) Large signal.** For a half-wave detector (series diode, capacitor, load $R_L$), DC balance is $I_s[e^{-V_o/nV_T}I_0(V_p/nV_T)-1]=V_o/R_L$ with $I_0$ the modified Bessel function. Small $V_p$: $V_o\approx V_p^2/(4nV_T)$ (square law); large $V_p$: $I_0(x)\approx e^x/\sqrt{2\pi x}$ gives $V_o\approx V_p-\frac{nV_T}{2}\ln(2\pi V_p/nV_T)$ (linear, peak detection). Script B shows the slope moving from 2 to 1 dB/dB.

**(d) TSS.** Video noise $v_n=\sqrt{4kTR_VB_v}$ (plus the video amplifier); TSS ≈ the input giving $\gamma P\approx2.5v_n$ → $P_{TSS}\approx2.5\sqrt{4kTR_VB_v}/\gamma$. HSMS-285x: 2.5 × 16 µV / 40 mV/µW = 1 nW = −60 dBm (−57 dBm on the data sheet) [1].

**(e) Log detector of a random envelope.** A successive-detection log amp outputs ≈ $\overline{20\log|x|}$. For Gaussian noise the envelope is Rayleigh; $E[\ln r^2]=\ln(2\sigma^2)-\gamma_E$, so the log-average is $10\log(e)\,\gamma_E=2.51$ dB below the RMS power (script E, exact to 0.05 dB). Modulated signals fall in between (QPSK −1.0 dB, 16-QAM −1.6 dB with 0.35 roll-off). Log amps therefore need a modulation-dependent calibration; RMS detectors don't.

### Level 3 — power meters and system use
- **Thermal (thermistor/thermocouple) sensors** measure true average power over wide bandwidths and are the reference standard; **diode power sensors** are fast and sensitive (to −70 dBm) but square-law only below ≈ −20 dBm, with correction tables beyond ([power measurement](../17-test-measurement/rf-power-measurement.md)).
- **Power control loops** (TX power servo) use a coupler + log/RMS detector + ADC/DAC; the detector's slope, temperature drift and waveform error set the loop's accuracy.
- **VSWR monitors**: two detectors on forward and reflected ports of a coupler; the coupler's directivity limits accuracy (a 10 dB-directivity microstrip coupler cannot resolve return losses much better than ≈ 10 dB — see [couplers](couplers-dividers-combiners.md#example-6--10-db-and-20-db-microstrip-couplers-why-directivity-is-poor)).
- **Video bandwidth vs sensitivity**: TSS rises 5 dB per decade of video bandwidth (output voltage ∝ P while noise voltage ∝ √B_v).

## Design equations & rules of thumb

| Quantity | Equation | Typical |
|---|---|---|
| Junction resistance | $R_j=nV_T/(I_s+I_b)$ | HSMS-285x: ≈ 9 kΩ at zero bias |
| Ideal voltage sensitivity | $1/[2(I_s+I_b)]$ | 167 mV/µW ideal; 40 mV/µW measured at 915 MHz |
| Square-law output | $v^2/(4nV_T)$ | open circuit |
| Square-law limit | ≈ −20 dBm (zero-bias Schottky) | above: linear/peak |
| TSS | $\approx2.5\sqrt{4kTR_VB_v}/\gamma$ | −57 dBm at 2 MHz video BW |
| Log amp | $V=V_{slope}(P-P_{int})$ | AD8307: 25 mV/dB, −84 dBm |
| Log-average of Rayleigh | −2.51 dB vs RMS | noise-like signals |
| Peak vs RMS | PAPR | QPSK 5 dB, 16-QAM 7 dB, noise ≈ 11 dB (finite record) |

## Worked examples

### Example 1 — Output-power monitor for a 2 W 433 MHz transmitter
Sample the PA output with a weak coupler (≈ −40 dB, e.g. the short coupled section in [couplers](couplers-dividers-combiners.md#example-4--forwardreflected-power-sampling-for-a-433-mhz-2-w-pa)); +33 dBm → −7 dBm at an AD8307 → $V_{out}=0.025(−7+84)=1.93$ V, comfortably inside the −75 to +17 dBm range, 0.13 dB per LSB with a 10-bit 3.3 V ADC [2]. LoRa is constant envelope, so a log amp reads correctly without waveform correction. A second detector on the reflected port gives a VSWR alarm (accuracy limited by coupler directivity).

### Example 2 — RSSI for a receiver at 915 MHz
An AD8318 (−25 mV/dB, 1 MHz–8 GHz, ≈ 60 dB range [3]) after the LNA gives a fast (10 ns) RSSI for AGC or burst detection. For QPSK/OFDM-like signals, correct by ≈ +1 to +2.5 dB (log-average error) or use an RMS detector (LTC5582 [4]).

### Example 3 — A zero-bias diode "field-strength meter"
HSMS-2850 matched at 915 MHz: 40 mV/µW → at −40 dBm (0.1 µW) ≈ 4 mV; at −57 dBm (TSS) ≈ 80 µV — measurable with a chopper/instrumentation amp. Above ≈ −20 dBm the reading stops being proportional to power; calibrate against a signal generator and a power meter, and expect several dB of drift over outdoor temperatures unless compensated.

### Example 4 — Measuring a noise-like signal with the wrong detector
Wideband noise (e.g. a jammer or OFDM) read by a peak detector: +11 dB error (record-length dependent); by a log detector: −2.5 dB; by an RMS detector: correct. A spectrum analyser in log-video/"sample" mode shows the same −2.5 dB bias for noise — the origin of the "noise marker" correction ([spectrum analysers](../17-test-measurement/spectrum-analyzers.md)).

## Practical notes
- **Matching:** a zero-bias diode's RF impedance is high (kΩ with ≈ 0.2 pF): a lossless match to 50 Ω is narrowband; a 50–68 Ω shunt resistor gives a broadband (but 1/Q-lossy) match — common in wideband detectors.
- **Video filter:** the RC after the diode sets response time vs ripple; its capacitor must be an RF short (tens of pF) and the video load large (≥ 100 kΩ) to preserve sensitivity.
- **Temperature compensation:** use a dual matched diode (one detecting, one reference with identical bias/load) and take the difference; this cancels the DC offset drift; residual sensitivity drift needs calibration.
- **Log/RMS ICs:** follow the reference layout for input coupling (often AC-coupled with a 50 Ω termination), decouple the supply, and note the intercept/slope temperature coefficients.
- **Protection:** zero-bias Schottkys have low breakdown (HSMS-285x PIV 2 V [1]); +10 dBm across them is already risky.

## Common mistakes & misconceptions
- *"A diode detector measures power."* Only in the square-law region (≲ −20 dBm for zero-bias parts); above it, it measures peak voltage.
- *"Log amps read true power."* They read the average of the log of the envelope — low by 1–2.5 dB for modulated/noise signals.
- *"More video bandwidth is free."* TSS degrades with √B (5 dB per decade).
- *"Zero-bias detectors don't drift."* Their sensitivity follows $I_s(T)$; compensate or calibrate.
- *"The detector's input is 50 Ω."* Bare diodes are kΩ-level; IC detectors specify their input impedance — check the match at your frequency.

## How to simulate / verify
- `tools/verify/rfckt_detectors.py`: diode sensitivity from first principles with HSMS-285x SPICE values, parasitic losses, square-law-to-linear transition (Bessel-function large-signal solution), TSS estimate, AD8307 transfer, waveform-dependent readings (peak/log/RMS) for CW/QPSK/16-QAM/noise, temperature model.
- SPICE (diode model + matching network, transient or harmonic balance) for a specific board; vendor evaluation boards for log/RMS ICs.
- Bench: signal generator + calibrated attenuators to measure detector law and slope; a thermal power sensor as reference.

## Open questions / gaps
- **Discrepancy:** first-principles ideal sensitivity (167 mV/µW; ≈ 123 mV/µW after $C_j$/$R_s$/video losses) vs the HSMS-285x data sheet's 40 mV/µW at 915 MHz. Matching-network loss and package parasitics (the data sheet refers to AN1124 for the package model) must account for the factor ≈ 3; not quantified here (logged).
- The temperature model (Is ∝ T² exp(−qφB/kT), φB = 0.25 eV assumed) predicts large drift (+14.5/−16.7 dB from −20/+85 °C relative to 25 °C for the ideal junction); real detectors with matching networks drift less but still several dB — no measured data gathered. Confidence: low for these numbers.
- Log-amp waveform errors for specific ICs (vendor-characterised) differ slightly from the ideal log-average model.

## Sources
1. Agilent/Avago (Broadcom), *HSMS-285x Series Surface Mount Zero Bias Schottky Detector Diodes* data sheet: TSS −57 dBm (915 MHz, 2 MHz video BW), γ 40 mV/µW (915 MHz, RL 100 kΩ, −40 dBm), R_V 8 kΩ, SPICE (Is 3 µA, n 1.06, Rs 25 Ω, Cj0 0.18 pF, BV 3.8 V), R_j formula, PIV 2 V, pair matching ΔV_F ≤ 15 mV. https://datasheet.octopart.com/HSMS-2850-TR1G-Avago-datasheet-26413.pdf (datasheet; read via pdftotext)
2. Analog Devices, *AD8307 Low Cost, DC to 500 MHz, 92 dB Logarithmic Amplifier* data sheet: −75 to +17 dBm, 25 mV/dB, intercept −84 dBm, 2.7–5.5 V, 7.5 mA. https://www.analog.com/media/en/technical-documentation/data-sheets/ad8307.pdf (datasheet; via vendor summary)
3. Analog Devices, *AD8318 1 MHz to 8 GHz, 70 dB Logarithmic Detector/Controller* data sheet: log conformance 1 MHz–6 GHz (useful to 8 GHz), ≈ 60 dB within ±1 dB, −25 mV/dB, 10 ns response. https://www.analog.com/media/en/technical-documentation/data-sheets/ad8318.pdf (datasheet; via summary)
4. Analog Devices (Linear Technology), *LTC5582 40 MHz to 10 GHz RMS Power Detector* data sheet: −60 to +2 dBm (frequency dependent), up to 57 dB linear range, ±0.5 dB over temperature, 90 ns rise, 41.6 mA at 3.3 V. https://www.analog.com/media/en/technical-documentation/data-sheets/ltc5582.pdf (datasheet; via summary)
5. Hewlett-Packard/Agilent application notes on Schottky detectors (AN 923 "Schottky barrier diode video detectors", AN 986 "Square law and linear detection", AN 1089/1124) — square-law theory, zero-bias design, package modelling. (app notes; background, not re-read here)
6. Euler–Mascheroni constant result for the log of a Rayleigh/exponential variable: standard probability result (e.g. Papoulis, *Probability, Random Variables and Stochastic Processes*); verified numerically. (textbook)
