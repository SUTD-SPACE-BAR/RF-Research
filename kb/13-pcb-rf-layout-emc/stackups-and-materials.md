---
title: PCB stackups and laminate materials for RF — FR-4 grades, glass styles, Rogers/PTFE/Megtron, and JLCPCB's stackups with 50 Ω geometries
domain: 13-pcb-rf-layout-emc
slug: stackups-and-materials
tags: [stackup, laminate, prepreg, core, FR-4, Tg, glass-style, 7628, 3313, 2116, 1080, 106, resin-content, fibre-weave, RO4003C, RO4350B, PTFE, Megtron-6, Isola-370HR, hybrid-stackup, JLCPCB, JLC04161H-7628, impedance-calculator, soldermask, CPWG, microstrip]
prerequisites:
  - ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md
  - ../02-electromagnetics/dielectrics-permittivity-loss-tangent.md
related:
  - jlcpcb-rf-manufacturing.md
  - grounding-and-return-paths.md
  - vias-stitching-fencing.md
  - rf-layout-rules.md
  - thermal-management-rf.md
  - ../02-electromagnetics/skin-effect-conductor-loss-roughness.md
  - ../04-real-components-hf/pcb-parasitics-traces-vias-pads.md
  - ../18-components-parts/pcb-substrates-parts.md
level: mixed
confidence: high
last_updated: 2026-09-27
---

# PCB stackups and laminate materials for RF

## Questions this page answers
- What is the difference between a core and a prepreg, and what do 7628, 3313, 2116, 1080 and 106 mean?
- Why does JLCPCB list a different dielectric constant for each prepreg type?
- How wide is a 50 Ω trace on each JLCPCB stackup, and what does JLCPCB's own calculator say?
- Why do different impedance calculators give different widths for the same JLCPCB stackup?
- Is FR-4 good enough for 433 MHz, 915 MHz, GNSS, 2.4 GHz and 5.8 GHz, or do I need Rogers?
- What do Tg, Td, CTE and moisture absorption mean for an RF board that goes on a rocket?
- What is the fibre-weave effect and does it matter for RF (phased arrays, filters)?
- Which 4-layer or 6-layer stackup should I pick for a LoRa / GNSS / ESP32 flight computer?
- Can I get a hybrid Rogers + FR-4 stackup at JLCPCB, and what does Rogers cost?
- Should I put the soldermask over my RF traces, and how much does it change the impedance?
- Why should I order "FR-4 TG155" rather than the default material when I ask for impedance control?

## TL;DR
- **A stackup is cores (cured glass-epoxy with copper) glued by prepregs (uncured glass-epoxy sheets).** On a JLCPCB 4-layer board the RF-relevant dimension is the *outer prepreg* between L1 and the L2 plane: **0.2104 mm (1×7628, Dk 4.4)**, 0.1164 mm (2116, 4.16), 0.0994 mm (3313, 4.1) or 0.0764 mm (1080, 3.91) [1]. The 1.07–1.27 mm core in the middle does not affect an L1 microstrip.
- **50 Ω on L1 (JLCPCB's own calculator, 1 oz, with soldermask / without)**: JLC04161H-7628 **0.359 / 0.377 mm**; -2116 0.181 / 0.199; -3313 0.151 / 0.171; -1080 0.107 / 0.128 mm; 2-layer 1.6 mm (JLC0216A, 1.43 mm core) **2.69 mm** microstrip or **0.92 mm CPWG with 0.20 mm gap** (1.09 mm without mask) [2]. An independent 2-D field solver fed with JLC's trapezoid-and-mask model reproduces all ten cases to 49.2–52.7 Ω (CPWG and 2-layer cases within 1.6 %; the thinnest prepreg, 1080, worst at +5.4 %) (script §9). JITX's published 0.3244 mm for JLC-7628 is ~10 % narrower than JLC's own tool and is the outlier.
- **Soldermask matters**: it narrows the 50 Ω width by 5 % (7628) to 17 % (1080) for microstrip and ~9–16 % for CPWG (it fills the gaps). Decide mask-on or mask-off over RF traces *before* computing widths, and tell the fab.
- **FR-4 Dk is a mixture property**: glass (εr ≈ 6.1–6.6) + resin (≈ 3–3.6). Resin-rich thin glass (106, 71 % resin) has Dk ≈ 3.8; glass-rich 7628 (42 % resin) ≈ 4.36 at 1 GHz (Isola 370HR table) [3]. Dk falls ≈ 0.1 per decade of frequency; Df ≈ 0.017–0.025.
- **Is FR-4 OK?** Yes for 433 MHz–2.4 GHz on short runs: a 50 Ω line on JLC-7628 loses ≈ 0.05 dB/cm at 915 MHz and ≈ 0.12 dB/cm at 2.45 GHz (smooth-copper model; roughness adds more). At 5.8 GHz FR-4 costs ≈ 0.24 dB/cm vs 0.05 dB/cm on 0.508 mm RO4350B — use Rogers for long feeds, filters and phased-array corporate feeds ≥ 5 GHz, or when Dk tolerance/stability sets a filter's frequency.
- **Rogers at JLCPCB is 2-layer only** (RO4350B 0.51/0.76/1.52 mm, and ZYF PTFE Dk 2.55–3.0), ENIG finish, from ≈ US$47–100 for 5 pcs of 100 × 100 mm [4][5]; no hybrid Rogers/FR-4 multilayers. For a 4-layer RF + digital board at JLC, use FR-4 7628 and keep RF runs short.
- **Order "FR-4 TG155" when you ask for impedance control**: JLC's calculator assumes Nan Ya NP-155F, but the quote page defaults to an unspecified "FR4-Standard TG135-140" [6][7].
- **Rocket relevance**: Tg (glass transition) sets the temperature where the z-axis CTE jumps (≈ 45 → 260 ppm/°C for Megtron 6 [8]); a 2 W LoRa module in a sealed av-bay will not approach Tg, but reflow and via reliability do. Moisture (FR-4 0.1–0.3 %) raises Dk/Df slightly; Rogers RO4000 absorbs 0.06 % [9].

### Canonical 50 Ω width table
**Policy:** order trace widths from the fab's own calculator for the exact stackup; every quoted width states stackup, reference layer, εr, copper and soldermask assumption. Values below are **JLCPCB's online calculator, run 2026-09-27** (1.6 mm boards; 1 oz outer finished as 1.38 mil ≈ 35 µm on 4-layer / 1.18 mil ≈ 30 µm on 2-layer; inner 0.5 oz; trapezoid W2 = W1 − 0.5 mil, width given is the bottom width W1; mask 1.2 mil on laminate / 0.6 mil over copper, εr 3.8) [2], with an independent FD field-solver check at those widths (script §9). Single-ended (SE) = microstrip on L1 referenced to L2 (2-layer: to L2 = bottom); CPWG = coplanar with ground on L1 at the stated gap, plus the L2 plane.

| Stackup (L1→ref dielectric, εr as stated by JLC) | SE 50 Ω, mask | SE 50 Ω, no mask | CPWG 50 Ω, 8 mil (0.203 mm) gap, mask | CPWG, no mask | FD check at JLC width |
|---|---|---|---|---|---|
| **JLC04161H-7628** (1 × 7628, 0.2104 mm, εr 4.4) | **0.359 mm** (14.12 mil) | 0.377 mm (14.85 mil) | 0.306 mm (12.04 mil) | 0.335 mm (13.17 mil) | 49.5 / 49.9 / 49.4 / 49.6 Ω |
| JLC04161H-3313A (3313 0.107 + 0.0994 mm = 0.206 mm, εr 4.1) | 0.345 mm (13.57) | 0.377 mm (14.85) | 0.292 mm (11.48) | 0.335 mm (13.17) | not run |
| JLC04161H-2116C (2116 0.124 + 1080 0.0764 = 0.200 mm) | 0.338 mm (13.29) | 0.363 mm (14.29) | 0.292 mm (11.48) | 0.320 mm (12.61) | not run |
| JLC04161H-7628A (7628 0.218 + 1080 0.0764 = 0.294 mm) | 0.514 mm (20.25) | 0.548 mm (21.57) | 0.406 mm (15.97) | 0.448 mm (17.65) | not run |
| JLC04161H-2116 (1 × 2116, 0.1164 mm, εr 4.16) | 0.181 mm (7.14) | 0.199 mm (7.84) | 0.171 mm (6.72) | 0.192 mm (7.56) | 51.0 Ω (SE mask) |
| JLC04161H-3313 (1 × 3313, 0.0994 mm, εr 4.1) | 0.151 mm (5.94) | 0.171 mm (6.72) | 0.142 mm (5.59) | 0.164 mm (6.44) | 51.2 Ω (SE mask) |
| JLC04161H-1080 (1 × 1080, 0.0764 mm, εr 3.91) | 0.107 mm (4.22) | 0.128 mm (5.03) | 0.106 mm (4.19) | 0.124 mm (4.89) | 52.7 Ω (SE mask) |
| **JLC0216A 2-layer 1.6 mm** (core 1.43 mm, εr 4.5) | **2.692 mm** (105.97 mil) | ≈ 2.65 mm (H-J estimate; not run in calculator) | **0.918 mm** (36.15) | 1.089 mm (42.88) | 49.2 Ω (SE mask), 49.8 / 49.2 Ω (CPWG) |
| 6-layer JLC06161H-3313 / -1080 (outer L1→L2 = 3313 / 1080) | same as 4-layer 3313 / 1080 rows (identical L1–L2 geometry; inferred, not run) | | | | |
| RO4350B 2-layer (JLC HF service), 0.508 mm, design Dk 3.66 | — | ≈ 1.07 mm (H-J, 35 µm; JLC calculator does not cover HF boards) | — | — | FD bare 49.9 Ω |

**Why other numbers you may see differ:** 0.372 mm (bare H-J/FD for 7628 with a rectangular 35 µm strip), 0.343–0.348 mm (FD with a gap-filling or conformal mask model of our own), 0.3244 mm (JITX) — different mask/etch assumptions; JLC's own tool (0.359 mm) is the one to order with. For 2-layer boards, 2.80 mm (h = 1.51 mm) and 2.97–3.06 mm (h = 1.6 mm) come from assuming the whole board, or board minus foil, is the dielectric; JLC's calculator template uses a **1.43 mm core** (JLC0216A), giving 2.69 mm masked. Script tables in §1–§8 that use h = 1.51 mm for the 2-layer board are illustrative only.

## Intuition (no math)
A multilayer PCB is a sandwich. **Cores** are already-cured sheets of woven glass cloth soaked in epoxy, with copper foil bonded to both faces; **prepregs** ("pre-impregnated") are sheets of glass cloth with partly cured resin that melt and flow in the lamination press, gluing cores and outer foils together. A JLCPCB 4-layer board is: outer foil (L1) – prepreg – core (L2 and L3 on its faces) – prepreg – outer foil (L4).

The glass cloth is described by an IPC style number: **106** (very thin, open, resin-rich), **1080**, **2116**, **3313**, **7628** (thick, heavy glass). Because glass has about twice the permittivity of epoxy, a sheet with more glass and less resin has a higher dielectric constant. That is why JLCPCB's page gives a *different* Dk for each prepreg: 7628 (4.4) > 2116 (4.16) > 3313 (4.1) > 1080 (3.91) [1]. It is not that the "material" changes — the glass/resin ratio does.

For an RF trace on the outer layer, **the thing that matters is the distance to the nearest solid plane**. On a 2-layer 1.6 mm board that is the whole core (1.43 mm on JLC0216A), so a 50 Ω microstrip is ≈ 2.7 mm wide (2.69 mm masked, JLC calculator) — wider than any chip pin. On a 4-layer board with L2 as ground, it is the ≈ 0.1–0.2 mm prepreg, so 50 Ω is ≈ 0.1–0.36 mm, similar to an 0402 pad. Thin dielectric to the plane also keeps the field (and the return current) tightly under the trace, which reduces radiation and coupling — the main reason RF boards are ≥ 4 layers ([grounding and return paths](grounding-and-return-paths.md)).

There is a price: a narrower trace has more copper loss, and thin prepregs make the impedance sensitive to thickness and etching tolerance. On the thinnest JLC prepreg (1080, 0.076 mm) a 50 Ω trace is 0.11–0.13 mm — near the fab's 0.09–0.10 mm minimum [10], so ±20 µm of etching is ±15 % of width.

Low-loss laminates (Rogers RO4000, PTFE, Megtron) have lower loss tangent and tighter Dk tolerance; they matter when a line is many wavelengths long (loss), when a resonant structure sets a frequency (filters, patch antennas, couplers), or when many paths must be phase-matched (phased arrays). For a UHF LoRa or GNSS front end with a few centimetres of 50 Ω line, FR-4 is fine.

## The math

### Level 1 — what sets Z0 and how sensitive it is
For microstrip, Z0 is a function of $W/h$ and εr only (plus copper thickness $t$ and coatings as corrections) — see the full formulas on the [planar-lines page](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md). Near 50 Ω on FR-4, the one-at-a-time sensitivities from the Hammerstad–Jensen model (script §5) are the same on every stackup because they depend only on $W/h$:

| Change | ΔZ0 near 50 Ω |
|---|---|
| dielectric thickness h +10 % | +2.85 Ω |
| trace width W +10 % | −2.6 to −2.8 Ω |
| Dk +0.2 (≈ +5 %) | −1.0 Ω |

So **h and W tolerances dominate**; Dk uncertainty is second-order for impedance (but first-order for the *electrical length* of resonators: frequency ∝ $1/\sqrt{\varepsilon_{eff}}$). A Monte-Carlo with h ±10 %, Dk ±0.2 and W ±10 % (uniform) keeps 97–98 % of boards within ±10 % of 50 Ω; with W ±20 % (JLCPCB's figure for *non*-impedance-controlled orders [10]) only 78–81 % stay inside ±10 % (script §5). That is the practical value of ticking "impedance control".

### Level 2 — why Dk depends on glass style, and the fibre-weave effect
A laminate is a composite of E-glass (ε_g ≈ 6.1–6.6) and resin (ε_r ≈ 3.0–3.6). The simplest bounds (Wiener) are the parallel mix $\varepsilon_\parallel=v_g\varepsilon_g+(1-v_g)\varepsilon_r$ (field along the glass sheets) and the series mix $1/\varepsilon_\perp=v_g/\varepsilon_g+(1-v_g)/\varepsilon_r$ (field through the sheets — the z-axis Dk that microstrip mostly sees). Resin content by *weight* (RC, e.g. "7628 RC 49 %") converts to volume fraction with the densities (glass ≈ 2.55, epoxy ≈ 1.2 g/cm³). The consequences, confirmed by the Isola 370HR table [3]:

| Glass style (1 ply) | Resin content | Pressed thickness | Dk @ 1 GHz | Df @ 1 GHz | Dk @ 10 GHz |
|---|---|---|---|---|---|
| 106 | 71 % | 0.051 mm | 3.81 | 0.024 | 3.63 |
| 1080 | 58–59 % | 0.064–0.076 mm | 4.02–4.04 | 0.021 | 3.86–3.88 |
| 3313 | 51 % | 0.089 mm | 4.17 | 0.019 | 4.03 |
| 2116 | 47–54 % | 0.102–0.127 mm | 4.11–4.26 | 0.018–0.020 | 3.96–4.17 |
| 7628 | 42–46 % | 0.178–0.203 mm | 4.28–4.36 | 0.017–0.018 | 4.14–4.24 |

JLCPCB's stated values (7628 4.4, 2116 4.16, 3313 4.1, 1080 3.91 [1]) follow the same ordering and sit within ≈ 0.1 of Isola's 100 MHz–1 GHz numbers — consistent with "one resin system, different glass/resin ratios". Note that **Df gets worse as resin content rises** (resin is the lossy part): the thin, resin-rich prepregs that give narrow 50 Ω lines are also the lossiest.

**Fibre-weave effect.** The glass is woven in bundles about 0.3–0.6 mm apart (7628: ≈ 44 × 31 yarns per inch [11]). A narrow trace that happens to run along a glass bundle sees a higher local Dk than one along a resin-rich window. The propagation delay difference per unit length is
$$\Delta\tau=\frac{\sqrt{\varepsilon_{eff,2}}-\sqrt{\varepsilon_{eff,1}}}{c}.$$
With bounding local Dk values of 3.81 and 4.36 (the resin-rich vs glass-rich laminates above) this is **8.6 ps/inch for microstrip, 11.5 ps/inch for stripline**; with a moderate 4.0–4.3 spread, 4.6/6.2 ps/inch (script §7) — consistent with the ≈ 5–10 ps/inch skews reported in the signal-integrity literature. For RF the equivalent is a phase error: **≈ 4–8° per inch at 2.45 GHz and 10–18° per inch at 5.8 GHz** between two nominally identical lines. That is negligible for a single LoRa feed, but it is a real phase-error term in a phased-array corporate feed or a Wilkinson/branch-line coupler on FR-4. Mitigations: spread-glass styles (1067/1086), routing at an angle (≈ 10°) to the weave, or a glass-free / low-Dk-contrast laminate [12].

**Loss partition.** From the Hammerstad-type loss model (script §6), $\alpha_c\propto R_s/(Z_0W)$ grows as the 50 Ω line narrows on thinner prepreg, while $\alpha_d\approx27.3\,q\,\varepsilon_r\tan\delta/(\sqrt{\varepsilon_{eff}}\lambda_0)$ ($q$ = filling factor) is nearly independent of h. On JLC-7628 at 915 MHz conductor and dielectric loss are about equal (2.75 vs 2.64 dB/m); on 1080 conductor loss dominates. **A wide microstrip on the 2-layer 1.6 mm board actually has lower loss than the thin-prepreg 4-layer line** (0.080 vs 0.116 dB/cm at 2.45 GHz) — the 4-layer board wins on field confinement, via inductance and component-pad matching, not on loss.

### Level 3 — frequency dependence, anisotropy, temperature and hybrids
- **Dispersion of Dk.** A laminate with nearly flat Df must have Dk falling ≈ linearly with log f (Kramers–Kronig; Djordjevic–Sarkar model on the [dielectrics page](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md)). Isola 7628: 4.42 (100 MHz) → 4.36 (1 GHz) → 4.24 (10 GHz) [3]. On a 50 Ω JLC-7628 line this moves Z0 by only +1.2 % from 1 to 10 GHz, but using a *1 MHz* datasheet Dk of 4.8 instead of the 1 GHz value shifts a resonator by ≈ 4 % (script §8). Rogers publishes a separate **"design Dk"** (RO4003C 3.55, RO4350B 3.66, measured by a microstrip differential-phase method, 8–40 GHz) alongside the **"process Dk"** (3.38 / 3.48 ± 0.05, clamped stripline at 10 GHz, which reads low because of air gaps) [9] — use the design value for circuit models.
- **Anisotropy.** Woven laminates have in-plane Dk > z-axis Dk (up to ~10 %). Microstrip fields are mostly vertical (z); CPWG with narrow gaps and edge-coupled differential pairs put more field in-plane, so they see a slightly higher Dk than a z-axis-calibrated number predicts.
- **Temperature.** Thermal coefficient of Dk: RO4003C +40 ppm/°C, RO4350B +50 ppm/°C (−50 to 150 °C) [9]; FR-4 is typically worse and less specified. A 915 MHz filter over a −20 to +60 °C flight envelope on RO4350B moves ≈ 50 ppm/°C × 80 °C / 2 ≈ 0.2 %, i.e. ≈ 2 MHz.
- **Tg and CTE.** Below Tg the z-axis CTE of FR-4 class materials is ≈ 45–60 ppm/°C; above Tg it rises ≈ 4–6× (Megtron 6: 45 → 260 ppm/°C [8]). Copper is 17 ppm/°C, so z-expansion strains via barrels during reflow and thermal cycling. **Standard FR-4 Tg 130–140 °C, "high-Tg" 150–180 °C.** RO4000 has Tg > 280 °C and z-CTE 32–46 ppm/°C [9].
- **Hybrid stackups** (Rogers core for the RF layer pair, FR-4 for the rest) save cost at volume fabs, but mixing materials of different CTE and press cycles needs a fab qualified for it. JLCPCB does not offer them (2-layer Rogers only [4]); order hybrids from an RF-specialist fab if you need a 4-layer board with a low-loss RF layer.

## Design equations & rules of thumb

| Rule / equation | When valid | Typical value |
|---|---|---|
| h = distance to the *nearest* plane (not board thickness) | multilayer microstrip | JLC-7628: 0.2104 mm |
| ΔZ0 ≈ +2.85 Ω per +10 % h; −2.7 Ω per +10 % W; −1 Ω per +0.2 Dk | near 50 Ω, FR-4 | script §5 |
| Mask narrows the 50 Ω width | 1.2/0.6 mil mask, εr 3.8 | −5 % (7628) … −17 % (1080) microstrip; −9 % … −16 % CPWG |
| Side ground gap S ≥ 2h → CPWG ≈ microstrip (±3 %) | CPWG | S/h = 1: −3.5 %; S/h = 0.5: −11 % |
| Fibre-weave skew $\Delta\tau=\Delta\sqrt{\varepsilon_{eff}}/c$ | narrow traces vs weave pitch | 4–9 ps/inch microstrip |
| Dielectric loss ≈ 91 f[GHz] $q\sqrt{\varepsilon}$ tanδ dB/m | TEM, low loss | FR-4 915 MHz ≈ 2.6 dB/m |
| Frequency error from Dk error ≈ ½ Δε_eff/ε_eff | resonators | Dk 4.8 vs 4.36 → 4 % |
| Use design Dk (Rogers) / 1–2 GHz Dk (FR-4) | circuit models | RO4350B 3.66 |

## Worked examples

### 1. The 915 MHz LoRa feed on a JLCPCB 4-layer board (JLC04161H-7628)
The E220-900T30D module's antenna output (or an SX1262 matching network) runs 15 mm to a U.FL. L1 microstrip over the L2 ground plane, soldermask over the trace: **JLCPCB's calculator gives 14.12 mil = 0.359 mm**; our field solver with the same trapezoid/mask model gives 49.5 Ω at that width. Electrical length: εeff ≈ 3.3 → λg ≈ 180 mm at 915 MHz, so 15 mm is 0.083 λ (30°) — a short line. Loss: ≈ 0.054 dB/cm × 1.5 ≈ 0.08 dB. With ±10 % impedance control the worst-case Z0 of 45–55 Ω gives |Γ| ≤ 0.05 (RL ≥ 26 dB) — far better than the U.FL itself (VSWR ≤ 1.3, RL ≥ 17.7 dB). **Conclusion:** on 7628 the trace is 0402-pad-sized, and component pads, U.FL signal pad and trace all have similar widths — no neck-down discontinuities.

### 2. The same feed on a 2-layer 1.6 mm board
Microstrip: JLC calculator (JLC0216A: 1.43 mm core, 30 µm copper, mask) gives **105.97 mil = 2.69 mm**. That is wider than an SX1262 RFO pin, an 0402 pad (0.5 mm) and a U.FL signal pad (≈ 1 mm), so every junction is a step discontinuity. **Better: CPWG with 8 mil (0.203 mm) gaps: 0.92 mm with mask, 1.09 mm without** [2]. The field solver gives 49.8 Ω (masked) and 49.2 Ω (unmasked) at JLC's widths. Note how much the mask matters for CPWG on thick boards (17 %): the gap field is concentrated at the surface, exactly where the mask lies. If you leave the RF trace unmasked (common for tuning), use the unmasked width. Stitch the side grounds to the bottom plane ([vias, stitching and fencing](vias-stitching-fencing.md)).

### 3. Choosing a prepreg for a 2.45 GHz ESP32-S3 / 5.8 GHz video board
On JLC04161H-1080 (0.0764 mm) a 50 Ω line is 0.107 mm masked — close to the 0.09 mm multilayer minimum, with ±20 µm etch meaning ±19 % width. Loss at 5.8 GHz: 0.34 dB/cm vs 0.24 dB/cm on 7628 (script §6). The benefits of thin prepreg (tiny via inductance to L2, very local return current) are already obtained with 7628 at these frequencies ([vias](vias-stitching-fencing.md): an L1→L2 via on 0.21 mm is ≈ 0.02 nH). **Choose 7628 (or 3313A/2116C, which JLC's calculator now lists first) for RF; reserve 1080/3313 for dense digital fan-out.**

### 4. A 4-element 5.8 GHz patch array feed: FR-4 or RO4350B?
A corporate feed of 2 × 60 mm branches plus 40 mm trunk (≈ 100 mm per path) on JLC-7628: loss ≈ 0.24 dB/cm → 2.4 dB, plus Dk-tolerance-driven phase error: ±0.2 Dk changes εeff by ≈ ±3 % → ±1.5 % phase velocity → over 100 mm (≈ 4.8 λg at εeff 3.2) that is ±26° common to all branches (steers nothing, but detunes the patches), while weave-induced *differential* errors of 4–18°/inch × ~4 inch are 16–70° between branches — enough to raise sidelobes. On 0.508 mm RO4350B: 0.053 dB/cm → 0.53 dB, Dk ±0.05 → ±6°, no significant weave effect (fine glass, low Dk contrast). **Use RO4350B (JLC 2-layer HF service) for the array board; keep the digital/power on a separate FR-4 board.** See [phased arrays](../12-phased-arrays/_index.md).

### 5. A GNSS L1 trace on the 6-layer JLC06161H-3313 (0.0994 mm to L2)
50 Ω = 5.94 mil (0.151 mm) with mask, per JLC's 4-layer 3313 result (the L1–L2 geometry is identical; not separately run for 6-layer). At 1575 MHz, loss is ≈ 0.12 dB/cm (script §6). Keep the run < 25 mm as u-blox advises for standard PCB material [13], i.e. ≤ 0.3 dB before the LNA — which adds ≈ 0.3 dB to the system noise figure if there is no active antenna ([noise figure](../07-noise-linearity/noise-figure-and-friis.md)).

## Practical notes
- **Put the stackup name in the fab notes and in the KiCad board file** (Board Setup → Physical Stackup: enter each prepreg/core thickness and εr, and "Solder mask" εr 3.8, 0.015–0.03 mm). The Space Bar primary FC's KiCad stackup did not match the fabbed one — for RF that changes every width. G. Sutherland's scripts generate KiCad/Altium stackup files from JLC's API (KiCad merges multiple dielectrics between two coppers into one) [7].
- **Material selection at order time**: for 4/6-layer impedance-controlled boards choose **FR-4 TG155** (Nan Ya NP-155F, which JLC's calculator assumes); the default TG135-140 material is unspecified and the upgrade costs very little [6][7].
- **Use the fab's own calculator for the order** (it knows the pressed prepreg thickness, trapezoid etch and mask), and your own field solver or openEMS for the design sanity check; expect ±1–3 Ω between tools. JLC's calculator reports the *bottom* width W1; its model uses W2 = W1 − 0.5 mil (script §9).
- **JLC 4-layer 1.6 mm options** (2026-09): the calculator offers 18 templates, now listing **JLC04161H-3313A** (2 × 3313 to L2, 0.206 mm) first as "recommended" and 7628 last as "Standard" [2]. Their L1–L2 dielectrics range from 0.076 mm (1080) to ≈ 0.65 mm (3 × 7628, variants C/F) — the thick variants give 1.2 mm-wide 50 Ω traces, useful to match large RF connector pads.
- **6-layer** JLC06161H-3313 and -1080 have 3313 (0.0994 mm) and 1080 (0.0764 mm) outer prepregs [1]; route RF on L1 over an L2 ground and keep L3/L4 for power and digital.
- **Copper**: JLC 1 oz outer is ≈ 35 µm finished (the calculator uses 1.38 mil ≈ 35 µm; its guide says 1.6 mil) [2][14]; inner 0.5 oz = 15.2 µm. ED copper roughness (≈ 1–2 µm rms) adds conductor loss at GHz ([skin effect & roughness](../02-electromagnetics/skin-effect-conductor-loss-roughness.md)).
- **Finish**: JLC's HF (Rogers/PTFE) boards are ENIG-only [4]; ENIG's nickel adds loss on exposed RF copper at ≥ 2.4 GHz — mask the RF traces (and use the masked width) or accept ≈ 1.5–5× surface resistance on plated faces ([JLCPCB RF manufacturing](jlcpcb-rf-manufacturing.md)).
- **Moisture and outgassing**: bake FR-4 boards before reflow if stored humid (Singapore!); for vacuum/high-altitude use, low-outgassing laminates matter only for spacecraft, not for sounding rockets.
- **Mechanical**: a 1.6 mm 4-layer board with 0.21 mm prepregs is as stiff as a 2-layer board; for vibration, the stackup matters less than mounting and component placement.

## Common mistakes & misconceptions
- **"FR-4 has εr = 4.5 (or 4.7)."** It depends on glass style/resin content (3.8–4.4 at 1 GHz for the prepregs above) and on frequency. Use the value for *your* prepreg, at your frequency.
- **Using the whole board thickness as h** on a multilayer board (gives ≈ 2.9 mm instead of 0.359 mm on JLC04161H-7628).
- **Ignoring soldermask**, or computing with mask and then ordering the RF trace unmasked (or vice versa): 5–17 % width error.
- **Trusting one calculator to ±1 Ω.** Calculators differ in copper thickness, trapezoid, mask model and Dk. The JITX-vs-JLC 10 % difference for JLC-7628 is an example; check against the fab's tool and a field solver.
- **"Rogers is needed for anything RF."** For ≤ 2.4 GHz and centimetre-scale lines FR-4 loss is < 0.3 dB; Rogers matters for filters, antennas, long feeds, arrays and ≥ 5 GHz.
- **Picking the thinnest prepreg "for RF".** It makes 50 Ω traces hard to fabricate and lossier; 7628/3313A (≈ 0.2 mm) is the sweet spot for UHF–5.8 GHz on FR-4.
- **Assuming "impedance control" is automatic** because the stackup name is JLC's. It must be selected; otherwise only ±20 % width tolerance applies [10].
- **Mixing up process Dk and design Dk** for Rogers (3.48 vs 3.66 for RO4350B — a 2.5 % frequency error).

## How to simulate / verify
- `python3 tools/verify/pcb_stackup_widths.py` (≈ 5–8 min; `--fast` ≈ 3 s skips field solutions): 50 Ω microstrip and CPWG widths on all stackups (Hammerstad–Jensen and Ghione–Naldi via W1-A4's `tline_microstrip.py` / `tline_cpwg.py`), FD field-solver checks bare and masked (`tline_fd2d.py`), CPWG-vs-microstrip gap rule, Monte-Carlo tolerance, loss table, fibre-weave skew, Dk dispersion, and **JLCPCB's own calculator outputs re-evaluated with the field solver** (§9).
- JLCPCB online calculator (https://jlcpcb.com/pcb-impedance-calculator): select layers/thickness/copper, add rows for "Single Ended (Non coplanar)" and "Coplanar Single Ended" with and without solder mask; each stackup template appears as a tab.
- KiCad PCB Calculator → Transmission lines (microstrip, coplanar with ground plane) for quick checks; openEMS for 3-D transitions ([EM solvers](../16-simulation-tools/em-solvers-fdtd-mom-fem.md)).
- **Measure**: order a test coupon (a 50–100 mm 50 Ω line with SMA/U.FL at both ends) on the same panel; TDR or VNA S21 phase gives εeff and Z0 ([TDR](../03-transmission-lines-matching/time-domain-reflectometry.md), [VNA practice](../17-test-measurement/nanovna-librevna-practical.md)).

## Open questions / gaps
- JLCPCB's calculator widths for thin prepregs reproduce 51–53 Ω in the field solver (7628, CPWG and 2-layer cases: 49.2–49.9 Ω). The residual is probably a different effective Dk or pressed thickness in JLC's model; only TDR coupons can settle it.
- The dielectric thickness of JLC 2-layer 1.0/0.8 mm boards (used here as 0.91/0.71 mm) was not confirmed from the calculator.
- The Dk/Df of JLC's default "FR4-Standard TG135-140" material is unpublished.
- Local Dk values of glass bundle vs resin window used for the weave-skew bound are laminate-average proxies, not measured micro-scale values.

## Sources
1. JLCPCB, "Controlled impedance PCB layer stackup," https://jlcpcb.com/impedance (accessed 2026-09-27) — prepreg thicknesses and Dk (7628 0.2104 mm/4.4, 2116 0.1164/4.16, 3313 0.0994/4.1, 1080 0.0764/3.91; core 4.6; mask 1.2 mil, εr 3.8). (manufacturer)
2. JLCPCB online impedance calculator, https://jlcpcb.com/pcb-impedance-calculator, run 2026-09-27 for 4-layer 1.6 mm (1 oz/0.5 oz) and 2-layer 1.6 mm (1 oz), 50 Ω single-ended and coplanar (8 mil gap), with/without solder mask; API model "W2_CoatedMicrostrip1B", W2 = W1 − 0.5 mil. Raw values recorded in research-logs/W3-C1-pcb-emc.md. (manufacturer tool)
3. Isola, "370HR Dielectric Constant / Dissipation Factor table," rev. C, 2020, https://www.isola-group.com/wp-content/uploads/data-sheets/370HR__Dk_Df_Tables.pdf — Dk/Df vs glass style, resin content, 100 MHz–10 GHz. (datasheet)
4. JLCPCB, "High-frequency PCB manufacturing," https://jlcpcb.com/pcb-fabrication/high-frequency-pcb (accessed 2026-09-27) — RO4350B and ZYF PTFE, 2-layer, 1 oz, ENIG, finished 0.65/0.9/1.65 mm, from US$47. (manufacturer)
5. JLCPCB blog, "Rogers PCB & PTFE PCB: high frequency PCB is available on JLCPCB," 9 Mar 2023, https://jlcpcb.com/blog/rogers-pcb-ptfe-pcb-high-frequency-pcb-is-available-on-jlcpcb — RO4350B 0.51/0.76/1.52 mm, PTFE Dk 2.55–3.0, from US$99.5 (Rogers) / US$50.5 (PTFE) for 5 pcs 100 × 100 mm. (manufacturer)
6. JLCPCB, "User guide to the JLCPCB impedance calculator," https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator — NP-155F for 4–8 layers, S1000-2M ≥ 10 layers; outer Cu 1.6 mil, mask 1.2/0.6/1.2 mil εr 3.8; values "for reference only". (manufacturer)
7. G. Sutherland, "Tips for getting PCBs made with JLCPCB," blog, 5 Jul 2025, https://blog.poly.nomial.co.uk/2025-07-05-tips-for-getting-pcbs-made-with-jlcpcb.html; and github.com/gsuberland/jlcpcb_autogenerated_stackups — TG135 default vs TG155 assumed by calculator; KiCad/Altium stackup export. (blog/tool — anecdotal but specific); JLCPCB Q&A #592 (2024-12, unanswered) raises the same point.
8. Panasonic, MEGTRON 6 R-5775(N) data sheet, 2022, https://industrial.panasonic.com/content/data/EM/PDF/CDS_MEGTRON6_R-5775(N)_220401.pdf — Dk 3.40/3.34 (1/13 GHz), Df 0.002/0.0037, Tg 210 °C (DMA), Td 410 °C, z-CTE 45/260 ppm/°C, water 0.14 %. (datasheet)
9. Rogers Corp., "RO4000 series high frequency circuit materials" data sheet (RO4003C/RO4350B), and "RO4003C and RO4350B laminates with TICER foil" (publ. 92-134, 2019) — process/design Dk, Df 0.0027/0.0037 @10 GHz and 0.0021/0.0031 @2.5 GHz, TCDk +40/+50 ppm/°C, CTE x/y/z 11/14/46 and 10/12/32 ppm/°C, Tg > 280 °C, Td 425/390 °C, k 0.71/0.69 W/m·K, moisture 0.06 %, standard thicknesses. (datasheet)
10. JLCPCB, "PCB manufacturing & assembly capabilities," https://jlcpcb.com/capabilities/pcb-capabilities (accessed 2026-09-27) — impedance ±10 % (±5 % on request), ±20 % width if not controlled, min trace/space 0.10/0.10 mm (1–2 L) and 0.09/0.09 mm (multilayer), 2-layer Dk 4.5. (manufacturer)
11. IPC-4412, *Specification for Finished Fabric Woven from "E" Glass for Printed Boards* (glass style yarn counts and thicknesses; values via secondary summaries). (standard)
12. Signal Integrity Journal / Z-zero articles on glass-weave skew (e.g. "How to avoid getting totally skewed," Z-zero, 2021; SIJ "Beware of the skew budget") — mitigation methods (angle routing ≈ 10°, spread and multi-ply glass). (trade articles)
13. u-blox, *MAX-M5Q Hardware Integration Manual*, UBX-13002460 R06 — keep the 50 Ω antenna line short (< 2.5 cm on standard PCB material without shielding), dielectric to layer-2 ground. (app note)
14. KB page [planar lines](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md) and its scripts `tline_microstrip.py`, `tline_cpwg.py`, `tline_fd2d.py` (W1-A4) — formulas and field solver reused here.
15. Verification script `tools/verify/pcb_stackup_widths.py` (this page).
