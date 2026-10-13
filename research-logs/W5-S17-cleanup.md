# Research log W5-S17: Clean-up after the running tasks
Status: complete (2026-10-13)
Owner scope: new kb/09-propagation-link-budget/satellite-links-doppler-tracking.md (+ 09 _index/_sources, taxonomy row);
surgical edits in 15/lora-impairments-doppler-drift-timing, 15/ground-station-design, 19/rf-exposure-safety (G-19-04 only),
16/nec-antenna-modelling (PyNEC quirks section only), 07/phase-noise-and-jitter (Leeson example), 21/gnss-interference-jamming-spoofing and
20/gnss-front-end-design (IMD rows, only if S13 has not done so), tools/taxonomy.md, _index.md of non-running domains,
gaps/GAP_REGISTER.md §3/§5, gaps/W5-S17-index-todo.md; scripts tools/verify/s17_*.py.
Do NOT edit _index.md of 06, 08, 10, 02, 03, 04, 05, 13, 19, 16, 18, 21 (running slices) — write lines to gaps/W5-S17-index-todo.md.

## Plan
- [x] G-09-01 — new page 09/satellite-links-doppler-tracking (LEO/MEO/GEO geometry, slant range, pass, Doppler + rate, link budgets 437 MHz CubeSat / 137 MHz Meteor-M, G/T, Gpredict/hamlib); script s17_satellite_pass.py (Singapore pass)
- [x] G-15-01 — 15/lora-impairments: replace 917–925 MHz E220 advice with 866–869 MHz CH 17/18 and duty arithmetic; link 19
- [x] G-15-03 — Doppler-rate tables: add v⊥²/R term; script s17_doppler_rate_los.py; fix 15 (+ copies in 09/20)
- [x] G-19-04 — 19/rf-exposure-safety: 5 % multi-transmitter rule, licensee responsibility, whole-body resonance, HF exemption thresholds
- [x] (a) 15/ground-station-design P.372 city 1150 K → ≈720 K, flag extrapolation > 250 MHz
- [x] (b) 16/nec-antenna-modelling: three PyNEC quirks from W5-S12 log
- [x] (c) 07/phase-noise-and-jitter Leeson example −164 → recompute
- [x] (d) Wi-Fi ch6/ch11 IMD rows in 21 + 20 (check S13 first)
- [x] (e) index chores (taxonomy + _index; todo file for running domains)
- [x] (f) glossary_harvest --build; build_index --check
- [x] Close items in GAP_REGISTER §5, mark §3

## Log (append-only)
- 2026-10-13 — Step 0: read CONVENTIONS, register rows (§3 ranks 4, 6, 13, 97; §6 S17; orchestrator notes), canonical values page. Log created.

- 2026-10-13 — G-15-03: wrote tools/verify/s17_doppler_rate_los.py (+ _output.txt). Sympy proves R̈ = a·r̂ + v⊥²/R; numeric check on proj_lora_link trajectory < 0.04 m/s² away from steps. Max R̈ 15.3 g (0.5 km), 13.7 g (2 km, matches 20 recipe), 11.1 g (5 km) on an 11.1 g flight. 868 MHz SF9/125 fails from 0.5/2 km stations only when the rotation term is counted. Edited 15/lora-impairments (Level 1 note, new #### subsection + table, TL;DR, rules table, WE2, verify list).
- 2026-10-13 — G-15-01: 15/lora-impairments Practical note rewritten — E220 in 866–869 MHz (CH 17 with E22 CH 24; CH 18 with CH 23; never CH 16); 917–925 MHz = 100 mW e.r.p. ≤ 1 % duty, duty arithmetic (71.9 ms → 0.14 Hz; 10 Hz = 72 % occupancy); WE1 868 numbers added. Links to 19, 20, 00 canonical.
- 2026-10-13 — Also aligned 15/rocket-telemetry-radio-design TL;DR "Two bands" and 15/lora-modules WE1 with 866–869 MHz guidance (same G-15-01 issue). 09/multipath-fading-doppler: TL;DR + table note that a_r = R̈ incl. v⊥²/R. 20/lora-rocket-telemetry-link already had the term (no edit).
- 2026-10-13 — Orchestrator note (a): fetched Rec. ITU-R P.372-13 PDF (itu.int, pdftotext). Table 3 "Outdoor man-made noise measurements in Europe" at 425 MHz: Fa 6/4/3 dB city/res/rural (=1155/728/579 K), decile deviations 1–2 dB. Table 1 line validity 0.3–250 MHz (eq. 13). The 1150 K in 15/ground-station-design is the MEASURED Table 3 value, not wrong; ≈720 K is the extrapolated Table 1 line. So NOT replaced: page now gives both, flags the 720 K as an out-of-range extrapolation, keeps 1150 K as conservative city figure. tools/verify/s17_p372_city.py PASS.
- 2026-10-13 — Orchestrator note (c): recomputed (s17_leeson_check.py PASS). The 07 example was numerically right: −164 dBc/Hz is L(10 MHz) = −163.6 (10 MHz is inside the 10.8 MHz corner, +3.4 dB), floor −167 stated separately. W5-E7's "floor −164" reading was a misreading. Clarified wording on 07/phase-noise-and-jitter §(d). 06/oscillator-phase-noise-ltv-isf:239 still lists this as an open issue (06 owned by S14/S15) → index-todo file.
- 2026-10-13 — Orchestrator note (b): verified the three PyNEC quirks empirically (tools/verify/s17_pynec_quirks.py + output: no RP/XQ → get_input_parameters None; GE0 monopole 42.6−j1686.6 Ω vs GE1 36.0+j0.36 Ω; E-field arrays θ-fastest). Added to 16/nec-antenna-modelling TL;DR trap bullet + 3 Common-mistakes bullets (surgical; S11 owns 16 and is running but had not edited this file since 2026-09-29 — S11 should re-read before its G-16-04 edits).
- 2026-10-13 — Orchestrator note (d): W5-S13 already added the ch 6 / ch 11 IMD rows to 21/gnss-interference (lines 88–89, frequency-only caveat) → no 21 edit. 20/gnss-front-end-design had only the ch 7 example → added ch 6 (1568.75 MHz, ≈1558–1580, GPS L1/E1/B1C) and ch 11 (1593.75 MHz, ≈1583–1605, GLONASS G1) to its Level 3 IMD bullet, linking 21.
- 2026-10-13 — G-19-04: read 47 CFR 1.1307 and 97.13 via Cornell LII (eCFR bot-blocked): (b)(5)(i) shared responsibility >5 % of limit; (b)(3)(i)(A) 1 mW; (C) Table 1 incl. HF rows 1920R², 3450R²/f², R ≥ λ/2π; (b)(3)(ii)(B) sum of fractions ≤ 1; 97.13(c) licensee duty, household occupational limits. Body resonance: search excerpts of DTIC AD-A100029 (65–70 MHz, 0.36–0.4 λ; title unverified) + Hirata 2012 (grounded worst case, λ/4 monopole analogy). Script tools/verify/s17_rf_exposure_rules.py PASS. 19/rf-exposure-safety: new "Rule details" subsection (resonance, summation, 5 % rule, HF exemption table with λ/2π trap), Q list, practical note, 2 common mistakes, verify, open questions, sources 6–7. (A python escape turned \a into BEL and \t into TAB in the first insert; found by a control-char scan and repaired.)
- 2026-10-13 — G-09-01: sources read — WMO OSCAR Meteor-M N2-3 (820 km SSO, LRPT 137.1/137.9/137.9125 MHz, 150 kHz, RHCP, 80 kbps; no EIRP), sigidwiki LRPT (QPSK 72 kBd, ~120 kHz), NOAA POES decommissioning (news/wiki, 2025), Gpredict AppStream + hamlib man pages (rigctld 4532, rotctld 4533, -x uplink), P.372-13 PDF. Wrote tools/verify/s17_satellite_pass.py (ALL PASS; two-body + J2, Singapore station, 96 h pass lists, keyhole demo 156°/s, transponder Doppler, budgets 437 MHz/LoRa/LRPT, GEO elevations). Bugs found and fixed: wrong check bound for 10° slant (1756 km is right; cross-checked by law of cosines), pass duration used index count (wrong with 0.5 s steps). Created kb/09-propagation-link-budget/satellite-links-doppler-tracking.md (~200 lines, template).
- 2026-10-13 — (e) index chores: scan of all kb pages vs taxonomy/_index → only 10/weak-signal-digital-modes (S8, running: todo file) and 21/gnss-receiver-integration-u-blox (taxonomy added). New 09 page added to 09/_index (reading order, pages, FAQ), 09/_sources, taxonomy; 15/_index FAQ lines. gaps/W5-S17-index-todo.md written.
- 2026-10-13 — (f) glossary_harvest --build: 331 pages, GLOSSARY 1085 terms. build_index --check: 287 pages, 0 broken links, 0 control characters, 0 missing template sections. Own anchor check over 12 edited files: 0 bad.
- 2026-10-13 — GAP_REGISTER: closed C128 (G-15-01), C129 (G-15-03), C130 (G-09-01), C131 (G-19-04); §2/§3 marked; change-log line incl. the P.372 finding.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| 1 | Rec. ITU-R P.372-13 (2016) PDF, §5, Tables 1–5 (pdftotext) | standard | man-made noise lines (0.3–250 MHz) and 425 MHz measured medians | primary; read directly |
| 2 | 47 CFR 1.1307, 97.13 (Cornell LII copy) | regulation | 5 % rule, exemptions incl. HF, λ/2π, sum of fractions, licensee duty | WebFetch summary + short quotes; eCFR bot-blocked |
| 3 | DTIC AD-A100029 (search excerpt), Hirata et al. 2012 (abstract) | gov. report / peer-reviewed | whole-body resonance 65–70 MHz, grounded worst case | title of AD-A100029 not verified |
| 4 | WMO OSCAR Meteor-M N2-3; sigidwiki LRPT; SatNOGS (search) | agency DB / community | Meteor orbit, LRPT parameters | no EIRP anywhere; 72 kBd vs 80 kbps labelling |
| 5 | Gpredict AppStream; hamlib rigctld/rotctld man pages (search summary) | software docs | SGP4/SDP4, ports 4532/4533, -x | secondary summary |
| 6 | NOAA POES decommissioning news (RTL-SDR.com, ARNewsline, mayhem wiki) | news | APT ended 2025 | consistent with 14 _sources |
| 7 | arXiv:2506.20858 (via 15 page [5]) | preprint | Norby high-SF failure at zenith | secondary |

## Contradictions / discrepancies found
- **P.372 city noise at 425 MHz (orchestrator note a):** the note said that 1150 K was wrong and should be ≈720 K. The primary source shows that 1150 K is P.372-13 **Table 3** (measured, Europe, 425 MHz, city Fa = 6 dB), and ≈720 K is the **Table 1 line** extrapolated beyond its 250 MHz validity. Both are reported on 15/ground-station-design, with the extrapolation flagged, and 1150 K was not replaced. 08/antenna-measurement quotes the extrapolated values (690 K city at 433 MHz) and labels them as extrapolations, which is consistent.
- **07 Leeson example (note c):** there was no numerical error. −164 dBc/Hz is the value at 10 MHz, and the floor of −167 dBc/Hz was stated separately. Only the wording was clarified.
- LRPT rate: 72 kBd (sigidwiki, SatNOGS) vs 80 kbps (WMO OSCAR, SatNOGS). Not resolved.

## Knowledge gaps noticed (for later gap-filling)
- No Meteor-M LRPT EIRP or antenna pattern was found in open sources.
- No Singapore counterpart of the FCC 5 % rule was found (NEA follows ICNIRP).
- The FCC SAR-based exemption (1.1307(b)(3)(i)(B)) formula was not transcribed.
- Measured satellite reception from Singapore (Meteor/TinyGS SNR vs elevation) would calibrate the 09 budgets → candidate for GAP_REGISTER §7.

## Cross-domain notes (things other domains should cover/link)
- See gaps/W5-S17-index-todo.md (10/_index + taxonomy for S8; 06 Leeson open-issue line; 16 note for S11; optional 08/14/19 FAQ links).
- 15 pages still use 923 MHz as the "900 MHz band" column in tables. Numbers scale by f, so they are only 6 % from 868 MHz, but a future pass could relabel them to 868.125 MHz for consistency with the canonical channel.

## Resume instructions (what the next agent should do if this one is interrupted)
- Task complete. Nothing to resume; follow-ups are in gaps/W5-S17-index-todo.md.
