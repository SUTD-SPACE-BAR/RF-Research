---
title: RF connectors and board launches — SMA edge launch, U.FL/IPEX, coax-to-microstrip transitions and return-loss budgets
domain: 13-pcb-rf-layout-emc
slug: connectors-and-launches
tags: [SMA, edge-launch, end-launch, U.FL, IPEX, MHF, W.FL, connector-footprint, ground-cut-out, antipad, pad-capacitance, transition, vertical-launch, return-loss-budget, mismatch-loss, mating-cycles, pigtail]
prerequisites:
  - ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md
  - ../04-real-components-hf/pcb-parasitics-traces-vias-pads.md
  - stackups-and-materials.md
related:
  - ../03-transmission-lines-matching/coax-and-cables.md
  - grounding-and-return-paths.md
  - vias-stitching-fencing.md
  - rf-layout-rules.md
  - ../18-components-parts/connectors-and-cables-parts.md
  - ../17-test-measurement/fixtures-and-deembedding.md
level: mixed
confidence: medium
last_updated: 2026-10-14
---

# RF connectors and board launches

## Questions this page answers
- Why does my SMA edge connector show bad return loss at 2.4 GHz even though the trace is 50 Ω?
- Should I cut the ground plane under the SMA or U.FL signal pad, and on which layers?
- How good is a U.FL, how many times can I plug it, and up to what frequency?
- What is a return-loss budget and how do connector, launch, trace and pads add up?
- Why do vertical (through-hole) SMAs perform worse than edge-launch ones above a few GHz?
- How much loss does a U.FL pigtail add at 433 MHz, 915 MHz, GNSS L1, 2.4 and 5.8 GHz?
- How should I place ground vias around an RF connector footprint?
- Is it better to use an SMA on the board or a U.FL-to-SMA bulkhead pigtail in a rocket?
- Can I rotate the antenna connector footprint 90° (or 45°) without ruining the signal?

## TL;DR
- **A connector pad is a short, wide transmission line.** On JLC04161H-7628 an edge-launch SMA pad 1.3 × 3 mm sits 0.21 mm above L2: Z_pad ≈ 22 Ω, RL only **12 dB at 2.45 GHz, 6 dB at 5.8 GHz**. **Voiding L2 (and keeping L3 solid) under the pad** raises Z_pad to ≈ 69 Ω and RL to **21 dB at 2.45 GHz, 14 dB at 5.8 GHz** (script §2). A 3-D openEMS model of the same pad (2026-10-13, `tools/verify/sim2_openems_pcb.py`) agrees: **11.4 dB intact, 21 dB voided at 2.45 GHz** (5.7 / 15.5 dB at 5.8 GHz), so the 1-D line-section estimate holds to ≈ 0.5–1 dB.
- **Shunt capacitance rule**: $|\Gamma|\approx\omega CZ_0/2$. 0.1 pF of excess pad capacitance is negligible at UHF (RL > 30 dB at 915 MHz) but 0.65 pF limits RL to 12 dB at 2.45 GHz (script §1).
- **Some pad capacitance is good**: it compensates the series inductance of the pin/solder transition. A 0.5 nH transition is exactly matched by 0.2 pF ($C=L/Z_0^2$) — the basis of "tune the pad width" in launch optimisation (script §4).
- **U.FL (Hirose)**: DC–6 GHz, VSWR ≤ 1.3 to 3 GHz / ≤ 1.4 to 6 GHz, **≈ 30 mating cycles** [1]; its small signal pad is benign on 4-layer boards (RL 32 dB at 915 MHz with L2 intact) — the mated connector (RL ≥ 17.7 dB) dominates.
- **1.13 mm U.FL pigtail loss ≈ 0.14/0.21/0.27/0.34/0.52 dB per 100 mm** at 433/915/1575/2450/5800 MHz (Hirose 3.73 dB/m at 3 GHz scaled ∝ √f; reproduces Hirose's 6 GHz figure within 3 %) (script §6).
- **Return-loss budget**: U.FL (Γ 0.13) + launch (0.056) + 55 Ω line (0.048) + DC-block pads (0.032) → **RSS RL 16.3 dB (0.10 dB mismatch loss); worst case 11.5 dB (0.32 dB)**. For a LoRa or GNSS link these are small; for a PA they set the load-pull (power and harmonics).
- **Vertical launches**: a through-board barrel behaves like coax: $Z=\frac{60}{\sqrt{\varepsilon_r}}\ln(D/d)$ — a 0.9 mm barrel needs a ≈ 5 mm ground ring/antipad for 50 Ω in FR-4; typical un-optimised footprints are ≈ 20–30 Ω (capacitive) (script §5).
- **Ground the connector body right at the board edge**: via rows along both sides of the launch, first vias within ≈ 0.5–1 mm of the pad; rows of vias at gap < λ/4 (in the dielectric) of the highest frequency form a "wall" [2].

## Intuition (no math)
A coaxial connector is a perfect 50 Ω transmission line until the point where its centre pin meets the board. There, the geometry changes abruptly: the pin (≈ 0.76–1.3 mm wide for SMA) sits on a pad that is often much wider than the 50 Ω trace, the connector's ground body touches the board's ground only at a few tabs or pads, and the return current has to find its way from the round coax shield into the flat ground plane. Each of these produces a small reflection: **excess capacitance** where metal is wide and close to the plane, **excess inductance** where the current path (pin or return) is narrow or detours.

The fix is to make the transition look like 50 Ω over as short a length as possible. On a thin-prepreg 4-layer board the pad is far too capacitive, so you **remove the ground plane directly under it** (the pad then references a deeper layer and becomes less capacitive). On a thick 2-layer board the trace is wider than the pin and the problem is the opposite (inductive neck-down), so you **use CPWG** near the connector to bring the 50 Ω width close to the pad width. In both cases, **the connector's ground must be tied to the board's ground planes with many vias right at the edge**, so the return current does not wander.

At 433 and 915 MHz most of this is second-order — a modest launch still gives > 20 dB return loss. It starts to matter at GNSS L1, is important at 2.4 GHz, and dominates at 5.8 GHz and above.

## The math

### Level 1 — single discontinuities
**Shunt capacitance** $C$ on a line of $Z_0$: $\Gamma=-\frac{j\omega CZ_0}{2+j\omega CZ_0}$, so $|\Gamma|\approx\omega CZ_0/2$ when small. Script §1:

| Excess C | 433 MHz | 915 MHz | 1575 MHz | 2.45 GHz | 5.8 GHz |
|---|---|---|---|---|---|
| 0.1 pF | 43 dB | 37 dB | 32 dB | 28 dB | 21 dB |
| 0.3 pF | 34 dB | 27 dB | 23 dB | 19 dB | 12 dB |
| 0.65 pF | 27 dB | 20 dB | 16 dB | 12 dB | 6 dB |
| 1.0 pF | 23 dB | 17 dB | 12 dB | 9 dB | 3 dB |

(RL values; excess pad capacitances for 0402/0603/SMA pads on JLC stackups are on the [PCB parasitics page](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md): 0402 ≈ +0.02 pF, 0603 ≈ +0.10 pF, SMA pad ≈ +0.65 pF on 0.21 mm prepreg.)

**Series inductance** $L$: $|\Gamma|\approx\omega L/(2Z_0)$ — 0.5 nH gives RL 22 dB at 2.45 GHz, 15 dB at 5.8 GHz (script §4).

### Level 2 — the pad as a line section, and compensation
A pad of width $W_p$ and length $\ell$ is a line of impedance $Z_p$ (from the microstrip formulas with the pad's height to its reference) and electrical length $\beta\ell$. Its reflection in a 50 Ω system follows from the ABCD matrix; for $\beta\ell\ll1$ it reduces to a shunt $C\approx\ell\sqrt{\varepsilon_{eff}}/(cZ_p)$ minus the line's own capacitance. Script §2 for a 1.3 × 3 mm SMA pad on JLC-7628:

| Reference plane under pad | Z_pad | RL @ 915 MHz | 2.45 GHz | 3.5 GHz | 5.8 GHz |
|---|---|---|---|---|---|
| L2 (0.21 mm) | 21.5 Ω | 19.7 dB | 11.6 dB | 8.9 dB | 5.7 dB |
| L2 voided → L3 (≈ 1.29 mm) | 68.6 Ω | 29.6 dB | 21.1 dB | 18.2 dB | 14.3 dB |
| L2 + L3 voided → L4 (≈ 1.52 mm) | 74.5 Ω | 27.6 dB | 19.2 dB | 16.2 dB | 12.4 dB |

**3-D check with openEMS** (W5-S11, 2026-10-13; `tools/verify/sim2_openems_pcb.py pad`, [openEMS workflow Run 4b](../16-simulation-tools/openems-workflow.md)). Same 1.3 × 3.0 mm pad between two 50 Ω lines on JLC04161H-7628 (prepreg 0.2104 mm, εr 4.4; core 1.065 mm, εr 4.55). The void extends 0.4 mm beyond the pad, L3 stays solid, and four stitching vias tie L2 to L3 around the void. The connector is modelled as a matched continuation (no pin or body), so this checks the pad, not the transition inductance.

| Case (mesh 1 / 2 / 3) | RL @ 915 MHz | 1.575 GHz | 2.45 GHz | 5.8 GHz |
|---|---|---|---|---|
| L2 intact | 19.5 / 19.7 / — dB | 15.1 / 15.0 | **11.5 / 11.4** | 5.5 / 5.7 |
| L2 voided | 28.5 / 29.2 / 29.8 dB | 24.3 / 24.7 / 24.8 | **21.2 / 21.3 / 20.9** | 16.2 / 15.5 / 15.5 |

The 1-D table above is confirmed within 0.2 dB (intact) and 0.2–1.2 dB (voided); at 5.8 GHz the void does slightly better than the 1-D estimate (15.5 vs 14.3 dB). Pre-registered ranges P1–P3 all passed. The mesh-3 run of the intact case stalled and is missing. Two side findings: (1) the void excites the L2–L3 parallel-plate region, which in the simulation needed absorbing side walls and in hardware needs **plenty of stitching vias around every void**; (2) an earlier pad series with the port inside the PML gave mesh-inconsistent numbers and was discarded. Simulation only; not yet measured on a coupon.

Voiding one layer is enough; voiding two over-shoots (the pad becomes inductive) and removes the reference that ties the connector's ground tabs to the internal planes.

**Compensation.** A transition that has series inductance $L$ (pin, solder, the return current's detour from the connector body to the board) followed by shunt capacitance $C$ (pad) is an L–C "artificial line" of impedance $\sqrt{L/C}$ and cutoff $\approx1/(\pi\sqrt{LC})$. If $C=L/Z_0^2$ the transition is matched up to a large fraction of the cutoff: $L$ = 0.5 nH → $C$ = 0.2 pF, cutoff ≈ 32 GHz; RL rises from 15 dB to > 40 dB at 5.8 GHz in the lumped model (script §4). That is why optimised launches (Southwest Microwave, Rogers) **taper** the trace at the pad and tune the ground gap rather than simply shrinking everything [2][3].

### Level 3 — vertical launches, ground walls, and budgets
**Vertical (through-hole or surface-mount "PCB-mount" SMA) launches** carry the signal through the board on a barrel surrounded by ground pins/vias; the barrel-in-ring structure is a coax with $Z\approx\frac{60}{\sqrt{\varepsilon_r}}\ln\frac{D}{d}$ ($D$ = effective ground-ring/antipad diameter, $d$ = barrel). 50 Ω in FR-4 needs $D/d\approx5.75$: 2.9 mm for a 0.5 mm barrel, 5.2 mm for 0.9 mm (script §5). Typical footprints with ≈ 2 mm antipads are ≈ 20–30 Ω and, together with the 90° bend and the via stub, are usable to ≈ 2–3 GHz without optimisation. For higher frequencies prefer edge-launch or a surface-mount connector designed for the stackup.

**Ground walls around the launch.** The connector's ground tabs and the board's top ground must be tied to the internal planes at the edge with via rows. Southwest Microwave treats a via row as a wall when the edge-to-edge gap is below a quarter-wavelength in the dielectric at the highest frequency (their 50 GHz boards: 0.029" edge-to-edge gaps ↔ λ/4 at 53 GHz in RO4350B; the via diameter/pitch quoted alongside in the summary we read are inconsistent with that gap) [2]. At UHF–5.8 GHz on FR-4 this is easily met; the practical rule is **vias every 1–2 mm along both edges of the launch for the first 5–10 mm**, closer near the pad ([vias, stitching and fencing](vias-stitching-fencing.md)).

**Return-loss budget.** Reflections from several discontinuities add with phases that depend on their spacing and frequency. Bounds: worst case $|\Gamma|\le\sum|\Gamma_i|$; for random phases, $|\Gamma|\approx\sqrt{\sum|\Gamma_i|^2}$. Mismatch loss $=-10\log_{10}(1-|\Gamma|^2)$ ([reflections page](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md)). Script §6 budget for a 915 MHz – 2.4 GHz front end: U.FL 0.130, launch 0.056, ±10 % line 0.048, DC-block pads 0.032 → worst |Γ| = 0.266 (RL 11.5 dB, VSWR 1.72, 0.32 dB), RSS 0.153 (RL 16.3 dB, VSWR 1.36, 0.10 dB).

## Design equations & rules of thumb

| Quantity | Equation | Typical |
|---|---|---|
| Shunt C discontinuity | $\lvert\Gamma\rvert\approx\omega CZ_0/2$ | 0.3 pF → 19 dB @ 2.45 GHz |
| Series L discontinuity | $\lvert\Gamma\rvert\approx\omega L/(2Z_0)$ | 0.5 nH → 22 dB @ 2.45 GHz |
| Compensated L–C | $C=L/Z_0^2$ | 0.5 nH ↔ 0.2 pF |
| Coaxial via / vertical launch | $Z=\frac{60}{\sqrt{\varepsilon_r}}\ln(D/d)$ | FR-4: D/d ≈ 5.75 for 50 Ω |
| Pad reference void | void L2 under pads wider than ≈ 2× the 50 Ω trace on thin prepreg | SMA, U.FL on 5.8 GHz boards, RF module pads |
| Via wall at launch | edge-to-edge gap < λ_d/4 (bound); use 1–2 mm pitch | [2] |
| Budget | worst $\sum\lvert\Gamma_i\rvert$, typical $\sqrt{\sum\lvert\Gamma_i\rvert^2}$ | RSS RL ≈ 16 dB |
| U.FL | VSWR ≤ 1.3 (≤ 3 GHz), 30 cycles | [1] |

## Worked examples

### 1. SMA edge-launch on a JLC 4-layer 2.4 GHz board
Trace 0.359 mm (50 Ω on JLC04161H-7628, εr 4.4, soldermask over the trace — [canonical width table](stackups-and-materials.md#canonical-50-ω-width-table)), SMA centre-pin pad 1.3 × 3 mm. Without a void: 11.6 dB RL at 2.45 GHz — the connector alone may be ≈ 20–25 dB, so the pad is the dominant reflection. Void L2 under the pad (and ≈ 0.3–0.5 mm beyond its edges), keep L3 solid as the pad's reference, place 2–3 GND vias on each side of the pad tying the top-layer GND tabs to L2 and L3, and taper the trace into the pad over ≈ 1 mm: predicted 21 dB at 2.45 GHz (1-D model 21.1 dB; openEMS 3-D 20.9–21.3 dB without the taper, against 11.4 dB with L2 intact). Verify with a VNA on a thru coupon (two connectors back-to-back) and use [TDR](../03-transmission-lines-matching/time-domain-reflectometry.md) to see whether the residual is capacitive (dip) or inductive (peak).

### 2. U.FL on the flight computer's GNSS input
MAX-M10S RF_IN → 8 mm of 50 Ω → U.FL. On JLC-7628 the U.FL signal pad (≈ 1 × 1 mm) with L2 intact gives 27 dB RL at 1575 MHz; the mated U.FL itself (VSWR ≤ 1.3 → 17.7 dB) dominates. **No void needed at L1.** Loss: 8 mm of trace (0.07 dB) + U.FL + 150 mm of 1.13 mm pigtail (0.4 dB) → ≈ 0.5 dB before an active antenna's LNA — irrelevant with a 20–30 dB active antenna, but 0.5 dB of noise figure with a passive patch ([GNSS antennas](../08-antennas/gnss-antennas.md)).

### 3. Pigtails in the av-bay: U.FL-to-SMA bulkhead vs board SMA
Space Bar boards use modules with SMA outputs (EBYTE E22/E220) and U.FL GNSS. The U.FL is rated ≈ 30 mating cycles [1] and its retention is by spring fingers — in a vibration environment secure it (retention clip, adhesive, or strain relief so the cable cannot lever the plug off). A board-mounted SMA (edge or vertical) survives ≈ 500 cycles and holds torque; a U.FL-to-SMA pigtail to a bulkhead costs 0.2–0.5 dB at 433–2450 MHz per 100–150 mm but decouples antenna-cable forces from the PCB. For telemetry at 433/915 MHz the loss is negligible; prefer robustness.

### 4. A tight 5.8 GHz budget
5.8 GHz video TX: PA → 10 mm line → SMA. U.FL-class connectors near 6 GHz have VSWR ≤ 1.4 (Γ 0.167); an unvoided SMA pad on thin prepreg gives RL 5.7 dB (Γ 0.52!) — the PA sees VSWR 3:1 at its output, losing power and changing harmonics. With the L2 void: RL 14 dB (Γ 0.19). Either optimise in openEMS or choose a 2-layer Rogers board (JLC HF service, 0.508 mm RO4350B: 50 Ω = 1.07 mm, close to the SMA pin pad width).

## Practical notes
- **Use the connector vendor's recommended footprint for the stackup it was designed on**, then adapt: most SMA edge-launch drawings assume 1.6 mm 2-layer FR-4 or 0.76 mm Rogers. On thin-prepreg 4-layer boards you must add the plane void yourself.
- **Void geometry**: in KiCad draw a rule area (keep-out: no copper/zones) on L2 under the pad, extended ≈ 0.3–0.5 mm (≈ 1.5–2.5h) beyond the pad; keep L3 solid; add GND vias around the void perimeter so the L2 edge is tied to L3.
- **Edge connector alignment**: board edge tolerance (JLC routing ±0.2 mm class) leaves a gap between connector and pad — keep the pad long enough (≥ 2 mm) for solder, and keep the connector body tabs soldered on both sides of the board where the part allows it.
- **U.FL/IPEX families**: Hirose U.FL (1.9–2.4 mm mated height), W.FL (smaller), IPEX MHF I (U.FL-compatible), MHF4 (smaller, 0.81 mm cable, not mateable with U.FL). Check the mating family before ordering pigtails. Use the connector's datasheet footprint; many modules' U.FL layouts include a GND keep-out under the signal pad on 2-layer boards.
- **ESD on connectors**: an external antenna port is an ESD entry point; use a low-capacitance TVS (< 0.5 pF, as u-blox recommends for GNSS RF_IN) or a DC-shorted antenna/λ/4 stub at UHF ([EMC](emc-emi-fundamentals.md)).
- **Mechanical**: in a rocket, SMA bulkheads and jam-nut mounts transfer antenna loads to the airframe, not the PCB; U.FL connections need retention.
- **Rotating or angling a connector footprint** (e.g. a U.FL turned 90° to suit the board outline) is fine *if the whole launch rotates with it*: the signal pad, any plane void under it, the ground pads and the ring of ground vias keep their geometry relative to the connector, and the 50 Ω trace bends ≥ 1–2 mm away from the pad (a 45°/arc bend on thin prepreg is a sub-0.03 pF effect, RL > 30 dB below 6 GHz — [layout rules](rf-layout-rules.md)). What breaks things is rotating only the connector and leaving the trace to enter the pad from the side, routing the trace under the connector's ground tabs, or losing the ground vias on one side. Edge-launch SMAs can't be angled — they must sit square to a board edge.
- **Measurement**: add a calibration/thru coupon with the same launch (two connectors joined by 20–50 mm of line) to the panel; it gives connector+launch RL and lets you de-embed the launch ([fixtures and de-embedding](../17-test-measurement/fixtures-and-deembedding.md)).

## Common mistakes & misconceptions
- **Using the vendor's 1.6 mm 2-layer SMA footprint unchanged on a 0.21 mm-prepreg 4-layer board** — a ≈ 22 Ω pad.
- **Voiding every plane under the pad** — over-compensates and disconnects the ground reference.
- **Too few ground vias at the connector** — the connector body's return current detours; RL degrades and the connector radiates.
- **Assuming U.FL is good for repeated bench plugging** — 30 cycles; use an SMA test port or a U.FL "tester" cable sparingly.
- **Neck-down of a 2.7 mm 2-layer microstrip (JLC0216A, 50 Ω masked) into a 1 mm connector pad** without CPWG or taper — inductive step at 2.4 GHz+.
- **Ignoring the connector in the link budget** — it is usually small, but a damaged U.FL or an unvoided pad at 5.8 GHz is not.

## How to simulate / verify
- `python3 tools/verify/pcb_launch.py`: shunt-C and series-L discontinuities, SMA/U.FL pads on JLC stackups as ABCD line sections with/without plane voids, L–C compensation, coaxial-via impedance, return-loss budget, U.FL pigtail loss (checked against Hirose's 6 GHz value).
- **openEMS**: 3-D model of the connector pin, pad, void and via fence; sweep void size and pad width ([openEMS workflow](../16-simulation-tools/openems-workflow.md)). The pad-only model (no connector) is `~/opt/openEMS/venv/bin/python tools/verify/sim2_openems_pcb.py pad` (Run 4b; ≈ 10–120 s per case; keep the MSL feed and its measurement plane well outside the PML).
- **VNA + TDR** on a thru coupon; time-gate to isolate each launch ([NanoVNA/LibreVNA](../17-test-measurement/nanovna-librevna-practical.md)).

## Open questions / gaps
- Connector-internal VSWR of specific SMA edge-launch parts (e.g. those in the JLC/LCSC catalogue) at 2.4/5.8 GHz and their recommended footprints were not collected; see [connectors parts](../18-components-parts/connectors-and-cables-parts.md).
- The 0.5 nH "transition inductance" is representative, not measured. The 2026-10-13 openEMS study modelled the pad only (connector as a matched continuation), so it confirms the pad/void numbers but not this inductance; a model with the connector pin and body (vendor STEP), or a measured thru coupon, would replace it.
- Southwest Microwave app note details were read only via a search summary (PDF too large for the fetch tool).

## Sources
1. Hirose Electric, *U.FL Series catalogue* (ultra-small surface-mount coaxial connectors) — DC–6 GHz, VSWR ≤ 1.3 (DC–3 GHz) / ≤ 1.4 (3–6 GHz), 30 mating cycles, 1.13 mm cable loss 3.73 dB/m @ 3 GHz and 5.44 dB/m @ 6 GHz (values as recorded by W1-A4 and cross-checked by search), https://www.hirose.com/product/series/U.FL. (datasheet)
2. B. Rosas, Southwest Microwave, "Optimizing test boards for 50 GHz end launch connectors" (and *Microwave Journal* "50 GHz end launch connector test boards") — grounded-coplanar launches on 30 mil RO4350, via rows as walls (gap < λ/4), trace tapering at the launch. https://mpd.southwestmicrowave.com/wp-content/uploads/2018/07/Optimizing-Test-Boards-for-50-GHz-End-Launch-Connectors.pdf (app note; read via search summary)
3. J. Coonrod, Rogers Corp., "Comparing microstrip and grounded coplanar waveguides," Rogers blog, 2020 — GCPW launch practice, sensitivity to copper plating. (manufacturer technical blog)
4. u-blox, *MAX-M5Q Hardware Integration Manual* UBX-13002460 — low-capacitance (< 0.5 pF) ESD protection on RF_IN; short 50 Ω line. (app note)
5. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley 2012 — ABCD/S conversion, discontinuities. (textbook)
6. KB: [PCB parasitics](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md) (pad capacitance values), [reflections](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md), [coax and cables](../03-transmission-lines-matching/coax-and-cables.md).
7. Verification script `tools/verify/pcb_launch.py` (this page).
