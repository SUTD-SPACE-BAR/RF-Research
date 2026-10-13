# Research log W6-F2: validation test campaign (20-projects-recipes)
Status: complete (2026-10-12)
Owner scope: kb/20-projects-recipes/validation-test-campaign.md (new page), one row in
kb/20-projects-recipes/_index.md, the 20 line of tools/taxonomy.md, tools/verify/f2_*.py,
this log. Local files only (no web).

## Plan
- [x] Step 0 reading: CONVENTIONS, INDEX, ethos + HIL methods (outside repo), 20/_index + every
      recipe's predictions, 17/_index, bench-measurement-recipes, rf-bring-up-debug-playbook,
      gaps/AGENT_REPORTED_GAPS.md, gaps/GAP_REGISTER.md "Needs real-world data" (re-check at end)
- [x] Harvest predicted values + their scripts for each test group (antennas, TX, RX, link,
      rocket-specific, materials/PCB, environment)
- [x] tools/verify/f2_campaign_predictions.py: recompute/collect predicted values and derive
      acceptance bands (uncertainty budgets: VNA cal, cable, fixture, tinySA amplitude accuracy,
      attenuator tolerance, statistics of PER curves)
- [x] Write kb/20-projects-recipes/validation-test-campaign.md (template; catalogue tables;
      equipment by tier; CSV/JSON schema; sequencing; KB update protocol)
- [x] Add row to kb/20-projects-recipes/_index.md; add slug to tools/taxonomy.md 20 line
- [x] Run python3 tools/build_index.py --check; fix my broken links
- [x] Re-check gaps/GAP_REGISTER.md "Needs real-world data" near end; align test IDs

## Log (append-only)
- 2026-10-03 — log created. Read CONVENTIONS.md, HANDOFF.md, INDEX.md page list, engineering
  ethos + HIL bench methods (from the user's avionics knowledge base, outside repo).

- 2026-10-03 — Step 0 done. Read all 11 recipes' test plans + pre-registered predictions (link P1-P10,
  ground station S1-S9/Q1-Q7, patch T1-T6/P1-P6, filter T1-T6/H1-H5, GNSS FE G-T1..6/G1-G5, LNA
  L-T1..6/N1-N5, SDR R1-R7/D1-D5, FMCW, phased array), 17 _index, bench recipes R1-R10,
  bring-up playbook, AGENT_REPORTED_GAPS, GAP_REGISTER (exists; section 7 R01-R26 = "needs real-world
  data"; orchestrator note names this task). Harvested numbers from 08 antennas-on-rockets (detuning
  only qualitative), 15 modules/impairments/sensitivity, 17 NF/OTA/SA/lab-setup/TDR, 13 stackups/
  JLC/via-fence/EMC (HERO table), 19 lab-safety + IMDA, 21 gnss-on-rockets, 14 survey, 07 P.372.
- Cavity-perturbation page (W5-E11: 17/resonator-and-cavity-perturbation-permittivity-measurement.md)
  does NOT exist yet at 2026-10-03 start; re-check before final link.
- Findings to carry into the page (faithful-reporting items):
  * Patch AR test T3 (patch recipe) radiates a test signal at L1; KB 19 says never transmit in RNSS
    bands -> campaign must require a shielded/absorber enclosure or chamber + containment check.
  * 905 MHz is not a Singapore SRD band -> Yagi/link tests at 905 MHz in SG must move to 866-869 or
    917-925 MHz (or be conducted).
  * KB has no P.1546 implementation (prop_empirical.py closed forms only) -> ground-range test is
    scored against two-ray (prop_two_ray.py) + Hata-open/Egli brackets; P.1546 = gap.
  * 2-layer JLC dielectric thickness used inconsistently: 1.6 mm (sim_openems_patch.py), 1.51 mm
    (patch walkthrough), 1.43 mm core (13 canonical table JLC0216A) -> M1 coupon measures it.
  * Nose-cone detuning: KB only "a few percent" (08) and P9 "2-5 % low"; no script. F2 adds a
    quasi-static energy-partition bracket (low confidence) that separates on-axis vs wall-taped.
  * E22 harmonics X, burst-current profile, crystal-vs-TCXO, RTL IIP3 vs gain: unknowns -> tests are
    measurements of unknowns with brackets, not validations; labelled as such.

- 2026-10-03 — Wrote tools/verify/f2_campaign_predictions.py (S0 decision rules, S1-S7 predictions and
  acceptance bands, --schema / --validate results-record tool). NOT YET RUN. Then PAUSED on request.

- 2026-10-12 — resumed. Ran f2_campaign_predictions.py: 28/28 checks PASS (~13 s); output saved to
  tools/verify/f2_campaign_predictions_output.txt. Notable outputs: wall-taped detuning bracket 15-27 %
  (on-axis 1-3 %); 6 dB BW of 500 kHz LoRa 551 (avg) / 641 kHz (peak model) >= 500; 99 % OBW 1.046 BW
  (131 kHz vs meas_sa 133); PER waterfall 5x300 -> sigma 0.06 dB; U_R1 0.48 dB; ring U(er) 0.05;
  patch band 2.26 % (er unknown) vs 0.85 % (ring er) against 2.2 % separation; via fence 1 mm pitch FDFD
  40.5 vs textbook 53.8 dB; L2 threshold -94.9 dBm; HERO test threshold -43.7 dBm on 1 ohm.
- Wrote kb/20-projects-recipes/validation-test-campaign.md (40 tests: C5 A6 T6 R5 L3 K6 M3 E2 F4), added
  _index row + reading-order item, taxonomy entry; build_index --check: 0 missing sections, 10 broken
  links all in other agents' pages (none mine). Cavity-perturbation page still absent -> not linked.
  GAP_REGISTER section 7 rows R01-R25 mapped in the page's Sequencing table (R26 is a letter to IMDA).
  --schema/--validate tested (empty file -> FAIL, exit 1).

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| 1 | KB recipes in 20 (all pre-registered prediction tables) | internal | catalogue rows | as on each page |
| 2 | KB 17 (bench recipes, playbook, NF, OTA, SA, lab setup, TDR in 03) | internal | methods, budgets | medium-high |
| 3 | KB 15, 13, 08, 21, 07, 14, 19 pages listed in the page's Sources | internal | predictions | as on each page |
| 4 | User's avionics KB: engineering-ethos, hil-bench-testing-methods | user notes | rules, record template | authoritative for team practice |
| 5 | GUM (JCGM 100) / ISO 14253-1 decision rules | standard | budgets, guarded acceptance | ISO 14253-1 from general knowledge, not re-read |

## Contradictions / discrepancies found
- 2-layer JLC dielectric thickness: 1.6 mm (sim_openems_patch.py), 1.51 mm (patch walkthrough), 1.43 mm
  core (13 canonical table). Impact on er extraction small (+-0.02); test M1 measures it.
- Nose-cone detuning: KB "a few %"; F2 heuristic says a wire taped to the wall detunes 15-27 % (likely
  high) vs 1-3 % on axis. Pre-registered as a ratio claim (A2).
- 99 % OBW: meas_sa.py 133 kHz vs this script 131 kHz (phase-continuous sim) - within 2 %, both quoted.
- Egli ratio form is ~21 dB more pessimistic than plane-earth at 433 MHz (its 20log(f/40) term) -
  recorded as a bracket, not a contradiction to fix.

## Knowledge gaps noticed (for later gap-filling)
- No P.1546/ITM/P.528 implementation in tools (prop_empirical closed forms only).
- No cavity-perturbation/resonator permittivity page (W5-E11 planned).
- Unknowns with no KB prediction: E22/E220 harmonic X, module NF, RSSI offset, RTL IIP3 vs gain, cheap
  noise-source ENR, e-match no-fire (130 mA anecdotal), u-blox AND/OR, man-made noise 868/915 MHz,
  gps-sdr-sim motion interpolation, tinySA RBW shape.

## Cross-domain notes (things other domains should cover/link)
- 20/patch-antenna-design-walkthrough T3: radiated AR test at L1 conflicts with 19 "never transmit in
  RNSS bands" -> add "shielded/absorber enclosure only + containment check" (done in F2-A4 only).
- 20/ground-station-tracking-yagi S4/S5 at 905 MHz: not a Singapore SRD band -> test at 868/920 MHz.
- 17 (any): cite F2 for the PER-waterfall Fisher-information result (5x300 packets -> 0.06 dB).
- GAP_REGISTER section 7: once results exist, append dispositions per the page's KB-update protocol.

## Resume instructions (what the next agent should do if this one is interrupted)
**Exact resume steps (paused 2026-10-03):**
1. Run `python3 tools/verify/f2_campaign_predictions.py`; fix any error/FAIL (checks reproduce KB numbers:
   A_eq 39.7 dB, A_fail 59.5 dB, ToA 288 ms, drift 81 Hz, J -95 dBm, 26.5 deg/10 g/s, OBW 133 kHz,
   Y 14.20 dB, via fence 41/25 dB, ground range 3.3 km, survey 1.3 dB). Do not tune checks to pass;
   report misses. Save output to tools/verify/f2_campaign_predictions_output.txt.
2. Write kb/20-projects-recipes/validation-test-campaign.md per the task spec (template headings incl.
   "The math" = uncertainty budgets/acceptance bands; catalogue groups A/T/R/L/K/M/E (+ flight scoring
   rows referencing link-recipe P4-P7, P10); map every row to GAP_REGISTER section 7 R01-R26; equipment
   by tier (link 17/lab-setup-by-budget); CSV/JSON schema (script --schema); sequencing (order JLC
   coupons week 0; metrology first: pads/cables, SA vs sensor, ENR cal, SDR ppm; ring er before patch);
   KB-update protocol ("## Measured results" section before Open questions; outcomes CONFIRMED/REFUTED/
   INCONCLUSIVE/VOID/MEASURED; GAP_REGISTER section 7 disposition / move to section 5).
   Carry the faithful-reporting findings listed in the Log above (L1 radiation, 905 MHz not SG band,
   no P.1546, 2-layer h inconsistency, wall-taped detuning bracket, unknowns as measurements).
3. Add one row to kb/20-projects-recipes/_index.md; append `validation-test-campaign` to the 20 line of
   tools/taxonomy.md; run `python3 tools/build_index.py --check` and fix my broken links.
4. Re-check whether kb/17-test-measurement/resonator-and-cavity-perturbation-permittivity-measurement.md
   exists (W5-E11); link it only if it exists. Re-read GAP_REGISTER section 7 for changes.
5. Fill Sources/Contradictions/Gaps/Cross-domain sections of this log; set Status complete; final reply
   <= 250 words (tests per group, top 10, gaps).

- Re-read this log's Plan and Log; continue from the first unchecked item.
- The page is kb/20-projects-recipes/validation-test-campaign.md; scripts are tools/verify/f2_*.py.
