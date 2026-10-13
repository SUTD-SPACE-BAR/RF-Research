---
title: Simulation verification and validation for RF — independent truth, pre-registration, convergence studies (Richardson, GCI), analytic benchmarks, cross-solver comparison, correlation to measurement, port de-embedding, faithful reporting
domain: 16-simulation-tools
slug: simulation-validation
tags: [verification, scorecard, model-form-uncertainty, s11-diagnosis, broken-model, validation, v-and-v, pre-registration, convergence, mesh-study, richardson-extrapolation, gci, benchmark, cross-validation, de-embedding, reference-plane, uncertainty, faithful-reporting, average-gain-test, measurement-correlation]
prerequisites: [tool-landscape-overview.md]
related: [openems-workflow.md, nec-antenna-modelling.md, spice-circuit-simulation.md, em-solvers-fdtd-mom-fem.md, python-rf-toolkit.md, ../17-test-measurement/fixtures-and-deembedding.md, ../17-test-measurement/vna-fundamentals-calibration.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Simulation verification and validation for RF

## Questions this page answers
- How do I know my simulation is right, not just converged?
- What is the difference between verification and validation?
- How do I do a mesh-convergence study and put an uncertainty on the result (Richardson extrapolation, GCI)?
- Which analytic benchmarks should every RF solver reproduce before I trust it?
- Two solvers disagree — how do I find out which one (or which set-up) is wrong?
- How do I compare a simulation with a NanoVNA measurement fairly (reference planes, de-embedding)?
- What does "pre-register the expected result" mean for an antenna simulation, and why bother?
- How often do honest pre-registered predictions actually miss, and what do the misses teach?
- My simulated S11 shows spikes, a flat floor or 0 dB — how do I find the set-up error?
- When is the model itself the uncertainty, so that no mesh study helps?

## TL;DR
- **Verification** = solving the equations right (code and numerical error); **validation** = solving the right equations (does the model represent the hardware?) [1], [2]. A converged simulation of the wrong geometry is verified and invalid.
- **Space Bar tenets apply directly** (`engineering-ethos` knowledge note): validate against *independent* truth (closed form, another code with a different discretisation, measurement) — never against a previous run of the same pipeline; **fix pass criteria before looking**; record everything; report misses faithfully.
- **Four layers of evidence**, cheapest first: (1) invariants (energy balance / average-gain test, reciprocity $S_{21}=S_{12}$, passivity $|S|\le1$, symmetry); (2) convergence in every numerical parameter (mesh, segments, harmonics, end criterion, box size); (3) cross-method agreement at the *same reference plane*; (4) measurement of the built part, with its own uncertainty.
- **Worked evidence in this KB** (all scripts in `tools/verify/sim_*.py`): openEMS microstrip Z0 within 0.3 % of two independent methods; openEMS patch f_res converged to 0.08 % (GCI ≈ 0.03 %, but the 1 MHz post-processing grid is 0.04 %); NEC vs own MoM: two of eight pre-registered tolerances **missed** (0.46 % resonance offset, 3 Ω feed resistance) and are reported as findings, not tuned away; ngspice matched five closed forms, after fixing three set-up traps.
- **The W5-S11 campaign** (Example 6): seven scripts and 42 pre-registered checks. **About a third missed** (nose cone at 433 MHz, laminate scaling, slot resonance and loss, end criteria, STL import, the optimiser's gain range, terrain, censoring fits), and every miss is reported with its cause. The largest uncertainty found was **model form**, not numerics: ITM and two-ray disagree by 10–50 dB for a landed rocket on a real profile.
- **Traps that validation caught here**: NEC2++ average gain depending on the φ-grid start (0.958 vs 1.004); PyNEC extended kernel silently ignored if set before `geometry_complete()`; openEMS end criterion evaluated on wall-clock time (non-reproducible stop step); SPICE noise figure at 27 °C instead of 290 K and with a noisy load; a Colpitts FFT taken before the bias network settled (31 kHz "oscillation").

## Intuition (no math)
A simulator answers exactly the question you typed, with a numerical error you did not see. Three things can be wrong: the *question* (geometry, materials, ports, surroundings differ from the hardware), the *numerics* (mesh too coarse, stopped too early, too few harmonics), and the *reading* (post-processing, reference planes, units). Verification attacks the second and third; validation the first. The most dangerous result is one that looks plausible — a clean S11 dip at almost the right frequency — because nobody questions it. That is why the pass criteria are written *before* running: once you have seen a nice plot, every discrepancy starts to look explainable.

## The math

### Level 1 — convergence and observed order
If a quantity $f(h)$ converges with mesh size $h$ as $f(h) = f_0 + Ch^p + \ldots$, three meshes with ratio $r = h_1/h_2 = h_2/h_3$ give the **observed order**
$$p = \frac{\ln\left|(f_1-f_2)/(f_2-f_3)\right|}{\ln r}$$
and the **Richardson-extrapolated** value $f_0 \approx f_3 + \frac{f_3-f_2}{r^p-1}$ [3]. Compare $p$ with the method's formal order (FDTD 2; FEM 2p for S-parameters; edge singularities reduce it towards 0.5–1). An observed order far from theory means the meshes are not yet in the asymptotic range, or the "result" is quantised by post-processing.

### Level 2 — Grid Convergence Index (Roache)
A conservative relative uncertainty for the finest-mesh result:
$$\mathrm{GCI}_{fine} = \frac{F_s\,|(f_3-f_2)/f_3|}{r^p-1},\qquad F_s = 1.25\ \text{(three meshes)},\ 3\ \text{(two meshes)}$$
with the generalisation for non-constant ratios in Celik et al. [4]. GCI bounds only the *discretisation* error — not model-form error (wrong εr, missing connector).

### Level 3 — uncertainty budget and comparison metric
For validation against measurement, compare the difference $E = S - D$ (simulation − data) with the combined uncertainty $u_{val} = \sqrt{u_{num}^2 + u_{input}^2 + u_D^2}$ (numerical, input-parameter and measurement uncertainty; ASME V&V 20 [2]). If $|E| \gg u_{val}$ the model has a form error to find; if $|E| \lesssim u_{val}$ the model is validated *to that level* and no better. Input uncertainty is usually dominant for PCB RF: εr ± 0.2 moves a 2.45 GHz FR-4 patch by ±2.3 %, far more than any mesh error.

## Design equations & rules of thumb

| Check | Pass level (typical) | Where used in this KB |
|---|---|---|
| Average-gain / energy balance (lossless) | 1.00 ± 0.02 free space; 2.00 over PEC | NEC and own MoM |
| Reciprocity | $|S_{21}-S_{12}|$ < 10⁻³ | any passive model |
| Passivity | $\max\mathrm{eig}(S^HS) \le 1$ | vector-fit models |
| Mesh study | ≥ 3 levels, ratio ≥ 1.3; change < ¼ of the tolerance you need | openEMS patch |
| NEC segments | double segments: Z within 1 Ω, G within 0.1 dB | NEC page |
| FDTD end criterion | −40 dB routine, −50 dB high Q; deterministic (`exact_endcriteria`) | openEMS page |
| HB harmonics | double K: results unchanged | HB page |
| Transient settling | ≥ 5 × slowest time constant before the FFT window | SPICE page |
| Cross-method | agree within the sum of their numerical uncertainties | microstrip Z0 |
| Measurement | within $u_{val}$ incl. εr/geometry tolerance | (to do, NanoVNA) |

**Canonical benchmarks** (known answers) to run before trusting a new tool or set-up:

| Benchmark | Known answer | Tests |
|---|---|---|
| Thin λ/2 dipole | resonance ≈ 0.483λ at a = 10⁻⁴λ, R ≈ 72 Ω, 2.15 dBi | MoM kernels, feed |
| λ/4 monopole on PEC | half the dipole Z, 5.19 dBi, AGT 2 | ground/image |
| PEC sphere RCS | Mie series (optical limit πa²) | scattering, NF2FF |
| WR-90 waveguide | TE10 cutoff 6.557 GHz | FEM/FDTD dispersion |
| Rectangular cavity | $f_{mnp}$ closed form | eigenmode solvers, Q with wall loss |
| Microstrip Z0 | H-J/FD solver within 0.3 % | ports, mesh at edges |
| Butterworth/Chebyshev LC filter | closed-form $|S_{21}|$ | circuit solvers |
| Matched pad NF | NF = loss at 290 K | SPICE noise set-up |

## Worked examples

### 1 — a mesh study with an honest uncertainty (openEMS patch, `sim_openems_patch.py`)
Max cell 3.08 → 2.05 → 1.38 mm ($r$ ≈ 1.50, 1.49): $f_{res}$ = 2.3860, 2.3950, 2.3970 GHz. Observed order (Celik iteration) $p$ = 3.9 — higher than FDTD's formal 2, a warning sign: the differences (9 MHz, 2 MHz) are only 9 and 2 steps of the 1 MHz post-processing grid. Richardson: $f_0$ = 2.3975 GHz; GCI_fine = 0.03 %. Honest statement: *numerical* uncertainty of $f_{res}$ ≈ ±0.1 % (grid quantisation and non-asymptotic order), versus a TL-model design error of −2.2 % and a laminate-εr uncertainty of ±2.3 %. The simulation is not the limiting factor; the board material is.

### 2 — cross-method agreement that means something (microstrip)
| Method | Discretisation | Z0 (W 2.80, h 1.51 mm, εr 4.5, t 0) |
|---|---|---|
| Hammerstad–Jensen | closed-form fit to exact solutions | 50.44 Ω |
| 2-D finite-volume solver, Richardson over 3 meshes | quasi-static, own code (W1-A4) | 50.38 Ω |
| openEMS EC-FDTD, MSL port (λ/50) | 3-D full-wave, port extraction | 50.31 Ω (λ/30: 49.98) |
Three different discretisations within 0.26 %; openEMS's own mesh change (0.6 %) is the largest term — so "openEMS Z0 ±0.7 %" is the defensible statement.

### 3 — faithful reporting of pre-registered misses (NEC vs own MoM)
`sim_nec_vs_mom.py` fixed its tolerances before the first run: resonant length within 1 mm, Yagi feed R within 3 Ω, gain within 0.2 dB, etc. Results: 6 pass, **2 miss** (−1.5 mm, −3.1 Ω). The script prints `[MISS]` and a summary rather than widening the tolerance. The interpretation (different feed models — NEC's one-segment applied-field source vs a node delta-gap — produce ~0.5 % length differences for a 2 mm wire; thin wires agree to 0.06 %) is recorded as a *finding* with a proposed discriminating measurement (cut two dipoles, measure resonance on a NanoVNA). This is exactly the "report failures with their output" tenet.

### 4 — traps found only because an invariant was checked
- **Average gain 0.958 for a lossless Yagi in NEC2++** → own integration of the same pattern gave 0.999 → the φ-grid started on the main beam; shifting φ₀ by 90° gave 1.004. Invariant: energy balance. Without the check one might "fix" a non-existent loss.
- **SPICE NF 9.01 dB for a 6 dB pad** → theory says 6.00 → the load resistor's noise was counted (Friis with the load as a second stage gives exactly 9.01 dB) → `noisy=0`. Then 6.149 dB at the default 27 °C → source resistor at 290 K (`temp=16.85`) → 6.112 dB = $1+(L-1)T/T_0$.
- **A lumped port on a PEC wall** reads |S11| = 0 dB at every frequency: the excitation edge is shorted. **STL faces lying on mesh lines** lost PEC edges and detuned a whip by 11 %. **Without `exact_endcriteria`, end criteria from 10⁻² to 10⁻⁵ all stopped at the same step** in an 8 s run, so the criterion was never actually tested. Details are in [openEMS practicalities](openems-workflow.md#practicalities-field-dumps-curved-and-stl-geometry-graded-meshes-and-a-deliberately-broken-model-toolsverifysim2_openems_brokenpy).
- **openEMS stop step 13 502 vs 16 555 for the same model** → source code shows the end criterion is evaluated at the ~4 s wall-clock progress report → `exact_endcriteria=True` → identical 2 660-step runs.

### 5 — comparing with a measurement (plan for the flight-computer antenna)
1. Pre-register: simulated f_res, S11 depth, bandwidth, with the input-uncertainty band from εr ± 0.2 and etch ± 20 µm (run the model at the corners).
2. Measure with a calibrated NanoVNA **at the same reference plane** as the simulation port (calibrate at the U.FL/SMA, or de-embed the pigtail with its measured S-parameters: `pigtail.inv ** meas` in scikit-rf).
3. Suppress what the model does not contain (cable common-mode current: ferrite choke; hand effect: hold the cable far away), or add it to the model.
4. Compare $E$ with $u_{val}$; if outside, suspect geometry/material first (actual εr, soldermask, ground-plane size, enclosure), then numerics.
5. Record the model version, mesh, measured file and calibration kit together ([VNA calibration](../17-test-measurement/vna-fundamentals-calibration.md), [fixtures and de-embedding](../17-test-measurement/fixtures-and-deembedding.md)).

### 6 — a pre-registration scorecard: the W5-S11 simulation campaign (2026-10-13)
Every script carries its expectations in its header, written before the first run. Later changes appear only as dated addenda. Results:

| Study (script) | Pre-registered check | Result | Verdict |
|---|---|---|---|
| nose cone, 915 MHz (`sim2_openems_nosecone.py`) | shift −0.5…−3 % | −1.2 % (3 meshes, 3 boundary set-ups) | pass |
| nose cone, 433 MHz | shift −0.3…−2 % | −2.8 % | **miss** — the energy-fraction estimate is too crude |
| εr 4.0 vs 4.7 | 0.8 × the shift | 0.92 × | **miss** — mixed normal/tangential field |
| av-bay counterpoise | > 3 % | +3.4 % | pass |
| slot under microstrip (`sim2_openems_pcb.py`) | Z_slot 50–150 Ω; resonance ±15 % | 70–94 Ω; +13.9 / +15.6 % | pass / **narrow miss** |
| slot, 60 mm, at 915 MHz | < −3 dB | −0.97 dB | **miss** |
| SMA pad, L2 intact / voided | RL 10–14 / 17–25 dB at 2.45 GHz; meshes within 1 dB | 11.4 / 21.3 dB; within 0.4 dB (after a port-in-PML set-up error was found and fixed) | pass |
| 915 MHz IFA in a fibreglass tube | shift −0.8…−3 % | best-match frequency **+0.68 %** (S11 minimum is not a resonance for this inductive IFA) | **miss** (sign) |
| IFA efficiency / directivity | 50–85 % / 1.8–3.0 dBi | 41 % / 8.5 dBi with MUR, 34 % / 4.9 dBi with PML | **miss**, not trusted (NF2FF anomaly) |
| array blindness, 15-element row (`sim2_openems_array_blindness.py`) | dip ≥ 3 dB at 38–50°; none at λ/2 | 2.2 dB dip at 53°; none at λ/2 | **miss** / pass |
| broken models (`sim2_openems_broken.py`) | B1–B6 | B1 ✓, B2 ✓ (after a port-on-wall error), B3 ✓, B4 ✗ (effect smaller), B5 ✗ (STL trap), B6 partly ✗ | see openEMS page |
| phase noise (`sim2_phase_noise_transient.py`) | ±1 dB over 0.3–30 MHz | 0.22 dB (F = 1); +1.94 dB at one bin (F = 2) | pass / **miss** — the tolerance was below the estimator scatter |
| Yagi optimiser (`sim2_nec_yagi_optimise.py`) | 7.5–8.5 / 6.5–7.8 dBi | 9.90 / 8.55 dBi | **miss**, high — superdirective optimum |
| ITM on a real profile (`sim2_coverage_itm.py`) | ITM real vs flat within 6 dB | −52.6 dB | **miss** — model-form disagreement |
| censored-data fits | naive n low > 0.5, σ low > 2 dB; Tobit/truncated recover | n −1.8 ✓, σ −1.92 ✗; Tobit ✓, truncated ✗ | mixed |

What the misses teach:
1. **First-order estimates are worth writing down even when they miss.** The nose-cone and slot misses each gave a correction factor: cone shift about 2× larger at 433 MHz, slot εeff ≈ 2.1 rather than 2.75. Those factors are now better rules of thumb than the originals.
2. **Some misses are in the set-up, not the physics.** The shorted port, the STL ambiguity, the end criterion that was never tested and the mesh slivers were all found because the result disagreed with a written expectation.
3. **A tolerance must exceed the estimator's own scatter.** Allowing ±1 dB on a single Welch bin with about 30 averages is a coin toss.
4. **Model-form uncertainty dwarfs numerical uncertainty near the ground.** Every terrain model here is converged and verified (ITM matches NTIA's vectors to 0.05 dB), yet two of them differ by 50 dB on the same path. Only a measurement decides.

### 7 — what to do when a simulated S11 looks wrong
Work through the symptom table on the [openEMS page](openems-workflow.md#practicalities-field-dumps-curved-and-stl-geometry-graded-meshes-and-a-deliberately-broken-model-toolsverifysim2_openems_brokenpy):
- spikes are enclosure or box modes: compare with the closed-form $f_{mn0}$;
- 0 dB everywhere means a shorted or open port;
- a −10 to −20 dB floor on a lossless line means a port inside the PML or too near a discontinuity;
- ripple or a wrong bandwidth means a truncated ring-down;
- a resonance that jumps without a physical change is a voxelisation artefact;
- far-field numbers that move with the boundary point to the NF2FF set-up.

In every case, look at the material and PEC dumps before changing the physics. Then re-run the known-answer reference: the 50 Ω microstrip should give |S11| < −50 dB.

## Practical notes
- **Write the expectation first** — one line per quantity with a tolerance and what a miss would mean — in the script header (as the `sim_*.py` scripts do) or a dated file; add later ideas as an addendum, never an edit.
- **Change one thing at a time** in convergence studies; keep all other parameters (box size, end criterion) fixed, then vary those separately.
- **Deterministic runs**: fixed seeds, `exact_endcriteria`, recorded versions; otherwise "the same" run differs and regressions are ambiguous.
- **Independent means different**: re-running the same solver with a finer mesh is verification, not validation. Two FDTD codes with the same (wrong) port model can agree and both be wrong; a closed form or a MoM code breaks that correlation.
- **Keep the misses**: a table of what disagreed and why is more valuable to the next designer than a clean plot.

## Common mistakes & misconceptions
- **"It converged, so it's right."** Convergence says nothing about the geometry/material being right.
- **"Two runs of my model agree."** Run-to-run agreement is blind to shared errors.
- **"The measurement is the truth."** It has uncertainty too (calibration, cable, fixture, environment); compare with $u_D$ included.
- **Moving the goalposts** — widening tolerances after seeing the result, or dropping the benchmark that failed.
- **Comparing at different reference planes** — the commonest cause of "the simulation is 20 MHz off" for PCB antennas fed through a trace and connector.
- **Quoting three decimals** from a model whose εr is known to two significant figures.
- **Setting a pass tolerance tighter than the estimator's scatter** (one spectral bin, a handful of Monte-Carlo runs). The "miss" is then noise. Estimate the scatter first (Example 6).
- **Fixing a miss by re-running until it passes** (new seeds, new tolerances). Post-hoc runs are useful diagnostics, but label them post-hoc and keep the original verdict (Example 6).

## How to simulate / verify
- `tools/verify/sim_openems_msl.py`, `sim_openems_patch.py` — mesh studies with pre-registered expectations (openEMS venv Python).
- `tools/verify/sim_nec_vs_mom.py` — cross-code comparison with PASS/MISS reporting.
- `tools/verify/sim_ngspice_examples.py`, `sim_harmonic_balance.py` — closed-form and cross-method circuit checks.
- `tools/verify/tline_fd2d.py` — Richardson extrapolation built in (`refine_study`).
- `cd tools && python3 -m pytest rfcalc/tests -q` — calculator regression tests pinned to KB worked examples (159, including the ITM port against NTIA's vectors).
- `tools/verify/sim2_*.py` (W5-S11) — the Example 6 campaign: nose cone, PCB features, array blindness, broken models (openEMS venv); phase noise, Yagi optimiser, ITM coverage and censoring (anaconda Python). Results: `sim2_*_results.txt`.

## Open questions / gaps
- No simulation-vs-measurement correlation exists yet in this KB for Marcus's own boards; the first NanoVNA measurement of a flight-computer antenna, compared against a pre-registered openEMS prediction, would be the most valuable validation step.
- A formal $u_{val}$ budget for a PCB antenna (εr, thickness, etch, mask, ground size) has not been computed.
- Example 6's openEMS predictions (nose-cone shift, slot and pad numbers, IFA) are all unmeasured. The first NanoVNA check should be the whip in the assembled nose cone, against −1.2 % at 915 MHz and −2.8 % at 433 MHz.

## Sources
1. W. L. Oberkampf and C. J. Roy, *Verification and Validation in Scientific Computing*, Cambridge University Press, 2010 — definitions, code vs solution verification, validation metrics. (textbook)
2. ASME V&V 20-2009, *Standard for Verification and Validation in Computational Fluid Dynamics and Heat Transfer* — validation comparison error and uncertainty $u_{val}$ (method transferable to EM). (standard)
3. L. F. Richardson, "The deferred approach to the limit," *Phil. Trans. R. Soc. A*, 226:299–361, 1927; P. J. Roache, "Perspective: a method for uniform reporting of grid refinement studies," *J. Fluids Eng.*, 116(3):405–413, 1994. (peer-reviewed)
4. I. B. Celik, U. Ghia, P. J. Roache, C. J. Freitas, H. Coleman, P. E. Raad, "Procedure for estimation and reporting of uncertainty due to discretization in CFD applications," *J. Fluids Eng.*, 130(7):078001, 2008. (peer-reviewed)
5. A. Taflove and S. C. Hagness, *Computational Electrodynamics*, 3rd ed., 2005 — dispersion/convergence order of FDTD; J.-M. Jin, *The Finite Element Method in Electromagnetics*, 3rd ed., 2014 — convergence of FEM. (textbooks)
6. IEEE Std 1597.1-2008, *Standard for Validation of Computational Electromagnetics Computer Modeling and Simulations*, and IEEE 1597.2-2010 (recommended practice, incl. the Feature Selective Validation method). (standard)
7. Space Bar avionics knowledge base, `engineering-ethos.md` and `simulation-validation-methods.md` (team tenets: independent truth, pre-registration, record everything, faithful reporting). (internal)
8. This repository: `tools/verify/sim_*.py` and `research-logs/W3-C2-simulation-tools.md` (all results quoted). (verification)
