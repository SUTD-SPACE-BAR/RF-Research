# 15-lora-ism-radios — LoRa and other ISM/SRD radios

Scope: the LoRa physical layer (chirp spread spectrum) derived from first principles; time-on-air,
sensitivity and link budgets; impairments that matter on rockets (Doppler rate, oscillator drift,
timing, capture, interference); the Semtech chip family and the modules built on it (EBYTE E22/E220/E32,
HopeRF RFM9x, Heltec/RAK/LilyGo/Seeed boards); LoRaWAN versus raw LoRa and mesh stacks; competing ISM
radios (FSK/GFSK, FHSS telemetry modems, 2.4 GHz options); rocket-telemetry radio and ground-station
design; and the band plans, duty-cycle and dwell rules that constrain all of it (Singapore IMDA, ETSI,
FCC, LoRaWAN RP002). Generic link-budget/propagation theory lives in
[09-propagation-link-budget](../09-propagation-link-budget/), antennas in [08-antennas](../08-antennas/),
generic modulation in [10-comms-modulation](../10-comms-modulation/), SDR in [14-sdr-dsp](../14-sdr-dsp/),
legal interpretation in [19-regulations-safety](../19-regulations-safety/).

Reader context: Space Bar primary FC downlinks with an EBYTE **E22-400T33D** (SX1268, 433 MHz, 2 W);
secondary FC with an **E220-900T30D** (LLCC68, 900 MHz, 1 W); RTK corrections have used a separate LoRa bridge.

## Reading order (beginner → advanced)
1. [lora-phy-css-math](lora-phy-css-math.md) — what a chirp is, SF/BW/CR, bit rate, de-chirp + FFT, time-on-air.
2. [lora-sensitivity-and-link-budget](lora-sensitivity-and-link-budget.md) — sensitivity equation, real noise figures, E22/E220 budgets, why landed rockets go quiet.
3. [ism-band-plans-duty-cycle](ism-band-plans-duty-cycle.md) — what you may transmit, where, how often (Singapore first).
4. [lora-modules-ebyte-rfm-heltec](lora-modules-ebyte-rfm-heltec.md) — what is inside the modules you fly; UART modules vs bare chips.
5. [semtech-chip-family](semtech-chip-family.md) — chip-level choices, register concepts, errata.
6. [lora-impairments-doppler-drift-timing](lora-impairments-doppler-drift-timing.md) — Doppler rate, drift, TCXO, capture, interference (advanced, rocket-critical).
7. [rocket-telemetry-radio-design](rocket-telemetry-radio-design.md) — putting it together for a flight.
8. [ground-station-design](ground-station-design.md) — antennas, LNA/filter chain, tracking, diversity, SDR recording.
9. [other-ism-radios-fsk-2g4](other-ism-radios-fsk-2g4.md) — when FSK/FHSS/2.4 GHz beats LoRa.
10. [lorawan-vs-raw-lora](lorawan-vs-raw-lora.md) — LoRaWAN, Meshtastic, Reticulum, and why rockets use raw LoRa.
11. [choosing-and-judging-lora-antennas](choosing-and-judging-lora-antennas.md) — practical antenna choice: gain vs elevation pattern (high-gain omnis vs rockets overhead), size test for gain claims, NanoVNA and A/B RSSI testing, ground planes, connectors, cables, mounting, airframe and ground-station choices. (Beginners can read this right after page 2.)

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [lora-phy-css-math](lora-phy-css-math.md) | CSS waveform, cyclic-shift symbols, orthogonality, processing gain, SER theory, coding chain, packet structure, ToA derivation (verified 5820 cases), LDRO | mixed | high |
| [lora-sensitivity-and-link-budget](lora-sensitivity-and-link-budget.md) | sensitivity equation, ideal vs Semtech SNR, implied NF, EBYTE claim check, E22/E220/SG-legal budgets, landed two-ray range, near-pad overload, records | mixed | high |
| [lora-impairments-doppler-drift-timing](lora-impairments-doppler-drift-timing.md) | ±25 % BW offset, ppm limits as timing slip, Doppler vs Doppler rate for Mach 1–5, allowed acceleration per SF/BW, crystal/TCXO/g-sensitivity, capture, quasi-orthogonality, multipath | mixed | medium |
| [semtech-chip-family](semtech-chip-family.md) | SX127x, SX126x, SX1268, LLCC68, LR11xx, LR2021, SX128x, STM32WL specs; PA/OCP/TCXO/image-cal concepts; SX126x known limitations | intermediate | medium |
| [lora-modules-ebyte-rfm-heltec](lora-modules-ebyte-rfm-heltec.md) | EBYTE naming, E22/E220 registers/modes/RSSI/LBT/WOR, air-rate codes (mapping unknown — SDR procedure), supply/heat, dev boards, UART vs bare chip, libraries | intermediate | medium |
| [lorawan-vs-raw-lora](lorawan-vs-raw-lora.md) | LoRaWAN architecture, classes, ADR, fair use, why not for rockets; Meshtastic; Reticulum; LR-FHSS | intro | medium |
| [other-ism-radios-fsk-2g4](other-ism-radios-fsk-2g4.md) | FOM = NF + Eb/N0 comparison of LoRa vs CC1101/Si4463/SX126x-FSK/RFD900x/XBee/nRF/SX1280-FLRC; when FSK wins | intermediate | medium |
| [rocket-telemetry-radio-design](rocket-telemetry-radio-design.md) | air-time budget, packet design, packet-level FEC, boost vs landed modes, look-angle nulls, plume, roll, two-band harmonics, same-band RTK conflict, uplink safety, flown examples | mixed | medium |
| [ground-station-design](ground-station-design.md) | Yagi/helix/CP, Friis chain with masthead LNA and SAW order, 925–960 MHz blocker risk in SG, tracking rates, pointing loss, diversity, SDR IQ recording, logging | intermediate | medium |
| [ism-band-plans-duty-cycle](ism-band-plans-duty-cycle.md) | IMDA TS SRD (433, 866–869, 917–925 MHz) vs the Exemption Notification, EU Decision 2025/105 sub-bands, FCC §15.247 and 97.303(n)(2)/IREC, Australia LIPD 2025, RP002 plans (AS923, EU868, US915, IN865), duty and dwell arithmetic | intro | medium |
| [choosing-and-judging-lora-antennas](choosing-and-judging-lora-antennas.md) | collinear gain vs elevation toward a rocket (pad → apogee → landed), minimum radiator length per claimed omni gain (5 dBi ≥ 1.24 λ, 8 dBi ≥ 2.84 λ), 5.16 dBi infinite-ground trap, mismatch and feeder tables, A/B RSSI sample sizes with interleaving, red flags, SMA/RP-SMA/U.FL, mounting, airframe and ground-station recommendations | mixed | medium |
| [lora-mesh-capacity-and-congestion](lora-mesh-capacity-and-congestion.md) | Meshtastic preset ToA (16-sym preamble), pure/slotted ALOHA and CSMA derived + MC, managed-flood MC (2 + n_router tx/msg; load ∝ (Hr)²), p^h, asymmetric links, firmware 25/40 % CU throttles, duty-cycle budgets, MeshCore, launch-day FDMA and near–far checks | mixed | medium |

Verification scripts (all in `tools/verify/`): `e6_lora_antennas.py` (antenna gain vs elevation, gain-claim size test, A/B RSSI statistics), `lora_toa.py` (ToA, bit rates, dwell/duty), `lora_css_sim.py`
(chirp modem Monte-Carlo, SNR thresholds, CFO/drift), `lora_doppler.py` (Doppler/drift budgets),
`lora_link_budget.py` (sensitivity, NF, budgets, landed two-ray), `lora_ground_station.py` (cascades,
Fresnel, tracking, diversity), `lora_ism_compare.py` (radio figure of merit).

## Domain FAQ (top questions → page#section)
- Can a LoRa ground station decode a CubeSat (TinyGS) without Doppler correction, and which SF fails near zenith? → [09 satellite links § Example 3](../09-propagation-link-budget/satellite-links-doppler-tracking.md#worked-examples)
- Why does a ground station near the pad see more acceleration than the rocket? → [impairments § line-of-sight term](lora-impairments-doppler-drift-timing.md#doppler-rate-seen-from-the-ground--the-line-of-sight-rotation-term)
- How long is my LoRa packet on the air? → [lora-phy-css-math § Level 3](lora-phy-css-math.md#level-3--the-full-phy-coding-chain-packet-structure-time-on-air-and-limits)
- What bit rate does SF7/125 kHz give? → [lora-phy-css-math § Level 1](lora-phy-css-math.md#level-1--definitions-and-rates)
- Why does LoRa work below the noise floor? → [lora-phy-css-math § Level 2](lora-phy-css-math.md#level-2--the-waveform-de-chirping-and-orthogonality)
- Is "−147 dBm at 2.4 kbps" real? → [lora-sensitivity-and-link-budget § Level 3](lora-sensitivity-and-link-budget.md#level-3--system-noise-external-noise-and-modules-with-lnas)
- How far will my E22/E220 reach from a rocket? → [lora-sensitivity-and-link-budget § Worked examples](lora-sensitivity-and-link-budget.md#worked-examples)
- Why do we lose the rocket after landing? → [lora-sensitivity-and-link-budget § Worked example 4](lora-sensitivity-and-link-budget.md#worked-examples)
- Does Doppler break LoRa on a Mach 3 rocket? → [lora-impairments-doppler-drift-timing § TL;DR](lora-impairments-doppler-drift-timing.md#tldr)
- Which SF survives a 10–20 g boost? → [lora-impairments-doppler-drift-timing § Level 2](lora-impairments-doppler-drift-timing.md#level-2--what-a-frequency-error-does-to-the-de-chirped-spectrum)
- Do I need a TCXO? → [lora-impairments-doppler-drift-timing § Worked example 1](lora-impairments-doppler-drift-timing.md#worked-examples)
- What SF/BW is EBYTE's "air data rate"? → [lora-modules-ebyte-rfm-heltec § Level 2](lora-modules-ebyte-rfm-heltec.md#level-2--how-the-uart-modules-behave)
- Is my 2 W 433 MHz radio legal in Singapore? → [ism-band-plans-duty-cycle § TL;DR](ism-band-plans-duty-cycle.md#tldr) (legal detail → domain 19)
- How often may I transmit under 1 % duty? → [ism-band-plans-duty-cycle § Level 2](ism-band-plans-duty-cycle.md#level-2--duty-cycle-and-dwell)
- LLCC68 vs SX1262 vs SX1268? → [semtech-chip-family § Level 1](semtech-chip-family.md#level-1--key-specifications)
- Which SX126x errata must my driver handle? → [semtech-chip-family § Level 3](semtech-chip-family.md#level-3--sx126x-known-limitations-errata-and-their-fixes)
- How should I design telemetry packets? → [rocket-telemetry-radio-design § Practical notes](rocket-telemetry-radio-design.md#practical-notes)
- Where should the ground station stand? → [rocket-telemetry-radio-design § Worked example 2](rocket-telemetry-radio-design.md#worked-examples)
- LNA before or after the SAW filter? → [ground-station-design § Level 1](ground-station-design.md#level-1--cascade-noise-figure-and-sensitivity)
- When is FSK better than LoRa? → [other-ism-radios-fsk-2g4 § Design equations](other-ism-radios-fsk-2g4.md#design-equations--rules-of-thumb)
- Can I use TTN/LoRaWAN for rocket telemetry? → [lorawan-vs-raw-lora § TL;DR](lorawan-vs-raw-lora.md#tldr)
- Will a higher-dBi antenna give my node more range? Is a high-gain omni good for a rocket? → [choosing-and-judging-lora-antennas § Level 1](choosing-and-judging-lora-antennas.md#level-1--gain-elevation-and-mismatch)
- Is this "10 dBi" antenna real? How do I compare two antennas? → [choosing-and-judging-lora-antennas § Level 2](choosing-and-judging-lora-antennas.md#level-2--why-gain-needs-length-and-how-to-test-two-antennas)
- Meshtastic shows a node 500 km away — is that RF range? → [lora-sensitivity-and-link-budget § Common mistakes](lora-sensitivity-and-link-budget.md#common-mistakes--misconceptions) (MQTT bridging, `via_mqtt`)

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
- Semtech SX1276/77/78/79 (Rev 7) and SX1261/2 (Rev 1.2/2.2) datasheets; SX1280 (Rev 3.0); AN1200.14.
- Vangelista 2017 (IEEE SPL); Tapparel et al. 2020 (SPAWC, gr-lora_sdr); Bor et al. 2016 (MSWiM); Croce et al. 2018 (IEEE CL); Elshabrawy & Robert 2018; Maleki et al. 2023 tutorial.
- IMDA TS SRD Issue 1 Rev 3 (Sep 2023) + the Exemption Notification; Decision (EU) 2025/105 (and ETSI EN 300 220-2 V3.2.1); 47 CFR §15.247 and §97.303(n)(2); ACMA LIPD 2025; LoRa Alliance RP002-1.0.3. Legal interpretation lives in [19-regulations-safety](../19-regulations-safety/_index.md).
- EBYTE E22-400TXXX datasheet; E220-900T30D manual; Altus Metrum AltOS telemetry; Featherweight GPS tracker manual.

## Known gaps
- EBYTE air-data-rate → SF/BW/CR mapping, sync word and framing: unknown (SDR measurement procedure given).
- No real rocket-flight LoRa PER-vs-acceleration data; Doroshkin 2019 / Norby 2022 thresholds not read first-hand.
- Semtech's Freq_drift_max equation reconstructed from quoted numbers (BW/(3·2^SF)).
- LR11xx / LR2021 / LLCC68 full datasheets, SX127x errata, AN1200.37/AN1200.59 not read.
- Legal interpretation of IMDA classes for rocket telemetry and licence routes → resolved in [19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md) (amateur 430–440 MHz ≤ 10 W ERP, temporary permit, experimental/localised licences; 866–869 MHz the best licence-exempt band); remaining ambiguities (30b vs 30c; 'tracking, tracing and data acquisition') need IMDA's written view.
- Singapore urban man-made noise and 900 MHz cellular adjacency not measured.
- University-team telemetry survey (USC RPL, BU, DARE, SEDS, EPFL) only at anecdotal level.
