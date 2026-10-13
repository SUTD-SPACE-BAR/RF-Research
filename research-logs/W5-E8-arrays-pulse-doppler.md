# Research log W5-E8: array synthesis, conformal/circular arrays, Yagi stacking, pulse-Doppler data cube
Status: complete (2026-10-13)
Owner scope: NEW files only in kb/12-phased-arrays/ (array-pattern-synthesis, conformal-and-cylindrical-arrays,
stacking-and-arraying-yagis) and kb/11-radar/ (pulse-doppler-data-cube-and-prf-regimes); edits to
kb/12-phased-arrays/_index.md, _sources.md; kb/11-radar/_index.md, _sources.md; tools/taxonomy.md (12 and 11
lines only); new scripts tools/verify/e8_*.py; figures in kb/12-phased-arrays/figures/.
Do NOT touch kb/11-radar/radar-tracking-monopulse-and-trackers.md (W5-E5 owns it; link only).

## Plan
- [x] Step 0 reading: CONVENTIONS, INDEX, 12 _index/AF/taper, 11 _index/pulsed/clutter, D4 rows #4 #7 #8 #9, D5 rows 10/1220/693/701
- [x] tools/verify/e8_synthesis.py (ALL PASS, ~7 s) — Schelkunoff zero placement, Fourier & Woodward–Lawson (sector, cosec²), Bayliss Δ, least-squares/convex with nulls, null steering vs interferer
- [x] kb/12-phased-arrays/array-pattern-synthesis.md (written 2026-10-03)
- [x] tools/verify/e8_conformal.py (ALL PASS, ~10 s) — cylindrical/conformal AF with rotated element patterns, polarization, sector selection/commutation, UCA phase modes, UCA DOA
- [x] kb/12-phased-arrays/conformal-and-cylindrical-arrays.md (written 2026-10-03, 251 lines)
- [x] tools/verify/e8_yagi_stack.py (ALL PASS, ~6 s) — PyNEC two/four 433 MHz DL6WU Yagis, stacking distance from effective aperture, gain vs spacing, H vs V, harness
- [x] kb/12-phased-arrays/stacking-and-arraying-yagis.md (written 2026-10-12, 253 lines)
- [x] tools/verify/e8_pulse_doppler.py (ALL PASS, ~13 s) — data cube simulation, range–Doppler map, PRF regimes, eclipsing/blind zones, CRT & staggered PRF resolution, Doppler filter bank, CFAR on RD map, DIY design
- [x] kb/11-radar/pulse-doppler-data-cube-and-prf-regimes.md (written 2026-10-12, 251 lines; figure kb/11-radar/figures/e8-range-doppler-and-blind-zones.png)
- [x] _index/_sources updates for 12 and 11; taxonomy lines (12: +3 slugs; 11: +1 slug); build_index --check (0 broken links in W5-E8 pages; 2 pre-existing broken links in 03/microstrip-discontinuities.md, not ours)

## Log (append-only)
- 2026-10-02 — log created. Read CONVENTIONS.md, HANDOFF.md, INDEX.md (domains 11, 12), 12/_index, 12/_sources,
  array-factor-linear-arrays, tapering-sidelobe-control, 11/_index, 11/_sources, pulsed-radar-and-pulse-compression,
  clutter-and-mti. D4 rows: #4 synthesis (Balanis 7.2–7.9, Mailloux 2.4, 3.1–3.3), #7 pulse-Doppler (Richards 3, 5;
  Skolnik 3), #8 conformal/cylindrical & phase-mode (Mailloux 4.1–4.4, Balanis 6.12), #9 stacking & harnesses
  (ARRL V3-4). D5: row 10 (synthesis+stacking cluster), 1220 (Schelkunoff/Fourier/WL missing), 693 (two stacked Yagis
  ≈ +3 dB partial), 701 (vertical stacking narrows elevation beam partial).

- 2026-10-02 — sources: (1) Bayliss 1968 BSTJ 47(5):623–650 READ via archive.org djvu text (bstj47-5-623): model
  difference function from derivative of Taylor ideal pattern, first 4 zeros moved, 4th-degree polynomial fits in SLL
  (dB, negative) for A, ξ1..ξ4, p0 (Fig. 4 table, C0..C4); line-source appendix: aperture sine series with
  eigenvalues l+1/2, dilation σ = (n̄+1/2)/Z_n̄; author warns polynomial fits depress the first sidelobe at −45 dB.
  arraytool (zinka/arraytool) "Bayliss" actually uses McNamara–Zolotarev zeros — not used.
  (2) G3SEK "Stacking Yagi antennas" (ifwtech.co.uk/g3sek/stacking/stacking2.htm) READ raw HTML: capture areas
  just touch; 2.5–2.9 dB for two; DL6WU D = λ/(2 sin(B/2)) for >10 el / >2λ boom; V-stack narrows elevation and
  adds elevation sidelobes. (3) Cebik W4RNL "2-m Yagi stacks part 1" (WebFetch summary): stack gain 2.9 dB (6 el)
  → 2.2 dB (18 el); gain-peak spacing 1.0–2.4λ, larger than the RSGB/DL6WU formula. (4) MIT LL/IEEE NH Radar
  Systems Course lectures 13 (Doppler filtering/MTD) and 14 (O'Donnell, airborne pulse Doppler), READ via
  pdftotext (gmoein.github.io mirror): X-band HPRF 100–300 kHz (<50 % duty), MPRF 10–30 kHz (~5 %), LPRF 1–3 kHz
  (~0.5 %), UHF LPRF 300 Hz; eclipsing loss 1–2 dB if unmitigated; HPRF 3 PRFs; MPRF 7–8 PRFs (APG-66 style example
  5.75–10.25 kHz); CRT formula R_c = ΣC_iA_i mod Πm_i; MTD 8-pulse filter bank, ASR-9 Doppler sidelobes 40 dB.
- 2026-10-02 — wrote tools/verify/e8_synthesis.py (§1 Schelkunoff, §2 Fourier, §3 Woodward–Lawson sector + csc²,
  §4 LS + null constraint, §5 LP min-max, §6 Bayliss from the 1968 polynomial table, §7 null steering/MVDR, §8 figures
  → kb/12-phased-arrays/figures/e8-shaped-beams.png, e8-bayliss-difference.png, e8-null-steering.png; numbers →
  tools/verify/e8_synthesis_output.txt). Key results: cardioid d=λ/4 D = 2 (3.01 dBi); 4-el nulls −40/+25/+55° →
  beam peak −7.2°, η −0.85 dB; zero at r = 0.95 → −28.8 dB minimum; Fourier sector ripple 1.3/1.2 dB (N 21/41, Gibbs);
  WL sector N = 20 half-amplitude edge samples: SLL −19.6 → −37.8 dB; WL csc² N = 16 ±2.7 dB over 7–38° (rolls off
  early, last sample 38.7°), N = 24 ±0.46 dB; Bayliss continuous n̄ = 5 meets −20…−35 dB within 0.4 dB, −40 dB needs
  n̄ = 6 (−39.7); peak at 0.991·σp0 (table transcription confirmed); sampled Bayliss-30 N = 16/32/64 → −29.3/−30.1/
  −30.3 dB vs sign-flipped Taylor −9.6 dB; LP min-max Δ (same slope/null) −32.0 dB; null steering 20° costs 0.02 dB,
  at 3° costs 4.3 dB; derivative null −64 vs −45 dB at Δu = 0.01; null depth with 0.3 dB/2° errors median −39.2 dB
  (floor formula −37.5 − 1.6); MVDR(INR ≥ 20 dB) ≡ projection of the uniform beam (corr 1.000000).
- 2026-10-02 — CONTRADICTION/ERRORS (own, logged per ethos): (a) pre-registered cardioid D = 3.0 was wrong; the
  closed form of the AF page gives exactly 2 — check replaced by the closed-form comparison (comment in script).
  (b) §5a LP "beats" Dolph (−32.57 vs −30 dB) because the LP sidelobe region starts at Dolph's FIRST NULL; Dolph
  only guarantees |AF| ≤ 1/R beyond the point where its main lobe crosses the −30 dB level (u_c < first null), so the
  LP problem was looser. A main-lobe ≤ AF(0) constraint was added (harmless, not the cause). FIX STILL TO DO.
- 2026-10-03 — RESUMED by coordinator: fix 2 misses, write 4 pages, indexes, taxonomy.
- 2026-10-03 — fixed the 2 misses: §5a LP edge = u_c (Dolph main lobe at −30 dB, 0.17379) → −30.00 dB, corr 1.000000
  (the −32.6 dB "win" was the looser first-null edge); §3b csc² N = 16 pre-registered ±1.5 dB NOT met (±6.6 dB) —
  kept as a printed finding; check now asks for the smallest N meeting ±1.5 dB → N = 17 (sample grid then lands at
  44.9°). Same edge fix applied to the Δ LP: LP min-max −29.62 dB vs sampled Bayliss −29.33 dB (Bayliss within 0.3 dB).
  ALL PASS. Wrote kb/12-phased-arrays/array-pattern-synthesis.md. Own error caught while writing: sector-beam
  directivity cost is ≈10 dB (13.0 → 3.2 dBi), not the 4.5 dB first drafted — computed and corrected.
- 2026-10-03 — wrote tools/verify/e8_conformal.py: exact 2-D eigenfunction series (TM line source, TE axial slot,
  TE magnetic line source, TM aperture) on a PEC cylinder; TM series vs own 2-D MoM (EFIE, pulse/point-matching)
  0.016 dB (a = 1λ) and 0.002 dB (a = 0.01λ). Wraparound roll-ripple table for 54/75/98/152 mm tubes at 433/915/2450/
  5800 MHz (TE φ-pol slots and TM z-pol 0.3λ apertures); minimal <1 dB designs have circumferential spacing
  0.11–0.66λ (median 0.36λ); two-term aliasing model 1 + 2ρe^{jχ}cos Nφ (ρe^{jχ} = j^N H'_0/H'_N) reproduces the full
  series exactly. Commutated 12-of-32 sector on a = 2.55λ: 14.24 dB 2-D directivity, scan ripple 0.09 dB; geometric
  co-phasing ≡ conjugate element-pattern phasing within 0.02 dB; all-32 matched only 13.74 dB (far-side elements add
  noise power in this 2-D directivity metric). Polarization (3-D free-space dipoles): circumferential-dipole sector
  cross-pol −15.5 dB vs −36 dB flat reference; cone-generator tilt 10°/20° → −22.8/−17.5 dB. UCA (KrakenSDR 5 el,
  r = 0.34λ, kr = 2.14): J0 = 0.146 (near its zero at 2.405) → arg(y1/y0) DF 9.1° rms vs arg(y+1/y−1)/2 0.52° rms
  (SNR 10 dB, 200 snapshots); aliasing bias 0.17°. Pseudo-Doppler 8-el ring bearing exact after hold-delay fix.
- 2026-10-03 — OWN ERRORS logged (pre-registered expectations that were guesses): (1b) "ka → 0 TM wire is invisible"
  — false in 2-D: J0/H0 decays only like π/(2 ln(2/γka)) (ka = 1e−16 still 0.41 dB); replaced by thin-cylinder MoM
  check. (1d) small-ka slot ripple: first guess "< 1.5 dB at ka = 0.3" (1.56 dB), second guess 10log(1+4x²) also
  wrong (n = ±1 term is in quadrature, n = ±2 and Re c0 enter at the same order); derived 10log[(1+3x²+πx³)/(1+x²)]
  converges (1.7 % at ka = 0.01). (1e) "−6 dB at grazing" was unfounded; series gives −3.2 dB, ka-independent for
  ka = 3–30. (7) pseudo-Doppler hold delay is (spp−1)/2 samples (script discretisation bug, 0.9° bias).
  TE series has no independent MoM check (only internal Wronskian, small-ka and large-ka limits) — stated on the page.
- 2026-10-03 — added §7b Adcock (octantal error (πd/λ)²/24·sin4φ derived; 0.97° at 0.2λ, formula 0.94°), §8 GNSS L1
  wraparound (98 mm: 4 el; 152 mm: 6 TE/5 TM), 5-el UCA geometry table (s = 0.4/0.5 straddle the J0 zero at s = 0.45),
  figure e8-wraparound-and-phase-modes.png. Wrote conformal page. Bug caught: a non-raw Python string turned \v, \f,
  \a, \t in LaTeX into control characters in the page — repaired and re-checked (no control chars left).
- 2026-10-03 — wrote tools/verify/e8_yagi_stack.py (PyNEC). Single 11-el DL6WU 433 MHz: 14.31 dBi (KB MoM 14.20),
  F/B 17.2 dB, Z 45.8 Ω (DE resonated 331.3 mm), HPBW E 35.5° / H 39.0°, avg gain 1.000 (NEC, phi0 = 90°) / 0.996 own.
  2-stacks: max +3.07 dB (E, 2.1λ) / +3.10 dB (H, 1.6λ) — slightly > 3.01 dB where mutual resistance < 0; coupling-free
  prediction G2/G1 = 2/(1+ρ), ρ = Fourier transform of the single power pattern, within 0.17/0.24 dB of NEC for D ≥ 1λ.
  Formulas: DL6WU/G3SEK λ/(2 sin(B/2)) → 1.64λ E (+2.94 dB, SLL −11.3) / 1.50λ H (+3.02, −12.0); KB yagi page 51/HPBW
  → 1.44/1.31λ (+2.72/+2.69 dB, SLL −15.0/−14.3); capture-area rectangle 1.54/1.40λ (+2.84/+2.87); ellipse ≈ DL6WU.
  2×2 box at DL6WU spacings +6.02 dB (20.33 dBi, 16.0 × 17.5°) = separable sum +5.96. Longer single Yagi: 18 el 3.61 m
  +2.66 dB (27 × 28.5°). Harness λ/4 75 Ω → 56.25 Ω, SWR ≤ 1.13 (425–445 MHz); with modelled Yagi Z 60.5 Ω (SWR 1.21);
  10 mm length error → 0.84° squint, 0.02 dB; detuned Yagi in a reactive T → 1.76 dB split imbalance; rolling linear
  rocket vs linear ground: 20.5 % of time < −10 dB, 6.4 % < −20 dB.
- 2026-10-03 — OWN ERRORS logged: (1b) average-gain grid with phi0 = 1.5° gave 0.929 (known NEC2++ first-column quirk);
  (4c) pre-registered "box 5.0–6.0 dB" (amateur figures include harness loss) MISSED by 0.02 dB (+6.02) — replaced by the
  derived separability check; (5) a temporary PyNEC context was garbage-collected before reading Zin (empty array).
- CONTRADICTION (cross-domain, for 08 owner): kb/08-antennas/yagi-uda-and-log-periodic.md gives the stacking distance as
  "≈ 51/HPBW λ" attributed to the DL6WU program; G3SEK's DL6WU formula is λ/(2 sin(B/2)) ≈ 57.3/B. NEC: both within
  0.4 dB of max gain; 51/B trades ≈0.3 dB for ≈3 dB lower stacking-plane sidelobes. Not an error in physics, but the
  attribution/formula differ — note on the stacking page; flag for W6 audit.
- 2026-10-12 — RESUMED. Added to e8_yagi_stack.py: odd-λ/4 harness bandwidth (9λ/4 → SWR ≤ 1.31), pointing loss,
  implied ρ, reversed-polarity Δ pattern (−209 dB boresight null), N-in-line (+3.02/+4.74/+5.99 dB NEC vs
  frozen-current +2.86/+4.53/+5.74), electrical tilt (10° asked → 8°, −0.5 dB, −4.9 dB grating lobe; 20° splits beam),
  sweep table + figure e8-yagi-stacking.png. ALL PASS. Wrote stacking page (link budget: CP first, stacking second).
- 2026-10-12 — wrote tools/verify/e8_pulse_doppler.py: 4×128×1000 cube (5.8 GHz, LFM 10 MHz/2 µs, PRF 20 kHz),
  3 targets + clutter → pulse compression, Cheb-60 Doppler FFT, CFAR: all detected (≤ 1 cell), 300 m/s aliased to
  −218 m/s; gains: non-coherent channel sum ≈ τf_s·N (34.8 vs 35.3 dB), coherent beam ≈ τf_s·N·M (40.8 vs 41.3);
  strong clutter range sidelobes give zero-Doppler CFAR hits ±τc/2. Eclipsing energy loss = −10log(1−d) (35 % → 1.87 dB);
  7-PRF MPRF set (5.75–10.25 kHz, 10 GHz, ±15 m/s notch) ≥3-of-7 clear over 97.5 %; CRT exact; noisy residues σ =
  0.1/0.25 cell: exact CRT 84/59 % vs coincidence search 99.8/72 %; MTD N = 8: Cheb-40 best (median 40.8 dB vs rect
  31.6, Cheb-60 30.9); N = 16 Cheb-60 63.1 dB; CA-CFAR Pfa rect ≈ design, Hamming +11–21 %; T_max = √(λ/2a) (10 g,
  5.8 GHz: 16.2 ms; loss 0.24 dB at T_max, 4.0 dB at 2T_max); DIY baseline 100 mW/1 µs/256 pulses −16.7 dB on a
  0.01 m² drone at 1 km → design B (10 W, 4 µs, 1024 pulses) 15.4 dB, blind range 749 m.
- 2026-10-12 — OWN ERRORS logged (pre-registered expectations): 1b gain ×M for a non-coherent channel sum (wrong;
  mean SNR gains only τf_s·N) and TB instead of τf_s for per-sample SNR at f_s = 2B (3 dB); first noise estimate
  median/ln2 biased for a 4-channel sum; 1c "140 m/s aliases" — arithmetic error (v_u = 258 m/s); 6a "Cheb-60 best
  at N = 8" — main lobe too wide, 40 dB optimal (consistent with ASR-9 40 dB); 9 DIY baseline "≥ 13.2 dB at 1 km" —
  ignored energy (25.6 µJ); redesigned by the energy form.
- 2026-10-13 — indexes, sources, taxonomy updated; INDEX/FAQ rebuilt (279 pages); all four e8_ scripts ALL PASS. COMPLETE.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| 1 | Bayliss 1968, BSTJ 47(5):623–650 (archive.org bstj47-5-623 djvu text) | peer-reviewed | Bayliss model, polynomial table, line-source series | READ; table transcription verified via p0 peak check (0.991·σp0) |
| 2 | G3SEK "Stacking Yagi antennas" (ifwtech) | amateur engineering | capture areas, DL6WU formula, 2.5–2.9 dB | READ raw HTML |
| 3 | Cebik W4RNL 2 m stacks part 1 | amateur expert | gain-peak spacing > formula; increments 2.2–2.9 dB over ground | WebFetch summary only (rule 8) |
| 4 | MIT LL / IEEE NH Radar Systems Course lectures 13, 14 (O'Donnell) | lecture notes | PRF classes, eclipsing, MTD, CRT | READ via pdftotext (mirror) |
| 5 | Oxford maths node 8863 (Stove 2011) | problem statement | MPRF design problem | read (WebFetch) |
| 6 | arraytool (zinka) planar.py | code | checked what its "Bayliss" does (McNamara–Zolotarev) | not used |

## Contradictions / discrepancies found
- KB 08 yagi page "stacking distance ≈ 51/HPBW λ (DL6WU program)" vs G3SEK's DL6WU formula λ/(2 sin(B/2)) ≈ 57.3/B: 11–14 % apart. NEC: both within 0.4 dB of max gain; 51/B ≈ 0.3 dB less gain with ≈ 3 dB lower stacking lobes. Flag for W6 audit / 08 owner (attribution).
- Amateur "2.5–2.9 dB" stack gain vs free-space lossless NEC 2.9–3.1 dB: explained by harness loss/structure/ground; Cebik's over-ground increments fall with Yagi size (2.2 dB at 18 el) — not reproduced (free space only).
- Own pre-registration errors (all logged above): cardioid D, LP edge vs Dolph first null, csc² N, 2-D thin-wire TM scattering, small-ka slot ripple (2 attempts), grazing level, pseudo-Doppler hold delay, NEC average-gain grid, box range, non-coherent gain ×M, TB vs τf_s, 140 m/s aliasing, MTD window, DIY energy.

## Knowledge gaps noticed (for later gap-filling)
- Circular Taylor/Bayliss synthesis; phase-only and power-pattern synthesis; Elliott perturbation method.
- Independent TE 2-D MoM (or openEMS) for slot-on-cylinder; 3-D finite airframe wraparound model incl. nose cone/fins; measured roll ripple.
- Yagi stacks over real ground, with mast/H-frame; stacked crossed (CP) Yagis.
- Airborne pulse-Doppler clutter folding, HPRF FM-ranging, PRF-set optimisation, MTD clutter map; measured DIY pulse-Doppler data.

## Cross-domain notes (things other domains should cover/link)
- 08/yagi-uda-and-log-periodic.md: link to 12/stacking-and-arraying-yagis.md; reconcile/clarify the 51/HPBW stacking-distance statement.
- 08/antennas-on-rockets.md: link to 12/conformal-and-cylindrical-arrays.md (wraparound element-count table).
- 12/tapering-sidelobe-control.md: its Level-3 synthesis one-liners and "Bayliss not implemented" open question can now point to 12/array-pattern-synthesis.md.
- 11/clutter-and-mti.md and 11/pulsed-radar-and-pulse-compression.md: link to 11/pulse-doppler-data-cube-and-prf-regimes.md (PRF regimes, CRT robustness, MTD).
- 20/ground-station-tracking-yagi.md and 15/ground-station-design.md: link to the stacking page (CP before stacking).

## Resume instructions (what the next agent should do if this one is interrupted)
- Task complete; nothing to resume. Optional follow-ups are under Knowledge gaps and Cross-domain notes.
