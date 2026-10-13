# 05-analog-electronics — Analog electronics for RF and sensor systems

Device physics and general analog circuit design that the RF (06), noise (07), SDR (14) and
LoRa/telemetry (15) domains build on: diodes (Schottky, PIN, varactor, step-recovery, Zener/TVS),
BJTs and FETs (Si, SiGe, GaAs, GaN, LDMOS), single- and multi-transistor amplifier topologies,
feedback and stability (including parasitic oscillation), real op-amps, low-noise design, active
filters, oscillators (LC, crystal, VCO, relaxation), data converters, power supplies for RF/analog
circuits, and sensor/ADC signal conditioning and protection. Lumped circuit theory and passive filter
prototypes live in [01](../01-circuit-theory/); real passive parasitics and crystals in [04](../04-real-components-hf/);
LNA/PA/mixer/PLL design in [06](../06-rf-circuits/); noise-figure and phase-noise theory in
[07](../07-noise-linearity/); PCB layout and EMC in [13](../13-pcb-rf-layout-emc/).

Every page has a matching verification script in `tools/verify/analog_*.py` (run with `python3`);
SPICE netlists on the pages run on the ngspice library bundled with KiCad via
`tools/verify/analog_ngspice.py` (no separate install needed on this Mac).

## Reading order (beginner → advanced)
1. [Diodes](diodes-schottky-pin-varactor.md) — the exponential junction, $V_T$, junction capacitance; then RF diode types.
2. [BJT fundamentals](bjt-fundamentals-small-signal.md) — $g_m = I_C/V_T$, hybrid-π, $f_T$/$f_{max}$, noise.
3. [FETs](fets-mosfet-jfet-gaas-gan.md) — MOSFET/JFET laws, $g_m/I_D$, HEMTs, GaN; device selection.
4. [Amplifier topologies](amplifier-topologies.md) — CE/CB/CC, cascode, diff pair, mirrors, feedback types, MMIC gain blocks.
5. [Feedback & stability](feedback-and-stability.md) — loop gain, phase margin, compensation, capacitive loads, parasitic oscillation.
6. [Op-amps: real limitations](op-amps-real-limitations.md) — GBW/noise gain, slew, noise, offsets, CMRR/PSRR, CFA, FDA; choosing.
7. [Low-noise design](low-noise-analog-design.md) — $e_n$–$i_n$ model, $R_{opt}$, NF of op-amp stages, resistor/1/f/kT/C noise.
8. [Active filters](active-filters.md) — Sallen-Key, MFB, biquads, tables, sensitivity, GBW, anti-alias.
9. [Oscillators](oscillators.md) — Barkhausen vs negative resistance, Colpitts/Pierce, crystal load caps, Leeson.
10. [Data converters](data-converters-adc-dac.md) — 6.02N+1.76, ENOB, jitter, aliasing, architectures, drivers, ADC NF.
11. [Power supplies for RF & analog](power-supplies-for-rf-and-analog.md) — LDO PSRR/noise, switcher spurs, LC damping, battery bursts.
12. [Analog signal conditioning](analog-signal-conditioning.md) — INAs, bridges, level shifting, protection, RFI filters, current sensing.

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [diodes-schottky-pin-varactor](diodes-schottky-pin-varactor.md) | Shockley law & tempco, depletion/diffusion C, Schottky detector responsivity and square-law limit (exact Bessel), PIN $R_S$ and switch IL/isolation, varactor C–V/Q/tuning, SRD, Zener/TVS at RF | mixed | high |
| [bjt-fundamentals-small-signal](bjt-fundamentals-small-signal.md) | Ebers–Moll, $g_m$, $r_\pi$, $r_o$, $f_T$ (hand vs ngspice), $f_{max}$ (vs Mason U), Miller, bias stability, $F_{min}$/$R_{opt}$/optimum $I_C$, breakdown, SiGe HBT | mixed | high |
| [fets-mosfet-jfet-gaas-gan](fets-mosfet-jfet-gaas-gan.md) | square law, velocity saturation, $g_m/I_D$ (EKV), JFET noise, HEMT/pHEMT, GaN power density & $R_{opt}$, Johnson limit, LDMOS, device-selection table, bias sequencing, pyro-FET gate drive | mixed | medium |
| [amplifier-topologies](amplifier-topologies.md) | basic stages, cascode, diff pair (tanh, IIP3 = 4$V_T$), degeneration IIP3 law, mirrors, Darlington, 4 feedback types, OCTC bandwidth, resistive-feedback gain block ($R_FR_E = Z_0^2$), MMIC biasing | mixed | high |
| [feedback-and-stability](feedback-and-stability.md) | loop gain, Bode/Nyquist, PM↔overshoot table, Miller pole splitting/RHP zero, capacitive load & $R_{ISO}$, TIA $C_F$, emitter-follower negative resistance and base stoppers | mixed | high |
| [op-amps-real-limitations](op-amps-real-limitations.md) | noise-gain bandwidth, slew/FPBW, 1/f integration, noise and DC budgets, CMRR/PSRR vs f, RRIO, zero-drift, CFA, FDA input impedance, EMI rectification, selection table | mixed | high |
| [low-noise-analog-design](low-noise-analog-design.md) | $e_n$–$i_n$ model, $R_{opt}$, $F_{min}$, transformers/paralleling, op-amp stage NF, resistor excess noise (noise index), kT/C, ENBW, TIA noise | mixed | high |
| [active-filters](active-filters.md) | SK/MFB equations (sympy), Butterworth/Bessel/Chebyshev section tables, Monte Carlo sensitivity, GBW needs, SK stop-band floor, anti-alias order | mixed | high |
| [oscillators](oscillators.md) | Barkhausen, Colpitts $R_{neg}$, Clapp/Hartley/Pierce, crystal $C_L$, $g_{m,crit}$, pulling ppm/pF, drive level, describing-function amplitude, Leeson, Wien, VCO tuning noise | mixed | high |
| [data-converters-adc-dac](data-converters-adc-dac.md) | quantisation SNR derivation & simulation, ENOB/SFDR/NSD, jitter SNR (derivation + Monte Carlo), aliasing & zone planning, ΣΔ, DAC sinc, kT/C, kickback, ADC NF & gain planning, references | mixed | high |
| [power-supplies-for-rf-and-analog](power-supplies-for-rf-and-analog.md) | LDO PSRR vs f & noise, buck ripple, LC/bead resonance and damping, pushing/AM spurs, 1S battery + 2 W LoRa burst droop, ground IR/bounce, sequencing, references | mixed | medium |
| [analog-signal-conditioning](analog-signal-conditioning.md) | difference-amp CMRR vs tolerance, INAs, bridges, level shifting, dividers into SAR ADCs, clamp back-powering, TVS choice, RFI filters, current sense, igniter continuity, isolation | mixed | high |

## Domain FAQ (top questions → page#section)
- *Why is a BJT's $g_m$ always $I_C/V_T$?* → [BJT#the-math](bjt-fundamentals-small-signal.md#the-math)
- *What limits my amplifier's bandwidth — $f_T$ or Miller?* → [BJT#level-2--derivations](bjt-fundamentals-small-signal.md#level-2--derivations), [topologies (OCTC)](amplifier-topologies.md#level-2--derivations)
- *Which transistor technology for an LNA or PA at 433/915 MHz, 2.4 GHz or 77 GHz?* → [FETs#design-equations--rules-of-thumb](fets-mosfet-jfet-gaas-gan.md#design-equations--rules-of-thumb) (selection table)
- *Why must GaN/GaAs amplifiers get gate bias before drain voltage?* → [FETs#worked-examples](fets-mosfet-jfet-gaas-gan.md#worked-examples) (example 4)
- *Will my pyro MOSFET fully turn on at 3.3 V?* → [FETs#worked-examples](fets-mosfet-jfet-gaas-gan.md#worked-examples) (example 1)
- *How much DC do I get from a Schottky detector, and where does square law end?* → [Diodes#level-2--derivations](diodes-schottky-pin-varactor.md#level-2--derivations)
- *How do I design a PIN RF switch?* → [Diodes#worked-examples](diodes-schottky-pin-varactor.md#worked-examples) (example 2)
- *Why do MMIC gain blocks look the way they do and how do I bias them?* → [Topologies#level-2--derivations](amplifier-topologies.md#level-2--derivations)
- *How much phase margin do I need, and what overshoot does it give?* → [Stability#level-2--derivations](feedback-and-stability.md#level-2--derivations)
- *Why does my op-amp oscillate driving a capacitor/cable/ADC?* → [Stability#worked-examples](feedback-and-stability.md#worked-examples)
- *Why does my emitter follower oscillate at UHF?* → [Stability#level-2--derivations](feedback-and-stability.md#level-2--derivations)
- *What bandwidth does my op-amp stage really have?* → [Op-amps#level-1--the-parameters-and-what-they-do](op-amps-real-limitations.md#level-1--the-parameters-and-what-they-do)
- *Which op-amp for a mV sensor / a high-impedance sensor / an ADC driver?* → [Op-amps#design-equations--rules-of-thumb](op-amps-real-limitations.md#design-equations--rules-of-thumb)
- *What is the optimum source resistance and NF of an amplifier?* → [Low-noise#level-2--derivations-and-design-consequences](low-noise-analog-design.md#level-2--derivations-and-design-consequences)
- *Why are thick-film resistors noisy?* → [Low-noise (excess noise)](low-noise-analog-design.md#level-2--derivations-and-design-consequences)
- *Sallen-Key or MFB, and what order anti-alias filter?* → [Active filters#tldr](active-filters.md#tldr)
- *Which load capacitors does my crystal need, and how far will it pull my LoRa frequency?* → [Oscillators#worked-examples](oscillators.md#worked-examples)
- *How does resonator Q set phase noise?* → [Oscillators (Leeson)](oscillators.md#level-2--derivations)
- *Where does 6.02N + 1.76 dB come from? How much jitter can I tolerate?* → [Data converters#level-2--derivations](data-converters-adc-dac.md#level-2--derivations)
- *Where will 433 MHz alias when I sample it, and how do I choose the sample rate?* → [Data converters#worked-examples](data-converters-adc-dac.md#worked-examples)
- *How much gain do I need ahead of an SDR's ADC?* → [Data converters (ADC NF)](data-converters-adc-dac.md#level-2--derivations)
- *Will an LDO clean up my switching regulator?* → [Power supplies#tldr](power-supplies-for-rf-and-analog.md#tldr)
- *Why does my LoRa transmitter disturb my sensor readings / brown out my board?* → [Power supplies#worked-examples](power-supplies-for-rf-and-analog.md#worked-examples) (example 3)
- *Why did my ferrite-bead filter make the rail noisier?* → [Power supplies#worked-examples](power-supplies-for-rf-and-analog.md#worked-examples) (example 4)
- *How do I read a bridge sensor / battery voltage / pyro current with an MCU ADC?* → [Signal conditioning#worked-examples](analog-signal-conditioning.md#worked-examples)
- *How can input protection back-power my board?* → [Signal conditioning#level-2--derivations-and-error-budgets](analog-signal-conditioning.md#level-2--derivations-and-error-budgets)
- *What resistor values should I use around an op-amp, and how do I AC-couple or sum signals?* → [Op-amps § practical recipes](op-amps-real-limitations.md#practical-recipes--resistor-values-ac-coupling-attenuators-a-mosfet-in-the-loop-summing-amplifiers)
- *How do I read a 4–20 mA sensor or run a long differential sensor line?* → [Signal conditioning § current loops](analog-signal-conditioning.md#current-loops-4-20-ma-and-long-differential-sensor-lines)
- *How do I build a comparator with hysteresis or a 555 timer?* → [Signal conditioning § comparators](analog-signal-conditioning.md#comparators-schmitt-triggers-and-timers)
- *What is a diode or transistor physically, and how do they fail?* → [Diodes § Level 0](diodes-schottky-pin-varactor.md#level-0--semiconductor-primer-doping-depletion-forward-voltages-how-diodes-fail), [BJT § Level 0](bjt-fundamentals-small-signal.md#level-0--v_be-f_beta-f_alpha-f_t-and-how-bjts-fail)
- *Can I power a sensor from ambient RF?* → [Diodes § rectennas](diodes-schottky-pin-varactor.md#rectennas--far-field-rf-energy-harvesting-efficiency-vs-input-power-ambient-budgets-the-exposure-cap)
- *How do I extend an amplifier's bandwidth (peaking, distributed, balanced)?* → [Topologies § bandwidth extension](amplifier-topologies.md#bandwidth-extension-and-broadband-amplifiers-peaking-t-coils-distributed-balanced-resistive-feedback-lnas)
- *Class A, B or AB output stage?* → [Topologies § output stages](amplifier-topologies.md#output-stages--class-a-class-b-and-class-ab-push-pull)
- *How do I design a mains rectifier and regulator, and is a switcher OK for a transmitter?* → [Power supplies § mains](power-supplies-for-rf-and-analog.md#mains-supply-fundamentals--rectifiers-ripple-series-and-shunt-regulators-smps-vs-linear-for-a-transmitter)
- *How long will my battery last on the pad, and what does the cold do?* → [Power supplies § batteries](power-supplies-for-rf-and-analog.md#batteries--chemistries-internal-resistance-ah--runtime-cold-and-peukert)

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
- Horowitz & Hill, *The Art of Electronics*, 3e — practical backbone for every page.
- Gray, Hurst, Lewis & Meyer, *Analysis and Design of Analog ICs*, 5e — device models, frequency response, noise, feedback.
- Sedra & Smith, *Microelectronic Circuits*; Razavi, *Design of Analog CMOS ICs* — derivations of stages and FET behaviour.
- Motchenbacher & Connelly, *Low-Noise Electronic System Design* — noise.
- Williams & Taylor, *Electronic Filter Design Handbook* — filter tables.
- Kester (ed.), *Data Conversion Handbook*; Schreier & Temes, *Understanding Delta-Sigma Data Converters* — converters.
- Jung (ed.), *Op Amp Applications Handbook*; TI *Op Amps for Everyone* — op-amp practice (free).
- Manufacturer notes actually read: Skyworks PIN and varactor notes, Mini-Circuits AN-60-010, TI SSZT999/SLVA043B/SLYT075, ST AN2867, LIGO T0900200, and ~20 datasheets (listed in `_sources.md`).

## Known gaps
- analog.com (ADI MT-series tutorials, Kester, Kitchin & Counts) was unreachable during this pass — several cross-checks rely on TI documents, textbooks and own derivations/simulations instead.
- FET page: representative (not part-specific) breakdown/current numbers in the power-density table; confidence medium.
- Power-supply page: battery internal resistance and wiring values are representative assumptions; E220-900T30D transmit current not sourced; ultra-high-PSRR LDO examples not sourced.
- Crystal motional parameters in the oscillator examples are representative, not from a specific datasheet.
- Thick-film resistor noise-index values per series not tabulated.
- MCU ADC (ESP32-S3, i.MX RT1062/Teensy 4.1) effective-bit figures not sourced — measure on hardware.
- Igniter no-fire/all-fire currents for continuity-test design must come from the igniter datasheet.
- Newly derived result worth an external cross-check: degenerated-BJT IIP3 law $A_{IIP3} = \sqrt8V_T(1+x)^2/\sqrt{|1-2x|}$ (topologies page).
