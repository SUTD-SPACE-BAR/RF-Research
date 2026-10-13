# 13-pcb-rf-layout-emc — PCB layout for RF, EMC and manufacturing

How to turn an RF schematic into a board that works the first time: choosing stackups and laminates (with JLCPCB's actual stackups and calculator results), where return currents flow and why splits and slots fail, vias, stitching and via fences, component placement and matching-network layout, connector launches, shield cans and isolation budgets, EMC/EMI (cable radiation, clock harmonics and self-desense, pyro and sensor susceptibility, ESD), power distribution for PAs/VCOs/LNAs, mixed-signal partitioning, JLCPCB manufacturing options, thermal management of PAs and LoRa modules in a sealed av-bay, and a review checklist. Transmission-line maths is in [03](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md), part parasitics in [04](../04-real-components-hf/_index.md), conductor/dielectric physics in [02](../02-electromagnetics/_index.md), antennas in [08](../08-antennas/_index.md), test gear in [17](../17-test-measurement/_index.md), parts in [18](../18-components-parts/_index.md). Numbers on these pages are reproduced by `tools/verify/pcb_*.py`.

## Reading order (beginner → advanced)
1. [Stackups and materials](stackups-and-materials.md) — cores/prepregs, glass styles, Dk vs resin, JLCPCB stackups and 50 Ω widths (calculator vs field solver), Rogers/PTFE, loss, fibre weave.
2. [Grounding and return paths](grounding-and-return-paths.md) — return-current footprint, crossover frequency, slots/splits, layer changes, star-ground myth, 20-H rule.
3. [RF layout rules](rf-layout-rules.md) — placement order, matching at the pin, 0201/0402/0603, LC-filter trace rule, crystals, keep-outs, reference layouts, KiCad.
4. [Vias, stitching and fencing](vias-stitching-fencing.md) — via inductance, the physics behind λ/20 stitching (FDFD-checked), CPWG fences, copper-island resonances, stubs, via-in-pad, thermal vias.
5. [Connectors and launches](connectors-and-launches.md) — SMA/U.FL pads and plane voids, L–C compensation, vertical launches, return-loss budgets, pigtail loss.
6. [Power distribution and decoupling for RF](power-distribution-decoupling-for-rf.md) — target impedance, anti-resonance, bead + cap peaking, PA burst droop, star feeding, VCO pushing.
7. [Mixed-signal layout](mixed-signal-layout.md) — ADC grounding, desense budgets, required isolation, bus and clock routing, floor-planning a flight computer.
8. [EMC/EMI fundamentals](emc-emi-fundamentals.md) — DM/CM radiation (Ott), allowed currents, clock spectra, harmonic-landing table, spread spectrum, pyro RF safety, rectification, ESD.
9. [Shielding and isolation](shielding-and-isolation.md) — can cavity modes and Q, seams/apertures, absorbers, feed-through filters, TX/GNSS budget.
10. [Thermal management](thermal-management-rf.md) — PA dissipation, θJA on your board, spreading vs vias, sealed av-bay transient, crystal drift.
11. [Making RF boards at JLCPCB](jlcpcb-rf-manufacturing.md) — impedance control, tolerances, features, finishes, Rogers, assembly, coupons.
12. [RF PCB review checklist](rf-pcb-review-checklist.md) — the actionable summary of all of the above.

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [stackups-and-materials](stackups-and-materials.md) | **canonical 50 Ω width table**, FR-4 grades/Tg, glass styles and resin content (Isola 370HR data), JLC 2/4/6-layer stackups, JLC calculator widths re-checked by FD solver (49.2–52.7 Ω), mask effect, CPWG gap rule, tolerance Monte-Carlo, loss table, weave skew, Rogers/PTFE/Megtron, hybrids | mixed | high |
| [grounding-and-return-paths](grounding-and-return-paths.md) | image-theory return current (FD-verified), 2πh effective width, kHz crossover, crosstalk 1/(1+(D/h)²), slot impedance and CM radiation, layer-change return vias, star ground, AGND/DGND, 20-H rule | mixed | high |
| [rf-layout-rules](rf-layout-rules.md) | placement order, pad C and ESL by case size, LC-filter trace placement, mitres/stubs, Semtech/TI/Espressif/u-blox rules, crystal thermal isolation, KiCad features | mixed | high |
| [vias-stitching-fencing](vias-stitching-fencing.md) | via L on JLC geometries, post-wall isolation vs pitch (own FDFD; thin-post formula fails for fat vias), stitching rules, island/finger resonances, stubs/backdrill, via-in-pad, thermal vias | mixed | medium |
| [connectors-and-launches](connectors-and-launches.md) | pad discontinuities, SMA plane voids (12 → 21 dB RL at 2.45 GHz), L–C compensation, vertical launch coax model, U.FL specs and pigtail loss, RL budgets | mixed | medium |
| [power-distribution-decoupling-for-rf](power-distribution-decoupling-for-rf.md) | target impedance, 100 nF ∥ 100 pF anti-resonance, bead + cap peaking/damping, E22 1.2 A burst droop (≥ 250 µF), star vs daisy chain, VCO pushing spurs, filter chain, plane capacitance | mixed | medium |
| [mixed-signal-layout](mixed-signal-layout.md) | single plane + partitioning, ADC grounding, LoRa/GNSS desense thresholds, required isolation (70–105 dB), what layout features give, shared-ground error, bus edges at L1, flight-computer floor plan; **termination and crosstalk budgets for SPI and clocks** on JLC04161H-7628 | mixed | medium |
| [emc-emi-fundamentals](emc-emi-fundamentals.md) | DM/CM constants re-derived, allowed currents vs FCC B, trapezoid spectra, harmonic-landing table (40 MHz×23 = 920 MHz; 25 MHz×63 = 1575 MHz), SSC FFT (≈ 4 dB below the usual estimate), pyro pickup vs MIL-STD-464 16.5 dB, RF rectification, ESD/TVS; **avionics standards and transients** (MIL-STD-461G/DO-160G families, EFT/surge/ESD, snubbers and TVS for pyro/servo loads); **conducted and radiated pre-compliance** (LISN, LPDA pre-scan, failed-test workflow, budget kit) | mixed | medium |
| [shielding-and-isolation](shielding-and-isolation.md) | can modes (FD-checked), Q and absorbers, slot SE, feed-through filters, isolation budgets, TX/GNSS coexistence; **enclosures, doors, meshes and fabrics** (seams, gaskets, mesh SE, Faraday boxes, SDR test recipe) | mixed | medium |
| [thermal-management-rf](thermal-management-rf.md) | dissipation, nodal θJA with EPAD vias, plane spreading, sealed av-bay transient for a 2 W module, pulse heating, crystal drift | mixed | medium |
| [jlcpcb-rf-manufacturing](jlcpcb-rf-manufacturing.md) | impedance control/tolerance (with conflicting reports), TG155, features, POFV, finishes and RF loss, Rogers 2-layer service, PCBA limits, coupons | intro | medium |
| [rf-pcb-review-checklist](rf-pcb-review-checklist.md) | sections A–K: frequency plan → bring-up | intro | high |
| [digital-termination-and-crosstalk](digital-termination-and-crosstalk.md) | overshoot vs TD/tr (Bergeron sim), series/parallel/Thevenin/AC termination with power, NEXT/FEXT from field-solver Lm/Cm vs modal sim, 3W rule on 7628 vs 2-layer, clock-to-RF coupling at 920 MHz | mixed | high |

## Domain FAQ (top questions → page#section)
- *How wide is a 50 Ω trace on a JLCPCB 2- or 4-layer board?* → **[canonical 50 Ω width table](stackups-and-materials.md#canonical-50-ω-width-table)** (JLC calculator values with stackup, εr and mask stated; other domains link here)
- *Why do calculators disagree on the JLC width?* → [Stackups § Practical notes / Common mistakes](stackups-and-materials.md#common-mistakes--misconceptions)
- *Do I need Rogers for 2.4 / 5.8 GHz?* → [Stackups § Worked example 4](stackups-and-materials.md#4-a-4-element-58-ghz-patch-array-feed-fr-4-or-ro4350b)
- *Where does return current flow, and should I split the ground plane?* → [Grounding § Level 1 / Intuition](grounding-and-return-paths.md#level-1--the-return-current-footprint)
- *Why is crossing a slot bad?* → [Grounding § Level 3](grounding-and-return-paths.md#level-3--obstacles-slots-splits-layer-changes-and-plane-edges)
- *How often should I stitch ground vias?* → [Vias § Level 2](vias-stitching-fencing.md#level-2--a-via-row-as-a-post-wall-the-physics-of-the-λ20-rule)
- *Should I via-fence or pour ground around my antenna?* → No — [Layout rules § Level 3](rf-layout-rules.md#level-3--why-the-antenna-keep-out-must-be-copper-free-and-never-fenced)
- *Is a cross-hatched ground plane OK for RF?* → [Grounding § Level 3](grounding-and-return-paths.md#level-3--obstacles-slots-splits-layer-changes-and-plane-edges)
- *0402 or 0201 at 2.4 GHz?* → [Layout rules § Level 1](rf-layout-rules.md#level-1--how-parasitics-shift-a-matching-element)
- *Should I void the ground under my SMA pad?* → [Connectors § Level 2](connectors-and-launches.md#level-2--the-pad-as-a-line-section-and-compensation)
- *How much bulk capacitance does a 2 W LoRa module need?* → [PDN § Worked example 1](power-distribution-decoupling-for-rf.md#1-supplying-an-ebyte-e22-400t33d-433-mhz-2-w-from-a-2s-pack)
- *Why does my bead filter make noise worse?* → [PDN § Level 3](power-distribution-decoupling-for-rf.md#level-3--bead--capacitor-filters-psrr-chains-and-pushing)
- *Which clocks jam my LoRa or GNSS?* → [EMC § TL;DR](emc-emi-fundamentals.md#tldr), [Mixed-signal § Worked example 4](mixed-signal-layout.md#4-my-gnss-loses-fix-when-the-sd-card-logs)
- *Can my telemetry transmitter fire a pyro channel?* → [EMC § Level 3](emc-emi-fundamentals.md#level-3--susceptibility-rectification-pyro-circuits-esd)
- *At what frequency does my shield can resonate?* → [Shielding § Level 1](shielding-and-isolation.md#level-1--cavity-modes-of-a-can)
- *Will the LoRa module overheat on the pad?* → [Thermal § Level 3](thermal-management-rf.md#level-3--transient-heating-enclosure-and-the-crystal)
- *ENIG, HASL or OSP for RF at JLCPCB?* → [JLCPCB § TL;DR](jlcpcb-rf-manufacturing.md#tldr)
- *What should I check before ordering?* → [Checklist](rf-pcb-review-checklist.md)
- *Which avionics EMC tests (MIL-STD-461, DO-160) matter for a flight computer, and how do I snubber a pyro or servo load?* → [EMC § standards and transients](emc-emi-fundamentals.md#emc-standards-and-transients-for-avionics)
- *How do I pre-scan conducted and radiated emissions before a lab visit?* → [EMC § pre-compliance](emc-emi-fundamentals.md#conducted-and-radiated-pre-compliance)
- *Does my SPI or clock line need termination, and how far apart must traces be?* → [Mixed-signal § SPI budgets](mixed-signal-layout.md#termination-and-crosstalk-budgets-for-spi-and-clocks)
- *How much does a mesh, a seam or a "Faraday bag" really shield?* → [Shielding § enclosures](shielding-and-isolation.md#enclosures-doors-meshes-and-fabrics)
- *How much RF power can a PCB trace carry thermally?* → [03 planar lines § power handling](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md#level-3--power-handling-of-rf-traces)

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
Ott, *Electromagnetic Compatibility Engineering*; Bogatin, *Signal and Power Integrity — Simplified*; Johnson & Graham, *High-Speed Digital Design*; Paul, *Introduction to EMC*; Archambeault, *PCB Design for Real-World EMI Control*; Pozar, *Microwave Engineering*; vendor app notes (Semtech AN1200.37/.40, TI SWRA640, Espressif ESP32-S3 guidelines, u-blox integration manual and GNSS-antennas note); JLCPCB documentation and calculator; Rogers/Isola/Panasonic datasheets; MIL-STD-464C.

## Known gaps
- No measured data yet on JLCPCB coupons (TDR) to settle the remaining 1–5 % calculator spread and the ±10 % vs ±20 % tolerance question.
- Via-fence isolation is from a 2-D FDFD (normal incidence, infinite posts); CPWG fence distance from the gap edge not derived.
- Pyro-lead RF pickup and av-bay thermal numbers are order-of-magnitude models — measure on the real vehicle.
- No openEMS 3-D studies of launches, slots or cans on JLC stackups yet (would replace several representative values) — see [16-simulation-tools](../16-simulation-tools/_index.md).
- Semtech AN1200.66 and ADI MT-031/MT-101 could not be retrieved in full; Southwest Microwave launch note only via summary.
