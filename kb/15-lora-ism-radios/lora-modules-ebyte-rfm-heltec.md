---
title: LoRa modules — EBYTE E22/E220/E32/E19, HopeRF RFM9x, Heltec, RAK, Seeed, LilyGo
domain: 15-lora-ism-radios
slug: lora-modules-ebyte-rfm-heltec
tags: [lora, ebyte, e22-400t33d, e220-900t30d, e32, e19, rfm95, rfm96, heltec, rak4631, wio-e5, t-beam, uart-module, radiolib, air-data-rate]
prerequisites:
  - lora-phy-css-math.md
  - semtech-chip-family.md
related:
  - lora-sensitivity-and-link-budget.md
  - lora-impairments-doppler-drift-timing.md
  - rocket-telemetry-radio-design.md
  - ground-station-design.md
  - ism-band-plans-duty-cycle.md
  - ../18-components-parts/rf-modules.md
  - ../05-analog-electronics/power-supplies-for-rf-and-analog.md
  - ../13-pcb-rf-layout-emc/thermal-management-rf.md
level: intermediate
confidence: medium
last_updated: 2026-10-14
---

# LoRa modules — EBYTE E22/E220/E32/E19, HopeRF RFM9x, Heltec, RAK, Seeed, LilyGo

## Questions this page answers
- What is inside an EBYTE E22-400T33D and E220-900T30D, and what do the part-number letters mean?
- How do the EBYTE M0/M1 modes, AUX pin and configuration registers work?
- What SF/BW/CR does an EBYTE "air data rate" of 2.4k or 19.2k correspond to?
- How do I read RSSI from an EBYTE module, and what are LBT, WOR and the "encryption key"?
- How much current and heat does a 2 W module need, and what supply should I design?
- Can an EBYTE UART module talk to a bare SX1262 running RadioLib?
- Which dev boards (Heltec, RAK4631, T-Beam, Wio-E5, RFM95) use which chip?
- Should I use a UART module or a bare chip with my own firmware for the next flight computer?

## TL;DR
- **EBYTE naming**: E22 = SX1262 (900) or **SX1268 (400)**; E220 = **LLCC68**; E32 = SX1276/SX1278; E19 = SX127x SPI. **T** = UART module with EBYTE firmware; **M** = SPI (raw chip + PA/LNA). Suffix: 22/30/33 = dBm; S = SMD, D = DIP/SMA [1][2][3].
- **E22-400T33D**: SX1268, 410.125–493.125 MHz in 1 MHz channels ($f$ = 410.125 + CH MHz, default CH 0x17 = 433.125 MHz), 33 ± 0.5 dBm, PA + LNA, 3.3–5.5 V, **TX 850–1200 mA**, RX 11–15 mA, 37 × 60 mm, 25.9 g, 240-byte sub-packets, SMA [1]. **Singapore: it may radiate only under a licence** (amateur 430–440 MHz ≤ 10 W ERP with IMDA consent, a temporary permit or an experimental licence) — the licence-exempt limit at 433 MHz is **10 mW e.r.p.**, and even the module's lowest step (24 dBm) is 13.5 dB over [8][11].
- **E220-900T30D**: LLCC68, 850.125–930.125 MHz ($f$ = 850.125 + CH MHz, **default 873.125 MHz — not a legal Singapore channel**), 30 dBm, **≥ 5.0 V for full power**, TX 620 mA, RX 17.2 mA, 200-byte sub-packets, SMA [2].
- **Air data rate codes** (REG0 bits 2–0) are identical on E22 and E220: 000/001/010 = 2.4k (default), 011 = 4.8k, 100 = 9.6k, 101 = 19.2k, 110 = 38.4k, 111 = 62.5k [1][2]. **EBYTE does not publish the SF/BW/CR behind them**; only 62.5k is uniquely identifiable (= SF5/BW500/CR4/5 = 62 500 b/s exactly). Measure the rest with an SDR (procedure below).
- The **sensitivity claims** (−147/−148 dBm "at 2.4 kbps") are ~18 dB optimistic ([link budget](lora-sensitivity-and-link-budget.md)); the **"encryption key" is a 2-byte scrambling factor**, not cryptography [1].
- RSSI: enable the per-packet RSSI byte (REG3 bit 7) or read ambient noise (`C0 C1 C2 C3 00 01`); **dBm = −(256 − value)** [1][2].
- Dev boards: Heltec LoRa 32 V3 = ESP32-S3 + SX1262; RAK4631 = nRF52840 + SX1262; T-Beam S3 = ESP32-S3 + SX1262; Wio-E5 = STM32WLE5JC; RFM95W = SX1276-class 868/915, RFM96W/98W = 433/470 [4][5][6].
- For a **custom rocket radio**, a bare chip or an SPI module (E22-xxxM, RFM9x) driven by **RadioLib** gives SF/BW/CR/LDRO control, per-packet SNR and frequency-error readout, precise TX/RX timestamps and frequency agility — none of which the UART modules expose.

## Intuition (no math)
A UART LoRa module is a radio with a tiny computer bolted on. You hand it bytes over a serial port; its own microcontroller chops them into packets, chooses the LoRa settings from a short menu ("air data rate"), adds addressing, and sends them. It is quick to get working and hides all RF design, but it also hides everything you might want to tune or measure. A bare chip (or an SPI module, which is a bare chip plus the RF parts) gives you the steering wheel: you choose the exact modulation, can read the signal quality of every packet, and can time transmissions precisely — at the cost of writing the driver and, for a bare chip, doing the RF layout.

## The math
### Level 1 — part-number decoding and the specifications that matter
| Module | Chip | Band | P_out | Supply | TX / RX current | Interface | Notes |
|---|---|---|---|---|---|---|---|
| **E22-400T33D** | SX1268 | 410–493 MHz | 33 dBm | 3.3–5.5 V | 850–1200 / 11–15 mA | UART | Primary FC downlink [1] — **licensed use only in SG** (SRD limit 10 mW e.r.p.; lowest step 24 dBm) |
| E22-400T30D | SX1268 | 410–493 MHz | 30 dBm | 3.3–5.5 V | 610 / 16–17 mA | UART | [1] |
| E22-400T22D | SX1268 | 410–493 MHz | 22 dBm | 2.3–5.5 V | 110 / 11 mA | UART, no PA/LNA | [1] |
| **E220-900T30D** | LLCC68 | 850–930 MHz | 30 dBm | 3.0–5.5 V (≥ 5 V) | 620 / 17.2 mA | UART | Secondary FC downlink [2] — SG exempt only at CH 16–18 ≤ 24–27 dBm or CH 67–74 at 21 dBm (lowest step) plus a ≥ 1 dB pad or a ≤ 1.15 dBi antenna, ≤ 1 % duty |
| E220-400/900T22 | LLCC68 | 433/470 or 868/915 | 22 dBm | | | UART | [2] |
| E32-433T30D | SX1278 | 410–441 MHz | 30 dBm | 2.7–5.5 V | | UART, 0.3–19.2k air rates | older [3] |
| E22-xxxM30S / E19 | SX126x / SX127x | | 30 dBm | | | **SPI** (raw chip + PA/LNA) | RadioLib-compatible |
| HopeRF RFM95W / 96W / 98W | SX1276-class / SX1278 | 868/915; 433/470 | +20 dBm PA_BOOST | 1.8–3.7 V | ~120 mA @ +20 | SPI | [5] |

Air-data-rate codes (REG0 bits 2:0, E22 and E220) and the **arithmetic candidates** for the hidden LoRa settings, using $R_b = SF\cdot BW\cdot 2^{-SF}\cdot 4/5$ (the DE = 0 form of $(SF-2\,DE)\cdots$; none of these candidates needs LDRO; unverified — see Level 2):

| Code | EBYTE label | Candidate settings (nominal $R_b$) | LLCC68-legal? |
|---|---|---|---|
| 000/001/010 | 2.4k (default) | SF9/125 (1758), SF10/250 (1953), SF11/500 (2148) | all |
| 011 | 4.8k | SF7/125 (5469), SF8/250 (6250), SF9/500 (7031) | all |
| 100 | 9.6k | SF7/250 (10 938), SF8/500 (12 500) | all |
| 101 | 19.2k | SF7/500 (21 875) | yes |
| 110 | 38.4k | SF6/500 (37 500) | yes |
| 111 | 62.5k | **SF5/500 (62 500 — exact)** | yes |

Every 2.4k candidate has a sensitivity of about −129 to −130 dBm (NF 6 dB) — consistent with the LLCC68 floor and confirming that "−147 dBm at 2.4k" cannot be right.

### Level 2 — how the UART modules behave
**Modes** (E22/E220 manuals [1][2]): M1 M0 = 0 0 *normal* (UART ↔ air, transparent); 0 1 *WOR* (wake-on-radio: transmitter prepends a long wake-up preamble; receiver duty-cycles with period T = (1 + WOR)·500 ms, 0.5–4 s, both ends must match); 1 0 *configuration* (radio off; registers at **9600 8N1 only**); 1 1 *deep sleep* (~2 µA). (Older E32 manuals use a different mapping — check the manual for your series.)
**AUX pin**: low during power-on self-test, reconfiguration and while data is pending; wait for its rising edge before sending; mode changes take effect ~1 ms after AUX goes high [1]. Avionics C routes M0/M1/AUX to the MCU — keep it that way; strapping modes with jumpers only removes the ability to recover a misconfigured module in the field.
**Configuration commands** (in mode 2): `C0 addr len data…` write & save, `C2 …` write temporary, `C1 addr len` read; wireless configuration via `CF CF` prefix; `FF FF FF` = format error [1].
**Registers (E22)** [1]: 00H/01H module address (0xFFFF = broadcast/listen); 02H NETID; 03H REG0 = UART baud (bits 7–5, 1200…115200), parity (4–3), air rate (2–0); 04H REG1 = sub-packet length (7–6: 240/128/64/32 B), ambient-RSSI enable (5), TX power (1–0: 33/30/27/24 dBm on the T33); 05H channel; 06H REG3 = RSSI byte (7), fixed-point vs transparent (6), repeater (5), LBT (4), WOR role (3), WOR period (2–0); 07H/08H CRYPT key (write-only). E220 is the same layout with its own power table (30/27/24/21 dBm) and 200-byte maximum sub-packet [2].
**Transparent vs fixed transmission**: in transparent mode the UART bytes are the payload; in fixed mode the first three bytes (ADDH, ADDL, CH) select the target and channel [1].
**LBT**: listens before transmitting and waits up to **2 s**, then transmits anyway [1] — dangerous for deterministic flight telemetry (adds up to 2 s latency); keep it off on the rocket.
**Sub-packets**: data longer than the sub-packet length is split into several radio packets and re-assembled at the receiver's UART; the buffer is 1000 B (E22) / 400 B (E220) [1][2]. Each extra radio packet adds a full preamble + header. Write each telemetry frame as one burst ≤ the sub-packet size.
**RSSI**: per-packet byte appended after the payload on the RX UART, or register 0x00 (current noise) / 0x01 (last packet) via `C0 C1 C2 C3 <addr> <len>` in normal mode; value → dBm = −(256 − RSSI) [1][2].

**Determining the hidden SF/BW/CR (procedure).** Put an SDR (RTL-SDR at 2.4 MS/s suffices for ≤ 500 kHz BW) next to the transmitter through an attenuator. On the waterfall: (1) the **sweep width** of a preamble chirp is BW; (2) the **chirp period** is $T_s$; then $SF = \log_2(T_s\cdot BW)$. (3) Decode with gr-lora_sdr at that SF/BW trying CR 1–4 and implicit/explicit header; the explicit header, if present, reveals CR and length [7]. (4) Check sync word and preamble length by trying bare-chip reception with RadioLib (sync words 0x12/0x34 first). Record the results in this page — **no verified public mapping exists** (searched EBYTE manuals, TTN forum, arduino-LoRa and RadioLib issues).

### Level 3 — electrical design: supply, heat, protection
**Supply current and droop.** The E22-400T33D draws 0.85–1.2 A in bursts [1]. With a 5 V rail, 2 W RF out and ~6 W in, about **4 W is heat while transmitting** (PA efficiency ~33 %). A telemetry duty of 50 % means ~2 W average dissipation into a 26 g module in a closed avionics bay. The supply must hold regulation through a 0 → 1.2 A step in microseconds: size the regulator for ≥ 1.5–2 A, put bulk low-ESR capacitance at the module, and keep the module ground return away from sensor/ADC grounds. EBYTE's hardware notes ask for ≥ 30 % supply margin, low ripple, and routing no high-speed or power traces under the module [2]. Under-voltage directly reduces output (EBYTE: ≥ 3.3 V for the E22, ≥ 5.0 V for the E220-T30D to "ensure output power") [1][2] — the Avionics C 5 V buck-boost for the E220 is therefore correct.
**Thermal**: estimate $\Delta T = P_{diss}\,\theta$; with no datasheet $\theta$, measure the module can temperature during a bench soak at flight duty cycle (thermocouple, 10 min). Heat also drifts the reference oscillator ([impairments](lora-impairments-doppler-drift-timing.md)); see [thermal management](../13-pcb-rf-layout-emc/thermal-management-rf.md).
**RF protection**: EBYTE rates blocking/damage input at 10 dBm ("less chance of burning when used at close range") [1][2]. Two 30–33 dBm modules or a module and a ground Yagi within a few metres can exceed this — never key a transmitter into a nearby receiver of the same band; do bench tests through ≥ 40 dB of attenuation.
**Antenna port**: SMA-K, 50 Ω [2]; never transmit without a load (PA damage and harmonic splatter).

## Design equations & rules of thumb
| Rule | Value |
|---|---|
| E22-400 channel | $f$ = 410.125 + CH MHz (CH 0–83) |
| E220-900 channel | $f$ = 850.125 + CH MHz; SG 866–869 MHz ⇒ CH 16–18 (866.125–868.125 MHz, 500 mW e.r.p.) (CH 16 only if the E22 is not on CH 23; normally CH 17 with E22 CH 24, CH 18 with CH 23); SG 917–925 MHz ⇒ CH 67–74 (917.125–924.125 MHz, 100 mW e.r.p., 1 %); EU 869.40–869.65 MHz unreachable (CH 19 = 869.125 MHz) |
| RSSI byte | dBm = −(256 − value) |
| Heat while transmitting (2 W module) | ≈ 4 W |
| Max sub-packet | 240 B (E22), 200 B (E220) |
| LBT worst-case delay | 2 s |
| WOR period | (1 + WOR)·0.5 s |
| 62.5k air rate | SF5/BW500/CR4/5 |

## Worked examples
**1. Moving the E220 to a legal Singapore channel.** Default 873.125 MHz is outside both Singapore SRD windows (866–869 and 917–925 MHz [8]). CH = 70 gives 850.125 + 70 = 920.125 MHz, inside 917–925 and away from the 866.25 MHz second harmonic of the E22 at 433.125 MHz. Command in configuration mode: write register 05H = 0x46 (`C0 05 01 46`). Also reduce power to the legal level ([band plans](ism-band-plans-duty-cycle.md)) — but at 917–925 MHz that is only **100 mW e.r.p. with ≤ 1 % duty** (TS SRD 30c), and even the E220's lowest step (21 dBm) is ≈ 0.5 dB over with a dipole. **For flight telemetry, prefer CH 17 or 18 (867.125 / 868.125 MHz) in 866–869 MHz** (500 mW e.r.p., no duty stated): pair CH 17 with the E22 on CH 24, and CH 18 with CH 23. 1 % duty allows only ≈ 0.14 Hz of 32-byte SF7/125 frames ([impairments](lora-impairments-doppler-drift-timing.md#practical-notes), [19](../19-regulations-safety/singapore-imda-rules.md)).
**Better alternative (W3-C5 X7):** 866–869 MHz (TS SRD sub-band 29) allows **500 mW e.r.p. with no duty limit stated**. CH 18 = 868.125 MHz (`C0 05 01 12`) at 24 dBm → 24 − 0.5 + 2.15 − 2.15 = 23.5 dBm = 224 mW e.r.p. (+3.5 dB margin; 27 dBm is only +0.5 dB — too thin). CH 18 is 1.9 MHz from the E22's 866.25 MHz second harmonic (CH 16 = 866.125 MHz would sit only 125 kHz from it). If the E22 is on CH 24 (434.125 MHz — needed in Singapore at BW > 125 kHz, because CH 23's channel edge falls below 433.05 MHz), its harmonic is 868.25 MHz, 125 kHz from CH 18: then use CH 17 = 867.125 MHz (1.125 MHz away). Caveats: IMDA flags 866–869 MHz "under review with the intent to refarm", and whether rocket telemetry is "tracking, tracing and data acquisition" is an interpretation — see [19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md).

**2. Frame sizing on the E22.** A 48-byte telemetry frame at the default 2.4k rate fits in one 240-byte sub-packet; at 62.5k (if it is SF5/500) it takes ≈ 8 ms on air with a 12-symbol preamble, versus 308 ms if the 2.4k setting were SF9/125 (`lora_toa.py`, SX126x SF5 rules). If firmware writes the frame in two UART bursts separated by a gap longer than the module's idle timeout, it may go out as two radio packets — double the overhead and a reassembly risk.

**3. Supply design for the E22-400T33D from a 2S pack.** 7.4 V nominal → 5 V buck rated 3 A; 1.2 A burst → 6 W input. Buck efficiency 90 % → 6.7 W from the battery while transmitting; for 20 % TX duty over a 60 min pad wait + flight, energy ≈ 0.2 × 6.7 W × 1 h = 1.3 Wh — a significant slice of a 2S 1000 mAh pack (7.4 Wh).

## Practical notes
- **Bare chip vs UART module** for Marcus's next board:

| | UART module (E22/E220-T) | SPI module / bare chip + RadioLib |
|---|---|---|
| RF design effort | none | none (SPI module) / full (bare chip) |
| SF/BW/CR/LDRO/preamble/sync | hidden menu | full control |
| Per-packet SNR, frequency error | no (RSSI only) | yes (Doppler/drift logging) |
| TX/RX timestamps | UART latency, buffering | IRQ-exact (TxDone/RxDone) |
| Frequency hopping / dual rate | no | yes |
| Interop with other LoRa gear | uncertain | standard |
| Firmware effort | minimal | driver + state machine |
- **Libraries**: RadioLib supports SX127x, SX126x, LLCC68, LR11x0, LR2021, SX128x, STM32WL plus CC1101, nRF24L01, RF69, Si443x and LoRaWAN [9]; Sandeep Mistry's *arduino-LoRa* is SX127x-only; Semtech's `sx126x_driver`/LoRaMac-node are the reference implementations; Renzo Mischianti's libraries wrap the EBYTE UART protocol (anecdotal-quality docs).
- **SPI power modules** (E22-xxxM30S): the SX126x drives an external PA — do not set the chip to its full +22 dBm into the PA input; the RadioLib maintainer advises staying around ≤ 18 dBm (forum advice, unverified) [10]; check the module manual for the intended drive level and the RX/TX switch control pins (often DIO2 or two GPIOs).
- **Dev boards** (Meshtastic hardware list [4]): RAK4631 (nRF52840 + SX1262), Heltec LoRa 32 V3 (ESP32-S3 + SX1262), LilyGo T-Beam S3-Core (ESP32-S3 + SX1262 + GNSS), T-Echo (nRF52840 + SX1262), Station G2 (ESP32-S3 + SX1262); Seeed Wio-E5 (STM32WLE5JC) [6]. Meshtastic recommends SX126x/LR11xx over SX127x [4].
- **Ground station**: the same UART module works as a receiver, but an SPI board or SDR logs SNR and frequency error too ([ground station](ground-station-design.md)).

## Common mistakes & misconceptions
- **"E220 and E22 are the same thing with different bands."** Different chips: LLCC68 lacks SF10–12 at 125 kHz and has a different sensitivity floor.
- **Believing the power and sensitivity ratings together** ("2 W and −147 dBm ⇒ 180 dB budget"). The sensitivity number is not achievable at the stated rate.
- **Hobby write-ups mis-identifying chips** (e.g. an English hobby tutorial, as summarised, calling the E220 SX1262-based and the E22 SX1276-based). Check the EBYTE datasheet [1][2].
- **Leaving the E220 on its default 873.125 MHz** — outside Singapore's bands.
- **"Turning the E22-400T33D down to its lowest power makes it licence-free."** Its lowest step is 24 dBm (≈ 224 mW e.r.p. with a dipole) vs the 10 mW e.r.p. limit; reaching 10 dBm needs a ≥ 14 dB pad, and a module that can be commanded back to 2 W arguably fails TS SRD §4.1(b) anyway — fly it under a licence ([19](../19-regulations-safety/singapore-imda-rules.md)).
- **Using the E220 at EU 869.5 MHz** — its 1 MHz grid cannot reach 869.40–869.65 MHz.
- **Running LBT on a rocket** — up to 2 s extra latency, non-deterministic.
- **Using the CRYPT key as security** — it is a proprietary 16-bit scrambling factor; treat the link as public.
- **Undersized supply**: a 1 A LDO or thin traces make the module brown-out mid-packet (AUX stuck low, resets).
- **Changing modes while AUX is low**, or configuring at a baud rate other than 9600.

## How to simulate / verify
- ToA for a guessed air-rate mapping: `python3 tools/verify/lora_toa.py` (edit the table at the bottom).
- Determine the real mapping: SDR procedure above, with gr-lora_sdr [7]; log it here.
- Bench current: 0.1 Ω shunt + oscilloscope on the module supply during a packet; measure droop at the pins.
- Thermal: thermocouple on the module shield at flight duty cycle for the full pad-wait duration.
- Sensitivity: calibrated attenuator ladder from a second module; find RSSI and attenuation at 1 % PER for each air rate.

## Open questions / gaps
- **Air-data-rate → SF/BW/CR mapping for E22/E220/E32 is unknown** (only 62.5k is unambiguous). Also unknown: sync word, preamble length, header mode, CRC and whether EBYTE scrambles the payload by default. Needs one SDR session.
- Whether the E22-400T33D / E220-900T30D use a TCXO; the NF and part numbers of their LNAs/PAs.
- Thermal resistance of the 2 W module.
- EBYTE E32/E19 manuals were not read in detail (search summaries only).

## Sources
1. EBYTE, *E22-400TXXX Data Sheet* (©2012–2022) — models, SX1268, frequency plan, power/current, sub-packets, modes, AUX, command set, register map, RSSI formula, LBT (2 s), WOR, CRYPT, repeater. https://www.cdebyte.com/pdf-down.aspx?id=2179 (module datasheet)
2. EBYTE, *E220-900T30D User Manual* (©2012–2020) — LLCC68, 850.125–930.125 MHz, default 873.125 MHz, ≥ 5 V, 620 mA TX, 17.2 mA RX, 200 B sub-packet, register map, hardware design notes. https://www.cdebyte.com/pdf-down.aspx?id=349 (module manual)
3. EBYTE, E32-433T30D product listing/manual (search summary) — SX1278, 410–441 MHz, 30 dBm, 2.7–5.5 V, 2.4 kb/s default. https://www.cdebyte.com/products/E32-433T30D (module listing — not read in full)
4. Meshtastic docs, "Supported devices" (accessed 2026-09-27) — MCU + radio of RAK4631, Heltec V3, T-Beam S3, T-Echo, Station G2; SX126x/LR11xx recommended. https://meshtastic.org/docs/hardware/devices/ (project docs)
5. HopeRF, RFM95W/RFM96W/RFM98W product pages and *RFM95/96/97/98(W)* datasheet (SparkFun mirror) — SX1276-class, bands, +20 dBm. https://www.hoperf.com/modules/lora/RFM95W.html (module datasheet — via search summary)
6. Seeed LoRa-E5 (STM32WLE5JC) listings (search summary). (vendor)
7. J. Tapparel et al., gr-lora_sdr (EPFL), SPAWC 2020 / arXiv:2002.08208. https://github.com/tapparelj/gr-lora_sdr (peer-reviewed + code)
8. IMDA, *TS SRD* Issue 1 Rev 3 (Sep 2023), Table 1 sub-bands 26a, 29, 30c and §4.1(b). https://www.imda.gov.sg/-/media/imda/files/regulation-licensing-and-consultations/ict-standards/telecommunication-standards/radio-comms/imdatssrd.pdf (regulator standard)
9. J. Gromeš, *RadioLib* README (accessed 2026-09-27) — supported modules and protocols. https://github.com/jgromes/RadioLib (library docs)
10. RadioLib discussion #507 "Range enlargement" — maintainer advice on E22 external-PA drive level and 62.5 kHz BW. https://github.com/jgromes/RadioLib/discussions/507 (forum — anecdotal)
11. [19 Singapore IMDA rules](../19-regulations-safety/singapore-imda-rules.md) — margins from `tools/verify/reg_erp_compliance.py`, licence routes (amateur, temporary permit, experimental, localised station). (KB page citing primary law)
