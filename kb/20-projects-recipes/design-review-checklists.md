---
title: Recipe — RF design-review checklists (schematic, layout, bring-up, pre-flight) for Space Bar radios, GNSS and ground stations
domain: 20-projects-recipes
slug: design-review-checklists
tags: [recipe, checklist, design-review, rf-schematic-review, rf-layout-review, bring-up, pre-flight, frequency-plan, harmonics, antenna-match, range-test, gnss-coexistence, regulatory, evidence, severity, pre-registration]
prerequisites:
  - lora-rocket-telemetry-link.md
  - ../13-pcb-rf-layout-emc/rf-pcb-review-checklist.md
  - ../17-test-measurement/rf-bring-up-debug-playbook.md
related:
  - ../13-pcb-rf-layout-emc/rf-layout-rules.md
  - ../19-regulations-safety/singapore-imda-rules.md
  - ../19-regulations-safety/international-rules-for-competitions.md
  - ground-station-tracking-yagi.md
  - bandpass-filter-design-walkthrough.md
  - gnss-front-end-design.md
  - lna-design-walkthrough.md
  - sdr-receiver-build.md
level: intermediate
confidence: medium
last_updated: 2026-10-02
---

# Recipe — RF design-review checklists for Space Bar radios

Four checklists that turn the recipes of this domain into go/no-go reviews: **RF schematic**, **RF layout**,
**bring-up** and **pre-flight RF**. Each item has an ID (keep it forever, never renumber), a severity
(**FB** flight-blocking / **H** high / **M** medium / **L** low), a pass criterion fixed *before* the review,
and the page that justifies it. The detailed layout review lives in [RF PCB review checklist](../13-pcb-rf-layout-emc/rf-pcb-review-checklist.md)
and the debug flow in [RF bring-up & debug playbook](../17-test-measurement/rf-bring-up-debug-playbook.md);
this page adds the project-specific items found while building the recipes. Automated part:
`python3 tools/verify/proj_preflight_rf.py [config.json]` checks band edges, e.r.p., duty, Doppler rate,
GNSS harmonics, harmonic-vs-second-link and **fails on missing evidence**.

## Questions this page answers
- What should an RF schematic review of a flight computer check?
- What layout mistakes make a LoRa or GNSS board fail?
- In what order should I bring up a new RF board, and what must each step show?
- What must be measured and on file before a rocket with two radios and GNSS flies?
- How do I check the frequency plan against other teams and the venue's rules?
- How do I record review findings so they are not lost or re-argued?

## TL;DR
- **Review in four gates**: schematic (before layout) → layout (before ordering) → bring-up (before integration) → pre-flight (before every campaign). Each gate has flight-blocking items; a gate passes only when every FB item is closed with evidence.
- **The ten items that caught the most problems while writing these recipes**: (1) channel *edges* inside the band (433.125 MHz at 250 kHz is outside Singapore's 433.05 MHz edge); (2) primary's 2nd harmonic vs the secondary's channel (433.125 → CH18, 434.125 → CH17, never CH16); (3) E22 CH 0–9 put 3f in or beside GPS/GLONASS L2 (use CH 24); (4) EBYTE air-rate → SF/BW identified by SDR before flight (the default "2.4k" behaves like SF9/125 and fails boost Doppler at 900 MHz); (5) e.r.p. includes antenna *peak* gain; (6) TX-side filter rejection at 1.5 GHz for GNSS coexistence (PA wideband noise); (7) SAW-first vs LNA-first decided from *measured* antenna coupling; (8) installed S11 in the closed airframe; (9) ground-station gain staging (one 8-bit SDR clips at ≈ −71 dBm); (10) a convergence check on any simulated high-Q structure (the patch moved 30 MHz between meshes).
- **Evidence rule** (team tenet): a check without its measurement file or plot is a FAIL, not a "probably fine". The pre-flight tool prints FAIL for every missing evidence item.
- **Findings**: give each a stable ID, severity, owner and disposition (open / fixed / waived-with-reason / superseded), keep an "everything still open" list at the top, and append corrections rather than editing history.

## Intuition (no math)
Checklists exist because experts forget the obvious under time pressure. RF failures are rarely exotic: a wrong channel number, a missing ground via, an antenna detuned by the nose cone, a module left on its default settings, a test done with the transmitter into a dummy load so the real coupling path was never exercised. A good checklist is short enough to actually use, ties every item to a reason (so it is not skipped as "bureaucracy") and demands evidence, so that "we checked" means "here is the plot".

## The math — the quantities the checklists test
### Level 1 — the arithmetic behind the frequency-plan items
- Channel inside band: $f_c - BW/2 \ge f_{lo}$ and $f_c + BW/2 \le f_{hi}$ (433.05–434.79 MHz holds 250 kHz channels centred 433.175–434.665 MHz).
- e.r.p. $= P_{cond} - L_{feed} + G_{peak} - 2.15$ dB; e.i.r.p. = e.r.p. + 2.15 dB ([IMDA](../19-regulations-safety/singapore-imda-rules.md)).
- Occupancy $\sum f_i T_{oa}(L_i) \le \min(0.7, d_{legal})$ ([telemetry recipe](lora-rocket-telemetry-link.md)).
- Doppler drift per packet $a_r f_c T_{oa}/c \le \tfrac12\,BW/(3\cdot2^{SF})$ (×16 with LDRO) ([impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)).
- Harmonics $n f_c$ (n = 2…5) outside every tracked GNSS band and ≥ 1.5 BW from the other link's channel.

### Level 2 — budgets the reviewer recomputes
Link margin (kT0 = −174 dBm/Hz, FSPL 32.45 + 20 log f_MHz + 20 log d_km), cascade NF, blocking isolation, TX-noise desense, filter rejection — each recipe's script recomputes them: `proj_lora_link.py`, `proj_ground_station.py`, `proj_harmonic_filter.py`, `proj_gnss_frontend.py`, `proj_lna_gnss.py`, `proj_sdr_receiver.py`.

### Level 3 — what a checklist cannot do
It cannot replace measurement of coupled, installed systems (airframe coupling, detuning, harmonics into the real antenna) nor tell you about unknown unknowns — hence the pre-flight evidence items and post-flight analysis.

## Design equations & rules of thumb
| Rule | Value |
|---|---|
| Spurious limit → dBc | $P_{out}$ + 36 dB (< 1 GHz), + 30 dB (≥ 1 GHz) (Singapore TS SRD) |
| Near-pad receiver protection | ≥ 100 m, or 20–30 dB pad, from a 2 W transmitter |
| Antenna separation (LoRa ↔ GNSS) | as far as possible; measure S21; ≥ 48 dB isolation needed for a MAX-M10S vs 2 W |
| Battery power-up trials | ≥ 22/22 clean before flight (team bring-up practice) |
| Evidence | file name + date + config line for every measurement |

## Worked examples

### Checklist 1 — RF schematic review (gate S, before layout)
| ID | Sev | Check | Pass criterion | Why / page |
|---|---|---|---|---|
| S-01 | FB | Frequency plan written down: every TX/RX, channel, BW, power, venue | table exists; `proj_preflight_rf.py` R1/R5 PASS | [telemetry](lora-rocket-telemetry-link.md) |
| S-02 | FB | Module variant and firmware named exactly (E22-400T33D vs T30D vs M33S) in BOM and schematic | matches the purchase record | Avionics B documentation-drift lesson |
| S-03 | H | Radio supply: regulator ≥ 1.5–2× burst current (E22 1.2 A), bulk low-ESR C at the module, ≥ 5 V for E220-T30D | calculation attached | [modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md) |
| S-04 | H | Mode/AUX pins of UART modules to MCU GPIOs (not only jumpers) | M0/M1/AUX routed | recover misconfigured modules |
| S-05 | FB | Harmonic LPF (or footprint) after every ≥ 20 dBm PA | footprint present; rejection target from `proj_harmonic_filter.py` | [filter recipe](bandpass-filter-design-walkthrough.md) |
| S-06 | H | π-match footprint (0 Ω + 2 DNP) at every antenna port | present | in-situ tuning |
| S-07 | FB | GNSS front end: SAW-first or LNA-first decision recorded with the coupling assumption; ESD at exposed antenna inputs; bias-tee for active antennas with DC block | decision + reason in the review log | [GNSS front end](gnss-front-end-design.md), [LNA](lna-design-walkthrough.md) |
| S-08 | H | GNSS I²C Fast-mode compliant (pull-ups, rise time) or UART; no 100 kHz assumption | per [u-blox integration](../21-gnss/gnss-receiver-integration-u-blox.md) | Avionics B lesson |
| S-09 | M | Crystal vs TCXO for SX126x at > +20 dBm or packets > 0.5 s | TCXO or documented reason | [impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md) |
| S-10 | M | Clock frequencies checked against GNSS bands (25 MHz × 63, 40 MHz × 39, 24 MHz × 65) | table from `gnss_self_interference.py` | [GNSS interference](../21-gnss/gnss-interference-jamming-spoofing.md) |
| S-11 | FB | Pyro wiring vs transmitter: no pyro line routed near antenna feeds; filtering on pyro gate lines | reviewed | [antennas on rockets](../08-antennas/antennas-on-rockets.md) |
| S-12 | M | Test points: RF test port / U.FL switch connector or coupon for conducted tests | present | bring-up |

### Checklist 2 — RF layout review (gate L, before ordering) — project items on top of [13's checklist](../13-pcb-rf-layout-emc/rf-pcb-review-checklist.md)
| ID | Sev | Check | Pass criterion | Why / page |
|---|---|---|---|---|
| L-01 | FB | Stackup in the KiCad file = the ordered JLC stackup; 50 Ω widths from that stackup and mask choice | screenshot of both | [stackups](../13-pcb-rf-layout-emc/stackups-and-materials.md) |
| L-02 | FB | RF path on top over unbroken L2 ground, no plane gaps, matching parts at the pins with own vias | visual + DRC | [RF layout rules](../13-pcb-rf-layout-emc/rf-layout-rules.md) |
| L-03 | H | Harmonic filter: parts in line, input/output ≥ 3 mm apart, trap inductors at 90°, two vias per shunt cap (4-layer) | as [filter recipe](bandpass-filter-design-walkthrough.md) layout notes | far-stop-band collapse |
| L-04 | H | LNA chain: input and output ≥ 20 mm apart or shielded for ≥ 30 dB gain; source/ground vias at the device | per [LNA recipe](lna-design-walkthrough.md) | oscillation |
| L-05 | H | LoRa module/PA and GNSS RF input at opposite board ends; shield-can footprints | distance recorded | coexistence |
| L-06 | M | Crystal/TCXO away from PA and module heat; copper void per Semtech guidance | reviewed | drift |
| L-07 | M | Antenna keep-outs for any PCB/chip antenna; module antennas at the edge | reviewed | [PCB antennas](../08-antennas/pcb-and-chip-antennas.md) |
| L-08 | M | Stitching/fences at ≤ λ/20 of the highest relevant frequency (GNSS LNA gain to ≈ 2 GHz → ≤ 7 mm) | reviewed | [vias & stitching](../13-pcb-rf-layout-emc/vias-stitching-fencing.md) |
| L-09 | L | Silkscreen: RF connector names, channel/power default, board ID | present | field use |
| L-10 | H | Simulated structures (patch, filters) converged: two meshes agree (≤ 0.3 % in frequency) with edge-locked meshing | log from openEMS | [patch recipe](patch-antenna-design-walkthrough.md) mesh trap |

### Checklist 3 — bring-up (gate B, per board) — order from the [playbook](../17-test-measurement/rf-bring-up-debug-playbook.md)
| ID | Sev | Check | Pass criterion | Page |
|---|---|---|---|---|
| B-01 | FB | Pre-registered expectations file committed before power-on | file hash in the log | ethos |
| B-02 | FB | Current-limited first power-up; rails within ±5 %; burst droop < 5 % during TX | scope captures | [telemetry T5](lora-rocket-telemetry-link.md) |
| B-03 | FB | Conducted TX into ≥ 40 dB (first pad ≥ 5 W): power ±1 dB of setting; frequency error; OBW; harmonics vs limits with the SA distortion check | plots on file | [spectrum analyzers](../17-test-measurement/spectrum-analyzers.md) |
| B-04 | H | EBYTE air-rate mapping recorded (SDR) | SF/BW/CR per code | [SDR recipe](sdr-receiver-build.md) |
| B-05 | H | Conducted/radiated sensitivity (attenuator method), leakage check with 50 Ω load | PER 1 % level within ±2 dB of prediction | [telemetry §7](lora-rocket-telemetry-link.md) |
| B-06 | FB | Installed antenna S11 in the closed airframe with battery and harness | ≤ −10 dB on channel; trims recorded | [NanoVNA](../17-test-measurement/nanovna-librevna-practical.md) |
| B-07 | FB | Self-interference: GNSS C/N0 with each TX keyed at flight schedule, one at a time | drop ≤ 3 dB | [GNSS front end G-T4](gnss-front-end-design.md) |
| B-08 | H | Ground chain: NF (Y-factor), noise-rise gain setting of each SDR, clip level | within prediction tolerances | [ground station](ground-station-tracking-yagi.md), [SDR](sdr-receiver-build.md) |
| B-09 | FB | 22/22 battery power-ups with radios and GNSS functional; boot CONFIG line logged each time | 22/22 | HIL/bench practice |
| B-10 | M | Thermal soak at flight duty (module can, filter inductors) | ΔT within limits | [filter H5](bandpass-filter-design-walkthrough.md) |

### Checklist 4 — pre-flight RF (gate F, every campaign)
| ID | Sev | Check | Pass criterion | Page |
|---|---|---|---|---|
| F-01 | FB | `proj_preflight_rf.py` with the campaign config | OVERALL PASS (or each FAIL waived in writing with reason) | this page |
| F-02 | FB | Venue frequency plan: assigned frequencies from the competition / IMDA permit / amateur consent; other teams' channels collected | no co-channel or harmonic overlap with neighbours ≤ 10 km | [competitions](../19-regulations-safety/international-rules-for-competitions.md) |
| F-03 | FB | Licences/permits on site (amateur licence + IMDA consent letter, temporary permit, competition approval); callsign in packets if amateur; encryption off | documents in the station box | [IMDA](../19-regulations-safety/singapore-imda-rules.md), [amateur](../19-regulations-safety/amateur-radio-licensing.md) |
| F-04 | FB | Configured power/channel/air rate read back from each module and logged in the boot CONFIG line | read-back = plan | ethos (log = evidence) |
| F-05 | FB | Installed S11 re-checked after final assembly (nose cone on) | ≤ −10 dB | B-06 |
| F-06 | H | Range test at legal power with the flight hardware (15-km-equivalent attenuation) within the last 30 days | PER < 1 % at A_eq | [telemetry §7](lora-rocket-telemetry-link.md) |
| F-07 | FB | Ground stations: positions cross-range ≥ 3–5 km, two azimuths, IQ recording verified (file grows), PPS time | checklist signed | [ground station](ground-station-tracking-yagi.md) |
| F-08 | H | Pad procedure: receivers ≥ 100 m or attenuated during pad checks; LNAs protected | in the launch procedure | [ground station](ground-station-tracking-yagi.md) |
| F-09 | FB | GNSS lock with all transmitters on, on the pad, ≥ 10 min; MON-RF jamming indicator nominal | logged | [GNSS front end](gnss-front-end-design.md) |
| F-10 | H | Landed-mode switch tested (both ends), recovery DF kit packed and calibrated | demonstrated | [phased-array starter](phased-array-starter-build.md) |
| F-11 | M | RF exposure distances for people near the pad transmitter | posted | [RF exposure](../19-regulations-safety/rf-exposure-safety.md) |
| F-12 | M | Spectrum survey of the site (1 h) and channel choice recorded | plot on file | [SDR recipe](sdr-receiver-build.md) |

### Example — what the pre-flight tool caught on this domain's own plan
Running `proj_preflight_rf.py` on the first draft of the Singapore test plan (433.125 MHz at SF7/250, E220 on CH18) failed R1: the 250 kHz channel's lower edge is 433.000 MHz, below the 433.05 MHz band edge. Moving the primary to 434.125 MHz then failed R5: its 2nd harmonic (868.25 MHz) sat 0.125 MHz from CH18. The final plan (434.125 MHz at 9.5 dBm with one 48-byte frame at 2 Hz — 9.8 % duty — and the E220 on CH17 at 24 dBm) passes R1–R5; R6 stays FAIL until the conducted-power, harmonic, installed-S11 and range-test files are attached.

## Practical notes
- Keep the four checklists as a version-controlled file in each board repo; each review appends a dated results block (never edits the previous one).
- One reviewer drives, one checks against the source page; disagreements become findings, not discussions.
- Record deliberate design choices that look like defects (e.g. downlink-only by design) so they are not re-raised every review.
- Severity is about consequence in flight, not about effort to fix.

## Common mistakes & misconceptions
- **"It passed on the bench."** Most RF findings here appear only in the assembled vehicle (coupling, detuning) or in the field (overload, multipath).
- **"The checklist says check harmonics — we looked at the SA."** Without the analyser-distortion check and the plot on file it is not evidence.
- **"Centre frequency in band = legal."** The occupied bandwidth must be in band.
- **"Same settings as last campaign."** Venue, assigned channel and legal limits change; rerun F-01.
- **"Waived because we ran out of time."** A waiver needs a written reason and the risk owner's name.

## How to simulate / verify
- `python3 tools/verify/proj_preflight_rf.py [config.json]` — gate F-01 automation (edit `CONFIG` or pass JSON with venue, radios, schedules, evidence paths).
- The recipe scripts listed in Level 2 for every budget a reviewer recomputes.
- `python3 tools/build_index.py --check` for the KB itself (link/section checks).

## Open questions / gaps
- The pre-flight tool's venue table covers Singapore exempt/amateur and IREC only; add EuRoC/Australia rows from [competitions](../19-regulations-safety/international-rules-for-competitions.md).
- No automated check yet for installed-S11 files or SA plots (the tool only checks that evidence is referenced).

## Sources
1. This KB, [RF PCB review checklist](../13-pcb-rf-layout-emc/rf-pcb-review-checklist.md) and [RF layout rules](../13-pcb-rf-layout-emc/rf-layout-rules.md) — layout items, stackup/50 Ω, return paths. (internal)
2. This KB, [RF bring-up & debug playbook](../17-test-measurement/rf-bring-up-debug-playbook.md) — order of bring-up, symptom-to-dB translation, instrument protection. (internal)
3. This KB, the domain-20 recipes ([telemetry](lora-rocket-telemetry-link.md), [ground station](ground-station-tracking-yagi.md), [filter](bandpass-filter-design-walkthrough.md), [patch](patch-antenna-design-walkthrough.md), [LNA](lna-design-walkthrough.md), [GNSS front end](gnss-front-end-design.md), [SDR](sdr-receiver-build.md), [FMCW](fmcw-radar-build.md), [phased array](phased-array-starter-build.md)) — the project-specific items. (internal)
4. This KB, [Singapore IMDA rules](../19-regulations-safety/singapore-imda-rules.md), [competition rules](../19-regulations-safety/international-rules-for-competitions.md), [amateur licensing](../19-regulations-safety/amateur-radio-licensing.md). (internal; regulator documents)
5. Space Bar avionics knowledge base (user's own notes) — engineering ethos (pre-registration, evidence, findings with IDs/severity/dispositions), HIL/bench practice (22/22 battery power-ups, boot CONFIG line), Avionics B lessons (documentation drift, I²C speed). (internal, user-provided)
