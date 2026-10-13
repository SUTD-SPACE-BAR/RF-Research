---
title: NEC antenna modelling in practice — NEC-2/4 on macOS (PyNEC, xnec2c, 4nec2, EZNEC, MMANA-GAL), card decks, segmentation, ground models, 433 MHz dipole and Yagi decks cross-checked against an independent MoM
domain: 16-simulation-tools
slug: nec-antenna-modelling
tags: [nec2, optimisation, nelder-mead, differential-evolution, particle-swarm, tolerance-analysis, nec4, nec2++, pynec, necpp, xnec2c, 4nec2, eznec, mmana-gal, mininec, card-deck, gw, ex, gn, ek, rp, segmentation, extended-kernel, sommerfeld, average-gain-test, yagi, dipole, method-of-moments]
prerequisites: [../08-antennas/antenna-simulation-nec-openems.md, ../08-antennas/dipoles-and-monopoles.md, em-solvers-fdtd-mom-fem.md]
related: [../08-antennas/yagi-uda-and-log-periodic.md, ../08-antennas/antennas-on-rockets.md, ../09-propagation-link-budget/two-ray-ground-reflection.md, simulation-validation.md, installing-tools-macos.md, python-rf-toolkit.md]
level: mixed
confidence: high
last_updated: 2026-10-14
---

# NEC antenna modelling in practice

The physics of the method of moments and the NEC modelling rules are on [antenna simulation (08)](../08-antennas/antenna-simulation-nec-openems.md); this page is the **hands-on companion**: how to run NEC on a Mac, how to write and read a card deck, how the ground options behave, and what an independent cross-check of NEC-2 against this repository's own MoM actually showed.

## Questions this page answers
- How do I run NEC-2 on a Mac without Windows?
- What do the GW, GE, GN, EK, EX, FR, RP cards mean, and what does a minimal deck look like?
- How do I model a 433 MHz dipole and a DL6WU Yagi, and what numbers should I expect?
- Which ground model should I use (free space, perfect, reflection-coefficient, Sommerfeld)?
- My NEC average-gain test says 0.96 for a lossless Yagi — is my model wrong?
- Does NEC agree with another independent code, and by how much?
- When should I stop using NEC and switch to openEMS?
- Can an optimiser (Nelder–Mead, genetic/differential evolution, particle swarm) design my Yagi, and which one should I use?
- Why did my optimiser find a 10 dBi 3-element Yagi with a 4 Ω feed?

## TL;DR
- **On macOS, use PyNEC** (`pip install PyNEC`; NEC2++ engine with Python bindings, arm64 wheels) for scripting and sweeps; the Windows GUIs (4nec2, EZNEC v7 — now free [4], MMANA-GAL) need a Windows PC/VM because the Homebrew Wine cask was disabled in Sept 2026; xnec2c (GTK) can be built from source (not tried here).
- **Minimal deck**: `CM/CE` comments → `GW` wires → `GE` (ground flag) → `GN` ground → `EK` (optional extended kernel) → `EX` source → `FR` frequency → `RP` pattern → `EN` [1].
- **Cross-check results** (`tools/verify/sim_nec_vs_mom.py`, PyNEC vs this repository's Galerkin MoM, pre-registered):
  | Case | NEC-2 | Own MoM | Pre-registered | Verdict |
  |---|---|---|---|---|
  | 433 MHz dipole, 2 mm wire: resonant length | 326.5 mm | 327.9 mm | within 1 mm | **miss (−1.5 mm, 0.46 %)** |
  | same: R at resonance / gain | 71.9 Ω / 2.135 dBi | 72.1 Ω / 2.136 dBi | 1 Ω / — | pass |
  | thin dipole (a = 10⁻⁴λ) | 0.4835λ, 72.0 Ω | 0.4838λ, 72.0 Ω | 0.2 % / 1 Ω | pass |
  | DL6WU 11-el 433 MHz Yagi gain / F/B | 14.31 dBi / 17.1 dB | 14.20 dBi / 16.3 dB | 0.2 dB | pass (+0.11 dB) |
  | same: feed impedance | 49.1 + j4.1 Ω | 52.2 + j0 Ω | R within 3 Ω | **miss (−3.1 Ω)** |
  | λ/4 monopole on perfect ground | 42.5 + j24.6 Ω, 5.19 dBi, AGT 2.000 | 42.8 + j22.8 Ω, 5.19 dBi | ½ dipole | pass |
- The two misses are ~0.5 % geometry-level differences between two feed/kernel discretisations — smaller than what a real build's tolerances and a bench trim do, but a reminder to **trim on the bench**.
- **Two traps found in PyNEC**: `set_extended_thin_wire_kernel(True)` is **silently ignored unless called after `geometry_complete()`**; the reported **average gain depends on where the φ grid starts** (0.958 with the Yagi beam on the first φ column, 1.004 when shifted by 90°; our own periodic integration of the same pattern gives 0.999 either way). Three more traps were hit by W5-S12 and checked in `tools/verify/s17_pynec_quirks.py` (see [Common mistakes](#common-mistakes--misconceptions)). With no `rp_card` you must call `xq_card(0)`, or nothing is solved. A wire touching a ground plane needs `geometry_complete(1)`. `get_e_theta()`/`get_e_phi()` come back flat with θ varying fastest.
- **Optimisation** (`tools/verify/sim2_nec_yagi_optimise.py`, Example 4). A 3-element 433 MHz Yagi was optimised with PyNEC and three methods: Nelder–Mead, differential evolution and particle swarm.
  - With F/B ≥ 15 dB and VSWR ≤ 1.5 on a direct 50 Ω feed across 433.05–434.79 MHz, the best design gives **8.55 dBi** on a 0.45λ boom.
  - With no constraints, the optimiser finds a **9.9 dBi superdirective** design whose feed impedance is 3.8 + j56 Ω.
  - Differential evolution and particle swarm agree within 0.02 dB. Two of five Nelder–Mead starts stopped at least 0.3 dB short.
  - A build tolerance of ±1 mm on lengths and ±2 mm on spacings costs less than 0.11 dB.
- **Ground**: Sommerfeld/Norton (`GN 2`) and the reflection-coefficient approximation (`GN 0`) agree above ≈ 0.5λ height but differ enormously close to the ground (433 MHz dipole at 0.03λ: 250 − j510 Ω vs 59 + j64 Ω) — use GN 2 for anything within a few tenths of a wavelength of the soil.

## Intuition (no math)
A NEC deck is a recipe: "here are the wires, here is the ground, drive this segment with 1 V at this frequency, and tell me the pattern". NEC then chops each wire into the number of segments you asked for, assumes a smooth current shape on each, and forces the electric field along every wire to be zero (a perfect conductor). The answer is the current on every segment; the feed impedance is 1 V divided by the feed current, and the pattern is what those currents radiate.

Everything that goes wrong is one of four things: the geometry is not what you built (wrong lengths, missing boom/mast/cable), the discretisation is outside NEC's rules (too few/many segments, too fat a wire), the ground is modelled with the wrong method, or the post-processing (pattern grid, average gain) is misleading. The cross-check below touched all four.

## The math

### Level 1 — what NEC solves
For thin wires NEC-2 solves the electric-field integral equation (EFIE) for the axial current $I(s)$:
$$ -\hat s\cdot\mathbf E^{inc}(s) = \frac{-j\eta}{4\pi k}\int_L I(s')\left[k^2\,\hat s\cdot\hat s' - \frac{\partial^2}{\partial s\,\partial s'}\right]\frac{e^{-jkR}}{R}\,ds' $$
with $R$ the distance from the source point on the wire axis to the observation point on the wire surface (the "thin-wire" or reduced kernel), $k = 2\pi/\lambda$, $\eta \approx 377\ \Omega$. Discretising gives the matrix equation $\mathbf Z\mathbf I = \mathbf V$ ([MoM, em-solvers page](em-solvers-fdtd-mom-fem.md#the-math)).

### Level 1½ — what the card deck becomes, algebra only
The algebra-only picture of MoM is on [08 antenna simulation, Level 1½](../08-antennas/antenna-simulation-nec-openems.md#level-1½--mom-as-simultaneous-equations-algebra-only): N segments, N unknown currents, an N × N mutual-impedance matrix, and one solve. The cards map onto it directly:
- `GW` cards fix the segments, and hence N;
- `EX` puts the 1 V source into one row of the voltage vector;
- `FR` sets the frequency at which the matrix is built;
- `RP` sums the solved currents' fields.

For the 11-element Yagi of Example 2 (21 segments per element), N = 231. The matrix has 231² ≈ 53 000 entries, and one PyNEC solve takes milliseconds. Example 4's optimiser therefore afforded about 26 000 of them in about 2 minutes.

### Level 2 — NEC-2's discretisation
- **Basis**: on segment $j$, $I_j(s) = A_j + B_j\sin k(s-s_j) + C_j[\cos k(s-s_j)-1]$; two of the three constants are eliminated by forcing current and charge continuity with the neighbours, leaving one unknown per segment [1].
- **Testing**: point matching at segment centres (collocation) — unlike our verification MoM, which uses triangle basis functions with Galerkin testing and a mixed-potential kernel. Agreement between two such different discretisations is meaningful evidence that both are right [7].
- **Source**: `EX 0` is an "applied-field" voltage source — a field $V/\Delta$ over the whole source segment; the feed gap is therefore one segment long. Our MoM puts a delta-gap at a node. At 2 mm diameter this difference in the effective gap is the most plausible cause of the 1.5 mm resonance offset.
- **Extended kernel (EK)**: adds the next term in the expansion of the exact ring-current field, allowing segment length/radius ratios down to ≈ 2 (0.5 absolute minimum) instead of ≈ 8 [1].
- **Pattern & average gain**: the far field is a sum over segments; the "average gain" is $\frac{1}{4\pi}\iint G\,d\Omega$ evaluated by a quadrature over the RP grid. For a lossless free-space model it must be 1 (2 over perfect ground).

### Level 3 — ground models
| GN type | Method | Valid for |
|---|---|---|
| `GN -1` | free space | antennas far from ground (≫ λ), rocket in flight |
| `GN 1` | perfect ground by image theory | ground planes, idealised radials |
| `GN 0` | finite ground via Fresnel reflection coefficients in the far field and an image-based near interaction | structures ≳ 0.2–0.5λ above ground |
| `GN 2` | Sommerfeld/Norton integrals for the near-field interaction (NEC-2 needs SOMNEC; NEC2++ computes it internally) | anything close to lossy ground; wires may not penetrate the ground in NEC-2 (NEC-4 allows buried wires) |

The far-field pattern over real ground uses the plane-wave reflection coefficient either way — so ground-wave/space-wave behaviour at grazing angles is idealised; see [two-ray reflection](../09-propagation-link-budget/two-ray-ground-reflection.md).

## Design equations & rules of thumb

| Card | Fields (NEC-2 User's Guide [1]) | Notes |
|---|---|---|
| `GW tag nseg x1 y1 z1 x2 y2 z2 rad` | straight wire, metres | same end points ⇒ connected |
| `GS 0 0 scale` | scale all dimensions | handy for inches/mm |
| `GE flag` | end geometry; 0 free space, 1 ground image present | must precede GN/EX |
| `GN type nrad 0 0 epsr sigma` | ground (table above) | average ground εr ≈ 13, σ ≈ 0.005 S/m |
| `EK 0` | extended thin-wire kernel on | after GE; needed if Δ/a < 8 |
| `LD 5 tag seg1 seg2 sigma` | wire conductivity loss | turn on for efficiency; AGT < 1 then |
| `EX 0 tag seg 0 Vr Vi` | voltage source on one segment | centre segment of an odd count |
| `TL`, `NT` | transmission line / 2-port network between segments | phasing lines, baluns |
| `FR 0 n 0 0 f_MHz df_MHz` | frequency sweep | |
| `RP 0 nth nph 1000 th0 ph0 dth dph` | pattern; `1000` = print format with average gain | offset φ0 from the main beam (trap above) |

| Rule (from [1] and the 08 page) | Value |
|---|---|
| Segment length Δ | λ/20–λ/10 (λ/20 near feeds, junctions) ; Δ > 10⁻³λ |
| Δ / radius | > 8 thin kernel; ≥ 2 with EK |
| Same-diameter elements | NEC-2 handles tapered/stepped tubes badly (NEC-4 or EZNEC's Leeson correction) |
| Average gain test (AGT) | 1.00 ± 0.02 free space lossless; 2.00 over perfect ground |
| Sommerfeld needed | height < ~0.2–0.5λ above lossy ground |

## Worked examples

### 1 — 433 MHz half-wave dipole (2 mm wire)
```
CM 433 MHz dipole, 2 mm diameter wire, free space
CE
GW 1 41 0 0 -0.16323 0 0 0.16323 0.001
GE 0
GN -1
EX 0 1 21 0 1.0 0
FR 0 1 0 0 433.0 0
RP 0 91 72 1000 0 90 2 5
EN
```
Resonance (41 segments, Δ/a = 8): **L = 326.5 mm, Z = 71.9 Ω, G = 2.135 dBi, AGT 0.9998**. Segmentation study at L = 328 mm (PyNEC):

| Segments | Δ/a | Kernel | Z (Ω) |
|---|---|---|---|
| 11 | 29.8 | thin | 72.28 + j2.25 |
| 21 | 15.6 | thin | 72.71 + j3.20 |
| 41 | 8.0 | thin | 73.06 + j3.83 |
| 81 | 4.0 | thin (outside rule) | 73.30 + j4.07 |
| 81 | 4.0 | extended | 73.11 + j3.50 |
| 161 | 2.0 | extended | 73.10 + j3.03 |

The thin kernel keeps drifting when Δ/a falls below 8; with EK the resistance is converged to 0.01 Ω and the reactance to ~0.5 Ω — a practical demonstration of the Δ/a rule. For a real build the result is "cut to 327 ± 2 mm and trim to resonance on a VNA" ([NanoVNA](../17-test-measurement/nanovna-librevna-practical.md)).

### 2 — DL6WU 11-element 433 MHz Yagi (6 mm elements, 1.72 m boom)
Element lengths and positions from `tools/verify/ant_yagi.py` (`dl6wu_design(2.3, …)`), driven element re-resonated as a plain dipole:
```
CM DL6WU 433 MHz, 6 mm elements, non-metallic boom
CE
GW 1 21 0.0000 0 -0.1681 0.0000 0 0.1681 0.003
GW 2 21 0.1385 0 -0.1676 0.1385 0 0.1676 0.003
GW 3 21 0.1904 0 -0.1486 0.1904 0 0.1486 0.003
GW 4 21 0.3150 0 -0.1465 0.3150 0 0.1465 0.003
GW 5 21 0.4639 0 -0.1445 0.4639 0 0.1445 0.003
GW 6 21 0.6370 0 -0.1426 0.6370 0 0.1426 0.003
GW 7 21 0.8308 0 -0.1410 0.8308 0 0.1410 0.003
GW 8 21 1.0385 0 -0.1396 1.0385 0 0.1396 0.003
GW 9 21 1.2566 0 -0.1383 1.2566 0 0.1383 0.003
GW 10 21 1.4851 0 -0.1373 1.4851 0 0.1373 0.003
GW 11 21 1.7240 0 -0.1363 1.7240 0 0.1363 0.003
GE 0
GN -1
EK 0
EX 0 2 11 0 1.0 0
FR 0 1 0 0 433.0 0
RP 0 91 180 1000 0 90 2 2
EN
```
| Model | G (dBi) | F/B (dB) | Z_in (Ω) | AGT |
|---|---|---|---|---|
| NEC-2, 21 seg/el, thin kernel (Δ/a = 5.3) | 14.35 | 17.5 | 47.6 + j6.8 | 1.004 |
| NEC-2, 21 seg/el, EK | 14.31 | 17.1 | 48.7 + j5.1 | 1.004 |
| NEC-2, 61 seg/el, EK | 14.31 | 17.1 | 49.1 + j4.1 | 1.005 |
| Own Galerkin MoM (`ant_yagi.py`) | 14.20 | 16.3 | 52.2 + j0.0 | 1.001 |
| DL6WU empirical gain formula (9.2 + 3.39 ln(boom/λ) dBd, boom 2.49λ) | 14.44 (12.29 dBd) | — | — | — |

Gain agrees to 0.11 dB — the quantity the link budget needs ([link budget](../09-propagation-link-budget/link-budget-methodology.md)). The feed impedance differs by ~3 Ω and ~4 Ω of reactance, consistent with NEC resonating the same dipole ≈ 1.5 mm shorter (Example 1); either way a gamma/hairpin match or a 1–2 mm trim absorbs it.

### 3 — the ground choice (horizontal 433 MHz dipole over average ground εr = 13, σ = 5 mS/m)
| Height | Z with GN 2 (Sommerfeld) | Z with GN 0 (refl. coeff.) |
|---|---|---|
| 0.02 m (0.03λ) | 250 − j510 Ω | 59 + j64 Ω |
| 0.05 m (0.07λ) | 55 + j8 Ω | 44 + j10 Ω |
| 0.10 m (0.14λ) | 60 + j16 Ω | 57 + j20 Ω |
| 0.35 m (0.51λ) | 67 − j9 Ω | 68 − j9 Ω |
| 2.0 m (2.9λ) | 73.7 − j0.6 Ω | 73.7 − j0.5 Ω |

A landed rocket's antenna lying in grass is the 0.03λ row: only the Sommerfeld model is credible, and it predicts a badly mismatched antenna — one reason the post-landing link is so much weaker than free-space estimates ([antennas on rockets](../08-antennas/antennas-on-rockets.md)). At 2 m the dipole's elevation pattern has its first lobe at 5° (7.8 dBi, the ground-reflection "+6 dB" of [two-ray](../09-propagation-link-budget/two-ray-ground-reflection.md) minus reflection loss) and only 3.4 dBi at 2° — the lobing that the ground station sees as the rocket descends.

### 4 — letting an optimiser design the Yagi (Nelder–Mead vs differential evolution vs particle swarm)
**Problem.** A hand-held 3-element Yagi for the 433 MHz ground station: 4 mm aluminium rod, non-conducting boom, free space, 21 segments per element, driven element fed directly with 50 Ω (no gamma/hairpin match). Five variables: reflector, driven and director lengths, and the two spacings, bounded to 0.47–0.53λ, 0.42–0.50λ, 0.40–0.48λ and 0.08–0.30λ. Objective, evaluated at 433.05, 433.92 and 434.79 MHz:
$$J = -G_{min} + 1.0\,\max(0,\ 15 - FB_{min}) + 10\,\max(0,\ VSWR_{max} - 1.5)$$
($G$ = boresight gain in dBi, FB = front-to-back at 180°). The penalties turn the specification into one number. Their weights decide how hard the optimiser pushes against each limit.

| Method (scipy / own code) | Evaluations | J | G_min | FB_min | VSWR_max | Design (L_ref / L_drv / L_dir; s_ref / s_dir, mm) |
|---|---|---|---|---|---|---|
| Nelder–Mead, 5 random starts | 413–927 (mean 663) | −8.35, −7.23, −8.48, −8.54, −7.89 | 7.23–8.54 dBi | 15.0 dB | 1.50 | best: 332.8 / 315.2 / 290.9; 169.4 / 140.3 |
| Differential evolution (`scipy.optimize.differential_evolution`) | 19 626 | −8.548 | 8.55 dBi | 15.0 dB | 1.50 | 332.8 / 315.7 / 292.5; 177.1 / 135.4 (boom 0.452λ), Z 33.8 + j1.4 Ω |
| Particle swarm (30 particles × 120 iterations, own 40-line code) | 3 630 | −8.526 | 8.53 dBi | 15.0 dB | 1.50 | 333.9 / 314.2 / 289.7; 162.7 / 144.7 |
| DE, gain only (no F/B, no match) | 16 500 | — | **9.90 dBi** | 6.5 dB | 30.4 | 337.6 / 345.4 / 307.5; **55.3** / 195.9, Z **3.8 + j55.8 Ω** |

Against the pre-registration in the script header:
- **Y1 missed, high.** Expected 7.5–8.5 dBi unconstrained and 6.5–7.8 dBi constrained. Found 9.90 and 8.55 dBi. The unconstrained optimum is a superdirective close-spaced reflector sitting on the 0.08λ bound: its feed resistance is 3.8 Ω.
- **Y2 passed.** DE and PSO agree within 0.02 dB. Two of five Nelder–Mead starts ended 0.66 and 1.32 dB short, in local optima with a long reflector.
- **Y3 half missed.** DE needed 30× the evaluations of one Nelder–Mead run, PSO only 5.5× (the pre-registration said ≥ 10× for both).
- **Y4 passed.** Over 500 builds with lengths ±1 mm and spacings ±2 mm, the 95th-percentile gain loss was 0.07 dB (worst 0.11 dB). VSWR stayed below 1.55 in 95 % of builds and below 2 in all of them.
- **Y5 missed as worded.** The unconstrained optimum does exceed the 9 dBi that [antennas on rockets](../08-antennas/antennas-on-rockets.md) Example 1 assumes for a 3-element hand-held Yagi. The practical, matched design gives 8.5 dBi, so the 9 dBi assumption is about 0.5 dB optimistic for a buildable 3-element Yagi.

A post-hoc check (not pre-registered) settles whether the supergain is real. With aluminium loss (`LD 5`, σ = 3.5 × 10⁷ S/m) the 9.9 dBi design keeps 9.68 dBi (efficiency 0.949 from the AGT). The constrained design loses only 0.02 dB. Both lossless AGTs are 0.999. So the supergain survives conductor loss in NEC. What kills it in practice is its 3.8 Ω feed, which needs a high-ratio match whose own loss and narrow bandwidth NEC does not see, and its sensitivity to rain, hands and the boom. **The constraint set is where the engineering happens; the optimiser only exploits whatever you leave out.**

Rules that follow:
- Use a **global, population-based method (DE or PSO) for the first pass** and a local method (Nelder–Mead or `polish=True`) to finish. A single Nelder–Mead run from a random start is a lottery here: 2 of 5 starts failed.
- **Specify the whole band, F/B and match in the objective.** Otherwise the optimiser finds unbuildable designs (supergain, 4 Ω feeds, single-frequency optima).
- **Run a tolerance Monte Carlo before believing the optimum.** Here it was robust; superdirective designs are not.
- **Re-check the winner with the AGT**, and if possible a finer segmentation or a second code, because optimisers drive models into corners where discretisation error matters.
- GUIs: 4nec2 has a built-in optimiser (Windows); with PyNEC the whole loop is about 100 lines of Python. Each NEC evaluation here took about 2 ms per frequency.

### 5 — scripting with PyNEC (sweep + AGT done right)
```python
import numpy as np, PyNEC
def dipole(L, f_mhz=433.0, a=1e-3, nseg=41, ek=False):
    c = PyNEC.nec_context(); g = c.get_geometry()
    g.wire(1, nseg, 0, 0, -L/2, 0, 0, L/2, a, 1.0, 1.0)
    c.geometry_complete(0)                       # GE
    if ek: c.set_extended_thin_wire_kernel(True) # EK - MUST come after geometry_complete()
    c.gn_card(-1, 0, 0, 0, 0, 0, 0, 0)            # free space
    c.ex_card(0, 1, nseg//2 + 1, 0, 1.0, 0, 0, 0, 0, 0)
    c.fr_card(0, 1, f_mhz, 0)
    # theta 0..180 step 2, phi 90..448 step 2 (start the phi grid AWAY from the main beam)
    c.rp_card(0, 91, 180, 0, 0, 0, 1, 0.0, 90.0, 2.0, 2.0, 0.0, 0.0)
    rp = c.get_radiation_pattern(0)
    return complex(c.get_input_parameters(0).get_impedance()[0]), np.max(rp.get_gain()), rp.get_average_power_gain()
from scipy.optimize import brentq
Lres = brentq(lambda L: dipole(L)[0].imag, 0.30, 0.34)   # -> 0.3265 m
```
`tools/verify/sim_nec_vs_mom.py` wraps this for all four cases above and prints PASS/MISS against the pre-registered tolerances.

## Practical notes
- **Model the real thing**: element diameter (6 mm tube vs 2 mm rod changes resonance by ~1 %), a metal boom (DL6WU boom correction, or insulate the elements), the feed cable (common-mode currents — add a choke or model the coax outer as a wire), the mast.
- **Rocket antennas**: NEC can model a monopole or dipole *on a conducting airframe* (airframe as a wire grid or a thick wire) in free space; it cannot model fibreglass/carbon-fibre nose cones, radomes or PCB substrates — use [openEMS](openems-workflow.md).
- **Tapered/telescoping elements**: NEC-2 mis-predicts them (junction of different radii); use constant-diameter equivalents, EZNEC's Leeson correction, or NEC-4.
- **Losses**: add `LD 5` (conductivity) to see efficiency; then AGT < 1 by exactly the efficiency — a useful check that the loss is where you think.
- **GUIs**: 4nec2 (Windows; optimiser, AGT, sweeps), EZNEC Pro+ v7 (free since the author's retirement, NEC-2D engine built in, can call external NEC-4.2/NEC-5; no support [4]), MMANA-GAL (MININEC engine: weaker near ground and at junctions), xnec2c (Linux/BSD GTK; macOS needs a source build).

## Common mistakes & misconceptions
- **Switching on EK in PyNEC before `geometry_complete()`** — it is silently ignored; results are thin-kernel. (Found and fixed while writing the verification script; the deck order GW…GE, then EK is the same rule.)
- **Asking for the impedance without an `RP` or `XQ` card.** PyNEC, like a NEC deck, only runs the solution when an execute card arrives. After `fr_card` alone, `get_input_parameters(0)` returns `None` (an AttributeError on `.get_impedance()`). Call `c.xq_card(0)` for impedance-only sweeps. (W5-S12; `s17_pynec_quirks.py`.)
- **`geometry_complete(0)` for a wire that touches the ground plane.** GE 0 tells NEC that no ground plane is present, so the current at the wire's base is not joined to its image. A 433 MHz λ/4 monopole over perfect ground then gives ≈ 43 − j1690 Ω instead of ≈ 36 + j0.4 Ω (half the dipole's 72 Ω). Use `geometry_complete(1)` whenever an end sits at z = 0 over `GN 1` or a Sommerfeld ground. (W5-S12; script.)
- **Reshaping `get_e_theta()` / `get_e_phi()` the wrong way.** They are flat arrays with **θ varying fastest** (all θ for the first φ, then the next φ). Use `np.array(rp.get_e_theta()).reshape(nph, nth).T` to get a (θ, φ) grid. A row-major `reshape(nth, nph)` silently scrambles the pattern and can flip the sign of a polarisation check. (W5-S12 hit this in an axial-ratio test; script.)
- **Trusting the printed average gain blindly** — NEC2++'s value depends on the φ-grid start when the main beam sits on the first column (0.958 vs 1.004 for the same Yagi); integrate the pattern yourself or offset the grid. A low AGT can be a post-processing artefact, not a model error.
- **Using `GN 0` for an antenna near the ground** — errors of hundreds of ohms below ~0.1λ.
- **"More segments are always better"** — with the thin kernel, Δ/a < 8 degrades accuracy (Example 1).
- **Believing a 0.5 % disagreement between codes is a bug** — two correct discretisations of different feed models legitimately differ at that level for fat wires; physical feed gaps are neither ideal model.
- **"The optimiser found 10 dBi from three elements, so the design is better."** It found a superdirective, 4 Ω-feed design because the objective did not forbid it (Example 4). Put match, F/B and bandwidth in the objective.
- **Trusting one local-optimiser run.** Nelder–Mead from random starts ended up to 1.3 dB short in 2 of 5 runs (Example 4).
- **Comparing NEC gain (dBi) with DL6WU's formula (dBd)** — convert (dBi = dBd + 2.15).

## How to simulate / verify
- `python3 tools/verify/sim_nec_vs_mom.py` (≈ 15 s): NEC-2 vs own MoM on the dipole, thin dipole, Yagi and monopole with pre-registered tolerances; prints the segmentation study.
- `python3 tools/verify/ant_mom_general.py`, `ant_yagi.py` (W1-A6): the independent MoM.
- `python3 tools/verify/sim2_nec_yagi_optimise.py` (≈ 2.5 min): Example 4 — Nelder–Mead ×5, differential evolution and particle swarm on a 3-element 433 MHz Yagi, tolerance Monte Carlo, post-hoc loss/AGT check; results in `sim2_nec_yagi_results.txt`.
- For a new design: (1) AGT = 1 in free space, lossless; (2) double segments → Z within 1 Ω, G within 0.1 dB; (3) one cross-code or measured check (NanoVNA S11 of the built antenna).

## Open questions / gaps
- The 1.5 mm resonance offset between NEC-2 and our MoM for a 2 mm wire is not attributed conclusively (feed model vs kernel); a measured 433 MHz dipole cut to both lengths would settle which is closer to reality.
- NEC-4.2 (licensed from LLNL) and NEC-5 were not tested; buried radials and insulated wires therefore remain unverified here.
- xnec2c on macOS not built.
- Example 4's optimum has not been built and measured. The superdirective variant's loss with a real matching network was not modelled: NEC's `LD` cards model conductor loss, not a lumped matching network's loss.

## Sources
1. G. J. Burke and A. J. Poggio, *Numerical Electromagnetics Code (NEC) — Method of Moments*, LLNL UCID-18834, 1981; Part I (theory: current expansion, extended kernel, Sommerfeld ground), Part III (User's Guide: card formats GW/GE/GN/EK/EX/LD/TL/NT/FR/RP, modelling guidelines). https://www.nec2.org/ (manual)
2. T. Molteno et al., NEC2++ / python-necpp (PyNEC), https://github.com/tmolteno/python-necpp ; PyPI `PyNEC` 2.3.4 — API used here (nec_context, wire, gn_card, ex_card, rp_card, set_extended_thin_wire_kernel). (tool documentation)
3. G. J. Burke, *Numerical Electromagnetics Code — NEC-4.2, Method of Moments*, LLNL, 2011 — buried wires, improved junctions (licensed). (manual)
4. R. Lewallen (W7EL), EZNEC website, https://www.eznec.com/ — EZNEC Pro+ v7.0 free, internal NEC-2D engine, optional external NEC-4.2/NEC-5, no support. (vendor)
5. L. B. Cebik (W4RNL), "When not to use NEC" and NEC-2 modelling articles, https://antenna2.github.io/cebik/ (expert articles)
6. G. Hoch (DL6WU), "Extremely long Yagi antennas," *VHF Communications* 3/1982 — spacing/length tables used by `ant_yagi.py`. (magazine, design method)
7. R. F. Harrington, *Field Computation by Moment Methods*, Macmillan, 1968; W. C. Gibson, *The Method of Moments in Electromagnetics*, 2nd ed., CRC, 2014 — Galerkin vs point matching. (textbooks)
8. This repository: `tools/verify/sim_nec_vs_mom.py` (W3-C2), `tools/verify/ant_mom_wire.py`, `ant_mom_general.py`, `ant_yagi.py` (W1-A6). (verification)
9. R. Storn, K. Price, "Differential evolution — a simple and efficient heuristic for global optimization over continuous spaces," *J. Global Optimization* 11, 341–359, 1997; J. Kennedy, R. Eberhart, "Particle swarm optimization," *Proc. IEEE ICNN*, 1995; M. Clerc, J. Kennedy, "The particle swarm — explosion, stability, and convergence," *IEEE Trans. Evol. Comput.* 6(1), 58–73, 2002 (constants used); J. A. Nelder, R. Mead, *Computer Journal* 7(4), 308–313, 1965; D. S. Weile, E. Michielssen, "Genetic algorithm optimization applied to electromagnetics: a review," *IEEE Trans. AP* 45(3), 343–353, 1997. (peer-reviewed)
10. This repository: `tools/verify/sim2_nec_yagi_optimise.py` and `sim2_nec_yagi_results.txt` (W5-S11). (verification)
