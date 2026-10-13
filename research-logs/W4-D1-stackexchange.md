# Research log W4-D1: Stack Exchange gap analysis
Status: complete (2026-09-29)
Owner scope: gaps/D1-stackexchange.md ; this log (no kb/ edits)

## Plan
- [ ] Step 0: read CONVENTIONS.md, INDEX.md, FAQ.md structure; create log (done 2026-09-27)
- [ ] Phase 1 harvest (target >= 400 distinct questions) via Stack Exchange API 2.3 using curl
      (raw JSON, exact titles — avoids the WebFetch-summary problem of CONVENTIONS rule 8).
      Raw JSON cached in scratchpad `se/` ; parsed rows appended to gaps/D1-stackexchange.md.
      Sites/tags: electronics (rf, antenna, impedance-matching, transmission-line, radio, lora, sdr,
      rf-amplifier, noise, oscillator, pll, rf-filter, pcb-design+rf, emi/emc, radar, smith-chart,
      vna/network-analyzer, spectrum-analyzer, mixer, balun, coaxial, gps, wireless, modulation,
      adc+rf/sampling, op-amp+noise/stability, crystal); ham (top votes overall + antenna,
      propagation, swr, feedline, licensing); dsp (radar, sdr, fft, modulation, beamforming, doa).
      Sort orders: votes and (where budget allows) activity/hot; views via view_count field.
- [ ] Phase 2 classify each question (domain 00–20) and check coverage by grep of FAQ.md + kb/,
      opening candidate sections when unsure. Status covered/partial/missing.
- [ ] Output: summary counts, top-40 ranked missing/partial clusters, misconceptions list,
      full table.
- [ ] Re-check still-being-written domains (06, 11, 12, 13, 14, 16, 17, 18, 19, 20) at end.

## Log (append-only)
- 2026-09-27 — Step 0 done. Read CONVENTIONS (§4 no copyright; rule 8 WebFetch summaries). INDEX
  lists 128 pages; on disk extra pages now exist in 03 (signal-flow-graphs-mason), 06 (mixers,
  rf-switches-attenuators-limiters), 11 (radar-range-equation), 12 (beam-steering-grating-lobes),
  14 (fft-spectral-analysis-windows), 17 (vna-fundamentals-calibration), 19 (singapore-imda-rules).
  13, 16, 18, 20 folders empty at start.
- 2026-09-27 — curl to api.stackexchange.com works from Bash (gzip JSON) → exact titles/scores/views;
  no WebFetch summarisation needed for harvest. Anonymous quota 300 req/day — budget ~60 calls.

## Resume instructions
(updated 2026-09-29, final) TASK COMPLETE. gaps/D1-stackexchange.md holds §0 method, §1 summary, §2 ranked
top-40 clusters, §3 misconceptions, §4 full 686-row table. If a later agent wants to refresh it against a
grown KB: re-check only rows with status partial/missing whose target page is marked "planned" in §2, and
update §1 counts. Scratchpad working files (cls5.txt, clusters.txt, gen_table.py, cluster_texts.json) are
session-local and may be gone; the gaps file is authoritative.

## Harvest progress
| batch | site | tag / sort | rows kept | cumulative |
|---|---|---|---|---|
| 1 | electronics | 48 tag queries (votes; rf/antenna also hot) | 3549 distinct raw | |
| 2 | ham | ALL votes p1-3 + 17 tags + hot | 1560 distinct raw | |
| 3 | dsp | 21 tags votes | 1683 distinct raw | 6792 distinct raw total |
| sel | all | top-N per tag (N 4–80 by relevance) → 886; manual off-topic exclusion (power-grid lines, audio mixers/amps, USB/HDMI digital, ham operating etiquette, audio DSP) → 686 kept | 686 | 686 |

- 2026-09-27 — Harvest done via curl+SE API (quota 300→184). Raw JSON in scratchpad/se/q_*.json,
  combined all.json, selection sel.json, exclusions exclude.txt, kept keep.json (686). Wrote the 686
  rows (status TBD) to gaps/D1-stackexchange.md so the harvest survives a crash. Next: read FAQ.md
  fully + new pages' question lists, then classify in batches of ~50–100 rows.
- 2026-09-27 — First-pass classification of all 686 rows done (scratchpad/se/cls.txt: row|domain|status|page|note),
  checking FAQ.md + live page question lists (livefaq.sh) + targeted grep of kb/. KB grew during the pass
  (new: 06 receiver-architectures, vco-and-pll; 11 cw-and-doppler, ambiguity-function, pulsed, RCS; 12
  planar, tapering, beamforming-architectures; 14 multirate, nco-ddc, digital-filters; 17 SA, nanovna;
  18 rf-transceiver-ics; 19 amateur). Next: re-check partial/missing rows in growing domains, then write output.
- 2026-09-29 — Resumed after usage-limit reset. Scratchpad intact. Saved first-pass classification to
  gaps/D1-stackexchange.md (686 rows, 370 covered / 213 partial / 103 missing before re-check). KB now 160
  pages; FAQ.md rebuilt. Starting re-check of growing domains.
- 2026-09-29 — Re-check done (41 rows updated from new pages: 06 receiver-arch/multipliers, 11 fmcw/cw/ambiguity, 12 beamforming-arch, 13 stackups, 14 nco-ddc, 17 SA/power); spot-check of 10 'covered' rows downgraded 4 (penetration-vs-frequency, carrier-vs-data-rate). Final: 397 covered / 197 partial / 92 missing. Table saved to gaps file.
- 2026-09-29 — Late re-check against 14 more new pages (KB 173 pages): 19 rows upgraded (clutter-and-mti,
  mimo-radar, software-demodulation, spice, openems, oscilloscopes, phase-noise-measurement, certification,
  lab-safety). Re-ranked clusters. Final: 411 covered / 188 partial / 87 missing. Wrote §0–§3 + table.
  Top gaps: PCB grounding/pours (13), adaptive beamforming/DOA (12), RF layout/launches (13), GNSS receiver
  operation (NEW, unplanned), spectrum allocation/certification (19), bench test practice (17), EMC (13),
  missing antenna types (NEW), via stitching (13), shielding (13).

## Knowledge gaps noticed (for the orchestrator)
- Not in any INDEX plan: GNSS receiver operation (TTFF/A-GNSS/1 PPS/update rate); wireless power & RF
  harvesting; other antenna types (slot/lens/random-wire/fan/OCF/RFID coils); superregenerative receivers;
  beginner first-RF-projects recipe; PLL vs DLL; diplexers/duplexers; iron-powder cores; SA/lab trivia.
- Myths not corrected anywhere: higher-f penetrates better; zeroing FFT bins as a filter; RC after LNA;
  element metal changes length; chirp phase factor-of-2; split ground planes; via fences around antennas;
  GNSS receivers transmit.
