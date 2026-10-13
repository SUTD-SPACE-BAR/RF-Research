---
title: Inductance and capacitance from fields — loop vs partial inductance, mutual inductance, standard geometries
domain: 02-electromagnetics
slug: inductance-capacitance-from-fields
tags: [inductance, capacitance, partial-inductance, loop-inductance, mutual-inductance, neumann-formula, ruehli, PEEC, coax, two-wire, wire-over-ground, microstrip, via-inductance, fringing, energy-method]
prerequisites: [maxwells-equations.md, poynting-vector-power-flow.md, quasi-static-vs-full-wave.md]
related: [skin-effect-conductor-loss-roughness.md, radiation-from-currents-hertzian-dipole.md, near-field-far-field.md, ../01-circuit-theory/transformers-coupled-inductors.md, ../03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md, ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md, ../04-real-components-hf/pcb-parasitics-traces-vias-pads.md, ../04-real-components-hf/package-parasitics-bondwires.md, ../13-pcb-rf-layout-emc/grounding-and-return-paths.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Inductance and capacitance from fields — loop vs partial inductance, mutual inductance, standard geometries

## Questions this page answers
- What *is* inductance and capacitance in terms of fields and stored energy?
- What is the inductance of a PCB trace, a via or a bond wire — and why do experts say that question is incomplete?
- What is the difference between loop inductance and partial inductance (Ruehli, Clayton Paul)?
- How do I compute mutual inductance between two loops or two wires?
- What are L and C per unit length of coax, a two-wire line, a wire over ground, a microstrip?
- How big is fringing capacitance, and when does the parallel-plate formula fail?
- Why does "1 nH/mm" come up so often, and when is it wrong?

## TL;DR
- **Energy definitions**: W_m = ½LI² and W_e = ½CV², with W_m = ½∫μ|H|²dV, W_e = ½∫ε|E|²dV (static/quasi-static). Equivalently **L = Φ/I** (flux linkage per ampere) and **C = Q/V** [1][2].
- **Inductance belongs to a closed current loop.** A "trace inductance" is only meaningful with its return path: the same 20 mm trace is ~6 nH as microstrip over a solid ground (h = 1.6 mm) but tens of nH if the return takes a detour.
- **Partial inductance** (Ruehli 1972; Paul 2010) assigns a unique self-partial L_p to each segment and a mutual partial M_p to each pair; **loop L = Σ L_p,i ± 2Σ M_p,ij**. It is the bookkeeping behind PEEC solvers and the "per-via" or "per-bond-wire" inductance numbers — valid only when summed around a loop [3][4].
- Round wire partial inductance: **L_p ≈ (μ0l/2π)[ln(2l/a) − 1]** (≈ 0.8–1.3 nH/mm for typical bond wires — the "1 nH/mm" rule). Verified in `tools/verify/em_inductance.py`, including an independent Neumann double integral (agrees within 1.4 %).
- **Via** (1.6 mm long, 0.3 mm dia): partial ≈ **0.69 nH**; the widely copied Johnson & Graham form with "+1" instead of "−1" gives 1.30 nH — about 2× larger. A signal via with a return via 1 mm away has **0.93 nH loop** inductance. For a via to a solid ground plane (a shunt ground in microstrip) the KB design value is Goldfarb–Pucel **≈0.54 nH** ([PCB parasitics](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md)) — which number applies depends on where the return current flows.
- **TEM lines**: coax L′ = (μ0/2π)ln(b/a), C′ = 2πε/ln(b/a); two-wire L′ = (μ0/π)acosh(D/2a); wire over ground L′ = (μ0/2π)acosh(h/a); always **L′C′ = με** (TEM). 50 Ω microstrip on 1.6 mm FR-4: **L′ ≈ 0.31 nH/mm, C′ ≈ 0.12 pF/mm**.
- **Fringing**: a strip over ground has 1.8× (w/h = 3), 2.2× (w/h = 1.9, i.e. 50 Ω), 3.0× (w/h = 1), 4.5× (w/h = 0.5) the parallel-plate capacitance (2-D finite-difference solve, matches Hammerstad–Jensen Z0 and ε_eff to < 0.4 %).
- **Mutual inductance** of coaxial loops: Maxwell's elliptic-integral formula (verified); two 5 cm-radius loops 5 cm apart: M = 24.7 nH.

## Intuition (no math)
An inductor stores energy in its magnetic field, a capacitor in its electric field. The inductance of a
circuit tells you how much magnetic energy (or flux) you get per ampere; the capacitance how much
electric energy (or charge) per volt. Nothing about "inductance" is attached to a component — it's a
property of the *whole field pattern* created by a current flowing around a closed path. A trace alone
carries no current unless something brings the current back, and the magnetic field (hence the energy)
lives mostly in the space between the trace and its return. Move the return further away and the
enclosed area — and inductance — grows.

Partial inductance is an accounting trick that lets us give each segment of a loop "its share", so that
we can compute complicated loops by adding up pieces. It works only as long as every piece is
eventually added into a complete loop, with the mutual terms between pieces. The "inductance of a
via" (≈ 0.5–1 nH) is such a share; the real behaviour depends on where the current returns.

Capacitance is similar but easier: charge and field lines end on conductors, and fringing fields around
the edges add capacitance beyond the simple "area over distance" picture — often doubling it for PCB
traces.

## The math

### Level 1 — definitions

| Definition | Formula | Notes |
|---|---|---|
| Self-inductance (flux) | L = Λ/I = N Φ/I | flux linkage through the loop |
| Self-inductance (energy) | L = 2W_m/I², W_m = ½∫μ|H|²dV | includes internal inductance |
| Mutual inductance | M₂₁ = Λ₂₁/I₁ = M₁₂ | reciprocity |
| Neumann formula | M = (μ0/4π)∮∮ d**l**₁·d**l**₂/R | filamentary loops |
| Capacitance | C = Q/V = 2W_e/V², W_e = ½∫ε|E|²dV | two conductors |
| Capacitance matrix | Q_i = Σ_j C_ij V_j | multi-conductor (Maxwell) |
| Coupling coefficient | k = M/√(L₁L₂) | 0 ≤ k ≤ 1 |

Units: L in henry (H = Wb/A = V·s/A), C in farad (F = C/V). Per-unit-length versions L′ (H/m), C′ (F/m)
for uniform lines (see [telegrapher's equations](../03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md)).

These are **quasi-static** definitions: they assume the structure is electrically small (see
[quasi-static vs full-wave](quasi-static-vs-full-wave.md)). At higher frequencies L and C of a
structure become frequency dependent (skin effect removes internal inductance; distributed effects
appear) and the right description is S-parameters or a transmission line.

### Level 2 — standard geometries (TEM lines)

Derivation pattern: apply Gauss/Ampère with symmetry, compute E and H, then Φ or W.

**Coax** (inner radius a, outer b): H = I/(2πr) ⇒ Φ′ = (μ0I/2π)ln(b/a) ⇒
**L′ = (μ0/2π)ln(b/a)**; E = V/(r ln(b/a)) ⇒ **C′ = 2πε/ln(b/a)**. RG-58-like (a 0.45, b 1.47 mm, PE
εr 2.25): L′ = 237 nH/m, C′ = 106 pF/m, Z0 = 47.3 Ω; the energy integrals reproduce these exactly
(script). At DC (uniform current) the inner conductor adds internal inductance μ0/8π = 50 nH/m (plus a
smaller outer-conductor term): 287 nH/m — the "L drops with frequency" effect of skin depth.

**Two-wire line** (radius a, centre spacing D): **L′ = (μ0/π)acosh(D/2a) ≈ (μ0/π)ln(D/a)**,
**C′ = πε/acosh(D/2a)**. 1 mm wire at 10 mm spacing: L′ = 1.20 µH/m, C′ = 9.3 pF/m, Z0 = 359 Ω.

**Wire over ground plane** (height h to centre, by image theory = half a two-wire line of spacing 2h):
**L′ = (μ0/2π)acosh(h/a)**, **C′ = 2πε/acosh(h/a)**. 1 mm wire 10 mm up: L′ = 738 nH/m (0.74 nH/mm).

**Parallel plates** (width w ≫ separation d): **L′ = μ0d/w**, **C′ = εw/d** — the basis of plane-pair
capacitance (a 100 × 50 mm FR-4 plane pair with 0.2 mm separation: C = 4.4ε0·5×10⁻³/0.2×10⁻³ ≈ 0.97 nF).

**TEM identity**: for any uniform TEM line in a homogeneous medium, **L′C′ = με** (script confirms
to 10⁻¹²); so knowing Z0 and the medium gives both: L′ = Z0√(μ_rε_r)/c, C′ = √(μ_rε_r)/(Z0c). For
quasi-TEM microstrip use ε_eff: a 50 Ω line on 1.6 mm FR-4 (w ≈ 3 mm, ε_eff ≈ 3.33):
**L′ = 0.31 nH/mm, C′ = 0.12 pF/mm**.

### Level 2 — fringing capacitance (verified with a field solver)

For a strip of width w a height h over a ground plane, the parallel-plate formula ignores field lines
leaving the strip's top and edges. A 2-D finite-difference Laplace solution (script section 5,
zero-thickness strip, Richardson-extrapolated in grid size) gives the air-case capacitance relative to
εw/h and the FR-4 (εr 4.4) Z0 and ε_eff, compared with the Hammerstad–Jensen closed forms [5]:

| w/h | C_air/C_pp (fringing factor) | Z0 FD | Z0 H–J | ε_eff FD | ε_eff H–J |
|---|---|---|---|---|---|
| 0.5 | 4.53 | 95.3 Ω | 95.5 Ω | 3.045 | 3.050 |
| 1.0 | 2.99 | 70.9 Ω | 71.0 Ω | 3.160 | 3.168 |
| 1.9 | 2.17 | 50.1 Ω | 50.2 Ω | 3.317 | 3.329 |
| 3.0 | 1.81 | 37.3 Ω | 37.5 Ω | 3.454 | 3.468 |

Two lessons: (1) for typical PCB traces the fringing field carries *half or more* of the capacitance —
pad and trace capacitance estimates from εA/d are low by ~2×; (2) a simple home-made solver agrees with
the standard closed forms to < 0.4 %, a useful sanity check of both. For a small pad (finite in both
directions) fringing is larger still. A 1 mm × 1 mm pad over ground 0.2 mm away: εA/d = 0.19 pF, and
with ~1.3–1.5× fringing (w/h = 5, edges on four sides; estimate) ≈ 0.25–0.3 pF.

### Level 3 — loop vs partial inductance

**Neumann's formula** gives the mutual inductance between two closed filamentary loops. Self-inductance
of a real wire loop follows by taking one path along the wire axis and the other along its surface
(external inductance) plus internal inductance.

**Partial inductance** (Ruehli [3]; Paul [4]): break each loop into straight segments. Define the
self-partial inductance of segment i as the flux from its current (extended to infinity) through the
area between the segment and infinity, and the mutual-partial M_ij similarly. For straight segments the
Neumann integral can be done analytically:
- Round wire, length l, radius a (surface current): L_p = (μ0/2π)[l ln((l + √(l² + a²))/a) − √(l² + a²) + a]
  ≈ **(μ0l/2π)[ln(2l/a) − 1]** for l ≫ a (+ μ0l/8π internal for uniform DC current) (Rosa/Grover).
- Two parallel, aligned filaments of length l, spacing d: **M_p = (μ0/2π)[l ln((l + √(l² + d²))/d) − √(l² + d²) + d]**.
- Perpendicular segments: M_p = 0.

Then **L_loop = Σ_i L_p,i + Σ_{i≠j} s_ij M_p,ij**, with s_ij = +1 if the currents in i and j flow in the same
direction, −1 if opposite. Checks (script):
- Two parallel wires (loop sides) of length l, spacing D: 2L_p − 2M_p → (μ0/π)acosh(D/2a)·l as l → ∞
  (ratio 0.94 at l = 5D, 0.998 at l = 100D; the short-l deficit is the end effects).
- Rectangular loops 5 × 5 cm (1 mm wire) and 10 × 2 cm: partial-sum 153.7 and 199.7 nH vs numerical
  Neumann 151.5 and 198.3 nH (−1.4 % / −0.7 %; the difference is the thin-filament treatment at corners).

Why it matters:
- **"Inductance of a trace/via/bond wire" = a partial inductance.** It is well defined (a property of
  the segment's geometry alone) but it is not measurable by itself and not the inductance the circuit
  sees. The circuit sees the loop: L_p,signal + L_p,return − 2M_p. Bringing the return close (large
  M_p) is what reduces loop inductance — the physics behind ground planes, adjacent return vias and
  tightly coupled power/ground pairs ([return paths](../13-pcb-rf-layout-emc/grounding-and-return-paths.md)).
- **Ground bounce / "ground inductance"**: the voltage across a return conductor's partial
  inductance (L_p,return·di/dt minus the mutual term) is what makes "ground" differ between two points.
- **PEEC solvers** (partial-element equivalent circuit) and FastHenry compute exactly these partials
  and assemble them into circuits.

**Vias.** Partial inductance of a via barrel (length h, diameter d): L_p ≈ (μ0h/2π)[ln(4h/d) − 1].
1.6 mm × 0.3 mm: 0.66 nH (thin-wire approx) / **0.69 nH** (exact cylindrical); 0.8 mm × 0.3 mm:
0.25 nH. The formula commonly quoted from Johnson & Graham [6], L = 5.08h[ln(4h/d) + 1] nH (h, d in
inches), has **+1** where the Rosa/Grover partial has **−1**, and gives ~2× the value (1.30 nH for
1.6 × 0.3 mm). What the circuit sees is the loop through the return: a signal via with a ground via
1 mm away has **L_loop = 0.93 nH** (0.47 nH "per via"), 1.13 nH at 2 mm, 1.28 nH at 5 mm (script) —
so the Johnson number is roughly the loop inductance with a distant return, which may be why it
"works" in practice. Treat single-via numbers as partials and always specify the return.

**Bond wires and component leads.** 10 mm of 25 µm-diameter gold wire: L_p = 12.8 nH (1.28 nH/mm);
0.25 mm wire: 0.82 nH/mm; 1 mm wire over 100 mm: 1.0 nH/mm. The "1 nH/mm" rule is the partial
inductance of a thin wire *far from its return*; over a ground plane at height h the loop value per
length is (μ0/2π)acosh(h/a) — 0.74 nH/mm for 1 mm wire at 10 mm, ~0.3 nH/mm for a 50 Ω microstrip.

### Level 3 — mutual inductance of loops (coupled coils, NFC, probes)

Two coaxial circular loops of radii r₁, r₂ at axial separation d (Maxwell):
$$M = \mu_0\sqrt{r_1r_2}\left[\left(\frac2k - k\right)K(k) - \frac2kE(k)\right],\qquad k^2 = \frac{4r_1r_2}{(r_1+r_2)^2 + d^2},$$
K, E complete elliptic integrals. Script (agrees with numerical Neumann to < 10⁻³): r₁ = r₂ = 5 cm,
d = 5 cm → **24.7 nH**; d = 20 cm → 1.30 nH; r₁ = 2, r₂ = 5, d = 3 cm → 9.77 nH. Far apart
(d ≫ r), M → μ0πr₁²r₂²/(2d³) (dipole–dipole): 1.54 nH at d = 20 cm (vs exact 1.30) — the 1/d³ law
behind the steep range limit of inductive (NFC, RFID, wireless-charging) links. Coupled-coil circuit
use: [transformers & coupled inductors](../01-circuit-theory/transformers-coupled-inductors.md).

### Level 3 — capacitance matrices and self-capacitance

For N conductors, Q = [C]V with Maxwell capacitance coefficients (C_ii > 0, C_ij < 0); SPICE
"mutual capacitance" C_m = −C_ij and "capacitance to ground" = Σ_j C_ij. An isolated sphere of radius R
has C = 4πε0R = **111 pF per metre of radius** (1 cm sphere: 1.1 pF; a person ≈ 100–200 pF is often
quoted for ESD models — the sphere estimate for R ≈ 1 m gives 111 pF). Self-capacitance of coils
(inter-turn) sets inductor self-resonance — see [inductors at RF](../04-real-components-hf/inductors-at-rf.md).

## Design equations & rules of thumb

| Equation | When valid | Typical value |
|---|---|---|
| L′_coax = (μ0/2π)ln(b/a) = 200 ln(b/a) nH/m | TEM, high f | RG-58: 237 nH/m |
| C′_coax = 2πε/ln(b/a) = 55.6 εr/ln(b/a) pF/m | | RG-58: 106 pF/m |
| L′_2wire = (μ0/π)acosh(D/2a) ≈ 400 ln(D/a) nH/m | D ≫ a for the log form | 1 mm @ 10 mm: 1.2 µH/m |
| L′_wire-over-ground = 200 acosh(h/a) nH/m | | 1 mm @ 10 mm: 0.74 nH/mm |
| L′C′ = με; L′ = Z0√ε_eff/c; C′ = √ε_eff/(Z0c) | TEM / quasi-TEM | 50 Ω FR-4 µstrip: 0.31 nH/mm, 0.12 pF/mm |
| L_p,wire ≈ 0.2 l[ln(2l/a) − 1] nH (l, a in mm) | l ≫ a | 25 µm wire: 1.28 nH/mm |
| L_p,via ≈ 0.2 h[ln(4h/d) − 1] nH (mm) | h ≫ d | 1.6 × 0.3 mm: 0.66–0.69 nH |
| L_loop = ΣL_p − 2ΣM_p (opposite currents) | any piecewise loop | via pair 1 mm apart: 0.93 nH |
| Fringing factor C/(εw/h) | strip over ground | 50 Ω: ≈ 2.2 |
| M_coax loops (Maxwell elliptic) → μ0πr₁²r₂²/(2d³) | coaxial loops; d ≫ r for approx | 5 cm loops, 5 cm apart: 24.7 nH |
| C_sphere = 4πε0R | isolated | 111 pF/m |

## Worked examples

**1. Inductance of a 915 MHz matching-network "trace".** A 5 mm, 0.3 mm-wide trace between two 0402
pads on 4-layer FR-4 with ground 0.2 mm below (h = 0.2 mm, w/h = 1.5 → Z0 ≈ 55 Ω, ε_eff ≈ 3.3):
L = Z0√ε_eff·l/c ≈ 55 × 1.82 × 5×10⁻³/3×10⁸ ≈ **1.7 nH**, plus C ≈ √ε_eff·l/(Z0c) ≈ 0.55 pF. At 915 MHz
X_L = 9.6 Ω — a significant part of a matching network whose parts are 5–20 nH. Include it.

**2. A via to ground for a shunt capacitor at 2.45 GHz.** One 0.3 mm via through 1.6 mm: loop through the
plane to the capacitor's other pad ≈ 0.7–1 nH → X_L ≈ 11–15 Ω at 2.45 GHz. A "100 pF" shunt capacitor
(X_C = 0.65 Ω) is then dominated by via inductance and series-resonates near
1/(2π√(1 nH × 100 pF)) ≈ 500 MHz. Use 2–4 vias close to the pad (parallel partials, reduced by mutual
coupling) or a smaller capacitor chosen to resonate at the band.

**3. Bond wire / module pin.** An RF IC's 1 mm bond wire (25 µm): ≈ 1 nH partial; the package pin +
PCB pad add ~0.5 nH. At 915 MHz ≈ 9 Ω — why RF IC reference designs specify exact matching values
for their evaluation layout ([package parasitics](../04-real-components-hf/package-parasitics-bondwires.md)).

**4. Loop antenna and probe coupling.** A 5 cm-radius NFC-style loop and a 2 cm test probe 3 cm apart on
axis: M = 9.8 nH; with 100 mA at 13.56 MHz in the big loop, the probe EMF = ωMI = 2π·13.56×10⁶·9.8×10⁻⁹·0.1
= **83 mV**.

## Practical notes
- Always draw the return path before quoting an inductance. For microstrip over a continuous plane the
  return runs directly beneath the trace at RF (minimum-inductance path); a slot or split in the plane
  forces a detour and adds loop inductance (and radiation — see
  [EMC](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md)).
- Field-solver tools for extraction: 2-D solvers (e.g. Saturn PCB, Atlc, openEMS in 2-D, FEMM for
  quasi-static fields) for L′/C′; FastHenry for partial inductances; full-wave for anything electrically
  large.
- Parallel vias: N vias do not give L/N because of mutual inductance; spacing them ≥ a few via diameters
  apart helps.
- Frequency dependence: internal inductance disappears as δ becomes small; L of a wire drops by the
  internal term (μ0/8π per metre for a round wire, ≈ 50 nH/m) between DC and RF.

## Common mistakes & misconceptions
- **"This trace has 1 nH/mm of inductance."** Partial inductance of a thin, isolated wire ≈ 1 nH/mm;
  a trace over a nearby ground plane has 0.3–0.5 nH/mm *loop* inductance. Without the return path the
  number is meaningless.
- **Adding partial inductances without the mutual terms.** Gives nonsense (loop inductances far too
  high).
- **Parallel-plate formula for traces and pads.** Fringing roughly doubles C for 50 Ω lines.
- **Johnson & Graham via formula as "the via inductance".** It is ~2× the partial inductance and roughly
  a loop value with a distant return; state which you mean.
- **"Mutual inductance falls as 1/d."** Between long parallel wires it falls slowly (logarithmically);
  between small loops it falls as 1/d³ (power coupling 1/d⁶).
- **Using static L/C for electrically long structures.** Beyond ~λ/10, use transmission-line or
  full-wave models.

## How to simulate / verify
- `python3 tools/verify/em_inductance.py` — TEM line L′/C′ and L′C′ = με; wire and mutual partial
  inductances; loop = sum of partials vs two-wire limit; rectangular loop partial-sum vs numerical
  Neumann; via partial vs Johnson & Graham vs via-pair loop; 2-D FD Laplace solver for microstrip
  (fringing factors, Z0 and ε_eff vs Hammerstad–Jensen to < 0.4 %); coaxial-loop mutual inductance
  (elliptic integrals vs Neumann); sphere capacitance; coax energy-method check.
- FastHenry (partial/loop inductance, frequency-dependent), FEMM (2-D magnetostatics/electrostatics),
  openEMS for full-wave extraction of via and pad parasitics.

## Open questions / gaps
- The exact expression and derivation printed in Johnson & Graham for via inductance were not re-read
  in this session; the "+1" form is as widely quoted. Flagged medium confidence.
- Pad fringing (3-D) given only as an estimate; a 3-D solver run would firm it up (16-simulation-tools).

## Sources
1. S. Ramo, J. R. Whinnery, T. Van Duzer, *Fields and Waves in Communication Electronics*, 3rd ed.,
   1994, ch. 2 (static fields: capacitance, inductance, energy), ch. 4 (circuit concepts from fields).
   (textbook)
2. D. K. Cheng, *Field and Wave Electromagnetics*, 2nd ed., 1989, §3-10, §6-11 (capacitance, inductance,
   Neumann formula, energy definitions). (textbook)
3. A. E. Ruehli, "Inductance calculations in a complex integrated circuit environment," *IBM J. Res.
   Dev.* 16(5), 470–481, 1972 (partial inductance). (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
4. C. R. Paul, *Inductance: Loop and Partial*, Wiley/IEEE Press 2010 (loop vs partial inductance;
   closed-form partials for wires and bars). (textbook; cited from knowledge)
5. E. Hammerstad and Ø. Jensen, "Accurate models for microstrip computer-aided design," IEEE MTT-S
   Digest 1980, pp. 407–409 (Z0 and ε_eff formulas used as reference in the script). (peer-reviewed;
   formulas as widely reproduced, e.g. Pozar/Wadell)
6. H. W. Johnson and M. Graham, *High-Speed Digital Design*, 1993, §7 (via inductance formula
   L = 5.08h[ln(4h/d) + 1] nH as commonly quoted). (textbook; chapter numbers checked against the publisher table of contents (sigcon.com HSDD ToC, W5-S18/S18b 2026-10-13); content cited from knowledge — see gap)
7. F. W. Grover, *Inductance Calculations*, Van Nostrand 1946 / Dover 2004 (straight-wire and coaxial-
   loop formulas); E. B. Rosa, "The self and mutual inductances of linear conductors," *Bull. Bureau of
   Standards* 4(2), 301–344, 1908. (handbook / classic; Rosa 1908 bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
8. J. C. Maxwell, *A Treatise on Electricity and Magnetism*, 1873, Vol. II (mutual inductance of coaxial
   circles, elliptic integrals). (classic; formula verified numerically)
9. B. C. Wadell, *Transmission Line Design Handbook*, Artech House 1991 (microstrip, two-wire,
   wire-over-ground formulas). (handbook; cited from knowledge)
