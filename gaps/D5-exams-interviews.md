# D5 — Exam, interview and problem-set gap analysis (W4-D5)

Status: **complete** (2026-10-02; KB checked live at 196 → 214 topic pages). Owner: W4-D5. Log:
`research-logs/W4-D5-exams-interviews.md`. Writes only to this file and the log.

**Status codes.** **C** = covered: the KB states the answer, ideally with a derivation or a worked
number. **P** = partial: the topic is there but not the specific point, procedure or number.
**M** = missing. **W** = KB-wrong: the KB contradicts the correct answer, or contradicts itself
(see §2). **OOS** in a note means the question is outside the KB's remit (digital logic,
schematic symbols, vacuum tubes, optoelectronics/solar, tower climbing, pure ham operating
procedure). Such rows count toward the "all questions" rates and are left out of the
"excl. OOS" rates.

**Method (short).**
- **Question sources.**
  - The current NCVEC pools, fetched as raw JSON from `github.com/russolsen/ham_radio_question_pool`, a machine-readable mirror of the public-domain DOCX releases (no WebFetch summaries were used):
    - Technician 2026–2030, the pool that replaced 2022–26 on 2026-07-01: T3–T9, plus T0C (RF exposure) and 6 rules questions.
    - General 2023–27: G3–G9, plus G0A and 5 rules questions.
    - Extra 2024–28: E3–E9, plus E0A and 10 rules questions.
    - Every question in the RF/electronics subelements was checked. Rules questions were included only where they bear on domain 19 (telemetry, model craft, spread spectrum, ID, Line A).
  - 153 interview questions:
    - RFInsights RFIC/comms/EM list, extracted from raw HTML by curl.
    - Fan Yang's Wi-Fi/RF list, InterviewPrep's 30 RF questions, ElectronicsPost analog questions, and Glassdoor- and ResumeGemini-style antenna and radar topics (these via WebFetch, used for topics only).
    - Behavioural, networking-stack and vague questions were dropped.
  - 102 problem types:
    - The chapter themes of Pozar (Microwave Engineering), Balanis (Antenna Theory), Razavi (RF Microelectronics), Skolnik (Introduction to Radar Systems), MIT 6.013 and Stanford EE133.
    - The MIT 6.776 problem sets PS1–PS6, read from the OCW PDFs with pdftotext. Problem types are described in our own words.
- **Checking.**
  - Each question was answered against the KB: page TL;DRs for orientation, then grep, then the relevant section.
  - On 2026-10-02, a second broad re-grep of every M/P concept against the live KB found 27 false negatives from my first pass and 9 rows upgraded by new pages (domain 13 EMC/shielding/layout, 08/slot-antennas, 18, 20). All were corrected. A residual false-negative rate of a few % on M rows is likely. Rows say which page and section supports them, so they can be re-checked.
- **KB-wrong sweep.** About 60 numeric TL;DR claims touched by the sampled questions were recomputed: wave-impedance extremes and convergence distances by script; class-C efficiency; crystal L1/Q/Δf; phase-quantisation lobes; loop/monopole Rrad; FSPL; detection SNRs; total-loss-with-SWR formula; and others. All checked out except the item in §2.

## 1. Summary

**1326 questions/problem types: 761 C (57 %) · 243 P (18 %) · 321 M (24 %) · 1 W.**

| Source | n | C | P | M | W | strict pass (C) | lenient (C+P) | excl. OOS: n / strict / lenient |
|---|---|---|---|---|---|---|---|---|
| Extra pool (E3–E9, E0A, E1 subset) | 481 | 295 | 68 | 118 | 0 | 61 % | 75 % | 446 / 66 % / 81 % |
| General pool (G3–G9, G0A, G1 subset) | 303 | 159 | 50 | 94 | 0 | 52 % | 69 % | 285 / 56 % / 73 % |
| Technician pool (T3–T9, T0C, T1 subset) | 287 | 129 | 68 | 90 | 0 | 45 % | 69 % | 245 / 53 % / 80 % |
| **All pool questions** | **1071** | 583 | 186 | 302 | 0 | **54 %** | **72 %** | 976 / 60 % / 79 % |
| Interview questions | 153 | 105 | 35 | 13 | 0 | 69 % | 92 % | 151 / 70 % / 92 % |
| Textbook/problem-set types | 102 | 73 | 22 | 6 | 1 | 72 % | 93 % | — |

**Pass rates by exam subelement.** The US exams pass at 74 %. "Strict" counts only C. "Lenient"
also counts P, because a P usually lets a careful reader pick the right multiple-choice option.

| Subelement (topic) | n | C | P | M | strict | lenient | excl. OOS strict / lenient | verdict |
|---|---|---|---|---|---|---|---|---|
| E4 test equipment, receivers, interference | 63 | 44 | 7 | 12 | 70 % | 81 % | — | passes lenient |
| E5 circuit theory (resonance, phase, Q) | 49 | 47 | 1 | 1 | **96 %** | 98 % | — | passes |
| E6 components (semis, cores, MMIC, opto) | 68 | 26 | 10 | 32 | 38 % | 53 % | 58 % / 80 % | fails (opto, logic, cores, symbols) |
| E7 practical circuits (amps, filters, PSU, DSP) | 99 | 63 | 18 | 18 | 64 % | 82 % | 70 % / 90 % | passes lenient |
| E8 signals and emissions | 48 | 26 | 12 | 10 | 54 % | 79 % | — | borderline (ham modes, CW) |
| E9 antennas and feed lines | 93 | 67 | 14 | 12 | 72 % | **87 %** | — | passes lenient |
| E3 propagation | 39 | 9 | 3 | 27 | 23 % | 31 % | — | fails (EME, meteor, aurora, TEP, space weather) |
| E0A RF/electrical safety | 12 | 5 | 1 | 6 | 42 % | 50 % | 56 % / 67 % | fails |
| E1 (telemetry/model-craft/SS rules subset) | 10 | 8 | 2 | 0 | 80 % | 100 % | — | passes |
| G4 amateur practices (station, RFI, meters, mobile) | 60 | 18 | 12 | 30 | 30 % | 50 % | 33 % / 56 % | fails |
| G5 electrical principles | 40 | 36 | 4 | 0 | **90 %** | 100 % | — | passes |
| G6 components | 23 | 10 | 5 | 8 | 43 % | 65 % | 53 % / 79 % | fails strict |
| G7 practical circuits | 38 | 19 | 5 | 14 | 50 % | 63 % | 63 % / 80 % | fails strict (rectifiers, logic, symbols) |
| G8 signals and emissions | 42 | 23 | 7 | 12 | 55 % | 71 % | — | fails (ham digital modes) |
| G9 antennas and feed lines | 46 | 31 | 8 | 7 | 67 % | 85 % | — | passes lenient |
| G3 propagation | 37 | 10 | 5 | 22 | 27 % | 41 % | — | fails (space weather, LUF, scatter) |
| G0A RF safety | 12 | 7 | 4 | 1 | 58 % | 92 % | — | passes lenient |
| G1 (SS/automatic-control rules subset) | 5 | 5 | 0 | 0 | 100 % | 100 % | — | passes |
| T3 radio waves and propagation | 35 | 23 | 7 | 5 | 66 % | 86 % | — | passes lenient |
| T4 station setup and operation | 23 | 4 | 5 | 14 | 17 % | 39 % | 36 % / 82 % | mostly operating procedure |
| T5 electrical principles | 50 | 17 | 33 | 0 | 34 % | 100 % | — | no DC/units primer (all P) |
| T6 components | 46 | 20 | 3 | 23 | 43 % | 50 % | 65 % / 74 % | fails (symbols, basic parts) |
| T7 equipment, troubleshooting, meters | 44 | 20 | 6 | 18 | 45 % | 59 % | 50 % / 65 % | fails (multimeters) |
| T8 modes, satellites, digital | 47 | 14 | 5 | 28 | 30 % | 40 % | 39 % / 53 % | fails (satellites, ham modes) |
| T9 antennas and feed lines | 23 | 17 | 5 | 1 | 74 % | **96 %** | — | passes |
| T0C RF exposure | 13 | 8 | 4 | 1 | 62 % | 92 % | — | passes lenient |
| T1 (telemetry/model-craft/ID rules subset) | 6 | 6 | 0 | 0 | 100 % | 100 % | — | passes |

So the KB would pass Extra E9 at 72 % strict / 87 % lenient, E5 at 96 %, and E4 at 70 % / 81 %.
E3 propagation fails at 23 % / 31 % and G4 practices at 30 % / 50 %. The **RF-engineering core**
(E4, E5, E7 and E9; G5 and G9; T3 and T9) passes. Failures sit in three areas:

- **Amateur-specific practice:** HF propagation and space weather, ham digital modes and CW, station RFI, satellites.
- **"Day-one" electronics the KB skips:** DC and units, meters, rectifiers and regulators, batteries, semiconductor and core basics.
- **Out-of-scope topics:** logic, symbols, tubes, opto.

**By domain** (all sources; n / C / P / M / W):

| Domain | n | C | P | M | W | comment |
|---|---|---|---|---|---|---|
| 00 math | 51 | 38 | 13 | 0 | 0 | P = no SI-prefix/units table |
| 01 circuits | 105 | 79 | 25 | 1 | 0 | P = DC Ohm's-law/power basics never stated |
| 02 EM | 39 | 30 | 7 | 2 | 0 | strong |
| 03 lines/matching | 91 | 79 | 8 | 4 | 0 | strong; double-stub, open-wire line, tuners, RG-213/hardline |
| 04 components | 36 | 22 | 6 | 8 | 0 | cores (powdered iron), cap families, basic parts |
| 05 analog | 206 | 81 | 32 | 93 | 0 | many M are OOS (logic, opto, symbols); real gaps: PSU basics, batteries, semiconductor primer, IC matching |
| 06 RF circuits | 125 | 73 | 37 | 15 | 0 | PA control (ALC/foldback/sequencing), class D, duplexers, crystal filters, Wilkinson non-ideal |
| 07 noise/linearity | 54 | 44 | 6 | 3 | 1 | the W (Leeson); S-meter; radiometry |
| 08 antennas | 119 | 81 | 20 | 18 | 0 | HF wire/multiband and receive-only antennas |
| 09 propagation | 120 | 47 | 16 | 57 | 0 | HF/space-weather/VHF-DX modes; ground wave; satellites |
| 10 comms | 130 | 54 | 30 | 46 | 0 | ham digital modes, CW, speech processing, modulator circuits |
| 11 radar | 12 | 10 | 2 | 0 | 0 | strong |
| 12 arrays | 15 | 10 | 4 | 1 | 0 | pattern synthesis, stacking |
| 13 PCB/EMC | 24 | 11 | 5 | 8 | 0 | station-level RFI remaining after the new 13 pages |
| 14 SDR/DSP | 42 | 21 | 5 | 16 | 0 | receiver DSP features (NB, NR, ANF), product detector |
| 15 LoRa/ISM | 2 | 0 | 2 | 0 | 0 | — |
| 16 simulation | 8 | 5 | 3 | 0 | 0 | — |
| 17 test & measurement | 46 | 24 | 6 | 16 | 0 | counters, multimeters, scope triggering |
| 18 parts | 12 | 10 | 0 | 2 | 0 | PL-259/RCA |
| 19 regulations/safety | 87 | 42 | 16 | 29 | 0 | lightning/station grounding; exposure-rule details; band designations |
| 20 projects | 2 | 0 | 0 | 2 | 0 | soldering |

**Interviews and problem sets are the strongest result.** 92–93 % are C+P. The KB answers
nearly every core interview question, mostly with derivations and worked numbers: cascaded
NF/IIP3, noise measure, Γopt vs S11*, degenerated-LNA Zin and Gm, Miller and pole splitting,
load-pull vs conjugate match, PLL loop design, IQ imbalance, OFDM/CP, fading/diversity, Smith
chart, S-parameters, coupler and Wilkinson theory, stability circles, radar equation, MTI,
pulse compression, arrays and grating lobes. It fails on two kinds of question:

- **Analog-IC device-level questions:** mismatch and Pelgrom, current mirrors, Vth vs L, PVT, layout, CMOS breakdown, gain boosting.
- **"Second-order" textbook topics:** double-stub, image-parameter filters, unilateral figure of merit, distributed amplifiers, radiometry, pattern synthesis, ISF phase noise, shunt peaking.

## 2. KB-wrong list (all)

| # | file:line | what the KB says | correct statement | source | severity |
|---|---|---|---|---|---|
| W1 | `kb/05-analog-electronics/oscillators.md:42`, `:99–101` (also its worked examples at :101 and the §4 numbers) | Gives Leeson as $\mathcal L=10\log[\tfrac{2FkT}{P_s}(1+(\tfrac{f_0}{2Q_L\Delta f})^2)(1+\tfrac{f_c}{\Delta f})]$, attributes it to Leeson 1966, and justifies the 2 by saying "the amplifier adds noise power density $FkT$ relative to signal power $P_s$ (both sidebands: $2FkT/P_s$)". Its 433 MHz example (QL 20, 0 dBm, F = 2) gives −127 dBc/Hz at 100 kHz. | **Two different results.** First, the KB contradicts itself. `07-noise-linearity/phase-noise-and-jitter.md:29, :61–65` and `06-rf-circuits/vco-and-pll-synthesizers.md:83` both give Leeson as $FkT/(2P_s)\cdot(\dots)$, 6 dB lower. Line 65 of the phase-noise page explains that $2FkT/P_s$ is the Lee–Hajimiri tank-resistor form, with $P_s$ the power dissipated in the tank. The same inputs therefore give answers 6 dB apart depending on which page a reader opens (−127 vs −133 dBc/Hz). Second, the "both sidebands" derivation is wrong. $\mathcal L(f)$ is a single-sideband quantity, $\mathcal L=S_\varphi/2$ (IEEE 1139, already on the phase-noise page at :55). Additive white noise of one-sided density $FkT$ on a carrier $P_s$ produces $S_\varphi=FkT/P_s$, because only the quadrature half of the noise is phase noise and the ±fm components are correlated. That gives a floor of $\mathcal L=FkT/(2P_s)$. Counting "both sidebands" would give $FkT/P_s$, not $2FkT/P_s$. **Fix:** state Leeson as $FkT/(2P_s)$ with $P_s$ the carrier power at the sustaining-amplifier input. Note the $2FkT/P_s$ variant as a different definition of $P_s$/F (Rhea; Lee–Hajimiri; Wikipedia). Recompute the oscillators-page examples (−110/−133/−153 dBc/Hz at 10 k/100 k/1 MHz for its 433 MHz case, crystal case 6 dB better), or label them as the Lee–Hajimiri form. Sources genuinely differ on the prefactor, so the error is the unflagged inconsistency plus the wrong rationale, not one "true" number. | Leeson, Proc. IEEE 54(2):329–330 (1966); Rubiola, *Phase Noise and Frequency Stability in Oscillators*, CUP 2008, ch. 1–2 ($b_0=FkT_0/P_0$, $\mathcal L=S_\varphi/2$); IEEE Std 1139; Lee & Hajimiri, IEEE JSSC 35(3) 2000 (the $2FkT/P_s$ form with tank power); Wikipedia "Leeson's equation" (prints 2FkT/Ps, citing Rhea 1997) | **medium**: this is the textbook problem type "derive oscillator phase noise with Leeson" (MIT 6.776 PS6, Razavi ch. 8, Pozar ch. 13), and the answer differs by 6 dB between pages |

No other KB statement checked in this sweep contradicts a correct answer. The near-misses below
are loose wording, not errors, and are listed for the D6 consistency audit:

- `06-rf-circuits/power-amplifiers.md:46` (TL;DR) says class F "with only a 3rd-harmonic open reaches 90.7 %". That figure assumes a half-sine current, i.e. all even harmonics shorted. The page's own table at :96 makes this clear: 81.6 % with only the 2nd current harmonic.
- `12-phased-arrays/beam-steering-grating-lobes.md`: the "worst quantisation lobe ≈ −6.02P + 4.4 dB" is a fit. The exact value, which the page also lists, is $20\log\tan(\pi/2^{P+1})$: −7.7, −14.0, −20.1, −26.2 and −32.2 dB for 2–6 bits. The fit is 0.5 dB off at P = 6.
- **Pool vs physics, not the KB.** Extra E5D08 gives "skin effect" as the main RF loss in film capacitors, and Extra E9D03 says the most efficient loading-coil position is "near the centre". The KB is silent on both. If pages are added, state the conditions (dielectric vs conductor loss in film capacitors; coil position vs coil loss and current distribution). Do not just copy the pool answers.

## 3. Ranked top-40 missing/partial topics

Ranked by value for Marcus's goal (custom radios, radar, LoRa, arrays, antennas, analog) ×
number of failed questions × M-vs-P severity. "Rows" are the §4 row numbers.

| Rank | Topic (status) | Rows (examples) | Target page | What is needed |
|---|---|---|---|---|
| 1 | **Oscillator phase-noise theory and vibration** (P/W) | 1238, 1249 (W), 1237, 268, 273 | 07/phase-noise-and-jitter, 05/oscillators | Fix W1. Add a Hajimiri–Lee ISF/LTV derivation next to Leeson. Add cross-coupled LC VCO start-up and tuning range. Add **microphonics/acceleration sensitivity** of LC/crystal oscillators and its mitigation (isolation, low-g crystals); matters on a rocket. |
| 2 | **PA control and protection** (M/P) | 464, 470, 468, 926, 193, 196, 596, 908 | 06/power-amplifiers, 06/rf-switches-attenuators-limiters | ALC and drive-level loops; VSWR foldback; T/R sequencing (delay RF after keying an external PA/LNA relay); neutralisation; **class D** (voltage/current-mode); class selection switch (linear vs saturated). |
| 3 | **Receiver gain control and DSP features** (M/P) | 50–52, 58, 460, 462, 466, 36, 34, 1267 | 14/software-demodulation (new section), 07/dynamic-range-sfdr-blocking | AGC loop design (detector, attack/decay, loop stability, where to apply gain reduction); noise blanker; spectral-subtraction/LMS noise reduction; auto-notch; IF shift/passband tuning; roofing filters. |
| 4 | **Duplexers/diplexers and IF crystal filters** (M/P) | 212, 213, 214, 619, 1142 | 06/rf-filters-lc-saw-baw-cavity-microstrip, 18/filter-parts-saw-ceramic-ltcc | Cavity notch/band-pass duplexers; diplexers; crystal lattice/ladder (Cohn) filters; filter spec terms (shape factor, ultimate rejection). |
| 5 | **Non-ideal combiners** (M/P) | 1065, 1066, 1072 | 06/couplers-dividers-combiners | Lossy Wilkinson (choosing R); outputs shorted/odd terminations; combining **uncorrelated** signals/noise (half dissipated in the resistor); implications for array noise. |
| 6 | **Modulator and detector circuits** (P) | 230, 231, 233, 235, 240, 607, 608, 624, 628, 272, 1242, 1243 | 10/analog-modulation-am-fm-pm-ssb, 06/mixers | Reactance/varactor FM and PM modulators; balanced modulator → DSB → filter/phasing/Weaver SSB (worked analysis); product detector; envelope-detector RC design (ripple vs diagonal clipping); AM over-modulation (μ > 1); de-emphasis vs PM; PLL FM demodulator. |
| 7 | **Necessary bandwidth and emission rules** (P/M) | 308, 306, 313, 320, 321, 1315, 954 | 19/spectrum-allocation-ism-bands, 10/digital-modulation-psk-qam-fsk | ITU-R SM.1138 / FCC 2.202 necessary-bandwidth formulas (FSK Bn = B + DK, CW, AM, FM); CW keying bandwidth and key clicks (rise-time shaping); FCC 97.307 spurious limits; emission designators. |
| 8 | **Bench instruments basics** (M/P) | 4, 5, 10, 12, 13, 284, 477–481, 933–943 | 17/oscilloscopes-and-probing-for-rf + new 17/basic-bench-instruments | Frequency counters (time base, gate time, ±1 count, reciprocal counting, prescalers); DMM vs analog meters, loading and Ω/V; true-RMS/crest factor; ohmmeter technique; scope triggering (line trigger) and probe-compensation procedure. |
| 9 | **Transmitter intermod and co-site interference** (P) | 39, 40 | 07/nonlinearity-p1db-ip3-intermod, 06/circulators-isolators | Reverse/transmitter IMD (signals entering a PA output); circulator/isolator mitigation; co-located 433 + 915 MHz rocket transmitters. |
| 10 | **Array pattern synthesis and antenna stacking** (M/P) | 1220, 352, 693, 701 | 12/tapering-sidelobe-control, 12/array-factor-linear-arrays, 08/yagi-uda-and-log-periodic | Schelkunoff polynomial, Fourier and Woodward–Lawson synthesis; two-element cardioid/end-fire worked case; stacking two Yagis (spacing, +3 dB, elevation beamwidth) for the ground station. |
| 11 | **Station/field RFI troubleshooting** (M/P) | 53, 54, 59, 487–489, 494–496, 515, 788, 912, 913, 919 | 13/emc-emi-fundamentals (new "station and field RFI" section) | AC-line/brute-force filters, motors and arcing, vehicle charging/ignition/ECU noise, consumer-device RFI (audio rectification, TV/cable leaks), ground loops and bonding (flat strap), RFI diagnosis by sound/spectrum signature. |
| 12 | **Lightning, surge and station grounding** (M) | 62, 63, 492, 497, 1294 | 19/lab-safety-esd-high-power or 13/grounding-and-return-paths | Ground rods, single-point ground panels, surge arrestors (GDT, λ/4 stubs) at masthead LNAs, bonding, why not soldered joints, mast safety. |
| 13 | **Satellite links** (M) | 958, 961, 965, 957, 963, 967 | new 09/satellite-links (or 15/ground-station-design section) | Orbits (LEO period), Keplerian elements/TLE and tracking, pass Doppler and Doppler rate, uplink/downlink modes, linear transponders; TinyGS/cubesat reception. |
| 14 | **Wide-band amplifier techniques** (M/P) | 1245, 1208, 1207, 1205 | 05/amplifier-topologies, 06/lna-design | Shunt/series/T-coil peaking; distributed (travelling-wave) amplifiers; balanced amplifiers (S-parameter analysis); unilateral figure of merit. |
| 15 | **Open-wire line and antenna tuners** (M/P) | 393, 465, 665, 1005 | 03/coax-and-cables, 03/impedance-matching-lumped-and-distributed | Ladder/window line Z0 and loss (incl. loss vs SWR using the existing TL formula); T/L/Pi tuner topologies and their losses; what a tuner does and does not fix. D1 also flagged this. |
| 16 | **CMOS LNA design depth** (P) | 1019, 1041, 1059, 1235, 1247, 1248 | 06/lna-design | Power-constrained optimisation (W_opt at fixed Pdc); cascode device sizing and noise; induced gate noise; noise-cancelling and CG–CS wide-band LNAs; tuned cascode with finite-Q inductors. |
| 17 | **PA nonlinear behaviour depth** (P) | 1035, 1036, 1037, 1040, 1053, 1069 | 06/power-amplifiers, 07/nonlinearity-p1db-ip3-intermod | AM-AM/AM-PM → EVM and IM3 asymmetry (analytic); memory effects; active load-pull; thermal runaway/ballasting; differential/balun PAs. |
| 18 | **Analog-IC building blocks and matching** (M/P) | 1021–1025, 1038, 1049–1052, 1071, 1156 | new 05/analog-ic-building-blocks; 05/fets-mosfet-jfet-gaas-gan | Current mirrors (accuracy, output R, noise); Pelgrom mismatch, common-centroid layout, finger layout; Vth(L) effects; PVT; bandgap/PTAT; CMOS breakdown limits; gain boosting; CG input R with ro. |
| 19 | **Power-supply fundamentals** (M/P) | 218–229, 583–589, 889, 781 | 05/power-supplies-for-rf-and-analog | Half/full-wave/bridge rectifiers with ripple maths; series vs shunt and discrete pass-transistor regulators; bleeders; SMPS vs linear size/weight; supply sizing for a transmitter. |
| 20 | **Batteries** (M/P) | 560, 863, 864, 223, 789 | 05/power-supplies-for-rf-and-analog | Chemistries (Li-ion/LiPo, LiFePO4, NiMH, lead-acid, alkaline): discharge limits, internal resistance vs pulse current, Ah→runtime with temperature and Peukert effects (cold launch sites). |
| 21 | **Semiconductor primer and typical device voltages** (M/P) | 114–120, 131, 133, 562, 564, 566 | 05/diodes-schottky-pin-varactor, 05/bjt-fundamentals-small-signal | Doping, carriers, depletion; typical VF (Si, Ge, Schottky, LED); VBE on; fα and fβ vs fT; point-contact diodes; diode/transistor failure mechanisms. |
| 22 | **Comparators, Schmitt triggers and op-amp basics** (M/P) | 136, 137, 1158, 1163, 1164 | 05/op-amps-real-limitations, 05/analog-signal-conditioning | Comparator hysteresis design; virtual-short concept; integrator/differentiator behaviour and stability. |
| 23 | **Comms PHY extensions** (M/P) | 1080, 1082, 1083, 1085, 1087, 1088, 1096, 1097, 1102 | 10/ofdm + new 10/mimo-and-diversity | OFDMA; pilot-based LS/MMSE channel estimation; LMMSE; MIMO/massive MIMO, CSI and sounding; Alamouti and transmit diversity; EGC vs MRC vs SC. |
| 24 | **Weak-signal ham digital modes as design references** (M) | 307, 326, 626, 629, 648, 650, 653, 654, 658, 661, 662, 985 | new 10/amateur-digital-modes | FT8/FT4/WSPR (8-FSK/4-FSK, LDPC, 50 Hz bandwidth, SNR in 2.5 kHz reporting) as benchmarks for low-rate telemetry; PSK31/Varicode; RTTY/Baudot; AFSK levels and IMD; DMR/D-STAR TDMA; APRS packet contents. |
| 25 | **SSB speech and processing** (M) | 285, 286, 498–500, 630, 793 | 10/analog-modulation-am-fm-pm-ssb | PEP/average of speech (≈2.5:1), compression/clipping effects, flat-topping, mic-gain distortion; consequences for PA back-off. |
| 26 | **Double-stub tuners and image-parameter filters** (M) | 1183, 1197 | 03/impedance-matching-lumped-and-distributed, 01/passive-filter-design-prototypes | Double-stub design and forbidden region (listed as a gap in 03/_index); constant-k/m-derived image-parameter filters. |
| 27 | **Coax and connector catalogue gaps** (M/P) | 1008, 1011, 1012, 582 | 03/coax-and-cables, 18/connectors-and-cables-parts | RG-213/RG-8, hardline/Heliax loss tables; UHF-series (PL-259/SO-239) frequency limits; RCA. |
| 28 | **Magnetic-core basics** (M/P) | 150–156, 576 | 02/magnetic-materials-permeability, 04/inductors-at-rf | Powdered iron vs ferrite (AL values, temperature stability, Q); laminations and eddy currents; toroid field containment; brass/ferrite tuning slugs. D1 also flagged this. |
| 29 | **Capacitor families beyond MLCC** (M/P) | 105, 108, 563, 567 | 04/capacitors-at-rf-mlcc | Electrolytic/tantalum/polymer impedance vs f (bulk decoupling), film/mica/porcelain RF capacitors and their loss mechanisms. |
| 30 | **RF-exposure rule details** (M/P) | 1269, 1273, 1281, 1293, 1297, 1302, 1303 | 19/rf-exposure-safety | 1 mW exemption; multi-transmitter 5 % rule; licensee responsibility; non-ionising vs ionising; whole-body resonance (why 30–300 MHz is strictest); HF exemption thresholds. |
| 31 | **Ground-wave and surface-wave propagation** (M/P) | 442, 447, 1176 | 09/two-ray-ground-reflection (new section) | Norton surface wave / ITU-R P.368 (range vs frequency, vertical polarisation); grounded-slab surface-wave β(f) for the patch/array pages. |
| 32 | **Wire-antenna theory depth** (P) | 1221, 1222, 1223, 1225 | 08/dipoles-and-monopoles, 08/antenna-simulation-nec-openems | Pocklington/Hallén equations (the KB's own MoM tool implements them); induced-EMF mutual impedance of parallel dipoles; biconical, discone, spirals (frequency-independent). |
| 33 | **Receive-only and DF antennas** (M/P) | 410–420 (E9H), 705 | 08/loop-antennas, 12/diy-phased-array-projects | Beverage/pennant/terminated loops, receiving directivity factor, sense antennas and cardioid DF. Useful for rocket-recovery DF. |
| 34 | **HF wire and multiband antennas** (M/P) | 354–360, 385, 674, 679, 699–708 | 08/wire-antennas-hf-random-wire-fan-dipole (planned) | Long wire/rhombic, OCFD, G5RV, Zepp, traps, inverted-V, halo, random wire, buried radials and ground loss, shunt-fed towers. |
| 35 | **Antenna practicalities** (P) | 337, 338, 342, 367, 375, 380, 686, 997 | 08/dipoles-and-monopoles, 08/antenna-matching-and-baluns, 08/yagi-uda-and-log-periodic | Loading-coil position vs efficiency; gamma-match design equations; reflector vs director in 2-element Yagis; front-to-side ratio; element diameter vs bandwidth; vehicle/airframe shielding of handhelds. |
| 36 | **HF propagation and space weather** (M) | 421–459 (E3), 709–743 (G3), 772–779 | 09/ionospheric-hf-propagation + new 09/space-weather-and-vhf-dx | LUF, E-hop range, chordal hop, scatter; EME, meteor scatter, aurora, TEP, sporadic-E statistics; K/A indices, solar flux, flares/CMEs. Low relevance to UHF telemetry but the biggest exam failure. |
| 37 | **Radar extras** (P) | 1253, 1257 | 11/radar-range-equation or 11/fmcw-radar | Conical scan and sequential lobing (vs monopulse); FMCW radio-altimeter error analysis (fixed error, step error), relevant to rocket/recovery altimetry. |
| 38 | **TL transients and radiometry** (M/P) | 1260, 1212 | 03/time-domain-reflectometry, 07/thermal-noise-and-noise-temperature | Lattice (bounce) diagrams with resistive/reactive terminations; radiometer sensitivity ΔT = Tsys/√(Bτ) and Dicke switching (ties to antenna-temperature measurement). |
| 39 | **DC and units primer** (P) | 804–852 (T5), 534–536, 763–766 | new 01/dc-circuits-and-units or 00/decibels-and-log-units | Ohm's law and DC power stated explicitly; SI prefixes; band designations (HF/VHF/UHF/SHF and IEEE letter bands). Quick win; the KB claims "any level". |
| 40 | **Component, symbol and logic basics** (M, mostly OOS) | 855, 856, 861, 870, 890, 897, 136, 182, T6C rows, E7A rows | new 04/component-basics-and-symbols | Potentiometers, relays, switch poles/throws, packages (DIP), schematic symbols; minimal digital logic (gates, flip-flops, counters, CMOS vs TTL). Lowest priority. |

Already planned in INDEX.md, and largely covered by the plan: rank 34 (08/wire-antennas-hf).
The four new pages from domain 13 closed most of the earlier board-level EMC gap; rank 11 is
the station-level remainder. Everything else is **NEW** (no planned page).

## 4. Full table

| # | question/problem type (paraphrase) | source | domain | status | KB page | note |
|---|---|---|---|---|---|---|
| 1 | What limits the highest frequency a DSO displays accurately (ADC sample rate) | Extra E4A01 | 17 | C | 17/oscilloscopes-and-probing-for-rf; 14/sampling-aliasing-bandpass-sampling | sample-rate rule ≥2.5×BW stated |
| 2 | What does a spectrum analyzer plot on its axes | Extra E4A02 | 17 | C | 17/spectrum-analyzers |  |
| 3 | Instrument to see transmitter spurs/IMD | Extra E4A03 | 17 | C | 17/spectrum-analyzers |  |
| 4 | How is a 10× probe compensated (square wave, flatten tops) | Extra E4A04 | 17 | P | 17/oscilloscopes-and-probing-for-rf | compensation cap mentioned; adjustment procedure absent |
| 5 | Why use a prescaler with a frequency counter | Extra E4A05 | 17 | P | 06/frequency-multipliers-dividers | prescalers only in PLL context; no counter page |
| 6 | Effect of aliasing on a DSO display (false low-frequency trace) | Extra E4A06 | 17 | C | 17/oscilloscopes-and-probing-for-rf; 14/sampling-aliasing-bandpass-sampling |  |
| 7 | Antenna analyzer vs SWR bridge (computes Z and SWR) | Extra E4A07 | 17 | P | 17/nanovna-librevna-practical | NanoVNA covered; "antenna analyzer" class (RigExpert/MFJ) and bridges not discussed |
| 8 | Instruments that measure SWR (wattmeter, VNA, analyzer) | Extra E4A08 | 17 | C | 17/rf-power-measurement; 17/vna-fundamentals-calibration |  |
| 9 | Good probing practice: shortest ground lead | Extra E4A09 | 17 | C | 17/oscilloscopes-and-probing-for-rf |  |
| 10 | Which scope trigger mode for mains-ripple measurement (line trigger) | Extra E4A10 | 17 | M | — | no scope triggering content |
| 11 | Analyzer measures velocity factor, cable length, resonance | Extra E4A11 | 17 | C | 03/telegrapher-equations-characteristic-impedance; 03/time-domain-reflectometry |  |
| 12 | What sets frequency-counter accuracy (time base) | Extra E4B01 | 17 | M | — | frequency counters not covered (gate time, ±1 count, reciprocal counting) |
| 13 | Meaning of voltmeter ohms-per-volt sensitivity | Extra E4B02 | 17 | M | — | meter loading/analog meters absent |
| 14 | Which S-parameter is forward gain (S21) | Extra E4B03 | 03 | C | 03/s-parameters |  |
| 15 | Which S-parameter is input return loss (S11) | Extra E4B04 | 03 | C | 03/s-parameters |  |
| 16 | Three one-port VNA cal standards (S-O-L) | Extra E4B05 | 17 | C | 17/vna-fundamentals-calibration |  |
| 17 | Load power from 100 W forward / 25 W reflected (75 W) | Extra E4B06 | 03 | C | 03/reflections-vswr-return-loss-mismatch |  |
| 18 | What S-parameter subscripts mean | Extra E4B07 | 03 | C | 03/s-parameters |  |
| 19 | Determine Q of a series tuned circuit from its bandwidth | Extra E4B08 | 01 | C | 01/resonance-and-q |  |
| 20 | What a 2-port VNA measures (filter response) | Extra E4B09 | 17 | C | 17/vna-fundamentals-calibration |  |
| 21 | Two-tone test for transmitter IMD with a spectrum analyzer | Extra E4B10 | 07 | C | 07/nonlinearity-p1db-ip3-intermod | two-tone method derived; SSB-audio variant implied |
| 22 | VNA measures input/output impedance and Γ | Extra E4B11 | 17 | C | 03/s-parameters; 17/vna-fundamentals-calibration |  |
| 23 | Effect of a noisy SDR master clock (reciprocal mixing with strong neighbours) | Extra E4C01 | 07 | C | 07/phase-noise-and-jitter; 06/receiver-architectures |  |
| 24 | Front-end filter/preselector against strong out-of-band signals | Extra E4C02 | 06 | C | 06/receiver-architectures |  |
| 25 | FM capture effect | Extra E4C03 | 10 | C | 10/analog-modulation-am-fm-pm-ssb | simulated |
| 26 | Definition of receiver noise figure | Extra E4C04 | 07 | C | 07/noise-figure-and-friis |  |
| 27 | What −174 dBm/Hz represents | Extra E4C05 | 07 | C | 07/thermal-noise-and-noise-temperature |  |
| 28 | Noise floor change 50 Hz → 1 kHz bandwidth (13 dB) | Extra E4C06 | 07 | C | 07/thermal-noise-and-noise-temperature |  |
| 29 | What MDS means | Extra E4C07 | 07 | C | 07/sensitivity-and-mds |  |
| 30 | SDR overload point (ADC full scale/reference) | Extra E4C08 | 14 | C | 07/dynamic-range-sfdr-blocking; 05/data-converters-adc-dac |  |
| 31 | Why a high first IF (image rejection by front end) | Extra E4C09 | 06 | C | 06/receiver-architectures | image attenuation vs IF tabulated |
| 32 | Why match receiver bandwidth to signal bandwidth | Extra E4C10 | 07 | C | 07/sensitivity-and-mds; 17/spectrum-analyzers |  |
| 33 | Why input attenuation costs little SNR on low HF bands (external noise dominates) | Extra E4C11 | 07 | C | 07/thermal-noise-and-noise-temperature | ITU-R P.372 noise levels cited |
| 34 | What a narrow roofing filter does (blocking DR close-in) | Extra E4C12 | 06 | P | 07/dynamic-range-sfdr-blocking; 06/receiver-architectures | concept of early selectivity present; term and superhet-HF context absent |
| 35 | Define reciprocal mixing | Extra E4C13 | 07 | C | 07/phase-noise-and-jitter |  |
| 36 | Purpose of IF shift / passband tuning | Extra E4C14 | 06 | M | — | receiver operating controls absent |
| 37 | Blocking dynamic range definition (noise floor to 1 dB compression) | Extra E4D01 | 07 | C | 07/dynamic-range-sfdr-blocking | KB calls it compression dynamic range |
| 38 | Symptoms of poor dynamic range (cross-mod, desense) | Extra E4D02 | 07 | C | 07/nonlinearity-p1db-ip3-intermod; 07/dynamic-range-sfdr-blocking |  |
| 39 | Repeater-to-repeater intermod generated in a transmitter final (reverse IMD) | Extra E4D03 | 07 | P | 07/nonlinearity-p1db-ip3-intermod | transmitter/reverse intermodulation not treated |
| 40 | Circulator at transmitter output to cut transmitter intermod | Extra E4D04 | 06 | P | 06/circulators-isolators | isolator function covered, IMD-reduction use not stated |
| 41 | Term for sensitivity loss from a strong nearby signal (desensitization) | Extra E4D06 | 07 | C | 07/dynamic-range-sfdr-blocking |  |
| 42 | Attenuation before first RF stage reduces desense | Extra E4D07 | 07 | C | 07/dynamic-range-sfdr-blocking | AGC/attenuation trade stated |
| 43 | What causes intermodulation (nonlinearity) | Extra E4D08 | 07 | C | 07/nonlinearity-p1db-ip3-intermod |  |
| 44 | Purpose of a preselector | Extra E4D09 | 06 | C | 06/receiver-architectures |  |
| 45 | Meaning of a +40 dBm third-order intercept | Extra E4D10 | 07 | C | 07/nonlinearity-p1db-ip3-intermod |  |
| 46 | Why odd-order IM products matter (fall in band) | Extra E4D11 | 07 | C | 07/nonlinearity-p1db-ip3-intermod |  |
| 47 | Link margin from Pt, gains, cable loss, path loss, MDS, SNR (+8 dB) | Extra E4D12 | 09 | C | 09/link-budget-methodology |  |
| 48 | Received level from Pt, Gt, Gr, path loss (−51 dBm) | Extra E4D13 | 09 | C | 09/friis-free-space-path-loss |  |
| 49 | Convert −100 dBm to watts (0.1 pW) | Extra E4D14 | 00 | C | 00/decibels-and-log-units |  |
| 50 | Automatic notch filter side-effect (removes CW signal) | Extra E4E01 | 14 | M | — | receiver DSP features (ANF, NR, NB) absent |
| 51 | What DSP noise reduction can reduce | Extra E4E02 | 14 | M | — |  |
| 52 | Noise blanker removes impulse noise | Extra E4E03 | 14 | M | — |  |
| 53 | Suppress vehicle charging-system noise (ferrite chokes) | Extra E4E04 | 13 | P | 04/ferrites-and-beads | ferrite theory present; vehicle/EMI remedy practice absent (13-emc page unwritten) |
| 54 | Brute-force AC-line filter for motor RFI | Extra E4E05 | 13 | M | — | mains EMI filters absent (13/emc-emi-fundamentals planned) |
| 55 | Interference signature of network/computer gear (stable carriers) | Extra E4E06 | 13 | C | 13/emc-emi-fundamentals | clock harmonics landing in band |
| 56 | Why shielded cables radiate (common-mode current) | Extra E4E07 | 13 | C | 02/radiation-from-currents-hertzian-dipole; 08/antenna-matching-and-baluns |  |
| 57 | Current flowing equally on all conductors = common mode | Extra E4E08 | 13 | C | 08/antenna-matching-and-baluns |  |
| 58 | Noise-blanker side effect on strong signals | Extra E4E09 | 14 | M | — |  |
| 59 | Sources of roaring/buzzing power-line noise (arcing) | Extra E4E10 | 13 | M | — | power-line/arc RFI absent |
| 60 | Corroded joints mixing broadcast signals ("rusty bolt"/PIM) | Extra E4E11 | 07 | C | 07/nonlinearity-p1db-ip3-intermod | PIM paragraph (corroded joints) |
| 61 | Comb of carriers at regular spacing = switch-mode supply | Extra E4E12 | 13 | C | 13/emc-emi-fundamentals; 00/fourier-series-and-transform | switcher harmonics as EMI source |
| 62 | Where to install the station surge protector (single-point ground panel) | Extra E4E13 | 19 | M | — | lightning/station grounding absent |
| 63 | Purpose of a single-point ground panel | Extra E4E14 | 19 | M | — |  |
| 64 | Why reactance voltages exceed the applied voltage in series RLC (resonance, Q×) | Extra E5A01 | 01 | C | 01/resonance-and-q |  |
| 65 | Resonant frequency of 50 µH / 40 pF (3.56 MHz) | Extra E5A02 | 01 | C | 01/resonance-and-q |  |
| 66 |  | Extra E5A03 | 01 | C | 01/resonance-and-q | Z |
| 67 | Impedance of parallel RLC at resonance (≈ R, maximum) | Extra E5A04 | 01 | C | 01/resonance-and-q |  |
| 68 | Raising Q of a matching network narrows bandwidth | Extra E5A05 | 03 | C | 03/impedance-matching-lumped-and-distributed | BW≈0.5/Q table |
| 69 | Circulating current in a parallel tank at resonance (maximum, Q×) | Extra E5A06 | 01 | C | 01/resonance-and-q; 01/energy-storage-and-reactive-power |  |
| 70 | Line current into a parallel RLC at resonance (minimum) | Extra E5A07 | 01 | C | 01/resonance-and-q |  |
| 71 | V–I phase at series resonance (in phase) | Extra E5A08 | 01 | C | 01/resonance-and-q |  |
| 72 | Q of a parallel RLC (R/X) | Extra E5A09 | 01 | C | 01/resonance-and-q |  |
| 73 | Resonant frequency of 50 µH / 10 pF (7.12 MHz) | Extra E5A10 | 01 | C | 01/resonance-and-q |  |
| 74 | Half-power BW from f0 = 7.1 MHz, Q = 150 (47.3 kHz) | Extra E5A11 | 01 | C | 01/resonance-and-q |  |
| 75 | Half-power BW from f0 = 3.7 MHz, Q = 118 (31.4 kHz) | Extra E5A12 | 01 | C | 01/resonance-and-q |  |
| 76 | Effect of higher Q in a series tank (internal voltages rise) | Extra E5A13 | 01 | C | 01/resonance-and-q |  |
| 77 | Name of the 63.2 % charging time (time constant) | Extra E5B01 | 01 | C | 01/transient-and-step-response |  |
| 78 | Symbol for susceptance (B) | Extra E5B02 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 79 | Polar impedance → admittance (reciprocal magnitude, negate angle) | Extra E5B03 | 00 | C | 00/complex-numbers-and-phasors |  |
| 80 | Time constant of paralleled Cs and Rs (220 s) | Extra E5B04 | 01 | C | 01/transient-and-step-response |  |
| 81 | Reactance → susceptance magnitude (reciprocal) | Extra E5B05 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 82 | Define susceptance | Extra E5B06 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 83 | Series RLC phase angle, Xc 500 / R 1k / XL 250 (14°, V lags) | Extra E5B07 | 00 | C | 00/complex-numbers-and-phasors |  |
| 84 | Series RLC phase angle, Xc 300 / R 100 / XL 100 (63°, V lags) | Extra E5B08 | 00 | C | 00/complex-numbers-and-phasors |  |
| 85 | Capacitor current leads voltage by 90° | Extra E5B09 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 86 | Inductor voltage leads current by 90° | Extra E5B10 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 87 | Series RLC phase angle, Xc 25 / R 100 / XL 75 (27°, V leads) | Extra E5B11 | 00 | C | 00/complex-numbers-and-phasors |  |
| 88 | Define admittance | Extra E5B12 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 89 | 100 Ω capacitive reactance in rectangular form (0 − j100) | Extra E5C01 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 90 | Polar form = magnitude and angle | Extra E5C02 | 00 | C | 00/complex-numbers-and-phasors |  |
| 91 | Pure inductive reactance in polar form (+90°) | Extra E5C03 | 00 | C | 00/complex-numbers-and-phasors |  |
| 92 | Log scale for frequency-response plots | Extra E5C04 | 00 | C | 00/laplace-transfer-functions-bode |  |
| 93 | Diagram showing impedance phase relations (phasor diagram) | Extra E5C05 | 00 | C | 00/complex-numbers-and-phasors |  |
| 94 | Interpret 50 − j25 Ω (R in series with capacitive X) | Extra E5C06 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 95 | Where pure R plots on rectangular axes | Extra E5C07 | 00 | C | 00/complex-numbers-and-phasors |  |
| 96 | Coordinate system for displaying phase angle (polar) | Extra E5C08 | 00 | C | 00/complex-numbers-and-phasors |  |
| 97 | Axes of rectangular impedance plot (R horizontal, X vertical) | Extra E5C09 | 00 | C | 00/complex-numbers-and-phasors |  |
| 98 | Locate 400 Ω + 38 pF at 14 MHz on an R–X plot | Extra E5C10 | 01 | C | 01/lumped-elements-impedance-admittance | figure question; arithmetic supported |
| 99 | Locate 300 Ω + 18 µH at 3.505 MHz on an R–X plot | Extra E5C11 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 100 | Locate 300 Ω + 19 pF at 21.2 MHz on an R–X plot | Extra E5C12 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 101 | Result of skin effect (R rises with f) | Extra E5D01 | 02 | C | 02/skin-effect-conductor-loss-roughness |  |
| 102 | Why short leads at VHF+ (lead inductance) | Extra E5D02 | 04 | C | 04/pcb-parasitics-traces-vias-pads |  |
| 103 | V–I phase for reactive power (90°) | Extra E5D03 | 01 | C | 01/energy-storage-and-reactive-power |  |
| 104 | Why short connections at microwave (phase shift/electrical length) | Extra E5D04 | 02 | C | 02/quasi-static-vs-full-wave |  |
| 105 | Why electrolytic caps fail at RF (inductance) | Extra E5D05 | 04 | P | 04/capacitors-at-rf-mlcc | ESL general; electrolytic/tantalum RF behaviour not described |
| 106 | Inductor self-resonance from inter-turn capacitance | Extra E5D06 | 04 | C | 04/inductors-at-rf |  |
| 107 | Self-resonance = nominal + parasitic reactance | Extra E5D07 | 04 | C | 04/capacitors-at-rf-mlcc; 04/inductors-at-rf |  |
| 108 | Main RF loss mechanism in film capacitors | Extra E5D08 | 04 | M | — | film/mica/porcelain capacitor families not covered |
| 109 | Reactive power in ideal L and C (stored, not dissipated) | Extra E5D09 | 01 | C | 01/energy-storage-and-reactive-power |  |
| 110 | Thicker conductor → longer electrical length (shortening factor) | Extra E5D10 | 08 | C | 08/dipoles-and-monopoles | MoM K vs λ/d table |
| 111 | Real power in 100 Ω + j100 Ω at 1 A (100 W) | Extra E5D11 | 01 | C | 01/energy-storage-and-reactive-power |  |
| 112 | What reactive power is (wattless) | Extra E5D12 | 01 | C | 01/energy-storage-and-reactive-power |  |
| 113 | Where GaAs is used (microwave) | Extra E6A01 | 05 | C | 05/fets-mosfet-jfet-gaas-gan |  |
| 114 | Which material has excess free electrons (N-type) | Extra E6A02 | 05 | P | 05/diodes-schottky-pin-varactor | doping/carrier basics not explained (no semiconductor-physics primer) |
| 115 | Why a reverse-biased PN junction does not conduct (depletion widens) | Extra E6A03 | 05 | P | 05/diodes-schottky-pin-varactor | Shockley law and Cj(V) given; depletion physics only implicit |
| 116 | Impurity that adds holes (acceptor) | Extra E6A04 | 05 | M | — | no doping primer |
| 117 | FET vs BJT DC input impedance | Extra E6A05 | 05 | C | 05/fets-mosfet-jfet-gaas-gan |  |
| 118 | Define BJT beta | Extra E6A06 | 05 | C | 05/bjt-fundamentals-small-signal |  |
| 119 | Silicon BJT is on when VBE ≈ 0.6–0.7 V | Extra E6A07 | 05 | P | 05/bjt-fundamentals-small-signal; 06/amplifier-stability-and-biasing | VBE 0.8 V used in RF example; typical on-voltage not stated |
| 120 | Alpha cutoff frequency (common-base gain −3 dB) | Extra E6A08 | 05 | M | — | fT and fmax covered, fα and fβ not |
| 121 | Depletion-mode FET conducts at VGS = 0 | Extra E6A09 | 05 | C | 05/fets-mosfet-jfet-gaas-gan |  |
| 122 | Symbol of an N-channel dual-gate MOSFET | Extra E6A10 | 05 | M | — | OOS; schematic symbols and dual-gate MOSFETs absent |
| 123 | Symbol of a P-channel JFET | Extra E6A11 | 05 | M | — | OOS; schematic symbols absent |
| 124 | Zener gate protection on MOSFETs (ESD) | Extra E6A12 | 05 | P | 05/fets-mosfet-jfet-gaas-gan; 19/lab-safety-esd-high-power | ESD classes covered; gate-clamp practice not |
| 125 | Zener: constant voltage vs current | Extra E6B01 | 05 | C | 05/diodes-schottky-pin-varactor |  |
| 126 | Schottky rectifier advantage (low VF) | Extra E6B02 | 05 | C | 05/diodes-schottky-pin-varactor |  |
| 127 | LED forward voltage set by band gap | Extra E6B03 | 05 | M | — | OOS; optoelectronics out of KB scope |
| 128 | Voltage-controlled capacitor (varactor) | Extra E6B04 | 05 | C | 05/diodes-schottky-pin-varactor |  |
| 129 | PIN as RF switch (low, constant capacitance off; R set by bias) | Extra E6B05 | 05 | C | 05/diodes-schottky-pin-varactor; 06/rf-switches-attenuators-limiters |  |
| 130 | Schottky as VHF/UHF mixer/detector | Extra E6B06 | 05 | C | 05/diodes-schottky-pin-varactor; 06/detectors-and-power-meters |  |
| 131 | Diode failure from over-current (junction temperature) | Extra E6B07 | 05 | P | 05/diodes-schottky-pin-varactor | thermal limits only for PAs (06/power-amplifiers) |
| 132 | Schottky = metal–semiconductor junction | Extra E6B08 | 05 | C | 05/diodes-schottky-pin-varactor |  |
| 133 | Point-contact diode use (RF detector) | Extra E6B09 | 05 | M | — |  |
| 134 | Schottky diode schematic symbol | Extra E6B10 | 05 | M | — | OOS; symbols absent |
| 135 | PIN attenuation controlled by forward DC current | Extra E6B11 | 06 | C | 06/rf-switches-attenuators-limiters |  |
| 136 | Comparator hysteresis purpose | Extra E6C01 | 05 | M | — | comparators absent |
| 137 | Comparator output when input crosses threshold | Extra E6C02 | 05 | M | — |  |
| 138 | Tri-state logic | Extra E6C03 | 05 | M | — | OOS; digital logic out of scope |
| 139 | BiCMOS logic advantage | Extra E6C04 | 05 | M | — | OOS |
| 140 | Lowest-power logic family (CMOS) | Extra E6C05 | 05 | M | — | OOS |
| 141 | Why CMOS has good noise immunity (threshold ≈ VDD/2) | Extra E6C06 | 05 | M | — | OOS |
| 142 | Pull-up / pull-down resistor | Extra E6C07 | 05 | M | — | OOS |
| 143 | NAND symbol | Extra E6C08 | 05 | M | — | OOS |
| 144 | How an FPGA is configured (HDL) | Extra E6C09 | 14 | P | 14/fpga-for-sdr | FPGA use covered; HDL/toolflow only mentioned |
| 145 | NOR symbol | Extra E6C10 | 05 | M | — | OOS |
| 146 | NOT symbol | Extra E6C11 | 05 | M | — | OOS |
| 147 | Define piezoelectricity | Extra E6D01 | 04 | C | 04/crystals-and-resonators |  |
| 148 | Crystal equivalent circuit (BVD) | Extra E6D02 | 04 | C | 04/crystals-and-resonators |  |
| 149 | Aspect of piezo effect (deformation under voltage) | Extra E6D03 | 04 | C | 04/crystals-and-resonators |  |
| 150 | Why laminated cores (eddy-current loss) | Extra E6D04 | 02 | P | 02/magnetic-materials-permeability | eddy currents covered for ferrites; laminations not |
| 151 | Ferrite vs powdered iron (ferrite needs fewer turns) | Extra E6D05 | 04 | M | — | iron-powder cores absent (also flagged by D1) |
| 152 | Core property that sets inductance (permeability) | Extra E6D06 | 02 | C | 02/magnetic-materials-permeability |  |
| 153 | Most temperature-stable core material (powdered iron) | Extra E6D08 | 04 | M | — |  |
| 154 | Ferrite beads as VHF/UHF parasitic suppressors on HF amplifiers | Extra E6D09 | 06 | P | 04/ferrites-and-beads; 06/amplifier-stability-and-biasing | lossy stabilisation covered; bead-on-lead practice not |
| 155 | Toroid advantage (field confined in core) | Extra E6D10 | 02 | P | 02/magnetic-materials-permeability | toroid formulas, not the confinement/coupling benefit |
| 156 | Core that lowers inductance (brass/copper slug) | Extra E6D11 | 02 | M | — |  |
| 157 | Cause of inductor saturation (excess flux) | Extra E6D12 | 04 | C | 04/inductors-at-rf |  |
| 158 | Why GaAs at UHF+ (electron mobility) | Extra E6E01 | 05 | C | 05/fets-mosfet-jfet-gaas-gan |  |
| 159 | Which package is through-hole (DIP) | Extra E6E02 | 04 | P | 04/package-parasitics-bondwires | SMD packages tabulated, DIP not |
| 160 | Highest-frequency MMIC material in the list (GaN) | Extra E6E03 | 05 | C | 05/fets-mosfet-jfet-gaas-gan |  |
| 161 | Usual MMIC I/O impedance (50 Ω) | Extra E6E04 | 18 | C | 18/lna-pa-gain-block-mmics |  |
| 162 | Typical UHF preamp NF (≈ 0.5 dB) | Extra E6E05 | 06 | C | 06/lna-design; 18/lna-pa-gain-block-mmics |  |
| 163 | Why MMICs are popular (fixed gain, 50 Ω, low NF) | Extra E6E06 | 18 | C | 18/lna-pa-gain-block-mmics; 05/amplifier-topologies |  |
| 164 | Line type used to connect MMICs (microstrip) | Extra E6E07 | 03 | C | 03/planar-lines-microstrip-stripline-cpwg |  |
| 165 | How a Darlington MMIC is biased (R/choke into output) | Extra E6E08 | 18 | C | 18/lna-pa-gain-block-mmics; 05/amplifier-topologies |  |
| 166 | Package with least parasitics above HF (SMD) | Extra E6E09 | 04 | C | 04/package-parasitics-bondwires |  |
| 167 | Advantages of SMT at RF | Extra E6E10 | 04 | C | 04/package-parasitics-bondwires; 04/pcb-parasitics-traces-vias-pads |  |
| 168 | What a DIP package is | Extra E6E11 | 04 | M | — |  |
| 169 | Why DIP isn't used at UHF (lead length/inductance) | Extra E6E12 | 04 | C | 04/package-parasitics-bondwires | lead-inductance table (SOIC 5 nH) supports it |
| 170 | What absorbs light in a PV cell (electrons) | Extra E6F01 | 05 | M | — | OOS; optoelectronics absent |
| 171 | Photoconductor resistance under light | Extra E6F02 | 05 | M | — | OOS |
| 172 | Optoisolator construction (LED + phototransistor) | Extra E6F03 | 05 | M | — | OOS |
| 173 | Photovoltaic effect | Extra E6F04 | 05 | M | — | OOS |
| 174 | Optical shaft encoder | Extra E6F05 | 05 | M | — | OOS |
| 175 | Photoconductive material (crystalline semiconductor) | Extra E6F06 | 05 | M | — | OOS |
| 176 | Solid-state relay | Extra E6F07 | 05 | M | — | OOS |
| 177 | Why optoisolators with mains switching | Extra E6F08 | 05 | M | — | OOS |
| 178 | PV cell efficiency definition | Extra E6F09 | 05 | M | — | OOS |
| 179 | Common PV cell material (silicon) | Extra E6F10 | 05 | M | — | OOS |
| 180 | Silicon cell open-circuit voltage (≈ 0.5 V) | Extra E6F11 | 05 | M | — | OOS |
| 181 | Which circuit is bistable (flip-flop) | Extra E7A01 | 05 | M | — | OOS; digital logic out of KB scope |
| 182 | Decade counter function (÷10) | Extra E7A02 | 06 | P | 06/frequency-multipliers-dividers | dividers/prescalers covered, counters not |
| 183 | Divide a pulse train by 2 (flip-flop) | Extra E7A03 | 06 | C | 06/frequency-multipliers-dividers | divider stages covered |
| 184 | Flip-flops needed to divide by 16 (4) | Extra E7A04 | 06 | C | 06/frequency-multipliers-dividers |  |
| 185 | Astable multivibrator | Extra E7A05 | 05 | M | — | OOS |
| 186 | Monostable multivibrator | Extra E7A06 | 05 | M | — | OOS |
| 187 | NAND truth | Extra E7A07 | 05 | M | — | OOS; logic out of scope |
| 188 | OR truth | Extra E7A08 | 05 | M | — | OOS |
| 189 | XNOR truth | Extra E7A09 | 05 | M | — | OOS |
| 190 | What a truth table is | Extra E7A10 | 05 | M | — | OOS |
| 191 | Positive logic convention | Extra E7A11 | 05 | M | — | OOS |
| 192 | Conduction angle of class AB (180–360°) | Extra E7B01 | 06 | C | 06/power-amplifiers |  |
| 193 | What a class D amplifier is | Extra E7B02 | 06 | M | 06/power-amplifiers | classes A–C, E, F covered; class D absent |
| 194 | Output filter needed after switching PA (harmonics) | Extra E7B03 | 06 | C | 06/power-amplifiers |  |
| 195 | Class A operating point (mid load line) | Extra E7B04 | 06 | C | 06/power-amplifiers; 05/bjt-fundamentals-small-signal |  |
| 196 | Preventing PA parasitic oscillation (suppressors, neutralisation) | Extra E7B05 | 06 | P | 06/amplifier-stability-and-biasing; 05/feedback-and-stability | stabilisation by loss/feedback covered; neutralisation procedure not |
| 197 | Grounded-grid/base stage has low input impedance | Extra E7B06 | 05 | C | 05/amplifier-topologies | via CB/CG analogy |
| 198 | Class C on SSB causes distortion/splatter (needs linear PA) | Extra E7B07 | 06 | C | 06/power-amplifiers; 10/digital-modulation-psk-qam-fsk | back-off/PAPR covered |
| 199 | Why switching amplifiers are efficient | Extra E7B08 | 06 | C | 06/power-amplifiers |  |
| 200 | Emitter follower: in-phase output | Extra E7B09 | 05 | C | 05/amplifier-topologies |  |
| 201 | Purpose of base divider resistors (bias) | Extra E7B10 | 05 | C | 05/bjt-fundamentals-small-signal | figure |
| 202 | Purpose of emitter resistor (self/degeneration bias) | Extra E7B11 | 05 | C | 05/bjt-fundamentals-small-signal |  |
| 203 | Identify common-emitter stage | Extra E7B12 | 05 | C | 05/amplifier-topologies |  |
| 204 | Topology of a low-pass pi network | Extra E7C01 | 01 | C | 01/passive-filter-design-prototypes; 03/impedance-matching-lumped-and-distributed |  |
| 205 | T of series C + shunt L is high-pass | Extra E7C02 | 01 | C | 01/passive-filter-design-prototypes |  |
| 206 | Why add a series L to make a Pi-L (more harmonic suppression) | Extra E7C03 | 03 | M | — | Pi-L/tube-PA tank networks absent |
| 207 | How a match turns complex Z into R (cancel X, transform R) | Extra E7C04 | 03 | C | 03/impedance-matching-lumped-and-distributed |  |
| 208 | Ripple in passband + sharp cutoff (Chebyshev) | Extra E7C05 | 01 | C | 01/passive-filter-design-prototypes |  |
| 209 | Elliptic filter characteristics (stop-band notches) | Extra E7C06 | 01 | C | 01/passive-filter-design-prototypes |  |
| 210 | Describe a Pi-L network | Extra E7C07 | 03 | M | — |  |
| 211 | Helical filters at VHF/UHF | Extra E7C08 | 06 | C | 06/rf-filters-lc-saw-baw-cavity-microstrip | Q≈50S√f rule given |
| 212 | What a crystal lattice filter is | Extra E7C09 | 06 | M | — | crystal IF filters absent |
| 213 | Cavity filters in repeater duplexers | Extra E7C10 | 06 | P | 06/rf-filters-lc-saw-baw-cavity-microstrip; 06/circulators-isolators | cavity Q covered; duplexer design (notch/pass cavities) absent |
| 214 | Shape factor as adjacent-channel rejection metric | Extra E7C11 | 06 | P | 17/phase-noise-measurement | only mentioned for RBW filters; not defined as a filter spec |
| 215 | How a linear regulator works | Extra E7D01 | 05 | C | 05/power-supplies-for-rf-and-analog |  |
| 216 | How a switch-mode regulator works (duty cycle) | Extra E7D02 | 05 | C | 05/power-supplies-for-rf-and-analog | buck ripple equations |
| 217 | Stable voltage reference (Zener/bandgap) | Extra E7D03 | 05 | C | 05/diodes-schottky-pin-varactor; 05/power-supplies-for-rf-and-analog |  |
| 218 | Three-terminal regulator = series regulator | Extra E7D04 | 05 | P | 05/power-supplies-for-rf-and-analog |  |
| 219 | Shunt regulator loads the source | Extra E7D05 | 05 | M | — |  |
| 220 | Pass transistor role in a discrete regulator | Extra E7D06 | 05 | P | 05/power-supplies-for-rf-and-analog | figure; discrete series regulator not drawn |
| 221 | Ripple-bypass capacitor across the zener in a discrete regulator | Extra E7D07 | 05 | M | — |  |
| 222 | Identify a linear regulator schematic | Extra E7D08 | 05 | P | 05/power-supplies-for-rf-and-analog |  |
| 223 | Battery run time = Ah / average current | Extra E7D09 | 05 | P | 05/power-supplies-for-rf-and-analog | battery droop covered; runtime arithmetic not explicit |
| 224 | Why SMPS are lighter (small HF magnetics) | Extra E7D10 | 05 | P | 05/power-supplies-for-rf-and-analog |  |
| 225 | Solar inverter purpose | Extra E7D11 | 05 | M | — | OOS; out of scope |
| 226 | LDO dropout voltage | Extra E7D12 | 05 | C | 05/power-supplies-for-rf-and-analog |  |
| 227 | Series regulator dissipation (Vin−Vout)·I | Extra E7D13 | 05 | C | 05/power-supplies-for-rf-and-analog |  |
| 228 | Bleeder/equalising resistors across series filter caps | Extra E7D14 | 05 | M | — | HV supply practice absent |
| 229 | Step-start in HV supplies | Extra E7D15 | 05 | M | — |  |
| 230 | Generate FM by reactance modulation of an oscillator | Extra E7E01 | 10 | P | 10/analog-modulation-am-fm-pm-ssb; 05/diodes-schottky-pin-varactor | FM maths covered; modulator circuits thin |
| 231 | Reactance modulator function | Extra E7E02 | 10 | P | 05/diodes-schottky-pin-varactor |  |
| 232 | What a frequency discriminator does | Extra E7E03 | 10 | C | 10/analog-modulation-am-fm-pm-ssb; 14/software-demodulation |  |
| 233 | SSB by balanced modulator + filter | Extra E7E04 | 10 | P | 10/analog-modulation-am-fm-pm-ssb | filter/phasing methods treated mathematically; balanced-modulator hardware absent |
| 234 | Pre-emphasis boosts highs | Extra E7E05 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 235 | Why de-emphasis (PM compatibility) | Extra E7E06 | 10 | P | 10/analog-modulation-am-fm-pm-ssb | de-emphasis SNR gain covered; PM-equivalence rationale not |
| 236 | Meaning of baseband | Extra E7E07 | 14 | C | 14/iq-complex-baseband |  |
| 237 | Mixer output frequencies | Extra E7E08 | 06 | C | 06/mixers |  |
| 238 | Over-driven mixer → spurious products | Extra E7E09 | 06 | C | 06/mixers; 07/nonlinearity-p1db-ip3-intermod |  |
| 239 | Diode envelope detector operation | Extra E7E10 | 06 | C | 06/detectors-and-power-meters; 10/analog-modulation-am-fm-pm-ssb |  |
| 240 | SSB demodulated by a product detector | Extra E7E11 | 14 | P | 14/software-demodulation | SSB demod covered in DSP; "product detector" term absent |
| 241 | Direct-sampling SDR definition | Extra E7F01 | 14 | C | 06/receiver-architectures; 14/sampling-aliasing-bandpass-sampling |  |
| 242 | Adaptive DSP filter for SSB noise | Extra E7F02 | 14 | P | 10/pulse-shaping-isi | adaptive equalisers only; audio NR absent |
| 243 | Hilbert-transform filter to generate SSB | Extra E7F03 | 14 | C | 00/linear-systems-convolution; 14/iq-complex-baseband |  |
| 244 | DSP SSB by quadrature combination | Extra E7F04 | 14 | C | 14/iq-complex-baseband; 06/transmitter-architectures |  |
| 245 | Nyquist rate | Extra E7F05 | 14 | C | 14/sampling-aliasing-bandpass-sampling |  |
| 246 | Bits for 1 mV resolution over 1 V (10) | Extra E7F06 | 05 | C | 05/data-converters-adc-dac |  |
| 247 | What an FFT does | Extra E7F07 | 14 | C | 14/fft-spectral-analysis-windows |  |
| 248 | Function of decimation | Extra E7F08 | 14 | C | 14/multirate-dsp-decimation-cic |  |
| 249 | Why an anti-alias filter in a decimator | Extra E7F09 | 14 | C | 14/multirate-dsp-decimation-cic |  |
| 250 | What sets direct-sampling SDR bandwidth (sample rate) | Extra E7F10 | 14 | C | 14/sampling-aliasing-bandpass-sampling |  |
| 251 | What sets MDS of an ideal direct-sampling SDR (Vref, bits) | Extra E7F11 | 05 | C | 05/data-converters-adc-dac |  |
| 252 | FIR can have constant group delay | Extra E7F12 | 14 | C | 14/digital-filters-fir-iir |  |
| 253 | Function of taps | Extra E7F13 | 14 | C | 14/digital-filters-fir-iir |  |
| 254 | More taps → sharper response | Extra E7F14 | 14 | C | 14/digital-filters-fir-iir | harris length rule |
| 255 | Op-amp output impedance (very low) | Extra E7G01 | 05 | C | 05/op-amps-real-limitations |  |
| 256 | Cap across RF of inverting amp → low-pass | Extra E7G02 | 05 | C | 05/feedback-and-stability; 05/active-filters |  |
| 257 | Op-amp input impedance (very high) | Extra E7G03 | 05 | C | 05/op-amps-real-limitations |  |
| 258 | Define input offset voltage | Extra E7G04 | 05 | C | 05/op-amps-real-limitations | DC error budget |
| 259 | Prevent ringing in op-amp audio filters (limit gain and Q) | Extra E7G05 | 05 | C | 05/active-filters | sensitivity vs Q results |
| 260 | Define gain–bandwidth | Extra E7G06 | 05 | C | 05/op-amps-real-limitations |  |
| 261 | Inverting gain RF/R1 = 470/10 (47) | Extra E7G07 | 05 | C | 05/amplifier-topologies; 05/op-amps-real-limitations |  |
| 262 | Ideal op-amp gain vs frequency (flat) | Extra E7G08 | 05 | C | 05/op-amps-real-limitations |  |
| 263 | Inverting amp output for 0.23 V, 10:1 (−2.3 V) | Extra E7G09 | 05 | C | 05/amplifier-topologies |  |
| 264 | Inverting gain 68k/1.8k (38) | Extra E7G10 | 05 | C | 05/amplifier-topologies |  |
| 265 | Inverting gain 47k/3.3k (14) | Extra E7G11 | 05 | C | 05/amplifier-topologies |  |
| 266 | What an op-amp is | Extra E7G12 | 05 | C | 05/op-amps-real-limitations |  |
| 267 | Three common oscillators (Colpitts, Hartley, Pierce) | Extra E7H01 | 05 | C | 05/oscillators |  |
| 268 | Define microphonics | Extra E7H02 | 05 | P | 11/cw-and-doppler-radar; 04/capacitors-at-rf-mlcc | mentioned (radar, MLCC piezo); oscillator microphonics not treated |
| 269 | What a PLL is | Extra E7H03 | 06 | C | 06/vco-and-pll-synthesizers |  |
| 270 | Colpitts feedback via capacitive divider | Extra E7H04 | 05 | C | 05/oscillators |  |
| 271 | Pierce feedback via crystal | Extra E7H05 | 05 | C | 05/oscillators |  |
| 272 | PLL uses: synthesis and FM demodulation | Extra E7H06 | 06 | P | 06/vco-and-pll-synthesizers | synthesis covered; PLL FM demod only via Costas/carrier loops |
| 273 | Reducing oscillator microphonics (mechanical isolation) | Extra E7H07 | 05 | M | — |  |
| 274 | NP0/C0G caps to reduce crystal oscillator drift | Extra E7H08 | 04 | C | 04/crystals-and-resonators; 04/capacitors-at-rf-mlcc |  |
| 275 | DDS building blocks | Extra E7H09 | 06 | C | 06/vco-and-pll-synthesizers; 14/nco-ddc-duc |  |
| 276 | DDS lookup-table contents | Extra E7H10 | 14 | C | 14/nco-ddc-duc |  |
| 277 | DDS spectral impurities (discrete spurs) | Extra E7H11 | 14 | C | 14/nco-ddc-duc |  |
| 278 | Crystal needs specified load capacitance | Extra E7H12 | 04 | C | 04/crystals-and-resonators |  |
| 279 | Stable microwave references (GPSDO, rubidium, DRO) | Extra E7H13 | 04 | P | 04/crystals-and-resonators; 14/sdr-hardware-survey | GPSDO/Rb mentioned in parts/SDR pages; no reference-oscillator page |
| 280 | Fourier analysis: square wave = odd harmonics | Extra E8A01 | 00 | C | 00/fourier-series-and-transform |  |
| 281 | A type of ADC (successive approximation) | Extra E8A02 | 05 | C | 05/data-converters-adc-dac |  |
| 282 | Time-domain description | Extra E8A03 | 00 | C | 00/fourier-series-and-transform |  |
| 283 | ADC dither | Extra E8A04 | 05 | C | 05/data-converters-adc-dac |  |
| 284 | Benefit of a true-RMS meter | Extra E8A05 | 17 | P | 00/decibels-and-log-units | rms of non-sinusoids only implicit |
| 285 | PEP-to-average ratio of unprocessed SSB speech (~2.5:1) | Extra E8A06 | 10 | M | — | PEP defined; speech statistics absent |
| 286 | What sets SSB speech PEP/average (speech characteristics) | Extra E8A07 | 10 | M | — |  |
| 287 | Why flash ADCs for SDR (speed) | Extra E8A08 | 05 | P | 05/data-converters-adc-dac | flash mentioned (sparkle codes); architecture trade table absent |
| 288 | Levels in an 8-bit ADC (256) | Extra E8A09 | 05 | C | 05/data-converters-adc-dac |  |
| 289 | DAC output LPF removes images | Extra E8A10 | 05 | C | 05/data-converters-adc-dac |  |
| 290 | ADC quality metric (THD/SINAD/ENOB) | Extra E8A11 | 05 | C | 05/data-converters-adc-dac |  |
| 291 | FM modulation index definition | Extra E8B01 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 292 | PM index independent of carrier frequency | Extra E8B02 | 10 | P | 10/analog-modulation-am-fm-pm-ssb | PM defined; this property not stated |
| 293 | Index for 3 kHz deviation / 1 kHz tone (3) | Extra E8B03 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 294 | Index for 6 kHz / 2 kHz (3) | Extra E8B04 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 295 | Deviation ratio 5/3 (1.67) | Extra E8B05 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 296 | Deviation ratio 7.5/3.5 (2.14) | Extra E8B06 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 297 | OFDM used for digital modes | Extra E8B07 | 10 | C | 10/ofdm |  |
| 298 | Describe OFDM | Extra E8B08 | 10 | C | 10/ofdm |  |
| 299 | Define deviation ratio | Extra E8B09 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 300 | Frequency-division multiplexing | Extra E8B10 | 10 | P | 10/ofdm | OFDM only; generic FDM not defined |
| 301 | Time-division multiplexing | Extra E8B11 | 10 | P | 11/mimo-radar-virtual-arrays | TDM in MIMO radar only |
| 302 | Define QAM | Extra E8C01 | 10 | C | 10/digital-modulation-psk-qam-fsk |  |
| 303 | Define symbol rate | Extra E8C02 | 10 | C | 10/digital-modulation-psk-qam-fsk |  |
| 304 | Why change PSK phase at zero crossings (bandwidth) | Extra E8C03 | 10 | P | 10/pulse-shaping-isi | pulse shaping covered; this rule not stated |
| 305 | PSK31 bandwidth minimised by sinusoidal (raised-cosine) pulses | Extra E8C04 | 10 | P | 10/pulse-shaping-isi | PSK31 not named |
| 306 | Bandwidth of 13-WPM Morse (≈52 Hz, 4×WPM) | Extra E8C05 | 10 | M | — | CW/Morse bandwidth absent |
| 307 | FT8 bandwidth (50 Hz) | Extra E8C06 | 10 | M | — | ham digital modes absent |
| 308 | Necessary BW of 4.8 kHz-shift 9600-baud FSK (15.36 kHz) | Extra E8C07 | 10 | P | 10/digital-modulation-psk-qam-fsk; 10/analog-modulation-am-fm-pm-ssb | Carson-style estimate gives 14.4 kHz; FCC/ITU necessary-bandwidth formula (K = 1.2) absent |
| 309 | How ARQ corrects errors | Extra E8C08 | 10 | C | 10/packet-framing-protocols |  |
| 310 | Gray code property | Extra E8C09 | 10 | C | 10/ber-ebn0-and-shannon |  |
| 311 | Higher data rate without more bandwidth (more efficient code/modulation) | Extra E8C10 | 10 | C | 10/digital-modulation-psk-qam-fsk; 10/ber-ebn0-and-shannon |  |
| 312 | Symbol rate = baud | Extra E8C11 | 10 | C | 10/digital-modulation-psk-qam-fsk |  |
| 313 | CW bandwidth depends on keying speed and rise/fall time | Extra E8C12 | 10 | P | 00/fourier-series-and-transform | edge-rate spectrum derived for clocks, not CW keying |
| 314 | What a constellation diagram shows | Extra E8C13 | 10 | C | 10/digital-modulation-psk-qam-fsk |  |
| 315 | Mesh node addressing (IP) | Extra E8C14 | 10 | M | — | amateur mesh networking absent |
| 316 | How mesh nodes form a network (discovery) | Extra E8C15 | 10 | P | 15/lorawan-vs-raw-lora | Meshtastic described, not mechanisms |
| 317 | Why spread spectrum resists interference | Extra E8D01 | 10 | C | 10/spread-spectrum-dsss-fhss-css |  |
| 318 | DSSS definition | Extra E8D02 | 10 | C | 10/spread-spectrum-dsss-fhss-css |  |
| 319 | FHSS definition | Extra E8D03 | 10 | C | 10/spread-spectrum-dsss-fhss-css |  |
| 320 | Short keying edges → key clicks | Extra E8D04 | 10 | P | 00/fourier-series-and-transform |  |
| 321 | Reduce key clicks with slower edges | Extra E8D05 | 10 | P | 00/fourier-series-and-transform |  |
| 322 | Parity bits detect some errors | Extra E8D06 | 10 | C | 10/channel-coding-fec |  |
| 323 | Cause of AFSK over-modulation (audio level) | Extra E8D07 | 10 | M | — | AFSK only as APRS example |
| 324 | AFSK/PSK distortion metric (IMD) | Extra E8D08 | 10 | M | — |  |
| 325 | Acceptable idle PSK IMD (−30 dB) | Extra E8D09 | 10 | M | — |  |
| 326 | Baudot vs ASCII | Extra E8D10 | 10 | M | — | character codes absent |
| 327 | ASCII advantage (upper/lower case) | Extra E8D11 | 10 | M | — |  |
| 328 | Isotropic radiator definition | Extra E9A01 | 08 | C | 08/antenna-fundamentals |  |
| 329 | ERP from 150 W, 4.2 dB losses, 7 dBd (286 W) | Extra E9A02 | 08 | C | 08/antenna-fundamentals; 09/friis-free-space-path-loss |  |
| 330 | Term for radiated power including gains/losses (ERP) | Extra E9A03 | 08 | C | 08/antenna-fundamentals |  |
| 331 | Height above ground changes feed impedance | Extra E9A04 | 08 | C | 16/nec-antenna-modelling; 09/two-ray-ground-reflection | NEC GN0 vs GN2 near-ground example |
| 332 | "Ground gain" (up to +6 dB from reflection) | Extra E9A05 | 09 | P | 09/two-ray-ground-reflection | lobing covered; term not |
| 333 | ERP from 200 W, 8 dB losses, 10 dBd (317 W) | Extra E9A06 | 08 | C | 08/antenna-fundamentals |  |
| 334 | EIRP from 200 W, 6 dB losses, 7 dBi (252 W) | Extra E9A07 | 08 | C | 08/antenna-fundamentals |  |
| 335 | Band with smallest Fresnel zone (highest f) | Extra E9A08 | 09 | C | 09/fresnel-zones-los-radio-horizon |  |
| 336 | Antenna efficiency = Rrad/Rtotal | Extra E9A09 | 08 | C | 08/antenna-fundamentals |  |
| 337 | Radial system improves ground-mounted λ/4 vertical efficiency | Extra E9A10 | 08 | P | 08/dipoles-and-monopoles | elevated radials/impedance covered; buried-radial ground-loss efficiency absent |
| 338 | Soil conductivity sets HF vertical ground loss | Extra E9A11 | 08 | P | 02/boundary-conditions-reflection-refraction; 09/two-ray-ground-reflection | ground constants in reflection only |
| 339 | 6 dBi in dBd (3.85) | Extra E9A12 | 08 | C | 00/decibels-and-log-units; 08/antenna-fundamentals |  |
| 340 | Read 3 dB beamwidth off a polar plot | Extra E9B01 | 08 | C | 08/antenna-fundamentals | figure |
| 341 | Read front-to-back ratio | Extra E9B02 | 08 | C | 08/yagi-uda-and-log-periodic |  |
| 342 | Read front-to-side ratio | Extra E9B03 | 08 | P | 08/yagi-uda-and-log-periodic | F/S not defined |
| 343 | Read F/B off an elevation plot | Extra E9B04 | 08 | C | 08/yagi-uda-and-log-periodic |  |
| 344 | Recognise elevation vs azimuth pattern | Extra E9B05 | 08 | P | 08/antenna-fundamentals | pattern cuts described generically |
| 345 | Elevation angle of peak lobe over ground | Extra E9B06 | 09 | C | 09/two-ray-ground-reflection | sinθ lobe formula given |
| 346 | Lossless gain antenna radiates same total power as isotropic | Extra E9B07 | 08 | C | 08/antenna-fundamentals |  |
| 347 | Far-field definition | Extra E9B08 | 02 | C | 02/near-field-far-field |  |
| 348 | Common antenna modelling method (MoM) | Extra E9B09 | 16 | C | 16/nec-antenna-modelling; 00/numerical-methods-overview |  |
| 349 | MoM principle (segments with current) | Extra E9B10 | 16 | C | 08/antenna-simulation-nec-openems |  |
| 350 | Too few segments → wrong feed impedance | Extra E9B11 | 16 | C | 08/antenna-simulation-nec-openems | NEC rules λ/10–λ/20 |
| 351 | Two verticals λ/2 apart, 180° → end-fire figure-8 | Extra E9C01 | 12 | C | 12/array-factor-linear-arrays | derivable from AF; no 2-element worked case |
| 352 | Two verticals λ/4 apart, 90° → cardioid | Extra E9C02 | 12 | P | 12/array-factor-linear-arrays | endfire theory only; cardioid not shown |
| 353 | Two verticals λ/2 apart, in phase → broadside figure-8 | Extra E9C03 | 12 | C | 12/array-factor-linear-arrays |  |
| 354 | Long-wire lobes align with wire as length grows | Extra E9C04 | 08 | M | — | 08/wire-antennas-hf page planned, unwritten |
| 355 | Why feed a dipole off-centre (OCFD multiband) | Extra E9C05 | 08 | M | — |  |
| 356 | Terminating a rhombic/long wire → unidirectional | Extra E9C06 | 08 | M | — | travelling-wave antennas absent |
| 357 | Folded dipole impedance (≈300 Ω) | Extra E9C07 | 08 | C | 08/dipoles-and-monopoles | 288 Ω |
| 358 | What a folded dipole is | Extra E9C08 | 08 | C | 08/dipoles-and-monopoles |  |
| 359 | G5RV description | Extra E9C09 | 08 | M | — |  |
| 360 | Zepp = end-fed half-wave | Extra E9C10 | 08 | P | 08/dipoles-and-monopoles | EFHW covered, Zepp name not |
| 361 | Vertical antenna over seawater → more low-angle radiation | Extra E9C11 | 09 | P | 02/boundary-conditions-reflection-refraction; 09/two-ray-ground-reflection | pseudo-Brewster over sea given; pattern consequence not spelled out |
| 362 | Extended double Zepp = centre-fed 1.25λ | Extra E9C12 | 08 | C | 08/dipoles-and-monopoles | in pattern table |
| 363 | Horizontal antenna higher → lower take-off angle | Extra E9C13 | 09 | C | 09/two-ray-ground-reflection |  |
| 364 | Sloping ground lowers downhill take-off angle | Extra E9C14 | 09 | M | — |  |
| 365 | Dish gain change when f doubles (+6 dB) | Extra E9D01 | 08 | C | 08/horn-reflector-aperture-antennas |  |
| 366 | Crossed Yagis fed 90° for CP | Extra E9D02 | 08 | C | 08/yagi-uda-and-log-periodic; 08/antenna-polarization-and-circular-polarization |  |
| 367 | Best loading-coil position on a short whip (≈ centre) | Extra E9D03 | 08 | P | 08/dipoles-and-monopoles | base/top loading discussed; coil position vs efficiency not |
| 368 | High-Q loading coil for efficiency (R_loss = X/Q) | Extra E9D04 | 08 | C | 08/dipoles-and-monopoles |  |
| 369 | Yagi driven element ≈ λ/2 | Extra E9D05 | 08 | C | 08/yagi-uda-and-log-periodic |  |
| 370 | Loading coils shrink SWR bandwidth | Extra E9D06 | 08 | C | 08/small-antenna-limits |  |
| 371 | Top loading improves efficiency | Extra E9D07 | 08 | C | 08/dipoles-and-monopoles |  |
| 372 | Higher antenna Q → less SWR bandwidth | Extra E9D08 | 08 | C | 08/antenna-fundamentals; 08/small-antenna-limits |  |
| 373 | Loading coil cancels capacitive reactance | Extra E9D09 | 08 | C | 08/dipoles-and-monopoles |  |
| 374 | Short whip Rrad falls below resonance | Extra E9D10 | 08 | C | 08/dipoles-and-monopoles | R∝h² |
| 375 | Why 2-element Yagis use a reflector (more gain) | Extra E9D11 | 08 | P | 08/yagi-uda-and-log-periodic | 2-element theory present; reflector-vs-director gain comparison not stated |
| 376 | Parasitic element length sets current phase | Extra E9D12 | 08 | C | 08/yagi-uda-and-log-periodic |  |
| 377 | Match needing split/insulated DE (hairpin/beta) | Extra E9E01 | 08 | C | 08/antenna-matching-and-baluns |  |
| 378 | Gamma match description | Extra E9E02 | 08 | C | 08/antenna-matching-and-baluns |  |
| 379 | Stub match | Extra E9E03 | 03 | C | 03/input-impedance-stubs-quarter-wave; 03/impedance-matching-lumped-and-distributed |  |
| 380 | Gamma-match series capacitor cancels inductance | Extra E9E04 | 08 | P | 08/antenna-matching-and-baluns | gamma described briefly |
| 381 | Hairpin needs a capacitive (short) DE | Extra E9E05 | 08 | C | 08/antenna-matching-and-baluns |  |
| 382 | Q-section impedance for 100→50 Ω (≈71, use 75 Ω) | Extra E9E06 | 03 | C | 03/input-impedance-stubs-quarter-wave |  |
| 383 | Load–line interaction parameter (Γ) | Extra E9E07 | 03 | C | 03/reflections-vswr-return-loss-mismatch |  |
| 384 | Use of a Wilkinson divider | Extra E9E08 | 06 | C | 06/couplers-dividers-combiners |  |
| 385 | Shunt-feeding a grounded tower (gamma) | Extra E9E09 | 08 | M | — |  |
| 386 | Phasing lines between driven elements control pattern | Extra E9E11 | 12 | C | 12/array-factor-linear-arrays |  |
| 387 | Velocity factor definition | Extra E9F01 | 03 | C | 03/telegrapher-equations-characteristic-impedance |  |
| 388 | Dielectric sets velocity factor | Extra E9F02 | 03 | C | 03/coax-and-cables |  |
| 389 | Why coax electrical length > physical | Extra E9F03 | 03 | C | 03/coax-and-cables |  |
| 390 | Shorted λ/2 line → low Z | Extra E9F04 | 03 | C | 03/input-impedance-stubs-quarter-wave |  |
| 391 | What microstrip is | Extra E9F05 | 03 | C | 03/planar-lines-microstrip-stripline-cpwg |  |
| 392 | Physical λ/2 of air line at 14.1 MHz (10.6 m) | Extra E9F06 | 03 | C | 03/input-impedance-stubs-quarter-wave |  |
| 393 | Open-wire line lower loss than coax | Extra E9F07 | 03 | P | 03/telegrapher-equations-characteristic-impedance | ladder/open-wire line loss not tabulated (D1 also flagged) |
| 394 | Foam vs solid dielectric coax (VF, loss, voltage) | Extra E9F08 | 03 | C | 03/coax-and-cables |  |
| 395 | Shorted λ/4 → high Z | Extra E9F09 | 03 | C | 03/input-impedance-stubs-quarter-wave |  |
| 396 | Shorted λ/8 → inductive | Extra E9F10 | 03 | C | 03/input-impedance-stubs-quarter-wave |  |
| 397 | Open λ/8 → capacitive | Extra E9F11 | 03 | C | 03/input-impedance-stubs-quarter-wave |  |
| 398 | Open λ/4 → low Z | Extra E9F12 | 03 | C | 03/input-impedance-stubs-quarter-wave |  |
| 399 | What a Smith chart computes | Extra E9G01 | 03 | C | 03/smith-chart |  |
| 400 | Smith chart coordinates (r circles, x arcs) | Extra E9G02 | 03 | C | 03/smith-chart |  |
| 401 | Z and SWR on a line from a Smith chart | Extra E9G03 | 03 | C | 03/smith-chart |  |
| 402 | Two families of circles | Extra E9G04 | 03 | C | 03/smith-chart |  |
| 403 | Locate a matching stub with a Smith chart | Extra E9G05 | 03 | C | 03/smith-chart |  |
| 404 | Name of outer circle (reactance axis) | Extra E9G06 | 03 | P | 03/smith-chart | figure; naming not given |
| 405 | Only straight line (resistance axis) | Extra E9G07 | 03 | C | 03/smith-chart |  |
| 406 | Normalising a Smith chart | Extra E9G08 | 03 | C | 03/smith-chart |  |
| 407 | Constant-SWR circles | Extra E9G09 | 03 | C | 03/smith-chart |  |
| 408 | Arcs = constant reactance | Extra E9G10 | 03 | C | 03/smith-chart |  |
| 409 | Wavelength scales in fractions of λ | Extra E9G11 | 03 | C | 03/smith-chart |  |
| 410 | Beverage length (≥ 1 λ) | Extra E9H01 | 08 | M | — | LF/HF receive antennas absent |
| 411 | 160/80 m RX antennas: directivity beats efficiency (atmospheric noise) | Extra E9H02 | 08 | C | 07/thermal-noise-and-noise-temperature; 08/loop-antennas |  |
| 412 | Receiving directivity factor definition | Extra E9H03 | 08 | M | — |  |
| 413 | Why shield a small DF loop (balance, deeper nulls) | Extra E9H04 | 08 | C | 08/loop-antennas |  |
| 414 | Small-loop DF challenge (bidirectional null) | Extra E9H05 | 08 | C | 08/loop-antennas |  |
| 415 | Correct Beverage termination (flattest SWR) | Extra E9H06 | 08 | M | — |  |
| 416 | Beverage termination absorbs back signals | Extra E9H07 | 08 | M | — |  |
| 417 | Sense antenna for DF | Extra E9H08 | 08 | M | — |  |
| 418 | Pennant (terminated loop) cardioid | Extra E9H09 | 08 | M | — |  |
| 419 | Raise multi-turn receive loop output (N, area) | Extra E9H10 | 08 | C | 08/loop-antennas | m = NIA |
| 420 | Cardioid single null for DF | Extra E9H11 | 08 | P | 08/loop-antennas |  |
| 421 | Maximum EME ground separation | Extra E3A01 | 09 | M | — | EME/space links absent |
| 422 | Libration fading on EME | Extra E3A02 | 09 | M | — |  |
| 423 | EME path loss least at perigee | Extra E3A03 | 09 | M | — | R⁴ radar-equation analogy available in 11/radar-range-equation but not applied |
| 424 | Direction of travel ⟂ E and H | Extra E3A04 | 02 | C | 02/wave-equation-plane-waves-polarization; 02/poynting-vector-power-flow |  |
| 425 | E and H mutually perpendicular | Extra E3A05 | 02 | C | 02/wave-equation-plane-waves-polarization |  |
| 426 | MUF falls at night → lower band | Extra E3A06 | 09 | C | 09/ionospheric-hf-propagation | MUF physics; day/night Ne |
| 427 | Microwave ducts form over water | Extra E3A07 | 09 | C | 09/fresnel-zones-los-radio-horizon | tropics/over water stated |
| 428 | Meteor trails ionise the E region | Extra E3A08 | 09 | M | — | meteor scatter absent |
| 429 | Best band for meteor scatter (28–148 MHz) | Extra E3A09 | 09 | M | — |  |
| 430 | Wave speed set by refractive index | Extra E3A10 | 02 | C | 02/wave-equation-plane-waves-polarization |  |
| 431 | Typical tropo-duct range (100–300 mi) | Extra E3A11 | 09 | P | 09/fresnel-zones-los-radio-horizon | ducting described; typical ranges absent |
| 432 | Aurora propagation cause (geomagnetic storms) | Extra E3A12 | 09 | M | — |  |
| 433 | Best mode for auroral paths (CW) | Extra E3A13 | 09 | M | — |  |
| 434 | What CP waves are | Extra E3A14 | 02 | C | 02/wave-equation-plane-waves-polarization |  |
| 435 | Where TEP occurs | Extra E3B01 | 09 | M | — |  |
| 436 | TEP maximum range | Extra E3B02 | 09 | M | — |  |
| 437 | TEP time of day | Extra E3B03 | 09 | M | — |  |
| 438 | Ordinary/extraordinary (magneto-ionic) waves | Extra E3B04 | 09 | M | — | Faraday rotation covered, o/x modes not |
| 439 | 160 m DX needs an all-dark path (D-layer absorption) | Extra E3B05 | 09 | P | 09/ionospheric-hf-propagation | D absorption ∝1/f² covered; path-darkness rule not |
| 440 | Long-path propagation bands | Extra E3B06 | 09 | M | — |  |
| 441 | Lower take-off angle → longer hop | Extra E3B07 | 09 | C | 09/ionospheric-hf-propagation | hop geometry |
| 442 | Ground-wave range falls with frequency | Extra E3B08 | 09 | M | — | surface/ground wave (Norton) absent |
| 443 | Sporadic-E season (solstices) | Extra E3B09 | 09 | P | 09/ionospheric-hf-propagation | "mostly in summer" only |
| 444 | Chordal-hop effect | Extra E3B10 | 09 | M | — |  |
| 445 | Sporadic-E time of day | Extra E3B11 | 09 | M | — |  |
| 446 | Chordal-hop definition | Extra E3B12 | 09 | M | — |  |
| 447 | Ground wave supports vertical polarisation | Extra E3B13 | 09 | M | — |  |
| 448 | Solar flares cause short blackouts | Extra E3C01 | 09 | M | — | space weather absent |
| 449 | Rising A/K index meaning | Extra E3C02 | 09 | M | — |  |
| 450 | Auroral-oval absorption when K high | Extra E3C03 | 09 | M | — |  |
| 451 | What Bz is | Extra E3C04 | 09 | M | — |  |
| 452 | Southward Bz → disturbance | Extra E3C05 | 09 | M | — |  |
| 453 | VHF/UHF radio horizon ≈15 % beyond geometric | Extra E3C06 | 09 | C | 09/fresnel-zones-los-radio-horizon | k = 4/3: 4.12 vs 3.57 √h |
| 454 | Flare classes (X largest) | Extra E3C07 | 09 | M | — |  |
| 455 | G5 storm scale | Extra E3C08 | 09 | M | — |  |
| 456 | What reporting networks (RBN/PSKreporter) report | Extra E3C09 | 09 | M | — |  |
| 457 | 304 Å solar parameter | Extra E3C10 | 09 | M | — |  |
| 458 | What VOACAP models (HF) | Extra E3C11 | 09 | C | 09/ionospheric-hf-propagation |  |
| 459 | Sudden HF noise rise = CME/flare | Extra E3C12 | 09 | M | — |  |
| 460 | Purpose of a receiver notch filter | General G4A01 | 14 | M | — | receiver operating features absent |
| 461 | Reverse sideband on CW to dodge interference | General G4A02 | 10 | M | — |  |
| 462 | How a noise blanker works (gates gain during pulses) | General G4A03 | 14 | M | — |  |
| 463 | Tube PA TUNE: plate-current dip | General G4A04 | 06 | M | — | OOS; vacuum-tube PAs absent |
| 464 | Why ALC on a PA (prevent overdrive) | General G4A05 | 06 | M | — | ALC only name-checked in 05/oscillators |
| 465 | Purpose of an antenna tuner | General G4A06 | 03 | P | 03/reflections-vswr-return-loss-mismatch | only a one-line mention of a conjugate-matching tuner (D1 also flagged) |
| 466 | Too much DSP noise reduction distorts signals | General G4A07 | 14 | M | — |  |
| 467 | Tube PA LOAD adjustment | General G4A08 | 06 | M | — | OOS |
| 468 | Why delay RF after keying an external amp (T/R relay sequencing) | General G4A09 | 06 | M | — | T/R switching covered (06/rf-switches), sequencing not |
| 469 | Electronic keyer function | General G4A10 | 10 | M | — |  |
| 470 | Why ALC must be off for AFSK | General G4A11 | 06 | M | — |  |
| 471 | Dual-VFO split use | General G4A12 | 06 | M | — |  |
| 472 | Receive attenuator prevents overload | General G4A13 | 07 | C | 07/dynamic-range-sfdr-blocking |  |
| 473 | Instrument with horizontal and vertical amplifiers (scope) | General G4B01 | 17 | C | 17/oscilloscopes-and-probing-for-rf |  |
| 474 | Scope vs DVM: complex waveforms | General G4B02 | 17 | C | 17/oscilloscopes-and-probing-for-rf |  |
| 475 | Check CW keying waveform with a scope | General G4B03 | 17 | P | 17/oscilloscopes-and-probing-for-rf |  |
| 476 | Attenuated RF to scope vertical for envelope pattern | General G4B04 | 17 | P | 17/oscilloscopes-and-probing-for-rf | envelope/trapezoid monitoring absent |
| 477 | Why voltmeters have high input impedance (loading) | General G4B05 | 17 | M | — | meter loading absent |
| 478 | DMM vs analog meter (precision) | General G4B06 | 17 | M | — |  |
| 479 | Two-tone test signals | General G4B07 | 07 | C | 07/nonlinearity-p1db-ip3-intermod |  |
| 480 | Two-tone test measures linearity | General G4B08 | 07 | C | 07/nonlinearity-p1db-ip3-intermod |  |
| 481 | When an analog meter is preferred (peaking) | General G4B09 | 17 | M | — |  |
| 482 | Directional wattmeter gives SWR | General G4B10 | 17 | C | 17/rf-power-measurement |  |
| 483 | Antenna analyzer connects to antenna + feed line | General G4B11 | 17 | C | 17/nanovna-librevna-practical |  |
| 484 | Nearby transmitters corrupt analyzer readings | General G4B12 | 17 | C | 17/nanovna-librevna-practical; 17/rf-bring-up-debug-playbook | VNA overload/never key into port covered |
| 485 | Analyzer measures coax Z0 | General G4B13 | 17 | C | 03/telegrapher-equations-characteristic-impedance; 17/nanovna-librevna-practical | Z0 = √(Zopen·Zshort) |
| 486 | Bypass cap reduces RFI to audio circuits | General G4C01 | 05 | P | 05/op-amps-real-limitations; 05/analog-signal-conditioning | RF rectification in op-amps + RFI filters covered; audio-equipment RFI not |
| 487 | Arcing connection → wideband interference | General G4C02 | 13 | M | — |  |
| 488 | RFI sound from SSB (distorted speech) | General G4C03 | 13 | M | — |  |
| 489 | RFI sound from CW (on/off hum) | General G4C04 | 13 | M | — |  |
| 490 | RF burns from high-impedance ground wire | General G4C05 | 19 | P | 19/lab-safety-esd-high-power; 04/pcb-parasitics-traces-vias-pads | RF burns at high-Z elements covered; ground-lead resonance not |
| 491 | Resonant ground wire → RF on chassis | General G4C06 | 19 | P | 13/grounding-and-return-paths | "30 mm ground trace = 172 Ω" principle; station ground not |
| 492 | No soldered joints in lightning grounds | General G4C07 | 19 | M | — |  |
| 493 | Ferrite choke for common-mode on audio cable | General G4C08 | 13 | C | 08/antenna-matching-and-baluns; 04/ferrites-and-beads |  |
| 494 | Minimise ground loops (bond enclosures) | General G4C09 | 13 | P | 13/grounding-and-return-paths | return paths covered; station bonding not |
| 495 | Hum on transmitted audio from a ground loop | General G4C10 | 13 | P | 05/low-noise-analog-design |  |
| 496 | Bonding enclosures to remove RF hot spots | General G4C11 | 13 | M | — |  |
| 497 | Why ground metal enclosures (shock safety) | General G4C12 | 19 | M | — |  |
| 498 | Purpose of a speech processor | General G4D01 | 10 | M | — |  |
| 499 | Speech processor raises average power | General G4D02 | 10 | M | — |  |
| 500 | Mis-set speech processor effects | General G4D03 | 10 | M | — |  |
| 501 | What an S-meter measures | General G4D04 | 07 | M | — | RSSI covered for LoRa modules; S-meter scale absent |
| 502 | 20 dB over S9 = 100× power | General G4D05 | 00 | C | 00/decibels-and-log-units | dB arithmetic |
| 503 | One S-unit = 6 dB | General G4D06 | 07 | M | — |  |
| 504 | Power increase for one S-unit (≈4×) | General G4D07 | 00 | P | 00/decibels-and-log-units | arithmetic covered; S-unit size missing |
| 505 | 3 kHz LSB occupies below the carrier | General G4D08 | 10 | C | 10/analog-modulation-am-fm-pm-ssb; 14/software-demodulation |  |
| 506 | 3 kHz USB occupies above the carrier | General G4D09 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 507 | LSB carrier ≥ 3 kHz above lower band edge | General G4D10 | 19 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 508 | USB carrier ≥ 3 kHz below upper edge | General G4D11 | 19 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 509 | Capacitance hat electrically lengthens a short antenna | General G4E01 | 08 | C | 08/dipoles-and-monopoles |  |
| 510 | Corona ball reduces tip discharge | General G4E02 | 08 | P | 08/antenna-fundamentals | high-voltage points noted; corona not |
| 511 | Fused heavy-gauge connection to battery for 100 W | General G4E03 | 05 | P | 05/power-supplies-for-rf-and-analog | battery/wiring droop covered for 2 W modules |
| 512 | Accessory socket wiring inadequate | General G4E04 | 05 | P | 05/power-supplies-for-rf-and-analog |  |
| 513 | HF mobile limited by short-antenna efficiency | General G4E05 | 08 | C | 08/dipoles-and-monopoles; 08/small-antenna-limits |  |
| 514 | Shortened antenna → narrow bandwidth | General G4E06 | 08 | C | 08/small-antenna-limits |  |
| 515 | Vehicle interference sources | General G4E07 | 13 | M | — |  |
| 516 | Solar panel cells in series-parallel | General G4E08 | 05 | M | — | OOS |
| 517 | Si cell open-circuit voltage (0.5 V) | General G4E09 | 05 | M | — | OOS |
| 518 | Series diode between panel and battery | General G4E10 | 05 | M | — | OOS |
| 519 | Charge controller for LiFePO4 | General G4E11 | 05 | M | — | OOS |
| 520 | Series LC at resonance: very low Z | General G5A01 | 01 | C | 01/resonance-and-q |  |
| 521 | What reactance is | General G5A02 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 522 | Opposition to AC in an inductor (reactance) | General G5A03 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 523 | Opposition to AC in a capacitor (reactance) | General G5A04 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 524 | XL rises with f | General G5A05 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 525 | XC falls with f | General G5A06 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 526 | Inverse of impedance (admittance) | General G5A07 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 527 | Impedance = V/I | General G5A08 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 528 | Unit of reactance (ohm) | General G5A09 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 529 | RF matching devices (transformer, pi, line) | General G5A10 | 03 | C | 03/impedance-matching-lumped-and-distributed; 01/transformers-coupled-inductors |  |
| 530 | Symbol for reactance (X) | General G5A11 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 531 | LC resonance: reactances cancel | General G5A12 | 01 | C | 01/resonance-and-q |  |
| 532 | 3 dB = factor 2 | General G5B01 | 00 | C | 00/decibels-and-log-units |  |
| 533 | Parallel branch currents sum (KCL) | General G5B02 | 01 | C | 01/network-theorems-max-power-transfer |  |
| 534 | DC power 400 V into 800 Ω (200 W) | General G5B03 | 01 | P | 01/network-theorems-max-power-transfer | P = V²/R used but DC basics not stated explicitly |
| 535 | P = VI for a 12 V, 0.2 A lamp | General G5B04 | 01 | P | 01/network-theorems-max-power-transfer |  |
| 536 | P = I²R for 7 mA in 1.25 kΩ | General G5B05 | 01 | P | 01/network-theorems-max-power-transfer |  |
| 537 | PEP from 200 Vpp on 50 Ω (100 W) | General G5B06 | 00 | C | 00/complex-numbers-and-phasors; 00/decibels-and-log-units |  |
| 538 | RMS value = DC-equivalent heating | General G5B07 | 00 | C | 00/complex-numbers-and-phasors |  |
| 539 | Vpp of 120 V rms (339 V) | General G5B08 | 00 | C | 00/complex-numbers-and-phasors |  |
| 540 | Vrms of 17 V peak (12 V) | General G5B09 | 00 | C | 00/complex-numbers-and-phasors |  |
| 541 | 1 dB loss = 20.6 % power loss | General G5B10 | 00 | C | 00/decibels-and-log-units |  |
| 542 | PEP/average for unmodulated carrier (1) | General G5B11 | 00 | C | 00/complex-numbers-and-phasors |  |
| 543 | Vrms for 1200 W in 50 Ω (245 V) | General G5B12 | 00 | C | 00/decibels-and-log-units |  |
| 544 | PEP of 1060 W carrier (1060 W) | General G5B13 | 00 | C | 00/complex-numbers-and-phasors |  |
| 545 | PEP of 500 Vpp on 50 Ω (625 W) | General G5B14 | 00 | C | 00/complex-numbers-and-phasors |  |
| 546 | Transformer action via mutual inductance | General G5C01 | 01 | C | 01/transformers-coupled-inductors |  |
| 547 | Reverse-driven 4:1 step-down multiplies V by 4 | General G5C02 | 01 | C | 01/transformers-coupled-inductors |  |
| 548 | 10 ∥ 20 ∥ 50 Ω (5.9 Ω) | General G5C03 | 01 | C | 01/lumped-elements-impedance-admittance | admittances add |
| 549 | 100 ∥ 200 Ω (67 Ω) | General G5C04 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 550 | Primary wire heavier in step-up transformer (current) | General G5C05 | 01 | P | 01/transformers-coupled-inductors |  |
| 551 | 500:1500 turns, 120 V in → 360 V | General G5C06 | 01 | C | 01/transformers-coupled-inductors |  |
| 552 | Turns ratio 600 → 50 Ω (3.5:1) | General G5C07 | 01 | C | 01/transformers-coupled-inductors | Z ∝ n² |
| 553 | Parallel capacitors add (10.75 nF) | General G5C08 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 554 | Three 100 µF in series (33.3 µF) | General G5C09 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 555 | Three 10 mH in parallel (3.3 mH) | General G5C10 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 556 | 20 + 50 mH series (70 mH) | General G5C11 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 557 | 20 µF series 50 µF (14.3 µF) | General G5C12 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 558 | Add C in parallel to increase C | General G5C13 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 559 | Add L in series to increase L | General G5C14 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 560 | Lead-acid minimum discharge voltage (10.5 V) | General G6A01 | 05 | M | — | battery chemistry basics absent (LiPo only) |
| 561 | Low internal resistance → high discharge current | General G6A02 | 05 | C | 05/power-supplies-for-rf-and-analog |  |
| 562 | Germanium diode threshold (0.3 V) | General G6A03 | 05 | M | — |  |
| 563 | Electrolytic caps: high C per volume | General G6A04 | 04 | M | — |  |
| 564 | Silicon diode threshold (0.7 V) | General G6A05 | 05 | P | 05/diodes-schottky-pin-varactor | Shockley law given; typical VF not stated |
| 565 | Why not wire-wound resistors at RF (inductance) | General G6A06 | 04 | P | 04/resistors-at-rf | resistor inductance covered; wire-wound type not named |
| 566 | BJT switch operating points (saturation/cutoff) | General G6A07 | 05 | P | 05/fets-mosfet-jfet-gaas-gan |  |
| 567 | Low-voltage ceramic caps are cheap | General G6A08 | 04 | P | 04/capacitors-at-rf-mlcc |  |
| 568 | MOSFET insulated gate | General G6A09 | 05 | C | 05/fets-mosfet-jfet-gaas-gan |  |
| 569 | Vacuum-tube control grid | General G6A10 | 06 | M | — | OOS; tubes absent |
| 570 | Inductor above SRF is capacitive | General G6A11 | 04 | C | 04/inductors-at-rf |  |
| 571 | Screen grid reduces grid–plate capacitance | General G6A12 | 06 | M | — | OOS |
| 572 | Ferrite mix determines frequency behaviour | General G6B01 | 04 | C | 04/ferrites-and-beads; 02/magnetic-materials-permeability |  |
| 573 | Meaning of MMIC | General G6B02 | 18 | C | 18/lna-pa-gain-block-mmics |  |
| 574 | CMOS vs TTL power | General G6B03 | 05 | M | — | OOS; logic families absent |
| 575 | BNC upper frequency (≈4 GHz) | General G6B04 | 18 | C | 18/connectors-and-cables-parts |  |
| 576 | Advantages of ferrite toroid inductors | General G6B05 | 02 | P | 02/magnetic-materials-permeability; 04/ferrites-and-beads | mix/µ covered; field containment not |
| 577 | Op-amp is an analog device | General G6B06 | 05 | C | 05/op-amps-real-limitations |  |
| 578 | Type N connector (weatherproof, ~10 GHz) | General G6B07 | 18 | C | 18/connectors-and-cables-parts |  |
| 579 | LED forward bias | General G6B08 | 05 | M | — | OOS |
| 580 | How a ferrite on coax blocks CM current (series impedance) | General G6B10 | 08 | C | 08/antenna-matching-and-baluns |  |
| 581 | What SMA is | General G6B11 | 18 | C | 18/connectors-and-cables-parts |  |
| 582 | RCA phono for LF/DC connections | General G6B12 | 18 | M | — |  |
| 583 | Bleeder resistor function | General G7A01 | 05 | M | — |  |
| 584 | Supply filter parts (C and L) | General G7A02 | 05 | C | 05/power-supplies-for-rf-and-analog |  |
| 585 | Full-wave centre-tap rectifier | General G7A03 | 05 | M | — | mains rectifier circuits absent |
| 586 | Half-wave rectifier characteristics | General G7A04 | 05 | M | — |  |
| 587 | Half-wave conducts 180° | General G7A05 | 05 | M | — |  |
| 588 | Full-wave conducts 360° | General G7A06 | 05 | M | — |  |
| 589 | Unfiltered full-wave output (pulses at 2f) | General G7A07 | 05 | M | — |  |
| 590 | SMPS: high frequency allows small components | General G7A08 | 05 | C | 05/power-supplies-for-rf-and-analog |  |
| 591 | FET schematic symbol | General G7A09 | 05 | M | — | OOS; schematic symbols absent |
| 592 | Zener symbol | General G7A10 | 05 | M | — | OOS |
| 593 | NPN symbol | General G7A11 | 05 | M | — | OOS |
| 594 | Solid-core transformer symbol | General G7A12 | 05 | M | — | OOS |
| 595 | Tapped inductor symbol | General G7A13 | 05 | M | — | OOS |
| 596 | Purpose of neutralisation (stop self-oscillation) | General G7B01 | 06 | P | 05/bjt-fundamentals-small-signal; 06/amplifier-stability-and-biasing | only as Mason-U concept |
| 597 | Most efficient class listed (C) | General G7B02 | 06 | C | 06/power-amplifiers |  |
| 598 | AND gate | General G7B03 | 05 | M | — | OOS |
| 599 | Class A conducts 100 % | General G7B04 | 06 | C | 06/power-amplifiers |  |
| 600 | States of a 3-bit counter (8) | General G7B05 | 05 | M | — | OOS |
| 601 | Shift register | General G7B06 | 05 | M | — | OOS |
| 602 | Oscillator = amplifier + filter in a loop | General G7B07 | 05 | C | 05/oscillators |  |
| 603 | PA efficiency = RF out / DC in | General G7B08 | 06 | C | 06/power-amplifiers |  |
| 604 | LC oscillator frequency set by tank | General G7B09 | 05 | C | 05/oscillators |  |
| 605 | Linear amplifier preserves waveform | General G7B10 | 06 | C | 06/power-amplifiers |  |
| 606 | Class C OK for FM (constant envelope) | General G7B11 | 06 | C | 06/power-amplifiers; 10/digital-modulation-psk-qam-fsk |  |
| 607 | Filter selects sideband after balanced modulator | General G7C01 | 10 | P | 10/analog-modulation-am-fm-pm-ssb |  |
| 608 | Balanced modulator gives DSB-SC | General G7C02 | 06 | P | 06/mixers | DBM covered as mixer, not as modulator |
| 609 | Matching transformer at transmitter output | General G7C03 | 03 | C | 03/impedance-matching-lumped-and-distributed; 06/power-amplifiers |  |
| 610 | Product detector in SSB receivers | General G7C04 | 14 | P | 14/software-demodulation |  |
| 611 | DDS: tunable with crystal stability | General G7C05 | 06 | C | 06/vco-and-pll-synthesizers |  |
| 612 | DSP filter advantage (any shape/BW) | General G7C06 | 14 | C | 14/digital-filters-fir-iir |  |
| 613 | Passband attenuation = insertion loss | General G7C07 | 06 | C | 06/rf-filters-lc-saw-baw-cavity-microstrip |  |
| 614 | What affects sensitivity (gain, BW, NF) | General G7C08 | 07 | C | 07/sensitivity-and-mds; 07/noise-figure-and-friis |  |
| 615 | I/Q are 90° apart | General G7C09 | 14 | C | 14/iq-complex-baseband |  |
| 616 | IQ lets software make any modulation | General G7C10 | 14 | C | 14/iq-complex-baseband |  |
| 617 | Functions done in SDR software | General G7C11 | 14 | C | 14/gnu-radio-and-software-stack; 14/software-demodulation |  |
| 618 | LPF cutoff = half-power point | General G7C12 | 01 | C | 01/passive-filter-design-prototypes |  |
| 619 | Ultimate rejection term | General G7C13 | 06 | P | 18/filter-parts-saw-ceramic-ltcc; 05/active-filters | stop-band floor discussed; term not |
| 620 | BPF bandwidth between half-power points | General G7C14 | 01 | C | 01/resonance-and-q |  |
| 621 | Direct FSK by switching an oscillator's frequency | General G8A01 | 10 | C | 10/digital-modulation-psk-qam-fsk; 06/transmitter-architectures |  |
| 622 | Phase modulation definition | General G8A02 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 623 | Frequency modulation definition | General G8A03 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 624 | Reactance modulator on an amplifier stage gives PM | General G8A04 | 10 | P | 10/analog-modulation-am-fm-pm-ssb |  |
| 625 | AM varies instantaneous power | General G8A05 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 626 | QPSK31 properties | General G8A06 | 10 | M | — | ham PSK modes absent |
| 627 | Narrowest phone emission (SSB) | General G8A07 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 628 | Over-modulation widens bandwidth | General G8A08 | 10 | P | 10/analog-modulation-am-fm-pm-ssb | AM with μ>1 not discussed |
| 629 | FT8 = 8-FSK | General G8A09 | 10 | M | — |  |
| 630 | AM "flat-topping" | General G8A10 | 10 | M | — |  |
| 631 | AM modulation envelope | General G8A11 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 632 | QPSK definition | General G8A12 | 10 | C | 10/digital-modulation-psk-qam-fsk |  |
| 633 | Define link budget | General G8A13 | 09 | C | 09/link-budget-methodology |  |
| 634 | Define link margin | General G8A14 | 09 | C | 09/link-budget-methodology; 09/link-margin-availability |  |
| 635 | LO is tuned to convert to a fixed IF | General G8B01 | 06 | C | 06/mixers; 06/receiver-architectures |  |
| 636 | Image at 2×IF from wanted signal | General G8B02 | 06 | C | 06/mixers |  |
| 637 | Mixing = heterodyning | General G8B03 | 06 | C | 06/mixers |  |
| 638 | Multiplier stage in VHF FM transmitter | General G8B04 | 06 | C | 06/frequency-multipliers-dividers |  |
| 639 | Odd-order IMs lie closest to the tones | General G8B05 | 07 | C | 07/nonlinearity-p1db-ip3-intermod |  |
| 640 | Carson BW for 5 kHz dev / 3 kHz (16 kHz) | General G8B06 | 10 | C | 10/analog-modulation-am-fm-pm-ssb | worked number in KB |
| 641 | Deviation needed at 12.21 MHz for 5 kHz at 146.52 MHz (÷12) | General G8B07 | 06 | P | 06/frequency-multipliers-dividers | phase-deviation ×N stated (20 log N); FM-deviation-×N example absent |
| 642 | Mode duty cycle vs PA average rating | General G8B08 | 06 | P | 06/power-amplifiers; 15/ism-band-plans-duty-cycle | thermal P_diss covered; mode duty/thermal rating not linked |
| 643 | Match RX bandwidth for best SNR | General G8B09 | 07 | C | 07/sensitivity-and-mds |  |
| 644 | Higher symbol rate needs more bandwidth | General G8B10 | 10 | C | 10/digital-modulation-psk-qam-fsk |  |
| 645 | Mixer outputs sum and difference | General G8B11 | 06 | C | 06/mixers |  |
| 646 | Intermodulation definition | General G8B12 | 07 | C | 07/nonlinearity-p1db-ip3-intermod |  |
| 647 | 2F1−F2 is odd-order | General G8B13 | 07 | C | 07/nonlinearity-p1db-ip3-intermod |  |
| 648 | WSPR beacons | General G8C02 | 10 | M | — |  |
| 649 | Packet header carries routing info | General G8C03 | 10 | C | 10/packet-framing-protocols |  |
| 650 | Baudot code | General G8C04 | 10 | M | — |  |
| 651 | NAK requests retransmission | General G8C05 | 10 | C | 10/packet-framing-protocols |  |
| 652 | ARQ retry limit drops link | General G8C06 | 10 | P | 10/packet-framing-protocols |  |
| 653 | FT8 works at very low SNR | General G8C07 | 10 | M | — | weak-signal ham modes absent (LoRa analogue covered) |
| 654 | PSK31 Varicode upper-case penalty | General G8C08 | 10 | M | — |  |
| 655 | Mesh resilience via alternate nodes | General G8C09 | 10 | P | 15/lorawan-vs-raw-lora |  |
| 656 | How FEC corrects errors (redundancy) | General G8C10 | 10 | C | 10/channel-coding-fec |  |
| 657 | FSK mark and space | General G8C11 | 10 | M | — | terminology absent |
| 658 | PSK31 Varicode | General G8C12 | 10 | M | — |  |
| 659 | Vertical side lines on a waterfall = overmodulation | General G8C13 | 14 | M | — |  |
| 660 | Waterfall axes | General G8C14 | 14 | P | 14/fft-spectral-analysis-windows | spectrogram covered |
| 661 | FT8 SNR report reference bandwidth (2.5 kHz) | General G8C15 | 10 | M | — |  |
| 662 | Digital voice modes (DMR, D-STAR, Fusion) | General G8C16 | 10 | M | — |  |
| 663 | Two-wire Z0 set by spacing and radius | General G9A01 | 03 | C | 02/inductance-capacitance-from-fields; 03/telegrapher-equations-characteristic-impedance | L′ = (µ0/π)acosh(D/2a) |
| 664 | High SWR increases loss in a lossy line | General G9A02 | 03 | C | 03/reflections-vswr-return-loss-mismatch | total-loss formula TL = 10 log[(a²−\|Γ\|²)/(a(1−\|Γ\|²))] (line 111) |
| 665 | Window-line nominal Z0 (≈450 Ω) | General G9A03 | 03 | M | — | open-wire/ladder line not covered (D1 also) |
| 666 | Reflection cause: line/load Z difference | General G9A04 | 03 | C | 03/reflections-vswr-return-loss-mismatch |  |
| 667 | Coax loss rises with f | General G9A05 | 03 | C | 03/coax-and-cables |  |
| 668 | Feed-line loss units (dB per length) | General G9A06 | 03 | C | 03/coax-and-cables |  |
| 669 | Match load to Z0 to avoid standing waves | General G9A07 | 03 | C | 03/reflections-vswr-return-loss-mismatch |  |
| 670 | Tuner at TX end leaves line SWR at 5:1 | General G9A08 | 03 | C | 03/reflections-vswr-return-loss-mismatch | tuner re-reflection myth addressed |
| 671 | SWR of 200 Ω on 50 Ω (4:1) | General G9A09 | 03 | C | 03/reflections-vswr-return-loss-mismatch |  |
| 672 | SWR of 10 Ω on 50 Ω (5:1) | General G9A10 | 03 | C | 03/reflections-vswr-return-loss-mismatch |  |
| 673 | Line loss lowers measured SWR | General G9A11 | 03 | C | 03/reflections-vswr-return-loss-mismatch | RL_in = RL_load + 2A |
| 674 | Random wire direct to rig → RF on equipment | General G9B01 | 08 | P | 08/dipoles-and-monopoles; 08/antenna-matching-and-baluns | CM/counterpoise physics covered; random wire not |
| 675 | Droop radials to get 50 Ω | General G9B02 | 08 | C | 08/dipoles-and-monopoles | MoM 30–60° table |
| 676 | Ground-plane vertical pattern (omni azimuth) | General G9B03 | 08 | C | 08/dipoles-and-monopoles |  |
| 677 | Dipole pattern in plane of wire (figure-8 ⟂) | General G9B04 | 08 | C | 08/dipoles-and-monopoles |  |
| 678 | Low dipole (< λ/2) high-angle pattern ~omni | General G9B05 | 09 | P | 09/two-ray-ground-reflection | image theory present; NVIS pattern consequence stated only in 09/ionospheric (NVIS) |
| 679 | Ground radials on/under surface | General G9B06 | 08 | M | — | buried radials absent |
| 680 | Dipole feed Z falls as height → 0.1λ | General G9B07 | 08 | P | 16/nec-antenna-modelling | NEC near-ground example only |
| 681 | Feed Z rises moving feed off-centre | General G9B08 | 08 | C | 08/dipoles-and-monopoles | EFHW ≈ 2 kΩ at end |
| 682 | Horizontal polarisation: lower ground loss at HF | General G9B09 | 08 | P | 09/two-ray-ground-reflection | minimum effective height vs polarisation covered, HF ground loss not |
| 683 | Half-wave dipole length at 14.25 MHz (≈33 ft) | General G9B10 | 08 | C | 08/dipoles-and-monopoles | shortening factor |
| 684 | Half-wave dipole at 3.55 MHz (≈132 ft) | General G9B11 | 08 | C | 08/dipoles-and-monopoles |  |
| 685 | Quarter-wave monopole at 28.5 MHz (≈8 ft) | General G9B12 | 08 | C | 08/dipoles-and-monopoles |  |
| 686 | Fatter elements widen Yagi bandwidth | General G9C01 | 08 | P | 08/yagi-uda-and-log-periodic |  |
| 687 | Yagi driven element ≈ λ/2 | General G9C02 | 08 | C | 08/yagi-uda-and-log-periodic |  |
| 688 | Reflector longer, director shorter | General G9C03 | 08 | C | 08/yagi-uda-and-log-periodic |  |
| 689 | dBi = dBd + 2.15 | General G9C04 | 08 | C | 08/antenna-fundamentals |  |
| 690 | Longer boom + directors → more gain | General G9C05 | 08 | C | 08/yagi-uda-and-log-periodic |  |
| 691 | Front-to-back ratio meaning | General G9C07 | 08 | C | 08/yagi-uda-and-log-periodic |  |
| 692 | Main lobe meaning | General G9C08 | 08 | C | 08/antenna-fundamentals |  |
| 693 | Two stacked Yagis ≈ +3 dB | General G9C09 | 12 | P | 12/array-factor-linear-arrays | array gain N covered; stacking not discussed |
| 694 | Boom length, element count, spacing set gain/F-B/BW | General G9C10 | 08 | C | 08/yagi-uda-and-log-periodic |  |
| 695 | Hairpin match description | General G9C11 | 08 | C | 08/antenna-matching-and-baluns |  |
| 696 | Gamma match needs no insulated DE | General G9C12 | 08 | C | 08/antenna-matching-and-baluns |  |
| 697 | NVIS antenna: low horizontal dipole | General G9D01 | 09 | C | 09/ionospheric-hf-propagation | worked NVIS example |
| 698 | EFHW feed Z very high | General G9D02 | 08 | C | 08/dipoles-and-monopoles |  |
| 699 | Halo antenna pattern | General G9D03 | 08 | M | — |  |
| 700 | Antenna traps for multiband | General G9D04 | 08 | M | — | 08/wire-antennas-hf planned |
| 701 | Vertical stacking narrows elevation beam | General G9D05 | 12 | P | 12/array-factor-linear-arrays | derivable, not stated for Yagis |
| 702 | LPDA wide bandwidth | General G9D06 | 08 | C | 08/yagi-uda-and-log-periodic |  |
| 703 | LPDA geometry (τ scaling) | General G9D07 | 08 | C | 08/yagi-uda-and-log-periodic |  |
| 704 | Screwdriver antenna: variable base loading | General G9D08 | 08 | P | 08/dipoles-and-monopoles | loading covered; screwdriver not |
| 705 | Beverage use | General G9D09 | 08 | M | — |  |
| 706 | Small loop nulls on its axis | General G9D10 | 08 | C | 08/loop-antennas |  |
| 707 | Multiband antennas: poor harmonic rejection | General G9D11 | 08 | M | — |  |
| 708 | Inverted-V | General G9D12 | 08 | M | — |  |
| 709 | Higher sunspot number → higher usable HF | General G3A01 | 09 | P | 09/ionospheric-hf-propagation | foF2 range given; solar-cycle dependence not |
| 710 | SID disrupts lower HF more | General G3A02 | 09 | M | — |  |
| 711 | Flare UV/X-ray arrival (8 min) | General G3A03 | 09 | M | — |  |
| 712 | Worst DX bands at solar minimum (10–15 m) | General G3A04 | 09 | M | — |  |
| 713 | Solar flux index (10.7 cm) | General G3A05 | 09 | M | — |  |
| 714 | Geomagnetic storm definition | General G3A06 | 09 | M | — |  |
| 715 | 20 m daytime DX at any solar-cycle point | General G3A07 | 09 | M | — |  |
| 716 | Geomagnetic storm degrades high-latitude HF | General G3A08 | 09 | M | — |  |
| 717 | Aurora reflects VHF | General G3A09 | 09 | M | — |  |
| 718 | 27-day solar rotation cycle | General G3A10 | 09 | M | — |  |
| 719 | CME arrival time | General G3A11 | 09 | M | — |  |
| 720 | K-index | General G3A12 | 09 | M | — |  |
| 721 | A-index | General G3A13 | 09 | M | — |  |
| 722 | Coronal-hole particles disturb HF | General G3A14 | 09 | M | — |  |
| 723 | Short/long-path echo | General G3B01 | 09 | M | — |  |
| 724 | Factors affecting MUF (distance, time, season, sun) | General G3B02 | 09 | P | 09/ionospheric-hf-propagation | distance/geometry covered; diurnal/solar only qualitative |
| 725 | Least attenuation just below MUF (FOT) | General G3B03 | 09 | C | 09/ionospheric-hf-propagation |  |
| 726 | Reverse-beacon/PSKreporter to check propagation | General G3B04 | 09 | M | — |  |
| 727 | Between LUF and MUF: refracted back | General G3B05 | 09 | C | 09/ionospheric-hf-propagation |  |
| 728 | Below LUF: absorbed | General G3B06 | 09 | P | 09/ionospheric-hf-propagation | D absorption ∝1/f² covered; LUF not defined |
| 729 | Define LUF | General G3B07 | 09 | M | 09/ionospheric-hf-propagation |  |
| 730 | Define MUF | General G3B08 | 09 | C | 09/ionospheric-hf-propagation |  |
| 731 | Max F2 single-hop distance (≈2500 mi / 4000 km) | General G3B09 | 09 | C | 09/ionospheric-hf-propagation | ≤ ~3800 km stated |
| 732 | Max E single-hop distance (≈1200 mi) | General G3B10 | 09 | M | — |  |
| 733 | LUF > MUF → no skywave | General G3B11 | 09 | M | — |  |
| 734 | Low HF in summer: high atmospheric noise | General G3B12 | 09 | P | 07/thermal-noise-and-noise-temperature | HF external noise covered; seasonal not |
| 735 | Lowest region (D) | General G3C01 | 09 | C | 09/ionospheric-hf-propagation |  |
| 736 | Critical frequency meaning | General G3C02 | 09 | C | 09/ionospheric-hf-propagation |  |
| 737 | Why F2 skip is longest (highest layer) | General G3C03 | 09 | C | 09/ionospheric-hf-propagation | hop geometry |
| 738 | Critical angle definition | General G3C04 | 09 | P | 09/ionospheric-hf-propagation | secant law implies it; not named |
| 739 | D-region daytime absorption on low bands | General G3C05 | 09 | C | 09/ionospheric-hf-propagation |  |
| 740 | HF scatter flutter | General G3C06 | 09 | M | — |  |
| 741 | HF scatter multipath distortion | General G3C07 | 09 | M | — |  |
| 742 | Why scatter into skip zone is weak | General G3C08 | 09 | M | — |  |
| 743 | Scatter fills skip zone | General G3C09 | 09 | M | — |  |
| 744 | NVIS definition | General G3C10 | 09 | C | 09/ionospheric-hf-propagation |  |
| 745 | Most absorbing region below 10 MHz by day (D) | General G3C11 | 09 | C | 09/ionospheric-hf-propagation |  |
| 746 | VHF strength changes over a few feet (multipath) | Technician T3A01 | 09 | C | 09/multipath-fading-doppler |  |
| 747 | Vegetation absorbs UHF/microwave | Technician T3A02 | 09 | C | 09/atmospheric-rain-attenuation | ITU-R P.833 numbers |
| 748 | Horizontal polarisation for VHF/UHF weak-signal DX | Technician T3A03 | 08 | M | — | operating convention |
| 749 | Cross-polarisation reduces signal | Technician T3A04 | 09 | C | 09/polarization-mismatch-loss |  |
| 750 | Reflect around obstructions to reach a repeater | Technician T3A05 | 09 | P | 09/diffraction-knife-edge | reflection/diffraction physics, not the practice |
| 751 | "Picket fencing" = mobile multipath flutter | Technician T3A06 | 09 | P | 09/multipath-fading-doppler | level-crossing rate covered; term absent |
| 752 | Precipitation cuts microwave range | Technician T3A07 | 09 | C | 09/atmospheric-rain-attenuation |  |
| 753 | Ionospheric fading from multipath | Technician T3A08 | 09 | C | 09/multipath-fading-doppler; 09/ionospheric-hf-propagation |  |
| 754 | Skywave elliptically polarised → either antenna works | Technician T3A09 | 09 | P | 09/ionospheric-hf-propagation | Faraday rotation covered; consequence for HF not stated |
| 755 | Multipath raises data error rates | Technician T3A10 | 10 | C | 10/pulse-shaping-isi; 09/multipath-fading-doppler |  |
| 756 | Ionosphere reflects HF | Technician T3A11 | 09 | C | 09/ionospheric-hf-propagation |  |
| 757 | Fog/rain negligible at 28–50 MHz | Technician T3A12 | 09 | C | 09/atmospheric-rain-attenuation |  |
| 758 | E ⟂ H in a radio wave | Technician T3B01 | 02 | C | 02/wave-equation-plane-waves-polarization |  |
| 759 | Polarisation = E-field orientation | Technician T3B02 | 02 | C | 02/wave-equation-plane-waves-polarization |  |
| 760 | Components of a radio wave | Technician T3B03 | 02 | C | 02/wave-equation-plane-waves-polarization |  |
| 761 | Velocity in free space = c | Technician T3B04 | 02 | C | 02/electromagnetic-units-and-constants |  |
| 762 | λ shortens as f rises | Technician T3B05 | 02 | C | 02/wave-equation-plane-waves-polarization |  |
| 763 | λ(m) ≈ 300/f(MHz) | Technician T3B06 | 02 | C | 02/electromagnetic-units-and-constants |  |
| 764 | Bands named by wavelength | Technician T3B07 | 19 | P | 19/spectrum-allocation-ism-bands |  |
| 765 | VHF = 30–300 MHz | Technician T3B08 | 19 | P | 19/spectrum-allocation-ism-bands | band-designation table absent |
| 766 | UHF = 300–3000 MHz | Technician T3B09 | 19 | P | 19/spectrum-allocation-ism-bands |  |
| 767 | HF = 3–30 MHz | Technician T3B10 | 09 | C | 09/ionospheric-hf-propagation |  |
| 768 | c ≈ 3×10⁸ m/s | Technician T3B11 | 02 | C | 02/electromagnetic-units-and-constants |  |
| 769 | All frequencies travel at c in vacuum | Technician T3B12 | 02 | C | 02/electromagnetic-units-and-constants |  |
| 770 | UHF not ionospheric → horizon-limited | Technician T3C01 | 09 | C | 09/ionospheric-hf-propagation; 09/fresnel-zones-los-radio-horizon |  |
| 771 | HF long-distance skywave common | Technician T3C02 | 09 | C | 09/ionospheric-hf-propagation |  |
| 772 | Auroral backscatter raspy sound | Technician T3C03 | 09 | M | — |  |
| 773 | Sporadic E beyond horizon on 10/6/2 m | Technician T3C04 | 09 | C | 09/ionospheric-hf-propagation |  |
| 774 | Knife-edge diffraction past obstructions | Technician T3C05 | 09 | C | 09/diffraction-knife-edge |  |
| 775 | Tropospheric ducting ~300 mi | Technician T3C06 | 09 | P | 09/fresnel-zones-los-radio-horizon | ducting described; typical ranges absent |
| 776 | Meteor scatter band (6 m) | Technician T3C07 | 09 | M | — |  |
| 777 | Ducting caused by temperature inversions | Technician T3C08 | 09 | C | 09/fresnel-zones-los-radio-horizon | anomalous-propagation paragraph |
| 778 | 10 m F-region DX timing | Technician T3C09 | 09 | M | — |  |
| 779 | 6/10 m F-region at solar peak | Technician T3C10 | 09 | M | — |  |
| 780 | Refraction extends radio horizon | Technician T3C11 | 09 | C | 09/fresnel-zones-los-radio-horizon |  |
| 781 | Supply rating for a 50 W mobile rig (13.8 V, 12 A) | Technician T4A01 | 05 | P | 05/power-supplies-for-rf-and-analog | efficiency/current arithmetic available |
| 782 | Choose SWR meter by frequency and power | Technician T4A02 | 17 | C | 17/rf-power-measurement |  |
| 783 | Short heavy DC leads to limit TX voltage drop | Technician T4A03 | 05 | C | 05/power-supplies-for-rf-and-analog | droop worked for 2 W module |
| 784 | FT8 audio interface wiring | Technician T4A04 | 14 | M | — | OOS: operating |
| 785 | RF power meter in the feed line | Technician T4A05 | 17 | C | 17/rf-power-measurement |  |
| 786 | Computer-radio interface signals | Technician T4A06 | 14 | M | — | OOS: operating |
| 787 | Computer line-in to radio speaker | Technician T4A07 | 14 | M | — | OOS: operating |
| 788 | Flat copper strap preferred for RF bonding | Technician T4A08 | 13 | P | 13/grounding-and-return-paths | inductance vs geometry covered; strap not |
| 789 | Battery runtime = Ah / current | Technician T4A09 | 05 | P | 05/power-supplies-for-rf-and-analog |  |
| 790 | Digital-voice hotspot | Technician T4A10 | 14 | M | — | OOS: operating |
| 791 | Mobile negative lead to battery chassis ground | Technician T4A11 | 05 | M | — |  |
| 792 | Electronic keyer | Technician T4A12 | 10 | M | — | OOS: operating |
| 793 | Excess mic gain distorts SSB | Technician T4B01 | 10 | M | — |  |
| 794 | Enter frequency via keypad/VFO | Technician T4B02 | 14 | M | — | OOS: operating |
| 795 | Squelch setting for weak FM | Technician T4B03 | 14 | M | — | OOS: operating |
| 796 | Off-frequency FM sounds distorted | Technician T4B04 | 10 | P | 10/analog-modulation-am-fm-pm-ssb |  |
| 797 | Scanning function | Technician T4B05 | 14 | M | — | OOS: operating |
| 798 | RIT/clarifier for SSB pitch | Technician T4B06 | 14 | M | — | OOS: operating |
| 799 | DMR code plug | Technician T4B07 | 19 | M | — | OOS: operating |
| 800 | Selectable RX bandwidth reduces noise | Technician T4B08 | 07 | C | 07/sensitivity-and-mds |  |
| 801 | DMR talkgroup selection | Technician T4B09 | 19 | M | — | OOS: operating |
| 802 | Best SSB filter width (2.4 kHz) | Technician T4B10 | 07 | P | 10/analog-modulation-am-fm-pm-ssb |  |
| 803 | D-STAR needs call sign programmed | Technician T4B11 | 19 | M | — | OOS: operating |
| 804 | Unit of current (ampere) | Technician T5A01 | 01 | P | — | no DC/units primer |
| 805 | Unit of power (watt) | Technician T5A02 | 01 | P | — | no DC/units primer |
| 806 | Flow of electrons = current | Technician T5A03 | 01 | P | — | no DC/units primer |
| 807 | Cycles per second = frequency | Technician T5A04 | 00 | C | 00/complex-numbers-and-phasors |  |
| 808 | Voltage difference drives current | Technician T5A05 | 01 | P | — | no DC/units primer |
| 809 | Unit of frequency (Hz) | Technician T5A06 | 00 | C | 00/complex-numbers-and-phasors |  |
| 810 | Why metals conduct (free electrons) | Technician T5A07 | 02 | P | 02/maxwells-equations; 02/skin-effect-conductor-loss-roughness | σ values given; free-electron picture absent |
| 811 | Good insulator (glass) | Technician T5A08 | 02 | C | 02/dielectrics-permittivity-loss-tangent |  |
| 812 | Define alternating current | Technician T5A09 | 00 | C | 00/complex-numbers-and-phasors |  |
| 813 | Power = rate of energy use | Technician T5A10 | 01 | C | 01/energy-storage-and-reactive-power |  |
| 814 | Resistance opposes DC, AC and RF | Technician T5A11 | 01 | C | 01/lumped-elements-impedance-admittance; 04/resistors-at-rf |  |
| 815 | 1.5 A in mA | Technician T5B01 | 00 | P | — | no SI-prefix table |
| 816 | 1 500 000 Hz = 1500 kHz | Technician T5B02 | 00 | P | — | no SI-prefix table |
| 817 | kilovolt | Technician T5B03 | 00 | P | — | no SI-prefix table |
| 818 | microvolt | Technician T5B04 | 00 | P | — | no SI-prefix table |
| 819 | 500 mW = 0.5 W | Technician T5B05 | 00 | P | — | no SI-prefix table |
| 820 | 3000 mA = 3 A | Technician T5B06 | 00 | P | — | no SI-prefix table |
| 821 | 3.525 MHz = 3525 kHz | Technician T5B07 | 00 | P | — | no SI-prefix table |
| 822 | 10⁶ pF = 1 µF | Technician T5B08 | 00 | P | — | no SI-prefix table |
| 823 | 5 → 10 W = +3 dB | Technician T5B09 | 00 | C | 00/decibels-and-log-units |  |
| 824 | 12 → 3 W = −6 dB | Technician T5B10 | 00 | C | 00/decibels-and-log-units |  |
| 825 | 20 → 200 W = +10 dB | Technician T5B11 | 00 | C | 00/decibels-and-log-units |  |
| 826 | 28 400 kHz = 28.4 MHz | Technician T5B12 | 00 | P | — | no SI-prefix table |
| 827 | 2425 MHz = 2.425 GHz | Technician T5B13 | 00 | P | — | no SI-prefix table |
| 828 | Energy in E-field = capacitance | Technician T5C01 | 02 | C | 02/inductance-capacitance-from-fields |  |
| 829 | Unit of capacitance (F) | Technician T5C02 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 830 | Energy in B-field = inductance | Technician T5C03 | 02 | C | 02/inductance-capacitance-from-fields |  |
| 831 | Unit of inductance (H) | Technician T5C04 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 832 | Unit of impedance (Ω) | Technician T5C05 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 833 | kHz abbreviation | Technician T5C06 | 00 | P | — | no SI-prefix table |
| 834 | MHz abbreviation | Technician T5C07 | 00 | P | — | no SI-prefix table |
| 835 | DC power P = I·E | Technician T5C08 | 01 | P | 01/network-theorems-max-power-transfer | complex power ½VI* given; DC form implicit |
| 836 | 13.8 V × 10 A = 138 W | Technician T5C09 | 01 | P | 01/network-theorems-max-power-transfer |  |
| 837 | 12 V × 2.5 A = 30 W | Technician T5C10 | 01 | P | 01/network-theorems-max-power-transfer |  |
| 838 | Current for 120 W at 12 V (10 A) | Technician T5C11 | 01 | P | 01/network-theorems-max-power-transfer |  |
| 839 | Impedance = opposition to AC | Technician T5C12 | 01 | C | 01/lumped-elements-impedance-admittance |  |
| 840 | Ohm's-law arithmetic (I=E/R) | Technician T5D01 | 01 | P | 01/lumped-elements-impedance-admittance | Z = V/I defined; DC Ohm's law not stated |
| 841 | Ohm's-law arithmetic (E=IR) | Technician T5D02 | 01 | P | 01/lumped-elements-impedance-admittance | Z = V/I defined; DC Ohm's law not stated |
| 842 | Ohm's-law arithmetic (R=E/I) | Technician T5D03 | 01 | P | 01/lumped-elements-impedance-admittance | Z = V/I defined; DC Ohm's law not stated |
| 843 | Ohm's-law arithmetic (90 V/3 A) | Technician T5D04 | 01 | P | 01/lumped-elements-impedance-admittance | Z = V/I defined; DC Ohm's law not stated |
| 844 | Ohm's-law arithmetic (12 V/1.5 A) | Technician T5D05 | 01 | P | 01/lumped-elements-impedance-admittance | Z = V/I defined; DC Ohm's law not stated |
| 845 | Ohm's-law arithmetic (12 V/4 A) | Technician T5D06 | 01 | P | 01/lumped-elements-impedance-admittance | Z = V/I defined; DC Ohm's law not stated |
| 846 | Ohm's-law arithmetic (120 V/80 Ω) | Technician T5D07 | 01 | P | 01/lumped-elements-impedance-admittance | Z = V/I defined; DC Ohm's law not stated |
| 847 | Ohm's-law arithmetic (200 V/100 Ω) | Technician T5D08 | 01 | P | 01/lumped-elements-impedance-admittance | Z = V/I defined; DC Ohm's law not stated |
| 848 | Ohm's-law arithmetic (240 V/24 Ω) | Technician T5D09 | 01 | P | 01/lumped-elements-impedance-admittance | Z = V/I defined; DC Ohm's law not stated |
| 849 | Ohm's-law arithmetic (2 Ω×0.5 A) | Technician T5D10 | 01 | P | 01/lumped-elements-impedance-admittance | Z = V/I defined; DC Ohm's law not stated |
| 850 | Ohm's-law arithmetic (10 Ω×1 A) | Technician T5D11 | 01 | P | 01/lumped-elements-impedance-admittance | Z = V/I defined; DC Ohm's law not stated |
| 851 | Ohm's-law arithmetic (10 Ω×2 A) | Technician T5D12 | 01 | P | 01/lumped-elements-impedance-admittance | Z = V/I defined; DC Ohm's law not stated |
| 852 | Series circuit: same current (KCL) | Technician T5D13 | 01 | C | 01/network-theorems-max-power-transfer |  |
| 853 | Parallel circuit: same voltage (KVL) | Technician T5D14 | 01 | C | 01/network-theorems-max-power-transfer |  |
| 854 | Component opposing DC current (resistor) | Technician T6A01 | 04 | C | 04/resistors-at-rf |  |
| 855 | Potentiometer as volume control | Technician T6A02 | 04 | M | — | basic components primer absent |
| 856 | Potentiometer controls resistance | Technician T6A03 | 04 | M | — |  |
| 857 | Capacitor stores E-field energy | Technician T6A04 | 04 | C | 02/inductance-capacitance-from-fields; 04/capacitors-at-rf-mlcc |  |
| 858 | Capacitor = conductors separated by insulator | Technician T6A05 | 04 | C | 04/capacitors-at-rf-mlcc |  |
| 859 | Inductor stores B-field energy | Technician T6A06 | 04 | C | 02/inductance-capacitance-from-fields; 04/inductors-at-rf |  |
| 860 | Inductor = coil of wire | Technician T6A07 | 04 | C | 04/inductors-at-rf |  |
| 861 | SPDT switch function | Technician T6A08 | 06 | P | 06/rf-switches-attenuators-limiters | RF SPDT covered; generic switch poles/throws not defined |
| 862 | SPST symbol | Technician T6A09 | 06 | M | — | OOS; symbols absent |
| 863 | Rechargeable chemistries (NiMH, Li-ion, lead-acid) | Technician T6A10 | 05 | P | 05/power-supplies-for-rf-and-analog | LiPo only |
| 864 | Non-rechargeable chemistry (carbon-zinc) | Technician T6A11 | 05 | M | — |  |
| 865 | Forward drop differs between diode types | Technician T6B01 | 05 | C | 05/diodes-schottky-pin-varactor |  |
| 866 | Diode conducts one way | Technician T6B02 | 05 | C | 05/diodes-schottky-pin-varactor |  |
| 867 | Transistor as switch | Technician T6B03 | 05 | C | 05/fets-mosfet-jfet-gaas-gan |  |
| 868 | Transistor has three semiconductor regions | Technician T6B04 | 05 | C | 05/bjt-fundamentals-small-signal |  |
| 869 | Gate/drain/source = FET | Technician T6B05 | 05 | C | 05/fets-mosfet-jfet-gaas-gan |  |
| 870 | Diode cathode stripe marking | Technician T6B06 | 05 | M | — |  |
| 871 | LED emits with forward current | Technician T6B07 | 05 | M | — | OOS |
| 872 | FET abbreviation | Technician T6B08 | 05 | C | 05/fets-mosfet-jfet-gaas-gan |  |
| 873 | Diode electrodes (anode, cathode) | Technician T6B09 | 05 | C | 05/diodes-schottky-pin-varactor |  |
| 874 | Transistor provides power gain | Technician T6B10 | 05 | C | 05/amplifier-topologies |  |
| 875 | Meaning of amplifier gain (V, I, P) | Technician T6B11 | 05 | C | 06/lna-design; 05/amplifier-topologies |  |
| 876 | BJT electrodes | Technician T6B12 | 05 | C | 05/bjt-fundamentals-small-signal |  |
| 877 | Electrical diagram = schematic | Technician T6C01 | 05 | M | — | OOS; schematic conventions absent |
| 878 | Identify resistor symbol | Technician T6C02 | 05 | M | — | OOS; symbols absent |
| 879 | Identify transistor symbol | Technician T6C03 | 05 | M | — | OOS |
| 880 | Identify lamp symbol | Technician T6C04 | 05 | M | — | OOS |
| 881 | Identify battery symbol | Technician T6C05 | 05 | M | — | OOS |
| 882 | Identify capacitor symbol | Technician T6C06 | 05 | M | — | OOS |
| 883 | Identify LED symbol | Technician T6C07 | 05 | M | — | OOS |
| 884 | Identify variable-resistor symbol | Technician T6C08 | 05 | M | — | OOS |
| 885 | Identify transformer symbol | Technician T6C09 | 05 | M | — | OOS |
| 886 | Identify variable-inductor symbol | Technician T6C10 | 05 | M | — | OOS |
| 887 | Identify antenna symbol | Technician T6C11 | 05 | M | — | OOS |
| 888 | What schematics represent (connections) | Technician T6C12 | 05 | M | — | OOS |
| 889 | Rectifier converts AC to pulsating DC | Technician T6D01 | 05 | M | — | power rectifiers absent (detector rectification covered) |
| 890 | What a relay is | Technician T6D02 | 05 | M | — |  |
| 891 | Shielded wire prevents coupling | Technician T6D03 | 13 | C | 13/emc-emi-fundamentals; 13/shielding-and-isolation | shielding theory; cable shielding practice (13/shielding page planned) |
| 892 | Meter shows a numeric value | Technician T6D04 | 17 | M | — |  |
| 893 | Regulator controls supply voltage | Technician T6D05 | 05 | C | 05/power-supplies-for-rf-and-analog |  |
| 894 | Transformer steps AC down | Technician T6D06 | 01 | C | 01/transformers-coupled-inductors |  |
| 895 | LED as indicator | Technician T6D07 | 05 | M | — | OOS |
| 896 | L + C make a resonant circuit | Technician T6D08 | 01 | C | 01/resonance-and-q |  |
| 897 | Integrated circuit definition | Technician T6D09 | 05 | M | — |  |
| 898 | Transistor controls current flow (figure) | Technician T6D10 | 05 | P | 05/bjt-fundamentals-small-signal |  |
| 899 | Tuned circuit = L and C | Technician T6D11 | 01 | C | 01/resonance-and-q |  |
| 900 | Sensitivity definition | Technician T7A01 | 07 | C | 07/sensitivity-and-mds |  |
| 901 | What a transceiver is | Technician T7A02 | 06 | C | 06/transmitter-architectures; 18/rf-transceiver-ics |  |
| 902 | Mixer converts frequency | Technician T7A03 | 06 | C | 06/mixers |  |
| 903 | Selectivity definition | Technician T7A04 | 06 | C | 06/receiver-architectures; 07/dynamic-range-sfdr-blocking |  |
| 904 | Oscillator generates a frequency | Technician T7A05 | 05 | C | 05/oscillators |  |
| 905 | Transverter | Technician T7A06 | 06 | M | — |  |
| 906 | PTT input | Technician T7A07 | 06 | M | — | OOS: operating |
| 907 | Modulation definition | Technician T7A08 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 908 | SSB vs FM mode switch on VHF PA (linear vs class C bias) | Technician T7A09 | 06 | P | 06/power-amplifiers | class/linearity covered; switch practice not |
| 909 | Add an RF power amplifier for more output | Technician T7A10 | 06 | C | 06/power-amplifiers |  |
| 910 | VFO sets TX/RX frequency | Technician T7A11 | 06 | C | 06/vco-and-pll-synthesizers |  |
| 911 | Over-deviation: speak further from mic | Technician T7B01 | 10 | M | — |  |
| 912 | Broadcast radio receives ham TX (front-end overload) | Technician T7B02 | 07 | P | 07/dynamic-range-sfdr-blocking | blocking physics; consumer RFI not |
| 913 | RFI causes: overload, harmonics, spurs | Technician T7B03 | 13 | P | 06/power-amplifiers; 07/dynamic-range-sfdr-blocking |  |
| 914 | Low output from high SWR (PA protection/foldback) | Technician T7B04 | 06 | C | 06/power-amplifiers; 03/reflections-vswr-return-loss-mismatch |  |
| 915 | Filter at victim receiver's antenna input | Technician T7B05 | 06 | P | 06/rf-filters-lc-saw-baw-cavity-microstrip |  |
| 916 | Neighbour RFI complaint procedure | Technician T7B06 | 19 | M | — | OOS: operating |
| 917 | Band-reject filter against a nearby FM broadcaster | Technician T7B07 | 06 | P | 06/rf-filters-lc-saw-baw-cavity-microstrip | notch responses via elliptic zeros; practice absent |
| 918 | Neighbour's device interfering: steps | Technician T7B08 | 19 | M | — | OOS: operating |
| 919 | Cable-TV RFI: check coax connectors | Technician T7B09 | 13 | M | — |  |
| 920 | Distorted audio through repeater: causes | Technician T7B10 | 10 | M | — | OOS: operating |
| 921 | Ferrite on mic cable stops RF feedback | Technician T7B11 | 13 | C | 04/ferrites-and-beads; 08/antenna-matching-and-baluns |  |
| 922 | Purpose of a dummy load | Technician T7C01 | 17 | C | 19/lab-safety-esd-high-power; 17/rf-bring-up-debug-playbook |  |
| 923 | Check antenna resonance with an analyzer | Technician T7C02 | 17 | C | 08/antenna-measurement; 17/nanovna-librevna-practical |  |
| 924 | Dummy load = non-inductive 50 Ω on heat sink | Technician T7C03 | 04 | C | 04/resistors-at-rf |  |
| 925 | Perfect match = 1:1 | Technician T7C04 | 03 | C | 03/reflections-vswr-return-loss-mismatch |  |
| 926 | PA power foldback on high SWR (protection) | Technician T7C05 | 06 | P | 06/power-amplifiers | ruggedness ratings covered; foldback not |
| 927 | 4:1 = mismatch | Technician T7C06 | 03 | C | 03/reflections-vswr-return-loss-mismatch |  |
| 928 | Feed-line loss becomes heat | Technician T7C07 | 03 | C | 03/coax-and-cables |  |
| 929 | Directional wattmeter for SWR | Technician T7C08 | 17 | C | 17/rf-power-measurement |  |
| 930 | Moisture causes coax failure | Technician T7C09 | 03 | C | 03/coax-and-cables | water ingress raises loss permanently |
| 931 | UV-resistant jacket | Technician T7C10 | 03 | C | 03/coax-and-cables | UV-rated jackets |
| 932 | Foam coax has lower loss | Technician T7C11 | 03 | C | 03/coax-and-cables |  |
| 933 | Voltmeter measures potential | Technician T7D01 | 17 | M | — | basic meters absent |
| 934 | Voltmeter in parallel | Technician T7D02 | 17 | M | — |  |
| 935 | Ammeter in series | Technician T7D03 | 17 | M | — |  |
| 936 | Ammeter measures current | Technician T7D04 | 17 | M | — |  |
| 937 | How an ohmmeter works | Technician T7D05 | 17 | M | — |  |
| 938 | Damage from measuring V on Ω range | Technician T7D06 | 17 | M | — |  |
| 939 | Multimeter measures V and R | Technician T7D07 | 17 | M | — |  |
| 940 | Don't use acid-core solder | Technician T7D08 | 20 | M | — | assembly/soldering practice absent |
| 941 | Cold solder joint appearance | Technician T7D09 | 20 | M | — |  |
| 942 | Ohmmeter on a large discharged cap (rising R) | Technician T7D10 | 17 | M | — |  |
| 943 | Circuit unpowered for in-circuit Ω | Technician T7D11 | 17 | M | — |  |
| 944 | SSB is a form of AM | Technician T8A01 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 945 | VHF packet uses FM/PM (AFSK) | Technician T8A02 | 10 | C | 10/analog-modulation-am-fm-pm-ssb | APRS example |
| 946 | SSB for VHF/UHF weak-signal voice | Technician T8A03 | 10 | M | — | OOS: operating convention |
| 947 | Repeaters use FM/PM | Technician T8A04 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 948 | CW narrowest | Technician T8A05 | 10 | P | 10/analog-modulation-am-fm-pm-ssb | CW not treated |
| 949 | USB convention on 10 m/VHF/UHF | Technician T8A06 | 10 | M | — | OOS: operating convention |
| 950 | SSB narrower than FM | Technician T8A07 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 951 | SSB voice ≈ 3 kHz | Technician T8A08 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 952 | NBFM voice 10–15 kHz | Technician T8A09 | 10 | C | 10/analog-modulation-am-fm-pm-ssb | Carson 11–16 kHz |
| 953 | Analog fast-scan TV ≈ 6 MHz | Technician T8A10 | 10 | M | — |  |
| 954 | CW bandwidth ≈ 150 Hz | Technician T8A11 | 10 | M | — |  |
| 955 | FM capture: only one signal received | Technician T8A12 | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 956 | Satellite beacon telemetry (health/status) | Technician T8B01 | 15 | P | 15/rocket-telemetry-radio-design | telemetry content covered for rockets |
| 957 | Excess uplink ERP blocks transponder | Technician T8B02 | 19 | M | — |  |
| 958 | Satellite tracking program outputs | Technician T8B03 | 09 | M | — | orbital mechanics absent |
| 959 | Satellite modes (SSB, FM, CW/data) | Technician T8B04 | 10 | M | — |  |
| 960 | Satellite beacon definition | Technician T8B05 | 15 | P | 15/lorawan-vs-raw-lora | TinyGS/Norby mentioned |
| 961 | Keplerian elements as tracking input | Technician T8B06 | 09 | M | — |  |
| 962 | Satellite Doppler shift | Technician T8B07 | 09 | C | 09/multipath-fading-doppler; 10/synchronization-carrier-timing |  |
| 963 | U/V mode meaning | Technician T8B08 | 19 | M | — |  |
| 964 | Spin fading from rotating antennas | Technician T8B09 | 08 | C | 08/antennas-on-rockets; 08/antenna-polarization-and-circular-polarization | rocket-roll equivalent derived |
| 965 | LEO ≈ 100 min orbit | Technician T8B10 | 09 | M | — |  |
| 966 | Anyone may receive amateur satellite telemetry | Technician T8B11 | 19 | M | — |  |
| 967 | Uplink level ≈ beacon strength on downlink | Technician T8B12 | 19 | M | — |  |
| 968 | Direction finding locates interference | Technician T8C01 | 12 | C | 12/adaptive-beamforming-doa; 12/diy-phased-array-projects |  |
| 969 | Directional antenna for fox hunting | Technician T8C02 | 08 | C | 08/loop-antennas; 12/diy-phased-array-projects | rocket recovery DF |
| 970 | Contesting | Technician T8C03 | 19 | M | — | OOS: operating |
| 971 | Contest exchange practice | Technician T8C04 | 19 | M | — | OOS: operating |
| 972 | Grid locator | Technician T8C05 | 19 | M | — | OOS: operating |
| 973 | IRLP access via DTMF | Technician T8C06 | 19 | M | — | OOS: operating |
| 974 | VoIP definition | Technician T8C07 | 10 | M | — | OOS |
| 975 | IRLP definition | Technician T8C08 | 19 | M | — | OOS: operating |
| 976 | EchoLink | Technician T8C09 | 19 | M | — | OOS: operating |
| 977 | EchoLink registration | Technician T8C10 | 19 | M | — | OOS: operating |
| 978 | Internet gateway station | Technician T8C11 | 19 | M | — | OOS: operating |
| 979 | Digital modes (packet, 802.11, FT8) | Technician T8D01 | 10 | P | 10/ofdm; 10/packet-framing-protocols | 802.11 covered |
| 980 | FT8 low-SNR mode | Technician T8D02 | 10 | M | — |  |
| 981 | APRS data types | Technician T8D03 | 10 | P | 10/analog-modulation-am-fm-pm-ssb | APRS physical layer only |
| 982 | NTSC | Technician T8D04 | 10 | M | — |  |
| 983 | APRS tactical map use | Technician T8D05 | 10 | M | — |  |
| 984 | PSK = phase shift keying | Technician T8D06 | 10 | C | 10/digital-modulation-psk-qam-fsk |  |
| 985 | DMR = 2-slot TDMA in 12.5 kHz | Technician T8D07 | 10 | M | — |  |
| 986 | Packet radio has header + checksum | Technician T8D08 | 10 | C | 10/packet-framing-protocols |  |
| 987 | CW = Morse code | Technician T8D09 | 10 | M | — |  |
| 988 | WSJT-X supports EME/meteor/beacons | Technician T8D10 | 10 | M | — |  |
| 989 | Role of ARQ | Technician T8D11 | 10 | C | 10/packet-framing-protocols |  |
| 990 | Amateur mesh on modified Wi-Fi gear | Technician T8D12 | 10 | M | — |  |
| 991 | Beam antenna definition | Technician T9A01 | 08 | C | 08/yagi-uda-and-log-periodic |  |
| 992 | Inductive loading lengthens electrically | Technician T9A02 | 08 | C | 08/dipoles-and-monopoles |  |
| 993 | Antenna polarisation = E-field orientation | Technician T9A03 | 08 | C | 08/antenna-polarization-and-circular-polarization |  |
| 994 | Rubber duck is inefficient | Technician T9A04 | 08 | C | 08/small-antenna-limits; 08/dipoles-and-monopoles |  |
| 995 | Shortening raises resonant frequency | Technician T9A05 | 08 | C | 08/dipoles-and-monopoles |  |
| 996 | Greatest gain among listed (Yagi) | Technician T9A06 | 08 | C | 08/yagi-uda-and-log-periodic |  |
| 997 | Vehicle body shields a handheld | Technician T9A07 | 08 | P | 08/antennas-on-rockets; 02/boundary-conditions-reflection-refraction | conductive-airframe analogue |
| 998 | 19-inch 2 m vertical = λ/4 | Technician T9A08 | 08 | C | 08/dipoles-and-monopoles |  |
| 999 | 5/8-λ whip has more gain (over ground) | Technician T9A09 | 08 | C | 08/dipoles-and-monopoles | myth-box states the conditions |
| 1000 | Dipole max radiation broadside | Technician T9A10 | 08 | C | 08/dipoles-and-monopoles |  |
| 1001 | Antenna gain definition | Technician T9A11 | 08 | C | 08/antenna-fundamentals |  |
| 1002 | Tape outdoor connectors (PL-259, BNC, N) | Technician T9B01 | 18 | C | 03/coax-and-cables; 20/ground-station-tracking-yagi | self-amalgamating tape |
| 1003 | Common coax impedance (50 Ω) | Technician T9B02 | 03 | C | 03/coax-and-cables |  |
| 1004 | Why coax is the default feed line | Technician T9B03 | 03 | C | 03/coax-and-cables |  |
| 1005 | Antenna tuner function | Technician T9B04 | 03 | P | 03/reflections-vswr-return-loss-mismatch | see G4A06 |
| 1006 | Coax loss rises with f | Technician T9B05 | 03 | C | 03/coax-and-cables |  |
| 1007 | Type N suitable above 400 MHz | Technician T9B06 | 18 | C | 18/connectors-and-cables-parts |  |
| 1008 | PL-259 for HF/VHF | Technician T9B07 | 18 | M | — | UHF-series connector absent |
| 1009 | Loss sources: water, SWR, connectors | Technician T9B08 | 03 | C | 03/coax-and-cables; 03/reflections-vswr-return-loss-mismatch |  |
| 1010 | Erratic SWR from loose connection | Technician T9B09 | 03 | P | 17/rf-bring-up-debug-playbook |  |
| 1011 | RG-213 less loss than RG-58 | Technician T9B10 | 03 | P | 03/coax-and-cables | RG-213 not tabulated (LMR-400 is) |
| 1012 | Lowest-loss line: air hardline | Technician T9B11 | 03 | P | 03/coax-and-cables | air-line loss optimum derived, hardline not listed |
| 1013 | SWR definition | Technician T9B12 | 03 | C | 03/reflections-vswr-return-loss-mismatch |  |
| 1014 | Design a 30 dBm PA: choose load impedance; when to power-combine | Interview (RFInsights RFIC) | 06 | C | 06/power-amplifiers; 06/couplers-dividers-combiners | Ropt = (VDD−Vk)²/2P, combining efficiency |
| 1015 | RF-compatible ESD protection design | Interview (RFInsights RFIC) | 05 | C | 13/emc-emi-fundamentals | ESD on RF ports section |
| 1016 | Input impedance into an inductively degenerated gate (Re = ωT·Ls) | Interview (RFInsights RFIC) | 06 | C | 06/lna-design |  |
| 1017 | Overall Gm of a matched source-degenerated LNA (ωT/2ω0Rs) | Interview (RFInsights RFIC) | 06 | C | 06/lna-design | derived with Q_in |
| 1018 | Ways to create a real input resistance in a CS stage | Interview (RFInsights RFIC) | 06 | C | 06/lna-design; 05/amplifier-topologies | degeneration, shunt R, feedback, CG |
| 1019 | How device width/current trade noise in CMOS LNA (power-constrained optimum) | Interview (RFInsights RFIC) | 06 | P | 06/lna-design | γ, ωT and Fmin shown; power-constrained W_opt method absent |
| 1020 | Derive NF of a common-source LNA | Interview (RFInsights RFIC) | 06 | C | 06/lna-design; 07/noise-figure-and-friis | F−1 = γ gd0 Rs (ω0/ωT)² derived |
| 1021 | Bandgap / PTAT reference design | Interview (RFInsights RFIC) | 05 | P | 05/power-supplies-for-rf-and-analog; 05/bjt-fundamentals-small-signal | ΔVBE PTAT and bandgap noise mentioned; bandgap circuit not derived |
| 1022 | Improve current-mirror matching (area, overdrive, common centroid) | Interview (RFInsights RFIC) | 05 | M | — | device mismatch (Pelgrom) absent |
| 1023 | How to match Vth between transistors | Interview (RFInsights RFIC) | 05 | M | — |  |
| 1024 | Vth dependence on channel length (short-channel/reverse-short-channel effects) | Interview (RFInsights RFIC) | 05 | M | — | short-channel only for Id/fT |
| 1025 | Does raising bias current raise or lower CMOS intrinsic gain? | Interview (RFInsights RFIC) | 05 | P | 05/fets-mosfet-jfet-gaas-gan | gm/ID covered; gm·ro vs ID trend not stated |
| 1026 | Design and compensate a two-stage op-amp | Interview (RFInsights RFIC) | 05 | C | 05/feedback-and-stability |  |
| 1027 | Why Miller compensation splits poles; why a nulling resistor | Interview (RFInsights RFIC) | 05 | C | 05/feedback-and-stability | RHP zero at gm2/Cc |
| 1028 | CS input impedance with and without Cgd (Miller) | Interview (RFInsights RFIC) | 05 | C | 05/bjt-fundamentals-small-signal; 05/amplifier-topologies |  |
| 1029 | Raise gain/output impedance (cascode, stacking, gain-boosting) | Interview (RFInsights RFIC) | 05 | P | 05/amplifier-topologies | OOS; cascode covered; gain boosting/regulated cascode absent |
| 1030 | Cascaded IIP3 and when the formula fails | Interview (RFInsights RFIC) | 07 | C | 07/nonlinearity-p1db-ip3-intermod | coherent worst case; memory/reactive interstage caveat |
| 1031 | IM3 change when only one tone's level rises (A1²A2) | Interview (RFInsights RFIC) | 07 | P | 07/nonlinearity-p1db-ip3-intermod | asymmetric-tone case not worked |
| 1032 | Relation between IIP3 and HD3 (IM3 = HD3 + 9.54 dB) | Interview (RFInsights RFIC) | 07 | C | 07/nonlinearity-p1db-ip3-intermod |  |
| 1033 | NF of two cascaded amplifiers (Friis) | Interview (RFInsights RFIC) | 07 | C | 07/noise-figure-and-friis |  |
| 1034 | Order two fixed amplifiers to minimise noise (noise measure) | Interview (RFInsights RFIC) | 07 | C | 06/lna-design |  |
| 1035 | How AM-AM/AM-PM degrade EVM | Interview (RFInsights RFIC) | 06 | P | 06/power-amplifiers | Rapp+AM/PM EVM simulation; no analytic EVM mapping |
| 1036 | PA memory effects and how to detect them | Interview (RFInsights RFIC) | 06 | P | 06/power-amplifiers; 07/nonlinearity-p1db-ip3-intermod | IM3 vs tone spacing noted; memory models absent |
| 1037 | PA biasing and thermal runaway | Interview (RFInsights RFIC) | 06 | P | 06/amplifier-stability-and-biasing; 05/bjt-fundamentals-small-signal | BJT tempco/runaway risk noted; ballasting/PA bias control absent |
| 1038 | Which CMOS breakdown (gate–drain vs drain–source) limits and why | Interview (RFInsights RFIC) | 05 | M | — | oxide breakdown/hot-carrier limits absent |
| 1039 | Which load impedance for a PAPR signal with varying envelope | Interview (RFInsights RFIC) | 06 | C | 06/power-amplifiers | load-pull contours, back-off efficiency |
| 1040 | Active load-pull: what and why | Interview (RFInsights RFIC) | 06 | P | 06/power-amplifiers | passive load-pull contours only |
| 1041 | Cascode LNA sizing: input device, Lg, Ls, cascode device, effect on NF | Interview (RFInsights RFIC) | 06 | P | 06/lna-design | degeneration design covered; cascode-device noise/sizing not |
| 1042 | On-chip inductors: current crowding, symmetric/differential inductors | Interview (RFInsights RFIC) | 04 | M | — | integrated passives absent |
| 1043 | CS output impedance with a high-Z gate and Cgd (Cgd feedback at HF) | Interview (RFInsights RFIC) | 05 | P | 05/amplifier-topologies |  |
| 1044 | Resonance, Q and BW of a parallel RLC | Interview (RFInsights RFIC) | 01 | C | 01/resonance-and-q |  |
| 1045 | Constant-Q locus of a series RL on the Smith chart | Interview (RFInsights RFIC) | 03 | C | 03/smith-chart | constant-Q arcs |
| 1046 | Oscillator tank impedance at start-up vs steady state (negative R) | Interview (RFInsights RFIC) | 05 | P | 05/oscillators | negative-R and amplitude settling covered; impedance view implicit |
| 1047 | Tank current vs source current at resonance (Q×) | Interview (RFInsights RFIC) | 01 | C | 01/resonance-and-q |  |
| 1048 | Effect of I/Q mismatch in RX and TX | Interview (RFInsights RFIC) | 14 | C | 14/iq-complex-baseband; 06/transmitter-architectures | IRR formula |
| 1049 | Transistor layout: fingers, parasitics | Interview (RFInsights RFIC) | 05 | M | — | IC layout absent |
| 1050 | Offset from load mismatch in a diff pair; sizing to reduce it | Interview (RFInsights RFIC) | 05 | P | 05/analog-signal-conditioning; 05/op-amps-real-limitations | offset specs covered; device-level mismatch absent |
| 1051 | Noise transfer from a current-mirror node to output | Interview (RFInsights RFIC) | 05 | M | — |  |
| 1052 | CG input impedance including ro feedback | Interview (RFInsights RFIC) | 05 | P | 05/amplifier-topologies | Rin ≈ 1/gm only |
| 1053 | AM-AM/AM-PM → asymmetric IM3 | Interview (RFInsights RFIC) | 07 | P | 07/nonlinearity-p1db-ip3-intermod; 06/power-amplifiers | asymmetry from memory noted, AM-PM mechanism not |
| 1054 | What SSB is | Interview (RFInsights RFIC) | 10 | C | 10/analog-modulation-am-fm-pm-ssb |  |
| 1055 | Handling antenna-impedance variation at the PA | Interview (RFInsights RFIC) | 06 | C | 06/power-amplifiers; 06/circulators-isolators; 06/couplers-dividers-combiners | ruggedness, isolator, balanced amps |
| 1056 | Zin of gain −1 amp with R across it (R/2, Miller) | Interview (RFInsights RFIC) | 05 | C | 05/bjt-fundamentals-small-signal |  |
| 1057 | Square-wave spectrum; 25 % duty cycle | Interview (RFInsights RFIC) | 00 | C | 00/fourier-series-and-transform |  |
| 1058 | Where Γopt lies vs S11* | Interview (RFInsights RFIC) | 06 | C | 06/lna-design; 07/noise-figure-and-friis |  |
| 1059 | Noise budget of a textbook CS LNA (Rg, Lg loss, channel, gate noise) | Interview (RFInsights RFIC) | 06 | P | 06/lna-design | gate-inductor loss dominance shown; induced gate noise not |
| 1060 | Transceiver link budget | Interview (RFInsights RFIC) | 09 | C | 09/link-budget-methodology; 07/receiver-cascade-analysis |  |
| 1061 | Voltage gain of a 20 dB LNA into 50 Ω and into 100 Ω | Interview (RFInsights RFIC) | 00 | C | 00/decibels-and-log-units | 20 log only for equal impedances |
| 1062 | 3 dB pad before a 3 dB-NF LNA (6 dB) | Interview (RFInsights RFIC) | 07 | C | 07/noise-figure-and-friis |  |
| 1063 | Max efficiency ≠ max power transfer; why load-pull | Interview (RFInsights RFIC) | 01 | C | 01/network-theorems-max-power-transfer; 06/power-amplifiers |  |
| 1064 | NF of a phased array (LNA before beamformer) | Interview (RFInsights RFIC) | 12 | C | 12/beamforming-architectures; 12/phase-shifters-ttd-components |  |
| 1065 | Lossy Wilkinson: choose isolation resistor for best isolation | Interview (RFInsights RFIC) | 06 | M | — | ideal Wilkinson only |
| 1066 | Wilkinson with outputs shorted into 25 Ω: S11 | Interview (RFInsights RFIC) | 06 | P | 06/couplers-dividers-combiners | even-mode idea present, not worked |
| 1067 | Parallel LC ∥ 50 Ω trace vs f; changing L/C at same f0 | Interview (RFInsights RFIC) | 03 | C | 03/smith-chart | Foster + constant-Q |
| 1068 | Why inductive degeneration; capacitive degeneration gives −R | Interview (RFInsights RFIC) | 06 | C | 06/lna-design; 05/oscillators |  |
| 1069 | 27 dBm from 1 V: required load; differential PA doubles swing | Interview (RFInsights RFIC) | 06 | P | 06/power-amplifiers | single-ended Ropt covered; differential/balun PA not |
| 1070 | LO phase noise on a QPSK constellation (rotation smear, EVM) | Interview (RFInsights RFIC) | 07 | C | 07/phase-noise-and-jitter; 10/digital-modulation-psk-qam-fsk |  |
| 1071 | PVT variation and matching strategies | Interview (RFInsights RFIC) | 05 | M | — |  |
| 1072 | Two uncorrelated noise sources into a Wilkinson: output noise | Interview (RFInsights RFIC) | 06 | P | 06/couplers-dividers-combiners | combining efficiency for coherent sources only |
| 1073 | Sine-driven switch in series with source: output spectrum | Interview (RFInsights RFIC) | 06 | C | 06/mixers | switching-mixer analysis |
| 1074 | Stabilise without resistors (lossy ferrite/feedback) | Interview (RFInsights RFIC) | 06 | C | 06/amplifier-stability-and-biasing | only loss or feedback stabilises |
| 1075 | How to simulate large-signal stability | Interview (RFInsights RFIC) | 16 | P | 06/amplifier-stability-and-biasing; 16/rf-circuit-simulators-harmonic-balance | HB mentioned; auxiliary-generator/pole-zero methods absent |
| 1076 | Why λ/4 is 180° on the Smith chart | Interview (RFInsights RFIC) | 03 | C | 03/smith-chart |  |
| 1077 | Changing Z0 of two parallel conductors | Interview (RFInsights RFIC) | 03 | C | 03/telegrapher-equations-characteristic-impedance; 02/inductance-capacitance-from-fields |  |
| 1078 | Filter before or after LNA? | Interview (RFInsights RFIC) | 07 | C | 07/receiver-cascade-analysis; 15/ground-station-design |  |
| 1079 | OFDM pros/cons with block diagram | Interview (RFInsights comms) | 10 | C | 10/ofdm |  |
| 1080 | OFDMA vs OFDM | Interview (RFInsights comms) | 10 | P | 10/ofdm | one-line mention |
| 1081 | Cyclic prefix purpose and length | Interview (RFInsights comms) | 10 | C | 10/ofdm |  |
| 1082 | OFDM channel estimation | Interview (RFInsights comms) | 10 | P | 10/ofdm | pilots tagged; estimator not derived |
| 1083 | MMSE vs LMMSE | Interview (RFInsights comms) | 10 | P | 10/pulse-shaping-isi | MMSE equaliser only |
| 1084 | Effect of changing subcarrier spacing | Interview (RFInsights comms) | 10 | C | 10/ofdm |  |
| 1085 | MIMO vs massive MIMO | Interview (RFInsights comms) | 10 | P | 00/matrices-and-linear-algebra-for-networks | SVD capacity only |
| 1086 | Antenna spacing in arrays | Interview (RFInsights comms) | 12 | C | 12/beam-steering-grating-lobes; 12/planar-arrays-element-pattern-coupling |  |
| 1087 | SVD for transmit antenna selection | Interview (RFInsights comms) | 10 | P | 00/matrices-and-linear-algebra-for-networks |  |
| 1088 | How a TX learns where to beamform (CSI, sounding, DOA) | Interview (RFInsights comms) | 12 | P | 12/adaptive-beamforming-doa | DOA covered; CSI feedback absent |
| 1089 | Types of diversity | Interview (RFInsights comms) | 09 | C | 09/multipath-fading-doppler |  |
| 1090 | Types of fading | Interview (RFInsights comms) | 09 | C | 09/multipath-fading-doppler |  |
| 1091 | Coherence BW/time, delay spread, Doppler | Interview (RFInsights comms) | 09 | C | 09/multipath-fading-doppler |  |
| 1092 | Flat vs frequency-selective channel | Interview (RFInsights comms) | 09 | C | 09/multipath-fading-doppler |  |
| 1093 | Key PHY parameters when designing a waveform | Interview (RFInsights comms) | 10 | C | 10/modulation-choice-guide |  |
| 1094 | What an impulse response is | Interview (RFInsights comms) | 00 | C | 00/linear-systems-convolution |  |
| 1095 | Large- vs small-scale fading | Interview (RFInsights comms) | 09 | C | 09/empirical-path-loss-models; 09/multipath-fading-doppler |  |
| 1096 | Diversity combining (SC/EGC/MRC) — which is best | Interview (RFInsights comms) | 09 | P | 09/multipath-fading-doppler | SC and MRC outage given; EGC absent |
| 1097 | Alamouti code and its rate | Interview (RFInsights comms) | 10 | M | — | space-time coding absent |
| 1098 | Autocorrelation ↔ PSD (Wiener–Khinchin) | Interview (RFInsights comms) | 00 | C | 00/probability-random-processes-and-psd |  |
| 1099 | Fourier transform and time–frequency duality | Interview (RFInsights comms) | 00 | C | 00/fourier-series-and-transform |  |
| 1100 | Sample rate and FFT length for 5 Hz + 10 Hz tones | Interview (RFInsights comms) | 14 | C | 14/sampling-aliasing-bandpass-sampling; 14/fft-spectral-analysis-windows |  |
| 1101 | SNR of two 10 dBm tones over a noise level | Interview (RFInsights comms) | 00 | C | 00/decibels-and-log-units |  |
| 1102 | Transmit-diversity drawback and fix | Interview (RFInsights comms) | 10 | M | — |  |
| 1103 | Short/open on the Smith chart; series lossless line moves | Interview (RFInsights EM) | 03 | C | 03/smith-chart |  |
| 1104 | What TEM mode is | Interview (RFInsights EM) | 02 | C | 02/waveguides-and-cavity-resonators; 03/telegrapher-equations-characteristic-impedance |  |
| 1105 | Microstrip cross-section field (quasi-TEM) | Interview (RFInsights EM) | 03 | C | 03/planar-lines-microstrip-stripline-cpwg |  |
| 1106 | EM-solver port types (wave vs lumped) | Interview (RFInsights EM) | 16 | C | 16/em-solvers-fdtd-mom-fem; 16/openems-workflow | lumped vs wave ports |
| 1107 | How to trust an EM simulation (convergence, validation) | Interview (RFInsights EM) | 16 | C | 16/simulation-validation; 16/em-solvers-fdtd-mom-fem |  |
| 1108 | Why a wave port must be wider than the microstrip | Interview (RFInsights EM) | 16 | P | 16/em-solvers-fdtd-mom-fem | wave-port eigenmode explained; sizing rule absent |
| 1109 | Differential signalling and crosstalk | Interview (RFInsights EM) | 13 | C | 03/s-parameters; 13/grounding-and-return-paths |  |
| 1110 | Surface roughness effect | Interview (RFInsights EM) | 02 | C | 02/skin-effect-conductor-loss-roughness |  |
| 1111 | Solver solution modes (driven/eigenmode/transient) | Interview (RFInsights EM) | 16 | P | 16/em-solvers-fdtd-mom-fem | method classes covered, HFSS modes not |
| 1112 | Real capacitor impedance vs frequency (SRF) | Interview (RFInsights EM) | 04 | C | 04/capacitors-at-rf-mlcc |  |
| 1113 | What device models come from I–V curves vs S-parameters | Interview (RFInsights EM) | 04 | P | 04/component-models-s2p-spice; 05/bjt-fundamentals-small-signal |  |
| 1114 | Amplifier linearisation techniques | Interview (RFInsights EM) | 06 | C | 06/power-amplifiers | DPD, Doherty, ET/EER, outphasing; feedforward absent |
| 1115 | Skin depth vs line width | Interview (RFInsights EM) | 02 | C | 02/skin-effect-conductor-loss-roughness; 03/planar-lines-microstrip-stripline-cpwg |  |
| 1116 | dB vs dBm; 1 mW and 2 mW in dBm | Interview (Fan Yang) | 00 | C | 00/decibels-and-log-units |  |
| 1117 | What LO leakage is and why | Interview (Fan Yang) | 06 | C | 06/receiver-architectures; 06/transmitter-architectures |  |
| 1118 | EVM and causes of bad EVM | Interview (Fan Yang) | 10 | C | 10/digital-modulation-psk-qam-fsk; 06/transmitter-architectures |  |
| 1119 | RX sensitivity and dynamic range | Interview (Fan Yang) | 07 | C | 07/sensitivity-and-mds; 07/dynamic-range-sfdr-blocking |  |
| 1120 | Debugging sensitivity degradation | Interview (Fan Yang) | 17 | C | 17/rf-bring-up-debug-playbook |  |
| 1121 | NF vs sensitivity and SNR | Interview (Fan Yang) | 07 | C | 07/noise-figure-and-friis; 07/sensitivity-and-mds |  |
| 1122 | IIP3/OIP3 and how to measure | Interview (Fan Yang) | 07 | C | 07/nonlinearity-p1db-ip3-intermod |  |
| 1123 | Impedance and reading a Smith chart | Interview (Fan Yang) | 03 | C | 03/smith-chart |  |
| 1124 | LC and pi matching | Interview (Fan Yang) | 03 | C | 03/impedance-matching-lumped-and-distributed |  |
| 1125 | Derive expected Wi-Fi 20 MHz MCS0 sensitivity | Interview (Fan Yang) | 10 | P | 07/sensitivity-and-mds | formula present; 802.11 SNR thresholds/implementation margins absent |
| 1126 | Out-of-band noise and blockers | Interview (Fan Yang) | 07 | C | 07/dynamic-range-sfdr-blocking |  |
| 1127 | S-parameters, how measured, S11/S21/S12 | Interview (Fan Yang) | 03 | C | 03/s-parameters; 17/vna-fundamentals-calibration |  |
| 1128 | How an LNA improves sensitivity | Interview (Fan Yang) | 07 | C | 07/noise-figure-and-friis; 06/lna-design |  |
| 1129 | Phase noise and its effect on EVM | Interview (Fan Yang) | 07 | C | 07/phase-noise-and-jitter | integrated phase error |
| 1130 | Explain/draw a PLL | Interview (Fan Yang) | 06 | C | 06/vco-and-pll-synthesizers |  |
| 1131 | Directional coupler and uses | Interview (Fan Yang) | 06 | C | 06/couplers-dividers-combiners; 17/rf-power-measurement |  |
| 1132 | Antenna gain, TRP and EIRP | Interview (Fan Yang) | 08 | C | 08/antenna-fundamentals; 17/antenna-range-ota-testing |  |
| 1133 | Microstrip Z0 vs width, height, εr | Interview (Fan Yang) | 03 | C | 03/planar-lines-microstrip-stripline-cpwg |  |
| 1134 | Buck converter operation | Interview (Fan Yang) | 05 | C | 05/power-supplies-for-rf-and-analog | ripple equations |
| 1135 | RBW and VBW | Interview (Fan Yang) | 17 | C | 17/spectrum-analyzers |  |
| 1136 | 802.11 MCS/channel-bandwidth relationship | Interview (Fan Yang) | 10 | M | — | OOS; Wi-Fi standards out of scope |
| 1137 | RF filter types and uses | Interview (InterviewPrep) | 06 | C | 06/rf-filters-lc-saw-baw-cavity-microstrip |  |
| 1138 | Intermodulation distortion and impact | Interview (InterviewPrep) | 07 | C | 07/nonlinearity-p1db-ip3-intermod |  |
| 1139 | Multipath propagation effects | Interview (InterviewPrep) | 09 | C | 09/multipath-fading-doppler |  |
| 1140 | Common interference sources and mitigation | Interview (InterviewPrep) | 13 | C | 13/emc-emi-fundamentals | EMC/shielding pages unwritten |
| 1141 | Component selection for an RF circuit | Interview (InterviewPrep) | 18 | C | 18/lna-pa-gain-block-mmics; 18/rf-transceiver-ics |  |
| 1142 | Duplexer vs diplexer and how they work | Interview (InterviewPrep) | 06 | P | 06/circulators-isolators | circulator duplexing; filter duplexers/diplexers absent |
| 1143 | Frequency planning to avoid spurs | Interview (InterviewPrep) | 06 | C | 06/mixers; 06/transmitter-architectures |  |
| 1144 | Grounding and shielding practice | Interview (InterviewPrep) | 13 | C | 13/shielding-and-isolation; 13/grounding-and-return-paths | 13/shielding-and-isolation unwritten |
| 1145 | RF and digital on the same PCB | Interview (InterviewPrep) | 13 | C | 13/rf-layout-rules; 13/emc-emi-fundamentals | 13/mixed-signal-layout unwritten |
| 1146 | Designing for FCC/ETSI compliance | Interview (InterviewPrep) | 19 | C | 19/certification-fcc-ce-imda |  |
| 1147 | Gain–beamwidth relation | Interview (Glassdoor antenna) | 08 | C | 08/antenna-fundamentals |  |
| 1148 | Modes in rectangular and circular waveguide | Interview (Glassdoor antenna) | 02 | C | 02/waveguides-and-cavity-resonators; 08/horn-reflector-aperture-antennas | circular only via TE11 attenuation rule |
| 1149 | High-gain microstrip antenna design | Interview (Glassdoor antenna) | 08 | C | 08/patch-antennas; 12/diy-phased-array-projects |  |
| 1150 | What a phased array is | Interview (Glassdoor antenna) | 12 | C | 12/beam-steering-grating-lobes |  |
| 1151 | RCS and its significance | Interview (ResumeGemini radar) | 11 | C | 11/radar-cross-section |  |
| 1152 | Radar signal-processing techniques | Interview (ResumeGemini radar) | 11 | C | 11/pulsed-radar-and-pulse-compression; 11/detection-theory-cfar |  |
| 1153 | Clutter and interference limits | Interview (ResumeGemini radar) | 11 | C | 11/clutter-and-mti |  |
| 1154 | Automotive radar principles | Interview (ResumeGemini radar) | 11 | C | 11/fmcw-radar; 11/mimo-radar-virtual-arrays |  |
| 1155 | CMRR and how to improve it | Interview (ElectronicsPost analog) | 05 | C | 05/analog-signal-conditioning |  |
| 1156 | Current mirror and its advantages | Interview (ElectronicsPost analog) | 05 | P | 05/amplifier-topologies | mentioned only |
| 1157 | Slew rate and full-power bandwidth | Interview (ElectronicsPost analog) | 05 | C | 05/op-amps-real-limitations |  |
| 1158 | Virtual short/virtual ground concept | Interview (ElectronicsPost analog) | 05 | P | 05/op-amps-real-limitations | implicit in NG analysis |
| 1159 | Input offset voltage, offset current, bias current | Interview (ElectronicsPost analog) | 05 | C | 05/op-amps-real-limitations |  |
| 1160 | PSRR | Interview (ElectronicsPost analog) | 05 | C | 05/op-amps-real-limitations |  |
| 1161 | GBW / unity-gain bandwidth | Interview (ElectronicsPost analog) | 05 | C | 05/op-amps-real-limitations |  |
| 1162 | Instrumentation amplifier | Interview (ElectronicsPost analog) | 05 | C | 05/analog-signal-conditioning |  |
| 1163 | Integrator output for a sine / square input | Interview (ElectronicsPost analog) | 05 | P | 05/active-filters |  |
| 1164 | Differentiator behaviour and stability | Interview (ElectronicsPost analog) | 05 | M | — |  |
| 1165 | Advantages of negative feedback | Interview (ElectronicsPost analog) | 05 | C | 05/amplifier-topologies; 05/feedback-and-stability |  |
| 1166 | Inverting vs non-inverting amplifier | Interview (ElectronicsPost analog) | 05 | C | 05/amplifier-topologies |  |
| 1167 | From R, L, G, C per metre compute Z0, α, β, vp at a frequency | Problem type (Pozar ch.2) | 03 | C | 03/telegrapher-equations-characteristic-impedance |  |
| 1168 | Input impedance of a lossy/lossless terminated line; λ/4 and λ/2 cases | Problem type (Pozar ch.2) | 03 | C | 03/input-impedance-stubs-quarter-wave |  |
| 1169 | Power delivered with mismatched generator and load on a line | Problem type (Pozar ch.2) | 03 | C | 03/reflections-vswr-return-loss-mismatch; 03/signal-flow-graphs-mason |  |
| 1170 | Loss of a mismatched lossy line (total loss vs SWR) | Problem type (Pozar ch.2) | 03 | C | 03/reflections-vswr-return-loss-mismatch | TL formula derived (line 111) |
| 1171 | Smith-chart problems: Z → Γ, VSWR, distance to Vmax/Vmin | Problem type (Pozar ch.2) | 03 | C | 03/smith-chart |  |
| 1172 | Rectangular-guide cutoff, λg, dispersion, attenuation | Problem type (Pozar ch.3) | 02 | C | 02/waveguides-and-cavity-resonators |  |
| 1173 | Circular waveguide TE11/TM01 cutoffs and field patterns | Problem type (Pozar ch.3) | 02 | C | 08/horn-reflector-aperture-antennas; 02/waveguides-and-cavity-resonators | TE11/TM01 cutoffs given; field plots absent |
| 1174 | Coax TE11 higher-order-mode cutoff | Problem type (Pozar ch.3) | 03 | C | 03/coax-and-cables |  |
| 1175 | Synthesise microstrip/stripline width for Z0; compute εeff and loss | Problem type (Pozar ch.3) | 03 | C | 03/planar-lines-microstrip-stripline-cpwg |  |
| 1176 | Surface-wave (TM0) modes on a grounded dielectric slab: cutoff and β | Problem type (Pozar ch.3) | 02 | P | 08/patch-antennas; 12/planar-arrays-element-pattern-coupling | TM0/TE1 cutoff stated; β(f) not derived |
| 1177 | Convert between Z, Y, S, ABCD; test reciprocity/losslessness | Problem type (Pozar ch.4) | 01 | C | 01/two-port-networks-zyh-abcd; 03/s-parameters |  |
| 1178 | Shift S-parameter reference planes | Problem type (Pozar ch.4) | 03 | C | 03/s-parameters |  |
| 1179 | Signal-flow-graph (Mason) reduction for Γin and GT | Problem type (Pozar ch.4) | 03 | C | 03/signal-flow-graphs-mason |  |
| 1180 | TRL calibration derivation | Problem type (Pozar ch.4) | 17 | C | 17/vna-fundamentals-calibration |  |
| 1181 | L-section matching of a complex load (two solutions) | Problem type (Pozar ch.5) | 03 | C | 03/impedance-matching-lumped-and-distributed |  |
| 1182 | Single-stub (shunt/series) tuner design | Problem type (Pozar ch.5) | 03 | C | 03/impedance-matching-lumped-and-distributed |  |
| 1183 | Double-stub tuner and its forbidden region | Problem type (Pozar ch.5) | 03 | M | — | listed as a gap in 03/_index |
| 1184 | Quarter-wave transformer bandwidth; multisection binomial/Chebyshev | Problem type (Pozar ch.5) | 03 | C | 03/impedance-matching-lumped-and-distributed; 03/input-impedance-stubs-quarter-wave |  |
| 1185 | Tapered lines (exponential, Klopfenstein) | Problem type (Pozar ch.5) | 03 | C | 03/impedance-matching-lumped-and-distributed |  |
| 1186 | Bode–Fano limit for an RC load | Problem type (Pozar ch.5) | 03 | C | 03/broadband-matching-bode-fano |  |
| 1187 | Series/parallel resonator Q, loaded vs unloaded Q | Problem type (Pozar ch.6) | 01 | C | 01/resonance-and-q |  |
| 1188 | λ/2 open and λ/4 shorted line resonators: equivalent RLC and Q | Problem type (Pozar ch.6) | 03 | C | 03/input-impedance-stubs-quarter-wave |  |
| 1189 | Rectangular cavity resonant frequency and Q (conductor + dielectric) | Problem type (Pozar ch.6) | 02 | C | 02/waveguides-and-cavity-resonators |  |
| 1190 | Resonator coupling: coupling coefficient, critical/over/under coupling | Problem type (Pozar ch.6) | 01 | P | 06/rf-filters-lc-saw-baw-cavity-microstrip; 01/resonance-and-q | Qe extraction covered; critical-coupling condition (g = 1) not stated |
| 1191 | Dielectric-resonator resonant frequency / Q | Problem type (Pozar ch.6) | 02 | P | 18/filter-parts-saw-ceramic-ltcc | DR/ceramic filters as parts; f0/Q calculation absent |
| 1192 | T-junction/resistive divider analysis | Problem type (Pozar ch.7) | 06 | C | 06/couplers-dividers-combiners |  |
| 1193 | Wilkinson even/odd-mode analysis; unequal split | Problem type (Pozar ch.7) | 06 | C | 06/couplers-dividers-combiners |  |
| 1194 | Coupled-line coupler Z0e/Z0o design; directivity | Problem type (Pozar ch.7) | 06 | C | 06/couplers-dividers-combiners |  |
| 1195 | Branch-line and rat-race hybrid analysis | Problem type (Pozar ch.7) | 06 | C | 06/couplers-dividers-combiners |  |
| 1196 | Lange coupler | Problem type (Pozar ch.7) | 06 | C | 06/couplers-dividers-combiners |  |
| 1197 | Image-parameter filters (constant-k, m-derived) | Problem type (Pozar ch.8) | 01 | M | — | image impedance defined only |
| 1198 | Insertion-loss method: prototype, scaling, LP→BP transforms | Problem type (Pozar ch.8) | 01 | C | 01/passive-filter-design-prototypes |  |
| 1199 | Richards' transformation and Kuroda identities | Problem type (Pozar ch.8) | 06 | C | 06/rf-filters-lc-saw-baw-cavity-microstrip |  |
| 1200 | Stepped-impedance LPF and coupled-line BPF design | Problem type (Pozar ch.8) | 06 | C | 06/rf-filters-lc-saw-baw-cavity-microstrip |  |
| 1201 | Ferrite permeability tensor, Faraday rotation, circulator S-matrix | Problem type (Pozar ch.9) | 06 | C | 06/circulators-isolators; 02/magnetic-materials-permeability |  |
| 1202 | Noise temperature/NF of lossy lines and cascades | Problem type (Pozar ch.10) | 07 | C | 07/thermal-noise-and-noise-temperature; 07/noise-figure-and-friis |  |
| 1203 | Dynamic range and SFDR of a receiver chain | Problem type (Pozar ch.10) | 07 | C | 07/dynamic-range-sfdr-blocking |  |
| 1204 | Stability circles and K/µ tests | Problem type (Pozar ch.12) | 06 | C | 06/amplifier-stability-and-biasing |  |
| 1205 | Constant-gain circles; unilateral design and unilateral figure of merit | Problem type (Pozar ch.12) | 06 | P | 06/lna-design | gain/noise circles covered; unilateral figure of merit absent |
| 1206 | LNA design with noise circles | Problem type (Pozar ch.12) | 06 | C | 06/lna-design |  |
| 1207 | Balanced amplifier analysis | Problem type (Pozar ch.12) | 06 | P | 06/couplers-dividers-combiners; 06/lna-design | mentioned; S-parameter analysis not worked |
| 1208 | Distributed (travelling-wave) amplifier gain/bandwidth | Problem type (Pozar ch.12) | 06 | P | 05/amplifier-topologies | one-line mention |
| 1209 | Transistor oscillator design via negative resistance | Problem type (Pozar ch.13) | 05 | C | 05/oscillators |  |
| 1210 | Frequency multiplier efficiency/phase noise | Problem type (Pozar ch.13) | 06 | C | 06/frequency-multipliers-dividers |  |
| 1211 | Mixer image, conversion loss, NF (SSB/DSB) | Problem type (Pozar ch.13) | 06 | C | 06/mixers |  |
| 1212 | Radiometer sensitivity (ΔT = Tsys/√(Bτ)), Dicke switching | Problem type (Pozar ch.14) | 07 | M | — | radiometry absent |
| 1213 | System link budget with G/T and C/N0 | Problem type (Pozar ch.14) | 09 | C | 09/link-budget-methodology |  |
| 1214 | Directivity/gain/efficiency/aperture from a given pattern | Problem type (Balanis ch.2) | 08 | C | 08/antenna-fundamentals |  |
| 1215 | Radiation integrals via vector potential A | Problem type (Balanis ch.3) | 02 | C | 02/radiation-from-currents-hertzian-dipole |  |
| 1216 | Finite dipole: current, pattern, Rrad, directivity vs length | Problem type (Balanis ch.4) | 08 | C | 08/dipoles-and-monopoles |  |
| 1217 | Small and large loops: Rrad, pattern | Problem type (Balanis ch.5) | 08 | C | 08/loop-antennas |  |
| 1218 | Uniform, binomial and Dolph–Chebyshev linear arrays | Problem type (Balanis ch.6) | 12 | C | 12/array-factor-linear-arrays; 12/tapering-sidelobe-control |  |
| 1219 | Planar arrays and grating-lobe lattice | Problem type (Balanis ch.6) | 12 | C | 12/planar-arrays-element-pattern-coupling |  |
| 1220 | Pattern synthesis: Schelkunoff polynomial, Fourier, Woodward–Lawson | Problem type (Balanis ch.7) | 12 | M | — | Dolph/Taylor only |
| 1221 | Pocklington/Hallén integral equations and MoM | Problem type (Balanis ch.8) | 08 | P | 08/antenna-simulation-nec-openems | own MoM tool exists; equations only cited |
| 1222 | Mutual impedance of parallel dipoles (induced EMF) | Problem type (Balanis ch.8) | 08 | P | 08/yagi-uda-and-log-periodic; 12/planar-arrays-element-pattern-coupling | MoM results; induced-EMF mutual-impedance formula not given |
| 1223 | Biconical and broadband wire antennas | Problem type (Balanis ch.9) | 08 | P | 08/dipoles-and-monopoles | one-line mention |
| 1224 | Axial-mode helix design | Problem type (Balanis ch.10) | 08 | C | 08/helical-antennas |  |
| 1225 | Frequency-independent antennas: LPDA (covered), spirals (absent) | Problem type (Balanis ch.11) | 08 | P | 08/yagi-uda-and-log-periodic |  |
| 1226 | Aperture fields via equivalence principle; uniform/tapered apertures | Problem type (Balanis ch.12) | 08 | C | 08/horn-reflector-aperture-antennas |  |
| 1227 | Optimum pyramidal horn design | Problem type (Balanis ch.13) | 08 | C | 08/horn-reflector-aperture-antennas |  |
| 1228 | Rectangular patch design (TL + cavity models) | Problem type (Balanis ch.14) | 08 | C | 08/patch-antennas |  |
| 1229 | Parabolic reflector efficiency, spillover/taper | Problem type (Balanis ch.15) | 08 | C | 08/horn-reflector-aperture-antennas |  |
| 1230 | Antenna measurement: far-field distance, gain transfer, 3-antenna method | Problem type (Balanis ch.17) | 08 | C | 08/antenna-measurement |  |
| 1231 | Power-series nonlinearity: P1dB, IP3, cross-modulation, cascades | Problem type (Razavi ch.2) | 07 | C | 07/nonlinearity-p1db-ip3-intermod |  |
| 1232 | Heterodyne image, Hartley/Weaver image-reject with phase error | Problem type (Razavi ch.4) | 06 | C | 06/receiver-architectures; 06/mixers |  |
| 1233 | Direct-conversion DC offset, IP2, flicker | Problem type (Razavi ch.4) | 06 | C | 06/receiver-architectures |  |
| 1234 | CS-inductive-degeneration LNA noise and match | Problem type (Razavi ch.5) | 06 | C | 06/lna-design |  |
| 1235 | Noise-cancelling / CG-CS wideband LNAs | Problem type (Razavi ch.5) | 06 | P | 06/lna-design | named only |
| 1236 | Passive vs active (Gilbert) mixer gain, noise, linearity | Problem type (Razavi ch.6) | 06 | C | 06/mixers |  |
| 1237 | Cross-coupled LC VCO start-up and tuning range | Problem type (Razavi ch.8) | 05 | P | 05/oscillators; 06/vco-and-pll-synthesizers | mentioned; not analysed |
| 1238 | Phase noise via the impulse-sensitivity function (LTV) vs Leeson | Problem type (Razavi ch.8) | 07 | P | 07/phase-noise-and-jitter | Hajimiri cited; ISF not derived (MIT 6.776 PS6 asks for both) |
| 1239 | Charge-pump PLL loop dynamics, loop-filter design, lock time | Problem type (Razavi ch.9) | 06 | C | 06/vco-and-pll-synthesizers |  |
| 1240 | Fractional-N ΣΔ noise and spurs | Problem type (Razavi ch.10) | 06 | C | 06/vco-and-pll-synthesizers |  |
| 1241 | PA classes efficiency; load-line; linearisation (Doherty, ET, outphasing, DPD) | Problem type (Razavi ch.12) | 06 | C | 06/power-amplifiers |  |
| 1242 | Choose RC of an AM envelope detector (ripple vs diagonal clipping) | Problem type (MIT 6.776 PS1) | 10 | P | 10/analog-modulation-am-fm-pm-ssb; 06/detectors-and-power-meters | envelope detection covered; RC design rule absent |
| 1243 | Analyse Weaver's SSB modulator | Problem type (MIT 6.776 PS1) | 06 | P | 06/mixers; 06/receiver-architectures | named/cited only |
| 1244 | S11/S21 of connector–trace–package–bondwire–pad model | Problem type (MIT 6.776 PS2) | 04 | C | 04/package-parasitics-bondwires; 03/s-parameters |  |
| 1245 | Shunt/zero-peaked amplifier bandwidth extension | Problem type (MIT 6.776 PS3) | 05 | M | — | inductive/shunt peaking absent |
| 1246 | Source follower ringing with capacitive load | Problem type (MIT 6.776 PS3) | 05 | C | 05/feedback-and-stability |  |
| 1247 | Tuned cascode amplifier with finite-Q inductors: gain at f0 | Problem type (MIT 6.776 PS4) | 06 | P | 06/lna-design; 01/resonance-and-q |  |
| 1248 | Power-constrained CMOS LNA design (fix Pdc, pick W, Lg, Ls) | Problem type (MIT 6.776 PS5) | 06 | P | 06/lna-design | see interview row |
| 1249 | Derive oscillator phase noise with Leeson's model | Problem type (MIT 6.776 PS6) | 07 | W | 05/oscillators; 07/phase-noise-and-jitter | 05/oscillators gives 2FkT/Ps vs FkT/(2Ps) in 07/phase-noise and 06/vco-and-pll — 6 dB apart (see §2 W1) |
| 1250 | Radar equation with Pd/Pfa, integration, fluctuation loss | Problem type (Skolnik ch.2) | 11 | C | 11/radar-range-equation; 11/detection-theory-cfar |  |
| 1251 | MTI blind speeds, staggered PRF, improvement factor | Problem type (Skolnik ch.3) | 11 | C | 11/clutter-and-mti |  |
| 1252 | PRF ambiguity resolution (Chinese remainder) | Problem type (Skolnik ch.3) | 11 | C | 11/pulsed-radar-and-pulse-compression |  |
| 1253 | Tracking radar: monopulse (covered) vs conical scan/sequential lobing (absent) | Problem type (Skolnik ch.4) | 11 | P | 12/tapering-sidelobe-control |  |
| 1254 | Pulse compression gain, sidelobes, Doppler tolerance | Problem type (Skolnik ch.6) | 11 | C | 11/pulsed-radar-and-pulse-compression; 11/ambiguity-function-waveforms |  |
| 1255 | Surface/volume clutter RCS and signal-to-clutter | Problem type (Skolnik ch.7) | 11 | C | 11/clutter-and-mti |  |
| 1256 | Multipath lobing and refraction (4/3 earth) for radar coverage | Problem type (Skolnik ch.8) | 09 | C | 09/two-ray-ground-reflection; 09/fresnel-zones-los-radio-horizon |  |
| 1257 | FM-CW radio altimeter range/accuracy | Problem type (Skolnik ch.3) | 11 | P | 11/fmcw-radar | FMCW theory present; altimeter-specific (fixed-error, step error) absent |
| 1258 | SAR/ISAR resolution | Problem type (Skolnik ch.14) | 11 | C | 11/sar-and-imaging |  |
| 1259 | Oblique incidence: Fresnel coefficients, Brewster, TIR | Problem type (MIT 6.013) | 02 | C | 02/boundary-conditions-reflection-refraction |  |
| 1260 | Transmission-line transients: bounce (lattice) diagrams with resistive loads | Problem type (MIT 6.013) | 03 | P | 03/time-domain-reflectometry; 03/telegrapher-equations-characteristic-impedance | TDR step reflections covered; multi-bounce lattice construction absent |
| 1261 | Dielectric slab waveguide / optical fibre modes | Problem type (MIT 6.013) | 02 | P | 02/boundary-conditions-reflection-refraction | TIR/evanescence only |
| 1262 | Poynting power flow in circuits and waves | Problem type (MIT 6.013) | 02 | C | 02/poynting-vector-power-flow |  |
| 1263 | EM forces/radiation pressure and energy methods (virtual work) | Problem type (MIT 6.013) | 02 | M | — |  |
| 1264 | EQS/MQS limits, charge relaxation, magnetic diffusion | Problem type (MIT 6.013) | 02 | C | 02/quasi-static-vs-full-wave |  |
| 1265 | Two-element arrays and array factor | Problem type (MIT 6.013) | 12 | C | 12/array-factor-linear-arrays |  |
| 1266 | Cookbook LC filter design (prototype → transform → simulate) | Problem type (Stanford EE133) | 01 | C | 01/passive-filter-design-prototypes |  |
| 1267 | Design a superhet AM broadcast receiver (tuned RF, IF, detector, AGC) | Problem type (Stanford EE133) | 06 | P | 06/receiver-architectures; 10/analog-modulation-am-fm-pm-ssb | architecture covered; AGC loop design absent |
| 1268 | Colpitts oscillator design and start-up | Problem type (Stanford EE133) | 05 | C | 05/oscillators |  |
| 1269 | Radio waves are non-ionising radiation | Technician T0C01 | 19 | P | 19/rf-exposure-safety | thermal mechanism stated; "non-ionising" not |
| 1270 | Band with lowest MPE (50 MHz, in 30–300 MHz) | Technician T0C02 | 19 | C | 19/rf-exposure-safety | FCC/ICNIRP tables |
| 1271 | 50 % duty doubles allowable power density | Technician T0C03 | 19 | C | 19/rf-exposure-safety | duty factor D in safe distance |
| 1272 | Exposure factors: f, power, distance, pattern | Technician T0C04 | 19 | C | 19/rf-exposure-safety |  |
| 1273 | Why limits vary with frequency (body absorption/resonance) | Technician T0C05 | 19 | P | 19/rf-exposure-safety | SAR basis given; whole-body resonance not explained |
| 1274 | Compliance by OET 65 calculation, modelling or measurement | Technician T0C06 | 19 | C | 19/rf-exposure-safety |  |
| 1275 | Touching an antenna while transmitting → RF burn | Technician T0C07 | 19 | C | 19/lab-safety-esd-high-power |  |
| 1276 | Relocating antennas reduces exposure | Technician T0C08 | 19 | C | 19/rf-exposure-safety | distance law |
| 1277 | Re-evaluate after any change | Technician T0C09 | 19 | P | 19/rf-exposure-safety |  |
| 1278 | Duty cycle sets average exposure | Technician T0C10 | 19 | C | 19/rf-exposure-safety |  |
| 1279 | Duty-cycle definition for exposure averaging | Technician T0C11 | 19 | C | 19/rf-exposure-safety |  |
| 1280 | RF vs ionising radiation (no DNA damage) | Technician T0C12 | 19 | P | 19/rf-exposure-safety |  |
| 1281 | Licensee responsible for exposure compliance | Technician T0C13 | 19 | M | — |  |
| 1282 | RF heats tissue | General G0A01 | 19 | C | 19/rf-exposure-safety |  |
| 1283 | Exposure depends on duty cycle, frequency, power density | General G0A02 | 19 | C | 19/rf-exposure-safety |  |
| 1284 | Compliance methods | General G0A03 | 19 | C | 19/rf-exposure-safety |  |
| 1285 | Time averaging meaning | General G0A04 | 19 | C | 19/rf-exposure-safety | 30-/6-min averaging |
| 1286 | Action if limits exceeded (prevent exposure) | General G0A05 | 19 | P | 19/rf-exposure-safety |  |
| 1287 | Fail exemption → OET 65 evaluation | General G0A06 | 19 | C | 19/rf-exposure-safety |  |
| 1288 | Lower duty cycle permits more power | General G0A07 | 19 | C | 19/rf-exposure-safety |  |
| 1289 | Routine evaluation + restrict high-exposure areas | General G0A08 | 19 | P | 19/rf-exposure-safety |  |
| 1290 | Calibrated field-strength meter + antenna | General G0A09 | 19 | C | 02/poynting-vector-power-flow; 17/antenna-range-ota-testing |  |
| 1291 | Neighbour in main lobe: prevent pointing at them | General G0A10 | 19 | P | 19/rf-exposure-safety |  |
| 1292 | Indoor antenna: check MPE in occupied areas | General G0A11 | 19 | P | 19/rf-exposure-safety |  |
| 1293 | Stations > 1 mW time-averaged are subject to exposure rules | General G0A12 | 19 | M | — | 1.1307 1 mW exemption not stated |
| 1294 | Ground rod's primary function (lightning dissipation) | Extra E0A01 | 19 | M | — |  |
| 1295 | Neighbour must be below uncontrolled MPE | Extra E0A02 | 19 | C | 19/rf-exposure-safety | general-population limits |
| 1296 | FCC limits most restrictive at 30–300 MHz | Extra E0A03 | 19 | C | 19/rf-exposure-safety |  |
| 1297 | Multi-transmitter sites: each ≥ 5 % of MPE shares responsibility | Extra E0A04 | 19 | M | — |  |
| 1298 | Microwave hazard from high-gain antennas | Extra E0A05 | 19 | C | 19/rf-exposure-safety | EIRP-based distance |
| 1299 | Separate E and H limits below 300 MHz | Extra E0A06 | 19 | C | 02/near-field-far-field; 19/rf-exposure-safety |  |
| 1300 | "100 % tie-off" tower safety | Extra E0A07 | 19 | M | — | OOS: tower climbing |
| 1301 | What SAR measures | Extra E0A08 | 19 | C | 19/rf-exposure-safety |  |
| 1302 | Exempt equipment (handhelds sold before May 2021) | Extra E0A09 | 19 | M | — |  |
| 1303 | 80 m always needs evaluation | Extra E0A10 | 19 | P | 19/rf-exposure-safety | exemption formula only for 300–1500 MHz discussed; HF table present |
| 1304 | Lanyards to tower legs | Extra E0A11 | 19 | M | — | OOS: tower climbing |
| 1305 | Shock-absorbing lanyard above head | Extra E0A12 | 19 | M | — | OOS: tower climbing |
| 1306 | Definition of telemetry (one-way measurement) | Extra E1D01 | 19 | C | 19/amateur-radio-licensing | 97.111(b)(7) |
| 1307 | Only space telecommand may be encrypted | Extra E1D02 | 19 | C | 19/amateur-radio-licensing |  |
| 1308 | Balloon telemetry ID = call sign | Extra E1D04 | 19 | C | 19/amateur-radio-licensing | ID rules 97.119 |
| 1309 | Model-craft telecommand ≤ 1 W | Extra E1D06 | 19 | C | 19/amateur-radio-licensing | 97.215 |
| 1310 | UHF space bands (70 cm, 13 cm) | Extra E1D09 | 19 | C | 19/amateur-radio-licensing | 70 cm stated; 13 cm not |
| 1311 | Who may transmit one-way (space, beacon, telecommand) | Extra E1D12 | 19 | C | 19/amateur-radio-licensing |  |
| 1312 | SS only above 222 MHz | Extra E1F01 | 19 | P | 19/amateur-radio-licensing | 70 cm SS allowed stated; 222 MHz floor not |
| 1313 | No TX 420–430 MHz north of Line A | Extra E1F05 | 19 | C | 19/amateur-radio-licensing |  |
| 1314 | No obscured messages on mesh networks | Extra E1F09 | 19 | C | 19/amateur-radio-licensing |  |
| 1315 | Spurious limit below 30 MHz (−43 dB) | Extra E1C10 | 19 | P | 06/power-amplifiers; 19/amateur-radio-licensing | ETSI harmonic limits covered; FCC 97.307(d)/(e) values absent |
| 1316 | Max SS power (10 W PEP) | General G1E08 | 19 | C | 19/amateur-radio-licensing |  |
| 1317 | Where automatic digital stations may operate (≤ 6 m + HF segments) | General G1E11 | 19 | C | 19/amateur-radio-licensing | 97.221(b) |
| 1318 | Secondary allocation obligations | General G1A06 | 19 | C | 19/spectrum-allocation-ism-bands |  |
| 1319 | FCC power measured as PEP output | General G1C11 | 19 | C | 19/amateur-radio-licensing; 00/complex-numbers-and-phasors |  |
| 1320 | ITU Region 2 = Americas | General G1E06 | 19 | C | 19/spectrum-allocation-ism-bands |  |
| 1321 | Space station = > 50 km altitude | Technician T1A07 | 19 | C | 19/amateur-radio-licensing |  |
| 1322 | Broadcasting prohibited | Technician T1D02 | 19 | C | 19/amateur-radio-licensing | 97.113(b) |
| 1323 | Encoded messages only for space/model-craft control | Technician T1D03 | 19 | C | 19/amateur-radio-licensing | 97.215 note |
| 1324 | No on-air ID needed for model-craft control | Technician T1D11 | 19 | C | 19/amateur-radio-licensing |  |
| 1325 | ID every 10 min and at end | Technician T1F03 | 19 | C | 19/amateur-radio-licensing |  |
| 1326 | Tech max power above 30 MHz (1500 W) | Technician T1B12 | 19 | C | 19/amateur-radio-licensing | 1.5 kW PEP |
