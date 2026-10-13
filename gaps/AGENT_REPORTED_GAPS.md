# Gaps & contradictions reported by research agents at hand-back (append-only)
Input for Wave 4/5. Full detail lives in each agent's research log.

## W1-A1 (00-math-foundations) — complete
- Contradictions resolved in pages: R&S 1MA98 typos; −174 dBm/Hz at 290 K (KB) vs 293 K (R&S);
  antenna-factor constant 29.77 dB (exact c) vs 29.79 (c = 3e8); 2nd-order peak 1/(2ζ) is |H(jωn)|
  not the true max; unit-square-plate capacitance 0.36679·4πε0L (Maxwell's 0.3607 superseded).
- Gaps: textbook section numbers cited from memory (marked "verify"); no z-transform page, no
  estimation/detection-theory depth, no optimisation page; FR-4 Djordjevic params from one paper
  (may not match JLC laminates); no measured Rician K for rocket-to-ground links.

## W1-A3 (02-electromagnetics) — complete (log items C1–C12, G1–G9)
- Contradictions: μ0 − 4π×1e-7 differs in sign between CODATA 2018 and 2022; CP handedness IEEE vs
  optics (+ e^{jωt}/e^{−iωt} flip); 120π vs 376.73 Ω → 789.0 vs 789.6 Ω dipole-Rr constants; gold
  resistivity 2.21 (CRC) vs 2.44 µΩ·cm (widely copied); Huray roughness geometry ambiguous in source;
  via inductance: Johnson & Graham formula ≈ 2× textbook partial inductance; rise-time "lumped" rules
  differ (Johnson & Graham vs Bogatin); vendor ENIG-loss blogs vs Coonrod measured data.
- Gaps: ENIG Ni resistivity/permeability vs frequency only bracketed; some material values not
  re-fetched from primary datasheets (medium confidence); no data on hand-laid rocket fibreglass εr/
  nose-cone detuning; carbon-fibre conductivity from secondary summaries; Orfanidis & Feynman sites
  403'd (cited at chapter level from knowledge — verify).

## W2-B3 (10-comms-modulation) — complete
- Contradictions: MSK 99% BW — NTIA/ITU table K=1.28 vs analytic/sim 1.18·Rb (unresolved; GMSK rows
  agree); short-block penalty 100→1000 bits: CCSDS 1.3 dB vs normal approximation 1.6 dB (both
  reported); WebFetch summariser produced some wrong facts — primary texts used instead.
- Findings worth surfacing: LoRa ≈ same Eb/N0 as coherent BPSK + K=7 conv code (~6 dB) at equal bit
  rate without PA back-off; LoRa CR 4/5–4/8 buys only ~0–0.4 dB in AWGN.
- Gaps: turbo/LDPC/polar not simulated; choice-guide GMSK-coherent and short LDPC/polar rows are
  estimates; no measured rocket fade data; 802.11 EVM limits & DVB-T carrier counts from memory (verify).

## W1-A2 (01-circuit-theory + 04-real-components-hf) — complete
- Contradictions: MLCC ESL spread ~5× (0.12–0.7 nH) — mount/measurement dependent; C0G upper temp
  +85 °C (older KEMET) vs +125 °C (Murata/EIA); Coilcraft datasheet SRF inconsistent with its own
  L(f) under a one-pole model; SX1261/2 in-packet drift formula is an image — adopted BW/(3·2^SF)
  from secondary summaries (medium) → forwarded to W2-B6 to verify.
- Gaps: no bench data for JLC parts (in-circuit inductor Q, mounted ESL, pad C); elliptic filter
  values fitted numerically, not checked vs Zverev tables; AT-cut coefficients not re-fetched from
  primary source; regulatory harmonic limits for filter example need domain 19.
- Cross-domain finding: Doppler *rate* during boost (~305 Hz/s @915 MHz) exceeds SF12 in-packet drift
  tolerance → use low SF during boost (for 15 and 20 recipes).
- Note: pages are 130–200 lines but long unwrapped paragraphs (13–21 KB each).

## W2-B6 (15-lora-ism-radios) — complete
- Verified from SX1262 datasheet images: in-packet drift limit BW/(3·2^SF) (×16 with LDRO) and ToA
  formula → W1-A2 crystals page's "medium" caveat can be lifted (Wave 5 task).
- Contradictions: EBYTE "−147/−148 dBm @2.4 kbps" physically impossible (≈19 dB optimistic for E22;
  impossible for E220/LLCC68 which lacks SF10–12 @125 kHz); co-SF capture threshold 6/0/~1 dB across
  sources; RFD900x sensitivity disagreement.
- **REGULATORY FLAG (surfaced to user):** IMDA SRD appears to allow 10 mW e.r.p. @433 MHz and 100 mW
  e.r.p. (≤1% duty) @917–925 MHz — E22 (2 W) and E220 (1 W) exceed these; E220 default 873.125 MHz is
  outside SG bands; E22 2nd harmonic 866.25 MHz lands in E220 range. → W3-C5 to rule definitively.
- Gaps: EBYTE air-rate→SF/BW mapping unpublished (SDR measurement procedure given); no rocket packet-
  loss vs acceleration data; LR11xx/LR2021/LLCC68 full datasheets + Doroshkin/Norby papers not read.

## W1-A6 (08-antennas) — complete
- Contradictions: Kraus helix gain formula overestimates 3–5 dB (King & Wong, Emerson NEC, own MoM:
  12.6 vs 16.6 dBic for 10 turns); 73+j42.5 Ω is exactly λ/2 infinitely thin — real wire MoM gives
  80+j45 Ω at λ/2 and 72 Ω at resonance ≈0.484λ; Hansen vs McLean Chu forms; small-loop Rr formula fails
  above ~0.1λ; DL6WU gain estimate ~0.2 dB optimistic; WebFetch fabricated TI DN023 contents
  (pdftotext values used).
- Gaps: no APCP plume attenuation data at 433/915 MHz; nose-cone detuning needs openEMS models of the
  team's hardware; QFH dimensions not numerically verified; IEEE Std 149 and several papers cited via
  secondary sources; MAX-M10S LNA specs missing (integration manual too large to fetch).

## W1-A5 (07-noise-linearity + 09-propagation-link-budget) — complete
- EBYTE "−147 dBm @2.4 kbps" needs Eb/N0 = −12.8 dB < Shannon limit → impossible; physics ≈ −128 dBm.
- Boost Doppler rate at 10 g, 433 MHz exceeds Semtech drift limit for SF12/BW125 and SF10 w/o LDRO;
  SF7–9 fine (consistent with W1-A2 + W2-B6).
- Contradictions: Egli & Hata constants differ across secondary sources; Leeson prefactor quoted 6 dB
  apart; own errors fixed (field-strength constant, mean vs median fade margin, phase-noise synthesis
  bug, HF hop geometry).
- Gaps: no DEM-based ITM/P.528 predictions for real launch sites; plume attenuation unquantified;
  EBYTE air-rate map, module NF/IIP3, LoRa PER vs Doppler rate unmeasured; ADI MT-008/MT-052 unfetchable
  (formulas re-derived + script-verified).

## W2-B1 (05-analog-electronics) — complete
- Tooling: KiCad's bundled ngspice driven via ctypes (tools/verify/analog_ngspice.py) — SPICE netlists
  on pages were actually simulated (forwarded to W3-C2).
- Contradictions/new results: HSMS-285x video-resistance constant 3% off k/q; "square law to −20 dBm"
  holds only for 50 Ω-terminated detectors (matched detector leaves square law ≈ −40 dBm); degeneration
  IIP3 rule (1+gm·RE)^1.5 wrong — exact √8·VT·(1+x)²/√|1−2x| with null at x = 0.5 (derived + simulated);
  1-bit ΣΔ SQNR 4–9 dB below linear formula; Mishra GaN paper SiC values are 6H polytype; own VCO
  phase-noise number fixed (−123 → −103 dBc/Hz).
- Gaps: analog.com timed out (ADI MT tutorials, Kester, Kitchin & Counts cited but not re-read);
  battery Rint, crystal params, FET power densities are representative; missing E220-900T30D TX current,
  igniter no-fire currents, MCU ADC ENOB.

## W1-A4 (03-transmission-lines-matching) — complete
- Own 2-D FD field solver tools/verify/tline_fd2d.py: Cohn stripline 0.13%, vs em_inductance 0.2%,
  Hammerstad–Jensen ≤0.4%.
- Contradictions: small-reflection theory (binomial BW, Chebyshev synthesis, Klopfenstein) optimistic
  by 20–35% ripple at 5:1 ratio (fine at 2:1); JITX/JLC diff widths match only with soldermask; JITX
  single-ended RS_50 0.3244 mm vs KB 0.372 mm bare / 0.343 mm masked (5–13%, unresolved → sent to W3-C1);
  Belden RG-58 Z/C/VF inconsistent ~5%; Fairview RG-316 loss table not √f+f; scikit-rf traps
  (DefinedGammaZ0 default γ = j rad/m; delay() takes round-trip time).
- Gaps: no measured TDR of JLC impedance coupons; no coupled-microstrip closed forms or exact Chebyshev
  transformer tables; EBYTE module source impedance unknown; Times Microwave PDFs 403 (distributor copies).

## W3-C5 (19-regulations-safety) — complete
- **Priority answer (Singapore):** neither module is licence-exempt at rated power. 433 MHz: 10 mW e.r.p.
  (Exemption Notification First Schedule item 13; TS SRD Iss.1 Rev 3 Sep 2023 sub-band 26a) — E22-400T33D
  22.5 dB over at max, 13.5 dB over at its lowest setting. 917–925 MHz LoRa end devices: 100 mW e.r.p.,
  1% duty (30c). 866–869 MHz: 500 mW e.r.p., no stated duty (band under IMDA review) — E220 legal here at
  24–27 dBm. Full-power routes: amateur licence (430–440 MHz ≤10 W ERP, IMDA written consent), temporary
  frequency permit (≤90 days), SUTD experimental licence, localised station licence.
- **Corrections needed in domain 15 (log X1–X13) → Wave 5:** TS SRD issue is Sep 2023 (not Apr 2023);
  Exemption Notification (500 mW) vs TS SRD (100 mW) conflict at 917–925 → treat 100 mW binding; E220 1 MHz
  channel steps can't reach EU 869.40–869.65; cite Decision (EU) 2025/105; 433 MHz is ITU ISM only in
  Region 1 (Singapore permits nationally); add US 97.303(n)(2) (no amateur 900 MHz at Spaceport America —
  IREC "Mode C" band plan contradicts); add Australian LIPD 2025 limits.
- Gaps needing IMDA written rulings: LoRa's 917–925 class; LoRa on 70 cm under amateur licence; whether
  rocket telemetry = "data acquisition" at 866–869. Missing: EBYTE FCC grants, Portugal/Australia amateur
  routes, no-fire ratings of team e-matches.

## W4-D1 (Stack Exchange sweep) — complete → gaps/D1-stackexchange.md
- 6,792 harvested via SE API (exact), 686 classified: 411 covered / 188 partial / 87 missing.
- Top missing: PCB grounding/pours/splits, beamforming/DOA, RF layout & launches (13/12 still being
  written); **GNSS receiver internals (TTFF, A-GPS, 1PPS, update rate) — no domain → new 21-gnss added**;
  spectrum allocation/signal ID/certification; bench test practice; EMC fixes; **antenna types missing:
  slot, lens, random-wire, fan dipole, RFID coils → added to 08 taxonomy**; via fencing; shielding.
- Uncorrected misconceptions: "higher frequencies penetrate walls better" (110k views); "zeroing FFT bins
  is a good filter" (122 votes); 6 more listed in D1 file.

## W2-B7 (14-sdr-dsp) — complete
- Contradictions: NCO spur "6.02 dB/bit" is typical; worst case 6.02P − 3.92 dB (Nicholas & Samueli 1987,
  sim-confirmed); harris 1978 table small misprints (Hamming scalloping 1.75 not 1.78 dB); PySDR says
  RTL-SDR is zero-IF but R820T2/R828D is low-IF ≈3.57 MHz; Pluto USB2 sustained rate 4–12 MS/s across
  sources; Airspy NF vendor 3.5 vs measured 7–8 dB; RTL-SDR Blog V4 EOL → V4L.
- Gaps: no bench data for SDR alias/image rejection, DC spike, IIP3 (→17); MT-002/Heinzel/GNU Radio wiki
  unfetchable (re-derived); hardware prices are Sep-2026 snapshots.
- Covers domain 10's gap on discriminator FSK loss (software-demodulation).

## W2-B2 (06-rf-circuits) — complete
- Verified with real datasheet data (ATF-54143 S+noise params, ADF4351, AFT05MS003N, HSMS-285x): μ/K proofs,
  optimised LNAs (433 MHz 0.38 dB NF; 1575 MHz 0.74 dB), class-E time-domain sim, 2-D FD microstrip, MASH ΣΔ,
  PLL noise budget.
- Contradictions: HSMS-285x voltage sensitivity theory 167 mV/µW ideal (~123 with losses) vs datasheet 40
  (unexplained); Raab 2001 class-F volume 47 vs 49 (believed 49); Edwards&Sinsky vs Pozar K>1 wording only.
- Gaps: ATF-54143 noise params <2 GHz vendor-extrapolated; Sokal finite-Q class-E eqs unfetched;
  large-signal stability only outlined; detector temperature model low-confidence; part tables → 18.

## W2-B4 (11-radar) — complete
- Verified: Swerling 0–4 exact vs MC; Shnidman ≤0.82 dB, Albersheim ≤0.28 dB worst case; CFAR Pfa; full
  FMCW range–Doppler–angle sim + 2-D CFAR; TI SWRA553 Table 1 reproduced; VCO nonlinearity from ZX95-2536C+
  data; Mie RCS; ray-traced corner reflectors; SAR backprojection.
- Contradictions: Hamming scalloping 1.75 vs harris 1.78 dB (same as W2-B7); Marshall–Palmer DSD integrates
  to ≈296R^1.47 not 200R^1.6; Rayleigh/dBZ rain formula overestimates 11–17 dB at 77 GHz; TI SWRA553 Eq.5
  mislabelled (it's velocity resolution, not max velocity).
- Gaps: no measured hobby-rocket RCS; **77–81 GHz absent from IMDA TS SRD? → confirm in 19**; Doppler-module
  NF at audio IF unmeasured; clutter σ0 textbook-level; ADI Phaser ramp/KrakenSDR rate/AWR2944 DDMA unconfirmed
  from primary docs; ω-k SAR, autofocus, non-Gaussian CFAR not simulated; textbooks cited from knowledge
  (all formulas re-derived + numerically checked).

## W2-B5 (12-phased-arrays) — complete
- Contradictions: phase-quantisation lobe worst case ≈ −6.02P + 4.4 dB (matches ADI −7.5 dB @2 bits);
  textbook 1/2^{2P} rule ~4.4 dB optimistic; Butler crossover −3.70 (N=4) to −3.92 dB vs glossary −3.0 dB;
  Dolph broadening formula under-predicts 5–10%; online REV amplitude-ratio formula differs from derivation;
  KrakenSDR price aligned to ≈US$750 (was stale 2023 figure).
- Gaps: Visser, Haupt, Stutzman & Thiele not consulted; several part specs from search summaries only
  (ADAR1000, JSPHS-2484+ read in full); no full-wave FR-4 scan-blindness result; no measured KrakenSDR
  accuracy at 433 MHz; Bayliss taper and Rotman lens described, not implemented.

## W3-C3 (17-test-measurement) — complete
- Verified vs scikit-rf: SOL/SOLT/TRL/unknown-thru/12-term; TRL 20–160° rule; −2.51 dB log-average bias;
  Y-factor + second-stage correction; cross-correlation 5·log m convergence; 2x-thru de-embedding.
- Contradictions: Keysight AN 1287-3 printed ±0.53/−0.44 dB example vs its own inputs → −0.47/+0.49 dB;
  RTL-SDR NF amateur tests 17.0 vs 13.6 dB vs datasheet ~4 dB; scikit-rf impedance-corrected 2x-thru worse
  than plain on a lumped DUT.
- Gaps: no team measurements (examples computed/illustrative); IEEE 149/370, CTIA only via secondary sources;
  unconfirmed NanoVNA CH1 match/max input, Pluto TX power, SDR NFs, E22-400T33D TX burst current; prices rough.

## W3-C2 (16-simulation-tools + tools/rfcalc) — complete
- rfcalc: 12 modules, 142 pytest tests pass (expected values from KB worked examples).
- Sim checks: ngspice 5/5; openEMS microstrip 50.31 Ω (≤0.3% vs 2 methods); openEMS 2.45 GHz patch resonates
  2.2% low; NEC vs own MoM missed 2/8 pre-registered tolerances (reported, not widened); HB demo = transient.
- Tool bugs: PyNEC extended-kernel ignored unless set after geometry close; NEC2++ avg-gain depends on grid
  start; openEMS stops on wall-clock unless exact_endcriteria=True; ngspice-47 `meas … WHEN` crashes in
  S-param runs; SPICE NF wrong at default 27 °C or with noisy load resistor.
- Gaps: no comparison vs measured hardware; many solvers described from docs only.

## W3-C4 (18-components-parts) — complete
- Top picks: SX1268/SX1262 (LoRa), CC1200/Si4463-C2A (FSK), AT86RF215 (SDR-like); LNAs TQP3M9036/PSA4-5043+
  (433/915), BGA524 (GNSS); FEM SKY66423-11/SE2435L + LC harmonic filter; SKY13330 T/R; SAW B39431 (433) /
  B39921 (915); PE43711 DSA; LMX2572/2594, ADF4159 (24 GHz chirps); IWR6843 (60 GHz, SG-legal); JLC RO4350B
  (Dk 3.66 design); MAX-M10S/ZED-F9P; ESP32-S3-WROOM-1U; MHF I LK. All RF parts checked are JLC "extended".
- Contradictions: u-blox limits ≤4 g / 80 km / 500 m/s vs forum 50 km, AND/OR combination undocumented
  (→ forwarded to W3-C7); ADAR2001/2004 are body-scanner Tx/Rx, not beamformers; JLC HF board price US$99.5
  vs "from US$47"; HMC472A 5 vs 6 bit unresolved; Si4463 revision spec differences; TI CC1190 "+6 dB range"
  vs 2.6–4.3 dB computed.
- Gaps: ADI/ST/Qorvo datasheets blocked scripted fetch (medium confidence); no bench data for cheap LNAs,
  AliExpress modules, connector vibration.

## Pause snapshot (2026-09-29)
- W4-D5 (paused, 1326 rows): first KB-wrong item — Leeson prefactor is 6 dB inconsistent between two pages
  (07 phase-noise page vs 05/06 oscillator/VCO pages?) → fix in consistency audit.
- W5-E1 (paused): fixes 1–3 done; 77–81 GHz in Singapore licence-exempt only as UWB device; misconceptions a,b done.
- W4-D2 (paused, 568 Reddit rows C236/P231/M93); background harvest scripts were killed by the orchestrator
  to honour the pause (resumable per agent).
- W3-C6 (paused): 2/10 recipes written; openEMS GNSS-patch sweep process killed by orchestrator — rerun it.
- W3-C7 (paused): research done (S1–S25), 6 scripts pass, 0 pages written yet.
- W5-E2 (paused): slot-antennas written (needs expanding), 4 pages to go. W5-E3 (paused): research ~70%, 0 pages.

## W4-D5 (exams/interviews) — complete → gaps/D5-exams-interviews.md
- 1326 checked (1071 NCVEC pool Qs, 153 interview, 102 problem types): 761 C / 243 P / 321 M / 1 KB-wrong.
- Pass rates (strict/lenient): pools 54/72% (60/79% in-scope); E5 96%; E9 72/87; E4 70/81; G5 90; T9 74/96;
  interviews 69/92; problem types 72/93. **Failing: E3 propagation 23%, G3 27%, G4 30%, T8 30%** → ham-style
  HF/VHF propagation (sunspots, grey-line, Es, ducting, meteor scatter, aurora) & station/operating gear.
- KB-wrong W1: Leeson prefactor — 05/oscillators.md:42,99–101 uses 2FkT/Ps with wrong "both sidebands"
  argument vs 07/phase-noise-and-jitter.md:29,62 and 06/vco-and-pll-synthesizers.md:83 FkT/(2Ps) → 6 dB.
- Top gaps: oscillator ISF/LTV phase noise + microphonics; PA control (ALC, VSWR foldback, T/R sequencing,
  class D); AGC loops + receiver DSP (NB/NR/notch); duplexers/diplexers + crystal IF filters; non-ideal
  Wilkinson & uncorrelated-noise combining; modulator/detector circuits; necessary-bandwidth/emission rules;
  bench instruments (counters, DMMs, scope triggering); transmitter IMD between co-sited radios; array
  pattern synthesis & Yagi stacking.

## W5-E1 (corrections) — complete
- 13 regulatory notes applied to 15; licence caveats on 9 pages in 00/06/08/09/17; legal-vs-licensed link
  budgets side by side (tools/verify/fix_legal_vs_licensed_link_budgets.py).
- **77–81 GHz licence-exempt in Singapore as UWB** (Exemption Notification item 17; IMDA TS UWB: mean ≤ −3 dBm/MHz,
  sweep ≥ 500 MHz); absent only from TS SRD.
- **E22-400T33D channels 0–6: 3rd harmonic in GPS/GLONASS L2 (tracked by ZED-F9P)** → forwarded to C7, C6.
- At 10 mW e.r.p., landed-rocket range ≈1.7 km vs ≈5.6 km licensed; 866–869 MHz best licence-exempt band for E220.
- Possibly still wrong: IMDA class for point-to-point LoRa (100 mW/1% assumed); FMCW mean-density measurement method;
  1947 ISM history Wikipedia-only; P.2040 wall values <1 GHz extrapolated; openEMS periodic BC unverified.

## W4-D4 (curriculum) — complete → gaps/D4-curriculum.md
- 28 sources (19 textbooks + 9 course groups), 1,725 sections: 69% covered / 21% shallow / 10% missing
  (textbooks 68/21/11; courses 79/15/6). Weakest: Kaplan GNSS 44% (pre-21 pages), Hong 51%, Mailloux 52%, Ott 54%.
- Dominant failure: "stated, not derived" (advanced method named + cited in one paragraph).
- Top missing/shallow: radar tracking (monopulse, α-β/Kalman); Kalman/state estimation incl. GNSS/IMU fusion;
  multiple access/ALOHA/duplexing; array pattern synthesis (Schelkunoff, Woodward–Lawson, Bayliss); wideband
  antennas; AGC loop design; pulse-Doppler data cube/PRF regimes; conformal/cylindrical arrays; ground-station
  antenna types + stacking; resonator coupling/cavity perturbation (permittivity measurement); microstrip
  discontinuity models; **z-transform absent**; GNSS coords/orbits/DOP/RTK/A-GNSS (21 in progress); digital
  termination/crosstalk; PA linearisation beyond DPD.
- Level ladder breaks ~10 places (ISF phase noise, Green's functions, z-transform, Volterra, estimation→tracking);
  "Level 1" in advanced domains is a results summary, not beginner maths; no "first radio" beginner project;
  no GLOSSARY.md.
→ W5-E5 launched for estimation/z-transform/tracking/multiple access.

## W4-D2 (Reddit) — complete → gaps/D2-reddit.md
- ~90k posts scanned (Arctic Shift archive + Reddit search RSS; Reddit JSON 403), 695 classified: 43.8% C /
  42.6% P / 13.5% M — practical questions: physics present, the "how-to step" missing.
- Weakest: projects/recipes 0% (20 was unwritten), learning paths 3%, r/sdr 19%, r/RTLSDR 28%.
- Top gaps: RF learning roadmap; book-by-audience; antenna identification guide; signal-ID workflow; beginner
  project ladder; SDR reception recipes (wx sats, ADS-B); RF immunity/interference hunting; choosing/judging
  LoRa antennas; beginner explainers; PCB layout residuals. (→ W5-E6, W5-E2, W5-E3, W3-C1 notified)
- Uncorrected misconceptions: Meshtastic "records" via MQTT bridging; no SDR gain-staging guidance; phantom
  signals from tuner harmonics (half); stock antennas assumed tuned (half); RF feared as ionising (half);
  "never via-fence the radiator" (half).
- Learning-path consensus: Pozar (25 threads), Balanis (15), ARRL Handbook (10); W2AEW, The Signal Path; NanoVNA
  as first instrument; "build something early" (16).

## W3-C7 (21-gnss) — complete
- COCOM/export: no primary u-blox doc states AND vs OR; only u-blox staff answer (u-blox 7 era) → no output above
  500 m/s at any altitude — design for that. Altitude limit 50 km (ZED-F9P HPG 1.00–1.12) → 80 km (HPG 1.13+, M10).
  Current US EAR 7A105 threshold 600 m/s.
- Boost: jerk (not acceleration) breaks PLL — 15 Hz PLL slips at typical ignition; FLL-assisted holds → expect RTK
  float during boost; DLR sounding-rocket data incl. ~100 Hz oscillator offset at 18 g; recommend PPK for trajectory.
- Self-interference: E22 ch 0–3 → 3rd harmonic in GPS L2, ch 5–6 → GLONASS L2 (F9P tracks both) → use ch 23/24;
  25 MHz & 8 MHz clock harmonics hit L1 C/A main lobe; 24/40 MHz hit BeiDou B1I; Wi-Fi − 433/868 intermod lands in L1.
- Integration: u-blox I²C Fast-mode only (explains team lesson); M10S defaults 9600 baud, no flash; RESET_N → cold start.
- RTK link: full RTCM stream ≈710 B/s → needs LoRa SF5–7 @250–500 kHz.
- Gaps: AND/OR needs cabled simulator test; u-blox loop params & E22 harmonic levels unpublished; no SG scintillation data.

## W5-E3 (14/17 additions) — complete
- Pages: 14/signal-identification-and-spectrum-survey, 14/sdr-front-end-protection-and-filtering,
  17/bench-measurement-recipes (E22-400T33D harmonics need ≤ −69 dBc → HPF before SA; ±0.33 dB with power sensor).
- Contradiction: multi-aperture shielding rule −20 log n vs √n variant (flagged as estimate).
- Gaps: measured IIP3 of RTL-SDR/HackRF/Airspy vs gain (cascades assume −10 dBm RTL, unpublished); SAW/cavity
  rejection at SG cellular band-8 (927–935 MHz) — relevant to 915 MHz ground receivers; no team measurements;
  HD Radio/radiosonde/HF-modem catalogue parameters unchecked vs standards.

## W4-D3 (forums + YouTube) — complete → gaps/D3-forums-youtube.md
- ~6,300 titles (EEVblog/QRZ via web search only — blocked; groups.io nanovna/tinysa/LibreVNA, RadioReference, eHam,
  TTN, SOTA, Arduino, Meshtastic GitHub, Hackaday, 17 YouTube channels); 699 classified: 69% C / 26% P / 5% M.
- Top gaps: bench measurements beyond S11 (output Z, dip meter); LoRa mesh capacity/congestion; radar applications
  (GPR, through-wall, Wi-Fi sensing, harmonic radar, RCWL-0516); everyday-device RF immunity (RCD trips, motors,
  Ethernet ferrites); handheld/vehicle antennas; antenna tuners/ATUs; discone/wideband; regs (NextNav 902–928,
  Baofeng legality, radar licensing); SA subtleties & receiver alignment; coax/connector practicalities.
- Uncorrected: "ferrites can't matter on Ethernet / throughput test proves fix"; discone "gain". Half: high-gain
  gateway antennas; "more hops/power always helps mesh"; cheap SDR vs classic receiver; "calibrate NanoVNA for 73 Ω".

## W4-D6 (consistency audit) — complete → gaps/D6-consistency-audit.md
- 24 issues (1 wrong, 6 inconsistent, 5 ambiguous, 12 cosmetic); 13/20/21 items provisional.
- WRONG: Leeson in 05/oscillators (2FkT/Ps, false "both sidebands") → FkT/(2Ps), Ps at sustaining-amp input,
  𝓛 = Sφ/2 (Rubiola arXiv:physics/0502143 Eqs 1.4, 1.26, 1.39); Lee–Hajimiri 2FkT/Psig uses tank power (+6 dB by
  definition). 05 examples shift −127 → −133 dBc/Hz.
- Inconsistent: via-to-plane L (03 ≈1 nH/J&G vs 04 0.54 vs 02 0.69); BGA524N6 IP1dB 18 says −12, datasheet −16 dBm
  (35 dB SAW then 1 dB short); RTL-SDR NF "no measurement" (17) vs 5.4 dB @437 MHz (14); JLC 7628 50 Ω width 0.343
  (03) vs 0.359 mm masked (13/JLC calc); 2-layer 50 Ω width 2.69–3.06 mm (thickness assumptions); matched filter
  2E/N0 (10) vs E/N0 (11); processing gain fs/2B real vs fs/B complex unstated; landed-rocket range 5.6 vs 11 km;
  micro-coax loss at L1 understated in 07.
- Canonical: kT0 −173.98≈−174 dBm/Hz; Cu IACS 5.80e7 S/m; η0 376.730 Ω; FSPL 32.45; budgets in E/N0; RO4350B design
  Dk 3.66; trace widths from fab calculator; via-to-plane ≈0.54 nH; SG limits 10 mW/100 mW@1%/500 mW e.r.p.;
  BGA524 −16 dBm; Hamming scalloping 1.75 dB (1.78 = 25/46 "exact Hamming" — not a misprint).
→ fixes: W5-E9 (most), W3-C1 (#5,#6), W3-C6 (#3,#9 in 20).

## W3-C6 (20-projects-recipes) — complete
- Predictions (pre-registered): 10 km flight / 15 km slant: 18.8 dB margin at 10 mW e.r.p., 41.3 dB at 2 W; SF9/125
  loses 1–12% boost packets at 868–905 MHz, fine at 433; GNSS FR-4 patch (openEMS, 2 meshes agree) AR 0.23 dB at
  1575.0 MHz, ≈+1.7 dBic; elliptic harmonic LPF 0.46 dB IL, H2 ≈ −51 dB (5th-percentile Monte-Carlo).
- **Band-edge finding: 433.125 MHz @250 kHz BW extends below Singapore's 433.05 MHz edge → use 434.125 MHz (E22 ch 24);
  E220 CH17 = 867.125 MHz.** Consistent with GNSS agent's "use ch 23/24" — ch 24 satisfies both.
- 18/lna-pa-gain-block-mmics BGA524N6 −4/−12 dBm are feature-list values; datasheet table IP1dB −16, IIP3 −9, OOB IIP3 −5.
- Gaps: no hardware tests yet; EBYTE air-rate map, PA noise 1.2–1.6 GHz, airframe antenna coupling, mm-wave rocket/plume
  returns unknown.

## W5-E2 (08 antenna additions) — complete
- 6 pages (slot, inductive/RFID/NFC/WPT, HF wire, multiband/wideband, lens/reflectarray, antenna-identification guide)
  + Q&A sections on 10 existing 08 pages. 8 scripts: 45 pre-registered checks pass, 5 miss (reported, not tuned).
- openEMS slot 488 Ω vs 474 Ω predicted (Booker ≈485 Ω); 915 MHz edge-notch slot 51.5 mm matches 872–986 MHz;
  discone SWR < 2.5 over 60–700 MHz but beam tilts below horizon.
- Contradictions: G5RV 20 m 1.8:1 not reproduced (NEC 2.3–7); OCF 1/3 point ≈100 Ω vs usual 4:1/6:1 balun lore;
  "magic" random-wire lengths fail across groundings; NXP AN11755 eq.(3) ambiguous; KB dipole Q 8–10 corrected to
  ≈6 (11.8% BW) by MoM.
- Gaps: Vivaldi/spiral/microstrip-crossing slot feed not simulated; Qi2 frequency secondary-only; active loops, linked
  dipoles, EFHW pitfalls absent; airframe slot needs real-tube model.

## W3-C1 (13-pcb-rf-layout-emc) — complete
- Canonical 50 Ω width table (stackups-and-materials.md#canonical-50-ω-width-table) from JLCPCB's own calculator, each
  with stackup/εr/mask: JLC04161H-7628 0.359 mm masked / 0.377 mm bare; JLC0216A 2-layer 2.692 mm (0.918 mm CPWG,
  8 mil gap); independent field solver 49.2–52.7 Ω for all ten. Settles JITX 0.3244 / 03 0.343 mm (mask assumptions).
- "Never via-fence/pour under radiator": ground 1 mm under 2.45 GHz radiator cuts Rrad ≈500×.
- Contradictions: textbook via-row isolation formula ~13 dB optimistic for practical via sizes; usual spread-spectrum
  clock estimate ~4 dB optimistic; JLC ±10% impedance tolerance vs forum ±20%; Southwest Microwave summary's via
  figures inconsistent with its own gap figure.
- Gaps: no TDR coupon measurement; no 3-D openEMS studies; pyro-pickup & av-bay thermal numbers are estimates;
  Semtech AN1200.66, ADI MT-031/MT-101 unreadable. Pages ~130–180 lines (dense).

## W5-E5 (estimation pack) — complete
- ML tone frequency/phase/amplitude meet CRB; threshold effect below ~12–16 dB integrated SNR. Ranging CRB: GPS code
  ≈1.1 m (tracking-loop formula gives 1.7 m); LoRa preamble ≈69 m at sensitivity.
- α-β = steady-state Kalman (exact); complementary filter = special case. 1-D baro+accel rocket filter: 0.09 m/s rms
  velocity, 2 ms apogee time; a 20 ms baro timestamp error raises NEES 2.9 → 329 (consistency test catches timing bugs).
- Monopulse optimum squint 0.425 beamwidth (Gaussian beams); PDA beats nearest-neighbour in clutter; GNSS-predictive
  Yagi pointing 5.1° → 0.26° at 1 km; six rockets sharing one LoRa channel deliver only 24% of packets.
- Flagged: 2E/N0 vs E/N0 complex-baseband convention differs between matched-filter and ambiguity pages (G-10-90).
- Not covered: IMM, attitude estimation, JPDA/MHT; EBYTE ACS and TX phase noise unmeasured.

## W5-E9 (consistency fixes) — complete
- All 24 D6 issues + orchestrator extras closed. Leeson FkT0/(2Ps) (−127 → −133 dBc/Hz example; fix_leeson_prefactor.py
  Monte-Carlo); via-to-plane ≈0.54 nH aligned 02/03/04/06/20; BGA524 −16/−9 dBm (35 dB SAW 1 dB short of 36 dB);
  widths linked to W3-C1 table; extra re-grep finds fixed (complex-IQ FFT floor −80 dBFS in 17; "CPWG 0.36 mm" in 20;
  CFRP numbers in 21). **E22 channel-avoid list unified everywhere: avoid CH 0–9, use CH 24 (434.125 MHz).**
  ZED-F9P L1/L2 confirmed; u-blox altitude 50/80 km by firmware; rtl_433 ≈380 decoders.
- New kb/00-math-foundations/canonical-values-and-conventions.md (+ fix_canonical_values.py, all pass), linked from
  CONVENTIONS §4.
- Deferred (gaps/W5-E9-deferred.md): build_index front-matter/anchor checks; MAX2659/AT2659 values unverified.
