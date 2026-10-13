---
title: LoRa ground-station design for rocket telemetry — antennas, LNA/filter chain, tracking, diversity, SDR recording
domain: 15-lora-ism-radios
slug: ground-station-design
tags: [ground-station, link-asymmetry, uplink, overload, lorawan-txpower, unused-port, yagi, helix, lna, saw-filter, tracking, rotator, diversity, sdr, gr-lora_sdr, fresnel, logging, rocket]
prerequisites:
  - lora-sensitivity-and-link-budget.md
  - ../07-noise-linearity/noise-figure-and-friis.md
  - ../08-antennas/yagi-uda-and-log-periodic.md
related:
  - rocket-telemetry-radio-design.md
  - lora-impairments-doppler-drift-timing.md
  - lora-modules-ebyte-rfm-heltec.md
  - ../08-antennas/helical-antennas.md
  - ../08-antennas/antenna-polarization-and-circular-polarization.md
  - ../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md
  - ../06-rf-circuits/lna-design.md
  - ../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md
  - ../14-sdr-dsp/sdr-hardware-survey.md
  - ../14-sdr-dsp/gnu-radio-and-software-stack.md
  - ../20-projects-recipes/ground-station-tracking-yagi.md
  - ../19-regulations-safety/rf-exposure-safety.md
  - ../19-regulations-safety/lab-safety-esd-high-power.md
  - ../19-regulations-safety/singapore-imda-rules.md
level: intermediate
confidence: medium
last_updated: 2026-10-14
---

# LoRa ground-station design for rocket telemetry

## Questions this page answers
- Should my ground station use an omni, a Yagi or a helix?
- Where do the LNA and the SAW filter go, and in which order?
- How much does coax loss before the receiver cost me?
- How fast must I track the rocket, and can I do it by hand?
- Is it worth running two receivers (diversity)?
- How do I record the raw LoRa signal with an SDR and decode it later?
- How high must my antenna be for a ground-to-ground or post-landing link?
- What should the ground station log so a flight can be analysed afterwards?
- Why might a 923 MHz receiver in Singapore be desensitised by nearby cellular sites?
- Why does my ground station hear the rocket but the rocket never hears my uplink (or the ACK)?
- Will a louder 1 W node fix my LoRa mesh?
- Why does my receiver stop working when the transmitter is right next to it?
- What does LoRaWAN "TXPower 3" mean in dBm at the antenna port?
- What do I do with the RF port I'm not using?

## TL;DR
- **In flight** the budget is ample ([link budget](lora-sensitivity-and-link-budget.md)); the ground station's job is to avoid **nulls** (polarisation, pattern), **overload** near the pad and **interference**, and to **record everything**. **After landing** the station's antenna **height** and gain decide whether you still hear the rocket (two-ray: every doubling of height ≈ +6 dB).
- **Antenna**: a vertically mounted Yagi (≈ 8.5 dBi for a directly fed 3-element up to ≈ 11 dBi for 6 elements at 433 MHz; 11-element DL6WU ≈ 14 dBi on 1.7 m [1]) or a **crossed Yagi / helix for circular polarisation** (constant −3 dB against a rolling linear rocket antenna, no roll nulls [2]). A 50–70° beam is easy to hand-track (10° error ≈ 0.5 dB loss for a 50° beam; `lora_ground_station.py`).
- **Receive chain** (Friis, `lora_ground_station.py`): module + 5 dB of coax = NF 11 dB; masthead LNA (0.8 dB, 18 dB gain) *then* SAW then coax = **NF 1.8 dB**; SAW *before* the LNA = 3.4 dB. Put the LNA at the antenna; put the filter first only if strong out-of-band signals would overload the LNA.
- **Singapore 923 MHz caveat**: the 917–925 MHz SRD band sits next to 3GPP band 8 cellular downlink (925–960 MHz) — nearby base stations can overload a wideband LNA; a steep filter (SAW/cavity) ahead of the LNA may be necessary despite its NF cost. 433 MHz has no comparable neighbour but has many SRD users.
- **Tracking**: elevation rate peaks at $v/D$: 300 m/s rocket, station 2 km away → 8.6 °/s; 1 km → 17 °/s. Hand tracking with GNSS-derived azimuth/elevation (as Featherweight's app does [3]) works for 50–70° beams; rotators must be checked against these rates.
- **Diversity**: two independent receivers (different positions/polarisations/bands) turn packet loss $p$ into $p^2$ (10 % → 1 %). De-duplicate by source ID + sequence counter.
- **SDR recording**: 1 MS/s 8-bit IQ = 2 MB/s = 7.2 GB/h; record the whole flight and decode offline with **gr-lora_sdr** [4]; you get carrier frequency (Doppler/drift), SNR and interference history even for packets the module missed.
- **Near pad**: 2 W at 1 m → +17 dBm at the receiver (above EBYTE's 10 dBm damage rating, and at the +17 dBm CW limit of a typical pHEMT LNA such as the PSA4-5043+ [9]); keep ≥ 30–100 m or use a 20–40 dB attenuator/limiter.
- **Links are asymmetric** ([section](#link-asymmetry-and-receiver-overload-near-the-pad)). Under an e.r.p. cap both ends radiate the same, but only the ground station adds a 12 dBi Yagi and a 1.8 dB-NF masthead LNA *on receive*. The rocket hears the uplink ≈ **17.5 dB worse** than the station hears the downlink (licence-exempt case; 11.5 dB in the licensed case where the station steps down to 30 dBm to stay under 10 W ERP). Any two-way exchange (ACK, command, mesh hop) closes only if the **weaker** direction closes, so a louder node fixes only the direction it transmits in.
- **Any ground transmitter is regulated and an RF-exposure source**: an uplink or RTK-correction bridge must meet the same licence-exempt limits as the rocket (in Singapore 10 mW e.r.p. at 433 MHz — a 12 dBi Yagi multiplies e.r.p. by ≈ 10 dB) or run under a licence; the E22 at 33 dBm into a 12 dBi Yagi is ≈ 17 W ERP, over even the 10 W ERP amateur limit ([19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md)). For the same station keep people **≥ 2 m in front of the Yagi** while it transmits (ICNIRP public: 1.0 m free space, 1.6 m with ground reflection, continuous TX) — [RF exposure](../19-regulations-safety/rf-exposure-safety.md).

## Intuition (no math)
Think of the ground station as an ear with a funnel. The funnel (antenna gain) collects more signal from where you point it and less noise and interference from elsewhere. The first amplifier (LNA) is like the eardrum — any loss before it (long thin coax, filters) is noise you can never remove, so put the LNA right at the antenna. Filters are ear-plugs for loud neighbours; they help if neighbours would otherwise deafen you, but they cost a little hearing. Because a rocket rolls, a single straight antenna on the ground periodically sees the rocket's antenna edge-on and hears nothing; a circularly polarised antenna hears it equally at all roll angles for a small fixed price. Finally, a recorder (SDR) that stores the raw radio signal lets you re-listen after the flight with better tools.

## The math
### Level 1 — cascade noise figure and sensitivity
Friis: $F = F_1 + \dfrac{F_2-1}{G_1} + \dfrac{F_3-1}{G_1G_2}+\dots$ (linear factors), a passive loss $L$ has $F = L$ ([noise figure & Friis](../07-noise-linearity/noise-figure-and-friis.md)). Sensitivity improves dB-for-dB with system NF (until external noise dominates, see below). `lora_ground_station.py` (module NF 6 dB):

| Chain | System NF |
|---|---|
| module, 1.5 dB coax | 7.5 dB |
| module, 5 dB coax (≈20 m RG58-class at 433 MHz) | 11.0 dB |
| masthead SAW (2 dB) → LNA (0.8 dB, 18 dB) → 5 dB coax → module | 3.4 dB |
| masthead LNA → SAW → 5 dB coax → module | **1.8 dB** |
| 5 dB coax → LNA at the receiver → module | 6.0 dB |

A masthead LNA recovers ~9 dB vs long coax straight into the module — as much as going from SF7 to SF10.

### Level 2 — geometry: height, Fresnel zone, tracking, pointing
**Fresnel clearance** (ground-to-ground or landed rocket): first-zone radius at mid-path $r_1 = \sqrt{\lambda d/4}$: 433 MHz — 18.6 m at 2 km, 41.6 m at 10 km; 923 MHz — 12.7 m and 28.5 m (script). Masts of a few metres never clear 60 % of it over km paths, so the landed link lives in the two-ray (−40 log d) regime and gains ≈ 6 dB per doubling of mast height ([Fresnel zones](../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md), [link budget example 4](lora-sensitivity-and-link-budget.md)). For the rocket in flight, elevation angle clears the zone within seconds.
**Tracking rate** for a vertical ascent at speed $v$, altitude $h$, station distance $D$: elevation $\epsilon = \arctan(h/D)$, $\dot\epsilon = vD/(D^2+h^2)$, maximum $v/D$ at lift-off: 100/300/600 m/s at D = 2 km → 2.9/8.6/17 °/s.
**Pointing loss** (Gaussian-beam approximation) $L \approx 12(\theta_e/\theta_{3dB})^2$ dB: a 50° beam loses 0.5 dB at 10° error and 1.9 dB at 20°; a 30° beam (long Yagi/helix) loses 5.3 dB at 20° — higher gain demands better tracking.

### Level 3 — external noise, blockers and diversity
**External noise**: with a masthead LNA the system temperature is dominated by the antenna temperature: sky 20–170 K at 433 MHz through the main lobe, ground ~290 K in sidelobes, and man-made noise near towns [5]. ITU-R P.372-13 Table 3 gives measured outdoor medians in Europe at 425 MHz of $F_a$ = 6 / 4 / 3 dB (city / residential / rural), i.e. **≈ 1150 / 730 / 580 K**, with decile spreads of only 1–2 dB. These are 1970s data and modern noise may differ. Do not confuse them with the P.372 city *line* $F_{am} = 76.8 - 27.7\log f_{MHz}$. That line is defined only for 0.3–250 MHz. Extrapolated to 425 MHz it gives 4.0 dB ≈ **720 K**, and that number is an extrapolation outside its validity range, not a P.372 value. The two numbers bracket a town site at about 700–1150 K. Use the measured 1150 K as the conservative city figure (as [07 thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md) and [15 link budget](lora-sensitivity-and-link-budget.md) do), and measure your own site (`tools/verify/s17_p372_city.py`). For $T_A$ versus elevation of a real Yagi over ground, see [08 antenna measurement](../08-antennas/antenna-measurement.md#antenna-temperature-and-gt-vs-elevation-over-ground). Pointing a directional antenna *up* at the rocket rather than along the horizon therefore improves noise as well as gain.
**Blockers**: an LNA's output P1dB/IIP3 must survive strong out-of-band signals ([dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)). In Singapore the 917–925 MHz band abuts 3GPP band 8 downlink (925–960 MHz; used for cellular — verify local assignments) and the E-GSM uplink (880–915 MHz) below it; LoRa's own selectivity (ACR 60–72 dB, blocking 88–99 dB at 1–10 MHz for SX1262 [6]) protects the chip but not a wideband LNA in front of it. Order: antenna → (limiter) → **filter if blockers are strong** → LNA → filter → coax.
**Diversity**: with independent loss events, selection combining at packet level gives $P_{loss} = \prod p_i$ (two receivers at 10 % → 1 %). Losses are correlated when caused at the rocket (tail-on null, plume), so place diversity branches to decorrelate them: **different look angles** (stations on opposite sides of the pad), **different polarisations**, **different bands** (433 + 900 MHz radios in the Space Bar fleet).

## Design equations & rules of thumb
| Rule | Value |
|---|---|
| LNA location | at the antenna; NF ≤ 1 dB, gain 15–20 dB |
| Filter before LNA only if | strong out-of-band signals (cellular, other teams) |
| Coax before any LNA | each dB adds a dB to NF |
| Tracking rate needed | $v/D$ (°/s = 57.3·v/D) |
| Pointing tolerance | error ≤ θ3dB/3 for < 1.3 dB loss |
| Circular ground antenna | −3 dB constant vs linear rocket antenna, no roll nulls |
| Height gain (two-ray) | +6 dB per doubling of either antenna height |
| Near-pad | ≥ 30–100 m or 20–40 dB attenuator |
| IQ recording | 1 MS/s 8-bit ≈ 7.2 GB/h |

## Worked examples
**1. Upgrading from a module on a 20 m coax to a masthead LNA.** NF 11.0 → 1.8 dB: sensitivity of SF9/125 improves from −124.5 to −133.7 dBm (−174 + 51 + NF − 12.5). In the landed two-ray regime (−40 log d) that 9.2 dB is ×1.7 range; in free space ×2.9.

**2. Hand-tracking budget.** 6-element 433 MHz Yagi (~10 dBi, θ3dB ≈ 50–60°). Rocket at 3 km altitude, 2 km away, climbing 300 m/s: $\dot\epsilon$ = 300·2000/(2000² + 3000²) = 0.046 rad/s = 2.6 °/s — easy by hand if you know where to point (use the downlinked GNSS position and a tablet display of az/el). At lift-off the rate is 8.6 °/s — just keep the beam above the pad; the budget is large there anyway.

**3. Two-station diversity for the tail-on null.** Station A 2 km east of the pad, station B 5 km west. At 10 km altitude A sees θ = 11.3° (≈ −16.2 dB axial-dipole loss, half-wave pattern cos(π/2·cos θ)/sin θ), B sees 26.6° (≈ −8.7 dB, same pattern; a short-dipole sin θ model gives −14.1 / −7.0 dB). Even if A drops packets during the null, B's pattern is ≈ 7.5 dB better; B's longer slant range (11.2 vs 10.2 km) costs 0.8 dB, so B's net advantage is ≈ 6.7 dB (corrected 2026-10-13 from "−6 dB / 10 dB better", D7 #1); combined loss ≈ product of the two stations' loss probabilities if other causes are independent.

**4. Recording the flight.** RTL-SDR at 1.0 MS/s (enough for 500 kHz LoRa) for 30 min: 3.6 GB of 8-bit IQ. Post-flight: gr-lora_sdr decodes all SF/BW combinations used, and the de-chirped peak offset gives the carrier frequency of every packet — a direct measurement of Doppler (velocity check against GNSS) and of oscillator drift.

## Practical notes
- **Polarisation on the pad**: a vertical rocket antenna and a horizontally mounted Yagi are cross-polarised (−15 to −25 dB) — mount Yagis vertically or use CP [2].
- **Helix vs crossed Yagi**: axial-mode helix gives CP naturally; realistic gain for a 10-turn helix is ~13 dBic, not the 16–17 dBi of Kraus's formula ([helical antennas](../08-antennas/helical-antennas.md)).
- **Protect the LNA**: a nearby 2 W transmitter (another team's, or your own rocket on the pad) can destroy it; use a limiter or keep a switchable attenuator in line during pad operations. Typical pHEMT LNAs are also ESD-fragile (PSA4-5043+: HBM Class 1B, MM 35 V) — ground the coax before connecting ([lab safety](../19-regulations-safety/lab-safety-esd-high-power.md)). LNA placement trade-off worked with real parts: [LNA design Example 5](../06-rf-circuits/lna-design.md); feeder loss per metre at 433/915 MHz: [coax Example 1](../03-transmission-lines-matching/coax-and-cables.md).
- **SDR choice**: the RTL-SDR Blog V4 is end-of-line; its successor V4L (R828S tuner) or a V3 is the cheap recorder, ideally behind a masthead LNA + SAW ([SDR hardware survey Example 1](../14-sdr-dsp/sdr-hardware-survey.md)). Decimation chain for a 1–2 MS/s capture down to a 125/500 kHz LoRa channel: [multirate Example 1](../14-sdr-dsp/multirate-dsp-decimation-cic.md); LoRa demodulation as non-coherent M-FSK and how a CFO appears as a one-bin shift: [software demodulation](../14-sdr-dsp/software-demodulation.md).
- **Bias-tee / power**: masthead LNAs are usually powered through the coax; check DC blocking on the receiver input.
- **Receivers**: the same module type as the flight radio guarantees modem compatibility; an SPI-chip receiver (SX1262 + RadioLib) also reports SNR and frequency error per packet; an SDR records everything. Run all three in parallel from a splitter (a 2-way splitter costs 3.5 dB but after a masthead LNA this barely affects NF).
- **Timing**: timestamp every packet from a GNSS-disciplined clock (PPS) so that multiple stations and the flight log can be aligned.
- **Logging**: raw payload bytes, RSSI, SNR, frequency error, receiver ID, antenna pointing (if tracked), station position, and SDR IQ files with start timestamps. Parse with the same protocol definition as the flight firmware.
- **Interference survey**: before launch day, sweep the band at the site with the SDR for an hour (433 MHz SRDs, 920 MHz LoRaWAN/RFID, cellular leakage); pick the channel with the lowest floor. EBYTE modules can report ambient-channel RSSI ([modules](lora-modules-ebyte-rfm-heltec.md)).
- **Several receivers on one antenna:** a 433 MHz four-receiver multicoupler is worked in [06 couplers § Example 8](../06-rf-circuits/couplers-dividers-combiners.md#example-8--a-433-mhz-ground-station-multicoupler-for-four-receivers).

## Link asymmetry and receiver overload near the pad

### Level 1 — two budgets, not one
A link budget has a direction. For each direction, received power is $P_r = \mathrm{EIRP}_{tx} - L_{path} + G_{rx} - L_{feed,rx}$ and the margin is $P_r - S_{rx}$, with $S_{rx} = -174 + NF_{rx} + 10\log_{10}BW + \mathrm{SNR}_{req}$. The path loss is the same both ways (reciprocity). The **transmit power, the receive antenna gain and the receive noise figure are not**, and neither is the noise around each receiver. Three consequences:
1. **An e.r.p. limit caps the radiated power, not the receive gain.** A 12 dBi Yagi used to transmit must have its conducted power cut by 12 dB to stay at the same e.r.p. On receive, the same Yagi's 12 dB is free.
2. **The masthead LNA helps only the downlink.** The station must also bypass it with a T/R relay to transmit, which adds loss to the uplink, and on receive the relay is the "unused port" that must not be left open (below).
3. **A two-way exchange closes only if both directions close**: $M_{2way} = \min(M_{down}, M_{up})$. Raising one node's power raises only the margin of the direction it transmits in. A "louder 1 W node" therefore cannot fix a mesh whose quiet nodes cannot reach it; its ACKs and routing beacons still depend on the weaker direction (see [mesh capacity](lora-mesh-capacity-and-congestion.md)).

### Level 2 — the E22 ↔ ground-station budget both ways
`tools/verify/s1_two_way_link.py`, 434.125 MHz, 30 km slant range (FSPL 114.7 dB), 13 dB fade/polarisation margin. Rocket: 2.15 dBi antenna, 0.5 dB feeder, receive NF 6 dB plus an assumed 3 dB local noise rise. Station: 12 dBi Yagi, 1 dB feeder, 0.3 dB T/R relay, system NF 1.8 dB.

| Case | Downlink EIRP / uplink EIRP | Margin SF7 down / up | SF9 down / up | Asymmetry |
|---|---|---|---|---|
| Licensed: rocket 33 dBm; station E22 stepped to 30 dBm (40.7 dBm EIRP = 38.6 dBm ERP, under the 10 W amateur limit; 33 dBm would be ≈ 14 W ERP) | 34.6 / 40.7 dBm | +47.6 / +36.1 dB | +52.6 / +41.1 dB | 11.5 dB |
| Licence-exempt: both ends 10 mW e.r.p. (rocket 10.5 dBm conducted; station 1.45 dBm, i.e. a 23 dB pad after the E22's lowest 24 dBm step) | 12.15 / 12.15 dBm | +25.1 / +7.6 dB | +30.1 / +12.6 dB | 17.5 dB |

When both ends radiate the same, the asymmetry is simply $(G_{GS} - G_{rocket} + L_{rocket}) + (NF_{rocket,eff} - NF_{GS})$: 10.35 + 7.2 = 17.6 dB, which the budget reproduces. In the licence-exempt case an uplink command at SF7 has only 7.6 dB left after the fade margin, while the downlink has 25 dB. Uplinks should therefore use a higher SF than the downlink, or be avoided (Space Bar flies downlink-only; [rocket telemetry § uplink](rocket-telemetry-radio-design.md)).

**LoRaWAN-style receive windows add a timing asymmetry.** A class A device listens only in RX1 (1 s after its uplink, same channel and, by default, the same data rate) and RX2 (2 s after, AS923 default 923.2 MHz at DR2 = SF10/125) [10]. A downlink that misses both windows is lost even if it would have closed. In addition, the gateway is half-duplex: while it transmits a downlink it hears no uplinks on any channel.

**LoRaWAN TXPower is an index, not dBm.** In EU868 and AS923, TXPower $n$ means EIRP = MaxEIRP − 2n dB (n = 0…7), with a default MaxEIRP of 16 dBm. The network can raise MaxEIRP in AS923 with `TxParamSetupReq`. In US915 the index is conducted power: 30 − 2n dBm (n = 0…14) [10]. The conducted setting is therefore EIRP − antenna gain + feeder loss: TXPower 0 is 13.85 dBm conducted with a 2.15 dBi dipole, and 17 dBm with a 0 dBi antenna and 1 dB of cable. AS923's default 16 dBm EIRP is below Singapore's 22.15 dBm EIRP (100 mW e.r.p.) LPWAN limit, and the 1 % duty rule still applies ([19](../19-regulations-safety/singapore-imda-rules.md)).

### Level 2 — receivers that fail when too close
Free-space distances, on a 12 dBi receive antenna, inside which the received power reaches each threshold. Below about 2D²/λ (≈ 2–5 m for a Yagi) these are only indicative.

| Threshold at the receive port | 2 W rocket (34.65 dBm EIRP) | 10 mW e.r.p. (12.15 dBm EIRP) |
|---|---|---|
| ≈ −15 dBm: SX126x 1 dB compression estimated as IIP3 (−5 dBm [6]) − 9.6 dB | 64 m | 4.8 m |
| ≈ −30 dBm: the same, referred to the SMA of a module with a ~15 dB internal LNA (estimate) | 360 m | 27 m |
| +10 dBm: SX126x absolute-maximum RF input [11]; EBYTE's "blocking/damage" rating [8] | 3.7 m | 0.3 m |
| +17 dBm: pHEMT masthead LNA CW limit (PSA4-5043+) [9] | 1.7 m | 0.1 m |

LoRa has a constant envelope, so compression of the wanted signal alone does not stop demodulation. The ways a too-close receiver actually fails are: **damage** above about +10 dBm; **AGC/IF saturation**, so that RSSI reads full scale and decoding becomes erratic (the level at which this happens in the EBYTE modules is unpublished, so measure it: register §7 R02/R03); **blocking** of a *second* receiver or channel at the site, which is a selectivity problem ([dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)); and **burn-out of a masthead LNA** by your own or another team's transmitter on the pad. Fixes: keep ≥ 30–100 m, point the Yagi away during pad checks, put a 20–40 dB switchable pad or a limiter ahead of the LNA ([SDR front-end protection](../14-sdr-dsp/sdr-front-end-protection-and-filtering.md)), and bench-test only through ≥ 40 dB of attenuation.

### Practical notes — the unused RF port
- **Terminate any RF port you are not using in 50 Ω**: the unused side of a splitter, a dual-antenna module's second port, an SDR's TX port, a T/R relay's TX throw. An open splitter port reflects, which upsets the split and the match of the port you do use. An open input picks up local noise and interference. An unterminated amplifier port can make the amplifier oscillate ([amplifier stability](../06-rf-circuits/amplifier-stability-and-biasing.md)).
- **Never transmit with no antenna or load.** EBYTE and SX126x PAs survive moderate mismatch (and SX126x clamping cuts power by 5–6 dB, see [chip errata 15.2](semtech-chip-family.md)), but full power into an open circuit for long packets risks the PA.
- **One antenna for TX and RX at the station** needs a relay or a switch that bypasses the masthead LNA during transmit. The LNA must never see the station's own transmitter: check the relay's isolation against the LNA's +17 dBm limit.

## Common mistakes & misconceptions
- **"It works in one direction, so the link is fine."** Budget each direction separately. ACKs, commands and mesh hops need the weaker direction.
- **"Turn the node up to 1 W and the mesh will work."** A louder node only raises the margin of what *it* transmits. Under an e.r.p. limit, the fix for the weak direction is receive gain, a lower NF or a higher SF, not more power.
- **Reading LoRaWAN TXPower as conducted dBm** (outside US915 it is EIRP relative to MaxEIRP).
- **Leaving a splitter or relay port open**, and **transmitting into the masthead LNA** through a T/R relay with poor isolation.
- **"A higher-gain antenna always helps."** Narrower beams need tracking; a 30° beam mis-pointed by 20° loses 5 dB.
- **"Put the filter first to be safe."** Its loss adds directly to NF; do it only for real blockers.
- **"The LNA fixes long coax at the receiver end."** An LNA after 5 dB of coax still leaves NF ≈ 6 dB.
- **Omni on a tripod for landed recovery** — height and gain matter most after landing; raise the antenna or walk toward the last fix.
- **One receiver, no recording** — a single loss mechanism can blank the whole flight with nothing to analyse.

## How to simulate / verify
- `python3 tools/verify/lora_ground_station.py` — cascades, Fresnel radii, tracking rates, pointing loss, diversity, IQ data rates.
- `python3 tools/verify/lora_link_budget.py` — in-flight and landed budgets with your antenna gains.
- `python3 tools/verify/s1_two_way_link.py` (6 checks) — downlink and uplink budgets (licensed and licence-exempt), equal-EIRP asymmetry formula, "louder node" check, overload distances, LoRaWAN TXPower index → conducted dBm.
- Bench: find the module's overload level by stepping a generator from −60 dBm to 0 dBm (never above +10 dBm) through the attenuator ladder and logging PER and RSSI.
- Measure the system: sky-vs-load noise comparison with the SDR (Y-factor) to find the real system temperature ([thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md)); attenuator-ladder sensitivity test through the whole chain.
- gr-lora_sdr on recorded IQ [4]; GNU Radio flowgraph → [SDR software](../14-sdr-dsp/gnu-radio-and-software-stack.md).

## Open questions / gaps
- Specific LNA and SAW part choices for 433/923 MHz (NF, P1dB, rejection above 925 MHz) are deferred to [18-components-parts](../18-components-parts/lna-pa-gain-block-mmics.md) and [filter parts](../18-components-parts/filter-parts-saw-ceramic-ltcc.md).
- Singapore cellular band-8 deployment near candidate launch/test sites not verified.
- Rotator slew capabilities of affordable amateur rotators not sourced.

## Sources
1. This KB, [Yagi-Uda and log-periodic](../08-antennas/yagi-uda-and-log-periodic.md) (W1-A6) — DL6WU gains at 433/915 MHz (MoM), 3-element ≈ 9 dBi with a matched ≈ 11 Ω feed, ≈ 8.5 dBi fed directly from 50 Ω (NEC, [16 NEC modelling Example 4](../16-simulation-tools/nec-antenna-modelling.md), added 2026-10-14). (internal)
2. This KB, [Antenna polarization & CP](../08-antennas/antenna-polarization-and-circular-polarization.md) — roll nulls, crossed-Yagi CP, pad cross-polarisation example. (internal)
3. Featherweight Altimeters, *GPS Tracker User's Manual* (2025) — GNSS-based pointing arrow, hand Yagi +6–8 dB ≈ ×2–3 range. (manufacturer)
4. J. Tapparel et al., "An Open-Source LoRa Physical Layer Prototype on GNU Radio," SPAWC 2020; gr-lora_sdr. https://github.com/tapparelj/gr-lora_sdr (peer-reviewed + code)
5. ITU-R P.372-13 (2016) via [thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md) — 425 MHz man-made noise; galactic 20–170 K at 433 MHz. (standard)
6. Semtech, *SX1261/2 Datasheet* Rev 1.2 — ACR 60/72 dB, blocking 88/90/99 dB, IIP3 −5 dBm. (datasheet)
7. 3GPP TS 36.101 (E-UTRA UE radio transmission and reception), operating band 8: UL 880–915 MHz, DL 925–960 MHz. (standard — band edges cited from general knowledge of the band table, not re-read in this pass)
8. EBYTE, *E22-400TXXX Data Sheet* — 10 dBm blocking/damage rating; ambient RSSI. (module datasheet)
9. This KB, [lab safety](../19-regulations-safety/lab-safety-esd-high-power.md) and [RF exposure](../19-regulations-safety/rf-exposure-safety.md) (W3-C5) — Mini-Circuits PSA4-5043+ Rev D (+17 dBm CW, HBM 1B, MM 35 V); ICNIRP 2020 safe distances for 2 W + 12 dBi Yagi at 433 MHz (`tools/verify/reg_rf_exposure.py`). (internal, citing datasheet and ICNIRP)
10. LoRa Alliance, *RP002-1.0.3 LoRaWAN Regional Parameters* (2021), Tables 10 and 72 (EU868/AS923 TXPower = MaxEIRP − 2n, default 16 dBm), US902-928 TXPower table (30 dBm − 2n conducted), AS923 RX2 923.2 MHz DR2, RECEIVE_DELAY1/2 = 1/2 s, 400 ms dwell, TxParamSetupReq. https://lora-alliance.org/wp-content/uploads/2021/05/RP002-1.0.3-FINAL-1.pdf (standard)
11. Semtech, *SX1261/2 Datasheet* Rev 1.2, Table 3-2 — absolute-maximum RF input level +10 dBm. (datasheet)
12. `tools/verify/s1_two_way_link.py` — numbers in the link-asymmetry section. (own verification)
