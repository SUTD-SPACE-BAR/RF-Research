---
title: Analog signal conditioning — instrumentation amplifiers, bridges, level shifting, ADC front ends, input protection, sensor-line filtering, current sensing, isolation
domain: 05-analog-electronics
slug: analog-signal-conditioning
tags: [signal-conditioning, instrumentation-amplifier, difference-amplifier, cmrr, wheatstone-bridge, strain-gauge, ratiometric, level-shifting, adc-front-end, voltage-divider, input-protection, clamp-diode, back-powering, tvs, esd, rfi-filter, current-sense, shunt, pyro-continuity, isolation]
prerequisites:
  - op-amps-real-limitations.md
  - data-converters-adc-dac.md
  - diodes-schottky-pin-varactor.md
related:
  - low-noise-analog-design.md
  - active-filters.md
  - power-supplies-for-rf-and-analog.md
  - fets-mosfet-jfet-gaas-gan.md
  - ../13-pcb-rf-layout-emc/emc-emi-fundamentals.md
  - ../13-pcb-rf-layout-emc/mixed-signal-layout.md
  - ../13-pcb-rf-layout-emc/grounding-and-return-paths.md
  - ../19-regulations-safety/lab-safety-esd-high-power.md
level: mixed
confidence: high
last_updated: 2026-10-12
---

# Analog signal conditioning — instrumentation amplifiers, bridges, level shifting, ADC front ends, input protection, sensor-line filtering, current sensing, isolation

## Questions this page answers
- When do I need an instrumentation amplifier instead of an op-amp difference amplifier?
- How much CMRR do I get from 1 % or 0.1 % resistors?
- How much voltage does a strain-gauge or pressure bridge give, and why measure ratiometrically?
- How do I scale and shift a ±2.5 V (or 0–8.4 V battery) signal into a 3.3 V ADC?
- Why does my voltage divider read wrong on the MCU's ADC, and what capacitor fixes it?
- How do I protect an analog input from ESD, reverse voltage and over-voltage — and how can the protection diodes *back-power* my board?
- How should I pick a TVS for a battery or pyro rail?
- How do I filter RF out of long sensor wires without ruining the INA's CMRR?
- How do I measure pyro-channel current and igniter continuity reliably?
- When is galvanic isolation needed?
- How do I read a 4–20 mA sensor with a 3.3 V ADC, and how long can the cable be?
- Why does a remote sensor read wrong when the pyro or servo current flows, and how do differential lines fix it?
- What is the difference between a comparator and an op-amp, and when do I need hysteresis?
- How do I calculate Schmitt-trigger thresholds for a battery-low detector?
- How does a 555 timer set its frequency?

## TL;DR
- **Difference amplifier CMRR from resistor mismatch:** worst case $CMRR ≈ (1+G)/(4\varepsilon)$ for tolerance ε: 1 % → 34 dB at G = 1, 0.1 % → 54 dB (Monte Carlo agrees, median ≈ 14 dB better) (`tools/verify/analog_signal_conditioning.py` §1). **Instrumentation amplifiers** (laser-trimmed, gain set by one resistor) reach ≥ 100 dB: INA333 $G = 1 + 100\,\text{kΩ}/R_G$, CMRR ≥ 100 dB for G ≥ 10, offset ≤ 25 µV + 75 µV/G, 50 nV/√Hz, zero-drift, 50 µA [1].
- **Bridges:** full push-pull bridge $V_{out} = V_{ex}\,\Delta R/R$ (linear); quarter bridge $V_{ex}\,x/(4+2x)$ (0.1 % nonlinearity at x = 0.002, 1 % at 0.02) (§3). A strain gauge (GF ≈ 2) at 1000 µε in a full bridge gives 2 mV/V = 6.6 mV at 3.3 V. Excite the bridge from the ADC's reference (ratiometric) so reference drift cancels.
- **Level shifting:** a passive two/three-resistor network can implement $V_{out} = aV_{in} + b$ only if $a + b/V_{ref} \le 1$; mapping ±2.5 V onto 0.15–3.15 V ($a$ = 0.6, $b$ = 1.65) needs an op-amp; equal resistors give $(V_{in}+3.3)/2$ → 0.40–2.90 V passively (§7).
- **Dividers into SAR ADCs:** 100 k/33 k (for a 2S pack) has 24.8 kΩ Thevenin resistance; the ADC's ~5 pF sampling capacitor needs 1.1 µs to settle to 12 bits — longer than a typical 1 µs acquisition → add ~100 nF at the pin (50 ppm kickback, 64 Hz corner) (§5). The divider also drains 63 µA ≈ 0.55 Ah/year in storage.
- **Protection:** series R + clamp diodes to the rails limit fault current to $(V_{fault} - V_{rail} - V_f)/R$ — 24 V through 10 kΩ → 2 mA *into the 3.3 V rail*. If the rail's load is smaller than that (board off, MCU asleep), the rail rises: **back-powering** (the same class of problem as the team's pyro-bus backfeed and GPS back-powering lessons). Use Schottky clamps to a load-capable rail, a Zener/TVS to ground, or series FET/limiter parts.
- **TVS choice:** working (stand-off) voltage ≥ the maximum *normal* voltage (full-charge pack plus charger overshoot), clamping voltage below what downstream survives, and capacitance acceptable for the signal (500 pF with a 10 kΩ source = 32 kHz pole) (§6). Under-rated TVS parts conduct in normal operation.
- **RFI filters for INAs:** series R in each leg, $C_{cm}$ from each leg to ground, $C_{diff} \ge 10\,C_{cm}$ across: $f_{DM} = 1/[2\pi R(2C_d + C_c)]$, $f_{CM} = 1/(2\pi RC_c)$. The large $C_d$ swamps $C_c$ mismatch: with ±5 % $C_c$ mismatch, CM→DM conversion at 1 MHz improves from −36 dB to −63 dB (§4) [2].
- **Current sensing:** 10 mΩ shunt + gain-50 current-sense amplifier: 3 A → 30 mV → 1.5 V; a 150 µV offset (INA180 class [3]) is 15 mA of error. **Igniter continuity:** 10 mA through 1.5 Ω is only 15 mV — design for mV resolution with a known, safe test current well below the igniter's no-fire rating (§8).

- **4–20 mA:** 150 Ω shunt → 0.60–3.00 V (NE 43 faults ≤ 3.6 / ≥ 21 mA → 0.54 / 3.15 V); compliance $V_{loop} \ge V_{tx,min} + I_{max}\sum R$ — 24 V, 10 V transmitter → 636 Ω total at 22 mA; beyond it the current silently drops (ngspice, `tools/verify/s3_lines_comparators.py`). **Long voltage lines:** a 1 V ground offset is a 1 V single-ended error, 19.8 mV through a 1 % difference amp, 10 µV through an INA.
- **Comparators/Schmitt/555:** hysteresis $\Delta V_H = V_{cc}R_1/R_2$ cures chatter (27 → 1 transitions in simulation); 1S undervoltage flag 3.31/3.51 V from 100 k/53.6 k/1.65 M; 555 $f = 1.443/((R_A+2R_B)C)$, verified by a behavioural ngspice model to 0.01 %.

## Intuition (no math)
Sensors rarely deliver what an ADC wants. A bridge gives millivolts riding on half the supply; a battery is several volts above the ADC's range; a thermocouple gives microvolts per degree on a long wire full of pickup; a pyro channel carries amps. Signal conditioning is the translation layer: **amplify** the small differential part, **reject** the common-mode part and the interference, **shift and scale** into the ADC's window, **filter** out what the ADC would alias, and **protect** everything from the outside world — without adding errors bigger than the signal.

The key idea for small signals is *differential* measurement: the signal is the difference between two wires; noise and ground shifts appear equally on both and cancel in a good differential amplifier. How well they cancel (CMRR) depends on matching: in a four-resistor difference amplifier, a 0.1 % mismatch lets 1 part in ~500 of the common-mode voltage through. Instrumentation amplifiers are difference amplifiers whose critical resistors are trimmed on-chip, with buffered high-impedance inputs.

The key idea for accuracy is *ratiometric* measurement: if the bridge is powered from the same reference the ADC uses, a 1 % reference drift changes both the signal and the ADC's scale by 1 %, and the digital reading does not move.

Protection is about where fault current goes. A diode clamp doesn't destroy energy — it steers current into a rail. If nothing on that rail consumes it, the rail voltage rises and parts that should be off are partially powered.

## The math

### Level 1 — the building blocks

**Four-resistor difference amplifier** ($R_1$ from $v_1$ to the inverting input, $R_2$ feedback; $R_3$/$R_4$ divider on the non-inverting input): with $R_2/R_1 = R_4/R_3 = G$, $V_{out} = G(v_2 - v_1)$. With mismatch,
$$A_{cm} = \frac{R_4}{R_3+R_4}\left(1+\frac{R_2}{R_1}\right) - \frac{R_2}{R_1},\qquad CMRR_{worst} \approx \frac{1+G}{4\varepsilon}.$$

**Three-op-amp instrumentation amplifier:** two non-inverting input buffers with gain $1 + 2R_F/R_G$ drive a unity-gain difference stage; the common-mode voltage passes the input stage at unity gain, the differential signal at gain G, so CMRR improves with gain. INA333: $G = 1 + 100\,\text{kΩ}/R_G$ [1].

**Wheatstone bridge** (excitation $V_{ex}$, arms R, fractional change x = ΔR/R):

| Configuration | $V_{out}$ exact | Linear approx. |
|---|---|---|
| Quarter (one active arm) | $V_{ex}\,x/(4+2x)$ | $V_{ex}x/4$ |
| Half, opposite arms same sign | $V_{ex}\,x/(2+x)$ | $V_{ex}x/2$ |
| Half, adjacent arms push-pull (±x) | $V_{ex}x/2$ | exact |
| Full, push-pull (±x) | $V_{ex}x$ | exact |

Strain: $x = GF\cdot\varepsilon$ (GF ≈ 2 for metal-foil gauges).

**Linear scaling** $V_{out} = aV_{in} + b$ with a passive network from $V_{in}$ and $V_{ref}$: $a = R_p/R_1$, $b = V_{ref}R_p/R_2$, $R_p = R_1\|R_2\|R_3$ → requires $a + b/V_{ref} \le 1$.

**Clamp current:** $I = (V_{fault} - V_{rail} - V_f)/R_s$; power in $R_s$: $I^2R_s$.

**INA RFI filter corners:** $f_{DM} = \dfrac{1}{2\pi R(2C_d + C_c)}$, $f_{CM} = \dfrac{1}{2\pi RC_c}$, with $C_d \ge 10C_c$ [2].

### Level 2 — derivations and error budgets

**CMRR of the difference amplifier (derivation).** Apply the same voltage $v_{cm}$ to both inputs: $V_{out} = v_{cm}\left[\frac{R_4}{R_3+R_4}(1+\frac{R_2}{R_1}) - \frac{R_2}{R_1}\right]$. With nominal $R_2 = GR_1$, $R_4 = GR_3$ this vanishes. Perturb each resistor by ±ε in the worst direction ($R_1, R_4$ up; $R_2, R_3$ down or vice versa): to first order $A_{cm} ≈ 4\varepsilon G/(1+G)$, while $A_{dm} = G$, giving $CMRR ≈ (1+G)/(4\varepsilon)$. Monte Carlo with uniform tolerances (§1): the minimum over 50 000 builds sits at the formula (34.6 vs 34.0 dB at 1 %, G = 1), the median ≈ 14 dB better. A source resistance in series with one input acts as a mismatch too: 100 Ω of unbalanced source impedance on a 10 kΩ difference amplifier is a 1 % error — another reason to use buffered INAs with high-impedance sources.

**Why instrumentation amplifiers.** The input buffers make the input impedance GΩ (so source imbalance doesn't unbalance the resistors), the precision matching is done on-chip (laser trim), and the input stage's differential gain G raises CMRR by G before the difference stage sees it. Watch the **input common-mode range vs output swing** limitation of 3-op-amp INAs ("diamond plot"): the internal nodes carry $V_{cm} ± G_1v_d/2$ and can saturate even when both input pins and the output are in range — critical on single 3.3 V supplies. INA333 inputs work from $V_- + 0.1$ V to $V_+ - 0.1$ V with $V_{REF}$ typically mid-supply [1].

**Bridge sensitivity and error budget.** A 350 Ω full-bridge load cell at 2 mV/V excited at 3.3 V gives 6.6 mV full scale. With an INA333 at G = 100 ($R_G$ = 1.01 kΩ): 660 mV full scale; offset ≤ 25.75 µV RTI (0.4 % of full scale; calibrate at zero load) and drift 0.1 µV/°C; noise 1 µV p-p 0.1–10 Hz (0.015 %). The dominant errors become the bridge's own temperature coefficient, lead resistance (use 6-wire sense for long leads), self-heating (3.3 V across 350 Ω dissipates 31 mW in the bridge) and thermal EMFs. Ratiometric operation: $V_{out} = V_{ex}x$ and the ADC reads $V_{out}/V_{ref}$; tie $V_{ex}$ to $V_{ref}$ and the reading $= x\,V_{ex}/V_{ref}$ is independent of the rail.

**Dividers into sampling ADCs.** A SAR ADC's input is a switch and a sampling capacitor $C_s$ (a few pF in MCUs). With source resistance $R_{th}$ the voltage settles as $e^{-t/R_{th}C_s}$; N-bit settling needs $(N+1)\ln2$ time constants (9 τ for 12 bits). 100 kΩ/33 kΩ → $R_{th}$ = 24.8 kΩ, τ = 124 ns with 5 pF → 1.12 µs, longer than a 1 µs acquisition (§5) — the classic "divider reads low/noisy" symptom. Fix: a capacitor at the ADC pin ≫ $C_s$ (100 nF → 50 ppm kickback = 0.2 LSB at 12 bits), accepting a 64 Hz corner (fine for battery voltage), or a buffer op-amp. (→ [data converters](data-converters-adc-dac.md) for the charge-bucket derivation.)

**Level shifting (derivation).** Node equation for a node fed by $V_{in}$ through $R_1$, $V_{ref}$ through $R_2$, ground through $R_3$: $V_{out}(1/R_1+1/R_2+1/R_3) = V_{in}/R_1 + V_{ref}/R_2$ → $a = R_p/R_1$, $b = V_{ref}R_p/R_2$ with $R_p \le R_1\|R_2$, hence $a + b/V_{ref} = R_p(1/R_1 + 1/R_2) \le 1$. For ±2.5 V → 0.15–3.15 V ($a$ = 0.6, $b$ = 1.65 V, $V_{ref}$ = 3.3 V): 0.6 + 0.5 = 1.1 → impossible passively (§7). Options: accept $a$ = 0.5 with equal resistors ($V_{out} = (V_{in}+3.3)/2$, 0.40–2.90 V, 76 % of the range, buffer the R/2 source impedance), or use an op-amp (inverting summer, or a difference amplifier referenced to 1.65 V). For negative inputs make sure no ADC pin ever goes below ground by more than its absolute-maximum rating during power-up.

**Clamp-diode back-powering (derivation of the risk).** A diode from the input to $V_{DD}$ conducts when $V_{in} > V_{DD} + V_f$; the current $I = (V_{in} - V_{DD} - V_f)/R_s$ flows *into* the $V_{DD}$ net. The rail is held only if its regulator can sink current (most LDOs and bucks cannot) or its load draws more than I. 24 V through 10 kΩ gives 2.0 mA (§6) — more than a sleeping MCU draws — so $V_{DD}$ climbs until something conducts. The same mechanism powers a GPS or sensor through its I/O pins when its supply is off (the team's buffered-UART fix for the GNSS module addresses exactly this) and puts "a few volts" on a nominally dead pyro rail through protection or ORing paths. Mitigations: (i) clamp to a rail that is always loaded or add a bleed/shunt (Zener) that can absorb the current; (ii) clamp to ground with a TVS/Zener rated below the ADC's absolute maximum; (iii) series FET or dedicated over-voltage-protected analog switches/buffers; (iv) ensure unpowered interfaces are high-impedance (buffers with "power-off protection" / $I_{off}$ spec).

**TVS selection.** A TVS conducts little below its reverse stand-off (working) voltage $V_{RWM}$, breaks down at $V_{BR}$ (≈ 1.1–1.2 × $V_{RWM}$), and clamps at $V_C$ (≈ 1.4–1.7 × $V_{RWM}$) at its rated pulse current. Rules: $V_{RWM}$ ≥ the highest *normal* voltage (a 2S pack is 8.4 V fully charged, plus any charger or regenerative overshoot); $V_C$ at the expected surge current below the downstream absolute maximum; pulse power rating for the threat (ESD vs inductive load dump vs hot-plug). A TVS with $V_{RWM}$ below the pack's full-charge voltage leaks or conducts continuously (heating, drain, eventual failure) — the "under-rated TVS on the pyro bus" lesson. On signal lines, TVS capacitance forms a low-pass with the source resistance (500 pF with 10 kΩ → 32 kHz; §6) and on RF lines it must be ≤ 0.3 pF (→ [diodes](diodes-schottky-pin-varactor.md) example 4).

**RFI filtering of differential inputs.** Long sensor leads are antennas; a nearby 2 W LoRa transmitter drives tens to hundreds of mV of RF common-mode onto them, which the INA's input transistors rectify into DC offsets (→ [op-amps](op-amps-real-limitations.md), EMI rectification). A filter with only $C_{cm}$ per leg converts common-mode to differential mode through capacitor mismatch; adding $C_d \ge 10C_{cm}$ across the inputs shorts that differential error. Numbers (§4; R = 1 kΩ, $C_c$ = 1 nF, $C_d$ = 10 nF): $f_{DM}$ = 7.6 kHz, $f_{CM}$ = 159 kHz; with ±5 % $C_c$ mismatch the CM→DM conversion at 1 MHz is −63 dB with $C_d$ vs −36 dB without, and at 433 MHz −115 vs −89 dB. Use C0G capacitors, keep the filter at the connector, and add a ferrite or common-mode choke for UHF.

**Current sensing.** Low-side shunts are simple (common mode ≈ 0 V) but lift the load's ground; high-side sensing keeps ground intact and detects shorts to ground, and needs a current-sense amplifier (CSA) whose common-mode range covers the rail (INA180: −0.2 to +26 V, gains 20/50/100/200, ±150 µV offset at 0 V, 350 kHz [3]). Trade: bigger shunt → better resolution, more dissipation and burden voltage. 3 A through 10 mΩ = 30 mV, 90 mW; ±150 µV offset ≡ ±15 mA (§8). Use a 4-terminal (Kelvin) shunt footprint; the sense traces must not carry load current.

**Igniter continuity measurement.** An e-match/igniter is ~0.5–2 Ω; a safe test current must be far below the igniter's specified no-fire current (check the product's data; typical design practice keeps it at least an order of magnitude below). With 10 mA the voltage is 5–15 mV; with 1 mA only 0.5–1.5 mV (§8). A reliable design therefore needs: a defined test current source (not a resistor from an uncertain rail), a differential measurement across the igniter terminals (not referenced to a ground shared with pyro return currents), gain and an offset well below the signal (zero-drift amplifier or INA), and a result that distinguishes three states — short, igniter-present, open — with margin. The team's earlier continuity sensing gave "effectively random" results; treat it as a precision low-resistance measurement problem, and do not let arming logic depend on it until it is characterised.

**Isolation.** Needed when grounds can differ by more than the input's common-mode range (ground-station equipment on mains, long cable runs, high-voltage batteries) or for safety. Options: digital isolators + isolated DC-DC with an ADC on the far side (usually best), isolation amplifiers, optocouplers (slow, CTR drift), transformer coupling for AC signals. Isolation breaks ground loops but adds a capacitive path (a few pF) for high-frequency common mode.

### Level 3 — details that bite
- **INA gain resistor tempco** directly scales the gain error: a 100 ppm/°C thick-film $R_G$ gives 0.5 % over 50 °C; use 25 ppm/°C thin film or better.
- **Reference pin impedance** of an INA or difference amplifier must be low: a resistor divider driving REF unbalances the internal difference stage and destroys CMRR; buffer it.
- **Bias-current return path:** INA inputs need a DC path to ground (floating thermocouples, AC-coupled inputs) or they drift to a rail.
- **Thermal EMFs:** copper–solder–tin junctions produce µV/K; keep input pairs symmetric and at equal temperature.
- **Multiplexed inputs:** switching between channels leaves charge on the sampling capacitor; high-impedance sources need buffers or longer acquisition times.
- **ESD standards:** IEC 61000-4-2 (contact ±8 kV, air ±15 kV at level 4) is the usual system-level target for connectors; component HBM ratings (1–2 kV) are not equivalent (→ [lab safety/ESD](../19-regulations-safety/lab-safety-esd-high-power.md)).

### Current loops (4-20 mA) and long differential sensor lines
Numbers below are from `tools/verify/s3_lines_comparators.py` §1–2 (ngspice; output in `_output.txt`).

**Why send a current?** In a series loop the current is the same everywhere, so wire resistance, connector resistance and moderate ground shifts do not change the reading, as long as the loop has enough voltage left over ("compliance"). The low receiver impedance (≈ 100–250 Ω) also makes the loop insensitive to capacitively coupled noise. The *live zero* (4 mA = 0 %) lets a 2-wire transmitter power itself from the loop and lets the receiver tell "0 %" from "broken wire" (0 mA). NAMUR NE 43 sets the measurement range at 3.8–20.5 mA and fault signals at ≤ 3.6 mA or ≥ 21 mA [8] (vendors differ: check the transmitter's configured alarm currents).

**Receiver for a 3.3 V ADC.** A 150 Ω shunt maps 4–20 mA to 0.60–3.00 V. NE 43 fault-low (3.6 mA) gives 0.54 V and fault-high (21 mA) gives 3.15 V, both still inside the ADC range, so firmware can flag them. A 12-bit LSB is 5.4 µA, or 0.034 % of span. The shunt's tempco is a gain error: 25 ppm/K over 50 K is 0.125 %, so use a 0.1 %, ≤ 25 ppm/K part. Put a series resistor and a TVS at the connector, and add an RC (e.g. 1 kΩ + 100 nF, 1.6 kHz) before the ADC pin. Most sensors are slow; filter at the source of the RF pickup.

**Compliance budget.** $V_{loop} \ge V_{tx,min} + I_{max}(R_{sh} + R_{prot} + R_{wire})$. Example: 24 V loop, a transmitter that needs ≥ 10 V (a typical 2-wire figure; read its datasheet), 2 × 200 m of 0.5 mm² copper (13.8 Ω), 50 Ω protection, 150 Ω shunt. At 22 mA the loop can afford 636 Ω, so 423 Ω are spare. ngspice confirms that the current holds at 20.000 mA with 400 Ω of extra resistance (12 V left at the transmitter). With 600 Ω extra it collapses to 17.6 mA: the reading is wrong *without any fault indication*. Verify the full-scale current at the longest cable.

**Long voltage-output sensor lines.** A remote sensor and the flight computer often sit at grounds that differ by tens of mV to volts while pyro, servo or radio current flows in the shared return. A single-ended ADC reading includes the *whole* ground difference. With a 1 V offset:
- single-ended: 1 V error;
- four-resistor difference amplifier, worst-case 1 % resistors: 19.8 mV (ngspice; 34 dB, matching $(1+G)/4\varepsilon$);
- INA with 100 dB CMRR: 10 µV.

Hence the rules. Send the signal *and its own reference conductor* in a twisted pair, measure the difference at the receiver with an INA or a differential ADC, and make sure the common-mode range covers the worst ground shift. Return the cable shield at the entry point, not through the signal reference. For long, noisy runs prefer a current loop or a digital link (RS-485, CAN). If the lines are long compared with the edge rates, or they pass near the transmitter antenna, add the RFI filter of Level 2 (series R, $C_{cm}$, $C_d \ge 10C_{cm}$) at the connector. RF that reaches the INA is rectified into DC offsets (→ [EMC — rectification](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md#level-3--susceptibility-rectification-pyro-circuits-esd)).

### Comparators, Schmitt triggers and timers
Numbers are from `tools/verify/s3_lines_comparators.py` §3–4 (ngspice).

**Comparator vs op-amp.** A comparator is an open-loop amplifier built to *saturate cleanly*. It has a fast output that swings to logic levels, recovers quickly from overdrive and tolerates large differential inputs. An op-amp used as a comparator works at low speed, but it recovers slowly from saturation (µs), may have input clamp diodes that draw current when the inputs differ by more than ~0.7 V, and can show phase reversal outside its common-mode range (→ [op-amps](op-amps-real-limitations.md)). Propagation delay is specified at a stated *overdrive* (input beyond the threshold, typically 5–100 mV) and grows sharply at small overdrive. Outputs are **push-pull** (drives both ways; the logic level is set by the comparator's supply) or **open-drain/collector**. Open-drain needs a pull-up $R_p$, gives a 10–90 % rise of $2.2R_pC_L$ (10 kΩ into 20 pF: 440 ns), permits wired-OR and level translation to another rail.

**Hysteresis (Schmitt trigger).** Near the threshold, noise makes a plain comparator toggle many times ("chatter"). In the simulation a slow 3.3 → 3.6 V ramp with 20 mV p-p of noise gave **27 transitions without hysteresis and 1 with it**. Positive feedback from the output to the + input moves the threshold away from the input once the output has switched. Non-inverting form, with the input through $R_1$ to the + node, feedback $R_2$ from the output (swinging 0 … $V_{cc}$) and the − input at $V_{ref}$:
$$V_{T+} = V_{ref}\left(1+\frac{R_1}{R_2}\right),\qquad V_{T-} = V_{ref}\left(1+\frac{R_1}{R_2}\right) - V_{cc}\frac{R_1}{R_2},\qquad \Delta V_H = V_{cc}\frac{R_1}{R_2}.$$
With an extra resistor $R_b$ from the + node to ground (a divider for a high input voltage), $V_{T+} = R_1V_{ref}(1/R_1 + 1/R_b + 1/R_2)$ and $V_{T-} = V_{T+} - R_1V_{cc}/R_2$. Rules:
- Make $\Delta V_H$ larger than the noise peak-to-peak at the comparator input. A few × the rms is not enough, because peaks reach ±3σ.
- Source impedance adds to $R_1$ and moves the thresholds.
- With an open-drain output, $R_p$ forms a divider with $R_2$; keep $R_2 \ge 100R_p$ [9].
- The inverting form (input to the − pin, reference and feedback on the + pin) gives inverted logic, with thresholds set by the same divider algebra.

**Worked example — 1S LiPo undervoltage flag (trip at 3.3 V falling, release at 3.5 V rising).** Use a 1.200 V reference and a push-pull comparator on 3.3 V. With $R_1$ = 100 kΩ, $\Delta V_H$ = 0.2 V needs $R_2 = R_1V_{cc}/\Delta V_H$ = 1.65 MΩ, and $V_{T+}$ = 3.5 V needs $R_b$ = 53.9 kΩ (E96: 53.6 kΩ). The E96 values give a rising threshold of 3.512 V and a falling one of 3.312 V; the ngspice sweep gives 3.507 / 3.316 V. The divider draws ≈ 23 µA from the cell, about 0.2 Ah/year; switch it off in storage, as for the ADC divider above. Put ~100 nF on the + node only if the delay it adds is acceptable. Without the hysteresis, the 0.1–0.3 V of droop during each LoRa burst (→ [power supplies](power-supplies-for-rf-and-analog.md)) would make the flag toggle at the packet rate. Decide in firmware whether "low" must persist for N samples.

**Window comparator.** Two comparators (or a dual with open-drain outputs wired together) flag "outside $V_L$…$V_H$". Typical uses are rail supervision, igniter-continuity classification (short / present / open) and detector-based carrier sensing with a squelch threshold.

**555 timer.** Two comparators at $V_{cc}/3$ and $2V_{cc}/3$, an SR latch and a discharge transistor. In the astable, C charges through $R_A + R_B$ from $V_{cc}/3$ to $2V_{cc}/3$ (time $\ln2\,(R_A+R_B)C$) and discharges through $R_B$ (time $\ln2\,R_BC$):
$$f = \frac{1}{\ln2\,(R_A+2R_B)C} = \frac{1.443}{(R_A+2R_B)C},\qquad D = \frac{R_A+R_B}{R_A+2R_B} > 50\ \%.$$
For $R_A$ = 10 kΩ, $R_B$ = 47 kΩ, C = 10 nF this gives 1387 Hz and 54.8 % duty. A behavioural ngspice 555 (a hysteretic switch at 1/3 and 2/3 of $V_{cc}$) gives 1387.3 Hz and 54.8 % [10]. The monostable pulse is $RC\ln3 = 1.1RC$. Because the thresholds are ratios of $V_{cc}$, the frequency does not depend on the supply, to first order. The bipolar NE555 draws several mA and puts large current spikes on the rail at each transition; use a CMOS version (TLC555/ICM7555 class, ≈ 100 µA) on battery boards, and decouple the pin. For anything precise or programmable, an MCU timer or a dedicated oscillator IC is usually the better choice; the 555 survives as a self-contained watchdog, buzzer or LED-flasher block.

## Design equations & rules of thumb

| Quantity | Equation | Typical |
|---|---|---|
| Difference-amp CMRR | $(1+G)/(4\varepsilon)$ worst case | 54 dB (G = 1, 0.1 %) |
| INA333 gain | $1 + 100\,\text{kΩ}/R_G$ | $R_G$ = 1.01 kΩ for G = 100 |
| INA offset RTI | $V_{OSI} + V_{OSO}/G$ | ≤ 25 + 75/G µV (INA333) |
| Full bridge | $V_{ex}\,\Delta R/R$ | 2 mV/V for 1000 µε |
| Quarter bridge | $V_{ex}x/(4+2x)$ | nonlinearity ≈ x/2 |
| Passive level-shift feasibility | $a + b/V_{ref} \le 1$ | otherwise use op-amp |
| SAR settling from $R_{th}$ | $(N+1)\ln2\cdot R_{th}C_s$ | add C ≫ $C_s$ |
| Clamp current | $(V_{fault}-V_{rail}-V_f)/R_s$ | keep ≤ datasheet (often 1–10 mA) |
| TVS | $V_{RWM}$ ≥ max normal V; $V_C$ < downstream abs max | — |
| RFI filter | $C_d \ge 10C_c$; $f_{DM}$, $f_{CM}$ above | C0G, at the connector |
| Shunt resolution | offset / $R_{shunt}$ | 15 mA for 150 µV/10 mΩ |
| Continuity signal | $I_{test}R_{igniter}$ | 5–15 mV at 10 mA |
| 4–20 mA shunt | $R_{sh} = V_{FS}/20$ mA | 150 Ω → 0.6–3.0 V |
| Loop compliance | $V_{loop} \ge V_{tx,min} + I_{max}(R_{sh}+R_{prot}+R_{wire})$ | 636 Ω at 24 V, 10 V, 22 mA |
| NAMUR NE 43 | valid 3.8–20.5 mA; fault ≤ 3.6 or ≥ 21 mA | [8] |
| Schmitt hysteresis | $\Delta V_H = V_{cc}R_1/R_2$; $V_{T+} = V_{ref}(1+R_1/R_2)$ | > noise p-p |
| Open-drain rise | $2.2R_pC_L$ (10–90 %) | 440 ns for 10 k/20 pF |
| 555 astable | $f = 1.443/((R_A+2R_B)C)$, $D = (R_A+R_B)/(R_A+2R_B)$ | monostable 1.1RC |

## Worked examples

### 1. Load-cell (thrust stand) front end on 3.3 V
350 Ω full bridge, 2 mV/V, excited from the ADC reference (3.3 V, ratiometric). INA333 at G = 100 → 0–660 mV (bias the output with REF at 0.3 V or so to stay off the bottom rail: output swings to 50 mV from rails [1]). RFI filter: 1 kΩ + 1 nF per leg + 10 nF across (7.6 kHz differential corner; fine for a thrust curve sampled at 1 kHz, with an anti-alias filter/decimation after). Errors: offset calibrates out; gain set by a 25 ppm/°C thin-film $R_G$; 31 mW bridge self-heating → allow warm-up.

### 2. 2S battery-voltage monitor on the flight computer
8.4 V max → 100 kΩ/33 kΩ → 2.08 V at the ADC; 100 nF at the pin (settles the sampling kickback; 64 Hz corner) (§5). Add a series 1–10 kΩ between the node and the pin if the ADC pin's clamp current must be limited during reverse-polarity or hot-plug events; consider switching the divider off with a small FET if storage drain (0.55 Ah/yr) matters.

### 3. Pyro current sense and continuity
High-side: 10 mΩ Kelvin shunt, INA180A2 (G = 50) → 1.5 V at 3 A; offset ≡ ±15 mA (§8) — fine for "did current flow" and for estimating igniter current. Continuity (separate path): a current-limited source of a few mA (well below no-fire) switched onto the channel only in a test state, with a differential measurement across the channel terminals through an INA at gain ~100 → 0.5–1.5 V for 0.5–1.5 Ω at 10 mA; "open" reads the source's compliance voltage; "short" reads ≈ 0. Verify on the bench with 0 Ω, 0.5 Ω, 2 Ω and open loads before trusting it in arming logic.

### 4. Protecting an external analog input
Connector → 1 kΩ (0.25 W, pulse-rated) → node with a TVS to ground ($V_{RWM}$ = 3.3–5 V, low capacitance) and a Schottky pair (BAT54S) to 3.3 V/ground → 100 Ω → ADC pin, 10 nF at the pin. A 24 V fault: 20 mA into the clamps through 1 kΩ (0.42 W in the resistor, §6) — so either use 10 kΩ (2 mA) or make sure the TVS to ground takes it instead of the rail.

## Practical notes
- **Put protection and RFI filtering at the connector**, before the signal enters the board's quiet area; route returns of the protection devices directly to chassis/ground entry.
- **Kelvin connections** for shunts and bridge excitation sense.
- **Test with the radio transmitting**: key the 433/915 MHz transmitter at full power with the antenna in its flight position and log all analog channels — offsets correlated with TX mean RF rectification or ground-return coupling (→ [power supplies](power-supplies-for-rf-and-analog.md)).
- **Characterise before trusting** — any measurement used for a safety decision (arming, deployment) needs a bench characterisation against known references and a fault-mode analysis (open, short, shorted to rail).

## Common mistakes & misconceptions
- **Building a "difference amplifier" with 1 % resistors and expecting 80 dB CMRR** — expect 34 dB worst case.
- **Driving an INA's REF pin from a resistor divider.**
- **Ignoring the INA's internal-node common-mode limits** on single supply (output and inputs in range, amplifier still saturated).
- **Direct high-value dividers into MCU ADCs without a pin capacitor.**
- **Clamp diodes to a lightly loaded rail** → back-powering (and "the board half-boots with the battery disconnected").
- **TVS stand-off voltage below the maximum normal voltage** (e.g. a 7 V TVS on a 2S pack).
- **Common-mode RFI filter without a differential capacitor** → CM→DM conversion by capacitor mismatch.
- **Measuring milliohms or a 1 Ω igniter with a single-ended ADC reading referenced to a ground that carries pyro current.**
- **Thick-film, high-tempco gain resistors** in precision INA stages.
- **Reading a remote voltage sensor single-ended across a ground that carries load current.** The ground offset is added to the reading; send the reference conductor and measure differentially.
- **Not checking 4–20 mA compliance at the longest cable and full scale.** When the transmitter runs out of voltage the current saturates *below* the true value and no fault is shown. Treat readings outside 3.8–20.5 mA as faults (NE 43).
- **A comparator without hysteresis on a slow or noisy signal**, e.g. a battery-low flag that toggles at the LoRa packet rate.
- **Using an op-amp as a fast comparator.** It is slow to recover from saturation, may have input clamps, and may phase-reverse.
- **Forgetting the pull-up of an open-drain comparator**, or making it so large that the rise time or the hysteresis divider is wrong.
- **A bipolar NE555 on a quiet analog rail.** Its transition spikes are large; use a CMOS 555 and decouple it.

## How to simulate / verify
- **Python:** `tools/verify/analog_signal_conditioning.py` — difference-amplifier CMRR worst-case formula vs Monte Carlo; INA333 $R_G$ and offset; bridge exact vs linear; RFI-filter corners and CM→DM conversion with capacitor mismatch; divider/ADC settling and kickback; clamp currents and TVS poles; level-shift feasibility; shunt and continuity numbers.
- **Loops, lines, comparators, 555:** `tools/verify/s3_lines_comparators.py` (+ `_output.txt`) — 4–20 mA levels and ngspice loop-compliance collapse; worst-case difference amp vs ground offset; Schmitt thresholds with E96 values checked by an ngspice sweep; chatter count with and without hysteresis; behavioural ngspice 555 vs the formula.
- **SPICE:** vendor INA macromodels (TI/ADI) reproduce CMRR vs frequency and input-range limits; add the RFI filter with ±5 % capacitor values and run `.ac` with a common-mode source; transient fault injection (a PWL 24 V step through the protection network) with the rail modelled as a regulator that cannot sink current shows back-powering.
- **Bench:** apply a common-mode sine to both inputs (shorted together) and measure output → CMRR; inject RF (a hand-held transmitter or a signal generator + small antenna) near sensor leads while logging; for continuity circuits, a decade box and a 4-wire DMM as references.

## Open questions / gaps
- Specific igniter no-fire/all-fire currents for the team's e-matches were not sourced; must come from the igniter's datasheet and be recorded with the continuity design.
- The ADI RFI-filter guidance ($C_d \ge 10C_c$) is cited from the INA-design literature; the ADI *Designer's Guide to Instrumentation Amplifiers* could not be fetched (analog.com timeouts).
- No part-specific TVS selection table for 1S/2S/3S packs yet (→ 18 components, 13 EMC).

## Sources
1. Texas Instruments, *INA333 micro-power (50 µA), zero-drift, rail-to-rail out instrumentation amplifier* datasheet SBOS445C. https://www.ti.com/lit/ds/symlink/ina333.pdf — gain equation, offset ±25 ± 75/G µV max, 0.1 µV/°C, 50 nV/√Hz, 1 µV p-p, CMRR ≥ 100 dB (G ≥ 10), input and output ranges, RFI-filtered inputs, 35 kHz at G = 10. (datasheet)
2. C. Kitchin, L. Counts, *A Designer's Guide to Instrumentation Amplifiers*, 3rd ed., Analog Devices 2006 — ch. 5–6 (RFI input filtering with differential and common-mode capacitors, $C_d \ge 10C_c$; input protection; bridge applications). (app note/book; not retrievable this session)
3. Texas Instruments, *INAx180 low- and high-side voltage-output current-sense amplifiers* datasheet. https://www.ti.com/lit/ds/symlink/ina180.pdf — CM −0.2 to 26 V, gains 20/50/100/200, offset ±150 µV (0 V) / ±500 µV (12 V), 350 kHz, ±1 % gain error. (datasheet)
4. W. Jung (ed.), *Op Amp Applications Handbook*, Analog Devices/Newnes 2005 — ch. 2 (difference and instrumentation amplifiers, CMRR from resistor matching), ch. 4 (sensor signal conditioning), ch. 7 (overvoltage protection, EMI/RFI). (textbook)
5. P. Horowitz, W. Hill, *The Art of Electronics*, 3rd ed., Cambridge 2015 — ch. 5 (precision circuits, instrumentation amplifiers, bridges), ch. 12 (input protection, back-powering through clamp diodes). (textbook)
6. IEC 61000-4-2, *Electromagnetic compatibility — Testing and measurement techniques — Electrostatic discharge immunity test*. (standard)
7. Space Bar avionics knowledge base (team-internal): flight-computer design lessons — pyro continuity sensing unreliable, pyro bus not cold on USB (backfeed), under-rated pyro-bus TVS, GPS back-powering avoided with a buffered UART, magnetometer offsets from a shared unfiltered regulator. (internal record)
8. NAMUR, *NE 43: Standardization of the signal level for the failure information of digital transmitters*, recommendation (1994, rev. 2003) — 3.8–20.5 mA measurement range, ≤ 3.6 / ≥ 21 mA failure signals (values cross-checked in several vendor summaries; the NAMUR text itself was not retrieved). (standard/recommendation)
9. A. Kay, T. Claycomb, *Comparator with Hysteresis Reference Design*, Texas Instruments TIDU020A, 2013. https://www.ti.com/lit/ug/tidu020a/tidu020a.pdf — threshold design, open-collector pull-up error ($R_h$ > 100 $R_p$). (app note)
10. Texas Instruments, *NE555/SA555/SE555 precision timers* datasheet SLFS022 — astable/monostable timing equations, supply-current transients; TLC555 datasheet for the CMOS version. (datasheet)
11. P. Horowitz, W. Hill, *The Art of Electronics*, 3rd ed., Cambridge 2015 — §12.3 (comparators, hysteresis, open-collector outputs), §7.2 (555 and monostables). (textbook)
