# Research log W6-F4: D7 audit fixes, Agent A
Status: complete (2026-10-14)
Owner scope: surgical edits in kb/04, 08, 09, 10, 14, 15, 17 (+ gaps/D7 status, gaps/GAP_REGISTER §8). Not 16 (W5-S11). W6-F5 is fixing #2, #8–#13 in parallel.

## Plan (D7 issues)
- [x] #1 15/ground-station-design Ex 3 — station B −8.7 dB, B ≈ 7.5 dB better
- [x] #3 SF during boost at 868/915 MHz — 09/multipath :29, :97; 04/crystals :152; check 15, 20
- [x] #4 + #21 08/antenna-measurement :112, :34 — P.372 Table 3 measured noise
- [x] #5 08/antennas-on-rockets :68; 10/multiple-access :51, :110, :162 — 866–869 MHz E220 band
- [x] #6 17/resonator :166 — h 1.43 mm, W 2.76 mm; check script
- [x] #7 range-acceleration clause: 04/crystals (:47, :152), 10/sync (:47, table, :207 + PLL check at 410 Hz/s), 10/spread (:123), 14/nco (:117), 14/software-demod (:164), 10/weak-signal (:113)
- [x] One-liners: (#11 reverted — owned by W6-F5), #15 (15/modules, 15/band-plans), #16 (09/link-budget-methodology), #18 (04/inductors), #19 (14/sdr-gain-staging), #20 (17/antenna-range)
- [x] #14 (13/emc), #22, #23 (20) — assigned to agent A by D7 §5 item 7 and in no other brief; done
- [x] GAP_REGISTER §8 change log; D7 status column; build_index --check

## Log (append-only)
- 2026-10-13 — read CONVENTIONS, canonical, D7. Log created.
- 2026-10-13 — #1 done (15/ground-station Ex3: −16.2/−8.7 dB, 7.5 dB pattern, −0.8 dB slant range → net 6.7 dB).
- 2026-10-14 — #3 done: re-ran s17_doppler_rate_los.py (868 MHz SF9/125 fails 107/96 Hz vs 81 Hz at 0.5/2 km; passes at 5 km 76 Hz). Edited 09/multipath (TL;DR, post-table, Ex 2 ×2), 04/crystals Ex 4, 15/impairments TL;DR band split. 20 already consistent (SF ≤ 8 @125 both bands — conservative) — not edited (Agent B domain).
- 2026-10-14 — #7 done: caveat + link on 04/crystals (TL;DR, Ex 4), 10/sync (TL;DR, table note, Ex 2 at 410/458 Hz/s: 16.6°/18.5°, BPSK 0.37/0.46 dB, loop holds), 10/spread, 14/nco, 14/software-demod, 10/weak-signal.
- 2026-10-14 — #4/#21 done: 08/antenna-measurement man-made noise → Table 3 measured; G/T swing note (≈ 9–12 dB LNA, 2–3 dB module if man-made enters at horizon; hand estimate).
- 2026-10-14 — #5 done: 08/antennas-on-rockets licence note (866–869 row −6 dB: 34/23 dB; 917–925 1 % duty can't carry 10 Hz); 10/multiple-access :51/:110/:162 channel counts (2–3 in 866–869; 8 in 917–925 checked: CH 67–74).
- 2026-10-14 — #6 done: 17/resonator 1.43 mm core, W 2.76 bare / 2.69 masked; scratch re-run with tline_microstrip: ring 164.7 mm for h 1.51 and 1.43 (εeff 3.3134 vs 3.3124), so e11_permittivity.py not changed; wrong-h inversion +0.49 %. Also fixed the "1.43–1.51 mm depending on how you count" wording.
- 2026-10-14 — one-liners #14, #15, #16, #18, #19 (1.064 dB/m computed; wrote ≈ 1.06), #20, #22, #23 done. #11 edited then reverted (W6-F5's brief owns #8–#13; F5 log lists #11); 09/atmospheric restored incl. last_updated 2026-09-29.
- 2026-10-14 — GAP_REGISTER §8 entry; D7 §2 "Fix status — agent A" table (separate table, not a column, to avoid colliding with W6-F5's D7 edits). build_index.py --check: 288 pages, 0 broken links, 0 control chars, 0 missing sections. Anchor check on the 21 edited pages: 0 broken.

## Contradictions / discrepancies found
- D7 #19 says 1.05 dB/m; log-log between the coax-table points gives 1.064 → wrote ≈ 1.06.
- D7 #1 omitted B's 0.8 dB longer slant range; added (net ≈ 6.7 dB).

## Resume instructions
Work through the plan; each item lists file:line from D7 (search the quoted text if lines drifted). Re-read each file just before editing (W6-F5 edits in parallel); bump last_updated to 2026-10-13.
