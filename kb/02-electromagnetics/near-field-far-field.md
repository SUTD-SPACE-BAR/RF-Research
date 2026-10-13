---
title: Near field and far field — reactive, radiating (Fresnel) and Fraunhofer regions
domain: 02-electromagnetics
slug: near-field-far-field
tags: [near-field, far-field, reactive-near-field, fresnel-region, fraunhofer, 2D2-over-lambda, wave-impedance, antenna-measurement, shielding, coupling, NFC, EMC]
prerequisites: [radiation-from-currents-hertzian-dipole.md, poynting-vector-power-flow.md]
related: [../08-antennas/antenna-measurement.md, ../17-test-measurement/antenna-range-ota-testing.md, ../13-pcb-rf-layout-emc/shielding-and-isolation.md, ../13-pcb-rf-layout-emc/emc-emi-fundamentals.md, ../09-propagation-link-budget/friis-free-space-path-loss.md, ../19-regulations-safety/rf-exposure-safety.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Near field and far field — reactive, radiating (Fresnel) and Fraunhofer regions

## Questions this page answers
- Where does an antenna's near field end and its far field begin?
- What do λ/2π, 0.62√(D³/λ) and 2D²/λ mean, and which applies to my antenna?
- How far away must I be to measure an antenna's gain or pattern correctly?
- What is "wave impedance", and why are magnetic near fields hard to shield?
- Why does Friis' formula fail when two antennas are close?
- Why does my radio detune when I put it near the rocket body or my hand?

## TL;DR
- **Reactive near field**: stored (non-radiating) energy dominates. For small antennas, **r < λ/2π** (0.159λ): **11 cm at 433 MHz, 5.2 cm at 915 MHz, 3.0 cm at 1575 MHz**. For electrically large antennas the usual boundary is **r < 0.62√(D³/λ)** [1].
- **Radiating near field (Fresnel region)**: 0.62√(D³/λ) < r < 2D²/λ — fields radiate but the pattern still changes with distance.
- **Far field (Fraunhofer)**: **r > 2D²/λ** (and r ≫ D, r ≫ λ). At 2D²/λ the path-length difference across the aperture gives a **22.5° (π/8) phase error**, and a uniformly illuminated circular aperture's on-axis gain is only **0.06 dB** low; at D²/λ it's 0.22 dB, at 0.5D²/λ 0.9 dB (`tools/verify/em_nearfield.py`) [1][2].
- Examples: 1 m 915 MHz Yagi → far field beyond **6.1 m**; 5.8 GHz 0.3 m dish → **3.5 m**; 24 GHz 5 cm radar array → **0.4 m**; a GNSS patch on a 7 cm ground plane → a few cm, but the λ/2π and "r ≫ λ" conditions push it to ≳ 0.5–1 m.
- **Wave impedance** Z_w = |E|/|H|: electric (dipole-like, high-impedance) sources ≈ η0/(kr) close in (e.g. 3.7 kΩ at kr = 0.1); magnetic (loop-like, low-impedance) ≈ η0·kr (38 Ω at kr = 0.1). Both approach 377 Ω, within 10 % by r ≈ λ/2 and within 1 % by r ≈ 1.6λ. The exact dipole curves overshoot (E-source dips to 257 Ω near kr ≈ 1.2; H-source peaks at 553 Ω) — popular monotonic sketches are approximate.
- **Shielding in the near field**: reflection loss of a metal sheet ∝ |Z_w|/|Z_s|: for a 1 MHz magnetic source 1 cm away, copper's reflection loss is ~35 dB vs 108 dB for a plane wave — low-frequency magnetic fields must be absorbed (thick/high-μ material) rather than reflected [3].

## Intuition (no math)
Close to any antenna, most of the field energy just sloshes back and forth between the antenna and the
space around it every cycle — like the field around a capacitor or inductor. That's the reactive
near field; it falls off fast (1/r² and 1/r³). A little of the energy detaches and leaves as a wave
(1/r). At about a sixth of a wavelength from a small antenna the two are equal; beyond a wavelength
or so, the outgoing wave dominates.

For a big antenna (a dish, a long Yagi, an array) there's a second effect: from nearby, different
parts of the antenna are at noticeably different distances from you, so their contributions don't add
with the phases they will have far away. The beam isn't "formed" yet. Only when you're far enough that
all parts are nearly equidistant (to within λ/16) does the pattern stop changing shape with distance —
that's 2D²/λ.

Anything placed in the reactive near field (a hand, a rocket's airframe, a battery, a metal bracket,
another antenna) interacts with the stored energy and changes the antenna's impedance and pattern.
Objects in the far field only scatter and block.

## The math

### Level 1 — the boundaries

| Region | Criterion | Physics |
|---|---|---|
| Reactive near field | r < λ/2π (small antennas); r < 0.62√(D³/λ) (large, D > λ) | 1/r², 1/r³ terms; E, H in quadrature; stored energy ≫ radiated |
| Radiating near field (Fresnel) | 0.62√(D³/λ) < r < 2D²/λ | radiation dominates but angular pattern depends on r |
| Far field (Fraunhofer) | r > 2D²/λ, r ≫ D, r ≫ λ | pattern independent of r; E ⟂ H ⟂ r̂; E/H = η; S ∝ 1/r² |

D is the largest dimension of the antenna (the aperture diameter, the length of a Yagi boom or of
the element, or of the antenna *plus the currents it excites on its ground plane or feed cable*).

**Boundary distances** (script):

| Antenna | λ | λ/2π | 0.62√(D³/λ) | 2D²/λ |
|---|---|---|---|---|
| 433 MHz λ/2 dipole (D = 0.35 m) | 69 cm | 11 cm | 15 cm | 35 cm |
| 433 MHz Yagi, D = 1 m | 69 cm | 11 cm | 75 cm | 2.9 m |
| 915 MHz Yagi, D = 1 m | 33 cm | 5.2 cm | 1.1 m | 6.1 m |
| 1575 MHz patch on 70 mm ground | 19 cm | 3.0 cm | 2.6 cm | 5.1 cm |
| 2.45 GHz 4×4 patch array, 0.25 m | 12 cm | 1.9 cm | 22 cm | 1.0 m |
| 5.8 GHz 0.3 m dish | 5.2 cm | 0.8 cm | 45 cm | 3.5 m |
| 24 GHz radar array, 5 cm | 1.25 cm | 0.2 cm | 6.2 cm | 40 cm |
| 77 GHz radar antenna, 2 cm | 0.39 cm | 0.06 cm | 2.8 cm | 20 cm |

For small antennas (D ≲ λ/2) the 2D²/λ criterion is *smaller* than λ/2π or than a wavelength, so the
binding conditions are kr ≫ 1 and r ≫ λ; a practical minimum is r ≳ 2–3λ for pattern work and
≳ 10λ for accurate gain (field-amplitude error of the 1/r² and 1/r³ terms is < 1 % beyond ~1.6λ — script
section 6).

### Level 2 — where 2D²/λ comes from

A point P at distance r on the axis of an aperture of diameter D sees the aperture edge at distance
√(r² + (D/2)²) ≈ r + D²/(8r). The extra phase is
$$\Delta\phi = \frac{kD^2}{8r} = \frac{\pi D^2}{4\lambda r}.$$
Setting Δφ = π/8 (22.5°, i.e. path difference λ/16) gives r = 2D²/λ. The effect on measured gain for a
uniformly illuminated circular aperture (Fresnel approximation, on-axis) is
$$\frac{G(r)}{G_\infty} = \left[\frac{\sin(x/2)}{x/2}\right]^2,\qquad x = \frac{\pi D^2}{4\lambda r},$$
giving −0.056 dB at 2D²/λ, −0.22 dB at D²/λ, −0.91 dB at 0.5D²/λ, −3.9 dB at 0.25D²/λ (script).
Tapered illuminations are less sensitive; sidelobes and nulls are *more* sensitive (null depths fill
in first). For low-sidelobe measurements ranges of 4–10 D²/λ or compact/near-field ranges are used
(see [antenna measurement](../08-antennas/antenna-measurement.md)).

The 0.62√(D³/λ) reactive boundary comes from requiring the next term in the distance expansion
(the cubic term) to be small (Balanis §2.2.4 [1]); it applies to antennas large compared with λ.

### Level 2 — wave impedance near electric and magnetic sources

From the Hertzian-dipole fields ([radiation page](radiation-from-currents-hertzian-dipole.md)), at
broadside:
$$Z_E = \frac{E_\theta}{H_\phi} = \eta\,\frac{1 + \frac{1}{jkr} - \frac{1}{(kr)^2}}{1 + \frac{1}{jkr}},\qquad Z_M = \frac{\eta^2}{Z_E}\ \text{(small loop, by duality)}.$$
Limits: |Z_E| → η/(kr) (high impedance, E-dominant) and |Z_M| → η·kr (low impedance, H-dominant) for
kr ≪ 1; both → η for kr ≫ 1.

| kr | r/λ | |Z_E| | |Z_M| |
|---|---|---|---|
| 0.05 | 0.008 | 7.5 kΩ | 19 Ω |
| 0.1 | 0.016 | 3.7 kΩ | 38 Ω |
| 0.5 | 0.080 | 608 Ω | 234 Ω |
| 1 | 0.159 | 266 Ω | 533 Ω |
| 2 | 0.32 | 304 Ω | 467 Ω |
| 5 | 0.80 | 362 Ω | 392 Ω |
| 10 | 1.59 | 373 Ω | 381 Ω |

Within 10 % of η0 beyond r ≈ 0.48λ (E) / 0.50λ (H); within 1 % beyond 1.6λ (script). Note the
overshoot around kr ≈ 1 (E-source minimum 257 Ω, H-source maximum 553 Ω): EMC textbooks often draw
monotonic curves meeting at λ/2π — a simplification.

Real sources are classified by their impedance: **high-impedance** (high voltage, low current —
open-ended traces, dipoles, heatsinks with dV/dt, switching nodes) produce E-dominant near fields;
**low-impedance** (high current — loops, inductors, power traces, transformer leakage) produce
H-dominant near fields.

### Level 3 — near-field shielding (Schelkunoff)

For a conducting sheet of surface impedance Z_s ≈ (1+j)R_s, the transmission-line model of shielding
gives reflection loss R ≈ 20 log₁₀(|Z_w|/4|Z_s|) dB plus absorption loss A = 8.686 t/δ dB (Schelkunoff;
Ott ch. 6 [3]). Because |Z_w| depends on the source type in the near field (script, copper):

| f | r | R (E source) | R (plane wave) | R (H source) |
|---|---|---|---|---|
| 1 MHz | 1 cm | 182 dB | 108 dB | 35 dB |
| 10 MHz | 1 cm | 152 dB | 98 dB | 45 dB |
| 100 MHz | 3 cm | 112 dB | 88 dB | 64 dB |
| 433 MHz | 5 cm | 87 dB | 82 dB | 77 dB |
| 1 GHz | 50 cm | 78 dB | 78 dB | 78 dB |

So electric near fields are trivially shielded by any thin conductor (even conductive paint), while
low-frequency magnetic fields leak through thin shields — absorption (thickness ≫ δ, or high-μ
material) or flux diversion is needed. In practice, apertures and seams, not the sheet, limit shielding
above ~100 MHz ([shielding](../13-pcb-rf-layout-emc/shielding-and-isolation.md)).

### Level 3 — consequences for coupling and link budgets

- **Friis' transmission formula assumes far field** for both antennas (plane-wave incidence, gain
  defined at infinity). Within ~2D²/λ or ~λ, coupling is governed by mutual impedance and can be far
  larger or smaller than Friis predicts. NFC/RFID at 13.56 MHz (λ/2π = 3.5 m) works entirely in the
  reactive near field — inductive coupling of two loops (mutual inductance, see
  [inductance](inductance-capacitance-from-fields.md)) falling as 1/r⁶ in power, not 1/r².
- **Power density and exposure**: S = E²/η0 only in the far field. In the reactive near field E and H
  must be evaluated separately (ICNIRP 2020 gives separate E and H reference levels and, close to a
  source, compliance must be shown for both — cited from knowledge; see
  [RF exposure](../19-regulations-safety/rf-exposure-safety.md)).
- **Near-field probing**: small loop probes sense H (current hot spots), stub/monopole probes sense E
  (voltage hot spots). Use them to find EMC sources on a flight-computer board.
- **Antennas near structures**: a 433 MHz whip within 11 cm of the airframe, battery pack or avionics
  bay is in its own reactive near field — expect detuning and pattern distortion; include those
  structures in simulation or tune in situ (see [antennas on rockets](../08-antennas/antennas-on-rockets.md)).

## Design equations & rules of thumb

| Equation | When valid | Typical value |
|---|---|---|
| r_reactive = λ/2π | small antennas | 433 MHz: 11 cm |
| r_reactive = 0.62√(D³/λ) | D ≫ λ | 915 MHz 1 m Yagi: 1.1 m |
| r_ff = 2D²/λ (+ r ≫ λ, r ≫ D) | pattern/gain measurement | 5.8 GHz 0.3 m dish: 3.5 m |
| Edge phase error = πD²/(4λr) | aperture | π/8 at 2D²/λ |
| On-axis gain error (uniform) = [sinc-like]² | finite range | −0.06 dB at 2D²/λ |
| |Z_E| ≈ η0/(kr), |Z_M| ≈ η0·kr | kr ≪ 1 | kr = 0.1: 3.7 kΩ / 38 Ω |
| |Z_w| within 1 % of η0 | r > 1.6λ | — |
| Reflection loss R = 20 log(|Z_w|/4|Z_s|) | thin metal shield | 1 MHz H-source 1 cm: 35 dB (Cu) |

## Worked examples

**1. Where to stand to measure a 915 MHz Yagi's gain.** D = 1 m: 2D²/λ = 6.1 m; r ≫ λ satisfied.
Use ≥ 6–10 m, antenna heights ≥ a few metres to keep the ground-reflection Fresnel zone clear (see
[Fresnel zones](../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md)). At 3 m the gain
reads ~0.2–0.4 dB low and nulls fill in.

**2. Testing the rocket's 433 MHz link on the bench.** Two modules 30 cm apart: kr = 2.7, just past
λ/2π but not "far": field amplitude within ~0.5 dB of the 1/r law (script section 6), but the
dipoles couple through their near fields and the path loss is ≈ 14.8 dB from Friis (20 log(4πr/λ)) —
far less than any flight distance; attenuators (≥ 60 dB) are needed to test sensitivity. For
repeatable results use ≥ 2 m (≈ 3λ) or a cabled test.

**3. Mm-wave radar lab test.** A 24 GHz array with D = 5 cm: far field beyond 40 cm; a corner
reflector target at 30 cm is in the radiating near field — the beam isn't formed and RCS/range
readings will be off. Test at ≥ 1 m.

**4. Shielding a switching regulator from the GNSS antenna.** The inductor's field at 1 cm is
H-dominant at 1 MHz (kr ≈ 2×10⁻⁴): a 35 µm copper can gives only ~35 dB reflection and ~5 dB absorption
(t/δ = 35/66 at 1 MHz → 4.6 dB). Place the regulator far from the antenna and orient/shield the
inductor (shielded inductors) rather than rely on a thin can; at the GNSS frequency itself (harmonics)
the same can works well.

## Practical notes
- The antenna's "D" includes currents on its ground plane or cable; a small patch on a big ground
  plane, or a monopole whose feed cable radiates, has a larger effective D.
- In simulations, NF2FF (near-to-far-field) transformation computes far-field patterns from fields on
  a closed box in the near field — you don't need a huge simulation volume (openEMS `CreateNF2FFBox`).
- Near-field ranges and planar scanners measure the radiating near field and transform to far field
  mathematically; they need phase and precise probe positioning.

## Common mistakes & misconceptions
- **"The far field starts at 2D²/λ for every antenna."** For small antennas the binding conditions are
  r ≫ λ/2π and r ≫ λ.
- **"Near field = stronger field."** It's a *different* field (reactive, non-plane-wave); its E/H ratio
  depends on the source.
- **"377 Ω everywhere."** Only in the far field of any source in free space.
- **Using Friis between antennas a wavelength apart.** Coupling there is mutual impedance, not Friis.
- **"A thin copper shield stops all fields."** Not low-frequency magnetic fields in the near field.
- **Measuring exposure with an E-field meter only, next to a loop antenna.** H can be far above what
  E/377 implies.

## How to simulate / verify
- `python3 tools/verify/em_nearfield.py` — boundary distances for Marcus's antennas; phase and on-axis
  gain error vs range; wave impedance vs distance (E and H sources) with 10 %/1 % convergence distances;
  Schelkunoff reflection loss for E/H/plane-wave sources; near-field error of far-field formulas.
- `python3 tools/verify/em_hertzian_dipole.py` section 5 — the underlying Z_w(kr) from the exact fields.
- openEMS: place E and H probes at increasing distance from a simulated dipole and plot |E|/|H|.

## Open questions / gaps
- ICNIRP near-field exposure assessment rules summarised only qualitatively; 19-regulations should
  state them.
- Mutual coupling vs distance for two 433 MHz dipoles (near-field regime) is an 08-antennas/NEC task.

## Sources
1. C. A. Balanis, *Antenna Theory*, 4th ed., 2016, §2.2.4 (field regions: reactive near field
   0.62√(D³/λ), radiating near field, far field 2D²/λ), §4.4 (region separation for a dipole). (textbook)
2. IEEE Std 149-2021 (Test procedures for antennas) — far-field criterion and range design (cited from
   knowledge; not read). (standard)
3. H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley 2009, ch. 6 (shielding: near-field vs
   far-field, wave impedance, reflection and absorption loss). (textbook; cited from knowledge)
4. C. R. Paul, *Introduction to Electromagnetic Compatibility*, 2nd ed., 2006, ch. 10 (shielding;
   near-field sources). (textbook)
5. S. A. Schelkunoff, "The impedance concept and its application to problems of reflection, refraction,
   shielding and power absorption," *Bell Syst. Tech. J.* 17(1), 17–48 (1938). (peer-reviewed; bibliographic data checked against
   Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
6. J. D. Kraus and R. J. Marhefka, *Antennas for All Applications*, 3rd ed., McGraw-Hill 2002, ch. 2
   (near and far fields). (textbook)
