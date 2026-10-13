---
title: Skin effect, conductor loss, surface roughness and plating
domain: 02-electromagnetics
slug: skin-effect-conductor-loss-roughness
tags: [skin-effect, skin-depth, surface-resistance, conductor-loss, AC-resistance, proximity-effect, surface-roughness, hammerstad, huray, groiss, cannonball, ENIG, immersion-silver, plating, litz, thin-film, sheet-resistance, drude, optical, plasmonics, dental-fillings, folklore]
prerequisites: [wave-equation-plane-waves-polarization.md, maxwells-equations.md]
related: [boundary-conditions-reflection-refraction.md, inductance-capacitance-from-fields.md, waveguides-and-cavity-resonators.md, dielectrics-permittivity-loss-tangent.md, ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md, ../04-real-components-hf/inductors-at-rf.md, ../13-pcb-rf-layout-emc/stackups-and-materials.md, ../13-pcb-rf-layout-emc/jlcpcb-rf-manufacturing.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Skin effect, conductor loss, surface roughness and plating

## Questions this page answers
- Why does RF current flow near the surface of a conductor, and how deep does it go?
- What is the skin depth of copper, silver, gold, aluminium and nickel at 433 MHz, 915 MHz, 2.4 GHz, 10 GHz, 77 GHz?
- What is surface resistance (Ω per square) and how do I get the AC resistance of a wire or a PCB trace from it?
- What is the proximity effect and when does it matter?
- How much does copper foil roughness increase loss, and which model (Hammerstad, Groiss, Huray, "cannonball") should I use?
- Is ENIG bad for RF? Why do people recommend immersion silver, OSP or bare copper?
- Does silver plating help? Does gold? When is Litz wire useful?
- If foil or a sputtered film is thinner than the skin depth, does radio pass through it?
- Does the skin depth keep shrinking at infrared and optical frequencies?
- Can dental fillings really pick up radio stations?

## TL;DR
- In a good conductor the fields and current decay as e^{−x/δ} with **δ = 1/√(πfμσ)** (the 1/e depth), shifting phase by 1 rad per δ [1][2][3].
- **Copper (IACS, 5.80×10⁷ S/m)**: δ = 66 µm at 1 MHz, **3.18 µm at 433 MHz, 2.19 µm at 915 MHz, 1.34 µm at 2.45 GHz**, 0.66 µm at 10 GHz, 0.24 µm at 77 GHz. Rule: δ_Cu ≈ 66 µm/√(f/MHz). Table below; verified in `tools/verify/em_skin_depth.py`.
- **Surface resistance R_s = 1/(σδ) = √(πfμ/σ)** Ω per square: Cu ≈ 5.4 mΩ at 433 MHz, 8.2 mΩ at 1 GHz, 26 mΩ at 10 GHz (∝ √f). A conductor of perimeter p has R' ≈ R_s/p per metre (if current is uniform around it); a 1 mm Cu wire at 433 MHz: 79× its DC resistance.
- **Silver** is only 3 % better than copper in R_s (√ of the conductivity ratio); **gold** 13 % worse, **aluminium** 26 % worse, **nickel** ≥ 2× worse (and far worse if ferromagnetic).
- **Roughness**: when the rms roughness approaches δ, loss rises. Hammerstad K = 1 + (2/π)atan(1.4(Δ/δ)²) saturates at 2 and underestimates loss above ~5–10 GHz; **Huray** "snowball" K = 1 + (3/2)·SR/(1 + δ/r + δ²/2r²) is unbounded-in-form and matches measurements to 50 GHz [4][5]. At 433–915 MHz roughness adds only ~5–30 % to conductor loss; at 10 GHz+ it can double or triple it.
- **ENIG**: the 3–6 µm electroless Ni-P layer has ~¼ (pure Ni) to ~1/35 (Ni-P) of copper's conductivity. On plated faces R_s rises ~1.5× at 433 MHz, ~2× at 915 MHz, ~4–5× at 2.4–6 GHz (layered model, script). Microstrip suffers less (current is mainly on the unplated underside) than CPWG (edge currents) [6][7]. **Immersion silver, OSP and bare Cu ≈ no penalty**; thin-Ni ENEPIG/EPIG much better than ENIG [6][7].
- On FR-4 at UHF, *dielectric* loss dominates conductor loss (50 Ω microstrip, 1.6 mm FR-4, 915 MHz: ~2.7 dB/m dielectric vs ~0.5 dB/m conductor).
- **Litz wire** helps up to ~1 MHz (strands thinner than δ, fully transposed); above a few MHz use solid/tubular or silver-plated conductors.

## Intuition (no math)
Imagine the conductor as many thin parallel filaments. An AC current in the centre filaments is
surrounded by more magnetic flux (from all the other filaments' currents) than a current near the
surface. More flux linkage means more inductance; at high frequency the current takes the
lowest-*impedance* path, not the lowest-resistance one, so it crowds into the low-inductance outer
filaments. Equivalently: a wave hitting a good conductor drives eddy currents that cancel the field
inside; within a few skin depths nothing is left.

Two consequences dominate RF design. First, only a thin shell of the conductor carries current, so
resistance rises as √f. Plating, surface finish and roughness — everything within a few δ of the
surface — suddenly matter, and the bulk metal underneath doesn't. Second, at a surface where the
current flows along peaks and valleys of a rough foil, the path is longer and the current crowds
into the bumps, so resistance rises further once δ becomes comparable to the roughness.

A skin-depth-thick layer is "where the current lives" only approximately: the current density
decays exponentially and 63 % of the current is within one δ, 86 % within 2δ, 95 % within 3δ.
A plating 3–5 δ thick behaves like bulk plating metal; a plating ≪ δ is nearly invisible.

## The math

### Level 1 — skin depth and surface resistance

$$\delta = \frac{1}{\sqrt{\pi f\mu\sigma}}\ \ [\text{m}],\qquad R_s = \frac{1}{\sigma\delta} = \sqrt{\frac{\pi f\mu}{\sigma}}\ \ [\Omega/\square],\qquad Z_s = (1+j)R_s.$$
f in Hz, μ = μ0μr (H/m), σ in S/m. Z_s is the surface impedance (ratio of tangential E to surface
current density J_s at the surface); its reactive part equals R_s — the "internal inductance" of the
skin layer, L_int = R_s/ω per square.

**Skin depth (µm)**, computed from CRC Handbook resistivities at 293 K [8] (Ag 1.587, Cu 1.678,
Au 2.214, Al 2.650, Ni 6.93 µΩ·cm) and IACS annealed copper (1.7241 µΩ·cm = 5.800×10⁷ S/m), μr = 1:

| f | Ag | Cu (pure, CRC) | Cu (IACS) | Au | Al | Ni (μr = 1)* |
|---|---|---|---|---|---|---|
| 1 MHz | 63.4 | 65.2 | 66.1 | 74.9 | 81.9 | 132 |
| 10 MHz | 20.1 | 20.6 | 20.9 | 23.7 | 25.9 | 41.9 |
| 100 MHz | 6.34 | 6.52 | 6.61 | 7.49 | 8.19 | 13.2 |
| 433 MHz | 3.05 | 3.13 | 3.18 | 3.60 | 3.94 | 6.37 |
| 915 MHz | 2.10 | 2.16 | 2.19 | 2.48 | 2.71 | 4.38 |
| 1 GHz | 2.01 | 2.06 | 2.09 | 2.37 | 2.59 | 4.19 |
| 1.575 GHz | 1.60 | 1.64 | 1.67 | 1.89 | 2.06 | 3.34 |
| 2.45 GHz | 1.28 | 1.32 | 1.34 | 1.51 | 1.66 | 2.68 |
| 5.8 GHz | 0.833 | 0.856 | 0.868 | 0.983 | 1.08 | 1.74 |
| 10 GHz | 0.634 | 0.652 | 0.661 | 0.749 | 0.819 | 1.33 |
| 24 GHz | 0.409 | 0.421 | 0.427 | 0.483 | 0.529 | 0.855 |
| 77 GHz | 0.228 | 0.235 | 0.238 | 0.270 | 0.295 | 0.477 |
| 100 GHz | 0.200 | 0.206 | 0.209 | 0.237 | 0.259 | 0.419 |

*Nickel is ferromagnetic: with μr ≈ 100 (plausible for bulk Ni well below its ferromagnetic
resonance) δ is 10× smaller and R_s 10× larger (script row "Ni (μr = 100)"). Nickel's effective
permeability falls toward 1 in the GHz range (FMR), so the μr = 1 column is the high-frequency
limit and a *lower bound* on loss at UHF. High-phosphorus electroless Ni-P is essentially
non-magnetic but has 5–15× the resistivity of pure Ni (see Level 3).

**Surface resistance (mΩ per square)**:

| f | Ag | Cu (IACS) | Au | Al | Ni (μr = 1) |
|---|---|---|---|---|---|
| 100 MHz | 2.50 | 2.61 | 2.96 | 3.23 | 5.23 |
| 433 MHz | 5.21 | 5.43 | 6.15 | 6.73 | 10.9 |
| 915 MHz | 7.57 | 7.89 | 8.94 | 9.78 | 15.8 |
| 2.45 GHz | 12.4 | 12.9 | 14.6 | 16.0 | 25.9 |
| 10 GHz | 25.0 | 26.1 | 29.6 | 32.3 | 52.3 |
| 77 GHz | 69.5 | 72.4 | 82.0 | 89.8 | 145 |

Quick rules: **δ_Cu ≈ 66.1 µm/√f_MHz**, **R_s,Cu ≈ 0.261 mΩ·√f_MHz**; for another metal multiply δ by
√(ρ/ρ_Cu) and R_s by √(ρ/ρ_Cu).

### Level 2 — derivation

In a good conductor (σ ≫ ωε, see [Maxwell](maxwells-equations.md)) displacement current is
negligible: ∇×**H** = σ**E**, ∇×**E** = −jωμ**H**. For a half-space x > 0 with current along z,
J_z(x) obeys the diffusion equation
$$\frac{d^2J_z}{dx^2} = j\omega\mu\sigma J_z = \left(\frac{1+j}{\delta}\right)^2J_z\ \Rightarrow\ J_z(x) = J_0e^{-(1+j)x/\delta},\quad \delta = \sqrt{\frac{2}{\omega\mu\sigma}} = \frac{1}{\sqrt{\pi f\mu\sigma}}.$$
This is the good-conductor limit of the plane-wave propagation constant, γ = (1+j)/δ (checked
against the exact γ for Cu and Ni to 10⁻⁶ in the script; see
[plane waves](wave-equation-plane-waves-polarization.md)).

**Total current per unit width** (surface current density):
J_s = ∫₀^∞ J_z dx = J_0δ/(1+j). **Power dissipated per unit area**:
$$P' = \frac{1}{2\sigma}\int_0^\infty|J_z|^2dx = \frac{|J_0|^2\delta}{4\sigma} = \frac12\frac{|J_s|^2}{\sigma\delta} = \frac12R_s|J_s|^2 = \frac12R_s|H_t|^2.$$
So *the loss is identical to a uniform current J_s flowing in a layer exactly δ thick* — the origin of
the "current flows in one skin depth" shorthand. Since |J_s| = |H_t| at the surface (boundary
condition), conductor loss follows from the tangential H of the lossless solution: the
**perturbation method** used for transmission lines, waveguides and cavities:
$$\alpha_c = \frac{P'_\text{loss per length}}{2P} = \frac{\tfrac12R_s\oint|H_t|^2dl}{2P}.$$
(Pozar §2.7, §3 [3]; Ramo et al. §5 [2].) The surface impedance Z_s = E_t/J_s = (1+j)R_s is the
Leontovich boundary condition used by solvers instead of meshing the metal.

**Round wire — exact solution.** For a wire of radius a, J_z(r) ∝ J₀(kr) with k = √(−jωμσ), and the
internal impedance per unit length is
$$Z_\text{int} = \frac{k}{2\pi a\sigma}\frac{J_0(ka)}{J_1(ka)}.$$
Limits: a ≪ δ → R_dc = 1/(πa²σ); a ≫ δ → R ≈ R_s/(2πa)·(1 + δ/(2a)) = R_dc(a/(2δ) + ¼) and
ωL_int → R. Exact vs asymptotes for a 1 mm diameter Cu wire (script):

| f | a/δ | R_ac/R_dc (exact Bessel) | a/(2δ) + ¼ |
|---|---|---|---|
| 10 kHz | 0.76 | 1.007 | 0.63 (invalid) |
| 100 kHz | 2.4 | 1.45 | 1.45 |
| 1 MHz | 7.6 | 4.05 | 4.03 |
| 100 MHz | 76 | 38.1 | 38.1 |
| 433 MHz | 157 | 79.0 | 79.0 |

**Proximity effect.** Near another current-carrying conductor, the current redistributes toward (for
opposite currents) or away from (same direction) the neighbour, so the effective perimeter shrinks.
For a two-wire line of wire radius a and centre spacing D, the exact TEM result is
R'_pair = (2·R_s/(2πa))·(D/2a)/√((D/2a)² − 1): the proximity factor is 1.34 at D/2a = 1.5, 1.15 at 2,
1.06 at 3, < 1.02 beyond 5 (script). In coils, proximity effect between adjacent turns typically
dominates skin effect and can raise R_ac several-fold above the single-wire value — one reason air
coils for high Q are space-wound (see [inductors at RF](../04-real-components-hf/inductors-at-rf.md);
Medhurst's measurements, not re-derived here).

**PCB traces.** For microstrip the current on the strip crowds at the underside (facing the ground)
and at the edges; the return current on the ground plane is concentrated under the trace within ~±3h.
The commonly used first-order estimate α_c ≈ R_s/(Z0·w) Np/m (wide strip, strip + ground) gives, for a
50 Ω line on 1.6 mm FR-4 (w ≈ 3 mm) at 915 MHz, ≈ 0.46 dB/m (×1.3 for typical roughness ≈ 0.6 dB/m),
versus ≈ 2.7 dB/m dielectric loss (tanδ 0.02) — FR-4 at UHF is **dielectric-loss dominated**
(script). Accurate α_c (Wheeler incremental inductance rule, edge singularities, thickness) belongs
to [planar lines](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md).
Copper thickness: ≥ 3δ everywhere avoids extra loss (1 oz = 35 µm ≫ 3δ above ~50 MHz; but a 0.5 oz
inner layer at 10 MHz (δ = 21 µm) is *not* skin-limited).

### Level 3 — surface roughness

Copper foil is rough on purpose (treatment on the "tooth" side for adhesion to the resin);
electrodeposited (ED) foil has a nodular ("snowball") texture; rolled-annealed (RA) and reverse-
treated or HVLP foils are smoother. When the rms roughness Δ becomes comparable to δ, current
follows the surface topography and crowds into the nodules.

**Hammerstad–Jensen (empirical, 1975/1980)** [9], a fit to Morgan's 1949 2-D groove calculations:
$$K_H = 1 + \frac{2}{\pi}\arctan\!\left[1.4\left(\frac{\Delta}{\delta}\right)^2\right]\quad(1\le K_H\le 2).$$
It saturates at 2 (for grooves, the path length can at most double), which real foils exceed above
roughly 5–10 GHz [4]. Useful up to a few GHz (Polar AP8155 notes saturation issues above ~4 GHz [10]).

**Groiss et al. (1996)** [11], from cavity-Q work:
$$K_G = 1 + \exp\!\left[-\left(\frac{\delta}{2\Delta}\right)^{1.6}\right]\quad(\le 2).$$
Same ceiling; transition is sharper. Described by Ansys as appropriate for relatively polished
conductors and frequency-domain only (non-causal). Polar suggests usefulness to ~7–10 GHz [10].

**Huray "snowball" model (Huray et al., DesignCon 2010)** [4]: treat nodules as N_i conducting
spheres of radius r_i sitting on a flat tile of area A_hex, sum their absorption cross sections
(electrically small spheres, dipole approximation):
$$K_\text{Huray} = \frac{P_\text{rough}}{P_\text{smooth}} \approx \frac{A_\text{matte}}{A_\text{hex}} + \frac32\sum_i\frac{N_i4\pi r_i^2/A_\text{hex}}{1 + \delta/r_i + \delta^2/(2r_i^2)}.$$
(first term = 1 for a flat base). The high-frequency limit 1 + (3/2)ΣN_i4πr_i²/A_hex depends only on
the *surface-area ratio* SR = N4πr²/A_hex of the nodules, not on rms height — Huray's key point that
rms roughness is a poor predictor. Validated against VNA data to 50 GHz with ~0.5 µm spheres (79
per tile for a high-profile foil, 50 for low-profile) [4]. Shlepnev (Simberian) shows the model has
only two independent parameters per sphere size — r and SR (or the "roughness factor"
RF = 1 + 1.5·SR) — and should be treated as a phenomenological fitting formula, identified from
measured insertion loss rather than from geometry [5].

**"Cannonball–Huray" (Simonovich 2015–2019)**: Huray with SR fixed at 4.887 (RF = 8.33) and
r = 0.06·Rz (10-point roughness from the foil datasheet). Shlepnev's critique: it is a one-parameter
special case whose success in published examples relied on tuning Rz after measurement [5]. Useful as
a first guess; not a substitute for fitting.

The geometric ambiguity is real: the 2010 paper's "hexagonal cells with a base dimension of 9.4 µm"
gives SR = 1.1, 3.2 or 4.3 for 79 spheres of 0.5 µm depending on whether 9.4 µm is the hexagon's
side, width across flats, or width across corners (script) — another reason to fit, not derive.

**Roughness factor K vs frequency** (Cu, script):

| Model | 433 MHz | 915 MHz | 2.45 GHz | 10 GHz | 24 GHz | 77 GHz |
|---|---|---|---|---|---|---|
| Hammerstad Δ = 0.3 µm (HVLP-like) | 1.01 | 1.02 | 1.05 | 1.18 | 1.39 | 1.73 |
| Hammerstad Δ = 1 µm | 1.09 | 1.18 | 1.42 | 1.81 | 1.92 | 1.97 |
| Hammerstad Δ = 2 µm (std ED) | 1.32 | 1.55 | 1.80 | 1.95 | 1.98 | 1.99 |
| Groiss Δ = 1 µm | 1.12 | 1.32 | 1.59 | 1.84 | 1.92 | 1.97 |
| Huray r 0.5 µm, SR 1 | 1.05 | 1.10 | 1.21 | 1.47 | 1.68 | 1.94 |
| Huray r 0.5 µm, SR 2 | 1.11 | 1.20 | 1.42 | 1.94 | 2.35 | 2.89 |
| Cannonball Rz = 5 µm | 1.11 | 1.21 | 1.48 | 2.30 | 3.14 | 4.48 |

(Parameter choices are illustrative; real foils span these. Rq ≈ 0.3–0.5 µm is typical of HVLP/RTF
foils and 1.5–3 µm of standard ED treated sides — medium confidence, foil-vendor data vary.)
Takeaway for Marcus's bands: at 433–915 MHz, roughness adds ~5–30 % to conductor loss (which is
itself small on FR-4); at 5.8 GHz and mm-wave radar (24/77 GHz) choose smooth foil and fit Huray
parameters from test coupons. Roughness also *increases the apparent Dk* (slower phase velocity from
extra internal inductance) — a reason "design Dk" exceeds "process Dk" in Rogers datasheets (see
[dielectrics](dielectrics-permittivity-loss-tangent.md)).

### Level 3 — plating and surface finishes

A plating layer of conductivity σ₁ and thickness t over a base metal σ₀ has surface impedance
(transmission-line analogy, η_i = √(jωμ_i/σ_i), γ_i = √(jωμ_iσ_i)):
$$Z_s = \eta_1\frac{\eta_0 + \eta_1\tanh\gamma_1t}{\eta_1 + \eta_0\tanh\gamma_1t}.$$
t ≪ δ₁ → Z_s → η₀ (base metal); t ≫ δ₁ → Z_s → η₁ (plating metal). Implemented for multilayers in
`Zs_layers()`; ratio R_s(finish)/R_s(smooth bare Cu):

| Finish (layer model) | 433 MHz | 915 MHz | 2.45 GHz | 5.8 GHz | 10 GHz | 25 GHz |
|---|---|---|---|---|---|---|
| ENIG: 0.08 µm Au / 5 µm Ni-P (60 µΩ·cm, μr 1) / Cu | 1.51 | 2.20 | 3.99 | 5.10 | 4.87 | 3.85 |
| ENIG, magnetic Ni bound: 5 µm Ni (7 µΩ·cm, μr 20) | 8.6 | 8.3 | 7.6 | 6.6 | 5.9 | 4.6 |
| Thin-Ni ENEPIG: 0.05 Au / 0.1 Pd / 0.1 µm Ni-P | 1.00 | 1.01 | 1.02 | 1.05 | 1.09 | 1.23 |
| Immersion Ag, 0.2 µm | 1.00 | 1.00 | 1.00 | 0.99 | 0.99 | 0.98 |
| Immersion Sn, 1 µm (11.5 µΩ·cm) | 1.03 | 1.06 | 1.17 | 1.41 | 1.67 | 2.30 |
| Bulk Ni-P (reference) | 5.90 | 5.90 | 5.90 | 5.90 | 5.90 | 5.90 |

Inputs (medium confidence): electroless Ni in PCB ENIG is typically mid-phosphorus (6–9 % P), 3–6 µm
thick [7][12]; its resistivity is several tens of µΩ·cm (60 µΩ·cm used here as representative; pure Ni
6.93) and mid-P deposits may be weakly magnetic while high-P (≳ 10–11 % P) deposits are non-magnetic as
plated [12]. The two ENIG rows bracket the physics: resistive Ni-P versus conductive-but-magnetic Ni.

**What the measurements say.** Coonrod (Rogers) measured ENIG vs bare copper: +0.38 dB/in at
25 GHz for an 8-mil (0.2 mm) microstrip and +0.21 dB/in for 20-mil; on GCPW at 50 GHz about 1.2 dB/in
with ENIG vs 0.5 dB/in for microstrip; **immersion silver and OSP were indistinguishable from bare
copper up to 40 GHz; immersion tin was worse** [6]. Milad (Uyemura) shows thick-Ni (3–6 µm) ENIG/ENEPIG
with much higher insertion loss than thin-Ni (0.1 µm) ENEPIG and Ni-free EPIG/IGEPIG on a 250 mm, 50 Ω
line [7]. Why the geometry matters: plating covers only exposed copper — the **top and side walls** of
a trace (and only where there is no solder mask). A microstrip carries most of its current on the
**underside** (unplated) and the ground-plane face (unplated), so ENIG's penalty is diluted; in
**CPWG**, current crowds at the facing edges of trace and coplanar ground — plated surfaces — so the
penalty is large.

**Practical ranking for RF traces**: bare Cu (with solder mask or OSP) ≈ immersion Ag ≈ OSP
< ENEPIG thin-Ni/EPIG < immersion Sn < HASL (rough, uneven, Sn-based) ≲ ENIG (thick Ni-P). At
433/915 MHz on FR-4 the absolute difference is small (conductor loss is a minor part of total), so
ENIG is acceptable for short UHF runs; at 5.8 GHz+ and on low-loss laminates, avoid ENIG on RF traces
or mask them. (JLCPCB finish options belong in
[jlcpcb-rf-manufacturing](../13-pcb-rf-layout-emc/jlcpcb-rf-manufacturing.md).)

**Silver and gold plating on RF hardware.** Silver plating (3–10 µm, ≫ δ above ~1 GHz) makes cavity
filters and connectors ~3 % lower-R_s than copper and protects copper from oxidation; tarnish (Ag₂S)
is thin and has little effect at UHF (medium confidence). Gold (hard gold usually contains Co/Ni and
has higher resistivity than pure Au) is used for corrosion resistance, not conductivity; a gold
flash ≪ δ over nickel behaves like nickel (the ENIG problem again). Connector centre pins are
commonly gold over nickel; the nickel underlayer is a known contributor to connector loss and
passive intermodulation (PIM) — for low-PIM connectors use white bronze/silver finishes (PIM details
belong in 07-noise-linearity / 18-components; cited from knowledge).

**Litz wire.** Many insulated strands, each thinner than δ, transposed so each occupies every
position in the bundle equally, force a uniform current distribution. Strand diameter ≲ δ: 0.47 mm
at 20 kHz, 0.21 mm at 100 kHz (≈ AWG 32), 66 µm at 1 MHz (≈ AWG 42) (script). Above roughly 1–3 MHz
the gains vanish: strand capacitance, imperfect transposition and bundle-level proximity effect take
over, and extremely fine strands are impractical (Sullivan 1999 [13] for the optimisation). For
HF–VHF coils use solid wire, copper tube or silver-plated wire; for UHF, geometry (spacing, Q of the
structure) matters more than wire type.

## Design equations & rules of thumb

| Equation | When valid | Typical value |
|---|---|---|
| δ = 1/√(πfμσ); δ_Cu ≈ 66.1/√f_MHz µm | σ ≫ ωε, μ constant | 433 MHz: 3.18 µm |
| R_s = √(πfμ/σ); R_s,Cu ≈ 0.261√f_MHz mΩ | same | 915 MHz: 7.9 mΩ/□ |
| Conductor ≥ 3–5δ thick → bulk behaviour | plating, foil, shields | 1 oz Cu ok > ~50 MHz |
| R'_wire ≈ R_s/(2πa)(1 + δ/2a) | a > ~2δ | 1 mm Cu at 433 MHz: 79×R_dc |
| Two-wire proximity factor (D/2a)/√((D/2a)²−1) | TEM pair | D/2a = 1.5: +34 % |
| α_c ≈ R_s/(Z0w) Np/m | wide microstrip, first order | 915 MHz FR-4 50 Ω: 0.46 dB/m |
| K_Hammerstad ≤ 2 | Δ ≲ δ, f ≲ 5 GHz | Δ = 1 µm @2.45 GHz: 1.42 |
| K_Huray = 1 + 1.5 SR/(1+δ/r+δ²/2r²) | fit r, SR to data; to 50 GHz+ | see table |
| ENIG penalty on plated faces ~1.5–5× R_s | 0.4–10 GHz | CPWG ≫ microstrip |
| Metal swap: R_s scales √(ρ) | same geometry | Ag −3 %, Au +13 %, Al +26 %, Ni ≥ +100 % |
| Temperature: ρ_Cu +0.39 %/K → R_s +0.2 %/K | near 20 °C | 60 °C rise: +12 % R_s |

(Cu temperature coefficient 0.00393/K is the IACS value at 20 °C — cited from knowledge.)

## Worked examples

**1. Skin depth at 433 MHz.** δ = 1/√(π·433×10⁶·4π×10⁻⁷·5.8×10⁷) = 1/√(9.914×10¹⁰) = **3.18 µm**
(IACS). A 35 µm (1 oz) trace is 11δ thick: the bottom 3δ ≈ 10 µm carries 95 % of the current in a
microstrip. R_s = 1/(σδ) = 1/(5.8×10⁷·3.18×10⁻⁶) = 5.43 mΩ/□.

**2. AC resistance of a 433 MHz quarter-wave whip made of 1 mm copper wire.** Length 0.17 m;
R' = R_s/(2πa) = 5.43×10⁻³/(2π·0.5×10⁻³) = 1.73 Ω/m (exact Bessel: 79.0 × 21.95 mΩ/m = 1.73 Ω/m).
With a sinusoidal current distribution the effective loss resistance referred to the feed is
≈ ½·R'·L = 0.15 Ω, versus ≈ 36 Ω radiation resistance of a monopole — efficiency ≈ 99.6 %.
(Loss in the ground plane/counterpoise usually dominates; see 08-antennas.)

**3. Gold-plated vs silver-plated SMA centre pin at 5.8 GHz.** R_s(Ag) = 19.1 mΩ, R_s(Au) =
22.5 mΩ: +18 %; but if the "gold" is a 0.1 µm flash over 2 µm nickel, the layered model gives
R_s ≈ R_s(Ni) or worse (Ni δ ≈ 1.7 µm at μr = 1, < 0.2 µm if magnetic) — potentially 2–7× copper.
Connector datasheets quote insertion loss directly; use them.

**4. Should Marcus's 915 MHz module board use ENIG?** A 20 mm 50 Ω microstrip on 1.6 mm FR-4:
dielectric loss ≈ 2.7 dB/m × 0.02 m = 0.055 dB; conductor loss ≈ 0.012 dB; with ENIG on the top/edges
(say +50 % conductor loss overall) ≈ +0.006 dB. Negligible. At 5.8 GHz on RO4003C the same logic
gives a measurable but still small difference for short lines; for long feed networks or 24/77 GHz,
avoid ENIG on RF copper.

## Practical notes
- Skin depth governs **shield thickness**: a 35 µm copper foil is 17δ at 1 GHz (≈ 150 dB absorption
  loss) but only 0.5δ at 10 kHz. Low-frequency magnetic shielding needs thick or high-μ material
  (see [shielding](../13-pcb-rf-layout-emc/shielding-and-isolation.md)).
- **Solder mask over RF traces** adds dielectric loss (tanδ ≈ 0.02–0.03 for LPI mask) and shifts
  impedance slightly, but prevents finish-metal penalties; many RF designers leave RF traces
  unmasked with ImAg/OSP, or masked with any finish.
- Electroplated PCB copper is slightly less conductive than annealed bulk (often quoted 5.0–5.8×10⁷
  S/m; medium confidence) — field solvers default to 5.8×10⁷.
- Measuring: split the loss of a test line into conductor (∝ √f) and dielectric (∝ f) parts by fitting
  α(f) = a√f + bf; the roughness term shows up as a deviation from √f above a few GHz.
- For cavity filters and resonators, R_s sets the unloaded Q (see
  [cavities](waveguides-and-cavity-resonators.md)); silver plating and polishing buy a few % of Q.

## Common mistakes & misconceptions
- **"At RF, current flows only on the surface."** It flows *mostly* within a few δ of the surface,
  decaying exponentially; nothing special happens exactly at δ. At 433 MHz that "surface" is 3 µm
  deep — still ~10⁴ atomic layers. (Common forum statement.)
- **"Skin effect makes the inside of a conductor useless, so hollow tubes are as good as solid."**
  True at RF if the wall is ≳ 3–5δ. At audio or power frequencies δ is mm-scale and the inside
  matters.
- **"Silver plating is much better than copper."** R_s improves by only 3 %; the benefit is corrosion
  resistance and avoiding worse underlayers.
- **"Gold is a good RF conductor."** Pure gold is 13 % worse than copper; practical gold platings
  over nickel can be much worse.
- **"Roughness never more than doubles loss."** That is an artefact of the Hammerstad/Groiss
  ceilings; measured loss on rough foils exceeds 2× at tens of GHz [4].
- **"RMS roughness predicts loss."** Two foils with equal Rq can differ substantially; nodule size and
  surface-area ratio matter [4][5].
- **"Thicker copper reduces RF loss."** Only up to ~3–5δ; beyond that, width (perimeter) and surface
  quality matter, not thickness.
- **"A film thinner than the skin depth is transparent."** Below δ the film acts as a sheet resistance R_□ = 1/(σt), and it *reflects*: T = 2/(2 + η0/R_□). 40 nm of aluminium (1 % of δ at 433 MHz) still blocks ≈ 48 dB. The exact slab result matches the sheet law up to t ≈ δ and then adds 8.7 dB of absorption per δ (16 µm kitchen foil: ≈ −114 dB at 433 MHz) (`tools/verify/s4_thin_film.py`; details in [boundary conditions — thin films](boundary-conditions-reflection-refraction.md#level-3--conducting-walls-lossy-half-spaces-and-limits-of-the-plane-wave-model)).
- **"Skin depth keeps falling as 1/√f all the way to light."** Only while ω ≪ γ, the electron collision rate (≈ 4 × 10¹³ s⁻¹ for gold, i.e. up to ≈ 1 THz). Above ≈ 10 THz the Drude conductivity becomes mostly imaginary (electron inertia, kinetic inductance), and the field penetration saturates at $c/\omega_p$ ≈ 22 nm for Au/Ag. The metal behaves as a lossy *plasma*, which is why optical antennas are plasmonic and shorter than λ/2. Above ω_p (≈ 137 nm, UV) metals become transparent. Gold at 433 MHz: 3.8 µm, at 1 THz 74 nm, at 1550 nm 22 nm (script §3).
- **"Dental fillings receive radio stations."** Physically possible only very close to a high-power AM transmitter, and the evidence is anecdotal. Three things are needed: an "antenna" (head, fillings, metal frames), a nonlinear junction (corroded dissimilar metals in saliva behave like a crude [diode detector](../05-analog-electronics/diodes-schottky-pin-varactor.md)), and a transducer (vibration or bone conduction). A 50 kW AM station gives ≈ 2.2 V/m at 1 km (≈ 0.2 V across a 0.1 m effective height), about 53 dB above a typical ≈ 5 mV/m city-grade signal (script §5). That is the same mechanism as the well-documented "rusty bolt" demodulation of AM broadcasts by fences, gutters and audio gear near transmitters ([audio rectification](../17-test-measurement/interference-hunting-and-rf-immunity.md)). Far from a transmitter the fields are 40–60 dB too weak. It is also unrelated to the microwave auditory effect (thermoelastic clicks from pulsed radar), which needs intense pulses.
- **"Skin effect and proximity effect are different physics."** Both are eddy-current redistribution
  by magnetic fields — from the conductor's own current (skin) or its neighbours' (proximity).

## How to simulate / verify
- `python3 tools/verify/s4_thin_film.py` — sheet law vs exact slab for thin Al/Cu films; Drude Au/Ag conductivity and penetration depth from 433 MHz to 600 nm; AM field strength for the dental-filling check.
- `python3 tools/verify/em_skin_depth.py` — skin-depth and R_s tables (Ag, Cu, IACS Cu, Au, Al, Ni);
  good-conductor formula vs exact γ; exact Bessel wire impedance vs asymptotes; proximity factor;
  Hammerstad/Groiss/Huray/Cannonball tables; layered surface impedance for ENIG/ENEPIG/ImAg/ImSn;
  microstrip loss split at 915 MHz; Litz strand sizes.
- Field solvers: openEMS models metals as conducting sheets or with a conductivity; for skin-effect
  accuracy in FDTD use a surface-impedance/“conducting sheet” model rather than meshing δ. Commercial
  tools (HFSS, ADS Momentum, Simbeor) implement Hammerstad, Groiss and Huray directly; scikit-rf's
  `MLine` includes a Hammerstad roughness option.
- Bench: two lengths of the same line on the same panel (e.g. 50 mm and 150 mm) measured on a VNA
  give α(f) by subtraction (de-embeds connectors); fit a√f + bf.

## Open questions / gaps
- Ni-P resistivity vs phosphorus content and the effective μr of ENIG nickel vs frequency: only
  bracketed here (60 µΩ·cm non-magnetic vs 7 µΩ·cm μr = 20). A peer-reviewed measurement (e.g.
  IEEE EMC/ECTC papers on ENIG loss modelling) should replace the brackets.
- Roughness parameters of JLCPCB's standard FR-4 and Rogers foils: unknown; needs coupon
  measurement (13-pcb / 17-test).
- Medhurst's proximity-effect data for solenoids not reproduced (04-real-components).

## Sources
1. D. K. Cheng, *Field and Wave Electromagnetics*, 2nd ed., 1989, §8-3 (plane waves in good
   conductors, skin depth, surface resistance). (textbook)
2. S. Ramo, J. R. Whinnery, T. Van Duzer, *Fields and Waves in Communication Electronics*, 3rd ed.,
   1994, ch. 5 (skin effect in plane conductors and round wires; internal impedance, Bessel-function
   solution). (textbook)
3. D. M. Pozar, *Microwave Engineering*, 4th ed., §1.7 (good conductors, surface resistance), §2.7
   (perturbation method for attenuation), §3.8 (microstrip conductor loss). (textbook)
4. P. G. Huray, O. Oluwafemi, J. Loyer, E. Bogatin, X. Ye, "Impact of copper surface texture on loss: a
   model that works," DesignCon 2010 (eqs. 1, 8, 9, 10; Morgan 1949 and Hammerstad context; validation
   to 50 GHz). (conference, read in full)
5. Y. Shlepnev, "Conductor surface roughness modeling: from 'snowballs' to 'cannonballs'," Simberian
   app note, Mar 2019; and "Unified approach to interconnect conductor surface roughness modelling,"
   IEEE EPEPS 2017 (unified K = 1 + (RF−1)F; Groiss transition function). (app note / conference)
6. J. Coonrod, "The impact of final plated finishes on insertion loss for high-frequency PCBs,"
   *PCD&F*, 2 Mar 2018 (measured ENIG, ImAg, ImSn, OSP vs bare Cu to 40–50 GHz). (trade article, measured
   data)
7. G. Milad, "Minimizing signal transmission loss in high-frequency circuits," Uyemura/IConnect007,
   Jul 2020 (thick-Ni vs thin-Ni ENEPIG vs EPIG insertion loss). (trade article)
8. CRC Handbook of Chemistry and Physics, "Electrical resistivity of pure metals" (values at 273/293/
   300 K; based on Ho et al., J. Phys. Chem. Ref. Data 12 (1983) etc.). (handbook)
9. E. Hammerstad and Ø. Jensen, "Accurate models for microstrip computer-aided design," IEEE MTT-S
   Int. Microwave Symp. Digest, 1980, pp. 407–409; E. Hammerstad and F. Bekkadal, *Microstrip
   Handbook*, Univ. Trondheim 1975; S. P. Morgan, "Effect of surface roughness on eddy current losses at
   microwave frequencies," *J. Appl. Phys.* 20, 352 (1949). (peer-reviewed; cited via [4])
10. Polar Instruments, "Surface roughness effect on PCB trace attenuation/loss" (AP8155). (app note)
11. S. Groiss, I. Bardi, O. Biro, K. Preis, K. R. Richter, "Parameters of lossy cavity resonators
    calculated by the finite element method," *IEEE Trans. Magn.* 32(3), 894–897, May 1996; formula via
    [5] and Ansys HFSS documentation. (peer-reviewed)
12. Electroless-nickel phosphorus-content properties: plating-industry summaries (ScienceDirect Topics
    "Electroless nickel coating"; Armoloy); 4–13 % P, PCB ENIG usually mid-P 6–9 %, high-P non-magnetic.
    (industry/secondary — medium confidence)
13. C. R. Sullivan, "Optimal choice for number of strands in a litz-wire transformer winding," *IEEE
    Trans. Power Electron.* 14(2), 283–291, 1999. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
14. M. A. Ordal et al., *Appl. Opt.* 22(7), 1099–1120 (1983) — Drude parameters for Au/Ag (ω_p ≈ 7.3 × 10⁴ cm⁻¹; Au ω_τ 215 cm⁻¹); reproduced σ_DC in s4_thin_film.py. (peer-reviewed; volume, issue, first page and year checked against Crossref by W5-S18b, 2026-10-13 (doi:10.1364/ao.22.001099; end page not listed there); parameters cited from knowledge, self-consistency checked)
15. L. Novotny and N. van Hulst, "Antennas for light," *Nature Photonics* 5, 83–90 (2011) (plasmonic optical antennas, effective-wavelength scaling). (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
