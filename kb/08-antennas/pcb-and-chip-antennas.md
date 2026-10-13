---
title: PCB and chip antennas — IFA, PIFA, meandered monopoles, chip antennas, ground-plane dependence, matching, module placement
domain: 08-antennas
slug: pcb-and-chip-antennas
tags: [pcb-antenna, ifa, pifa, meander, chip-antenna, ground-plane, keep-out, pi-network, matching, esp32, 868mhz, 915mhz, 2.4ghz, 433mhz, ti-dn007, ti-dn023, ti-dn024, ti-an043, johanson, ignion]
prerequisites: [antenna-fundamentals.md, dipoles-and-monopoles.md, small-antenna-limits.md, ../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md, ../03-transmission-lines-matching/smith-chart.md]
related: [antenna-matching-and-baluns.md, antenna-measurement.md, gnss-antennas.md, antennas-on-rockets.md, ../13-pcb-rf-layout-emc/rf-layout-rules.md, ../13-pcb-rf-layout-emc/stackups-and-materials.md, ../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md, slot-antennas.md, multiband-and-wideband-antennas.md, antenna-identification-guide.md]
level: mixed
confidence: high
last_updated: 2026-10-02
---

# PCB and chip antennas

## Questions this page answers
- How does an inverted-F (IFA) antenna work, and why is there a short to ground next to the feed?
- Can I just copy TI's 2.4 GHz or 868/915 MHz PCB antenna? What must match?
- Why does my chip antenna perform far worse than its datasheet?
- How big must the ground plane be, and what is the "keep-out" area?
- How do I design the pi-matching network, and what do I measure to tune it?
- Where should an ESP32 module (with PCB antenna) go on my board?
- Is a PCB antenna viable at 433 MHz on a flight computer?
- PIFA vs IFA vs meandered monopole vs chip — which do I choose?
- How close can an antenna be to metal (an enclosure, a battery, a carbon-fibre tube)?
- Which antennas work on or inside metal?
- How do I make one PCB antenna cover 315 and 433 MHz?

## TL;DR
- Almost every PCB/chip antenna is a **monopole whose other half is the board's ground plane** (plus attached cables). Ground size, shape, nearby parts and the enclosure set its tuning, pattern and efficiency. Vendor numbers apply only to *their* board (TI AN058 [4]; Johanson [8]; Ignion [9]).
- **IFA**: a λ/4 monopole bent parallel to the ground edge (inverted-L) plus a short-circuit stub that taps the impedance to ≈ 50 Ω without components. TI's DN007 2.4 GHz IFA is 25.7 × 7.5 mm on 1 mm FR-4: 1.1/3.3/1.6 dBi peak by plane, RL < −15 dB, > 300 MHz with < 10 % reflection [1]. TI's DN023 868/915 MHz IFA is 43 × 20 mm on 0.8 mm FR-4 with a 31 × 45 mm ground: ≈ 50 MHz bandwidth, max gain −0.12 dBi [2].
- **Meandered monopole**: TI's DN024 (38 × 25 mm antenna, 43 × 63 mm ground, 1.6 mm FR-4) measured **97.7 % efficiency, 5.05 dBi peak** at 868 MHz (CTIA OTA) and 73 MHz VSWR-2 bandwidth with a 1.8 nH/2.7 pF match [3].
- **Chip antennas** trade size for efficiency and bandwidth: Johanson's 25 × 5 mm 433 MHz chip: −4.0 dBi average gain on its evaluation board, but **−7.2 dBi** and RL ≥ 5 dB only on a "larger PCB" without retuning [8]. Ignion's 30 × 3 mm TRIO mXTEND on a 142 × 60 mm board: > 50–55 % efficiency, 1.1–1.5 dBi at 698–960 MHz with a 40 × 12 mm clearance and an LC match [9].
- **Always lay out a pi (shunt–series–shunt) network** at the feed; start with 0 Ω/NC and tune with a VNA on the final board in its enclosure (TI [4], Johanson [8], Espressif's "CLC" [10]).
- **Keep-out**: no copper on any layer under the antenna element, no components or traces near its open end; TI DN023 asks ≥ 5 mm from the antenna sides (≥ 15 mm if a ground plane runs alongside) [2]; Espressif recommends ≥ 15 mm clearance around a module's PCB antenna in the housing and placing the antenna beyond the board edge [10].
- At **433 MHz** a PCB/chip antenna on a small flight-computer board is fundamentally inefficient (Chu–McLean; [small-antenna limits](small-antenna-limits.md)); use a λ/4 whip with a counterpoise, or a dipole, via the module's SMA/IPEX connector.

## Intuition (no math)
Take a λ/4 monopole standing on a ground plane and fold it over so it runs parallel to the ground edge: it now fits on a PCB, but it sits very close to the ground, so its radiation resistance drops (the image current nearly cancels it) and it becomes capacitive. Add a short from the element to ground near the feed: the short and the feed form a little loop that acts as an inductive shunt; sliding the feed along the element relative to the short picks off whatever impedance you want — like tapping a transformer. That is the **inverted-F**. A **PIFA** makes the horizontal arm a plate (wider → more bandwidth). A **meander** crams more conductor length into the same length, lowering the resonance; the price is lower radiation resistance, narrower bandwidth, and more sensitivity to loss. A **chip antenna** is a meander or helix inside a high-permittivity ceramic, which shrinks it further — and makes it even more of a small antenna.

Because the ground plane carries the "other half" of the current, the board dimension parallel to the antenna often matters more than the antenna itself: a 2.4 GHz antenna on a board ~λ/4 or larger (≥ 30 mm) behaves well; an 868 MHz antenna wants a ground ~λ/4–λ/2 long (80–170 mm) for best efficiency; at 433 MHz that means 170–350 mm — larger than most flight computers.

## The math

### Level 1 — resonant length and impedance tapping
- **Resonance**: total conductor length from the shorting point (or the feed, for a meander) to the open end ≈ λ_eff/4, with λ_eff = λ₀/√ε_eff. For a trace on FR-4 with no ground underneath, ε_eff ≈ (εr + 1)/2 ≈ 2.7 is an upper bound (air on one side); the field is only partly in the substrate, so real ε_eff is closer to 1.5–2.5 depending on trace width and board thickness. Example: 2.45 GHz, λ₀/4 = 30.6 mm; DN007's main arm is 25.6 mm — consistent with ε_eff ≈ 1.4 plus the bends and the shorting-stub geometry. **Do not design from this formula; copy a reference design exactly or simulate.**
- **Impedance of an IFA**: the feed-to-short spacing s sets the tap ratio; larger s → higher input resistance. An approximation treats the feed–short segment as a shorted transmission-line stub in parallel with the radiating arm; the reactances cancel at resonance.
- **Matching network**: for a measured Z_A at the feed, choose an L or pi network (Smith chart). Two components suffice for a single frequency; the third gives a Q/bandwidth degree of freedom ([impedance matching](../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md)).

### Level 2 — why the ground plane dominates
For a monopole-type antenna, the current on the ground plane is equal and opposite to the antenna current at the feed and spreads over the board. If the board's length along the antenna axis is L_g, the "dipole" formed by element + ground has an arm L_g. When L_g ≈ λ/4 the combination is close to a resonant asymmetric dipole with healthy radiation resistance; when L_g ≪ λ/4 the ground arm is electrically short, radiation resistance and efficiency fall, and currents spill onto cables. This is why TI's 169 MHz antenna on a board sized for 868 MHz measured 7 % vs 91 % [4] and why Ignion characterises its chip on boards of 126–142 mm length [9]. Chu–McLean applies to the sphere enclosing *board plus antenna* ([small-antenna limits](small-antenna-limits.md)).

**Near-field loading.** The antenna's reactive field extends ≈ λ/2π (19 mm at 2.45 GHz, 52 mm at 915 MHz). Dielectric (plastic, FR-4, a hand, a nose cone) in that region adds capacitance → resonance shifts *down*; metal nearby (battery, shield can, LCD) shorts out part of the field → shifts and efficiency loss. Keep-out rules are simply "keep the reactive region empty".

### Level 3 — measurement subtleties and limits
- Measuring a small antenna with a coax cable perturbs it: TI AN043 notes that moving the semi-rigid cable changed resonance by 5–10 MHz and reflection by 3–4 dB on a 2.4 GHz dongle antenna [5]. Use ferrite beads on the cable, route it away from the antenna along the ground, and/or measure efficiency over the air.
- Ground-plane size changes bandwidth, not just tuning: AN043's USB dongle antenna had ≈ 250 MHz bandwidth alone and ≈ 100 MHz when plugged into a laptop [5].
- Harmonics: the antenna radiates the PA's harmonics wherever it has gain; a dual-band antenna (DN024 dual-band mode: 868 MHz and 2.44 GHz) will radiate the 868 MHz third harmonic at 2.6 GHz efficiently — filter the PA [3].

## Reference designs (measured, from the app notes)

| Design | Band | Size (antenna) | Board/ground | Substrate | Result | Source |
|---|---|---|---|---|---|---|
| TI DN007 IFA | 2.4–2.4835 GHz | 25.7 × 7.5 mm | CC2430DB | FR-4 1.0 mm | 1.1 / 3.3 / 1.6 dBi (XY/XZ/YZ); RL < −15 dB; > 300 MHz at < 10 % refl. | [1] |
| TI AN043 IFA (USB dongle) | 2.4 GHz | 15.2 × 5.7 mm | dongle | FR-4 | VSWR < 2 over ISM; BW ≈ 250 MHz free, ≈ 100 MHz in laptop | [5] |
| TI DN023 IFA | 868/915/955 MHz | 43 × 20 mm | 31 × 45 mm | FR-4 0.8 mm | ≈ 50 MHz (<10 % refl.), max gain −0.12 dBi; tune by L6 (≈ 9 mm @868, 1 mm @915); 955 MHz only ≈ 25 MHz | [2] |
| TI DN024 meander monopole | 868/915/920 (+2.44 GHz) | 38 × 25 mm | 43 × 63 mm (board 45 × 95) | FR-4 1.6 mm | 97.7 % eff., 5.05 dBi peak (868); VSWR-2 BW 73 MHz; match 1.8 nH series / 2.7 pF shunt | [3] |
| Johanson 0433AT62A0020 chip | 423–443 MHz | 25 × 5 × 1.2 mm | Johanson evaluation board EB1 (see datasheet drawing) | — | −4.0 dBi avg gain, RL ≥ 9.5 dB (EVB1); larger PCB: −7.2 dBi avg, RL ≥ 5 dB | [8] |
| Ignion NN03-310 TRIO mXTEND chip | 698–960 MHz (+1.7–2.7 GHz) | 30 × 3 × 1 mm | 142 × 60 mm, clearance 40 × 12 mm | FR-4 1 mm | > 50–55 % avg eff., 1.1–1.5 dBi peak, VSWR < 3 | [9] |

### Antennas near or on metal, and dual-band SRD boards
**Near a conducting sheet** a parallel dipole sees its antiphase image: own MoM at 433 MHz (`tools/verify/ant2_qa.py` §d) — feed R = 90, 34, 22, 5.6, 0.9, 0.2 Ω at spacings of 0.25, 0.125, 0.1, 0.05, 0.02, 0.01 λ (173 mm … 7 mm), with the resonance pulled as well. With just 2 Ω of unavoidable loss (connector, match, conductor) the efficiency is 98 %, 94 %, 92 %, 74 %, 30 %, 9 %. Rule: keep wire/IFA-type antennas ≥ λ/10 (≈ 70 mm at 433 MHz, 33 mm at 915 MHz) from large metal or carbon fibre, or use an antenna that *needs* the metal: a **patch or PIFA** (the metal is its ground), a **slot or edge notch cut in the metal** ([slot antennas](slot-antennas.md), e.g. the 915 MHz edge notch), or for 13.56 MHz a coil on a **ferrite sheet** ([inductive coupling](inductive-coupling-rfid-nfc-wpt.md#level-3--limits-and-refinements)). Putting a finished radio in a metal or carbon box without an external antenna typically costs tens of dB; in plastic it mainly detunes (retune in the box).
**Dual-band 315/433 MHz** (D1 #129): the bands are only 1.37:1 apart, so either (i) one antenna with a dual-resonant matching network (each band then has the efficiency of a small antenna at that frequency), (ii) two branches (a longer and a shorter meander/IFA arm from one feed, tuned on the real board), or (iii) a wire whip with a trap. TI DN024's dual-band option (868 MHz + 2.44 GHz) shows the same idea for widely spaced bands [3]; for closely spaced 315/433 MHz no reference design was found here, so expect to tune each branch with the ground plane and enclosure in place (openEMS model recommended).

## Design equations & rules of thumb

| Rule | Value / guidance |
|---|---|
| Copy exactly | same substrate thickness/εr, copper, ground outline, keep-out (TI [1]–[3], [5]) |
| Ground length along the antenna | ≥ λ/4 for good efficiency (≈ 31 mm @2.45 GHz, 82 mm @915 MHz, 173 mm @433 MHz) |
| Keep-out under antenna | no copper on any layer; no parts/traces near the open end |
| Side clearance | ≥ 5 mm (TI DN023), ≥ 15 mm to adjacent ground planes/housing (DN023, Espressif) |
| Feed point | at the board edge; antenna beyond the edge if possible (Espressif) |
| Matching footprint | pi network (0402), placed at the feed; start 0 Ω / NC |
| Thickness change | thinner/thicker PCB → antenna slightly longer/shorter (AN043) |
| Enclosure | plastic within the near field lowers f by several %; tune in the enclosure |
| Efficiency expectations | 2.4 GHz IFA 60–90 %; 868/915 MHz IFA/meander on ≥ 40 × 60 mm ground 50–95 %; 433 MHz chip on small board 5–30 % |

## Worked examples

**Example 1 — A 915 MHz PCB antenna for a ground-station tracker board.** Board 60 × 100 mm, 1.6 mm FR-4. Use TI DN024's meander (38 × 25 mm) at one short edge with the 100 mm dimension along the antenna's radiating direction; DN024's own ground was 43 × 63 mm, so expect the resonance to move *down* on the larger ground (DN024 notes L4 must be shortened for larger grounds [3]). Lay out the pi network; after assembly and enclosure, measure S11, then trim the last meander segment (or retune the pi) for minimum reflection across 902–928 MHz.

**Example 2 — Designing the match from a measurement.** Measured (after port extension to the feed pad) Z_A = 20 − j35 Ω at 915 MHz. R < 50 Ω, so use a series element then a shunt element toward the 50 Ω side: Q = √(50/20 − 1) = 1.225; series reactance +Q·R − X_A = 24.5 + 35 = 59.5 Ω → **L = 10.35 nH**; shunt susceptance Q/50 = 0.0245 S capacitive → **C = 4.26 pF** on the transceiver side. Our check: return loss −73 dB at 915 MHz and −32 dB at 902/928 MHz (for a frequency-independent Z_A; a real antenna's Z_A varies, so re-measure). In a pi footprint: shunt(NC) – series(10 nH) – shunt(4.3 pF → nearest 4.3 pF C0G). See [Smith chart](../03-transmission-lines-matching/smith-chart.md).

**Example 3 — ESP32-S3 module on the Avionics-B coprocessor board.** Place the module at a board edge with its PCB antenna *overhanging* the edge (or with the base board cut away under and beside it), feed point close to the edge, solid ground and via stitching up to the antenna boundary, ≥ 15 mm clearance to housing/metal in all directions (Espressif [10]); keep the ESP32 antenna away from the LoRa antenna and the GNSS patch (Wi-Fi/BLE at 2.4 GHz is out of band for both but its PA noise and harmonics are not). Inside a fibreglass airframe, 2.4 GHz still works; inside CFRP it does not. (The team's ESP32-S3 used an external-antenna module, which avoids the board-edge constraint but needs the same care with the external antenna's placement and cable.)

**Example 4 — Should Avionics-C use a 433 MHz chip antenna?** Board ≈ 40 × 80 mm → enclosing sphere a ≈ 45 mm → ka ≈ 0.41 → Q_min ≈ 17; bandwidth isn't the limit, but a 25 mm chip on this ground performs like Johanson's "larger PCB"/eval-board range, i.e. roughly −4 to −7 dBi average gain [8] versus ≈ 0–2 dBi for a λ/4 whip with a counterpoise — a 5–9 dB penalty that equals halving or quartering the range. Use the SMA/IPEX connector and a proper external antenna.

## Practical notes
- **Stack-up**: the antenna region should have no inner-layer copper; on a 4-layer board, pull back all planes under the antenna and keep a clean ground edge ([stack-ups](../13-pcb-rf-layout-emc/stackups-and-materials.md), [RF layout rules](../13-pcb-rf-layout-emc/rf-layout-rules.md)).
- **Feed line**: 50 Ω CPWG from the radio to the matching network to the antenna; keep it short; stitch vias along it.
- **Components near the antenna**: batteries, buzzers, connectors and screws within the keep-out detune; so do mounting standoffs.
- **Solder mask, conformal coat, potting**: all lower the resonance (thin mask: small; potting compound εr ≈ 3–4 around the antenna: large). Tune after coating.
- **Production variation**: FR-4 εr tolerance and etch tolerance shift resonance by ~1–3 %; broadband designs (DN007's 300 MHz) are robust, narrowband chips are not.
- **Measure over the air**: stepped-CW power sweep with a spectrum analyser (max hold) as TI does [1], [4]; relative results are enough to centre the antenna.

## Common mistakes & misconceptions
- **"The chip antenna is 50 Ω, no matching needed."** Only on the vendor's board; leave the pi footprint (Johanson, TI) [4], [8].
- **"Ground plane under the antenna improves it."** Copper under an IFA/monopole element kills it (shorts the fringing field); the ground must stop at the antenna edge.
- **"A PCB antenna copied from a 1.6 mm reference works on my 0.8 mm board."** Retune: the thickness changes ε_eff and the resonance (AN043 [5]).
- **"The antenna is fine; the range problem is the radio."** On small boards the antenna is usually the dominant loss; measure TRP/efficiency or compare against a reference whip.
- **"Fractal chip antennas are fundamentally better."** No (Best 2003; [small-antenna limits](small-antenna-limits.md)); compare measured efficiency on your board size.
- **"Module antennas can go anywhere."** Espressif explicitly warns against centring the module with a keep-out hollowed on all sides; the antenna should be at the edge [10].
- **"A via fence (or ground ring) around the chip antenna keeps board noise out of it."** An antenna's job is to couple to fields in its reactive region (≈ λ/2π: 52 mm at 915 MHz, 19 mm at 2.45 GHz); grounded copper or vias placed there detune it and short its fringing field exactly like a ground pour under it, so efficiency drops — the keep-out must stay empty (≥ 5 mm side clearance, ≥ 15 mm where ground runs alongside, TI DN023 [2]; Espressif [10]). You cannot "shield" an antenna on the board without shielding the wanted signal too. Board noise is fixed at the **source**: shield cans over the MCU/DC-DC/SDRAM, filtered and short return paths, spread-spectrum or slower clock edges, and correct grounding of the feed. Via stitching *is* right along the CPWG feed line and along the edge of the ground plane *up to* the keep-out boundary — not around the radiator. (Myth flagged by W4-D1, electronics.stackexchange.com/q/41871; layout detail in [13 vias & fencing](../13-pcb-rf-layout-emc/vias-stitching-fencing.md).)
- **"Fill every free area with ground copper."** Good practice for the digital/RF circuit area (stitched to the main ground), wrong inside an antenna keep-out, and harmful as unstitched islands, which can resonate; see the ground-under-antenna entry above and [13 grounding](../13-pcb-rf-layout-emc/grounding-and-return-paths.md).
- **App-note physics caveat**: TI AN058's introduction describes an antenna as "basically an air core inductor" and says the λ/2 dipole "produces most power at the ends" [4]; both statements are wrong as physics (the λ/2 dipole's current and radiating strength peak at the centre — [dipoles-and-monopoles](dipoles-and-monopoles.md)). The app note's *practical* guidance is sound.

- **"Any antenna can sit against the metal case."** A dipole λ/50 from metal has R ≈ 0.9 Ω (MoM) — almost all power goes into loss; choose patch/PIFA/slot types for on-metal mounting or keep ≥ λ/10 clearance.
- **"A full-metal laptop or phone can't have internal antennas."** The metal itself is used as the antenna via slots and gaps ([slot antennas](slot-antennas.md#slot-in-a-ground-plane--enclosure-wi-fi-in-metal-laptops-metal-airframes)).

## How to simulate / verify
- openEMS (free) or a commercial FDTD/MoM with dielectric (Sonnet, CST, HFSS, Ansys/Altair FEKO): model the full board outline, substrate, ground cut-outs and enclosure; NEC-2 is **not** suitable for PCB antennas on dielectric (Cebik [11]; [simulation](antenna-simulation-nec-openems.md)).
- VNA procedure: calibrate at the cable end, solder a semi-rigid (or U.FL test pigtail) to the feed pad, apply port extension/electrical delay to the pad (open/short trick in AN058 [4]), add ferrite on the cable, then tune the pi network.
- `python3 tools/verify/ant_small_limits.py` — check whether your board size can support the bandwidth you need.

## Open questions / gaps
- A simulated (openEMS) efficiency vs ground-plane length curve for DN023/DN024-style antennas at 915 MHz would quantify the "≥ λ/4 ground" rule.
- Taoglas and Molex chip-antenna ground-plane guidance was not retrieved in this pass.
- EBYTE module antenna connector variants and stock antenna performance for E22-400T33D/E220-900T30D should be documented in domain 15/18.

## Sources
1. TI, *2.4-GHz Inverted F Antenna*, Design Note DN007 (SWRU120D), 2007/2019 — dimensions, 1 mm FR-4, gains by plane, reflection < −15 dB, > 300 MHz bandwidth, pi-network recommendation, avoid ground near antenna ends. https://www.ti.com/lit/pdf/swru120 (app note, measured)
2. F. Kervel, TI Design Note DN023 (SWRA228), *868 MHz, 915 MHz and 955 MHz Inverted F Antenna* — 43 × 20 mm, 0.8 mm FR-4, 31 × 45 mm ground, −0.12 dBi, ≈ 50 MHz BW, L6 tuning, ≥ 5 mm / 15 mm clearances, 1300 m range at 38.4 kBaud. https://www.ti.com/lit/swra228 (app note, measured)
3. R. Wallace, TI Design Note DN024 (SWRA227), *Monopole PCB Antenna with Single or Dual Band Option* — CTIA OTA table (TRP, efficiency 97.7 %, peak 5.05 dBi), match values, BW 73 MHz, harmonic caveat. https://www.ti.com/lit/pdf/swra227 (app note, measured)
4. R. Wallace, TI Application Note AN058 (SWRA161), *Antenna Selection Guide* — antenna types, chip-antenna caveats, same-area 868 vs 169 MHz efficiency, measurement methods, pi-network. https://www.ti.com/lit/pdf/swra161 (app note)
5. A. Andersen, TI Application Note AN043 (SWRA117), *Small Size 2.4 GHz PCB antenna* — 15.2 × 5.7 mm IFA, VSWR < 2, coax-placement sensitivity (5–10 MHz, 3–4 dB), BW 250 → 100 MHz with laptop, thickness compensation. https://www.ti.com/lit/pdf/swra117 (app note, measured)
6. C. A. Balanis, *Antenna Theory*, 4th ed., 2016 — §14.x PIFA/IFA and small antennas. (textbook)
7. K.-L. Wong, *Planar Antennas for Wireless Communications*, Wiley, 2003 — PIFA/IFA design. (textbook; cited from general knowledge)
8. Johanson Technology, *433 MHz ISM Antenna SMD 0433AT62A0020E* datasheet v3.0, 2018 — mounting considerations 1 (EVB1: −4.0 dBi, RL ≥ 9.5 dB) and 2 (larger PCB: −7.2 dBi average, RL ≥ 5 dB); pi network advice. https://www.johansontechnology.com/datasheets/antennas/0433AT62A0020.pdf (datasheet)
9. Ignion, *TRIO mXTEND NN03-310 User Manual*, Dec 2025 — efficiency > 50–55 %, peak 1.1–1.5 dBi at 698–960 MHz on 142 × 60 mm board, 40 × 12 mm clearance, LC matching. https://ignion.io/files/UM_NN03-310.pdf (manufacturer manual)
10. Espressif, *ESP Hardware Design Guidelines — ESP32-S3 PCB layout design* — module antenna beyond board edge/feed near edge, cut-outs, ≥ 15 mm clearance, CLC matching for chip-down PCB antennas. https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html (manufacturer guideline)
11. L. B. Cebik, "When not to use NEC" (amod128) — PCB antennas with substrates need other solvers. https://antenna2.github.io/cebik/content/amod/amod128.html (expert article)
