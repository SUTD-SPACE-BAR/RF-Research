---
title: Sourcing RF parts and evaluation boards from Singapore — distributors, LCSC/JLC basic vs extended vs global-sourcing parts, eval boards, samples, marketplace modules and counterfeit pitfalls
domain: 18-components-parts
slug: sourcing-and-eval-boards
tags: [sourcing, singapore, mouser, digikey, element14, lcsc, jlcpcb, basic-parts, extended-parts, preferred-extended, global-sourcing, eval-board, samples, aliexpress, counterfeit, spf5189z, neo-m8n, pluto-clone, nanovna-clone, moq, lead-time, gst, export-control]
prerequisites: []
related:
  - rf-transceiver-ics.md
  - lna-pa-gain-block-mmics.md
  - rf-modules.md
  - connectors-and-cables-parts.md
  - ../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md
  - ../14-sdr-dsp/sdr-hardware-survey.md
  - ../17-test-measurement/lab-setup-by-budget.md
  - ../17-test-measurement/nanovna-librevna-practical.md
level: intro
confidence: medium
last_updated: 2026-09-29
---

# Sourcing RF parts and evaluation boards (from Singapore)

## Questions this page answers
- Where should I buy RF parts in Singapore — Mouser, Digikey, element14, LCSC, AliExpress?
- What do JLCPCB "basic", "preferred extended", "extended" and "global sourcing" parts mean for my assembly bill?
- Which RF parts are realistically stocked at LCSC for JLC assembly?
- When should I buy an evaluation board instead of designing my own PCB, and what do they cost?
- Can I get free samples as a student?
- Which marketplace modules are commonly fake or mis-specified, and how do I check?

## TL;DR
- **Authorised distributors with Singapore storefronts**: **Mouser SG** (free shipping ≳ S$60), **DigiKey SG** (free delivery ≥ S$60, else S$24), **element14 SG** (free delivery on web orders > S$55 ex-GST; has a Singapore warehouse "local stock" range) (thresholds per search extracts, 2026-09 — verify) [1]. Use them for Mini-Circuits (also direct), ADI, TI, Qorvo, Skyworks, pSemi, Infineon, NXP, u-blox, Nordic and anything not at LCSC.
- **LCSC + JLCPCB assembly**: JLC's quoted PCBA price = US$8 setup + US$1.50 stencil + US$0.0017 per joint + components, and **US$3 per unique extended part**; **preferred extended** parts are exempt from that fee; ~698 basic parts vs 300k+ extended (JLC FAQ, updated 2026-09) [2]. **Every RF IC, SAW, LTCC filter and RF connector checked for this domain is extended** (none basic); only passives (e.g. 0402 resistors 22/33/100/330 Ω basic, 47/51/75/150/300 Ω preferred) avoid fees [3].
- **LCSC RF depth (2026-04 snapshot)**: deep for Semtech LoRa (SX1262 10k, LLCC68 16.5k), SX1280, CC1101, Si4463 (22k), nRF52832/52840/5340, ESP32-S3 modules (32k), SKY13453 switches (61k), Murata GNSS SAW (88k), Hirose U.FL (226k), TCXOs; thin (≤ 100) for AD936x, AT86RF215, ADF4159/ADF590x, beamformers; absent for many ADI high-speed ADCs, Guerrilla RF, most Mini-Circuits connectorised parts [3].
- **"Global Sourcing Parts"** at LCSC/JLC are procured on demand from external suppliers ("quality-assured parts from trusted global suppliers" per JLC) — longer lead times and higher prices; several RF parts appear only this way (QPL9547, PSA4-5043+, SE2435L, LR1121) [2][3].
- **Eval boards first** for anything above ~3 GHz, anything with a BGA, and any FEM/PA: vendor EVBs copy-able layouts (Skyworks SKY66423-11EK1 MSRP US$99 [4]; ADI Phaser ≈ US$2,875; RFSoC 4x2 academic US$2,499 [5]); Mini-Circuits TB- test boards for their MMICs/filters.
- **Samples**: ADI allows **2 pieces per part, up to 4 parts per request per 14 days**, company/university e-mail required [6] — SUTD addresses qualify in principle; TI restricts samples on some products; Mini-Circuits and others route through distributors or "EZ samples" (unverified details).
- **Marketplace (AliExpress/Taobao/Shopee) pitfalls, documented cases**: counterfeit **u-blox NEO-M8N** (ROM-only, firmware 2.01, cannot be updated; some re-labelled NEO-6M) [7]; **"AD9361" Pluto-class SDRs** that carry AD9363 silicon, TCXO/VCTCXO substitutions [8]; **NanoVNA clones** using salvaged/reject parts [9]; SPF5189Z LNA boards of unknown genuineness and stability [10]. No documented "fake SAW filter" case was found — but measure any unbranded RF part.
- **Singapore specifics**: GST 9 % applies to imports including low-value goods bought online (general knowledge; verify current rules); some high-performance RF/ADC parts carry US export-control classifications — distributors may ask for end-use statements (unverified per part).

## Intuition (no math)
RF parts are small, expensive to test and easy to fake: a remarked die looks identical, and a module with a different chip inside may "work" at close range while losing 10 dB of sensitivity. Authorised distributors buy directly from the manufacturer (traceable lots, datasheet-conformant parts, returns); marketplace sellers may be selling genuine surplus, reclaimed parts, or clones. For flight hardware, buy from an authorised channel or LCSC/JLC's own stock; use the marketplace for antennas, cables, cheap modules for experiments, and parts you can measure on arrival.

The JLC cost model rewards **few unique extended parts**: every extra unique RF part costs US$3 on top of its price, regardless of quantity. It is often cheaper to use one RF switch type everywhere or to move rarely-changed RF parts to a hand-soldered second pass.

## The math — cost and risk rules
### Level 1 — JLC assembly cost for an RF board
$$C \approx 8 + 1.5 + 0.0017\,N_{joints} + 3\,N_{ext,unique} + \sum \text{part prices}\quad[\text{US\$}]$$
(economic assembly, per JLC FAQ [2]; shipping and PCB extra). Example: 30 unique extended parts (typical RF+MCU board) → US$90 in fees alone — often more than the parts.

### Level 2 — "is the cheap part worth the risk?"
Expected cost of a marketplace part = price + P(bad) × (debug time × hourly value + board respin). With P(bad) of even 10 % and a day of debugging, a US$1 saving is negative value for anything on the critical path.

## Design equations & rules of thumb
| Rule | When valid | Typical values |
|---|---|---|
| JLC fee = US$3 × unique extended parts | economic PCBA | 20 RF/IC types → US$60 |
| Consolidate to preferred-extended/basic passives | pads, dividers, bias | [switches](rf-switches-attenuator-parts.md) pad tables |
| Order ≥ free-shipping threshold (S$55–60) | SG distributors | batch orders per project phase |
| Buy 2–3 spares of every RF IC | prototype runs | rework destroys QFNs |
| Measure every unbranded RF part | marketplace | S21/S11 with NanoVNA, NF via SDR comparison |

## Comparison tables
### A. Where to buy (Singapore, 2026-09)
| Source | Strengths | Weaknesses | Best for |
|---|---|---|---|
| Mouser SG | huge RF catalogue (Mini-Circuits, Qorvo, Skyworks, ADI, TI), datasheets, fast DHL | price at qty 1; some parts export-screened | prototyping parts, eval boards |
| DigiKey SG | same class; good parametric search; S$24 under S$60 | | |
| element14 SG | local SG warehouse stock for some lines, academic accounts | smaller RF range | quick local delivery |
| RS Components SG | lab consumables, tools, some RF | | tools, connectors |
| **LCSC** | cheap passives, Chinese RF (Maxscend, Awinic, TST SAWs), in-stock Semtech/Nordic/Espressif; direct feed into JLC assembly | extended/global-sourcing fees; thin Western RF stock | JLC-assembled production boards |
| Manufacturer web stores (Mini-Circuits, ADI, TI) | genuine, full product range, EVBs | shipping, MOQ on some | eval boards, samples |
| Marketplaces (AliExpress, Taobao, Shopee, Lazada) | antennas, cables, modules, SDRs cheap | counterfeits, variable quality | experiments, non-critical items |
| Local shops (e.g. Sim Lim Tower) | same-day adapters, cables, tools | limited RF parts, prices vary (anecdotal) | emergencies |

### B. LCSC/JLC part classes
| Class | Fee at JLC | Examples (RF-relevant) |
|---|---|---|
| Basic | none | 0402/0603 resistors & MLCCs (limited value list, ~30 basic 0402 R values in the snapshot) [3] |
| Preferred extended | none (exempt) | some passives (e.g. 0402 47/51/75/150/300 Ω) [2][3] |
| Extended | US$3 per unique part | all RF ICs, SAWs, LTCC filters, RF connectors, TCXOs [3] |
| Global sourcing | procured on demand; price/lead time vary | QPL9547TR7, PSA4-5043+, SE2435L, LR1121, MAX-M10S, SAM-M10Q (listed as "Global Sourcing Parts") [3] |

### C. Evaluation boards and platforms (examples; check current prices)
| Board | Vendor | What for | Price hint |
|---|---|---|---|
| SKY66423-11EK1/EK2/EK3 | Skyworks | 915/868 MHz FEM (+27 dBm) with SX1261 reference | MSRP US$99 [4] |
| Mini-Circuits TB-xxx (e.g. TB-PMA3-14LN+) | Mini-Circuits | MMIC/filter characterisation with SMA | tens of US$ (unverified) |
| EVAL-CN0566-RPIZ (Phaser) | ADI | 8-ch 10 GHz beamforming + FMCW | ≈ US$2,875 (12-domain) |
| ADALM-PLUTO, AD-FMCOMMS boards | ADI | AD936x SDR | Pluto ≈ US$250 (14-domain) |
| TI LMX2594EVM, LMX2572EVM, IWR6843 EVMs | TI | PLL / mmWave radar | (unverified) |
| Semtech SX1262 dev kits (e.g. SX1262MB2CAS) | Semtech | LoRa reference RF layout | (unverified) |
| RFSoC 4x2 | Real Digital / AMD | GS/s direct sampling | US$2,499 academic [5] |
| Infineon DEMO BGT60TR13C, Acconeer XE125 | Infineon, Acconeer | 60 GHz radar | (unverified) |

### D. Marketplace items: documented problems
| Item | Problem | Check | Source |
|---|---|---|---|
| u-blox NEO-M8N modules | counterfeit: no flash, locked to FW 2.01 (2013), some are re-labelled NEO-6M | u-center: firmware/ROM version, try FW update, QR/label check | [7] |
| Pluto+ / LibreSDR "AD9361" | AD9363 configured as AD9361; TCXO vs VCTCXO swaps | read chip marking; measure performance above 3.8 GHz and at 56 MHz BW | [8] (anecdotal) |
| NanoVNA clones | salvaged/reject parts, poor performance | compare with a known-good unit/cal standards | [9] (forum) |
| SPF5189Z LNA boards | obsolete chip, variable matching/shielding, oscillation | S21 with NanoVNA, NF comparison with an SDR | [10] (anecdotal) |
| nRF24L01+ modules | clone silicon common (anecdotal) | register/behaviour tests; range test | [rf-transceiver-ics](rf-transceiver-ics.md) |
| EBYTE LoRa modules | genuine but marketing sensitivity claims optimistic by ~18 dB | range/PER test | [LoRa modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md) |

## Worked examples
### 1. JLC bill for a LoRa + GNSS flight board
Unique extended parts: SX1268, TCXO, SAW (433), SKY13453 switch, U.FL, GNSS module, GNSS SAW, BGA524 LNA, MCU, IMU, baro, 3 regulators, 2 connectors, ESD, crystal ≈ 18 → **US$54** in extended fees + US$9.50 setup/stencil + joints (~500 joints → US$0.85) + parts. Reduce by sharing parts (one regulator type, one ESD diode type) and using basic/preferred passives for pads and bias networks.

### 2. Should I use the marketplace GNSS module or a MAX-M10S from LCSC?
MAX-M10S at LCSC: C4153167, ~US$9.07, 1,165 in stock (global sourcing) [3]; marketplace "M10" modules are cheaper but the NEO-M8N history [7] shows fakes exist. For flight: buy the module from LCSC/Mouser and verify the firmware string on first power-up; keep marketplace modules for bench tests.

## Practical notes
- **Datasheet revisions**: download the datasheet from the manufacturer, not the distributor mirror; errata (e.g. SX126x) matter ([Semtech family](../15-lora-ism-radios/semtech-chip-family.md)).
- **Moisture sensitivity**: many RF QFN/LGA parts are MSL 3 — bake before hand-reflow if the bag has been open (standard practice).
- **ESD**: GaAs/pHEMT LNAs are ESD-sensitive (PSA4-5043+ Class 1B, 500 V HBM [lna parts](lna-pa-gain-block-mmics.md)); use a grounded mat.
- **Lifecycle checks**: look for "NRND", "Last Time Buy" (SKY65364-21, AS193-73LF found in this domain) before designing in.
- **Keep an RF parts kit**: SMA adapters, 3/6/10/20 dB attenuators, DC blocks, bias tee, 50 Ω loads, U.FL pigtails, a few LNAs/gain blocks, a NanoVNA/LibreVNA ([lab setup by budget](../17-test-measurement/lab-setup-by-budget.md)).
- **Refreshing LCSC data**: this domain's stock/prices are from a 2026-04 snapshot; run `python3 ~/.claude/skills/jlc-trawler/scripts/trawl.py update` (≈ 1 GB) or `refresh <C-numbers>` before ordering.

## Incoming-inspection checklist for RF parts and modules
| Step | What to check | Tool |
|---|---|---|
| 1. Packaging | manufacturer reel/label, lot/date code, MSL label, ESD bag | eyes, datasheet |
| 2. Marking | marking code vs datasheet "package marking" table; font/laser quality vs manufacturer photos | loupe/microscope |
| 3. Dimensions | body size, pad layout (clones sometimes differ) | calipers |
| 4. Firmware/ID strings | GNSS ROM/FW version (UBX-MON-VER), radio chip version registers (e.g. SX126x, Si446x PART_INFO) | u-center, SPI read |
| 5. DC current | idle/RX/TX current vs datasheet | bench supply |
| 6. RF function | S21/S11 of filters, LNAs, switches; TX power/spectrum of modules | NanoVNA/LibreVNA, spectrum analyser or SDR |
| 7. Sensitivity/range | PER vs attenuation, or side-by-side comparison with a known-good unit | step attenuator, SDR |
| 8. Record | photo + results in the project log (record-everything tenet) | notebook/repo |

## Starter RF parts kit (order once, reuse for years)
| Item | Typical choice | Source |
|---|---|---|
| SMA adapter kit (M-M, F-F, right-angle, SMA-N, SMA-BNC) | genuine or good-quality marketplace kit | Mouser/DigiKey or marketplace |
| Fixed attenuators 3/6/10/20/30 dB, 2 W, DC–6 GHz | Mini-Circuits VAT-series or equivalent | Mini-Circuits/Mouser |
| DC blocks, bias tee, 50 Ω loads | Mini-Circuits BLK/ZFBT class | Mini-Circuits |
| U.FL–SMA pigtails (1.13 mm, 10–15 cm) | BAT Wireless BWIPX1-SMA-1.13L100 (LCSC C784403) | LCSC |
| LNA and gain-block test boards | PGA-103+/TQP3M9036 on your own coupon, or Mini-Circuits ZX60 | LCSC/Mini-Circuits |
| SMA torque wrench 8 in-lb | 5/16" bit | Mouser/DigiKey |
| VNA + SDR | LibreVNA or genuine NanoVNA; RTL-SDR v4/Airspy/Pluto | [lab setup by budget](../17-test-measurement/lab-setup-by-budget.md) |

## Recommended approach for Marcus
1. Prototype with vendor EVBs or modules; measure.
2. Lay out your own board copying the EVB RF section; choose parts in LCSC stock where possible; keep unique extended parts few.
3. Order RF ICs not at LCSC from Mouser/DigiKey/element14 SG (combine to beat the S$55–60 threshold) and hand-solder, or consign to JLC.
4. Treat marketplace parts as untrusted until measured; never fly them untested.

## Parts to avoid (or use knowingly)
- Marketplace GNSS modules and SDRs without firmware/chip verification [7][8].
- Last-time-buy parts for new designs.
- Parts with only a distributor parametric listing and no datasheet (common for small Chinese RF vendors) — test first.

## Common mistakes & misconceptions
- *"LCSC stock = JLC assembly availability."* Mostly true for in-stock items; "global sourcing" parts add lead time.
- *"Basic parts cover RF."* They do not (no RF ICs are basic).
- *"Free samples are free for anyone."* ADI requires registration with a company/university domain and limits quantities [6].

## How to simulate / verify
- Incoming inspection: marking/photo vs manufacturer images, X-ray if available, simple functional tests (S21/S11, current draw, firmware ID strings).
- Cost model:
```python
jlc = lambda n_joints, n_ext, parts_usd: 8 + 1.5 + 0.0017*n_joints + 3*n_ext + parts_usd
print(jlc(500, 18, 60))   # ~US$124 for one board batch (excl. PCB, shipping)
```

## Open questions / gaps
- Distributor free-shipping thresholds and GST treatment should be re-checked (search extracts only).
- TI and Mini-Circuits sample policies not verified from primary pages.
- No systematic counterfeit-rate data for LCSC "global sourcing" RF parts.

## Sources
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
