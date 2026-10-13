# Research log W3-C1: 13-pcb-rf-layout-emc
Status: complete
Owner scope: kb/13-pcb-rf-layout-emc/ ; tools/verify/pcb_*.py ; this log

## Plan
Order chosen so that the pages other pages lean on come first.
- [x] stackups-and-materials — done (kb/13-pcb-rf-layout-emc/stackups-and-materials.md; tools/verify/pcb_stackup_widths.py all pass incl. §9: 10 JLC-calculator cases 49.2–52.7 Ω in FD)
- [x] grounding-and-return-paths — done (tools/verify/pcb_return_current.py all pass; FD check of image-theory distribution)
- [x] vias-stitching-fencing — done (tools/verify/pcb_via_fence.py all pass, FDFD ~15 min)
- [x] rf-layout-rules — done (tools/verify/pcb_layout_rules.py all pass)
- [x] connectors-and-launches — done (tools/verify/pcb_launch.py all pass)
- [x] shielding-and-isolation — done (pcb_cavity_modes.py)
- [x] emc-emi-fundamentals — done (tools/verify/pcb_emc_radiation.py all pass)
- [x] power-distribution-decoupling-for-rf — done (tools/verify/pcb_pdn.py all pass)
- [x] mixed-signal-layout — done (pcb_mixed_signal.py)
- [x] jlcpcb-rf-manufacturing — done (no new script; uses pcb_stackup_widths.py)
- [x] thermal-management-rf — done (tools/verify/pcb_thermal.py all pass)
- [x] rf-pcb-review-checklist — done
- [x] _index.md, _sources.md — done; link/template check on all 14 files clean
- [x] verification scripts: pcb_stackup_widths, pcb_return_current, pcb_via_fence, pcb_layout_rules, pcb_launch, pcb_cavity_modes, pcb_emc_radiation, pcb_pdn, pcb_mixed_signal, pcb_thermal (10 scripts)

## Log (append-only)
- 2026-09-27 — Step 0: read CONVENTIONS.md, INDEX.md, HANDOFF.md, _TASK_SPECS W3-C1. No prior log → fresh start. 13-pcb folder empty.
- 2026-09-27 — Read existing 04 pcb-parasitics page (Goldfarb-Pucel vias, pad C, slot estimate — link, don't duplicate), 02 skin-effect (ENIG layered-model table + Coonrod data), 02 dielectrics (FR-4 D-S model, glass-weave anisotropy), W1-A4 log (tline_microstrip.py ms_hj/width_for; tline_cpwg.py cpwg(); JITX/LibreCAL JLC7628 designs; 50 Ω on JLC7628 ≈0.372 mm bare/≈0.35 with mask).
- 2026-09-27 — Fetched S1–S9 (JLCPCB stackups/capabilities/HF/calculator; Rogers, Isola 370HR, Megtron 6 datasheets saved in scratchpad/src and read with pdftotext).
- 2026-09-27 — Coordinator message: resume after usage limit (same context, continued).
- 2026-09-27 — Ran JLCPCB online calculator via browser pane (S23); wrote pcb_stackup_widths.py (sections 1–9, all fast checks pass; FD sections 1–3 pass: H-J vs FD ≤0.2 %); wrote stackups-and-materials.md (~330 lines).
- 2026-09-29 — pcb_emc_radiation.py (8 sections, all pass): DM/CM from dipole superposition at r=100 m (far field) within 1 %; Ott 8 µA@30 MHz reproduced; clock-harmonic landing table (40 MHz×23 = 920 MHz inside SG 920–925 band; 25 MHz×63 = 1575 MHz inside L1 C/A; 8 MHz×197 = 1576 MHz); SSC FFT; pyro pickup (resonant-dipole bound 145 mA at 0.2 m vs 19.5 mA MIL-STD-464 limit for 130 mA no-fire); RF rectification; TVS RL. Wrote shielding page (pcb_cavity_modes.py all pass).
- 2026-09-29 — pcb_via_fence.py: thin-post grating formula X/eta=(a/λ)ln(a/2πr) checked by own FDFD (periodic cell, PML): converges to within ~0.6 dB for r/a=0.05; for fat vias (r/a≥0.1) the leading-term formula over-predicts isolation badly (r/a=0.15: formula 44 dB vs FDFD 31 dB at a=λ/20) → script uses FDFD-derived log-term Λ(r/a) (0.84 @0.075, 0.58 @0.1, 0.27 @0.15). Sources: JLCPCB plating blog (hole wall ~20–25 µm, IPC-6012 Class 2); Rogers/Coonrod GCPW blog (qualitative); easyw RF-tools-KiCAD (via fence/stitching plugins). pcb_launch.py written, all pass.
- 2026-09-29 — Resumed (usage limit). §9 FD fixed (box-width unit bug: S in mil) — CPWG/2L cases 49.2–49.9 Ω. Wrote pcb_return_current.py (8 sections, all pass) and grounding-and-return-paths.md. Source added: Shim & Hubing 2001 20-H rule (CVEL PDF, via search summary).

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| S1 | JLCPCB impedance stackups jlcpcb.com/impedance (3 WebFetch passes) | manufacturer | stackups | summaries inconsistent on some 6L middle-prepreg values (0.1088 vs 0.1164 mm); consistent: 7628 0.2104 mm Dk4.4, 3313 0.0994 Dk4.1, 1080 0.0764 Dk3.91, 2116 0.1164 Dk4.16, core 4.6, mask 1.2 mil/0.6 mil over Cu Dk3.8, inner Cu 0.0152 mm; JLC06161H-3313 top 3313 + 0.55 core; JLC06161H-1080 top 1080 |
| S2 | JLCPCB PCB capabilities page | manufacturer | tolerances | Z ±10 % (±5 % on request); 1 oz outer 0.10/0.10 (2L), 0.09/0.09 (ML); min drill 0.15, min via dia 0.25; POFV default ≥6L, 0.15–0.55 mm; finishes HASL/LF-HASL/ENIG/OSP; thickness ±10 %; 2L Dk 4.5 |
| S3 | JLCPCB HF PCB page + blog (Mar 2023) | manufacturer | Rogers/PTFE | 2-layer only; RO4350B (Dk3.48/Df0.0037) dielectric 0.51/0.76/1.52 mm (finished 0.65/0.9/1.65); PTFE ZYF255DA/265D/300CA-C/-P; ENIG finish; 1 oz; from $47–99.5 |
| S4 | Rogers RO4003C/RO4350B datasheets (pdftotext of JLC-hosted TICER sheet + Rogers main sheet) | datasheet | materials | Dk process 3.38/3.48±0.05, design 3.55/3.66 (8–40 GHz), Df 0.0027/0.0037 @10G, 0.0021/0.0031 @2.5G, TCDk +40/+50 ppm/°C, CTE x 11/10 y 14/12 z 46/32, Tg >280, Td 425/390, k 0.71/0.69 W/mK, 0.06 % moisture |
| S5 | Isola 370HR Dk/Df table rev C 2020 (pdftotext) | datasheet | glass-style dependence | 1x106 71 % resin Dk 3.81/Df 0.024 @1 GHz; 1x1080 58 % 4.04/0.021; 1x2116 47 % 4.26/0.018; 1x7628 42 % 4.36/0.017 @1 GHz; 10 GHz values ~0.1–0.2 lower Dk, higher Df |
| S6 | Panasonic Megtron 6 R-5775(N) datasheet 2022 (pdftotext) | datasheet | low-loss | Dk 3.40 @1G / 3.34 @13G; Df 0.002 / 0.0037; Tg 210 °C (DMA; web summaries quote 185 DSC); Td 410; CTE z 45 ppm; water 0.14 % |
| S7 | JLCPCB impedance-calculator user guide | manufacturer | calculator assumptions | NP-155F for 4–8 L, S1000-2M ≥10 L; outer Cu 1.6 mil, inner 0.6 mil (0.5 oz); mask 1.2/0.6/1.2 mil εr 3.8; models: coplanar SE/diff, SE/diff non-coplanar; "reference only" |
| S8 | G. Sutherland blog (2025-07) + github gsuberland/jlcpcb_autogenerated_stackups | blog/tool — anecdotal | TG135 vs TG155 gotcha | quote defaults FR4 TG135-140 (unspecified material) while calculator assumes NP-155F → select TG155 for impedance control; KiCad/Altium stackup export; README warns JLC data has typos |
| S9 | JLCPCB Q&A #592 (2024-12) | forum-like | same gotcha | question unanswered |
| S10 | Ott, "Grounding of mixed signal PCBs" tech tip + "Partitioning and layout of a mixed-signal PCB" PCD June 2001 (hott.shielddigitaldesign.com) | expert article | AGND/DGND | single plane + partitioning; split only with single bridge and no traces crossing slots |
| S11 | Zumbahlen, "Staying Well Grounded", Analog Dialogue 46-06 (2012) | app article | AGND/DGND pins | pins named for internal circuits; tie both to analog ground at converter |
| S12 | Semtech AN1200.37 Rev1.1 (Jan 2018) "Recommendations for best performance" (pdftotext) | app note | thermal/crystal drift | PA heat → crystal drift; top-layer copper cuts around XTAL; 2L vs 4L same drift rate (heat mostly via top layer); +22 dBm @3.7 V needs insulation or TCXO; >1 s packets need TCXO; TCXO below −20/above 70 °C |
| S13 | Semtech AN1200.40 Rev1.1 (May 2018) SX1261/2 reference design explanation (pdftotext) | app note | ref layouts | E406 2L FR-4 top=all parts+RF, bottom=GND+control; E428 4L: L1 parts/RF, L2 RF ground ref, L3 control, L4 solid GND; copper void around XTAL all layers; E449 TCXO for ≤2.8 s packets; PA match + 2nd-harmonic notch + pi LPF; LNA balun LC; Zopt diff 74+j134 @915 (SX1261) |
| S14 | Espressif ESP32-S3 hardware design guidelines, PCB layout (docs.espressif.com, latest) | app note | ESP32 RF | L2 solid GND no traces; 50 Ω RF on outer layer no vias; 135°/arc bends; CLC match in 0201 near pin; 15 mil stub 100 Ω for harmonics; ≥9 EPAD vias; crystal ≥2.0 mm from clock pin; antenna ≥15 mm clearance; USB 90 Ω ±10 % |
| S16 | TI SWRA640H (Dec 2018, rev May 2024) CC13xx/CC26xx HW config & PCB design (pdftotext) | app note | layout rules | match top-to-GND distance to ref design or re-tune balun; balun symmetric, amplitude imbalance ≤1.5 dB, phase ≤10°; solid GND under RF path back to EGP vias, no traces under RF path; LC filter: put trace inductance in series with L, not with shunt C; 20 dBm: remove header pins, high-Q parts, full shield; decoupling: same layer, power into cap then pin, separate via per cap; XTAL load caps short symmetric loop, solid GND to chip; DCDC parts at DCDC_SW with short GND |
| S17 | FCC 47 CFR 15.109 (via Cornell LII) | regulation | EMC limits | Class B @3 m: 100/150/200/500 µV/m (30–88/88–216/216–960/>960 MHz); Class A @10 m: 90/150/210/300 |
| S18 | MIL-STD-464C (2010) §5.x + App. A (pdftotext) | standard | pyro RF safety | EIDs ≥16.5 dB below MNFS for safety (=15 % of no-fire current), 6 dB other; MNFS = ≤0.1 % fire in 5 min @95 % conf.; 1 A/1 W hot-bridgewire EIDs common |
| S19 | privatedata.com hobby igniter page (Q2G2 all-fire 333 mA/100 ms, no-fire 130 mA/5 s) via search summary | hobby — anecdotal | e-match sensitivity | unverified numbers, use as order-of-magnitude |
| S20 | Southwest Microwave "Optimizing test boards for 50 GHz end launch connectors" (search summary) | app note | via-wall spacing | via edge-to-edge gap < λ/4 in dielectric (0.029" on RO4350 ↔ 53 GHz); 0.020" vias at 0.040" centres |
| S21 | Hirose U.FL catalog (via W1-A4 log) + search summary | datasheet | U.FL | DC–6 GHz, 30 mating cycles, VSWR ≤1.3 (DC–3 GHz), ≤1.4 (3–6 GHz), 3.0×3.1 mm |
| S22 | Rick Hartley, Sierra Circuits article/video "How grounding controls noise and EMI" (talk) | talk | stackup philosophy | planes one dielectric from every signal/power layer; fields carry the energy |
| S23 | JLCPCB online impedance calculator jlcpcb.com/pcb-impedance-calculator, run 2026-09-27 via browser (4L 1.6 mm, 1 oz outer, 0.5 oz inner; API /api/jlcTools/impedance/calc; model name "W2_CoatedMicrostrip1B" = Polar Si9000 naming; trapezoid W2 = W1 - 0.5 mil; outer Cu 1.38 mil; mask 1.2/0.6 mil εr 3.8) | manufacturer tool | 50 Ω widths | 50 Ω SE (mask / no mask), W1 in mil: 7628 14.12/14.85; 3313A 13.57/14.85; 3313 5.94/6.72; 2116 7.14/7.84; 1080 4.22/5.03; 1080A 10.23/11.20; 2116C 13.29/14.29; 7628A 20.25/21.57 (h=0.218+0.0764); 7628E 30.27/31.66; 7628B 39.17/40.63; 7628C/F 46.96/47.36 (3-ply 7628 to L2). Calculator now lists JLC04161H-3313A first ("recommended") and 7628 last ("Standard"). |
| S24 | JLCPCB blog "PCB plating thickness" (hole wall ~20–25 µm, IPC-6012 Class 2) | manufacturer blog | thermal vias | |
| S25 | Shim & Hubing, "20-H rule modeling and measurements", IEEE EMC 2001 (CVEL PDF; via search summary) | peer-reviewed | 20-H rule | no far-field reduction; slightly higher at resonances |
| S26 | easyw/RF-tools-KiCAD (GitHub) | tool | KiCad RF | via fence/stitching generators, round tracks, taper/mitre wizards, mask expander |
| S27 | Rogers blog, J. Coonrod, "Comparing microstrip and grounded coplanar waveguides" (2020) | manufacturer blog | GCPW | qualitative; GCPW more sensitive to copper plating thickness |
| S28 | Würth WE-SHC shielding cabinets (product pages via search summary) | manufacturer | cans | tin-plated, SE up to ~60 dB 0.5–3 GHz; seamless versions |
| S29 | Test & Measurement Tips, tinySA Ultra article (+ vendor listings) | trade/vendor | pre-compliance | 100 kHz–5.3 GHz (6 GHz ultra), RBW 200 Hz–850 kHz, LNA |
| S30 | u-blox GNSS Antennas app note UBX-15030289 R03 (pdftotext) | app note | GNSS interference | jammer dynamic range 6–12 dB over thermal; CPU harmonics to 1.5 GHz; EMC regs stop ~1 GHz; ≥40 dB GSM isolation; −5 dBm max input; C/N0 44–50 dBHz; remote antenna >1 m OK |
| S31 | JLCPCB surface-finish guide (help article) | manufacturer | finishes | HASL/LF-HASL/ENIG (Ni 3–6 µm, Au 1–2 µin)/OSP (free, ~3-month shelf) |
| S32 | JLCPCB PCB assembly capabilities page | manufacturer | assembly | Economic ≥0402, 0.4 mm pitch, 2–4 L; Standard 0201/01005, 0.35 mm pitch, 0.3 mm BGA; X-ray both |
| S33 | Fedevel forum thread 'JLCPCB controlled impedance issues' (Dec 2024) | forum — anecdotal | impedance tolerance | ±20 %, no report per live chat |
| S34 | EBYTE E22-400T33D spec/manual (LCSC/EBYTE listings via search) | datasheet | thermal | −40…+85 °C, 850–1200 mA TX |
| S15 | u-blox MAX-M5Q hardware integration manual UBX-13002460 R06 (pdftotext) | app note | GNSS layout/EMI | 50 Ω line short (<2.5 cm on std PCB w/o shielding); gap to top GND ≥ dielectric thickness, use CPWG model if gap <5W; ground under module; vias around microstrip & serial lines; in-band jamming from display/MCU/bus harmonics; EMI: unshielded line >3 mm acts as antenna — series R>20 Ω or ferrite (BLM15HD102SN1) or 47 nH on lines; ~20 dB antenna isolation achievable handheld; SAW if needed |

## Contradictions / discrepancies found
- JLCPCB impedance tolerance: capabilities page ±10 % (±5 % on request) and a search summary claiming TDR reports, vs a Dec 2024 Fedevel forum report (JLC live chat: ±20 % only, no impedance report). Unresolved — recommend own coupon.
- JLCPCB assembly: a search summary said Economic PCBA min 0201 / Standard 0402; the capabilities page itself says Economic ≥0402, Standard 0201 (01005 possible). Page value used.
- Spread-spectrum clocking: common estimate "peak reduction ≈ 10log(nδf0/RBW)" overestimates the benefit of triangular modulation by ≈ 4 dB (own FFT: 11.8 vs 15.8 dB for 40 MHz×23, 0.5 %, 120 kHz RBW) — triangular profiles concentrate power at the spread edges; recorded on emc page.
- DM/CM constants: Paul (1.257e-6 with per-wire I_C, free space) vs Ott (12.6e-7 with total I_CM, incl. ground-reflection ×2) are numerically equal but defined differently; verified by dipole superposition (pcb_emc_radiation.py §1).
- Southwest Microwave 50 GHz end-launch note (via search summary): "0.020\" vias on 0.040\" centres" but "gap 0.029\"" — inconsistent (0.040−0.020 = 0.020\"); the 0.029\" gap ↔ λ/4 at 53 GHz in εr 3.66 is self-consistent, so only the gap criterion is used.
- Thin-post grating formula X/η=(a/λ)ln(a/2πr) (textbook leading term) vs own FDFD: fine for r/a ≤ 0.05 (≤0.6 dB), but for typical PCB via fences (0.3 mm drill at 1 mm pitch, r/a = 0.15) it over-predicts single-row isolation by ~13 dB (44.5 vs 31.2 dB at a=λ/20). KB uses FDFD values.
- **W1-A4 JITX discrepancy resolved (2026-09-27):** JLCPCB's own calculator gives 50 Ω on JLC04161H-7628 = 14.12 mil = 0.359 mm with mask (0.377 mm without). W1-A4 FD: 0.372 bare / 0.343–0.348 masked (rectangular strip). My FD with JLC's own trapezoid + mask model at JLC's widths: 49.5 Ω (7628, t 1.38 mil), 51.3 (3313), 52.8 (1080), 51.0 (2116) masked; bare 49.9/51.3/52.4/51.4 — JLC's calculator agrees with an independent field solver to ≤ 5.5 %, best on 7628. JITX RS_50 = 0.3244 mm is ~10 % narrower than JLC's own tool → JITX is the outlier (probably a different mask/Dk assumption). Script tools/verify/pcb_stackup_widths.py §9.
- JLCPCB 6-layer middle prepreg thickness differs between WebFetch passes (2116 0.1088 vs 0.1164 mm) — summaries unreliable; only outer prepregs used in pages.
- JLCPCB Rogers thickness: blog lists 0.51/0.76/1.52 mm, HF page lists finished 0.65/0.9/1.65 mm — consistent if blog = dielectric, page = finished incl. Cu/plating.
- Megtron 6 Tg: datasheet 210 °C (DMA) vs web 185 °C (DSC) — method difference.
- JLCPCB impedance calculator assumes NP-155F (TG155) but quote page defaults to TG135-140 for 4/6 L (Sutherland; JLC Q&A #592 unanswered).

## Knowledge gaps noticed (for later gap-filling)
- No TDR coupon measurement of JLCPCB stackups (settles 1–5 % calculator residual and the ±10 % vs ±20 % tolerance conflict).
- openEMS 3-D studies on JLC-7628: SMA/U.FL launch + void, slot under microstrip (Z_slot assumed 100 Ω), CPWG fence distance from gap edge, shield-can coupling — would replace representative values in 04/13 pages.
- Pyro-lead RF pickup measured on a dummy bridge near the flight antenna; e-match manufacturer no-fire data.
- Av-bay thermal soak data for E22/E220 at flight duty (bay h, thermal mass assumed).
- Semtech AN1200.66 full text; ADI MT-031/MT-101 (fetch timeouts); Southwest Microwave launch app note (PDF > 10 MB).
- CISPR 32 limits quoted from knowledge only.
- VCO pushing figures for SX126x / GNSS LOs not published.

## Cross-domain notes (things other domains should cover/link)
- W5-E9 / all domains: link 50 Ω widths to kb/13-pcb-rf-layout-emc/stackups-and-materials.md#canonical-50-ω-width-table (JLC04161H-7628: 0.359 mm masked / 0.377 mm unmasked, εr 4.4; JLC0216A 2-layer: 2.692 mm masked, CPWG 0.918 mm @ 8 mil gap); 03 planar-lines 0.343 mm is our own FD mask model, not an ordering width.
- 08 pcb-and-chip-antennas: add one line "never via-fence or pour ground around the radiator" linking 13/rf-layout-rules Level 3 (keep-out physics now derived there).
- 03 planar-lines page: can now cite JLC calculator values (0.359/0.377 mm etc.) and the resolution of the JITX discrepancy (stackups page §9 / pcb_stackup_widths.py §9).
- 04 pcb-parasitics page: via-fence/stitching physics now in 13/vias (FDFD Λ(r/a)); slot estimate cross-linked from 13/grounding.
- 16-simulation-tools: openEMS examples wanted for launches, slots, via fences, shield cans on JLC-7628 (see gaps).
- 17-test-measurement: coupon TDR procedure for JLC boards; near-field probe + tinySA pre-compliance; desense test procedure (RSSI/C/N0 with subsystems toggled).
- 18-components: low-C TVS (≤0.5 pF) for RF ports, shield cans at LCSC, RF-grade 0201/0402 parts as JLC basic/extended.
- 19-regulations: CISPR 32 limits; FCC 15.109 table already in 13/emc.
- 20-projects: rf-pcb-review-checklist should be linked from design-review-checklists.
- 15-lora: E22 thermal on pad (13/thermal) and 40 MHz×23 = 920 MHz channel collision (13/emc) worth a line in rocket-telemetry-radio-design.
- 02 radiation page: states "Ott's versions ... are 2× larger" — true when both are written with TOTAL CM current; but Paul's 1.257e-6 uses per-wire I_C (total 2I_C, free space) while Ott's 12.6e-7 uses total I_CM with ground-reflection ×2 — same constant, different current definitions. Clarified in 13/emc-emi-fundamentals; W4-D6 audit may want a one-line note on the 02 page.

## Resume instructions (what the next agent should do if this one is interrupted)
- **COMPLETE 2026-10-03.** pcb_via_fence.py full run finished in ≈ 4.3 min (machine otherwise idle), ALL CHECKS PASSED, values identical to those in vias-stitching-fencing.md (default configuration; no coarsening needed). All 10 pcb_*.py scripts pass; 12 pages + _index + _sources written; no background jobs left. Nothing remains for W3-C1; follow-ups are listed under Knowledge gaps and Cross-domain notes.
- **PAUSED 2026-10-02 (2nd time, user request).** No background jobs running. ALL content work is DONE (12 pages + _index + _sources; canonical width table; antenna keep-out rule; D2 item-10 gaps closed; link/template check clean; all scripts except pcb_via_fence.py re-confirmed ALL PASS today, incl. new §9 of pcb_return_current.py and §6 of pcb_layout_rules.py).
  - ONLY remaining steps: (1) run `python3 -u tools/verify/pcb_via_fence.py` to completion (~20–30 min; run in background, check for "ALL CHECKS PASSED") — it passed fully on 2026-09-29, two later confirmation runs were stopped by pauses, and every section that printed gave identical values; (2) set Status: complete; (3) send final ≤250-word report (mention the canonical width table at stackups-and-materials.md#canonical-50-ω-width-table for W5-E9).
- 2026-10-03 — resumed; pcb_via_fence.py full run ALL PASS (≈ 4.3 min). Status → complete.
- 2026-10-02 (resumed again): DONE — (1) canonical 50 Ω width table added to stackups-and-materials.md §"Canonical 50 Ω width table" (D6 audit #5/#6; anchor stackups-and-materials.md#canonical-50-ω-width-table) and domain-13 width quotes aligned (stackup/εr/mask stated); (2) antenna keep-out rule with physics (R_rad/R0 = 1 − 1.5[sin x/x + cos x/x² − sin x/x³], x = 2kd ≈ 0.8(kd)²; pcb_layout_rules.py §6, numeric = closed form) in rf-layout-rules (TL;DR, new Level 3, Common mistakes), vias (mistake + table row), checklist §D; (3) D2 item 10: hatched planes (pcb_return_current.py §9 FD: 52.7 Ω solid → 58/87 Ω at 0.6 mm pitch, 59/120 Ω at 1.0 mm), "ground must be 50 Ω" myth, system-level ground loops (grounding page), exposed ground copper + >10 GHz notes (layout rules), connector rotation (connectors), plus audio/TDMA immunity fixes (emc) and enclosure/mesh/fabric shielding note (shielding). Remaining: via-fence re-run (in progress, scratchpad/via_out4.txt), then Status complete + final report.
- **PAUSED 2026-10-02 (user request via coordinator).** No background jobs left running.
  - ALL 12 pages + _index.md + _sources.md are WRITTEN; link/template check clean; 9 of 10 scripts re-confirmed ALL PASS on 2026-10-02.
  - Step 1: re-run `python3 -u tools/verify/pcb_via_fence.py` (~15–20 min, run in background). It passed fully on 2026-09-29; the 2026-10-02 confirmation was killed partway (sections 1, 2a and the first two rows of 2b had printed the same values as before).
  - Step 2 (new coordinator request, D2 Reddit sweep): (a) add an explicit, explained rule "never via-fence or pour ground under/around the antenna radiator or inside its keep-out" — put it in rf-layout-rules.md (TL;DR + Common mistakes + Practical notes), vias-stitching-fencing.md (Common mistakes) and rf-pcb-review-checklist.md (§D/§F). Why: ground under or near the radiator becomes part of the antenna (detunes it, lowers radiation resistance/efficiency, shields it); fences belong around *feed lines*, not the radiating element; keep-out must be copper-free on all layers. (b) read gaps/D2-reddit.md §2 item 10 ("PCB layout gaps the new 13/ pages don't cover", rows marked partial) and close them in the relevant 13 pages or the checklist.
  - Step 3: set Status: complete; send the final ≤250-word report (pages written, 10 scripts, contradictions: JITX vs JLC width resolved; SWM summary inconsistency; thin-post formula vs FDFD; SSC estimate 4 dB optimistic; JLC ±10 % vs ±20 % forum; PCBA summary inversion; Megtron Tg DMA vs DSC; gaps as listed below).
- (old) 2026-10-02: RESUMED earlier the same day. PDN + mixed-signal pages done- 2026-10-02: checklist, _index, _sources written; all quick scripts re-run ALL PASS; waiting on pcb_via_fence.py confirmation (scratchpad/via_out3.txt), pcb_return_current.py (30 s) to re-run.
- 2026-10-02: jlcpcb-rf-manufacturing + thermal pages done (pcb_thermal.py nodal θJA model, sealed-bay RC). Remaining: rf-pcb-review-checklist, _index, _sources, final via-fence confirmation.
- 2026-10-02: RESUMED. PDN + mixed-signal pages done (pcb_pdn.py §7 plane-C added after catching a 10x error in the page; pcb_mixed_signal.py new). Source S30: u-blox GNSS antennas app note UBX-15030289 R03 (pdftotext). via-fence re-run started (scratchpad/via_out3.txt). Next: mixed-signal, jlcpcb, thermal (+pcb_thermal.py), checklist, _index, _sources.
- (old) PAUSED 2026-09-29 (coordinator request, usage limit). State then:
  - Pages done (7): stackups-and-materials, grounding-and-return-paths, connectors-and-launches, rf-layout-rules, vias-stitching-fencing, shielding-and-isolation, emc-emi-fundamentals.
  - tools/verify/pcb_pdn.py JUST WRITTEN, NOT YET RUN: run `python3 tools/verify/pcb_pdn.py`, fix any FAIL, then write kb/13-pcb-rf-layout-emc/power-distribution-decoupling-for-rf.md from its output (target Z, anti-resonance, bead+cap peaking/damping, E22 1.2 A burst droop → ≥~200 µF bulk, star vs daisy chain, VCO pushing spurs, LDO+LC chain; link 04 capacitors/ferrites pages, 15 modules page).
  - A re-run of pcb_via_fence.py may have been left running writing scratchpad/via_out2.txt — just re-run it (~15 min) at the end to confirm ALL PASS.
  - Remaining after PDN: mixed-signal-layout (use harmonic table from pcb_emc_radiation.py §4 and §3 levels; ESP32 40 MHz×23=920 MHz, SD 25 MHz×63=1575 MHz), jlcpcb-rf-manufacturing (sources S1–S3, S7, S8, S23, S24; finishes ENIG/HASL/OSP from 02 skin page), thermal-management-rf (write pcb_thermal.py: PA dissipation E22 ~4 W while TX, via arrays from pcb_via_fence §6, θJA, sealed av-bay lumped RC heating), rf-pcb-review-checklist (no script), then _index.md and _sources.md, then set Status: complete and send the ≤250-word final report.
- 2026-09-29: pages 1–2 done (stackups, grounding) with passing scripts.
- Pages done (7): stackups, grounding, connectors, rf-layout-rules, vias, shielding, emc.
- Next pages in order: power-distribution-decoupling-for-rf (pcb_pdn.py), mixed-signal-layout (harmonic-landing table in pcb_emc_radiation.py), jlcpcb-rf-manufacturing, thermal-management-rf (pcb_thermal.py), rf-pcb-review-checklist, _index, _sources.
- Read this log's Plan + Log. Pages marked [x] are done; check kb/13-pcb-rf-layout-emc/ for partially written pages (look at last section present).
- Continue with the first unchecked page in Plan order. Sources already fetched are in the table (don't re-fetch unless a number is needed).
