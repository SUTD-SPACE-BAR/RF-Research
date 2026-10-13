---
title: Vias, ground stitching and via fences — inductance, stitching pitch (λ/10–λ/20 and why), CPWG fences, stubs and backdrilling, via-in-pad, thermal vias
domain: 13-pcb-rf-layout-emc
slug: vias-stitching-fencing
tags: [via, via-inductance, goldfarb-pucel, ground-stitching, stitching-pitch, lambda-over-20, via-fence, post-wall, CPWG, grounded-coplanar, substrate-integrated-waveguide, SIW, via-stub, backdrill, via-in-pad, POFV, thermal-via, exposed-pad, copper-island, FDFD]
prerequisites:
  - ../04-real-components-hf/pcb-parasitics-traces-vias-pads.md
  - grounding-and-return-paths.md
  - stackups-and-materials.md
related:
  - rf-layout-rules.md
  - connectors-and-launches.md
  - shielding-and-isolation.md
  - thermal-management-rf.md
  - jlcpcb-rf-manufacturing.md
  - ../02-electromagnetics/waveguides-and-cavity-resonators.md
  - ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# Vias, ground stitching and via fences

## Questions this page answers
- How much inductance does a via have on a JLCPCB 4-layer board, and when does it matter?
- Where does the "stitch ground every λ/10 (or λ/20)" rule come from, and how much isolation does a via row really give?
- How far apart should via-fence vias be along a grounded coplanar waveguide at 915 MHz, 2.4 GHz and 5.8 GHz?
- Why do floating or single-via copper islands cause trouble?
- Do I need back-drilling or blind vias for RF on a 1.6 mm board?
- Should I put vias in the exposed pad of a QFN (PA, SX1262, ESP32-S3), and will solder wick into them?
- How much heat does one thermal via carry?

## TL;DR
- **Via inductance is the length to the plane that matters**: an L1→L2 via on JLC04161H-7628 (0.21 mm) is **≈ 0.015 nH** (0.09 Ω at 915 MHz) — negligible; L1→L3 (1.28 mm) ≈ 0.38 nH; through a 1.6 mm 2-layer board ≈ 0.54 nH (3.1 Ω at 915 MHz, 8.4 Ω at 2.45 GHz) (Goldfarb–Pucel; script §1; details on the [04 parasitics page](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md)).
- **A row of vias between two planes is a shunt-inductive "post wall"**, not a solid wall. Its single-row isolation for a parallel-plate wave is set by pitch/wavelength and via radius. With **0.3 mm vias in FR-4** (own FDFD solution, script §2–3):

  | pitch | 915 MHz | 2.45 GHz | 5.8 GHz |
  |---|---|---|---|
  | 1 mm | 49 dB | 41 dB | 33 dB |
  | 2 mm | 33 dB | 25 dB | 17 dB |
  | 3 mm | 26 dB | 18 dB | 11 dB |
  | 5 mm | 19 dB | 11 dB | 5 dB |

  **λ/20 ≈ 18 dB per row, λ/10 ≈ 9 dB** — that is the physics behind the λ/10–λ/20 rules. A second row 1.5 mm away roughly doubles the dB.
- **The textbook thin-post formula $X/\eta=(a/\lambda)\ln(a/2\pi r)$ overestimates isolation by ≈ 13 dB for typical fat PCB vias** (r/a = 0.15); it is fine only for r/a ≲ 0.05 (checked against FDFD).
- **Un-stitched copper resonates**: a floating island or a GND strip between two vias resonates at $c/(2L\sqrt{\varepsilon_{eff}})$; a GND finger with one via at $c/(4L\sqrt{\varepsilon_{eff}})$ — a **10 mm finger resonates at ≈ 4.6 GHz, 30 mm at 1.5 GHz (GNSS!)** (script §4). Stitch pours at ≤ λ/20 of the highest frequency of concern and delete slivers.
- **Via stubs**: a through-via used L1→L2 on a 1.6 mm board leaves a 1.35 mm stub resonating at ≈ 26 GHz — **backdrilling and blind vias are irrelevant below ≈ 6–8 GHz** on normal boards (script §5).
- **Thermal vias**: one 0.3 mm via with a 20 µm wall (JLC plates ≈ 20–25 µm) through 1.6 mm is **≈ 240 K/W**; 9 in parallel ≈ 26 K/W before spreading; epoxy fill adds nothing thermally, copper fill would give ≈ 4× (script §6). Via-in-pad (POFV, epoxy-filled and capped) stops solder wicking; JLC makes it default on ≥ 6 layers [1].

## Intuition (no math)
A via is a short wire. Its inductance depends on how far it has to go before it reaches the plane that carries the return current — so a via from the top layer to a ground plane 0.2 mm below is almost nothing, while a via through a 1.6 mm board is a few ohms at UHF. That is one of the main practical advantages of a 4-layer RF board with ground on L2.

**Stitching vias** tie copper areas on different layers together so that they behave as one ground. Two ground planes (or a top pour and L2) form a parallel-plate "waveguide" in which energy can travel between them; any edge or opening lets it escape (radiation) or couple somewhere else. A row of vias across that gap acts like a picket fence: vias are thin inductors in parallel, so a wave squeezes between them, and the closer and fatter the pickets, the less gets through. Once the pickets are much closer than a wavelength, the leakage per row is small, and two rows are much better than one. That is the whole content of the "λ/10–λ/20" rules — they are **isolation targets per row**, not magic numbers.

**Copper without enough vias is an antenna.** A ground pour island connected by one via, or not at all, is a resonant patch or stub at the frequency where its length is λ/4 or λ/2 — and it sits right next to your RF traces. Either stitch it properly or delete it.

**Thermal vias** are the main path for PA heat from the top-layer exposed pad into the internal planes. A plated via is a thin copper tube (≈ 20–25 µm wall), so each carries surprisingly little heat; you need many, and the heat then has to spread in the planes.

## The math

### Level 1 — via inductance and reactance (JLC geometries)
Goldfarb–Pucel: $L=\frac{\mu_0}{2\pi}\left[h\ln\frac{h+\sqrt{h^2+r^2}}{r}+\frac32\left(r-\sqrt{r^2+h^2}\right)\right]$ ([04 page](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md)). Script §1:

| Via (drill) | L | X @ 915 MHz | X @ 2.45 GHz | X @ 5.8 GHz |
|---|---|---|---|---|
| L1→L2, JLC-7628 (0.3 mm) | 0.015 nH | 0.09 Ω | 0.24 Ω | 0.56 Ω |
| L1→L2, JLC-3313 (0.3 mm) | 0.003 nH | 0.02 Ω | 0.05 Ω | 0.12 Ω |
| L1→L3, JLC-7628 (0.3 mm) | 0.38 nH | 2.2 Ω | 5.9 Ω | 14 Ω |
| through 1.6 mm (0.3 mm) | 0.54 nH | 3.1 Ω | 8.4 Ω | 20 Ω |
| through 1.6 mm (0.2 mm) | 0.66 nH | 3.8 Ω | 10.1 Ω | 24 Ω |

**Consequence:** on a 4-layer board with L2 ground, shunt parts and ground pins connect through essentially zero via inductance; on a 2-layer board every ground via is a few ohms at UHF and must be included in matching (or doubled/tripled — but coupled vias don't divide perfectly, see the 04 page).

### Level 2 — a via row as a post wall (the physics of the λ/20 rule)
Between two planes separated by $h\ll\lambda$ only the TEM parallel-plate wave propagates, with E vertical — parallel to the vias. A periodic row of posts (pitch $a$, radius $r$) presents to a wave arriving normally a **shunt inductive reactance** $X$; for thin posts the classical leading-order result is
$$\frac{X}{\eta}\approx\frac{a}{\lambda}\ln\frac{a}{2\pi r}\qquad(r\ll a\ll\lambda),$$
and the transmission through the row is $T=\frac{2jX/\eta}{1+2jX/\eta}$ (shunt element across a line of impedance η). Writing $X/\eta=(a/\lambda)\Lambda(r/a)$, isolation grows as the pitch shrinks relative to λ and as the posts get fatter (smaller Λ).

**Independent check (script §2):** a 2-D finite-difference frequency-domain solution of the Helmholtz equation in one periodic cell with PMLs and staircased PEC posts. For thin posts (r/a = 0.02–0.05) it converges to the formula within 0.4–0.6 dB. For typical PCB vias the formula fails: with a 0.3 mm drill at 1 mm pitch (r/a = 0.15) $\ln(a/2\pi r)$ = 0.059, predicting 44.5 dB at a = λ/20, whereas the FDFD gives Λ = 0.276 and **31.2 dB**. FDFD values of Λ: 1.25 (r/a 0.05), 0.84 (0.075), 0.59 (0.10), 0.28 (0.15). The table in the TL;DR uses these.

**Two rows** spaced $s$ (staggered or not, $s\ll\lambda$): cascade shunt–line–shunt; the isolation in dB roughly doubles (e.g. 2 mm pitch at 2.45 GHz: 25 dB one row → 42 dB two rows 1.5 mm apart).

**Where the common rules come from:**
- **"λ/20 pitch"** (EMC practice for board-edge and pour stitching): ≈ 18 dB per row for 0.3 mm vias — a reasonable target for "keep plane-pair energy in".
- **"λ/10"**: ≈ 9 dB per row — the *minimum* for a via row to behave as a wall at all.
- **"gap < λ/4 in the dielectric"** (Southwest Microwave, 50 GHz launches) [2]: a *cutoff-style* bound — below it the gap between vias does not transmit freely — but at λ/4 a single row gives only ≈ 10 dB; their boards use it at the top of a 50 GHz band, i.e. far tighter at lower frequencies.
- **SIW design rules** (substrate-integrated waveguide: via diameter $d<\lambda_g/5$, pitch $p\le2d$, commonly attributed to Deslandes & Wu and Xu & Wu [3][4]) are much tighter because an SIW wall must reflect a *guided* wave with negligible leakage over many wavelengths.

### Level 3 — resonances of un-stitched copper, via stubs, via-in-pad and heat
**Copper islands and fingers.** A top-layer copper region over a ground plane is a microstrip patch/stub with $\varepsilon_{eff}\approx2.7$ (FR-4). Open–open (floating island) or shorted–shorted (strip between two stitching vias) it resonates at $f=c/(2L\sqrt{\varepsilon_{eff}})$; shorted at one end only (a "finger" with one via) at $c/(4L\sqrt{\varepsilon_{eff}})$ (script §4):

| L | λ/2 mode | λ/4 mode (one via) |
|---|---|---|
| 5 mm | 18.2 GHz | 9.1 GHz |
| 10 mm | 9.1 GHz | 4.6 GHz |
| 20 mm | 4.6 GHz | 2.3 GHz |
| 30 mm | 3.0 GHz | 1.5 GHz |
| 50 mm | 1.8 GHz | 0.91 GHz |

So **stitching pitch along a pour edge and between pour vias should be < λ/4 of the highest frequency with margin, i.e. ≤ λ/10–λ/20**: at 915 MHz ≤ 10–20 mm, at 2.45 GHz ≤ 3.7–7.4 mm, at 5.8 GHz ≤ 1.6–3.1 mm (top copper, script §4). Between buried planes (εr 4.4) λ/20 is 7.8 / 2.9 / 1.2 mm.

**CPWG via fences.** In grounded coplanar waveguide the side grounds and the bottom plane must be at the same potential; otherwise the side-ground strips support their own (slotline/parallel-plate/patch) modes and the line becomes lossy and resonant. Rules: a row of vias along each side ground, **first row close to the gap edge (≈ 0.5–1 × h from it, not more than ≈ W+S)**, pitch ≤ λ/20 of the highest frequency of interest (the side strip between two vias must not reach λ/2 below the band's upper edge) [5][6]. The Rogers/Coonrod literature adds that via position also matters for loss at mm-wave [6].

**Via stubs.** A through via used only from L1 to L2 leaves an open stub to the bottom; its quarter-wave resonance $f=c/(4\ell_{stub}\sqrt{\varepsilon_r})$ is ≈ 26 GHz for the 1.35 mm stub of a JLC 4-layer 1.6 mm board and ≈ 11.5 GHz for a 3.1 mm stub (script §5). Keep operating frequencies below ≈ 1/3 of it: **backdrilling/blind vias matter only above ≈ 8 GHz on 1.6 mm boards** (radar at 24 GHz: yes).

**Via-in-pad.** Open vias in an exposed pad wick solder away (voids, poor thermal/ground contact) and let flux/solder escape to the far side. Options: tented from the bottom (partial), small drill (≤ 0.3 mm) with paste-window reduction, or **plugged-and-over-plated (POFV: epoxy-filled and capped)** — JLCPCB offers epoxy- or copper-paste-filled and capped vias, 0.15–0.55 mm, **default on ≥ 6-layer boards** [1].

**Thermal vias.** Axial conduction through the plated wall: $R_{via}=\ell/(k_{Cu}A_{wall})$, $A_{wall}=\pi[(d/2)^2-(d/2-t)^2]$. For $k_{Cu}$ = 385 W/m·K, 1.6 mm length (script §6):

| drill | 20 µm wall | 25 µm wall | if solid-Cu filled |
|---|---|---|---|
| 0.2 mm | 368 K/W | 302 K/W | 132 K/W |
| 0.3 mm | 236 K/W | 192 K/W | 59 K/W |
| 0.4 mm | 174 K/W | 141 K/W | 33 K/W |

An array of N vias ≈ $R_{via}/N$ in parallel (9 × 0.3 mm: 26 K/W) — before the much larger spreading resistance in the planes and the board-to-air resistance ([thermal management](thermal-management-rf.md)). Epoxy fill (k ≈ 0.3 W/m·K) adds nothing thermally. A via to L2 only (0.21 mm) is ≈ 31 K/W — heat gets into L2 easily; spreading then dominates.

## Design equations & rules of thumb

| Item | Rule / value | Basis |
|---|---|---|
| Ground via for a shunt part | one per pad, at the pad; on 4-layer it is ≈ free | §1 |
| Via-row isolation (0.3 mm vias, FR-4) | λ/20 → ≈ 18 dB/row; λ/10 → ≈ 9 dB/row; 2 rows ≈ 2× dB | §2–3 FDFD |
| Stitching of pours/edges | pitch ≤ λ/20 of highest frequency of concern | §3–4 |
| Unstitched copper | no floating islands; fingers < λ/10 of top frequency | §4 |
| CPWG fence | row per side, first row ≈ 0.5–1 h from the gap, pitch ≤ λ/20 | [5][6] |
| SIW wall | d < λg/5, p ≤ 2d (commonly quoted) | [3][4] |
| Via stub | $f=c/(4\ell\sqrt{\varepsilon_r})$; backdrill only if f_op > f_stub/3 | §5 |
| Thermal via | ≈ 240 K/W (0.3 mm/20 µm/1.6 mm); N in parallel | §6 |
| Via-in-pad | POFV (filled+capped) for EPADs with vias | [1] |
| Antenna keep-out | no fences, pours or vias inside it on any layer; stitch the ground edge facing it | [layout rules](rf-layout-rules.md) |

## Worked examples

### 1. Stitching the L1 ground pour around a 915 MHz LoRa front end
Highest frequency of concern: the PA's 5th harmonic, 4.6 GHz (the LoRa chip's harmonic filter handles the conducted part; the pour must not radiate it). λ/20 at 4.6 GHz on top copper ≈ 2 mm. Practical: **vias every 2–3 mm along pour edges next to RF traces**, every 5 mm elsewhere; no pour fingers > 5 mm without a via at the tip (a 10 mm finger resonates at 4.6 GHz). On JLC this is cheap: 0.3 mm vias are standard.

### 2. A via fence between a 2.45 GHz transmitter and a GNSS LNA
Two compartments inside one board, energy leaking in the L2–L3 plane pair: one row of 0.3 mm vias at 2 mm pitch gives ≈ 25 dB at 2.45 GHz and ≈ 29 dB at 1.575 GHz (same model); two rows 1.5 mm apart ≈ 42 dB at 2.45 GHz. This only fixes the *inside-the-board* path; coupling through the air above needs distance or a shield can ([shielding](shielding-and-isolation.md)).

### 3. Exposed pad of an SX1262 (4 × 4 mm QFN) at +22 dBm
Dissipation ≈ 0.3–0.5 W during TX (Semtech's power/heat figures, [thermal page](thermal-management-rf.md)). Nine 0.3 mm vias in the EPAD to L2/L3/L4 ≈ 26 K/W axially (through the whole board) — already less than the spreading from a small board to air. Use a paste window of ≈ 50–70 % of the pad in segments, and either small open vias (accept some voiding) or POFV.

### 4. Is backdrilling needed for a 24 GHz radar feed on a 1.6 mm 4-layer board?
If the RF line changes layers L1→L2 with a through via: 1.35 mm stub → 26 GHz resonance, too close to 24 GHz. Avoid layer changes (keep RF on L1), use a 2-layer Rogers board, or use a blind via / backdrilling (not a JLC standard 4-layer option — check HDI services).

## Practical notes
- **JLCPCB via sizes**: minimum drill 0.15 mm, minimum via diameter 0.25 mm (multilayer) [1]; 0.3 mm drill / 0.5–0.6 mm pad is the cheap default for stitching. Tiny vias cost more (precision surcharge) and have higher inductance and thermal resistance.
- **KiCad**: use the RF-tools "Via Fence Generator" / "Via Stitching" plugins or place vias manually along a GND zone; set the zone-to-via connection to **solid** (no thermal relief) for stitching vias; enable "Remove islands" on zones or delete islands manually.
- **Don't let stitching vias perforate the reference plane under an RF trace** — they don't hurt the plane, but via antipads on *other* nets do: keep signal vias (other nets) out of the ±3–5h return-current strip under RF traces ([grounding](grounding-and-return-paths.md)).
- **Plane-pair edges**: stitch GND planes together along the board perimeter at ≤ λ/20 of the highest emission frequency — it closes the plane-pair cavity's radiating edge (better than the 20-H rule).
- **Thermal vias under PAs**: vias both inside the EPAD and in the surrounding GND pour; heat also needs a large L2/L3 copper area and a path to the enclosure ([thermal management](thermal-management-rf.md)).

## Common mistakes & misconceptions
- **"More vias always help."** Coupled vias saturate (04 page); for isolation, pitch relative to λ and number of rows matter; for inductance, proximity to the part matters.
- **Using the thin-wire formula for via fences** — overestimates isolation by > 10 dB for normal via sizes.
- **Stitching at λ/10 of the *operating* frequency and forgetting harmonics.**
- **Floating copper "for EMC"** — it is a resonator, not a shield.
- **Backdrilling a 915 MHz design** — pointless expense.
- **Expecting epoxy-filled vias to conduct heat better** — the copper wall does all the work.
- **Via-fencing the antenna.** Fences and stitched pours suppress radiation from *lines*; around or under a *radiator* they cancel the radiation you want (ground 1 mm below a 2.45 GHz radiator cuts R_rad ≈ 500×; [layout rules §Level 3](rf-layout-rules.md#level-3--why-the-antenna-keep-out-must-be-copper-free-and-never-fenced)). Fence the feed line up to the keep-out boundary and stop; keep the keep-out copper-free on every layer; do stitch the ground-plane *edge* that faces the keep-out (it is the antenna's counterpoise).

## How to simulate / verify
- `python3 tools/verify/pcb_via_fence.py` (≈ 10–15 min; FDFD): via inductance table; thin-post formula vs own FDFD with mesh refinement; FDFD Λ(r/a) for fat vias; single/double-row isolation vs pitch at 0.915/2.45/5.8/10 GHz; resonances of un-stitched copper; via-stub frequencies; thermal via resistances.
- openEMS: two microstrips separated by via fences; a CPWG with and without side-ground vias (look for resonance notches in S21) ([EM solvers](../16-simulation-tools/em-solvers-fdtd-mom-fem.md)).
- Bench: near-field H-probe over pour edges while transmitting; a resonating island is a bright spot.

## Open questions / gaps
- The FDFD is 2-D (infinitely tall posts between PEC plates, normal incidence) — real fences have finite plane size, oblique incidence and pads; treat values as ±2–3 dB.
- CPWG via-row distance from the gap edge is quoted as a practitioner range (0.5–1 h) — not derived here; an openEMS parametric study would settle it for JLC stackups.
- SIW rules (d < λg/5, p ≤ 2d) are quoted from secondary summaries of Deslandes & Wu / Xu & Wu, not re-read in the original papers.

## Sources
1. JLCPCB, "PCB manufacturing & assembly capabilities" (min drill 0.15 mm, min via diameter 0.25 mm; POFV epoxy/copper-paste filled and capped, 0.15–0.55 mm, default ≥ 6 layers), https://jlcpcb.com/capabilities/pcb-capabilities; JLCPCB blog "PCB plating thickness" (hole-wall copper ≈ 20–25 µm, IPC-6012 Class 2). Accessed 2026-09-27. (manufacturer)
2. B. Rosas, Southwest Microwave, "Optimizing test boards for 50 GHz end launch connectors" — via rows as walls when the edge-to-edge gap < λ/4 in the dielectric. (app note; via search summary)
3. D. Deslandes, K. Wu, "Accurate modeling, wave mechanisms, and design considerations of a substrate integrated waveguide," *IEEE Trans. MTT* 54(6), 2516–2526, 2006. (peer-reviewed; rules quoted from secondary summaries)
4. F. Xu, K. Wu, "Guided-wave and leakage characteristics of substrate integrated waveguide," *IEEE Trans. MTT* 53(1), 66–73, 2005. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
5. N. Marcuvitz, *Waveguide Handbook*, MIT Rad. Lab. Series vol. 10, 1951 (inductive post gratings); R. E. Collin, *Field Theory of Guided Waves*, 2nd ed., IEEE Press 1991 (thin-wire gratings) — leading-term shunt reactance. (textbooks; from knowledge)
6. J. Coonrod, Rogers Corp., "Comparing microstrip and grounded coplanar waveguides," Rogers blog 2020, and "Making the most of coplanar waveguide," *Microwave Journal* ROG Blog, Dec 2014 — CPWG via connection of side grounds. (manufacturer technical blog)
7. M. E. Goldfarb, R. A. Pucel, "Modeling via hole grounds in microstrip," *IEEE MGWL* 1(6), 1991 (via inductance; via 04 page). (peer-reviewed)
8. H. W. Johnson, M. Graham, *High-Speed Digital Design*, 1993 — vias, stubs, return vias. (textbook)
9. easyw, *RF-tools-KiCAD* (via fence and stitching generators), https://github.com/easyw/RF-tools-KiCAD. (software)
10. Verification script `tools/verify/pcb_via_fence.py` (this page; own FDFD).
