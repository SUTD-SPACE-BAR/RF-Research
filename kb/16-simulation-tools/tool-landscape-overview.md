---
title: RF simulation tool landscape — which tool for which problem (circuits, lines, antennas, EM, links, radar), free vs commercial, fidelity, learning curve, macOS support
domain: 16-simulation-tools
slug: tool-landscape-overview
tags: [tool-selection, itm, longley-rice, terrain-profile, coverage-prediction, srtm, censored-data, tobit, decision-table, spice, harmonic-balance, nec, openems, fdtd, fem, mom, scikit-rf, rfcalc, link-budget, radar-simulation, macos, free-software, student-licence]
prerequisites: []
related: [installing-tools-macos.md, spice-circuit-simulation.md, rf-circuit-simulators-harmonic-balance.md, em-solvers-fdtd-mom-fem.md, nec-antenna-modelling.md, openems-workflow.md, python-rf-toolkit.md, impedance-and-rf-calculators.md, simulation-validation.md]
level: intro
confidence: high
last_updated: 2026-10-13
---

# RF simulation tool landscape

## Questions this page answers
- I want to simulate X (a matching network, a filter, a PCB antenna, a Yagi, a link, a radar) — which tool should I use?
- Which free tools run natively on my Mac, and which need Windows?
- How accurate is each kind of tool, and how long does it take to learn?
- When is a closed-form calculator enough and when do I need a full-wave EM solver?
- What does this knowledge base already provide (scripts, calculators) so I don't start from zero?
- How do I predict coverage over real terrain (the landing area, a hill between me and the rocket), and how far can I trust it?
- Why does a TTN-Mapper-style coverage map show the link working much further away than it really does?

## TL;DR
- **Start with the cheapest tool that captures the physics that matters**: a closed form (`tools/rfcalc`) → a linear network model (scikit-rf, SPICE `.sp`) → a specialised solver (NEC for wires, 2-D field solver for lines) → full-wave 3-D (openEMS) → measurement. Each step up costs 10–100× more effort.
- **Mac-native and tested here**: ngspice (brew; also inside KiCad), PyNEC (NEC-2), openEMS (built from source), scikit-rf, numpy/scipy, `tools/rfcalc` (159 tests, incl. the ITM terrain model), KiCad's PCB Calculator. **Mac, not tested**: LTspice (admin-password `.pkg`), MEEP (conda-forge), Qucs-S (unsigned; owner's Gatekeeper decision), SimSmith (Java). **Windows-only**: 4nec2, EZNEC (free v7), MMANA-GAL, Saturn PCB Toolkit, AppCAD, Sonnet Lite, QucsStudio, AWR MWO (free 6-month academic), HFSS/CST student editions, Keysight ADS.
- **Fidelity ladder**: closed forms ≈ 0.3–3 % for their idealised geometry; linear network models exact for what is modelled (parasitics must be added); NEC ≈ 1 % on wires within its rules; full-wave 3-D ≈ 0.5–2 % frequency when converged; the dominant real-world error is usually **material and geometry tolerance** (FR-4 εr ± 5 % ⇒ ± 2.3 % patch frequency), which only measurement removes.
- **Everything should be validated** against an independent answer before use ([simulation validation](simulation-validation.md)).
- **Terrain coverage**: `rfcalc itm` / `rfcalc.itm` is a pure-Python port of NTIA/ITS's ITM (Longley–Rice). It reproduces all of NTIA's area-mode example vectors and 4 of their 5 point-to-point vectors to ≤ 0.05 dB; the fifth needs a 3 680-point profile that was not transcribed. On a real 15 km SRTM profile (Example 4), ITM and the KB's flat-earth two-ray model **disagree by 10–50 dB for a landed rocket**. ITM also refuses antennas below 0.5 m, so the canonical 0.1 m case cannot be run in it. For ground-level links the model is the uncertainty; only a measurement settles it.
- **Mapper data are censored** (Example 5). Logging only the packets that arrived and fitting a line gave a path-loss exponent of 1.7 instead of 3.5, and a median range 2.4× too long. A censored (Tobit) fit that also uses the failed attempts recovers n = 3.60 and σ = 8.06 dB (true values 3.5 and 8).

## Intuition (no math)
Tools differ in *what they assume away*. A link-budget calculator assumes free space and a few dB of margin terms; SPICE assumes wires have no length; NEC assumes the antenna is thin wires in air; a 2-D line solver assumes the line is infinitely long; a 3-D FDTD/FEM solver assumes only what you drew. The right tool is the one whose assumptions are true enough for your question — and the art is knowing which assumption breaks first. At 433 MHz a 20 mm trace is λ/17 in FR-4 (lumped is marginal); at 2.45 GHz it is λ/3 (never lumped). A dipole in free space is a wire problem; the same dipole inside a fibreglass nose cone is a dielectric problem.

## The math
The "which tool" question reduces to a few dimensionless numbers:
- **Electrical size** $L/\lambda$: lumped circuits valid for $L \lesssim \lambda/10$ (SPICE); beyond that, transmission lines or EM.
- **Geometry aspect**: wires with $2\pi a/\lambda \ll 1$ and segment rules → MoM (NEC); planar layered → 2.5-D MoM; arbitrary 3-D with dielectrics → FDTD/FEM.
- **Quality factor** $Q$: high-Q structures favour frequency-domain methods (FEM, HB) over time-domain (FDTD ring-down, transient settling ∝ Q).
- **Bandwidth**: broadband answers favour time-domain (one FDTD run covers the band).
- **Nonlinearity**: linear → S-parameters/AC; weakly/strongly nonlinear periodic → HB; arbitrary → transient.
- **Problem cost**: FDTD cells $\sim (L/h)^3$, MoM unknowns $\sim (L/h)^2$ with $N^2$ memory, wire MoM $\sim L/\Delta$ ([EM solvers](em-solvers-fdtd-mom-fem.md#level-2--cost-and-accuracy-scaling)).

## Design equations & rules of thumb — the decision table

| Problem | First tool (free, Mac) | Fidelity | Learning curve | Upgrade path | KB page / script |
|---|---|---|---|---|---|
| dB, dBm, VSWR, mismatch | `rfcalc db` / `rfcalc.units` | exact | minutes | — | [decibels](../00-math-foundations/decibels-and-log-units.md) |
| Link budget, FSPL, range | `rfcalc link` | free-space + margins | minutes | ITU-R models, terrain tools | [link budget](../09-propagation-link-budget/link-budget-methodology.md) |
| Ground-level / landed-rocket coverage over terrain | `rfcalc itm` (point-to-point with a DEM profile, or area mode with Δh) | model-limited: 10–50 dB spread between models near the ground (Example 4) | hours | SPLAT!/Radio Mobile maps; ITU-R P.1812; **measurement** | Example 4 below; [two-ray](../09-propagation-link-budget/two-ray-ground-reflection.md) |
| Fresnel / horizon / LOS altitude | `rfcalc fresnel/horizon`, `rfcalc.propagation` | smooth earth | minutes | terrain profile tools | [Fresnel](../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md) |
| Receiver NF/IIP3 cascade, sensitivity | `rfcalc cascade`, `rfcalc sens` | datasheet-limited | minutes | HB with real models | [cascade](../07-noise-linearity/receiver-cascade-analysis.md) |
| LoRa air time, sensitivity | `rfcalc lora` | Semtech formulas | minutes | — | [LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md) |
| Trace impedance | `rfcalc microstrip/cpwg`, KiCad calculator; `tline_fd2d.py` for mask/thickness | 0.3 % ideal; ±2–5 Ω real | minutes | fab calculator, TDR coupon | [calculators](impedance-and-rf-calculators.md) |
| L/π/T matching, stubs | `rfcalc lmatch`, scikit-rf | exact (ideal parts) | minutes–hours | vendor S2P parts, EM of pads | [matching](../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md) |
| LC filters, bias tees, diplexers | ngspice `.sp`, scikit-rf | exact + parasitics you add | hours | EM of layout | [SPICE](spice-circuit-simulation.md) |
| Oscillators, PA supply transients, ADC front ends | ngspice / LTspice transient | model-limited | hours | HB/PSS | [SPICE](spice-circuit-simulation.md) |
| PA compression, mixers, multipliers, IP3 | Python HB sketch; Xyce / Qucs-S | model-limited | days | AWR MWO (academic), ADS | [HB](rf-circuit-simulators-harmonic-balance.md) |
| Touchstone handling, de-embedding, TDR | scikit-rf | exact for the data | hours | — | [Python toolkit](python-rf-toolkit.md) |
| Dipoles, monopoles, Yagis, helices, loops | PyNEC (NEC-2) | ~1 % within rules | hours | EZNEC/4nec2 GUI (Windows), NEC-4 | [NEC](nec-antenna-modelling.md) |
| Patch, PCB, chip antennas; antenna in nose cone | openEMS | 1–2 % converged | days–weeks | CST/HFSS/Feko | [openEMS](openems-workflow.md) |
| Connector launches, vias, discontinuities | openEMS (fine mesh) | 1–2 dB RL-level | days | HFSS/CST | [openEMS](openems-workflow.md) |
| Planar filters/couplers | openEMS; Sonnet Lite (Windows) | ~1 % | days | Sonnet, Momentum, AXIEM | [EM solvers](em-solvers-fdtd-mom-fem.md) |
| Array factor, beam steering | `rfcalc array`, `rfcalc.arrays` | isotropic-element ideal | minutes | NEC/openEMS with coupling | [array factor](../12-phased-arrays/array-factor-linear-arrays.md) |
| Radar range, FMCW parameters, detection SNR | `rfcalc radar/fmcw`, `rfcalc.radar` | textbook | minutes | RadarSimPy (free tier), MATLAB | [radar detection](../11-radar/detection-theory-cfar.md) |
| Modulation, BER, LoRa CSS waveforms | numpy/scipy (`tools/verify/comms_*`, `lora_css_sim.py`) | exact for the model | hours | GNU Radio (deprecated Qt5 formula) | [comms](../10-comms-modulation/_index.md) |

### Tool catalogue — cost, platform, learning curve (status 2026-09)

| Tool | Class | Cost | macOS (Apple Silicon) | Learning curve | Status on this Mac |
|---|---|---|---|---|---|
| `tools/rfcalc` | calculators (Python) | free | native | minutes | tested, 159 tests |
| `rfcalc.itm` / `rfcalc itm` | ITM (Longley–Rice v1.2.2) terrain loss, point-to-point and area mode; port of NTIA/ITS's reference code | free (NTIA licence: derivatives allowed with acknowledgement) | native | hours (the inputs, not the code) | tested: NTIA's example vectors to ≤ 0.05 dB |
| SPLAT!, Radio Mobile, Signal-Server | ITM/Longley–Rice coverage maps with a DEM | free | SPLAT! builds on Unix; Radio Mobile is Windows | days | not installed |
| KiCad PCB Calculator | line/attenuator/via calculators | free | native | minutes | present (KiCad 10), GUI not exercised |
| scikit-rf | network analysis (Python) | free (BSD) | native | hours | tested (2.0.1) |
| ngspice | SPICE | free | native (brew; KiCad library) | hours | tested (47 CLI, 44.2 library) |
| LTspice | SPICE | free | native `.pkg` (admin password) | hours | not installed |
| Qucs-S (+ QucsatorRF, Xyce) | schematic RF/SPICE, HB | free | unsigned cask (Gatekeeper blocks first launch; owner decides) | days | installed, not used |
| Xyce | SPICE + HB | free (open source) | source build | days | not installed |
| QucsStudio | RF circuit, HB | freeware | Windows only | days | — |
| Keysight ADS | RF circuit/HB/EM | commercial (student via University Program) | Windows/Linux | weeks | — |
| Cadence AWR MWO | RF circuit/HB/EM | commercial (free 6-month academic) | Windows only | weeks | — |
| SimSmith | Smith-chart matching | free | Java | hours | not installed |
| RFSim99 | linear RF circuit | freeware (1999) | Windows only | hours | — |
| PyNEC (NEC-2) | wire MoM (Python) | free (GPL) | native wheel | hours | tested (2.3.4) |
| 4nec2, EZNEC v7, MMANA-GAL | NEC/MININEC GUIs | free | Windows only (Wine cask disabled) | hours | — |
| xnec2c | NEC-2 GUI | free (GPL) | source build (GTK) | hours | not built |
| openEMS | 3-D EC-FDTD | free (GPL) | source build (~25 min) | weeks | tested (v0.37-rc3) |
| MEEP | 3-D FDTD | free (GPL) | conda-forge osx-arm64 | weeks | not installed |
| Elmer, Palace, OpenParEM | 3-D FEM | free (GPL/Apache) | source/Spack builds | weeks | not installed |
| Sonnet Lite | 2.5-D planar MoM | free (64 MB limit) | Windows only | days | — |
| HFSS / CST / Feko student | 3-D FEM / FIT / MoM | free for students, size-limited (Feko "no-limits" claim unverified) | Windows (Linux for some) | weeks | — |
| `tools/verify/tline_fd2d.py` | 2-D quasi-static field solver | free (this KB) | native | minutes | tested |
| RadarSimPy | radar baseband simulator | free tier / licensed | pre-built modules | days | not installed |
| GNU Radio | streaming SDR/DSP | free | brew formula (deprecated Qt5, disable 2027-05-19) | days | not installed |

## Worked examples
### 1 — "Will my 915 MHz chip antenna match on the new flight-computer board?"
1. Minutes: vendor datasheet + `rfcalc lmatch` for the matching network from the vendor's reference impedance; trace width from `rfcalc microstrip`.
2. Hours: scikit-rf with the chip antenna's S-parameter file and vendor S2P capacitor/inductor files → realistic RL across 902–928 MHz with E-series values.
3. Days: openEMS of the board outline + ground clearance + chip antenna footprint (the ground plane is part of the antenna).
4. Truth: build, NanoVNA S11 at the matching pads, tune with the π-pad. Steps 1–2 usually suffice to choose parts; step 4 is never optional.

### 2 — "How far will the 433 MHz telemetry reach?"
`rfcalc link` with the E22's 33 dBm, cable losses and ground-Yagi gain gives −75.8 dBm at 30 km — ≈ 49 dB margin at SF7/125 kHz (−124.5 dBm) and ≈ 52 dB at the page's 2.4 kb/s sensitivity; NEC gives the Yagi's real gain (14.3 dBi for an 11-element DL6WU — better than the assumed 11 dBi) and the dipole's pattern nulls; the Fresnel/horizon functions show where the descent link is lost. No EM solver needed — the uncertainty is in fades, pointing and plume, not in the antenna model.

### 3 — "Is 18 MHz from my Colpitts exact?"
SPICE transient gives 18.80 MHz vs 18.17 MHz from the tank formula because device capacitances load the tank; the simulation is the better predictor, but only after checking the bias network has settled ([SPICE](spice-circuit-simulation.md#worked-examples)).

### 4 — terrain coverage for a landed rocket with ITM on a real profile (`tools/verify/sim2_coverage_itm.py`)
**Set-up.** The profile is 100 SRTM-90 m elevations along 32.99° N from 106.97° W to 106.81° W (14.92 km, 150.7 m spacing), taken from the OpenTopoData public API on 2026-10-13. It runs across the desert plain east of Spaceport America, New Mexico, the IREC/Spaceport America Cup range. This is an example site: the team's own launch sites are not recorded in the Space Bar notes. The terrain dips from 1401 m to 1386 m and then rises to 1552 m, so the profile is concave.

The rest of the set-up follows the KB's canonical landed case ([09 Example E](../09-propagation-link-budget/link-budget-methodology.md#example-e--landed-rocket-the-case-that-actually-limits-recovery)): ground station on a 5 m mast at the west end, landed rocket to the east, 433.92 MHz, H-pol, medium-dry ground (εr 15, σ 10⁻³ S/m). One input differs: the rocket antenna is **0.5 m** above the ground, because ITM rejects heights below 0.5 m and warns below 1 m. ITM was run with climate 4 (desert), N₀ 301 and the median (50/50/50 %).

| d (km) | FSPL | two-ray, 0.5 m | two-ray, 0.1 m (canonical) | ITM, flat profile | ITM, real profile | ITM Δh (m) |
|---|---|---|---|---|---|---|
| 1.06 | 85.7 | 113.0 | 126.6 | 112.3 | 109.5 | 17.5 |
| 3.01 | 94.8 | 131.2 | 144.8 | 131.3 | 113.0 | 21.2 |
| 4.97 | 99.1 | 139.9 | 153.5 | 141.0 | 122.8 | 45.8 |
| 9.95 | 105.2 | 151.9 | 165.6 | 156.2 | 109.3 | 76.5 |
| 14.92 | 108.7 | 159.0 | 172.6 | 164.6 | 111.9 | 91.9 |
(basic transmission loss in dB)

Against the pre-registration:
- **T1 passed.** On a flat profile, ITM sits +0.1 to +5.6 dB above the two-ray model, so with no terrain the two models agree.
- **T2 missed badly.** On the real profile, ITM's loss at 10–15 km is about 50 dB *below* the flat case, close to free space.

The cause of the T2 miss is ITM's effective-height rule. ITM measures antenna heights above a least-squares line fitted through the terrain. A concave profile puts both ends tens of metres above that line, so the two-ray cancellation that dominates at 0.5 m disappears. As a post-hoc control, the profile was mirrored to put a 160 m hump between the stations. ITM still gives about 10 dB *less* loss than flat (153.7 dB at 14.9 km, in diffraction mode), because its effective heights grow with terrain roughness either way.

**T3 passed**: ITM refuses 0.1 m (error 1001). **T4 passed**: with the canonical budget (33 dBm, 0 dBi, 11 dBic, −3 dB polarisation, −1 dB feeder, 2.4 kb/s at −128 dBm), the margin at 15 km is +56 dB by ITM and +9 dB by two-ray at 0.5 m. The canonical 0.1 m two-ray case runs out of margin at about 11.5 km.

What to take from it:
1. A few decimetres of antenna height are worth about 14 dB in the plane-earth regime: compare the 0.5 m and 0.1 m two-ray columns.
2. For an antenna this low, ITM is outside its recommended range: its input check warns below 1 m (recommended 1–1000 m). Two defensible models then differ by 10–50 dB. This is model-form uncertainty in the sense of [simulation validation](simulation-validation.md); no mesh or code check can remove it.
3. Plan recovery with the pessimistic model: the KB's flat-earth two-ray with the real antenna height. Use a terrain tool to find **shadows**, meaning ridges between the station and the likely landing zone, not to claim extra margin. Then measure: carry a beacon to known points in the landing area and log RSSI.
4. For the ascent (rocket in the air), ITM accepts terminal heights only up to 3 km. ITU-R P.528 (air-to-ground) is the right model above that, and it is not yet in rfcalc. Use the free-space budget plus the antenna pattern there; terrain matters only near the horizon.

CLI: `cd tools && python3 -m rfcalc itm --f 433.92M --d 10km --dh 30 --htx 5 --hrx 0.5 --pol 0` (area mode), or add `--profile elev.txt --spacing 150.7` for a point-to-point profile. The defaults are climate 1 (equatorial, Singapore), N₀ 360, εr 15, σ 0.005.

### 5 — why mapper coverage data lie (censoring), and how to fit them properly
Community mappers (TTN Mapper, Helium explorers) record a point **only when a packet was received**. The failed attempts, which carry the information about the edge of coverage, are missing.

A simulation in the same script shows the effect. It draws 4 000 attempts at 0.2–20 km with PL = 40 + 35 log₁₀ d + X (σ = 8 dB), a 14 dBm EIRP and a −120 dBm threshold. Only 20 % of packets arrive, and none beyond 5 km.

| Fit | n (true 3.5) | σ (true 8 dB) | median range at the threshold (true 0.48 km) |
|---|---|---|---|
| ordinary least squares on received packets | **1.70** | 6.08 dB | **1.17 km (+142 %)** |
| censored (Tobit) MLE, failed attempts' positions known | 3.60 | 8.06 dB | 0.47 km |
| truncated MLE, received packets + known threshold only | 4.32 | 8.65 dB | — |

Pre-registered results:
- **C1 passed for n but narrowly missed for σ.** σ came out 1.92 dB low; the threshold for a pass was 2 dB.
- **C2 passed for the Tobit fit and missed for the truncated fit.** The truncated fit's n is 0.82 too high. With only short-range survivors, truncation alone pins n poorly.
- **C3 passed.**

The rule follows from this. When you map your own link, **log every transmission with its position, including the ones nobody heard.** Your own transmitter's log provides that, and with it the Tobit fit works. A map of received points shows where the lucky tail of the fading distribution reached, not the median coverage.

## Practical notes
- **Keep a golden set of benchmarks** per tool (dipole, microstrip, Butterworth filter, pad NF) and rerun them after upgrades — both ngspice and openEMS changed behaviour between versions in ways that matter (e.g. ngspice-47's `meas sp … WHEN` crash).
- **Budget time for meshing and set-up**, not solving; most FDTD/FEM time is spent building and checking the model.
- **Licences**: free academic licences (AWR, HFSS/CST student) are for learning and coursework; check terms before using them for team hardware.
- **Record** every run with tool version, inputs and results (as `tools/verify/sim_openems_results.txt`).

## Common mistakes & misconceptions
- **Reaching for full-wave EM first** — a link budget or a matching network rarely needs it; a PCB antenna always does.
- **Using NEC for PCB antennas or FDTD for long wire antennas** — wrong assumptions or absurd cost.
- **Believing expensive tools are more accurate** — accuracy comes from the set-up; free solvers validated here agree with closed forms to < 0.3 %.
- **Ignoring component and material tolerances** — they usually dominate simulator error.
- **Reading coverage off a map of received packets.** Received-only data are censored: the fit flattens the path-loss slope (1.7 instead of 3.5) and overstates range by 2–3× (Example 5).
- **Running a terrain model outside its validity and ignoring its warnings.** ITM flags antennas below 1 m and refuses heights below 0.5 m. Near the ground its answer can be 50 dB from a two-ray model on the same path (Example 4).

## How to simulate / verify
- Tool installation and smoke tests: [installing tools on macOS](installing-tools-macos.md).
- Calculators: `cd tools && python3 -m rfcalc --help`; tests: `python3 -m pytest rfcalc/tests -q` (159 tests; `rfcalc/tests/test_itm.py` checks the ITM port against NTIA's area.csv / p2p.csv / pfls.csv vectors).
- Terrain and censoring: `python3 tools/verify/sim2_coverage_itm.py` (≈ 10 s; Examples 4–5, pre-registered T1–T4 and C1–C3; results in `sim2_coverage_results.txt`).
- Solver checks: `tools/verify/sim_ngspice_examples.py`, `sim_nec_vs_mom.py`, `sim_openems_msl.py`, `sim_openems_patch.py`, `sim_harmonic_balance.py`.

## Open questions / gaps
- ITM is in rfcalc (Examples 4–5), but **ITU-R P.528 (air-to-ground) and P.1812 are not**. A DEM loader (SRTM/Copernicus tiles to a profile) is not automated: Example 4 used 100 points from a public elevation API, pasted into the script.
- ITM's NTIA p2p vector 1 (a 3 679-interval profile) is not in the tests.
- **No measurement** decides between ITM and two-ray for a landed 433 MHz antenna at 0.1–0.5 m. This is the most valuable recovery-link measurement still missing (see [20 validation test campaign](../20-projects-recipes/validation-test-campaign.md)).
- A worked end-to-end example (openEMS antenna pattern → NEC-style link budget with real pattern nulls → telemetry margin vs rocket attitude) would tie the tools together.

## Sources
1. Tool documentation as cited on each page: ngspice manual; openEMS docs; NEC-2 User's Guide (Burke & Poggio 1981); scikit-rf docs; Qucs-S project page. (tool documentation)
2. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — lumped vs distributed criteria, network analysis. (textbook)
3. A. Taflove and S. C. Hagness, *Computational Electrodynamics*, 3rd ed., 2005; J.-M. Jin, *The Finite Element Method in Electromagnetics*, 3rd ed., 2014; R. F. Harrington, *Field Computation by Moment Methods*, 1968. (textbooks)
4. Vendor pages checked 2026-09-27/29: Ansys HFSS Student limitations; Cadence AWR University FAQ; eznec.com; Sonnet Lite information; JLCPCB impedance-calculator guide. (vendor documentation)
5. This repository: `tools/rfcalc/`, `tools/verify/sim_*.py` (W3-C2) and the domain verification scripts they build on. (verification)
6. NTIA/ITS, *Irregular Terrain Model (ITM)* reference implementation and example vectors (area.csv, p2p.csv, pfls.csv), https://github.com/NTIA/itm (C++ v1.3 ≡ FORTRAN 1.2.2; licence permits derivative works with acknowledgement). G. A. Hufford, A. G. Longley, W. A. Kissick, *A guide to the use of the ITS Irregular Terrain Model in the area prediction mode*, NTIA Report 82-100, 1982. (government reference code / report)
7. OpenTopoData public API, SRTM 90 m dataset (NASA SRTM v4), https://www.opentopodata.org/ — Example 4's profile, queried 2026-10-13. (data)
8. J. Tobin, "Estimation of relationships for limited dependent variables," *Econometrica* 26(1), 24–36, 1958 — the censored-regression (Tobit) likelihood used in Example 5. (peer-reviewed)
9. This repository: `tools/rfcalc/itm.py`, `tools/rfcalc/tests/test_itm.py`, `tools/verify/sim2_coverage_itm.py` (W5-S11). (verification)
