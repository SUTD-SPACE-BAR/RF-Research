---
title: Package parasitics — bondwires, leads, exposed pads and ground pins
domain: 04-real-components-hf
slug: package-parasitics-bondwires
tags: [package-parasitics, bondwire, lead-inductance, qfn, exposed-pad, soic, tssop, bga, flip-chip, ground-pins, ground-bounce, source-degeneration, rfic-layout]
prerequisites:
  - pcb-parasitics-traces-vias-pads.md
  - ../01-circuit-theory/lumped-elements-impedance-admittance.md
related:
  - component-models-s2p-spice.md
  - ../05-analog-electronics/amplifier-topologies.md
  - ../06-rf-circuits/lna-design.md
  - ../06-rf-circuits/power-amplifiers.md
  - ../06-rf-circuits/amplifier-stability-and-biasing.md
  - ../13-pcb-rf-layout-emc/grounding-and-return-paths.md
  - ../13-pcb-rf-layout-emc/rf-layout-rules.md
  - ../15-lora-ism-radios/semtech-chip-family.md
level: intermediate
confidence: medium
last_updated: 2026-09-27
---

# Package parasitics — bondwires, leads, exposed pads and ground pins

## Questions this page answers
- How much inductance does a bondwire have? Is "1 nH per mm" right?
- How much lead inductance do SOIC, TSSOP and QFN packages have?
- Why do RF ICs (LoRa transceivers, LNAs, PAs) have so many ground pins and a big exposed pad?
- How should I connect a QFN exposed pad to ground, and how many vias does it need?
- What does ground inductance do to an amplifier's gain and stability?
- Why is a PA's ground connection so critical?
- Why do RF parts come in QFN/BGA/flip-chip rather than SOIC?

## TL;DR
- **Bondwire** (isolated, HF): $L=\frac{\mu_0\ell}{2\pi}\left[\ln\frac{2\ell}{r}-1\right]$: a 1 mm, 25 µm gold wire is **0.82 nH**; 0.5 mm → 0.34 nH; 2 mm → 1.91 nH — so "≈1 nH/mm" is a fair rule for 1–2 mm wires far from ground. Low over a ground paddle (image effect) it is less: 1 mm at 50–100 µm height ≈0.41–0.55 nH. Two wires in parallel don't halve L: at 100 µm pitch (L+M)/2 = 0.62 nH vs 0.41 nH ideal.
- **Package leads (TI, 20-pin averages):** SOIC 5.0 nH / 0.72 pF, SSOP 3.5 nH, TSSOP 2.8 nH, TVSOP 2.6 nH, **QFN 1.18 nH / 0.25 pF** (16-pin QFN 0.82 nH). At 915 MHz 5 nH is **29 Ω** — which is why RF chips are QFN/BGA/flip-chip.
- **Ground inductance hurts twice:** (1) *degeneration* — a common-source stage with gm = 50 mS loses 0.34 dB (1 nH) at 915 MHz and 2 dB at 2.45 GHz, and the phase shift can cause instability; (2) *ground bounce/coupling* — 0.5 A of PA current through 0.5 nH at 915 MHz develops **1.4 V peak** of RF across the "ground", coupling into everything sharing it.
- **Many ground pins + exposed pad** put many small inductances in parallel and separate the ground currents of different blocks inside the package.
- **QFN exposed pad:** on a 4-layer board with the EP stitched to L2 by ~9 vias the PCB part of the ground path is ≈3 pH; on a 1.6 mm 2-layer board ≈0.2 nH (coupled vias). The downbonds inside the package then dominate (≈0.1–0.6 nH). Use the vendor's recommended via pattern (Semtech's SX126x reference layouts use a dense via array under the EP).
- Flip-chip and "HotRod" packages remove bondwires: TI measured ≈1.0 nH vs 1.4 nH switching-loop inductance for flip-chip vs standard QFN of the same converter.

## Intuition (no math)
Inside a plastic IC package, the silicon die is connected to the package terminals by fine wires (bondwires, 18–50 µm diameter, 0.5–3 mm long) or, in flip-chip packages, by solder bumps. Then the terminals (leads or pads) connect to the PCB. Every millimetre of that path is inductance, and at UHF a nanohenry is several ohms — comparable to the impedances inside an RF circuit (a PA's optimum load is a few ohms; a 50 Ω input sees gate/base impedances of tens of ohms).

The most sensitive connection is **ground**. An RF transistor's "source" or "emitter" is only as grounded as its bondwires and pins allow. Inductance there feeds a voltage back into the input (negative feedback, reducing gain; with the wrong phase it can cause oscillation), and if several circuits share it, the large current of one (a PA) creates a voltage that the others see as signal. Chip designers fight this with many parallel ground bondwires, separate ground pins for each block, and a large exposed pad soldered to the PCB ground right under the die — and they expect you to finish the job with a solid, via-dense ground on the board.

## The math

### Level 1 — bondwire and lead numbers
Straight isolated round wire (Grover; see [PCB parasitics](pcb-parasitics-traces-vias-pads.md)): $L=\frac{\mu_0\ell}{2\pi}\left[\ln\frac{2\ell}{r}-1+\frac r\ell\right]$ (add $+\tfrac14$ inside the bracket at DC). Values from `tools/verify/components_bondwire.py` §1:

| Wire diameter | 0.5 mm | 1.0 mm | 1.5 mm | 2.0 mm |
|---|---|---|---|---|
| 18 µm | 0.37 nH | 0.88 | 1.44 | 2.04 |
| 25 µm | 0.34 | 0.82 | 1.35 | 1.91 |
| 33 µm | 0.31 | 0.76 | 1.26 | 1.80 |
| 50 µm | 0.27 | 0.68 | 1.14 | 1.64 |

Package lead parasitics (TI QFN comparison tables; averages over pins) and their reactance:

| Package | L | C | X_L @ 433.92 / 915 / 2450 MHz |
|---|---|---|---|
| SOIC-20 | 5.01 nH | 0.72 pF | 13.7 / 28.8 / 77 Ω |
| SSOP-20 | 3.50 nH | 0.42 pF | 9.5 / 20.1 / 54 Ω |
| TSSOP-20 | 2.81 nH | 0.32 pF | 7.7 / 16.1 / 43 Ω |
| TVSOP-20 | 2.56 nH | 0.34 pF | 7.0 / 14.7 / 39 Ω |
| QFN-20 | 1.18 nH | 0.25 pF | 3.2 / 6.8 / 18 Ω |
| QFN-16 | 0.82 nH | 0.24 pF | 2.2 / 4.7 / 12.6 Ω |

### Level 2 — geometry effects
- **Height over ground.** A wire at height $h$ above a return plane has loop inductance $L=\frac{\mu_0\ell}{2\pi}\cosh^{-1}(h/r)$: 1 mm of 25 µm wire at 50/100/200/400 µm → 0.41/0.55/0.69/0.83 nH. Low, short loops over the paddle are lower-inductance than tall arcs.
- **Arc length.** A 1 mm span with 150 µm loop height has ≈1.06 mm of wire → 0.88 nH instead of 0.82 nH.
- **Parallel wires.** Two identical wires with mutual inductance $M$: $L_{eff}=(L+M)/2$. For 1 mm wires at 50/100/200/500 µm pitch: 0.68/0.62/0.56/0.49 nH vs the ideal 0.41 nH. Fanning wires out (different directions) reduces $M$.
- **DC and RF resistance.** Au 1 mm × 25 µm: 50 mΩ DC; at 915 MHz (skin depth 2.6 µm) ≈0.12 Ω, i.e. Q ≈ 40 for the wire alone. Cu 1 mm × 50.8 µm: ≈8.3–8.6 mΩ DC (TI quotes 8.6 mΩ) — why power ICs use many Cu wires or flip-chip.

### Level 3 — effects on circuits
**Source/emitter degeneration.** A transconductance stage with a common-lead inductance $L_s$: $A_v=-g_mR_L/(1+j\omega g_mL_s)$ (ignoring $C_{gs}$ current). For $g_m=50$ mS: $L_s=1$ nH costs 0.08 / 0.34 / 2.0 dB at 434 / 915 / 2450 MHz; 2 nH (an SOT-23 ground lead plus via) costs 1.2 dB at 915 MHz and 5.3 dB at 2.45 GHz. Degeneration also creates a real input resistance $g_mL_s/C_{gs}=\omega_TL_s$ — deliberately used in LNAs for noise-and-gain matching ([LNA design](../06-rf-circuits/lna-design.md)) — but when it is *parasitic and uncontrolled*, it shifts match and stability ([stability](../06-rf-circuits/amplifier-stability-and-biasing.md)).

**Ground bounce and common-impedance coupling.** RF current $I$ through a shared ground inductance $L_g$ produces $V=I\omega L_g$: 0.5 A at 915 MHz through 0.5 nH → 1.44 V peak; through 0.1 nH → 0.29 V; 1 A through 0.5 nH → 2.9 V. A transceiver whose PA, VCO and LNA share such an impedance would couple PA output into the VCO (pulling) or the receiver. That is why transceiver ICs split ground pins per block and why the exposed pad is the main PA ground.

**Exposed pad (EP) ground path.** Die → downbonds to the paddle (≈0.56 nH for one 0.6 mm wire; ≈0.14 nH for four and ≈0.07 nH for eight with a rough mutual-coupling allowance) → solder → PCB via array. Script §3: with 4 downbonds, the total is ≈0.34 nH on a 2-layer 1.6 mm board (9 coupled vias ≈0.2 nH) vs ≈0.14 nH on a 4-layer board with vias to L2. The PCB contribution can be made negligible — the internal part is fixed by the IC designer and already accounted for in the datasheet's reference design.

**Package capacitance** (0.2–0.7 pF per pin) adds to every RF pin's matching network; with lead inductance it resonates (SOIC: ≈2.7 GHz; QFN: ≈9 GHz), setting an upper frequency for leaded packages.

**Flip-chip / WLCSP / BGA** replace wires with bumps and balls of much lower inductance; TI's HotRod flip-chip QFN measured ≈1.0 nH vs 1.4 nH switching-loop inductance for the bondwire QFN of the same converter (loop includes PCB and capacitors).

## Design equations & rules of thumb

| Item | Rule | Value |
|---|---|---|
| Bondwire | $\frac{\mu_0\ell}{2\pi}[\ln(2\ell/r)-1]$ | ≈0.8–0.9 nH per mm for 1–2 mm |
| Wire over paddle | $\frac{\mu_0\ell}{2\pi}\cosh^{-1}(h/r)$ | 1 mm @ 100 µm: 0.55 nH |
| Two wires in parallel | $(L+M)/2$ | ≥ 0.6 L at typical pitch |
| Lead L | SOIC 5, TSSOP 2.8, QFN 0.8–1.2 nH | TI tables |
| Degeneration loss | $|1+j\omega g_mL_s|$ | 1 nH, 50 mS, 915 MHz: 0.34 dB |
| Ground bounce | $V=I\omega L$ | 0.5 A, 0.5 nH, 915 MHz: 1.4 V |
| EP vias | as many as the vendor layout shows; 4-layer with L2 ground | PCB part ≪ 0.1 nH |

## Worked examples

### 1. Choosing a package for a 915 MHz discrete LNA
An SOT-23 transistor's emitter/source lead plus its via (≈1.5–2 nH total) degenerates a 50 mS device by ≈1 dB at 915 MHz and adds unpredictable feedback; a 4-pin SOT-343 or a QFN/DFN MMIC with multiple ground leads (and ideally an exposed pad) keeps it < 0.5 nH. Use the device's S-parameters *including* its package and the vendor's recommended footprint.

### 2. SX126x/SX127x layout on a JLCPCB 4-layer board
Follow the Semtech reference layout: EP soldered with a dense via array to an unbroken L2 ground, every GND pin connected with its own via, decoupling capacitors at each supply pin with their own vias. With 0.21 mm prepreg the vias contribute a few pH; on a 2-layer board, each via is ≈0.5 nH and the shared ground impedance would be tens of times larger — one reason 2-layer transceiver boards show worse sensitivity and spurs ([Semtech chip family](../15-lora-ism-radios/semtech-chip-family.md)).

### 3. A 2 W module's ground
A 2 W PA at 433 MHz may carry ~0.5–1 A of RF current in its output/ground loop. If the module's ground pads connect to the carrier board through two small vias on a 2-layer board (≈0.4 nH), that is ≈0.5–1 V of RF on "ground" — enough to couple into a GNSS receiver or IMU wiring. Give modules a solid ground pour with many vias under and around their ground pads.

## Practical notes
- **Datasheet reference designs already include the package**; copying the footprint and via pattern exactly is the cheapest way to get datasheet performance.
- **Don't route under the EP** or break the ground under RF ICs; keep the EP via array filled/tented per assembler advice (JLCPCB offers via-in-pad filling for fine-pitch parts).
- **Separate grounds by path, not by splitting planes**: keep noisy currents (PA, switching regulator) physically away from sensitive returns on the same continuous plane ([grounding](../13-pcb-rf-layout-emc/grounding-and-return-paths.md)).
- **Measuring**: package parasitics are best taken from vendor S-parameters or IBIS/package models; a TDR on the board with and without the part reveals pad/lead effects ([TDR](../03-transmission-lines-matching/time-domain-reflectometry.md)).

## Common mistakes & misconceptions
- **"Ground is ground."** At 915 MHz 0.5 nH is 2.9 Ω; with amps of RF current, ground has volts on it.
- **Using leaded (SOIC/TSSOP) packages above a few hundred MHz** and expecting datasheet gain/stability.
- **Too few EP vias** or leaving the EP unsoldered (voids) — raises PA ground inductance and thermal resistance.
- **Assuming N bondwires/vias give L/N** — mutual coupling limits the benefit.
- **Ignoring package capacitance** in matching networks for sub-pF-sensitive designs at 2.4 GHz.

## How to simulate / verify
- `python3 tools/verify/components_bondwire.py` — bondwire L tables, height/arc/parallel effects, package-lead reactance, EP ground path estimates, degeneration and ground-bounce numbers, bondwire resistance.
- Simulate transistors with vendor S-parameters that include the package, or add package L/C explicitly to a die model; EM-simulate the EP via array for PAs ([EM solvers](../16-simulation-tools/em-solvers-fdtd-mom-fem.md)).

## Open questions / gaps
- Downbond counts and lengths inside specific RF ICs (SX126x, SX127x) are not published; the EP estimates use assumed geometry (confidence medium).
- BGA ball and WLCSP bump inductances are not quantified here (vendor package models needed).

## Sources
1. Texas Instruments, "Quad flat no-lead (QFN) package comparison tables" — average lead R, L, C for SOIC/SSOP/TSSOP/TVSOP/QFN (14/16/20-pin). https://www.ti.com/pdfs/logic/qfncompare.pdf (manufacturer data)
2. A. Fagnani, "Understanding flip chip QFN (HotRod™) and standard QFN performance differences," TI Application Report SLVAEE1, July 2019 — bondwire resistance (Cu 1 mm × 50.8 µm ≈ 8.6 mΩ), loop inductance 1.0 vs 1.4 nH. https://www.ti.com/lit/pdf/slvaee1 (app note)
3. F. W. Grover, *Inductance Calculations*, Dover — straight-wire and parallel-filament mutual inductance. (textbook)
4. "Bond wire and its characterization at RF frequencies," *High Frequency Electronics* (rule of thumb ≈1 nH/mm; parallel/flat wires lower inductance). https://www.highfrequencyelectronics.com (industry article; content not fully retrieved — rule of thumb cross-checked by calculation)
5. T. H. Lee, *The Design of CMOS Radio-Frequency Integrated Circuits*, 2nd ed., Cambridge UP, 2004 — bondwire inductance, source degeneration, package effects. (textbook)
6. Semtech, "SX1261/2 data sheet," rev. 1.2, 2019 — QFN 4×4 mm package; reference design practice; thermal note about PCB heat paths. (datasheet)
7. Verification script `tools/verify/components_bondwire.py` (this KB).
