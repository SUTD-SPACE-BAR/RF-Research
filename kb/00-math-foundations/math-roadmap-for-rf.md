---
title: Maths roadmap for RF, antennas, radar and analog design
domain: 00-math-foundations
slug: math-roadmap-for-rf
tags: [roadmap, learning-path, prerequisites, study-plan, math-for-rf]
prerequisites: []
related:
  - decibels-and-log-units.md
  - complex-numbers-and-phasors.md
  - fourier-series-and-transform.md
  - laplace-transfer-functions-bode.md
  - linear-systems-convolution.md
  - vector-calculus-for-em.md
  - probability-random-processes-and-psd.md
  - differential-equations-circuits-waves.md
  - special-functions-bessel-sinc.md
  - matrices-and-linear-algebra-for-networks.md
  - numerical-methods-overview.md
level: mixed
confidence: high
last_updated: 2026-10-03
---

# Maths roadmap for RF, antennas, radar and analog design

*New to RF? Start with [RF concepts for beginners](rf-concepts-for-beginners.md); for books, courses, instruments and projects see the [RF learning roadmap](rf-learning-roadmap.md); for the KB's constants and sign/unit conventions see [canonical values and conventions](canonical-values-and-conventions.md).*

## Questions this page answers
- What maths do I actually need to design radios, antennas, radars, phased arrays and analog circuits?
- In what order should I learn it, starting from high-school algebra?
- Which maths does each RF topic depend on (link budgets, matching, filters, LNAs, antennas, arrays, FMCW radar, LoRa)?
- How can I check whether I'm ready for a given topic?
- What free courses and books cover each stage?
- What can I skip (for now)?

## TL;DR
- **Stage 0 (algebra, logs, trig)** already unlocks link budgets, dBm arithmetic, Friis, and most rules of thumb → [decibels](decibels-and-log-units.md).
- **Stage 1 (complex numbers & phasors)** is the single most important step: impedance, matching, S-parameters, Smith charts, filters, I/Q and SDR all live in the complex plane → [complex numbers and phasors](complex-numbers-and-phasors.md).
- **Stage 2 (calculus → ODEs → Fourier/Laplace → linear systems)** gives transients, resonance/Q, Bode plots, stability, spectra, modulation and filtering → [ODEs](differential-equations-circuits-waves.md), [Fourier](fourier-series-and-transform.md), [Laplace/Bode](laplace-transfer-functions-bode.md), [linear systems](linear-systems-convolution.md).
- **Stage 3 (linear algebra, probability)** gives network matrices, arrays/MIMO, calibration fitting, noise, BER, fading and detection → [matrices](matrices-and-linear-algebra-for-networks.md), [probability and PSD](probability-random-processes-and-psd.md).
- **Stage 4 (vector calculus, PDEs, special functions)** gives Maxwell's equations, waves, waveguides, radiation and antenna patterns → [vector calculus](vector-calculus-for-em.md), [special functions](special-functions-bessel-sinc.md).
- **Stage 5 (numerical methods)** lets you trust or build simulators (SPICE, NEC, openEMS, FEM) → [numerical methods](numerical-methods-overview.md).
- Every page in this folder has a runnable `tools/verify/math_*.py` script: running and modifying them is the fastest way to learn each topic.

## Intuition (no math)
RF engineering stacks a few mathematical ideas over and over:
1. **Ratios on a log scale** (dB) — because everything multiplies and spans huge ranges.
2. **Rotating arrows** (complex numbers/phasors) — because everything is a sine wave at some frequency with an amplitude and a phase.
3. **Frequency thinking** (Fourier/Laplace) — because filters, mixers, modulation and noise are easiest to understand as "what happens to each frequency".
4. **Linear systems and matrices** — because most of the hardware is linear, and many ports/antennas/nodes interact.
5. **Randomness** (probability, PSD) — because noise, fading and interference set the limits.
6. **Fields in space** (vector calculus, PDEs) — because antennas, lines and PCBs are governed by Maxwell's equations.
7. **Computation** — because real geometries need simulation, and simulations need checking.

You can build real hardware after stages 0–2; stages 3–5 are what let you derive, optimise and trust.

## The math

### Level 1 — the learning path, stage by stage

| Stage | Topics | You can then… | KB page(s) | Free course / text |
|---|---|---|---|---|
| 0 | algebra, exponents, $\log_{10}$, $\ln$, trig identities, unit conversions, SI prefixes | do link budgets, dBm↔W↔V, Friis, noise floors | [decibels](decibels-and-log-units.md) | any pre-calculus text; R&S 1MA98 [1] |
| 1 | complex arithmetic, polar/rect, Euler, phasors, RMS/peak/PEP | analyse RLC at a frequency, matching, S₁₁, Smith chart, I/Q | [complex/phasors](complex-numbers-and-phasors.md) | MIT 18.03 notes §5–6 [2]; Lyons quadrature tutorial [3] |
| 2a | single-variable calculus (derivative, integral, exponential/log, Taylor series) | understand RC/RL transients, energy, averages/RMS | [ODEs](differential-equations-circuits-waves.md) | MIT 18.01 [4] |
| 2b | linear ODEs, damping, resonance | ringing, Q, oscillator start-up, decoupling | [ODEs](differential-equations-circuits-waves.md) | MIT 18.03 [2] |
| 2c | Fourier series/transform, DFT | spectra, harmonics/EMI, modulation, FFT/SDR | [Fourier](fourier-series-and-transform.md) | MIT 6.003 [5]; Stanford EE261 [6] |
| 2d | Laplace, poles/zeros, Bode, feedback | filters, PLL loops, op-amp/LNA stability | [Laplace/Bode](laplace-transfer-functions-bode.md) | MIT 6.003 [5] |
| 2e | convolution, causality, Hilbert, group delay | filtering, matched filters, dispersion, material models | [linear systems](linear-systems-convolution.md) | Oppenheim & Willsky [7] |
| 3a | matrices, linear systems, eigenvalues, SVD, least squares | network matrices, nodal analysis, arrays/MIMO, calibration | [matrices](matrices-and-linear-algebra-for-networks.md) | MIT 18.06 [8] |
| 3b | probability, random processes, PSD | noise figure, sensitivity, BER, fading margin, radar detection | [probability/PSD](probability-random-processes-and-psd.md) | MIT 6.041 [9], 6.011 [10] |
| 4a | multivariable calculus, grad/div/curl, Gauss/Stokes, curvilinear coords | Maxwell's equations, boundary conditions, line/coax fields | [vector calculus](vector-calculus-for-em.md) | MIT 18.02 [4]; Griffiths ch. 1 [11] |
| 4b | PDEs, separation of variables, Helmholtz | waveguides, cavities, radiation, skin effect | [ODEs/PDEs](differential-equations-circuits-waves.md) | Kreyszig ch. 12 [12]; MIT 6.013 [13] |
| 4c | special functions | FM spectra, dish patterns, diffraction, Chebyshev filters/arrays | [special functions](special-functions-bessel-sinc.md) | NIST DLMF [14] |
| 5 | numerical methods | SPICE/NEC/openEMS/FEM literacy and checking | [numerical methods](numerical-methods-overview.md) | Numerical Recipes [15]; Taflove & Hagness [16] |
| grad | Green's functions, dyadics, estimation/detection theory, optimisation, stochastic calculus (phase noise), conformal mapping | research-level antenna/array/radar/oscillator work | (later KB additions) | Orfanidis EWA [17]; Van Trees [18] |

MIT 6.013's stated prerequisites — complex numbers, vector operators, simple matrix operations, basic calculus, RLC circuits and Fourier transforms [13] — match stages 1–4a: that is the minimum for an undergraduate EM course.

### Level 2 — which maths each RF topic needs

| RF topic (KB domain) | Essential maths | Helpful extras |
|---|---|---|
| Link budgets, Friis, path loss ([09](../09-propagation-link-budget/link-budget-methodology.md)) | dB, logs, powers of distance | probability (fade margins), special functions (knife-edge, Fresnel zones) |
| Thermal noise, NF, sensitivity ([07](../07-noise-linearity/noise-figure-and-friis.md)) | dB, algebra (Friis cascade), noise-power addition | PSD, ENBW, correlated noise (noise parameters) |
| Nonlinearity, IP3, intermod ([07](../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md)) | power series, trig product identities, dB slopes | Fourier (spectra of distorted signals), Bessel (FM/PM spurs) |
| Lumped circuits, resonance, Q ([01](../01-circuit-theory/resonance-and-q.md)) | phasors, 2nd-order ODEs | Laplace, energy methods |
| Filters ([01](../01-circuit-theory/passive-filter-design-prototypes.md), [06](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md)) | Laplace, poles/zeros, Bode, Chebyshev polynomials | group delay, coupled-resonator eigenvalues |
| Transmission lines, Smith chart, matching ([03](../03-transmission-lines-matching/smith-chart.md)) | phasors, complex division, hyperbolic functions, telegrapher ODE | bilinear (Möbius) maps, Bode–Fano integrals |
| S-parameters, two-ports, VNA ([03](../03-transmission-lines-matching/s-parameters.md), [17](../17-test-measurement/vna-fundamentals-calibration.md)) | matrices, complex algebra | signal-flow graphs, least squares (calibration) |
| Real components, parasitics ([04](../04-real-components-hf/capacitors-at-rf-mlcc.md)) | phasors, resonance | Kramers–Kronig (causal models), fitting |
| Amplifiers, LNA, PA, stability ([05](../05-analog-electronics/feedback-and-stability.md), [06](../06-rf-circuits/lna-design.md)) | phasors, Laplace/Bode, feedback, 2-port matrices | noise correlation matrices, optimisation |
| Oscillators, PLLs, phase noise ([06](../06-rf-circuits/vco-and-pll-synthesizers.md), [07](../07-noise-linearity/phase-noise-and-jitter.md)) | Laplace/feedback, PSD | nonlinear ODEs, stochastic processes |
| Mixers, receivers, SDR ([06](../06-rf-circuits/receiver-architectures.md), [14](../14-sdr-dsp/iq-complex-baseband.md)) | Fourier (modulation theorem), complex baseband, sampling | Hilbert transform, multirate DSP, z-transform |
| Modulation, BER, coding ([10](../10-comms-modulation/ber-ebn0-and-shannon.md)) | probability, Q-function, Fourier | linear algebra (codes, equalisers), information theory |
| LoRa / chirp spread spectrum ([15](../15-lora-ism-radios/lora-phy-css-math.md)) | Fourier (chirps, DFT), dB, probability | time–bandwidth product, detection theory |
| Antennas ([08](../08-antennas/antenna-fundamentals.md)) | vector calculus, spherical coords, phasors, dB | special functions (apertures), numerical EM (MoM/FDTD) |
| Phased arrays ([12](../12-phased-arrays/array-factor-linear-arrays.md)) | complex exponentials, Fourier (array factor = DTFT), matrices | SVD/eigen (adaptive beamforming), Chebyshev (tapers), optimisation |
| Radar ([11](../11-radar/radar-range-equation.md)) | dB, Fourier (pulses, chirps, Doppler), probability (detection, CFAR) | matched filtering, ambiguity functions, SAR (2-D Fourier) |
| Propagation, fading ([09](../09-propagation-link-budget/multipath-fading-doppler.md)) | phasor addition, probability (Rayleigh/Rician) | special functions (diffraction), stochastic channel models |
| PCB layout, EMC ([13](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md)) | Fourier (trapezoid spectra), transmission-line maths | causal material models, numerical EM |
| Simulation ([16](../16-simulation-tools/em-solvers-fdtd-mom-fem.md)) | numerical methods, linear algebra | PDE theory, convergence analysis |

### Level 3 — self-check questions (can you answer these? if not, read the linked page)

- **Stage 0**: What is 27 dBm in watts? What is −100 dBm + 30 dB? Why is 30 dBm + 30 dBm not 60 dBm? → [decibels](decibels-and-log-units.md)
- **Stage 1**: What is $1/(3+4j)$ in polar form? What is the impedance of 10 nH at 433 MHz? Why is there a ½ in $\tfrac12\mathrm{Re}\{VI^*\}$? → [phasors](complex-numbers-and-phasors.md)
- **Stage 2**: What are the harmonics of a 50 % square wave? What bandwidth does a 1 µs pulse occupy? Where are the poles of a series RLC and what is its Q? What is group delay? → [Fourier](fourier-series-and-transform.md), [Laplace](laplace-transfer-functions-bode.md), [ODEs](differential-equations-circuits-waves.md), [linear systems](linear-systems-convolution.md)
- **Stage 3**: Convert a Z-matrix to an S-matrix. Why is a lossless S-matrix unitary? What fade margin gives 99 % availability in Rayleigh fading? What is the ENBW of an RC filter? → [matrices](matrices-and-linear-algebra-for-networks.md), [probability](probability-random-processes-and-psd.md)
- **Stage 4**: Derive the coax capacitance from Gauss's law. Where do the near-field terms of a dipole equal the far-field term? What is the cutoff of WR-90? What is the first-null angle of a 1 m dish at 5.8 GHz? → [vector calculus](vector-calculus-for-em.md), [ODEs/PDEs](differential-equations-circuits-waves.md), [special functions](special-functions-bessel-sinc.md)
- **Stage 5**: Why does an FDTD code blow up at Courant number > 1? How many segments for a 433 MHz dipole in NEC? → [numerical methods](numerical-methods-overview.md)

All of these are answered with numbers (and checked by scripts) on the linked pages.

## Design equations & rules of thumb

| Rule | Why |
|---|---|
| Learn complex numbers before anything else beyond dB | 80 % of RF circuit work is complex algebra at one frequency |
| Always write units and the reference (dBm vs dB, peak vs rms, Hz vs rad/s) | most "maths errors" in RF are convention errors |
| Think "one frequency at a time" (phasors), then "all frequencies" (Fourier), then "time domain" (Laplace/convolution) | increasing generality, same ideas |
| Use numerical checks (the verify scripts) to confirm every derivation | the KB's own quality rule; builds intuition |
| Defer graduate topics until a project needs them | they're easier with a concrete problem |

## Worked examples — tracing a project to its maths

**1. A LoRa rocket-telemetry link (433 MHz, 2 W).** Needs: dB arithmetic (EIRP, path loss, sensitivity) → [decibels](decibels-and-log-units.md); thermal noise and ENBW → [probability/PSD](probability-random-processes-and-psd.md); fade margin (Rician/Rayleigh) → same page; antenna gain and polarisation (dBi/dBic) → [decibels](decibels-and-log-units.md); knife-edge loss after landing → [special functions](special-functions-bessel-sinc.md); LoRa processing gain ($TB=2^{SF}$) → [Fourier](fourier-series-and-transform.md). Stage 0–3 maths is enough; domains: [09](../09-propagation-link-budget/link-budget-methodology.md), [15](../15-lora-ism-radios/rocket-telemetry-radio-design.md).

**2. Matching a chip antenna to 50 Ω.** Needs: complex impedance and reflection coefficient → [phasors](complex-numbers-and-phasors.md); L-networks and bandwidth via nodal analysis → [matrices](matrices-and-linear-algebra-for-networks.md); Smith chart (a complex-plane map) → [Smith chart](../03-transmission-lines-matching/smith-chart.md). Stage 1 + a little 3a.

**3. An FMCW radar at 24 GHz.** Needs: chirps and beat frequencies (Fourier, modulation theorem) → [Fourier](fourier-series-and-transform.md); FFT windows and resolution → [14](../14-sdr-dsp/fft-spectral-analysis-windows.md); detection thresholds (Q-function, CFAR) → [probability](probability-random-processes-and-psd.md); radar equation in dB → [decibels](decibels-and-log-units.md); antenna beamwidth (aperture Fourier/jinc) → [special functions](special-functions-bessel-sinc.md). Stages 0–3 plus 4c; domain [11](../11-radar/fmcw-radar.md).

**4. A steerable 8-element 2.4 GHz array.** Needs: complex exponentials and the array factor as a DTFT → [Fourier](fourier-series-and-transform.md); tapers (Dolph–Chebyshev) → [special functions](special-functions-bessel-sinc.md); MVDR/MUSIC (covariance, eigenvectors) → [matrices](matrices-and-linear-algebra-for-networks.md); calibration (least squares) → same; mutual coupling (network matrices, EM simulation) → [numerical methods](numerical-methods-overview.md). Stages 1–5; domain [12](../12-phased-arrays/array-factor-linear-arrays.md).

**5. A 433 MHz LNA.** Needs: phasors and two-port S-parameters → [phasors](complex-numbers-and-phasors.md), [matrices](matrices-and-linear-algebra-for-networks.md); stability (poles, Bode, K-factor) → [Laplace/Bode](laplace-transfer-functions-bode.md); noise figure and noise-power addition → [probability](probability-random-processes-and-psd.md); bias transients and decoupling resonances → [ODEs](differential-equations-circuits-waves.md). Stages 1–3; domain [06](../06-rf-circuits/lna-design.md).

**6. Simulating a patch antenna in openEMS.** Needs: Maxwell in differential form and boundary conditions → [vector calculus](vector-calculus-for-em.md); cavity-model resonance via separation of variables → [ODEs/PDEs](differential-equations-circuits-waves.md); FDTD stability, cells per wavelength, convergence → [numerical methods](numerical-methods-overview.md); causal FR-4 model → [linear systems](linear-systems-convolution.md). Stages 4–5; domains [08](../08-antennas/patch-antennas.md), [16](../16-simulation-tools/openems-workflow.md).

## Practical notes
- **Learning by running**: each `tools/verify/math_*.py` script is a set of small numerical experiments; change a parameter (a frequency, a Q, a K-factor) and predict the result before running it.
- **Time budget** (self-study, rough): stage 0–1: 1–2 weeks; stage 2: 1–2 months; stage 3: 1–2 months; stage 4: 2–3 months; stage 5: ongoing with projects. You can (and should) build hardware in parallel — Marcus already has stage 0–1 experience from flight-computer and LoRa work.
- **Tools**: Python (numpy/scipy/sympy/matplotlib/scikit-rf) replaces most of the hand calculation; sympy checks algebra; a scientific calculator with complex mode is handy on the bench.

## Common mistakes & misconceptions
1. **Skipping complex numbers** and trying to learn Smith charts, S-parameters or I/Q by rote — they make sense only as complex-plane geometry.
2. **Memorising dB rules without $P\propto V^2$** — leads to 10 vs 20 log errors forever.
3. **Believing you must master Maxwell's equations before building anything** — circuit-level RF (matching, filters, link budgets) needs only stages 0–3.
4. **Mixing conventions from different books** ($e^{j\omega t}$ vs $e^{-i\omega t}$, peak vs rms phasors, $f$ vs $\omega$ Fourier) — pick the KB's conventions (CONVENTIONS §4.5) and translate everything else.
5. **Learning maths without numbers** — always attach a realistic RF example (433 MHz, 50 Ω, −174 dBm/Hz) to each formula.
6. **Treating simulation output as truth** without the numerical-methods checks.

## How to simulate / verify
Run all maths-domain checks:
```bash
for f in tools/verify/math_*.py; do echo "== $f"; python3 "$f" | tail -1; done
```
Each should print `ALL PASS` (`math_linear_systems.py` takes ~20 s).

## Open questions / gaps
- Graduate-level topics (dyadic Green's functions, detection/estimation theory, optimisation for matching/array synthesis, stochastic differential equations for oscillator phase noise, the z-transform in depth) have no dedicated pages yet; add them when a project needs them. The z-transform is expected in [14-sdr-dsp](../14-sdr-dsp/digital-filters-fir-iir.md).
- Time estimates above are the author's judgement, not sourced.

## Sources
1. A. Winter, *dB or not dB?*, Rohde & Schwarz 1MA98 (v12e 2015 / v14e 2024). http://courses.ece.ubc.ca/elec391/1MA98_12e.pdf (app note).
2. H. R. Miller, *18.03 Supplementary Notes*, MIT (2012). https://math.mit.edu/classes/18.03/sup/sup0.pdf ; MIT OCW 18.03 https://ocw.mit.edu/courses/18-03-differential-equations-spring-2010/ (lecture notes).
3. R. Lyons, *Quadrature Signals: Complex, But Not Complicated* (2000/2008). https://dspguru.com/dsp/tutorials/quadrature-signals/ (tutorial).
4. MIT OCW 18.01 Single Variable Calculus and 18.02 Multivariable Calculus. https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/ ; https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/ (lecture notes).
5. D. Freeman, MIT 6.003 Signals and Systems (Fall 2011). https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/ (lecture notes).
6. B. Osgood, Stanford EE261 *The Fourier Transform and its Applications*. https://see.stanford.edu/Course/EE261 (lecture notes/video).
7. A. V. Oppenheim, A. S. Willsky, S. H. Nawab, *Signals and Systems*, 2nd ed., Prentice Hall (1997) (textbook).
8. G. Strang, MIT 18.06 Linear Algebra. https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/ ; *Introduction to Linear Algebra*, 5th ed. (2016) (lecture notes/textbook).
9. J. Tsitsiklis et al., MIT 6.041 Probabilistic Systems Analysis; D. Bertsekas, J. Tsitsiklis, *Introduction to Probability*, 2nd ed. (2008). https://ocw.mit.edu/courses/6-041-probabilistic-systems-analysis-and-applied-probability-fall-2010/ (lecture notes/textbook).
10. A. V. Oppenheim, G. C. Verghese, MIT 6.011 Signals, Systems and Inference. https://ocw.mit.edu/courses/6-011-signals-systems-and-inference-spring-2018/ (lecture notes).
11. D. J. Griffiths, *Introduction to Electrodynamics*, 4th ed. (2013), ch. 1 (textbook).
12. E. Kreyszig, *Advanced Engineering Mathematics*, 10th ed., Wiley (2011) (textbook).
13. MIT OCW 6.013 Electromagnetics and Applications (Spring 2009), syllabus prerequisites. https://ocw.mit.edu/courses/6-013-electromagnetics-and-applications-spring-2009/ (lecture notes).
14. NIST Digital Library of Mathematical Functions. https://dlmf.nist.gov (standard reference).
15. W. H. Press et al., *Numerical Recipes*, 3rd ed., Cambridge (2007) (textbook).
16. A. Taflove, S. C. Hagness, *Computational Electrodynamics: The FDTD Method*, 3rd ed., Artech House (2005) (textbook).
17. S. J. Orfanidis, *Electromagnetic Waves and Antennas*, Rutgers (free online). https://www.ece.rutgers.edu/~orfanidi/ewa (textbook).
18. H. L. Van Trees, *Detection, Estimation, and Modulation Theory, Part I* (1968/2013) and *Optimum Array Processing* (2002), Wiley (textbooks).
