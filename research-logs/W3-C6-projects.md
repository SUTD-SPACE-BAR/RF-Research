# Research log W3-C6: 20-projects-recipes
Status: complete (2026-10-02)
Owner scope: kb/20-projects-recipes/, research-logs/W3-C6-projects.md, tools/verify/proj_*.py

## Plan
Recipe template (inside the CONVENTIONS page template; "The math" = design calculations):
requirements → architecture options & trade study → calculations (scripted) → part selection (→18)
→ block diagram → layout notes (→13) → simulation plan (→16) → build & bring-up/test plan with
pass/fail (→17) → regulatory check (→19, singapore-imda-rules.md authoritative) → risks/failure
modes → cost → pre-registered predictions.

- [x] lora-rocket-telemetry-link — DONE 2026-09-29 (399 lines; script tools/verify/proj_lora_link.py) — 433/900 MHz downlink, 10 km apogee / 15 km slant, SF/BW vs Doppler rate, packets, antennas, GS, link budget legal vs licensed, dual band, attenuator range test, pre-registered predictions
- [x] ground-station-tracking-yagi — DONE 2026-09-29 (script proj_ground_station.py) — DL6WU 433/915 Yagi, LNA+SAW at feed, cable, tracking, diversity, SDR recording
- [x] patch-antenna-design-walkthrough — DONE 2026-10-02 (proj_patch_gnss.py, proj_openems_gnss_patch.py) — 1575.42 MHz (and 2.45 GHz) patch on JLC FR-4, calc → openEMS → fab → NanoVNA; CP variant
- [x] bandpass-filter-design-walkthrough — DONE 2026-10-02 (proj_harmonic_filter.py) — 433 MHz LC LPF/BPF after LoRa PA; 915 MHz microstrip/SAW option
- [x] lna-design-walkthrough — DONE 2026-10-02 (proj_lna_gnss.py) — 433 MHz or GNSS L1 LNA, stability, noise match, bias, layout, measurement
- [x] gnss-front-end-design — DONE 2026-10-02 (proj_gnss_frontend.py) — active antenna chain, ZED-F9P/MAX-M10S, SAW/LNA budget, LoRa harmonics/desense of L1
- [x] sdr-receiver-build — DONE (proj_sdr_receiver.py) — gr-lora_sdr ground receiver / spectrum monitor, front-end filter, gain staging
- [x] fmcw-radar-build — DONE (proj_fmcw.py) — 24 GHz module or TI mmWave or ADI Phaser; chirp design, processing, corner reflectors
- [x] phased-array-starter-build — DONE (proj_phased_array.py) — 4–8 el receive array (KrakenSDR/Pluto/Phaser), calibration, DOA; phased array vs tracked Yagi
- [x] design-review-checklists — DONE (proj_preflight_rf.py) — RF schematic, RF layout, bring-up, pre-flight RF checklists
- [x] _index.md, _sources.md — DONE (beginner-project-ladder.md by W5-E6 listed as entry point)

## Log (append-only)
- 2026-09-29 — Created log. Read CONVENTIONS.md, INDEX.md, HANDOFF.md. kb/20 empty (fresh start).
  Domains still in progress: 06 (B2), 11 (B4), 12 (B5), 13 (C1, only 1 page), 14 (B7), 16 (C2), 17 (C3), 18 (C4).

- 2026-09-29 — Read avionics KB (capabilities, B-V3, C, lessons, ethos, HIL). Read KB pages: 19 singapore-imda-rules (authoritative),
  international-rules; 15 rocket-telemetry-radio-design, lora-sensitivity-and-link-budget, lora-impairments, ground-station-design,
  lora-modules; 08 antennas-on-rockets, yagi (TL;DR); 18 lna-pa-gain-block-mmics (TL;DR); 17 antenna-range-ota-testing (TL;DR).
- 2026-09-29 — Wrote tools/verify/proj_lora_link.py: point-mass trajectory (3500 N, 6.93 s, 11.8 kg prop, Isp 210) -> 9998 m apogee,
  Mach 2.0, 11.1 g burn, 8.7 g drag decel; stations A/B/C/D; per-packet Semtech drift check (SF9/125 fails 1-12 % at 868/905 MHz,
  OK at 433; SF10-12/125 fail 7-35 %); air time (SF7/125 102 %, SF7/250 51 %, SF7/500 25 %); cascade NF 1.73 dB; budgets at 15 km
  (433 10 mW e.r.p. 19.1 dB margin, 33 dBm 41.6 dB, 868 24 dBm 28.5 dB); landed two-ray; range-test numbers (A_eq 39.7 dB @1 km;
  conducted ladder needs ~145 dB -> impractical); E22 2nd harmonic 866.25 MHz vs E220 CH16 (0.125 MHz!). JLC DB prices for
  EBYTE modules (snapshot 2026-07-08). Web: E22-400M33S product page (SX1268, 32 MHz crystal); E22-400T22D power steps unverified.
- 2026-09-29 — Wrote kb/20-projects-recipes/lora-rocket-telemetry-link.md.
- 2026-09-29 — CORRECTION (appended, not silently edited): first version of proj_lora_link.py used 2.3 dB for 15 m RG-58 and
  1.3 dB for 15 m LMR-240 at 433 MHz; kb/03 coax fits give 4.3 dB and 2.6 dB. Script now uses the fits; ground-chain NF 1.73 ->
  2.01 dB; all margins in the page shifted by -0.3 dB (e.g. 433 10 mW e.r.p. 19.1 -> 18.8 dB); page updated.
- 2026-09-29 — Wrote tools/verify/proj_ground_station.py (imports ant_yagi DL6WU + MoM; 6-el 433: 11.19 dBi, 73 ohm, 50x61 deg;
  11-el 14.2; 6-el 868/905 11.2 dBi, 80-83 ohm; CP harness ABCD: 56 ohm, AR <= 0.27 dB with 50-ohm Yagis BUT AR 3.3-4.1 dB with
  the 6-el native 73-81 ohm while harness S11 looks better (-33..-48 dB) -> trap; cascades; blocking; tracking: fixed 6-el worst
  4.9 dB, tablet p95 0.6 dB, G-5500 el lag 18 deg). Web: Yaesu G-5500DC rotation times (58 s/360 az, 67 s/180 el), TDK B3710
  (433.00-434.71 MHz, <=2.7 dB) and B3744 (868.3 MHz, 600 kHz, 290 ohm//1.3 pF) via distributor summaries.
- 2026-09-29 — Wrote kb/20-projects-recipes/ground-station-tracking-yagi.md.
- 2026-10-02 — RESUMED. Fixed proj_harmonic_filter.py bugs: (1) fmt() now prints trap zeros including the 0.16/0.20 pF
  parasitic (inductor self-C + pads); (2) shunt-cap re-optimisation bounded to 0.6-1.6x prototype; trap L choice weighted
  toward the prototype L. 433 elliptic: 15 nH||2.1 pF (864.4 MHz), 16 nH||0.8 pF (1284 MHz), C 5.9/10/4.1 pF: IL 0.46 dB,
  2f 60.4, 3f 76.4 dB; MC p5 2f 50.9, 3f 61.5; far stop band collapses (4 GHz 27 dB, 6 GHz 1.5 dB). 905: IL 0.54, RL 31.7.
  JLC DB: GJM1555C1H2R1WB01D etc. (high-Q 0402, +/-0.05 pF), Coilcraft 0603CS/0402CS (thin stock), LFCN-490+ C3008205 $3.06.
  Wrote kb/20-projects-recipes/bandpass-filter-design-walkthrough.md.
- 2026-10-02 — openEMS quick #2: linear 44.88 mm -> 1558.5 MHz (-1.07 %), same as run #1 (mesh-independent); CP a=5.36,
  xf=15: AR min 1.80 dB at 1572.5 MHz, LHCP (corner choice), AR BW 10 MHz, Z 54.7+13.4j. Running `design` sweep (mirrored = RHCP).
- 2026-10-02 — openEMS design sweep (mirrored cut = RHCP): a 4.8 -> AR 4.5 dB; a 5.9 -> AR 0.77 dB @1577.5 MHz. Final 44.94 mm,
  a 5.9, xf 15 (coarse): AR 0.72 dB @1575.0 MHz, AR<=3 dB 15 MHz, S11 -15.5 dB @L1, D_RHCP 6.30 dBic, X-pol -21.2 dBic,
  e_rad 35.6 %, G_RHCP 1.81 dBic (1.7 realised), HPBW 96 deg, AR 2.4 dB at horizon. Optimum cut 1.10x the 1/(2Q) rule
  (rule derived by cavity perturbation in the page). Wrote patch-antenna-design-walkthrough.md. Fine-mesh run in progress.
- 2026-10-02 — Coordinator cross-domain findings (W5-E1) applied: E22 CH 0-6 3f in GPS/GLONASS L2 (script §10 now lists all
  channels; also CH 10-22 3f in Galileo E6/BDS B3; CH23 0.17 MHz above E6 edge) -> recipe 1 freq plan, filter F7;
  landed 10 mW e.r.p. range cross-check 1.75 km (bare module) reproduced vs my 2.1 km (LNA) -> both quoted in recipes 1/2.
  To do: fmcw recipe must state 77-81 GHz licence-exempt only as UWB (mean <= -3 dBm/MHz, sweep >= 500 MHz).
- 2026-10-02 — Verified BGA524N6 datasheet rev 3.0 (pdftotext of a mirror): table IP1dB -16 dBm, IIP3 -9 dBm, IIP3_oob -5 dBm;
  feature list says IP1dB -12, IIP3_oob -4; AN420 (1.8 V, 0201) IP1dB -12.3, IIP3 +3.5, IIP3_oob -7.8. Wrote proj_lna_gnss.py.
- 2026-10-02 — CORRECTION/ANOMALY A1 (appended): fine-mesh final run moved the AR minimum to 1545 MHz (-1.9 %), AR at L1
  10.2 dB -> coarse result not converged. Cause: patch edges not on mesh lines (uniform grid, no thirds rule) -> patch size
  quantised by up to a cell. Fixed in script (edge-locked thirds-rule lines, mode `edges`); rerunning coarse+fine on the final
  geometry. Patch page numbers must be revised after this rerun (page currently quotes the coarse values).
- 2026-10-02 — edge-locked mesh (thirds rule) coarse run of the final geometry 44.94/5.9/15: AR min 0.65 dB at **1567.5 MHz**
  (was 1575.0 with the free grid), AR at L1 2.66 dB, S11 -16 dB at L1. Fine edge-locked run was KILLED at the pause (no result).
- 2026-10-02 — Wrote lna-design-walkthrough.md and gnss-front-end-design.md (scripts proj_lna_gnss.py, proj_gnss_frontend.py).
  Coordinator FYI: W5-E6 creates kb/20-projects-recipes/beginner-project-ladder.md -> list it as beginners' entry in _index.md.
- 2026-10-02 — Resumed; wrote proj_sdr_receiver.py and sdr-receiver-build.md (RTL clip ~-71 dBm at LNA input -> high/low pair).
- 2026-10-02 — ANOMALY A1 RESOLVED: edge-locked thirds-rule mesh, side 44.71 mm: coarse AR min 1577.5 MHz, fine 1575.0 MHz
  (0.16 % apart, converged). Fine: AR 0.23 dB min, 0.35 dB at L1, S11 -15.6 dB, D_RHCP 6.29 dBic, X-pol -28.3, e 35.6 %,
  G_RHCP 1.81 dBic. Patch page revised (final side 44.71 mm; mesh trap documented; free-grid rows flagged as quantised).
- 2026-10-02 — Wrote proj_fmcw.py + fmcw-radar-build.md (IWR6843 60 GHz SRD; 77-81 GHz UWB-only rule incl. >= 500 MHz sweep;
  TDM-MIMO v_max/N_TX; rail-exit config C: +-124 m/s, R_max 20 m IF-limited; rocket at 6 m 35 m/s, 20 m 64 m/s).
- 2026-10-02 — Wrote proj_phased_array.py + phased-array-starter-build.md (KrakenSDR UCA r 23.6 cm; 2 deg phase -> 0.65 deg;
  1 cm cable = 7.9 deg @433; triangulation 1 deg -> 220 m median; Phaser HPBW 13.3 deg; Yagi wins for telemetry).
- 2026-10-02 — Wrote tools/verify/proj_preflight_rf.py (automated pre-flight RF gate, PASS/FAIL incl. missing evidence).
  NEW FINDING F-BE: 433.125 MHz at 250 kHz occupies 433.000-433.250 MHz -> lower edge below the SG 433.05 MHz band edge;
  for 250/500 kHz in SG use CH24 434.125 MHz, and then the E220 must move to CH17 (2 x 434.125 = 868.25 MHz is 0.125 MHz
  from CH18). Recipe 1 corrected (TL;DR, freq plan, parts, regulatory, risks). Also removed a wrong suggestion
  ("move primary to 433.625 MHz" - EBYTE channels are 1 MHz steps).
- 2026-10-02 — Coordinator audit items: #9 landed-range assumptions now stated explicitly in recipe 1 (two-ray, heights,
  SF, margins, NF; kb/15 bare-module 5.6/1.7 km cross-check shown); #3 BGA524N6 IP1dB -16 dBm: gnss-front-end TL;DR and
  Level 2 corrected (SAW-first + 20 dB coupling is 4 dB short for the E22 and 1 dB short at 905 MHz for no-compression).
- 2026-10-02 — Wrote design-review-checklists.md, _index.md, _sources.md. Ran tools/build_index.py --check: 0 pages missing
  template sections in kb/20; only broken links are to beginner-project-ladder.md (being written by W5-E6). NOTE: that
  command also regenerates INDEX.md and FAQ.md (auto-generated files) - done as a side effect, no hand edits.
  All background openEMS jobs finished; none running.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| 1 | JLCPCB parts DB snapshot 2026-07-08 (~/jlc-trawler-data) | distributor data | module prices | prices change; USD qty 1-9 |
| 2 | cdebyte.com E22-400M33S page (via search summary) | vendor | chip, crystal | summary only |

## Contradictions / discrepancies found

## Knowledge gaps noticed (for later gap-filling)
- E22-400T22D/S power steps (22/17/13/10 dBm per secondary sources) unverified from EBYTE manual.
- No installed null-depth data for rocket dipoles (the -20 dBi floor used in proj_lora_link.py is an assumption).

## Cross-domain notes (things other domains should cover/link; errors found)
- Band-edge check (applies to 15/19 pages that quote "433.125 MHz" for Singapore licence-exempt operation): at BW 250/500 kHz
  433.125 MHz is outside 433.05-434.79 MHz (lower channel edge 433.000/432.875 MHz). 19 singapore-imda-rules example 1/2 and
  15 band-plan statements assume 125 kHz implicitly; worth stating "<= 125 kHz at 433.125, or use 434.125 MHz".
- 15 rocket-telemetry-radio-design / lora-impairments recommend putting the E220 in 917-925 MHz to avoid the E22 2nd harmonic,
  while 19 singapore-imda-rules recommends 866-869 MHz (500 mW, no duty) as the most permissive band. Not an error, but a
  tension: 917-925 MHz LoRa class (100 mW, 1 % duty) cannot carry 10 Hz telemetry (0.2-0.4 Hz max for 48 B frames). The
  recipe resolves it: 868.125 MHz (CH18, 1.875 MHz from the harmonic), never CH16 (0.125 MHz from 866.25 MHz).
- 18 lna-pa-gain-block-mmics.md line ~108: BGA524N6 "IIP3 / IP1dB = -4 / -12 dBm" mixes the datasheet FEATURE-LIST
  out-of-band IIP3 (-4) with the feature-list IP1dB (-12). The rev 3.0 electrical table gives in-band IP1dB -16 dBm,
  IIP3 -9 dBm, out-of-band IIP3 -5 dBm (06 lna-design.md quotes the table values, correctly). Correction for 18: list
  "IIP3 -9 (in-band) / -5 (oob); IP1dB -16 (table; -12 in the feature list)". Source: Infineon BGA524N6 data sheet rev 3.0, p.9.
- A close ground station sees radial acceleration above the vehicle's own (LOS rotation, v_perp^2/R term): 13.7 g vs 11.1 g
  for a 2 km station. 15 lora-impairments tables use vehicle acceleration only; worth a sentence there.

## Resume instructions
Task complete (2026-10-02). 10 recipes + _index + _sources written; 11 scripts tools/verify/proj_*.py.
If revisiting: (1) add EuRoC/Australia venues to proj_preflight_rf.py; (2) when hardware tests run, append results to each
recipe's pre-registered prediction table as a dated addendum (never edit the predictions); (3) re-run build_index --check
after W5-E6 lands beginner-project-ladder.md.
