---
title: Oscillators — Barkhausen and negative resistance, Colpitts/Clapp/Hartley/Pierce/crystal/VCO, start-up and amplitude, phase-noise basics, ring and relaxation
domain: 05-analog-electronics
slug: oscillators
tags: [oscillator, barkhausen, negative-resistance, colpitts, clapp, hartley, pierce, crystal-oscillator, load-capacitance, gm-crit, gain-margin, drive-level, pulling, vco, varactor, leeson, phase-noise, wien-bridge, ring-oscillator, relaxation-oscillator, describing-function, cross-coupled-vco, lc-vco, tuning-range, capacitor-bank, quadrature-vco, qvco]
prerequisites:
  - feedback-and-stability.md
  - bjt-fundamentals-small-signal.md
  - diodes-schottky-pin-varactor.md
  - ../01-circuit-theory/resonance-and-q.md
related:
  - ../04-real-components-hf/crystals-and-resonators.md
  - ../07-noise-linearity/phase-noise-and-jitter.md
  - ../06-rf-circuits/vco-and-pll-synthesizers.md
  - ../15-lora-ism-radios/semtech-chip-family.md
  - data-converters-adc-dac.md
  - power-supplies-for-rf-and-analog.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Oscillators — Barkhausen and negative resistance, Colpitts/Clapp/Hartley/Pierce/crystal/VCO, start-up and amplitude, phase-noise basics, ring and relaxation

## Questions this page answers
- What really makes a circuit oscillate, and why is "loop gain = 1 at 0°" not the whole story?
- How do I view an oscillator as a negative resistance cancelling a resonator's loss?
- How do Colpitts, Clapp, Hartley and Pierce oscillators work, and what sets their frequency?
- How do I pick the load capacitors for a crystal, and how much will a wrong value pull my LoRa radio's frequency?
- What is $g_{m,crit}$ and gain margin for a crystal oscillator, and why do some crystal circuits fail to start in the cold?
- What limits the amplitude of an oscillator, and how big does it get?
- What is Leeson's model and why does resonator Q dominate phase noise?
- How do VCOs, ring oscillators and RC relaxation oscillators differ?
- How does a cross-coupled LC VCO start, what sets its amplitude, and how much tail current does it need?
- How wide can a varactor VCO tune, and why do synthesiser chips use switched capacitor banks?
- How does a quadrature VCO produce I and Q, and how accurate is its 90°?

## TL;DR
- **Barkhausen:** a steady oscillation at $f_0$ needs loop gain $T(j\omega_0) = 1\angle0°$. For *start-up* you need $|T| > 1$ (closed-loop poles in the right half-plane); a nonlinearity then reduces the effective gain until $|T| = 1$ exactly. Barkhausen is a steady-state condition, not a stability criterion.
- **Negative resistance:** a resonator with loss $R_{loss}$ oscillates when the active circuit presents $R_{neg}$ with $|R_{neg}| > R_{loss}$; design for 3–5× margin. A transistor with capacitors $C_1$ (b–e) and $C_2$ (e–ground) presents $Z = 1/j\omega C_1 + 1/j\omega C_2 - g_m/(\omega^2C_1C_2)$ — exact for an ideal $g_m$ device (`tools/verify/analog_oscillators.py` §1).
- **Colpitts:** $f_0 = 1/\left(2\pi\sqrt{LC_1C_2/(C_1+C_2)}\right)$; a BJT Colpitts in ngspice ran at 8.752 MHz vs 8.765 MHz hand (§6). **Clapp** adds a small series C to swamp transistor capacitances (better stability). **Hartley** uses a tapped inductor.
- **Pierce crystal oscillator** (MCU/radio XTAL pins): choose $C_1 = C_2 = 2(C_L - C_{stray})$ (14 pF for $C_L$ = 10 pF with 3 pF stray). Start-up: $g_m > g_{m,crit} = 4\,ESR\,\omega^2(C_0+C_L)^2$ with **gain margin ≥ 5** (ST AN2867) [1]; 0.86 mA/V for a 32 MHz, 40 Ω, $C_0$ 1.5 pF, $C_L$ 10 pF crystal (§2).
- **Pulling:** $\Delta f/f = -C_m/[2(C_0+C_L)^2]$ per farad of load change → ≈ 19 ppm/pF for that crystal: 1 pF of layout error = 17 kHz at 915 MHz, 14 % of a 125 kHz LoRa channel (§2). This is why LoRa radios often use TCXOs.
- **Amplitude:** a BJT's large-signal transconductance falls as $G_m/g_m = 2I_1(x)/[xI_0(x)]$ ($x = V_1/V_T$); with a start-up margin of 3 the base-emitter swing settles near 140 mV peak, with 5 near 244 mV (§3). Big margins mean hard limiting and harmonics.
- **Leeson:** $\mathcal L(\Delta f) = 10\log\left[\frac{FkT_0}{2P_s}\left(1+\left(\frac{f_0}{2Q_L\Delta f}\right)^2\right)\left(1+\frac{f_c}{\Delta f}\right)\right]$, with $P_s$ the carrier power at the sustaining-amplifier input and $\mathcal L = S_\varphi/2$ (white floor −177 dBc/Hz for F = 1, 0 dBm). A 433 MHz LC VCO with $Q_L$ = 20, 0 dBm, F = 2: −133 dBc/Hz at 100 kHz; doubling $Q_L$ gains 6 dB. A 32 MHz crystal ($Q_L$ = 50 000): −160.5 dBc/Hz at 1 kHz (§4). Multiplying a reference by N adds $20\log N$ (+29 dB from 32 → 915 MHz).
- **Cross-coupled LC VCO** (the on-chip workhorse): the pair presents $-2/g_m$ differentially, so it starts when $g_mR_p>1$ ($R_p$ = per-side tank resistance). In the current-limited regime the differential amplitude is $(4/\pi)I_TR_p$. ngspice at 433 MHz ($R_p$ = 408 Ω): threshold 150 µA, and 1.03 V at 2 mA against 1.04 V predicted (`tools/verify/s4_vco.py`). Tuning range is $\sqrt{C_{max}/C_{min}}$ of the *total* tank C: fixed C dilutes it (1.29 → 1.125 in the example). Capacitor banks cut $K_{VCO}$ by about $2^N$.
- **Wien bridge:** needs amplifier gain exactly 3; poles cross the jω axis at K = 3 (§5) — amplitude control (lamp, diode, JFET, AGC) is mandatory.

## Intuition (no math)
An oscillator is a resonator that loses a little energy each cycle, plus an amplifier that tops it up at the right moment. A swing (the resonator) left alone decays; a child pumping at the right phase keeps it going. If the pumping adds more than is lost, the amplitude grows — until something limits it (the child can only push so hard; the transistor runs out of current or voltage). The frequency is set almost entirely by the resonator, *if* it is a high-Q resonator: then small changes in the amplifier's phase barely move the frequency. That is why crystal oscillators (Q of 10⁴–10⁶) are so much more stable and quiet than LC (Q of 10–100) or RC oscillators (effective Q of ~1).

Two equivalent ways to see it: (1) a feedback loop whose gain around the loop is exactly one with zero phase at one frequency (Barkhausen); (2) a resonator connected to a circuit with *negative resistance* — a circuit that returns energy — which cancels the resonator's loss. The second view is often easier at RF, where "the loop" is hard to identify.

Noise: the amplifier adds a little random noise each cycle. The resonator filters it — within its bandwidth $f_0/2Q$ the noise is converted to random phase wander, which grows the closer you look to the carrier. Higher Q, higher signal power and a quieter amplifier all reduce this phase noise.

## The math

### Level 1 — conditions and frequencies

**Barkhausen condition:** $T(j\omega_0) = a(j\omega_0)\beta(j\omega_0) = 1$, i.e. $|T| = 1$ and $\angle T = 0°$ (or 360°·n). Start-up requires $|T(j\omega_0)| > 1$ in small signal.

**Negative-resistance condition** (series resonator with loss $R_{loss}$, active port $Z_a = R_a + jX_a$): $R_a + R_{loss} < 0$ for start-up, $X_a + X_{res} = 0$ sets frequency; in steady state $R_a(A) = -R_{loss}$ at amplitude A.

**Oscillator frequencies**

| Type | Frequency | Feedback / notes |
|---|---|---|
| Colpitts | $1/(2\pi\sqrt{L\,C_1C_2/(C_1+C_2)})$ | capacitive divider; $n = C_1/(C_1+C_2)$ |
| Clapp | $≈ 1/(2\pi\sqrt{LC_3})$ when $C_3 \ll C_1, C_2$ | series $C_3$ with L swamps device C |
| Hartley | $1/(2\pi\sqrt{(L_1+L_2+2M)C})$ | tapped inductor |
| Pierce (crystal) | crystal at load resonance with $C_L$ | inverter + $C_1$, $C_2$ |
| Wien bridge | $1/(2\pi RC)$ | needs gain = 3 |
| Phase-shift (3 RC) | $1/(2\pi\sqrt6RC)$ | needs gain = 29 |
| Ring (N inverters, odd) | $1/(2Nt_d)$ | $t_d$ = stage delay |
| RC relaxation (Schmitt) | $\propto 1/RC$ | e.g. 555: $1.44/[(R_A+2R_B)C]$ |

**Crystal load capacitance:** $C_L = \dfrac{C_1C_2}{C_1+C_2} + C_{stray}$ → $C_1 = C_2 = 2(C_L - C_{stray})$, $C_{stray}$ typically 2–5 pF (pins + traces).

**Critical transconductance and gain margin** [1]: $g_{m,crit} = 4\,ESR\,(2\pi f)^2(C_0+C_L)^2$; gain margin $= g_m/g_{m,crit} \ge 5$.

**Drive level:** $DL = I_{rms}^2\,ESR$ with $I_{rms} \approx 2\pi f(C_0+C_L)V_{rms}$ across the crystal [1].

### Level 2 — derivations

**Colpitts negative resistance.** Put a transconductor $g_m$ (collector at AC ground) with $C_1$ from base to emitter and $C_2$ from emitter to ground. Drive the base with test current $I_t$. KCL at the emitter: $j\omega C_1v_{be} + g_mv_{be} = j\omega C_2v_e$; at the base: $I_t = j\omega C_1v_{be}$; and $v_b = v_{be} + v_e$. Eliminating:
$$Z_{in} = \frac{v_b}{I_t} = \frac{1}{j\omega C_1} + \frac{1}{j\omega C_2} - \frac{g_m}{\omega^2C_1C_2}.$$
The capacitive part is $C_1$ in series with $C_2$ (which resonates with the tank L), and the real part is negative. Script §1 confirms it to all digits (e.g. 20 mS, 100 pF, 100 pF at 50 MHz: −20.3 − j63.7 Ω). This is the same mechanism that makes emitter followers oscillate with capacitive loads (→ [feedback & stability](feedback-and-stability.md)). Start-up requires $g_m/(\omega^2C_1C_2) > R_{loss}$ (the tank's series loss, including the device's $r_\pi$, $r_b$ and $R_E$ contributions).

**Pierce crystal oscillator ↔ $g_{m,crit}$.** The Pierce is the same circuit viewed from the crystal: the inverter (transconductance $g_m$) with $C_1$ at its input and $C_2$ at its output presents $-g_m/(\omega^2C_1C_2)$ in series with $C_1C_2/(C_1+C_2)$. Near its parallel (load) resonance the crystal (motional $R_m = ESR$, $L_m$, $C_m$ in parallel with $C_0$) behaves as an inductance with an effective series resistance $ESR(1+C_0/C_L)^2$. With $C_1 = C_2 = 2C_L$: $|R_{neg}| = g_m/(4\omega^2C_L^2)$, and $|R_{neg}| > ESR(1+C_0/C_L)^2$ gives
$$g_m > 4\,ESR\,\omega^2(C_0+C_L)^2 = g_{m,crit},$$
the ST formula [1] (script §2 checks both forms agree). Consequences: large $C_L$ or $C_0$ and high ESR make start-up hard ($\propto (C_0+C_L)^2$); a crystal marginal at room temperature fails at −40 °C when ESR rises and inverter $g_m$ falls. Demand gain margin ≥ 5 using *maximum* ESR.

**Load resonance and pulling.** With load $C_L$ the crystal oscillates where its reactance cancels $C_L$:
$$f_L = f_s\left(1 + \frac{C_m}{2(C_0+C_L)}\right),\qquad \frac{1}{f}\frac{df_L}{dC_L} = -\frac{C_m}{2(C_0+C_L)^2}.$$
For $C_m$ = 5 fF, $C_0$ = 1.5 pF, $C_L$ = 10 pF: $f_L$ is 217 ppm above series resonance, with sensitivity −18.9 ppm/pF (script §2). Crystal makers specify frequency *at* the stated $C_L$; a board with the wrong $C_1$, $C_2$ or unaccounted stray capacitance is off by ~10–20 ppm per pF. (Crystal physics in depth → [crystals & resonators](../04-real-components-hf/crystals-and-resonators.md).)

**Amplitude limiting (describing function).** Drive a BJT's base-emitter with $V_1\cos\omega t$ around a bias set by a current source. The collector current becomes $I_C e^{x\cos\omega t}/I_0(x)$ (the bias self-adjusts so the average stays $I_C$), whose fundamental is $2I_C I_1(x)/I_0(x)$, so the large-signal transconductance is
$$\frac{G_m(x)}{g_m} = \frac{2I_1(x)}{x\,I_0(x)},\qquad x = \frac{V_1}{V_T}$$
[2]. Oscillation settles where $G_m(x)$ has fallen to $g_{m,crit}$, i.e. $G_m/g_m = 1/\text{margin}$: margin 2 → $x$ = 3.3 (86 mV peak); 3 → 5.4 (140 mV); 5 → 9.5 (244 mV); 10 → 19.5 (504 mV) (script §3). At large x the collector current is a train of narrow pulses (class-C-like): rich in harmonics, and the device spends part of the cycle cut off. More margin gives reliable start-up but more harmonics, more AM-to-PM conversion and sometimes squegging (bias-network relaxation). Amplitude control (AGC, ALC) or a limiting stage that is outside the resonator improves phase noise.

**Wien bridge.** The RC network has $\beta(s) = sRC/[(sRC)^2 + 3sRC + 1]$, equal to 1/3 at $\omega = 1/RC$ with zero phase. With a non-inverting gain K the closed-loop poles are roots of $(sRC)^2 + (3-K)sRC + 1$: in the LHP for K < 3, on the jω axis at K = 3, in the RHP for K > 3 (script §5). Exactly-3 cannot be held by resistors alone, so a gain element that decreases with amplitude (thermistor/lamp, diodes, JFET with a rectifier-driven gate) is part of every practical Wien oscillator.

**Leeson's model (phase noise).** The amplifier adds white noise of one-sided density $FkT_0$ to a carrier of power $P_s$ at its input. Half of that additive noise is in phase quadrature, and $\mathcal L$ counts one sideband ($\mathcal L \equiv S_\varphi/2$), so the white phase floor is $FkT_0/(2P_s)$, with $P_s$ the carrier power at the amplifier input (Rubiola Eq. 1.39: $S_\varphi = FkT_0/P_s$) [3, 9]. Lee & Hajimiri write $2FkT/P_{sig}$ with $P_{sig}$ the power dissipated in the tank resistance, which is 6 dB higher by definition (open-circuit tank noise $4kTR$ versus matched available noise $kT$), not a contradiction [10]. Inside the resonator's half-bandwidth $f_0/(2Q_L)$ the feedback loop turns additive noise into phase fluctuations with a $1/\Delta f^2$ skirt; flicker noise up-conversion adds a $1/\Delta f^3$ region below the corner $f_c$:
$$\mathcal L(\Delta f) = 10\log_{10}\left[\frac{FkT_0}{2P_s}\left(1+\left(\frac{f_0}{2Q_L\Delta f}\right)^2\right)\left(1+\frac{f_c}{\Delta f}\right)\right]\ \text{dBc/Hz}$$
[3, 9]. Examples (§4, $T_0$ = 290 K): 433 MHz LC VCO ($Q_L$ = 20, $P_s$ = 0 dBm, F = 2, $f_c$ = 10 kHz): −110 dBc/Hz at 10 kHz, −133 at 100 kHz, −153 at 1 MHz, white floor −174; with $Q_L$ = 40: −116/−139/−159 (6 dB better). 32 MHz crystal ($Q_L$ = 5×10⁴, −10 dBm, $f_c$ = 1 kHz): −160.5 dBc/Hz at 1 kHz, flattening to −164 (verified by `tools/verify/fix_leeson_prefactor.py`, which also checks the floor by Monte Carlo). Leeson is an empirical/linear model — F and $f_c$ are fitted, not predicted; Hajimiri–Lee's impulse-sensitivity model explains the up-conversion mechanisms. Theory and measurement → [phase noise & jitter](../07-noise-linearity/phase-noise-and-jitter.md). In a PLL, the reference's phase noise is multiplied by N inside the loop bandwidth (+20 log N; +29 dB from 32 MHz to 915 MHz) (→ [VCO & PLL](../06-rf-circuits/vco-and-pll-synthesizers.md)).

### Level 3 — practical physics and limits
- **Frequency stability** = resonator stability + (amplifier phase change)/(resonator phase slope). The phase slope $d\phi/d\omega = 2Q/\omega_0$, so a phase disturbance Δφ shifts frequency by $\Delta f/f_0 = \Delta\phi/(2Q)$: 1° of amplifier phase drift moves an LC oscillator (Q = 50) by 175 ppm but a crystal (Q = 50 000) by 0.17 ppm.
- **Supply pushing and load pulling:** supply changes alter device capacitances (pushing, Hz/V); load changes reflect into the tank (pulling). Buffer the oscillator, regulate its supply with a low-noise LDO (→ [power supplies](power-supplies-for-rf-and-analog.md)), and remember that supply noise × pushing becomes FM noise/spurs.
- **VCOs:** varactor-tuned LC tanks (→ [diodes](diodes-schottky-pin-varactor.md) for C–V laws and tuning range). $K_{VCO}$ (Hz/V) × tuning-line noise (V/√Hz) gives frequency noise $K_{VCO}v_n$ (Hz/√Hz) and, for small modulation index, $\mathcal L(\Delta f) \approx 20\log_{10}[K_{VCO}v_n/(\sqrt2\,\Delta f)]$: a 10 MHz/V VCO with 10 nV/√Hz on its tuning line gives 0.1 Hz/√Hz → −103 dBc/Hz at 10 kHz from that alone (script §7). Keep $K_{VCO}$ just large enough for the tuning range.
- **Overtone crystals:** above ~30–50 MHz crystals run on 3rd/5th mechanical overtones; the oscillator needs an LC trap so it cannot start on the fundamental.
- **Ring oscillators:** no resonator (Q ≈ 1) → poor phase noise, but tiny and wide-tuning; inside CMOS PLLs and ADC clocks. **Relaxation oscillators** (RC + comparator, 555, MCU RC oscillators) are cheap and accurate to ~1 % after trimming; jitter is set by comparator noise at the threshold crossing.
- **MEMS and ceramic resonators:** ceramic resonators (Q ~ 1000, ±0.5 %) are fine for MCUs without USB/radio needs; MEMS oscillators replace crystals where shock/vibration robustness matters — relevant for rockets (crystals show acceleration sensitivity ~1 ppb/g; see 04).

### Level 3 — cross-coupled LC VCOs: start-up, amplitude, tuning range, capacitor banks and quadrature
*(G-05-07. Phase-noise theory, ISF and tail-noise up-conversion are on [phase noise & jitter](../07-noise-linearity/phase-noise-and-jitter.md) and [VCO & PLL](../06-rf-circuits/vco-and-pll-synthesizers.md); this section covers the circuit.)*

**Topology.** Two transistors M1 and M2 share a tail current $I_T$. Each drain has a tank ($L$, $C$, loss $R_p$ to the supply), and each gate is driven by the *other* drain. This is the oscillator in almost every integrated synthesiser, SX126x/SX127x-class transceivers included (their internal VCO architecture is not published; a cross-coupled LC VCO is the norm, from knowledge).

**Negative resistance (Level 1–2).** Apply a differential test voltage $v_d=v_1-v_2$. Device currents $g_mv_{gs}$ with $v_{gs1}=v_2$ and $v_{gs2}=v_1$ give $i_1-i_2=-g_mv_d$. The port current is $(i_1-i_2)/2$, so
$$Z_d=-\frac{2}{g_m}.$$
The differential tank is $2R_p$ (two halves in series), so start-up needs $2/g_m<2R_p$, i.e. **$g_mR_p>1$**; design for 2–3×. With $g_m=\sqrt{2\beta I_T/2}$ (square-law MOS at balance) this is a minimum tail current. Example (`s4_vco.py` §1–2): $L$ = 10 nH and $C$ = 13.5 pF per side, Q = 15 → $f_0$ = 433.2 MHz, $R_p$ = 408 Ω, $g_{m,crit}$ = 2.45 mS. With β = 40 mA/V² the critical tail current is **150 µA**. In ngspice (level-1 NMOS, 0.02 V kick) 100 µA decays, 160 µA grows slowly, and the circuit runs at 432.9–433.1 MHz against 433.2 MHz by hand.

**Amplitude.** Well above threshold the pair switches fully, so the tail current is steered alternately into each side. The differential current is a ±$I_T$ square wave whose fundamental is $(4/\pi)I_T$, and each side converts it with $R_p$:
$$V_{d,pk}\approx\frac{4}{\pi}I_TR_p\quad(\text{current-limited regime}).$$
ngspice: 0.509 V at 1 mA and 1.029 V at 2 mA, against 0.520 and 1.040 V predicted. Near threshold (160–300 µA) the amplitude is set instead by $g_m$ compression and falls below the formula. Past the point where the swing pushes the devices into triode or the tail source out of saturation ("voltage-limited regime"), extra current only adds noise. The best phase noise sits at the edge between the two regimes (Hajimiri–Lee [11]).

**Tuning range.** With a varactor $C_v(V)$ in parallel with fixed capacitance $C_{fix}$ (devices, wiring, inductor self-C, fixed caps):
$$\frac{f_{max}}{f_{min}}=\sqrt{\frac{C_{fix}+C_{v,max}}{C_{fix}+C_{v,min}}}.$$
§3 uses junction varactors ($C_{J0}$ = 10 pF, $V_J$ = 0.7 V, M = 0.5) with $C_{fix}$ = 8 pF per side. Over $V_r$ = 0.2–1.8 V the analytic prediction is 388.1–436.5 MHz and ngspice gives 387.5–436.2 MHz (agreement within 0.6 MHz). The varactor alone has a 1.29 frequency ratio, but the fixed capacitance cuts it to **1.125**. Keep $C_{fix}$ small, use abrupt or hyperabrupt varactors ([diodes](diodes-schottky-pin-varactor.md)), and do not let the swing forward-bias the varactor near $V_r$ ≈ 0, which is lossy and nonlinear.

**Switched capacitor banks.** A wide range from varactors alone needs a huge $K_{VCO}$ (MHz/V), and tuning-line noise times $K_{VCO}$ is FM noise (above). Instead, split the tank C into an N-bit binary bank of switched units (coarse, digital, selected by the synthesiser's band calibration) plus a small varactor (fine, analogue). Each of the $2^N$ bands overlaps its neighbour by ~30 %. Example (§4): covering 3.4–4.0 GHz (÷4 → 850–1000 MHz, ÷8 → 425–500 MHz, a common way to serve 433/868/915 MHz from one VCO) needs $C_{max}/C_{min}$ = 1.38. With one band, $K_{VCO}$ ≈ 780 MHz/V over 1 V; a 4-bit bank brings it to ≈ 49 MHz/V. The cost is switch loss and parasitics. An "on" unit has $Q=1/(\omega R_{on}C_u)$ (22 for 100 fF and 20 Ω at 3.7 GHz). An "off" unit still shows its switch's $C_{off}$ in series. Because $R_{on}C_{off}$ is a fixed technology figure of merit (0.5 ps assumed), widening the switch for Q shrinks the on/off ratio: 40 Ω gives 9:1 at Q 11, and 10 Ω gives 3:1 at Q 43. Bank design is this trade, plus overlap margin for process spread.

**Quadrature VCOs.** Image-reject and zero-IF receivers need I and Q LOs. Three common sources: (a) run the VCO at 2f and divide by 2 with a master–slave flip-flop (quadrature set by duty-cycle accuracy; very common in transceivers); (b) a polyphase RC filter after the VCO (lossy, narrowband); (c) the **quadrature VCO (QVCO)**, two identical cross-coupled VCOs that inject into each other, one in phase and one inverted, through coupling devices of strength $m=G_c/G_p$ [12]. The coupling current is in quadrature with each tank's own voltage, so each tank must supply a phase shift φ with $\tan\varphi=m$. That forces both to run *off* resonance by
$$\frac{\Delta\omega}{\omega_0}=\frac{m}{2Q},$$
with outputs exactly 90° apart when the tanks match. The ODE model in §5 (Q = 10, van der Pol devices) gives an offset of 0.0094 (m = 0.2) and 0.0196 (m = 0.4), against 0.010 and 0.020 predicted, and 90.00°. Two costs follow:
- **Phase-noise penalty.** Operating off the tank peak reduces the phase slope by $\cos^2\varphi=1/(1+m^2)$, about 0.3–1.3 dB of Leeson penalty for m = 0.2–0.4 from the tank alone; the coupling devices add their own noise.
- **Quadrature error from tank mismatch.** In the model, the error grows linearly with the fractional mismatch δ and inversely with m. It runs 2–4× the naive $Q\delta/m$ (the factor rises with start-up margin): for m = 0.4 and δ = 0.1 %, 3.3° at margin 2 and 5.7° at margin 3. Weak coupling (m = 0.2) loses lock, or flips to the −90° mode, by δ ≈ 0.2–0.5 %. Real QVCOs therefore use m ≈ 0.3–0.5, carefully matched layout, and often a calibration. Divide-by-2 is preferred when the extra VCO frequency is affordable. The amplitude-and-phase error analysis is in Mazzanti–Svelto–Andreani [13]; our numbers are from the simplified model, so treat them as trends (medium confidence).

## Design equations & rules of thumb

| Quantity | Equation | Typical |
|---|---|---|
| Start-up | $|T| > 1$ small-signal; $|R_{neg}| > R_{loss}$ | margin 3–5 (LC), ≥ 5 (crystal) |
| Colpitts $R_{neg}$ | $-g_m/(\omega^2C_1C_2)$ | — |
| Crystal $C_L$ | $C_1C_2/(C_1+C_2) + C_{stray}$ | stray 2–5 pF |
| Load caps | $C_1 = C_2 = 2(C_L - C_{stray})$ | 14 pF for 10 pF $C_L$ |
| $g_{m,crit}$ | $4\,ESR\,\omega^2(C_0+C_L)^2$ | < 1 mA/V at 32 MHz |
| Gain margin | $g_m/g_{m,crit} \ge 5$ | use max ESR [1] |
| Pulling | $-C_m/[2(C_0+C_L)^2]$ | 10–25 ppm/pF |
| Drive level | $I_{rms}^2 ESR$ | ≤ datasheet max (often 10–300 µW) |
| BJT $G_m$ | $2I_1(x)/[xI_0(x)]$ | x ≈ 5 at margin 3 |
| Frequency sensitivity to phase | $\Delta f/f = \Delta\phi/(2Q)$ | Q dominates stability |
| Leeson | see above | −6 dB per 2× $Q_L$ or 2× $P_s$ |
| PLL multiplication | $+20\log_{10}N$ | +29 dB, 32→915 MHz |
| Wien gain | exactly 3 (with AGC) | — |
| Ring oscillator | $1/(2Nt_d)$ | — |
| Cross-coupled start-up | $g_mR_p>1$ ($Z_d=-2/g_m$) | 433 MHz, $R_p$ 408 Ω: 2.45 mS |
| Cross-coupled amplitude | $V_{d,pk}\approx(4/\pi)I_TR_p$ | 2 mA, 408 Ω: 1.04 V |
| VCO tuning ratio | $\sqrt{(C_{fix}+C_{v,max})/(C_{fix}+C_{v,min})}$ | fixed C dilutes range |
| Cap-bank $K_{VCO}$ | ≈ (band width × overlap)/($2^N$ × V range) | 4 bits: 780 → 49 MHz/V |
| QVCO offset | $\Delta\omega/\omega_0=m/(2Q)$ | m 0.4, Q 10: 2 % |

## Worked examples

### 1. Load capacitors for a 32 MHz crystal on a LoRa transceiver board
Crystal: 32 MHz, $C_L$ = 10 pF, ESR ≤ 40 Ω, $C_0$ ≈ 1.5 pF, $C_m$ ≈ 5 fF (representative values; check your crystal's datasheet). Estimate stray = 3 pF → $C_1 = C_2$ = 14 pF (use 15 pF, or 12 pF if the IC's pins are known to add more). Critical $g_m$: 0.86 mA/V → with an oscillator $g_m$ of 5 mA/V the margin is 5.8 (OK); at 1 mA/V it would be 1.2 (fails cold). Pulling: 19 ppm/pF → a 1 pF mistake costs 17 kHz at 915 MHz. Many Semtech SX126x designs use a 32 MHz TCXO instead (± 1–2 ppm over temperature), because a crystal's ±10–20 ppm tolerance plus temperature drift is a large fraction of a narrow LoRa channel at high spreading factors (→ [Semtech chip family](../15-lora-ism-radios/semtech-chip-family.md)).
Note: several radio ICs (SX126x among them) integrate trimmable load capacitors on the XTAL pins — then external capacitors may be unnecessary; follow the reference design.

### 2. A 10 MHz Colpitts test oscillator
L = 2.2 µH, $C_1$ = 220 pF, $C_2$ = 470 pF: hand $f_0$ = 8.765 MHz; ngspice (common-base BJT, 1 mA) 8.752 MHz (§6). Loop gain ≈ $g_mRn(1-n)$ = 88 with R = 10 kΩ, n = 0.32 — so the amplitude is set by hard limiting (≈ 20 V p-p on the collector, above the 9 V rail thanks to the inductor). For a cleaner sine, reduce the loop gain to ~3–5 (lower R, lower current or a smaller n) or add amplitude control.

### 3. How much does resonator Q buy?
433 MHz oscillator, 1 mW, F = 2: at 100 kHz offset, $Q_L$ = 20 → −133 dBc/Hz; $Q_L$ = 40 → −139 dBc/Hz (Leeson with $FkT_0/2P_s$). With a SAW resonator ($Q_L$ ~ 1000s), close-in noise drops by another ~30 dB — which is why SAW-stabilised 433 MHz transmitters exist. For a PLL synthesiser, the loop suppresses VCO noise inside the loop bandwidth and replaces it with 20 log N × reference noise.

### 4. A discrete-style 433 MHz cross-coupled VCO budget
$L$ = 10 nH (Q 15) per side gives $R_p$ = 408 Ω, so you need $g_m$ > 2.45 mS. Choose $I_T$ = 1 mA (×6.7 above the 150 µA threshold in the MOS model) for ≈ 0.5 V differential, (4/π)·1 mA·408 Ω. For ±25 MHz of tuning around 412 MHz, an 8 pF fixed + 5.3–8.8 pF varactor tank gives 388–436 MHz (ngspice 387.5–436.2 MHz). $K_{VCO}$ ≈ 30 MHz/V over 1.6 V, so 10 nV/√Hz on the tuning line contributes ≈ −93 dBc/Hz at 10 kHz ($20\log[K_{VCO}v_n/(\sqrt2\Delta f)]$). That is why the tuning line is filtered hard and the range kept no wider than needed. In practice at 433 MHz a discrete builder uses a ready-made PLL/VCO chip or the transceiver's internal synthesiser; this budget is how to judge one.

## Practical notes
- **Crystal layout:** crystal and load caps next to the IC pins, ground guard around them, no digital traces underneath; the load caps' ground return straight to the IC's ground. Every pF of trace matters (pulling above).
- **Measure without loading:** a 10 pF scope probe on a crystal pin pulls the frequency by ~100 ppm and can stop oscillation. Measure the buffered clock output, or use a 1 pF active probe or a near-field loop into a spectrum analyser.
- **Start-up time** of crystal oscillators is ms (energy builds at a rate set by the Q); radio ICs specify it — relevant to duty-cycled LoRa nodes and to flight-computer boot timing.
- **Vibration:** crystal oscillators have acceleration sensitivity (Γ, typically ~10⁻⁹/g); on a rocket, vibration at f_v appears as phase-noise sidebands at ±f_v and boost acceleration shifts the frequency. For telemetry this is usually negligible vs the LoRa tolerance; for coherent/radar systems it is not (→ [crystals](../04-real-components-hf/crystals-and-resonators.md)).
- **Supply:** power oscillators and VCOs from their own filtered rail; switching-regulator ripple appears as spurs at $f_0 \pm f_{sw}$ (→ [power supplies](power-supplies-for-rf-and-analog.md)).
- **Tank form vs Leeson form of the noise prefactor** (why some sources write 2FkT/P with P the tank dissipation) is explained in [06 oscillator phase noise (ISF)](../06-rf-circuits/oscillator-phase-noise-ltv-isf.md#level-2--derivations).

## Common mistakes & misconceptions
- **"Barkhausen says |T| = 1, so design for loop gain 1."** Then it never starts. Design small-signal $|T|$ (or $|R_{neg}|/R_{loss}$) of 3–5 and let the nonlinearity settle it.
- **Choosing crystal caps equal to $C_L$.** The two capacitors are in series: $C_1 = C_2 ≈ 2(C_L - C_{stray})$.
- **Ignoring $g_{m,crit}$ and ESR at cold temperature** — marginal oscillators fail in the field (or on a cold launch pad).
- **Over-driving a crystal** (high drive level) — frequency shift, ageing, even fracture of small crystals; many MCU datasheets let you select drive strength.
- **Probing a crystal pin with a scope probe** and concluding the oscillator is faulty (or fine).
- **Using an RC/relaxation or ring oscillator where phase noise matters** (ADC clocks, LO references).
- **Making $K_{VCO}$ larger than needed** — every nV/√Hz on the tuning line becomes FM noise. Use a capacitor bank for range and a small varactor for fine tuning.
- **"Tuning range = varactor ratio."** Only the *total* tank capacitance counts: √((C_fix + C_vmax)/(C_fix + C_vmin)). 8 pF of fixed C turns a 1.29 varactor range into 1.125.
- **"More tail current always lowers phase noise."** Only in the current-limited regime; once the swing saturates (voltage-limited) the amplitude stops growing and noise rises.
- **"A QVCO's outputs are exactly 90° apart."** Only for matched tanks. A 0.1 % tank mismatch gives several degrees at m = 0.4, and weak coupling can lose lock or flip to the −90° mode.

## How to simulate / verify
- **Python:** `tools/verify/analog_oscillators.py` — exact vs formula Colpitts negative resistance; crystal $C_L$, $g_{m,crit}$ (two equivalent derivations), gain margin, pulling ppm/pF and kHz at 433/868/915 MHz, drive level; BJT describing function and settled amplitudes vs margin; Leeson curves ($FkT_0/2P_s$); Wien-bridge poles vs gain; ngspice Colpitts transient. `tools/verify/fix_leeson_prefactor.py` — Monte Carlo proof that additive white noise gives $S_\varphi = N_0/P_s$ and $\mathcal L = N_0/(2P_s)$ (AM and PM get equal halves), and the corrected examples.
- **ngspice Colpitts** (runs via `tools/verify/analog_ngspice.py`):
```spice
* common-base Colpitts oscillator ~10 MHz (tank L1 with C1-C2 divider, feedback to emitter)
.model QC NPN(IS=1e-15 BF=200 VAF=50 TF=0.3n CJE=3p CJC=2p)
VCC vcc 0 DC 9 PULSE(0 9 0 1u)
L1 vcc c 2.2u
C1 c e 220p
C2 e 0 470p
RE e vee 2.2k
VEE vee 0 DC -3
Q1 c b e QC
RB b 0 100
CB b 0 100n
RL c vcc 10k
.tran 1n 60u 50u 1n
.end
```
  The supply ramp (PULSE) provides the start-up kick; in real circuits noise does. For crystal oscillators, simulate with the crystal's BVD model ($R_m$, $L_m$, $C_m$ ∥ $C_0$) — start-up takes thousands of cycles, so use `.option` with a coarse step or reduce Q temporarily, or do a small-signal negative-resistance analysis (`.ac` of the active port impedance).
- **Python + ngspice:** `tools/verify/s4_vco.py` (output `s4_vco_output.txt`, ≈ 45 s) — cross-coupled −2/g_m and g_mR_p > 1; ngspice NMOS 433 MHz oscillator start-up threshold, amplitude vs (4/π)I_TR_p and frequency; ngspice varactor tuning vs analytic; capacitor-bank K_VCO and switch Q / on-off trade; QVCO ODE: offset m/(2Q), 90° mode, phase error vs mismatch and lock loss.
- **Bench:** frequency counter on a buffered output (ppm error vs $C_L$); spectrum analyser for harmonics and spurs; phase-noise with a spectrum analyser (dBc/Hz, RBW-corrected) or an SDR-based method (→ [phase-noise measurement](../17-test-measurement/phase-noise-measurement.md)).

## Open questions / gaps
- Crystal motional parameters used ($C_m$ = 5 fF, $C_0$ = 1.5 pF, ESR 40 Ω) are representative of 32 MHz fundamental crystals, not taken from a specific datasheet — check a real part (e.g. the crystal in a Semtech reference design).
- Hajimiri–Lee ISF phase-noise theory is referenced, not derived; belongs with 07.
- Corrected 2026-10-02 (W5-E9, D6 #1): this page previously used $2FkT/P_s$ with a "both sidebands" argument, which made every Leeson example 6 dB too noisy. $\mathcal L$ is single-sideband by definition and only the quadrature half of the additive noise is phase noise, so Leeson's prefactor is $FkT_0/(2P_s)$ ($P_s$ at the amplifier input). Lee–Hajimiri's $2FkT/P_{sig}$ is the same physics with $P_{sig}$ = tank power. Still missing: a worked mapping of one definition onto the other for a concrete Colpitts with known tank R.
- The VCO tuning-line noise formula is stated loosely; the careful narrowband-FM derivation is in [phase noise & jitter](../07-noise-linearity/phase-noise-and-jitter.md).

## Sources
1. STMicroelectronics, *AN2867: Oscillator design guide for STM8AF/AL/S, STM32 MCUs and MPUs*, Rev 24, 2026. https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm8afals-stm32-mcus-and-mpus-stmicroelectronics.pdf — Pierce oscillator, $C_L$ and load capacitors, $g_{m,crit} = 4\,ESR(2\pi F)^2(C_0+C_L)^2$, gain margin ≥ 5, drive level $I_{rms}^2ESR$. (app note; formulas via search excerpts)
2. P. R. Gray, P. J. Hurst, S. H. Lewis, R. G. Meyer, *Analysis and Design of Analog Integrated Circuits*, 5th ed., Wiley 2009 — large-signal transconductance of the BJT (Bessel-function describing function), oscillator amplitude. Also K. K. Clarke, D. T. Hess, *Communication Circuits: Analysis and Design*, Addison-Wesley 1971 (origin of the Bessel $G_m$ treatment). (textbook)
3. D. B. Leeson, "A simple model of feedback oscillator noise spectrum," *Proc. IEEE* 54(2), 329–330, 1966. (peer-reviewed)
4. A. Hajimiri, T. H. Lee, "A general theory of phase noise in electrical oscillators," *IEEE J. Solid-State Circuits* 33(2), 179–194, 1998. (peer-reviewed)
5. T. H. Lee, *The Design of CMOS Radio-Frequency Integrated Circuits*, 2nd ed., Cambridge 2004 — ch. 17–18 (oscillators, negative resistance, Colpitts/Clapp, phase noise). (textbook)
6. W. Hayward, R. Campbell, B. Larkin, *Experimental Methods in RF Design*, ARRL 2003 — ch. 4 (practical LC and crystal oscillators, amplitude limiting, measurement). (textbook)
7. P. Horowitz, W. Hill, *The Art of Electronics*, 3rd ed., Cambridge 2015 — ch. 7 (oscillators and timers: Wien bridge, relaxation, 555, crystal oscillators). (textbook)
8. B. Razavi, *RF Microelectronics*, 2nd ed., Prentice Hall 2011 — ch. 8 (oscillators, cross-coupled and Colpitts, VCO tuning, phase noise). (textbook)
9. E. Rubiola, "The Leeson effect — Phase noise in quasilinear oscillators," arXiv:physics/0502143, 2005 — Eq. 1.4 ($\mathcal L = S_\varphi/2$), Eq. 1.26 (Leeson filtering), Eq. 1.39 ($b_0 = FkT_0/P_0$, $P_0$ at the sustaining-amplifier input). https://arxiv.org/abs/physics/0502143 (peer-reviewed author's monograph draft; as read by W4-D6)
10. T. H. Lee, A. Hajimiri, "Oscillator phase noise: a tutorial," *IEEE J. Solid-State Circuits* 35(3), 326–336, 2000 — modified Leeson form with $2FkT/P_{sig}$, $P_{sig}$ = power dissipated in the tank. (peer-reviewed)
11. A. Hajimiri, T. H. Lee, "Design issues in CMOS differential LC oscillators," *IEEE J. Solid-State Circuits* 34(5), 717–724, 1999 — current- vs voltage-limited regimes, amplitude (4/π)I_T R, tail-noise effects. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge, amplitude law reproduced in ngspice)
12. A. Rofougaran, J. Rael, M. Rofougaran, A. Abidi, "A 900 MHz CMOS LC-oscillator with quadrature outputs," *ISSCC Dig. Tech. Papers*, 1996, pp. 392–393; P. Andreani, A. Bonfanti, L. Romanò, C. Samori, "Analysis and design of a 1.8-GHz CMOS LC quadrature VCO," *IEEE JSSC* 37(12), 1737–1747, 2002. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
13. A. Mazzanti, F. Svelto, P. Andreani, "On the amplitude and phase errors of quadrature LC-tank CMOS oscillators," *IEEE JSSC* 41(6), 1305–1313, 2006. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge — trends reproduced by the ODE model, not its exact formulas)
