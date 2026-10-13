---
title: PCB substrates for RF — what JLCPCB, PCBWay, OSH Park and Aisler actually offer (FR-4 grades, RO4350B, PTFE), cost, lead time and when low-loss laminate is worth it
domain: 18-components-parts
slug: pcb-substrates-parts
tags: [pcb, laminate, substrate, fr-4, tg155, 7628, 3313, rogers, ro4350b, ro4003c, ptfe, zyf255da, fr408hr, jlcpcb, pcbway, osh-park, aisler, cost, lead-time, design-dk, process-dk]
prerequisites:
  - ../13-pcb-rf-layout-emc/stackups-and-materials.md
  - ../02-electromagnetics/dielectrics-permittivity-loss-tangent.md
related:
  - ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md
  - ../13-pcb-rf-layout-emc/jlcpcb-rf-manufacturing.md
  - ../08-antennas/patch-antennas.md
  - ../12-phased-arrays/beamforming-architectures.md
  - sourcing-and-eval-boards.md
  - phased-array-and-radar-parts.md
level: intro
confidence: medium
last_updated: 2026-09-29
---

# PCB substrates for RF — what the fabs offer, cost, and when it is worth it

> Physics and stackup geometry (50 Ω widths, Dk dispersion, loss per cm) live in
> [stackups & materials](../13-pcb-rf-layout-emc/stackups-and-materials.md) and
> [dielectrics](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md). This page is the
> *procurement* view: which laminate you can actually order where, for how much, and the ordering gotchas.

## Questions this page answers
- Can I get Rogers or PTFE boards from JLCPCB, in how many layers and thicknesses, and what does it cost?
- What do PCBWay, OSH Park and Aisler offer for RF work?
- Is plain FR-4 good enough for 433 MHz, 915 MHz, GNSS, 2.4 GHz, 5.8 GHz, 24 GHz?
- Which Dk do I type into my calculator when the fab says "RO4350B, Dk 3.48"?
- What should I tick on the JLC order form for an impedance-controlled RF board?

## TL;DR
- **JLCPCB FR-4**: impedance-controlled 4/6-layer stackups with published prepreg Dk — 7628 = 4.4, 3313 = 4.1, 2116 = 4.16, 1080 = 3.91; core 4.6; soldermask Dk 3.8; 2-layer FR-4 Dk quoted 4.5 [1][2]. Order **FR-4 TG155** when you ask for impedance control (the calculator assumes it; the default TG135-140 material is unspecified) [5].
- **JLCPCB high-frequency**: **2-layer only**, 1 oz copper; **Rogers RO4350B** (Dk 3.48 process value, Df 0.0037) at 0.51 / 0.76 / 1.52 mm (finished 0.6 / 0.9 / 1.65 mm); **PTFE** "ZYF" laminates at 0.76 / 1.52 mm — ZYF255DA (Dk 2.55, Df 0.0018), ZYF265D (2.65, 0.0019), ZYF300CA-C (2.94, 0.0016), ZYF300CA-P (3.00, 0.0018); promotional price for 5 pcs ≤ 100 × 100 mm: **Rogers from US$99.5, PTFE from US$50.5** (JLC news article) [3]; a newer JLC HF page quoted "from US$47" (per [5]) — prices change, re-quote. No hybrid Rogers + FR-4 multilayers.
- **PCBWay**: FR-4 plus Rogers RO4000-series (incl. Rogers-4 + FR-4 mixed stackups with ShengYi/RO4403 prepreg, pure RO4000 multilayers with 4450F prepreg), PTFE and PTFE + FR-4 hybrids; "pure PTFE multilayer" not possible [4]. Use PCBWay (or an RF-specialist fab) when you need a **4-layer board with a low-loss RF layer**.
- **OSH Park**: 4-layer boards use **Isola FR408HR** (prepreg 2113, 0.1999 mm, Dk 3.61 @ 1 GHz; ENIG, purple mask), US$10/in² per 3 boards, 9–14 days; 2-layer US$5/in² per 3 [6][7]. A 2025 notice warned of a possible future stackup change due to material availability [6]. Measured by one user to beyond 50 GHz (lossy but usable for short lines) with Z₀ reading ~56 Ω high with the published Dk (anecdotal, 2018) [8].
- **Aisler** (EU): standard FR-4 2/4+ layers, fast European manufacturing (from 2 business days); no RF laminates listed [9].
- **When is low-loss laminate worth it?** Per the 13-domain page: FR-4 50 Ω line ≈ 0.05 dB/cm at 915 MHz, 0.12 dB/cm at 2.45 GHz, 0.24 dB/cm at 5.8 GHz vs ≈ 0.05 dB/cm on 0.508 mm RO4350B at 5.8 GHz [5]. FR-4 is fine for 433 MHz–2.4 GHz front ends with cm-scale traces; use RO4350B/PTFE for **patch antennas and arrays ≥ 5 GHz, filters/couplers whose frequency depends on Dk, long feed networks, and anything at 24 GHz**.
- **Design Dk vs process Dk**: Rogers quotes RO4350B process Dk 3.48 ± 0.05 but design Dk **3.66** (RO4003C 3.38 / 3.55) — use the design value in circuit models; the difference is ≈ 2.5 % in resonant frequency [5][10].

## Intuition (no math)
Every dB lost in a PCB trace before the LNA or after the PA costs link margin, and every percent of Dk uncertainty moves the frequency of anything resonant (filters, patches, couplers, stubs). FR-4 is a glass-epoxy mixture with fairly high loss tangent (≈ 0.017–0.025) and a Dk that varies with glass style, resin content, frequency and batch; low-loss laminates (Rogers RO4000 hydrocarbon-ceramic, PTFE) have 5–10× lower loss tangent and tight, documented Dk. At 433–915 MHz your traces are a few percent of a wavelength and FR-4 loss is negligible; at 5.8 and 24 GHz a 10 cm array feed on FR-4 can lose several dB and detune.

The practical constraint at hobby/prototype fabs is *layer count*: JLCPCB's low-loss boards are 2-layer only, so a flight computer that needs 4+ layers for digital routing stays on FR-4 (keep RF runs short), while antennas, arrays, filters and radar front ends go on separate 2-layer Rogers/PTFE boards.

## The math
### Level 1 — dielectric loss per unit length
For a TEM-like line, dielectric attenuation is
$$\alpha_d \approx 27.3\,\frac{\sqrt{\varepsilon_{eff}}}{\lambda_0}\,q\,\tan\delta\quad[\text{dB/m}]$$
($q$ = filling factor ≈ $(\varepsilon_{eff}-1)/(\varepsilon_r-1)\cdot\varepsilon_r/\varepsilon_{eff}$ for microstrip), i.e. proportional to frequency and to $\tan\delta$ ([dielectrics](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md)). Conductor loss grows as $\sqrt f$ plus roughness. Rule: FR-4's dielectric loss overtakes conductor loss above ≈ 1–2 GHz on typical 50 Ω lines.

### Level 2 — frequency shift from Dk error
A resonator's frequency scales as $f \propto 1/\sqrt{\varepsilon_{eff}}$, so $\Delta f/f \approx -\tfrac12\,\Delta\varepsilon_{eff}/\varepsilon_{eff}$. Using RO4350B process Dk 3.48 instead of design Dk 3.66 (5 % in $\varepsilon_r$, ~4 % in $\varepsilon_{eff}$ for a microstrip) mis-predicts a patch by ≈ 2–2.5 %: at 5.8 GHz that is ~130 MHz — larger than a patch's bandwidth ([patch antennas](../08-antennas/patch-antennas.md)).

### Level 3 — cost per dB
Decide by total loss saved, not material prestige: $\Delta L = (\alpha_{FR4}-\alpha_{RO})\,\ell$. For a 5.8 GHz 4 × 4 patch array with ≈ 10 cm of corporate feed: $(0.24-0.05)$ dB/cm × 10 cm ≈ **1.9 dB** saved (≈ 35 % more received power per element path) for ~US$50–100 extra per prototype batch — clearly worth it. For a 433 MHz LoRa board with 3 cm of trace: $(0.03)$ dB saved — not worth it.

## Design equations & rules of thumb
| Rule | When valid | Typical values |
|---|---|---|
| FR-4 OK if trace loss < 0.3 dB and nothing resonant depends on Dk | ≤ 2.4 GHz, cm-scale traces | 915 MHz: 0.05 dB/cm on JLC-7628 [5] |
| Low-loss laminate for ≥ 5 GHz feeds, patches, filters, arrays | resonant/long structures | 5.8 GHz: FR-4 0.24 vs RO4350B 0.05 dB/cm [5] |
| Use design Dk, not process Dk | Rogers | RO4350B 3.66; RO4003C 3.55 [10] |
| $\Delta f/f \approx -\tfrac12\Delta\varepsilon_{eff}/\varepsilon_{eff}$ | resonators | 5 % Dk error → ~2–2.5 % frequency error |
| JLC HF boards: 2 layers, 1 oz, ENIG | ordering | [3][5] |
| Order TG155 for impedance-controlled FR-4 | JLC multilayer | [5] |

## Comparison tables
### A. Laminates you can order (as of 2026-09; re-check each fab's page)
| Fab | Material | Layers | Thickness | Dk / Df (fab or datasheet) | Price hint | Lead time |
|---|---|---|---|---|---|---|
| JLCPCB | FR-4 (TG135-140 default, TG155 option) | 1–20+ | 0.4–2.0+ mm | prepreg 7628 4.4, 3313 4.1, 2116 4.16, 1080 3.91; core 4.6; 2L 4.5 [1][2] | 5 × 100×100 mm 2L ≈ a few US$ (promo; unverified today) | days |
| JLCPCB | **Rogers RO4350B** | **2** | 0.51 / 0.76 / 1.52 mm (finished 0.6 / 0.9 / 1.65) | 3.48 process (3.66 design) / 0.0037 [3][10] | from US$99.5 (5 pcs ≤ 100×100 mm, news) [3]; "from US$47" (later page, per [5]) | quote |
| JLCPCB | **PTFE ZYF255DA / ZYF265D / ZYF300CA-C / ZYF300CA-P** | **2** | 0.76 / 1.52 mm | 2.55/0.0018; 2.65/0.0019; 2.94/0.0016; 3.00/0.0018 [3] | from US$50.5 (5 pcs, news) [3] | quote |
| PCBWay | FR-4 (ShengYi), IT158/IT180A, Rogers RO4000 (pure multilayer with 4450F prepreg; RO4000+FR-4 mixed), PTFE, PTFE+FR-4 | 2–multilayer | per quote | per material datasheet | quote (higher than JLC for HF, unverified) | 3–10 working days for stocked Rogers (search extract) [4] |
| OSH Park | FR-4 (2L), **Isola FR408HR** (4L) | 2 / 4 | 1.6 mm (2L; 0.8 mm option), 4L 2113 prepreg 0.1999 mm | FR408HR 3.61 @ 1 GHz (prepreg) [6] | 2L US$5/in² per 3; 4L US$10/in² per 3 [7] | 9–14 calendar days (4L) |
| Aisler | FR-4 | 2 / 4+ | standard | not published as RF material | from €14.20 | from 2 business days (EU) [9] |
| RF-specialist fabs (Europe/US/China) | RO4003C, RO3003, RT/duroid 5880, Taconic, Megtron 6, hybrids | any | any | datasheet | US$100s–1000s per prototype run | 1–3 weeks |

### B. Material properties to put in your models (from the 13/02 domain pages and datasheets)
| Material | Design Dk (≈ 1–10 GHz) | Df | Notes |
|---|---|---|---|
| JLC FR-4 7628 prepreg | 4.4 (fab) | ≈ 0.017–0.025 (typ.) | Dk falls ~0.1 per decade [5] |
| Isola FR408HR (OSH Park 4L) | 3.61–3.67 | ≈ 0.009–0.012 (datasheet class) | "low-loss FR-4" [6][8] |
| Rogers RO4003C | 3.55 (process 3.38) | 0.0027 @ 10 GHz | not flame-rated (UL 94 V-0 is RO4350B) [10] |
| Rogers RO4350B | 3.66 (process 3.48) | 0.0037 @ 10 GHz | JLC 2-layer [3][10] |
| JLC ZYF255DA PTFE | 2.55 | 0.0018 | soft, needs care in handling and plating [3] |
| RT/duroid 5880 (PTFE/glass microfibre) | 2.20 | 0.0009 | mmWave, specialist fabs |

## Worked examples
### 1. 433 MHz flight computer — FR-4 or Rogers?
50 Ω CPWG from SX1268 to U.FL: 3 cm on JLC 4-layer 7628. Loss ≈ 0.03 dB/cm at 433 MHz (scaling the 0.05 dB/cm @ 915 MHz figure roughly with $f$) → ≈ 0.1 dB. **FR-4 TG155**, JLC04161H-7628, mask-aware width from the JLC calculator [5]. Rogers would save < 0.1 dB and force 2 layers.

### 2. 5.8 GHz 4 × 4 patch array
Feed ≈ 10 cm → FR-4 ≈ 2.4 dB vs RO4350B 0.51 mm ≈ 0.5 dB [5]: order a separate 2-layer **RO4350B 0.76 mm** (or PTFE ZYF265D) board from JLC for the antenna/feed, design with Dk 3.66, and keep the beamformer/digital electronics on a 4-layer FR-4 board connected by coax — see [phased-array & radar parts](phased-array-and-radar-parts.md).

### 3. 24 GHz radar front end
At 24 GHz FR-4 loss is several dB per 10 cm and Dk tolerance shifts antenna patterns; use RO4350B/RO4003C or PTFE (or buy a radar module with antenna-in-package — [radar parts](phased-array-and-radar-parts.md)). JLC's 0.51 mm RO4350B gives a 50 Ω microstrip ≈ 1.1 mm wide (compute with the design Dk; value here unverified), acceptable up to ~30 GHz on short lines.

## Practical notes
- **Tell the fab what you mean**: impedance control on; stackup name (e.g. JLC04161H-7628); material TG155; soldermask over RF traces or not (changes width) — [stackups & materials](../13-pcb-rf-layout-emc/stackups-and-materials.md).
- **ENIG on HF boards**: JLC's Rogers/PTFE boards are ENIG; nickel under the gold raises surface loss on exposed RF copper at ≥ 2.4 GHz — mask RF traces or accept a small penalty [5].
- **PTFE handling**: soft laminate; avoid flexing, thin copper features can lift; drills and plating are harder — keep via counts modest and pads generous (fab guidance, general).
- **Panel coupons**: add a 50 Ω through-line and an open/short stub coupon on every RF board so you can measure the real Dk/loss with a VNA ([fixtures & de-embedding](../17-test-measurement/fixtures-and-deembedding.md)).
- **Thermal & mechanical in rockets**: Rogers RO4000 has low z-CTE and high Tg (> 280 °C); PTFE is dimensionally softer — for structural or bolted boards prefer FR-4 or RO4000 [10].

## Ordering checklist (JLCPCB RF board)
1. **Layers & material**: FR-4 **TG155** for impedance-controlled multilayers; "High-frequency" product for Rogers/PTFE (2-layer only) [3][5].
2. **Stackup**: pick the named stackup (JLC04161H-7628 / -3313 / -2116 / -1080 for 4-layer 1.6 mm) and compute widths with JLC's own calculator for that stackup, mask on/off as built [5].
3. **Impedance control**: tick it and list the controlled nets/widths in the order notes (JLC tests coupons on its own tolerance).
4. **Copper weight**: 1 oz outer is standard for HF boards [3]; heavier copper makes narrow 50 Ω traces harder to etch accurately.
5. **Surface finish**: ENIG for fine-pitch QFN/LGA RF parts (flatness); remember the nickel loss note above; HASL is uneven for 0.4–0.5 mm pitch.
6. **Soldermask over RF traces**: decide, then design widths accordingly; mask openings over coupled lines change coupling.
7. **Via-in-pad / plugged vias** under exposed-pad RF ICs: specify filled/capped vias if you use via-in-pad, otherwise solder wicks away from the thermal pad.
8. **Coupons**: add a 50 Ω through-line and a resonator coupon on the panel edge to measure Dk/loss.
9. **Board outline & edge plating**: for edge-launch SMAs, keep copper pull-back and ground stitching per the connector drawing ([connectors](connectors-and-cables-parts.md)).
10. **Re-quote HF prices** each time — promotions change [3][5].

## Material data you should record for each build
| Item | Why | Where from |
|---|---|---|
| Laminate part number and lot (if provided) | Dk/Df traceability | order confirmation |
| Measured Z₀ of coupon (TDR) | validates width calculation | NanoVNA/LibreVNA TDR ([TDR](../03-transmission-lines-matching/time-domain-reflectometry.md)) |
| Measured resonator frequency → effective Dk | calibrates antenna/filter models | ring or stub coupon |
| Insertion loss per cm at your band | link budget | two-line method |

## Recommended picks for Marcus's use cases
| Use case | Board | Why |
|---|---|---|
| Flight computer with 433/915 MHz radio, GNSS | JLC 4-layer FR-4 TG155, JLC04161H-7628 (or -3313) | cheap, fine loss at UHF/L-band |
| 2.4 GHz modules / BLE | same (use certified module + its antenna rules) | |
| Patch antennas 2.4/5.8 GHz, arrays, filters, couplers | JLC 2-layer RO4350B 0.76 mm or PTFE ZYF265D | low loss, known Dk |
| 24 GHz radar/antenna experiments | JLC 2-layer RO4350B 0.51 mm or specialist fab | thin substrate, low loss |
| 4-layer board needing one low-loss RF layer | PCBWay (Rogers + FR-4 mixed) or specialist fab | JLC cannot do hybrids |
| Quick EU-made FR-4 prototypes | Aisler | speed, EU |

## Parts (materials) to avoid (or use knowingly)
- **Using process Dk (3.48) for RO4350B designs** — use 3.66 [10].
- **Default "FR4-Standard TG135-140"** for impedance-controlled builds at JLC — choose TG155 [5].
- **PTFE for structural or heavily-drilled boards** — use RO4000 or FR-4.
- **Trusting generic "FR-4 Dk 4.5"** for filters/antennas without a coupon measurement.

## Common mistakes & misconceptions
- *"RF means Rogers."* At 433–915 MHz with short traces, FR-4 costs < 0.2 dB.
- *"Rogers boards fix a bad layout."* Return paths, via fences and launches matter more than Dk at UHF ([13-pcb](../13-pcb-rf-layout-emc/grounding-and-return-paths.md)).
- *"All FR-4 is the same."* Glass style and resin content change Dk by ~0.5 [5].
- *"The price on the website is the price."* HF board prices and promotions change; always re-quote.

## How to simulate / verify
```python
import math
# resonant-frequency error from using process instead of design Dk (patch/stub, eps_eff ~ eps_r for estimate)
f0 = 5.8e9; dk_design, dk_process = 3.66, 3.48
print(f0*(math.sqrt(dk_design/dk_process) - 1)/1e6, "MHz high")   # ~150 MHz upper bound (eps_eff shift is smaller)
# loss saved on a 10 cm feed at 5.8 GHz (numbers from 13-pcb stackups page)
print((0.24 - 0.05)*10, "dB")
```
- Measure Dk/loss on a coupon with a NanoVNA/LibreVNA (ring resonator or two-line method); compare with the JLC impedance calculator and an openEMS model ([openEMS workflow](../16-simulation-tools/openems-workflow.md)).

## Open questions / gaps
- Current (2026-09) JLC HF prices: sources disagree (US$99.5/50.5 in the launch article vs "from US$47" on a later page) — re-quote.
- PCBWay HF prices and exact thickness menus not captured; OSH Park 2-layer material Dk not captured.
- Singapore-local fabs with RF laminates not surveyed.
- The 24 GHz 50 Ω width on 0.51 mm RO4350B is an unverified estimate.

## Sources
1. JLCPCB, *Controlled impedance PCB parameters and stackup*, https://jlcpcb.com/impedance (fetched 2026-09-29) — prepreg Dk 7628 4.4, 3313 4.1, 1080 3.91, 2116 4.16; core 4.6; soldermask 3.8. (manufacturer)
2. JLCPCB, *PCB capabilities*, https://jlcpcb.com/capabilities/pcb-capabilities (fetched 2026-09-29) — "RF PCB 1 oz copper, 2-layer RF PCBs with Rogers and PTFE cores", FR-4 2-layer Dk 4.5, Rogers/PTFE max panel 590 × 438 mm. (manufacturer)
3. JLCPCB news, *JLCPCB offers Rogers & PTFE high-frequency PCBs*, https://jlcpcb.com/news/rogers-ptfe-high-frequency-pcb-available (fetched 2026-09-29) — RO4350B 0.51/0.76/1.52 mm (finished 0.6/0.9/1.65 mm), ZYF PTFE Dk/Df, 2 layers, 1 oz, prices from US$99.5 / US$50.5. (manufacturer)
4. PCBWay, *PCB capabilities*, https://www.pcbway.com/capabilities.html (fetched 2026-09-29) — board materials incl. Rogers-4 series + FR-4 mixed, pure Rogers-4 multilayer (4450F), PTFE, PTFE + FR-4; lead-time statement from a search extract. (manufacturer)
5. This KB: [PCB stackups and laminate materials](../13-pcb-rf-layout-emc/stackups-and-materials.md) (W3-C1) — loss per cm, TG155 gotcha, design vs process Dk, JLC HF "from US$47". (internal)
6. OSH Park Docs, *4 Layer Prototype Service* (stackup table, FR408HR 2113 prepreg Dk 3.61 @ 1 GHz, 2025 material notice), https://docs.oshpark.com/services/four-layer/ (fetched 2026-09-29). (manufacturer)
7. OSH Park Docs, *Fabrication services* (2L US$5/in², 4L US$10/in², lead times), https://docs.oshpark.com/services/ (fetched 2026-09-29). (manufacturer)
8. D. Harmon, *OSHPark 4 Layer PCB Measurements* (2018), https://harmoninstruments.com/posts/oshpark_4l.html — used beyond 50 GHz; Z₀ ~56 Ω vs design. (blog — anecdotal measurement)
9. Aisler, *Beautiful Boards*, https://aisler.net/en/products/boards (fetched 2026-09-29) — FR-4 2/4+ layers, EU manufacture from 2 business days, from €14.20. (manufacturer)
10. Rogers Corp., *RO4000 series laminates* data sheet (process vs design Dk) — via [5] and [dielectrics](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md). (datasheet)
