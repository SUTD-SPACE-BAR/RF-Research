# 03-transmission-lines-matching — Transmission lines and impedance matching

Scope: how signals travel on two-conductor lines (coax, PCB microstrip/stripline/CPWG), what
characteristic impedance, reflections, VSWR and S-parameters mean, how to read and use the Smith chart,
how to match loads (lumped L/Pi/T, stubs, λ/4, multi-section, tapers) and what limits broadband
matching (Bode–Fano, Chu), plus time-domain reflectometry and mismatch uncertainty. Lumped two-port
theory and filters live in [01-circuit-theory](../01-circuit-theory/two-port-networks-zyh-abcd.md);
component parasitics in [04](../04-real-components-hf/component-models-s2p-spice.md); distributed
filters/couplers/baluns in [06](../06-rf-circuits/couplers-dividers-combiners.md); PCB layout rules
and stackup practice in [13](../13-pcb-rf-layout-emc/rf-layout-rules.md); VNA calibration in
[17](../17-test-measurement/vna-fundamentals-calibration.md). Every page's formulas are checked by
Python scripts in `tools/verify/tline_*.py` (all passing as of 2026-09-27), including an independent
2-D field solver (`tline_fd2d.py`).

## Reading order (beginner → advanced)
1. [Telegrapher's equations and characteristic impedance](telegrapher-equations-characteristic-impedance.md) — what a transmission line is, Z0, γ, velocity factor.
2. [Reflections, VSWR, return loss and mismatch loss](reflections-vswr-return-loss-mismatch.md) — Γ, VSWR, RL, the conversion table, SWR myths.
3. [Input impedance, stubs, quarter- and half-wave lines](input-impedance-stubs-quarter-wave.md) — Zin, λ/4 inversion, stubs as L/C and resonators.
4. [The Smith chart](smith-chart.md) — the Γ-plane map, moves, reading a NanoVNA.
5. [Coaxial lines and RF cables](coax-and-cables.md) — why 50 Ω, cable loss tables, ground-station and pigtail choices.
6. [Planar lines — microstrip, stripline, CPW/CPWG, differential pairs](planar-lines-microstrip-stripline-cpwg.md) — trace widths on JLCPCB stackups, formula accuracy.
7. [Impedance matching — lumped and distributed](impedance-matching-lumped-and-distributed.md) — L/Pi/T, Q and bandwidth, component loss, stubs, transformers, tapers, pi-pad tuning procedure.
8. [S-parameters](s-parameters.md) — waves, conversions, physical checks, mixed-mode, Touchstone, gains and stability preview.
9. [Signal-flow graphs, Mason's rule and mismatch uncertainty](signal-flow-graphs-mason.md).
10. [Time-domain reflectometry](time-domain-reflectometry.md) — TDR and VNA time-domain, resolution, windows, gating.
11. [Broadband matching and the Bode–Fano limit](broadband-matching-bode-fano.md) — hard limits, small antennas.
12. [Periodic structures, EBG and metamaterial basics](periodic-structures-ebg.md) — Floquet/Bloch, slow-wave and Bragg lines, surface and leaky waves, mushroom AMC, CRLH, hype check (advanced).

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [telegrapher-equations-characteristic-impedance](telegrapher-equations-characteristic-impedance.md) | RLGC derivation, Z0, γ, low-loss & distortionless line, VF, ohmmeter myth, measuring Z0/VF | mixed | high |
| [reflections-vswr-return-loss-mismatch](reflections-vswr-return-loss-mismatch.md) | Γ, VSWR, RL, ML, standing waves, lossy-line masking, PA/SWR myths, voltage stress | mixed | high |
| [input-impedance-stubs-quarter-wave](input-impedance-stubs-quarter-wave.md) | Zin, λ/4, λ/2, stubs, resonant stubs (Q = β/2α), harmonic traps, λ/4 table | mixed | high |
| [smith-chart](smith-chart.md) | Möbius map, Z/Y chart, constant-Q, moves, Foster rule, NanoVNA reading, stability circles preview | mixed | high |
| [impedance-matching-lumped-and-distributed](impedance-matching-lumped-and-distributed.md) | L/Pi/T, complex loads, BW vs Q, finite-Q loss, stubs, binomial/Chebyshev/Klopfenstein, pi-pad procedure, 433/915/2450 MHz examples | mixed | high |
| [broadband-matching-bode-fano](broadband-matching-bode-fano.md) | Bode–Fano integrals, finite-order results, Chu/McLean, Q_Z from VNA | advanced | high |
| [s-parameters](s-parameters.md) | power vs pseudo-waves, conversions, unitarity/passivity, renormalisation, mixed-mode, T-params, Touchstone, gains, K/μ | mixed | high |
| [planar-lines-microstrip-stripline-cpwg](planar-lines-microstrip-stripline-cpwg.md) | H-J, Wheeler, K-J, Cohn, Ghione–Naldi, diff pairs, loss, JLCPCB widths, soldermask/thickness effects | mixed | high |
| [coax-and-cables](coax-and-cables.md) | coax Z0, 30/60/77 Ω optima, loss tables (LMR, RG, semi-rigid, U.FL), power, phase stability | mixed | high |
| [time-domain-reflectometry](time-domain-reflectometry.md) | TDR shapes, L/C area rule, VNA low-pass/band-pass, windows, resolution, aliasing, gating | mixed | high |
| [signal-flow-graphs-mason](signal-flow-graphs-mason.md) | flow graphs, Mason's rule, Γin and G_T derivations, mismatch uncertainty, directivity, ripple | intermediate | high |
| [antenna-tuners-and-atus](antenna-tuners-and-atus.md) | what a tuner does/doesn't; mismatched-line total loss tables (RG-58/LMR-400/ladder, SWR 3–20, same-antenna comparison: 4 % vs 52 % vs 70–75 %); SWR flattered by line loss; lossy L/T networks (exact ABCD, Q_n/Q_u rule, T max-C rule); auto-tuner blocks/search (ATU-100), remote/internal tuners (IC-7300 3:1), RX-only use | mixed | medium |
| [microstrip-discontinuities](microstrip-discontinuities.md) | open end (KJK/Hammerstad), gap, step, corner & 50 % mitre (KJK), Douville–James optimum mitre, Hammerstad T, Goldfarb–Pucel via; openEMS: corner within 0.7 dB, open end +11–18 % vs KJK (reported miss); when closed forms fail | mixed | medium |
| [periodic-structures-ebg](periodic-structures-ebg.md) | Floquet/Bloch condition and Bloch impedance, loaded slow-wave and Bragg lines, k–β diagram and leaky-wave scan, grounded-slab TM0 and exact HED surface-wave loss vs Jackson–Alexopoulos, mushroom EBG/AMC (openEMS: f0 5.82 vs 5.80 GHz model), CRLH lines, metamaterial hype check | advanced | medium |

## Domain FAQ (top questions → page#section)
- *Why doesn't my coax measure 50 Ω on a multimeter?* → [telegrapher#intuition](telegrapher-equations-characteristic-impedance.md#intuition-no-math)
- *How much power do I lose with VSWR 2?* → [reflections#level-1](reflections-vswr-return-loss-mismatch.md#level-1--definitions-and-conversions) (0.51 dB)
- *Does reflected power damage my LoRa module?* → [reflections#common-mistakes](reflections-vswr-return-loss-mismatch.md#common-mistakes--misconceptions)
- *Why does SWR change with cable length?* → [reflections#common-mistakes](reflections-vswr-return-loss-mismatch.md#common-mistakes--misconceptions)
- *How long is a quarter wave of RG-316 at 433 MHz?* → [stubs#design-equations](input-impedance-stubs-quarter-wave.md#design-equations--rules-of-thumb) (120 mm)
- *Which way do I move on the Smith chart for a series inductor?* → [smith-chart#level-2](smith-chart.md#level-2--derivations)
- *How do I match my chip antenna with the pi pad?* → [matching#practical-notes](impedance-matching-lumped-and-distributed.md#practical-notes--tuning-a-pi-pad-on-a-real-board-with-a-vna)
- *Can I make my small 433 MHz antenna broadband with a better network?* → [bode-fano#tldr](broadband-matching-bode-fano.md#tldr)
- *How wide is a 50 Ω trace on JLCPCB 2-layer / 4-layer?* → [planar-lines#tldr](planar-lines-microstrip-stripline-cpwg.md#tldr) (order the JLC calculator values: 2.69 mm masked microstrip or 0.92 mm masked CPWG with a 0.203 mm gap on JLC0216A; 0.359 mm masked on JLC04161H-7628 — [canonical widths](../00-math-foundations/canonical-values-and-conventions.md#b-materials-and-fabrication); the 2.8 mm figure is a bare h = 1.51 mm model input)
- *Which coax for my ground station?* → [coax#worked-examples](coax-and-cables.md#worked-examples)
- *What do S11/S21 mean and how do I read a .s2p?* → [s-parameters](s-parameters.md)
- *How do I find a bad connector with a NanoVNA?* → [TDR#worked-examples](time-domain-reflectometry.md#worked-examples)
- *Why does my logic edge overshoot at the end of a long trace? What are the small extra steps on my TDR?* → [TDR#level-2b](time-domain-reflectometry.md#level-2b--lattice-bounce-diagrams-with-resistive-and-reactive-terminations)
- *Can an EBG/AMC ground plane let my antenna sit flat on the airframe?* → [periodic#hype-check](periodic-structures-ebg.md#level-3--ebgmushroom-surfaces-crlh-lines-and-where-the-models-break) (narrowband: BW ≈ k0h)
- *Why is my power measurement ±0.3 dB even with a calibrated meter?* → [mason#level-3](signal-flow-graphs-mason.md#level-3--measurement-uncertainty-from-mismatch)
- *When should I use a radial or butterfly stub instead of a straight one, and can I trust the formula on thick FR-4?* → [stubs#radial-and-butterfly-stubs](input-impedance-stubs-quarter-wave.md#radial-and-butterfly-stubs); other distributed structures: [stubs#zoo](input-impedance-stubs-quarter-wave.md#a-zoo-of-distributed-pcb-structures-where-each-is-covered)
- *How much RF power can a microstrip trace carry before it overheats or arcs?* → [planar-lines#power-handling](planar-lines-microstrip-stripline-cpwg.md#level-3--power-handling-of-rf-traces)
- *How do I match a differential port, a high-impedance detector or two amplifier stages?* → [matching#special-topics](impedance-matching-lumped-and-distributed.md#special-topics)
- *Is ladder line or twisted pair better than coax for my HF antenna?* → [coax#open-wire-ladder-line-and-twisted-pair](coax-and-cables.md#open-wire-ladder-line-and-twisted-pair)

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
Pozar *Microwave Engineering* (4th ed.) chapters 2–6 and 12; Collin *Foundations for Microwave Engineering*;
Orfanidis *Electromagnetic Waves and Antennas* (free); Steer *Microwave and RF Design* (free);
Matthaei–Young–Jones; Wadell; Gupta et al.; Kurokawa 1965; Marks & Williams 1992; Hammerstad & Jensen 1980;
Kirschning & Jansen 1982; Klopfenstein 1956; Bode 1945 / Fano 1950; Keysight AN 154 and AN 1287-12;
scikit-rf documentation.

## Verification scripts
| Script | Checks | Runtime |
|---|---|---|
| `tools/verify/tline_telegrapher.py` | RLGC, Z0/γ vs skrf, low-loss & distortionless, RG-58 from geometry, step into open line, sympy | s |
| `tools/verify/tline_reflections.py` | conversion table, standing waves, lossy-line masking, total loss (vs skrf), source dissipation, 915 MHz budget | s |
| `tools/verify/tline_input_impedance.py` | Zin vs skrf, λ/4, stubs, resonant-stub Q, λ/4 bandwidth, Pi-equivalent | s |
| `tools/verify/tline_smith.py` | circle geometry, move directions, Foster, stability circle, lossless invariance; makes the figure | s |
| `tools/verify/tline_matching.py` | L/Pi/T, finite Q, stubs (skrf), binomial/Chebyshev/Klopfenstein vs exact cascades | ~5 s |
| `tools/verify/tline_bode_fano.py` | Fano integral, optimised ladders vs bound, Chu, Q_Z | ~2 min |
| `tools/verify/tline_sparams.py` | conversions, power vs pseudo waves, unitarity, mixed-mode, T, Touchstone, gains, K/μ | s |
| `tools/verify/tline_fd2d.py` | 2-D FD field solver + self-test vs Cohn | s |
| `tools/verify/tline_microstrip.py` | H-J/Wheeler/K-J/Cohn/Wheeler-78 vs FD & skrf, diff pairs, JLC widths, loss | ~4 min |
| `tools/verify/tline_cpwg.py` | CPW/CPWG vs FD & skrf, thickness, mask, JLC designs | ~3 min |
| `tools/verify/tline_coax.py` | coax Z0, 30/60/77 Ω optima, datasheet fits, TE11, thermal power | s |
| `tools/verify/tline_tdr.py` | low-pass transform, window constants vs Keysight, L/C area rule, resolution, aliasing | s |
| `tools/verify/tline_mason.py` | Mason vs direct solve, sympy derivations, mismatch uncertainty, directivity, ripple | s |
| `tools/verify/s5_tdr_lattice.py` | lattice/bounce diagrams with resistive and reactive ends (TDR Level 2b) | s |
| `tools/verify/s5_bloch_ebg.py`, `s5_mushroom_openems.py` | Bloch/ABCD stop bands, light-loading formulas, mushroom EBG (openEMS) for periodic-structures-ebg | s / min |
| `tools/verify/s6_radial_stub.py`, `s6_radial_stub_openems.py` | radial/butterfly stub Bessel model and variants; openEMS check recorded as a pre-registered miss | s / min |
| `tools/verify/s6_trace_heating.py` | RF trace power handling: loss, temperature rise, breakdown margins | s |
| `tools/verify/s6_matching_special.py` | double-stub forbidden region, half-circuit differential matching, special topics | s |
| `tools/verify/s6_coupled_offset.py` | coupled microstrip (Kirschning–Jansen), trapezoidal etch, offset stripline | s |
| `tools/verify/s6_ladder_line.py` | open-wire/ladder line and twisted pair Z0 and loss | s |
| `tools/verify/s6_image_filters.py` | image-parameter filters (on 01/passive-filter) | s |

## Known gaps
- Measured TDR data of JLCPCB impedance coupons (to settle the ±3 Ω spread between calculators; soldermask thickness over copper vs in gaps is unpublished per stackup).
- *(Closed 2026-10-13 by W5-S6: coupled microstrip (Kirschning–Jansen), trapezoidal etch and offset/asymmetric stripline are now on [planar-lines](planar-lines-microstrip-stripline-cpwg.md).)* Still open: measured coupled-line data on a JLC stackup.
- Exact (Riblet) Chebyshev transformer tables; Fano's finite-n closed forms. *(The double-stub forbidden-region derivation was added to [matching](impedance-matching-lumped-and-distributed.md) by W5-S6, 2026-10-13.)*
- Layer-peeling TDR inversion and loss compensation; NanoVNA firmware TDR internals.
- EBYTE module output impedance / VSWR protection behaviour (not published in sources consulted).
- Causal wideband dielectric and roughness models are only referenced (→ 02-electromagnetics).
