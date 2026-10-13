---
title: LoRa mesh capacity and congestion — airtime, ALOHA collisions, flooding overhead, Meshtastic presets and a launch-day estimate
domain: 15-lora-ism-radios
slug: lora-mesh-capacity-and-congestion
tags: [lora, mesh, meshtastic, meshcore, aloha, csma, channel-utilisation, airtime, flooding, hop-limit, duty-cycle, capacity, collisions, launch-site, rocket]
prerequisites:
  - lora-phy-css-math.md
  - lorawan-vs-raw-lora.md
  - ism-band-plans-duty-cycle.md
related:
  - lora-impairments-doppler-drift-timing.md
  - lora-sensitivity-and-link-budget.md
  - rocket-telemetry-radio-design.md
  - ground-station-design.md
  - ../10-comms-modulation/multiple-access-and-duplexing.md
  - ../10-comms-modulation/packet-framing-protocols.md
  - ../00-math-foundations/probability-random-processes-and-psd.md
  - ../19-regulations-safety/singapore-imda-rules.md
  - ../19-regulations-safety/regulatory-faq-misc.md
level: mixed
confidence: medium
last_updated: 2026-10-14
---

# LoRa mesh capacity and congestion

## Questions this page answers
- How much airtime does one Meshtastic message cost, and how much more does flooding add per hop?
- What happens when a LoRa mesh channel gets congested, and why do big events overload Meshtastic?
- What is the ALOHA collision probability, and where does the famous 18 % come from?
- Are 6–7 mesh hops useful or harmful?
- Why can more transmit power or more ROUTER nodes make a mesh worse?
- Why can a high-power node be heard but not hear others?
- Should a busy mesh move from LongFast to a faster preset?
- How does MeshCore's routing differ from Meshtastic's flooding?
- How many LoRa links can share an area before they collide?
- How many rockets and ground stations can share a channel on launch day?
- My node "heard" something 5 000 km away. Is that an RF record?

## TL;DR
- **Airtime is the currency.** A 50-byte Meshtastic packet takes **641 ms on LongFast** (SF11/250 kHz, 16-symbol preamble) but only **26 ms on ShortTurbo** (SF7/500). The shorter preset costs **13 dB** of link budget (`tools/verify/e10_mesh_capacity.py`).
- **Pure ALOHA** (transmit whenever you like) succeeds with probability $e^{-2G}$, where $G$ is the offered load in packets per packet-time. Throughput peaks at $1/(2e)$ = **18.4 %** at $G=0.5$. For **90 % delivery the channel may be busy only ≈ 5 %** of the time. Listen-before-talk (CSMA) helps only when every node can hear every other node.
- **Flooding multiplies load.** With managed flooding in one collision domain, each message costs about **2 transmissions** (original plus one relay). **Every ROUTER adds about one more**, because routers never cancel. Unmanaged flooding costs N transmissions.
- **More hops or more power enlarge the flood domain.** Your node then carries other people's floods from a wider area. In the script, raising the radio range from 3 to 8 km at hop limit 3 raised the transmissions one node hears per "everyone sends one message" round from about 20 to about 415. End-to-end delivery also falls as $p^h$: 0.9⁷ = 0.48.
- **Meshtastic throttles itself.** It skips its own non-essential sends above **25 % channel utilisation** and stops sending at **40 %** (firmware `airtime.h`). At default intervals (position every 15 min, telemetry every 30 min, node info every 3 h) plus one text per minute site-wide, **about 100 LongFast nodes in one collision domain reach the 25 % threshold**.
- **Duty cycle caps every node, including relays.** Under Singapore's TS SRD 1 % class for LPWAN end devices, a LongFast node may send **one 50-byte packet every 64 s**, and that budget includes its rebroadcasts. Meshtastic's SG_923 region preset applies no duty-cycle limit (it uses 100 %).
- **Rocket telemetry must not share an ALOHA channel.** One E22 at SF7/125 sending 32-byte frames at 10 Hz fills **72 %** of a channel on its own. On launch day, give each rocket its own channel (FDMA). The 433.05–434.79 MHz SRD band holds only about **11 × 125 kHz** channels, and adjacent-channel rejection must beat the near–far ratio.

## Intuition (no math)
A LoRa channel is one room where everyone talks in turn, but nobody waits politely. With pure ALOHA, a packet is ruined if anyone else starts talking while it is on the air. That means from one packet-length *before* it starts (their packet overlaps its start) to one packet-length *after* it starts. The danger window is therefore **twice** the packet length. The longer each packet (high SF, narrow BW), the bigger the window and the fewer packets fit.

A mesh adds a second effect: **every message is repeated**. In Meshtastic every node that hears a broadcast may repeat it, up to the hop limit, so one message becomes several transmissions. Each repeat uses airtime in the area around the repeater. Raising the hop limit, adding ROUTER nodes or raising transmit power all make each message travel further. Every node in that larger area must then carry the extra traffic, which at some point is more traffic than the channel can hold. The mesh then "collapses": packets collide, retries add load, and the firmware starts muting itself.

Power has a second trap: **links are only as good as the weaker direction**. A 1 W node is heard from far away, but it hears no better than a 100 mW node, because its receiver is the same chip. Distant nodes hear it and route to it, but it cannot hear their answers.

Rocket telemetry is the opposite of a chat mesh. It is one transmitter sending many short frames as fast as possible. Such a link fills a channel by itself, so two rockets on one channel will collide constantly. They need separate channels, not a smarter protocol.

## The math

### Level 1 — airtime, utilisation and the 2T window
- **Time on air** $T$ (s) of one packet: Semtech formula from [LoRa PHY](lora-phy-css-math.md); in short, $T = (N_{pre} + 4.25 + N_{payload})\,2^{SF}/BW$.
- **Channel utilisation** (fraction of time the channel is busy, as heard by one receiver):
$$U = \sum_i r_i\,T_i$$
where $r_i$ (packets/s) is the rate of transmitter $i$ that this receiver can hear. For a whole collision domain, the **offered load** in packet-times is $G = \lambda T$, with $\lambda$ the total packet rate (s⁻¹).
- **Pure-ALOHA success** for one packet: $P_s = e^{-2G}$. For example, $G = 0.1$ (channel busy 10 % of the time) gives $P_s$ = 0.82.
- **Duty-cycle limit** $d$: a node may transmit for at most $d$ of the time, so the minimum gap between packets is $T/d$. For LongFast with $T$ = 0.641 s and $d$ = 1 %, that gap is 64 s.
- **Multi-hop delivery** with per-hop success $p$ and $h$ hops (no retries): $P_{e2e} = p^h$.

### Level 2 — derivations

**Pure ALOHA.** Model transmission start times from all nodes as a Poisson process of rate $\lambda$. This is reasonable for many independent nodes with random timers; see [random processes](../00-math-foundations/probability-random-processes-and-psd.md). A tagged packet $[t, t+T]$ survives only if no other packet starts in $(t-T, t+T)$, a window of length $2T$. For a Poisson process, $P(\text{0 arrivals in }\tau) = e^{-\lambda\tau}$, so
$$P_s = e^{-2\lambda T} = e^{-2G}.$$
Throughput (successful packets per packet-time) is $S = G e^{-2G}$. Setting $dS/dG = e^{-2G}(1-2G) = 0$ gives $G^* = 1/2$ and $S_{max} = 1/(2e) \approx 0.184$. This is the 18.4 % ceiling.

**Slotted ALOHA.** If everyone starts only on slot boundaries of length $T$, the vulnerable window shrinks to $T$: $P_s = e^{-G}$, $S = Ge^{-G}$, maximum $1/e \approx 0.368$ at $G = 1$. LoRa meshes have no common time base, so this is a bound, not an option.

**Design inversion.** For a target success $P_s$ the allowed load is $G = -\ln(P_s)/2$. 90 % gives $G$ = 0.053, so the **channel may be busy only ≈ 5 % of the time**. 99 % gives 0.5 %. The Monte-Carlo in `e10_mesh_capacity.py` matches $e^{-2G}$ and $e^{-G}$ to within 0.01 for $G$ = 0.05–1.

**Listen-before-talk (CSMA).** Meshtastic does a channel-activity detection (CAD) before transmitting and backs off if the channel is busy. Classic non-persistent CSMA [10] gives
$$S = \frac{G e^{-aG}}{G(1+2a) + e^{-aG}},\qquad a = \frac{\tau}{T},$$
where $\tau$ is the time to detect another transmission. Meshtastic's slot time is about 2.5 symbols of CAD plus 7.6 ms of propagation, turnaround and processing. That gives $a$ = 0.044 for LongFast (max $S$ ≈ 0.65) but $a$ = 0.31 for ShortTurbo (max $S$ ≈ 0.31). CSMA helps much less on fast presets, because the fixed 7.6 ms is a large fraction of a short packet. **CSMA only works if every node hears every other.** In a mesh, two nodes on opposite sides of a relay often cannot hear each other (**hidden terminals**), so at the relay they behave like pure ALOHA again. Bor et al. likewise found that pure ALOHA is a good lower bound for real LoRa networks [6].

**Flooding overhead.** Let $k$ be the number of transmissions per original message, counting all relays.
- *Unmanaged flood* (every node repeats once; duplicates are suppressed by packet ID): $k = N$ for a connected network of $N$ nodes.
- *Managed flood, one collision domain* (everyone hears everyone): the source transmits, every receiver starts a random timer, and the first timer to fire rebroadcasts. Everyone else hears that rebroadcast and cancels, so $k \approx 2$. ROUTER and REPEATER roles never cancel [3], so $k \approx 2 + n_{router}$ (script: 2.0, 4.4, 10.9 for 0, 3, 10 routers among 40 nodes).
- *Managed flood, spread network*: $k$ is roughly the number of relays needed to cover the area reached within the hop limit $H$, capped by the network size.

**Load on one node.** Suppose every node originates messages at rate $\lambda_0$, with node density $\rho$ (nodes/km²) and radio range $r$. Your node must carry every flood whose source lies within about $H$ hops, roughly a disc of radius $Hr$. It hears $k_{heard}$ transmissions of each such message. So
$$U_{node} \approx \lambda_0\,\rho\,\pi (H r)^2\,k_{heard}\,T \quad(\text{until } \pi(Hr)^2 \text{ covers the whole network}).$$
Both $H$ and $r$ enter **squared**. Doubling range, which costs +6 dB in free space or about +9 dB at a path-loss exponent of 3, roughly quadruples the traffic every node must carry. The same holds for doubling the hop limit, until the flood already covers the whole mesh. The script's 150-node, 30 × 30 km network shows the trend: transmissions heard by the central node per round went 16 → 20 → 62 for hop limits 1 → 3 → 7 at 3 km range, and 20 → 169 → 415 for range 3 → 5 → 8 km at hop limit 3.

**Hops hurt reliability too.** Each hop must win its own collision lottery: $P_{e2e} = p^h$. At $p = 0.9$, 3 hops give 0.73 and 7 hops give 0.48. Acknowledged messages are retransmitted (Meshtastic retries when `want_ack` is set), so lost packets are not just lost: their retries add more load.

**Asymmetric links.** Node A transmits at $P_A$ and node B at $P_B$, with the same receiver sensitivity $S$ and the same path loss $L(d)$. A→B closes up to $L = P_A - S$ and B→A only up to $L = P_B - S$. With path loss $\propto d^n$, A is heard out to $10^{(P_A-P_B)/(10n)}$ times the distance at which A can hear B. For 30 dBm vs 22 dBm at $n = 3$ that ratio is 1.85. Meshtastic gives the *shortest* rebroadcast delay to the *lowest*-SNR receiver, to push floods outward [3]. Distant nodes that hear a loud node only weakly therefore rebroadcast first, and their replies may never reach it.

**Meshtastic's contention window, in numbers** [5]. The firmware maps the received SNR linearly from −20…+10 dB onto a contention-window exponent CW = 3…8, then picks a random delay:
- ROUTER: $\text{delay} \in [0,\,2\,CW)\times t_{slot}$, at most 16 slots.
- Every other relaying role: $\text{delay} = 16\,t_{slot} + [0,\,2^{CW})\times t_{slot}$. The 16-slot offset lets routers go first.
- On LongFast, $t_{slot} = 2.5 \times 8.192 + 7.6$ = 28.1 ms. A router fires within 0.45 s. A client that heard the packet weakly (CW = 3) fires within 0.45–0.67 s. A client that heard it strongly (CW = 8) may wait up to 7.6 s, which is usually long enough to hear someone else relay first and cancel.

The scheme pushes floods outward cheaply. Its cost is latency, a few seconds per hop on slow presets, plus the router exception: routers fire first *and* never cancel.

### Level 3 — what the simple models leave out
- **Capture.** A LoRa receiver usually decodes the stronger of two same-SF packets if it is ≥ 6 dB stronger and its preamble arrives early enough ([impairments](lora-impairments-doppler-drift-timing.md)) [6]. Capture makes $e^{-2G}$ pessimistic: at N = 200, Bor et al.'s delivery ratio rose from 0.51 to 0.64 when capture was modelled [6]. With several gateways or sinks, capture at *any* sink is enough, and delivery improved again.
- **Stochastic geometry.** Georgiou and Raza model nodes as a Poisson point process around one gateway. They show that coverage probability falls exponentially with node count, because of same-SF interference. In their analysis this limit matters more than regulatory duty cycle [7]. The $\rho\,\pi(Hr)^2$ scaling above is the mesh version of the same effect.
- **Spreading factors are quasi-orthogonal**, not orthogonal. A different-SF signal more than ~16 dB stronger still breaks reception ([impairments](lora-impairments-doppler-drift-timing.md)). Different Meshtastic presets also end up on different default frequency slots, because the slot is derived from the channel name. Two meshes on different presets therefore mostly cannot hear each other at all: they cannot relay for each other, yet they still raise each other's noise floor if they overlap in frequency.
- **Non-Poisson traffic.** Synchronised events break the Poisson assumption and make collisions worse than $e^{-2G}$. Examples are everyone pressing "send" at launch, or all nodes rebooting together and sending node info. Meshtastic stretches broadcast intervals for meshes above 40 nodes by $1 + 0.075(N_{online}-40)$ [3].
- **Path-learning routing (MeshCore).** MeshCore floods only to discover a path. The destination's delivery report carries back the list of repeaters, and later messages carry that path so that only the named repeaters relay. Client ("companion") nodes never repeat. After three failed retries it floods again [9]. For person-to-person traffic, $k$ falls from "every relay in range" to "one per hop". Group channels still flood [9]. Meshtastic 2.6+ does something similar for direct messages, learning a next-hop relay and falling back to flooding [3].

## Design equations & rules of thumb

| Quantity | Equation / rule | When valid | Typical value |
|---|---|---|---|
| Pure-ALOHA success | $e^{-2G}$ | Poisson traffic, no capture, single domain | G = 0.05 → 0.90; G = 0.25 → 0.61 |
| Pure-ALOHA throughput max | $1/(2e)$ at $G = 0.5$ | as above | 18.4 % |
| Slotted ALOHA | $e^{-G}$; max $1/e$ | common time base (not LoRa meshes) | 36.8 % |
| Non-persistent CSMA | $S = Ge^{-aG}/(G(1+2a)+e^{-aG})$ | everyone hears everyone | LongFast a = 0.044 → max 0.65 |
| Allowed load for success $P_s$ | $G = -\ln P_s/2$ | pure ALOHA | 90 % → 5.3 % busy |
| Managed-flood transmissions | $k \approx 2 + n_{router}$ | one collision domain | 2 with no routers |
| Flood-domain load | $\propto \rho\,(Hr)^2$ | network larger than the flood reach | ×4 per doubling of H or r |
| End-to-end delivery | $p^h$ | independent hops, no retry | 0.9³ = 0.73 |
| Link asymmetry | range ratio $10^{\Delta P/(10n)}$ | same RX, path-loss exponent n | 8 dB, n = 3 → ×1.85 |
| Duty-cycle packet gap | $T/d$ | per node, including its relays | LongFast 50 B at 1 % → 64 s |
| Meshtastic throttles | 25 % CU polite, 40 % hard stop | firmware `airtime.h` [4] | — |

**Meshtastic presets** (SF/BW/CR from [1]; ToA from `e10_mesh_capacity.py` with the firmware's 16-symbol preamble, explicit header, CRC on and LDRO auto; "link budget" is Meshtastic's own figure [1]):

| Preset | SF | BW (kHz) | CR | ToA 50 B (ms) | ToA 255 B (ms) | Link budget [1] | 50 B pkts/min at 25 % CU |
|---|---|---|---|---|---|---|---|
| ShortTurbo | 7 | 500 | 4/5 | 26.4 | 102 | 140 dB | 567 |
| ShortFast | 7 | 250 | 4/5 | 52.9 | 204 | 143 dB | 284 |
| ShortSlow | 8 | 250 | 4/5 | 95.5 | 362 | 145.5 dB | 157 |
| MediumFast | 9 | 250 | 4/5 | 181 | 642 | 148 dB | 83 |
| MediumSlow | 10 | 250 | 4/5 | 341 | 1181 | 150.5 dB | 44 |
| LongTurbo | 11 | 500 | 4/8 | 443 | 1656 | 150 dB | 34 |
| **LongFast (default)** | 11 | 250 | 4/5 | **641** | 2157 | 153 dB | 23 |
| LongModerate | 11 | 125 | 4/8 | 2036 | 7934 | 156 dB | 7 |
| LongSlow | 12 | 125 | 4/8 | 3547 | 14295 | 158.5 dB | 4 |

The link-budget column follows the KB's sensitivity rule (SNR limit −2.5 dB per SF step plus 10 log BW). LongFast to MediumFast is 5 dB, and LongFast to ShortTurbo is 10 + 3 = 13 dB ([sensitivity](lora-sensitivity-and-link-budget.md)). The 50-byte payload is an assumption: a 16-byte Meshtastic header [5] plus about 34 bytes for a short text or position.

## Worked examples

**1. One LongFast message under Singapore's 1 % rule.** $T$ = 0.641 s for 50 B. At $d$ = 1 % (TS SRD 30c for LPWAN end devices; see [band plans](ism-band-plans-duty-cycle.md)), the minimum gap is 0.641/0.01 = **64 s**, or at most 56 packets per hour. Default position, telemetry and node-info traffic is 6.3 packets per hour, which leaves about 50 per hour for texts **and for relaying others' packets**. A Singapore ROUTER on LongFast that obeyed 1 % could relay fewer than one packet a minute. Meshtastic's SG_923 preset applies 100 % duty [2], so the firmware will not enforce this for you. Legality is covered in [19 Singapore](../19-regulations-safety/singapore-imda-rules.md).

**2. A launch-site mesh on LongFast.** Assume $n$ nodes all within range of each other, which is typical for a few-km launch field. Each node sends its defaults (4 + 2 + ⅓ packets per hour). The whole site sends one text per minute. Managed flooding gives $k$ = 2.
- Load: $\lambda = (6.33n + 60)\times 2/3600$ s⁻¹ and $U = \lambda T$.
- n = 20 → U = 6.6 %, $e^{-2U}$ = 0.88. n = 50 → 13.4 %, 0.76. n = 100 → 24.7 %, 0.61.
- At about **101 nodes** the mesh reaches Meshtastic's 25 % "polite" threshold, and nodes start skipping their own position and telemetry packets.
- On ShortTurbo the same threshold is reached at about 2 700 nodes. That is 24× the headroom, bought with 13 dB of link budget. On a flat launch field where every node is within a few km, that 13 dB is usually affordable. Trade the margin you do not need for capacity.

**3. Should a busy city mesh leave LongFast for MediumFast?** The ToA ratio is 641/181 = 3.5, so the channel holds 3.5× more traffic. The price is 5 dB of link budget. The range factor is $10^{-5/(10n)}$: 0.56 in free space ($n$ = 2), or 0.68 at $n$ = 3. Each node's coverage *area* falls to 0.32–0.46. Some links that were one hop become two, which adds relays (larger $k$) and multiplies per-hop losses ($p^h$). In a dense mesh where most links have more than 5 dB of margin, the switch wins clearly, which is the argument made in the Meshtastic discussions (forum — anecdotal). In a sparse rural mesh it can break connectivity. Decide from measured link margins (SNR of received packets), not from node counts — and take $n$ from a fit that includes the lost packets, because a received-only fit can return $n$ ≈ 1.7 where the truth is 3.5 (Common mistakes).

**4. Four rockets on one 433 MHz channel.** An E22 at SF7/125 sending 32-byte frames (8-symbol preamble) has $T$ = 71.9 ms. At 5 Hz per rocket and 4 rockets, $G = 4 \times 5 \times 0.0719$ = 1.44, so $P_s = e^{-2.88}$ = **5.6 %**. Even *one* rocket at 10 Hz has $G$ = 0.72. A shared channel cannot work, and no MAC protocol fixes a channel that is 144 % full. Use **one channel per rocket**:
- 433.05–434.79 MHz SRD: 1.74 MHz holds 11 channels at 125 kHz with a 25 kHz guard, 6 at 250 kHz, 3 at 500 kHz. Licence-exempt power there is only 10 mW e.r.p. in Singapore.
- 70 cm amateur 430–440 MHz (licensed, secondary): about 66 × 125 kHz.
- IREC Mode A, 902–909 MHz, 500 kHz ≤ BW ≤ 1 MHz: about 13 channels at 500 kHz.

For the channel plan and duplexing see [multiple access](../10-comms-modulation/multiple-access-and-duplexing.md).

**5. Near–far check for adjacent channels at the pad.** Team B's rocket sits on the pad 200 m from your ground station at 30 dBm. Your rocket is at 20 km, also at 30 dBm. The free-space path-loss difference is $20\log(20000/200)$ = **40 dB**, so B arrives 40 dB stronger than your wanted signal. SX1262 adjacent-channel rejection is 60–72 dB at ±1.5 BW, and blocking is 88 dB at ±1 MHz ([impairments](lora-impairments-doppler-drift-timing.md)). Spacing channels ≥ 1.5 BW apart therefore leaves about 20 dB of margin. Co-channel, even a different SF fails, because −16 dB of quasi-orthogonality is far short of 40 dB. Rules:
- Never put two teams on the same channel.
- Space channels by at least 1.5 BW.
- Keep pad transmitters off or at low power until the count-down if you can.

**6. The loud node.** A LilyGO T-Beam at 30 dBm in a mesh of 22 dBm Heltecs, with identical SX1262 receivers. Downlink and uplink differ by 8 dB, so at $n$ = 3 the T-Beam is heard 1.85× further than it can hear. Nodes 1.0–1.85 units away see it in their node list, but their replies to it fail. The T-Beam also floods every message it relays over 1.85² = 3.4× the area, adding load there. To raise range in *both* directions, improve the antenna or its height. Gain at the receive end helps both directions; transmit power helps only one.

**7. How many long-range links can share an area?** Take a same-SF link of length $d$. An interferer corrupts it unless it arrives at least 6 dB below the wanted signal (capture). With path loss $\propto d^n$, any co-channel transmitter within $d\cdot10^{6/(10n)}$ of the receiver is harmful while it transmits: 2.0 d at $n$ = 2, 1.6 d at $n$ = 3. That holds however much margin the link has.
- For 5 km links at $n$ = 3, the harmful zone around each receiver is a disc of radius 8 km, which is 200 km². In a 10 × 10 km region every co-channel transmitter is therefore inside every receiver's harmful zone, and the region is **one collision domain per channel**.
- Capacity then comes only from more channels (FDMA), quasi-orthogonal SFs (useful only when powers are within ~16 dB), and time. The sum of offered loads on a channel must stay ≈ 0.05 for 90 % success.
- Short links (say 300 m inside a building) allow real spatial reuse: a 0.5 km harmful radius fits about 130 discs into 100 km².
- This is why long-range LoRa does not scale like Wi-Fi. The quality that makes it attractive, reach, also makes everyone your neighbour.

**8. A Meshtastic node on the ground-station table.** A 20 dBm, 915 MHz node sits 2 m from a 900 MHz telemetry receive antenna. Free-space loss at 2 m is $20\log 2 + 20\log 915 - 27.55$ = 37.7 dB, so −17.7 dBm reaches the receiver. A rocket near the end of its range arrives at about −120 dBm, so the ratio is about 102 dB. That exceeds the SX1262's 88–99 dB blocking figures even at 1–10 MHz offset ([impairments](lora-impairments-doppler-drift-timing.md)), and the receiver is desensitised whenever the node transmits. At 20 m the level is −37.7 dBm (about 82 dB above the wanted signal), which is marginal. Move the mesh node to another band, at least tens of metres away, or switch it off during the flight window ([ground station](ground-station-design.md)).

## Practical notes
- **Measure channel utilisation, do not guess it.** Meshtastic reports "ChUtil", the airtime of all packets heard over the last minute (6 × 10 s bins), and "AirUtilTX", your own transmit share over the past hour [4]. Rough guide: under 10 % is healthy, 10–25 % shows growing collisions, and above 25 % the firmware sheds your traffic.
- **ROUTER is for high, well-placed sites only.** Meshtastic's docs describe ROUTER as an infrastructure node that *always* rebroadcasts [8]. A ROUTER on a balcony in a dense area adds one transmission to every message it hears, for no coverage gain. Use CLIENT or CLIENT_MUTE indoors. For trackers and sensors, use roles that do not relay.
- **Hop limit: 3 is the default, 7 the maximum** [2]. Raise it only along a known chain of high sites, not "to be safe".
- **Prefer a faster preset when links have margin.** On a launch field or in a city, ShortFast/ShortTurbo or MediumFast, or MeshCore's SF7/62.5 kHz "narrow" setting [9], usually works better than LongFast.
- **Bridged nodes (MQTT/Internet) create false "ranges".** A node 5 000 km away in your list arrived over the Internet, not by RF. Check the hop count and the "via MQTT" flag before claiming a record.
- **Rocket telemetry and team messaging must not share a channel.** Telemetry at 5–10 Hz is a high-duty, near-continuous transmission. Put it on its own frequency, away from the mesh's frequency slot, and keep the mesh for people.
- **Duty cycle applies to relays.** In duty-limited regions (EU 868 MHz 1–10 %, Singapore LPWAN class 1 %), heavily used relays are the first to go silent or to break the rules.

**Duty-cycle budget per preset** (minimum gap between 50-byte packets from one node, including its relays; `e10_mesh_capacity.py`):

| Preset | ToA 50 B | Gap at 1 % | Gap at 10 % | Packets/hour at 1 % |
|---|---|---|---|---|
| ShortTurbo | 26.4 ms | 2.6 s | 0.26 s | 1 360 |
| ShortFast | 52.9 ms | 5.3 s | 0.53 s | 680 |
| MediumFast | 181 ms | 18.1 s | 1.8 s | 199 |
| LongFast | 641 ms | 64 s | 6.4 s | 56 |
| LongModerate | 2.04 s | 204 s | 20 s | 17 |
| LongSlow | 3.55 s | 355 s | 35 s | 10 |

**Congestion triage checklist** (for "the mesh worked yesterday and is useless today"):
1. Read ChUtil on two or three nodes. Above 25 %, you have a capacity problem, not a range problem.
2. Count ROUTER/REPEATER nodes that can hear each other. More than one or two per area usually means extra overhead with no extra coverage.
3. Check the hop limit on the busiest senders. Above 3 needs a reason.
4. Look for chatty nodes: trackers set to send position every 30 s, telemetry modules at short intervals, MQTT downlink bridges injecting Internet traffic onto RF.
5. Check whether the mesh uses a faster preset that every node in the area can still reach (verify SNR margins first).
6. Check for nodes far above everyone else in power. They create asymmetric links and enlarge flood domains.
7. Only then consider more relays or higher sites, and measure ChUtil again afterwards.

## Common mistakes & misconceptions
- **"More TX power and more hops always help a mesh."** Both enlarge the area each flood covers. Load grows roughly as $(H r)^2$, and delivery falls as $p^h$. Past a modest size, extra hops and power reduce throughput for everyone (D3 #447/#449; D2 3a). Add relays only where geometry demands them.
- **"A louder 1 W node fixes my range."** It only fixes one direction. The link closes at the weaker direction, which is set by the *other* node's power and *your* receiver. Fix both ends with antennas and height (D2 #228/#240). Check legality first ([regulatory FAQ](../19-regulations-safety/regulatory-faq-misc.md)).
- **"Our coverage map shows the mesh reaches 8 km, so n ≈ 2 here."** A map of *received* packets is censored: the failures are missing, so it shows where the lucky tail of the fading reached. In a simulation with a true path-loss exponent of 3.5, a fit to received points only gave **n = 1.7** and a median range 2.4× too long; a censored (Tobit) fit with the failed attempts recovered 3.6 ([tool landscape Example 5](../16-simulation-tools/tool-landscape-overview.md)). Plan hop distances and the range factors in this page with an $n$ fitted to logs that include the packets nobody heard (sender-side sequence numbers).
- **"My node heard something 400–5 500 miles away."** Almost always an MQTT or Internet bridge, not RF. Genuine long hops need elevated line of sight or tropospheric ducting ([Fresnel/LOS](../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md)) (D2 #246/#254).
- **"Set my home node to ROUTER so I help the mesh."** In a dense area a ROUTER that is not high adds load and creates bad relay paths (D2 #226/#245; D3 #443).
- **"LongSlow/SF12 is best because it has the most range."** It costs 5.5× the airtime of LongFast per packet (3.5 s vs 0.64 s for 50 B). It collapses a busy mesh and is fragile to drift ([PHY](lora-phy-css-math.md)).
- **"The channel is fine below 18 %."** 18.4 % is the throughput *maximum*, reached when 63 % of packets collide ($e^{-1}$ = 0.37 success). For 90 % delivery stay near 5 % offered load, or use capture, CSMA and multiple channels.
- **"Collisions need two packets to start at the same time."** Any overlap kills both, unless one captures. The vulnerable window is $2T$.
- **"The region preset makes my settings legal."** Meshtastic's SG_923 uses 100 % duty at 20 dBm, while TS SRD's LPWAN-end-device class specifies 1 % ([band plans](ism-band-plans-duty-cycle.md)).
- **"Several rockets can share a channel if they use different SFs."** Quasi-orthogonality fails at about 16 dB of power difference, and a rocket on the pad is ~40 dB stronger than one at 20 km. Use separate channels.

## How to simulate / verify
- `python3 tools/verify/e10_mesh_capacity.py` (output in `tools/verify/e10_mesh_capacity_output.txt`, 27 checks pass). It covers preset ToA; pure/slotted ALOHA analytic vs Monte-Carlo; non-persistent CSMA with Meshtastic's slot time; a managed-flooding Monte-Carlo (SNR-weighted delays, duplicate cancellation, routers that never cancel) on random geometric graphs; central-node load vs hop limit and range; $p^h$; and the launch-day scenarios.
- ToA and sensitivity: `tools/rfcalc/lora.py` (verified in `tools/verify/lora_toa.py`).
- Full discrete-event simulators: **Meshtasticator**, Meshtastic's own simulator of the firmware's radio layer, collisions and rebroadcasting [11]. **LoRaSim**, Bor et al.'s SimPy simulator with capture [6].
- Quick estimate for your own scenario (uses the KB's verified ToA function):

```python
import math, sys; sys.path.insert(0, "tools")
from rfcalc.lora import time_on_air
T = time_on_air(50, 11, 250e3, cr=1, npre=16, chip="sx126x")   # LongFast, 50-byte packet
nodes, own_per_h, texts_per_h, k = 60, 4 + 2 + 1/3, 60, 2.0       # defaults; k = tx per message
U = (nodes * own_per_h + texts_per_h) * k / 3600 * T              # channel utilisation
print(f"ToA {T*1e3:.0f} ms, U = {100*U:.1f} %, pure-ALOHA success {math.exp(-2*U):.2f}")
```

- In the field: log ChUtil and AirUtilTX from a node at the busiest site during an event. Compare the delivery ratio of acknowledged messages with $e^{-2U}$.

## Open questions / gaps
- The flooding model here is idealised: unit-disc radio range, no fading, no capture inside the flood simulation, and a simplified delay rule. Real meshes have irregular links. Treat the transmissions-per-message numbers as trends.
- Meshtastic's channel-hash → frequency-slot mapping, and whether co-located meshes on different presets overlap in frequency, was not checked in the firmware.
- No measured launch-site data. A ChUtil log from an actual launch day (several teams, Meshtastic plus telemetry) would calibrate example 2.
- There is an internal inconsistency in Bor et al. [6] (64 vs 120 nodes for DER > 0.9); see Sources.
- The US Part 15 basis for 250 kHz non-hopping LoRa at 30 dBm (the Meshtastic US preset) is discussed in the [regulatory FAQ](../19-regulations-safety/regulatory-faq-misc.md). It is not settled here.

## Sources
1. Meshtastic, "Radio Settings — modem presets" (SF, BW, CR, data rate, link budget per preset), accessed 2026-10-03. https://meshtastic.org/docs/overview/radio-settings/ (project docs)
2. Meshtastic, "LoRa configuration" — hop limit (default 3, max 7), default preset LONG_FAST, EU 10 % hourly duty, SG_923 917–925 MHz 20 dBm 100 % duty. https://meshtastic.org/docs/configuration/radio/lora/ (project docs)
3. Meshtastic, "Mesh Broadcast Algorithm" — managed flooding, SNR-weighted contention window, ROUTER/REPEATER always rebroadcast, next-hop routing for DMs from 2.6, interval scaling above 40 nodes. https://meshtastic.org/docs/overview/mesh-algo/ (project docs)
4. Meshtastic firmware, `src/airtime.h` / `src/airtime.cpp` — `max_channel_util_percent = 40`, `polite_channel_util_percent = 25`, `polite_duty_cycle_percent = 50`; CU window 6 × 10 s; TX utilisation per hour. https://github.com/meshtastic/firmware (vendor code, read 2026-10-03)
5. Meshtastic firmware, `src/mesh/RadioInterface.h/.cpp` — preamble 16 symbols, `MESHTASTIC_HEADER_LENGTH 16`, CWmin 3/CWmax 8, slot time = max(2.25, 2 + 0.5) symbols + 7.6 ms, SNR-mapped contention window. https://github.com/meshtastic/firmware (vendor code)
6. M. Bor, U. Roedig, T. Voigt, J. M. Alonso, "Do LoRa Low-Power Wide-Area Networks Scale?", ACM MSWiM 2016 — pure-ALOHA DER $=e^{-2NT\lambda}$ as a lower bound; capture raises DER (0.51 → 0.64 at N = 200); multiple sinks help; LoRaSim. Accepted version: https://eprints.lancs.ac.uk/id/eprint/81674/ (peer-reviewed). *Note:* its text gives N = 64 nodes for DER > 0.9 with LoRaWAN-like settings (SN3), while its Fig. 4 caption and abstract give 120 nodes (per 3.8 ha). The KB quotes neither as a design number.
7. O. Georgiou, U. Raza, "Low Power Wide Area Network Analysis: Can LoRa Scale?", *IEEE Wireless Commun. Lett.* 6(2), 162–165, 2017; arXiv:1610.04793 — stochastic-geometry coverage; exponential decay with node count from co-SF interference. (peer-reviewed)
8. Meshtastic, "Device configuration — roles" (CLIENT, CLIENT_MUTE, CLIENT_BASE, ROUTER, ROUTER_LATE, REPEATER), node-info interval 10 800 s; "Position" (broadcast 900 s); "Telemetry" (1 800 s). https://meshtastic.org/docs/configuration/radio/device/ (project docs)
9. MeshCore, "FAQ" — flood-then-direct path learning, only repeaters/room servers repeat, group channels flood, 64-hop limit, US recommended 910.525 MHz SF7/BW 62.5 kHz/CR5. https://docs.meshcore.io/faq/ (project docs)
10. L. Kleinrock, F. A. Tobagi, "Packet Switching in Radio Channels: Part I — Carrier Sense Multiple-Access Modes and Their Throughput-Delay Characteristics", *IEEE Trans. Commun.* COM-23(12), 1400–1416, 1975 — non-persistent CSMA throughput. Also D. Bertsekas, R. Gallager, *Data Networks*, 2nd ed., 1992, §4.2–4.4 (ALOHA, CSMA). (peer-reviewed / textbook)
11. Meshtastic, *Meshtasticator* — discrete-event simulator of the firmware's radio layer. https://github.com/meshtastic/Meshtasticator (project tool)
12. Forum demand: Meshtastic GitHub discussions #278, #298, #3874, #6199, #6644, #7430, #9936; Hackaday "Meshtastic: a tale of two cities" (2025); Geerling Engineering video on Meshtastic overload — catalogued in `gaps/D3-forums-youtube.md` rows 441–458, 654 and `gaps/D2-reddit.md` rows 220–254. (forum — anecdotal)
