# 01-circuit-theory — Lumped circuit theory for RF

Linear, lumped-element circuit theory as it is used in RF and analog design: impedance and admittance, network theorems and power transfer (including why real PAs and LNAs are deliberately *not* conjugate-matched), resonance and Q, LC filter synthesis from low-pass prototypes, two-port matrices (Z, Y, h, ABCD, T), transformers and coupled inductors, transient response, and stored energy / reactive power (component stress). Transmission lines, the Smith chart, S-parameters and matching-network design live in [03-transmission-lines-matching](../03-transmission-lines-matching/_index.md); non-ideal real parts (parasitics, SRF, MLCC derating, crystals) in [04-real-components-hf](../04-real-components-hf/_index.md); SAW/cavity/microstrip filters and baluns in [06-rf-circuits](../06-rf-circuits/_index.md). Every numeric claim on these pages is reproduced by a script in `tools/verify/circuits_*.py`.

## Reading order (beginner → advanced)
1. [Lumped elements, impedance and admittance](lumped-elements-impedance-admittance.md) — the vocabulary: $j\omega L$, $1/j\omega C$, series/parallel, reactance tables at 433/915/2450 MHz.
2. [Network theorems and maximum power transfer](network-theorems-max-power-transfer.md) — KCL/KVL, nodal analysis, Thévenin, conjugate match, available power, load-line and noise match.
3. [Resonance and Q](resonance-and-q.md) — resonators, loaded/unloaded Q, bandwidth, insertion loss vs Q, L-match Q.
4. [Transient and step response](transient-and-step-response.md) — time constants, 0.35/tr, damping, ringing (scope probes, decoupling).
5. [Energy storage and reactive power](energy-storage-and-reactive-power.md) — complex power, stored energy, component voltage/current stress.
6. [Two-port networks — Z, Y, h, ABCD, T](two-port-networks-zyh-abcd.md) — matrix descriptions, conversions, cascades, network properties.
7. [Transformers and coupled inductors](transformers-coupled-inductors.md) — k, leakage/magnetising inductance, taps and capacitive dividers, coupled resonators.
8. [Passive LC filter design from low-pass prototypes](passive-filter-design-prototypes.md) — Butterworth/Chebyshev/elliptic/Bessel, scaling, transforms, finite-Q loss, 433 MHz harmonic LPF and 915 MHz BPF designs.

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [lumped-elements-impedance-admittance](lumped-elements-impedance-admittance.md) | V–I laws, $Z$/$Y$, reactance vs frequency, series↔parallel conversion, lumped limit, Foster/passivity | intro | high |
| [network-theorems-max-power-transfer](network-theorems-max-power-transfer.md) | KCL/KVL, nodal/mesh, Thévenin/Norton, superposition, MPT & conjugate match, mismatch factor, 50 % efficiency myth, PA load-line, LNA noise match | mixed | high |
| [resonance-and-q](resonance-and-q.md) | series/parallel resonance, energy Q, $Q_u$/$Q_e$/$Q_L$, BW, IL vs Q, component Q, L-match Q, group delay | mixed | high |
| [passive-filter-design-prototypes](passive-filter-design-prototypes.md) | response families, g-values, order formulas, scaling, LP→HP/BP/BS, J-inverter coupled resonators, delay–loss rule, harmonic LPF & 915 MHz BPF | mixed | high |
| [two-port-networks-zyh-abcd](two-port-networks-zyh-abcd.md) | Z/Y/h/ABCD/T definitions, conversions, interconnections, terminated two-port, reciprocity/symmetry/losslessness, image impedance | intermediate | high |
| [transformers-coupled-inductors](transformers-coupled-inductors.md) | mutual inductance, ideal/real transformer models, bandwidth, taps, capacitive divider, coupled-resonator k, TL transformers | mixed | high |
| [transient-and-step-response](transient-and-step-response.md) | RC/RL/RLC transients, rise time–bandwidth, overshoot vs ζ, cascades, band-pass envelopes, probe ringing | intro | high |
| [energy-storage-and-reactive-power](energy-storage-and-reactive-power.md) | complex power, stored energy, Tellegen/Poynting, reactive power in matches/filters/small antennas, voltage and current ratings | mixed | high |

## Domain FAQ (top questions → page#section)
- *What is the reactance of 10 nH / 10 pF at 433 or 915 MHz?* → [lumped elements § Worked examples](lumped-elements-impedance-admittance.md#worked-examples)
- *Does conjugate matching waste half the power?* → [network theorems § Level 2](network-theorems-max-power-transfer.md#level-2--the-conjugate-match-available-power-and-mismatch)
- *Why isn't a PA or LNA conjugate matched?* → [network theorems § Level 3](network-theorems-max-power-transfer.md#level-3--why-real-rf-stages-are-deliberately-not-conjugate-matched)
- *What is loaded vs unloaded Q and how does it set bandwidth and loss?* → [resonance and Q § Level 2](resonance-and-q.md#level-2--derivations)
- *How do I design a harmonic filter for my 433 MHz transmitter?* → [filter prototypes § Worked example A](passive-filter-design-prototypes.md#a-harmonic-low-pass-filter-after-a-43392-mhz-lora-pa)
- *Can I make a 902–928 MHz filter from chip L and C?* → [filter prototypes § Worked example B](passive-filter-design-prototypes.md#b-915-mhz-band-pass-3-pole-chebyshev-01-db)
- *How much loss does component Q add to a filter?* → [filter prototypes § Level 3](passive-filter-design-prototypes.md#level-3--real-world-corrections)
- *How do I convert S to Z/Y/ABCD, and cascade blocks?* → [two-ports § Level 2](two-port-networks-zyh-abcd.md#level-2--conversions-and-terminated-two-ports)
- *Why does impedance transform by the turns ratio squared, and what limits transformer bandwidth?* → [transformers § Level 2](transformers-coupled-inductors.md#level-2--equivalent-circuits)
- *Why does my scope ring at 100 MHz?* → [transients § Worked example 1](transient-and-step-response.md#1-why-your-scope-rings-at-120-mhz)
- *Is rise time × bandwidth always 0.35?* → [transients § Level 3](transient-and-step-response.md#level-3--general-systems-bandwidth-rules-and-limits)
- *What voltage rating do my matching-network capacitors need at 2 W?* → [reactive power § Level 3](energy-storage-and-reactive-power.md#level-3--component-stress-in-real-rf-networks)

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
Pozar *Microwave Engineering* (4th ed.); Bowick *RF Circuit Design* (2nd ed.); Hagen *Radio-Frequency Electronics* (2nd ed.); Ludwig & Bogdanov *RF Circuit Design* (2nd ed.); Matthaei/Young/Jones; Zverev *Handbook of Filter Synthesis*; Williams & Taylor *Electronic Filter Design Handbook*; Hong & Lancaster *Microstrip Filters*; Cripps *RF Power Amplifiers*; Agarwal & Lang *Foundations of Analog and Digital Electronic Circuits*; Steer *Microwave and RF Design* (open textbook).

## Verification scripts
`tools/verify/circuits_impedance_basics.py`, `circuits_power_transfer.py`, `circuits_resonance_q.py`, `circuits_filter_prototypes.py`, `circuits_two_port.py`, `circuits_transformers.py`, `circuits_transient.py`, `circuits_reactive_power.py` — each runs standalone (`python3 tools/verify/<name>.py`) and asserts its key results.

## Known gaps
- Elliptic LC element values are numerically fitted (checked against SciPy's elliptic response), not cross-checked with a printed Zverev table entry.
- No measured in-circuit Q data for JLCPCB-stocked chip inductors at 433/915 MHz (bench campaign suggested).
- Coupling between adjacent chip inductors vs spacing is not quantified (needs EM simulation; see 13-pcb-rf-layout-emc).
- Active-filter and op-amp topics are in 05-analog-electronics; nonlinear/large-signal circuit behaviour (harmonic balance) in 16-simulation-tools.
