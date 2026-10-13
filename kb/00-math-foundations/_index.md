# 00-math-foundations — Maths foundations for RF, antennas, radar and analog design

The mathematical toolkit that every other domain in this knowledge base leans on: logarithmic units, complex numbers and phasors, Fourier and Laplace methods, linear systems and causality, vector calculus, probability and noise spectra, differential equations and waves, special functions, linear algebra, and numerical methods. Each page is layered (algebra → calculus/complex → general theory), tied to RF examples at 433/915 MHz, 2.4/5.8 GHz and radar bands, and backed by a runnable verification script in `tools/verify/math_*.py` (every script prints `ALL PASS`). Start with the roadmap if you are unsure where to begin.

## Reading order (beginner → advanced)
0a. [RF concepts for beginners](rf-concepts-for-beginners.md) — the genuine Level-1 tour (high-school maths): what RF is, λ = c/f, dB, impedance and 50 Ω, antennas, bandwidth, noise, sharing the air, penetration, why RF is non-ionising. Start here if you are new.
0b. [RF learning roadmap](rf-learning-roadmap.md) — the practice companion to the maths roadmap: stages zero → graduate, books by audience, free courses, videos, first instruments, what to build, and the KB reading order.
1. [Maths roadmap for RF](math-roadmap-for-rf.md) — what to learn, in what order, for which RF topic (read first).
2. [Decibels and logarithmic units](decibels-and-log-units.md) — stage 0; needed everywhere.
3. [Complex numbers and phasors](complex-numbers-and-phasors.md) — stage 1; the key step for circuits, matching, S-parameters, I/Q.
4. [Differential equations for circuits and waves](differential-equations-circuits-waves.md) — transients, resonance/Q, wave equation, modes.
5. [Fourier series and the Fourier transform](fourier-series-and-transform.md) — spectra, EMI harmonics, pulses, chirps, DFT.
6. [Laplace transform, transfer functions and Bode plots](laplace-transfer-functions-bode.md) — poles/zeros, Bode, stability, group delay.
7. [Linear systems, convolution, causality and Kramers–Kronig](linear-systems-convolution.md) — impulse response, Hilbert, causal dielectric models, dispersion.
8. [Matrices and linear algebra for networks](matrices-and-linear-algebra-for-networks.md) — nodal/MNA, Z/Y/ABCD/S, eigenvalues, SVD/MIMO, beamforming, least squares.
9. [Probability, random processes and PSD](probability-random-processes-and-psd.md) — noise, ENBW, Q-function/BER, Rayleigh/Rician fading, detection.
10. [Vector calculus for electromagnetics](vector-calculus-for-em.md) — grad/div/curl, Gauss/Stokes, spherical coordinates, phasor fields, Hertzian dipole.
11. [Special functions](special-functions-bessel-sinc.md) — sinc, Bessel/FM, jinc/apertures, Fresnel/knife-edge, erf/Q, Chebyshev (filters/arrays), Legendre.
12. [Numerical methods overview](numerical-methods-overview.md) — root finding, quadrature, FFT, ODE solvers, FD, FDTD, MoM, FEM, convergence.
13. [The z-transform and discrete-time systems](z-transform-and-discrete-time-systems.md) — difference equations, ROC, z-plane stability, s↔z (bilinear, impulse invariance), EMA, digital PLL, ΣΔ, CIC.
14. [Estimation theory — LS, ML, MAP/MMSE, CRB](estimation-theory-ml-map-crb.md) — estimator properties, Fisher information, frequency/phase/delay bounds for radar, GNSS and LoRa.
15. [Kalman filtering and state estimation](kalman-filter-and-state-estimation.md) — KF derivation, Q/R tuning, α-β trackers, complementary filters, EKF/UKF, NEES/NIS, baro+IMU rocket fusion, GNSS/INS coupling.
R. [Canonical values and conventions](canonical-values-and-conventions.md) — reference, not a reading step: KB constants, canonical design values with sources, sign/unit conventions, factor-of-2 traps, Singapore limits and the LoRa channel-edge rule. Check it before quoting a number.

## Pages
| Page | What it covers | Level | Confidence | Verify script |
|---|---|---|---|---|
| [rf-concepts-for-beginners](rf-concepts-for-beginners.md) | Level-1 tour of ten ideas with high-school maths and "go deeper" links: spectrum, λ = c/f table, dB/dBm, reactance/impedance/Γ and why 50 Ω, antennas as converters (gain = focusing), modulation and bandwidth, kTB and SNR, superposition and selectivity, wall loss vs frequency, photon energy and non-ionising RF | intro | high | `e6_beginner_numbers.py` |
| [rf-learning-roadmap](rf-learning-roadmap.md) | five practice stages (what to learn/read/watch/buy/build), books by audience with read-first chapters, Pozar chapter → KB map, specialist tracks, free courses and texts, video channels, first instruments, persona plans, KB reading order over all 22 domains | intro | medium | — |
| [math-roadmap-for-rf](math-roadmap-for-rf.md) | learning path; maths needed per RF topic; self-check questions; project→maths traces | mixed | high | (runs all `math_*.py`) |
| [decibels-and-log-units](decibels-and-log-units.md) | 10 vs 20 log; dBm/dBW/dBµV/dBi/dBd/dBic/dBc/dBc/Hz/dBFS/dB-Hz/dBsm/dBK; Neper; dBm↔V at 50 Ω; coherent vs incoherent sums; field strength ↔ power; tables; mental maths | mixed | high | `math_decibels.py` |
| [complex-numbers-and-phasors](complex-numbers-and-phasors.md) | Euler; polar/rect; phasors and $d/dt\to j\omega$; impedance; RMS/peak/PEP; complex power (peak vs rms phasors); complex envelope; analytic signal; negative frequency; conventions | mixed | high | `math_complex_phasors.py` |
| [fourier-series-and-transform](fourier-series-and-transform.md) | series/transform; square & trapezoid clock spectra (EMI near 433/920 MHz); sinc; theorems; time–bandwidth; pulsed RF; LFM chirp & LoRa TB = 2^SF; DFT; aperture↔pattern | mixed | high | `math_fourier.py` |
| [laplace-transfer-functions-bode](laplace-transfer-functions-bode.md) | Laplace pairs; poles/zeros; 2nd-order ζ/ωₙ/Q, peaking/overshoot; Bode rules and errors; phase/gain margin; minimum phase; Bode gain–phase integral; group delay; $t_rf_{3dB}=0.35$ | mixed | high | `math_laplace_bode.py` |
| [linear-systems-convolution](linear-systems-convolution.md) | LTI; convolution; BIBO; causality; Hilbert transform; Paley–Wiener; Kramers–Kronig; Debye & Djordjevic–Sarkar FR-4 models; phase vs group delay; waveguide dispersion | mixed | high | `math_linear_systems.py` (~20 s) |
| [vector-calculus-for-em](vector-calculus-for-em.md) | grad/div/curl/Laplacian meaning; integral theorems; Maxwell integral↔differential; cylindrical/spherical operators; phasor fields; Helmholtz; Green's function; Hertzian dipole; boundary conditions | mixed | high | `math_vector_calculus.py` |
| [probability-random-processes-and-psd](probability-random-processes-and-psd.md) | Gaussian/Rayleigh/Rician/exponential/χ²/Poisson; Q/erfc; WSS, autocorrelation, Wiener–Khinchin; one- vs two-sided PSD; ENBW; noise addition; shot/Johnson noise; fade-margin table; CFAR threshold; averaging | mixed | high | `math_probability_psd.py` |
| [differential-equations-circuits-waves](differential-equations-circuits-waves.md) | RC/RL; ½CV² charging loss; series/parallel RLC; ζ, Q, ringing; decoupling resonance; telegrapher → wave equation; d'Alembert; separation of variables (waveguide cutoffs); skin depth as diffusion | mixed | high | `math_differential_equations.py` |
| [special-functions-bessel-sinc](special-functions-bessel-sinc.md) | sinc; Bessel $J_n$ & FM (Carson, Bessel null); jinc/dish beams; Fresnel integrals & ITU-R P.526 knife-edge; erf/Q; Chebyshev filters & Dolph–Chebyshev arrays; Legendre; spherical Bessel; $I_0$ | mixed | high | `math_special_functions.py` |
| [matrices-and-linear-algebra-for-networks](matrices-and-linear-algebra-for-networks.md) | nodal & MNA; network matrices and Z↔S; reciprocity/losslessness/passivity; ABCD cascades; eigenvalues (coupled resonators); SVD & MIMO capacity; MVDR/MUSIC; least squares & OSL VNA cal; conditioning | mixed | high | `math_matrices.py` |
| [numerical-methods-overview](numerical-methods-overview.md) | bisection/Newton/Brent; quadrature; FFT; ODE stability & stiffness; finite differences; FDTD (Yee, Courant, dispersion); MoM; FEM; method choice; convergence/validation | mixed | high | `math_numerical_methods.py` |
| [z-transform-and-discrete-time-systems](z-transform-and-discrete-time-systems.md) | definition, ROC (causal vs anti-causal), pairs/properties, partial-fraction inverse, unilateral with ICs, stability (unit circle, Jury triangle), unit-circle response, z = e^{sT}, impulse invariance vs bilinear (warping, prewarp), matched-z, Euler mappings, EMA lag/noise, digital PLL, ΣΔ NTF/in-band noise, CIC | mixed | high | `est_ztransform.py` |
| [estimation-theory-ml-map-crb](estimation-theory-ml-map-crb.md) | bias/variance/MSE, LS/WLS/BLUE, ML, MAP/MMSE (Gaussian = Kalman update), LMMSE/orthogonality, RLS, Fisher information and CRB derivation, nuisance parameters, tone frequency/phase/amplitude CRB, delay CRB and rms bandwidth, carrier-phase ranging, threshold effect, GNSS/LoRa/radar numbers, DOP | mixed | high | `est_crb.py` |
| [kalman-filter-and-state-estimation](kalman-filter-and-state-estimation.md) | KF derived two ways, Joseph form, innovations, Riccati/DARE, DWNA/CWNA/Van Loan, Q/R tuning table, α-β/α-β-γ = steady-state KF (Kalata, conventions, stability), complementary filter equivalence, EKF, UKF, NEES/NIS tests, 1-D rocket baro+accel+bias fusion (apogee), GNSS/INS loose/tight/deep | mixed | high | `est_kalman.py` |
| [canonical-values-and-conventions](canonical-values-and-conventions.md) | single reference for constants (kT0, η0, IACS Cu), design values (via 0.54 nH, JLC 50 Ω widths, coax loss, BGA524, RTL-SDR NF), standard forms (FSPL, Leeson FkT0/2Ps, detection E/N0), conventions (e^{jωt}, IEEE RHCP, dBi, ERP = EIRP − 2.15, 10 vs 20 log, peak phasors, real vs complex processing gain), Singapore limits, E22 CH 24 band-edge rule, canonical scenario sets; seeded from the D6 audit | mixed | high | `fix_canonical_values.py` |

Run all checks: `for f in tools/verify/math_*.py tools/verify/est_ztransform.py tools/verify/est_crb.py tools/verify/est_kalman.py; do echo "== $f"; python3 "$f" | tail -1; done`

## Domain FAQ (top questions → page#section)
- *I'm new to RF — where do I start?* → [RF concepts for beginners](rf-concepts-for-beginners.md), then the [RF learning roadmap](rf-learning-roadmap.md)
- *Which value/convention does the KB use (kT, 2E/N0 vs E/N0, fs/B vs fs/2B, ERP vs EIRP, RHCP sign)?* → [canonical values and conventions](canonical-values-and-conventions.md)
- *Which RF book should I read first, and how do I get through Pozar?* → [learning roadmap § Level 2](rf-learning-roadmap.md#level-2--which-book-for-whom)
- *Is RF radiation ionising like X-rays?* → [concepts § 10](rf-concepts-for-beginners.md#10-why-rf-is-non-ionising) (433 MHz photon = 1.8 µeV vs ≈ 12.4 eV)
- *Do higher frequencies penetrate walls better?* → [concepts § 9](rf-concepts-for-beginners.md#9-why-higher-frequency-does-not-penetrate-better)
- *Why 10 log for power but 20 log for voltage?* → [decibels § Level 2](decibels-and-log-units.md#level-2--why-20-log-impedance-changes-adding-signals-statistics)
- *Is 30 dBm + 30 dBm = 60 dBm?* → [decibels § Common mistakes](decibels-and-log-units.md#common-mistakes--misconceptions)
- *How many volts is 33 dBm into 50 Ω?* → [decibels § dBm table](decibels-and-log-units.md#design-equations--rules-of-thumb) (9.99 V rms, 28.3 V p-p)
- *Why is thermal noise −174 dBm/Hz?* → [decibels § Level 3](decibels-and-log-units.md#level-3--the-whole-zoo-of-log-units-and-where-the-rules-bend), [probability § Level 3](probability-random-processes-and-psd.md#level-3--detection-averaging-shot-noise-and-multipath-statistics)
- *What is a phasor and why does d/dt become jω?* → [phasors § Level 2](complex-numbers-and-phasors.md#level-2--euler-phasors-impedance-power)
- *Why is there a ½ in P = ½Re{VI\*}?* → [phasors § Level 2](complex-numbers-and-phasors.md#level-2--euler-phasors-impedance-power)
- *What is negative frequency?* → [phasors § Level 3](complex-numbers-and-phasors.md#level-3--envelopes-analytic-signals-negative-frequency-conventions)
- *Can my 24/40 MHz clock interfere with 433/915 MHz LoRa?* → [Fourier § Worked example 2](fourier-series-and-transform.md#worked-examples)
- *Why is a chirp's bandwidth B regardless of its length?* → [Fourier § Level 3](fourier-series-and-transform.md#level-3--uncertainty-pulsed-rf-chirps-dft-and-space-domain-fourier)
- *How do I sketch a Bode plot / what is phase margin?* → [Laplace § Level 2](laplace-transfer-functions-bode.md#level-2--the-laplace-transform-poleszeros-second-order-systems-bode-sketching)
- *Why must a lossy PCB dielectric have frequency-dependent εr?* → [linear systems § Level 3](linear-systems-convolution.md#level-3--hilbert-transform-causality-relations-kramerskronig-dispersion)
- *How much does FR-4 εr change from 100 MHz to 2.4 GHz?* → [linear systems § Worked example 3](linear-systems-convolution.md#worked-examples)
- *Why do noise powers add but voltages don't?* → [probability § Intuition](probability-random-processes-and-psd.md#intuition-no-math)
- *How much fade margin for 99 % availability?* → [probability § fading table](probability-random-processes-and-psd.md#level-3--detection-averaging-shot-noise-and-multipath-statistics)
- *What is ENBW?* → [probability § Level 2](probability-random-processes-and-psd.md#level-2--distributions-random-processes-psd-enbw)
- *Why do my supply rails ring after a load step?* → [ODEs § Worked example 2](differential-equations-circuits-waves.md#worked-examples)
- *What does curl mean physically?* → [vector calculus § Intuition](vector-calculus-for-em.md#intuition-no-math)
- *Where does the near field end at 433 MHz?* → [vector calculus § Worked example 5](vector-calculus-for-em.md#worked-examples) (λ/2π = 11 cm)
- *How do I calibrate FM deviation (Bessel null)?* → [special functions § Level 2](special-functions-bessel-sinc.md#level-2--definitions-identities-and-derivations)
- *How much loss does a hill cause (knife-edge)?* → [special functions § Worked example 4](special-functions-bessel-sinc.md#worked-examples)
- *Why is a lossless S-matrix unitary?* → [matrices § Level 2](matrices-and-linear-algebra-for-networks.md#level-2--mna-network-matrices-eigenvalues)
- *Why doesn't MIMO help my long-range LOS link?* → [matrices § Level 3](matrices-and-linear-algebra-for-networks.md#level-3--svd-arrays-least-squares-conditioning)
- *Why does my FDTD simulation blow up?* → [numerical methods § Level 3](numerical-methods-overview.md#level-3--full-wave-em-solvers)
- *FDTD, MoM or FEM — which should I use?* → [numerical methods § Choosing a method](numerical-methods-overview.md#level-3--full-wave-em-solvers)
- *How do I turn my firmware's filter recursion into a transfer function, and is it stable?* → [z-transform § Level 1–2](z-transform-and-discrete-time-systems.md#the-math)
- *Bilinear transform or impulse invariance? Why prewarp?* → [z-transform § Level 3 and Worked example 2](z-transform-and-discrete-time-systems.md#worked-examples)
- *How much lag does my EMA add to the barometer?* → [z-transform § Worked example 1](z-transform-and-discrete-time-systems.md#worked-examples) (α = 0.1 at 100 Hz → 90 ms)
- *What is the best possible ranging / frequency accuracy (Cramér–Rao bound)?* → [estimation § Level 3](estimation-theory-ml-map-crb.md#the-math)
- *Why does carrier-phase GNSS reach millimetres?* → [estimation § carrier-phase ranging](estimation-theory-ml-map-crb.md#the-math)
- *How do I fuse barometer and accelerometer to get velocity and apogee?* → [Kalman § Worked example 1](kalman-filter-and-state-estimation.md#worked-examples)
- *How do I tune Q and R, and check my filter (NEES/NIS)?* → [Kalman § Level 2–3](kalman-filter-and-state-estimation.md#the-math)
- *Is an α-β filter / complementary filter a Kalman filter?* → [Kalman § Level 3](kalman-filter-and-state-estimation.md#the-math)

(Anchors follow GitHub-style heading slugs; if a renderer differs, search the page for the section title.)

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
- Oppenheim & Willsky, *Signals and Systems*; MIT 6.003 / 6.011 notes — Fourier, Laplace, LTI, random processes.
- H. R. Miller, *MIT 18.03 Supplementary Notes* — complex exponentials, ODEs, frequency response, pole diagrams.
- Bracewell, *The Fourier Transform and Its Applications*; Osgood, Stanford EE261 notes.
- Papoulis & Pillai, *Probability, Random Variables and Stochastic Processes*; Rice (1944–45) BSTJ.
- Griffiths, *Introduction to Electrodynamics* ch. 1; Pozar, *Microwave Engineering*; Orfanidis, *Electromagnetic Waves and Antennas* (free).
- NIST DLMF (special functions); NIST SP 811 §8.7 (log units); ITU-R P.526 (diffraction).
- R&S 1MA98 (decibels); Kester MT-001/MT-003 (ADC dB metrics).
- Djordjevic et al. (2001) IEEE T-EMC (causal FR-4 model); Klauder et al. (1960) BSTJ (chirps); Dolph (1946) Proc. IRE (Chebyshev arrays).
- Strang, *Introduction to Linear Algebra*; Tse & Viswanath (MIMO); Ho–Ruehli–Brennan (1975) MNA.
- Press et al., *Numerical Recipes*; Taflove & Hagness (FDTD); Yee (1966); Harrington (MoM); Jin (FEM).

## Known gaps
- z-transform, estimation theory (LS/ML/MAP/CRB) and Kalman filtering now have pages (W5-E5, 2026-10-03). Still missing: optimisation methods (matching/array synthesis), dyadic Green's functions, stochastic differential equations for oscillator phase noise, IMM/attitude (quaternion) estimation, RTS smoothers, ZOH/modified z-transform derivations.
- Textbook section numbers once cited from memory (Pozar, Kreyszig, Papoulis, Balanis, Numerical Recipes, Jin, Orfanidis) were checked against tables of contents by W5-S18 on 2026-10-13. Two were corrected: Pozar §4.1 → §4.2 for the Z/Y matrices, and Jin ch. 9 is absorbing boundary conditions, not edge elements. Still unverified: Taub & Schilling ch. 4 and Haykin §2.7 (special functions), and the Pozar table number (Table 4.2).
- The FR-4 Djordjevic–Sarkar parameters are for one measured board; JLCPCB laminate characterisation belongs to 13-pcb-rf-layout-emc.
- Measured Rician K-factors for rocket-to-ground links are not yet in the KB (see 09/15).
