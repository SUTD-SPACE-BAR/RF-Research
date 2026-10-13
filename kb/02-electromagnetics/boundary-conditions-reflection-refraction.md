---
title: Boundary conditions, reflection and refraction (Fresnel, Brewster, TIR, radomes, ground and sea)
domain: 02-electromagnetics
slug: boundary-conditions-reflection-refraction
tags: [boundary-conditions, fresnel, snell, brewster, total-internal-reflection, multilayer, transfer-matrix, radome, nose-cone, ground-reflection, sea-reflection, carbon-fibre, PEC, thin-film, sheet-resistance, paint, low-e-glass, optical-antenna, plasmonics, folklore]
prerequisites: [maxwells-equations.md, wave-equation-plane-waves-polarization.md, ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md]
related: [dielectrics-permittivity-loss-tangent.md, skin-effect-conductor-loss-roughness.md, ../08-antennas/antennas-on-rockets.md, ../09-propagation-link-budget/two-ray-ground-reflection.md, ../03-transmission-lines-matching/input-impedance-stubs-quarter-wave.md, ../13-pcb-rf-layout-emc/shielding-and-isolation.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Boundary conditions, reflection and refraction (Fresnel, Brewster, TIR, radomes, ground and sea)

## Questions this page answers
- What conditions must E, H, D and B satisfy at an interface between two materials or at a metal surface?
- How much of a wave reflects off a dielectric, the ground or the sea, and how does this depend on angle and polarization?
- What is the Brewster angle and why does vertical polarization over ground have a reflection "dip"?
- What is total internal reflection and what is an evanescent wave?
- How thick can a fibreglass nose cone be before it hurts my 433/915 MHz link? What is a half-wave radome wall?
- Can I put an antenna inside a carbon-fibre airframe?
- Why is the ground-reflected wave in a two-ray model nearly −1 at low grazing angles?
- Does a metal film thinner than the skin depth (a space blanket, a crisp packet, metallic paint, low-e window glass) let radio through?
- Do antennas still work at optical frequencies?

## TL;DR
- **Boundary conditions** (unit normal n̂ from 1 to 2): tangential **E** continuous; tangential **H** jumps by surface current (n̂ × (H₂ − H₁) = **J**_s); normal **D** jumps by surface charge; normal **B** continuous. At a perfect conductor: E_tan = 0, B_n = 0 [1][2][3].
- **Normal incidence**: Γ = (η₂ − η₁)/(η₂ + η₁) — exactly the transmission-line formula with Z → η. Air → εr 4.5: |Γ| = 0.36 (13 % power). Copper at 433 MHz absorbs only 4R_s/η0 = 5.8×10⁻⁵ of the incident power.
- **Snell's law** n₁ sin θ₁ = n₂ sin θ₂ (phase matching along the interface). **Fresnel coefficients** differ for TE (s, E ⟂ plane of incidence, "horizontal" over ground) and TM (p, "vertical").
- **Brewster angle** tan θ_B = n₂/n₁: TM reflection vanishes (air→εr 4.5: 64.8° from normal). Over lossy ground/sea there is a *pseudo*-Brewster minimum: sea at 433 MHz at ≈ 3.9° grazing (|R_V| = 0.32); medium ground ≈ 14.5° grazing.
- **Total internal reflection** beyond θ_c = asin(n₂/n₁) (εr 4.5 → air: 28.1°); the field outside is evanescent, decaying over ~ a tenth of a wavelength.
- **Radome / nose cone**: a *half-wave* solid wall (t = λ/(2√(εr − sin²θ))) is transparent at one frequency, but at 915 MHz in fibreglass it is **75.6 mm** thick — impractical. Rockets use **thin walls**: 2–3 mm of fibreglass (εr ≈ 4.7, tanδ 0.02) costs **< 0.1 dB at 433–915 MHz**, 0.2–0.7 dB at 2.45 GHz, and matters at 5.8 GHz+ (`tools/verify/em_fresnel_radome.py`). The bigger UHF risk is *detuning* of an antenna within ~λ/2π of the wall.
- **Carbon fibre is a conductor** (σ ≈ 10³–3×10⁴ S/m in-plane at UHF — the script's input range; DC values up to ~4×10⁴): a 1 mm CFRP wall attenuates 433 MHz by **≈ 46–111 dB** (`em_fresnel_radome.py` §3e; 50–162 dB at 1575 MHz). Antennas must be outside it or behind a fibreglass/glass window.
- **Thin conducting films obey a sheet law, not the skin depth**: for t ≪ δ, transmission = 2/(2 + η0/R_□), independent of frequency. 40 nm of aluminium (t/δ = 0.01 at 433 MHz) still blocks ≈ 48 dB; low-e glass (≈ 5 Ω/□) ≈ 32 dB; decorative metallic-flake paint (insulating flakes) ≈ 0 dB (`tools/verify/s4_thin_film.py`).
- Ground reflection at grazing incidence → Γ ≈ −1 for both polarizations: the basis of the two-ray model ([09-propagation](../09-propagation-link-budget/two-ray-ground-reflection.md)).

## Intuition (no math)
A wave hitting a new material must "fit" on both sides: the electric field along the surface cannot
jump (otherwise an infinite curl would be needed), and neither can the magnetic field along the
surface unless a sheet of current flows there. Satisfying both at once with just the incident and
transmitted wave is generally impossible when the two media have different impedances — so a
reflected wave appears to balance the books. It is the same story as a mismatched transmission line:
a 50 Ω line into 75 Ω reflects 20 % of the voltage; free space (377 Ω) into fibreglass (~174 Ω)
reflects 37 %.

At oblique incidence the wave's pattern along the surface must match on both sides, which fixes the
refraction angle (Snell). The reflection then depends on polarization, because the tangential-field
"bookkeeping" differs for E lying in the surface (TE) versus E tilted out of it (TM). For TM there is
one angle — Brewster's — where the reflected contributions cancel exactly; that is why polarised
sunglasses (vertical transmission axis) kill glare off water, and why vertically polarized radio
waves reflect weakly off the ground at moderate elevation angles.

A slab (radome, nose cone wall, PCB) has two surfaces. Their reflections add with a phase that
depends on the thickness. If the slab is very thin compared with the wavelength inside it, the two
reflections nearly cancel (they have opposite sign) and the slab is almost invisible. If it is exactly
half a wavelength thick, they cancel perfectly again. In between, they add.

## The math

### Level 1 — boundary conditions and normal incidence

With n̂ the unit normal pointing from medium 1 into medium 2, **J**_s the surface current (A/m),
ρ_s the surface charge (C/m²):

| Field | Condition | Derived from (pill-box / loop) |
|---|---|---|
| E tangential | n̂ × (**E**₂ − **E**₁) = 0 | Faraday, thin loop straddling the interface |
| H tangential | n̂ × (**H**₂ − **H**₁) = **J**_s | Ampère–Maxwell, thin loop |
| D normal | n̂ · (**D**₂ − **D**₁) = ρ_s | Gauss, thin pill-box |
| B normal | n̂ · (**B**₂ − **B**₁) = 0 | Gauss (magnetic), pill-box |

Between two ordinary dielectrics (no free surface current or charge): E_t, H_t, D_n, B_n all
continuous. At a **perfect electric conductor** (PEC; fields zero inside): E_t = 0, B_n = 0,
**J**_s = n̂ × **H**, ρ_s = n̂·**D**. A finite-conductivity metal carries the current in a skin depth
rather than a sheet; the PEC result is the δ → 0 limit (use the surface-impedance boundary condition
**E**_t = Z_s **J**_s with Z_s = (1+j)R_s — see [skin effect](skin-effect-conductor-loss-roughness.md)).

**Normal incidence** from medium 1 (η₁) on medium 2 (η₂), plane interface at z = 0:
$$\Gamma = \frac{E_r}{E_i} = \frac{\eta_2 - \eta_1}{\eta_2 + \eta_1},\qquad \tau = \frac{E_t}{E_i} = 1 + \Gamma = \frac{2\eta_2}{\eta_2 + \eta_1}.$$
Power reflected |Γ|², transmitted (lossless) 1 − |Γ|². For non-magnetic media
Γ = (n₁ − n₂)/(n₁ + n₂) with n = √εr.
- Air → εr 4.5: Γ = −0.359, |Γ|² = 12.9 %, return loss 8.9 dB.
- Air → water (εr ≈ 80): |Γ| = 0.80, |Γ|² = 64 %.
- Air → PEC: Γ = −1 (E cancels at the surface, H doubles).
- Air → copper at f: 1 − |Γ|² ≈ 4R_s/η0 (5.8×10⁻⁵ at 433 MHz; 4.3×10⁻⁴ at 24 GHz; verified).

### Level 2 — oblique incidence, Snell and Fresnel

Plane of incidence = plane containing the incident wave vector and the normal. Two independent
polarizations:
- **TE** (transverse electric, "s", "perpendicular", E ⟂ plane of incidence). Over flat ground this is
  **horizontal polarization**.
- **TM** (transverse magnetic, "p", "parallel", E in the plane of incidence). Over ground this is
  **vertical polarization** (E has a vertical component).

Phase matching of the tangential wavenumber gives Snell's law: k₁ sin θ_i = k₁ sin θ_r = k₂ sin θ_t,
so θ_r = θ_i and n₁ sin θ_i = n₂ sin θ_t.

Treating each polarization as a transmission-line problem with **wave impedances**
Z_TE = η/cos θ and Z_TM = η cos θ gives the Fresnel coefficients (non-magnetic media, E-field ratios):
$$r_\text{TE} = \frac{n_1\cos\theta_i - n_2\cos\theta_t}{n_1\cos\theta_i + n_2\cos\theta_t},\qquad r_\text{TM} = \frac{n_2\cos\theta_i - n_1\cos\theta_t}{n_2\cos\theta_i + n_1\cos\theta_t},$$
with cos θ_t = √(1 − (n₁/n₂)² sin²θ_i) (complex when medium 2 is lossy or beyond the critical angle;
pick the root that decays away from the interface).

**Sign conventions (a common source of disagreement).** The TM sign depends on the reference
directions chosen for the reflected E-field. With the form above (Born & Wolf, Hecht, and the
"vertical" coefficient used in radio propagation) r_TM → +(n₂−n₁)/(n₂+n₁) at normal incidence while
r_TE → −(n₂−n₁)/(n₂+n₁): they differ in sign at normal incidence even though the physical field is the
same, because the reflected TM reference vector flips. Some texts (and Pozar's Γ_∥ derived from the
H-field) use the opposite sign. Always compare magnitudes, or check at normal incidence.

Written with grazing angle ψ = 90° − θ_i (radio convention, medium 1 = air, medium 2 = ground of
complex εr):
$$R_H = \frac{\sin\psi - \sqrt{\varepsilon_r - \cos^2\psi}}{\sin\psi + \sqrt{\varepsilon_r - \cos^2\psi}},\qquad R_V = \frac{\varepsilon_r\sin\psi - \sqrt{\varepsilon_r - \cos^2\psi}}{\varepsilon_r\sin\psi + \sqrt{\varepsilon_r - \cos^2\psi}}.$$
As ψ → 0 both → −1 (hence the two-ray "−1" at long range). These are exactly r_TE and r_TM above
(identity checked in the script).

**Brewster angle.** r_TM = 0 when tan θ_B = n₂/n₁ (lossless). Air→εr 4.5: θ_B = 64.76° from normal
(25.2° grazing). There is no Brewster angle for TE with non-magnetic media. Script check: |r_TM| <
10⁻¹² at θ_B; energy conservation |r|² + (Re(n₂cosθ_t)/(n₁cosθ_i))|t|² = 1 to 10⁻⁹.

**Pseudo-Brewster angle.** With a lossy medium r_TM has a non-zero minimum and its phase swings
through −90°. For 433 MHz (script):

| Surface (εr) | pseudo-Brewster grazing angle | |R_V|min | |R_H| at same angle |
|---|---|---|---|
| Sea water, 20 °C, 35 g/kg: 71.6 − j200.6 (ITU-R P.527-6 [4]) | 3.9° | 0.32 | 0.99 |
| "Medium" ground: εr 15, σ 5 mS/m (illustrative) | 14.5° | 0.003 | 0.93 |

Consequence: vertically polarized links over the sea at a few degrees elevation see a much weaker
reflected ray (less multipath fading) than horizontally polarized ones; over land at 10–20°
elevation, V-pol reflection nearly vanishes. Rocket ground stations looking up at > 10° elevation
over land therefore see weak V-pol ground reflection but strong H-pol reflection (|R_H| ≈ 0.8–0.9).

**Total internal reflection (TIR).** Going from dense to less dense (n₁ > n₂), for
θ_i > θ_c = asin(n₂/n₁), sin θ_t > 1 and cos θ_t is imaginary: |r_TE| = |r_TM| = 1. The transmitted
field is **evanescent**, e^{−αz} with α = k₀√(n₁² sin²θ_i − n₂²), carrying no average power across the
interface. εr 4.5 → air: θ_c = 28.1°; at 60° incidence and 5.8 GHz the 1/e decay length in air is
5.3 mm (λ0 = 51.7 mm). TIR guides waves in dielectric slabs (surface waves on thick substrates,
dielectric resonator antennas, optical fibre) and explains why patch-antenna substrates can trap
power in surface waves (see [patch antennas](../08-antennas/patch-antennas.md)). Placing a second
dense medium within the evanescent tail couples power across ("frustrated TIR") — the principle of
some couplers.

### Level 2 — multilayers: transfer matrix and radome walls

Each homogeneous layer of thickness d, wave impedance Z_w (Z_TE = η/cos θ, Z_TM = η cos θ) and
normal wavenumber k_z = k₀√(εr − sin²θ₀) (θ₀ in air) acts as a transmission-line section with ABCD
matrix
$$\begin{pmatrix}\cos k_zd & jZ_w\sin k_zd\\ j\sin k_zd/Z_w & \cos k_zd\end{pmatrix}.$$
Multiply the matrices of all layers, terminate in the output medium's Z_w, and compute
Γ = (Z_in − Z₀)/(Z_in + Z₀) with Z₀ the input half-space's wave impedance — identical to cascading
line sections in [input impedance](../03-transmission-lines-matching/input-impedance-stubs-quarter-wave.md).
This is implemented in `slab_stack()` in `em_fresnel_radome.py`.

**Single slab in air**: reflection vanishes when k_z d = mπ:
$$t_\text{half-wave} = \frac{m\lambda_0}{2\sqrt{\varepsilon_r - \sin^2\theta_0}}.$$
For fibreglass-epoxy (εr ≈ 4.7) at normal incidence (m = 1): 160 mm at 433 MHz, **75.6 mm at
915 MHz**, 28 mm at 2.45 GHz, 11.9 mm at 5.8 GHz. Half-wave walls are practical only at X-band and
above (and are narrowband: they are transparent only near the design frequency and angle).

**Thin wall**: for k_z d ≪ 1 the slab is a small shunt susceptance; |Γ| ≈ (k₀d/2)(εr − 1) at normal
incidence. From the script (εr 4.7, lossless): |Γ|² < 1 % for t < λ_d/53 — i.e. **2.8 mm at 915 MHz**,
6.0 mm at 433 MHz, 1.06 mm at 2.45 GHz, 0.45 mm at 5.8 GHz (λ_d = λ0/√εr). |Γ|² < 10 % for about
3.4× those thicknesses.

**A-sandwich**: two thin, strong skins separated by a low-εr core (foam/honeycomb) about a quarter
wavelength (electrical) thick. The two skin reflections are equal and, after the round-trip through the
λ/4 core (180°), cancel. Script at 5.8 GHz: 0.5 mm skins (εr 4.7) + foam (εr 1.1): |Γ|² = −15 dB
with a 5 mm core, **−42 dB** with a 12.4 mm (≈ λ/4) core. (This is the "quarter-wave" radome; a
single quarter-wave layer is also the classic anti-reflection coating between two different media,
with n_layer = √(n₁n₂).)

**Loss inside the wall** is small unless the wall is thick in wavelengths: 27.3·tanδ dB per
wavelength in the material (see [plane waves](wave-equation-plane-waves-polarization.md)); a λ/2 wall
of tanδ = 0.02 costs 0.36 dB at any frequency.

### Level 3 — conducting walls, lossy half-spaces and limits of the plane-wave model

**Conducting sheet (carbon fibre, metallised plastic).** A conductor of thickness t ≫ δ transmits
roughly |τ|² ≈ (4η_m/η0)²·e^{−2t/δ} (η_m = (1+j)/(σδ) — "absorption + reflection" shielding
model, see [shielding](../13-pcb-rf-layout-emc/shielding-and-isolation.md)). CFRP laminates have
in-plane conductivity of order 10³–4×10⁴ S/m along the fibres and 1–100 S/m transverse (anisotropy
ratios ~10³ reported) [7][8]. Script (1 mm wall, isotropic σ as a bound):

| σ (S/m) | δ at 433 MHz | Transmission 433 MHz | 915 MHz | 1575 MHz |
|---|---|---|---|---|
| 10³ | 0.77 mm | −46 dB | −48 dB | −50 dB |
| 10⁴ | 0.24 mm | −80 dB | −93 dB | −107 dB |
| 3×10⁴ | 0.14 mm | −111 dB | −136 dB | −162 dB |

Even the pessimistic end kills a LoRa or GNSS link; a unidirectional ply with E ⟂ fibres is more
transparent, but any practical quasi-isotropic layup has plies in all directions. **Antennas must be
outside CFRP, or behind a fibreglass/Kevlar/glass window or nose cone** (see
[antennas on rockets](../08-antennas/antennas-on-rockets.md)).

**Thin films and paints (t ≪ δ): the sheet-resistance law.** When a conducting layer is much thinner than both δ and λ, the current density is uniform through it, so it acts as a single **shunt sheet conductance** $G_\square=\sigma t=1/R_\square$ on a "transmission line" of impedance η0 (free space on both sides). A shunt admittance $Y$ on a line of impedance $Z_0$ transmits $T=2/(2+Z_0Y)$, so
$$T=\frac{2}{2+\eta_0/R_\square},\qquad SE=20\log_{10}\!\Big(1+\frac{\eta_0}{2R_\square}\Big)\ \text{dB},$$
and the result is **frequency-independent**. It is mostly *reflection*: the sheet shorts out the wave impedance, and almost nothing is absorbed. The exact conducting-slab transfer matrix agrees within 0.2 dB up to t ≈ δ. Beyond that, absorption ($e^{-t/\delta}$, 8.7 dB per δ) adds on top (`tools/verify/s4_thin_film.py` §1: Al at 433 MHz, 10 nm → −36.5 dB, 1 µm → −76.4 dB; 16 µm kitchen foil → −114 dB exact vs −100 dB sheet law). Numbers (§2): 1 Ω/□ → 45.5 dB, 10 Ω/□ → 25.9 dB, 100 Ω/□ → 9.2 dB.

| Film | R_□ (typical, order) | Transmission |
|---|---|---|
| Silver-filled EMI paint, 25 µm | ≈ 0.02 Ω/□ | −80 dB |
| Copper/nickel EMI paint | 0.1–1 Ω/□ | −45 to −65 dB |
| Space blanket / aluminised PET (30–50 nm Al) | ≈ 1–2 Ω/□ | ≈ −40 dB |
| Low-e (silver-stack) window glass | ≈ 3–10 Ω/□ | −26 to −36 dB |
| ITO glass | 10–100 Ω/□ | −9 to −26 dB |
| Decorative metallic-flake paint, antistatic coatings | ≳ 10⁶ Ω/□ (flakes isolated in binder) | ≈ 0 dB |

The R_□ values are typical orders from product classes, not a single datasheet (medium confidence). Measure a coupon with an ohmmeter/four-point probe and apply the formula. In practice the seams, holes and edges of a wrapped phone or a "Faraday bag" leak far more than the film transmits ([shielding apertures](../13-pcb-rf-layout-emc/shielding-and-isolation.md)). The low-e result is why modern energy-efficient buildings have much higher building-entry loss than older ones (ITU-R P.2109 "thermally efficient" class [11]).

**Antennas at optical frequencies.** Metals follow the Drude model $\varepsilon(\omega)=1-\omega_p^2/[\omega(\omega-j\gamma)]$ (Au: $\omega_p$ = 1.37 × 10¹⁶ rad/s, γ = 4.05 × 10¹³ s⁻¹ [12]; the model reproduces σ_DC = 4.1 × 10⁷ S/m). Up to THz, ω ≪ γ, the conductivity is real and the classical skin depth holds (3.8 µm at 433 MHz). Above ≈ 10 THz, ω ≫ γ: electron inertia (kinetic inductance, $\omega L_k/R=\omega/\gamma$ = 30 at 1550 nm) dominates. The penetration depth saturates at $c/\omega_p$ ≈ 22 nm instead of shrinking as $1/\sqrt f$, and above the plasma frequency (λ ≈ 137 nm, UV) metals become transparent (script §3; real gold also has interband absorption below ≈ 600 nm). So antennas *do* work at optical frequencies: nano-dipoles, bow-ties and optical Yagi–Udas have been demonstrated [13]. But they are plasmonic resonators: the resonant length is a scaled "effective wavelength" well below λ/2, ohmic loss is large, and rectifying the output (optical rectennas) needs diodes that are fast enough at hundreds of THz, which is the hard part.

**Limits of the flat, infinite-interface model.**
- *Curvature*: a nose cone of radius ≫ λ is locally flat; at 433 MHz (λ = 69 cm) a 10 cm diameter
  cone is *not* — it is a dielectric perturbation in the antenna's near field. Transmission-loss
  numbers above are then only indicative; the dominant effect becomes **detuning** (resonance
  shift of a few % when a dielectric wall is within ~λ/2π, 5 cm at 915 MHz, of a monopole/dipole)
  and pattern change. Simulate the antenna with the wall (openEMS/NEC with dielectric support) or
  tune it in its installed state.
- *Roughness*: ground and sea are rough; specular reflection is reduced by the Rayleigh roughness
  factor exp(−2(2πσ_h sin ψ/λ)²) for rms height σ_h — at 433 MHz and 5° grazing, 1 m waves reduce
  specular reflection substantially (details in 09-propagation).
- *Finite size*: reflection from a plate is specular only if the plate spans several Fresnel zones.
- *Near field*: all of this assumes plane waves incident from far away.

## Design equations & rules of thumb

| Equation | When valid | Typical value |
|---|---|---|
| Γ = (η₂−η₁)/(η₂+η₁) | normal incidence | air→εr 4.7: −0.37 (13.7 %) |
| n₁ sin θ₁ = n₂ sin θ₂ | any plane interface | — |
| tan θ_B = n₂/n₁ | TM, lossless | εr 4.5: 64.8° |
| θ_c = asin(n₂/n₁) | n₁ > n₂ | εr 4.5→air: 28.1° |
| t_½λ = λ0/(2√(εr − sin²θ)) | solid radome | fibreglass 915 MHz: 75.6 mm |
| Thin wall OK if t < λ0/(53√εr) (εr≈4.7, |Γ|²<1 %) | normal incidence | 915 MHz: 2.8 mm |
| A-sandwich core ≈ λ0/(4√εr,core) | two thin skins | 5.8 GHz foam: 12.3 mm |
| 1 − |Γ|² ≈ 4R_s/η0 | metal, normal incidence | Cu 433 MHz: 5.8×10⁻⁵ |
| R_H, R_V → −1 as ψ → 0 | flat ground/sea | two-ray model |

## Worked examples

**1. Radome thickness for 915 MHz in fibreglass (εr = 4.7, tanδ = 0.02).**
Half-wave wall at normal incidence: t = 0.3276/(2√4.7) = 0.3276/4.336 = **75.6 mm**. At 45°
incidence: t = 0.3276/(2√(4.7 − 0.5)) = 79.9 mm. Neither is a practical nose cone. Thin-wall
alternative: a 2 mm G10/fibreglass wall gives IL = 0.037 dB at normal incidence, 0.065 dB (TE) /
0.018 dB (TM) at 45°; a 3 mm wall 0.07 dB (script). Conclusion: at 915 MHz any sensible fibreglass
nose cone is electrically transparent; design effort goes into the antenna's installed tuning, not the
wall.

**2. The same airframe with a 5.8 GHz video link or 24 GHz radar altimeter.** 2 mm fibreglass at
5.8 GHz: IL 0.8 dB normal, 1.5 dB (TE, 45°). At 24 GHz, 1–2 mm walls cost ~2 dB but a 3 mm wall is
near a half-wave resonance (λ_d/2 = 2.9 mm) and costs only 0.4 dB: at mm-wave, choose wall thickness
deliberately (script table 3b).

**3. Sea reflection for a 433 MHz recovery link.** A ground station on a beach receives a rocket on
its parachute at 2° elevation over the sea. From the script: |R_H| = 0.996, |R_V| = 0.45 (angle
−142°). A vertically polarized link sees a reflected ray ~7 dB weaker than the direct ray; a
horizontally polarized one sees an almost equal and opposite reflected ray and deep two-ray nulls.
Prefer V-pol (or CP) over water.

**4. Carbon-fibre electronics bay.** 433 MHz LoRa inside a 1 mm CFRP tube: −46 dB even if σ were
only 10³ S/m, and more likely −80 dB. With a 60 dB link margin (see
[Poynting example 2](poynting-vector-power-flow.md)) the link becomes marginal to impossible; move the
antenna into a fibreglass section or the nose cone.

## Practical notes
- Fibreglass (E-glass/epoxy, G10/FR-4 class) εr is typically 4.2–5.2 depending on glass/resin ratio;
  see [dielectrics](dielectrics-permittivity-loss-tangent.md). For thin walls the exact value hardly
  matters at UHF.
- Paint and fillers: carbon-black, conductive (EMI) and some primer paints are lossy/conductive, and a
  *continuous conductive* coat shields a fibreglass nose cone (sheet law above: 0.3 Ω/□ → −56 dB).
  Decorative metallic-flake paint is usually insulating at DC and nearly transparent at UHF, but check
  it: measure R_□ of a painted coupon, then test it with two antennas and a VNA or SDR (transmission
  with/without the coupon).
- Wet foam or moisture uptake raises εr and loss (water εr ≈ 80) — relevant for sandwich radomes.
- The plane-wave slab model is a quick screen; for an antenna ≲ λ/2π from the wall, simulate the
  installed antenna.

## Common mistakes & misconceptions
- **"Radome walls should be a quarter wavelength thick."** A single quarter-wave *solid* wall
  maximises reflection (the two surface reflections add). Quarter-wave spacing is used for the
  *core* of an A-sandwich or for an anti-reflection layer between two media; a solid wall should be
  thin or a half wavelength.
- **"Brewster angle eliminates ground reflection for all polarizations."** Only TM (vertical) has a
  Brewster (or pseudo-Brewster) minimum; horizontal polarization reflects strongly at all low angles.
- **"TE/TM" vs "horizontal/vertical".** Over flat ground TE = horizontal, TM = vertical. In waveguides
  "TE/TM" means something related but different (field component along the guide axis).
- **Sign of r_TM**: different books use opposite reference directions; don't conclude a formula is
  wrong from a sign at normal incidence.
- **"Carbon fibre is a dielectric like fibreglass."** It is a (poor) conductor; it shields.
- **"A reflecting metal plate absorbs nothing."** It absorbs 4R_s/η0 of the incident power — tiny
  per bounce, but it sets the Q of cavities and the loss of reflectors at mm-wave.
- **"A metal film thinner than the skin depth lets RF through."** The skin depth governs *absorption*; a thin film *reflects* via its sheet resistance. 40 nm of aluminium is 1 % of δ at 433 MHz and still blocks ≈ 48 dB (T = 2/(2 + η0/R_□)). A space blanket or a crisp packet shields well, and the leaks are at its seams.
- **"Any metallic paint blocks radio" / "paint never matters".** It depends on whether the coat is electrically continuous. EMI paints at 0.02–1 Ω/□ block 45–80 dB; decorative flake paint (isolated flakes, ≳ 10⁶ Ω/□) is ≈ transparent at UHF. Measure R_□.
- **"Antennas stop working at optical frequencies" / "an optical antenna is just a tiny dipole."** Both are wrong. Metals at optical frequencies are inductive (Drude, ωL_k/R ≈ 30 at 1550 nm) with a fixed ≈ 22 nm penetration depth, so nano-antennas work as *plasmonic* resonators with a shortened effective wavelength and high loss. They do exist and radiate; efficient rectification of their output is the unsolved part.
- **Using infinite-slab results for a small curved nose cone at UHF.** At 433 MHz a 10 cm cone is a
  near-field object; detuning dominates.

## How to simulate / verify
- `python3 tools/verify/s4_thin_film.py` (output `s4_thin_film_output.txt`) — sheet law vs exact conducting slab for Al/Cu from 10 nm to 16 µm at 433 MHz and 2.45 GHz; R_□ → transmission table; Drude Au/Ag σ, penetration depth and kinetic ratio from 433 MHz to 600 nm.
- `python3 tools/verify/em_fresnel_radome.py` — Fresnel TE/TM with lossy media, energy conservation,
  Brewster/critical angles, evanescent decay; transfer-matrix slabs (half-wave, thin-wall table,
  A-sandwich, CFRP); sea and ground R_H/R_V vs grazing angle with pseudo-Brewster; metal reflection
  loss vs 4R_s/η0.
- openEMS: plane-wave excitation on a periodic (PBC) unit cell containing the slab gives |S21| of the
  wall; or model the installed antenna inside the nose cone and compare S11 with/without the cone.
- Bench: two antennas facing each other at > 2D²/λ with the wall coupon between them, measure
  S21 with a NanoVNA / SDR; normalise to no-coupon. For UHF the coupon must be ≫ λ wide to avoid
  diffraction round it — prefer testing the actual nose cone around the installed antenna.

## Open questions / gaps
- The "medium ground" values (εr 15, σ 5 mS/m) are illustrative; ITU-R P.527-6 gives a soil model
  from texture and moisture that 09-propagation should implement for UHF.
- CFRP conductivity is from secondary search results (TLM modelling papers); ply-by-ply anisotropic
  transmission for real layups is not computed here.
- Measured detuning of 433/915 MHz antennas inside fibreglass nose cones: to be gathered by
  08-antennas (antennas-on-rockets) — ideally from the Space Bar team's own measurements.

## Sources
1. D. K. Cheng, *Field and Wave Electromagnetics*, 2nd ed., 1989, §7-4 (boundary conditions), §8-7
   to §8-10 (normal and oblique incidence, Brewster angle, total reflection). (textbook)
2. D. J. Griffiths, *Introduction to Electrodynamics*, 4th ed., §7.3.6 (boundary conditions), §9.3
   (reflection and transmission at normal and oblique incidence; Fresnel equations). (textbook)
3. C. A. Balanis, *Advanced Engineering Electromagnetics*, 2nd ed., 2012, ch. 5 (reflection and
   transmission; multilayer; lossy media; pseudo-Brewster). (textbook)
4. ITU-R P.527-6 (09/2021), sea-water double-Debye model (implemented in
   `tools/verify/em_dielectrics.py`; ε ≈ 71.6 − j200.6 at 433 MHz, 20 °C, 35 g/kg). (standard)
5. S. J. Orfanidis, *Electromagnetic Waves and Antennas*, Rutgers (free online), ch. 5–8 (reflection
   and transmission, multilayer structures and transfer matrices, oblique incidence, multilayer film
   applications). (textbook, free; site 403 on 2026-09-27, cited from knowledge; chapter numbers checked
   against the 2016 table of contents by W5-S18b, 2026-10-13: 5 Reflection and Transmission, 6 Multilayer
   Structures, 7 Oblique Incidence, 8 Multilayer Film Applications)
6. D. J. Kozakoff, *Analysis of Radome-Enclosed Antennas*, 2nd ed., Artech House 2010 (half-wave,
   thin-wall and A-sandwich radome walls). (textbook; cited from knowledge)
7. "Modeling curved carbon fiber composite (CFC) structures in the transmission-line modeling (TLM)
   method," arXiv:1502.01227 (CFC conductivity values used in EM modelling). (preprint; secondary)
8. Search-result summaries of CFRP conductivity/shielding studies (longitudinal ~4×10⁴ S/m DC falling to
   ~3×10³ S/m at 12 GHz; transverse ~10 S/m; longitudinal/transverse ratio ~930), e.g. "Electromagnetic
   shielding of oriented carbon fiber composite materials" (ResearchGate 241633450). (peer-reviewed
   papers seen via abstract/figure summaries only — medium confidence)
9. ITU-R P.368-10 (2022), sea water εr = 70, σ = 5 S/m (used in cross-checks). (standard)
10. D. M. Pozar, *Microwave Engineering*, 4th ed., §1.7–1.8 (plane-wave reflection from a media
    interface; oblique incidence; Γ sign conventions). (textbook)
11. ITU-R P.2109-2 (2023), *Prediction of building entry loss* — "traditional" vs "thermally efficient" (metallised-glass, foil-backed insulation) building classes. (standard; used qualitatively)
12. M. A. Ordal et al., "Optical properties of the metals Al, Co, Cu, Au, Fe, Pb, Ni, Pd, Pt, Ag, Ti, and W in the infrared and far infrared," *Appl. Opt.* 22(7), 1099–1120 (1983), Drude fits (Au ω_p 7.28 × 10⁴ cm⁻¹, ω_τ 215 cm⁻¹; Ag 7.25 × 10⁴, 145 cm⁻¹). doi:10.1364/AO.22.001099 (peer-reviewed; parameters recalled and checked by reproducing σ_DC of Au/Ag within 4 % in s4_thin_film.py; a 2015 arXiv paper attributes a ≈ 219 cm⁻¹ damping to "Ordal" for silver, which matches Ordal's *gold* value — treat Ag γ as ±50 %)
13. L. Novotny, "Effective wavelength scaling for optical antennas," *Phys. Rev. Lett.* 98, 266802 (2007); L. Novotny and N. van Hulst, "Antennas for light," *Nature Photonics* 5, 83–90 (2011); A. G. Curto et al., "Unidirectional emission of a quantum dot coupled to a nanoantenna," *Science* 329, 930–933 (2010) (optical Yagi–Uda). (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
