# W5-E1 deferred fixes (for domains 13, 16, 18, 20, 21 — being written by other agents on 2026-09-29)

Written by W5-E1 (corrections pass). Each item: target page → the fix needed → the source/evidence.
The owning agent (or the Wave-6 audit) should apply these and tick them off here.

## A. Regulatory corrections (from W3-C5 cross-domain notes X1–X13 and the W5-E1 77–81 GHz check)

- [x] **18/phased-array-and-radar-parts.md** lines ~41, ~138, ~153 — APPLIED by W5-E1 on 2026-10-02 (18 became editable). "77–81 GHz not listed" is true only for IMDA TS SRD.
  Correct to: 77–81 GHz is licence-exempt in Singapore **as an Ultra-Wideband device** (Exemption Notification
  First Schedule item 17: 77.00–81.00 GHz −3 dBm/MHz; IMDA TS UWB Issue 1, 1 Oct 2016, Table 1: mean e.i.r.p. density
  ≤ −3 dBm/MHz, peak ≤ 55 dBm/50 MHz; §1.2 needs 10 dB BW ≥ 500 MHz; §4.1 excludes fixed outdoor installations).
  See kb/19-regulations-safety/singapore-imda-rules.md (radar-bands bullet) and kb/11-radar/diy-radar-hardware.md Example 4.
- [ ] **20-projects-recipes/lora-rocket-telemetry-link.md** — every link budget should show both the licence-exempt
  case (433 MHz: 10 mW e.r.p. in SG; 866–869 MHz: 500 mW e.r.p.; 917–925 MHz LoRa: 100 mW e.r.p. + 1 % duty) and the
  licensed case (amateur 430–440 MHz ≤ 10 W ERP with IMDA consent; temporary permit), and link
  ../19-regulations-safety/singapore-imda-rules.md. Any "2 W at 433 MHz" budget needs the licence caveat.
- [ ] **20/lora-rocket-telemetry-link.md** — if it moves the E220 to a channel: prefer CH 16–18 (866.125–868.125 MHz,
  sub-band 29, 500 mW e.r.p., no duty limit stated) over 917–925 MHz (100 mW, 1 %); EU 869.40–869.65 MHz is
  unreachable on the E220's 1 MHz grid (nearest 869.125 MHz) — X5/X7.
- [ ] **20/lora-rocket-telemetry-link.md** — add the pyro/RF interaction test (continuous TX near a dummy igniter;
  ≥ 16.5 dB below MNFS per MIL-STD-464C) → ../19-regulations-safety/lab-safety-esd-high-power.md (X12).
- [x] **18/rf-transceiver-ics.md / rf-modules.md** — CHECKED 2026-10-02: rf-modules.md has no E22/E220 rows and already warns against 1–2 W telemetry modules at full power in SG (Common mistakes); nothing to change. Original note — any E22-400T33D/E220-900T30D entry: note the SG
  licence-exempt limits (E22 lowest step 24 dBm is 13.5 dB over 10 mW e.r.p.; E220 needs CH16–18 ≤ 24–27 dBm or
  917–925 MHz ≤ ~20 dBm/1 %) and that §4.1(b) of TS SRD (no user control into non-compliance) makes a 2 W-capable
  module a licence-route device (X8).

## B. D1 misconceptions (gaps/D1-stackexchange.md §3) whose home is a non-editable domain
Status checked 2026-10-02 against the 13 pages W3-C1 has since written:
- [x] "Always split analog and digital ground planes" — now corrected in 13/grounding-and-return-paths.md (Common mistakes, split AGND/DGND entry). Nothing deferred.
- [x] "Slowing edges with series resistors is only about SI" — now covered by 13/emc-emi-fundamentals.md (edge-rate TL;DR and question); W5-E1 also added 00/fourier mistake 11 (433 MHz harmonic −8.7 dB for 0.5→2 ns edges).
- [ ] **13/vias-stitching-fencing.md** — add an explicit Common-mistakes entry "a via fence / ground ring around a chip antenna reduces its noise" (wrong: grounded copper in the reactive region detunes it and cuts efficiency; fix noise at the source; stitch along the feed and the ground edge only up to the keep-out). Antenna-side text already added by W5-E1 to 08/pcb-and-chip-antennas.md (Common mistakes).
- [ ] **13/grounding-and-return-paths.md** — add "fill every free area with ground copper" (◐): good in circuit areas when stitched at ≤ λ/20; wrong inside antenna keep-outs; unstitched islands can resonate. (13/rf-layout-rules already covers "copper pour under the antenna".)
- [ ] **21/gnss-receiver-architecture-acquisition-tracking.md (now exists; pseudorange solution present)** — add an explicit Common-mistakes entry "GPS receivers talk to the satellites" (one-way broadcast, 4 pseudoranges for x,y,z + clock; A-GNSS via separate link). Interim entry added by W5-E1 to 08/gnss-antennas.md Common mistakes (cites Misra & Enge 2006).

## C. Cross-domain notes from completed research logs targeting 13/20/21, or needing new sourced content
(16 and 18 became editable on 2026-10-02; their link-level items were applied directly — see research-logs/W5-E1-corrections.md triage table.)
- [ ] **13** (W1-A2) filter layout: ground vias per shunt capacitor, input/output isolation, inter-inductor coupling — check rf-layout-rules.
- [ ] **13** (W1-A3) ENIG vs ImAg/OSP, plane-pair resonances (100×50 mm → 715 MHz), DM/CM radiation numbers, near-field shielding, JLCPCB per-prepreg Dk — keywords present in 13 pages; verify numbers match 02 (Wave-6 audit).
- [ ] **13** (W1-A4) CPWG via-fence spacing, soldermask effect, JLCPCB impedance ordering/tolerance, U.FL launch capacitance — keywords present; verify vs 03 numbers.
- [ ] **13** (W2-B1) RF rectification/EMIRR in op-amps, PA return-current routing vs sensor grounds, switcher layout spikes.
- [ ] **13** (W2-B2) LNA source-via count/placement; shield-can box modes.
- [ ] **13** (W3-C3) JLCPCB-specific ε_eff for TRL line lengths (17 uses 3.0–3.3).
- [ ] **20/lora-rocket-telemetry-link** (W1-A5, W2-B6) reuse 15 budgets & lora_*.py; Doppler-ramp HIL test; E22 3rd-harmonic channel plan (avoid CH 0–6; prefer CH 24 = 434.125 MHz — see 15/rocket-telemetry Practical notes).
- [ ] **20/fmcw-radar-build** (W2-B4) reuse radar_fmcw.py chirp recipe + ZX95 predistortion; 77–81 GHz UWB conditions.
- [ ] **20/phased-array-starter-build, ground-station-tracking-yagi** (W2-B5) array_diy.py ladder and v/D elevation-rate kinematics.
- [ ] **08 (owner W5-E2)** (W1-A5) NEC model of a Yagi's antenna temperature vs elevation over ground; rocket dipole end-on null −16 dB at a 0.5 km station.
- [ ] **17 (owner W5-E3 / Wave 6)** (W2-B1) PSRR injection measurement (VNA + line injector), 0.1–10 Hz noise measurement, measuring a crystal oscillator without probe pulling — needs sourced procedures (vendor app notes).
- [ ] **18 (gap, new page needed)** (W1-A2, W2-B1, W2-B2) JLCPCB-stocked RF-grade C0G capacitors and wirewound inductors; zero-drift op-amps, low-noise LDOs with MHz PSRR, RF TVS; double-balanced-mixer spur tables, UHF circulators/isolators, SMD couplers/hybrids.
- [ ] **15 (gap)** (W2-B2) SX126x RF-pin impedances and reference-design match/balun values — needs the Semtech reference design BOM; not researched in W5-E1.

## D. Broken links / template issues in non-editable domains
(build_index --check, 2026-10-02: 29 broken links, 0 pages missing sections)
- [ ] 06/lna-design and 07/receiver-cascade-analysis → ../20-projects-recipes/gnss-front-end-design.md — planned slug in taxonomy; OK until 20 writes it.
- [ ] 08/slot-antennas → multiband-and-wideband-antennas.md (×3) — W5-E2's planned page (its log plans to add it to taxonomy.md). Not touched by W5-E1.
- [ ] 14/signal-identification-and-spectrum-survey → sdr-front-end-protection-and-filtering.md, ../17-test-measurement/bench-measurement-recipes.md — W5-E3's planned pages (add to taxonomy.md). Not touched.
- [ ] 20 (ground-station-tracking-yagi, lora-rocket-telemetry-link) → phased-array-starter-build, lna-design-walkthrough, gnss-front-end-design, sdr-receiver-build — planned slugs.
- [ ] 21 pages → rtk-ppp-and-corrections, gnss-interference-jamming-spoofing, gnss-timing-1pps, gnss-error-sources-dop, ttff-agps-almanac-ephemeris (planned) and **sdr-gnss-and-diy-receivers (NOT in taxonomy — W3-C7 should add it or retarget)**.
