---
title: Radar cross section (RCS) — definition, canonical shapes, corner-reflector calibration targets, real targets, Swerling statistics
domain: 11-radar
slug: radar-cross-section
tags: [rcs, dbsm, sphere, mie, rayleigh-scattering, physical-optics, flat-plate, cylinder, dihedral, trihedral, corner-reflector, calibration-target, drone-rcs, pedestrian-rcs, bird-rcs, rocket-rcs, swerling, glint, stealth, radar-absorbing-material]
prerequisites:
  - radar-range-equation.md
  - ../02-electromagnetics/boundary-conditions-reflection-refraction.md
  - ../02-electromagnetics/wave-equation-plane-waves-polarization.md
related:
  - detection-theory-cfar.md
  - diy-radar-hardware.md
  - clutter-and-mti.md
  - cw-and-doppler-radar.md
  - ../08-antennas/antenna-fundamentals.md
  - ../00-math-foundations/special-functions-bessel-sinc.md
  - ../09-propagation-link-budget/atmospheric-rain-attenuation.md
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# Radar cross section (RCS)

## Questions this page answers
- What exactly is radar cross section, and why is it not the physical area of the target?
- What is a dBsm?
- Why does a small metal sphere reflect so weakly at low frequency, and why does RCS oscillate near one wavelength?
- What are the RCS formulas for a sphere, flat plate, cylinder, dihedral and trihedral corner reflector?
- How do I build a corner-reflector calibration target for my 24/60/77 GHz radar, and how big should it be?
- What RCS should I assume for a person, a drone, a car, a bird, or a hobby rocket?
- Why does the echo from a drone or a car jump around by 10–20 dB when it turns slightly?
- Which Swerling model fits which target?
- How do stealth shaping and radar-absorbing materials reduce RCS?
- How do I measure the RCS of my own target (e.g. a rocket airframe)?

## TL;DR
- **Definition:** $\sigma = \lim_{R\to\infty}4\pi R^2|E_s|^2/|E_i|^2$ — the area of an imaginary isotropic scatterer returning the same echo. Units m²; **dBsm** $= 10\log_{10}(\sigma/1\,\mathrm{m^2})$. It depends on frequency, aspect, polarisation and (for bistatic) on both angles.
- **Three regimes** (verified with an exact Mie series for a metal sphere): Rayleigh ($ka \ll 1$) $\sigma = 9\pi a^2(ka)^4$ ∝ $f^4$; resonance near $ka \approx 1$ (peak **3.65 πa²** at $ka$ = 1.03, circumference ≈ λ); optical ($ka \gg 1$) $\sigma \to \pi a^2$, independent of frequency.
- **Flat-phase reflectors:** $\sigma = 4\pi A_{eff}^2/\lambda^2$. Flat plate at normal incidence $4\pi A^2/\lambda^2$ (but only within ≈ ±0.44 λ/b of normal — ±1° for 10 cm at 77 GHz); cylinder broadside $2\pi aL^2/\lambda$; dihedral $8\pi a^2b^2/\lambda^2$; **triangular trihedral $4\pi a^4/(3\lambda^2)$**; square trihedral $12\pi a^4/\lambda^2$ (effective areas confirmed by ray tracing to < 1 %).
- **Calibration target:** a 10 cm-edge triangular trihedral gives **−2.9 dBsm at 10.5 GHz, 4.3 at 24 GHz, 12.2 at 60 GHz, 14.4 dBsm at 77 GHz**, and stays within ~2 dB over ±20° of its axis — far more forgiving than a plate. Plate-angle errors must be ≪ λ/a (2.2° at 77 GHz for 10 cm).
- **Real targets (measured/sourced):** person −16.6 to 0 dBsm vs aspect at 77 GHz, averages −7.7 to −3 dBsm at 24/77 GHz [8]; small–medium drones −8 to −19 dBsm mean at 24 GHz [9], −20 to −5 dBsm at X-band [10]; bird ~10–100 cm² (−30 to −20 dBsm; a 100 g water sphere computes to 12–25 cm² from 2.4 to 77 GHz); car ~10–20 dBsm at microwave frequencies, strongly aspect-dependent [1], [11]; small hobby rocket nose/tail-on: *estimated* −30 to −10 dBsm (no measurements found), broadside specular flashes of roughly +10 to +20 dBsm (98 mm × 2 m tube, 3–24 GHz) lasting only fractions of a degree.
- **Complex targets fluctuate:** many comparable scatterers add with random phases → RCS is exponentially distributed (std = mean; Swerling 1/2). One dominant scatterer + clutter of small ones → std ≈ 0.7–0.87 × mean (Swerling 3/4-like). Budget the fluctuation loss (8 dB at Pd 0.9) from [detection theory](detection-theory-cfar.md).

## Intuition (no math)
The radar equation pretends the target is a small isotropic "re-radiator" that captures a certain area's worth of incident power and throws it back equally in all directions. RCS is that pretend area. A real target does not scatter isotropically: a flat mirror sends almost everything back in one tight beam, so when it faces you squarely its RCS is enormous — far larger than its physical area — and a few degrees off it is almost invisible. A sphere scatters roughly equally in all directions, so its RCS equals its shadow area πa² (at high frequency).

Corner reflectors are clever mirrors: three mutually perpendicular faces bounce any ray entering the corner straight back towards the source (the same trick as a bicycle reflector or the retroreflectors left on the Moon). They behave like a big flat plate that is always facing you — ideal as calibration targets.

Size relative to wavelength matters. An object much smaller than λ cannot form a directed echo: it just gets polarised by the field and radiates like a tiny dipole, very weakly (∝ $f^4$ — the same law that makes the sky blue). Near one wavelength in circumference, waves creeping around the object interfere with the front-face reflection and the RCS oscillates. Much larger than λ, ray optics takes over.

Real targets — drones, people, cars, rockets — are collections of plates, edges, cylinders, cavities and wires. Their echoes add with phases that change every time the target rotates by a fraction of a wavelength's worth of path difference, so the total "twinkles": this is target fluctuation (glint/scintillation).

## The math

### Level 1 — definitions and canonical formulas
**Definition (monostatic).** With incident field magnitude $|E_i|$ at the target and scattered field $|E_s|$ at range $R$:
$$\sigma = \lim_{R\to\infty} 4\pi R^2\frac{|E_s|^2}{|E_i|^2}\quad[\mathrm{m^2}],\qquad \sigma_{dBsm} = 10\log_{10}\frac{\sigma}{1\ \mathrm{m^2}}.$$
The limit removes near-field effects; in practice the far-field condition is $R > 2D^2/\lambda$ where $D$ is the target's largest dimension. *Bistatic* RCS $\sigma_b(\theta_i,\phi_i;\theta_s,\phi_s)$ is defined the same way with separate incidence and observation directions. Polarisation: σ is really a 2×2 scattering matrix $[S_{HH}, S_{HV}; S_{VH}, S_{VV}]$; the "RCS" usually quoted is $|S_{pp}|^2$ for the radar's own polarisation.

**Canonical results** ($k = 2\pi/\lambda$, all perfectly conducting):

| Shape | Peak monostatic σ | Condition / angular width |
|---|---|---|
| Sphere, radius $a$ | $9\pi a^2(ka)^4$ (Rayleigh) … $\pi a^2$ (optical) | aspect-independent |
| Flat plate, area $A$ (side $b$) | $4\pi A^2/\lambda^2$ | normal incidence; −3 dB (two-way) at $\sin\theta \approx 0.443\lambda/b$ |
| Circular disk, radius $r$ | $4\pi^3 r^4/\lambda^2$ | normal incidence |
| Cylinder, radius $a$, length $L$ | $2\pi aL^2/\lambda$ | broadside; width ~ λ/(2L) in the plane containing the axis |
| Dihedral (fold length $a$, plate width $b$) | $8\pi a^2b^2/\lambda^2$ | wide in the plane ⟂ fold, narrow along it |
| Triangular trihedral (edge $a$) | $4\pi a^4/(3\lambda^2)$ | ±20° for < ~2 dB loss |
| Square trihedral (edge $a$) | $12\pi a^4/\lambda^2$ | narrower than triangular |
| Straight wire / dipole at resonance | ≈ $0.86\lambda^2$ (half-wave, broadside, co-polar) | why chaff works |

### Level 2 — derivations

**Physical optics (PO).** On the illuminated side of a smooth, large conductor, the induced surface current is approximated by twice the tangential incident magnetic field, $\mathbf J_s \approx 2\hat n\times\mathbf H_i$, and zero in the shadow. Radiating this current back to the source (monostatic) gives
$$\sigma = \frac{4\pi}{\lambda^2}\left|\int_{S_{lit}}(\hat n\cdot\hat k_i)\,e^{\,j2\mathbf k\cdot\mathbf r}\,dS\right|^2 .$$
The factor $e^{j2\mathbf k\cdot\mathbf r}$ is the two-way phase to each surface patch. Every flat-phase formula above follows from this integral:
- *Flat plate at normal incidence:* the phase is constant, the integral is $A$: $\sigma = 4\pi A^2/\lambda^2$. Tilted by θ in one principal plane (plate side $b$): the phase varies linearly across the plate, giving $\sigma(\theta) = \frac{4\pi A^2}{\lambda^2}\cos^2\theta\,\mathrm{sinc}^2\!\left(\frac{2b\sin\theta}{\lambda}\right)$ (numerical PO integral matches to 10⁻⁴). A 10 cm plate at 77 GHz: 19.2 dBsm peak, −3 dB at 0.99° — a mirror that must be aimed to a degree.
- *Cylinder broadside:* $I = La\int_{-\pi/2}^{\pi/2}\cos\phi\,e^{j2ka\cos\phi}d\phi$. For $ka\gg1$ stationary phase at φ = 0 gives $|I|^2 \approx L^2a^2\pi/(ka)$, so $\sigma = 2\pi aL^2/\lambda$ (numerical PO within 0.4 %). A 100 mm × 1 m tube at 24 GHz: 14.0 dBsm broadside.
- *Sphere:* the PO integral over the lit hemisphere tends to $\pi a^2$ for $ka\gg1$ (verified), which is the optical limit.
- *Corner reflectors:* each ray that makes the full two- or three-bounce path returns parallel to itself with a path length that is the same for all rays (a property of orthogonal mirrors). The reflector therefore acts like a flat plate whose area is the **effective area** $A_{eff}$ — the projected area of the rays that complete all bounces — so $\sigma = 4\pi A_{eff}^2/\lambda^2$.
  - Triangular trihedral, along its symmetry axis: the aperture is an equilateral triangle of area $(\sqrt3/2)a^2$; the fully retro-reflected part is a hexagon of 2/3 of it: $A_{eff} = a^2/\sqrt3$ ⇒ $\sigma = 4\pi a^4/(3\lambda^2)$.
  - Square trihedral: $A_{eff} = \sqrt3\,a^2$ ⇒ $\sigma = 12\pi a^4/\lambda^2$ (9 times the triangular one, but narrower acceptance and heavier).
  - Dihedral at symmetric incidence: each face projects $ab/\sqrt2$, all rays double-bounce: $A_{eff} = \sqrt2\,ab$ ⇒ $\sigma = 8\pi a^2b^2/\lambda^2$.
  Monte-Carlo ray tracing in `tools/verify/radar_rcs.py` reproduces all three effective areas to < 1 % and gives the triangular trihedral's falloff: −0.7 dB at 10°, −2.1 dB at 20°, −5.5 dB at 30° off axis (PO/GO estimate).

**Sphere — exact (Mie) solution.** Expanding the incident plane wave in vector spherical harmonics and matching boundary conditions gives the backscatter efficiency
$$\frac{\sigma}{\pi a^2} = \frac{1}{(ka)^2}\left|\sum_{n=1}^{\infty}(-1)^n(2n+1)(a_n - b_n)\right|^2,$$
with $a_n, b_n$ ratios of Riccati–Bessel functions of $ka$ (and of $mka$ for a dielectric of refractive index $m$) [2], [3]. For a PEC sphere the script shows: $\sigma/\pi a^2 = 9(ka)^4$ for $ka$ = 0.05–0.1 (Rayleigh), a first peak of 3.655 at $ka$ = 1.028, and convergence to 1 (0.996 at $ka$ = 50). For a small *dielectric* sphere (raindrop, insect, bird at long wavelength) the Rayleigh limit is
$$\sigma = \frac{\pi^5 D^6}{\lambda^4}|K|^2,\qquad K = \frac{m^2-1}{m^2+2},$$
the basis of weather-radar reflectivity (see [clutter](clutter-and-mti.md)); $|K|^2 \approx 0.93$ for water at microwave frequencies.

**Birds as water spheres.** Using the double-Debye liquid-water permittivity of ITU-R P.840 (25 °C: 77.2 − j8.9 at 2.4 GHz, 62.8 − j29.9 at 10 GHz, 34.0 − j35.7 at 24 GHz, 9.6 − j17.4 at 77 GHz) a 100 g "bird" (a 2.88 cm-radius water sphere, πa² = 26 cm²) gives 22.8, 25.0, 18.8, 14.8 and 12.1 cm² at 2.4, 5.6, 10, 24 and 77 GHz — the RCS drops below πa² at mm-wave because lossy water reflects less (|Γ|² falls). Vaughn's review [4] warns that birds are better modelled as prolate spheroids (length/width 3–10) and that with horizontal polarisation the peak (broadside) RCS resembles a resonant half-wave dipole — i.e. larger and much more aspect-dependent than the sphere estimate.

### Level 3 — real targets, statistics, limits

**Scattering mechanisms of a complex target** (roughly in order of strength at microwave frequencies): specular reflection from flat or singly-curved surfaces facing the radar; multiple-bounce corners (dihedral between a wing and a fuselage, a car's wheel arch); cavities and ducts (engine inlets, a rocket nozzle); edge diffraction and tips (weak, but they dominate when nothing faces the radar); travelling and creeping waves on long, thin or smooth bodies (important nose-on for missiles and rockets); and resonances of wires, antennas, propellers. Methods: PO and geometrical/physical theory of diffraction for large bodies, full-wave solvers (MoM, FDTD, FEM — see 16-simulation-tools) for resonant ones [2], [5].

**Why targets fluctuate.** For $M$ scatterers with amplitudes $a_i$ at ranges $r_i$, $\sigma(\theta) = \left|\sum_i\sqrt{\sigma_i}\,e^{-j2kr_i(\theta)}\right|^2$. A rotation by δθ changes the path difference between two scatterers separated by $d$ by $2d\,\delta\theta$; one full cycle of fluctuation occurs for $\delta\theta \approx \lambda/(2d)$. A 30 cm drone at 77 GHz decorrelates every **0.4°** of rotation (λ/2d = 3.9 mm/0.6 m = 6.5 mrad). With many comparable scatterers the central limit theorem makes the complex sum Gaussian, so σ is exponential (Swerling 1/2; simulated std/mean = 0.98, P(σ < 0.1 σ̄) = 0.094 vs theory 0.095). One dominant scatterer plus many small ones gives a Rician amplitude (simulated std/mean = 0.86 for equal powers, exact Rice 0.866); Swerling 3/4 (χ² with 4 dof, std/mean 0.707) is the conventional stand-in [6], [7].

**Which Swerling model?** Scan-to-scan (1, 3) if the target does not rotate by ≳ λ/(2d) within one coherent dwell and the frequency is fixed; pulse-to-pulse (2, 4) if the radar hops frequency by more than $c/(2d)$ between pulses (the decorrelation frequency step: 500 MHz for a 30 cm target) or the target tumbles/spins fast (propellers). An FMCW chirp sweeping 1–4 GHz over a 30 cm drone decorrelates *within* the chirp — the range profile then resolves individual scatterers instead (range resolution 3.75–15 cm), which is really a change of regime from "point target" to "extended target".

**Frequency dependence of common targets.** People: nearly flat in dBsm from 24 to 77 GHz on average (JRC measurements [8]), aspect variation ±8 dB. Vehicles: log-normal statistics, mean growing slowly (∝ log f) from 10 to 79 GHz [11]. Drones: dominated by motors, battery and electronics; plastic bodies and propellers contribute more at mm-wave (and produce the micro-Doppler lines used for classification; see [CW and Doppler](cw-and-doppler-radar.md)).

**Hobby rockets — an estimate (no published measurements found).** Consider a 98 mm-diameter, 2 m-long rocket.
- *Airframe material decides everything.* Carbon fibre is conductive — treat as metal. Fibreglass, cardboard and plastic are partly transparent at microwave frequencies; the echo then comes from internal metal (motor case, avionics bay threaded rods, batteries, bulkhead hardware), which is smaller and cluttered.
- *Broadside (metal or CF airframe):* $2\pi aL^2/\lambda$ = +10.9 dBsm at 3 GHz, +20.0 dBsm at 24 GHz — but only within a few λ/(2L) of perpendicular (±0.2° at 24 GHz), so it appears as a brief flash as the rocket pitches.
- *Tail-on (the view from a ground radar after launch):* motor aft closure and nozzle (a cone/cavity of ~40–50 mm diameter), four fins seen edge-on, fin-can hardware. If a 50 mm flat disk faced the radar squarely it would give −23.1 dBsm at 3 GHz and −5.0 dBsm at 24 GHz ($4\pi^3r^4/\lambda^2$), but nozzles are conical and fins edge-on, so values in the −30 to −10 dBsm range should be assumed, with large fluctuations.
- *Nose-on:* ogive tip plus creeping/travelling waves — typically very small (≪ −20 dBsm).
- *Plume:* an aluminised solid-propellant exhaust contains alumina particles and free electrons that can scatter (and attenuate) microwaves; for small motors the effect is not quantified here.
- **Practical fix for tracking:** put a known reflector (e.g. a small trihedral or a Luneburg-lens reflector) inside a radar-transparent fibreglass nose cone — then design the tracking radar around a known σ.

**RCS reduction (for context and for test-range clutter control).**
- *Shaping:* tilt flat surfaces away from threat directions so that specular flashes go elsewhere; align edges into a few directions (a stealth aircraft's RCS is concentrated in a few narrow "spikes"). Shaping moves energy in angle; it cannot remove it.
- *Radar-absorbing materials (RAM):* Salisbury screen (377 Ω resistive sheet λ/4 in front of metal — narrowband), Jaumann multilayer screens (wider band), magnetically loaded elastomers (ferrite/carbonyl-iron paints, thin at low GHz), carbon-loaded foam pyramids (anechoic chambers). See [magnetic materials](../02-electromagnetics/magnetic-materials-permeability.md) and [boundary conditions](../02-electromagnetics/boundary-conditions-reflection-refraction.md) for the physics.
- *Cancellation:* passive (a second scatterer out of phase — narrowband) or active (re-transmitted anti-echo — impractical for hobbyists).

## Design equations & rules of thumb

| Equation / rule | When valid | Typical numbers |
|---|---|---|
| $\sigma_{dBsm} = 10\log_{10}\sigma$ | — | 1 m² = 0 dBsm; 0.01 m² = −20 dBsm |
| Sphere optical $\pi a^2$; Rayleigh $9\pi a^2(ka)^4$ | $ka > 10$; $ka < 0.5$ | 15 cm dia ball: −17.5 dBsm (optical) |
| $\sigma = 4\pi A_{eff}^2/\lambda^2$ | flat-phase reflectors, $A \gg \lambda^2$ | scales with $f^2$ |
| Triangular trihedral $4\pi a^4/(3\lambda^2)$ | edge $a \gtrsim 10\lambda$ | 10 cm: 4.3 dBsm @24 GHz, 14.4 @77 GHz |
| Plate lobe −3 dB: $\sin\theta = 0.443\lambda/b$ | PO | 10 cm @77 GHz: ±1.0° |
| Decorrelation angle $\approx\lambda/(2d)$ | target extent $d$ | 30 cm drone @77 GHz: 0.37° |
| Decorrelation frequency step $\approx c/(2d)$ | target range extent $d$ | 30 cm → 500 MHz |
| Far-field distance $2D^2/\lambda$ | measurement of σ | 30 cm reflector @77 GHz: 46 m (!) |
| Substitution: $\sigma_t = \sigma_{ref}P_t/P_{ref}$ | same range, same setup | ±1 dB with care |

**Corner-reflector design table** (triangular trihedral, $\sigma = 4\pi a^4/3\lambda^2$, computed):

| Edge $a$ | 2.4 GHz | 10.525 GHz | 24.125 GHz | 60 GHz | 77 GHz |
|---|---|---|---|---|---|
| 5 cm | −27.8 | −14.9 | −7.7 | 0.2 | 2.4 dBsm |
| 10 cm | −15.7 | −2.9 | 4.3 | 12.2 | 14.4 dBsm |
| 20 cm | −3.7 | 9.2 | 16.4 | 24.3 | 26.5 dBsm |
| 30 cm | 3.4 | 16.2 | 23.4 | 31.3 | 33.5 dBsm |

(At 2.4 GHz a 5 cm reflector is only 0.4λ — below the validity of the optical formula; use a ≥ 30 cm reflector.)

## Worked examples

**Example 1 — Calibration target for a 77 GHz FMCW board.** You want a target 20 dB above a person (−5 dBsm) → 15 dBsm. From the table, a triangular trihedral with $a$ ≈ 10.5 cm gives ≈ 15 dBsm. Far field: $D$ is the aperture size (~0.15 m) → $2D^2/\lambda$ = 11.6 m; at 5 m you are in the near field of the reflector and the echo is lower than 15 dBsm (partially focused wavefront). Check: at 12 m range, with the radar of the [range-equation example B](radar-range-equation.md) (SNR 15 dB at 121 m for this reflector), the SNR is $15 + 40\log_{10}(121/12) = 55$ dB — ample for calibrating angle and range offsets. Construction: 1.5 mm aluminium or double-sided FR-4 copper-clad (copper thickness ≫ skin depth: 0.24 µm at 77 GHz), faces bonded with a 3-D-printed square jig; keep inter-plate errors ≪ λ/a = 2.2° (aim < 0.3°). Mount on a wooden or plastic pole, tilt so the symmetry axis points at the radar (elevation ≈ 35° up from the base plane for a trihedral resting on one face).

**Example 2 — 24 GHz module with a swinging reflector.** A CW Doppler module (HB100 at 10.525 GHz or CDM324 at 24.125 GHz) sees only moving targets. A 10 cm trihedral (−2.9 dBsm at 10.5 GHz, 4.3 dBsm at 24 GHz) swung on a 1 m pendulum gives a known σ with Doppler up to $2v_{max}/\lambda$ — at 1 m/s, 70 Hz (10.5 GHz) or 161 Hz (24 GHz) — a perfect bench test for the audio amplifier chain (see [CW and Doppler](cw-and-doppler-radar.md)).

**Example 3 — Is a drone visible to a 77 GHz radar at 30 m?** Take a mean of −15 dBsm (the measured −8 to −19 dBsm span at 24 GHz [9]; comparable at 77 GHz). The [range-equation example](radar-range-equation.md) gives 22.3 m per virtual channel at SNR 15 dB. At 30 m the mean SNR is 15 − 40 log(30/22.3) = 9.8 dB. With Swerling 1 fluctuation, single-look Pd at Pfa 10⁻⁶ is only $P_{FA}^{1/(1+\bar\chi)} = 10^{-6/(1+9.6)} \approx 0.27$. Coherent combination of the 12 virtual channels adds 10.8 dB (SNR 20.6 dB, Pd ≈ 0.89). This is why drone radars use arrays and multiple looks.

**Example 4 — Rocket tail-on RCS bound.** 54 mm motor, nozzle exit 30 mm; model the aft closure face as a 54 mm flat disk (worst case, facing the radar): $4\pi^3r^4/\lambda^2$ at 24.125 GHz ($r$ = 27 mm) = 4π³ × 5.3 × 10⁻⁷/1.544 × 10⁻⁴ = 0.43 m² ≈ −3.7 dBsm — but only within ±0.44λ/D ≈ ±5.8° of the axis, and a real conical nozzle returns far less. Use −20 dBsm for a conservative budget and verify by measurement (below).

## Practical notes
- **Measuring RCS by substitution.** Put the unknown target and a reference trihedral at the same range in the same beam spot (separately), record echo powers after the same processing, subtract a background (empty-scene) measurement coherently, and use $\sigma_t = \sigma_{ref}P_t/P_{ref}$. Rotate the target on a turntable (a cheap stepper-motor turntable works) to get σ(θ); report median and percentiles, not just the peak.
- **Background and multipath.** Outdoors, the ground bounce can change the apparent σ by ±6 dB (two-way propagation factor); raise the target and radar, or use a range gate/FFT bin to separate the target from ground clutter.
- **Polarisation.** Trihedrals preserve linear polarisation (odd bounces); dihedrals rotate it depending on their fold orientation (even bounces: a 45°-tilted dihedral converts H to V — useful as a polarimetric calibration target, and a way to hide a reflector from co-polar radar).
- **Near-field of big reflectors.** A 30 cm trihedral at 77 GHz needs ~46 m to be in its far field; closer, the effective σ is lower. Size the reflector to the range you can use.
- **Chaff-like wires.** A half-wave wire has σ ≈ 0.86λ² broadside: at 24 GHz a 6 mm wire is ~1.3 cm² — tiny. At 433 MHz (λ = 0.69 m) it would be 0.4 m², which is why hobby antennas and wiring can dominate the RCS at low frequencies.
- **Composite airframes:** measure! A fibreglass rocket with an internal all-thread and a LiPo can look very different from the same rocket in carbon fibre.

## Common mistakes & misconceptions
- **"RCS = physical cross-sectional area."** Only for a large conducting sphere. A 10 cm flat plate at 77 GHz facing the radar is 19 dBsm (83 m²), 8 300 times its area; the same plate 5° off-normal is below 0 dBsm.
- **"Higher frequency always means bigger RCS."** True for flat-phase reflectors (∝ $f^2$), false for spheres in the optical region (constant), and the reverse in the Rayleigh region ($f^4$ growth up to resonance).
- **Quoting a single RCS for a complex target.** Always give aspect, frequency, polarisation and statistics (mean/median); the same car can be 0 dBsm or 30 dBsm.
- **Using a flat plate as a calibration target.** Its ±1° acceptance at mm-wave makes alignment hopeless; use a trihedral.
- **Forgetting reflector far field.** Calibrating with a large reflector too close under-reads σ.
- **Assuming plastics are invisible.** Low-loss plastics have small but non-zero reflectivity (ε_r ≈ 2.5–4.5), and thick radomes can produce multiple reflections — see [boundary conditions / radomes](../02-electromagnetics/boundary-conditions-reflection-refraction.md).

## How to simulate / verify
- `tools/verify/radar_rcs.py` (~6 s, **ALL PASS**): Mie series (PEC and water), Rayleigh limits, PO integrals (plate pattern, cylinder, sphere), Monte-Carlo ray tracing of trihedral/dihedral effective areas and trihedral angular falloff, many-scatterer statistics, reflector design table.
- For real geometries use a full-wave or asymptotic solver: openEMS (FDTD, free) can compute monostatic RCS of objects a few λ in size; for electrically large targets PO/SBR (shooting-and-bouncing-ray) codes are used — see 16-simulation-tools (planned). A quick PO code for faceted CAD (STL) models is a good weekend project using the PO integral above.
- Cross-check any simulation with a sphere (Mie is exact) before trusting it on a drone model.

## Open questions / gaps
- No measured RCS of hobby-scale rockets (fibreglass/CF, 54–98 mm) was found; values here are engineering estimates. A turntable measurement at 24 and 77 GHz would fill this gap.
- Vehicle RCS numbers at 77/79 GHz were taken from textbook-level ranges and a log-normal characterisation [11], not from a specific measured table.
- Skolnik's classic table of typical RCS values [1] was used from memory of the textbook (not re-checked page-by-page); treat those rows as approximate (medium confidence).
- Rocket-plume RCS/attenuation for amateur APCP motors is not quantified.
- The trihedral angular falloff was computed with geometric optics (effective area), not full PO/diffraction.

## Sources
1. M. I. Skolnik, *Introduction to Radar Systems*, 3rd ed., McGraw-Hill, 2001, ch. 2 (RCS is part of the radar-equation chapter per the D4 chapter map; the section number §2.7 is not verified) — RCS definition, sphere regimes, table of typical microwave RCS values (e.g. automobile ~100 m², man ~1 m², bird ~0.01 m², insect ~10⁻⁵ m²) (values used approximately). (textbook)
2. E. F. Knott, J. F. Shaeffer, M. T. Tuley, *Radar Cross Section*, 2nd ed., Artech House, 1993 (SciTech reprint 2004) — PO integral, canonical shapes, corner reflectors, RAM, measurement. (textbook)
3. C. F. Bohren, D. R. Huffman, *Absorption and Scattering of Light by Small Particles*, Wiley, 1983, ch. 4 — Mie coefficients $a_n, b_n$ (implemented in the script). (textbook)
4. C. R. Vaughn, "Birds and insects as radar targets: A review," *Proc. IEEE*, vol. 73, no. 2, pp. 205–227, Feb. 1985 — prolate-spheroid and half-wave-dipole models better than water spheres. (peer-reviewed; abstract)
5. C. A. Balanis, *Advanced Engineering Electromagnetics*, 2nd ed., Wiley, 2012, ch. 11–13 — sphere/cylinder scattering, PO, GTD. (textbook)
6. P. Swerling, "Probability of detection for fluctuating targets," *IRE Trans. IT*, vol. 6, pp. 269–308, 1960. (peer-reviewed)
7. M. A. Richards, *Fundamentals of Radar Signal Processing*, 2nd ed., 2014, ch. 2 & 7 — RCS statistics, decorrelation angle/frequency. (textbook)
8. EC JRC / EMSL, "Radar cross section measurements of pedestrian dummies and humans in the 24/77 GHz frequency bands," 2013 (JRC78619): −16.6 to 0 dBsm vs azimuth at 77 GHz; averages −7.7 to −3.0 dBsm; 24 and 77 GHz averages close. https://publications.jrc.ec.europa.eu/repository/handle/JRC78619 (report; abstract)
9. R. Nakamura, K. Suzuki, H. Hadama, "RCS measurements of various drones at 24 GHz," *IEICE Comm. Express*, vol. 9, no. 7, 2020: mean −8.1 to −19.1 dBsm (Phantom 3, Bebop, 3DR Solo, Mavic Pro, Matrice 600; HH/VV). https://www.jstage.jst.go.jp/article/comex/9/7/9_2020XBL0018/_article (peer-reviewed letter; abstract)
10. Search-result summaries of X-band drone RCS studies (e.g. A. Semkin et al.; Quevedo et al., "Drone detection and RCS measurements with RAD-DAR," *IET RSN* 2019): typical −15 to −5 dBsm at X-band; Phantom-class 0.01–0.35 m² depending on propellers/polarisation/angle. (peer-reviewed, secondary access — medium confidence)
11. "Measurement results of vehicular RCS characteristics for 79 GHz millimeter band," IEEE conf. 2017 (IEEE Xplore 8311576) — vehicle RCS at 10/24/79 GHz, log-normal/log-Weibull statistics, mean ∝ log f (from abstract). (peer-reviewed; abstract)
12. ITU-R Recommendation P.840 — double-Debye permittivity of liquid water (as implemented; also used in 09-propagation). (standard)
13. `tools/verify/radar_rcs.py` — all computed numbers on this page. (verification script)
