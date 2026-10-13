---
title: Maxwell's equations — integral, differential and phasor forms, and where circuit laws come from
domain: 02-electromagnetics
slug: maxwells-equations
tags: [maxwell, gauss, faraday, ampere, displacement-current, continuity, constitutive-relations, phasors, KVL, KCL, lorentz-force]
prerequisites: [../00-math-foundations/vector-calculus-for-em.md, ../00-math-foundations/complex-numbers-and-phasors.md, electromagnetic-units-and-constants.md]
related: [wave-equation-plane-waves-polarization.md, poynting-vector-power-flow.md, boundary-conditions-reflection-refraction.md, quasi-static-vs-full-wave.md, radiation-from-currents-hertzian-dipole.md, inductance-capacitance-from-fields.md, ../01-circuit-theory/lumped-elements-impedance-admittance.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Maxwell's equations — integral, differential and phasor forms, and where circuit laws come from

## Questions this page answers
- What do each of Maxwell's four equations actually say, in plain words?
- What is displacement current, is it "real", and why is it essential for radio waves to exist?
- How do the integral and differential forms relate, and when should I use which?
- What are constitutive relations (D = εE, B = μH, J = σE) and when do they break down?
- How do I write Maxwell's equations for sinusoidal signals (phasor / time-harmonic form)?
- Where do KVL and KCL come from, and exactly when do they stop being true?
- Why does my oscilloscope show different voltages depending on how I route the probe ground lead?
- Is a conductor a conductor at all frequencies? (σ/ωε and charge relaxation time)

## TL;DR
- Four laws (SI): **Gauss** ∇·**D** = ρ; **no magnetic monopoles** ∇·**B** = 0; **Faraday** ∇×**E** = −∂**B**/∂t; **Ampère–Maxwell** ∇×**H** = **J** + ∂**D**/∂t. Plus the Lorentz force **F** = q(**E** + **v**×**B**) and constitutive relations [1][2][3].
- **Displacement current ∂D/∂t** is what lets a changing E-field create an H-field without charges moving. Faraday + displacement current together give a self-sustaining wave travelling at 1/√(με) — without it there is no radio.
- **Charge conservation** ∇·**J** + ∂ρ/∂t = 0 is built into the equations (take the divergence of Ampère–Maxwell); Maxwell added ∂D/∂t precisely to make Ampère's law consistent with it.
- **Phasor form** (e^{jωt}): ∇×**E** = −jωμ**H**, ∇×**H** = (σ + jωε)**E** + **J**_source. Conduction and displacement combine into a complex permittivity ε_c = ε − jσ/ω.
- **σ/(ωε)** decides "conductor or dielectric": copper at 433 MHz: 2.4×10⁹ (perfect conductor for most purposes); sea water: ≈ 3 at 433 MHz, ≈ 0.5 at 2.45 GHz (transitional); FR-4: ≈ 0.02 (a good dielectric). Verified in `tools/verify/em_maxwell.py`.
- **KVL** is Faraday's law with the magnetic flux through the loop neglected; **KCL** is charge conservation with charge accumulation at nodes neglected. Both are *quasi-static approximations*; they fail when loops enclose changing flux you did not model as an inductance, or when circuits are electrically large (> ~λ/10).
- A 20 mm × 10 mm loop 2 mm from a wire carrying 100 mA at 100 MHz picks up ≈ 0.45 V of EMF — "voltage" between two points then depends on the path.

## Intuition (no math)
Think of the equations as four statements about *sources* and *circulation*:

1. **Electric charge is a source of electric field** (Gauss). Field lines start on positive
   charge and end on negative charge. Count the flux out of a closed surface and you have counted
   the charge inside.
2. **There is no magnetic charge** (Gauss for magnetism). B-field lines never start or end; every
   line that enters a closed surface leaves it.
3. **A changing magnetic field makes the electric field circulate** (Faraday). Push a magnet
   through a coil and an EMF appears around the coil. The electric field here has *no* start or end
   — it curls around the changing flux like water around a drain. This is why "voltage" around
   a loop need not be zero.
4. **Currents — and changing electric fields — make the magnetic field circulate** (Ampère–
   Maxwell). A wire's current wraps H around it. Maxwell's insight was that a changing electric field
   does the same even where no charge moves — between capacitor plates, or in empty space.

Put 3 and 4 together in empty space: a changing E creates a curling H; that changing H creates a
curling E a little further along; and so on. The disturbance propagates on its own, at the speed
that the two "stiffnesses" ε0 and μ0 allow: c = 1/√(ε0μ0). This is light, radio, radar. Remove
displacement current and step 4 fails in vacuum — there would be no waves at all.

Circuit theory is what remains when everything is small compared with the wavelength: the
fields are confined to components (E in capacitors, B in inductors), so the "loop" of wires
between them encloses negligible changing flux (→ KVL), and wires don't pile up charge (→ KCL).

## The math

### Level 1 — the integral forms and what each term means

For a fixed surface S with boundary curve C (right-hand rule relates dl to dS), and a closed
surface ∂V enclosing volume V:

| Law | Integral form | Plain words |
|---|---|---|
| Gauss (electric) | $\oint_{\partial V}\mathbf D\cdot d\mathbf S = Q_\text{enc} = \int_V\rho\,dV$ | Net outward electric flux = free charge inside |
| Gauss (magnetic) | $\oint_{\partial V}\mathbf B\cdot d\mathbf S = 0$ | Magnetic flux lines are closed |
| Faraday | $\oint_C\mathbf E\cdot d\mathbf l = -\dfrac{d}{dt}\int_S\mathbf B\cdot d\mathbf S$ | EMF around a loop = −rate of change of flux through it |
| Ampère–Maxwell | $\oint_C\mathbf H\cdot d\mathbf l = \int_S\mathbf J\cdot d\mathbf S + \dfrac{d}{dt}\int_S\mathbf D\cdot d\mathbf S$ | MMF around a loop = conduction current + displacement current through it |

Symbols and SI units: **E** electric field (V/m); **D** electric flux density (C/m²); **H**
magnetic field (A/m); **B** magnetic flux density (T = Wb/m²); ρ free charge density (C/m³);
**J** free current density (A/m²); Q charge (C). The EMF ∮E·dl is in volts; ∮H·dl (the
magnetomotive force) is in amperes (ampere-turns).

(For a moving loop, Faraday's integral law with the total time derivative of flux includes the
motional EMF **v**×**B** — the "flux rule". The differential form below is the fixed-frame
statement.)

The **Lorentz force** on a charge q moving with velocity **v**: **F** = q(**E** + **v**×**B**).
This is how fields do work on matter; it is the physical definition of E and B.

### Level 1½ — the four laws in words, algebra only
The integrals above say four things. Each can be checked with one multiplication.
- **Charge makes E** (Gauss). Field lines start on positive charge and end on negative charge.
- **There are no magnetic charges** (Gauss for B). Magnetic field lines always close on themselves.
- **Changing B makes E** (Faraday). A loop of area A in a field B at frequency f picks up an EMF of $\omega BA$ (peak, for B perpendicular to the loop). That is how a loop antenna, a transformer and an unwanted ground loop all work.
- **Current and changing E make B** (Ampère–Maxwell). The second source is the displacement current $\varepsilon\,\partial E/\partial t$, i.e. $j\omega\varepsilon E$ per m². In a material the ratio of displacement current to conduction current is $\omega\varepsilon/\sigma$. Above 1 the material behaves as a dielectric, below 1 as a conductor.

*Worked number (verified, `tools/verify/s18b_level15_numbers.py`).* At 433.92 MHz:
- **Capacitor gap:** a 1 pF capacitor with 1 V across it carries $\omega CV$ = **2.73 mA** through its gap as pure displacement current. The same current flows as conduction current in the leads.
- **Materials:** $\omega\varepsilon/\sigma$ is **0.49** for seawater (εr 81, σ 4 S/m), so the two currents are comparable and seawater is a lossy conductor. It is 4 × 10⁻¹⁰ for copper (pure conductor). In FR-4 the conduction-to-displacement ratio is just tanδ ≈ 0.02 (a good dielectric).
- **Faraday:** a 1 cm² loop in a 1 µT field picks up **0.27 V**.

### Level 2 — differential forms

Apply the divergence theorem ∮**F**·d**S** = ∫∇·**F** dV and Stokes' theorem ∮**F**·d**l** =
∫(∇×**F**)·d**S** (see [vector calculus](../00-math-foundations/vector-calculus-for-em.md)); since the
volumes/surfaces are arbitrary, the integrands must match:

$$\nabla\cdot\mathbf D = \rho,\qquad \nabla\cdot\mathbf B = 0,\qquad \nabla\times\mathbf E = -\frac{\partial\mathbf B}{\partial t},\qquad \nabla\times\mathbf H = \mathbf J + \frac{\partial\mathbf D}{\partial t}.$$

Use the **integral form** for problems with symmetry (field of a wire, coax, sphere), for
boundary conditions (pill-box and loop arguments — see
[boundary conditions](boundary-conditions-reflection-refraction.md)), and for circuit reasoning
(EMF around a loop). Use the **differential form** to derive wave equations and for numerical
solvers (FDTD discretises the two curl equations directly — the Yee algorithm).

**Why displacement current is required (derivation).** Take the divergence of the original
Ampère law ∇×**H** = **J**. Since ∇·(∇×**H**) ≡ 0 for any field (checked symbolically in
`tools/verify/em_maxwell.py`), it would force ∇·**J** = 0 always — i.e. charge could never
accumulate anywhere, which is false for a charging capacitor. Charge conservation requires
$$\nabla\cdot\mathbf J = -\frac{\partial\rho}{\partial t} = -\frac{\partial}{\partial t}\nabla\cdot\mathbf D = -\nabla\cdot\frac{\partial\mathbf D}{\partial t},$$
so ∇·(**J** + ∂**D**/∂t) = 0 always. Replacing **J** by **J** + ∂**D**/∂t restores consistency.
This is exactly Maxwell's 1865 addition [1][2]. The classic check: apply Ampère's integral law to
a loop around the wire feeding a capacitor, once with a flat surface cut by the wire (conduction
current I) and once with a surface ballooning between the plates (no conduction current). Only
with ∂D/∂t = I/A between the plates do both surfaces give the same answer.

**Continuity equation.** Taking the divergence of Ampère–Maxwell and using Gauss:
$$\nabla\cdot\mathbf J + \frac{\partial\rho}{\partial t} = 0\qquad\Longleftrightarrow\qquad \oint\mathbf J\cdot d\mathbf S = -\frac{dQ_\text{enc}}{dt}.$$
It is not an independent law; it follows from Maxwell's equations. Conversely, for time-varying
fields the two divergence equations follow from the two curl equations plus continuity (take ∇· of
Faraday: ∂(∇·**B**)/∂t = 0). So for time-harmonic problems only the **two curl equations** are
independent — which is why solvers only discretise those.

### Level 2 — constitutive relations

Maxwell's equations have more unknowns (E, D, H, B, J) than equations. Material behaviour closes
the system:

$$\mathbf D = \varepsilon_0\mathbf E + \mathbf P,\qquad \mathbf B = \mu_0(\mathbf H + \mathbf M),\qquad \mathbf J = \sigma\mathbf E\ (+\ \mathbf J_\text{source}).$$

**P** (polarisation, C/m²) is the dipole moment per unit volume; **M** (magnetisation, A/m) the
magnetic moment per unit volume. For **linear, isotropic, instantaneous** media,
**P** = ε0χ_e**E**, **M** = χ_m**H**, so **D** = ε0(1+χ_e)**E** = ε**E** with ε = ε0εr, and
**B** = μ**H** with μ = μ0μr; **J** = σ**E** is Ohm's law in point form.

Where each simplification fails (and where this KB covers it):

| Assumption | Fails when | Consequence / page |
|---|---|---|
| Linear | ferrites near saturation, high-field breakdown, nonlinear dielectrics (ferroelectrics) | intermod, detuning; [magnetic materials](magnetic-materials-permeability.md) |
| Isotropic | glass-weave laminates (εr differs in-plane vs through-thickness), magnetised ferrites (tensor μ), liquid crystals | [dielectrics](dielectrics-permittivity-loss-tangent.md), circulators |
| Instantaneous (non-dispersive) | always, strictly: ε(ω), μ(ω), σ(ω) are frequency dependent; causality ties real and imaginary parts (Kramers–Kronig) | Debye/Djordjevic–Sarkar models |
| Homogeneous | layered/graded media, PCBs | effective permittivity (microstrip) |
| Local | plasmas, metals at THz (spatial dispersion) | out of scope |

In the frequency domain dispersion is handled simply: ε, μ, σ become complex functions of ω.

### Level 2 — phasor (time-harmonic) form

With the KB convention (CONVENTIONS §4.5) **E**(r,t) = Re{**E**(r)e^{jωt}}, time derivatives
become jω:
$$\nabla\times\mathbf E = -j\omega\mathbf B = -j\omega\mu\mathbf H,\qquad \nabla\times\mathbf H = \mathbf J_s + \sigma\mathbf E + j\omega\varepsilon\mathbf E = \mathbf J_s + j\omega\varepsilon_c\mathbf E,$$
$$\varepsilon_c = \varepsilon' - j\varepsilon'' - j\frac{\sigma}{\omega},\qquad \nabla\cdot(\mu\mathbf H) = 0,\qquad \nabla\cdot(\varepsilon_c\mathbf E) = -\frac{\nabla\cdot\mathbf J_s}{j\omega} = \rho_s\ \text{(impressed charge only)}.$$
(The last form follows from taking the divergence of the Ampère–Maxwell phasor equation; in a
homogeneous region without impressed sources ∇·**E** = 0.)
Here **J**_s is an impressed source current (an antenna feed), σ**E** the conduction current, and
ε'' the dielectric (polarisation) loss. A measurement cannot distinguish σ/ω from ε'' at a
single frequency; datasheets lump them into a **loss tangent**
$$\tan\delta = \frac{\omega\varepsilon'' + \sigma}{\omega\varepsilon'}.$$
Physics texts using e^{−iωt} write ε = ε' + iε'' and ∇×**E** = iωμ**H**; replace j → −i to convert
(see [complex numbers & phasors](../00-math-foundations/complex-numbers-and-phasors.md)). Whether
phasor amplitudes are **peak** (Pozar, Balanis, Harrington) or **rms** (some power-engineering
texts) changes factors of ½ in power expressions; this KB uses **peak** phasors unless stated.

**Good conductor vs good dielectric.** The ratio of conduction to displacement current density is
|σ**E**| / |jωε**E**| = σ/(ωε). Numbers from `tools/verify/em_maxwell.py`:

| Material (εr, σ) | σ/(ωε) at 433 MHz | at 2.45 GHz | Crossover f where σ = ωε | Relaxation time τ = ε/σ |
|---|---|---|---|---|
| Copper (1, 5.8×10⁷ S/m) | 2.4×10⁹ | 4.3×10⁸ | ~10¹⁸ Hz (formal) | 1.5×10⁻¹⁹ s (formal; see Level 3) |
| Sea water (70, 5 S/m) [4] | 3.0 | 0.52 | 1.28 GHz | 1.2×10⁻¹⁰ s |
| Fresh water (80, 0.01 S/m) | 0.005 | 0.0009 | 2.2 MHz | 7×10⁻⁸ s |
| Medium-dry ground (15, 10⁻³ S/m) (LF values) | 0.003 | 0.0005 | 1.2 MHz | 1.3×10⁻⁷ s |
| FR-4 (4.4, tanδ = 0.02) | 0.02 (by definition ≈ tanδ) | 0.02 | — | — |

Rule: σ/(ωε) ≫ 1 → good conductor (skin effect, see
[skin effect](skin-effect-conductor-loss-roughness.md)); ≪ 1 → good dielectric (low loss
propagation). Sea water is a conductor at HF–VHF and becomes a lossy dielectric in the GHz range;
this matters for sea-surface reflection (see
[reflection](boundary-conditions-reflection-refraction.md)). Ground σ values at UHF are larger than
the LF values listed because dielectric relaxation losses rise with frequency (ITU-R P.527 [5]).

### Level 3 — from Maxwell to Kirchhoff, and when it fails

**KVL.** Integrate **E** around a closed circuit path C. Faraday gives
$$\sum_k v_k = \oint_C\mathbf E\cdot d\mathbf l = -\frac{d\Phi_C}{dt},$$
where Φ_C is the magnetic flux through *any* surface bounded by the path. Circuit theory proceeds
by (1) routing the path through the *inside* of each component so that its terminal voltage is
v_k = ∫E·dl across it (for an inductor, the path along the wire inside the coil sees almost no E, so
the "voltage drop" v_L = L di/dt appears between its terminals outside the coil), and (2) assuming
that the flux through the rest of the loop (the wiring) is negligible, or has been lumped into an
explicit inductor. Then Σv_k = 0. KVL is therefore **Faraday's law with the wiring's flux either
ignored or lumped**.

KVL fails — more precisely, "the voltage between two nodes" becomes path dependent — when an
un-modelled changing flux links the measurement loop. Classic demonstrations (Lewin's two-resistor
ring around a solenoid; see also Romer 1982 [6]) show two voltmeters connected to the same two
nodes reading different values. In RF hardware:
- a scope probe ground lead forms a loop; nearby switching or RF currents induce an EMF in it that
  the scope reports as "signal" (the 1 cm ground-spring fix works by shrinking the loop area);
- the "voltage" between two ground points on a PCB is ambiguous at RF: it depends on the path
  along which you integrate E (see [grounding](../13-pcb-rf-layout-emc/grounding-and-return-paths.md)).

Worked scale (from `em_maxwell.py`): a 20 mm × 10 mm loop whose near side is 2 mm from a long
wire carrying 100 mA rms at 100 MHz has mutual inductance M = (μ0 L/2π) ln(12/2) = 7.2 nH and
EMF = ωMI = **0.45 V rms**.

**KCL.** Integrate continuity over a small closed surface around a node:
Σ i_k = −dQ_node/dt. KCL (Σi_k = 0) holds when the node's charge does not change — i.e. when the
node's capacitance to everything else (explicitly or implicitly) is negligible or has been lumped
into a capacitor element. At RF, a pad of 1 mm² over a ground plane 0.2 mm away is ≈ 0.2 pF
(ε = 4.4ε0): at 2.4 GHz its reactance is ≈ 330 Ω — not negligible next to 50 Ω. KCL then only
holds if you add that capacitor to the schematic.

**When is the lumped description valid?** When the circuit's largest dimension ℓ ≪ λ (commonly
ℓ < λ/10, stricter λ/20 for accurate phase; for pulses, when the propagation delay across the circuit
≪ rise time). The retardation, radiation and path-dependent voltages all scale with (ℓ/λ). Full
treatment and criteria: [quasi-static vs full-wave](quasi-static-vs-full-wave.md) and Haus &
Melcher ch. 3 [3].

**Charge relaxation and "E = 0 inside a conductor".** Combining continuity, Gauss and Ohm in a
homogeneous conductor: ∂ρ/∂t = −(σ/ε)ρ, so any interior free charge decays as e^{−t/τ} with
τ = ε/σ. For copper the formal τ ≈ 1.5×10⁻¹⁹ s; the actual relaxation is limited by the electron
collision time (~2.5×10⁻¹⁴ s for Cu at room temperature, Drude model) — still far faster than any RF
period, so conductors are charge-neutral inside and carry charge only on their surfaces [2][7].
"E = 0 inside a conductor" is a *static* statement; at RF, E inside a good conductor is small but
non-zero and decays over the skin depth.

**Magnetic sources (duality).** Antenna theory adds fictitious magnetic current **M** and charge
ρ_m: ∇×**E** = −**M** − jωμ**H**, ∇·**B** = ρ_m. These are mathematical equivalents (e.g. the
tangential E over an aperture acts like a magnetic current sheet), not claims that monopoles exist.
They make the equations symmetric under E→H, H→−E, ε↔μ, J→M, M→−J (Harrington [8] ch. 3;
Balanis [9] ch. 3). The small loop antenna is the dual of the Hertzian dipole
([radiation](radiation-from-currents-hertzian-dipole.md)).

**Uniqueness.** In a region with some loss, the fields are uniquely determined by the sources
plus either tangential E or tangential H on the boundary. This justifies equivalence principles,
image theory and the use of perfect-conductor boundaries in solvers [8].

## Design equations & rules of thumb

| Equation | When valid | Typical value / note |
|---|---|---|
| I_D = C dV/dt = jωCV | any capacitor | 10 pF, 1 V, 433 MHz → 27 mA |
| EMF = −dΦ/dt = −jωMI | loop coupling to a current | 7 nH mutual, 100 mA, 100 MHz → 0.45 V |
| σ/(ωε) ≫ 1 → conductor | material classification | sea water crossover ≈ 1.3 GHz |
| τ = ε/σ | charge relaxation | Cu: ≪ 1 fs; sea water ≈ 0.12 ns |
| ε_c = ε' − j(ε'' + σ/ω) | phasor analysis | tanδ = (ωε''+σ)/(ωε') |
| Lumped if ℓ < λ/10 (λ/20 for phase-critical) | circuit theory validity | λ in FR-4 at 915 MHz ≈ 16 cm → 1.6 cm |

## Worked examples

**1. Displacement current in a DC-blocking capacitor.** A 10 pF 0402 capacitor passes 1 V rms at
433 MHz. X_C = 1/(2π·433×10⁶·10×10⁻¹²) = 36.8 Ω; I = V/X_C = 27.2 mA rms. Between the plates no
charge moves, yet Ampère–Maxwell gives exactly this current as ∂D/∂t integrated over the plate area:
D = Q/A, so ∫(∂D/∂t)·dS = dQ/dt = I. The H-field circling the capacitor body equals the one
circling the leads.

**2. Is sea water a conductor for a 433 MHz rocket-recovery beacon?** Using ITU-R P.368 sea water
(εr = 70, σ = 5 S/m) [4]: σ/(ωε) = 5/(2π·433×10⁶·70·8.854×10⁻¹²) = 2.97. Conduction dominates
but not overwhelmingly; the wave penetrates only ~1 cm (computed in
[skin effect](skin-effect-conductor-loss-roughness.md) and
[wave equation](wave-equation-plane-waves-polarization.md)). A beacon under 10 cm of sea water is
effectively silent; one floating on it radiates, with a strong ground-plane effect.

**3. Probe ground-lead pickup.** A 15 cm scope ground lead forming a loop of ~10 cm² near a
switching regulator's 1 A, 10 ns edge: B ≈ μ0I/(2πd) at d = 2 cm is 10 µT; dΦ/dt ≈ (10 µT ×
10⁻³ m²)/10 ns ≈ 1 V spike appears in the "measured" signal. The fix (probe tip + ground spring,
< 1 cm² loop) reduces this by ~20 dB. (Order-of-magnitude estimate; the flux is not uniform.)

**4. Where does the current "go" in a capacitor at 1.575 GHz?** The GNSS LNA input DC block of
100 pF: X_C ≈ 1 Ω. The same displacement-current picture holds, but now the capacitor's own
parasitic inductance (~0.5 nH for 0402, X_L ≈ 5 Ω) dominates — Maxwell's equations don't care about
the label "capacitor"; the field structure does. See
[capacitors at RF](../04-real-components-hf/capacitors-at-rf-mlcc.md).

## Practical notes
- Field solvers (openEMS FDTD, NEC-2 MoM, FEM tools) are just discretisations of these equations
  with constitutive relations and boundary conditions; if a simulation disagrees with a
  measurement, the usual culprits are materials (ε, tanδ, σ, roughness) and boundaries, not
  Maxwell. See [EM solvers](../16-simulation-tools/em-solvers-fdtd-mom-fem.md).
- When a board "misbehaves at RF", ask which Maxwell term the schematic omits: a loop area
  (Faraday → un-modelled mutual inductance), a node capacitance (displacement current → un-modelled
  C), or an electrically long path (retardation).
- Kirchhoff "violations" are measurable with an ordinary scope; they are the physical basis of
  EMC ground-loop coupling (see [EMC fundamentals](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md)).

## Common mistakes & misconceptions
- **"Displacement current is not a real current, so it doesn't matter."** It carries no charge,
  but it produces magnetic field exactly like conduction current and is the reason capacitors pass
  AC and waves propagate. In vacuum it is the *only* current. (Whether to call it "current" is
  semantics; its magnetic effect is not.)
- **"Maxwell's equations are eight/four independent equations."** In time-varying problems the
  divergence equations follow from the curl equations and continuity; only the curl equations are
  independent (six scalar equations).
- **"A voltmeter measures the potential difference between two points."** A voltmeter measures
  ∫E·dl along its leads. With changing magnetic flux, E is not conservative, and different lead
  routes give different readings. "Potential difference" is only uniquely defined in electrostatics
  (or with a chosen gauge).
- **"KVL is a fundamental law."** It is a quasi-static approximation of Faraday's law. It is
  excellent at audio frequencies and on small RF modules, and must be patched (by adding mutual
  inductances and parasitic capacitances) or abandoned for electrically large structures.
- **"The field inside a conductor is always zero."** Only in electrostatics. At RF, E and J
  decay exponentially into the conductor over the skin depth.
- **"Magnetic field lines always close."** B lines always close (∇·B = 0). H lines can start and end
  where magnetisation changes (∇·H = −∇·M), e.g. at the faces of a permanent magnet.
- **"Electrons carry the signal at nearly the speed of light."** Electrons drift at mm/s (drift
  velocity v = I/(nqA); ~0.07 mm/s for 1 A in 1 mm² Cu). The signal is the electromagnetic field
  guided by the conductors, travelling at c/√εr,eff. See
  [Poynting vector](poynting-vector-power-flow.md).

## How to simulate / verify
- `python3 tools/verify/em_maxwell.py` — symbolic proof that Ampère–Maxwell + Gauss imply
  continuity; symbolic check that a plane wave satisfies Maxwell's equations only if k = ω√(με) and
  η = √(μ/ε); σ/(ωε) and τ for common materials; displacement-current and loop-EMF numbers above.
- openEMS (FDTD) directly time-steps the curl equations on a Yee grid; a charging parallel-plate
  capacitor model shows the H-field circling the gap exactly as around the wire.
- A two-voltmeter demonstration: two resistors (e.g. 100 Ω and 900 Ω) in a ring around a ferrite
  core driven by a primary winding; scope probes on the same two nodes but routed on opposite sides
  of the core read opposite-signed voltages.

## Open questions / gaps
- Historical attributions (Maxwell 1865 "A dynamical theory of the electromagnetic field"; the
  Heaviside vector form) are stated from standard textbook accounts; not re-verified against
  primary sources.
- Electron collision time for Cu (~2.5×10⁻¹⁴ s) is a Drude-model textbook value (Ashcroft & Mermin
  Table 1.3 order of magnitude); medium confidence.

## Sources
1. D. J. Griffiths, *Introduction to Electrodynamics*, 4th ed., 2013, ch. 7 (electrodynamics,
   Maxwell's correction to Ampère's law, §7.3), ch. 8 (conservation laws). (textbook)
2. D. K. Cheng, *Field and Wave Electromagnetics*, 2nd ed., Addison-Wesley 1989, ch. 7
   (time-varying fields and Maxwell's equations; time-harmonic form; §5 charge relaxation in
   conductors). (textbook)
3. H. A. Haus and J. R. Melcher, *Electromagnetic Fields and Energy*, Prentice Hall 1989; free at
   MIT OCW RES.6-001 and https://web.mit.edu/6.013_book/www/ — ch. 1–2 (integral/differential laws),
   ch. 3 (conditions for quasistatics). (textbook, free)
4. ITU-R Recommendation P.368-10 (08/2022), *Ground-wave propagation prediction method for
   frequencies between 10 kHz and 30 MHz*, Fig. 2 (sea water, average salinity: σ = 5 S/m, εr = 70).
   (standard)
5. ITU-R Recommendation P.527-6 (09/2021), *Electrical characteristics of the surface of the Earth*
   (frequency dependence of water and soil permittivity; penetration depth eq. 4). (standard)
6. R. H. Romer, "What do 'voltmeters' measure?: Faraday's law in a multiply connected region,"
   *Am. J. Phys.* 50, 1089 (1982). (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge, not re-read)
7. N. W. Ashcroft and N. D. Mermin, *Solid State Physics*, 1976, ch. 1 (Drude relaxation times).
   (textbook)
8. R. F. Harrington, *Time-Harmonic Electromagnetic Fields*, McGraw-Hill 1961 / IEEE Press 2001,
   ch. 1 (fundamental concepts, magnetic currents), ch. 3 (duality, uniqueness, equivalence). (textbook)
9. C. A. Balanis, *Advanced Engineering Electromagnetics*, 2nd ed., Wiley 2012, ch. 1 (Maxwell's
   equations, constitutive parameters), ch. 3 (duality, uniqueness). (textbook)
10. R. P. Feynman, R. B. Leighton, M. Sands, *The Feynman Lectures on Physics*, Vol. II, ch. 18
    ("The Maxwell Equations") and ch. 17 (laws of induction, flux rule exceptions); online at
    feynmanlectures.caltech.edu (site returned 403 on 2026-09-27; cited from knowledge). (textbook, free)
11. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley 2012, §1.2–1.3 (Maxwell's equations,
    fields in media, loss tangent definition). (textbook)
