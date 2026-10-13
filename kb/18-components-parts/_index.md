# 18-components-parts — Components and parts (what to buy, where, and why)

Selection guides with real part numbers for custom radios, LoRa front ends, GNSS, radars, phased arrays and analog/RF
circuits: which specifications matter (linked to the theory domains), comparison tables, LCSC/JLCPCB stock and price
(2026-04 snapshot of the jlcparts database, US$ at qty 1), Mouser/DigiKey/element14 availability, assembly gotchas,
recommended picks for Space Bar use cases, and parts to avoid. Physics lives in 03/04/06/07/08/11/12/13/14; this domain
is the procurement layer. All prices and stock are "as of" the snapshot — refresh before ordering.

## Reading order (beginner → advanced)
1. [sourcing-and-eval-boards](sourcing-and-eval-boards.md) — where to buy in Singapore, JLC basic/extended/global-sourcing, samples, fakes.
2. [rf-modules](rf-modules.md) — GNSS, Wi-Fi/BLE, LoRa modules; certification and antenna rules; u-blox 4 g / 500 m/s limits.
3. [connectors-and-cables-parts](connectors-and-cables-parts.md) — SMA/U.FL/MMCX/N; torque; pigtails.
4. [rf-transceiver-ics](rf-transceiver-ics.md) — packet radios, SoCs, IQ transceivers, GNSS front ends.
5. [lna-pa-gain-block-mmics](lna-pa-gain-block-mmics.md) — LNAs, gain blocks, FEMs, LDMOS/GaN.
6. [filter-parts-saw-ceramic-ltcc](filter-parts-saw-ceramic-ltcc.md) — SAW/LTCC/chip filters, harmonic filtering.
7. [rf-switches-attenuator-parts](rf-switches-attenuator-parts.md) — switches, DSAs, pads, limiters.
8. [mixers-plls-vcos-parts](mixers-plls-vcos-parts.md) — mixers, IQ mod/demod, PLLs (incl. FMCW ramps), clocks, TCXOs, DDS.
9. [pcb-substrates-parts](pcb-substrates-parts.md) — which laminates the fabs sell; when Rogers is worth it.
10. [adcs-dacs-for-sdr](adcs-dacs-for-sdr.md) — converters for SDRs and radar beat signals.
11. [phased-array-and-radar-parts](phased-array-and-radar-parts.md) — mmWave radar SoCs, 24 GHz chipset, beamformers, phase shifters.

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [rf-transceiver-ics](rf-transceiver-ics.md) | FOM-normalised comparison of CC1101/CC1200/CC1125/CC13xx, Si4463, EFR32FG23, S2-LP, SX12xx, nRF52/53/54, ESP32, AT86RF215, SX1255/57, AD936x, ADRV9002, LMS7002M, MAX2769B; range extenders | intermediate | medium |
| [lna-pa-gain-block-mmics](lna-pa-gain-block-mmics.md) | QPL9547, TQP3M9036/9037, TQL9092, PSA4-5043+, PMA/PGA series, GNSS LNAs (BGA524, MAX2659, AT2659), handset LNAs, GALI/ERA/MAR/GVA/ADL56xx gain blocks, SE2435L/SKY66423/CC1190 FEMs, RD01MUS2/AFT05MS004N/CGH40010F | intermediate | medium |
| [mixers-plls-vcos-parts](mixers-plls-vcos-parts.md) | ADE/ADEX/SYM mixers, ADL5801/LTC5562, TRF3705/ADL5375/ADL5380, ADF4351/MAX2871/LMX2572/LMX2594/LMX2820, ADF4159/LMX2491 ramps, LMX2571, Si5351/MS5351M/Si5341/LMK, TCXOs, AD9850/AD9910 | intermediate | medium |
| [rf-switches-attenuator-parts](rf-switches-attenuator-parts.md) | SKY13453/13351/13330, PE4259/PE42420/PE42442, HMC544A/849A, ADRF5019; PE43711/PE4312 (PE4314 is 75 Ω), HMC624A, DAT-31R5A; JLC-basic π-pads; limiters/PIN diodes | intermediate | medium |
| [filter-parts-saw-ceramic-ltcc](filter-parts-saw-ceramic-ltcc.md) | 433/868/915 MHz and GNSS SAWs in LCSC stock, LFCN/LFCG/HFCN/BFCN LTCC, TDK/Johanson/Murata chip LPFs, ST BALF, cavity preselectors; harmonic-filter sizing | intermediate | medium |
| [connectors-and-cables-parts](connectors-and-cables-parts.md) | connector families, frequency limits, cycles, torque, MHF I LK for vibration, LCSC genuine vs clone connectors, cable assemblies | intro | medium |
| [pcb-substrates-parts](pcb-substrates-parts.md) | JLC FR-4 prepregs, JLC RO4350B/ZYF PTFE (2-layer), PCBWay hybrids, OSH Park FR408HR, Aisler; design vs process Dk; ordering checklist | intro | medium |
| [adcs-dacs-for-sdr](adcs-dacs-for-sdr.md) | LTC2208, ADC3664, ADS4249, ADS42LB69, AD9226/AD9280, MAX19506, AD9680/AD9208/ADC12DJ3200/AFE7950/RFSoC, DACs, ADAR7251 and audio codecs for FMCW | intermediate | medium |
| [phased-array-and-radar-parts](phased-array-and-radar-parts.md) | IWR6843/AOP, AWR1843, IWRL6432, BGT60TR13C/LTR11AIP, A121/XM125, ADF4159+ADF5901+ADF5904+ADAR7251, ADAR1000/ADTR1107, AWMF-0108 (Qorvo), phase shifters, radar modules; SG band legality | intermediate | medium |
| [sourcing-and-eval-boards](sourcing-and-eval-boards.md) | SG distributors and thresholds, JLC PCBA fee model, LCSC RF depth, global-sourcing parts, EVBs, samples, documented counterfeits, inspection checklist, starter kit | intro | medium |
| [rf-modules](rf-modules.md) | u-blox M10/M9/F9P/F10N/X20P, Quectel L76K/LC76G/LC29H/LG290P, UM980, ATGM336H; ESP32/nRF modules; LoRa/telemetry modules; VTX/SDR pointers; certification rules; GNSS integration checklist | intermediate | medium |
| [coax-and-connector-practicalities](coax-and-connector-practicalities.md) | torque/cycles/cleaning, adapter budgets, SMA vs RP-SMA ID table, U.FL limits (2–4 N pull, 75 g shock, extraction tool), weatherproofing, crimp vs solder, semi-rigid SMA, bend radius, phase matching, NanoVNA VF/loss/TDR, 75 Ω on 50 Ω (0–0.69 dB), fake cable checks, launch-day checklist | intro | medium |
| [rf-passives-and-support-parts](rf-passives-and-support-parts.md) | JLC basic/preferred C0G and RF-inductor sets (no basic RF inductors), wire-wound vs multilayer vs air-core, harmonic-filter example, DC blocks, terminations, bias tees, low-C ESD, low-noise LDOs, zero-drift op-amps, ferrites/shield clips, couplers/splitters, UHF circulators (web data), ADE-1 spur tables | intermediate | medium |
| [_sources](_sources.md) | consolidated bibliography and data-gathering method | — | — |

## Top picks at a glance (details and caveats on each page)
| Need | Pick | Page |
|---|---|---|
| LoRa downlink chip | SX1268 (433) / SX1262 (915/923), bare or E22-xxxM SPI module | [rf-transceiver-ics](rf-transceiver-ics.md), [15-domain](../15-lora-ism-radios/semtech-chip-family.md) |
| High-rate FSK downlink | CC1200 (+CC1190 at 915 MHz), Si4463-C2A | [rf-transceiver-ics](rf-transceiver-ics.md) |
| SDR-like custom radio at 433/915/2.4 GHz | AT86RF215 + small FPGA | [rf-transceiver-ics](rf-transceiver-ics.md) |
| 433/915 MHz mast-head LNA | TQP3M9036 (or PSA4-5043+) + SAW/cavity preselector | [lna-pa-gain-block-mmics](lna-pa-gain-block-mmics.md) |
| GNSS LNA / SAW | BGA524N6 / Murata SAFFB1G56KB0F0AR1X | [lna…](lna-pa-gain-block-mmics.md), [filters](filter-parts-saw-ceramic-ltcc.md) |
| +27…+30 dBm at 868/915 MHz | SKY66423-11 / SE2435L + LC harmonic LPF | [lna…](lna-pa-gain-block-mmics.md), [filters](filter-parts-saw-ceramic-ltcc.md) |
| 433 MHz SAW / 915 MHz SAW | B39431B3710U410 / B39921B3728U410 | [filters](filter-parts-saw-ceramic-ltcc.md) |
| T/R switch ~1 W | SKY13330-397LF | [switches](rf-switches-attenuator-parts.md) |
| Digital step attenuator | PE43711 (fine), PE4312 (cheap) | [switches](rf-switches-attenuator-parts.md) |
| Wideband LO / chirp PLL | LMX2572 (≤ 6.4 GHz), LMX2594 (≤ 15 GHz), ADF4159 (24 GHz chain) | [mixers/PLLs](mixers-plls-vcos-parts.md) |
| Radio TCXO | KDS 1XXD32000MBA (32 MHz), Huaxin 2T026000VY (26 MHz) | [mixers/PLLs](mixers-plls-vcos-parts.md) |
| Flight antenna connector | I-PEX MHF I LK or U.FL + adhesive; SMA bulkhead | [connectors](connectors-and-cables-parts.md) |
| Antenna/array substrate | JLC 2-layer RO4350B (Dk 3.66 design) | [substrates](pcb-substrates-parts.md) |
| Radar for pad tests | TI IWR6843 (60 GHz) EVM; CDM324/HB100 + PCM1808 for Doppler | [radar parts](phased-array-and-radar-parts.md) |
| Flight GNSS | MAX-M10S (secondary), ZED-F9P (primary, L1/L2 antenna) | [rf-modules](rf-modules.md) |
| Wi-Fi/BLE | ESP32-S3-WROOM-1U | [rf-modules](rf-modules.md) |

## Domain FAQ (top questions → page#section)
- How do I compare radio chips quoted at different data rates? → [rf-transceiver-ics](rf-transceiver-ics.md#the-math) (FOM)
- Does an external LNA really add 6 dB? → [rf-transceiver-ics](rf-transceiver-ics.md#worked-examples) (CC1190 example), [lna-pa-gain-block-mmics](lna-pa-gain-block-mmics.md#worked-examples)
- Which LNA for my 433 MHz ground station, and where does it go? → [lna-pa-gain-block-mmics](lna-pa-gain-block-mmics.md#worked-examples)
- How much harmonic filtering does a 1 W PA need? → [filter-parts-saw-ceramic-ltcc](filter-parts-saw-ceramic-ltcc.md#worked-examples)
- Can my RF switch survive +30 dBm into a broken antenna? → [rf-switches-attenuator-parts](rf-switches-attenuator-parts.md#the-math)
- How do I make an attenuator pad from JLC basic resistors? → [rf-switches-attenuator-parts](rf-switches-attenuator-parts.md#worked-examples)
- Which PLL can make FMCW chirps? → [mixers-plls-vcos-parts](mixers-plls-vcos-parts.md#comparison-tables-lcsc-data-2026-04-snapshot-1-us-qty-1)
- Can the Si5351 clock my ADC? → [mixers-plls-vcos-parts](mixers-plls-vcos-parts.md#worked-examples)
- Why did my U.FL fall off, and how tight should an SMA be? → [connectors-and-cables-parts](connectors-and-cables-parts.md#tldr)
- Is FR-4 OK or do I need Rogers? What Dk do I use? → [pcb-substrates-parts](pcb-substrates-parts.md#tldr)
- Can an audio codec digitise my radar? → [adcs-dacs-for-sdr](adcs-dacs-for-sdr.md#worked-examples)
- Which radar chip is legal and good for pad tests in Singapore? → [phased-array-and-radar-parts](phased-array-and-radar-parts.md#tldr)
- What do JLC "extended" and "global sourcing" parts cost me? → [sourcing-and-eval-boards](sourcing-and-eval-boards.md#the-math--cost-and-risk-rules)
- Is my GNSS module fake? Will it stop above 500 m/s? → [sourcing-and-eval-boards](sourcing-and-eval-boards.md#comparison-tables), [rf-modules](rf-modules.md#tldr)
- Which JLC-stocked C0G caps, RF inductors, pads, bias tees and low-capacitance ESD parts should I use? → [rf-passives-and-support-parts](rf-passives-and-support-parts.md#practical-notes) (harmonic filter, bias tee and ESD examples: [worked examples](rf-passives-and-support-parts.md#worked-examples))

## Key references for this domain (→ [_sources](_sources.md))
Vendor datasheets read as raw text (TI, Mini-Circuits, pSemi, Skyworks, u-blox, Microchip, Silicon Labs, Espressif);
the jlcparts/LCSC snapshot (2026-04) for stock and prices; JLCPCB/PCBWay/OSH Park capability pages; KB theory pages
in 03, 04, 06, 07, 08, 11, 12, 13, 14, 15, 19.

## Known gaps
- Analog Devices / ST / Qorvo documents could not be fetched by script: their numbers are LCSC parametrics or search
  extracts (medium confidence) — re-verify ADF4351/MAX2871 phase noise, HMC472A bit count, LTC2208/AD9226 performance.
- LCSC stock/prices are a 2026-04 snapshot; Mouser/DigiKey prices not captured systematically.
- No bench measurements yet of the cheap Chinese handset LNAs, marketplace LNA/SDR modules or U.FL vs MHF-LK under vibration.
- u-blox GNSS limit enforcement (AND/OR) is undocumented — needs a HIL/simulator test.
- 433 MHz watt-level FEM options are thin (RFFM6406 lifecycle unverified).
