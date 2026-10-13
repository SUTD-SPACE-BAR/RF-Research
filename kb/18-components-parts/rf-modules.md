---
title: RF modules — GNSS (u-blox, Quectel, Unicore, ZHONGKEWEI), Wi-Fi/BLE (ESP32, nRF52), LoRa and telemetry modems, video transmitters and SDR modules; certification and antenna rules (selection guide)
domain: 18-components-parts
slug: rf-modules
tags: [module, gnss, max-m10s, neo-m9n, sam-m10q, zed-f9p, zed-x20p, neo-f10n, l76k, lc76g, lc29h, lg290p, um980, atgm336h, operational-limits, cocom, airborne-4g, esp32-s3-wroom-1, esp32-s3-mini-1, esp32-c6, esp32-c5, nrf52840-module, nina-b3, e73, lora-module, e22, e220, ra-01sc, rak3172, rak4630, sik, rfd900x, vtx, certification, antenna, lcsc]
prerequisites:
  - ../08-antennas/gnss-antennas.md
  - ../19-regulations-safety/certification-fcc-ce-imda.md
related:
  - ../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md
  - ../15-lora-ism-radios/other-ism-radios-fsk-2g4.md
  - ../15-lora-ism-radios/rocket-telemetry-radio-design.md
  - ../14-sdr-dsp/sdr-hardware-survey.md
  - ../08-antennas/pcb-and-chip-antennas.md
  - ../08-antennas/antennas-on-rockets.md
  - ../19-regulations-safety/singapore-imda-rules.md
  - ../09-propagation-link-budget/multipath-fading-doppler.md
  - rf-transceiver-ics.md
  - sourcing-and-eval-boards.md
  - lna-pa-gain-block-mmics.md
level: intermediate
confidence: medium
last_updated: 2026-10-03
---

# RF modules — selection guide

## Questions this page answers
- Which GNSS module should go on the flight computer (single-band, dual-band, RTK), and what are its altitude/velocity/acceleration limits on a rocket?
- Will my GNSS stop working above 500 m/s or 18/50/80 km?
- Which ESP32 or nRF52840 module variant (PCB antenna vs U.FL) should I use, and does its certification still apply?
- Which LoRa/telemetry modules are in LCSC stock for JLC assembly?
- What about video transmitters and SDR modules?
- What antenna rules come with a certified module?

## TL;DR
- **GNSS modules (u-blox)**: **MAX-M10S** (L1, 4 concurrent GNSS, −167 dBm tracking, 25 mW continuous tracking, up to 10–20 Hz depending on constellations; C4153167, ~US$9.07 at LCSC) [1]; **NEO-M9N** (L1, −167 dBm, 25 Hz, flash firmware; C5119087, ~US$15) [2]; **SAM-M10Q** (M10 with built-in patch; C5443880, ~US$35); **ZED-F9P** (L1/L2 multi-band RTK, cm-level with corrections, up to 25 Hz with GPS-only-class configs; C5120257, ~US$80) [3]; **NEO-F10N** (L1/L5 dual-band meter-level; GPS L5 used only after overriding its pre-operational health flag) [4]; **ZED-X20P** (all-band L1/L2/L5/L6 PPP-RTK) [5].
- **u-blox operational limits (datasheet, "assuming Airborne 4 g platform")**: **dynamics ≤ 4 g, altitude 80,000 m, velocity 500 m/s** — same on MAX-M10S, NEO-M9N, ZED-F9P, NEO-F10N, ZED-X20P [1–5]. **The altitude limit depends on firmware:** 50 km on ZED-F9P HPG 1.00–1.12 (-00B, -01B), 80 km on HPG 1.13 and later (-02B, -04B) and on M10 ([GNSS on rockets](../21-gnss/gnss-on-rockets-dynamics-and-limits.md)); check the firmware version on your module. u-blox community answers report that MAX-M10S output becomes invalid above 500 m/s; whether altitude and velocity limits combine with AND or OR is not stated in the datasheets (contradictory community statements) [6]. **Design for no position output above 500 m/s at any altitude** (speed-only cut-off; the AND/OR logic is undocumented), so rockets > 500 m/s lose GNSS during the fast phase; boost transients (jerk at ignition/burnout) may break lock — set the dynamic model to *Airborne 4 g* and treat GNSS as a coast/descent sensor.
- **Other GNSS**: Quectel **L76K** (GPS/BDS/GLONASS/QZSS L1, ≤ 5 Hz, −162 dBm tracking; C2916234, ~US$4.02), **LC76G** (5 constellations, 1 Hz, 1.5 m CEP; C7437114, ~US$6.40), **LC29H** (L1+L5 dual-band; EA variant outputs RTK/raw > 1 Hz, "dual-frequency RTK for < US$60"; C5116497 BA variant ~US$25.8), **LG290P** (quad-band L1/L2/L5/E6 RTK, 20 Hz) [7][8]; Unicore **UM980** (all-constellation multi-frequency RTK) [9]; ZHONGKEWEI **ATGM336H** (AT6558R, C90770, 5.8k stock, ~US$2.88) — cheapest; limited documentation [10].
- **Wi-Fi/BLE modules (certified; LCSC stock)**: ESP32-S3-WROOM-1 (PCB antenna, C2913202, 32.6k, ~US$4.90) / **-1U (U.FL, C3013946)**; ESP32-S3-MINI-1 (C2913206); ESP32-C3-MINI-1 (C2934569, ~US$2.78); ESP32-C6-MINI-1 (Wi-Fi 6 + 802.15.4, C5736265); ESP32-C5-WROOM-1U (dual-band 2.4/5 GHz, C51950748, ~US$5.46); ESP32-H2-MINI-1 (BLE + 802.15.4); nRF52840: EBYTE E73-2G4M08S1C (C356849, ~US$7.45), u-blox NINA-B302 (C6335962, ~US$18.6); RAK4630 (nRF52840 + SX1262, C33033533, ~US$17.6) [10].
- **LoRa modules in LCSC stock** (details in [LoRa modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md)): E22-900M30S (C411294, ~US$6.82), E22-400M22S (C411291, ~US$4.62), E220-900M30S (C2965511), E32-433T30D (C97351, ~US$11.5), Ai-Thinker Ra-02 (SX1278, C90039) and Ra-01SC (C2830750, ~US$3.07), RAK3172 (STM32WLE5, C19723904, ~US$7.21) [10]. SiK and RFD900x modems: [other ISM radios](../15-lora-ism-radios/other-ism-radios-fsk-2g4.md).
- **Certification & antennas** (from 19-domain): a module's grant covers *its* RF part only with the **same-type, equal-or-lower-gain antenna**; SMA-connector modules generally cannot hold a full FCC modular grant (unique-coupler rule); adding an external PA voids it; in Singapore, suppliers must register modules sold separately, and **certification never overrides power limits** (a certified 1 W 915 MHz module still breaks the 100 mW LPWAN limit) [11].

## Intuition (no math)
A module is a pre-designed, pre-tested RF subsystem — chip, reference oscillator, matching, filters, shield, often an antenna — sold with firmware and (usually) regulatory approvals. It trades a little cost and flexibility for removing the riskiest RF layout work. For a rocket flight computer the right default is **modules for GNSS and Wi-Fi/BLE, bare chips or SPI modules for LoRa** (so you control the waveform — see [rf-transceiver-ics](rf-transceiver-ics.md)).

GNSS modules carry two rocketry-specific traps: (1) **export-control-style limits** (velocity/altitude) built into the firmware and (2) **dynamics limits** of the tracking loops (the datasheet envelope is ≤ 4 g in the Airborne 4 g model; the physical cause of boost dropouts is jerk and oscillator g-sensitivity — [GNSS on rockets](../21-gnss/gnss-on-rockets-dynamics-and-limits.md)). Both come from the receiver design, not the antenna.

## The math — module specs vs mission
### Level 1 — GNSS velocity/altitude envelope
If the rocket's speed $v(t)$ exceeds 500 m/s at any point, expect invalid fixes for that interval (MAX-M10S community report [6]); the datasheet envelope is $|a| \le 4g$, $h \le 80$ km, $v \le 500$ m/s [1]. A rocket that reaches Mach 1.5 (≈ 500 m/s at altitude) is at the edge. Doppler at L1 for 500 m/s line-of-sight velocity: $f_d = v f/c$ = 2.6 kHz — tracking loops handle this; the *rate of change* during boost (≫ 4 g) is what breaks lock ([multipath/Doppler](../09-propagation-link-budget/multipath-fading-doppler.md)).

### Level 2 — link budget of a certified 2.4 GHz module
FSPL $=20\log_{10}d + 20\log_{10}f - 147.55$ dB. At 2.44 GHz: 1 km → 100.2 dB, 5 km → 114.2 dB, 10 km → 120.2 dB. With ESP32-S3 (+20 dBm BLE, −104.5 dBm BLE coded 125 kb/s [rf-transceiver-ics]) and 2 dBi antennas each end: margins 28.3 / 14.3 / 8.3 dB (Wi-Fi 11b 1 Mb/s, −98.4 dBm: 22.2 / 8.2 / 2.2 dB) — before fading, polarisation and legal EIRP limits ([link budget](../09-propagation-link-budget/link-budget-methodology.md)).

### Level 3 — power budget
GNSS tracking power: MAX-M10S 25 mW [1]; multi-band RTK modules draw several times more (ZED-F9P class; value not verified here) — size the battery for pad wait time, not flight time.

## Design equations & rules of thumb
| Rule | When valid | Typical values |
|---|---|---|
| u-blox envelope ≤ 4 g, ≤ 80 km (50 km on ZED-F9P HPG ≤ 1.12), ≤ 500 m/s at any altitude | Airborne 4 g model [1–5] | expect dropouts outside |
| Use *Airborne 4 g* dynamic model on rockets | u-blox M8/M9/M10/F9/X20 | configure via UBX-CFG |
| FSPL $=20\log d+20\log f-147.55$ | far field | 2.44 GHz, 5 km: 114.2 dB |
| Keep module antenna type and gain ≤ certified | modular approvals | [11] |
| Module PCB antenna needs ground-plane keep-out and board-edge placement | ESP32 -1/-MINI, nRF modules | see [PCB & chip antennas](../08-antennas/pcb-and-chip-antennas.md) |

## Comparison tables (LCSC data: 2026-04 snapshot [10]; US$ qty 1)
### A. GNSS modules
| Module | Bands / constellations | Sensitivity (tracking) | Nav rate | Limits | Notes | LCSC / stock / US$ |
|---|---|---|---|---|---|---|
| **u-blox MAX-M10S** | L1; GPS/GAL/BDS/GLO (4 concurrent) | −167 dBm | 10–20 Hz (config-dependent) | ≤ 4 g, 80 km, 500 m/s | 25 mW tracking; integrated LNA + SAW for passive antennas [1] | C4153167 / 1.2k / 9.07 |
| u-blox NEO-M9N | L1; 4 concurrent | −167 dBm | up to 25 Hz | same | flash, data logger [2] | C5119087 / 292 / 15.03 |
| u-blox SAM-M10Q | L1 with patch antenna | (see DS) | | same | antenna built in (placement matters) | C5443880 / 95 / 35.24 |
| u-blox MAX-M8Q / NEO-M8N | L1 (M8) | | | (M8 class) | older; NEO-M8N counterfeits common [sourcing] | C6898733 / 25 / 8.76; C6330769 / 11 / 48.71 |
| **u-blox ZED-F9P** | L1/L2 multi-band RTK | −167 dBm | up to 25 Hz (config-dependent) | same | RTK < 0.06 m H with SPARTN [3]; Space Bar's primary FC GNSS | C5120257 / 104 / 80.11 |
| u-blox NEO-F10N | L1/L5 | (see DS) | | same | GPS L5 flagged pre-operational — override health [4] | not in snapshot |
| u-blox ZED-X20P | L1/L2/L5/L6 all-band | −167 dBm | | same | PPP-RTK, 1.2 m CEP PVT [5] | not in snapshot |
| Quectel L76K | GPS/BDS/GLO/QZSS L1 | −162 dBm | ≤ 5 Hz | (not verified) | 10.1 × 9.7 mm [7] | C2916234 / 1.3k / 4.02 |
| Quectel LC76G | GPS/GLO/BDS/GAL/QZSS L1 | | 1 Hz | (not verified) | 1.5 m CEP [7] | C7437114 / 297 / 6.40 |
| Quectel LC86G | L1 (unverified) | | | | | C5943068 / 221 / 7.12 |
| Quectel LC29H (BA/DA/EA) | L1 + L5 | | EA > 1 Hz RTK/raw | (not verified) | cheap dual-band RTK (EA) [8] | C5116497 (BA) / 286 / 25.77 |
| Quectel LG290P | L1/L2/L5/E6 | | 20 Hz (RTK) | (not verified) | quad-band RTK [7] | not in snapshot |
| Unicore UM980 | all-constellation multi-frequency | | | (not verified) | RTK [9] | not in snapshot |
| ZHONGKEWEI ATGM336H / ATGM332D | BDS/GPS/GLO L1 (AT6558R) | | | (not verified) | cheapest; sparse English docs | C90770 / 5.8k / 2.88; C128659 / 4.7k / 2.69 |
Boards: SparkFun (MAX-M10S, NEO-F10N, ZED-F9P), ArduSimple simpleRTK2B (ZED-F9P; ≈ US$197 at one distributor [9]) — good for bench evaluation and RTK base stations.

### B. Wi-Fi / BLE / 802.15.4 modules
| Module | Radio | Antenna | LCSC / stock / US$ | Notes |
|---|---|---|---|---|
| **Espressif ESP32-S3-WROOM-1 / -1U** | Wi-Fi 4 + BLE 5 | PCB / U.FL | C2913202 / 32.6k / 4.90; C3013946 / 18k / 5.04 | N16R8 variants listed; PSRAM options |
| Espressif ESP32-S3-MINI-1 | Wi-Fi 4 + BLE 5 | PCB | C2913206 / 12.4k / 4.31 | smaller |
| Espressif ESP32-C3-MINI-1 | Wi-Fi 4 + BLE 5 (RISC-V) | PCB | C2934569 / 7.3k / 2.78 | cheapest ESP32 module |
| Espressif ESP32-C6-MINI-1 / -WROOM-1 | Wi-Fi 6 + BLE + 802.15.4 | PCB (MINI-1U: U.FL) | C5736265 / 6.1k / 3.71; C6034714 / 1.1k / 4.00 | Thread/Zigbee capable |
| Espressif ESP32-C5-WROOM-1U | dual-band 2.4/5 GHz Wi-Fi 6 | U.FL | C51950748 / 513 / 5.46 | 5 GHz links |
| Espressif ESP32-H2-MINI-1 | BLE + 802.15.4 | PCB | C18203134 / 308 / 3.18 | no Wi-Fi |
| Espressif ESP32-WROOM-32E | classic ESP32 | PCB | C701342 / 20.5k / 4.06 | legacy |
| EBYTE E73-2G4M08S1C | nRF52840 | PCB | C356849 / 2.1k / 7.45 | cheap nRF52840 module |
| u-blox NINA-B302 | nRF52840 | external antenna pin | C6335962 / 32 / 18.58 | |
| RAKwireless RAK4630 | nRF52840 + SX1262 | pads | C33033533 / 308 / 17.61 | Meshtastic/RAK4631 core |

### C. LoRa and telemetry modules (see the 15-domain pages for behaviour)
| Module | Chip | Interface / power | LCSC / stock / US$ |
|---|---|---|---|
| EBYTE E22-900M30S / E22-400M22S | SX1262 / SX1268 | SPI, 30 / 22 dBm | C411294 / 929 / 6.82; C411291 / 705 / 4.62 |
| EBYTE E220-900M30S | LLCC68 | SPI, 30 dBm | C2965511 / 21 / 5.88 |
| EBYTE E32-433T30D | SX1278 | UART, 30 dBm | C97351 / 273 / 11.48 |
| Ai-Thinker Ra-02 / Ra-01SC | SX1278 / (LLCC68, unverified) | SPI | C90039 / 1.8k / 6.48; C2830750 / 4.3k / 3.07 |
| RAKwireless RAK3172 | STM32WLE5 | UART AT / custom FW | C19723904 / 958 / 7.21 |
| RFD900x / SiK modems | Si1000/Si4432 (SiK), RFD custom | UART, FHSS | distributors — [other ISM radios](../15-lora-ism-radios/other-ism-radios-fsk-2g4.md) |

### D. Video transmitters and SDR modules (pointers)
| Class | Examples | Notes |
|---|---|---|
| Analog 5.8 GHz VTX | TBS Unify-class, generic 25–1000 mW VTX | power far above SG SRD limits at high settings — check [Singapore IMDA rules](../19-regulations-safety/singapore-imda-rules.md); rockets usually record video onboard instead |
| Digital FPV | DJI O3/O4, Walksnail Avatar, HDZero, OpenIPC (Wi-Fi-based) | closed systems (except OpenIPC); range and legality per band/power |
| SDR modules | PlutoSDR, LibreSDR/AntSDR, bladeRF, USRP B2xx, CaribouLite, RTL-SDR | [SDR hardware survey](../14-sdr-dsp/sdr-hardware-survey.md) |

## Worked examples
### 1. GNSS for a 6 km apogee rocket with ~450 m/s peak speed
Peak speed below 500 m/s → within the u-blox envelope, but boost acceleration of 10–15 g exceeds the 4 g dynamics spec. That 4 g is the datasheet envelope for the Airborne 4 g model, not a hard tracking threshold: constant acceleration costs a 3rd-order loop nothing in steady state, and loss of lock is actually driven by jerk at ignition/burnout and by oscillator g-sensitivity ([GNSS on rockets](../21-gnss/gnss-on-rockets-dynamics-and-limits.md)). Expect degraded/lost tracking around those transients and re-acquisition during coast (a few seconds with hot start ≈ 1 s TTFF [1]). Design: MAX-M10S (secondary FC) or ZED-F9P (primary) with *Airborne 4 g*, 10 Hz, an active or well-grounded antenna ([GNSS antennas](../08-antennas/gnss-antennas.md)), and state estimation that fuses IMU/baro through boost. Keep a SAW before any LNA because of the on-board telemetry transmitter ([filter parts](filter-parts-saw-ceramic-ltcc.md)).

### 2. A supersonic rocket reaching 650 m/s
Above 500 m/s the fix is invalid for the whole high-speed interval (MAX-M10S behaviour [6]); if the *altitude* criterion is also involved, behaviour depends on firmware logic not documented in the datasheet. Options: accept the gap (GNSS resumes on descent), use a receiver sold without the limit for licensed high-altitude/space work (outside the scope of this KB; export-controlled), or rely on IMU/baro for the fast phase. Record raw measurement flags to learn what your firmware actually does (and report it — faithful-reporting tenet).

### 3. Pad-to-ground-station BLE/Wi-Fi status link at 1–5 km
From Level 2: BLE coded PHY with ESP32-S3 at +20 dBm and 2 dBi antennas has 28 dB margin at 1 km and 14 dB at 5 km in free space; Wi-Fi 11b 1 Mb/s has 22 / 8 dB. Use the **-1U** (U.FL) module with an external antenna of the certified type/gain, mount it at the board edge away from metal, and confirm the 2.4 GHz EIRP limit for Singapore (19-domain).

## Practical notes
- **GNSS configuration**: dynamic model Airborne 4 g, disable unused constellations to raise the nav rate (u-blox rates depend on the constellation set [1]), enable UBX-NAV-PVT at the flight rate, log raw flags; check "fix OK" and the carrier-solution flags, not just lat/lon.
- **GNSS antenna/LNA**: MAX-M10S integrates LNA + SAW for passive antennas [1]; ZED-F9P needs an active multi-band antenna for full performance (the Avionics-B-V3 flew an L1-only antenna — an L1/L2 antenna is needed to use F9P's multi-band capability).
- **Firmware authenticity**: on first power-up read the firmware/ROM version string; counterfeit M8N modules are locked to ROM 2.01 ([sourcing](sourcing-and-eval-boards.md)).
- **Module antenna keep-out**: follow the module datasheet keep-out (no copper under/near the PCB antenna, antenna at the board edge); an enclosure or carbon-fibre airframe detunes it — use -1U/U.FL variants with an external antenna on rockets ([antennas on rockets](../08-antennas/antennas-on-rockets.md)).
- **Power**: ESP32 Wi-Fi TX bursts draw several hundred mA; give the module ≥ 500 mA headroom and bulk capacitance ([power supplies for RF](../05-analog-electronics/power-supplies-for-rf-and-analog.md)).
- **Certification**: keep the module's antenna type and gain; don't add PAs; for sale in Singapore the supplier registers the equipment; for your own experimental use the operating rules (power, band) still apply ([certification](../19-regulations-safety/certification-fcc-ce-imda.md)).

## GNSS module integration checklist (flight computer)
1. **Antenna path**: passive patch → short 50 Ω CPWG → module RF_IN (MAX-M10S has LNA + SAW inside [1]); active antenna → bias via the module's antenna supply pin with current limiting/short protection.
2. **Ground plane**: patch antennas need the specified ground-plane size; module RF pin needs a solid reference plane and stitching ([GNSS antennas](../08-antennas/gnss-antennas.md)).
3. **Blocker protection**: on-board 433/915 MHz transmitters couple into the GNSS antenna — keep SAW-first filtering and physical separation ([filter parts](filter-parts-saw-ceramic-ltcc.md)).
4. **Supply**: low-noise LDO; decouple per the integration manual; keep switchers' harmonics away from 1.57 GHz (check harmonic landing).
5. **Backup power (V_BCKP)**: supercap or cell for hot start (≈ 1 s TTFF [1]) after power glitches during flight.
6. **Timepulse**: route PPS to the MCU for time-stamping telemetry and sensor fusion.
7. **Configuration at boot**: dynamic model Airborne 4 g, nav rate, constellations, message set; save to BBR/flash; verify with UBX-CFG polls at each power-up (don't assume saved config survived).
8. **Logging**: log fix type, numSV, pDOP, flags and velocity accuracy, not just position — needed to interpret dropouts near the 500 m/s / 4 g limits.
9. **ESD/back-powering**: buffer the UART so the module is not back-powered from MCU I/O when switched off (lesson from Avionics-C: buffered UART).
10. **Pre-flight**: outdoor cold-start test with the airframe/nose cone in place; record C/N₀ per satellite.

## Recommended picks for Marcus's use cases
| Use case | Pick | Why |
|---|---|---|
| Secondary FC GNSS | u-blox MAX-M10S (LCSC) | 25 mW, integrated LNA + SAW, deep LCSC stock; read the firmware version on arrival |
| Primary FC GNSS / RTK | ZED-F9P (with L1/L2 antenna) or LG290P/UM980 as newer multi-band options | cm-level with corrections |
| Cheap dual-band experiments | Quectel LC29HEA | dual-band RTK for < US$60 (rtklibexplorer) [8] |
| Pad Wi-Fi/BLE status link | ESP32-S3-WROOM-1U + external antenna | certified, U.FL, deep stock |
| BLE sensor node | ESP32-C3-MINI-1 or E73 (nRF52840) | cheap |
| LoRa downlink | SX1268/SX1262 bare or E22-xxxM SPI module | control of waveform ([15-domain](../15-lora-ism-radios/rocket-telemetry-radio-design.md)) |

## Parts to avoid (or use knowingly)
- **Marketplace NEO-M8N and other GNSS modules without firmware check** ([sourcing](sourcing-and-eval-boards.md)).
- **SAM-M10Q (built-in patch) inside a metal/carbon airframe** — antenna cannot see the sky.
- **PCB-antenna Wi-Fi modules inside enclosures** — use U.FL variants.
- **High-power VTX / 1–2 W telemetry modules at full power in Singapore** without a licence ([Singapore IMDA rules](../19-regulations-safety/singapore-imda-rules.md)).

## Common mistakes & misconceptions
- *"COCOM is 18 km and 515 m/s and all receivers use OR."* u-blox datasheets state 80 km (50 km on ZED-F9P HPG 1.00–1.12) / 500 m/s / 4 g operational limits; the exact enforcement logic is undocumented and community reports disagree — test or log it [1][6].
- *"Dual-band = better on a rocket."* Dual-band improves multipath/ionospheric errors and RTK; it does not fix boost dynamics or the velocity limit.
- *"A certified module makes my board certified."* Only the module's intentional radiator, with its certified antenna; the host still needs EMC compliance ([certification](../19-regulations-safety/certification-fcc-ce-imda.md)).

## How to simulate / verify
```python
import math
fspl = lambda d, f: 20*math.log10(d) + 20*math.log10(f) - 147.55
for d in (1e3, 5e3, 10e3):
    L = fspl(d, 2.44e9); print(d, round(L, 1), round(20 + 2 + 2 - L + 104.5, 1))   # BLE coded margin
```
- GNSS: record UBX-NAV-PVT and UBX-NAV-STATUS during a HIL replay or a vehicle/drone test; a GNSS simulator (or an SDR GPS signal generator used legally in a shielded box) can probe the velocity limit behaviour.
- Module RF: conducted TX power/spectrum via a U.FL-to-SMA pigtail into an attenuator and spectrum analyser ([17-test-measurement](../17-test-measurement/spectrum-analyzers.md)).

## Open questions / gaps
- u-blox limit-enforcement logic (AND vs OR, hysteresis) — undocumented; bench/flight evidence needed.
- Quectel/Unicore/ZHONGKEWEI operational limits not verified.
- ZED-F9P and multi-band module power consumption not verified here.
- Ra-01SC chip identity (LLCC68) unverified; ESP32 module certification lists per country not verified.

## Sources
1. u-blox, *MAX-M10S Standard precision GNSS module data sheet* UBX-20035208, https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf — 25 mW tracking, −167 dBm, rates, operational limits (≤ 4 g, 80,000 m, 500 m/s, assuming Airborne 4 g), integrated LNA/SAW. (datasheet)
2. u-blox, *NEO-M9N-00B data sheet* UBX-19014285, https://content.u-blox.com/sites/default/files/NEO-M9N-00B_DataSheet_UBX-19014285.pdf. (datasheet)
3. u-blox, *ZED-F9P-04B data sheet* UBX-21044850, https://content.u-blox.com/sites/default/files/ZED-F9P-04B_DataSheet_UBX-21044850.pdf. (datasheet)
4. u-blox, *NEO-F10N data sheet* UBX-23002117 (SparkFun mirror), https://docs.sparkfun.com/SparkFun_u-blox_NEO-F10N/assets/component_documentation/NEO-F10N_DataSheet_UBX-23002117.pdf. (datasheet)
5. u-blox, *ZED-X20P-00B data sheet* UBXDOC-963802114-12690, https://content.u-blox.com/sites/default/files/documents/ZED-X20P-00B_DataSheet_UBXDOC-963802114-12690.pdf. (datasheet)
6. u-blox support community, *u-blox M10S velocity and altitude operational limits* and *cocom* topic; BigRedBee, *High altitude GPS operation*; Rocketry Forum threads (via search extract). (manufacturer forum / blog — anecdotal)
7. Quectel, *L76K hardware design* V1.0 (2021), *LC76G series GNSS specification*, *LG290P GNSS module specification* V1.3 (via search extracts). (datasheet, secondary extract)
8. rtklibexplorer, *Dual frequency RTK for less than $60 with the Quectel LC29HEA* (2024-04-28), https://rtklibexplorer.wordpress.com/2024/04/28/dual-frequency-rtk-for-less-than-60-with-the-quectel-lc29hea/; Quectel LC29H series specification. (blog — quantitative; datasheet)
9. Unicore, *UM980* product page, https://en.unicore.com/products/um980/; ArduSimple simpleRTK2B listing (distributor price). (manufacturer / distributor)
10. Local JLCPCB/LCSC parts database (jlcparts in-stock snapshot, newest record 2026-04-01) via `jlc-trawler`. (distributor data)
11. This KB: [Certification — FCC, CE, IMDA](../19-regulations-safety/certification-fcc-ce-imda.md) and [Singapore IMDA rules](../19-regulations-safety/singapore-imda-rules.md) (W3-C5). (internal)
