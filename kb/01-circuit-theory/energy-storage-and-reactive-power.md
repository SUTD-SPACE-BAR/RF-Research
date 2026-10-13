---
title: Energy storage and reactive power
domain: 01-circuit-theory
slug: energy-storage-and-reactive-power
tags: [complex-power, reactive-power, power-factor, stored-energy, var, tank-voltage, circulating-current, capacitor-voltage-rating, component-stress, matching-network, loop-antenna]
prerequisites:
  - lumped-elements-impedance-admittance.md
  - resonance-and-q.md
  - network-theorems-max-power-transfer.md
related:
  - passive-filter-design-prototypes.md
  - transient-and-step-response.md
  - ../02-electromagnetics/poynting-vector-power-flow.md
  - ../04-real-components-hf/capacitors-at-rf-mlcc.md
  - ../04-real-components-hf/inductors-at-rf.md
  - ../08-antennas/loop-antennas.md
  - ../08-antennas/small-antenna-limits.md
  - ../06-rf-circuits/power-amplifiers.md
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Energy storage and reactive power

## Questions this page answers
- What are real, reactive and apparent power, and what does "var" mean?
- What is power factor, and does it matter in RF circuits?
- How much energy is stored in an inductor or capacitor, and how does that relate to reactive power?
- Why can the voltage across a capacitor in a matching network be much higher than the RF voltage on the 50 Ω line?
- How do I check capacitor voltage and inductor current ratings for a 2 W LoRa transmitter's matching network or filter?
- Why does a small tuned loop antenna need a high-voltage capacitor?
- Where does reactive power "go"? Does it heat anything?

## TL;DR
- Complex power with peak phasors: $S=\tfrac12VI^*=P+jQ$ [VA]. $P$ [W] is dissipated/delivered; $Q$ [var] is energy sloshing in and out of fields each cycle; $|S|$ is apparent power; power factor $\mathrm{PF}=P/|S|=\cos\phi$.
- Stored energies (time-average): $W_m=\tfrac14L|I|^2$, $W_e=\tfrac14C|V|^2$. **$Q=2\omega(W_m-W_e)$** — inductive networks have $Q>0$, capacitive $Q<0$; at resonance $W_m=W_e$ and $Q=0$ at the terminals even though each element holds lots of energy.
- Reactive power in an element: $Q_L=\tfrac12|I|^2X_L$, $Q_C=\tfrac12|V|^2/X_C$. **In an L-match each reactive element carries $Q_n\times P$ vars** (verified): 2 W through a 50→5 Ω match at 433.92 MHz puts 6 var in each element; 20 W through 50→0.5 Ω puts 199 var and ~9 A peak through a 1.8 nH series inductor.
- **Tank voltage ∝ √(Q·P·X):** a small tuned loop antenna (50 nH, 0.5 Ω total loss) at 2 W and 433.92 MHz has Q ≈ 270, **2.8 A loop current and ≈390 V peak across a 2.7 pF tuning capacitor**. Standard 50 V 0402 C0G parts will arc.
- Inside a harmonic LPF at 2 W the branch voltages exceed the 14.1 V line voltage (up to **23.8 V peak** across a trap in the 5th-order elliptic design) — rate capacitors ≥ 50 V and check trap currents (0.4–0.5 A peak).
- Reactive power itself heats nothing; the *currents* it implies heat the element ESRs: $P_{loss}=Q_{element}/Q_{component}$ (e.g. 6 var in an inductor of Q = 50 → 0.12 W).

## Intuition (no math)
In a resistor, energy flows one way: from the source into heat. In an inductor or capacitor, energy flows *in* for a quarter-cycle, is stored in the field, and flows *back out* the next quarter-cycle. On average nothing is consumed, but current still has to flow to carry that energy back and forth. **Reactive power** is the size of that to-and-fro flow. It is "power" in the sense of energy per unit time, but it does no net work.

In a resonant circuit the inductor and capacitor trade energy with *each other*: while the inductor is releasing energy the capacitor is absorbing it. The source only has to top up the small loss each cycle. So a high-Q tank holds far more energy than it receives per cycle — Q times more (energy definition of Q, see [resonance and Q](resonance-and-q.md)). Large stored energy in a small capacitor means a large voltage ($W=\tfrac12CV^2$); in a small inductor it means a large current. That is why high-Q matching networks, traps and small antennas stress components well beyond what the "2 W into 50 Ω" figure suggests.

## The math

### Level 1 — definitions
With peak phasors $V$ and $I$ at one port:
$$S=\tfrac12VI^*=P+jQ,\qquad P=\tfrac12|V||I|\cos\phi,\qquad Q=\tfrac12|V||I|\sin\phi,$$
$\phi=\angle V-\angle I$ (positive for inductive loads). For an impedance $Z=R+jX$: $P=\tfrac12|I|^2R$, $Q=\tfrac12|I|^2X$. Units: W, var (volt-ampere reactive), VA. With rms phasors drop the ½.

Element energies (instantaneous): $w_L=\tfrac12Li^2$, $w_C=\tfrac12Cv^2$. Their time averages in sinusoidal steady state are $W_m=\tfrac14L|I|^2$ and $W_e=\tfrac14C|V_C|^2$ (peak phasors), with peak stored energy twice the average.

### Level 2 — the complex Poynting (Tellegen) balance
For any network, the complex power delivered by the sources equals the sum over elements of $\tfrac12V_kI_k^*$ (Tellegen's theorem). Grouping elements:
$$S_{source}=P_{loss}+2j\omega\,(W_m-W_e).$$
So a one-port's input reactance is set by the *imbalance* of magnetic and electric energy: $X_{in}=\dfrac{4\omega(W_m-W_e)}{|I|^2}$ and $R_{in}=\dfrac{2P_{loss}}{|I|^2}$. This is the circuit form of the complex Poynting theorem ([Poynting vector](../02-electromagnetics/poynting-vector-power-flow.md)) and it is how cavities and antennas are analysed. Verified numerically (script §1–2) for a series RLC at 433.92 MHz: $S=1.196-j0.750$ VA equals the element sum, and $2\omega(W_m-W_e)=-0.750$ var.

**Q as an energy ratio**, restated: $Q=\omega_0\,W_{stored}/P_{loss}$ where at resonance $W_{stored}=2W_m=2W_e$ (time-average total). Hence the **reactive power in each element of a resonator is Q times the real power** it passes or dissipates.

### Level 3 — component stress in real RF networks

**L-match stress.** For an L-section transforming $R_{lo}$ to $R_{hi}$ with node $Q_n=\sqrt{R_{hi}/R_{lo}-1}$ and delivering power $P$:
$$I_{series,pk}=\sqrt{2P/R_{lo}},\quad V_{shunt,pk}=\sqrt{2PR_{hi}},\quad Q_{series}=Q_{shunt}=Q_nP.$$
The script confirms $Q_L=Q_C=Q_nP$ exactly. Consequences:

| Case | $Q_n$ | Series L, current | Shunt C, voltage | var per element |
|---|---|---|---|---|
| 2 W, 433.92 MHz, 50→5.06 Ω | 2.98 | 5.53 nH, 0.89 A pk (0.63 A rms) | 21.9 pF, 14.1 V pk | 5.96 |
| 1 W, 915 MHz, 50→12.5 Ω | 1.73 | 3.77 nH, 0.40 A pk | 6.03 pF, 10.0 V pk | 1.73 |
| 20 W, 433.92 MHz, 50→0.5 Ω | 9.95 | 1.82 nH, 8.94 A pk (6.3 A rms) | 73.0 pF, 44.7 V pk | 199 |

**Loss from reactive power.** An element of component quality $Q_c$ carrying reactive power $Q_{el}$ dissipates $P_{d}=Q_{el}/Q_c$. In the 2 W case, an inductor with $Q_c=50$ burns 0.12 W (0.26 dB of the 2 W), a C0G capacitor with $Q_c=500$ only 12 mW. In the 20 W case the inductor would burn ~4 W — which is why high-power, low-impedance matching uses air-wound or strip inductors and porcelain/high-Q capacitors (ATC, Johanson).

**Filter internals.** Terminal voltages alone do not bound internal voltages. In the 5th-order elliptic 433.92 MHz LPF of [filter prototypes](passive-filter-design-prototypes.md), at 2 W: shunt capacitors see 14.1–17.6 V peak, but the parallel L∥C trap branches see 19.1 and **23.8 V peak**, with 0.42–0.43 A peak in the trap inductors (script §4). At the trap's own resonance (2f) the circulating current is Q-times the (small) harmonic current, which is harmless unless the harmonic is strong.

**Small antennas.** An electrically small loop or tuned whip has a small radiation resistance and a large reactance, so its matched Q is high (bounded below by the Chu limit, [small antenna limits](../08-antennas/small-antenna-limits.md)). With $L=50$ nH ($X=136\ \Omega$ at 433.92 MHz), $R_{rad}=0.1\ \Omega$, $R_{loss}=0.4\ \Omega$: $Q=273$, loop current $\sqrt{2P/R}=2.83$ A peak at 2 W, tuning capacitor 2.69 pF with **386 V peak** across it; radiation efficiency only 20 %. ([Loop antennas](../08-antennas/loop-antennas.md).)

**Voltage ratings and RF.** Capacitor DC voltage ratings do not directly equal RF ratings: at RF the limits are (a) dielectric breakdown/surface flash-over (peak voltage), and (b) self-heating from $I^2\cdot$ESR (current rating, often given in vendor charts like the Johanson "max current" curves that fall with frequency). Use peak RF voltage ≤ ~50 % of the rated DC voltage for margin, and check the current/power curves ([capacitors at RF](../04-real-components-hf/capacitors-at-rf-mlcc.md)).

## Design equations & rules of thumb

| Quantity | Equation | Notes |
|---|---|---|
| Complex power | $S=\tfrac12VI^*$ | peak phasors |
| Power factor | $P/|S|=\cos\phi$ | rarely used in RF; VSWR/Γ used instead |
| Stored energy | $W_m=\tfrac14L|I|^2$, $W_e=\tfrac14C|V|^2$ | time averages |
| Input reactance | $X=4\omega(W_m-W_e)/|I|^2$ | Tellegen/Poynting |
| Element reactive power | $Q_n\cdot P$ in L-match | — |
| Element loss | $P_d=Q_{el}/Q_{component}$ | — |
| Line voltage, 50 Ω | $V_{pk}=\sqrt{2PZ_0}$ | 2 W → 14.1 V; 1 W → 10 V; 100 mW → 3.2 V |
| Tuned small antenna | $V_C=\sqrt{2P/R}\,X$ | can be hundreds of volts |
| Mismatched line peak | $V_{max}=\sqrt{2PZ_0}\,(1+|\Gamma|)/\sqrt{1-|\Gamma|^2}$ (for delivered P) | see [reflections](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md) |

## Worked examples

### 1. Checking parts for a 2 W 433 MHz PA output network
Series 5.53 nH carrying 0.63 A rms: choose an inductor with Irms ≥ 1 A (the Coilcraft 0402HP-5N6 is rated 1.6 A Irms for a 15 °C rise; the family spans 0.16–2.3 A depending on value — check the specific part). Shunt 21.9 pF at 14.1 V peak: an 0402 C0G rated 50 V is adequate (28 % of rating). If the antenna is disconnected (|Γ| → 1), voltages near the PA can nearly double — rate for ≥ 30 V peak.

### 2. How much power does the matching inductor waste?
Reactive power 5.96 var; with inductor Q = 50 at 433 MHz the loss is 0.12 W = 6 % of 2 W (0.26 dB). With a Q = 25 multilayer inductor, 0.24 W (0.54 dB) — and the part runs hot. Output-stage inductors are where Q matters most.

### 3. A tuned PCB loop on a rocket airframe
Numbers as in Level 3: 386 V peak at 2 W. Mitigations: use a larger loop (higher $R_{rad}$, lower Q), a capacitor rated ≥ 500 V RF (porcelain/ATC 100B-class or a PCB/air-gap capacitor), or reduce power; also note the 20 % efficiency. A resonant half-wave or quarter-wave antenna avoids the problem.

## Practical notes
- **Where to look for trouble:** series-resonant elements (current), shunt elements in high-impedance nodes (voltage), traps, small antennas, and any network with Q ≳ 5.
- **Hot spots:** a matching inductor that browns on the board after a few long transmissions is carrying more reactive power than its Q can handle.
- **Mismatch** raises internal stress unpredictably; test the transmitter into short and open loads at low duty cycle to see whether any part arcs or overheats (with appropriate PA protection).
- **LoRa duty cycle** helps thermally (long off times), but voltage breakdown is instantaneous — rate for peak, not average.

## Common mistakes & misconceptions
- **"Reactive power is wasted power."** It is not dissipated; it is energy exchange. Its cost is the extra current (and hence $I^2R$ loss in ESRs) needed to carry it.
- **"At resonance there is no reactive power."** At the *terminals* $Q=0$; inside, each element carries Q times the real power.
- **"2 W into 50 Ω means 14 V everywhere."** Internal nodes of filters and matching networks can exceed the line voltage, and small antennas can reach hundreds of volts.
- **Using DC voltage ratings for RF without derating** or ignoring current (self-heating) ratings at high frequency.
- **Mixing peak and rms** — a factor of two in power and √2 in voltage; SPICE and most RF formulas use peak phasors unless told otherwise.

## How to simulate / verify
- `python3 tools/verify/circuits_reactive_power.py` — complex power balance, $Q=2\omega(W_m-W_e)$, L-match stresses ($Q_{el}=Q_nP$), internal voltages/currents of the elliptic LPF at 2 W, and the loop-antenna capacitor voltage.
- SPICE `.ac` with a source set to the correct peak amplitude; probe element voltages and currents directly; for harmonic content use `.tran` or harmonic balance ([RF simulators](../16-simulation-tools/rf-circuit-simulators-harmonic-balance.md)).
- Bench: thermal camera on matching components during a long transmit; a small current probe or a temperature-rise test for inductors.

## Open questions / gaps
- RF current/voltage ratings for common JLCPCB 0402/0603 C0G parts are rarely published; vendor curves (Johanson, ATC, Murata GJM power data in SimSurfing) should be consulted per part (cross-link to 18-components-parts).

## Sources
1. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — §1.6 (complex Poynting theorem), §2.x and §4.1 (input impedance from stored energies and loss), §6.1 (Q and stored energy). (textbook)
2. B. D. H. Tellegen, "A general network theorem, with applications," *Philips Research Reports*, 7, 259–269, 1952. (peer-reviewed/historical)
3. C. Bowick, *RF Circuit Design*, 2nd ed., Newnes, 2008 — ch. 4 (component stress in matching networks). (textbook)
4. S. C. Cripps, *RF Power Amplifiers for Wireless Communications*, 2nd ed., Artech House, 2006 — output-network losses vs Q. (textbook)
5. Johanson Technology, "Multi-layer high-Q capacitors" catalog (2022) — RF max-current vs frequency charts for R07S/R14S (thermal-resistance-based). https://www.johansontechnology.com/docs/2818/johanson-technology-multi-layer-high-q-capacitors8--4-2022_VRkwKZd.pdf (datasheet)
6. L. J. Chu, "Physical limitations of omni-directional antennas," *J. Appl. Phys.*, 19, 1163–1175, 1948 — minimum Q of small antennas. (peer-reviewed)
7. Verification script `tools/verify/circuits_reactive_power.py` (this KB).
