---
title: RF transceiver ICs — sub-GHz packet radios, radio SoCs, IQ/SDR transceivers and GNSS front-ends (selection guide)
domain: 18-components-parts
slug: rf-transceiver-ics
tags: [transceiver, cc1101, cc1200, cc1125, cc1310, cc1352p, si4463, efr32fg23, s2-lp, stm32wl, nrf52840, nrf5340, nrf54l15, esp32-s3, at86rf215, sx1255, sx1257, ad9361, ad9363, ad9364, adrv9002, lms7002m, max2769, lcsc, jlcpcb]
prerequisites:
  - ../07-noise-linearity/sensitivity-and-mds.md
  - ../07-noise-linearity/noise-figure-and-friis.md
  - ../15-lora-ism-radios/other-ism-radios-fsk-2g4.md
related:
  - ../15-lora-ism-radios/semtech-chip-family.md
  - ../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md
  - ../15-lora-ism-radios/rocket-telemetry-radio-design.md
  - ../14-sdr-dsp/iq-complex-baseband.md
  - ../04-real-components-hf/crystals-and-resonators.md
  - lna-pa-gain-block-mmics.md
  - rf-modules.md
  - adcs-dacs-for-sdr.md
  - sourcing-and-eval-boards.md
level: intermediate
confidence: medium
last_updated: 2026-10-13
---

# RF transceiver ICs — selection guide

## Questions this page answers
- Which radio chip should I put on my next rocket flight computer or ground station, other than a LoRa chip?
- How do I compare a CC1101, CC1200, Si4463 and SX1262 fairly when their datasheets quote sensitivity at different data rates?
- Is there a cheap chip that gives me raw I/Q samples so I can run my own waveform, like a mini SDR?
- What is the difference between the AD9361, AD9363 and AD9364, and are the "AD9361" Pluto clones real?
- Which of these chips can JLCPCB actually assemble from LCSC stock, and roughly what do they cost?
- Do I need an external LNA or PA (range extender) in front of the chip, and how much does it buy me?
- Should I design in a bare GNSS front-end IC (MAX2769) or just use a GNSS module?

## TL;DR
- **Four families**: (1) *packet transceivers* with the modem on chip (CC1101, CC1200/CC1125, Si4463, S2-LP, SX126x) driven by an MCU over SPI; (2) *radio SoCs* with MCU + radio on one die (CC1310/CC1312/CC1352, EFR32FG23, STM32WL, nRF52/53/54, ESP32); (3) *IQ transceivers* that output baseband samples (AT86RF215, SX1255/SX1257, AD936x, ADRV9002, LMS7002M) — you write the modem; (4) *GNSS front-ends* (MAX2769B) — almost always replaced by a module (see [rf-modules](rf-modules.md)).
- **Compare sensitivity by figure of merit** $FOM = S - 10\log_{10}R_b + 174$ dB (lower is better) [see 15-other-ISM]. From the datasheet numbers collected here: LoRa ≈ 13 dB; AT86RF215 MR-O-QPSK ≈ 13 dB; EFR32FG23 GFSK 15–17 dB; CC1125/CC1310 at 50 kb/s ≈ 17 dB; CC1200 18–20 dB; Si4463 ≈ 21 dB; CC1101 ≈ 30 dB (old, wide filters).
- **Best general sub-GHz FSK picks (2026)**: **CC1200** (137–950 MHz bands, +16 dBm, −109 dBm @ 50 kb/s, 1.25 Mb/s max) [2]; **Si4463-C2A** (142–1050 MHz, +20 dBm, cheapest in LCSC stock at ~US$1.7) [8]; **EFR32FG23** if you want the MCU included (+20 dBm, −111.5 dBm @ 38.4 kb/s) [10]. CC1101 still works for simple links but is 10 dB worse per bit.
- **SDR-like custom radios on a budget**: **AT86RF215** — 389.5–510, 779–1020 and 2400–2483.5 MHz, two independent radios, 13-bit I/Q over LVDS at up to 4 MS/s, +14.5 dBm, NF < 5 dB, 1.8–3.6 V, QFN-48, ~US$13 [11]; it is the heart of the CaribouLite RPi HAT [22]. **SX1255/SX1257** (400–510 / 862–1020 MHz, 500 kHz BW) are the IQ front-ends in LoRa gateways [12].
- **Wideband SDR/radar**: **AD9361** (70 MHz–6 GHz, 2×2, 200 kHz–56 MHz BW), **AD9364** (1×1, same range), **AD9363** (325 MHz–3.8 GHz, ≤ 20 MHz BW; the PlutoSDR chip) [13]; **ADRV9002** (30–6000 MHz, 12 kHz–40 MHz BW, low power) [14]; **LMS7002M** (100 kHz–3.8 GHz, 2×2, up to 160 MHz RF BW) [15]. These are BGA parts (AD9361 BGA-144 at ~US$127 at LCSC, 30 in stock) — buy a board unless you have a strong reason (see [adcs-dacs-for-sdr](adcs-dacs-for-sdr.md)).
- **Every RF IC at JLCPCB is an "extended" part** (no basic RF parts; one-off feeder fee per unique part). LCSC stock is deep for SX1262, LLCC68, SX1280, CC1101, Si4463, nRF52832/52840/5340, ESP32-S3 modules; thin (≤ 100) for AD936x, AT86RF215, SX1255, MAX2769B [21].
- **Range extenders**: CC1190 (850–950 MHz, +27 dBm, LNA NF 2.9 dB) [6], SE2435L, SKY66423-11 (sub-GHz); CC2592, RFX2401C, nRF21540 (2.4 GHz). An LNA helps only if the chip's own NF is poor — typically 2–4 dB of sensitivity, not the 6 dB marketing number (worked example below).

## Intuition (no math)
A radio chip is a receiver front end (LNA, mixer, filters), a synthesiser, a transmitter (PA), and a "modem" that turns bits into waveforms and back. Families differ in **how much of the modem is fixed in silicon**:

- A **packet transceiver** has a fixed menu of modulations (FSK/GFSK/4-FSK/OOK, sometimes LoRa or O-QPSK) and a packet engine (preamble, sync word, CRC, FIFO). You configure registers, write bytes, and it does the rest. Fast to use, cheap, low current, but you cannot invent a new waveform.
- A **radio SoC** is the same radio with a microcontroller on the same die and vendor protocol stacks (BLE, Thread, Wi-SUN, Sidewalk). One chip replaces MCU + radio; you are tied to the vendor SDK.
- An **IQ transceiver** stops at the ADC/DAC: it hands you complex baseband samples (see [IQ and complex baseband](../14-sdr-dsp/iq-complex-baseband.md)). Any waveform your processor or FPGA can generate is possible — chirps for radar, custom FSK with FEC, a software LoRa modem — at the price of writing DSP and moving a lot of data.
- A **GNSS front-end** is an IQ receiver hard-wired for 1.57 GHz with 1–3-bit ADC outputs; the correlators live in your FPGA/CPU. Modules integrate the correlator engine and are what almost everyone should use.

For a rocket, the decisive specifications are: frequency coverage of your legal band (433/868/915/923 MHz in Singapore — see [ISM band plans](../15-lora-ism-radios/ism-band-plans-duty-cycle.md)), output power, sensitivity *at the data rate you need*, tolerance to frequency error and Doppler, blocking (a nearby transmitter on the pad), supply current bursts, package (can JLC place it, can you rework it), and the firmware ecosystem (RadioLib, vendor SDK).

## The math
### Level 1 — sensitivity, and why you must normalise it
A receiver's sensitivity is
$$S = -174\ \text{dBm/Hz} + 10\log_{10}B_n + NF + SNR_{min}$$
where $B_n$ (Hz) is the noise bandwidth, $NF$ (dB) the receiver noise figure and $SNR_{min}$ (dB) the SNR the demodulator needs for the specified error rate ([sensitivity & MDS](../07-noise-linearity/sensitivity-and-mds.md)). Vendors quote $S$ at whatever rate looks best (CC1125: −129 dBm "at 300 b/s"). Dividing out the bit rate $R_b$ gives a rate-independent figure of merit
$$FOM = S - 10\log_{10}R_b + 174 = NF + \left(\frac{E_b}{N_0}\right)_{req} + \text{filter/implementation loss}\ \ [\text{dB}]$$
(derivation in [other ISM radios](../15-lora-ism-radios/other-ism-radios-fsk-2g4.md)). Two chips with the same FOM give the same range at the same bit rate and power.

### Level 2 — FOM table from the datasheet numbers on this page
Computed with the snippet in *How to simulate / verify* (test conditions differ: 1 % PER, BER 0.1 %, BLE 30.8 % PER — treat ±2 dB as noise):

| Chip / mode | S (dBm) | $R_b$ | FOM (dB) | Source |
|---|---|---|---|---|
| AT86RF215 MR-O-QPSK | −123 | 6.25 kb/s | 13.0 | [11] |
| EFR32FG23 GFSK 868 MHz | −125.3 | 2.4 kb/s | 14.9 | [10] |
| EFR32FG23 FSK 868 MHz | −111.5 | 38.4 kb/s | 16.7 | [10] |
| EFR32FG23 GFSK 915 MHz | −96.9 | 2 Mb/s | 14.1 | [10] |
| CC1125 | −110 | 50 kb/s | 17.0 | [3] |
| CC1310 | −110 | 50 kb/s | 17.0 | [4] |
| CC1200 | −109 | 50 kb/s | 18.0 | [2] |
| CC1200 | −123 | 1.2 kb/s | 20.2 | [2] |
| ESP32-S3 BLE coded | −104.5 | 125 kb/s | 18.5 | [17] |
| Si4463 (B1 rev.) | −126 | 500 b/s | 21.0 | [9] |
| CC1101 (433 MHz) | −116 | 0.6 kBaud | 30.2 | [1] |
| SX1262 LoRa SF12/125 (for reference) | −137 | 244 b/s | 13.1 | [25] |

Observations: (i) modern FSK SoCs (FG23, CC13xx, CC1125) are within 2–4 dB of LoRa per bit; (ii) the CC1101 is ~13 dB worse per bit at low rates because its narrowest channel filter is wide relative to 600 b/s — at 38–250 kb/s it closes the gap; (iii) FOMs at very low rates are worse than at medium rates for most FSK chips because crystal-limited filter bandwidth, not thermal noise, sets the floor — which is exactly why frequency accuracy (TCXO) matters ([crystals & TCXOs](../04-real-components-hf/crystals-and-resonators.md)).

### Level 3 — what an external LNA/PA front end really buys
With a front-end LNA of gain $G_1$ and noise figure $F_1$ ahead of a chip with noise factor $F_2$ (all linear),
$$F_{sys} = F_1 + \frac{F_2 - 1}{G_1}$$
([Friis](../07-noise-linearity/noise-figure-and-friis.md)). The sensitivity gain is $NF_2 - NF_{sys}$ — large only when $NF_2$ is large. On transmit, an external PA adds $P_{out,ext} - P_{out,chip}$ dB directly to the link budget but costs supply current, harmonics (needs a low-pass filter: [filter parts](filter-parts-saw-ceramic-ltcc.md)) and, in Singapore's SRD bands, may exceed the legal ERP (see 19-regulations). For IQ transceivers, the useful dynamic range is set by NF at the bottom and by the ADC full-scale/AGC at the top; the ideal quantisation SNR of a 13-bit converter is $6.02\cdot13 + 1.76 = 80$ dB over the full sample bandwidth, and a narrowband signal gains a further $10\log_{10}(f_s/B)$ of processing gain ([data converters](../05-analog-electronics/data-converters-adc-dac.md)).

## Design equations & rules of thumb
| Rule | When valid | Typical values |
|---|---|---|
| $FOM = S - 10\log_{10}R_b + 174$ | comparing chips at different rates | LoRa 13 dB, good FSK 15–18, legacy FSK 24–30 |
| Sensitivity gain from external LNA = $NF_{chip} - NF_{sys}$ | LNA directly at antenna, after only a SAW/switch | 2–4 dB for modern chips (NF 5–7 dB) |
| TCXO needed if $f\cdot\Delta_{ppm} >$ ~25 % of RX bandwidth | narrowband FSK < 10 kHz BW, LoRa SF ≥ 11 at 125 kHz | 915 MHz × 10 ppm = 9.15 kHz |
| PA current ≈ $P_{out}/(\eta V_{DD})$ | sizing regulators and batteries | CC1190 +26 dBm at PAE 50 % → ~0.4 W/3.3 V ≈ 0.24 A |
| IQ data rate = $2 \times N_{bits} \times f_s$ | sizing the host link | AT86RF215 13 bit × 2 × 4 MS/s ≈ 104 Mb/s (+framing) |
| Guaranteed tuning range only | AD9363/ADRV/SX1255 | using a chip outside its datasheet range is unsupported even if it "works" |

## Comparison tables (specs as of 2026-09; LCSC data from the 2026-04 snapshot [21])
Prices are LCSC/JLC unit price at qty 1 in USD (JLC charges the same part plus a per-unique-part feeder fee for extended parts); Mouser/Digikey prices are typically 1.2–2× higher for small quantities (unverified general observation). "Stock" = LCSC units in the snapshot.

### A. Sub-GHz packet transceivers (MCU drives over SPI)
| Part | Bands | Max P_out | Best sensitivity quoted | Max rate | RX current | Package | LCSC / stock / US$ | Notes |
|---|---|---|---|---|---|---|---|---|
| **TI CC1200** | 137–158.3, 164–190, 205–237.5, 274–316.6, 410–475, 820–950 MHz | +16 dBm | −123 dBm @ 1.2 kb/s; −109 @ 50 kb/s | 1.25 Mb/s | 19–23 mA peak | VQFN-32 5×5 | C122881 / 965 / 2.83 | 86 dB blocking @ 10 MHz, 60 dB ACS @ 12.5 kHz [2]; AltOS/TeleMetrum family uses CC11xx/CC1200 [25] |
| TI CC1125 / CC1120 | 164–192, 410–480, 820–960 MHz (CC112x family) | +16 dBm | −129 dBm @ 300 b/s; −110 @ 50 kb/s | 200 kb/s | 17–26 mA peak | QFN-32 5×5 | C133234 / 721 / 3.11 (CC1125); C66751 / 9.4k / 2.17 (CC1120) | narrowband champion: 104 dB blocking @ 10 MHz, 67 dB ACS @ 6.25 kHz [3] |
| TI CC1101 | 300–348, 387–464, 779–928 MHz | +12 dBm | −116 dBm @ 0.6 kBaud (433) | 600 kb/s | ~14.5 mA | QFN-20 4×4 | C29953 / 7.9k / 1.26 | old (2006-era), huge community, RadioLib support; poor FOM [1] |
| **SiLabs Si4463-C2A** | 142–1050 MHz | +20 dBm (Si4461 +16, Si4460 +13) | −129 dBm (rate not stated on p.1) | 1 Mb/s | 10/13 mA | QFN-20 4×4 | C476202 / 22k / 1.69 | 69 dB ACS, 79 dB blocking @ 1 MHz; built-in ramp control for an external FET PA to +27/+30 dBm [8]; production promised to ≥ 2036 |
| ST S2-LP | 413–479, 826–958 MHz (S2-LPQTR; S2-LPCBQTR: 452–527, 904–1055) | +14 dBm (+16 dBm boost mode) | −128 dBm @ 0.3 kb/s 2-FSK (electrical table; feature list says "down to −130") | 500 kb/s | 7.2 mA (LPM) / 8.6 mA (HPM) at 868 MHz | QFN-24 4×4 | C880591 / 1.7k / 2.10 | ST DS11896 Rev 9 electrical tables [26] (checked 2026-10-13); very low RX current, Sigfox-capable |
| Semtech SX1262 / SX1268 / LLCC68 | 150–960 / 410–810 / 150–960 MHz | +22 dBm | LoRa −148 dBm | 62.5 kb/s LoRa, 300 kb/s GFSK | 4.6 mA | QFN-24 4×4 | C191341 / 10k / 2.96; C244368 / 5k / 2.72; C5120261 / 16.5k / 1.81 | full detail in [Semtech family](../15-lora-ism-radios/semtech-chip-family.md) |
| Semtech SX1276 / SX1278 | 137–1020 / 137–525 MHz | +20 dBm | −148 dBm | 300 kb/s FSK | ~10 mA | QFN-28 6×6 | C80171 / 8.5k / 4.93; C67678 / 4.1k / 3.92 | legacy; prefer SX126x for new designs |
| ADI ADF7021 | 80–650, 862–950 MHz | +13 dBm | ~−130 dBm (narrowband, unverified) | 32 kb/s | ~25 mA | LFCSP-48 7×7 | C206881 / 240 / 10.99 | narrowband 2/3/4-FSK; used in amateur digital-voice hotspots (anecdotal) |

### B. Sub-GHz radio SoCs (MCU + radio)
| Part | CPU / memory | Bands | Max P_out | Sensitivity | RX / TX current | Package | LCSC / stock / US$ |
|---|---|---|---|---|---|---|---|
| **TI CC1310** | Cortex-M3 48 MHz, 32–128 KB flash | 287–351, 359–439, 431–527, 718–878, 861–1054 MHz | +15 dBm | −124 dBm long-range mode; −110 @ 50 kb/s | 5.4 mA / 13.4 mA @ +10 dBm | VQFN-32/48 | C84353 (F128 RGZ) / 5k / 2.81 [4] |
| TI CC1312R | Cortex-M4F, 352 KB flash | sub-GHz | +14 dBm | similar to CC1310 | | VQFN-48 7×7 | C543014 / 5.3k / 3.47 |
| **TI CC1352P** | Cortex-M4F 48 MHz, 352 KB flash, 80 KB SRAM | 431–527, 861–1054, 1069–1329, 2360–2500 MHz | **+20 dBm** (temp-compensated) | −121 dBm LRM; −105 dBm BLE coded | 5.8 mA / 63 mA @ +20 dBm 915 MHz | VQFN-48 7×7 | C2151654 / 37 / 4.89 [5] |
| **SiLabs EFR32FG23** | Cortex-M33 78 MHz, up to 512 KB flash | sub-GHz | +14 or **+20 dBm** variants | −125.3 @ 2.4 kb/s; −111.5 @ 38.4 kb/s; −110.7 @ 100 kb/s 433 MHz | 3.7–5.1 mA / 85.5 mA @ +20 dBm | QFN-40/48 | not in snapshot (FG25 C6612121 / 25 / 11.38) [10] |
| ST STM32WLE5 / WL55 | Cortex-M4 (+M0+ on WL55) | 150–960 MHz | +22 / +15 dBm | SX126x-class LoRa + (G)FSK | | UFQFPN-48 | C2888218 / 625 / 3.49 (WLE5CC); C5270474 / 63 / 8.21 (WL55CC) — see [Semtech family](../15-lora-ism-radios/semtech-chip-family.md) |

### C. 2.4 GHz SoCs (BLE / 802.15.4 / Wi-Fi)
| Part | Radio | Max P_out | Sensitivity | Package | LCSC / stock / US$ | Notes |
|---|---|---|---|---|---|---|
| Nordic nRF52840 | BLE 5 (coded PHY), 802.15.4, 2 Mb/s proprietary | +8 dBm | −103 dBm BLE 125 kb/s [25] | aQFN-73 7×7 (0.5 mm pitch, fine) / WLCSP | C190794 / 5k / 6.00 | USB; RAK4631 core; aQFN needs good stencil/paste — JLC can place it |
| Nordic nRF52832 | BLE 5 (no coded PHY) | +4 dBm | −96 dBm 1 Mb/s (unverified) | QFN-48 6×6 | C77540 / 23.7k / 3.71 | cheapest Nordic that is easy to route |
| Nordic nRF5340 | BLE 5.x, 802.15.4, dual Cortex-M33 | +3 dBm (unverified) | ~−98 dBm 1 Mb/s (unverified) | aQFN-94 7×7 | C3015611 / 11.5k / 7.43 | needs nRF21540 FEM for range |
| Nordic nRF54L15 | BLE 6, 802.15.4, M33 128 MHz, 1.5 MB NVM | +8 dBm | −96…−98 dBm 1 Mb/s (sources disagree) [19] | QFN-48 6×6 | C42458750 / 1.7k / 3.58 | the new default Nordic part (2025+) |
| Espressif ESP32-S3 | Wi-Fi 4 2.4 GHz + BLE 5 (coded) | 21 dBm (11b), 20 dBm BLE | −98.4 dBm 11b 1 Mb/s; −104.5 dBm BLE 125 kb/s [17] | QFN-56 7×7 | C2913194 (S3R8) / 3.1k / 3.12 | use the **module** (certified) — [rf-modules](rf-modules.md) |
| Espressif ESP32-C6 / H2 / C5 | C6: Wi-Fi 6 + BLE + 802.15.4 [18]; H2: BLE + 802.15.4; C5: dual-band 2.4/5 GHz Wi-Fi 6 | ~20 dBm | | QFN | H2 C22470214 / 5.7k / 1.90; C5 C51950746 / 631 / 3.55 | |
| TI CC2340R5 | BLE 5.3 | +8 dBm (unverified) | | VQFN-24 | C20416850 / 6.8k / 1.25 | very cheap BLE |
| Semtech SX1280/81 | 2.4 GHz LoRa, FLRC, GFSK, ranging | +12.5 dBm | −132 dBm LoRa | QFN-24 | C125969 / 14k / 3.94 | [Semtech family](../15-lora-ism-radios/semtech-chip-family.md); ExpressLRS hardware |

### D. IQ / SDR-style transceivers (you write the modem)
| Part | RF range | Channels | IQ interface / BW | TX power | Package | LCSC / stock / US$ | Use for |
|---|---|---|---|---|---|---|---|
| **Microchip AT86RF215** (also -IQ variant without baseband) | 389.5–510, 779–1020, 2400–2483.5 MHz | 2 independent TRX (sub-GHz + 2.4 GHz) | 13-bit I/Q, LVDS, $f_s$ ≤ 4 MHz; also full 802.15.4g MR-FSK/OFDM/O-QPSK modems | +14.5 dBm @ 900 MHz; 62 mA @ 14 dBm | QFN-48 7×7 | C1526155 / 5 / 12.92 | custom waveforms at 433/915 MHz, software LoRa, radar experiments, CaribouLite [11][22] |
| Semtech SX1255 / SX1257 | 400–510 / 862–1020 MHz | 1 TRX | Zero-IF, digital I/Q (sigma-delta TX bitstream), ≤ 500 kHz BW | ~+5 dBm driver (unverified) | QFN-32 5×5 | C89372 (SX1255) / 70 / 6.84 | LoRa gateway front ends (SX1301/SX1302 + SX125x) [12] |
| **ADI AD9361** | 70 MHz–6 GHz | 2×2 | 12-bit, 200 kHz–56 MHz channel BW, LVDS/CMOS | ~+7 dBm (unverified) | BGA-144 10×10 | C515884 / 30 / 127.5 | USRP B210, bladeRF-class designs [13] |
| ADI AD9364 | 70 MHz–6 GHz | 1×1 | same as AD9361 | | BGA-144 | not in snapshot | USRP B200/B205mini [13] |
| ADI AD9363 | 325 MHz–3.8 GHz (one secondary source says 380 MHz) | 2×2 | 12-bit, ≤ 20 MHz BW | | BGA-144 | C653459 / 7 / 72.9 | ADALM-PLUTO; firmware hack extends tuning but performance outside spec is unguaranteed [13] |
| ADI ADRV9002 | 30–6000 MHz | 2×2 | 12 kHz–40 MHz BW, narrowband + wideband profiles, low power | | BGA-196 | not in snapshot | battery-powered SDR, land-mobile radio [14] |
| ADI AD9371 / ADRV9009 | 300 MHz–6 GHz (AD9371) / 75 MHz–6 GHz (ADRV9009) (unverified) | 2×2 | up to 100/200 MHz BW class, JESD204B | | BGA-196 | C578841 / 58 / 184; C659657 / 10 / 283 | FPGA-heavy wideband systems — not a first project |
| Lime LMS7002M | 100 kHz–3.8 GHz | 2×2 | 12-bit, up to 160 MHz RF BW (80 MHz baseband) | | aQFN-261 (fine pitch) | LCSC listing exists (C5752085), not in snapshot | LimeSDR family [15] |

### E. GNSS front-end ICs (module alternatives are in [rf-modules](rf-modules.md))
| Part | Bands | Key spec | Output | Package | LCSC / stock / US$ | Notes |
|---|---|---|---|---|---|---|
| ADI/Maxim **MAX2769B** (original MAX2769, also MAX2769C) | GPS/Galileo/GLONASS L1 | cascaded NF ≈ 1.4–1.5 dB incl. on-chip LNA (0.8 dB first stage); IF filter BW 2.6/4.6/8.6/24 MHz [16] | 1–3-bit ADC or analog IF | TQFN-28 5×5 | C118482 / 55 / 4.49 | classic GNSS-SDR front end (research receivers); use a module for flight |
| ZHONGKEWEI AT6558R | BDS/GPS/GLONASS SoC | full receiver chip (inside ATGM336H) | NMEA | QFN-40 5×5 | C500608 / 8.3k / 0.66 | cheap Chinese GNSS SoC; limited documentation |
| u-blox UBX-M10050 | GPS/GAL/BDS/GLO L1 | the chip inside MAX-M10S | UBX/NMEA | chip | C44571738 / 102 / 4.84 | chip-down design needs u-blox HW integration manual + SAW/LNA |

## Worked examples
### 1. Which FSK chip for a 50 kb/s, 433 MHz rocket downlink?
Requirement: 50 kb/s GFSK, legal 433 MHz SRD channel, 10 mW-class ERP, want margin at 20 km. Sensitivities at 50 kb/s: CC1125 −110 dBm, CC1310 −110 dBm, CC1200 −109 dBm [2][3][4]; Si4463 is not quoted at 50 kb/s on page 1, so scale from its FOM ≈ 21 dB: $S \approx 21 + 10\log_{10}(5\times10^4) - 174 = -106$ dBm. At equal TX power the CC1125/CC1310 buy ~4 dB (≈ 1.6× range in free space) over the Si4463; the CC1200 costs 1 dB versus the CC1125 but offers 1.25 Mb/s for a pad-side high-rate dump. The SX1262 in GFSK mode is similar (FOM 16–19 dB, [other ISM](../15-lora-ism-radios/other-ism-radios-fsk-2g4.md)) and gives LoRa as a fallback on the same footprint — the reason it is the default recommendation in [rocket telemetry radio design](../15-lora-ism-radios/rocket-telemetry-radio-design.md).

### 2. How much does a CC1190 range extender improve a 915 MHz receiver?
CC1190 LNA path: NF 2.9 dB *including* its T/R switch and antenna match, gain ≈ 11 dB (assumed from TI's high-gain mode; verify in the CC1190 datasheet tables) [6]. Chip NF unknown — try 6, 7, 8 and 10 dB:
- $NF_{chip}$ = 6 dB → $F_{sys} = 10^{0.29} + (10^{0.6}-1)/10^{1.1} = 1.95 + 0.24 = 2.19$ → 3.4 dB → gain **2.6 dB**.
- 7 dB → 3.56 dB (gain 3.4 dB); 8 dB → 3.75 dB (4.3 dB); 10 dB → 4.26 dB (5.7 dB).
TI's "6 dB typical sensitivity improvement" therefore implies a chip NF near 10 dB (older CC11xx parts). With a modern SX1262 (NF ≈ 6 dB class) expect 2–3 dB on receive; the bigger win is on transmit: +27 dBm vs +14–16 dBm is +11–13 dB (subject to legal limits).

### 3. Is a 4 MS/s, 13-bit IQ radio enough for software LoRa at 433 MHz?
AT86RF215 at $f_s$ = 4 MS/s complex: thermal noise in 4 MHz with NF 5 dB is $-174 + 66.0 + 5 = -103$ dBm. A LoRa SF12/125 kHz signal needs SNR ≈ −20 dB in 125 kHz: $S \approx -174 + 51.0 + 5 - 20 = -138$ dBm, i.e. 35 dB *below* the wideband noise — fine, because the signal is recovered by processing gain (channel filtering, $10\log_{10}(f_s/B)$ = 15.1 dB for complex IQ at 4 MS/s into 125 kHz — use $f_s/2B$ for a real ADC — then LoRa despreading for the rest), and the 80 dB ideal quantisation SNR of 13 bits leaves ample headroom as long as AGC keeps strong pad-side signals from clipping. The practical limits are CPU/FPGA throughput and the chip's AGC/blocking, not the ADC (software LoRa decoder performance vs silicon is **unverified** here).

## Practical notes
- **Reference oscillator**: every chip here needs a crystal or TCXO (26 MHz for AT86RF215, 30 MHz typical for Si446x, 32 MHz for SX126x, 40 MHz for CC1200/CC1125 — check each datasheet). For narrowband FSK (< 25 kHz channels), LoRa SF ≥ 10 or large temperature swings in a rocket, use a TCXO (±0.5–2 ppm) — see [crystals & resonators](../04-real-components-hf/crystals-and-resonators.md) and [mixers/PLLs/VCOs parts](mixers-plls-vcos-parts.md) for TCXO part numbers.
- **Copy the reference design exactly**: the matching/balun/harmonic filter values in TI/SiLabs/Semtech reference designs assume their layout, stack-up and component series (Murata LQW/LQG, Johanson). Changing the inductor series shifts the match; see [inductors at RF](../04-real-components-hf/inductors-at-rf.md).
- **Packages and JLC assembly**: QFN-20…48 with exposed pad are routine at JLC. The nRF52840 aQFN-73 and nRF5340 aQFN-94 need ≥ 4 layers and via-in-pad or careful fan-out; AD936x BGA-144 (0.8 mm pitch) needs 6+ layers — JLC can place BGAs, but a failed BGA is a scrapped board. Hand rework of QFN exposed pads needs hot air; BGAs need a reball station.
- **Firmware ecosystem**: RadioLib (Arduino/ESP-IDF/Pico) supports CC1101, Si443x, nRF24, RF69, SX126x/SX127x/SX128x, LR11x0, STM32WL (project documentation [20]; check current list). CC1200/CC1125 are configured with TI SmartRF Studio register exports; Si446x with SiLabs WDS/"radio_config.h"; AT86RF215 with Microchip stacks or community drivers (CaribouLite code) — budget time accordingly.
- **Current bursts**: a +20 dBm PA draws 60–90 mA (CC1352P 63 mA at 915 MHz [5]; EFR32FG23 85.5 mA [10]); with an external +27–30 dBm PA it is 0.3–0.6 A — size the regulator and decoupling ([power supplies for RF](../05-analog-electronics/power-supplies-for-rf-and-analog.md)).
- **Lifecycle**: SiLabs publishes a longevity date (Si4463 to ≥ 2036) [8]; TI CC1101 is old but active; MAX2769 has been superseded by MAX2769B/C; check each vendor page before committing.
- **Suspicious listings**: the LCSC snapshot lists a "CC1312R74T0RGZR" under manufacturer "AGM" (not TI) [21] — treat odd manufacturer names on marketplace listings as a red flag (see [sourcing](sourcing-and-eval-boards.md)).

## Recommended picks for Marcus's use cases
| Use case | First choice | Alternative | Why |
|---|---|---|---|
| LoRa rocket downlink (433 / 923 MHz) | SX1262/SX1268 bare or E22-xxxM SPI module | LR1121 (multi-band) | see [Semtech family](../15-lora-ism-radios/semtech-chip-family.md) |
| High-rate FSK downlink (50–250 kb/s) | CC1200 (+CC1190 at 915 MHz) | Si4463-C2A (+20 dBm, cheapest), EFR32FG23 | good FOM, blocking, deep LCSC stock |
| Narrowband long-range beacon (≤ 1.2 kb/s) | CC1125 + TCXO | Si4463 | 104 dB blocking, −129 dBm @ 300 b/s |
| Single-chip sub-GHz node (sensor, recovery beacon) | CC1310 / CC1352P | STM32WLE5 (LoRa) | MCU included, −124 dBm long-range mode |
| Custom waveform / SDR-like at 433/915/2.4 GHz | **AT86RF215** + small FPGA (iCE40/ECP5) | SX1255/57 | real I/Q at low cost and power |
| Wideband SDR, FMCW/pulsed radar prototyping | buy PlutoSDR/LibreSDR/bladeRF/USRP | AD9361/AD9364 chip-down only after that | BGA, power tree, FPGA; see [adcs-dacs-for-sdr](adcs-dacs-for-sdr.md) |
| BLE/Wi-Fi ground link, phone app | ESP32-S3-WROOM/MINI **module** | nRF52840 module | certification carries over (see [rf-modules](rf-modules.md)) |
| GNSS on the flight computer | u-blox MAX-M10S / NEO-M9N module | Quectel LC76G | see [rf-modules](rf-modules.md); MAX2769B only for GNSS-SDR research |

## Parts to avoid (or use knowingly)
- **nRF24L01+ modules** from marketplaces: widely reported to carry clone silicon (e.g. Si24R1) with different sensitivity and register behaviour (forum — anecdotal); FOM ≈ 29 dB even when genuine [25].
- **CC1101** for new long-range designs: ~10 dB worse per bit than CC1125/CC1200.
- **LLCC68** if you need SF ≥ 10 at 125 kHz (not supported) — [Semtech family](../15-lora-ism-radios/semtech-chip-family.md).
- **"AD9361" SDR clones** sold with AD9363 silicon configured as AD9361: reports of different performance and of VCTCXO swaps on HamGeek Pluto+ boards (forum — anecdotal) [24]. Fine for learning; measure before trusting specs.
- **Grey-market BGA transceivers** (AD936x, ADRV) from marketplace sellers: counterfeit/recycled risk and no recourse; buy from ADI, Mouser, Digikey, LCSC (authorised for some lines) — [sourcing](sourcing-and-eval-boards.md).
- **Chip-down GNSS** on a first flight computer: the SAW/LNA/TCXO/layout details are unforgiving; modules exist for a reason.

## Common mistakes & misconceptions
- *"−129 dBm is better than −117 dBm, so chip A has more range."* Only at the same bit rate and error criterion. Normalise with FOM first.
- *"An external LNA always gives 6 dB."* It gives $NF_{chip}-NF_{sys}$; for a 6 dB-NF chip that is ~2.5 dB, and a lossy filter or switch before the LNA eats it back ([receiver cascade](../07-noise-linearity/receiver-cascade-analysis.md)).
- *"The AD9363 is an AD9361 with a software lock."* The datasheet guarantees only 325 MHz–3.8 GHz and 20 MHz BW; outside that you are relying on luck, and a clone's "AD9361" marking may be a relabelled AD9363 [13][24].
- *"The SoC's +20 dBm is legal in Singapore."* Legal ERP depends on the band (see 19-regulations and [ISM band plans](../15-lora-ism-radios/ism-band-plans-duty-cycle.md)).
- *"JLC basic parts will keep my assembly cheap."* No RF IC is a basic part; each unique RF part adds the extended-part fee [21].

## How to simulate / verify
- **FOM and cascade arithmetic** (reproduces the tables above):
```python
import math
fom = lambda S, Rb: S - 10*math.log10(Rb) + 174
print(fom(-109, 50e3), fom(-116, 600), fom(-123, 6250))   # CC1200, CC1101, AT86RF215
lin = lambda d: 10**(d/10)
for nf_chip in (6, 7, 8, 10):                                # CC1190 LNA NF 2.9 dB, G 11 dB
    F = lin(2.9) + (lin(nf_chip) - 1)/lin(11)
    print(nf_chip, round(10*math.log10(F), 2))
```
- **Bench check of sensitivity**: signal generator → step attenuator → DUT, count PER at 1 % while lowering power; or compare two boards by RSSI/SNR at the same attenuation ([17-test-measurement](../17-test-measurement/rf-bring-up-debug-playbook.md), planned).
- **Frequency error**: read the chip's frequency-error estimator (SX126x, CC1200 FREQOFF) across temperature, or measure the carrier with an SDR.
- **Stock/price refresh**: `python3 ~/.claude/skills/jlc-trawler/scripts/trawl.py refresh C122881 C476202 C1526155` (live JLC check) or LCSC product pages.

- Headline specs of the SDR transceiver/tuner chips (AD9361/AD9363/AD9364, LMS7002M, MAX2837, R820T/R828D/R828S) and the boards built on them are summarised, with sources and measured NFs, in [14 SDR hardware survey](../14-sdr-dsp/sdr-hardware-survey.md).

## Open questions / gaps
- nRF5340, nRF52832 and SX1255/57 TX-power figures were not verified from primary datasheets in this pass (sites unreachable) — marked unverified. The S2-LP row was checked against ST DS11896 Rev 9 on 2026-10-13 (W5-S18b) [26].
- CC1200/CC1190 noise figures are not stated on the pages read; the cascade example uses assumed chip NF values.
- AD9363 lower frequency limit: ADI sources say 325 MHz; one secondary article says 380 MHz (contradiction logged).
- Si4463 revision differences: B1 datasheet 119–1050 MHz / −126 dBm @ 500 b/s [9] vs C2A datasheet 142–1050 MHz / −129 dBm [8] — use the C2A numbers for new designs.
- No measured comparison (same board, same antenna) of CC1200 vs SX1262-GFSK vs Si4463 exists in this KB — a good bench project.

## Sources
1. Texas Instruments, *CC1101 Low-Power Sub-1 GHz RF Transceiver* product page, https://www.ti.com/product/CC1101 (accessed 2026-09-27) — bands, +12 dBm, −116 dBm @ 0.6 kBaud, 0.6–600 kb/s. (datasheet/product page)
2. Texas Instruments, *CC1200 High-Performance Sub-1 GHz RF Transceiver* product page, https://www.ti.com/product/CC1200 (accessed 2026-09-27) — bands, +16 dBm, −123/−109 dBm, 1.25 Mb/s, blocking/ACS, currents, VQFN-32. (datasheet/product page)
3. Texas Instruments, *CC1125 Ultra-High Performance RF Narrowband Transceiver* datasheet, https://www.ti.com/lit/ds/symlink/cc1125.pdf, p. 1 — −129 dBm @ 300 b/s, 104 dB blocking, 67 dB ACS @ 6.25 kHz, +16 dBm, 0–200 kb/s. (datasheet)
4. Texas Instruments, *CC1310 SimpleLink Sub-1 GHz Wireless MCU* product page, https://www.ti.com/product/CC1310 — bands, +15 dBm, −124 dBm LRM, −110 dBm @ 50 kb/s, currents. (datasheet/product page)
5. Texas Instruments, *CC1352P SimpleLink multiband wireless MCU with integrated PA* product page, https://www.ti.com/product/CC1352P — bands, +20 dBm, −121/−105 dBm, 63 mA @ +20 dBm. (datasheet/product page)
6. Texas Instruments, *CC1190 850–950 MHz RF Front End* datasheet, https://www.ti.com/lit/ds/symlink/cc1190.pdf, p. 1 — +27 dBm, PAE 50 % @ 26 dBm, LNA NF 2.9 dB, "6 dB typical sensitivity improvement". (datasheet)
7. Texas Instruments, *CC2592 2.4 GHz range extender* datasheet, https://www.ti.com/lit/ds/symlink/cc2592.pdf — +22 dBm, 155 mA, LNA NF 4.7 dB. (datasheet)
8. Silicon Labs, *Si4463/61/60-C High-Performance, Low-Current Transceiver*, Rev 1.0 (10/2014), https://www.silabs.com/documents/public/data-sheets/Si4463-61-60-C.pdf, p. 1; lifecycle note from https://www.silabs.com/wireless/proprietary/ezradiopro-sub-ghz-ics/device.si4463 — 142–1050 MHz, −129 dBm, +20/+16/+13 dBm, 69 dB ACS, 79 dB blocking, production to ≥ 2036. (datasheet)
9. Silicon Labs, *Si4464/63/62/61/60* (B1) datasheet Rev 1.4 (10/2024), https://www.silabs.com/documents/public/data-sheets/Si4464-63-61-60.pdf — 119–1050 MHz, −126 dBm @ 500 b/s (via search-result extract; not re-read in full). (datasheet, secondary extract)
10. Silicon Labs, *EFR32FG23 Wireless SoC Family Data Sheet* (2025), https://www.silabs.com/documents/public/data-sheets/efr32fg23-datasheet.pdf, feature list — sensitivities, currents, +14/+20 dBm. (datasheet)
11. Microchip/Atmel, *AT86RF215 Device Family datasheet* 42415E (05/2016), https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-42415-WIRELESS-AT86RF215_Datasheet.pdf, pp. 1–3 — bands, 13-bit I/Q LVDS ≤ 4 MHz, PHYs, +14.5 dBm, NF < 5 dB, −123 dBm, currents. (datasheet)
12. Semtech, *SX1255* (Rev 3.1, 2018) and *SX1257* (Rev 1.2, 2018) datasheets, Mouser mirrors https://www.mouser.com/datasheet/2/761/SEMT_S_A0005068298_1-2575674.pdf and https://www.mouser.com/datasheet/2/761/DS_SX1257_V1.2-1360316.pdf — zero-IF digital IQ front ends, 500 kHz max BW (via search extract). (datasheet, secondary extract)
13. Analog Devices, *AD9361, AD9364 and AD9363* wiki/system documentation, https://wiki.analog.com/resources/eval/user-guides/ad-fmcomms2-ebz/ad9361 and https://developer.analog.com/docs/system-level/solutions/reference-designs/fmcomms2/common/introduction_to_ad9361_ad9364.html — ranges, bandwidths, channel counts (via search extract; one article cites 380 MHz for AD9363). (manufacturer documentation)
14. Analog Devices, *ADRV9002 Dual Narrow-Band and Wideband RF Transceiver* datasheet Rev A, https://www.analog.com/media/en/technical-documentation/data-sheets/adrv9002.pdf — 30–6000 MHz, 12 kHz–40 MHz (via search extract). (datasheet)
15. Lime Microsystems, *LMS7002M FPRF MIMO Transceiver* datasheet v3.1, https://www.mouser.com/datasheet/2/982/LMS7002M-Data-Sheet-v3.1r00-1600568.pdf; https://limemicro.com/silicon/lms7002m/ — 100 kHz–3.8 GHz, 12-bit, 160 MHz RF BW, 2×2 (via search extract). (datasheet)
16. Analog Devices/Maxim, *MAX2769 Universal GPS Receiver* datasheet, https://www.analog.com/media/en/technical-documentation/data-sheets/max2769.pdf — NF 1.4 dB, IF filter options (via search extract). (datasheet)
17. Espressif, *ESP32-S3 Series Datasheet* v2.2, https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf, §6 RF characteristics — 21 dBm 11b, −98.4 dBm 11b 1 Mb/s, −104.5 dBm BLE 125 kb/s. (datasheet)
18. Espressif, *ESP32-C6 Series Datasheet*, https://www.espressif.com/sites/default/files/documentation/esp32-c6_datasheet_en.pdf, p. 1 — Wi-Fi 6 + BLE 5 + 802.15.4. (datasheet)
19. Nordic Semiconductor, *nRF54L15* product page https://www.nordicsemi.com/Products/nRF54L15 and news release (2023) — +8 dBm, −96/−98 dBm (sources disagree), M33 128 MHz, 1.5 MB NVM (via search extract). (manufacturer)
20. J. Gromes et al., *RadioLib* — universal wireless communication library, https://github.com/jgromes/RadioLib — supported-module list (project documentation; not re-verified in this pass). (software documentation)
21. Local JLCPCB/LCSC assembly-parts database (jlcparts "in-stock" snapshot, newest record 2026-04-01) queried with the `jlc-trawler` tool, ~/jlc-trawler-data/jlcpcb-components.sqlite3 — LCSC numbers, stock, qty-1 prices, basic/extended status. (distributor data; snapshot, re-check before ordering)
22. RTL-SDR.com, *CaribouLite: a 30–6000 MHz 13-bit 4 MHz SDR HAT* (2021), https://www.rtl-sdr.com/cariboulite-a-30-6000-mhz-13-bit-4mhz-sdr-hat-for-the-raspberry-pi/; Crowd Supply project page — AT86RF215 + RFFC5072 + iCE40LP1K. (news/project page)
23. u-blox, *Counterfeit products and u-blox brand misuse*, https://www.u-blox.com/en/counterfeit-products-and-u-blox-brand-misuse. (manufacturer notice)
24. F5OEO/tezuka_fw GitHub discussion #184, *Fixing up the Hamgeek pluto+ AD9363 SDR*, https://github.com/F5OEO/tezuka_fw/discussions/184; SDRstore article on AD9361 vs AD9363 boards. (forum — anecdotal)
25. This KB: [Other ISM radios](../15-lora-ism-radios/other-ism-radios-fsk-2g4.md) (FOM method, nRF52840/nRF24/AltOS numbers) and [Semtech chip family](../15-lora-ism-radios/semtech-chip-family.md). (internal)
26. STMicroelectronics, *S2-LP ultra-low power, high performance, sub-1 GHz transceiver*, data sheet DS11896 Rev 9, Sep 2021 (read with pdftotext from a distributor mirror, cdn.components.ru/media/PDF/3233202.pdf; current ST revision is later) — bands p. 1–2; Table 7 RX current 8.6/7.2 mA; Tables 19–22 sensitivity −128 dBm at 0.3 kb/s, −122 dBm at 1.2 kb/s 2-FSK; PA table +14/+16 dBm (boost) HPM. (datasheet)
