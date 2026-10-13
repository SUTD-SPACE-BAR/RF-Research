# 16-simulation-tools — Simulation tools and calculators

Scope: the practical toolbox for simulating RF waveforms, circuits, transmission lines, EM effects and
antennas, and for predicting link and radar performance — which tool to use for which problem, how the
underlying numerical methods work (MNA/SPICE, harmonic balance, FDTD, MoM, FEM), how to install and run
the free tools on Marcus's Apple-Silicon Mac (ngspice, KiCad's libngspice, PyNEC, openEMS, scikit-rf),
and how to verify and validate results. Every tool claim marked "tested" was run on this machine
(2026-09-27/29) by `tools/verify/sim_*.py`; the KB's own calculators live in `tools/rfcalc/`
(142 pytest tests, CLI `python3 -m rfcalc`; see [tools/README.md](../../tools/README.md)). Antenna-physics
aspects of NEC/openEMS are in [08-antennas/antenna-simulation-nec-openems](../08-antennas/antenna-simulation-nec-openems.md).

## Reading order (beginner → advanced)
1. [tool-landscape-overview](tool-landscape-overview.md) — decision table: problem → tool, fidelity, learning curve, macOS support.
2. [installing-tools-macos](installing-tools-macos.md) — exact tested commands; what worked (ngspice, PyNEC, openEMS), what did not (Wine, LTspice pkg), Qucs-S Gatekeeper note.
3. [impedance-and-rf-calculators](impedance-and-rf-calculators.md) — KiCad/Saturn/JLCPCB/IPC-2141/rfcalc vs a 2-D field solver; soldermask and copper-thickness effects.
4. [python-rf-toolkit](python-rf-toolkit.md) — scikit-rf (Touchstone, cascades, calibration, TDR, vector fitting → SPICE), other Python RF libraries, rfcalc.
5. [spice-circuit-simulation](spice-circuit-simulation.md) — ngspice/LTspice/Qucs-S/Xyce; AC, noise, transient, `.sp`; L-match, Butterworth, Colpitts, pad-NF examples; RF limits.
6. [nec-antenna-modelling](nec-antenna-modelling.md) — NEC-2 on macOS (PyNEC), card decks for a 433 MHz dipole and a DL6WU Yagi, ground models, cross-check vs own MoM.
7. [em-solvers-fdtd-mom-fem](em-solvers-fdtd-mom-fem.md) — method comparison, free and commercial solvers, student limits, accuracy pitfalls.
8. [openems-workflow](openems-workflow.md) — openEMS install, meshing, ports, NF2FF; microstrip and 2.45 GHz patch runs with mesh studies.
9. [rf-circuit-simulators-harmonic-balance](rf-circuit-simulators-harmonic-balance.md) — HB vs transient (own HB demo), ADS, AWR, QucsStudio, SimSmith, RFSim99.
10. [simulation-validation](simulation-validation.md) — V&V discipline, convergence/GCI, benchmarks, cross-solver comparison, measurement correlation, de-embedding.

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [tool-landscape-overview](tool-landscape-overview.md) | which tool for which RF problem; Mac vs Windows; fidelity ladder | intro | high |
| [installing-tools-macos](installing-tools-macos.md) | tested install commands and outcomes on Apple Silicon | intro | high |
| [spice-circuit-simulation](spice-circuit-simulation.md) | SPICE analyses, MNA, S-parameters in ngspice, noise traps, example netlists | mixed | high |
| [rf-circuit-simulators-harmonic-balance](rf-circuit-simulators-harmonic-balance.md) | harmonic balance, shooting, envelope; commercial/free RF simulators | mixed | medium |
| [em-solvers-fdtd-mom-fem](em-solvers-fdtd-mom-fem.md) | FDTD/FIT/MoM/FEM/2.5-D compared; solver catalogue; pitfalls | mixed | medium |
| [nec-antenna-modelling](nec-antenna-modelling.md) | NEC-2 practice, decks, grounds, PyNEC traps, NEC vs own MoM | mixed | high |
| [openems-workflow](openems-workflow.md) | openEMS end-to-end with two validated runs | mixed | high |
| [python-rf-toolkit](python-rf-toolkit.md) | scikit-rf and friends; rfcalc | mixed | high |
| [impedance-and-rf-calculators](impedance-and-rf-calculators.md) | calculator comparison vs field solver; rfcalc CLI | intro | high |
| [simulation-validation](simulation-validation.md) | verification & validation methods with this KB's worked evidence | mixed | high |

## Domain FAQ (top questions → page#section)
- Which tool should I use for a PCB antenna / a Yagi / a filter / a link budget? → [tool-landscape-overview](tool-landscape-overview.md#design-equations--rules-of-thumb--the-decision-table)
- Do I need to install ngspice if I have KiCad? → [installing-tools-macos](installing-tools-macos.md#2--the-kicad-route-no-install-at-all)
- How do I install openEMS on an M-series Mac? → [installing-tools-macos](installing-tools-macos.md#4--openems-from-source-tested-25-min-total), [openems-workflow](openems-workflow.md)
- Why did macOS say Qucs-S could not be verified? → [installing-tools-macos](installing-tools-macos.md#5--qucs-s-and-gatekeeper-what-happened-here)
- How do I get S-parameters out of ngspice? → [spice-circuit-simulation](spice-circuit-simulation.md#a--433-mhz-l-match-125-ω-pa-side-load-to-50-ω-s-parameters)
- Why is my SPICE noise figure wrong? → [spice-circuit-simulation](spice-circuit-simulation.md#d--noise-analysis-of-a-6-db-π-attenuator-does-spice-give-nf--loss)
- What does a NEC deck for a 433 MHz dipole/Yagi look like? → [nec-antenna-modelling](nec-antenna-modelling.md#worked-examples)
- My NEC average gain is 0.96 for a lossless antenna — bug? → [nec-antenna-modelling](nec-antenna-modelling.md#common-mistakes--misconceptions)
- How fine must an openEMS mesh be? → [openems-workflow](openems-workflow.md#design-equations--rules-of-thumb)
- Why do calculators disagree on my 50 Ω CPWG width? → [impedance-and-rf-calculators](impedance-and-rf-calculators.md#2--cpwg-the-thickness-and-mask-effect-dominates)
- How do I turn a Touchstone file into a SPICE model? → [python-rf-toolkit](python-rf-toolkit.md#5--touchstone--spice-vector-fitting-checked-in-ngspice)
- When do I need harmonic balance instead of SPICE transient? → [rf-circuit-simulators-harmonic-balance](rf-circuit-simulators-harmonic-balance.md#1--why-hb-wins-for-a-high-q-multiplier-own-python-hb-tested)
- How do I know my simulation is right? → [simulation-validation](simulation-validation.md)

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
Taflove & Hagness (FDTD); Harrington, Gibson (MoM); Jin (FEM); Burke & Poggio NEC-2 manual; Kundert/White/Sangiovanni-Vincentelli and Maas (harmonic balance); Nagel SPICE2 and the ngspice manual; scikit-rf paper and docs; openEMS docs; Oberkampf & Roy, ASME V&V 20, Roache/Celik (V&V and GCI).

## Verification scripts and tools (this domain)
- `tools/rfcalc/` — consolidated calculators + `tests/` (142 tests).
- `tools/verify/sim_ngspice_examples.py` — ngspice CLI + KiCad libngspice: L-match `.sp`, Butterworth LPF, Colpitts, pad NF, vector-fit → SPICE (all pass).
- `tools/verify/sim_nec_vs_mom.py` — PyNEC vs own Galerkin MoM (6 pass, 2 pre-registered misses reported).
- `tools/verify/sim_openems_msl.py`, `sim_openems_patch.py` — openEMS microstrip and patch with mesh studies (results in `sim_openems_results.txt`).
- `tools/verify/sim_harmonic_balance.py` — own harmonic-balance solver vs transient.

## Known gaps
- Not run on this machine: LTspice, Xyce, Qucs-S/QucsatorRF (installed but unsigned; never used), MEEP, Elmer, Palace, OpenParEM, gprMax, Sonnet Lite, any commercial solver.
- No simulation-vs-measurement correlation of Marcus's own hardware yet (first NanoVNA comparison is the top validation priority).
- xnec2c not built on macOS; NEC-4 untested.
- Open discrepancies: NEC-2 vs own MoM 0.46 % resonance offset for a 2 mm dipole; openEMS MSL-port Z0 +0.7 % rise over 0.44–2.44 GHz.
