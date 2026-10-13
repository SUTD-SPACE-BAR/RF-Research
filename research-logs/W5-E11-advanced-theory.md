# Research log W5-E11: advanced theory pack (Level-3 rungs)
Status: complete (2026-10-13)
Owner scope: NEW files only —
- kb/03-transmission-lines-matching/microstrip-discontinuities.md
- kb/02-electromagnetics/greens-functions-and-integral-equations.md
- kb/17-test-measurement/resonator-and-cavity-perturbation-permittivity-measurement.md
- kb/07-noise-linearity/volterra-series-and-nonlinear-analysis.md
- kb/10-comms-modulation/mimo-capacity-and-channel-estimation.md
- kb/13-pcb-rf-layout-emc/digital-termination-and-crosstalk.md
- tools/verify/e11_*.py
Plus: one-line cross-links on pages that cite these methods; _index.md, _sources.md of 02/03/07/10/13/17;
tools/taxonomy.md lines for 02/03/07/10/13/17. Do NOT edit other agents' new files in 03/10/17.

Origin: gaps/D4-curriculum.md top-50 #10, #11, #14, #17, #21, #23 and §4 level check ("broken rungs").

## Plan
- [x] 03 microstrip-discontinuities (written 2026-10-13, 250 lines) — open end (Kirschning), step, bend/mitre (Douville–James), T, gap, via; closed-form limits; openEMS/quasi-static check of ≥2
- [x] 02 greens-functions-and-integral-equations (written 2026-10-13, 250 lines) — scalar & dyadic G, EFIE/MFIE, Pocklington/Hallén (link 08 MoM), Sommerfeld/layered media outline, MoM
- [x] 17 resonator-and-cavity-perturbation-permittivity-measurement (written 2026-10-13, 256 lines) — perturbation derivation, split-post/split-cylinder, ring resonator & two-line on JLC FR-4 with NanoVNA, coupling & Q0 extraction, nose-cone fibreglass
- [x] 07 volterra-series-and-nonlinear-analysis (written, 250+ lines, Saleh Ex. 4 re-checked) — kernels, nonlinear currents, IIP3 with memory, power-series limits, AM-PM, Rapp/Saleh/memory polynomial, DPD link
- [x] 10 mimo-capacity-and-channel-estimation (written, ≥ 250 lines, links OK) — channel model, SVD + water-filling (derive), diversity vs multiplexing, Alamouti, LS/MMSE estimation, OFDM pilots, ground-station diversity
- [x] 13 digital-termination-and-crosstalk (written, ≥ 250 lines) — reflections, rise time vs length, termination schemes, NEXT/FEXT from Lm/Cm, 3W rule numerically, clocks near RF
- [x] taxonomy (02/03/07/10/13/17), _index rows, _sources sections, 12 one-line cross-links; build_index --check: 0 broken links, 0 missing sections (284 pages)

## Log (append-only)
- 2026-10-03 — Step 0: read CONVENTIONS, HANDOFF, D4 §2 rows #10/#11/#14/#17/#21/#23 and §4. canonical-values-and-conventions.md does NOT exist yet (W5-E9 still running) — use CONVENTIONS rule 5 and the canonical width table in 13/stackups-and-materials.
- 2026-10-03 — Discontinuities sources: Qucs-core C++ source (msopen/msgap/msstep/mscorner/msmbend/mstee/msvia.cpp, GitHub Qucs/qucs master) + Qucs technical papers node76–83 (LaTeX alt text, raw curl, not WebFetch) + Qucs bibliography node103. Kirschning–Jansen–Koster 1981 open end (5 Q-terms, <2.5 % for 0.01≤u≤100, εr≤50); Hammerstad 1981 open end; Kirschning–Jansen–Koster 1983 corner & 50 % mitred bend (W/h 0.2–6, εr 2.36–10.4, ≤14 GHz, ~0.3 %); Gupta et al. step (εr≤10, 1.5≤W1/W2≤3.5); Kirschning gap; Hammerstad 1981 T-junction; Goldfarb–Pucel via. Douville–James optimum mitre M = 52+65 exp(−1.35 W/h) % confirmed by Wikipedia raw (cites MTT-26(3):175–182, evidence 0.25≤W/h≤2.75, 2.5≤εr≤25, VSWR<1.1 within ±4 % of M) and leleivre.com calculator JS (x/d = 0.52+0.65 exp(−1.35W/h)).
- 2026-10-03 — openEMS debugging: port Z/beta extraction is ill-conditioned inside the open-end standing wave (gave eeff 3.79); fixed by reference subtraction (open run minus matched "through" run on the identical mesh; beta from the through run → eeff 3.398, Z 50.04 at 915 MHz, λ/30 mesh). All-PML boundaries (MUR walls trapped surface waves; end criterion never reached). Wrote tools/verify/e11_discontinuities_openems.py (open ends W 2.80/0.75 mm; bends square/50 %/D-J/75 %) and tools/verify/e11_discontinuities.py (closed forms + openEMS comparison; NOT yet run). Full openEMS run was started then KILLED at PAUSE (no results saved).

- 2026-10-12 — RESUMED. openEMS run complete (~12 min total; results in tools/verify/e11_discontinuities_openems_results.txt + data/e11_openems_discontinuities.npz). Square bend |S11| matches KJK corner model within 0.7 dB (−20.2 vs −19.5 dB at 2.45 GHz); 50 % mitre KJK model −29.8 vs openEMS −29.4 dB; D-J optimum (57.3 %) −36.2 dB at 2.45 GHz, −28.0 dB at 5.8 GHz (16 dB better than square); 75 % worse (−24.3). PRE-REGISTERED MISS: open-end Δl from openEMS is +11.5 % (W/h 1.85) and +18 % (W/h 0.5) above KJK, mesh-converged to 0.5 % (coarse vs fine) — reported faithfully. Closed forms: three open-end models agree < 5 % near 50 Ω but spread 15 % at u = 0.1 and u = 8 (my 8 % expectation missed). e11_discontinuities.py 15/18.
- 2026-10-12 — e11_greens.py 14/14 (after fixing a buggy first Hallen implementation: unstable end condition + Gauss on near-singular kernel; final: N+1 match points incl. wire end, analytic asinh self term; Richardson-extrapolated Hallen 80.38+j45.38 vs Galerkin 80.21+j44.96 Ω for a = 1e-4 λ). Square-plate MoM extrapolates to C/(4πε0a) = 0.367 (within Hwang & Mascagni 2004's 0.36 ± 0.01; 1.7 % above the 0.3607 often quoted — from knowledge, not re-checked). Sommerfeld identity to 1e-10; TM0 pole β/k0 − 1 = 2.5e-4 at 915 MHz on 1.51 mm FR-4.
- 2026-10-12 — e11_permittivity.py: cavity perturbation vs 2-D FD eigen (rod ∥ E, 100 mm TE101 cavity) within 1–3 % for Δf/f < 2 %; coupling Q0 extraction exact to < 1 % except very strong coupling (|S21| −0.5 dB: −1.04 %); ring resonator: uncorrected εr bias +1.8 % (1 mm gaps) / +2.5 % (0.25 mm) from gap capacitance loading — my 1 % expectation missed; model-based fit removes it; tanδ within 5.3 %. Two-line eigenvalue method exact despite connector boxes. Free-space slab fit: thickness error dominates (+0.1 mm → −3.3 % εr).

- 2026-10-13 — PAGE 1 written: kb/03-transmission-lines-matching/microstrip-discontinuities.md. Next: page 2 (Green's functions), script e11_greens.py done 14/14.

- 2026-10-13 — PAGE 2 written: kb/02-electromagnetics/greens-functions-and-integral-equations.md; e11_greens.py 15/15 (added explicit-dyadic check). Next: page 3 (17 permittivity).

- 2026-10-13 — PAGE 3 written: kb/17-test-measurement/resonator-and-cavity-perturbation-permittivity-measurement.md (e11_permittivity.py 15/17; misses: εr=10 rod 3.2 % > 3 % bound; extreme over-coupled transmission Q0 −1.04 %). Next: page 4 Volterra.

- 2026-10-13 — e11_volterra.py 9/11: Wiener–Hammerstein kernel exact; nonlinear-currents Volterra vs RK4 ODE within 0.32 dB (miss vs 0.3 dB bound, at −94 dBc where g3 and g2² terms nearly cancel); IM3 spans 31 dB over 0.1–5 MHz spacing, IIP3 +3.5 → −12.6 dBm as spacing crosses the 1 MHz bypass corner; lower/upper asymmetry up to 9.2 dB. DPD: memory-polynomial DPD −60.4 vs memoryless −56.1 dBc ACLR (4.3 dB, miss vs 5 dB bound) though model NMSE differs by 34 dB — linear memory inflates NMSE but not ACLR. First DPD attempt (0.35 rms drive) made ACLR worse than no DPD: over-driven into saturation.

- 2026-10-13 — PAGE 4 written: kb/07-noise-linearity/volterra-series-and-nonlinear-analysis.md (not yet length/link-checked). PAUSED.

- (resumed) Volterra page finished (250 lines). e11_mimo.py 27/27 — note: first OFDM-pilot check used a wrong threshold (MSE < −25 dB when the noise floor IS −25 dB for N/D = L); replaced by the theory value σ²L/Np (−28.0/−25.0 dB matched to 0.1 dB). Next: MIMO page.

- PAGE 5 written: kb/10-comms-modulation/mimo-capacity-and-channel-estimation.md (238 lines; e11_mimo.py 27/27). PAUSED (#3).

- e11_crosstalk.py 12/14: Bergeron sim — overshoot 5.2 % at TD = tr/10 (miss vs < 5 % bound), 10 % at TD/tr ≈ 0.16, 35 % for long lines (Rs 25 Ω, 5 pF); AC termination (50 Ω + 100 pF) has no overshoot but a slow RC tail (13.5 ns to 5 %) — miss vs "settles faster" expectation. NEXT/FEXT formulas from field-solver Lm/L, Cm/C match exact even/odd modal simulation within 1–5 %; FEXT negative; stripline εe = εo. 3W: −27.5 dB NEXT on 7628 (W 0.2 mm) but −15.5 dB on 1.5 mm 2-layer (W 0.3 mm). Clock beside RF trace at 920 MHz, 10 mm run: −25.6/−34.2/−43.1/−53.8 dB for 0.2/0.5/1/2 mm gaps.

- PAGE 6 written: kb/13-pcb-rf-layout-emc/digital-termination-and-crosstalk.md. Next: cross-links, indexes, taxonomy, build_index --check.

- Final: taxonomy + indexes + cross-links done (03/planar-lines, 03/stubs, 02/radiation, 02/waveguides, 02/dielectrics, 07/nonlinearity, 06/power-amplifiers, 10/ofdm, 00/matrices, 13/mixed-signal, 13/grounding, 16/em-solvers). build_index --check clean. COMPLETE.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| 1 | qucs-core ms*.cpp + Qucs tech papers §11 (curl, LaTeX alt text) | software docs | all discontinuity formulas | raw text, not summariser |
| 2 | Wikipedia "Microstrip" raw; leleivre.com calculator JS | secondary | Douville–James mitre | two consistent secondaries |
| 3 | Hwang & Mascagni 2004 (search abstract) | peer-reviewed | square-plate C 0.36 ± 0.01 | abstract only |
| 4 | MathWorks / IEEE 802.16 / patent (search) | docs | Saleh parameters | α_φ discrepancy |
| 5 | Textbooks cited from knowledge: Gupta et al., Harrington, Gibson, Chew, Pozar, Chen et al., Maas, Wambacq & Sansen, Tse & Viswanath, Bogatin, Hall & Heck, Johnson & Graham | textbook | derivations (re-derived and numerically checked) | chapter-level |

## Contradictions / discrepancies found
- Saleh TWT AM-PM parameter α_φ: 4.0033 (MathWorks comm.MemorylessNonlinearity default) vs 4.033 (IEEE 802.16 impairment presentation, a USPTO patent) — via WebSearch summary 2026-10-13; KB uses 4.0033 and notes the variant.
- Open-end Δl: openEMS +11–18 % above Kirschning–Jansen–Koster (unresolved; see page 1).
- 03/input-impedance-stubs attributes the 0.412 open-end formula to "Hammerstad 1975 as reproduced in Qucs"; Qucs reproduces a different Hammerstad-1981 (0.102…) form. Numbers agree (~0.39h).

## Knowledge gaps noticed (for later gap-filling)
- openEMS vs KJK open-end Δl (+11–18 %) unresolved — needs 3-D excess-charge solve or Sonnet/literature comparison.
- No CPWG discontinuity closed forms; no layered-media MoM implemented; square-plate value 0.3607 not re-checked.
- Measured data needed: JLC FR-4 ring/two-line εr, Space Bar fibreglass coupon, ESP32/i.MX RT GPIO edge rates, dual-receiver ground-station correlation.
- SPDR/split-cylinder fixture K-tables; ASTM D2520 text not obtained.

## Cross-domain notes (things other domains should cover/link)
- 13/stackups and 02/dielectrics: add measured εr when the 17 ring/two-line recipe is run.
- 15/ground-station-design: could link the MIMO page's dual-receiver (polarisation/height diversity) recipe.
- 08/antennas-on-rockets: could link the 17 nose-cone εr recipe (not edited — kept to the listed cross-link set).
- 12-phased-arrays: periodic (Floquet) Green's function still missing (D4).

## Resume instructions
PAUSED (third pause). Done: pages 1–4 complete (03 discontinuities, 02 Green's functions, 17 permittivity, 07 Volterra — each ≥ 250 lines); page 5 (10 MIMO) written at 238 lines; scripts e11_discontinuities(+_openems), e11_greens, e11_permittivity, e11_volterra, e11_mimo all run, outputs in tools/verify/e11_*_output.txt.
1. MIMO page: add ~12 lines (e.g. more Practical notes / Open questions), run `python3 tools/build_index.py --check | grep mimo-capacity`, tick Plan.
2. Page 6: write tools/verify/e11_crosstalk.py (lossless-line lattice/time-domain sims of series/parallel/Thevenin/AC termination with CMOS driver ~25 Ω + 5 pF load; overshoot vs TD/t_r; NEXT/FEXT coefficients Kb = ¼(Lm/L + Cm/C), Kf = ½(Cm/C − Lm/L)·len/(v t_r) from tline_fd2d.coupled_params (even/odd Z, εeff → L, C matrices); check vs even/odd modal frequency-domain coupled-line simulation; 3W rule vs spacing on JLC-7628 0.2 mm traces and 2-layer; clock harmonic coupling into RF trace), then kb/13-pcb-rf-layout-emc/digital-termination-and-crosstalk.md (≥250 lines, template; link 13/mixed-signal-layout, 13/grounding-and-return-paths, 03/time-domain-reflectometry, 03/reflections…).
3. Cross-links (one line each) from: 03/planar-lines, 03/input-impedance-stubs (open end + attribution note), 02/radiation-from-currents, 02/waveguides-and-cavity, 02/dielectrics (fibreglass gap → 17 page), 07/nonlinearity, 06/power-amplifiers, 10/ofdm, 00/matrices, 13/mixed-signal, 13/grounding, 16/em-solvers; update _index.md + _sources.md of 02/03/07/10/13/17; add slugs to tools/taxonomy.md lines (02, 03, 07, 10, 13, 17); run `python3 tools/build_index.py --check`; set Status complete.
Background jobs: none.
