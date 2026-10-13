# Research log W5-E12: quick fixes (GNSS radiation, 905 MHz, 2-layer thickness, LoRa CR, G_p)
Status: complete
Owner scope: surgical line edits only in the named pages (20, 07, 18, 00 canonical, and any page that radiates in GNSS bands or mislabels 902–928 MHz as Singapore); gaps/GAP_REGISTER.md §5/§8; this log.

## Plan
- [x] 1. GNSS L1 radiation: patch walkthrough T3 + Regulatory check + Common mistakes; 08/antenna-measurement AR recipe caveat. KB grep (1164–1300 / 1559–1610 MHz, gps-sdr-sim, rotating source) found no other radiated instruction (LNA recipe, 21 HIL/gps-sdr-sim, validation campaign already conducted/shielded).
- [x] 2. 905 MHz: ground-station S4/S5 + regulatory check (SG bands only; 902–928 = US/IREC); IREC/US labels in gnss-front-end (L31, coupling table), lna-design (L53, table header), lora-rocket-telemetry (Doppler table), 20/_index; validation-campaign note updated. 15: no Singapore misuse found.
- [x] 3. JLC 2-layer: canonical §B row (1.6 mm finished board vs 1.43 mm core), 03/planar-lines L40, 16/impedance-and-rf-calculators rfcalc bullet, 20/patch design bullet (TL shift +0.02 % at 1.43 mm), 20/validation F2-M1. 13/grounding L77, 04, 08/patch, 03/telegrapher, 16/openems-workflow were already explicit.
- [x] 4. LoRa CR notation: 07/sensitivity-and-mds §math + canonical Level 1 row.
- [x] 5. G_p → G_P,power in 18/lna-pa-gain-block-mmics (2×) and 18/_sources; GLOSSARY.md + tools/glossary_ambiguous.md entry updated.
- [x] 6. build_index.py --check (4 broken links, all → 19/regulatory-faq-misc.md, not ours); GAP_REGISTER C56–C60 + change log.

## Log (append-only)
- 2026-10-12 — read CONVENTIONS, canonical page, 19/singapore-imda-rules. Log created.
- 2026-10-12 — all five fixes applied; last_updated bumped on every edited page (20/_index has no front matter).
- 2026-10-12 — WebFetch jlcpcb.com/impedance: lists 4/6-layer only; 2-layer core 1.43 mm rests on the W3-C1 calculator run (2026-09-27).

## Contradictions / discrepancies found
- tools/verify/sim_openems_patch.py still uses h = 1.6 mm; the 16 benchmarks use 1.51 mm. Left as labelled model inputs (changing them would invalidate verified results).

## Cross-domain notes
- GLOSSARY.md is rebuilt by tools/glossary_harvest.py --build; the G_p wording is also in tools/glossary_ambiguous.md so it survives.

## Resume instructions
None — complete.
