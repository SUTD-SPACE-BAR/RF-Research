# Research log W6-F6: apply W5-S11 simulation results cross-domain
Status: complete (2026-10-14)
Owner scope: kb/08-antennas/{antennas-on-rockets,dipoles-and-monopoles,yagi-uda-and-log-periodic}.md; kb/13-pcb-rf-layout-emc/{grounding-and-return-paths,connectors-and-launches}.md; kb/12-phased-arrays/planar-arrays-element-pattern-coupling.md; kb/09-propagation-link-budget/{empirical-path-loss-models,two-ray-ground-reflection}.md; kb/15-lora-iot/lora-sensitivity-and-link-budget.md + mesh pages; 15/20 pages quoting 9 dBi 3-el Yagi; kb/20 recipes/validation campaign; gaps/GAP_REGISTER.md §8.

Source of results: research-logs/W5-S11-simulation-coverage.md (Cross-domain notes); kb/16-simulation-tools/openems-workflow.md Runs 3/4/5; kb/16-simulation-tools/nec-antenna-modelling.md Example 4; kb/16-simulation-tools/tool-landscape-overview.md Examples 4/5; scripts tools/verify/sim2_*.py.

## Plan
- [x] 08/antennas-on-rockets — trim 1.25 %/mm (was 0.6 %), Yagi 8.5 dBi, nose-cone table (G10 −1.2/−2.8 %, bay +3.4 %), IFA +0.7 % sign
- [x] 08/dipoles-and-monopoles — trim sensitivity + nose-cone pointer
- [x] 08/yagi-uda-and-log-periodic — buildable 3-el ≈ 8.5 dBi
- [x] 15/20 pages quoting 9 dBi 3-el Yagi
- [x] 13/grounding-and-return-paths — Z_slot 70–94 Ω, εeff ≈ 2.1
- [x] 13/connectors-and-launches — openEMS RL 11.4 / 21 dB at 2.45 GHz
- [x] 12/planar-arrays-element-pattern-coupling — finite-row dip ≈ 52° vs 44°; no Floquet in openEMS
- [x] 09/empirical-path-loss-models, 09/two-ray-ground-reflection — ITM vs two-ray 10–50 dB; rfcalc itm
- [x] 15/lora-sensitivity-and-link-budget + mesh pages — n = 1.7 vs 3.5 selection bias
- [x] 20 recipes/validation campaign — predicted values (simulation-informed, unmeasured)
- [x] GAP_REGISTER §8 change-log
- [x] build_index --check; glossary_harvest --build

## Log (append-only)
- 2026-10-14 — Step 0: read CONVENTIONS (§4, §5, §6b), canonical-values, W5-S11 log, 16/openems-workflow Runs 3–5, 16/nec Example 4, 16/tool-landscape Examples 4–5.

- 2026-10-14 — edited 08/antennas-on-rockets (8 edits), 08/dipoles-and-monopoles (2), 08/yagi-uda (4), 20/ground-station-tracking-yagi (9.2 dBi → ≈ 8.5 dBi note), 15/ground-station-design (2), 13/grounding-and-return-paths (5; openEMS slot table), 13/connectors-and-launches (5; openEMS pad table), 12/planar-arrays (5; 52° vs 44°, openEMS has no Floquet BC — page had said it does). 15 others checked: no other 3-el 9 dBi quotes in 15/20 (antenna-measurement 08 Example 1/2 use the 9.15 dBi matched design as a simulated measurement — left).

- 2026-10-14 — edited 09/two-ray-ground-reflection (5; ITM vs two-ray table, rfcalc itm CLI verified working), 09/empirical-path-loss-models (7; censoring n = 1.7, ITM now in tools), 15/lora-sensitivity-and-link-budget (1), 15/lora-mesh-capacity-and-congestion (2), 20/beginner-project-ladder rung 7 (1), 20/lora-rocket-telemetry-link P9 (annotated, prediction unchanged), 20/validation-test-campaign (4; A2 row, intro, open questions). GAP_REGISTER: §7 R07/R21 annotated, §8 change-log line. build_index --check: 0 broken links, 0 missing sections; glossary_harvest --build: 1086 terms. Total 15 kb/ files.
- Not done (out of brief): 00/canonical-values landed-rocket row note (S11 cross-domain note; 09 two-ray page now states why canonical keeps two-ray); 13/mixed-signal-layout slot numbers; 08/antenna-measurement Examples 1–2 still use the 9.15 dBi matched design (a simulated measurement of that design — consistent, left).

## Contradictions / discrepancies found
- 08 whip trim 0.6 %/mm vs NEC 1.25 %/mm at 915 MHz (0.6 % is the 433 MHz figure) — corrected, old value stated.
- 3-el Yagi 9–9.2 dBi (matched 11 Ω feed, 6 mm, single frequency) vs 8.55 dBi (direct 50 Ω, 4 mm, band-constrained): both valid for their constraints; pages now budget ≈ 8.5 dBi.
- IFA in tube moved +0.7 % (pre-registered: down) — 08 "always lower" qualified.
- 12: finite-row dip at ≈ 52°, shallow, vs Floquet estimate 44° (and vs Pozar–Schaubert "slightly inside"); 12 had claimed openEMS supports periodic boundaries — it does not (v0.37).
- 20 campaign F2 on-axis bracket 1.0–1.6 % (433) / 1.4–2.7 % (915) vs openEMS whip-in-cone 2.8 % / 1.2 % (different geometry) — stated in the A2 row.
## Resume instructions
Nothing pending. (Was: re-read this log; continue the first unchecked Plan item.) Each edit: cite S11 script/page, state the old value faithfully, bump last_updated to 2026-10-14. No sub-agents (§6b).
