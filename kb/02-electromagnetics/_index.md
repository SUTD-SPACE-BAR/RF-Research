# 02-electromagnetics — Fields and waves

The physics underneath every RF circuit, antenna and link: Maxwell's equations and where circuit
theory comes from (and fails); plane waves in lossless and lossy media, including polarization and the
IEEE-vs-optics handedness trap; the Poynting vector, energy flow in circuits and field-strength units;
boundary conditions, reflection/refraction, radome and nose-cone walls, ground and sea reflection;
skin effect, conductor loss, copper roughness and PCB surface finishes (ENIG vs immersion silver);
dielectric and magnetic materials (Debye, Djordjevic–Sarkar, ferrites, Snoek's limit, gyrotropic
media); the quasi-static/lumped limit; radiation from currents (Hertzian dipole, small loop,
differential- vs common-mode EMC radiation); near-field vs far-field regions; waveguides, cavities, SIW
and PCB plane resonances; and inductance/capacitance defined from fields (loop vs partial inductance).
Transmission-line theory and the Smith chart live in [03](../03-transmission-lines-matching/_index.md),
antennas beyond fundamentals in [08](../08-antennas/_index.md), propagation in
[09](../09-propagation-link-budget/_index.md), PCB EMC practice in
[13](../13-pcb-rf-layout-emc/_index.md). Every numeric claim is reproduced by a script in
`tools/verify/em_*.py` (13 scripts, all passing on 2026-09-27).

## Reading order (beginner → advanced)
1. [Electromagnetic units and constants](electromagnetic-units-and-constants.md) — ε0, μ0, c, η0 after the 2019 SI; dBµV/m ↔ dBm conversions; Gaussian vs SI.
2. [Maxwell's equations](maxwells-equations.md) — the four laws in words, integral/differential/phasor forms, displacement current, constitutive relations, KVL/KCL as approximations.
3. [Wave equation, plane waves, polarization](wave-equation-plane-waves-polarization.md) — γ = α + jβ, η, lossy media, CP/AR/handedness.
4. [Poynting vector and power flow](poynting-vector-power-flow.md) — E = √(ηS), field strength from EIRP, energy flows in the fields, complex Poynting theorem.
5. [Quasi-static vs full-wave](quasi-static-vs-full-wave.md) — when a circuit is lumped (λ/10, λ/20, rise-time rules).
6. [Boundary conditions, reflection, refraction](boundary-conditions-reflection-refraction.md) — Fresnel, Brewster, TIR, radomes, CFRP, ground/sea.
7. [Skin effect, conductor loss, roughness](skin-effect-conductor-loss-roughness.md) — δ tables, R_s, Huray/Hammerstad, ENIG.
8. [Dielectrics](dielectrics-permittivity-loss-tangent.md) — ε', ε'', tanδ, Debye, Djordjevic–Sarkar, material values (FR-4, Rogers, PTFE, water, PLA/ABS…).
9. [Magnetic materials](magnetic-materials-permeability.md) — complex μ, ferrite beads, Snoek's limit, Polder tensor.
10. [Inductance and capacitance from fields](inductance-capacitance-from-fields.md) — energy definitions, loop vs partial, vias, microstrip L′/C′, fringing.
11. [Radiation from currents / Hertzian dipole](radiation-from-currents-hertzian-dipole.md) — potentials, full dipole fields, R_rad, Larmor, small loop, DM/CM radiation.
12. [Near field vs far field](near-field-far-field.md) — λ/2π, 2D²/λ, wave impedance, near-field shielding, measurement distances.
13. [Waveguides and cavity resonators](waveguides-and-cavity-resonators.md) — TE/TM modes, cutoff, v_p/v_g, loss, cavity Q, SIW, PCB plane resonances.

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [electromagnetic-units-and-constants](electromagnetic-units-and-constants.md) | CODATA 2022 μ0/ε0/Z0, μ0 = 2αh/(e²c), deviation from 4π×10⁻⁷ (−1.4×10⁻¹⁰, sign flip vs 2018), 120π error, dBµV/m/dBm/m²/dBm conversions, Gaussian↔SI, units table | mixed | high |
| [maxwells-equations](maxwells-equations.md) | integral/differential/phasor forms, displacement-current derivation, continuity, constitutive relations and their limits, σ/ωε table (Cu, sea, ground, FR-4), KVL/KCL from Faraday/continuity and their failure, charge relaxation, duality, uniqueness | mixed | high |
| [wave-equation-plane-waves-polarization](wave-equation-plane-waves-polarization.md) | Helmholtz derivation, exact α/β/η, low-loss and good-conductor limits, 27.3·tanδ dB/λ, sea/fresh water attenuation, linear/circular/elliptical polarization, Stokes/AR/XPD, IEEE vs optics handedness and time-convention traps, PLF | mixed | high |
| [poynting-vector-power-flow](poynting-vector-power-flow.md) | Poynting theorem (real and complex), Z from stored energies, E from EIRP (2 W at 1/30 km), energy flow in coax/resistive wire/two-wire line, Veritasium question, non-uniqueness, exposure-style numbers | mixed | high |
| [boundary-conditions-reflection-refraction](boundary-conditions-reflection-refraction.md) | BCs, normal/oblique Fresnel (TE/TM sign conventions), Brewster/pseudo-Brewster, TIR/evanescent, transfer matrix, half-wave/thin-wall/A-sandwich radomes, 915 MHz fibreglass nose-cone numbers, CFRP shielding, sea/ground R_H/R_V | mixed | high |
| [skin-effect-conductor-loss-roughness](skin-effect-conductor-loss-roughness.md) | δ and R_s tables (Ag/Cu/Au/Al/Ni, 1 MHz–100 GHz), derivation, Bessel wire solution, proximity effect, microstrip loss split, Hammerstad/Groiss/Huray/Cannonball, layered-finish model (ENIG, ENEPIG, ImAg, ImSn), measured finish data, Litz | mixed | high |
| [dielectrics-permittivity-loss-tangent](dielectrics-permittivity-loss-tangent.md) | complex ε, polarisation mechanisms, Debye, ITU-R P.527 water/sea model, Kramers–Kronig, Djordjevic–Sarkar with measured FR-4 parameters, anisotropy/weave/moisture/temperature, materials table (FR-4, RO4003C/4350B, PTFE, alumina, G10, PLA/ABS, water, CFRP) | mixed | medium |
| [magnetic-materials-permeability](magnetic-materials-permeability.md) | complex μ, bead impedance model, gyromagnetic resonance, Snoek's limit (units trap), mix selection (31/43/52/61/67), MnZn dimensional resonance, Polder tensor, μ±, Faraday rotation, Kittel, nickel at RF | mixed | medium |
| [quasi-static-vs-full-wave](quasi-static-vs-full-wave.md) | electrical-length table for UHF–5.8 GHz on FR-4, lumped-model error (βl)²/3, π-section S11, rise-time rules (J&G vs Bogatin), EQS/MQS time constants, what breaks (retardation, radiation, resonances) | mixed | high |
| [radiation-from-currents-hertzian-dipole](radiation-from-currents-hertzian-dipole.md) | potentials, Lorenz gauge, retarded potentials, full dipole fields (sympy-verified), R_rad 789 vs 790 Ω, triangular-current short dipole, Larmor, reactive power 1/(kr)³, small loop, DM/CM EMC formulas and µA-level CM limits | mixed | high |
| [near-field-far-field](near-field-far-field.md) | reactive/radiating/far regions with a table for Marcus's antennas, 2D²/λ phase and gain error, wave impedance vs distance (with overshoot), Schelkunoff near-field shielding, Friis validity, bench-test distances | mixed | high |
| [waveguides-and-cavity-resonators](waveguides-and-cavity-resonators.md) | TE/TM derivation, WR sizes for 433 MHz–10 GHz, dispersion, wave impedance, TE10 loss, circular modes, below-cutoff vents, cavity Q (closed form = numeric), PCB plane-pair modes, SIW | mixed | high |
| [inductance-capacitance-from-fields](inductance-capacitance-from-fields.md) | energy/flux definitions, TEM line L′/C′, fringing via FD Laplace solver, loop vs partial inductance (Ruehli/Paul), Neumann check, via and bond-wire inductance (J&G discrepancy), coaxial-loop mutual inductance | mixed | high |
| [greens-functions-and-integral-equations](greens-functions-and-integral-equations.md) | scalar & dyadic Green's function derived (sympy), EFIE/MFIE/CFIE, Pocklington & Hallén (own Hallén vs Galerkin MPIE 80.4+j45.4 vs 80.2+j45.0 Ω), square-plate MoM, Sommerfeld identity, layered media & surface-wave pole, why planar solvers use them | advanced | high |

## Domain FAQ (top questions → page#section)
- *Is μ0 still exactly 4π×10⁻⁷, and does it matter?* → [constants § Level 2](electromagnetic-units-and-constants.md#level-2--where-μ0-comes-from-now)
- *How do I convert dBm received into dBµV/m?* → [constants § log units](electromagnetic-units-and-constants.md#level-2--log-units-for-field-strength)
- *What field does my 2 W 433 MHz transmitter make at 1 km / 30 km?* → [Poynting § Worked examples](poynting-vector-power-flow.md#worked-examples)
- *Does energy flow in the wire or around it?* → [Poynting § where the energy flows](poynting-vector-power-flow.md#level-2--where-the-energy-flows-in-real-circuits)
- *What is displacement current and why does it matter for radio?* → [Maxwell § Level 2](maxwells-equations.md#level-2--differential-forms)
- *When does KVL fail? Why does my scope ground lead pick up noise?* → [Maxwell § Level 3](maxwells-equations.md#level-3--from-maxwell-to-kirchhoff-and-when-it-fails)
- *Which way does RHCP rotate? Why do optics books disagree?* → [plane waves § polarization](wave-equation-plane-waves-polarization.md#level-2--polarization)
- *How much do I lose receiving CP with a linear antenna?* → [plane waves § Level 3](wave-equation-plane-waves-polarization.md#level-3--polarization-mismatch-and-the-general-lossy-medium)
- *How fast does 433 MHz die in sea water?* → [plane waves § Worked example 2](wave-equation-plane-waves-polarization.md#worked-examples)
- *How thick can my fibreglass nose cone be at 915 MHz?* → [reflection § Worked example 1](boundary-conditions-reflection-refraction.md#worked-examples)
- *Can I put an antenna inside a carbon-fibre airframe?* → [reflection § conducting walls](boundary-conditions-reflection-refraction.md#level-3--conducting-walls-lossy-half-spaces-and-limits-of-the-plane-wave-model)
- *Why is vertical polarization better over the sea?* → [reflection § pseudo-Brewster](boundary-conditions-reflection-refraction.md#level-2--oblique-incidence-snell-and-fresnel)
- *What is the skin depth of copper at 433 MHz / 2.4 GHz?* → [skin effect § tables](skin-effect-conductor-loss-roughness.md#level-1--skin-depth-and-surface-resistance)
- *Is ENIG bad for RF? Immersion silver vs ENIG?* → [skin effect § plating](skin-effect-conductor-loss-roughness.md#level-3--plating-and-surface-finishes)
- *Which roughness model should I use?* → [skin effect § roughness](skin-effect-conductor-loss-roughness.md#level-3--surface-roughness)
- *What Dk/Df should I use for FR-4, RO4003C, PLA?* → [dielectrics § Material values](dielectrics-permittivity-loss-tangent.md#material-values)
- *Why does FR-4's Dk change with frequency? What is Djordjevic–Sarkar?* → [dielectrics § Level 3](dielectrics-permittivity-loss-tangent.md#level-3--the-djordjevicsarkar-wideband-debye-model)
- *Which ferrite mix for 433/915 MHz? Why is a bead a resistor?* → [magnetics § Level 2](magnetic-materials-permeability.md#level-2--spin-resonance-relaxation-and-snoeks-limit)
- *How do circulators work (why ferrite)?* → [magnetics § Polder tensor](magnetic-materials-permeability.md#level-3--gyrotropic-ferrites-the-polder-tensor)
- *When is a trace a transmission line?* → [quasi-static § Level 2](quasi-static-vs-full-wave.md#level-2--how-big-the-lumped-model-error-is)
- *What's the inductance of a via / trace / bond wire?* → [L and C § partial inductance](inductance-capacitance-from-fields.md#level-3--loop-vs-partial-inductance)
- *Why do cables radiate more than PCB loops?* → [radiation § DM vs CM](radiation-from-currents-hertzian-dipole.md#level-3--differential-mode-vs-common-mode-radiation-emc)
- *Where does 80π²(l/λ)² come from?* → [radiation § Level 2](radiation-from-currents-hertzian-dipole.md#level-2--phasor-form-and-the-hertzian-dipole)
- *How far away must I be to measure my Yagi?* → [near/far field § Worked examples](near-field-far-field.md#worked-examples)
- *Why are low-frequency magnetic fields hard to shield?* → [near/far field § Level 3](near-field-far-field.md#level-3--near-field-shielding-schelkunoff)
- *Why does my PCB resonate at a few hundred MHz?* → [waveguides § cavities](waveguides-and-cavity-resonators.md#level-3--cavity-resonators)
- *Phase velocity faster than light in a waveguide?* → [waveguides § Common mistakes](waveguides-and-cavity-resonators.md#common-mistakes--misconceptions)

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
Griffiths (*Introduction to Electrodynamics*), Cheng (*Field and Wave Electromagnetics*), Ramo–Whinnery–
Van Duzer, Pozar (*Microwave Engineering*), Balanis (*Advanced Engineering Electromagnetics*, *Antenna
Theory*), Harrington (*Time-Harmonic Electromagnetic Fields*), Jackson, Haus & Melcher (free, MIT),
Orfanidis (free, Rutgers), Feynman Vol. II (free), Clayton Paul (*Inductance: Loop and Partial*;
*Introduction to EMC*), Ott; papers: Djordjevic et al. 2001 (FR-4), Huray et al. 2010 (roughness),
Groiss et al. 1996, Hammerstad & Jensen 1980, Snoek 1948; data: NIST CODATA 2022, BIPM SI Brochure,
ITU-R P.527-6, P.368-10, CRC resistivities, Rogers datasheets.

## Known gaps
- Several material values (PTFE, alumina, G10, Kapton, solder mask, TCDk, moisture uptake) are from
  well-known datasheets but not re-fetched → medium confidence; a pass should fetch primary datasheets.
- ENIG nickel: resistivity vs phosphorus and effective μr(f) only bracketed; need a peer-reviewed
  measurement.
- Hand-laid rocket fibreglass Dk/Df and measured detuning of 433/915 MHz antennas inside nose cones —
  measure (08-antennas / 17-test).
- CFRP conductivity values from secondary summaries; anisotropic ply-by-ply transmission not modelled.
- Johnson & Graham via formula and rise-time rules quoted from knowledge (books not re-read).
- IEEE Std 145/211 polarization definitions quoted via secondary sources.
- Orfanidis (Rutgers) and Feynman Lectures sites were blocked (HTTP 403) during research; cited at
  chapter level from knowledge.
