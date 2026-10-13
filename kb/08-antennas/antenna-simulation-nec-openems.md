---
title: Antenna simulation — NEC-2/MoM for wire antennas, openEMS/FDTD for patches and PCB antennas, modelling rules and verification
domain: 08-antennas
slug: antenna-simulation-nec-openems
tags: [nec2, nec4, mom, method-of-moments, 4nec2, xnec2c, necpp, pynec, mmana-gal, mininec, eznec, openems, fdtd, segmentation, average-gain-test, convergence, verification, pocklington, hallen, integral-equation, delta-gap, reduced-kernel]
prerequisites: [antenna-fundamentals.md, dipoles-and-monopoles.md, ../00-math-foundations/numerical-methods-overview.md]
related: [../16-simulation-tools/nec-antenna-modelling.md, ../16-simulation-tools/openems-workflow.md, ../16-simulation-tools/em-solvers-fdtd-mom-fem.md, ../16-simulation-tools/simulation-validation.md, ../16-simulation-tools/installing-tools-macos.md, patch-antennas.md, pcb-and-chip-antennas.md, yagi-uda-and-log-periodic.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Antenna simulation: NEC (method of moments) and openEMS (FDTD)

## Questions this page answers
- Which tool should I use for a Yagi, a whip, a patch, a PCB antenna, or an antenna inside a nose cone?
- How does NEC work, and what are its segmentation rules?
- What can NEC-2 not model (dielectrics, PCBs, stepped-diameter elements)?
- What is the average gain test and why should I always check it?
- How do I set up a patch or PCB antenna in openEMS (mesh, ports, boundaries, NF2FF)?
- How do I know my simulation is right (convergence, cross-checks)?
- What do 4nec2, xnec2c, NEC2++/PyNEC, MMANA-GAL and EZNEC differ in?
- Why does my 433 MHz antenna resonate at a completely different frequency (e.g. 1.4 GHz) in simulation?
- What are Pocklington's and Hallén's equations, and how do they become a MoM matrix?
- Why does the dipole current come out as a sine wave, and when does that fail?
- Why do short-dipole impedances change when I use very short segments?

## TL;DR
- **Wire antennas (dipoles, monopoles with radials, Yagis, LPDAs, helices, loops, quads) in free space or over ground → NEC-2/NEC-4 (MoM).** Fast, accurate when the segmentation rules are obeyed. Free front-ends: 4nec2 (Windows), xnec2c (Linux/macOS), NEC2++/PyNEC (library/Python), EZNEC (freeware in recent versions — check), MMANA-GAL (MININEC engine).
- **Anything with dielectric substrate, PCB traces, ceramic, finite ground boards, radomes, enclosures → full-wave FDTD/FEM/3-D MoM.** Free: **openEMS** (EC-FDTD, Python/Octave, near-to-far-field). Commercial: CST, HFSS, FEKO, Sonnet (planar MoM; Lite version free).
- **NEC-2 rules** (manual Part III [1]): segment length Δ < λ/10 (≤ λ/20 in critical regions), Δ > 10⁻³λ; Δ/a > 8 for < 1 % error with the thin-wire kernel (≥ 2 minimum), extended kernel allows Δ/a ≥ 2; 2πa/λ ≪ 1; connected wires share exact end points; ≤ 30 wires per junction; sources need parallel, equal neighbouring segments; patches ≥ 25 per λ², ≤ 0.04λ² each, closed surfaces only.
- **Known NEC-2 weaknesses**: stepped/tapered-diameter elements (telescoping Yagi tubes — use NEC-4, EZNEC's Leeson correction, or constant diameter), acute-angle junctions and close wires of different radii, very short segments/tiny loops, wires in/at lossy ground (buried radials: NEC-4), no dielectric substrates (flat strips and PCB antennas need other solvers; Cebik [3]).
- **Always check**: (1) segmentation convergence (double the segments; Z_in and gain should change by ≲ 1 %/0.1 dB), (2) the **average gain test** (lossless free-space model → average gain 1.00, i.e. 0 dB; our scripts report P_rad/P_in = 1.000), (3) a cross-check against a known result (resonant thin dipole ≈ 72 Ω at ≈ 0.47–0.49λ; λ/4 monopole on PEC ≈ 36 Ω, 5.2 dBi).
- **openEMS essentials**: mesh ≤ λ/15–λ/20 in the highest-εr material at the highest frequency, "thirds rule" refinement at metal edges, ≥ 3–4 cells through thin substrates; MUR or PML boundaries ≥ λ/4 from the structure (at the lowest frequency); lumped or MSL port; NF2FF box inside the boundary; Gaussian excitation spanning the band; end criterion ≈ −40 to −50 dB energy decay.
- **Integral equations**: NEC and the KB MoM solve **Pocklington's equation** (the electric field on the wire is zero) in weak, mixed-potential form. **Hallén's equation** is the same physics with the 1-D Helmholtz operator inverted analytically. Its zeroth-order solution is the sinusoidal current I₀ sin k(h − |z|). A direct Hallén solver (`s12_mutual_hallen.py`) agrees with the KB Galerkin MoM within 0.6 Ω for a thin λ/2 dipole (Richardson limit 80.5 + j45.8 Ω vs 80.3 + j45.3; NEC 80.0 + j45.5). The resonance is 0.482λ at 72.0 Ω.
- This repository contains an independent thin-wire MoM (`tools/verify/ant_mom_wire.py` for parallel wires, `ant_mom_general.py` for arbitrary wire structures with junctions, loads and PEC ground) used to verify the numbers on these pages.

## Intuition (no math)
**Method of moments (NEC).** Chop each wire into short segments and ask: "what currents on these segments make the total tangential electric field on every wire surface zero (perfect conductor), given the source voltage?" Each segment's current produces a field at every other segment (a known Green's function); that gives a matrix equation Z·I = V. Solve it and you have the currents; the pattern, impedance and gain follow directly. It is efficient because only the wires (1-D) are discretised, but it only knows about wires (and simple closed patches) in free space or over an idealised ground.

**FDTD (openEMS).** Fill a box of space with a 3-D grid, put the electric and magnetic fields on staggered grid points (Yee cell), and step Maxwell's equations forward in time from a short pulse. Materials (dielectrics, metals, lossy media) are just properties of grid cells, so substrates, enclosures and nose cones are easy. Boundaries absorb outgoing waves (MUR/PML). One run gives a whole frequency band via Fourier transform; the far field comes from a near-to-far-field transform on a closed box around the antenna. The cost is memory and time: the grid must resolve the smallest features and the shortest wavelength.

## The math

### Level 1 — the MoM matrix
With N basis functions f_n (current shapes on segments), unknown amplitudes I_n, and testing functions w_m:
$$\sum_n Z_{mn}I_n=V_m,\qquad Z_{mn}=-\langle w_m,\mathbf E(f_n)\rangle,\qquad V_m=\langle w_m,\mathbf E^\text{inc}\rangle .$$
NEC-2 uses a three-term (constant + sine + cosine) current expansion per segment with point matching at segment centres, the thin-wire (reduced) kernel or an extended kernel, and a delta-gap/"applied-field" source [1]. Our verification MoM uses Galerkin testing with triangle basis functions and the mixed-potential form (see the script headers) — a different discretisation, which makes agreement between the two a meaningful check.

Radiated fields: once I is known, E_far ∝ Σ I_n ∫ f_n e^{jk r̂·r′} dl′; directivity follows by integrating |E|² over the sphere; the input impedance is V/I at the source.

### Level 1½ — MoM as simultaneous equations, algebra only
- **Unknowns.** Cut the wire into N segments and give each an unknown current $I_n$. The equation for segment m says that the field from all N currents, added up at segment m, must cancel the source voltage there and be zero everywhere else on the metal: $Z_{m1}I_1 + Z_{m2}I_2 + \dots + Z_{mN}I_N = V_m$.
- **The matrix.** $Z_{mn}$ is "the voltage induced on segment m per ampere on segment n". It is a mutual impedance and depends only on geometry and frequency. N segments give N equations in N unknowns, the same algebra as a nodal circuit analysis.
- **Answers.** Solve once to get every $I_n$. The input impedance is $V_{feed}/I_{feed}$, and the pattern is the sum of the segments' fields. Nothing else is needed.
- **Cost.** The matrix has N² entries and a direct solve takes about N³ operations. Doubling the segments therefore costs 4× the memory and 8× the time, which is why the segmentation rules (≤ λ/10, Δ/a > 8) aim for "enough", not "as many as possible".

*Worked numbers (verified, `tools/verify/s18_level15_numbers.py`).* A 433 MHz half-wave dipole about 330 mm long, in 2 mm wire, cut into 21 segments:
- **Segments:** each is 15.7 mm (≈ λ/44), and Δ/a = 15.7 for a 1 mm radius, so both rules are met.
- **Matrix:** it has 21² = 441 complex entries, which solves in microseconds.
- **Convergence check:** doubling to 41 segments (the check in "Always check") costs about 8× the time, still trivial.

### Level 2 — why the segmentation rules exist
- **Δ < λ/10**: the current must be well sampled along the wire (its variation is sinusoidal with period λ); in NEC-2's basis each segment represents a smooth current, and λ/10 keeps interpolation error small; λ/20 near feeds, junctions and tips.
- **Δ/a > 8 (thin-wire kernel)**: the reduced kernel assumes the current is a filament on the axis and the field is matched on the surface (or vice versa); when a segment is short compared to the radius, the self-term approximation fails. The extended kernel adds the next term of the series expansion of the exact ring-current field, permitting Δ/a ≈ 2 [1].
- **Δ > 10⁻³λ**: in NEC-2's constant/sine/cosine basis, the three terms become numerically indistinguishable on very short segments (ill-conditioning) [1].
- **Junctions**: current continuity and charge conservation across a junction are enforced only if the segment end points coincide exactly (within 10⁻³ of the shortest segment); large radius steps or very unequal segment lengths at a junction degrade accuracy.
- **Ground**: the image method (perfect ground) and the Sommerfeld/Norton method (lossy ground, NEC-2 with SOMNEC) are accurate near ground; the reflection-coefficient approximation is only valid for structures several tenths of λ above ground [1].

### Level 3 — Pocklington and Hallén: the integral equations behind NEC and our MoM
**Set-up.** We use the $e^{j\omega t}$ convention and the Lorenz gauge. A z-directed wire of radius a and half-length h carries a total current I(z′); the thin-wire (reduced) kernel puts it on the axis and matches the field on the surface. Then
$$A_z(z)=\mu\int_{-h}^{h}I(z')\,G(z-z')\,dz',\qquad G=\frac{e^{-jkR}}{4\pi R},\quad R=\sqrt{(z-z')^2+a^2},$$
and $\mathbf E=-j\omega\mathbf A-\nabla\Phi$ with $\nabla\cdot\mathbf A=-j\omega\mu\varepsilon\Phi$ gives the scattered axial field
$$E_z^{s}=\frac{1}{j\omega\mu\varepsilon}\Big(\frac{\partial^2}{\partial z^2}+k^2\Big)A_z .$$
On a perfect conductor the total tangential field vanishes, $E_z^s=-E_z^{inc}$.

**Pocklington's equation.** Moving the operator inside the integral gives
$$\int_{-h}^{h}I(z')\Big(\frac{\partial^2}{\partial z^2}+k^2\Big)G(z-z')\,dz'=-j\omega\varepsilon\,E_z^{inc}(z).$$
The kernel $\partial^2G/\partial z^2$ is hyper-singular as $a\to0$. Galerkin MoM avoids it. Write $E_z^s=-j\omega A_z-\partial\Phi/\partial z$ with the charge $q=-(1/j\omega)\,dI/dz$ (continuity). Then test with the same triangle functions $f_m$ used as basis and integrate the $\partial/\partial z$ by parts onto the testing function:
$$Z_{mn}=j\omega\mu\langle f_m,G*f_n\rangle+\frac{1}{j\omega\varepsilon}\langle f_m',G*f_n'\rangle ,$$
which is exactly the matrix in `tools/verify/ant_mom_wire.py` and `ant_mom_general.py` (Level 1 above). Only 1/R singularities remain, and they are integrated analytically. NEC-2 point-matches the same equation with a three-term sinusoidal basis [1], [2], [6].

**Hallén's equation.** Write $\psi=A_z/\mu=\int I\,G\,dz'$. Pocklington says $(d^2/dz^2+k^2)\psi=-j\omega\varepsilon E_z^{inc}$, an ordinary differential equation in z that can be solved exactly. For a delta-gap source $E_z^{inc}=V\delta(z)$ (V drives current in +z, so $Z_\text{in}=V/I(0)$), use $(d^2/dz^2+k^2)\sin k|z|=2k\,\delta(z)$ and $\omega\varepsilon/k=1/\eta$. The even (symmetric-feed) solution is
$$\int_{-h}^{h}I(z')\frac{e^{-jkR}}{4\pi R}\,dz'=C_1\cos kz-\frac{jV}{2\eta}\sin k|z| ,$$
with the constant $C_1$ fixed by $I(\pm h)=0$. The kernel is now only weakly singular, which is why classical theory (King, Balanis ch. 8) prefers Hallén.

**Zeroth order: where the sine current comes from.** For a thin wire the kernel is sharply peaked, so $\int I\,G\,dz'\approx I(z)\,\Omega/4\pi$ with $\Omega=2\ln(2h/a)$. Then $I(z)\propto C_1\cos kz-(jV/2\eta)\sin k|z|$, and $I(h)=0$ forces $I(z)=I_0\sin k(h-|z|)$, the induced-EMF current of [dipoles](dipoles-and-monopoles.md#level-2--derivations). At this order the input impedance is purely reactive, $Z_0=-j(\eta/\pi)\ln(2h/a)\cot kh$. Radiation resistance appears only at the next order in $1/\Omega$ (King–Middleton), which is why the induced-EMF method gets R from the far-field power instead.

**Verification** (`tools/verify/s12_mutual_hallen.py`, all PASS). The script solves Hallén directly: pulse basis, point matching at the segment centres plus the wire end, the 1/R part integrated analytically.
- **Thin λ/2 dipole (a = 10⁻⁴λ):** N = 201/401/801 pulses give 81.4 + j51.0, 80.9 + j48.3 and 80.7 + j47.1 Ω. The reactance converges only as ~1/N, so a pre-registered "N = 201 within 3 Ω" check failed. The Richardson limit, **80.5 + j45.8 Ω**, matches the Galerkin MoM (80.3 + j45.3) and NEC-2 (80.0 + j45.5). The Hallén resonance is 0.4817λ at 72.0 Ω (MoM 0.4838λ, 72.0 Ω).
- **The current** matches sin k(h − |z|) to within 0.05 of its peak.
- **Short dipoles (a = 10⁻³λ, segments ≈ 5a):** for L = 0.1λ, Hallén gives −992 Ω, the MoM −978 Ω and NEC −1059 Ω. The transmission-line formula −120[ln(L/2a) − 1]cot(kh) gives −1075 Ω (within 8 %). The zeroth-order Hallén value is −1700 Ω, about 70 % too high, so treat it only as a qualitative result.
- **Segments shorter than ≈ 2–3 radii:** all three solvers drift (Hallén −270 Ω at Δ = a/2). Two things fail together: the reduced kernel, and the delta-gap capacitance, which grows as the gap shrinks.

### Level 3 — FDTD fundamentals for openEMS users
- **Stability**: explicit time stepping needs the Courant limit Δt ≤ 1/(c√(1/Δx² + 1/Δy² + 1/Δz²)); openEMS computes it from the finest mesh cell — so one tiny cell slows the whole simulation.
- **Dispersion error**: numerical phase velocity error grows as (Δ/λ)²; λ/20 cells give sub-percent resonance error for patches, provided edges are resolved.
- **Metal edges** have singular fields; openEMS guidance places mesh lines at ⅓ inside and ⅔ outside of a metal edge ("thirds rule") to capture the edge correctly.
- **Loss**: specify dielectric loss via conductivity κ = 2πf₀ε₀εr tanδ at the design frequency (openEMS's kappa), so tanδ is correct near f₀ only; metal as PEC or with conductivity (sheet models for thin copper).
- **Ports**: a lumped port (resistance + source across a gap) for probe feeds and small antennas; an MSL port for microstrip lines (gives de-embedded S11 at a reference plane).
- **NF2FF**: equivalent currents on a closed box inside the absorbing boundary; the box must enclose the antenna (and its ground/board) and stay out of the PML.
- **End criterion**: stop when the field energy has decayed by 40–50 dB; high-Q antennas ring for a long time (GNSS ceramic patches, small loops) — too early a stop gives a smeared S11.

## Tool comparison

| Tool | Engine | Platform | Strengths | Limits |
|---|---|---|---|---|
| 4nec2 | NEC-2 (NEC-4 if licensed), free | Windows (Wine on macOS) | geometry editor, optimiser, sweeps, AGT | Windows-centric |
| xnec2c | NEC-2 in C, free | Linux/macOS (GTK) | fast, multi-threaded sweeps, live plots, reads NEC decks | NEC-2 limits |
| NEC2++ / PyNEC | NEC-2 C++ library with Python bindings | any | scripting, optimisation loops, CI | NEC-2 limits |
| EZNEC (v7, freeware — verify) | NEC-2/NEC-4 (Pro) | Windows | polished UI, Leeson correction for stepped elements | Windows |
| MMANA-GAL | MININEC | Windows | quick Yagi optimisation | MININEC ground and junction weaknesses |
| NEC-4.2 | NEC-4 (licensed, LLNL) | any | buried wires, better thin-wire/junction handling, insulated wires | licence |
| openEMS | EC-FDTD, free | Linux/macOS/Windows, Python/Octave | dielectrics, PCBs, radomes, arbitrary 3-D | slow for electrically large/high-Q; meshing skill |
| Sonnet Lite | planar MoM | Windows | accurate layered planar structures | size-limited free version; planar only |
| CST / HFSS / FEKO | FDTD/FIT, FEM, MoM | commercial | everything, including large platforms (FEKO MLFMM, PO) | cost |
| `tools/verify/ant_mom_*.py` | own Galerkin MoM | Python | independent cross-check, scripting | PEC wires only, free space/PEC ground |

Installation on macOS and detailed workflows: [installing tools on macOS](../16-simulation-tools/installing-tools-macos.md), [NEC modelling](../16-simulation-tools/nec-antenna-modelling.md), [openEMS workflow](../16-simulation-tools/openems-workflow.md).

## Design equations & rules of thumb

| Rule | Value |
|---|---|
| NEC segment length | λ/20–λ/10; > 10⁻³λ |
| NEC Δ/a | > 8 thin kernel (≥ 2 absolute min); ≥ 2 with EK (≥ 0.5 min) |
| Wire radius | 2πa/λ ≪ 1 |
| Junctions | coincident ends; ≤ 30 wires; avoid big radius/length steps |
| Helix | ≥ 12–16 segments per turn (our MoM: 12 → 24 changed axial gain by 0.3 dB) |
| Yagi elements | ≥ 21 segments per element; same segment length on all elements helps |
| Average gain test | 1.00 ± 0.05 (≈ ±0.2 dB) for lossless free-space models; ≈ 2 over perfect ground |
| openEMS mesh | ≤ λ_min/(15–20·√εr) in dielectric; ≥ 3–4 cells across substrate thickness; thirds rule at edges |
| openEMS boundary | ≥ λ_max/4 air margin; PML_8 or MUR |
| openEMS end criterion | 1e-4 to 1e-5 (−40 to −50 dB) |
| Cross-check | known analytic results; two different solvers; measurement |

## Worked examples

**Example 1 — NEC-2 deck for a 433 MHz dipole (2 mm wire).** From our MoM, resonance is at ≈ 328 mm. A minimal deck (card formats per NEC-2 Part III [1]; verify field order in your front-end):
```
CM 433 MHz dipole, 2 mm wire, free space
CE
GW 1 41 0 0 -0.164 0 0 0.164 0.001
GE 0
EX 0 1 21 0 1.0 0
FR 0 1 0 0 433.0 0
RP 0 181 1 1000 0 0 1 1
EN
```
GW: tag 1, 41 segments (Δ = 8.0 mm = λ/87; Δ/a = 8.0 — right at the thin-kernel limit, so either keep 41 or switch on the extended kernel with EK if you use more segments), end points in metres, radius 1 mm. EX 0: voltage source on segment 21 (the centre). Expected: Z ≈ 72 + j0 Ω near 433 MHz, peak gain ≈ 2.15 dBi, average gain 1.00. Doubling the segments to 81 requires EK (Δ/a = 4).

**Example 2 — Cross-checking our MoM against textbook values.** Our Galerkin MoM gives, for a thin dipole (a = 10⁻⁴λ), resonance at 0.4838λ with 72.0 Ω; for a λ/4 monopole on PEC 42.8 + j22.8 Ω at exactly λ/4 (a = 10⁻³λ) and 5.19 dBi; four horizontal λ/4 radials give 22.8 Ω; the energy check P_rad/P_in is 1.000 in all cases. These match NEC-reported values in the literature (≈ 72 Ω resonant dipole; ≈ 20–25 Ω flat-radial ground plane) — so the scripts can be trusted for the wire structures on these pages.

**Example 3 — A convergence study that caught a bug.** While building `ant_mom_wire.py`, the Yagi's P_rad/P_in came out 0.955 → 0.978 → 0.989 as the pattern grid was refined — first-order convergence, which should not happen for a smooth periodic integrand. The cause: the φ integral used a trapezoid rule on a periodic grid that omitted the wrap-around interval and half-weighted the φ = 0 column — exactly the main-beam direction. Replacing it with the periodic rectangle rule gave 1.0009 at every grid size, and the directivity dropped by 0.2 dB (14.40 → 14.20 dBi). Lesson: the average-gain/energy check is cheap and catches both model and post-processing errors.

**Example 4 — openEMS patch sketch (Python API; compare with the official "Simple Patch Antenna" tutorial [4]).** Units mm; 2.45 GHz FR-4 patch from [patch-antennas](patch-antennas.md#worked-examples):
1. `FDTD = openEMS(NrTS=30000, EndCriteria=1e-4)`; `FDTD.SetGaussExcite(2.45e9, 1.0e9)`; boundaries `['MUR']*6` (or `'PML_8'`).
2. `CSX = ContinuousStructure()`; add substrate box (εr = 4.4, kappa from tanδ at 2.45 GHz), ground and patch metal boxes (37.23 × 28.81 mm), priority so metal overrides dielectric.
3. Lumped port (50 Ω) from ground to patch at the probe position (x₀ from the cos² law as a starting point), oriented along z.
4. Mesh: fixed lines at all metal edges with thirds-rule refinement, ≤ λ/20 in the substrate (≈ 2.9 mm at 2.45 GHz in εr = 4.4) and ≥ 4 cells across 1.6 mm; smooth to ≤ λ/20 in air; boundary ≥ 31 mm (λ/4) away.
5. `nf2ff = FDTD.CreateNF2FFBox()`; run; compute S11 from the port, find f_res, then far field at f_res: directivity, and efficiency = P_rad/P_accepted.
6. Compare with the TL/cavity predictions (f within ~2 %, D ≈ 6 dBi, e_rad ≈ 40 %).

## Practical notes
- **Model what you build**: the feed line, connector launch, board outline, battery, nose cone — for small antennas these dominate.
- **Parameter sweeps and optimisers** (4nec2, xnec2c, Python loops) are powerful but will exploit model weaknesses (e.g. NEC-2 stepped-radius error); sanity-check optima.
- **Ground models**: rocket ground stations on tripods at 433 MHz are ≥ 2λ above ground — free-space models are adequate for gain; include Sommerfeld ground for low-angle patterns and for pad-level links.
- **Record** decks/scripts in version control with results (engineering ethos: pre-register the expected result, then run).

## Common mistakes & misconceptions
- **"NEC can model my PCB antenna if I use thin wires."** It cannot model the substrate's effect; results can be off by 10–30 % in frequency (Cebik [3]).
- **"More segments are always better."** Beyond the rules (Δ/a < 2 thin kernel, Δ < 10⁻³λ), accuracy *decreases*. Our Hallén/MoM/NEC study shows a 0.1λ dipole's reactance moving from ≈ −1000 Ω to −270…−720 Ω once segments are shorter than the radius (reduced kernel plus delta-gap capacitance).
- **"The sinusoidal current is exact."** It is the zeroth-order (Ω → ∞) Hallén solution. It gives no resistance at all at that order, and finite thickness shifts resonance to 0.47–0.49λ.
- **"The optimiser found 18 dBi on a 1λ boom."** Check AGT and convergence; super-gain solutions are usually numerical artefacts or impractically narrowband.
- **"FDTD results are exact."** Mesh, boundaries, end criterion and port definitions all introduce errors; do a mesh-refinement run.
- **"The simulated pattern is what I will measure."** Only if the cable, mast and surroundings are modelled — or suppressed in the measurement (chokes, range design).

- **"The simulator says my 433 MHz antenna resonates at 1.4 GHz."** (D2 #19) Usual causes, in order: (1) **no ground/counterpoise in the model** — a λ/4 monopole simulated without its ground behaves as a short dipole whose own first resonance is near 2× (and 6× for the next) the intended frequency; (2) **wrong port location or port across the wrong gap** (a port in series with a shorted stub, or across an IFA's short); (3) **units** (mm vs inch vs m: a 25.4× scale error); (4) reading a **higher-order resonance** (3λ/4 at ≈ 3f, λ at 2f for an end-fed) because the sweep did not include the fundamental; (5) a **mesh that misses the thin wire or gap** (FDTD) or segments longer than λ/10 at the top of the sweep (NEC); (6) a **ground plane resonance** of a finite board. Always sweep from ≈ f/3 to 3f first, plot R and X (not just S11), and sanity-check against the hand formula (λ/4 = 173 mm at 433 MHz).

## How to simulate / verify
- `tools/verify/s12_mutual_hallen.py` (≈ 1 min): direct Hallén solver vs Galerkin MoM vs NEC-2; zeroth-order check; induced-EMF mutual impedance (closed form, numeric near-field integral, NEC and MoM two-ports).
- Our scripts: `tools/verify/ant_mom_wire.py` (dipole resonance vs thickness; λ/2 impedance), `tools/verify/ant_mom_general.py` (monopoles, radials, folded dipole, loops, helices), `tools/verify/ant_yagi.py` (Yagi/LPDA). Each prints the energy check.
- Cross-code checks: run the same dipole/Yagi in xnec2c or 4nec2 and compare Z_in and gain (expect agreement within ~1–2 Ω and ~0.1–0.2 dB when both follow the rules).
- For openEMS models: halve the mesh size once; the resonance should move < 0.5 %.

## Open questions / gaps
- EZNEC's current licence status (freeware since v7?) should be confirmed by domain 16.
- A side-by-side NEC-2 vs our MoM table for the DL6WU Yagis would strengthen confidence further (requires installing xnec2c/PyNEC — W3-C2).
- The "equal-area" wire-grid radius rule for modelling surfaces says the wire surface area parallel to one polarisation equals the surface it replaces, i.e. wire circumference 2πa = grid spacing. It was checked by W5-S18 (2026-10-13) through later papers that discuss Ludwig (1987), not Ludwig's paper itself. Ludwig's infinite-cylinder study supports it as a rule of thumb, not a proof. Paknys (1991) found it the most accurate choice for that problem. Later work (EPFL, Rubinstein et al. 2005) finds it good for rectangular grids but weaker for triangular meshes, and one GPR study preferred radii 10–15 % smaller. Treat it as a starting point and run a radius convergence check.

## Sources
1. G. J. Burke and A. J. Poggio, *Numerical Electromagnetics Code (NEC) — Method of Moments*, Lawrence Livermore National Laboratory, 1981; Part III User's Guide, Section II "Structure Modeling Guidelines" (segment and radius rules, junctions, ground methods, patches, limitations). https://www.nec2.org/part_3/secii.html (manual)
2. C. A. Balanis, *Antenna Theory*, 4th ed., 2016 — ch. 8 (integral equations, MoM, Pocklington/Hallén), ch. 12 (FDTD overview in later editions); A. Taflove and S. C. Hagness, *Computational Electrodynamics: The FDTD Method*, 3rd ed., Artech House, 2005 — Courant limit, dispersion, PML. (textbooks)
3. L. B. Cebik (W4RNL), "When not to use NEC" (amod128) and "Within the lines: NEC-2" — non-round/flat elements, PCB antennas, IS/UM cards, NEC-2 practice. https://antenna2.github.io/cebik/content/amod/amod128.html (expert articles)
4. openEMS documentation: "Simple Patch Antenna" tutorial (Python/MATLAB), NF2FF, mesh guidance (thirds rule). https://docs.openems.de/python/openEMS/Tutorials/Simple_Patch_Antenna.html ; https://wiki.openems.de/index.php/NF2FF.html (tool documentation)
5. R. F. Harrington, *Field Computation by Moment Methods*, Macmillan, 1968; W. C. Gibson, *The Method of Moments in Electromagnetics*, 2nd ed., CRC, 2014 — Galerkin MoM, basis functions, thin-wire kernels (used for our verification MoM). (textbooks)
6. S. J. Orfanidis, *Electromagnetic Waves and Antennas*, 2016 ed., ch. 24 "Currents on Linear Antennas" (Hallén and Pocklington integral equations, §24.8–24.12 MoM incl. NEC sinusoidal basis, MATLAB codes). [chapter numbers checked against the 2016 edition's table of contents, W5-S18 2026-10-13; the 2010 edition numbers ch. 11–18 one lower, with Aperture Antennas as ch. 18 and Currents on Linear Antennas as ch. 21]. https://eceweb1.rutgers.edu/~orfanidi/ewa/ (textbook)
7. This repository: `tools/verify/ant_mom_wire.py`, `ant_mom_general.py`, `ant_yagi.py`, `s12_mutual_hallen.py`. (verification)
8. R. W. P. King, *The Theory of Linear Antennas*, Harvard, 1956; E. Hallén, "Theoretical investigations into the transmitting and receiving qualities of antennae," *Nova Acta Regiae Soc. Sci. Upsaliensis* 11, 1938; H. C. Pocklington, "Electrical oscillations in wires," *Proc. Cambridge Phil. Soc.* 9, 1897 — the integral equations and the Ω expansion. (textbook / historical; cited via Balanis ch. 8 and Orfanidis ch. 24)
