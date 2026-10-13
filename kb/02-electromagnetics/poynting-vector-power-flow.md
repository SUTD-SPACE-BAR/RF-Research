---
title: Poynting vector, energy flow and field strength
domain: 02-electromagnetics
slug: poynting-vector-power-flow
tags: [poynting, energy, power-density, field-strength, complex-power, reactive-power, energy-flow-in-circuits, dBuV/m, EIRP, radiation-pressure]
prerequisites: [maxwells-equations.md, wave-equation-plane-waves-polarization.md, electromagnetic-units-and-constants.md]
related: [near-field-far-field.md, radiation-from-currents-hertzian-dipole.md, inductance-capacitance-from-fields.md, ../09-propagation-link-budget/friis-free-space-path-loss.md, ../19-regulations-safety/rf-exposure-safety.md, ../01-circuit-theory/energy-storage-and-reactive-power.md, ../03-transmission-lines-matching/coax-and-cables.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Poynting vector, energy flow and field strength

## Questions this page answers
- What is the Poynting vector and what does it physically represent?
- How do I convert between transmitted power, power density (W/m²) and field strength (V/m, dBµV/m)?
- What field strength does my 2 W 433 MHz transmitter produce at 1 km, 10 km or 30 km?
- Does electrical energy flow *inside* the copper wire or in the space around it?
- In a coax cable, where exactly is the power flowing?
- What is reactive power in field terms, and how does the "complex Poynting theorem" relate to impedance?
- Why can't I use S = E²/377 right next to my antenna?

## TL;DR
- **Instantaneous Poynting vector S = E × H** (W/m²) is the local rate of electromagnetic energy flow per unit area. **Poynting's theorem**: power flowing into a closed surface = rate of increase of stored field energy + power dissipated (J·E) inside [1][2][3].
- **Time-average (phasor, peak amplitudes): ⟨S⟩ = ½ Re{E × H*}**. Plane wave: ⟨S⟩ = E²_rms/η = |E_pk|²/(2η).
- **Field strength from EIRP (far field, free space): S = EIRP/(4πr²), E_rms = √(η0 S) = √(30·EIRP)/r**. 2 W isotropic at 1 km → 7.74 mV/m (77.8 dBµV/m); 2 W into a dipole (3.3 W EIRP) at 30 km → 0.33 mV/m (50.4 dBµV/m). Verified in `tools/verify/em_plane_waves.py`.
- **Energy in circuits flows through the fields around and between the conductors, not through the metal.** Conductors guide the fields and absorb a little energy through their surfaces (their I²R loss). In a coax, all the power flows in the dielectric; 59 % of it within the inner half of the gap of an RG-58-like line. In a resistive wire, S points radially *into* the wire and its surface integral equals I²R exactly (`tools/verify/em_poynting.py`) [4][5][6].
- **Complex Poynting theorem**: ½∮(E×H*)·dS inward = P_loss + 2jω(W_m − W_e) — the field basis of Z = R + jX; reactive power is energy sloshing between E and H storage.
- **S = E²/η0 only applies in the far field.** In the reactive near field (r < λ/2π ≈ 11 cm at 433 MHz) E/H ≠ 377 Ω and the "power density" formula misleads (see [near field](near-field-far-field.md)).

## Intuition (no math)
Energy in an electromagnetic system is stored in the fields: ½εE² per cubic metre in the
electric field and ½μH² in the magnetic field. When both fields are present *and crossed*, energy
moves, in the direction of E × H. A plane wave from an antenna is the obvious case. The less
obvious case is an ordinary circuit: the battery's E-field (from surface charges on the wires) and
the current's H-field (circling the wires) are crossed in the space around the wires, so energy
streams from the battery through the surrounding space to the load. The wires are like rails that
steer this flow; the energy enters the load (and, slightly, the wires themselves) through their
surfaces.

This is not a philosophical nicety for RF engineers — it is how a transmission line works. The
signal in a coax *is* the field between the conductors; the electrons in the copper creep along at
micrometres per second and merely carry the surface currents that terminate the magnetic field.
That is why the dielectric (not the copper) sets the propagation speed, why a microstrip's energy
lives partly in the air above it, and why anything placed in the fringing field near a trace
interacts with the signal.

## The math

### Level 1 — definitions and plane-wave relations

$$\mathbf S(t) = \mathbf E(t)\times\mathbf H(t)\quad[\mathrm{W/m^2}],\qquad \langle\mathbf S\rangle = \tfrac12\mathrm{Re}\{\mathbf E\times\mathbf H^*\}\ \ (\text{peak phasors}).$$

Energy densities (J/m³, linear isotropic media): w_e = ½ε|E|², w_m = ½μ|H|² (instantaneous);
time-averages with peak phasors ¼ε|E|² and ¼μ|H|².

Plane wave in a lossless medium of impedance η: E ⟂ H, |E| = η|H|, and
$$\langle S\rangle = \frac{|E_\text{pk}|^2}{2\eta} = \frac{E_\text{rms}^2}{\eta} = \eta H_\text{rms}^2,\qquad E_\text{rms} = \sqrt{\eta\,\langle S\rangle}.$$
Energy velocity = ⟨S⟩/⟨w⟩ = 1/√(με) = v_p (for a plane wave in a lossless, non-dispersive
medium, and w_e = w_m on average).

**Isotropic source in free space:** power spreads over 4πr², so
$$S = \frac{P_t G_t}{4\pi r^2} = \frac{\mathrm{EIRP}}{4\pi r^2},\qquad E_\text{rms} = \sqrt{\frac{\eta_0\,\mathrm{EIRP}}{4\pi r^2}} = \frac{\sqrt{29.98\cdot\mathrm{EIRP}}}{r}\approx\frac{\sqrt{30\,\mathrm{EIRP}}}{r}.$$
Units: P in W, r in m, E in V/m. For received power see
[Friis](../09-propagation-link-budget/friis-free-space-path-loss.md) and the dBµV/m ↔ dBm conversion in
[units & constants](electromagnetic-units-and-constants.md).

### Level 1½ — field strength from power, algebra only
- **Spread the power over a sphere.** A source of EIRP P gives $S = P/(4\pi r^2)$ W/m² at distance r.
- **Turn power density into field.** In free space $E = \eta_0 H$ with η0 ≈ 377 Ω, and $S = E_{rms}^2/\eta_0$. So $E_{rms} = \sqrt{377\,S}$, which simplifies to $\sqrt{30P}/r$.
- **Turn field back into received power.** An antenna of gain G collects $S\cdot G\lambda^2/(4\pi)$. Putting the three steps together gives the Friis equation.

*Worked number (verified, `tools/verify/s18b_level15_numbers.py`).* 1 W EIRP at 1 km gives S = 1/(4π × 10⁶) = **79.6 nW/m²**. Then $E_{rms}$ = √(377 × 79.6 × 10⁻⁹) = **5.48 mV/m** (74.8 dBµV/m) and H = 14.5 µA/m. At 433 MHz an isotropic antenna has λ²/4π = 0.0381 m², so it receives 3.0 nW = **−55.2 dBm**. The FSPL formula gives the same: 30 − (32.45 + 20 log 433) = −55.2 dBm.

### Level 2 — Poynting's theorem (derivation)

Start from Faraday and Ampère–Maxwell in linear, non-dispersive media. Dot the first with **H**,
the second with **E**, subtract, and use the identity ∇·(**E**×**H**) = **H**·(∇×**E**) −
**E**·(∇×**H**):
$$\nabla\cdot(\mathbf E\times\mathbf H) = -\mathbf H\cdot\frac{\partial\mathbf B}{\partial t} - \mathbf E\cdot\frac{\partial\mathbf D}{\partial t} - \mathbf E\cdot\mathbf J.$$
With **B** = μ**H**, **D** = ε**E**: **H**·∂**B**/∂t = ∂(½μH²)/∂t, and similarly for E. Integrate over
a volume V with surface ∂V:
$$\boxed{-\oint_{\partial V}(\mathbf E\times\mathbf H)\cdot d\mathbf S = \frac{d}{dt}\int_V\left(\tfrac12\varepsilon E^2 + \tfrac12\mu H^2\right)dV + \int_V\mathbf E\cdot\mathbf J\,dV}$$
Power flowing in through the surface = rate of increase of stored energy + power delivered to
charges (Joule heating σE², or work done *on* a source if **E**·**J** < 0 — a battery or an antenna
feed pumps energy *out*, so there **E**·**J** is negative).

**Time-harmonic (complex) Poynting theorem.** With peak phasors, using the conjugate of
Ampère–Maxwell:
$$-\tfrac12\oint(\mathbf E\times\mathbf H^*)\cdot d\mathbf S = \underbrace{\tfrac12\int\sigma|E|^2dV + \tfrac{\omega}{2}\int(\varepsilon''|E|^2+\mu''|H|^2)dV}_{P_\text{loss}} + 2j\omega\underbrace{\int\left(\tfrac14\mu'|H|^2 - \tfrac14\varepsilon'|E|^2\right)dV}_{W_m - W_e}.$$
Applied to a one-port network with port current I (peak), the left side is ½VI* = ½Z|I|², so
$$Z_\text{in} = \frac{P_\text{loss} + 2j\omega(W_m - W_e)}{\tfrac12|I|^2}.$$
Resistance is set by dissipated (and radiated) power, reactance by the imbalance of stored magnetic
and electric energy. At resonance W_m = W_e and Z is real. Checked numerically for a series RLC in
`em_poynting.py`. This is also the rigorous basis for radiation resistance
(P_rad = ½I²R_rad, see [radiation](radiation-from-currents-hertzian-dipole.md)) and for Q
(Q = ω·W_stored/P_loss, see [cavities](waveguides-and-cavity-resonators.md) and
[resonance](../01-circuit-theory/resonance-and-q.md)).

(With dispersive media the energy-density terms need the Brillouin form
w_e = ¼ d(ωε')/dω |E|²; the loss terms are unchanged. Jackson §6.8 [3].)

### Level 2 — where the energy flows in real circuits

**(a) Coaxial line.** TEM fields between inner radius a and outer radius b: E_r = V/(r ln(b/a)),
H_φ = I/(2πr). The Poynting vector S_z = E_rH_φ = VI/(2πr² ln(b/a)) is purely axial and exists only
in the dielectric. Integrating over the annulus:
$$\int_a^b\frac{VI}{2\pi r^2\ln(b/a)}2\pi r\,dr = VI.$$
The circuit power VI is *entirely* the field flux (checked to 10⁻⁹ in `em_poynting.py` for an
RG-58-like geometry, a = 0.45 mm, b = 1.47 mm, εr = 2.25, Z0 = 47.3 Ω). Because S ∝ 1/r², the flow is
concentrated near the inner conductor: 15 % within the first 0.09 mm, 59 % inside r = 2a. That is also
where the E-field peaks (18 kV/m at the inner-conductor surface for 1 W; 183 kV/m for 100 W),
which sets the voltage breakdown and multipaction limits of a cable.

**(b) A resistive wire (DC or low frequency).** Inside a wire of conductivity σ carrying I, the
axial field is E_z = J/σ; by continuity of tangential E it exists just outside the surface too.
H_φ = I/(2πa) at the surface. So S = E × H points **radially inward** with magnitude E_zH_φ; the flux
through the surface of length L is (J/σ)(I/2πa)(2πaL) = I²L/(σπa²) = I²R. The energy dissipated in
the wire enters it *sideways* from the surrounding field — checked in `em_poynting.py` (10 A in a
1 mm Cu wire: 699 W/m² inward, 2.195 W per metre = I²R).

**(c) Two-wire line feeding a load.** Around a pair of wires the surface charges create an E-field
between them and the currents create an H-field circling them; S points along the line from source
to load, mostly in the region between and near the wires. For a DC pair of thin wires 2 cm apart
(`em_poynting.py`, geometry of Boulé [5]): 77 % of the transported power flows within 1.2 cm of the
line centre, 93 % within 2 cm, 98 % within 4 cm. Boulé shows analytically that for perfect
conductors the longitudinal flux equals the battery power, and that for resistive wires the
transported flux decreases along the line by exactly the power entering the wire surfaces [5].
Davis & Kaplan compute the full 3-D flow for a circular loop circuit, including non-zero S outside
the loop [6].

**(d) Microstrip and PCB traces.** Energy flows in the dielectric under the trace *and* in the air
above it; the split sets ε_eff (quasi-TEM). Anything placed in the fringing field (a finger, a
nearby trace, a radome wall) sits in the energy flow and couples to it. See
[planar lines](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md).

### Level 3 — subtleties

**Non-uniqueness.** Only the *closed-surface integral* of S is fixed by Poynting's theorem; one can
add the curl of any vector field to S without changing it. The E × H form is the conventional (and
relativistically natural) choice and agrees with momentum density g = S/c². In purely static
configurations (a charge next to a bar magnet) E × H circulates in closed loops with zero net flux —
it represents stored angular momentum of the field, not energy transport (Feynman Vol. II ch. 27
[7]). Treat local S as physically meaningful but don't over-interpret circulating static flows.

**Transient energy flow (the "Veritasium" question).** A 2021 video posed: a battery, switch and lamp
connected by two wires each light-seconds long, the lamp 1 m from the switch — when does the lamp
light? The field picture says some energy arrives after ≈ (1 m)/c, carried across the gap by the
field launched when the switch closes. What reaches the lamp that early is set by the capacitive
and inductive coupling between the two ends of the wire pair — the pair acts as a transmission line
with impedance of a few hundred ohms — and it is only a fraction of the final steady-state power.
Full power arrives only after waves have travelled the length of the wires and back. Both "1 m/c"
and "the wire length/c" are right for different fractions of the power; the popular debate mostly
came from not stating which quantity was meant. (Physics: standard transmission-line transients;
treatment of the specific geometry: forum/video debate, *unverified — forum*, but consistent with
[5][6].)

**Momentum and radiation pressure.** A plane wave carries momentum density S/c²; normal incidence
on a perfect absorber gives pressure ⟨S⟩/c, on a perfect reflector 2⟨S⟩/c. 1 kW/m² → 3.3 µPa —
negligible for RF hardware.

**Power flow in lossy media and conductors.** In a good conductor, the time-average Poynting flux
into the surface per unit area is ½R_s|H_t|² (R_s = 1/(σδ)), the basis of all conductor-loss
calculations (see [skin effect](skin-effect-conductor-loss-roughness.md)).

**Field-strength units.** Regulations and datasheets quote: V/m, dBµV/m, µV/m, A/m, W/m², mW/cm²
(= 10 W/m²), dBm/m². Conversions (far field): dBm/m² = dBµV/m − 115.76; E [V/m] = √(377·S [W/m²]);
S [mW/cm²] = E²/3770. EMC limits (CISPR, FCC Part 15) are quasi-peak or average dBµV/m at 3 m or
10 m — measured with an antenna factor, not computed from these formulas.

## Design equations & rules of thumb

| Equation | When valid | Typical value |
|---|---|---|
| ⟨S⟩ = ½Re{E×H*} | always (peak phasors) | — |
| S = E²_rms/η0 | far field, free space | 1 V/m → 2.65 mW/m² |
| E_rms = √(30 EIRP)/r | far field, free space | 2 W, 1 km → 7.74 mV/m |
| E[dBµV/m] = EIRP[dBm] − 20 log r[km] + 44.77 | far field | 33 dBm at 1 km → 77.8 dBµV/m |
| P_coax = ∫S dA = VI | TEM line | — |
| Surface-loss flux = ½R_s|H_t|² | good conductor | Cu 433 MHz R_s = 5.4 mΩ |
| Z = [P + 2jω(W_m−W_e)]/(½|I|²) | any one-port | resonance ⇔ W_m = W_e |
| Radiation pressure = S/c | absorber | negligible at RF |

(The 44.77 dB constant: E[dBµV/m] = 20 log₁₀(√(29.98·EIRP_W)/r_m) + 120 = 14.77 + (EIRP_dBm − 30)
− (20 log r_km + 60) + 120 = EIRP_dBm − 20 log r_km + 44.77.)

## Worked examples

**1. 2 W LoRa (EBYTE E22-400T33D, 33 dBm) at 1 km.** Isotropic: S = 2/(4π·10⁶) = 1.59×10⁻⁷
W/m²; E = √(376.73 × 1.59×10⁻⁷) = **7.74 mV/m rms = 77.8 dBµV/m**; H = E/η0 = 20.6 µA/m. With a
2.15 dBi dipole: 9.92 mV/m (79.9 dBµV/m). (Script values.)

**2. The same link at 30 km apogee range.** E = √(30·3.28)/30 000 = **0.33 mV/m (50.4 dBµV/m)**.
A ground dipole (G = 2.15 dBi, A_e = Gλ²/4π = 0.0625 m² at 433 MHz) collects
P = S·A_e = 2.9×10⁻¹⁰·0.0625 = 1.8×10⁻¹¹ W = **−77.4 dBm**, the free-space Friis result; LoRa
sensitivity at SF12/125 kHz is ≈ −137 dBm (Semtech SX127x/SX126x class, cited from knowledge), so ~60 dB of margin before fading, pattern nulls and
polarization loss (see [LoRa link budget](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md)).

**3. Is 1 W at 10 km "a lot" of field?** 1 W EIRP → 0.548 mV/m (54.8 dBµV/m); check with the dB
formula: 30 dBm − 20 + 44.77 = 54.8 dBµV/m. For comparison, FM-broadcast protected service contours
are of order 0.5–1 mV/m (54–60 dBµV/m) (cited from knowledge; regulatory context in
19-regulations-safety).

**4. RF exposure next to the ground station.** 2 W into a 2.15 dBi antenna, observer at 0.2 m:
far-field formula gives S = 6.5 W/m² (0.65 mW/cm²), E = 50 V/m. But at 433 MHz, r/(λ/2π) = 1.8 —
the observer is at the edge of the reactive near field, so the plane-wave power density is only an
estimate (usually conservative for E, not always for H). At 1 m, S = 0.26 W/m², far below the
ICNIRP 2020 general-public whole-body reference level of f/200 = 2.2 W/m² at 433 MHz (400–2000 MHz
band; cited from knowledge — definitive treatment in
[RF exposure safety](../19-regulations-safety/rf-exposure-safety.md)).

**5. Power flow in 50 Ω coax at 100 W.** For the RG-58-like geometry (Z0 = 47.3 Ω): V_pk = √(2PZ0)
= 97 V; E at the inner conductor = V/(a ln(b/a)) = 183 kV/m (1.8 kV/cm) — far below the ~30 kV/cm
breakdown of air and far below PE's dielectric strength, so RG-58's power limit is thermal (conductor
+ dielectric loss heating), not voltage.

## Practical notes
- A "field strength meter" or SDR with a calibrated antenna measures dBµV/m via the antenna factor;
  use it to check EIRP of a telemetry transmitter against the prediction in example 1 (at a range
  ≥ several wavelengths and ≥ 2D²/λ, clear of reflections — see
  [antenna ranges](../17-test-measurement/antenna-range-ota-testing.md)).
- In a PCB, the Poynting picture tells you where not to put things: the energy of a microstrip flows
  in a region roughly 3× the trace width either side and a few substrate heights above. Keep
  radomes, enclosures, cables and fingers out of that region, or account for them.
- Cable heating and connector power ratings follow from where the loss flux enters: mostly the
  inner conductor (highest H, smallest surface) — which is why inner conductors run hot.

## Common mistakes & misconceptions
- **"Electrons carry the energy down the wire at nearly light speed."** Drift velocity is ~0.1 mm/s.
  The signal and energy travel in the fields at c/√εr,eff; electrons only carry the surface currents
  and charges that shape the fields. (Common forum confusion; physics per [2][4][5].)
- **"Energy flows *only* outside the wire, so the wire doesn't matter."** The wire's surface
  charges and currents *create and guide* the field. And the wire's own dissipation enters it
  radially; inside a resistive conductor S is not zero — it points inward.
- **"The Poynting vector tells me exactly where each joule goes."** Only closed-surface integrals are
  unambiguous; circulating static flows carry no net energy.
- **Using S = P/(4πr²) in the near field** (hand-held radios, on-board antennas): E/H is not 377 Ω
  there; exposure standards require separate E and H assessment or simulation.
- **Peak vs rms**: ⟨S⟩ = E²_pk/(2η) = E²_rms/η. Mixing them gives 3 dB errors.
- **Adding power densities of two coherent waves.** Two coherent waves add in *field*, so power
  densities can double or cancel (standing waves, multipath). Only incoherent/averaged signals add
  in power.

## How to simulate / verify
- `python3 tools/verify/em_poynting.py` — coax flux integral = VI; distribution across the gap; DC
  wire inward flux = I²R; two-wire DC line power-within-radius; complex Poynting theorem vs series RLC
  impedance; exposure-style numbers.
- `python3 tools/verify/em_plane_waves.py` — EIRP → S → E tables (section 4).
- openEMS: record E and H dumps on a plane cutting a microstrip; integrate ½Re(E×H*) over the plane
  and compare with the port power — a good sanity check of a simulation's energy bookkeeping.

## Open questions / gaps
- The quantitative early-time power reaching the lamp in the "Veritasium" geometry depends on the
  exact geometry; not computed here (a good openEMS exercise for 16-simulation-tools).
- ICNIRP 2020 reference levels quoted from knowledge; 19-regulations-safety should confirm.

## Sources
1. D. J. Griffiths, *Introduction to Electrodynamics*, 4th ed., 2013, §8.1 (Poynting's theorem),
   Example 8.1 (power into a resistive wire). (textbook)
2. S. Ramo, J. R. Whinnery, T. Van Duzer, *Fields and Waves in Communication Electronics*, 3rd ed.,
   1994, ch. 3 (Poynting theorem, energy flow in circuits and in coaxial lines, complex Poynting
   theorem and circuit impedance). (textbook)
3. J. D. Jackson, *Classical Electrodynamics*, 3rd ed., 1999, §6.7–6.8 (Poynting's theorem, harmonic
   fields, definitions of impedance and admittance from fields; dispersive energy densities). (textbook)
4. R. F. Harrington, *Time-Harmonic Electromagnetic Fields*, 1961/2001, §1-10–1-11 (complex power,
   complex Poynting theorem, input impedance). (textbook)
5. M. Boulé, "DC power transported by two infinite parallel wires," *Am. J. Phys.* 92(1), 14–22 (2024);
   arXiv:2305.11827. (peer-reviewed)
6. B. S. Davis and L. Kaplan, "Poynting vector flow in a circular circuit," *Am. J. Phys.* 79, 1155
   (2011); arXiv:1207.2173. (peer-reviewed)
7. R. P. Feynman et al., *Feynman Lectures on Physics* Vol. II, ch. 27 ("Field energy and field
   momentum", §27-5 examples of energy flow: charging capacitor, resistive wire, charge + magnet).
   (textbook, free online; cited from knowledge)
8. D. M. Pozar, *Microwave Engineering*, 4th ed., §1.6 (energy and power, complex Poynting theorem),
   §2.2 (field analysis of transmission lines — coax power flow). (textbook)
9. ICNIRP, "Guidelines for limiting exposure to electromagnetic fields (100 kHz to 300 GHz),"
   *Health Physics* 118(5):483–524, 2020, Table 5 (general-public reference levels). (standard;
   bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
10. Veritasium, "The Big Misconception About Electricity," YouTube, Nov 2021, and follow-up
    discussion threads (EE/Physics Stack Exchange, Reddit). (video/forum — used only for the
    misconception, not for physics)
