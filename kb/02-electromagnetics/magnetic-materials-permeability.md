---
title: Magnetic materials — complex permeability, ferrites, Snoek's limit and gyrotropic media
domain: 02-electromagnetics
slug: magnetic-materials-permeability
tags: [permeability, complex-permeability, ferrite, NiZn, MnZn, YIG, snoek-limit, ferromagnetic-resonance, polder-tensor, gyrotropic, faraday-rotation, ferrite-bead, circulator, iron-powder, carbonyl-iron, distributed-gap, gapped-core, effective-permeability, maxwell-garnett]
prerequisites: [maxwells-equations.md, dielectrics-permittivity-loss-tangent.md, electromagnetic-units-and-constants.md]
related: [skin-effect-conductor-loss-roughness.md, inductance-capacitance-from-fields.md, ../04-real-components-hf/ferrites-and-beads.md, ../04-real-components-hf/inductors-at-rf.md, ../06-rf-circuits/circulators-isolators.md, ../06-rf-circuits/baluns-and-rf-transformers.md, ../13-pcb-rf-layout-emc/emc-emi-fundamentals.md]
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# Magnetic materials — complex permeability, ferrites, Snoek's limit and gyrotropic media

## Questions this page answers
- What do μ', μ'' and "complex permeability" mean on a ferrite datasheet?
- Why does a ferrite's permeability collapse above some frequency, and why can't I have high μ *and* high frequency (Snoek's limit)?
- Why is a ferrite bead a resistor at 100 MHz rather than an inductor?
- Which ferrite mix (31, 43, 61, 67…) for 433 MHz or 915 MHz? Do ferrites work at 2.4 GHz?
- What makes a magnetised ferrite "gyrotropic", and how does that give circulators and isolators?
- Why does nickel (e.g. in ENIG or connector plating) behave strangely at RF?
- Why does an iron-powder toroid have μ ≈ 10 when iron itself has μ in the thousands, and why is it so stable and low-loss?
- What does an air gap do to a core's permeability, temperature drift and Q?
- Do magnets affect radio waves or antennas?

## TL;DR
- **Complex relative permeability μ_r = μ' − jμ''** (e^{jωt}). A winding on a core of air inductance L0 has **Z = jωL0μ_r = ωL0μ'' + jωL0μ'** — μ' makes inductance, μ'' makes series resistance (loss) [1][2].
- Magnetisation in ferrites comes from electron spins precessing about internal (anisotropy) fields at the **ferromagnetic-resonance** frequency; above it, spins can't follow and μ → 1.
- **Snoek's limit (SI)**: **(μ_i − 1)·f_r ≈ (2/3)(γ/2π)·μ0M_s**, γ/2π = 28.0 GHz/T [3][4]. For NiZn with μ0M_s ≈ 0.35 T: (μ_i − 1)f_r ≈ 6.5 GHz ⇒ μ_i = 800 (Fair-Rite 43) rolls off near ~8 MHz; μ_i = 125 (61) near ~50 MHz; μ_i = 40 (67) near ~170 MHz (`tools/verify/em_magnetics.py`).
- Above f_r the material is **lossy (μ'' > μ')** — perfect for **EMI suppression beads** (resistive impedance, no resonance with stray C). 43 material is the classic 25–300 MHz suppression mix; 61/52 are used ~200–1000 MHz [5].
- By a few GHz all bulk ferrites have μ' → ~1 and modest μ''; "GHz beads" rely on specially formulated materials and small geometry — check the measured impedance curve, not μ_i.
- **MnZn** ferrites (μ_i 1500–10 000) are conductive-ish (ρ ~ Ω·m) and have huge εr (10⁴–10⁵): eddy currents and *dimensional resonance* limit them to ≲ 1–10 MHz. **NiZn** (ρ ~ 10³–10⁷ Ω·m) is the RF ferrite.
- A **DC-magnetised ferrite** (YIG, Li/Ni ferrites) has a tensor permeability (**Polder tensor**) with different μ for right- and left-circular polarization: **μ± = 1 + ω_m/(ω0 ∓ ω)**, ω0 = γμ0H0, ω_m = γμ0M_s. Non-reciprocity ⇒ circulators, isolators, Faraday rotators, YIG filters/oscillators [1][6].
- **Iron powder = metal particles + distributed air gap.** Packing carbonyl-iron spheres at a fill fraction of ≈ 0.64 gives μ_e ≈ (1+2p)/(1−p) ≈ 6 (catalogue −2/−6: 10/8.5). Any gap divides μ, the temperature coefficient and the loss tangent by the same factor μ/μ_e, which is why powder cores are stable (35–95 ppm/°C) and high-Q (material Q ≈ 370 at 7 MHz for −2) but need many turns ([iron powder vs ferrite](../04-real-components-hf/ferrites-and-beads.md#iron-powder-vs-ferrite-cores-gapped-cores-and-hf-transformers-efhw-491)).
- **Nickel** is ferromagnetic (μ_r ≫ 1 below GHz) and resistive: nickel underlayers (ENIG, connector plating) raise surface resistance and create passive intermodulation (see [skin effect](skin-effect-conductor-loss-roughness.md)).

## Intuition (no math)
In a magnetic material each electron spin behaves like a tiny spinning top with a magnetic moment.
Push it with a magnetic field and it doesn't simply swing over — it *precesses* around the field,
like a gyroscope, at a rate set by the field strength (28 GHz per tesla). In an unmagnetised ferrite
the internal "field" holding spins in place is the crystal's anisotropy field (plus demagnetising
fields at grain boundaries). A weak AC field wobbles the spins and adds a lot of magnetisation — high
permeability — as long as the AC frequency is below the spins' natural precession frequency. Near that
frequency the response lags and absorbs energy (μ'' peaks); well above it the spins can't respond
at all and the material looks like air.

The catch (Snoek): a *soft* material (weak anisotropy, easy to magnetise → high μ) is precisely one
whose restoring field is weak → low precession frequency. So high μ and high cutoff frequency trade
against each other, with the product fixed by the saturation magnetisation. You can't buy a μ = 1000
ferrite that works at 433 MHz.

A permanent DC bias field lines up all the spins. Now an RF field's rotating component either
co-rotates with the spins' natural precession (strong interaction) or counter-rotates (weak). The
material treats right- and left-circular polarization differently — it is *gyrotropic* — and
direction of travel relative to the bias matters. That breaks reciprocity, which no passive dielectric
or metal structure can do on its own, and is how a circulator routes TX → antenna → RX.

## The math

### Level 1 — complex permeability and the inductor/bead model

$$\mathbf B = \mu_0\mu_r\mathbf H,\qquad \mu_r = \mu' - j\mu''.$$
For a winding of N turns on a closed core whose air-core inductance is L0 = μ0N²A_e/ℓ_e
(A_e effective area, ℓ_e effective path length):
$$Z = j\omega L_0\mu_r = \underbrace{\omega L_0\mu''}_{R_s(\omega)} + j\underbrace{\omega L_0\mu'}_{X_s(\omega)}.$$
The magnetic loss tangent tanδ_m = μ''/μ' ; the core's Q = μ'/μ''. Datasheets plot μ'(f) and μ''(f)
("complex permeability") measured on a toroid, or directly |Z|, R, X for a finished bead.

**Per-turn toroid inductance** (air): L0 = (μ0h/2π)·ln(OD/ID). A small bead (OD 3.5, ID 1.3, h 6 mm)
has L0 = 1.19 nH; with μ' = 800 → 0.95 µH per turn at low frequency.

### Level 2 — spin resonance, relaxation and Snoek's limit

**Gyromagnetic precession.** A magnetic moment **m** with angular momentum obeys
d**M**/dt = −γμ0 **M** × **H** (Landau–Lifshitz, without damping), γ = g e/(2m_e) ≈ 1.76×10¹¹ rad s⁻¹ T⁻¹
(γ/2π = 28.02 GHz/T for g ≈ 2.0023; CODATA γ_e). In an effective field B_eff = μ0H_eff the natural
precession frequency is f = (γ/2π)B_eff: 2.8 GHz at 0.1 T.

**Snoek's argument (polycrystalline cubic ferrite) [3].** For an unbiased material the restoring
field is the anisotropy field H_A: f_r = (γ/2π)μ0H_A. Rotational susceptibility averaged over random
grain orientations: χ_i = μ_i − 1 = (2/3)M_s/H_A. Eliminating H_A:
$$\boxed{(\mu_i - 1)\,f_r = \frac{2}{3}\frac{\gamma}{2\pi}\mu_0M_s = \frac{\gamma\,\mu_0M_s}{3\pi}}$$
In Gaussian units (datasheets): (μ_i − 1)f_r = (2/3)(2.80 MHz/Oe)(4πM_s [G]). **Caution:** papers often
write "γM_s/3π" with M_s meaning 4πM_s in gauss (or μ0M_s in tesla); plugging M_s in emu/cm³ gives an
answer 4π too small (see [units](electromagnetic-units-and-constants.md)).

Numbers (script; μ0M_s from B at 10 Oe as a proxy for saturation — medium confidence):

| Material class | μ0M_s | (μ_i − 1)f_r | μ_i = 40 | μ_i = 125 | μ_i = 800 | μ_i = 5000 |
|---|---|---|---|---|---|---|
| NiZn (Fair-Rite 43-like, 3500 G) | 0.35 T | 6.5 GHz | 168 MHz | 53 MHz | 8.2 MHz | — |
| MnZn (≈ 4800 G) | 0.48 T | 9.0 GHz | — | — | 11 MHz | 1.8 MHz |
| YIG (1780 G) | 0.178 T | 3.3 GHz | 85 MHz | 27 MHz | — | — |

This is an *upper bound* for the onset of the μ' roll-off (domain-wall resonance, which dominates at
lower frequency in large-grain material, rolls off earlier). Generalisations (Bi-anisotropic
"Acher limit", thin films with shape anisotropy) raise the product, which is how thin-film magnetic
materials reach GHz [4].

**Frequency response models.** A single relaxation μ_r = 1 + (μ_i − 1)/(1 + jf/f_r) reproduces the
typical broad NiZn spectrum: μ' flat then falling, μ'' peaking near f_r and decaying slowly as 1/f.
A damped resonance (Lorentz) μ_r = 1 + (μ_i − 1)/(1 − (f/f_r)² + jζf/f_r) reproduces narrower
resonances (and the negative μ' some datasheets show just above f_r). Both are causal. Using the
relaxation model with μ_i 800, f_r 8 MHz on the 1.19 nH bead (script):

| f | μ' | μ'' | Z (Ω) |
|---|---|---|---|
| 1 MHz | 788 | 98 | 0.7 + j5.9 |
| 10 MHz | 313 | 390 | 29 + j23 |
| 100 MHz | 6.1 | 64 | 47 + j4.5 |
| 1 GHz | 1.05 | 6.4 | 48 + j8 |

At 100 MHz and above the bead is essentially a **~50 Ω resistor** (for this model): ωL0μ'' ≈
2πf·L0·(μ_i f_r/f) = 2πL0μ_i f_r — frequency independent. That broadband resistance is what makes
beads effective EMI absorbers: they dissipate rather than reflect, and don't create high-Q resonances
with stray capacitance. Real beads also have a winding/terminal capacitance that eventually takes over
(|Z| falls above a self-resonance, often 0.5–2 GHz for SMD beads) — see
[ferrites and beads](../04-real-components-hf/ferrites-and-beads.md).

**Practical mix choice (Palomar/Fair-Rite guidance) [5][7]:**

| Mix | Class | μ_i | Suppression range (vendor) | Inductors / transformers |
|---|---|---|---|---|
| 75 | MnZn | 5000 | 150 kHz–10 MHz | 0.1–10 MHz |
| 73 | MnZn | 2500 | < 50 MHz | < 10 MHz |
| 31 | MnZn | 1500 | 1–300 MHz (best 1–10 MHz) | 1:1 only |
| 43 | NiZn | 800 | 25–300 MHz | 3–60 MHz |
| 52 | NiZn | 250 | 200–1000 MHz | 1–60 MHz |
| 61 | NiZn | 125 | 200–1000 MHz | 1–300 MHz (Fair-Rite: inductors to ~25 MHz) |
| 67 | NiZn | 40 | (low-loss inductors to ~50–100 MHz — from knowledge) | |

Note the vendor ranges are consistent with Snoek: *low-loss inductor use* ends near f_r
(61: ~25–50 MHz), while *suppression use* starts near f_r where μ'' is large.

**For Marcus's bands:** at 433/915 MHz, clamp-on 43 cores still add resistive impedance on cables
(common-mode chokes on the LoRa coax or GNSS cable) but a few turns are needed; 52/61 are better per
turn at 433–1000 MHz. As *inductor cores* no bulk ferrite is useful at 433 MHz — use air-core or
ceramic-core inductors. At 2.4 GHz only special GHz-rated SMD beads work, and their impedance comes
largely from geometry and conductor loss.

### Level 2 — MnZn vs NiZn: resistivity, permittivity, dimensional resonance

MnZn ferrites have resistivity ~0.1–10 Ω·m and apparent εr of 10⁴–10⁵ at low frequency (grain
boundary capacitance); NiZn: ~10³–10⁷ Ω·m (Fair-Rite 43: 10⁵ Ω·cm = 10³ Ω·m [7]) and εr ~ 10–20 at
high frequency (medium confidence). In MnZn the internal wavelength λ = λ0/√(μ'ε') becomes comparable
to the core size at MHz frequencies: with μ 2000 and εr 10⁵, λ ≈ 2.1 cm at 1 MHz (script), so a
2 cm core supports a half-wave standing wave — **dimensional resonance** — and effective μ collapses
and loss spikes. Together with eddy currents this limits MnZn to power and low-HF use.

### Level 2 — powdered iron and gapped cores: the distributed air gap

**A gap in series with the core.** Take a closed core of path length $\ell_e$ and permeability μ, with a small gap $g\ll\ell_e$. $B$ is continuous across the gap (no fringing). Ampère's law gives $NI=\frac{B}{\mu_0\mu}\ell_e+\frac{B}{\mu_0}g$, so the core behaves as one material of
$$\mu_e=\frac{B\,\ell_e}{\mu_0NI}=\frac{\mu}{1+\mu g/\ell_e}\;\xrightarrow{\;\mu g\gg\ell_e\;}\;\frac{\ell_e}{g}.$$
Once the gap dominates, μ_e is set by geometry, not by the material. Differentiate: $\frac{d\mu_e}{\mu_e}=\frac{d\mu}{\mu}\cdot\frac{\mu_e}{\mu}$. A relative change of μ, whether from temperature, DC bias, or the imaginary part (μ → μ′ − jμ″), is **diluted by μ_e/μ**. So the temperature coefficient and the loss tangent tan δ = μ″/μ′ both fall by that factor. The price: (a) A_L falls by μ/μ_e, so you need √(μ/μ_e) times more turns for the same L, with more copper loss and self-capacitance; (b) saturation needs μ/μ_e times more ampere-turns, which is the point of a gapped power choke. Example (`tools/verify/s4_core_turns_loss.py` §5): a 43 FT240 (μ 800, ℓ_e 145 mm) with a 3.4 mm gap gives μ_e = 40, 630 ppm/°C and material Q ≈ 20 at 7 MHz, against 1.25 %/°C and Q ≈ 1 ungapped.

**Iron powder is the same idea taken to the limit.** Carbonyl iron is made by decomposing Fe(CO)₅ into roughly spherical particles a few µm across (particle size from knowledge). The particles are coated with an insulator and pressed with a binder. Every particle is separated from its neighbours by a thin non-magnetic layer, so the gap is *distributed* through the volume. A sphere of very high intrinsic μ in a non-magnetic matrix can raise the average B only by its shape (demagnetising factor 1/3). The Maxwell Garnett mixing rule in the limit μ_particle → ∞ gives
$$\mu_e\approx\frac{1+2p}{1-p},$$
where $p$ is the volume fill fraction. The Micrometals densities (5.0 g/cm³ for −2/−6, 6.4–6.5 for −1/−3/−8/−15) against iron's 7.87 give p = 0.64 and 0.81–0.83, so μ_e ≈ 6 and 14–15. The catalogue values are 8.5–10 and 20–35 [10]. That is the right size: the mixing rule ignores particle contact and non-sphericity, which raise μ at high fill (script §8). The large intrinsic μ of iron has almost no effect, which is why the mixes are so stable. The +35 to +95 ppm/°C that remains is set by the gap structure and binder rather than by iron's own μ(T) (mechanism from knowledge, medium confidence); the vendor offers tuned mixes, with −6/−7 at 35/30 ppm/°C the most stable [10].

**Why powder has low eddy loss although iron is a metal.** In bulk iron (σ ≈ 10⁷ S/m, μ_r ≈ 100 assumed) the skin depth is 16 µm at 1 MHz and 5 µm at 10 MHz, so a solid core would carry flux only in a thin skin. Particles of a few µm are at or below δ, so the field penetrates them, and the classical eddy loss of a sphere scales as $p_{ec}=\sigma(\pi f B d)^2/20$, ∝ d²f². For d = 5 µm this gives 1.2 × 10⁻⁴ W m⁻³ T⁻² Hz⁻², close to the eddy coefficient in Micrometals' −2 loss formula (9.6 × 10⁻⁵ in the same units). Converted to a loss tangent, the term gives μ″ ∝ f, i.e. a material Q of ≈ 720/370/180/90 at 3.6/7.1/14.2/28.5 MHz. That matches the vendor's "high Q to 40 MHz" for −2 and the higher maximum frequencies of the finer −10/−17 mixes (83/170 MHz). Hysteresis loss grows as B³ at low flux (Rayleigh region), so it is negligible in receive-level tuned circuits.

**Ferrite vs powder in one sentence.** A ferrite is an insulating *ceramic* with a high, lossy, temperature-sensitive μ that Snoek limits to low frequency. Iron powder is a *metal* diluted by a distributed gap into a low, stable μ with small loss that grows as f². Choose ferrite for broadband ohms per turn and powder for tuned, stable, high-Q coils. The mix table and EFHW numbers are on [ferrites and beads](../04-real-components-hf/ferrites-and-beads.md#iron-powder-vs-ferrite-cores-gapped-cores-and-hf-transformers-efhw-491).

### Level 3 — gyrotropic ferrites: the Polder tensor

Bias the ferrite with an internal static field H0 along z so that M = M_s ẑ. Linearising the
Landau–Lifshitz equation for small RF fields (e^{jωt}) gives **b** = μ0[μ]**h** with
$$[\mu] = \begin{pmatrix}\mu & j\kappa & 0\\ -j\kappa & \mu & 0\\ 0 & 0 & 1\end{pmatrix},\qquad \mu = 1 + \frac{\omega_0\omega_m}{\omega_0^2 - \omega^2},\quad \kappa = \frac{\omega\,\omega_m}{\omega_0^2 - \omega^2},$$
ω0 = γμ0H0 (Larmor/FMR), ω_m = γμ0M_s (Pozar §9.1 [1]; sign of κ depends on the time convention
and the sign convention for γ). Losses: replace ω0 by ω0 + jαω (Gilbert damping) or equivalently
use the FMR linewidth ΔH (YIG single crystals: ΔH < 1 Oe; polycrystalline microwave ferrites: tens of
Oe — from knowledge).

**Circularly polarised eigenmodes.** For waves along z, right- and left-circular RF fields see
$$\mu_\pm = \mu \pm \kappa = 1 + \frac{\omega_m}{\omega_0 \mp \omega}.$$
The "+" (co-rotating with precession) mode resonates at ω = ω0 (FMR absorption); the "−" mode does not.
Checked in the script: YIG (μ0M_s = 0.178 T), μ0H0 = 0.05 T, 10 GHz: μ+ = 0.42, μ− = 1.44.

**Faraday rotation.** A linear wave = RHCP + LHCP; with β± = k0√(εrμ±) they accumulate different phase
and the polarization plane rotates by θ = (β− − β+)L/2 — in the same sense regardless of propagation
direction relative to the lab (non-reciprocal: a round trip doubles rather than cancels the rotation).
For a fully-filled YIG medium (εr ≈ 15) at 10 GHz with the numbers above, (β− − β+)/2 ≈ 224 rad/m ≈
128°/cm (illustrative; practical rotators use partially filled guides and weaker magnetisation).

**Kittel formulas (shape matters).** The internal field differs from the applied field by the
demagnetising field. FMR frequency: infinite medium/sphere f = (γ/2π)μ0H_applied; thin film magnetised
in-plane f = (γ/2π)√(B0(B0 + μ0M_s)); normally magnetised film f = (γ/2π)(μ0H_applied − μ0M_s). Script:
YIG film in-plane at 0.1 T → 4.7 GHz vs 2.8 GHz for a sphere. YIG-sphere filters and oscillators tune
linearly at 28 MHz/mT.

**Devices** (details in [circulators/isolators](../06-rf-circuits/circulators-isolators.md)):
junction circulators (Y-junction stripline with ferrite discs; operated above or below resonance to
avoid FMR loss), resonance isolators (absorb the co-rotating mode), field-displacement isolators,
Faraday-rotation isolators, phase shifters (latching ferrite phase shifters in phased arrays — link
[12-phased-arrays](../12-phased-arrays/phase-shifters-ttd-components.md)), YIG-tuned filters/oscillators.

### Level 3 — ferromagnetic metals (nickel, iron) at RF

Nickel (μ0M_s ≈ 0.61 T), iron and steels are metals: eddy currents confine the field to a skin depth
δ = 1/√(πfμσ), which is reduced by √μ_r. With μ_r ≈ 100, nickel's δ at 433 MHz would be ~0.6 µm vs 6.4 µm
for μ_r = 1 (see skin-effect table). The effective RF permeability of Ni decreases through the
sub-GHz to GHz range as the FMR/natural resonance is approached, and it is strongly affected by
stress, thickness and (for electroless Ni-P) phosphorus content (high-P deposits are non-magnetic)
[8]. Consequences: steel screws, nickel-plated connectors and ENIG finishes add loss and can generate
passive intermodulation (hysteresis nonlinearity) — avoid them in the RF path of high-power or
multi-carrier systems.

## Design equations & rules of thumb

| Equation | When valid | Typical value |
|---|---|---|
| Z = jωL0(μ' − jμ'') | winding on core | bead above f_r ≈ 2πL0μ_if_r (resistive) |
| (μ_i − 1)f_r ≈ (2/3)(28 GHz/T)μ0M_s | polycrystalline, unbiased | NiZn ≈ 6.5 GHz; MnZn ≈ 9 GHz |
| L0 = (μ0h/2π)ln(OD/ID) per turn² | toroid | small bead ≈ 1.2 nH |
| f_FMR = 28.0 GHz/T × μ0H_internal | biased ferrite | 0.1 T → 2.8 GHz |
| μ± = 1 + ω_m/(ω0 ∓ ω) | biased, circular modes | YIG 0.05 T, 10 GHz: 0.42 / 1.44 |
| Thin film: f = γ/2π √(B0(B0+μ0M_s)) | in-plane bias | YIG 0.1 T → 4.7 GHz |
| Use NiZn for > ~1 MHz; MnZn < ~1–10 MHz | material choice | — |
| μ_e = μ/(1 + μg/ℓ_e) | gapped core, g ≪ ℓ_e | tempco, tan δ scale by μ_e/μ |
| μ_e ≈ (1+2p)/(1−p) | dilute high-μ spheres (Maxwell Garnett) | p 0.64 → 6 (−2/−6 catalogue 10/8.5) |
| p_ec = σ(πfBd)²/20 | eddy loss in a conducting sphere | d 5 µm ≈ Micrometals −2 term |

## Worked examples

**1. Can I wind a 433 MHz matching inductor on a 61-material toroid?** Snoek: μ_i = 125 → f_r ≲ 53
MHz. At 433 MHz, μ' ≈ 1–5 and μ'' comparable → Q of order 1. No: use an air-core or ceramic-core
inductor (Q 40–100 at 433 MHz; see [inductors at RF](../04-real-components-hf/inductors-at-rf.md)).

**2. Choke for the GNSS antenna cable.** Common-mode current on the outside of a coax near 1575 MHz:
bulk 43 material has μ'' of only a few there; a clamp-on core adds perhaps tens of ohms per turn.
Better: a sleeve balun/λ/4 choke or good cable routing (13-pcb EMC). For 100–300 MHz digital noise on
the same cable, a 43 core with 2–3 turns (hundreds of ohms) is effective.

**3. Snoek estimate for a datasheet.** A NiZn material lists μ_i = 250 and B = 3000 G at 10 Oe:
(μ_i − 1)f_r ≈ (2/3)(2.80 MHz/Oe)(3000) = 5.6 GHz → f_r ≈ 22 MHz. Its vendor suppression range
(e.g. 52 material: 200–1000 MHz) starts an order of magnitude above f_r, where μ'' dominates.

## Practical notes
- Ferrite data are for small signals at 25 °C; μ_i varies strongly with temperature (MnZn has a
  secondary permeability maximum; NiZn falls toward the Curie point, e.g. > 130 °C for 43 [7]) and DC
  bias (a bead carrying DC saturates and loses impedance — check the DC-bias derating curve).
- "Impedance at 100 MHz" is the standard SMD-bead spec; ask for the full R/X/|Z| curve and the
  DC-bias curves.
- Ferrites next to antennas detune and absorb: keep beads and ferrite-loaded parts out of the antenna's
  reactive near field unless intended.
- Ferrite and magnetic materials show hysteresis → intermodulation; for PIM-sensitive systems
  (duplex, multi-carrier) avoid ferromagnetic materials in the RF path.

## Common mistakes & misconceptions
- **"High-μ ferrite = better choke at all frequencies."** Above f_r, μ' collapses; a low-μ NiZn can
  give more impedance at 400 MHz than a high-μ MnZn.
- **"Beads are inductors."** Above f_r they are mostly resistors — that's the point.
- **"Ferrites block RF by reflecting it."** Suppression ferrites absorb (μ''), converting RF to heat.
- **"μ_r = 1 for everything at RF."** True for non-magnetic metals and most dielectrics; false for
  nickel, steel, ferrites and magnetic absorbers up to their resonances.
- **"Magnets affect radio waves."** In air they do not. Maxwell's equations are linear in vacuum, so a static field simply adds to the RF field without interacting with it. A copper antenna next to a 0.5 T NdFeB magnet changes its resistance only by about (μ_e B)² ≈ 5 × 10⁻⁶ (magnetoresistance). Magnets matter only through **materials that respond to them**: (a) ferrites and iron cores, where a magnet's 0.3–0.5 T surface field pushes 43 material (B ≈ 0.35 T at 10 Oe) towards saturation and collapses μ, detuning a ferrite-rod AM antenna or killing a bead or choke; (b) magnetised plasma, where the Earth's 50 µT field gives the ionosphere a 1.40 MHz electron gyrofrequency and hence Faraday rotation and o/x modes ([09 HF propagation](../09-propagation-link-budget/hf-propagation-modes-and-prediction.md)); (c) biased ferrite devices such as circulators and YIG filters, by design (above; gyrofrequency 28 GHz/T). A magnetic car-roof mount is fine; a speaker magnet next to a ferrite-cored inductor is not (`tools/verify/s4_thin_film.py` §4).
- **"Iron powder has μ ≈ 10 because it is poor iron."** The particles are excellent iron. The μ is low because of the distributed insulating gap, and that same gap is what makes the core stable and hard to saturate.
- **"A gap only lowers inductance."** It also divides the temperature coefficient, the loss tangent and the DC-bias sensitivity by μ/μ_e. It is a design tool, not a defect.
- **Unit trap in Snoek's formula**: M_s in A/m vs 4πM_s in gauss vs μ0M_s in tesla differ by factors
  of 4π and μ0.
- **"Circulators are reciprocal devices with clever phasing."** They require a gyrotropic
  (non-reciprocal) material — biased ferrite — or active/time-modulated circuits.

## How to simulate / verify
- `python3 tools/verify/s4_thin_film.py` §4 — gyrofrequency vs B, copper magnetoresistance order of magnitude.
- `python3 tools/verify/s4_core_turns_loss.py` §5, §8 — gapped μ_e/tempco/Q dilution; Maxwell Garnett fill-fraction estimate vs catalogue μ; iron skin depth vs particle size; sphere eddy coefficient vs Micrometals' formula.
- `python3 tools/verify/em_magnetics.py` — Snoek-limit table; relaxation vs Lorentz permeability
  models and bead impedance; Polder tensor μ, κ, μ± identities; Kittel FMR for sphere and film;
  Faraday rotation estimate; MnZn dimensional-resonance wavelengths.
- Fit vendor μ'(f), μ''(f) CSV (Fair-Rite provides downloadable complex-permeability data) with one or
  two relaxation/Lorentz poles for SPICE (bead model) or FDTD (openEMS Lorentz material).
- Measure a bead or choke with a VNA in series-through configuration (Z = 2Z0(1 − S21)/S21) — see
  17-test-measurement.

## Open questions / gaps
- Measured μ(f) of electroplated and electroless nickel (ENIG) at 0.1–10 GHz: not found in this
  session; needed to firm up the ENIG loss model.
- NiZn/MnZn resistivity and permittivity ranges quoted at medium confidence (only Fair-Rite 43's 10⁵
  Ω·cm verified).
- The Polder κ sign convention differs between texts (Pozar vs Collin vs physics); verified only the
  μ± magnitudes, not the handedness mapping.

## Sources
1. D. M. Pozar, *Microwave Engineering*, 4th ed., ch. 9 (theory and design of ferrimagnetic
   components: Polder tensor, circular polarization, Faraday rotation, circulators, isolators). (textbook)
2. C. A. Balanis, *Advanced Engineering Electromagnetics*, 2nd ed., §2.4–2.5 (magnetic materials,
   ferrites, tensor permeability). (textbook)
3. J. L. Snoek, "Dispersion and absorption in magnetic ferrites at frequencies above one Mc/s,"
   *Physica* 14, 207–217 (1948). (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
4. T. Nakamura, "Snoek's limit in high-frequency permeability of polycrystalline Ni–Zn, Mg–Zn, and
   Ni–Zn–Cu spinel ferrites," *J. Appl. Phys.* 88, 348 (2000); and "Generalization of Snoek's limit for
   modeling initial permeability of magnetic materials," *J. Appl. Phys.* 63, 3765 (1988). (peer-reviewed;
   via abstracts)
5. Palomar Engineers, "Ferrite mix selection" (mix, μ_i, suppression and transformer ranges). (vendor)
6. B. Lax and K. J. Button, *Microwave Ferrites and Ferrimagnetics*, McGraw-Hill 1962 (Polder tensor,
   Kittel equations). (textbook; cited from knowledge)
7. Fair-Rite Products, "43 Material data sheet" (μ_i 800, B 3500 G at 10 Oe, ρ 1×10⁵ Ω·cm, T_c > 130 °C;
   complex-permeability CSV); 61-material product highlight (inductors to 25 MHz, EMI > 200 MHz). (datasheet)
8. Electroless-nickel property summaries (high-P deposits non-magnetic as plated) — see
   [skin-effect page](skin-effect-conductor-loss-roughness.md) source 12. (industry — medium)
9. C. Kittel, "On the theory of ferromagnetic resonance absorption," *Phys. Rev.* 73, 155 (1948).
   (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
10. Micrometals, *2019 Iron Powder RF Materials* catalogue (mix μ, density, temperature coefficient,
   maximum frequency, core-loss formula with eddy coefficient d). https://www.acalbfi.com/media/pdf/RF_materials_micrometals_2019.pdf (datasheet)
11. Maxwell Garnett mixing rule and the eddy loss of a conducting sphere in a uniform AC field —
   standard results, e.g. A. Sihvola, *Electromagnetic Mixing Formulas and Applications*, IET 1999 (textbook; Sihvola 1999 (IET, doi:10.1049/pbew047e) checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge),
   and classical eddy-current texts; both checked numerically against the Micrometals data in s4_core_turns_loss.py §8.
