---
title: RF power measurement — thermal and diode sensors, average/peak/burst power of LoRa packets, directional couplers and wattmeters, attenuators and their ratings, mismatch uncertainty, and cheap AD8307/AD8318 log-detector meters
domain: 17-test-measurement
slug: rf-power-measurement
tags: [power-meter, power-sensor, thermistor, thermocouple, diode-detector, square-law, peak-power, burst-power, duty-cycle, lora, directional-coupler, wattmeter, bird-43, attenuator, dummy-load, mismatch-uncertainty, ad8307, ad8318, log-detector, calibration]
prerequisites: [../00-math-foundations/decibels-and-log-units.md, ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md, ../05-analog-electronics/diodes-schottky-pin-varactor.md]
related: [spectrum-analyzers.md, vna-fundamentals-calibration.md, signal-generators-and-sources.md, sdr-as-test-equipment.md, lab-setup-by-budget.md, rf-bring-up-debug-playbook.md, ../06-rf-circuits/couplers-dividers-combiners.md, ../06-rf-circuits/detectors-and-power-meters.md, ../04-real-components-hf/resistors-at-rf.md, ../15-lora-ism-radios/semtech-chip-family.md, ../19-regulations-safety/lab-safety-esd-high-power.md]
level: mixed
confidence: high
last_updated: 2026-09-27
---

# RF power measurement

## Questions this page answers
- What is the most accurate way to measure my LoRa module's output power on a student budget?
- Thermistor, thermocouple, diode — what is the difference, and why do diode sensors misread some signals?
- My power meter shows +8 dBm but the module is set to +22 dBm — why?
- How much uncertainty does mismatch add to a power reading?
- How do I choose attenuators and dummy loads (power rating, frequency, accuracy)?
- How do I use a directional coupler or a through-line wattmeter, and how far can I trust its SWR reading?
- How good are the cheap AD8307/AD8318 log-detector power meter modules, and how do I calibrate one?

## TL;DR
- **Sensor families** [1]: thermistor (DC-substitution; transfer standards), **thermocouple** (true average, square-law, typically −30 to +20 dBm), **diode** (−70 to +20 dBm for wide-range types; *true square law only from the noise floor to ≈ −20 dBm*, transition −20 to 0 dBm, then linear/peak).
- **Diode law matters for modulated signals**: a CW-calibrated diode sensor reads a two-tone signal of equal average power correctly below −30 dBm but ≈ 0.9 dB low above 0 dBm (script; theory 20 log(2√2/π) = −0.91 dB). **Constant-envelope signals — FSK, GFSK and LoRa chirps — read correctly at any level**, which makes LoRa easy to measure.
- **Bursts**: an averaging meter reads P_burst + 10 log(duty cycle). A 22 dBm SX1262 sending a 41 ms packet every second reads +8.2 dBm; add back +13.9 dB, or use a peak/burst sensor, a gated SA zero-span, or the radio's CW/test mode.
- **Mismatch uncertainty** = 20 log(1 ± |Γ_source||Γ_sensor|): source SWR 1.5 + sensor SWR 1.1 → ±0.08 dB; SWR 2.0 + 1.2 → ±0.26 dB; SWR 3.0 + 1.2 → ±0.40 dB. A well-matched 10 dB pad in front of the sensor cuts the SWR-2.0 case to ±0.03 dB.
- **Attenuators**: the *first* pad dissipates almost all the power (1 W into 10 + 20 dB → 0.90 W in the 10 dB pad). Rate it ≥ 2× the worst-case CW power, check its frequency range and measure its real loss at your frequency.
- **Couplers/wattmeters**: reflected-power (SWR) accuracy is set by **directivity**: with 20 dB directivity, a true SWR 1.22 load reads anywhere from 1.00 to 1.50.
- **AD8307** (DC–500 MHz, 92 dB range −75…+17 dBm, +25 mV/dB, intercept −84 dBm) and **AD8318** (1 MHz–8 GHz, ≈ 57 dB ±1 dB range at 0.9–2.2 GHz, −24.5 mV/dB, intercept ≈ +20…22 dBm, abs. max +12 dBm) modules become ±0.5 dB instruments *after* a multi-point calibration at the frequency of use [2], [3].

## Intuition (no math)
Power is the one RF quantity that everything else is referenced to, and measuring it well is mostly about three things: (1) turning RF into something you can measure at DC — heat (thermistor, thermocouple) or a rectified voltage (diode); (2) getting *all* the power into the sensor, which a mismatch prevents in an uncertain way because you don't know the phase of the reflections; (3) knowing what "power" you mean — the average over seconds, the average while the packet is on, or the instantaneous peak.

Thermal sensors don't care about waveform: heat is heat. Diodes are fast and sensitive, but a diode is a square-law device only for tiny signals; for bigger ones it becomes a peak detector, and then a signal whose envelope varies (two tones, OFDM, QAM) is misread. LoRa's chirp has a constant envelope — the diode sees a steady sine of slowly changing frequency — so even a cheap detector reads it correctly once calibrated with CW.

## The math

### Level 1 — the working formulas
- dBm ↔ W: P(dBm) = 10 log₁₀(P/1 mW); 1 W = 30 dBm; 0 dBm into 50 Ω = 0.224 V rms.
- **Average power of a packetised transmitter**: P_avg = P_burst · D, D = t_on/T. In dB: P_avg = P_burst + 10 log D.
- **Mismatch uncertainty** (source reflection Γ_g, sensor reflection Γ_l, phases unknown): the power delivered differs from the "matched" value by a factor |1 − Γ_g Γ_l|⁻², whose limits are
  $$MU = 20\log_{10}(1\pm|\Gamma_g||\Gamma_l|)\ \text{dB}.$$
  (Link: [mismatch loss vs uncertainty](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md).)
- **Pad dissipation**: a pad of A dB fed with P_in dissipates P_in(1 − 10^{−A/10}).
- **Log detector transfer**: V_out = S·(P_in − P_x), slope S (V/dB), intercept P_x (dBm). AD8307: S = +25 mV/dB, P_x = −84 dBm [2]; AD8318: S ≈ −24.5 mV/dB, P_x ≈ +20…22 dBm [3]. Invert: P_in = V_out/S + P_x.

### Level 2 — the diode detector law, derived
A diode biased by a constant current I₀ with an RF voltage v cos ωt across it (and a video filter that averages): the diode current i = I_s(e^{v_d/nV_T} − 1). Requiring the *average* current to stay I₀ forces a DC shift ΔV of the junction voltage with
$$\langle e^{(\Delta V + v\cos\omega t)/nV_T}\rangle = 1 \;\Rightarrow\; \Delta V = -nV_T\ln I_0\!\left(\frac{v}{nV_T}\right),$$
where I₀(·) is the modified Bessel function. For small x = v/nV_T, ln I₀(x) ≈ x²/4 → |ΔV| = v²/(4nV_T) ∝ P (**square law**); for large x, ln I₀(x) ≈ x − ½ ln(2πx) → |ΔV| ≈ v (**linear/peak**). With v the peak voltage of P in 50 Ω and n = 1.05, the output deviates from square law by −0.04 dB at −30 dBm, −0.33 dB at −20 dBm, −2.0 dB at −10 dBm and −5.5 dB at 0 dBm (script §2) — matching Keysight's description of the square-law region ending near −20 dBm and the linear region beginning above ≈ 0 dBm [1]. Sensors correct the static curve with calibration tables, but no static table fixes *envelope-varying* signals in the linear region: for two equal tones the envelope is 2a|cos(πΔf t)|; a peak-reading detector averages the envelope (mean 4a/π) whereas a CW of the same power has amplitude √2 a, so the indicated power is 20 log(2√2/π) = −0.91 dB low (script: −0.15 dB at −20 dBm, −0.55 at −10, −0.80 at 0, −0.90 at +20 dBm).

Modern "wide-dynamic-range" sensors avoid this by switching between diode stacks so the active diodes stay in their square-law region (e.g. two paths covering −70…+20 dBm) [1]; peak-power sensors instead deliberately use the fast diode as an envelope detector and are calibrated for it.

### Level 3 — uncertainty budget of a power measurement
A typical budget combines: sensor calibration factor uncertainty (1–3 % for a good thermocouple/diode sensor), meter instrumentation (≈ 0.5 %), zero/zero-drift and noise (important below −50 dBm for diode sensors), linearity, temperature, **mismatch** (often the largest term), and for attenuated measurements the attenuator's calibrated loss uncertainty (±0.05–0.3 dB) plus its own mismatch at both ports. Systematic worst-case terms add linearly; independent random terms add RSS (Keysight AN 1449-3 [4]; same structure as the VNA budget in [VNA calibration](vna-fundamentals-calibration.md)). Mismatch between cascaded elements (source–pad–pad–sensor) creates several Γ·Γ products; a well-matched pad next to a poorly matched source is the classic fix, because the source's reflection is seen through the pad twice (−2A dB) while the pad's own |Γ| is small (script §1: SWR-2.0 source, SWR-1.2 sensor: ±0.26 dB → ±0.07 dB with a 6 dB pad → ±0.03 dB with 10 dB).

## Design equations & rules of thumb

| Quantity | Relation / value | Notes |
|---|---|---|
| Averaging meter on bursts | P_burst = P_avg − 10 log D | measure D (ToA, period) |
| Mismatch uncertainty | 20 log(1 ± \|Γg\|\|Γl\|) | SWR 1.5 & 1.1 → ±0.08 dB |
| Pad improves source match | Γ_eff ≈ √(Γ_pad² + (Γ_src 10^{−A/10})²) | 10 dB pad: SWR 2 → ≈ 1.09 |
| Diode square-law limit | ≈ −20 dBm [1] | transition to ≈ 0 dBm |
| Two-tone error, linear region | −0.91 dB (CW-calibrated) | 20 log(2√2/π) |
| Thermocouple range | ≈ −30 to +20 dBm [1] | true average |
| Wide-range diode sensors | −70 to +20 dBm [1] | multi-path |
| Coupler directivity D | reflected reading Γ ± 10^{−D/20} | need D ≥ RL + 15 dB for ±1 dB-ish |
| Pad dissipation | P(1 − 10^{−A/10}) | first pad takes most |
| AD8307 | +25 mV/dB, −84 dBm intercept, −75…+17 dBm, DC–500 MHz [2] | input 1.1 kΩ ∥ 1.4 pF — needs 50 Ω termination |
| AD8318 | −24.5 mV/dB, ≈ +20 dBm intercept, ±1 dB over ≈ 57 dB (0.9–2.2 GHz), abs max +12 dBm [3] | 10 ns response — resolves bursts |

## Worked examples

**Example 1 — measuring an E22-900T22S (SX1262, +22 dBm) at 915 MHz with a thermocouple sensor.** Put the module in CW/test mode if its firmware allows (then no duty-cycle correction). Chain: module → SMA → 20 dB 2 W pad (calibrated: 20.12 dB at 915 MHz on the VNA) → sensor (range to +20 dBm, so +2 dBm is comfortable). Reading +1.74 dBm → P_out = 1.74 + 20.12 = 21.86 dBm. Mismatch: module output SWR unknown (assume 2.0, |Γ| 0.33) into the pad input (SWR 1.05, |Γ| 0.024) → ±0.07 dB; pad output (SWR 1.05) into the sensor (SWR 1.1) → ±0.01 dB; pad calibration ±0.05 dB; sensor cal factor ±2 % (±0.09 dB) → total ≈ ±0.22 dB worst case, ±0.13 dB RSS. Caveat: the module's power into a 50 Ω pad may differ from its power into your antenna (load-pull).

**Example 2 — the "wrong" power reading.** Same module in normal packet mode, 41.2 ms packets every 1.0 s: an averaging meter reads 8.15 dBm; burst power = 8.15 − 10 log(0.0412) = 22.0 dBm (script §4). With a 60 s interval and 1.32 s packets (D = 2.2 %) the correction is +16.6 dB. Measure D with a scope on the TX-enable line or an SA in zero span.

**Example 3 — calibrating an AD8318 module (AliExpress "1–8000 MHz RF power meter").** Feed a generator at 915 MHz through calibrated pads so the levels at the module are known (verify the generator with a real power meter or a calibrated SA at one level). Two-point calibration at −40 and −10 dBm gives slope −23.9 mV/dB and intercept 21.5 dBm on our synthetic device with ±0.4 dB conformance ripple; residual error across −55…−5 dBm is up to 0.73 dB. A 12-point least-squares fit gives −24.34 mV/dB and 0.41 dB residual; a lookup table with interpolation removes the ripple at that frequency (script §3). Recalibrate per band (433, 868/915, 1575 MHz) and note the ±0.5 dB temperature drift [3]. Protect it: +12 dBm absolute maximum [3] — a 1 W module needs ≥ 30 dB in front.

**Example 4 — SWR from a cheap coupler.** A coupler with 20 dB directivity on a ground-station feeder whose true SWR is 1.22 (RL 20 dB) reads 1.00–1.50 depending on phase; with 30 dB directivity 1.15–1.30; with 40 dB 1.20–1.25 (script §5). Most HF/VHF "SWR meters" have 20–30 dB directivity — they are fault indicators, not precision instruments. Use the VNA for RL, and the coupler for "is anything broken while transmitting".

**Example 5 — pad chain for a 1 W test.** 1 W into 10 dB then 20 dB: the 10 dB pad dissipates 0.90 W, the 20 dB pad 0.10 W; into 20 + 20 dB, the first dissipates 0.99 W (script §6). Put a 2–5 W pad (or a coupler/dummy load with a tap) first; cheap "2 W" SMA pads get hot and drift in value.

## Practical notes
- **Budget options**: (a) a used thermocouple/diode power meter + sensor (HP/Agilent 436A/437B/E4418B with 8481A/8482A/E9300A, often US$200–600 used) — the best accuracy per dollar; (b) a USB power sensor (Mini-Circuits PWR-series, similar); (c) an AD8318/AD8307 module + your own calibration (±0.5–1 dB); (d) a spectrum analyzer (±0.7–2 dB) — see [lab setup](lab-setup-by-budget.md).
- **Zero the sensor** with no RF applied before low-level readings; let thermal sensors stabilise after large power steps.
- **Calibration factor**: enter the sensor's cal factor for the frequency (printed on the sensor or in its data), or the meter reads 1–5 % off.
- **Attenuators**: check frequency rating (cheap "6 GHz" pads can be ±1 dB off at 5.8 GHz), power rating (average *and* peak), and measure S21/S11 on the VNA. Keep a "calibrated" set labelled with their measured loss at 433/915/1575/2450 MHz.
- **Dummy loads**: a 50 Ω load rated for the full CW power (LoRa modules can get stuck in TX); SMA loads are typically 1–2 W; N-type loads 5–50 W; oil-filled for more. Check its RL at your frequency (a "2 W 3 GHz" load may be RL 20 dB at 2.4 GHz).
- **Directional couplers** give a sample (e.g. −20 or −30 dB) while the main line goes to the antenna or load — the correct way to monitor a transmitter continuously. Coupling flatness and directivity vs frequency matter; calibrate the coupled path with the VNA ([couplers](../06-rf-circuits/couplers-dividers-combiners.md)).
- **Through-line wattmeters** (Bird 43 style, plug-in elements per band/power) are rugged and accurate to about ±5 % of full scale (manufacturer class; unverified here) — read in the top half of the scale.
- **Heat and safety**: RF burns and hot pads are real at 1–5 W; never disconnect a transmitting cable; see [lab safety](../19-regulations-safety/lab-safety-esd-high-power.md).

## Common mistakes & misconceptions
- **Averaging meter on packets, no duty-cycle correction** — reads 10–20 dB low.
- **Diode sensor above −20 dBm on a modulated (non-constant-envelope) signal** — up to ~1 dB error for two-tone, more for high-PAPR signals; use a thermocouple or keep the diode in square law with a pad.
- **Nominal pad values** — a "30 dB" pad is 29.6–30.5 dB; measure it.
- **Ignoring mismatch** — an SWR-3 source into an SWR-1.2 sensor is ±0.4 dB of uncertainty before any other error.
- **Trusting a cheap SWR meter's 1.1:1** — its own directivity may be the limit.
- **Overloading log-detector modules** — +12 dBm absolute maximum on the AD8318 [3].
- **Measuring into the wrong load**: a PA's output power depends on its load; the power into a 50 Ω pad is not necessarily the power into the antenna.

## How to simulate / verify
- `python3 tools/verify/meas_power.py` — (1) mismatch uncertainty and the pad fix; (2) diode detector law via Bessel I₀, square-law deviation and two-tone error; (3) log-detector two-point and least-squares calibration; (4) duty-cycle corrections for LoRa packets; (5) coupler directivity vs SWR reading; (6) pad dissipation.
- Cross-check a power meter against the SA and the log detector at one frequency and level before a campaign; log the three readings (record-everything).

## Open questions / gaps
- ToA/period values in Example 2 and script §4 are illustrative; use the team's actual packet schedule (see `tools/verify/lora_toa.py` in domain 15).
- The Bird-43 ±5 % figure and the used-meter prices are from general knowledge, not verified sources.
- No measurement yet of an actual AliExpress AD8318 module's conformance across 433/915/1575 MHz.

## Sources
1. Keysight AN 1449-2, *Fundamentals of RF and Microwave Power Measurements (Part 2): Power Sensors and Instrumentation*, 5988-9214EN — thermistor/thermocouple/diode sensors, square-law region (noise to ≈ −20 dBm), transition to ≈ 0 dBm, linear above; thermocouple ≈ −30 to +20 dBm; wide-dynamic-range diode sensors −70 to +20 dBm; peak-power sensors. (app note; read)
2. Analog Devices, *AD8307 Low Cost DC–500 MHz, 92 dB Logarithmic Amplifier* datasheet — −75 to +17 dBm, 25 mV/dB (23–27), intercept −84 dBm, ±0.3 dB typ conformance, input 1.1 kΩ ∥ 1.4 pF. (datasheet; read, foxdelta mirror)
3. Analog Devices, *AD8318 1 MHz to 8 GHz, 70 dB Logarithmic Detector/Controller* datasheet Rev. B — per-frequency slope/intercept/±1 dB range (900 MHz: −24.5 mV/dB, 22 dBm, 57 dB; 1.9 GHz: −24.4 mV/dB, 20.4 dBm), ±0.5 dB over temperature, 10 ns response, abs. max +12 dBm. (datasheet; read, octopart mirror)
4. Keysight AN 1449-3, *Fundamentals of RF and Microwave Power Measurements (Part 3): Power Measurement Uncertainty per International Guides*, 5988-9215EN — uncertainty budgets, mismatch. (app note; cited)
5. Keysight AN 1449-1 (Part 1), *Introduction to Power, History, Definitions, International Standards and Traceability*, 5988-9213EN — average/pulse/peak definitions. (app note; cited)
6. This repository: `tools/verify/meas_power.py`. (verification)
