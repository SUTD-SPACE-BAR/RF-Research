---
title: Component models — vendor S-parameter files, equivalent circuits and how to use them
domain: 04-real-components-hf
slug: component-models-s2p-spice
tags: [s-parameters, touchstone, s2p, spice-model, equivalent-circuit, murata-simsurfing, coilcraft, modelithics, kemet-ksim, tdk-seat, de-embedding, fixture, series-thru, shunt-thru, reference-plane, passivity, causality]
prerequisites:
  - capacitors-at-rf-mlcc.md
  - inductors-at-rf.md
  - ../01-circuit-theory/two-port-networks-zyh-abcd.md
  - ../03-transmission-lines-matching/s-parameters.md
related:
  - pcb-parasitics-traces-vias-pads.md
  - resistors-at-rf.md
  - ferrites-and-beads.md
  - ../16-simulation-tools/python-rf-toolkit.md
  - ../16-simulation-tools/spice-circuit-simulation.md
  - ../16-simulation-tools/rf-circuit-simulators-harmonic-balance.md
  - ../17-test-measurement/fixtures-and-deembedding.md
  - ../17-test-measurement/vna-fundamentals-calibration.md
level: intermediate
confidence: high
last_updated: 2026-09-27
---

# Component models — vendor S-parameter files, equivalent circuits and how to use them

## Questions this page answers
- Where do I get accurate RF models for capacitors, inductors, beads and resistors?
- What is in a vendor `.s2p` file, and was it measured in series or shunt?
- Should I use the S-parameter file or the SPICE/equivalent-circuit model?
- Why doesn't my simulation with vendor models match my board?
- How do I include pads, vias and the PCB in a simulation that uses de-embedded part models?
- How can I tell if an S-parameter file is bad (non-passive, non-causal)?
- How do I use `.s2p` files in scikit-rf, QUCS-S, LTspice or a harmonic-balance simulator?
- Can S-parameter models show DC bias, saturation or temperature effects?

## TL;DR
- **Sources:** Murata SimSurfing (MLCC, inductors, beads; includes DC-bias/temperature for MLCCs; S-parameters and SPICE netlists), Coilcraft (S-parameters and SPICE for every RF inductor, generated from a fitted model), KEMET K-SIM, TDK SEAT/product-center models, Johanson/ATC design tools, Würth REDEXPERT, Vishay thin-film resistor models, and **Modelithics** substrate-scalable libraries (licensed; bundled with some simulators).
- **Know the measurement configuration.** Murata measures MLCC S-parameters in **shunt** mode (1-port/2-port shunt) on Yokowo jigs over a 100 µm glass-epoxy microstrip (≤ 8.5 GHz) or 160 µm fluorine CPW (≤ 20 GHz), with land pattern and via de-embedded, **no DC bias**. Coilcraft RF-inductor S-parameters are **generated from a fitted lumped model** (first resonance only), de-embedded to 50 Ω, excluding board effects.
- **De-embedded ≠ on your board.** Pads, vias, solder and nearby ground add capacitance/inductance: adding 0.05–0.2 pF pad capacitance to a 10 nH model (SRF 4.69 GHz) pulls the in-circuit series resonance to 4.46–3.92 GHz (script). Coilcraft notes the on-board SRF will be lower than the model's. Always cascade your own pad/via/line models.
- **Series vs shunt fixture** matters for accuracy: with a 0.01 dB/0.1° S21 error, a 0.1 Ω impedance extracted from a series-thru measurement is 209 % wrong but 0.2 % from shunt-thru; a 1 kΩ impedance is 0.2 % (series) vs 9 % (shunt). Low-Z parts (bypass caps) → shunt; high-Z parts (chokes, beads) → series.
- **Reference planes:** 1 mm of unaccounted microstrip is 2° of S21 at 915 MHz and 5.3° at 2.45 GHz (double on S11) — enough to mis-tune a sharp match.
- **S-parameters are small-signal and linear**: no saturation, no DC-bias dependence unless the vendor provides bias-specific files; for beads and Class-2 MLCCs select the bias-specific model.
- Check files: passivity ($\lambda_{max}(\mathbf S^H\mathbf S)\le1$), reciprocity ($S_{12}=S_{21}$ for passives), frequency range (don't extrapolate), header (`# Hz S MA R 50`). scikit-rf's `is_passive()`/`is_reciprocal()` catch a +0.17 dB normalisation error instantly.

## Intuition (no math)
A vendor model is a promise about a component *in a specific test setup*. The vendor mounts the part on a test board, measures it with a network analyser, and then mathematically removes ("de-embeds") the test board so that what's left is "just the part" between two reference planes. Your board is different: different pads, different distance to ground, a via, solder fillets, maybe a nearby part. At 433 MHz these differences are usually small; at 2.4 GHz and above they can be as large as the part itself.

Two kinds of models exist. **S-parameter files** are tables of measured (or model-generated) data vs frequency — accurate within their frequency range and setup, but opaque and unusable outside it (no extrapolation to DC or higher frequencies; no bias dependence). **Equivalent circuits** (SPICE subcircuits: C with ESL and ESR, L with parallel C and loss resistors) are compact, work in time-domain SPICE and at any frequency, but only approximate the real behaviour (usually good up to the first resonance). **Substrate-scalable models** (Modelithics) are equivalent circuits whose parameters are fitted over many measurements so the model can include *your* substrate thickness and εr and pad dimensions — the closest thing to "the part on your board".

## The math

### Level 1 — configurations and impedance extraction
A two-terminal part $Z$ can be measured as a two-port in two ways (ports at $Z_0$):

| | Series-thru (part in the line) | Shunt-thru (part from line to ground) |
|---|---|---|
| $S_{21}$ | $\dfrac{2Z_0}{Z+2Z_0}$ | $\dfrac{2Z}{2Z+Z_0}$ |
| $S_{11}$ | $\dfrac{Z}{Z+2Z_0}$ | $\dfrac{-Z_0}{2Z+Z_0}$ |
| Extraction | $Z=2Z_0\left(\dfrac{1}{S_{21}}-1\right)$ | $Z=\dfrac{Z_0}{2}\dfrac{S_{21}}{1-S_{21}}$ |
| Best for | $|Z|\gtrsim Z_0$ (inductors, chokes, beads, DC blocks) | $|Z|\lesssim Z_0$ (bypass caps, PDN) |

Both formulas reproduce the model to machine precision (`tools/verify/components_s2p_models.py` §1), and a Touchstone write/read round-trip is exact.

### Level 2 — sensitivity and why vendors choose a configuration
Differentiating the extraction formulas: series-thru relative error ≈ $\left|\dfrac{2Z_0+Z}{Z}\right|\cdot|\delta S_{21}/S_{21}|$ — explodes for $|Z|\ll2Z_0$; shunt-thru relative error ≈ $\left|\dfrac{2Z+Z_0}{Z_0}\right|\cdot|\delta S_{21}/S_{21}|$ — explodes for $|Z|\gg Z_0/2$. With a realistic 0.01 dB / 0.1° uncertainty (script §2):

| $|Z|$ | 10 mΩ | 0.1 Ω | 1 Ω | 10 Ω | 100 Ω | 1 kΩ | 10 kΩ |
|---|---|---|---|---|---|---|---|
| series-thru error | 2090 % | 209 % | 21 % | 2.3 % | 0.42 % | 0.23 % | 0.21 % |
| shunt-thru error | 0.21 % | 0.21 % | 0.22 % | 0.29 % | 1.05 % | 9.0 % | 95 % |

Hence Murata's shunt measurement of MLCCs (their SRF-region impedance is tens of mΩ) and the series-oriented characterisation of inductors. Note that the **mounting geometry differs** between configurations: a shunt part's current returns through its ground via; a series part's return is the plane under it. Each configuration therefore reports a different "ESL" for the same capacitor — which is part of why published ESL values vary 2–5× ([capacitors](capacitors-at-rf-mlcc.md)).

### Level 3 — using models correctly
**Mounting correction.** Build the in-circuit model as: *line/pad model* → *vendor part model* → *pad/via model*. For shunt parts add the via inductance (Goldfarb–Pucel, [PCB parasitics](pcb-parasitics-traces-vias-pads.md)). Example (script §3): a 10 nH model with $C_p=0.115$ pF (the value implied by Coilcraft's 4.7 GHz datasheet SRF) resonates at 4.69 GHz; with 0.05 / 0.10 / 0.20 pF pad capacitance to ground at each end (and a quarter of that across the part) the series-branch resonance falls to 4.46 / 4.25 / 3.92 GHz. For precise work, measure your pads (a "thru" and an empty-pad "open" on a coupon) or use EM-simulated pad S-parameters, then de-embed or embed accordingly ([fixtures and de-embedding](../17-test-measurement/fixtures-and-deembedding.md)).

**Reference planes and port impedance.** Touchstone headers state units, format and reference impedance (`# MHz S MA R 50`). The data are referenced to the vendor's reference planes (usually the part's terminations after de-embedding); line lengths you add must start there. 1 mm on FR-4 microstrip is 0.95° at 433.92 MHz, 2.0° at 915 MHz, 5.3° at 2.45 GHz, 12.7° at 5.8 GHz of transmission phase.

**Interpolation and extrapolation.** Simulators interpolate between data points (linear or spline — can create ripples if points are sparse) and must *extrapolate* to DC for transient/harmonic-balance analyses. Files that start at 10 MHz or 100 MHz make DC operating points and time-domain results questionable; prefer the equivalent-circuit model for SPICE transient work.

**Passivity and causality.** A passive part must satisfy $\lambda_{max}(\mathbf S^H\mathbf S)\le1$ at every frequency; measured files sometimes violate this slightly (noise, calibration drift, normalisation errors), which can make time-domain simulations unstable or create "gain" in a passive filter. In the script, multiplying $S_{21}$ by 1.02 (+0.17 dB) gives $\lambda_{max}=1.038$ and scikit-rf flags `is_passive() == False` and `is_reciprocal() == False`. Causality (Kramers–Kronig consistency of real and imaginary parts) matters for time-domain use; tools such as scikit-rf's vector fitting (`skrf.VectorFitting`) can produce passive, causal rational models from data.

**Large-signal and bias effects.** S-parameters describe a linear small-signal response. They cannot model inductor/bead saturation, Class-2 MLCC DC-bias loss, or nonlinearity. Murata SimSurfing and TDK SEAT provide bias- and temperature-specific MLCC and bead data; Coilcraft warns its S-parameters must not be used for large-signal loss or saturation modelling.

## Design equations & rules of thumb

| Item | Equation / rule | Notes |
|---|---|---|
| Series-thru extraction | $Z=2Z_0(1/S_{21}-1)$ | use for $|Z|\gtrsim Z_0$ |
| Shunt-thru extraction | $Z=\frac{Z_0}{2}S_{21}/(1-S_{21})$ | use for $|Z|\lesssim Z_0$ |
| Reference-plane phase | $360°\,f\sqrt{\varepsilon_{eff}}\,\ell/c$ | 1 mm: 2° @ 915 MHz |
| Passivity | $\lambda_{max}(\mathbf S^H\mathbf S)\le1$ | scikit-rf `is_passive()` |
| Model validity | SPICE models: to ~first SRF; S-params: only within file range | — |
| Mounted SRF | lower than vendor model | add pad C and via L |

## Worked examples

### 1. Simulating the 433.92 MHz harmonic LPF with vendor models (scikit-rf)
```python
import skrf as rf
from skrf.media import MLine
f = rf.Frequency(100, 3000, 2901, unit='MHz')
line = MLine(frequency=f, w=0.36e-3, h=0.2104e-3, t=35e-6, ep_r=4.4, tand=0.02)   # JLC 4-layer
C1 = rf.Network('GJM1555C1H5R6.s2p')      # vendor shunt-measured cap -> use as 2-port shunt element
L2 = rf.Network('0402HP-16N.s2p')         # vendor series inductor
pad = line.line(0.5e-3, 'm')              # 0.5 mm pad/line section
filt = pad ** C1 ** pad ** L2 ** pad      # ... continue the ladder
filt.plot_s_db()
```
(File names are illustrative; download the actual part files from Murata/Coilcraft. Note that a vendor 2-port *shunt* file already contains the part as a shunt element between two ports — cascade it directly; don't convert it to a series element.)

### 2. Why the board disagrees with the model at 2.4 GHz
A 2.4 GHz matching network built with vendor models shows a 60 MHz shift on the board. Likely culprits, in order: pad capacitance (0.05–0.1 pF each), the ground-via inductance of shunt capacitors (0.5 nH on a 1.6 mm 2-layer board = 7.7 Ω at 2.45 GHz), reference-plane offsets of ~1 mm (5° of phase), and neighbouring-part coupling. Add them to the model (or EM-simulate the layout) before blaming the vendor.

### 3. Choosing a bias-correct bead model
A 600 Ω bead on a 300 mA rail: download the model for 300 mA (SimSurfing "DC bias" setting) rather than the 0 A curve; the 100 MHz impedance may be a fraction of 600 Ω ([ferrites](ferrites-and-beads.md)).

## Practical notes
- **Keep a local model library** per project with the exact part numbers and the vendor's "readme"/measurement-condition notes; record which files are shunt- vs series-measured.
- **Qucs-S / QUCS** and **LTspice** accept S-parameter blocks (LTspice via a subcircuit with S-parameter support in recent versions, or use the SPICE netlists); **ngspice** is best used with equivalent circuits. Harmonic-balance tools (Keysight ADS, Cadence AWR, QucsStudio) handle `.snp` directly ([simulation tools](../16-simulation-tools/tool-landscape-overview.md)).
- **Modelithics** models are the gold standard for pad/substrate-aware simulation but are licensed; in a free flow, emulate them by cascading vendor data with scikit-rf pad models and validating against a VNA measurement of a test coupon.
- **Your own measurements** become models too: save NanoVNA/LibreVNA data as Touchstone, de-embed the fixture, check passivity, then reuse ([NanoVNA/LibreVNA](../17-test-measurement/nanovna-librevna-practical.md)).

## Common mistakes & misconceptions
- **Treating a de-embedded model as the in-circuit part** — forgetting pads and vias.
- **Using a shunt-measured capacitor file as a series element** (or vice versa) without converting via Z.
- **Extrapolating** an S-parameter file below its first frequency point (DC) or above its last.
- **Assuming S-parameter files include DC bias or saturation.**
- **Ignoring the file's reference impedance** or mixing files with different $Z_0$.
- **Trusting non-passive measured data** in transient simulations.
- **Believing datasheet single-number specs (SRF, Q) over the model** — datasheet SRF is fixture-dependent, as shown for the Coilcraft 0402HP series ([inductors](inductors-at-rf.md)).

## How to simulate / verify
- `python3 tools/verify/components_s2p_models.py` — builds series/shunt two-ports, Touchstone round-trip, extraction formulas, fixture sensitivity table, pad-induced SRF shift, reference-plane phase, passivity/reciprocity detection, and prints SPICE subcircuits.
- scikit-rf: `rf.Network('file.s2p')`, `.is_passive()`, `.is_reciprocal()`, cascade `**`, de-embed with `.inv`, `rf.VectorFitting` for rational models ([Python RF toolkit](../16-simulation-tools/python-rf-toolkit.md)).
- Validate on hardware: a coupon with through, open-pad and part-mounted structures, measured with a calibrated VNA.

## Open questions / gaps
- Exact measurement conditions for KEMET K-SIM and TDK SEAT S-parameter data were not retrieved in this pass (check each tool's documentation).
- LTspice's native S-parameter support details vary by version; see 16-simulation-tools.

## Sources
1. Murata, "Multilayer ceramic capacitors — S-parameter measurement conditions." https://www.murata.com/en-us/tool/data/sparameterdata/sparameter-mlcc/condition — shunt modes, jigs, substrates, de-embedding, frequency ranges, equipment. (manufacturer documentation)
2. Murata, "Design support software SimSurfing." https://www.murata.com/en-us/tool/simsurfing — S-parameter/SPICE downloads, DC-bias and temperature characteristics. (manufacturer tool)
3. Coilcraft, "S-parameters for high-frequency circuit simulations," Doc 1721, rev. 01/03/23 — model-generated inductor S-parameters, de-embedding, on-board SRF lower than model, first resonance only, small-signal only, Modelithics recommendation. https://www.coilcraft.com/getmedia/35dbfd16-8483-4ef7-bb07-9b28a04f6dcc/doc1721_When-to-Use-S-parameters.pdf (app note)
4. Coilcraft, "Spice models / S-parameters" and "How to use our models in …" pages. https://www.coilcraft.com/en-us/models/spice/ (manufacturer documentation)
5. Modelithics, vendor model datasheets (e.g. Murata GJM, Johanson R07S, Murata LQG15HS) hosted at https://www.modelithics.com/models/Vendor/ — substrate-scalable models and validity ranges. (vendor documentation)
6. Vishay, Technical Note 60107 (measurements by Modelithics; pad/transmission-line model). https://www.vishay.com/docs/60107/freqresp.pdf (app note)
7. B. Gustavsen, A. Semlyen, "Rational approximation of frequency domain responses by vector fitting," *IEEE Trans. Power Delivery*, 14(3), 1052–1061, 1999 — basis of passive/causal macromodelling (scikit-rf `VectorFitting`). (peer-reviewed)
8. D. M. Pozar, *Microwave Engineering*, 4th ed., 2012 — §4.3 S-matrix properties (unitarity/passivity), §4.4 ABCD for de-embedding. (textbook)
9. Verification script `tools/verify/components_s2p_models.py` (this KB).
