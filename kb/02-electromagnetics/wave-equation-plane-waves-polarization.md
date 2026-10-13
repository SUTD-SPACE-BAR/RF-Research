---
title: Wave equation, plane waves, lossy media and polarization
domain: 02-electromagnetics
slug: wave-equation-plane-waves-polarization
tags: [wave-equation, helmholtz, plane-wave, propagation-constant, intrinsic-impedance, lossy-media, attenuation, polarization, circular-polarization, axial-ratio, handedness, IEEE-convention]
prerequisites: [maxwells-equations.md, ../00-math-foundations/complex-numbers-and-phasors.md, ../00-math-foundations/differential-equations-circuits-waves.md]
related: [poynting-vector-power-flow.md, boundary-conditions-reflection-refraction.md, skin-effect-conductor-loss-roughness.md, dielectrics-permittivity-loss-tangent.md, ../08-antennas/antenna-polarization-and-circular-polarization.md, ../09-propagation-link-budget/polarization-mismatch-loss.md, ../03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Wave equation, plane waves, lossy media and polarization

## Questions this page answers
- How does the wave equation fall out of Maxwell's equations?
- What are the propagation constant γ = α + jβ and the intrinsic impedance η, and how do I compute them for any material?
- What is the wavelength and speed of a wave inside FR-4, water or fibreglass?
- How fast does a 433 MHz signal die in sea water, fresh water or a lossy radome?
- What is the difference between linear, circular and elliptical polarization, and what is axial ratio?
- Which way does a "right-hand circularly polarized" wave rotate — and why do physics/optics books say the opposite?
- How much signal do I lose receiving a circularly polarized GNSS signal with a linear antenna?

## TL;DR
- Source-free Maxwell ⇒ **vector Helmholtz equation** ∇²**E** − γ²**E** = 0 with **γ = √(jωμ(σ + jωε)) = α + jβ** (Np/m, rad/m) [1][2][3].
- **Intrinsic impedance η = √(jωμ/(σ + jωε))**; vacuum η0 = 376.73 Ω; lossless dielectric η = η0/√εr (FR-4 ≈ 180 Ω); good conductor η = (1+j)/(σδ) (Cu at 433 MHz: 5.43 mΩ ∠45°).
- Lossless dielectric: β = ω√(με), **λ = λ0/√(εr μr)**, **v_p = c/√(εr μr)**. FR-4 (εr 4.4) at 915 MHz: λ = 15.6 cm, v = 0.477c.
- Low-loss dielectric: **α ≈ (β/2) tanδ** ⇒ **27.3·tanδ dB per wavelength in the material** (FR-4: 0.55 dB/λ; 3.5 dB/m at 915 MHz).
- Good conductor: **α = β = 1/δ**, δ = 1/√(πfμσ) (Cu, 433 MHz: 3.18 µm). Sea water (εr 70, σ 5 S/m) at 433 MHz: α = 78 Np/m = **680 dB/m**, 1/e field depth 1.3 cm.
- Polarization = the curve traced by **E** at a fixed point. Axial ratio AR = major/minor axis (0 dB = circular, ∞ = linear).
- **IEEE handedness**: point your thumb along the propagation direction; if your fingers curl the way **E** rotates, the hand you used names the polarization. With e^{jωt} and propagation +z, **(x̂ − jŷ) is RHCP**. Traditional optics naming ("as seen by an observer facing the oncoming wave") calls the same wave *left*-handed. **IEEE-RHCP = optics-LCP.** GNSS signals are RHCP in the IEEE sense [4][5].
- Linear antenna receiving pure CP: **−3 dB**. Opposite-sense CP: theoretically −∞ dB (typically 15–25 dB in practice, limited by AR). Verified in `tools/verify/em_plane_waves.py`.

## Intuition (no math)
A plane wave is the simplest self-sustaining solution of Maxwell's equations: sheets of uniform E
and H, perpendicular to each other and to the direction of travel, sliding along at the speed of
light in the medium. It is what any antenna's field looks like when you are far enough away that
the wavefront curvature across your receiver is negligible.

In a material, polarisable molecules "load" the wave — the field has to push charges around as it
passes — and the wave slows down by √εr. Wavelength shrinks by the same factor, because frequency
cannot change across a boundary (the source sets it). If the charges also collide and dissipate
energy (loss tangent, conductivity), the wave decays as it goes. In a metal the electrons are free,
the wave drives huge currents, and it dies within a few micrometres: the skin effect.

Polarization is simply the *direction* of the electric field and how that direction evolves in
time. If E always points the same way (up–down), it's linear. If E has two perpendicular
components that are 90° apart in time phase and equal in size, the tip of E traces a circle —
circular polarization. Everything in between is elliptical. Circular polarization is popular for
satellites (GNSS) and rockets because the received power doesn't depend on how the antennas are
rotated about the line of sight, and because reflections flip the handedness, so a matched CP
antenna rejects single-bounce multipath.

## The math

### Level 1 — the key results

For a wave travelling in +z with time dependence e^{jωt}:
$$\mathbf E(z) = \mathbf E_0\,e^{-\gamma z} = \mathbf E_0\,e^{-\alpha z}e^{-j\beta z},\qquad \mathbf H = \frac{1}{\eta}\,\hat{\mathbf z}\times\mathbf E.$$

| Quantity | General | Lossless (σ = 0, ε real) | Units |
|---|---|---|---|
| propagation constant γ | √(jωμ(σ + jωε)) | jω√(με) | 1/m |
| attenuation α = Re γ | see Level 2 | 0 | Np/m (×8.686 → dB/m) |
| phase constant β = Im γ | see Level 2 | ω√(με) = 2π/λ | rad/m |
| wavelength λ | 2π/β | λ0/√(εrμr) | m |
| phase velocity v_p | ω/β | c/√(εrμr) | m/s |
| intrinsic impedance η | √(jωμ/(σ+jωε)) | √(μ/ε) = η0√(μr/εr) | Ω |

Symbols: ω = 2πf (rad/s); μ = μ0μr (H/m); ε = ε0εr (F/m), complex if the material is lossy;
σ conductivity (S/m); η0 = 376.73 Ω.

### Level 1½ — wavelength, loss and impedance in a material, algebra only
- **The phase advances 360° per wavelength.** In a material λ shrinks by $\sqrt{\varepsilon_r\mu_r}$, and so does the speed.
- **The impedance drops by the same factor** (for μr = 1): $\eta = \eta_0/\sqrt{\varepsilon_r}$.
- **Low-loss attenuation.** If tanδ ≪ 1, then $\alpha \approx \beta\tan\delta/2$ Np/m. Multiply by 8.686 for dB/m. The loss per wavelength is therefore about $27.3\tan\delta$ dB, whatever the frequency.

*Worked number (verified, `tools/verify/s18b_level15_numbers.py`, which also checks the exact complex γ).* Bulk FR-4 at 433 MHz with εr 4.4 and tanδ 0.02:
- **Wavelength:** 0.692/√4.4 = **0.330 m**, so β = 19.0 rad/m.
- **Impedance:** η = 377/2.10 = **180 Ω**.
- **Loss:** α = 19.0 × 0.01 = 0.190 Np/m = **1.65 dB/m**. That is about 0.55 dB per wavelength, consistent with the 27.3 tanδ rule.

### Level 2 — deriving the wave equation

Start from the phasor curl equations in a homogeneous, linear, isotropic, source-free region
(see [Maxwell's equations](maxwells-equations.md)):
$$\nabla\times\mathbf E = -j\omega\mu\mathbf H,\qquad \nabla\times\mathbf H = (\sigma + j\omega\varepsilon)\mathbf E.$$
Take the curl of the first and substitute the second:
$$\nabla\times\nabla\times\mathbf E = -j\omega\mu(\sigma + j\omega\varepsilon)\mathbf E.$$
Use the identity ∇×∇×**E** = ∇(∇·**E**) − ∇²**E** and ∇·**E** = 0 (no free charge in a homogeneous
source-free region):
$$\boxed{\nabla^2\mathbf E - \gamma^2\mathbf E = 0,\qquad \gamma^2 = j\omega\mu(\sigma + j\omega\varepsilon).}$$
The same equation holds for **H**. In the time domain for σ = 0 this is ∇²**E** = με ∂²**E**/∂t²,
the wave equation with speed 1/√(με).

**Plane-wave solution.** Look for fields depending only on z: d²E_x/dz² = γ²E_x ⇒
E_x = E⁺e^{−γz} + E⁻e^{+γz} — forward and backward waves, exactly like voltage waves on a
transmission line (see [telegrapher's equations](../03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md);
the analogy is exact with V↔E, I↔H, Z0↔η, and γ = √((R+jωL)(G+jωC)) ↔ √(jωμ(σ+jωε))).
Faraday then gives H_y = E_x/η with
$$\eta = \frac{j\omega\mu}{\gamma} = \sqrt{\frac{j\omega\mu}{\sigma + j\omega\varepsilon}}.$$
Because ∇·**E** = 0 and ∇·**H** = 0, a plane wave has no field component along its direction of
travel: it is **TEM** (transverse electromagnetic). **E**, **H** and the propagation direction form a
right-handed triad (**E**×**H** points along travel). Verified symbolically in
`tools/verify/em_maxwell.py` (k = ω√(με), η = √(μ/ε)).

**Explicit α and β.** Write the loss tangent tanδ = σ/(ωε') (+ ε''/ε' for dielectric loss). Then
$$\alpha = \omega\sqrt{\frac{\mu\varepsilon'}{2}\left[\sqrt{1+\tan^2\delta}-1\right]},\qquad \beta = \omega\sqrt{\frac{\mu\varepsilon'}{2}\left[\sqrt{1+\tan^2\delta}+1\right]}.$$

**Limiting cases** (all checked numerically in `em_plane_waves.py`):

| Regime | Condition | α | β | η |
|---|---|---|---|---|
| Lossless | tanδ = 0 | 0 | ω√(με) | √(μ/ε) (real) |
| Low-loss dielectric | tanδ ≪ 1 | (β/2)·tanδ = (ω/2)√(με')·tanδ | ≈ ω√(με') | ≈ √(μ/ε')(1 + j tanδ/2) |
| Good conductor | tanδ ≫ 1 | √(πfμσ) = 1/δ | = α | (1+j)√(πfμ/σ) = (1+j)/(σδ) |

The low-loss result gives the useful rule **dielectric loss = 8.686·π·tanδ ≈ 27.3·tanδ dB per
wavelength (in the medium)**, or in dB/m: α_dB = 27.3·√εr·tanδ/λ0 (per metre with λ0 in m). This is
also the dielectric loss of any TEM transmission line filled with that dielectric (microstrip needs
a filling factor; see [planar lines](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md)).

The good-conductor result gives the skin depth δ and the surface resistance R_s = Re η = 1/(σδ),
developed in [skin effect](skin-effect-conductor-loss-roughness.md). η's 45° phase says E and H
are 45° out of time phase inside a metal; |η| of copper at 433 MHz is 7.7 mΩ — the metal nearly
shorts the tangential E field, which is why it reflects almost everything.

**Group velocity and dispersion.** If β(ω) is not proportional to ω (lossy/dispersive media,
waveguides), a narrow-band pulse envelope travels at v_g = dω/dβ, not v_p. In a lossless,
non-dispersive dielectric v_g = v_p. In lossy dielectrics with constant tanδ, the Kramers–Kronig
relations force εr to vary slowly with frequency (see
[dielectrics](dielectrics-permittivity-loss-tangent.md)), so real PCB interconnects are always
slightly dispersive.

### Level 2 — polarization

At a fixed point (z = 0) a general plane wave travelling along +z has
$$\mathbf E(t) = \mathrm{Re}\{(\hat x\,E_x + \hat y\,E_y)e^{j\omega t}\},\qquad E_x = a\,e^{j\phi_x},\ E_y = b\,e^{j\phi_y}.$$
Let Δφ = φ_y − φ_x.
- **Linear**: Δφ = 0 or π (any a, b). Tilt angle = atan(±b/a).
- **Circular**: a = b and Δφ = ±π/2.
- **Elliptical**: everything else.

**Handedness (IEEE Std 145 / 211 definition) [4][5][6].** A wave is *right-hand* polarized if,
viewed by an observer looking in the direction of propagation (i.e. from behind the wave, looking
away from the transmitter), **E** rotates clockwise — equivalently, counter-clockwise when viewed
with the wave approaching the observer. Equivalently: thumb of the **right** hand along the
propagation direction, fingers curl with **E**.

With e^{jωt} and +z propagation:
$$\mathbf E_\text{RHCP} = E_0(\hat x - j\hat y)e^{-jkz},\qquad \mathbf E_\text{LHCP} = E_0(\hat x + j\hat y)e^{-jkz}.$$
Check: for x̂ − jŷ, E(t) at z = 0 is x̂cos ωt + ŷ sin ωt — rotating from +x toward +y, i.e.
counter-clockwise about +z; thumb along +z, the right hand's fingers curl x→y ⇒ right-handed. The
script `em_plane_waves.py` traces E(t) numerically and confirms the sign of a Stokes-parameter
formula against the trace (the first version of the script had the Stokes sign flipped — exactly
the kind of error this topic invites).

**Three conventions that flip the answer:**
1. **Time convention.** Physics texts using e^{−iωt} write the *same* physical RHCP wave as
   (x̂ + iŷ)e^{ikz}. The algebraic sign of the imaginary unit is flipped; the physics isn't.
2. **Naming convention.** Traditional optics (e.g. Born & Wolf; Hecht) names handedness as seen by
   an observer *facing the oncoming wave*: clockwise = "right". That makes **IEEE-RHCP = optics
   LHCP** [5][7]. Particle-physics *helicity* (spin projection on momentum) agrees with IEEE:
   positive helicity = IEEE right-hand.
3. **Transmit vs receive, and reflections.** An antenna's handedness is defined for the wave it
   *transmits*. A helix wound right-handed radiates RHCP (IEEE) in axial mode. On reflection from a
   conductor at normal incidence the rotation sense in space is unchanged but the propagation
   direction reverses, so the handedness **flips** (RHCP → LHCP). A matched RHCP receiver therefore
   rejects single-bounce specular reflections — a key GNSS multipath mitigation (see
   [GNSS antennas](../08-antennas/gnss-antennas.md)).

Radio astronomy uses the IEEE convention (IAU 1973 resolution), which is the opposite of the
traditional optics convention [5]; always state which one you mean.

**Axial ratio.** Decompose any elliptical wave into RHCP and LHCP components of amplitudes E_R and
E_L. Then
$$\mathrm{AR} = \frac{|E_R| + |E_L|}{\big||E_R| - |E_L|\big|}\quad(\ge 1),\qquad \mathrm{AR_{dB}} = 20\log_{10}\mathrm{AR}.$$
Cross-polar discrimination XPD = 20 log(|E_R|/|E_L|) relates to AR by
XPD = 20 log[(AR+1)/(AR−1)]: AR = 3 dB ⇒ XPD = 15.3 dB; AR = 1 dB ⇒ XPD = 24.8 dB.

Using Stokes parameters with the sign fixed for e^{jωt}:
S0 = |E_x|² + |E_y|², S1 = |E_x|² − |E_y|², S2 = 2Re(E_xE_y*), S3 = 2Im(E_xE_y*);
ellipticity angle χ = ½ asin(S3/S0) (χ > 0 ⇒ IEEE right-hand for +z propagation), AR = 1/|tan χ|,
tilt ψ = ½ atan2(S2, S1). Example (script): E_x = 1, E_y = 0.8∠−60° ⇒ AR = 1.82 (5.2 dB), tilt 32.9°,
right-handed.

### Level 3 — polarization mismatch and the general lossy medium

**Polarization loss factor** between an incident wave of axial ratio r_w and a receive antenna of
axial ratio r_a, with major axes misaligned by Δθ (signs of r: + for right, − for left) [6][8]:
$$\mathrm{PLF} = \frac{1}{2} + \frac{4r_wr_a + (1-r_w^2)(1-r_a^2)\cos 2\Delta\theta}{2(1+r_w^2)(1+r_a^2)}.$$
Results (script): CP onto linear = −3.00 dB; two same-sense 3 dB-AR antennas: 0 dB (aligned) to
−0.51 dB (axes crossed); opposite-sense perfect CP: −∞. Link-budget use is in
[polarization mismatch](../09-propagation-link-budget/polarization-mismatch-loss.md).

**Faraday rotation and birefringence.** In magnetised plasma (ionosphere) or magnetised ferrite the
RHCP and LHCP waves have different β; a linearly polarized wave (= RHCP + LHCP) has its plane
rotated as it propagates. Faraday rotation through the ionosphere scales as 1/f²: large at VHF,
small but not zero at L-band — one reason GNSS uses CP (propagation details:
[09-propagation](../09-propagation-link-budget/ionospheric-hf-propagation.md); ferrite devices:
[magnetic materials](magnetic-materials-permeability.md)). In anisotropic dielectrics (glass-weave
laminates, 3D-printed parts with oriented rasters) two linear polarizations see different εr —
birefringence; a thin anisotropic radome can slightly degrade CP axial ratio.

**Non-uniform and evanescent plane waves.** In lossy media or beyond the critical angle of total
internal reflection, planes of constant phase and constant amplitude need not coincide; the
propagation vector becomes complex, **k** = **β** − j**α** with **α** not parallel to **β**. These
"inhomogeneous plane waves" appear in [reflection/refraction](boundary-conditions-reflection-refraction.md)
and in waveguides below cutoff ([waveguides](waveguides-and-cavity-resonators.md)).

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| λ = 299.79/(f_MHz √εr) m | lossless or low loss | FR-4 915 MHz: 15.6 cm; RO4003C 2.45 GHz: 6.49 cm |
| v_p = c/√εr | non-magnetic, low loss | FR-4: 0.477c ≈ 14.3 cm/ns |
| η = 376.73/√εr Ω | non-magnetic, low loss | FR-4: 180 Ω; RO4003C: 200 Ω; water (εr 80): 42 Ω |
| α_dB ≈ 27.3·tanδ per λ (in medium) | tanδ ≪ 1 | FR-4 tanδ 0.02: 0.55 dB/λ |
| α_dB/m ≈ 91·f_GHz·√εr·tanδ | tanδ ≪ 1 | FR-4 915 MHz: 3.5 dB/m |
| δ = 1/√(πfμσ) | tanδ ≫ 1 | Cu 433 MHz: 3.18 µm; see skin-effect page table |
| E_R ⟂ E_L; AR from Stokes | any polarization | AR 3 dB ⇒ XPD 15.3 dB |
| CP → linear: −3 dB | ideal antennas | GNSS patch vs whip: see 08-antennas |

(91 = 27.3 × 1/0.29979 × 1 GHz scaling: α_dB/m = 27.3 √εr tanδ / λ0 with λ0 = 0.29979/f_GHz m.)

## Worked examples

All numbers from `tools/verify/em_plane_waves.py`.

**1. Wavelength and loss in FR-4 at 915 MHz (εr 4.4, tanδ 0.02).**
β = 2π√4.4/λ0 = 2π·2.098/0.3276 = 40.2 rad/m ⇒ λ = 15.6 cm; v_p = 0.477c.
α = (β/2)·0.02 = 0.402 Np/m = 3.49 dB/m (exact 0.4022 Np/m). A 5 cm feedline would add 0.17 dB of
*dielectric* loss if it were a TEM stripline in FR-4 — conductor loss adds to this.

**2. 433 MHz beacon in sea water (εr = 70, σ = 5 S/m [ITU-R P.368]).**
tanδ = σ/(ωε) = 2.97 — neither regime applies, so use the exact formula: α = 78.3 Np/m
(680 dB/m), β = 109 rad/m (λ = 5.76 cm), |η| = 25.4 Ω ∠35.7°. The 1/e field depth is 1.28 cm
(identical to the ITU-R P.527 penetration-depth formula, eq. 4 [9] — checked). After 10 cm the field
is down 68 dB, on top of the reflection loss at the surface. At 2.45 GHz: α = 109 Np/m, 1/e depth
0.92 cm. (Sea water's permittivity also varies with frequency — the P.527 model is implemented in
`em_dielectrics.py` — but σ ≈ 5 S/m dominates at UHF.)

**3. Fresh water at 433 MHz (εr = 80, σ = 0.01 S/m).** Conduction alone gives α = 0.21 Np/m =
1.8 dB/m, λ = 7.7 cm, η = 42 Ω. But that is the wrong answer: water's *dipolar relaxation* (Debye,
relaxation frequency ≈ 17 GHz at 20 °C) contributes ε'' ≈ 1.9 at 433 MHz (ITU-R P.527-6 model), about
4.5× the conduction term (0.42). Total: tanδ ≈ 0.029, **α ≈ 1.18 Np/m ≈ 10 dB/m**, 1/e depth 0.85 m
(`em_dielectrics.py`). At 2.45 GHz dipolar loss alone gives 266 dB/m — the microwave-oven effect. See
[dielectrics](dielectrics-permittivity-loss-tangent.md).

**4. Polarization of a crossed-dipole with imperfect phasing.** Two crossed dipoles fed with equal
amplitude but a 70° (instead of 90°) phase shift: E_x = 1, E_y = 1∠−70°. AR = 1/tan(35°) = 1.43 →
**3.1 dB**, right-handed for +z. A 20° phasing error alone costs you "3 dB AR" CP.

**5. Linear 433 MHz ground antenna receiving a spinning rocket's linear antenna.** Instantaneous
PLF = cos²Δθ; as the rocket rolls, Δθ sweeps through 90° and the link fades to −∞ (in practice
−20 to −30 dB). Using a CP ground antenna (or CP on either end) converts this into a constant
−3 dB loss. This is a central design choice in
[rocket telemetry radio design](../15-lora-ism-radios/rocket-telemetry-radio-design.md).

## Practical notes
- Measure a material's εr from the wavelength: resonators (ring, λ/2 line) on the substrate give
  λ_g, hence εr,eff. The plane-wave formulas apply to stripline directly and to microstrip via εr,eff.
- For radomes and nose cones, the loss inside the wall is usually negligible (a few mm of material:
  < 0.05 dB) compared with **reflection** at the walls (see
  [boundary conditions](boundary-conditions-reflection-refraction.md)).
- Human tissue (εr ≈ 40–55, σ ≈ 1–2 S/m at UHF) behaves like weak sea water: a body next to a
  433 MHz handheld absorbs and detunes. Pocketed transmitters lose 5–15 dB (08/09 domains).
- CP antennas are specified by AR *over a beamwidth*; AR is usually good only near boresight.
  A GNSS patch with 3 dB AR at zenith may be almost linear at the horizon.

## Common mistakes & misconceptions
- **"RHCP means clockwise."** Clockwise *as seen from where*? IEEE: clockwise viewed from behind
  the wave (looking in the propagation direction). Optics (traditional): clockwise viewed facing
  the wave = *right* in optics = *left* in IEEE. Always state the convention; see
  [antenna polarization](../08-antennas/antenna-polarization-and-circular-polarization.md).
- **Mixing time conventions.** x̂ − jŷ (e^{jωt}) and x̂ + iŷ (e^{−iωt}) are the same wave. Formulas
  pulled from physics papers need j → −i.
- **"A CP wave's E-field magnitude pulses at 2f."** For ideal CP the magnitude is constant; only
  direction rotates. For linear polarization the magnitude oscillates.
- **"Frequency changes in a dielectric."** Frequency is fixed by the source; wavelength and speed
  change.
- **"Loss tangent is a per-metre loss."** tanδ gives a loss per *wavelength* (27.3·tanδ dB/λ), so
  the same material is ~10× lossier per metre at 10× the frequency.
- **"Waves in metal travel at c."** In copper at 433 MHz v_p = ω/β = ωδ ≈ 8.6 km/s (!) and λ ≈ 20 µm
  — the wave inside the metal is a highly damped diffusion, not free propagation.
- **Using σ/(ωε) ≫ 1 formulas for sea water at GHz.** Sea water is transitional (σ/ωε ≈ 0.5–3)
  across 0.4–2.5 GHz; use the exact γ.

## How to simulate / verify
- `python3 tools/verify/em_plane_waves.py` — γ, η, λ, v_p for air, FR-4, RO4003C, G10, sea/fresh
  water, copper; low-loss and good-conductor approximations vs exact; ITU-R penetration depth; Stokes
  parameters, AR, tilt and IEEE handedness cross-checked against a numerical time trace;
  polarization-loss factor; field strength from EIRP.
- openEMS: a plane-wave excitation (`SetPlaneWaveExcite` in the MATLAB/Python interface) through a
  lossy slab reproduces α and the reflection — a good first validation of a new material model.
- scikit-rf `Freespace` media object gives γ and η for a (lossy, dispersive) medium.

## Open questions / gaps
- IEEE Std 145-2013 and IEEE Std 211-2018 definitions are quoted from secondary descriptions (MATLAB
  documentation, Thorlabs tutorial) and textbook knowledge; the standards themselves (paywalled) were
  not read directly.
- Measured AR degradation of CP through anisotropic 3D-printed or glass-weave radomes: not found;
  flagged for 08-antennas / antennas-on-rockets.

## Sources
1. D. K. Cheng, *Field and Wave Electromagnetics*, 2nd ed., 1989, ch. 8 (plane electromagnetic waves:
   lossless and lossy media, good conductors, polarization, group velocity). (textbook)
2. D. M. Pozar, *Microwave Engineering*, 4th ed., 2012, §1.4 (the wave equation and basic plane-wave
   solutions; lossy media; good conductors). (textbook)
3. S. Ramo, J. R. Whinnery, T. Van Duzer, *Fields and Waves in Communication Electronics*, 3rd ed.,
   Wiley 1994, ch. 6 (propagation and reflection of plane waves). (textbook)
4. IEEE Std 145-2013, *IEEE Standard for Definitions of Terms for Antennas* (polarization handedness
   definitions) — cited via [5], [6]. (standard; not read directly)
5. MathWorks, "Polarized Fields" (Phased Array System Toolbox documentation) and E. Gentzsch,
   "Polarization Handedness Convention," Thorlabs tutorial, 10 Jul 2017 — both state IEEE-RCP = optics
   LCP; radio astronomy follows IEEE. https://www.mathworks.com/help/phased/ug/polarized-fields.html
   (vendor documentation)
6. C. A. Balanis, *Antenna Theory*, 4th ed., 2016, §2.12 (polarization, axial ratio, polarization loss
   factor). (textbook)
7. M. Born and E. Wolf, *Principles of Optics*, 7th ed., Cambridge 1999, §1.4.2 (elliptical
   polarization; optics handedness convention). (textbook; cited from knowledge)
8. T. Milligan, *Modern Antenna Design*, 2nd ed., Wiley 2005, §1.11 (polarization mismatch between
   two elliptically polarized antennas). (textbook; cited from knowledge)
9. ITU-R P.527-6 (09/2021), eq. (4) penetration depth; and ITU-R P.368-10, Fig. 2 (sea water
   εr = 70, σ = 5 S/m). (standard)
10. S. J. Orfanidis, *Electromagnetic Waves and Antennas*, Rutgers (free online; site blocked
    2026-09-27), 2016 ed., ch. 2 "Uniform Plane Waves" (§2.1 lossless media, §2.5 Polarization, §2.6–2.7
    lossy and weakly lossy media) and ch. 4 "Propagation in Birefringent Media". (textbook, free; cited from
    knowledge. Chapter and section numbers checked against the 2016 table of contents by W5-S18b,
    2026-10-13. Polarization is §2.5, not ch. 4 as written before. Where the Stokes parameters and the
    IEEE-vs-optics handedness note sit inside the book was not checked.)
