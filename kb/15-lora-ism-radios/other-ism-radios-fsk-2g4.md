---
title: Other ISM radios — FSK/GFSK sub-GHz, SiK/RFD900x, XBee, 2.4 GHz (nRF, BLE coded, ESP-NOW LR, SX1280 FLRC) — and when they beat LoRa
domain: 15-lora-ism-radios
slug: other-ism-radios-fsk-2g4
tags: [fsk, gfsk, expresslrs, elrs, fhss-rc-link, image-transfer, bulk-data, codec2, halow, 802.11ah, fountain-code, cc1101, cc1310, cc1352, si4463, s2-lp, sik, rfd900x, xbee, nrf24l01, nrf52840, ble-coded-phy, esp-now, flrc, sx1280, telemetry]
prerequisites:
  - lora-sensitivity-and-link-budget.md
  - ../10-comms-modulation/digital-modulation-psk-qam-fsk.md
  - ../10-comms-modulation/ber-ebn0-and-shannon.md
related:
  - semtech-chip-family.md
  - ground-station-design.md
  - ../14-sdr-dsp/signal-identification-and-spectrum-survey.md
  - ../12-phased-arrays/adaptive-beamforming-doa.md
  - rocket-telemetry-radio-design.md
  - ism-band-plans-duty-cycle.md
  - ../10-comms-modulation/spread-spectrum-dsss-fhss-css.md
  - ../18-components-parts/rf-transceiver-ics.md
level: intermediate
confidence: medium
last_updated: 2026-10-12
---

# Other ISM radios — and when they beat LoRa

## Questions this page answers
- How does LoRa compare with plain FSK/GFSK radios (CC1101, Si4463, SX126x FSK) at the same data rate?
- What are SiK/RFD900x telemetry radios, and why do UAV and rocketry people use them?
- Is an XBee-PRO 900HP better than LoRa?
- What can 2.4 GHz options (nRF24L01+, nRF52840 BLE long range, ESP-NOW LR, SX1280 FLRC) do?
- When should I choose FSK over LoRa for rocket telemetry?
- How does ExpressLRS work (packet rates, hopping, telemetry ratio), and are its range claims believable?
- How do I recognise an ExpressLRS or drone link, or a jammer, on an SDR waterfall?
- Can I send a camera image or voice from a rocket over LoRa, and how long does a 600 kB photo take?
- What is Wi-Fi HaLow (802.11ah), and is it better than LoRa for images?

## TL;DR
- **Figure of merit** $FOM = S - 10\log_{10}R_b + 174 = NF + E_b/N_0$ (lower = better), from datasheets (`tools/verify/lora_ism_compare.py`): **LoRa ≈ 12.5–13.6 dB** (SX1262/LLCC68, any SF); SX1280 FLRC 15–17 dB; SX1262 GFSK 16–19 dB; Si4463 GFSK 18–21 dB; RFD900x 21–26 dB; XBee-PRO 900HP 20–24 dB; nRF52840 BLE (incl. coded PHY) 19–20 dB; CC1101 24–30 dB; nRF24L01+ 26–29 dB. At equal bit rate LoRa is **~4–15 dB more sensitive** than typical FSK radios.
- But **FSK wins on rate, latency and drift tolerance**: 38.4–500 kb/s (vs LoRa's 5–22 kb/s at usable SFs), millisecond packets, short symbols that don't care about Doppler rate, mature hardware FEC/FHSS radios, FCC-certified hopping modems.
- **SiK** (3DR/HM-TRP, Si1000 + Si4432): FHSS + adaptive TDM, 433/900 MHz, up to 250 kb/s air rate, ≤ 20 dBm, "−121 dBm", ECC correcting up to 25 % bit errors, MAVLink-aware, LBT/AFA options [1]. **RFD900x**: 902–928 (or 865–870) MHz, FHSS, 0–30 dBm, 12–750 kb/s air rates, dual-antenna diversity, AES, **−111 dBm at 12 kb/s (1e-5 BER)**, 1 A TX peak, 60 mA RX [2].
- **XBee-PRO 900HP**: 902–928 MHz FHSS (25 of 64 channels), 24 dBm, −110 dBm at 10 kb/s, −101 dBm at 200 kb/s [3]; used by Stanford SSI in 2017 SAC but limited to ~10 km with omni dipoles (anecdotal) [4].
- **Altus Metrum** uses TI CC11xx/CC1200 GFSK at 38.4 kbaud with rate-½ convolutional FEC in the 70 cm amateur band [5] — the canonical FSK rocketry downlink.
- **ExpressLRS** (open-source RC link; [section](#expresslrs-class-links)) runs LoRa SF5–9 at 500/800 kHz, FLRC or GFSK at **fixed packet rates** (25–1000 Hz) with 8-byte packets, channel occupancy of 75–93 %, a hop every 2–4 packets (12.5–500 hops/s) and telemetry in 1 of every N packets. Its "40 km at 250 Hz, 100 mW, omni antennas" claim is the **zero-margin** free-space range (39 km with 2 dBi at both ends); with 10 dB of margin it is 12 km.
- **Bulk data** ([section](#bulk-data-images-and-voice)): under the Singapore licence-exempt limits a 600 kB image takes ≈ 51 min at 433 MHz (LoRa SF7/500, 10 % duty), ≈ 7 min at 866–869 MHz (no duty stated), ≈ 8.5 h at 917–925 MHz (1 % duty), but 38 s with GFSK 250 kb/s at 866–869 MHz and 29 s with SX1280 FLRC at 2.4 GHz near the pad. Send thumbnails (≈ 10 kB) in flight and full images after recovery. Codec2 voice at 450–1300 b/s fits a 433 MHz exempt duty only at SF7/500.
- **2.4 GHz** costs 15 dB of free-space path loss vs 433 MHz for equal antenna gains; useful for high rate (SX1280 FLRC 1.3 Mb/s; LoRa 1625 kHz 71–202 kb/s), ranging (SX1280), or short-range pad links — not for 30 km at low power.

## Intuition (no math)
Every digital radio pays for bits with energy: to deliver one bit reliably it needs a certain energy per bit relative to the noise density ($E_b/N_0$), plus whatever its receiver noise figure wastes. FSK radios are simple and fast but need more energy per bit; LoRa spends time to reach low $E_b/N_0$ with a very tolerant receiver. If you have more transmit power, antenna gain and geometry than you need (typical in-flight rocket links), FSK's faster, shorter packets are worth more than LoRa's extra sensitivity. If you are sensitivity-limited (landed rocket, low power, long range), LoRa wins.

## The math
### Level 1 — normalising sensitivity
For any receiver, $S = -174 + 10\log_{10}R_b + NF + E_b/N_0$ (at its specified error rate), so $FOM \equiv S - 10\log_{10}R_b + 174$ collects the radio's noise figure, required $E_b/N_0$ and any receiver-filter inefficiency. Table from `lora_ism_compare.py` (test conditions differ — PER 1 %, BER 0.1 % or 1e-5 — so treat ±2 dB as noise):

| Radio / mode | S (dBm) | $R_b$ | FOM (dB) | S scaled to 20 kb/s |
|---|---|---|---|---|
| SX1262 LoRa SF12/125 | −137 | 244 | 13.1 | −117.9 |
| SX1262 LoRa SF7/500 | −117 | 21 875 | 13.6 | −117.4 |
| SX1262 GFSK 250 kb/s | −104 | 250 000 | 16.0 | −115.0 |
| Si4463 GFSK 40 kb/s | −110 | 40 000 | 18.0 | −113.0 |
| SX1280 FLRC 650 kb/s | −100.5 | 650 000 | 15.4 | −115.6 |
| nRF52840 BLE coded 125 kb/s | −103 | 125 000 | 20.0 | −111.0 |
| XBee-PRO 900HP 200 kb/s | −101 | 200 000 | 20.0 | −111.0 |
| RFD900x 64 kb/s | −105 | 64 000 | 20.9 | −110.1 |
| CC1101 GFSK 38.4 kBaud | −104 | 38 400 | 24.2 | −106.8 |
| nRF24L01+ 2 Mb/s | −82 | 2 000 000 | 29.0 | −102.0 |

### Level 2 — why LoRa's FOM is ~13 dB and FSK's ~16–25 dB
Non-coherent binary FSK needs $E_b/N_0 \approx 13.4$ dB for BER $10^{-5}$ (and ~11 dB for $10^{-3}$) ([BER & Shannon](../10-comms-modulation/ber-ebn0-and-shannon.md)); with NF ≈ 5–6 dB that predicts FOM ≈ 16–19 dB — what the good FSK chips achieve (SX1262 GFSK, Si4463). LoRa is $M$-ary orthogonal signalling with $M = 2^{SF}$; its $E_b/N_0$ requirement falls with $\log_2 M$ bits per symbol, to ≈ 6 dB at 1 % PER ([sensitivity page](lora-sensitivity-and-link-budget.md)), hence FOM ≈ 12–13 dB. Coded FSK (convolutional/LDPC, as AltOS, CC1200 FEC, FLRC) recovers 3–6 dB of the gap. Radios with FOM > 22 dB (CC1101 at low rates, nRF24L01+) waste energy in wide receive filters relative to the bit rate or in simple demodulators.

### Level 3 — FHSS radios and regulation
SiK/RFD900x and XBee-900HP hop over many channels to satisfy FCC §15.247 at up to 1 W (US) ([band plans](ism-band-plans-duty-cycle.md)) and to average out narrowband interference and frequency-selective fades; adaptive TDM (SiK) schedules both directions without collisions [1]. LoRa-based systems can hop too (LoRaWAN US915, LR-FHSS), but a UART LoRa module can't. For a *licensed* amateur 70 cm link (AltOS), no hopping is required.

## Design equations & rules of thumb
| Question | Answer |
|---|---|
| Need > 30 kb/s continuous? | FSK/GFSK, FLRC, RFD900x |
| Need < 20 ms packets / low latency? | FSK or LoRa SF5–7 at 500 kHz |
| Sensitivity-limited (landed, legal low power)? | LoRa |
| Strong acceleration + long packets? | FSK (short symbols) or LoRa SF ≤ 8 |
| US FCC compliance without your own certification? | certified FHSS modem (RFD900x, XBee) |
| 2.4 GHz for range? | only with high-gain antennas; +15 dB path loss vs 433 MHz |
| Two-way MAVLink-style link | SiK/RFD900x (TDM built in) |

## Worked examples
**1. 40-byte frames at 20 Hz.** 6.4 kb/s of payload. LoRa SF7/500 (21.9 kb/s nominal): 20.5 ms/frame → 41 % occupancy, sensitivity −117 dBm. Si4463 at 40 kb/s: ~8 ms of payload per frame + preamble/sync (~2–3 ms) → ~20 % occupancy, −110 dBm. RFD900x at 64 kb/s: −105 dBm. With 30 km slant range at 433 MHz (FSPL 115 dB), 20 dBm + 0 dBi + 10 dBi gives −85 dBm received — **all three close with 20–30 dB margin**; FSK buys headroom for more data or redundancy, LoRa buys margin for nulls.
**2. Legal-power Singapore 433 MHz link (10 mW e.r.p.).** Received at 30 km with 10 dBi Yagi: 12.15 − 115 + 10 ≈ −93 dBm. Si4463 at 40 kb/s (−110 dBm) has 17 dB margin; LoRa SF9/125 (−129.5 dBm) has 36 dB. In a 16 dB tail null, FSK is down to 1 dB; LoRa still has 20 dB — here LoRa's sensitivity matters.
**3. 2.4 GHz pad/ascent link with SX1280 FLRC at 650 kb/s.** +12.5 dBm, 2 dBi each end, −100.5 dBm sensitivity → MAPL 117 dB → free-space range ≈ 7 km. Good for high-rate video/sensor bursts near the pad, not for 30 km.

## Practical notes
- **TI CC1101** (300–348, 387–464, 779–928 MHz; up to 500 kBaud; +12 dBm; −116 dBm at 0.6 kBaud/433 MHz; saturation −14 dBm) [6] is the classic cheap sub-GHz FSK chip; **CC1310/CC1312** add a Cortex-M3/M4 and a long-range mode (−124 dBm at 625 b/s, needs a TCXO); **CC1352P** adds +20 dBm and BLE (−121 dBm SimpleLink long range, −105 dBm BLE coded) [7] (vendor/search-level).
- **Si4463/64** (119–1050 MHz, +20 dBm at 85 mA/915 MHz, −126 dBm at 500 b/s, 4GFSK up to 1 Mb/s, 64-byte FIFOs) [8] — a strong, flexible FSK choice; ST's S2-LP is comparable (not researched here).
- **Nordic nRF52840**: BLE 5 coded PHY 125 kb/s at −103 dBm, 1 Mb/s at −95 dBm, +8 dBm (+21 dBm with nRF21540 FEM) [9]; **nRF24L01+**: 0 dBm, −94 dBm at 250 kb/s, −82 dBm at 2 Mb/s [10] — short-range only.
- **ESP-NOW / ESP32 LR mode**: Espressif's proprietary 802.11 long-range mode at 256/512 kb/s, ~1 km LOS claims with PCB antennas (vendor/forum-level) [11] — handy for pad-side links between ESP32 boards, not for flight downlinks.
- **SX1262 FSK mode**: the LoRa chips you already use also do GFSK up to 300 kb/s (−104 dBm at 250 kb/s) [12] — a bare-chip design can switch between LoRa (range) and GFSK (rate) per flight phase with the same hardware.

## ExpressLRS-class links

ExpressLRS (ELRS) is a community open-source radio-control link for drones and planes. It runs on SX127x (900 MHz), SX1280 (2.4 GHz) and LR1121/LR2021 (both bands) hardware. Its design choices make it a useful template for hopped, fixed-rate rocket telemetry. Mode data below are re-typed from the ELRS source tables (`ExpressLRS_AirRateConfig` / `AirRateRFperf`) [14]; arithmetic is from `tools/verify/s1_elrs_link.py`.

### Level 1 — the modes
| Band / chip | Mode | Modulation | Packet interval | Hop every | Sensitivity [14] | ELRS air time |
|---|---|---|---|---|---|---|
| 900 MHz SX127x | 200 Hz | LoRa SF6/500 kHz, CR 4/7, 8-symbol preamble | 5 ms | 4 packets | −112 dBm | 4.38 ms |
| | 100 Hz | SF7/500 | 10 ms | 4 | −117 dBm | 8.77 ms |
| | 50 Hz | SF8/500, 10-symbol preamble | 20 ms | 4 | −120 dBm | 18.56 ms |
| | 25 Hz | SF9/500, 10-symbol preamble | 40 ms | 2 | −123 dBm | 29.95 ms |
| 2.4 GHz SX1280 | 500 Hz | LoRa SF5/800 kHz, CR 4/6 (LI) | 2 ms | 4 | −105 dBm | 1.51 ms |
| | 250 Hz | SF6/800 | 4 ms | 4 | −108 dBm | 3.30 ms |
| | 150 Hz | SF7/800 | 6.67 ms | 4 | −112 dBm | 5.87 ms |
| | 50 Hz | SF8/800 | 20 ms | 2 | −115 dBm | 10.80 ms |
| | F1000 / F500 | FLRC 650 kb/s, BT 1, CR ½ | 1 / 2 ms | 2 | −104 dBm | 0.39 ms |
| LR1121 900 MHz | K1000 | GFSK 300 kb/s | 1 ms | 2 | −101 dBm | 0.66 ms |

Every packet is **8 bytes** (13 bytes in the 8/12/16-channel "full-resolution" modes) with implicit header. ELRS carries its own CRC (14- or 16-bit) inside the packet and turns the LoRa CRC off [14]. The FHSS channel plans are FCC915 (40 channels, 903.5–926.9 MHz), AU915 (20), EU868 (13, 863.275–869.575 MHz), EU433/AU433 (3), US433 (8), TH920 (8, 920.5–924.7 MHz) and ISM2G4 (80, 2400.4–2479.4 MHz). The hop sequence is pseudo-random, built from the binding-phrase seed, and the **sync channel** (the middle of the list) recurs once per pass [14]. "Telemetry ratio 1:N" means that 1 of every N packets is sent from the receiver back to the transmitter [15].

### Level 2 — the arithmetic
- **Air time**: the SX127x ToA formula with implicit header and no CRC reproduces ELRS's own figures within 4 µs: 4384 vs 4380 µs (200 Hz), 29 952 vs 29 950 µs (25 Hz) (script). Channel occupancy is therefore **75–93 %**. ELRS fills the air on purpose, which only an FHSS duty-cycle regime (or a licence) permits.
- **Hopping**: hop rate = packet rate / hop interval, i.e. 50 hops/s at 200 Hz, 12.5 at 25 Hz, 125 at 2.4 GHz 500 Hz and 500 at F1000. Dwell per channel is 20–80 ms. One pass through the 40-channel FCC915 plan takes 0.8 s at 200 Hz. A narrowband interferer therefore costs 1/40 of the packets, rather than all of them as on a fixed channel.
- **Telemetry**: at 200 Hz and 1:64 there are 3.1 downlink packets/s of a few bytes each. ELRS's defaults give about 3 telemetry packets/s at every rate (1:64 at 200 Hz, 1:16 at 50 Hz, 1:8 at 25 Hz).
- **Range claim**: the docs claim over 40 km at 250 Hz, 100 mW, with omni antennas, in clear line of sight [15]. MAPL = 20 + 2 + 2 + 108 = 132 dB, which is 39 km in free space at 2.44 GHz with **zero margin**, 12 km with 10 dB margin and 25 km with 0 dBi antennas. The claim is consistent with physics only in ideal line of sight with no fade margin; budget 10–15 dB for a real link ([link budget](lora-sensitivity-and-link-budget.md)). At 900 MHz (25 Hz, −123 dBm, 1 W) the zero-margin free-space range is 1800 km, so 900 MHz ranges are set by the horizon and terrain, not by power.

### Spotting ELRS/drone links and jammers on an SDR
- **ELRS 2.4 GHz**: a waterfall from 2.400–2.480 GHz shows short bursts (0.4–11 ms) every 1–20 ms, about 0.8 MHz wide (LoRa) or 0.6 MHz (FLRC), hopping over 80 channels 1 MHz apart. A LoRa burst de-chirps cleanly at BW 812.5 kHz; FLRC looks like a GFSK block. Plain Wi-Fi occupies 20 MHz blocks. Classic Bluetooth hops 1 MHz channels at up to 1600 hops/s, and BLE uses 2 MHz channels, hopping once per connection event.
- **ELRS 900 MHz**: bursts 500 kHz wide, 4–30 ms long, on a 600 kHz grid from 903.5 to 926.9 MHz (FCC915), at a perfectly regular cadence of 5, 10, 20 or 40 ms. Any regular cadence plus chirps means LoRa-based RC; LoRaWAN instead has irregular uplinks on fixed channels.
- **Jammer**: a continuous wideband rise in the noise floor, a swept CW line ("sawtooth" in the waterfall), or a barrage over the whole band, with no packet structure. Measure duty and bandwidth ([signal identification](../14-sdr-dsp/signal-identification-and-spectrum-survey.md)) and find it with [direction finding](../12-phased-arrays/adaptive-beamforming-doa.md#practical-direction-finding-for-rocket-recovery). A continuous source suits pseudo-Doppler and Watson–Watt units.

### The analogue for hopped rocket telemetry
A rocket link that copies ELRS's pattern would use a fixed frame schedule, a hop every N frames along a seeded sequence, a known sync channel for re-acquisition after a fade, and its own short CRC. The design questions it raises are these.
1. **The ground receiver must stay in lock through nulls.** After a missed packet ELRS keeps hopping on its timing, and it falls back to the sync channel after a disconnect timeout. A rocket ground station should do the same, plus an SDR that records the whole band ([ground station](ground-station-design.md)).
2. **Doppler rate and drift are no worse than with a fixed channel**, because the hop is fast compared with the dynamics. The frequency error must still stay within the bin tolerance ([impairments](lora-impairments-doppler-drift-timing.md)).
3. **Regulation is per band, not per channel.** The 433.05–434.79 MHz SRD band holds only three 500 kHz channels (ELRS's EU433 plan) and is still capped at 10 mW e.r.p. and 10 % duty in Singapore. ELRS's TH920 plan (920.5–924.7 MHz) sits inside Singapore's 917–925 MHz band, but whether an FHSS RC/telemetry link is a "non-specific SRD" (30d, 100 mW e.r.p.) or an LPWAN device (1 % duty) is an interpretation to confirm with IMDA ([19](../19-regulations-safety/singapore-imda-rules.md)). ELRS's 75–93 % occupancy is not licence-exempt under a 1 % or 10 % rule.

## Bulk data: images and voice

### Level 1 — the delivery-time arithmetic
A 600 kB image is 4.8 Mbit. Its delivery time is
$$T = \frac{8\,S_{image}}{R_{good}},\qquad R_{good} = \frac{8\,P_{frag}\cdot (k/n)\cdot \min(d,\,0.7)}{T_{packet}(P_{frag}+H)}$$
with $P_{frag}$ = 200 B of image per fragment, an 8 B fragment header (image id, index, count), erasure FEC at code rate $k/n$ = 0.8, legal duty cycle $d$, a 0.7 ceiling for turnaround gaps, and $T_{packet}$ the air time of one 208-byte packet. `tools/verify/s1_image_throughput.py` evaluates it under the Singapore licence-exempt limits. It assumes a ground-station NF of 1.8 dB and 13 dB margin. Free-space range is for flight; "landed" means a flat-earth two-ray path with a 0.1 m rocket antenna and a 5 m mast.

| Band (SG licence-exempt) | Mode | Packet | Goodput | 10 kB | 50 kB | 600 kB | Range: free space / landed |
|---|---|---|---|---|---|---|---|
| 433 MHz, 10 mW e.r.p., 10 % | LoRa SF7/500 | 82 ms | 1.6 kb/s | 51 s | 4.3 min | 51 min | 270 km / 1.6 km |
| | LoRa SF9/125 | 1046 ms | 0.12 kb/s | 11 min | 54 min | 11 h | 960 km / 3.0 km |
| | GFSK 250 kb/s | 7 ms | 18 kb/s | 4 s | 22 s | 4.4 min | 51 km / 0.7 km |
| 866–869 MHz, 500 mW e.r.p., no duty stated | LoRa SF7/500 | 82 ms | 10.9 kb/s | 7 s | 37 s | 7.3 min | 960 km / 4.2 km |
| | GFSK 250 kb/s | 7 ms | 128 kb/s | 0.6 s | 3 s | 38 s | 180 km / 1.8 km |
| | HaLow 1 MHz MCS10 (estimate) | 22 ms | 40 kb/s | 2 s | 10 s | 2 min | 230 km / 2.0 km |
| 917–925 MHz LPWAN, 100 mW e.r.p., 1 % | LoRa SF7/500 | 82 ms | 0.16 kb/s | 8.5 min | 43 min | 8.5 h | 400 km / 2.8 km |
| | GFSK 250 kb/s | 7 ms | 1.8 kb/s | 44 s | 3.7 min | 44 min | 76 km / 1.2 km |
| 2.4 GHz, 100 mW e.i.r.p. | SX1280 FLRC 325 kb/s | 5.4 ms | 166 kb/s | 0.5 s | 2.4 s | 29 s | 27 km / 1.2 km |
| | SX1280 LoRa SF7/1625 | 25 ms | 36 kb/s | 2 s | 11 s | 2.3 min | 83 km / 2.1 km |

Reading the table:
- **Duty cycle, not modulation, is the first limit.** The same SF7/500 mode is 7× faster at 866–869 MHz than at 433 MHz and 70× faster than at 917–925 MHz. Under a licence (no SRD duty rule) the 433 MHz row improves by the same 7× ([band plans](ism-band-plans-duty-cycle.md)).
- **Rate trades against landed range.** In the two-ray regime range grows only as the fourth root of the link budget, so a 25 dB faster mode loses about 4× in range.
- **Practical plan**: in flight, send ≈ 10 kB thumbnails (or JPEG low-resolution scans) interleaved with telemetry, keeping telemetry first. Store full images on board. Transfer full images after recovery over USB or Wi-Fi, or on the pad with FLRC/GFSK at short range. At 2.4 GHz the 100 mW e.i.r.p. class (32d) requires a sharing mechanism (LBT/DAA); otherwise the limit is 10 mW, 10 dB less ([19](../19-regulations-safety/singapore-imda-rules.md)).

### Level 2 — fragmentation, FEC and ARQ
- **Fragmentation**: the radio's maximum payload is 255 B on SX126x, 240 B on the E22 and 200 B on the E220. Each fragment needs an image id, its index and the total count. The header is 4 % of a 200-byte fragment, but the preamble and sync add a fixed air time per packet (12.25 symbols for LoRa), which favours large fragments at high SF.
- **Packet-level erasure FEC**: a rocket downlink is an erasure channel ([rocket telemetry Level 3](rocket-telemetry-radio-design.md)). With systematic Reed–Solomon over fragments, or a fountain code (LT/RaptorQ), any $k$ of $n$ received fragments rebuild a block. Choose $n/k$ above $1/(1-p)$ for loss rate $p$; for example, rate 0.8 survives 20 % loss with no return channel. Interleave blocks over a time longer than a roll null or plume outage.
- **ARQ** (selective repeat with a bitmap of missing fragments) is more efficient when an uplink exists. However, the uplink is the weaker direction ([ground station § asymmetry](ground-station-design.md#link-asymmetry-and-receiver-overload-near-the-pad)), and each request costs a TX/RX turnaround and duty cycle. A hybrid (FEC for the bulk, one NACK round after recovery) is the usual compromise.
- **HaLow (IEEE 802.11ah)** is Wi-Fi in sub-GHz bands. Secondary sources give Singapore channels in 866–869 MHz and 920–925 MHz [16]. In a 1 MHz channel its most robust mode (MCS10: BPSK, rate ½, two-fold repetition) is 150 kb/s PHY [16]. Sensitivity in the table is an estimate. It brings IP networking and ARQ, but it needs association and two-way traffic, so a tumbling rocket at range is a poor client. It is better suited to a pad-to-control-tent link.

### Voice
Codec2 encodes speech at 3200, 2400, 1600, 1400, 1300, 1200, 700 and 450 b/s [17]. In 400 ms frames the occupancy on LoRa is: 1300 b/s (69 B) 32 % at SF7/125, 8 % at SF7/500, and over 100 % at SF9/125; 700 b/s (39 B) 21 % at SF7/125 and 5 % at SF7/500. Only SF7/500 fits the 433 MHz licence-exempt 10 % duty. Voice for the recovery team is better carried by licensed amateur handhelds or PMR-class radios than by the telemetry link.

## Common mistakes & misconceptions
- **"ExpressLRS gets 40 km, so my rocket link will too."** That figure has zero fade margin and ideal line of sight. Rocket links need 10–15 dB of margin for nulls.
- **Copying ELRS's 80–90 % channel occupancy into a licence-exempt band** that has a 1 % or 10 % duty rule.
- **"LoRa can stream images."** At licence-exempt duty cycles a 600 kB image takes from 7 minutes to 8.5 hours. Send thumbnails and store the full image.
- **Sending a file with no FEC and no plan for missing fragments** on a one-way link.
- **"LoRa has the best range, so it's the best telemetry radio."** In LOS flight, rate/latency/robustness usually matter more than the last 10 dB.
- **Comparing sensitivities without normalising bit rate** — a −126 dBm FSK spec at 500 b/s is not better than −117 dBm LoRa at 21.9 kb/s (FOM 21 vs 13.6).
- **Trusting "up to 40 km" marketing** without heights/antennas — same caveat as LoRa ([link budget](lora-sensitivity-and-link-budget.md)).
- **Choosing 2.4 GHz for a long link because "the chip is newer"** — 15 dB more path loss than 433 MHz for equal antenna gains.
- **RFD900x sensitivity figures differ by version** (see Open questions).

## How to simulate / verify
- `python3 tools/verify/lora_ism_compare.py` — FOM and rate-normalised sensitivity for every radio in the table; add your own.
- For any candidate, run the attenuator-ladder PER test at your frame length; datasheet test conditions (PER 1 % vs BER 1e-5) are not comparable.
- `python3 tools/verify/s1_elrs_link.py` (6 checks): ELRS air times vs `rfcalc.lora`, hop and telemetry arithmetic, range-claim budget.
- `python3 tools/verify/s1_image_throughput.py` (4 checks): the image-delivery table and Codec2 occupancy under the Singapore limits.

## Open questions / gaps
- RFD900x sensitivity: datasheet V1.2 table gives −111 dBm at 12 kb/s (BER 1e-5) [2], while distributor summaries quote "> −121 dBm at low data rates" (older firmware/air rates, e.g. 4 kb/s?) — unresolved.
- ST S2-LP, Semtech SX1231, and Microchip RN2483/RN2903 not covered.
- ESP32 LR mode figures are vendor/forum claims; CC1310/CC1352 from search summaries.
- HaLow Singapore channels (866–869 / 920–925 MHz) and the MCS10 150 kb/s figure come from secondary sources [16]; HaLow sensitivity is estimated, not sourced; whether IMDA classes HaLow under TS SRD 29/30b is not confirmed.
- ELRS mode data are from the GitHub master branch as read on 2026-10-03; they change between releases.
- The SiK ECC is described as correcting "up to 25 % of bit errors" [1] — the code (believed Golay (24,12)) is not confirmed here.

## Sources
1. ArduPilot docs, "SiK Telemetry Radio" (accessed 2026-09-27) — FHSS, adaptive TDM, 433/900 MHz, ≤ 250 kb/s air rate, 20 dBm, −121 dBm, ECC up to 25 % bit errors, MAVLink framing, LBT/AFA, HM-TRP (Si1000 + Si4432). https://ardupilot.org/copter/docs/common-sik-telemetry-radio.html (project docs)
2. RFDesign, *RFD900x DataSheet* V1.2 — 902–928/865–870 MHz, 12–750 kb/s, 0–30 dBm, sensitivity table (−111 @ 12 kb/s … −94 @ 224 kb/s, 1e-5 BER), 1 A TX peak, 60 mA RX, dual RPSMA diversity, AES, US 51 channels. https://files.rfdesign.com.au/Files/documents/RFD900x%20DataSheet%20V1.2.pdf (datasheet)
3. Digi, *XBee-PRO 900HP* datasheet (via search summary) — 24 dBm, −110 dBm @ 10 kb/s, −101 dBm @ 200 kb/s, 25 of 64 hop channels. (datasheet — not read in full)
4. Spaceport America Cup / Stanford SSI 2017 notes (search summary) — XBee-900HP limited to ~10 km with omni dipoles. (anecdotal)
5. Altus Metrum, *AltOS Telemetry* documentation (2025). https://altusmetrum.org/AltOS/doc/telemetry.html (vendor docs)
6. Texas Instruments, *CC1101 Low-Power Sub-1 GHz RF Transceiver*, SWRS061I — bands, data rate 0.6–500 kBaud, sensitivity tables (433: −116 @ 0.6k, −112 @ 1.2k, −104 @ 38.4k, −95 @ 250k), saturation −14 dBm, +12 dBm. https://www.ti.com/lit/ds/symlink/cc1101.pdf (datasheet)
7. TI CC1310 / CC1352P product information (search summaries) — long-range mode −124 dBm (CC1310), +20 dBm and −121/−105 dBm (CC1352P). (vendor — not read in full)
8. Silicon Labs, *Si4464/63/61/60 datasheet* Rev 1.4 — 119–1050 MHz, +20 dBm (85 mA @ 915 MHz), RX sensitivity −126 dBm @ 500 b/s … −97 dBm @ 500 kb/s, 4GFSK −88 dBm @ 1 Mb/s. https://www.silabs.com/documents/public/data-sheets/Si4464-63-61-60.pdf (datasheet)
9. Nordic Semiconductor, nRF52840 product page and Product Specification (via search summary) — +8 dBm, −95 dBm @ 1 Mb/s, −103 dBm @ 125 kb/s coded. (datasheet)
10. Nordic Semiconductor, *nRF24L01+ Product Specification* v1.0 (via search summary) — −82/−85/−94 dBm at 2 M/1 M/250 kb/s; 0 dBm. (datasheet)
11. Espressif ESP32 LR mode (community summaries; Espressif docs moved) — 256/512 kb/s, ~1 km LOS. (forum — anecdotal)
12. Semtech, *SX1261/2 Datasheet* Rev 1.2, Table 3-8 — GFSK sensitivities (−118 @ 4.8 kb/s, −104 @ 250 kb/s). (datasheet)
13. Semtech, *SX1280/81/82 Datasheet* Rev 3.0 — FLRC and 2.4 GHz LoRa sensitivities. (datasheet)
14. ExpressLRS project, source code (GitHub `ExpressLRS/ExpressLRS`, master, read 2026-10-03): `src/src/common.cpp` (ExpressLRS_AirRateConfig, AirRateRFperf: SF/BW/CR, preamble, hop interval, packet interval, sensitivity, TOA), `src/lib/FHSS/FHSS.cpp` (regulatory-domain channel plans, sync channel), `src/lib/OTA/OTA.h` (8/13-byte packets, CRC14/CRC16). https://github.com/ExpressLRS/ExpressLRS (community project — code)
15. ExpressLRS documentation, "Signal Health" and "Lua script" pages, https://www.expresslrs.org (accessed 2026-10-03) — packet-rate/sensitivity table, "over 40 km at 250 Hz 100 mW" claim, telemetry ratio 1:N, power 10–2000 mW. (community project docs)
16. Argenox, "Introduction to Wi-Fi 802.11ah HaLow" and Hackaday (2016) — Singapore 866–869 / 920–925 MHz, 1 MHz MCS10 150 kb/s. (secondary — unverified against IEEE 802.11ah / IMDA)
17. D. Rowe et al., *Codec 2* open-source speech codec, README (github.com/drowe67/codec2) — modes 3200…450 b/s. (project docs)
18. `tools/verify/s1_elrs_link.py`, `tools/verify/s1_image_throughput.py` — numbers in the ELRS and bulk-data sections. (own verification)
