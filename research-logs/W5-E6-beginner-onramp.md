# Research log W5-E6: beginner on-ramp (00 / 14 / 15 / 19 / 20 new pages)
Status: complete
Owner scope: NEW files only — kb/00-math-foundations/rf-learning-roadmap.md,
kb/00-math-foundations/rf-concepts-for-beginners.md, kb/20-projects-recipes/beginner-project-ladder.md,
kb/14-sdr-dsp/sdr-gain-staging-and-reception-recipes.md, kb/15-lora-ism-radios/choosing-and-judging-lora-antennas.md;
surgical edits: kb/19-regulations-safety/rf-exposure-safety.md (new "RF is non-ionising" section), 15 range/link-budget
pages ("Common mistakes": Meshtastic MQTT-bridged "range records" are not RF range); _index.md + _sources.md of
00, 14, 15, 19 (NOT 20's _index); tools/taxonomy.md slugs (00, 14, 15, 19 lines; add `beginner-project-ladder` to 20).
Do not edit other 14 or 20 files (other agents own them). Scripts: tools/verify/e6_*.py.

## Plan
- [x] Step 0 reading — CONVENTIONS.md (done), HANDOFF.md (done), math-roadmap-for-rf.md (done),
      gaps/D2-reddit.md §0–§4 (done, lines 1–302). Still to read: INDEX.md; D1-stackexchange.md beginner/learning rows
      (grep "LRN\|beginner\|learn\|book"); D5-exams-interviews.md beginner rows; D4-curriculum.md "Level 1" finding;
      the 00/14/15/19 _index.md and _sources.md; tools/taxonomy.md; 17/lab-setup-by-budget, 16/tool-landscape-overview,
      14/sdr-hardware-survey, 17/sdr-as-test-equipment, 15/lora-sensitivity-and-link-budget, 15/lorawan-vs-raw-lora,
      08/antenna-fundamentals, 08/antenna-measurement, 19/rf-exposure-safety, 20/_index (read only).
- [x] e6 verify scripts DONE: e6_beginner_numbers.py (43/43), e6_gain_staging.py (27/27), e6_lora_antennas.py (20/20); was: tools/verify/e6_beginner_numbers.py — photon energy vs ionisation (E = h f, eV at 433 MHz /
      2.4 GHz / 77 GHz vs ~10–12 eV; 13.6 eV H), wavelengths, dB examples, dipole lengths at 433 MHz, cable loss /
      velocity-factor measurement maths, HB100 Doppler (10.525 GHz: 31.4 Hz per km/h... verify), elevation-pattern
      numbers for high-gain omni vs rocket overhead.
- [x] kb/00-math-foundations/rf-learning-roadmap.md (DONE, written 2026-10-02) — stages zero→grad; books by audience (Pozar, Balanis, ARRL Handbook
      & Antenna Book, EMRFD, AoE, Bowick, Razavi, Lee, Skolnik, Richards, Mailloux, Lyons, PySDR: level, prereqs,
      strengths, read-first); free courses (MIT OCW etc.); video channels (names/topics only); first instruments
      (NanoVNA, tinySA, RTL-SDR); "build something early"; KB reading order linking every domain _index.md; complements
      math-roadmap-for-rf (link, don't duplicate). Use D2 §4 consensus counts as "community consensus (n threads)".
- [x] kb/00-math-foundations/rf-concepts-for-beginners.md (DONE, 467 lines) — true Level-1, high-school maths: what RF is; f, λ, c; dB;
      impedance & why 50 Ω; what an antenna does; bandwidth and noise; why higher f doesn't "penetrate better";
      RF is non-ionising (photon energy worked numbers). Each section ends "go deeper →".
- [x] kb/20-projects-recipes/beginner-project-ladder.md (DONE 2026-10-03, 11 rungs) — 8–12 graded projects (RTL-SDR FM/ADS-B; NOAA APT/Meteor LRPT
      with V-dipole/QFH; 433 MHz dipole + NanoVNA; cable loss & velocity factor; tinySA on a LoRa TX; LoRa P2P range
      test; HB100 Doppler radar; 2.4 GHz patch on JLC FR-4; KrakenSDR / two-SDR DOA) each: goal, kit+cost, steps,
      learn, KB links, measure.
- [x] kb/14-sdr-dsp/sdr-gain-staging-and-reception-recipes.md (DONE 2026-10-03) — LNA/mixer/VGA gain, AGC, overload signs, phantom
      signals (tuner LO harmonics, images), bias-tee LNAs, dynamic-range demo; recipes ADS-B, AIS, APRS, NOAA/Meteor,
      ISS, LoRa monitoring (gr-lora_sdr), rtl_433. Link (don't duplicate) signal-identification-and-spectrum-survey.md
      and sdr-front-end-protection-and-filtering.md (owned by W5-E3).
- [x] kb/15-lora-ism-radios/choosing-and-judging-lora-antennas.md (DONE 2026-10-03) — gain vs pattern; fake gain claims, NanoVNA S11 and
      comparative RSSI testing; ground plane, connectors (SMA vs RP-SMA), cable loss, mounting; rocket airframe and
      ground-station choices → links to 08.
- [x] Surgical "Common mistakes" addition in 15 range/link-budget page(s) (DONE: lora-sensitivity-and-link-budget + lorawan-vs-raw-lora): MQTT/internet-bridged Meshtastic "records".
- [x] Surgical edit 19/rf-exposure-safety.md (DONE): "RF is non-ionising" section with photon-energy numbers.
- [x] Update _index.md + _sources.md of 00, 14, 15, 19 (+ refreshed the ladder row in 20/_index); tools/taxonomy.md; build_index --check run (no broken links from W5-E6 pages; 0 pages missing sections).
- [x] Final report via SubagentHandback (≤250 words).

## Log (append-only)
- 2026-10-02 — Started. Read CONVENTIONS.md, HANDOFF.md, kb/00-math-foundations/math-roadmap-for-rf.md,
  gaps/D2-reddit.md lines 1–302 (§0 method, §1 summary, §2 top-40, §3 misconceptions, §4 learning paths).
  Key inputs captured from D2: top gaps #1 roadmap (29 posts), #2 books (19), #5 project ladder (10), #6 SDR recipes
  (19), #8 LoRa antennas (9), #9 beginner explainers (16), #11 SDR spurs/gain staging (10), #17 videos (8), #20 DSP
  path (7). D2 §4a book thread counts (of 53 LRN threads): Pozar 25, Balanis 15, Stutzman&Thiele 5, Kraus 4, ARRL
  Antenna Book 2, ARRL Handbook 10, Bowick 5, EMRFD 4, AoE 3, Razavi 7, Lee CMOS 1, Gonzalez 4, Lee Planar 3,
  Collin 5, Steer 3, Griffiths 3, Ulaby 2, Orfanidis 3, Skolnik 3, Richards 3, Lyons 5, Smith DSP Guide 4,
  Proakis 3, PySDR 3. §4b videos: W2AEW 9, The Signal Path 7, R&S 5 + Keysight 4, Microwaves101 5, MIT/Stanford/
  Berkeley/NPTEL 4+3. §4c tools: NanoVNA 9, RTL-SDR 4, tinySA 4, HackRF 3, Pluto 2; ham licence suggested 8.
  §4d: build-and-measure early (16 threads); read Pozar with a goal; sim not substitute; entry points per background.
  §3 myths to fix: MQTT "range records" (✗, 3a); higher-dBi omni (✅ in 08 already, add elevation picture);
  stock antennas mistuned (◐); more SDR gain always better (✗); phantom stations at wrong frequency e.g. FM ×4
  ≈ 410 MHz (◐); wavy NOAA images = sample-clock/ppm/Doppler (✗); RF dangerous like ionising (◐ — no page
  contains "ionising"); must master Pozar first (◐).
- 2026-10-02 — PAUSE received from coordinator during Step 0. No pages written yet; no background jobs started.

- 2026-10-02 — WROTE kb/00-math-foundations/rf-learning-roadmap.md (stages table, books-by-audience table with
  D4-fetched chapter numbers, Pozar chapter→KB map, specialist tracks, self-check questions, all 22 domain _index
  links, free courses (MIT OCW URLs checked 200), video channels, first instruments). Then PAUSE received; Status →
  paused; no background jobs were started.

- 2026-10-03 — RESUMED (coordinator). Domain 20 complete; allowed to add my page to 20/_index.md if not listed.

- 2026-10-03 — Added §11 (two-ray range-test prediction: breakpoint 13 m, 3.3 km at 10 mW e.r.p. SF9 with 10 dB fade
  margin; 6.6 km with a 6 m mast) to e6_beginner_numbers.py (now 43/43 PASS).
- 2026-10-03 — WROTE kb/20-projects-recipes/beginner-project-ladder.md (11 rungs; W3-C6 had already listed it in
  20/_index.md — will refresh that row only). NOAA APT ended 2025 → Meteor-M LRPT rung.

- 2026-10-03 — Added §5 to e6_gain_staging.py (masthead-LNA SNR benefit vs ITU-R P.372 environment: Meteor city 0.2,
  residential 0.6, rural 1.7, galactic-only 3.9 dB; ADS-B 1090 MHz 14.2 dB) → 27/27 PASS.
- 2026-10-03 — WROTE kb/14-sdr-dsp/sdr-gain-staging-and-reception-recipes.md (window/floor-lift rule, librtlsdr table,
  Monte-Carlo A/B, LNA benefit table, 5 worked examples, 7 recipes, bias-tee notes; links front-end + signal-ID pages
  instead of repeating them).

- 2026-10-03 — WROTE kb/15-lora-ism-radios/choosing-and-judging-lora-antennas.md (gain-vs-elevation table, size test for gain claims, mismatch, A/B statistics, connectors, mounting, airframe and ground-station choices).

- 2026-10-03 — EDITED 15/lora-sensitivity-and-link-budget.md (Common-mistakes bullet on MQTT-bridged Meshtastic
  "records", source [13] protobufs+MQTT docs; linked 09/fresnel for ducting because 09/vhf-uhf-anomalous-propagation
  is planned but not yet written) and 15/lorawan-vs-raw-lora.md (short pointer bullet; last_updated → 2026-10-03).
- 2026-10-03 — EDITED 19/rf-exposure-safety.md: new subsection "RF is non-ionising — photon energy vs the ionisation
  threshold" (photon table, one-photon argument, heating, eye/testes caveat flagged as not re-read), TL;DR bullet,
  2 new Questions, Common-mistakes bullet, source [5] Tschurlovits 1997; last_updated → 2026-10-03.

- 2026-10-03 — Index/taxonomy pass: 00/_index (reading order 0a/0b, 2 rows, 4 FAQ), 00/_sources (E1–E13), 14/_index
  (reading-order 0, row, script row, 3 FAQ), 14/_sources, 15/_index (item 11, row, script mention, 3 FAQ), 15/_sources,
  19/_index (row, FAQ, refs), 19/_sources, 20/_index (row refreshed; W3-C6 had listed the page), tools/taxonomy.md
  (00: rf-concepts-for-beginners, rf-learning-roadmap; 14: sdr-gain-staging-and-reception-recipes; 15: choosing-and-
  judging-lora-antennas; 20: beginner-project-ladder). `python3 tools/build_index.py --check`: 259 pages, 2278
  questions; 11 broken links, none from W5-E6 pages (all point to other agents' planned pages); 0 pages missing
  template sections. Cross-linked the new (other agent's) 15/lora-mesh-capacity-and-congestion.md, which makes the
  same MQTT point — consistent.
- 2026-10-03 — Status → complete.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| 1 | gaps/D2-reddit.md §2–§4 | internal gap analysis | gap list, community-consensus counts | counts are regex rankings, not exact |
| 2 | gaps/D4-curriculum.md §3–§4 | internal | fetched book ToCs (read-first chapters), Level-1 finding | ToCs fetched by W4-D4 |
| 3 | osmocom rtl-sdr source (tuner_r82xx.c, librtlsdr.c) | software source | gain table, VGA, AGC | primary; read directly |
| 4 | meshtastic/protobufs mesh.proto, config.proto | software source | via_mqtt, ignore_mqtt | primary; read directly |
| 5 | Meshtastic docs (MQTT, antenna selection, antenna testing, getting started) | project docs | MQTT bridging, VSWR<2, SMA/RP-SMA, no-antenna warning | WebFetch summaries (rule 8: cross-checked against protobufs where it mattered) |
| 6 | Tschurlovits 1997 IAEA-CN-67/153 | conference paper | ionising thresholds/definitions | read via pdftotext |
| 7 | NOAA OSPO/NESDIS notices | operator notices | NOAA-15/18/19 decommissioning dates | search summaries, two notices agree |
| 8 | usradioguy Meteor page; sigidwiki LRPT; rtl-sdr.com V-dipole & M2-3 articles | community | Meteor 137.9 MHz 72k QPSK 120 kHz; V-dipole | two independent community sources agree |
| 9 | AMSAT / ARISS | amateur orgs | ISS frequencies | two sources agree |
| 10 | aprs.world, hamradio.my | community | APRS 144.390 MHz SG/MY | anecdotal; matches W5-E3 catalogue |
| 11 | gr-lora_sdr README; rtl_433 README | software docs | SF range; protocols/defaults | read directly via curl |
| 12 | Steer open textbook (NCSU/Open Textbook Library); MIT OCW course URLs | open texts / lecture notes | free-resource list | URLs checked HTTP 200 |
| 13 | Pozar/ARRL edition searches | search | editions | search summaries |

## Contradictions / discrepancies found
- rtl_433 decoder count: 14/software-demodulation says ~200; the current README lists ~380 protocols (older vs newer count, not a physics conflict) → cross-domain note.
- The ionising threshold has no single value in the literature (ICRU: depends on medium; Attix 4–25 eV; 10 eV textbooks; EURATOM 12.4 eV; BEIR 34 eV per ion pair). Pages use 12.4 eV and state the spread; conclusion unaffected.
- The V-dipole designer's "−20 dB for vertically polarised terrestrial signals" is a claim, not verified; quoted as the designer's claim only.

## Knowledge gaps noticed (for later gap-filling)
- No measured R820T/R828D NF/IIP3 vs gain index at 137/433/1090 MHz (gain-staging Monte-Carlo uses NF 4.5 dB, ENOB 7 as illustration).
- No Singapore 137 MHz / 433 MHz man-made-noise measurement (decides whether a masthead LNA helps weather-satellite reception).
- No measured patterns/efficiency of common commercial LoRa/Meshtastic antennas; RSSI spread σ for A/B tests is assumed (4 dB).
- No discrete "first radio" rung (crystal set, superregen, one-transistor FM) — D1 #11/D4 #24; needs an 06 superregen section first.
- No Singapore university RF course list (NUS/NTU/SUTD).
- Bowick and Lee *Planar Microwave Engineering* chapter-level ToCs not fetched.
- "Eye lens and testes most sensitive to local heating" stated as standard guidance but not re-read in a primary source.

## Cross-domain notes (things other domains should cover/link)
- 00/math-roadmap-for-rf.md (W1-A1) should add rf-learning-roadmap.md and rf-concepts-for-beginners.md to its `related:` list and TL;DR (not in my edit scope).
- 14/software-demodulation.md: update "~200 device decoders" for rtl_433 to "~380 listed protocols (README, 2026)".
- 14/sdr-hardware-survey.md: could add the librtlsdr gain-table facts (VGA 16.3/26.5 dB) and link sdr-gain-staging-and-reception-recipes.md.
- 08/antenna-fundamentals.md forum note on 10 dBi collinears: link choosing-and-judging-lora-antennas.md (elevation table).
- 02/09 pages on penetration and 19/rf-exposure: now linked from 00/rf-concepts-for-beginners; reciprocal "beginner version" links would help.
- 06/receiver-architectures: superregenerative receiver section would enable a rung-0 "first radio" project in the ladder.

## Resume instructions (what the next agent should do if this one is interrupted)
Task complete (2026-10-03). Nothing to resume. If revisiting: re-run the three e6 scripts; re-check Meteor-M frequencies and
RTL-SDR/NanoVNA/tinySA prices before relying on them; act on the cross-domain notes above.
