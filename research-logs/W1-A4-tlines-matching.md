# Research log W1-A4: 03-transmission-lines-matching
Status: complete
Owner scope: kb/03-transmission-lines-matching/, research-logs/W1-A4-tlines-matching.md, tools/verify/tline_*.py

## Plan
Order chosen so that later pages can link back to derived results (foundations first).
- [x] telegrapher-equations-characteristic-impedance — done (kb/03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md; verified tools/verify/tline_telegrapher.py)
- [x] reflections-vswr-return-loss-mismatch — done (verified tools/verify/tline_reflections.py)
- [x] input-impedance-stubs-quarter-wave — done (verified tools/verify/tline_input_impedance.py)
- [x] smith-chart — done (verified tools/verify/tline_smith.py; figure figures/smith-chart-anatomy.png)
- [x] impedance-matching-lumped-and-distributed — done (verified tools/verify/tline_matching.py)
- [x] broadband-matching-bode-fano — done (verified tools/verify/tline_bode_fano.py, ~2 min)
- [x] s-parameters — done (verified tools/verify/tline_sparams.py)
- [x] planar-lines-microstrip-stripline-cpwg — done (verified tline_fd2d.py, tline_microstrip.py, tline_cpwg.py)
- [x] coax-and-cables — done (verified tools/verify/tline_coax.py)
- [x] time-domain-reflectometry — done (verified tline_tdr.py)
- [x] signal-flow-graphs-mason — done (verified tline_mason.py)
- [x] _index.md, _sources.md — done

Verification scripts planned (tools/verify/):
- tline_telegrapher.py — RLGC -> Z0, gamma vs skrf; low-loss approx error; distortionless
- tline_reflections.py — conversion table; mismatch loss; lossy line masking SWR
- tline_input_impedance.py — Zin formula vs skrf cascade; stubs
- tline_smith.py — Mobius map properties, constant circles
- tline_matching.py — L/Pi networks, stubs, binomial/Chebyshev, Klopfenstein, finite-Q loss; 433/915/2450 examples
- tline_bode_fano.py — Bode-Fano bound numerics vs Chebyshev match achievable
- tline_sparams.py — conversions, unitarity, renormalisation, mixed-mode, T-params, group delay
- tline_microstrip.py / tline_cpwg.py / tline_stripline.py — calculators + validation
- tline_coax.py — Z0, 30/77 ohm optima, loss model
- tline_tdr.py — IFFT TDR of synthetic discontinuities, windowing
- tline_mason.py — Mason vs direct matrix; mismatch uncertainty limits

## Log (append-only)
- 2026-09-27 — Read CONVENTIONS.md, INDEX.md, HANDOFF.md, CLAUDE.md. Created this log.
- 2026-09-27 — Qucs tech docs node75 (microstrip): H-J quasi-static Z0/eeff, thickness correction, K-J dispersion (P1..P4, R1..R17), loss formulas. (WebFetch summary garbled some parentheses in R8 and dW1 — rely on skrf MLine source + own FD field solver for validation.) -> planar-lines page.
- 2026-09-27 — JLCPCB jlcpcb.com/impedance: 4L JLC04161H-7628 prepreg 0.2104 mm Dk 4.4; -3313 0.0994 mm Dk 4.1; -1080 0.0764 mm Dk 3.91; 2116 0.1164 mm Dk 4.16; core Dk 4.6; outer Cu 0.035 mm. JLC impedance-calculator guide: outer Cu 1.6 mil, inner 0.6 mil (0.5 oz), soldermask 1.2 mil er 3.8, NP-155F for 4-8L. JLCPCB custom-pcb page: 2-layer FR-4 Dk ~4.5, Df ~0.02. -> planar-lines page.
- 2026-09-27 — Cable datasheets (pdftotext of WebFetch-saved PDFs): L-com LMR-400/240/195 (loss tables 50 MHz-5.8 GHz, VF 85/84/80 %, dims); Belden 8240 RG-58 (loss 1-1000 MHz, 52 ohm nominal 51.5+/-1.5, VF 66 %, dims); Fairview RG174 (19 dB/100ft @400 MHz, 32 @1 GHz), Fairview RG316 (21 @400 MHz, 38 @1 GHz, 58 @3 GHz dB/100ft); Pasternack RG402 (11.1 dB/100ft @1 GHz, 43.4 @10 GHz), RG405 (22 @1 GHz, 80 @10 GHz); Hirose U.FL catalog (DC-6 GHz, 30 mating cycles, 1.13 mm cable 3.73 dB/m @3 GHz, 5.44 @6 GHz). -> coax page.
- 2026-09-27 — Wrote telegrapher page + tline_telegrapher.py (all pass). Found my first draft of Example 3 had an unverified Zin number; recomputed with skrf MLine (0.5 mm trace on 1.6 mm FR-4 = 108 ohm, 25 mm -> 56.5+j33.9 ohm).
- 2026-09-27 — Searched return-loss sign convention (Bird 2009 IEEE APM editorial), reflected-power myth (IZ2UUF blog, Maxwell Reflections, K6OIK Stearns paradox paper cited in skrf), SWR-vs-cable-length forum threads. Wrote reflections page + tline_reflections.py (all pass).

- 2026-09-27 — Wrote input-impedance/stubs page + script (all pass). Wrote Smith chart page + script (all pass) incl. figure; NanoVNA formats from WA5OKO user guide and PA3A tutorial. Fixed constant-Q centre sign in my own first test (upper arc centred at (0,-1/Q)).

- 2026-09-27 — Wrote matching page + tline_matching.py (all pass). Murata LQW15AN/LQG15HS Q figures from distributor listings (Q min at test freq only).

- 2026-09-27 — (resumed after API limit) Bode-Fano script: Nelder-Mead and differential evolution stuck at |G|~0.171 for 3-4 resonators; SLSQP epigraph minimax found 0.110/0.084 (monotone toward bound 0.043). Wrote Bode-Fano page. Sources: Bode 1945, Fano 1950, Pozar 5.9, Matthaei 4.09, Chu 1948, McLean 1996, Yaghjian-Best 2005, Shlivinski-Hadad PRL 2018 (arXiv 1805.03704).

- 2026-09-27 — Wrote s-parameters page + tline_sparams.py (all pass). Sources: Kurokawa 1965, Marks-Williams 1992 (NIST JRES free), Frickey 1994, Bockelman-Eisenstadt 1995, Rollett 1962, Edwards-Sinsky 1992, Keysight AN154 (5952-1087), IBIS Touchstone 2.0/2.1 spec (2.1 ratified 26 Jan 2024), Dobrowolski 2016 (skrf T convention). Found skrf T convention [b1;a1]=T[a2;b2].

- 2026-09-27 — Wrote tools/verify/tline_fd2d.py (own FV Laplace solver, graded mesh, Richardson extrapolation): reproduces Cohn exact stripline within 0.13 %. tline_microstrip.py: H-J vs FD within 0.4 % (W/h 0.1-10, er 2.2-10); H-J thickness correction within 0.2 % of FD; own K-J == skrf; Wheeler-78 stripline within ~1 % of FD. tline_coax.py all pass (optimum ratios 3.591/sqrt(e)/e; datasheet fits; P*alpha const).
- 2026-09-27 — Cross-check vs published JLCPCB-stackup designs: JITX jlcpcb.JLC04161H_7628 (RS_50 0.3244 mm; DRS_100 0.1722/0.15; DRS_90 0.2332/0.15) and LibreCAL PR #8 (CPWG 0.34/0.20 mm Saturn PCB Toolkit; built 0.30/0.18 mm). FD bare-board gives DRS_100 = 109 ohm and DRS_90 = 97 ohm; with gap-filling soldermask (er 3.8, +10 um over Cu) 98.4 and 88.9 ohm -> JITX numbers evidently include soldermask. Single-ended 50 ohm on JLC7628: H-J/FD bare 0.372 mm; with mask ~0.35 mm; JITX 0.3244 mm is ~7 % narrower still (open discrepancy).
- 2026-09-27 — PTFE phase knee: Times Microwave / Microwave Journal articles (knee 18-24 C, ~-130 ppm/C between 15-25 C vs -30 ppm/C below) -> coax page.

- 2026-09-27 — (resumed again after 2nd limit) tline_cpwg.py ALL PASS: Ghione-Naldi CPWG within 1 % of FD (t=0); formula invalid for S >= 2h (overestimates; FD -> microstrip). 1.6 mm 2-layer CPWG 50 ohm (35 um Cu, no mask): gap 0.15/0.20/0.25/0.30 mm -> W 0.76/1.01/1.22/1.39 mm (microstrip 2.80 mm). JLC7628 CPWG 0.34/0.20: 48.7 ohm bare, 45.7 with mask; LibreCAL 0.30/0.18: 51.1 bare / 47.6 masked.
- 2026-09-27 — Cross-checked own FD vs W1-A3's independent FD (tools/verify/em_inductance.py strip_capacitance, uniform grid): both within 1 % of H-J for w/h 0.5-3 on er 4.4 (mine: 95.44/70.95/50.16/37.39 ohm vs H-J 95.45/71.03/50.22/37.47).
- 2026-09-27 — Keysight AN 1287-12 (5989-5723EN, via testunlimited.com copy, pdftotext): window table min/normal/max: step rise 0.45/0.99/1.48 per span, LP impulse width 0.60/0.98/1.39, impulse sidelobes -13/-44/-75 dB, step sidelobes -21/-60/-70 dB; bandpass impulse width 2x; alias-free range 1/df. tline_tdr.py reproduces rise/width constants within 2 % with Kaiser beta 0/6/13 and sidelobes -13/-44 dB (max window -98 dB vs -75: Keysight's 'maximum' is evidently not exactly beta 13). Two-event 3-dB-dip resolution = 1.25 x (0.98/span x v/2).

- 2026-09-27 — Wrote planar-lines, TDR and Mason pages; tline_mason.py all pass. Confirmed own FD agrees with W1-A3's em_inductance.py FD within 0.11-0.21 % (95.26/70.87/50.07/37.31 vs mine 95.44/70.95/50.16/37.39 ohm).

- 2026-09-27 — Wrote _index.md and _sources.md. Link check: all intra-domain links/anchors resolve (GitHub slug rules); all cross-domain links point to slugs planned in INDEX.md. Final runs: telegrapher, reflections, input_impedance, smith, matching, sparams, fd2d, coax, tdr, mason ALL PASS; microstrip (ms_out2) ALL PASS; cpwg ALL PASS; bode_fano rerun launched (last known run ALL PASS before adding Q_Z/Chu-table lines).

- 2026-09-27 — Final tline_bode_fano.py rerun: ALL PASS. Task complete.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| S1 | Qucs Technical Papers, microstrip section (qucs.sourceforge.net/tech/node75.html) | documentation of open-source simulator, cites H-J 1980 / K-J 1982 | planar-lines formulas | good secondary; primary papers paywalled |
| S2 | JLCPCB impedance stackups (jlcpcb.com/impedance) + calculator guide + custom-pcb page | manufacturer | stackup numbers | manufacturer data, may change |
| S3 | L-com LMR-400/240/195 datasheets (Times Microwave data) | datasheet | coax loss tables | manufacturer |
| S4 | Belden 8240 RG-58 techdata (rev 02-20-2026) | datasheet | RG-58 loss | manufacturer |
| S5 | Fairview Microwave RG174, RG316 datasheets | datasheet | loss tables | distributor/manufacturer |
| S6 | Pasternack RG402/U, RG405/U datasheets | datasheet | semi-rigid loss | manufacturer |
| S7 | Hirose U.FL series catalog (2020) | datasheet | U.FL freq range, VSWR, 30 mating cycles, micro-coax loss | manufacturer |
| S8 | Keysight AN 1287-12 (5989-5723EN) | app note | TDR window constants, ranges | manufacturer app note, read via pdftotext |
| S9 | JITX jlcpcb.JLC04161H_7628 docs; LibreCAL PR #8 | software docs / forum | published JLC routing widths | secondary |
| S10 | Kurokawa 1965; Marks & Williams 1992; Bird 2009; Klopfenstein 1956; Kajfez-Prewitt 1973; Bode 1945; Fano 1950; McLean 1996; Yaghjian-Best 2005; Shlivinski-Hadad 2018 | peer-reviewed | theory | bibliographic details via search; content from textbook knowledge + numerical checks |
| — | Full bibliography: kb/03-transmission-lines-matching/_sources.md | | | |

## Contradictions / discrepancies found
- JITX JLC04161H_7628 RS_50 = 0.3244 mm vs our H-J/FD 0.372 mm bare / ~0.35 mm with soldermask (7-13 % narrower); JITX diff-pair values reconcile with FD only when soldermask is included. Recorded on planar-lines page.
- Fairview RG-316 attenuation table (1->3 GHz rises by 1.53x) is inconsistent with the k1 sqrt(f)+k2 f law (sqrt(3)=1.73) — flag the 3 GHz value.
- RG-174/RG-316 nominal dimensions + VF give ~45 ohm (stranded centre conductor: effective diameter < OD). Datasheet dimension conventions.
- Hammerstad-Jensen a(u) term: WebFetch summary of Qucs page garbled it; correct form (confirmed from skrf source and agreement with FD): a = 1 + ln[(u^4+(u/52)^2)/(u^4+0.432)]/49 + ln[1+(u/18.1)^3]/18.7.
- Small-reflection theory vs exact cascades (own finding, tline_matching.py): binomial BW formula (Pozar) optimistic by ~1.5 points at 2:1 and 5-7 points at 5:1; Chebyshev synthesis from small-reflection theory gives 0.060-0.068 ripple instead of 0.05 at 5:1 (exact minimax optimum over the same band 0.0555); Klopfenstein 5:1 at Gm 0.02 gives 0.026. At 2:1 all agree to <5 %. Recorded on the matching page.
- scikit-rf DefinedGammaZ0 default gamma = 1j (1 rad/m) — .line() lengths in metres are then NOT free-space; must pass gamma explicitly. Trap noted on matching page.
- skrf.taper.Klopfenstein end-step handling differs from Pozar's textbook form (skrf forces the final value to 'stop'); responses differ by <0.002 in |Gamma|.
- scikit-rf Network.delay(d, unit) on a 1-port treats d as ROUND-TRIP (adds a line of d/2): verified numerically; noted in smith-chart snippet.
- Belden 8240 RG-58 datasheet nominals are mutually inconsistent at ~5 %: 52 ohm stated, but 1/(vp*C) with its own 93.5 pF/m and VF 0.66 gives 54 ohm, and geometry (0.838 mm / 2.95 mm, er from VF) gives 49.8 ohm. Recorded in telegrapher page Example 1.
- Real RG-58 loss exceeds smooth-solid-copper theory by 10 % (100 MHz) to 26 % (1 GHz) — braid/tin/roughness; not a contradiction but a model limit.
- "Reflected power heats the PA": ham literature (Maxwell W2DU) vs later critics; resolved on the page by showing Thevenin-source dissipation depends on Gamma phase and that real PAs are not Thevenin 50 ohm sources.

## Knowledge gaps noticed (for later gap-filling)
- Measured TDR of JLCPCB impedance coupons (calculator spread ~3 ohm: soldermask thickness over Cu vs in gaps unpublished).
- JITX RS_50 0.3244 mm on JLC7628 vs our 0.343 mm (masked) / 0.372 mm (bare): unresolved ~5-13 %.
- Coupled-microstrip closed forms (Kirschning-Jansen coupled), trapezoidal etch, offset stripline (6-layer JLC).
- Exact Riblet Chebyshev transformer tables; Fano finite-n closed forms; double-stub forbidden region.
- EBYTE E22/E220 module output impedance / VSWR protection not documented in sources read.
- Primary Times Microwave / Huber+Suhner PDFs returned HTTP 403; distributor copies used.
- Keysight AN 1449-3 (power uncertainty) and Tektronix TDR note cited from general knowledge, not re-fetched.
- NanoVNA firmware TDR internals (window/DC extrapolation) not verified.

## Cross-domain notes (things other domains should cover/link)
- 02-electromagnetics: causal wideband dielectric models (Djordjevic-Sarkar/Svensson — skrf MLine default), Huray/Groiss roughness; our pages link skin-effect-conductor-loss-roughness and dielectrics pages. W1-A3's em_inductance.py FD agrees with our tline_fd2d.py within 0.2 %.
- 04-real-components-hf: via inductance (rule of thumb used: ~1 nH through 1.6 mm, 0.05-0.1 nH through 0.2 mm prepreg), 0402 L/C Q-vs-f curves and SRF (matching page quotes ranges only), 0-ohm jumper ~0.5 nH.
- 06-rf-circuits: PA load-line/load-pull and VSWR ruggedness; LNA noise vs gain match; stability circles (only previewed here); baluns/common-mode chokes (reflections page relies on them).
- 08-antennas: small-antenna Q vs Chu (factors 1.5-3), chip-antenna ground-plane dependence (Bode-Fano page examples), antennas in rocket airframes (detuning).
- 13-pcb-rf-layout-emc: CPWG via-fence spacing, soldermask handling, JLCPCB impedance ordering/tolerance, connector launches (U.FL pad capacitance example on TDR page).
- 15-lora-ism-radios: ground-station feeder choice (coax page Example 1 numbers), masthead LNA.
- 17-test-measurement: VNA SOL/TRL calibration, port extension, TDR practice, power-meter uncertainty budgets (Mason page), NanoVNA effective directivity.

## Resume instructions (what the next agent should do if this one is interrupted)
- Task is essentially COMPLETE: all 11 topic pages + _index.md + _sources.md exist in kb/03-transmission-lines-matching/; all tline_*.py scripts pass.
- All scripts confirmed passing (final Bode-Fano rerun ALL PASS). Nothing outstanding; future work = gaps listed above.
- Do not edit HANDOFF.md (orchestrator-owned).
