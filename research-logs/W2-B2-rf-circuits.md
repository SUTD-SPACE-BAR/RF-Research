# Research log W2-B2: 06-rf-circuits
Status: complete (2026-09-29)
Owner scope: kb/06-rf-circuits/, research-logs/W2-B2-rf-circuits.md, tools/verify/rfckt_*.py

## Plan
Order chosen so later pages can link back (stability/gain definitions first, systems last).
- [x] amplifier-stability-and-biasing — DONE 2026-09-27 (kb/06-rf-circuits/amplifier-stability-and-biasing.md; verified by tools/verify/rfckt_stability.py, rfckt_noise2port.py) — K/Δ/μ/μ' derivations, stability circles, stabilisation, bias tees, BJT/FET bias, GaAs/GaN sequencing, bench oscillation, LF stability
- [x] lna-design — DONE 2026-09-27 (kb/06-rf-circuits/lna-design.md; verified by tools/verify/rfckt_lna.py) — gain definitions, noise/gain circles, SCM, inductive degeneration, noise vs input match, MMIC survey, limiters; 433 MHz + 1575 MHz worked designs (real S2P/noise tables if obtainable)
- [x] power-amplifiers — DONE 2026-09-27 (verified by tools/verify/rfckt_pa.py) — classes A..F/F⁻¹ efficiency derivations (conduction angle Fourier), Cripps load line, load-pull, harmonic terminations, output filter, back-off/PAPR, Doherty, ET, DPD, thermal, ruggedness; 433 MHz 2 W and 915 MHz 1 W examples
- [x] rf-filters-lc-saw-baw-cavity-microstrip — DONE 2026-09-27 (verified by tools/verify/rfckt_filters.py) — technology survey; stepped-impedance LPF, coupled-line/hairpin/interdigital BPF, Richards/Kuroda; coupling-matrix method; 433 MHz LC BPF + 2.45 GHz microstrip examples verified in skrf
- [x] couplers-dividers-combiners — DONE 2026-09-27 (verified by tools/verify/rfckt_couplers.py) — Wilkinson (even/odd derivation), branch-line, rat-race, Lange, coupled-line couplers, directivity, resistive splitters, combining efficiency
- [x] baluns-and-rf-transformers — DONE 2026-09-27 (verified by tools/verify/rfckt_baluns.py) — Marchand, lumped LC balun equations, Guanella/Ruthroff TLTs, ferrite transformers, imbalance specs, chip baluns and SX126x/CC1101 matches
- [x] rf-switches-attenuators-limiters — DONE 2026-09-27 (verified by tools/verify/rfckt_switches.py) — PIN/FET/SOI switches, T/R switching, Pi/T attenuator equations, DSAs, limiters
- [x] mixers — DONE 2026-09-27 (verified by tools/verify/rfckt_mixers.py) — multiplication, diode SBM/DBM/TBM, Gilbert, passive FET, conversion gain, LO drive, isolation, IP3, spur charts, Hartley/Weaver, IQ imbalance IRR, harmonic & subsampling mixers
- [x] vco-and-pll-synthesizers — DONE 2026-09-27 (verified by tools/verify/rfckt_pll.py) — VCO topologies, Kvco, integer-N / frac-N, charge pump, loop filters (2nd/3rd order passive), phase-noise contributions, spurs, lock time, DDS, parts
- [x] receiver-architectures — DONE 2026-09-27 (verified by tools/verify/rfckt_rx_tx.py A–F) — superhet, image, half-IF, dual conversion, zero-IF impairments, low-IF, digital IF, direct RF sampling; frequency planning; SX126x / AD9361 / R820T examples
- [x] transmitter-architectures — DONE 2026-09-27 (verified by tools/verify/rfckt_rx_tx.py G–I) — direct up-conversion, two-step, polar, IQ modulator impairments, masks, harmonic/spur suppression
- [x] detectors-and-power-meters — DONE 2026-09-27 (verified by tools/verify/rfckt_detectors.py) — diode detectors (square-law, sensitivity, TSS), log amps, RMS detectors, temperature compensation
- [x] frequency-multipliers-dividers — DONE 2026-09-27 (verified by tools/verify/rfckt_multipliers.py) — diode/transistor multipliers, efficiency, 20 log N, prescalers, regenerative/injection-locked dividers
- [x] circulators-isolators — DONE 2026-09-29 (verified by tools/verify/rfckt_circulators.py) — ferrite gyrator physics, junction circulators, isolators, non-magnetic alternatives, uses
- [x] _index.md, _sources.md — DONE 2026-09-29

Verification scripts planned (tools/verify/):
- rfckt_stability.py — K, Δ, μ, μ' equivalences; stability circles vs brute-force; stabilising resistor
- rfckt_lna.py — 433/1575 MHz designs; noise & gain circles; matching; skrf cascade NF
- rfckt_pa.py — conduction-angle Fourier efficiencies; class-E Sokal values; Cripps Ropt; harmonic filter
- rfckt_filters.py — prototypes; 433 MHz LC BPF; 2.45 GHz stepped-impedance LPF, coupled-line / hairpin BPF
- rfckt_couplers.py — Wilkinson, branch-line, rat-race S-parameters
- rfckt_baluns.py — lumped LC balun; Marchand ideal model
- rfckt_attenuators.py — Pi/T values
- rfckt_mixers.py — spur chart; IRR vs gain/phase imbalance
- rfckt_pll.py — loop-filter synthesis, phase margin, closed-loop noise
- rfckt_rx_tx.py — frequency plans, image/half-IF, sideband suppression
- rfckt_detectors.py — diode detector sensitivity
- rfckt_multipliers.py — harmonic content, 20 log N

## Log (append-only)
- 2026-09-27 — Read CONVENTIONS.md, INDEX.md, HANDOFF.md, CLAUDE.md, _TASK_SPECS (W2-B2). kb/06 empty; only kb/00 decibels page exists elsewhere. Created this log.
- 2026-09-27 — Fetched ATF-54143 datasheet (Avago, via modelithics.com mirror) → pdftotext. Got full S-param table (3 V/60 mA, 0.1–18 GHz), noise-parameter table (0.5–10 GHz), abs-max ratings, enhancement-mode bias equations (R1=295, R2=1205, R3=32.3 Ω example), LF-termination resistors R3/R4 note. Used in stability + LNA pages; data typed into tools/verify/rfckt_atf54143_data.py.
- 2026-09-27 — Fetched Edwards & Sinsky 1992 (IEEE T-MTT 40(12) 2303–2311) PDF (uni-lj mirror). Key: μ>1 alone necessary & sufficient; μ = min distance ΓL-plane origin → unstable region; K>1 only necessary; one auxiliary condition suffices (Appendix I); Table I test values.
- 2026-09-27 — TriQuint "Biasing GaN on SiC HEMT devices" (rfmw mirror): pHEMT pinch-off ≈ −1 V, GaN ≈ −4 V (Vds 10 V), gate leakage target <100 µA/mm, 3 W/mm dissipation at 30 V/100 mA/mm, trap-related Idq drift. TriQuint/Bellantoni "Bias techniques for GaN and pHEMT depletion mode devices" (2014): bias requirements list (bilateral gate current, stable into large capacitance, temp slope). Wolfspeed seq. note 403 (search summary only: gate pinched off before drain; Vgs ≈ −4 V pinch-off).
- 2026-09-27 — Rosu VA3IUL "Bias circuits for RF devices" (qsl.net): Vbe −2.5 mV/°C, β +0.5 %/°C, hFE spread 3:1, active PNP bias, LF loop oscillation through bias network. Search: Platzker/Struble/Hetzler 1993 IMS "Instabilities diagnosis and the role of K" (K test rigorous only if no RHP poles of unloaded circuit; NDF).
- 2026-09-27 — Wrote tools/verify/rfckt_atf54143_data.py (typed tables), rfckt_noise2port.py (Hillbrand–Russer chain noise matrices; self-test passes), rfckt_stability.py (A–J all PASS: μ⇔K&|Δ| equivalence on 2e5 random 2-ports; μ = geometric distance; circles; MSG/MAG reproduces data-sheet column to 0.00 dB; Rollett invariance; stabilisation study; via inductance; bias arithmetic). Wrote amplifier-stability-and-biasing.md.
- Finding: MSG = |S21/S12| invariant under any reciprocal embedding, K invariant under lossless embedding (numerically confirmed) — explains why single-R stabilisation to K=1 leaves MAG=MSG and why matching cannot stabilise.
- 2026-09-27 — LNA sources: BGA524N6 DS v3.5 (19.6 dB, 0.55 dB, 2.5 mA, IP1dB −16 dBm, IIP3 −9 dBm, Pin max 0 dBm, 8.2 nH LQW input L); PGA-103+ DS (0.05–4 GHz, 22.1 dB/0.5 dB/OIP3 39 dBm at 0.4 GHz, 5 V 97 mA, Pin max +21 dBm); ZED-F9P integration manual R16 (active antenna 17–50 dB gain, NF<4 dB, ideally 30–40 dB, total NF ≈ 3 dB, OOB rejection 40 dB, RF_IN abs max example +15 dBm, ESD mandatory); NAVIGATION 67(1):143 overview of OOB interference (filter-first vs LNA-first).
- 2026-09-27 — rfckt_noise2port.py extended with Y/Z-representation conversions and shunt feedback; rfckt_lna.py A–J + G all PASS: gain defs, SCM, noise & gain circles, U bounds, inductive degeneration closed forms (F = 1+γ gd0 Rs (ω0/ωT)², derived & verified), full ATF-54143 LNAs by differential evolution with realistic parts: 433 MHz (needs 1.5 kΩ+82 pF drain–gate feedback for unconditional stability to 100 MHz; NF 0.38 dB, G 22.1 dB, S11 −8.9, S22 −19.4) and 1575 MHz (NF 0.74 dB, G 19.2 dB, S11 −9.4, S22 −15.2), Monte Carlo 100 % stable. Source L 0.5 nH aligns S11* with Γopt (|diff| 0.05) at unchanged NFmin.
- 2026-09-27 — Wrote lna-design.md (269 lines). Session was interrupted by API limit after writing it; resumed, restructured this log.
- 2026-09-27 — PA sources: AFT05MS003N DS rev0 2015 (1.8–941 MHz, 7.5 V, 3.2 W, 350–520 MHz broadband 15.1 dB/73 % ηD; RθJC 4.1 °C/W; Coss 23.2 pF; Vgs(th) 2.2 V; VSWR >65:1 at 9 V; Zload 430 MHz = 5.86+j5.95 Ω); SKY66122-11 DS (863–928 MHz FEM, +30 dBm at 5 V/640 mA, gain 33 dB, 2fo −22 dBc max in DS test setup, 3fo–10fo −72 dBc, ruggedness 10:1, Pin max +16 dBm, LNA NF 2.6 dB/16 dB); ETSI EN 300 220-1 spurious limits via ST AN4305 + ETSI (−54 dBm broadcast bands incl. 470–790 MHz in V3, −36 dBm other <1 GHz, −30 dBm >1 GHz). Raab 2001 class-F paper: search gives 'vol 47' — believed actually IEEE T-MTT 49(6) 1162–1166 (June 2001); flagged. Sokal QEX 2001 PDFs unreachable (redirect/refused) → class-E constants from Raab 1977 recalled and verified by own time-domain simulation.
- 2026-09-27 — Wrote rfckt_pa.py (A–I ALL PASS: conduction-angle Fourier, class-F LP table = Raab, class-E ODE sim 99.9 % / Vpk 3.74 Vcc at QL 10, Cripps contours, AFT05 load estimate 6.22+j2.99 vs DS 5.86+j5.95, Doherty curve, back-off, ETSI harmonic budget + 7th-order Chebyshev LPF (−44 dB @866, −73 dB @1299), DPD ACLR −43→−63 dBc). Wrote power-amplifiers.md. FCC 15.205/15.209 checked via eCFR search (2690–2900 restricted; 500 µV/m @3 m >960 MHz).
- 2026-09-27 — Filter sources: Raltron RSF-433.920-1600 (DigiKey: 2.4 dB, 1.6 MHz, 3x3 mm); Murata SAFFB1G56KB0F0A (≤2.0 dB, 1561–1602 MHz, LCSC C91647); Qorvo blog BAW vs SAW (Q 1000–1500 vs 2500–5000; SAW ≲2.5 GHz) + EDN (TCF −45 SAW, −15..−25 TC-SAW, 20–30 FBAR ppm/°C). Wrote rfckt_filters.py (A–H ALL PASS, ~8 min: Kuroda derived identity, own 2-D FD Laplace solver (±1.1 % vs Hammerstad–Jensen; Garg–Bahl within 3.7 %), stepped-impedance LPF (skrf MLine), coupled-line BPF incl. inhomogeneous 2f0 spurious (−5.8 dB), coupled-resonator LC BPF with split-mode k and group-delay Qe, Cohn loss formula, coupling matrix inline/CQ, resonator Q: FR-4 47, RO4350B 126, coax cavity 4400–7000, helical 500–1000). Wrote rf-filters-lc-saw-baw-cavity-microstrip.md.
- 2026-09-27 — Wrote rfckt_netsolve.py (nodal solver: lines, coupled lines w/ unequal modal velocity, RLC; terminated-nodal S extraction after finding that Kron reduction fails for cascaded λ/4 lines at f0; microstrip helpers hj_z0/garg_bahl/coupled_synth). rfckt_couplers.py ALL PASS (Wilkinson equal/unequal/lumped, branch-line AR over L1 band, rat-race, 10/20 dB couplers: microstrip directivity 11.3/5.9 dB, resistive splitter, combining efficiency, weak coupler 6 dB/oct). Wrote couplers-dividers-combiners.md (Pozar ch.7 based; own derivations).
- 2026-09-27 — (session resumed after usage-limit reset; PA script already existed and passes — coordinator note was stale.) Johanson 0433BM15A0001 DS (430–435 MHz, IL ≤1.9 dB, 2f0 ≥34 dB, 180±10°, ≤1.5 dB, 1 W, 0805). rfckt_netsolve.py extended (per-port z0, tline_float for TLT windings). rfckt_baluns.py ALL PASS: lattice balun values/11 % BW, Marchand family with Z0o(Z0e→∞)=√(RsRb)/2 (found numerically, then derived), Guanella flat vs Ruthroff closed form (−0.97 dB at λ/4, null λ/2), LF limit, imbalance→CM. Wrote baluns-and-rf-transformers.md (antenna baluns left to 08).
- 2026-09-27 — Switch sources: PE4259 (vendor summary: 0.35 dB/30 dB @1 GHz, IP1dB +33.5 dBm @3 V, 25 kHz max rate), PE4302 (6-bit 31.5 dB DC–4 GHz, discontinued → PE4312), pSemi/Marki Ron·Coff notes (RF-SOI 100–200 fs; Tower 2020 PCM <10 fs claim), MACOM limiter (flat leakage ≈+15 dBm, spike 0.5 erg), IEEE PIN limiter spike/recovery paper (summary). rfckt_switches.py ALL PASS. Wrote rf-switches-attenuators-limiters.md. Finding: anti-parallel Schottky limiter is soft (+20→+10 dBm) — cannot protect a 0 dBm-rated GNSS LNA.
- 2026-09-27 — Mixer sources: Mini-Circuits AN-00-009 (read in full via pdftotext: CL, SSB vs DSB, compression within ~10 dB of LO, ~30 dB isolation, NF≈CL+0.5 dB, IP3 example −10→−17 dBm, IM3 −69 → IIP3 +16), AN-00-010/001 (search summary: IP3≈P1dB+15 diode/+10 FET; IP3≈LO+10 dB). rfckt_mixers.py ALL PASS (2/π switching, LO harmonic responses, spur/image/half-IF finder, IRR closed form vs IQ sim, diff-pair IIP3 = 4VT, APDP odd-product rule, subsampling folding, AN example). Wrote mixers.md.
- 2026-09-27 — PLL sources: ADF4351 DS rev0 via pdftotext (PFD max 32 MHz frac/45 int, ICP 0.312–5 mA, Kv 40 MHz/V, PN_SYNTH −220/−221, PN1_f −116/−118 (10 kHz, 1 GHz), in-band formula, VCO open-loop table, 2nd/3rd harmonics −19/−13 dBc, PFD spurs −80 dBc, output −4..+5 dBm); LMX2594 (TI page summary: 10 MHz–15 GHz, FoM −236, 1/f −129, PFD 300/400 MHz); Si5351 (datasheet summaries: VCO 600–900 MHz, multisynth 8+1/1048575..900, 2.5 kHz–200 MHz with R dividers). rfckt_pll.py ALL PASS (Banerjee filter synthesis exact; 3rd pole; noise budget → jitter-optimal 50 kHz, 248 fs; lock 34 µs; MASH-3 sim matches closed form −0.08 dB; leakage spurs; DDS −6.02P bound; Si5351 exact 10.7 MHz; Leeson).
- 2026-09-27 — Wrote vco-and-pll-synthesizers.md (ADF4351 433.92 MHz example: C1 2.66 nF/C2 17.4 nF/R2 503 Ω; noise budget; reciprocal-mixing link to RX page).
- 2026-09-27 — RX/TX sources: SX1261/2 DS (search excerpt: 'mostly low-IF'); R820T/RTL2832U community docs (3.57 MHz IF, 28.8 MS/s 8-bit ADC, DDC); AD9361 (ADI product page facts). rfckt_rx_tx.py ALL PASS (IF choice table, IIP2 +57 dBm, flicker zero-IF +10.5 vs low-IF +1.5 dB, jitter SNR, Nyquist zones, superhet cascade NF 3.8 dB/IIP3 −1.9 dBm, reciprocal mixing, IQ-mod sideband suppression, carrier leakage, polar delay EVM ~1 %/0.01 symbol, polar bandwidth expansion, LO pulling plan). Wrote receiver-architectures.md.
- 2026-09-27 — Wrote transmitter-architectures.md.
- 2026-09-27 — Detector sources: HSMS-285x DS via pdftotext (TSS −57 dBm, γ 40 mV/µW, Rv 8k, SPICE Is 3 µA n 1.06 Rs 25 Cj0 0.18 pF BV 3.8, PIV 2 V); AD8307 (92 dB, −75..+17 dBm, 25 mV/dB, −84 dBm), AD8318 (1 MHz–8 GHz, 60 dB ±1 dB, −25 mV/dB, 10 ns), LTC5582 (40 MHz–10 GHz, 57 dB, ±0.5 dB) via vendor summaries. rfckt_detectors.py ALL PASS (TSS estimate −60 vs −57 dBm; log-average of Rayleigh −2.51 dB; peak/log/RMS table). Wrote detectors-and-power-meters.md (confidence medium: sensitivity discrepancy + temperature model).
- 2026-09-27 — rfckt_multipliers.py ALL PASS (optimum conduction angles 120/80/60°, In closed form, push-push, APDP, 20logN vs Bessel incl. deviation at x100, divider floors, prescaler contiguity P(P−1), comb sinc, Page bound). ADF4351 prescaler limits read from DS (4/5 ≤3.6 GHz, NMIN 23; 8/9 NMIN 75). Wrote frequency-multipliers-dividers.md.
- 2026-09-29 — Resumed after usage-limit reset. rfckt_circulators.py fixed and ALL PASS (Polder tensor, Faraday rotation → √εr·ωm/2c = 11.6°/mm for YIG, ideal circulator unitary & non-reciprocal, non-ideal circulator: open antenna → PA VSWR 1.63 (30 dB term.) / 2.36 (15 dB term.), T/R leakage dominated by antenna reflection, junction disk R≈52 mm at 433 MHz). Circulator part example via search: VidaRF VDC-04200450-3 drop-in 420–450 MHz, 0.25 dB IL, 21 dB isolation, 400 W (trade-press summary).
- 2026-09-29 — Wrote circulators-isolators.md (confidence medium: lossless tensor model, first-order junction theory, part data from trade press).
- 2026-09-29 — Wrote _sources.md (consolidated bibliography, read-status flags) and _index.md (reading order, page table, 22-entry domain FAQ with anchors, script table, gaps). Read-only checks: all 14 pages have required template sections; no links to unplanned pages; 0 broken intra-domain anchors. Running all 16 rfckt scripts for final confirmation.
- 2026-09-29 — Final confirmation: all 16 tools/verify/rfckt_*.py scripts run clean (14 ALL PASS + netsolve/noise2port self-tests; atf54143_data is a data module). Task complete.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| 1 | ATF-54143 data sheet (Avago) | datasheet | S/noise tables, bias, ratings | primary; Fmin < 2 GHz extrapolated by vendor |
| 2 | Edwards & Sinsky 1992 T-MTT | peer-reviewed | μ test | read in full |
| 3 | TriQuint "Biasing GaN on SiC HEMT" | app note | pinch-off, drift | vendor |
| 4 | Bellantoni/TriQuint 2014 bias techniques | app note | GaN bias requirements | vendor |
| 5 | Rosu VA3IUL bias circuits | compiled notes | BJT tempco, topologies | secondary |
| 6 | Platzker/Struble/Hetzler 1993 IMS | peer-reviewed | K insufficiency, NDF | abstract only |
| 7 | Mini-Circuits PGA-103+ DS | datasheet | gain block numbers | primary |
| 8 | Mini-Circuits bias-tee blog | app note | choke/block rules | vendor |
| 9 | Coilcraft 0603CS/0805CS | datasheet | SRF values | via product pages |
| 10 | ADI HMC920 | datasheet | bias controller features | via vendor summary |
| 11 | Infineon BGA524N6 DS | datasheet | GNSS LNA specs | read via pdftotext |
| 12 | u-blox ZED-F9P Integration Manual R16 | manual | active-antenna specs | read (relevant sections) |
| 13 | NAVIGATION 67(1) OOB interference review | peer-reviewed | filter vs LNA order | summary only |
| 14 | NXP AFT05MS003N DS | datasheet | 433 MHz PA example, Zload | read |
| 15 | Skyworks SKY66122-11 DS | datasheet | 915 MHz FEM | read |
| 16 | ETSI EN 300 220-1 (via ST AN4305/search) | standard | spurious limits | summary |
| 17 | 47 CFR 15.205/15.209 (eCFR) | regulation | restricted bands | summary |
| 18 | Raltron / Murata SAW data | datasheet | SAW examples | distributor/summary |
| 19 | Qorvo/EDN BAW vs SAW | vendor/trade | Q, TCF | summary |
| 20 | Johanson 0433BM15A0001 DS | datasheet | chip balun | read |
| 21 | pSemi PE4259/PE4302, Ron·Coff notes | datasheet/app note | switches, DSA | summaries |
| 22 | MACOM limiter data; IEEE limiter paper | vendor/peer-reviewed | limiter behaviour | summaries |
| 23 | Mini-Circuits AN-00-009 (+AN-00-010/001) | app note | mixer terms, IP3 rules | AN-00-009 read |
| 24 | ADI ADF4351 DS | datasheet | PLL example, prescaler | read |
| 25 | TI LMX2594, SiLabs Si5351 | datasheet | PLL/clock facts | summaries |
| 26 | Semtech SX1261/2 DS (excerpt), RTL-SDR community docs, ADI AD9361 | datasheet/community | RX architecture examples | excerpts/secondary |
| 27 | Agilent HSMS-285x DS | datasheet | detector theory numbers | read |
| 28 | ADI AD8307/AD8318, LTC5582 | datasheet | detector ICs | summaries |
| 29 | Trade press (VidaRF drop-in circulator) | trade press | UHF circulator example | vendor claim |

## Contradictions / discrepancies found
- HSMS-285x: first-principles ideal voltage sensitivity 1/(2Is) = 167 mV/µW (≈123 after Cj/Rs/video losses) vs data sheet 40 mV/µW @915 MHz — factor ≈3 unexplained in detail (matching loss/package); flagged on detectors page.
- Edwards & Sinsky call K>1 "only a necessary condition"; Pozar/Gonzalez present K>1 & |Δ|<1 as the test. Consistent (K>1 necessary, insufficient alone); verified numerically.
- ATF-54143 data-sheet test circuit NF 0.5 dB @ 2 GHz vs our realistic, unconditionally-stable 1575 MHz design 0.74 dB — explained by part Q and stability constraint, not a contradiction.

## Knowledge gaps noticed (for later gap-filling)
- ATF-54143 Fmin below 2 GHz is vendor-extrapolated; no measured 433 MHz noise parameters found.
- SX126x effective NF (≈6 dB) only derived from sensitivity; domain 15 to confirm.
- Large-signal/parametric stability (Suárez & Quéré) only outlined.
- Sokal finite-QL class-E polynomials not fetched (PDF unreachable); Raab 2001 class-F volume number (47 vs 49) to confirm.

## Cross-domain notes (things other domains should cover/link)
- 18: add real part tables flagged in 06 pages: DBM spur tables, PIN limiters, UHF circulators/isolators, SAW/BAW at 433/868/915/1575 MHz, SMD couplers/hybrids.
- 15: SX126x RF-pin impedances/reference balun & match values; SX126x IF and image rejection; absolute-max RF input.
- 16: harmonic-balance / nonlinear stability workflow (06 stability page points there).
- 11: circulator T/R leakage numbers (06 circulators Example 2) for CW/FMCW radar pages.
- 01 passive-filter-design-prototypes covers lumped LC prototypes, 433 LPF, 915 BPF; 06 filters page links there and does not repeat.
- 18 filter-parts: table of JLCPCB-stocked SAW/BAW/ceramic parts (e.g., SAFFB1G56KB0F0A C91647).
- 19: confirm Singapore 433.05–434.79 MHz SRD rules; ETSI EN 300 220 harmonic limits used in 06 PA page.
- 04: inductor SRF/Q models (e.g. 0603CS-R10 100 nH SRF 1.4 GHz; 0805CS-102 1 µH SRF 180 MHz), capacitor ESL; via inductance ≈ 0.5–1 nH.
- 07: noise measure (Haus–Adler), noise temperature, Friis; 06 pages link there.
- 13: source-via count/placement for LNAs; shield-can box modes.
- 15: SX126x NF; ground-station LNA placement (06 lna-design Example 5).
- 17: NF measurement (Y-factor), oscillation hunting.

## Resume instructions (what the next agent should do if this one is interrupted)
- Pages done: amplifier-stability-and-biasing, lna-design, power-amplifiers, rf-filters-lc-saw-baw-cavity-microstrip, couplers-dividers-combiners, baluns-and-rf-transformers, rf-switches-attenuators-limiters, mixers, vco-and-pll-synthesizers, receiver-architectures, transmitter-architectures, detectors-and-power-meters, frequency-multipliers-dividers. frequency-multipliers-dividers, circulators-isolators (ALL 14 topic pages done) + _index.md + _sources.md. Task COMPLETE: all scripts pass (2026-09-29). Future work = items under 'Knowledge gaps' and 'Cross-domain notes'. INDEX.md/FAQ.md NOT regenerated by this agent (orchestrator runs tools/build_index.py).
- Page template: CONVENTIONS.md §3; each page ~250–700 lines, own words, verification scripts in tools/verify/rfckt_*.py (run each with python3; all should end "ALL PASS").
- Shared helpers: rfckt_netsolve.py (nodal S-parameter solver + microstrip formulas), rfckt_noise2port.py (noise-correlation cascade, ABCD/S/Y/Z conversions, shunt feedback), rfckt_atf54143_data.py (device tables). rfckt_lna.py takes ~2.5 min (differential evolution).
- PDFs: WebFetch saves binaries under ~/.claude/projects/.../tool-results/; extract with pdftotext -layout into the session scratchpad.
- Keep appending to "Log" above (not below this section).
