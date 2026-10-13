# W5-S18 deferred items (quality pass, 2026-10-13)

Written by W5-S18 (log: `research-logs/W5-S18-quality-pass.md`). These are items S18 found but could not do, either because a running slice owns the page or because no primary source was reachable. Each line gives the page, what is needed, and the owner at the time.

## 1. G-X-01 — pages that need a "Level 1½" rung but were owned by running slices

All of these have a `level: mixed/advanced` page whose `### Level 1` opens with integrals, sums, vectors or matrices. The heuristic count is in brackets. Add the same kind of rung as the 13 S18 pages: a few algebra-only bullets plus one verified worked number, inserted between Level 1 and Level 2. Template: `kb/12-phased-arrays/adaptive-beamforming-doa.md#level-1½--two-antennas-algebra-only`.

| Page | Owner on 2026-10-13 | Suggested bridge |
|---|---|---|
| 16-simulation-tools/em-solvers-fdtd-mom-fem [44] | S11 | FDTD leapfrog as "update E from the curl of H" with a 1-D Courant number example; cells-per-wavelength arithmetic |
| 16-simulation-tools/rf-circuit-simulators-harmonic-balance [12] | S11 | HB as "N harmonics × M nodes simultaneous equations"; one diode at two harmonics |
| 16-simulation-tools/nec-antenna-modelling [8] | S11 (PyNEC section by S17) | point to the new MoM Level 1½ on 08/antenna-simulation-nec-openems |
| 02-electromagnetics/maxwells-equations [24] | S5 (02 domain) | the four laws as "charge makes E, current and changing E make B, changing B makes E", with a 433 MHz displacement-current number |
| 02-electromagnetics/radiation-from-currents-hertzian-dipole [17] | S5 | radiation resistance $80\pi^2(l/\lambda)^2$ with a 5 cm wire at 433 MHz |
| 02-electromagnetics/poynting-vector-power-flow [9], wave-equation-plane-waves-polarization [8] | S5 | E = 377 H, S = E²/377 with a 1 W EIRP at 1 km number |
| 10-comms-modulation/synchronization-carrier-timing [8], matched-filter-detection [3], ber-ebn0-and-shannon [3], digital-modulation-psk-qam-fsk [3] | S8 | Eb/N0 = C/N0 − 10 log Rb arithmetic; matched filter = "correlate with the known pulse"; one BPSK Q-function number from a table |
| 21-gnss/gnss-signals-and-codes [11], sdr-gnss-and-diy-receivers [12], gnss-on-rockets-dynamics-and-limits [7] | S13 (21 domain) | C/A chip 293 m, code-phase → range; Doppler ±5 kHz from 3.9 km/s |
| 15-lora-ism-radios/lora-impairments-doppler-drift-timing [15] | S17 | ppm → Hz → fraction of a LoRa bin at SF12/125 kHz |
| 06-rf-circuits/vco-and-pll-synthesizers [3] | S15 | loop as "phase error × K = correction", N-times-multiplied reference noise (20 log N) |
| 06-rf-circuits/baluns-and-rf-transformers [3] | S14 (complete, but on the orchestrator's do-not-edit list) | CM/DM ratio from 0.5 dB / 5° imbalance |

Unowned pages that were checked and do **not** need a rung, because their Level 1 is already algebra with numbers: 11/fmcw-radar, 11/pulsed-radar-and-pulse-compression, 12/array-factor-linear-arrays, 00/z-transform-and-discrete-time-systems, 00/estimation-theory-ml-map-crb, 00/kalman-filter-and-state-estimation, 00/probability-random-processes-and-psd, 15/lora-phy-css-math, 11/radar-tracking-monopulse-and-trackers. Lower-traffic candidates left for a later pass: 14/iq-complex-baseband (complex exponentials in Level 1), 11/radar-cross-section, 12/beam-steering-grating-lobes.

## 2. G-X-02 — citations not verified or not editable

| Item | Where | Why deferred / what is needed |
|---|---|---|
| Skolnik 3rd ed. section-level ToC (FM-CW altimeter location, RCS table §2.7, SAR "ch. 14") | 11/fmcw-radar ref 17, 11/radar-cross-section ref 1, 11/sar-and-imaging ref 3, 11/_sources T1 (all now flagged) | GBV catalogue ToC (gbv.de/dms/hebis-darmstadt/toc/195384067.pdf) still returned HTTP 429. Read it when it is reachable, then replace the flags with the real section numbers |
| Taub & Schilling 2nd ed. ch. 4; Haykin 4th ed. §2.7 | 00/special-functions-bessel-sinc ref 2, 00/_sources T15 (flagged NOT verified) | no ToC found; the CiNii record BA0046790X may list it |
| Pozar 4th ed. "Table 4.2" number | 00/matrices-and-linear-algebra-for-networks (flagged) | the section numbers are verified, the table number is not |
| Jin 3rd ed. ch. 9 = Absorbing Boundary Conditions | 00/numerical-methods-overview (corrected) | based on search summaries of the publisher sample ToC; confirm from the Wiley sample PDF |
| Orfanidis chapter numbers on 02 pages ("ch. 2, 4–8", "ch. 5–8") | 02/_sources T10, 02/boundary-conditions-reflection-refraction, 02/wave-equation-plane-waves-polarization | 02 is owned by S5. They are consistent with the 2016 ToC (5 Reflection and Transmission, 6 Multilayer Structures, 7 Oblique Incidence, 8 Multilayer Film Applications); only the "checked" annotation is missing. The 2016 vs 2010 numbering is recorded in 08/dipoles-and-monopoles ref 3 |
| Many "cited from knowledge" journal references in 02 | 02/* | owned by S5; these are bibliographic and are not textbook section numbers |
| USB 2.0 §7.1.11 and Maxim AN2141 | 04/crystals-and-resonators ref 15 | owned by S4 |
| 802.11 EVM / DVB-T parameters "from memory" | 10/_index | owned by S8 |
| QucsStudio / RFSim99 / SimSmith status | 16/rf-circuit-simulators-harmonic-balance | owned by S11 |
| RFX2401C, CGH40010F, PD55003 and S2-LP specs "from memory" | 18/lna-pa-gain-block-mmics, 18/rf-transceiver-ics | owned by S13 |
| Murmann ADC-survey range "from memory" | 06/receiver-architectures ref 16 | on the do-not-edit list (S14) |
| IEEE Std 521-2019 HF/VHF/UHF rows "from memory" | 19/spectrum-allocation-ism-bands | a paywalled standard, not a textbook section; needs the standard |

## 3. Orchestrator notes tagged S17/S18 that S18 left to S17

- 07/phase-noise-and-jitter: the Leeson worked example quotes −164 dBc/Hz, but its own FkT/(2Ps) inputs give −167. The page is owned by S17.
- Wi-Fi ch 6 − 2×434.125 MHz IMD onto GPS L1: this belongs in the coexistence rows of 21/gnss-interference-jamming-spoofing and 20/gnss-front-end-design, which are in S17's scope.

## 4. Saleh α_φ — done, nothing deferred

Recorded on 07/volterra-series-and-nonlinear-analysis (Open questions) and 07/_sources.md as **4.0033**. The 4.033 in the IEEE 802.16 slides is a dropped digit. 06/power-amplifiers only names the model and needs no change.

## 5. 0.412 open-end attribution — already correct

03/input-impedance-stubs-quarter-wave (S6-owned) already reads "Hammerstad 1975 as reproduced in Wadell; Qucs implements the 1981 form and Kirschning–Jansen–Koster". The stale note on 03/microstrip-discontinuities was updated. **For S6:** no action needed. If you edit the stubs page, keep the current wording.
- (orchestrator 2026-10-13, from W5-S5) add link from 08/patch-antennas to 03/periodic-structures-ebg (surface-wave suppression / EBG ground planes).
- (orchestrator 2026-10-13, from W5-S6) 03 is now free: apply the 03/_index updates listed in research-logs/W5-S6-lines-matching.md
  (new sections: radial/butterfly stubs, coupled microstrip, offset stripline, RF trace power handling, image-parameter filters,
  open-wire/ladder line) and 03 Level-1½/citation items deferred earlier.

## 6. Status update (W5-S18b, 2026-10-13; log research-logs/W5-S18b-quality-pass-2.md)
**§1 Level 1½: done** on 10/synchronization-carrier-timing, 10/matched-filter-detection, 10/ber-ebn0-and-shannon, 10/digital-modulation-psk-qam-fsk, 21/gnss-signals-and-codes, 21/sdr-gnss-and-diy-receivers, 21/gnss-on-rockets-dynamics-and-limits, 15/lora-impairments-doppler-drift-timing, 06/vco-and-pll-synthesizers, 06/baluns-and-rf-transformers, 02/maxwells-equations, 02/radiation-from-currents-hertzian-dipole, 02/poynting-vector-power-flow, 02/wave-equation-plane-waves-polarization, and the lower-traffic 14/iq-complex-baseband (numbers: tools/verify/s18b_level15_numbers.py, ALL PASS). 11/radar-cross-section and 12/beam-steering-grating-lobes were re-read: their Level 1 is already a formula table with numbers, so no rung was added. **Still open:** 16/em-solvers-fdtd-mom-fem, 16/rf-circuit-simulators-harmonic-balance, 16/nec-antenna-modelling (W5-S11). The heuristic rescan also flags 00/vector-calculus-for-em, 00/matrices-and-linear-algebra-for-networks, 01/network-theorems-max-power-transfer, 01/transformers-coupled-inductors and 00/numerical-methods-overview as candidates for a later pass.
**§2 citations:** USB/AN2141 (04/crystals) done, and the UART "±2 % per side" was corrected to a ±2–3.3 % total mismatch. 802.11 EVM and DVB-T (10) were checked via secondary sources; the 802.11 table number is still unconfirmed. RFX2401C, CGH40010F and S2-LP (18) were checked against their data sheets. PD55003 rests on a product-page summary only. Murmann (06/receiver-architectures) checked against a secondary source. IEEE 521: UHF row still single-sourced. Orfanidis on 02: annotated, and wave-equation ref 10 corrected (polarization is §2.5). The many 02 "cited from knowledge" journal references were checked against Crossref (tools/verify/s18b_citation_check.py). Books not in Crossref are unchanged. **Still open:** the Skolnik 3e ToC (GBV still HTTP 429), Taub & Schilling / Haykin, the Pozar Table 4.2 number, the Jin sample PDF, KDB 558074, and the 16 simulator status (S11).
**§3:** the 07 Leeson item was closed by S17 (06 line updated by S18b). The Wi-Fi IMD rows were left to S17's pages; 21/gnss-interference now links 06/co-site Example 4.
**Orchestrator items:** 08/patch-antennas → 03/periodic-structures-ebg link **done**. 03/_index S6 updates **done**.
- (orchestrator 2026-10-13, after W5-S18b) remaining for 16 once W5-S11 finishes: Level-1½ rungs on 16 pages, simulator-status
  citations, bad anchor in 16/_index (spice-circuit-simulation#a--433-mhz…), NEC→08 MoM rung link. Also Level-1½ candidates in 00/01;
  Skolnik 3e ToC still unverified (HTTP 429).
- 2026-10-14 (W5-S11): 16 items done — Level 1½ rungs on 16/em-solvers-fdtd-mom-fem, 16/rf-circuit-simulators-harmonic-balance, 16/nec-antenna-modelling (numbers: tools/verify/sim2_level15_numbers.py, ALL PASS; NEC rung links to the 08 MoM Level 1½); QucsStudio/SimSmith/RFSim99 status cited on 16/rf-circuit-simulators-harmonic-balance (refs 10–12); 16/_index anchor fixed (D7 #26).
