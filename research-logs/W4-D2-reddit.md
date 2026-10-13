# Research log W4-D2: Reddit question sweep (gap analysis)
Status: complete
Owner scope: gaps/D2-reddit.md, research-logs/W4-D2-reddit.md (no kb/ edits)

## Plan
- [x] Step 0: read CONVENTIONS, INDEX, D1 summary; create this log
- [x] Phase 1: harvest >= 500 distinct on-topic question posts from Reddit (695 classified; ≈90 000 posts scanned)
      subs: rfelectronics, amateurradio, HamRadio, RTLSDR, sdr, AskElectronics (search), ElectricalEngineering (search),
      PrintedCircuitBoard (search), meshtastic, LoRa, rocketry, HighPowerRocketry, radar, GNURadio, DSP, ECE, antennas
- [x] Phase 2: classify domain + coverage (covered/partial/missing) vs FAQ.md and kb/
- [x] Spot-check covered calls (3 rounds, 26 rows, 5 downgraded); re-check domains that grew (32 rows re-assessed 2026-10-02)
- [x] Write gaps/D2-reddit.md (summary, top-40, misconceptions, learning path, full table)

## Log (append-only)
- 2026-09-29 — read CONVENTIONS.md, HANDOFF.md, INDEX.md (actual kb: 209 files incl _index/_sources), D1 summary + top-40.
  Noted kb/21-gnss/ folder exists (empty so far) — GNSS receiver internals = domain 21.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |

## Contradictions / discrepancies found
## Knowledge gaps noticed (for later gap-filling)
## Cross-domain notes
## Resume instructions
- Raw harvested JSON is in the session scratchpad (lost on crash). Harvested/filtered rows are appended to
  gaps/D2-reddit.md §5 progressively; if interrupted, read that table, continue with subs not yet listed in the log.
- 2026-09-29 — Access test: reddit.com/.json and api.reddit.com return 403 (blocked unauthenticated); old.reddit .json redirects
  to login; reddit RSS (top.rss) works but is rate-limited to ~1 request/min (x-ratelimit headers) and has no score.
  PullPush API refuses agents (429 "no free scraping for agents") — not used. Arctic Shift archive API
  (arctic-shift.photon-reddit.com/api/posts/search) returns raw JSON incl. score + num_comments; scores for old posts
  look current (not frozen at ingestion). DECISION: harvest via Arctic Shift (read-only, 1 req/s), sort by score locally.
  Scripts: scratchpad/reddit/harvest.py (dedicated subs full history; amateurradio 2022+; keyword title searches in
  AskElectronics, PrintedCircuitBoard, ElectricalEngineering, ECE, rocketry, amateurradio pre-2022). Launched in background.
- 2026-09-29 — Arctic Shift full-text title search times out under load ("Timeout. Maybe slow down a bit") -> dropped;
  replaced by Reddit search RSS (sort=top, t=all, 100/query, ~1 req/min per x-ratelimit) for keyword queries in
  AskElectronics, ElectricalEngineering, PrintedCircuitBoard, ECE, rocketry, HighPowerRocketry, amateurradio, meshtastic,
  RTLSDR, rfelectronics (scratchpad/reddit/rss_harvest.py; scores then looked up via Arctic Shift /api/posts/ids).
  Arctic Shift paging is ~500 posts/min, so big subs are flair-filtered: amateurradio QUESTION/ANTENNA/PROPAGATION,
  RTLSDR Troubleshooting/"DIY Projects/questions"/Antennas; meshtastic 2024+ only. Small subs full history.
- 2026-09-29 — Read live "Questions this page answers" of all 190+ kb pages (scratchpad/kbq.txt) for coverage checks.
  New since INDEX build: 11/diy-radar-hardware, 11/sar-and-imaging, 12/adaptive-beamforming-doa, 12/array-calibration,
  12/phase-shifters-ttd-components, 13/grounding-and-return-paths, 14/fpga-for-sdr, 14/gnu-radio-and-software-stack,
  14/sdr-hardware-survey, 14/software-demodulation, 16/* (6 pages), 17/* (11 pages), 18/* (4 pages), 19/* (7 pages).
- 2026-09-29 02:10 — rfelectronics fully harvested (14 054 posts, 7 680 question-like). Classified 250 rows
  (scratchpad/reddit/class_rf.tsv, class_rf2.tsv). gen.py writes gaps/D2-reddit.md (summary + full table) from class_*.tsv;
  hand-written §§2–4 go in scratchpad/reddit/sec_mid.md. First gaps/D2-reddit.md written (250 rows).
  Status codes: C covered / P partial / M missing / O out-of-scope (career). Domains LRN (learning path), CAR (career), 21 (GNSS).
- 2026-09-29 02:15 — Classified r/sdr, r/GNURadio, r/Radar, r/LoRa (class_sdr.tsv), AskElectronics RSS batch 1 (class_ae.tsv): 374 rows.
  r/HighPowerRocketry has only 38 archived posts (no RF questions); r/antennas does not exist in the archive (r/Antenna is tiny).
  Spot-check #1 of 12 "covered" rows: 4 downgraded to partial (t6chs0, jdfk3c FM discriminator circuits only named;
  8ie4nm radiated LO leakage; hvtrrg crystal package pinout). 8 confirmed (Wilkinson, coax Z0, DC-block value, beamwidth
  70λ/D, SA input protection, normal-mode helix, CPWG vs microstrip, PLL reference spurs).
  Started parallel meshtastic 2024+ harvest (mesh.log) and learn_mentions.py (counts resource names in learning-thread comments).
- 2026-09-29 02:30 — Classified HamRadio (class_ham), meshtastic 2024–26 (class_mesh), rocketry RSS (class_rocket),
  rfelectronics past-year extras (class_rf3), RTLSDR flairs (class_rtl), DSP (class_dsp): 568 rows (C 236 / P 231 / M 93 + O).
  clusters.py groups P/M rows into ~33 topic clusters (regex + per-id overrides) and ranks them
  (relevance × [log Σscore + log Σcomments] × (1+0.15n) × (1+0.3·missing share)).
  Learning-thread comment mining (learn_mentions.py, 52 threads / 1 180 comments): Pozar 27 threads, Balanis 16,
  commercial EM tools 13, ARRL Handbook 9, W2AEW 9, ham licence 8, NanoVNA 8, Razavi 8, The Signal Path 7 …
  Still running: amateurradio flair harvest (main job); RSS queue (meshtastic, PCB, ECE, EE, amateurradio, RTLSDR, rfelectronics, AE).

## Resume instructions (exact, written at pause 2026-09-29 ~02:27)
Scratch dir: /private/tmp/claude-501/-Users-marcusquek-Documents-RF-Physics/ba6f154f-f0b8-4b88-bbb5-5e60575969d1/scratchpad/reddit
(if lost, re-harvest with harvest.py / rss_harvest.py — both resumable via .done markers / rss/*.xml).
State: 568 classified rows in class_*.tsv; gaps/D2-reddit.md last generated at 568 rows (summary + full table; §2–4 placeholder).
Drafted: sec_head.md (§0), sec3.md (§3 misconceptions). NOT yet: sec_mid.md (must = §2 + sec3.md + §4).
Background jobs (may have died): `python3 -u harvest.py dedicated >> dedicated.log` (was at amateurradio QUESTION flair 2026;
remaining amateurradio ANTENNA/PROPAGATION flairs); `python3 -u rss_harvest.py >> rss.log` (done through meshtastic/settings;
remaining PCB, ECE, EE, amateurradio, RTLSDR, rfelectronics, AskElectronics extras). Restart both if not running.
Next steps: (1) python3 scores.py; classify amateurradio (flair data + RSS), PCB/ECE/EE/RTLSDR RSS results into new class_*.tsv
(skip ids in done_ids.txt); (2) rerun learn_mentions.py (add ECE/EE/amateurradio learning ids, extra book patterns) → write §4;
(3) MODE=md python3 clusters.py → split big clusters to 40 rows → write sec_mid.md = §2 + sec3.md + §4; (4) re-check domains
11–14,16–18,20,21 pages that landed since (re-extract kbq), spot-check #3; (5) python3 gen.py; set Status complete; final reply.
- (pause note) Both background jobs (harvest.py dedicated, rss_harvest.py) were terminated (exit 143) at pause — restart both on resume; they skip completed work.
- 2026-10-02 — RESUMED by coordinator. Background jobs had been killed; deciding whether to restart.
- 2026-10-02 — Restarted only rss_limited.py (PrintedCircuitBoard 8 + ElectricalEngineering 7 + ECE 5 queries; never searched before; PCB = weakest KB domain). harvest.py NOT restarted: amateurradio QUESTION 2025–26 already on disk is enough.
- 2026-10-02 — Classified amateurradio QUESTION flair 2025–26 (class_ar.tsv, 39 rows) → 607 rows. Re-check of
  still-being-written domains: 23 pages landed since first extraction (08/slot-antennas; 13 connectors-and-launches,
  emc-emi-fundamentals, power-distribution, rf-layout-rules, shielding-and-isolation, vias-stitching-fencing; 16 ×4;
  17 lab-setup, bring-up playbook; 18 ×7; 20 ground-station-tracking-yagi, lora-rocket-telemetry-link; 21-gnss/gnss-signals-and-codes).
  32 rows re-assessed: 13 upgraded to covered, 7 missing→partial, rest notes updated; none downgraded.
- 2026-10-02 — Classified r/PrintedCircuitBoard (36) and r/ElectricalEngineering (34, incl. 6 CAR) RSS results → 677 rows.
  Spot-check #3 (8 covered rows from PCB/EE/amateurradio batches): 7 confirmed, 1 downgraded (67nyjb diff-pair vs 2×50 Ω).
  Cumulative spot-checks: 26 covered rows checked, 5 downgraded (19 %).
  §2 built by clusters.py (43 clusters after splitting learning/antenna/satellite/layout groups; top 40 shown), §3 sec3.md
  (34 myths), §4 sec4.md (learn_mentions over 53 LRN threads / 1 006 comments). assemble.py → sec_mid.md; gen.py → gaps/D2-reddit.md.

- 2026-10-02 03:10 — Classified r/ECE (18 rows) → 695 rows (C 298 / P 290 / M 92 / O 15). Final assembly written.
  No background jobs left running. Task COMPLETE.

## Sources consulted (final)
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| 1 | Arctic Shift Reddit archive API (arctic-shift.photon-reddit.com /api/posts/search, /posts/ids, /comments/search) | data API (raw JSON) | post titles, scores, comment counts; comment text for resource-name counting only | scores current for old posts (checked); very recent posts may lag |
| 2 | Reddit search RSS (www.reddit.com/r/<sub>/search.rss, sort=top) | official feed | keyword top-100 lists for AskElectronics, PCB, EE, ECE, rocketry, HPR, meshtastic | ~1 req/min; no scores (looked up via #1) |
| 3 | kb/ pages (215), FAQ.md, gaps/D1-stackexchange.md | internal | coverage checks; D1 comparison | pages kept landing — re-extracted twice |

## Contradictions / discrepancies found
- None between KB pages found in this sweep. Note D1 marked "always split grounds" and "via fence around chip antenna" as ✗;
  13/grounding-and-return-paths now corrects the first (✅ here), the second is still not stated (◐).

## Knowledge gaps noticed (for later gap-filling) — see gaps/D2-reddit.md §2 (top 40) and §3 (34 myths)
- Largest: RF learning roadmap + book list + videos (NEW 00/rf-learning-roadmap); antenna-ID and signal-ID guides;
  beginner project ladder (20/first-rf-projects); SDR reception recipes (weather sats, ADS-B); SDR spurs/gain staging;
  Meshtastic network operation; judging LoRa antennas; RF immunity/interference hunting; bulk data over sub-GHz.

## Cross-domain notes
- 21-gnss: receiver anatomy/anti-jam/sample generation questions (5 rows) wait on planned 21/ pages.
- 19: add non-ionising paragraph + lightning/station grounding; consumer-band (FRS/PMR, 300–390 MHz remotes) rules.
- 08: other-antenna-types (RFID/NFC, lens, sector, biconical), wire antennas, antenna-ID guide.

## Resume instructions
- Task complete. To regenerate the output from the scratch folder: python3 assemble.py && python3 gen.py
  (class_*.tsv = hand classifications; clusters.py = §2 clustering; sec_head/sec3/sec4.md = hand-written sections).
