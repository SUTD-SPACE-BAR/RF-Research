# Research log W2-B5: 12-phased-arrays
Status: complete
Owner scope: kb/12-phased-arrays/ ; research-logs/W2-B5-phased-arrays.md ; tools/verify/array_*.py

## Plan
Order: foundations first (array factor → steering → planar/coupling → tapering), then hardware
(architectures → components → calibration), then signal processing (adaptive/DOA), then DIY projects,
then _index/_sources. Verification scripts written alongside each page.

- [x] array-factor-linear-arrays — DONE (kb/12-phased-arrays/array-factor-linear-arrays.md; verified by tools/verify/array_factor.py) — AF derivation (ULA), pattern multiplication, broadside/endfire, Hansen–Woodyard, nulls, HPBW (0.886λ/Nd), directivity (sum formula, 2Nd/λ), array gain vs SNR gain
- [x] beam-steering-grating-lobes — DONE (kb/12-phased-arrays/beam-steering-grating-lobes.md; verified by tools/verify/array_steering.py) — progressive phase, grating-lobe condition, visible space (u-space circle), scan loss, beam broadening, squint (PS vs TTD, derive IBW), quantisation lobes (2^-2B), subarray TTD
- [x] planar-arrays-element-pattern-coupling — DONE (verified by tools/verify/array_planar.py, reuses ant_mom_wire.py) — rect/triangular lattices (grating lobe diagrams), 2-D AF, element vs active element pattern, mutual coupling, active reflection coefficient vs scan, scan blindness, embedded element efficiency, Hannan limit, edge effects, small arrays
- [x] tapering-sidelobe-control — DONE (verified by tools/verify/array_taper.py) — uniform, binomial, Dolph–Chebyshev (derive), Taylor n̄, cosine-on-pedestal, taper efficiency, beamwidth broadening, random errors → sidelobe floor, error budgets
- [x] beamforming-architectures — DONE (verified by tools/verify/array_architecture.py) — analog RF/IF/LO, digital, hybrid/subarrays, Butler, Rotman, trade-offs, digital-array SNR/dynamic range (+10logN), synchronisation (LO/clock), phase noise correlation
- [x] phase-shifters-ttd-components — DONE (verified by tools/verify/array_components.py) — switched-line, reflection, loaded-line, vector modulator, TTD; ADAR1000, HMC642/HMC1133-class, Anokiwave AWMF, T/R modules; cost per element
- [x] array-calibration — DONE (verified by tools/verify/array_calibration.py) — error sources, REV method, mutual-coupling self-cal, near-field probing, beacon far-field, KrakenSDR noise-source method
- [x] adaptive-beamforming-doa — DONE (verified by tools/verify/array_doa.py) — DAS, MVDR (derive), LCMV, sample covariance, diagonal loading, MUSIC, Root-MUSIC, ESPRIT, spatial smoothing, CRB, Python demos
- [x] diy-phased-array-projects — DONE (tools/verify/array_diy.py) — ADI Phaser CN0566, KrakenSDR, coherent RTL-SDR, Pluto/B210 2ch, FR-4 patch arrays, MIT, rocket tracking array vs Yagi, budget
- [x] _index.md — DONE
- [x] _sources.md — DONE

Verification scripts planned (tools/verify/array_*.py):
- array_factor.py — ULA AF closed form vs brute sum; HPBW numeric vs 0.886λ/(Nd); directivity numeric (sum formula) vs 2Nd/λ; endfire & Hansen–Woodyard D; array SNR gain Monte Carlo
- array_steering.py — grating lobe onset; scan HPBW broadening; squint PS vs TTD; quantisation lobe levels vs bits (Monte Carlo + formula); 8-el 5.8 GHz example
- array_planar.py — 2-D AF rect vs triangular lattice grating-lobe limits; element-count saving of triangular lattice; active reflection coefficient from a coupling model (e.g., infinite-array dipole Floquet or simple S-matrix), scan loss cos^n
- array_taper.py — Dolph–Chebyshev weights (derive & compare scipy.signal.windows.chebwin), Taylor weights (compare scipy taylor), taper efficiency, HPBW broadening, random-error sidelobe floor Monte Carlo vs formula
- array_architecture.py — digital array SNR/dynamic range; phase-noise correlated vs uncorrelated; Butler matrix beams
- array_doa.py — DAS, MVDR, MUSIC, Root-MUSIC, ESPRIT on synthetic ULA data; RMSE vs CRB; spatial smoothing for coherent sources; diagonal loading
- array_calibration.py — REV method simulation; noise-source channel cal simulation

## Log (append-only)
- 2026-09-27 — Read CONVENTIONS.md, INDEX.md, HANDOFF.md, _TASK_SPECS (B5 section), example page (08 antenna-fundamentals) and W1-A6 log for format. 12-phased-arrays folder empty; no prior log → fresh start. Created this log.
- 2026-09-27 — ADI "Phased Array Antenna Patterns" Parts 1–3 (Delos/Broughton/Kraft, Analog Dialogue 54(2),(3) 2020): WebFetch saved PDFs → pdftotext (summariser could not read). Key facts: ΔΦ=2πd sinθ/λ (ex: 15 mm, 10.6 GHz, 30° → 95°); HPBW≈0.886λ/(Nd cosθ); 1st SL −13 dBc; BW doubles at 60°; far field >2D²/λ with D=(N−1)d; cosine element factor; grating lobes θ=arcsin(mλ/d) at boresight (d=1.5λ → 0, ±41.3°); dmax=λ/(1+|sinθmax|) (10 GHz, ±50° → 17 mm); squint Δθ=arcsin((f0/f)sinθ0)−θ0, low freq squints more & away from boresight; hybrid arch mitigates squint; beam-angle resolution θRES≈sin⁻¹(Φ_LSB/(Nπ)) (2-bit, 30 el → ~1°); worst-case QSLL angles sin⁻¹(n/2^B), n odd (2-bit: ±14.5°, ±48.6°), worst QSLL ≈ −7.5 dB at 2 bits, ~6 dB/bit, independent of aperture size.
- 2026-09-27 — PySDR Phaser chapter: CN0566 8 elements, d=14 mm, ~10.25 GHz, HB100 source, ADF4159 LO, LTC5548 mixers → ~2 GHz IF into Pluto, 2× ADAR1000 (4 ch each), each ADAR1000 sum → one Pluto RX channel; cal stored as phase_cal_val.pkl / gain_cal_val.pkl (8 values each). ADAR1000 product page: ≥31 dB gain range, 360° phase, 6-bit-class resolution (≤0.5 dB, 2.8°). KrakenSDR wiki: 5× R820T2 + RTL2832U, single clock, 8-bit, 24–1766 MHz, 2.56 MHz BW, auto noise-source cal vs CH0; UCA radius r=sλ/√(2(1−cos(360°/n))), s in 0.2–0.5 (≥0.5 ambiguous); cables equal to 1 cm below ~900 MHz (1 cm ≈14° at 800 MHz); "in almost all cases" use MUSIC; decorrelation options designed for ULA; setting #sources too high is bad. Hannan 1964 abstract (ADS/IEEE): element gain in large array = 4πA/λ² × cosθ ideal; array gain = N × embedded element gain.

- 2026-09-27 — Nikolova McMaster L14 (pdftotext): HW β=−(kd+2.94/N), z_min≈−1.47, D_HW≈1.789·4Nd/λ, back-lobe condition d≈(N−1)λ/(4N); BSA D≈2Nd/λ, EFA 4Nd/λ. Wrote tools/verify/array_factor.py — results: closed form = brute sum (1e−15); HPBW N=8 λ/2 12.80° (formula 12.69°), 30°→14.84°, 60°→28.84° (formula 25.38°, 14% low for small N); N≥32 exact. First SLL: N=3 −9.54, 4 −11.30, 5 −12.04, 8 −12.80, 16 −13.15, ∞ −13.26 dB. Exact D (double sum) = numeric sphere integral; D=N at d=λ/2 for ALL scan angles (incl. endfire); d=λ → D=N (grating lobes); 8×0.7λ at 45° → 5.75 (grating lobe). HW exact ratio 1.757 (N=5) … 1.803 (N=100) vs 1.789 approx. cosθ element (6.02 dBi) ×8 at λ/2 → 14.09 dBi vs naive 15.05; cos² 15.21 vs 16.81. Monte-Carlo SNR gain = N; Hamming N=8 → 7.28 dB; isotropic-noise array gain = directivity exactly (sinc(kd) correlation). 915 MHz 4 λ/2 dipoles side by side: 9.22 dBi; over infinite λ/4 reflector 12.96 dBi.
- 2026-09-27 — PAGE WRITTEN: array-factor-linear-arrays (≈330 lines).

- 2026-09-27 — (resumed after usage-limit reset) tools/verify/array_steering.py written & run (~4 min). Results: GL peak at horizon d=λ/(1+|sinθ0|); null-margin version d=λ(1−1/N)/(1+|sinθ0|) (N=8, ±60°: 0.536λ vs 0.469λ). Beam broadening N=8: ×1.159/1.436/2.253 at 30/45/60° (1/cos: 1.155/1.414/2.0). Squint numeric = asin((f0/f)sinθ0) exactly. IBW: 3-dB edge loss ⇔ B/f0 = Θ3bs/sinθ0 (numeric match to 0.5%); 1-dB edge loss ⇔ 0.59×that. Subarray TTD (4×8) at ±10%: peak stays within 0.4°, but lobes rise to −7 dB, 1.16 dB loss. Phase quantisation: gain loss exact = −20log sinc(1/2^P) (2 bits 0.91 dB, 3 b 0.22, 4 b 0.056); worst-case error-pattern lobe ≈ −6.02P + 4.4 dB (2 b −7.7, 3 b −14.0, 4 b −20.1, 5 b −26.2, 6 b −32.2) independent of N and taper, at sinθ0 = n/2^P (n odd) — confirms ADI Part 3; classic 1/2^{2P} is ~4.4 dB optimistic for worst case. Dither (random per-element phase offset) lowers the worst lobe by ~6.5 dB (N=100). 8-element: 4-bit worst SLL over 0–45° −10.8 dB (uniform, ideal −12.8), Taylor-25 → −17.2 dB. ADI θ_RES=sin⁻¹(Φ_LSB/(Nπ)) is a proportionality: actual half-array-LSB beam shift is ≈1.5× larger (LS-slope 1.5·LSB/N). Random phase error pointing σ_u = σ_φ λ/(2πd)·√(12/(N(N²−1))) confirmed by MC.

- 2026-09-27 — PAGE WRITTEN: beam-steering-grating-lobes (≈190 long lines).

- 2026-09-27 — Kildal, Vosoogh, Maci 2015 (IEEE AWPL, Chalmers author version, pdftotext): e_emb,j = 1 − Σ_i|S_ij|²; embedded element in dense array has cosθ pattern (D_emb = 4 = 6 dBi); Hannan asymptote e_emb = π dx dy/λ² valid for dx,dy < 0.56λ; = π/4 = 79% at λ/2×λ/2; realized gain of array = sum of embedded realized gains; infinite-array relation e_emb = 1 − (1/π²)∬|R(γx,γy)|² (must integrate over invisible region too). Pozar 1994 "The active element pattern" (abstract). Pozar & Schaubert 1984 blindness: Floquet-mode ↔ surface-wave coupling theory (abstract). Sharp 1961: equilateral triangular lattice saves 13.4%.
- 2026-09-27 — tools/verify/array_planar.py (≈70 s): triangular saving 13.4% (analytic = brute-force reciprocal lattice); 8×8 λ/2 planar: isotropic 19.74 dBi (two-sided), cosθ element 23.04 dBi = Hannan 4πA/λ² 23.03 dBi (N·D_el 24.08 overestimates by 1.05 dB = π/4); MoM (reused ant_mom_wire.py) 8 resonant λ/2 dipoles (0.4764λ, a=0.001λ) side by side at λ/2: Z12 = −17.5−28.7j Ω, |S21| −15.0 dB, |S31| −22.1 dB; |Γa| centre 0.33 (0°), 0.07 (45°), 0.44 (60°), 0.61 (75°); realized gain vs scan −0.58/−1.34/−2.85/−3.88 dB at 30/45/60/75 (≈cos until 60°); e_emb centre 0.906, edge 0.946 (S-matrix = pattern integral); over λ/4 reflector: |Γa| 0.13/0.07/0.29/0.63/0.77 at 0/30/45/60/75°, scan loss −0.19/−0.73/−2.24/−6.82 dB, broadside realized 15.86 dBi, e_emb 0.884/0.930. Edge vs centre embedded gain at 30°: 1.03 vs 2.41 dBi (free space). TM0 grounded-slab β/k0 (FR-4 1.6 mm, 5.8 GHz: 1.0121; FR-4 3.2 mm 10.25 GHz: 1.289); blindness estimate sinθb = λ/d − β/k0: FR-4 1.6 mm 5.8 GHz d=λ/2 → 81°, d=0.6λ → 40.9° (GL 41.8°); FR-4 3.2 mm 10.25 GHz d=λ/2 → 45°.

- 2026-09-27 — PAGE WRITTEN: planar-arrays-element-pattern-coupling. New design rule derived: printed arrays d ≤ λ/(β_sw/k0 + sinθm) (FR-4 1.6 mm 5.8 GHz ±45° → 0.582λ).

- 2026-09-27 — Nikolova L15 (pdftotext): binomial HPBW 1.06/√(N−1), D≈1.77√N; Dolph N=10 26 dB example x0=1.08515, weights 1:1.357:1.974:2.496:2.789; d_max/λ = 1 − arccos(1/x0)/π. Taylor 1955 citation confirmed (TPGAP.1955.5720407). Elliott 1958 abstract. tools/verify/array_taper.py: own Dolph (Chebyshev + inverse DFT) = scipy chebwin (4e−16); own Taylor = scipy taylor (2e−16); 8/30 dB weights match 00 page; Balanis broadening factor f underestimates exact broadening 5–10%; large-N HPBW_u = (2λ/(πNd))√(acosh²R − acosh²(R/√2)) is a lower bound; Taylor largest monotonic n̄ (N=200): 3/5/7/9/11 for 20/25/30/35/40 dB (≫ '2A²+½'); random-error floor (σa²+σφ²)/(Nη) = MC within 0.1 dB; failures floor p(1−p)/(Nη); monopulse 16-el uniform slope 0.22/°; 8-el realistic (ADAR1000 steps + 0.3 dB/3° residual) 25 dB design → −21.9 dB median.
- 2026-09-27 — PAGE WRITTEN: tapering-sidelobe-control.

- 2026-09-27 — ADI articles (via search/Embedded Computing reprint): Delos 2018 LO phase noise model (reference correlated; distributed PLL/VCO uncorrelated → 10logN); Delos/Jones/Robertson 2018 forced spurious decorrelation (LO offset + NCO, ADRV9009; 10logN for uncorrelated noise and spurs). ADI "Hybrid beamforming receiver dynamic range" and MWJ ADC-merit PDF: timed out / 403 (not read). RF Essentials glossary Butler crossover claim (−3.0 dB for N=8) contradicted by AF math (−3.87 dB). tools/verify/array_architecture.py: DBF noise floor improvement = 10logN (3.03/5.94/9.02/12.00 dB for N=2/4/8/16); uncorrelated spurs −10logN on average; correlated spur only AF-suppressed; H2/H3 steered off (8 el, 20°: −13.0/−19.6 dB); phase-noise improvement 10log(N/(1+(N−1)ρ)) MC-verified; Butler orthogonal, crossover −3.70 (N=4), −3.87 (8), −3.92 dB (∞); analog cascade 8 el: +7.0 dB (25 dB LNA), −9.0 dB (no LNA); sync numbers.
- 2026-09-27 — PAGE WRITTEN: beamforming-architectures.

- 2026-09-27 — ADAR1000 datasheet Rev. B (WebFetch-saved PDF from a distributor mirror, pdftotext): 8–16 GHz, 4 ch half-duplex; 360°, 2.8° phase resolution, RMS phase error 2°, ≥31 dB gain range, ≤0.5 dB steps, RMS gain error 0.2 dB; Rx single-channel gain 10 dB (9.5 GHz), NF 8 dB, IP1dB −16 dBm, IIP3 −7 dBm; Tx gain 21 dB, OP1dB 10 dBm, Psat 14 dBm, Tx NF 22 dB; 121 stored beam positions; phase/gain switching 20 ns, T/R 180 ns; supply 3.3 V 260 mA Rx / 350 mA Tx (4 ch) and −5 V; 7×7 mm LGA; bias DACs for external PA/LNA. ADTR1107 (search summary of datasheet): 6–18 GHz PA+LNA+SPDT, Psat 25 dBm, Tx gain 22 dB, Rx gain 18 dB, NF 2.5 dB, 5×5 mm; 4 per ADAR1000 in λ/2 lattice. ADAR4002 (search summary): 0.5–19 GHz TTD, 7-bit, 508 ps max/4 ps (range 0) or 254 ps/2 ps (range 1), plus 6-bit 31.5 dB DSA.

- 2026-09-29 — (resumed after second usage-limit reset) Disk check: 5 pages + 5 array_*.py present. Search summaries: HMC649A 3–6 GHz 6-bit (5.625° LSB), rms phase error 4°, IL variation ±0.5 dB; HMC647A 2.5–3.1 GHz 6-bit rms 1.5°; HMC642A 9–12.5 GHz 6-bit rms 4.5°, IL 7–10 dB; HMC928 analog 2–4 GHz 0–450° with 0–13 V, ±5° phase error (obsolete); ADL5390 vector multiplier 20–2400 MHz, +5 dB to <−30 dB, 360°; Anokiwave AWMF-0108 26.5–29.5 GHz quad 5-bit phase/5-bit gain, Tx 26 dB/+9 dBm, Rx coherent gain 28 dB, NF 5 dB, IIP3 −28 dBm, 1.8 V, 6×6 QFN (Anokiwave now part of Qorvo). Mini-Circuits JSPHS-2484+ datasheet (pdftotext): 2150–2484 MHz, 180° min, IL 2.0 dB typ, VSWR 1.5, 0–15 V control (phase at 15 V: 321°/267°/201° at 2150/2300/2484 MHz — strongly frequency-dependent & nonlinear), max operating power 0 dBm.

- 2026-09-29 — Search summaries: PE44820 (8-bit 1.7–2.2 GHz, 1.4° steps), QPC2108 (2.5–4 GHz 6-bit, rms < 2.8°, RFMW US$171.39 @1–24), EVAL-CN0566-RPIZ ≈ US$2,875 (DigiKey via search), KrakenSDR US$299 (campaign) → 399 → 499 (2023); ADAR1000 price not exposed. tools/verify/array_components.py: loaded-line closed forms Zc=Z0/√(1+b²), Δφ=2atan b exact; RTPS 5:1 varactor 83°/176°/246–287° (bare/resonated/transformed @2.44 GHz); vector-mod DAC 6/8/10-bit max 1.15/0.29/0.07°; I/Q imbalance peak ½√(ε²+δ²); JSPHS-2484+ slope nonlinearity 4.7–7×; TTD sizing; Friis chains (PS-first 7.0 dB vs LNA-first 1.1 dB; ADAR1000 alone 8.3 dB vs with ADTR1107 2.7 dB).
- 2026-09-29 — PAGE WRITTEN: phase-shifters-ttd-components.

- 2026-09-29 — REV: Mano & Katagi 1982 (Electron. Commun. Jpn 65-B(5); abstract via Wiley/Semantic Scholar) + arXiv 2504.16107 (RHEV, html) summary of classic REV: P(φ) sinusoidal in element phase, amplitude ratio from (Pmax−Pmin)/(Pmax+Pmin) (for ratio ≤ 1), phase at max; limitations: ≥3 states, accuracy limited by phase-shifter accuracy (6-bit PS errors up to 11°), two-solution ambiguity, noise sensitivity grows with N. Aumann, Fenn, Willwerth 1989 IEEE TAP 37(7):844–850 (abstract): mutual-coupling technique needs Tx/Rx between element pairs. MDPI Electronics 12(3):489 (2023) comparison paper — 403, not read.
- 2026-09-29 — tools/verify/array_calibration.py (~20 s): REV (own derivation, LS fit of P = A + B cos(D+ψ), pick |En| < |E0−En|) recovers channel errors to 0.07 dB/0.44° (6-bit, 20 dB SNR, 2° PS error) and restores Taylor-25 SLL from −8.4 to −23.2 dB (design −24.4); needs N·2^P readings (512 for 8×6-bit; ≥3 states each). Noise-source cross-correlation phase std = √((2/s + 1/s²)/(2M)) (MC match: 20 dB, 65536 samples → 0.022°). Fractional delay: LESSON — adjacent-bin cross-spectrum phase slope is hopelessly noise-biased; use bins M/4 apart (0.2988 vs 0.3 true). Mutual-coupling ALS (translation invariance + reciprocity): residual 0.004 dB/0.03° ideal, 0.18 dB/1.6° with 10% edge-coupling perturbation, 0.64 dB/4.4° with 30%; exact gauge: t_m(−1)^m, r_n(−1)^n, c_k(−1)^k leaves all M_mn unchanged (π on alternate elements) — resolved by assuming errors < 90°. Accuracy for floor 10 dB under design: 8 el −25 dB → 0.29 dB/1.9°; 64 el −30 dB → 0.44 dB/3.0°.

- 2026-09-29 — PAGE WRITTEN: array-calibration.

- 2026-09-29 — Citations confirmed via search: Reed, Mallett, Brennan IEEE TAES 10(6):853–863, 1974 (K≈2N → 3 dB); Krim & Viberg IEEE SPM 13(4):67–94, 1996. Spatial-smoothing literature: P coherent sources need 2P elements (forward) or 3P/2 (forward–backward) (search summary). tools/verify/array_doa.py (~70 s): single source N=8 K=100: Bartlett/MUSIC/Root-MUSIC reach √stochastic-CRB (e.g. 0 dB: 3.78e−3 vs 3.68e−3 in u; 20 dB: 3.57e−4 vs 3.48e−4); MVDR ≈ +3–5%; ESPRIT (TLS, max-overlap subarrays) ≈ 25–40% above CRB; threshold below −5 dB. Resolution (two sources, N=8, K=100): at 0.5 Rayleigh Bartlett 0%, MVDR needs ≥10 dB, MUSIC 93% at 0 dB, Root-MUSIC/ESPRIT 100% at 0 dB; at 0.3 Rayleigh MVDR needs 20 dB, MUSIC 98% at 10 dB, Root/ESPRIT ≈80% at 0 dB. Coherent pair: R rank-1 (eigs 16.8, 0.011); unsmoothed MUSIC errors ≈0.03 u and 36% failures; FSS L=5/6 and FBSS L=6 → 100%, 3–4e−4 u. SMI SINR loss matches RMB (K+2−N)/(K+1): K=12 −3.47 vs −3.36 dB (≈2N−4 for N=8… K=2N=16: −2.36 dB). MPDR signal cancellation: SNR 20 dB, Δu=0.02 → −11.6 dB SINR (optimum 29) vs 21.7 dB with 20 dB loading. LCMV null −299 dB at constraint. MDL: K=100 correct at ≥−5 dB. UCA 5 el s=0.4λ → r=0.340λ (23.6 cm at 433 MHz), 360° no mirror ambiguity (ULA mirror correlation 1.000, UCA 0.145).

- 2026-09-29 — PAGE WRITTEN: adaptive-beamforming-doa.

- 2026-09-29 — Searches: Charvat MIT IAP 2012 phased-array radar (pegboard + Wi-Fi antennas; switched-array concept, book "Small and Short-Range Radar Systems"); Pluto Rev C/D RX2/TX2 on u.FL, factory 1R1T, enable "2r2t"/AD9361 mode (EngineerZone, ADI HDL docs, plutoplus issue); KerberosSDR (4× R820T2, 24 MHz–1.7 GHz, noise source, disconnect antennas when syncing, Linux native). Consistency: 14-sdr-dsp/sdr-hardware-survey prices (Pluto 250, B210 2387, KrakenSDR 749–775 USD); 15-lora ism page: Singapore 433 MHz 10 mW e.r.p. tools/verify/array_diy.py: element counts vs gain/band; link budgets (433 2 W 30 km dipole margin 49 dB; 5.8 GHz 25 dBm 30 km needs ≥20–23 dBi); elevation rates v/D (300 m/s, 2 km → 8.6°/s); DF cross-range; interferometer ambiguity (d=λ: 20° ↔ −41.1°).
- 2026-09-29 — PAGE WRITTEN: diy-phased-array-projects. Fixed KrakenSDR price on components page to ≈US$750 (consistency).

- 2026-09-29 — _index.md and _sources.md written. tools/build_index.py --check: all 12-phased-arrays links resolve except 3 to planned-but-unwritten pages (13/jlcpcb-rf-manufacturing, 13/rf-layout-rules, 16/rf-circuit-simulators-harmonic-balance) — allowed by CONVENTIONS §4.7. No missing template sections. TASK COMPLETE (9 pages + _index + _sources; 9 verify scripts).

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| S1 | Delos, Broughton, Kraft, "Phased Array Antenna Patterns—Part 1: Linear Array Beam Characteristics and Array Factor", Analog Dialogue 54(2), May 2020 | app note | AF, steering phase, HPBW 0.886λ/(Nd cosθ), far-field, element factor | high (cross-checked with own derivation) |
| S2 | same authors, "Part 2: Grating Lobes and Beam Squint", AD 54(2) Jun 2020 | app note | dmax=λ/(1+|sinθ|), squint formula, TTD vs PS, hybrid | high |
| S3 | same authors, "Part 3: Sidelobes and Tapering", AD 54(3) Jul 2020 | app note | tapering analogy, beam-angle resolution vs LSB, quantisation lobes (−7.5 dB @2 bit, 6 dB/bit) | medium-high (QSLL numbers to be checked numerically) |
| S4 | PySDR ch. "Hands-on with Phaser" (Lichtman), pysdr.org/content/phaser | tutorial | CN0566 architecture facts | medium-high |
| S5 | ADI ADAR1000 product page | datasheet | 4-ch X/Ku beamformer, ≥31 dB gain range, 360°, ≤2.8° step | high |
| S6 | KrakenSDR docs wiki (krakenrf/krakensdr_docs), pages Home, 04 Antenna Array Setup, 05 Web Interface | vendor docs | KrakenSDR specs, UCA radius formula, spacing multiplier, cable tolerance, algorithm recommendation | high for specs |
| S8 | Nikolova, McMaster ECE lecture 14 "Linear array theory II" (2025) | lecture notes | HW derivation, directivity approximations | high (matches Balanis ch. 6 and own numerics) |
| S9 | Kildal, Vosoogh, Maci, "Fundamental directivity limitations of dense array antennas: a numerical study using Hannan's embedded element efficiency", IEEE AWPL 2015 (Chalmers CPL author version) | peer-reviewed | e_emb definition, Hannan asymptote π dx dy/λ², active-reflection integral | high |
| S10 | Pozar, "The active element pattern", IEEE TAP 42(8):1176–1178, 1994 (abstract via ADS/Semantic Scholar) | peer-reviewed | AEP concept | high |
| S11 | Pozar & Schaubert, "Scan blindness in infinite phased arrays of printed dipoles", IEEE TAP 32(6):602–610, 1984 (abstract) | peer-reviewed | blindness from Floquet↔surface-wave coupling | high |
| S12 | Sharp, "A triangular arrangement of planar-array elements that reduces the number needed", IRE TAP 9(2):126–129, 1961 (abstract) | peer-reviewed | 13.4% element saving | high |
| S13 | ADAR1000 data sheet Rev. B (analog.com/media/en/technical-documentation/data-sheets/adar1000.pdf; read via distributor mirror PDF) | datasheet | beamformer IC specs | high |
| S14 | ADTR1107 data sheet (analog.com; search-result summary) | datasheet | front-end specs | medium (summary, not full read) |
| S15 | ADAR4002 data sheet/product page (analog.com, Mouser; search summary) | datasheet | TTD specs | medium |
| S16 | ADI product pages HMC649A, HMC647A, HMC642A, HMC928, ADL5390 (search summaries) | datasheet | phase shifter specs | medium (summaries) |
| S17 | Anokiwave AWMF-0108 product page (search summary) | datasheet | mmWave beamformer example | medium |
| S18 | Mini-Circuits JSPHS-2484+ datasheet (pdftotext) | datasheet | analog varactor PS at 2.4 GHz | high |
| S19 | Mano & Katagi, "A method for measuring amplitude and phase of each radiating element of a phased array antenna", Electron. Commun. Jpn. 65-B(5):58–64, 1982 (abstract) | peer-reviewed | REV method | high (method re-derived) |
| S20 | arXiv 2504.16107 (2025) "Phased array calibration based on rotating-element harmonic electric-field vector with time modulation" (html) | preprint | classic REV equations/limitations summary | medium |
| S21 | Aumann, Fenn, Willwerth, IEEE TAP 37(7):844–850, 1989 (abstract) | peer-reviewed | mutual-coupling calibration | high (method re-derived) |
| S22 | Reed, Mallett, Brennan, IEEE TAES 10(6):853–863, 1974 (abstract/summary) | peer-reviewed | SMI convergence | high (reproduced) |
| S23 | Krim & Viberg, IEEE SPM 13(4):67–94, 1996 (abstract) | peer-reviewed review | DOA overview | high |
| S7 | Hannan, "The element-gain paradox for a phased-array antenna", IEEE TAP 12(4):423–433, 1964 (abstract) | peer-reviewed | element gain 4πA/λ² cosθ; array gain = N × element gain | high |

## Contradictions / discrepancies found
- KrakenSDR price: search results (Crowd Supply updates) US$299 campaign → 399 → 499 (2023); 14-sdr-dsp/sdr-hardware-survey (fetched 2026-09-27) lists US$749–775. Phased-array pages now use ≈US$750 (2026) and cite the SDR survey.
- REV amplitude ratio: arXiv 2504.16107 summary gives Δγ = (Pmax−Pmin)/(Pmax+Pmin); own derivation gives k = (√Pmax−√Pmin)/(√Pmax+√Pmin); the former equals 2k/(1+k²) (agrees only for k ≪ 1). Possibly a summariser/normalisation issue; page uses the derived form.
- Butler-matrix crossover: rfessentials.com glossary says −3.9 dB (N=4) and −3.0 dB (N=8); array-factor math gives −3.70 dB (N=4), −3.87 dB (N=8), → −3.92 dB. Page uses computed values and flags the glossary.
- Dolph–Chebyshev beam-broadening factor f = 1 + 0.636[(2/R)cosh√(acosh²R − π²)]² (as recalled from Balanis §6.8) gives 5–10% less broadening than exact patterns (N = 8–32, 25–40 dB). Possibly my recollection of the formula or its intended reference length; page says 'use exact numerics'.
- 'Largest monotonic Taylor n̄ ≈ 2A²+½' (from memory) is much smaller than the numerical monotonic limit; not asserted on the page.
- Phase-quantisation lobe level: widely quoted peak 1/2^{2P} (Miller 1964 as reproduced in Mailloux/Hansen — attribution from memory, book not checked) vs ADI Part 3 worst case −7.5 dB at 2 bits (≈1/2^{2P}+4.5 dB). Own numerics: worst case ≈ −6.02P + 4.4 dB at special angles sinθ0=n/2^P (n odd) where the error sequence alternates 0/LSB/2 and all spatial harmonics alias together; a single-harmonic continuous-ramp analysis gives 1/(2^P−1)². Both "right" for different conditions — page states the worst case.
- ADI Part 3 θ_RES ≈ sin⁻¹(Φ_LSB/(Nπ)) is written as a proportionality; true shift of the half-array-at-LSB state is ≈1.5× (least-squares slope). Noted on the steering page.

## Knowledge gaps noticed (for later gap-filling)
- Visser, Haupt, Stutzman & Thiele not consulted; Mailloux/Hansen chapter numbers from memory.
- Bayliss taper and Rotman-lens design equations not implemented.
- Component specs for ADTR1107, ADAR4002, HMC64x, QPC2108, PE44820, AWMF-0108, ADL5390 from search summaries only.
- No field-measured KrakenSDR DF accuracy; no measured FR-4 patch coupling; no openEMS unit-cell blindness result.
- ADI 'Hybrid beamforming receiver dynamic range' article not read (timeouts).
- Pages are 150–200 (long) lines each (≈25–33 kB); line counts below the 250-line guide because paragraphs are single lines.
- Full-wave (openEMS unit cell) Γa(θ) and blind angle for an FR-4 5.8 GHz patch array — only Floquet phase-matching estimates exist (planar page).
- Measured patch-to-patch coupling (E/H-plane) on FR-4 at 2.4/5.8 GHz not sourced.

## Cross-domain notes (things other domains should cover/link)
- 20-projects-recipes/phased-array-starter-build: use diy-phased-array-projects ladder (2-ch interferometer → KrakenSDR DF → FR-4 2.4 GHz Butler array → Phaser) and array_*.py scripts.
- 20-projects-recipes/ground-station-tracking-yagi: rocket elevation-rate kinematics (v/D) from array_diy.py §3.
- 18-components-parts: phase shifters/beamformer ICs list (ADAR1000, ADTR1107, ADAR4002, HMC647A/649A/642A, QPC2108, PE44820, JSPHS-2484+, ADL5390, AWMF-0108).
- 11-radar/mimo-radar-virtual-arrays and diy-radar-hardware already link here; switched-array (Charvat) radar is covered briefly in DIY page.
- 17-test-measurement/antenna-range-ota-testing: embedded-element-pattern and REV calibration measurement recipes.
- 08-antennas/antenna-measurement: embedded element pattern measurement (one port driven, others loaded) — planar page links there.
- 16-simulation-tools/openems-workflow: periodic unit-cell (Floquet) simulation recipe for phased-array elements.
- 03-transmission-lines-matching/s-parameters: N-port S-matrices, active reflection coefficient as a derived quantity.

## Resume instructions (what the next agent should do if this one is interrupted)
- Read this log's Plan checkboxes; pages marked [x] are done on disk in kb/12-phased-arrays/.
- Done so far: array-factor-linear-arrays, beam-steering-grating-lobes, planar-arrays-element-pattern-coupling (+ tools/verify/array_factor.py, array_steering.py, array_planar.py).
- Done also: tapering-sidelobe-control (+ array_taper.py).
- Done also: beamforming-architectures (+ array_architecture.py).
- Done also: phase-shifters-ttd-components (+ array_components.py).
- Done also: array-calibration (+ array_calibration.py).
- Done also: adaptive-beamforming-doa (+ array_doa.py).
- Done also: diy-phased-array-projects (+ array_diy.py).
- ALL DONE (2026-09-29). Nothing left to resume; for follow-up work see "Knowledge gaps noticed".
- Keep writing sources into the table as they are read; _sources.md is compiled from the per-page Sources lists at the end.
- WebFetch summariser can't read PDFs: it saves them under ~/.claude/projects/.../tool-results/*.pdf — run pdftotext on that file.
