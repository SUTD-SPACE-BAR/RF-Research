# Research log W3-C4: 18-components-parts
Status: complete (2026-09-29)
Owner scope: kb/18-components-parts/ (+ this log)

## Plan
- [x] rf-transceiver-ics — DONE 249 lines; Semtech (link 15), TI CC1101/CC1200/CC1310/CC1352, SiLabs Si4463/EFR32, ST S2-LP/STM32WL, Nordic nRF52/53/9160, ESP32 radios, ADI AD9361/63/64/ADRV9002, LMS7002M, AT86RF215, MAX2769, GNSS ICs
- [x] lna-pa-gain-block-mmics — DONE; LNAs, PAs, gain blocks, FEMs, GNSS LNA+SAW
- [x] mixers-plls-vcos-parts — DONE; mixers, IQ mod/demod, PLL/VCO (ADF4351, LMX2594/2572/2491, MAX2870, HMC830), clocks (Si5351, Si5341, LMK), TCXOs, DDS
- [x] rf-switches-attenuator-parts — DONE; PE42xxx, SKY13xxx, HMC, BGS, DSAs, pads, limiters, T/R switches
- [x] filter-parts-saw-ceramic-ltcc — DONE; SAW 433/868/915/1575, LTCC (LFCN/HFCN), Johanson, cavity, harmonic filters
- [x] connectors-and-cables-parts — DONE; SMA/SMB/MCX/MMCX/U.FL/MHF4/N/BNC/2.92; cables; sources
- [x] pcb-substrates-parts — DONE (procurement view; physics deferred to W3-C1 stackups page); JLCPCB/PCBWay/Aisler/OSH Park laminates, Rogers, cost
- [x] adcs-dacs-for-sdr — DONE; LTC2208, AD9226, AD9208, AD9680, ADS42LB69, MAX19506, audio codecs, RFSoC
- [x] phased-array-and-radar-parts — DONE (procurement view; 11/12 domains hold theory/devices); ADAR1000/2001, Anokiwave, phase shifters, TI IWR/AWR, BGT60/24, A121, ADF5904/5610
- [x] sourcing-and-eval-boards — DONE; SG distributors, LCSC/JLC basic/extended, eval boards, AliExpress pitfalls, MOQ, samples
- [x] rf-modules — DONE; LoRa (link 15), GNSS modules, Wi-Fi/BLE modules, SiK/RFD900x, VTX, SDR modules
- [x] _index.md, _sources.md — DONE (sources auto-compiled from page Sources sections; anchors checked)

Approach: WebFetch datasheet/product pages for key numbers (ask for exact spec tables, cross-check vs second source).
Local tool: jlc-trawler skill (local JLC/LCSC DB) for LCSC stock/basic-vs-extended checks.

## Log (append-only)
- 2026-09-27 — read CONVENTIONS.md, INDEX.md, task spec; folder empty; started log.

- 2026-09-27 — Method: vendor PDFs via curl + pdftotext (raw text, avoids WebFetch-summary errors) works for TI, Mini-Circuits,
  Microchip, SiLabs, Espressif; ADI (analog.com, wiki.analog.com), ST, Qorvo (429), Digikey (403) BLOCK curl/WebFetch -> used
  search extracts for those, marked. Datasheet text cache: scratchpad/ds/*.txt (TI: lmx2594, lmx2572, lmx2491, lmx2820, iwr6843,
  iwr6843aop, awr1843, iwrl6432, ads42lb69, cc1190, trf3705, lmk04828, cdce913, adc12dj3200, cc1125, cc2592, lmx2571, dac5672, ads4249,
  afe7950, lmk61e2; Mini-Circuits ~35 parts; AT86RF215; Si4463-C; EFR32FG23; ESP32-S3/C6).
- 2026-09-27 — wrote rf-transceiver-ics.md (FOM table, 5 comparison tables with LCSC#, 3 worked examples, picks/avoid).

- 2026-09-29 — LCSC product pages (JSON-LD PropertyValue) fetched with lcsc.py for ~40 LNA/PA/FEM parts; Skyworks product pages
  curl-able (SKY66423-11 +27 dBm NF 1.5; SKY65364-21 is LTB); SE2435L datasheet (+30 dBm 550 mA, 2f −22 dBc); RD01MUS2 DS.
  Wrote lna-pa-gain-block-mmics.md (7 tables, 4 worked examples incl. IIP3 penalty, SE2435L harmonic filter need 44 dB).

- 2026-09-29 — mixers/PLL page: TI DS p.1 (LMX2594/2572/2491/2820/2571, TRF3705, LMK04828, CDCE913, LMK61E2), MC mixers, LCSC
  attrs for ADI parts, search extracts (ADF4351/4371/MAX2870/ADF4159/Si5351/MS5351M/AD9850/AD9910), LCSC TCXO search. Check:
  FOM formula reproduces LMX2594 −110 dBc/Hz headline within 2.5 dB. Wrote mixers-plls-vcos-parts.md.

- 2026-09-29 — switches page: Skyworks /Products/Switches/<pn> pages (spec tables), pSemi PDFs psemi.com/pdf/datasheets/<pn>ds.pdf
  (curl OK): PE4259, PE42420, PE42442, PE43711, PE4312, PE4314 (75 ohm!). JLC basic 0402 resistor list = only 30 values in
  snapshot (+ preferred 150/300/47/51/75/680) -> pads 300/22, 150/33, 100/75. Wrote rf-switches-attenuator-parts.md.

- 2026-09-29 — filters page: LCSC SAW/LTCC attrs; MC LFCN/LFCG/HFCN/BFCN DS tables (LFCN-1000+ only 30 dB from 1.9 GHz; LFCN-490+
  40 dB from 880 MHz). Chebyshev check: 7-pole 0.1 dB fc 500 MHz -> 47.5 dB @ 868; fc 1.05 GHz -> 47.8 dB @ 1830. No documented
  'fake SAW' case found (search) -> stated honestly. Wrote filter-parts-saw-ceramic-ltcc.md.

- 2026-09-29 — connectors page: LCSC connector attrs (U.FL genuine vs clones; KH-IPEX 3 GHz rating; Molex 73251-1150 18 GHz),
  Hirose/I-PEX catalogue extracts (U.FL 30 cycles, heights; MHF4 12 GHz; MHF I LK 35 N), torque guides. Wrote connectors page.

- 2026-09-29 — substrates: JLC impedance/capabilities/news pages (RO4350B + ZYF PTFE, 2-layer, $99.5/$50.5), PCBWay capabilities,
  OSH Park docs (FR408HR 3.61, $10/in2), Aisler; W3-C1's stackups page already covers physics -> linked, not duplicated.

- 2026-09-29 — ADC page: TI DS p.1 (ADC3664, ADS4249, ADS42LB69, ADC12DJ3200, AFE7950, DAC5672, PCM1808, AIC3204); search extracts
  (LTC2208, MAX19506, AD9680/AD9208, RFSoC 4x2 $2,499, Red Pitaya LTC2145). ENOB/NSD/DR/jitter checks computed. Linked 14-sdr
  survey + 11-radar DIY pages (already cover boards/modules) rather than duplicating.

- 2026-09-29 — radar/array page: TI mmWave DS p.1 (IWR6843/AOP, AWR1843, IWRL6432), LCSC attrs (ADF5901/5904, BGT60LTR11, XM125,
  LD2410B, MAPS-010164), search extracts (BGT60TR13C, A121, BGT24LTR11, ADAR2001/2004 = body-scanner TX/RX not beamformers,
  AWMF-0108; Qorvo closed Anokiwave acquisition 5 Feb 2024). Wrote phased-array-and-radar-parts.md.

- 2026-09-29 — sourcing page: JLC PCBA FAQ (US$8 setup, $1.50 stencil, $0.0017/joint, $3/extended, preferred exempt, 698 basic),
  SG distributor free-shipping thresholds (search extract), ADI sample policy (2 pcs/part, 4 parts/14 days), counterfeit cases.

- 2026-09-29 — modules page: u-blox datasheets via curl (MAX-M10S, NEO-M9N, ZED-F9P, NEO-F10N, ZED-X20P): all list operational
  limits <=4 g / 80,000 m / 500 m/s 'assuming Airborne 4 g'; community: M10S invalid >500 m/s; AND/OR logic undocumented.
  Quectel/Unicore via search extracts; LCSC module stock. Wrote rf-modules.md. Next: _index.md, _sources.md.

- 2026-09-29 — wrote _index.md (reading order, page table, top-picks, FAQ with verified anchors) and _sources.md (method +
  per-page bibliography). Link check: all internal links resolve except 2 planned 13-domain slugs (mixed-signal-layout,
  jlcpcb-rf-manufacturing). Added checklists to substrates/sourcing/modules/connectors pages; per-channel BOM to radar page.
  TASK COMPLETE. No tools/verify scripts written (scope restricted to kb/18); verification snippets are inline in each page.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| S1 | jlcparts in-stock DB snapshot (newest 2026-04-01) via jlc-trawler | distributor data | all LCSC#/stock/price | snapshot; refresh before ordering |
| S2 | LCSC product pages JSON-LD parametrics | distributor data | NF/gain/IP3/etc. for many parts | distributor transcription of DS; frequency points often unstated |
| S3 | TI datasheets p.1 (≈30) via curl+pdftotext | datasheet | transceivers, PLLs, ADCs, mmWave | high |
| S4 | Mini-Circuits datasheets (≈35) | datasheet | LNAs, gain blocks, mixers, LTCC, DSA | high (page-1 tables) |
| S5 | pSemi datasheets (6), Skyworks product pages (8), SE2435L DS | datasheet/manufacturer | switches, DSAs, FEMs | high |
| S6 | u-blox datasheets (5) | datasheet | GNSS modules, operational limits | high |
| S7 | AT86RF215, Si4463-C, EFR32FG23, ESP32-S3/C6 datasheets | datasheet | transceivers | high |
| S8 | JLCPCB impedance/capabilities/news/FAQ pages; PCBWay capabilities; OSH Park docs; Aisler | manufacturer | substrates, PCBA fees | medium-high (prices change) |
| S9 | Search extracts for ADI/Maxim/LTC/ST/Qorvo/Quectel/Infineon/Acconeer docs | secondary extract | parts whose vendor sites block scripts | medium; marked in pages |
| S10 | Forums/blogs: u-blox portal, rtklibexplorer, F5OEO tezuka_fw, nanorfe, QRP-Labs, Harmon Instruments, rtl-sdr.com | forum/blog | counterfeits, clone behaviour, measurements | anecdotal except quantitative measurements |

## Contradictions / discrepancies found
- GNSS limits: u-blox datasheets say 80 km / 500 m/s / 4 g; forum posts quote 50 km (ITAR) and claim M8N 100 m/s vertical, M9N 20,000 m/s (clearly garbled); AND/OR enforcement logic undocumented.
- Task brief lists ADAR2001/ADAR2004 as beamformer ICs; ADI describes them as mmWave body-scanner x4 TX and 10–40 GHz 4-ch RX mixer (not phase-shifting beamformers).
- JLC HF board price: launch article US$99.5 (Rogers)/US$50.5 (PTFE) vs later JLC HF page 'from US$47' (W3-C1). Thickness: core 0.51/0.76/1.52 vs finished 0.6/0.9/1.65 mm (same article; both true).
- HMC472A: search extract '6-bit 0.5 dB LSB' vs common description 5-bit 1 dB LSB (unresolved).
- PGA-103+: MC DS gain 11 dB @ 2 GHz, NF 0.6 dB @ 1 GHz vs LCSC listing 18 dB / 1.5 dB (different frequency points).
- Si4463: SiLabs product page says 142–1050 MHz, −124 dBm; C2A datasheet p.1 says 142–1050 MHz, −129 dBm; B1 datasheet 119–1050 MHz, −126 dBm @ 500 b/s → revision differences (use C2A).
- AD9363 lower limit: ADI docs 325 MHz; one secondary article 380 MHz.
- nRF54L15 1 Mb/s sensitivity: −96 vs −98 dBm in different Nordic/partner sources.
- CC1190 "6 dB sensitivity improvement" (TI) vs Friis estimate 2.6–4.3 dB for chip NF 6–8 dB (implies TI assumed ~10 dB chip NF).

## Knowledge gaps noticed (for later gap-filling)
- ADI/ST/Qorvo primary datasheets unread (script-blocked): ADF4351/MAX2871 phase noise, HMC472A bits, LTC2208/AD9226, S2-LP, nRF5340 TX/RX figures.
- Bench data needed: Chinese handset LNAs, marketplace SPF5189Z/AD9226 modules, U.FL vs MHF I LK vibration, B39431 SAW vs cavity preselector.
- u-blox limit enforcement logic (AND/OR); Quectel/Unicore operational limits.
- Mouser/DigiKey pricing not systematically captured; SG local fabs with RF laminates not surveyed.
- NF of broadband LNAs at 433 MHz (curves not read); Chinese handset LNAs only distributor-characterised; 433 MHz FEM options thin.

## Cross-domain notes (things other domains should cover/link)
- INDEX.md needs a rebuild (tools/build_index.py) to list the 11 new 18-domain pages + _index/_sources (not in my scope).
- 13/jlcpcb-rf-manufacturing (planned, W3-C1) should link 18/pcb-substrates-parts (procurement view) and 18/sourcing-and-eval-boards (JLC PCBA fees).
- 08/gnss-antennas and 15/rocket-telemetry-radio-design should cite the u-blox datasheet operational limits (<=4 g, 80 km, 500 m/s, Airborne 4 g) from 18/rf-modules.
- 19 could add rules for 5.8 GHz video transmitters and 2.4 GHz module EIRP (rf-modules points there).
- 20-projects-recipes: use the 'Top picks' table in 18/_index.md for BOMs (LoRa link, GNSS front end, FMCW build, LNA walkthrough).
- 06/rf-switches-attenuators-limiters (theory) could link the JLC-basic pi-pad table in 18/rf-switches-attenuator-parts.

## Resume instructions
- Task complete (2026-09-29): 11 pages + _index.md + _sources.md in kb/18-components-parts/. If extending: refresh the
  LCSC snapshot (trawl.py update), re-verify medium-confidence ADI/ST/Qorvo numbers from primary datasheets, and add bench
  measurements listed under Knowledge gaps.
