---
title: Antenna tuners and ATUs — what a tuner does and does not do, L/T/Pi topologies and their losses, auto-tuner algorithms, remote and at-antenna tuners, and the "tuners fix antennas" myth in numbers
domain: 03-transmission-lines-matching
slug: antenna-tuners-and-atus
tags: [antenna-tuner, atu, transmatch, matching-network, l-network, t-network, pi-network, auto-tuner, n7ddc, atu-100, relay, remote-tuner, ladder-line, mismatch-loss, feedline-loss, swr, inductor-q, hf]
prerequisites:
  - reflections-vswr-return-loss-mismatch.md
  - impedance-matching-lumped-and-distributed.md
  - coax-and-cables.md
related:
  - smith-chart.md
  - ../08-antennas/wire-antennas-hf-random-wire-fan-dipole.md
  - ../08-antennas/antenna-matching-and-baluns.md
  - ../08-antennas/small-antenna-limits.md
  - ../06-rf-circuits/rf-switches-attenuators-limiters.md
  - ../06-rf-circuits/couplers-dividers-combiners.md
  - ../17-test-measurement/rf-power-measurement.md
  - ../17-test-measurement/interference-hunting-and-rf-immunity.md
level: mixed
confidence: medium
last_updated: 2026-10-12
---

# Antenna tuners and ATUs

## Questions this page answers
- What does an antenna tuner actually do, and what does it not do?
- Does a tuner at the radio fix the SWR on my feedline?
- How much power do I lose using a tuner at the rig with high SWR on coax?
- Why is a tuner better at the antenna end, and how is a remote tuner powered and controlled?
- How do L, T and Pi tuners differ, and why can a T tuner waste power?
- How does an automatic antenna tuner find a match, and why do cheap (N7DDC-style) ones fail?
- Are ordinary relays good enough inside an RF tuner?
- Which antennas will my radio's internal tuner match?
- Does a tuner help a receive-only shortwave setup?
- What should I consider when choosing a tuner?

## TL;DR
- **A tuner is a matching network.** It transforms whatever impedance appears at its output terminals into ≈ 50 Ω at its input, so the transmitter delivers full power. It does **nothing** on the antenna side of itself:
  - the SWR on the feedline between tuner and antenna stays exactly as it was;
  - the feedline's extra loss from that SWR stays;
  - the antenna's radiation efficiency and pattern stay.
- **Put the tuner where the mismatch is.** 30 m of RG-58 at 14 MHz loses 1.3 dB matched, but 4.1 dB at SWR 10 and 6.2 dB at SWR 20. An off-band dipole (≈ 10 − j400 Ω at 3.6 MHz) fed with 30 m of RG-58 delivers **only ≈ 4 %** of the power, even with a perfect "1:1" at the rig. With 450 Ω ladder line, the same antenna gets ≈ 52 %. With an L-network tuner at the antenna (inductor Q 200–300) plus matched coax behind it, it gets ≈ 70–75 % (`e10_tuner_loss.py`).
- **A lossy feedline flatters the SWR reading.** The rig sees $RL_{in} = RL_{load} + 2A$. An *open circuit* at the end of 30 m of RG-58 at 28 MHz reads 4.7:1 at the rig.
- **Topologies** (inductor unloaded Q = 100–300):
  - **L** (2 elements) has the lowest loaded Q, so the lowest loss. Loss fraction ≈ $Q_n/Q_u$, where $Q_n = \sqrt{R_{high}/R_{low}-1}$: < 0.1 dB for 12.5 or 200 Ω loads.
  - **High-pass T** (C–L–C) has a free parameter. Set with *maximum* capacitance it is nearly as good as an L. With small C it loses **1–4 dB** on the same loads.
  - **Pi** (C–L–C, low-pass) adds harmonic suppression.
  - Very low-R reactive loads, such as a short whip at 5 − j500 Ω, cost 1.3–3 dB in the coil alone (Q 300–100). That loss is the antenna's loading-coil loss wherever it is placed.
- **Auto-tuners** sense forward/reflected power with a directional coupler, then step relay-switched L and C banks. The N7DDC ATU-100 uses 7 L (0.05–4.5 µH) and 7 C (10 pF–1 nF) with C switchable to either side: 32 768 states. It searches coarse-to-fine, stores memories per frequency, retunes when SWR > 1.3, and needs ≥ 5 W to start [3]. Weak points: small relays hot-switched under RF, the coupler's directivity, and narrow L/C ranges.
- **Internal radio tuners** match only modest mismatches: the IC-7300's covers 16.7–150 Ω, i.e. SWR < 3:1 [4]. They tidy up a resonant antenna. They are not for random wires.
- **Receive-only**: mismatch costs a receiver little; 3:1 is 1.25 dB of mismatch loss. Where an HF receiver is already limited by external noise, that loss is often invisible. A tuner can still help as a *preselector* that attenuates strong out-of-band signals, but that is a filter function, not a gain function.

## Intuition (no math)
Think of the transmitter as a pump designed for one pipe size (50 Ω). The antenna system presents some other "pipe": very high, very low or reactive impedance. A tuner is an adapter fitting **at the point where you install it**. Everything downstream of the fitting is unchanged: if the pipe beyond it is leaky (lossy coax) and the mismatch makes the fluid slosh back and forth (standing waves), the sloshing still happens and the leaks still leak. Only the pump is happy.

That is why location matters. Put the adapter right at the antenna, and the coax carries matched (non-sloshing) power with only its normal loss. Put it at the radio, and the coax carries a standing wave whose high-current and high-voltage points sit along the cable, where the copper and dielectric losses are worse. Use ladder line instead of coax and the "leak" is small even with sloshing, because ladder line's loss is tiny. That is why the classic multiband antenna is a doublet fed with ladder line into a tuner.

Nothing in the tuner changes the antenna's own efficiency. A short whip with 5 Ω of radiation resistance still needs a big series inductor to cancel its capacitance, and that inductor's resistance eats power. A tuner that does the cancelling in the shack simply moves the inductor's loss 30 m away, and adds the coax's high-SWR loss on top.

## The math

### Level 1 — what the meter shows and what the antenna gets
- Mismatch at the load: $\Gamma_L = (Z_L - Z_0)/(Z_L + Z_0)$; SWR $s = (1+|\Gamma|)/(1-|\Gamma|)$ ([reflections](reflections-vswr-return-loss-mismatch.md)).
- Matched one-way loss of a line, $A$ dB; $a = 10^{A/10}$.
- **Total loss of a mismatched lossy line** (power in at the tuner ÷ power delivered to the antenna terminals), the same formula as on the reflections page:
$$TL = 10\log_{10}\frac{a^2 - |\Gamma_L|^2}{a\,(1-|\Gamma_L|^2)}\ \text{dB}.$$
- **SWR seen at the input**: $|\Gamma_{in}| = |\Gamma_L|\,10^{-A/10}$, i.e. $RL_{in} = RL_L + 2A$.
- **L-network loss** (series element of unloaded Q $Q_u$): fraction lost ≈ $Q_n/Q_u$ with $Q_n = \sqrt{R_{high}/R_{low} - 1}$.

### Level 2 — derivations

**Why a tuner at the rig cannot fix the line.** On a line with real $Z_0$ the forward and reflected waves are set by the *load* at the far end and by the line; the source end only sets their overall level. A lossless tuner at the source end re-reflects the returning wave back towards the load in phase ("conjugate match"). All the power that is not dissipated eventually enters the load. That is why "reflected power is lost" is a myth ([reflections](reflections-vswr-return-loss-mismatch.md)). But the line now carries the standing-wave pattern of $\Gamma_L$, and its ohmic loss is the integral of $|I|^2R' + |V|^2G'$ along it. That integral grows with SWR. Writing the forward power at the load as $P^+$ and integrating the two travelling waves along a line of attenuation α:
$$P_{in} = P^+\left(a - \frac{|\Gamma_L|^2}{a}\right),\qquad P_L = P^+(1-|\Gamma_L|^2),$$
whose ratio is the total-loss formula. The script checks it against exact voltage/current bookkeeping on a lossy line: 1.924 dB and 4.142 dB for SWR 3 and 10, identical to 3 decimal places. Nothing in this calculation depends on the tuner. Only moving the matching point, or lowering the line loss, changes it.

**Numbers for 30 m of feedline** (`e10_tuner_loss.py`; RG-58 and LMR-400 losses from the [coax fits](coax-and-cables.md) extrapolated down to HF; ladder line assumed 0.2 dB/100 ft at 14 MHz, dry):

| Line, 30 m | f (MHz) | Matched (dB) | SWR 3 | SWR 10 | SWR 20 |
|---|---|---|---|---|---|
| RG-58 | 3.6 | 0.65 | 1.01 | 2.49 | 4.02 |
| RG-58 | 14 | 1.31 | 1.92 | 4.14 | 6.15 |
| RG-58 | 28 | 1.89 | 2.65 | 5.26 | 7.47 |
| LMR-400 | 14 | 0.45 | 0.72 | 1.86 | 3.13 |
| LMR-400 | 28 | 0.64 | 1.00 | 2.46 | 3.98 |
| 450 Ω ladder | 14 | 0.20 | 0.32 | 0.90 | 1.63 |
| 450 Ω ladder | 28 | 0.28 | 0.45 | 1.23 | 2.16 |

The SWR on a given line depends on that line's $Z_0$. The *same antenna* is a much smaller mismatch to 450 Ω ladder line when its impedance is high:

| Same antenna, 30 m | RG-58 | LMR-400 | 450 Ω ladder |
|---|---|---|---|
| 3.6 MHz, Z = 10 − j400 Ω (a 7 MHz dipole used on 80 m, order of magnitude) | SWR 325, **14.1 dB loss (3.9 % delivered)** | 9.8 dB (10 %) | SWR 81, 2.9 dB (52 %) |
| 14 MHz, Z = 2000 + j500 Ω (near a high-impedance point) | SWR 42, 8.8 dB (13 %) | 5.1 dB (31 %) | SWR 4.7, 0.47 dB (90 %) |

**The flattering SWR meter.** Each pass through the line attenuates the wave by $A$, so the reflected wave reaching the rig is down $2A$. For RG-58 at 28 MHz ($A$ = 1.89 dB over 30 m), an antenna SWR of 10 reads 3.3:1 at the rig, and even an *open circuit* (SWR ∞) reads 4.7:1. Internal tuners rated for 3:1 then "find a match" into what is mostly a 30 m dummy load made of coax.

**L-network loss.** An L-network matching $R_{low}$ to $R_{high}$ has loaded $Q_n = \sqrt{R_{high}/R_{low}-1}$ ([matching](impedance-matching-lumped-and-distributed.md)). Its series element carries the full current with reactance $X = Q_nR_{low}$. With unloaded Q $Q_u$ that element has $R_{loss} = X/Q_u$, so the fraction of power lost is $R_{loss}/(R_{low}+R_{loss}) \approx Q_n/Q_u$. The script's exact ABCD calculation agrees within 5 %: for example 12.5 Ω, $Q_u$ = 100 gives 0.0170 exact vs 0.0173 from the rule. For a resistive 4:1 mismatch an L-network costs under 0.1 dB with any decent coil. The coil matters only for large ratios and reactive loads.

**Reactive loads and the loading-coil loss.** A short whip with $Z = 5 - j500$ Ω needs about +500 Ω of series inductance just to resonate it. With $Q_u$ = 300 that inductor has 1.67 Ω of loss against 5 Ω of radiation resistance, i.e. 25 % lost (1.25 dB). With $Q_u$ = 100 it is 3.0 dB. This is the [small-antenna efficiency limit](../08-antennas/small-antenna-limits.md) in another form. Putting the inductor in a tuner at the rig does not avoid it, and adds the coax's SWR-325 loss too.

**T and Pi networks.** A three-element network has one more degree of freedom than needed, so a whole family of settings matches the same load. They differ in loaded Q.
- **High-pass T** (series C, shunt L, series C): with the input capacitor at *maximum* capacitance (smallest reactance), the T behaves like an L-network with a small extra series C, and the loaded Q is lowest. With the capacitors near *minimum* the circulating current in the shunt inductor is large. On the script's loads, the best T setting loses 0.03–0.3 dB on moderate loads and 1.7–3.7 dB on the whip. Settings with small input C (|X| > 1 kΩ) lose **1–4 dB** where the L loses < 0.1 dB.
  - Rule: tune a T with the most capacitance that still gives a match. Better, have the auto-tuner prefer that branch.
- **Pi** (shunt C, series L, shunt C) is a low-pass network. It suppresses harmonics, which is why valve PA output networks are Pi or Pi-L. As a tuner it has the same "family of solutions, choose the low-Q one" property.

**Smith-chart picture.** On the [Smith chart](smith-chart.md) an L-network is two moves: a series element slides the point along a constant-resistance circle, and a shunt element slides it along a constant-conductance circle. The match is the pair of moves that lands on the centre. A T or Pi adds a third move, so infinitely many paths reach the centre. Long detours (large arcs, i.e. high loaded Q) are the lossy ones. Seen this way, the "maximum capacitance" rule for a T tuner just picks the shortest path.

**Where the tuner sits — summary for the 80 m example** (Z = 10 − j400 Ω, 30 m of line, 3.6 MHz):

| Arrangement | What the rig sees | Loss before the antenna | Delivered |
|---|---|---|---|
| Tuner at rig, RG-58 | 1:1 after tuning | 14.1 dB (line at SWR 325) + tuner | ≈ 4 % |
| Tuner at rig, LMR-400 | 1:1 | 9.8 dB + tuner | ≈ 10 % |
| Balanced tuner at rig, 450 Ω ladder | 1:1 | 2.9 dB + tuner | ≈ 50 % |
| Tuner at antenna (Q 200–300), RG-58 behind it | 1:1 | 0.65 dB + 0.5–0.8 dB | ≈ 70–75 % |
| Resonant 80 m antenna, no tuner | ≈ 1.5:1 | 0.65–0.70 dB | ≈ 85 % |

### Level 3 — auto-tuners, remote tuners and limits
- **Sensing.** A directional coupler (tandem-match or Bruene bridge, [couplers](../06-rf-circuits/couplers-dividers-combiners.md)) gives forward and reflected voltages, and an MCU computes SWR. Coupler directivity limits how low an SWR the tuner can recognise: at 25 dB directivity, a true 1.0:1 can read as anything up to ≈ 1.12:1 ([power measurement](../17-test-measurement/rf-power-measurement.md)).
- **Network.** Relay-switched, binary or uneven-step L and C banks in an L-network, plus one relay that moves C to the input or output side. This covers $R_L < 50$ and $R_L > 50$. ATU-100: 7 L (0.05–4.5 µH steps, 8.53 µH max) and 7 C (10 pF–1 nF), so $2^7\times2^7\times2$ = 32 768 states [3].
- **Search.** Exhaustive search at ~5 ms per relay settle and measurement would take ~160 s. Practical firmware does coarse steps on one axis, then the other, then refines near the best point, and stores the result per frequency segment (memories). Tune time is a fraction of a second to a few seconds. The ATU-100 triggers a retune when SWR exceeds 1.3 and has changed since the last tune, and tunes on any signal of ≥ 5 W, including speech [3].
- **Failure modes.**
  - Relays switched under RF ("hot switching") arc and weld. Tune at low power, and use firmware that interlocks power during switching.
  - Small signal relays have contact capacitance and limited voltage rating. High-impedance loads at 100 W produce hundreds of volts (√(PR): ≈ 450 V rms for 100 W into 2 kΩ).
  - Too little L or C to reach low bands or extreme loads. Coupler errors at low power. Clone boards with substituted cores and capacitors.
  - See [RF switches](../06-rf-circuits/rf-switches-attenuators-limiters.md) for relay vs semiconductor switches.
- **Remote (at-antenna) tuners.** Weatherproof boxes at the feed point. Some take DC over the coax through bias-T inserters; others, such as Icom's AH-4 (manufacturer), use a separate control cable. All need a good common-mode choke on the coax at the tuner, because an end-fed wire against a tuner box drives current onto the coax shield otherwise ([baluns/chokes](../08-antennas/antenna-matching-and-baluns.md)).
- **Internal tuners** are small relay L-networks with limited range (16.7–150 Ω for the IC-7300 [4]). They are meant for a resonant antenna slightly off frequency.

## Design equations & rules of thumb

| Quantity | Equation / rule | Typical value |
|---|---|---|
| Total mismatched-line loss | $10\log[(a^2-|\Gamma|^2)/(a(1-|\Gamma|^2))]$ | 30 m RG-58, 14 MHz, SWR 10: 4.1 dB |
| SWR at the rig | $|\Gamma_{in}| = |\Gamma_L|10^{-A/10}$ | open at 30 m RG-58, 28 MHz: 4.7:1 |
| L-network loaded Q | $Q_n = \sqrt{R_h/R_l-1}$ | 12.5 → 50 Ω: 1.7 |
| L-network loss | ≈ $Q_n/Q_u$ (fraction) | Q_n 1.7, Q_u 100: 1.7 % (0.08 dB) |
| Loading a short whip | $R_{coil} = X/Q_u$ vs $R_{rad}$ | 500 Ω, Q 300, R_rad 5 Ω: 1.25 dB |
| T-tuner setting | maximum capacitance that still matches | avoids 1–4 dB extra loss |
| Voltage at a high-Z tuner output | $V = \sqrt{PR}$ | 100 W into 2 kΩ: 447 V rms |
| Internal ATU range | ≈ SWR 3:1 | IC-7300 16.7–150 Ω [4] |
| Auto-tuner minimum power | a few watts to sense | ATU-100 ≥ 5 W [3] |

**Auto-tuner building blocks**:

| Block | Typical implementation | What limits it |
|---|---|---|
| Forward/reflected sensor | tandem-match transformer coupler + diode detectors | directivity (sets lowest measurable SWR), diode threshold at low power |
| Controller | small MCU (ATU-100: PIC16F1938 class) | search algorithm, memory size |
| Inductor bank | 5–7 relay-switched air or toroidal coils, binary or uneven steps | Q, self-resonance of the largest coil on 10–6 m |
| Capacitor bank | 5–7 relay-switched C0G/mica capacitors, 10 pF–1 nF | voltage rating at high-Z loads |
| Topology relay | moves the C bank to the input or output side of L | needed for R < 50 Ω vs R > 50 Ω |
| Relays | signal relays (cheap) or RF-rated relays | hot-switching damage, contact capacitance, current |

**Choosing a tuner**:
1. Range: the impedances your antenna presents on every band (measure with a [NanoVNA](../17-test-measurement/nanovna-librevna-practical.md) or model in NEC).
2. Location: at the antenna if the feeder is coax and the SWR is high.
3. Power and voltage ratings at the extreme impedance.
4. Balanced or unbalanced output: ladder line needs a balanced tuner, or a 1:1 current balun at an unbalanced tuner's output.
5. Inductor Q and capacitor range (T-tuners need large C for low loss).
6. Memories, tune time and minimum tune power for auto-tuners.

## Worked examples

**1. "My tuner shows 1:1, so my 80 m signal must be fine."** A 7 MHz dipole is used on 3.6 MHz, fed with 30 m of RG-58, with an auto-tuner at the rig. The antenna presents roughly 10 − j400 Ω, i.e. SWR ≈ 325 on 50 Ω coax. Total line loss is 14.1 dB, so only about **4 %** of 100 W (≈ 4 W) reaches the antenna; the rest heats the coax. The tuner reports 1:1 because it matched the rig to whatever the coax input presents. Options:
- Swap to 450 Ω ladder line: 2.9 dB (52 % delivered).
- Put the tuner at the antenna with coax behind it. Only the matched coax loss (0.65 dB) plus the tuner's own loss remains: 0.54–0.79 dB for this very reactive, low-R load with a Q 300–200 coil, ≈ 1.2–1.4 dB in total (70–75 % delivered).
- Add a resonant 80 m antenna.

**2. LoRa-band analogue: why a mismatched rocket antenna can't be "fixed" in the ground station.** At 433 MHz, 2 m of RG-316 (0.72 dB/m, so 1.44 dB) to a flight antenna with SWR 5. Total loss: $a = 10^{0.144} = 1.393$, $|\Gamma| = 0.667$, giving $TL = 10\log[(1.94 - 0.444)/(1.393 \times 0.556)]$ = **2.87 dB**, against 1.44 dB matched. A matching network at the radio end would recover the mismatch loss at the radio (≈ 2.55 dB for SWR 5) but not the extra 1.4 dB burnt in the cable. Match **at the antenna feed**, on the flight board or in the nosecone ([antenna matching](../08-antennas/antenna-matching-and-baluns.md)).

**3. A portable auto-tuner on a random wire.** A 17.7 m wire with a 9:1 unun gives worst-band SWR ≈ 10 behind the unun ([wire antennas](../08-antennas/wire-antennas-hf-random-wire-fan-dipole.md)). Put the auto-tuner *at the feed point* (or the unun there and only 2 m of coax to the tuner). With 2 m of RG-58 at 14 MHz ($A$ ≈ 0.09 dB), SWR 10 costs ≈ 0.4 dB. With 30 m it costs 4.1 dB. Tune at 5–10 W, then raise the power.

**4. T-tuner setting matters.** A 12.5 Ω load at HF with $Q_u$ = 100. A well-set T (maximum input C) loses 0.09 dB; a setting with small input C (|X₁| > 1 kΩ) can lose 3.7 dB (`e10_tuner_loss.py`). Both show 1:1. With a manual T tuner, start with both capacitors at maximum capacitance and use the least inductance that dips the SWR.

**5. Receive-only SWL with a 10 m wire.** The wire's impedance varies wildly with frequency. On a receiver, mismatch loss is $10\log(1-|\Gamma|^2)$: 3:1 costs 1.25 dB, 10:1 costs 4.8 dB. Below about 10 MHz, atmospheric and man-made noise ([P.372](../07-noise-linearity/thermal-noise-and-noise-temperature.md)) is typically 20–50 dB above kTB, so a 5 dB loss lowers signal and noise together and SNR is unchanged. A tuner earns its place as a preselector against strong broadcast signals, and above ~20 MHz in quiet locations, where external noise drops towards the receiver's own floor.

**6. Designing an L-network for a measured load.** A NanoVNA at a 7 MHz antenna feed reads 200 + j0 Ω, and the job is to match it to 50 Ω. $Q_n = \sqrt{200/50 - 1}$ = 1.732. Use a series element on the 50 Ω side and a shunt element across the 200 Ω load.
- Series inductor: $X_s = Q_n \times 50$ = 86.6 Ω, so $L = 86.6/(2\pi \cdot 7\times10^6)$ = **1.97 µH**.
- Shunt capacitor across the load: $X_p = 200/Q_n$ = 115.5 Ω, so $C = 1/(2\pi \cdot 7\times10^6 \cdot 115.5)$ = **197 pF**.
- Loss with a Q 200 coil: ≈ $Q_n/Q_u$ = 0.9 % (0.04 dB).
- Both values are inside an ATU-100's range (0.05–8.5 µH, 10 pF–1.87 nF), with C switched to the output (high-impedance) side.
- For a reactive load, first absorb the reactance into the series element (e.g. 200 + j50 Ω: the series element must also cancel the transformed reactance; let the Smith chart or `e10_tuner_loss.py`'s `match_L` do it).

## Practical notes
- **Tune at low power** (5–10 W, or the manufacturer's tune power), then increase. Never switch a relay tuner or band-switch a manual one while transmitting.
- **Voltage and current extremes**: high-impedance loads stress capacitors and relay contacts (hundreds of volts); low-impedance loads stress inductors and contacts with amperes of current. Check both against the rating at your power.
- **Balanced feeders**: put a 1:1 current balun (choke) at an unbalanced tuner's output, or use a true balanced tuner. A 4:1 voltage balun at very high or low impedances can itself overheat.
- **Remote tuners**: choke the coax at the tuner. Keep the counterpoise or radial system at the tuner, not the coax shield. Weatherproof the coax connector ([coax practicalities](../18-components-parts/coax-and-connector-practicalities.md)).
- **Measure the system, not the tuner.** A NanoVNA at the antenna feed point tells you what the tuner must handle and how much line loss to expect. A wattmeter at the antenna (or a field-strength meter) verifies delivered power.

**Manual T-tuner procedure** (with an SWR meter or NanoVNA at the tuner input):
1. Set both capacitors to maximum capacitance (the plates fully meshed).
2. With the receiver on, peak the band noise with the inductor (a quick receive-side pre-tune).
3. Transmit at 5–10 W. Find the inductor setting that gives the deepest SWR dip, using the *least* inductance that dips.
4. Trim the output capacitor, then the input capacitor, for the minimum. Reduce capacitance only as far as needed to reach about 1.2:1.
5. Record the settings per band segment. Raise the power and re-check that the SWR does not drift; drift means heating or arcing.

**When you do not need a tuner at all**:
- Resonant antennas on their design band (VSWR < 2: mismatch loss < 0.5 dB, and most transmitters tolerate it).
- VHF/UHF/LoRa links. Mismatch there is fixed at the antenna feed with a matching network on the board ([matching](impedance-matching-lumped-and-distributed.md), [antenna matching](../08-antennas/antenna-matching-and-baluns.md)), never with an HF-style tuner at the radio.
- Receive-only use below ~20 MHz where external noise dominates (example 5).

## Common mistakes & misconceptions
- **"A tuner adds or subtracts wire, so it fixes a bad antenna"** (D3 #516). It is a matching network at its own terminals. The antenna's current distribution, efficiency and pattern are unchanged ([wire antennas](../08-antennas/wire-antennas-hf-random-wire-fan-dipole.md)).
- **"A tuner at the rig removes the SWR on the feedline"** (D3 #210). The standing wave between tuner and antenna is set by the antenna and the line. Only the line's loss (which grows with SWR) and the tuner's position change what is lost: example 1 delivers 4 %.
- **"Reflected power is lost, so 3:1 is a disaster."** With a matched source end it is re-reflected. What is lost is the extra *line* loss, which is small on short or low-loss lines (30 m LMR-400 at 14 MHz, SWR 3: 0.72 vs 0.45 dB).
- **"A good SWR at the rig proves the antenna is good."** Coax loss masks the mismatch: an open circuit at the end of 30 m RG-58 at 28 MHz reads 4.7:1.
- **"All T-tuner settings that give 1:1 are equal."** Loss varies by several dB. Use maximum capacitance.
- **"An internal tuner handles any wire."** Typically 3:1 only (16.7–150 Ω for the IC-7300 [4]).
- **"Ordinary relays are fine in a tuner."** Only within their RF voltage, current and capacitance limits, and never hot-switched ([RF switches](../06-rf-circuits/rf-switches-attenuators-limiters.md)) (D3 #517).
- **"A tuner improves receive-only reception."** Rarely as gain. Mainly as a preselector (D3 #4/#219).
- **"A 1:1 SWR at the rig means the tuner is efficient."** Every lossless *and* lossy setting that matches shows 1:1. Tuner loss must be measured as power out ÷ power in (example 4).
- **"Ladder line needs no balun."** An unbalanced tuner driving ladder line puts common-mode current on the line and into the shack. Use a balanced tuner, or a 1:1 current balun at the tuner output.

## How to simulate / verify
- `python3 tools/verify/e10_tuner_loss.py` (output `tools/verify/e10_tuner_loss_output.txt`, all checks pass). It checks the mismatched-line formula against exact bookkeeping, produces the loss tables and same-antenna comparisons, the SWR at the rig, the lossy L/T network efficiency vs load and $Q_u$ (exact ABCD), the $Q_n/Q_u$ rule, and the auto-tuner state count.
- Quick check of your own feedline (paste into Python):

```python
import math
def total_loss_db(matched_db, swr):
    a = 10 ** (matched_db / 10); g = (swr - 1) / (swr + 1)
    return 10 * math.log10((a * a - g * g) / (a * (1 - g * g)))
def swr_at_rig(matched_db, swr_ant):
    g = (swr_ant - 1) / (swr_ant + 1) * 10 ** (-matched_db / 10)
    return (1 + g) / (1 - g)
print(total_loss_db(1.31, 10), swr_at_rig(1.31, 10))   # 30 m RG-58 at 14 MHz -> 4.14 dB, 4.0:1
```

- scikit-rf: `skrf.tlineFunctions.zl_2_total_loss` gives the same mismatched-line loss ([reflections page](reflections-vswr-return-loss-mismatch.md)).
- Model the antenna in NEC ([NEC](../16-simulation-tools/nec-antenna-modelling.md)), export Z(f), and run it through the line and network functions in the script to choose the tuner location and range before buying.
- Bench: a NanoVNA on the tuner output with a resistor-capacitor dummy (e.g. 12 Ω or 600 Ω plus reactance) and a power meter or calorimetric dummy load at the output measure tuner loss directly ([bench recipes](../17-test-measurement/bench-measurement-recipes.md)).

## Open questions / gaps
- HF cable losses are extrapolated from the KB's 433–2450 MHz fits ($k_1\sqrt f + k_2 f$). The commonly quoted Belden 8240 HF figures are ~20 % higher, so the RG-58 numbers here are slightly optimistic. Ladder-line loss (0.2 dB/100 ft at 14 MHz) is an assumed typical dry value; wet window line can be several times worse.
- The antenna impedances in the examples are order-of-magnitude values, not NEC runs of a specific installation.
- The ATU-100 search algorithm is not documented in detail in the manual read [3]; the coarse–fine description here is generic.
- The ARRL Antenna Book tuner chapter [1] was not re-read for this pass; its T-network loss curves were not compared numerically.
- Not covered: tuners for magnetic loops (the loop's own capacitor is the tuner; see [loop antennas](../08-antennas/loop-antennas.md)); balanced-tuner topologies (link-coupled, balanced T) in detail; the heating of baluns at extreme impedances.
- Not measured: an actual auto-tuner's loss across its range (calorimetric). A bench test with known R+jX dummy loads would calibrate the T-network table.
- The relay hot-switching failure rate is anecdotal (forum reports), not quantified.

## Sources
1. ARRL, *The ARRL Antenna Book*, 24th ed., 2019 — transmatches, L/T/Pi networks, feedline loss at high SWR, ladder line, remote tuners. (handbook; background)
2. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — §2.7 lossy lines and §5.1 L-section matching (loaded Q). (textbook); S. D. Stearns (K6OIK), "Transmission line power paradox and its resolution," Pacificon 2014 — total loss of a mismatched line. https://www.fars.k6ya.org/docs/K6OIK-A_Transmission_Line_Power_Paradox_and_Its_Resolution.pdf (conference talk)
3. OZ9F (translation of N7DDC documentation), *Technical Description of the Autotuner board ATU-100 Extended* — 5–7 L and C relays, base model 0.05–4.5 µH and 10 pF–1 nF, max 8.53 µH, C before/after L, retune when SWR > 1.3, 100 W working/150 W measured, ≥ 5 W to tune, tunes on any signal. http://www.oz9f.dk/wp-content/uploads/2020/02/ATU-100_Extended_Board_User_Manual_eng.pdf (designer manual)
4. Icom America, *IC-7300* product specifications / instruction manual — internal tuner 16.7–150 Ω unbalanced (SWR < 3:1), tuning to ≤ 1.5:1. https://www.icomamerica.com/lineup/products/IC-7300/ (manufacturer)
5. Times Microwave Systems, LMR-400 attenuation equation (0.12229√f + 0.00026f dB/100 ft); Belden 8240 (RG-58) attenuation table — as fitted in [coax-and-cables](coax-and-cables.md). (datasheets)
6. Forum demand: EEVblog (auto-tuner for SWL), QRZ (tuners and SWL; Icom AH-4 feeding), SOTA reflector (portable auto-tuners; internal tuners on KX2/KX3), Hackaday (automatic antenna tuner 2014; "What's wrong with this antenna tuner" 2025), YouTube (KB9VBR, lcfgroup, Waters & Stanton) — `gaps/D3-forums-youtube.md` rows 4, 219, 224, 345, 346, 464, 492, 517, 634, 673, 674; `gaps/D2-reddit.md` rank 24. (forum — anecdotal)
