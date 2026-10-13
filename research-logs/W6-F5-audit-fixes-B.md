# Research log W6-F5: D7 audit fixes, Agent B
Status: complete (2026-10-14)
Owner scope: kb/00, kb/03 (G_P note only), kb/06, kb/07, kb/09 (#11 one line), kb/11, kb/20 (patch page), gaps/GAP_REGISTER.md, gaps/D7, tools/ (glossary, verify script clean-ups). NOT domain 16 (W5-S11 editing).
Parallel agent: W6-F4 fixes D7 #1, #3–#7 (re-read shared files right before editing).

## Plan (checklist)
- [x] #2 11/fmcw-radar Ex 2: USRR 22.5 m → 75 m with 15 MHz IF; fix dependents
- [x] R_b (SF − 2DE) on canonical page + 07/sensitivity-and-mds (D7 #9); grep for other copies; re-run fix_canonical_values.py
- [x] 06/vco Ex 1: TCXO alone −115 dBc/Hz, not "TCXO-limited" (D7 #8)
- [x] #10 G_P vs G_p: G_power / G_proc disambiguation; canonical page; tools/glossary_ambiguous.md; glossary_harvest.py --build
- [x] #11 09/atmospheric (already fixed when checked) landed case: label assumption set
- [x] #12 20/patch trim rate per mm of side vs per edge
- [x] #13 06/receiver-architectures RTL-SDR NF at L-band
- [x] #24 GAP_REGISTER C56 anchor (pass-fail → passfail)
- [ ] #26 16/_index anchor — DEFERRED (W5-S11 still editing 16)
- [x] tools: s18b_citation_check.py output path from __file__
- [x] tools: analog_ngspice.py usage message
- [x] tools: 11 slow scripts — runtime header comment (measured) or --quick; results unchanged
- [x] GAP_REGISTER §8 change log; mark D7 issues fixed; build_index.py --check; pytest

## Log (append-only)
- 2026-10-13 — read CONVENTIONS, canonical page, D7. Note: task numbering swaps D7 #8/#9 (task #8 = R_b = D7 #9; task #9 = VCO = D7 #8). D7 #17 (03 via label) is assigned to Agent B in D7 §5 but not in my brief — left for orchestrator.

## Resume instructions
Work down the checklist; each item is independent. Re-read a file before editing it; bump last_updated to 2026-10-13.
- 2026-10-14 — (date rolled over; last_updated now 2026-10-14). Started background timing of the 11 slow scripts on a scratch copy of the repo (3 parallel, 30 min cap) so the header runtimes are measured, not guessed.
- #2 DONE: 11/fmcw-radar Ex 2. radar_fmcw.py's TI table shows the profiles do NOT share one IF: LRR 15 MHz (16.67 Msps), MRR 10, SRR/USRR 4.5 MHz (5 Msps). So TI's 22.5 m is right for USRR's own IF; the page's "same ~15 MHz IF" claim was wrong. Rewrote: same 15 MHz IF → 75 m; TI's 4.5 MHz → 22.5 m; R_max/ΔR = f_IF·T_ADC (450/750/225). Table unchanged (correct).
- R_b (D7 #9) DONE: canonical Level-1 row → (SF − 2DE), DE = 1 with LDRO (T_sym ≥ 16.38 ms: SF11/12 @125, SF12 @250), SF12/125 = 244 b/s. 07/sensitivity: formula, Eb/N0 note (+0.79 dB at SF12 with LDRO), table header "DE = 0" + note (20/244/488 b/s for the three LDRO rows), Ex 1 (244 b/s). Grep for copies: 15/lora-modules :61 (DE = 0 form; candidates need no LDRO — labelled); 10/weak-signal :46, :153 and 10/modulation-choice :116 labelled "nominal (DE = 0)". 15/lora-phy and rfcalc.lora already correct. Added 2 checks to fix_canonical_values.py (R_b SF12/125 LDRO 244; LDRO auto-on rule) → ALL PASS.
- 06/vco Ex 1 (D7 #8) DONE: re-derived from rfckt_pll.py model at 1 kHz: TCXO −115.2, ADF4351 1/f −115.3, in-band floor −122.2 → total −111.8 dBc/Hz. Wording now "reference and PLL chip together, not TCXO-limited" with the three terms.
- #13 DONE: 06/receiver-architectures :227 RTL-SDR NF ≈ 12 dB at L-band IF (canonical 11.9 dB @ 1280 MHz). Cascade recomputed: 0.800 dB with 6 or 12 dB SDR, 0.803 dB with 20 dB (D7's "≤ 20 dB unchanged" slightly overstated; wrote the 0.803).
- #10 DONE: renamed operating power gain G_P → G_power (03/s-parameters, 06/lna-design, 06/_index; 18 "G_P,power" → G_power) and processing gain G_p → G_proc (10/spread 18 subs, 10/multiple-access 2, 15/lora-phy 3), with a first-use note on 03, 06/lna and 10/spread. Canonical Level-1 table: new "Gain symbols" row. tools/glossary_terms.txt: DSSS/processing-gain formulas → G_proc, new "operating power gain" entry; tools/glossary_ambiguous.md G_p row rewritten (also lists 05/oscillators' tank conductance G_p). glossary_harvest.py --build: 1086 terms, OK. 05/oscillators m = G_c/G_p (conductance) left as is.
- #11 SKIPPED: W6-F4's plan lists #11 as theirs and the 09/atmospheric line already carries the canonical-set label (checked 2026-10-14). No edit by me.
- #12 DONE: 20/patch :159/:160 → "≈ ∓36 MHz per mm of side length, i.e. ≈ ∓70 MHz per mm per edge". Kept the page's 36 MHz/mm (its calibration set 43.8/44.71/45.7 mm gives 36/34 MHz/mm; D7's −f/L = 35.2 is the same within rounding). Lines 48/134 already say "per mm of side" — unchanged.
- #24 DONE: GAP_REGISTER C56 anchor pass-fail → passfail (matches the heading slug).
- tools DONE: s18b_citation_check.py — glob and output path from __file__ (ROOT/HERE); tested from / on the scratch copy (writes into its own dir). analog_ngspice.py — usage message (no args/-h: exit 0; partial args: exit 2).
- D7 #17 DONE (D7 §5 assigns it to Agent B; W6-F4's status table lists it as "agent B's in §5 but not in W6-F5's brief", so I took it): 03/microstrip-discontinuities :198 via labelled "h = 1.51 mm model input; 0.54 nH for the canonical 1.6 mm via". No numeric change.
- pytest tools/rfcalc/tests: 159 passed.
- Slow-script timing in progress (scratch copy, 3 in parallel, load average 30–70 from other agents): pcb_stackup_widths 161 s, radar_detection_cfar 186 s, both exit 0 / ALL PASS.
- Slow scripts (all exit 0, no FAIL lines): ant_yagi 684 s, array_steering 530, rfckt_filters 606, rfckt_lna 220, s4_vco 198, radar_detection_cfar 186, pcb_stackup_widths 161, tline_microstrip 153, s6_coupled_offset 141, sim2_nec_yagi_optimise 132, rfckt_pa 112. Measured-runtime header comment added to 10 (not sim2_nec — S11/domain 16). No --quick modes added (keeps results identical).
- D7 agent-B status table added (§2); GAP_REGISTER §8 entry added. build_index.py --check: 288 pages, 0 broken links / control chars / missing sections. pytest 159 passed. fix_canonical_values ALL PASS.
- Left for orchestrator: D7 #26 (16/_index anchor) after W5-S11 finishes. Optional D7 §5 item (front-matter and anchor checks in build_index.py) not done.
