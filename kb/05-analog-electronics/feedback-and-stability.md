---
title: Feedback and stability — loop gain, Bode and Nyquist, phase margin, compensation, capacitive loads, parasitic oscillation
domain: 05-analog-electronics
slug: feedback-and-stability
tags: [feedback, loop-gain, bode, nyquist, phase-margin, gain-margin, compensation, dominant-pole, miller-compensation, pole-splitting, lead-lag, capacitive-load, isolation-resistor, emitter-follower-oscillation, base-stopper, ferrite-bead, parasitic-oscillation, tia]
prerequisites:
  - amplifier-topologies.md
  - ../00-math-foundations/laplace-transfer-functions-bode.md
  - ../00-math-foundations/complex-numbers-and-phasors.md
related:
  - op-amps-real-limitations.md
  - oscillators.md
  - active-filters.md
  - power-supplies-for-rf-and-analog.md
  - ../06-rf-circuits/amplifier-stability-and-biasing.md
  - ../06-rf-circuits/vco-and-pll-synthesizers.md
  - ../04-real-components-hf/ferrites-and-beads.md
  - ../13-pcb-rf-layout-emc/power-distribution-decoupling-for-rf.md
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Feedback and stability — loop gain, Bode and Nyquist, phase margin, compensation, capacitive loads, parasitic oscillation

## Questions this page answers
- What exactly is "loop gain", and how do I find it in a real circuit?
- What do phase margin and gain margin mean, and how much do I need?
- How does phase margin relate to overshoot and ringing on a step response?
- When is the simple Bode test not enough and I need the Nyquist criterion?
- How do op-amps stay stable (dominant-pole and Miller compensation, pole splitting, the right-half-plane zero)?
- Why does my op-amp ring or oscillate when I hang a capacitor (or a long cable, or an ADC input) on its output — and how do $R_{ISO}$ and in-loop compensation fix it?
- Why does a transimpedance amplifier or a high-value feedback resistor need a small feedback capacitor, and how big?
- Why does an emitter follower oscillate at hundreds of MHz, and why does a 100 Ω base resistor cure it?
- How do I track down and cure a parasitic oscillation on a real board?

## TL;DR
- Feedback: $A = a/(1+T)$ with loop gain $T(s) = a(s)\beta(s)$. Everything about stability is in $T$ — not in $a$ and not in $A$.
- **Bode test** (for loops whose $|T|$ crosses 1 once): phase margin PM = 180° + ∠T at $|T| = 1$; gain margin GM = 1/|T| where ∠T = −180°. Aim for **PM ≥ 45–60°**, GM ≥ 6–10 dB.
- **PM ↔ transient** for a two-pole loop (`tools/verify/analog_stability.py` §1): 30° → 42 % overshoot, 5.7 dB peaking; 45° → 23 %, 2.4 dB; 60° → 8.8 %, 0.3 dB; 65° → 4.7 %, no peaking; 76° → critically damped. Rule: ζ ≈ PM/100.
- **Nyquist** is the general tool (multiple crossings, conditionally stable loops, RHP poles): closed-loop RHP poles Z = N + P. A loop $K/(1+s)^3$ goes unstable at K = 8 (18 dB) — script §2 shows the closed-loop poles cross and the Nyquist plot starts encircling −1 there.
- **Compensation:** dominant pole (make one pole so low that $|T|$ reaches 1 before the second pole); **Miller pole splitting** in two-stage op-amps: $p_1 ≈ 1/(g_{m2}R_1R_2C_c)$, $p_2 ≈ g_{m2}/C_{load}$, GBW = $g_{m1}/C_c$, RHP zero at $g_{m2}/C_c$ (cancelled by a nulling resistor $R_z ≥ 1/g_{m2}$) — approximations within 0.2 % of exact (script §4).
- **Capacitive load:** op-amp open-loop output resistance $R_o$ with $C_L$ adds a pole $1/(2\pi R_oC_L)$ inside the loop. Unity-gain buffer, 10 MHz GBW, $R_o$ = 100 Ω: PM 90° → 61° (100 pF) → 23° (1 nF) → 7° (10 nF). An isolation resistor adds a zero $1/(2\pi R_{ISO}C_L)$: with 10 nF, $R_{ISO}$ = 10/22/47 Ω gives PM 47/73/86° (script §3) [1].
- **Feedback resistor + input capacitance** (TIA, high-value $R_F$) adds a pole in β: 100 kΩ with 20 pF gives PM ≈ 5°; $C_F = \sqrt{C_{in}/(2\pi R_FGBW)}$ = 1.8 pF restores ≈ 54° (script §6); for an inverting amplifier the neutral choice is $C_F = C_{in}R_G/R_F$.
- **Emitter/source follower** with capacitive load has a *negative* input resistance ≈ $-g_m/(\omega^2C_\pi C_L)$; with a few tens of nH of base-lead/trace inductance it oscillates at UHF unless the base resistance exceeds ≈ $g_mL/(C_\pi+C_L)$. Example (5 mA, 20 nH, 20 pF): exact small-signal threshold 95 Ω; ngspice oscillates at 82 Ω and is quiet at 100 Ω (script §5). **Cures:** base/gate stopper resistor (22–220 Ω) or ferrite bead right at the pin, short leads, local decoupling, series output resistor.

## Intuition (no math)
Negative feedback subtracts a sample of the output from the input. If the loop reacts instantly, errors are corrected and everything becomes precise and linear. But every real amplifier takes time to respond, and each pole adds lag — up to 90° per pole. By the time the correction arrives it may be late enough (180° of lag) that "subtracting" has become "adding": the feedback is now positive at that frequency. If the loop still has gain ≥ 1 there, a disturbance at that frequency returns bigger than it left and grows — oscillation. If the gain is just under 1, it returns almost as big and rings for a long time — a poorly damped, peaky response. Phase margin is the lag budget left at the frequency where the loop gain falls to 1; gain margin is how far the gain is below 1 at the frequency where the lag hits 180°.

Compensation is the art of arranging the poles so the loop gain falls to 1 *before* too much lag accumulates: make one pole dominant (the loop gain falls at a steady 20 dB/decade with 90° of lag, a well-behaved "integrator") and push all others above the crossover.

Parasitic oscillation is the same story with unintended loops: the stray inductance of a base lead, the capacitance of a load, the shared impedance of a supply trace. A follower driving a capacitor is really a small amplifier with a resonant circuit in its input — and at high frequency it shows negative resistance, which is exactly what an oscillator needs. A base stopper resistor adds enough positive resistance to beat it.

## The math

### Level 1 — definitions

**The feedback equation.** Forward gain $a(s)$, feedback factor $\beta(s)$ (the fraction of output returned), loop gain $T(s) = a(s)\beta(s)$:
$$A(s) = \frac{a(s)}{1+T(s)}\ \xrightarrow{\ |T|\gg1\ }\ \frac{1}{\beta(s)}.$$
For op-amps, $1/\beta$ is the **noise gain** (the gain from a voltage source in series with the non-inverting input to the output) — for both inverting and non-inverting configurations it equals $1+Z_F/Z_G$.

**Margins.** Let $f_c$ be the frequency where $|T(j2\pi f_c)| = 1$ (crossover) and $f_{180}$ where ∠T = −180°:
$$\text{PM} = 180^\circ + \angle T(jf_c),\qquad \text{GM} = -20\log_{10}|T(jf_{180})|\ \text{dB}.$$

**Rate of closure.** On a Bode plot of $|a|$ and $|1/\beta|$ (both in dB), $|T|$ is the gap between them. If the curves intersect with a closing slope of 20 dB/decade the loop is stable with good margin; 40 dB/decade means little or no phase margin [1][2].

### Level 2 — derivations

**Two-pole loop: phase margin → damping.** Take $T(s) = \omega_u/[s(1+s/p_2)]$ (an integrator with unity-gain frequency $\omega_u$ plus a second pole). Then
$$\frac{A}{A_\infty} = \frac{T}{1+T} = \frac{\omega_n^2}{s^2+2\zeta\omega_ns+\omega_n^2},\quad \omega_n^2 = \omega_up_2,\ \ \zeta = \frac12\sqrt{p_2/\omega_u}.$$
Solving $|T| = 1$ and evaluating the phase gives the exact relation
$$\text{PM} = \arctan\frac{2\zeta}{\sqrt{\sqrt{1+4\zeta^4}-2\zeta^2}},$$
and the familiar second-order results: overshoot $e^{-\pi\zeta/\sqrt{1-\zeta^2}}$, frequency-response peak $1/(2\zeta\sqrt{1-\zeta^2})$ for ζ < 0.707. Numerically (script §1):

| PM | ζ | Step overshoot | Closed-loop peaking |
|---|---|---|---|
| 30° | 0.27 | 41.6 % | 5.7 dB |
| 45° | 0.42 | 23.3 % | 2.4 dB |
| 60° | 0.61 | 8.8 % | 0.3 dB |
| 65° | 0.70 | 4.7 % | 0 dB |
| 76° | 0.99 | ≈ 0 % | 0 dB |

So "ζ ≈ PM/100" is a decent rule below ~65°. Inverting the table is a practical measurement: count the overshoot on a small-signal step to estimate PM.

**Nyquist criterion.** Map the closed contour enclosing the right-half s-plane through $T(s)$. The number of clockwise encirclements of −1, N, satisfies $Z = N + P$, where P is the number of open-loop RHP poles of T and Z the number of closed-loop RHP poles. Stable ⇔ Z = 0. For $T = K/(1+s)^3$: the phase reaches −180° at $\omega = \sqrt3$ where $|T| = K/8$, so the loop is stable for K < 8 (GM = 18.1 dB at K = 1). Script §2 confirms that at K = 8.1 two closed-loop poles are in the RHP and the plot encircles −1 twice. Use Nyquist (or check closed-loop poles directly) whenever |T| crosses unity more than once, when a loop is **conditionally stable** (stable only in a gain window — e.g. high-order PLL filters or ΣΔ modulators that go unstable when the gain *drops* during overload), or when open-loop RHP poles exist.

**Dominant-pole compensation.** With open-loop poles $p_1 < p_2 < p_3 \dots$ and DC loop gain $T_0$, placing a new pole (or lowering $p_1$) to $p_d$ so that $T_0p_d = p_2$ puts crossover at $p_2$ with PM ≈ 45°; for 60° cross over at ≈ $p_2/1.7$ (plus the extra lag of higher poles). Cost: bandwidth. An op-amp compensated for unity-gain stability (β = 1) is over-compensated at higher noise gain — "decompensated" op-amps exploit that (stable only for noise gain ≥ some minimum) (→ [op-amps](op-amps-real-limitations.md)).

**Miller compensation and pole splitting.** Two gain stages (transconductances $g_{m1}, g_{m2}$; node resistances $R_1, R_2$; node capacitances $C_1, C_2$) with a capacitor $C_c$ across the second stage. The characteristic polynomial is $1 + b_1s + b_2s^2$ with $b_1 = R_1(C_1+C_c) + R_2(C_2+C_c) + g_{m2}R_1R_2C_c$ and $b_2 = R_1R_2(C_1C_2 + C_c(C_1+C_2))$. Widely separated poles give
$$p_1 \approx \frac{1}{g_{m2}R_1R_2C_c},\qquad p_2 \approx \frac{g_{m2}C_c}{C_1C_2 + C_c(C_1+C_2)} \xrightarrow{C_c\gg C_1} \frac{g_{m2}}{C_2},\qquad \text{GBW} = \frac{g_{m1}}{C_c},\qquad z_{RHP} = +\frac{g_{m2}}{C_c}.$$
$C_c$ pushes $p_1$ down (Miller) and $p_2$ up (at high frequency $C_c$ shorts the second stage into a diode-connected load $1/g_{m2}$) — *pole splitting*. For stability need $p_2 \gtrsim 2$–3 × GBW and the RHP zero well above GBW (it adds phase *lag* like a pole while raising gain). Script §4: with $g_{m1}$ = 1 mS, $g_{m2}$ = 10 mS, $C_c$ = 3 pF, $p_2$/GBW = 5.4 and the approximations match the exact roots within 0.2 %. A resistor $R_z$ in series with $C_c$ moves the zero to $1/[C_c(1/g_{m2} - R_z)]$ — infinite at $R_z = 1/g_{m2}$, into the LHP (useful phase lead) for larger $R_z$ [3].

**Lead and lag compensation.** A lead network (zero below a pole) adds up to $\arcsin[(\alpha-1)/(\alpha+1)]$ of phase between them for a pole/zero ratio α — placed at crossover, it buys phase margin. A lag network lowers loop gain above a corner without adding much phase lag near crossover. In op-amp circuits the most common "lead" is a small capacitor across the feedback resistor (it creates a zero in β, i.e. phase lead in T).

**Capacitive load.** Model the op-amp output as an ideal source behind open-loop output resistance $R_o$. The load $C_L$ forms a pole at $1/(2\pi R_oC_L)$ *inside* the loop:
$$T(s) = \frac{a(s)\beta}{1+sR_oC_L}.$$
If that pole sits below the crossover it eats up to 90° of phase margin (script §3). Remedies [1][4]:
- **Isolation resistor** $R_{ISO}$ between the op-amp output and $C_L$, feedback taken from the op-amp pin: $T = a\beta(1+sR_{ISO}C_L)/[1+s(R_o+R_{ISO})C_L]$ — the zero cancels the pole's phase above $1/(2\pi R_{ISO}C_L)$. TI's rule: place the zero at or below the frequency where the loaded open-loop gain is 20 dB, for PM > 60° [1]. Cost: DC/low-frequency error from load current in $R_{ISO}$, and slower settling.
- **$R_{ISO}$ + dual feedback:** DC feedback from the load side (through $R_F$), high-frequency feedback from the op-amp pin (through $C_F$) — restores DC accuracy, slower settling [1].
- **Noise-gain shaping** ($R$ in series with $C_F$, or R–C from the inverting input to ground): raises $1/\beta$ at high frequency so crossover moves below the load pole; costs noise and bandwidth [1].
- **Snubber** (series R–C from output to ground) damping the load resonance; or choose an op-amp specified for unlimited capacitive load.

**Feedback network pole (TIA / large $R_F$).** Input capacitance $C_{in}$ (op-amp input + photodiode/sensor + stray) and $R_F$ make $\beta(s) = 1/(1+sR_FC_{in})$ — a pole in β = a zero-free rise in $1/\beta$ that meets the falling $|a|$ at 40 dB/decade. Adding $C_F$ across $R_F$: $\beta = (1+sR_FC_F)/[1+sR_F(C_{in}+C_F)]$. The classic choice for a single-pole op-amp is $C_F \approx \sqrt{C_{in}/(2\pi R_FGBW)}$ (≈ 45–65° PM depending on $C_{in}/C_F$); for 100 kΩ, 20 pF, 10 MHz: 1.78 pF → PM 54° (vs 5° with no $C_F$; script §6). For an inverting amplifier with gain resistor $R_G$, "neutral" compensation $C_F = C_{in}R_G/R_F$ makes β frequency-independent.

**Emitter-follower negative resistance (derivation).** Ignore $C_\mu$ first. Looking into the base of a follower with emitter load $Z_L$ and internal $Z_\pi = r_\pi\|(1/sC_\pi)$:
$$Z_{in} = Z_\pi + (1+g_mZ_\pi)Z_L .$$
Above $1/(2\pi r_\pi C_\pi)$, $Z_\pi \approx 1/(j\omega C_\pi)$, and with $Z_L = 1/(j\omega C_L)$ the cross term is $g_m/[(j\omega)^2C_\pi C_L] = -g_m/(\omega^2C_\pi C_L)$ — a **negative real part**. The reactive part is the series combination of $C_\pi$ and $C_L$, which resonates with base-circuit inductance $L$ at $\omega_0^2 = (C_\pi+C_L)/(LC_\pi C_L)$. At resonance the negative resistance is $-g_mL/(C_\pi+C_L)$, so the loop oscillates when
$$R_{source} + r_b \lesssim \frac{g_mL}{C_\pi + C_L}.$$
Example: $I_C$ = 5 mA ($g_m$ = 0.19 S), L = 20 nH (≈ 2 cm of lead or trace), $C_L$ = 20 pF, $C_\pi$ ≈ 11 pF → bound 124 Ω. The full small-signal model (with $r_\pi$ and $C_\mu$) gives 95 Ω at ≈ 460 MHz, and an ngspice transient oscillates with 82 Ω and is quiet at 100 Ω (script §5). The same mechanism makes source followers, and the emitter-follower output stages of op-amps and audio amplifiers, oscillate — and it is why RF transistor datasheets warn about gate/base stoppers.

### Level 3 — real-world subtleties
- **Loop gain in circuits without an obvious "β":** break the loop at a point where one side is a low impedance and the other high (op-amp output), or use Middlebrook's double-injection or Tian's method in SPICE — a series AC voltage source in the loop gives $T = -V_{return}/V_{inject}$ when the break point is impedance-favourable. Bench: inject through a small resistor with an isolation transformer and a network analyser (or the Bode function of a USB scope).
- **Multiple loops:** local feedback (degeneration, Miller) nested inside global feedback; stability must hold for each loop and the whole. Supply impedance shared by stages creates an unintended loop ("motorboating" at low frequency, squegging at RF) — local decoupling breaks it (→ [power supplies](power-supplies-for-rf-and-analog.md)).
- **Large-signal and conditional stability:** slew-rate limiting and saturation change effective loop gain; conditionally stable loops can oscillate after overload. ΣΔ modulators and high-order PLLs need explicit large-signal checks.
- **RF amplifiers:** stability is judged with S-parameters (Rollett K and μ) because "the loop" includes the source/load terminations; resistive loading, stabilising RC networks and feedback are the cures (→ [amplifier stability & biasing](../06-rf-circuits/amplifier-stability-and-biasing.md)).
- **Oscillators are the flip side:** they are designed to violate these criteria in a controlled way (→ [oscillators](oscillators.md)).

## Design equations & rules of thumb

| Quantity | Equation / rule | Notes |
|---|---|---|
| Closed-loop gain | $a/(1+T)$ → $1/\beta$ | error ≈ 1/T |
| Phase margin | $180° + \angle T$ at $|T| = 1$ | target 45–60°; 60–70° for fast settling |
| Gain margin | $-20\log|T|$ at −180° | target ≥ 6–10 dB |
| PM ↔ ζ | ζ ≈ PM/100 (PM < 65°) | exact formula above |
| Rate of closure | 20 dB/dec stable; 40 dB/dec marginal | Bode of $|a|$ vs $|1/\beta|$ [1] |
| Miller comp. | GBW = $g_{m1}/C_c$; $p_2 ≈ g_{m2}/C_2$; $z = g_{m2}/C_c$ | need $p_2 ≳ 2$–3 GBW |
| Nulling resistor | $R_z ≥ 1/g_{m2}$ | removes/relocates RHP zero |
| Capacitive-load pole | $1/(2\pi R_oC_L)$ | $R_o$ = open-loop output resistance (datasheet $Z_o$ plot) |
| Isolation zero | $1/(2\pi R_{ISO}C_L)$ | typical $R_{ISO}$ 10–100 Ω |
| TIA feedback cap | $C_F ≈ \sqrt{C_{in}/(2\pi R_FGBW)}$ | ≈ 45–65° PM |
| Neutral compensation | $C_F = C_{in}R_G/R_F$ | inverting amps with large R |
| Follower oscillation | unstable if $R_s + r_b ≲ g_mL/(C_\pi+C_L)$ | use base stopper above this |
| Base/gate stopper | 22–220 Ω, or ferrite bead, *at the pin* | also for paralleled MOSFETs |

## Worked examples

### 1. Driving an ADC input or a long cable from a unity-gain buffer
Op-amp: 10 MHz GBW, $R_o$ ≈ 100 Ω (read the open-loop output impedance curve). Load: 10 nF (a filter capacitor or ~100 m of coax — or a reference-buffer decoupling capacitor). Unity gain: PM = 7° — it will ring or oscillate (script §3). Add $R_{ISO}$ = 22 Ω: zero at 0.72 MHz, PM = 73°. If the load draws DC current (e.g. ADC reference input), move DC feedback to the load side (dual feedback) to remove the $R_{ISO}$ drop [1]. Many SAR-ADC driver data sheets specify exactly this "R–C" between driver and ADC for the same reason plus charge-kickback absorption (→ [data converters](data-converters-adc-dac.md)).

### 2. A photodiode transimpedance amplifier
$R_F$ = 100 kΩ, photodiode + op-amp input 20 pF, op-amp 10 MHz GBW. Without $C_F$: PM ≈ 5° (rings at ~0.9 MHz). $C_F = \sqrt{20\text{ pF}/(2\pi\cdot100\text{ kΩ}\cdot10\text{ MHz})}$ = 1.78 pF → use 1.8 pF (PM ≈ 54°; closed-loop bandwidth ≈ $1/(2\pi R_FC_F)$ ≈ 0.89 MHz). 2 pF → 58°; 5 pF → 83° but only 320 kHz bandwidth (script §6). The pad/trace capacitance of an 0402 resistor is ~0.1–0.2 pF — at this scale layout is part of the design (→ [low-noise design](low-noise-analog-design.md)).

### 3. A 433 MHz buffer that oscillates at ~500 MHz
Symptom: an emitter follower buffering a VCO output shows a spur at 460 MHz and a DC shift in emitter voltage when probed. Model: 5 mA, 20 nH of base lead and trace, 20 pF of load (the next stage + trace). Threshold ≈ 95 Ω (script §5). Fix: 100–150 Ω SMD resistor *at the base pin* (or a ferrite bead with ≥ 100 Ω at 500 MHz), plus 100 pF + 10 nF decoupling right at the collector. Confirm with a spectrum analyser (the fix should remove the spur without changing the wanted signal much — the stopper forms a low-pass with the input capacitance, so check the loss at 433 MHz).

### 4. Checking an op-amp design by the step test
Drive the circuit with a small (≤ 50 mV) square wave; if the overshoot is 25 %, the PM is ≈ 45° (table above). Large-signal steps are slew-limited and tell you nothing about PM.

## Practical notes
- **Finding a parasitic oscillation:** look with a spectrum analyser or a wideband scope with a low-capacitance probe (the probe's own capacitance can start or stop it). Symptoms: DC operating point wrong, fuzzy traces, supply current too high, performance changes when a hand approaches, excessive heating.
- **Cures in order of preference:** (1) base/gate stopper resistor or ferrite bead at the device pin; (2) local supply decoupling at every active device — a small RF capacitor (100 pF–1 nF) plus 100 nF plus bulk (→ [decoupling](../13-pcb-rf-layout-emc/power-distribution-decoupling-for-rf.md)); (3) shorten leads/loops, solid ground plane; (4) series output resistor for capacitive loads; (5) reduce gain/add loss at the oscillation frequency (resistive loading, RC stabiliser).
- **Ferrite beads** are lossy (resistive) above ~100 MHz — good for killing VHF/UHF parasitics without DC drop; check the R–X curve and DC-bias derating (→ [ferrites & beads](../04-real-components-hf/ferrites-and-beads.md)).
- **Paralleled MOSFETs** (pyro drivers, load switches) need individual gate resistors to prevent inter-device oscillation.
- **Op-amp inputs** with large feedback resistors (≥ 100 kΩ) need a small $C_F$; check the stray capacitance of the inverting node.

## Common mistakes & misconceptions
- **Checking stability of the closed-loop gain instead of the loop gain.** A gain-of-10 amplifier and a gain-of-1 buffer using the same op-amp have very different phase margins — the buffer is the harder case.
- **"The op-amp is unity-gain stable, so any circuit with it is stable."** Capacitive loads, feedback-network poles and $C_{in}$ with large resistors change the loop.
- **Adding a capacitor across the feedback resistor of a *non-inverting* buffer to "slow it down".** For a follower it does nothing useful; for other circuits check what it does to $1/\beta$.
- **Using Barkhausen's "|T| = 1 at 180°" as a stability test.** Stability requires the Nyquist condition; a loop can have |T| > 1 at −180° and still be stable (conditionally), or be unstable despite passing a naive Bode check if it has RHP poles.
- **Placing the base stopper at the far end of a trace.** The inductance you are fighting is between the stopper and the pin; put it at the pin.
- **Probing an RF stage with a 10 pF scope probe and declaring it stable.** The probe changes the circuit.

## How to simulate / verify
- **Python:** `tools/verify/analog_stability.py` — PM/ζ/overshoot/peaking table from both the closed form and numeric loop analysis; Nyquist encirclement counting and closed-loop poles for $K/(1+s)^3$; op-amp $C_L$ and $R_{ISO}$ phase-margin sweeps; Miller pole splitting vs exact roots; follower critical base resistance (small-signal roots) plus ngspice transient; TIA $C_F$ sweep.
- **ngspice follower oscillation test** (via `tools/verify/analog_ngspice.py`):
```spice
* emitter follower with base lead inductance and capacitive load
.model QF NPN(IS=1e-15 BF=200 VAF=50 TF=40p CJE=2p CJC=0.5p RB=0)
VCC vcc 0 DC 5
VB bsrc 0 DC 2 PULSE(2 2.05 10n 0.1n 0.1n 1u 2u)
Rst bsrc b1 82
Lb b1 b 20n
Q1 vcc b e QF
IE e 0 DC 5m
CL e 0 20p
.tran 0.02n 400n 0 0.02n
.end
```
  With `Rst` = 82 Ω `v(e)` shows sustained ~0.17 V p-p oscillation; with 100 Ω it decays to nothing.
- **Loop gain in SPICE:** insert a 0 V source in the loop at a low-to-high-impedance boundary, add AC excitation, and plot $-V_{return}/V_{inject}$; or use the Tian/Middlebrook probe subcircuits common in LTspice examples. Always also run a small-signal step (transient) — it catches mistakes in the loop-break.
- **Bench:** small-signal square-wave test (overshoot → PM), frequency response with a VNA or USB scope Bode mode, spectrum analyser sweep for parasitics (→ [spectrum analysers](../17-test-measurement/spectrum-analyzers.md)).

## Open questions / gaps
- $R_o$ (open-loop output impedance) of real op-amps is frequency dependent (inductive or capacitive regions); the single-resistor model is a first approximation — use datasheet $Z_o$ plots or vendor models.
- ADI's Analog Dialogue articles on capacitive loading (Ask the Applications Engineer 25 and 32) could not be retrieved (timeouts); cross-check of the $R_{ISO}$/in-loop compensation equations against them is pending.

## Sources
1. C. Wells, *Do-it-yourself: Three ways to stabilize op amp capacitive loads*, Texas Instruments SSZT999, 2017. https://www.ti.com/lit/pdf/sszt999 — capacitive load forms an extra pole with output impedance; $R_{ISO}$ zero; placement at loaded $A_{OL}$ = 20 dB for PM > 60°; $R_{ISO}$+DFB; noise-gain increase with $R_{Fx}$; rate of closure. (app note)
2. S. Franco, *Design with Operational Amplifiers and Analog Integrated Circuits*, 4th ed., McGraw-Hill 2015 — ch. 8 (stability, noise gain, rate of closure, capacitive loads, input-capacitance compensation, TIA). (textbook)
3. P. R. Gray, P. J. Hurst, S. H. Lewis, R. G. Meyer, *Analysis and Design of Analog Integrated Circuits*, 5th ed., Wiley 2009 — ch. 9 (frequency response and stability of feedback amplifiers, Nyquist, PM ↔ transient, Miller compensation, pole splitting, RHP zero and nulling resistor). (textbook)
4. Texas Instruments, *Determine optimal isolation resistance for driving capacitive loads*, SBOA418; and *Operational amplifier stability theory and compensation*, SBOA626. https://www.ti.com/lit/pdf/sboa418 , https://www.ti.com/lit/wp/sboa626/sboa626.pdf (app notes; identified by search, not read in full)
5. R. Mancini (ed.), *Op Amps for Everyone*, Texas Instruments SLOD006B, 2002 — ch. 5–7 (feedback and stability theory, voltage-feedback compensation). https://www.ti.com/lit/an/slod006b/slod006b.pdf (app note/book)
6. J. G. Graeme, *Photodiode Amplifiers: Op Amp Solutions*, McGraw-Hill 1996 — TIA feedback-capacitance compensation. (textbook)
7. P. Horowitz, W. Hill, *The Art of Electronics*, 3rd ed., Cambridge 2015 — ch. 2 (emitter-follower oscillation, base stoppers), ch. 4 (op-amp stability, capacitive loads). (textbook)
8. R. D. Middlebrook, "Measurement of loop gain in feedback systems," *Int. J. Electronics* 38(4), 485–512, 1975. (peer-reviewed)
