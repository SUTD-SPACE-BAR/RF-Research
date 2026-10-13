---
title: Op-amps — real limitations (GBW, slew, noise, offsets, CMRR/PSRR, output drive, RRIO, CFA, FDA) and how to choose one
domain: 05-analog-electronics
slug: op-amps-real-limitations
tags: [op-amp, gain-bandwidth, noise-gain, slew-rate, full-power-bandwidth, voltage-noise, current-noise, flicker-noise, offset, bias-current, cmrr, psrr, rail-to-rail, zero-drift, chopper, current-feedback, fully-differential, adc-driver, emi-rejection, selection]
prerequisites:
  - feedback-and-stability.md
  - amplifier-topologies.md
related:
  - low-noise-analog-design.md
  - active-filters.md
  - data-converters-adc-dac.md
  - analog-signal-conditioning.md
  - power-supplies-for-rf-and-analog.md
  - diodes-schottky-pin-varactor.md
  - ../07-noise-linearity/thermal-noise-and-noise-temperature.md
  - ../07-noise-linearity/shot-and-flicker-noise.md
  - ../18-components-parts/adcs-dacs-for-sdr.md
level: mixed
confidence: high
last_updated: 2026-10-12
---

# Op-amps — real limitations (GBW, slew, noise, offsets, CMRR/PSRR, output drive, RRIO, CFA, FDA) and how to choose one

## Questions this page answers
- Why is my gain-of-10 amplifier's bandwidth only a tenth of the op-amp's GBW — and why does an inverting gain of −1 only get half?
- What is the difference between small-signal bandwidth and full-power bandwidth?
- How do I add up $e_n$, $i_n$ and resistor noise, and what does the 1/f corner do to low-frequency noise?
- How big is the DC error of my circuit (offset, drift, bias current, CMRR, PSRR), and when do I need a zero-drift op-amp?
- Why does supply ripple from a switching regulator show up at the op-amp output?
- What does "rail-to-rail" really mean, and why is there distortion near the positive rail on some RRIO parts?
- Why can't I put a capacitor across the feedback resistor of a current-feedback amplifier?
- How do fully differential amplifiers drive ADCs, and what input impedance does a single-ended source see?
- Why does my sensor amplifier's output shift when the LoRa transmitter keys up?
- How do I choose an op-amp?
- What resistor values should I use for a given gain — 1 kΩ or 1 MΩ?
- Why does my AC-coupled non-inverting amplifier drift to a rail, and where does the bias resistor go on a single supply?
- Is an op-amp stable as an attenuator (gain below 1)?
- How do I stop an op-amp + MOSFET current sink from oscillating?
- Why is a summing amplifier noisier and slower than its gain suggests?

## TL;DR
- **Bandwidth is set by the noise gain** $NG = 1/\beta = 1 + Z_F/Z_G$, not the signal gain: $f_{-3dB} \approx GBW/NG$. Inverting −1 has NG = 2 → half the GBW (`tools/verify/analog_opamp.py` §1).
- **Slew rate** limits large signals: full-power bandwidth $FPBW = SR/(2\pi V_{pk})$. MCP6002 (0.6 V/µs) → 58 kHz at 1.65 V peak; OPA333 (0.16 V/µs) → 15 kHz (§2) [1][2]. A single-pole BJT-input op-amp has $SR = 4\pi V_T\cdot GBW$ ≈ 0.33 V/µs per MHz — degeneration or FET inputs raise it.
- **Noise:** $e_n$ (V/√Hz) is multiplied by NG; $i_n$ flows through the source and feedback resistances; add all in quadrature. 1/f: $v_{rms} = e_n\sqrt{f_c\ln(f_2/f_1) + (f_2-f_1)}$; peak-to-peak ≈ 6.6 × rms. Bipolar (OPA1612: 1.1 nV/√Hz, 1.7 pA/√Hz at 1 kHz [3]) wins below ~1 kΩ source; CMOS (MCP6002: 28 nV/√Hz, 0.6 fA/√Hz [1]) wins at high source impedance.
- **DC errors:** $V_{OS}$ + drift·ΔT + $I_B R$ + ΔV$_{CM}$/CMRR + ΔV$_S$/PSRR, all × NG at the output. MCP6002 (±4.5 mV max) vs OPA333 zero-drift (10 µV max, 0.05 µV/°C, auto-zeroed every 8 µs) — 5.6 mV vs 20 µV RTI in the same budget (§5) [1][2].
- **CMRR and PSRR fall ~20 dB/decade** above a low corner (often 10 Hz–10 kHz); an 86 dB PSRR can be ~26 dB at 100 kHz — so SMPS ripple at 0.3–2 MHz passes almost unattenuated (§6). Filter the op-amp supply.
- **Rail-to-rail** input usually means two complementary input pairs with a crossover region (offset step, distortion) ~1 V below V+; zero-drift/charge-pump designs avoid it. Output "rail-to-rail" swings to within tens of mV only at light load.
- **Current-feedback amplifiers (CFA):** bandwidth set by the feedback resistor, nearly independent of gain ($f_{-3dB} ≈ 1/[2\pi C_T(R_F + R_{in}G)]$ — 129 → 106 MHz from G = 1 to 10 vs a 250 MHz-GBW VFA's 250 → 25 MHz; §7); thousands of V/µs; high $i_n$; **never** a capacitor across $R_F$. THS3091: 6000 V/µs, 305 MHz at G = 2, 1.1 nV/√Hz but 14–15 pA/√Hz [4].
- **Fully differential amplifiers (FDA)** drive differential ADCs with set output common mode; single-ended input impedance $R_G/[1 - R_F/(2(R_G+R_F))]$ (1.33 kΩ for 1 kΩ/1 kΩ; sympy §8). THS4551: 135 MHz GBW, 3.3 nV/√Hz, HD2/HD3 −128/−139 dBc at 100 kHz [5].
- **Practical recipes** (ngspice, `tools/verify/s3_opamp_recipes.py`): keep $R_F$ ≈ 1–100 kΩ (100 k/1 M with 10 pF at the − input peaks +7.8 dB); AC-coupled non-inverting stages need a bias-return $R_B$ to mid-rail and $C_G$ in series with $R_G$ (else the output sits on a rail); noise gain is never < 1, so inverting attenuators are fine with unity-gain-stable parts — only decompensated parts need noise-gain shaping; an op-amp driving a MOSFET gate needs $R_{gate}$ + $C_F$/$R_F$ dual feedback (58 % → 3.5 % overshoot); an N-input summer has NG = 1 + N·$R_F$/R.
- **RF immunity:** op-amp input stages rectify RF (a nearby 2 W LoRa burst → DC shifts). Use RC/ferrite input filters and parts with a specified EMIRR.

## Intuition (no math)
An op-amp is an amplifier with enormous gain at DC (10⁵–10⁷) that falls steadily — by design — at 20 dB per decade, so that at the frequency GBW its gain is 1. Feedback works by comparing output against input; it can only enforce the closed-loop gain where the op-amp still has gain to spare. At a closed-loop gain of 10 the op-amp runs out of spare gain at GBW/10. What matters is how much of the output is fed back — the noise gain — because that is what the loop "sees"; an inverting amplifier of gain −1 feeds back half the output, so it behaves like a gain-of-2 loop.

Slew rate is a different, *large-signal* limit: the internal compensation capacitor is charged by a finite current, so the output can only change so many volts per microsecond no matter how small the signal's frequency content. A big sine wave hits the slew limit at a much lower frequency than its small-signal bandwidth.

The op-amp's imperfections can all be drawn as sources at its inputs: a small DC battery (offset voltage), small current sources (bias currents), and noisy versions of both (voltage and current noise). The circuit then amplifies these "input-referred" errors by the noise gain. This single picture handles DC error budgets, noise budgets and drift.

Supply and common-mode rejection are the op-amp's ability to ignore changes on its supply pins or on both inputs together. They are excellent at DC and poor at high frequency, because the internal circuitry that balances these errors out also runs out of loop gain.

## The math

### Level 1 — the parameters and what they do

| Parameter | Symbol / unit | Effect on circuit | Where it bites |
|---|---|---|---|
| Open-loop gain | $A_{OL}$, dB | gain error ≈ NG/$A_{OL}$ | high-gain, precision DC |
| Gain-bandwidth product | GBW, Hz | $f_{-3dB} ≈ GBW/NG$ | any AC gain |
| Slew rate | SR, V/µs | FPBW = SR/(2π$V_{pk}$) | large, fast signals, ADC drive |
| Offset voltage, drift | $V_{OS}$ (µV–mV), $dV_{OS}/dT$ | output offset = NG·$V_{OS}$ | DC sensors, detectors |
| Bias/offset current | $I_B$, $I_{OS}$ (fA–µA) | error = $I_B$ × resistance | high-Z sources |
| Voltage noise | $e_n$ (nV/√Hz), 1/f corner $f_c$ | output noise = NG·$e_n$ | low-Z sources |
| Current noise | $i_n$ (fA–pA/√Hz) | noise = $i_n$ × resistance | high-Z sources |
| CMRR, PSRR | dB (vs f) | error = Δ$V_{CM}$/CMRR, Δ$V_S$/PSRR | noisy supplies, bridges |
| Input CM range, output swing | V from rails | clipping, crossover distortion | single-supply, 3.3 V systems |
| Output current, $Z_o$ | mA, Ω | load drive; $Z_o$ + $C_L$ → instability | cables, ADCs, capacitive loads |
| Quiescent current | $I_Q$ | battery life, and speed/noise trade | battery systems |

**Closed-loop bandwidth.** For a single-pole op-amp $A(s) = A_0/(1+s/\omega_a)$ with $GBW = A_0\omega_a/2\pi$:
$$A_{CL}(s) = \frac{1/\beta}{1 + s/(2\pi\,GBW\,\beta)}\ \Rightarrow\ f_{-3dB} = GBW\cdot\beta = \frac{GBW}{NG}.$$

**Full-power bandwidth.** A sine $V_{pk}\sin\omega t$ has maximum slope $\omega V_{pk}$; slewing starts when $\omega V_{pk} > SR$:
$$FPBW = \frac{SR}{2\pi V_{pk}}.$$

**Input-referred error model.** Output error $= NG\cdot[V_{OS} + I_{B+}R_+ - I_{B-}(R_F\|R_G) + \dots]$; output noise density
$$e_{out}^2 = NG^2\left[e_n^2 + i_{n+}^2R_s^2 + i_{n-}^2(R_F\|R_G)^2 + 4kTR_s + 4kT(R_F\|R_G)\right].$$

### Level 2 — derivations and budgets

**Why SR ∝ GBW in simple op-amps.** In a two-stage Miller-compensated op-amp, the input pair's tail current $I_{tail}$ is the most current available to charge $C_c$, so $SR = I_{tail}/C_c$. The small-signal GBW is $g_{m1}/(2\pi C_c)$ with $g_{m1} = (I_{tail}/2)/V_T$ for a BJT pair. Dividing: $SR = 2\pi\,GBW\cdot 2V_T = 4\pi V_T\,GBW$ — 0.33 V/µs per MHz (§2). Degenerating the input pair (lower $g_m$ per current) or using FET inputs (larger $V_{ov}$) raises SR/GBW; CFAs escape it entirely (below).

**1/f noise integration.** With $e_n^2(f) = e_{n,w}^2(1 + f_c/f)$ (white level $e_{n,w}$, corner $f_c$):
$$v_{rms}^2 = \int_{f_1}^{f_2}e_n^2(f)\,df = e_{n,w}^2\left[f_c\ln\frac{f_2}{f_1} + (f_2-f_1)\right].$$
10 nV/√Hz with a 100 Hz corner over 0.1–10 Hz: 217 nV rms (closed form = numeric), ≈ 1.4 µV p-p using the common 6.6 × rms (≈ 99.9 % of Gaussian samples) convention (§3). Only the *ratio* $f_2/f_1$ enters the 1/f part: every decade adds the same amount — you cannot filter it away by narrowing the band, only by lowering $f_c$ (larger devices, bipolar inputs) or chopping/auto-zeroing. From the MCP6002's 6.1 µV p-p (0.1–10 Hz) and 28 nV/√Hz at 1 kHz, the implied corner is ≈ 230 Hz (§3) [1]. A single-pole filter's noise bandwidth is $(\pi/2)f_{-3dB}$ (1571 Hz for 1 kHz, §3; → [low-noise design](low-noise-analog-design.md)).

**Zero-drift (auto-zero/chopper) op-amps** measure and cancel their own offset continuously, removing $V_{OS}$, drift and 1/f noise; the OPA333 corrects every 8 µs [2]. Costs: chopping/auto-zero ripple and spurs near the correction frequency (and its aliasing products with signals near it), higher broadband noise density than a good bipolar part, and input current *spikes* rather than a steady $I_B$ (the 70 pA typical is an average [2]).

**DC error budget** (§5; G = +11, 10 kΩ source, ΔT = 50 K, 1 V common-mode change, 0.2 V supply change):

| Term | MCP6002 [1] | OPA333 [2] |
|---|---|---|
| $V_{OS}$ (max) | 4500 µV | 10 µV |
| drift × 50 K | 100 µV | 2.5 µV |
| $I_B$ × 10 kΩ | 0.01 µV | 2 µV |
| 1 V / CMRR | 1000 µV (60 dB min) | 5 µV (106 dB) |
| 0.2 V / PSRR | 10 µV (86 dB) | 1 µV (5 µV/V) |
| **Sum RTI → RTO (×11)** | **5.6 mV → 62 mV** | **20 µV → 0.23 mV** |

A CMOS general-purpose op-amp is fine for AC-coupled or calibrated signals; mV-level DC signals (bridges, thermocouples, diode detectors) need zero-drift or precision parts. Note the MCP6002's 1 pA bias current makes it better than many "precision" bipolar parts on the $I_B$ line.

**CMRR/PSRR vs frequency.** Both are typically flat to a corner (10 Hz–10 kHz) and then fall ~20 dB/decade. Example (§6): 86 dB at DC with a 100 Hz corner → 46 dB at 10 kHz, 26 dB at 100 kHz, ~6 dB at 1 MHz. 20 mV of 1 MHz buck-converter ripple then appears as ~10 mV RTI — at a gain of 10 it swamps a sensor signal. Check the PSRR *plot*, not the table value, and filter the supply with an RC/LC/LDO (→ [power supplies](power-supplies-for-rf-and-analog.md)).

**Current-feedback amplifier (CFA).** The input stage is a unity-gain buffer from + to − input (low output resistance $R_{in}$ ≈ 10–50 Ω at the − input); the *current* out of the − input drives a transimpedance stage $Z(s) = R_t/(1+sR_tC_T)$. With feedback $R_F$ and gain resistor $R_G$ (G = 1 + $R_F/R_G$):
$$A_{CL}(s) = \frac{G}{1 + \dfrac{R_F + R_{in}G}{Z(s)}}\ \Rightarrow\ f_{-3dB} \approx \frac{1}{2\pi C_T(R_F + R_{in}G)}.$$
With $R_F$ fixed, gain is set by $R_G$ and bandwidth barely moves (129 → 106 MHz for G = 1 → 10 in the §7 model). Consequences: use the datasheet's recommended $R_F$ (THS3091: 1.78 kΩ at G = 1, 1.21 kΩ at G = 2 [4]); lower $R_F$ → more bandwidth but less phase margin; a capacitor across $R_F$ lowers the feedback impedance at high frequency → oscillation. Slew rate is not limited by a fixed tail current (the input buffer delivers current proportional to the error), giving thousands of V/µs [4][6].

**Fully differential amplifier (FDA).** Two outputs, a separate common-mode loop forcing $(v_{op}+v_{on})/2 = V_{OCM}$, and two matched feedback networks. Differential gain $R_F/R_G$. With a single-ended source driving one $R_G$ (other $R_G$ grounded), the virtual inputs move with the input common mode, so the source sees
$$R_{in,SE} = \frac{R_G}{1 - \dfrac{R_F}{2(R_G+R_F)}} = \frac{2R_G(R_G+R_F)}{2R_G+R_F}$$
(1333 Ω for 1 kΩ/1 kΩ; sympy nodal derivation §8). Match the source impedance into *both* $R_G$ legs (add $R_s$ to the grounded leg) to keep the feedback factors equal, or the output common-mode noise and even-order distortion rise. FDAs convert single-ended to differential for SAR/pipeline ADCs, level-shift to the ADC's common mode, and cancel even harmonics (THS4551 HD2 −128 dBc [5]).

### Level 3 — the less obvious limitations
- **Input common-mode range and phase reversal:** some older JFET and bipolar op-amps invert their output when an input goes beyond the CM range; modern datasheets state "no phase reversal". Never assume rail-to-rail input unless stated.
- **RRIO crossover:** complementary input pairs hand over ~0.8–1.5 V below V+; offset changes by up to hundreds of µV and THD degrades across the transition. For ADC drivers keep the signal on one side, or use zero-crossover (charge-pump) parts [2].
- **Differential input limits:** many bipolar op-amps have back-to-back clamp diodes across the inputs; used as comparators or during slewing they draw large input currents.
- **Output stage:** swing to the rail degrades with load current (MCP6002: within 25 mV only at light load [1]); short-circuit current is a few mA in micropower parts (OPA333 ±5 mA [2]) — driving an ADC's sampling capacitor or a 1 kΩ load may exceed what a micropower part can do quickly.
- **Open-loop output impedance** can be kΩ for micropower parts (OPA333: 2 kΩ at 350 kHz [2]) — a small capacitive load already adds a low pole (→ [feedback & stability](feedback-and-stability.md)).
- **Distortion vs frequency:** closed-loop distortion ≈ open-loop distortion / loop gain; loop gain falls with frequency, so THD rises ~20 dB/decade above the op-amp's dominant pole.
- **EMI rectification:** RF on the inputs (or supply, or output) is rectified by the input transistors' nonlinearity and appears as a DC offset or as audio/envelope demodulation — e.g. the TDMA-like buzz of a phone or the packet envelope of a LoRa transmitter. Datasheets increasingly specify EMIRR (dB vs frequency) [7]. Put a series R and small C (or ferrite) at inputs that come from cables, keep the transmitter's PA return currents out of the sensor ground (→ [EMC](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md)).
- **Decompensated op-amps** (stable only for NG ≥ 5, 10…) offer higher GBW/SR for high-gain stages; unusable as buffers.

### Practical recipes — resistor values, AC coupling, attenuators, a MOSFET in the loop, summing amplifiers
All numbers in this subsection are from `tools/verify/s3_opamp_recipes.py` (ngspice; output in `s3_opamp_recipes_output.txt`). The op-amp is a two-pole macro-model: GBW 10 MHz, second pole at 1.73 × GBW, which gives about 60° phase margin as a follower. Resistor noise is computed at 300 K, as in the other budgets on this page.

**1. Choosing resistor values (an inverting gain of −10).** The gain fixes only the *ratio* $R_F/R_G$. The impedance level is a compromise between four effects:

| $R_G$ / $R_F$ | Noise referred to the signal input, bipolar ($e_n$ 1.1 nV, $i_n$ 1.7 pA) / CMOS (MCP6002) | Output error from $I_B$ = 100 nA × $R_F$ (bipolar) | Current drawn through $R_F$ at 1 V output | Pole $1/(2\pi (R_F\|R_G)C_{in})$ with 5 pF, vs crossover GBW/NG = 909 kHz |
|---|---|---|---|---|
| 100 Ω / 1 kΩ | 1.8 / 30.8 nV/√Hz | 0.1 mV | 1 mA | 350 MHz |
| 1 kΩ / 10 kΩ | 4.8 / 31.1 | 1 mV | 0.1 mA | 35 MHz |
| 10 kΩ / 100 kΩ | 21.7 / 33.6 | 10 mV | 10 µA | 3.5 MHz |
| 100 kΩ / 1 MΩ | 175 / 52.6 | 100 mV | 1 µA | **350 kHz — inside the loop bandwidth** |
| 1 MΩ / 10 MΩ | 1705 / 138 | 1 V | 0.1 µA | 35 kHz |

- **Too low.** The resistors load the op-amp output and the signal source (an inverting stage's input resistance is $R_G$). They also waste supply current. Below a few hundred ohms, the output stage's distortion and heating start to matter.
- **Too high.** Resistor thermal noise, $i_n$ and $I_B$ all grow with resistance. Board leakage (≈ 10¹⁰–10¹² Ω, worse when dirty or humid) starts to compete with 10 MΩ parts. The input capacitance (pin plus about 1–3 pF of pad and trace) forms a pole with $R_F\|R_G$ *inside the feedback network*, which removes phase margin. In ngspice, 100 kΩ/1 MΩ with 10 pF at the inverting input peaks **+7.8 dB at 380 kHz**. Adding $C_F = R_GC_{in}/R_F$ (1 pF) across $R_F$ removes the peak completely, but it also sets a closed-loop pole at $1/(2\pi R_FC_F)$ = 159 kHz. A smaller $C_F$ trades a little peaking for bandwidth.
- **Sweet spot.** For general-purpose voltage-feedback op-amps, make $R_F$ ≈ 1–100 kΩ. Go to the low end with low-noise bipolar parts and fast signals. Go to the high end, or higher, with CMOS parts on micropower budgets, accepting the noise and adding $C_F$. CFAs are different: use the datasheet's $R_F$.

**2. AC-coupled non-inverting stage on a single supply — the bias-return path.** A coupling capacitor in front of the + input leaves that input with **no DC path**. The bias current then charges $C_{in}$: 100 nA into 1 µF ramps the input at 0.1 V/s and hits a rail in about 16 s (ngspice transient). Even a 1 pA CMOS input is left at a voltage set by leakage, so its operating point is undefined. The recipe (ngspice-verified, 3.3 V, gain 21):
- $R_B$ = 100 kΩ from the + input to a **mid-rail bias** (a 100 k/100 k divider decoupled by 10 µF). Not to ground: on a single supply, ground is the bottom rail.
- **DC gain 1 for the bias.** Put $C_G$ (10 µF) in series with $R_G$ (4.99 kΩ). DC then sees a follower, so the output sits at mid-rail: ngspice gives 1.635 V, the 15 mV deficit being $I_BR_B$ = 10 mV plus the divider loading. If $R_G$ goes straight to ground, the mid-rail bias is amplified ×21 and **the output sits at the 3.3 V rail** (ngspice).
- **Two low-frequency corners**, at $1/(2\pi R_BC_{in})$ = 1.6 Hz and $1/(2\pi R_GC_G)$ = 3.2 Hz. Together they give a −3 dB point of 3.9 Hz. Put the larger time constant on the side you care less about.
- **Cost.** $I_BR_B$ is a DC offset, and the $R_B$ noise current flows in the source impedance. For bipolar parts keep $R_B$ ≲ 100 kΩ. CMOS parts tolerate MΩ, but the bias network must not inject supply noise: decouple the mid-rail.

**3. Attenuators, "gain below one" and stability.** The loop sees the noise gain $NG = 1 + R_F/R_{in}$, which is **never below 1**, whatever the signal gain. An inverting −0.1 stage (10 kΩ in, 1 kΩ feedback) has NG = 1.1, so it has slightly *more* phase margin than a follower. ngspice peaking with a unity-gain-stable model: follower +0.08 dB, −0.1 attenuator +0.04 dB. Some textbooks and app notes warn against "op-amp attenuators" in general [9]; forum threads dispute this (forum — anecdotal). The correct statement is narrower:
- **The trap is a decompensated op-amp** (stable only for NG ≥ 5): as a −0.1 attenuator it peaks **+4.9 dB at 25 MHz**.
- **Fix: noise-gain shaping.** Put $R_n$ + $C_n$ from the inverting input to ground so that, near crossover, $NG_{hf} = 1 + R_F/(R_{in}\|R_n) = 5$. With $R_n$ = 256 Ω and $C_n$ = 10 nF, the peaking drops to +0.10 dB. $C_n$ keeps the DC noise gain at 1.1, so offset is not amplified. The noise *above* the $R_nC_n$ zero is amplified by 5, the price of the fix (→ [feedback & stability](feedback-and-stability.md)).
- A passive divider in front of a follower is the simplest attenuator when the source can drive it.

**4. A MOSFET inside the loop (V-to-I current sink, LED/heater/load-test driver).** The op-amp drives a MOSFET gate, and the feedback comes from the source sense resistor $R_S$, so $I = V_{set}/R_S$. The MOSFET is a source follower inside the loop. Its gate capacitance ($C_{iss}$ ≈ 1–2 nF for small power FETs) forms a pole with the op-amp's open-loop output resistance $R_o$: $1/(2\pi R_oC_{iss})$ ≈ 1 MHz for 100 Ω and 1.5 nF. That pole sits *below* the loop crossover. Simulated 0.1 → 0.2 A step (10 MHz op-amp, $R_o$ = 100 Ω, 1.5 nF + 0.2 nF gate capacitance, $R_S$ = 1 Ω):
- **Direct drive: 58 % overshoot**, ringing near 1 MHz. With a bigger FET or a slower op-amp it oscillates.
- **Dual feedback** settles with **3.5 % overshoot in 1.7 µs**. It uses a gate resistor $R_{gate}$ = 100 Ω (isolates the capacitance; also damps VHF oscillation of the FET itself), a local high-frequency feedback $C_F$ = 220 pF from the op-amp *output* to its inverting input, and $R_F$ = 1 kΩ from $R_S$ to the inverting input (DC accuracy). This is the $R_{ISO}$ + dual-feedback recipe for a capacitive load ([feedback & stability](feedback-and-stability.md)). Too much $C_F$ (≥ 1 nF here) removes the overshoot but stretches settling to 7–16 µs.
- Check the MOSFET's linear-mode safe operating area ($V_{DS}I_D$ for the full pulse length): trench FETs specified only for switching can fail in linear mode (→ [FETs](fets-mosfet-jfet-gaas-gan.md)).

**5. Summing amplifier noise gain.** An inverting summer with N inputs of resistance R has, for each input, a signal gain of $-R_F/R$. Its noise gain is $1 + R_F/(R/N)$, because all the input resistors are in parallel from the loop's point of view. Four 10 kΩ inputs with 10 kΩ feedback: unity gain per input but NG = 5, so the bandwidth is GBW/5 (ngspice: 200 kHz for a 1 MHz op-amp), and $e_n$ and $V_{OS}$ appear ×5 at the output. Unused inputs still count unless they are removed. Summing many channels at low gain is therefore noisy and slow. A passive resistive sum into a non-inverting stage has the same issue.

**6. RF rectification ("GSM buzz", LoRa-packet thump).** This is a frequent cause of "mysterious" DC shifts. The cure is an RC or ferrite at every input that comes from a cable, together with a closed PA return loop. See EMI rectification above and [EMC — rectification](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md#level-3--susceptibility-rectification-pyro-circuits-esd). For long sensor lines and 4–20 mA loops, see [signal conditioning](analog-signal-conditioning.md#current-loops-4-20-ma-and-long-differential-sensor-lines).

## Design equations & rules of thumb

| Quantity | Equation | Notes |
|---|---|---|
| Noise gain | $NG = 1 + Z_F/Z_G$ | same for inverting and non-inverting |
| Closed-loop BW | $GBW/NG$ | single-pole op-amp |
| Gain error | ≈ $NG/A_{OL}$ | at DC; grows with f |
| Full-power BW | $SR/(2\pi V_{pk})$ | large-signal |
| SR vs GBW (BJT pair) | $4\pi V_TGBW$ | ≈ 0.33 V/µs per MHz |
| Settling (single pole) | $t = \tau\ln(1/\epsilon)$, $\tau = 1/(2\pi f_{-3dB})$ | 16-bit (15 ppm): 11.1 τ; plus slew time |
| 1/f + white noise | $e_n\sqrt{f_c\ln(f_2/f_1)+(f_2-f_1)}$ | per-decade 1/f contribution constant |
| p-p from rms | × 6.6 | Gaussian, 0.1 % exceedance |
| ENBW single pole | $(\pi/2)f_{-3dB}$ | → low-noise page |
| Resistor noise | $\sqrt{4kTR}$ = 4.00 nV/√Hz @ 1 kΩ at $T_0$ = 290 K (4.07 at 300 K) | budgets on this page use 300 K |
| Crossover source resistance | $R_s ≈ e_n/i_n$ | below: $e_n$ dominates; above: $i_n$ |
| Output DC error | $NG(V_{OS} + \dots)$ | budget table above |
| CFA bandwidth | $1/[2\pi C_T(R_F + R_{in}G)]$ | set by $R_F$ |
| FDA SE input R | $R_G/[1 - R_F/(2(R_G+R_F))]$ | — |
| Resistor level | $R_F$ ≈ 1–100 kΩ; feedback pole $1/(2\pi(R_F\|R_G)C_{in})$ ≫ GBW/NG | else add $C_F = R_GC_{in}/R_F$ |
| AC-coupled non-inv. | $R_B$ to mid-rail; corners $1/(2\pi R_BC_{in})$, $1/(2\pi R_GC_G)$ | DC gain 1 via $C_G$ |
| Attenuator NG | $1 + R_F/R_{in}$ ≥ 1 | shaping: $NG_{hf} = 1 + R_F/(R_{in}\|R_n)$ |
| Summer NG | $1 + NR_F/R$ (N equal inputs) | bandwidth GBW/NG |
| Op-amp + MOSFET | pole $1/(2\pi R_oC_{iss})$ inside loop | $R_{gate}$ 47–220 Ω + $C_F$/$R_F$ |

**Choosing an op-amp — first cut**

| Application | Prioritise | Typical choice |
|---|---|---|
| mV DC signals (bridges, detectors, thermocouples) | $V_{OS}$, drift, 1/f, CMRR | zero-drift CMOS (OPA333 class) or precision bipolar |
| High-impedance sensors (pH, piezo, photodiode, electrometer) | $I_B$, $i_n$, input C | CMOS/JFET input |
| Low-impedance, low-noise audio/sensor (< 1 kΩ) | $e_n$, 1/f | bipolar (OPA1612 class) |
| General 3.3 V buffering, slow sensors | RRIO, $I_Q$, cost | MCP6002 / LMV321 class |
| SAR ADC driving (16–18 bit) | settling, $e_n$, THD, output Z | FDA (THS4551 class) or fast precision VFA + RC |
| Video/IF, large fast swings, cables | SR, BW at gain, drive | CFA (THS3091 class) or high-speed VFA |
| Battery-powered always-on | $I_Q$ | nanopower CMOS — accept low GBW/SR |

## Worked examples

### 1. Amplifying a zero-bias diode detector (2.7 mV full-scale) for a 3.3 V ADC
From the [diode page](diodes-schottky-pin-varactor.md): −25 dBm gives 2.66 mV from a ~9 kΩ source. Target 2.5 V full scale → gain ≈ 940.
- MCP6002: 4.5 mV $V_{OS}$ exceeds the signal — unusable without calibration and chopping.
- OPA333: 10 µV (0.4 % of full scale), 0.05 µV/°C, $I_B$ 200 pA × 9 kΩ = 1.8 µV. But GBW 350 kHz / 940 = 370 Hz bandwidth; fine for a slowly updated power reading, too slow for per-packet envelope. Split the gain (e.g. ×31 then ×31: 11 kHz each) or pick a higher-GBW zero-drift part.
- Noise: 1.1 µV p-p (0.1–10 Hz) ≈ 0.04 % of full scale — negligible compared with detector temperature drift (−0.34 %/K).

### 2. Noise budget of a ×101 non-inverting stage ($R_F$ = 100 kΩ, $R_G$ = 1 kΩ, $R_s$ = 1 kΩ)
(§4) Input-referred: OPA1612 → 6.3 nV/√Hz (resistors dominate: 4.07 + 4.05 nV/√Hz at 300 K); MCP6002 → 28.6 nV/√Hz ($e_n$ dominates); THS3091 CFA → 21.9 nV/√Hz ($i_n$ = 15 pA/√Hz × 1 kΩ dominates). Lesson: the "1.1 nV/√Hz" CFA is not a low-noise preamp at 1 kΩ; and at this source impedance the bipolar op-amp's own noise is already below the resistors'.

### 3. Single-ended sensor to a differential 16-bit SAR ADC with an FDA
THS4551, $R_G = R_F$ = 1 kΩ (gain 1), $V_{OCM}$ = ADC mid-scale. Source sees 1.33 kΩ (§8). Output noise density: NG·$e_n$ = 2 × 3.3 = 6.6 nV/√Hz plus four resistors each contributing 4.07 nV/√Hz at the output → 10.5 nV/√Hz differential; through a 100 kHz RC between FDA and ADC (ENBW 157 kHz; the RC also absorbs charge kick-back — see [data converters](data-converters-adc-dac.md)) that is 4.2 µV rms, far below a 16-bit LSB of 153 µV (±5 V differential span, 10 V/2¹⁶) (script §9). Settling: 18-bit in < 500 ns for 4 V steps [5].

### 4. Why a gain-of-−1 inverter is slower than a follower
Same op-amp (1 MHz GBW): follower 1 MHz; inverting −1 → NG = 2 → 500 kHz; inverting −10 → NG = 11 → 91 kHz (§1).

## Practical notes
- **Decouple every op-amp** with 100 nF at the pins plus bulk nearby; high-speed parts need low-ESL capacitors and a ground plane directly under them.
- **Bias-current compensation resistor** (matching DC resistance at both inputs) helps bipolar op-amps with matched $I_B$; it only adds noise for CMOS/JFET or bias-cancelled parts.
- **High-speed layout:** remove ground plane under the inverting-input node to reduce its capacitance; keep $R_F$ short; for CFAs never add $C_F$.
- **Protect inputs** from cables with series resistors and clamps; respect the maximum input current (often 10 mA) (→ [signal conditioning](analog-signal-conditioning.md)).
- **In mixed RF boards** (flight computers with 1–2 W LoRa), filter op-amp inputs and supplies against RF, and test with the transmitter keyed at full power next to the board.
- **JLCPCB availability:** general-purpose CMOS dual op-amps (LMV358/MCP6002 class) are cheap basic parts; precision and high-speed parts are usually extended parts — check before designing in.

## Common mistakes & misconceptions
- **Computing bandwidth from signal gain instead of noise gain.**
- **Using small-signal bandwidth for large signals** — a 1 MHz op-amp may only deliver full-scale sine to tens of kHz.
- **Taking the headline $e_n$ at 1 kHz for a 0.1–10 Hz application** — 1/f dominates; read the 0.1–10 Hz p-p spec.
- **Ignoring $i_n$ with high-value resistors** or using bipolar/CFA parts with high-impedance sources.
- **Trusting "rail-to-rail" literally** — check the output swing at your load and the input crossover region.
- **Relying on DC PSRR** with a switching regulator supply.
- **Capacitor across the feedback resistor of a CFA** — it oscillates.
- **Driving capacitive loads (cables, ADC inputs, reference pins) directly** — add $R_{ISO}$ (→ [feedback & stability](feedback-and-stability.md)).
- **AC-coupling the + input with no DC return**, or returning $R_B$ to ground on a single supply (→ recipe 2).
- **Returning $R_G$ to ground in a single-supply AC amplifier**, which multiplies the mid-rail bias by the gain and pins the output to a rail. Put a capacitor in series with $R_G$.
- **"Op-amps are unstable at gains below 1."** The loop sees the noise gain, which is ≥ 1. The real problem is decompensated parts and capacitive loads.
- **Driving a MOSFET gate straight from an op-amp in a current-sink loop** — the gate capacitance is a capacitive load inside the loop.
- **Using MΩ feedback resistors without $C_F$** — the input-capacitance pole causes peaking or oscillation.
- **Assuming a zero-drift op-amp is always quieter** — it is quieter at low frequency, but chopping ripple and broadband noise can be worse than a good bipolar part above ~100 Hz.

## How to simulate / verify
- **Python:** `tools/verify/analog_opamp.py` — noise-gain bandwidth checks, FPBW numbers, SR/GBW relation, 1/f integration (closed form vs numeric), MCP6002 1/f-corner inference, ENBW, stage noise budgets, DC error budgets, PSRR ripple feedthrough, CFA vs VFA bandwidth model, FDA input impedance by sympy.
- **Recipes:** `tools/verify/s3_opamp_recipes.py` (+ `_output.txt`) — resistor-value table, input-capacitance peaking and $C_F$, AC-coupled bias return (.op of right/wrong versions, transient drift), attenuator stability with unity-gain-stable vs decompensated macro-models and noise-gain shaping, MOSFET current-sink step response, summing-amp bandwidth — all in ngspice.
- **SPICE:** use vendor macromodels (TI, ADI, Microchip publish them; they model $e_n$, $i_n$, $Z_o$, CMRR/PSRR vs f to varying fidelity). Run `.noise` for output noise density and integrate; `.ac` with an AC source on the supply pin to see PSRR; transient steps for slew/settling. For quick what-ifs a single-pole model is enough:
```spice
* single-pole op-amp macro (GBW 1 MHz, A0 = 1e5, Ro 100 ohm) in a gain-of-10 non-inverting stage
.subckt OA1 inp inn out
Gin 0 n1 inp inn 1m
Rp n1 0 100Meg
Cp n1 0 159p
Eb n2 0 n1 0 1
Ro n2 out 100
.ends
Vin in 0 AC 1
X1 in fb out OA1
Rf out fb 9k
Rg fb 0 1k
.ac dec 50 10 10MEG
.end
```
  $A_0 = G_mR_p = 10^5$, open-loop pole $1/(2\pi R_pC_p)$ = 10 Hz → GBW = 1 MHz. The closed-loop −3 dB appears at ≈ GBW/10 = 100 kHz (checked with ngspice, script §9).
- **Bench:** measure output offset with inputs shorted; 0.1–10 Hz noise with a 0.1 Hz HPF / 10 Hz LPF and a scope; PSRR by injecting a sine onto the supply through a coupling network.

## Open questions / gaps
- OPA333 noise density (nV/√Hz) is shown only as a figure; not quoted.
- ADI MT-series tutorials (MT-033/-034/-047/-048) timed out; CFA and noise equations here are derived and cross-checked against TI datasheets and textbooks only.
- EMIRR: TI's SBOA128 defines it; numbers for specific parts at 433/915 MHz not collected (→ gap for 13 EMC).

## Sources
1. Microchip, *MCP6001/1R/1U/2/4 1 MHz Low-Power Op Amp* datasheet DS20001733L. https://ww1.microchip.com/downloads/en/DeviceDoc/MCP6001-1R-1U-2-4-1-MHz-Low-Power-Op-Amp-DS20001733L.pdf — GBW 1 MHz, SR 0.6 V/µs, $V_{OS}$ ±4.5 mV, drift ±2 µV/°C, $I_B$ ±1 pA, CMRR 60/76 dB, PSRR 86 dB, 28 nV/√Hz, 6.1 µV p-p, 0.6 fA/√Hz, 100 µA, PM 90°. (datasheet)
2. Texas Instruments, *OPAx333 1.8-V micropower CMOS zero-drift op amps* datasheet SBOS351E. https://www.ti.com/lit/ds/symlink/opa333.pdf — $V_{OS}$ 10 µV max, 0.05 µV/°C, PSRR 5 µV/V, $I_B$ ±200 pA, CMRR ≥ 106 dB, GBW 350 kHz, SR 0.16 V/µs, 1.1 µV p-p, $Z_o$ 2 kΩ, ±5 mA, 17 µA, 8 µs correction. (datasheet)
3. Texas Instruments, *OPA161x SoundPlus high-performance bipolar-input audio op amps* datasheet. https://www.ti.com/lit/ds/symlink/opa1612.pdf — 1.1 nV/√Hz, 1.7 pA/√Hz @ 1 kHz, 27 V/µs, 40 MHz, 3.6 mA. (datasheet)
4. Texas Instruments, *THS309x high-voltage, low-distortion current-feedback op amps* datasheet. https://www.ti.com/lit/ds/symlink/ths3091.pdf — 6000 V/µs, 305 MHz (G = 2), 1.1 nV/√Hz, 14–15 pA/√Hz, ±310 mA, $R_F$ 1.78 k / 1.21 k. (datasheet)
5. Texas Instruments, *THS4551 low-noise, precision, 150-MHz fully differential amplifier* datasheet SBOS778D. https://www.ti.com/lit/ds/symlink/ths4551.pdf — 135 MHz GBW, 220 V/µs, 3.3 nV/√Hz, HD2/HD3 −128/−139 dBc, 1.37 mA, settling. (datasheet)
6. Analog Devices, *MT-034: Current Feedback (CFB) Op Amps* tutorial. https://www.analog.com/media/en/training-seminars/tutorials/MT-034.pdf — CFA architecture; bandwidth set by feedback resistor (identified via search; PDF timed out). (app note)
7. Texas Instruments, *EMI Rejection Ratio of Operational Amplifiers*, SBOA128. https://www.ti.com/lit/pdf/sboa128 — EMIRR definition and measurement. (app note; not read in full)
8. W. Jung (ed.), *Op Amp Applications Handbook*, Analog Devices/Newnes 2005 — ch. 1 (op-amp specifications, noise, CFA), ch. 6 (sensor signal conditioning). (textbook; free from ADI)
9. R. Mancini (ed.), *Op Amps for Everyone*, TI SLOD006B, 2002 — ch. 8–11 (CFA vs VFA, error sources, noise). https://www.ti.com/lit/an/slod006b/slod006b.pdf (app note/book)
10. P. Horowitz, W. Hill, *The Art of Electronics*, 3rd ed., Cambridge 2015 — ch. 4 (op-amp limitations, single-supply biasing, op-amp + transistor current sources), ch. 5 (precision design, zero-drift), ch. 8 (noise). (textbook)
11. R. Mancini, *Single-Supply Op Amp Design Techniques*, Texas Instruments SLOA058, 2001 — mid-rail biasing and AC coupling of single-supply stages. (app note)
12. S. Franco, *Design with Operational Amplifiers and Analog Integrated Circuits*, 4th ed., McGraw-Hill 2015 — ch. 8 (noise gain, decompensated op-amps, noise-gain shaping, input-capacitance compensation). (textbook)
