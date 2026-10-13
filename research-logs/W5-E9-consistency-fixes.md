# Research log W5-E9: apply D6 consistency-audit fixes + canonical values page
Status: complete (2026-10-03)
Owner scope: surgical edits to existing kb/ pages named in gaps/D6-consistency-audit.md (NOT kb/13-pcb-rf-layout-emc/,
NOT kb/20-projects-recipes/); new page kb/00-math-foundations/canonical-values-and-conventions.md; one line in
CONVENTIONS.md §4; kb/00-math-foundations/_index.md; tools/taxonomy.md (00 line); tools/verify/fix_*.py; gaps/W5-E9-deferred.md; this log.

Numbering: D6 issue numbers are used below. Task-prompt numbering → D6: prompt #1 Leeson = D6 #1; prompt #2 via = D6 #7;
prompt #3 BGA524 = D6 #13; prompt #4 RTL NF = D6 #14; prompt #5/#6 widths = D6 #11/#12; prompt #7 matched filter = D6 #8;
prompt #8 processing gain = D6 #15; prompt #9 landed range = D6 #16; prompt #10 micro-coax = D6 #24.

## Plan (checklist of every D6 issue)
- [x] #1 wrong — Leeson prefactor in 05/oscillators.md (2FkT/Ps → FkT/(2Ps)); examples; tools/verify/analog_oscillators.py → **fixed (see log)**
- [x] #2 cosmetic — 07/phase-noise-and-jitter "floor −164" → −164 at 10 MHz, asymptotic −167 → **fixed 07/phase-noise-and-jitter.md:63**
- [x] #3 cosmetic — resistor noise 290 K first in 05/low-noise-analog-design + 05/op-amps-real-limitations → **fixed 05/low-noise-analog-design.md:42,68,107; 05/op-amps-real-limitations.md:141,168**
- [x] #4 cosmetic — skin depth IACS in 04/inductors-at-rf → **fixed 04/inductors-at-rf.md:62**
- [x] #5 cosmetic — E220 917–925 MHz "≤ ~20 dBm" in 19/singapore-imda-rules:50,53 and 15/lora-modules:55 → **fixed 19/singapore-imda-rules.md:50,53 (+19/_index:23); 15/lora-modules-ebyte-rfm-heltec.md:55; 15/ism-band-plans-duty-cycle.md:45; 20/lora-rocket-telemetry-link.md:196**
- [x] #6 cosmetic — 17/spectrum-analyzers Example 4 module name → **fixed 17/spectrum-analyzers.md:93**
- [x] #7 inconsistent — ground-via inductance in 03/input-impedance-stubs (≈0.54 nH), also 02/04 context → **fixed 03/input-impedance-stubs-quarter-wave.md:95,155,+gap note; 03/impedance-matching-lumped-and-distributed.md:163 (extra instance: 0.05–0.1→0.02 nH, ≈1→0.54 nH); 04/pcb-parasitics:41; 02/inductance-capacitance-from-fields:29; 06/amplifier-stability-and-biasing:199; 20/bandpass-filter-design-walkthrough:103 (clarified 0.1 nH allowance)**
- [x] #8 ambiguous — 2E/N0 vs E/N0 in 10/matched-filter + 11/pulsed-radar → **fixed 10/matched-filter-detection.md:46,80; 11/pulsed-radar-and-pulse-compression.md:79**
- [x] #9 cosmetic — Hamming 1.78 "misprint" wording in 11/radar-range-equation (+ 11/_sources) → **fixed 11/radar-range-equation.md:121,213; 11/_sources.md:45; 14/fft-spectral-analysis-windows.md:173 (extra instance)**
- [x] #10 cosmetic (optional) — SF12 Doppler-rate "≈3 g (sim) to 6 g (Semtech rule)" → **optional; added range at 15/lora-impairments-doppler-drift-timing.md:40**
- [x] #11 provisional (13) — 7628 50 Ω width in 03/planar-lines: depends on W3-C1 canonical table → **fixed (W3-C1 table present): 03/planar-lines-microstrip-stripline-cpwg.md:41,138,+gap note; 04/pcb-parasitics-traces-vias-pads.md:135; 20/lna-design-walkthrough.md:180 (extra: CPWG 0.36 → microstrip 0.359 / CPWG 0.306)**
- [x] #12 provisional (13) — 2-layer width in 03/04/08: depends on W3-C1 canonical table → **fixed: 03/planar-lines:40,43(CPWG),136; 04/pcb-parasitics:63,103; 03/telegrapher-equations-characteristic-impedance.md:178; 08/patch-antennas.md:139; 16/openems-workflow.md:76 (extra) — all link to 13 canonical width table**
- [x] #13 inconsistent — BGA524 P1dB −16 dBm in 18/lna-pa + 18/filter-parts SAW margin → **fixed 18/lna-pa-gain-block-mmics.md:108,186,+gap note; 18/filter-parts-saw-ceramic-ltcc.md:143 (36 dB, SAW 1 dB short)**
- [x] #14 inconsistent — RTL-SDR NF in 17/sdr-as-test-equipment vs 14 → **fixed 17/sdr-as-test-equipment.md:29,54,105; 20/lna-design-walkthrough.md:54,203 (notes, pre-registered predictions unchanged); 14/fft:151 'suppose 6 dB' left (hypothetical, consistent with 5.4 dB)**
- [x] #15 ambiguous — processing gain real vs complex in 14/sdr-hardware-survey, 18/rf-transceiver-ics (+07, 18/adcs) → **fixed 14/sdr-hardware-survey.md:45,64,95; 18/rf-transceiver-ics.md:164 (D6 cited :86, drifted); 07/dynamic-range-sfdr-blocking.md:52,87; 18/adcs-dacs-for-sdr.md:67; 05/data-converters-adc-dac.md:138,177; extra FFT-floor instances 17/sdr-as-test-equipment.md:25,38 (complex IQ per-bin floor −SNR−10logN = −80 dBFS @1024/8-bit, simulated) and 17/oscilloscopes-and-probing-for-rf.md:45**
- [x] #16 ambiguous — landed-rocket range assumption set in 09 Example E and 15 → **fixed: canonical assumption set + scenario table added to 09/link-budget-methodology.md Example E (ranges recomputed from prop_two_ray.py §5: 11.5/19 km licensed, 3.6/6 km exempt); 15/lora-sensitivity-and-link-budget.md:45,141 qualified; 20/lora-rocket-telemetry-link.md:153 and 20/ground-station-tracking-yagi.md:228 cross-ref**
- [x] #17 ambiguous — class-F wording 06/power-amplifiers TL;DR → **fixed 06/power-amplifiers.md:46**
- [x] #18 cosmetic — phase-quantisation lobe exact form in 12/beam-steering + 12/_index → **fixed 12/beam-steering-grating-lobes.md:35,68,96,125; 12/_index.md:36**
- [x] #19 cosmetic — GNSS C/N0 00/decibels:279 (+ canonical range) → **fixed 00/decibels-and-log-units.md:160 (range + SNR recomputed),279 (T_a note: 44 dB-Hz at 100 K)**
- [x] #20 cosmetic — CFRP σ range unify (02, 08) → **fixed: unified σ 10³–3×10⁴ S/m (script em_fresnel_radome.py §3e input) and its dB: 02/boundary-conditions-reflection-refraction.md:31; 02/dielectrics-permittivity-loss-tangent.md:201; 08/antennas-on-rockets.md:28,77,103; 08/gnss-antennas.md:32 (L1 50–162 dB). 21 '> 100 dB' left (consistent lower bound at L1 for σ ≥ 10⁴)**
- [x] #21 provisional (20) — E22 CH 24 vs CH 23 in 20 → defer to W3-C6 → **no-change: 20/lora-rocket-telemetry-link.md:54,229 (W3-C6) already say CH 24 for SG at BW > 125 kHz and justify CH 23 for licensed use; aligned 20/gnss-front-end-design.md:152 under C1**
- [x] #22 ambiguous — u-blox 4 g meaning in 18/rf-modules → **fixed 18/rf-modules.md:47,121**
- [x] #23 cosmetic — taxonomy additions / broken links → **partly fixed: D6's 7 broken links now resolve (targets written by owners); taxonomy now has kalman/beginner-ladder/multiband (owners) + sdr-gnss-and-diy-receivers (W5-E9) + canonical slug; build_index front-matter/anchor validation deferred to Wave 6 (one-off check run, see gaps/W5-E9-deferred.md)**
- [x] #24 inconsistent — micro-coax loss 07/receiver-cascade:120; 00/decibels:255 RG-316; 17/vna label illustrative → **fixed 07/receiver-cascade-analysis.md:120 (2.6 dB/m @L1); 00/decibels-and-log-units.md:255–257 (0.72 dB/m; 32.2 dBm, 33.7 dBm EIRP, 31.5 dBm ERP, 21.5 dB over); 17/vna-fundamentals-calibration.md:113 labelled illustrative**
- [x] C1 (coordinator, 2026-10-02) — 433.125 MHz CH23 at BW 250 kHz spreads below 433.05 MHz (fc − BW/2 = 433.000); at 125 kHz only just inside (433.0625). Recommend CH24 434.125 MHz (E220 CH17 867.125 MHz). Fix 21/gnss-interference-jamming-spoofing (+ harmonic table) to "CH24, or CH23 only with BW ≤ 125 kHz"; grep 15, 09, 21 (and 20) for 433.125 / CH23 recommendations; record band-edge rule in canonical page → **fixed (see log); canonical-page entry in Task 2**
- [x] C2 (coordinator) — 18/lna-pa-gain-block-mmics lists BGA524N6 IIP3/IP1dB −4/−12 dBm (feature list) → table values IP1dB −16, IIP3 −9, OOB IIP3 −5 dBm (part of #13) → **fixed with #13 (table row −9/−16, OOB −5)**
- [x] D1 (coordinator, from W5-E6) — reciprocal link from 00/math-roadmap-for-rf.md to rf-learning-roadmap.md + rf-concepts-for-beginners.md (one line near top) → **added one line under the H1 of 00/math-roadmap-for-rf.md linking rf-concepts-for-beginners, rf-learning-roadmap (and the canonical page)**
- [x] D2 (coordinator) — 14/software-demodulation.md rtl_433 decoder count ≈200 → verify vs rtl_433 README (≈380?) and update → **fixed 14/software-demodulation.md:98 (≈380; README 380 entries up to [386], 44 disabled by default, fetched with curl 2026-10-03); 14/sdr-gain-staging-and-reception-recipes.md:353 gap note updated**
- [x] G-18-01 (GAP_REGISTER #1) — 18/lna-pa-gain-block-mmics.md:114 ZED-F9P "L1+L5" → L1/L2 (verify u-blox); grep KB for F9P … L5 → **fixed 18/lna-pa-gain-block-mmics.md:114 (+gap note); 21/gnss-signals-and-codes.md:151 note updated; verified via u-blox ZED-F9P product summary UBX-17005151 (0xB = L1/L2: L2C/L2OF/E5b/B2I; 15B = L1/L5). KB grep: no other F9P-L5 claims**
- [x] G-15-02 (GAP_REGISTER #2) — unify E22 3rd-harmonic avoid-channels across 15 and 21 (W3-C7: CH 0–3 → GPS L2, CH 5–6 → GLONASS L2) + band-edge CH 24 → **unified to W3-C7 analysis: avoid CH 0–9 (0–3 GPS L2, 4 edge/5–6 GLONASS L2, 7–9 filter skirts), CH 10–22 E6/B3, use CH 24: 15/rocket-telemetry-radio-design.md:145; 07/nonlinearity-p1db-ip3-intermod.md:102; 20/lora-rocket-telemetry-link.md:54 (CH 24 now default primary),154,232; 20/gnss-front-end-design.md:51; 20/bandpass-filter-design-walkthrough.md:75; 21/gnss-interference-jamming-spoofing.md:28. Not edited: 20/gnss-front-end G5/G231 pre-registered test rows ('CH 0–6' test), 13 (outside scope)**
- [x] G-18-02 (GAP_REGISTER #5) — 18/rf-modules.md:38 80 km firmware note (50 km ZED-F9P HPG 1.00–1.12; 80 km HPG 1.13+ and M10; no output > 500 m/s at any altitude) → **fixed 18/rf-modules.md:38,62,166 (50 km HPG 1.00–1.12; 80 km HPG ≥1.13 and M10; no output >500 m/s any altitude), per 21 datasheet table**
- [x] Close G-18-01, G-15-02, G-18-02 rows in gaps/GAP_REGISTER.md §5 → **added C53–C55 to gaps/GAP_REGISTER.md §5 and tagged the ranked list/table rows 'closed → §5 C5x'**
- [x] Task 2 — canonical-values-and-conventions.md + CONVENTIONS §4 link + 00/_index link + taxonomy 00 line → **done: kb/00-math-foundations/canonical-values-and-conventions.md (template; tables A–E + conventions + Singapore + band-edge rule + scenario sets); CONVENTIONS.md §4 item 5 one-line link; 00/_index.md (reading order R., Pages row, FAQ); tools/taxonomy.md 00 line; 00/decibels Common mistake 16 (D6 §4.2 traps pointer); tools/verify/fix_canonical_values.py ALL PASS**
- [x] Task 3 — re-grep KB for other instances of each corrected value → **re-greps done per issue; extra instances fixed (see log); final sweep of 14 old phrases = 0 hits**
- [x] Task 4 — build_index.py --check; re-run touched verify scripts → **build_index.py --check: 266 pages, 0 missing template sections, 8 broken links all in pages of running agents (W5-E7/E8/E10); analog_oscillators.py exit 0; fix_leeson_prefactor.py, fix_canonical_values.py ALL PASS; prop_two_ray.py, em_fresnel_radome.py re-run (values used)**

## Log (append-only)
- 2026-10-02 — Step 0: read CONVENTIONS.md, HANDOFF.md, gaps/D6-consistency-audit.md (24 issues). W3-C1 still
  in-progress; 13/stackups-and-materials.md has no canonical width table yet (re-check before closing #11/#12).
- 2026-10-02 — #1 Leeson fixed: 05/oscillators.md TL;DR (l.42), Level-2 paragraph (l.99–101), example 3 (l.140), gap note, sources [9] Rubiola, [10] Lee–Hajimiri 2000, 05/_sources rows; tools/verify/analog_oscillators.py §4 now FkT0/(2Ps) at 290 K (+assert); new tools/verify/fix_leeson_prefactor.py (Monte Carlo S_phi=N0/Ps, AM=PM split, examples) ALL PASS. KB grep: no other 2FkT/Ps use (07, 06 already FkT/2Ps).
- 2026-10-02 — #2 fixed 07/phase-noise-and-jitter.md:63. #3 fixed 05/low-noise-analog-design.md:42,68,107 and 05/op-amps-real-limitations.md:141,168 (also corrected "3.99 at 290 K" → 4.00). #4 fixed 04/inductors-at-rf.md:62 (IACS 3.17 µm at 433.92 MHz = 3.18 at 433 MHz).
- 2026-10-02 — Coordinator message: items C1, C2 added; domain 20 now editable surgically.
- 2026-10-02 — C1 band-edge: 21/gnss-interference-jamming-spoofing.md:78,115,122 (CH 24; CH 23 only ≤125 kHz); 15/rocket-telemetry-radio-design.md:48 (E220 CH17 with CH24 primary),145 (edge rule); 15/ism-band-plans-duty-cycle.md:120; 15/lora-modules-ebyte-rfm-heltec.md:106 (CH17 alt); 19/singapore-imda-rules.md:142 (E22 edge rule); 20/gnss-front-end-design.md:152. 20/lora-rocket-telemetry-link.md:54,229 already correct (W3-C6). 09 only uses 433.125 as an example frequency (no change). 13/shielding uses 433.125 harmonics only (not mine).
- 2026-10-02 — PAUSED by coordinator while starting #5 (only grep done, no partial edits). Done so far: #1–#4, #13, C1, C2.

- 2026-10-03 — RESUMED. Coordinator: W3-C1 canonical 50 Ω width table now at 13/stackups-and-materials.md#canonical-50-ω-width-table → apply D6 #11/#12 (prompt #5/#6) with links.
- 2026-10-03 — W3-C1 canonical 50 Ω width table present at 13/stackups-and-materials.md:48 (### Canonical 50 Ω width table): 7628 0.359 masked/0.377 bare; JLC0216A 2-layer 1.43 mm core 2.692 mm masked, CPWG 0.918/1.089 mm (0.203 mm gap).
- 2026-10-03 — #20 extra: 21/gnss-on-rockets-dynamics-and-limits.md:129 '> 100 dB' → 50–160 dB at L1 (supersedes tick note).
- 2026-10-03 — Issues #5–#24 processed (see ticks). Extra instances found by re-grep and fixed: 03/impedance-matching (via), 06/amplifier-stability (via), 20/bandpass (via allowance note), 14/fft (Hamming), 17/sdr + 17/oscilloscopes (complex FFT floor −SNR−10logN, simulated −80.0 dBFS @1024/8-bit), 16/openems-workflow (2-layer stack note), 20/lna (CPWG width), 21/gnss-on-rockets (CFRP), 19/_index (E220 21 dBm). Next: #23 taxonomy, Task 2 canonical page.
- 2026-10-03 — Canonical page written: kb/00-math-foundations/canonical-values-and-conventions.md; verify script tools/verify/fix_canonical_values.py ALL PASS. Coordinator added D1, D2, G-18-01, G-15-02, G-18-02.

## Contradictions / discrepancies found
- D6 #15 cited 18/rf-transceiver-ics.md:86 for f_s/B; the statement is actually at :164 (line drift).
- D6 #14: beyond RTL V3, 14 already had LSF/Rowetel figures for Pluto (6.1 dB @437) and HackRF (11.1 dB @435), so 17's "not found" was wrong for those too.
- New during fixes: FFT per-bin floor for complex IQ is −SNR−10logN (17 used the real-data N/2 form for SDRs) — simulated −80.1 dBFS vs −80.0 formula (1024 pt, 8-bit).
- New: the old 03 stub rule "0.5–1.5 mm" understated a single-via short (≈1.8 mm at 0.54 nH; ≈3.3 mm with the old 1 nH).
- New: 20/lna-design-walkthrough said "50 Ω CPWG ≈ 0.36 mm" on 7628; 0.36 mm is the microstrip width, CPWG with 0.203 mm gap is 0.306 mm.
- G-15-02: "GPS L2 band" was defined as the ±10.23 MHz main lobe (CH 0–2) in 15/20 and as the allocation to 1240 MHz (CH 0–3) in 21 — same physics; unified avoid-list CH 0–9.
## Cross-domain notes
- Residuals for W3-C1, W3-C6, running agents and Wave 6 are in gaps/W5-E9-deferred.md.
- Closed GAP_REGISTER rows C53–C55 (G-18-01, G-15-02, G-18-02).
## Resume instructions
TASK COMPLETE — nothing to resume. (Historical pause notes below.)
Status at pause: #1, #2, #3, #4, #13, C1, C2 fixed (ticked above). No file is half-edited.
Next steps, in order:
1. #5: 19/singapore-imda-rules.md:50 and :53 and 15/lora-modules-ebyte-rfm-heltec.md:55 — replace "≤ ~20 dBm"/"≤ 20 dBm" (917–925 MHz)
   with "21 dBm (lowest step) plus a ≥ 1 dB pad or a ≤ 1.15 dBi antenna, ≤ 1 % duty"; bump 19/singapore last_updated (its l.142 was
   already edited for C1 without a bump). Also check 20/lora-rocket-telemetry-link.md:196 ("E220 20 dBm (30c)") — 20 is now editable.
2. Then #6, #7, #8, #9, #10, #14, #15, #16, #17, #18, #19, #20, #22, #23, #24 in that order (D6 "recommended fix" column; grep the
   quoted text — line numbers drift). #21: verify 20/lora-rocket-telemetry-link.md:54 (W3-C6 already says CH 24 for SG at >125 kHz) → likely no-change.
3. #11/#12: re-check kb/13-pcb-rf-layout-emc/stackups-and-materials.md for a W3-C1 canonical width table; if present, align 03 with a link; else defer
   in gaps/W5-E9-deferred.md (do not edit 13).
4. Task 2: write kb/00-math-foundations/canonical-values-and-conventions.md (template; D6 §3 tables + conventions list + Singapore limits +
   band-edge rule fc ± BW/2 inside 433.05–434.79 → E22 CH 24, CH 23 only ≤ 125 kHz; E220 CH 17 with CH 24 primary); one line in CONVENTIONS.md §4;
   link from kb/00-math-foundations/_index.md; add slug to tools/taxonomy.md 00 line.
5. Task 3 re-greps; Task 4: python3 tools/build_index.py --check; re-run tools/verify/analog_oscillators.py and fix_leeson_prefactor.py (both pass now).
6. Write gaps/W5-E9-deferred.md; set Status complete; final report ≤ 250 words via SubagentHandback.
Log helper (optional): scratchpad logtool.py (add/tick) — may be gone in a new session; edit this file directly instead.
