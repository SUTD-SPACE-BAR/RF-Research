---
title: Lumped elements, impedance and admittance
domain: 01-circuit-theory
slug: lumped-elements-impedance-admittance
tags: [impedance, admittance, reactance, susceptance, phasor, lumped-element, series-parallel-conversion, reactance-chart, Q]
prerequisites:
  - ../00-math-foundations/complex-numbers-and-phasors.md
  - ../00-math-foundations/decibels-and-log-units.md
related:
  - network-theorems-max-power-transfer.md
  - resonance-and-q.md
  - energy-storage-and-reactive-power.md
  - two-port-networks-zyh-abcd.md
  - ../03-transmission-lines-matching/smith-chart.md
  - ../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md
  - ../04-real-components-hf/capacitors-at-rf-mlcc.md
  - ../04-real-components-hf/inductors-at-rf.md
  - ../02-electromagnetics/quasi-static-vs-full-wave.md
level: intro
confidence: high
last_updated: 2026-10-12
---

# Lumped elements, impedance and admittance

## Questions this page answers
- What are Ohm's law and electrical power, and how do I size a resistor for an LED or a divider?
- What do the prefixes p, n, µ, m, k, M and G mean, and how do I convert between them?
- How much power does a resistor dissipate, and when will it burn?
- What is impedance, and how is it different from resistance?
- Why does a capacitor's impedance fall with frequency while an inductor's rises?
- What is the reactance of 10 nH or 10 pF at 433 MHz, 915 MHz and 2.4 GHz?
- What is admittance, and when is it easier to use than impedance?
- How do I combine impedances in series and in parallel?
- How do I turn a series R + jX into an equivalent parallel R ∥ X (and why is that only true at one frequency)?
- Why is a capacitor's reactance negative?
- When can I treat a component or a PCB trace as "lumped"?
- What value of L or C gives 50 Ω of reactance at my frequency?
- Is a 100 nF capacitor a "short circuit" at 433 MHz?

## TL;DR
- With the engineering phasor convention $e^{j\omega t}$: $Z_R=R$, $Z_L=j\omega L$, $Z_C=1/(j\omega C)=-j/(\omega C)$. Reactance $X_L=+\omega L$ (positive, inductive), $X_C=-1/(\omega C)$ (negative, capacitive). $\omega=2\pi f$.
- Admittance $Y=1/Z=G+jB$ (siemens). Series elements add impedances; shunt (parallel) elements add admittances. Ladder networks are analysed by alternating the two.
- Handy numbers: **1 nH ≈ 2.73 Ω at 433.92 MHz, 5.75 Ω at 915 MHz, 15.4 Ω at 2.45 GHz; 1 pF ≈ 367 Ω, 174 Ω, 65 Ω** at the same frequencies (verified by `tools/verify/circuits_impedance_basics.py`).
- 50 Ω of reactance: **18.3 nH or 7.34 pF at 433.92 MHz; 8.70 nH or 3.48 pF at 915 MHz; 3.25 nH or 1.30 pF at 2.45 GHz.** Useful for sanity-checking any matching network you are handed.
- A series $R+jX$ equals a parallel $R_p\parallel X_p$ at one frequency with $R_p=R(1+Q^2)$, $X_p=X(1+1/Q^2)$, $Q=|X|/R$. For $Q\gg1$: $R_p\approx Q^2R$, $X_p\approx X$.
- "Lumped" means the element is small compared with the wavelength (rule of thumb < λ/10–λ/20 *in the medium*). At 915 MHz on FR-4 microstrip λ ≈ 180 mm, so a 0402 part (1 mm) is lumped but a 20 mm trace is not.
- Real parts are not ideal: every capacitor has series inductance, every inductor has shunt capacitance. A 100 nF 0402 MLCC is **inductive** above roughly 20 MHz — at 433 MHz it looks like ~0.5 nH, not a short (see [capacitors at RF](../04-real-components-hf/capacitors-at-rf-mlcc.md)).

- **DC basics:** $V = IR$, $P = VI = I^2R = V^2/R$, energy = $P\,t$ (1 Wh = 3600 J); a red LED at 10 mA from 3.3 V needs 130 Ω (ngspice 9.8 mA); a 1 Ω igniter across a 2S pack takes 8.4 A / 71 W (`tools/verify/s3_primer.py` §1).

## Intuition (no math)
A **resistor** turns electrical energy into heat; its voltage and current rise and fall together. A **capacitor** stores energy in an electric field between plates: current has to flow *into* it before voltage can build up, so the current waveform peaks a quarter-cycle *before* the voltage. The faster you wiggle the voltage (higher frequency), the more charge must shuttle in and out per second, so a capacitor passes more current — its opposition to AC falls with frequency. An **inductor** stores energy in a magnetic field; it fights any change in current by generating a back-voltage, so the voltage peaks a quarter-cycle *before* the current. The faster the current tries to change, the harder it fights — its opposition rises with frequency.

**Impedance** is a single complex number that captures both "how many volts per amp" (the magnitude) and "how far ahead or behind the current is" (the phase). The real part, **resistance**, is the part that absorbs power. The imaginary part, **reactance**, is the part that stores energy and hands it back every cycle; it causes phase shift but no average power loss.

**Admittance** is just the reciprocal — "how many amps per volt". It is the natural language for things connected side-by-side, because parallel branches share the same voltage and their currents simply add.

Why the fuss about "lumped"? Circuit theory assumes a signal arrives at both ends of a component at the same instant. That is only true if the component is much shorter than a wavelength. At 433 MHz a wavelength in air is 69 cm, so millimetre-sized chips are fine. A long PCB trace, a coax cable or an antenna is *not* lumped; it must be treated as a transmission line or an electromagnetic structure ([telegrapher equations](../03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md), [quasi-static vs full-wave](../02-electromagnetics/quasi-static-vs-full-wave.md)).

## The math

### Level 0 — DC basics (Ohm's law, power, SI prefixes)
*For readers starting from zero; impedance below is the AC generalisation of resistance.*

- **Charge, current, voltage.** Current $I$ (amperes, A) is charge flow, coulombs per second. Voltage $V$ (volts, V) is energy per unit charge, joules per coulomb, between two points. It is always a *difference*, so "the voltage at a node" means relative to a chosen ground.
- **Ohm's law.** For a resistor, $V = IR$ ($R$ in ohms, Ω). Doubling the voltage doubles the current. Conductance $G = 1/R$ is in siemens (S).
- **Kirchhoff's laws.** The currents into a node sum to zero (charge is not stored at a point). The voltages around any closed loop sum to zero (energy is conserved). These two laws, plus the element laws, solve every circuit on this page.
- **Series and parallel.** In series, resistances add. In parallel, conductances add: $R_1\|R_2 = R_1R_2/(R_1+R_2)$. A divider gives $V_{out} = V_{in}R_2/(R_1+R_2)$, but only if the load draws much less current than the divider.
- **Power and energy.** $P = VI = I^2R = V^2/R$ (watts, W). Energy is $E = Pt$, in joules or watt-hours (1 Wh = 3600 J). A cell's capacity in mAh times its voltage is its energy: 1000 mAh × 3.7 V = 3.7 Wh = 13.3 kJ.
- **SI prefixes:**

| Prefix | p | n | µ | m | — | k | M | G |
|---|---|---|---|---|---|---|---|---|
| Factor | 10⁻¹² | 10⁻⁹ | 10⁻⁶ | 10⁻³ | 1 | 10³ | 10⁶ | 10⁹ |
| Example | 10 pF matching capacitor | 1 nH via | 63 µA divider current | 10 mA LED | 1 Ω igniter | 10 kΩ pull-up | 1 MΩ scope input | 2.4 GHz |

  Multiplying prefixes add exponents: 2 mA × 3 kΩ = 6 V (10⁻³ × 10³ = 1); 1 µA × 1 MΩ = 1 V; 1 kΩ × 1 nF = 1 µs.

**Worked numbers** (`tools/verify/s3_primer.py` §1, ngspice .op where marked):
- **LED resistor.** A red LED with $V_F$ ≈ 2.0 V at 10 mA from 3.3 V needs $R = (3.3-2.0)/0.010$ = 130 Ω. The resistor dissipates 13 mW and the LED 20 mW. ngspice with an LED model gives 9.8 mA (the LED voltage rises slightly with current).
- **Battery divider.** 8.4 V across 100 kΩ + 33 kΩ draws 63 µA and wastes 0.53 mW, giving 2.084 V at the tap (ngspice).
- **Resistor ratings.** An 0603 resistor rated 0.1 W can take at most $\sqrt{PR}$ = 10 V across 1 kΩ, or 0.32 A through 1 Ω. Check pulse ratings for inrush and pyro paths.
- **Wiring.** 1 m of 0.5 mm² copper is 34 mΩ. At 2 A it drops 69 mV and dissipates 0.14 W, so connectors and thin wires matter for radio bursts.
- **Why pyro outputs are dangerous.** A 1 Ω igniter across an 8.4 V 2S pack takes 8.4 A and 71 W, so the FET must be provably off.

### Level 1 — the element laws and their impedances

Time-domain element laws (SI units):

| Element | Law | Impedance $Z$ | Admittance $Y$ | Reactance / susceptance |
|---|---|---|---|---|
| Resistor $R$ [Ω] | $v=Ri$ | $R$ | $G=1/R$ [S] | — |
| Capacitor $C$ [F] | $i=C\,\dfrac{dv}{dt}$ | $\dfrac{1}{j\omega C}$ | $j\omega C$ | $X_C=-\dfrac{1}{\omega C}$, $B_C=+\omega C$ |
| Inductor $L$ [H] | $v=L\,\dfrac{di}{dt}$ | $j\omega L$ | $\dfrac{1}{j\omega L}$ | $X_L=+\omega L$, $B_L=-\dfrac{1}{\omega L}$ |

Here $\omega=2\pi f$ is angular frequency in rad/s, $f$ in Hz. A general impedance is written $Z=R+jX$ and a general admittance $Y=G+jB$, where $G$ is conductance and $B$ susceptance (both in siemens, S).

Combination rules:
- Series: $Z_\text{tot}=Z_1+Z_2+\dots$ (same current through each).
- Parallel: $Y_\text{tot}=Y_1+Y_2+\dots$, i.e. $Z_\text{tot}=\left(\sum 1/Z_k\right)^{-1}$; for two, $Z_1\parallel Z_2=Z_1Z_2/(Z_1+Z_2)$.
- Two capacitors in series: $C=C_1C_2/(C_1+C_2)$; in parallel: $C_1+C_2$. Inductors (uncoupled) the other way round: series add, parallel combine like resistors.

### Level 2 — where $j\omega$ comes from

Assume every voltage and current is a sinusoid at one frequency: $v(t)=\operatorname{Re}\{V e^{j\omega t}\}$, where the **phasor** $V=|V|e^{j\phi}$ carries amplitude and phase ([complex numbers and phasors](../00-math-foundations/complex-numbers-and-phasors.md)). Differentiation then becomes multiplication by $j\omega$:

$$\frac{d}{dt}\operatorname{Re}\{Ve^{j\omega t}\}=\operatorname{Re}\{j\omega Ve^{j\omega t}\}.$$

Substituting into $i=C\,dv/dt$ gives $I=j\omega C V$, so $Z_C=V/I=1/(j\omega C)$. Since $1/j=-j$, the current phasor is $+90^\circ$ ahead of the voltage. For the inductor, $V=j\omega L I$: voltage leads current by $90^\circ$. These are exact for ideal elements in sinusoidal steady state; transients need the full differential equations or the Laplace domain ($j\omega\to s$, see [transient and step response](transient-and-step-response.md)).

**Impedance ↔ admittance.** With $Z=R+jX$:
$$Y=\frac{1}{R+jX}=\frac{R}{R^2+X^2}-j\frac{X}{R^2+X^2}\quad\Rightarrow\quad G=\frac{R}{R^2+X^2},\;B=\frac{-X}{R^2+X^2}.$$
Note $G\ne 1/R$ unless $X=0$ — a very common slip.

**Series ↔ parallel equivalence.** A series pair $R_s+jX_s$ and a parallel pair $R_p\parallel jX_p$ have the same terminal impedance at one frequency if their admittances match: $1/R_p=G$ and $-1/X_p=B$. Defining $Q=|X_s|/R_s$ and eliminating:
$$R_p=R_s\,(1+Q^2),\qquad X_p=X_s\left(1+\frac{1}{Q^2}\right),$$
and the inverse $R_s=R_p/(1+Q^2)$, $X_s=X_p\,Q^2/(1+Q^2)$ with $Q=R_p/|X_p|$ (the same $Q$ — it is a property of the impedance, not of the representation). For $Q\gtrsim 5$ the approximations $R_p\approx Q^2R_s$ and $X_p\approx X_s$ are within 4 %. This transformation is the heart of L-network matching ([resonance and Q](resonance-and-q.md), [impedance matching](../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md)). Because $X_s$ itself depends on frequency, the equivalence holds only at the frequency where it was computed — the parallel model of a lossy inductor is a different circuit at 400 MHz and at 900 MHz.

### Level 3 — general properties and limits of validity

- **Passivity.** A passive one-port always has $\operatorname{Re}\{Z(j\omega)\}\ge 0$. A negative real part means an active device (an oscillating transistor, a tunnel diode) — this is how oscillators are analysed ([oscillators](../05-analog-electronics/oscillators.md)).
- **Foster's reactance theorem.** For any *lossless* one-port, $dX/d\omega>0$ and $dB/d\omega>0$ everywhere: reactance always increases with frequency, and poles and zeros alternate. Consequence: you cannot build a lossless network whose reactance falls with frequency (a "negative inductor" over a band) — which is why broadband matching has fundamental limits ([Bode–Fano](../03-transmission-lines-matching/broadband-matching-bode-fano.md)).
- **Causality.** $R(\omega)$ and $X(\omega)$ of a causal, stable network are not independent; they are a Hilbert-transform (Kramers–Kronig) pair. Practical consequence: a measured S-parameter file whose real and imaginary parts are inconsistent will make time-domain simulations misbehave ([component models](../04-real-components-hf/component-models-s2p-spice.md)).
- **Lumped approximation.** Kirchhoff's laws follow from Maxwell's equations only when the circuit is electrically small, so that the displacement current outside components and the propagation delay across the circuit are negligible. The usual rule is size $<\lambda/10$ (for loose work) to $<\lambda/20$ (for accurate work), with $\lambda=c/(f\sqrt{\varepsilon_\text{eff}})$ in the medium. On FR-4 microstrip ($\varepsilon_\text{eff}\approx3.3$): λ ≈ 380 mm at 433.92 MHz, 180 mm at 915 MHz, 67 mm at 2.45 GHz.
- **Convention warning.** Physics texts often use $e^{-i\omega t}$, in which $Z_L=-i\omega L$ and $Z_C=i/(\omega C)$. Nothing physical changes; every $j$ becomes $-i$. This KB always uses $e^{j\omega t}$ (CONVENTIONS §4.5).
- **Real components** are small networks, not single elements: capacitor = C + ESR + ESL (+ shunt pad capacitance); inductor = L + series loss R + shunt winding capacitance; resistor = R + series L + shunt C. The ideal models on this page are the building blocks for those models ([04-real-components-hf](../04-real-components-hf/_index.md)).

## Design equations & rules of thumb

| Quantity | Equation | Valid when | Typical values |
|---|---|---|---|
| Inductive reactance | $X_L=2\pi fL$ | below SRF | 10 nH → 27.3 Ω @ 433.92 MHz, 57.5 Ω @ 915 MHz |
| Capacitive reactance | $X_C=-1/(2\pi fC)$ | below SRF | 10 pF → −36.7 Ω @ 433.92 MHz, −17.4 Ω @ 915 MHz |
| L for reactance $X$ | $L=X/(2\pi f)$ | — | 50 Ω → 18.3 nH (433.92 MHz), 8.7 nH (915 MHz) |
| C for reactance $X$ | $C=1/(2\pi f|X|)$ | — | 50 Ω → 7.34 pF (433.92 MHz), 3.48 pF (915 MHz) |
| DC block "transparent" | $|X_C|\ll Z_0$, e.g. $\le 1\,\Omega$ | $C$ below its SRF | ≥ 370 pF @ 433 MHz, ≥ 175 pF @ 915 MHz (but see SRF!) |
| Z → Y | $G=R/(R^2+X^2)$, $B=-X/(R^2+X^2)$ | always | — |
| Series → parallel | $R_p=R_s(1+Q^2)$, $X_p=X_s(1+Q^{-2})$ | one frequency | Q = 100: $R_p=10^4R_s$ |
| Lumped limit | length $<\lambda_g/10$ | — | 18 mm @ 915 MHz on FR-4 |

A **reactance chart** (log–log plot of $|X|$ vs $f$ with lines of constant L rising at +1 decade/decade and lines of constant C falling at −1 decade/decade) lets you read off the element for a reactance, and the resonant frequency where an L-line crosses a C-line. The table in the worked example below is a numerical reactance chart for the reader's bands.

## Worked examples

### 1. Reactance table at the reader's bands
Computed by `tools/verify/circuits_impedance_basics.py` (Ω; capacitor values are $|X_C|$):

| Element | 433.92 MHz | 868 MHz | 915 MHz | 1575.42 MHz | 2.45 GHz |
|---|---|---|---|---|---|
| 1 nH | 2.73 | 5.45 | 5.75 | 9.90 | 15.4 |
| 10 nH | 27.3 | 54.5 | 57.5 | 99.0 | 154 |
| 100 nH | 273 | 545 | 575 | 990 | 1539 |
| 1 pF | 367 | 183 | 174 | 101 | 65.0 |
| 10 pF | 36.7 | 18.3 | 17.4 | 10.1 | 6.50 |
| 100 pF | 3.67 | 1.83 | 1.74 | 1.01 | 0.650 |
| 1 nF | 0.367 | 0.183 | 0.174 | 0.101 | 0.065 |

Reading it: to cancel +27 Ω of stray inductive reactance at 433 MHz you need about 10 pF in series; at 2.45 GHz the same 10 nH is +154 Ω and a 0.4 nH pad-and-via parasitic is already +6 Ω. (The 1 nF row is the *ideal* value — a real 1 nF 0402 capacitor is past its self-resonance at 915 MHz; see [capacitors at RF](../04-real-components-hf/capacitors-at-rf-mlcc.md).)

### 2. An antenna-like load at 433.92 MHz: $Z=30-j40\ \Omega$
- $|Z|=\sqrt{30^2+40^2}=50\ \Omega$, phase $\arctan(-40/30)=-53.1^\circ$ (capacitive — typical of an electrically short whip).
- Admittance: $Y=\dfrac{30+j40}{30^2+40^2}=0.012+j0.016$ S, i.e. $G=12$ mS, $B=+16$ mS. (Note $1/G=83.3\ \Omega\ne30\ \Omega$.)
- The series reactance −40 Ω is equivalent to $C=1/(2\pi\cdot433.92\text{ MHz}\cdot40)=9.17$ pF.
- A **series inductor** of $40/(2\pi\cdot433.92\text{ MHz})=14.7$ nH cancels it and leaves a pure 30 Ω.
- The **parallel** equivalent is $R_p=83.3\ \Omega$ in parallel with $X_p=-62.5\ \Omega$ (5.87 pF). A **shunt inductor** of $62.5/(2\pi f)=22.9$ nH would instead cancel the susceptance and leave 83.3 Ω. Which you choose depends on whether you then need to transform 30 Ω or 83 Ω to 50 Ω — this is exactly how an L-match is designed.

### 3. Series ↔ parallel for a high-Q inductor
A 22 nH chip inductor at 433.92 MHz has $X=60.0\ \Omega$. If its Q is 50, its series loss resistance is $R_s=60/50=1.2\ \Omega$. The parallel model is $R_p=1.2(1+2500)=3001\ \Omega$ in parallel with $X_p=60.0(1+1/2500)=60.02\ \Omega$. So a "lossy inductor" in a tank circuit behaves like an ideal 22 nH with a 3 kΩ resistor across it — the number used when computing loaded Q ([resonance and Q](resonance-and-q.md)).

### 4. Series RLC at 434 MHz
$R=2\ \Omega$, $L=22$ nH, $C=6.1$ pF resonate at $f_0=1/(2\pi\sqrt{LC})=434.4$ MHz. The script gives $Z=2-j90.1\ \Omega$ at $f_0/2$, $2-j12.7\ \Omega$ at $0.9f_0$, exactly $2\ \Omega$ at $f_0$, and $2+j90.1\ \Omega$ at $2f_0$: capacitive below resonance, inductive above.

## Practical notes
- **Usable value ranges at UHF.** Below roughly 1 nH or 0.5 pF, pads, vias and traces contribute as much as the part, so values are set by layout, not by the BOM. Above ~100 nH (inductors) or ~100 pF (capacitors) at 433–915 MHz, parts approach their self-resonance. Designs that need 0.3 pF or 0.7 nH at 2.4 GHz are layout-sensitive and should be tuned on the board ([PCB parasitics](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md)).
- **Tolerances matter more than at audio.** A ±0.25 pF tolerance on a 2.2 pF part is ±11 %; a matching network with a 1.5 pF shunt at 915 MHz shifts noticeably with ±0.1 pF. RF-grade C0G parts come in ±0.05 pF (W) and ±0.1 pF (B) tolerances.
- **Reference planes.** When a datasheet (e.g. a LoRa module) says the RF pin is "50 Ω", it means the impedance at the pad is designed to be 50 Ω, *not* that a trace of any length is harmless. The trace from pin to antenna connector should itself be a 50 Ω transmission line ([planar lines](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md)).
- **Measurement.** A NanoVNA/LibreVNA measures $S_{11}$ and converts to $Z=Z_0(1+\Gamma)/(1-\Gamma)$; the displayed "equivalent L or C" is simply $X/\omega$ or $-1/(\omega X)$ at each frequency — a real part changes with frequency in a way no single L or C does ([VNA fundamentals](../17-test-measurement/vna-fundamentals-calibration.md)).

## Common mistakes & misconceptions
- **Prefix slips** (mA vs µA, nF vs pF): an error of 1000×. Write the exponents out when in doubt.
- **Forgetting that a divider is loaded** by whatever it drives (an ADC input, a transistor base); its output is the Thevenin voltage only into an open circuit.
- **Sizing a resistor by resistance only**: check $P = I^2R$ against its rating, with margin, and its pulse rating.
- **"Capacitor reactance is positive."** With $Z=R+jX$, a capacitor has *negative* $X$. Many calculators print $|X_C|$; keep the sign when summing reactances or you will "cancel" things that actually add.
- **Adding parallel impedances directly.** Parallel elements add as admittances. 50 Ω ∥ −j50 Ω is not $50-j50$; it is $25-j25\ \Omega$.
- **$G=1/R$ for a complex impedance.** Only when $X=0$. For $30-j40$, $G=12$ mS, not 33 mS.
- **Using a series↔parallel conversion across a band.** It is exact at one frequency only; a single parallel R, L model of a lossy inductor is wrong a factor of two in frequency away.
- **Forgetting $2\pi$.** $X_L=2\pi fL$, not $fL$ — an error of 6.28× that shows up as matching networks "off by a lot".
- **"A 100 nF capacitor is a short at RF."** Real capacitors are series-resonant; above the SRF (≈20 MHz for 100 nF 0402) they are inductors of ~0.4–0.6 nH plus mounting. At 915 MHz that is a few ohms of *inductive* reactance, which is fine for supply bypass but not what you want as a precise matching element.
- **Treating every trace as lumped.** A 30 mm "short" trace at 2.45 GHz is almost λ/2 on FR-4 and completely transforms the impedance at its end.

## How to simulate / verify
- `python3 tools/verify/circuits_impedance_basics.py` reproduces every number on this page (reactance table, Z↔Y, series↔parallel identities asserted to machine precision).
- `python3 tools/verify/s3_primer.py` §1 — the DC-basics numbers and an ngspice .op of the LED and divider examples.
- scikit-rf: build a one-port from an impedance array, e.g. `rf.Network(frequency=f, z=Z, z0=50)` then read `.s`, `.z`, or plot on a Smith chart.
- SPICE (LTspice/ngspice): `.ac dec 200 1e6 3e9` on an R-L-C network and plot `V(n)/I(V1)` to get impedance; use a 1 A AC current source into a node for a direct impedance probe ([SPICE](../16-simulation-tools/spice-circuit-simulation.md)).
- Bench: measure a chip inductor soldered on a short 50 Ω test fixture with a calibrated NanoVNA and compare the displayed L vs frequency with the datasheet — the rise near SRF is the parasitic capacitance showing itself.

## Open questions / gaps
- None at this level; the practical limits of "lumped" for specific PCB structures are treated quantitatively in [PCB parasitics](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md) and [quasi-static vs full-wave](../02-electromagnetics/quasi-static-vs-full-wave.md).

## Sources
1. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — §2.x phasors and impedance; §4.1 impedance and admittance of one-ports incl. Foster's theorem discussion. (textbook)
2. C. Bowick, J. Blyler, C. Ajluni, *RF Circuit Design*, 2nd ed., Newnes, 2008 — ch. 1 (components and reactance), ch. 4 (series/parallel conversion used for matching). (textbook)
3. J. B. Hagen, *Radio-Frequency Electronics: Circuits and Applications*, 2nd ed., Cambridge UP, 2009 — ch. 2–3 (impedance, resonant circuits, series–parallel equivalence). (textbook)
4. R. Ludwig, G. Bogdanov, *RF Circuit Design: Theory and Applications*, 2nd ed., Pearson, 2009 — ch. 1 (lumped vs distributed, RF behaviour of passive components). (textbook)
5. M. B. Steer, *Microwave and RF Design* (open textbook, NC State / LibreTexts), vol. I–IV, 2019–2026 — lumped elements, impedance and admittance conventions. https://eng.libretexts.org/Bookshelves/Electrical_Engineering/Electronics (textbook, open)
6. R. M. Foster, "A reactance theorem," *Bell System Technical Journal*, 3(2), 259–267, 1924 — monotonic reactance of lossless one-ports. (peer-reviewed)
7. Verification script: `tools/verify/circuits_impedance_basics.py` (this KB) — all numeric tables and examples.
8. BIPM, *The International System of Units (SI Brochure)*, 9th ed., 2019 — SI prefixes and unit definitions. (standard)
9. P. Horowitz, W. Hill, *The Art of Electronics*, 3rd ed., Cambridge 2015 — ch. 1 (voltage, current, Ohm's law, dividers, power). (textbook)
