# 17-test-measurement — Test and measurement

Scope: how to *measure* RF hardware correctly on a student budget — vector network analyzers and their
calibration (error models, SOL/SOLT/SOLR/TRL/LRM, cal-kit definitions, port extension, uncertainty), the
NanoVNA/LiteVNA/LibreVNA family in practice, spectrum analyzers (RBW, detectors, noise corrections, internal
distortion, tinySA/Siglent), oscilloscopes and RF probing (rise time, probe loading, Z0 probes, ground leads,
near-field probes), RF power (thermal/diode sensors, bursts, mismatch, log detectors), noise figure (Y-factor,
gain method, hot/cold) and receiver sensitivity testing, phase noise (direct, phase-detector, discriminator,
cross-correlation), antenna ranges and OTA/field testing of the rocket telemetry link, SDRs as instruments,
signal generators and attenuators, fixtures and de-embedding (2x-thru/P370, TRL on JLCPCB boards), lab set-up by
budget, and a board bring-up/debug playbook. Theory lives elsewhere and is linked: S-parameters and mismatch in
[03](../03-transmission-lines-matching/s-parameters.md), noise figure and phase-noise theory in
[07](../07-noise-linearity/noise-figure-and-friis.md), antenna-measurement theory in
[08](../08-antennas/antenna-measurement.md), propagation in [09](../09-propagation-link-budget/link-budget-methodology.md),
LoRa specifics in [15](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md).

## Reading order (beginner → advanced)
1. [lab-setup-by-budget](lab-setup-by-budget.md) — what to buy first (VNA → pads/loads → SA → SDR → power meter).
2. [nanovna-librevna-practical](nanovna-librevna-practical.md) — using a low-cost VNA: antenna S11 in situ, matching, filters, cables, TDR, SMD parts.
3. [spectrum-analyzers](spectrum-analyzers.md) — RBW/VBW, DANL, detectors, −2.51 dB log-average bias, LoRa TX power/OBW/harmonics safely.
4. [rf-power-measurement](rf-power-measurement.md) — sensors, bursts and duty cycle, mismatch uncertainty, attenuators, AD8307/AD8318.
5. [rf-bring-up-debug-playbook](rf-bring-up-debug-playbook.md) — the step order and symptom → cause → test tables.
6. [vna-fundamentals-calibration](vna-fundamentals-calibration.md) — error models and calibration maths; uncertainty.
7. [fixtures-and-deembedding](fixtures-and-deembedding.md) — open/short, 2x-thru, TRL on PCBs, chip antennas on small boards.
8. [oscilloscopes-and-probing-for-rf](oscilloscopes-and-probing-for-rf.md) — rise time, probe loading, Z0 probes, near-field probes.
9. [sdr-as-test-equipment](sdr-as-test-equipment.md) — RTL-SDR/HackRF/Pluto as SA, power meter, source, NF meter.
10. [signal-generators-and-sources](signal-generators-and-sources.md) — ADF4351/Si5351/tinySA sources, filtering, attenuator stacks.
11. [noise-figure-measurement](noise-figure-measurement.md) — Y-factor derivation, gain method, hot/cold loads, conducted LoRa sensitivity.
12. [antenna-range-ota-testing](antenna-range-ota-testing.md) — ground-reflection ranges, TRP/TIS, drone and attenuation range tests.
13. [phase-noise-measurement](phase-noise-measurement.md) — direct SA method limits, phase detector, discriminator, cross-correlation.
14. [bench-measurement-recipes](bench-measurement-recipes.md) — step-by-step recipes with expected numbers and uncertainty: is-it-transmitting, output impedance (two-/four-load, load-pull-lite), SWR-meter directivity, shield boxes, EBYTE power/harmonics, Wheeler cap, attenuator range test, pulses on an SA, ferrite μ.

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [vna-fundamentals-calibration](vna-fundamentals-calibration.md) | architecture, 1-port 3-term derivation (closed-form SOL), 12-/8-/16-term models, SOLT/SOLR/TRL/LRM, cal-kit C0–C3/L0–L3/offsets, port extension vs de-embedding, dynamic range/IFBW, uncertainty budgets | mixed | high |
| [nanovna-librevna-practical](nanovna-librevna-practical.md) | NanoVNA-H/H4, V2 Plus4, LiteVNA, LibreVNA specs; harmonic mode; firmware/software; recipes A–G; pitfalls | intro | medium |
| [spectrum-analyzers](spectrum-analyzers.md) | superhet, RBW/sweep time, DANL↔NF, detector biases (−1.05/−2.51 dB), ENBW, channel power/OBW, internal distortion tests, tinySA/Siglent, LoRa TX tests | mixed | high |
| [oscilloscopes-and-probing-for-rf](oscilloscopes-and-probing-for-rf.md) | t_r·BW constants, amplitude error, 10× probe loading, Z0 probes, ground-lead ringing, ENOB/FFT, H/E near-field probes | mixed | high |
| [rf-power-measurement](rf-power-measurement.md) | thermistor/thermocouple/diode sensors, diode law (Bessel I₀), two-tone error, bursts/duty cycle, mismatch uncertainty, couplers, pads, AD8307/AD8318 calibration | mixed | high |
| [noise-figure-measurement](noise-figure-measurement.md) | Y-factor derivation, ENR choice and error sensitivity, second-stage/temperature/loss corrections, gain method with SA, hot/cold loads, SDR NF, conducted sensitivity/PER statistics | mixed | high |
| [phase-noise-measurement](phase-noise-measurement.md) | direct SA method with corrections, analyzer floor, phase-detector/PLL, delay-line discriminator, cross-correlation (5 log m), multiplication, budget setups | mixed | medium |
| [antenna-range-ota-testing](antenna-range-ota-testing.md) | ground-reflection range design, ground-test pessimism (two-ray), attenuation range test, TRP/TIS, drone/kite tests, RSSI statistics | mixed | medium |
| [sdr-as-test-equipment](sdr-as-test-equipment.md) | SDR specs and limits, IQ image, dBFS→dBm calibration, sweeping, FFT tone power, SDR as source and NF meter | intro | medium |
| [signal-generators-and-sources](signal-generators-and-sources.md) | lab generators, ADF4351 harmonics/phase noise, clean-up LPF order, Si5351, tinySA/HackRF as sources, attenuator-stack uncertainty, low-level/isolation budget | mixed | medium |
| [lab-setup-by-budget](lab-setup-by-budget.md) | ≈S$300 / S$2 000 / S$15 000 kits, accessories, used-equipment checklist, Singapore notes | intro | medium |
| [fixtures-and-deembedding](fixtures-and-deembedding.md) | port extension vs open/short vs P370 2x-thru vs TRL; JLCPCB TRL line plan; chip antennas on small boards | mixed | medium |
| [rf-bring-up-debug-playbook](rf-bring-up-debug-playbook.md) | bring-up order with pass criteria; symptom→cause→test tables (range, GNSS, resets, harmonics, measurement drift) | intermediate | medium |
| [bench-measurement-recipes](bench-measurement-recipes.md) | R1–R10: transmit check, two-/four-load source impedance and load-pull-lite Γs, SWR-meter calibration and directivity extraction, shield boxes (slot SE, waveguide below cutoff, box resonances, TEM cell), conducted vs radiated, E22-400T33D power + harmonics with HPF and GUM budget, Wheeler cap uncertainty, attenuator range tests, pulse desensitisation (K = 1.505), ferrite μ′/μ″ | mixed | medium |
| [basic-bench-instruments](basic-bench-instruments.md) | frequency counters (gate time, ±1 count, timebase), DMMs at RF, scope triggering, dip meters and other everyday bench tools | mixed | medium |
| [interference-hunting-and-rf-immunity](interference-hunting-and-rf-immunity.md) | RFI hunt procedure, near/far distance laws, body fade/offset attenuator/3rd harmonic, noise-signature table, RCD/GFCI trips (Y-cap leakage, BEAMA transients, ARRL), CM choke threshold effect (K9YC), Ethernet and iperf myth, averaging to prove a fix, av-bay field vs IEC levels, PA-current magnetometer upset | mixed | medium |
| [resonator-and-cavity-perturbation-permittivity-measurement](resonator-and-cavity-perturbation-permittivity-measurement.md) | cavity perturbation derived & FD-checked, Q0 from QL and coupling (over/under), ring resonator on JLC FR-4 (gap-loading bias), two-line eigenvalue method, split-post/split-cylinder, fibreglass nose-cone recipe | mixed | medium |

## Domain FAQ (top questions → page#section)
- *How do I measure my rocket antenna's SWR without the cable lying to me?* → [nanovna-librevna-practical § Recipe A](nanovna-librevna-practical.md#recipe-a--antenna-s11-in-situ-rocket-nose-cone-or-av-bay)
- *Why exactly three calibration standards, and how is SOL solved?* → [vna-fundamentals-calibration § Level 1](vna-fundamentals-calibration.md#level-1--the-one-port-3-term-model-and-sol-calibration)
- *Do cal-kit definitions (offset delay, C0) matter at 915 MHz?* → [vna-fundamentals-calibration § Level 3](vna-fundamentals-calibration.md#level-3--calibration-kit-definitions-and-the-reference-plane)
- *How do I measure my 1 W / 2 W LoRa module's power and harmonics without destroying my tinySA?* → [spectrum-analyzers § Example 4](spectrum-analyzers.md#worked-examples), [rf-bring-up-debug-playbook](rf-bring-up-debug-playbook.md)
- *Why does my power meter read 14 dB low on LoRa packets?* → [rf-power-measurement § Example 2](rf-power-measurement.md#worked-examples)
- *Why does the analyzer read noise 2.5 dB low?* → [spectrum-analyzers § Level 2](spectrum-analyzers.md#level-2--where-the-noise-corrections-come-from)
- *Can I measure an LNA's noise figure with a tinySA?* → [noise-figure-measurement § Example 2](noise-figure-measurement.md#worked-examples)
- *How do I test my ground station's real sensitivity?* → [noise-figure-measurement § Example 4](noise-figure-measurement.md#worked-examples)
- *My range test only reached 1.5 km — will the rocket link work at 10 km?* → [antenna-range-ota-testing § Level 2](antenna-range-ota-testing.md#level-2--derivations)
- *How do I turn a short-range test into a link margin?* → [antenna-range-ota-testing § Example 3](antenna-range-ota-testing.md#worked-examples)
- *How do I measure a 0402 inductor or a matching capacitor on its pads?* → [fixtures-and-deembedding](fixtures-and-deembedding.md), [nanovna-librevna-practical § Recipe F](nanovna-librevna-practical.md#recipe-f--smd-component-on-a-fixture)
- *Why does my probe make the 100 MHz signal ring?* → [oscilloscopes-and-probing-for-rf § Level 2](oscilloscopes-and-probing-for-rf.md#level-2--where-the-constants-come-from)
- *Every TCXO I measure is −98 dBc/Hz — why?* → [phase-noise-measurement § Example 1](phase-noise-measurement.md#worked-examples)
- *What should the team buy first?* → [lab-setup-by-budget](lab-setup-by-budget.md)
- *Range is 10× shorter than expected — what do I check?* → [rf-bring-up-debug-playbook § A](rf-bring-up-debug-playbook.md#a-range-is-10-shorter-than-expected--20-db-missing-in-free-space)
- *How do I measure my amplifier's or module's output impedance?* → [bench recipes R2](bench-measurement-recipes.md#r2--outputsource-impedance-of-an-amplifier-generator-or-module-d1-295)
- *How do I calibrate my SWR meter and how far can I trust it?* → [bench recipes R3](bench-measurement-recipes.md#r3--calibrating-an-swrwattmeter-and-finding-its-directivity-d1-638)
- *How do I build/check a shield box and simulate bad reception?* → [bench recipes R5](bench-measurement-recipes.md#r5--shield-boxes-conducted-vs-radiated-tests-bad-reception-in-the-lab-d1-173-d2-213)
- *What is my E22-400T33D's true power and 2nd harmonic?* → [bench recipes R6](bench-measurement-recipes.md#r6--ebyte-module-true-output-power-and-harmonics-safely)
- *Why does a pulse read low on my SA?* → [bench recipes R9](bench-measurement-recipes.md#r9--pulsed-signals-on-a-spectrum-analyser-d1-512)

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
Rytting (error models), Keysight/Agilent AN 1287-3/-12 and 5989-4840 (VNA calibration, time domain, cal kits),
AN 150 (spectrum analysis), AN 1449-2 (power sensors), AN 57-2/57-3 (noise figure), Engen & Hoer 1979 (TRL),
Rubiola & Vernotte (cross-spectrum), Tektronix ABCs of Probes, IEEE Std 149 and IEEE 370, vendor documentation for
NanoVNA/LiteVNA/LibreVNA/tinySA/Siglent/HackRF/Pluto/ADF4351/AD8307/AD8318, and scikit-rf.

## Verification scripts
`tools/verify/meas_vna_cal.py`, `meas_nanovna.py`, `meas_sa.py`, `meas_power.py`, `meas_noise_figure.py`,
`meas_phase_noise.py`, `meas_scope_probe.py`, `meas_range.py`, `meas_sdr.py`, `meas_siggen.py`, `meas_deembed.py`,
`meas_bringup.py` — all run with numpy/scipy/scikit-rf 2.0 in under a few seconds each. `e3_bench.py` (W5-E3, 33/33 PASS, < 1 s; output in `e3_bench_output.txt`) checks the bench-recipes page.

## Known gaps
- No team *measurements* yet: every worked example is computed or illustrative; the first campaign should replace them with measured data (antenna in nose cone, attenuation range test, flight-computer desense, AD8318 conformance).
- IEEE Std 149, IEEE 370 and CTIA test plans were cited through secondary sources, not read.
- NanoVNA CH1 match/maximum input, Pluto TX power, RTL-SDR V4/HackRF noise figures and budget-scope FFT SFDR are unverified.
- Phase-noise product notes (HP 11729B/C) not retrieved; methods derived from first principles + Rubiola.
- Real-time/FFT analyzers and vector signal analysis (EVM, LoRa demod analysis) are only touched on.
- Bench recipes (W5-E3): analyser IP2, tinySA absolute accuracy, EBYTE source match, Bird-43 accuracy and die-cast box SE are assumed typical values; no hot-S22/true load-pull of the EBYTE PAs yet.
