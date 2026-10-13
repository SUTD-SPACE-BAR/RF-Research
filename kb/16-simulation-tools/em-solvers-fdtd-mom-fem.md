---
title: EM solvers compared — FDTD, FIT, MoM, FEM and 2.5-D planar methods; openEMS, MEEP, gprMax, Elmer, Palace, OpenParEM, Sonnet, HFSS, CST, FEKO, EMPro; accuracy pitfalls
domain: 16-simulation-tools
slug: em-solvers-fdtd-mom-fem
tags: [fdtd, fit, mom, fem, bem, planar-mom, 2.5d, yee, courant, efie, rwg, nedelec, weak-form, adaptive-mesh, pml, wave-port, openems, meep, gprmax, elmer, palace, openparem, sonnet, hfss, cst, feko, empro, student-edition]
prerequisites: [../02-electromagnetics/maxwells-equations.md, ../00-math-foundations/numerical-methods-overview.md, ../02-electromagnetics/quasi-static-vs-full-wave.md]
related: [openems-workflow.md, nec-antenna-modelling.md, tool-landscape-overview.md, simulation-validation.md, rf-circuit-simulators-harmonic-balance.md, ../08-antennas/antenna-simulation-nec-openems.md]
level: mixed
confidence: medium
last_updated: 2026-10-14
---

# EM solvers compared: FDTD, FIT, MoM, FEM and planar methods

## Questions this page answers
- What is the difference between FDTD, FEM and the method of moments, and which should I use for a PCB antenna, a filter, a connector launch or a nose-cone radome?
- What does "2.5-D planar" (Sonnet, Momentum, AXIEM) mean?
- Which free solvers exist (openEMS, MEEP, gprMax, Elmer, Palace, OpenParEM) and what do the commercial ones (HFSS, CST, FEKO, EMPro) add?
- What do the free student editions limit (mesh size, platform)?
- Why do two solvers disagree on my antenna, and which pitfalls (mesh, ports, boundaries, convergence) cause most errors?
- How big a model can I afford — cells, unknowns, run time?

## TL;DR
| Method | Discretises | Natural problems | Cost scaling | Free tools | Commercial |
|---|---|---|---|---|---|
| **FDTD / FIT** (time domain, volume grid) | whole volume, hexahedral cells | broadband antennas, PCB structures, radomes, pulses, nonlinear/dispersive media | memory ∝ N cells, time ∝ N·steps | openEMS, MEEP, gprMax | CST (FIT), EMPro FDTD, XFdtd |
| **FEM** (frequency domain, volume) | whole volume, tetrahedra (edge elements) | resonant/closed structures, filters, connectors, waveguides, fine geometry | sparse solve per frequency; memory ≫ FDTD per unknown | Elmer, Palace, OpenParEM | HFSS, CST FD, COMSOL RF, EMPro FEM |
| **MoM / BEM** (frequency domain, surfaces or wires) | conductor surfaces/wires only | wire antennas, large metallic bodies, arrays in free space | dense N×N; direct O(N³), MLFMM O(N log N) | NEC-2/PyNEC, (openEMS has none) | FEKO, NEC-4, CST IE, HFSS-IE |
| **2.5-D planar MoM** | metal on layered stack-ups | PCB/MMIC filters, couplers, planar antennas, vias | dense but only on metal | Sonnet Lite (limited, Windows) | Sonnet, Keysight Momentum, Cadence AXIEM |
| **2-D quasi-static** | line cross-section | Z0, εeff, coupling of lines | trivial | `tline_fd2d.py`, OpenParEM2D | Polar Si9000, HFSS 2D Extractor |
- **Rule of choice**: wires in free space → MoM (NEC); planar PCB circuits → 2.5-D MoM or FDTD; antennas with dielectrics/enclosures → FDTD or FEM; high-Q closed resonators and connectors → FEM; electrically huge metal platforms → MoM+MLFMM or asymptotic (PO/SBR).
- **Free, tested here**: openEMS (FDTD; microstrip Z0 within 0.3 % of two independent methods; patch converged to 0.08 %), PyNEC (MoM; within 0.1 dB of our own MoM on a Yagi). Others described from documentation.
- **Student editions**: HFSS Student: 64 000 3-D volume elements, 8 000 surface, 2 000 2-D triangles, 4 cores, **Windows only** [8]; CST Student: mesh-cell limited, Windows (limits vary by version — unverified); Feko student edition "no-limits" since 2023.1 (single-sourced) ; AWR (6-month, Windows) and Keysight ADS (via a University Program agreement) for 2.5-D planar.
- **Most solver disagreements are set-up differences** — port definition and de-embedding, mesh at metal edges, boundary distance, loss models — not algorithm errors. Do a convergence study in *every* solver and compare de-embedded quantities at the same reference plane.

## Intuition (no math)
- **FDTD** is "let the waves happen": grid all of space, step Maxwell's equations forward in time from a pulse, watch the energy leave through absorbing walls. It sees everything (dielectrics, lossy parts, gaps) but pays for every cubic millimetre of air.
- **MoM** is "only the metal matters": the fields anywhere are sums of fields from currents on the metal, via a known formula (Green's function). Solve for the currents that make the tangential field zero on the metal. No air to mesh — superb for wires and metal bodies in free space — but every piece of metal talks to every other piece, so the matrix is dense, and dielectrics need special Green's functions (layered media) or volume formulations.
- **FEM** is "a flexible net": tetrahedra follow any curved or tiny geometry, the matrix is sparse (each element only talks to neighbours), and adaptive refinement puts elements where the field changes fastest. It solves one frequency at a time and needs an artificial outer boundary (radiation boundary or PML) for open problems.
- **2.5-D planar** is MoM with the substrate built into the Green's function: you only mesh the copper shapes on each layer (plus vias). Perfect for PCB filters and couplers; it cannot model finite dielectric blocks, radomes or connectors bodies.

## The math

### Level 1 — the four equations
- **FDTD**: discretised curl equations $\partial_t\mathbf H = -\mu^{-1}\nabla\times\mathbf E$, $\partial_t\mathbf E = \varepsilon^{-1}(\nabla\times\mathbf H - \sigma\mathbf E)$ on a staggered Yee grid; stable if $\Delta t \le 1/(c\sqrt{\Delta x^{-2}+\Delta y^{-2}+\Delta z^{-2}})$ (details: [openEMS workflow](openems-workflow.md#the-math)) [1].
- **MoM**: for currents $\mathbf J = \sum_n I_n\mathbf f_n$ on the conductors, enforce $\hat n\times(\mathbf E^{inc} + \mathbf E^{scat}[\mathbf J]) = 0$ weakly with testing functions $\mathbf w_m$: $\mathbf Z\mathbf I = \mathbf V$, $Z_{mn} = -\langle\mathbf w_m, \mathbf E^{scat}[\mathbf f_n]\rangle$, $V_m = \langle \mathbf w_m, \mathbf E^{inc}\rangle$ [2]. Wires: NEC's sinusoidal basis ([NEC page](nec-antenna-modelling.md#the-math)); surfaces: Rao–Wilton–Glisson (RWG) triangle-pair basis.
- **FEM**: the vector Helmholtz equation $\nabla\times(\mu_r^{-1}\nabla\times\mathbf E) - k_0^2\varepsilon_r\mathbf E = -jk_0\eta_0\mathbf J$; weak form: find $\mathbf E$ in $H(\mathrm{curl})$ such that for all test functions $\mathbf W$
$$\int_V\left[\mu_r^{-1}(\nabla\times\mathbf W)\cdot(\nabla\times\mathbf E) - k_0^2\varepsilon_r\,\mathbf W\cdot\mathbf E\right]dV + \oint_S(\text{boundary/port terms}) = -jk_0\eta_0\int_V\mathbf W\cdot\mathbf J\,dV$$
discretised with Nédélec (edge) elements, whose degrees of freedom are tangential field components along tetrahedron edges — this enforces tangential continuity and avoids spurious modes that node-based elements produce [3].
- **2.5-D planar MoM**: same as MoM with the layered-medium (Sommerfeld-integral) Green's function; Sonnet encloses the circuit in a shielded box so the Green's function is a fast-converging mode sum evaluated with FFTs [5].
  Derivations (Green's functions, EFIE/MFIE, Pocklington/Hallén, Sommerfeld integrals): [Green's functions](../02-electromagnetics/greens-functions-and-integral-equations.md).

### Level 1½ — FDTD as "update E from the curl of H", algebra only
- **Two interleaved grids.** Store E at whole steps and H half a step later, and half a cell apart in space. Each update is one line of arithmetic: the new H at a point is the old H minus (Δt/μ) times the difference of the two neighbouring E values divided by Δz. The new E is the old E minus (Δt/ε) times the difference of the two neighbouring H values divided by Δz. Repeat. No matrix is ever solved.
- **The speed limit (Courant).** In one step a wave must not cross more than one cell, so Δt ≤ Δz/c in 1-D, and Δt ≤ Δ/(c√3) for cubic cells in 3-D. The ratio S = cΔt/Δz is the Courant number. Above 1 the arithmetic blows up; just below 1 the 1-D scheme is almost exact.
- **Cells per wavelength.** Use about 20 cells per wavelength **in the material**: λ = c/(f√εr), cell ≈ λ/20. The number of cells scales as (size/cell)³ and the number of steps as (run time)/Δt, so halving the cell costs 16× (8× cells, 2× steps).
- **One run covers the band.** A short pulse in, the ringing recorded, and one Fourier transform at the end give the response at every frequency in the pulse's band.

*Worked numbers (verified, `tools/verify/sim2_level15_numbers.py`).* At 2.45 GHz in FR-4 (εr 4.4), λ = 58.3 mm, so the cell is ≈ 2.9 mm. With 1 mm cells, Δt ≤ 3.34 ps in 1-D and ≤ 1.93 ps in 3-D: **212 steps per 2.45 GHz period**. A 100 × 100 × 20 mm box of 1 mm cells is 200 000 cells. A 1-D leapfrog run at S = 0.99 moves a Gaussian pulse at **v/c = 1.0000** without splitting it.

### Level 2 — cost and accuracy scaling
| | Unknowns for a structure of size $L$ at wavelength λ | Memory | Time | Error vs mesh size $h$ |
|---|---|---|---|---|
| FDTD | $N \sim (L/h)^3$, $h \approx \lambda/20$ or smaller features | $\propto N$ | $\propto N \cdot N_t$, $N_t \propto L/(c\Delta t)$ × ringing | phase error $\propto (kh)^2$ |
| FEM (order p) | $N \sim (L/h)^3$ with adaptive local refinement | sparse, $\propto N$ (direct solvers more) | per frequency | $\propto h^{p}$ (field), faster for S-params |
| MoM (surfaces) | $N \sim (L/h)^2$ | $\propto N^2$ | $N^3$ direct, $N\log N$ MLFMM | depends on basis; ~λ/10 mesh |
| MoM (wires) | $N \sim L/\Delta$ | $N^2$ | trivial below ~10⁴ unknowns | segment rules (NEC) |

### Level 3 — boundaries, ports and convergence, formally
- **Open boundaries**: FDTD uses Mur (1st-order one-way wave equation) or PML (a lossy, reflectionless-at-all-angles layer, Bérenger/CPML); FEM uses first-order absorbing boundaries (reflection grows at oblique incidence; need λ/4 air) or PML; MoM needs none (the Green's function radiates).
- **Ports**: a *lumped/gap port* imposes a voltage across a small gap (introduces a gap capacitance and assumes a quasi-static feed); a *wave port* solves the 2-D eigenmode of the feed line's cross-section and launches that mode — giving de-embeddable S-parameters referred to a known $Z_0$ (power-wave or line impedance definitions differ by a few percent for quasi-TEM lines). FDTD's MSL port extracts β and Z from V/I probes ([openEMS](openems-workflow.md#level-3--ec-fdtd-ports-nf2ff)).
- **Convergence**: FEM codes refine adaptively until $\max_{ij}|S_{ij}^{(k)} - S_{ij}^{(k-1)}| < \Delta S$ (e.g. 0.02) at the adaptation frequency; FDTD stops on field-energy decay; MoM converges with segment/triangle density. None of these guarantees accuracy at *other* frequencies or of *far-field* quantities — check those separately.

## Design equations & rules of thumb

| Problem (Marcus's use cases) | First choice | Why |
|---|---|---|
| 433/915 MHz dipole, Yagi, whip, radials | NEC-2 (PyNEC) | wires in free space; seconds per run |
| Monopole on a metal airframe | NEC-2 (thick wire / wire grid) | metal only |
| Antenna inside a fibreglass nose cone | openEMS (FDTD) | dielectric shell, broadband |
| PCB IFA/meander/chip antenna + ground plane | openEMS; commercial FEM/FIT | substrate, finite board |
| 2.45 GHz / GNSS patch | openEMS; Sonnet (if planar only, infinite substrate) | Run 2 on the openEMS page |
| Microstrip filter, coupler, stub | 2.5-D MoM (Sonnet Lite) or openEMS; SPICE/skrf for ideal lines | planar |
| SMA edge launch, via transitions | FEM (HFSS) or openEMS with fine mesh | 3-D, small features |
| Line impedance | 2-D quasi-static solver | exact enough, seconds |
| Whole rocket RCS at X-band | MoM+MLFMM or PO (commercial) | electrically huge |

| Pitfall | Symptom | Fix |
|---|---|---|
| Coarse mesh at metal edges | resonance several % off; changes with mesh | thirds rule / adaptive refinement; convergence study |
| Boundary too close | pattern ripple, wrong efficiency | ≥ λ/4 air; PML |
| Lumped port on a long feed | wrong Z_in, spurious resonances | wave/MSL port, or de-embed the feed |
| Skin depth vs mesh | copper loss wrong | use surface-impedance (thin-sheet) models; don't mesh through copper |
| Dielectric dispersion ignored | Q and frequency off at 5–24 GHz | Djordjevic–Sarkar model |
| Stopping criteria too loose | smeared, too-wide bandwidth | FDTD −50 dB for high Q; FEM ΔS ≤ 0.01 |
| Symmetry plane wrong (PEC vs PMC) | missing mode / wrong feed | check field symmetry of the excitation |

## Worked examples

### 1 — how big is the model? (own estimates)
- **NEC Yagi** (11 elements × 21 segments): N = 231 unknowns → a 231 × 231 complex matrix (0.85 MB), LU in milliseconds. Our cross-check sweep over 4 meshes and 3 cases took 13 s.
- **openEMS 2.45 GHz patch**: 127 k to 1.16 M cells; 8 s to 54 s on an M-series Mac (≈ 130 MCells/s). Memory ≈ 6 field components × 4 bytes + material coefficients ≈ 50–100 bytes/cell → ≈ 0.1 GB at 1 M cells.
- **openEMS 915 MHz PCB antenna** with 0.2 mm features on an 80 × 40 mm board in a λ/4 (82 mm) air box: graded mesh from 0.1 mm near copper to 16 mm (λ/20) in air, roughly 150 × 120 × 90 ≈ 1.6 M cells; Courant step set by the 0.1 mm cells ≈ 0.2 ps → one 915 MHz period ≈ 5 700 steps; with 30–60 periods of ringing ≈ 2–3 × 10⁵ steps ≈ 1–1.5 h at 100 MCells/s. The smallest cell, not the air box, dominates run time.
- **FEM student limit**: HFSS Student's 64 000 tetrahedra correspond to a mean edge of ≈ 6 mm (22 mm³ per element) in a (142 mm)² × 70 mm air box (volume of a regular tetrahedron $a^3/(6\sqrt2)$) — enough for a simple patch if adaptive refinement spends elements near the edges, marginal for a meandered PCB antenna with 0.2 mm features.

### 2 — two solvers, one line: what agreement to expect
From this KB: microstrip W 2.80 / h 1.51 mm / εr 4.5: 2-D FD 50.38 Ω, openEMS 50.31 Ω, Hammerstad–Jensen 50.44 Ω; a spread of 0.26 % between three methods with completely different discretisations (quasi-static finite volume, 3-D EC-FDTD with a port extraction, closed-form fit). For a patch antenna, expect 1–2 % frequency spread between competent set-ups in different solvers and ~0.5 dB in gain — larger differences mean a set-up difference to find.

### 3 — the MoM vs FDTD run-time trade for a 433 MHz dipole
MoM: 41 unknowns, milliseconds. FDTD: the dipole's 1 mm radius must be resolved (≈ 0.25 mm cells near the wire) inside a λ/4 = 173 mm air margin — ~10⁶ cells and ~10⁵ steps, tens of seconds to minutes. Use FDTD for wires only when a dielectric or enclosure forces you to.

## Practical notes
- **openEMS** (EC-FDTD, GPL, Python/Octave, Cartesian and cylindrical grids): the workhorse free 3-D solver in this KB — installed and validated ([workflow](openems-workflow.md)).
- **MEEP** (MIT, GPL-2.0, Python): FDTD with subpixel smoothing and strong photonics features; conda-forge `pymeep` 1.34 has osx-arm64 builds (not tested here). Its units are normalised (a, c = 1) — convert carefully for RF.
- **gprMax** (GPL-3.0): FDTD aimed at ground-penetrating radar and antennas in soil, dispersive media; Python + Cython/CUDA.
- **Elmer FEM** (CSC Finland, multiphysics; GPL/LGPL): includes a vector Helmholtz (edge element) solver for time-harmonic EM; meshing via Gmsh (already present in this Mac's Homebrew) — steeper learning curve for RF.
- **Palace** (AWS Labs, Apache-2.0; MFEM/libCEED): parallel 3-D FEM with eigenmode, driven frequency-domain, transient, electrostatic and magnetostatic solvers; lumped and wave ports; Spack install; aimed at superconducting-circuit and RF problems on laptops to HPC [6].
- **OpenParEM** (GPLv3): OpenParEM2D (port/line modes: Z0, γ, losses) and OpenParEM3D (S-parameters, antenna gain/directivity) with high-order elements and adaptive refinement, MPI parallel; version 2.1 (May 2025) [7].
- **Sonnet** (2.5-D, shielded box): Sonnet Lite is free (Windows) with a 64 MB memory limit [9] (two metal levels and ≤ 6 ports according to secondary listings — unverified); accurate for planar filters and couplers.
- **HFSS** (Ansys; adaptive FEM + integral equation + SBR+), **CST Studio** (FIT time domain, FEM frequency domain, IE, asymptotic), **FEKO** (MoM/MLFMM, PO/UTD, FEM, FDTD hybrids; strong for platforms and arrays), **EMPro** (Keysight; FEM + FDTD, ADS integration): all Windows/Linux, none native on macOS.

## Common mistakes & misconceptions
- **"FEM is more accurate than FDTD" (or vice versa).** Both converge to the same answer; accuracy is set by mesh, ports, boundaries and materials. Pick by problem type and cost.
- **Trusting a pretty 3-D pattern.** Check efficiency ≤ 1, the average-gain/energy balance, mesh convergence, and that the pattern is computed at the frequency you care about.
- **Comparing S-parameters at different reference planes** (one solver de-embedded to the patch edge, the other at the connector).
- **Meshing through copper thickness** for skin-effect loss at GHz — enormous meshes; use surface impedance.
- **Believing student-edition results that hit the mesh limit** — a model stopped short of convergence looks just as convincing.
- **Using NEC for a PCB antenna** (no substrate) or **FDTD for a 20 m HF wire antenna** (billions of cells).

## How to simulate / verify
- Cross-method checks already in the repository: `tools/verify/sim_nec_vs_mom.py` (NEC vs Galerkin MoM), `sim_openems_msl.py` (FDTD vs 2-D FD vs closed form), `sim_openems_patch.py` (FDTD vs TL/cavity model).
- For any new solver: start with a canonical benchmark whose answer is known — a λ/2 dipole (73 Ω, 2.15 dBi), a PEC sphere's RCS (Mie series), a WR-90 waveguide cutoff (6.557 GHz), a 50 Ω microstrip — before the real model ([simulation validation](simulation-validation.md)).

## Open questions / gaps
- Only openEMS and PyNEC were run; MEEP, Elmer, Palace, OpenParEM, gprMax and the commercial tools are described from documentation.
- CST Student Edition limits and current Feko student terms need confirmation from vendor pages (single-sourced / secondary).
- A shared benchmark (same patch in openEMS and one FEM code) would quantify cross-method spread on an antenna.

## Sources
1. A. Taflove and S. C. Hagness, *Computational Electrodynamics: The Finite-Difference Time-Domain Method*, 3rd ed., Artech House, 2005 — Yee algorithm, stability, dispersion, PML (J.-P. Bérenger, *J. Comput. Phys.* 114:185–200, 1994). (textbook / peer-reviewed)
2. R. F. Harrington, *Field Computation by Moment Methods*, Macmillan, 1968 (IEEE Press reprint 1993); S. M. Rao, D. R. Wilton, A. W. Glisson, "Electromagnetic scattering by surfaces of arbitrary shape," *IEEE Trans. Antennas Propag.*, 30(3):409–418, 1982. (textbook / peer-reviewed)
3. J.-M. Jin, *The Finite Element Method in Electromagnetics*, 3rd ed., Wiley-IEEE Press, 2014 — vector Helmholtz weak form, Nédélec edge elements, absorbing boundaries, ports. (textbook)
4. W. C. Gibson, *The Method of Moments in Electromagnetics*, 2nd ed., CRC Press, 2014 — basis/testing choices, MLFMM scaling. (textbook)
5. J. C. Rautio and R. F. Harrington, "An electromagnetic time-harmonic analysis of shielded microstrip circuits," *IEEE Trans. MTT*, 35(8):726–730, 1987 — basis of Sonnet. (peer-reviewed)
6. AWS Labs, *Palace* documentation, https://awslabs.github.io/palace/ ; github.com/awslabs/palace (Apache-2.0). (tool documentation)
7. OpenParEM project, https://openparem.org/ (GPLv3; 2D/3D FEM; v2.1 May 2025). (tool documentation)
8. Ansys Help, "HFSS Student Limitations" (v25.1): 64 000 3-D volume elements, 8 000 surface elements, 2 000 2-D triangles, HPC ≤ 4 cores, no Linux. (vendor documentation)
9. Sonnet Software, "Sonnet Lite Information" (help v18): memory limit 64 MB. (vendor documentation)
10. MEEP (github.com/NanoComp/meep, GPL-2.0; conda-forge pymeep 1.34 osx-arm64), gprMax (github.com/gprMax/gprMax, GPL-3.0), Elmer FEM (github.com/ElmerCSC/elmerfem) — repository metadata checked 2026-09-29. (tool documentation)
