# Research log W5-S14: 06 receiver residuals
Status: complete (2026-10-13)
Owner scope: kb/06-rf-circuits/receiver-architectures.md, kb/06-rf-circuits/mixers.md, kb/06-rf-circuits/baluns-and-rf-transformers.md (surgical additions); kb/20-projects-recipes/beginner-project-ladder.md (one rung/link only); tools/verify/s14_*.py; gaps/GAP_REGISTER.md (§3 marks + §5 rows); this log. No _index.md edits.

Items: G-20-01 (superregen / crystal set / cheap OOK modules / FM bug), G-06-01 (Ku LNB, offset dish, L-band refeed), G-06-03 (receiver power budget, duty cycling, LO radiation, TX cannot sense RX), G-06-05 (mixer LPTV, passive-mixer noise folding, N-path / Tayloe), G-06-08 (balun practicalities, SA612 LO feed).

## Plan
- [x] Step 0 reading (CONVENTIONS, INDEX, register rows, canonical values, 06/_index)
- [x] grep KB for existing coverage — done; findings in log
- [x] sources: Armstrong 1922, Insam superregen, Moore/EMRFD, ARRL Handbook, Tayloe 2001, Soer/Klumperink N-path, Razavi passive mixer, LNB datasheets, SX1262 currents, FCC 15.111 / EN 300 440 LO radiation
- [x] tools/verify/s14_superregen.py — quench model (linear-mode growth, sensitivity vs quench, selectivity, re-radiation estimate), OOK range vs superhet
- [x] tools/verify/s14_tayloe.py — 4-path Tayloe detector time-domain sim: conversion gain, harmonic responses, noise folding, N-path bandpass; ngspice cross-check
- [x] tools/verify/s14_rx_budget.py — LNB numbers, offset-dish geometry, 1.7 GHz dish link budget, RX current budgets, LO radiation
- [x] receiver-architectures.md: 3 new Level-3 subsections, Examples 7–11, TL;DR/Q/table/practical/mistakes/verify/gaps/sources 7–18
- [x] mixers.md: TL;DR bullet, 4 Qs, Level 3 LPTV/N-path section (a)–(c), table rows, Examples 6–7, mistakes, verify, gaps, sources 9–12
- [x] baluns: TL;DR bullet, 4 Qs, #balun-practicalities-footprints-dots-placement-and-the-sa612, mistakes, verify, sources 7–8
- [x] ladder: Rung 0 (optional warm-up) + Open-questions bullet updated
- [x] GAP_REGISTER §5 rows C114–C118 + §3/§2 marks + change log

## Log (append-only)
- 2026-10-13 — Step 0 read. E7 and E6 complete, so 06 and the ladder are free. Last §5 row is C86 (others may be appending concurrently: re-check before writing).

- 2026-10-13 — grep results: FS1000A/XY-MK/RXB6/Tayloe/SoftRock/foxhole: 0 hits. LNB only in 08/antenna-identification-guide:85 and 19/spectrum-allocation:143; offset dish in 08/horn-reflector-aperture-antennas (blockage, Example 4 2.45 GHz 0.9 m offset dish; 'offset feed f/D not covered'). SA612 in 18/mixers-plls-vcos-parts:40,119,203 (clone risk, unverified specs) and 14/sdr-hardware-survey:43. Home FM legality already in 19/regulatory-faq-misc (§15.239 250 µV/m @3 m ≈ −47 dBm EIRP; no SG provision) — link, don't duplicate. SX1262 RX 4.6 mA DC-DC / 8.8 mA LDO, TX 118 mA @ +22 dBm in 15/semtech-chip-family. Ladder 'Open questions' already says a rung 0 could follow a 06 superregen page.
- 2026-10-13 — Analysis notes (to verify by script, not yet written): ideal 4-path 25 % sampling mixer: cap voltage = 0.9003·A (sinc π/4); harmonic responses k ≡ 1 mod 4 (3LO −9.5 dB image sense, 5LO −14 dB); noise-folding F = 1/sinc²(π/4) = 1.234 (0.91 dB), since Σ sinc² over k≡1 mod 4 = 1; 8-path 0.23 dB; in-band Z_in ≈ 4.3 R_s (R_sh, Andrews–Molnar); baseband pole 1/(2π N R_s C). Switching-mixer SSB NF 3.92 dB / DSB 0.91 dB. 'TX cannot sense RX': matched dipole σ = G²λ²/4π ≈ 0.10 m² at 433 MHz; 1 W, 2 dBi, 1 km → ≈ −132 dBm co-channel echo (check). LO radiation limits: FCC §15.111 (2 nW conducted), §15.109; EN 300 220 RX spurious −57/−47 dBm (verify).
- 2026-10-13 — PAUSED by coordinator before any web research, scripts or page edits. No background jobs started. No page or register files modified.
- 2026-10-13 — RESUMED by coordinator; continuing from resume step (1).
- 2026-10-13 — Research done (resume session 1). Facts gathered:
  * SA612A (NXP DS Rev 3, 4 Jun 2014, read via pdftotext): VCC 4.5–8 V, ICC 2.4 mA typ; f_in 500 MHz, f_osc 200 MHz; NF 5.0 dB @45 MHz; Gconv 14 min/17 typ dB; IP3i −13 dBm (table) vs "typically −15 dBm" (text) → contradiction; Ri 1.5 kΩ, Ci 3 pF per input (≈1.5 kΩ‖3 pF through 50 MHz), inputs symmetrical, must not be DC-biased externally, single-ended and balanced input configs shown (Fig 4); Ro(mix) 1.5 kΩ per output; external LO into OSC_B pin 6 via DC-block, 200 mVpp min – 300 mVpp max (= −10.0 to −6.5 dBm across 50 Ω, my calc). KB 18/mixers-plls-vcos-parts:119 lists IIP3 ≈ −15 "unverified" → now verified (note in cross-domain).
  * Tayloe (article "Ultra Low Noise, High Performance, Zero IF Quadrature Product Detector and Preamplifier", D. Tayloe; date not confirmed; US patent 6,230,000 B1 2001 "Product detector and method therefor"): <1 dB conversion loss claim (vs 7–8 dB prior art per patent); IP3 +30 dBm claim; Q = 3500 at 7 MHz (2 kHz tracking BW); bandwidth from 4×(Rsys+R+Rswitch)·C; example Rsys 50 Ω, 1 kHz −3 dB → C ≈ 0.8 µF (my calc 1/(2π·4·50·1 kHz) = 0.796 µF). Soer, U. Twente MSc 2007 "Analysis and comparison of switch-based frequency converters" (25 % double-balanced best NF/CL trade).
  * Modules (seller specs only, unverified): XY-MK-5V −105 dBm, FS1000A 10 mW, "about 200 m"; SYN480R ≈ −107 dBm claim; RXB6 no figure found. CC1101 (KB 15): −116 @0.6k, −112 @1.2k baud at 433 MHz.
  * Superregen theory: Moncunill-Geniz, Palà-Schönwälder, Mas-Casals, "A generic approach to the theory of superregenerative reception", IEEE TCAS-I 52(1) 2005 (abstract only); linear vs logarithmic (saturated) mode definitions confirmed via patent background. Armstrong, Proc. IRE 10(4) 1922.
  * LNB: universal LO 9.75/10.6 GHz, input 10.7–12.75 GHz (IF 950–2150 derived); PLL LNBs ±10–300 kHz (Goobay ±300 kHz, 25 MHz xtal; NISD ±10/30/100 kHz, NF 0.8 dB); Othernet Bullseye TCXO 2 ppm (vendor "10 kHz"); Labgear VK8L DRO ±1.3 MHz @25 °C, ±2.5 MHz −40…70 °C; Av-Comm DRO ±1 MHz, NF 0.7 dB, 65 dB gain; vendor "0.1 dB NF" claims implausible. Check: 9.75 GHz/25 MHz = 390 → 30 ppm crystal = ±293 kHz (matches ±300 kHz spec).
  * GOES HRIT/EMWIN: 1694.1 MHz, 927 ksps BPSK, 400 kb/s, 1.205 MHz BW, linear pol; min dish 1.0 m (El ≥ 10°), 1.2 m at 5° (NOAA). Downlink EIRP not found. GOES-E/W not visible from Singapore → use relative budget / polar L-band (Metop AHRPT 1701.3 MHz) with assumed EIRP clearly labelled.
  * Regulation: FCC §15.111(a) receiver antenna-terminal power ≤ 2.0 nW (= −57 dBm); §15.109(a) Class B at 3 m: 30–88 MHz 100, 88–216 150, 216–960 200, >960 500 µV/m (200 µV/m ≈ −49.2 dBm EIRP, my calc). EN 300 220-2 V2.4.1 cl. 4.3.7 points to EN 300 220-1 cl. 8.6 for RX spurious limits (values not read; −57/−47 dBm from memory — mark unverified).
  * Power: RTL-SDR Blog V3 270–280 mA at 5 V (vendor DS); SX1262 RX 4.6 mA DC-DC / 8.8 LDO (KB 15); SX1262 sleep 160 nA cold / 600 nA warm from memory (module DS show 1–3 µA) — mark.
  * Analysis to verify in scripts: 4-path ideal QSD cap amplitude sinc(π/4)=0.9003; responses only k≡1 mod 4 (3LO −9.5 dB mirrored, 5LO −14 dB); F = 1/sinc²(π/4) = 1.234 (0.91 dB), 8-path 0.23 dB; in-band Z_in fundamental ≈ R_s·0.81/(1−0.81) ≈ 4.3 R_s; baseband pole 1/(2πN R_s C). Superregen linear mode with ζ ramp → Gaussian sensitivity, BW_RF(−3 dB) = √(ln2)·√(ω0 ζ̇)/π (433.92 MHz, 500 kHz quench, ζ ±0.01 → ≈ 2 MHz); log mode: on-time +ln10/(ζ1ω0) per 20 dB (84 ns at ζ1 0.01). Two-ray range 40 log d regime: 7 dB sensitivity → 1.5× range. TX-can't-sense-RX: matched dipole σ = G²λ²/4π ≈ 0.10 m² at 433 MHz → echo ≈ −132 dBm at 1 km from 1 W. Simulation approach for QSD: per-cap IIR lfilter over concatenated window samples (vectorised), complex z = (v0−v2)+j(v1−v3); ngspice cross-check 7 MHz, R 50 Ω, C 10 nF, Δ 10 kHz → expect 0.893 V cap beat amplitude.
- 2026-10-13 — PAUSED again (coordinator) before any script or page edit. No background jobs.
- 2026-10-13 — RESUMED (2nd) at step (3): writing scripts.
- 2026-10-13 — tools/verify/s14_tayloe.py ALL PASS (output saved *_output.txt): cap amp 0.9003 A, single-pole f_p = 1/(2πNRC) (Tayloe 50 Ω/1 kHz → 0.796 µF, Q 3500), harmonic responses 3LO −9.54 dB mirrored / 5LO −13.98 upright / 7LO −16.9 mirrored, DC/2LO/4LO < −60 dB, F from deterministic H_k = 1.2335 (0.911 dB, N=4) and 1.0524 (0.222 dB, N=8), Monte Carlo 1.242, Z_in in-band 4.28 R (real), ngspice 7 MHz 0.8935 V vs 0.8932 V predicted.
- 2026-10-13 — tools/verify/s14_superregen.py ALL PASS: Gaussian sensitivity; ODE B = 1.451 MHz vs closed form 1.452 MHz (500 kHz quench, lnK 15); design law B = √(2 ln2 lnK)/(π Tg) (50 k→145 kHz … 1 M→2.9 MHz); 1 MHz off-tune only 5.7 dB rejection; ENBW 1.064·B, floor −104 dBm (NF 8); log mode equal steps per 10 dB; re-radiation estimate −13 dBm vs −49.2 dBm EIRP FCC (≈36 dB over); OOK two-ray ranges 267 m (−100 dBm) vs 532 m (CC1101 −112); 12 dB → 2× (two-ray) vs 4× (free space); FM bug 0.1 pF → 250 kHz; §15.239 = −47.3 dBm EIRP; crystal-set diode exact n VT ln I0: 74 % of peak at 200 mV, 0.23 mV at 5 mV (square law).

- 2026-10-13 — tools/verify/s14_rx_budget.py ALL PASS: LNB IF 950–2150; PLL ×390 (30 ppm → ±292 kHz); cascade NF 0.800 dB; IF noise into SDR −36 dBm; offset dish f 0.5/h 0.05/D 0.8 → offset 24.2°, f/D_eq 0.74; Singapore GEO 105.5°E El 87.4° (face 63°), QO-100 El ≈ 3°; 0.8 m at 1694 MHz 20.0 dBi, HPBW 15.5°, G/T 0.2 dB/K, −1.9 dB vs NOAA 1 m minimum (implied EIRP ≈ 48.8 dBm under stated assumption); SX1262 15.2 mW vs RTL-SDR 1.375 W (91×); duty-cycled RX 139 µA, 101-symbol preamble; LO leakage superhet −45 dBm (+12 dB over −57); matched dipole σ 0.102 m², echo −131.8 dBm @1 km; SA612 LO −10.0…−6.5 dBm, L-match 6.04 µH/77.5 pF, Si5351 divider 1 k/68 Ω → 268 mVpp; reversed IQ leg swaps sideband; empty 0402 pads RL 39.8/24.8/17.4 dB at 0.43/2.45/5.8 GHz.
- 2026-10-13 — Starting page edits.
- 2026-10-13 — receiver-architectures.md edited (163 → 296 lines): #first-radio-receivers-crystal-sets-superregeneration-and-cheap-ook-modules, #satellite-tv-lnbs-offset-dishes-and-l-band-re-feeds, #receiver-power-budget-duty-cycling-and-lo-radiation, Examples 7–11.
- 2026-10-13 — mixers.md (154 → 193 lines) and baluns-and-rf-transformers.md edited.
- 2026-10-13 — ladder Rung 0 added; internal links/anchors of all 4 edited pages checked (none missing). GAP_REGISTER: C114 G-20-01, C115 G-06-01, C116 G-06-03, C117 G-06-05, C118 G-06-08. Status complete.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| 1 | NXP SA612A DS Rev 3 (2014), full text via pdftotext | datasheet | balun/SA612 entry | primary; IP3 table/text mismatch |
| 2 | Tayloe US 6,230,000 B1 (2001); Tayloe article transcription (pdf4pro) | patent/magazine | mixers N-path | venue/date of article unconfirmed |
| 3 | Soer, U. Twente MSc 2007 | thesis | mixers N-path context | abstract-level |
| 4 | Moncunill-Geniz et al., IEEE TCAS-I 2005 (abstract); superregen patent background (linear/log mode) | peer-reviewed | superregen theory | model re-derived and ODE-checked |
| 5 | Tayda / BerryBase / SYN480R listings | vendor | module specs | seller claims, marked unverified |
| 6 | Goobay, NISD, Labgear VK8L, Av-Comm, Othernet listings/DS | vendor | LNB LO stability, NF, gain | vendor claims; 0.1 dB NF flagged |
| 7 | NOAA HRIT/EMWIN broadcast page | agency | L-band dish example | EIRP not found |
| 8 | 47 CFR 15.109, 15.111 (law.cornell.edu) | regulation | LO radiation limits | primary |
| 9 | ETSI EN 300 220-2 V2.4.1 (NATO mirror, pdftotext) | standard | points to EN 300 220-1 cl. 8.6 | -1 limit values not read |
| 10 | RTL-SDR Blog V3 datasheet (Mouser) | datasheet | SDR current 270–280 mA | primary |

## Contradictions / discrepancies found
- SA612A IP3i: −13 dBm (Table 6) vs "typically −15 dBm" (application text) in the same data sheet; KB 18/mixers-plls-vcos-parts:119 lists ≈ −15 dBm "unverified" — page 06 now quotes the table.
- XY-MK-5V seller sensitivity −105 dBm is ≈ 1 dB below the modelled thermal floor of a 500 kHz-quench SRO (NF 8 dB); not physical without heavy post-detection averaging.
- LNB "0.1 dB NF" vendor claims vs 0.7–0.8 dB from other vendors.

## Knowledge gaps noticed (for later gap-filling)
- Measured XY-MK-5V quench frequency, sensitivity and re-radiation (bench job; fits §7 "needs real-world data").
- EN 300 220-1 cl. 8.6 receiver spurious values; GOES HRIT downlink EIRP; L-band GEO options visible from Singapore (FengYun etc.).
- QSD with real switch R, baseband op-amp noise and clock skew not modelled.

## Cross-domain notes (things other domains should cover/link)
- 18/mixers-plls-vcos-parts:119: SA612A IIP3 now verified (−13 dBm table / −15 text), conversion gain 14 min/17 typ dB, NF 5.0 dB, 2.4 mA, 4.5–8 V — the 18 owner can drop "unverified".
- 08/horn-reflector-aperture-antennas "offset-dish feed design not covered": 06/receiver-architectures now has offset geometry (offset angle, f/D_eq) — link it.
- 06/_index (not edited by rule): add FAQ entries for superregen, LNB, Tayloe/N-path and balun practicalities; 14/sdr-hardware-survey could link the N-path section for SoftRock-class receivers.

## Resume instructions (what the next agent should do if this one is interrupted)
- DONE. (Historic:) State at pause (2nd): Step 0, KB grep and web research DONE (facts in Log entry 'Research done'); NOTHING written to kb/, tools/ or gaps/ yet. Skip resume step (2) except optional checks (EN 300 220-1 cl. 8.6 values, SX1262 sleep currents); start at step (3).
- Resume: (1) ToolSearch select:WebSearch,WebFetch; (2) research per Plan sources (Armstrong 1922, Moncunill-Geniz 2005, Insam 2002, EMRFD, ARRL Handbook, Tayloe 2001 patent 6,230,000 / QEX-RF Design article, Andrews–Molnar 2010 mixer-first, Soer 2009 N-path, SA612A datasheet, universal LNB 9.75/10.6 GHz, XY-MK-5V/FS1000A/RXB6 listings, FCC 15.109/15.111, EN 300 220); (3) write tools/verify/s14_superregen.py, s14_tayloe.py (+ ngspice deck), s14_rx_budget.py, each ending ALL PASS; (4) Edit (re-read first, bump last_updated) receiver-architectures.md (superregen/first radios, LNB + offset dish + 1.7 GHz dish budget, RX power budget/LO radiation/TX-can't-sense-RX), mixers.md (LPTV/conversion matrices, noise folding, N-path/Tayloe), baluns-and-rf-transformers.md (practicalities, SA612 LO feed); (5) ladder: add rung 0 link + update its Open-questions bullet; (6) GAP_REGISTER: re-check last C number (was C86), append §5 rows, mark §3 rows 'closed → §5 Cnn', add change-log line.
