---
title: Inductors at RF — types, Q, SRF, saturation and air-coil design
domain: 04-real-components-hf
slug: inductors-at-rf
tags: [inductor, chip-inductor, wirewound, multilayer, thin-film, air-core, air-coil, q-factor, srf, self-resonance, saturation, wheeler, nagaoka, lundin, rosa-correction, skin-effect, coilcraft, murata]
prerequisites:
  - ../01-circuit-theory/lumped-elements-impedance-admittance.md
  - ../01-circuit-theory/resonance-and-q.md
related:
  - capacitors-at-rf-mlcc.md
  - ferrites-and-beads.md
  - pcb-parasitics-traces-vias-pads.md
  - component-models-s2p-spice.md
  - ../01-circuit-theory/passive-filter-design-prototypes.md
  - ../01-circuit-theory/transformers-coupled-inductors.md
  - ../02-electromagnetics/skin-effect-conductor-loss-roughness.md
  - ../02-electromagnetics/inductance-capacitance-from-fields.md
  - ../02-electromagnetics/magnetic-materials-permeability.md
level: mixed
confidence: high
last_updated: 2026-10-14
---

# Inductors at RF — types, Q, SRF, saturation and air-coil design

## Questions this page answers
- What kinds of RF inductors exist (air-core, wirewound ceramic, multilayer, thin-film, ferrite-core) and when do I use each?
- How do inductance and Q change with frequency, and why does inductance "rise" near the self-resonant frequency?
- How far below SRF should I operate a chip inductor?
- Why do multilayer inductors have lower Q than wirewound ones, and how much does it matter?
- How do I calculate the inductance of an air-wound coil (Wheeler, Nagaoka, Lundin)? How accurate are these formulas?
- Do RF inductors saturate?
- What inductor should I use for an RF choke / bias-T at 433 or 915 MHz?
- Why doesn't my measured inductor match the datasheet?

## TL;DR
- Model: series $L$ + loss $R(f)$, shunt parasitic $C_p$ (winding/pad capacitance). **SRF $=1/(2\pi\sqrt{LC_p})$**; below SRF $L_{eff}\approx L/(1-(f/f_{SR})^2)$ rises, Q peaks and then collapses to zero at SRF. Above SRF the part is a capacitor.
- **Operate at ≤ ~1/2–1/3 of SRF** for matching/filters (L within ~10–30 % of nominal); RF chokes are best near SRF (maximum impedance).
- **Q by technology at UHF (0402, ~10 nH, 900 MHz, typical):** wirewound ceramic (Coilcraft 0402HP) **Q ≈ 60–100**; multilayer (Murata LQG15HS) **Q ≈ 30**; thin-film ≈ similar to multilayer with tighter tolerance; air-core springs Q ≈ 100–200. Loss in filters and PA matching is dominated by the inductor ([resonance and Q](../01-circuit-theory/resonance-and-q.md)).
- Datasheet check (Coilcraft 0402HP-10N): L = 9.98 nH @ 900 MHz, 10.4 nH @ 1.7 GHz; Q 62/90; SRF 4.7 GHz; DCR 0.11 Ω; Irms 1.3 A. Murata LQG15HS10N: Q 29 @ 900 MHz; SRF 3.9 GHz typ.
- **Air-coil inductance:** $L=\mu_0\pi r^2N^2k_L/\ell$ with Nagaoka's coefficient $k_L(D/\ell)$ (exact elliptic-integral form; Lundin's formula to < 3 ppm). **Wheeler's** $k_L\approx1/(1+0.45D/\ell)$ is within **0.33 % for ℓ ≥ 0.4D** but −3.8 % at ℓ = 0.2D and −10.6 % at ℓ = 0.1D (verified). Round-wire (Rosa) corrections reduce L by a further ~5–12 % for typical hand-wound UHF coils.
- Example: 5 turns, 3 mm ID, 0.5 mm wire, 1 mm pitch → **≈42 nH** (current-sheet 46 nH), X = 116 Ω at 433.92 MHz; 3 turns → ≈22 nH.
- Air-core and ceramic-core RF inductors **do not saturate**; ferrite-core RF chokes and all power inductors do — current ratings then refer to saturation and heating.
- **Datasheet SRF is fixture-dependent and conservative**: the simple one-pole model with datasheet SRF overestimates the rise of L by several ×; use vendor S-parameter models for accuracy ([component models](component-models-s2p-spice.md)).

## Intuition (no math)
An inductor stores energy in its magnetic field; its value depends only on geometry (turns, diameter, length) and on the permeability of whatever the field passes through. At RF the winding does two unwanted things. First, the turns and pads are conductors sitting next to each other at different voltages — that's capacitance, and at some frequency the inductance resonates with it (the **SRF**). Approaching SRF, the capacitance "helps" the inductor, making it look bigger; past SRF, the capacitance wins and the part behaves like a capacitor. Second, current crowds into a thin skin on the wire surface and pushes against the neighbouring turns (proximity effect), so the resistance rises with frequency — while the reactance rises too. **Q** (reactance/resistance) therefore rises with frequency at first, reaches a peak, and then falls to zero at SRF as the reactance collapses.

Different construction methods trade Q, size, tolerance and cost:
- **Wirewound on a ceramic core** (Coilcraft 0402HP/0603HP, Murata LQW): a real copper wire — thick conductor, highest Q, good current rating.
- **Multilayer** (Murata LQG, TDK MLG): printed spiral layers inside ceramic — thin conductors, lower Q, cheap and consistent.
- **Thin-film** (Murata LQP, TDK MHQ): photolithographic spiral — very tight tolerance, low Q.
- **Air-core** (springs, hand-wound coils): no core loss, highest Q, larger, tunable by squeezing turns.
- **Ferrite core**: high inductance per volume (µH chokes) but core loss, lower SRF, saturation and temperature drift.

## The math

### Level 1 — the lumped model
$$Z_L(\omega)=\frac{(R+j\omega L)}{1+j\omega C_p(R+j\omega L)},\qquad f_{SR}\approx\frac{1}{2\pi\sqrt{LC_p}}.$$
For $R\ll\omega L$: $L_{eff}\approx\dfrac{L}{1-(f/f_{SR})^2}$, $Q_{eff}\approx\dfrac{\omega L}{R}\left[1-(f/f_{SR})^2\right]$. At $f=f_{SR}/2$, $L_{eff}$ is +33 % and Q is 75 % of $\omega L/R$; at $f_{SR}/3$, +12.5 % and 89 %.

**Loss resistance** grows roughly as $R\approx R_{DC}+k\sqrt f$ once the skin depth $\delta=\sqrt{\rho/(\pi f\mu_0)}$ is smaller than the wire radius (Cu at the KB design conductivity, IACS 5.80×10⁷ S/m: 3.17 µm at 433.92 MHz, 2.19 µm at 915 MHz, 1.34 µm at 2.45 GHz; pure annealed Cu, CRC 1.678 µΩ·cm, gives 3.13/2.16/1.32 µm, see [skin effect](../02-electromagnetics/skin-effect-conductor-loss-roughness.md)). If $R\propto\sqrt f$ then $Q\propto\sqrt f$ below SRF — the rising part of every Q-vs-f curve.

### Level 2 — air-coil formulas (current sheet)
For a single-layer solenoid of $N$ turns, mean radius $r$ (diameter $D=2r$), length $\ell$:
$$L_s=\mu_0\frac{\pi r^2N^2}{\ell}\,k_L\!\left(\frac{D}{\ell}\right),$$
where Nagaoka's coefficient $k_L\le1$ corrects the long-solenoid formula for fringing at the ends. Exact (Lorenz/Nagaoka) form with modulus $k^2=D^2/(D^2+\ell^2)$, $k'^2=1-k^2$:
$$k_L=\frac{4}{3\pi k'}\left[\frac{k'^2}{k^2}\big(K(k)-E(k)\big)+E(k)-k\right],$$
$K,E$ complete elliptic integrals. **Verification** (`tools/verify/components_inductors.py` §1): this formula, a direct numerical integration of Maxwell's coaxial-loop mutual inductance over the sheet, and Lundin's 1985 handbook formula agree to < 1×10⁻⁶ (e.g. $k_L=0.688423$ at ℓ = D, matching Knight's benchmark).

**Wheeler's formula** (1928; "long-coil" form, inches and µH): $L=\dfrac{a^2N^2}{9a+10b}$ with $a$ = radius, $b$ = length. In SI it is equivalent to $k_L\approx1/(1+0.45D/\ell)$. Computed errors:

| ℓ/D | 0.1 | 0.2 | 0.4 | 0.5 | 0.8 | 1 | 2 | 5 | 10 |
|---|---|---|---|---|---|---|---|---|---|
| exact $k_L$ | 0.2033 | 0.3198 | 0.4719 | 0.5255 | 0.6381 | 0.6884 | 0.8181 | 0.9201 | 0.9588 |
| Wheeler error | −10.6 % | −3.8 % | −0.27 % | +0.15 % | +0.30 % | +0.18 % | −0.22 % | −0.29 % | −0.19 % |

Max |error| for ℓ ≥ 0.4D: 0.331 % — consistent with Knight's ±0.33 % (Wheeler's own claim was ±1 % for $b>0.8a$).

### Level 3 — real coils, chip-inductor behaviour and saturation

**Round-wire (Rosa) corrections.** A coil of round wire is not a current sheet: $L=L_s-\mu_0rN(k_s+k_m)$, with the self-correction depending on pitch $p$ and wire diameter $d$ — at RF (no internal inductance) $k_s=\tfrac32-\ln(2p/d)$ (at DC $\tfrac54-\ln(2p/d)$) — and the mutual correction $k_m(N)$ (0.114 for N = 2, 0.218 for N = 5, 0.266 for N = 10, → 0.337 for N → ∞; computed from Rosa's GMD expression). For UHF hairpin/spring coils with p ≈ 2d these corrections lower L by ~5–12 %:

| Coil (air) | Current sheet | Rosa-corrected | X @ 433.92 MHz | X @ 915 MHz |
|---|---|---|---|---|
| 5 t, 3.5 mm mean dia, 0.5 mm wire, 1 mm pitch | 46.0 nH | 42.4 nH | 116 Ω | 244 Ω |
| 3 t, same | 23.7 nH | 21.9 nH | 60 Ω | 126 Ω |
| 8 t, 2.5 mm mean dia, 0.4 mm wire, 0.6 mm pitch | 66.8 nH | 58.5 nH | 160 Ω | 337 Ω |

Leads add roughly 1 nH per mm of lead length (see [PCB parasitics](pcb-parasitics-traces-vias-pads.md)) — at 20 nH that is a 5–10 % effect, so trim on the board.

**Air-coil Q estimate.** The 5-turn coil has 55 mm of wire; isolated-wire skin-effect resistance at 433.92 MHz is 0.19 Ω, giving an upper-bound Q ≈ 600; proximity effect between turns typically multiplies $R$ by 2–3 (Medhurst 1947), so Q ≈ 200–300 — in line with commercial air-core springs.

**Chip inductor L(f) vs the one-pole model.** Using the Coilcraft 0402HP datasheet table (§3 of the script): with the datasheet SRF, $L_0/(1-(f/f_{SR})^2)$ predicts 11.5 nH at 1.7 GHz for the 10N part but the datasheet lists 10.4 nH; for 47N, 94 nH predicted vs 58.9 nH listed. Fitting the listed L(1.7 GHz) instead implies an "intrinsic" SRF 1.5–1.8× higher than the datasheet's (8.7 vs 4.7 GHz for 10N). Explanation: L and Q are measured on an impedance analyser with fixture compensation, SRF on a network analyser in a different fixture (SMD-D) whose pads add capacitance; the parasitic is also distributed, not a single lumped $C_p$. **Practical meaning:** the datasheet SRF is a conservative, fixture-referenced number (on your board SRF will be near or below it); don't extrapolate L(f) from it — use the vendor's S-parameter/SPICE model plus your pads. Implied lumped $C_p$ from datasheet SRF is ≈50–115 fF for 0402HP values.

**Saturation and current ratings.** Air and ceramic cores have $\mu_r=1$ and cannot saturate; their Irms rating (Coilcraft: current for a 15 °C rise) is thermal. Ferrite-core RF chokes (e.g. 0805LS/1008 ferrite types) and bead-like inductors lose inductance with DC current ($I_{sat}$ typically quoted for −10 % to −30 % L) and have lower Q and SRF from core loss ([ferrites](ferrites-and-beads.md), [magnetic materials](../02-electromagnetics/magnetic-materials-permeability.md)).

**Temperature and tolerance.** Ceramic-core wirewound TCL +25 to +125 ppm/°C (0402HP). Tolerances: wirewound 2–5 % (±0.1–0.2 nH at low values), multilayer ±0.3 nH or ±5 %, thin-film ±0.05–0.1 nH. For sub-3 nH values the pads and trace (≈0.5–1 nH) matter as much as the part.

## Design equations & rules of thumb

| Item | Equation / rule | Typical |
|---|---|---|
| Effective L below SRF | $L/(1-(f/f_{SR})^2)$ | +12.5 % at $f_{SR}/3$ (single-pole idealisation) |
| Operating margin | $f\le f_{SR}/3$ … $f_{SR}/2$ | 0402HP-22N (SRF 3.3 GHz) fine to ~1.1–1.6 GHz |
| RF choke | $|Z|$ largest near SRF; want $|Z|\ge10Z_0$ at f | 433 MHz: ~180–270 nH (SRF ≈ 0.6–1 GHz) or a ferrite choke; check datasheet $|Z|$ |
| Air coil | $L=\mu_0\pi r^2N^2k_L/\ell$ | Wheeler $k_L\approx1/(1+0.45D/\ell)$, ±0.33 % for ℓ ≥ 0.4D |
| Wheeler (inch, µH) | $a^2N^2/(9a+10b)$ | $a$ radius, $b$ length |
| Rosa correction | $-\mu_0rN(k_s+k_m)$, $k_s=\tfrac32-\ln(2p/d)$ | −5…−12 % for p ≈ 1.5–2.5 d |
| Skin depth Cu | $\delta=\sqrt{\rho/(\pi f\mu_0)}$ | 3.17 µm @ 434 MHz (IACS) |
| Q (typ, 0402, ~10 nH, 900 MHz) | wirewound 60–100; multilayer ≈ 30 | 0402HP-10N 62; LQG15HS10N 29 |

## Worked examples

### 1. Choosing a matching inductor for 433.92 MHz
Need ≈22 nH (60 Ω). Options: Coilcraft 0402HP-22N (Q 60 @ 900 MHz, lower at 433 MHz; SRF 3.3 GHz; 0.16 Ω DCR; 800 mA) or Murata LQG15HS22N (Q ≈ 23–24 @ 800–900 MHz; SRF 1.9 GHz min / 2.5 GHz typ; 0.42 Ω max DCR). In a 2 W PA L-match carrying ~6 var ([reactive power](../01-circuit-theory/energy-storage-and-reactive-power.md)) the multilayer part would dissipate roughly twice as much (≈0.2–0.25 W) and lose ≈0.5 dB — choose wirewound for PA outputs and filters, multilayer is fine in low-power, broadband matches.

### 2. An RF choke (bias feed) for a GNSS active antenna at 1575.42 MHz
The choke should present $|Z|\gg50\ \Omega$ at 1575 MHz and low DCR. A 47–68 nH wirewound (SRF 1.8–2.4 GHz) gives $X\approx$ 470–670 Ω at 1575 MHz (plus the SRF boost) — adequate. A 220 nH part would be past its SRF (≈0.96 GHz) and look like a ~0.1 pF capacitor (≈1 kΩ) — still high impedance, but unpredictable; check the vendor impedance curve.

### 3. A hand-wound tank coil for 433.92 MHz
Target 22 nH with 0.5 mm enamelled wire on a 3 mm drill: 3 turns at 1 mm pitch gives ≈21.9 nH (Rosa-corrected), plus ~2–4 nH of leads. Stretch or compress to tune: increasing pitch from 1 to 1.3 mm lowers L by ≈10 % (21.9 → 19.7 nH, same script). Expect unloaded Q ≈ 150–250.

## Practical notes
- **Coupling:** chip inductors' fields extend around them; neighbouring inductors in a filter couple (k ≈ 0.01–0.05). Rotate adjacent parts 90° and keep them apart ([transformers](../01-circuit-theory/transformers-coupled-inductors.md)).
- **Pads under inductors:** a ground plane directly under a chip inductor lowers L slightly (eddy currents) and adds capacitance (lower SRF); RF layouts sometimes clear the plane under the inductor on the top inner layer — only if the return-path design allows it ([RF layout](../13-pcb-rf-layout-emc/rf-layout-rules.md)).
- **JLCPCB availability:** multilayer (Murata LQG, Sunlord SDCL, Chilisin) is commonly stocked as basic/extended parts; wirewound high-Q (LQW, Coilcraft) is often extended or consigned. For a PA output network or a narrow filter, paying for wirewound is worth it.
- **Measuring:** a calibrated VNA with a series-thru or shunt fixture; convert to L and Q vs frequency; compare with the vendor S2P ([VNA](../17-test-measurement/vna-fundamentals-calibration.md)). Impedance analysers (4291/E4991) are the reference below ~3 GHz.

## Common mistakes & misconceptions
- **Using a multilayer inductor in a narrow filter** and blaming the design for 3–6 dB of loss.
- **Operating near SRF** where L is strongly frequency dependent and part-to-part variation is large.
- **Believing Wheeler's formula for flat, short coils** (ℓ < 0.4D): errors grow to 4–11 %. Use the elliptic form or Lundin's formula (script).
- **Forgetting leads and pads** for small coils: 1–2 mm of lead is ~1–2 nH.
- **"Inductors saturate at RF current."** Air/ceramic RF inductors don't; they overheat. Ferrite-cored ones do saturate.
- **Extrapolating L(f) from the datasheet SRF** — the one-pole model with datasheet SRF can be wrong by tens of percent near SRF (see Level 3).

## How to simulate / verify
- `python3 tools/verify/components_inductors.py` — Nagaoka coefficient three ways, Wheeler error table, Rosa-corrected air-coil examples, Coilcraft 0402HP L(f) consistency check, skin depth and Q estimate.
- Vendor models: Coilcraft S-parameters (fitted-model generated, first resonance only; Doc 1721), Murata SimSurfing, Modelithics substrate-scalable models ([component models](component-models-s2p-spice.md)).
- Air-coil calculators: coil32.net, Knight's spreadsheets (g3ynh.info), or the script above.
- EM: openEMS/FastHenry for coils and PCB spirals ([EM solvers](../16-simulation-tools/em-solvers-fdtd-mom-fem.md)).

## Open questions / gaps
- Proximity-effect factor for UHF air coils is taken as 2–3 from classic literature (Medhurst); not computed here.
- No in-circuit Q measurements of JLCPCB-stocked multilayer inductors at 433/915 MHz (bench task).
- The Coilcraft L(f)/SRF inconsistency is explained qualitatively (fixture differences, distributed capacitance); a quantitative model would need the vendor S-parameters.

## Sources
1. Coilcraft, "Chip inductors — 0402HP series (1005)," Doc 526, rev. 12/20/2023 — L, Q (900 MHz, 1.7 GHz), SRF, DCR, Irms table; measurement fixtures (SMD-F/4286, 4287A/16197, 8722ES/SMD-D); TCL. https://www.coilcraft.com/getmedia/54459dcc-b821-4a9d-b91e-0416ea86a9b2/0402hp.pdf (datasheet)
2. Murata, "LQG15HS series" catalog O05E11 (Modelithics-hosted) — Q min 8 @ 100 MHz, typical Q at 800 MHz–2.4 GHz (e.g. 10 nH: 27/29/35/33/28), SRF, DCR. https://www.modelithics.com/models/Vendor/Murata/LQG15HS.pdf (datasheet)
3. D. W. Knight, "An introduction to the art of solenoid inductance calculation, with emphasis on radio-frequency applications," v0.20, 2016 (g3ynh.info) — Nagaoka coefficient, Lundin formula, Wheeler 1925/1928 formula accuracy (±0.33 % for ℓ ≥ 0.4D), Rosa corrections. https://coil32.net/files/Dave_Knight/Solenoids.pdf (technical monograph, well-referenced)
4. R. Lundin, "A handbook formula for the inductance of a single-layer circular coil," *Proc. IEEE*, 73(9), 1428–1429, 1985. (peer-reviewed)
5. H. A. Wheeler, "Simple inductance formulas for radio coils," *Proc. IRE*, 16(10), 1398–1400, 1928. (peer-reviewed)
6. H. Nagaoka, "The inductance coefficients of solenoids," *J. Coll. Sci. Tokyo*, 27(6), 1909; E. B. Rosa, "The self and mutual inductances of linear conductors," *Bull. Bureau of Standards*, 4, 1908; F. W. Grover, *Inductance Calculations*, Van Nostrand 1946 / Dover. (historical, peer-reviewed/textbook)
7. R. G. Medhurst, "H.F. resistance and self-capacitance of single-layer solenoids," *Wireless Engineer*, Feb./Mar. 1947. (peer-reviewed)
8. Coilcraft, "S-parameters for high-frequency circuit simulations," Doc 1721, 2023 — how inductor S-params are generated, de-embedding, SRF on board vs model. https://www.coilcraft.com/getmedia/35dbfd16-8483-4ef7-bb07-9b28a04f6dcc/doc1721_When-to-Use-S-parameters.pdf (app note)
9. C. Bowick, *RF Circuit Design*, 2nd ed., 2008 — ch. 1 (inductor Q, air-coil design). (textbook)
10. Verification script `tools/verify/components_inductors.py` (this KB).
