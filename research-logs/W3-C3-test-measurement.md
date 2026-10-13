# Research log W3-C3: 17-test-measurement
Status: complete (2026-09-29)
Owner scope: kb/17-test-measurement/ ; tools/verify/meas_*.py ; this log

## Plan
Order: VNA core first (others link to it), then SA (power/NF/phase-noise lean on it), then the rest.
- [x] vna-fundamentals-calibration (done 2026-09-27, ~260 lines; verified by tools/verify/meas_vna_cal.py §1–13) — architecture, 1-port 3-term derivation, 2-port 8/12-term, SOL/SOLT/TRL/LRM/unknown-thru, cal-kit definitions (offset delay, C0–C3, L0–L3), port ext vs de-embedding, dynamic range, IFBW, averaging, uncertainty, U.FL/SMA planes. Verify with scikit-rf (meas_vna_cal.py)
- [x] nanovna-librevna-practical (done 2026-09-27; verified by tools/verify/meas_nanovna.py) — variants, firmware, ranges/harmonic mode, Saver/App, LibreVNA; recipes (antenna S11 in situ, pi-match tuning, filter S21, cable loss & VF, TDR, SMD fixture); pitfalls
- [x] spectrum-analyzers (done 2026-09-27; verified by tools/verify/meas_sa.py) — superhet, RBW/VBW, sweep time, DANL ∝ 10log RBW, detectors, log-avg bias −2.51 dB, noise/channel power, preamp/atten, internal mixing tests, phase-noise floor; tinySA/Ultra, Siglent/Rigol, SDR SA; LoRa TX power/OBW/harmonics safely. Verify (meas_sa_detectors.py)
- [x] oscilloscopes-and-probing-for-rf (done 2026-09-29; verified by tools/verify/meas_scope_probe.py) — BW/rise time, sample rate/ENOB, probe loading, active/low-Z probes, ground-lead ringing, near-field probes, scope FFT (meas_scope_probe.py)
- [x] rf-power-measurement (done 2026-09-27; verified by tools/verify/meas_power.py) — thermal/thermocouple/diode sensors, avg/peak/burst, couplers/wattmeters, attenuators & ratings, mismatch uncertainty, AD8307/AD8318 modules & calibration (meas_power.py)
- [x] noise-figure-measurement (done 2026-09-29; verified by tools/verify/meas_noise_figure.py) — Y-factor derivation, ENR, noise sources, cold-source/gain method with SA, 2nd-stage correction, SDR NF, LoRa sensitivity with step attenuator (meas_noise_figure.py)
- [x] phase-noise-measurement (done 2026-09-29; verified by tools/verify/meas_phase_noise.py) — direct SA method & limits, RBW/log corrections, PLL / delay-line discriminator, cross-correlation, cheap options (meas_phase_noise.py)
- [x] antenna-range-ota-testing (done 2026-09-29; verified by tools/verify/meas_range.py) — DIY far-field range, ground-reflection range, reference antennas, SDR+turntable pattern, TRP/TIS, rocket telemetry field tests, range-test-by-attenuation (meas_range.py)
- [x] sdr-as-test-equipment (done 2026-09-29; verified by tools/verify/meas_sdr.py) — RTL-SDR/HackRF/Pluto as SA, power meter, gen, NF meter; limits
- [x] signal-generators-and-sources (done 2026-09-29; verified by tools/verify/meas_siggen.py) — lab gens, ADF4351/MAX2870 (harmonics, spurs, filtering), Si5351, tinySA gen, noise sources, attenuators, step attenuators
- [x] lab-setup-by-budget (done 2026-09-29; no script — verification checklist) — tiers S$300 / S$2 000 / S$15 000; used gear
- [x] fixtures-and-deembedding (done 2026-09-29; verified by tools/verify/meas_deembed.py) — SMD fixtures, TRL on JLCPCB, 2x-thru/AFR, reference planes, chip antennas on small boards (meas_deembed.py)
- [x] rf-bring-up-debug-playbook (done 2026-09-29; verified by tools/verify/meas_bringup.py) — step-by-step bring-up; symptom→cause→test tables
- [x] _index.md, _sources.md (done 2026-09-29)

## Log (append-only)
- 2026-09-27 — Step 0: read CONVENTIONS.md, INDEX.md, CLAUDE.md, task spec. No prior log → fresh start. Folder kb/17-test-measurement/ empty. Skimmed 08/antenna-measurement (covers far-field rule, 3-antenna, Wheeler cap, SDR pattern recipe — link, don't duplicate), 03/s-parameters (T-matrix de-embedding already there), 03/reflections (mismatch), 07 NF/phase-noise (theory). 03 TDR and signal-flow-graph pages are planned but not yet written.
- 2026-09-27 — Read sources 1–11 (VNA error models/cal kits; NanoVNA/LibreVNA/V2/LiteVNA/tinySA specs) via curl+pdftotext (raw text, not WebFetch summaries). Scratch copies in scratchpad/w3c3/.
- 2026-09-27 — Wrote tools/verify/meas_vna_cal.py (13 checks, all pass) and kb/17-test-measurement/vna-fundamentals-calibration.md. scikit-rf gotcha: media.line(z0=65) sets PORT z0=65 in skrf 2.x → use DefinedGammaZ0(z0_port=50, z0=65). TRL exactly-180° point singular (skrf residual shape error) → avoid that grid point. MegiQ sells U.FL SOL kit (search listing).
- 2026-09-27 — Sources 12–17 read. Wrote tools/verify/meas_nanovna.py (TDR res/range, Z-method accuracy map, VF/loss from S11, L-match + tolerance, LNA headroom). Writing nanovna-librevna-practical.
- 2026-09-27 — nanovna-librevna-practical.md written (models table, software, recipes A–G, examples). Next: spectrum-analyzers (sources: AN 150, AN 1303, R&S Rauscher).
- 2026-09-27 — Sources 18–19 read. meas_sa.py written (log-avg −2.511 dB MC, ENBW, DANL slope, NF from specs, LoRa chirp peak-vs-RBW, channel power, OBW 132.8 kHz, attenuator chain). spectrum-analyzers.md written. Next: rf-power-measurement (AD8307/AD8318 datasheets, Keysight AN 1449, mismatch uncertainty).
- 2026-09-27 — Sources 20–22 read; meas_power.py (mismatch, diode Bessel-I0 law, two-tone −0.90 dB, log-det cal, duty cycle, coupler directivity, pads); rf-power-measurement.md written. Next: noise-figure-measurement (AN 57-1/57-2).
- 2026-09-29 — Resumed after usage-limit reset (coordinator message). Continuing with noise-figure-measurement.
- 2026-09-29 — Sources 23–26; meas_noise_figure.py run (all sections OK); noise-figure-measurement.md written. Next: phase-noise-measurement.
- 2026-09-29 — Source 27 read (R&S mwrf article and hpmemoryproject 3048 page not retrievable: 60-byte / mod_security). meas_phase_noise.py run OK; phase-noise-measurement.md written. Next: oscilloscopes-and-probing-for-rf.
- 2026-09-29 — Source 28; meas_scope_probe.py OK (Gaussian tr·BW 0.340, 1-pole 0.350, Butterworth-4 0.387, brick-wall 0.446; lead 0.77 nH/mm). oscilloscopes page written. Next: antenna-range-ota-testing.
- 2026-09-29 — meas_range.py (ground-reflection range heights, two-ray vs FSPL table, attenuation method, TRP/TIS integration, RSSI N) OK; antenna-range-ota-testing.md written (no new external sources; IEEE 149/CTIA cited via domain 08/Balanis). Next: sdr-as-test-equipment.
- 2026-09-29 — Sources 29–32; meas_sdr.py OK (IRR formula = FFT sim; cal curve; hop counts; FFT tone power). sdr-as-test-equipment.md written. Next: signal-generators-and-sources.
- 2026-09-29 — Source 33; meas_siggen.py OK; signal-generators-and-sources.md written. Next: fixtures-and-deembedding.
- 2026-09-29 — scikit-rf deembedding docstrings read (IEEEP370 classes live in skrf.calibration.deembedding, not skrf.calibration). meas_deembed.py OK (P370 NZC ≈3 % on 0402 L; ZC variant worse for lumped DUT; open/short exact). fixtures-and-deembedding.md written. Next: lab-setup-by-budget.
- 2026-09-29 — Source 34 (prices); lab-setup-by-budget.md written. Next: rf-bring-up-debug-playbook, then _index, _sources.
- 2026-09-29 — Read ~/.claude/knowledge/space-bar-avionics (design lessons, ethos, HIL/bring-up, Avionics B: E22-400T33D is 2 W/33 dBm, ZED-F9P active antenna). meas_bringup.py OK; rf-bring-up-debug-playbook.md written. Next: _index.md, _sources.md, final checks (links, front-matter), INDEX rebuild? (tools/build_index.py is shared — do not run unless allowed; note for orchestrator).
- 2026-09-29 — _index.md (reading order, pages table, FAQ with verified anchors, scripts, gaps) and _sources.md (51 entries, read/summary/cited tags) written. Added missing "Design equations & rules of thumb" sections to lab-setup and playbook. All 12 meas_*.py scripts re-run OK. Status → complete.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| 1 | D. Rytting, "Network Analyzer Error Models and Calibration Methods" (slides, emlab.uiuc.edu mirror) | seminar notes | 1-port 3-term bilinear form + linear-in-e form, 12-term formulae & cal steps, 16-term, 8-term T-matrix, TRL/LRM/TXYZ/UXYZ standard counts, unknown-thru det trick, residual table (APC-7 18 GHz: OSL fixed −40/−35 dB, sliding −52/−41, TRL −60/−60, TRM −40/−40) | read raw PDF via pdftotext |
| 2 | Agilent AN 1287-3 "Applying Error Correction to Network Analyzer Measurements" 5965-7709E (2002; umd mirror) | app note | response/enhanced-response/2-port cal, adapter VSWR 1.5 → ~14 dB effective directivity, worked uncertainty (8753D: ±0.5 dB refl, ±0.05 dB trans for 1 dB/16 dB RL filter), TRL vs TRL*, swap-equal-adapters, adapter removal (length within λ/4) | read raw |
| 3 | Keysight 5989-4840 "Specifying Calibration Standards and Kits" (ucsb mirror) | app note | offset delay/loss (GΩ/s)/Z0 definitions, C0..C3 units 1e-15/1e-27/1e-36/1e-45, L0..L3 1e-12/1e-24/1e-33/1e-42, TRL class table (line phase ≥ ±20° from thru), offset-load ≥ 20° separation | read raw |
| 4 | Copper Mountain "VNA master class – calibration, kits, error terms" (B. Walker) | vendor seminar | SOLR (unknown thru) recommended, open C polynomial example (T4311: 28.353 ps, C0 −4.3 fF…), least-squares overdetermined 1-port | read raw |
| 5 | nanovna.com home page | vendor/community | original NanoVNA 50 kHz–300 MHz, Si5351 odd-harmonic to 900 MHz, 40 dB DR @ 900 MHz, H rev3.4+ 40 dB to 1.5 GHz, 2.7 GHz fw with large noise; "2.7 GHz NanoVNA plus usually fake"; NE602 replacement in H v3.7 / H4 v4.4 | raw curl |
| 6 | hugen79/NanoVNA-H README | vendor | >70 dB DR 50k–300 MHz direct Si5351 output; odd harmonics to 900 MHz | raw |
| 7 | Retailer listings (Radioddity etc.) for H4 DR table | retailer | >70 dB (50k–300M), >60 dB (300–900M), >40 dB (0.9–1.5G); port SWR <1.1 | secondary; consistent with nanovna.com |
| 8 | LibreVNA README + specsheet.pdf (jankae) | vendor/open-source | 100 kHz–6 GHz (8 GHz harmonic), −40…0 dBm, DR table (5–2940 MHz S21 85/105 dB), IFBW 10 Hz–50 kHz, resistive bridges, 2 receivers, 1st IF 60 MHz, 2nd 250 kHz, ADC 16 bit 800 kHz; SA mode −103 dBc/Hz @1 GHz 10 kHz | raw |
| 9 | nanorfe.com NanoVNA V2 page | vendor | V2_2 50k–3 GHz, Plus4 50k–4.4 GHz, DR 60 dB (V2_2) / 90 dB Plus4 AVG20 1 GHz / 80 dB 3 GHz; S11 noise floor −50 dB <1.5 GHz, −40 dB <3 GHz; no harmonics; Plus4 Pro adjustable IF | raw |
| 10 | zeenko.tech LiteVNA page | vendor | 50 kHz–6.3 GHz, single mixer + RF switches | raw |
| 11 | tinysa.org wiki Specification (Basic and Ultra) + Limitations | vendor wiki | full spec lists (see page) | raw |
| 12 | NanoVNA-Saver README (github NanoVNA-Saver) | open-source docs | features: segments >10k pts, averaging, cal with non-ideal standards (no load C), TDR, filter analysis | raw |
| 13 | DiSlord NanoVNA-D README | open-source docs | firmware for H/H4 (F072/F303), DFU flashing, companion tools (NanoVNA-App by OneOfEleven) | raw |
| 14 | nVhelp (oristopo.github.io) via WebFetch | community docs | NanoVNA output: 10 MHz −12.13, 50 MHz −12.57, 100 MHz −13.21, 200 MHz −14.85, 300 MHz −7.92 dBm; >300 MHz boosted Si5351 3rd harmonic | WebFetch summary (quoted numbers) — medium |
| 15 | groups.io / hugen79 issue #18 (search snippets) | forum | Si5351 drive 2 mA <300 MHz, 8 mA above; 8 mA nonlinearity in harmonic mode; ~10–13 dB drop above 300 MHz | forum — anecdotal |
| 16 | Agilent AN 1287-12 "Time Domain Analysis Using a Network Analyzer" (qsl.net mirror) | app note | Table 1-3: LP step 0.45/0.99/1.48 ÷ span, LP impulse 0.60/0.98/1.39, BP impulse 1.20/1.95/2.77; alias-free range = 1/Δf × vf × c | read raw |
| 18 | Keysight AN 150 "Spectrum Analysis Basics" 5952-0292 (2016; electrooptical.net mirror) | app note | ST = k span/RBW² (k 2–3), noise-as-signal (Rayleigh 1.253σ, 0.886σ → 1.05 dB; log 2.5 dB; ENBW 1.05–1.13; total corrections +0.55/+2.0/−0.5), NF_SA(N) definition & example (−110 dBm/10 kHz → 26.5 dB), internal distortion slopes, preselector | read raw |
| 19 | Siglent SSA3000X Plus datasheet DS0703P-E04B | datasheet | DANL tables (SSA3021X Plus: preamp off −135/−139 typ 0.2–1.5 GHz; on −155/−158; 10–200 MHz on −156/−161 typ), phase noise 1 GHz −95/−98 @10k, −115/−117 @1M, SHI +45 dBm, TOI +14 (typ), P1dB >0 dBm, abs ±0.7 dB (±0.4 typ), max avg +30 dBm, damage +33 dBm | read raw |
| 20 | AD8318 datasheet Rev B (octopart mirror; analog.com timed out) | datasheet | 900 MHz: −24.5 mV/dB (−26…−23), intercept 22 dBm (19.5–24), ±1 dB range 57 dB, ±3 dB 65 dB; 1.9 GHz −24.4 mV/dB / 20.4 dBm; abs max input +12 dBm; ±0.5 dB over temp; 10 ns response | read raw |
| 21 | AD8307 datasheet (foxdelta mirror) | datasheet | −75…+17 dBm, 92 dB ±3 dB / 88 dB ±1 dB, 25 mV/dB (23–27), intercept −84 dBm (20 µV), ±0.3 dB conformance ≤100 MHz, 1.1 kΩ∥1.4 pF | read raw |
| 22 | Keysight AN 1449-2 Power sensors & instrumentation 5988-9214EN (cloudinary mirror) | app note | diode square law noise→−20 dBm, transition −20…0 dBm, linear above; thermocouple −30…+20 dBm; wide-range diode −70…+20 dBm | read raw |
| 23 | Keysight AN 57-2 "NF Measurement Accuracy – Y-factor" 5952-3706E (qsl.net mirror) | app note | ENR def, Y, eqs 2-14..2-18, 2nd-stage, 6 dB ENR up to NF 16–18 dB, jitter √N, mismatch not correctable | read raw |
| 24 | Keysight AN 57-3 "10 hints NF" (repeater-builder mirror) | app note | preamp, shielding, linearity hints | read raw |
| 25 | SDRangel noise-figure plugin readme (search summary) | open-source docs | Y-factor with ENR tables, 346 family or calibrated low-cost | summary only |
| 26 | Semtech SX1261/2 datasheet (other agent's scratch copy) | datasheet | LoRa sensitivity at PER 1 %, 64 B, preamble 8, CR4/5, CRC, explicit header | read raw |
| 27 | E. Rubiola & F. Vernotte, "The cross-spectrum experimental method," arXiv:1003.0113 | tutorial preprint | ⟨Syx⟩m = Scc + O(1/√m); 5 dB per decade averaging; statistical vs hardware limit; κ=0.1 → m≈5e3 for 0 dB SNR | read raw |
| 28 | Tektronix "ABCs of Probes" primer (download.tek.com) | vendor primer | Tr≈0.35/BW (0.40–0.45 >1 GHz), 3–5× rule (3:1→5 %, 5:1→2 %), probe C table (P6139B 8 pF, TPP1000 12 pF, P6243 ≤1 pF), 500 Ω 10× for 50 Ω, 11 pF + 6-inch lead rings ~140 MHz | read raw |
| 29 | HackRF One docs (hackrf.readthedocs.io) | vendor docs | 1 MHz–6 GHz, 2–20 Msps, 8-bit, max input −5 dBm, TX power table | read raw |
| 30 | ADI wiki ADALM-PLUTO detailed specs | vendor wiki | AD9363 325 MHz–3.8 GHz, 200 kHz–20 MHz, 12-bit, USB ≤4 MSPS no drops, RSSI 100 dB ±2 dB, EVM ≤−40 dB | read raw (TX power table not rendered) |
| 31 | RTL-SDR Blog V4 product pages (search summary) | vendor | R828D, 0.5–1766 MHz, 2.4 MHz stable, 1 ppm TCXO | summary |
| 32 | "Noise Figure Measurements of RTL-SDR Dongles" (IDC-Online PDF) | blog reprint | E4000 @700 MHz: 17.0 dB MDS vs 13.6 dB Y-factor; datasheet ~4 dB | read raw; anecdotal |
| 33 | ADF4351 datasheet Rev 0 (utoronto mirror; analog.com times out) | datasheet | 35 MHz–4.4 GHz, −4…+5 dBm ±1 dB, H2 −19/−20, H3 −13/−10 dBc, VCO PN table, floor −220 dBc/Hz, 1/f −116, PFD spurs −80 dBc | read raw |
| 34 | Price listings (R&L, SeeSii, Siglent NA store, Saelig, rtl-sdr.com) via search | retailer | tinySA Ultra ~US$120–130, Ultra+ ZS406 ~US$187–210, LibreVNA US$600–700, SSA3021X Plus US$1 300 (clearance)–1 733 | search summaries; indicative |
| 17 | LiteVNA User Guide (randl.com PDF) | vendor manual | 50 kHz–6.3 GHz, DR >70 dB <3 GHz / >50 dB ≥3 GHz, S11 floor −50/−40 dB, 10–1001 pts, >550 pts/s; TDR windows normal = Kaiser β6, max = β13 | read raw |

## Contradictions / discrepancies found
- scikit-rf IEEEP370_SE_ZC_2xThru (impedance-corrected) gave a worse result (9.2 vs 9.8 nH, true 10.06) than the NZC variant for a lumped series DUT; ZC is intended for impedance-mismatched fixtures — noted in fixtures page, not a contradiction of sources but a usage caveat.
- RTL-SDR (E4000) noise figure: amateur article measured 17.0 dB (MDS) vs 13.6 dB (Y-factor) vs datasheet ≈ 4 dB — methods disagree by 3.4 dB; recorded in sdr page.
- AN 1287-3 Fig. 14 prints reflection uncertainty "16 dB +0.53/−0.44 dB"; recomputing its own inputs (ΔS11 = 0.0088 on 0.158) gives −0.47/+0.49 dB. Minor rounding/arithmetic; noted in VNA page Example 4.

## Knowledge gaps noticed (for later gap-filling)
- No team measurements anywhere in domain 17: nose-cone antenna S11, attenuation range test margin, flight-computer desense at 433 MHz, GNSS C/N0 vs LoRa TX, AD8318 module conformance at 433/915/1575 MHz, SX126x/SX127x RSSI accuracy vs known levels.
- Not read directly: IEEE Std 149, IEEE 370-2020, CTIA OTA test plan, Engen & Hoer 1979, Ferrero & Pisani 1992, HP 11729B/C phase-noise product notes, Keysight AN 57-1, AN 1303, AN 1449-3.
- Unverified specs: NanoVNA-H/H4 CH1 input match and absolute max input; DiSlord point limits (101/401); Pluto TX power (ADI table not rendered); RTL-SDR V4/HackRF/Pluto noise figures; budget-scope FFT SFDR; MAX2870 specs; E22-400T33D burst current; Bird-43 accuracy; used-equipment prices.
- Cheap noise-source modules: ENR uncalibrated — calibration campaign against 346B or hot/cold load would make them usable.
- Real-time/FFT analyzers, vector signal analysis (EVM, LoRa demod quality), and VNA cold-source NF not covered in depth.

## Cross-domain notes (things other domains should cover/link)
- tools/build_index.py was NOT run (shared INDEX.md/FAQ.md outside my scope) — orchestrator should rebuild INDEX/FAQ to pick up 13 new pages + rf-bring-up-debug-playbook (already in taxonomy).
- 08-antennas/antenna-measurement.md "Open questions" asked domain 17 to summarise IEEE 149 range design: done at first-principles level in antenna-range-ota-testing (ground-reflection range h_r = λR/(4h_t)); IEEE 149 still not read.
- 08: sleeve-balun dimensions for 433/915 MHz test cables should be computed/verified (fixtures page defers to 08).
- 13-pcb: pages linked but not yet existing at time of check: connectors-and-launches, emc-emi-fundamentals, jlcpcb-rf-manufacturing, mixed-signal-layout, rf-pcb-review-checklist (all planned). JLCPCB-specific ε_eff for TRL line lengths should come from 13/stackups (17 uses 3.0–3.3).
- 15-lora: required-SNR thresholds (−7.5/−12.5/−20 dB) and LoRa frequency-offset tolerance are used/linked; E22-400T33D (2 W) burst current + decoupling should be documented in lora-modules page.
- 19-regulations: harmonic/spurious limits for LoRa TX test pass criteria (IMDA/ETSI/FCC) — playbook links certification page for limits.
- 03: time-domain-reflectometry and signal-flow-graphs-mason pages are linked from 17 (VNA/NanoVNA pages).
- Space Bar knowledge base: flown telemetry radio is EBYTE E22-400T33D (433 MHz, 2 W/33 dBm) — test-gear protection numbers in playbook use it. If the team adopts a new radio, update playbook §4.

## Resume instructions (what the next agent should do if this one is interrupted)
- Read this log's Plan + Log. Pages marked [x] are done; check kb/17-test-measurement/ for partially written pages (look at the last section present).
- Continue with the first unchecked page in Plan order. Sources already fetched are in the table (don't re-fetch unless a number is needed).
- Verification scripts go in tools/verify/meas_*.py; run them and quote outputs in the pages.
- 2026-09-29 FINAL state: all 13 pages + _index.md + _sources.md written; 12 scripts tools/verify/meas_*.py all run OK; template sections and front-matter checked; relative links checked (only planned-but-unwritten domain-13 targets missing); _index anchors checked. Task complete — nothing left to resume except the gaps above.
- Raw source texts (pdftotext) were in session scratchpad …/scratchpad/w3c3/ (may be gone in a new session; re-download from URLs in the sources table if needed).
