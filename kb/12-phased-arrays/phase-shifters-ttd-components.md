---
title: Phase shifters, true-time-delay units and beamformer ICs — switched-line, loaded-line, reflection-type, vector modulator, TTD, T/R modules, cost per element
domain: 12-phased-arrays
slug: phase-shifters-ttd-components
tags: [phase-shifter, switched-line, loaded-line, reflection-type-phase-shifter, high-pass-low-pass, vector-modulator, varactor, true-time-delay, TTD, beamformer-IC, ADAR1000, ADTR1107, ADAR4002, HMC642A, HMC649A, PE44820, QPC2108, AWMF-0108, JSPHS, T/R-module, VGA, step-attenuator, calibration-registers, cost-per-element]
prerequisites: [beam-steering-grating-lobes.md, beamforming-architectures.md, ../03-transmission-lines-matching/input-impedance-stubs-quarter-wave.md, ../06-rf-circuits/couplers-dividers-combiners.md]
related: [array-calibration.md, tapering-sidelobe-control.md, diy-phased-array-projects.md, ../05-analog-electronics/diodes-schottky-pin-varactor.md, ../06-rf-circuits/rf-switches-attenuators-limiters.md, ../06-rf-circuits/lna-design.md, ../06-rf-circuits/power-amplifiers.md, ../02-electromagnetics/magnetic-materials-permeability.md, ../18-components-parts/rf-switches-attenuator-parts.md, ../18-components-parts/sourcing-and-eval-boards.md]
level: mixed
confidence: medium
last_updated: 2026-09-29
---

# Phase shifters, TTD units and beamformer ICs

## Questions this page answers
- How does a phase shifter actually shift phase — what's inside?
- What's the difference between a switched-line, loaded-line, reflection-type and vector-modulator phase shifter?
- Is a switched-line phase shifter a phase shifter or a time delay?
- Can I build my own phase shifter at 2.4 or 5.8 GHz from switches, varactors or a hybrid coupler?
- What does a beamformer IC like the ADAR1000 contain, and what are its real specs?
- How much loss and noise does a phase shifter add, and where must the LNA go?
- How many bits and how much delay range do I need for a true-time-delay (TTD) unit?
- What's in a T/R module?
- Why does a phase shifter's gain change with its phase setting (and vice versa)?
- What does a phased-array channel cost at hobby/student scale?
- Which parts exist for 433 MHz, 915 MHz, 2.4 GHz, 5.8 GHz and 10 GHz?

## TL;DR
- **Four circuit families**: (1) **switched-line** — switch between two line lengths; phase ∝ frequency, so it is really a **TTD bit**; (2) **loaded-line** — a pair of switched shunt susceptances ±jB a quarter-wave apart; matched when Z_c = Z₀/√(1+b²) and gives Δφ = 2 arctan b (verified exactly); good for small bits (≤ 45°); (3) **reflection-type (RTPS)** — a 90° hybrid with two identical variable reactive loads, S₂₁ = −jΓ_L; a 5:1 varactor gives only ≈ 83° at 2.44 GHz, ≈ 176° with a resonating series L, ≈ 250–290° with an impedance-transformed load; (4) **vector modulator** — split into I and Q, weight each, sum: any phase *and* amplitude; accuracy set by DACs and I/Q imbalance (0.5 dB / 3° imbalance → ±2.2° phase error before calibration). MMIC digital phase shifters mostly use switched **high-pass/low-pass** filter bits (a relative of loaded-line) for broadband ≈ constant phase steps.
- **ADAR1000** (8–16 GHz, 4 channels, half-duplex) from its data sheet: 360° with 2.8° steps (RMS phase error 2°), ≥ 31 dB gain range in ≤ 0.5 dB steps (RMS gain error 0.2 dB), Rx channel gain 10 dB with **NF 8 dB** and IIP3 −7 dBm, Tx gain 21 dB with OP1dB 10 dBm/Psat 14 dBm, 121 stored beam states, 20 ns beam switching; ≈0.9 W (Rx) per 4 channels [1]. It *needs* a front end: **ADTR1107** (6–18 GHz PA + LNA + switch: Rx gain 18 dB, NF 2.5 dB; Tx Psat 25 dBm) [2] — the pair gives a channel NF ≈ 2.7 dB instead of 8.3 dB (script §7).
- Discrete digital phase shifters (6-bit, 5.625° LSB): HMC647A 2.5–3.1 GHz (rms 1.5°), QPC2108 2.5–4 GHz (rms < 2.8°, ≈ US$170 each at 1–24 pcs), HMC649A 3–6 GHz (rms 4°), HMC642A 9–12.5 GHz (rms 4.5°, IL 7–10 dB); PE44820 8-bit 1.7–2.2 GHz (1.4° steps) [3–6]. Analog: Mini-Circuits JSPHS-2484+ (2.15–2.484 GHz, 180° min, 2 dB IL, 0–15 V, strongly nonlinear: slope varies 5× across the range) [7]; ADL5390 vector multiplier 20 MHz–2.4 GHz [8].
- **TTD**: needed delay span (N−1)d sinθ_max/c — 523 ps for 8 × λ/2 at 5.8 GHz and ±60°; bits = log₂(span/LSB); a 4 ps LSB leaves 2.4° rms phase error at 5.9 GHz. ADAR4002: 0.5–19 GHz, 7-bit, 508 ps/4 ps or 254 ps/2 ps ranges [9].
- **Phase and gain are never independent**: attenuator states shift phase, phase states change insertion loss (±0.4–0.5 dB typical) — calibrate a 2-D table, not two 1-D ones.
- **LNA first**: a 6 dB phase shifter before the LNA gives a 7 dB channel NF; after a 30 dB LNA, 1.1 dB (script §7).
- **Student-scale reality** (2026): a 4–8 channel array via phase-shifter ICs costs roughly US$100–300 per channel in parts at 2–6 GHz; the ADI Phaser (8 ch, 10 GHz, complete) ≈ US$2,900; coherent SDR channels (KrakenSDR ≈ US$750 for 5 channels in 2026, ≤ 1.77 GHz — [SDR survey](../14-sdr-dsp/sdr-hardware-survey.md); it launched at US$299 in 2021–22) are the cheapest way to *digital* phase control below 1.8 GHz.

## Intuition (no math)

**Four ways to delay a wave.** (1) Make it travel further: switch in an extra length of line (switched line). (2) Slow it down a bit: hang small capacitors (or inductors) on the line so it looks electrically longer or shorter (loaded line; high-pass/low-pass bits). (3) Bounce it: send it into a coupler whose two "mirror" ports are terminated by adjustable reactances; the reflected wave comes out of the fourth port with a phase set by those reactances (reflection type). (4) Build it from two orthogonal pieces: any phasor is a·cos + b·sin; split the signal into a 0° and a 90° copy, scale each by a signed number, add (vector modulator) — exactly what an I/Q modulator does.

**Phase vs delay.** Switched-line bits give a *delay*: their phase grows with frequency. That is perfect for wideband steering (no squint) but means a "90° bit" is only 90° at one frequency. Loaded-line, high-pass/low-pass and vector modulators give an approximately *constant phase* over a band — which is what a narrowband phase shifter is supposed to do, and what causes beam squint in wideband use ([beam steering](beam-steering-grating-lobes.md)).

**Everything leaks into everything.** Switches have loss that differs slightly per state; a VGA changes its phase as its gain changes; temperature moves both. So a real beamformer channel is a 2-D map from (phase code, gain code) to a complex gain. That's why data sheets quote *RMS phase error* and *RMS gain error* over all states, and why calibration tables exist ([calibration](array-calibration.md)).

**Where the loss goes matters.** A phase shifter is a lossy passive block (4–10 dB for 6-bit MMICs). On receive, loss before the first amplifier adds dB-for-dB to the noise figure. On transmit, loss after the last PA is wasted output power. T/R modules put the LNA and PA right at the antenna for exactly this reason.

## The math

### Level 1 — the four circuits

| Type | Principle | Phase vs f | Typical use | Watch out for |
|---|---|---|---|---|
| Switched-line | Δφ = βΔL = 2πf ΔL√ε_eff/c | ∝ f (TTD) | large bits (180°), TTD bits | switch isolation → resonances when off-line ≈ λ/2 |
| Loaded-line | ±jB pair, λ/4 apart: Δφ = 2 arctan(bZ₀·…) | ≈ flat | small bits (11.25–45°) | bandwidth ≈ ±10% for 45° |
| High-pass/low-pass (switched filter) | toggle between HP and LP T/π networks with ±φ/2 | ≈ flat over octave | MMIC digital phase shifters | loss per bit |
| Reflection-type | 90° hybrid + two loads: S₂₁ = −jΓ_L | depends on load | analog (varactor) and digital | range limited by C ratio; hybrid bandwidth |
| Vector modulator | I/Q split, bipolar VGAs, sum | ≈ flat | continuous phase + amplitude | I/Q imbalance, noise of active VGAs |
| Ferrite (latching) | gyromagnetic phase shift | ≈ flat | high-power radar | size, cost, drive energy |
| MEMS / liquid crystal | switched lines/varactors; tunable ε | depends | mmWave, satcom panels | speed, reliability, temperature |

### Level 2 — derivations

**(a) Switched-line bit.** Two paths differing in length ΔL on a line with effective permittivity ε_eff: Δφ(f) = 2πf ΔL√ε_eff/c = 2πf·τ with τ = ΔL√ε_eff/c. Because Δφ ∝ f it is a TTD bit. Used as a "phase" bit, it has error Δφ₀·(f/f₀ − 1): a 180° bit on FR-4-class microstrip (ε_eff 3.3) at 5.8 GHz is 14.23 mm and errs ±9° at ±5% (script §1). The two SPDT switches' isolation matters: the "off" path is a stub that resonates when its length approaches λ/2, putting a notch in the "on" path — keep off-path lengths short or use SP3T/terminated designs.

**(b) Loaded-line bit (derivation).** Shunt susceptance jB, a line of characteristic impedance Z_c and electrical length θ = 90°, then jB again. ABCD: M = [[1, 0],[jB, 1]]·[[0, jZ_c],[j/Z_c, 0]]·[[1, 0],[jB, 1]]. Multiplying out: A = D = −BZ_c, B_ABCD = jZ_c, C = j(1/Z_c − B²Z_c). The match condition S₁₁ = 0 for a symmetric network is B_ABCD/Z₀ = C·Z₀, i.e. Z_c/Z₀ = Z₀(1/Z_c − B²Z_c), giving **Z_c = Z₀/√(1 + b²)** with b = BZ₀. Then, using the match condition B_ABCD/Z₀ = CZ₀, S₂₁ = 2/(A + B_ABCD/Z₀ + CZ₀ + D) = 2/(−2BZ_c + 2jZ_c/Z₀) = √(1+b²)/(j − b): unit magnitude, phase −90° − arctan b. The opposite state (−B) gives −90° + arctan b, so **Δφ = 2 arctan b**, i.e. **b = tan(Δφ/2)**. Script §2 confirms numerically for 11.25°, 22.5° and 45° bits (|S₁₁| < 1e−15 at centre, Δφ exact). Frequency behaviour: with a capacitor (B ∝ f) for +B and an inductor (B ∝ −1/f) for −B, a 45° bit holds 45.1–45.6° and return loss > 20 dB over ±10% — much flatter than switched line.

**(c) Reflection-type phase shifter.** An ideal 3-dB 90° hybrid with identical loads Z_L on its through and coupled ports sends the reflected waves to the isolated port with S₂₁ = −jΓ_L and nothing back to the input (so the input stays matched whatever the loads — the key advantage). With Γ_L = (Z_L − Z₀)/(Z_L + Z₀) and a purely reactive load jX, |Γ_L| = 1 and arg Γ_L = π − 2 arctan(X/Z₀): the phase range is set by how far X can swing *relative to Z₀*. Script §3 with a 0.5–2.5 pF (5:1) varactor: 82.9° at 2.44 GHz and 70.6° at 5.8 GHz for the bare varactor; resonating it with a series L (3.81 nH at 2.44 GHz) sweeps X through zero and raises the range to 176°; referencing the loads to 25 or 15 Ω through an impedance transformer extends it to 246° / 287° (2.44 GHz). Two cascaded RTPS stages give 360°. The varactor's series resistance makes |Γ_L| < 1 and state-dependent — the insertion-loss variation of analog phase shifters.

**(d) Vector modulator.** Output = (w_I + jw_Q)·x after a quadrature split, so phase = atan2(w_Q, w_I) and amplitude = |w|. With n-bit DACs spanning ±1, rounding w_I, w_Q gives max phase errors 1.15° / 0.29° / 0.07° and amplitude ripple ±0.18 / ±0.05 / ±0.01 dB for 6 / 8 / 10 bits (script §4) — already better than most switched designs. The dominant errors are analog: a Q-path gain error ε and quadrature error δ produce a phase error that varies with the set angle (0.2 dB / 1° → ±0.8°; 0.5 dB / 3° → ±2.2°; 1 dB / 5° → ±4.1°, plus 0.25–1.3 dB amplitude ripple). For small errors the phase error is (ε/2)sin2φ + (δ/2)(1 − cos2φ), whose peak deviation about its mean is ½√(ε² + δ²) (2.26° predicted vs 2.23° computed for 0.5 dB/3°). They are systematic, so a 2-D calibration table removes them. Active VGAs add noise and have finite linearity, so vector modulators sit after the LNA.

**(e) Digital phase-shifter bits and errors.** A P-bit shifter cascades bits of 180°, 90°, …, 360°/2^P. Each bit contributes a phase and a loss error that depends on the *other* bits' states (mismatch interaction), so the 2^P states have an RMS phase error (HMC647A 1.5°, QPC2108 < 2.8°, HMC649A 4°, HMC642A 4.5°) and an insertion-loss variation (±0.4–0.5 dB) [3–6]. For array performance these errors behave like the random errors of [tapering](tapering-sidelobe-control.md) §(f): with 4° rms and 0.4 dB, a 16-element array's error floor is ≈ (0.046² + 0.070²)/16 → −25 dB; calibrate per state if you need better.

**(f) TTD sizing.** Delay span T = (N − 1)d sinθ_max/c; with LSB τ_q the number of bits is ⌈log₂(T/τ_q + 1)⌉ and the rounding error is a uniform delay error with rms τ_q/√12, i.e. a phase error 360°·f·τ_q/√12 at frequency f. Script §6: 8 × 25.84 mm at ±60° → 523 ps; 4 ps LSB → 8 bits, 2.4° rms at 5.875 GHz; 32 × 15 mm at ±45° → 1.1 ns, 9–10 bits. ADAR4002's 7-bit, 508 ps/4 ps range covers the 8-element 5.8 GHz case only up to ±54° (508 ps < 523 ps) [9] — or use it per subarray with phase shifters inside ([architectures](beamforming-architectures.md)).

**(g) Chain noise figure (receive).** Friis, element chain LNA → phase shifter → combiner → receiver ([noise figure](../07-noise-linearity/noise-figure-and-friis.md)). 2.4 GHz with a 6 dB-loss phase shifter and an 8 dB-NF SDR: LNA 15 dB → NF 3.3 dB; LNA 30 dB → 1.1 dB; phase shifter first → 7.0 dB (script §7). X band: ADAR1000 alone → 8.3 dB; ADTR1107 LNA (18 dB, 2.5 dB NF) in front → 2.7 dB. Note that a lossless N-way combiner does not add noise for the *coherent* array output but its excess loss does.

### Level 3 — beyond the basics

- **Bidirectional vs separate Tx/Rx paths**: ADAR1000 has separate Tx and Rx channels (different gain/NF) sharing one phase-control word per mode; the T/R switch time (180 ns) sets radar blind range; beam-state RAM (121 states) lets an FPGA step beams in 20 ns without SPI traffic [1].
- **T/R module anatomy** (per element): antenna port → circulator or T/R switch → (Rx) limiter → LNA → … ; (Tx) … → driver → PA → harmonic filter; plus a shared phase shifter/attenuator ("common leg"), control logic, bias sequencing (GaAs/GaN negative gate bias first — the ADAR1000 generates PA/LNA gate-bias DACs for this [1]) and power detection. GaN PAs at 5–10 W per element dominate modern radar; silicon beamformer ICs (SiGe BiCMOS or CMOS) dominate satcom/5G panels (e.g. AWMF-0108: 26.5–29.5 GHz, 4 channels, 5-bit phase and gain, Rx coherent gain 28 dB, NF 5 dB, Tx +9 dBm [10]).
- **Wideband phase shifting** without TTD: all-pass-network ("Schiffman" coupled-line) phase shifters give nearly constant differential phase over an octave.
- **Temperature**: beamformer gain drifts ±2.5–3 dB over −40…+85 °C (ADAR1000 data sheet [1]); phase drifts too — use the on-chip temperature sensor to index calibration tables.
- **Linearity in receive arrays**: each element sees full-strength interferers before any spatial filtering; ADAR1000's Rx IP1dB −16 dBm (+18 dB LNA in front → −34 dBm at the antenna) sets how close a strong emitter may be.

## Design equations & rules of thumb

| Rule | Validity | Value |
|---|---|---|
| Switched line: τ = ΔL√ε_eff/c; Δφ = 2πfτ | TTD bit | 5.8 GHz 180° bit on ε_eff 3.3: 14.2 mm |
| Loaded line: b = tan(Δφ/2), Z_c = Z₀/√(1+b²) | λ/4 spacing | 45° bit: b = 0.414, Z_c = 46.2 Ω |
| RTPS: S₂₁ = −jΓ_L; range = Δarg Γ_L | ideal hybrid | 5:1 varactor: 83° bare, 176° resonated (2.44 GHz) |
| Vector modulator: peak phase error ≈ ½√(ε² + δ²) (ε fractional Q-gain error, δ quadrature error in rad) | small, systematic I/Q imbalance | 0.5 dB/3° → ±2.2° (formula 2.26°) |
| TTD bits = ⌈log₂(T/τ_q + 1)⌉, φ_rms = 360 f τ_q/√12 | TTD | 523 ps, 4 ps → 8 bits, 2.4° @ 5.9 GHz |
| Channel noise factor F ≈ F_LNA + (L_PS·F_rest − 1)/G_LNA (linear ratios) | Friis | LNA gain ≥ PS loss + 15 dB |
| Error floor from PS errors ≈ (σ_a² + σ_φ²)/(Nη_t) | uncorrelated state errors | 4° + 0.4 dB, N = 16 → −25 dB |

## Worked examples

**Example 1 — a 4-element 2.44 GHz receive array with discrete parts.**
Per channel: LNA (≈ 1 dB NF, ≥ 25 dB gain) → 6-bit phase shifter (e.g. QPC2108-class at 2.5–4 GHz is out of band at 2.44 GHz; choose a 2–3 GHz part such as an HMC647A-class device only if its band covers you, or an analog JSPHS-2484+ with a DAC) → 4:1 Wilkinson → one SDR. Using the JSPHS-2484+: its 0–15 V range gives ≈ 180–320° across the band, so you need **two in cascade or a 180° switched-line bit** for full 360°, a 12–16 V DAC, and a per-frequency lookup table (its phase-vs-voltage slope varies 4.7–7× across the range, and the voltage giving 90° at 2440 MHz gives 104° at 2300 MHz and 86° at 2484 MHz — script §5) [7]. Chain NF ≈ 1.1 dB with a 30 dB LNA (script §7). Cost is dominated by the phase shifters and LNAs: order US$50–200 per channel — at which point **two coherent 2-channel SDRs or a digital approach** often wins for a 4-element array.

**Example 2 — ADAR1000 + ADTR1107 X-band channel.** Rx: ADTR1107 LNA 18 dB / 2.5 dB NF, then ADAR1000 channel (10 dB, NF 8 dB, IIP3 −7 dBm), then a mixer: cascade NF 2.7 dB, gain 21 dB (script §7). Tx: ADAR1000 channel (21 dB gain, Psat 14 dBm) drives the ADTR1107 PA (22 dB, Psat 25 dBm) → ≈ 25 dBm per element; 8 elements → EIRP ≈ 25 + 9 + 9 + ≈5 dBi element ≈ 48 dBm at broadside. Power: the ADAR1000 alone draws ≈ 3.3 V × 0.26 A ≈ 0.86 W on receive for 4 channels [1], plus the front ends.

**Example 3 — how many bits of TTD for a wideband 16-element 5.8 GHz array?** ±60°, d = 25.84 mm → T = 1.12 ns (script §6). With a 4 ps LSB: 9 bits, 2.4° rms at 5.875 GHz — negligible against a 16-element beam. ADAR4002 (508 ps max) can't span it alone: cascade two, or split into two 8-element subarrays each with its own phase shifters and a subarray-level delay.

**Example 4 — why a vector modulator is attractive for DIY at ≤ 2.4 GHz.** An ADL5390-class vector multiplier (20–2400 MHz, +5 dB to < −30 dB gain, continuous 360°) [8] driven by two 10-bit DACs gives < 0.1° quantisation error and amplitude control for tapering in one part; its I/Q imbalance (a few tenths of a dB and degrees) is systematic and calibrates out with a 2-D table. It needs a quadrature splitter in front and an LNA before it.

**Example 5 — calibration registers in practice.** ADI's Phaser software stores 8 phase offsets and 8 gain offsets (phase_cal_val.pkl, gain_cal_val.pkl) that are added to each channel's steering phase and taper gain before the ADAR1000 registers are written [11]; state-dependent errors (RMS 2° phase, 0.2 dB gain [1]) are left uncalibrated — adequate for ≈ −25 dB sidelobes with 8 elements ([tapering](tapering-sidelobe-control.md) example 1).

## Practical notes
- **Check the band edges**: most 6-bit MMIC phase shifters are specified over a fraction of an octave; outside it the bits' phase steps drift. Many parts target S-band (2.5–4 GHz) radar, *not* 2.4 GHz ISM — read the data sheet band.
- **Bias sequencing**: GaAs pHEMT switches/PAs usually need negative control or gate voltages; apply negative bias before drain supply. Beamformer ICs often provide these rails.
- **Control speed**: SPI updates of many channels take microseconds; use latch/load pins (TX_LOAD/RX_LOAD on ADAR1000) so all channels change simultaneously, and beam-state memory for fast scanning [1].
- **Layout**: every channel's trace from beamformer to antenna must be phase-matched or calibrated; 1 mm of 50 Ω microstrip on FR-4 is ≈ 12.7° at 5.8 GHz ([PCB RF layout](../13-pcb-rf-layout-emc/rf-layout-rules.md)).
- **Varactor phase shifters** are sensitive to RF level (the RF voltage modulates the capacitance): JSPHS-2484+ is rated for 0 dBm maximum operating power [7] — receive-only, after the LNA but before strong gain.
- **Obsolescence**: some classic parts (e.g. HMC928 analog 2–4 GHz, 0–450°) are marked obsolete; check lifecycle before designing in.
- **Parts catalogues** belong to [18-components-parts](../18-components-parts/rf-switches-attenuator-parts.md); this page lists representative devices only.

## Common mistakes & misconceptions
- **"A switched-line phase shifter has constant phase."** It has constant *delay*; phase ∝ f.
- **"6 bits means 5.6° accuracy."** 6 bits means 5.6° *resolution*; accuracy is the RMS phase error (1.5–4.5° for the parts above) and its gain coupling — often worse than the LSB/√12 = 1.6°.
- **"The phase shifter's loss doesn't matter on receive because the array has gain."** It adds to NF unless an LNA precedes it.
- **"Setting gain doesn't change phase."** Step attenuators and VGAs shift phase by several degrees across their range — calibrate jointly.
- **Using an analog (varactor) phase shifter as if linear in voltage.** It's strongly nonlinear and frequency-dependent; you need a lookup table per frequency.
- **Forgetting that a TTD must cover the full delay span, not just 360°.** Phase wraps; delay doesn't.
- **Assuming beamformer ICs are drop-in for any band.** ADAR1000 is 8–16 GHz; nothing like it is common at 433/915 MHz, where coherent SDR receivers or cable-length/relay-switched networks are the practical route.

## How to simulate / verify
- `tools/verify/array_components.py` (< 1 s): switched-line phase error vs frequency, loaded-line match/phase closed forms vs ABCD numerics (exact), RTPS phase range with bare/resonated/transformed varactor loads, vector-modulator DAC and I/Q-imbalance errors, JSPHS-2484+ data-sheet nonlinearity, TTD bits/errors, element-chain Friis budgets.
- Circuit-level: scikit-rf or Qucs-S/ngspice with S-parameter models of the switch/varactor (vendor .s2p files) to evaluate each state ([RF circuit simulators](../16-simulation-tools/rf-circuit-simulators-harmonic-balance.md)).
- Measurement: a 2-port VNA (NanoVNA/LibreVNA) sweeping every phase state (64 states × a few gain states) builds the calibration table directly ([VNA practice](../17-test-measurement/nanovna-librevna-practical.md)).

## Open questions / gaps
- Several part specs (ADTR1107, ADAR4002, HMC64x, QPC2108, PE44820, AWMF-0108, ADL5390) were taken from distributor/manufacturer page summaries rather than full data-sheet reads — medium confidence; the ADAR1000 and JSPHS-2484+ data sheets were read in full.
- No sourced unit prices for ADAR1000/ADTR1107 (distributor pages did not expose prices to the search tool); per-channel costs on this page are order-of-magnitude estimates except QPC2108 and the Phaser.
- Low-cost phase shifters for 433/915 MHz (e.g. switched-line relay networks, quadrature-hybrid + varactor designs) were not surveyed; the practical route at those bands is coherent SDRs ([DIY projects](diy-phased-array-projects.md)).

## Sources
1. Analog Devices, *ADAR1000 8 GHz to 16 GHz, 4-Channel, X Band and Ku Band Beamformer*, data sheet Rev. B (7/2022), analog.com/media/en/technical-documentation/data-sheets/adar1000.pdf — all ADAR1000 numbers (read in full via a distributor mirror). (datasheet)
2. Analog Devices, *ADTR1107 6 GHz to 18 GHz Front-End IC* data sheet/product page — Psat 25 dBm, Tx gain 22 dB, Rx gain 18 dB, NF 2.5 dB, 5 × 5 mm, designed to pair 4:1 with ADAR1000. (datasheet; summary)
3. Analog Devices, HMC647A (2.5–3.1 GHz, 6-bit, rms phase error 1.5°, IL variation ±0.4 dB), HMC649A (3–6 GHz, 6-bit, rms 4°, ±0.5 dB) and HMC642A (9–12.5 GHz, 6-bit, rms 4.5°, IL 7–10 dB) product pages. (datasheet; summaries)
4. Qorvo, *QPC2108 2.5–4 GHz 6-bit digital phase shifter* (0.15 µm GaAs pHEMT; rms phase error < 2.8°, amplitude error < 0.4 dB); RFMW distributor pricing US$171.39 (1–24 pcs), seen via search 2026-09. (datasheet / distributor)
5. pSemi, *PE44820 UltraCMOS 8-bit digital phase shifter, 1.7–2.2 GHz* (358.6° in 1.4° steps; usable 1.1–3.0 GHz narrowband) product page. (datasheet; summary)
6. Analog Devices, *HMC928 analog phase shifter 2–4 GHz* (0–450° with 0–13 V, ±5° phase error; obsolete) product page. (datasheet; summary)
7. Mini-Circuits, *JSPHS-2484+ 180° voltage-variable phase shifter, 2150–2484 MHz* data sheet — phase vs control-voltage table, 2.0 dB IL, VSWR 1.5, 0 dBm max operating power (read in full). (datasheet)
8. Analog Devices, *ADL5390 RF/IF vector multiplier* data sheet/product page — 20–2400 MHz, +5 dB to < −30 dB, continuous 360°. (datasheet; summary)
9. Analog Devices, *ADAR4002 0.5 GHz to 19 GHz true time delay unit* product page/Mouser — 7-bit, 508 ps/4 ps and 254 ps/2 ps ranges, 6-bit 31.5 dB DSA. (datasheet; summary)
10. Anokiwave (now Qorvo), *AWMF-0108 26.5–29.5 GHz quad beamformer IC* product page — 5-bit phase/gain, Tx 26 dB/+9 dBm, Rx coherent gain 28 dB, NF 5 dB, IIP3 −28 dBm, 1.8 V, 6 × 6 mm QFN. (datasheet; summary)
11. M. Lichtman, *PySDR* "Hands-on with Phaser" — phase_cal_val.pkl / gain_cal_val.pkl per-channel calibration. (tutorial)
12. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — ABCD/S-parameter conversions and 90° hybrids used in the derivations. (textbook)
13. S. K. Koul, B. Bhat, *Microwave and Millimeter Wave Phase Shifters*, vols. I–II, Artech House, 1991 — standard reference for switched-line, loaded-line, reflection-type and ferrite phase shifters (cited for scope; not read). (textbook)
14. `tools/verify/array_components.py` — all numbers marked "script". (own verification)
