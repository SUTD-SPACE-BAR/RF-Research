---
title: Thermal management for RF boards — PA dissipation, exposed pads and thermal vias, copper spreading, junction temperature, and a 2 W LoRa module in a sealed rocket av-bay
domain: 13-pcb-rf-layout-emc
slug: thermal-management-rf
tags: [thermal, PA-dissipation, efficiency, junction-temperature, theta-JA, theta-JC, exposed-pad, thermal-via, spreading-resistance, copper-pour, natural-convection, radiation, thermal-time-constant, av-bay, duty-cycle, crystal-drift, TCXO, E22-400T33D, SX1262]
prerequisites:
  - vias-stitching-fencing.md
  - ../06-rf-circuits/power-amplifiers.md
related:
  - power-distribution-decoupling-for-rf.md
  - rf-layout-rules.md
  - jlcpcb-rf-manufacturing.md
  - ../04-real-components-hf/crystals-and-resonators.md
  - ../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md
  - ../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# Thermal management for RF boards

## Questions this page answers
- How much heat does my 2 W LoRa module or my PA chip produce while transmitting?
- How do I estimate a PA's junction temperature from θJA/θJC?
- How much do thermal vias under an exposed pad really help?
- Why is copper area (spreading) more important than via count once there are a few vias?
- Will an EBYTE E22-400T33D overheat in a sealed av-bay sitting on a hot launch pad?
- Why does my LoRa frequency drift during long packets, and how does layout fix it?
- When does a single packet heat the die appreciably?

## TL;DR
- **Heat = DC power − RF power out.** E22-400T33D at 33 dBm: 4.25–6 W in, 2 W out → **2.3–4 W of heat while transmitting**; E220-900T30D ≈ 2.1 W; SX1262 at +22 dBm ≈ 0.23 W; a 1 W FEM such as SKY66122 ≈ 2.2 W (script §1) [1][2].
- **$T_j=T_a+P\,\theta_{JA}$**, but θJA is a property of *your board*: for a 4 × 4 mm exposed-pad QFN on a 50 × 50 mm JLC 4-layer board in still air, a nodal model gives **≈ 42 K/W with no EPAD vias, 36 K/W with 4, 34 K/W with 9, 32.5 K/W with 16** — the same order as datasheet θJA values for such packages on JEDEC 4-layer boards (script §2–3).
- **Spreading and board-to-air dominate once there are a few vias**: one 0.3 mm via through 1.6 mm is ≈ 240 K/W, but 9 in parallel ≈ 26 K/W, while copper-plane spreading (35 µm: ≈ 24–32 K/W per plane from a 2 mm pad to 15–30 mm radius; 15 µm inner planes ≈ 2.3× worse) and the board-to-air term (≈ 14 K/W for 50 × 50 mm, h ≈ 14 W/m²K) remain. **More copper area and a conduction path to the structure beat more vias.**
- **Sealed av-bay**: a 26 g module (≈ 21 J/K) with ≈ 20 K/W to the bay air and ≈ 2 K/W from the bay to outside air reaches **≈ 123 °C steady state at 100 % TX duty (85 °C after ≈ 7 min), ≈ 77 °C at 50 %, ≈ 50 °C at 20 %** from a 32 °C pad ambient (lumped estimate; solar heating adds more) (script §4). The E22 is rated −40 to +85 °C [1]. **Limit TX duty/power on the pad, or give the module a conduction path to a metal bulkhead.**
- **Per-packet die heating is small** (0.25 W for 0.3 s: ≈ 2 K at the die; script §5); what drifts a LoRa crystal is the board warming over seconds: Semtech measured excessive drift at +22 dBm for packets > 0.4–0.5 s without thermal isolation of the crystal, and recommends a copper void around the XO or a TCXO [3][4].

## Intuition (no math)
A PA is a converter of DC power into RF power with an efficiency of ≈ 30–50 %; the rest becomes heat in a few square millimetres of silicon. That heat must travel: from the die into the package's exposed pad, from the pad through solder into the top copper, through vias into the internal planes, sideways through the copper to a large area, and finally from the board surfaces into the air (convection and radiation) or into whatever the board is bolted to. Each step is a thermal resistance (K/W), and the temperature rise is power times the sum.

The intuitive mistake is to focus on the first step (vias under the pad). A handful of vias already makes that step small; the large terms are usually the **sideways spreading** in thin copper and the **board-to-air** step, which depend on copper area and on what surrounds the board. In a rocket av-bay the air is still and enclosed, so the "air" is not a sink at all: it warms up with the electronics, and the real sink is the airframe wall and bulkheads.

Heat takes time to arrive: a module with a few tens of J/K of thermal mass and tens of K/W to its surroundings has a time constant of minutes. That is why short telemetry bursts are harmless while a long pad wait with continuous transmission is not.

## The math

### Level 1 — dissipation and junction temperature
$$P_{diss}=P_{DC}-P_{out}+P_{in}\approx P_{DC}(1-\eta),\qquad T_j=T_a+P_{diss}(\theta_{JC}+\theta_{CB}+\theta_{BA}).$$
Datasheet θJA values are measured on standardised (JEDEC) test boards; on your board the case-to-ambient part differs. θJC (die to exposed pad) is typically a few K/W for QFNs; θ of the solder joint is small if voiding is controlled.

### Level 2 — vias, spreading and board-to-air
**Via conduction**: $R_{via}=\ell/(k_{Cu}A_{wall})$, $A_{wall}=\pi[(d/2)^2-(d/2-t)^2]$; 0.3 mm drill, 20 µm wall: 236 K/W per via through 1.6 mm, 31 K/W through the 0.21 mm prepreg to L2 ([vias](vias-stitching-fencing.md) §6).

**Spreading in a copper plane** (thin disk source of radius $r_1$ in an annulus to $r_2$, heat leaving at $r_2$):
$$R_{spread}=\frac{\ln(r_2/r_1)}{2\pi k_{Cu}t}.$$
From a 2 mm pad: 35 µm plane to 15/30 mm radius 23.8/32.0 K/W; 15.2 µm (JLC inner 0.5 oz) 54.8/73.6 K/W (script §3). Four planes connected by vias in parallel ≈ 10 K/W.

**Board to air**: $R=1/(hA)$ with natural convection $h_c$ ≈ 5–10 W/m²K and radiation $h_r=4\varepsilon\sigma T^3$ ≈ 6 W/m²K (ε ≈ 0.9 soldermask, ≈ 330 K): a 50 × 50 mm board (both sides) ≈ 14 K/W.

**Nodal model** (script §2): pad → top-plane spreading, and pad → (vias ∥ prepreg conduction) → L2 → (vias through the core) → L3 → L4, each plane spreading to a board node → air. Result for a 4 × 4 mm EPAD on a 50 × 50 mm JLC-7628 board: θJA ≈ 42 / 36 / 34 / 32.5 K/W with 0 / 4 / 9 / 16 vias. Diminishing returns beyond ≈ 9 vias; the board-to-air 14 K/W and θJC 5 K/W don't change.

### Level 3 — transient heating, enclosure, and the crystal
**Lumped two-node model of a module in a closed bay** (script §4): module heat capacity $C_m=mc$ ≈ 0.026 kg × 800 J/kg·K ≈ 21 J/K; module-to-bay-air $R_{m}=1/(hA)$ with h ≈ 11 W/m²K (weak convection + radiation) over 2 × 37 × 60 mm → ≈ 20 K/W; bay contents (boards, bulkheads, part of the battery) ≈ 135 J/K; bay to outside through a 98 mm × 250 mm tube with h ≈ 6 W/m²K → ≈ 2 K/W. Time constants ≈ 7 min (module) and ≈ 5 min (bay). With the 4 W worst-case TX heat and $T_a$ = 32 °C:

| TX duty | average heat | module after 60 min | steady state | reaches 85 °C |
|---|---|---|---|---|
| 100 % | 4.0 W | 123 °C | 123 °C | ≈ 7 min |
| 50 % | 2.0 W | 77 °C | 77 °C | never |
| 20 % | 0.8 W | 50 °C | 50 °C | never |
| 5 % | 0.2 W | 37 °C | 37 °C | never |

These are lower bounds: a white airframe in Singapore sun can sit 10–30 °C above air temperature, and other heat sources (regulators, MCU) share the bay.

**Pulse heating of the die** (three-node ladder die/package/board, script §5): 0.25 W for 0.05/0.3/1/3 s raises the die by 1.4/2.4/3.9/5.1 K (steady state would be 11 K). Single packets don't threaten junctions; they do warm the local board over seconds.

**Crystal drift.** An XO a few millimetres from a 0.23 W radio chip warms by ≈ 0.3–1.4 K above the surrounding board in steady state (crude spreading estimate, script §6) — tenths of a ppm at a typical slope of ≈ 0.3 ppm/K near room temperature, ≈ 300 Hz at 915 MHz per 0.3 ppm. LoRa tolerates a frequency *drift within a packet* of only a fraction of a bin; Semtech's measurements show that at +22 dBm without isolation the drift exceeds the limit for packets longer than ≈ 0.4–0.5 s, hence copper voids around the XO on all layers or a TCXO [3][4] ([crystals](../04-real-components-hf/crystals-and-resonators.md), [LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)).

## Design equations & rules of thumb

| Quantity | Equation | Typical |
|---|---|---|
| Dissipation | $P_{DC}(1-\eta)$ | 2 W LoRa module: 2.3–4 W |
| Junction temp | $T_a+P\theta_{JA}$ | SX1262 +22 dBm: +8 K |
| Via (0.3 mm, 20 µm, 1.6 mm) | $\ell/(kA_{wall})$ | ≈ 240 K/W; N in parallel |
| Plane spreading | $\ln(r_2/r_1)/(2\pi kt)$ | 35 µm: ≈ 25–30 K/W; 15 µm: ≈ 55–75 K/W |
| Board to still air | $1/(hA)$, h ≈ 10–15 W/m²K | 50 × 50 mm: ≈ 14 K/W |
| EPAD vias | 5–9 × 0.3 mm, filled or small | diminishing returns beyond ≈ 9 |
| Module time constant | $RC$ | minutes |
| Crystal isolation | copper void around XO on all layers, or TCXO | Semtech [3][4] |

## Worked examples

### 1. SX1262 at +22 dBm on a JLC 4-layer board
Heat ≈ 0.23 W (DC-DC mode lowers it; Semtech shows DC-DC halves SX1261 consumption vs LDO, and that the SX1262 PA dissipates *less* heat at +22 dBm than at +14 dBm because it is optimised for full power [3]). With 9 EPAD vias θJA ≈ 34 K/W → $T_j$ ≈ $T_a$ + 8 K. Not a junction problem; it is a crystal-drift problem — isolate the XO or use a TCXO.

### 2. A discrete 1 W PA/FEM (SKY66122 class, 2.2 W heat)
Same board: 2.2 W × 34 K/W = +75 K → at 60 °C bay ambient, $T_j$ ≈ 135 °C — too hot for comfort. Improve: double the board area (board-to-air ≈ 7 K/W), use 1 oz inner planes (halves their spreading), 16+ EPAD vias with POFV, and most effectively **bolt the board's ground area to an aluminium bulkhead** with a thermal pad (≈ 1–3 K/W) — θJA ≈ 15 K/W → +33 K ([PA design](../06-rf-circuits/power-amplifiers.md)).

### 3. E22-400T33D on the pad
Pad wait 45 min with telemetry every second at SF9/125 kHz (≈ 0.3 s packets → ≈ 30 % duty): average ≈ 1.2 W → module ≈ 60 °C plus solar load. Options: (a) reduce TX power on the pad (the E22 has 24/27/30/33 dBm settings — at 27 dBm heat falls by roughly half for a ≈ 6 dB link-margin cost), (b) lower the update rate until launch detect, (c) mount the module so its metal shield touches a bulkhead or a copper pour stitched to the FC ground, (d) log the module temperature (or a nearby thermistor) — the Space Bar "record everything" ethos. During flight (minutes) the thermal time constant makes heating secondary.

### 4. Thermal vias vs copper area for an LDO feeding a PA
A 5 V → 3.3 V LDO carrying 0.5 A dissipates 0.85 W; in SOT-223 on a small pad θJA ≈ 60–100 K/W (typical datasheet range for minimum pads) → +50–85 K. Doubling the pad copper to ≈ 6 cm² with vias to L2/L3 roughly halves it; a buck converter removes most of the heat entirely ([PDN](power-distribution-decoupling-for-rf.md)).

## Practical notes
- **EPAD design**: follow the datasheet land pattern; 0.3 mm vias at 1.0–1.2 mm pitch in the pad; paste windows ≈ 50–70 % of the pad area in a grid (reduces float and voids); POFV if the vias are large or many ([JLCPCB](jlcpcb-rf-manufacturing.md)).
- **Inner planes are thin** at JLC (0.5 oz = 15 µm) — they spread heat poorly; 1 oz inner copper is an option for hot boards.
- **Keep heat away from the crystal, the GNSS module and sensors**: place the PA/module at the board edge near a mounting hole or bulkhead; void copper around the XO; don't put the barometer next to the PA (pressure sensors are temperature-compensated, but gradients across the package cause errors).
- **Thermal and RF ground are the same copper**: the stitched ground pour that spreads heat also gives the PA its RF ground — design both together.
- **Measure**: thermocouple or a small NTC epoxied to the module shield, logged during a bench soak at the flight duty cycle and in a closed box that mimics the av-bay; a thermal camera on an open board (emissivity of bare metal is low — measure on soldermask or tape).
- **Power handling of the RF trace itself** (loss, temperature rise, breakdown): [03 planar lines § power handling](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md#level-3--power-handling-of-rf-traces).

## Common mistakes & misconceptions
- **Using the datasheet θJA as if it were your board's.**
- **"More thermal vias always help"** — diminishing returns; spreading and board-to-air dominate.
- **Ignoring the enclosure**: still air in a sealed bay is not an infinite sink.
- **Leaving a 2 W radio transmitting continuously during a long pad wait.**
- **Putting the crystal next to the PA** — the classic LoRa drift problem.
- **Thermal-relief spokes on a PA's ground pad** to ease hand soldering — adds thermal and RF impedance.

## How to simulate / verify
- `python3 tools/verify/pcb_thermal.py` (seconds): dissipation table; nodal θJA model with 0–16 EPAD vias; plane spreading; sealed av-bay two-node transient vs duty cycle; three-node pulse heating; crystal-distance estimate.
- FEM: Elmer or the thermal solvers in commercial EDA for a real board outline; openEMS does not do thermal ([simulation tools](../16-simulation-tools/_index.md)).
- Bench: soak test in a closed foam box; log module temperature and LoRa frequency offset (SDR) over a long packet.

## Open questions / gaps
- Module heat capacity (800 J/kg·K), the bay convection coefficient (≈ 11 W/m²K) and the bay thermal mass are assumptions; a measured soak test of the actual av-bay would replace them.
- θJC = 5 K/W is a typical QFN value, not from a specific datasheet.
- The crystal temperature slope (≈ 0.3 ppm/K near 25 °C) is an assumed AT-cut-like value; use the actual crystal's curve.
- Solar heating of the airframe on a Singapore pad is not modelled.

## Sources
1. EBYTE, *E22-400T33D product specification / user manual* (v1.5) — 33 dBm, TX current 850–1200 mA, supply 2.3–5.5 V, operating temperature −40 to +85 °C (via LCSC/EBYTE listings and search summary); module mass/dimensions as summarised in [LoRa modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md). (datasheet)
2. Skyworks SKY66122-11 data (5 V, 640 mA, 1 W) as summarised in [power amplifiers](../06-rf-circuits/power-amplifiers.md). (datasheet)
3. Semtech, AN1200.37 *SX1261/2 Recommendations for Best Performance*, rev 1.1, 2018 — DC-DC vs LDO dissipation, SX1262 PA heat at +22 vs +14 dBm, PCB heating → crystal drift, top-layer cuts as thermal insulation, TCXO recommendations. (app note)
4. Semtech, AN1200.40 *SX1261/2 Reference Design Explanation*, rev 1.1, 2018 — copper void around the crystal on all layers; TCXO design for long packets. (app note)
5. JLCPCB, hole-wall plating ≈ 20–25 µm; inner copper 0.5 oz (15.2 µm) — [JLCPCB RF manufacturing](jlcpcb-rf-manufacturing.md). (manufacturer)
6. F. P. Incropera, D. P. DeWitt et al., *Fundamentals of Heat and Mass Transfer*, Wiley — conduction in annuli, natural convection coefficients, radiation linearisation. (textbook; from knowledge)
7. JEDEC JESD51 series (θJA test boards and definitions) — why datasheet θJA differs from the application board. (standard; from knowledge)
8. Space Bar avionics knowledge base — engineering ethos (record everything) and flight-computer architecture (E22 on the primary FC). (internal)
9. Verification script `tools/verify/pcb_thermal.py` (this page).
