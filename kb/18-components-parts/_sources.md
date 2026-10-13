# 18-components-parts — sources

Bibliography for the domain, collected from each page's *Sources* section (numbering is per page).
Reliability tags: (datasheet), (manufacturer), (distributor data), (application note), (blog), (forum — anecdotal),
"secondary extract" = the number came from a search-engine or WebFetch summary of the primary document, not from
reading the document text itself (see CONVENTIONS rule 8) — treat those as medium confidence.

## How the data were gathered (2026-09-27/29)
- **LCSC/JLCPCB stock, prices, basic/extended status**: local jlcparts "in-stock" snapshot
  (`~/jlc-trawler-data/jlcpcb-components.sqlite3`, newest record 2026-04-01) queried with the `jlc-trawler` skill
  and small scripts; LCSC product pages (JSON-LD parametrics) fetched 2026-09-29. Prices are US$ at qty 1 (JLC price
  table); stock numbers are a snapshot — refresh before ordering (`trawl.py refresh <C-numbers>`).
- **Datasheets read as raw text** (curl + pdftotext, avoiding WebFetch summarisation errors): TI (≈ 30 parts),
  Mini-Circuits (≈ 35 parts), pSemi (6), Skyworks product pages (8), Microchip AT86RF215, Silicon Labs Si4463-C and
  EFR32FG23, Espressif ESP32-S3/C6, u-blox MAX-M10S/NEO-M9N/ZED-F9P/NEO-F10N/ZED-X20P, Mitsubishi RD01MUS2,
  Skyworks SE2435L, JLCPCB/PCBWay/OSH Park/Aisler web pages.
- **Blocked to scripts** (analog.com, st.com, qorvo.com, digikey.com, alldatasheet): numbers for ADI/Maxim/LTC, ST,
  Qorvo parts come from LCSC parametrics or search extracts and are marked as such.

## Most-used references
| Domain / source | Used by pages |
|---|---|
| ti.com | adcs-dacs-for-sdr, lna-pa-gain-block-mmics, mixers-plls-vcos-parts, phased-array-and-radar-parts, rf-transceiver-ics |
| analog.com | adcs-dacs-for-sdr, mixers-plls-vcos-parts, phased-array-and-radar-parts, rf-transceiver-ics, sourcing-and-eval-boards |
| minicircuits.com | filter-parts-saw-ceramic-ltcc, lna-pa-gain-block-mmics, mixers-plls-vcos-parts, rf-switches-attenuator-parts |
| github.com | mixers-plls-vcos-parts, rf-transceiver-ics, sourcing-and-eval-boards |
| skyworksinc.com | lna-pa-gain-block-mmics, rf-switches-attenuator-parts, sourcing-and-eval-boards |
| mouser.com | phased-array-and-radar-parts, rf-transceiver-ics |
| lcsc.com | lna-pa-gain-block-mmics, phased-array-and-radar-parts |
| jlcpcb.com | pcb-substrates-parts, sourcing-and-eval-boards |
| realdigital.org | adcs-dacs-for-sdr, sourcing-and-eval-boards |
| rtklibexplorer.wordpress.com | rf-modules, sourcing-and-eval-boards |

## [rf-transceiver-ics](rf-transceiver-ics.md)
*RF transceiver ICs — sub-GHz packet radios, radio SoCs, IQ/SDR transceivers and GNSS front-ends (selection guide)*

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

## [lna-pa-gain-block-mmics](lna-pa-gain-block-mmics.md)
*LNAs, PAs, gain blocks and front-end modules — part selection guide (sub-GHz, GNSS, 2.4 GHz, microwave)*

1. Local JLCPCB/LCSC parts database (jlcparts in-stock snapshot, newest record 2026-04-01) via `jlc-trawler`, plus LCSC product-page parametrics (https://www.lcsc.com/product-detail/<C-number>.html, fetched 2026-09-29) — stock, prices, NF/gain/IP3/P1dB listings. (distributor data)
2. This KB: [Receiver cascade analysis](../07-noise-linearity/receiver-cascade-analysis.md), [Noise figure & Friis](../07-noise-linearity/noise-figure-and-friis.md). (internal)
3. Skyworks, *SE2435L: 860 to 930 MHz High-Power RF Front-End Module* datasheet, https://www.skyworksinc.com/-/media/D3C064001C9E45EDB6C26EDBFB0FD0F5.pdf, pp. 1–6 — +30 dBm, NF 2 dB, RX gain 16 dB, currents 550/380/275 mA, PAE 64 %, harmonics. (datasheet)
4. Skyworks, *SKY66423-11 860–930 MHz RF Front-End Module* product page, https://www.skyworksinc.com/en/Products/Front-end-Modules/SKY66423-11 (fetched 2026-09-29) — +27 dBm, NF 1.5 dB, 2.0–4.8 V, MCM-16, layout warning; SKY65364-21 page (LTB). (manufacturer)
5. Mini-Circuits datasheets, https://www.minicircuits.com/pdfs/<model>.pdf (fetched 2026-09-27): PSA4-5043+, PMA2-43LN+, PMA3-83LN+, PMA-5451+, PSA-5451+, PMA-545G1+, PMA3-14LN+, PGA-103+, SAV-541+, TAMP-72LN+, GALI-84+, GALI-74+, GALI-S66+, ERA-5SM+, MAR-6SM+, PSA-39+, PHA-13HLN+, ZX60-P103LN+, ZX60-33LN+, ZFL-500LN+, ZHL-4240. (datasheets)
6. Texas Instruments, *CC1190 850–950 MHz RF Front End* datasheet, https://www.ti.com/lit/ds/symlink/cc1190.pdf. (datasheet)
7. Texas Instruments, *CC2592 2.4 GHz range extender* datasheet, https://www.ti.com/lit/ds/symlink/cc2592.pdf. (datasheet)
8. Mitsubishi Electric, *RD01MUS2 Silicon RF Power MOS FET* datasheet (Feb 2017), https://www.mitsubishielectric.com/semiconductors/hf/products/datasheet/rd01mus2.pdf — P_out > 0.8 W, power gain G_power > 14 dB, 65 % @ 520 MHz, 7.2 V. (datasheet)
9. Mitsubishi Electric RD06HHF1 / RD15HVF1 datasheets (via search summary: 6 W @ 30 MHz; 15 W 175–520 MHz). (datasheet, secondary extract)
10. NXP, *AFT05MS003N 3 W CW 1.8–941 MHz 7.5 V LDMOS* and *AFT05MS004N 136–941 MHz 4 W* datasheets, https://www.nxp.com/docs/en/data-sheet/AFT05MS003N.pdf, https://www.nxp.com/docs/en/data-sheet/AFT05MS004N.pdf (titles via search; not re-read). (datasheet, secondary extract)
11. This KB: [Coaxial lines and RF cables](../03-transmission-lines-matching/coax-and-cables.md) — RG-58 2.9 dB/10 m at 433 MHz. (internal)
12. Qorvo RFFM6406 / RFFM6906 product summaries (via search results, qorvo.com blocked to direct fetch). (manufacturer, secondary extract)
13. Forum/marketplace reports on SPF5189Z LNA boards (rtl-sdr.com tag pages, AliExpress listings) — variability and oscillation anecdotes. (forum — anecdotal)

## [mixers-plls-vcos-parts](mixers-plls-vcos-parts.md)
*Mixers, IQ modulators/demodulators, PLL synthesizers, VCOs, clock generators, TCXOs and DDS — part selection guide*

1. Local JLCPCB/LCSC parts database (jlcparts in-stock snapshot, newest record 2026-04-01) via `jlc-trawler`, and LCSC product-page parametrics (fetched 2026-09-29). (distributor data)
2. Analog Devices product pages/datasheets — ADF4351 (Rev A), ADF4371, MAX2870 — via search extracts: https://www.analog.com/en/products/adf4351.html, https://www.analog.com/en/products/adf4371.html, https://www.analog.com/en/products/MAX2870.html. (datasheet, secondary extract)
3. Texas Instruments, *LMX2572 6.4-GHz low-power wideband RF synthesizer* datasheet SNAS740B (2019), https://www.ti.com/lit/ds/symlink/lmx2572.pdf, p. 1. (datasheet)
4. Texas Instruments, *LMX2594 15-GHz wideband PLLatinum RF synthesizer* datasheet SNAS696C, https://www.ti.com/lit/ds/symlink/lmx2594.pdf, p. 1. (datasheet)
5. Texas Instruments, *LMX2820 22.6-GHz wideband PLLatinum RF synthesizer* datasheet, https://www.ti.com/lit/ds/symlink/lmx2820.pdf, p. 1. (datasheet)
6. Analog Devices, *ADF4159 Direct Modulation/Fast Waveform Generating 13 GHz Fractional-N Frequency Synthesizer* datasheet, https://www.analog.com/media/en/technical-documentation/data-sheets/adf4159.pdf (features via search extract). (datasheet, secondary extract)
7. Texas Instruments, *LMX2491 6.4-GHz low-noise RF PLL with ramp/chirp generation* datasheet SNAS711A, https://www.ti.com/lit/ds/symlink/lmx2491.pdf, p. 1. (datasheet)
8. Texas Instruments, *LMX2571 low-power, high-performance PLLatinum RF synthesizer with FSK modulation* datasheet, https://www.ti.com/lit/ds/symlink/lmx2571.pdf, p. 1. (datasheet)
9. Mini-Circuits datasheets ADE-1+, ADEX-10L+, SYM-25DHW+, https://www.minicircuits.com/pdfs/ADE-1+.pdf etc. (fetched 2026-09-27). (datasheet)
10. Texas Instruments, *TRF3705 300-MHz to 4-GHz quadrature modulator* datasheet SLWS223B, https://www.ti.com/lit/ds/symlink/trf3705.pdf, p. 1. (datasheet)
11. Silicon Labs, *Si5351A/B/C-B* datasheet Rev 1.3 (2020), mirror https://download.mikroe.com/documents/datasheets/Si5351-datasheet.pdf (range change 8 kHz–160 MHz → 2.5 kHz–200 MHz via search extract). (datasheet, secondary extract)
12. QRP Labs, *MS5351M performance*, https://qrp-labs.com/synth/ms5351m.html; xiaolaba, *MS5351_Si5351_testing*, https://github.com/xiaolaba/MS5351_Si5351_testing. (hobbyist measurement — anecdotal but quantitative)
13. Texas Instruments datasheets: LMK04828 (SNAS605AS), CDCE913 (SCAS849I, 2024), LMK61E2 (SNAS674C), https://www.ti.com/lit/ds/symlink/<part>.pdf, p. 1. (datasheet)
14. Analog Devices, *AD9850 CMOS 125 MHz complete DDS synthesizer* (Rev H) and *AD9910 1 GSPS 14-bit DDS* (Rev E) datasheets — features via search extract: https://www.analog.com/media/en/technical-documentation/data-sheets/AD9850.pdf, https://www.analog.com/media/en/technical-documentation/data-sheets/AD9910.pdf. (datasheet, secondary extract)
15. This KB: [Phase noise and jitter](../07-noise-linearity/phase-noise-and-jitter.md), [Oscillators](../05-analog-electronics/oscillators.md), [Crystals and resonators](../04-real-components-hf/crystals-and-resonators.md). (internal)

## [rf-switches-attenuator-parts](rf-switches-attenuator-parts.md)
*RF switches, digital step attenuators, fixed pads, limiters and T/R switching — part selection guide*

1. Local JLCPCB/LCSC parts database (jlcparts in-stock snapshot, newest record 2026-04-01) via `jlc-trawler`; LCSC product-page parametrics (fetched 2026-09-29); JLC basic/preferred 0402 resistor list from the same snapshot. (distributor data)
2. Skyworks product pages (specification tables; fetched 2026-09-29): https://www.skyworksinc.com/Products/Switches/SKY13453-385LF, …/SKY13351-378LF, …/SKY13330-397LF, …/SKY13317-373LF, …/AS179-92LF, …/AS193-73LF. (manufacturer)
3. pSemi, *PE4259 UltraCMOS High-power SPDT RF Switch 10 MHz–3.0 GHz* product specification, https://www.psemi.com/pdf/datasheets/pe4259ds.pdf, p. 1. (datasheet)
4. pSemi, *PE42420 UltraCMOS SPDT RF Switch 20–6000 MHz*, https://www.psemi.com/pdf/datasheets/pe42420ds.pdf, p. 1. (datasheet)
5. pSemi, *PE42442 UltraCMOS SP4T RF Switch 30 MHz–6 GHz*, https://www.psemi.com/pdf/datasheets/pe42442ds.pdf, p. 1. (datasheet)
6. Analog Devices product summaries HMC624A, HMC472A, HMC849A (via search extracts; analog.com not reachable by script). (manufacturer, secondary extract)
7. pSemi, *PE43711 UltraCMOS RF Digital Step Attenuator 9 kHz–6 GHz*, https://www.psemi.com/pdf/datasheets/pe43711ds.pdf, p. 1. (datasheet)
8. pSemi, *PE4312 UltraCMOS RF Digital Step Attenuator 1 MHz–4 GHz*, https://www.psemi.com/pdf/datasheets/pe4312ds.pdf, p. 1. (datasheet)
9. Mini-Circuits, *DAT-31R5A+ Series Digital Step Attenuator*, https://www.minicircuits.com/pdfs/DAT-31R5A-PN+.pdf, p. 1. (datasheet)
10. pSemi, *PE4314 UltraCMOS RF Digital Step Attenuator 1 MHz–2.5 GHz* (75 Ω), https://www.psemi.com/pdf/datasheets/pe4314ds.pdf, p. 1. (datasheet)
11. This KB: [RF switches, attenuators and limiters (theory)](../06-rf-circuits/rf-switches-attenuators-limiters.md), [Resistors at RF](../04-real-components-hf/resistors-at-rf.md). (internal)

## [filter-parts-saw-ceramic-ltcc](filter-parts-saw-ceramic-ltcc.md)
*Filter parts — SAW, LTCC/ceramic, chip low-pass, baluns-with-filter, cavity and lumped filters for 433/868/915 MHz, GNSS and 2.4 GHz (selection guide)*

1. Local JLCPCB/LCSC parts database (jlcparts in-stock snapshot, newest record 2026-04-01) via `jlc-trawler`; LCSC product-page parametrics (fetched 2026-09-29) for SAW/LTCC/chip filters and baluns. (distributor data)
2. Mini-Circuits datasheets LFCN-400+, LFCN-490+, LFCN-1000+, LFCN-1575+, LFCG-900+, HFCN-1100+, BFCN-1560+, https://www.minicircuits.com/pdfs/<model>.pdf (fetched 2026-09-27), p. 1 tables. (datasheet)
3. This KB: [RF filters — technologies and microstrip design](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md); [Passive LC filter design from low-pass prototypes](../01-circuit-theory/passive-filter-design-prototypes.md) (Chebyshev formula). (internal)
4. NanoVNA V2 forum (nanorfe.com) threads on narrowband/UHF frequency accuracy — relevant to measuring SAW filters with low-cost VNAs. (forum — anecdotal)

## [connectors-and-cables-parts](connectors-and-cables-parts.md)
*RF connectors and cable assemblies — SMA, SMB, MCX, MMCX, U.FL/MHF, W.FL, N, BNC, 3.5/2.92 mm; pigtails, semi-rigid and sourcing (selection guide)*

1. Local JLCPCB/LCSC parts database (jlcparts in-stock snapshot, newest record 2026-04-01) via `jlc-trawler`; LCSC product-page parametrics (fetched 2026-09-29) — connector ratings, stock, prices; RF cable assemblies. (distributor data)
2. This KB: [Coaxial lines and RF cables](../03-transmission-lines-matching/coax-and-cables.md) — cable loss table (RG-58/174/316, LMR, 1.13 mm) and TE₁₁ cutoff. (internal)
3. Hirose U.FL/W.FL/X.FL catalogues (U.FL Series 2020–2021: mated height 1.9–2.4 mm; X.FL 0.94/1.2 mm; W.FL 1.4/1.65 mm) and I-PEX MHF4 product page (mated height 1.2–1.7 mm max, "up to 12 GHz") via search extracts; Wikipedia *Hirose U.FL* (30 cycles, DC–6 GHz). https://www.hirose.com/product/en/products/W.FL/, https://www.i-pex.com/product/mhf-4. (manufacturer catalogue, secondary extract)
4. Connector torque guides: Taoglas APN-25-8-001 *SMA connector torque guide*; Times Microwave *Connector torque requirements*, https://timesmicrowave.com/connector-torque-requirements/; Anritsu *RF and microwave connector care* 10100-00031D — SMA 5/8 in-lb, N 12–15 in-lb, 3.5/2.92 mm 8 in-lb (via search extract). (application notes)
5. Wikipedia, *SMA connector*, *N connector* — frequency ratings (secondary). (encyclopedia)
6. I-PEX, *MHF I LK* and *MHF 4L LK* product pages / Future Electronics summary — lock, 35 N / 23 N initial mating force, U.FL-intermateable, https://www.i-pex.com/product/mhf-I-lk. (manufacturer, secondary extract)

## [pcb-substrates-parts](pcb-substrates-parts.md)
*PCB substrates for RF — what JLCPCB, PCBWay, OSH Park and Aisler actually offer (FR-4 grades, RO4350B, PTFE), cost, lead time and when low-loss laminate is worth it*

1. JLCPCB, *Controlled impedance PCB parameters and stackup*, https://jlcpcb.com/impedance (fetched 2026-09-29) — prepreg Dk 7628 4.4, 3313 4.1, 1080 3.91, 2116 4.16; core 4.6; soldermask 3.8. (manufacturer)
2. JLCPCB, *PCB capabilities*, https://jlcpcb.com/capabilities/pcb-capabilities (fetched 2026-09-29) — "RF PCB 1 oz copper, 2-layer RF PCBs with Rogers and PTFE cores", FR-4 2-layer Dk 4.5, Rogers/PTFE max panel 590 × 438 mm. (manufacturer)
3. JLCPCB news, *JLCPCB offers Rogers & PTFE high-frequency PCBs*, https://jlcpcb.com/news/rogers-ptfe-high-frequency-pcb-available (fetched 2026-09-29) — RO4350B 0.51/0.76/1.52 mm (finished 0.6/0.9/1.65 mm), ZYF PTFE Dk/Df, 2 layers, 1 oz, prices from US$99.5 / US$50.5. (manufacturer)
4. PCBWay, *PCB capabilities*, https://www.pcbway.com/capabilities.html (fetched 2026-09-29) — board materials incl. Rogers-4 series + FR-4 mixed, pure Rogers-4 multilayer (4450F), PTFE, PTFE + FR-4; lead-time statement from a search extract. (manufacturer)
5. This KB: [PCB stackups and laminate materials](../13-pcb-rf-layout-emc/stackups-and-materials.md) (W3-C1) — loss per cm, TG155 gotcha, design vs process Dk, JLC HF "from US$47". (internal)
6. OSH Park Docs, *4 Layer Prototype Service* (stackup table, FR408HR 2113 prepreg Dk 3.61 @ 1 GHz, 2025 material notice), https://docs.oshpark.com/services/four-layer/ (fetched 2026-09-29). (manufacturer)
7. OSH Park Docs, *Fabrication services* (2L US$5/in², 4L US$10/in², lead times), https://docs.oshpark.com/services/ (fetched 2026-09-29). (manufacturer)
8. D. Harmon, *OSHPark 4 Layer PCB Measurements* (2018), https://harmoninstruments.com/posts/oshpark_4l.html — used beyond 50 GHz; Z₀ ~56 Ω vs design. (blog — anecdotal measurement)
9. Aisler, *Beautiful Boards*, https://aisler.net/en/products/boards (fetched 2026-09-29) — FR-4 2/4+ layers, EU manufacture from 2 business days, from €14.20. (manufacturer)
10. Rogers Corp., *RO4000 series laminates* data sheet (process vs design Dk) — via [5] and [dielectrics](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md). (datasheet)

## [adcs-dacs-for-sdr](adcs-dacs-for-sdr.md)
*ADCs, DACs and audio codecs for DIY SDRs and radars — LTC2208, AD9226, ADS42LB69, ADS4249, ADC3664, AD9680/AD9208, ADC12DJ3200, MAX19506, AD9708/AD9767, PCM1808, ADAR7251, RFSoC (selection guide)*

1. Analog Devices, *LTC2208 16-Bit, 130 Msps ADC* data sheet (2208fc), https://www.analog.com/media/en/technical-documentation/data-sheets/2208fc.pdf — 78 dBFS noise floor, 100 dB SFDR, 700 MHz inputs, 70 fs jitter (via search extract). (datasheet, secondary extract)
2. Texas Instruments, *ADC3664 14-bit 125 MSPS dual ADC* data sheet, https://www.ti.com/lit/ds/symlink/adc3664.pdf, p. 1 — NSD −156.9 dBFS/Hz, SNR 77.5 dBFS, 100 mW/ch, 1.4 GHz BW. (datasheet)
3. Texas Instruments, *ADS4249 dual 14-bit 250 MSPS ultralow-power ADC* SBAS534E, https://www.ti.com/lit/ds/symlink/ads4249.pdf, p. 1. (datasheet)
4. Texas Instruments, *ADS42LBx9 14/16-bit 250 MSPS ADCs* data sheet, https://www.ti.com/lit/ds/symlink/ads42lb69.pdf, p. 1. (datasheet)
5. Analog Devices AD9226 product page (12-bit 65 MSPS, via search extract); AliExpress AD9226 module listings (prices). (manufacturer / marketplace)
6. Analog Devices/Maxim, *MAX19506 dual 8-bit 100 Msps ADC* data sheet, https://www.analog.com/media/en/technical-documentation/data-sheets/max19506.pdf — 49.8 dBFS, 69 dBc, 57 mW/ch (via search extract). (datasheet, secondary extract)
7. Analog Devices, *AD9680* and *AD9208* data sheets / product pages (via search extracts): https://www.analog.com/en/products/ad9680.html, https://www.analog.com/media/en/technical-documentation/data-sheets/AD9208.pdf. (datasheet, secondary extract)
8. Texas Instruments, *ADC12DJ3200 6.4 GSPS single / 3.2 GSPS dual 12-bit RF-sampling ADC*, https://www.ti.com/lit/ds/symlink/adc12dj3200.pdf, p. 1. (datasheet)
9. Texas Instruments, *AFE7950 4T6R RF sampling AFE* SBASA41E (2025), https://www.ti.com/lit/ds/symlink/afe7950.pdf, p. 1. (datasheet)
10. Real Digital, *RFSoC 4x2* (ZU48DR, 4 × 5 GS/s ADC, 2 × 14-bit 9.85 GS/s DAC, academic US$2,499), https://www.realdigital.org/hardware/rfsoc-4x2; Red Pitaya documentation (STEMlab 125-14: LTC2145-14, Zynq 7010), https://redpitaya.readthedocs.io (via search extracts). (vendor)
11. Texas Instruments, *DAC5672 14-bit 275 MSPS DAC* SLAS440D, https://www.ti.com/lit/ds/symlink/dac5672.pdf, p. 1. (datasheet)
12. Texas Instruments PCM1808 and TLV320AIC3204 data sheets p. 1 (https://www.ti.com/lit/ds/symlink/pcm1808.pdf, …/tlv320aic3204.pdf); local JLCPCB/LCSC parts database (jlcparts in-stock snapshot, newest record 2026-04-01) via `jlc-trawler`. (datasheet; distributor data)

## [phased-array-and-radar-parts](phased-array-and-radar-parts.md)
*Phased-array and radar parts — beamformer ICs, phase shifters, mmWave radar SoCs (TI, Infineon, Acconeer), ADI 24 GHz chipset and radar modules (procurement guide)*

1. Texas Instruments, *IWR6843 single-chip 60–64 GHz mmWave sensor* datasheet, https://www.ti.com/lit/ds/symlink/iwr6843.pdf, p. 1. (datasheet)
2. Texas Instruments, *IWR6843AOP* datasheet, https://www.ti.com/lit/ds/symlink/iwr6843aop.pdf, p. 1. (datasheet)
3. Texas Instruments, *AWR1843 single-chip 76–81 GHz automotive radar sensor* datasheet, https://www.ti.com/lit/ds/symlink/awr1843.pdf, p. 1. (datasheet)
4. Texas Instruments, *IWRL6432 single-chip 57–64 GHz low-power mmWave sensor* datasheet, https://www.ti.com/lit/ds/symlink/iwrl6432.pdf, p. 1. (datasheet)
5. Infineon, *BGT60TR13C* data sheet v2.4.9 and product page (via search extract), https://www.infineon.com/part/BGT60TR13C. (datasheet, secondary extract)
6. LCSC listing for BGT60LTR11AIPE6327XUMA2 (61–61.5 GHz, 10 dBm, 128 mA TX), https://www.lcsc.com/product-detail/C3606906.html. (distributor data)
7. Acconeer, *A121 Pulsed Coherent Radar datasheet* v1.5 (Mouser mirror) and product pages (via search extract), https://www.mouser.com/datasheet/2/1126/A121_datasheet-3133196.pdf. (datasheet, secondary extract)
8. This KB: [DIY radar hardware](../11-radar/diy-radar-hardware.md) (IMDA TS SRD Sep 2023 radar bands; 77–81 GHz via IMDA TS UWB 2016) and [Singapore IMDA rules](../19-regulations-safety/singapore-imda-rules.md). (internal)
9. Analog Devices ADF4159 / ADF5901 / ADF5904 / ADAR7251 product information via LCSC parametrics and search extracts (ADI site not reachable by script). (manufacturer/distributor, secondary)
10. Local JLCPCB/LCSC parts database (jlcparts in-stock snapshot, newest record 2026-04-01) via `jlc-trawler`; LCSC product-page parametrics (fetched 2026-09-29). (distributor data)
11. This KB: [Phase shifters and TTD components](../12-phased-arrays/phase-shifters-ttd-components.md) and [DIY phased-array projects](../12-phased-arrays/diy-phased-array-projects.md) (W2-B5) — ADAR1000/ADTR1107, HMC64x, PE44820, QPC2108, ADAR4002, JSPHS-2484+, Phaser, KrakenSDR. (internal)
12. Anokiwave, *AWMF-0108 26–30 GHz single-pol quad beamformer IC* product page / Microwave Journal (2016) (via search extract), https://www.anokiwave.com/products/awmf-0108/. (manufacturer, secondary extract)
13. Qorvo, *Qorvo to Acquire Anokiwave* (press release, Jan 2024) and Qorvo FY2024 10-K (completion 5 Feb 2024, US$93.7 M), https://www.qorvo.com/newsroom/news/2024/qorvo-to-acquire-anokiwave. (corporate filing)
14. Analog Devices, *ADAR2001* and *ADAR2004* data sheets (via search extract), https://www.analog.com/media/en/technical-documentation/data-sheets/adar2001.pdf, …/adar2004.pdf. (datasheet, secondary extract)
15. This KB: [DIY radar hardware](../11-radar/diy-radar-hardware.md) — HB100 and IPM-165/CDM324 specifications. (internal)
16. Infineon, *BGT24LTR11* application note AN615 / product page (TX ≈ 6 dBm typ.) (via search extract). (application note, secondary extract)

## [sourcing-and-eval-boards](sourcing-and-eval-boards.md)
*Sourcing RF parts and evaluation boards from Singapore — distributors, LCSC/JLC basic vs extended vs global-sourcing parts, eval boards, samples, marketplace modules and counterfeit pitfalls*

1. Mouser SG, DigiKey SG (delivery information), element14 SG (delivery information, local stock) — free-shipping thresholds via search extract (2026-09): https://www.mouser.sg, https://www.digikey.sg/en/help-support/delivery-information, https://sg.element14.com/help-delivery-information. (distributor, secondary extract)
2. JLCPCB, *PCB Assembly FAQs* (last updated 9 Sep 2026), https://jlcpcb.com/help/article/pcb-assembly-faqs — setup US$8, stencil US$1.50, US$0.0017/joint, US$3 per extended part, preferred extended exempt, ~698 basic / 300k+ extended; JLC parts page (global sourcing description), https://jlcpcb.com/parts. (manufacturer)
3. Local JLCPCB/LCSC parts database (jlcparts in-stock snapshot, newest record 2026-04-01) via `jlc-trawler`, and the part tables in the other 18-domain pages. (distributor data)
4. Skyworks, *SKY66423-11* product page (EVB list, SKY66423-11EK1 MSRP US$99), https://www.skyworksinc.com/en/Products/Front-end-Modules/SKY66423-11 (fetched 2026-09-29). (manufacturer)
5. Real Digital, *RFSoC 4x2* (academic US$2,499), https://www.realdigital.org/hardware/rfsoc-4x2 (via search extract); ADI Phaser price from [DIY phased-array projects](../12-phased-arrays/diy-phased-array-projects.md). (vendor / internal)
6. Analog Devices, *Frequently Asked Questions About Sample Requests*, https://www.analog.com/en/support/sample-products/faq-sample-requests.html (via search extract: 2 pcs/part, 4 parts/request/14 days, company or university e-mail). (manufacturer, secondary extract)
7. u-blox, *Counterfeit products and u-blox brand misuse*; u-blox portal thread *PSA: fake u-blox modules*; rtklibexplorer, *Counterfeit M8N modules* (2016), https://rtklibexplorer.wordpress.com/2016/12/06/counterfeit-m8n-modules/. (manufacturer notice; blog)
8. F5OEO/tezuka_fw discussion #184 *Fixing up the Hamgeek pluto+ AD9363 SDR*, https://github.com/F5OEO/tezuka_fw/discussions/184. (forum — anecdotal)
9. NanoVNA V2 forum (nanorfe.com), threads on clones using salvaged/reject parts. (forum — anecdotal)
10. rtl-sdr.com LNA articles and marketplace SPF5189Z listings; Mini-Circuits PGA-103+ datasheet ("may be used as a replacement for SPF-5189Z"). (forum/marketplace — anecdotal; datasheet)

## [rf-modules](rf-modules.md)
*RF modules — GNSS (u-blox, Quectel, Unicore, ZHONGKEWEI), Wi-Fi/BLE (ESP32, nRF52), LoRa and telemetry modems, video transmitters and SDR modules; certification and antenna rules (selection guide)*

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

## Added by W5-E10 (2026-10-12) — coax-and-connector-practicalities
12. Hirose, *U.FL Series* datasheet (VSWR, 30 cycles, shock/vibration, cable-pull limits, extraction tool). https://media.digikey.com/pdf/Data%20Sheets/Hirose%20PDFs/UFL%20Series.pdf (datasheet)
13. Keysight, "Connector Care" / "Cleaning RF Connectors" help pages. (manufacturer guidance)
14. Times Microwave WK-U / CommScope 221213 weatherproofing kits; OnAllBands weatherproofing guide. (product data / practitioner)
15. This repository: `tools/verify/e10_coax.py`. (verification)
