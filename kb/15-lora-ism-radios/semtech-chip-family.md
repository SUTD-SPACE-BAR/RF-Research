---
title: Semtech LoRa chip family — SX127x, SX126x, LLCC68, LR11xx, LR2021, SX128x, STM32WL
domain: 15-lora-ism-radios
slug: semtech-chip-family
tags: [lora, semtech, reference-design, bring-up, pe4259, rf-switch, ranging, time-of-flight, rssi-ranging, tdoa, localisation, sx1276, sx1278, sx1262, sx1268, llcc68, lr1110, lr1121, lr2021, sx1280, stm32wl, errata, pa-config, tcxo, image-calibration]
prerequisites:
  - lora-phy-css-math.md
related:
  - lora-modules-ebyte-rfm-heltec.md
  - lora-sensitivity-and-link-budget.md
  - lora-impairments-doppler-drift-timing.md
  - other-ism-radios-fsk-2g4.md
  - ../18-components-parts/rf-transceiver-ics.md
  - ../06-rf-circuits/power-amplifiers.md
  - ../13-pcb-rf-layout-emc/rf-layout-rules.md
level: intermediate
confidence: medium
last_updated: 2026-10-13
---

# Semtech LoRa chip family — SX127x, SX126x, LLCC68, LR11xx, LR2021, SX128x, STM32WL

## Questions this page answers
- Which LoRa chip is inside my E22 / E220 / RFM95 / Heltec board, and does it matter?
- What is the difference between SX1276, SX1278, SX1262, SX1268 and LLCC68?
- Why can't an LLCC68 run SF12?
- Which chip should I use for a new 433 MHz or 920 MHz rocket radio?
- What do PA_BOOST, OCP, paDutyCycle/hpMax, DIO2 RF-switch and DIO3 TCXO settings do?
- What SX126x errata/known limitations must firmware work around?
- What are LR1110/LR1120/LR1121/LR2021 and SX1280, and when are they worth it?
- Why must I run image calibration for 433 MHz on an SX126x?
- What does the Semtech SX1262 reference design contain (matching, harmonic filter, balun, RF switch, TCXO)?
- Why does my custom LoRa board transmit 30–50 dB low?
- How do I bring up a bare SX126x/SX127x board step by step?
- Can I find a landed rocket by RSSI, by time of flight (SX1280 ranging) or by LoRa TDOA, and how accurate is each?

## TL;DR
- **Generation 1 (SX127x, 2013+)**: register-mapped SPI, FIFO, SF6–12, BW 7.8–500 kHz (SX1276/78/79), +20 dBm on PA_BOOST (limited to 1 % duty at +20 dBm, VSWR ≤ 3:1) [1]. SX1276 137–1020 MHz; SX1278 137–525 MHz (433 MHz boards); SX1277 SF6–9 only.
- **Generation 2 (SX126x, 2017+)**: command-based SPI with a BUSY line, DC-DC, 4.6 mA RX, SF5–12, +22 dBm (SX1262/SX1268) or +15 dBm (SX1261), −148 dBm best sensitivity [2]. **SX1268** = 410–810 MHz variant (China 470–510 MHz focus) used in the **E22-400** modules; SX1262 = 150–960 MHz.
- **LLCC68** (in the **E220** modules): SX1262-compatible but SF limited by BW — **SF5–9 @125 kHz, SF5–10 @250, SF5–11 @500**; best sensitivity ≈ −129 dBm [3]. Fine for fast telemetry; no long-range slow modes.
- **LR11xx (2021+)**: LR1110 = sub-GHz LoRa/LR-FHSS + GNSS (GPS/BeiDou) and Wi-Fi scanners; LR1121 = multi-band LoRa (sub-GHz +22 dBm, 2.4 GHz, 1.9–2.1 GHz S-band, 1.55 GHz L-band) without the scanners; compatible with SX1261/2/8 [4][5].
- **LR2021 ("LoRa Plus", datasheet 2026)**: sub-GHz + 2.4 GHz + S-band, LoRa to 125 kb/s, FLRC bursts to 2.6 Mb/s, claimed −141.5 dBm at SF12/125, larger offset tolerance "obviating TCXO" [6] — promising for rockets, unverified here.
- **SX1280/81/82**: 2.4 GHz LoRa (BW 203–1625 kHz), FLRC 260–1300 kb/s, GFSK, +12.5 dBm, −132 dBm best; SX1280/82 include a time-of-flight ranging engine [7].
- **STM32WLE5/WL55**: Cortex-M4 (+M0+ on WL55) with an SX126x-class radio on the same die, 150–960 MHz, +22 dBm/+15 dBm PAs [8].
- **Reference designs** (AN1200.40 [13]): the SX1262 board E428V03A (4-layer, crystal, +22 dBm, 118 mA at 3.3 V) and E449V01A (TCXO, for packets > 400 ms). The TX path is choke-fed RFO → L-C match → parallel-LC 2nd-harmonic notch → π low-pass → PE4259 switch. The RX path is a 3-element LC balun into the differential LNA. The BOM values are per region and supplied on request, so copy a *published* board for your band. **"Transmits 30–50 dB low"** almost always means the wrong PA pin (RFM95: PA_BOOST not selected), an RF switch that is unpowered or in the wrong state (the PE4259 isolates the off path by 29 dB at 1 GHz), or the antenna on the wrong port. The [bring-up checklist](#reference-design-integration-and-bring-up) separates these.
- **Ranging** ([section](#ranging-and-localisation)): RSSI ranging is good only to ×/÷ 1.7 (σ 6 dB, n = 2.5) and is biased by tens of times if the path-loss exponent is wrong. SX1280 two-way ToF gave a 46 m mean error over 1.4 km in a rural LOS test (σ 84 m) after calibrating offsets of several hundred metres [16]. LoRaWAN TDoA gives about 150 m median. For a landed rocket a downlinked GNSS fix plus DF is better than any of them.
- Must-know firmware items on SX126x: image calibration for your band (default 902–928 MHz; 430–440 MHz needs 0x6B/0x6F) [2]; TCXO via DIO3 then recalibrate; DIO2 as RF-switch control; OCP 60 → 140 mA after SetPaConfig; four "known limitations" workarounds (500 kHz TX quality, PA clamping, implicit-header timeout, inverted IQ) [2].

## Intuition (no math)
All Semtech LoRa chips share the same modem idea (chirps, SF/BW/CR), so an SX1276 and an SX1262 on the same settings talk to each other — with two exceptions: SF6 (implemented differently) and anything outside the smaller chip's allowed SF/BW set (LLCC68). What changed between generations is the plumbing: power consumption, how you program them (registers vs commands), how much PA power is on-chip, how good the synthesiser and calibration are, and what extra radios or GNSS scanners are bundled. For a rocket the important differences are: available output power (and how clean it is), whether slow modes exist (LLCC68 no), TCXO support, and the errata your firmware must work around.

## The math
### Level 1 — key specifications
| Chip | Gen | Frequency | Max P_out | LoRa SF / BW | Best LoRa sensitivity | RX current | Notes |
|---|---|---|---|---|---|---|---|
| SX1272/73 | 1 | 860–1000 MHz [9] | +20 dBm (PA_BOOST) [9] | SF6–12 (SX1273 reduced) | −137 dBm [9] | ~10 mA [9] | older 868/915 part |
| SX1276 | 1 | 137–1020 MHz | +20 dBm | SF6–12, 7.8–500 kHz | −148 dBm | ~10 mA-class | RFM95/96/98, LilyGo T-Beam v1.x, Heltec v2 |
| SX1277 | 1 | 137–1020 MHz | +20 dBm | SF6–9 | −139 dBm | | |
| SX1278 | 1 | 137–525 MHz | +20 dBm | SF6–12 | −148 dBm | | 433 MHz boards (Ra-01, E32-433) |
| SX1279 | 1 | 137–960 MHz | +20 dBm | SF6–12 | −148 dBm | | |
| SX1261 | 2 | 150–960 MHz | +15 dBm | SF5–12, 7.8–500 kHz | −148 dBm | 4.6 mA (DC-DC) | |
| SX1262 | 2 | 150–960 MHz | +22 dBm | SF5–12, 7.8–500 kHz | −148 dBm | 4.6 / 5.3 mA boosted | Heltec v3, RAK4631, E22-900 |
| SX1268 | 2 | 410–810 MHz [10] | +22 dBm | as SX1262 | −148 dBm | 4.6 mA | **E22-400T33D** |
| LLCC68 | 2 | 150–960 MHz | +22 dBm | SF5–9@125, –10@250, –11@500 | ≈ −129 dBm (SF9/125) | ~SX1262 | **E220-900T30D** |
| LR1110/20 | 3 | 150–960 MHz (+2.4 GHz, S-band on LR1120) | +22 / +15 dBm | as SX126x + LR-FHSS | "low-NF front end" | | GNSS + Wi-Fi scanners |
| LR1121 | 3 | 150–960 MHz, 1.9–2.1 GHz, 2.4 GHz, 1.55 GHz | +22 dBm (sub-GHz), ~+11.5 dBm (2.4 GHz) [5] | as SX126x + LR-FHSS | | | no scanners, AES-128 |
| LR2021 | 4 | sub-GHz, 2.4 GHz, S-band | +22 dBm | LoRa up to 125 kb/s | −141.5 dBm SF12/125 (claim) [6] | | FLRC 2.6 Mb/s, O-QPSK, OOK |
| SX1280/81/82 | – | 2.400–2.500 GHz | +12.5 dBm | SF5–12, 203–1625 kHz | −132 dBm (SF12/203) | 5.5–8.2 mA | FLRC, ranging (not SX1281) |
| STM32WLE5 | SoC | 150–960 MHz | +22 (HP) / +15 (LP) dBm | SX126x-class | −136.5 dBm SF12/125 (module claim) [8] | | LoRa only on WLE5/WL55, not WLE4 |

Sources for rows without a bracket: SX127x [1], SX126x [2], LLCC68 [3], SX128x [7]. SX1276/77/78/79 sensitivities and ranges are from the variant table in [1].

### Level 2 — register/command-level concepts that matter
**SX127x**
- **PA pins**: RFO (up to +14 dBm, efficient) or **PA_BOOST** (up to +17 dBm continuous, +20 dBm with the high-power DAC setting). A board wires only one; RFM95/96 use PA_BOOST, so firmware must select it (`PaSelect = 1`) or you get nothing useful. At +20 dBm: supply 2.4–3.7 V, **duty ≤ 1 %**, VSWR ≤ 3:1 [1].
- **OCP** (`RegOcp`): $I_{max} = 45 + 5\cdot OcpTrim$ mA (0–15) or $-30 + 10\cdot OcpTrim$ mA (16–27), limiting PA current only; +20 dBm draws ~120 mA [1].
- **Ports**: LF (≤ 525 MHz, band 2/3) and HF (band 1) RF paths; LoRa RSSI = −164 + Rssi (LF) or −157 + Rssi (HF), + SNR/4 when SNR < 0 [1].
- **SF6** needs implicit header plus `DetectionOptimize = 0b101` and `RegDetectionThreshold = 0x0C` [1]. **Sync word** `RegSyncWord` 0x39 (0x12 private, 0x34 LoRaWAN). **AFC**: read FEI, retune, write `PpmCorrection` [1].
- The datasheet refers to an **errata note** for 500 kHz operation (`IfFreq`, `HighBWOptimize1/2` registers) [1] — use the errata sheet when running BW 500 kHz.

**SX126x (SX1261/2/8, LLCC68, and the STM32WL radio)**
- **Command interface**: every SPI transaction is an opcode; poll **BUSY** before each command. Sequence: `SetStandby` → `SetPacketType(LoRa)` → `SetRfFrequency` → `SetPaConfig` → `SetTxParams` → `SetModulationParams` (SF, BW, CR, LDRO) → `SetPacketParams` (preamble, header, length, CRC, IQ) → `SetDioIrqParams` → `SetTx/SetRx`.
- **PA configuration** (`SetPaConfig`: paDutyCycle, hpMax, deviceSel, paLut): SX1262 +22 dBm = (0x04, 0x07, 0, 1) with `SetTxParams` +22; +20 dBm = (0x03, 0x05); +17 = (0x02, 0x03); +14 = (0x02, 0x02). **Never** paDutyCycle > 0x04 on SX1262 or hpMax > 0x07 (PA overstress/ageing) [2]. TX current at +22 dBm: 118 mA (868/915 MHz), 107 mA (434/490 MHz); PA is powered from VBAT and loses 2/3/6 dB at 2.7/2.4/1.8 V [2].
- **OCP** register 0x08E7: 0x18 (60 mA) after POR, set to 0x38 (140 mA) when SetPaConfig selects SX1262; adjust *after* SetPaConfig, 2.5 mA steps [2].
- **DC-DC vs LDO**: DC-DC saves RX current (4.6 vs 8.8 mA) [2].
- **Rx boosted gain**: register 0x08AC = 0x96 (vs 0x94 power-saving) — ~+4 dB sensitivity (−137 vs −133 dBm SF12/125) for +0.7 mA; must be re-applied when using RX duty cycling [2].
- **DIO2 as RF switch** (`SetDIO2AsRfSwitchCtrl`) drives an external T/R switch automatically; **DIO3 as TCXO supply** (`SetDIO3AsTCXOCtrl`, 1.6–3.3 V, ≤ 4 mA, clipped-sine ≤ 1.2 Vpp into XTA via 220 Ω + 10 pF); after enabling a TCXO the power-on calibration will have failed and a full `Calibrate` is needed [2].
- **Image calibration** (`CalibrateImage`): done by default for 902–928 MHz only. For 430–440 MHz use (0x6B, 0x6F); 470–510 (0x75, 0x81); 779–787 (0xC1, 0xC5); 863–870 (0xD7, 0xDB) [2]. Image attenuation is 35 dB without and 54 dB with IQ calibration [2] — an uncalibrated 433 MHz receiver is vulnerable to image interference.
- **Sync word** registers 0x0740/0x0741: 0x3444 public, 0x1424 private [2 Rev 2.2].
- **CAD** on SX126x detects preamble *and* data symbols (SX127x: preamble only) [2].

### Level 3 — SX126x known limitations (errata) and their fixes
From SX1261/2 datasheet §15 [2]:
| # | Problem | Fix (before each TX / at init) |
|---|---|---|
| 15.1 | Modulation quality at **LoRa BW 500 kHz** degrades *other* receivers' sensitivity | Register 0x0889 bit 2 = 0 for 500 kHz, = 1 for all other BW and FSK |
| 15.2 | **PA clamping** too protective: 5–6 dB less output into a mismatched antenna | Register `TxClampConfig` (0x08D8) bits 4–1 = 1111 after POR / cold start |
| 15.3 | **Implicit-header RX timeout** timer not stopped on RxDone → spurious timeouts later | After any Rx with timeout: stop RTC (reg 0x0902) and clear event (reg 0x0944) |
| 15.4 | **Inverted-IQ** packets lost for long payloads | Reg 0x0736 bit 2 = 0 with inverted IQ, = 1 with standard IQ |

Libraries (RadioLib, Semtech's `sx126x_driver`, LoRaMac-node) implement these; a hand-written driver must too. Item 15.2 matters for rocket antennas that detune when installed in an airframe; item 15.1 matters if you choose BW 500 kHz for high-rate telemetry (it degrades the *ground* receiver even if it is an SX127x).

## Design equations & rules of thumb
| Rule | Value |
|---|---|
| Chip generations inter-operate on LoRa | yes for SF7–12, same BW/sync/IQ/LDRO; not SX127x-SF6 ↔ SX126x-SF6 |
| LLCC68 SF limit | SF ≤ 9 (125 kHz), ≤ 10 (250), ≤ 11 (500) |
| SX1262 TX current | 118 mA @ +22 dBm (915), 107 mA (434) |
| SX1276 +20 dBm | ≤ 1 % duty, VSWR ≤ 3:1, 2.4–3.7 V |
| SX126x OCP default | 60 mA POR, 140 mA after SetPaConfig(SX1262) |
| Image calibration | re-run for any band other than 902–928 MHz |
| Rx boosted | +4 dB sensitivity for ~0.7 mA |
| 2.4 GHz vs 433 MHz path loss | +15 dB for the same antenna gains |

## Worked examples
**1. Designing your own 433 MHz board.** Options: SX1262 (150–960 MHz, covers 433 fine) or SX1268 (410–810 MHz, what EBYTE used). Both +22 dBm. Add an external PA only if you have legal authority for more power ([band plans](ism-band-plans-duty-cycle.md)). Firmware must: select TCXO on DIO3 if fitted and recalibrate; run `CalibrateImage(0x6B, 0x6F)`; apply limitation 15.2 (antenna mismatch in an airframe is certain); set OCP after SetPaConfig; enable Rx boosted on the ground unit.

**2. Why the E220 (LLCC68) cannot mirror the E22's slow modes.** An E22 at SF12/125 (−137 dBm class) cannot be received by an E220 at all — the LLCC68 rejects SF12 at 125 kHz. Common ground: SF5–9 at 125 kHz, up to SF10 at 250 kHz, SF11 at 500 kHz. For telemetry at SF7–9 this costs nothing.

**3. Power budget for a +22 dBm SX1262 transmitting a 72 ms SF7 packet 10 times per second at 434 MHz.** Duty 72 %; average PA current ≈ 0.72 × 107 mA ≈ 77 mA from VBAT (plus ~few mA logic) — manageable from a 1S cell; compare the 2 W E22 module at 850–1200 mA TX ([modules](lora-modules-ebyte-rfm-heltec.md)). (Regulatory note: +22 dBm at 72 % duty is a *licensed* configuration in Singapore — the 433 MHz licence-exempt limit is 10 mW e.r.p. at ≤ 10 % duty, i.e. ≤ ~10 dBm conducted into a dipole; see [19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md).)

## Practical notes
- **Layout/thermal**: SX126x datasheet warns to thermally isolate the crystal from the PA [2]; Semtech AN1200.37 gives layout recommendations (not read in this pass). Reference designs use 32 MHz low-g crystals [11] — relevant under rocket acceleration.
- **Harmonics**: a +22 dBm class-D/E PA needs a proper low-pass matching network; module makers do this, your board must too (see [PA design](../06-rf-circuits/power-amplifiers.md), [RF layout](../13-pcb-rf-layout-emc/rf-layout-rules.md)).
- **Drivers**: RadioLib supports SX127x, SX126x, LLCC68, LR11xx, SX128x, STM32WL; Sandeep Mistry's arduino-LoRa supports SX127x only; Semtech's official drivers are `sx126x_driver`, `lr11xx_driver` and LoRaMac-node ([modules](lora-modules-ebyte-rfm-heltec.md)).
- **Counterfeits/relabels**: cheap boards sold as "SX1276" sometimes carry SX1278 (525 MHz upper limit) — check the marking and test at your frequency.

## Reference-design integration and bring-up

### What the SX1262 reference design is made of
Semtech publishes three SX1261/2 reference boards (AN1200.40 Rev 1.1 [13]): **E406V03A** (SX1261, 2-layer, crystal, +14/15 dBm at 25.5 mA, covers all sub-GHz bands with per-region BOMs), **E428V03A** (SX1262, 4-layer, crystal, +22 dBm at ≈ 118 mA/3.3 V; US/Canada, where packets stay under 400 ms) and **E449V01A** (SX1262, 4-layer, **TCXO**, for regions allowing longer packets). The application schematic is also in the datasheet (§14.5) [2]. Signal path and job of each part (designators as in the datasheet and AN1200.40):

| Block | Parts | What it does | Design rule |
|---|---|---|---|
| PA supply | L1 from VR_PA to RFO, C1/C2 decoupling | VR_PA (internal regulator, from VBAT on the SX1262 board) biases the PA's open-drain output through the choke | output power follows VR_PA; keep the choke self-resonance well above f |
| Impedance match | L2 (series), C3 (shunt), with the following stages | transforms 50 Ω to the PA's optimum load, e.g. SX1261 at 915 MHz Z_opt = 11.7 + j4.8 Ω for 14.6 dBm (13.5 + j7.6 Ω for higher efficiency) [13] | Z_opt comes from load-pull at the RFO pad; all later stages contribute to it |
| 2nd-harmonic notch | L3 ∥ C4 | parallel resonance at 2f blocks the second harmonic | rule of thumb: L3 = ¾ of the plain-match value, C4 resonates L3 at 2f [13] |
| Higher-harmonic low-pass | C5, L4, C7 (π), C6 DC block | 50 Ω-to-50 Ω low-pass for 3f and above; C5 does both matching and filtering | tune on the PCB; parasitics shift it |
| RF switch | U2 PE4259, controlled from DIO2 (via 100 Ω / 1 nF) and from a host line ANT_SW (via 100 Ω / 1 nF) | pin 6 powers the switch (single-pin mode); pin 4 CTRL high → RFC–RF1 (TX path), low → RF2 (RX path). Isolation 29 dB, insertion loss 0.35 dB at 1 GHz [14] | `SetDIO2AsRfSwitchCtrl(1)` drives DIO2 high in TX; ANT_SW must be high or the switch is unpowered |
| Antenna network | C8, C9, L5, C10 | matches a non-50 Ω antenna and adds filtering | fit 0 Ω/DNP for a 50 Ω antenna |
| RX balun / match | C11, C12, L6 (+ optional C13) | single-ended 50 Ω → differential LNA optimum source, e.g. 74 + j134 Ω (SX1261, 915 MHz) [13] | source-pull defines it; the balun also sets selectivity |
| Reference | 32 MHz crystal with a copper void on all layers, or a TCXO on DIO3 | heat from the PA drifts the crystal during long packets | +22 dBm at 3.7 V needs thermal insulation or a TCXO; packets near 1 s need a TCXO [15] |
| DC-DC | 15 µH between DCC_SW and VREG, 470 nF/100 nF | core supply from the DC-DC (halves SX1261 consumption vs LDO) [15] | drop the inductor and short VDD_IN–VREG for LDO mode |

AN1200.40 states that the component values are per-region BOMs, available from Semtech on request, and that the load-pull data may not be current [13]. For a team board, the low-risk path is to **copy a published board for your band exactly**, including stack-up and layout (Semtech EVK, or an open module such as an RFM9x/E22-M-class datasheet layout), rather than to derive the network. Then verify it on a VNA and a spectrum analyser ([PA design](../06-rf-circuits/power-amplifiers.md), [matching](../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md)). AN1200.37 [15] gives the SX1262 thermal arithmetic: at +22 dBm, 3.3 V × 118 mA = 389 mW in, 158 mW radiated and 231 mW dissipated in the package. The SX1262 PA is optimised for +22 dBm, so turning the power down cuts current but not the heat that reaches the crystal.

### Why a custom board transmits 30–50 dB low
| Symptom | Likely cause | Check |
|---|---|---|
| SX127x board (RFM95/96) gives a few dBm or less | `PaSelect = 0` (RFO) on a board that wires only **PA_BOOST**; the register default selects RFO [1] | set RegPaConfig bit 7; read it back |
| SX126x output ~30 dB low, RX also deaf | RF switch unpowered (ANT_SW low) or DIO2 not configured as switch control, so the PA drives the switch's isolated port (≈ 29 dB isolation [14]) | scope DIO2 and ANT_SW during TX; `SetDIO2AsRfSwitchCtrl(1)` |
| TX fine, RX 20–30 dB deaf | switch polarity inverted (TX and RX swapped), or a separate-GPIO switch driven backwards | swap the logic and compare RSSI from a known source |
| 5–6 dB low into the real antenna, correct into 50 Ω | SX1262 PA clamping on mismatch (errata 15.2) [2] | apply the TxClampConfig fix; measure S11 of the installed antenna |
| 2–6 dB low on a weak supply | PA powered from VBAT; −2/−3/−6 dB at 2.7/2.4/1.8 V [2] | measure VBAT *during* the burst |
| Wrong `SetPaConfig` for the chip (SX1261 table on an SX1262) | device-select bit / table mismatch [2] | use the table row for your chip and power |
| Output fine, frequency off or calibration error flags | TCXO enabled without recalibration; XTA/XTB load capacitors wrong | `GetDeviceErrors` after boot |
| Strong 2nd/3rd harmonic, or fundamental low | notch/low-pass detuned by parasitics or wrong part values | spectrum analyser through an attenuator; VNA on the filter |

### Bring-up checklist (bare SX126x board)
1. **Power and clocks, no RF**: check supply rails and current in standby; BUSY goes low after reset; `GetStatus` answers; read `GetDeviceErrors` (oscillator, PLL and calibration flags) and log it at every boot.
2. **Reference**: if a TCXO is fitted, `SetDIO3AsTCXOCtrl(voltage, delay)` and then a full `Calibrate(0x7F)`; check that the error flags have cleared.
3. **Band setup**: `CalibrateImage` for your band (430–440 MHz: 0x6B, 0x6F; 863–870 MHz: 0xD7, 0xDB); `SetRegulatorMode` (DC-DC if L fitted); apply errata 15.1–15.4.
4. **Switch**: `SetDIO2AsRfSwitchCtrl(1)` (or drive the switch GPIOs); hold ANT_SW high if your board copies the Semtech schematic.
5. **CW test into a 30–40 dB pad and a power sensor or spectrum analyser**: `SetPaConfig` (for SX1262 +22 dBm use 0x04, 0x07, 0x00, 0x01), `SetTxParams`, OCP at 140 mA, then `SetTxContinuousWave`. Expect within ±1–2 dB of the setting at the connector. Check 2f and 3f against the regulatory limit (Singapore: −36 dBm below 1 GHz, −30 dBm above [19 IMDA](../19-regulations-safety/singapore-imda-rules.md)).
6. **Frequency**: measure the CW frequency; the error should be within the crystal tolerance (±10–20 ppm ≈ 4–9 kHz at 434 MHz). Re-measure after a 1 s carrier to see thermal drift.
7. **RX sensitivity**: a generator → step attenuator (or a second known-good board through ≥ 60 dB) to find the 10 % PER level. Compare with −124 dBm (SF7/125) at NF ≈ 6 dB ([17 bench recipes](../17-test-measurement/bench-measurement-recipes.md)).
8. **Installed antenna**: measure S11 in the airframe, then repeat step 5 radiated at a few metres (and step 7 through a pad) with the full system powered, to catch self-desense from the MCU, GNSS and DC-DC.

## Ranging and localisation

Ways to find a landed rocket without (or in addition to) its GNSS fix; numbers from `tools/verify/s1_ranging_error.py`.

### Level 1 — the four options
| Method | Needs | Accuracy (order of magnitude) | Limits |
|---|---|---|---|
| **RSSI ranging** | one receiver, a path-loss model | range only, ×/÷ 1.7 (σ 6 dB, n = 2.5): 2 km reads as 1.2–3.5 km | shadowing σ, unknown exponent n, antenna pattern of a lying rocket |
| **Two-way time of flight** (SX1280/SX1281-2 ranging engine) | both ends SX1280 (2.4 GHz), calibration | rural LOS: mean error 46 m up to 1.4 km, σ 84 m; positioning with 4 anchors 30 m DRMS, 5 m with a Kalman filter [16] | range overestimated by multipath (resolution c/BW = 185–739 m); 2.4 GHz path loss; ≤ +12.5 dBm |
| **TDOA** (one-way, ≥ 3 GNSS-timed receivers) | receivers with 1PPS timestamps | LoRaWAN field median ≈ 150 m [17]; a 433 MHz rocket node 40 m in ground tests [18] | 125 kHz multipath resolution 2.4 km; receiver geometry |
| **Direction finding** | a Yagi or array | two 1° bearings from a 2 km baseline: median 225 m at 5 km ([12 DF](../12-phased-arrays/adaptive-beamforming-doa.md#practical-direction-finding-for-rocket-recovery)) | multipath; needs a signal while you move |

### Level 2 — error models
**RSSI.** Log-distance loss with lognormal shadowing, $P_r = P_0 - 10n\log_{10}(d/d_0) + X_\sigma$, inverted for $d$, gives a multiplicative error: $\hat d/d = 10^{X/(10n)}$, a 68 % interval of ×/÷ $10^{\sigma/(10n)}$. The Cramér–Rao bound is $\sigma_d/d \ge (\ln 10/10)\,\sigma/n$, which is 0.55 for σ = 6 dB and n = 2.5 [19]. This is the origin of the "RSSI ranging is off by ×1.5–2.5" folklore: ×/÷ 1.58 at σ 4 dB/n 2 and ×/÷ 2.0 at σ 6 dB/n 2. A **wrong exponent is worse than the noise**. Calibrate n = 2 on the line-of-sight pad, then use it on a landed rocket where the true n is about 3.5, and 1 km reads as 32 km. Averaging many packets removes small-scale fading but not shadowing, which is fixed for a given spot.

**Two-way ToF.** Node A sends a request, B replies after a known delay $T_B$, and A measures the round trip: $d = c(T_A - T_B)/2$, with no clock synchronisation [16]. Error terms [16]:
- **Clock offset**: $\Delta d \approx c\,\delta\,T_B/2$. With δ = 40 ppm and T_B = 42.9 ms (BW 406 kHz, SF10) this is **257 m**; at BW 1625 kHz/SF5 it is 2 m. Running the exchange twice with the roles swapped ("back-to-back") cancels it.
- **Noise**: the paper's CRLB, eq. (4), gives σ_d ≈ 1.26 m at BW 403 kHz, SF5, SNR 12.5 dB, 15 symbols; 2.11 m was measured on a cable. Our evaluation of eq. (4) as transcribed gives exactly half of that; the factor of 2 is unresolved.
- **Multipath**: paths closer than $c/BW$ (739 m at 406 kHz, 185 m at 1625 kHz) cannot be separated, so the estimate is biased long. The paper's empirical correction was $d_c = 0.95d + 1$ m.
- **Fixed delays**: 1 ns of uncalibrated delay is 15 cm of range. The measured per-SF/BW offsets are "several hundred metres", so **calibrate over a cable of known length** at the frequencies used, and repeat after large temperature changes [16]. Semtech's AN1200.89 describes a passive "advanced ranging" mode: a third radio that overhears a ranging exchange measures a time difference, which gives TDOA-like hyperbolae. Its HDOP degrades more than 20× outside the anchor area [20].

**TDOA.** The timing bound for a chirp of bandwidth B, with $B_{rms} = B/\sqrt{12}$, is $\sigma_\tau \ge 1/(2\pi B_{rms}\sqrt{2E/N_0})$. An 8-symbol SF7/125 preamble at 0 dB SNR gives 98 ns (29 m). Two u-blox PPS edges at 30 ns RMS each add 42 ns, for 106 ns (32 m) in total ([GNSS timing](../21-gnss/gnss-timing-1pps.md)). The field median of 150 m [17] is set by multipath, not by these bounds.

### Practical notes
- For a rocket, the cheapest accurate locator is still **the GNSS fix it sends during descent and after landing**, plus a carrier beacon for DF. SX1280 ranging needs a second 2.4 GHz radio on board and anchors on the ground, so it pays off only for a team that already flies SX1280/LR1121 hardware.
- If you do use RSSI, use it as a **gradient** (walk toward increasing RSSI) or as a sanity check on DF, never as a range by itself.

## Common mistakes & misconceptions
- **"Copying the reference schematic is enough."** The values are per-region and the layout is part of the design. Copy a published board, stack-up included, for your band.
- **"No output — the chip is dead."** Check PA_BOOST/RFO selection, RF-switch power and polarity, and that the antenna is on the right port before replacing silicon.
- **"RSSI tells me the distance."** Only to a factor of about 2, and it can be wrong by 10–30× if the path-loss exponent is wrong.
- **"ToF ranging works out of the box."** The SX1280 needs calibrated delay offsets (hundreds of metres uncorrected) and role-swapped exchanges to cancel crystal offsets.
- **"LLCC68 is just a cheaper SX1262."** Electrically similar, but the SF/BW restriction removes the slow modes.
- **"SX1268 only works in China."** It covers 410–810 MHz, including 433 MHz; the regulatory focus is marketing, not physics.
- **Forgetting PA_BOOST on RFM95/96** → "my module transmits only a few metres".
- **Setting SX1276 to +20 dBm continuously** — violates its 1 % duty rating.
- **Skipping image calibration on 433 MHz SX126x boards** → reduced image rejection.
- **Enabling a TCXO without recalibrating** → wrong frequency / failed calibration flags.
- **Assuming SX1280 at 2.4 GHz gives similar range**: +12.5 dBm and 15 dB extra path loss vs 433 MHz (same antenna gains); it is a high-rate/ranging part, not a range part.

## How to simulate / verify
- Read back the SX126x `GetDeviceErrors` and calibration flags after boot; log them (the team's boot-log practice).
- Measure output power and harmonics with a spectrum analyser through an attenuator; check the 15.2 fix by comparing power into a deliberately mismatched load.
- Verify interoperability: an SX1276 board with RadioLib and an SX1262 board on identical SF/BW/sync/LDRO; sweep SF7–12.
- Sensitivity numbers → `tools/verify/lora_link_budget.py`.
- `python3 tools/verify/s1_ranging_error.py` (6 checks): RSSI-ranging Monte Carlo and CRB, exponent-mismatch bias, ToF clock-offset and multipath terms (reproduces Müller et al.'s 257 m and 185 m), TDOA timing bound vs PPS jitter.
- Bring-up: follow the checklist above and log each step's measured value in the board's bring-up record ([RF bring-up playbook](../17-test-measurement/rf-bring-up-debug-playbook.md)).

## Open questions / gaps
- LR1110/LR1120/LR1121/LR2021 and LLCC68 **full datasheets** were not read (product pages and a third-party module sheet only); their sensitivity tables, current consumption and errata are not in this KB.
- SX127x errata sheet contents not transcribed.
- SX1272/SX1273 BW set (believed 125/250/500 kHz only) not re-verified.
- STM32WL figures come from search summaries of ST/Seeed documents (ST pages timed out).
- AN1200.37 was read on 2026-10-03 (W5-S1): thermal arithmetic and the crystal/TCXO advice are in the reference-design section. The reference-design BOM values themselves are not public (AN1200.40: on request).
- The PE4259 truth table comes from a search summary of the pSemi datasheet; re-read the datasheet before relying on the pin-6 behaviour. The ANT_SW role is read from the schematic, not from a Semtech statement.
- The ToF CRLB factor of 2 (Müller et al. eq. 4 as transcribed vs their stated 1.26 m) is unresolved. The SX1280 datasheet ranging chapter could not be downloaded in this pass.

## Sources
1. Semtech, *SX1276/77/78/79 Datasheet* Rev 7 (May 2020) — variant table, PA_BOOST/+20 dBm limits, OCP formula, RSSI formulas, SF6 settings, sync word, FEI/AFC, errata references. (datasheet)
2. Semtech, *SX1261/2 Datasheet* Rev 1.2 (June 2019), and Rev 2.2 register table — power consumption, PA settings Table 13-21, OCP Table 5-2, TCXO control, image calibration Table 9-2, Rx boosted 0x08AC, CAD, sync-word registers, §15 known limitations. https://cdn.sparkfun.com/assets/6/b/5/1/4/SX1262_datasheet.pdf (datasheet)
3. DreamLNK, *DL-LLCC68-S datasheet* (LCSC C2894790) — LLCC68 SF/BW limits and sensitivity. (module datasheet)
4. Semtech, LR1110 product page (accessed 2026-09-27) — 150–960 MHz, +22/+15 dBm, GNSS/Wi-Fi scanning, LR-FHSS, SX126x compatibility. (vendor web)
5. Semtech, LR1121 product page (accessed 2026-09-27) — bands incl. S-band and L-band, +22 dBm sub-GHz, 2.4 GHz power, AES-128. (vendor web)
6. Semtech, LR2021 product page (accessed 2026-09-27; datasheet v2.2 dated 2026-08-08) — bands, FLRC-burst 2.6 Mb/s, −141.5 dBm, TCXO-free claim. (vendor web)
7. Semtech, *SX1280/SX1281/SX1282 Datasheet* Rev 3.0 (July 2019) — +12.5 dBm, LoRa BW 203–1625 kHz, sensitivities, FLRC, ranging engine, frequency-error rules. (datasheet)
8. ST STM32WLE5 datasheet (st.com, via search summary) and Seeed LoRa-E5 (STM32WLE5JC) listing — Cortex-M4 + SX126x die, 22 dBm, −136.5 dBm SF12/125. (datasheet/vendor — not fetched in full)
9. Semtech, SX1272 product page (accessed 2026-09-27) — 860–1000 MHz, +20 dBm, −137 dBm, 10 mA RX. (vendor web)
10. Semtech, SX1268 product page (accessed 2026-09-27) — 410–810 MHz, +22 dBm, −148 dBm, 4.6 mA. (vendor web)
11. Semtech, *AN1200.14* Rev 2.1 (2018) — reference designs use 32 MHz low-g crystals. (app note)
12. `tools/verify/s1_ranging_error.py` — numbers in the ranging section. (own verification)
13. Semtech, *AN1200.40 SX1261/2 Reference Design Explanation* Rev 1.1 (May 2018) — E406V03A/E428V03A/E449V01A, PA bias via VR_PA choke, match/notch/π-filter topology and the ¾-L3 notch rule, SX1261 915 MHz Z_opt 11.7 + j4.8 Ω (14.6 dBm), LNA source Z_opt 74 + j134 Ω, BOMs on request. https://cdn-reichelt.de/documents/datenblatt/A200/SX1262REFERENCE.pdf (app note)
14. pSemi, *PE4259 SPDT RF switch datasheet* (DOC-03694) — single-pin vs complementary control, CTRL high → RF1, isolation 29 dB and IL 0.35 dB at 1 GHz. https://www.psemi.com/pdf/datasheets/pe4259ds.pdf (datasheet — via search summary)
15. Semtech, *AN1200.37 Recommendations for Best Performance* Rev 1.1 (Jan 2018) — 389 mW in / 158 mW out / 231 mW dissipated at +22 dBm, crystal drift from PA heat, thermal-relief cuts, TCXO for ~1 s packets, NDK NX2016SA/NT2016SA. https://cdn.sparkfun.com/assets/f/f/b/4/2/SX1262_AN-Recommendations_for_Best_Performance.pdf (app note)
16. P. Müller, H. Stoll, L. Sarperi, C. Schüpbach, "Outdoor Ranging and Positioning based on LoRa Modulation," ICL-GNSS 2021, doi:10.1109/ICL-GNSS51451.2021.9452277 — SX1280 two-way ranging, clock-offset error, c/BW multipath resolution, CRLB, cable calibration, 46.4 m mean error to 1.4 km, 30 m / 5 m DRMS positioning. (peer-reviewed conference)
17. D. Plets et al., "Experimental Performance Evaluation of Outdoor TDoA and RSS Positioning in a Public LoRa Network," IPIN 2018 — ≈ 150 m median TDoA (as cited in [16]). (peer-reviewed conference; via citation)
18. M. Brzynska, K. Klimaszewski, K. Martin, "A Localisation and Telemetry LoRa Node for Rockets," SoftCOM 2023 — 40 m TDoA error in ground tests. (peer-reviewed conference; via [rocket telemetry](rocket-telemetry-radio-design.md))
19. N. Patwari, J. N. Ash, S. Kyperountas, A. O. Hero III, R. L. Moses, N. S. Correal, "Locating the nodes: cooperative localization in wireless sensor networks," *IEEE Signal Processing Magazine* 22(4):54–69, 2005 — RSS ranging CRB ∝ (ln10/10)σ/n. (peer-reviewed; from memory of the standard result, re-derived in the script; bibliographic data checked against Crossref by W5-S18b, 2026-10-13)
20. Semtech, *AN1200.89 Theory and Principle of Advanced Ranging* v2.0 (Apr 2024) — RTToF principle, multipath over-estimation, HDOP, passive advanced-ranging mode. https://www.semtech.com/uploads/technology/LoRa/theory-and-principle-of-advanced-ranging.pdf (app note)
