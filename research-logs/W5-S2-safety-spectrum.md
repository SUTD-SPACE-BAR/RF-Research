# Research log W5-S2: Station safety, spectrum vocabulary, analogue-mode details (gap slice S2)
Status: complete (2026-10-13)
Owner scope (edit only these, surgically): kb/19-regulations-safety/lab-safety-esd-high-power.md;
kb/19-regulations-safety/spectrum-allocation-ism-bands.md; kb/10-comms-modulation/analog-modulation-am-fm-pm-ssb.md;
kb/20-projects-recipes/lora-rocket-telemetry-link.md (ONE test row only, G-20-02); gaps/GAP_REGISTER.md (§3 → §5 moves for my rows);
tools/verify/s2_*.py. NOT allowed: 19/rf-exposure-safety.md, any _index.md.

## Plan
- [x] G-19-01 — 19/lab-safety: new section "Lightning, surge and station grounding" (strike-current physics: 1st-stroke 10/350 µs,
      di/dt, inductive voltage on down-conductor, ground-rod resistance (Dwight), ground potential rise, step voltage; arrestor types
      GDT / λ/4 stub / DC-pass-blocked; single-point entry panel; bonding; launch-site and rooftop checklists; the "roof is best" myth;
      power-line clearance). Script s2_lightning_grounding.py
- [x] G-19-02 — 19/lab-safety: hazard table (BeO, magnetron/PA HV, RF burns, power-line clearance, eye lens) + handling rules.
- [x] G-19-03 — 19/spectrum-allocation: band-designation tables (ITU RR Art. 2 band numbers 4–12, IEEE Std 521 letter bands) and
      emission-designator section (ITU RR Appendix 1, SM.1138 necessary bandwidth; decode 125KF1D / LoRa designators; SM.329
      spurious vs out-of-band domain boundary 250 % of Bn). Script s2_necessary_bandwidth.py
- [x] G-10-04 — 10/analog-modulation: SSB practice section: LSB/USB convention (history), SSB audio bandwidth, speech PEP/average
      ≈ 2.5:1 (simulated crest factor), compression/clipping, ALC, PA back-off, flat-topping; AM+FM on one carrier vs QAM. Script s2_speech_crest.py
- [x] G-10-09 — 10/analog-modulation: necessary-bandwidth formula table for CW/AM/SSB/FM (SM.1138), why CW is efficient; link E7 key-click page
      (06/transmitter-architectures has key clicks? check) 
- [x] G-20-02 — 20/lora-rocket-telemetry-link: one test row (pyro/RF interaction ≥ 16.5 dB below MNFS) + link to 19/lab-safety.
- [x] GAP_REGISTER §3 → §5 moves.

## Log (append-only)
- 2026-10-03 — Step 0: read CONVENTIONS, INDEX (grep), GAP_REGISTER §3 rows (ranks 7, 49, 50, 64, 69, 90), §6 S2 row, orchestrator notes;
  canonical-values page exists (kb/00/canonical-values-and-conventions.md) — use its TS SRD values, ERP/EIRP, spurious limits;
  read 19/singapore-imda-rules (authoritative SG). Read the four target pages. Existing related content: 14/sdr-front-end-protection
  (GDT/λ/4 stub summary, defers station grounding to 19), 08/dipoles-and-monopoles:182 (DC-grounded antennas), 19/rf-exposure already has the
  non-ionising section and eye-lens Q (W5-E6) — link to it, do not edit it.
- 2026-10-03 — Research (spectrum vocabulary, G-19-03 / G-10-09), primary sources READ as text (curl to itu.int is refused; WebFetch saves
  the PDF binary to ~/.claude/projects/.../tool-results/*.pdf, then pdftotext works). Key facts recorded:
  * RR Appendix 1 (Rev. WRC-12): Bn = 3 numerals + 1 letter (H/K/M/G at the decimal point; first char not 0/K/M/G); 0.001–999 Hz → H,
    1.00–999 kHz → K, etc.; examples 180.4 kHz = 180K, 180.5 kHz = 181K, 12.5 kHz = 12K5, 6 kHz = 6K00. 1st symbol N A H R J B C F G D P K L M Q V W X;
    2nd 0 1 2 3 7 8 9 X; 3rd N A B C D E F W X; optional 4th A–F, G H J K L M N W X; 5th N C(code-division incl. bandwidth expansion) F T W X;
    dash where 4th/5th unused.
  * SM.1138-3 (10/2019) Annex 1 formulas + examples: A1A Bn = BK (K 5 fading / 3 non-fading; 25 wpm B = 20 → 100HA1AAN); A2A BK + 2M (2K10A2AAN);
    A3E 2M (M 3000 → 6K00A3EJN); H3E M (3K00H3EJN); J3E M − lowest (3000 − 300 → 2K70J3EJN); sound bcast DSB 2M (M 4000 → 8K00A3EGN);
    F1B Bn = 2M + 2DK, M = B/2, K 1.2 (B 100, D 85 → 304HF1BBN); F3E 2M + 2DK K 1 (D 5000, M 3000 → 16K0F3EJN; 180KF3EGN);
    radar unmodulated pulse 2K/t (3M00P0NAN); OFDM Ns·K (16M6W7D).
  * NTIA Annex J (Jan 2021 rev 1/2023, ntia.gov/sites/default/files/2023-11/j_2021_edition_rev_2023.pdf): digital = 99 % OBW; radar = B20dB;
    FSK telegraphy Bn = B + 2KD (K 1.1–1.2); Morse B ≈ 0.8 × WPM; GMSK K table; 2K80J3E (M 2.7 kHz, Ml 350 Hz); 11K0F3E; 24M0G1D (GPS).
  * SM.329-13 (09/2024): RR 1.144/1.145/1.146/1.146A/1.146B definitions; spurious domain ≥ 250 % of Bn from centre; reference BW 1 kHz
    (9–150 kHz), 10 kHz (to 30 MHz), 100 kHz (30 MHz–1 GHz), 1 MHz (> 1 GHz); Cat A 43 + 10 log P or 70 dBc (= −13 dBm absolute);
    Cat B SRD −36 dBm < 1 GHz, −54 dBm in 47–74/87.5–118/174–230/470–862 MHz, −30 dBm > 1 GHz; Table 1 measurement ranges (300–600 MHz: to 3 GHz).
  * SM.1539-2 (09/2024) Table: 30 MHz–1 GHz BL 25 kHz (separation 62.5 kHz), BU 10 MHz (1.5 Bn + 10 MHz); 1–3 GHz BL 100 kHz, BU 50 MHz.
  * LoRa designators in use: 125KF1D (LoRa-APRS), 62K5F1D (IARU-R1 MeshCore RFC, github Guru-RF/meshcore-rfc-iaru-r1) — community usage;
    strict Bn would be the 99 % OBW (≈ 133 kHz at BW 125 kHz per canonical page) → "133KF1D"; 5-symbol F1DEC is my interpretation (flag it).
  * Band names: ITU-R V.431-8 PDF located (https://www.itu.int/dms_pubrec/itu-r/rec/v/R-REC-V.431-8-201508-I!!PDF-E.pdf) — NOT yet read;
    IEEE Std 521 letter bands still to verify.
- 2026-10-12 — Resumed. Step 1 done: ITU-R V.431-8 Table 1 read (bands 3–15, ULF…EHF; band 12+ have no ITU symbol; "lower limit exclusive,
  upper inclusive"; Note 1 band N = 0.3×10^N–3×10^N Hz; Table 3 broadcast bands I–V; Table 4 letter bands L 1–2, S 2–4, C 4–8, X 8–12, Ku 12–18,
  K 18–27, Ka 27–40 GHz, "not advisable" in ITU texts). IEEE 521-2019 via Bucknell chart (secondary): adds V 40–75, W 75–110, mm 110–300, THz 300–1000 GHz.
  06/pa-control-protection-and-sequencing.md now exists (ALC, ramps/key clicks) — link it from 10.
- 2026-10-12 — Lightning/grounding research: ITU-T K.112 (05/2021) read via pdftotext (equipotential bonding is the objective; earth R "as low as
  10 Ω" whenever feasible, else min ring radius; feeder bonded top of tower + at entry bar (and at bending point if horizontal run ≥ 10/15/20 m
  for LPL I/II/III–IV); unshielded cables via SPDs at 3 places; welded/crimped joints; min Cu 16 mm² to avoid melting at 10 MJ/Ω; rooftop: bonding
  network along cable tray, not along roof edge; soil-resistivity Table B.1). ABB IEC/BS EN 62305 guide: LPL max 200/150/100/100 kA, min 3/5/10/16 kA,
  rolling sphere 20/30/45/60 m. IEC 62305-1 LPL I first stroke 200 kA 10/350, 100 C, 10 MJ/Ω; subsequent 50 kA 0.25/100, 200 kA/µs (secondary
  search summary of the IEC table — label). Reeve (2011) NEC Art. 810 paper: ADU per 810.20, ≥ 10 AWG Cu (810.21(H)), 6 AWG bond to power electrode
  (810.21(J)), straight path no sharp bends (810.21(E)), solder-only joints not acceptable (250.70). PolyPhaser IS-50NX-C2-ME datasheet: GDT + DC block,
  125–1000 MHz, 0.1 dB, 50 kA 8/20, 600 V ±20 % turn-on, 220 µJ let-through @3 kA. MSS: ≈ 176 lightning days/yr, peak Nov, Apr–May. SS 555:2010
  (IEC 62305:2006 based; BCA deemed-to-satisfy from 1 Jul 2011 per IES circular; current edition unverified). OSHA 1910.333(c)(3) 10 ft (305 cm)
  ≤ 50 kV + 4 in/10 kV; OSHA 1910.1024 Be PEL 0.2 µg/m³ TWA, STEL 2.0, AL 0.1; NOAA JetStream: lightning > 10 mi from rain, wait 30 min.

- 2026-10-12 — Scripts written, ALL PASS: tools/verify/s2_necessary_bandwidth.py (RR App.1 formatter vs all 15 footnote examples; 13 SM.1138/NTIA
  sample designators; CW 13/25 WPM → 52/100 Hz; LoRa 99 % OBW by simulation: SF7 1.047×BW (131 kHz at 125 kHz), SF9 ≈ 1.00, SF12 0.986;
  SM.329/1539 boundaries; V.431 band numbers). tools/verify/s2_speech_crest.py (macOS `say` TTS 4 voices + source-filter model: unprocessed
  SSB PEP/avg 13.3–15.1 dB whole recording, 11.9–13.6 dB talk-only (TTS); RF clip 6/12/18 dB → +2.8/+5.1/+6.1 dB average at equal PEP;
  compressor w/o look-ahead −1.9 dB (worse), with look-ahead +4.9 dB). tools/verify/s2_lightning_grounding.py (r = 10 I^0.65 vs rolling sphere;
  Dwight vs average-potential numerics ±0.1 %; GPR, step voltage, L·di/dt, loop pickup, λ/4 stub RL, GDT vs RF peak).
- Speech-processing literature: Hershberger W9GR, QEX Nov/Dec 2014 (CESSB: overshoot after SSB filter; ≈ 3.8 dB peak reduction → ≈ +140 %
  average at equal PEP vs ≈ +80 % for fast look-ahead ALC); SM5BSZ DUBUS article (re-peaking after RF clip + filter); US patent 4,410,764 (17 dB
  typical unprocessed PAPR; compression ~1 dB; 18 dB clipping → ~8 dB). Exam pool E8A06 answer 2.5:1 (4 dB) is far below every measurement → Contradiction.
- 2026-10-12 — G-19-03 DONE: 19/spectrum-allocation-ism-bands — new sections "Band names: ITU numbers and radar letter bands",
  "Emission designators and necessary bandwidth", "Out-of-band vs spurious domains (ITU-R SM.329, SM.1539)"; TL;DR +3 bullets, Level 1 band-number
  formula, 6 new questions, worked examples 4–5, 5 Common-mistakes entries, verify + gaps + sources 8–15; last_updated 2026-10-12.
  (Note: running `tools/build_index.py --help` regenerated INDEX.md/FAQ.md as a side effect — it has no --help; harmless regeneration.)
- 2026-10-12 — G-10-04 + G-10-09 DONE: 10/analog-modulation-am-fm-pm-ssb — new sections "SSB in practice — sideband conventions, speech statistics
  and processing" (LSB/USB + band-edge rule, SSB audio BW, PEP/avg derivation + simulated table, processing table, ALC/flat-topping, AM+FM vs QAM)
  and "Necessary bandwidth of analogue emissions, and why CW is efficient" (SM.1138 table, CW 14.3 dB argument, key clicks → 06/pa-control);
  TL;DR +2, 8 questions, design-table rows, Examples 6–7, practical notes, 6 Common mistakes, verify, gaps, sources 10–13; last_updated 2026-10-12.
- 2026-10-13 — G-19-01 + G-19-02 DONE: 19/lab-safety-esd-high-power — new "Lightning, surge and station grounding" (intuition, Level 1–3 numbers,
  protection-hierarchy table, GDT vs λ/4-stub table, bonding layout in words, rooftop section + myth, launch-site checklist, power-line clearance)
  and "Other bench and station hazards" table; TL;DR +3, 9 questions, design rows, Examples 5–7, 9 Common mistakes, verify, gaps, sources 7–16.
- 2026-10-13 — G-20-02 DONE: 20/lora-rocket-telemetry-link test row T11 (pyro/RF interaction, ≥ 16.5 dB below MNFS), last_updated bumped.
- 2026-10-13 — GAP_REGISTER: §5 rows C68–C73 appended; §3 rows 7/49/50/64/69/90 and §2 item 7 marked "closed → §5 Cnn" (same convention as
  W5-E9/W5-S1 — rows kept, per the register's "do not delete rows" rule). INDEX/FAQ rebuilt (build_index.py; 279 pages). All 3 scripts ALL PASS;
  build_index --check: no broken links from the four edited pages.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
| 1 | ITU RR Appendix 1 (Rev. WRC-12), itu.int/en/ITU-R/terrestrial/workshops/wrs12/Miscellaneous/Appendix1.pdf | treaty text | designator symbols, Bn notation | read in full via pdftotext |
| 2 | Rec. ITU-R SM.1138-3 (10/2019) | standard | Bn formulas + examples | read in full |
| 3 | NTIA Manual Annex J (2021 rev 2023) | regulator | Bn method preference, 99 % OBW, K tables | read §J.1–J.3.7 |
| 4 | Rec. ITU-R SM.329-13 (09/2024) | standard | domains, reference BWs, Cat A/B | read §1–4.2, Annex 4 |
| 5 | Rec. ITU-R SM.1539-2 (09/2024) | standard | OoB/spurious boundary variations | Table read |
| 6 | Guru-RF MeshCore IARU-R1 RFC (GitHub) | community proposal | 62K5F1D / 125KF1D usage | forum-level |
| 7 | Rec. ITU-R V.431-8 (08/2015) | standard | band numbers/names, letter bands | Table 1–4 read |
| 8 | IEEE Std 521-2019 via D. Kelley (Bucknell) chart | standard (secondary reproduction) | V/W/mm/THz letter bands | standard itself paywalled |
| 9 | Rec. ITU-T K.112 (05/2021) | standard | bonding/earthing practice for radio sites | read §6–7, Annex B |
| 10 | ABB "Total Solution to Earthing & Lightning Protection", IEC/BS EN 62305 guide | manufacturer guide | LPL currents, rolling sphere | |
| 11 | W. Reeve, "Antenna system bonding and grounding requirements in the NEC" (2011) | engineering paper | NEC 810/250 rules | US code, informational |
| 12 | PolyPhaser IS-50NX-C2-ME datasheet rev 1.1 (2020) | datasheet | GDT arrestor numbers | |
| 13 | MSS weather.gov.sg "Weather systems" | regulator/met service | 176 lightning days | |
| 14 | 29 CFR 1910.333, 1910.1024 (Cornell LII) | regulation | power-line clearance; Be limits | US rules as reference |
| 15 | NOAA JetStream "Lightning safety"; OSHA 3863 | agency guidance | 10 mi / 30 min | |

## Contradictions / discrepancies found
- SSB speech PEP/average: FCC/ARRL exam pool (Extra E8A06) "≈ 2.5:1" (4 dB) vs measured/simulated unprocessed speech 12–17 dB (this task's TTS
  13–15 dB; US 4,410,764 17 dB; forum 14 dB). Page states the measured values and explains 2.5:1 as roughly a heavily processed figure (W5-S2 reading).
- LoRa 99 % OBW: canonical page says ≈ 133 kHz at BW 125 kHz; this simulation gives 131 kHz at SF7 and ≈ 125 kHz at SF ≥ 9 (ideal chirps,
  no PA/filter). Not edited (canonical page not in scope); 19 page quotes "≈ 1.05 × BW at SF7, ≈ 1.0 × BW at SF ≥ 9; canonical uses 133 kHz as a
  conservative edge figure". Cross-domain note for the canonical page owner.
- Reeve (2011) writes that conductor bends should "form an included angle less than 90 deg" — reads as a typo for "not less than 90°"
  (NFPA 780 practice); page states radius ≥ 200 mm and no hairpins.

## Knowledge gaps noticed (for later gap-filling)
- Measured speech PEP/average on a live talker and the team's own SSB/FM rig (TTS is a lower bound).
- IEC 62305-1 / NFPA 780 / ARRL grounding book not read directly (paywalled); SS 555 current edition and Singapore wiring-code bonding rules unchecked.
- No IMDA-stated emission designator for LoRa; ask in the R26 written query.

## Cross-domain notes (things other domains should cover/link)
- 00/canonical-values: LoRa 99 % OBW simulated 131 kHz (SF7/125) and ≈ 125 kHz at SF ≥ 9; the 133 kHz edge figure is conservative — owner may add the SF dependence.
- 15/ground-station-design and 14/sdr-front-end-protection: link to 19/lab-safety#lightning-surge-and-station-grounding (λ/4 stub also shorts 2f0 —
  matters for a diplexed 433/868 feed).
- 19/singapore-imda-rules: could cite 19/spectrum-allocation#emission-designators-and-necessary-bandwidth for permit applications (F1D, 99 % OBW).
- 13/emc (G-13-01 surge/EFT) can reuse the loop-pickup formula and K.112 bonding rules.

## Resume instructions (what the next agent should do if this one is interrupted)
- **State at pause (2026-10-03):** Step 0 done; all four target pages read (none edited); spectrum-vocabulary research done (see Log).
  Scratch copies of the ITU PDFs/texts were in the session scratchpad (lost); re-fetch via WebFetch (it saves the PDF) + pdftotext if needed.
- **Exact next steps, in order:**
  1. Read ITU-R V.431-8 (band numbers 4–15, abbreviations VLF…EHF/THF, metric names, "0.3×10^N to 3×10^N Hz, lower limit excluded") and
     verify IEEE Std 521 letter bands (L 1–2, S 2–4, C 4–8, X 8–12, Ku 12–18, K 18–27, Ka 27–40, V 40–75, W 75–110, mm 110–300 GHz).
  2. Write tools/verify/s2_necessary_bandwidth.py (Bn formulas vs every SM.1138/NTIA example above; RR App.1 rounding/formatter incl.
     180.5 kHz → 181K; LoRa 99 % OBW → designator; SM.329/SM.1539 boundary for E22 CH 24 at 125/250/500 kHz; band-number function).
  3. Edit 19/spectrum-allocation-ism-bands: add "Band names" + "Emission designators and necessary bandwidth" + "Out-of-band vs spurious
     domains" sections, Common-mistakes entries, sources; bump last_updated. (G-19-03)
  4. Edit 10/analog-modulation: necessary-bandwidth table (A1A/A3E/H3E/J3E/F3E/F1B) + "why CW is efficient" (G-10-09; link
     06/transmitter-architectures and 17/oscilloscopes for key clicks — the planned E7 PA-control page does not exist); SSB practice section
     (G-10-04): LSB/USB convention, 300–2700 Hz audio, speech PEP/average via `say -o x.aiff` + script s2_speech_crest.py (clipping/compression/ALC,
     PA back-off), AM+FM on one carrier vs QAM.
  5. Research + edit 19/lab-safety: lightning/station grounding section (G-19-01: IEC 62305-1 / NFPA 780 strike parameters, ITU-T K.56/K.27,
     ARRL grounding; ground-rod Dwight formula, GPR, L·di/dt on down-conductor, GDT/λ/4 stub, single-point entry panel, bonding, rooftop & launch-site
     checklists, "roof is always best" myth, power-line clearance) with script s2_lightning_grounding.py; hazard table (G-19-02: BeO, magnetron/PA HV,
     RF burns, power lines, eye lens → link 19/rf-exposure, do not edit it).
  6. Add ONE test row to 20/lora-rocket-telemetry-link test plan (table at "## Build, bring-up and test plan"): pyro/RF interaction, continuous TX
     at max power with dummy igniter, pass = induced current ≤ 15 % of no-fire (≥ 16.5 dB below MNFS), link 19/lab-safety Example 3. (G-20-02)
  7. GAP_REGISTER: move ranks 7, 49, 50, 64, 69, 90 from §3 to §5 (next free C-numbers after C55) with page#section; update log; final report.
- Check the Plan checkboxes; each finished item has a dated Log line naming the section added. For an unfinished item, re-read the target
  page, grep for the section heading named in the plan (it may be partially written), finish it, then do the register move (§3 row → §5 Cxx).
