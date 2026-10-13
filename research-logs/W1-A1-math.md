# Research log W1-A1: 00-math-foundations
Status: complete
Owner scope: kb/00-math-foundations/ ; research-logs/W1-A1-math.md ; tools/verify/math_*.py

## Plan
Order of writing (dB first because every other domain leans on it; roadmap last because it links all):
- [x] decibels-and-log-units — DONE (kb/00-math-foundations/decibels-and-log-units.md, verify tools/verify/math_decibels.py ALL PASS) — 10 vs 20 log, every dB unit, Neper, dBm<->V at 50 ohm, coherent vs incoherent addition, tables, mental math
- [x] complex-numbers-and-phasors — DONE (verify tools/verify/math_complex_phasors.py ALL PASS) — Euler, polar/rect, phasors from sinusoidal steady state, complex impedance, RMS/peak/PEP/avg, complex power, analytic signal, negative frequency
- [x] fourier-series-and-transform — DONE (verify tools/verify/math_fourier.py ALL PASS) — series/transform, pulse-train & square-wave spectra (clock EMI), sinc, time-bandwidth, Parseval, convolution/modulation theorems, pulsed RF, chirp, DFT basics
- [x] laplace-transfer-functions-bode — DONE (verify tools/verify/math_laplace_bode.py ALL PASS) — s-domain, poles/zeros, Bode sketching, stability, minimum phase, group delay, s vs jw
- [x] linear-systems-convolution — DONE (verify tools/verify/math_linear_systems.py ALL PASS, ~20 s) — LTI, impulse response, causality, Hilbert, Kramers-Kronig, group/phase delay, dispersion
- [x] vector-calculus-for-em — DONE (verify tools/verify/math_vector_calculus.py ALL PASS incl. Hertzian dipole H_phi by sympy spherical curl) — grad/div/curl/Laplacian meaning, Gauss/Stokes, cylindrical/spherical, phasor vector fields
- [x] probability-random-processes-and-psd — DONE (verify tools/verify/math_probability_psd.py ALL PASS; shot-noise 2qI by Poisson simulation) — distributions (Gaussian/Rayleigh/Rician/exp/chi2/Poisson), autocorrelation, Wiener-Khinchin, white noise, ENBW, noise power addition, Q/erfc, CLT
- [x] differential-equations-circuits-waves — DONE (verify tools/verify/math_differential_equations.py ALL PASS) — 1st/2nd-order ODEs, zeta/wn, wave equation, separation of variables
- [x] special-functions-bessel-sinc — DONE (verify tools/verify/math_special_functions.py ALL PASS) — sinc, Bessel Jn (FM, apertures), jinc, Fresnel integrals, erf/Q, Chebyshev, Legendre
- [x] matrices-and-linear-algebra-for-networks — DONE (verify tools/verify/math_matrices.py ALL PASS) — nodal matrix, eigen, Z/Y/S preview, SVD (MIMO/arrays), least squares
- [x] numerical-methods-overview — DONE (verify tools/verify/math_numerical_methods.py ALL PASS) — root-finding, quadrature, FFT, ODE solvers, finite differences, FDTD/MoM/FEM concepts
- [x] math-roadmap-for-rf — DONE — maths-per-topic map + learning path, links every page
- [x] _index.md (anchors validated) ; [x] _sources.md (consolidated, with read/located/recalled status per source)
- [x] verification scripts: 11 x tools/verify/math_*.py, all ALL PASS (final run 2026-09-27)

## Log (append-only)
- 2026-09-27 — Read CONVENTIONS.md, INDEX.md, HANDOFF.md. kb/00-math-foundations empty. Created this log.
- 2026-09-27 — Wrote _sources.md. Final run: all 11 math_*.py ALL PASS; link check 0 bad; all 12 pages contain every CONVENTIONS s3 section. Pages are 169-334 lines but with long dense lines (~20-35 kB each). TASK COMPLETE.
- 2026-09-27 — Wrote math-roadmap-for-rf.md and _index.md. Link check (scratchpad linkcheck.py) of all pages vs INDEX.md (now auto-generated table format from tools/taxonomy.md): 0 bad links; _index anchors validated (1 typo fixed). Spot-checked overlaps with 10-comms BER (9.6 dB @1e-5), analog-modulation Carson, 01 two-port ABCD convention: consistent.
- 2026-09-27 — Wrote numerical-methods-overview.md (read Space Bar engineering-ethos.md to phrase validation tenets accurately).
- 2026-09-27 — Wrote tools/verify/math_numerical_methods.py (ALL PASS): root finding, quadrature, FFT, ODE stability, FD Laplace coax (2.7% staircase error at 161^2), 1-D Yee FDTD (vp=c at S=1; S=0.5 dispersion matches theory to 3e-5; S=1.05 unstable), MoM square plate, 1-D FEM. Fixed my FDTD phase-extraction bug (needed spatial unwrap) and wrong MoM reference.
- 2026-09-27 — Wrote matrices-and-linear-algebra-for-networks.md + math_matrices.py (ALL PASS; skrf z2s lives in skrf.network). Replaced a hand-wavy 'loaded Q=2 -> 200 MHz BW' claim with computed RL bandwidths (343-507 MHz @10 dB).
- 2026-09-27 — (resumed after API session limit) Wrote special-functions-bessel-sinc.md + math_special_functions.py (ALL PASS). Fixed own wrong hand value of Dolph x0 (1.1512 -> 1.1807). Uniform 8-element array first sidelobe is -12.8 dB (finite N), not -13.26.
- 2026-09-27 — Wrote differential-equations-circuits-waves.md + math_differential_equations.py (ALL PASS). Script caught my skin-depth slip (3.14 -> 3.18 um at 433 MHz). Sources: MIT 18.03 notes, Kreyszig 10e ch1-2,12 (recalled), Pozar s2.1/3.3, Griffiths ch9.
- 2026-09-27 — Wrote probability-random-processes-and-psd.md + math_probability_psd.py (ALL PASS). Self-caught error: first draft said Pd~0.5-0.6 at 13 dB SNR (Pfa 1e-6); ncx2 gives 0.87-0.90 -> corrected (11.2 dB for Pd 0.5, 13.2 dB for 0.9).
- 2026-09-27 — Wrote vector-calculus-for-em.md + math_vector_calculus.py (ALL PASS). Checked Space Bar avionics KB (sensor-calibration, design-lessons) before referencing magnetometer practice.
- 2026-09-27 — Wrote linear-systems-convolution.md + math_linear_systems.py (ALL PASS). Numerically showed constant-eps'/constant-tan-d model has 50% of dispersive impulse response at t<0; D-S model causal. Initial KK quad failed from bad scaling -> nondimensionalised (fixed).
- 2026-09-27 — Wrote laplace-transfer-functions-bode.md + math_laplace_bode.py (ALL PASS incl. Bode gain-phase integral reproducing -atan(w)). Sources: Cheever Swarthmore Bode notes, Keysight group-delay help, O&W ch6/9, MIT 18.03 s15-28, MIT 6.003 L6/L11-13.
- 2026-09-27 — Wrote fourier-series-and-transform.md + math_fourier.py (ALL PASS). Worked example: 24 MHz x18 = 432 MHz (Teensy crystal), 40 MHz x23 = 920 MHz (ESP32) clock harmonics near LoRa bands. Caught own slip (LoRa bin 1/Ts=977 Hz) before publishing.
- 2026-09-27 — Fourier research: MSU EMC module (trapezoid spectra, pdftotext), MIT 6.003 lecture list, Klauder 1960 chirp paper located, Osgood EE261 notes located. Writing tools/verify/math_fourier.py next.
- 2026-09-27 — Wrote complex-numbers-and-phasors.md + tools/verify/math_complex_phasors.py (ALL PASS; RLC ODE vs phasor 6e-11). Sources: Lyons tutorial, MIT 18.03 notes (TOC read), DSP SE Q431, 47 CFR 97.3, UIUC ECE330. Pozar section numbers cited from memory -> flagged 'verify' in page.
- 2026-09-27 — Wrote decibels-and-log-units.md (334 lines) + tools/verify/math_decibels.py (all PASS). Found AF constant 29.77 (exact c) vs 29.79 (c=3e8) rounding difference; logged.
- 2026-09-27 — dB research: read R&S 1MA98 in full (pdftotext of WebFetch-saved copy); NIST SP811 s8.7; searched dBic and forum dB confusions (Physics Forums 10 vs 20, AAC dB addition). Key: R&S uses 293 K for -174 dBm/Hz (=-173.93), KB convention is 290 K (-173.98) -> note on page.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| S1 | Winter, R&S 1MA98 "dB or not dB?" v12e 2015 (http://courses.ece.ubc.ca/elec391/1MA98_12e.pdf) | app note | dB page (secs 2-6) | good; typos: Table 6-1 lists -3 dB voltage "0.798" (should be 0.708); 5.8 example mislabels unit |
| S3 | Inside GNSS "Measuring GNSS signal strength" 2010 | trade column | C/N0 vs SNR | ok |
| S4 | A.H. Systems / TDK antenna factor notes | app note | AF=9.73/(lambda sqrt G) | re-derived; constant 29.77 (exact c) vs 29.79 quoted |
| S5 | Kester MT-001, MT-003 (ADI) | app note | 6.02N+1.76, dBFS/dBc | standard refs |
| S6 | Keysight "Spectrum Analyzers: Noise and Sensitivity" | app note | RBW scaling of noise | |
| S7 | Lyons "Quadrature Signals: Complex but not complicated" (2000/2008) | tutorial | phasors, negative freq, IQ | widely used |
| S8 | Miller, MIT 18.03 Supplementary Notes (2012) | lecture notes | complex exp (s5-6), ERF (s10), damping (s15), freq resp (s16), impulse/conv (s21-24), pole diagram (s27-28) | excellent; also for ODE/Laplace pages |
| S9 | DSP SE Q431 negative frequency thread | forum | misconceptions | anecdotal |
| S10 | 47 CFR 97.3 PEP definition; UIUC ECE330 L2 complex power | regulation; lecture notes | PEP; peak vs rms phasor S | |
| S11 | MSU EMRG "Module 3: Signals and Spectra" (EMC notes after C.R. Paul, Intro to EMC, p.365) | lecture notes | trapezoid spectrum bounds 1/(pi tau), 1/(pi tr) | good |
| S12 | MIT 6.003 Fall 2011 (Freeman) lecture list: L8 convolution, L9 freq resp, L11 Bode, L14-20 Fourier, L21-22 sampling, L23-24 modulation | lecture notes | Fourier/Laplace/Bode pages | |
| S13 | Klauder et al., "Theory and design of chirp radars", BSTJ 39(4):745-808, 1960 (archive.org/details/bstj39-4-745) | peer-reviewed | chirp spectrum, TB product, Fresnel ripple | classic |
| S14 | Osgood, EE261 lecture notes (Stanford) | lecture notes | Fourier transform general | |
| S15 | Cheever, Swarthmore LPSA "Asymptotic Bode diagram" | lecture notes | Bode rules, 3 dB/5.7 deg errors | its '2nd-order peak 1/(2 zeta)' is value at wn, not true max (noted) |
| S16 | Keysight E5080B help "Group delay" | manufacturer doc | group delay, aperture | |
| S17 | Bode 1945 Network Analysis & Feedback Amplifier Design | textbook (historical) | gain-phase integral | verified numerically, not read |
| S18 | Djordjevic, Biljic, Likar-Smiljanic, Sarkar, IEEE T-EMC 43(4):662-667, 2001 (read in full via pdftotext) | peer-reviewed | Kramers-Kronig, causal FR-4 log model eq.(5), eps' -0.14/decade, eps''~0.1 | key source; parameters sample-specific |
| S19 | Orfanidis EWA ch1 s1.17 Kramers-Kronig (via search snippet; site 403) | textbook | KK | section no. from search result |
| S20 | Dmitriev-Zdorov et al., SI Journal 2020, causal roughness models | trade journal | causality in SI models | author from PDF filename |
| S21 | Griffiths Intro to Electrodynamics 4e ch1 (s1.2-1.6) | textbook | vector calculus | section numbers from memory + search confirmation of 1.2-1.5 |
| S22 | OpenStax Calculus Vol 3 s6.5, 6.7, 6.8 | textbook (free) | div/curl, Stokes, divergence thm | |
| S23 | Ulaby & Ravaioli Fundamentals of Applied EM 7e ch3 | textbook | vector analysis | not re-read |
| S24 | Physics Forums "Intuition on divergence and curl" | forum | misconception (straight lines can have curl) | anecdotal |
| S25 | Oppenheim & Verghese, Signals Systems and Inference (MIT 6.011 notes ch9-10, 2018 L18 slides) | textbook/lecture | random processes, PSD, W-K | slides only for L18 |
| S26 | Rice 1944/45 BSTJ "Mathematical analysis of random noise" (archive.org bstj23-3-282, bstj24-1-46) | peer-reviewed | shot noise, narrowband noise, Rician | located, not read in full |
| S27 | Papoulis & Pillai 4e; Bertsekas & Tsitsiklis (MIT 6.041) | textbooks | distributions, CLT, Poisson | chapter numbers recalled |
| S28 | NIST DLMF ch7 (erf/erfc) | standard | Q-function | |
| S29 | jensign.com noise bandwidth note; EmbeddedRelated noise blog | tech note/blog | ENBW; RSS addition misconception | |
| S30 | ITU-R P.526-14 (2018) s2.7, s4.1 eqs 26-31 (read via pdftotext) | standard | Fresnel integrals, knife-edge J(nu) exact & approx | authoritative |
| S31 | Dolph 1946 Proc IRE 34:335-348 | peer-reviewed | Dolph-Chebyshev arrays | abstract only; maths re-derived + chebwin |
| S32 | NIST DLMF ch7, 10, 14, 18 | standard | special functions | |
| S33 | Ho, Ruehli, Brennan, IEEE TCAS 22(6):504-509, 1975 (MNA) | peer-reviewed | MNA | abstract/metadata |
| S34 | Tse & Viswanath, Fundamentals of Wireless Communication ch7 | textbook | MIMO capacity via SVD | |
| S35 | Strang Intro to Linear Algebra 5e; MIT 18.06 | textbook | LU, LS, eig, SVD | chapters recalled |
| S36 | Yee 1966 IEEE TAP 14(3):302-307 (FDTD); stability condition corrected by Taflove & Brodwin 1975 | peer-reviewed | FDTD | metadata via search |
| S37 | Liebig et al., openEMS EC-FDTD (docs.openems.de; paper on EC-FDTD platform) | software doc / paper | openEMS method | |
| S38 | Mukhopadhyay & Majumdar arXiv:0704.1563 (2007), Table 2 of unit-square-plate capacitance values; Read 1997 JCP 133:1-5 (0.3667874); Maxwell 1878 (0.3607) | preprint + cited refs | MoM benchmark | read via pdftotext |
| S2 | NIST SP 811 (2008) sec 8.7 logarithmic quantities (https://www.nist.gov/pml/special-publication-811/nist-guide-si-chapter-8) | standard | Neper/bel defs, 1 dB = 0.1151 Np, "dBm" deprecated by SI rules | authoritative |

## Contradictions / discrepancies found
- Unit square plate capacitance: Maxwell (1878) 0.3607 x 4 pi eps0 L (=40.14 pF for 1 m) is still quoted; accurate modern value (Goto 1992; Read 1997) is 0.36679 x 4 pi eps0 L = 40.81 pF. I initially recalled 0.3607 (wrong); MoM verify now uses Read's value (40x40 pulse MoM: 40.60 pF, -0.5%).
- Second-order resonant peak: Swarthmore Bode notes (and many web sources) give peak height 1/(2 zeta); that is |H(j wn)|. True maximum is 1/(2 zeta sqrt(1-zeta^2)) at wn sqrt(1-2 zeta^2) (verified numerically). Page states both.
- R&S 1MA98 Table 6-1 gives -3 dB voltage ratio "0.798"; correct is 10^(-3/20)=0.708 (typo in source). Section 5.8 example writes "-80 dB(V/m) = -80 dB(uV/m) + 120 dB" (unit label swapped). Pages use corrected values.
- Reference temperature for "-174 dBm/Hz": R&S uses 20 C (293.15 K -> -173.93 dBm/Hz); IEEE noise-figure standard T0=290 K -> -173.98 dBm/Hz. Both round to -174; KB uses 290 K.
- NIST SP811 s8.7 says SI rules preclude "dBm" (reference must be stated as L_P (re 1 mW)); industry/ITU use dBm universally. Page explains both.

## Knowledge gaps noticed (for later gap-filling)
- Section numbers for Pozar, Kreyszig, Papoulis, Balanis, Numerical Recipes, Jin, Taub&Schilling cited from memory of ToCs and flagged 'verify' on pages -> W4-D4 (textbook ToC check) should confirm.
- No page yet for: z-transform (expected 14-sdr-dsp), detection/estimation theory depth (11-radar), optimisation (matching/array synthesis), dyadic Green's functions, SDEs for phase noise.
- Measured Rician K-factors for rocket-to-ground links at 433/915 MHz (none found yet) — 09/15 domains or Marcus's own flight logs.
- dBFS full-scale convention (sine vs square) varies by ADC vendor — 14-sdr-dsp/05-analog should record per part.

## Cross-domain notes (things other domains should cover/link)
- 02-electromagnetics/dielectrics + 13-pcb/stackups: use D-S causal model; example table eps'(f) for Djordjevic FR-4 sample in linear-systems page; JLCPCB FR-4 values need their own characterisation.
- 16-simulation-tools: causality/passivity enforcement of S-parameters (vector fitting) and openEMS dispersive materials.
- 15-lora-ism-radios: confirm LoRa SNR demod limits (SF7 -7.5 ... SF12 -20 dB) from Semtech datasheet; dB page example 2 uses -20 dB @SF12 and NF 6 dB -> -137 dBm.
- 08-antennas: dB page uses dipole D=1.641 (2.15 dBi) and Ae=G lambda^2/4pi; AF constant 29.77 dB/m (exact c).
- 17-test-measurement: log-average bias 2.51 dB for noise; RBW noise-bandwidth corrections instrument-specific.

## Resume instructions (what the next agent should do if this one is interrupted)
- TASK COMPLETE (2026-09-27). All 12 pages + _index.md + _sources.md written; 11 verify scripts ALL PASS.
- If extending: follow CONVENTIONS s3; write/extend tools/verify/math_<topic>.py first; re-run `for f in tools/verify/math_*.py; do python3 $f | tail -1; done`; re-run a link check against INDEX.md (now auto-generated from tools/taxonomy.md; planned slugs live there).
- Items flagged 'verify' on pages are textbook section numbers recalled from memory (see Knowledge gaps).
