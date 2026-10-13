---
title: Dielectrics — complex permittivity, loss tangent, dispersion and material values
domain: 02-electromagnetics
slug: dielectrics-permittivity-loss-tangent
tags: [permittivity, dielectric-constant, Dk, Df, loss-tangent, debye, djordjevic-sarkar, kramers-kronig, FR-4, rogers, RO4003C, RO4350B, PTFE, alumina, water, fibreglass, G10, PLA, ABS, 3D-printing, anisotropy, moisture]
prerequisites: [maxwells-equations.md, wave-equation-plane-waves-polarization.md]
related: [skin-effect-conductor-loss-roughness.md, boundary-conditions-reflection-refraction.md, magnetic-materials-permeability.md, ../13-pcb-rf-layout-emc/stackups-and-materials.md, ../18-components-parts/pcb-substrates-parts.md, ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md, ../04-real-components-hf/capacitors-at-rf-mlcc.md]
level: mixed
confidence: medium
last_updated: 2026-10-03
---

# Dielectrics — complex permittivity, loss tangent, dispersion and material values

## Questions this page answers
- What do Dk, Df, εr, ε', ε'' and tanδ mean and how are they related?
- Why do materials polarise, and why does that cause loss?
- What is a Debye relaxation, and why does FR-4's permittivity drift slowly with frequency?
- What is the Djordjevic–Sarkar (wideband Debye) model and why do simulators insist on it?
- Why does a Rogers datasheet give two different Dk values ("process" and "design")?
- What εr and tanδ should I use for FR-4, RO4003C, RO4350B, PTFE, alumina, fibreglass, water, PLA/ABS 3D-printed parts?
- How much do glass weave, moisture and temperature change the numbers?
- Is carbon fibre a dielectric?

## TL;DR
- **Complex relative permittivity** (e^{jωt}): ε_r = ε' − jε''; **tanδ = ε''/ε'** (includes conduction σ/(ωε0) if present). Datasheets: **Dk = ε'**, **Df = tanδ** [1][2].
- Loss per wavelength in a TEM medium ≈ 27.3·tanδ dB — so a constant-tanδ material's loss per metre grows ∝ f.
- Polarisation mechanisms: electronic (optical), ionic (IR), orientational/dipolar (µwave: water), interfacial/space-charge (low f, composites). Each gives a dispersion step in ε' and a loss peak in ε''.
- **Debye relaxation**: ε = ε∞ + Δε/(1 + jωτ); ε'' peaks (= Δε/2) at ωτ = 1. Water at 20 °C relaxes at ≈ 17 GHz (ITU-R P.527-6) — which is why water is so lossy at 2.45 GHz [3].
- **Causality**: ε' and ε'' are tied by Kramers–Kronig. A *constant* Dk with *constant* Df is non-causal; the **Djordjevic–Sarkar** model ε = ε∞ + Δε/(ln(ω₂/ω₁))·ln((ω₂ + jω)/(ω₁ + jω)) gives nearly flat Df and Dk falling slowly with log f (FR-4 measured: ≈ −0.14 per decade, 10 kHz–10 GHz) [4].
- **Typical values** (details and sources in table): FR-4 Dk ≈ 4.3–4.7 at 1 GHz, Df ≈ 0.015–0.022; **RO4003C design Dk 3.55, Df 0.0027 @10 GHz**; **RO4350B design Dk 3.66, Df 0.0037 @10 GHz** [5]; PTFE ≈ 2.1, Df ~ 2–4×10⁻⁴; alumina 99.5 % ≈ 9.8; fibreglass/G10 ≈ 4.2–5.2; **printed ABS 2.57, Df 0.0047 @15 GHz** [6]; **printed PLA ≈ 2.5–2.8, Df ≈ 0.01–0.02** [7][8]; water ≈ 80 − j1.9 at 433 MHz (20 °C).
- Glass-weave laminates are **anisotropic** (in-plane Dk > z-axis Dk, up to ~10 % by bounding estimates) and locally inhomogeneous (fibre-weave effect).
- **Carbon fibre composites are conductors**, not dielectrics (see [reflection page](boundary-conditions-reflection-refraction.md)).

## Intuition (no math)
A dielectric is full of charges that can't flow but can *shift*: electron clouds distort around
nuclei, ions in a crystal lattice move slightly, polar molecules (like water) rotate to line up with
the field. Each shift makes a tiny dipole whose field partly cancels the applied field. The material
therefore stores more electric energy for a given voltage — its permittivity is larger than vacuum's —
and waves travel more slowly through it.

Shifting charges takes time and costs friction. If the field oscillates slowly, the dipoles keep
up, store energy and give it back each cycle (little loss). If the field oscillates much faster than
they can respond, they don't move at all (no contribution to ε, no loss). In between — around their
"relaxation frequency" — they move but lag behind, and the lag dissipates energy as heat. That's the
loss tangent. Water molecules have their big rotational relaxation near 17–20 GHz, which is why a
microwave oven at 2.45 GHz heats water efficiently but doesn't need to be at the peak (it would heat
only the surface layer).

PCB laminates like FR-4 are a messy mixture (epoxy, glass, fillers) with a huge spread of relaxation
times, so instead of a single loss peak they have a nearly flat loss tangent over many decades — and,
by causality, a permittivity that drifts slowly downward with frequency.

## The math

### Level 1 — definitions

$$\mathbf D = \varepsilon_0\varepsilon_r\mathbf E,\qquad \varepsilon_r = \varepsilon' - j\varepsilon'',\qquad \tan\delta = \frac{\varepsilon''}{\varepsilon'} + \frac{\sigma}{\omega\varepsilon_0\varepsilon'}.$$
- ε' (Dk): energy storage; sets wavelength (λ = λ0/√ε' for low loss), impedance, capacitance.
- ε'' (and σ): energy loss. Power dissipated per unit volume = ½ωε0ε''|E|² (peak phasors).
- Physics texts using e^{−iωt} write ε = ε' + iε''; the sign of the imaginary part flips, not the physics.
- For an RC-circuit picture: a capacitor filled with the dielectric has C = ε0ε'A/d in parallel with
  conductance G = ωε0ε''A/d, so its quality factor is Q = 1/tanδ (e.g. Df = 0.02 → Q = 50; C0G MLCC
  dielectrics have Df ~ 10⁻⁴ → Q ~ 10⁴ from the dielectric alone).

Loss rules (low loss, TEM or plane wave; derived in
[plane waves](wave-equation-plane-waves-polarization.md)):
$$\alpha_d \approx \frac{\beta}{2}\tan\delta\ \text{Np/m}\ \Rightarrow\ 27.3\tan\delta\ \text{dB per wavelength} \approx 91\,f_\text{GHz}\sqrt{\varepsilon'}\tan\delta\ \text{dB/m}.$$
Microstrip: multiply by the filling factor q = ε'(ε_eff − 1)/(ε_eff(ε' − 1)) (Pozar §3.8).

### Level 2 — polarisation mechanisms and the Debye model

| Mechanism | What moves | Typical relaxation/resonance | Relevance |
|---|---|---|---|
| Electronic | electron cloud vs nucleus | UV/optical (~10¹⁵ Hz), resonant | sets ε∞ (≈ n² optical) |
| Ionic / atomic | ions in lattice | infrared (~10¹³ Hz), resonant | ceramics (alumina εr 9.8, BaTiO₃ huge) |
| Orientational (dipolar) | permanent molecular dipoles rotate | kHz–GHz, relaxation | water (≈ 17 GHz), polar polymers, epoxy |
| Interfacial (Maxwell–Wagner) | charges pile up at internal interfaces | mHz–MHz | composites, moist materials, electrolytic caps |

**Debye model** (one relaxation time τ). A population of dipoles relaxing toward equilibrium
with dP/dt = (ε0Δε E − P)/τ gives, in the frequency domain,
$$\varepsilon_r(\omega) = \varepsilon_\infty + \frac{\varepsilon_s - \varepsilon_\infty}{1 + j\omega\tau},\qquad \varepsilon' = \varepsilon_\infty + \frac{\Delta\varepsilon}{1+\omega^2\tau^2},\qquad \varepsilon'' = \frac{\Delta\varepsilon\,\omega\tau}{1+\omega^2\tau^2}.$$
ε'' peaks at ωτ = 1 with value Δε/2 (checked in `tools/verify/em_dielectrics.py`); ε' falls by Δε
across ~2 decades centred there. The equivalent circuit is C∞ in parallel with a series R–C branch —
the same model used for dielectric absorption in capacitors.

**Water (ITU-R P.527-6, double Debye)** [3]. Pure water at T °C: ε_s = 77.66 + 103.3Θ,
ε₁ = 0.0671ε_s, ε∞ = 3.52 − 7.52Θ, Θ = 300/(T + 273.15) − 1, principal relaxation
f₁ = 20.20 − 146.4Θ + 316Θ² GHz, secondary f₂ = 39.8f₁; sea water adds salinity corrections and an
ionic conductivity term (≈ 4.8 S/m at 20 °C, 35 g/kg). Script results at 20 °C:

| f | Pure water ε' | ε'' | tanδ | α (dB/m) | Sea water ε' | ε'' | α (dB/m) |
|---|---|---|---|---|---|---|---|
| 433 MHz | 80.0 | 1.91 | 0.024 | 8.4 | 71.6 | 200.6 | 663 |
| 915 MHz | 79.9 | 4.02 | 0.050 | 37.5 | 71.5 | 97.2 | 826 |
| 1.575 GHz | 79.4 | 6.89 | 0.087 | 111 | 71.3 | 59.8 | 946 |
| 2.45 GHz | 78.6 | 10.6 | 0.135 | 266 | 70.8 | 43.0 | 1093 |
| 10 GHz | 60.8 | 32.7 | 0.54 | 3700 | 59.2 | 34.7 | 3950 |

(f₁ = 17.0 GHz for pure water at 20 °C; Kaatze 1989 gives τ = 8.27 ps at 25 °C, i.e.
f = 1/(2πτ) = 19.2 GHz [9] — consistent with the temperature trend.) Practical meaning: rain, wet
foliage, people and wet ground are lossy at UHF; a wet radome or a soggy parachute bag matters more
than its dry material.

### Level 2 — causality and Kramers–Kronig

Because D(t) can only depend on past E(t), ε(ω) − ε∞ is analytic in the lower half ω-plane (e^{jωt}),
which forces
$$\varepsilon'(\omega) - \varepsilon_\infty = \frac{2}{\pi}\,\mathrm{P}\!\!\int_0^\infty\frac{x\,\varepsilon''(x)}{x^2-\omega^2}\,dx.$$
Any loss therefore implies dispersion. The script evaluates this integral numerically for a Debye
material and recovers ε' within ~1 % in the loss region. Consequences:
- Df constant over all frequencies with Dk constant is **impossible** (non-causal); time-domain
  simulations with such a model produce precursors before the signal arrives [4].
- A material with nearly constant Df over many decades must have Dk decreasing ~linearly in log f.

### Level 3 — the Djordjevic–Sarkar (wideband Debye) model

Djordjevic, Biljić, Likar-Smiljanić and Sarkar (2001) measured FR-4 from 10 Hz to 12 GHz (parallel
plate below 50 MHz, a 300 mm microstrip up to 12 GHz, X-band waveguide checks). Findings: ε' decays
almost linearly in log f by ≈ 0.14 per decade between 10 kHz and 10 GHz; ε'' ≈ 0.1 and tanδ ≈ 0.02 are
nearly constant; estimated errors ±0.2 in ε', ±0.02 in ε'' [4]. They modelled this as a continuous sum
of Debye terms with relaxation frequencies uniformly spread in log between ω₁ and ω₂:
$$\varepsilon_r(\omega) = \varepsilon_\infty + \frac{\Delta\varepsilon'}{(m_2-m_1)\ln 10}\ln\!\frac{\omega_2 + j\omega}{\omega_1 + j\omega} - j\frac{\sigma}{\omega\varepsilon_0},\qquad m_i = \log_{10}\omega_i.$$
For ω₁ ≪ ω ≪ ω₂: ε' decreases by Δε'/(m₂ − m₁) per decade and ε'' ≈ (π/2)/ln 10 × (decay per decade)
= 0.682 × decay (script: 0.6821). Their FR-4 fit: ε∞ = 4.27, Δε'/(m₂−m₁) = 0.14, ω₁ = 10⁴ s⁻¹,
ω₂ = 10¹² s⁻¹, plus a small DC conductivity. The script evaluates it:

| f | 1 MHz | 100 MHz | 433 MHz | 915 MHz | 2.45 GHz | 10 GHz | 20 GHz |
|---|---|---|---|---|---|---|---|
| ε' (Dk) | 5.00 | 4.72 | 4.63 | 4.58 | 4.52 | 4.44 | 4.40 |
| tanδ (Df) | 0.019 | 0.020 | 0.021 | 0.021 | 0.021 | 0.021 | 0.020 |

That FR-4 sample (1.575 mm, from one board) is on the high-Dk side of today's FR-4s; modern FR-4s
vary with resin content (see below). **How EDA tools use it**: you enter one (Dk, Df) at one frequency
(e.g. 4.4 / 0.02 at 1 GHz) and the tool fixes ω₁, ω₂ (commonly 1 kHz-ish and 1 THz-ish) and solves
for ε∞ and Δε. Script example: Dk 4.40, Df 0.020 at 1 GHz → ε∞ = 4.01, Δε = 1.16 → Dk 4.79 at 1 MHz,
4.45 at 433 MHz, 4.35 at 2.45 GHz, 4.27 at 10 GHz. A "1 MHz Dk" copied from an old datasheet into a
GHz simulation is therefore typically 0.2–0.4 too high.

### Level 3 — anisotropy, weave, moisture, temperature

**Glass-weave anisotropy.** A laminate is layers of woven E-glass (ε ≈ 6.1–6.6) in resin (epoxy
ε ≈ 3–3.6; values medium confidence). Fields parallel to the glass sheets (in-plane) see glass and resin
roughly "in parallel"; fields normal to them (z-axis, what a microstrip mostly sees) see them "in
series". Wiener bounds with ε_glass 6.1 and ε_resin 3.2 give in-plane/z-axis ratios up to ~8–11 % for
resin volume fractions 0.45–0.75 (script); real laminates lie between the bounds, so anisotropy is a
few % to ~10 %. Laminate suppliers usually publish only z-axis (or method-dependent) Dk [10]. It matters
for: coplanar/GCPW lines and vias (in-plane fields), resonators and filters where both components
exist, and the *difference between Dk test methods* (stripline resonator, split-post, clamped
stripline all weight directions differently).

**Fibre-weave effect.** Across a trace width comparable to the weave pitch (~0.5 mm for 1080/2116
glass), local Dk alternates between glass-rich and resin-rich regions: impedance and delay vary by
position — skew in differential pairs at multi-Gb/s. Mitigations: spread glass (1067/1086 styles),
routing at an angle to the weave, low-Dk glass. Minor at UHF; relevant to high-speed ADC/FPGA links
(13-pcb domain).

**Resin content.** Thin cores/prepregs have more resin → lower Dk (e.g. 1080 prepreg ≈ 3.9–4.0 vs
7628 ≈ 4.4–4.6 in some fab stack-up tables — medium confidence; fabs publish their own values). Use the
fab's stack-up Dk per layer for impedance control.

**Moisture.** FR-4 absorbs ~0.1–0.3 % water by weight (medium confidence). Lichtenecker mixing with
the ITU water model (script) gives +0.6 % Dk per 0.5 % water volume and a small Df increase; measured
Df increases after humidity soaks are often larger because absorbed water binds at resin–glass
interfaces (qualitative; see 13-pcb). PTFE and hydrocarbon-ceramic laminates (RO4000) absorb far less
(RO4003C/RO4350B quote ~0.06 % — cited from datasheet memory, verify).

**Temperature.** Dk drifts with temperature (thermal coefficient of Dk, TCDk). Rogers quotes +40
ppm/°C (RO4003C) and +50 ppm/°C (RO4350B) (cited from knowledge of the datasheet); FR-4 is worse and
less specified, and its Df rises with temperature. For a 915 MHz filter, 100 ppm/°C × 60 °C = 0.6 % Dk
→ 0.3 % frequency shift (2.7 MHz) — comparable to the bandwidth of narrow filters.

## Material values

Values at room temperature; "@f" gives the test frequency. Where a range is given it spans grades or
sources. Confidence: H = datasheet/peer-reviewed, M = typical/secondary, L = rough.

| Material | ε' (Dk) | tanδ (Df) | @ f | Source / notes | Conf. |
|---|---|---|---|---|---|
| Vacuum | 1 | 0 | all | definition | H |
| Air (dry, sea level) | 1.00059 | ~0 | RF | (n−1) ≈ 2.9×10⁻⁴; humidity adds | M |
| FR-4 (Djordjevic sample) | 4.58 | 0.021 | 1 GHz | D-S fit to measured data [4] | H |
| FR-4 (generic, resin-dependent) | 4.0–4.7 | 0.015–0.025 | 1 GHz | manufacturers quote 4.2–5.5 at low f [4]; fab stack-up tables | M |
| Rogers RO4003C | 3.38 ± 0.05 (process), **3.55 (design)** | 0.0027 / 0.0021 | 10 / 2.5 GHz | Rogers datasheet [5] | H |
| Rogers RO4350B | 3.48 ± 0.05 (process), **3.66 (design)** | 0.0037 / 0.0031 | 10 / 2.5 GHz | Rogers datasheet [5] | H |
| Rogers RT/duroid 5880 (glass-microfibre PTFE) | 2.20 | 0.0009 | 10 GHz | Rogers datasheet (from knowledge) | M |
| PTFE (pure, unfilled) | 2.0–2.1 | 1–4×10⁻⁴ | 1–10 GHz | von Hippel tables (from knowledge) | M |
| Alumina 96 % | 9.4–9.6 | 3–10×10⁻⁴ | 1–10 GHz | ceramic-substrate datasheets (from knowledge) | M |
| Alumina 99.5–99.6 % | 9.8–9.9 | ~1×10⁻⁴ | 10 GHz | ditto | M |
| Fibreglass laminate / G10 (E-glass epoxy) | 4.2–5.2 | 0.015–0.025 | 1 MHz–1 GHz | NEMA G-10 limits commonly quoted as Dk ≤ 5.2, Df ≤ 0.025 at 1 MHz (from knowledge); hand-laid rocket fibreglass depends on glass/resin ratio | M |
| Epoxy resin (neat) | 3.0–3.6 | 0.01–0.03 | 1 GHz | (from knowledge) | L |
| E-glass fibre | 6.1–6.6 | ~0.002–0.006 | 1 MHz–10 GHz | (from knowledge) | M |
| Polyimide (Kapton) | 3.2–3.5 | 0.002–0.008 | 1 kHz–10 GHz | DuPont datasheet (from knowledge) | M |
| LPI solder mask | 3.3–4.0 | 0.02–0.03 | 1 GHz | fab data (from knowledge) | L |
| ABS, 3D-printed (FDM) | 2.57 ± 0.02 | 0.0047 | 15 GHz | Castles et al. 2016, split-post resonator; printed ≈ bulk within 1 % [6] | H |
| ABS, 3D-printed 100 % infill | ≈ 3.0 | — | (not stated) | Kuzmanić et al. 2023 LC-meter method [11] | M |
| PLA, 3D-printed | ≈ 2.75 (E-plane), 2.74–2.96 anisotropic | 0.012–0.016 | 0.5–20, 40, 60 GHz | IEEE CoBCom 2016 (Xplore 7843900) [7] | M |
| PLA (7 colours), SLA resins | 2.45–2.75 | up to > 0.02 (silver PLA, black resin highest) | 70–110 GHz | Işık et al., arXiv 2607.16937 (2026) [8] | M |
| Pure water, 20 °C | 80.0 / 78.6 | 0.024 / 0.135 | 0.433 / 2.45 GHz | ITU-R P.527-6 [3] | H |
| Sea water, 20 °C, 35 g/kg | 71.6 − j200.6 | 2.8 | 433 MHz | ITU-R P.527-6 [3] | H |
| Carbon-fibre composite | *conductor*: σ ≈ 10³–3×10⁴ S/m in-plane at UHF (DC up to ~4×10⁴) | — | DC–GHz | see [reflection page](boundary-conditions-reflection-refraction.md) | M |

**3D-print infill.** Printed parts are air–polymer mixtures. Kuzmanić et al. measured PLA/ABS εr
falling from ≈ 2.81/3.00 at 100 % infill to ≈ 1.98/2.29 at 33 % [11]. Simple mixing rules with a 33 %
*volume* fraction predict only 1.4–1.6 (script: linear 1.60, Lichtenecker 1.41, Maxwell-Garnett 1.50) —
because slicer "infill %" excludes perimeters and top/bottom skins, so the real solid fraction is much
higher. For RF parts (radomes, lens antennas, dielectric-loaded antennas) measure a coupon printed with
the same settings. Infill orientation also makes printed parts anisotropic (PLA 2.74 vs 2.96 [7]).

## Design equations & rules of thumb

| Equation | When valid | Typical value |
|---|---|---|
| tanδ = ε''/ε' (+ σ/ωε0ε') | any | FR-4 0.02 |
| α_d ≈ 27.3 tanδ dB/λ ≈ 91 f_GHz √ε' tanδ dB/m | tanδ ≪ 1, TEM | FR-4 915 MHz: 3.5 dB/m |
| Q_dielectric = 1/tanδ | capacitor / resonator | FR-4: 50; RO4003C: 370; PTFE: > 2000 |
| Debye peak ε''max = Δε/2 at ωτ = 1 | single relaxation | water f₁ ≈ 17 GHz (20 °C) |
| D-S: dε'/d log₁₀f ≈ −ε''/0.682 | wideband, ω₁ ≪ ω ≪ ω₂ | FR-4: −0.14/decade |
| Use "design Dk" for circuit design | Rogers laminates | RO4003C 3.55, RO4350B 3.66 |
| λ_g = λ0/√ε_eff | low loss | microstrip ε_eff < ε' |
| Δf/f ≈ −½ΔDk/Dk | resonators | 1 % Dk error → 0.5 % detuning |

## Worked examples

**1. Why a 915 MHz filter designed on "FR-4 Dk 4.8" lands low.** If the datasheet's 1 MHz Dk (4.8)
is used but the laminate is 4.45 at 915 MHz (D-S fit to 4.4 at 1 GHz), the real resonators are
electrically shorter than designed: f_actual ≈ f_design·√(4.8/4.45) → the filter lands **~3.9 % high**
(≈ 36 MHz at 915 MHz) — enough to miss the band. Use the Dk at the operating frequency, from the fab's
stack-up, and tune.

**2. Loss of a 100 mm, 50 Ω line at 2.45 GHz: FR-4 vs RO4003C.** Dielectric part (TEM estimate
× filling factor ≈ 0.85): FR-4 (4.35, 0.021): 91·2.45·√4.35·0.021·0.85 ≈ 8.3 dB/m → 0.83 dB; RO4003C
(3.55, 0.0024): 91·2.45·√3.55·0.0024·0.85 ≈ 0.86 dB/m → 0.09 dB. Conductor loss adds ~0.1–0.2 dB for
both. At 2.45 GHz, FR-4 costs ~0.7 dB more per 100 mm; for a short antenna feed, fine; for a filter or
coupler, use RO4003C.

**3. Printed PLA radome/lens at 5.8 GHz.** ε' ≈ 2.7, tanδ ≈ 0.014: loss 91·5.8·1.64·0.014 ≈ 12 dB/m =
0.12 dB per cm of solid material. A 2 mm wall: < 0.03 dB loss (reflection dominates — see
[radomes](boundary-conditions-reflection-refraction.md)). A 5 cm solid dielectric lens: ~0.6 dB.

**4. Capacitor Q from Df.** A 10 pF capacitor made with an FR-4 dielectric (e.g. a PCB interplane or
"gimmick" capacitor) has Q ≈ 1/0.02 = 50 → ESR = X_C/Q = (1/(2π·433 MHz·10 pF))/50 = 0.74 Ω. A C0G
MLCC of the same value (Df ~ 10⁻⁴ plus electrode loss) typically shows ESR ~ 0.1–0.3 Ω at 433 MHz (see
[capacitors at RF](../04-real-components-hf/capacitors-at-rf-mlcc.md)).

## Practical notes
- **Process vs design Dk (Rogers)**: process Dk comes from a clamped-stripline test on the bare
  laminate (IPC-TM-650 2.5.5.5); design Dk is what circuits actually show (includes copper roughness,
  measurement-method differences) — use design Dk for impedance and resonator design [5].
- **Dk test methods disagree** by a few % (stripline resonator, split-post, full-sheet resonance,
  microstrip differential phase). Compare numbers only within the same method.
- **Solder mask** over microstrip lowers impedance by ~1–3 Ω and adds loss; specify/model it.
- **Measuring your own material** (fibreglass nose cone, printed part): ring or λ/2 microstrip
  resonator on the material, split-cylinder/split-post resonator (lab), or two-antenna free-space
  transmission through a large sheet; for liquids and soft materials an open-ended coax probe.
- **For simulations**, always use a causal (D-S or multi-Debye) model for broadband/time-domain runs;
  single-frequency runs can use constant Dk/Df at that frequency.

## Common mistakes & misconceptions
- **"FR-4 has εr = 4.4" (full stop).** FR-4 is a family; Dk depends on resin content, glass style,
  frequency (−0.14/decade), temperature and moisture. 4.4 at ~1 GHz is a reasonable default only.
- **"Loss tangent = loss per metre."** It is loss per wavelength; at 10× frequency the loss per metre
  is ~10× higher.
- **Using constant Dk/Df in time-domain simulation.** Non-causal; use D-S.
- **"Water loss at 2.45 GHz is a special resonance."** It is the low-frequency flank of a broad Debye
  *relaxation* peaking near 17–20 GHz, not a sharp resonance. Operating *below* the peak is what makes
  ovens work: the table gives 266 dB/m at 2.45 GHz (power penetration depth 4.34/266 m ≈ 1.6 cm, i.e.
  volumetric heating) but 3700 dB/m at 10 GHz (≈ 1.2 mm — surface heating only). The 2.45 GHz choice
  itself is regulatory history (an ISM frequency since 1947), see
  [19 spectrum allocation](../19-regulations-safety/spectrum-allocation-ism-bands.md#common-mistakes--misconceptions).
- **"3D-print infill % = solid fraction."** Walls and skins raise the true fill; measure.
- **"Carbon fibre nose cones are RF-transparent like fibreglass."** They are conductive.
- **"Higher Dk substrate = worse."** Higher Dk shrinks circuits (λ/√εr) and is chosen deliberately
  (ceramics for filters, patches); loss depends on Df and conductor loss, not Dk per se.

## How to simulate / verify
- `python3 tools/verify/em_dielectrics.py` — Debye peak; numerical Kramers–Kronig; Djordjevic–Sarkar
  FR-4 table with the paper's parameters; the 0.682 relation; single-point D-S fit as EDA tools do;
  ITU-R P.527-6 pure/sea-water model at 433 MHz–24 GHz; mixing rules for 3D-print infill; Wiener
  anisotropy bounds; moisture effect.
- scikit-rf: `skrf.media.DefinedAEpTandZ0` / `MLine` accept frequency-dependent εr (D-S model is
  implemented in `MLine` via `diel='djordjevicsvensson'`).
- openEMS supports Debye/Lorentz dispersive materials (`AddDebyeMaterial`, `AddLorentzMaterial`) for
  broadband FDTD; fit the D-S curve with a few Debye poles.

## Open questions / gaps
- Many table rows (PTFE, alumina, G10, Kapton, epoxy, E-glass, solder mask, RT/duroid 5880, TCDk and
  moisture-absorption values) are from well-known datasheets/tables but were **not re-fetched** in this
  session — marked M/L. A later pass should fetch the Rogers RT/duroid, DuPont Kapton, CoorsTek/Kyocera
  alumina and a G10 supplier datasheet.
- JLCPCB's per-prepreg Dk values (7628/2116/3313/1080) should be recorded in 13-pcb/jlcpcb page.
- Hand-laid rocket fibreglass (glass cloth + laminating epoxy, often with voids) Dk/Df: no source
  found; propose measuring a coupon (ring resonator or free-space transmission).
  (Measurement recipe and a 4.0–4.6 mixing estimate now in [permittivity measurement](../17-test-measurement/resonator-and-cavity-perturbation-permittivity-measurement.md).)
- Measured FR-4 anisotropy ratios: sources found only discuss the concept [10]; numbers here are
  bounds.

## Sources
1. D. M. Pozar, *Microwave Engineering*, 4th ed., §1.3 (complex permittivity, loss tangent), §3.8
   (microstrip dielectric loss with filling factor). (textbook)
2. C. A. Balanis, *Advanced Engineering Electromagnetics*, 2nd ed., ch. 2 (electrical properties of
   matter: polarisation mechanisms, Debye relaxation, Kramers–Kronig). (textbook)
3. ITU-R Recommendation P.527-6 (09/2021), *Electrical characteristics of the surface of the Earth*,
   §5.1 (pure and sea water double-Debye models, eqs. 5–27). Implemented in `em_dielectrics.py`. (standard)
4. A. R. Djordjević, R. M. Biljić, V. D. Likar-Smiljanić, T. K. Sarkar, "Wideband frequency-domain
   characterization of FR-4 and time-domain causality," *IEEE Trans. EMC* 43(4), 662–667, Nov 2001.
   http://mtt.etf.bg.ac.rs/Mikrotalasna.Tehnika/Clanci/FR4_EMC_2001.pdf (peer-reviewed, read in full)
5. Rogers Corporation, *RO4000 Series High Frequency Circuit Materials* datasheet (RO4003C, RO4350B:
   process/design Dk, Df at 2.5 and 10 GHz) — via mirrors incl. JLCPCB's copy
   (static.jlcpcb.com/pdf/ROGERS_Datasheet.pdf). (datasheet)
6. D. Castles et al., "Microwave dielectric characterisation of 3D-printed BaTiO₃/ABS polymer
   composites," *Scientific Reports* 6, 22714 (2016), PMC4778131 (pure ABS: ε' = 2.57, tanδ = 0.0047 at
   15 GHz). (peer-reviewed)
7. "Complex permittivity and anisotropy measurement of 3D-printed PLA at microwaves and
   millimeter-waves," IEEE CoBCom 2016, IEEE Xplore 7843900 (authors not verified in this session;
   values from abstract). (peer-reviewed conference; abstract only)
8. K. A. Işık, M. M. Asgari, X. Wang, M. Masyukov, I. Nefedova, Z. Taylor, V. S. Asadchy, "Permittivity
   characterization of 3D-printed materials at millimeter waves," arXiv:2607.16937 (Jul 2026). (preprint)
9. U. Kaatze, "Complex permittivity of water as a function of frequency and temperature," *J. Chem.
   Eng. Data* 34, 371–374 (1989) (τ ≈ 8.27 ps at 25 °C). (peer-reviewed; via abstract)
10. L. Simonovich et al., "PCB laminate anisotropy: the impact on advanced via modeling" and "A
    heuristic technique to determine anisotropic properties in PCB laminates," *Signal Integrity
    Journal* (suppliers do not publish anisotropic Dk). (trade journal; titles/abstracts only)
11. Kuzmanić et al., "Influence of 3D printing properties on relative dielectric constant in PLA and ABS
    materials," *Progress in Additive Manufacturing*, 2023, PMC9942642. (peer-reviewed)
12. A. von Hippel (ed.), *Dielectric Materials and Applications*, MIT Press 1954 (classic tables for
    PTFE, polymers, ceramics). (handbook; cited from knowledge)
