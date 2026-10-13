---
title: Basic bench instruments — frequency counters (gate time, ±1 count, reciprocal counting, prescalers, time-base error), multimeters (Ω/V loading, true RMS, crest factor, DMMs at RF and diode RF probes), scope triggering and probe compensation, and dip meters
domain: 17-test-measurement
slug: basic-bench-instruments
tags: [frequency-counter, gate-time, plus-minus-one-count, reciprocal-counter, prescaler, time-base, tcxo, ocxo, gpsdo, trigger-error, multimeter, dmm, ohms-per-volt, loading, true-rms, average-responding, form-factor, crest-factor, rf-probe, diode-detector, oscilloscope-trigger, holdoff, probe-compensation, dip-meter, grid-dip, coupled-resonators]
prerequisites: [../00-math-foundations/decibels-and-log-units.md, ../01-circuit-theory/transient-and-step-response.md, oscilloscopes-and-probing-for-rf.md]
related: [oscilloscopes-and-probing-for-rf.md, spectrum-analyzers.md, bench-measurement-recipes.md, nanovna-librevna-practical.md, signal-generators-and-sources.md, lab-setup-by-budget.md, rf-bring-up-debug-playbook.md, sdr-as-test-equipment.md, ../04-real-components-hf/crystals-and-resonators.md, ../05-analog-electronics/oscillators.md, ../06-rf-circuits/detectors-and-power-meters.md, ../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md]
level: intro
confidence: medium
last_updated: 2026-10-12
---

# Basic bench instruments

## Questions this page answers
- My frequency counter shows nine digits — how many of them are true?
- What is gate time, and why does a cheap counter show only "433.920 0 MHz" after one second?
- What is the difference between a direct counter and a reciprocal counter, and what does a prescaler cost me?
- How accurate is the frequency of my 433 MHz transmitter as read on a counter with a plain crystal time base?
- Why does my analogue meter read a lower voltage than my DMM on the same bias node?
- What is "true RMS", and why does my cheap meter read a square wave 11 % high?
- Can I measure RF with a multimeter?
- How do I trigger a scope reliably on a LoRa packet?
- How do I compensate a 10× probe, and what happens if I don't?
- What is a dip meter, and how do I use one (or a NanoVNA instead) to find a resonance?

## TL;DR
- **Counter error = ±1 count ± time-base error ± trigger error** [1]. A direct counter resolves ±1/T_gate Hz (±1 Hz in 1 s at any frequency); a **reciprocal** counter times whole input periods against a fast clock, so its *relative* resolution ≈ t_res/T_gate whatever the input frequency (10⁻⁹ in 1 s for 1 ns; interpolating counters do 20–100 ps) [1], [2]. At 1 kHz that is 10⁶× finer than a direct counter (script §A).
- **The time base usually dominates at RF**: a 5 ppm plain crystal is ±2.17 kHz at 433.92 MHz, 2 000× the ±1 count; a 1 ppm TCXO ±434 Hz; an OCXO (10⁻⁸) ±4.3 Hz; a GPSDO (10⁻¹¹) ±0.004 Hz (script). Lock the counter (and SA, VNA, generator) to a GPS-disciplined 10 MHz before you measure ppm-level LoRa offsets.
- **A ÷N prescaler on a direct counter costs a factor N in resolution** for the same gate time (÷64: ±64 Hz in 1 s) [1]; reciprocal counters do not lose resolution this way.
- **Meters load what they measure**: an analogue meter's Ω/V rating × range is its input resistance (20 kΩ/V on 10 V = 200 kΩ → reads 2/3 of a node with 100 kΩ source resistance); a DMM is ≈ 10 MΩ (−1 %) (script §B).
- **Average-responding meters assume a sine**: they scale the rectified mean by π/(2√2) = 1.1107, so a square wave reads **+11.1 %**, a triangle **−3.8 %**, an AC-coupled 10 %-duty pulse **−33 %**. True-RMS meters are right only within their **bandwidth** (e.g. 20 kHz for a Fluke 87V [5]) and **crest factor** limit (pulse train at duty D: CF = √((1−D)/D) → 3 at 10 %).
- **DMMs do not measure RF**: use a diode RF probe (peak-reading, square-law below ~0.1 V), an RF power meter or an SA. A DMM near a transmitter can show DC offsets from RF rectified in its input.
- **Scope probe compensation**: a 10× probe is a 9 MΩ/1 MΩ divider whose capacitors must have the same ratio; 10 % mis-compensation is a ≈ 9 % amplitude error for everything above ≈ 1.6 kHz (script §C) — adjust on the 1 kHz calibrator until the square wave is flat.
- **Dip meter**: an oscillator with a plug-in coil; a resonant circuit nearby absorbs power at its resonance and the oscillator's grid/gate/collector current dips. Couple loosely — at k = 0.1 the two coupled tanks split by 10 % and you read the wrong frequency (script §D). A NanoVNA with one or two small loops does the same job better ([bench recipe R11](bench-measurement-recipes.md#r11--resonance-and-q-with-coupled-loops-dip-meter-substitute)).

## Intuition (no math)
A **frequency counter** opens a gate for a known time and counts how many cycles go through it. Two things limit it: it cannot count a fraction of a cycle (so the last digit wobbles by one), and its idea of "one second" comes from its own crystal oscillator, which is wrong by some parts per million. A reciprocal counter turns the problem round: it counts its own fast clock during a whole number of input cycles, so the fraction-of-a-cycle problem shrinks to a fraction of a clock tick. Neither trick helps the time base: a counter is never more accurate than its reference.

A **meter** is a load. An old moving-coil meter draws real current from what it measures, and a high-impedance node sags when you touch it. A DMM draws far less. "Average-responding" meters measure the average of the rectified waveform and then multiply by the number that makes a sine read its RMS value; on any other waveform that number is wrong. "True RMS" meters compute the heating value, but only for waveforms whose energy lies inside their bandwidth and whose peaks fit inside their input range.

A **scope probe** is a voltage divider made of resistors (which set the ratio at low frequency) and capacitances (which set it at high frequency). If the two ratios differ, a square wave shows rounded or overshooting corners, and every sine above a few kHz is measured with the wrong amplitude. **Triggering** is how the scope decides when "time zero" is; for intermittent RF events (packets) you trigger on something that happens once per event, such as the transmit-enable line or the supply-current step.

A **dip meter** is an oscillator you can bring near a circuit. When the oscillator is tuned to the circuit's resonance, the circuit absorbs energy from it and the oscillator's current dips. It needs no connection — useful for traps, tank circuits and antenna elements — but its dial is approximate and coupling too tightly pulls the frequency.

## The math

### Level 1 — the working formulas
- **Direct counter**: f = N/T_gate; resolution ±1/T_gate (Hz); relative ±1/(f·T_gate) [1].
- **Prescaled direct counter** (÷N before the gate): resolution ±N/T_gate [1].
- **Reciprocal counter**: measures n input periods in time T ≈ n/f with clock resolution t_res; relative resolution ≈ t_res/T, independent of f [1], [2].
- **Time-base error**: Δf = f·(aging × time since calibration + temperature + calibration error) — a systematic error, not reduced by averaging [1], [3].
- **Trigger error** (period/reciprocal measurements): rms ≈ 1.4·√(x² + e_n²)/(dV/dt) per edge, x = counter input noise, e_n = signal noise, dV/dt = slew rate at the trigger point (2πfA for a sine of amplitude A) [1]; averaged over n periods it falls as 1/n.
- **Meter loading**: V_read = V_true·R_in/(R_in + R_s); analogue R_in = (Ω/V) × full-scale range.
- **Average-responding AC reading**: V_read = 1.1107·⟨|v|⟩; true RMS = √⟨v²⟩. Form factor FF = V_rms/⟨|v|⟩ (sine 1.1107, square 1, triangle 1.1547); error = 1.1107/FF − 1.
- **Crest factor** CF = V_peak/V_rms (sine √2, triangle √3, square 1; AC-coupled pulse of duty D: √((1−D)/D)).
- **Probe compensation**: divider R1 (tip) ∥ C1 into R2 ∥ C2 (scope + cable + trimmer); flat when R1C1 = R2C2; otherwise the high-frequency ratio C1/(C1+C2) differs from the DC ratio R2/(R1+R2), settling with τ = (R1∥R2)(C1 + C2).
- **Dip meter coupling**: reflected resistance into the dipper coil at resonance R_refl = k²ωL₁Q₂; two coupled resonators of equal f₀ show modes at f₀/√(1 ± k).

### Level 2 — derivations
**±1 count.** The gate opens at a random phase of the input. In T seconds, f·T cycles pass; the counter registers ⌊fT⌋ or ⌈fT⌉ depending on where the gate edges fall, so the result is ambiguous by one count: ±1/T in Hz. At 433.92 MHz in 1 s this is ±1 Hz (2.3 × 10⁻⁹) — negligible next to any non-disciplined time base. At 1 kHz it is ±1 Hz = 10⁻³, which is why direct counters are poor at audio frequencies [2].

**Prescaling.** If the input is divided by N first, only f/N cycles per second reach the gate, and the ±1 count now represents N input cycles: ±N/T. Keysight's AN 200 lists this as the price of a cheaper, slower gate: "poorer resolution by a factor of N" for the same measurement time [1].

**Reciprocal counting.** The counter waits for an input edge, opens the gate, counts its internal clock (period t_c) until the edge that ends n input periods, and computes f = n/(count·t_c). The ±1 count is now one *clock* period, so ΔT/T = t_c/T with T ≈ the gate time. A 100 MHz clock (10 ns) gives 10⁻⁸ in 1 s; analogue or digital interpolation of the start/stop edges brings the effective t_res to tens of ps, giving the "digits per second" specifications of modern counters (a 10-digits/s counter resolves 1 part in 10¹⁰ in 1 s) [2].

**Trigger error.** Noise e_n on a slope of dV/dt moves the instant at which the input comparator switches by e_n/(dV/dt). AN 200's expression adds the counter's own input noise and a factor ≈ 1.4 for the two edges [1]. A 10 MHz TCXO output of 1 V p-p (A = 0.5 V) with 1 mV noise has slew 3.1 × 10⁷ V/s at zero crossing → ≈ 45 ps per edge, negligible in a 1 s gate (4.5 × 10⁻¹¹). A 50 Hz, 1 V p-p sine with 10 mV of noise gives ≈ 89 µs per edge — 0.45 % of a single 20 ms period (script §A). Hence: measure low frequencies with period averaging and a low-pass/noise-reject input.

**Average-responding meters.** For v = A sin ωt, ⟨|v|⟩ = 2A/π and V_rms = A/√2, so the meter scales the mean by (A/√2)/(2A/π) = π/(2√2) = 1.1107. A square wave of amplitude A has ⟨|v|⟩ = V_rms = A, so it reads 1.1107A: +11.1 %. A triangle has ⟨|v|⟩ = A/2, V_rms = A/√3 → reading 0.5554A vs 0.5774A: −3.8 %. Numerically verified for these and for a 10 % duty pulse (script §B).

**Probe compensation.** The divider transfer function is H(s) = Z₂/(Z₁ + Z₂) with Z_i = R_i/(1 + sR_iC_i). If R₁C₁ = R₂C₂ the zeros and poles cancel and H = R₂/(R₁ + R₂) at all frequencies. Otherwise H(0) = R₂/(R₁ + R₂) and H(∞) = C₁/(C₁ + C₂), with a single pole at 1/[(R₁∥R₂)(C₁ + C₂)]. For R₁ = 9 MΩ, R₂ = 1 MΩ, C₂ ≈ 100 pF (scope 15 pF + cable + trimmer; illustrative), the correct C₁ = 11.1 pF and τ = 100 µs → a corner at 1.6 kHz. A ±10 % error in C₁ gives H(∞)/H(0) = 0.909 / 1.089 — a 9 % amplitude error on every signal above a few kHz, i.e. on everything RF-related (script §C). That is why the scope's calibrator is a ~1 kHz square wave: its edges show the HF ratio, its flat tops the DC ratio [4].

**Dip meter.** Model the dipper's coil L₁ and the circuit under test (L₂, Q₂) as coupled by mutual inductance M = k√(L₁L₂). At the circuit's resonance its loop impedance is R₂ = ωL₂/Q₂, and the dipper coil sees an added series resistance (ωM)²/R₂ = k²ωL₁Q₂. With L₁ = 1 µH at 14 MHz and Q₂ = 100: 0.9 Ω at k = 0.01, 88 Ω at k = 0.1 (script §D). That added loss reduces the oscillation amplitude, which shows as a dip in the rectified grid/gate current. When the two tanks are both resonant near f₀ and coupled by k, the system has two modes at f₀/√(1 ± k): at k = 0.1 they are 10 % apart, so the dip appears at a frequency that is not the DUT's. Critical coupling k_c = 1/√(Q₁Q₂) (0.014 for Q₁ = 50, Q₂ = 100) separates "one dip at f₀" from "split response"; work at k well below k_c, i.e. just close enough to see a dip.

### Level 3 — limits
- **Counters and modulated signals.** A counter measures the average zero-crossing rate over its gate. On a LoRa chirp it reports roughly the mean over the symbols captured — not the carrier error — and on a burst it may read garbage between packets. Use the radio's CW test mode, or measure the offset in an SDR/SA locked to a GPSDO ([LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)).
- **Counter sensitivity and input impedance.** RF inputs are 50 Ω and need tens of mV; a counter coupled by a loose loop to a transmitter can count a harmonic or a strong neighbour instead. Confirm with a spectrum display.
- **Allan deviation, not ppm.** For short-term stability (e.g. a TCXO under vibration) the relevant quantity is the Allan deviation at a given gate time; a single ppm figure hides it ([phase-noise measurement](phase-noise-measurement.md)).
- **True RMS above the bandwidth.** A switching-regulator ripple at 500 kHz on a 20 kHz-bandwidth meter is simply filtered out: the meter reads low, not "approximately". Use a scope with the 20 MHz limit for ripple.
- **Diode RF probes** (a Schottky diode, a series capacitor and a large resistor into a DMM) read close to the peak voltage minus a few tenths of a volt at levels of volts and follow a square law below ≈ 0.1 V ([detectors](../06-rf-circuits/detectors-and-power-meters.md)). Their input capacitance (≈ 1–2 pF) loads UHF nodes like a 10× probe; calibrate against a known level at the frequency of use.

## Design equations & rules of thumb
| Quantity | Relation | When valid | Typical values (script) |
|---|---|---|---|
| Direct-counter resolution | ±1/T_gate | any f | ±1 Hz in 1 s |
| Prescaled resolution | ±N/T_gate | direct + ÷N | ÷64: ±64 Hz in 1 s |
| Reciprocal resolution | ≈ t_res/T_gate (relative) | any f | 1 ns: 10⁻⁹ in 1 s |
| Time-base error | f × (aging·t + temp + cal) | always, systematic | 5 ppm → ±2.17 kHz at 433.92 MHz |
| Trigger error | 1.4√(x² + e_n²)/slew per edge | period / reciprocal | 10 MHz 1 Vpp: 45 ps |
| Analogue meter R_in | (Ω/V) × range | DC | 20 kΩ/V, 10 V: 200 kΩ |
| Average-responding error | 1.1107/FF − 1 | non-sine | square +11.1 %, triangle −3.8 % |
| Crest factor, pulse duty D | √((1−D)/D) (AC-coupled) | rectangular | D = 10 %: 3.0 |
| Probe compensation corner | 1/[2π(R₁∥R₂)(C₁+C₂)] | 10× passive | ≈ 1.6 kHz |
| Dip-meter pull | modes at f₀/√(1 ± k) | two resonant tanks | k = 0.1 → 10 % split |

## Worked examples
**Example 1 — how far off is my E22 at 433.125 MHz?** A hobby counter with a ±5 ppm crystal time base and a 1 s gate reads 433.126 2 MHz in the module's CW test mode. The ±1 count is ±1 Hz; the time base is ±2.17 kHz. All the counter can say is that the transmitter is within 1.2 ± 2.2 kHz of 433.125 MHz — no conclusion about a ±10 ppm (±4.3 kHz) module budget is possible until the counter is referenced to a GPSDO (then ±0.004 Hz from the reference plus ±1 Hz resolution) (script §A).

**Example 2 — the 1 kHz audio tone.** Measuring a 1 kHz tone with a direct counter in a 1 s gate gives "1000 Hz ± 1 Hz" (10⁻³). A reciprocal counter with 1 ns resolution gives ±1 µHz in the same second. With 10 mV of hum on a 1 V p-p tone, the per-edge trigger error is ≈ 4.5 µs (0.45 % of one period); averaging 1 000 periods reduces it to ≈ 4.5 ns.

**Example 3 — the sagging bias node.** A 5 V supply feeds a 200 kΩ/200 kΩ divider (2.5 V, Thévenin 100 kΩ) on an LNA bias line. A 20 kΩ/V analogue meter on its 10 V range (200 kΩ) reads 1.67 V; a DMM (10 MΩ) reads 2.48 V. Neither is "wrong": the analogue meter changed the circuit (script §B).

**Example 4 — square-wave PWM on a "cheap" meter.** A 3.3 V-p-p, 50 % duty square wave AC-coupled is ±1.65 V: true RMS 1.65 V. An average-responding meter shows 1.83 V (+11.1 %). A 10 % duty 3.3 V pulse train (AC-coupled RMS 0.99 V) reads 0.66 V on an average-responding meter (−33 %) and needs a meter with crest-factor capability ≥ 3.

**Example 5 — triggering on a LoRa packet.** To capture the PA supply current during an E22 transmission: trigger in **normal** (not auto) mode on the falling edge of the module's AUX pin (or on the MCU's TX-start GPIO) as an external/second channel, with the current probe on channel 1; set holdoff longer than the packet (e.g. 100 ms for a 71.9 ms SF7 packet) so that each packet triggers once; use single-shot to freeze the first packet after power-up. Triggering on the RF itself through a detector works too, but edge triggering on a noisy envelope needs hysteresis ("noise reject") or HF-reject coupling.

**Example 6 — finding a trap's resonance with a dip meter.** A 7 MHz coax trap is checked with a dip meter. Far away: no dip. Moving closer: a dip appears at 7.18 MHz; closer still the dip deepens and moves to 7.05 MHz — the pulling of §D. Back off to the point where the dip is just visible, read 7.17 MHz, and confirm the oscillator frequency with a counter or SDR rather than the dial (dial calibration is typically a few per cent). On a NanoVNA the same measurement takes two loops and gives Q as well ([R11](bench-measurement-recipes.md#r11--resonance-and-q-with-coupled-loops-dip-meter-substitute)).

## Practical notes
- **Reference everything to one 10 MHz.** Counter, SA, generator, VNA and SDR locked to a common GPSDO remove the time-base term from every comparison ([signal generators](signal-generators-and-sources.md)).
- **Count CW, not packets.** Use the transceiver's continuous-wave test mode; LoRa packets and chirps defeat counters.
- **Know the counter's input**: 50 Ω RF input with a prescaler (often > 100 MHz) vs 1 MΩ low-frequency input with trigger level, coupling and filter controls. Protect the RF input with a pad when counting a transmitter.
- **Meters**: use the DMM's low-Z mode only when you want to load ghost voltages away; use 10 MΩ for bias nodes; check the true-RMS bandwidth before trusting an AC reading of anything but mains.
- **Probe compensation** is per probe *and* per scope channel — re-do it whenever you move a probe.
- **Trigger modes**: auto (free-runs without a trigger — good for DC levels, bad for rare events), normal (waits), single (one capture). Holdoff, pulse-width, runt and sequence (A→B) triggers isolate one event in a burst.
- **Dip meters** are now rare and second-hand; a NanoVNA with a home-made loop, or a tinySA with its generator output, replaces them for most jobs.

## Common mistakes & misconceptions
- **"Nine digits means nine-digit accuracy."** The display shows resolution; accuracy is set by the time base [3]. A 5 ppm counter at 433 MHz is good to about ±2 kHz, whatever the display says.
- **Using a long gate to fix a time-base error.** Averaging reduces ±1 count and trigger error, never the time-base error [1].
- **Counting a LoRa transmitter in normal operation** and calling the result its frequency offset.
- **Measuring bias nodes with a low-Ω/V analogue meter** and "finding" a fault that the meter created.
- **Trusting an average-responding meter on PWM, triangle or noise** — it is calibrated only for sines.
- **Reading ripple at hundreds of kHz with a DMM** — its bandwidth is tens of kHz.
- **"My DMM reads 0.3 V on the antenna line, so there is RF."** That is a rectified artefact or a DC bias; measure RF with an RF instrument.
- **Skipping probe compensation** and attributing 9 % amplitude errors or "ringing" corners to the circuit.
- **Coupling a dip meter tightly to get a deep dip** — the frequency you read is then pulled several per cent.

## How to simulate / verify
- `python3 tools/verify/s10_bench_instruments.py` §A–D — counter resolution (direct, prescaled, reciprocal), time-base and trigger error; meter loading, average-responding errors and crest factors (numerical waveforms); probe compensation ratios and corner; dip-meter reflected resistance, mode splitting and critical coupling. ALL PASS.
- SPICE: build the 9 MΩ ∥ C₁ / 1 MΩ ∥ C₂ divider and drive it with a 1 kHz square wave while sweeping C₁ to see under/over-compensation ([SPICE](../16-simulation-tools/spice-circuit-simulation.md)).

## Open questions / gaps
- The 100 pF value for cable + scope + trimmer capacitance and the 1 ns reciprocal resolution are illustrative; check a specific probe and counter data sheet.
- Dip-meter dial accuracy ("a few per cent") is from general handbook practice, not a specific instrument specification.
- No Allan-deviation measurement of the team's TCXOs yet; see [phase-noise measurement](phase-noise-measurement.md) for methods.

## Sources
1. Keysight Technologies, *Fundamentals of the Electronic Counters*, Application Note 200, 5965-7660E — ±1 count, time-base, trigger and systematic errors; trigger error 1.4√(x² + e_n²)/slew; prescaler resolution penalty; period averaging; reciprocal counters. (app note; read via pdftotext)
2. Keysight Technologies, *10 Hints for Getting the Most from Your Frequency Counter* — direct vs reciprocal counters, resolution in digits per second, gate-time standardisation. https://assets.testequity.com/te1/Documents/pdf/10_hints_counter.pdf (app note; read via pdftotext)
3. Keysight N9020B MXA data sheet 5992-1255 — frequency-reference accuracy expressed as aging × time + temperature stability + calibration accuracy (an example of how time-base error is specified). (datasheet; read)
4. Tektronix, *ABCs of Probes* primer — passive-probe compensation and the calibrator square wave. (vendor primer; read for the probing page)
5. Fluke, *87V Industrial Multimeter* product page — true-RMS AC voltage bandwidth 20 kHz (3 dB at 1 kHz with the low-pass filter on). https://www.fluke.com/en-us/product/electrical-testing/digital-multimeters/fluke-87v (datasheet; WebFetch)
6. ARRL, *The ARRL Handbook* (current ed.) — dip meters, RF probes, station test equipment practice. (handbook; general, not re-read)
7. This repository: `tools/verify/s10_bench_instruments.py`. (verification)
