# W5-S17 index to-do (lines for files owned by still-running slices)

Written by W5-S17 on 2026-10-13. These are the index lines that are needed but that W5-S17 did not write, because the files belong to slices that are still running. Whoever owns the file (or the orchestrator, once the slice finishes) should apply them and then delete the line here.

Scan method: every `kb/*/*.md` page except `_index`/`_sources` was checked for its slug in `tools/taxonomy.md` and for its file name in its domain `_index.md`. On 2026-10-13 ~18:40, only two pages were missing anything.

## 10-comms-modulation (owned by W5-S8, running)
- `tools/taxonomy.md`, under `## 10-comms-modulation`: append ` · weak-signal-digital-modes` to the last line (`… multiple-access-and-duplexing · mimo-capacity-and-channel-estimation`). W5-S8's scope lists "slug in tools/taxonomy.md", so S17 left this line for S8 to avoid a duplicate.
- `kb/10-comms-modulation/_index.md`, Pages table: add a row for `[weak-signal-digital-modes](weak-signal-digital-modes.md)` (FT8/FT4/WSPR/JT65/JT9/Q65/FST4, PSK31, RTTY, APRS, DMR/D-STAR; SNR in 2.5 kHz → Eb/N0; comparison with LoRa SF12 and Shannon). Also add it to the reading order. Level and confidence come from the page front matter.

## 21-gnss (owned by W5-S13, running)
- `kb/21-gnss/gnss-receiver-integration-u-blox.md` was already in `21/_index.md` but missing from `tools/taxonomy.md`. **Done by S17** (taxonomy only; it is not an _index edit).

## Cross-links the running slices may want (not index lines)
- 06/oscillator-phase-noise-ltv-isf.md:239 (W5-S14/S15 domain) still lists "07 Leeson example quotes −164 while FkT/2Ps gives −167" as open. W5-S17 rechecked it (`tools/verify/s17_leeson_check.py`). The 07 numbers were right: −164 dBc/Hz is L(10 MHz) = −163.6 dBc/Hz, 10 MHz sits inside the 10.8 MHz corner, and the floor is −167 dBc/Hz as stated. The 07 wording was clarified, so the 06 line can be removed.
- 16/nec-antenna-modelling.md (W5-S11): S17 added three PyNEC traps (TL;DR trap bullet and Common mistakes; `s17_pynec_quirks.py`). S11 should re-read the page before its G-16-04 edits.
- 19/_index.md (W5-S16, now complete): no new 19 page; `rf-exposure-safety` gained a "Rule details" subsection (G-19-04). An FAQ line could point to it: *Why are exposure limits strictest at 30–300 MHz / am I exempt on HF?* → `rf-exposure-safety.md#rule-details--body-resonance-several-transmitters-who-is-responsible-hf-exemptions`.
- 08/_index.md, 14/_index.md, 15/_index.md: optional FAQ links to the new `09/satellite-links-doppler-tracking.md` (CubeSat/TinyGS Doppler, Meteor-M G/T, Gpredict/hamlib). S17 added the 15/_index FAQ lines (15 is not owned by a running slice); 08 and 14 are left to their owners.

## Status update (W5-S18b, 2026-10-13)
- 10-comms-modulation lines: already done by W5-S8 (taxonomy slug, _index row, reading order, FAQ, script row) — nothing left.
- 06/oscillator-phase-noise-ltv-isf Leeson open-issue line: **done** (replaced by the S17 resolution note).
- 16/nec-antenna-modelling note for S11: **still open** (16 owned by W5-S11).
- 19/_index FAQ line for rf-exposure "Rule details": **done**. 08/_index and 14/_index FAQ links to 09/satellite-links-doppler-tracking: **done**.
