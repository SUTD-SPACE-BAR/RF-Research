# D4 — Curriculum coverage check: textbook ToCs and university syllabi (W4-D4)

Status: **complete** (2026-10-02; started 2026-09-29, paused for the usage limit, resumed). Owner: W4-D4.
Log: `research-logs/W4-D4-curriculum.md`. KB state: 200 pages at start → 229 at the final re-check (domains 13, 16,
18 completed, 20 at 3/10, 21 at 3/8 during the run; affected rows re-checked on 2026-10-02).

## 0. Method

- **Where the ToCs came from.** Publisher product pages fetched raw with `curl` (Wiley pages embed the
  full section-level ToC as text), publisher sample-page PDFs / catalogue records, and official course
  pages. WebFetch summaries were used only to *find* pages, never as the source of a section title
  (CONVENTIONS rule 8). Pirate PDF hosts that search engines returned (scribd, file lockers, personal
  wordpress uploads) were **not** used. Each per-source table names its ToC source.
- **Mapping.** Every section (or group of sections that map identically) was matched against INDEX.md,
  FAQ.md and a keyword grep of all `kb/` pages; where the grep was ambiguous the page section was
  opened. Titles only are listed (facts); no ToC text is reproduced beyond section names.
- **Status definitions.**
  - **covered** — a KB page has a section, derivation or worked example at roughly the depth of the
    source section (for a graduate text: the key result is derived or verified, not just stated).
  - **shallow** — the topic is present but only as a statement / one paragraph / a citation; the note
    says what is missing (derivation depth, worked example, advanced form, design procedure).
  - **missing** — nothing usable in the KB.
  - **n/a** — not relevant to the reader's goals (history, multimedia, company-specific standards
    lists, superconductors …); excluded from percentages.
- **n** = number of source sections the row stands for; percentages are weighted by n.
- **Planned** = INDEX/taxonomy already has an unwritten page that would close the row.

## 1. Summary

**28 sources mapped**: 19 textbooks (most at section level; Lee, Cripps, Richards, Proakis, ARRL Handbook/Antenna Book,
Hayward and Skolnik only at chapter level) and 9 course/curriculum groups (MIT 6.013, 6.776, LL radar; Stanford
EE359/EE252/EE133; Berkeley EE142/242A; Georgia Tech ECE6360/6361; Caltech EE153; TU Delft/ETH; MOOCs/vendors).
**1 725 in-scope source sections/lectures** (200 more marked n/a).

**Overall (weighted by sections): 69 % covered · 21 % shallow · 10 % missing.**
Textbooks 68/21/11; courses 79/15/6; unweighted mean over sources 73/19/8.

Per source (n = in-scope sections; percentages exclude n/a):

| # | Source | n (in scope) | covered | shallow | missing | n/a |
|---|---|---|---|---|---|---|
| 3.1 | Pozar, *Microwave Engineering* | 100 | 77 % | 14 % | 9 % | 0 |
| 3.2 | Balanis, *Antenna Theory: Analysis and Design* | 146 | 67 % | 22 % | 11 % | 3 |
| 3.3 | Razavi, *RF Microelectronics* | 201 | 68 % | 21 % | 11 % | 18 |
| 3.4 | Lee, *The Design of CMOS Radio-Frequency Integrated Circuits* | 18 | 72 % | 28 % | 0 % | 2 |
| 3.5 | Ott, *Electromagnetic Compatibility Engineering* | 172 | 54 % | 28 % | 18 % | 1 |
| 3.6 | Hong, *Microstrip Filters for RF/Microwave Applications* | 65 | 51 % | 22 % | 28 % | 7 |
| 3.7 | Mailloux, *Phased Array Antenna Handbook* | 143 | 52 % | 29 % | 18 % | 0 |
| 3.8 | Kaplan & Hegarty, *Understanding GPS/GNSS* | 66 | 44 % | 35 % | 21 % | 25 |
| 3.9 | Cripps, *RF Power Amplifiers for Wireless Communications* | 14 | 57 % | 43 % | 0 % | 0 |
| 3.10 | Richards, *Fundamentals of Radar Signal Processing* | 9 | 78 % | 22 % | 0 % | 0 |
| 3.11 | Proakis & Salehi, *Digital Communications* | 16 | 69 % | 31 % | 0 % | 0 |
| 3.12 | Rappaport, *Wireless Communications: Principles and Practice* | 67 | 76 % | 9 % | 15 % | 51 |
| 3.13 | Bogatin, *Signal and Power Integrity — Simplified* | 221 | 77 % | 23 % | 0 % | 0 |
| 3.14 | Lyons, *Understanding Digital Signal Processing* | 136 | 82 % | 6 % | 12 % | 24 |
| 3.15 | Horowitz & Hill, *The Art of Electronics* | 102 | 82 % | 16 % | 2 % | 50 |
| 3.16 | *The ARRL Handbook for Radio Communications* | 29 | 76 % | 21 % | 3 % | 4 |
| 3.17 | *The ARRL Antenna Book for Radio Communications* | 26 | 58 % | 38 % | 4 % | 1 |
| 3.18 | Hayward, Campbell & Larkin, *Experimental Methods in RF Design* | 11 | 91 % | 9 % | 0 % | 1 |
| 3.19 | Skolnik, *Introduction to Radar Systems* | 11 | 82 % | 9 % | 9 % | 0 |
| 3.20 | MIT 6.013 *Electromagnetics and Applications* | 38 | 97 % | 3 % | 0 % | 11 |
| 3.21 | MIT 6.776 *High Speed Communication Circuits* | 26 | 62 % | 38 % | 0 % | 0 |
| 3.22 | MIT Lincoln Laboratory *Introduction to Radar Systems* | 11 | 82 % | 9 % | 9 % | 0 |
| 3.23 | Stanford EE359, EE252, EE133 | 31 | 55 % | 32 % | 13 % | 1 |
| 3.24 | Berkeley EE142 / EE242A *Integrated Circuits for Communications* | 7 | 86 % | 14 % | 0 % | 1 |
| 3.25 | Georgia Tech ECE 6360 *Microwave Design* | 17 | 94 % | 6 % | 0 % | 0 |
| 3.26 | Caltech EE 153 *Microwave Circuits and Antennas* | 14 | 100 % | 0 % | 0 % | 0 |
| 3.27 | TU Delft (EE4620, EE4675, ET4169/4175, EE4565) + ETH | 14 | 50 % | 14 % | 36 % | 0 |
| 3.28 | MOOCs and vendor curricula | 14 | 100 % | 0 % | 0 % | 0 |
| | **Textbooks (3.1–3.19)** | 1553 | 68 % | 21 % | 11 % | 187 |
| | **Courses/MOOCs (3.20–3.28)** | 172 | 79 % | 15 % | 6 % | 13 |
| | **All sources** | 1725 | 69 % | 21 % | 10 % | 200 |

**How to read the numbers.**
- Coverage is high wherever an undergraduate/first-graduate course goes (Pozar, MIT 6.013, Caltech EE153,
  GaTech 6360, Lyons, AoE analog chapters: 77–100 %). It falls in the specialist graduate texts: **Kaplan GNSS
  (44 % covered; 21-gnss is only 3/8 written), Mailloux (52 %), Hong (51 %), Ott (54 %)**, and in the
  research-flavoured TU Delft courses (50 %).
- Chapter-level sources (Lee, Cripps, Richards, Proakis) cannot show "missing" (a whole chapter is rarely absent),
  so their gaps appear as "shallow"; read those rows' notes.
- Domains 13 (EMC/layout), 20 (projects) and 21 (GNSS) were landing during the check; rows were re-checked on
  2026-10-02 (KB at 229 pages). Ott rose from 27 % to 54 % covered after five domain-13 pages landed.
- The commonest pattern is not absence but **"stated, not derived"**: the KB names an advanced method in one
  paragraph with a citation (ISF phase noise, Woodward–Lawson, Schelkunoff synthesis, Volterra/AM-PM, Stein limit,
  Bayliss, Green's functions) — fine for an engineer, insufficient for a graduate student.

## 2. Ranked top-50 missing / shallow topics

Score = number of independent sources that expect the topic (S) × relevance to radios / radars / LoRa / phased
arrays / antennas / analog (R: 3 high, 2 medium, 1 low). "New" = no page planned; otherwise the target is an
existing page (extend) or a planned slug.

| # | Topic | S | R | Sources (table §) | Target | What is needed |
|---|---|---|---|---|---|---|
| 1 | **Radar tracking & parameter estimation** — monopulse Σ/Δ angle error, sequential lobing/conical scan, angle/range/Doppler CRLB, α-β and Kalman trackers, track-while-scan, gating | 4 | 3 | Skolnik 4, Richards 7, MIT LL L9, Mailloux 1.1.6 | NEW 11/tracking-radar-monopulse-and-track-filters | derive monopulse slope & σ_θ; α-β/Kalman tracker with a rocket-tracking worked example; script |
| 2 | **State estimation & Kalman filtering** (linear/extended KF, process noise, innovations) as a maths foundation | 4 | 3 | Kaplan 11.1–11.2 & 13.1–13.3, Richards 7, Skolnik 4, MIT LL L9 | NEW 00/estimation-and-kalman-filtering (+ section in 21 for GNSS/IMU) | L1 intuition → L2 scalar KF → L3 EKF; GNSS/baro/IMU fusion example for the flight computer |
| 3 | **Multiple & random access, duplexing** — ALOHA/slotted ALOHA throughput, CSMA, TDMA/FDMA, TDD/FDD, half-duplex trade-offs | 4 | 3 | Rappaport 9.1–9.6, Proakis 16, Razavi 3.6, EE359 L19 | NEW 10/multiple-access-aloha-duplexing | S = G e^(−2G) derivation; many-LoRa-node and multi-team launch-day collision budget |
| 4 | **Array pattern synthesis, worked** — Schelkunoff null placement, Fourier & Woodward–Lawson shaped beams, Bayliss, Elliott, numerical/convex synthesis, thinned & circular-Taylor arrays | 2 | 3 | Balanis 7.2–7.9, Mailloux 2.4, 3.1–3.3 (≈20 sections) | NEW 12/array-pattern-synthesis | each method with a script and a sector/cosec² example; thinning statistics |
| 5 | **Wideband antenna elements** — biconical, bow-tie, discone, Vivaldi/antipodal, spirals & frequency-independence, tightly-coupled/connected arrays | 3 | 2.5 | Balanis 9.2–9.4, 9.7, 11.1–11.3; Mailloux 5.3.6, 5.4.x; TU Delft EE4620 | NEW 08/wideband-antennas-discone-vivaldi-spiral | design equations, NEC/openEMS models; discone for scanner/ground station |
| 6 | **AGC loop design** (analog log-domain and digital), detectors, gain stepping | 3 | 2.5 | Razavi 5.4, 13.2.3; ARRL HB 12; Lyons 13.30 | extend 07/dynamic-range-sfdr-blocking or NEW 06/agc-loops | loop dynamics (attack/decay, stability), LoRa/SDR AGC behaviour |
| 7 | **Pulse-Doppler processing** — fast/slow-time data cube, PRF regimes (low/medium/high), range–Doppler map, MTD, PRF ambiguity resolution | 2 | 3 | Richards 3, 5; Skolnik 3 | extend 11/clutter-and-mti or NEW 11/pulse-doppler-processing | data-matrix walkthrough (also the FMCW mental model); CRT ambiguity resolution example |
| 8 | **Conformal / cylindrical arrays & phase-mode theory** | 2 | 3 | Mailloux 4.1–4.4, Balanis 6.12 | NEW 12/conformal-and-circular-arrays | wrap-around arrays on a body tube; UCA phase modes; roll-invariant patterns |
| 9 | **Ground-station antenna types** — corner reflector, collinear, turnstile/eggbeater, stacking & phasing harnesses | 2 | 3 | Balanis 15.3, Antenna Book V2-4, V3-3, V3-4 | extend 08/yagi-uda… or NEW 08/ground-station-antenna-types | stacking distance & harness design; omni CP options for tracking |
| 10 | **Resonator coupling & cavity perturbation** — coupling coefficient g (under/critical/over), external Q, gap/aperture coupling; perturbation for εr/tanδ measurement | 2 | 3 | Pozar 6.6–6.7; MIT 6.013 L14, L16 | extend 01/resonance-and-q; NEW 17/material-permittivity-measurement | derive g from S11; split-ring / cavity εr measurement of FR-4 with a NanoVNA |
| 11 | **Microstrip discontinuity models** — step, bend/mitre, T-junction, gap, via; when to EM-simulate | 2 | 3 | Pozar 4.6, Hong 4.3 | extend 03/planar-lines… or 04/pcb-parasitics… | closed-form models (Hammerstad, Kirschning) + openEMS check |
| 12 | **z-transform** (definition, ROC, poles/zeros, inverse, relation to Laplace) | 1+ | 3 | Lyons 6.3–6.5 (+ Proakis implicit; 00/_index lists as known gap) | NEW section/page 00/z-transform or 14/digital-filters L2 | bridge Laplace → z; bilinear mapping derived; ladder break (§4) |
| 13 | **GNSS remainder** — ECEF/ENU coordinates, Kepler orbits & ephemeris computation, UERE & DOP, RAIM, RTK/PPP, A-GNSS, Doppler velocity | 1 | 3 | Kaplan 2.2–2.3, 2.6, 3.8, 10–13 | planned 21/gnss-error-sources-dop, 21/rtk-ppp-and-corrections, 21/ttff-agps…, 21/gnss-timing-1pps (+ coordinates section) | five planned pages still unwritten |
| 14 | **Digital termination & crosstalk budgets** — series/parallel/AC termination, NEXT/FEXT, saturation length, guard traces | 3 | 2 | Bogatin 8.8–8.12, 10.x; AoE 12.9–12.10; ETH 227-0112 | extend 13/rf-layout-rules or 13/mixed-signal-layout | flight-computer SPI/clock routing numbers |
| 15 | **PA linearisation beyond DPD** — feed-forward, Cartesian feedback, envelope feedback, adaptive bias | 3 | 2 | Razavi 12.6, Cripps 14, MIT 6.776 L20 | extend 06/power-amplifiers | block diagrams + error budgets; when each beats DPD |
| 16 | **Fading-channel performance & capacity** — average BER in Rayleigh/Rician, outage & ergodic capacity, adaptive modulation | 3 | 2 | Proakis 13–14, EE359 L7–L13, Rappaport 6.12 | extend 10/ber-ebn0-and-shannon + 09/multipath-fading-doppler | closed forms (1/(4γ̄) etc.); LoRa SF adaptation as the reader's analogue |
| 17 | **MIMO communications** — STBC/Alamouti, spatial multiplexing, diversity–multiplexing trade-off, MIMO-OFDM | 3 | 2 | Proakis 15, EE359 L14–L17, Balanis 16.11 | NEW 10/mimo-and-space-time-coding | builds on the SVD capacity already in 00/matrices… |
| 18 | **Oscillator phase noise, LTV/ISF theory** (Γ_rms, flicker up-conversion, tail-current noise) | 3 | 2 | Razavi 8.7.4–8.7.5, Lee 18, MIT 6.776 L17 | extend 07/phase-noise-and-jitter L3 | derive ISF result; compare with Leeson on the 433 MHz VCO example |
| 19 | **Bandwidth extension & broadband amplifiers** — shunt/series peaking, distributed and balanced amplifiers | 3 | 2 | Pozar 12.4, Lee 9, MIT 6.776 L6–L9 | extend 05/amplifier-topologies | balanced amp with 90° hybrids (ties to 06/couplers) |
| 20 | **Radiometry & interferometry** — total-power/Dicke radiometer ΔT, beam efficiency, aperture synthesis/VLBI basics | 4 | 1.5 | Pozar 14.4, EE252, MIT 6.013 R24, Balanis 2.10 | NEW 08/radiometry-and-interferometry | also explains antenna-temperature measurements with an SDR |
| 21 | **Green's functions, equivalence & reciprocity** — free-space & dyadic Green's function derivation, F potential/magnetic currents, Love/Schelkunoff equivalence, Lorentz reciprocity | 4 | 1.5 | Balanis 3.2–3.5, 3.8, 12.2; Pozar 1.9; Mailloux 6.2; TU Delft EE4620 | NEW 02/green-functions-equivalence-reciprocity | the L3 foundation that horn/slot/aperture/MoM pages currently assume |
| 22 | **Periodic structures, EBG & artificial dielectrics** — Bloch impedance, k–β diagrams, slow-wave lines, AMC ground planes | 4 | 1.5 | Pozar 8.1, Balanis 4.7, Hong 10.2, TU Delft EE4620 | NEW 03/periodic-structures-ebg | low-profile antennas over AMC; periodic filters |
| 23 | **Volterra series, AM-PM and memory effects** | 2 | 2 | Razavi 2.2.6, 2.7–2.8; Cripps 9 | extend 07/nonlinearity… L3 | method of nonlinear currents; theory under the DPD memory polynomial |
| 24 | **"First radio" beginner builds** — crystal set/TRF, super-regenerative OOK receiver, simple FM transceiver | 3 | 2 | AoE 1.8, Razavi 4.4, Stanford EE133 | NEW 20/first-radio-builds | the missing Level-0 rung (§4) |
| 25 | **RF prototyping & construction** — Manhattan, dead-bug, copper-clad, enclosures | 2 | 2.5 | ARRL HB 23, Hayward 1–5 | NEW 17/rf-prototyping-construction | |
| 26 | **Practical Doherty, continuous modes (class J), load-pull practice** | 2 | 2 | Cripps 4, 8, 10, 12; Razavi 12.9 | extend 06/power-amplifiers | offset lines, peaking-device sizing; DIY tuner load-pull |
| 27 | **Advanced filter synthesis** — coupling matrix from polynomials (Cameron), extracted-pole, canonical, linear-phase, multiband (433+915) | 2 | 2 | Hong 7.6, 9.4–9.8; Pozar 8.1–8.2 | extend 06/rf-filters… L3 | dual-band 433/915 example |
| 28 | **Crystal ladder IF filters & crystal parameter measurement** | 2 | 2 | ARRL HB 10, Hayward 2–5 | extend 04/crystals-and-resonators | Cohn/min-loss ladder with measured motional parameters |
| 29 | **FFT internals & practical DSP tricks** — radix-2 butterflies, overlap-add/save, sliding DFT, zoom FFT, sub-bin peak interpolation | 1 | 2.5 | Lyons 4.3–4.6, 13.x | extend 14/fft-spectral-analysis-windows | sub-bin interpolation matters for FMCW range and tone estimation |
| 30 | **PLL dynamics** — lock time, Gardner sampled-loop limit, two-point modulation, offset PLLs, fractional spurs from CP non-linearity | 1 | 2.5 | Razavi 9.3.4–9.3.5, 10.3–10.5, 11.2.5 | extend 06/vco-and-pll-synthesizers | FMCW chirp linearity & FSK modulation via PLL |
| 31 | **Satellite communications** — pass geometry, Doppler correction, link budget to LEO/CubeSat | 2 | 2 | ARRL HB S1, Antenna Book V3-3 | NEW 09/satellite-links-doppler-tracking | reuse rocket Doppler maths |
| 32 | **Waveguide theory gaps** — circular guide & cavity, parallel-plate modes, transverse resonance, modal V/I, probe/loop/aperture (Bethe) excitation | 2 | 1.5 | Pozar 3.2, 3.4, 3.9, 4.1, 4.7–4.8, 6.4 | extend 02/waveguides-and-cavity-resonators | cantenna/horn feed design at 2.4/5.8/10 GHz |
| 33 | **Surface & leaky waves on grounded slabs** (dispersion, cut-off vs h/λ, leaky-wave antennas) | 2 | 1.5 | Pozar 3.6, TU Delft EE4620 | extend 03/planar-lines… or 08/patch-antennas | |
| 34 | **Printed series-fed patch arrays** (comb-line, 24/60/77 GHz radar boards) | 2 | 2 | Mailloux 5.8.2, Balanis 14.8 | extend 08/patch-antennas or 12/diy-phased-array-projects | |
| 35 | **Practical direction-finding for recovery** — Yagi null-seeking, pseudo-Doppler, Watson–Watt/Adcock | 1 | 3 | Antenna Book V3-8 | extend 12/adaptive-beamforming-doa or NEW 08/direction-finding-for-recovery | |
| 36 | **Microwave tubes & pulse modulators** (magnetron, klystron, TWT) | 3 | 1 | Pozar 11.5, Skolnik 10, MIT LL L10 | NEW section 11/diy-radar-hardware | surplus-magnetron safety & behaviour |
| 37 | **HF wire & travelling-wave antennas** (long-wire, V, rhombic, Beverage, traps, fan, OCF, quad) | 3 | 1 | Balanis 10.2, Antenna Book V2-1–V2-5, ARRL HB 21 | planned 08/wire-antennas-hf-random-wire-fan-dipole | |
| 38 | **Comparators, Schmitt triggers, output stages, current mirrors, timers** | 1 | 2 | AoE 2.4, 7.2, 12.3 | NEW 05/comparators-output-stages | |
| 39 | **Voltage references & bias references** (bandgap, PTAT, constant-gm) | 2 | 1.5 | AoE 9.10, Lee 10 | extend 05/power-supplies… | ADC reference selection |
| 40 | **Mixer LPTV analysis** — conversion matrices, passive-mixer noise folding, cyclostationary noise | 2 | 1.5 | Razavi 2.1.2, 6.2, 6.3.2; Lee 18 | extend 06/mixers L3 | |
| 41 | **PCB/on-chip spiral inductors** (modified Wheeler, current-sheet formulas, Q) | 2 | 1.5 | Razavi 7.2, Lee 4 | extend 04/inductors-at-rf | printed inductors for compact matching |
| 42 | **EMC regulation & transients for avionics** — MIL-STD-461/DO-160, EFT/surge, contact protection/snubbers for pyro & servo loads | 1 | 2.5 | Ott 1.4–1.11, 7, 14 | extend 13/emc-emi-fundamentals | |
| 43 | **Coded modulation & iterative decoding** — TCM, BICM, BCJR, belief propagation | 3 | 1 | Proakis 8, Rappaport 7.17, Balanis 16.11 | extend 10/channel-coding-fec | |
| 44 | **Cable shielding & ground loops** — transfer impedance, pigtails, shield termination, CM chokes on cables | 1 | 2 | Ott 2.6–2.17, 3.2–3.6 | extend 13/emc-emi-fundamentals | |
| 45 | **Quadrature/coupled oscillators, cap-bank VCOs, injection-locking theory (Adler)** | 1 | 2 | Razavi 8.6, 8.11 | extend 05/oscillators | basis for injection-locked phased arrays |
| 46 | **Information theory basics & signal-space geometry** — entropy, mutual information, source coding, Gram–Schmidt, biorthogonal/simplex | 2 | 1.5 | Proakis 2–3, 6; EE359 L7 | extend 10/ber-ebn0-and-shannon | |
| 47 | **Antenna tuners** (L/T/π ATU topologies, losses) | 1 | 1.5 | ARRL HB 20 (+ D1 Stack Exchange gap) | extend 08/antenna-matching-and-baluns | |
| 48 | **Repeater duplexers & cavity notch filters** | 1 | 2 | ARRL HB 18 | extend 06/rf-filters… | ground station beside a cell/pager site |
| 49 | **Co-channel interference & frequency reuse (C/I)** | 2 | 1 | Rappaport 3, Razavi 3.5 | extend 10/multiple-access… (#3) | |
| 50 | **Analog phasing (SSB) networks & product detectors** | 2 | 1.5 | Hayward 9, ARRL HB 11–12 | extend 14/iq-complex-baseband | RC polyphase / allpass pairs |

## 3. Per-source mapping tables

### 3.1 Pozar, *Microwave Engineering*, 4th ed. (Wiley 2012)
ToC source: Wiley product page 9781118213636, "Table of Contents" field (raw HTML, fetched 2026-09-29).
Page abbreviations: `02/…` = `kb/02-electromagnetics/…` etc.

| § | Section | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1.1 | Introduction to microwave engineering | 00/math-roadmap-for-rf, 19/spectrum-allocation-ism-bands | covered | 1 | |
| 1.2–1.6 | Maxwell; fields in media & BCs; wave eq.; general plane waves; energy & power | 02/maxwells-equations, 02/boundary-conditions…, 02/wave-equation…, 02/poynting… | covered | 5 | |
| 1.7–1.8 | Reflection at an interface; oblique incidence | 02/boundary-conditions-reflection-refraction | covered | 2 | Fresnel, Snell, multilayer TMM |
| 1.9 | Useful theorems (reciprocity, image theory) | 02/maxwells-equations, 08/antenna-fundamentals | shallow | 1 | Lorentz reciprocity & reaction stated, not derived; no uniqueness-theorem argument |
| 2.1–2.2 | Lumped model; field analysis of lines | 03/telegrapher-equations…, 02/inductance-capacitance-from-fields | covered | 2 | |
| 2.3–2.6 | Terminated line; Smith chart; λ/4 transformer; generator & load mismatch | 03/input-impedance-stubs…, 03/smith-chart, 03/reflections…, 03/signal-flow-graphs-mason | covered | 4 | |
| 2.7 | Lossy lines (perturbation method, Wheeler incremental-inductance rule) | 03/telegrapher…, 02/skin-effect… | covered | 1 | Wheeler rule only mentioned once |
| 2.8 | Transients on lines | 03/time-domain-reflectometry | covered | 1 | no bounce (lattice) diagram for mismatched source *and* load |
| 3.1 | General TEM/TE/TM solutions | 02/waveguides-and-cavity-resonators | covered | 1 | |
| 3.2 | Parallel-plate waveguide | 02/waveguides…, 02/inductance-capacitance… | shallow | 1 | formulas only; no TM/TE mode derivation |
| 3.3 | Rectangular waveguide | 02/waveguides… | covered | 1 | |
| 3.4 | Circular waveguide | 02/waveguides…, 08/horn-reflector… | shallow | 1 | Bessel-root cut-offs mentioned; no TE11/TM01 derivation or attenuation |
| 3.5 | Coaxial line (incl. higher-order modes) | 03/coax-and-cables, 18/connectors-and-cables-parts | covered | 1 | |
| 3.6 | Surface waves on a grounded dielectric sheet | 08/patch-antennas, 12/planar-arrays… | shallow | 1 | named as a loss/scan-blindness mechanism; no TM0/TE1 dispersion relation or cut-off vs h/λ |
| 3.7–3.8 | Stripline; microstrip | 03/planar-lines-microstrip-stripline-cpwg | covered | 2 | |
| 3.9 | Transverse-resonance technique | — | missing | 1 | one passing mention |
| 3.10–3.11 | Wave velocities & dispersion; summary | 02/waveguides…, 03/planar-lines… | covered | 2 | |
| 4.1 | Equivalent voltages/currents for waveguide modes; Z properties | — | missing | 1 | modal V/I and even/odd Z(ω) properties absent |
| 4.2–4.5 | Z/Y matrices; S-matrix (power waves, generalised S); ABCD; signal-flow graphs | 01/two-port-networks…, 03/s-parameters, 03/signal-flow-graphs-mason | covered | 4 | |
| 4.6 | Discontinuities & modal analysis | 03/input-impedance-stubs… (open-end Δℓ), 04/pcb-parasitics… | shallow | 1 | open-end only; no microstrip step/bend/T-junction models, no mode matching |
| 4.7–4.8 | Waveguide excitation by currents; aperture coupling (Bethe) | — | missing | 2 | probe/loop feed theory and small-aperture polarisability absent |
| 5.1–5.4 | L-networks; single-stub; double-stub; λ/4 | 03/impedance-matching…, 03/input-impedance-stubs… | covered | 4 | double-stub: 3 mentions, no forbidden-region design example |
| 5.5–5.8 | Small reflections; binomial & Chebyshev multisection; tapers (Klopfenstein) | 03/impedance-matching… | covered | 4 | Chebyshev multisection only briefly |
| 5.9 | Bode–Fano | 03/broadband-matching-bode-fano | covered | 1 | |
| 6.1–6.2 | Series/parallel resonators; line resonators | 01/resonance-and-q, 03/input-impedance-stubs… | covered | 2 | |
| 6.3 | Rectangular cavity | 02/waveguides-and-cavity-resonators | covered | 1 | |
| 6.4 | Circular cavity | — | missing | 1 | no TE011/TM010 |
| 6.5 | Dielectric resonators | 06/rf-filters…, 18/filter-parts… | shallow | 1 | named; no mode/Q estimate |
| 6.6 | Excitation of resonators (coupling coefficient; gap- & aperture-coupled) | 01/resonance-and-q, 06/rf-filters… | shallow | 1 | loaded/external Q present; under/critical/over-coupling (coupling coefficient g) absent |
| 6.7 | Cavity perturbation | — | missing | 1 | also the standard εr/tanδ measurement method |
| 7.1–7.3 | Divider/coupler properties; T-junction; Wilkinson | 06/couplers-dividers-combiners | covered | 3 | |
| 7.4 | Waveguide directional couplers (Bethe-hole, multihole) | 06/couplers… | shallow | 1 | |
| 7.5–7.8 | Quadrature hybrid; coupled-line couplers; Lange; 180° hybrid | 06/couplers… | covered | 4 | |
| 7.9 | Other couplers (Moreno, Schwinger, Riblet, reflectometer) | 06/couplers…, 06/detectors… | shallow | 1 | reflectometer yes; others no |
| 8.1 | Periodic structures (Bloch impedance, k–β diagram) | — | missing | 1 | Floquet appears only for arrays |
| 8.2 | Image-parameter filters | 06/rf-filters… | shallow | 1 | one mention |
| 8.3–8.5 | Insertion-loss method; transformations; implementation (Richards, Kuroda, inverters) | 01/passive-filter-design-prototypes, 06/rf-filters… | covered | 3 | |
| 8.6–8.8 | Stepped-impedance LPF; coupled-line BPF; coupled-resonator BPF | 06/rf-filters… | covered | 3 | worked 2.45 GHz examples |
| 9.1–9.2 | Ferrite properties (Polder tensor); plane waves in ferrite (Faraday rotation) | 02/magnetic-materials-permeability, 06/circulators-isolators | covered | 2 | |
| 9.3 | Ferrite-loaded rectangular guide | 06/circulators… | shallow | 1 | |
| 9.4, 9.6 | Isolators; circulators | 06/circulators-isolators | covered | 2 | |
| 9.5 | Ferrite phase shifters | 12/phase-shifters-ttd-components | shallow | 1 | latching/Reggia-Spencer only named |
| 10.1–10.4 | Noise; noise figure; nonlinear distortion; dynamic range | 07/* | covered | 4 | |
| 11.1–11.3 | Diodes & diode circuits; BJTs; FETs | 05/diodes…, 05/bjt…, 05/fets…, 06/detectors… | covered | 3 | |
| 11.4 | Microwave integrated circuits (hybrid MIC, MMIC processes) | 05/amplifier-topologies, 18/lna-pa… | shallow | 1 | no process/technology overview |
| 11.5 | Microwave tubes | — | missing | 1 | klystron/TWT/magnetron only in passing (relevant to magnetron-based DIY radar) |
| 12.1–12.3 | Two-port power gains; stability; single-stage design (gain & noise circles) | 06/lna-design, 06/amplifier-stability-and-biasing | covered | 3 | |
| 12.4 | Broadband amplifiers (balanced, distributed, feedback) | 05/amplifier-topologies, 06/couplers… | shallow | 1 | feedback amp covered; balanced amp one line; distributed amp one line |
| 12.5 | Power amplifiers | 06/power-amplifiers | covered | 1 | |
| 13.1–13.2 | RF oscillators; microwave (negative-resistance, DRO) oscillators | 05/oscillators, 11/cw-and-doppler-radar | covered | 2 | DRO design not worked |
| 13.3–13.5 | Phase noise; multipliers; mixers | 07/phase-noise-and-jitter, 06/frequency-multipliers-dividers, 06/mixers | covered | 3 | |
| 14.1–14.3 | System aspects of antennas; wireless systems; radar systems | 08/antenna-fundamentals, 09/link-budget…, 11/radar-range-equation | covered | 3 | |
| 14.4 | Radiometer systems | — | missing | 1 | total-power/Dicke radiometer, ΔT = T_sys/√(Bτ) absent |
| 14.5 | Microwave propagation | 09/* | covered | 1 | |
| 14.6 | Other applications (RFID, WPT, EMC, radiation hazards) | 08/inductive-coupling-rfid-nfc-wpt, 13/emc-emi-fundamentals, 19/rf-exposure-safety | covered | 1 | landed 2026-10 |

### 3.2 Balanis, *Antenna Theory: Analysis and Design*, 4th ed. (Wiley 2016)
ToC source: Wiley product page 9781118642061 (raw HTML ToC field). Multimedia/reference sections are n/a.

| § | Section | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1.1–1.4 | Types; radiation mechanism; current on a thin wire | 08/antenna-fundamentals, 02/radiation-from-currents-hertzian-dipole | covered | 4 | |
| 1.5 | Historical advancement | — | n/a | 1 | |
| 2.1–2.6 | Pattern; power density; intensity; beamwidth; directivity | 08/antenna-fundamentals | covered | 6 | |
| 2.7 | Numerical techniques (directivity by numerical integration) | 08/antenna-fundamentals, 16/nec-antenna-modelling | covered | 1 | |
| 2.8–2.9, 2.11–2.14 | Efficiency; gain & realised gain; bandwidth; polarisation; input impedance; radiation efficiency | 08/antenna-fundamentals, 08/antenna-polarization… | covered | 6 | |
| 2.10 | Beam efficiency | — | missing | 1 | minor (radiometry/remote sensing metric) |
| 2.15 | Vector effective length & equivalent areas | 08/loop-antennas, 08/dipoles…, 09/friis… | shallow | 1 | effective height used; vector effective length / polarisation-matched open-circuit voltage not formalised |
| 2.16–2.18 | Max directivity & effective area; Friis & radar eq.; antenna temperature | 09/friis…, 11/radar-range-equation, 07/thermal-noise… | covered | 3 | |
| 3.2–3.4 | Vector potentials A (electric) and F (magnetic current) | 02/radiation-from-currents…, 02/maxwells-equations | shallow | 3 | A covered; F / magnetic-current sources and their use for slots/apertures only named |
| 3.5 | Solution of inhomogeneous wave eq. (Green's function) | 00/vector-calculus-for-em, 00/numerical-methods-overview | shallow | 1 | free-space Green's function stated, not derived; no dyadic form |
| 3.6–3.7 | Far-field approximation; duality | 02/radiation-from-currents…, 02/near-field-far-field | covered | 2 | |
| 3.8 | Reciprocity & reaction theorems | 08/antenna-fundamentals | shallow | 1 | TX/RX pattern equality stated; no Lorentz/reaction derivation |
| 4.1–4.6 | Infinitesimal, small, finite and half-wave dipoles; region separation | 08/dipoles-and-monopoles, 02/near-field-far-field | covered | 6 | |
| 4.7 | Elements near PEC, PMC and EBG surfaces | 08/dipoles-and-monopoles (images) | shallow | 1 | PEC images yes; PMC/AMC/EBG ground planes (low-profile antennas) absent |
| 4.8–4.9 | Ground effects; computer codes | 16/nec-antenna-modelling, 09/two-ray-ground-reflection | covered | 2 | |
| 5.1–5.3, 5.7 | Small loop; constant-current loop; ferrite loop | 08/loop-antennas | covered | 4 | |
| 5.4–5.6 | Non-uniform-current loop; ground effects; polygonal loops | 08/loop-antennas | shallow | 3 | Fourier-series current on large loops not treated |
| 5.8 | Mobile-communication applications | — | n/a | 1 | |
| 6.1–6.6 | Two-element, N-element uniform arrays; directivity; design; 3-D characteristics | 12/array-factor-linear-arrays, 12/beam-steering-grating-lobes | covered | 6 | |
| 6.7 | Rectangular-to-polar graphical solution | 12/beam-steering… (visible region) | shallow | 1 | |
| 6.8 | Non-uniform amplitude (binomial, Dolph–Chebyshev) | 12/tapering-sidelobe-control | covered | 1 | |
| 6.9 | Superdirectivity | 08/small-antenna-limits, 12/array-factor… | shallow | 1 | named; no tolerance-sensitivity analysis |
| 6.10–6.11 | Planar arrays; design considerations | 12/planar-arrays-element-pattern-coupling | covered | 2 | |
| 6.12 | Circular arrays | 12/adaptive-beamforming-doa (UCA for DoA) | shallow | 1 | UCA array factor / phase-mode theory absent |
| 7.2 | Continuous (line) sources | 12/tapering-sidelobe-control, 00/fourier-series-and-transform | shallow | 1 | |
| 7.3 | Schelkunoff polynomial method | 12/array-factor-linear-arrays, 12/tapering-sidelobe-control | shallow | 1 | one paragraph each; no worked null-placement example |
| 7.4 | Fourier-transform synthesis | 12/tapering-sidelobe-control | shallow | 1 | |
| 7.5 | Woodward–Lawson | 12/tapering-sidelobe-control | shallow | 1 | one bullet; no shaped-beam (sector / cosec²) example |
| 7.6 | Taylor line source (n̄) | 12/tapering-sidelobe-control | covered | 1 | |
| 7.7–7.9 | Taylor one-parameter; triangular/cosine tapers; line-source phase distributions | 12/tapering-sidelobe-control | shallow | 3 | tapers yes; one-parameter & quadratic-phase (defocus) not treated |
| 7.10 | Continuous aperture sources | 08/horn-reflector-aperture-antennas | covered | 1 | |
| 8.1–8.4 | Integral equations (Pocklington, Hallén); finite-diameter wires; MoM solution | 08/antenna-simulation-nec-openems, 16/nec…, 16/em-solvers… | covered | 4 | own thin-wire MoM script |
| 8.5–8.7 | Self-impedance; mutual impedance; mutual coupling in arrays | 08/dipoles…, 08/yagi-uda…, 12/planar-arrays… | covered | 3 | induced-EMF method |
| 9.1–9.2 | Biconical antenna | 08/dipoles-and-monopoles | shallow | 2 | one mention |
| 9.3–9.4 | Bow-tie; Vivaldi | — | missing | 2 | UWB/radar-relevant (Vivaldi arrays) |
| 9.5–9.6 | Cylindrical (thick) dipole; folded dipole | 08/dipoles-and-monopoles | covered | 2 | |
| 9.7 | Discone & conical-skirt monopole | — | missing | 1 | common wideband ground-station/scanner antenna |
| 9.8 | Matching techniques (stub, λ/4, T/gamma/omega match, baluns) | 08/antenna-matching-and-baluns, 06/baluns… | covered | 1 | gamma/T-match only briefly (no design equations) |
| 10.2 | Travelling-wave antennas (long-wire, V, rhombic, Beverage) | — | missing | 1 | planned `08/wire-antennas-hf-random-wire-fan-dipole` unwritten |
| 10.3 | Broadband antennas (helix, Yagi–Uda …) | 08/helical-antennas, 08/yagi-uda-and-log-periodic | covered | 1 | |
| 11.1–11.3 | Frequency-independence theory; equiangular spiral | — | missing | 3 | spirals are the standard wideband CP element (DF, ESM) |
| 11.4–11.6 | Log-periodic; small-antenna limits; miniaturisation | 08/yagi-uda-and-log-periodic, 08/small-antenna-limits, 08/pcb-and-chip-antennas | covered | 3 | |
| 11.7 | Fractal antennas | 08/small-antenna-limits | covered | 1 | treated critically vs Chu bound |
| 12.1–12.2 | Field-equivalence (Huygens) principle | 08/horn-reflector…, 09/diffraction-knife-edge | shallow | 2 | used, not derived (Love/Schelkunoff equivalents) |
| 12.3–12.7 | Radiation equations; directivity; rectangular & circular apertures; design | 08/horn-reflector-aperture-antennas, 00/special-functions… | covered | 5 | |
| 12.8 | Babinet's principle | 08/slot-antennas | covered | 1 | landed 2026-10 (Babinet, slot impedance η²/4Z) |
| 12.9 | Fourier transforms in aperture theory | 00/fourier-series-and-transform | covered | 1 | |
| 12.10 | Ground-plane edge effects: GTD | 11/radar-cross-section | shallow | 1 | GTD/PO named for RCS; no edge-diffraction coefficient, no finite-ground-plane pattern ripple (relevant to GNSS patches) |
| 13.1–13.4 | E-/H-plane sectoral and pyramidal horns | 08/horn-reflector-aperture-antennas | covered | 4 | |
| 13.5–13.6 | Conical; corrugated horns | 08/horn-reflector… | shallow | 2 | |
| 13.7–13.9 | Aperture-matched; multimode; dielectric-loaded horns | — | missing | 3 | niche |
| 13.10 | Phase centre | 08/gnss-antennas, 08/horn-reflector… | covered | 1 | |
| 14.1–14.2, 14.4–14.5 | Rectangular patch (TL & cavity models); Q/BW/efficiency; input impedance | 08/patch-antennas | covered | 4 | |
| 14.3 | Circular patch | 00/special-functions… | shallow | 1 | Bessel root named only |
| 14.6 | Coupling between patches | 12/planar-arrays… | shallow | 1 | |
| 14.7–14.9 | CP patches; arrays & feed networks; mobile antennas (PIFA, IFA) | 08/antenna-polarization…, 08/pcb-and-chip-antennas, 13/stackups-and-materials | covered | 3 | |
| 14.10 | Dielectric-resonator antennas | — | missing | 1 | |
| 15.1–15.2 | Plane reflector | 08/dipoles… (images) | covered | 2 | |
| 15.3 | Corner reflector | — | missing | 1 | the radar trihedral is covered; the corner-reflector *antenna* (cheap 8–12 dBi ground-station antenna) is not |
| 15.4 | Parabolic reflector | 08/horn-reflector-aperture-antennas | covered | 1 | |
| 15.5 | Spherical reflector | — | missing | 1 | niche |
| 16.1–16.7 | Smart-antenna background, propagation, benefits | 12/adaptive-beamforming-doa, 09/multipath-fading-doppler | covered | 7 | |
| 16.8 | Beamforming (switched, adaptive, DoA) | 12/adaptive-beamforming-doa, 12/beamforming-architectures | covered | 1 | |
| 16.9 | MANETs | — | n/a | 1 | |
| 16.10–16.12 | System design; diversity combining, Rayleigh fading, TCM; other geometries | 09/multipath-fading-doppler, 10/channel-coding-fec | shallow | 3 | MRC/EGC/SC named; no combining-gain derivation; TCM absent |
| 17.1–17.7, 17.9 | Ranges; patterns; gain; directivity; efficiency; impedance; polarisation | 08/antenna-measurement, 17/antenna-range-ota-testing | covered | 8 | near-field scanning (planar/spherical NF→FF) only named |
| 17.8, 17.10 | Current measurements; scale models | — | missing | 2 | niche |

### 3.3 Razavi, *RF Microelectronics*, 2nd ed. (Prentice Hall 2011)
ToC source: Pearson/InformIT official sample-pages PDF (ptgmedia.pearsoncmg.com …/0137134738.pdf), read with
`pdftotext -layout`. Counted at sub-section level (x.y.z). IC-process-only items (on-chip MOS/MIM capacitors,
divider logic styles) are n/a for a PCB builder.

| § | Section | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1.1–1.2 | Wireless world; why RF design is hard | — | n/a | 2 | |
| 1.3 | The big picture (transceiver block diagram) | 06/receiver-architectures | covered | 1 | |
| 2.1.1, 2.1.3 | Units; nonlinearity | 00/decibels…, 07/nonlinearity… | covered | 2 | |
| 2.1.2 | Time variance (LPTV view of mixers/samplers) | 00/linear-systems-convolution | shallow | 1 | one mention; mixers never analysed as LPTV systems (conversion matrices) |
| 2.2.1–2.2.5 | Harmonics; compression; cross-modulation; IM; cascades | 07/nonlinearity-p1db-ip3-intermod | covered | 5 | |
| 2.2.6 | AM/PM conversion | 06/power-amplifiers | shallow | 1 | named for PAs; no derivation of AM-PM from nonlinear capacitance, no effect on EVM worked |
| 2.3.1–2.3.5 | Noise as random process; spectrum; filtering; device noise; circuit representation (vn/in) | 00/probability…, 07/thermal-noise…, 07/shot-and-flicker-noise, 05/low-noise-analog-design | covered | 5 | |
| 2.4.1–2.4.2 | Sensitivity; dynamic range | 07/sensitivity-and-mds, 07/dynamic-range-sfdr-blocking | covered | 2 | |
| 2.5.1–2.5.4 | Q; series↔parallel; matching networks; loss in matching networks | 01/resonance-and-q, 03/impedance-matching…, 01/energy-storage… | covered | 4 | |
| 2.6 | S-parameters | 03/s-parameters | covered | 1 | |
| 2.7.1, 2.8.1 | Nonlinear dynamic systems; Volterra series & method of nonlinear currents | — | missing | 2 | no Volterra kernels anywhere; needed for frequency-dependent IM3 (memory) and for DPD theory |
| 3.1–3.2.2 | General; AM; PM/FM | 10/analog-modulation-am-fm-pm-ssb | covered | 3 | |
| 3.3.1–3.3.6 | ISI; constellations; quadrature mod.; GMSK/GFSK; QAM; OFDM | 10/pulse-shaping-isi, 10/digital-modulation…, 10/ofdm | covered | 6 | |
| 3.4 | Spectral regrowth | 06/power-amplifiers, 10/digital-modulation… | covered | 1 | |
| 3.5 | Mobile RF communications (cellular concept) | — | shallow | 1 | frequency reuse / hand-off absent (see Rappaport) |
| 3.6.1–3.6.3 | TDD/FDD; FDMA; TDMA | 10/spread-spectrum…, 10/packet-framing-protocols | shallow | 3 | only in passing; no duplexer/half-duplex trade-off page |
| 3.6.4 | CDMA | 10/spread-spectrum-dsss-fhss-css | covered | 1 | |
| 3.7.1–3.7.3 | GSM; IS-95; WCDMA | — | n/a | 3 | legacy cellular |
| 3.7.4–3.7.5 | Bluetooth; 802.11a/b/g | 15/other-ism-radios-fsk-2g4, 10/ofdm | covered | 2 | |
| 3.8 | DPSK | 10/ber-ebn0-and-shannon | covered | 1 | |
| 4.1–4.2.5 | Heterodyne, modern heterodyne, direct-conversion, image-reject, low-IF receivers | 06/receiver-architectures, 06/mixers, 14/iq-complex-baseband | covered | 6 | |
| 4.3.1–4.3.5 | TX architectures | 06/transmitter-architectures | covered | 5 | |
| 4.4 | OOK transceivers (incl. super-regenerative) | 10/digital-modulation… | shallow | 1 | super-regenerative receivers (the classic cheap 433 MHz module) one mention |
| 5.1–5.2 | LNA general; input-matching problem | 06/lna-design | covered | 2 | |
| 5.3.1–5.3.2 | CS with inductive load; resistive-feedback | 05/amplifier-topologies, 06/lna-design | covered | 2 | |
| 5.3.3, 5.3.5 | Common-gate LNA; CG variants | 05/amplifier-topologies | shallow | 2 | CG input match 1/gm stated; no NF ≥ 1+γ/α derivation or gm-boosting |
| 5.3.4 | Cascode CS with inductive degeneration | 06/lna-design (Ex. 4) | covered | 1 | |
| 5.3.6–5.3.7 | Noise-cancelling; reactance-cancelling LNAs | 06/lna-design | shallow | 2 | named only; wideband noise-cancelling (Bruccoleri) not derived |
| 5.4–5.5 | Gain switching; band switching | 07/dynamic-range… (AGC) | shallow | 2 | AGC concept only; no LNA gain-step design |
| 5.6.1–5.6.2 | High-IP2 LNAs (differential etc.) | 06/receiver-architectures | shallow | 2 | IP2 as a system spec covered; circuit techniques absent |
| 5.7.1 | Nonlinearity of degenerated CS stage | 05/amplifier-topologies (Ex. 3) | covered | 1 | |
| 5.7.2–5.7.4 | Undegenerated CS; differential & degenerated pairs | 05/amplifier-topologies, 07/nonlinearity… | shallow | 3 | tanh diff-pair IIP3 not derived |
| 6.1.1, 6.1.3 | Mixer parameters; single/double-balanced | 06/mixers | covered | 2 | |
| 6.1.2 | Mixer noise figures (SSB/DSB) | 06/mixers, 07/noise-figure-and-friis | covered | 1 | |
| 6.2.1, 6.2.3–6.2.5 | Passive (switching) mixer gain, noise, input impedance, current-driven mixers | 06/mixers | shallow | 4 | commutating-mixer 2/π gain named; no noise folding / impedance-translation analysis |
| 6.2.2 | LO self-mixing | 06/receiver-architectures | covered | 1 | |
| 6.3.1, 6.3.3 | Active (Gilbert) mixer conversion gain; linearity | 06/mixers | covered | 2 | |
| 6.3.2 | Noise in active mixers | 06/mixers | shallow | 1 | cyclostationary noise / flicker transfer not analysed |
| 6.4.1–6.4.4 | Improved active mixers (current helpers, gm boost, high IP2, low flicker) | — | missing | 4 | IC-level; low priority |
| 6.5.1–6.5.2 | Up-conversion mixers | 06/transmitter-architectures | covered | 2 | |
| 7.1 | Passive devices: general | 04/* | covered | 1 | |
| 7.2.1–7.2.2 | Spiral inductor structure & geometries | — | missing | 2 | PCB/on-chip spiral inductors absent (inductors-at-rf covers chip & air coils) |
| 7.2.3–7.2.6 | Inductance equations; parasitic C; loss (skin, proximity, substrate); modelling | 04/inductors-at-rf, 02/skin-effect…, 04/component-models-s2p-spice | covered | 4 | spiral-specific formulas (modified Wheeler, current-sheet for spirals) absent |
| 7.2.7 | Alternative inductor structures | — | missing | 1 | |
| 7.3.1–7.3.3 | Transformer structures; coupling capacitance; modelling | 01/transformers-coupled-inductors, 06/baluns… | covered | 3 | |
| 7.4.1 | T-line structures | 03/planar-lines… | covered | 1 | |
| 7.5 | Varactors | 05/diodes-schottky-pin-varactor | covered | 1 | |
| 7.6.1–7.6.2 | MOS and metal-plate (MIM/MOM) capacitors | — | n/a | 2 | IC-process |
| 8.1–8.2.2 | Oscillator parameters; feedback & one-port views | 05/oscillators | covered | 3 | |
| 8.3 | Cross-coupled oscillator | 05/oscillators, 06/vco-and-pll… | shallow | 1 | named; no −2/gm analysis |
| 8.4 | Three-point (Colpitts) | 05/oscillators, 16/spice… (Ex. C) | covered | 1 | |
| 8.5.1 | VCO tuning-range limitations | 05/oscillators | shallow | 1 | |
| 8.5.2 | Effect of varactor Q | 05/diodes… (Ex. 3) | covered | 1 | |
| 8.6.1–8.6.3 | Wide-tuning VCOs: continuous; amplitude vs tuning; discrete (cap banks) | — | missing | 3 | |
| 8.7.1–8.7.3 | Phase-noise concepts; effects (reciprocal mixing); LTI (Leeson) analysis | 07/phase-noise-and-jitter, 06/receiver-architectures | covered | 3 | |
| 8.7.4 | Phase-noise analysis II (LTV / ISF) | 07/phase-noise-and-jitter | shallow | 1 | Hajimiri–Lee cited, not derived; no Γ_rms / Γ_dc flicker up-conversion |
| 8.7.5 | Noise of the bias (tail) current source | — | missing | 1 | |
| 8.7.6 | VCO figure of merit | 06/vco-and-pll…, 18/mixers-plls-vcos-parts | covered | 1 | |
| 8.8.1 | Low-noise VCO design procedure | 05/oscillators | shallow | 1 | |
| 8.9 | LO interface (buffers, LO pulling) | 06/transmitter-architectures | shallow | 1 | LO pulling named |
| 8.10 | Mathematical model of VCOs | 06/vco-and-pll-synthesizers | covered | 1 | |
| 8.11.1–8.12 | Quadrature & coupled oscillators | — | missing | 4 | also underpins injection-locked arrays |
| 9.1–9.2.6 | Phase detector; type-I PLL dynamics | 10/synchronization-carrier-timing, 06/vco-and-pll… | covered | 7 | |
| 9.3.1–9.3.3, 9.3.6–9.3.7 | PFD; charge pump; CPPLL; frequency-multiplying; higher-order loops | 06/vco-and-pll-synthesizers | covered | 5 | |
| 9.3.4 | CPPLL transient response / lock time | 06/vco-and-pll… | shallow | 1 | lock time only mentioned |
| 9.3.5 | Limits of the continuous-time approximation | — | missing | 1 | Gardner's sampled-loop stability limit (BW < f_PFD/10 rule) not derived |
| 9.4.1–9.4.2 | PFD/CP skew, width mismatch; compliance | 06/vco-and-pll… | shallow | 2 | reference spurs named |
| 9.4.3–9.4.6 | Charge injection; up/down mismatch; CLM; circuit fixes | — | n/a | 4 | IC-level |
| 9.5.1–9.8 | PLL phase noise (VCO, reference); loop bandwidth; design; phase margin | 06/vco-and-pll…, 07/phase-noise-and-jitter | covered | 5 | |
| 10.1–10.2 | Integer-N synthesiser | 06/vco-and-pll… | covered | 2 | |
| 10.3–10.4 | Settling; spur-reduction techniques | 06/vco-and-pll… | shallow | 2 | |
| 10.5.1–10.5.2 | PLL-based modulation (in-loop / two-point; offset PLL) | 06/transmitter-architectures | shallow | 2 | two-point modulation mentioned; offset (translational) loop one line |
| 10.6.1–10.6.3 | Pulse-swallow; dual-modulus; prescaler choice | 06/frequency-multipliers-dividers | covered | 3 | |
| 10.6.4 | Divider logic styles | — | n/a | 1 | |
| 10.6.5–10.6.7 | Miller; injection-locked dividers; divider delay & noise | 06/frequency-multipliers-dividers | shallow | 3 | ILD covered at L3; divider noise floor not quantified |
| 11.1–11.2.4 | Fractional-N: randomisation, ΣΔ noise shaping, higher order, out-of-band noise | 06/vco-and-pll… (MASH verified) | covered | 5 | |
| 11.2.5 | Effect of CP mismatch (noise folding) | — | missing | 1 | fractional spurs from CP non-linearity absent |
| 11.3.1–11.3.4 | Quantisation-noise reduction (DAC feed-forward, fractional divider, reference doubling, multiphase) | 06/frequency-multipliers… | shallow | 4 | reference doubler exists in parts pages only |
| 11.4 | Spectrum of quantisation noise | 06/vco-and-pll… | covered | 1 | |
| 12.1.1–12.3.3 | PA considerations; classes A/B/C; harmonic-enhanced A; class E; class F | 06/power-amplifiers | covered | 10 | |
| 12.4 | Cascode output stages | — | n/a | 1 | CMOS-specific |
| 12.5 | Large-signal impedance matching | 06/power-amplifiers (load line, load-pull) | covered | 1 | |
| 12.6.1, 12.6.2, 12.6.4 | Feed-forward; Cartesian feedback; envelope feedback | — | missing | 3 | only DPD / ET / Doherty covered among linearisers |
| 12.6.3 | Predistortion | 06/power-amplifiers (memory polynomial, verified DPD sim) | covered | 1 | |
| 12.7.1–12.8.2 | Polar modulation; outphasing | 06/transmitter-architectures | covered | 5 | Chireix combiner compensation not treated |
| 12.9 | Doherty PA | 06/power-amplifiers | covered | 1 | ideal symmetric efficiency verified; no practical design (offset lines, load-modulation with real device) |
| 12.10.1–12.10.5 | CMOS PA design examples | 06/power-amplifiers | n/a | 5 | |
| 13.1.1–13.1.4 | System-level RX/TX/synth; frequency planning | 07/receiver-cascade-analysis, 06/receiver-architectures | covered | 4 | |
| 13.2.1–13.2.2, 13.3.1–13.3.2 | LNA, mixer, PA, up-converter design | 06/* | covered | 4 | |
| 13.2.3 | AGC design | 07/dynamic-range… | shallow | 1 | no AGC loop dynamics (log-domain loop, attack/decay) |
| 13.4.1–13.4.3 | Synthesiser design (VCO, divider, loop) | 06/vco-and-pll… | covered | 3 | |

### 3.4 Lee, *The Design of CMOS Radio-Frequency Integrated Circuits*, 2nd ed. (Cambridge 2004)
ToC source: Cambridge Higher Education product page (chapter list `tocSimplified`, raw HTML). Section-level
titles are not publicly exposed (Cambridge Core requires login; LoC catalogue returned HTTP 403), so rows are
**chapters**; the note lists the chapter's characteristic topics checked by grep.

| Ch | Chapter | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1 | A nonlinear history of radio | — | n/a | 1 | (history: regenerative/superheterodyne origins mentioned only once) |
| 2 | Overview of wireless principles | 10/*, 09/* | covered | 1 | |
| 3 | Passive RLC networks (resonators, Q, matching, Foster/Cauer forms) | 01/resonance-and-q, 03/impedance-matching…, 03/broadband-matching-bode-fano | covered | 1 | |
| 4 | Characteristics of passive IC components (spiral inductors, on-chip capacitors, interconnect) | 04/inductors-at-rf, 04/capacitors-at-rf-mlcc | shallow | 1 | discrete parts deep; on-chip / PCB spiral inductors absent |
| 5 | A review of MOS device physics (short-channel, velocity saturation, scaling) | 05/fets-mosfet-jfet-gaas-gan | covered | 1 | |
| 6 | Distributed systems (lines, lumped-vs-distributed) | 03/telegrapher…, 02/quasi-static-vs-full-wave | covered | 1 | |
| 7 | The Smith chart and S-parameters | 03/smith-chart, 03/s-parameters | covered | 1 | |
| 8 | Bandwidth estimation (open- and short-circuit time constants, rise-time addition) | 05/amplifier-topologies, 01/transient-and-step-response | covered | 1 | OCτ present; no shunt-peaking / bandwidth-extension (inductive peaking, distributed amp) |
| 9 | High-frequency amplifier design (shunt peaking, distributed amplifiers, cascades) | 05/amplifier-topologies | shallow | 1 | shunt/series peaking absent; distributed amp one line |
| 10 | Voltage references and biasing (bandgap, constant-gm) | 05/power-supplies-for-rf-and-analog, 06/amplifier-stability-and-biasing | shallow | 1 | discrete bias networks covered; bandgap/PTAT and constant-gm references only named |
| 11 | Noise (MOSFET drain & induced gate noise, noise models) | 07/thermal-noise…, 07/shot-and-flicker-noise, 05/fets… | shallow | 1 | induced gate noise and its correlation (c ≈ j0.395) only mentioned once |
| 12 | LNA design (power-constrained noise optimisation) | 06/lna-design | covered | 1 | CMOS inductively degenerated LNA worked (Ex. 4) |
| 13 | Mixers | 06/mixers | covered | 1 | |
| 14 | Feedback systems (root locus, phase margin, compensation) | 05/feedback-and-stability, 00/laplace… | covered | 1 | root locus absent |
| 15 | RF power amplifiers (classes, linearisation, efficiency enhancement) | 06/power-amplifiers | covered | 1 | |
| 16 | Phase-locked loops | 06/vco-and-pll-synthesizers, 10/synchronization… | covered | 1 | |
| 17 | Oscillators and synthesizers (describing functions, Colpitts, DDS) | 05/oscillators, 06/vco-and-pll…, 14/nco-ddc-duc | covered | 1 | |
| 18 | Phase noise (LTV/ISF theory, cyclostationary noise, flicker up-conversion) | 07/phase-noise-and-jitter | shallow | 1 | **the chapter's core (ISF) is cited, not derived** |
| 19 | Architectures (GPS receiver, WLAN transceiver examples) | 06/receiver-architectures, 06/transmitter-architectures | covered | 1 | GPS example: 21-gnss pages pending |
| 20 | RF circuits through the ages | — | n/a | 1 | |

### 3.5 Ott, *Electromagnetic Compatibility Engineering* (Wiley 2009)
ToC source: Wiley product page 9780470189306 (raw ToC field). Most of domain 13 was still planned
(`emc-emi-fundamentals`, `shielding-and-isolation`, `power-distribution-decoupling-for-rf`,
`mixed-signal-layout`, `vias-stitching-fencing`) at first check; all five had landed by the 2026-10-02 re-check and rows were updated.

| § | Section | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1.1–1.3, 1.12, 1.15 | EMC intro; noise & interference; design for EMC; noise path; network theory | 13/emc-emi-fundamentals, 02/radiation-from-currents… | covered | 5 | page landed 2026-10 |
| 1.4–1.11 | Documentation; US/Canada/EU/international/military/avionics EMC rules; regulatory process | 13/emc-emi-fundamentals, 19/certification-fcc-ce-imda | shallow | 8 | FCC 15B / CISPR limits used; MIL-STD-461 / DO-160 (avionics) not treated |
| 1.14 | Miscellaneous noise sources | — | missing | 1 | |
| 2.1–2.2 | Capacitive coupling; effect of shield on it | 13/grounding-and-return-paths | shallow | 2 | crosstalk distance rules only; no coupling-capacitance model |
| 2.3–2.5 | Inductive coupling; mutual inductance; effect of shield on magnetic coupling | 02/inductance-capacitance-from-fields, 13/grounding… | shallow | 3 | M computed, but shield-current / shield cut-off frequency (ω = R_s/L_s) not treated |
| 2.6–2.10 | Shielding against magnetic radiation; receptor shielding; common-impedance coupling; experiments | — | missing | 5 | |
| 2.11–2.15 | Shield transfer impedance; coax vs twisted pair; braided & spiral shields; shield terminations (pigtails) | 03/coax-and-cables, 18/connectors-and-cables-parts | shallow | 5 | transfer impedance one mention; pigtail inductance not quantified |
| 2.16–2.17 | Ribbon cables; electrically long cables | — | missing | 2 | |
| 3.1 | AC power distribution & safety grounds | — | n/a | 1 | mains wiring |
| 3.2–3.4, 3.7 | Signal grounds; equipment grounding; ground loops; single reference | 13/grounding-and-return-paths | shallow | 4 | return-path physics covered well; single-point vs multipoint vs hybrid grounding, ground-loop breaking absent |
| 3.5–3.6 | Common-mode choke (LF and HF analysis) | 04/ferrites-and-beads, 06/baluns… | shallow | 2 | CM choke as balun covered; CM choke for ground-loop/cable emission not analysed |
| 4.1 | Balancing (CMRR, balanced circuits) | 05/analog-signal-conditioning, 05/op-amps-real-limitations | covered | 1 | |
| 4.2–4.3 | Filtering; power-supply decoupling | 04/ferrites-and-beads, 04/capacitors-at-rf-mlcc, 05/power-supplies… | covered | 2 | plus 13/power-distribution-decoupling-for-rf (landed 2026-10) |
| 4.4–4.6 | Driving capacitive loads; system bandwidth; modulation & coding | 05/feedback-and-stability (Ex. 1) | covered | 3 | |
| 5.1–5.7 | Passive components (C, L, transformers, R, conductors, lines, ferrites) | 04/*, 03/* | covered | 7 | |
| 6.1–6.2 | Near/far fields; wave impedance | 02/near-field-far-field | covered | 2 | |
| 6.3–6.8 | Shielding effectiveness; absorption & reflection loss; magnetic-material shields | 02/near-field-far-field (Schelkunoff) | covered | 6 | derived at L3 but no practical can/enclosure design |
| 6.9–6.12 | Shield experiments; apertures; waveguide below cut-off; conductive gaskets | 13/shielding-and-isolation | shallow | 4 | hole/slot size rules covered; waveguide-below-cut-off and gaskets one or two mentions |
| 6.13–6.18 | Ideal shield; conductive windows; internal shields; cavity resonance; shield grounding | 13/shielding-and-isolation | covered | 6 | can resonance, fence spacing, feed-throughs (windows n/a) |
| 7.1–7.14 | Contact protection (arcs, inductive loads, snubbers) | 01/transient-and-step-response | missing | 14 | only relevant to pyro/servo switching: flyback/snubber design absent |
| 8.1–8.8 | Intrinsic noise (thermal, ENBW, shot, contact/flicker, popcorn, addition, measurement) | 07/thermal-noise…, 07/shot-and-flicker-noise, 00/probability… | covered | 8 | |
| 9.1–9.12 | Active-device noise (F, Vn–In model, optimum source R, cascades, T_e, BJT/FET/op-amp noise) | 07/noise-figure-and-friis, 05/low-noise-analog-design, 05/op-amps-real-limitations | covered | 12 | |
| 10.1–10.5 | Digital circuit grounding & ground noise | 13/grounding-and-return-paths, 02/quasi-static… | shallow | 5 | ground bounce / SSN not quantified |
| 10.6–10.7 | Ground-plane current distribution & impedance; logic current flow | 13/grounding-and-return-paths, 02/inductance-capacitance… (partial L) | covered | 2 | |
| 11.1–11.9 | Digital power distribution & decoupling (strategies, placement, bulk, power-entry filters) | 13/power-distribution-decoupling-for-rf, 04/capacitors-at-rf-mlcc | covered | 9 | target impedance, bulk for TX bursts, bead damping |
| 12.1–12.4 | Differential- and common-mode radiation and their control | 13/emc-emi-fundamentals | covered | 4 | Ott formulas and CM-current limits |
| 13.1–13.9 | Conducted emissions (LISN, SMPS noise, power-line filters, dithering, motor drives, harmonics) | 05/power-supplies… | missing | 9 | SMPS spur/ripple for RF rails covered in 05; LISN/CE testing absent (13.1, 13.3, 13.8–13.9 mostly n/a for battery avionics) |
| 14.1–14.4 | RF and transient immunity; power-line disturbances | 13/emc-emi-fundamentals (own-TX upset of sensors/pyro) | shallow | 4 | RF immunity of flight electronics covered; transient (EFT/surge) immunity absent (power-line n/a) |
| 15.1–15.11 | ESD (generation, HBM, protection, hardening, grounding, software hardening) | 19/lab-safety-esd-high-power, 05/diodes… (TVS), 05/analog-signal-conditioning | shallow | 11 | TVS selection covered; system ESD design (entry paths, software time windows) absent |
| 16.1–16.4 | PCB layout, chassis connection, return-path discontinuities, stack-up | 13/grounding-and-return-paths, 13/stackups-and-materials | covered | 4 | |
| 17.1–17.10 | Mixed-signal layout (split planes, ADC grounding, vertical isolation) | 13/mixed-signal-layout | covered | 10 | page landed 2026-10 |
| 18.1–18.12 | Pre-compliance EMC measurements (probes, CM cable current, near-field, CE, SA, 1 m RE, immunity, margin) | 13/emc-emi-fundamentals, 17/oscilloscopes-and-probing-for-rf, 17/spectrum-analyzers | covered | 12 | conducted-emission (LISN) testing absent |

### 3.6 Hong, *Microstrip Filters for RF/Microwave Applications*, 2nd ed. (Wiley 2011; 1st ed. with Lancaster 2001)
ToC source: Wiley product page 9780470408773 (raw ToC field). The 2nd edition (Hong alone) supersedes Hong & Lancaster.

| § | Section | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1 | Introduction | — | n/a | 1 | |
| 2.1–2.8 | Network variables; S, Y, Z, ABCD; line networks; connections; conversions | 01/two-port-networks…, 03/s-parameters | covered | 8 | |
| 2.9 | Symmetrical network analysis (even/odd bisection) | 06/couplers… (even/odd) | covered | 1 | |
| 2.10–2.12 | Multiport; equivalent & dual networks; multimode networks | 03/s-parameters (mixed-mode) | shallow | 3 | |
| 3.1–3.3 | Transfer functions; LP prototypes; frequency & element transformations | 01/passive-filter-design-prototypes | covered | 3 | |
| 3.4 | Immittance (J/K) inverters | 01/passive-filter-design-prototypes, 06/rf-filters… | covered | 1 | |
| 3.5 | Richards' transformation & Kuroda identities | 06/rf-filters… | covered | 1 | |
| 3.6 | Dissipation and unloaded Q | 01/passive-filter-design-prototypes, 06/rf-filters… | covered | 1 | |
| 4.1–4.2 | Microstrip lines; coupled lines | 03/planar-lines…, 06/couplers… | covered | 2 | |
| 4.3 | Discontinuities and components (steps, bends, T-junctions, gaps, lumped elements) | 03/input-impedance-stubs… (open end) | shallow | 1 | see Pozar 4.6 |
| 4.4–4.5 | Other microstrip lines; CPW | 03/planar-lines-microstrip-stripline-cpwg | covered | 2 | |
| 4.6 | Slotlines | 03/planar-lines… | shallow | 1 | named |
| 5.1–5.2 | Low-pass and band-pass filters (stepped-impedance, stub, end-/parallel-coupled, hairpin, interdigital, combline) | 06/rf-filters… | covered | 2 | end-coupled & pseudo-combline not worked |
| 6.1–6.2 | High-pass and band-stop filters | 01/passive-filter-design-prototypes | shallow | 2 | lumped transformations only; no distributed quasi-HP or stub band-stop design |
| 7.1–7.6 | General coupling matrix; coupling theory; extracting k and Qe; examples; N+2 matrix | 06/rf-filters… (L2 extraction, L3 coupling matrix, Ex. 6) | covered | 6 | N+2 (source/load) matrix and synthesis of M from a polynomial (Cameron) not derived |
| 8.1–8.4 | CAD, computer-aided analysis, synthesis by optimisation | 16/em-solvers…, 16/python-rf-toolkit, 16/openems-workflow | shallow | 4 | no filter-tuning/optimisation workflow (space mapping, EM-circuit co-sim) |
| 9.1–9.3 | Single pair of TZs; cascaded quadruplet; trisection | 06/rf-filters… | covered | 3 | quadruplet demo verified |
| 9.4–9.7 | TL-inserted inverters; linear-phase; extracted-pole; canonical filters | — | missing | 4 | |
| 9.8 | Multiband filters | — | missing | 1 | (433 + 915 dual-band front end is a plausible need) |
| 10.1–10.3 | Open-loop/hairpin miniaturisation; slow-wave; dual-mode resonators | 06/rf-filters… (hairpin) | shallow | 3 | |
| 10.4–10.6 | Lumped-element; high-εr; multilayer (LTCC) filters | 06/rf-filters…, 18/filter-parts-saw-ceramic-ltcc | covered | 3 | |
| 11.1–11.6 | Superconducting filters | — | n/a | 6 | |
| 12.1–12.5 | UWB filters | — | missing | 5 | low priority |
| 13.1–13.8 | Tunable & reconfigurable filters (varactor combline, MEMS, piezo, ferroelectric) | 05/diodes… (varactors) | missing | 8 | varactor-tuned pre-selector is relevant to SDR front ends |

### 3.7 Mailloux, *Phased Array Antenna Handbook*, 3rd ed. (Artech House 2018)
ToC source: publisher e-book preview PDF on api.pageplace.de (preview-9781630815080), read with `pdftotext`.
(artechhouse.com is behind a Cloudflare challenge and was not used.) Counted at x.y.z level.

| § | Section | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1.1.1–1.1.2 | System requirements; directive properties | 12/array-factor-linear-arrays, 11/radar-range-equation | covered | 2 | |
| 1.1.3 | Array noise characterisation | 12/beamforming-architectures, 07/noise-figure-and-friis | shallow | 1 | array G/T with per-element LNAs & beamformer loss not derived |
| 1.1.4–1.1.5 | Receiving antenna in polarised field; system considerations | 09/polarization-mismatch-loss, 12/beamforming-architectures | covered | 2 | |
| 1.1.6 | Monopulse beam splitting | 12/tapering-sidelobe-control (Bayliss), 12/diy-phased-array-projects | shallow | 1 | Σ/Δ patterns named; monopulse ratio / angle-error slope & accuracy not derived (also missing from 11-radar tracking) |
| 1.2.1–1.2.11 | Scanning & collimation; 1-D/2-D scan; beamwidth & directivity; realised gain & scan loss; grating lobes; bandwidth; array size | 12/array-factor…, 12/beam-steering-grating-lobes, 12/planar-arrays… | covered | 11 | |
| 1.2.12 | EIRP and G/T of large 2-D arrays | 09/link-budget-methodology, 12/beamforming-architectures | covered | 1 | |
| 1.2.13–1.2.14 | Gain limits from circuit loss; random errors | 12/beamforming-architectures, 12/tapering-sidelobe-control | covered | 2 | |
| 1.2.15 | Minimum number of elements vs scan coverage | 12/beam-steering… | covered | 1 | |
| 1.2.16 | Time-delay compensation | 12/beam-steering…, 12/phase-shifters-ttd-components | covered | 1 | |
| 1.3.1–1.3.5 | Aperture; feed architectures; beamforming; RF control components; MMICs | 12/beamforming-architectures, 12/phase-shifters…, 18/phased-array-and-radar-parts | covered | 5 | |
| 1.3.6 | Antenna components for mobile phones | 08/pcb-and-chip-antennas | covered | 1 | |
| 1.3.7 | Metamaterials for array control | — | missing | 1 | low priority |
| 2.1.1–2.1.2 | Radiation integrals; element pattern, coupling & gain | 12/planar-arrays-element-pattern-coupling | covered | 2 | |
| 2.2.1–2.2.2 | Linear & planar array characteristics | 12/array-factor…, 12/planar-arrays… | covered | 2 | |
| 2.3 | Scanning to endfire | 12/array-factor… (Hansen–Woodyard) | covered | 1 | |
| 2.4.1–2.4.3 | Thinned arrays (density taper, probabilistic, quantised amplitude) | 12/tapering-sidelobe-control | shallow | 3 | one mention; statistical sidelobe of random thinning (≈ 1/N_elements) not derived |
| 3.1.1–3.1.3 | Fourier; Schelkunoff; Woodward synthesis | 12/tapering-sidelobe-control, 12/array-factor… | shallow | 3 | see Balanis 7.3–7.5 |
| 3.1.4–3.1.5 | Dolph–Chebyshev; Taylor line source | 12/tapering-sidelobe-control (verified) | covered | 2 | |
| 3.1.6 | Modified sin πz/πz patterns | — | missing | 1 | |
| 3.1.7 | Bayliss difference patterns | 12/tapering-sidelobe-control | shallow | 1 | named; no Bayliss coefficients |
| 3.1.8–3.1.10 | Elliott's Taylor-based methods; discretisation of continuous illuminations; power-pattern optimisation | 12/tapering-sidelobe-control | shallow | 3 | discretisation by sampling mentioned; Elliott's root-perturbation absent |
| 3.2.1–3.2.3 | Numerical power-pattern synthesis; alternating projection; constrained synthesis | 12/tapering-sidelobe-control | shallow | 3 | convex/LS synthesis named; no worked script (would be a natural `tools/verify` addition) |
| 3.3.1–3.3.2 | Taylor circular & Bayliss circular synthesis | — | missing | 2 | relevant to round planar arrays |
| 3.4.1–3.4.5 | Adaptive arrays; generalised S/N optimisation; sidelobe canceller; fully adaptive; wideband adaptive | 12/adaptive-beamforming-doa | covered | 5 | sidelobe canceller (GSC) not by name; wideband (tapped-delay) adaptive only mentioned |
| 3.5 | Patterns by covariance-matrix inversion | 12/adaptive-beamforming-doa (MVDR/SMI) | covered | 1 | |
| 3.6.1–3.6.4 | Synthesis with mutual coupling; with measured element patterns; array-failure correction | 12/array-calibration, 12/planar-arrays… | shallow | 4 | failure correction 2 mentions |
| 4.1–4.1.1 | Conformal arrays: methods of analysis | — | missing | 2 | conformal arrays on a rocket body tube are directly relevant (wrap-around telemetry antennas) |
| 4.2.1–4.2.4 | Circular/cylindrical arrays; phase-mode excitation; directional elements; sector arrays | 12/adaptive-beamforming-doa (UCA), 08/antennas-on-rockets | shallow | 4 | phase-mode theory absent |
| 4.3–4.4 | Spherical, hemispherical, truncated-conical arrays | — | missing | 2 | |
| 5.1–5.2 | Array elements; polarisation of infinitesimal elements | 08/antenna-fundamentals, 08/antenna-polarization… | covered | 2 | |
| 5.3.1–5.3.2, 5.3.7 | Effective radius; dipole & monopole; folded dipole | 08/dipoles-and-monopoles | covered | 3 | |
| 5.3.3–5.3.5 | Special feeds; off-centre-fed dipoles; sleeve dipole/monopole | 08/dipoles-and-monopoles, 08/antennas-on-rockets | covered | 3 | |
| 5.3.6, 5.3.8–5.3.9 | Bow-tie & wideband dipoles; microstrip dipoles; other wire structures | — | missing | 3 | |
| 5.4.1–5.4.10 | Wideband elements (self-complementary, TEM horn, long-slot/connected, spiral, Vivaldi & antipodal Vivaldi, broadband & capacitively coupled dipoles, bunny-ear) | 12/planar-arrays… (tightly-coupled one mention) | missing | 10 | whole wideband-element family absent |
| 5.5.1–5.5.4 | Aperture elements (slot, open waveguide, ridged guide, horn) | 08/slot-antennas, 08/horn-reflector… | shallow | 4 | slot & horn covered; open-ended/ridged waveguide radiators absent |
| 5.6.1–5.6.2 | Microstrip patch elements; Collings balanced radiator | 08/patch-antennas | covered | 2 | |
| 5.7 | Elements for alternative transmission lines | — | missing | 1 | |
| 5.8.1–5.8.2 | Waveguide slot arrays; printed series-fed arrays | 08/slot-antennas (slotted-waveguide omni) | shallow | 2 | slotted-waveguide array covered; printed series-fed (comb-line) patch arrays — the 24 GHz radar-board antenna — absent |
| 5.9 | Elements & polarisers for polarisation diversity | 08/antenna-polarization… | shallow | 1 | |
| 6.1 | Mutual impedance effects | 12/planar-arrays-element-pattern-coupling | covered | 1 | |
| 6.2.1–6.2.2 | Integral-equation formulation for finite & infinite arrays | 12/planar-arrays… (Floquet) | shallow | 2 | periodic Green's function not derived |
| 6.3–6.5 | Scan blindness & surface waves; infinite-array impedance & element patterns; semi-infinite/finite arrays | 12/planar-arrays… | covered | 3 | |
| 6.6.1–6.6.2 | Wide-angle matching: reduced spacing; WAIM sheets | 12/planar-arrays… | shallow | 2 | WAIM one mention |
| 6.7 | Coupling on non-planar surfaces | — | missing | 1 | |
| 6.8–6.8.1 | Small arrays & waveguide simulators | 12/planar-arrays… | shallow | 2 | |
| 7.1–7.2.4 | Random amplitude & phase errors (average pattern, directivity, pointing error, peak sidelobes) | 12/tapering-sidelobe-control, 12/array-calibration | covered | 5 | |
| 7.3.1–7.3.3 | Periodic errors; phase quantisation lobes and their reduction | 12/beam-steering-grating-lobes | covered | 3 | |
| 7.3.4–7.3.6 | Subarrays with quantised taper; time delay at subarray ports; discrete-phase subarrays | 12/beamforming-architectures, 12/beam-steering… | covered | 3 | |
| 8.1–8.1.2 | Multiple-beam systems; crossover loss | 12/beamforming-architectures | covered | 3 | |
| 8.2.1–8.2.5 | Orthogonality loss & Stein limit; power dividers; beam-forming matrices (Butler) & optical beamformers | 12/beamforming-architectures | covered | 5 | Stein limit 2 mentions — stated, not derived |
| 8.3.1–8.3.3 | Multiple-beam lenses (Rotman); reflectors; reflectarrays | 12/beamforming-architectures | shallow | 3 | Rotman covered; reflectarray/lens one line |
| 9.1.1–9.1.3 | Limited field-of-view arrays; aperiodic & thinned arrays | 12/beamforming-architectures | shallow | 3 | |
| 9.2.1–9.2.3 | Completely overlapped subarrays; array-fed reflectors/lenses; dual-transform | — | missing | 3 | |
| 9.3.1–9.3.3 | Wideband scanning: time-delayed offset beams; contiguous & overlapped TTD subarrays | 12/phase-shifters-ttd-components, 12/beam-steering… | covered | 3 | overlapped TTD subarrays not treated |

### 3.8 Kaplan & Hegarty (eds.), *Understanding GPS/GNSS: Principles and Applications*, 3rd ed. (Artech 2017)
ToC source: NavtechGPS (GNSS training vendor) hosted ToC PDF `1024B_TOC.pdf`, read with `pdftotext`.
Domain 21-gnss was empty on 2026-09-29; re-checked 2026-10-02 when 3 of its 8 planned pages had landed
(`gnss-signals-and-codes`, `gnss-receiver-architecture-acquisition-tracking`, `gnss-on-rockets-dynamics-and-limits`).
Rows still waiting for a planned page are marked *planned 21/<slug>*.

| § | Section | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1.1–1.3, 1.10 | Introduction; GNSS overview; GPS; organisation | 21/gnss-signals-and-codes | covered | 4 | |
| 1.4–1.7 | GLONASS; Galileo; BeiDou; regional systems | 21/gnss-signals-and-codes | covered | 4 | signals/bands level |
| 1.8 | Augmentations (SBAS, GBAS) | 21/gnss-signals-and-codes (SBAS) | shallow | 1 | *planned 21/rtk-ppp-and-corrections* |
| 1.9 | Markets and applications | — | n/a | 1 | |
| 2.1 | Ranging by time of arrival | 21/gnss-receiver-architecture… | covered | 1 | |
| 2.2 | Reference coordinate systems (ECEF, WGS-84, geodetic↔ECEF, ENU) | — | missing | 1 | not in the 3 landed pages; needed for flight-computer navigation maths |
| 2.3 | Fundamentals of satellite orbits (Kepler elements) | — | missing | 1 | |
| 2.4 | GNSS signals | 21/gnss-signals-and-codes | covered | 1 | |
| 2.5 | Position determination from ranging codes (linearised least squares) | 21/gnss-receiver-architecture… | covered | 1 | |
| 2.6 | User velocity (Doppler / delta-range) | 21/gnss-receiver-architecture…, 21/gnss-on-rockets… | shallow | 1 | Doppler-velocity solution not derived |
| 2.7 | Frequency sources, time, and GNSS | 04/crystals-and-resonators, 21/gnss-on-rockets… (g-sensitivity) | shallow | 1 | *planned 21/gnss-timing-1pps* |
| 3.1–3.4, 3.6 | GPS overview; space, control, user segments; services | 21/gnss-signals-and-codes | shallow | 5 | segments only in passing |
| 3.5 | GPS geodesy & time scale | — | missing | 1 | |
| 3.7 | GPS signals (L1 C/A, L1C, L2C, L5; codes, nav data) | 21/gnss-signals-and-codes | covered | 1 | |
| 3.8 | Ephemeris parameters & satellite-position computation | 21/gnss-signals-and-codes (nav message) | shallow | 1 | *planned 21/ttff-agps-almanac-ephemeris* |
| 4.7, 5.5, 6.6 | GLONASS FDMA, Galileo (BOC/CBOC) and BeiDou signals | 21/gnss-signals-and-codes | covered | 3 | |
| 4.1–4.6, 5.1–5.4, 5.6–5.10, 6.1–6.5 | GLONASS/Galileo/BeiDou programmes, segments, geodesy/time, services, SAR, deployment | — | n/a | 20 | system-programme detail, low relevance |
| 7.1–7.2 | QZSS; NavIC | 21/gnss-signals-and-codes | covered | 2 | |
| 8.1–8.3 | Receiver overview; antennas; front end | 21/gnss-receiver-architecture…, 08/gnss-antennas, 07/receiver-cascade-analysis | covered | 3 | |
| 8.4–8.5 | Digital channels; acquisition (serial, FFT-parallel, coherent/non-coherent integration) | 21/gnss-receiver-architecture… | covered | 2 | |
| 8.6–8.8 | Carrier tracking (Costas, FLL-assisted PLL); code tracking (DLL); loop filters | 21/gnss-receiver-architecture…, 10/synchronization-carrier-timing | covered | 3 | discriminator-curve derivations & loop-order vs dynamics table worth checking for depth |
| 8.9 | Measurement errors & tracking thresholds (thermal jitter, dynamic stress) | 21/gnss-on-rockets-dynamics-and-limits | covered | 1 | acceleration/jerk limits for rockets |
| 8.10–8.13 | Pseudorange/delta-range/integrated-Doppler formation; initial operations; data demod; special functions | 21/gnss-receiver-architecture… | shallow | 4 | |
| 9.1–9.2 | Disruptions; interference | 06/rf-switches… (Ex. 4), 13/mixed-signal-layout (self-jamming), 13/shielding-and-isolation | shallow | 2 | *planned 21/gnss-interference-jamming-spoofing* |
| 9.3 | Ionospheric scintillation | 09/ionospheric-hf-propagation | covered | 1 | |
| 9.4–9.5 | Signal blockage; multipath | 08/gnss-antennas, 21/gnss-on-rockets… | covered | 2 | |
| 10.1–10.3 | Measurement errors; pseudorange error budgets (UERE) | — | missing | 3 | *planned 21/gnss-error-sources-dop* |
| 11.1–11.2 | PVT estimation concepts (DOP, least squares, Kalman) | 21/gnss-receiver-architecture… (Kalman intro) | shallow | 2 | DOP geometry derivation *planned 21/gnss-error-sources-dop* |
| 11.3–11.5 | Availability; integrity (RAIM); continuity | — | missing | 3 | |
| 12.1–12.3 | Code- & carrier-based DGNSS (RTK, integer ambiguity) | 18/rf-modules (ZED-F9P RTK use) | shallow | 3 | *planned 21/rtk-ppp-and-corrections* |
| 12.4–12.6 | PPP; RTCM SC-104 formats; examples | 15/rocket-telemetry-radio-design (RTCM over LoRa) | shallow | 3 | |
| 13.1–13.3 | Integration overview; GNSS/INS; land-vehicle sensors | — | missing | 3 | GNSS/IMU fusion (loosely/tightly coupled Kalman) absent KB-wide — core flight-computer knowledge |
| 13.4–13.5 | A-GNSS; hybrid positioning | — | missing | 2 | *planned 21/ttff-agps…* |
| 14.1–14.4 | Markets; civil & military applications | — | n/a | 4 | export (COCOM) limits are covered in 21/gnss-on-rockets |

### 3.9 Cripps, *RF Power Amplifiers for Wireless Communications*, 2nd ed. (Artech 2006)
ToC source: Skillsoft book page "In this Book" chapter list (raw HTML). Chapter level only; notes list the
chapter topics checked.

| Ch | Chapter | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1 | Introduction (linear/weakly/strongly nonlinear, device models, conjugate match, device technology) | 06/power-amplifiers, 01/network-theorems… (Ex. 3), 05/fets-mosfet-jfet-gaas-gan | covered | 1 | |
| 2 | Linear PA design (load line vs conjugate match, load-pull contours, class A) | 06/power-amplifiers (Cripps contours verified) | covered | 1 | |
| 3 | Conventional high-efficiency modes (reduced conduction angle, AB/B/C) | 06/power-amplifiers (conduction-angle Fourier table) | covered | 1 | |
| 4 | Class AB PAs at GHz (knee, nonlinear Cgs/Cds, harmonic shorts) | 06/power-amplifiers | shallow | 1 | knee voltage used; nonlinear-capacitance effects on AB linearity (sweet spots) absent |
| 5 | Practical design of linear PAs (matching, harmonic terminations, stability, thermal) | 06/power-amplifiers (Ex. 1–2), 06/amplifier-stability-and-biasing, 13/thermal-management-rf | covered | 1 | |
| 6 | Overdriven PAs and class F (and inverse F) | 06/power-amplifiers (class-F LP optimisation) | covered | 1 | |
| 7 | Switching-mode amplifiers (class D, E) | 06/power-amplifiers (class-E ODE sim, Ex. 3) | covered | 1 | |
| 8 | Switching PA modes at GHz (finite switch resistance, parasitic C, class E limits; continuous modes) | 06/power-amplifiers | shallow | 1 | class-J / continuous class-B/J modes absent |
| 9 | Nonlinear effects (AM-AM, AM-PM, IM, spectral regrowth, memory) | 06/power-amplifiers, 07/nonlinearity… | shallow | 1 | AM-PM and memory effects named only; no Volterra/behavioural models |
| 10 | Efficiency enhancement (Doherty, ET, EER, outphasing, bias adaptation) | 06/power-amplifiers, 06/transmitter-architectures | covered | 1 | ideal-device Doherty only — practical Doherty design (offset lines, peaking-device sizing, AM-PM) missing |
| 11 | PA bias circuit design (bias networks, video/baseband impedance, sequencing) | 06/amplifier-stability-and-biasing (Ex. 5–8) | covered | 1 | baseband (video-bandwidth) impedance / bias-induced memory absent |
| 12 | Load-pull techniques (passive, active, harmonic load-pull) | 06/power-amplifiers | shallow | 1 | concept only; no load-pull system or DIY load-pull with a tuner |
| 13 | PA architecture (balanced, push-pull, combining) | 06/couplers… (Ex. 5 combining), 06/baluns… | shallow | 1 | balanced PA and push-pull (balun-based) not treated as PA topologies |
| 14 | PA linearisation (predistortion, feed-forward, Cartesian loop, envelope feedback) | 06/power-amplifiers (DPD) | shallow | 1 | DPD good; feed-forward & Cartesian loop missing |

### 3.10 Richards, *Fundamentals of Radar Signal Processing*, 2nd ed. (McGraw-Hill 2014)
ToC source: McGraw-Hill product page (mheducation.com, chapter list in the page description; raw HTML).
Section titles are behind AccessEngineering/VitalSource logins (HTTP 403), so rows are chapters; notes list the
chapter's standard topics checked by grep.

| Ch | Chapter | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1 | Introduction to radar systems | 11/radar-range-equation, 11/pulsed-radar… | covered | 1 | |
| 2 | Signal models (amplitude/RCS & Swerling, clutter, noise, Doppler, spatial & spectral models) | 11/radar-cross-section, 11/detection-theory-cfar, 11/clutter-and-mti | covered | 1 | clutter amplitude distributions (Weibull, K, log-normal) only 2 mentions |
| 3 | Pulsed-radar data acquisition (A/D, I/Q demodulation & errors, fast/slow time data matrix, range sampling & straddle) | 14/iq-complex-baseband, 11/pulsed-radar…, 11/radar-range-equation (straddle) | shallow | 1 | fast-time/slow-time data cube vocabulary appears once; no data-matrix walk-through (the core mental model for FMCW/pulse-Doppler processing) |
| 4 | Radar waveforms (matched filter, LFM, range–Doppler coupling, stepped frequency, phase codes, ambiguity, range-sidelobe control) | 11/pulsed-radar-and-pulse-compression, 11/ambiguity-function-waveforms, 10/matched-filter-detection | covered | 1 | stepped-frequency (3 mentions) and mismatch/sidelobe-suppression filters shallow |
| 5 | Doppler processing (MTI cancellers, blind speeds, staggered PRF, improvement factor, pulse-Doppler DFT, MTD, pulse-pair) | 11/clutter-and-mti, 11/cw-and-doppler-radar | covered | 1 | MTD filter bank and pulse-pair (weather) estimator absent; PRF-ambiguity resolution (CRT) 4 mentions |
| 6 | Detection fundamentals (NP, coherent/non-coherent & binary integration, Albersheim/Shnidman, CFAR family) | 11/detection-theory-cfar | covered | 1 | |
| 7 | Measurements and tracking (estimation accuracy, CRLB for range/Doppler/angle, monopulse, α-β and Kalman trackers) | 11/ambiguity-function-waveforms (delay CRB) | shallow | 1 | **range CRB present; angle (monopulse) estimation, track filters (α-β, Kalman), gating/association absent** |
| 8 | Introduction to synthetic-aperture imaging (resolution, stripmap/spotlight, RDA/PFA/backprojection, autofocus) | 11/sar-and-imaging | covered | 1 | speckle one mention |
| 9 | Introduction to beamforming and STAP | 12/adaptive-beamforming-doa, 11/clutter-and-mti (STAP L3) | covered | 1 | STAP at overview depth (clutter ridge, DoF); no SMI-STAP worked example |

### 3.11 Proakis & Salehi, *Digital Communications*, 5th ed. (McGraw-Hill 2008)
ToC source: McGraw-Hill Online Learning Centre "Table of Contents" page and its linked brief-ToC Word file
(highered.mheducation.com/sites/0072957166/…; text read with `strings`). Chapter level (the publisher file is
the brief ToC); notes list chapter topics checked by grep.

| Ch | Chapter | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1 | Introduction | 10/* | covered | 1 | |
| 2 | Deterministic & random signal analysis (bandpass/lowpass equivalents, signal space, Gram–Schmidt, bandpass processes) | 14/iq-complex-baseband, 00/probability…, 10/matched-filter-detection | covered | 1 | signal-space/Gram–Schmidt only 2 mentions (no geometric derivation of error probability) |
| 3 | Digital modulation schemes (PAM/PSK/QAM, orthogonal/biorthogonal/simplex, CPM/CPFSK/MSK, spectra) | 10/digital-modulation-psk-qam-fsk | covered | 1 | biorthogonal/simplex absent; CPM general theory (phase trellis) shallow |
| 4 | Optimum receivers for AWGN (ML/MAP, error probabilities, union bound, non-coherent detection) | 10/matched-filter-detection, 10/ber-ebn0-and-shannon | covered | 1 | |
| 5 | Carrier & symbol synchronisation (ML phase/timing estimation, loops) | 10/synchronization-carrier-timing | covered | 1 | |
| 6 | Introduction to information theory (entropy, source coding, capacity, cut-off rate) | 10/ber-ebn0-and-shannon | shallow | 1 | Shannon capacity & finite-block-length covered; entropy/mutual information, source coding, capacity of constrained constellations absent |
| 7 | Linear block codes (Hamming, cyclic, BCH, RS, bounds) | 10/channel-coding-fec, 10/packet-framing-protocols | covered | 1 | |
| 8 | Trellis & graph codes (convolutional, Viterbi, BCJR, TCM, turbo, LDPC, BP) | 10/channel-coding-fec | shallow | 1 | Viterbi & code families covered; BCJR/sum-product only named; TCM absent |
| 9 | Band-limited channels (ISI, Nyquist, partial response, MLSE) | 10/pulse-shaping-isi | covered | 1 | partial response / duobinary 2 mentions |
| 10 | Adaptive equalisation (LMS, RLS, blind/CMA, DFE) | 10/pulse-shaping-isi (L3 + script §5) | covered | 1 | |
| 11 | Multichannel & multicarrier systems (OFDM) | 10/ofdm | covered | 1 | |
| 12 | Spread spectrum (DSSS, FHSS, processing & jamming margin, SS acquisition/tracking) | 10/spread-spectrum-dsss-fhss-css, 15/lora-phy-css-math | covered | 1 | PN acquisition & DLL tracking shallow (see Kaplan 8.5–8.7) |
| 13 | Fading channels I (characterisation, Rayleigh/Rician/Nakagami, diversity, performance in fading) | 09/multipath-fading-doppler, 09/link-margin-availability | covered | 1 | outage & diversity verified; average BER in Rayleigh fading (≈1/(4 Eb/N0)) not stated for coherent schemes |
| 14 | Fading channels II (capacity, outage capacity, coding for fading, BICM) | 09/multipath-fading-doppler, 10/channel-coding-fec (interleaver) | shallow | 1 | interleaving for a rolling rocket covered; ergodic/outage capacity, BICM absent |
| 15 | Multiple-antenna systems (MIMO channel & capacity, space-time codes, Alamouti, spatial multiplexing) | 00/matrices-and-linear-algebra… (SVD capacity) | shallow | 1 | SVD capacity derived in the maths page; no MIMO comms page (STBC, Alamouti, V-BLAST, diversity–multiplexing) |
| 16 | Multiuser communications (multiple access, MUD, random access/ALOHA) | 10/spread-spectrum…, 15/lorawan-vs-raw-lora | shallow | 1 | ALOHA throughput (relevant to multi-rocket LoRa channels) one mention; MUD absent |

### 3.12 Rappaport, *Wireless Communications: Principles and Practice*, 2nd ed. (Prentice Hall 2002)
ToC source: InformIT (Pearson) product page, "Table of Contents" tab (raw HTML; section titles unnumbered,
numbered here by order).

| § | Section(s) | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1.1–1.5, 2.1–2.6 | Evolution of mobile radio; 2G/3G, WLL/LMDS, WLAN, Bluetooth/PAN | 15/other-ism-radios-fsk-2g4 | n/a | 11 | history/standards survey |
| 3.1–3.7 | Cellular concept: frequency reuse, channel assignment, handoff, interference & capacity (C/I), trunking & GoS, coverage/capacity improvement | — | missing | 7 | co-channel interference / C/I maths useful for multi-team LoRa launches; the rest n/a-ish |
| 4.1–4.3 | Propagation intro; free space; power ↔ field | 09/friis-free-space-path-loss, 02/electromagnetic-units-and-constants | covered | 3 | |
| 4.4–4.6 | Reflection; ground reflection (two-ray) | 02/boundary-conditions…, 09/two-ray-ground-reflection | covered | 3 | |
| 4.7 | Diffraction | 09/diffraction-knife-edge | covered | 1 | |
| 4.8 | Scattering (rough surfaces, Rayleigh criterion, RCS) | 09/two-ray… (roughness), 11/radar-cross-section | covered | 1 | |
| 4.9–4.11 | Link budget with path-loss models; outdoor models; indoor models | 09/link-budget-methodology, 09/empirical-path-loss-models | covered | 3 | |
| 4.12–4.13 | Building penetration; ray tracing & site-specific modelling | 09/empirical-path-loss-models | shallow | 2 | penetration loss table absent; ray tracing named |
| 5.1–5.5 | Small-scale multipath; impulse-response model; measurements; channel parameters; fading types | 09/multipath-fading-doppler | covered | 5 | channel-sounding methods shallow |
| 5.6–5.7 | Rayleigh & Rician distributions; statistical fading models (Clarke/Jakes, level-crossing) | 09/multipath-fading-doppler, 00/probability… | covered | 2 | |
| 5.8 | Multipath shape-factor theory | — | missing | 1 | niche |
| 6.1–6.5 | FM vs AM; AM; angle modulation; digital-mod overview; line coding | 10/analog-modulation…, 10/digital-modulation… | covered | 5 | line coding (Manchester/NRZ) partially in packet-framing |
| 6.6–6.10 | Pulse shaping; geometric representation; linear; constant-envelope; combined modulation | 10/pulse-shaping-isi, 10/digital-modulation… | covered | 5 | |
| 6.11 | Spread-spectrum modulation | 10/spread-spectrum… | covered | 1 | |
| 6.12 | Modulation performance in fading & multipath | 09/multipath-fading-doppler, 10/modulation-choice-guide | shallow | 1 | see Proakis ch. 13 note |
| 7.1–7.9 | Equalisation: fundamentals, training, survey, linear & nonlinear (DFE, MLSE), adaptive algorithms, fractionally spaced | 10/pulse-shaping-isi | covered | 9 | |
| 7.10–7.11 | Diversity techniques; RAKE receiver | 09/multipath-fading-doppler, 10/spread-spectrum… | covered | 2 | RAKE one paragraph |
| 7.12–7.16 | Interleaving; channel coding; block & convolutional codes; coding gain | 10/channel-coding-fec | covered | 5 | |
| 7.17 | Trellis-coded modulation | — | missing | 1 | |
| 7.18 | Turbo codes | 10/channel-coding-fec | covered | 1 | |
| 8.1–8.11 | Speech coding | — | n/a | 11 | voice codecs (Codec2 for amateur digital voice would be the only relevant item) |
| 9.1–9.3 | Multiple access: FDMA; TDMA | 10/packet-framing-protocols, 15/ism-band-plans-duty-cycle | shallow | 3 | |
| 9.4 | Spread-spectrum multiple access (CDMA, FH-MA) | 10/spread-spectrum… | covered | 1 | |
| 9.5 | Space-division multiple access | 12/adaptive-beamforming-doa | covered | 1 | |
| 9.6 | Packet radio (ALOHA, slotted ALOHA, CSMA, reservation) | 15/lorawan-vs-raw-lora | missing | 1 | ALOHA throughput S = G e^(−2G) absent — the governing formula for many LoRa nodes |
| 9.7 | Capacity of cellular systems | — | n/a | 1 | |
| 10.1–10.15 | Wireless networking (PSTN, SS7, ISDN, UMTS …) | — | n/a | 15 | |
| 11.1–11.12 | Wireless standards (AMPS … PHS, US PCS & ISM bands) | 19/spectrum-allocation-ism-bands | n/a | 12 | ISM-band item covered |
| App. A | Trunking theory (Erlang B/C) | — | n/a | 1 | |
| App. B | Noise-figure calculations for link budgets | 07/noise-figure-and-friis, 09/link-budget-methodology | covered | 1 | |
| App. E–F | Gaussian approximations for CDMA; Q/erf functions | 00/special-functions…, 00/probability… | covered | 2 | |

### 3.13 Bogatin, *Signal and Power Integrity — Simplified*, 3rd ed. (Pearson 2018)
ToC source: 3rd-ed. chapter 1–4 sections from InformIT (page truncates after §4.2); full section list from the
official **2nd-ed.** Pearson sample-pages PDF (ptgmedia …/9780132349796.pdf), same 13-chapter structure.
Rows grouped; 3rd-ed. additions (serial-link eye/equalisation, more S-parameter material) fall in ch. 9, 12.
Domain 13 pages landed during this check; rows were re-checked on 2026-10-02 against `emc-emi-fundamentals`,
`shielding-and-isolation`, `power-distribution-decoupling-for-rf`, `mixed-signal-layout`, `rf-layout-rules`, `vias-stitching-fencing`.

| § | Section(s) | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1.1–1.15 | SI/PI/EMC overview; single-net quality; cross talk; rail collapse; EMI; methodology; models; measurements | 02/quasi-static-vs-full-wave, 13/grounding-and-return-paths, 17/* | covered | 15 | |
| 2.1–2.17 | Time/frequency domains; spectra of square waves; bandwidth vs rise time (0.35/t_r); bandwidth of measurement/model/interconnect | 00/fourier-series-and-transform, 01/transient-and-step-response, 17/oscilloscopes-and-probing-for-rf | covered | 17 | |
| 3.1–3.11 | Impedance; ideal vs real elements; equivalent circuit models; SPICE; measurement-based modelling | 01/lumped-elements…, 04/component-models-s2p-spice, 16/spice-circuit-simulation | covered | 11 | |
| 4.1–4.6 | Resistance: bulk resistivity, per length, sheet resistance | 02/skin-effect…, 04/pcb-parasitics… | covered | 6 | sheet resistance (Ω/□) never named |
| 5.1–5.9 | Capacitance: parallel plate, Dk, plane capacitance, per-length, 2-D field solvers, effective Dk | 02/inductance-capacitance-from-fields (own FD solver), 03/planar-lines…, 02/dielectrics… | covered | 9 | |
| 6.1–6.6, 6.8 | Inductance principles; self/mutual; partial; loop inductance | 02/inductance-capacitance-from-fields, 04/pcb-parasitics… | covered | 7 | |
| 6.7 | Effective inductance & ground bounce | 05/power-supplies…, 04/package-parasitics… | covered | 1 | |
| 6.9–6.13 | PDN loop inductance; per-square inductance of planes; via contacts; clearance-hole fields; loop mutual | 13/power-distribution-decoupling-for-rf, 04/pcb-parasitics… | shallow | 5 | plane spreading inductance mentioned (2), not derived |
| 6.14–6.19 | Equivalent inductance of multiples; current distribution & skin depth; high-μ materials; eddy currents | 02/skin-effect…, 02/magnetic-materials… | covered | 6 | |
| 7.1–7.12 | Physical basis of lines: return, speed, instantaneous & characteristic impedance, driving a line | 03/telegrapher…, 13/grounding-and-return-paths | covered | 12 | |
| 7.13–7.14 | Return paths; switching reference planes | 13/grounding-and-return-paths | covered | 2 | |
| 7.15–7.20 | First-order & n-section models; approximations & 2-D solver Z0; frequency variation of Z0 | 03/telegrapher…, 16/impedance-and-rf-calculators, 03/planar-lines… | covered | 6 | |
| 8.1–8.7 | Reflections; source impedance; bounce diagrams; simulating; TDR | 03/reflections…, 03/time-domain-reflectometry | covered | 7 | bounce diagram only 2 mentions |
| 8.8–8.12 | Unintentional discontinuities; when to terminate; termination strategies; short series lines & stubs | 02/quasi-static… (rise-time criteria) | shallow | 5 | **digital termination strategies (series/source, parallel, AC, Thevenin) absent** (also a D1 gap) |
| 8.13–8.19 | Capacitive end/mid loads; delay adders; corners & vias; loaded lines; inductive discontinuities; compensation | 03/time-domain-reflectometry (L2 lumped discontinuities, Ex. 2), 04/pcb-parasitics… | covered | 7 | compensation of a connector/pad discontinuity worked in TDR Ex. 2 |
| 9.1–9.12 | Lossy lines: conductor & dielectric loss, Df, models, lossy Z0 & velocity, attenuation, measured properties | 03/telegrapher…, 02/skin-effect…, 02/dielectrics… (Djordjevic–Sarkar) | covered | 12 | |
| 9.13–9.17 | Interconnect bandwidth; time-domain lossy behaviour; eye diagrams; pre-emphasis & equalisation | 10/pulse-shaping-isi (eye) | shallow | 5 | eye diagram covered for comms; interconnect ISI, CTLE/FFE for serial links absent (low priority for RF) |
| 10.1–10.4 | Cross talk origin; NEXT/FEXT; describing cross talk | 13/grounding-and-return-paths (crosstalk distance, Ex. 4) | shallow | 4 | NEXT/FEXT coefficients & saturation length absent |
| 10.5–10.7 | SPICE/Maxwell capacitance matrices; inductance matrix | 02/inductance-capacitance-from-fields (L3 capacitance matrices) | covered | 3 | |
| 10.8–10.20 | Saturation length; coupled currents; NEXT & FEXT; reducing FEXT; simulation; guard traces; Dk; timing; switching noise | 13/mixed-signal-layout, 13/grounding-and-return-paths | shallow | 13 | clock-to-RF isolation budget now covered; NEXT/FEXT coefficients and saturation length still absent |
| 11.1–11.11 | Differential signalling; differential/odd/even-mode impedance; return currents; modal velocities | 03/planar-lines… (Ex. 3 100 Ω pair), 06/couplers… (even/odd), 06/baluns… | covered | 11 | |
| 11.12–11.22 | Coupled-line model; measuring modes; terminating diff & common signals; mode conversion; EMI; crossing gaps; tight vs loose coupling; impedance matrix | 03/s-parameters (mixed-mode Ex. 3), 13/grounding… | shallow | 11 | mode conversion covered; termination of differential + common mode, tight-vs-loose coupling design rules absent |
| 12.1–12.18 | S-parameters for SI (return/insertion loss, port impedance, phase/magnitude of S21, single-ended vs mixed-mode, time vs frequency) | 03/s-parameters, 16/python-rf-toolkit (TDR from S) | covered | 18 | |
| 13.1–13.7 | PDN problem, root cause, guidelines, target impedance, VRM | 13/power-distribution-decoupling-for-rf | covered | 7 | |
| 13.8–13.21 | SPICE impedance; on-die C; package; MLCC & ESL; mounting loop inductance; parallel caps & anti-resonance; value selection; count | 04/capacitors-at-rf-mlcc (ESL, anti-resonance Ex. 3), 04/ferrites-and-beads | covered | 14 | |
| 13.22–13.28 | Sculpting impedance profiles; spreading inductance; location; chip view | 13/power-distribution-decoupling-for-rf | shallow | 7 | |

### 3.14 Lyons, *Understanding Digital Signal Processing*, 3rd ed. (Prentice Hall 2010)
ToC source: InformIT product page "Table of Contents" (raw HTML, complete).

| § | Section(s) | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1.1–1.8 | Discrete sequences; amplitude/power; LTI systems | 00/linear-systems-convolution | covered | 8 | |
| 2.1–2.4 | Aliasing; lowpass & bandpass sampling; practical bandpass sampling | 14/sampling-aliasing-bandpass-sampling | covered | 4 | |
| 3.1–3.13 | DFT: equation, symmetry, linearity, magnitudes, axis, shift, inverse, leakage, windows, scalloping, resolution & zero padding, processing gain, DFT of rect functions | 14/fft-spectral-analysis-windows | covered | 13 | |
| 3.14 | Interpreting the DFT via the DTFT | 14/sampling-aliasing…, 00/fourier-series-and-transform | shallow | 1 | DTFT named only (3 mentions) |
| 4.1–4.2 | FFT vs DFT; practical hints | 14/fft-spectral-analysis-windows | covered | 2 | |
| 4.3–4.6 | Radix-2 derivation; bit reversal; butterflies | 14/fft-spectral-analysis-windows (L3) | shallow | 4 | algorithm sketched; butterfly/bit-reversal (needed for FPGA FFTs) one mention |
| 5.1–5.10 | FIR filters: convolution; LP/BP/HP design; Parks–McClellan; half-band; phase response; analysis | 14/digital-filters-fir-iir, 14/multirate… | covered | 10 | |
| 6.1–6.2 | IIR intro; Laplace transform | 00/laplace-transfer-functions-bode | covered | 2 | |
| 6.3–6.5 | z-transform; IIR analysis by z-transform; poles & zeros | 14/digital-filters-fir-iir | shallow | 3 | **no z-transform derivation anywhere in the KB** (00/_index lists it as a known gap) |
| 6.6–6.9 | IIR structures; pitfalls; cascaded biquads; gain scaling | 14/digital-filters-fir-iir (L3 structures, quantisation) | covered | 4 | |
| 6.10–6.13 | Impulse-invariance; bilinear transform; optimised IIR; IIR vs FIR | 14/digital-filters-fir-iir | covered | 4 | impulse invariance one mention |
| 7.1–7.3 | Differentiators; integrators; matched filters | 10/matched-filter-detection, 14/software-demodulation | covered | 3 | differentiator design one mention |
| 7.4 | Interpolated FIR (IFIR) | — | missing | 1 | |
| 7.5 | Frequency-sampling filters | — | missing | 1 | |
| 8.1–8.9 | Quadrature signals; complex phasors; negative frequency; complex down-conversion | 14/iq-complex-baseband, 00/complex-numbers-and-phasors | covered | 9 | |
| 9.1–9.6 | Discrete Hilbert transform; analytic signal generation | 00/linear-systems-convolution (L3), 14/iq-complex-baseband | covered | 6 | discrete Hilbert FIR design not worked |
| 10.1–10.14 | Sample-rate conversion: decimation, interpolation, polyphase, rational factors, half-band, IFIR, CIC | 14/multirate-dsp-decimation-cic | covered | 14 | |
| 11.1–11.6 | Signal averaging: coherent, incoherent, FFT averaging, phase-angle averaging, exponential averaging | 14/fft-spectral-analysis-windows, 17/spectrum-analyzers, 00/probability… | covered | 6 | |
| 12.1–12.5 | Data formats: fixed point, precision, finite word length, floating & block floating point | 14/digital-filters-fir-iir, 14/fpga-for-sdr | covered | 5 | |
| 13.x (≈12 items) | DSP tricks that are covered: multiplier-free translation (fs/4), arctan/CORDIC, FM demod algorithms, DC removal, ADC quantisation-noise reduction (dither) & ADC testing, frequency-domain windowing, quadrature oscillator, Goertzel, zero-phase filtering, spectral flipping | 14/nco-ddc-duc, 14/software-demodulation, 05/data-converters-adc-dac, 14/fft-spectral-analysis-windows, 14/multirate… | covered | 12 | |
| 13.x (≈15 items) | DSP tricks missing: sliding DFT; zoom FFT; fast FIR via FFT (overlap-add/save); digital AGC loop; magnitude/α-max-β-min approximation; spectral-peak (sub-bin) interpolation; single-tone detection; large DFTs from small FFTs; real-sequence FFT tricks; signal-transition detection; running variance | — | missing | 15 | sub-bin peak interpolation matters for FMCW range and LoRa-style tone estimation |
| 13.x (≈24 items) | Remaining niche tricks (polynomial evaluation, sharpened FIR, impulsive-noise smoothing, twiddle computation …) | — | n/a | 24 | |
| App. A–I | Complex numbers; geometric series; statistics; dB; filter terms; FSF tables; Chebyshev windows | 00/*, 14/fft-spectral-analysis-windows | covered | 9 | |

### 3.15 Horowitz & Hill, *The Art of Electronics*, 3rd ed. (Cambridge 2015) — analog/RF chapters
ToC source: authors' site artofelectronics.net/the-book/table-of-contents/ (x.y level). Digital chapters 10, 11,
14, 15 and non-electronics appendices are n/a for this check (listed as one row each).

| § | Section(s) | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1.1–1.7 | Foundations: V/I/R; signals; C & ac circuits; L & transformers; diodes; impedance | 01/*, 05/diodes…, 00/complex-numbers… | covered | 7 | |
| 1.8 | Putting it together — an AM radio | 10/analog-modulation…, 06/receiver-architectures | shallow | 1 | no end-to-end "simplest radio" walkthrough at beginner level (crystal set / TRF); 20-projects has none planned |
| 1.9–1.10 | Other passive components; markings & tiny parts | 04/*, 18/* | covered | 2 | |
| 2.1–2.3 | BJT basics; basic circuits; Ebers–Moll applied | 05/bjt-fundamentals-small-signal | covered | 3 | |
| 2.4 | Amplifier building blocks (differential pair, current mirrors, push-pull output) | 05/amplifier-topologies | shallow | 1 | diff pair covered; current mirrors 3 mentions; push-pull/class-AB output stages absent |
| 2.5–2.6 | Negative feedback; typical transistor circuits | 05/feedback-and-stability, 05/amplifier-topologies | covered | 2 | |
| 3.1–3.6 | FETs: linear circuits, JFETs, switches, power MOSFETs, linear MOSFET use | 05/fets-mosfet-jfet-gaas-gan | covered | 6 | load switches / high-side switching (pyro channels) in Ex. 1 |
| 4.1–4.9 | Op-amps: ideal; basic circuits; smorgasbord; detailed behaviour; single supply; other amp types; compensation | 05/op-amps-real-limitations, 05/feedback-and-stability | covered | 9 | |
| 5.1–5.10 | Precision design: error budgets, component errors, input/output errors, RRIO, choosing op-amps | 05/op-amps-real-limitations, 05/analog-signal-conditioning | covered | 10 | |
| 5.11 | Auto-zero / chopper amplifiers | 05/op-amps-real-limitations | shallow | 1 | 4 mentions; no chopper-artefact (ripple, IM) treatment |
| 5.12 | Designs by the masters (DMM) | — | n/a | 1 | |
| 5.13–5.17 | Difference, instrumentation & fully differential amplifiers | 05/analog-signal-conditioning, 05/op-amps-real-limitations | covered | 5 | |
| 6.1–6.3 | Filters: passive; active | 01/passive-filter-design-prototypes, 05/active-filters | covered | 3 | |
| 7.1 | Oscillators (RC, relaxation, LC, crystal) | 05/oscillators, 04/crystals-and-resonators | covered | 1 | relaxation/RC oscillators briefly |
| 7.2 | Timers (555, monostables) | — | missing | 1 | minor |
| 8.1–8.9 | Low-noise: noise, SNR & NF, BJT & JFET noise, en from NF, bipolar–FET shoot-out, diff/feedback amp noise, op-amp noise | 05/low-noise-analog-design, 07/noise-figure-and-friis, 05/op-amps-real-limitations | covered | 9 | |
| 8.10 | Signal transformers (noise matching) | 01/transformers-coupled-inductors, 05/low-noise-analog-design | shallow | 1 | |
| 8.11 | Noise in transimpedance amplifiers | 05/low-noise-analog-design (Ex. 4), 05/feedback-and-stability (Ex. 2) | covered | 1 | |
| 8.12–8.14 | Noise measurement & sources; bandwidth limiting & rms; SNR by bandwidth narrowing (lock-in) | 17/noise-figure-measurement, 00/probability… | shallow | 3 | lock-in / synchronous detection absent |
| 8.15–8.16 | Power-supply noise; interference, shielding, grounding | 05/power-supplies…, 13/grounding-and-return-paths | covered | 2 | |
| 9.1–9.3 | Zener → series-pass → integrated linear regulators | 05/power-supplies-for-rf-and-analog | covered | 3 | |
| 9.4 | Heat and power design (θJA, heatsinks) | 13/thermal-management-rf | covered | 1 | landed 2026-10 (junction temperature, thermal vias, spreading) |
| 9.5 | AC line → unregulated supply | — | n/a | 1 | |
| 9.6 | Switching regulators & dc–dc converters | 05/power-supplies-for-rf-and-analog | covered | 1 | converter topologies (buck/boost/SEPIC) and loop compensation only at spur/ripple level |
| 9.7–9.9 | Offline switchers; real-world switcher; inverters & switching amps | — | n/a | 3 | |
| 9.10 | Voltage references | 05/power-supplies…, 05/fets… | shallow | 1 | references for ADCs only mentioned |
| 9.11–9.13 | Power modules; batteries & supercaps; other topics | 05/power-supplies… (1S/2S pack Ex. 3) | covered | 3 | |
| 10–11 | Digital logic; programmable logic | 14/fpga-for-sdr (FPGA only) | n/a | 12 | |
| 12.1–12.2 | CMOS/TTL interfacing; probing digital signals | 17/oscilloscopes-and-probing-for-rf | n/a | 2 | |
| 12.3 | Comparators (hysteresis, speed) | — | missing | 1 | comparator/Schmitt design absent (2 mentions) — needed for envelope/RSSI squelch, zero-crossing FSK |
| 12.4–12.8 | Driving loads; opto emitters/detectors; optocouplers; fibre links | 05/low-noise-analog-design (photodiode) | shallow | 5 | |
| 12.9–12.10 | Digital signals & long wires; driving cables | 03/reflections…, 02/quasi-static… | shallow | 2 | back-termination / cable drivers absent (see Bogatin 8.9–8.12) |
| 13.1–13.4 | DACs, examples, converter linearity | 05/data-converters-adc-dac | covered | 4 | |
| 13.5–13.12 | ADCs: flash, SAR, integrating, ΔΣ, trade-offs, unusual converters, system examples | 05/data-converters-adc-dac, 18/adcs-dacs-for-sdr | covered | 8 | |
| 13.13 | Phase-locked loops | 06/vco-and-pll-synthesizers | covered | 1 | |
| 13.14 | Pseudorandom sequences & noise generation | 10/spread-spectrum… | shallow | 1 | LFSR theory only in passing |
| 14–15 | Computers, buses, microcontrollers | — | n/a | 18 | |
| App. E, H, J | LC Butterworth filters; transmission lines & matching; SPICE primer | 01/passive-filter…, 03/*, 16/spice-circuit-simulation | covered | 3 | |
| App. A–D, F, G, I, K–P | Other appendices (maths, schematics, resistors, Thevenin, load lines, curve tracer, TV, suppliers, instruments, scope …) | 00/*, 01/*, 17/* | n/a | 13 | |

### 3.16 *The ARRL Handbook for Radio Communications* (96th ed., 2019; chapter structure unchanged in later editions)
ToC source: arrl.org product page "ARRL Handbook 2019" (Table of Contents block, raw HTML); the 2024+ reference
page (arrl.org/arrl-handbook-reference) confirms the same chapter numbering for ch. 2, 3, 14, 17, 19–21.
Chapter level. Operating-practice chapters are n/a.

| Ch | Chapter | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1 | What is amateur (ham) radio? | 19/amateur-radio-licensing | covered | 1 | |
| 2 | Electrical fundamentals | 01/*, 00/* | covered | 1 | |
| 3 | Radio fundamentals | 00/decibels…, 02/wave-equation…, 19/spectrum-allocation… | covered | 1 | |
| 4 | Circuits and components | 04/*, 05/* | covered | 1 | |
| 5 | RF techniques (parasitics, Q, matching, RF construction practice) | 04/*, 01/resonance-and-q, 13/rf-layout-rules | covered | 1 | |
| 6 | Computer-aided circuit design | 16/spice-circuit-simulation, 16/rf-circuit-simulators-harmonic-balance, 16/tool-landscape-overview | covered | 1 | |
| 7 | Power sources | 05/power-supplies-for-rf-and-analog | covered | 1 | |
| 8 | DSP and SDR fundamentals | 14/* | covered | 1 | |
| 9 | Oscillators and synthesizers | 05/oscillators, 06/vco-and-pll-synthesizers | covered | 1 | |
| 10 | Analog and digital filtering (incl. crystal ladder, helical resonator filters, diplexers) | 01/passive-filter…, 06/rf-filters…, 14/digital-filters…, 20/bandpass-filter-design-walkthrough | shallow | 1 | **crystal ladder (Cohn/min-loss) IF filters absent**; helical resonators 1 mention; diplexer design absent |
| 11 | Modulation | 10/* | covered | 1 | |
| 12 | Receiving (superhet, direct conversion, AGC, noise blankers, product detection) | 06/receiver-architectures, 07/* | shallow | 1 | AGC loop design, product detector/BFO, noise blanker absent |
| 13 | Transmitting | 06/transmitter-architectures | covered | 1 | |
| 14 | Transceiver design topics (T/R switching, sequencing, frequency planning) | 06/rf-switches…, 06/receiver-architectures | covered | 1 | |
| 15 | Digital protocols and modes (packet, APRS, FT8/WSPR, PSK31, digital voice) | 10/packet-framing-protocols, 14/software-demodulation, 10/analog-modulation… (APRS ex.) | shallow | 1 | APRS/AX.25 partly; weak-signal modes (FT8/WSPR ≈ −24 dB SNR in 2.5 kHz) absent — useful benchmark vs LoRa |
| 16 | Telemetry and navigation (APRS, GPS, balloon/rocket payloads) | 15/rocket-telemetry-radio-design, 20/lora-rocket-telemetry-link, 08/gnss-antennas | covered | 1 | GNSS navigation side waits for 21-gnss |
| 17 | RF power amplifiers (solid-state & tube, LDMOS, matching, cooling) | 06/power-amplifiers, 06/amplifier-stability-and-biasing | covered | 1 | PCB-level thermal now in 13/thermal-management-rf; heatsink sizing for 50–100 W amps absent |
| 18 | Repeaters (duplexers, cavity filters, desense) | 06/rf-filters… (cavity), 07/dynamic-range… | shallow | 1 | duplexer/notch-cavity design absent |
| 19 | Propagation of radio signals | 09/* | covered | 1 | |
| 20 | Transmission lines (incl. tuners, baluns, common-mode chokes) | 03/*, 08/antenna-matching-and-baluns | covered | 1 | **antenna tuners (ATU/transmatch topologies, losses) absent** |
| 21 | Antennas | 08/* | covered | 1 | HF wire antennas planned (08/wire-antennas-hf…) |
| 22 | Component data and references | 18/*, 04/* | covered | 1 | |
| 23 | Construction techniques (Manhattan/dead-bug, soldering, enclosures, PCB) | 13/rf-layout-rules, 18/sourcing-and-eval-boards | shallow | 1 | prototyping methods for RF (Manhattan, copper-clad, dead-bug) absent |
| 24 | Assembling a station | 15/ground-station-design | covered | 1 | |
| 25 | Test equipment and measurements | 17/* | covered | 1 | |
| 26 | Troubleshooting and maintenance | 17/rf-bring-up-debug-playbook | covered | 1 | |
| 27 | RF interference | 13/emc-emi-fundamentals, 13/shielding-and-isolation | shallow | 1 | RFI diagnosis (fundamental overload vs harmonics vs CM ingress) not as a procedure |
| 28 | Safety | 19/rf-exposure-safety, 19/lab-safety-esd-high-power | covered | 1 | |
| S1 | Space communications (satellites, Doppler, EME) | 15/rocket-telemetry-radio-design (Doppler) | missing | 1 | satellite pass geometry, Doppler correction, CubeSat links absent |
| S2–S5 | Digital communications; image communications; digital basics; station accessories | — | n/a | 4 | |

### 3.17 *The ARRL Antenna Book for Radio Communications*, 24th ed. (ARRL 2019)
ToC source: arrl.org product page "ARRL Antenna Book" (Contents block, raw HTML). Chapter level.

| Ch | Chapter | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| V1-1 | Antenna fundamentals | 08/antenna-fundamentals | covered | 1 | |
| V1-2 | Dipoles and monopoles | 08/dipoles-and-monopoles | covered | 1 | |
| V1-3 | The effects of ground (radials, ground systems, reflection) | 16/nec-antenna-modelling (ground models), 09/two-ray…, 08/dipoles… | covered | 1 | radial-field design for verticals brief |
| V1-4 | Radio-wave propagation | 09/* | covered | 1 | |
| V1-5 | Loop antennas | 08/loop-antennas | covered | 1 | |
| V1-6 | Multielement arrays (phased verticals, broadside/end-fire) | 12/array-factor…, 08/yagi-uda… | covered | 1 | phased-vertical feed systems (current forcing) absent |
| V1-7 | Antenna modelling | 08/antenna-simulation-nec-openems, 16/nec-antenna-modelling | covered | 1 | |
| V2-1–V2-2 | Single-band & multiband MF/HF antennas (traps, fan, OCF, EFHW) | 08/dipoles-and-monopoles (EFHW) | shallow | 2 | *planned* 08/wire-antennas-hf-random-wire-fan-dipole |
| V2-3 | HF Yagi and quad antennas | 08/yagi-uda-and-log-periodic | shallow | 1 | Yagi yes; cubical quad absent |
| V2-4 | Broadside and end-fire arrays (collinear, curtains, W8JK) | 12/array-factor… | shallow | 1 | collinear antennas (common 433/915 MHz base antenna) only 6 mentions in dipoles |
| V2-5 | Long-wire and travelling-wave antennas | — | missing | 1 | see Balanis 10.2 |
| V2-6 | HF antenna-system design | — | n/a | 1 | |
| V3-1 | VHF, UHF and microwave antennas | 08/yagi-uda…, 08/helical…, 08/horn-reflector…, 08/patch-antennas | covered | 1 | |
| V3-2 | VHF/UHF mobile and rover antennas | 08/dipoles… (loaded monopoles) | covered | 1 | |
| V3-3 | Antennas for space communications (CP Yagis, eggbeaters, helices, EME arrays) | 08/helical-antennas, 20/ground-station-tracking-yagi, 08/antenna-polarization… | covered | 1 | turnstile/eggbeater omni CP only briefly |
| V3-4 | VHF/UHF/microwave antenna systems (stacking, phasing harnesses, feeders) | 08/yagi-uda… (3 mentions of stacking), 15/ground-station-design | shallow | 1 | stacking distance & phasing-harness design absent |
| V3-5–V3-7 | Portable; stealth & limited-space; mobile & maritime HF | 08/small-antenna-limits | shallow | 3 | |
| V3-8 | Receiving and direction-finding antennas (Beverage, small loops, Adcock, Doppler DF) | 12/adaptive-beamforming-doa, 08/loop-antennas, 08/yagi-uda… (recovery DF Yagi) | shallow | 1 | array DoA covered; practical DF methods for rocket recovery (Yagi null-seeking, pseudo-Doppler, Watson–Watt) not consolidated |
| V4-1–V4-2 | Transmission lines; line-system techniques (stubs, baluns, chokes, switching) | 03/*, 08/antenna-matching-and-baluns | covered | 2 | |
| V4-3 | Antenna materials and construction | 20/ground-station-tracking-yagi, 08/yagi-uda… | shallow | 1 | weatherproofing/corrosion & connector sealing barely mentioned |
| V4-4 | Building antenna systems and towers (rotators) | 20/ground-station-tracking-yagi, 15/ground-station-design | covered | 1 | |
| V4-5 | Antenna & transmission-line measurements | 08/antenna-measurement, 17/nanovna-librevna-practical | covered | 1 | |
| V4-6 | Antenna-system troubleshooting | 17/rf-bring-up-debug-playbook, 03/time-domain-reflectometry | covered | 1 | |

### 3.18 Hayward, Campbell & Larkin, *Experimental Methods in RF Design* (ARRL 2003/2009)
ToC source: ARRL news release for the book (arrl.org/news/…, contents list, raw HTML). Chapter level.

| Ch | Chapter | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1 | Basic investigations in electronics | 01/*, 05/*, 17/lab-setup-by-budget | covered | 1 | |
| 2–5 | Amplifiers, filters, oscillators and mixers (feedback amps, LC filters, VFO/VXO, diode-ring mixers, diplexed mixer terminations) | 05/amplifier-topologies (50 Ω feedback amp), 01/passive-filter…, 05/oscillators, 06/mixers | covered | 4 | crystal-filter design & measurement of crystal motional parameters absent; VFO/VXO stability practice absent |
| 6 | Superheterodyne transmitters and receivers | 06/receiver-architectures, 06/transmitter-architectures, 07/receiver-cascade-analysis | covered | 1 | |
| 7 | Measurement equipment (return-loss bridges, step attenuators, power meters, homebrew spectrum analyser, noise sources) | 17/*, 06/detectors-and-power-meters | covered | 1 | homebuilt test gear (RL bridge, log-amp power meter) covered via parts; building a spectrum analyser absent |
| 8 | Direct-conversion receivers (AM detection, microphonics, LO radiation, audio gain distribution) | 06/receiver-architectures, 14/iq-complex-baseband | covered | 1 | analog (non-SDR) DC receiver practice shallow |
| 9 | Phasing receivers and transmitters (polyphase / allpass networks, opposite-sideband suppression) | 14/iq-complex-baseband, 10/analog-modulation… | shallow | 1 | analog phasing networks (RC polyphase, allpass pairs) one mention each |
| 10–11 | DSP components; DSP applications in communications | 14/* | covered | 2 | |
| 12 | Field operation, portable gear and integrated stations | 15/ground-station-design | n/a | 1 | |

### 3.19 Skolnik, *Introduction to Radar Systems*, 3rd ed. (McGraw-Hill 2001)
ToC source: the section-level catalogue ToC (GBV/hebis scan, gbv.de/dms/hebis-darmstadt/toc/195384067.pdf) returned
HTTP 429 to both curl and WebFetch on 2026-09-29 and again on 2026-10-02; chapter scopes are taken from the book's
own preface as indexed by the search engine (chapter numbers 1–11 confirmed; ch. 2 opening sections 2.1–2.4
seen in the catalogue snippet). **Chapter level, medium confidence on titles** — re-verify when GBV allows.

| Ch | Chapter (scope) | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1 | Introduction to radar (basics, bands, applications) | 11/radar-range-equation, 19/spectrum-allocation… (radar bands) | covered | 1 | |
| 2 | The radar equation (noise, Pd/Pfa, integration, RCS & fluctuations, PRF, losses) | 11/radar-range-equation, 11/detection-theory-cfar, 11/radar-cross-section | covered | 1 | |
| 3 | MTI and pulse-Doppler radar | 11/clutter-and-mti, 11/cw-and-doppler-radar | covered | 1 | pulse-Doppler PRF regimes (low/medium/high) only 4 mentions |
| 4 | Tracking radar (monopulse, conical scan, sequential lobing, track-while-scan, α-β/Kalman) | — | missing | 1 | **no tracking-radar content at all** (also Richards ch. 7, Mailloux 1.1.6) |
| 5 | Detection of signals in noise (matched filter, detectors, integrators, automatic detection, CFAR) | 10/matched-filter-detection, 11/detection-theory-cfar | covered | 1 | |
| 6 | Information from radar signals (accuracy, ambiguity diagram, pulse compression, target recognition) | 11/ambiguity-function-waveforms, 11/pulsed-radar-and-pulse-compression, 11/cw-and-doppler-radar (micro-Doppler) | covered | 1 | angle accuracy absent |
| 7 | Radar clutter (surface-clutter equation, land/sea/weather clutter, detection in clutter) | 11/clutter-and-mti | covered | 1 | σ⁰ models & sea-state tables thin |
| 8 | Propagation of radar waves (flat-earth multipath, curvature, refraction & ducting, diffraction, attenuation) | 09/two-ray…, 09/fresnel-zones-los-radio-horizon (4/3 earth), 09/diffraction…, 09/atmospheric-rain-attenuation, 11/radar-range-equation (propagation factor) | covered | 1 | ducting/anomalous propagation brief |
| 9 | The radar antenna (reflectors, phased arrays, radomes, sidelobes) | 08/horn-reflector…, 12/*, 02/boundary-conditions… (radome walls) | covered | 1 | |
| 10 | Radar transmitters (magnetron, klystron, TWT, solid-state, modulators) | 06/power-amplifiers (solid-state) | shallow | 1 | tubes & pulse modulators absent (relevant to surplus-magnetron DIY radar) |
| 11 | Radar receivers (NF, mixers, duplexers & receiver protectors, displays) | 07/noise-figure-and-friis, 06/mixers, 06/rf-switches-attenuators-limiters, 06/circulators-isolators (Ex. 2) | covered | 1 | |

### 3.20 MIT 6.013 *Electromagnetics and Applications* (Staelin, Spring 2009, OCW)
Source: OCW calendar page (lecture L / recitation R topics, raw HTML). Grouped by unit.

| Sessions | Topics | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| L1–L4, R1–R5 | Foundations: Gauss/Ampère, media & BCs, Maxwell, UPW, polarisation, Poynting; R/L/C from fields | 02/maxwells-equations, 02/wave-equation…, 02/poynting…, 02/inductance-capacitance-from-fields | covered | 9 | |
| L5–L6, R6–R7 | Forces, motors, generators, MEMS | — | n/a | 4 | |
| L7 | Laplace's equation, separation of variables | 00/differential-equations-circuits-waves (L3) | covered | 1 | |
| L8 | Fields in media: uniaxial media, quarter-wave plate | 02/dielectrics… (anisotropy), 02/wave-equation… | shallow | 1 | anisotropic propagation (birefringence) not derived |
| R9, L9–L10, R11–R12 | Lossy media, skin depth, plasmas; oblique incidence, TE/TM, Brewster; vp/vg | 02/skin-effect…, 09/ionospheric-hf-propagation (plasma), 02/boundary-conditions… | covered | 5 | |
| L11–L12, R13–R14 | TEM lines, telegrapher, transients (graphical, L/C/diode loads), lossy TEM | 03/telegrapher…, 03/time-domain-reflectometry | covered | 4 | non-linear (diode) load transients absent |
| L13–L16, R15–R18 | Γ(z), Smith chart, stub tuning; RLC & TEM resonators, Q_L/Q_I/Q_E, coupling; parallel-plate & rectangular guides; cavities & perturbation | 03/smith-chart, 03/impedance-matching…, 01/resonance-and-q, 02/waveguides… | covered | 8 | resonator coupling (Q_E, critical coupling) and cavity perturbation shallow/missing (see Pozar 6.6–6.7) |
| L17–L20, R19–R24 | Antenna gain, A_e, R_r, RF links, radar; radiation from currents; Hertzian dipole; receiving antennas; arrays & mirrors; aperture antennas; thermal noise, radio astronomy, remote sensing | 08/antenna-fundamentals, 09/friis…, 02/radiation-from-currents…, 12/array-factor…, 08/horn-reflector… | covered | 10 | radio-astronomy / remote-sensing (radiometry) applications missing |
| L21–L24, R25–R27 | Optical fibres, lasers, optical resonators; acoustics | — | n/a | 7 | |

### 3.21 MIT 6.776 *High Speed Communication Circuits* (Lee & Perrott, Spring 2005, OCW)
Source: OCW lecture-notes page (raw HTML).

| Lec | Topic | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 1–2 | Communication-system overview; transceiver architectures | 06/receiver-architectures, 06/transmitter-architectures | covered | 2 | |
| 3–5 | Waveguides & lines; S-parameters & impedance transformers; generalised Γ, Smith chart | 02/waveguides…, 03/* | covered | 3 | |
| 6–9 | MOS & passives; gain-bandwidth; broadband amplifiers & enhancement (shunt peaking, distributed); narrowband amplifiers | 05/fets…, 05/amplifier-topologies | shallow | 4 | bandwidth-extension techniques missing (see Lee ch. 9) |
| 10–13 | Amplifier noise modelling; NF & nonlinearity; LNAs; LNA examples | 07/*, 06/lna-design | covered | 4 | |
| 14–15, 17 | VCOs; VCO examples; VCO noise | 05/oscillators, 07/phase-noise-and-jitter | shallow | 3 | VCO noise via ISF only cited |
| 15–16 | Mixers | 06/mixers | covered | 2 | |
| 18–20 | PA basics; other classes & PA modulation; linearisation & adaptive bias | 06/power-amplifiers | shallow | 3 | feed-forward/Cartesian/adaptive bias missing (see Razavi 12.6) |
| 21–23 | PLLs & integer-N; noise in integer-/fractional-N; fractional-N design & bandwidth extension | 06/vco-and-pll-synthesizers | covered | 3 | |
| 24–25 | Advanced topics; transceiver design example | 06/receiver-architectures | covered | 2 | |

### 3.22 MIT Lincoln Laboratory *Introduction to Radar Systems* (O'Donnell, OCW RES.LL-001) and *Build a Small Radar System* (Charvat et al., OCW RES.LL-003)
Source: OCW course pages; the 10-lecture agenda via the search index of MIT LL's lecture PDFs (ll.mit.edu is
Cloudflare-challenged); RES.LL-003 course description (raw HTML).

| Item | Topic | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| LL-001 L1–L2 | Introduction; radar equation | 11/radar-range-equation | covered | 2 | |
| L3 | Propagation effects (attenuation, multipath, ducting) | 09/*, 11/radar-range-equation (propagation factor) | covered | 1 | |
| L4 | Target RCS | 11/radar-cross-section | covered | 1 | |
| L5 | Detection of signals in noise & pulse compression | 11/detection-theory-cfar, 11/pulsed-radar… | covered | 1 | |
| L6 | Radar antennas | 08/horn-reflector…, 12/* | covered | 1 | |
| L7 | Radar clutter and chaff | 11/clutter-and-mti | shallow | 1 | chaff absent |
| L8 | Signal processing: MTI & pulse Doppler | 11/clutter-and-mti | covered | 1 | |
| L9 | Tracking & parameter estimation (sequential lobing, monopulse, trackers) | — | missing | 1 | see Skolnik ch. 4 |
| L10 | Transmitters & receivers | 06/power-amplifiers, 07/*, 11/diy-radar-hardware | covered | 1 | tube transmitters absent |
| LL-003 | Build a coffee-can-style radar: Doppler, ranging (FMCW), SAR imaging | 11/diy-radar-hardware, 11/fmcw-radar, 11/sar-and-imaging | covered | 1 | 20-projects/fmcw-radar-build planned |

### 3.23 Stanford EE359, EE252, EE133 (EE314 not accessible)
Sources: EE359 Winter 2020 lecture page (web.stanford.edu/class/ee359/lectures.html); EE252 course page (bulletin
summary); EE133 course description (search index of the course-info PDF); EE314 web directory is empty and
explorecourses requires login.

| Item | Topic | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| EE359 L1–L3 | Intro; path-loss models; mmWave propagation, shadowing | 09/friis…, 09/empirical-path-loss-models, 09/atmospheric-rain-attenuation | covered | 3 | |
| L4–L6 | Statistical fading; narrowband/wideband models; Doppler & delay spread | 09/multipath-fading-doppler | covered | 3 | |
| L7–L8 | Shannon capacity; capacity of flat & frequency-selective fading channels | 10/ber-ebn0-and-shannon | shallow | 2 | fading-channel capacity (CSI at TX/RX, water-filling) missing |
| L9–L10 | Linear modulation in AWGN & fading; average error & outage; Doppler impact | 10/digital-modulation…, 09/multipath-fading-doppler | shallow | 2 | average Pe in fading not derived |
| L11–L12 | Diversity, MRC; transmit diversity | 09/multipath-fading-doppler (L3) | covered | 2 | Alamouti/transmit diversity missing |
| L13–L14 | Adaptive modulation (variable-rate MQAM) | — | missing | 2 | LoRa ADR-like SF adaptation is the reader's analogue |
| L14–L17 | MIMO capacity, beamforming, diversity–multiplexing trade-off; MIMO decoding; OFDM & MIMO-OFDM | 00/matrices… (SVD capacity), 10/ofdm | shallow | 4 | no MIMO comms page |
| L18–L19 | Spread spectrum; multiuser (MUD, random access, cellular design) | 10/spread-spectrum… | shallow | 2 | random access / cellular design missing |
| L20 | Summary & advanced topics | — | n/a | 1 | |
| EE252 | Antenna parameters; dipoles, loops, reflectors, Yagis, helices, slots, horns, microstrip; measurements; Friis/radar; feeds, matching, baluns, broadbanding; arrays | 08/*, 12/* | covered | 6 | |
| EE252 | Aperture synthesis, interferometry, VLBI; thermal radiation, antenna temperature, passive microwave remote sensing | 07/thermal-noise… (antenna temperature) | missing | 2 | interferometry/aperture synthesis and radiometry absent |
| EE133 | AM (multiplier) & FM (VCO, PLL) modulation/demodulation, SDR concepts; capstone 24 MHz FM two-way radio | 10/analog-modulation…, 06/vco-and-pll…, 14/* | covered | 3 | no complete "build a simple FM transceiver" recipe in 20-projects plan |

### 3.24 Berkeley EE142 / EE242A *Integrated Circuits for Communications* (Niknejad); EE117 (not accessible)
Source: EECS catalogue descriptions (via search index; www2.eecs.berkeley.edu refused connections from this
host on 2026-10-02).

| Item | Topic | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| 142/242A | Tuned & feedback HF amplifiers, matching, optimal gain/matching via two-port theory | 06/lna-design, 06/amplifier-stability…, 05/amplifier-topologies | covered | 1 | |
| 142/242A | Distortion: harmonic, IM, cross-modulation, effect of feedback on distortion | 07/nonlinearity… | shallow | 1 | effect of feedback on distortion not derived |
| 142/242A | Noise analysis | 07/* | covered | 1 | |
| 142/242A | PAs: classes A/B/AB/C and IC realisations | 06/power-amplifiers | covered | 1 | |
| 142/242A | Mixers: BJT/FET/IC, conversion gain, spurious response | 06/mixers (spur chart) | covered | 1 | |
| 142/242A | Oscillators: amplitude & frequency stability | 05/oscillators | covered | 1 | |
| 142/242A | Analog multipliers and PLLs | 06/mixers (Gilbert), 06/vco-and-pll… | covered | 1 | |
| EE117 | EM fields and waves (catalogue unreachable) | 02/*, 03/* | n/a | 1 | not counted |

### 3.25 Georgia Tech ECE 6360 *Microwave Design* (Spring 2023 syllabus) and ECE 6361 *Microwave Design Lab*
Source: official ECE6360 syllabus PDF (sites.gatech.edu), ECE 6361 catalogue description.

| Item | Topic | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| wk 1–9 | Radio systems; HFSS/ADS; plane waves; lines; metallic waveguides; microstrip/stripline/CPW/slotline; networks; Smith chart & matching; multisection & tapers | 02/*, 03/*, 16/tool-landscape-overview | covered | 9 | slotline shallow |
| wk 7 | Transitions | 13/connectors-and-launches, 18/connectors-and-cables-parts | covered | 1 | landed during this check |
| wk 10–12 | T-junctions, dividers, couplers, resonators & filters | 06/couplers…, 06/rf-filters… | covered | 3 | |
| wk 12–13 | mmWave & emerging technologies | 18/phased-array-and-radar-parts, 11/diy-radar-hardware | shallow | 1 | mmWave packaging/AiP, on-glass/LTCC not treated |
| wk 13–14 | Microwave measurements; beamforming networks | 17/*, 12/beamforming-architectures | covered | 2 | |
| ECE 6361 | Passive & active microwave design/measurement with CAD and VNAs | 16/*, 17/vna-fundamentals-calibration | covered | 1 | |

### 3.26 Caltech EE 153 *Microwave Circuits and Antennas*
Source: Caltech EE course page/catalogue description (via search index).

| Item | Topic | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| lectures | Lines, Z0, max power transfer, matching, SFGs, dividers, coupled lines & even/odd analysis, couplers, filters, noise, amplifiers, oscillators, mixers, antennas | 03/*, 01/network-theorems…, 06/*, 07/*, 08/* | covered | 13 | |
| lab | Design/fab/measure microstrip filters, dividers, couplers, LNAs, oscillators (Microwave Office) | 06/*, 16/* (open tools), 20/* (planned walkthroughs) | covered | 1 | commercial-CAD workflow replaced by open tools in the KB |

### 3.27 TU Delft (EE4620, EE4675, ET4169/ET4175, EE4565) and ETH Zürich (227-0110/0111/0112)
Sources: TU Delft course pages via search index (microelectronics.tudelft.nl failed TLS verification from this host);
ETH course titles via search index (vvz.ethz.ch not fetched). Descriptions only.

| Item | Topic | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| EE4620 | Green's functions of stratified media; dominant spectral contributions & far field | 00/numerical-methods-overview, 16/em-solvers… | missing | 2 | spectral-domain Green's functions (Sommerfeld integrals) absent — the theory behind planar MoM solvers |
| EE4620 | Surface waves & leaky waves | 08/patch-antennas, 12/planar-arrays… | shallow | 1 | leaky-wave antennas one mention |
| EE4620 | Artificial dielectrics; spectral representation of planar lines; connected arrays | 12/planar-arrays… (tightly-coupled mention) | missing | 3 | |
| EE4675 | Radar object classification: micro-Doppler, ML on radar data | 11/cw-and-doppler-radar (micro-Doppler) | shallow | 1 | ML classification absent |
| ET4169/ET4175 | Radar I/II: principles → theory & system design | 11/* | covered | 2 | |
| EE4565 | Propagation & scattering of EM waves | 09/*, 11/radar-cross-section | covered | 1 | |
| ETH 227-0110 | EM waves: materials, effects, antennas | 02/*, 08/* | covered | 1 | |
| ETH 227-0111 (I/II) | Radio-frequency electronics I & II | 06/*, 07/* | covered | 2 | titles only |
| ETH 227-0112 | High-speed signal propagation | 03/*, 13/* | covered | 1 | SI-specific crosstalk/termination gaps as in Bogatin |

### 3.28 MOOCs and vendor curricula
Sources: Coursera course pages via search index (TU/e *Microwave Engineering and Antennas*; *RF and mm-Wave
Circuit Design*; *RF/Microwave Design* series), Keysight *RF & Microwave Fundamentals eLearning* overview
(5992-1584), Rohde & Schwarz Technology Academy pages.

| Item | Topic | KB page(s) | Status | n | Note |
|---|---|---|---|---|---|
| TU/e Coursera | Applications & trends; passive circuits (lines, matching, combiners, filters); antenna theory, range, phased arrays; active front-end circuits | 03/*, 06/*, 08/*, 12/* | covered | 4 | |
| Coursera RF & mm-wave | System specs → LNA, PA, mixers, oscillators, PLL synthesisers | 07/receiver-cascade…, 06/* | covered | 1 | |
| Coursera RF/MW design (ADS, antenna design) | Commercial-tool workflows (ADS/EM co-simulation) | 16/tool-landscape-overview, 16/openems-workflow | covered | 2 | |
| Keysight eLearning | Cable & connector care; line fundamentals; spectrum, network, signal-generation, power-measurement fundamentals | 18/connectors-and-cables-parts, 03/*, 17/* | covered | 6 | connector torque/care practice brief |
| R&S Technology Academy | RF basics, measurements, modulation | 17/*, 10/* | covered | 1 | |

## 4. Level check — does the KB serve both a beginner and a graduate student?

**Structure is right.** All but five of 229 pages carry "Intuition (no math)" plus Level 1/2/3 maths, and
`00-math-foundations/math-roadmap-for-rf` gives a staged learning path. Front-matter levels: 180 mixed,
29 intermediate, 18 intro, 2 advanced.

**Beginner (high-school maths) — partly served.**
- Foundation pages (00, 01, 03, 04) really do start with algebra in Level 1 (decibels, phasors, L-match,
  reactance tables).
- In the advanced domains, "Level 1" means *summary of results*, not *beginner*. The Level 1 sections of
  11/ambiguity-function, 12/adaptive-beamforming-doa, 03/broadband-matching-bode-fano and 14/digital-filters
  open with integrals, Hermitian matrices or H(z). There a beginner gets only the Intuition section, so the
  rung between "intuition" and "integral" is missing.
- There is no Level-0 project rung: 20-projects has 3 of 10 pages, and none is a "first radio". AoE 1.8,
  Razavi 4.4 and Stanford EE133 all teach through a simple receiver (top-50 #24). There is no GLOSSARY.md
  (deferred to Wave 6).

**Graduate student — well served in noise/cascades, matching, arrays, radar detection, sampling/multirate.
In those areas Level 3 derives and verifies. The ladder breaks where Level 3 *names* the graduate method
without deriving it:**

| Domain | Rung present | Broken rung (what a graduate course expects next) |
|---|---|---|
| DSP (14) | Laplace (00) → FIR/IIR by H(z) | **z-transform never derived**; IIR design uses H(z) without it (#12) |
| Oscillators (05/07) | Barkhausen → Leeson (L2) | **ISF/LTV phase noise cited only** (#18) |
| EM/antennas (02/08) | Hertzian dipole, A-potential (L2) | **Green's function / equivalence / reciprocity not derived**; aperture, slot and horn L3 rest on stated results (#21) |
| Estimation (10/11/12/21) | detection (NP, CFAR), CRB for DOA and timing | **no estimation→tracking rung**: Kalman, α-β, monopulse absent (#1, #2) |
| Comms (10) | AWGN BER, Shannon, OFDM | fading BER/capacity, MIMO, information theory only touched (#16, #17, #46) |
| Arrays (12) | AF, tapers (Taylor verified) | synthesis methods are one-liners (#4); conformal arrays absent (#8) |
| Nonlinearity (07/06) | power-series IP3, DPD sim | Volterra / memory theory absent (#23) |
| Filters (01/06) | prototypes, inverters, coupling-matrix analysis | synthesis of the coupling matrix from polynomials absent (#27) |
| Mixers (06) | switching mixer, SSB/DSB NF | LPTV / noise-folding analysis absent (#40) |
| GNSS (21) | signals, acquisition/tracking, rocket dynamics | coordinates, orbits, DOP/UERE, RTK/PPP still planned (#13) |

**Recommendation.** Add a "Level 1½" sentence-and-algebra rung to the Level 1 of every advanced-domain page.
Write the ten "broken rung" items as Level-3 extensions of the existing pages; most do not need new pages.
Add one beginner project page (#24).

## 5. Access notes and by-products

- **Not reachable / not used:** Skolnik section-level ToC (GBV catalogue HTTP 429 on 2026-09-29 and 2026-10-02);
  artechhouse.com, ll.mit.edu, O'Reilly, VitalSource, AccessEngineering, ebooks.com (Cloudflare challenge or HTTP 403);
  Stanford explorecourses (login) and the empty EE314 directory; Berkeley www2.eecs (connection refused);
  TU Delft department site (TLS verification failure). No Cloudflare challenge was bypassed. Pirate PDF hosts
  returned by search were ignored.
- **"6.S02"** did not resolve to a radar course; MIT's radar material was taken from OCW RES.LL-001 and RES.LL-003.
- **Open textbooks worth citing in Wave 5** (seen in the GaTech ECE6360 syllabus): M. Steer, *Microwave and RF Design*,
  3rd ed., NC State open access (5 volumes); R. Collin, *Foundations of Microwave Engineering* (IEEE Xplore);
  K. Sarabandi, *Foundations of Electromagnetics* (Michigan Publishing, open). Also MIT LL's `mit-ll/radar-intro`
  interactive lectures on GitHub.
- **Re-check trigger:** when 21-gnss reaches 8/8 and 20-projects ≥ 8/10, re-score tables 3.8, 3.16–3.18 and #13, #24.
