# Research log W6-F3: second (final) internal consistency audit
Status: complete (2026-10-13)
Owner scope: gaps/D7-second-consistency-audit.md and this log only. No kb/ edits. No sub-agents.

## Plan
- [x] Step 0: read CONVENTIONS, canonical page, D6, GAP_REGISTER §8 (done at start)
- [x] C5 mechanical: build_index --check (on a copy), pytest tools/rfcalc/tests, tools/verify/*.py (120 s each, skip *openems*, skip scripts another agent is running)
- [x] C1 canonical-value greps across all domains (02/03/16 last, provisional)
- [x] C2 re-derive ≥ 60 Wave-5 worked-example numbers (scratch scripts in scratchpad)
- [x] C3 new-vs-old contradictions (Doppler rate, Yagi stacking, 866 vs 917, P.372, SF during boost, NF claims)
- [x] C4 conventions (e^{jωt}, RHCP, dBic, E/N0, processing gain, G_p)
- [x] C6 GAP_REGISTER closed-row link resolution; FAQ duplicate questions
- [x] Write gaps/D7-second-consistency-audit.md; final report

## Status of concurrent agents at start (2026-10-13)
- S5 (02): log says complete. S6 (03): in-progress. S11 (16): in-progress. S18b (quality pass): in-progress.
- Findings in 03 and 16 are provisional; 02 findings are final (S5 complete) unless S18b edits.

## Log (append-only)
- 2026-10-13 — Step 0 read. Log created.

## Resume instructions
If paused: read Plan ticks and the Log; D7 draft (if any) is gaps/D7-second-consistency-audit.md; scratch scripts in the session scratchpad are disposable — re-derive from this log's notes. Continue with the first unticked item.
- 2026-10-13 — C5 partial: build_index --check run on a scratch copy (live INDEX/FAQ byte-identical to regenerated): 0 broken links, 0 control chars, 0 missing sections, 288 pages. Own extra checks: body anchors (2 broken: 04/_index → ferrites L3 en-dash slug; 16/_index → spice example A, provisional), front-matter paths 0 broken, all pages in taxonomy. pytest rfcalc 159 passed. verify/*.py running in background (scratch copy, 4 workers, 120 s): analog_ngspice needs argv (helper); several TIMEOUTs under load — rerun serially later.
- 2026-10-13 — C1/C2/C3 findings so far (to D7): SF-during-boost advice 09 (SF ≤ 9 at 915) vs 15/20 (SF ≤ 8 @125k); Doppler-rate examples in 04/10/14 use vehicle accel without v⊥²/R caveat; 08/antenna-measurement man-made noise uses only extrapolated P.372 lines (76/257/690 K) vs measured Table 3 (580/730/1150 K) on 07/15/08-multiband; 08/antennas-on-rockets licence note uses 917–925 for E220 (not 866–869 best band); 10/multiple-access treats 917–925 as the E220 band; 17/resonator uses 1.51 mm "JLC 2-layer" dielectric (canonical 1.43 mm core); 15/ground-station Ex3 station B −6 dB (half-wave dipole gives −8.7 dB; "10 dB better" → 7.5 dB); 13/emc Ex2 says 920–925 band (now 917–925). ~70 numbers re-derived, all others reproduce.
- 2026-10-13 — C6: GAP_REGISTER closed rows: all page refs resolve (abbreviated slugs are unique prefixes); C56 anchor uses "pass-fail" (GitHub slug is "passfail"). FAQ near-duplicate scan: ~45 pairs; checked torque, fade margins, active-antenna gain, SG radar rules — consistent.
- 2026-10-13 — Wrote gaps/D7-second-consistency-audit.md (26 issues: 2 wrong, 4 inconsistent, 7 ambiguous, 13 cosmetic; ≈140 numbers re-derived). S6 finished during the audit (03 findings final); S11 and S18b still running (16 provisional). Remaining: fill the <!-- RERUN-RESULTS --> placeholder in D7 §4 with the serial re-run of the 22 timed-out verify scripts (scratch runner rerun.py → runs/_rerun.txt), then set Status complete.
- 2026-10-13 — RESUMED after network drop (coordinator: S5, S6, S18b finished; only 16/S11 still editing). Serial re-run of the 22 timed-out scripts: 11 pass, 11 still exceed 120 s with no output (slow, not crashed); s18b_citation_check passes from repo root. D7 §4 filled; header updated (02/03 final, 16 provisional). Status complete.
