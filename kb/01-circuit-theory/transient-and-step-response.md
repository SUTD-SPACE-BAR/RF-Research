---
title: Transient and step response (RC, RL, RLC)
domain: 01-circuit-theory
slug: transient-and-step-response
tags: [transient, step-response, time-constant, rise-time, bandwidth, damping-ratio, overshoot, ringing, rlc, settling-time, probe-ground-lead]
prerequisites:
  - lumped-elements-impedance-admittance.md
  - resonance-and-q.md
  - ../00-math-foundations/differential-equations-circuits-waves.md
  - ../00-math-foundations/laplace-transfer-functions-bode.md
related:
  - energy-storage-and-reactive-power.md
  - passive-filter-design-prototypes.md
  - ../03-transmission-lines-matching/time-domain-reflectometry.md
  - ../17-test-measurement/oscilloscopes-and-probing-for-rf.md
  - ../13-pcb-rf-layout-emc/power-distribution-decoupling-for-rf.md
  - ../04-real-components-hf/ferrites-and-beads.md
  - ../05-analog-electronics/feedback-and-stability.md
level: intro
confidence: high
last_updated: 2026-10-13
---

# Transient and step response (RC, RL, RLC)

## Questions this page answers
- What is a time constant and how long does an RC or RL circuit take to settle?
- Where does the "rise time × bandwidth ≈ 0.35" rule come from, and when is it 0.4 or 0.45?
- What do damping ratio ζ and Q have to do with overshoot and ringing?
- Why does my scope show ringing at ~100 MHz on every fast edge?
- Why does a decoupling capacitor ring when the load current steps?
- How long does a narrowband filter or resonator take to respond to a burst (e.g. a LoRa or radar pulse)?
- How do rise times of cascaded stages combine?
- What is the difference between the time-domain view and the frequency-domain view of the same circuit?

## TL;DR
- First-order (RC or RL): $\tau=RC$ or $L/R$; step response $1-e^{-t/\tau}$; **10–90 % rise time $t_r=\tau\ln9=2.197\tau$**; 1 % settling $4.6\tau$, 0.1 % in $6.9\tau$.
- $f_{3dB}=1/(2\pi\tau)$ ⇒ **$t_r\cdot f_{3dB}=\ln9/2\pi=0.350$**. The product is 0.34–0.35 for Gaussian-like responses (single pole, Bessel, Gaussian) and rises to 0.37–0.41 for Butterworth N = 3–5 (sharper roll-off ⇒ slower edge with overshoot). Oscilloscopes with flat responses quote ≈0.4–0.45.
- Second-order (series RLC): $\omega_0=1/\sqrt{LC}$, **$\zeta=\dfrac{R}{2}\sqrt{\dfrac CL}=\dfrac{1}{2Q}$**. Underdamped ($\zeta<1$) step overshoot $=\exp(-\pi\zeta/\sqrt{1-\zeta^2})$: 85 % at ζ = 0.05, 53 % at 0.2, 16 % at 0.5, 4.3 % at 0.707, none at ≥ 1. Ringing at $\omega_d=\omega_0\sqrt{1-\zeta^2}$, envelope decays with $\tau_{env}=2L/R=2Q/\omega_0$.
- **Damping needs $R$ comparable to $\sqrt{L/C}$** (the characteristic impedance). 150 nH of scope ground lead with 12 pF of probe capacitance has $\sqrt{L/C}=112\ \Omega$ and rings at **119 MHz** with 49 % overshoot from a 50 Ω source; a 5 nH spring ground moves it to 650 MHz and overdamps it.
- Rise times of cascaded stages add roughly in quadrature, $t_{r,tot}\approx\sqrt{\sum t_{r,i}^2}$ (within ≈10 % for RC chains; exact for Gaussians).
- A resonator/filter of loaded Q takes ≈ $Q_L/\pi$ cycles to build up or decay by $1/e$ in amplitude: a 915 MHz stage with $Q_L=30$ has a 10.4 ns envelope time constant.

## Intuition (no math)
A capacitor charging through a resistor is like filling a bucket through a hose whose flow slows as the bucket fills: fast at first, then ever more slowly, never quite finishing. The **time constant** is how long it would take at the initial rate; after about five time constants it is within 1 %. An inductor is the mirror image: it resists changes in current, so current creeps up to its final value with the same exponential shape.

Put an inductor and a capacitor together and energy can slosh back and forth, so a sudden step makes the circuit **ring** at its natural frequency, the ringing dying away as the resistance burns energy. The **damping ratio** ζ says how quickly: small ζ (high Q) means many cycles of ringing; ζ ≈ 0.7 gives a crisp edge with a few percent overshoot; ζ ≥ 1 gives no overshoot but a slower rise. Whether a circuit rings is decided by comparing its resistance with $\sqrt{L/C}$ — the impedance at which the inductor and capacitor "trade" energy.

The time and frequency views are the same information. A circuit that cuts off sharply above some frequency cannot reproduce a sharp edge (edges contain high frequencies), so it rounds and delays the edge; if its cutoff is very steep it also overshoots and rings (the Gibbs phenomenon). That is why a Butterworth or Chebyshev filter rings on a pulse while a Bessel filter doesn't.

## The math

### Level 1 — first-order circuits
For a series RC driven by a step $V_s$ at $t=0$ (capacitor initially at $v_0$):
$$v_C(t)=V_s+(v_0-V_s)e^{-t/\tau},\qquad\tau=RC.$$
For an RL circuit the current follows the same law with $\tau=L/R$. 10 % is reached at $t=\tau\ln(10/9)$, 90 % at $\tau\ln10$, so $t_r=\tau\ln9=2.197\tau$. The frequency response $H=1/(1+j\omega\tau)$ has $f_{3dB}=1/(2\pi\tau)$, so
$$t_r\,f_{3dB}=\frac{\ln9}{2\pi}=0.3497.$$

### Level 2 — second-order (RLC) circuits
Series RLC with the output across C, driven by a voltage step. KVL gives
$$LC\ddot v_C+RC\dot v_C+v_C=V_s\quad\Longleftrightarrow\quad H(s)=\frac{\omega_0^2}{s^2+2\zeta\omega_0s+\omega_0^2},$$
with $\omega_0=1/\sqrt{LC}$, $\zeta=\dfrac{R}{2}\sqrt{C/L}$ and $Q=1/(2\zeta)=\omega_0L/R$ (the same Q as on [resonance and Q](resonance-and-q.md)). Poles at $s=-\zeta\omega_0\pm j\omega_0\sqrt{1-\zeta^2}$.
- **Underdamped** ($\zeta<1$): $v_C(t)/V_s=1-\dfrac{e^{-\zeta\omega_0t}}{\sqrt{1-\zeta^2}}\sin(\omega_dt+\phi)$, $\omega_d=\omega_0\sqrt{1-\zeta^2}$, $\cos\phi=\zeta$. Peak overshoot $M_p=e^{-\pi\zeta/\sqrt{1-\zeta^2}}$ at $t_p=\pi/\omega_d$.
- **Critically damped** ($\zeta=1$): $1-(1+\omega_0t)e^{-\omega_0t}$; fastest rise without overshoot ($t_r=3.36/\omega_0$).
- **Overdamped** ($\zeta>1$): two real poles; slow.
Overshoot values computed by step simulation match the formula to <0.05 % (`tools/verify/circuits_transient.py` §2): 85.4 % (ζ = 0.05), 52.7 % (0.2), 16.3 % (0.5), 4.33 % (0.707).

The envelope $e^{-\zeta\omega_0t}=e^{-t/(2L/R)}$ decays with time constant $2L/R=2Q/\omega_0$; in cycles of the ringing, the amplitude falls by $1/e$ in $Q/\pi$ cycles. A rough count: the number of visible ring cycles ≈ Q.

The **parallel** RLC (e.g. a tank driven by a current step, or a supply node with a decoupling capacitor) is the dual: $\zeta=\dfrac{1}{2R_p}\sqrt{L/C}$, so *large* parallel resistance means *low* damping.

### Level 3 — general systems, bandwidth rules and limits
- **Rise-time × bandwidth for other responses** (script §3): single pole 0.350; two identical poles 0.344; Butterworth N = 2/3/4/5: 0.342/0.365/0.387/0.408 with 4.3/8.2/10.8/12.8 % overshoot; Bessel N = 2–5 (3-dB-normalised): 0.342–0.351 with < 1 % overshoot; Gaussian 0.340. So **0.35 is right for well-behaved (Gaussian-like) systems**; sharp-cutoff systems are slower and ring. Keysight quotes ~0.35 for Gaussian-response scopes and ~0.4–0.45 for maximally-flat ones.
- **Cascades.** For Gaussian responses rise times add exactly in quadrature; for chains of real poles the rule underestimates slightly (−7.5 % for two equal RC stages, −9.8 % for three). The practical use: a scope + probe of rise times $t_{r,s}$ and $t_{r,p}$ measuring a signal of rise time $t_{r,x}$ displays $\sqrt{t_{r,x}^2+t_{r,s}^2+t_{r,p}^2}$; to measure within 5 % you need instrument rise time ≲ 1/3 of the signal's.
- **Band-pass transients.** A narrowband filter is equivalent to a low-pass filter acting on the envelope (complex baseband). Its envelope rise time is set by the bandwidth: $t_r\approx0.35\cdot2/\Delta f_{3dB}$ ≈ $0.7/\Delta f$ (factor 2 because a band-pass of width Δf corresponds to a low-pass of width Δf/2). A single resonator's envelope time constant is $2Q_L/\omega_0=1/(\pi\Delta f)$. For pulsed radar or FSK the filter bandwidth must be ≳ 1/(pulse length) to avoid smearing ([pulsed radar](../11-radar/pulsed-radar-and-pulse-compression.md)).
- **Distributed effects.** When the edge's spatial extent $t_r\cdot v$ is comparable to the interconnect length, the lumped RLC picture gives way to transmission-line reflections (TDR, ringing from impedance steps). A rough criterion: treat as a transmission line if the interconnect delay exceeds ~1/6 of the rise time ([TDR](../03-transmission-lines-matching/time-domain-reflectometry.md)).
- **Nonlinear transients** (diode recovery, PA turn-on, ferrite saturation) need time-domain SPICE rather than these formulas.

## Design equations & rules of thumb

| Quantity | Equation | Typical |
|---|---|---|
| RC / RL time constant | $\tau=RC$, $L/R$ | 10 kΩ × 100 nF = 1 ms |
| Rise time (10–90 %) | $2.197\tau$ | — |
| Rise-time–bandwidth | $t_r\approx0.35/f_{3dB}$ (0.4–0.45 for flat-response scopes) | 100 MHz scope → 3.5 ns |
| Settling | 1 %: 4.6τ; 0.1 %: 6.9τ; 0.01 %: 9.2τ | ADC drivers |
| Damping ratio (series) | $\zeta=\frac R2\sqrt{C/L}=1/2Q$ | — |
| Damping ratio (parallel) | $\zeta=\frac{1}{2R_p}\sqrt{L/C}$ | — |
| Overshoot | $e^{-\pi\zeta/\sqrt{1-\zeta^2}}$ | ζ = 0.707 → 4.3 % |
| Ring frequency | $f_d=f_0\sqrt{1-\zeta^2}$ | — |
| Envelope decay | $\tau_{env}=2L/R=2Q/\omega_0$ | — |
| Cascade | $t_r\approx\sqrt{\sum t_{r,i}^2}$ | ±10 % |
| Band-pass envelope | $t_r\approx0.7/\Delta f_{3dB}$ | 125 kHz LoRa BW → ≈5.6 µs |

## Worked examples

### 1. Why your scope rings at ~120 MHz
A standard 10× probe with a 15 cm ground clip: loop inductance ≈150 nH (order of magnitude; roughly 1 nH per mm of loop), probe tip capacitance ≈12 pF. $f_0=1/(2\pi\sqrt{150\,\text{nH}\cdot12\,\text{pF}})=118.6$ MHz, $\sqrt{L/C}=112\ \Omega$. Driven from a 50 Ω source, ζ = 50/(2·112) = 0.22 → **49 % overshoot** and ringing at ~119 MHz that is *not in the circuit*. Replace the clip with a spring ground tip (≈5 nH): $f_0=650$ MHz and ζ = 1.22 — no overshoot within the scope's bandwidth. ([Oscilloscopes and probing](../17-test-measurement/oscilloscopes-and-probing-for-rf.md).)

### 2. A bulk decoupling capacitor at the end of a long supply trace
20 nH of wiring/trace to a 10 µF MLCC with 5 mΩ ESR: $f_0=356$ kHz, $\sqrt{L/C}=44.7$ mΩ, ζ = 0.056 (Q ≈ 9). A load step — e.g. a LoRa PA keying on at 2 W and drawing ~1 A — excites a 356 kHz ring with ~84 % overshoot of the voltage dip, which can reset an MCU or modulate the PA. Adding ≈45 mΩ of *damping* resistance (a polymer or tantalum bulk capacitor's ESR, or a small series resistor on a second bulk capacitor) brings ζ to ≈0.56. This is the same physics as the ferrite-bead + capacitor resonance ([ferrites and beads](../04-real-components-hf/ferrites-and-beads.md), [PDN for RF](../13-pcb-rf-layout-emc/power-distribution-decoupling-for-rf.md)).

### 3. Settling of an ADC anti-alias RC
1 kΩ and 1 nF (τ = 1 µs) in front of a 12-bit ADC: to settle within ½ LSB (1/8192 = 0.012 %) needs $\ln8192\cdot\tau=9.0\ \mu$s — much longer than the "3τ" people assume.

### 4. Envelope response of a 915 MHz filter
A front-end stage with $Q_L=30$ at 915 MHz has envelope time constant $2Q_L/\omega_0=10.4$ ns (9.5 RF cycles). Irrelevant for LoRa (symbols are ms long) but significant for a 20 ns radar pulse.

## Practical notes
- **Measuring rise time** needs a measurement system at least 3× faster than the edge; otherwise you are measuring the scope ($t_{r,scope}\approx0.35/BW$, e.g. 7 ns for a 50 MHz scope).
- **Ringing on pyro/servo or supply lines** after switching is usually lead inductance with the load or decoupling capacitance; add a snubber (R ≈ $\sqrt{L/C}$ in series with C ≈ 3–4× the parasitic C) or shorten the loop.
- **Rocket avionics relevance:** supply transients when a 2 W LoRa module keys up at the same time a servo moves are the classic source of brown-outs; size bulk capacitance for the droop and damp it rather than just adding more MLCC (which raises Q).
- **Simulators:** SPICE `.tran` with a fast pulse source shows the real waveform including nonlinearity; set a max time step ≤ 1/20 of the fastest period of interest.
- **Snubbers, flyback diodes and TVS for pyro and servo loads** are worked out for avionics in [13 EMC § standards and transients](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md#emc-standards-and-transients-for-avionics).

## Common mistakes & misconceptions
- **"0.35/BW is exact."** It holds for single-pole/Gaussian-like responses; brick-wall-ish responses give 0.4–0.45 and overshoot.
- **"More capacitance always reduces ringing."** Adding low-ESR capacitance lowers $\sqrt{L/C}$ and can *reduce* damping (higher Q); what damps is resistance comparable to $\sqrt{L/C}$.
- **"3τ is settled."** 3τ is 95 %; precision settling needs 7–9 τ.
- **Blaming the circuit for probe ringing.** A 15 cm ground lead typically rings at 100–200 MHz; confirm with a short ground spring.
- **Using the series-RLC damping formula for a parallel tank.** In a parallel circuit larger R means *less* damping.
- **Forgetting the source impedance.** The damping resistance includes the driving source's output impedance and any series resistance, not just the component ESR.

## How to simulate / verify
- `python3 tools/verify/circuits_transient.py` — rise time vs τ, RLC overshoot formula vs step simulation, rise-time–bandwidth products for eleven response types, cascade rule accuracy, and all worked-example numbers.
- `scipy.signal.step`/`lsim` for linear systems; LTspice/ngspice `.tran` for circuits with parasitics and nonlinearity ([SPICE](../16-simulation-tools/spice-circuit-simulation.md)).
- Bench: square-wave generator (fast edge) into the circuit, measure with a short-ground probe; compare ring frequency and decay with $f_d$ and $\tau_{env}$.

## Open questions / gaps
- Probe ground-lead inductance per length depends on loop geometry; the 150 nH figure is an order-of-magnitude estimate (see [PCB parasitics](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md) for loop-inductance formulas).

## Sources
1. A. Agarwal, J. H. Lang, *Foundations of Analog and Digital Electronic Circuits*, Morgan Kaufmann, 2005 — ch. 10 (first-order transients), ch. 12 (second-order, damping). (textbook)
2. H. W. Johnson, M. Graham, *High-Speed Digital Design: A Handbook of Black Magic*, Prentice Hall, 1993 — ch. 1 (rise time and bandwidth, 0.35 rule and knee frequency), ch. 3 (probe ground-lead ringing). (textbook)
3. Keysight Technologies, "Understanding oscilloscope frequency response and its effect on rise-time accuracy," AN 5988-8008; and "Evaluating oscilloscope bandwidths for your application," AN 5989-5733 — 0.35 (Gaussian) vs ≈0.4–0.45 (maximally flat). https://www.keysight.com/us/en/assets/7018-01129/application-notes/5988-8008.pdf (app note)
4. K. Ogata, *Modern Control Engineering*, 5th ed., Prentice Hall, 2010 — ch. 5 (second-order step response, overshoot formula). (textbook)
5. A. B. Williams, F. J. Taylor, *Electronic Filter Design Handbook*, 4th ed., 2006 — step responses of Butterworth, Chebyshev, Bessel filters. (textbook)
6. Verification script `tools/verify/circuits_transient.py` (this KB).
