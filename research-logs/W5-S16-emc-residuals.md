# Research log W5-S16: 13 EMC residuals (GAP_REGISTER slice S16)
Status: complete (2026-10-13)
Owner scope (edit only): kb/13-pcb-rf-layout-emc/emc-emi-fundamentals.md; kb/13-pcb-rf-layout-emc/mixed-signal-layout.md;
kb/13-pcb-rf-layout-emc/shielding-and-isolation.md; kb/19-regulations-safety/certification-fcc-ce-imda.md;
new scripts tools/verify/s16_*.py; gaps/GAP_REGISTER.md (§3 status + §5 closed rows only). No _index.md edits.
Do NOT edit W5-E11's 13/digital-termination-and-crosstalk.md (planned, not yet written) — link only.

## Plan
- [x] G-13-01 → 13/emc-emi-fundamentals: new section "EMC standards and transients for avionics" (MIL-STD-461G and DO-160G
      test families in context, EFT/surge/ESD waveforms, snubber + flyback/TVS design for pyro and servo loads, contact
      protection, hot-plug ceramic-cap overshoot); worked example; script s16_snubber_transients.py.
- [x] G-13-03 → 13/emc-emi-fundamentals (LISN conducted emissions, LPDA pre-scan with antenna factor, failed-test workflow,
      budget kit) + 19/certification (radio test modes, lab-day workflow, pointer); script s16_precompliance.py.
- [x] G-13-02 → 13/mixed-signal-layout: termination + NEXT/FEXT + saturation length + guard traces for flight-computer SPI/clock
      on JLC04161H-7628; script s16_crosstalk.py (reuses tools/verify/tline_fd2d.py field solver; Bergeron TDR sim).
- [x] G-13-04 → 13/shielding-and-isolation: enclosure seams/doors/gaskets, wire-mesh and fabric SE vs frequency, Faraday-box
      phone budget, SDR cage-test recipe with dynamic-range budget; script s16_mesh_shielding.py.
- [x] Close rows in GAP_REGISTER §5, mark §3 rows closed.

## Log (append-only)
- 2026-10-13 — Step 0 done: read CONVENTIONS, INDEX (grep), GAP_REGISTER §3 rows (G-13-01/02/03/04), §6 S16, orchestrator notes;
  canonical values (§B JLC stackup 0.2104 mm/εr 4.4; AF constant 29.77 used in 00/decibels and 08/antenna-measurement);
  17/interference-hunting (to link; covers hunting, ferrites, RCD, av-bay immunity — not duplicated). Read all four target pages.
  W5-E11's 13 page not yet written (E11 log: planned "reflections, rise time vs length, termination schemes, NEXT/FEXT from Lm/Cm,
  3W rule numerically") → my mixed-signal section is the flight-computer budget layer; link to E11 page for theory.

- 2026-10-13 — Web research (secondary summaries; the standards themselves were not fetched: ATEC 461G PDF 403, TUBITAK PDFs parse error):
  * MIL-STD-461G (11 Dec 2015; superseded by **MIL-STD-461H, 17 Apr 2026**, not reviewed): CE102 10 kHz–10 MHz (50 µH / 5 µH LISN);
    CS101 30 Hz–150 kHz; CS114 BCI 10 kHz–200 MHz; CS115 impulse 5 A, ≈30 ns, ≤2 ns edges, 30 Hz for 1 min (vendor datasheet + VectorNav;
    IT article confirms 2 ns, 30 Hz, 1 min, 50 Ω fixture); CS116 damped sines 10 k/100 k/1 M/10 M/30 M/100 MHz, ≤1 pulse/s (Imax curve not
    confirmed); CS117 lightning indirect + CS118 personnel ESD new in G, CS106 removed; RE102 10 kHz–18 GHz; RS103 2 MHz–40 GHz, levels
    1–200 V/m by platform (Table XI values not confirmed); RS105 ≥ 50 kV/m.
  * DO-160G (Dec 2010, Change 1 Dec 2014; = EUROCAE ED-14G): sections 15 magnetic, 16 power input (only section with both emission and
    susceptibility), 17 voltage spike, 18 audio-frequency conducted susceptibility, 19 induced signal, 20 RF susceptibility (CS ≈ CS114,
    RS ≈ RS103, reverb chamber), 21 RF emission (conducted 150 kHz–150 MHz current probe; radiated 100 MHz–6 GHz per one lab),
    22 lightning induced (WF3 1/10 MHz damped sine, WF4 6.4/69 µs voltage, WF5A 40/120 µs current; sets A = 3+4, B = 3+5A; levels Voc/Isc
    table 22-2 not confirmed), 23 direct effects, 25 ESD.
  * IEC 61000-4-4 EFT: 5/50 ns, 15 ms bursts every 300 ms, 5 kHz (traditional) or 100 kHz; power 0.5/1/2/4 kV, signal 0.25/0.5/1/2 kV.
  * IEC 61000-4-5 surge: 1.2/50 µs Voc, 8/20 µs Isc, 2 Ω effective (12 Ω / 42 Ω coupling = from knowledge, unconfirmed); classes 0–4 =
    25 V/0.5/1/2/4 kV; 10/700 µs telecom.
  * CISPR 32 Class B conducted QP/AV: 0.15–0.5 MHz 66→56 / 56→46 (linear in log f), 0.5–5 MHz 56/46, 5–30 MHz 60/50 dBµV; radiated
    10 m QP 30 (30–230 MHz) / 37 (230–1000 MHz) dBµV/m; 3 m = +10 dB (40/47) not confirmed from text; >1 GHz 50–54 dBµV/m AV at 3 m.
  * CISPR 25 voltage method 0.15–108 MHz (current probe to 245 MHz), 5 µH AN with 50 Ω port; one LISN if return < 20 cm to chassis,
    else two (TekBox manual); unused port terminated in 50 Ω.

- 2026-10-13 (resumed) — wrote tools/verify/s16_crosstalk.py (ALL PASS; output s16_crosstalk_output.txt). Key: 0.2 mm traces on
  JLC04161H-7628 L1, Z0 66–67 Ω, v 0.576c; NEXT_sat kb 9.0/4.2/2.3/1.0 % at gaps 0.2/0.4/0.6/1.0 mm; kf −5.2/−3.7/−2.6/−1.3 %;
  0.6 mm + stitched guard kb 0.97 % (floating guard 2.43 % — no help); L_sat = v·tr/2 = 86 mm at 1 ns; MTL-FDTD matches closed forms
  (NEXT 15.77 vs 15.77 mV at 30 mm; FEXT −23.4 vs −22.8 mV at 150 mm) WITH tr = linear 0–100 % ramp (= 1.25 × 10–90 %).
  100 mm SPI SCK, Rout 30 Ω (assumed), 5 pF: unterminated overshoot +1.18 V / ring-back −0.43 V, settles 4.8 ns; series 37 Ω: 0 overshoot;
  parallel 67 Ω: DC 2.28 V, 34 mA; Thevenin 2×134 Ω: 12 mA; AC 67 Ω+100 pF: 22 mW at 20 MHz, slow settle. l_crit = v·tr/6 = 29 mm at 1 ns.
- 2026-10-13 — wrote tools/verify/s16_snubber_transients.py (ALL PASS; output s16_snubber_transients_output.txt). Key: ring-halving
  80→40 MHz with 470 pF → Cpar 157 pF, L 25 nH, R 12.7 Ω, Cs 680 pF, 0.88 mW at 20 kHz; turn-off peak 35.1 → 19.9 V, ring killed.
  Pyro 6 A, 0.8 µH wiring: unclamped 310 V → FET avalanche ~35 V, 18.9 µJ, 180 ns; freewheel diode + 10 µF bulk → +1.04 V.
  Solenoid 10 mH/12 Ω: diode-only 1.63 ms to 10 %; Zener 24 V 0.216 ms, switch 33 V. Hot-plug 2S into 5 µF eff MLCC via 0.5 µH:
  15.6 V peak (3S 23.5 V); damping 0.32 Ω + 20 µF → 10.5/15.7 V. Surge 1 kV/2 Ω into 20 V clamp: 490 A, 171 mJ; EFT 2 kV/50 Ω: 40 A,
  30 µJ/pulse, 2.2 mJ/burst. 8/20 analytic t³e^(−t/3.911 µs) verified (front 8.0 µs, duration 19.1 µs).

- 2026-10-13 (resumed 2) — s16_precompliance.py ALL PASS: 50 µH LISN |Z| 36 Ω @150 kHz, 48–50 Ω ≥ 0.5 MHz; 5 µH AN 5.7 Ω @150 kHz,
  25 Ω @1 MHz; bare 2 MHz buck (8.4→3.3 V, 1 A, 5 µF eff) 76 dBµV at LISN = +30 dB over CISPR 32 B AV; 1 µH+10 µF filter −39 dB under;
  filter Z peak 4.35 Ω → 0.45 Ω with 0.5 Ω+47 µF (converter −R 19 Ω); AF(6 dBi) 13.8/17.0/24.2 dB/m @300/433/1000 MHz; −85 dBm @400 MHz
  → 39.3 dBµV/m; FCC 46 → 6.7 dB margin; fixed 1 m height under-reads 3.3 dB @100 MHz, 4.3 dB @500 MHz.
  s16_mesh_shielding.py ALL PASS: insect screen 65/53/46/40/38/30 dB at 0.1/0.433/0.915/1.8/2.45/5.8 GHz; ¼" cloth 46…11; chicken wire
  28/15/9/5/3/1; log form invalid for fat wires (a/2πr<3). Fabric 0.05 Ω/sq 71.5 dB, 1 Ω/sq 45.5 dB; foil > 114 dB. Seams 50 mm: 17 dB
  @433, 4 dB @1.8 GHz. Phone needs 44–74 dB. SDR cage test: 113 dB measurable with 100 Hz bins, 30 dB pad substitution.

- 2026-10-13 — DONE page edit 13/emc-emi-fundamentals: new sections '## EMC standards and transients for avionics' (G-13-01) and
  '## Conducted and radiated pre-compliance' (G-13-03 part 1), TL;DR, questions, design rows, 8 common mistakes, verify, gaps, sources 11–27.

- 2026-10-13 — DONE 19/certification: '## Radio test modes and the lab day' (G-13-03 part 2) + TL;DR bullet, 2 questions, mistake, gap, source 8.

- 2026-10-13 — DONE 13/mixed-signal-layout: '## Termination and crosstalk budgets for SPI and clocks' (G-13-02) + TL;DR, 4 questions, 6 design rows, 5 mistakes, verify, gaps, sources 9–12.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| 1 | Com-Power MIL-STD-461 tech note (PDF, pdftotext) | vendor | 461G method ranges, LISNs | marketing summary |
| 2 | Interference Technology: Intro to 461G; CS115/RS105 review; RS101–RS103 | trade | G changes, CS115 2 ns/30 Hz/1 min, RS105, RS103 levels range | secondary |
| 3 | Solar 9355-1 datasheet; VectorNav primer | vendor | CS115 5 A / 30 ns | 461D/E-era |
| 4 | ATEC / TÜBİTAK CS116 notes (search summaries) | lab | CS116 frequencies, pulse rate | Imax curve not obtained |
| 5 | Wikipedia DO-160; ATEC/TÜV/Applus DO-160 pages | encyclopedia/lab | section list, §16/§20/§21 notes | cross-checked |
| 6 | AVI3000, Holt HI-8450 report, IT DO-160 articles | vendor/trade | §22 WF3/4/5A, sets | level tables not obtained |
| 7 | AMETEK EFT; TI blog | app note | IEC 61000-4-4 | 2 sources |
| 8 | Wikipedia IEC 61000-4-5; TI AN | encyclopedia/app note | surge waveform, 2 Ω, classes | 12/42 Ω from knowledge |
| 9 | TI SLYY202; I.B.L. glossary | app note/lab | CISPR 32 limits | 3 m values not confirmed (derived +10.5 dB) |
| 10 | TekBox 5 µH LISN manual; TI SLLA569 | vendor | CISPR 25 AN, 20 cm rule | |
| 11 | TestEquity/Tequipment TekBox listings | retail | kit prices 2026-10-13 | prices change |
| — | Textbooks from knowledge: Ott 2009, Paul, Bogatin 2018, Johnson & Graham 1993, Paul MTL 2008, Marcuvitz 1951, Casey 1988, Middlebrook 1976, LT AN88 | textbook/paper | formulas | all formulas re-derived and checked by script |

## Contradictions / discrepancies found
- Crosstalk closed forms (Bogatin-style NEXT ∝ ℓ/L_sat, FEXT ∝ TD/t_r) match FDTD only when t_r is the linear-ramp (0–100 %) duration;
  with the 10–90 % time they read ≈ 20 % high below saturation. Stated on 13/mixed-signal.
- W5-E11's 13/digital-termination page: K_b agrees (< 2 %); ℓ_sat 83 mm there vs 86 mm here (4 %, assumed v). Noted on the page.
- Johnson–Graham 1/(1+(D/h)²) predicts 3.35× NEXT drop from 0.2 → 0.6 mm gap; field solver gives 3.88×. Fine for ranking.
- TI blog gives EFT repetition "2–5 kHz" vs 5 kHz / 100 kHz elsewhere — used the standard's 5/100 kHz.
- CISPR 25 AN described in one source as "5 Ω + 1 µH" vs (5 µH + 1 Ω)‖50 Ω in vendor docs — used 5 µH.

## Knowledge gaps noticed (for later gap-filling)
- MIL-STD-461G/H and DO-160G primary texts not read (403/parse errors): CS116 Imax curve, RS103 Table XI, CS118 levels, DO-160 §22 level
  tables, and 461H changes are open. CE101/CE106/RE101/RE103/RS101 ranges from knowledge.
- ESP32-S3/Teensy output impedance and edge rate per drive strength unpublished → measure (candidate §7 real-world-data row).
- Real flight-computer measurements wanted: pyro turn-off drain waveform, LiPo hot-plug overshoot through the real arming switch,
  DIY box SE with the SDR recipe (all described as tests; results belong on the pages as dated addenda).
- EBYTE E22/E220 undocumented test/CW command — unverified.

## Cross-domain notes (things other domains should cover/link)
- 13/_index (not edited by me): the four pages' rows could mention the new sections (standards/transients, pre-compliance, SPI budget,
  enclosures/meshes). 17/interference-hunting line 241 "LISN-based conducted-emission measurement (see EMC pre-c…)" can now point to
  13/emc-emi-fundamentals#conducted-and-radiated-pre-compliance.
- 17/lab-setup-by-budget could list the EMC pre-compliance kit (TekBox LISN/limiter/current probe prices on 13/emc page).
- 01/transient-and-step-response snubber rule is now worked out in 13/emc §standards (link back would help).
- Note: running `tools/build_index.py --help` rebuilt INDEX.md/FAQ.md (the script ignores --help); 0 broken links reported.

## Resume instructions
Task complete — nothing to resume. (Historic notes below.)
PAUSED (2nd) after two scripts. To resume: skip s16_crosstalk/s16_snubber (done). Remaining scripts: s16_precompliance.py,
s16_mesh_shielding.py. Then page edits + GAP_REGISTER closure. Original steps: (1) re-read this log, the four target pages and GAP_REGISTER §5 (last C-row was C79 at pause
time — re-check). (2) Write scripts: s16_snubber_transients.py (RC snubber via ring-halving: f0 → Cpar = Cadd/3, L, R = √(L/C), Cs = 3–4×Cpar,
P = CV²f; pyro FET turn-off spike I·√(L/Coss); solenoid decay diode vs zener t = (L/R)ln(1+IR/(Vz+Vf)); hot-plug ceramic-cap overshoot ≈2×Vbat
with damping; surge/EFT energy into TVS), s16_crosstalk.py (reuse tools/verify/tline_fd2d.py Geometry/solve_energy for coupled microstrip on
JLC04161H-7628 h = 0.2104 mm εr 4.4: Lm/L, Cm/C, kb, kf, Lsat = v·tr/2, grounded-guard case; Bergeron line sim for unterminated/series/
parallel/Thevenin/AC termination), s16_precompliance.py (LISN Z vs f, buck DM emission vs CISPR 32/25, AF = 20log f − G − 29.77, distance
scaling, RBW correction), s16_mesh_shielding.py (wire-mesh |T| ≈ 2(a/λ)ln(a/2πr), sheet SE = 20log(1+η0/2Rs), screw-pitch seam SE, phone
link-margin budget, SDR cage-test dynamic range with attenuator substitution). (3) Then add the sections named below. Earlier note:
If interrupted: check which [ ] items above are done by grepping the target pages for the new section headings
("EMC standards and transients", "Conducted and radiated pre-compliance", "Termination and crosstalk budgets",
"Enclosures, doors, meshes and fabrics"). Scripts in tools/verify/s16_*.py; run each and paste outputs into the pages.
Then close GAP_REGISTER rows (next free C-number: check the last §5 row first).
