---
title: Quasi-static vs full-wave — when is a circuit "lumped"?
domain: 02-electromagnetics
slug: quasi-static-vs-full-wave
tags: [lumped, distributed, electrical-length, quasistatic, EQS, MQS, retardation, rise-time, knee-frequency, lambda-over-10, transmission-line-criterion, radiation]
prerequisites: [maxwells-equations.md, wave-equation-plane-waves-polarization.md]
related: [radiation-from-currents-hertzian-dipole.md, inductance-capacitance-from-fields.md, near-field-far-field.md, ../03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md, ../01-circuit-theory/lumped-elements-impedance-admittance.md, ../04-real-components-hf/pcb-parasitics-traces-vias-pads.md, ../16-simulation-tools/em-solvers-fdtd-mom-fem.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Quasi-static vs full-wave — when is a circuit "lumped"?

## Questions this page answers
- When can I treat a PCB trace as just a wire, and when must I treat it as a transmission line?
- Where do the "λ/10" and "λ/20" rules come from, and how wrong is a lumped model at those sizes?
- How do I decide from a digital signal's rise time rather than its clock frequency?
- What exactly "breaks" when a circuit gets electrically large: phase, impedance, radiation, KVL?
- What are electroquasistatic (EQS) and magnetoquasistatic (MQS) approximations?
- How big is "small" at 433 MHz, 915 MHz, 2.4 GHz on FR-4?

## TL;DR
- A structure is **lumped** when its size ℓ ≪ λ in the medium (λ = λ0/√ε_eff), equivalently when the propagation delay across it ≪ the signal's period or rise time. Then fields are quasi-static, retardation is negligible and KVL/KCL hold (see [Maxwell](maxwells-equations.md)) [1][2].
- **How wrong is lumped?** A short-circuited (open) stub modelled as a pure L (C) has reactance error ≈ (βℓ)²/3: **0.5 % at λ/50, 3.3 % at λ/20, 13 % at λ/10, 21 % at λ/8** (`tools/verify/em_quasistatic.py`). A single π-section model of a matched line: |S11| = −48 dB at λ/20, −30 dB at λ/10, −12 dB at λ/5.
- **Rule of thumb**: ℓ < λ/20 for accurate component-level modelling (matching networks, filters), ℓ < λ/10 for "roughly lumped". On FR-4 microstrip (ε_eff ≈ 3.3): **λ/10 = 38 mm at 433 MHz, 18 mm at 915 MHz, 6.7 mm at 2.45 GHz**; λ/20 is half that.
- **Digital edges**: lumped if ℓ < t_r/(6 t_pd) (Johnson & Graham) — ~5–6 ps/mm t_pd on FR-4 → 1 ns edge: ≈ 27 mm. Bogatin's variant (reflections matter when delay > 20 % of t_r) gives ≈ 33 mm. Spectral content: f_knee ≈ 0.5/t_r (Johnson & Graham) or BW ≈ 0.35/t_r (single-pole 10–90 %) [3][4].
- Electrical size also governs **radiation**: a wire of length ℓ with uniform current has R_rad = 80π²(ℓ/λ)² — **7.9 Ω at λ/10**, already significant beside 50 Ω; a loop radiates ∝ (C/λ)⁴ and stays negligible much longer.
- **EQS vs MQS** (Haus & Melcher): quasistatics requires τ_em = ℓ/c ≪ the time scale of interest; then either E-energy (EQS: capacitors, high-impedance) or H-energy (MQS: inductors, low-impedance) dominates, and charge relaxation τ_e = ε/σ and magnetic diffusion τ_m = μσℓ² decide which, with τ_em² = τ_eτ_m [2].

## Intuition (no math)
Every field change travels at a finite speed. If the far end of a circuit learns of a change at the
near end almost instantly compared with how fast the signal is changing, the whole circuit moves in
lockstep and "the voltage at a node" is a single, well-defined number. That's the lumped world.

When the signal changes significantly during the travel time — the circuit is a sizeable fraction of
a wavelength, or a rise time is shorter than a few round trips — different parts of the same wire
carry different voltages and currents at the same moment. Now the geometry *is* the circuit: a trace
has a characteristic impedance, reflections occur at discontinuities, stubs become resonators, and
currents that don't close in a small loop radiate.

The transition is gradual, not a cliff at λ/10. What you can tolerate depends on what you need:
a 13 % error in an inductor value (λ/10) is fine for a bias choke but disastrous for a narrowband
matching network at 915 MHz; 8 Ω of radiation resistance is noise in a power rail but a real antenna in
an EMC test.

## The math

### Level 1 — electrical length

$$\theta = \beta\ell = \frac{2\pi\ell}{\lambda_g} = \frac{2\pi f\ell\sqrt{\varepsilon_\text{eff}}}{c},\qquad t_\text{pd} = \frac{\sqrt{\varepsilon_\text{eff}}}{c}\ \ (\text{s/m}).$$
ℓ: physical length (m); λ_g: guided wavelength; ε_eff: effective permittivity of the line (microstrip
on FR-4 ≈ 3.2–3.4; stripline = εr ≈ 4.4); t_pd: propagation delay per unit length (FR-4 microstrip
≈ 6.1 ps/mm, stripline ≈ 7.0 ps/mm).

| f | λ0 | λ_g microstrip (ε_eff 3.3) | λ/10 | λ/20 | stripline λ/10 (εr 4.4) |
|---|---|---|---|---|---|
| 13.56 MHz | 22.1 m | 12.2 m | 1.22 m | 0.61 m | 1.05 m |
| 100 MHz | 3.00 m | 1.65 m | 165 mm | 83 mm | 143 mm |
| 433 MHz | 69.2 cm | 38.1 cm | 38 mm | 19 mm | 33 mm |
| 915 MHz | 32.8 cm | 18.0 cm | 18 mm | 9.0 mm | 15.6 mm |
| 1575.42 MHz | 19.0 cm | 10.5 cm | 10.5 mm | 5.2 mm | 9.1 mm |
| 2.45 GHz | 12.2 cm | 6.74 cm | 6.7 mm | 3.4 mm | 5.8 mm |
| 5.8 GHz | 5.17 cm | 2.85 cm | 2.8 mm | 1.4 mm | 2.5 mm |

(ε_eff = 3.3 is a representative 50 Ω FR-4 microstrip value; see
[planar lines](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md).)

### Level 2 — how big the lumped-model error is

**Stubs.** A lossless line of length ℓ terminated in a short has Z_in = jZ0 tan βℓ; the lumped model
is an inductor L = Z0ℓ/v (i.e. jZ0βℓ). An open stub has Z_in = −jZ0 cot βℓ vs a capacitor C = ℓ/(Z0v).
Expanding tan x = x + x³/3 + …:
$$\frac{Z_\text{exact} - Z_\text{lumped}}{Z_\text{exact}} \approx \frac{(\beta\ell)^2}{3}.$$
Exact errors (script): λ/50 → 0.53 %; λ/20 → 3.3 % (L) / 3.4 % (C); λ/10 → 13.5 % / 15.6 %; λ/8 → 21 %
/ 27 %; λ/6 → 40 % / 65 %. So "λ/10" means "about 10–15 % reactance error"; "λ/20" means ~3 %.

**Through-lines.** A matched line of length ℓ modelled by one C/2–L–C/2 π-section (L and C equal to the
line's totals): phase error 0.08° and |S11| = −48 dB at λ/20; 0.66° and −30 dB at λ/10; 6° and −12 dB at
λ/5 (script). Several cascaded sections (≥ 10 per wavelength) push the valid range up — the basis of
SPICE "lumped line" models.

**Why it matters for matching networks.** A 915 MHz L-network with a 10 nH series inductor realised
as a 9 mm (λ/20) trace section already has a 3 % reactance error plus shunt capacitance; at λ/10 the
match can be several dB off. Keep matching components tight (0402, adjacent pads) and include pad/trace
lengths in the model (see [PCB parasitics](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md)).

### Level 2 — rise-time criteria (digital signals)

A digital edge with 10–90 % rise time t_r has significant spectral content up to about
- BW ≈ 0.35/t_r (exact for a single-pole/Gaussian-like edge, 10–90 %), or
- f_knee ≈ 0.5/t_r (Johnson & Graham's "knee frequency", beyond which the spectrum falls faster
  than 20 dB/decade) [3].

Published "lumped if…" criteria differ (this is a genuine inconsistency between popular sources):

| Rule | Condition for lumped | 1 ns edge on FR-4 microstrip | Source |
|---|---|---|---|
| Johnson & Graham | ℓ < t_r/(6 t_pd) ("1/6 of the edge's electrical length") | 27.5 mm | [3] |
| Bogatin | delay TD < 20 % of t_r (ℓ < t_r/(5 t_pd)) | 33 mm | [4] |
| "Critical length" (reflection just completes within the edge) | ℓ < t_r/(2 t_pd) | 82 mm | common SI heuristic |

The first two are close (within 20 %); the third is a *different* question (when a round trip of an
unterminated line fits inside the edge) and should not be used as a lumped criterion. Rule of thumb
compatible with all: **if the trace's one-way delay is < t_r/6, ignore transmission-line effects;
if it is > t_r/2, you must terminate.** In between, ringing is visible and termination is advisable.

Example: an SPI or I²C bus with 2 ns edges: t_r/(6t_pd) = 55 mm; a 10 cm flight-computer bus
between boards is *not* lumped even though the clock is only 10 MHz. The rise time, not the clock rate,
sets the physics.

### Level 3 — Haus & Melcher quasistatics (EQS / MQS) and what breaks

Haus & Melcher [2] (ch. 3) formalise the approximation by comparing three time constants for a
system of size ℓ, permittivity ε, permeability μ, conductivity σ:
- electromagnetic transit time **τ_em = ℓ√(με) = ℓ/v**;
- charge relaxation time **τ_e = ε/σ**;
- magnetic diffusion time **τ_m = μσℓ²** (time for a field to diffuse into a conductor of size ℓ;
  ~skin-depth physics).

They satisfy **τ_em² = τ_e τ_m** (checked in the script). Fields are quasistatic when the time scale of
interest τ (≈ 1/ω or t_r) ≫ τ_em. Then one of two limits applies:
- **Electroquasistatic (EQS)**: electric energy dominates; ∇×**E** ≈ 0 (E is a gradient of a potential),
  but ∂**D**/∂t is kept in charge conservation. Capacitors, high-impedance nodes, electrostatic
  discharge, dielectric sensors, the body at UHF (τ_e ≈ 0.9 ns for εr 50, σ 0.5 S/m).
- **Magnetoquasistatic (MQS)**: magnetic energy dominates; ∂**D**/∂t is dropped from Ampère's law
  (∇×**H** ≈ **J**, so ∇·**J** ≈ 0 and KCL holds), but Faraday's law is kept. Inductors, transformers,
  eddy currents, skin effect (τ_m of a 10 cm copper piece is 0.7 s — so even at 1 kHz the field doesn't
  penetrate copper bulk).

Circuit theory is the **dual quasistatic** limit: EQS inside capacitors, MQS inside inductors,
negligible fields (or lumped parasitics) in the wiring.

**What breaks as size grows** (all scale with ℓ/λ):
1. *Retardation / phase*: different parts of the circuit are at different phases (βℓ). Voltage becomes
   position dependent → transmission lines.
2. *Path-dependent voltage*: Faraday EMF in un-modelled loops (∝ ω × loop area) — the start of KVL
   failure, significant long before λ/10 at high currents.
3. *Radiation*: power leaves as waves. Short wire (uniform current): R_rad = 80π²(ℓ/λ)² → 0.08 Ω at
   λ/100, 2.0 Ω at λ/20, 7.9 Ω at λ/10; with a triangular current (open-ended short dipole) 4× less.
   Loop of circumference C: R_rad = 20π²(C/λ)⁴ → 0.02 Ω at C = λ/10. Radiation from *common-mode*
   currents on cables is the dominant EMC problem because cables are electrically long (see
   [radiation](radiation-from-currents-hertzian-dipole.md)).
4. *Distributed resonances*: a structure ≈ λ/4 (open–short) or λ/2 long resonates — ground-plane and
   enclosure resonances, via stubs, parasitic self-resonance of components.
5. *Higher-order modes*: when the cross-section approaches λ/2 (wide microstrip, coax, enclosures),
   non-TEM modes propagate (see [waveguides](waveguides-and-cavity-resonators.md)).

**Full-wave tools** (FDTD, FEM, MoM) solve Maxwell without these approximations; quasi-static
extractors (2D field solvers for Z0, RLGC extractors, Q3D-type tools, FastHenry/FastCap) are valid
only when the extracted structure is small or uniform along its length.

## Design equations & rules of thumb

| Equation | When valid | Typical value |
|---|---|---|
| λ_g = c/(f√ε_eff) | low-loss line | FR-4 µstrip 915 MHz: 18.0 cm |
| Lumped reactance error ≈ (βℓ)²/3 | short stub/element | λ/10: 13 %; λ/20: 3.3 % |
| Lumped if ℓ < λ/20 (accurate), λ/10 (rough) | sinusoidal RF | 433 MHz FR-4: 19 / 38 mm |
| Lumped if ℓ < t_r/(6 t_pd) | digital edges | 1 ns: ≈ 27 mm on FR-4 |
| Terminate if ℓ > t_r/(2 t_pd) | digital edges | 1 ns: ≈ 82 mm |
| f_knee ≈ 0.5/t_r; BW ≈ 0.35/t_r | edge spectrum | 1 ns: 500 / 350 MHz |
| R_rad ≈ 80π²(ℓ/λ)² (uniform I) | short wire | λ/10: 7.9 Ω |
| τ_em² = τ_eτ_m; quasistatic if τ ≫ τ_em | any system | 10 cm board: τ_em ≈ 0.3–0.7 ns |

## Worked examples

**1. 433 MHz LoRa module on a flight-computer board.** The trace from the E22 module's RF pin to the
SMA is 25 mm of 50 Ω microstrip on FR-4. λ_g ≈ 381 mm → 25 mm = λ/15 (βℓ = 24°). Is it lumped? For
*matching* purposes it's a 24° section of 50 Ω line — harmless if the line is 50 Ω (a matched line of
any length is transparent) but it rotates any mismatch around the Smith chart by 48°. If the trace were
80 Ω (too narrow), it would act as an inductor-like discontinuity with ~7 % error from a lumped model.
Treat it as a transmission line and make it 50 Ω.

**2. 915 MHz matching network.** A π-match with 0402 parts spread over 6 mm: 6/180 = λ/30, βℓ = 12°
→ lumped reactance error ≈ 1.5 %; acceptable, but include pad capacitance (~0.05–0.1 pF each) and the
interconnect inductance (~0.5–1 nH/mm-ish for thin traces — see
[inductance from fields](inductance-capacitance-from-fields.md)).

**3. 2.45 GHz on the same board.** λ/20 = 3.4 mm: a matching network spread over 6 mm is λ/11 —
design it with transmission-line sections (or simulate with the layout).

**4. Digital bus between two boards.** 2 ns edges, 120 mm of ribbon cable (t_pd ≈ 5 ps/mm): delay
0.6 ns; t_r/6 = 0.33 ns < 0.6 ns < t_r/2 = 1 ns → ringing likely; add series termination at the
driver.

## Practical notes
- "Lumped" is a modelling decision per question: the same 20 mm trace is lumped for its DC resistance,
  not lumped for its phase at 915 MHz, and possibly an antenna for a 1.5 GHz harmonic.
- Component packages have electrical size too: an 0603 inductor at 5.8 GHz is λ/20 of *itself*, and
  its self-resonance is a distributed effect captured by S-parameter models, not ideal L
  ([component models](../04-real-components-hf/component-models-s2p-spice.md)).
- Ground planes and enclosures resonate when a dimension reaches λ/2 in the dielectric: a 100 mm ×
  50 mm FR-4 board's parallel-plate (power/ground) cavity has its first mode near
  c/(2·0.1·√4.4) ≈ 715 MHz — right between Marcus's LoRa bands (see
  [waveguides/cavities](waveguides-and-cavity-resonators.md), 13-pcb PDN).

## Common mistakes & misconceptions
- **"It's only a 10 MHz clock, so no transmission-line effects."** The edge rate sets the bandwidth.
- **"λ/10 is a hard threshold."** It is a ~13 % reactance-error point; choose the threshold from the
  accuracy you need.
- **"Lumped means no radiation."** A λ/20 wire with uniform current still has ~2 Ω radiation resistance;
  EMC failures come from electrically-small-but-not-negligible structures carrying large currents.
- **Using the free-space wavelength.** On FR-4 the guided wavelength is ~0.55 λ0 (microstrip) or 0.48 λ0
  (stripline).
- **"KVL holds as long as the circuit is small."** Small *and* without un-modelled flux linkage;
  large currents near a small loop can still induce significant EMF.

## How to simulate / verify
- `python3 tools/verify/em_quasistatic.py` — stub reactance error vs (βℓ)²/3; π-section vs exact line
  (phase, S11); radiation resistance of short wires/loops; electrical-length table; rise-time rule
  comparison; Haus & Melcher time constants and τ_em² = τ_eτ_m.
- scikit-rf: compare `line.line(d, 'mm')` against a lumped `inductor`/`capacitor` network on a Smith
  chart as frequency sweeps.
- SPICE: model a trace as N LC sections vs a lossless T-line element (`T`/`TLINE`); increase N until
  results converge — N ≥ 10 per wavelength at the highest frequency of interest.

## Open questions / gaps
- The Johnson & Graham "1/6" and Bogatin "20 %" rules are quoted from knowledge of those books (not
  re-read this session); the page states them as rules of thumb, which is how the books present them.

## Sources
1. S. Ramo, J. R. Whinnery, T. Van Duzer, *Fields and Waves in Communication Electronics*, 3rd ed.,
   1994, ch. 4 (circuit concepts from field theory; when lumped elements apply) and ch. 5. (textbook)
2. H. A. Haus and J. R. Melcher, *Electromagnetic Fields and Energy*, 1989 (free: MIT OCW RES.6-001;
   web.mit.edu/6.013_book), ch. 3 "Introduction to the electroquasistatic and magnetoquasistatic
   fields": §3.3 conditions for fields to be quasistatic; ch. 7 (charge relaxation), ch. 10 (magnetic
   diffusion). (textbook, free)
3. H. W. Johnson and M. Graham, *High-Speed Digital Design: A Handbook of Black Magic*, Prentice Hall
   1993, ch. 1 (knee frequency 0.5/t_r; lumped vs distributed criterion ~1/6 of the edge's
   electrical length). (textbook; chapter numbers checked against the publisher table of contents (sigcon.com HSDD ToC, W5-S18/S18b 2026-10-13); content cited from knowledge)
4. E. Bogatin, *Signal and Power Integrity — Simplified*, 3rd ed., Prentice Hall 2018, ch. 7–8
   (bandwidth 0.35/t_r; when a line needs termination: TD > 20 % of rise time). (textbook; cited from
   knowledge)
5. D. M. Pozar, *Microwave Engineering*, 4th ed., §2.1 (lumped-element circuit model of a line and its
   validity; Δz ≪ λ). (textbook)
6. C. A. Balanis, *Antenna Theory*, 4th ed., §4.2 (radiation resistance of infinitesimal and small
   dipoles), §5.2 (small loop). (textbook)
