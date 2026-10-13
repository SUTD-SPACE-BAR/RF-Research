---
title: openEMS workflow — installing on Apple Silicon, Python interface, meshing (λ/20, thirds rule), ports, boundaries, NF2FF, and two worked runs (microstrip line, 2.45 GHz patch)
domain: 16-simulation-tools
slug: openems-workflow
tags: [openems, nose-cone, rotpoly, stl, field-dump, paraview, slot, connector-pad, ifa, scan-blindness, broken-model, csxcad, fdtd, ec-fdtd, yee, courant, mesh, thirds-rule, pml, mur, lumped-port, msl-port, nf2ff, end-criteria, microstrip, patch-antenna, python, apple-silicon]
prerequisites: [em-solvers-fdtd-mom-fem.md, installing-tools-macos.md, ../08-antennas/antenna-simulation-nec-openems.md]
related: [../08-antennas/patch-antennas.md, ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md, simulation-validation.md, python-rf-toolkit.md, impedance-and-rf-calculators.md, ../08-antennas/pcb-and-chip-antennas.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# openEMS workflow

## Questions this page answers
- How do I install openEMS and its Python interface on an M-series Mac?
- What does an openEMS Python script consist of (geometry, materials, mesh, excitation, ports, boundaries, NF2FF)?
- How fine must the mesh be, what is the "thirds rule", and how many cells through a 1.6 mm substrate?
- Lumped port or microstrip (MSL) port — which, and how do I get S11, Z_in, Z0 and εeff out?
- How long should the simulation run (end criterion), and why do two identical runs stop at different time steps?
- Does openEMS actually give the right answer for a microstrip line and a patch antenna on FR-4?
- How do I get directivity, gain and radiation efficiency from the near-to-far-field (NF2FF) box?
- How much does a fibreglass nose cone detune my 433/915 MHz whip?
- How much does a slot in the ground plane under a trace, or a connector pad on thin prepreg, cost me?
- Can openEMS simulate a scanned phased-array unit cell (Floquet), and if not, how do I see scan blindness?
- How do I dump fields and animate them in ParaView, import STL or curved parts, and avoid tiny mesh cells?
- My simulated S11 has spikes, sits at 0 dB, or is nonsense — what did I set up wrong?

## TL;DR
- **Install** (tested, no sudo, ~25 min): `brew install cmake boost hdf5 cgal vtk qt5compat`, `git clone --recursive https://github.com/thliebig/openEMS-Project.git`, `./update_openEMS.sh ~/opt/openEMS --python`; run scripts with `~/opt/openEMS/venv/bin/python` ([installing](installing-tools-macos.md)). There is no PyPI/conda package and the old Homebrew formula is broken [1].
- **openEMS = EC-FDTD** (equivalent-circuit FDTD on a rectilinear, graded mesh; Cartesian or cylindrical) with CSXCAD for geometry; Python or Octave/MATLAB front ends; ParaView/AppCSXCAD for viewing [1], [2].
- **Mesh rules**: ≤ λ/20 of the *highest* frequency in the *densest* dielectric (λ/30–λ/50 for impedance accuracy), graded by ≤ 1.4–1.5× per cell; **thirds rule** at metal edges (lines ⅓ inside, ⅔ outside the edge); ≥ 4 cells through thin substrates. The Courant limit ties the time step to the *smallest* cell.
- **Boundaries** ≥ λ/4 (at the lowest frequency) from radiating structures; MUR (cheap) or PML_8 (better); PEC for a ground plane at the domain edge.
- **Run 1 — microstrip** (`tools/verify/sim_openems_msl.py`): W 2.80 mm, h 1.51 mm, εr 4.5, t = 0 → **Z0 = 50.31 Ω** at 1 GHz (λ/50 mesh, 231 k cells, 13 s) vs Hammerstad–Jensen 50.44 Ω (−0.27 %) and this KB's 2-D field solver 50.38 Ω (−0.15 %); εeff 3.40 (H-J 3.39); coarse→fine mesh changed Z0 by 0.6 %.
- **Run 2 — 2.45 GHz FR-4 patch** (`sim_openems_patch.py`, three meshes 127 k–1.16 M cells, 8–54 s): **f_res = 2.397 GHz** (−2.2 % vs the transmission-line-model design, converged to 0.08 %), Z_in 42 + j5 Ω, S11 −20 dB, BW(VSWR 2) 2.2 %, **D = 6.95 dBi, radiation efficiency 44.5 %, G = 3.44 dBi** (TL/cavity model: 6.1 dBi, 40 %, 2.1 dBi).
- **Run 3 — nose cone** (`sim2_openems_nosecone.py`, three meshes plus a boundary study). A 3 mm G10 ogive cone (εr 4.7) pulls a 915 MHz whip down **1.2 %** and a 433 MHz whip **2.8 %**. The shift agrees within 0.05 points across meshes and boundary types. A conductive av-bay under the bulkhead moves it **+3.4 %**: the counterpoise matters more than the cone.
- **Run 4 — PCB features** (`sim2_openems_pcb.py`). A ground slot under a 50 Ω line behaves as a series L with **Z_slot ≈ 70–94 Ω** and resonates where the slot's εeff is ≈ 2.1; a 60 mm slot costs 10 dB at L1. An SMA pad on JLC-7628 gives RL 11.4 dB at 2.45 GHz, and **21 dB** with L2 voided under it. An 88 mm printed IFA matches at 915 MHz (−11 dB, 4.9 % bandwidth); a fibreglass tube moves its best match by only +0.7 %. Its NF2FF gain is boundary-dependent and not trusted.
- **Practicalities** (`sim2_openems_broken.py`): field dumps and a ParaView recipe; `AddRotPoly` and STL import (STL faces lying on mesh lines detuned a whip by 11 %); sliver-free graded meshes; a deliberately broken model with a symptom table (a port on a PEC wall gives 0 dB; box modes give spikes; a port in the PML gives a −11 dB floor; a truncated ring-down gives a wrong bandwidth).
- **No Floquet/periodic boundary** exists in openEMS v0.37 (PEC, PMC, MUR, PML only). Scan blindness was therefore looked for in a finite 15-element row's embedded element pattern (Run 5). At 0.586λ on 1.6 mm FR-4 there is a shallow (2–3 dB), reproducible E-plane dip near 52°, against the 44° estimate; at λ/2 there is none.
- **Trap found**: openEMS checks the end criterion only at its ~4 s wall-clock progress reports unless `exact_endcriteria=True` is passed to `Run()`; identical runs then stop at different time steps (patch: 13 502 vs 16 555 steps, BW 2.25 vs 2.17 %). With the flag, runs are bit-reproducible (tested).

## Intuition (no math)
FDTD fills a box with a 3-D grid of little cells. Electric-field samples sit on cell edges, magnetic-field samples on cell faces, offset by half a cell (the Yee cell). Each time step, the E field is updated from the curl of H around it, then H from the curl of E — a direct discretisation of Faraday's and Ampère's laws. Launch a short Gaussian pulse from a port, let it ring through the structure and out into absorbing boundaries, record voltages and currents at the ports and tangential fields on a closed box, then Fourier-transform: one run gives the whole band.

Everything is a trade between cell size and run time. Cells must be small enough to resolve the shortest wavelength *and* the smallest geometric feature (a 0.2 mm CPWG gap, a 1.6 mm substrate). The time step must be small enough that a wave cannot skip a cell in one step (Courant). So one tiny cell anywhere slows the whole run — that is why openEMS uses non-uniform (graded) meshes and why meshing is the skill.

## The math

### Level 1 — Yee update and Courant limit
In 1-D (fields $E_x$, $H_y$, propagation along $z$), with half-step staggering:
$$H_y^{n+1/2}(k+\tfrac12) = H_y^{n-1/2}(k+\tfrac12) - \frac{\Delta t}{\mu\,\Delta z}\left[E_x^n(k+1)-E_x^n(k)\right]$$
$$E_x^{n+1}(k) = E_x^{n}(k) - \frac{\Delta t}{\varepsilon\,\Delta z}\left[H_y^{n+1/2}(k+\tfrac12)-H_y^{n+1/2}(k-\tfrac12)\right]$$
Stability in 3-D requires the Courant–Friedrichs–Lewy condition
$$\Delta t \le \frac{1}{c\sqrt{\Delta x^{-2}+\Delta y^{-2}+\Delta z^{-2}}}$$
— e.g. uniform 0.5 mm cells: Δt ≤ 0.96 ps; a 2.45 GHz period (408 ps) then takes ≥ 424 steps [3].

### Level 2 — numerical dispersion and why λ/20
The discrete wave travels slightly slower than $c$; for a well-resolved wave the phase-velocity error is of order $\frac{1}{24}(k\Delta)^2$ (1-D, at the Courant limit it vanishes along axes; in 3-D it is direction-dependent) [3]. With $\Delta = \lambda/20$, $k\Delta = 0.314$ → ≈ 0.4 % phase error, i.e. a resonator's frequency is a few tenths of a percent low; with λ/10 it is ≈ 1.6 %. Fields near metal edges vary like $r^{-1/2}$ (singular), so the local mesh must be much finer than λ/20 there — the thirds rule places the two nearest lines so that the edge is not on a grid line (which systematically over- or under-estimates the edge charge) [2].

### Level 3 — EC-FDTD, ports, NF2FF
- **EC-FDTD** (openEMS's formulation) interprets each cell edge as an equivalent circuit (capacitance from the averaged permittivity of the four surrounding cells, conductance from κ), which handles material interfaces that are not on grid lines by averaging [1].
- **Loss** is conductivity κ (S/m): a dielectric with loss tangent tanδ at $f_0$ is modelled as $\kappa = 2\pi f_0\varepsilon_0\varepsilon_r\tan\delta$ — correct at $f_0$, with loss ∝ 1/f error away from it (fine over a few-percent band).
- **Ports**: a *lumped port* is a resistor $R$ plus a voltage source across a cell edge line; $S_{11} = (V-RI)/(V+RI)$ per frequency. An *MSL port* records voltage at three planes and current at two; from these openEMS derives $\beta = \sqrt{-\,\partial_z E\,\partial_z H/(EH)}$ and $Z_0 = \sqrt{E\,\partial_zE/(H\,\partial_zH)}$ (openEMS `ports.py`) — i.e. the port measures the line it sits on, giving a de-embedded reference plane.
- **NF2FF**: equivalent currents $\mathbf J_s = \hat n\times\mathbf H$, $\mathbf M_s = -\hat n\times\mathbf E$ on a closed box are Fourier-transformed at the chosen frequency and radiated analytically to the far field; directivity $D = 4\pi U_{max}/P_{rad}$; radiation efficiency $e = P_{rad}/P_{acc}$ with $P_{acc} = \tfrac12\mathrm{Re}(V I^*)$ at the port.

## Design equations & rules of thumb

| Item | Rule | Source / check |
|---|---|---|
| Max cell in air | λ_min/20 (λ/30 for Z0/S11 better than 1 %) | [2]; Run 1 |
| Max cell in dielectric | λ_min/(20√εr) | |
| Substrate | ≥ 4 cells through h (8 for Z0 to < 1 %) | Run 1: 4→8 cells +0.6 % |
| Metal edges | thirds rule (`AddEdges2Grid(..., metal_edge_res=res/2)` or manual lines at ±⅓/⅔) | [2] |
| Grading | neighbouring cells ≤ 1.4–1.5× (`SmoothMeshLines(dir, res, 1.4)`) | tutorials |
| Air margin to MUR/PML | ≥ λ_max/4 (31 mm at 2.45 GHz) | [2] |
| NF2FF box | inside the boundary, outside PML, enclosing all radiators (board + feed) | |
| Excitation | `SetGaussExcite(f0, fc)`, fc = 20 dB half-bandwidth | tutorials |
| End criterion | 1e-4 (−40 dB) routine; 1e-5 for high-Q; `exact_endcriteria=True` for reproducibility | this page |
| Tan δ | κ = 2π f0 ε0 εr tanδ | [2] |
| Courant | Δt ≤ 1/(c√(Σ Δ⁻²)) — smallest cell rules | [3] |

## Worked examples

### Run 1 — does openEMS get a microstrip's Z0 right?
Geometry: JLCPCB-like 2-layer stack — 1.51 mm dielectric, εr 4.5 (lossless; a model input — JLC's own JLC0216A template uses a 1.43 mm core, see the [canonical width table](../13-pcb-rf-layout-emc/stackups-and-materials.md#canonical-50-ω-width-table)), zero-thickness PEC strip 2.80 mm wide, 100 mm long, two MSL ports meeting at the centre (openEMS tutorial style), PML_8 on the line ends, PEC ground at z-min, MUR elsewhere. Pre-registered: Z0 within 2 % of H-J and of the 2-D FD solver; mesh refinement < 1 %.
```python
from CSXCAD import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import C0
FDTD = openEMS(NrTS=200000, EndCriteria=1e-4)
FDTD.SetGaussExcite(1.6e9, 1.4e9)                                  # 0.2-3.0 GHz
FDTD.SetBoundaryCond(['PML_8', 'PML_8', 'MUR', 'MUR', 'PEC', 'MUR'])
CSX = ContinuousStructure(); FDTD.SetCSX(CSX)
mesh = CSX.GetGrid(); mesh.SetDeltaUnit(1e-3)                      # mm
res = C0 / (3e9 * 4.5**0.5) / 1e-3 / 50                            # lambda_min/50 in the substrate
third = [2*res/3/4, -res/3/4]                                      # thirds rule, fine cell res/4
mesh.AddLine('x', [-50, 50]); mesh.SmoothMeshLines('x', res)
mesh.AddLine('y', [0, 1.40 + third[0], 1.40 + third[1], -1.40 - third[0], -1.40 - third[1]])
mesh.SmoothMeshLines('y', res/4); mesh.AddLine('y', [-25, 25]); mesh.SmoothMeshLines('y', res)
mesh.AddLine('z', [i*1.51/8 for i in range(9)]); mesh.AddLine('z', 20); mesh.SmoothMeshLines('z', res)
CSX.AddMaterial('FR4', epsilon=4.5).AddBox([-50, -25, 0], [50, 25, 1.51])
pec = CSX.AddMetal('strip')
p1 = FDTD.AddMSLPort(1, pec, [-50, -1.4, 1.51], [0, 1.4, 0], 'x', 'z', excite=-1,
                     FeedShift=10*res, MeasPlaneShift=100/3, priority=10)
p2 = FDTD.AddMSLPort(2, pec, [50, -1.4, 1.51], [0, 1.4, 0], 'x', 'z', MeasPlaneShift=100/3, priority=10)
FDTD.Run('/tmp/msl', cleanup=True, exact_endcriteria=True)
import numpy as np; f = np.linspace(0.2e9, 3e9, 141)
p1.CalcPort('/tmp/msl', f)                       # p1.Z_ref = extracted line impedance, p1.beta
eps_eff = (np.real(p1.beta) * C0 / (2*np.pi*f))**2
```
(the full script is `tools/verify/sim_openems_msl.py`). Results:

| Mesh | Cells | Time | Z0 @ 0.44 / 0.92 / 1.58 / 2.44 GHz | εeff @ 0.92 GHz |
|---|---|---|---|---|
| λ/30, 4 substrate cells | 56 k | 4 s | 49.92 / 49.97 / 50.12 / 50.44 Ω | 3.403 |
| λ/50, 8 substrate cells | 231 k | 13 s | 50.17 / 50.29 / 50.47 / 50.82 Ω | 3.402 |
| Hammerstad–Jensen + Kirschning–Jansen (t = 0) | — | — | 50.43 / 50.42 / 50.42 / 50.46 Ω | 3.403 |
| 2-D FD solver (`tline_fd2d.py`, Richardson-extrapolated) | — | 2 s | 50.38 Ω (quasi-static) | 3.386 |

$|S_{11}| < -53$ dB and $|S_{21}| = -0.01$ dB (referenced to the extracted Z0): the ports and PML are clean. Z0 agrees with two independent methods within 0.3 %; the small rise of the openEMS Z0 with frequency (+0.7 % from 0.44 to 2.44 GHz, not predicted by K-J) is within typical port-extraction error and is logged as an open discrepancy. A first attempt with the excitation placed too close to the PML and a short line never decayed (energy stuck at 0 dB for 90 s) — if the energy does not fall within a few pulse lengths, look at the source/port placement before anything else.

### Run 2 — 2.45 GHz probe-fed patch on FR-4 (the patch-antennas page example)
Design from [patch antennas](../08-antennas/patch-antennas.md#worked-examples) (TL model): L = 28.81 mm (resonant), W = 37.23 mm, εr 4.4, tanδ 0.02, h 1.6 mm; here with a finite 80 × 80 mm ground and substrate and a 50 Ω lumped probe port 8.3 mm inside the radiating edge. MUR boundaries ≥ 40 mm from the board, NF2FF box auto-created, κ from tanδ at 2.45 GHz.

| Mesh (max cell / substrate cells) | Cells | Time | f_res | Z_in at f_res | BW (VSWR 2) | D | e_rad | G |
|---|---|---|---|---|---|---|---|---|
| 3.1 mm / 4 | 127 k | 8 s | 2.386 GHz | 41.5 + j4.5 Ω | 2.14 % | 6.95 dBi | 44.2 % | 3.40 dBi |
| 2.1 mm / 6 | 400 k | 25 s | 2.395 GHz | 42.2 + j4.4 Ω | 2.17 % | 6.95 dBi | 44.8 % | 3.47 dBi |
| 1.4 mm / 8 | 1.16 M | 54 s | 2.397 GHz | 42.1 + j5.5 Ω | 2.21 % | 6.95 dBi | 44.5 % | 3.44 dBi |
| TL/cavity model (`ant_patch.py`) | — | — | 2.45 GHz (design) | ~50 Ω (inset point) | 2.6 % | 6.1 dBi | 40 % | 2.1 dBi |

Against the pre-registration: frequency within ±3 % ✓ (−2.2 %, converged: +0.38 % then +0.08 % per refinement), efficiency ✓ (44.5 vs 40 %), bandwidth ✓ (2.2 vs 2.6 %), directivity higher than the two-slot model by 0.85 dB — plausible for a finite 80 mm (0.65λ) ground that the two-slot model does not include, but not separately verified. **Engineering conclusion**: the TL model's patch would come out ≈ 50 MHz low; shorten L by ≈ 2 % (≈ 0.6 mm) *and* expect εr tolerance (±0.2 → ±2.3 %) to matter as much — trim or measure the laminate ([patch antennas](../08-antennas/patch-antennas.md)).

### Post-processing snippet (patch)
```python
f = np.linspace(2.0e9, 2.9e9, 901)
port.CalcPort(sim_path, f)
s11 = port.uf_ref / port.uf_inc;  zin = port.uf_tot / port.if_tot
fres = f[np.argmin(abs(s11))]
ff = nf2ff.CalcNF2FF(sim_path, fres, np.arange(0, 181, 2.0), [0.0, 90.0], center=[0, 0, 1e-3])
D = ff.Dmax[0]; eff = ff.Prad[0] / np.interp(fres, f, port.P_acc)   # radiation efficiency
```

### Run 3 — nose-cone detuning of a quarter-wave whip (915 and 433 MHz) (`tools/verify/sim2_openems_nosecone.py`)
**Model** (the team's cone and bulkhead are not recorded in the Space Bar notes, so the KB's representative cone from [antennas on rockets](../08-antennas/antennas-on-rockets.md) Example 3 is used):
- a 4:1 tangent-ogive fibreglass cone, inner radius 50 mm, wall 3 mm, 424 mm long, with a 20 mm shoulder, built with `AddRotPoly` (a body of revolution from an (r, z) polygon);
- G10-class laminate, εr 4.7, tanδ 0.02;
- a 2 mm aluminium bulkhead disc of radius 50 mm;
- a 2 × 2 mm square PEC whip (equivalent round radius 1.18 mm), 78 mm long (the KB's bench-trimmed 915 MHz whip) or 165 mm (433 MHz), fed by a 50 Ω lumped port across a 1 mm gap;
- MUR boundaries λ/4 (at the low band edge) from the cone.

Fine-region cells of 2.0 / 1.4 / 1.0 mm give 1.0 / 2.4 / 4.9 M cells. Each run took 13–170 s at 100–250 MCells/s; set-up of the `RotPoly` material adds about 40 s. Resonance is taken where X = 0. The bare and coned cases use **identical meshes**, so most of the discretisation error cancels in the shift.

| Case (mesh 2 unless stated) | f_res (X = 0) | R at f_res | Shift vs bare | e_rad | Note |
|---|---|---|---|---|---|
| 915 MHz whip, bare, mesh 1 / 2 / 3 | 932.87 / 934.93 / 936.38 MHz | 25.2 / 25.0 / 24.9 Ω | — | 98 % | +0.37 % from mesh 1 to 3 |
| 915 MHz whip in cone, mesh 1 / 2 / 3 | 921.24 / 923.59 / 925.28 MHz | 23.4 / 23.2 / 23.1 Ω | **−1.25 / −1.21 / −1.19 %** | 96.9 % | the shift converges (0.03 points from mesh 2 to 3) |
| in cone, PML_8 instead of MUR | 919.86 (bare 931.50) MHz | 21.7 Ω | −1.25 % | 98.3 % | absolute f −0.37 % |
| in cone, air margin doubled (MUR) | 918.49 (bare 929.95) MHz | 21.7 Ω | −1.23 % | 96.1 % | absolute f −0.53 % |
| cone of εr 4.0 (hand-laid laminate) | 924.53 MHz | 23.6 Ω | −1.11 % | 97.0 % | 0.92 × the εr 4.7 shift |
| disc + 250 mm conductive av-bay tube (r 45 mm), bare | 966.39 MHz | 33.5 Ω | **+3.36 % vs disc only** | 99.0 % | the counterpoise matters more than the cone |
| same, in cone | 950.04 MHz | 25.2 Ω | −1.69 % | 97.6 % | |
| 433 MHz whip (165 mm), bare, mesh 1 / 2 / 3 | 497.94 / 497.93 / 497.90 MHz | 31.4–31.7 Ω | — | 96.7 % | the 100 mm disc is only 0.14λ: resonance +15 % above 433 MHz |
| 433 MHz whip in cone, mesh 1 / 2 / 3 | 483.79 / 483.98 / 484.11 MHz | 29.7–30.0 Ω | **−2.84 / −2.80 / −2.77 %** | 95.7–96.0 % | |

**Against the pre-registration** (script header, written before any run):
- **P1 passed at 915 MHz** (predicted −0.5 to −3 %, central −1.5 %; found −1.2 %). **P1 missed at 433 MHz** (predicted −0.3 to −2 %; found −2.8 %). The simple energy-fraction estimate under-weighted the cone: the longer whip has its whole length inside the cone's near-field zone, and the ogive narrows towards the tip.
- **P2 passed.** The cone's loss costs 1.2 points of efficiency, 0.05 dB.
- **P3 passed.** The shift moved by less than 0.05 points between meshes, and by less than 0.05 points between MUR, PML and a doubled box.
- **P4 missed.** εr 4.0 gives 0.92 × the shift rather than the ~0.8 × of (εr − 1) scaling. That lies between (εr − 1) and (εr − 1)/εr scaling, consistent with a field that crosses the wall partly normal to it.
- **P5 passed.** A conductive av-bay below the bulkhead moved the resonance +3.4 %, nearly three times the cone's effect.
- **P6 passed.** The bare whip resonates at 935 MHz with R = 25 Ω.

**Directivity is boundary-sensitive here and is not reported as a result.** It came out 2.12 dBi with MUR, 2.17 dBi with a doubled box and 1.70 dBi with PML_8. The NF2FF read-out uses only the φ = 0°/90° cuts, which is adequate for f_res and S11 but not for D. This is listed as an open question.

**Engineering answers**:
1. A G10 nose cone pulls a 915 MHz whip down about **1.2 %** (11 MHz) and a 433 MHz whip about **2.8 %** (14 MHz).
2. Each mm of a 78 mm whip is about 1.25 % at 915 MHz (PyNEC over a perfect ground: 77/78/79 mm → 900.3/889.0/878.0 MHz). The cone therefore costs about one millimetre of trim; this is the "a few percent" of 08 made concrete. 08 Example 3 quotes ≈ 0.6 % per 1 mm step, about half the computed value; this is recorded as a cross-domain note, not edited here.
3. The ground system is the bigger unknown. A 100 mm bulkhead disc alone puts a 165 mm whip at 498 MHz, and adding a conductive av-bay moves it by another 3 %.
4. In the real rocket the feed coax and the electronics act as counterpoise, so **trim in the assembled airframe** (08 Example 3), not on the bench.

(Cross-domain: these numbers belong in 08/antennas-on-rockets; recorded in the W5-S11 log for that domain's owner.)

## Practical notes
- **Start from a tutorial**: `~/opt/src/openEMS-Project/openEMS/python/Tutorials/` has Simple_Patch_Antenna, MSL_NotchFilter, Helical_Antenna, Horn, RCS_Sphere, StripLine2MSL, CRLH_Extraction, … — each a validated starting point.
- **Look at the geometry** before running: `CSX.Write2XML('model.xml')` and open it in AppCSXCAD (a GUI — run it yourself), or pass `debug_PEC=True`/`debug_material=True` to `Run()` and view the VTK files in ParaView. Misplaced priorities (substrate overriding metal) are the commonest silent error.
- **Performance** on an Apple-Silicon Mac: ≈ 100–170 MCells/s for these sizes (openEMS picks the thread count itself; our runs settled on 1 thread for tiny meshes). A 1 M-cell patch at 2.45 GHz takes about a minute; a 433 MHz PCB antenna with 0.2 mm features in a λ/4 air box can take hours — exploit symmetry (PMC/PEC walls), shrink the air box to λ/4, and mesh fine only where needed.
- **Reproducibility**: pass `exact_endcriteria=True` to `FDTD.Run()` (maps to the `--exact-endcriteria` command-line option). Without it the stopping step depends on machine speed; with it two runs gave identical 2660-step results (tested on the λ/30 microstrip).
- **Copper thickness and soldermask**: model 35 µm copper as a thin box if the gap/width is < ~10× the thickness (CPWG with 0.2 mm gaps); model the mask (εr ≈ 3.8, 15–25 µm) for thin stack-ups — they shift Z0 by 2–5 Ω ([impedance calculators](impedance-and-rf-calculators.md)).
- **Save the script, the version line and the results** together (`tools/verify/sim_openems_results.txt` pattern).

### Recipe for a new model (e.g. a 915 MHz PCB antenna on the flight computer)
1. **Write down the expected answer first** (resonance from the datasheet/TL model, expected bandwidth, gain range) and the pass criteria — see [simulation validation](simulation-validation.md).
2. **Units and frequency plan**: `SetDeltaUnit(1e-3)` (mm); Gaussian centred on the band with `fc` covering ±30–50 % so the mismatch around resonance is visible.
3. **Geometry**: substrate box (priority 0), copper as metal boxes/polygons (priority 10), ground plane as the real board outline; include the feed line to where the matching network or U.FL connector sits, and the ground clearance (keep-out) exactly as in KiCad.
4. **Ports**: lumped port (50 Ω) at the matching-network pads, or an MSL port on the feed line if you want a de-embedded reference plane.
5. **Mesh**: fixed lines on every metal edge (thirds rule), ≥ 4 cells through the substrate, ≤ λ/20 in dielectric, smooth with ratio 1.4; air box ≥ λ/4 at the lowest frequency (82 mm at 915 MHz).
6. **Boundaries**: MUR for a first look, PML_8 for the final answer; NF2FF box auto-created (inside the boundary).
7. **Dry run**: `FDTD.Run(path, setup_only=True, debug_PEC=True)` and inspect the PEC/material VTK in ParaView (or the XML in AppCSXCAD — a GUI you start yourself); count cells and estimate time from ≈ 100 MCells/s.
8. **Run** with `exact_endcriteria=True`, EndCriteria 1e-4 (1e-5 for high Q).
9. **Post-process**: S11, Z_in, bandwidth, NF2FF at resonance → D, e_rad, G; check $P_{rad} \le P_{acc}$.
10. **Refine** the mesh once or twice; report the change in f_res and G. **Compare** with the pre-registered expectation and, finally, with a NanoVNA measurement of the built board — the only arbiter for things you did not model (enclosure, battery, cable).

### What openEMS is and is not good for (in this KB's use cases)

| Use case | openEMS suitability | Notes |
|---|---|---|
| Microstrip/CPWG impedance, discontinuities, SMA launch | good | MSL port gives de-embedded S-parameters; 2-D solvers are faster for plain Z0 |
| Patch antennas, GNSS patches on ground planes | good | high-Q ceramic patches need long runs (−50 dB) |
| PCB IFA/meander antennas at 433/915 MHz | good but slow | fine features in a large air box; use symmetry and graded meshes |
| Antenna inside a fibreglass nose cone | good | model the cone as a dielectric shell; carbon fibre as a lossy conductor sheet |
| Wire Yagis, dipoles | works, inefficient | NEC is 100–1000× faster ([NEC](nec-antenna-modelling.md)) |
| Electrically huge structures (whole rocket at 5.8 GHz) | poor | billions of cells; use MoM with MLFMM or asymptotic methods (commercial) |
| Circuits with active devices | not the tool | SPICE / harmonic balance, with openEMS-extracted S-parameters |

### Run 4 — flight-computer PCB features (`tools/verify/sim2_openems_pcb.py`)
**4a — microstrip over a slot in its ground plane** (the "slot under a trace" of [13 grounding](../13-pcb-rf-layout-emc/grounding-and-return-paths.md), whose page assumed Z_slot = 100 Ω).
- Line: 50 Ω microstrip on the JLC 2-layer core (W 2.691 mm, h 1.43 mm, εr 4.5), with MSL ports.
- Slot: 1 mm wide, crossing the line at its centre, with air above and below the board.
- Each run: 0.23–0.35 M cells, 6–17 s.
- The equivalent series inductance comes from a fit to $|S_{21}|^2 = 1/(1 + (\omega L/2Z_0)^2)$ below the first resonance. The slot impedance then follows from the 13 page's $L = Z_{slot}\ell/(4v)$ with $v = c/\sqrt{(\varepsilon_r+1)/2}$.

| Slot length | S21 at 433 / 915 / 1575 / 2450 MHz | First S21 minimum | L_fit | Z_slot from L_fit |
|---|---|---|---|---|
| none | −0.01 / 0.00 / 0.00 / 0.00 dB | — | — | — |
| 10 mm | −0.01 / −0.01 / −0.03 / −0.07 dB | > 3 GHz | 1.20 nH | 87 Ω |
| 20 mm | −0.01 / −0.05 / −0.18 / −0.62 dB | > 3 GHz | 1.95 nH | 70 Ω |
| 40 mm | −0.05 / −0.29 / −1.46 / **−14.8** dB | −19.6 dB at 2.573 GHz | 4.35 nH | 79 Ω |
| 60 mm (mesh 1 / mesh 2) | −0.17 / −0.97 / **−10.0** / −2.5 dB | −17.3 dB at 1.741 GHz (1.758 GHz on mesh 2) | 7.63 nH (7.82) | 92 Ω (94) |

Against the pre-registration:
- **S1 passed.** The fitted Z_slot is 70–94 Ω, so the page's 100 Ω is a fair round number, slightly high.
- **S2 passed at 40 mm and missed narrowly at 60 mm.** The resonances sit 13.9 % (40 mm) and 15.6 % (60 mm) above the $\lambda_{slot}/2$ estimate with $(\varepsilon_r+1)/2$; the tolerance was ±15 %. The effective permittivity the slot actually sees is ≈ 2.06–2.12, not 2.75, because a 1.43 mm board is thin compared with the slot's fringing field.
- **S3 passed for 10 mm and missed for 60 mm.** A 10 mm slot costs 0.01 dB at 915 MHz. The 60 mm slot costs only 0.97 dB at 915 MHz, not the > 3 dB predicted. It costs 10 dB at 1575 MHz, near its resonance.
- **P3 passed for the slot.** The resonance moved 1.0 % between meshes.

**Lesson for layout.** A slot is harmless while it is short compared with λ/2 in the slot, and destructive near its resonance. A 60 mm split under a GNSS trace notches L1 by 10 dB. The same slot at 915 MHz is a 1 dB problem plus a radiator (EMC), because in this lossless model the power missing from S21 is either reflected or radiated by the slot.

**4b — SMA edge-launch signal pad on JLC04161H-7628, L2 intact vs voided** (the [13 connectors-and-launches](../13-pcb-rf-layout-emc/connectors-and-launches.md) case).
- Pad: 1.3 × 3.0 mm, between two 50 Ω lines (0.403 mm, t = 0). The connector is taken as a matched continuation.
- Stack: L1–L2 prepreg 0.2104 mm (εr 4.4), L2–L3 core 1.065 mm (εr 4.55).
- Void case: the L2 void extends 0.4 mm beyond the pad, L3 stays solid, and four stitching vias tie L2 to L3 around the void.
- Fine cells of 0.10 / 0.06 / 0.035 mm, 0.18–1.1 M cells, 9–116 s.

| Case, mesh 1 / 2 / 3 | RL at 0.915 GHz | 1.575 GHz | 2.45 GHz | 5.8 GHz |
|---|---|---|---|---|
| L2 intact | 19.5 / 19.7 / — dB | 15.1 / 15.0 | **11.5 / 11.4** | **5.5 / 5.7** |
| L2 voided under the pad | 28.5 / 29.2 / 29.8 dB | 24.3 / 24.7 / 24.8 | **21.2 / 21.3 / 20.9** | **16.2 / 15.5 / 15.5** |
| 1-D line-section model (`pcb_launch.py`) | — | — | 12 / 21 dB | 6 / 14 dB |

Against the pre-registration:
- **P1 passed.** L2 intact gives 10–14 dB at 2.45 GHz and 5–8 dB at 5.8 GHz.
- **P2 passed.** L2 voided gives 17–25 dB and 11–17 dB.
- **P3 passed.** The meshes agree within 0.4 dB at 2.45 GHz.
- The intact-plane mesh-3 run stalled at −38 dB of energy and hit the 25-minute cap, so it is missing.
- 13's 1-D numbers hold to about 0.5–2 dB. At 5.8 GHz the void does slightly better than the 1-D estimate (15.5 vs 14 dB).

Two set-up lessons came out of this sub-run:
1. **The first pad series put the MSL feed and its measurement plane inside the 5.4 mm PML.** This is the port-in-PML fault of the broken-model table. It gave mesh-inconsistent nonsense: 13.3 → 10.5 dB at 2.45 GHz and 8.0 → 3.6 dB at 5.8 GHz between meshes. Moving the feed 9 mm and the plane 14 mm in fixed it.
2. **A void excites the L2–L3 parallel-plate region.** In simulation it needed absorbing y-walls. A static field stays trapped there, so the energy never falls below about −9 dB and the run must be bounded with NrTS. In hardware the equivalent is plenty of stitching vias around every void.

**4c — a 915 MHz printed IFA on a flight-computer-sized board, free and inside a fibreglass body tube.**
- Board: 100 × 40 mm, 1.6 mm FR-4 (εr 4.5, tanδ 0.02) with an 80 × 40 mm top-layer ground pour.
- Antenna: a 1 mm trace in the 20 × 40 mm clearance, made of a 9 mm shorting leg, 36 mm along the board end, then folded back along the edges. The feed is 6 mm from the short, through a 50 Ω lumped port at the ground edge.
- Tube: εr 4.7, 3 mm wall, inner radius 50 mm, axis along the board.
- Antenna-region cells of 0.7 / 0.5 / 0.35 mm give 1.1 / 1.8 / 4.2 M cells, 50–250 s per run.
- This geometry is assumed. The team's boards use modules with external antennas, so this is the "could it go on the board?" case.
- Design step: a length sweep found 50 / 62 / 75 / 82 / 87 / 92 mm → best match at 1355 / 1161 / 1037 / 970 / 924 / 882 MHz. 88 mm was chosen and gives 914.9 MHz on mesh 1.

| 88 mm IFA | Best match (S11 minimum) | Z there | S11 | VSWR-2 bandwidth |
|---|---|---|---|---|
| free, mesh 1 / 2 / 3 | 914.90 / 917.60 / 917.87 MHz | 51.5–51.9 + j28 Ω | −11.4 dB | 4.85–4.90 % |
| in the tube, mesh 1 / 2 / 3 | 921.11 / 923.81 / 924.08 MHz | 51.9–52.3 + j24 Ω | −12.7 dB | 5.67 % |
| shift | **+0.68 % on every mesh** | X down 4 Ω | +1.3 dB better | +0.8 points |

Against the pre-registration:
- **I2 missed: the sign is wrong.** The best-match frequency moved *up*. This IFA never reaches X = 0 in band; its reactance is about +28 Ω. The tube's capacitive loading cancels about 4 Ω of that inductive reactance, and the best match slides up. "Resonance" taken from the S11 minimum is not a resonance proxy here, and the pre-registration assumed it was.
- **I3 passed.** The shift changed by 0.00 points between meshes.
- **I1 partly passed.** R (51 Ω) and bandwidth (4.9 %) are inside the predicted ranges.

**Not reported as results: efficiency and directivity.** NF2FF gave D = 8.5 dBi with MUR boundaries and 4.9 dBi with PML_8, and e_rad 41 % and 34 %. A 0.3λ IFA cannot have 8.5 dBi, and the boundary dependence matches Run 3's. Until that is resolved, use these models for match and frequency only, and measure gain.

**Engineering reading.**
1. A fibreglass tube around the board barely detunes this IFA (< 1 %), and in the direction that depends on the antenna's reactance.
2. The cost of a board antenna at 915 MHz is the 20 × 40 mm keep-out and an 88 mm trace path. Even then the match is only −11 dB without a matching network. An external whip on a U.FL is the simpler choice, as the team already does.

### Run 5 — scan blindness without Floquet boundaries: the embedded element pattern of a finite row (`tools/verify/sim2_openems_array_blindness.py`)
**Why this route.** openEMS v0.37 has no phase-shifted periodic boundary; its boundary types are PEC, PMC, MUR and PML_n, checked in the source. So the textbook scanned unit cell cannot be built. Hannan's relation gives another way in. In a large array the centre element's embedded pattern (that element driven, all others terminated in 50 Ω) is the array's scan gain per element:
$$G_{emb}(\theta) \approx \frac{4\pi A_{cell}}{\lambda^2}\,(1 - |\Gamma_a(\theta)|^2)\cos\theta$$
so a scan blindness ($|\Gamma_a| \to 1$) appears as a dip in one run's pattern.

**Model.**
- 1.6 mm FR-4 (εr 4.4, lossless), PEC ground at the z boundary, substrate running into PML (an "infinite" slab).
- 15 probe-fed patches in one E-plane row, 15.74 × 11.75 mm (the TL-model design for 5.8 GHz).
- Spacing d = 0.586λ (30.3 mm) and 0.5λ (25.8 mm). Each run: 0.8–2.8 M cells, 43–128 s.
- The estimate from [12 planar arrays](../12-phased-arrays/planar-arrays-element-pattern-coupling.md) is $\sin\theta_b = \lambda/d - \beta_{TM_0}/k_0$, giving **44°** at 0.586λ and 81° at 0.5λ.

| Case | Centre-element S11 minimum | E-plane embedded pattern at 5.8 GHz | Verdict |
|---|---|---|---|
| d = 0.586λ, coarse / fine mesh | 5.16 / 5.20 GHz | local minimum −4.3 dB at 50–55°, recovering to −2.3 dB at 65°; residual from a smooth cos^q fit −1.6 / −2.2 dB at 53° | **A1 missed**: dip < 3 dB, at 53° rather than 44° |
| d = 0.5λ | 5.155 GHz | no dip ≥ 3 dB within 0–70° (largest −2.4 dB at 75°) | A2 passed |
| d = 0.586λ minus d = 0.5λ (post-hoc) | — | −1.7, −1.8, −2.1, −2.6, −1.5 dB at 40, 45, 50, 55, 60°; ≈ 0 at 65° | a relative blindness signature centred near 52° |
| one isolated patch, coarse / fine | 5.150 / 5.188 GHz | — | the low match frequency belongs to the patch and probe, not to the array |

How to read it:
1. A 15-element, one-dimensional row on an infinite slab shows a **reproducible but shallow** (2–3 dB) E-plane dip near 52°. The phase-matching estimate for an infinite 2-D array is 44°.
2. Finite size softens and shifts the dip. Only one row couples, and the edge elements are not in an "array environment". The patches are also mismatched at 5.8 GHz (their S11 minimum sits at 5.2 GHz: the TL design plus probe reactance comes out 11 % low here, against 2 % at 2.45 GHz in Run 2).
3. The H-plane fit residuals (−0.8 to −4 dB near 55°) appear for the isolated patch too. They are an element-shape artefact of the cos^q fit, so the H-plane check (A3) is inconclusive.
4. **Engineering reading.** On 1.6 mm FR-4 at 5.8 GHz, a 0.586λ lattice puts a measurable gain dip inside a ±45–55° scan range, and λ/2 spacing does not. That supports the 12 page's spacing rule $d \le \lambda/(\beta_{sw}/k_0 + \sin\theta_{max})$.
5. A quantitative $\Gamma_a(\theta)$ needs a periodic-boundary code (CST/HFSS/Ansys student, or MEEP, which has Bloch-periodic boundaries; not installed here), or a much larger 2-D finite array.

### Practicalities: field dumps, curved and STL geometry, graded meshes, and a deliberately broken model (`tools/verify/sim2_openems_broken.py`)
**Field dumps and ParaView animation.**
```python
et = CSX.AddDump("Et_midplane", dump_type=0, file_type=0, sub_sampling=[2, 2, 1])   # 0 = E(t), VTK
et.AddBox([-50, -25, H/2], [50, 25, H/2])                                            # a plane inside the substrate
ef = CSX.AddDump("Ef", dump_type=10, frequency=[915e6, 2.45e9])                      # 10 = E at given f (complex)
```
- Time-domain dumps (`dump_type` 0 = E, 1 = H, 2 = J, …) write one `.vtr` file per dump step. The microstrip reference run wrote 57 files `Et_midplane_0000000000.vtr` … into the simulation folder.
- Frequency-domain dumps (`dump_type` 10–15, with `frequency=[…]`; 20–22 for SAR) write the complex field at each listed frequency. Use `file_type=1` (HDF5) for those you will post-process in Python.
- **ParaView recipe**:
  1. File → Open, select the `Et_*.vtr` group. ParaView recognises the numbered files as one time series.
  2. Apply, then colour by `E-Field` (Magnitude or one component).
  3. Set the colour range to a fixed value (e.g. ±1 % of the peak), not "per time step". Otherwise the decaying wave seems to stay bright.
  4. Press Play, and use File → Save Animation for a movie.
- **Dump only what you need.** A full-volume dump of a 5 M-cell model at every step is gigabytes. Dump a plane, sub-sample (`sub_sampling`) and/or set `opt_resolution`.
- `debug_material=True` / `debug_PEC=True` in `Run()` (or `setup_only=True` for a dry run) write `material_dump.vtr` and `PEC_dump.vtp`. Open these first: they show what the voxeliser actually built.

**Curved and imported geometry.**
- **Bodies of revolution use `AddRotPoly`.** Give an (r, z) polygon and rotate it about an axis: `prop.AddRotPoly(points=[r_list, z_list], norm_dir='x', elevation=0, rot_axis='z', angle=[0, 2*np.pi])`. Run 3's ogive nose cone is built this way, and so is the conical-horn tutorial. Cylindrical shells (`AddCylindricalShell`) suit body tubes.
- **CAD parts come in through STL/PLY with `prop.AddPolyhedronReader(fn, priority=…)` followed by `.ReadFile()`.** Two traps were found:
  1. **Faces exactly on mesh lines are ambiguous.** The 915 MHz whip written as a 12-triangle STL box with its faces on the mesh lines lost 127 of its PEC edges in the dump and resonated at **832 MHz instead of 933 MHz (−10.8 %)**. Moving the STL faces 0.01 mm off the lines gave **932.87 MHz, identical to the primitive**. Keep imported surfaces off grid lines: offset them, or place the mesh with the thirds rule around them. Then compare the PEC dump with the primitive version.
  2. **Set-up time.** The 64-facet STL bulkhead disc took 474 s to voxelise, against 13 s for `AddCylinder`. Use primitives for simple shapes and STL only for genuine CAD parts.

**Graded meshes without slivers.**
- `SmoothMeshLines(dir, res, ratio=1.4)` fills gaps with a geometric grading. It never removes lines, so two lines a few µm apart survive and set the time step.
- That happened twice in this work. A nose-cone mesh built from `np.arange` steps plus fixed lines gave a 0.54 ps time step (1.8 ps after the fix). The IFA board mesh had a 0.017 mm cell and a 0.11 ps step.
- The fix is a merge-then-subdivide helper, `fill_lines()` in `sim2_openems_nosecone.py`: sort the fixed lines, merge any closer than 0.3 × res, and split each gap into equal cells ≤ res.
- **Always print `min(diff(lines))` per axis, or the "FDTD timestep is" line, before a long run.**
- The deliberately ungraded mesh (case `ungraded`: 0.25 mm cells jumping to 4 mm at x = 0, a ratio of 16) made the clean microstrip reflect at −39 dB (median −48 dB, against −54 dB). That is small for a line. A resonator or antenna sitting across such a jump would also shift.

**A deliberately broken model — what each fault looks like.** The reference is Run 1's microstrip, with |S11| < −53 dB. Each case changes one thing; expectations B1–B6 are in the script header.

| Case | What was changed | Symptom | Pre-registered? |
|---|---|---|---|
| ref | nothing | \|S11\| ≤ −53.7 dB, \|S21\| −0.01 dB | B1 ✓ |
| pec_box | lumped ports touching the closed PEC wall | **\|S11\| = 0 dB at every frequency** (the port's excitation edge lies on PEC, so the port is shorted) | B2 not testable — a real, separate set-up error |
| pec_box2 | the same line in a closed 100 × 100 × 21.5 mm PEC box, ports 5 mm inside | one narrow spike: \|S11\| −1.9 dB, \|S21\| −13 dB at **2.063 GHz** = empty-box TE₁₁₀ 2.120 GHz lowered 2.7 % by the substrate | B2 ✓ |
| port_pml | MSL feed placed inside the PML | \|S11\| ≈ −11 dB everywhere, \|S21\| down to −17.7 dB on a lossless line: garbage | B3 ✓ |
| ungraded | 16× mesh jump | \|S11\| max −38.9 dB | B4 ✗ (smaller than the −35…−20 dB predicted) |
| stl | whip + bulkhead from STL on grid lines | f_res 919.6 MHz (−1.4 %); 832 MHz with the STL whip alone; fixed by a 0.01 mm offset | B5 ✗ → trap found |
| patch_ec | 2.45 GHz patch, EndCriteria 10⁻² … 10⁻⁵, **without** `exact_endcriteria` | all four runs stopped after the same ~8 s (BW 2.18/2.18/2.14/2.14 %): the criterion is never checked within 4 s | the wall-clock trap again |
| patch_ecx | same, `exact_endcriteria=True` | 10⁻² (−20 dB): f +0.13 %, S11 −12.1 dB instead of −19.3, BW +12 %, e_rad 31.8 instead of 43.9 %. 10⁻³: BW +9.8 %. 10⁻⁴: BW +3.7 %, e_rad −0.8 points | B6 partly ✗ (expected 10⁻³ within 2 %, 10⁻⁴ within 0.5 %) |

**Diagnosing spikes or nonsense in a simulated S11:**
1. **Narrow spikes, or S21 dips, on a structure that should be smooth** are cavity or box resonances. Compute $f_{mn0} = \tfrac{c}{2}\sqrt{(m/a)^2+(n/b)^2}$ for the enclosure (lowered a few % by the dielectric) and see whether the spikes line up. Fixes: an absorbing boundary instead of PEC, or a real enclosure with absorber or via fences if the hardware is shielded.
2. **|S11| ≈ 0 dB everywhere** means the port is shorted (on a PEC wall or a metal priority conflict) or open (not touching the conductor). Look at the PEC dump around the port.
3. **A flat −10 to −20 dB "floor" on a lossless through-line**: the port or its feed sits inside the PML, or too close to a discontinuity.
4. **Ripple with a period of 1/(ring-down time)**, a wrong bandwidth or depth, or efficiency that varies run to run: the time signal was truncated. Use `exact_endcriteria=True` and −50 dB for resonant antennas.
5. **A resonance that moves when nothing physical changed** (an STL re-export, a tiny mesh edit): voxelisation. Compare `PEC_dump.vtp` and `material_dump.vtr`.
6. **A far-field number that moves with the boundary type** (Run 3: D 1.70–2.17 dBi between PML and MUR): check the NF2FF box placement and angular sampling before quoting directivity.

## Common mistakes & misconceptions
- **Mesh too coarse at edges** — resonances shift by several percent; always run a refinement series (≥ 3 levels) and report the change.
- **Boundaries too close / NF2FF box touching the PML** — pattern and efficiency errors; keep λ/4 of air.
- **Port too close to a discontinuity or the source inside the absorbing layer** — no decay, garbage S11 (Run 1's first attempt).
- **Stopping too early** — high-Q antennas (GNSS ceramic patches, small loops) need −50 dB; an early stop smears S11 and bandwidth.
- **Trusting a pretty 3-D pattern** — check that $P_{rad} \le P_{acc}$ (efficiency ≤ 1), that D is sensible for the aperture, and that the pattern does not change with mesh.
- **Forgetting the feed**: an ideal lumped port directly on the patch ignores the connector, via and feed line; for a PCB antenna include the feed line with an MSL port and de-embed.
- **Believing the TL-model patch dimensions are final** — Run 2 shows a 2 % frequency error even before laminate tolerance.

## How to simulate / verify
- `~/opt/openEMS/venv/bin/python tools/verify/sim_openems_msl.py` — Run 1 (≈ 20 s); set `RFKB_EXACT_EC=1` for deterministic stopping.
- `~/opt/openEMS/venv/bin/python tools/verify/sim_openems_patch.py` — Run 2 (≈ 90 s, three meshes).
- `~/opt/openEMS/venv/bin/python tools/verify/sim2_openems_nosecone.py [case …]` — Run 3 (each case 15 s–3 min; `RFKB_DRY=1` = set-up only, with material/PEC dumps).
- `~/opt/openEMS/venv/bin/python tools/verify/sim2_openems_pcb.py slot | pad | ifa_sweep | ifa_L<len>_<free|tube>_m<k>` — Run 4.
- `~/opt/openEMS/venv/bin/python tools/verify/sim2_openems_array_blindness.py d0586 d05` — Run 5.
- `~/opt/openEMS/venv/bin/python tools/verify/sim2_openems_broken.py [ref pec_box pec_box2 port_pml ungraded stl stl_whip stl_whip_eps patch_ec patch_ecx]` — the practicalities section.
- All W5-S11 results: `tools/verify/sim2_openems_results.txt` (human-readable) and `.jsonl` (machine-readable, including patterns).
- Independent references: `python3 -m rfcalc microstrip --w 2.8mm --h 1.51mm --er 4.5 --t 0` (closed form), `tools/verify/tline_fd2d.py` (2-D FD), `tools/verify/ant_patch.py` (TL/cavity patch model).

## Open questions / gaps
- The 0.85 dB directivity excess of the finite-ground patch vs the two-slot model was not checked against a larger-ground run.
- The slight frequency dependence of the openEMS MSL-port Z0 (+0.7 % over 0.44–2.44 GHz) is unexplained.
- The nose cone (Run 3) and the PCB features (Run 4) are now simulated, but **none is measured**. The team's real cone, bulkhead and harness geometry are unknown. A NanoVNA sweep of the whip in the assembled nose cone, against Run 3's −1.2 % / −2.8 %, is the decisive check (validation register R07/R21).
- Run 3's directivity depends on the boundary (1.70–2.17 dBi) and was not resolved. Suspects: the two-cut NF2FF sampling, and the NF2FF box placement next to the PML.
- Not modelled: CPWG via-fence distance from the gap edge, shield-can coupling, and a scanned infinite-array unit cell (no Floquet boundary in openEMS). These are left in the gap register.

- **Phased-array unit cells (W2-B5 request):** openEMS v0.37 has **no** phase-shifted periodic (Floquet) boundary. Checked in the source: the boundary types are PEC, PMC, MUR and PML_n. A scanned infinite-array unit cell therefore cannot be simulated; Run 5 uses a finite row instead; for broadside-only scans a unit cell between PEC/PMC walls (waveguide-simulator method) works in any FDTD code, and a finite-array model with all ports terminated gives embedded element patterns directly ([12 planar arrays](../12-phased-arrays/planar-arrays-element-pattern-coupling.md)).

## Sources
1. T. Liebig, openEMS project and documentation (v0.37), https://www.openems.de/ , https://docs.openems.de/ ; source repository github.com/thliebig/openEMS-Project (install docs, Python API, `ports.py`, `nf2ff.py`, `openems.cpp` end-criterion logic). (tool documentation / source)
2. openEMS tutorials "Simple Patch Antenna" and "MSL Notch Filter" (Python), in `openEMS/python/Tutorials/` — mesh resolution, thirds rule, MSL port setup, κ from tanδ. (tool documentation)
3. A. Taflove and S. C. Hagness, *Computational Electrodynamics: The Finite-Difference Time-Domain Method*, 3rd ed., Artech House, 2005 — ch. 3 (Yee algorithm), ch. 4 (numerical dispersion and stability, Courant limit), ch. 7 (PML), ch. 8 (near-to-far-field). (textbook)
4. K. S. Yee, "Numerical solution of initial boundary value problems involving Maxwell's equations in isotropic media," *IEEE Trans. Antennas Propag.*, 14(3):302–307, 1966. (peer-reviewed)
5. T. Liebig, A. Rennings, S. Held, D. Erni, "openEMS — a free and open source equivalent-circuit (EC) FDTD simulation platform supporting cylindrical coordinates suitable for the analysis of traveling wave MRI applications," *Int. J. Numerical Modelling: Electronic Networks, Devices and Fields*, DOI 10.1002/jnm.1875 (online Dec. 2012; as listed in the openEMS publications page). (peer-reviewed)
6. E. Hammerstad and Ø. Jensen, "Accurate models for microstrip computer-aided design," IEEE MTT-S Digest, 1980, pp. 407–409 (reference Z0 for Run 1). (peer-reviewed)
7. This repository: `tools/verify/sim_openems_msl.py`, `sim_openems_patch.py`, `sim_openems_results.txt` (W3-C2); `tline_fd2d.py`, `ant_patch.py` (W1-A4, W1-A6). (verification)
