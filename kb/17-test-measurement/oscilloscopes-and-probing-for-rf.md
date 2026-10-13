---
title: Oscilloscopes and probing for RF — bandwidth and rise time, sample rate and ENOB, passive-probe loading, low-Z (Z0) and active probes, ground-lead ringing, near-field H/E probes, and the scope FFT
domain: 17-test-measurement
slug: oscilloscopes-and-probing-for-rf
tags: [oscilloscope, bandwidth, rise-time, sample-rate, enob, probe, passive-probe, probe-loading, z0-probe, low-impedance-probe, active-probe, ground-lead, ringing, spring-ground, near-field-probe, h-field, e-field, loop-probe, fft, emc-debug]
prerequisites: [../01-circuit-theory/transient-and-step-response.md, ../05-analog-electronics/data-converters-adc-dac.md, ../02-electromagnetics/near-field-far-field.md]
related: [basic-bench-instruments.md, spectrum-analyzers.md, rf-bring-up-debug-playbook.md, lab-setup-by-budget.md, ../13-pcb-rf-layout-emc/emc-emi-fundamentals.md, ../13-pcb-rf-layout-emc/grounding-and-return-paths.md, ../05-analog-electronics/power-supplies-for-rf-and-analog.md, ../14-sdr-dsp/fft-spectral-analysis-windows.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Oscilloscopes and probing for RF

## Questions this page answers
- What scope bandwidth do I need to see a 433 MHz or 915 MHz signal, or a fast edge?
- Why does my 10× probe make a 100 MHz signal disappear or ring?
- What is a Z0 (low-impedance, resistive-divider) probe and how do I build one?
- How long can the probe's ground lead be?
- How do I find which part of my board is radiating a spur (near-field probes)?
- Is a scope's FFT a substitute for a spectrum analyzer?
- How do I look at the LoRa module's supply current burst and PA ramp?

## TL;DR
- **Rise time × bandwidth ≈ 0.35** for Gaussian/1-pole responses (computed 0.340 and 0.350), **0.40–0.45** for flat, fast-roll-off scopes > 1 GHz (4th-order Butterworth 0.387, 8th 0.459, brick-wall 0.446) [1]. System rise ≈ √(t_scope² + t_probe²); the measuring system should be 3–5× faster than the edge (3× → 5 % error, 5× → 2 %).
- **Amplitude of a sine**: at f = 0.3·BW a Gaussian scope reads 3 % low, at 0.5·BW 8 %, at BW 29 %. A 915 MHz carrier needs ~3 GHz of bandwidth for 3 % amplitude — use a spectrum analyzer or power meter for RF levels; use the scope for time-domain behaviour.
- **A 10× passive probe is not "high impedance" at RF**: 10 MΩ ∥ 12 pF is 133 Ω at 100 MHz, 31 Ω at 433 MHz and 15 Ω at 915 MHz — on a 25 Ω node it drops the signal 0.15/2.2/6.0 dB.
- **Z0 probe** (450 Ω series into the scope's 50 Ω input = 10×; 950 Ω = 20×): ≈ 400–500 Ω nearly flat to GHz (0.4 dB loading of a 25 Ω node) — the cheapest good RF probe you can make.
- **Ground leads ring**: the Tektronix example (11 pF probe, 6-inch lead) rings at ~140 MHz [1] → ≈ 0.77 nH/mm; shorten to a 5 mm spring/barrel ground → ~770 MHz, Q < 1.
- **Near-field H-loop**: V = ωμ₀HA — a 10 mm loop gives 96 dBµV for 1 A/m at 100 MHz, rising 6 dB/octave until the loop inductance and 50 Ω load flatten it (~400 MHz for 10 mm). Pair with an SA to locate spur sources.
- **Scope FFT**: with ENOB ≈ 7 the full-scale SNR is ≈ 44 dB, raised per bin by the FFT's processing gain (1 M points → +57 dB), but spurs (interleaving, clock) typically limit SFDR to 40–50 dBc: good for "where is the 48 MHz clock leaking", not for −60 dBc harmonic compliance.

## Intuition (no math)
An oscilloscope is a wideband voltmeter drawing voltage against time. At RF its two enemies are bandwidth (it smooths everything faster than its rise time) and the probe (which changes the circuit it touches). A probe is a small capacitor to ground plus a loop of wire: the capacitor loads high-impedance nodes, and the wire loop's inductance forms a resonant circuit with it that rings when an edge hits it. At 433–915 MHz, a standard 10× probe is closer to a short circuit than to an open.

The fix is to change the probe, not the scope: a low-value resistor straight into a 50 Ω scope input (the Z0 probe) looks like a few hundred ohms with almost no capacitance, and a spring ground a few millimetres long replaces the 15 cm alligator lead. For finding *where* RF is coming from rather than measuring it, you don't touch the circuit at all: a small loop of coax sniffs the magnetic field of currents in traces, a short stub sniffs the electric field of nodes.

## The math

### Level 1 — bandwidth, rise time, loading
- **Rise time**: t_r ≈ k/BW, k ≈ 0.35 (Gaussian/1-pole), 0.40–0.45 (flat fast scopes) [1]. Cascade: t_sys² ≈ t_scope² + t_probe² (+ t_source²).
- **Sinusoidal amplitude error** (Gaussian): |H| = exp(−(ln 2/2)(f/BW)²): −0.12 dB at 0.2 BW, −0.27 dB at 0.3 BW, −0.75 dB at 0.5 BW, −3.01 dB at BW.
- **Probe loading**: Z_probe = R_p ∥ 1/(jωC_p). A node with Thévenin impedance Z_s is attenuated by Z_probe/(Z_s + Z_probe).
- **Ground-lead resonance**: f_r = 1/(2π√(L_g C_p)); Q ≈ √(L_g/C_p)/R_source.
- **ADC**: SNR_ideal = 6.02·ENOB + 1.76 dB; FFT processing gain 10 log(N/2) (real samples; 10 log N for a complex FFT); bin ENBW = w·f_s/N (w = 1, 1.5, 3.77 for rectangular, Hann, flat-top).
- **H-loop probe**: Faraday, V_oc = ωμ₀HA (A = loop area, H uniform over it).

### Level 2 — where the constants come from
**Gaussian rise time.** |H(f)| = exp(−(ln2/2)(f/B)²) is the Fourier transform of a Gaussian impulse response with σ_t = √(ln 2)/(2πB). The step response is an error function whose 10 %–90 % points are ±1.2816σ_t apart: t_r = 2.563σ_t = 0.340/B. For a single pole, the step 1 − e^{−t/τ} gives t_r = τ ln 9 = ln 9/(2πB) = 0.350/B. Scopes are designed with near-Gaussian roll-off to avoid overshoot; above ~1 GHz they use flatter "maximally flat" responses with less phase linearity: our analog Butterworth step responses give 0.342 (2nd order), 0.387 (4th), 0.459 (8th), and an ideal brick-wall 0.446 — consistent with the 0.40–0.45 range [1]. The flatter responses also overshoot and ring on edges — a "ringing" edge on a fast scope is partly the scope.

**Why a 10× probe fails at RF.** The 9 MΩ tip resistor is shunted by a compensation capacitor so that the divider ratio is 10 at all frequencies; the input looks like ≈ 10 MΩ ∥ 8–12 pF (Tektronix P6139B 8 pF, TPP1000 12 pF [1]). At 915 MHz, 12 pF is 14.5 Ω: probing the 50 Ω antenna feed of a LoRa module loads it as badly as a 15 Ω resistor to ground and detunes any matching network.

**Z0 probe.** A resistor R_t in series with a 50 Ω scope input (or a 50 Ω cable terminated in 50 Ω) forms a divider (R_t + 50)/50: 450 Ω → 10×, 950 Ω → 20×. The input is R_t + 50 in parallel with the tiny capacitance of a single SMD resistor (~0.1–0.3 pF). Script: with 0.2 pF, the 450 + 50 Ω probe presents |Z| = 499/433/276 Ω at 0.1/0.915/2.4 GHz, loading a 25 Ω node by only 0.42–0.45 dB — nearly frequency independent, so it can be calibrated out. Costs: it loads DC (500 Ω to ground — AC-couple with a capacitor if the node has bias) and reduces sensitivity.

**Ground-lead ringing.** Tektronix states that an 11 pF probe with a 6-inch ground lead rings at about 140 MHz [1]; solving f = 1/(2π√(LC)) gives L ≈ 117 nH, i.e. ≈ 0.77 nH per mm of lead (loop). Scaling (script §4): 76 mm → 198 MHz; 25 mm → 346 MHz; 5 mm spring → 773 MHz and heavily damped (Q ≈ 0.7 from a 25 Ω source). A 1 pF active probe with the same 6-inch lead rings at 465 MHz with Q ≈ 14 — worse, because low C raises √(L/C).

### Level 3 — scope FFT and near-field probing
**Scope FFT dynamic range.** An 8-bit scope with ENOB ≈ 7 has ≈ 44 dB full-scale SNR; spreading the noise over N/2 bins lowers the per-bin floor by 10 log(N/2) (57 dB for 10⁶ points → −101 dBFS per bin). Dynamic range is therefore set by *spurs* — ADC interleaving spurs, clock feedthrough, non-linearity (typically 40–50 dBc for 8-bit scopes; high-resolution 10–12-bit scopes do better) — not by noise. At 5 GS/s and 10⁶ points the bin spacing is 5 kHz (Hann ENBW 7.5 kHz) — a usable "RBW" for looking at LoRa channels, but record-length limited and with no preselection: strong out-of-band signals alias if the scope's analog BW exceeds f_s/2.

**Near-field H-loop.** A shielded loop (semi-rigid coax bent into a circle with a gap in the shield at the top; the centre conductor soldered to the shield at the other end) responds to the magnetic field of *currents*, rejecting the electric field thanks to the shield. Open-circuit voltage V = ωμ₀HA: a 10 mm loop gives 75.8/95.8/108.6/115.1/123.5 dBµV per A/m at 10/100/433/915/2400 MHz (script §6). Its inductance (≈ 19 nH for 10 mm, 0.5 mm wire) into a 50 Ω load forms a high-pass corner at R/(2πL) ≈ 410 MHz above which the output flattens, and stray capacitance self-resonates the loop near ~1 GHz — use 3–5 mm loops for GHz work and treat readings as *relative*. A trace carrying 10 mA at 1 cm distance produces H = I/(2πr) ≈ 0.16 A/m. The **E-field probe** is a short stub (a few mm of centre conductor protruding from coax) that responds to node voltages (dV/dt). Near-field theory: [near field vs far field](../02-electromagnetics/near-field-far-field.md); EMC use: [EMC fundamentals](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md).

## Design equations & rules of thumb

| Item | Rule / value | Notes |
|---|---|---|
| Rise time | t_r ≈ 0.35/BW (≤ 1 GHz scopes), 0.40–0.45/BW (fast flat scopes) [1] | 100 MHz → 3.5 ns |
| Measuring an edge | system 3–5× faster than the edge [1] | 3× → 5 %, 5× → 2 % error |
| Sine amplitude | f ≤ 0.3 BW for ≤ 3 % error | Gaussian |
| 10× passive probe | 10 MΩ ∥ 8–12 pF [1] | 133 Ω at 100 MHz, 15 Ω at 915 MHz |
| Ground lead | ≈ 0.77 nH/mm (from Tek example) | 15 cm → ~140 MHz ring with 11 pF |
| Z0 probe | R_t = 450 Ω (10×) or 950 Ω (20×) into 50 Ω | AC-couple on biased nodes |
| Sample rate | ≥ 2.5 × BW for real-time; ≥ 5 × BW to see edges well | anti-alias depends on scope |
| ADC SNR | 6.02 ENOB + 1.76 dB | 8-bit scope ENOB ~6–7 |
| FFT bin | ENBW = w·f_s/N | w = 1.5 Hann |
| H-loop | V = ωμ₀HA | 6 dB/oct until R/(2πL) |

## Worked examples

**Example 1 — what can a 100 MHz scope show about a 433 MHz LoRa board?** Not the carrier: a Gaussian 100 MHz response is ≈ 56 dB down at 433 MHz (−3.01 dB × (433/100)²), and it aliases if f_s < 866 MS/s. It *can* show: the supply current burst when the PA turns on (via a current probe or a 0.1 Ω shunt), the PA ramp/TX-enable timing, the SPI traffic, the TCXO at 32 MHz (0.32·BW → ≈ 3 % low), and the envelope of the RF if you add a diode detector (e.g. a Schottky + RC, or the AD8318's 10 ns-response output from [RF power measurement](rf-power-measurement.md)). This is how you measure LoRa time-on-air and duty cycle.

**Example 2 — the "ringing" 3.3 V rail.** A 1 GHz-bandwidth scope with the standard 15 cm ground clip shows 200 mV of ~140 MHz ringing on every MCU clock edge. Replace the clip with the probe's spring ground (5 mm) at a decoupling capacitor: the ringing disappears (the resonance moved to ~770 MHz and is damped) — it was the probe. What remains is real supply noise.

**Example 3 — build a Z0 probe for the LoRa module's RF output (915 MHz).** Solder a 0402 470 Ω (close to 450 Ω; the ratio becomes (470 + 50)/50 = 10.4×) at the end of a short semi-rigid or RG-316 pigtail, the shield to the nearest ground via with a 1–2 mm strap, and connect to a 50 Ω scope input (or SA). Input ≈ 520 Ω ∥ ~0.2 pF: probing a 50 Ω line mid-way (Thévenin 25 Ω) drops the signal ≈ 0.4 dB — calibrate by probing a known 50 Ω line fed from a generator. With a series 100 pF DC block it is also safe on biased nodes (PA drain/LNA output).

**Example 4 — hunting a 48 MHz-harmonic spur desensing 433 MHz.** Your LoRa ground station hears a spur at 432.0 MHz (9 × 48 MHz). With a 10 mm H-loop into a tinySA (RBW 10 kHz, span 1 MHz around 432 MHz) scan the board: the reading peaks (say 30 dB above elsewhere) over the USB-to-UART bridge crystal traces. Orient the loop perpendicular to the trace to maximise coupling (the field circles the current). Fix: move/shield the clock, spread-spectrum or change the frequency, filter the traces ([mixed-signal layout](../13-pcb-rf-layout-emc/mixed-signal-layout.md)).

**Example 5 — using the scope FFT for a sanity check.** 5 GS/s, 10⁶ points on an 8-bit scope looking at a 50 Ω test port: Hann ENBW 7.5 kHz; the noise floor per bin is ≈ −100 dBFS but spurs at −45 dBc appear from interleaving. A harmonic reading of −50 dBc is therefore indistinguishable from the scope's own spurs — use a spectrum analyzer for harmonic levels.

## Practical notes
- **Scope choice** for a student RF team: 100–200 MHz, 4-channel, 1 GS/s scopes (Rigol DHO800/DHO900, Siglent SDS1000X-E/SDS800X HD class) cover firmware/power/timing debug; RF carriers are the SA's job. A 12-bit "HD" scope is better for power-rail noise and FFTs. See [lab setup](lab-setup-by-budget.md).
- **Use the 50 Ω input** (if the scope has one) with Z0 probes and coax; the 1 MΩ input's capacitance and the cable's reflection make it poor above ~50 MHz.
- **Current probing**: a current probe or a low-inductance shunt (e.g. 0.1 Ω 1206 with Kelvin sense and a coax pigtail) to see the 100–700 mA LoRa PA bursts; beware the shunt's inductance (1 nH at 10 MHz = 0.06 Ω).
- **Bandwidth limit** (20 MHz) button is your friend for power-rail ripple; turn it off for edges.
- **Probe compensation and triggering** (compensating a 10× probe on the 1 kHz calibrator, holdoff and external triggering on a LoRa packet) are covered in [basic bench instruments](basic-bench-instruments.md); a 10 % mis-compensated probe reads every signal above ≈ 1.6 kHz 9 % wrong.
- **Differential/active probes** (FET-input, ≤ 1 pF) are the right tool for high-impedance nodes and fast logic, but expensive and ESD-fragile.
- **Near-field probe kits** (commercial sets of H-loops and E-stubs ~US$20–100, or DIY from semi-rigid coax) with an SA are the most valuable EMC-debug tool per dollar; a preamp (20–30 dB) helps with weak fields.
- **Safety**: scope grounds are earth-referenced — never clip the ground lead to a floating high-voltage node or a mains-referenced circuit.

## Common mistakes & misconceptions
- **Measuring RF power with a scope** — bandwidth roll-off, probe loading and 8-bit accuracy make ±1–3 dB errors routine.
- **Blaming the circuit for ringing** caused by a 15 cm ground clip.
- **Probing an antenna feed with a 10× probe** — 15 Ω at 915 MHz shunts and detunes it.
- **"1 GS/s is enough for 433 MHz"** — only as an alias; the scope must have ≥ 433 MHz *analog* bandwidth and ≥ 2.5× sample rate to show it properly.
- **Reading dBm off a scope FFT without accounting for the 1 MΩ input, probe attenuation and window** (a 1 MΩ input doesn't define power at all).
- **Trusting absolute near-field probe readings** — they are relative and orientation-dependent.

## How to simulate / verify
- `python3 tools/verify/meas_scope_probe.py` — (1) rise-time × BW for Gaussian, 1-pole, Butterworth 2/4/8 and brick-wall; cascade error; (2) sine amplitude error vs f/BW; (3) passive and Z0 probe loading vs frequency; (4) ground-lead L from the Tek example and ringing vs length; (5) ADC ENOB, FFT processing gain and ENBW; (6) H-loop sensitivity and self-resonance.
- SPICE: model a probe as R_p ∥ C_p with a series L_g (0.77 nH/mm) and drive it with a 1 ns edge from 25 Ω to reproduce the ringing ([SPICE simulation](../16-simulation-tools/spice-circuit-simulation.md)).

## Open questions / gaps
- Typical SFDR of specific budget scopes (Rigol DHO/Siglent SDS) FFTs was not verified; the 40–50 dBc figure is a general 8-bit estimate.
- The ground-lead nH/mm value is derived from one Tektronix example; loop geometry changes it (± factor ~2).
- Near-field probe calibration (antenna factor in dB(A/m)/V) requires a TEM cell or a microstrip reference; not covered.

## Sources
1. Tektronix, *ABCs of Probes* primer (02_ABCs-of-Probes-Primer, download.tek.com) — t_r ≈ 0.35/BW (Gaussian; 0.40–0.45 for > 1 GHz scopes), 3–5× rise-time rule (3:1 → 5 %, 5:1 → 2 %), probe capacitance table (P6139B 8 pF, TPP1000 12 pF, P6243 ≤ 1 pF), 500 Ω 10× probes for 50 Ω inputs, 11 pF + 6-inch lead rings at ~140 MHz. (vendor primer; read)
2. H. Johnson and M. Graham, *High-Speed Digital Design: A Handbook of Black Magic*, Prentice Hall, 1993 — probing, ground loops, low-Z probe construction. (textbook; cited)
3. H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley, 2009 — near-field probes and EMC troubleshooting. (textbook; cited)
4. Keysight/Agilent AN 1287-12 (time-domain) and oscilloscope fundamentals material — ENOB/SNR relation (standard ADC theory; see [data converters](../05-analog-electronics/data-converters-adc-dac.md)). (app note / theory; cited)
5. This repository: `tools/verify/meas_scope_probe.py`. (verification)
