---
title: RF PCB review checklist — schematic, stackup, layout, EMC, thermal, manufacturing and bring-up checks for LoRa/GNSS/2.4 GHz boards
domain: 13-pcb-rf-layout-emc
slug: rf-pcb-review-checklist
tags: [checklist, design-review, schematic-review, layout-review, RF, EMC, desense, stackup, impedance, return-path, decoupling, crystal, antenna, connector, pyro, thermal, JLCPCB, bring-up, KiCad]
prerequisites:
  - stackups-and-materials.md
  - grounding-and-return-paths.md
  - rf-layout-rules.md
related:
  - vias-stitching-fencing.md
  - connectors-and-launches.md
  - shielding-and-isolation.md
  - emc-emi-fundamentals.md
  - power-distribution-decoupling-for-rf.md
  - mixed-signal-layout.md
  - jlcpcb-rf-manufacturing.md
  - thermal-management-rf.md
  - ../20-projects-recipes/design-review-checklists.md
level: intro
confidence: high
last_updated: 2026-10-02
---

# RF PCB review checklist

## Questions this page answers
- What should I check before sending an RF board (LoRa, GNSS, 2.4/5.8 GHz) to fabrication?
- What schematic items commonly break RF boards?
- What layout checks catch the most common RF and EMC failures?
- What should the fab notes and the as-built record contain?
- What do I measure first when the boards arrive?

## TL;DR
- Review in this order: **frequency plan → stackup → schematic → placement → RF routing → return paths → supplies → EMC/I-O → thermal → manufacturing → test hooks**. Each item below links to the page that explains *why* and gives the numbers.
- The five checks that catch most first-spin failures: (1) **the 50 Ω width matches the ordered stackup and mask choice**; (2) **no RF or fast signal crosses a plane gap or changes reference without a return via**; (3) **matching/filter parts sit at the pins with their own ground vias, as in the reference design**; (4) **no clock harmonic lands on your receive channels** (and edges are slowed); (5) **bulk capacitance and star feeding for PA bursts**.
- For Space Bar flight computers add: pyro-lead RF safety, TX duty/thermal on the pad, crystal/TCXO choice for long packets, and the as-built stackup in the repo.

## Intuition (no math)
A checklist is a way of not relying on memory at 2 a.m. before the JLCPCB cut-off. RF boards fail in a small number of repeatable ways — wrong impedance, broken return paths, parasitics in the match, self-interference, starved supplies, heat and assembly problems — and each has a cheap check at design time and an expensive fix after fabrication. The items below are short; follow the links for the physics and numbers.

## The math
This page collects decisions rather than derivations. The quantitative criteria referenced below come from:
- Z0 tolerance and widths — [stackups](stackups-and-materials.md) (ΔZ0 ≈ +2.85 Ω per +10 % h, −2.7 Ω per +10 % W).
- Return-current footprint $K\propto h/(h^2+x^2)$; 90 % within ±6.3h — [grounding](grounding-and-return-paths.md).
- Via-fence isolation ≈ 18 dB/row at λ/20 — [vias](vias-stitching-fencing.md).
- Discontinuity $|\Gamma|\approx\omega CZ_0/2$ — [connectors](connectors-and-launches.md).
- Desense: spur ≤ noise floor − 6 dB for ≤ 1 dB loss — [mixed-signal](mixed-signal-layout.md).
- Droop $I\cdot ESR+L\,dI/dt+I\,t_{resp}/C$ — [PDN](power-distribution-decoupling-for-rf.md).
- $T_j=T_a+P\theta_{JA}$ — [thermal](thermal-management-rf.md).

## Design equations & rules of thumb

### A. Frequency plan and architecture
- [ ] List every oscillator/clock (MCU, crystal, USB, SD, SPI, switcher f_sw) and every receive band; run the harmonic-landing table (`pcb_emc_radiation.py` §4). Move channels/clocks off collisions (e.g. avoid 920.000 MHz with a 40 MHz clock; SD ≠ 25 MHz near GNSS) — [EMC](emc-emi-fundamentals.md).
- [ ] Transmitter vs other receivers on the board/vehicle: isolation budget (antenna coupling + filters ≥ P_TX − receiver max/blocking input) — [shielding](shielding-and-isolation.md).
- [ ] Reference oscillator: crystal with thermal isolation, or TCXO for long packets at high power / outside −20…+70 °C — [rf-layout-rules](rf-layout-rules.md).
- [ ] Regulatory channel/power for the band (Singapore SRD 920–925 MHz etc.) — [band plans](../15-lora-ism-radios/ism-band-plans-duty-cycle.md).

### B. Stackup and materials
- [ ] Stackup named (e.g. JLC04161H-7628), material **FR-4 TG155** for impedance orders, copper weights, finish — [JLCPCB](jlcpcb-rf-manufacturing.md).
- [ ] L1 RF over **solid L2 GND**; L3 GND (or power pour) — no splits under RF.
- [ ] 50 Ω width from the fab calculator *with the chosen mask option*, quoted with stackup, εr and mask assumption; cross-checked with a second tool (KiCad/field solver) — [canonical width table](stackups-and-materials.md#canonical-50-ω-width-table).
- [ ] Rogers (2-layer) only if loss/Dk tolerance/phase matching require it (≥ 5 GHz feeds, filters, arrays).
- [ ] KiCad Physical Stackup matches the ordered stackup (Space Bar documentation-drift lesson).

### C. Schematic
- [ ] RF section copied from the vendor reference design (values, *case sizes*, topology); deviations noted with a reason.
- [ ] Footprints for RF parts match the reference (0201/0402); vendor S-parameter models identified for re-tuning.
- [ ] Test/tuning provisions: 0 Ω/DC-block positions for a U.FL test port, π-pad placeholders after the chip.
- [ ] DC blocks and bias-Ts on RF lines where needed; ESD on antenna ports ≤ 0.2–0.5 pF — [EMC](emc-emi-fundamentals.md).
- [ ] RF switch control logic and default states; PA never enabled without a load.
- [ ] Supplies: PA rail sized for bursts (≥ 30 % margin; bulk ≥ ≈ 250 µF at a 2 W module); separate/filtered rails for VCO/LNA/GNSS/sensors; bead + cap filters damped — [PDN](power-distribution-decoupling-for-rf.md).
- [ ] Every connector that leaves the board has a filter footprint (C to GND + bead/CM choke).
- [ ] Pyro outputs: RF bypass at the connector, shorted/clamped when disarmed, twisted leads specified — [EMC](emc-emi-fundamentals.md).
- [ ] MCU drive strength/series resistors on fast lines (SPI, SD, clocks) — 22–47 Ω.

### D. Placement
- [ ] Antennas/connectors at board edges, far apart (GNSS one end, TX the other); keep-outs drawn on all layers.
- [ ] **No via fence, ground pour, stitching via, shield can or trace inside or around an antenna radiator's keep-out** (any layer); fences stop at the keep-out boundary; the ground edge facing the antenna is solid and stitched — [rf-layout-rules](rf-layout-rules.md#level-3--why-the-antenna-keep-out-must-be-copper-free-and-never-fenced).
- [ ] RF IC → match/filter/switch in signal order at the pins; shunt parts' ground vias at their pads.
- [ ] Crystal/TCXO: short symmetric loop, copper void/thermal isolation from PA, no traces underneath — [rf-layout-rules](rf-layout-rules.md).
- [ ] PA/module near a board edge or mounting point with a heat path; not next to crystal, baro or GNSS — [thermal](thermal-management-rf.md).
- [ ] Switchers near the power entry, away from GNSS/LNA (≥ 20–30 mm); hot loops minimal — [mixed-signal](mixed-signal-layout.md).
- [ ] Digital (MCU, SD, USB) partitioned away from RF and sensors; sensors on clean filtered rails.

### E. RF routing
- [ ] RF on L1, no layer changes; if unavoidable, GND return vias within ≈ 1 mm and identical reference on both sides — [grounding](grounding-and-return-paths.md).
- [ ] CPWG gaps ≥ 0.15–0.2 mm; side grounds fenced at ≤ λ/20 of the highest frequency of concern (incl. harmonics) — [vias](vias-stitching-fencing.md).
- [ ] No stubs > λ/20 (unpopulated pads, test points, branches).
- [ ] Wide pads (SMA, module RF pads) on thin prepreg: L2 void under the pad, L3 solid, vias around the void — [connectors](connectors-and-launches.md).
- [ ] Rotated/angled connector footprints keep the full launch geometry (pad, void, ground vias) rotated with them; the bend is in the 50 Ω trace ≥ 1–2 mm from the pad.
- [ ] Trace inductance in series with inductors, not with shunt capacitors (TI LC-filter rule).
- [ ] Bends: 45°/arc (cosmetic below 6 GHz on thin prepreg).
- [ ] Balun/differential RF paths symmetric (TI: ≤ 1.5 dB / 10° imbalance).

### F. Return paths and ground
- [ ] Highlight every fast/RF net and check the reference plane underneath for gaps/slots/antipad chains (±3–5h corridor).
- [ ] No floating copper islands; pours stitched at ≤ λ/20; fingers < λ/10 of the top frequency.
- [ ] Solid (not cross-hatched) reference planes under RF and controlled-impedance lines; hatching only where flexibility/warp demands it, with Z0 recomputed — [grounding](grounding-and-return-paths.md).
- [ ] System grounding across boards and cables reviewed (ground loops, shield bonding, where battery/servo/pyro returns flow) — [grounding](grounding-and-return-paths.md).
- [ ] Board-edge GND stitching; shield-can ring stitched to L2 every 1–3 mm.
- [ ] RF ground pads: solid zone connections (no thermal spokes); ≥ the reference's EPAD via count (ESP32-S3: ≥ 9).
- [ ] High-current returns (battery, pyro, servo) compact and away from sensors/ADC references.

### G. Supplies and decoupling
- [ ] Decoupling at each pin, smallest closest, one via per cap, power routed through the cap first.
- [ ] Check anti-resonances of mixed-value banks in the RF bands (`pcb_pdn.py` §2).
- [ ] Star feeding of PA vs LNA/VCO from the bulk/plane; no daisy chain behind the PA.
- [ ] Regulator stability with the chosen output caps; brown-out thresholds set.

### H. EMC and I/O
- [ ] Every cable entry filtered at the connector; CM chokes on USB/CAN/harness where needed.
- [ ] Antenna feed balanced/choked (no CM current on coax); coax routed away from sensors and pyro leads.
- [ ] Fast buses on inner layers, not along edges; SSC enabled where available.
- [ ] Optional shield-can footprints over the RF section (f₁₁₀ well above internal frequencies).

### I. Thermal
- [ ] PA/module dissipation computed; θJA estimate for *this* board; pad TX duty/power plan for a sealed av-bay.
- [ ] EPAD land pattern, paste windows, via-in-pad choice (POFV) agreed with the assembler.

### J. Manufacturing and documentation
- [ ] Impedance control selected; impedance table in order remarks (layer, reference, width, mask).
- [ ] Minimum features with margin (trace/space ≥ 0.1 mm, vias 0.3/0.5–0.6 mm) — [JLCPCB](jlcpcb-rf-manufacturing.md).
- [ ] Finish chosen for RF (OSP, or ENIG with RF traces masked); Standard PCBA if 0201.
- [ ] Test coupon (50 Ω line + launches) on the panel.
- [ ] As-built record in the repo: stackup, material, finish, BOM with exact module variants, fab notes.

### K. Bring-up and verification plan
- [ ] Power-up with current limit; check rails under a dummy burst load.
- [ ] VNA on the matching network/antenna port (chip unpowered); conducted TX power and harmonics into an attenuator + SA.
- [ ] Frequency offset/drift over a long packet (SDR).
- [ ] Desense test: receiver noise floor/RSSI and GNSS C/N0 with each subsystem toggled.
- [ ] Near-field scan for hot spots; CM current on harnesses.
- [ ] Thermal soak at flight duty cycle in a closed box.
- [ ] Pyro channel RF test: dummy bridge current with the flight transmitter at its closest position.

## Worked examples

### 1. Applying the checklist to a Space Bar secondary-FC-style board
ESP32-S3 + E220-900T30D (900 MHz, 1 W, UART) + MAX-M10S GNSS (U.FL) + BMP390/LSM6DSV/MMC5983 on a 4-layer JLC board: A — 40 MHz × 23 = 920 MHz sits in the SG band → set the E220 channel ≥ 0.5 MHz away and note it; SD clock not 25 MHz. B — JLC04161H-7628 (εr 4.4), TG155, 50 Ω = 0.359 mm with soldermask (canonical table). C — E220 on its own 5 V buck-boost (already so on Avionics C), add ≥ 220 µF low-ESR at the module; ESD at the U.FL ≤ 0.5 pF. D — GNSS at one end, E220 SMA at the other, sensors on a filtered LDO. E — GNSS RF_IN to U.FL on L1, 8 mm, no vias. F — no L2 gaps; stitch pours. I — 1 W module ≈ 2.1 W heat while TX; pad duty ≤ 20 %. K — desense test with SD logging active.

### 2. Reviewing someone else's KiCad board
Use the `pcbreview` skill/tooling where available for deterministic return-path, impedance and decoupling checks, then walk sections D–H manually with the RF nets highlighted on each layer.

## Practical notes
- Keep this checklist in the board repo and tick it in the PR/design review — evidence over memory (Space Bar engineering ethos: pre-registration and faithful reporting).
- Record every deviation from the vendor reference and its justification.
- After bring-up, add any new failure mode to the checklist (and to this page).

## Common mistakes & misconceptions
- **Reviewing only the schematic** — most RF failures are layout (return paths, parasitics, coupling).
- **Treating EMC as a later problem** — self-desense is an RF performance problem from day one.
- **No test hooks** — without a conducted test port and a coupon, faults can't be isolated.

## How to simulate / verify
- Scripts referenced throughout: `pcb_stackup_widths.py`, `pcb_return_current.py`, `pcb_via_fence.py`, `pcb_layout_rules.py`, `pcb_launch.py`, `pcb_cavity_modes.py`, `pcb_emc_radiation.py`, `pcb_pdn.py`, `pcb_mixed_signal.py`, `pcb_thermal.py` (all in `tools/verify/`).
- EM simulation (openEMS/Sonnet) of the match region and launches when deviating from the reference at ≥ 2.4 GHz.

## Open questions / gaps
- The checklist has not yet been validated against a real Space Bar board review; expect additions after the next design cycle.

## Sources
1. This domain's pages (each item links to its supporting page and sources).
2. Texas Instruments SWRA640H (2024); Semtech AN1200.37/.40 (2018); Espressif ESP32-S3 hardware design guidelines; u-blox MAX-M5Q integration manual and GNSS antennas app note UBX-15030289 — reference-design and layout rules. (app notes)
3. H. W. Ott, *Electromagnetic Compatibility Engineering*, 2009; E. Bogatin, *Signal and Power Integrity — Simplified*, 2018. (textbooks)
4. MIL-STD-464C (2010) — EID RF safety margins. (standard)
5. Space Bar avionics knowledge base — flight-computer design lessons and engineering ethos. (internal)
