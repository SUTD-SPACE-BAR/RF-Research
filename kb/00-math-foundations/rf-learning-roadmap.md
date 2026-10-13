---
title: RF learning roadmap — from zero to graduate level for radios, radars, LoRa links and antennas (stages, books by audience, free courses, video channels, first instruments, what to build, and the KB reading order)
domain: 00-math-foundations
slug: rf-learning-roadmap
tags: [roadmap, learning-path, study-plan, beginner, books, textbooks, pozar, balanis, arrl-handbook, arrl-antenna-book, emrfd, art-of-electronics, bowick, razavi, lee, skolnik, richards, mailloux, lyons, pysdr, steer, orfanidis, free-courses, mit-ocw, videos, w2aew, the-signal-path, rohde-schwarz, keysight, andreas-spiess, nanovna, tinysa, rtl-sdr, ham-licence, build-early, self-check]
prerequisites: []
related:
  - rf-concepts-for-beginners.md
  - math-roadmap-for-rf.md
  - ../20-projects-recipes/beginner-project-ladder.md
  - ../17-test-measurement/lab-setup-by-budget.md
  - ../16-simulation-tools/tool-landscape-overview.md
  - ../19-regulations-safety/amateur-radio-licensing.md
level: intro
confidence: medium
last_updated: 2026-10-02
---

# RF learning roadmap — from zero to graduate level

This page is the **practice** companion to the [maths roadmap](math-roadmap-for-rf.md): that page says
which maths to learn in which order; this one says what to *read, watch, buy and build* at each stage,
which book suits whom, and in which order to read this knowledge base. It deliberately does not repeat
the maths stages — each stage below names the maths stage it needs.

Where a recommendation rests on what learners report working for them, it is marked **community
consensus (n threads)**: counts are from the 53 learning-path threads whose comments were machine-read in
the Reddit sweep ([gaps/D2-reddit.md §4](../../gaps/D2-reddit.md)) — a ranking signal, not a survey.

## Questions this page answers
- Where do I start learning RF if I want to build radios, radars, LoRa links and antennas?
- Should I read Pozar first, or build something first?
- Which RF book is right for me — Pozar, Balanis, the ARRL Handbook, EMRFD, Bowick, Razavi, Lee, Skolnik, Richards, Mailloux, Lyons or PySDR?
- Which chapters of Pozar should a builder read first, and which can wait?
- Are there good free RF courses and free textbooks?
- Which YouTube channels are worth watching for RF and test equipment?
- What instruments should I buy first, and in what order?
- I come from physics / software / ham radio / embedded avionics — where is my entry point?
- In what order should I read this knowledge base's domains?
- How do I know I am ready to move to the next stage? Is there a "LeetCode for RF"?

## TL;DR
- **Build and measure from week one.** The single most repeated advice is to get an SDR or a NanoVNA and make an antenna early, alongside the reading (community consensus, 16 threads). This KB's [project ladder](../20-projects-recipes/beginner-project-ladder.md) gives 11 graded builds.
- **Five stages**: (0) curious beginner → (1) hobby builder / ham → (2) EE student or serious builder → (3) working RF/microwave designer → (4) specialist / graduate (antennas, PA/LNA, radar, arrays, SDR/DSP, PCB/EMC, GNSS). Each stage below lists maths stage, KB pages, one or two books, a free course or video series, a purchase and a project.
- **Books by audience**: start practical with the **ARRL Handbook**, **Bowick** or **EMRFD**; take **Pozar** as the core microwave reference *with a goal*, not cover to cover; **Balanis** (reference) or **Stutzman & Thiele** (gentler) for antennas; **Skolnik** then **Richards** for radar; **Mailloux** for arrays; **Razavi** and **Lee** for RF ICs; **Lyons** plus the free **PySDR** for DSP/SDR. Pozar is the most named book by far (25 of 53 threads) and also the most complained about.
- **Free, high-quality material exists**: MIT OCW 6.013 (EM), 6.003 (signals), 6.450 (digital comms), 6.776 (RF circuits), Lincoln Laboratory's radar course and "build a small radar" course; Steer's 5-volume *Microwave and RF Design* (open access, 2019); Orfanidis' *Electromagnetic Waves and Antennas*; PySDR; Smith's *DSP Guide*.
- **First instruments** (≈ US$300 in 2026): RTL-SDR (≈ US$40), NanoVNA-H4 (≈ US$110), tinySA Ultra (≈ US$120–130), plus a 50 Ω load, a 30–40 dB power attenuator and good SMA cables ([lab set-up by budget](../17-test-measurement/lab-setup-by-budget.md)).
- **A ham licence** is a cheap, structured way into practical RF and the only legal route to high-power experiments on 70 cm in Singapore (community consensus, 8 threads; [amateur licensing](../19-regulations-safety/amateur-radio-licensing.md)).
- **Self-check**: each stage ends with questions; if you can answer them with numbers, move on. The KB's "Questions this page answers" lists and the `tools/verify/` scripts are the closest thing to a "LeetCode for RF".

## Intuition (no math)
RF is learned in a loop: **read** a little, **predict** a number, **build** something, **measure** it,
and **explain** the difference. The theory-only route stalls because RF is full of second-order
effects — parasitics, ground currents, cable radiation — that only show up on the bench; the
build-only route stalls because without impedance, decibels and noise you cannot tell whether a result
is good. People who get good at RF keep both halves moving.

Your starting point matters less than it seems. A **ham operator** has the bench intuition but often
lacks the complex-number maths. A **physics student** knows Maxwell's equations but has never matched an
amplifier or read a datasheet; they should start with circuits and measurement. A **software person** is
fastest through SDR and DSP — sampling, I/Q and filters — then moves down into the hardware. An **EE
student** has the circuit maths and needs EM, microwave networks and a lab project. An **embedded or
avionics engineer** (the KB's reader) already ships radios as modules; the step up is to understand what
is inside the module, the antenna and the link, so that failures can be predicted rather than
discovered (community consensus, entry-point advice in 4 thread clusters; D2 §4d).

## The math
The maths for each stage is in [math-roadmap-for-rf](math-roadmap-for-rf.md) (stages 0–5). Below,
"maths stage" refers to that page.

### Level 1 — the five stages at a glance

| Stage | Who | Maths stage | Learn (KB pages) | Read | Watch / course | Buy | Build (ladder #) |
|---|---|---|---|---|---|---|---|
| **0 — Curious beginner** | no electronics background | 0 (algebra, logs) | [concepts tour](rf-concepts-for-beginners.md), [decibels](decibels-and-log-units.md), [spectrum allocation](../19-regulations-safety/spectrum-allocation-ism-bands.md) | ARRL Handbook ch. 2–3; a ham licence study guide | W2AEW basics (scope, spectrum, "what is…"); Andreas Spiess LoRa/SDR introductions | RTL-SDR + dipole kit (≈ US$40) | 1 (FM + ADS-B), 2 (weather satellite) |
| **1 — Hobby builder / ham** | can solder, reads schematics | 0–1 (dB, complex numbers) | [lumped elements](../01-circuit-theory/lumped-elements-impedance-admittance.md), [resonance and Q](../01-circuit-theory/resonance-and-q.md), [coax](../03-transmission-lines-matching/coax-and-cables.md), [reflections/VSWR](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md), [antenna fundamentals](../08-antennas/antenna-fundamentals.md), [dipoles](../08-antennas/dipoles-and-monopoles.md), [Friis](../09-propagation-link-budget/friis-free-space-path-loss.md), [NanoVNA practice](../17-test-measurement/nanovna-librevna-practical.md) | ARRL Handbook ch. 5, 20, 21; ARRL Antenna Book V1-1, V1-2, V4-5; EMRFD ch. 1 and 7; Bowick (components, resonance, matching chapters) | W2AEW (VNA, SWR, baluns); Andreas Spiess (antennas, NanoVNA tests); Rohde & Schwarz / Keysight "fundamentals" videos | NanoVNA-H4, tinySA Ultra, 50 Ω load, attenuators | 3 (433 MHz dipole), 4 (cable), 5 (tinySA on LoRa), 6 (range test) |
| **2 — EE student / serious builder** | circuits course done | 1–3 (phasors, Fourier/Laplace, probability) | [Smith chart](../03-transmission-lines-matching/smith-chart.md), [S-parameters](../03-transmission-lines-matching/s-parameters.md), [matching](../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md), [noise figure](../07-noise-linearity/noise-figure-and-friis.md), [link budget](../09-propagation-link-budget/link-budget-methodology.md), [filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md), [IQ baseband](../14-sdr-dsp/iq-complex-baseband.md), [LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md) | Pozar ch. 2, 4, 5, 8, 10 (read with a goal; map below); AoE ch. 1, 8 and App. H; Lyons ch. 1–3, 8 or PySDR | MIT OCW 6.013 (EM) and 6.003 (signals); The Signal Path (instrument teardowns) | step attenuator, SAW/LC filters, a small LNA board, HackRF or Pluto | 7 (HB100), 8 (2.4 GHz patch), 9 (DOA), [band-pass filter](../20-projects-recipes/bandpass-filter-design-walkthrough.md) |
| **3 — RF/microwave designer** | designs boards with radios | 3–5 | [LNA](../06-rf-circuits/lna-design.md), [PA](../06-rf-circuits/power-amplifiers.md), [stability](../06-rf-circuits/amplifier-stability-and-biasing.md), [VCO/PLL](../06-rf-circuits/vco-and-pll-synthesizers.md), [mixers](../06-rf-circuits/mixers.md), [RF layout](../13-pcb-rf-layout-emc/rf-layout-rules.md), [EMC](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md), [openEMS](../16-simulation-tools/openems-workflow.md), [VNA calibration](../17-test-measurement/vna-fundamentals-calibration.md) | Pozar ch. 6, 7, 11–13; Razavi ch. 2, 4–6; Balanis ch. 2, 4, 6, 14; Lee *Planar Microwave Engineering*; Bogatin / Ott for SI/EMC | MIT OCW 6.776 (RF circuits); Keysight / R&S application-note webinars | LiteVNA or LibreVNA, used bench SA, calibrated pads, power sensor | [LoRa telemetry link](../20-projects-recipes/lora-rocket-telemetry-link.md), [ground station](../20-projects-recipes/ground-station-tracking-yagi.md), [LNA walkthrough](../20-projects-recipes/lna-design-walkthrough.md), [GNSS front end](../20-projects-recipes/gnss-front-end-design.md) |
| **4 — Specialist / graduate** | research or product lead | 4–5 + graduate topics | domain tracks below | Skolnik + Richards (radar); Mailloux (arrays); Balanis in full (antennas); Razavi + Lee CMOS (RFIC); Proakis/Oppenheim (comms/DSP); Kaplan & Hegarty (GNSS) | MIT LL RES.LL-001 and RES.LL-003 (radar); Berkeley EE142 / TU Delft notes (D4 §3) | noise source, phase-noise capability, EM licences as needed | [FMCW radar](../20-projects-recipes/fmcw-radar-build.md), [phased-array starter](../20-projects-recipes/phased-array-starter-build.md), [SDR receiver](../20-projects-recipes/sdr-receiver-build.md) |

Chapter numbers are from the tables of contents mapped in [gaps/D4-curriculum.md §3](../../gaps/D4-curriculum.md)
(Pozar 4th ed., Balanis 4th ed., ARRL Handbook 96th-ed. structure, Antenna Book 24th ed., EMRFD, AoE 3rd ed.,
Lyons 3rd ed., Razavi 2nd ed., Skolnik 3rd ed., Richards 2nd ed., Mailloux 3rd ed.).

### Level 2 — which book for whom

| Book (edition) | Level | Prerequisites | Strengths | Weak for | Read first |
|---|---|---|---|---|---|
| **ARRL**, *The ARRL Handbook for Radio Communications* (annual; 101st ed. 2024) | beginner → intermediate | algebra; curiosity | everything a builder meets in one volume: RF technique, filters, receivers, transmitters, transmission lines, antennas, construction; practical numbers | derivations; microwave design | ch. 2–3 (fundamentals), 5 (RF techniques), 20 (lines), 21 (antennas), 23 (construction) |
| **ARRL**, *The ARRL Antenna Book* (25th ed. 2023; 24th ed. 2019 mapped) | beginner → intermediate | dB, basic circuits | practical antenna systems, ground effects, Yagis, VHF/UHF and space antennas, feedlines, measurement and troubleshooting | rigorous theory | V1-1 (fundamentals), V1-2 (dipoles/monopoles), V3-1 and V3-3 (VHF/UHF, space), V4-1 (lines), V4-5 (measurements) |
| **Hayward, Campbell & Larkin**, *Experimental Methods in RF Design* (ARRL 2003/2009) | intermediate | basic transistor circuits | design-measure-iterate method; home-built test gear (return-loss bridge, step attenuator, power meter); amplifiers, filters, oscillators, mixers, receivers | microwave, modern ICs | ch. 1 (basic investigations), ch. 7 (measurement equipment), then ch. 2–5 as you build |
| **Horowitz & Hill**, *The Art of Electronics* (3rd ed. 2015) | beginner → intermediate | algebra | the best general analog reference: real components, transistors, op-amps, low-noise design | RF beyond a few hundred MHz | ch. 1 (foundations), ch. 8 (low-noise), App. H (transmission lines) |
| **Bowick (with Blyler & Ajluni)**, *RF Circuit Design* (2nd ed. 2008) | beginner → intermediate | basic circuits, a little complex arithmetic | the gentlest route into components at RF, resonant circuits, filters and L-network matching with worked numbers | noise, systems, EM | the components, resonant-circuit and impedance-matching chapters (recalled — check the ToC) |
| **Pozar**, *Microwave Engineering* (4th ed. 2012; international adaptation 2021) | senior undergraduate → graduate | EM (Maxwell, plane waves), circuits, phasors, calculus | the standard reference for lines, waveguides, S-parameters, matching, couplers, filters, noise, amplifiers, oscillators/mixers; many problems | "how to build it"; hard as a first book (community consensus: most named, 25 threads, and most complained about) | ch. 2 (lines, Smith chart), 4 (network analysis), 5 (matching), then 8 (filters), 10 (noise), 12 (amplifiers) — see the map below |
| **Lee**, *Planar Microwave Engineering* (Cambridge 2004) | intermediate | circuits, some EM | intuition-first treatment of planar (PCB) microwave circuits and measurement, with history | systems | as a companion to Pozar ch. 2–5 (recalled; 3 threads) |
| **Balanis**, *Antenna Theory: Analysis and Design* (4th ed. 2016) | senior undergraduate → graduate | vector calculus, EM | the antenna reference: parameters, dipoles, loops, arrays, MoM, horns, patches, measurement (15 threads) | quick practical answers | ch. 2 (fundamental parameters), 4 (dipoles), 6 (arrays), 14 (patches), 17 (measurements) |
| **Stutzman & Thiele**, *Antenna Theory and Design* (3rd ed. 2012) | undergraduate | EM basics | gentler course text than Balanis (5 threads) | depth | early chapters in course order |
| **Razavi**, *RF Microelectronics* (2nd ed. 2011) | graduate | transistor circuits, Laplace, noise | system-to-transistor view of transceivers: nonlinearity, architectures, LNAs, mixers, oscillators, PLLs, PAs (7 threads) | discrete/board-level work | ch. 2 (basic concepts), 4 (transceiver architectures), then 5–6 (LNA, mixers) |
| **Lee**, *The Design of CMOS Radio-Frequency Integrated Circuits* (2nd ed. 2004) | graduate | MOS devices, feedback | very readable on noise, LNAs, oscillators and phase noise (ISF) | discrete design | ch. 11 (noise), 12 (LNA), 17–18 (oscillators, phase noise) |
| **Skolnik**, *Introduction to Radar Systems* (3rd ed. 2001) | undergraduate → graduate | dB, probability basics | the classic system view: radar equation, MTI, tracking, detection, clutter, propagation, antennas, transmitters, receivers (3 threads; most comments) | modern signal processing | ch. 1–2 (radar equation), then 3 (MTI/pulse-Doppler) and 5 (detection) |
| **Richards**, *Fundamentals of Radar Signal Processing* (2nd ed. 2014) | graduate | DSP, probability | signal models, waveforms, matched filtering, Doppler processing, detection, CRLB/tracking, SAR, STAP | hardware | ch. 1–4 (models, data acquisition, waveforms), 6 (detection) |
| **Mailloux**, *Phased Array Antenna Handbook* (3rd ed. 2018) | graduate | antennas, Fourier | the practical array reference: patterns, synthesis, element coupling, errors, multiple beams | introductory examples | ch. 1–3 (requirements, patterns, synthesis), 6 (mutual impedance), 7 (errors) |
| **Lyons**, *Understanding Digital Signal Processing* (3rd ed. 2010) | beginner → intermediate | algebra, complex numbers | the clearest DSP explanations: sampling, DFT/FFT, filters, quadrature signals, multirate, "DSP tricks" (5 threads) | proofs | ch. 1–3 (sequences, sampling, DFT), 8 (quadrature signals), 10 (sample-rate conversion) |
| **Lichtman**, *PySDR: A Guide to SDR and DSP using Python* (free online) | beginner → intermediate | Python | hands-on SDR: IQ, sampling, filters, synchronisation, real hardware (3 threads) | RF hardware | the IQ sampling, frequency domain and filters chapters, then the chapter for your SDR |
| *Free alternatives*: **Steer**, *Microwave and RF Design* (3rd ed. 2019, 5 vols, open access); **Orfanidis**, *Electromagnetic Waves and Antennas* (free); **Smith**, *The Scientist and Engineer's Guide to DSP* (free) | intermediate | as Pozar / Balanis / Lyons | complete, free and searchable | fewer worked builds | Steer vol. 2 (lines), vol. 3 (networks); Orfanidis on lines and antennas |

**Pozar with a goal — chapter → KB map for a builder** (read the bold chapters first; the rest when a
project needs them):

| Pozar ch. (4th ed.) | Topic | KB pages | Builder priority |
|---|---|---|---|
| 1 | EM theory | [02 domain](../02-electromagnetics/_index.md) | skim; return when antennas need it |
| **2** | **transmission lines, Smith chart, λ/4, mismatch** | [telegrapher](../03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md), [Smith chart](../03-transmission-lines-matching/smith-chart.md), [reflections](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md) | first |
| 3 | lines and waveguides (3.7–3.8 microstrip/stripline matter most) | [planar lines](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md), [waveguides](../02-electromagnetics/waveguides-and-cavity-resonators.md) | microstrip now, waveguides later |
| **4** | **Z/Y/S/ABCD, signal-flow graphs** | [S-parameters](../03-transmission-lines-matching/s-parameters.md), [two-ports](../01-circuit-theory/two-port-networks-zyh-abcd.md), [signal-flow graphs](../03-transmission-lines-matching/signal-flow-graphs-mason.md) | first (4.7–4.8 can wait) |
| **5** | **matching and tuning, Bode–Fano** | [matching](../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md), [Bode–Fano](../03-transmission-lines-matching/broadband-matching-bode-fano.md) | first |
| 6 | resonators | [resonance and Q](../01-circuit-theory/resonance-and-q.md), [cavities](../02-electromagnetics/waveguides-and-cavity-resonators.md) | 6.1–6.2 now |
| 7 | dividers and couplers | [couplers](../06-rf-circuits/couplers-dividers-combiners.md) | when you need a splitter/hybrid |
| **8** | **filters** | [filter prototypes](../01-circuit-theory/passive-filter-design-prototypes.md), [RF filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md) | early |
| 9 | ferrites | [circulators/isolators](../06-rf-circuits/circulators-isolators.md) | later |
| **10** | **noise and nonlinear distortion** | [noise figure](../07-noise-linearity/noise-figure-and-friis.md), [nonlinearity](../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md), [dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md) | early |
| 11 | devices | [05 domain](../05-analog-electronics/_index.md) | as needed |
| **12** | **amplifier design** | [stability](../06-rf-circuits/amplifier-stability-and-biasing.md), [LNA](../06-rf-circuits/lna-design.md), [PA](../06-rf-circuits/power-amplifiers.md) | when you design an LNA |
| 13 | oscillators, phase noise, mixers | [VCO/PLL](../06-rf-circuits/vco-and-pll-synthesizers.md), [phase noise](../07-noise-linearity/phase-noise-and-jitter.md), [mixers](../06-rf-circuits/mixers.md) | later |
| 14 | systems: antennas, links, radar, propagation | [08](../08-antennas/_index.md), [09](../09-propagation-link-budget/_index.md), [11](../11-radar/_index.md) | read early for motivation |

### Level 3 — specialist tracks (stage 4) and graduate topics

| Track | Core reading | KB entry | Graduate-level next step |
|---|---|---|---|
| Antennas | Balanis ch. 2–8, 12–14; ARRL Antenna Book for practice | [08 domain](../08-antennas/_index.md), [antenna simulation](../08-antennas/antenna-simulation-nec-openems.md) | Green's functions, equivalence and reciprocity derivations (D4 broken rung) |
| LNA / PA / RF circuits | Pozar ch. 10–13; Razavi; Gonzalez *Microwave Transistor Amplifiers*; Cripps *RF Power Amplifiers* | [06](../06-rf-circuits/_index.md), [07](../07-noise-linearity/_index.md) | noise parameters and correlation matrices; Volterra/memory models |
| Radar | Skolnik → Richards; MIT LL radar courses | [11](../11-radar/_index.md) | ambiguity functions, CFAR, tracking ([estimation](estimation-theory-ml-map-crb.md)) |
| Phased arrays | Mailloux; Balanis ch. 6 | [12](../12-phased-arrays/_index.md) | adaptive beamforming, array calibration, synthesis |
| SDR / DSP | Lyons → Oppenheim & Schafer; PySDR; harris *Multirate Signal Processing* | [14](../14-sdr-dsp/_index.md), [z-transform](z-transform-and-discrete-time-systems.md) | multirate design, synchronisation, FPGA implementation |
| Comms / LoRa | Proakis & Salehi; Tse & Viswanath (free); Semtech app notes | [10](../10-comms-modulation/_index.md), [15](../15-lora-ism-radios/_index.md) | detection/estimation theory, coding |
| PCB / SI / EMC | Bogatin *Signal and Power Integrity — Simplified*; Ott *EMC Engineering* | [13](../13-pcb-rf-layout-emc/_index.md) | full-wave board simulation and validation |
| GNSS | Kaplan & Hegarty *Understanding GPS/GNSS* (3rd ed. 2017); Misra & Enge | [21](../21-gnss/_index.md) | tracking loops, RTK/PPP |

**Self-check questions — move on when you can answer with numbers** (each is answered on the linked page):
- *Stage 0*: What is the wavelength at 433 MHz, and roughly how long is a dipole for it? What is 33 dBm in watts? Why is RF non-ionising? → [concepts](rf-concepts-for-beginners.md)
- *Stage 1*: What VSWR corresponds to 10 dB return loss, and how much power is lost? Why does 10 m of RG-58 hide an antenna's mismatch? How do you measure a cable's velocity factor? → [reflections](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md), [NanoVNA](../17-test-measurement/nanovna-librevna-practical.md)
- *Stage 2*: Design an L-network from 12 − j40 Ω to 50 Ω at 433 MHz. What is the noise figure of LNA + SAW + RTL-SDR in both orders? What sensitivity does LoRa SF9/125 kHz give with NF 6 dB? → [matching](../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md), [Friis cascade](../07-noise-linearity/noise-figure-and-friis.md), [LoRa link budget](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md)
- *Stage 3*: Is a given transistor unconditionally stable at 1.575 GHz (K, μ)? How much isolation does a GNSS receiver need from a 2 W 433 MHz transmitter's harmonics? Why does an openEMS patch resonate 2 % off the closed form? → [stability](../06-rf-circuits/amplifier-stability-and-biasing.md), [GNSS front end](../20-projects-recipes/gnss-front-end-design.md), [simulation validation](../16-simulation-tools/simulation-validation.md)
- *Stage 4*: Derive the range resolution and maximum unambiguous range of an FMCW radar from its chirp parameters; what grating-lobe condition limits an 8-element array's scan? → [FMCW](../11-radar/fmcw-radar.md), [grating lobes](../12-phased-arrays/beam-steering-grating-lobes.md)

## Design equations & rules of thumb
| Rule | Why (source) |
|---|---|
| Build something in the first month; keep one project running at every stage | the most repeated learner advice (community consensus, 16 threads); bench effects are invisible on paper |
| Read Pozar with a question, chapter by chapter, not cover to cover | community consensus (Pozar threads); the map above gives a builder's order |
| Buy a VNA before a spectrum analyzer; buy pads and a dummy load with the first transmitter | antennas and matching are the first thing to fail; a transmitter into nothing or into an instrument destroys hardware ([lab set-up](../17-test-measurement/lab-setup-by-budget.md)) |
| Simulate after you can measure | "simulation is not a substitute for the bench" recurs in learner threads (D2 §4d); validate every model ([simulation validation](../16-simulation-tools/simulation-validation.md)) |
| Pair each chapter with a KB verify script and change one parameter | predicting before running builds intuition ([maths roadmap](math-roadmap-for-rf.md)) |
| Get a licence before you transmit beyond licence-exempt limits | legality and structured learning (8 threads; [Singapore rules](../19-regulations-safety/singapore-imda-rules.md)) |
| Time budget: stage 0 a few weeks; stage 1 2–4 months; stage 2 a year of study alongside a degree; stage 3 years of design work | author's judgement (unsourced), consistent with the maths roadmap's estimates |

## Worked examples — four learning plans
**1. Embedded / avionics engineer (the KB's reader: flies EBYTE LoRa modules and u-blox GNSS).** Weeks
1–2: [concepts](rf-concepts-for-beginners.md), [decibels](decibels-and-log-units.md),
[LoRa link budget](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md); ladder projects 1, 3 and 5
(SDR, NanoVNA dipole, tinySA look at the flight radio). Weeks 3–6: [phasors](complex-numbers-and-phasors.md),
[reflections](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md),
[Smith chart](../03-transmission-lines-matching/smith-chart.md), Pozar ch. 2 and 5,
[antennas on rockets](../08-antennas/antennas-on-rockets.md); projects 4 and 6 (cable, range test).
Weeks 7–12: [noise figure](../07-noise-linearity/noise-figure-and-friis.md),
[ground station](../15-lora-ism-radios/ground-station-design.md),
[RF layout](../13-pcb-rf-layout-emc/rf-layout-rules.md); build the
[LoRa telemetry link recipe](../20-projects-recipes/lora-rocket-telemetry-link.md) and the
[ground station](../20-projects-recipes/ground-station-tracking-yagi.md) with pre-registered predictions.

**2. Software developer.** Start with PySDR and an RTL-SDR (project 1), then Lyons ch. 1–3 and 8,
[sampling](../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md), [IQ](../14-sdr-dsp/iq-complex-baseband.md),
[FFT](../14-sdr-dsp/fft-spectral-analysis-windows.md), [software demodulation](../14-sdr-dsp/software-demodulation.md);
decode APRS, AIS, LoRa ([reception recipes](../14-sdr-dsp/sdr-gain-staging-and-reception-recipes.md)). Only then
move down into hardware: [gain staging](../14-sdr-dsp/sdr-gain-staging-and-reception-recipes.md), [front-end
protection](../14-sdr-dsp/sdr-front-end-protection-and-filtering.md), [noise figure](../07-noise-linearity/noise-figure-and-friis.md),
and a NanoVNA antenna project. Software people are fastest through SDR/DSP (D2 §4d).

**3. Physics student.** You know Maxwell; you do not know parts. Skip most of 02; spend the time on
[real components](../04-real-components-hf/_index.md), [lumped circuits](../01-circuit-theory/_index.md),
AoE ch. 1 and 8, and the bench (projects 3–5). Then Pozar ch. 2, 4, 5 go quickly, and Balanis is natural
reading. Pair theory with measurement from the start (D2 §4d entry-point advice).

**4. Complete beginner or new ham.** Concepts page → a licence course (the exam syllabus covers safety,
rules and basic RF; [amateur licensing](../19-regulations-safety/amateur-radio-licensing.md)) → ARRL
Handbook ch. 2–3 → RTL-SDR projects 1–2 → NanoVNA dipole (project 3). Learn complex numbers
([maths stage 1](math-roadmap-for-rf.md)) before attempting Pozar.

## Practical notes

### The KB reading order (first pass, then by domain)
**First pass (beginner → builder):** [concepts tour](rf-concepts-for-beginners.md) →
[decibels](decibels-and-log-units.md) → [phasors](complex-numbers-and-phasors.md) →
[lumped elements](../01-circuit-theory/lumped-elements-impedance-admittance.md) →
[reflections](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md) →
[coax](../03-transmission-lines-matching/coax-and-cables.md) →
[antenna fundamentals](../08-antennas/antenna-fundamentals.md) →
[Friis](../09-propagation-link-budget/friis-free-space-path-loss.md) →
[thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md) →
[LoRa link budget](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md) →
[NanoVNA practice](../17-test-measurement/nanovna-librevna-practical.md) →
[Singapore rules](../19-regulations-safety/singapore-imda-rules.md) →
[project ladder](../20-projects-recipes/beginner-project-ladder.md).

**Then by domain** — each `_index.md` has its own beginner → advanced reading order:

| # | Domain | Read it when | Depends on |
|---|---|---|---|
| 00 | [Maths foundations](_index.md) | throughout; start with the [maths roadmap](math-roadmap-for-rf.md) | — |
| 01 | [Circuit theory](../01-circuit-theory/_index.md) | stage 1 | 00 stage 1 |
| 02 | [Electromagnetics](../02-electromagnetics/_index.md) | stage 2 (physicists can skim) | 00 stage 4 |
| 03 | [Transmission lines and matching](../03-transmission-lines-matching/_index.md) | stage 1–2 — the core of RF | 01 |
| 04 | [Real components at HF](../04-real-components-hf/_index.md) | stage 1–2, before designing boards | 01 |
| 05 | [Analog electronics](../05-analog-electronics/_index.md) | stage 2 | 01, 04 |
| 06 | [RF circuits](../06-rf-circuits/_index.md) | stage 2–3 | 03, 05, 07 |
| 07 | [Noise and linearity](../07-noise-linearity/_index.md) | stage 2 | 00 stage 3 |
| 08 | [Antennas](../08-antennas/_index.md) | stage 1 (fundamentals) → 3 | 02, 03 |
| 09 | [Propagation and link budgets](../09-propagation-link-budget/_index.md) | stage 1 (Friis) → 2 | 00 dB |
| 10 | [Communications and modulation](../10-comms-modulation/_index.md) | stage 2 | 00 stages 2–3 |
| 11 | [Radar](../11-radar/_index.md) | stage 3–4 | 07, 09, 10 |
| 12 | [Phased arrays](../12-phased-arrays/_index.md) | stage 3–4 | 08, 00 Fourier/matrices |
| 13 | [PCB, RF layout and EMC](../13-pcb-rf-layout-emc/_index.md) | stage 2–3, before your first RF board | 03, 04 |
| 14 | [SDR and DSP](../14-sdr-dsp/_index.md) | stage 1 (recipes) → 3 | 00 Fourier |
| 15 | [LoRa and ISM radios](../15-lora-ism-radios/_index.md) | stage 1–3 (the reader's daily work) | 07, 09, 10 |
| 16 | [Simulation tools](../16-simulation-tools/_index.md) | stage 2–3, after you can measure | 03, 08 |
| 17 | [Test and measurement](../17-test-measurement/_index.md) | stage 1 onwards | 03 |
| 18 | [Components and parts](../18-components-parts/_index.md) | stage 2–3, when choosing parts | 04, 06 |
| 19 | [Regulations and safety](../19-regulations-safety/_index.md) | stage 0–1, before transmitting | — |
| 20 | [Projects and recipes](../20-projects-recipes/_index.md) | every stage (start with the [ladder](../20-projects-recipes/beginner-project-ladder.md)) | varies |
| 21 | [GNSS](../21-gnss/_index.md) | stage 2–3 | 07, 10 |

### Free courses and free texts
- **MIT OpenCourseWare**: 6.013 *Electromagnetics and Applications* (2009) — EM, lines, antennas;
  6.003 *Signals and Systems* (2011); 6.450 *Principles of Digital Communications I* (2006);
  6.776 *High Speed Communication Circuits* (Lee & Perrott, 2005) — RF circuits, noise, PLLs;
  Lincoln Laboratory RES.LL-001 *Introduction to Radar Systems* (2007) and RES.LL-003 *Build a Small Radar
  System* (2011, the "coffee-can radar"); maths courses 18.01/18.02/18.03/18.06 (via the
  [maths roadmap](math-roadmap-for-rf.md)). (4 threads name MIT/Stanford/Berkeley/NPTEL lectures; D4 §3
  maps 6.013, 6.776 and the LL courses against the KB.)
- **Other university material** mapped in D4: Stanford EE133/EE252/EE359 notes, Berkeley EE142
  (Niknejad), Georgia Tech ECE 6360, TU Delft and ETH Zürich antenna/microwave courses; NPTEL (IIT) hosts
  full video courses on microwave engineering and antennas.
- **MOOCs and vendor curricula**: TU Eindhoven's *Microwave Engineering and Antennas* (Coursera);
  Keysight *RF & Microwave Fundamentals* eLearning; Rohde & Schwarz Technology Academy and knowledge
  centre (D4 §3.28).
- **Free textbooks**: Steer, *Microwave and RF Design* (3rd ed., 2019, five volumes, CC BY-NC, NC State
  University Libraries); Orfanidis, *Electromagnetic Waves and Antennas* (Rutgers); Lichtman, *PySDR*;
  S. W. Smith, *The Scientist and Engineer's Guide to Digital Signal Processing* (dspguide.com);
  Tse & Viswanath, *Fundamentals of Wireless Communication* (free draft).
- **Reference sites**: Microwaves101 (rules of thumb; 5 threads), radartutorial.eu (radar basics).

### Video channels (channel and topic names only)
| Channel | Topics worth starting with | Signal |
|---|---|---|
| **W2AEW** (Alan Wolke) | oscilloscope and spectrum-analyzer basics, VNA and SWR measurement, baluns, transmission lines, "back to basics" circuits | 9 threads |
| **The Signal Path** (Shahriar Shahramian) | instrument teardowns and repairs, microwave/mm-wave hardware, RFIC tours, measurement deep dives | 7 threads |
| **Rohde & Schwarz** | spectrum-analysis, network-analysis, power and noise-figure measurement fundamentals; modulation and 5G basics | 5 threads |
| **Keysight** | RF and microwave measurement fundamentals, VNA calibration, signal-integrity basics | 4 threads |
| **Andreas Spiess** (the guy with the Swiss accent) | LoRa and Meshtastic range and antenna tests, NanoVNA and tinySA introductions, ESP32 radios | named in Meshtastic's antenna-testing docs; not counted in D2 |
| Marshall Bruner RF; EEVblog | animated explainers (IQ, radar equation, pulse compression, P1dB); bench basics and teardowns | 7 high-scoring r/rfelectronics posts; general |

### First instruments (and why in this order)
1. **RTL-SDR** (Blog V3 or V4L, ≈ US$35–40; the V4 is end-of-life): see the spectrum, receive real signals,
   learn gain and noise ([hardware survey](../14-sdr-dsp/sdr-hardware-survey.md)).
2. **NanoVNA-H4** (≈ US$110; good to ~900 MHz; LiteVNA for GNSS and 2.4 GHz): antennas, cables, filters,
   matching — the first thing that fails in a real system ([NanoVNA practice](../17-test-measurement/nanovna-librevna-practical.md)).
3. **tinySA Ultra** (≈ US$120–130): is it transmitting, how much, where are the harmonics; absolute max
   input +6 dBm, so always behind ≥ 40 dB of rated attenuation for a 1–2 W LoRa module
   ([spectrum analyzers](../17-test-measurement/spectrum-analyzers.md)).
4. **Accessories**: 50 Ω load, 30–40 dB / 2 W attenuator, 10 dB pad, SMA adaptors and a torque wrench,
   RG-316 jumpers — 15–25 % of the budget ([lab set-up by budget](../17-test-measurement/lab-setup-by-budget.md)).
Community consensus names the NanoVNA (9 threads), RTL-SDR (4), tinySA (4), HackRF (3) and Pluto (2).

### "Build something early"
Pick the lowest ladder rung you cannot yet explain with numbers, build it this week, and write down a
prediction first (pre-registration, as the team's engineering ethos requires). The
[project ladder](../20-projects-recipes/beginner-project-ladder.md) gives eleven rungs from an RTL-SDR
FM receiver to a two-channel direction finder, each with kit, cost, steps and what to measure.

## Common mistakes & misconceptions
- **"I must finish Pozar (and all the maths) before I build anything."** Learners who succeed build in
  parallel; circuit-level RF needs maths stages 0–3 only (D2 §3d, ◐ before this page; [maths roadmap](math-roadmap-for-rf.md)).
- **"You need an expensive lab to learn RF."** A ≈ US$300 kit covers 433/915 MHz antenna, cable and
  transmitter work ([lab set-up by budget](../17-test-measurement/lab-setup-by-budget.md)).
- **"Simulation can replace measurement."** Every simulation must be validated against an independent
  answer; material and geometry tolerances dominate real errors ([tool landscape](../16-simulation-tools/tool-landscape-overview.md)).
- **"Balanis/Pozar are the only real books."** They are references; the ARRL books, EMRFD and Bowick are
  where many working RF engineers first learned to build.
- **"A ham licence is only for talking on the radio."** It is the cheapest structured RF course and the
  legal route to higher-power experiments.
- **"Watching videos is learning."** Videos give the picture; only predicting and measuring a number makes
  it stick — pair each video with a bench check.
- **"Learn commercial EM tools first because employers use them."** Learn the physics and the free tools
  (NEC, openEMS, scikit-rf); commercial tools are learned on the job (D2 §4c: mostly career threads).

## How to simulate / verify
- Each stage's self-check questions are answered with numbers on the linked pages; most of those numbers
  are reproduced by `tools/verify/*.py` (run the ones for the domain you are studying).
- The beginner numbers used here and on the concepts page: `python3 tools/verify/e6_beginner_numbers.py`.
- Track progress by keeping a lab notebook of predictions vs measurements for each ladder project.

## Open questions / gaps
- Thread counts are regex-based rankings from one Reddit sweep (53 threads); Stack Exchange (D1), forum
  and YouTube (D3) learner advice may weight resources differently.
- Bowick and Lee *Planar Microwave Engineering* chapter details are recalled, not checked against a fetched
  table of contents; Pozar/Balanis/ARRL/EMRFD/AoE/Lyons/Razavi/Lee CMOS/Skolnik/Richards/Mailloux chapter
  numbers come from D4's fetched tables of contents.
- Prices are 2026 snapshots from the KB's 14/17 pages and will drift.
- No Singapore-specific course list (NUS/NTU/SUTD RF electives) has been compiled.
- Time estimates per stage are judgement, not data.

## Sources
1. This KB: [gaps/D2-reddit.md §4](../../gaps/D2-reddit.md) (community thread counts for books, videos, tools and advice; 53 threads, 1 006 comments, machine-counted), [gaps/D4-curriculum.md §3](../../gaps/D4-curriculum.md) (fetched tables of contents of Pozar, Balanis, Razavi, Lee, Mailloux, Richards, Lyons, AoE, ARRL Handbook, Antenna Book, EMRFD, Skolnik; MIT 6.013/6.776/LL course maps; MOOCs), [maths roadmap](math-roadmap-for-rf.md), [lab set-up by budget](../17-test-measurement/lab-setup-by-budget.md), [NanoVNA practice](../17-test-measurement/nanovna-librevna-practical.md), [spectrum analyzers](../17-test-measurement/spectrum-analyzers.md), [SDR hardware survey](../14-sdr-dsp/sdr-hardware-survey.md). (internal)
2. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley (2012); international adaptation (2021). (textbook)
3. C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed., Wiley (2016). (textbook)
4. W. L. Stutzman, G. A. Thiele, *Antenna Theory and Design*, 3rd ed., Wiley (2012). (textbook)
5. ARRL, *The ARRL Handbook for Radio Communications*, 101st ed. (2024; chapter structure mapped from the 96th ed., 2019). (handbook)
6. ARRL, *The ARRL Antenna Book for Radio Communications*, 25th ed. (2023; 24th ed. 2019 mapped). (handbook)
7. W. Hayward, R. Campbell, B. Larkin, *Experimental Methods in RF Design*, ARRL (2003; rev. 2009). (textbook)
8. P. Horowitz, W. Hill, *The Art of Electronics*, 3rd ed., Cambridge University Press (2015). (textbook)
9. C. Bowick, J. Blyler, C. Ajluni, *RF Circuit Design*, 2nd ed., Newnes (2008). (textbook)
10. T. H. Lee, *Planar Microwave Engineering*, Cambridge University Press (2004); *The Design of CMOS Radio-Frequency Integrated Circuits*, 2nd ed., Cambridge (2004). (textbooks)
11. B. Razavi, *RF Microelectronics*, 2nd ed., Prentice Hall (2011). (textbook)
12. M. I. Skolnik, *Introduction to Radar Systems*, 3rd ed., McGraw-Hill (2001). (textbook)
13. M. A. Richards, *Fundamentals of Radar Signal Processing*, 2nd ed., McGraw-Hill (2014). (textbook)
14. R. J. Mailloux, *Phased Array Antenna Handbook*, 3rd ed., Artech House (2018). (textbook)
15. R. G. Lyons, *Understanding Digital Signal Processing*, 3rd ed., Prentice Hall (2010). (textbook)
16. M. Lichtman, *PySDR: A Guide to SDR and DSP using Python*, https://pysdr.org (free online textbook)
17. M. Steer, *Microwave and RF Design*, 3rd ed., 5 vols., NC State University Libraries (2019), CC BY-NC 4.0. https://repository.lib.ncsu.edu/handle/1840.20/36776 ; Open Textbook Library listing https://open.umn.edu/opentextbooks/textbooks/microwave-and-rf-design-modules (open textbook)
18. S. J. Orfanidis, *Electromagnetic Waves and Antennas*, Rutgers University (free online). https://eceweb1.rutgers.edu/~orfanidi/ewa/ (textbook; server refuses automated clients)
19. S. W. Smith, *The Scientist and Engineer's Guide to Digital Signal Processing*, https://www.dspguide.com (free textbook)
20. MIT OpenCourseWare: 6.013 (Spring 2009) https://ocw.mit.edu/courses/6-013-electromagnetics-and-applications-spring-2009/ ; 6.003 (Fall 2011) https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/ ; 6.450 (Fall 2006) https://ocw.mit.edu/courses/6-450-principles-of-digital-communications-i-fall-2006/ ; 6.776 (Spring 2005) https://ocw.mit.edu/courses/6-776-high-speed-communication-circuits-spring-2005/ ; RES.LL-001 https://ocw.mit.edu/courses/res-ll-001-introduction-to-radar-systems-spring-2007/ ; RES.LL-003 https://ocw.mit.edu/courses/res-ll-003-build-a-small-radar-system-capable-of-sensing-range-doppler-and-synthetic-aperture-radar-imaging-january-iap-2011/ (lecture notes; all URLs resolved 2026-10-02)
21. D. Tse, P. Viswanath, *Fundamentals of Wireless Communication*, Cambridge (2005), free draft (via 00/_sources T18). (textbook)
22. E. Bogatin, *Signal and Power Integrity — Simplified*, 3rd ed., Pearson (2018); H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley (2009); E. D. Kaplan, C. J. Hegarty (eds.), *Understanding GPS/GNSS*, 3rd ed., Artech (2017) (mapped in D4). (textbooks)
23. Meshtastic documentation, "Antenna testing" (refers readers to Andreas Spiess' VNA tutorials). https://meshtastic.org/docs/hardware/antennas/antenna-testing/ (project docs; fetched 2026-10-02)
24. Microwaves101 https://www.microwaves101.com ; radartutorial.eu https://www.radartutorial.eu (reference websites)
