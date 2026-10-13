# 04-real-components-hf — Real components at RF

How real passive parts and interconnects behave at radio frequencies: chip resistors, MLCCs, inductors and air coils, ferrite beads and chokes, PCB traces/vias/pads, IC packages and bondwires, quartz crystals and oscillators, and the vendor models (S-parameters, SPICE) used to simulate them. Ideal-element theory is in [01-circuit-theory](../01-circuit-theory/_index.md); board-level layout practice (stackups, grounding, stitching) in [13-pcb-rf-layout-emc](../13-pcb-rf-layout-emc/_index.md); part selection/sourcing in [18-components-parts](../18-components-parts/_index.md). Numbers on these pages are reproduced by `tools/verify/components_*.py`.

## Reading order (beginner → advanced)
1. [Capacitors at RF — MLCC](capacitors-at-rf-mlcc.md) — dielectric classes, DC bias/ageing, ESR/ESL/SRF, DC blocks, bypass and anti-resonance.
2. [Inductors at RF](inductors-at-rf.md) — technologies, Q and SRF, air-coil formulas (Wheeler/Nagaoka/Lundin/Rosa).
3. [Resistors at RF](resistors-at-rf.md) — parasitics, thin vs thick film, terminations, attenuators, derating.
4. [Ferrites and beads](ferrites-and-beads.md) — complex permeability, DC-bias collapse, bead–cap resonance and damping, Fair-Rite mixes, CM chokes.
5. [PCB parasitics — traces, vias, pads](pcb-parasitics-traces-vias-pads.md) — partial vs loop inductance, via formulas, pad capacitance, plane slots.
6. [Package parasitics and bondwires](package-parasitics-bondwires.md) — bondwire and lead inductance, exposed pads, ground pins.
7. [Crystals and resonators](crystals-and-resonators.md) — BVD model, load capacitance, pulling, XO/TCXO/OCXO, LoRa frequency budgets, rocket g-sensitivity and Doppler.
8. [Component models — S2P and SPICE](component-models-s2p-spice.md) — vendor files, measurement configurations, mounting corrections, passivity.

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [capacitors-at-rf-mlcc](capacitors-at-rf-mlcc.md) | C0G vs X7R/X5R/Y5V (EIA codes), DC-bias, ageing, ESR/ESL/SRF, capacitor Q, DC-block tables at 433/915/2450 MHz, parallel anti-resonance, orientation, RF-grade parts, voltage ratings | mixed | high |
| [inductors-at-rf](inductors-at-rf.md) | wirewound/multilayer/thin-film/air/ferrite inductors, L(f), Q(f), SRF, saturation, Nagaoka/Lundin/Wheeler with error table, Rosa corrections, Coilcraft/Murata data | mixed | high |
| [resistors-at-rf](resistors-at-rf.md) | RLC model, flat value $\sqrt{L/C}$, Vishay thin-film data, terminations, π/T pads with power split, derating | intro | medium |
| [ferrites-and-beads](ferrites-and-beads.md) | R/X/|Z| curves, $\mu'$/$\mu''$, DC bias, bead–capacitor resonance and damping, Fair-Rite 31/43/61/73, CM chokes, when beads hurt | mixed | high |
| [pcb-parasitics-traces-vias-pads](pcb-parasitics-traces-vias-pads.md) | trace L′/C′ on JLCPCB stackups, wire/strip partial L, Goldfarb–Pucel via, Johnson loop formula, coupled vias, pad capacitance, plane slots | mixed | medium |
| [package-parasitics-bondwires](package-parasitics-bondwires.md) | bondwire L (tables), lead L by package (TI data), EP ground path, degeneration and ground bounce, flip-chip | intermediate | medium |
| [crystals-and-resonators](crystals-and-resonators.md) | BVD, fs/fp/fL, pulling, load caps, Pierce gm, drive level, AT-cut cubic, ageing, oscillator classes, LoRa offset/drift limits, TCXO need, g-sensitivity, Doppler | mixed | medium |
| [component-models-s2p-spice](component-models-s2p-spice.md) | vendor model sources, series/shunt fixtures and sensitivity, mounting and reference planes, interpolation, passivity/causality, bias limits | intermediate | high |

## Domain FAQ (top questions → page#section)
- *Which DC-block capacitor value at 433 / 915 / 2450 MHz?* → [MLCC § Worked example 1](capacitors-at-rf-mlcc.md#1-choosing-dc-block-capacitors-toolsverifycomponents_mlccpy-3)
- *Why is my 10 µF ceramic only 3 µF?* → [MLCC § Level 3 DC-bias](capacitors-at-rf-mlcc.md#level-3--distributed-behaviour-class-2-physics-and-limits)
- *Does 100 nF + 100 pF in parallel help?* → [MLCC § Worked example 3](capacitors-at-rf-mlcc.md#3-does-100-pf-across-100-nf-help-at-433-mhz-5)
- *Wirewound or multilayer inductor?* → [Inductors § TL;DR and Worked example 1](inductors-at-rf.md#1-choosing-a-matching-inductor-for-43392-mhz)
- *How accurate is Wheeler's formula?* → [Inductors § Level 2](inductors-at-rf.md#level-2--air-coil-formulas-current-sheet)
- *Can I build an attenuator from chip resistors for my 2 W transmitter?* → [Resistors § Worked example 2](resistors-at-rf.md#2-measuring-a-2-w-lora-module-on-a-spectrum-analyser)
- *Why did adding a ferrite bead make my supply noisier?* → [Ferrites § Level 3](ferrites-and-beads.md#level-3--the-beadcapacitor-resonance-and-damping)
- *Which Fair-Rite mix for a cable?* → [Ferrites § Level 2](ferrites-and-beads.md#level-2--material-physics-complex-permeability)
- *Is a PCB trace 1 nH/mm? How much is a via?* → [PCB parasitics § TL;DR, Level 2](pcb-parasitics-traces-vias-pads.md#level-2--isolated-conductors-and-vias)
- *Why do RF chips have so many ground pins?* → [Package parasitics § Level 3](package-parasitics-bondwires.md#level-3--effects-on-circuits)
- *How do I choose crystal load capacitors?* → [Crystals § Level 2](crystals-and-resonators.md#level-2--pulling-load-capacitors-and-the-pierce-oscillator)
- *Does LoRa need a TCXO?* → [Crystals § Level 3 / Worked example 2](crystals-and-resonators.md#2-when-a-433-mhz-lora-link-needs-a-tcxo)
- *Will rocket acceleration shift my radio frequency?* → [Crystals § Worked example 4](crystals-and-resonators.md#4-boost-phase-effects-on-a-rocket-915-mhz)
- *Why doesn't my simulation with vendor S-parameters match the board?* → [Component models § Level 3](component-models-s2p-spice.md#level-3--using-models-correctly)

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
Manufacturer technical documentation dominates this domain: Murata (GJM, LQG, SimSurfing, S-parameter conditions), Coilcraft (0402HP datasheet, Doc 1721), Johanson, Kyocera-AVX/ATC (coupling-capacitor notebook, LICC), KEMET (F9000), Vishay (TN 60107), Fair-Rite (EMI suppression guide, material sheets), TI (QFN comparison tables, SLVAEE1), Semtech (SX1261/2 datasheet, AN1200.14, AN1200.37), plus Vig's quartz tutorial, Knight's solenoid-inductance monograph, Goldfarb & Pucel (via model), H. Johnson (via inductance), Burket (ferrite beads), and textbooks by Bowick, Ludwig & Bogdanov, Pozar, Grover, Paul and Lee.

## Verification scripts
`tools/verify/components_mlcc.py`, `components_inductors.py`, `components_resistors.py`, `components_ferrite_bead.py`, `components_pcb_parasitics.py`, `components_bondwire.py`, `components_crystal.py`, `components_s2p_models.py`.

## Known gaps
- No bench measurements yet of JLCPCB-stocked parts (in-circuit Q of multilayer inductors, mounted ESL of 0402 MLCCs on JLC stackups, pad capacitance) — the "medium" confidence pages rely on models plus vendor data.
- AT-cut cubic coefficients quoted from standard literature (not re-fetched); SX1261/2 in-packet drift formula inferred from secondary summaries (datasheet shows it as an image).
- Complex permeability curves for Fair-Rite materials are only described, not digitised.
- MEMS oscillators, BGA/WLCSP package parasitics and KEMET/TDK model measurement conditions not covered in depth.
- Coilcraft 0402HP: datasheet SRF inconsistent with a single-pole L(f) model (documented on the inductors page; needs vendor S-parameters to model quantitatively).
