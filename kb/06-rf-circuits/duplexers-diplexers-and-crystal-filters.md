---
title: Duplexers, diplexers and crystal/ceramic IF filters — cavity and SAW/BAW duplexers, 433 + 915 MHz antenna sharing, crystal ladder design from motional parameters (Dishal/Cohn), monolithic and ceramic filters
domain: 06-rf-circuits
slug: duplexers-diplexers-and-crystal-filters
tags: [duplexer, diplexer, multiplexer, cavity-filter, notch-cavity, bpbr, repeater, saw-duplexer, baw, fdd, tdd, trap-diplexer, 433-mhz, 915-mhz, crystal-filter, ladder-filter, lattice-filter, lsb-ladder, dishal, cohn, k-q, motional-capacitance, g3uur, monolithic-crystal-filter, mcf, ceramic-filter, 10.7-mhz, 455-khz, shape-factor, ultimate-rejection, roofing-filter]
prerequisites:
  - rf-filters-lc-saw-baw-cavity-microstrip.md
  - ../01-circuit-theory/passive-filter-design-prototypes.md
  - ../04-real-components-hf/crystals-and-resonators.md
  - ../01-circuit-theory/resonance-and-q.md
related:
  - circulators-isolators.md
  - receiver-architectures.md
  - co-site-interference-and-transmitter-intermod.md
  - agc-loops-and-receiver-gain-control.md
  - ../08-antennas/multiband-and-wideband-antennas.md
  - ../18-components-parts/filter-parts-saw-ceramic-ltcc.md
  - ../15-lora-ism-radios/ground-station-design.md
  - ../20-projects-recipes/bandpass-filter-design-walkthrough.md
level: mixed
confidence: medium
last_updated: 2026-10-12
---

# Duplexers, diplexers and crystal/ceramic IF filters

## Questions this page answers
- What is the difference between a duplexer and a diplexer, and when do I need either?
- How does a repeater's cavity duplexer get 70–80 dB of isolation with only 5 MHz between transmit and receive?
- Can a cavity notch filter knock out another team's transmitter 600 kHz from my channel?
- How do I share one antenna between a 433 MHz and a 915 MHz LoRa radio on the rocket or at the ground station?
- What is a crystal ladder filter, and how do I design one from cheap microprocessor crystals?
- How do I measure a crystal's motional capacitance and inductance without a crystal tester?
- Why does my crystal filter come out narrower than designed, and why are its skirts lopsided?
- What are shape factor and ultimate rejection?
- When do I use a monolithic crystal filter or a ceramic 10.7 MHz / 455 kHz filter instead?

## TL;DR
- **A duplexer** lets a transmitter and receiver on *nearby* frequencies in the same band share an antenna at the same time (FDD). **A diplexer** splits *different bands* onto separate ports. A T/R switch does the job for half-duplex (TDD) radios like LoRa ([switches](rf-switches-attenuators-limiters.md)). A circulator separates directions at the *same* frequency, but only by about 20 dB ([circulators](circulators-isolators.md)).
- **Repeater budget:** a 25 W UHF repeater with −155 dBc/Hz transmitter noise at 5 MHz offset (assumed) and a 6 dB NF receiver in 12.5 kHz needs **≥ 67 dB** of isolation at the receive frequency (noise) and **≥ 74 dB** at the transmit frequency (carrier below −30 dBm). That matches commercial 6-cavity 440 MHz duplexers: 75–80 dB, 1.4–1.5 dB loss, 5–8 MHz split [5].
- **One notch cavity** (shunt series resonator, unloaded Q $Q_u$), sized for 0.3 dB loss at the pass frequency Δf away, gives a notch set by $R=X_{min}f_0/(2Q_u\Delta f)$. At $Q_u$ = 3000 and 5 MHz: **−26 dB**, so three cavities make ≈ 75 dB. At 0.58 MHz the same cavity manages only −10 dB. You cannot cavity-filter a launch-site neighbour a few hundred kHz away (simulated).
- **433 + 915 MHz on one antenna:** a crossover (complementary Butterworth) diplexer at 630 MHz gives only 16 dB at 5th order. A **trap diplexer** gives far more. Its 433 arm has a parallel LC resonant at 915 in series plus a resonating capacitor; its 915 arm has a parallel LC at 433 plus a resonating inductor; shunt traps sit at each port. With inductor Q 50: **0.14 / 0.22 dB loss, ≥ 40 dB cross-band rejection and isolation, ≥ 33 dB return loss**. An un-optimised analytic start gave 59–61 dB rejection with 0.3 dB loss. At ±5 % tolerance the 5th-percentile rejection is still 29 dB.
- **Crystal ladder (LSB ladder) by the k–q (Dishal) method:**
  - Coupling capacitors $C_{i,i+1}=C_m\,Q_F/k_{i,i+1}$ with $Q_F=f_0/BW$. End resistance $R_e=2\pi L_m\,BW/q$.
  - Tune every mesh to the highest mesh frequency with series capacitors.
  - A 4-pole 0.1 dB Chebyshev from 10 MHz crystals ($L_m$ 12 mH, $C_m$ 21.1 fF, $C_0$ 4.5 pF, Q 75 k) has $C_{12}$ ≈ 107 pF, $C_{23}$ ≈ 136 pF, $R_e$ ≈ 161 Ω, end tuning caps ≈ 135 pF.
  - Result: **2.40 kHz at −3 dB, 1.4 dB loss, shape factor 4.6**; ngspice agrees with the Python solver to < 0.001 dB.
  - $C_0$ narrowed the C0-free design by 14 %. The skirts are lopsided: 88 dB rejection 30 kHz below the passband, 157 dB above.
- **Motional capacitance by the G3UUR method:** $C_m=2\Delta f\,(C_0+C_s)/f$ from the frequency shift Δf when a series capacitor $C_s$ is switched in. It is within 0.02 % of exact (simulated).
- **Off-the-shelf IF filters:** Murata SFELF10M7FA00 is 10.7 MHz, 280 kHz at −3 dB, 330 Ω, 4 dB loss; CFWLA455KBFA is 455 kHz, ±15 kHz at −6 dB, 1.5 kΩ [8]. A handset band-8 TC-SAW duplexer offers about 55–60 dB TX–RX isolation at 1.5–1.9 dB loss [6].

## Intuition (no math)
A radio that transmits and receives *at the same time* on one antenna has to stop its own transmitter, typically 10–100 W, from reaching a receiver that is looking for signals of −120 dBm. That is a ratio of 160 dB or more. Two things leak across. The transmitter's carrier can overload the receiver. Less obviously, the transmitter's broadband *noise* also lands right on the receive frequency, where no receive filter can remove it, so it must be filtered on the transmit side. A duplexer is two filters: one passing transmit and stopping receive, one passing receive and stopping transmit. Their outputs join at the antenna, with line lengths chosen so each filter looks like an open circuit to the other's band.

When the two frequencies are close (5 MHz at 440 MHz is about 1 %), only very high-Q resonators can tell them apart. That means coaxial cavities the size of a drink can or bigger, or acoustic (SAW/BAW) resonators in a phone. When they are far apart (433 vs 915 MHz, a factor of two), a few lumped L and C elements suffice. That is a diplexer, and it is easy.

A **crystal filter** applies the same coupled-resonator theory as any band-pass filter ([RF filters](rf-filters-lc-saw-baw-cavity-microstrip.md)), but its resonators are quartz crystals with Q of about 100 000. That allows bandwidths of a few hundred hertz to a few kilohertz at 5–20 MHz. A quartz crystal is electrically a very large inductor in series with a tiny capacitor (the motional arm), with a small "case" capacitance $C_0$ across it. The ladder filter strings identical crystals in series with capacitors from each junction to ground. The capacitors set how strongly neighbouring crystals "talk" (the coupling), and the end resistances set how quickly energy leaves the filter. Get both right and you get a textbook Butterworth or Chebyshev passband. The $C_0$ bridging each crystal is the spoiler. It narrows the filter, makes the skirts asymmetric, and sets a floor on far-out rejection.

## The math

### Level 1 — definitions and specification terms
- **Insertion loss** at the passband centre; **ripple** across the passband; **3 dB / 6 dB bandwidth**.
- **Shape factor** $SF=BW_{60}/BW_6$, the ratio of the bandwidths at −60 dB and −6 dB (some vendors use −60/−3 or −40/−3; state which). An ideal brick wall has SF = 1; four poles give about 4–5, eight poles about 2.
- **Ultimate (stopband) rejection:** the floor far from the passband, set by parasitic coupling ($C_0$, layout, ground return) rather than by the filter order.
- **Isolation** (duplexer, diplexer): $|S_{TX,RX}|$ between the non-common ports in each band. **Rejection:** $|S_{ant,RX}|$ at the TX frequency, and vice versa.
- **Crystal (BVD) model:** $L_m$, $C_m$, $R_m$ in series, shunted by $C_0$. $f_s=1/(2\pi\sqrt{L_mC_m})$, $f_p\approx f_s(1+C_m/2C_0)$, $Q=2\pi f_sL_m/R_m$ ([crystals](../04-real-components-hf/crystals-and-resonators.md)).
- **k–q parameters:** for a low-pass prototype $g_0\dots g_{n+1}$, the normalised end Q is $q_1=g_0g_1$ and $q_n=g_ng_{n+1}$, and the normalised coupling is $k_{i,i+1}=1/\sqrt{g_ig_{i+1}}$. Denormalise with $Q_F=f_0/BW$: $Q_{e}=q\,Q_F$, $K_{ij}=k_{ij}/Q_F$ [9][10].

**Which separator do I need?**

| Situation | Device | Isolation available | Example |
|---|---|---|---|
| TX and RX at different times, same frequency (TDD) | T/R switch (PIN, SOI, relay) | 20–40 dB (switch off-state) | LoRa, FSK telemetry, radar T/R |
| TX and RX simultaneous, same band, different frequencies (FDD) | duplexer (cavity, SAW/BAW) | 50–90 dB | repeater, LTE handset |
| TX and RX simultaneous, same frequency | circulator (+ cancellation) | ≈ 20 dB (+ 20–40 dB with active cancellation) | CW radar, full-duplex experiments |
| Two or more bands on one antenna | diplexer / triplexer | 30–60 dB | 433 + 915 MHz, GNSS L1/L5 |
| Strong neighbour inside a receive band | high-Q notch, or nothing practical | depends on $Q_u\Delta f/f_0$ | launch-site co-channel planning |

### Level 2 — derivations
**(a) Repeater isolation budget.** On the transmit side, broadband noise $N_{TX}=P_{TX}+\mathcal L_{TX}(\Delta f)+10\log B$ must fall 10 dB below the receiver floor $-174+NF+10\log B$. On the receive side, the transmit carrier must stay below the receiver's blocking level. With 25 W (+44 dBm), −155 dBc/Hz at 5 MHz (assumed), NF 6 dB and B = 12.5 kHz: $N_{TX}$ = −70.1 dBm against a floor of −127.0 dBm, so the isolation at $f_{RX}$ must be ≥ 67.0 dB. With a −30 dBm blocking level, the isolation at $f_{TX}$ must be ≥ 74.0 dB (script §C). These are the 70–80 dB values seen on commercial 6-cavity units [5], and they explain why both directions need several cavities.

**(b) A notch cavity as a shunt series resonator.** A λ/4 coaxial cavity loop-coupled to the line behaves near resonance like a series RLC to ground with $R=\omega_0L/Q_u$. At resonance it shorts the line through R: $S_{21}=2R/(2R+Z_0)$. At an offset Δf its reactance is $X\approx2L\cdot2\pi\Delta f$, and the loss is $|2jX/(2jX+Z_0)|$. Demanding ≤ $L_p$ dB of loss at the pass frequency fixes $X_{min}=(Z_0/2)/\sqrt{10^{L_p/10}-1}$ (93.5 Ω for 0.3 dB). That fixes L, and then
$$R=\frac{X_{min}\,f_0}{2Q_u\,\Delta f}\quad\Rightarrow\quad\text{notch}=20\log\frac{2R}{2R+Z_0}.$$
The depth is governed by the product $Q_u\cdot\Delta f/f_0$ (script §C, 434.5 MHz notch):

| Pass offset | $Q_u$ = 300 (helical) | 3000 (λ/4 coax cavity) | 10 000 (large cavity) |
|---|---|---|---|
| 5 MHz | −9.1 dB | **−25.8 dB** | −35.9 dB |
| 0.58 MHz | −1.7 dB | −9.9 dB | −18.2 dB |

Repeater duplexers therefore cascade 2–3 notch cavities per side. Many use "pass-reject" (BpBr) cavities, whose extra series reactance puts a pass peak on one side of the notch, steepening the slope between the two frequencies. The Δf/f₀ product is also why the 600 kHz neighbour at a launch site is a frequency-planning problem, not a filtering problem ([co-site](co-site-interference-and-transmitter-intermod.md)).

**(c) Why a crossover diplexer is weak for 433/915.** A complementary pair of singly-terminated Butterworth filters (low-pass and high-pass sharing a common port, with input admittances that add to a constant) splits power as $1/(1+\Omega^{2n})$ and $\Omega^{2n}/(1+\Omega^{2n})$ around the crossover. With the crossover at $\sqrt{433.92\times915}$ = 630 MHz, 915 MHz is only Ω = 1.45. The rejection in the wrong arm is 10.2 / 16.3 / 22.7 / 29.2 dB for n = 3 / 5 / 7 / 9 (§A). Two widely spaced *narrow* bands are better served by placing transmission zeros (traps) on the opposite band.

**(d) Trap diplexer.**
- *433 arm:* a parallel $L_1C_1$ resonant at 915 MHz is an open circuit there, so the 433 arm does not load the 915 path. At 433 MHz it is inductive, $X=\omega L_1/(1-(f/f_{trap})^2)$ = 23.8 Ω for 6.8 nH. A series $C_s$ = 15.3 pF cancels that reactance.
- *915 arm:* a parallel $L_2C_2$ resonant at 433 MHz (22 nH, 6.1 pF) is capacitive at 915 MHz (−36.5 Ω). A series 6.4 nH cancels it.
- *Shunt traps:* series LC to ground resonant at the *other* band, on each port, deepen the rejection.

With finite Q ($Q_L$ = 50, $Q_C$ = 300) the analytic values already give 0.29 / 0.33 dB loss, 59–61 dB rejection and 15.5 / 17.9 dB return loss. A Nelder–Mead optimisation weighting loss and return loss converged to 0.14 / 0.22 dB loss, ≥ 33 dB return loss and 40 dB rejection (§B). The optimiser traded the surplus rejection away, so choose the weighting to suit your need. A ±5 % component Monte Carlo keeps the 95th-percentile loss below 0.25 dB and the 5th-percentile rejection at 29 dB.

Component values (nH / pF; script §B):

| Element | Function | Analytic start | Optimised |
|---|---|---|---|
| $L_1\,\|\,C_1$ (series, 433 arm) | open at 915 MHz | 6.80 / 4.45 | 6.78 / 3.68 |
| $C_s$ (series, 433 arm) | cancels arm reactance at 433 | 15.3 | 125 (≈ short; trap retuned instead) |
| $L_2\,\|\,C_2$ (series, 915 arm) | open at 433 MHz | 22.0 / 6.12 | 28.7 / 5.94 |
| $L_s$ (series, 915 arm) | cancels arm reactance at 915 | 6.38 | 1.88 |
| $L_{t1}$–$C_{t1}$ (shunt at 433 port) | short at 915 MHz | 15.0 / 2.02 | 20.0 / 1.46 |
| $L_{t2}$–$C_{t2}$ (shunt at 915 port) | short at 433 MHz | 39.0 / 3.45 | 41.3 / 3.21 |
| Result | IL 433/915; rejection; RL | 0.29/0.33 dB; 59–61 dB; 15.5/17.9 dB | 0.14/0.22 dB; 40 dB; 33/36 dB |

Round to E24/E12 values and re-simulate. With the ±5 % spread the response stays within the Monte Carlo figures above.

**(e) Crystal ladder by the coupled-resonator (Dishal) method.** In the *lower-sideband (LSB) ladder*, identical crystals sit in series with shunt capacitors $C_{i,i+1}$ to ground between them. Each crystal, together with the capacitors in its current loop, forms a series-resonant *mesh*. For two series meshes sharing a shunt capacitor $C_{12}\gg C_m$, the coupling coefficient is $K_{12}\approx C_m/C_{12}$. Setting $K_{12}=k_{12}/Q_F$ gives
$$C_{i,i+1}=\frac{C_m\,Q_F}{k_{i,i+1}}.$$
The end mesh is loaded by the termination in series, $Q_e=2\pi f_0L_m/R_e=q\,Q_F$, so
$$R_e=\frac{2\pi L_m\,BW}{q}.$$
**Mesh tuning:** each mesh resonates at $f_s\sqrt{1+C_m\sum1/C}$ over the capacitors in its loop. End meshes, with one coupling cap, sit lower than inner meshes, with two. Add series capacitors to every mesh below the highest so all meshes resonate at the same frequency; with all other meshes open, each mesh is tuned alone (Dishal's alignment idea [9][11]). For the 4-pole, 0.1 dB Chebyshev design (g = 1.1088, 1.3061, 1.7703, 0.8180, 1.3554; $q_1=q_4$ = 1.1088; $k_{12}=k_{34}$ = 0.831, $k_{23}$ = 0.658; script §D) at a 2.4 kHz *ripple* bandwidth:
- $C_{12}$ = 105.8 pF, $C_{23}$ = 133.7 pF, $R_e$ = 163 Ω. The end meshes sit 997 Hz and the inner meshes 1786 Hz above $f_s$, so the end meshes get series caps of 133.7 pF.
- Without $C_0$ the −3 dB bandwidth is 2824 Hz. That is correct: the 0.1 dB-ripple band of an n = 4 Chebyshev is $1/\cosh(\tfrac14\cosh^{-1}(1/\varepsilon))$ = 0.82 of its 3 dB band.
- With $C_0$ = 4.5 pF it shrinks to 2432 Hz (−14 %) and the centre drops 208 Hz. Hayward reports the same narrowing [4].
- Re-designing for a 2366 Hz ripple bandwidth (iterating on the simulated 3 dB bandwidth) gives exactly 2400 Hz at −3 dB with $C_0$. Loss is 1.43 dB with Q = 75 k crystals, and the central-80 % ripple is 0.74 dB, larger than 0.1 dB because of finite Q and $C_0$.
- Shape factor (60/6 dB) is 4.6. Rejection 30 kHz below is 88 dB; 30 kHz above it is 157 dB, because the crystals' parallel resonances near $f_s$ + 23 kHz put transmission zeros on the high side (the "LSB" ladder's steep upper skirt). The $C_0$-bridged floor 2 MHz away is about 105 dB in the ideal model; real layouts reach 60–90 dB.

**(f) Cohn "minimum-loss" and other variants.** Cohn showed that dissipation loss in coupled-resonator filters depends on the element values. Equal coupling capacitors throughout (the "min-loss", equal-element design) give close to the lowest loss for given resonator Q and are very easy to build. They give a less flat (not exactly Butterworth/Chebyshev) passband [3][4]. The *USB ladder* puts crystals in the shunt arms and has its steep skirt on the low side. *Lattice* (bridge) filters with two crystal frequencies give symmetric skirts but need matched pairs and a balanced transformer.

**(g) Measuring the motional parameters (G3UUR).** Run the crystal in a simple series-mode oscillator and note the frequency with the series capacitor shorted ($\approx f_s$) and with a known $C_s$ in series. The load-resonance formula $f_L=f_s[1+C_m/(2(C_0+C_s))]$ gives
$$C_m=\frac{2\Delta f\,(C_0+C_s)}{f},\qquad L_m=\frac{1}{(2\pi f_s)^2C_m}.$$
Measure $C_0$ with a capacitance meter at a frequency well away from resonance, e.g. 1 MHz. In §E the exact BVD load resonance gave +2814 Hz (33 pF) and +1010 Hz (100 pF), and the formula recovered $C_m$ to 0.02 %. In practice the oscillator's own series capacitance enters; G3UUR's published procedure accounts for it, or calibrate with one crystal of known $C_m$. $R_m$ comes from the insertion loss at $f_s$ in a known-impedance fixture. Matching the crystals' $f_s$ to within about 10 % of the filter bandwidth matters more than matching $L_m$.

### Level 3 — duplexer and filter technologies
- **Cavity duplexers** (VHF/UHF repeaters): 4–6 λ/4 coaxial cavities with $Q_u$ of a few thousand, either notch-only (when TX and RX are close), band-pass, or BpBr. They are tuned on a network analyser for maximum notch depth at the opposite frequency with acceptable loss. The cables between cavities and the tee are part of the design: their length makes each arm look open at the other band at the junction. Temperature drift of the cavity (Invar rods) and power handling (cavity voltage) set the commercial specs [5][7].
- **SAW/BAW duplexers** (cellular FDD handsets): acoustic resonators in ladder and lattice arrangements give 1.5–3 dB loss and 50–60 dB isolation in packages under 2 mm. One band-8 TC-SAW part lists about 55 dB minimum and 60 dB typical TX→RX isolation, with 1.5 dB TX and 1.9 dB RX loss [6]. Power handling is about +30 dBm, adequate for handsets but not repeaters. BAW (FBAR) wins above about 2 GHz and for tight bands.
- **Diplexers and multiplexers** (multi-band antennas, cable TV, GNSS L1/L5, 433/915 shared antennas): lumped LC or LTCC parts. Broadband crossover designs suit widely separated bands, and trap designs suit narrow bands far apart. A *triplexer* adds a third band. Check that the antenna really matches at both bands ([multiband antennas](../08-antennas/multiband-and-wideband-antennas.md)).
- **Monolithic crystal filters (MCF):** two or more electrode pairs on one quartz plate. They are acoustically coupled through the plate, and the coupling is set by electrode spacing. Supplied as 2-pole (and 4-pole) sections at 10.7, 21.4 and 45 MHz, they serve as *roofing filters* (a few to 15 kHz wide) right after the first mixer of a superhet. They protect the later stages and the AGC detector from strong nearby signals ([receivers](receiver-architectures.md), [AGC](agc-loops-and-receiver-gain-control.md)).
- **Ceramic filters:** PZT resonators with Q ~ 1000. They are cheap, have fixed bandwidths and are characterised for fixed terminations. 10.7 MHz FM-IF parts are 330 Ω with 150–280 kHz 3 dB bandwidths (SFELF10M7FA00: 280 ± 50 kHz, 4 ± 2 dB loss, 650 kHz at −20 dB, about 30 dB spurious rejection [8]). 455 kHz AM/NBFM IF parts are 1.5–2 kΩ (CFWLA455KBFA: ±15 kHz at −6 dB, ±30 kHz at −30 dB, ≤ 4 dB loss, 1500 Ω [8]). Mis-terminating them causes ripple and loss. Ceramic resonators also have strong spurious responses well away from the passband, so add an LC filter.

### Level 3 — choosing the filter technology
| Technology | Resonator $Q_u$ | Practical fractional BW | Loss | Power | Size / cost | Typical use |
|---|---|---|---|---|---|---|
| Lumped LC (0402–0805) | 30–80 at UHF | > 5 % | 0.3–2 dB | W | mm, cents | diplexers, harmonic filters |
| Helical resonator | 300–1000 | 0.5–5 % | 1–3 dB | W | cm, $ | VHF/UHF preselectors |
| λ/4 coaxial cavity | 2000–10 000 | 0.1–1 % (notch: Δf ≥ ~1 %) | 0.3–1.5 dB | 100 W+ | dm, $$ | repeater duplexers |
| SAW / BAW | 500–2000+ (acoustic) | 0.3–5 % | 1–3 dB | ≤ ~1 W | mm, < $1 | handset duplexers, ISM band filters |
| Ceramic (PZT) | ~1000 | 0.5–3 % at 10.7 MHz / 455 kHz | 2–6 dB | mW | mm, cents | FM/AM IF |
| Quartz crystal | 50 000–200 000 | 0.002–0.1 % | 1–4 dB | mW | cm, $ | SSB/CW/data IF, roofing |

The $Q_u$ ranges are orders of magnitude from [1][4][7] and the filter-parts page [18 filter parts](../18-components-parts/filter-parts-saw-ceramic-ltcc.md). The rule behind every row is the loss formula in [RF filters](rf-filters-lc-saw-baw-cavity-microstrip.md#level-1--the-loss-formula-and-the-design-numbers): loss rises as (fractional bandwidth × $Q_u$)⁻¹.

## Design equations & rules of thumb

| Quantity | Equation | Typical numbers |
|---|---|---|
| Repeater TX-side isolation | $P_{TX}+\mathcal L+10\log B-(\text{floor}-10)$ | 25 W, −155 dBc/Hz: 67 dB |
| Repeater RX-side isolation | $P_{TX}-P_{block}$ | 25 W, −30 dBm: 74 dB |
| Cavity notch resistance | $R=X_{min}f_0/(2Q_u\Delta f)$ | $Q_u$ 3000, 5 MHz, 0.3 dB: −26 dB per cavity |
| Crossover diplexer leakage | $1/(1+\Omega^{2n})$ | Ω 1.45, n 5: −16 dB |
| Trap reactance (parallel LC below resonance) | $X=\omega L/(1-(f/f_{trap})^2)$ | 6.8 nH, 433 vs 915: +23.8 Ω |
| Ladder coupling cap | $C_{ij}=C_mQ_F/k_{ij}$ | 21 fF, 10 MHz, 2.4 kHz: ~107/136 pF |
| Ladder end resistance | $R_e=2\pi L_m BW/q$ | 12 mH, 2.4 kHz: ~160 Ω |
| Chebyshev 3 dB vs ripple BW (n = 4, 0.1 dB) | ×1.21 | — |
| $C_0$ narrowing | ~10–20 % for BW ≈ 2–3 kHz at 10 MHz | design wider and iterate |
| G3UUR | $C_m=2\Delta f(C_0+C_s)/f$ | 33 pF: +2.8 kHz |
| Shape factor | $BW_{60}/BW_6$ | 4-pole ≈ 4.6 |

Rules of thumb:
- Duplexers need $Q_u\,\Delta f/f_0$ ≳ 30 per cavity for useful notches at low loss.
- Diplexer: if the two bands differ by more than about ×1.5, use traps or elliptic sections, not a simple crossover.
- Crystal filters: buy 20–50 crystals of one type, measure them all, and select by $f_s$ (within 10–20 % of the bandwidth). Build in a shielded box with short ground returns and match the ends (L-network or transformer) to the computed $R_e$.
- Specify IF filters by termination impedance as well as bandwidth.

## Worked examples

### Example 1 — Full-duplex ground station: uplink at 915 MHz while receiving the 433 MHz downlink on one antenna
The ground station transmits 1 W (+30 dBm) at 915 MHz to command the rocket while the 433 MHz receiver keeps listening, through a dual-band antenna and the trap diplexer of (d). With ≥ 40 dB isolation, the 433 port sees ≈ −10 dBm of 915 MHz. That is far above the LNA's comfortable input; it would compress an SX126x front end or an external LNA ([dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)). Add a 433 MHz SAW filter after the diplexer's 433 port (≥ 40 dB at 915 MHz typical; [18 filter parts](../18-components-parts/filter-parts-saw-ceramic-ltcc.md)) to bring it to about −50 dBm. Also check the 915 transmitter's *output noise* at 433 MHz. PA noise 480 MHz away is negligible compared with in-band noise, but harmonics and spurs of the 915 chain near 433 are not, so filter the 915 TX output too. Or simply time-share (TDD): LoRa is half-duplex anyway.

### Example 2 — Rocket with E22 (433) and E220 (915) on one antenna
The same trap diplexer (insertion loss ≈ 0.2 dB, 40 dB isolation) connects both modules to a dual-band whip or blade. When the E22 transmits 2 W, the E220's port sees about −7 dBm of 433 MHz. That is acceptable for a module whose PA output stage is off, but it is also an injection signal for transmitter intermodulation when both transmit together ([co-site](co-site-interference-and-transmitter-intermod.md)). Time-interleave the two transmitters or accept the IMD level computed there. Use ≥ 0.25 W-rated parts in the 433 arm (2 W passes through) and NP0/C0G capacitors.

### Example 3 — A 2.4 kHz SSB/data IF filter from four 10 MHz crystals
Measure the crystals first by G3UUR: say $L_m$ = 12 mH, $C_0$ = 4.5 pF, Q ≈ 75 k. The design steps (§D):
1. Choose 0.1 dB Chebyshev n = 4; target −3 dB = 2.4 kHz, so the ripple bandwidth starts at ≈ 2.0 kHz before the $C_0$ correction. After iteration the design ripple bandwidth is 2366 Hz.
2. $C_{12}=C_{34}$ ≈ 107 pF and $C_{23}$ ≈ 136 pF (use 100 + 6.8 pF and 120 + 15 pF C0G).
3. $R_e$ ≈ 161 Ω. Match to 50 Ω with an L-network or a 1:3 (turns 1:1.8) transformer at each end.
4. Series tuning caps of about 135 pF in the end meshes.
5. Expect 1.4 dB loss, shape factor 4.6, and a high-side skirt much steeper than the low side.

Position the BFO or LO for the sideband accordingly. The LSB ladder's steep upper skirt suits it to rejecting the opposite sideband when the carrier sits on the upper edge.

### Example 4 — Can a cavity save my receiver from another team's 434.5 MHz transmitter?
The wanted channel is 433.92 MHz and the interferer 434.5 MHz (580 kHz away). For 0.3 dB loss at 433.92, a $Q_u$ = 3000 cavity notches the interferer by only about 10 dB, and a 10 000-Q cavity by 18 dB (§C). The fixes are frequency coordination (move channels several MHz apart), physical separation and antenna pattern nulls, or relying on the LoRa receiver's own selectivity and co-channel tolerance ([co-site](co-site-interference-and-transmitter-intermod.md)). Cavities make sense only for *band*-scale separation.

### Example 5 — Choosing IF filters for a homebrew 433 MHz narrowband receiver
Take a single-conversion superhet: 433.92 MHz → 10.7 MHz IF, for FSK telemetry with ±5 kHz deviation, 2.4 kb/s.
- **Choose the IF:** Carson bandwidth is 2(5 + 2.4) ≈ 15 kHz. Add ±1 kHz Doppler and crystal error ([LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)), so the IF needs about 20 kHz.
- **Ceramic is too wide:** a 10.7 MHz ceramic filter (≥ 150 kHz) would let 7–10 neighbouring 25 kHz channels into the AGC detector.
- **Use crystal filtering:** a 2-pole 10.7 MHz MCF (≈ 15–20 kHz) as a roofing filter, followed by either a 4-pole crystal ladder at ≈ 20 kHz or a second conversion to 455 kHz with a ±10 kHz ceramic filter.
- **Image:** the image lies 21.4 MHz away and needs a 433 MHz front-end SAW ([receivers](receiver-architectures.md)). An SX126x module avoids all of this with an integrated low-IF architecture. The superhet route is for learning, or for a receiver whose selectivity you control.

### Example 6 — Bench-testing a home-made crystal ladder
1. Set up a VNA or SDR + tracking generator with 50 Ω → L-match → filter → L-match → 50 Ω. Check the L-matches alone first.
2. Sweep ±10 kHz with ≤ 20 Hz steps and a narrow IF bandwidth. Read the loss, the −3 dB and −60 dB widths, and the ripple.
3. If the passband shows a "hump" or dip in the middle, the meshes are mistuned: adjust the end series caps first, then the inner meshes.
4. If the passband is too narrow overall, reduce the coupling caps by 5–10 % and recompute $R_e$.
5. Sweep ±2 MHz to find the ultimate rejection; a floor near −60 dB usually means input–output coupling through the layout.

## Practical notes
- **Tuning a cavity duplexer:** use a VNA with the unused port terminated. Tune each notch cavity for its deepest notch at the opposite frequency, then adjust the pass frequency with the coupling loop and cable lengths. Re-check at operating power and temperature: cavities drift with temperature unless they are Invar-compensated.
- **Diplexer layout:** keep the two arms' first elements close to the common node (a few mm at UHF) so the junction does not add a stub. Use RF-rated 0402/0603 inductors with Q ≥ 40 at the frequency. Verify with a VNA, since lumped parts detune by several per cent.
- **Crystal filter construction:** a ground plane, short leads, a shield between input and output sections, and crystal cases grounded. The ultimate rejection usually comes from layout coupling, not from the simulation's $C_0$ floor. Measure with a VNA set to a narrow IF bandwidth (or an SDR with a tracking generator) at fine frequency steps: 2.4 kHz is a few points on a coarse sweep.
- **Group delay:** narrow crystal filters have long, peaked group delay at the band edges, about $n/(\pi BW)$ in order of magnitude, i.e. milliseconds. CW signals "ring", and data through them suffers ISI. Use them for SSB/CW, not for wideband data.
- **Ceramic filters:** observe the input/output impedance and polarity marks. A mismatched 455 kHz filter can show several dB of ripple.

## Common mistakes & misconceptions
- *"Duplexer and diplexer are the same thing."* A duplexer separates TX and RX in one band (FDD). A diplexer separates two bands.
- *"A LoRa ground station needs a duplexer."* LoRa is half-duplex: a T/R switch (inside the module) suffices. A diplexer is needed only to share an antenna between bands.
- *"Any good notch filter can remove a nearby interferer."* Notch depth at low pass loss scales with $Q_u\Delta f/f_0$; a few hundred kHz at 433 MHz is beyond any practical cavity.
- *"Design the crystal filter with the series-resonator model and it will be right."* $C_0$ narrows it by 10–20 % and shifts it. Iterate (design wider) or use an effective-inductance correction [4].
- *"Chebyshev g-values give the 3 dB bandwidth."* They are normalised to the ripple bandwidth; the 3 dB bandwidth is wider (×1.21 for n = 4, 0.1 dB).
- *"All crystals of one part number are interchangeable in a filter."* Their $f_s$ spread is often comparable to the filter bandwidth; select them.
- *"Shape factor tells me the stopband."* It describes the skirt. Ultimate rejection (far-out floor) is a separate specification limited by parasitics.

## How to simulate / verify
- `python3 tools/verify/rf2_duplex_xtal.py` (≈ 3 s, ngspice; ALL PASS) covers: §A crossover diplexer leakage; §B trap diplexer (analytic start, optimisation, ±5 % Monte Carlo); §C cavity notch and repeater isolation budget; §D crystal ladder (g-values, k–q, coupling caps, mesh tuning, with/without $C_0$, bandwidth iteration, shape factor, ultimate rejection, ngspice AC cross-check); §E G3UUR formula.
- For layout effects use openEMS or a VNA on the built board ([16 openEMS](../16-simulation-tools/openems-workflow.md)). Hayward's and the "Dishal" crystal-ladder programs [4][12] implement the same k–q method with practical refinements.

## Open questions / gaps
- Repeater duplexer and SAW duplexer figures come from vendor pages via search summaries ([5][6]); no data sheet was read in full.
- The trap diplexer is a lumped schematic with ideal interconnect. Pad and trace parasitics at 915 MHz will shift it; an EM or VNA check is needed.
- The −155 dBc/Hz transmitter noise at 5 MHz is an assumed planning value, not a measured figure for any specific transmitter.
- Cohn's equal-element ("min-loss") ladder was described, not simulated; its k–q values were not re-derived here.
- Monolithic crystal filter parameters (coupling vs electrode gap) were not quantified.
- The technology-selection $Q_u$ ranges are order-of-magnitude summaries, not part-specific data.
- Circulator-plus-active-cancellation isolation figures in the separator table are indicative only; see [circulators](circulators-isolators.md).

## Sources
1. G. L. Matthaei, L. Young, E. M. T. Jones, *Microwave Filters, Impedance-Matching Networks, and Coupling Structures*, Artech House, 1980 (coupled-resonator theory, k and Q, diplexers/multiplexers). (textbook; background)
2. A. I. Zverev, *Handbook of Filter Synthesis*, Wiley, 1967 (crystal filters, k–q tables, predistortion). (textbook; cited)
3. S. B. Cohn, "Dissipation loss in multiple-coupled-resonator filters," *Proc. IRE* 47(8), 1342–1348, Aug. 1959. (peer-reviewed; cited for min-loss design)
4. W. Hayward, "Designing narrow-bandwidth ladder filters," 2019, http://w7zoi.net/filters/genfil.pdf; and W. Hayward, R. Campbell, B. Larkin, *Experimental Methods in RF Design*, ARRL, 2003, ch. 3 (k–q method, LSB/USB ladders, mesh tuning, $C_0$ narrowing, G3UUR measurement). (lecture notes / handbook; genfil read)
5. Repeater duplexer data: repeater-builder.com "Duplexer specifications guide" and J. Portune W6NBC, *The Cavity Duplexer*; vendor examples BCD-440 (6 cavity, 80 dB, 1.5 dB, 5–8 MHz split) and Jiesai 6-cavity 440–480 MHz (≥ 75 dB, ≤ 1.4 dB). https://www.repeater-builder.com/antenna/duplexer-specs.html (ham/vendor; via search summary)
6. Sanan RBD0943G4G band-8 TC-SAW duplexer data sheet (TX→RX isolation ≈ 55 dB min / 60 dB typ, TX loss 1.5 dB typ, RX loss 1.9 dB typ). https://www.sanan-ic.com/Public/Uploads/uploadfile/files/20240524/QuanzhouSanan_DataSheet_1612DPXB8_RBD0943G4G_rev1.0.pdf (datasheet; via search summary)
7. ARRL, *The ARRL Handbook*, repeater and filter chapters (cavity, BpBr duplexers). (handbook; background)
8. Murata SFELF10M7FA00-B0 and CFWLA455KBFA-B0 product data (CERAFIL). https://www.murata.com/en-us/products/productdetail?partno=SFELF10M7FA00-B0 (datasheets; via search summary)
9. M. Dishal, "Design of dissipative band-pass filters producing desired exact amplitude-frequency characteristics," *Proc. IRE* 37(9), 1050–1069, 1949. (peer-reviewed; cited)
10. D. M. Pozar, *Microwave Engineering*, 4th ed., 2012, §8.3–8.8 (prototype g-values, coupled resonators). (textbook)
11. M. Dishal, "Alignment and adjustment of synchronously tuned multiple-resonant-circuit filters," *Proc. IRE* 39(11), 1448–1455, 1951. (peer-reviewed; cited)
12. "Dishal" crystal-ladder design program, help file (author not recorded here), https://warc.org.uk/wp-content/uploads/2014/01/eDishalHelp-1.pdf (software documentation; equal-element Cohn design noted)
13. `tools/verify/rf2_duplex_xtal.py` (this KB).
