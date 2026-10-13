---
title: Numerical methods overview — from root-finding to FDTD, MoM and FEM
domain: 00-math-foundations
slug: numerical-methods-overview
tags: [numerical-methods, root-finding, newton, quadrature, gauss-legendre, fft, ode-solvers, stiffness, finite-differences, fdtd, yee, courant, mom, fem, convergence, validation]
prerequisites: [matrices-and-linear-algebra-for-networks.md, differential-equations-circuits-waves.md, vector-calculus-for-em.md]
related:
  - fourier-series-and-transform.md
  - linear-systems-convolution.md
  - ../16-simulation-tools/tool-landscape-overview.md
  - ../16-simulation-tools/em-solvers-fdtd-mom-fem.md
  - ../16-simulation-tools/openems-workflow.md
  - ../16-simulation-tools/nec-antenna-modelling.md
  - ../16-simulation-tools/spice-circuit-simulation.md
  - ../16-simulation-tools/simulation-validation.md
  - ../14-sdr-dsp/fft-spectral-analysis-windows.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Numerical methods overview — from root-finding to FDTD, MoM and FEM

## Questions this page answers
- How do calculators and simulators solve equations that have no closed form?
- When should I use bisection, Newton or Brent's method?
- Which numerical integration rule should I use, and why is Gauss–Legendre so accurate?
- Why is the FFT fast, and what does it actually compute?
- Why does my transient simulation blow up or need tiny time steps (stiffness, stability)?
- What are FDTD, MoM and FEM, how do they differ, and which one fits antennas, PCBs, cavities?
- What is the Courant (CFL) condition and "cells per wavelength"?
- How do I know a simulation result is right (convergence and validation)?

## TL;DR
- **Root finding**: bisection is slow but guaranteed (1 bit per iteration: 38 iterations to 10⁻¹⁰ in the verify script); Newton converges quadratically (5 iterations) but needs a derivative and a good start; `scipy.optimize.brentq` combines both — the default for "solve for the width that gives 50 Ω".
- **Quadrature**: trapezoid/Simpson are fine for smooth periodic or tabulated data; Gauss–Legendre with N points is exact for polynomials of degree 2N−1 and reached 3×10⁻¹⁵ on the dipole-pattern integral with 32 points. Singular or oscillatory integrands need special handling.
- **FFT**: an $O(N\log N)$ algorithm for the DFT (≈30× faster than a matrix DFT at N = 1024 here, far more at large N). It computes exactly the DFT — with its periodic-extension assumptions.
- **ODEs**: explicit methods (Euler, RK4) have stability limits (forward Euler on an RC blows up for $\Delta t>2\tau$); stiff circuits (widely separated time constants) need implicit methods (backward Euler, trapezoidal, Gear/BDF — what SPICE uses). Oscillators need energy-conserving/symplectic or small-step methods.
- **Finite differences** replace derivatives with differences on a grid; central differences are 2nd-order accurate (halve h → error ÷4). Curved boundaries become staircases (coax C′ 2.7 % low on a 161² grid).
- **FDTD** (Yee 1966): leapfrogs E and H on a staggered grid; explicit; broadband from one run; needs Courant number $S=c\Delta t/\Delta x\le1$ in 1-D ($\le1/\sqrt3$ in 3-D uniform grids) and ≥ 10–20 cells per wavelength; numerical dispersion makes waves slightly slow (0.31 % at 20 cells/λ, S = 0.5). openEMS uses an equivalent-circuit variant (EC-FDTD).
- **MoM** (NEC, integral-equation solvers): unknowns only on conductor surfaces/wires; dense matrix; ideal for wire antennas and open radiation problems (radiation condition built into the Green's function). Square-plate capacitance: 40.60 pF with 1600 pulses vs benchmark 40.81 pF.
- **FEM** (HFSS, Elmer, FEniCS): volume mesh of tetrahedra; sparse matrix; handles complex geometry and materials; needs absorbing boundaries/PMLs for radiation.
- **Always** do a convergence study (refine mesh/time step until the answer stops changing) and validate against a known result before trusting a new model.

## Intuition (no math)
Most real problems don't have tidy formula answers. Numerical methods replace a smooth, infinite problem with a large but finite set of simple arithmetic steps: chop time into small steps, space into small cells, an integral into a weighted sum, a curved surface into flat patches. The answer is then an approximation whose error you control by making the pieces smaller — at the cost of computer time and memory.

Three families dominate EM simulation:
- **FDTD** fills space with a grid of little boxes and marches Maxwell's equations forward in time, like a very fine cellular automaton. You kick it with a pulse and watch fields spread; one run gives the response at all frequencies in the pulse's bandwidth.
- **MoM** only puts unknowns on the metal (wires, plates). It asks: "what currents on the metal would make the total field satisfy the boundary conditions?" Each little piece of current affects every other through a known formula (the Green's function), so you get a dense but relatively small matrix. Perfect for wire antennas like dipoles, Yagis, monopoles on rockets.
- **FEM** fills the whole volume with small tetrahedra and finds the field that best satisfies Maxwell's equations in an averaged ("weak") sense. It shines for complicated shapes and materials (filters, connectors, packages) but needs care at open boundaries.

The trade-offs are always: accuracy vs cells, frequency vs time domain, open vs closed problems, metal vs dielectric-heavy structures.

## The math

### Level 1 — the core ideas

- **Discretise**: replace continuous $x$ by samples $x_i=x_0+ih$.
- **Approximate**: derivatives by differences ($f'(x)\approx\frac{f(x+h)-f(x-h)}{2h}$), integrals by sums ($\int f\approx\sum w_if(x_i)$), functions by simple pieces (linear, polynomial).
- **Solve**: a set of algebraic equations, usually linear ($\mathbf A\mathbf x=\mathbf b$; see [matrices](matrices-and-linear-algebra-for-networks.md)).
- **Check**: error shrinks as $h^p$ for an order-$p$ method; confirm by refining.

### Level 2 — the standard toolbox

**Root finding** [1 ch. 9]. Solve $g(x)=0$.
- *Bisection*: keep a bracket $[a,b]$ with a sign change and halve it. Error halves each step; guaranteed if $g$ is continuous.
- *Newton–Raphson*: $x_{n+1}=x_n-g(x_n)/g'(x_n)$. Quadratic convergence (digits double each step) near a simple root; can diverge or jump roots from a poor start.
- *Secant/Brent*: derivative-free; Brent's method (`brentq`) is bracketed and super-linear — the robust default.
- Verified: solving BPSK BER = 10⁻⁵ for $E_b/N_0$ (9.588 dB): bisection 38 iterations, Newton 5.
- RF uses: synthesising microstrip width for a target $Z_0$, finding resonant frequencies ($\mathrm{Im}\,Z=0$), solving waveguide/dielectric-slab dispersion equations, matching-network component values.

**Numerical integration (quadrature)** [1 ch. 4].
- Trapezoid: error $O(h^2)$ (but spectrally accurate for smooth periodic integrands over a full period).
- Simpson: $O(h^4)$ for smooth integrands; needs even intervals.
- Gauss–Legendre: nodes at Legendre-polynomial roots; N points integrate polynomials up to degree 2N−1 exactly.
- Adaptive (`scipy.integrate.quad`): refines where the integrand varies; handles endpoint singularities.
- Verified on $\int_0^\pi\frac{\cos^2(\frac\pi2\cos\theta)}{\sin\theta}d\theta=1.21883$ (the λ/2-dipole radiated-power integral; gives $D=1.641$): N = 32 errors — trapezoid 9.6×10⁻⁷, Simpson 3.8×10⁻⁶, Gauss 2.7×10⁻¹⁵. (Simpson lags here because the integrand's endpoint behaviour defeats its error model — a reminder that "higher order" needs smoothness.)

**FFT** [1 ch. 12], [2]. The Cooley–Tukey algorithm splits an N-point DFT into two N/2-point DFTs recursively (for $N=2^m$), reducing $N^2$ complex multiplies to $\frac N2\log_2N$. It is not an approximation: it gives the DFT exactly (verified to 10⁻¹¹). Everything about windows, leakage and bin scaling is DFT physics ([Fourier](fourier-series-and-transform.md), [FFT and windows](../14-sdr-dsp/fft-spectral-analysis-windows.md)).

**ODE integration** [1 ch. 17].
- Forward (explicit) Euler: $y_{n+1}=y_n+\Delta t\,f(t_n,y_n)$, 1st order. For $\dot y=-y/\tau$ it is stable only if $\Delta t<2\tau$ (verified: 1.9τ decays, 2.1τ explodes).
- Runge–Kutta 4: 4th order; RC step to 5τ with $\Delta t=\tau/10$ accurate to 10⁻⁶ (verified).
- **Stiffness**: circuits often mix nanosecond and millisecond time constants (RF decoupling + bias RC). Explicit methods must use the smallest time constant for stability even when it has decayed away. Implicit methods (backward Euler, trapezoidal, BDF/Gear) are stable for any step on decaying modes; SPICE uses trapezoidal/Gear with adaptive steps and Newton iteration on the nonlinear equations at each step [3].
- **Energy conservation**: explicit Euler makes an ideal LC tank's energy grow without bound (verified: > 2× after 5000 steps of $0.02/\omega_0$); a symplectic (semi-implicit) Euler keeps it bounded within 1 %. The trapezoidal rule preserves the amplitude of undamped oscillations (but adds phase error); backward Euler adds artificial damping — SPICE users see this as oscillators that won't start or rings that decay too fast.

**Finite differences** [1 ch. 20]. Central difference $f''\approx\frac{f_{i+1}-2f_i+f_{i-1}}{h^2}$, error $O(h^2)$ (verified: halving h divides the first-derivative error by 3.99998). Applied to Laplace's equation on a grid → sparse linear system (5-point stencil). Verified: coax with b/a = 2.3 (air) has $C'=2\pi\varepsilon_0/\ln2.3=66.79$ pF/m; a Cartesian FD grid gives 63.45 pF/m (81²) and 65.00 pF/m (161²) — converging, with the error dominated by staircasing the circular boundaries. Conformal/sub-cell techniques or FEM fix curved boundaries.

### Level 3 — full-wave EM solvers

**FDTD (finite-difference time-domain)** [4], [5]. Yee's scheme places E and H components on interleaved grids offset by half a cell and half a time step, then leapfrogs the curl equations:
$$H^{n+1/2}=H^{n-1/2}-\frac{\Delta t}{\mu}\nabla_h\times E^n,\qquad E^{n+1}=E^n+\frac{\Delta t}{\varepsilon}\nabla_h\times H^{n+1/2}$$
(with $\nabla_h\times$ the central-difference curl). Properties:
- Explicit, 2nd-order in space and time; memory ∝ number of cells; no matrix solve.
- **Courant–Friedrichs–Lewy stability**: $c\Delta t\le\left(\frac{1}{\Delta x^2}+\frac{1}{\Delta y^2}+\frac{1}{\Delta z^2}\right)^{-1/2}$ — in 1-D, $S=c\Delta t/\Delta x\le1$ (verified: S = 1.05 blows up). Yee's original paper stated the condition incorrectly; it was corrected by Taflove and Brodwin (1975) [4].
- **Numerical dispersion**: the discrete dispersion relation $\frac{1}{c\Delta t}\sin\frac{\omega\Delta t}{2}=\frac{1}{\Delta x}\sin\frac{k\Delta x}{2}$ (1-D) makes waves travel slightly slower than $c$ and frequency-dependently. Verified: S = 1 in 1-D is exact ("magic time step", $v_p=c$); S = 0.5 with 20 cells/λ gives $v_p=0.99687c$ vs theory 0.99689c. Rule: ≥ 10 cells per wavelength in the highest-εr material at the highest frequency, 20+ for accurate phase (arrays, filters).
- Broadband from one pulse run; S-parameters via DFT of port voltages/currents; far fields via near-to-far transformation.
- Needs absorbing boundaries (PML, Mur) for open problems; dispersive materials via auxiliary differential equations (Debye/Lorentz; see [linear systems](linear-systems-convolution.md) for why they must be causal).
- Weaknesses: staircased curved/thin features (use fine or graded meshes), high-Q structures need very long runs, and thin wires need sub-cell models.
- **openEMS** uses Equivalent-Circuit FDTD (EC-FDTD), supports Cartesian and cylindrical meshes, Matlab/Octave/Python front ends [6] ([openEMS workflow](../16-simulation-tools/openems-workflow.md)).

**MoM (method of moments / integral-equation methods)** [7]. Write the fields as integrals of unknown surface/wire currents against the Green's function ([vector calculus](vector-calculus-for-em.md): $e^{-jkR}/4\pi R$), enforce the boundary condition (tangential E = 0 on metal, or V = const in electrostatics), expand the unknown in basis functions (pulses, triangles, RWG, sinusoids) and test with weighting functions (point matching or Galerkin) → dense $\mathbf Z\mathbf I=\mathbf V$.
- Unknowns only on conductors; radiation condition automatic; ideal for wire antennas (NEC-2/4: [NEC modelling](../16-simulation-tools/nec-antenna-modelling.md)), planar layered structures (Sonnet, "2.5-D" solvers), RCS of metal targets.
- Cost: $O(N^2)$ memory, $O(N^3)$ direct solve (fast multipole/iterative methods reduce this).
- Verified toy problem: capacitance of a 1 m × 1 m plate with pulse basis + point matching (analytic self-term): 40.35 pF (20×20), 40.60 pF (40×40), converging towards the accurate benchmark 0.3667874·4πε₀·L = 40.81 pF [8]. The slow convergence comes from the edge/corner charge singularities — the same reason antenna wire ends and patch edges need fine segmentation.
- Pitfalls: segment length ≲ λ/10–λ/20, wire radius ≪ segment length (thin-wire kernel validity), care at junctions of different radii, and buried/lossy grounds need special Green's functions.

**FEM (finite element method)** [9]. Mesh the volume (tetrahedra), approximate the field with low-order polynomial basis functions on each element (edge/Nédélec elements for vector E-fields to avoid spurious modes), and require the residual of the curl–curl equation $\nabla\times\mu^{-1}\nabla\times\mathbf E-\omega^2\varepsilon\mathbf E=-j\omega\mathbf J$ to be orthogonal to the basis (Galerkin weak form) → sparse $\mathbf K\mathbf x=\mathbf b$ per frequency.
- Handles arbitrary geometry and inhomogeneous/anisotropic materials; adaptive mesh refinement driven by error estimates (HFSS's hallmark).
- Frequency-domain (one solve per frequency, with interpolating sweeps); eigenmode solvers for cavities/filters.
- Open problems need PMLs or absorbing boundaries.
- Verified toy problem: 1-D FEM with linear elements for $-u''=1$ reproduces the exact nodal values (a known super-convergence property for this case).

**Choosing a method**

| Problem | Good fit | Why |
|---|---|---|
| wire antennas (dipole, monopole on rocket body approximated as wires, Yagi, helix) | MoM (NEC) | few unknowns, open space, fast sweeps |
| patch antenna on finite ground, with connector | FDTD (openEMS) or FEM | dielectric + metal + feed details; broadband |
| PCB traces, vias, planar filters | 2.5-D MoM (layered) or FDTD | layered media Green's functions / broadband |
| cavity filters, connectors, packages | FEM | complex 3-D geometry, high Q, eigenmodes |
| broadband pulse / TDR / radar pulse | FDTD | time domain native |
| large RCS / reflectors | MoM + fast multipole, or asymptotic (PO/GTD) | electrically large |
| circuits with lumped parts | SPICE / harmonic balance | ODEs + nonlinear devices ([RF simulators](../16-simulation-tools/rf-circuit-simulators-harmonic-balance.md)) |

**Convergence and validation** (the Space Bar engineering tenets apply directly: validate against independent truth — closed-form theory, exact invariants, published measurements, or an independently written tool — never against a previous run of the same pipeline; fix pass criteria before looking at the result; label results "sim-predicted", never "measured"): (1) refine mesh and time step until key outputs (resonant frequency, S₁₁ minimum, gain) change by less than your tolerance; (2) check energy/passivity (|S₁₁|² + |S₂₁|² ≤ 1); (3) validate the setup on a problem with a known answer (half-wave dipole impedance ≈ 73 + j42 Ω, patch resonance from cavity model, the benchmarks in the verify script); (4) cross-check with a second method or measurement ([simulation validation](../16-simulation-tools/simulation-validation.md)).

## Design equations & rules of thumb

| Rule | When valid | Typical values |
|---|---|---|
| bisection: 1 bit/iteration; Newton: digits double | smooth $g$, simple root | 38 vs 5 iterations to 10⁻¹⁰ |
| Gauss–Legendre N pts exact to degree 2N−1 | smooth integrands | 32 pts → 10⁻¹⁵ |
| FFT cost $\frac N2\log_2N$ vs $N^2$ | $N=2^m$ best | |
| forward Euler stable iff $\Delta t<2\tau_{\min}$ | decaying modes | |
| 1-D FDTD $S\le1$; 3-D uniform $S\le1/\sqrt3$ | Yee | |
| ≥ 10–20 cells per wavelength (in material) | FDTD/FEM | 2.4 GHz in FR-4 (λ ≈ 58 mm): cells ≤ 3–6 mm, finer near metal edges |
| wire segment ≤ λ/10–λ/20, radius ≪ segment | MoM thin wire | 433 MHz: ≤ 35 mm segments |
| convergence study before trusting | always | change < tolerance on refinement |

## Worked examples

**1. Solve for a microstrip width (root finding).** Given a closed-form $Z_0(w)$ (Hammerstad–Jensen, in [planar lines](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md)), find $w$ with $Z_0(w)=50$ Ω: bracket $w\in[0.05h, 20h]$ (Z₀ is monotonic in w) and call `brentq(lambda w: Z0(w)-50, 0.05*h, 20*h)`. Newton would also work but brackets are safer when formulas have piecewise regions.

**2. Choosing an FDTD mesh for a 433 MHz monopole on a rocket.** λ₀ = 692 mm; air around the rocket and a fibreglass body tube (εr ≈ 4–5 → λ ≈ 330 mm inside). Global cells of λ/20 in air (35 mm) are too coarse near the feed and body tube: grade down to ~1 mm at the feed gap and tube wall. With S at the 3-D Courant limit and the smallest cell 1 mm, $\Delta t\approx\frac{1}{c\sqrt3}\times1\,\text{mm}=1.9$ ps; a run of ~50 ns (enough for a low-Q antenna to ring down) needs ~26 000 steps — fine for openEMS on a laptop. A high-Q filter would need far longer.

**3. NEC model of a 433 MHz dipole.** Half-wave dipole ≈ 0.48λ = 332 mm of 1 mm radius wire: 21 segments of 15.8 mm (≈ λ/44) satisfy both the segment-length and thin-wire rules; expect Z ≈ 70 + j0 Ω near resonance and verify that doubling segments changes Z by < 1 %.

**4. SPICE transient with a stiff circuit.** A PA bias network (10 kΩ, 10 µF: τ = 0.1 s) with an RF choke/decoupling resonance (1 nH, 10 pF: ~1.6 GHz): an explicit integrator would need picosecond steps for 0.1 s — 10¹¹ steps. SPICE's implicit trapezoidal/Gear method takes large steps once the fast modes have decayed. If you actually need the RF waveform and the slow bias together, use harmonic balance or envelope simulation instead ([RF simulators](../16-simulation-tools/rf-circuit-simulators-harmonic-balance.md)).

## Practical notes
- Python ecosystem: `scipy.optimize` (brentq, newton, least_squares), `scipy.integrate` (quad, solve_ivp with `Radau`/`BDF` for stiff), `numpy.fft`/`scipy.fft`, `scipy.sparse.linalg`, `scikit-rf`; `PyNEC`/`necpp` for NEC; openEMS Python bindings; FEniCS/Elmer/Palace for FEM.
- Float64 has ~16 digits; subtracting nearly equal numbers (e.g. $1-|\Gamma|^2$ near a perfect match, or $\Delta_e$ in VNA cal) loses digits — reformulate or use higher precision.
- Record solver settings (mesh, time step, boundary, excitation, end criterion) with every result so it can be reproduced — a sim result without its settings is not evidence.

## Common mistakes & misconceptions
1. **"Finer is always better."** Beyond convergence, extra cells only cost time; and in FDTD, the time step shrinks with the smallest cell, so one tiny cell slows the whole run.
2. **Trusting a single run** without a mesh-convergence study.
3. **Ignoring numerical dispersion** in electrically large FDTD models — phase errors accumulate over many wavelengths (arrays, long lines).
4. **Violating the Courant limit** when hand-coding FDTD — instant blow-up (verified).
5. **Using explicit ODE solvers on stiff circuits** — tiny steps or instability.
6. **MoM segments too long or too fat**; mismatched junction radii — wrong impedances.
7. **Assuming the FFT approximates the Fourier transform** — it computes the DFT of your sampled, windowed, periodically-extended record.
8. **Comparing simulated and measured S₁₁ without de-embedding** connectors/cables, or without modelling the feed as built.
9. **Forgetting absorbing boundary distance** (λ/4 or more from radiators is a common minimum; check the solver's guidance) — boundaries too close detune antennas.

## How to simulate / verify
- `python3 tools/verify/math_numerical_methods.py` (~1–5 s) — bisection vs Newton iteration counts; trapezoid/Simpson/Gauss on the dipole integral (and D = 1.641); FFT = DFT with timing; forward-Euler stability limit, RK4 accuracy, explicit vs symplectic energy in an LC tank; central-difference order; FD Laplace coax C′ convergence; 1-D Yee FDTD at S = 1 (vp = c), S = 0.5 (dispersion matches theory), S = 1.05 (unstable); MoM square plate vs 40.81 pF benchmark; 1-D FEM. All PASS.

## Open questions / gaps
- Harmonic balance, envelope transient and shooting methods for nonlinear RF circuits are only mentioned; 16-simulation-tools should cover them.
- Fast multipole / ACA acceleration and asymptotic methods (PO, GTD/UTD) for large structures are not covered.

## Sources
1. W. H. Press, S. A. Teukolsky, W. T. Vetterling, B. P. Flannery, *Numerical Recipes*, 3rd ed., Cambridge (2007): ch. 4 (integration), ch. 9 (root finding), ch. 12–13 (FFT and spectral applications), ch. 17 (ODEs incl. stiff), ch. 20 (PDEs) (textbook; all six chapter numbers confirmed against the contents list on numerical.recipes by W5-S18, 2026-10-13).
2. J. W. Cooley, J. W. Tukey, "An algorithm for the machine calculation of complex Fourier series," *Mathematics of Computation* 19(90):297–301 (1965) (peer-reviewed).
3. L. W. Nagel, *SPICE2: A computer program to simulate semiconductor circuits*, UC Berkeley ERL Memo M520 (1975) — MNA, Newton iteration, implicit (trapezoidal/Gear) integration (technical report; cited for the method description).
4. K. S. Yee, "Numerical solution of initial boundary value problems involving Maxwell's equations in isotropic media," *IEEE Trans. Antennas Propag.* 14(3):302–307 (1966), doi:10.1109/TAP.1966.1138693; stability condition corrected by A. Taflove, M. E. Brodwin, *IEEE Trans. MTT* 23(8):623–630 (1975) (peer-reviewed).
5. A. Taflove, S. C. Hagness, *Computational Electrodynamics: The Finite-Difference Time-Domain Method*, 3rd ed., Artech House (2005): ch. 3 (Yee algorithm), ch. 4 (numerical dispersion and stability), ch. 7 (PML) (textbook).
6. T. Liebig et al., openEMS documentation, https://docs.openems.de/intro.html ; T. Liebig, A. Rennings, S. Held, D. Erni, "openEMS – a free and open source equivalent-circuit (EC) FDTD simulation platform supporting cylindrical coordinates suitable for the analysis of traveling wave MRI applications," *Int. J. Numerical Modelling: Electronic Networks, Devices and Fields* (2013) (software documentation / peer-reviewed; volume/page details not re-verified).
7. R. F. Harrington, *Field Computation by Moment Methods*, Macmillan (1968; IEEE Press reprint 1993), ch. 1–2 (method, electrostatic examples incl. square plate) (textbook); G. J. Burke, A. J. Poggio, *NEC — Method of Moments*, LLNL (1981) (technical report).
8. S. Mukhopadhyay, N. Majumdar, "Use of triangular elements for nearly exact BEM solutions," arXiv:0704.1563 (2007), Table 2 (compilation of unit-square-plate capacitance values: Maxwell 1878 0.3607; Goto et al. 1992 0.3667892; F. H. Read, *J. Comput. Phys.* 133:1–5 (1997) 0.3667874, all × 4πε₀L). https://arxiv.org/abs/0704.1563 (preprint + cited peer-reviewed values).
9. J.-M. Jin, *The Finite Element Method in Electromagnetics*, 3rd ed., Wiley-IEEE (2014), ch. 3–4 (1-D/2-D FEM), ch. 8 "Vector Finite Elements" (edge elements), ch. 9 "Absorbing Boundary Conditions" (textbook; corrected by W5-S18, 2026-10-13: ch. 9 is ABCs, not edge elements — from the publisher's sample ToC and O'Reilly chapter previews via search summaries, not opened directly).
