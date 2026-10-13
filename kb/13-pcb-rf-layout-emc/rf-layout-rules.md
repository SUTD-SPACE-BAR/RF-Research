---
title: RF PCB layout rules — placement order, matching at the pin, component sizes, keep-outs, crystals, isolation, reference layouts and KiCad practice
domain: 13-pcb-rf-layout-emc
slug: rf-layout-rules
tags: [rf-layout, placement, matching-network, 0201, 0402, 0603, pad-capacitance, ESL, bend, mitre, antenna-keep-out, crystal, TCXO, thermal-isolation, PA-LNA-isolation, reference-design, SX1262, SX126x, CC1310, CC1312, ESP32-S3, u-blox, MAX-M10S, KiCad, net-tie, rule-area, via-fence-plugin]
prerequisites:
  - stackups-and-materials.md
  - grounding-and-return-paths.md
  - ../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md
related:
  - vias-stitching-fencing.md
  - connectors-and-launches.md
  - shielding-and-isolation.md
  - power-distribution-decoupling-for-rf.md
  - mixed-signal-layout.md
  - thermal-management-rf.md
  - rf-pcb-review-checklist.md
  - ../04-real-components-hf/capacitors-at-rf-mlcc.md
  - ../04-real-components-hf/inductors-at-rf.md
  - ../08-antennas/pcb-and-chip-antennas.md
  - ../15-lora-ism-radios/semtech-chip-family.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# RF PCB layout rules

## Questions this page answers
- In what order should I place parts on an RF board?
- How close to the chip pin must the matching network be, and in what orientation?
- Is 0402 good enough at 2.4 GHz, or do I need 0201? When is 0603 too big?
- Why does my 2.2 pF matching capacitor behave like 3 pF at 2.4 GHz?
- Where should the trace inductance go in an LC filter or match?
- Do microstrip bends need to be mitred or curved?
- How much keep-out does a chip or PCB antenna need, and can there be copper under it?
- Where do I put the crystal or TCXO for an SX1262, and why does my LoRa frequency drift during long packets?
- How do I keep PA energy out of the LNA / receive path?
- How closely must I copy a reference layout (Semtech, TI, Espressif, u-blox)?
- What KiCad features help with RF layout (rule areas, net ties, custom pads, via-fence plugins)?
- Should I put a via fence or ground pour around my antenna to "shield" it?
- What is the exposed (unmasked) ground copper next to RF sections for?
- What changes when I lay out above 10 GHz?

## TL;DR
- **Placement order**: antenna/connector location and keep-out → RF IC or module → matching/filter/switch *at the pins* → crystal/TCXO (thermally isolated) → decoupling at each supply pin → DC-DC → digital → cables/connectors. Route RF first, on the top layer, over an unbroken L2 ground, without vias [1][2][3].
- **Copy the reference layout's stackup distance** (top layer → first ground) — TI warns that changing it can force a re-design of the balun/filter [1]. JLC04161H-7628 (0.21 mm) is close to most 4-layer reference designs.
- **Component size at 2.4 GHz**: ESL + pads make a nominal 2.2 pF shunt capacitor look like **2.56 pF (0201), 2.85 pF (0402), 3.58 pF (0603)**; at 915 MHz a 3.3 pF looks like 3.40/3.49/3.76 pF (script §2). **0402 is fine to ≈ 2.4 GHz if you use vendor S-parameters; 0201 at 2.4–6 GHz (Espressif's ESP32-S3 match uses 0201) [3]; 0603 only for DC blocks, chokes and bulk.**
- **Pads on thin prepreg**: 0201 ≈ −4 fF, 0402 ≈ +17 fF, 0603 ≈ +99 fF excess vs the 50 Ω line on JLC-7628 (script §1) — 0402 is "invisible" at UHF.
- **Put interconnect inductance in series with the inductor, never with a shunt capacitor**: 0.5 nH in the shunt-C branch drops its self-resonance from 6.5 to 4.3 GHz and makes 1.5 pF act like 2.2 pF at 2.45 GHz (TI's LC-filter rule, quantified in script §3) [1].
- **Bends don't matter below ≈ 6 GHz on thin prepreg**: an unmitred 90° 50 Ω bend on JLC-7628 is ≈ 22 fF (RL ≈ 34 dB at 5.8 GHz); on 2-layer 1.6 mm it is ≈ 160 fF (RL ≈ 24 dB at 2.45 GHz). Use 45°/arc bends anyway; optimum mitre ≈ 57–58 % [4].
- **Crystal/TCXO**: short symmetric loop, solid GND under it, no traces beneath, ≥ 2 mm from the chip clock pin (Espressif) [3]; for SX126x at +22 dBm, **copper void around the crystal on all layers** or a **TCXO**; packets > 1 s at +22 dBm need a TCXO (Semtech measurements) [5][6].
- **Antenna keep-out**: no copper on any layer under a PCB/chip antenna; ESP32 module antennas want ≈ 15 mm clearance all round and the feed at the board edge [3]. **Never via-fence or pour ground under or around the radiator, or anywhere inside its keep-out**: ground 1 mm under a 2.45 GHz radiator cuts its radiation resistance ≈ 500× (a short radiator's efficiency falls from ≈ 84 % to ≈ 1 %) (script §6). Fences belong along the *feed line*, stopping at the keep-out boundary.
- **Isolation**: separate TX (PA, harmonic filter) and RX (LNA, SAW) paths by distance, ground and via fences; keep the PA harmonic filter's output away from its input; consider a shield can for > +20 dBm ([shielding](shielding-and-isolation.md)).

## Intuition (no math)
At RF every piece of copper is part of the circuit. A matching network that is 5 mm away from the chip pin is not the network you designed: the 5 mm of trace is ≈ 1.7 nH and 0.6 pF of extra L and C, and at 2.4 GHz that is as big as the parts themselves. So RF layout is mostly about **making the physical circuit equal the schematic** — short connections, parts right at the pins, a solid ground immediately below, and ground vias right at every grounded pad — and about **keeping unwanted coupling paths small**: PA to LNA, crystal to PA heat, digital harmonics to antenna.

Reference designs encode this knowledge: the chip vendor already found a placement where the matching and filtering work on a given stackup. The safest path is to copy it (component sizes, positions, orientations, via positions, and the dielectric thickness to ground) and change only what you must.

Physical size matters because of two parasitics: **pad capacitance** (a wide pad close to the ground plane) and **mounted inductance** (the current loop through the part, its pads and the via). Both grow with case size. At 433 MHz almost anything works; at 2.4 GHz a 0603 capacitor is noticeably "bigger" than its label; at 5.8 GHz and above, 0201 and thin-film parts, and EM simulation of the layout, become normal.

## The math

### Level 1 — how parasitics shift a matching element
A shunt capacitor $C$ with mounted inductance $L$ (ESL + via) and pad capacitance $C_p$ has effective capacitance
$$C_{eff}=\frac{C}{1-\omega^2LC}+C_p .$$
For the representative mounted ESL values 0.25 nH (0201), 0.40 nH (0402), 0.65 nH (0603) plus the ≈ 0.02 nH L1→L2 via on JLC-7628 (script §2):

| Nominal | f | 0201 | 0402 | 0603 |
|---|---|---|---|---|
| 1.0 pF | 2.45 GHz | 1.07 pF | 1.14 pF | 1.39 pF |
| 2.2 pF | 2.45 GHz | 2.56 pF | 2.85 pF | 3.58 pF |
| 3.3 pF | 915 MHz | 3.40 pF | 3.49 pF | 3.76 pF |
| 8.2 pF | 915 MHz | 8.85 pF | 9.29 pF | 10.2 pF |

Series inductors have the dual problem: parasitic capacitance $C_p$ lowers their SRF and raises the effective inductance $L/(1-\omega^2LC_p)$ ([inductors at RF](../04-real-components-hf/inductors-at-rf.md)). The practical answer is to use the vendor's S-parameter models for the exact part in simulation, and to keep the part size and pad geometry identical between the reference design and your layout.

### Level 2 — where interconnect inductance should go
In an LC ladder, a connecting trace of inductance $L_t$ (≈ 0.3 nH/mm for 50 Ω on JLC-7628; ≈ 0.5 nH for 1.5 mm) either adds to a series inductor — harmless, just re-tune it down by $L_t$ — or sits in series with a shunt capacitor, turning it into a series LC that resonates at $1/(2\pi\sqrt{(L_t+L_{ESL})C})$. For 1.5 pF with 0.4 nH ESL: 6.5 GHz without the trace, **4.3 GHz with 0.5 nH of trace** — right where a 2.45 GHz transmitter's second harmonic (4.9 GHz) should be attenuated, and the capacitor already reads 2.2 pF at the fundamental (script §3). TI's rule: lay out the ladder so each shunt capacitor's pad touches the node, its ground via is at its pad, and the connecting trace runs to the series inductor [1].

### Level 3 — why the antenna keep-out must be copper-free (and never fenced)
An antenna radiates because its currents are *not* cancelled by nearby return currents — the opposite of a transmission line, whose return current hugs it so that it does *not* radiate ([grounding](grounding-and-return-paths.md)). Put a conductor close to a radiating element and it carries an image current that cancels the radiation. For a horizontal (parallel-to-board) current element at height d over a ground plane, the radiation resistance relative to free space is
$$\frac{R_{rad}}{R_{rad,0}}=1-\frac32\left[\frac{\sin x}{x}+\frac{\cos x}{x^2}-\frac{\sin x}{x^3}\right]_{x=2kd}\approx\frac45(kd)^2\quad(kd\ll1),$$
(script §6: numerical hemisphere integration of the dipole + image pair agrees with this closed form to < 0.01 %). At 2.45 GHz, d = 1 mm (kd = 0.051): 0.0021; d = 3 mm: 0.019; at 915 MHz, d = 3 mm: 0.0026, d = 10 mm: 0.029. With the radiator's conductor and matching losses unchanged, efficiency collapses — a short 10 mm radiator (R_rad ≈ 5.3 Ω, 1 Ω loss) goes from ≈ 84 % to ≈ 1 % with ground 1 mm below it — and the resonant frequency and input impedance move (the near field is loaded by the ground). That is why chip/PCB antennas specify a **copper-free keep-out on every layer** and a defined ground-plane edge beside it ([PCB and chip antennas](../08-antennas/pcb-and-chip-antennas.md)).

The common confusion: for monopole-type antennas (IFA, chip antennas, whips) **the board ground *is* part of the antenna** — the counterpoise. Its *edge* next to the keep-out must be solid and well stitched (the antenna current returns along it), and its size sets the antenna's bandwidth and efficiency. But ground *under* the radiating arm, ground "fences" around the radiator, or a shield can over it short out the radiating near field. Via fences and grounded coplanar structures are for transmission lines (to *stop* radiation); use them on the feed line up to the keep-out boundary and stop there.

### Level 3b — bends, stubs and when to go to EM simulation
A right-angle microstrip bend has excess capacitance at the outer corner; the optimum mitre for 0.25 ≤ W/h ≤ 2.75 is $M\approx52+65e^{-1.35W/h}$ % of the corner diagonal (Douville & James, as quoted by Gupta/Pozar) [4] — ≈ 57–58 % for 50 Ω on FR-4. The unmitred corner's excess capacitance is of order $\tfrac12C'W$: ≈ 22 fF on JLC04161H-7628 (W ≈ 0.37 mm, bare-copper H-J width), ≈ 160 fF on a 2-layer 1.6 mm board (W ≈ 2.65 mm bare, JLC0216A 1.43 mm core, εr 4.5) — ordering widths are in the [canonical table](stackups-and-materials.md#canonical-50-ω-width-table) (script §4, crude estimate). So bends matter for wide lines on thick boards at ≥ 2.4 GHz and not at all for thin-prepreg lines below 6 GHz.

**Stubs**: any unterminated copper attached to an RF node — a test pad, an unpopulated footprint, a via stub, a "just in case" 0 Ω pad — is an open stub; at λ/4 it shorts the node. On FR-4 microstrip λ/4 is 45 mm at 915 MHz, 17 mm at 2.45 GHz, 7 mm at 5.8 GHz (script §5); keep stubs < λ/20 (9/3.4/1.4 mm) or remove them.

**When to EM-simulate**: whenever the layout differs from the reference (part size, stackup, positions) at ≥ 2.4 GHz, or whenever a structure is > λ/20 (a third of the table above). TI recommends simulating both the reference and the custom layout and matching their S21/S22 [1].

## Design equations & rules of thumb

| Rule | Value | Source/notes |
|---|---|---|
| Matching network at the pin | first element within ≈ 1 mm of the pin | [1][2][3] |
| Shunt C effective value | $C/(1-\omega^2LC)+C_p$ | 2.2 pF 0402 → 2.85 pF @ 2.45 GHz |
| Case size | ≤ 1 GHz: 0402/0603; 2.4 GHz: 0402 (0201 better); ≥ 5 GHz: 0201 | script §1–2 |
| Interconnect L placement | in series with inductors, not with shunt C | TI [1] |
| Balun symmetry (CC13xx) | amplitude ≤ 1.5 dB, phase ≤ 10° imbalance | TI [1] |
| Bend mitre | $52+65e^{-1.35W/h}$ % | [4]; negligible on thin prepreg |
| Stub limit | < λ/20 | 9 mm @ 915 MHz, 3.4 mm @ 2.45 GHz |
| GNSS 50 Ω line | < 25 mm on standard FR-4 w/o shielding; gap to top GND ≥ dielectric thickness | u-blox [7] |
| Crystal | ≥ 2 mm from chip clock pin; no traces under | Espressif [3] |
| SX126x crystal at +22 dBm | copper void on all layers around XTAL, or TCXO; TCXO for > 1 s packets | Semtech [5][6] |
| Antenna clearance | ESP32 module ≈ 15 mm all round | Espressif [3] |
| RF on outer layer, no vias, 135° or arc bends | — | Espressif [3] |
| EPAD vias (ESP32-S3) | ≥ 9 | Espressif [3] |

## Worked examples

### 1. Placing an SX1262 front end on JLC04161H-7628 (915 MHz, +22 dBm)
Follow Semtech's E428 4-layer reference: L1 components and RF routing, **L2 solid RF ground reference**, L3 control routing, L4 solid ground [6]. Order:
1. Put the U.FL/SMA at the board edge, 5–15 mm from the chip; draw the 50 Ω path (0.359 mm with mask) on L1 with **no layer changes**.
2. Place the RF switch (if used) and the TX chain: VR_PA choke (rated > 130 mA for +22 dBm, < 100 mV drop [8]), PA matching L/C at the RFO pin, 2nd-harmonic trap, π low-pass — in a line, in signal order, shunt capacitors grounded by their own via at the pad, trace inductance in the series inductors.
3. Place the RX balun/match (C–L–C) symmetrically at RFI_P/RFI_N, as close as possible [6][8].
4. Crystal: 32 MHz XTAL within a few mm of XTA/XTB with a **copper void on all layers around it** (thermal insulation), or a TCXO powered from DIO3 — mandatory for +22 dBm packets longer than ≈ 400–500 ms [5].
5. DC-DC inductor (DCC_SW) close to the pin but on the far side from the RF path; decoupling caps at VBAT/VR_PA pins (AN1200.66 uses 47 pF + 47 nF on VR_PA [9]).
6. Stitch the L1 GND pour to L2 around the RF section at ≤ λ/20 (9 mm at 915 MHz; use 2–3 mm in practice) and fence the TX filter ([vias](vias-stitching-fencing.md)).

### 2. Why the 2.4 GHz match "didn't work" after changing to 0603
A 2.45 GHz CLC match (1.0 pF – 2.7 nH – 1.0 pF) copied from a reference in 0402 was re-drawn in 0603 to ease hand soldering. Effective shunt capacitance rises from 1.14 to 1.39 pF (+22 %), and each 0603 pad adds 0.1 pF on thin prepreg; the match's centre frequency drops by roughly half the fractional change of the resonating C (≈ 8–10 %, ≈ 200 MHz) — outside the 2.4 GHz band. Return to the reference size (0402 or 0201), or re-tune on the VNA ([NanoVNA](../17-test-measurement/nanovna-librevna-practical.md)).

### 3. Crystal drift budget on a +22 dBm LoRa board
Semtech measured that without thermal insulation an SX1262 at +22 dBm (3.7 V) drifts beyond the maximum tolerable offset during long packets; with a copper void the drift stays acceptable for 400–500 ms but not for 1 s; a TCXO is needed for longer packets or below −20 °C/above 70 °C [5]. A rocket downlink at SF9/125 kHz with 40 bytes lasts ≈ 0.29 s (explicit header, CRC, CR 4/5, 8-symbol preamble) — insulation suffices at room temperature, but the av-bay can reach > 50 °C on a Singapore pad; **use a TCXO for flight hardware** ([LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md), [crystals](../04-real-components-hf/crystals-and-resonators.md)).

### 4. ESP32-S3 with its PCB antenna next to a LoRa module
Espressif asks for the antenna at the board edge with ≈ 15 mm clearance and no copper under it on any layer [3]. A 900 MHz LoRa module 20 mm away on the same board couples tens of dBm into the ESP32 front end during transmission (the module's 30 dBm vs ESP32 RX blocking), and the ESP32's 2.4 GHz TX harmonics are not a problem for 915 MHz, but its digital noise is ([mixed-signal](mixed-signal-layout.md)). Put the two antennas at opposite board ends, orthogonal polarisation if possible, and time-share TX in firmware.

## Practical notes
- **Exposed (unmasked) ground copper next to RF sections** has several legitimate jobs: a **shield-can landing ring** (solderable frame), **tuning and rework pads** (space to add a shunt part or a ground strap during matching), **EMC bonding** of the board ground to an enclosure, gasket or clip, **probe ground** for scope/VNA test points, and occasionally heat spreading. It is not an antenna element; keep it stitched to L2 like any other ground copper, and keep it outside antenna keep-outs.
- **Above ≈ 10 GHz (24 GHz radar, X/Ku band)** the rules tighten: via stubs and backdrilling start to matter ([vias](vias-stitching-fencing.md) §5), connector launches need EM-optimised GCPW footprints and end-launch connectors, copper roughness (prefer VLP/HVLP foil) and soldermask (remove it over RF lines) add loss, glass-weave phase errors grow, and only 0201/01005 or thin-film parts are small enough. Use a low-loss laminate (RO4003C/RO4350B or PTFE), simulate every transition in 3-D, and expect a specialist fab rather than a budget FR-4 service ([stackups](stackups-and-materials.md), [JLCPCB](jlcpcb-rf-manufacturing.md)).
- **Modules (EBYTE E22/E220, ESP32-S3-WROOM)**: they are pre-matched; your job is the ground under them (solid L2, many vias to the module's GND pads), a clean supply, and the antenna feed. No traces under the module on L1/L2 (u-blox and EBYTE both say so for their modules) [7].
- **GNSS**: keep the RF_IN line short and away from digital; ground under the module on L1 and L2; vias around the microstrip and serial lines; ESD protection < 0.5 pF [7].
- **Test access**: add a 0 Ω/DC-block footprint oriented so it can be rotated to divert the RF path to a U.FL test connector for conducted measurements (Semtech/TI eval boards do this).
- **Unpopulated options** (alternative match topologies, SAW bypass): each unpopulated pad is a stub — keep them on the line, not on branches.
- **Soldermask over RF**: decide early; compute widths accordingly ([stackups](stackups-and-materials.md)). Mask-defined vs copper-defined pads change pad capacitance slightly.
- **Silkscreen and fiducials**: keep silkscreen off RF pads (it lifts the part); no silkscreen ink over antenna elements is needed for performance.
- **KiCad practice** (features from KiCad 7–9, from the KiCad docs/experience — verify in your version):
  - *Board Setup → Physical Stackup*: enter the JLC stackup (thicknesses, εr, mask) so the built-in calculator and DRC length/impedance tools are consistent.
  - *Net classes / constraints*: an "RF_50R" class with the 50 Ω width and ≥ 3h clearance to other nets.
  - *Rule areas (keep-outs)*: for plane voids under connector pads and antenna keep-outs on each layer.
  - *Custom pad shapes* (polygons) for tapered launches and CPWG ends; *net-tie footprints* to join a local RF ground or a star point deliberately without DRC errors.
  - *Zone connection = solid* for RF ground pads and stitching vias (no thermal spokes).
  - *Via fences / stitching*: the easyw **RF-tools-KiCAD** plugin set (via fence generator, via stitching, round tracks, tapered/mitred track wizards, mask expander) [10].
  - *Arc tracks* and *teardrops*: arcs are fine; disable teardrops on RF pads (they change pad geometry).

## Common mistakes & misconceptions
- **Routing RF through a via "because it was easier"** — each L1→L4 through-via is a discontinuity with a stub and a return-path problem ([grounding](grounding-and-return-paths.md)).
- **Matching network placed "near" the chip** (5–10 mm away) — the trace becomes part of the match.
- **Changing component size or stackup from the reference and expecting the same values** [1].
- **Sharing one ground via among several shunt parts** — common inductance couples them (TI: one via per decoupling capacitor) [1].
- **Copper pour under the antenna "for ground"** — detunes and shields it ([PCB antennas](../08-antennas/pcb-and-chip-antennas.md)).
- **"A via fence around the antenna and its matching network improves it."** A fence around the *feed line and match* is fine up to the keep-out boundary; a fence or pour around the *radiator* cancels its radiation (R_rad ∝ (kd)² near ground, Level 3 above). Never fence the radiator.
- **Crystal next to the PA** — heat-induced drift during long LoRa packets [5].
- **Thermal-relief spokes on RF ground pads** — extra inductance.
- **Obsessing over bend shape at 915 MHz** while ignoring the ground via of a shunt capacitor.

## How to simulate / verify
- `python3 tools/verify/pcb_layout_rules.py`: pad capacitance by case size on JLC stackups, effective shunt capacitance with ESL, the LC-filter trace-placement effect, mitre/bend estimates, λ/10–λ/20 lengths, and (§6) the radiation resistance of a radiator near ground (numerical vs closed form).
- Use vendor S-parameter models (Murata SimSurfing, Coilcraft, Johanson) in scikit-rf/Qucs-S with line sections for the traces ([component models](../04-real-components-hf/component-models-s2p-spice.md)).
- openEMS/Sonnet for the full match region at ≥ 2.4 GHz; compare with the reference layout's simulated S21/S22 [1].
- Bench: VNA on the matching network with the chip unpowered (small-signal) is a first check; conducted TX power and harmonics into a spectrum analyser with attenuator; frequency drift during long packets with an SDR ([test & measurement](../17-test-measurement/_index.md)).

## Open questions / gaps
- Mounted ESL values per case size are representative (0.25/0.40/0.65 nH); vendor data for specific parts on JLC-7628 would tighten the table.
- The bend capacitance is a crude ½C′W estimate; the mitre formula is quoted from secondary sources.
- KiCad feature availability changes between versions; the list above was not re-checked against KiCad 9 documentation.
- Semtech AN1200.66 (PCB design guidelines for LR11xx/SX126x) could not be retrieved in full; only its VR_PA decoupling values were seen (via search summary).

## Sources
1. Texas Instruments, *CC13xx/CC26xx Hardware Configuration and PCB Design Considerations*, SWRA640H, Dec 2018 (rev. May 2024), §4 PCB layout — stackup distance, balun symmetry, solid ground under RF path, LC filter layout, decoupling and crystal layout, DC/DC placement. (app note)
2. u-blox, *MAX-M5Q Hardware Integration Manual*, UBX-13002460 R06 — layout checklist, microstrip < 2.5 cm, ground under module, vias around RF and serial lines. (app note)
3. Espressif Systems, *ESP32-S3 Hardware Design Guidelines — PCB layout design*, https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html (accessed 2026-09-27) — 4-layer assignment, 50 Ω RF on outer layer without vias, 135°/arc bends, CLC match in 0201 near the pin, 15 mil 100 Ω stub, ≥ 9 EPAD vias, crystal ≥ 2.0 mm from clock pin, antenna ≥ 15 mm clearance. (app note)
4. R. J. P. Douville, D. S. James, "Experimental study of symmetric microstrip bends and their compensation," *IEEE Trans. MTT* 26(3), 175–182, 1978 — optimum mitre formula (as quoted in K. C. Gupta et al., *Microstrip Lines and Slotlines*, and design handbooks; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge). (peer-reviewed)
5. Semtech, AN1200.37 *SX1261/2 Recommendations for Best Performance*, rev. 1.1, Jan 2018 — PA heat → crystal drift; top-layer cuts for thermal insulation; TCXO for > 1 s packets at +22 dBm and outside −20…70 °C. (app note)
6. Semtech, AN1200.40 *SX1261/2 Reference Design Explanation*, rev. 1.1, May 2018 — E406 (2-layer), E428 (4-layer: L2 RF ground, L3 control, L4 ground), E449 (TCXO) layouts, copper void around the crystal on all layers, PA match + 2nd-harmonic trap + π LPF, RX LC balun. (app note)
7. u-blox, *MAX-M10S Integration Manual* UBX-20053088 (search summary) and MAX-M5Q manual [2] — GCPW with layer-2 ground, ground below the module on top and second layers, no signals crossing under the module. (app note)
8. Semtech, *SX1261/2 Data Sheet* (DS.SX1261-2.W.APP) rev. 1.2/2.2 — VR_PA choke current (> 130 mA for SX1262) and < 100 mV drop, RX balun layout symmetry (via search summary). (datasheet)
9. Semtech, AN1200.66 *PCB Design Guidelines for LR11xx & SX126x* — VR_PA decoupling 47 pF and 47 nF (search summary only). (app note)
10. easyw, *RF-tools-KiCAD* (GitHub) — via fence/stitching generators, round tracks, taper/mitre footprint wizards. https://github.com/easyw/RF-tools-KiCAD (software)
11. KB pages: [capacitors at RF](../04-real-components-hf/capacitors-at-rf-mlcc.md) (ESL ranges), [PCB parasitics](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md), [PCB and chip antennas](../08-antennas/pcb-and-chip-antennas.md).
12. Verification script `tools/verify/pcb_layout_rules.py` (this page).
