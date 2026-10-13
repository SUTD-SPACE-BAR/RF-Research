---
title: Making RF boards at JLCPCB — impedance control, tolerances, minimum features, via-in-pad, surface finishes, Rogers/PTFE service, assembly of RF parts, and what can't be done cheaply
domain: 13-pcb-rf-layout-emc
slug: jlcpcb-rf-manufacturing
tags: [JLCPCB, impedance-control, tolerance, stackup, TG155, NP-155F, trace-width, drill, via-in-pad, POFV, surface-finish, ENIG, HASL, OSP, Rogers, RO4350B, PTFE, assembly, PCBA, 0201, 01005, X-ray, test-coupon, TDR, fab-notes]
prerequisites:
  - stackups-and-materials.md
related:
  - vias-stitching-fencing.md
  - connectors-and-launches.md
  - rf-layout-rules.md
  - thermal-management-rf.md
  - rf-pcb-review-checklist.md
  - ../02-electromagnetics/skin-effect-conductor-loss-roughness.md
  - ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md
  - ../18-components-parts/pcb-substrates-parts.md
level: intro
confidence: medium
last_updated: 2026-10-02
---

# Making RF boards at JLCPCB

## Questions this page answers
- Does JLCPCB do impedance control on 2-layer boards, and what tolerance do I actually get?
- Which JLCPCB stackup and material should I select for a 4-layer RF board?
- What are the minimum trace, space, drill and via sizes, and do they limit CPWG gaps?
- Should I choose HASL, ENIG or OSP for an RF board?
- Can JLCPCB make Rogers or PTFE boards, and with how many layers?
- Can JLCPCB assemble 0201 parts, QFNs with exposed pads, U.FL connectors and shield cans?
- How do I check that what came back has the impedance I asked for?
- What RF board features are not available cheaply at JLCPCB?

## TL;DR
- **Impedance control is offered on multilayer stackups (4–32 layers)**, stated tolerance **±10 % (±5 % on request)**; without it only **±20 % trace-width tolerance** applies [1]. 2-layer boards have no formal impedance control (calculator templates exist, e.g. JLC0216A) [2][3]. One designer reported in Dec 2024 that JLC live chat quoted ±20 % and no impedance report [4] — **contradictory; verify with your own coupon**.
- **Select "FR-4 TG155" for impedance-controlled 4/6-layer orders** — the calculator assumes Nan Ya NP-155F; the quote page's default TG135-140 is unspecified [5][6].
- **Use JLC's calculator for the order and name the stackup** (e.g. JLC04161H-7628, εr 4.4, 1 oz): 50 Ω on L1 = 0.359 mm with soldermask / 0.377 mm without; an independent field solver agrees within 1 % for 7628. All stackups: [canonical width table](stackups-and-materials.md#canonical-50-ω-width-table).
- **Minimum features** (1 oz): trace/space 0.10/0.10 mm (1–2 layers), 0.09/0.09 mm (multilayer); 2 oz 0.16/0.15 mm; min drill 0.15 mm; min via diameter 0.25 mm; board thickness ±10 % (≥ 1 mm) [1]. CPWG gaps ≥ 0.15–0.2 mm keep you away from the limits and the etch-tolerance sensitivity.
- **Via-in-pad**: epoxy- or copper-paste-filled and capped (POFV), 0.15–0.55 mm, **default on ≥ 6-layer boards** [1]; hole-wall copper ≈ 20–25 µm (IPC-6012 Class 2) [7].
- **Finishes**: HASL (leaded / lead-free), ENIG (Ni ≈ 3–6 µm, Au 1 or 2 µin), OSP (no extra charge, ≈ 3-month shelf life) [8]. For RF: **OSP ≈ bare copper**; ENIG's nickel adds conductor loss on exposed faces (≈ 1.5× R_s at 433 MHz, ≈ 4–5× at 2.4–6 GHz on plated faces) — negligible for short UHF microstrip, significant for CPWG/long lines at ≥ 2.4 GHz; **mask the RF traces** or use OSP ([skin effect](../02-electromagnetics/skin-effect-conductor-loss-roughness.md)). HASL is uneven — avoid for fine-pitch RF ICs and launches.
- **Rogers/PTFE**: **2-layer only**, RO4350B (dielectric 0.51/0.76/1.52 mm) and ZYF PTFE (Dk 2.55–3.0), 1 oz, **ENIG only**, from ≈ US$47–100 for 5 × 100 × 100 mm [9][10]. No hybrid Rogers/FR-4 multilayers.
- **Assembly**: Economic PCBA ≥ 0402, ≥ 0.4 mm pitch, 2–4 layers; **Standard PCBA 0201 (01005 possible), 0.35 mm pitch, 0.3 mm BGA**; X-ray on QFN/BGA/LGA in both [11]. **0201 RF matching parts need Standard PCBA.**

## Intuition (no math)
JLCPCB is a high-volume prototype fab: it gets its low prices by running fixed processes on fixed materials. Anything that fits those processes (FR-4 4/6-layer stackups from its menu, 0.3 mm vias, standard finishes) is cheap and fast; anything that needs a special process (hybrid laminates, blind/buried vias on cheap boards, immersion silver, back-drilling, ±5 % impedance with a TDR report on every board) is either unavailable, slower, or priced like a specialist fab.

For RF up to ≈ 6 GHz that is mostly fine. The main things to get right are: **choosing the stackup and material explicitly** (so the 50 Ω width is right), **asking for impedance control** (so it is checked), **choosing a finish** that doesn't add loss where current flows, and **designing within the minimum features with margin** (so etch tolerance doesn't dominate). Then **measure**: a 50 Ω test coupon on the panel tells you what you actually got.

## The math

### Level 1 — what the tolerances mean for Z0
From the [stackups page](stackups-and-materials.md) (script §5): near 50 Ω, +10 % dielectric thickness → +2.85 Ω, +10 % width → −2.7 Ω, +0.2 Dk → −1 Ω. With h ±10 %, Dk ±0.2 and W ±10 %, ≈ 98 % of boards fall inside 45–55 Ω; with W ±20 % (no impedance control) only ≈ 80 %. The return-loss consequence is mild: a 55 Ω line has |Γ| = 0.048 (RL 26 dB) — **a ±10 % impedance error is rarely what breaks an RF board**; resonant structures (filters, stubs, patch antennas) care more about Dk and etch (frequency shifts) than about Z0.

### Level 2 — etch tolerance vs geometry
Etching changes width by a roughly fixed amount (tens of µm) regardless of nominal width, so the fractional error grows as features shrink. With ±20 µm: a 0.359 mm 7628 microstrip is ±5.6 % (≈ ±1.5 Ω); a 0.107 mm 1080 microstrip ±19 % (≈ ±5 Ω); a CPWG gap of 0.10 mm ±20 % (and, because narrow-gap CPWG is gap-dominated, Z0 moves several ohms). **Prefer 7628/3313A stackups and CPWG gaps ≥ 0.15–0.2 mm.** JLC's calculator models the etch trapezoid as top width = bottom − 0.5 mil (12.7 µm) ([stackups §9](stackups-and-materials.md)).

### Level 3 — finish loss, quantitatively
The [skin-effect page](../02-electromagnetics/skin-effect-conductor-loss-roughness.md) layered-conductor model gives ENIG (≈ 5 µm Ni-P under 0.08 µm Au) surface-resistance ratios vs copper of ≈ 1.5 (433 MHz), 2.2 (915 MHz), ≈ 4 (2.4 GHz), ≈ 5 (5–6 GHz) on the **plated** faces; Coonrod's measurements show the penalty is diluted on microstrip (current mostly on the unplated underside) and strong on CPWG (edge currents), with OSP/immersion silver indistinguishable from bare copper. JLC's ENIG nickel is ≈ 3–6 µm, i.e. the "thick-Ni" case [8]. Example from that page: a 20 mm 50 Ω microstrip at 915 MHz gains ≈ +0.006 dB from ENIG — negligible; at 5.8 GHz on CPWG with exposed edges, a few tenths of dB per 10 cm.

## Design equations & rules of thumb

| Item | JLCPCB value (2026-09) | Source |
|---|---|---|
| Impedance tolerance | ±10 % (±5 % on request); width ±20 % if not controlled | [1] (forum report of ±20 % only [4]) |
| Layers with impedance control | 4–32 (not 2) | [2][3] |
| Material for impedance orders | FR-4 TG155 (NP-155F) | [5][6] |
| Trace/space, 1 oz | 0.10/0.10 (1–2 L); 0.09/0.09 mm (ML) | [1] |
| Min drill / via diameter | 0.15 / 0.25 mm | [1] |
| Hole-wall copper | ≈ 20–25 µm | [7] |
| Via-in-pad | POFV epoxy/Cu-paste, 0.15–0.55 mm; default ≥ 6 L | [1] |
| Board thickness tolerance | ±10 % (≥ 1.0 mm), ±0.1 mm (< 1 mm) | [1] |
| Finishes | HASL, LF-HASL, ENIG (Ni 3–6 µm, Au 1–2 µin), OSP | [8] |
| Rogers / PTFE | 2-layer only; RO4350B 0.51/0.76/1.52 mm; ZYF Dk 2.55–3.0; ENIG | [9][10] |
| Assembly, Economic | ≥ 0402, ≥ 0.4 mm pitch, 0.5 mm BGA, 2–4 L, 0.8–1.6 mm | [11] |
| Assembly, Standard | 0201 (01005), 0.35 mm pitch, 0.3 mm BGA, 1–32 L, SPI | [11] |

## Worked examples

### 1. Ordering a 4-layer LoRa + GNSS flight computer for 915 MHz/L1
- Stackup **JLC04161H-7628** (or -3313A), **FR-4 TG155**, 1.6 mm, 1 oz outer / 0.5 oz inner, **impedance control: yes**, noting "50 Ω single-ended L1 ref L2, W = 0.359 mm (14.12 mil), soldermask over trace" in the order remarks.
- Finish: **ENIG** if fine-pitch QFNs/LGAs need flat pads (SX1262 QFN-24, ESP32-S3 module LGA), with RF traces **under soldermask** (no ENIG on RF copper). OSP is an RF-friendlier choice if assembly happens soon after fabrication (≈ 3-month shelf life).
- Vias 0.3/0.5–0.6 mm for stitching; EPAD vias 0.3 mm (accept some voiding) or pay for POFV.
- Assembly: Standard PCBA if any 0201 is used (ESP32-S3 reference match is 0201 [12]); otherwise Economic.
- Add a **50 Ω coupon**: 60 mm of the RF trace with U.FL/SMA footprints at both ends, on the panel rail or a breakaway tab.

### 2. A 5.8 GHz patch-array board
FR-4 loses ≈ 0.24 dB/cm and its Dk/weave spread causes phase errors ([stackups example 4](stackups-and-materials.md)). JLC RO4350B 0.508 mm 2-layer: 50 Ω ≈ 1.07 mm (H-J), ENIG only — so put soldermask over the feed network (mask εr 3.8 and tanδ ≈ 0.02–0.03 add a little loss and lower Z0 ~1–3 %; recompute widths with mask) or accept the ENIG penalty on short lines. Digital/power go on a separate cheap FR-4 board joined by a connector or U.FL.

### 3. Checking what came back
TDR the coupon (NanoVNA/LibreVNA time-domain mode, or a fast-edge TDR): Z0 along the line, launch discontinuities at the ends. From S21 phase over 60 mm get εeff and compare with the calculator's prediction (3.2–3.35 for 7628). Keep the measurements with the board revision — the "as-built truth" the Space Bar lessons ask for ([TDR](../03-transmission-lines-matching/time-domain-reflectometry.md), [fixtures](../17-test-measurement/fixtures-and-deembedding.md)).

## Practical notes
- **Name things exactly** in the order and in the repo: stackup ID, material (TG155), finish, impedance lines (layer, reference, width, mask/no mask). The Space Bar primary FC's KiCad stackup and the fabbed one differed.
- **KiCad export**: Gerbers + drill + a stackup drawing/fab notes layer; G. Sutherland's scripts generate KiCad stackup files from JLC's API (KiCad merges multiple dielectric plies between two coppers) [6].
- **RF part sourcing**: JLC's parts library ("basic" vs "extended" parts) determines assembly cost; RF-grade C0G 0201/0402 capacitors and wirewound 0402 inductors are often "extended" parts (fee per unique part). Use the `jlc-trawler` skill or the LCSC catalogue to choose ([components](../18-components-parts/_index.md)).
- **U.FL and shield cans**: both are standard SMT parts for assembly; for cans, a two-piece frame + lid lets you rework and tune; check the part's reel availability at LCSC.
- **Edge-launch SMA**: board edge routing tolerance and the connector's tab geometry matter; order the SMA as a hand-soldered part if it isn't stocked.
- **Not cheaply available at JLC** (as of the sources read): hybrid Rogers + FR-4 multilayers; multilayer Rogers; immersion silver/tin; back-drilling; per-board TDR reports with ±5 % on cheap orders; blind/buried vias outside HDI services (check the HDI page).

## Common mistakes & misconceptions
- **Leaving the material at the default TG135-140** while designing to the TG155 stackup.
- **Assuming 2-layer boards are impedance controlled.**
- **Designing CPWG at the 0.09–0.10 mm minimum gap** — etch tolerance then dominates Z0.
- **Unmasked RF traces with ENIG at 2.4–6 GHz** without accounting for the nickel loss.
- **0201 parts on an Economic PCBA order** — not supported [11].
- **No test coupon** — then there is no way to separate a fab error from a design error.

## How to simulate / verify
- `python3 tools/verify/pcb_stackup_widths.py` (JLC calculator values re-checked with a field solver; tolerance Monte-Carlo; loss tables).
- JLC online calculator, then TDR/VNA on the coupon (see above).
- For finish loss, the 02 page script `tools/verify/em_skin_depth.py` (layered ENIG model).

## Open questions / gaps
- Whether JLC provides a TDR report and what tolerance is actually guaranteed on standard orders: the capabilities page (±10 %) and a Dec 2024 user report (±20 %, no report) disagree [1][4]. Settle with a coupon measurement and record it here.
- JLC's HF (Rogers) page lists ENIG only; whether OSP/HASL are possible on Rogers orders was not confirmed.
- JLC capability numbers change; re-check before each order.

## Sources
1. JLCPCB, "PCB manufacturing & assembly capabilities," https://jlcpcb.com/capabilities/pcb-capabilities (accessed 2026-09-27) — impedance ±10 % (±5 % on request), trace/space, drill/via, POFV, thickness tolerance, finishes, Dk values. (manufacturer)
2. JLCPCB, "Controlled impedance PCB layer stackup," https://jlcpcb.com/impedance — multilayer impedance stackups. (manufacturer)
3. JLCPCB order-page/help summaries (via search): impedance control offered for 4–32 layers, not double-sided. (manufacturer; search summary)
4. Fedevel forum, "JLCPCB controlled impedance issues for high speed boards," Dec 2024 — live-chat quote of ±20 % and no impedance report. (forum — anecdotal)
5. JLCPCB, "User guide to the JLCPCB impedance calculator" — NP-155F for 4–8 layers. (manufacturer)
6. G. Sutherland, "Tips for getting PCBs made with JLCPCB," 2025, and gsuberland/jlcpcb_autogenerated_stackups (GitHub) — TG155 vs default TG135-140; stackup export. (blog/tool — anecdotal)
7. JLCPCB blog, "PCB plating thickness" — hole wall copper ≈ 20–25 µm, IPC-6012 Class 2. (manufacturer blog)
8. JLCPCB, "Surface finishes guide: HASL, ENIG & OSP compared," https://jlcpcb.com/help/article/jlcpcb-surface-finish — ENIG Ni ≈ 3–6 µm, Au 1 or 2 µin; HASL 1–40 µm, not for fine pitch/BGA; OSP free, ≈ 3-month shelf life, 4 soldering operations. (manufacturer)
9. JLCPCB, "High-frequency PCB manufacturing," https://jlcpcb.com/pcb-fabrication/high-frequency-pcb — RO4350B, ZYF PTFE, 2 layers, ENIG, from US$47. (manufacturer)
10. JLCPCB blog, "Rogers PCB & PTFE PCB: high frequency PCB is available on JLCPCB," 9 Mar 2023. (manufacturer)
11. JLCPCB, "PCB assembly capabilities," https://jlcpcb.com/capabilities/pcb-assembly-capabilities — Economic vs Standard PCBA package sizes, pitches, layers, X-ray, SPI. (A search summary inverted the Economic/Standard package sizes; the page itself was used.) (manufacturer)
12. Espressif, ESP32-S3 hardware design guidelines — CLC match in 0201. (app note)
13. KB: [stackups and materials](stackups-and-materials.md), [skin effect, roughness and plating](../02-electromagnetics/skin-effect-conductor-loss-roughness.md) (ENIG model and Coonrod data).
