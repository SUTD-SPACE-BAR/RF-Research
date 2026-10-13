---
title: Resistors at RF — thin vs thick film, parasitics, terminations, attenuators and derating
domain: 04-real-components-hf
slug: resistors-at-rf
tags: [resistor, chip-resistor, thin-film, thick-film, parasitic-inductance, parasitic-capacitance, rf-termination, attenuator, pi-pad, t-pad, power-derating, flip-chip, laser-trim]
prerequisites:
  - ../01-circuit-theory/lumped-elements-impedance-admittance.md
  - ../01-circuit-theory/two-port-networks-zyh-abcd.md
related:
  - capacitors-at-rf-mlcc.md
  - pcb-parasitics-traces-vias-pads.md
  - component-models-s2p-spice.md
  - ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md
  - ../06-rf-circuits/rf-switches-attenuators-limiters.md
  - ../17-test-measurement/spectrum-analyzers.md
  - ../17-test-measurement/rf-power-measurement.md
  - ../07-noise-linearity/thermal-noise-and-noise-temperature.md
level: intro
confidence: medium
last_updated: 2026-09-27
---

# Resistors at RF — thin vs thick film, parasitics, terminations, attenuators and derating

## Questions this page answers
- Does a chip resistor still behave like a resistor at 433 MHz, 915 MHz or 2.4 GHz?
- Why are low-value resistors inductive and high-value resistors capacitive at RF?
- Is there a resistor value that stays flat to the highest frequency?
- Thin film or thick film — which for RF?
- How do I make a good 50 Ω termination on a PCB?
- What resistor values do I need for a 3/6/10/20 dB 50 Ω attenuator, and can chip resistors take my transmitter's power?
- How do I derate a chip resistor's power with temperature?
- Why does a 10 kΩ bias resistor on an RF line not isolate as well as I expected?

## TL;DR
- Model: $Z=(R+j\omega L)\parallel\frac{1}{j\omega C}$. Low values are **inductive** (L dominates), high values **capacitive** (C dominates). The value $R=\sqrt{L/C}$ is flat to first order (zero first-order phase) — with 0402-like parasitics (0.4 nH, 0.05 pF incl. pads) that is ≈90 Ω, and 50–200 Ω stays within 10 % to 7–11 GHz (script).
- **High-value resistors don't isolate at RF**: a "10 kΩ" 0402 looks like ≈3.5 kΩ − j4.8 kΩ at 433.92 MHz and ≈170 − j1280 Ω at 2.45 GHz with 0.05 pF of shunt capacitance. For bias feeds use an RF choke or a quarter-wave line plus the resistor.
- **Thin film** (NiCr/TaN, laser-trimmed, flip-chip options) has lower and more repeatable parasitics, tighter tolerance and TCR, and is characterised to 40–70 GHz by vendors (Vishay FC/CH). The part's *internal* parasitics are tiny (0402 flip-chip: 26 fF, ~2 pH); **pads, mounting and vias dominate** at UHF. Thick film is fine at 433/915 MHz for 10–1000 Ω; for precise terminations/attenuators above ~2 GHz prefer thin film.
- **50 Ω termination:** two 100 Ω 0402 in parallel beat one 49.9 Ω by ~7 dB of return loss (with a 0.3 nH ground via): 29 vs 22 dB at 2.45 GHz. Keep the via right at the pad.
- **Attenuators (50 Ω, π):** 3 dB 292.4/17.6 Ω; 6 dB 150.5/37.4 Ω; 10 dB 96.3/71.2 Ω; 20 dB 61.1/247.5 Ω; 30 dB 53.3/789.8 Ω. At **2 W input a 20 dB π pad dumps 1.64 W in its input shunt resistor** — far beyond any 0402 (62.5 mW). Use a coaxial power attenuator to measure a 2 W LoRa module.
- **Derating** (typical thick-film spec): full power to 70 °C, linear to zero at 155 °C — an 0402 is 62.5 mW at 70 °C, 40 mW at 100 °C, 22 mW at 125 °C.

## Intuition (no math)
A chip resistor is a film of resistive material between two metal end caps on a ceramic substrate. Current flowing along the film has a magnetic field around it (inductance); the two end caps, facing each other and the ground plane under the board, form small capacitors. When the resistance is small, the inductive voltage $\omega L$ becomes comparable to $R$ first — the part looks inductive. When the resistance is large, the capacitive current $\omega CV$ bypasses the film first — the part looks capacitive. In between, at about $\sqrt{L/C}$ — conveniently near 50–100 Ω for small chips — the two errors partly cancel.

Making the part smaller shrinks both $L$ and $C$ and pushes all of this higher in frequency. Laser-trim cuts (which lengthen the current path) add inductance and asymmetric fields, which is why RF resistors use "balanced" trims. For practical PCB work at UHF the pads, the solder, the via to ground and the distance to the ground plane matter as much as the resistor itself.

## The math

### Level 1 — the lumped model
$$Z(\omega)=\frac{R+j\omega L}{1+j\omega CR-\omega^2LC}.$$
To first order in ω: $Z\approx R\,[1+j\omega(L/R-RC)]$, so the phase error vanishes when $R^2=L/C$. With $L=0.4$ nH, $C=0.05$ pF: $R_{opt}=89.4\ \Omega$; phase at 1 GHz is +2.4° for 44.7 Ω, 0.0° for 89.4 Ω and −2.4° for 179 Ω (script §1, matching the first-order term).

Frequency where |Z| is 10 % off (same parasitics):

| R | 5 Ω | 20 Ω | 50 Ω | 89 Ω | 200 Ω | 1 kΩ | 10 kΩ |
|---|---|---|---|---|---|---|---|
| 10 % error above | 0.91 GHz | 3.5 GHz | 7.2 GHz | 11.3 GHz | 10.2 GHz | 1.55 GHz | 0.15 GHz |

### Level 2 — what the vendors measure (thin film)
Vishay's technical note 60107 measured NiCr thin-film chips (50–1000 Ω) on alumina from 0.1 to 40 GHz (measurements by Modelithics) and fitted a model with *internal* elements (shunt C across the film, series L) and *external* ones (connection inductance, capacitance to ground, plus a transmission-line model of the pads). Internal values: 0201 flip-chip 0.0206 pF; 0402 flip-chip 0.0262 pF / 0.0019 nH; 0402 wrap-around 0.0392 pF / 0.121 nH; 0603 flip-chip 0.0403 pF / 0.027 nH. Findings: resistors are either shunt-C or series-L dominated depending on value; the smallest case performs best (0201 ≫ 0402 ≈ 0603); flip-chip beats wrap-around; balanced edge-sense trims beat S-cuts which beat L-cuts; and the external (pad/mount) coefficients depend strongly on case size — i.e. **the footprint matters most**. With only internal parasitics, a 0402 flip-chip 50 Ω resistor is 49.98 − j0.98 Ω at 2.45 GHz (script §2) — essentially ideal; the practical error comes from the mounting.

**Thin vs thick film.** Thick film (ruthenium-oxide glass paste, screen-printed and fired) has a granular structure, wider tolerance (1–5 %), higher TCR (±100–200 ppm/°C) and higher current noise; RF parasitics are broadly similar in magnitude for the same case and trim at UHF, but less controlled. Thin film (sputtered NiCr/TaN, photo-patterned) gives 0.1–1 % tolerance, ±5–50 ppm/°C, low noise and repeatable RF behaviour; RF-specific ranges (Vishay FC/CH, Susumu, Mini-Circuits/IMS terminations) are specified to tens of GHz.

### Level 3 — terminations, attenuators, power and noise

**Terminations to ground.** A shunt resistor to ground adds the via inductance in series and pad capacitance in parallel. Paralleling two 2R resistors halves $L$ and doubles $C$ → $\sqrt{L/C}$ halves toward 50 Ω, and the via's share of error is unchanged. Script §3 (0.3 nH via, 0.05 pF pad): 1 × 49.9 Ω 0402 → RL 37/31/22/15 dB at 0.43/0.92/2.45/5.8 GHz; 2 × 100 Ω 0402 → 44/38/29/22 dB; 1 × 49.9 Ω 0603 → 35/28/20/12 dB.

**Attenuator pads.** For a matched 50 Ω π pad of attenuation $A$ dB, $K=10^{A/20}$: shunt $R_{sh}=Z_0\frac{K+1}{K-1}$, series $R_{se}=Z_0\frac{K^2-1}{2K}$. T pad: series $Z_0\frac{K-1}{K+1}$, shunt $Z_0\frac{2K}{K^2-1}$. Power distribution in a π pad with matched load (script §4, 2 W in): 10 dB pad — 1.04 W input shunt, 0.66 W series, 0.10 W output shunt, 0.20 W out; 20 dB — 1.64 W, 0.33 W, 0.016 W; 30 dB — 1.88 W in the input shunt. **The input resistor takes almost all the power.** (Matrix algebra for pads: [two-ports](../01-circuit-theory/two-port-networks-zyh-abcd.md).)

**Power derating.** Chip resistors are rated at an ambient (typically 70 °C) and derated linearly to zero at their maximum film temperature (155 °C for common thick-film series, e.g. Yageo RC; check each datasheet). 0402: 62.5 mW → 51.5 mW (85 °C), 40.4 mW (100 °C), 22.1 mW (125 °C). Pulse power (TX bursts) can exceed continuous ratings only per the vendor's pulse curves; maximum working voltage (typ. 50 V for 0402) also limits high values.

**Noise.** A resistor's thermal noise is $\sqrt{4kTR\Delta f}$ regardless of type; thick film adds excess (1/f "current") noise under DC bias — irrelevant at RF but relevant in bias networks of LNAs and oscillators ([thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md)).

## Design equations & rules of thumb

| Item | Equation / rule | Typical |
|---|---|---|
| Flattest value | $R=\sqrt{L/C}$ | ≈50–100 Ω for 0402/0603 on FR-4 |
| Low-R error | $X\approx\omega L$ | 5 Ω 0402 at 915 MHz: +j2.3 Ω |
| High-R error | shunt $X_C=1/\omega C$ | 0.05 pF: 7.3 kΩ @ 433.92 MHz, 1.3 kΩ @ 2.45 GHz |
| π pad | $R_{sh}=Z_0\frac{K+1}{K-1}$, $R_{se}=Z_0\frac{K^2-1}{2K}$ | 10 dB: 96.3/71.2 Ω |
| T pad | $R_{se}=Z_0\frac{K-1}{K+1}$, $R_{sh}=Z_0\frac{2K}{K^2-1}$ | 10 dB: 26.0/35.1 Ω |
| Power in π input shunt | $P_{in}\,Z_0/R_{sh}=P_{in}\,(K-1)/(K+1)$ | 20 dB: 82 % → 1.64 W of 2 W |
| Derating | $P(T)=P_{70}\,(155-T)/85$ for $T>70$ °C | 0402 @ 100 °C: 40 mW |
| Termination | 2 × 100 Ω ∥ with via at pad | ≈ +7 dB RL vs 1 × 49.9 Ω |

## Worked examples

### 1. Bias resistor on an RF line
Feeding DC to a GNSS antenna through 10 kΩ at 1575 MHz: with 0.05 pF shunt parasitic the resistor's impedance is only ~2 kΩ (mostly capacitive) — still > 40× 50 Ω, so the loading is small (≈0.1 dB), but at 5.8 GHz it would be ~0.55 kΩ. For low loss use an RF choke (≥ 47 nH) in series with the resistor ([inductors](inductors-at-rf.md)).

### 2. Measuring a 2 W LoRa module on a spectrum analyser
Spectrum analyser input: max +20–30 dBm, but for linear measurement keep the mixer below ~−10 dBm. Need ≈40 dB total: a 2 W-rated (preferably 5–10 W) coaxial 30 dB attenuator first (its input element absorbs ~1.9 W), then a 10 dB SMA pad. Never build the first stage from 0402 resistors. ([Spectrum analysers](../17-test-measurement/spectrum-analyzers.md), [RF power measurement](../17-test-measurement/rf-power-measurement.md).)

### 3. A PCB 6 dB pad for a receiver test port (low power)
π: shunt 150 Ω (E96 150), series 37.4 Ω (E96 37.4), 0402 thin film. Mount the shunt resistors with a via directly at each ground pad; expected RL > 25 dB to ~2.5 GHz.

## Practical notes
- **Pads:** keep resistor pads minimal (IPC-7351 nominal or "RF" reduced pads) and on 50 Ω line width where possible; a pad much wider than the line is a shunt capacitor.
- **Ground vias** for terminations: one via per pad side, as close as possible; two vias for > 2 GHz.
- **Resistors in matching networks** (for stability or broadbanding, e.g. a series 10 Ω at a transistor gate) are fine in thick film at UHF; include their inductance in simulation.
- **Power in bursts:** a TX duty cycle does not raise the *peak* voltage/current tolerance; check pulse ratings.
- **JLCPCB:** basic-part thick-film 0402/0603 (Uni-Royal, Yageo) are fine for most UHF uses; thin-film RF parts are extended/consigned.

## Common mistakes & misconceptions
- **"A resistor is frequency independent."** At RF it is an RLC; values far from $\sqrt{L/C}$ drift first.
- **"High-value resistors isolate RF."** Shunt capacitance of tens of fF bypasses them at GHz.
- **"Any 1 % resistor makes a good termination."** Return loss above 1–2 GHz is set by the via and pad, not the resistor tolerance.
- **Putting a chip pad attenuator in front of a watt-level transmitter** — the first resistor burns out (and may take the analyser input with it).
- **Forgetting derating** at the high temperatures inside a rocket avionics bay or near a PA.

## How to simulate / verify
- `python3 tools/verify/components_resistors.py` — RLC resistor model, flatness at $\sqrt{L/C}$, Vishay internal-parasitic effect, termination return loss, attenuator values and power split, derating.
- Vendor S-parameters/models: Vishay (FC/CH series), Modelithics resistor libraries; add the pad/via model.
- Bench: VNA one-port measurement of a PCB termination; two-port for a pad (check $S_{21}$ and both return losses).

## Open questions / gaps
- The 0.4 nH / 0.05 pF "mounted" parasitics are order-of-magnitude assumptions (consistent with Vishay's statement that external/pad effects dominate); real values depend on stackup and should come from EM simulation or measurement — hence page confidence "medium".
- Pulse-power ratings of common JLCPCB resistors at RF duty cycles are not tabulated.

## Sources
1. Vishay Intertechnology, "Frequency response of thin film chip resistors," Technical Note 60107, rev. 04-Feb-2009 — 0.1–40 GHz measurements, lumped model, internal parasitics by case size, trim and termination effects. https://www.vishay.com/docs/60107/freqresp.pdf (app note)
2. Vishay, "FC series high frequency (up to 40 GHz) resistor, thin film," datasheet 60093. https://www.vishay.com/docs/60093/fcseries.pdf (datasheet)
3. Yageo, "General purpose chip resistors RC0402," datasheet — 62.5 mW rating, derating 70 → 155 °C. https://datasheet.octopart.com/RC0402FR-07100KL-Yageo-datasheet-8324255.pdf (datasheet)
4. D. M. Pozar, *Microwave Engineering*, 4th ed., 2012 — attenuator networks via ABCD/S matrices; terminations. (textbook)
5. R. Ludwig, G. Bogdanov, *RF Circuit Design*, 2nd ed., 2009 — §1.4 high-frequency resistors (RLC model, value dependence). (textbook)
6. W. Hayward, R. Campbell, B. Larkin, *Experimental Methods in RF Design*, ARRL, 2003 — attenuator pads and terminations for test. (textbook)
7. Verification script `tools/verify/components_resistors.py` (this KB).
