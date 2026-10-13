---
title: Recipe — LoRa rocket telemetry downlink (433 + 900 MHz) for a 10 km apogee, 15 km slant-range flight
domain: 20-projects-recipes
slug: lora-rocket-telemetry-link
tags: [recipe, lora, rocket-telemetry, e22-400t33d, e220-900t30d, sx1268, llcc68, link-budget, doppler-rate, spreading-factor, packet-design, dual-band, ground-station, range-test, attenuator-method, pre-registration, imda, irec]
prerequisites:
  - ../15-lora-ism-radios/rocket-telemetry-radio-design.md
  - ../15-lora-ism-radios/lora-sensitivity-and-link-budget.md
  - ../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md
  - ../09-propagation-link-budget/link-budget-methodology.md
  - ../08-antennas/antennas-on-rockets.md
related:
  - ground-station-tracking-yagi.md
  - bandpass-filter-design-walkthrough.md
  - gnss-front-end-design.md
  - sdr-receiver-build.md
  - design-review-checklists.md
  - ../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md
  - ../15-lora-ism-radios/ground-station-design.md
  - ../19-regulations-safety/singapore-imda-rules.md
  - ../19-regulations-safety/international-rules-for-competitions.md
  - ../17-test-measurement/antenna-range-ota-testing.md
  - ../09-propagation-link-budget/link-margin-availability.md
level: intermediate
confidence: medium
last_updated: 2026-10-14
---

# Recipe — LoRa rocket telemetry downlink (433 + 900 MHz), 10 km apogee, 15 km slant range

This is an end-to-end design walkthrough. It does not re-derive the physics — each step links to
the KB page that does. All numbers come from `python3 tools/verify/proj_lora_link.py` (trajectory,
Doppler, air time, cascade, budgets, range-test numbers) unless another script is named.

## Questions this page answers
- How do I design a complete LoRa telemetry downlink for a rocket that goes to 10 km?
- Which spreading factor and bandwidth survive the boost of a 10 km rocket at 433 MHz and at 900 MHz?
- Will the EBYTE default "2.4k" air rate lose packets during boost?
- Where should the ground station stand so the rocket's tail null doesn't blank the link near apogee?
- How much link margin do I really have at 15 km with a Singapore-legal 10 mW, and with a licensed 2 W?
- Does 10 Hz telemetry fit inside a 10 % or 1 % duty-cycle rule?
- How do I run the 433 MHz primary and the 900 MHz secondary without one interfering with the other?
- How do I range-test the link in Singapore without breaking the power limit?
- Why does a conducted attenuator test of a 2 W module not work on a bench?
- What should I predict *before* the flight so the flight can prove me right or wrong?
- How much does the whole telemetry system cost?

## TL;DR
- **The flight link is never power-limited at 10 km; it is limited by geometry, dynamics and air time.** Licensed 33 dBm at 433 MHz leaves ≈ 41 dB of margin at 15 km even inside the tail null; the Singapore-legal 10 mW e.r.p. still leaves ≈ 19 dB with a masthead-LNA ground station and ≈ 30 dB along the actual trajectory from a well-placed station.
- **SF/BW is chosen by Doppler rate and air time, not by sensitivity.** For the modelled 10 km flight (11 g boost, 8.7 g drag deceleration after burnout, Mach 2.0), Semtech's per-packet drift rule is met with margin by **SF7–8 at 125 kHz, SF7–9 at 250–500 kHz** in both bands; **SF9/125 fails 1–10 % of boost/coast packets at 868–905 MHz** (but passes at 433 MHz), and **SF10–12/125 fail 7–35 %** in either band. The EBYTE default "2.4k" air rate (every candidate mapping has ≈ 244 Hz bins and ≈ 0.3 s frames) behaves like SF9/125 — **do not fly the E220 at its default rate**.
- **Air time**: 40 B state @10 Hz + 32 B GNSS @2 Hz + 16 B health @1 Hz occupies **102 % at SF7/125 (impossible), 51 % at SF7/250, 25 % at SF7/500**. Under Singapore's 10 % duty rule (433 MHz, sub-band 26a) a combined 48 B frame can go at most **4.1 Hz (SF7/500) / 2.0 Hz (SF7/250)**; under 1 % (917–925 MHz LoRa) only **0.4 Hz** — useless for flight telemetry.
- **Station placement beats power**: a station **5 km cross-range** never sees the aft axis closer than 29° (≥ −6 dB pattern loss); a station 2 km cross-range spends 22 s below 20° (min 13.5°); a station **up-range** of a pad with a downrange tilt looks straight up the tail (0°) near apogee. Put the primary station cross-range 3–5 km, add a second station on another azimuth.
- **Ground chain**: LNA (0.8 dB NF, 18 dB) → SAW → 15 m LMR-240 (2.6 dB) → 3.5 dB splitter → module gives **NF 2.0 dB** vs 6.3 dB (module direct) and 10.3 dB (module after 15 m RG-58, 4.3 dB). SF7/250 sensitivity improves from −121.5 to **−125.5 dBm** — if the site's man-made noise is low (city noise at 425 MHz raises the effective NF back to ≈ 6.6 dB).
- **Frequency plan**: primary **434.125 MHz (CH 24)** by default — it fits the Singapore band at any LoRa bandwidth and its 3f (1302.4 MHz) clears the 1215–1300 MHz RNSS band; 433.125 MHz (CH 23, the module default) remains acceptable for licensed/abroad use or at ≤ 125 kHz; never CH 0–9, whose 3rd harmonic lands in or beside GPS/GLONASS L2 ([21 interference](../21-gnss/gnss-interference-jamming-spoofing.md)); for **Singapore licence-exempt tests at BW 250/500 kHz use CH 24 (434.125 MHz)** — 433.125 MHz ± 125 kHz starts at 433.000 MHz, *below* the 433.05 MHz band edge (433.125 MHz is fine only at ≤ 125 kHz) — and then move the secondary to CH 17 (867.125 MHz), because 2 × 434.125 = 868.25 MHz would sit 125 kHz from CH 18 (`proj_preflight_rf.py`); secondary **868.125 MHz (CH18) at ≤ 24 dBm** in Singapore (sub-band 29, 500 mW e.r.p.) — **never CH16 (866.125 MHz): it sits 125 kHz from the E22's 2nd harmonic** — and 902.5–908.5 MHz Mode A (500 kHz, ≤ 30 dBm, ≤ 6 dBi) at IREC.
- **Range test**: conducted testing of a 2 W module to its sensitivity needs ≈ 145–155 dB of isolation — not achievable on a bench. Instead do a **radiated, 15-km-equivalent test at 1–2 km at legal power** (10 mW e.r.p.) with a step attenuator at a *shielded* receiver: insert 39.7 dB at 1 km (33.7 dB at 2 km) and expect PER < 1 % with ≈ 20 dB still spare (SF7/250).
- **Pre-registered predictions** (section below) cover NF, sensitivity, range-test attenuation, in-flight RSSI, Doppler, drift losses and landed range, each with a tolerance and a pass/fail interpretation.

## Intuition (no math)
A rocket telemetry link is three different links glued together. On the pad the rocket is close and loud; in flight it is far but in clear sky, so the signal is strong except when the rocket's antenna points its "blind spot" (the tail) at you or the rocket rolls its polarisation away; after landing it lies in grass and the ground swallows the signal. So the design job is: pick a *fast* LoRa mode that the rocket's acceleration cannot smear, send self-contained frames at a fixed schedule so every loss is countable, put the ground station where it looks at the rocket's side rather than its tail, and give the landed phase its own slow, robust mode. Power is the last knob, and in Singapore it is the one the law fixes for you.

## Requirements
| ID | Requirement | Value | Source / rationale |
|---|---|---|---|
| R1 | Apogee | 10 km AGL | mission |
| R2 | Design slant range | 15 km (covers apogee from a 5–11 km offset station and descent drift) | mission |
| R3 | Ascent update rate | state ≥ 10 Hz, GNSS ≥ 2 Hz, health ≥ 1 Hz | estimator/phase monitoring; Altus Metrum flies 10 Hz ascent ([rocket telemetry design](../15-lora-ism-radios/rocket-telemetry-radio-design.md)) |
| R4 | Ascent packet loss | ≤ 5 % averaged over boost+coast, no gap > 2 s | recovery decision support |
| R5 | Descent/landed | last GNSS fix ≥ every 10 s until recovery; landed range ≥ 3 km with a 6 m mast | recovery |
| R6 | Redundancy | two independent links (primary FC 433 MHz, secondary FC 900 MHz), independent power and MCU | fleet architecture (Avionics B + C) |
| R7 | Legality | Singapore: TS SRD limits or a licence/permit; abroad: venue rules | [IMDA page](../19-regulations-safety/singapore-imda-rules.md), [competitions](../19-regulations-safety/international-rules-for-competitions.md) |
| R8 | Observability | per-packet RSSI (SNR, frequency error where the radio allows), GNSS-timed ground timestamps, raw IQ recording | record-everything ethos |
| R9 | Downlink-only | no uplink commands | team decision (safety) |

## Architecture options and trade study
| Option | What | + | − | Verdict |
|---|---|---|---|---|
| A. UART modules as flown (E22-400T33D, E220-900T30D) | EBYTE firmware; "air data rate" menu | zero RF design; already on Avionics B/C | **SF/BW behind air-rate codes unpublished**; RSSI only; UART buffering adds jitter; LBT up to 2 s; default E220 channel illegal in SG ([modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md)) | fly it only after the SDR mapping measurement; LBT off |
| B. SPI power modules + RadioLib (E22-400M33S / E22-400M22S, E22-900M30S / E220-900M30S) | same chips + PA/LNA; firmware sets SF/BW/CR/LDRO | full control; per-packet SNR + frequency error; IRQ timestamps; flight-phase mode switching; exact legal power setting | driver + state machine work; RF switch control pins | **recommended for the next board** |
| C. Bare SX1262/SX1268 + own PA/LPF | chip-down design | smallest, cheapest, full control | full RF layout, harmonic filter, PA design ([LNA/PA parts](../18-components-parts/lna-pa-gain-block-mmics.md)) | only if board space demands it |
| D. GFSK radio (CC1200/Si4463, Altus-style 38.4 kbaud + convolutional code) | non-LoRa | high rate, short frames, very Doppler-tolerant | ≈ 15–20 dB less sensitive than LoRa SF7 at equal rate class; different ground receiver | good backup band; see [other ISM radios](../15-lora-ism-radios/other-ism-radios-fsk-2g4.md) |

Decision: keep Option A for the current fleet with the checks below, and design Option B into the next flight computer (one module footprint per band, SPI to the ESP32-S3).

## The math — design calculations

### Level 1 — the four budgets
1. **Air-time budget** $\sum_i f_i\,T_{oa}(L_i) \le d$ with $T_{oa}$ from the Semtech formula ([LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md)) and $d$ = 0.7 (practical cap) or the legal duty cycle ([band plans](../15-lora-ism-radios/ism-band-plans-duty-cycle.md)).
2. **Drift budget** $|\Delta f_D| = \frac{f_c}{c}\,|\dot r(t+T_{oa}) - \dot r(t)| \le \frac{BW}{3\cdot 2^{SF}}$ (×16 with LDRO) for every packet ([impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)). This is the exact per-packet form of the "allowed acceleration" tables.
3. **Link budget** $P_{rx} = P_{tx} - L_{tx} + G_t(\theta) - L_{fs}(R) - L_{pol} - L_{point} + G_r$, sensitivity $S = -174 + 10\log BW + NF_{sys} + \mathrm{SNR}_{req}(SF)$, margin $P_{rx}-S$ ([link budget methodology](../09-propagation-link-budget/link-budget-methodology.md), [LoRa sensitivity](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md)).
4. **Legal budget** e.r.p. $= P_{tx} - L_{tx} + G_{t,max} - 2.15$ dB against the venue's limit ([IMDA](../19-regulations-safety/singapore-imda-rules.md)).

### Level 2 — the flight that drives the radio
A point-mass 2-D model (ISA density, Cd(M) 0.45 → 0.65 transonic → 0.5, 130 mm body, 3° rail tilt) tuned to 10 km:

| Quantity | Value |
|---|---|
| Motor | 3500 N average, 6.93 s burn, 11.8 kg propellant, Isp 210 s; lift-off mass 31.8 kg |
| Burnout | 692 m/s (Mach 2.0) at 2457 m |
| Peak acceleration (burn) | 11.1 g kinematic |
| Peak drag deceleration (coast) | 8.7 g along track |
| Apogee | 9998 m at 41.3 s, 1.57 km downrange |
| Descent | drogue 30 m/s, main 6 m/s at 450 m, 8 m/s wind → lands 4.7 km downrange at 434 s |

Seen from four candidate stations (pad at origin, downrange = +x):

| Station | Max slant R | Max radial accel | Peak Doppler 433 / 920 MHz | Min look angle from aft axis (coast) | Time < 20° | Max elevation rate |
|---|---|---|---|---|---|---|
| A: 2 km cross-range | 10.3 km | 13.7 g | 0.78 / 1.65 kHz | 13.5° at z = 8.8 km | 21.7 s | 10.4 °/s |
| B: 5 km up-range | 12.0 km | 11.0 g | 0.53 / 1.12 kHz | **0.0°** at t = 36.5 s | 10.4 s | 5.8 °/s |
| C: 5 km cross-range | 11.3 km | 11.1 g | 0.48 / 1.01 kHz | **29.0°** | 0 s | 6.3 °/s |
| D: 5 km down-range | 10.6 km | 11.1 g | 0.43 / 0.91 kHz | 35.6° | 0 s | 6.9 °/s |

Two non-obvious results:
- **A close station sees more radial acceleration than the rocket feels** (13.7 g vs 11.1 g): the line of sight rotates, adding $v_\perp^2/R$ to $\ddot r$ — the same "zenith pass" effect that broke high-SF LoRa on the Norby CubeSat ([impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)).
- **Up-range stations look up the tail** when the trajectory arcs away from them; the point-mass model makes this exact (0°), a real rocket weathercocking into wind will do something similar. Down-range and cross-range stations do not.
- No station ≥ 2 km away looks through the 22° plume cone *during the burn* for this trajectory (burnout at 2.5 km altitude), so burn-phase dropouts, if they occur, point to something other than plume ([antennas on rockets](../08-antennas/antennas-on-rockets.md)).

**Doppler-rate check** (40 B frame, CR4/5, 8-symbol preamble, explicit header; % of packet start times in boost+coast that exceed the Semtech per-packet limit):

| Setting | ToA | Limit | 433 MHz: A / C / along-track | 868 MHz: A / C / along-track | 905 MHz (IREC/US): A / C / along-track |
|---|---|---|---|---|---|
| SF7/125 | 82 ms | 326 Hz | 0 / 0 / 0 % | 0 / 0 / 0 % | 0 / 0 / 0 % |
| SF8/125 | 154 ms | 163 Hz | 0 / 0 / 0 % | 0 / 0 / 0 % | 0 / 0 / 0 % |
| SF9/125 | 288 ms | 81 Hz | 0 / 0 / 0 % (max 56 Hz) | **7.6 / 1.4 / 9.8 %** | **7.9 / 1.9 / 12.4 %** |
| SF10/125 | 535 ms | 41 Hz | **11 / 7 / 22 %** | **25 / 12 / 34 %** | **27 / 12 / 35 %** |
| SF12/125 (LDRO) | 1974 ms | 163 Hz | **11 / 7 / 17 %** | **24 / 12 / 31 %** | **25 / 12 / 32 %** |
| SF7–9/250 | 41–144 ms | 651–163 Hz | 0 % | 0 % | 0 % |
| SF10/250 | 267 ms | 81 Hz | 0 % | 7.0 / 0.3 / 4.9 % | 7.4 / 0.9 / 7.9 % |
| SF7–9/500 | 21–72 ms | 1302–326 Hz | 0 % | 0 % | 0 % |
| SF11/500 | 247 ms | 81 Hz | 0 % | 6.3 / 0 / 0 % | 6.7 / 0 / 0 % |

Losses at the high-SF settings cluster in the burn (thrust) and just after burnout (drag), exactly where the flight is most interesting. **Rule for this vehicle: SF ≤ 8 at 125 kHz, SF ≤ 9 at 250/500 kHz, in both bands.** A harder motor (20 g) halves every "safe" margin — rerun the script with your thrust curve.

**The EBYTE air-rate trap.** The E22/E220 "2.4k" default is one of SF9/125, SF10/250 or SF11/500 (all ≈ 1.8–2.1 kb/s; [modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md)). All three have a 244 Hz bin and a ≈ 0.25–0.3 s frame, so all three sit at the edge in the table above: fine at 433 MHz, **1–12 % loss at 868–905 MHz during boost**. Use 9.6k (SF7/250 or SF8/500 candidates) or 19.2k (SF7/500 candidate) for flight — and measure which one it really is.

### Level 3 — where these models break
- The point-mass trajectory has no attitude dynamics: real look angles near apogee depend on weathercocking, coning and tumbling. Treat the "0° up-range" result as a warning, not a number.
- The −20 dBi floor on the axial-dipole null is an assumption: body currents, coax and the nose-cone ground fill the null by an unknown amount. Real nulls may be deeper (the pattern formula alone goes to −∞).
- The Semtech drift rule is a datasheet *guideline*, not a measured PER curve; in-packet tracking by the chip may be better or worse. That is exactly why the drift predictions below are pre-registered for falsification.
- The noise model assumes a 290 K antenna; a site near town at 433 MHz can be 1150 K (ITU-R P.372), which erases the LNA's advantage ([thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md)).
- Free-space loss is assumed for the flight; multipath from the ground under the station (low elevation early in flight) adds ±6 dB lobing.

## Design equations & rules of thumb
| Rule | Value for this design |
|---|---|
| Frames per second allowed | $d/T_{oa}$: 48 B at SF7/250 → 14.4 Hz (70 %), 2.0 Hz (10 %), 0.2 Hz (1 %) |
| Doppler rate | 14.2 Hz/s per g at 433 MHz, 30.2 Hz/s per g at 923 MHz |
| Safe boost settings (≤ 11–14 g radial) | SF ≤ 8 @125 kHz; SF ≤ 9 @250/500 kHz |
| Tail-null avoidance | station offset ≥ 0.5 × apogee cross-range (look angle ≥ 29° here) |
| Masthead LNA benefit | 4.3 dB vs module direct; 8.3 dB vs module after 15 m RG-58 at 433 MHz |
| Linear rocket → CP ground antenna | −3 dB constant, no roll nulls |
| Near-pad receiver level (2 W, 10 dBi) | +19.5 dBm at 1 m, −0.5 dBm at 10 m, −10 dBm at 30 m, −20.5 dBm at 100 m |
| Landed range (two-ray, 0.2 m / 2 m; other assumption sets in [09 Example E](../09-propagation-link-budget/link-budget-methodology.md#example-e--landed-rocket-the-case-that-actually-limits-recovery)) | 433 MHz 33 dBm SF9/125: 7.5 km; 10 mW e.r.p.: 2.1 km (masthead LNA) — 5.6 / 1.7 km with a bare module |
| E22 channels to avoid with onboard GNSS | CH 0–9 (3f in or beside GPS/GLONASS L2); CH 10–22 (3f in Galileo E6 / BeiDou B3); use CH 24 |
| 15-km-equivalent attenuation at test distance $d$ | $20\log(15\,\mathrm{km}/d)$ + 16 dB null: 39.7 dB at 1 km |

## Worked examples

### 1. Packet design and schedule (both links)
Use the 40-byte self-contained state frame from [rocket telemetry design, example 5](../15-lora-ism-radios/rocket-telemetry-radio-design.md) (version, source+type, per-type sequence counter, flight time, phase/flags, ENU position, velocity, quaternion, baro altitude, peak acceleration, battery/pyro volts, fault bitmask, TX-power byte, application CRC-16). Add:
- a **32-byte GNSS frame** carrying the current fix plus the last three fixes as deltas (so one received frame recovers the track over the last 1.5 s — packet-level redundancy against correlated fades, [link margin](../09-propagation-link-budget/link-margin-availability.md));
- a **16-byte health frame** (radio config echo: SF/BW/power/channel, board ID, uptime, SD/NOR drop counters);
- on the UART modules, **write each frame in one burst ≤ the sub-packet size** (240 B E22, 200 B E220) so it is one radio packet.

| Setting | Full schedule occupancy | Verdict |
|---|---|---|
| SF7/125 | 101.7 % | impossible; at 125 kHz-limited venues decimate state to 5 Hz (≈ 61 %) |
| SF7/250 | 50.9 % | **primary choice** (433 MHz, 868 MHz) |
| SF7/500 | 25.4 % | best Doppler/air time; required at IREC Mode A; sensitivity 4.5 dB worse than SF7/250 |
| SF8/500 | 47.5 % | alternative if SF7/500 margin is short |
| SF9/125 | 353.6 % | pad/landed modes only |

Flight-phase plan for Option B radios (both ends switch on flight events + timeouts; the ground scans both): pad SF9/125 1 Hz health+GNSS → boost/coast SF7/250 full schedule → descent SF8/250 at 2–5 Hz → landed SF11/125 + LDRO (SX1268) or SF9/125 (LLCC68, its limit) GNSS every 5 s.

### 2. Ground receive chain
| Chain | System NF | SF7/250 sensitivity |
|---|---|---|
| module direct (1 m jumper) | 6.3 dB | −121.2 dBm |
| module after 15 m RG-58 (4.3 dB) | 10.3 dB | −117.2 dBm |
| **LNA (0.8 dB, 18 dB) → SAW 2 dB → 15 m LMR-240 2.6 dB → splitter 3.5 dB → module** | **2.01 dB** | **−125.5 dBm** |
| SAW first, then LNA | 3.59 dB | −123.9 dBm |

With antenna temperature 100 / 290 / 1150 K the effective NF is −0.3 / 2.0 / 6.6 dB (coax losses from the fits in [coax & cables](../03-transmission-lines-matching/coax-and-cables.md): RG-58 28.7 dB/100 m, LMR-240 17.0 dB/100 m at 433 MHz) — measure the site noise floor before trusting the LNA advantage. Design detail (LNA choice, SAW, bias-tee, limiter) is in [ground-station-tracking-yagi](ground-station-tracking-yagi.md).

### 3. Static worst-case budget at 15 km
Assumptions: rocket antenna −14 dBi (axial dipole 11° off the tail), rocket feed 0.5 dB, CP ground antenna (−3 dB against the linear rocket antenna), 1 dB pointing, ground gain 10 dBic (433) / 12 dBic (868–920), SF7/250 unless noted, 500 kHz rows +1.5 dB (datasheet penalty).

| Configuration | Conducted | Received | Margin, LNA chain | Margin, bare module | Legal basis |
|---|---|---|---|---|---|
| 433 MHz, 10 mW e.r.p. (26a) | 10.5 dBm | −106.7 dBm | **18.8 dB** | 14.5 dB | licence-exempt, ≤ 10 % duty |
| same, SF9/125 | 10.5 dBm | −106.7 dBm | 26.8 dB | 22.5 dB | (air time too long for flight) |
| 433 MHz, 1 mW e.r.p. (26b) | 0.5 dBm | −116.7 dBm | 8.8 dB | 4.5 dB | licence-exempt, no duty limit |
| 433 MHz, E22 33 dBm | 33 dBm | −84.2 dBm | **41.3 dB** | 37.0 dB | amateur licence + IMDA consent / permit / abroad |
| same, SF7/500 | 33 dBm | −84.2 dBm | 36.8 dB | 32.5 dB | " |
| 868.125 MHz, E220 24 dBm (sub-band 29) | 24 dBm | −97.2 dBm | **28.2 dB** | 24.0 dB | licence-exempt, 500 mW e.r.p. |
| 920.125 MHz, E220 21 dBm (lowest step) + 1 dB pad (30c) | 20 dBm after the pad | −101.7 dBm | 23.7 dB | 19.4 dB | 100 mW e.r.p., **1 % duty** |
| 905 MHz IREC Mode A, 30 dBm SF7/500 | 30 dBm | −91.6 dBm | 29.4 dB | 25.1 dB | Part 15 DTS, TX antenna ≤ 6 dBi |
| 920 MHz, 30 dBm under a temporary permit | 30 dBm | −91.7 dBm | 33.7 dB | 29.4 dB | IMDA permit |

Compare these with the margin allocation of [link margin & availability](../09-propagation-link-budget/link-margin-availability.md) (≈ 10–20 dB statistical reserve after deterministic losses): every licensed or 868 MHz case is comfortable; 433 MHz at 10 mW is adequate *only with the LNA chain and CP*; 1 mW is not a flight option.

### 4. Along the trajectory (station C, 5 km cross-range)
| t | Altitude | Range | Look angle | $G_t$ | 433 MHz 33 dBm | 433 MHz 10 mW e.r.p. | 868 MHz 24 dBm |
|---|---|---|---|---|---|---|---|
| 2 s | 207 m | 5.0 km | 88° | +2.1 dBi | −58.5 dBm | −81.0 dBm | −71.6 dBm |
| 10 s | 4.2 km | 6.6 km | 50° | −1.1 dBi | −64.1 dBm | −86.6 dBm | −77.2 dBm |
| 20 s | 7.6 km | 9.2 km | 33° | −4.6 dBi | −70.5 dBm | −93.0 dBm | −83.5 dBm |
| 30 s | 9.4 km | 10.7 km | 29° | −5.7 dBi | −73.0 dBm | −95.5 dBm | −86.0 dBm |
| apogee | 10.0 km | 11.3 km | 66° | +1.1 dBi | −66.7 dBm | −89.2 dBm | −79.7 dBm |
| **minimum ascent margin** | | | | | **52.4 dB** | **29.9 dB** | **39.4 dB** |

From station A (2 km) the minima are 47.0 / 24.5 / 34.0 dB (at look angle 13.7°); from station B (5 km up-range) 37.3 / **14.8** / 24.3 dB — with the null floored at −20 dBi, i.e. probably optimistic. The station choice is worth ≈ 15 dB, more than the difference between 10 mW and 100 mW.

### 5. Landed rocket
Assumptions (audit item #9 — every landed-range number depends on them): **two-ray plane-earth model** $L \approx 40\log d - 20\log(h_th_r)$ beyond the breakpoint, **rocket antenna 0.2 m above ground, 0 dBi**, station mast 2 m or 6 m, ground antenna 10 dBi, **−3 dB polarisation, −10 dB terrain/fade allowance** (13 dB total margin), **SF9/125 (SF11/125 where stated)**, conducted power as listed with 0.5 dB rocket feed, **masthead-LNA chain NF 2.0 dB** (kT0 = −174 dBm/Hz, sensitivity −174 + 10 log BW + NF + SNR_req):

| Link | 2 m mast | 6 m mast |
|---|---|---|
| 433 MHz 33 dBm SF9/125 | 7.5 km | 13.0 km |
| 433 MHz 33 dBm SF11/125 (LDRO, SX1268 only) | 10.0 km | 17.4 km |
| 433 MHz 10 mW e.r.p. SF9/125 | 2.1 km | 3.6 km |
| 433 MHz 10 mW e.r.p. SF11/125 | 2.7 km | 4.8 km |
| 868 MHz 24 dBm SF9/125 (LLCC68 floor) | 4.5 km | 7.8 km |
| *cross-check, bare module (NF 6 dB + 1 dB cable), EIRP at the limit, 13 dB margin, as in [LoRa sensitivity](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md):* 433 MHz 2 W / 10 mW e.r.p., SF9/125 | 5.6 / **1.7 km** | — |

Requirement R5 (≥ 3 km with a 6 m mast) is met by every case; at 10 mW e.r.p. only with the mast and the masthead LNA (3.6 km) — a 2 m tripod gives 2.1 km, and a bare module on a 2 m tripod only 1.7 km (the domain-15 figure; the 0.4 km difference is the LNA's ≈ 5 dB of noise figure partly offset by this recipe's 2.15 dB lower EIRP assumption). Real terrain is worse than flat earth ([two-ray](../09-propagation-link-budget/two-ray-ground-reflection.md), [empirical models](../09-propagation-link-budget/empirical-path-loss-models.md)); transmit the last fix repeatedly *during descent* and walk the last kilometres with a handheld 3-element Yagi.

### 6. Dual-band frequency plan
- **Channel edges, not centres, must be inside the band**: 433.05–434.79 MHz holds a 250 kHz LoRa channel only between 433.175 and 434.665 MHz centres — CH 24 (434.125 MHz) works, CH 23 (433.125 MHz) does not (its lower edge is 433.000 MHz); at 125 kHz both work. The pre-flight tool flags this automatically.
- E22 2nd harmonic of 433.125 MHz = 866.250 MHz (of 434.125 MHz = 868.250 MHz). Against E220 channels: CH16 866.125 MHz is **0.125 MHz away — inside a 250 kHz LoRa channel**; CH17 (867.125) is 0.875 MHz away; **CH18 (868.125) is 1.875 MHz away → use CH18 with a 433.125 MHz primary; with a 434.125 MHz primary use CH17 (867.125 MHz, 1.125 MHz from 868.25 MHz)**. EBYTE channels step in 1 MHz, so the valid Singapore pairs are **(433.125 MHz at ≤ 125 kHz, CH18 868.125 MHz)** or **(434.125 MHz at 250 kHz, CH17 867.125 MHz)**; verify the harmonic offset on a spectrum analyser.
- Singapore requires spurious ≤ −36 dBm below 1 GHz, ≤ −30 dBm above ([IMDA](../19-regulations-safety/singapore-imda-rules.md)): at 33 dBm that is ≥ 69 dBc on the 2nd harmonic — measure it; the E22 datasheet does not state harmonics. A low-pass filter design for this is in [bandpass-filter-design-walkthrough](bandpass-filter-design-walkthrough.md).
- **E22 channel choice vs GNSS (3rd harmonic).** With $f$ = 410.125 + CH MHz, the 3rd harmonic of **CH 0–2 lands in GPS L2 (1217.4–1237.8 MHz) and CH 4–6 in GLONASS L2 (1242.4–1249.1 MHz)** — both tracked by the ZED-F9P; CH 3 sits between them, inside any L2 front-end filter. (Domain 21 states the same physics as CH 0–3 → GPS L2 allocation, CH 5–6 → GLONASS L2 with CH 4 on its edge, CH 7–9 on the F9P filter skirts: the KB avoid-list is **CH 0–9**.) **CH 10–22 (420.125–432.125 MHz) put 3f in Galileo E6 / BeiDou B3I** (1258–1299 MHz; not tracked by the ZED-F9P, tracked by triple-band receivers). CH 23 = 433.125 MHz → 1299.375 MHz, 0.17 MHz above the E6 main-lobe edge. A legal −30 dBm harmonic coupled at −20 dB into the onboard GNSS antenna is still a −50 dBm in-band CW jammer against −130 dBm satellites, so **regulatory compliance is not coexistence**: keep 3f out of every GNSS band the onboard receiver uses (use CH 24 = 434.125 MHz: CH ≥ 23 keeps 3f out of the F9P bands, CH ≥ 24 out of the whole RNSS allocation; above 437 MHz is cleaner still if the venue allows) and filter (finding by W5-E1; `proj_lora_link.py` §10 lists every channel). The E220's 2nd/3rd harmonics (1700–1860 / 2550–2790 MHz) hit no GNSS band.
- No intermodulation product of order ≤ 5 between 433.125 MHz and 868/905/920 MHz lands within 157 MHz of GNSS L1 (1575.42 MHz); the remaining GNSS threats are blocking/desense by the fundamentals and transmitter wideband noise, handled in [gnss-front-end-design](gnss-front-end-design.md).
- Onboard, both radios only transmit (R9), so mutual *desense* is not a flight issue; it is a ground issue only if a ground transmitter exists (e.g. the RTK-corrections bridge).

### 7. Range test by the attenuator method (Singapore-legal)
Why not conducted? From 24 dBm down to the module's −121.5 dBm (SF7/250) needs 145.5 dB of attenuation, and the leakage around the attenuators must be ≥ 20 dB below that — ≥ 165 dB isolation, impossible with hobby enclosures. So:
1. **Legal radiated power.** E22 at its lowest step (24 dBm) → **≥ 13.5 dB pad** (0.25 W rating, use a 1–2 W part) → dipole: ≤ 10 mW e.r.p. At 33 dBm the pad must be ≥ 22.5 dB and dissipate 2 W.
2. **Path.** 1–2 km, clear line of sight, both antennas high enough for 60 % first-Fresnel clearance at mid-path (7.9 m at 1 km, 11.2 m at 2 km, 433 MHz) — e.g. between two rooftops or across open water. **Measure the path**: log RSSI (or tinySA channel power) at 0 dB attenuation; do not assume free space.
3. **Shielded receiver.** Ground chain in a metal box on its own battery, step attenuator (0–70 dB, 1 dB steps) on a bulkhead between antenna cable and receiver, logging to SD/serial-over-fibre. **Validity check before every run: replace the antenna cable with a 50 Ω load; zero packets must be received.** The box needs ≥ 69 dB isolation at 1 km (≥ 63 dB at 2 km).
4. **Equivalent-range point.** Insert $A_{eq} = 20\log(15\,\mathrm{km}/d) + 16$ dB (null) = 39.7 dB at 1 km. Pass: PER < 1 % over ≥ 300 packets.
5. **Find the edge.** Step up until PER = 1 % → $A_{fail}$. Predicted $A_{fail} = P_{rx}(0\,\mathrm{dB}) - S$ = 59.5 dB (SF7/250) / 67.5 dB (SF9/125) at 1 km if the path is free-space; with the *measured* $P_{rx}$ the prediction is $P_{rx,meas} + 125.5$ dB (SF7/250).
6. With an SX126x receiver (Option B), the **SNR method** avoids going to failure: margin = SNR$_{meas}$ − SNR$_{req}$(SF), valid when SNR$_{meas}$ is below about +5 dB (LoRa SNR saturates at high signal).
The method and its statistics (≥ 62 packets for ±0.5 dB at σ = 2 dB) are in [antenna range & OTA testing](../17-test-measurement/antenna-range-ota-testing.md).

## Part selection
Prices: LCSC unit price for qty 1–9 from the JLCPCB parts database snapshot of 2026-07-08 (USD), unless marked "est." (estimate — check before ordering). Part-family context: [transceiver ICs](../18-components-parts/rf-transceiver-ics.md), [LNA/PA MMICs](../18-components-parts/lna-pa-gain-block-mmics.md), [modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md).

| Function | Part | Key specs | Price | Notes |
|---|---|---|---|---|
| Primary TX (current) | EBYTE E22-400T33D | SX1268, 33 dBm, UART, SMA | $17.08 (C5124403) | min step 24 dBm → pad for SG tests |
| Primary TX (next, licensed) | EBYTE E22-400M33S | SX1268 + PA/LNA, 33.5 dBm, SPI | $10.01 (C5352927) | RadioLib; check RF-switch pins and PA drive level |
| Primary TX (next, SG-legal) | EBYTE E22-400M22S | SX1268, 22 dBm, SPI | $4.62 (C411291) | set 10 dBm exactly in firmware |
| Secondary TX (current) | EBYTE E220-900T30D | LLCC68, 30 dBm, UART, needs ≥ 5 V | $8.92 (C970288) | CH18 (with a 433.125 MHz primary) or CH17 (with 434.125 MHz), ≤ 24 dBm in SG |
| Secondary TX (next) | EBYTE E22-900M30S (SX1262) or E220-900M30S (LLCC68) | 30 dBm SPI | $6.82 (C411294) / $5.88 (C2965511) | prefer SX1262: SF10–12, LDRO for landed mode |
| Rocket antennas | λ/2 sleeve dipoles in fibreglass nose/coupler; λ/4 over bulkhead | axial, linear | est. $5–15 each (DIY) | [antennas on rockets](../08-antennas/antennas-on-rockets.md) |
| Rocket feed | U.FL/IPEX-to-SMA pigtail with retention, or RG-316 | 0.2–0.5 dB | est. $2–5 | ferrite choke at antenna base |
| Ground LNA | Qorvo TQP3M9036 (433/915) | NF 0.45 dB, 19.8 dB, OIP3 +36 dBm | ≈ $2.8 (C920261, via 18 page) | on a small bias-tee board at the mast |
| Ground antenna | crossed 6-el Yagi (433), crossed 8–11 el (868/905) | 10 / 12 dBic CP | est. $30–60 DIY | [ground-station recipe](ground-station-tracking-yagi.md) |
| Ground receivers | same UART module (compatibility) + SX1262/SX1268 dev board (SNR/FEI) + RTL-SDR Blog V3/V4L (IQ; V4 is end of line) | — | est. $10 + $20 + $40 | splitter after the LNA |
| Test | NanoVNA-H4, tinySA Ultra, 1–2 W SMA pads (10/20 dB), step attenuator 0–70 dB, 50 Ω loads | — | est. $70 + $130 + $40 + $60 | [NanoVNA](../17-test-measurement/nanovna-librevna-practical.md), [spectrum analyzers](../17-test-measurement/spectrum-analyzers.md) |

## Block diagram
```
ROCKET (primary FC)                                  ROCKET (secondary FC)
 ESP32-S3 --UART/SPI--> E22-400 (SX1268+PA) --LPF?--> sleeve dipole 433 (nose cone)
 5 V buck (>=2 A, bulk C) ------^                     ESP32-S3 --> E220/E22-900 --> sleeve dipole 868/905 (coupler)
 flight log: every queued frame + radio config        5 V buck-boost (>=1.5 A) ------^

GROUND STATION (x2 sites, cross-range 3-5 km, different azimuths)
 crossed Yagi (CP, 433) -> [limiter] -> LNA -> SAW -> 15 m LMR-240 -> 4-way splitter -+-> E22 UART rx  -> laptop log
                             ^ bias-tee DC (5 V)                                     +-> SX1268 dev board (SNR, FEI)
                                                                                     +-> RTL-SDR (IQ 1 MS/s -> disk)
                                                                                     +-> spare / tinySA
 crossed Yagi (CP, 868/905) -> same chain for the secondary link
 GNSS receiver (PPS) -> timestamps for every packet; tablet: az/el from downlinked GNSS
```

## Layout notes
- Module supply: 0 → 1.2 A steps in µs; ≥ 2 A regulator, low-ESR bulk at the module pins, short wide return; keep the module's return current out of the sensor/ADC ground ([grounding & return paths](../13-pcb-rf-layout-emc/grounding-and-return-paths.md), [power supplies for RF](../05-analog-electronics/power-supplies-for-rf-and-analog.md)). Brown-out mid-packet looks exactly like an RF dropout — Avionics B's lesson on sensors sharing a noisy regulator applies.
- SPI modules: 50 Ω CPWG from the module pad to the U.FL/SMA, stitched ground vias, no signals under the module ([stackups](../13-pcb-rf-layout-emc/stackups-and-materials.md), [RF layout rules](../13-pcb-rf-layout-emc/rf-layout-rules.md)); leave a π-network footprint (0 Ω + two DNP shunts) for a harmonic LPF or antenna match.
- Thermal: a 2 W module dissipates ≈ 4 W while transmitting; at 50 % occupancy that is 2 W average in a closed bay — conduct it to the airframe/bulkhead and keep the crystal/TCXO of other radios away ([thermal management](../13-pcb-rf-layout-emc/thermal-management-rf.md)).
- Antennas: 433 and 900 MHz antennas at opposite ends of the avionics bay (≥ λ/2 = 35 cm apart), GNSS antenna as far as possible from both, coax routed along the axis with a choke at each antenna ([antenna matching & baluns](../08-antennas/antenna-matching-and-baluns.md)).

## Simulation plan
| What | Tool | Output | Pass criterion |
|---|---|---|---|
| Trajectory, Doppler, air time, budgets | `proj_lora_link.py` (this page) with the team's 6-DOF trajectory replacing the point mass | tables above | drift-loss % ≤ R4 for the chosen setting |
| Rocket antenna in the airframe | NEC-2 (wire model of dipole + body) or openEMS (dipole in fibreglass tube with bulkheads, battery, threaded rods) ([NEC](../16-simulation-tools/nec-antenna-modelling.md), [openEMS](../16-simulation-tools/openems-workflow.md)) | S11 shift, pattern incl. null depth | resonance shift and null depth replace the −20 dBi assumption |
| LoRa demodulator under drift | `tools/verify/lora_css_sim.py` style Monte-Carlo with the recorded Doppler profile | PER vs time | agrees with the Semtech-rule table within a factor 2 in loss % |
| Ground chain cascade incl. IIP3 | `rfcalc.noise.cascade` | NF, IIP3 | NF ≤ 2 dB, input P1dB > −10 dBm at pad distance |

Independent validation (team tenet 1): cross-check the trajectory against RocketPy/OpenRocket, the budgets against [link budget methodology](../09-propagation-link-budget/link-budget-methodology.md) example A, and the air time against Semtech's LoRa calculator.

## Build, bring-up and test plan (pass/fail fixed in advance)
| # | Test | Method | Pass |
|---|---|---|---|
| T1 | Module identity & config | read registers, log board ID, air rate, channel, power; LBT off, CRYPT off | config line printed at boot matches the flight plan |
| T2 | Air-rate mapping | SDR waterfall + gr-lora_sdr on each EBYTE air rate ([modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md), [SDR recipe](sdr-receiver-build.md)) | SF, BW, CR, preamble, sync word identified for 2.4k/4.8k/9.6k/19.2k; recorded in the KB |
| T3 | Conducted power & harmonics | module → 40 dB (≥ 5 W) attenuator → tinySA/power meter ([RF power](../17-test-measurement/rf-power-measurement.md)) | power within ±1 dB of setting; 2nd/3rd harmonic ≤ −36/−30 dBm-equivalent at the antenna |
| T4 | Occupied bandwidth (IREC Mode A) | analyser 6 dB BW | ≥ 500 kHz |
| T5 | Supply droop | 0.1 Ω shunt, scope during a packet | droop < 5 %; no AUX stuck low over 1000 packets |
| T6 | Installed antenna match | NanoVNA through the flight coax, assembled airframe, battery & harness in ([NanoVNA](../17-test-measurement/nanovna-librevna-practical.md)) | |S11| ≤ −10 dB across the channel after trimming; record length |
| T7 | Ground chain NF | Y-factor with a noise source or sky/terrain comparison ([NF measurement](../17-test-measurement/noise-figure-measurement.md)) | ≤ 2.5 dB (prediction 2.0 dB) |
| T8 | Range test | method in example 7 | P3 (below) |
| T9 | Roll test | rocket section on a turntable at flight roll rate, 100+ m, attenuated; linear vs CP ground antenna | CP: RSSI ripple ≤ 3 dB; linear: nulls observed (validates the choice) |
| T10 | Pad-to-flight rehearsal | full stack on battery, 1 h pad wait at the flight schedule | no resets, thermal steady, loss counters clean against end-of-run frame count |
| T11 | Pyro/RF interaction (HERO) | each e-match replaced by a same-resistance dummy with a thermocouple or low-level current sensor; avionics bay fully wired in the airframe; each radio transmits **continuously at maximum power** on each flight channel, with pyro channels disarmed, then armed-not-firing ([lab safety, worked example 3](../19-regulations-safety/lab-safety-esd-high-power.md#worked-examples)). Radiating at full power needs a screened enclosure or a licence/permit in Singapore | induced bridgewire current ≤ 15 % of the e-match no-fire current (**≥ 16.5 dB below MNFS**, MIL-STD-464C) in every configuration; no FET gate or continuity-sense line changes state |

Bring-up discipline follows the team's HIL/bench methods: capture from reset, grep every warning then check what is *missing*, count drops as well as losses, 22/22 battery power-ups before flight.

## Regulatory check
- **Singapore (tests):** 433.05–434.79 MHz: ≤ 10 mW e.r.p. with ≤ 10 % duty (26a) or ≤ 1 mW with none (26b) — the whole occupied channel must lie inside the band (use 434.125 MHz for 250 kHz); a schedule that fits 10 % duty is one 48-byte frame at 2 Hz (SF7/250, 9.8 %); the E22-400T33D is non-exempt at any of its power steps and its user-adjustable power is itself a TS SRD §4.1(b) concern — use it only through a legal pad for tests, or under an amateur licence with IMDA consent, a temporary permit or an experimental licence. 866–869 MHz: ≤ 500 mW e.r.p., no duty stated (band under refarm review). 917–925 MHz LoRa: ≤ 100 mW, ≤ 1 % → not usable for 10 Hz telemetry. The E220's default 873.125 MHz is outside both bands. Full text and margins: [Singapore IMDA rules](../19-regulations-safety/singapore-imda-rules.md), [amateur licensing](../19-regulations-safety/amateur-radio-licensing.md).
- **Duty-cycle window:** TS SRD defines none. Averaged over one hour (the ETSI convention), a 10-minute flight at 25 % (SF7/500) plus a 50-minute pad wait at 3 % averages 6.8 %; at SF7/250 it averages 13.6 %. Treat the 1-hour reading as an *interpretation* and ask IMDA in writing before relying on it.
- **IREC/Spaceport America:** 902.0–909.0 MHz Mode A (BW ≥ 500 kHz, no hopping, ≤ 1 W, ≤ 6 dBi) for the E220 — SF7/500 fits the Doppler table; 70 cm SRAD needs a US-licensed operator, ≤ 125 kHz and ≤ 200 mW unless ESRA approves more ([competitions](../19-regulations-safety/international-rules-for-competitions.md)). Record conducted power, 6 dB bandwidth and harmonics before travelling.
- **RF exposure:** 2 W at 433 MHz near people on the pad — check the safe distance in [RF exposure safety](../19-regulations-safety/rf-exposure-safety.md).

## Pre-registered predictions
Write these into a dated, write-once file in the flight repo *before* T7/T8 and the flight; later changes go in an addendum (team tenet 2).

| ID | Prediction | Tolerance | If outside tolerance, it means… |
|---|---|---|---|
| P1 | Ground chain NF (LNA→SAW→15 m LMR-240→splitter→module) = 2.0 dB | ±0.5 dB | cable/SAW loss or LNA NF differs from datasheet; recompute budgets |
| P2 | Chain sensitivity at 1 % PER: SF7/250 −125.5 dBm; SF9/125 −133.5 dBm (290 K source) | ±2 dB | module NF ≠ 6 dB (EBYTE LNA helps or hurts) or wrong SF/BW mapping |
| P3 | 1 km radiated test at 10 mW e.r.p.: PER < 1 % with 39.7 dB inserted; $A_{fail} = P_{rx,meas} + 125.5$ dB (SF7/250) | ±3 dB | leakage (check the load test) or P2 failure |
| P4 | Flight, station C, primary at 33 dBm SF7/250: median RSSI near apogee −67 dBm; ascent minimum ≈ −73 dBm around t ≈ 30 s | ±6 dB | antenna installed gain/null depth differs from the axial-dipole model |
| P5 | Ascent packet loss (SF7/250 both bands, station C) < 2 %, losses not concentrated in the burn | — | a non-RF cause (power, UART, antenna connector under vibration) |
| P6 | Measured carrier offset (SX126x FEI or SDR) follows $-\dot r f_c/c$ from GNSS: peak 0.48 kHz at 433 MHz from station C, after removing the static crystal offset | ±50 Hz | GNSS/radio time alignment or oscillator drift under PA heating |
| P7 | If any link is flown at SF9/125 at 868–905 MHz, packets straddling the burn and the first seconds of coast are lost at 1–10 % (C: ≈ 1.4 %; A: ≈ 7.6 %), none at 433 MHz | factor 2 | the Semtech rule is conservative/optimistic for LLCC68 — a useful KB result either way |
| P8 | Landed reception, 433 MHz 33 dBm SF9/125, 2 m mast: up to ≈ 7.5 km over flat ground | terrain-dependent (−50 %/+0 %) | terrain/vegetation loss larger than the 10 dB allowance |
| P9 | Installed sleeve dipole resonates 2–5 % low before trimming. *Simulation-informed context (openEMS, [openEMS workflow Run 3](../16-simulation-tools/openems-workflow.md), 2026-10-13; to be measured):* a 433 MHz λ/4 whip inside a 3 mm G10 ogive shifts −2.8 % from the cone alone (−1.2 % at 915 MHz), and a conductive av-bay counterpoise moves it +3.4 %, so the net installed shift depends on the ground system; P9 is kept unchanged | ±2 % | airframe/battery coupling stronger than expected |
| P10 | No dropouts attributable to plume (all stations ≥ 2 km see look angles > 22° during the burn) | — | plume attenuation at larger angles than 22°, or a different mechanism |

## Risks and common failure modes
| Risk | Likelihood / impact | Mitigation |
|---|---|---|
| Wrong/unknown EBYTE air-rate mapping → high-SF mode at 900 MHz loses boost packets | high / medium | T2; fly ≥ 9.6k; Option B radios |
| Tail-null blackout near apogee with a close or up-range station | high / high | stations cross-range 3–5 km on two azimuths; turnstile in the nose if the station must be close |
| Linear–linear roll fades | high / medium | CP ground antennas (T9) |
| Receiver/LNA overload or damage on the pad | medium / high | ≥ 100 m or 20–40 dB in-line attenuator/limiter during pad checks |
| Harmonic of E22 in the secondary channel | medium / medium | channel pairs (433.125, CH18) or (434.125, CH17), never CH16; LPF; T3; `proj_preflight_rf.py` |
| Brown-out during TX bursts | medium / high | T5; ≥ 2 A supply; bulk capacitance |
| Detuned antenna in the airframe | high / medium | T6 in the flight configuration |
| Carbon-fibre or foil in front of an antenna | low / catastrophic | RF window; handheld-radio check through the tube |
| Illegal emission during tests | medium / legal | pads, 10 mW e.r.p., duty logs, licence/permit for full power |
| Ground logging silently recording nothing (port grabbed by another process) | medium / high | dashboard tails the log file; capture-from-reset checklist |
| Landed rocket unheard behind terrain | high / high | mast, repeated last fix during descent, handheld Yagi, second link |

## Cost estimate
| Item | Qty | Cost (USD) |
|---|---|---|
| Flight radios (E22-400M33S + E22-900M30S, or the current UART modules) | 1 set + 1 spare | ≈ 35–55 |
| Rocket antennas, pigtails, chokes, fibreglass window work | — | ≈ 30 |
| Ground: two crossed Yagis (DIY aluminium/PVC) | 2 | ≈ 60–120 |
| Ground: LNA/SAW/bias-tee boards (JLC-assembled), limiter, coax (LMR-240), splitters | 2 chains | ≈ 80–150 |
| Ground receivers: module + SX126x dev board + RTL-SDR Blog V3/V4L per band | 2 bands | ≈ 140 |
| GNSS/PPS timing receiver, tablet/laptop (existing) | — | ≈ 20 |
| Test: NanoVNA-H4, tinySA Ultra, pads, step attenuator, loads, shielded box | once | ≈ 300 |
| **Total (excluding laptops)** | | **≈ 650–800** |
Estimates except the LCSC module prices; add IMDA fees if licensed (amateur exam S$20–40 + licence S$50–100 / 5 yr; temporary permit S$150–275 per campaign — [IMDA](../19-regulations-safety/singapore-imda-rules.md)).

## Practical notes
- Put the **radio configuration in every health frame and in the boot CONFIG line** of the flight log (the log is the evidence of legal settings and of what actually flew).
- Ground stations timestamp with GNSS PPS so two stations and the flight log align; de-duplicate by source + sequence counter; compute loss against the end-of-flight frame count.
- Record IQ at both stations for the whole flight (≈ 3.6 GB per 30 min at 1 MS/s 8-bit) — it is the only way to analyse packets the modules missed ([ground station design](../15-lora-ism-radios/ground-station-design.md)).
- Survey the site for an hour before launch day with the SDR: 433 MHz key fobs and 920 MHz LoRaWAN raise the effective noise floor.
- If the venue forces 125 kHz at 433 MHz, SF7/125 with state decimated to 5 Hz is the only fit; the Doppler table says it is safe.

## Common mistakes & misconceptions
- **"We need SF12 for 15 km."** At 15 km in LOS even SF7/500 has ≥ 23 dB of margin at 868 MHz legal power; SF12 loses 7–31 % of boost packets and cannot carry 10 Hz.
- **"Put the station right next to the pad to be close."** Closeness puts the tail null on you near apogee, raises Doppler rate by LOS rotation and overloads the receiver on the pad.
- **"The default EBYTE settings worked on the bench, so they'll work in flight."** The bench has no acceleration; the default 2.4k rate is marginal at 433 MHz and fails at 900 MHz during boost.
- **"A 10 % duty limit means 10 Hz telemetry is fine at a short frame."** A 48-byte LoRa frame at SF7/250 is 49 ms: 10 % allows only 2 Hz.
- **"Conducted test with a pile of attenuators proves sensitivity."** Leakage around the pads dominates beyond ≈ 80–100 dB; do the load-terminated leakage check.
- **"The harmonic doesn't matter because the second radio is on another band."** 2 × 433.125 = 866.25 MHz lands on E220 CH16.
- **"Ground tests at 1.5 m height show the range."** Two-ray loss makes ground-level tests 30–50 dB pessimistic for flight ([OTA testing](../17-test-measurement/antenna-range-ota-testing.md)).

## How to simulate / verify
- `python3 tools/verify/proj_lora_link.py` — sections 1–10 reproduce every number on this page; edit `ROCKET`, `STATIONS` and the config tables for your vehicle.
- Supporting scripts: `tools/verify/lora_toa.py`, `lora_doppler.py`, `lora_link_budget.py`, `lora_ground_station.py`, `ant_rocket.py`, `reg_erp_compliance.py`; calculator package `tools/rfcalc` (`python3 -m rfcalc lora …`).
- After flight: plot per-packet RSSI/SNR/FEI against flight time, look angle (from GNSS + attitude), IMU acceleration and station; score P1–P10.

## Open questions / gaps
- EBYTE air-rate → SF/BW/CR mapping still unmeasured (T2 will close it).
- No measured LoRa PER-vs-acceleration data from a real rocket in the KB; P7 is designed to produce it.
- E22-400T22D/S power steps (reported as 22/17/13/10 dBm in secondary sources) not verified from the EBYTE manual.
- Whether IMDA reads the 26a 10 % duty over an hour or per transmission; whether rocket telemetry qualifies as sub-band 29 "data acquisition" — ask IMDA.
- Null depth of an installed rocket dipole (simulation plan row 2).
- TCXO vs crystal in E22-400M33S (EBYTE says "high-precision 32 MHz crystal") — measure FEI vs temperature during T10.

## Sources
1. This KB, [Rocket telemetry radio design](../15-lora-ism-radios/rocket-telemetry-radio-design.md) — frame layout, phase plan, uplink policy, flown examples. (internal)
2. This KB, [LoRa sensitivity & link budget](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md) — sensitivity equation, SNR table, implied NF, landed two-ray range. (internal)
3. This KB, [LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md) — Semtech per-packet drift rule BW/(3·2^SF), ×16 LDRO; Norby zenith-rate failures. (internal)
4. This KB, [LoRa modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md) — E22/E220 registers, air-rate candidates, channel formulae, supply notes. (internal)
5. This KB, [Antennas on rockets](../08-antennas/antennas-on-rockets.md) — axial nulls, plume cone (Kinefuchi et al. 2015), CP ground antennas. (internal)
6. This KB, [Singapore IMDA rules](../19-regulations-safety/singapore-imda-rules.md) and [competition rules](../19-regulations-safety/international-rules-for-competitions.md) — power/duty limits, IREC Mode A. (internal; primary sources cited there)
7. This KB, [Link margin & availability](../09-propagation-link-budget/link-margin-availability.md), [two-ray](../09-propagation-link-budget/two-ray-ground-reflection.md), [OTA testing](../17-test-measurement/antenna-range-ota-testing.md). (internal)
8. Semtech, *SX1261/2 Datasheet* Rev 1.2 (2019), §4.1.2 drift rule, sensitivity tables, TX power vs VBAT. (datasheet — via [3])
9. Semtech, *SX1276/77/78/79 Datasheet* Rev 7 (2020) / AN1200.13 — time-on-air formula. (datasheet — via `tools/rfcalc/lora.py`)
10. EBYTE, E22-400M33S product page (cdebyte.com, accessed 2026-09-29) — SX1268, 410–493 MHz, 33 dBm, SPI, 32 MHz crystal. https://www.cdebyte.com/products/E22-400M33S (vendor)
11. JLCPCB/LCSC parts database snapshot 2026-07-08 (local `jlcpcb-components.sqlite3`) — prices and stock of E22/E220 modules. (distributor data)
12. ITU-R P.372 man-made noise at 425 MHz — via [thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md). (standard)
13. Space Bar avionics knowledge base (user's own notes) — Avionics B (E22-400T33D, 2S) and C (E220-900T30D, 1S, 5 V buck-boost), downlink-only design, record-everything and pre-registration tenets, HIL/bench log discipline. (internal, user-provided)
