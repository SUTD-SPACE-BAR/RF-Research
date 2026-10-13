# Research log W4-D3: forums (EEVblog, QRZ, eHam, groups.io, RadioReference, Hackaday, Meshtastic, TTN) + YouTube
Status: complete (2026-10-02)
Owner scope: gaps/D3-forums-youtube.md, research-logs/W4-D3-forums-youtube.md (no kb/ edits)

## Plan
- [x] Step 0: read CONVENTIONS (§4 no copyright, rule 8 WebFetch = summaries), HANDOFF, INDEX, D1 summary/top-40/misconceptions
- [ ] Phase 1 harvest (target >= 400 distinct on-topic questions), in this order, writing rows to
      gaps/D3-forums-youtube.md §5 incrementally (raw harvest files in scratchpad/harvest/*.tsv):
  - [ ] EEVblog forum: RF/Microwave/Ham board + Test Equipment board (curl board index pages if reachable; else WebSearch site:)
  - [ ] groups.io topic titles: nanovna-users, LibreVNA, tinysa (curl topics pages / RSS)
  - [ ] QRZ forums (antennas/feedlines), eHam, RadioReference (scanners/antennas), SOTA reflector, APRS
  - [ ] Hackaday posts (RF/SDR/LoRa/radar) — recurring comment objections
  - [ ] Meshtastic discourse / GitHub discussions; TTN forum (Discourse JSON: /top.json, /search.json)
  - [ ] YouTube: channel video lists via RSS feeds (channel_id) / WebSearch for titles; W2AEW, R&S, Keysight, Tek,
        Andreas Spiess, Tech Minds, Phil's Lab, Robert Feranec, The Signal Path, Mr Carlson's Lab, AllAboutCircuits
- [ ] Phase 2 classify domain + coverage vs FAQ.md / kb (grep), spot-check covered, re-check in-progress domains
- [ ] Write gaps/D3-forums-youtube.md (summary, top-40, misconceptions, explainer-quality notes, full table)

## Log (append-only)
- 2026-09-29 — Step 0 done. KB at ~195 pages (INDEX). Unwritten: most of 13 (only stackups, grounding), 16 (tool-landscape,
  harmonic-balance, simulation-validation), 17 (lab-setup-by-budget, rf-bring-up-debug-playbook), 18 (connectors, substrates,
  adcs, array parts, sourcing, rf-modules), 20 (all), 21 (all), 08 (slot, wire-hf, rfid/nfc/wpt planned).
  D1 top-40 read (PCB grounding, DOA, RF layout, GNSS ops, spectrum alloc, bench practice, EMC, other antennas, via stitching,
  shielding, superregen, SDR hw, ...). D2 in progress (Reddit via Arctic Shift).

## Sources consulted
| # | Source | Type | Used for | Reliability notes |

## Contradictions / discrepancies found
## Knowledge gaps noticed (for later gap-filling)
## Cross-domain notes
## Resume instructions
- Harvested rows are appended to gaps/D3-forums-youtube.md §5 (full table) per source as they are classified.
  Raw harvest (titles/URLs) in scratchpad is lost on crash; if interrupted, read §5 and this log, continue with sources
  not yet marked [x] in the plan, then do Phase 2 summary sections.
- 2026-09-29 — Access tests: EEVblog forum, QRZ forums = Cloudflare 403 to curl (use WebSearch site: titles);
  groups.io topic pages need JS (RSS only = latest 20 msgs → use WebSearch site:groups.io); RadioReference 405;
  eHam forums moved (404). Working raw sources: TTN forum + SOTA reflector + Arduino forum (Discourse search.json),
  Meshtastic GitHub Discussions (gh api graphql, read-only), Hackaday RSS (tag/category feeds, slash:comments count)
  + post HTML comments, YouTube channel pages (ytInitialData, "Popular" chip continuation via youtubei/v1/browse)
  and YouTube search result pages (ytInitialData, exact titles + view counts).
- 2026-09-29 — Raw harvest (scratchpad/harvest): ttn.tsv 995 topics (36 queries), sota.tsv 1088 (33 q), arduino.tsv 1351
  (23 q), mesh_gh.tsv 299 discussions (22 q), hackaday.tsv 304 posts (18 feeds) + hd_comments.txt (30 posts' comments),
  yt_channels.tsv 967 popular videos (W2AEW, Keysight, KeysightLabs, Tektronix, Andreas Spiess, Tech Minds, Phil's Lab,
  Robert Feranec, The Signal Path, Mr Carlson's Lab, HB9BLA (exists: 32 videos), IMSAI Guy, Ham Radio Crash Course,
  KB9VBR, Fesz, EEVblog, R&S (@rohde-schwarz), All About Circuits (@allaboutcircuitsvideo)), yt_search.tsv 969 results
  (54 topic searches). Next: WebSearch for EEVblog/QRZ/eHam/groups.io/RadioReference titles.
- 2026-09-29 — WebSearch harvest (titles are exact search-result page titles): EEVblog RF board + Test Equipment (~110),
  groups.io nanovna-users/tinysa/LibreVNA (~55), RadioReference (~20), eHam articles (~12), QRZ (~8: QRZ is poorly
  indexed by the search engine; `site:forums.qrz.com` returns ~1 hit per query) → scratchpad/harvest/ws.tsv (228 rows).
  Wayback: EEVblog board index snapshots only for 2021-01, 2022-01, 2023-12 (testgear), 2026-08 → wb_eev.tsv (119 incl. counts).
  Hackaday comments on 30 posts read (hd_filt.txt) for objections/misconceptions.
- 2026-09-29 — YouTube: popular lists per channel parsed (see yt_channels.tsv); topic searches (yt_search.tsv) ranked;
  top-40 comments fetched for 20 flagship explainers → scratchpad/harvest/yt_comments.txt (110 KB, NOT yet read).
  PAUSED here on coordinator request. No rows written to gaps/D3-forums-youtube.md yet (file does not exist).

## Resume instructions (exact, as of pause)
Scratchpad (session): /private/tmp/claude-501/-Users-marcusquek-Documents-RF-Physics/ba6f154f-f0b8-4b88-bbb5-5e60575969d1/scratchpad/harvest/
Raw files there: ttn.tsv, sota.tsv, arduino.tsv, mesh_gh.tsv, hackaday.tsv, hd_comments.txt, hd_filt.txt (read),
yt_channels.tsv, yt_search.tsv, yt_comments.txt (unread), ws.tsv (228 WebSearch titles: EEVblog/groups.io/RR/eHam/QRZ),
wb_eev.tsv (Wayback EEVblog). Scripts: discourse.py, ghdisc.py, hackaday.py, hdcomments.py, yt.py, ytsearch.py, ytcomments.py.
If the scratchpad is gone, re-run the scripts (commands are in this log; each takes 1–5 min) — WebSearch rows must be redone.
Next steps:
 1. Skim yt_comments.txt (filter for '?', 'finally', 'understand', 'wrong') for viewer questions + praise (§3/§4).
 2. Select ~450 on-topic rows: TTN ~60 (RF keyword filter, sort by posts), SOTA ~35, Arduino ~45, Meshtastic ~12,
    Hackaday ~45 (posts + comment objections), YouTube ~90 (channel + search titles), ws.tsv ~200, wb_eev ~30.
 3. Classify each (domain 00–21/NEW; covered/partial/missing vs FAQ.md + grep kb/), write gaps/D3-forums-youtube.md
    §5 table INCREMENTALLY (per source), then §1 summary, §2 top-40 (note D1 overlap), §3 misconceptions, §4 explainers.
 4. Spot-check 10 covered rows; re-check domains 11,12,13,16,17,18,20,21 at end; set Status complete; final ≤250-word reply.
- 2026-10-02 — Resumed. Read yt_comments.txt (top comments are mostly praise; few questions). Built scratchpad/harvest/build.py
  (resolves URL/popularity from raw TSVs, appends rows to gaps/D3 §5) + kbg.py (regex coverage grep over kb/).
  Appended rows 1–268 (EEVblog WebSearch 130; groups.io/RadioReference/eHam/QRZ/other + Wayback EEVblog 138).
  Noted new pages landing during run: 13/mixed-signal-layout, 13/jlcpcb-rf-manufacturing, 13/power-distribution-decoupling-for-rf,
  14/signal-identification-and-spectrum-survey, 20/bandpass-filter-design-walkthrough, 21/gnss-signals-and-codes,
  21/gnss-receiver-architecture-acquisition-tracking → re-check rows in 13/14/20/21 at the end.
  Next: TTN, SOTA, Arduino, Meshtastic, Hackaday (+comments), YouTube rows; then §1–§4.
- 2026-10-02 — Rows 269–699 appended: TTN 69, SOTA 47 + Arduino 56 + Meshtastic 13, Hackaday 55 posts + 34 comment-derived,
  YouTube 157 (channel popular lists + topic-search explainers). Wave-5 pages that landed during the run and were used:
  08/inductive-coupling-rfid-nfc-wpt, 13/rf-pcb-review-checklist, 13/thermal-management-rf, 13/mixed-signal-layout,
  13/jlcpcb-rf-manufacturing, 14/signal-identification-and-spectrum-survey, 20/patch-antenna-design-walkthrough,
  21/{gnss-signals-and-codes, gnss-receiver-architecture-acquisition-tracking, gnss-receiver-integration-u-blox,
  rtk-ppp-and-corrections, gnss-interference-jamming-spoofing, gnss-on-rockets-dynamics-and-limits}.
  Next: re-check early rows (1–453) against those new pages; spot-check covered; dedupe check; write §1–§4.
- 2026-10-02 — Re-checked rows against pages landed during run (08/inductive-coupling, 14/sdr-front-end-protection-and-filtering,
  13/rf-pcb-review-checklist, 21/*): 13 rows updated via scratchpad/harvest/upd.py + u1.json. Spot-check of 16 covered rows:
  2 downgraded (wideband LNA #56, MeshCore #458), 2 partial→covered (underwater #308-ish, HC-12 underwater). Fixed mis-resolved
  LibreVNA row #179 URL. Table now 699 rows (664 distinct URLs; Hackaday comment rows share post URLs):
  465 covered / 176 partial / 58 missing. Clusters + scores computed (scratchpad/harvest/clusters.py, clusters.json).
  PAUSED on user request (second pause).

## Resume instructions (exact, as of second pause)
- gaps/D3-forums-youtube.md: header + §5 full table (rows 1–699) are COMPLETE and re-checked. Do NOT re-append rows.
  The file's top still says "Status: in progress"; §1–§4 are NOT written yet.
- Scratchpad: /private/tmp/claude-501/-Users-marcusquek-Documents-RF-Physics/ba6f154f-f0b8-4b88-bbb5-5e60575969d1/scratchpad/harvest/
  (backup copy: research-logs/raw-harvest/d3-forums-youtube). Run `python3 clusters.py` there to print cluster ranking.
  Before writing §2, fix clusters.py: row 231 is in both C5 and C19 (keep it in C19 only); rows 239 (paint/RF), 350 (WSPR
  antenna comparison) and 412 (rotating-assembly diversity) are unclustered — put 239 in C29, 350 in C15c, 412 in C28b.
- Next steps: (1) write §1 Summary (counts by status/source/domain — numbers printed by the stats snippet in this log's step:
  covered 465, partial 176, missing 58; per-source and per-domain tables can be re-computed from the table with a short script);
  (2) §2 top-40 ranked clusters (C1 tuners top; note D1 overlaps: C1↔D1#40, C2/C3↔D1#8, C5/C6/C7↔D1#7/#29/#5, C8↔D1#39,
  C13↔D1#5, C14↔D1#11, C15c/C16↔D1#6, C17↔D1#20/#34, C24↔D1#37, C30↔D1#15, C31↔D1#38, C35↔D1#10, C42↔D1#19; D2 file
  check: gaps/D2-reddit.md if present); (3) §3 misconceptions table (SWR/reflected power, tuner-fixes-antenna, coax CM,
  NanoVNA 73 Ω cal, adapter-after-cal, high-gain gateway omni, LoRa range claims, LNA always helps, SDR ADC/bit myths,
  discone gain, EH/CFA antennas, Ethernet ferrites, 2:1 SWR kills PA); (4) §4 explainer-quality list from yt_search/yt_comments
  (Veritasium/Zach Star Smith chart, w2aew IQ #170, BetaPhoenix impedance matching, Ask Dave 50 Ω, Euge transmission lines,
  R&S Understanding series, Andreas Spiess LoRa #112, Visual Electric LoRa chirps, Marshall Bruner radar, Hans Rosenberg PCB,
  Rick Hartley grounding, IZ2UUF balun, Jon Kraft phaser); (5) set file Status complete, log Status complete, ≤250-word reply.
- 2026-10-02 — Resumed (third session). Second coverage re-check against pages landed since the pause:
  08/wire-antennas-hf-random-wire-fan-dipole, 21/gnss-timing-1pps, 21/ttff-agps-almanac-ephemeris, 21/gnss-error-sources-dop,
  20/lna-design-walkthrough, 20/gnss-front-end-design → 36 more rows updated (33 upgrades; tuner myth, random wire/unun,
  OCF, traps, verticals/radials, timing GPS, active-antenna supervisor). Cluster fixes applied (231→C19 only; 239→C29,
  350→C15c, 412→C28b); covered rows auto-dropped from clusters. Wrote §0 method, §1 summary, §2 top-40 (47 clusters,
  D1/D2 overlaps), §3 misconceptions (32: 19 ✅ / 11 ◐ / 2 ✗), §4 explainer notes (17 entries). File status set complete.
  Final numbers: 699 questions (664 distinct threads/videos), 484 covered / 179 partial / 36 missing.

## Resume instructions
- Task complete. Nothing pending. If the orchestrator wants a refresh after more Wave-5 pages land, re-run the
  coverage greps (scratchpad harvest/kbg.py) on §2 clusters ranks 1–20 and update rows with harvest/upd.py.
