# Research log W4-D4: curriculum coverage check (textbook ToCs + university syllabi)
Status: complete (2026-10-02)
Owner scope: gaps/D4-curriculum.md, this log (no kb/ edits)

## Plan
Method: for each source get chapter/section titles (facts only), map to KB page(s) by grepping
FAQ.md / INDEX.md / kb/ headings; open the section when unsure. Status per row:
covered / shallow (say what is missing) / missing. Write results into gaps/D4-curriculum.md one
source at a time (crash safety).

Textbooks
- [x] Pozar, Microwave Engineering 4e (Wiley page ToC; table 3.1 written)
- [x] Balanis, Antenna Theory 4e (Wiley ToC; table 3.2)
- [x] Razavi, RF Microelectronics 2e (Pearson sample PDF ToC; table 3.3)
- [x] Lee, Design of CMOS RF ICs 2e (Cambridge chapter list only; table 3.4)
- [x] Skolnik 3e (chapter scopes only; GBV 429 twice; table 3.19, medium confidence)
- [x] Richards FRSP 2e (McGraw-Hill page chapter list; table 3.10)
- [x] Mailloux, Phased Array Antenna Handbook 3e (pageplace.de publisher preview; table 3.7)
- [x] Horowitz & Hill AoE 3e (artofelectronics.net ToC; table 3.15)
- [x] Proakis & Salehi 5e (McGraw-Hill OLC brief ToC; table 3.11)
- [x] Rappaport 2e (InformIT ToC; table 3.12)
- [x] Ott, EMC Engineering (Wiley ToC; table 3.5)
- [x] Bogatin SPI 3e (InformIT partial 3e + Pearson 2e sample PDF; table 3.13)
- [x] Kaplan & Hegarty, Understanding GNSS 3e (NavtechGPS ToC PDF; table 3.8)
- [ ] ARRL Handbook (RF chapters) + ARRL Antenna Book
- [x] Hayward EMRFD (ARRL news release contents; table 3.18)
- [x] Cripps 2e (Skillsoft chapter list; table 3.9)
- [x] Hong & Lancaster, Microstrip Filters (2e Hong; Wiley ToC; table 3.6)
- [x] Lyons, Understanding DSP 3e (InformIT ToC; table 3.14)
Courses
- [x] MIT 6.013, 6.776, 6.S02 / MIT LL radar (tables 3.20–3.28)
- [x] Stanford EE133, EE252, EE314, EE359 (tables 3.20–3.28)
- [x] Berkeley EE142, EE242A, EE117 (tables 3.20–3.28)
- [x] Georgia Tech ECE 6360/6361 (tables 3.20–3.28)
- [x] Caltech EE153 (tables 3.20–3.28)
- [x] TU Delft / ETH RF courses (tables 3.20–3.28)
- [x] Coursera/edX; Keysight/R&S curricula (tables 3.20–3.28)
Output
- [x] Summary stats, top-50 ranked list, per-source tables, level check

## Log (append-only)
- 2026-09-29 — Wiley pages embed ToC text (wTableOfContents); extractor script in scratchpad (wiley.py). Got Pozar, Balanis, Ott, Hong ToCs. Wrote Pozar table (3.1). Keyword-grep helper k.sh used for mapping.
- 2026-09-29 — started; read CONVENTIONS.md, HANDOFF.md, INDEX.md (196 pages; domains 13, 16, 18,
  20, 21 still largely planned), tools/taxonomy.md, gaps/D1 header for format.
- 2026-09-29 — Balanis, Razavi (Pearson ptgmedia sample-pages PDF, pdftotext -layout), Lee (Cambridge HE page tocSimplified; LoC catdir 403; OpenLibrary has no ToC) mapped; tables 3.2–3.4 written.
- 2026-09-29 — Ott, Hong mapped (tables 3.5, 3.6). Skolnik: GBV library ToC PDF (gbv.de/dms/hebis-darmstadt/toc/195384067.pdf) found but GBV returned HTTP 429 (rate limit) to curl and WebFetch — retry later.
- 2026-09-29 — Mailloux mapped (table 3.7). artechhouse.com is Cloudflare-challenged (not bypassed); api.pageplace.de publisher preview PDFs are a usable alternative for Artech books.
- 2026-09-29 — Kaplan (navtechgps.com/wp-content/uploads/1024B_TOC.pdf) and Cripps (skillsoft.com book page chapter list) mapped; tables 3.8–3.9. kb/21-gnss is empty at check time.
- 2026-09-29 — Richards (mheducation chapter list; AccessEngineering/VitalSource 403), Proakis (highered.mheducation.com OLC brief ToC .doc via curl|strings), Rappaport (informit.com ToC tab) mapped; tables 3.10–3.12. Skolnik still blocked by GBV 429.
- 2026-09-29 — Bogatin mapped (3.13). O'Reilly/ebooks.com 403; InformIT 3e ToC truncated at §4.2; used Pearson 2e sample PDF for sections. NOTE: domain-13 pages rf-layout-rules, vias-stitching-fencing, shielding-and-isolation appeared during the run — re-check Ott/Bogatin rows at the end.
- 2026-09-29 — Lyons mapped (3.14). Finding: z-transform absent KB-wide (confirmed by 00/_index known gaps).
- 2026-09-29 — AoE mapped (3.15). Gaps: comparators, thermal design, output stages, cable driving, lock-in.
- 2026-09-29 — PAUSED by coordinator. Tables 3.1–3.15 complete in gaps/D4-curriculum.md. ARRL Handbook 96th-ed chapter list fetched (arrl.org/arrl-handbook-2019, 'Table of Contents' block) and Antenna Book 24th-ed chapter list fetched (arrl.org/arrl-antenna-book, 'Contents' block) but NOT yet written.
- 2026-10-02 — RESUMED. KB now 214 pages (13: +connectors-and-launches, emc-emi-fundamentals, rf-layout-rules, shielding-and-isolation, vias-stitching-fencing; 08: +slot-antennas; 16: +simulation-validation, tool-landscape-overview; 18 complete; 20: 2 pages; 21 still empty). Wrote ARRL Handbook (3.16) and Antenna Book (3.17).
- 2026-10-02 — Hayward (3.18) and Skolnik (3.19, chapter level; GBV still 429) written. Textbooks complete. Next: courses.
- 2026-10-02 — Courses mapped (3.20–3.28). Inaccessible: Stanford explorecourses (login), EE314 (empty dir), Berkeley www2.eecs (ECONNREFUSED), TU Delft site (TLS verify fail), ll.mit.edu & artechhouse (Cloudflare), GBV (429). MIT '6.S02' not found as a radar course; used OCW RES.LL-001/003 instead.
- 2026-10-02 — Re-checked rows against newly landed pages (13: emc-emi-fundamentals, shielding-and-isolation, power-distribution-decoupling-for-rf, mixed-signal-layout, thermal-management-rf; 08: slot-antennas, inductive-coupling-rfid-nfc-wpt; 21: gnss-signals-and-codes, gnss-receiver-architecture-acquisition-tracking, gnss-on-rockets-dynamics-and-limits; 20: bandpass-filter-design-walkthrough). Kaplan table rewritten. Stats computed by scratchpad/stats.py (weighted by n column): 1725 in-scope sections, 69 % covered / 21 % shallow / 10 % missing. Wrote §1, §2 (top-50), §4 level check, §5 access notes. COMPLETE.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| 1 | wiley.com product pages (Pozar 4e, Balanis 4e, Ott 2009, Hong 2e) | publisher ToC | exact section titles | raw HTML field wTableOfContents via curl; exact |
| 2 | ptgmedia.pearsoncmg.com/images/9780137134731/samplepages/0137134738.pdf | publisher sample pages | Razavi 2e ToC | official Pearson sample; exact |
| 3 | cambridge.org/highereducation/books/the-design-of-cmos-radio-frequency-integrated-circuits/… | publisher | Lee 2e chapter list | chapter level only |

## Contradictions / discrepancies found
- None between sources and KB physics (not in scope); note: 'Level 1' in advanced-domain pages is a results summary, not high-school level — conflicts with CONVENTIONS §3 intent ('algebra-level statement').

## Knowledge gaps noticed (for later gap-filling)
- See gaps/D4-curriculum.md §2 (ranked top-50). Headline: radar tracking/monopulse; Kalman/estimation; multiple/random access (ALOHA); array synthesis; wideband antennas; z-transform; ISF phase noise; Green's functions; GNSS remainder.

## Cross-domain notes

## Resume instructions
Task complete. To refresh: re-run the greps for rows marked shallow/missing whose target page has since landed (see gaps/D4-curriculum.md §5 re-check trigger), then recompute stats (weighted by the n column; script logic described in §0).
