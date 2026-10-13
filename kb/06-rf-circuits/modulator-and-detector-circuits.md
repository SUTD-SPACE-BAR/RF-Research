---
title: Modulator and detector circuits — varactor and reactance FM, PM modulators, balanced modulators and SSB, envelope and product detectors, synchronous AM, and FM discriminators (slope, Foster–Seeley, ratio, quadrature, PLL)
domain: 06-rf-circuits
slug: modulator-and-detector-circuits
tags: [modulator, fm-modulator, varactor, hyperabrupt, reactance-modulator, phase-modulator, armstrong, balanced-modulator, dsb-sc, ssb, filter-method, phasing-method, weaver, envelope-detector, diagonal-clipping, product-detector, bfo, synchronous-detection, foster-seeley, ratio-detector, quadrature-detector, slope-detector, pll-demodulator, discriminator, s-curve]
prerequisites:
  - ../10-comms-modulation/analog-modulation-am-fm-pm-ssb.md
  - ../05-analog-electronics/diodes-schottky-pin-varactor.md
  - mixers.md
  - detectors-and-power-meters.md
related:
  - vco-and-pll-synthesizers.md
  - transmitter-architectures.md
  - receiver-architectures.md
  - duplexers-diplexers-and-crystal-filters.md
  - ../14-sdr-dsp/software-demodulation.md
  - ../10-comms-modulation/synchronization-carrier-timing.md
  - ../01-circuit-theory/resonance-and-q.md
level: mixed
confidence: medium
last_updated: 2026-10-12
---

# Modulator and detector circuits

## Questions this page answers
- How does a varactor or a "reactance modulator" make FM, and how linear is it?
- How do I make phase modulation, and what is the difference from FM in hardware?
- What is a balanced modulator, and how do the filter and phasing methods turn DSB into SSB?
- How do I choose R and C for a diode envelope detector, and what is diagonal clipping?
- What is a product detector and a BFO, and why does SSB need one?
- Why does synchronous AM detection survive selective fading when an envelope detector doesn't?
- How do Foster–Seeley, ratio, quadrature and PLL FM detectors work, and which rejects AM?
- How do these analog circuits map onto the one-line DSP demodulators in an SDR?

## TL;DR
- **Varactor FM:** $K_v=df/dV$ comes from $C(V)=C_{j0}/(1+V/\varphi)^\gamma$ in the tank. At 433.92 MHz with an abrupt junction (γ = 0.5) plus fixed C, $K_v$ = 13 MHz/V, and a ±0.5 V tone gives ±6.5 MHz with **2.9 % modulation THD**. A hyperabrupt γ = 2 varactor *alone* makes f linear in V (0 % THD, simulated). Narrowband telemetry (±5 kHz) needs only millivolts, so linearity is rarely the limit; PLL loop bandwidth is ([transmitters](transmitter-architectures.md)).
- **Reactance modulator:** a transistor with an RC phase shifter looks like a capacitance $C_{eq}\approx(1+g_mR)\,C$ (ωRC ≪ 1). At 10.7 MHz with C = 2 pF and R = 100 Ω, $g_m$ = 5/20/50 mS gives 3/6/12 pF. The bias, and hence $g_m$, is the modulation input. Placed on an oscillator it gives FM; on a tuned amplifier it gives **PM**, $\Delta\varphi=\arctan(2Q\Delta f_0/f_0)\approx Q\,\Delta C/C$: Q = 20 and ΔC/C = 0.5 % gives 5.7°, linear to 1 %.
- **Balanced modulator → DSB-SC:** a baseband offset of δ (relative to the modulation peak) leaks a carrier $20\log(2\delta)$ below one sideband: 1 % → −34 dB. **Phasing SSB:** 1° of phase error → −41 dB unwanted sideband; 1 % gain error → −46 dB; 2 % with 2° → −34 dB (formula = simulation).
- **Envelope detector:** choose $1/f_c\ll RC\le\sqrt{1-\mu^2}/(\mu\omega_m)$. For μ = 0.8 at 3 kHz the limit is 39.8 µs. In ngspice (Schottky, 455 kHz) RC = 5/20/100 µs gave **0.5 / 1.1 / 15 % THD**; the last is diagonal clipping.
- **Product (coherent) detection** scales as cos θ with LO phase error θ (0.708 at 45°, simulated). Under **selective fading** that drops the carrier 10 dB, a μ = 0.7 AM signal comes out of an envelope detector with **60 % THD** and out of a synchronous detector with ≈ 0 %.
- **FM discriminators:**
  - The quadrature detector's S-curve is $\sin(\arctan(2Q\Delta f/f_0))$, linear within 5 % for $|2Q\Delta f/f_0|$ < 0.33 (confirmed by a time-domain limiter–tank–multiplier simulation).
  - Foster–Seeley gives an odd S-curve whose peaks sit at $2Q\Delta f/f_0$ ≈ ±1.06 (kQ = 1) but follows input AM 1:1.
  - The **ratio detector** output $(|A|-|B|)/(|A|+|B|)$ is amplitude-independent.
  - A **PLL** demodulator recovered exactly $\Delta f/K_v$ (0.501 V vs 0.500 V, THD < 0.01 %).

## Intuition (no math)
A *modulator* writes information onto a carrier by varying its amplitude, frequency or phase. A *detector* (demodulator) reads it back.
- **FM:** change a tuning element of the oscillator (a varactor, or a transistor made to look like a capacitor). The frequency follows the audio or data.
- **PM:** leave the oscillator alone and shift the phase of a later stage. A tuned amplifier whose resonance is nudged delays the carrier a little more or a little less.
- **AM and DSB:** multiply the carrier by the message. A balanced modulator is a multiplier arranged so that the carrier itself cancels (balance) and only the sidebands survive. Then remove one sideband with a sharp filter, or by the phasing trick (two DSB signals in quadrature that cancel one sideband), to get SSB.

On the receive side:
- **Envelope detector:** a diode charges a capacitor to the peaks of the RF and lets it discharge slowly through a resistor. Too fast a discharge leaves carrier ripple. Too slow, and the voltage cannot follow a falling envelope, so the output "clips diagonally".
- **Product detector:** multiplies the signal by a local carrier (a BFO). It is the only way to recover SSB or DSB, whose envelope is not the message, and it is also a better AM detector when the carrier fades.
- **FM detectors** turn frequency into amplitude. A tuned circuit's phase changes linearly with frequency near resonance. Quadrature and Foster–Seeley detectors measure that phase change; a ratio detector measures it in a way that ignores amplitude. A PLL simply makes its own oscillator follow the incoming frequency and reports the control voltage it needed.

## The math

### Level 1 — the transfer laws
- Varactor: $C(V)=C_{j0}(1+V/\varphi)^{-\gamma}$ (γ ≈ 0.5 abrupt, 0.33 graded, 1–2 hyperabrupt). Tank $f=1/(2\pi\sqrt{L(C_{fix}+C(V))})$, $K_v=df/dV$ ([diodes](../05-analog-electronics/diodes-schottky-pin-varactor.md)).
- FM: $s=A\cos(\omega_ct+2\pi K_v\int v_m\,dt)$; PM: $s=A\cos(\omega_ct+K_pv_m)$.
- DSB-SC: $s=m(t)\cos\omega_ct$. SSB (upper): $s=m\cos\omega_ct-\hat m\sin\omega_ct$, with $\hat m$ the Hilbert transform ([analog modulation](../10-comms-modulation/analog-modulation-am-fm-pm-ssb.md)).
- Envelope detector: $V_{out}\approx A_c[1+\mu m(t)]$ for $1/f_c\ll RC\le\sqrt{1-\mu^2}/(\mu\omega_m)$.
- Coherent detector: $\text{LPF}\{s(t)\cdot2\cos(\omega_ct+\theta)\}=m(t)\cos\theta$ for DSB.
- Discriminator: $V_{out}=K_d\,\Delta f$ near centre; $K_d$ in V/Hz.

### Level 2 — derivations
**(a) Varactor modulator linearity.** If the varactor is the only tank capacitance, $f\propto C^{-1/2}\propto(1+V/\varphi)^{\gamma/2}$, which is linear in V exactly when **γ = 2**. That is why hyperabrupt "tuning varactors" exist. With an abrupt junction (γ = 0.5) and fixed capacitance in parallel, f(V) is concave. Script §A (433.92 MHz, 4 V bias):
- abrupt (10 pF, 3 pF fixed): $K_v$ = 12.99 MHz/V, and ±0.5 V gives ±6.52 MHz with 2.88 % THD, mostly 2nd harmonic;
- hyperabrupt alone (γ = 2): $K_v$ = 92.3 MHz/V and essentially zero THD.

Distortion scales roughly with deviation, so a ±5 kHz FSK/NBFM deviation from a 13 MHz/V VCO (0.4 mV drive) is linear for all practical purposes. The real issues are $K_v$ drift with bias and temperature, and the PLL's suppression of modulation inside its bandwidth. Hence two-point modulation, or modulating the fractional-N divider, as LoRa/FSK chips do ([transmitter architectures](transmitter-architectures.md), [VCO & PLL](vco-and-pll-synthesizers.md)). A crystal oscillator pulled by a varactor (VXO) gives clean but small deviation, about ±(pullability) ppm, and is often frequency-multiplied afterwards. Multiplication by N also multiplies the deviation (and the phase noise, 20 log N; [multipliers](frequency-multipliers-dividers.md)).

**(b) Reactance modulator.** Connect a capacitor C from the tank node to a transistor's gate, and a resistor R from gate to ground. The branch current is $v/(R+1/j\omega C)$, the gate voltage is that current times R, and the drain current is $g_m$ times the gate voltage. The total admittance seen by the tank is
$$Y=\frac{1+g_mR}{R+1/(j\omega C)}\approx j\omega(1+g_mR)C\quad(\omega RC\ll1).$$
The circuit adds a capacitance proportional to $g_m$, plus a small conductance (the real part, 92–369 kΩ in §B). Modulating the bias modulates $g_m$, hence $C_{eq}$, hence frequency. Swapping R and C gives an inductive reactance. This is the classic valve and transistor FM modulator. Varactors replaced it, but the idea, an active device synthesising a variable reactance, lives on in active inductors and capacitance multipliers ([amplifier topologies](../05-analog-electronics/amplifier-topologies.md)).

**(c) Phase modulator.** A tuned amplifier stage of loaded Q has transfer phase $\varphi=-\arctan(2Q\,\delta)$ with $\delta=(f-f_0)/f_0$. Shift its resonance by $\Delta f_0=-f_0\Delta C/2C$ with a varactor or reactance modulator and the carrier's phase moves by $\Delta\varphi=\arctan(2Q\Delta f_0/f_0)\approx Q\Delta C/C$ rad. With Q = 20: 0.5 % → 5.7° (linear), 2 % → 21.8° (22.9° linear), 5 % → 45° (57° linear) (§B). PM modulators are therefore linear only to about ±0.5 rad. Armstrong's *indirect FM* integrates the audio first (so PM becomes FM) at a small index, then multiplies the frequency to reach the wanted deviation. A reactance modulator on an *amplifier* stage gives PM; on the *oscillator* it gives FM.

**(d) Balanced modulator and carrier suppression.** A diode-ring or Gilbert-cell mixer driven hard by the carrier multiplies the baseband by a ±1 square wave. The output is $\frac4\pi[m(t)\cos\omega_ct+\dots]$: DSB-SC plus odd harmonics that a band-pass removes ([mixers](mixers.md)). Any DC offset δ in the baseband path (diode mismatch, op-amp offset) adds $\frac4\pi\delta\cos\omega_ct$, a carrier leak. Relative to one sideband ($m$ of peak 1 gives sidebands of ½ each) the leak is $20\log(2\delta)$: −34 dB at 1 %, −44 dB at 0.3 % (§C). A carrier-null trimmer (balance pot) in old SSB rigs adjusted exactly this.

**(e) SSB generation.**
- *Filter method:* generate DSB at a fixed IF (e.g. 9 MHz) and remove the unwanted sideband with a crystal filter. For voice (300–3000 Hz) the two sidebands are only 600 Hz apart at their inner edges, so the filter needs a shape factor of about 1.5–2 for 50–60 dB rejection. That means 6–8 poles ([crystal filters](duplexers-diplexers-and-crystal-filters.md)).
- *Phasing method:* $I=m\cos\omega_ct$ and $Q=\hat m\sin\omega_ct$ subtracted. A gain ratio g and phase error φ between the two paths leave an unwanted sideband
$$\frac{P_{unwanted}}{P_{wanted}}=\frac{1+g^2-2g\cos\varphi}{1+g^2+2g\cos\varphi},$$
giving −41.2 dB at 1°, −46.1 dB at 1 % gain error, −34.0 dB at 2 % and 2° (formula = simulation, §C). This is the same expression as IQ-modulator sideband suppression ([transmitters](transmitter-architectures.md#level-2)). An SDR's DAC-based IQ path is a phasing modulator with digitally exact phase, so its suppression is set by analog mismatch after the DACs.
- *Weaver method:* two quadrature conversions with a low-pass filter between; no wideband 90° audio network is needed ([mixers](mixers.md)).

**(e′) AM modulators: high-level and low-level.**
- *High-level (collector/drain) modulation:* a saturated class-C/E PA's output amplitude is proportional to its supply, so modulate the supply: $V_{DD}(t)=V_0(1+\mu m(t))$. Output power goes as $V_{DD}^2$. Its average for a tone is $P_0(1+\mu^2/2)$, so the *modulator* (audio amplifier, transformer or switching supply) must deliver $\mu^2/2$ of the DC input power: 12.5 % at μ = 0.5 and 50 % at μ = 1 (§C). This is efficient, because the PA stays saturated. It is the ancestor of envelope tracking and EER ([PA linearisation](power-amplifiers.md#level-3--linearity-memory-and-system-level-techniques)).
- *Low-level modulation:* modulate a small stage (base/gate bias, a mixer or a DAC) and amplify linearly in class A/AB. It needs a linear PA, as SSB does.
- *Over-modulation* (μ > 1): the envelope folds through zero, an envelope detector distorts badly, and the spectrum widens (splatter). Use a limiter or ALC on the *audio* to cap μ ([PA control](pa-control-protection-and-sequencing.md)).

**(f) Envelope detector RC.** Between carrier peaks the capacitor discharges as $e^{-t/RC}$. Ripple at $f_c$ requires $RC\gg1/f_c$. Following the falling envelope $A_c(1+\mu\cos\omega_mt)$ requires the capacitor's discharge slope $V/RC$ to exceed the envelope slope at every instant:
$$\frac{1}{RC}\ge\frac{\mu\omega_m|\sin\omega_mt|}{1+\mu\cos\omega_mt}\ \ \forall t\quad\Rightarrow\quad RC\le\frac{\sqrt{1-\mu^2}}{\mu\,\omega_m}.$$
The maximum of the right-hand side occurs where $\cos\omega_mt=-\mu$. ngspice (Schottky detector, 455 kHz carrier, 3 kHz tone, μ = 0.8, limit 39.8 µs; §D):

| RC | recovered-tone THD | comment |
|---|---|---|
| 5 µs | 0.5 % | 2.3 carrier periods; ripple removed by the audio filter |
| 20 µs | 1.1 % | inside the limit |
| 100 µs | 15.2 % | diagonal clipping |

At low RF levels the diode works in its square-law region and the output follows the *square* of the envelope, adding 2nd-harmonic distortion ([detectors](detectors-and-power-meters.md)). Either bias the diode, keep the IF level high (as AGC does), or use a synchronous detector. The detector's AC load (the audio stage) must not be much smaller than its DC load R, or negative-peak clipping appears at high μ.

**(g) Product and synchronous detection.** Multiplying by $2\cos(\omega_ct+\theta)$ and low-pass filtering gives $m(t)\cos\theta$ for DSB: 1.000, 0.708 and 0.001 at θ = 0, 45° and 90° (§E). For SSB, a BFO frequency error Δf shifts every audio component by Δf (the voice "pitch" problem) while a phase error is inaudible ([analog modulation](../10-comms-modulation/analog-modulation-am-fm-pm-ssb.md#level-2--spectra-and-detection)). For AM, a carrier-recovery loop (PLL or Costas) supplies the LO; that is "synchronous AM". The advantage shows under *selective fading*. If multipath notches the carrier by 10 dB while the sidebands survive, the effective modulation index exceeds 1 and the envelope folds. In §E an envelope detector then produced 60 % THD, while the synchronous detector (locked to the weak but intact carrier phase) produced ≈ 0 %.

**(h) FM discriminators.**
- *Slope detector:* tune a resonant circuit off-centre so the input sits on its skirt. Amplitude then varies with frequency, and an envelope detector follows. It is simple, nonlinear and AM-sensitive.
- *Quadrature (coincidence) detector:* a small capacitor feeds a parallel tank resonant at $f_0$, producing a copy of the limited IF shifted by 90° plus the tank phase $\arctan(2Q\Delta f/f_0)$. Multiplying the copy with the original (an XOR or Gilbert cell) and low-pass filtering gives
$$V_{out}\propto\sin\!\big(\arctan(2Q\Delta f/f_0)\big),$$
linear within 5 % for $|2Q\Delta f/f_0|<0.33$. Choose $Q\le0.165\,f_0/\Delta f_{max}$: at a 10.7 MHz IF with ±75 kHz, Q ≤ 23. A time-domain simulation (limiter, Q = 20 tank, multiplier) gave a monotone odd S-curve within 0.06 of theory at ±75 kHz (§F).
- *Foster–Seeley:* a double-tuned transformer whose secondary voltage $V_2$ lags the primary by 90° at resonance, and by 90° ± arctan(x) off-resonance, $x=2Q\Delta f/f_0$. The centre-tapped secondary, with the primary injected at the tap, gives two diode voltages, $|V_1+V_2/2|$ and $|V_1-V_2/2|$. Their difference is an odd S-curve; for critical coupling (kQ = 1) its peaks are at x ≈ ±1.06 (§F). The output scales with input amplitude, so a limiter must precede it.
- *Ratio detector:* the same transformer, with one diode reversed and a large capacitor holding $|A|+|B|$ constant. The output is $(|A|-|B|)/(|A|+|B|)$, independent of input amplitude. A 20 % input AM changed the Foster–Seeley output by 20 % and the ratio-detector output by < 10⁻¹² (§F). It is the classic limiter-less broadcast FM detector.
- *PLL demodulator:* a loop locked to the incoming FM must drive its VCO with $v=\Delta f(t)/K_v$; that control voltage *is* the demodulated output. The loop bandwidth must exceed the highest modulation frequency (with a margin for phase error, keeping $|\theta_e|$ well below 90°) and the lock range must exceed the peak deviation. With $f_n$ ≈ 20 kHz, a ±5 kHz / 1 kHz tone gave 0.501 V against 0.500 V predicted (§F). Below the FM threshold a PLL extends performance by a few dB, compared with a discriminator, because its narrower noise bandwidth delays the onset of clicks ([analog modulation](../10-comms-modulation/analog-modulation-am-fm-pm-ssb.md#level-3--threshold-clicks-capture-and-limits-of-the-theory)).

**(i) Detectors in noise.**
- *Envelope detector:* above about 10 dB CNR the output SNR follows the AM figure of merit $\mu^2/(2+\mu^2)$ (−4.8 dB at μ = 1) ([analog modulation](../10-comms-modulation/analog-modulation-am-fm-pm-ssb.md)). Below it, the noise envelope dominates and the message is "captured" by noise, a threshold effect. A coherent (product) detector has no threshold: it stays linear in noise at any CNR, which is why weak-signal AM is best detected synchronously.
- *Discriminators:* FM detectors show the familiar FM threshold near 10 dB CNR in the Carson bandwidth. A PLL or an FM-feedback demodulator lowers it by a few dB, because the loop's noise bandwidth is narrower than Carson's.
- *Diode detectors at very low level:* in the square-law region the output SNR falls as the *square* of the input SNR, so pre-detection gain (an LNA) and narrow pre-detection filtering pay off disproportionately ([detectors](detectors-and-power-meters.md)).

### Level 3 — analog circuits vs SDR DSP
| Analog circuit | DSP equivalent ([software demodulation](../14-sdr-dsp/software-demodulation.md)) | What the DSP version removes |
|---|---|---|
| Envelope detector | $|I+jQ|$ | diagonal clipping, square-law distortion |
| Product detector + BFO | multiply by an NCO, take Re | BFO drift (still needs correct tuning) |
| Synchronous AM | PLL/Costas on IQ | (same principle) |
| Quadrature / Foster–Seeley / ratio | $\arg(r[n]r^*[n-1])$ | tank Q trade-off, alignment |
| PLL FM demodulator | digital PLL | analog VCO non-linearity |
| Balanced modulator | multiply baseband by the NCO in the DUC | carrier leak (only DAC/mixer offsets remain) |
| Phasing SSB | IQ DAC + quadrature modulator | the 90° audio network |

The analog circuits remain relevant in three places: in chips (quadrature detectors inside FM receiver ICs, varactor VCOs inside every PLL), in very low-power receivers (envelope detectors in wake-up receivers), and in exam questions.

### Level 3 — choosing a circuit
| Need | Modulator | Detector | Why |
|---|---|---|---|
| Narrowband FM/FSK telemetry, simple | varactor VCO in a PLL (two-point) | quadrature or PLL | integrated in every transceiver IC |
| Very clean, small deviation | VXO (crystal + varactor) ×N | PLL | crystal stability; deviation multiplied with N |
| Wideband FM audio | varactor VCO (hyperabrupt) | ratio or quadrature detector | linear f(V), AM rejection |
| AM, efficiency matters | high-level drain modulation | envelope (or synchronous under fading) | PA stays saturated |
| SSB voice | balanced modulator + crystal filter, or IQ/phasing in DSP | product detector + BFO | spectral efficiency, no carrier |
| OOK / ASK beacons, wake-up radios | keyed PA (ramped) | envelope detector (zero-bias Schottky) | microwatt receivers, simple |
| Phase-coherent data (PSK) | IQ modulator | coherent (Costas) | needed for BPSK/QPSK ([synchronisation](../10-comms-modulation/synchronization-carrier-timing.md)) |

## Design equations & rules of thumb

| Quantity | Equation | Typical numbers |
|---|---|---|
| Varactor $K_v$ | $df/dV$ from $C(V)$ in the tank | 433 MHz abrupt: 13 MHz/V |
| Linear FM from a varactor | γ = 2, varactor-only tank | hyperabrupt tuning diodes |
| Reactance modulator | $C_{eq}=(1+g_mR)C$ | 2 pF, 100 Ω, 20 mS: 6 pF |
| PM modulator | $\Delta\varphi\approx Q\Delta C/C$ (< 0.5 rad) | Q 20, 0.5 %: 5.7° |
| DSB carrier leak | $20\log(2\delta)$ re one sideband | 1 % offset: −34 dB |
| Phasing SSB | $\frac{1+g^2-2g\cos\varphi}{1+g^2+2g\cos\varphi}$ | 1°: −41 dB |
| Envelope RC | $1/f_c\ll RC\le\sqrt{1-\mu^2}/(\mu\omega_m)$ | μ 0.8, 3 kHz: ≤ 40 µs |
| Coherent detector | ∝ cos θ | 45°: −3 dB |
| Quadrature detector | $\sin(\arctan(2Q\Delta f/f_0))$; Q ≤ 0.165 f₀/Δf | 10.7 MHz, ±75 kHz: Q ≤ 23 |
| PLL demodulator | $v=\Delta f/K_v$; BW > f_m,max | 5 kHz/(10 kHz/V) = 0.5 V |

## Worked examples

### Example 1 — An FSK/NBFM transmitter from a 433 MHz VCO
Take a VCO with $K_v$ = 13 MHz/V (abrupt varactor, §A). For ±5 kHz deviation, the modulation input needs ±0.38 mV. Inside a PLL with a 50 kHz loop bandwidth, a 1.2 kb/s FSK waveform (fundamental 600 Hz) would be tracked out by the loop. Either inject at the reference/divider (two-point modulation) or make the loop narrower than the lowest modulation frequency. With data that has DC content (long runs of 1s), use two-point modulation or a fractional-N divider modulation, which is what SX126x-class chips do internally ([transmitters](transmitter-architectures.md)). Deviation calibration: the Bessel-null method ([analog modulation Ex. 3](../10-comms-modulation/analog-modulation-am-fm-pm-ssb.md#example-3--calibrating-deviation-with-the-first-carrier-null)).

### Example 2 — Envelope detector for an AM airband/beacon receiver at a 455 kHz IF
Audio up to 3 kHz, modulation up to μ = 0.8:
- **RC window:** $RC\le\sqrt{1-0.64}/(0.8\cdot2\pi\cdot3000)$ = 39.8 µs and RC ≫ 2.2 µs.
- **Choose:** RC = 20 µs (R = 10 kΩ, C = 2 nF), then a 3 kHz audio low-pass. ngspice gives 1.1 % THD (§D).
- **Bias:** keep the IF level at the detector ≥ about 0.5 V peak (AGC) so a Schottky stays out of its square-law region. A 1–10 µA forward bias also helps at low levels ([detectors](detectors-and-power-meters.md)).
- **AGC tap:** the detector's DC component is a natural AGC voltage ([AGC](agc-loops-and-receiver-gain-control.md)).

### Example 3 — An analog SSB exciter, filter vs phasing
*Filter method:* a 9 MHz balanced modulator (SBL-1-class diode ring), carrier balance to −40 dB (δ ≈ 0.5 %), then an 8-pole crystal ladder of 2.4 kHz with SF ≈ 1.8. The unwanted sideband is suppressed by > 60 dB, limited by the filter's stopband at the inner edge.

*Phasing method:* matching the audio and RF quadrature networks to 1 % and 1° gives about 40 dB. That is the classic reason the filter method dominated analog SSB, while software IQ generation (phasing done digitally) dominates now.

### Example 4 — Choosing an FM detector for a 10.7 MHz IF
For ±75 kHz broadcast FM with a quadrature detector, Q ≤ 23 keeps the S-curve linear to 5 %. With an IC limiter (≈ 60 dB of gain), the quadrature detector is the economical choice. Without a hard limiter, use a ratio detector. For narrowband ±5 kHz telemetry at 455 kHz: $Q\le0.165\times455/5$ ≈ 15, so a ceramic discriminator resonator (or a PLL) gives a steep, linear S-curve. For the lowest threshold, use a PLL demodulator with a loop bandwidth just above the data rate.

### Example 5 — Why an analog AM receiver distorts at dusk on shortwave
Ionospheric multipath creates frequency-selective fades a few hundred Hz wide that sweep through the signal. When a fade sits on the carrier (−10 dB) the envelope detector sees μ_eff ≈ 2.2 and distorts heavily: 60 % THD in §E. "Exalted carrier" or synchronous detection, which regenerates a strong local carrier phase-locked to the weak received one, removes the distortion. Modern SDR "SAM" modes do exactly this.

### Example 6 — An OOK beacon receiver with a bare diode detector
A 433.92 MHz OOK recovery beacon could be received with a zero-bias Schottky detector straight after an LNA and SAW. The detector's tangential sensitivity is about −55 to −60 dBm ([detectors](detectors-and-power-meters.md#level-2--derivations)). Even with a 20 dB LNA that is only about −80 dBm at the antenna, roughly 50 dB worse than a superhet or LoRa receiver, because the detector's noise is video noise across its whole bandwidth, not kTB in a narrow channel. Use it only for short-range direction finding near the landing site, where its simplicity and instant response help. Use a narrowband receiver (SDR + matched filter) for range.

### Example 7 — Bench recipes
- **Measure the AM depth:** feed the modulated carrier to a scope in XY mode (modulating audio on X, RF envelope on Y) to get the trapezoid, then $\mu=(A-B)/(A+B)$ from its long (A) and short (B) sides. On a spectrum analyser, each sideband sits at $20\log(\mu/2)$ dBc ([analog modulation](../10-comms-modulation/analog-modulation-am-fm-pm-ssb.md#practical-notes)).
- **Measure $K_v$ of a modulator:** step the DC bias by ±10 mV and read the frequency on a counter. Repeat across the bias range to map its non-linearity.
- **Trace a discriminator S-curve:** sweep a CW generator ±2× the expected deviation through the IF and record the DC output. The slope at centre is $K_d$ (V/Hz); the linear span sets the maximum deviation.
- **Check SSB suppression:** transmit a single audio tone and read the wanted sideband, opposite sideband and carrier on a spectrum analyser. Expect > 40 dB (phasing) or > 60 dB (filter) on the opposite sideband.

## Practical notes
- **Varactor modulators:** decouple the bias line with a resistor large enough not to load the tank (its noise becomes FM; see [07 tuning-line noise](../07-noise-linearity/phase-noise-and-jitter.md#level-3--plls-systems-and-measurement-subtleties)). Use anti-series varactor pairs to reduce RF-induced capacitance changes (AM–PM; [ISF page](oscillator-phase-noise-ltv-isf.md#am-to-pm-conversion-varactor-tanks)).
- **Balanced modulators:** carrier balance drifts with temperature. For > 40 dB, use a trimmer or a DC-servo on the baseband offset. A diode ring needs about +7 dBm LO drive (level 7) for its rated balance ([mixers](mixers.md)).
- **Envelope detectors:** keep the leads short and put an RF bypass on the output (part of C). Watch the detector's AC load: a following stage with low input impedance reduces the effective R and causes negative-peak clipping.
- **Discriminator alignment:** sweep the IF (generator or SDR tracking source) and scope the output to trace the S-curve. Set the zero crossing at the IF centre and check symmetry. A ratio detector's large capacitor must have a time constant of about 0.1–0.2 s to hold the amplitude reference.
- **PLL demodulators:** check the lock range against the maximum deviation *plus* the frequency offset (Doppler and crystal error on a rocket can be ±1–2 kHz at 433 MHz).

- **Relevance to the Space Bar radios:**
  - LoRa and FSK modules modulate digitally (fractional-N PLL modulation) and demodulate in DSP, so none of these circuits appear on the board.
  - They do appear in test gear: the SDR's demodulators, an FM handheld used as a field receiver, an OOK beacon.
  - They appear in custom designs: a 433 MHz FSK link with a discrete VCO, or an AM/FM beacon for recovery.
  - The design rules above (Kv linearity, RC limits, S-curve range vs deviation plus Doppler) are what to check.
- **Doppler and FM detectors:** a rocket's ±1–2 kHz Doppler at 433 MHz appears as a DC offset at an FM discriminator's output. AC-coupled audio ignores it, but data slicers need AFC or DC-free coding, and the offset uses up S-curve range ([LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)).

## Common mistakes & misconceptions
- *"PM and FM need different oscillators."* PM is FM with a differentiated message, and vice versa; the hardware difference is only *where* the reactance is modulated (amplifier vs oscillator).
- *"A bigger detector capacitor is always smoother."* Beyond $\sqrt{1-\mu^2}/(\mu\omega_m)$ it causes diagonal clipping.
- *"Envelope detection works for SSB with a strong carrier added."* Only if the reinserted carrier is far larger than the sideband; otherwise the output distorts. Use a product detector.
- *"Foster–Seeley rejects AM."* Only with a limiter in front; the ratio detector rejects AM by construction.
- *"Higher Q makes a better quadrature detector."* Higher Q raises sensitivity but shrinks the linear range ($|2Q\Delta f/f_0|$ < 0.33 for 5 %).
- *"A PLL demodulator works with any loop bandwidth."* Too narrow a bandwidth tracks the modulation incompletely (distortion, loss of lock); too wide lets in noise.
- *"Over-modulating AM just makes it louder."* At μ > 1 the envelope folds, the detector output distorts, and the spectrum splatters into adjacent channels.
- *"Carrier suppression in DSB is perfect."* Offsets as small as 1 % leave a carrier only 34 dB down.

- *"The ratio detector needs no limiter, so the IF gain doesn't matter."* Its AM rejection holds only while the stabilising capacitor's voltage is steady; fast AM (impulse noise, fast fading) still leaks through.
- *"A slope detector is a cheap FM detector."* It works, but it is nonlinear, AM-sensitive and has a poor threshold; use it for receiving NBFM on an AM-only receiver in an emergency.
- *"Indirect (Armstrong) FM needs no frequency multiplication."* The PM stage is linear only to ±0.5 rad, so reaching useful deviation requires ×N multiplication, which multiplies phase noise too.
- *"DSB-SC can be detected with a free-running BFO like SSB."* DSB needs phase coherence (cos θ). A free-running BFO produces a beating, fading output, while SSB tolerates a small frequency error.

## How to simulate / verify
- `python3 tools/verify/rf2_moddet.py` (≈ 2 s, ngspice; ALL PASS) covers: §A varactor f(V), $K_v$ and THD for γ = 0.5 vs 2; §B reactance-modulator admittance and PM modulator; §C DSB carrier leak and phasing-SSB suppression; §D ngspice envelope detector with three RC values; §E coherent detection vs phase error and selective-fading AM; §F quadrature-detector S-curve (analytic and time-domain), Foster–Seeley and ratio S-curves and AM rejection, PLL demodulator.
- GNU Radio: *Frequency Mod*, *AM Demod*, *Quadrature Demod*, *PLL Freq Det* blocks reproduce the same behaviours on recorded IQ ([14 software demodulation](../14-sdr-dsp/software-demodulation.md)).

- For a deeper check, re-run §D with a real detector diode's SPICE model (e.g. the HSMS-285x parameters in [detectors](detectors-and-power-meters.md)) and with the AC load of the following audio stage connected. Negative-peak clipping then appears for low AC/DC load ratios.
- The quadrature-detector check uses an idealised 90° coupling (Hilbert transform). A circuit-level version (series coupling capacitor into the tank, XOR multiplier) can be built in ngspice with behavioural sources.
- Use the same script pattern to test any discriminator design: sweep a constant-envelope tone across the IF and read the DC output to get the S-curve.

## Open questions / gaps
- Classic discriminator design texts (Clarke & Hess; Krauss, Bostian & Raab) were not re-read this session; the derivations here are standard and re-done numerically.
- The Foster–Seeley model is the idealised phasor form (lossless transformer, ideal envelope diodes); diode drops and loading flatten its peaks.
- Practical ceramic discriminator resonator data (455 kHz, 10.7 MHz) were not gathered.
- The PLL demodulator's threshold-extension benefit is stated qualitatively, not simulated against a discriminator in noise.
- The envelope-detector threshold and the square-law SNR penalty are stated from theory, not simulated here.
- Commercial reactance-modulator and VXO deviation figures (ppm of pullability per volt) were not gathered for specific crystals.
- Synchronous-AM performance with a *noisy* recovered carrier (carrier loop bandwidth vs fading rate) is not analysed; §E uses an ideal carrier reference.
- No measured data on the team's hardware; all results are simulations.

## Sources
1. H. L. Krauss, C. W. Bostian, F. H. Raab, *Solid State Radio Engineering*, Wiley, 1980 (modulators, AM/FM detectors, discriminators). (textbook; cited, not re-read)
2. K. K. Clarke, D. T. Hess, *Communication Circuits: Analysis and Design*, Addison-Wesley, 1971 (envelope detector, diagonal clipping, FM discriminators, PLL demodulation). (textbook; cited)
3. S. Haykin, M. Moher, *Communication Systems*, 5th ed., Wiley, 2009 (DSB/SSB generation, coherent detection, envelope-detector RC condition). (textbook; cited)
4. B. Razavi, *RF Microelectronics*, 2nd ed., 2011, ch. 3–4 (modulation, IQ/phasing, sideband suppression). (textbook; cited)
5. ARRL, *The ARRL Handbook*, modulation and receiver chapters (balanced modulators, product detectors, reactance modulators, ratio/quadrature detectors). (handbook; background)
6. W. Hayward, R. Campbell, B. Larkin, *Experimental Methods in RF Design*, ARRL, 2003 (product detectors, SSB generation in practice). (handbook; cited)
7. E. H. Armstrong, "A method of reducing disturbances in radio signaling by a system of frequency modulation," *Proc. IRE* 24(5), 689–740, 1936 (indirect FM). (peer-reviewed; classic)
8. `tools/verify/rf2_moddet.py` (this KB).
