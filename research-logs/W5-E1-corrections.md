# Research log W5-E1: corrections (regulatory, radar-band, crystals caveat, D1 myths, cross-domain notes, links)
Status: complete (2026-10-02)
Owner scope: edits to finished domains 00–12, 14, 15, 17, 19 ; tools/verify/fix_*.py ; gaps/W5-E1-deferred.md ;
INDEX.md/FAQ.md via tools/build_index.py. NOT editable: 13, 16, 18, 20, 21 (defer to gaps/W5-E1-deferred.md).

## Plan (tick as done; record file + section)
### Fix 1 — regulatory corrections to domain 15 (W3-C5 X1–X13)
- [x] X1 ism-band-plans: TS SRD Issue 1 Rev 3 date → Sep 2023
- [x] X2 ism-band-plans: 917–925 MHz Exemption Notification 500 mW vs TS SRD 30c 100 mW/1 % conflict; TS SRD binding
- [x] X3 ism-band-plans: "domain 19 must confirm" → resolved licence routes
- [x] X4 ism-band-plans: Meshtastic SG_923 20 dBm into >2.15 dBi exceeds 100 mW e.r.p.
- [x] X5 ism-band-plans: E220 1 MHz grid cannot reach EU 869.40–869.65 MHz
- [x] X6 ism-band-plans: EU legal source → Decision (EU) 2025/105
- [x] X7 lora-modules: 866–869 MHz (CH16–18) 500 mW alternative
- [x] X8 lora-modules: E22-400T33D Singapore legality warning (10 mW e.r.p.)
- [x] X9 ism-band-plans: US 97.303(n)(2) + IREC SBP Rev D limits
- [x] X10 ism-band-plans: Australia LIPD 2025
- [x] X11 ground-station-design: link 19 rf-exposure + lab-safety (LNA overload)
- [x] X12 rocket-telemetry-radio-design: pyro/RF interaction test → 19/lab-safety
- [x] X13 ism-band-plans: 433 ISM Region 1 only
- [x] Link budgets in 15 show legal licence-exempt vs licensed case — DONE (lora-sensitivity Ex.1–5 labelled + new side-by-side table in Ex.3; rocket-telemetry Ex.1–2; new tools/verify/fix_legal_vs_licensed_link_budgets.py ALL PASS) (lora-sensitivity-and-link-budget, rocket-telemetry-radio-design, ground-station-design, lora-modules)
- [x] 09 link-budget-methodology + 08 rocket examples assuming 2 W @433 MHz: add licence caveat — DONE: 09/link-budget-methodology (TL;DR caveat, Ex. A/B/E), 09/friis Ex.1, 09/two-ray Ex.1; 08/antennas-on-rockets (TL;DR, table note), 08/yagi Ex.4; also 17/rf-bring-up Ex.1, 00/decibels Ex.1, 06/power-amplifiers Ex.1 (TS SRD Table 1-a cross-check), 15/semtech Ex.3
### Fix 2 — 77–81 / 24 / 60 GHz radar in Singapore
- [x] check TS SRD; update 19/singapore-imda-rules + 11/diy-radar-hardware — DONE: 19/singapore-imda-rules (Q list, SRD table row, new 'Radar bands' bullet, src 2 & new src 12); 19/spectrum-allocation (TL;DR, radar table row, src 5–6); 11/diy-radar-hardware (TL;DR, table, new Example 4, mistake, gap, src 8, 18, 19); 11/fmcw-radar, cw-and-doppler, radar-range-equation, sar-and-imaging, _sources, _index (Apr→Sep 2023; 77–81 GHz UWB). 18/phased-array-and-radar-parts deferred (gaps/W5-E1-deferred.md §A)
### Fix 3 — crystals caveat
- [x] 04/crystals-and-resonators: lift medium-confidence caveat; cross-link with 15/lora-impairments both ways — DONE (04: TL;DR '=', §Level-2 bracket replaced by confirmation, open question resolved, related += impairments; 15/impairments: back-link sentence after Semtech's rule)
### Fix 4 — D1 §3 misconceptions (9 ✗ + 8 ◐)
- [x] ✗ higher f penetrates walls better → 09/atmospheric-rain-attenuation — DONE (Q, TL;DR, Level-2 paragraph, mistake, verify, src 9 P.2040-3; tools/verify/fix_penetration_vs_frequency.py ALL PASS)
- [x] ✗ zeroing FFT bins → 14 — DONE (digital-filters mistake 10 + Q + verify + src 1 ch. 8; fft-windows mistake 11; tools/verify/fix_fft_bin_zeroing.py ALL PASS)
- [x] ✗ RC after LNA lowers noise → 06/lna-design — DONE (Common mistakes; Friis 1.23 vs 1.10 dB; noise folding 16 dB)
- [x] ✗ element metal changes resonant length → 08/dipoles-and-monopoles — DONE (mistake; tools/verify/fix_element_metal.py ALL PASS: Cu vs Al 16 µm)
- [x] ✗ chirp phase 2π(f0+kt)t → 11/fmcw-radar — DONE (mistake; numerically checked: wrong form ends at f0+2B)
- [x] ✗ split analog/digital ground planes → already corrected in 13/grounding (W3-C1) — nothing to do
- [x] ✗ via fences around chip antenna → 08/pcb-and-chip-antennas DONE; 13/vias deferred (§B)
- [x] ✗ GPS receivers talk to satellites → 08/gnss-antennas DONE (src 10 Misra & Enge); 21 deferred (§B)
- [x] ◐ longer ¼-wave whip better → 08/dipoles-and-monopoles — DONE (MoM: +5/10/20 % → VSWR 1.6/2.2/4.0)
- [x] ◐ high SWR causes ghosts/ISI on HF receive → 03/reflections — DONE (0.30 µs echo, −18.5 dB)
- [x] ◐ phase noise can be averaged out → 17/phase-noise-measurement — DONE
- [x] ◐ fill every free area with ground copper → 08/pcb-and-chip-antennas entry added; 13 deferred (§B)
- [x] ◐ matching network moves reflection elsewhere → 03/impedance-matching — DONE
- [x] ◐ higher carrier → higher data rate → 10/ber-ebn0-and-shannon — DONE
- [x] ◐ 2.4 GHz water resonance → 19/spectrum-allocation (src 7) + 02/dielectrics — DONE
- [x] ◐ series-R edges only SI → 00/fourier mistake 11 DONE; 13/emc already covers it
### Fix 5 — cross-domain notes of completed logs (W1-*, W2-*, W3-C3, W3-C5, W4-D1)
- [x] triage every note (applied / already done / deferred / not applicable) — table below (DONE 2026-10-02)
### Fix 6 — broken links
- [x] run --check; classify; fix unplanned targets in editable domains; missing template section (19/international Worked example) — DONE: no unplanned targets left in editable domains except W5-E2/W5-E3's own planned pages; 19/international now has 4 worked examples; 0 pages missing sections
- [x] rebuild INDEX/FAQ at end — DONE (227 pages, 41 667 lines, 1938 questions; 27 broken links, all to planned slugs or other agents' planned pages — listed in gaps/W5-E1-deferred.md §D)

## Log (append-only)
- 2026-09-29 — Step 0: read CONVENTIONS, HANDOFF, INDEX (203 pages). Read W3-C5 log X1–X13 and C1–C4;
  extracted cross-domain notes from all completed logs; read D1 §3 (32 myths: 15 ✅, 8 ◐, 9 ✗).
  build_index --check: 97 broken links; all in editable domains point to PLANNED slugs (13/18/20) except
  02/_index and 04/_index → 13/_index.md, 18/_index.md (domain indexes those agents will write) and 16's
  tools/README.md (16 not editable). 19/international-rules-for-competitions lacks a "Worked example" section.

- 2026-10-02 — RESUMED. Scope update from coordinator: 16 and 18 now complete → editable; 13/20/21 still off-limits; 08 being
  extended by W5-E2 (add sections only, no rewrites); new 14/17 pages being written by W5-E3 (don't touch new pages).

- 2026-10-02 — Fix 4 COMPLETE: myths added to 06/lna-design, 08/dipoles (2), 08/pcb-and-chip-antennas (2), 08/gnss-antennas,
  11/fmcw-radar, 03/reflections, 03/impedance-matching, 17/phase-noise-measurement, 10/ber-ebn0-and-shannon, 02/dielectrics,
  19/spectrum-allocation, 00/fourier. New script tools/verify/fix_element_metal.py (ALL PASS). 13 already covers split planes and
  series-R; via-fence/fill-copper (13) and GNSS-one-way (21) deferred in gaps/W5-E1-deferred.md §B. Also applied deferred §A item
  for 18/phased-array-and-radar-parts (+18/_sources) now that 18 is editable.

- 2026-10-02 — Fix 5 DONE: 94 notes triaged (table below); 20 applied as edits (some rows cover several notes) in 07, 08, 10, 11, 14, 15, 16, 17, 18; rest present or deferred (§C of gaps/W5-E1-deferred.md).

- 2026-10-02 — Fix 6 DONE: --check → 29 then 27 broken links; none in editable domains points to an unplanned page except
  W5-E2 (08/slot-antennas → multiband-and-wideband-antennas) and W5-E3 (14/signal-identification → sdr-front-end-protection…,
  17/bench-measurement-recipes) planned pages — left to their owners. 13/_index.md and tools/README.md now exist (earlier
  unplanned links resolved). Added "Worked examples" (4) to 19/international-rules-for-competitions. Linked the 08/gnss myth to
  the new 21 receiver page; refined the 15 harmonic note with 21's band table. All 4 fix_*.py scripts ALL PASS. INDEX/FAQ rebuilt.
- 2026-10-02 — TASK COMPLETE.

## Cross-domain note triage (Fix 5)
| Source log | Note (short) | Target | Action |
|---|---|---|---|
| W1-A1 | D-S causal dielectric model | 02 dielectrics; 13 stackups | already present in both (keyword check) |
| W1-A1 | vector fitting / passivity; openEMS dispersive materials | 16 | present (simulation-validation, python-rf-toolkit; em-solvers covers Debye/Lorentz) |
| W1-A1 | confirm LoRa SNR limits from Semtech DS | 15 | already done by W2-B6 (sensitivity page Table) |
| W1-A1 | 2.15 dBi, Ae, AF 29.77 dB/m consistency | 08 | consistent; AF pointer added in 08/antenna-measurement §E (new) |
| W1-A1 | log-average 2.51 dB, RBW corrections | 17 | present (spectrum-analyzers, phase-noise) |
| W1-A2 | Doppler-rate vs SF12 drift | 15 | present (rocket-telemetry, impairments) |
| W1-A2 | SRD harmonic limits for 01 433 MHz LPF | 19/01 | present (19 Table 1-a; 01 links 19); pass criterion added to 17/playbook §D |
| W1-A2 | SAW IL at 902–928, baluns, PA load-pull | 06 | present |
| W1-A2 | filter layout, inter-inductor coupling | 13 | deferred §C |
| W1-A2 | power-wave vs pseudo-wave S-params | 03 | present (s-parameters) |
| W1-A2 | JLCPCB C0G caps / wirewound inductors | 18 | no passives page — deferred §C (gap) |
| W1-A3 | microstrip Wheeler loss, filling factor | 03 | present |
| W1-A3 | ferrite→magnetic-materials; Medhurst; partial vs loop L | 04 | present |
| W1-A3 | circulators build on Polder tensor | 06 | present |
| W1-A3 | nose-cone, CFRP, near-field detuning; IEEE CP convention | 08 | present |
| W1-A3 | two-ray with R_H/R_V, P.527 | 09 | present |
| W1-A3 | ENIG/OSP, plane-pair resonance, DM/CM, shielding | 13 | keywords present in 13 pages (W3-C1); verify in Wave 6 — deferred §C |
| W1-A3 | openEMS validation exercises | 16 | present (simulation-validation) |
| W1-A3 | far-field range distances, two-length loss a√f+bf, coupon | 17 | present (antenna-range, fixtures) |
| W1-A3 | ICNIRP f/200, FCC Class B | 19 / 13 | present (19 rf-exposure; 13 emc) |
| W1-A4 | causal models, Huray | 02 | present |
| W1-A4 | via L, 0402 Q/SRF, 0 Ω jumper | 04 | present |
| W1-A4 | PA load-pull, LNA noise vs gain, stability circles | 06 | present |
| W1-A4 | small-antenna Q, chip ground, airframe detuning | 08 | present |
| W1-A4 | CPWG fence, soldermask, JLCPCB impedance, launches | 13 | keywords present (vias, stackups, jlcpcb, connectors) — deferred §C for verification |
| W1-A4 | ground-station feeder (coax Ex. 1), masthead LNA | 15 | APPLIED: link added in ground-station Practical notes |
| W1-A4 | VNA cal, port extension, TDR, uncertainty | 17 | present |
| W1-A5 | EBYTE −147 dBm impossible; air-rate map | 15 | present (mapping itself still a gap in 15) |
| W1-A5 | Doppler rate vs drift; HIL ramp | 15 / 20 | 15 present; 20 deferred §C |
| W1-A5 | real LNA noise params | 06 / 18 | present (ATF-54143, 18 lna page) |
| W1-A5 | Y-factor sky-vs-load with SDR | 17 | present (sdr-as-test, noise-figure) |
| W1-A5 | NEC Yagi Ta vs elevation | 08 | deferred §C (W5-E2 is extending 08) |
| W1-A5 | E22 3rd harmonic in GNSS L2; E6 edges | 15 / 20 | APPLIED: 15/rocket-telemetry Practical note (CH 0–2 → GPS L2, CH 4–6 → GLONASS L2, 433.125 → 1299.375 MHz vs E6 edge 1299.21; prefer CH 24); 20 deferred |
| W1-A6 | nose cone/CFRP numbers | 02 | present |
| W1-A6 | IEEE handedness in polarization-mismatch | 09 | present |
| W1-A6 | 15 links to antennas-on-rockets, Yagi | 15 | present |
| W1-A6 | openEMS 2.45 GHz inset patch; nose-cone model | 16 | inset present; nose-cone listed in 16 open questions |
| W1-A6 | antenna-range links antenna-measurement | 17 | present |
| W2-B1 | detectors/LNA noise params/K-μ | 06 | present |
| W2-B1 | phase-noise→jitter, Leeson, tuning-line FM noise | 07 | jitter/Leeson present; APPLIED tuning-line FM-noise paragraph (L = (K_v v_n)²/2f_m², −89 dBc/Hz @10 kHz example) |
| W2-B1 | EMIRR, PA returns, switcher layout | 13 | keywords present (mixed-signal, emc) — deferred §C verify |
| W2-B1 | E220 TX current; crystal vs TCXO | 15 | present (620 mA; impairments) |
| W2-B1 | op-amp/LDO/TVS part tables | 18 | no page — deferred §C (gap) |
| W2-B1 | PSRR injection, 0.1–10 Hz noise, crystal probing | 17 | not present — deferred §C (needs sourced procedures; W5-E3 writing 17) |
| W2-B2 | DBM spurs, limiters, circulators, SAW, couplers | 18 | limiters + SAW present; DBM spur tables, circulators, couplers missing — deferred §C |
| W2-B2 | SX126x RF-pin impedance / reference match; IF/image; abs-max | 15 | image/abs-max partly present; reference match values need Semtech reference-design read — deferred §C (gap) |
| W2-B2 | HB / nonlinear stability workflow | 16 | present |
| W2-B2 | circulator T/R leakage for CW/FMCW | 11 | APPLIED: links + numbers in 11/fmcw (TX leakage) and 11/cw (Practical notes) |
| W2-B2 | 18 JLCPCB SAW parts | 18 | present (filter-parts) |
| W2-B2 | SG 433 rules; ETSI harmonic limits in 06 PA | 19 / 06 | APPLIED (06 PA cross-check vs TS SRD Table 1-a) |
| W2-B2 | inductor SRF/Q, ESL, via L | 04 | present |
| W2-B2 | LNA source vias, shield-can box modes | 13 | deferred §C |
| W2-B2 | SX126x NF; GS LNA placement | 15 | present; APPLIED link to 06 LNA Ex. 5 in ground-station |
| W2-B2 | Y-factor, oscillation hunting | 17 | present |
| W2-B3 | consistency of LoRa SNR | 15 | consistent |
| W2-B3 | 14 RRC/polyphase/Farrow/demod; reference comms_*.py | 14 | topics present; APPLIED comms_*.py references in 14/software-demodulation |
| W2-B3 | crystal/TCXO g-sensitivity | 04 | present |
| W2-B3 | ISM FHSS/DSSS/LoRa dwell, AS923 | 19 / 15 | present |
| W2-B3 | radar pages link matched-filter-detection | 11 | present |
| W2-B3 | fade statistics, roll nulls | 09 | present (link-margin-availability, polarization) |
| W2-B4 | 12 pages linked from 11 | 12 | present |
| W2-B4 | 14 windows/IQ/hardware | 14 | present |
| W2-B4 | 20 fmcw-radar-build | 20 | deferred §C |
| W2-B4 | GS az/el mount could host radar | 15 | not applied — already covered by 11/diy rocket-tracking option 3 linking ground-station |
| W2-B4 | 19 radar bands; 77–81 GHz absent | 19 | APPLIED (Fix 2: UWB exemption) |
| W2-B5 | 20 phased-array-starter, tracking-yagi kinematics | 20 | deferred §C |
| W2-B5 | phase shifter/beamformer IC list | 18 | present (phased-array-and-radar-parts) |
| W2-B5 | EEP and REV measurement recipes | 17 / 08 | APPLIED: new 08/antenna-measurement recipe §E (EEP, active Γ, AF; Pozar 1994) + pointer in 17/antenna-range open questions |
| W2-B5 | Floquet unit-cell recipe | 16 | APPLIED as open question in 16/openems-workflow (support not verified) |
| W2-B5 | N-port S, active reflection | 03 | present |
| W2-B6 | crystals caveat | 04 | APPLIED (Fix 3) |
| W2-B6 | 19 IMDA classes, amateur route, legality | 19 | done by W3-C5; 15 corrected (Fix 1) |
| W2-B6 | gr-lora_sdr workflow ↔ ground-station | 14 | present |
| W2-B6 | 20 recipe reuse budgets | 20 | deferred §A/§C |
| W2-B6 | LNA/SAW for 433 & 917–925 with > 925 MHz rejection | 18 | present (filter-parts) |
| W2-B6 | 07/09 consistency | 07/09 | consistent |
| W2-B7 | 10 link to discriminator-loss simulation | 10 | APPLIED (10/_index Known gaps; digital-modulation Open questions) |
| W2-B7 | 05 data-converters → 14 sampling | 05 | present |
| W2-B7 | 07 → 14 FFT / hardware NFs | 07 | APPLIED (noise-figure-and-friis How to verify) |
| W2-B7 | 15 ground-station: V4L, multirate Ex. 1, software-demod | 15 | APPLIED (ground-station Practical notes) |
| W2-B7 | 15 impairments → 14 software-demod Ex. 3 | 15 | APPLIED |
| W2-B7 | 17 sdr-as-test & NF measurement → 14 scaling | 17 | sdr-as-test present; APPLIED to noise-figure-measurement |
| W2-B7 | 18 adcs / rf-transceiver → 14 hardware survey | 18 | adcs present; APPLIED to rf-transceiver-ics |
| W2-B7 | 12 KrakenSDR cal, NCO coherence, PFB | 12 | present |
| W2-B7 | 11 Pluto FMCW resolution, FPGA chirp | 11 | present |
| W2-B7 | 16 radioconda / SDR++ | 16 | APPLIED as untested note in 16/installing-tools-macos open questions (→ 14 software stack) |
| W2-B7 / W3-C3 | rebuild INDEX/FAQ | — | Fix 6 |
| W3-C3 | IEEE 149 summary | 17 | done by W3-C3 |
| W3-C3 | sleeve-balun dimensions 433/915 | 08 | present (antenna-matching-and-baluns) |
| W3-C3 | 13 planned pages; JLCPCB ε_eff for TRL | 13 | pages now exist; ε_eff for TRL deferred §C |
| W3-C3 | E22 burst current + decoupling | 15 | present (modules Level 3) |
| W3-C3 | harmonic/spurious pass criteria | 19 / 17 | APPLIED (17/playbook §D criterion from TS SRD Table 1-a) |
| W3-C5 | X1–X13 | 15 | APPLIED (Fix 1) |
| W4-D1 | (no cross-domain section; myth list) | various | Fix 4 |

## Resume instructions
TASK COMPLETE (2026-10-02). Follow-ups live in gaps/W5-E1-deferred.md (§A regulatory items for 20; §B myths for 13/21;
§C cross-domain notes for 13/20/21 and new-content gaps in 08/15/17/18; §D links owned by other agents). Verification scripts
written: tools/verify/fix_legal_vs_licensed_link_budgets.py, fix_penetration_vs_frequency.py, fix_fft_bin_zeroing.py,
fix_element_metal.py (all ALL PASS).
