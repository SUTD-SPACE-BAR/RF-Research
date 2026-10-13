---
title: LoRaWAN vs raw LoRa (and Meshtastic, Reticulum) — what each is for, and why rockets use raw LoRa
domain: 15-lora-ism-radios
slug: lorawan-vs-raw-lora
tags: [lorawan, lora, classes, adr, gateway, network-server, ttn, regional-parameters, meshtastic, reticulum, rnode, tinygs, rocket]
prerequisites:
  - lora-phy-css-math.md
  - ism-band-plans-duty-cycle.md
related:
  - rocket-telemetry-radio-design.md
  - lora-modules-ebyte-rfm-heltec.md
  - ground-station-design.md
  - ../10-comms-modulation/packet-framing-protocols.md
level: intro
confidence: medium
last_updated: 2026-10-03
---

# LoRaWAN vs raw LoRa (and Meshtastic, Reticulum)

## Questions this page answers
- What is the difference between LoRa and LoRaWAN?
- What are LoRaWAN Class A, B and C devices?
- What does ADR do, and why is it bad for moving devices?
- Could I send rocket telemetry through The Things Network or a LoRaWAN gateway?
- What are Meshtastic and Reticulum, and are they useful for a launch site?
- Which should I use for a rocket downlink, an RTK-correction link, or a recovery beacon?

## TL;DR
- **LoRa** is the physical layer (chirp modulation, [PHY page](lora-phy-css-math.md)). **LoRaWAN** is a MAC/network protocol on top of it: star-of-stars topology (end devices → multi-channel gateways → network server → application server), AES-128 security, 13 bytes of minimum MAC overhead, regional channel plans (RP002) [1][2].
- **Classes** [3]: A — every uplink is followed by two short receive windows (RX1 after 1 s, RX2 after 2 s by default [1]); B — adds beacon-synchronised ping slots; C — listens continuously (mains-powered).
- **ADR**: the *network server* chooses SF and TX power from the SNR margin of recent uplinks (The Things Stack uses the last 20) [4]; it assumes a stationary device — TTN advises disabling it when the device moves [4].
- **LoRaWAN is a poor fit for rocket telemetry**: public-network fair use on TTN is **30 s of uplink air time and 10 downlinks per device per day** [5]; AS923/EU plans impose ≤ 1 % duty and (AS923) 400 ms dwell [1]; multi-second network latency; no gateways at remote launch sites; ADR is wrong for a moving vehicle. A 5-minute flight at 10 Hz with 72 ms frames needs 216 s of air time.
- **Raw LoRa** (point-to-point, your own framing) gives full control of SF/BW/CR, timing, frequency and error handling — what Space Bar and most rocketry teams use.
- **Meshtastic**: open-source LoRa mesh messaging on SX126x/LR11xx boards, presets from SF7/500 to SF11/125 (LongFast = SF11/250), hop limit 3, region presets (SG_923 = 917–925 MHz, 20 dBm) [6]. Useful as a launch-site text/position network, not for 10 Hz telemetry.
- **Reticulum**: cryptographic network stack (Curve25519 ECDH, per-packet encryption) that runs over LoRa via RNode firmware on common boards [7]; good for secure low-rate site networks.
- **Where LoRaWAN *can* help**: a post-landing recovery beacon near a city with TTN coverage (balloon trackers do this; the 702–832 km records were LoRaWAN [8]), or satellite reception networks (TinyGS, Norby [9]).

## Intuition (no math)
LoRa is a way of shaping radio waves; LoRaWAN is a set of traffic rules for millions of cheap sensors sharing a few channels with a city-wide network of gateways. The rules optimise for battery life and fairness: talk rarely, briefly, and let the network tell you how loud and how slow to be. A rocket is the opposite: one vehicle, talking constantly for a few minutes, moving fast, far from any network. So rockets use LoRa without the WAN — their own point-to-point protocol to their own ground station.

## The math
### Level 1 — overhead and air-time arithmetic
LoRaWAN frame overhead ≥ 13 bytes (MHDR 1, DevAddr 4, FCtrl 1, FCnt 2, FPort 1, MIC 4) [10]; with no application payload an SF7/125 uplink lasts 46.3 ms and an SF12/125 uplink 1155 ms ([PHY page](lora-phy-css-math.md)). TTN's 30 s/day budget then allows ≈ 650 empty SF7 frames or 26 SF12 frames per day.
Rocket need: $N = f\,T_{flight}$ frames of air time $T_p$ each: 10 Hz × 300 s × 72 ms (32-byte SF7/125) = 216 s — **7× the whole daily TTN allowance in one flight**, and 22× the 1 % duty-cycle budget of that 300 s window (3 s).

### Level 2 — LoRaWAN mechanics relevant to a designer
- **Uplink**: ALOHA — the device transmits whenever it wants on a pseudo-randomly chosen channel from the regional plan (AS923 default 923.2/923.4 MHz + network-added channels) [1]. Gateways (8-channel concentrators) receive all SFs on all channels simultaneously.
- *ALOHA/slotted-ALOHA throughput derived and simulated, CSMA/LBT and launch-day channel planning: [multiple access and duplexing](../10-comms-modulation/multiple-access-and-duplexing.md).*
- **Downlink**: only in the RX1/RX2 windows after an uplink (Class A); LoRaWAN downlinks use **inverted IQ** so devices don't hear each other [1].
- **Join**: OTAA (join-request/accept, JOIN_ACCEPT_DELAY1/2 = 5/6 s) or ABP; session keys for network MIC and application payload encryption [1][2].
- **ADR**: the network measures the SNR margin $m = \text{SNR}_{meas} - \text{SNR}_{req}(SF)$ over recent uplinks and steps SF down (and power) while keeping an installation margin; e.g. a device at SF12 with +5 dB SNR has a 25 dB margin and could run SF7 with 12.5 dB to spare [4]. ADR_ACK_LIMIT 64 / ADR_ACK_DELAY 32 control the device-side fallback when downlinks stop arriving [1].
- **Regional limits** (EU868 1 %, AS923 1 % + 400 ms dwell, US915 400 ms dwell on 125 kHz channels) are in [band plans](ism-band-plans-duty-cycle.md).

### Level 3 — mesh and alternative stacks
- **Meshtastic** floods packets through up to 3 hops by default ("really, 3 is fine") [6]; each rebroadcast costs air time, so mesh capacity shrinks rapidly with node count and SF. Channels use a pre-shared key (see Meshtastic docs). Presets and region limits: [6].
- Mesh airtime, ALOHA collision limits, flooding overhead and launch-day capacity are worked in [LoRa mesh capacity and congestion](lora-mesh-capacity-and-congestion.md).
- **Reticulum** separates routing/transport from the medium; RNode is a LoRa "radio modem" firmware, the host runs the stack; all multi-hop traffic is encrypted with ephemeral ECDH keys [7].
- **LR-FHSS** (LoRaWAN DR8–11 in some regions): frequency-hopping narrowband bursts for massive/satellite uplinks; ToA $N\times233.472$ ms of headers + $\lceil(L+3)/2\rceil\times102.4$ ms payload (CR1/3) [1] — seconds per packet, not telemetry.

## Design equations & rules of thumb
| Use case | Recommended stack |
|---|---|
| Rocket flight telemetry (5–20 Hz) | raw LoRa (SF7, 125–500 kHz) or FSK, own protocol |
| RTK corrections to rocket/rover | raw LoRa or FSK, own framing, separate band |
| Post-landing beacon near a city | raw LoRa to own station; optionally LoRaWAN/TTN as backup |
| Launch-site team messaging/positions | Meshtastic (legal region preset) |
| Secure low-rate site network | Reticulum over RNode |
| Satellite / HAB experiments | LoRaWAN or TinyGS networks |

## Worked examples
**1. TTN as a backup recovery channel.** After landing, send a 20-byte GNSS fix (33 bytes with MAC overhead) at SF10/125 (DR2): 453 ms per uplink (`lora_toa.py`, 8-symbol preamble, explicit header, CRC); 30 s/day allows ~66 fixes — adequate for a one-off recovery if a gateway is in range (not the case at most launch sites).
**2. Why ADR fails in flight.** ADR's decision uses the last ~20 uplinks; at 10 Hz those span 2 s during which the geometry, antenna nulls and Doppler change completely. The network would command an SF based on stale conditions, and the command arrives only in a later RX window — seconds late.

## Practical notes
- Commercial "LoRa" dev boards often ship with LoRaWAN firmware (e.g. Wio-E5 AT firmware, RAK AT firmware); for raw LoRa use RadioLib or vendor SDK P2P modes ([modules](lora-modules-ebyte-rfm-heltec.md)).
- If you do use LoRaWAN, Singapore devices use AS923-1; check the IMDA end-device limits (100 mW e.r.p., ≤ 1 % duty) [band plans](ism-band-plans-duty-cycle.md).
- EBYTE UART modules are raw LoRa with a proprietary framing/addressing layer; they are not LoRaWAN devices (TTN forum moderator: "not suited for TTN") [11].

## Common mistakes & misconceptions
- **"LoRa = LoRaWAN."** LoRa is the modulation; LoRaWAN is one of several protocols on top.
- **"LoRaWAN gives me encryption, so raw LoRa is insecure."** Raw LoRa has whatever security you implement; LoRaWAN's AES-128 keys are only as good as their provisioning.
- **Leaving ADR on for mobile devices.**
- **Using a public network for time-critical data** — latency and fair-use limits make it unsuitable.
- **Assuming Meshtastic's region presets equal legality** (SG_923 applies no duty cycle; IMDA's LPWAN-end-device class specifies ≤ 1 %).
- **Taking Meshtastic "range records" seen in the app at face value.** Packets bridged over the internet by
  MQTT gateways and re-broadcast locally show a distant node's position with a local RSSI/SNR; the firmware
  flags them (`via_mqtt`). That is internet range, not RF range — see
  [LoRa link budget — common mistakes](lora-sensitivity-and-link-budget.md) and disable MQTT for range tests.

## How to simulate / verify
- Air-time and duty budgets: `python3 tools/verify/lora_toa.py` (includes `regulatory_timing`).
- The Things Network airtime calculator reproduces the same formula for LoRaWAN frames (+13 bytes).

## Open questions / gaps
- LoRaWAN 1.0.x vs 1.1 security details, Class B beacon timing, and LoRaWAN relay are not covered.
- Helium and other public networks (coverage near Singapore launch/test sites) not researched.
- Meshtastic encryption details (cipher/mode) not verified here.

## Sources
1. LoRa Alliance, *RP002-1.0.3 LoRaWAN Regional Parameters* (2021) — default timing constants (RECEIVE_DELAY1 1 s, RECEIVE_DELAY2 2 s, JOIN_ACCEPT_DELAY1/2 5/6 s, ADR_ACK_LIMIT 64, ADR_ACK_DELAY 32), PHY settings (IQ inversion downlink), AS923 channels/DRs, LR-FHSS ToA. (standard)
2. LoRa Alliance, LoRaWAN L2 specification TS001 (referenced by RP002; not read in this pass). (standard)
3. The Things Network docs, "Device Classes" (accessed 2026-09-27). https://www.thethingsnetwork.org/docs/lorawan/classes/ (project docs)
4. The Things Network docs, "Adaptive Data Rate" (accessed 2026-09-27) — network-side decision, last 20 uplinks, margin example, backoff, mobile-device advice. https://www.thethingsnetwork.org/docs/lorawan/adaptive-data-rate/ (project docs)
5. The Things Network, Fair Use Policy (forum/docs summary) — 30 s uplink air time and 10 downlinks per node per 24 h on the public community network. https://www.thethingsnetwork.org/forum/t/fair-use-policy-explained/1300 (community policy)
6. Meshtastic docs, "Radio Settings" and "LoRa configuration" (accessed 2026-09-27) — presets, regions, hop limit, duty handling. https://meshtastic.org/docs/overview/radio-settings/ (project docs)
7. Reticulum Network Stack manual ("What is Reticulum?", "Communications Hardware", 2026) — Curve25519 ECDH, per-packet encryption, RNode LoRa firmware. https://reticulum.network/manual/whatis.html (project docs)
8. The Things Network, record articles (702 km, 832 km, 1336 km). (community news)
9. arXiv:2506.20858 (2025) — Norby LoRa satellite and TinyGS reception network. (preprint)
10. avbentem, *airtime-calculator* README — 13-byte LoRaWAN overhead breakdown. https://github.com/avbentem/airtime-calculator (community tool)
11. TTN forum, "E32 'low-level' parameters" thread — EBYTE E32 described as a UART-fronted plain LoRa module, not suited for TTN. https://www.thethingsnetwork.org/forum/t/e32-low-level-parameters/48017 (forum — anecdotal)
