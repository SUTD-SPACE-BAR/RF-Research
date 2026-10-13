---
title: Resonance and Q
domain: 01-circuit-theory
slug: resonance-and-q
tags: [resonance, quality-factor, unloaded-q, loaded-q, external-q, bandwidth, series-resonance, parallel-resonance, tank-circuit, insertion-loss, component-q, l-network]
prerequisites:
  - lumped-elements-impedance-admittance.md
  - ../00-math-foundations/complex-numbers-and-phasors.md
related:
  - energy-storage-and-reactive-power.md
  - passive-filter-design-prototypes.md
  - transient-and-step-response.md
  - transformers-coupled-inductors.md
  - ../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md
  - ../04-real-components-hf/capacitors-at-rf-mlcc.md
  - ../04-real-components-hf/inductors-at-rf.md
  - ../04-real-components-hf/crystals-and-resonators.md
  - ../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md
  - ../05-analog-electronics/oscillators.md
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Resonance and Q

## Questions this page answers
- What happens at resonance in a series and in a parallel LC circuit?
- What exactly is Q, and why are there so many definitions (energy, bandwidth, X/R)?
- What is the difference between unloaded Q, loaded Q and external Q?
- How is bandwidth related to Q?
- How do I convert a series-loss model to a parallel-loss model of a resonator?
- If my inductor has Q = 50 and my capacitor Q = 500, what is the Q of the tank?
- Why does a narrow filter made from chip inductors have so much insertion loss?
- What is the Q of an L-matching network and why does it set the match bandwidth?
- Why is the voltage across a resonant capacitor so much bigger than the input voltage?
- What is the group delay of a resonator?

## TL;DR
- Resonance: $\omega_0=1/\sqrt{LC}$. A **series** LC is a short (minimum impedance, equal to its loss $R$) at $\omega_0$; a **parallel** LC is an open (maximum impedance $R_p$). Characteristic reactance $X_0=\omega_0L=1/(\omega_0C)=\sqrt{L/C}$.
- **Q = 2π × (energy stored)/(energy lost per cycle)** $=\omega_0 W/P_{loss}$. For a series resonator $Q=X_0/R_s$; for a parallel resonator $Q=R_p/X_0$. **3-dB bandwidth $=f_0/Q$** (verified numerically).
- **Loaded Q**: $1/Q_L=1/Q_u+1/Q_e$ — internal losses ($Q_u$, unloaded) and external loading ($Q_e$, source and load) add as parallel conductances.
- Tank $Q_u$ is limited by the worst component: $1/Q_u=1/Q_{L}+1/Q_{C}$. Chip inductors (Q ≈ 30–100 at UHF) usually dominate; C0G capacitors (Q in the hundreds to thousands) rarely do.
- **Insertion loss of one resonator at centre $=-20\log_{10}(1-Q_L/Q_u)$**: 0.9 dB at $Q_L/Q_u=0.1$, 3.1 dB at 0.3, 6 dB at 0.5. Narrow filters from low-Q parts are lossy — use SAW/ceramic/cavity parts for narrow bandwidths ([RF filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md)).
- An **L-match** between $R_{hi}$ and $R_{lo}$ has node $Q_n=\sqrt{R_{hi}/R_{lo}-1}$; its 3-dB bandwidth is ≈ $2f_0/Q_n$ for $Q_n\gtrsim5$ (wider for small $Q_n$).
- At resonance the reactive voltages (series) or currents (parallel) are **Q times** the drive — a real hazard for capacitor voltage ratings ([energy and reactive power](energy-storage-and-reactive-power.md)).
- Group delay of a single resonator at centre $\tau=2Q_L/\omega_0$ (5.2 ns for $Q_L=7.1$ at 433.92 MHz).

## Intuition (no math)
A resonator is a system that sloshes energy back and forth between two stores — the electric field of a capacitor and the magnetic field of an inductor — like a pendulum trading potential and kinetic energy. At one particular frequency the slosh is self-sustaining: the capacitor discharges into the inductor exactly in time for the inductor to recharge the capacitor with the opposite polarity. Drive it at that frequency and even a small push each cycle builds a big oscillation, limited only by the losses.

**Q** measures how many cycles the energy survives. A high-Q resonator is a heavy, well-oiled pendulum: once swinging it keeps going for many cycles, and it only responds strongly to pushes at exactly its natural rhythm (narrow bandwidth). A low-Q resonator is a pendulum in treacle: it stops quickly and responds sluggishly to a broad range of pushing rates.

Energy leaks out of a real resonator by two routes: it is burned inside (wire resistance, dielectric loss — the *unloaded* Q) and it is deliberately extracted by whatever the resonator is connected to (the source and the load — the *external* Q). The *loaded* Q, which sets the bandwidth you actually see, combines both. The fraction that goes out usefully versus the fraction burned inside is what sets the insertion loss.

## The math

### Level 1 — resonant frequency, Q and bandwidth

For ideal $L$ [H] and $C$ [F]: $\omega_0=1/\sqrt{LC}$, $f_0=\omega_0/2\pi$. At $\omega_0$, $|X_L|=|X_C|=X_0=\sqrt{L/C}$ [Ω].

| | Series RLC (loss $R_s$ in series) | Parallel RLC (loss $R_p$ in parallel) |
|---|---|---|
| Impedance at $\omega_0$ | $Z=R_s$ (minimum) | $Z=R_p$ (maximum) |
| $Q$ | $X_0/R_s=\dfrac{1}{R_s}\sqrt{\dfrac LC}$ | $R_p/X_0=R_p\sqrt{\dfrac CL}$ |
| Reactive magnification | $|V_C|=|V_L|=Q\,|V_{in}|$ | $|I_C|=|I_L|=Q\,|I_{in}|$ |
| 3-dB bandwidth | $\Delta f=f_0/Q$ | $\Delta f=f_0/Q$ |

### Level 2 — derivations

**Series RLC impedance** near resonance: $Z(\omega)=R_s+j\left(\omega L-\dfrac{1}{\omega C}\right)=R_s\left[1+jQ\left(\dfrac{\omega}{\omega_0}-\dfrac{\omega_0}{\omega}\right)\right]$.
Define the fractional detuning $\delta=(\omega-\omega_0)/\omega_0$; for small $\delta$, $\omega/\omega_0-\omega_0/\omega\approx2\delta$, so $Z\approx R_s(1+j2Q\delta)$. Driven by a voltage source, $|I|^2\propto1/(1+4Q^2\delta^2)$, which falls to half at $\delta=\pm1/(2Q)$. Hence the full 3-dB bandwidth is $2\cdot\omega_0/(2Q)=\omega_0/Q$. The parallel case is the dual (admittance $Y\approx G_p(1+j2Q\delta)$).

**Energy definition.** In a series resonator carrying peak current $I$ at $\omega_0$, total stored energy is constant, $W=\tfrac12LI^2$ (it flows between L and C without change of total), and average dissipated power is $P=\tfrac12I^2R_s$. So
$$Q\equiv\omega_0\frac{W_{stored}}{P_{loss}}=\frac{\omega_0L}{R_s}.$$
This definition is the general one: it applies to cavities, crystals, antennas, dielectric resonators and transmission-line resonators, where no single "R" exists. The bandwidth definition $Q=f_0/\Delta f$ agrees with it only for an isolated, single, high-Q resonance.

**Unloaded, external and loaded Q.** Represent the resonator's internal loss by $G_u$ and the external loading (source and load resistances, transformed to the resonator terminals) by $G_e$. All are in parallel across the same tank:
$$Q_u=\frac{1}{X_0G_u},\qquad Q_e=\frac{1}{X_0G_e},\qquad Q_L=\frac{1}{X_0(G_u+G_e)}\ \Rightarrow\ \frac1{Q_L}=\frac1{Q_u}+\frac1{Q_e}.$$
With separate source and load, $1/Q_e=1/Q_{e,src}+1/Q_{e,load}$. For the example in `tools/verify/circuits_resonance_q.py` (22 nH, Q = 50, i.e. $R_p=3.0$ kΩ, loaded by 1 kΩ source and 1 kΩ load): $Q_u=50$, $Q_e=8.34$, $Q_L=7.14$, bandwidth 60.7 MHz, matching the numerical sweep.

**Insertion loss of a resonator.** For a single parallel resonator between equal source and load conductances $G$ (so $G_e=2G$), the transfer at resonance relative to the available power is
$$\frac{P_L}{P_{av}}=\frac{4G^2}{(2G+G_u)^2}=\left(\frac{2G}{2G+G_u}\right)^2=\left(1-\frac{Q_L}{Q_u}\right)^2,$$
so $IL=-20\log_{10}(1-Q_L/Q_u)$ dB. Numerically 1.339 dB for $Q_L/Q_u=0.143$ (script §3). Multi-resonator filters generalise this: mid-band loss grows roughly as $\sum_k 4.343\,g_k\,\omega_c'/(\text{FBW}\cdot Q_{u,k})$ dB ([filter prototypes](passive-filter-design-prototypes.md)).

**Series ↔ parallel loss conversion.** $R_p=R_s(1+Q^2)\approx Q^2R_s$ ([lumped elements](lumped-elements-impedance-admittance.md)). A 22 nH inductor with Q = 50 at 433.92 MHz has $R_s=1.20\ \Omega$ or equivalently $R_p=3.0$ kΩ.

**Component Q.** Each lossy element contributes its own loss conductance across the tank, so $1/Q_u=\sum_k 1/Q_k$. For L-Q = 50 and C-Q = 500, $Q_u=45.5$; for L-Q = 50 and C-Q = 100, $Q_u=33.3$.

### Level 3 — generalisations and limits

- **L-network (matching) Q.** Transforming $R_{lo}$ up to $R_{hi}$ with a series reactance $X_s$ and a shunt reactance $X_p$ requires $X_s=Q_nR_{lo}$, $X_p=R_{hi}/Q_n$ with $Q_n=\sqrt{R_{hi}/R_{lo}-1}$ (the series→parallel conversion run backwards). When matched, the source resistance equals the transformed load, so the loaded Q is ≈ $Q_n/2$ and the 3-dB bandwidth ≈ $2f_0/Q_n$. The script checks this: 50→0.5 Ω ($Q_n=9.95$) gives 20.3 % vs 20.1 % predicted; 50→5 Ω ($Q_n=3$) gives 76 % vs 67 % — the approximation weakens for $Q_n\lesssim3$. Higher transformation ratios force higher $Q$ and narrower bandwidth; multi-section (Pi, T, ladder) networks let you choose $Q$ independently ([matching](../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md)).
- **Frequency-dependent loss.** Conductor loss rises as $\sqrt f$ (skin effect), dielectric loss as $f\tan\delta$, so component Q is a function of frequency. Chip-inductor Q typically rises, peaks well below SRF, and collapses near SRF ([inductors at RF](../04-real-components-hf/inductors-at-rf.md)).
- **Group delay.** Near resonance the phase of a resonator's transfer function is $-\arctan(2Q_L\delta)$, so group delay at centre is $\tau=2Q_L/\omega_0$ (5.24 ns for $Q_L=7.14$ at 433.92 MHz, verified). Narrow filters have long delays and delay peaks at band edges.
- **Transient view.** A resonator released from an initial state rings with an amplitude envelope $e^{-\omega_0t/(2Q)}$ and an energy envelope $e^{-\omega_0t/Q}$: the amplitude falls to $1/e$ in $Q/\pi$ cycles and the energy in $Q/(2\pi)$ cycles ([transients](transient-and-step-response.md)).
- **Coupled resonators** split into two modes whose separation is set by the coupling coefficient $k$; this is the basis of band-pass filter synthesis ([transformers and coupled inductors](transformers-coupled-inductors.md)).
- **Crystals and SAW/BAW resonators** are mechanical resonators with Q of $10^4$–$10^6$ and $10^3$ respectively; their electrical equivalent is still an RLC with a shunt capacitance ([crystals](../04-real-components-hf/crystals-and-resonators.md)).

## Design equations & rules of thumb

| Quantity | Equation | Valid when | Typical |
|---|---|---|---|
| Resonant frequency | $f_0=1/(2\pi\sqrt{LC})$ | lumped, below SRF of parts | 22 nH + 6.12 pF → 433.92 MHz |
| Q (general) | $Q=\omega_0W/P$ | any resonator | — |
| Series / parallel Q | $X_0/R_s$ / $R_p/X_0$ | single RLC | — |
| Bandwidth | $\Delta f_{3dB}=f_0/Q_L$ | isolated resonance, $Q\gtrsim5$ | $Q_L=7.1$ at 433.92 MHz → 61 MHz |
| Loaded Q | $1/Q_L=1/Q_u+1/Q_e$ | — | — |
| Single-resonator IL | $-20\log_{10}(1-Q_L/Q_u)$ | resonance, symmetric loading | 0.9 dB at $Q_L/Q_u=0.1$ |
| Tank $Q_u$ | $1/Q_u=1/Q_L+1/Q_C$ | — | chip L Q ≈ 30–100 at UHF dominates |
| L-match Q | $Q_n=\sqrt{R_{hi}/R_{lo}-1}$ | — | 50→5 Ω: 3.0 |
| L-match BW | ≈ $2f_0/Q_n$ | $Q_n\gtrsim5$ | 50→0.5 Ω: ≈20 % |
| Group delay | $\tau=2Q_L/\omega_0$ | single resonator, centre | — |
| Reactive magnification | $V_C=QV_{in}$ (series) | at resonance | Q = 50, 1 V → 50 V |

## Worked examples

### 1. A 433.92 MHz series trap
22 nH (Q = 50 at 433.92 MHz → $R_s=1.20\ \Omega$) in series with 6.115 pF. $X_0=59.98\ \Omega$, $Q=50.0$, $\Delta f=8.68$ MHz. Used as a shunt notch across a 50 Ω line, it presents 1.2 Ω at 433.92 MHz → notch depth $20\log_{10}(1.2/(1.2+25))\approx-26.8$ dB (50 Ω source ∥ 50 Ω load = 25 Ω). A trap for the **second harmonic** of a 433 MHz PA (867.8 MHz) would use ~11 nH and 3.06 pF — but at 868 MHz the inductor's Q and the capacitor's SRF must be checked.

### 2. A band-pass tank at 433.92 MHz between 1 kΩ terminations
Same 22 nH (Q = 50) and 6.115 pF in parallel; source and load presented at 1 kΩ each (via taps or transformers, see [transformers](transformers-coupled-inductors.md)). $Q_L=7.14$, $\Delta f=60.7$ MHz, insertion loss 1.34 dB, group delay 5.24 ns. To narrow the bandwidth to 10 MHz you need $Q_L=43$, i.e. $Q_L/Q_u=0.87$ → **IL = 17.6 dB**. This is why you cannot build a 10 MHz-wide 433 MHz filter from chip inductors; a SAW filter does it with ~2 dB loss.

### 3. Tank Q from datasheets
Coilcraft 0402HP-22N has typical Q = 60 at 900 MHz and 74 at 1.7 GHz (datasheet table). Its Q is still rising with frequency below 1 GHz, so at 433 MHz it is lower — reading the typical Q-vs-frequency curve gives roughly 45 (approximate). A Murata GJM C0G capacitor of a few pF has Q in the several hundreds at UHF (see [capacitors](../04-real-components-hf/capacitors-at-rf-mlcc.md)). Combined $Q_u\approx1/(1/45+1/500)=41$ — the inductor dominates.

### 4. L-match Q for a 2 W PA
Transforming 50 Ω to 5 Ω ([max power transfer](network-theorems-max-power-transfer.md)): $Q_n=3.0$, bandwidth ~70 % — broad enough that component tolerance barely matters. Transforming 50 Ω to 0.5 Ω (a 20 W PA at 3.3 V) needs $Q_n\approx10$, bandwidth ≈20 %, and currents of several amps in the series element — that is where multi-section networks and low-loss parts are required.

## Practical notes
- **Measure Q in-circuit, not just from datasheets.** Datasheet Q is for the bare part in a specific fixture; pads, vias, solder and nearby copper add loss and capacitance. A two-port "weakly coupled" measurement of $S_{21}$ bandwidth (loosely coupled so $Q_L\approx Q_u$) is the standard method ([VNA](../17-test-measurement/vna-fundamentals-calibration.md)).
- **Tuning.** A resonator with $Q_L=40$ at 433 MHz has a bandwidth of 11 MHz; a ±2 % capacitor tolerance moves $f_0$ by ±1 % (±4.3 MHz) — a significant fraction of the band. Use tight tolerance C0G (±0.05–0.1 pF) or plan a trimmer.
- **Temperature.** C0G capacitors drift ≤±30 ppm/°C; chip inductors +25 to +125 ppm/°C (Coilcraft 0402HP TCL). Over 80 °C that is < 1 % of $f_0$ — negligible for broad matching networks, significant for narrow filters.
- **Magnetic coupling between nearby resonators** (two chip inductors side-by-side) turns independent resonators into coupled ones — orient them at 90° or separate them.

## Common mistakes & misconceptions
- **"Q is X/R."** Only for a single element or a single series/parallel RLC. The general definition is energy-based; bandwidth-Q equals energy-Q only for an isolated high-Q resonance.
- **Using unloaded Q to predict bandwidth.** Bandwidth is set by the loaded Q; a Q = 50 inductor in a 50 Ω-loaded tank may give $Q_L\approx1$.
- **"Higher Q is always better."** Higher $Q_L$ gives narrower bandwidth and more sensitivity to tolerances; in matching networks you usually want the *lowest* Q that achieves the transformation. It is high *unloaded* Q that is always better (lower loss).
- **Ignoring the reactive magnification.** A series-resonant matching network driven with 2 W can put tens to hundreds of volts across a small capacitor ([energy page](energy-storage-and-reactive-power.md)).
- **Confusing SRF with the circuit's resonance.** A component's self-resonant frequency is a parasitic resonance; operating a part near its SRF makes its effective value strongly frequency dependent.

## How to simulate / verify
- `python3 tools/verify/circuits_resonance_q.py` — numerically checks $\Delta f=f_0/Q$ (series and parallel), energy Q, loaded Q, insertion loss formula, group delay and L-match bandwidth.
- SPICE `.ac` sweep of the tank between its terminations; measure $-3$ dB points; compare with $f_0/Q_L$.
- scikit-rf: build the tank from `rf.media.DefinedGammaZ0(...).inductor/capacitor/resistor` elements, cascade and read `s21`; see the filter script `tools/verify/circuits_filter_prototypes.py` for a complete example.

## Open questions / gaps
- Measured in-circuit Q of common JLCPCB-available chip inductors at 433/915 MHz is not documented here; worth a bench campaign (see [inductors at RF](../04-real-components-hf/inductors-at-rf.md)).

## Sources
1. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — §6.1 series and parallel resonant circuits, loaded and unloaded Q, external Q; §8.8 filters using coupled resonators. (textbook)
2. C. Bowick, *RF Circuit Design*, 2nd ed., Newnes, 2008 — ch. 2 (resonant circuits, loaded Q, insertion loss), ch. 4 (L-network Q and bandwidth). (textbook)
3. J. B. Hagen, *Radio-Frequency Electronics*, 2nd ed., Cambridge UP, 2009 — ch. 3 (resonant circuits, Q, coupling). (textbook)
4. W. Hayward, R. Campbell, B. Larkin, *Experimental Methods in RF Design*, ARRL, 2003 — ch. 3 and 7 (resonator Q measurement, IL vs Q of filters). (textbook)
5. G. L. Matthaei, L. Young, E. M. T. Jones, *Microwave Filters, Impedance-Matching Networks, and Coupling Structures*, McGraw-Hill, 1964 (Artech reprint) — §4.13 dissipation loss vs unloaded Q. (textbook)
6. Coilcraft, "Chip inductors — 0402HP series (1005)", Document 526, rev. 12/20/2023 — Q vs frequency, TCL. https://www.coilcraft.com/getmedia/54459dcc-b821-4a9d-b91e-0416ea86a9b2/0402hp.pdf (datasheet)
7. Verification script `tools/verify/circuits_resonance_q.py` (this KB).
