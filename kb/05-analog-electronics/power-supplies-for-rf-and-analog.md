---
title: Power supplies for RF and analog — LDO PSRR and noise, switcher ripple and spurs, LC/ferrite post-filters, ground bounce, sequencing, battery-powered bursts, references
domain: 05-analog-electronics
slug: power-supplies-for-rf-and-analog
tags: [ldo, psrr, ldo-noise, switching-regulator, buck, ripple, spurs, pushing, lc-filter, ferrite-bead, damping, middlebrook, ground-bounce, supply-sequencing, battery, lipo, internal-resistance, brown-out, lora-pa-current, voltage-reference, bandgap]
prerequisites:
  - op-amps-real-limitations.md
  - ../01-circuit-theory/resonance-and-q.md
  - ../04-real-components-hf/ferrites-and-beads.md
related:
  - oscillators.md
  - data-converters-adc-dac.md
  - low-noise-analog-design.md
  - analog-signal-conditioning.md
  - fets-mosfet-jfet-gaas-gan.md
  - ../13-pcb-rf-layout-emc/power-distribution-decoupling-for-rf.md
  - ../13-pcb-rf-layout-emc/grounding-and-return-paths.md
  - ../13-pcb-rf-layout-emc/mixed-signal-layout.md
  - ../15-lora-ism-radios/rocket-telemetry-radio-design.md
  - ../04-real-components-hf/capacitors-at-rf-mlcc.md
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# Power supplies for RF and analog — LDO PSRR and noise, switcher ripple and spurs, LC/ferrite post-filters, ground bounce, sequencing, battery-powered bursts, references

## Questions this page answers
- How much switching-regulator ripple gets through an LDO at 1–2 MHz, and why does PSRR fall with frequency?
- How noisy is an LDO (µV rms), and does it matter for my ADC, VCO or sensor?
- How big is a buck converter's output ripple, and why is it often larger than the formula says?
- How do supply ripple and noise show up as spurs next to my LO or transmitter carrier?
- How do I design an LC or ferrite-bead post-filter that does not resonate and make things worse?
- What happens to a 1S LiPo when a 2 W LoRa module draws 1 A+ bursts through a buck-boost — and to my sensor readings?
- What is ground bounce, and how big is it?
- Why must some RF amplifiers be powered up in a particular order?
- What makes a good voltage reference?
- How big a reservoir capacitor does my rectifier need, and why is a bridge better than a half-wave rectifier?
- What is the difference between a series and a shunt (Zener) regulator, and what does the capacitor across the Zener do?
- Should a transmitter run from a switching or a linear supply?
- How do I build a bench supply for a 2 W LoRa module?
- Which battery chemistry should I use, and how long will it last?
- Why does my flight computer reset when the radio transmits on a cold morning?

## TL;DR
- **LDO PSRR** is high at low frequency (loop gain) and falls through 100 kHz–1 MHz: TPS7A20 at 300 mA: 65/92/75/60/40 dB at 100 Hz/1 k/10 k/100 k/1 MHz [1]. 10 mV of 1 MHz buck ripple → ≈ 100 µV after the LDO (`tools/verify/analog_power.py` §3). Switchers run at 0.5–3 MHz, exactly where LDOs are weakest → add an LC/ferrite pre-filter or choose an LDO with MHz PSRR.
- **LDO noise:** 7 µV rms (10 Hz–100 kHz) for a low-noise LDO (TPS7A20 [1]) vs ≈ 99 µV rms (10 Hz–10 kHz, 0.003 % of V_out) for a generic AMS1117-3.3 [2] — a 14× difference in rms over a narrower band, ≈ 45× in average density (§1).
- **Buck ripple:** $\Delta I_L = (V_{in}-V_{out})D/(Lf_{sw})$, $\Delta V \approx \Delta I_L/(8f_{sw}C) + \Delta I_LR_{ESR}$ + ESL spikes. 5 → 3.3 V, 2 MHz, 2.2 µH: 255 mA p-p ripple current; 1.6 mV (capacitive) + 1.3–5 mV (ESR) with a derated 10 µF (§2). MLCCs lose ≥ 50 % of capacitance at rated-ish DC bias.
- **Ripple → spurs:** VCO pushing $K_p$ (Hz/V) with ripple $V_r$ at $f_r$: sidebands at $f_0 \pm f_r$ of $20\log(K_pV_r/2f_r)$ dBc — 1 MHz/V × 1 mV at 1 MHz → −66 dBc. A saturated PA whose output amplitude ∝ $V_{DD}$: $20\log(V_r/2V_{DD})$ — 10 mV on 5 V → −60 dBc (§5).
- **LC/bead filters resonate:** 1 µH + 10 µF peaks +14.6 dB at 50 kHz (lightly loaded); a bead (~1.5 µH at low frequency) + 1 µF peaks +22 dB at 130 kHz. Damp with an R–C leg: $C_d = 4C$, $R_d ≈ \sqrt{L/C}$ → peak +1.1 dB while keeping −64 dB at 2 MHz (§3–4).
- **Battery bursts:** an E22-400T33D-class 2 W module draws 850–1200 mA when transmitting and needs ≥ 5 V for full power [3]. Through a 5 V buck-boost from a 1S cell (η ≈ 0.88, 130 mΩ battery + wiring), 1.2 A at the radio means 1.7–2.3 A from the cell and 0.22–0.30 V of droop (§6). Plan brown-out thresholds, bulk capacitance, and *separate* PA return currents from sensor/ADC grounds: 1.2 A through 5 mΩ of shared ground = 6 mV = 7 LSB of a 12-bit, 3.3 V ADC.
- **Ground bounce** $V = L\,di/dt$: 1 nH × 50 mA/1 ns = 50 mV — digital edges, not the PA's slow burst, are usually the worst (§7).
- **Sequencing:** depletion-mode GaAs/GaN PAs need negative gate bias before drain voltage (→ [FETs](fets-mosfet-jfet-gaas-gan.md)); many ADCs/FPGAs have supply-order or ramp requirements.

- **Rectifiers:** ripple ≈ $I/fC$ (half-wave), $I/2fC$ (bridge) — conservative; a 9 V rms, 4700 µF bridge at 1.2 A simulates 9.0 V peak / 1.54 V p-p with 4.3 A diode pulses (`tools/verify/s3_rectifier_battery.py`). Series regulators waste $(V_{in}-V_{out})I$; shunt (Zener) regulators waste their full current at light load and reject ripple only by $r_z/(R+r_z)$.
- **Batteries:** use Wh, not Ah, behind converters; a constant-power load collapses when $V_{oc}^2 < 4RP$. A 1S pack feeding a 6 W radio burst stays above 3.5 V at 25 °C but falls to 2.86 V at −20 °C and 3.7 V open-circuit (cell 300 mΩ assumed) — below a 3.0 V brown-out. Peukert $k$ ≈ 1.05 (Li-ion) vs 1.1–1.3 (lead-acid); alkaline cells (150–300 mΩ) cannot feed 1 A bursts.

## Intuition (no math)
A linear regulator (LDO) is an op-amp driving a pass transistor so that the output copies a reference. It rejects input ripple only as well as its loop gain allows — lots at low frequency, little above its loop bandwidth (tens of kHz to ~1 MHz). Above that, only the output capacitor and the pass device's own isolation help. A switching regulator is efficient but, by design, chops current at hundreds of kHz to a few MHz, leaving ripple and fast edge "spikes" at the fundamental and harmonics — right where the LDO is weakest. So the usual clean-rail recipe is: switcher (efficiency) → passive LC or ferrite filter (kills MHz) → LDO (kills low-frequency ripple and load steps) → local decoupling.

A passive LC filter is a resonant circuit: below resonance it passes, above it attenuates at 40 dB/decade, and *at* resonance it can amplify if nothing dissipates energy. Real loads (an LDO, an RF IC) often present little damping, so an undamped filter can turn a small ripple at the resonance into a big one. Adding a resistor in series with an extra capacitor across the output damps it without wasting DC power.

Any supply wobble reaches RF signals: an oscillator's frequency shifts slightly with supply voltage ("pushing"), and an amplifier's gain or output swing does too. Periodic ripple becomes discrete sidebands (spurs) around the carrier; random supply noise becomes phase/amplitude noise.

A battery is a voltage source with internal resistance. A big current pulse (a LoRa PA transmitting) drops the terminal voltage by I × R instantly, and a regulator downstream draws *more* current as its input voltage falls (constant power). Everything that shares the battery, the converter or the ground return sees the disturbance.

## The math

### Level 1 — key relations

**PSRR:** $PSRR(f) = 20\log_{10}(\Delta V_{in}/\Delta V_{out})$. Ripple through a chain multiplies: total rejection (dB) = sum of stage rejections (dB), if impedances don't interact.

**Buck converter ripple (continuous conduction):**
$$D = \frac{V_{out}}{V_{in}},\quad \Delta I_L = \frac{(V_{in}-V_{out})D}{Lf_{sw}},\quad \Delta V_{out} \approx \frac{\Delta I_L}{8f_{sw}C} + \Delta I_L\,ESR\ (+\ ESL\ \text{spikes}).$$

**Second-order LC filter** (series L with resistance $R_L$, shunt C, load R):
$$H(s) = \frac{1}{1 + (sL + R_L)(sC + 1/R)},\quad f_r = \frac{1}{2\pi\sqrt{LC}},\quad Z_0 = \sqrt{L/C},\quad Q \approx \frac{Z_0}{R_L + Z_0^2/R}.$$
Attenuation ≈ $(f/f_r)^2$ (40 dB/decade) well above $f_r$.

**Spurs from ripple** (sinusoidal ripple $V_r$ at $f_r$):
- FM via VCO pushing $K_p$: modulation index $\beta = K_pV_r/f_r$; each sideband $≈ 20\log(\beta/2)$ dBc (small β).
- AM on a PA with amplitude ∝ $V_{DD}$: $m = V_r/V_{DD}$; each sideband $20\log(m/2)$ dBc.

**Battery droop:** $V_{term} = V_{oc} - I R_{int}$; with a regulator of efficiency η delivering $P_{out}$: $I_{in} = P_{out}/[\eta(V_{oc} - I_{in}R)]$ → $I_{in} = \dfrac{V_{oc} - \sqrt{V_{oc}^2 - 4RP_{out}/\eta}}{2R}$.

**Ground bounce / IR shift:** $\Delta V = L\,di/dt + I R$.

### Level 2 — derivations and design

**Why LDO PSRR falls with frequency.** Input ripple couples to the output through the pass device (its output resistance and capacitance) and is then corrected by the loop: $PSRR \approx$ (feed-through attenuation) × (1 + loop gain). The loop gain rolls off from its dominant pole (often set by the output capacitor and load) — typically giving 60–90 dB at 1 kHz but only 20–45 dB at 1 MHz; beyond the loop's unity-gain frequency the output capacitor's impedance vs the pass device's impedance sets a floor, and the capacitor's ESL eventually ruins it. The PSRR also degrades near dropout (little $V_{in}-V_{out}$ headroom → pass device in triode) and at high load current: TPS7A20 at 1 MHz is 45 dB at 20 mA but 40 dB at 300 mA; at 100 Hz, 95 vs 65 dB [1]. Give an LDO ≥ 300–500 mV headroom if PSRR matters.

**LDO noise.** Output noise is the reference (bandgap) noise times the error amplifier's closed-loop gain ($V_{out}/V_{ref}$) plus the amplifier's own noise; many LDOs therefore quote noise as a fraction of $V_{out}$ (AMS1117: 0.003 % of $V_{out}$, 10 Hz–10 kHz → 99 µV rms at 3.3 V [2]). Low-noise LDOs filter the reference with an internal or external "noise-reduction" capacitor or use a current-reference architecture whose noise does not scale with $V_{out}$ (TPS7A20: 7 µV rms, 10 Hz–100 kHz, no bypass capacitor [1]). Average densities if white: 22 nV/√Hz vs ≈ 1 µV/√Hz (§1). For a 16-bit ADC on 3.3 V (50 µV LSB) an AMS1117 supplying the reference path would add ~2 LSB rms of noise; for a VCO, supply noise × pushing becomes phase noise ($K_pv_n$ Hz/√Hz; see [oscillators](oscillators.md)).

**Buck ripple (derivation and the real-world extras).** In steady state the inductor sees $V_{in}-V_{out}$ for $DT$: $\Delta I_L = (V_{in}-V_{out})DT/L$. The ripple current (triangle, zero mean) flows into the output capacitor; the charge in one half-cycle is $\frac12\cdot\frac{\Delta I_L}{2}\cdot\frac T2$, so $\Delta V_C = \Delta I_L/(8fC)$. The ESR adds $\Delta I_L\cdot ESR$ (a triangle in phase with the current), and the ESL adds spikes at every switching edge ($L_{ESL}\,di/dt$ with di/dt of the *switch-node* current in the input loop, coupled into the output) — tens of mV at 50–300 MHz in poor layouts. Example (§2): 5 → 3.3 V, 2 MHz, 2.2 µH: $\Delta I_L$ = 255 mA; with 22 µF nominal (≈ 10 µF after DC bias), 5 mΩ: 1.6 mV + 1.3 mV. The formula's number is rarely the problem; the spikes and the switching harmonics coupled by layout are (→ [decoupling](../13-pcb-rf-layout-emc/power-distribution-decoupling-for-rf.md)).

**Designing and damping an LC post-filter.** Choose $f_r$ a decade (≥ 40 dB) or more below $f_{sw}$. Example: 1 µH (50 mΩ DCR) + 10 µF: $f_r$ = 50 kHz, $Z_0$ = 0.32 Ω; at 2 MHz −64 dB. But lightly loaded (11 Ω) it peaks +14.6 dB at 50 kHz (Q ≈ 5) (§3) — any load step or ripple component near 50 kHz is amplified, and an LDO or switcher downstream may even interact with it. Middlebrook's approach: add a damping leg $R_d$ + $C_d$ across the output; with $C_d = nC$, the peak falls sharply for n ≈ 4 and $R_d ≈ Z_0$: +1.1 dB peak, −64 dB at 2 MHz unchanged (§3) [4]. Alternatives: an electrolytic/polymer capacitor whose ESR provides $R_d$ naturally; a resistor in parallel with the inductor (costs HF attenuation); or simply a series resistor if the load current is small (RC filter for op-amp or reference rails).
Middlebrook's input-filter criterion also applies when a filter *feeds* a switcher: the regulator's input looks like a negative resistance ($-V_{in}^2/P$); the filter's peak output impedance must stay well below it, or the converter oscillates [4].

**Ferrite beads.** At low frequency a bead is mostly an inductor (≈ 0.3–2 µH for common 0603/0805 parts) with small DCR; its lossy (resistive) region lies above ~10–100 MHz. So bead + MLCC is an LC filter with a resonance in the tens-to-hundreds of kHz and high Q: 1.5 µH + 1 µF → +22 dB peak at 130 kHz (§4). Beads are excellent at stopping VHF/UHF noise (and RF from a nearby transmitter) from travelling along a rail, poor at stopping kHz switching ripple, and their inductance collapses under DC bias current. Use them with a damping capacitor/resistor or where the resonance is harmless (→ [ferrites & beads](../04-real-components-hf/ferrites-and-beads.md)).

**Ripple to spurs (derivation).** A VCO with pushing $K_p$ and supply $V_r\cos\omega_rt$ produces $\phi(t) = (K_pV_r/f_r)\sin\omega_rt$ — narrowband FM with index β = $K_pV_r/f_r$ and first sidebands $J_1(\beta)/J_0(\beta) ≈ \beta/2$. So 1 mV at 1 MHz with $K_p$ = 1 MHz/V → −66 dBc; the same ripple at 100 kHz → −46 dBc (lower-frequency ripple is worse for FM) (§5). Inside a PLL loop bandwidth the loop suppresses VCO pushing, outside it does not. For a saturated PA (output amplitude ∝ $V_{DD}$), supply ripple amplitude-modulates: $20\log(V_r/2V_{DD})$ — 10 mV on 5 V → −60 dBc. Transmit-spectrum masks and receiver blocking performance both care; LoRa's own spreading helps the receiver little against a strong discrete spur within the channel.

**1S battery + buck-boost + LoRa PA burst.** Model: open-circuit cell voltage $V_{oc}$, $R$ = internal resistance + connector/wiring (0.10 + 0.03 Ω, representative of a small LiPo — measure yours), converter η = 0.88, radio 5 V × 1.2 A (upper end of the E22-400T33D's 850–1200 mA [3]). Solving the constant-power equation (§6): at 4.2 V, 1.71 A and 0.22 V droop; at 3.7 V, 1.98 A and 0.26 V; at 3.3 V, 2.27 A and 0.30 V (terminal 3.0 V). Consequences:
- Converter input current limit and inductor saturation must cover ≈ 2.3 A plus ripple at end-of-discharge; the cell's own current rating and cold-temperature resistance (higher on a cold launch rail) matter.
- The MCU and sensor rails fed from the same cell see the droop; set brown-out detection and converter UVLO consistently and test at minimum cell voltage.
- If the source is current-limited (USB bench supply, a small cell), bulk capacitance must supply the burst: $C = I\Delta t/\Delta V$ → 1200 µF for 1.2 A for 100 µs at 100 mV; for a millisecond-scale LoRa packet (hundreds of ms at high SF) capacitors cannot carry it — the source must.
- Ground: the PA return current (≈ 1–2 A) must not share copper with sensor/ADC returns: 1.2 A × 5 mΩ = 6 mV = 7 LSB (12-bit) or 119 LSB (16-bit) (§6). This is one plausible contributor to "noise only when transmitting" symptoms (compare the Space Bar lesson of magnetometer offsets from a shared, unfiltered regulator) — give sensors their own filtered rail and keep the radio's supply loop and return tight (→ [grounding](../13-pcb-rf-layout-emc/grounding-and-return-paths.md)).
- EBYTE's own guidance: use a regulated supply with low ripple, reliable grounding, and ≥ 30 % current margin [3].

**Ground bounce.** $L\,di/dt$ across shared return inductance: a PA burst ramping 1.2 A in 2 µs across 10 nH is only 6 mV, but a digital output switching 50 mA in 1 ns across 1 nH is 50 mV (§7). Fast digital edges and switcher loops, not slow PA envelopes, dominate bounce; solid planes and short return paths are the cure.

**Voltage references.** Bandgap references (≈ 1.2 V core, scaled up) are the norm: 1/f noise of a few µV p-p (0.1–10 Hz) per volt for good parts, drift 2–20 ppm/°C, thermal hysteresis and long-term drift; buried-Zener references (≈ 7 V) are quieter and more stable but need higher supply. A reference buffer (low-noise op-amp) with a large low-ESR capacitor at the ADC's REF pin supplies SAR charge pulses (→ [data converters](data-converters-adc-dac.md)). Using the supply rail as the ADC reference makes every supply ripple a measurement error — unless the measurement is ratiometric (bridge excited from the same rail; → [signal conditioning](analog-signal-conditioning.md)).

**Sequencing and soft start.** Depletion-mode RF devices (GaN, GaAs D-pHEMT) need the negative gate supply up before the drain supply (→ [FETs](fets-mosfet-jfet-gaas-gan.md)); ADCs/FPGAs may require core-before-I/O or monotonic ramps; LDO/switcher soft-start limits inrush into large capacitances (hot-plugging a battery into hundreds of µF causes connector arcing and supply overshoot from cable inductance — add a TVS or series damping).

### Mains supply fundamentals — rectifiers, ripple, series and shunt regulators, SMPS vs linear for a transmitter
Numbers below are from `tools/verify/s3_rectifier_battery.py` §1–3 (ngspice; output in `_output.txt`). Mains: Singapore 230 V, 50 Hz.

**Rectifiers.** A transformer secondary of $V_{rms}$ has peak $\sqrt2V_{rms}$.
- **Half-wave** (one diode) charges the reservoir capacitor once per cycle.
- **Full-wave**, either centre-tapped with two diodes or a **bridge** with four, charges it twice per cycle. A bridge loses 2 $V_F$ at the peak, a centre-tap 1 $V_F$ but needs twice the winding.

Between peaks the capacitor supplies the load current alone, so with the discharge assumed to last the whole period [5][11]:
$$\Delta V_{pp} \approx \frac{I}{fC}\ \text{(half-wave)},\qquad \Delta V_{pp} \approx \frac{I}{2fC}\ \text{(full-wave/bridge)},\qquad V_{peak} \approx \sqrt2V_{rms} - nV_F - I_{pk}R_w .$$
The diode conducts only near the peak, for a conduction angle θ. To replace the charge $I\,T$ in that short time, the peak current is several times $I$. That raises $V_F$, the drop in the winding resistance $R_w$, transformer heating and harmonic mains current. A capacitor-input supply needs a transformer VA rating of ≈ 1.6–1.8 × the DC power.

ngspice check (9 V rms secondary, $R_w$ = 0.5 Ω, 1N4007-class diodes, 4700 µF, 1.2 A constant load):

| | Peak | Trough | Ripple (sim) | Formula | Diode peak current | Conduction |
|---|---|---|---|---|---|---|
| Half-wave | 9.50 V | 5.68 V | 3.82 V p-p | $I/fC$ = 5.11 V | 7.0 A | 93° |
| Bridge | 9.04 V | 7.49 V | 1.54 V p-p | $I/2fC$ = 2.55 V | 4.3 A | 76° per pulse |

Two lessons from the table:
- The ideal 12.73 V peak shrinks to 9.0 V once $I_{pk}R_w$ and 2 $V_F$ at 4 A are counted. The $I/2fC$ formula is *conservative*, by 40 % here, because recharge takes a sizeable part of the cycle. Use it for design and simulate for the real numbers.
- A bleeder resistor across the reservoir discharges it when the supply is off (safety for large capacitors). A small RC or ferrite after the bridge suppresses diode-switching hash that otherwise reaches a receiver as broadband noise at 100 Hz repetition.

**Series (linear) regulators.** A pass transistor in series, controlled by an error amplifier against a reference, drops $V_{in}-V_{out}$ and passes the load current. Efficiency ≈ $V_{out}/V_{in}$; dissipation $(V_{in}-V_{out})I$. The input trough must stay above $V_{out} + V_{dropout}$ at minimum mains: that is the design constraint, not the average. Classic LM317/LM1085-class parts need ≈ 1.3–2.5 V; modern LDOs need 0.1–0.6 V at their rated current.

**Shunt regulators.** A Zener (or a TL431) in parallel with the load, fed through a resistor R, holds the voltage by sinking whatever the load does not take:
$$R = \frac{V_{in,min}-V_Z}{I_{L,max}+I_{Z,min}},\qquad P_{Z,max} = V_Z\frac{V_{in,max}-V_Z}{R}\ \text{(at no load)} .$$
For a 5.1 V, 0–20 mA rail from 12 V ± 1 V: R = 236 Ω (use 220 Ω); at no load the Zener dissipates 183 mW and the resistor 284 mW. The input current is *constant*, so a shunt regulator wastes power at light load. It is used for references and µA–mA rails, and for clamping. Ripple rejection is $r_z/(R+r_z)$, with Zener dynamic resistance $r_z$ ≈ 10–30 Ω: ngspice gives 100 mV out for 2 V p-p in. A **ripple-bypass capacitor** across the Zener helps only where its reactance is below $r_z$. 100 µF (15.9 Ω at 100 Hz) only reaches 82 mV, while 1000 µF gives 14 mV. Its main value is removing the Zener's avalanche noise above ~1 kHz (→ [Zener noise](diodes-schottky-pin-varactor.md)).

**SMPS vs linear for a transmitter.** Take 5 V at 1.2 A (E22-400T33D in TX) from a 12 V adapter. A linear regulator is 42 % efficient and dissipates 8.4 W, which needs a large heatsink. A buck at ~90 % loses 0.67 W, but puts ripple and edge spikes at $f_{sw}$ and its harmonics onto the PA supply. That gives AM/PM spurs at $f_c \pm f_{sw}$ (ripple-to-spurs above: 10 mV on 5 V → −60 dBc). It also radiates hash into the receiver. The usual answer is buck → damped LC → (optionally) LDO with ≥ 0.4 V headroom (Worked example 1). A battery-powered flight computer uses switchers for efficiency. A bench or ground-station supply can afford linear regulation when the input is only a few volts above the output.

### Batteries — chemistries, internal resistance, Ah → runtime, cold and Peukert
Typical per-cell values (ranges from Linden's handbook [7] and representative datasheets [8]; a specific cell's datasheet overrides them):

| Chemistry | Nominal / full / cut-off (V) | Specific energy | Internal resistance (small cells, 25 °C) | High-current pulses | Cold | Notes |
|---|---|---|---|---|---|---|
| Li-ion / LiPo (LCO, NMC) | 3.6–3.7 / 4.20 / 3.0 | 150–250 Wh/kg | ≈ 10–100 mΩ (high-rate pouches lowest) | excellent in "C-rated" pouches; energy-type 18650s 1–2C | resistance rises steeply below 0 °C; **never charge below 0 °C** (lithium plating) | Space Bar packs: 1S (Avionics C) and 2S (Avionics B) |
| LiFePO₄ | 3.2–3.3 / 3.6–3.65 / 2.0–2.5 | 90–160 Wh/kg | very low in power cells (mΩ) | excellent | as Li-ion | flat curve, safer chemistry; 1S is too low for a 3.3 V LDO |
| NiMH | 1.2 / 1.4–1.5 (charging) / 1.0 | 60–120 Wh/kg | ≈ 20–50 mΩ (AA) | good | moderate | low-self-discharge types hold charge for a year |
| Alkaline (Zn/MnO₂) | 1.5 / 1.6 / 0.8–0.9 | high at low drain only | **150–300 mΩ fresh** (Energizer E91 [8]), rising with use | poor | poor (E91 rated −18 to 55 °C [8]) | fine for µA–mA loads; cannot feed a 1 A radio burst |
| Sealed lead-acid | 2.0 / 2.3–2.45 (charging) / 1.75 | 30–40 Wh/kg | low (large cells) | good | capacity falls in cold | ground-station batteries; strong Peukert effect |

**Internal resistance vs pulse current.** Model the cell as $V_{oc}$ in series with an ohmic $R_0$ (electrolyte, contacts) and one or more R‖C "polarisation" branches (charge transfer, diffusion; time constants of ms to minutes). A pulse first drops $IR_0$ instantly, then sags further as the RC branches charge. A DC pulse test (ΔV/ΔI after 10 ms and after 1 s) is the useful bench number. A 1 kHz AC-IR meter reads only $R_0$ and is optimistic. With a regulator downstream the load is **constant power**, so the current rises as the voltage falls. The constant-power solution above has no solution at all when $V_{oc}^2 < 4RP$: the converter input collapses and the board browns out.

**Ah → runtime.** Runtime ≈ usable energy / average power: $t = (C_{Ah}V_{nom}\cdot u)/\bar P_{bat}$, where $u$ is the usable fraction (depth to the cut-off, temperature, ageing). Use energy (Wh), not Ah, when the load sits behind a converter. **Peukert's law**, $t = H\,(C/(IH))^k$ for a capacity $C$ rated over $H$ hours, describes the rate dependence. $k$ ≈ 1.0–1.1 for Li-ion (1 Ah at 2 A: 29.0 instead of 30 min) and ≈ 1.1–1.3 for lead-acid (25 min). It is a fit, not physics, and it ignores temperature and rest recovery.

**Cold.** Below room temperature the electrolyte conductivity falls and the charge-transfer resistance rises. Below about −20 °C charge transfer dominates the cell's resistance [9]. Commercial Li-ion cells are reported at roughly 10× room-temperature resistance at −20 °C (review quoted in the log; cell-dependent). Available capacity also falls, with NCA/NMC cells reaching only about half depth at −20 °C in one DOE-lab study [10]. Launch sites at dawn, high-altitude balloons and the cold-soaked airframe on the pad are therefore the design corners. Remedies:
- keep packs warm until launch (insulated bay, pocket, a heater on the pad);
- size the pack for cold resistance, not room-temperature capacity;
- raise the converter UVLO hysteresis so that a burst does not cause a reset loop;
- schedule high-power transmissions *after* the pack has self-heated, where the mission allows.

### Level 3 — subtleties
- **PSRR is measured with a specific output capacitor and load;** a different capacitor changes it. LDO stability also depends on the output capacitor's ESR/ESL (some old LDOs need ESR; modern ones are MLCC-stable, e.g. TPS7A20 with ≥ 1 µF [1]).
- **Spread-spectrum switchers** smear spurs into a noise pedestal — good for EMC tests, but the total power is the same; for radios, a fixed, known frequency placed outside sensitive bands (and synchronised to the ADC/radio clock) is often better.
- **Switcher frequency planning:** pick $f_{sw}$ and harmonics away from IFs, ADC Nyquist bands and receive channels; beware harmonics landing in the 433/868/915 MHz bands (≈ the 200th–400th harmonic of a 2 MHz switcher still carries measurable energy from fast edges).
- **Thermoelectric and dielectric absorption effects** matter for µV references and integrators (→ [low-noise design](low-noise-analog-design.md)).
- **Load transients:** LDO recovery time and output capacitor size set the dip when a radio switches from RX (≈ 15 mA) to TX (≈ 1 A) [3]; this dip can momentarily reset MCUs on shared rails.

## Design equations & rules of thumb

| Quantity | Equation / rule | Typical |
|---|---|---|
| Cascade rejection | sum of dB (stages isolated) | switcher → LC (40–60 dB) → LDO (40–90 dB) |
| LDO headroom | ≥ 300–500 mV for PSRR | PSRR collapses near dropout |
| Buck ripple current | $(V_{in}-V_{out})D/(Lf_{sw})$ | 20–40 % of $I_{out}$ |
| Output ripple | $\Delta I_L/(8fC) + \Delta I_L ESR$ + spikes | mV + spikes |
| MLCC DC bias | derate 30–80 % near rated V | check curves |
| LC filter | $f_r = 1/2\pi\sqrt{LC}$ ≤ $f_{sw}/10$ | 40 dB/decade |
| Damping | $C_d ≈ 4C$, $R_d ≈ \sqrt{L/C}$ | peak ≈ +1 dB |
| Bead + cap | resonance tens–hundreds kHz, high Q | add damping |
| VCO pushing spur | $20\log(K_pV_r/2f_r)$ dBc | — |
| PA AM spur | $20\log(V_r/2V_{DD})$ dBc | −60 dBc for 10 mV/5 V |
| Battery current | $P_{out}/(\eta V_{term})$ | 1.7–2.3 A for 6 W from 1S |
| Hold-up capacitance | $C = I\Delta t/\Delta V$ | mF for 100 µs–1 ms |
| Ground IR shift | $I R_{shared}$ | 6 mV per 1.2 A × 5 mΩ |
| Ground bounce | $L\,di/dt$ | 50 mV for 50 mA/ns/nH |
| Reservoir ripple | $I/fC$ half-wave, $I/2fC$ full-wave | conservative; 2.55 V for 1.2 A, 4700 µF, 50 Hz bridge |
| Rectifier peak | $\sqrt2V_{rms} - nV_F - I_{pk}R_w$ | 12.7 → 9.0 V (9 V rms, 1.2 A) |
| Transformer rating | ≈ 1.6–1.8 × DC power | capacitor input |
| Linear headroom | trough at low mains ≥ $V_{out} + V_{DO}$ | design at −10 % mains |
| Zener resistor | $(V_{in,min}-V_Z)/(I_{L,max}+I_{Z,min})$ | no-load $P_Z = V_Z(V_{in,max}-V_Z)/R$ |
| Battery collapse | $V_{oc}^2 < 4RP_{in}$ | 3.10 V for 0.33 Ω, 7.3 W |
| Runtime | $C_{Ah}V_{nom}u/\bar P$ | 2.45 h for 1 Ah, 1.21 W, u = 0.8 |
| Peukert | $t = H(C/IH)^k$ | k 1.05 Li-ion, 1.1–1.3 lead-acid |

## Worked examples

### 1. A clean 3.3 V rail for a GNSS/LoRa front end from a 5 V buck
Buck (2 MHz): ≈ 3–5 mV ripple + edge spikes at the output. Chain: 1 µH + 10 µF (+ 40 µF / 0.33 Ω damping leg, or a polymer capacitor with that ESR) → −64 dB at 2 MHz, ≈ +1 dB peak (near 26 kHz) → then a low-noise LDO with ≥ 0.4 V headroom (so the buck is set to ≈ 3.8 V): PSRR 60 dB at 100 kHz, 40 dB at 1 MHz [1]. Net 2 MHz ripple: 5 mV × 10^(−64/20) × 10^(−40/20) ≈ 30 nV — the switcher is gone; what remains is the LDO's own 7 µV rms noise and layout coupling.

### 2. Spur budget for a VCO on a switcher-derived rail
VCO pushing 5 MHz/V (datasheet), rail ripple 1 mV at 1 MHz → −52 dBc sidebands at ±1 MHz (§5). Target −80 dBc → need 28 dB more rejection at 1 MHz: an LC stage (≥ 40 dB at 1 MHz with $f_r$ ≤ 100 kHz) does it; an LDO alone (40 dB) barely does.

### 3. Flight computer: 2 W LoRa burst on a 1S pack
From §6: at 3.3 V end-of-charge the buck-boost draws 2.3 A and the cell terminal drops to 3.0 V. Design actions: (i) converter rated ≥ 3 A input, (ii) MCU brown-out below 3.0 V at the converter input but above the MCU regulator's dropout, (iii) radio supply on its own buck-boost (as on Avionics C) with ≥ 100 µF low-ESR bulk at the module, (iv) PA return current kept out of the sensor ground (star at the battery/converter), (v) test by keying the radio continuously at minimum pack voltage and cold temperature while logging sensor data — look for offsets correlated with TX.

### 4. Why the "filtered" rail got noisier
A 600 Ω@100 MHz bead + 1 µF feeding a sensor rail: resonance ≈ 130 kHz with Q ≈ 12 (§4) — a 1.2 MHz switcher's subharmonic or the sensor's own 100 kHz current pulses get amplified ~20 dB. Fix: raise C to 10 µF *and* add a damping leg (or use a resistor instead of the bead for a low-current rail: 10 Ω + 10 µF is a 1.6 kHz RC with no resonance).

### 5. A bench supply for a 2 W LoRa module (E22-400T33D: 5 V, 1.2 A in TX)
Linear option (script §1–2): 230 V → 9 V rms, ≥ 17 VA transformer → bridge (≥ 3 A diodes; they carry 4.3 A pulses) → 4700 µF → 5 V LDO.
- **Headroom.** The trough is 7.49 V nominal and ≈ 6.6 V at −10 % mains. A 1.3 V-dropout regulator just works; an LM317-class part with ≈ 2 V dropout does not. A 10–12 V secondary adds margin at the cost of dissipation.
- **Dissipation.** $(8.28 - 5)\times1.2$ = 3.9 W in continuous TX (0.44 W average at 10 % duty). For $T_J$ ≤ 125 °C at 40 °C ambient in TO-220 (θ_JC 3 K/W, 0.5 K/W pad), the heatsink needs θ_SA ≤ 18 K/W.
- **Hold-up and wiring.** Add 470 µF low-ESR at the module, and a short twisted supply pair so that the 1.2 A step does not ring through cable inductance.

Switching option: a 12 V adapter and a 5 V buck lose 0.67 W instead of 8.4 W, but need the LC + damping filter of example 1. Check the RF output for $f_c \pm f_{sw}$ spurs. Either way, test that the TX power and spectrum do not change when the supply is swapped for a laboratory supply.

### 6. Cold-launch check for a 1S flight computer
Load: 6 W radio + 0.4 W logic through 0.88-efficient converters = 7.27 W at the cell during a burst. Assumed cell resistance (measure yours): 50 mΩ at 25 °C, 125 mΩ at 0 °C, 300 mΩ at −20 °C, plus 30 mΩ of wiring.

| Cell temperature | $V_{oc}$ 4.0 V (full) | $V_{oc}$ 3.7 V (mid) |
|---|---|---|
| 25 °C | 1.89 A, 3.85 V | 2.06 A, 3.54 V |
| 0 °C | 1.97 A, 3.69 V | 2.16 A, 3.37 V |
| −20 °C | 2.23 A, 3.26 V | **2.54 A, 2.86 V — below a 3.0 V brown-out** |

The input collapses entirely below $V_{oc} = \sqrt{4RP}$ = 3.10 V at −20 °C. An ngspice battery model with a 1 s polarisation RC (script §4) shows the cold terminal voltage falling from 3.49 V just after the step to 3.36 V after 1 s of transmission, on its way to the 3.26 V steady state. A long SF12 packet (1.8 s) sees nearly the full sag.

Runtime at the same assumptions: a 1000 mAh pack (3.7 Wh) with a 1.21 W average load (logic plus 10 % TX duty) lasts 2.45 h at 25 °C with 80 % usable. With an assumed 50 % usable at −20 °C, 1.5 h.

Design actions:
- keep the pack warm until launch, or use a 2S pack with a buck (half the current for the same power and the same absolute IR drop, so half the relative droop);
- set the UVLO and brown-out with hysteresis;
- verify on the bench with the pack cold-soaked in a freezer and the radio keyed for its longest packet.

## Practical notes
- **Place decoupling at the pins**, with the smallest capacitor closest and its own vias; the high-current loops of switchers (input capacitor – switch – diode/FET) must be as small as possible.
- **Measure ripple correctly:** scope probe with a ground spring (not the ground lead), 20 MHz bandwidth limit for ripple, full bandwidth for spikes; or a 50 Ω coax pigtail with a DC-block into the scope/spectrum analyser.
- **Supply noise in RF:** check the RF output on a spectrum analyser for spurs at $f_c \pm f_{sw}$ and harmonics; toggle the switcher (bench supply bypass) to confirm.
- **Batteries:** measure pack internal resistance with a pulsed load (ΔV/ΔI) at the temperatures you fly at; include connector and wiring. Keep the pyro supply separate from the logic/radio supply where possible (Avionics C allows a separate pyro battery).
- **Reference choice:** for 12-bit MCU ADCs a clean 3.3 V LDO or a shunt reference is enough; for 16-bit+ use a dedicated low-noise reference and buffer.

## Common mistakes & misconceptions
- **"The LDO will clean up the switcher."** Only at low frequency; at 1–2 MHz typical LDOs give 20–45 dB.
- **Using the datasheet PSRR at 1 kHz for a 2 MHz switcher.**
- **Running an LDO with 100 mV headroom** and expecting datasheet PSRR.
- **Undamped LC or bead filters** that peak at their resonance.
- **Assuming the ripple formula covers the spikes** — ESL/layout spikes at 50–300 MHz often dominate and couple into RF.
- **Sharing ground returns between PA/switcher currents and ADC/sensor references.**
- **Forgetting that a regulator's input current rises as its input voltage falls** (constant-power load) — battery droop feeds on itself.
- **Plugging a battery into a board with hundreds of µF and no inrush control** — sparks, overshoot and possible TVS/regulator damage.
- **Powering a GaN/GaAs PA drain before its gate bias.**
- **Designing a linear supply from the average rectified voltage.** The ripple trough at low mains must clear the dropout.
- **A transformer sized by DC watts.** Capacitor-input rectifiers draw peaky current; rate the transformer at ≈ 1.6–1.8 × the DC power and the diodes for the pulse current.
- **Expecting a Zener bypass capacitor to remove 100 Hz ripple.** It must be far below $r_z$ in reactance at 100 Hz (mF); it mainly cuts avalanche noise.
- **Sizing a battery in mAh for a load behind a converter** — use Wh, and include converter efficiency and the constant-power current rise at low voltage.
- **Using room-temperature internal resistance for a cold launch,** or charging Li-ion below 0 °C.
- **Running a 1 A radio from alkaline cells.** At 150–300 mΩ per cell the drop is 0.2–0.4 V per cell, worse in the cold.

## How to simulate / verify
- **Python:** `tools/verify/analog_power.py` — LDO noise density conversion; buck ripple with derated capacitors; ripple through an LDO PSRR table and LC filters; damping-leg optimisation; bead + cap resonance; spur levels from pushing and AM; 1S battery constant-power droop, ground-IR in LSBs, hold-up capacitance; ground bounce.
- **Rectifiers, regulators, batteries:** `tools/verify/s3_rectifier_battery.py` (+ `_output.txt`) — ngspice half-wave and bridge rectifiers vs the ripple formulas, linear bench-supply headroom and heatsink, Zener regulator ripple with and without bypass capacitors, Peukert, Ah→runtime, cold-launch constant-power droop (closed form and an ngspice battery model with polarisation RC).
- **ngspice** (via `tools/verify/analog_ngspice.py`): AC analysis of the LC/bead filter with the real load; add the LDO as a behavioural block with a PSRR(f) transfer; transient of a buck with a PWL load step for spikes (vendor switcher models when available). Example filter check:
```spice
* LC post-filter with damping leg; V1 = 1 V AC ripple source
V1 in 0 AC 1
L1 in a 1u
RL1 a out 0.05
C1 out 0 10u
Rd out d 0.316
Cd d 0 40u
Rload out 0 11
.ac dec 100 1k 10MEG
.end
```
  (ngspice: peak +1.1 dB, moved down to ≈ 26 kHz by the extra 40 µF; −63.9 dB at 2 MHz — matching the Python model, script §8.)
- **Bench:** inject a sine onto the input rail (through a coupling capacitor or a line-injection transformer) and measure the output with a spectrum analyser to get PSRR; scope + current probe on the battery lead while the radio transmits.

## Open questions / gaps
- Cold-temperature internal-resistance multipliers (×2.5 at 0 °C, ×6 at −20 °C) and usable-capacity fractions in example 6 are assumptions bracketed by [9][10] (example 6); measure the team's packs cold (pulsed ΔV/ΔI after 10 ms and 1 s).
- The 100 mΩ internal resistance for a small 1S LiPo and 30 mΩ wiring are representative assumptions; the team's actual packs should be measured (pulsed ΔV/ΔI, at cold temperature).
- The E220-900T30D (1 W) transmit current was not found in the sources retrieved; only the E22-400T33D's 850–1200 mA [3].
- A specific LDO with MHz-range PSRR (e.g. ultra-high-PSRR parts) was not sourced here; see 18 components.
- Middlebrook's optimal-damping closed forms are cited, not re-derived; the damping result here is numerical.

## Sources
1. Texas Instruments, *TPS7A20 300 mA ultra-low-noise, low-IQ, high-PSRR LDO* datasheet SBVS338H. https://www.ti.com/lit/ds/symlink/tps7a20.pdf — PSRR vs frequency at 20 and 300 mA, 7 µV rms (10 Hz–100 kHz), dropout, ≥ 1 µF MLCC stability. (datasheet)
2. Advanced Monolithic Systems, *AMS1117 1 A low-dropout voltage regulator* datasheet. http://www.advanced-monolithic.com/pdf/ds1117.pdf — RMS output noise 0.003 % of V_out (10 Hz–10 kHz), ripple rejection 60–75 dB at 120 Hz, dropout ≈ 1.1–1.3 V at 1 A (via datasheet search summary). (datasheet)
3. Chengdu Ebyte, *E22-400T33X User Manual* v1.5. https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2024/07/E22-400T33X_UserManual_EN_v1.5-1.pdf — supply 3.3–5.5 V (≥ 5 V guarantees output power), emission current 850–1200 mA, receive 11–15 mA, sleep 2 µA; recommendations on ripple, grounding and 30 % margin. (datasheet/manual)
4. R. D. Middlebrook, "Design techniques for preventing input-filter oscillations in switched-mode regulators," *Proc. Powercon 5*, 1978; and R. W. Erickson, D. Maksimović, *Fundamentals of Power Electronics*, 2nd ed., Springer 2001, ch. 10 (input filter design, damping networks). (peer-reviewed / textbook)
5. P. Horowitz, W. Hill, *The Art of Electronics*, 3rd ed., Cambridge 2015 — ch. 9 (voltage regulators, references, LDO noise, switcher ripple). (textbook)
6. Space Bar avionics knowledge base (team-internal): Avionics C power architecture (1S, separate 5 V buck-boost for the radio), Avionics B 2S (7.0–8.4 V) input, and the magnetometer-offset lesson (shared, unfiltered regulator). (internal record)
7. T. B. Reddy (ed.), *Linden's Handbook of Batteries*, 4th ed., McGraw-Hill 2011 — chemistry voltages, specific energy, rate (Peukert) and temperature behaviour of alkaline, NiMH, lead-acid, Li-ion and LiFePO₄ cells. (textbook; ranges, not re-read page by page)
8. Energizer, *E91 AA alkaline product datasheet* (2018). https://data.energizer.com/pdfs/e91.pdf — nominal 1.5 V, internal resistance 150–300 mΩ fresh, operating −18 to 55 °C, capacity vs drain (chart only). (datasheet)
9. S. S. Zhang, K. Xu, T. R. Jow, "Electrochemical impedance study on the low temperature of Li-ion batteries," *Electrochimica Acta* 49, 1057–1061 (2004) — charge-transfer resistance dominates below −20 °C. (peer-reviewed; abstract-level)
10. US DOE national-laboratory study of NCA/NMC cells over −20 to 40 °C (OSTI 1962091, "The influence of temperature on area-specific impedance…") — cells reach only ≈ 50 % depth at −20 °C at the test rate. (lab report; via search summary, not read in full)
11. A. S. Sedra, K. C. Smith, *Microelectronic Circuits*, 7th ed., Oxford 2015 — ch. 4 (rectifier circuits, ripple and conduction angle, Zener shunt regulators). (textbook)
