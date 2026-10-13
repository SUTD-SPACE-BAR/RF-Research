# Research log W4-D6: internal consistency audit of kb/
Status: complete (2026-10-02)
Owner scope: writes ONLY gaps/D6-consistency-audit.md and this log (no kb/ edits)

## Plan
- [x] Step 0: read CONVENTIONS.md, INDEX.md, gaps/AGENT_REPORTED_GAPS.md, HANDOFF.md
- [x] Item 0: Leeson prefactor (05 oscillators vs 07 phase-noise vs 06 VCO/PLL) — derive, cite Leeson 1966 / Rubiola
- [x] Check 1: physical constants & reference values (k, T0, kT0, c, eps0, mu0, eta0, Cu rho, FR-4, RO4350B)
- [x] Check 2: standard results (FSPL, horizon, Fresnel, dipole Z/G, Chu, Ae, Friis, IP3, SFDR, sensitivity, SQNR, jitter SNR, matched filter, windows, radar eq)
- [x] Check 3: LoRa numbers (SNR limits, sensitivities, ToA, drift, Doppler, EBYTE, Singapore limits)
- [x] Check 4: conventions (e^{jwt}, Gamma sign, steering vector sign, CP handedness, dBi/dBic/dBd, ERP/EIRP, RMS vs peak)
- [x] Check 5: contradicting claims (50 ohm, ENIG, lambda/10 vs lambda/20, via L, Kraus helix, RTL-SDR IF)
- [x] Check 6: tools/build_index.py --check (broken links, missing sections)
- [x] Check 7: front-matter sanity; duplicate topics (link budgets 09/15/20; NF measurement 07/17; rockets 08/15)
- [x] Domains 13, 20, 21 last (provisional)
- [x] Write gaps/D6-consistency-audit.md incrementally (summary, issue table, canonical values, misconceptions)

## Log (append-only)
- 2026-10-02 — log created; Step 0 reads done (CONVENTIONS, HANDOFF, AGENT_REPORTED_GAPS, INDEX head). 260 md files in kb/, ~40.5k lines.

- 2026-10-02 — Leeson resolved (issues #1–2 written to gaps/D6). Rubiola arXiv:physics/0502143 Eqs 1.4/1.26/1.39 confirm FkT/(2Ps) with Ps at sustaining-amp input; Lee&Hajimiri 2000 2FkT/Psig = tank-power definition (6 dB by definition).
- 2026-10-02 — Checks 1–5 largely done by grep (helper script kg.py in session scratchpad; recreate: python regex search over kb/**/*.md printing file:line). Consistent: kT0, c/eps0/mu0, eta0 (120π flagged in 02 already), FSPL 32.45 everywhere, horizon 4.12, Fresnel 550 form, dipole Z/G, Chu/McLean, IIP3 cascade, SFDR, LoRa SNR limits, ToA examples (all match rfcalc), drift limit + Doppler-rate examples (04/09/10/14/15/20 agree), RHCP (x−jy)e^{−jkz}, steering e^{+jkxu}, ERP=EIRP−2.15, peak phasors ½Re{VI*}, ENIG ratios, λ/10–λ/20 rules, window table (Hamming 1.75 with 0.54; NEW: harris 1.78 = scalloping of 'exact Hamming' a0=25/46), radar (4π)^3.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| 1 | E. Rubiola, "The Leeson effect", arXiv:physics/0502143 (rev. 2024-11-26), Eqs. 1.4, 1.24–1.26, 1.37–1.39, 2.1 | tutorial/peer-level preprint (author's book CUP 2008) | L = Sφ/2; b0 = FkT0/P0, P0 at sustaining-amp input; Leeson formula | read via pdftotext (exact text) |
| 2 | T. H. Lee, A. Hajimiri, "Oscillator phase noise: a tutorial", IEEE JSSC 35(3) 326–336, 2000 (UCSB course copy) | peer-reviewed | tank-noise derivation, equipartition, 2FkT/Psig modified Leeson | equations are images; mechanism text read; 2FkT/Psig confirmed by search snippet + derivation |
| 3 | tools/rfcalc (lora.py), tools/verify/* (lora_toa, noise_phase_jitter, analog_oscillators, rfckt_pll), own scratch scripts | KB tools | recomputation of ToA, Leeson, windows, skin depth, via L, jitter SNR, FSPL | — |

- 2026-10-02 ~16:30 — issues #11–24 written; link check re-run (243 pages, 7 broken links, 0 missing sections); summary, canonical-values table (§3) and misconceptions (§4) written. Task complete.

## Contradictions / discrepancies found
(see gaps/D6-consistency-audit.md issue table — that file is the master record)

## Knowledge gaps noticed (for later gap-filling)
- See gaps/D6-consistency-audit.md §4 (items 1, 4, 9, 10).

## Cross-domain notes (things other domains should cover/link)

## Resume instructions (what the next agent should do if this one is interrupted)
- Task COMPLETE. Output: gaps/D6-consistency-audit.md (24 issues, canonical-values table §3, misconceptions §4).
- Wave 6 second audit: re-run the canonical-value greps on pages created after 2026-10-02 15:00 (00/z-transform, 08/lens-reflectarray,
  08/multiband, 17/bench-measurement-recipes, 20/fmcw-radar-build, 20/sdr-receiver-build, 21/sdr-gnss-and-diy-receivers and later 13/20/21 pages),
  re-run build_index --check on a copy (the script rewrites INDEX/FAQ), and tick off fixes for issues #1–24.
