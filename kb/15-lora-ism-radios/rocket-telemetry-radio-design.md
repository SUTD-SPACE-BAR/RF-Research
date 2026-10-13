---
title: Rocket telemetry radio design — requirements, packets, FEC, Doppler, antennas, redundancy, what teams flew
domain: 15-lora-ism-radios
slug: rocket-telemetry-radio-design
tags: [rocket, telemetry, lora, packet-design, fec, doppler, antenna-nulls, plume, redundancy, uplink-safety, rtk, e22-400t33d, e220-900t30d, altus-metrum, featherweight, eggfinder, bigredbee, rdf-beacon, airtag, tracker-landscape]
prerequisites:
  - lora-phy-css-math.md
  - lora-sensitivity-and-link-budget.md
  - lora-impairments-doppler-drift-timing.md
related:
  - lora-modules-ebyte-rfm-heltec.md
  - ground-station-design.md
  - ism-band-plans-duty-cycle.md
  - other-ism-radios-fsk-2g4.md
  - ../08-antennas/antennas-on-rockets.md
  - ../08-antennas/antenna-polarization-and-circular-polarization.md
  - ../10-comms-modulation/packet-framing-protocols.md
  - ../10-comms-modulation/channel-coding-fec.md
  - ../20-projects-recipes/lora-rocket-telemetry-link.md
  - ../19-regulations-safety/singapore-imda-rules.md
  - ../19-regulations-safety/lab-safety-esd-high-power.md
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# Rocket telemetry radio design

## Questions this page answers
- How do I choose SF, bandwidth and packet size so my rocket telemetry keeps up with the flight?
- What should a telemetry packet contain, and how do I make packet loss measurable?
- Is LoRa's built-in coding enough, or do I need extra FEC?
- Which radio settings survive boost (Doppler rate), and which are best after landing?
- Why does telemetry drop out near apogee or right above the pad, and how do antenna placement and roll matter?
- Does the motor plume block the signal?
- How do I run a 433 MHz and a 900 MHz radio on the same vehicle without them interfering?
- Should my rocket accept commands over the radio, and if so how do I make that safe?
- Can I send RTK corrections to the rocket over LoRa while it is also transmitting telemetry?
- What have amateur and university rocket teams actually flown for telemetry?
- Which commercial rocket GPS trackers and RDF beepers exist, on which bands and at what power, and can I receive them with an SDR?
- Why won't an AirTag or a Bluetooth tag find my rocket in a field?

## TL;DR
- **Budget the air time first.** Update rate × time-on-air must fit the channel (and any duty-cycle rule). A 40-byte frame takes 82 ms at SF7/125, 41 ms at SF7/250, 20.5 ms at SF7/500 and 288 ms at SF9/125 (`lora_toa.py`). 10 Hz ascent telemetry (Altus Metrum's rate [1]) needs ≤ 100 ms per frame ⇒ **SF7 at 125–500 kHz**; SF9/125 caps you at ~3.5 Hz.
- **In flight the link budget is huge** (line of sight); what you need is update rate and robustness to **Doppler rate** (≤ 23 g allowed at SF9/125 and 433 MHz, ≤ 6 g at SF10/125, half at 923 MHz — Semtech drift rule) ⇒ **SF7–8 during boost**. After landing the ground kills the link (two-ray, terrain) ⇒ switch to a **slow, robust mode** (SF10–12, narrow BW, LDRO, TCXO) and send the last GNSS fix repeatedly.
- **Packet design**: fixed-length frames, protocol version, source ID, per-type sequence counters, flight-time stamp, CRC; deterministic decimation schedule (e.g. state 10 Hz, GNSS 2–5 Hz, health 1 Hz). Loss is then countable and a stale parser can't silently mis-decode (Space Bar lesson).
- **FEC**: LoRa CR4/5 only detects errors; CR4/8 corrects one bit per codeword. LoRa failures on rockets are **whole-packet erasures** (nulls, drift, collisions), so add **packet-level redundancy** (repeat key fields, rolling history of the last N fixes, or an XOR parity packet every k packets) rather than more bit-level coding.
- **Antenna geometry dominates**: axial antennas null toward the tail — 10 km up, 2 km offset, the look angle is 11° and an axial dipole is ~16 dB down [2]; the station should sit several km from the pad or use diversity; circular polarisation at the ground removes roll nulls for −3 dB; plume attenuation is strong within ~22° of the aft axis [2][3].
- **Near-pad overload**: +17 dBm at 1 m from a 2 W module into a Yagi; keep receivers ≥ tens of metres away or attenuate.
- **Two bands**: E22 at 433.125 MHz has its 2nd harmonic at 866.25 MHz; keep the E220 in 866–869 MHz (500 mW e.r.p., no duty stated): CH 18 = 868.125 MHz is 1.9 MHz from that harmonic. With the E22 on the band-edge-safe CH 24 = 434.125 MHz, the harmonic moves to 868.25 MHz, so use CH 17 = 867.125 MHz instead. Never use CH 16. 917–925 MHz is not a good escape, because its 100 mW e.r.p. / ≤ 1 % duty limit cannot carry 10 Hz telemetry ([impairments § practical notes](lora-impairments-doppler-drift-timing.md#practical-notes)). Also filter, separate antennas, and never co-locate an onboard *receiver* (e.g. RTK corrections) in the same band as a 2 W onboard transmitter.
- **Legal power and duty set the design in Singapore** ([19](../19-regulations-safety/singapore-imda-rules.md)): licence-exempt limits are 10 mW e.r.p. + 10 % duty at 433 MHz, 500 mW e.r.p. (no duty stated) at 866–869 MHz, 100 mW e.r.p. + 1 % at 917–925 MHz. The 2 W E22 needs an **amateur licence (≤ 10 W ERP, IMDA consent)** or a permit. 10 Hz telemetry is therefore legal only under a licence, or licence-exempt at 866–869 MHz; the 1 % rule at 917–925 MHz allows ~0.1 Hz.
- **Pyro safety**: before flight, run a continuous-TX test with the flight antenna next to a dummy igniter/e-match circuit and confirm the induced RF stays ≥ 16.5 dB below the no-fire level (MIL-STD-464C margin; ≈ 15 % of no-fire current) — [lab safety § HERO](../19-regulations-safety/lab-safety-esd-high-power.md).
- **Uplink**: Space Bar flew downlink-only by design. If you add commands: authenticate (HMAC with counters, not EBYTE's "key"), require multi-step arming, and make link loss a safe state.
- **Commercial trackers** ([table](#commercial-rocket-trackers-and-beacons)): Featherweight (915 MHz LoRa, 100 mW, two-way), Eggfinder (900 MHz FSK, 100 mW), BigRedBee (900 MHz 250/100 mW; 70 cm APRS), Altus Metrum (70 cm, 40 mW, with an RDF tone after landing) and RDF beepers (216–220 / 433.9 MHz, ≤ 10 mW). None of them is licence-exempt in Singapore at its stated power and duty, except possibly a ≤ 10 mW 433.92 MHz beeper. BLE/UWB tags need passing phones and fail in empty fields.
- **Flown examples**: Altus Metrum TeleMetrum (70 cm GFSK 38.4 kbaud, rate-½ K=4 convolutional code, 32-byte frames, 10 Hz ascent) [1]; Featherweight LoRa 915 MHz tracker (41.8 km altitude, 44.5 km range, stub antennas) [4]; Stanford SSI XBee-900HP (≤ 10 km with dipoles, 2017) and later LoRa (SAC reports, anecdotal) [5]; Norby CubeSat LoRa at 436.7 MHz from 560 km [6].

## Intuition (no math)
A rocket flight has three radio regimes. **On the pad** the rocket is close, stationary and loud — so loud that receivers can be overloaded. **In flight** it is in clear line of sight almost all the way, so signal strength is rarely the problem; instead the rocket accelerates hard (which smears slow LoRa symbols), rolls (which spins a linear antenna's polarisation through nulls), points its tail at you (where rocket antennas are blind) and may hide behind its own exhaust. **After landing** it lies in the grass: the ground reflection cancels the direct wave and hills block it, so the link budget suddenly matters a lot. A good design uses fast, short packets for flight, slow robust packets after landing, antennas and a ground-station position chosen for the geometry, and a packet format that tells you precisely what was lost.

## The math
### Level 1 — the throughput budget
Payload bits per second needed: $R_{need} = \sum_i f_i L_i$ (rate $f_i$ and bytes $L_i$ of each frame type, ×8). A single half-duplex radio can carry at most $\sum_i f_i\,T_{p}(L_i) \le d_{max}$, where $T_p$ is the time-on-air ([PHY page](lora-phy-css-math.md)) and $d_{max}$ is 1 for unregulated use, or the legal duty cycle ([band plans](ism-band-plans-duty-cycle.md)). Keep a margin (≤ 70 % channel occupancy) for UART/turnaround gaps.

40-byte frame, 8-symbol preamble, CRC, CR4/5 (`lora_toa.py`):

| Setting | ToA | Max frames/s (100 %) | 10 Hz occupancy |
|---|---|---|---|
| SF7/125 | 82.2 ms | 12.2 | 82 % |
| SF7/250 | 41.1 ms | 24.3 | 41 % |
| SF7/500 | 20.5 ms | 48.8 | 21 % |
| SF8/500 | 38.5 ms | 26.0 | 39 % |
| SF9/500 | 71.9 ms | 13.9 | 72 % |
| SF9/125 | 287.7 ms | 3.5 | — |

(Implicit header saves nothing at SF7 for 40 bytes because of interleaver-block rounding, and 2.5–5 ms at SF8–9/500.)

### Level 2 — dynamics: Doppler rate, look angle, plume, roll
**Doppler rate** $\dot f = a_r f_c/c$ (14.2 Hz/s per g at 433 MHz, 30.2 at 923 MHz). Semtech's drift rule (total drift per packet $< BW/(3\cdot 2^{SF})$, ×16 with LDRO) gives the allowed radial acceleration for a 32-byte packet ([impairments](lora-impairments-doppler-drift-timing.md)): at 125 kHz, 433 MHz — SF7 319 g, SF8 86 g, SF9 23 g, SF10 6.3 g; at 923 MHz half of that. High-power boosts are 5–20 g and the ground station sees most of it radially early in flight ⇒ SF ≤ 8 at 125 kHz (or SF ≤ 9 at 500 kHz) during boost. The static Doppler (≤ 2.5 kHz at Mach 5, 433 MHz) is harmless.
**Look angle** from the tail axis for a vertical rocket at altitude $h$ with the station at horizontal distance $D$: $\theta = \arctan(D/h)$. An axial dipole's gain relative to broadside ∝ $\cos^2(\tfrac{\pi}{2}\cos\theta)/\sin^2\theta$ (half-wave) → −16 dB at θ = 11° [2]. Increasing $D$ from 2 km to 5 km at $h$ = 10 km raises θ to 27° (≈ −6 dB, see [antennas on rockets](../08-antennas/antennas-on-rockets.md)).
**Plume**: exhaust plasma attenuates strongly for look angles within ~22° of the aft axis (P-band flight data, Kinefuchi et al. [3]); the LOS enters that cone when $h > D/\tan 22° = 2.5D$ — i.e. above 5 km for a station 2 km from the pad, *while the motor burns*.
**Roll** with a linear rocket antenna and a linear ground antenna: PLF = cos²(ω_r t + ψ₀) — two nulls per revolution; a circular ground antenna gives a constant −3 dB and only a frequency offset equal to the roll rate (irrelevant for LoRa) [7].

### Level 3 — erasure channel view and packet-level FEC
With LoRa's CRC, the telemetry channel is effectively a **packet-erasure channel** with erasure probability $p$ that varies strongly in time (nulls every half-roll, plume, drift during boost). For independent erasures, sending each critical field in $r$ consecutive packets reduces its loss to $p^r$; an XOR parity packet over $k$ data packets recovers any single erasure in the group at overhead $1/k$ (a (k+1, k) erasure code; Reed–Solomon over packets generalises to any $m$ erasures with $m$ parity packets — see [channel coding](../10-comms-modulation/channel-coding-fec.md)). But roll fades are **correlated over tens of ms** and plume/null outages over seconds, so interleave redundancy over a span longer than the outage (e.g. carry the last 5 GNSS fixes in every 1 Hz status frame). LoRa's own CR4/7–4/8 corrects single-bit errors per codeword — useful against residual ±1-bin errors ([PHY page](lora-phy-css-math.md)), not against erasures.

## Design equations & rules of thumb
| Rule | Value / action |
|---|---|
| Frame rate × ToA | ≤ 0.7 (unregulated) or ≤ legal duty |
| Boost phase | SF7–8 @125 kHz, or SF ≤ 9 @500 kHz; TCXO; short frames |
| Landed phase | SF10–12, narrow BW, LDRO on, repeat last fix, raise ground antenna |
| Station offset from pad | several km (look angle > 20–25° at apogee) or two stations |
| Ground polarisation | circular (−3 dB, no roll nulls) or dual-linear diversity |
| Near-pad receiver distance | ≥ 30–100 m, or 20–40 dB attenuator |
| Two radios on board | different bands, avoid harmonic relations (433 ×2 = 866 MHz), ≥ λ/2 antenna separation, filters |
| Critical data redundancy | repeat in ≥ 3 frames spread over > 1 s |
| Uplink | authenticated, counter-based, multi-step, fail-safe on link loss |
| Legal envelope (SG, licence-exempt) | 433: 10 mW e.r.p., 10 %; 866–869: 500 mW e.r.p.; 917–925: 100 mW e.r.p., 1 % — else amateur licence/permit ([19](../19-regulations-safety/singapore-imda-rules.md)) |
| Pyro/RF check | continuous TX near dummy igniter: induced RF ≥ 16.5 dB below no-fire ([19 lab safety](../19-regulations-safety/lab-safety-esd-high-power.md)) |

## Worked examples
**1. Throughput for a Space-Bar-style downlink.** Frame types: state (attitude, velocity, altitude, flight phase) 40 B at 10 Hz during ascent; GNSS 32 B at 2 Hz; health/pyro bitmask 16 B at 1 Hz. Air time per second at SF7/500: 10 × 20.5 + 2 × 18.0 + 1 × 12.9 = 254 ms → 25 % occupancy, fine. At SF7/125: 822 + 144 + 51 = 1017 ms → **exceeds 100 %** — must decimate state to 5 Hz. At SF9/125: impossible. After landing: GNSS 32 B at SF11/125 (987 ms, LDRO) every 5 s = 20 % occupancy. **Legality (Singapore):** 25 % occupancy is fine under an amateur licence (no SRD duty rule) and licence-exempt at 866–869 MHz (no duty stated, ≤ 500 mW e.r.p.), but **not** licence-exempt at 433 MHz (≤ 10 %: cut state frames to ~3 Hz at SF7/500) or at 917–925 MHz (≤ 1 %: one 40 B SF7/500 frame every ~2 s) — [band plans](ism-band-plans-duty-cycle.md), [19](../19-regulations-safety/singapore-imda-rules.md).

**2. Where the station should stand.** Apogee 10 km, station 2 km from pad: θ = 11.3° ⇒ axial-dipole loss ≈ 16 dB [2]; during burn above h = 5 km the LOS is also inside the 22° plume cone. With the E22 at SF7/500 the in-flight margin is still ≈ 45 dB at 30 km (link budget page, before the null — this is the **licensed** 33 dBm case), so 16 dB is survivable — but a carbon-fibre section or a detuned antenna could take the rest. At the **licence-exempt** 10 mW e.r.p. the same link has ≈ 20 dB less (≈ 25 dB before the null, ≈ 9 dB after it) — still closing, with little left for a detuned antenna (`tools/verify/fix_legal_vs_licensed_link_budgets.py`). Moving the station to 5 km (θ = 26.6° at apogee) or adding a second station on the other side is cheap insurance.

**3. An onboard RTK-corrections receiver next to the 2 W telemetry transmitter.** If both were in the 433 MHz band with antennas ~20 cm apart (near field; coupling perhaps −15 to −25 dB — estimate), the receiver would see +8 to +18 dBm whenever the E22 transmits: above EBYTE's 10 dBm damage rating and far beyond the ~88–99 dB blocking of an SX126x at 1–10 MHz offset. Put the corrections link in a different band (e.g. 900 MHz or 2.4 GHz when telemetry is at 433), filter its input, and schedule telemetry TX gaps (TDMA) around correction bursts. Corrections themselves are a few hundred bytes per second for multi-constellation RTCM at 1 Hz (typical; check your base station's output) — SF7/250–500 carries that easily.

**4. Pad-wait energy for the E22.** 1.2 A × 5 V = 6 W while transmitting; at 25 % occupancy (example 1) for 1 h on the pad = 1.5 Wh (+ regulator loss) — plan the battery, or telemeter at 1 Hz on the pad and switch to 10 Hz at launch detect.

**5. An example 40-byte state frame** (illustrative layout, scaled integers; adapt to the team's protocol definition):

| Bytes | Field | Encoding | Resolution / range |
|---|---|---|---|
| 1 | sync/version | protocol version (bump on any change) | — |
| 1 | source + frame type | 4 + 4 bits | primary/secondary FC, type |
| 2 | sequence counter (per type) | uint16 | wraps after 65 536 frames (1.8 h at 10 Hz) |
| 4 | flight time | uint32, ms since boot/launch | 49 days |
| 1 | flight phase + flags | enum + bits | pad…landed, armed, pyro continuity |
| 3 × 2 | position (ENU from pad) | int16, 1 m | ±32.7 km (use int24 or coarser units above that) |
| 3 × 2 | velocity | int16, 0.1 m/s | ±3276 m/s |
| 4 × 2 | attitude quaternion | int16, 1/32767 | unit quaternion |
| 2 | baro altitude | uint16, 1 m | 0–65 km |
| 2 | max/abs acceleration | int16, 0.01 g | ±327 g |
| 2 | battery V + pyro bus V | 2 × uint8, 0.05 V | 0–12.75 V |
| 2 | health / fault bitmask | 16 bits | — |
| 1 | spare / TX power step | uint8 | for link diagnostics |
| 2 | application CRC-16 | covers header + payload | detects stale-parser mismatches that pass LoRa CRC |
| **40** | | | |

Everything the ground needs to reconstruct the trajectory is in one self-contained frame; the rolling GNSS history and pyro event log go in slower frame types.

**6. Flight-phase radio plan** (bare-chip design; both ends switch on events + timeouts):

| Phase | Mode | Frames | Why |
|---|---|---|---|
| Pad (hours) | SF9/125, 1 Hz health + GNSS | low duty, low heat | long wait, check link |
| Boost / coast | SF7/500 (or SF7/250), 10 Hz state + 2 Hz GNSS | ≤ 30 % occupancy | Doppler-rate tolerance, update rate |
| Descent | SF8/250, 2–5 Hz | moderate | rotating/swinging under chute |
| Landed | SF11/125 + LDRO (SX1262) or SF9/125 (LLCC68), last fix every 5–10 s | robust | ground-reflection loss, terrain |

## Practical notes
- **Protocol hygiene** (from Space Bar flight-software lessons): one source-of-truth wire format; version byte bumped on any change; per-type sequence counters and a source field so each ground receiver can count losses unambiguously; ground parser generated from the same definition. Log **RSSI, SNR and frequency error** of every received packet with a ground timestamp, and on the rocket log every frame that was *queued* for TX — then losses are attributable (null, plume, drift, collision).
- **Deterministic decimation**: choose which frames go out by a fixed schedule synchronised to flight time, not by "whenever the UART is free"; a UART module's sub-packet splitting and LBT make timing non-deterministic ([modules](lora-modules-ebyte-rfm-heltec.md)).
- **Mode switching by flight phase**: pad (low rate, full health), boost/coast (fast SF7), descent (moderate), landed (slow robust + beacon). Both ends must switch in lock-step — use a scheduled switch keyed on flight events plus a timeout fallback, and have the ground station scan both modes (two receivers or an SDR).
- **Antennas**: see [antennas on rockets](../08-antennas/antennas-on-rockets.md): nose-cone (fibreglass) monopoles/dipoles, wraparound or flush patches, no carbon fibre in front of antennas, detuning by the airframe (re-measure S11 installed), feed-line chokes.
- **Heat & power**: 2 W modules dissipate ~4 W while transmitting; supply ≥ 1.5–2 A with bulk capacitance; brown-outs mid-packet look like RF dropouts.
- **Two radios**: the Space Bar fleet uses 433 MHz (primary) and 900 MHz (secondary) — independent MCUs, power, sensors and bands, which also gives frequency diversity against fades. Keep the harmonic relation in mind and test the pair together on the bench with a spectrum analyser.
- **Telemetry harmonics vs the on-board GNSS (W1-A5 note).** The E22's 3rd harmonic is $3f$: at the default 433.125 MHz it is 1299.375 MHz — inside the RNSS allocation 1215–1300 MHz but 0.17 MHz above the Galileo E6 band edge (1278.75 ± 20.46 MHz → 1299.21 MHz), which the ZED-F9P does not use anyway. **Low E22 channels are dangerous** (KB canonical list, from the [21 interference](../21-gnss/gnss-interference-jamming-spoofing.md) analysis): CH 0–3 (410.125–413.125 MHz) put the 3rd harmonic at 1230.4–1239.4 MHz, in the GPS L2 band (CH 0–2 inside the 1227.6 ± 10.23 MHz main lobe; L2C itself occupies ≈ ±1 MHz), CH 5–6 at 1245.4–1248.4 MHz inside GLONASS L2OF (1242.9–1248.6 MHz channel centres; CH 4 = 1242.4 MHz on its lower edge), and CH 7–9 on the ZED-F9P's second-band filter skirts — **avoid CH 0–9** — all inside the ZED-F9P's second-band front end, which spans E5b/B2I at 1207 MHz up to GLONASS L2 ([21 GNSS signals](../21-gnss/gnss-signals-and-codes.md)); even an off-signal harmonic there can compress the front end. A harmonic that merely meets the regulatory −30 dBm (TS SRD Table 1-a) is still ~100 dB above a −130 dBm GNSS signal, so on-board coexistence needs the PA's harmonic filter, physical separation and the GNSS SAW — and a channel plan that keeps $3f$ out of 1164–1300 MHz where possible (3f clears 1300 MHz for carriers above 433.33 MHz: CH 24 = 434.125 MHz → 1302.4 MHz is better than the default CH 23 and still inside the 433.05–434.79 MHz band. CH 24 is also the band-edge-safe choice: the whole channel $f_c \pm BW/2$ must be in 433.05–434.79 MHz, and CH 23 at BW 250 kHz starts at 433.000 MHz, so use CH 23 only at BW ≤ 125 kHz (lower edge 433.0625 MHz); anywhere in 434–440 MHz works under an amateur licence). Spectrum check: transmit into the flight antenna with the GNSS receiver running and watch its C/N0 on L2 ([08 GNSS antennas](../08-antennas/gnss-antennas.md), [19 spectrum allocation Example 3](../19-regulations-safety/spectrum-allocation-ism-bands.md#worked-examples)).
- **Pyro / RF interaction test** (W3-C5 X12): with the flight radio transmitting continuously at flight power into the flight antenna, instrument a dummy igniter (or the e-match's bridgewire replaced by a sensing resistor/thermocouple) in the real harness position and confirm the RF-induced current is ≤ 15 % of the no-fire current (= 16.5 dB margin, MIL-STD-464C §5.4) on every frequency to be used and with the pyro channels both disarmed and armed-but-not-firing (19 lab-safety Example 3); keep leads twisted and loops small. Method, SLP-20 distances and the Friis bound are on [lab safety](../19-regulations-safety/lab-safety-esd-high-power.md) (`tools/verify/reg_hero_distance.py`).
- **Uplink safety**: prefer no uplink; if needed (e.g. abort/arming on the pad only), use message authentication codes with monotonic counters, time windows, two-step arm/fire, no command that can fire pyros in one packet, and physical interlocks. Link loss must never arm anything.
- **Beyond LoRa:** for how near-limit weak-signal modes compare per bit, and an FT8-style recovery beacon, see [10 weak-signal modes § Example 2](../10-comms-modulation/weak-signal-digital-modes.md#example-2--ft8-versus-lora-sf12-at-the-same-bit-rate) and [§ Example 4](../10-comms-modulation/weak-signal-digital-modes.md#example-4--could-a-rocket-recovery-beacon-use-an-ft8-style-waveform); for SF adaptation (and why ADR does not suit a rocket) see [10 BER § Level 3c](../10-comms-modulation/ber-ebn0-and-shannon.md#level-3c--capacity-of-fading-channels-ergodic-outage-and-adaptive-modulation-w5-s8).

## Commercial rocket trackers and beacons

What the hobby market sells, as of 2025–2026 manuals and product pages. Use it as a benchmark and as a backup for the team's own radios. Powers are conducted output as stated by the maker. "SG" means usable licence-exempt in Singapore at that band and power ([19](../19-regulations-safety/singapore-imda-rules.md)).

| Product | Band | Power | Protocol / rate | Range evidence | Receiver; SDR-receivable? | SG licence-exempt? |
|---|---|---|---|---|---|---|
| **Featherweight GPS Tracker** (and Swift) | 915 MHz, 28 frequencies × 2 = 56 channels | 100 mW (maker; one retailer lists 50 mW); Swift 158 mW | LoRa, two-way: the ground station ACKs over LoRa and relays to a phone by Bluetooth; pointing arrow from GNSS | 145 900 ft (44.5 km) slant range, 2017, stub antennas (maker) [4][10] | Featherweight ground station + phone app; LoRa decodable with gr-lora_sdr if SF/BW known | no: the US 902–928 MHz plan; even in 917–925 MHz, 100 mW conducted ≈ 100 mW e.r.p. needs ≤ 1 % duty |
| **Eggtimer Eggfinder** (TX + RX/LCD; also inside Eggtimer TRS/Quasar) | 900 MHz, 909–925 MHz in 2 MHz steps (US; Aus/NZ 915–928) | 100 mW | HopeRF HM-TRP (Si4432-class FSK), NMEA position at 1 Hz, one-way | "tested > 10 000 ft" LOS (manual) vs "over 6 miles" (maker) [11] | Eggfinder RX/LCD or any HM-TRP; plain FSK, so an SDR can decode it with the right deviation/rate | no: not a SG band at 909–915 MHz; 917–925 MHz channels need ≤ 1 % duty at 100 mW e.r.p. |
| **BigRedBee BRB900** (legacy) / **BRB900L** (LoRa) | 900 MHz; BRB900L also 433 MHz | 250 mW (BRB900); 100 mW (BRB900L) | proprietary FSK (BRB900); LoRa at 1 Hz (BRB900L) | maker: 6–10 mi or "15 miles in the air"; BRB900L rated to 80 km altitude [12] | BRB receivers with LCD; LoRa decodable | 433 MHz version needs an amateur licence (maker), and in SG 100 mW is > 10 mW e.r.p. |
| **BigRedBee BeeLine GPS** | 70 cm (also 2 m at 5 W) | 100 mW | APRS AFSK 1200 baud | used above 100 kft (maker) [12] | any APRS radio/TNC; RTL-SDR + direwolf | needs an amateur licence |
| **Altus Metrum TeleMetrum / TeleMega / TeleGPS** | 70 cm, default 434.550 MHz | TeleMetrum 10 mW (v1), 40 mW (later); TeleGPS not stated by the maker (one retailer: 16 mW) | GFSK 38.4/9.6/2.4 kbaud with K=4 convolutional FEC, 10 Hz ascent; optional APRS; **½ s RDF tone every 5 s in descent and after landing** [1][13] | no range figure from the maker; flown widely in US high-power rocketry | TeleDongle/TeleBT; open-source AltOS, so SDR decoding is documented | needs an amateur licence (434.550 MHz is in the SRD band, but 40 mW > 10 mW e.r.p. and the telemetry exceeds 10 % duty) |
| **RDF beepers** (e.g. LL Electronics; Adept T400; UK "TRAXA") | 216–220 MHz (LL, US); 433.9 MHz (Adept); 433.92 MHz (TRAXA) | < 3 mW CW pulses (LL); ~10 mW (TRAXA) | unmodulated or tone-modulated pulses, days of battery | maker claims miles on the ground (anecdotal) [14] | dedicated −150 dBm-class receivers (LL) or any 433 MHz receiver/SDR with a Yagi | 433.92 MHz at ≤ 10 mW e.r.p. and ≤ 10 % duty can be; 216–220 MHz cannot |
| **BLE / UWB tags** (AirTag, SmartTag, Tile) | 2.4 GHz BLE; 6.5–8 GHz UWB | ~0 to +10 dBm class | crowd-sourced: a nearby phone must hear the tag and report its own GNSS position | tens of metres for BLE; UWB "precision finding" within ~10 m | phone only | legal as consumer devices, **but useless in an empty field**: no passing phones, short BLE range, UWB only at the end |

**What this means for Space Bar.**
1. Every product here sends **GNSS position plus a beacon**. Only Altus Metrum adds an explicit DF tone, and that is the cheapest feature to copy (see [12 DF procedure](../12-phased-arrays/adaptive-beamforming-doa.md#practical-direction-finding-for-rocket-recovery)).
2. The 900 MHz products are built for US Part 15 hopping/digital rules and are **not licence-exempt in Singapore** at their stated power and duty. The 70 cm products need an amateur licence everywhere.
3. All of them are receivable with an RTL-SDR on the ground, which makes a cheap cross-check and backup station possible: APRS via direwolf, LoRa via gr-lora_sdr, FSK via a GNU Radio flowgraph ([ground station](ground-station-design.md)).
4. Ranges are maker claims at line of sight. On the ground every one of them is limited by the landed two-ray path ([link budget Example 4](lora-sensitivity-and-link-budget.md)).

## Common mistakes & misconceptions
- **"An AirTag in the nose cone will find it."** It works only where phones pass by. Carry a radio beacon.
- **"A 900 MHz tracker that is licence-free in the US is licence-free here."** Check band, e.r.p. and duty against the local rules.
- **"More SF = more reliable telemetry."** In flight, SF10–12 at 125 kHz is *less* reliable (Doppler rate, drift, fewer frames). Save slow modes for after landing.
- **"We lost telemetry at apogee because of range."** Usually geometry: tail-on nulls, plume, or a polarisation null — check the look angle before adding power.
- **"LoRa has FEC so we're covered."** Bit-level coding doesn't fix whole-packet erasures.
- **Time-based rate limiting** ("send when ready") hides losses and overloads the channel when the MCU is fast; use a fixed schedule.
- **Testing the link on the bench with both units 1 m apart at full power** — receiver overload and possible damage; use attenuators.
- **Same-band RX and TX on one vehicle** (e.g. RTK corrections and telemetry both at 433 MHz).
- **Trusting "encryption" in EBYTE modules for command links.**

## How to simulate / verify
- `python3 tools/verify/lora_toa.py` — frame air time and occupancy; `lora_doppler.py` — acceleration limits per SF/BW; `lora_link_budget.py` — flight and landed budgets, near-pad levels.
- **HIL**: inject recorded flight acceleration profiles into a Doppler emulator (SDR re-transmitting a LoRa waveform with a frequency ramp) and measure PER per SF — the team's HIL philosophy applied to RF.
- **Range/roll test**: rotate the rocket section on a turntable at flight roll rates in front of a ground antenna 100+ m away (with attenuation) and record per-packet RSSI; compare linear vs circular ground antennas.
- **Pyro/RF**: continuous-TX dummy-igniter test (Practical notes) — `tools/verify/reg_hero_distance.py` for the matched-lead worst case.
- **Legal vs licensed budgets**: `tools/verify/fix_legal_vs_licensed_link_budgets.py`.
- **Post-flight**: plot per-packet RSSI/SNR/FEI against flight time, altitude, look angle and IMU acceleration; this is the only way to validate the models above for your airframe.

## Open questions / gaps
- No verified, published LoRa PER-vs-acceleration data from real rocket flights were found; Norby (LEO) and lab studies are the closest. Space Bar's own flight logs could fill this.
- Tracker table: output powers are the makers' figures (Featherweight's own pages disagree with a retailer). No independent measurements of any product's power or spectrum were found; an SDR check of each product's air interface would settle SF/BW and deviation.
- University team telemetry choices (USC RPL, Boston University, TU Delft DARE, SEDS chapters, EPFL Rocket Team) were not researched in depth; the SAC/Stanford/MSU items are search-snippet level.
- Plume attenuation at 433/900 MHz for amateur solid motors (APCP) is unquantified here (flight data are P-band on a large solid motor).
- RTCM bandwidth for the ZED-F9P base configuration used by the team was not measured.

## Sources
1. Altus Metrum, *AltOS Telemetry* documentation (2025) — 38.4/9.6/2.4 kbaud GFSK, deviation/bandwidth, rate-½ K=4 convolutional code, 4×4 interleaving, PN whitening, fixed 32-byte packets, packet types, 10 Hz ascent / 1 Hz descent, CC1111/CC1120/CC1200. https://altusmetrum.org/AltOS/doc/telemetry.html (vendor docs)
2. This KB, [Antennas on rockets](../08-antennas/antennas-on-rockets.md) (W1-A6) — axial nulls (NASA wraparound antennas), 11° look angle → −16 dB, plume cone, `tools/verify/ant_rocket.py`. (internal)
3. K. Kinefuchi, K. Okita, I. Funaki, T. Abe, "Prediction of in-flight RF attenuation by a rocket plume," *J. Spacecraft & Rockets* 52(2), 2015 — strong attenuation within ~22° of the aft axis (via W1-A6). (peer-reviewed)
4. Featherweight Altimeters, *GPS Tracker User's Manual* (Feb 2025) — 915 MHz LoRa tracking to >137 000 ft altitude and 145 900 ft range (2017) with stub antennas; loss after landing; lost-rocket relay. (manufacturer — anecdotal)
5. Spaceport America Cup / IREC reports: Stanford SSI 2017 (XBee-900HP, ≤ 10 km with omni dipoles), Stanford "Project Olympus" 2022 (LoRa telemetry), MSU LoRa 915 MHz 1–10 Hz — search-result summaries only. (anecdotal)
6. arXiv:2506.20858 (2025) — Norby CubeSat: SX1278 at 436.703 MHz from 560 km, ~1 M packets received; Doppler-rate failures at high elevation. (preprint)
7. This KB, [Antenna polarization & CP](../08-antennas/antenna-polarization-and-circular-polarization.md) — roll nulls with linear–linear, spin Doppler with CP. (internal)
8. Space Bar avionics knowledge base (user's own notes): downlink-only telemetry, protocol/versioning/sequence-counter lessons, E22-400T33D primary and E220-900T30D secondary, RTK via separate LoRa bridge. (internal, user-provided)
9. M. Brzynska, K. Klimaszewski, K. Martin, "A Localisation and Telemetry LoRa Node for Rockets," SoftCOM 2023 — STM32WL at 433 MHz, TDoA localisation with 20.8 ns timer, 40 m error in ground tests. (peer-reviewed conference)
10. Featherweight Altimeters, *GPS Tracker User's Manual* (20 Feb 2025), https://www.featherweightaltimeters.com/uploads/1/0/9/5/109510427/gps_tracker_manual_2025feb20.pdf — 915 MHz LoRa, GS ACK, Bluetooth to phone, 28 × 2 channels, 112/60 mA; product pages: 100 mW (maker), 50 mW (Apogee Components listing), Swift 158 mW. (manufacturer)
11. Eggtimer Rocketry, *Eggfinder GPS Tracker Users Manual* (TX Rev B6 / RX Rev B4D) and *Eggfinder LCD Users Manual* Rev 2.01c (2021) — 100 mW, 909–925 MHz in 2 MHz steps, HM-TRP-900, 1 Hz NMEA, > 10 000 ft tested; Eggfinder FAQ ("over six miles"). https://eggtimerrocketry.com (manufacturer — claims differ)
12. BigRedBee, product pages and FAQ (shop.bigredbee.com, accessed 2026-10-12) — BRB900 250 mW proprietary 900 MHz, BRB900L 100 mW LoRa 433/900 MHz at 1 Hz (433 MHz needs an amateur licence), BeeLine 70 cm APRS 100 mW, 2 m 5 W. (manufacturer)
13. Altus Metrum, *The Altus Metrum System: An Owner's Manual*, https://altusmetrum.org/AltOS/doc/altusmetrum.html — 10 mW → 40 mW radio, APRS, ½ s RDF tone every 5 s after apogee/landing, default 434.550 MHz. (manufacturer manual)
14. Rocketry Forum threads on LL Electronics (216–220 MHz, < 3 mW CW, −150 dBm receivers), Adept T400 (433.9 MHz) and UK TRAXA (433.92 MHz, 10 mW) beacons; ukrocketman.com RF-transmitter notes. (forum — anecdotal)
15. Apple, AirTag technical specifications and Find My network description (apple.com) — Bluetooth LE + UWB, location via nearby Apple devices. (vendor — not re-read in this pass; the BLE/UWB ranges in the table are order-of-magnitude)
