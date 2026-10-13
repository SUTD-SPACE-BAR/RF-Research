---
title: Multiple access and duplexing — FDMA, TDMA, CDMA, OFDMA, ALOHA and slotted-ALOHA throughput, CSMA/LBT, FDD vs TDD, duplexers vs T/R switches, and a launch-day channel plan
domain: 10-comms-modulation
slug: multiple-access-and-duplexing
tags: [multiple-access, fdma, tdma, cdma, ofdma, sdma, aloha, slotted-aloha, throughput, poisson, capture-effect, csma, lbt, cad, hidden-terminal, guard-time, gnss-time, duplexing, fdd, tdd, half-duplex, duplexer, t-r-switch, circulator, desensitisation, near-far, channel-plan, lora, launch-day]
prerequisites: [../00-math-foundations/probability-random-processes-and-psd.md, spread-spectrum-dsss-fhss-css.md, packet-framing-protocols.md]
related:
  - ofdm.md
  - spread-spectrum-dsss-fhss-css.md
  - synchronization-carrier-timing.md
  - ../15-lora-ism-radios/lorawan-vs-raw-lora.md
  - ../15-lora-ism-radios/lora-mesh-capacity-and-congestion.md
  - ../15-lora-ism-radios/ism-band-plans-duty-cycle.md
  - ../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md
  - ../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md
  - ../15-lora-ism-radios/rocket-telemetry-radio-design.md
  - ../15-lora-ism-radios/ground-station-design.md
  - ../06-rf-circuits/rf-switches-attenuators-limiters.md
  - ../06-rf-circuits/circulators-isolators.md
  - ../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md
  - ../12-phased-arrays/adaptive-beamforming-doa.md
  - ../19-regulations-safety/singapore-imda-rules.md
  - ../21-gnss/gnss-timing-1pps.md
level: mixed
confidence: high
last_updated: 2026-10-14
---

# Multiple access and duplexing

## Questions this page answers
- How do many radios share one band — FDMA, TDMA, CDMA, OFDMA and space division?
- What is ALOHA, and why is its maximum throughput only 18 % (37 % slotted)?
- If six rockets share one LoRa channel, what fraction of packets survive?
- Does the LoRa capture effect or using different spreading factors save me?
- What are CSMA and listen-before-talk, and why do hidden terminals break them?
- How long must the guard time be in a TDMA schedule, and can GNSS time synchronise it?
- What is the difference between FDD and TDD, and when do I need a duplexer rather than a T/R switch?
- How much isolation must a duplexer give, and what is receiver desensitisation?
- Why can another team's transmitter on the next pad wipe out my ground station?
- How should several teams and vehicles share frequencies on a launch day?

## TL;DR
- **Four dimensions to share:** frequency (FDMA — separate channels, guard bands), time (TDMA — slots with guard times), code (CDMA — spreading codes; LoRa's spreading factors are a weak form), and space (SDMA — directional antennas, separation). OFDMA allocates subcarriers inside one OFDM signal. **Duplexing** separates a link's two directions by frequency (FDD) or time (TDD).
- **Pure ALOHA** (transmit whenever you like): a packet survives only if no other starts within ±1 packet time, so with Poisson offered load G (packets per packet-time) $S=Ge^{-2G}$, **max 1/(2e) = 18.4 % at G = 0.5**. **Slotted ALOHA** halves the vulnerable window: $S=Ge^{-G}$, **max 1/e = 36.8 % at G = 1**. Verified by simulation.
- **Per-packet survival** among N Poisson senders with rate r and airtime $T_a$: $P=e^{-2(N-1)rT_a}$. **Six rockets at 2 Hz on one SF7/125 kHz channel (32 B, 71.9 ms)** → only **24 %** of packets survive (MC 23 %); two rockets → 75 %. Shared channels do not work for telemetry.
- **Capture** (LoRa same-SF: the stronger packet survives if ≥ 6 dB above the rest) raises slotted-ALOHA throughput at G = 1 from 0.37 to ~0.5 with 8 dB power spread — helpful, but it is the *strong* one that survives. **Different SFs are only quasi-orthogonal (~−16 dB)**; near the pad, path-loss disparities of 30–46 dB defeat both.
- **CSMA** (listen first): non-persistent CSMA gives $S=\frac{Ge^{-aG}}{G(1+2a)+e^{-aG}}$ (a = propagation delay / packet time), up to 0.82 for a = 0.01 — far better than ALOHA *if everyone can hear everyone*. Ground stations cannot hear each other behind terrain and all hear the rocket: classic hidden terminals. LoRa's CAD implements LBT.
- **TDMA on GNSS time** works well: a 2 Hz frame (0.5 s) holds **six 71.9 ms LoRa slots with ~4 ms guards (95 % efficiency)**; guards come from scheduling jitter and propagation (30 km = 0.1 ms), not clock drift, when PPS-disciplined.
- **FDD needs a duplexer**: e.g. 30 dBm TX with −135 dBc/Hz noise at the RX frequency needs **≈ 73 dB** of TX-to-RX isolation to keep desense ≤ 0.4 dB (and ~70 dB to keep the carrier below a −40 dBm blocker limit). **TDD needs only a T/R switch** — but 33 dBm through 25 dB of switch isolation is still 8 dBm at the LNA. LoRa modules are half-duplex TDD radios.
- **Launch-day plan:** one channel per vehicle (FDMA; e.g. ten 1 MHz E22 channels in 430–440 MHz under an amateur licence, only two in the licence-exempt 433.05–434.79 MHz band; for the E220, **2–3 channels in 866–869 MHz** (CH 17/18 with the E22, CH 16 only if no E22 is on CH 23; 500 mW e.r.p., the preferred exempt band) and 8 in 917–925 MHz (100 mW e.r.p., 1 % duty — too little for 10 Hz telemetry)), TDMA on GNSS time inside a team, uplink in TDD slots, and ground stations sited away from other teams' pads.

## Intuition (no math)
A radio band is a shared room. If everyone talks at once in the same voice, nobody is understood. There are only a few ways to share the room:
- **Different pitches** — FDMA: each pair talks on its own frequency, with a little space between channels so they don't bleed into each other.
- **Taking turns** — TDMA: everyone gets a time slot, which needs everyone to share a clock and leave short gaps between turns.
- **Different languages** — CDMA: everyone talks at once, but each conversation is coded so that a listener tuned to one code hears the others as faint background noise — provided nobody is shouting much louder than the rest (the near-far problem).
- **Different corners of the room** — SDMA: directional antennas and distance.

**ALOHA** is the "just talk and hope" approach: send whenever you have something to say, and if two packets overlap, both are lost. It works beautifully when the room is quiet and degrades fast as traffic grows. The surprise is how little traffic it takes: with packets arriving at random, a packet is safe only if nobody else started during a window *twice* its own length (anyone who started up to one packet-length before, or anyone starting during it). The best you can ever get is 18 % of the channel's capacity; if everyone agrees to start only at slot boundaries, the window halves and the best is 37 %. That's why the formula matters for LoRa networks (LoRaWAN uplinks are ALOHA) and for rocket telemetry: several teams sharing one channel lose most of their packets.

**Listening before talking** (CSMA) helps a lot — if you can hear everyone. On a launch range, ground stations behind hills cannot hear each other, while everyone hears the rocket high in the sky. Listening then gives false confidence (hidden terminals).

**Duplexing** is about one link's two directions. A walkie-talkie is time-division duplex: press to talk, release to listen; one antenna, a switch, and the transmitter and receiver never operate together. A phone call on cellular FDD transmits and receives at once on two frequencies, which requires a duplexer — a pair of sharp filters that keeps the transmitter's huge power (and its noise) out of the sensitive receiver next to it. LoRa radios are half-duplex: a switch, not a duplexer.

## The math

### Level 1 — sharing frequency, time and code

- **FDMA:** N channels of bandwidth $B_c$ with guard $B_g$ need total bandwidth $N(B_c+B_g)$. The guard must cover oscillator offsets (±ppm × carrier: ±20 ppm at 433 MHz is ±8.7 kHz), Doppler (Mach 3 at 433 MHz is ±1.49 kHz), the transmit spectrum's skirts and the receiver's selectivity.
- **TDMA:** a frame of length $T_F$ holds slots of length $T_s=T_a+T_g$ (packet airtime + guard). Efficiency $T_a/T_s$; each user's update rate $1/T_F$.
- **CDMA/spread spectrum:** processing gain $G_{proc}=B_{spread}/R_b$ lets $K$ equal-power users share a band with per-user SINR $\approx G_{proc}/(K-1)$ (ignoring noise) — but only if received powers are equal (power control).
- **Duplex:** FDD uses two frequencies separated by the *duplex spacing*; TDD alternates direction in time, with a guard of at least the round-trip propagation plus TX/RX switching time.

### Level 2 — random access: ALOHA, slotted ALOHA, capture and CSMA

**Traffic model.** Packets of fixed duration $T$ (the unit of time). New and retransmitted packets together form a Poisson process of rate $G$ per $T$ (the *offered load*); throughput $S$ is the rate of successful packets per $T$ (0 ≤ S ≤ 1). The Poisson assumption is the many-independent-users limit [1], [2].

**Pure ALOHA** [1]. A packet starting at $t_0$ collides with any packet starting in $(t_0-T,\ t_0+T)$ — the *vulnerable period* $2T$. For Poisson arrivals, P(no other start in 2T) $=e^{-2G}$. Hence
$$S=G\,e^{-2G},\qquad\frac{dS}{dG}=e^{-2G}(1-2G)=0\Rightarrow G^*=\tfrac12,\quad S_{\max}=\frac{1}{2e}=0.184 .$$
**Slotted ALOHA** [3]. Starts are aligned to slot boundaries, so a packet collides only with others in the *same* slot: $P=e^{-G}$, $S=Ge^{-G}$, $G^*=1$, $S_{\max}=1/e=0.368$. Both verified by simulation within 1–3 % at G = 0.25–2. Above $G^*$ the throughput *falls* — retransmissions add load and the channel can collapse (ALOHA instability), which is why random back-off with growing windows is needed.

**Finite number of senders.** One sender among N, each others' packets Poisson at rate $r$ (packets/s) with airtime $T_a$:
$$P_{\rm success}=e^{-2(N-1)rT_a}\quad(\text{pure}),\qquad e^{-(N-1)rT_a}\ (\text{slotted, if slots}=T_a).$$
Periodic senders with independent random phases behave close to this (verified by MC with random Poisson streams: 0.233 vs 0.237 for N = 6, 2 Hz, 71.9 ms). Strictly periodic senders with *drifting* clocks are worse: two transmitters with nearly equal periods slide into each other and collide for many consecutive packets — a burst outage rather than random losses.

**Capture.** If a receiver decodes the strongest of several overlapping packets when it exceeds the rest by a threshold (LoRa same-SF: ≥ 6 dB, and the strong packet's preamble must not start too late — [LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)), some collisions still deliver one packet. MC (slotted, G = 1, received powers log-normal with 8 dB spread): S = 0.505 vs 0.368 without capture. Capture favours near/strong transmitters — it is not fairness.

**CSMA and listen-before-talk** [4]. Let $a$ = (propagation + detection delay) / packet time. In **non-persistent CSMA**, a station with a packet senses the channel; if busy it reschedules after a random delay, if idle it transmits. Collisions happen only if another station starts within $a$ of the first (before it can sense it). Renewal argument: the channel alternates idle periods (mean $1/G$, Poisson) and busy periods. A busy period begun at $t$ contains a success iff no other arrival occurs in $(t,t+a)$, probability $e^{-aG}$; its mean length is $1+2a-\frac{1-e^{-aG}}{G}$ (the last colliding arrival is on average $a-\frac{1-e^{-aG}}{G}$ after the first, then the packet plus a further $a$ to clear). Throughput = useful time / cycle:
$$S=\frac{e^{-aG}}{1+2a-\frac{1-e^{-aG}}{G}+\frac1G}=\frac{G\,e^{-aG}}{G(1+2a)+e^{-aG}} .$$
Verified by event simulation (within 1 % at a = 0.01, 0.1; G = 0.5–10). Maxima: 0.815 (a = 0.01, G ≈ 9.4), 0.515 (a = 0.1, G ≈ 2.5). For LoRa, $a$ is tiny in propagation terms (30 km = 0.1 ms vs 72 ms packets) but the effective sensing delay includes the radio's CAD time (a few symbols) and TX/RX turnaround — still small, so CSMA would be very efficient **if all stations could hear each other**.

**Throughput vs offered load** (formulas above; the ALOHA columns and CSMA at a = 0.01/0.1 are simulation-verified):

| G (offered load) | pure ALOHA | slotted ALOHA | np-CSMA, a = 0.01 | np-CSMA, a = 0.1 |
|---|---|---|---|---|
| 0.1 | 0.082 | 0.090 | 0.091 | 0.089 |
| 0.25 | 0.152 | 0.195 | 0.199 | 0.191 |
| 0.5 | **0.184** | 0.303 | 0.331 | 0.307 |
| 1 | 0.135 | **0.368** | 0.493 | 0.430 |
| 2 | 0.037 | 0.271 | 0.649 | 0.509 |
| 3 | 0.007 | 0.149 | 0.722 | 0.512 |

At light load all schemes deliver nearly everything offered ($S\approx G$); they differ in how gracefully they saturate. For telemetry the useful figure is the *loss* $1-S/G$: already 39 % for pure ALOHA at G = 0.25.

**Hidden and exposed terminals.** Sensing measures the channel at the *transmitter*, but collisions happen at the *receiver*. Two ground stations behind a ridge both hear the rocket but not each other: each senses "idle" and both transmit uplinks into the rocket — hidden terminals. Conversely, a strong nearby transmitter on a different link makes a station defer unnecessarily — exposed terminal. RTS/CTS handshakes (Wi-Fi) mitigate this; for rocket uplinks, schedule them (TDMA) instead.

### Level 3 — FDMA/TDMA/CDMA/OFDMA in practice, duplexing, near-far and a launch-day plan

**FDMA design.** Channel spacing must exceed the occupied bandwidth plus frequency uncertainty, and the receiver's adjacent-channel selectivity (ACS) must exceed the worst *power disparity* between a wanted far signal and an unwanted near one. That disparity is set by geometry (near-far, below), not by the modulation. Practical grids: EBYTE E22-400 modules tune 410.125 + CH MHz (1 MHz steps) and E220-900 850.125 + CH MHz ([modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md)) — counting channels whose 125 kHz occupied band fits wholly inside an allocation: **10** in 430–440 MHz (amateur, licensed), **2** in 433.05–434.79 MHz (SG licence-exempt SRD, 10 mW e.r.p.), **2–3** in 866–869 MHz (E220 CH 16–18; CH 17/18 when paired with an E22, preferred: 500 mW e.r.p., no duty limit stated) and **8** in 917–925 MHz (E220; 100 mW e.r.p., 1 % duty) — legal limits per band are on the [band-plan page](../15-lora-ism-radios/ism-band-plans-duty-cycle.md) and in [domain 19](../19-regulations-safety/singapore-imda-rules.md). Bare SX126x chips tune in ~1 Hz steps, so finer grids (e.g. 200 kHz) are possible with a TCXO. (The [LoRa mesh capacity page](../15-lora-ism-radios/lora-mesh-capacity-and-congestion.md) quotes ≈ 11 × 125 kHz channels for the same band — a tighter packing than the 200–250 kHz spacing with drift margin assumed here; the count depends entirely on the guard you allow. Its CSMA maxima, 0.65 at a = 0.044 and 0.31 at a = 0.31, agree with the formula on this page: 0.646 and 0.314.)

**TDMA design.** Guard time per slot $T_g\ge2\epsilon_{sync}+\tau_{prop,\max}+\tau_{turnaround}$, where $\epsilon_{sync}$ is each node's timing uncertainty. With **GNSS PPS** both ends know time to ~µs; the dominant terms are MCU/UART scheduling jitter (assume ~2 ms for UART LoRa modules; far less with a bare chip and a hardware timer) and propagation (30 km → 0.1 ms). Free-running 20 ppm crystals drift 0.2 ms in 10 s between resyncs — tolerable if resynchronised every few seconds from a beacon. If the GNSS fix is lost (boost, [GNSS limits](../21-gnss/gnss-on-rockets-dynamics-and-limits.md)), the node must hold time on its oscillator — budget the holdover drift. See [GNSS timing](../21-gnss/gnss-timing-1pps.md).

**CDMA and LoRa.** LoRa chirp spread spectrum gives processing gain $2^{SF}$, so it tolerates in-band interference *weaker* than itself; different SFs are only quasi-orthogonal (other-SF interference fails beyond ~16 dB stronger) and same-SF signals collide (capture ≥ 6 dB). Classical DS-CDMA requires tight power control — impossible between a rocket and a pad transmitter. FHSS (frequency hopping) spreads collisions across channels: with $N_h$ hop channels and uncoordinated hoppers, the per-hop collision probability falls by $N_h$ but is not zero ([spread spectrum](spread-spectrum-dsss-fhss-css.md)). **OFDMA** assigns sets of subcarriers (resource blocks) of one OFDM symbol stream to different users, with a common time/frequency grid and timing advance so that uplink signals arrive orthogonal ([OFDM](ofdm.md)); it needs a central scheduler. **SDMA** uses beams and nulls ([adaptive beamforming](../12-phased-arrays/adaptive-beamforming-doa.md)) — on a range, separation and antenna directivity are the cheapest SDMA.

**FDD and the duplexer.** In FDD the transmitter and receiver run simultaneously at frequencies $f_{TX}$ and $f_{RX}$ separated by the duplex spacing. The duplexer (two band-pass filters joined at the antenna: cavity, helical, ceramic, SAW/BAW — [RF filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md)) must provide:
1. **TX-noise rejection at $f_{RX}$:** transmitter noise density at the RX offset, $P_{TX}+L_{TX}(\Delta f)$ dBm/Hz, attenuated by the isolation $I$, must sit below the receiver noise floor $-174+NF$ dBm/Hz. Desensitisation from an interference density $N_i$ added to the receiver's own $N_r$: $\Delta=10\log_{10}(1+N_i/N_r)$ dB — 0.41 dB at 10 dB below, 3.01 dB when equal (verified). Example: 30 dBm, −135 dBc/Hz at the RX offset, NF 6 dB → $I\ge(30-135)-(-168)+10$ = **73 dB**.
2. **TX-carrier rejection at the receiver input:** keep $P_{TX}-I$ below the receiver's blocking/compression limit (assume −40 dBm here → **70 dB**); otherwise reciprocal mixing and LNA compression desensitise it ([dynamic range](../07-noise-linearity/_index.md)).
3. **RX-band rejection in the TX path** (the RX filter) and low insertion loss in both.
Amateur repeaters do this with large cavity duplexers at a few MHz spacing. Circulators add only ~20 dB isolation and do not filter noise ([circulators](../06-rf-circuits/circulators-isolators.md)).

**TDD and the T/R switch.** In TDD the receiver is off (or its LNA protected) while transmitting, so the requirement is protecting the LNA and fast switching, not continuous isolation: a PIN/SOI switch with 20–40 dB isolation is enough *if* the leakage is below the LNA's damage level — 33 dBm through 25 dB of isolation leaves **8 dBm** at the LNA, just under EBYTE's 10 dBm rating ([RF switches](../06-rf-circuits/rf-switches-attenuators-limiters.md)). Guard time must cover TX→RX turnaround (hundreds of µs for LoRa chips, longer through UART modules) and round-trip propagation (0.2 ms at 30 km). LoRa modules, LoRaWAN class A (two receive windows after each uplink) and most hobby links are half-duplex TDD.

**Near–far on a launch range.** Free-space path loss differs by $20\log_{10}(d_{far}/d_{near})$: a rocket at 30 km vs another team's pad transmitter 1 km from your ground station: **29.5 dB**; a rocket at 10 km vs a neighbouring pad 50 m away: **46 dB** (verified). That exceeds same-SF capture (6 dB) and the inter-SF tolerance (~16 dB), so on the same channel the near transmitter wins regardless of SF. On adjacent channels it must be beaten by the receiver's adjacent-channel selectivity plus your SNR margin — check the datasheet ACS/blocking at 1 MHz offset against these disparities, and remember front-end overload (blocking) can desensitise even far-off channels if the near signal is strong enough to compress the LNA.

**Which access scheme for which job.**

| Scheme | Needs | Strengths | Weaknesses | Where you meet it |
|---|---|---|---|---|
| FDMA | channel plan, frequency accuracy, receiver selectivity | simple, continuous links, no timing | spectrum per user; near-far via adjacent-channel leakage | one channel per rocket/team; analogue FM; GLONASS |
| TDMA | common time (GNSS PPS, beacon), guard times | one channel, deterministic latency, no collisions | sync loss = collisions; guard overhead | multi-vehicle team links, GSM, satellite TDMA |
| CDMA / spread spectrum | codes, power control | graceful overload, interference tolerance | near-far kills it without power control | GPS (CDMA), IS-95/WCDMA, LoRa SFs (weakly) |
| OFDMA | central scheduler, tight sync, timing advance | flexible allocation, multipath-robust | complexity | LTE/5G, Wi-Fi 6 |
| ALOHA | nothing | trivial, no coordination | ≤ 18 % (37 % slotted), collapses under load | LoRaWAN uplinks, sporadic sensors |
| CSMA/LBT | sensing (CAD) | high throughput if all hear all | hidden terminals; latency | Wi-Fi, LBT-regulated bands, uplinks in range |
| SDMA | directional antennas, geometry | reuse the same channel | needs separation/pointing | tracking Yagis, cellular sectors |

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| pure ALOHA $S=Ge^{-2G}$, max $1/2e$ | Poisson, fixed length | 18.4 % at G = 0.5 |
| slotted ALOHA $S=Ge^{-G}$, max $1/e$ | slot = packet | 36.8 % at G = 1 |
| $P_{\rm success}=e^{-2(N-1)rT_a}$ | N independent senders | 6 × 2 Hz × 71.9 ms → 24 % |
| np-CSMA $S=\frac{Ge^{-aG}}{G(1+2a)+e^{-aG}}$ | all hear all, delay a | 0.82 max at a = 0.01 |
| TDMA guard $\ge2\epsilon_{sync}+\tau_{prop}+\tau_{turn}$ | | GNSS-timed: ~ms |
| FDMA spacing > occupied BW + 2×(ppm·f + Doppler) | | 20 ppm @ 433 MHz = ±8.7 kHz |
| desense $10\log(1+N_i/N_r)$ | | 0.41 dB at −10 dB |
| FDD isolation $\ge P_{TX}+L_{TX}(\Delta f)-(-174+NF)+10$ | TX noise | 30 dBm, −135 dBc/Hz → 73 dB |
| near-far $20\log(d_{far}/d_{near})$ | free space | 30 km vs 1 km: 29.5 dB |
| LoRa ToA (32 B): SF7/125 71.9 ms; SF7/500 18.0 ms; SF9/125 246.8 ms | CR 4/5, 8-sym preamble, CRC | `rfcalc.lora.time_on_air` |

## Worked examples

**1. Six teams on one channel.** Six rockets each send a 32-byte SF7/125 kHz frame (71.9 ms) at 2 Hz on the same frequency, uncoordinated. The others' offered load is $5\times2\times0.0719=0.72$ packet-times per packet-time, so $P_{\rm success}=e^{-1.44}$ = **24 %** (MC 23 %). With four rockets: 42 %; two: 75 %. Capture rescues the *closest* rocket's packets, which is the wrong one for whoever is tracking a distant rocket. Conclusion: separate channels (FDMA), always.

**2. TDMA inside one team (booster + sustainer + payload + uplink).** Frame 0.5 s (2 Hz updates), slots of 71.9 ms + ~4.1 ms guard (±2 ms scheduling jitter at both ends, 0.1 ms propagation): **6 slots per frame**, 94.6 % efficiency. Assign: slot 0 booster, 1 sustainer, 2 payload, 3 ground uplink (commands/acks), 4–5 spare/retransmissions. All nodes start their slot from the GNSS PPS edge plus slot offset; if a vehicle loses GNSS during boost it holds on its TCXO (20 ppm × 10 s = 0.2 ms — inside the guard). Switching to SF7/500 kHz (18.0 ms) gives ~22 slots per 0.5 s (if the regulations for your band allow 500 kHz).

**3. Channel plan for a launch day (several teams, Singapore context).**
- *Licence-exempt 433.05–434.79 MHz* (10 mW e.r.p.): only **2** EBYTE E22 channels (433.125, 434.125 MHz) — enough for two teams, not more; a bare SX126x on a 250 kHz (200 kHz) grid fits 7 (8) channels of 125 kHz with ±10 kHz drift margin.
- *Amateur 430–440 MHz* (licence + per-frequency consent): **10** E22 channels at 1 MHz spacing — one per team/vehicle with 1 MHz between neighbours, which also helps adjacent-channel selectivity.
- *866–869 MHz* (E220, TS SRD 29, 500 mW e.r.p., no duty limit stated — the KB's preferred exempt band for the E220): **2–3** channels (CH 16–18; use CH 17 with E22 CH 24 or CH 18 with E22 CH 23, never CH 16 next to E22 CH 23's 2nd harmonic) — enough for one or two teams' 900 MHz links.
- *917–925 MHz* (E220, LPWAN rules, 100 mW e.r.p., 1 % duty): **8** channels — but the 1 % duty cap cannot carry 10 Hz flight telemetry (a 20.5 ms SF7/500 frame at 10 Hz is already 20 %); use it only for occasional beacons ([band plans](../15-lora-ism-radios/ism-band-plans-duty-cycle.md)).
- Rules: register every team's frequency, SF/BW and TX power with the range officer; put teams whose pads are adjacent on channels farthest apart; site ground stations away from other pads (the 46 dB near-far case); test all transmitters together on the pad before flights (a "radio check" with every ground station logging RSSI of every other team); ban uncoordinated frequency hopping on the shared allocation.

**4. Is LBT worth it for uplinks?** Two ground stations 3 km apart behind a ridge sending commands to their rockets on a shared channel: they cannot hear each other, so CSMA degenerates to ALOHA for their mutual collisions. Scheduling uplinks into TDMA slots (example 2) is the robust fix; CAD/LBT still helps against other in-range users.

**5. Do I need a duplexer for a full-duplex 433/915 MHz link?** A rocket transmitting telemetry at 433 MHz while listening for commands at 915 MHz uses two separate radios and antennas — the "duplex spacing" is ~480 MHz, so modest filters (SAW at the 915 MHz receiver, low-pass after the 433 MHz PA) give the 70+ dB needed; check the 433 MHz PA's 2nd harmonic (866 MHz) and noise at 915 MHz. A same-band FDD link (e.g. 433 TX / 438 RX) would need a cavity-class duplexer — impractical in a rocket; use TDD instead.

**6. Desense from a nearby transmitter's noise.** Another team's 1 W (30 dBm) transmitter 1 MHz away whose phase noise at 1 MHz offset is −130 dBc/Hz radiates −100 dBm/Hz of noise into your channel at its antenna; 50 m away (path loss ≈ 59 dB at 433 MHz, plus ~0 dBi antennas) it arrives at −159 dBm/Hz — **9 dB above** a 6 dB-NF receiver's −168 dBm/Hz floor: desense ≈ 9.4 dB, i.e. your link loses most of its margin even though the channels "don't overlap". Separation (≥ 500 m → −179 dBm/Hz, 0.3 dB) or a different band fixes it.

## Practical notes
- **Measure, don't assume, on the day**: log RSSI and packet loss of your link with all other teams transmitting; record the noise floor of your channel with and without others on.
- **Randomise periodic transmissions** (jitter the period by a few %) when channels must be shared, to avoid two drifting periodic senders colliding for seconds at a time.
- **Use the SX126x CAD** (channel activity detection) for LBT on uplinks if the regulations require "polite" access; it detects LoRa preambles of the configured SF below the noise floor.
- **Half-duplex timing**: UART modules (EBYTE) add milliseconds of latency and turnaround; a bare chip with hardware timers is needed for tight TDMA.
- **Ground-station LNA protection**: a co-sited transmitter (your own uplink on the same mast) needs a T/R switch or sequencing and a limiter before the LNA ([ground station](../15-lora-ism-radios/ground-station-design.md)).
- **Doppler and ppm** eat FDMA guard bands slowly; at 433 MHz they are small compared with 1 MHz spacing but matter on a 25–50 kHz grid.

## Common mistakes & misconceptions
1. **"LoRa's spreading makes collisions harmless."** Same-SF packets collide (capture needs ≥ 6 dB); other-SF signals fail beyond ~16 dB disparity.
2. **Using ALOHA's 18 % as "how much of my bandwidth I can use"** — it is the best case with optimal load; real systems run far below it for acceptable loss.
3. **Assuming duty-cycle limits prevent collisions** — duty cycle limits each device's load, not who overlaps whom.
4. **Assuming carrier sense works on a range** — hidden terminals; collisions occur at the receiver.
5. **TDMA with free-running clocks and no guard** — 20 ppm drift is 20 µs per second; plan resync and guards.
6. **Thinking channels that don't overlap can't interfere** — transmitter phase noise, spurs, and receiver blocking desense neighbours, especially at short range.
7. **Using a circulator as a duplexer** — ~20 dB isolation, no filtering of TX noise.
8. **Forgetting that TDD needs LNA protection** — a T/R switch's isolation still lets several dBm into the LNA.
9. **Planning a channel per team without checking the module's tuning grid** — EBYTE modules step 1 MHz, so the licence-exempt 433 MHz band holds only two channels.

## How to simulate / verify
- `python3 tools/verify/est_multiple_access.py` (≈ 2 s, **ALL PASS**): pure and slotted ALOHA by simulation vs formulas and maxima; finite-N success probability vs MC; capture-effect throughput; non-persistent CSMA event simulation vs Kleinrock–Tobagi; LoRa time on air vs the KB's `tools/rfcalc/lora.py`; launch-day numbers (shared-channel survival, TDMA slots and guards, FDMA channel counts on the EBYTE and bare-chip grids); FDD isolation and desense; TDD switch leakage; near-far disparities; neighbour-transmitter noise desense at 50 m and 500 m.
- For your own plan: simulate each team's actual packet schedule (period, jitter, airtime) and count overlaps; or measure with an SDR waterfall on the range ([signal identification](../14-sdr-dsp/signal-identification-and-spectrum-survey.md)).

## Open questions / gaps
- Measured adjacent-channel selectivity / blocking of the E22/E220 modules at 1 MHz offset is not in the KB — needed to close the near-far budget.
- Phase-noise floor of the EBYTE modules' transmitters at 1 MHz offset (assumed −130…−135 dBc/Hz here) is unmeasured.
- Whether IMDA requires LBT for any of the bands used is not stated here; see [domain 19](../19-regulations-safety/singapore-imda-rules.md).
- ALOHA stability/back-off dynamics and LoRaWAN-scale simulations (thousands of nodes, SF allocation) are not covered.

## Sources
1. N. Abramson, "The ALOHA system — another alternative for computer communications," *AFIPS Conf. Proc.* vol. 37 (Fall Joint Computer Conference), pp. 281–285 (1970) — pure ALOHA, $S=Ge^{-2G}$, max 1/(2e). (peer-reviewed conference; located; result re-derived and simulated)
2. D. Bertsekas, R. Gallager, *Data Networks*, 2nd ed., Prentice Hall (1992), ch. 4 (multiaccess communication: slotted/pure ALOHA, stability, CSMA). (textbook; recalled)
3. L. G. Roberts, "ALOHA packet system with and without slots and capture," *ACM SIGCOMM Computer Communication Review* 5(2):28–42 (1975; circulated 1972) — slotted ALOHA, capture. (peer-reviewed; recalled citation)
4. L. Kleinrock, F. A. Tobagi, "Packet switching in radio channels: Part I — carrier sense multiple-access modes and their throughput-delay characteristics," *IEEE Trans. Commun.* COM-23(12):1400–1416 (1975). (peer-reviewed; located; non-persistent formula re-derived and simulated here)
5. T. S. Rappaport, *Wireless Communications: Principles and Practice*, 2nd ed., Prentice Hall (2002), ch. 9 (FDMA, TDMA, SSMA/CDMA, SDMA, packet radio, ALOHA, CSMA, duplexing). (textbook; §9.1–9.6 per the D4 curriculum row)
6. J. G. Proakis, M. Salehi, *Digital Communications*, 5th ed., McGraw-Hill (2008), ch. 16 (multiuser communications, random access). (textbook; recalled)
7. B. Razavi, *RF Microelectronics*, 2nd ed., Prentice Hall (2011), §3.6 (duplexing and multiple access; duplexer requirements). (textbook; recalled)
8. D. Croce, M. Gucciardo, S. Mangione, G. Santaromita, I. Tinnirello, "Impact of LoRa imperfect orthogonality: analysis of link-level performance," *IEEE Commun. Lett.* 22(4):796–799 (2018) — inter-SF rejection ≈ −16 dB; via the KB [LoRa impairments page](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md). (peer-reviewed)
9. M. Bor, U. Roedig, T. Voigt, J. M. Alonso, "Do LoRa low-power wide-area networks scale?" *ACM MSWiM* (2016) — capture timing; via the KB LoRa impairments page. (peer-reviewed)
10. Semtech, SX1261/2 and SX1276/77/78/79 datasheets (time-on-air formula, CAD, co-channel rejection −6 dB) — via the KB's `tools/rfcalc/lora.py` and [LoRa pages](../15-lora-ism-radios/lora-phy-css-math.md). (datasheet)
11. EBYTE E22-400T33D and E220-900T30D user manuals (channel = 410.125 / 850.125 + CH MHz; 10 dBm input rating) — via the KB [modules page](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md). (manufacturer documentation)
