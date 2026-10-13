---
title: Baluns and RF transformers (lattice LC, Marchand, Guanella/Ruthroff TLTs, ferrite, chip baluns)
domain: 06-rf-circuits
slug: baluns-and-rf-transformers
tags: [balun, lattice-balun, lc-balun, marchand, transmission-line-transformer, guanella, ruthroff, ferrite, mixed-mode, amplitude-imbalance, phase-imbalance, common-mode, cc1101, sx126x, johanson, sa612, ne602, dot-convention, bridged-footprint, dnp, balun-placement, push-pull]
prerequisites:
  - ../01-circuit-theory/transformers-coupled-inductors.md
  - ../03-transmission-lines-matching/s-parameters.md
  - couplers-dividers-combiners.md
related:
  - ../08-antennas/antenna-matching-and-baluns.md
  - mixers.md
  - power-amplifiers.md
  - ../04-real-components-hf/ferrites-and-beads.md
  - ../02-electromagnetics/magnetic-materials-permeability.md
  - ../15-lora-ism-radios/semtech-chip-family.md
  - ../13-pcb-rf-layout-emc/rf-layout-rules.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Baluns and RF transformers

Antenna-side baluns (common-mode chokes on coax, sleeve baluns, W1HIS choke rules) are covered in [antenna matching and baluns](../08-antennas/antenna-matching-and-baluns.md); coupled-inductor theory in [transformers](../01-circuit-theory/transformers-coupled-inductors.md). This page covers the *circuit* baluns and transformers used between chips, mixers, PAs and 50 Ω lines.

## Questions this page answers
- Why does my transceiver (CC1101, SX126x RX input, AD9361, many mixers) have differential RF pins, and how do I connect it to a 50 Ω antenna?
- How do I design a lumped LC ("lattice") balun, and how wide is it?
- How does a Marchand balun work and what coupling does it need?
- What is the difference between a Guanella and a Ruthroff transformer, and why does one work to higher frequency?
- What do amplitude and phase imbalance specs mean for my system?
- What sets the low- and high-frequency limits of a ferrite transformer?
- Should I use a chip balun (e.g. Johanson) or discrete parts?
- What are mixed-mode S-parameters (Sdd, Scs, Sds)?
- Can I leave a balun footprint empty and bridge it with 0 Ω for a single-ended build?
- What do the dots on a transformer or balun mean, and what happens if I reverse one?
- Where should the balun sit relative to the chip?
- How do I feed an SA612/NE602: single-ended, through a balun, and how much LO?

## TL;DR
- A **balun** converts between an unbalanced (single-ended, ground-referenced) port and a balanced (differential) port, usually with an impedance ratio. Quality metrics: insertion loss, return loss, **amplitude imbalance** (dB) and **phase imbalance** (deviation from 180°) — together they set how much signal leaks into the **common mode**: 1.5 dB / 10° → CM/DM ≈ −18 dB; 0.5 dB / 3° → −28 dB (verified).
- **Lumped lattice balun** (two L-sections, one low-pass, one high-pass): $L=\sqrt{R_uR_b}/\omega_0$, $C=1/(\omega_0\sqrt{R_uR_b})$. 433.92 MHz, 50 → 100 Ω: 25.9 nH, 5.19 pF; 868 MHz: 13.0 nH, 2.59 pF; 915 MHz: 12.3 nH, 2.46 pF. Perfect at $f_0$; ≈ 11 % bandwidth for RL > 15 dB, < 1 dB and < 10° imbalance; CM/DM ≈ −20 dB at ±10 % (verified).
- **Marchand balun** (two coupled λ/4 sections on a λ/2 open main line): perfectly balanced at $f_0$ for any coupling; match requires a one-parameter family of $(Z_{0e},Z_{0o})$; as $Z_{0e}\to\infty$, $Z_{0o}\to\sqrt{R_sR_b}/2$ (35.4 Ω for 50 → 100 Ω; verified). Bandwidth 50–80 % with high even-mode impedance — why Marchands appear in broadband mixers and on-chip.
- **Transmission-line transformers (TLTs)**: the windings are a transmission line, so leakage and winding capacitance become the line's L and C. **Guanella** (equal-delay, voltages add after equal delays) is ideally frequency-independent; **Ruthroff** (bootstrap: direct + delayed voltage added) falls 1 dB when the line is λ/4 and nulls at λ/2 — $P/P_{av}=\frac{4(1+\cos\beta l)^2}{(1+3\cos\beta l)^2+4\sin^2\beta l}$ (derived form verified). The ferrite only blocks the common-mode path; low-frequency limit where the magnetising/CM reactance ≈ $Z_0/2$ (−3 dB).
- **Chip/IPD baluns** matched to specific chips integrate the balun, match and harmonic LPF: Johanson 0433BM15A0001 (TI CC110x/CC430, 430–435 MHz, 0805-size 2.0 × 1.25 mm, ≤ 1.9 dB IL, ≥ 34 dB at 2f₀, 180° ± 10°, ≤ 1.5 dB amplitude difference, 1 W CW) [5]. They save area and tuning time at the cost of ~1–2 dB loss vs a well-tuned discrete network.
- **Practicalities** ([below](#balun-practicalities-footprints-dots-placement-and-the-sa612)): an empty 0402 pad pair (≈ 0.15 pF) left on a 50 Ω line costs RL 40 dB at 433 MHz but 17 dB at 5.8 GHz. A reversed dot on one IQ leg swaps the received sideband; on a push-pull output it cancels the fundamental and keeps the 2nd harmonic. The SA612 inputs are 1.5 kΩ ∥ 3 pF each and may be driven single-ended. An external LO goes into pin 6 at **200–300 mVpp (−10 to −6.5 dBm across 50 Ω)**, so a 3.3 V Si5351 output needs ≈ 22 dB of attenuation (1 kΩ/68 Ω → 268 mVpp fundamental).

## Intuition (no math)
A single-ended signal is a voltage between one wire and ground. A differential signal is the difference between two wires that swing in opposite directions — whatever happens equally to both (supply noise, ground bounce, even-order distortion) cancels. RF ICs use differential ports because they double voltage swing on low supplies, reject substrate noise, and cancel even harmonics in mixers and PAs. The antenna and the coax, however, are single-ended. A balun is the translator.

The lattice balun makes the two antiphase outputs by sending the input through two different L-networks: a low-pass one that delays the signal by 90° and a high-pass one that advances it by 90°. The two outputs therefore differ by 180° — but only at the design frequency, where both networks also transform the impedance correctly. Move off frequency and the phases drift in opposite directions: narrowband.

The Marchand balun uses coupled lines: the input wave travels down a half-wave line, and two quarter-wave "pick-up" lines grounded at their outer ends see currents in opposite directions, giving antiphase outputs at their inner ends. The phase balance comes from symmetry, not from frequency-dependent networks, which is why it is broadband.

A transmission-line transformer is a length of twisted pair or coax wound on a ferrite. The line carries the signal in its normal (differential) mode — unaffected by the ferrite — while the ferrite makes any common-mode current (the same current on both conductors) see a large impedance. By connecting several lines in series at one end and parallel at the other, voltages add while currents split: 1:4, 1:9 impedance ratios over decades of bandwidth.

## The math

### Level 1 — definitions and mixed-mode quantities
With port 1 single-ended and ports 2, 3 forming the balanced pair (each referenced to $Z_b/2$):
$$S_{ds21}=\frac{S_{21}-S_{31}}{\sqrt2},\quad S_{cs21}=\frac{S_{21}+S_{31}}{\sqrt2},\quad S_{dd22}=\frac{S_{22}-S_{23}-S_{32}+S_{33}}{2}$$
Amplitude imbalance $=20\log|S_{21}/S_{31}|$; phase imbalance $=\angle(S_{21}/S_{31})-180°$. For outputs $1$ and $-a e^{j\delta}$ the ratio of common- to differential-mode output is
$$\frac{|S_{cs21}|}{|S_{ds21}|}=\left|\frac{1-ae^{j\delta}}{1+ae^{j\delta}}\right|.$$
Typical consequences: a balanced mixer's LO-to-RF isolation and even-order (IIP2) rejection, and a differential PA's 2nd-harmonic cancellation, are limited to roughly this CM/DM ratio.

### Level 1½ — imbalance as a leftover, algebra only
- **The ideal case.** An ideal balun puts +½ and −½ of the drive on its two legs. Their difference (differential mode, DM) is the wanted signal and their sum (common mode, CM) is zero.
- **A real balun leaves something over.** If the second leg is $-a e^{j\delta}$ instead of −1, the sum is $1 - a e^{j\delta}$, not zero. The CM/DM ratio is the Level 1 formula $|(1-ae^{j\delta})/(1+ae^{j\delta})|$.
- **Small errors add in quadrature.** For small errors the ratio is ≈ $\tfrac12\sqrt{\varepsilon^2+\delta^2}$, with ε = a − 1 (a fraction) and δ in radians. Phase alone at 10° gives −21 dB; amplitude alone at 1 dB gives −25 dB.

*Worked number (verified, `tools/verify/s18b_level15_numbers.py`).* For 0.5 dB and 5°: a = 1.059, so ε = 0.059 and δ = 0.087 rad. Then ½√(0.0035 + 0.0076) = 0.053, i.e. **−25.6 dB**. The exact formula also gives −25.6 dB. A differential PA behind this balun therefore gets only about 26 dB of 2nd-harmonic cancellation from symmetry.

### Level 2 — derivations

**(a) Lattice balun.** Consider each output branch driving half of the balanced load ($R_b/2$ to the virtual ground). A low-pass π/T section with $\omega_0L=1/(\omega_0C)=Z_m$ is a quarter-wave-equivalent network with characteristic impedance $Z_m$ and phase −90°; the high-pass dual (series C, shunt L) has +90°. Each transforms its termination $R_b/2$ to $Z_m^2/(R_b/2)$; in parallel at the input the two give $Z_m^2/R_b$, which equals $R_u$ when $Z_m=\sqrt{R_uR_b}$. Hence $L=\sqrt{R_uR_b}/\omega_0$, $C=1/(\omega_0\sqrt{R_uR_b})$, outputs equal in amplitude and 180° apart [1][2]. Off frequency, the two branches' phases move in opposite directions and their impedances mistrack → the ≈ 11 % bandwidth found in check A (independent of the impedance ratio for the criteria used).

**(b) Marchand balun.** Two symmetric coupled-line sections (even/odd impedances $Z_{0e},Z_{0o}$), each λ/4 at $f_0$; the main conductors are in series and open at the far end; the secondary conductors are grounded at their outer ends and the balanced load is between their inner ends. At $f_0$ the structure is exactly balanced by symmetry for any coupling (check B1). In the limit $Z_{0e}\to\infty$ each section behaves like an ideal quarter-wave transformer of impedance $2Z_{0o}$ in the line-to-line mode, so matching requires $(2Z_{0o})^2=R_sR_b$, i.e.
$$Z_{0o}=\tfrac12\sqrt{R_sR_b}\qquad(35.4\ \Omega\text{ for }50\to100\ \Omega)$$
(verified to 0.02 Ω). Finite $Z_{0e}$ lowers the required $Z_{0o}$ (100 → 26.1 Ω, 250 → 31.0 Ω) and narrows the band; the even-mode (common-mode) impedance is what chokes the unwanted mode [3][2]. In microstrip, the unequal even/odd velocities degrade balance off-centre; broadside-coupled or multilayer (LTCC) realisations reach tighter coupling.

**(c) Ruthroff 1:4 (bootstrap).** A line of impedance $Z_0$, input $V_1$ at one end; the far end of conductor B is tied to the input, so the output is $V_1$ plus the line's delayed output. Solving the line equations with source $R_g$ and load $R_L=4R_g$, $Z_0=2R_g$ gives the transmission ratio in the TL;DR [4]: flat at low frequency, −0.97 dB at βl = 90°, zero at 180° (checks C2–C3). The loss is because the direct and delayed voltages no longer add in phase.

**(d) Guanella 1:4 (equal delay).** Two lines of $Z_0=2R_g=100\ \Omega$, inputs in parallel (each sees 100 Ω: 100 ∥ 100 = 50), outputs in series (100 + 100 = 200). Each line is terminated in its own $Z_0$, so it only adds delay; both delays are equal and the voltages add in phase at every frequency (check C1, ideal core). The high-frequency limit in practice comes from parasitic capacitance, the connections and imperfect $Z_0$; the low-frequency limit from the finite common-mode (choking) reactance [4].

**(e) Low-frequency limit.** A shunt reactance $X$ across a matched $Z_0$ path gives $|S_{21}|^2=4X^2/(4X^2+Z_0^2)$: −3 dB at $X=Z_0/2$, −0.26 dB at $2Z_0$, −0.04 dB at $5Z_0$ (check D). For a conventional (flux-coupled) transformer $X=\omega L_m$ (magnetising inductance); for a TLT the relevant reactance is the common-mode choking impedance of the winding on the core.

### Level 3 — practical limits and variants
- **Flux-coupled wideband transformers** (Mini-Circuits ADT/TC-style) are limited at high frequency by leakage inductance and winding capacitance (resonance), at low frequency by $L_m$; ferrite loss and saturation limit power. Bifilar/trifilar windings raise coupling.
- **Baluns with DC paths:** a lattice balun has an inductor to ground on one output (DC short) and a series capacitor on the other (DC block) — check whether your IC needs DC bias on its RF pins (many PA outputs need a DC feed; many LNA inputs must be DC-blocked).
- **Integrated passive devices (IPD) / LTCC baluns** combine balun + harmonic filter + DC block; matched to a specific chip's *conjugate* differential impedance (which is not 100 Ω real). Using one designed for another chip gives mismatch.
- **Even-mode rejection in mixers:** double-balanced mixers rely on two baluns; their imbalance sets LO/RF isolation and IIP2 ([mixers](mixers.md)).
- **Differential PAs** cancel even harmonics by symmetry: a balun with −18 dB CM/DM leaves the 2nd harmonic only ≈ 18 dB below what a single-ended device would produce — still needs a harmonic filter ([power amplifiers](power-amplifiers.md)).

## Design equations & rules of thumb

| Quantity | Equation / value | Notes |
|---|---|---|
| Lattice balun | $L=\sqrt{R_uR_b}/\omega_0$, $C=1/(\omega_0\sqrt{R_uR_b})$ | ≈ 11 % BW (15 dB RL, 1 dB, 10°) |
| Marchand (ideal, $Z_{0e}\to\infty$) | $Z_{0o}=\sqrt{R_sR_b}/2$ | 50→100 Ω: 35.4 Ω; 50–80 % BW |
| Guanella 1:n² | n lines, inputs parallel, outputs series; each $Z_0=nR_{in}=\sqrt{R_{in}R_{out}}$ | 1:4: two 100 Ω lines for 50→200 Ω |
| Ruthroff 1:4 | $Z_0=2R_g$; −1 dB at λ/4, null at λ/2 | keep line ≪ λ/4 |
| LF limit | −3 dB at $X_{m}=Z_0/2$; use $X_m\ge5Z_0$ | 1:1 at 3.5 MHz, 50 Ω → $L_m\ge11.4$ µH |
| Imbalance → CM | $\lvert(1-ae^{j\delta})/(1+ae^{j\delta})\rvert$ | 1 dB/5° → −23 dB |

## Worked examples

### Example 1 — Discrete balun for a 433 MHz differential transceiver port
For a chip whose differential port wants 100 Ω real (check the data sheet — often it is complex, e.g. a few tens of ohms in series with a reactance, and the TX optimum differs from RX): $L$ = 25.9 nH (27 nH wire-wound), $C$ = 5.19 pF (5.1 pF C0G). Place the L-to-ground and C-to-ground elements symmetrically close to the pins; add a series DC-block cap on the inductive branch if the pin must not see DC to ground. Expect 0.3–0.6 dB loss with Q ≈ 40 inductors. For a complex target $Z_{diff}$, absorb its reactance into the branch elements (or add a series match) and verify in simulation: the real-part formula above is the starting point.

### Example 2 — Chip balun for a TI CC1101 at 433 MHz
Johanson 0433BM15A0001: unbalanced 50 Ω, balanced side conjugate-matched to CC110x/CC430, 430–435 MHz, IL ≤ 1.9 dB, RL ≥ 9.5 dB, 2f₀ ≥ 34 dB and 3f₀–5f₀ ≥ 35 dB attenuation, phase 180° ± 10°, amplitude ≤ 1.5 dB, 1 W CW, balanced ports DC-blocked internally [5]. From Example E of the script, the worst-case imbalance corresponds to CM/DM ≈ −18 dB. It replaces ≈ 8–10 discrete parts including the harmonic filter; the 1.9 dB worst-case IL costs ≈ 1.9 dB of TX power and RX sensitivity compared with an ideal network (typical is lower).

### Example 3 — 1:4 transformer for a 200 Ω folded dipole or a mixer IF port (HF–VHF)
Guanella: two 100 Ω bifilar windings (e.g. twisted enamelled pair) on a two-hole ferrite core, inputs paralleled at 50 Ω, outputs in series at 200 Ω; choose turns so the common-mode reactance ≥ 5 × 50 Ω at the lowest frequency. Ruthroff: one 100 Ω winding; simpler but keep each winding's length ≪ λ/4 at the top frequency (at λ/4 it already loses ≈ 1 dB, script C). For UHF, prefer printed Marchand or LTCC parts.

### Example 4 — Marchand balun for a 2.45 GHz double-balanced mixer
50 → 100 Ω: choose $Z_{0e}$ as high as practical (≥ 150 Ω) and $Z_{0o}$ from the matched family: $Z_{0e}$ = 150 → $Z_{0o}$ = 28.6 Ω (k = 0.68, 65 % bandwidth); 250 → 31.0 Ω (81 %) (script B). k ≈ 0.7 is too tight for edge-coupled microstrip on FR-4 (gaps ≪ 0.1 mm) — use broadside coupling in a multilayer stack-up or a spiral/LTCC form.

## Practical notes
- **Symmetry in layout** matters as much as values: equal trace lengths from the balun to the IC pins, symmetric grounding, no vias on only one side.
- **Measure baluns** with a 3- or 4-port VNA, or a 2-port VNA and terminations (measure 1→2 with 3 terminated, then 1→3), then compute mixed-mode parameters; the NanoVNA's 2 ports are enough with careful terminations.
- **Chip-matched parts** are specified with the chip's reference layout; deviating (different stack-up, long traces) shifts the match.
- **Power and linearity:** ferrite-core TLTs saturate and heat at high power; LTCC baluns have power ratings (1 W CW for the Johanson example [5]).
- **DC:** some baluns short one side to ground; some block both. Check before applying bias through them.

### Balun practicalities: footprints, dots, placement and the SA612
- **Bridged footprints in single-ended builds.** Reference boards often carry a balun footprint that a single-ended variant bypasses with a 0 Ω link (or DNP parts and a jumper). Three things go wrong:
  - *Stubs.* Empty pads add ≈ 0.1–0.2 pF each. An unused leg routed to the far pad is an open stub. An empty 0402 pair on a 50 Ω line: RL 39.8 dB at 433.92 MHz, 33.3 dB at 915 MHz, 24.8 dB at 2.45 GHz, 17.4 dB at 5.8 GHz (script J). Harmless at LoRa frequencies, noticeable at Wi-Fi. Keep bypass links on the signal path, not on a branch.
  - *The other half of a differential input.* When a differential pin pair is driven single-ended, the unused pin must be AC-grounded with a capacitor at the pin, not left floating or tied through a long trace.
  - *What you give up.* Expect worse even-order rejection (IIP2, half-IF spur), more LO leakage to the RF port and a different input impedance (one side instead of the differential pair). Check the chip's data sheet for an approved single-ended configuration before relying on it.
- **Dot polarity.** Dots mark the winding ends that go positive together. On a balun the dots decide which output is the "+" leg. The consequences of a reversed winding:
  - In an IQ receiver, one reversed leg turns $g\to-g$: the image-rejection ratio inverts (41.2 dB → −41.2 dB at 1°), so the receiver now selects the **image** (USB ↔ LSB swapped).
  - In a push-pull PA or a centre-tapped output transformer, one reversed half cancels the fundamental and passes the 2nd harmonic (script I).
  - In a transformer-feedback (Norton) amplifier, feedback turns positive and it oscillates.
  - On a DBM, swapping one balun only inverts the IF sign, which is harmless unless a phasing network follows.
  Mark dots on the schematic symbol **and** the silkscreen, and check with a scope (two probes, common ground) at low frequency before RF tests.
- **Placement.** Put the balun right at the chip's differential pins: both legs equal in length, mirror-symmetric, and within ≈ λ/20 of the pins (≈ 9 mm at 915 MHz in FR-4 microstrip with ε_eff ≈ 3.3; reference layouts for chip baluns are tighter still). Ground the balun's unbalanced-side return straight to the chip's ground plane with vias at the pad. The single-ended 50 Ω side may then run any length. Chip baluns are not symmetric parts: port numbering (unbalanced, balanced +/−, DC/GND) differs between vendors and a mirrored footprint is the most common error. Check the footprint against the data sheet's pin-out drawing, not the symbol.
- **SA612/NE602 front ends.** The Gilbert-cell inputs (IN_A, IN_B, pins 1–2) are internally biased, symmetrical, ≈ 1.5 kΩ ∥ 3 pF each through 50 MHz, and must not be DC-biased externally. The outputs (pins 4–5) are 1.5 kΩ each to the internal supply. Typical figures: 17 dB conversion gain (14 dB min) and NF 5.0 dB at 45 MHz, 2.4 mA at 4.5–8 V. IIP3 is −13 dBm in the dynamic-characteristics table but "typically −15 dBm" in the application text, so quote the table [7]. Input options:
  1. *Single-ended*: drive pin 1 through a match and AC-ground pin 2. The data sheet allows it. At 7.1 MHz a 50 Ω → 1.5 kΩ L-match is Q = 5.39: series 6.04 µH, shunt 80.5 pF less the 3 pF pin capacitance → 77.5 pF.
  2. *Balanced*: a transformer or balun to the 3 kΩ differential input (turns ratio √(3000/50) = 7.75:1, e.g. a tuned secondary). It gives better 2nd-order rejection, lower LO leakage back out of the RF port and full use of the double balance (script H).

  For an **external LO**, inject at OSC_B (pin 6) through a DC-blocking capacitor at 200–300 mVpp (−10.0 to −6.5 dBm across 50 Ω) [7]. A Si5351 or MCU output at 3.3 Vpp is ≈ 22 dB too hot and its square wave adds harmonic LO responses. Pad it down (1 kΩ series + 68 Ω shunt gives a 268 mVpp fundamental) and low-pass it if spurs matter. An external balun or DBM is the upgrade when the SA612's IIP3 (≈ −13 dBm) limits strong-signal handling. Note that SA612s from marketplaces are often clones ([mixers/PLL parts](../18-components-parts/mixers-plls-vcos-parts.md)).

## Common mistakes & misconceptions
- *"Any balun is a common-mode choke."* A voltage (Ruthroff-type) balun forces equal voltages, not equal currents, and does not stop CM current on a coax feeding an unbalanced antenna — see the antenna page.
- *"A 1:1 balun means the differential side is 50 Ω."* It means 50 Ω *differential*, i.e. 25 Ω per side to the virtual ground.
- *"Lumped baluns are broadband."* They are exact only at $f_0$ (≈ 11 % usable band).
- *"Phase imbalance of 10° is negligible."* It already limits common-mode rejection to ≈ 20 dB.
- *"A chip balun for chip X works for chip Y."* It is matched to X's differential impedance; Y's is different.
- *"Guanella and Ruthroff are the same with different winding."* Guanella adds equally delayed voltages (broadband); Ruthroff adds a direct and a delayed one (limited to ≪ λ/4).
- *"Dots don't matter on a balun."* Reversing one changes which sideband an IQ receiver hears, or cancels a push-pull fundamental.
- *"A DNP balun footprint is invisible."* It is ≈ 0.15 pF per pad pair plus any stub. That is fine at 433 MHz but not at 5.8 GHz.
- *"The SA612 LO pin wants logic levels."* It wants 200–300 mVpp; a 3.3 V square wave overdrives it by ≈ 22 dB.

## How to simulate / verify
- `tools/verify/s14_rx_budget.py` §H–J: SA612 LO levels, L-match and turns ratio, Si5351 divider, dot-polarity sideband swap and push-pull cancellation, empty-footprint return loss (20/20 PASS overall).
- `tools/verify/rfckt_baluns.py`: lattice balun (values, mixed-mode, bandwidth), Marchand family and $Z_{0e}\to\infty$ limit, Guanella vs Ruthroff with an ideal floating-line model (and the Ruthroff closed form), magnetising-inductance limit, imbalance → CM conversion. Uses the nodal solver `tools/verify/rfckt_netsolve.py` (`tline_float` models a TLT winding whose common mode is fully choked).
- scikit-rf: build the balun as a 3-port and use `Network.se2gmm()` for mixed-mode parameters.
- EM: openEMS for printed Marchands (coupled-line dispersion, via grounds).

## Open questions / gaps
- SX126x RF-pin impedances and Semtech's reference balun/match values were not extracted here (domain 15 / 18 should hold the reference designs).
- Ferrite core material data (A_L, µ″ vs frequency for 43/61/67 mixes) are in [ferrites](../04-real-components-hf/ferrites-and-beads.md) and domain 08; no core-specific transformer design is worked here.
- Printed Marchand with realistic microstrip modal velocities not simulated (only ideal TEM coupled lines).

## Sources
1. C. Bowick, *RF Circuit Design*, 2nd ed., Newnes, 2008 — lumped L-network and balun matching. (textbook)
2. D. M. Pozar, *Microwave Engineering*, 4th ed., 2012, §7.3 and §7.6 (even/odd-mode and coupled-line analysis used for the Marchand). (textbook)
3. N. Marchand, "Transmission-line conversion transformers," *Electronics*, 17, pp. 142–145, Dec. 1944; K. S. Ang, I. D. Robertson, "Analysis and design of impedance-transforming planar Marchand baluns," *IEEE Trans. MTT*, 49(2), pp. 402–406, Feb. 2001. (magazine/peer-reviewed)
4. C. L. Ruthroff, "Some broad-band transformers," *Proc. IRE*, 47(8), pp. 1337–1342, Aug. 1959; G. Guanella, "Novel matching systems for high frequencies," *Brown Boveri Review*, 31, pp. 327–329, 1944; J. Sevick, *Transmission Line Transformers*, 4th ed., Noble, 2001. (peer-reviewed / textbook)
5. Johanson Technology, *0433BM15A0001 430/403 MHz Impedance Matched Balun/LPF for TI chipsets*, detail specification rev. 10/27/2015. https://www.johansontechnology.com/datasheets/chipset-specific/0433BM15A0001.pdf (datasheet)
6. D. E. Bockelman, W. R. Eisenstadt, "Combined differential and common-mode scattering parameters: theory and simulation," *IEEE Trans. MTT*, 43(7), pp. 1530–1539, July 1995 (mixed-mode S-parameters). (peer-reviewed)
7. NXP, *SA612A Double-balanced mixer and oscillator*, product data sheet Rev. 3, 4 June 2014 (input 1.5 kΩ ∥ 3 pF, symmetrical inputs not to be DC-biased, single-ended/balanced input and output configurations, external LO 200–300 mVpp at OSC_B pin 6, Gconv 14/17 dB, NF 5.0 dB, IP3i −13 dBm table vs −15 dBm text, 2.4 mA, 4.5–8 V). https://www.nxp.com/docs/en/data-sheet/SA612A.pdf (datasheet; read in full)
8. W. Hayward, R. Campbell, B. Larkin, *Experimental Methods in RF Design*, ARRL, 2003 — transformer phasing, push-pull and NE602-based receiver practice (chapters not re-checked). (textbook)
