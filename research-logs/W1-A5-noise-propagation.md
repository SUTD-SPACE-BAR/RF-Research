# Research log W1-A5: 07-noise-linearity + 09-propagation-link-budget
Status: complete
Owner scope: kb/07-noise-linearity/, kb/09-propagation-link-budget/, research-logs/W1-A5-noise-propagation.md,
tools/verify/noise_*.py, tools/verify/prop_*.py

## Plan
Order: verification scripts that produce worked-example numbers first (so pages cite verified numbers),
then pages roughly in dependency order, then _index.md/_sources.md for both domains.

### 07-noise-linearity
- [x] thermal-noise-and-noise-temperature — DONE (kb/07-noise-linearity/thermal-noise-and-noise-temperature.md) — Johnson–Nyquist (Nyquist 1928 line argument + Planck form), kTB, −174 dBm/Hz, Te, antenna temperature, ITU-R P.372 external noise vs f, lossy passive NF = L
- [x] noise-figure-and-friis — DONE (+ tools/verify/noise_friis_nparams.py) — F/NF/Te, Friis 1944 cascade derivation, LNA-first, cable-before-LNA, SSB vs DSB mixer NF, noise matching (Fmin, Rn, Γopt), noise circles preview
- [x] phase-noise-and-jitter — DONE — L(f), Leeson 1966, integration to RMS jitter, reciprocal mixing, ADC SNR (MT-008/Kester), OFDM EVM, radar; PLL shaping overview
- [x] nonlinearity-p1db-ip3-intermod — DONE — power series, harmonics, compression, P1dB, IP2/IP3 derivation, 9.6 dB rule (and why it fails), IIP vs OIP, IM frequencies, cascaded IIP3, XMOD, AM–PM
- [x] dynamic-range-sfdr-blocking — DONE (+ noise_dynamic_range.py) — SFDR=2/3(IIP3−N), blocking, desense, selectivity, ADC DR, AGC
- [x] receiver-cascade-analysis — DONE (level_diagram added to noise_cascade.py) — full cascade, tools/verify/noise_cascade.py, 915 MHz chain + GNSS active antenna chain
- [x] shot-and-flicker-noise — DONE (+ noise_shot_flicker.py) — 2qI, 1/f corner, mixers, zero-IF, oscillators
- [x] sensitivity-and-mds — DONE — −174+10log B+NF+SNRmin, MDS, LoRa negative SNR, worked examples (E22/E220)
- [x] _index.md, _sources.md — DONE

### 09-propagation-link-budget
- [x] friis-free-space-path-loss — DONE — aperture derivation, FSPL dB forms, "high f attenuates more" misconception, EIRP/ERP
- [x] link-budget-methodology — DONE — template, G/T, Eb/N0; 433 MHz 2 W → Yagi @30 km; 915 MHz 1 W; tools/verify/prop_link_budget.py
- [x] fresnel-zones-los-radio-horizon — DONE — Fresnel radius, 60 % rule, k=4/3, horizon, rocket below horizon on descent
- [x] two-ray-ground-reflection — DONE (+ sections 7-8 in prop_two_ray.py) — derivation, breakpoint, 1/d^4, lobing, polarization dependence, pad
- [x] empirical-path-loss-models — DONE — log-distance, Hata, COST-231, Egli, P.1546/P.1411/P.452/P.528, ITM
- [x] multipath-fading-doppler — DONE — Rayleigh/Rician, K, delay spread, Bc/Tc, Doppler (Mach 3 @433), fade margin, diversity
- [x] atmospheric-rain-attenuation — DONE (+ P.2109 in prop_atmospheric.py) — P.676, P.838, fog, foliage, building penetration
- [x] ionospheric-hf-propagation — DONE — layers, foF2, MUF, skip, NVIS, Faraday, scintillation, GNSS iono delay
- [x] diffraction-knife-edge — DONE — v parameter, P.526 J(v), Deygout/Epstein–Peterson, landed rocket shadowing
- [x] link-margin-availability — DONE — margin vs outage probability, lognormal/Rayleigh combos
- [x] polarization-mismatch-loss — DONE — PLF, lin–circ 3 dB, AR mismatch formula, rocket roll/attitude nulls
- [x] _index.md, _sources.md — DONE

### Verification scripts (tools/verify/) — ALL WRITTEN AND PASSING (2026-09-27)
- [x] noise_thermal.py — Planck vs RJ, kTB table, lossy-line Te
- [x] noise_cascade.py — cascade calculator (gain/NF/IIP3/P1dB) + 915 MHz and GNSS examples
- [x] noise_phase_jitter.py — integrate L(f) to jitter; ADC SNR; reciprocal mixing
- [x] noise_ip3_twotone.py — time-domain two-tone through polynomial; confirm 3:1 slope, P1dB−IIP3 = 9.64 dB
- [x] noise_sensitivity.py — sensitivity for LoRa SF/BW
- [x] prop_link_budget.py — link budget engine + 433/915 examples
- [x] prop_fspl.py, prop_fresnel_horizon.py, prop_two_ray.py, prop_knife_edge.py, prop_empirical.py, prop_doppler_fading.py, prop_polarization.py, prop_margin.py, prop_atmospheric.py, prop_ionosphere.py

## Log (append-only)
- 2026-09-27 — Final pass: ran all scripts (19/19 ok), template/link check passed. Pages are 117-196 lines but 13-28 kB each (dense paragraphs + tables), i.e. below the 250-line guideline by line count, not by content. Status set complete.
- 2026-09-27 — Self-correction: prop_margin.py §2 normalised Suzuki composite to the linear mean; path-loss models predict the median -> now median-referenced (sigma 6 dB, 1 % outage: 24.0 dB; sigma 8: 26.9 dB vs naive 38.6). Lognormal mean exceeds median by sigma^2 ln10/20.
- 2026-09-27 — 09/friis page: caught own error (field-strength constant 74.77 -> 44.77), added numeric check §8 to prop_fspl.py.
- 2026-09-27 — Resumed after rate-limit interruption; wrote remaining 07 pages (shot/flicker, phase noise, nonlinearity, dynamic range, cascade, sensitivity) + _index/_sources; added noise_dynamic_range.py and level_diagram(). Starting 09.
- 2026-09-27 — Wrote + ran 16 scripts. Verified: MC NF vs Friis (0.003 dB), two-tone cascade IIP3 (0.01 dB), cubic P1dB-IIP3 = 9.64 dB (tanh 8.96, cubic+quintic 13.5, Rapp-p2 has no cubic term), phase-noise integration vs numeric vs time-domain synthesis (after fixing a sqrt2 bug in the synthesis), P.676-11 line-by-line reproduces 0.19 dB/km @22 GHz, 14.7 @60 GHz; P.838 regression reproduces Table 5; J(v) approx max error 0.12 dB; AR-mismatch formula = Jones to 1e-15; horizon 4.12 sqrt(h). Found: 433 MHz gas loss 0.0025 dB/km (my initial 0.006 assumption was 2x too high).
- 2026-09-27 — Read S11-S17. Derived: horizontal-pol min effective height at 433 MHz over medium ground ≈ 3 cm vs vertical ≈ 0.44 m → a landed rocket with axial dipole lying flat is H-pol and suffers far more plane-earth loss. Doppler-rate vs Freq_drift_max: SF12/BW125 fails during 10 g boost at 433 MHz. MT-008 fetch timing out repeatedly (use Kester textbook knowledge; mark).
- 2026-09-27 — Read S6 P.838-3, S7 P.676-11, S8 SX1262 Rev2.2, S9 Stüber Hata lecture, S10 Egli wiki. P.527-6 (fetched by another agent) only has figure for legacy ground constants.
- 2026-09-27 — Read S1 P.372-13, S2 SX1262 DS, S3/S4 EBYTE datasheets, S5 P.526-14 (via WebFetch-saved PDFs + pdftotext into scratchpad). MT-008/MT-052 fetch timed out (retry later).
- 2026-09-27 — Read CONVENTIONS.md, INDEX.md, HANDOFF.md; skimmed ~/.claude/knowledge/space-bar-avionics (E22-400T33D 433 MHz 2 W on primary, E220-900T30D 900 MHz 1 W on secondary, ZED-F9P active antenna, MAX-M10S). Created this log.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| S1 | ITU-R P.372-13 (09/2016) Radio noise | standard | Fa def, eq.(1) system noise factor, Pn=Fa+B-204 dBW, Table 1 c/d (city 76.8/27.7, resid 72.5, rural 67.2, quiet rural 53.6/28.6, galactic 52/23; valid 0.3-250 MHz), Tables 2-5 (Europe 425 MHz Fa: city 6, resid 4, rural 3 dB), galactic Tb scaling f^-2.75 | authoritative; newer revisions (-14..-17) exist, check if man-made model changed |
| S2 | Semtech SX1261/2 datasheet Rev 1.2 (Jun 2019) | datasheet | LoRa sensitivity table (SF12/BW125 -137 dBm, SF12/BW10.4 -148, SF7/BW125 -124), SNR table SF5..12 = -2.5..-20 dB, IIP3 -5 dBm, blocking 88/90/99 dB @1/2/10 MHz, CFO tolerance ±25% BW and SF12 ±50 ppm... | implied NF ≈ 6 dB consistent across table |
| S3 | EBYTE E22-400TXXX datasheet (2022) | datasheet | E22-400T33D: SX1268, 410.125-493.125 MHz, 33±0.5 dBm, sensitivity "-147±1 dBm at 2.4 kbps", 2.4-62.5 kbps, tested 16 km (5 dBi, 2.5 m) | sensitivity claim inconsistent with Eb/N0 physics (see Contradictions) |
| S4 | EBYTE E220-900T30D user manual | datasheet | LLCC68, 850.125-930.125 MHz, 30 dBm, -147/-148 dBm "at 2.4 kbps", 10 km (5 dBi, 2.5 m) | same issue |
| S6 | ITU-R P.838-3 (03/2005) rain specific attenuation | standard | gamma=kR^alpha; regression coefficients Tables 1-4; Table 5 values (1 GHz kH 2.59e-5 aH 0.9691; 10 GHz 0.01217/1.2571; 24 GHz 0.1425/1.0101; 60 GHz 0.8606/0.7656; 77 GHz 1.1320/0.7177) | NOTE: WebFetch summarizer returned hallucinated coefficients — always pdftotext |
| S7 | ITU-R P.676-11 (09/2016) gaseous attenuation Annex 1 | standard | line-by-line eqs (1)-(9), Tables 1 (O2) and 2 (H2O) → implemented in tools/verify/prop_atmospheric.py | |
| S8 | Semtech SX1261/2 DS Rev 2.2 (Dec 2024) p.24 | datasheet | Freq_drift_max = BW/(3*2^SF) over packet with LDRO off; 16x with LDRO on; sensitivity table unchanged vs Rev 1.2 | formula read from rendered page image |
| S9 | Stüber, EE6604 Week 7 lecture (Georgia Tech 2019) | lecture notes | Okumura–Hata A,B,C,D, a(hm), COST-231; validity 150-1000 MHz stated | D has -19.33 log f (Rappaport/Hata: +18.33 in L_open form) — likely typo |
| S10 | Wikipedia "Egli model" (cites Egli 1957 Proc IRE 45(10) 1383-1391) | encyclopedia | ratio form PR = GB GM (hB hM/d^2)^2 (40/f)^2 PT | dB constants vary between secondary sources |
| S11 | ITU-R P.531-13 (09/2016) ionospheric effects Earth-space | standard | TEC 1e16-1e18 el/m2; Faraday eq(2) Ω=2.36e-14 Bav NT/f^2 (f GHz); XPD=-20log(tanΩ); group delay 1.345e-7 NT/f^2 s (→40.3 NT/f^2 m); Table 3 max effects at 1 GHz (Faraday 108°, 0.25 µs); S4 ∝ f^-1.5 weak/moderate | |
| S12 | ITU-R P.528-4 (08/2019) aeronautical propagation | standard | 125 MHz-15.5 GHz, heights 1.5 m-20 km AMSL, q 1-99 %, isotropic antennas, LOS two-ray + diffraction + troposcatter; best model for rocket-to-ground | NTIA open-source implementation exists |
| S13 | TTN articles: 702 km (2017) and 832 km (2020) balloon LoRaWAN records at 14 dBm | news (anecdotal) | free-space sanity check of link budget | SF not stated |
| S14 | Meshtastic docs "Range tests" | community docs | 331 km ground record (868 MHz SF12 BW62.5), 206 km balloon (915 LongFast SF11 BW250) | anecdotal |
| S15 | Jha, "3rd-order intercept point" Columbia notes 2006 | lecture notes | power-series two-tone expansion, IIP3 = sqrt(4a1/3a3) | consistent with Razavi |
| S16 | Bullington 1957 BSTJ 36(3) 593-626 "Radio propagation fundamentals" (archive.org text) | peer-reviewed | plane-earth + surface wave, minimum effective antenna height (figure only) | formula for h0 derived myself from small-angle Fresnel expansion |
| S17 | arXiv 2209.00287 "Correction to Friis noise factors" | preprint | claims total F = product of stage-wise in-situ noise factors — a redefinition, not contradiction | preprint, not peer-reviewed |
| S18 | ITU-R P.840-8 (08/2019) clouds and fog | standard | Kl double-Debye eqs (2)-(11); 0.05 g/m3 medium fog (300 m vis), 0.5 thick (50 m) | implemented |
| S19 | ITU-R P.833-9 (09/2016) vegetation | standard | Aev = Am[1-exp(-d gamma/Am)]; Table 1 (St Petersburg): 466.475 MHz gamma 0.12 dB/m Am 18 dB; 949 MHz 0.17/26.5; Am=A1 f^alpha fits (Rio 0.18/0.752, Mulhouse 1.15/0.43, SPb 1.37/0.42) | |
| S20 | É. Dieudonné, A. Kameni, L. Pichon, D. Monchaux, "Radio frequency attenuation by a rocket plume using diffraction theory and finite element modeling," EUCASS 2017, doi:10.13009/EUCASS2017-21 | conference paper (peer-reviewed conf.) | plume attenuation vs look angle: M-V 2nd stage at 85 km, 300 MHz in-flight data (Kinefuchi et al.) ~20-30 dB at small look angle; <5 dB after first minimum; tau_min = 20.97 - 19.03 log f(GHz) deg (0.2-6 GHz) | large launcher, not student motors |
| S21 | ITU-R P.525-5 (11/2024) free-space attenuation | standard | Lbf = 32.4 + 20 log f(MHz) + 20 log d(km) | via search snippet |
| S22 | NTIA ITM page + github.com/NTIA/itm | software doc | ITM 20 MHz-20 GHz, >1 km, free space+diffraction+troposcatter | |
| S23 | ITU-R P.1546-6 / P.1812-7/-8 scope (search snippets) | standard | P.1546 30-4000 MHz 1-1000 km 1-50 %; P.1812 30 MHz-6 GHz, 0.25-3000 km, 1-50 % time, 1-99 % loc, terminals <~3 km | |
| S24 | ITU-R P.2109-2 (08/2023) building entry loss | standard | eqs (1)-(10), Table 1 coefficients (traditional 12.64/3.72/0.96/9.6/2.0/9.1/-3.0/4.5/-2.0; thermally-efficient 28.19/-3.00/8.48/13.5/3.8/27.8/-2.9/9.4/-2.1); 80 MHz-73 GHz data | implemented |
| S5 | ITU-R P.526-14 (01/2018) Propagation by diffraction | standard | Fresnel radius eq (2),(3) R=550 sqrt(n d1 d2/((d1+d2) f)), J(v) exact (30) and approx (31) for v>-0.78, 0.6 R1 clearance, rounded obstacle T(m,n), Bullington, Deygout-type multi edge | authoritative |

## Contradictions / discrepancies found
- C4: Leeson prefactor: FkT/(2Ps) (Leeson) vs 2FkT/Ps (Lee/Hajimiri tank formulation) — 6 dB, definitional (Ps, F meanings), both printed in noise_phase_jitter.py.
- C5 (self-found, fixed): own field-strength constant error (74.77 -> 44.77); own Suzuki normalisation (mean -> median); own phase-noise synthesis sqrt2 bug; own ionosphere hop geometry. All corrected before pages were finalised.
- C2: Egli dB constant for hm>=10 m quoted as 83.9 or 85.9 by secondary sources; the ratio form (isotropic gains) gives 88.0 dB (= 120 - 32.04). 83.9 ≈ 88.0 - 4.3 would correspond to dipole-referenced gains. Report ratio form as primary.
- C3: Okumura–Hata frequency validity quoted as 150-1000 MHz (Stüber) vs 150-1500 MHz (Hata 1980/Rappaport); large-city a(hm) coefficient 8.28 vs 8.29; open-area term 19.33 vs 18.33 (Stüber vs Rappaport).
- C1: EBYTE E22-400T33D and E220-900T30D datasheets state receive sensitivity -147 dBm "at air data rate 2.4 kbps". LoRa needs Eb/N0 ≈ 6 dB (derived from Semtech SNR table: SNR - 10log(SF*CR/2^SF) ≈ 6.1-6.3 dB for all SF at CR4/5). With NF ≈ 6 dB (implied by SX1262 table), S(2.4 kbps) ≈ -174 + 6 + 10log(2400) + 6 ≈ -128 dBm. -147 dBm at 2.4 kbps would need Eb/N0 ≈ -13 dB, below the Shannon limit (-1.59 dB). The -147/-148 figure matches the chip's narrowest-BW SF12 setting (~20-40 bit/s). Treat EBYTE figure as chip best-case, not at 2.4 kbps. Big impact on range predictions (~19 dB, ~9x range).

## Knowledge gaps noticed (for later gap-filling)
- No DEM-based ITM/P.1812/P.528 runs for real launch/landing sites; NTIA ITM/P.528 libraries not wrapped in tools/.
- Plume attenuation for student-scale motors at 433/915 MHz unquantified (only M-V large-stage data).
- LoRa PER vs Doppler-rate unmeasured (only SX126x Freq_drift_max criterion); EBYTE air-rate SF/BW mapping unknown.
- ADI MT-008 / MT-052 not re-read (timeouts): formulas re-derived + verified.
- Installed rocket-antenna co/cross-pol pattern; antenna-antenna isolation at a shared ground station (assumed 30-50 dB).
- Singapore TEC/scintillation climatology, P.453 ducting stats, P.837 rain rates not extracted.
- Quiet-Sun / burst flux at 433/915 MHz and ΔTa for a Yagi (not sourced numerically).
- Modern man-made noise data at 433/868/915 MHz near launch sites / Singapore; check P.372-14+ for revised man-made noise model.
- Effective NF of EBYTE E22/E220 modules (built-in LNA) unpublished — needs Y-factor measurement.

## Cross-domain notes (things other domains should cover/link)
- 15-lora: EBYTE '-147 dBm at 2.4 kbps' claim is physically impossible (Eb/N0 bound); 15 should find EBYTE air-rate -> SF/BW mapping (measure with SDR) and give real sensitivity per air rate.
- 15/20: Doppler RATE during boost vs SX126x Freq_drift_max = BW/(3*2^SF) (x16 with LDRO): SF12/BW125 exceeds limit at ~10 g at 433 MHz; SF10/125 (LDRO off) at ~10 g; recommend SF7-9 or LDRO on for boost telemetry. HIL test with a signal generator ramp.
- 06/18: LNA noise parameters of real parts for 433/915/L1 (illustrative values used here).
- 17: Y-factor / sky-vs-load antenna-temperature measurement with SDR.
- 08: NEC model of Yagi Ta vs elevation over ground; rocket dipole pattern nulls end-on (psi = axis-LOS angle) — 0.5 km GS from pad sees ~ -16 dB pattern loss during vertical ascent.
- 20/15: E22 3rd harmonic of low channels (410.125-412.6 MHz) lands in GPS L2 band (1217-1238 MHz) — relevant if ZED-F9P uses L2; default channel 433.125 MHz -> 1299.4 MHz (clear of L2, just above Galileo E6 upper edge ~1298.75?) — verify E6 band edges.

## Resume instructions
(updated after every page)
- Pages DONE: 07/thermal-noise-and-noise-temperature, 07/noise-figure-and-friis, 07/shot-and-flicker-noise, 07/phase-noise-and-jitter, 07/nonlinearity-p1db-ip3-intermod, 07/dynamic-range-sfdr-blocking, 07/receiver-cascade-analysis, 07/sensitivity-and-mds (all 8 07 topic pages done) + 07/_index.md + 07/_sources.md. DOMAIN 07 COMPLETE.
- Scripts DONE (all run clean): tools/verify/noise_{thermal,cascade,friis_nparams,ip3_twotone,phase_jitter,sensitivity,shot_flicker}.py,
  prop_{fspl,link_budget,fresnel_horizon,two_ray,knife_edge,empirical,doppler_fading,margin,atmospheric,ionosphere,polarization}.py.
  Page numbers must be quoted from these scripts' output (run them; do not recompute by hand).
- 09 DONE so far: friis-free-space-path-loss, link-budget-methodology, fresnel-zones-los-radio-horizon, two-ray-ground-reflection, empirical-path-loss-models, multipath-fading-doppler, atmospheric-rain-attenuation, ionospheric-hf-propagation, diffraction-knife-edge, link-margin-availability, polarization-mismatch-loss (all 11 09 topic pages done).
- 09/_index.md + 09/_sources.md DONE. DOMAIN 09 COMPLETE.
- TASK COMPLETE (2026-09-27). Final verification: all 19 noise_/prop_ scripts run clean; all 19 topic pages have the 11 template sections + front matter; no links to unplanned pages.
- Source texts (pdftotext) are in the session scratchpad (may be lost); key facts are recorded in "Sources consulted" above.
- Final: set Status: complete, write <=250-word report.
