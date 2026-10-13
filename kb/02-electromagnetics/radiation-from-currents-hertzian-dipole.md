---
title: Radiation from currents — potentials, the Hertzian dipole, small loops and why circuits radiate
domain: 02-electromagnetics
slug: radiation-from-currents-hertzian-dipole
tags: [radiation, vector-potential, lorenz-gauge, retarded-potentials, green-function, hertzian-dipole, radiation-resistance, larmor, small-loop, magnetic-dipole, duality, common-mode, differential-mode, EMC]
prerequisites: [maxwells-equations.md, wave-equation-plane-waves-polarization.md, poynting-vector-power-flow.md]
related: [near-field-far-field.md, quasi-static-vs-full-wave.md, ../08-antennas/antenna-fundamentals.md, ../08-antennas/dipoles-and-monopoles.md, ../08-antennas/loop-antennas.md, ../08-antennas/small-antenna-limits.md, ../13-pcb-rf-layout-emc/emc-emi-fundamentals.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Radiation from currents — potentials, the Hertzian dipole, small loops and why circuits radiate

## Questions this page answers
- How do currents produce radiated waves, step by step from Maxwell's equations?
- What are the scalar and vector potentials, the Lorenz gauge and "retarded" potentials?
- What are the complete fields of a Hertzian (infinitesimal) dipole, including the near-field terms?
- Where does R_rad = 80π²(l/λ)² come from, and why do some books get 789 Ω and others 790 Ω?
- Why do accelerating charges radiate but steady currents don't?
- How much does a small loop radiate, and why is a small loop antenna so inefficient?
- Why do cables (common-mode) radiate far more than PCB loops (differential-mode)?

## TL;DR
- Write **B = ∇×A** and **E = −∇Φ − ∂A/∂t**. In the **Lorenz gauge** each potential obeys a wave equation driven by its source; in phasor form **(∇² + k²)A = −μJ**, solved by the **retarded potential** A(r) = (μ/4π)∫J(r′)e^{−jkR}/R dV′ — each source element contributes a spherical wave delayed by R/c [1][2][3].
- **Hertzian dipole** (current I, length l ≪ λ, along z): H_φ = (jkIl sinθ/4πr)(1 + 1/jkr)e^{−jkr}; E_θ = (jηkIl sinθ/4πr)(1 + 1/jkr − 1/(kr)²)e^{−jkr}; E_r = (ηIl cosθ/2πr²)(1 + 1/jkr)e^{−jkr}. The 1/r terms radiate; 1/r² and 1/r³ terms are stored (reactive) near field. Verified symbolically from A in `tools/verify/em_hertzian_dipole.py`.
- **Radiation resistance R_rad = (2π/3)η(l/λ)² = 789.0(l/λ)² Ω** with η0 = 376.73 Ω; the textbook **80π²(l/λ)² = 789.6(l/λ)²** uses η = 120π (0.07 % high). Directivity 1.5 (1.76 dBi). Short dipole with triangular current: ¼ of that, **20π²(l/λ)²**.
- **Larmor**: a charge q with acceleration a radiates P = q²a²/(6πε0c³) — identical to ½I²R_rad for the equivalent dipole (checked numerically). Radiation needs *changing* current (acceleration); DC doesn't radiate.
- **Small loop** (area A, circumference C ≪ λ) is the dual (magnetic dipole m = IA): **R_rad = 20π²(C/λ)⁴ = 320π⁴A²/λ⁴** — tiny: a 3 cm loop at 433 MHz has 68 mΩ, so copper loss (~0.16 Ω for 1 mm wire) makes it only ~30 % efficient.
- **EMC** (far field, max direction, free space): differential-mode loop **E ≈ 1.316×10⁻¹⁴ f²AI/r**; common-mode wire pair **E ≈ 1.257×10⁻⁶ f I_C L/r** (Paul) [4]. At 100 MHz, **3.6 µA** of common-mode current on a 1 m cable produces 150 µV/m at 3 m (≈ the FCC Class B limit), versus **34 mA** in a 1 cm² differential loop.

## Intuition (no math)
A static charge has a static field; a charge moving at constant velocity carries its field along with
it. When a charge *accelerates*, the news of the change spreads outward at c. Far away, the field
lines still point to where the charge "was"; close in, they point to where it "is"; joining them is
a kink travelling outward at the speed of light. That kink is transverse to the direction of travel and
its strength falls as 1/r — not 1/r² like a static field — so it carries energy to infinity. That is
radiation. (This picture is due to J. J. Thomson and popularised by Purcell.)

An RF current in a wire is charges sloshing back and forth — constant acceleration and deceleration —
so every short piece of wire is a little radiator. Whether a circuit radiates *usefully* (an antenna) or
*uselessly* (EMC trouble) is a question of how well these contributions add up far away. Two
equal-and-opposite currents close together (a transmission line, a small loop) nearly cancel — only
the tiny path difference between them survives, so radiation grows steeply with size (∝ size² for the
power from a loop's area). A current flowing in the same direction on both wires of a cable
(common-mode) doesn't cancel at all; even microamps radiate.

## The math

### Level 1 — potentials and the result

Because ∇·**B** = 0 we can write **B** = ∇×**A** (A: magnetic vector potential, Wb/m). Faraday then
lets us write **E** = −∇Φ − ∂**A**/∂t (Φ: scalar potential, V). Potentials are not unique (gauge
freedom: A → A + ∇χ, Φ → Φ − ∂χ/∂t leaves E and B unchanged). The **Lorenz gauge**
∇·**A** + με ∂Φ/∂t = 0 decouples them:
$$\nabla^2\mathbf A - \mu\varepsilon\frac{\partial^2\mathbf A}{\partial t^2} = -\mu\mathbf J,\qquad \nabla^2\Phi - \mu\varepsilon\frac{\partial^2\Phi}{\partial t^2} = -\frac{\rho}{\varepsilon}.$$
Solution (retarded potentials; R = |**r** − **r**′|, v = 1/√(με)):
$$\mathbf A(\mathbf r,t) = \frac{\mu}{4\pi}\int\frac{\mathbf J(\mathbf r',\,t - R/v)}{R}\,dV',\qquad \Phi(\mathbf r,t) = \frac{1}{4\pi\varepsilon}\int\frac{\rho(\mathbf r',\,t-R/v)}{R}\,dV'.$$
Each source element contributes as in statics, but evaluated at the *retarded time* t − R/v.

### Level 1½ — a short wire in three numbers, algebra only
The retarded-potential integrals above reduce to three facts for a wire much shorter than λ.
- **Delay.** The field at distance r reflects the current r/c earlier: 3.34 µs per km, i.e. about 1444 cycles at 433 MHz. This is the "retarded time".
- **Far-field strength.** The far field is $E = 60\pi\,I\,(l/\lambda)\sin\theta/r$ V/m (peak I in A, r in m). It grows with the current-times-length product measured in wavelengths.
- **Radiation resistance.** For a uniform current, $R_{rad} = 80\pi^2(l/\lambda)^2$ ≈ 789 (l/λ)² Ω. It is quadratic in length: double the wire and R rises four times. A real open-ended short dipole has a triangular current (zero at the tips) and gives one quarter of this, $20\pi^2(l/\lambda)^2$.

*Worked number (verified, `tools/verify/s18b_level15_numbers.py`).* Take a 5 cm wire at 433 MHz (λ = 0.692 m, l/λ = 0.0722).
- **Radiation resistance:** **4.12 Ω** with uniform current (e.g. top-loaded), **1.03 Ω** with triangular current. A 1 Ω loss resistance therefore wastes about half the power in the triangular case.
- **Fields and power:** a 10 mA peak current gives **136 µV/m** (peak) broadside at 1 km. It radiates ½I²R = 0.21 mW in the uniform case.

### Level 2 — phasor form and the Hertzian dipole

With e^{jωt}, k = ω√(με):
$$(\nabla^2 + k^2)\mathbf A = -\mu\mathbf J\ \Rightarrow\ \mathbf A(\mathbf r) = \frac{\mu}{4\pi}\int\mathbf J(\mathbf r')\frac{e^{-jkR}}{R}\,dV',$$
using the free-space Green's function e^{−jkR}/(4πR). Then **H** = (1/μ)∇×**A** and (away from sources)
**E** = (1/jωε)∇×**H** — no need for Φ (the Lorenz condition is built in).

**Hertzian dipole**: a uniform current I on a length l ≪ λ along z at the origin (charges ±Q = ±I/jω
accumulate at the ends). Then A = ẑ μIl e^{−jkr}/(4πr). Taking the curls in spherical coordinates
(done symbolically in the script, which asserts agreement with these forms):
$$H_\phi = \frac{jkIl\sin\theta}{4\pi r}\left[1 + \frac{1}{jkr}\right]e^{-jkr},$$
$$E_r = \frac{\eta Il\cos\theta}{2\pi r^2}\left[1 + \frac{1}{jkr}\right]e^{-jkr},\qquad E_\theta = \frac{j\eta kIl\sin\theta}{4\pi r}\left[1 + \frac{1}{jkr} - \frac{1}{(kr)^2}\right]e^{-jkr}.$$

- **kr ≫ 1 (far field)**: only E_θ and H_φ ∝ 1/r survive, in phase, with E_θ/H_φ = η — a local plane
  wave. Pattern ∝ sin θ (doughnut, null along the wire).
- **kr ≪ 1 (near field)**: E ≈ quasi-static field of an electric dipole p = Ql (∝ 1/r³), H ≈ Biot–Savart
  field of the current element (∝ 1/r²). E and H are 90° out of phase → reactive (stored) energy.
- The terms are equal in magnitude at **kr = 1, r = λ/2π** — the conventional boundary of the reactive
  near field (see [near field vs far field](near-field-far-field.md)).

**Radiated power and radiation resistance.** Far-field Poynting vector
S_r = ½Re(E_θH_φ*) = (η/2)(kIl sinθ/4πr)². Integrating over the sphere (script, symbolic):
$$P_\text{rad} = \frac{\eta\pi}{3}\left(\frac{Il}{\lambda}\right)^2 = \frac12 I^2R_\text{rad},\qquad \boxed{R_\text{rad} = \frac{2\pi\eta}{3}\left(\frac{l}{\lambda}\right)^2}$$
Numerically **(2π/3)η0 = 789.02 Ω** (CODATA η0) vs **80π² = 789.57 Ω** (η = 120π) — the familiar formula
is 0.069 % high because of the 120π rounding (see [constants](electromagnetic-units-and-constants.md)).
Directivity D = 4πU_max/P = 1.5 = 1.76 dBi.

**Short (not infinitesimal) dipole.** A centre-fed wire of length l ≪ λ has a *triangular* current
(maximum I0 at the feed, zero at the open ends). Its average current is I0/2, so the far field is halved
and R_rad (referred to the feed current) is quartered: **R_rad ≈ 20π²(l/λ)²** — e.g. 1.97 Ω for a λ/10
dipole. A short monopole of height h over a large ground plane has half the R_rad of the equivalent
dipole of length 2h (image theory): ½·20π²(2h/λ)² = 40π²(h/λ)² — details in
[dipoles and monopoles](../08-antennas/dipoles-and-monopoles.md).

**Complex power through a sphere.** Integrating ½E×H* over a sphere of radius r gives
$$P(r) = \frac{\eta\pi}{3}\left(\frac{Il}{\lambda}\right)^2\left[1 - \frac{j}{(kr)^3}\right],$$
checked numerically at kr = 0.3, 1, 3. The real part (radiated power) is independent of r; the
imaginary part (net stored electric energy, capacitive) grows as 1/(kr)³ close in. This huge reactive
power relative to radiated power is why electrically small antennas have high Q and narrow bandwidth
([small antenna limits](../08-antennas/small-antenna-limits.md), Chu/Wheeler).

### Level 2 — why accelerating charges radiate: Larmor

A point charge q with (non-relativistic) acceleration a radiates
$$P = \frac{q^2a^2}{6\pi\varepsilon_0c^3}\quad\text{(SI; Gaussian: }2q^2a^2/3c^3).$$
For harmonic motion x = x0 cos ωt, the dipole moment p = qx0 and the equivalent current element is
|Il| = ωp. The time-average of Larmor's formula equals ½|Il|²(2πη0/3λ²) exactly (script: 1 nC, 1 cm
amplitude at 433 MHz → 0.609 W both ways). So "accelerating charge radiates" and "a time-varying current
element radiates" are the same statement. A DC current in a closed circuit has no acceleration along
straight segments (and the radiation from charges turning corners cancels in steady state): no
radiation.

### Level 3 — the small loop (magnetic dipole) and duality

A loop of area A carrying uniform current I (circumference C ≪ λ) is a magnetic dipole m = IA. By
duality (E → H, H → −E, ε ↔ μ, Il → jωμIA; see [Maxwell](maxwells-equations.md) Level 3), its far
field is
$$E_\phi = \frac{\eta k^2IA\sin\theta}{4\pi r}e^{-jkr},\qquad H_\theta = -\frac{E_\phi}{\eta},$$
and
$$R_\text{rad} = 20\pi^2\left(\frac{C}{\lambda}\right)^4 = \frac{320\pi^4A^2}{\lambda^4}\ \ (\approx 31\,171\,A^2/\lambda^4).$$
The ⁴ power makes small loops very poor radiators (script): at 433 MHz a 1 cm loop has 0.84 mΩ, 3 cm
68 mΩ, 5 cm 0.52 Ω. (At 915 MHz a 5 cm loop has C/λ = 0.48 — no longer small; the formula no longer
applies.) N turns multiply R_rad by N² (and loss by ~N plus proximity effect). The near field of a
small loop is magnetic-dominant (low wave impedance) — the dual of the dipole's electric-dominant near
field.

Duality also gives: a slot in a conducting plane radiates like a magnetic dipole (Babinet), and
aperture fields can be represented by magnetic surface currents (equivalence principle) — used
throughout [aperture antennas](../08-antennas/horn-reflector-aperture-antennas.md).

### Level 3 — differential-mode vs common-mode radiation (EMC)

Clayton Paul [4] and Ott [5] model a PCB trace pair or a cable as two parallel wires of length L,
separation s, carrying a differential current I_D (equal and opposite) and a common-mode current I_C
(same direction on each wire). In free space, at the maximum-radiation direction, far field:
$$|E_\text{DM}| \approx \frac{\eta_0\pi}{c^2}\frac{f^2AI_D}{r} = 1.316\times10^{-14}\frac{f^2(Ls)I_D}{r},\qquad |E_\text{CM}| \approx \frac{\eta_0}{c}\frac{fI_CL}{r} = 1.257\times10^{-6}\frac{fI_CL}{r}$$
(f in Hz, L, s, r in m, currents in A; both constants reproduced in the script from η0 and c; Paul's I_C
is the current *per wire*, so the total CM current is 2I_C). Ott's versions for measurements over a
ground plane are 2× larger (ground-reflection allowance).

Key contrast: DM radiation ∝ f²·(loop area) — controlled by keeping signal and return close (small
loops); CM radiation ∝ f·L — controlled by preventing CM current (good return paths, CM chokes,
shielding terminations). Numbers (script, 100 MHz, 3 m, 150 µV/m ≈ FCC Part 15 Class B 88–216 MHz limit
— limit value cited from knowledge): **I_C = 3.6 µA** on a 1 m cable vs **I_D = 34 mA** in a 1 cm² loop.
A flight-computer harness or a GNSS antenna cable carrying a few µA of CM noise from a switching
regulator can therefore desensitise its own receiver — see
[EMC fundamentals](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md).

## Design equations & rules of thumb

| Equation | When valid | Typical value |
|---|---|---|
| A = (μ/4π)∫J e^{−jkR}/R dV′ | any source, homogeneous medium | — |
| R_rad = (2π/3)η(l/λ)² ≈ 789(l/λ)² Ω | uniform current, l ≪ λ | λ/10: 7.9 Ω |
| R_rad ≈ 20π²(l/λ)² | short dipole, triangular current | λ/10: 1.97 Ω |
| R_rad = 20π²(C/λ)⁴ | small loop, C ≲ λ/10 (≈ λ/3 rough) | 3 cm @ 433 MHz: 68 mΩ |
| D = 1.5 (1.76 dBi) | any short dipole or small loop | — |
| P = q²a²/(6πε0c³) | non-relativistic charge | Larmor |
| near-field boundary kr = 1 | Hertzian dipole | r = λ/2π (11 cm @ 433 MHz) |
| E_DM = 1.316×10⁻¹⁴ f²AI/r | electrically small loop | 1 cm², 34 mA, 100 MHz → 150 µV/m @ 3 m |
| E_CM = 1.257×10⁻⁶ f I_C L/r | L ≪ λ, pair with CM current | 1 m, 3.6 µA, 100 MHz → 150 µV/m @ 3 m |

## Worked examples

**1. How much does a 20 mm trace radiate at 433 MHz?** If it carried a uniform 10 mA with the return
far away (a worst case — really a monopole-ish structure): l/λ0 = 0.02/0.692 = 0.029;
R_rad = 789 × 0.029² = 0.66 Ω; P = ½·0.01²·0.66 = 33 µW = −14.8 dBm. With a tight return path (a
microstrip over its ground, loop area ≈ 20 mm × 1.6 mm = 32 mm²) it is a small loop instead — use the
area form: R_rad = 31 171·(32×10⁻⁶)²/0.692⁴ ≈ 1.4×10⁻⁴ Ω, P ≈ 7 nW (−51 dBm). A 36 dB difference purely
from routing the return.

**2. Small-loop antenna efficiency at 433 MHz.** 3 cm diameter single-turn loop of 1 mm copper wire:
R_rad = 68 mΩ. Loss: R_s = 5.43 mΩ (433 MHz), R_loss = R_s·C/(2πb) = 5.43×10⁻³ × 0.0942/(2π×0.5×10⁻³)
= 0.163 Ω. Efficiency = 0.068/(0.068 + 0.163) = **29 % (−5.3 dB)**, before matching-network loss. A
wider strip or tube (larger b) and a larger loop help; this is why compact 433 MHz loop antennas in
key fobs are 10–20 dB below a dipole. See [loop antennas](../08-antennas/loop-antennas.md).

**3. Radiation from a charge oscillating in a wire (sanity check).** An LC tank current of 100 mA
at 100 MHz in a 5 mm lead (l/λ = 1.67×10⁻³): R_rad = 2.2 mΩ, P = ½(0.1)²(2.2×10⁻³) = 11 µW. Small but
detectable — which is why unshielded oscillators leak.

**4. Common-mode on a GNSS cable.** A 0.5 m antenna cable with 10 µA of CM current at 150 MHz (a
regulator harmonic): E at 3 m ≈ 1.257×10⁻⁶ × 1.5×10⁸ × 10⁻⁵ × 0.5/3 = 0.31 mV/m (70 dBµV/m) — far above
Class B limits at that frequency and more than enough to couple into nearby receivers.

## Practical notes
- Every RF-carrying structure radiates somewhat; EM simulators find it automatically, SPICE never does.
  If a matched circuit "loses" a few percent of power in simulation vs theory at UHF, radiation from
  electrically non-small loops is a suspect.
- For intended antennas, use full-wave tools (NEC-2 for wires, openEMS for PCB antennas); the Hertzian
  dipole is the building block (MoM codes literally sum short current segments like this).
- For EMC, the formulas above give order-of-magnitude estimates (±6 dB); resonant cable lengths
  (λ/4, λ/2) can radiate far more than the short-wire formula predicts.

## Common mistakes & misconceptions
- **"A steady DC current radiates a little."** No; radiation requires time-varying current
  (acceleration).
- **"Electrons emit the radio wave and it flies off the wire."** The radiation is the collective field
  of all charges' accelerations; individual electron motions are ~mm/s drifts with small oscillations.
- **Using 80π²(l/λ)² for a short open-ended dipole.** That's for uniform current; a real short dipole
  has triangular current → 20π²(l/λ)².
- **Mixing up E_r and E_θ in the near field.** Close in, E has a strong radial component (like a static
  dipole); only E_θ radiates.
- **"The near field is just a stronger version of the far field."** It's a different field: 1/r³ and
  1/r² terms, reactive, and E/H ≠ 377 Ω.
- **"Loops don't radiate."** Small loops radiate weakly (∝ (C/λ)⁴) but PCB current loops with fast
  edges and cables with CM current are the dominant EMC radiators.
- **Gaussian Larmor formula in SI** (missing 4πε0): errors of ~10¹¹.

## How to simulate / verify
- `python3 tools/verify/em_hertzian_dipole.py` — sympy derivation of the full dipole fields from A;
  symbolic radiated power and R_rad; 789.0 vs 789.6 Ω; Larmor ≡ ½I²R_rad; complex power 1 − j/(kr)³
  checked by numerical integration; wave impedance vs kr (electric and magnetic dipoles); small-loop
  R_rad; Paul's DM/CM constants and example currents.
- NEC-2 (e.g. via `necpp` or 4nec2): a λ/50 dipole with a single source segment reproduces
  R_rad ≈ 20π²(l/λ)² once the triangular current forms (enough segments).
- openEMS: a short dipole or small loop with an NF2FF box gives radiated power and pattern; compare with
  the formulas.

- Derivation of the scalar/dyadic Green's function, EFIE/MFIE and the MoM: [Green's functions and integral equations](greens-functions-and-integral-equations.md).
## Open questions / gaps
- FCC Part 15 Class B limits used for the EMC example are quoted from knowledge (19-regulations to
  confirm).
- Radiation from finite-length transmission lines with discontinuities (e.g. microstrip end effects)
  belongs to 03/13; not quantified here.

## Sources
1. D. J. Griffiths, *Introduction to Electrodynamics*, 4th ed., ch. 10 (potentials, gauges, retarded
   potentials, Jefimenko), ch. 11 (dipole radiation, Larmor formula §11.2.1). (textbook)
2. C. A. Balanis, *Antenna Theory*, 4th ed., 2016, ch. 3 (vector potentials, radiation integrals),
   §4.2 (infinitesimal dipole: fields, power, R_rad, directivity, reactive power 1 − j/(kr)³), §4.3
   (small dipole), §5.2 (small loop). (textbook)
3. R. F. Harrington, *Time-Harmonic Electromagnetic Fields*, 1961/2001, ch. 2 (potentials, radiation
   from a current element), ch. 3 (duality, equivalence). (textbook; chapter-level citation)
4. C. R. Paul, *Introduction to Electromagnetic Compatibility*, 2nd ed., Wiley 2006, §8.1 (simple
   emission models for differential- and common-mode currents; constants 1.316×10⁻¹⁴ and 1.257×10⁻⁶).
   (textbook; constants reproduced from first principles in the script)
5. H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley 2009, ch. 12 (digital circuit
   radiation: differential- and common-mode emission, ground-plane factor 2). (textbook; cited from
   knowledge)
6. E. M. Purcell and D. J. Morin, *Electricity and Magnetism*, 3rd ed., Cambridge 2013, Appendix H
   (radiation by an accelerated charge — field-line kink picture). (textbook; cited from knowledge)
7. J. D. Jackson, *Classical Electrodynamics*, 3rd ed., §9.1–9.3 (radiation from localized oscillating
   sources, electric and magnetic dipole fields). (textbook)
