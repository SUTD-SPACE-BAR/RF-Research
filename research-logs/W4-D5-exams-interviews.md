# Research log W4-D5: exams / interviews / problem-set gap sweep
Status: complete
Owner scope: gaps/D5-exams-interviews.md and this log only (no kb/ edits)

## Plan
- [x] Step 0: read CONVENTIONS, INDEX, HANDOFF; create log (this file)
- [x] Fetch NCVEC pools (Technician 2022-26, General 2023-27, Extra 2024-28) as raw text (curl); save to scratchpad
- [x] Sample RF/electronics subelements: T4-T9 (T5, T6, T7, T9 esp.), G4-G9, E4-E9 → >= 200 questions
- [x] Interview-style lists (RF engineer, analog IC, antenna/radar) → >= 100 questions
- [x] Problem types from Pozar/Balanis/Razavi/Skolnik chapters + MIT OCW / Stanford psets → >= 50
- [x] For each: grep kb + read section → covered / partial / missing / KB-wrong
- [x] Write gaps/D5-exams-interviews.md incrementally (table first, then summary, KB-wrong, top-40)
- [x] Final reply <= 250 words

## Log (append-only)
- 2026-09-29 — Step 0 done: read CONVENTIONS.md, HANDOFF.md, INDEX.md (196 pages in INDEX; 230 .md files in kb incl. _index/_sources). Domains 13 (2 pages), 16 (7), 17 (13), 18 (6), 20 (0), 21 (0) still partial.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| 1 | NCVEC pools via github.com/russolsen/ham_radio_question_pool (JSON): Technician 2026-30, General 2023-27, Extra 2024-28 | public-domain exam pools | 1071 questions | raw text (curl), exact |
| 2 | rfinsights.com/rfic-interview-questions | interview list | ~100 RFIC/comms/EM questions | raw HTML (curl) |
| 3 | fanyang.substack.com wireless/RF interview post | interview list | 20 questions | WebFetch summary (topics only) |
| 4 | interviewprep.org RF engineer questions; electronicspost.com analog questions; resumegemini radar; Glassdoor antenna (search snippets) | interview lists | topics | WebFetch/search (topics only) |
| 5 | MIT OCW 6.776 (2005) PS1–PS6 PDFs | problem sets | problem types | pdftotext; paraphrased |
| 6 | Pozar 4e, Balanis 4e, Razavi 2e, Skolnik 3e chapter themes; MIT 6.013; Stanford EE133 cookbook (scratchpad) | textbooks/courses | problem types | own knowledge of ToCs; paraphrased |
| 7 | Wikipedia "Leeson's equation" (raw wikitext); Rubiola 2008; Leeson 1966; Lee & Hajimiri 2000 | refs | W1 adjudication | sources disagree on prefactor; documented |

## Contradictions / discrepancies found (KB-wrong candidates)
- W1: 05/oscillators.md:42, :99–101 Leeson 2FkT/Ps ("both sidebands") vs 07/phase-noise-and-jitter.md:29/62 and 06/vco-and-pll-synthesizers.md:83 FkT/(2Ps): 6 dB inconsistency + wrong rationale. External sources split (Leeson/Rubiola FkT/2Ps; Rhea/Wikipedia/Lee–Hajimiri 2FkT/Ps with other Ps definition).
- Near-misses (not wrong): PA TL;DR class-F 90.7 % wording; phase-quantisation-lobe fit −6.02P+4.4 vs exact tan form.

## Knowledge gaps noticed
- See gaps/D5-exams-interviews.md §3 (top-40).
- Method lesson: single-regex greps produced ~27 false "missing/partial" calls; a broad multi-term re-grep + reading the hit lines is needed before declaring a gap.

## Cross-domain notes

## Resume instructions
If interrupted: read this log's progress lines; working files are in the session scratchpad
(may be lost) — the durable progress is gaps/D5-exams-interviews.md (table rows appended in
batches). Continue from the last batch number recorded below; re-fetch pools with curl if the
scratchpad is gone.
- 2026-09-29 — Pools fetched as JSON from github.com/russolsen/ham_radio_question_pool (raw text of the NCVEC pools; Technician 2026-2030 is the current pool, 409 q; General 2023-27 423 q; Extra 2024-28 599 q). Working files in scratchpad/d5/ (dump2.py, addrows.py, kbg.sh, kbl.sh; allrows.tsv mirrors the table). Read every page's TL;DR (tldr.txt) to map the KB.
- 2026-09-29 — Batch 1: Extra E4 (63 q) → table rows 1–63 in gaps/D5. KB-wrong candidate noted: Leeson prefactor differs between 05/oscillators (2FkT/Ps) and 07/phase-noise-and-jitter (FkT/2Ps) — to check.
- 2026-09-29 — Batches 2–7: Extra E5, E6, E7, E8, E9, E3 → rows 64–459 (all Extra E3–E9 done, 459 q). New pages appeared during run (16/simulation-validation, 16/tool-landscape-overview, 18/adcs-dacs-for-sdr, 18/phased-array-and-radar-parts, 20/lora-rocket-telemetry-link) — later rows use the live KB.
- 2026-09-29 — Batches 8–13: General G4, G5, G6, G7, G8, G9, G3 → rows 460–745 (General done, 286 q).
- 2026-09-29 — Batches 14–18: Technician T3–T9 → rows 746–1012 (Technician done, 268 q). Pools complete: 1013 q?
- 2026-09-29 — Batch 19: 153 interview questions (RFInsights RFIC/comms/EM, Fan Yang, InterviewPrep, Glassdoor-style antenna, ResumeGemini radar, ElectronicsPost analog) → rows 1014–1166.
- 2026-09-29 — Batch 20: 101 problem types (Pozar, Balanis, Razavi, MIT 6.776 PS1–6 read via OCW PDFs, Skolnik, MIT 6.013, EE133) → rows 1167–1268.
- 2026-09-29 — Batch 21: RF-exposure subelements T0C, G0A, E0A (all) + 21 domain-19 rules questions (telemetry, model craft, SS, ID, Line A) → rows 1269–1326.

## Resume instructions (PAUSED 2026-09-29, exact)
- DONE: table rows 1–1326 appended to gaps/D5-exams-interviews.md (§4) — Extra E3–E9, General G3–G9, Technician T3–T9, T0C/G0A/E0A, 21 domain-19 rules q, 153 interview q, 101 problem types. Mirror: scratchpad/d5/allrows.tsv (may be lost; the gap file is authoritative).
- KB-wrong found so far: 1 — 05/oscillators.md:42 and :99–100 Leeson prefactor 2FkT/Ps with "both sidebands" rationale vs 07/phase-noise-and-jitter.md:29/62 FkT/(2Ps) (6 dB inconsistency; sources disagree: Leeson 1966/Rubiola vs Rhea/Wikipedia/Lee–Hajimiri). Row "MIT 6.776 PS6" already marked W.
- Planned edit: interview row "Amplifier linearisation techniques" → C (06/power-amplifiers covers DPD, Doherty, ET/EER, outphasing; feedforward absent).
- NEXT: (1) optional second KB-wrong sweep of C rows in 03/06/07/08; (2) compute counts/pass rates per subelement from the §4 table (strict = C; lenient = C+P; also excluding notes tagged OOS/"out of scope"); (3) write §1 Summary, §2 KB-wrong list, §3 top-40 ranked gaps at the TOP of gaps/D5 (above §4); (4) set Status complete; final ≤250-word reply.
- 2026-10-02 — Resumed after usage-limit pause.
- 2026-10-02 — Live-KB recheck (KB now 214 topic pages: new 13/emc-emi-fundamentals, 13/shielding-and-isolation, 13/rf-layout-rules, 13/connectors-and-launches, 13/vias-stitching-fencing, 08/slot-antennas, 18/rf-modules, 18/pcb-substrates-parts, 20/ground-station-tracking-yagi). Broad re-grep of all M/P concepts found false negatives in my earlier greps: SWR total-loss formula (03/reflections:111), ducting (09/fresnel:66), coax weatherproofing (03/coax:130), circular-waveguide cutoffs (08/horn:51), PIM (07/nonlinearity:104), wave ports (16/em-solvers:62), slab surface waves (08/patch:79). 27 rows corrected (fix1.py). Lesson: my single-regex greps under-detect; the broad re-grep pass is essential.
- 2026-10-02 — KB-wrong sweep: verified ~60 numeric TL;DR claims (wave-impedance extremes 256.6/553 Ω at kr 1.17 and 10 %/1 % convergence at 0.50λ/1.59λ by script; class-C 89.7 %; crystal L1/Q/Δf; phase-quantisation lobes; loop/monopole Rrad; FSPL; MD/coherent detection SNRs). All correct. Leeson: 3 pages state it; 05/oscillators is the outlier (2FkT/Ps with a wrong "both sidebands" rationale); 07/phase-noise and 06/vco-and-pll use FkT/(2Ps). Wikipedia (citing Rhea 1997) prints 2FkT/Ps — sources disagree, so the item is reported as a KB-internal contradiction + incorrect derivation, not as a single wrong number.
- 2026-10-02 — Stats: 1326 rows (1071 pool q, 153 interview, 102 problem types); 761 C / 243 P / 321 M / 1 W. Writing §1–§3.

- 2026-10-02 — DONE. gaps/D5-exams-interviews.md written: §1 summary/pass rates, §2 KB-wrong (W1), §3 top-40, §4 1326-row table. Status complete.
