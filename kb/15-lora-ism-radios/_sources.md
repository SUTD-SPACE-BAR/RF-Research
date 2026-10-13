# 15-lora-ism-radios — bibliography

Reliability tags: (datasheet) (app note) (standard) (regulation) (peer-reviewed) (preprint) (review)
(vendor docs/web) (project docs) (community news) (forum — anecdotal) (internal = another KB page).
"Read" = full text consulted; "summary" = abstract/search-result level only.

## Semtech datasheets, app notes and code
- **[SX127x]** Semtech, *SX1276/77/78/79 Datasheet*, Rev 7, May 2020 — variant table, LoRa modem (SF6–12 SNR table, CR, LDRO, SF6), ToA §4.1.1.7, sensitivity tables (HF/LF), CCR/ACR, FERR (±25 % BW, SF10–12 ppm), FEI/AFC/PpmCorrection, RSSI formulas, PA_BOOST +20 dBm limits, OCP. https://cdn.sparkfun.com/assets/7/7/3/2/2/SX1276_Datasheet.pdf (datasheet; read)
- **[SX126x]** Semtech, *SX1261/2 Datasheet*, Rev 1.2, June 2019 (+ Rev 2.2 register table) — SNR table SF5–12, BW table, LDRO, packet format, ToA §6.1.4, power consumption, sensitivity, FERR, crystal/TCXO, drift rule §4.1.2, PA config, OCP, image calibration, Rx boost, known limitations §15, sync-word registers. https://cdn.sparkfun.com/assets/6/b/5/1/4/SX1262_datasheet.pdf (datasheet; read)
- **[SX128x]** Semtech, *SX1280/SX1281/SX1282 Datasheet*, Rev 3.0, July 2019 — 2.4 GHz LoRa/FLRC/GFSK, sensitivities, frequency-error rules, ranging. https://www.tme.eu/Document/1042f35a88b6ee421559d19923804032/SX128x.pdf (datasheet; read)
- **[AN1200.14]** Semtech, *LoRa Modulation Crystal Oscillator Guidance*, Rev 2.1, Aug 2018 — crystal spec (±10/±30 ppm), 2 ppb/g, ±25 % BW figure, TCXO list. (app note; read)
- **[AN1200.13]** Semtech, *LoRa Modem Designer's Guide* (2013) — ToA formula (same as SX127x DS). https://www.mouser.com/pdfdocs/semtech-lora-modem-design.pdf (app note; fetch timed out — content taken from [SX127x])
- **[sx126x_driver]** Semtech/Lora-net, `sx126x_driver` `src/sx126x.c` — ToA integer arithmetic. https://github.com/Lora-net/sx126x_driver (vendor code; read via summary)
- **[Semtech-web]** Semtech product pages (accessed 2026-09-27): SX1272, SX1268, LR1110, LR1121, LR2021. https://www.semtech.com (vendor web; read)

## Peer-reviewed / preprints / reviews
- **[Vangelista17]** L. Vangelista, "Frequency Shift Chirp Modulation: The LoRa Modulation," *IEEE Signal Processing Letters* 24(12):1818–1821, 2017. (peer-reviewed; summary)
- **[Tapparel20]** J. Tapparel, O. Afisiadis, P. Mayoraz, A. Balatsoukas-Stimming, A. Burg, "An Open-Source LoRa Physical Layer Prototype on GNU Radio," IEEE SPAWC 2020, arXiv:2002.08208; gr-lora_sdr https://github.com/tapparelj/gr-lora_sdr (peer-reviewed; read)
- **[Knight16]** M. Knight, B. Seeber, "Decoding LoRa: Realizing a Modern LPWAN with SDR," Proc. GNU Radio Conf. 2016. https://pubs.gnuradio.org/index.php/grcon/article/view/8 (conference; summary)
- **[Ghanaatian19]** R. Ghanaatian, O. Afisiadis, M. Cotting, A. Burg, "LoRa Digital Receiver Analysis and Implementation," ICASSP 2019, arXiv:1811.04146. (peer-reviewed; summary)
- **[Elshabrawy18]** T. Elshabrawy, J. Robert, "Closed-Form Approximation of LoRa Modulation BER Performance," *IEEE Commun. Lett.* 22(9):1778–1781, 2018. (peer-reviewed; summary)
- **[Bor16]** M. Bor, U. Roedig, T. Voigt, J. Alonso, "Do LoRa Low-Power Wide-Area Networks Scale?", ACM MSWiM 2016. https://uu.diva-portal.org/smash/get/diva2:1044681/FULLTEXT01.pdf (peer-reviewed; read)
- **[Croce18]** D. Croce, M. Gucciardo, S. Mangione, G. Santaromita, I. Tinnirello, "Impact of LoRa Imperfect Orthogonality: Analysis of Link-Level Performance," *IEEE Commun. Lett.* 22(4), 2018. (peer-reviewed; via [Maleki23])
- **[Maleki23]** A. Maleki, H. H. Nguyen, E. Bedeer, R. Barton, "A Tutorial on Chirp Spread Spectrum for LoRaWAN: Basics and Key Advances," arXiv:2310.10503, 2023. (review; read in part)
- **[DtS25]** "Doppler Estimation and Compensation Techniques in LoRa Direct-to-Satellite Communications," arXiv:2506.20858, 2025 — Norby, Doroshkin 2019 summary, LDRO. (preprint; read in part)
- **[Doroshkin19]** A. Doroshkin et al., "Experimental Study of LoRa Modulation Immunity to Doppler Effect in CubeSat Radio Communications," *IEEE Access* 7:75721–75731, 2019. (peer-reviewed; NOT accessible — cited via [DtS25])
- **[Zadorozhny22]** A. Zadorozhny et al., "First Flight-Testing of LoRa Modulation in Satellite Radio Communications in Low-Earth Orbit," *IEEE Access* 10:100006–100023, 2022. (peer-reviewed; via [DtS25])
- **[Sensors21]** "Characterizing the Impact of Doppler Effects on Body-Centric LoRa Links with SDR," *Sensors* 2021 (PMC8231252). (peer-reviewed; summary)
- **[Kinefuchi15]** K. Kinefuchi et al., "Prediction of in-flight RF attenuation by a rocket plume," *J. Spacecraft & Rockets* 52(2), 2015. (peer-reviewed; via 08-antennas)
- **[Brzynska23]** M. Brzynska, K. Klimaszewski, K. Martin, "A Localisation and Telemetry LoRa Node for Rockets," SoftCOM 2023. (peer-reviewed conference; read)

## Standards and regulations
- **[IMDA-SRD]** IMDA, *Technical Specification — Short Range Devices*, IMDA TS SRD Issue 1 Rev 3, **September 2023** (latest; 433/866/917 MHz rows identical to the April 2023 printing first read by W2-B6). (regulator standard; read)
- **[SG-EXEMPT]** *Telecommunications (Exemption from sections 53, 54(1)(b) and 55) Notification*, First Schedule item 13 (917–925 MHz 500 mW ERP — conflicts with TS SRD 30c's 100 mW/1 %; TS SRD treated as binding). Via [19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md). (legislation)
- **[EU-2025/105]** Commission Implementing Decision (EU) 2025/105 amending 2006/771/EC — EU SRD bands (primary legal source for the EU figures). (EU law)
- **[47CFR97]** 47 CFR 97.303(n)(2) — no amateur 33 cm in the White Sands box (Spaceport America); **[IREC-SBP]** IREC 2026 Student Band Plan Rev D; **[AU-LIPD]** ACMA LIPD Class Licence 2025. (regulation / competition rules / legislation)
- **[EN300220]** ETSI EN 300 220-2 V3.2.1 (2018-06), Table B.1 and FHSS clause. (standard; read)
- **[FCC15.247]** 47 CFR §15.247 (Cornell LII). https://www.law.cornell.edu/cfr/text/47/15.247 (regulation; read)
- **[RP002]** LoRa Alliance, *RP002-1.0.3 LoRaWAN Regional Parameters*, 2021. (standard; read)
- **[P.372]** ITU-R P.372-13 (2016) *Radio noise* — via [07 thermal noise page](../07-noise-linearity/thermal-noise-and-noise-temperature.md). (standard; internal)
- **[3GPP-B8]** 3GPP TS 36.101 operating band 8 (880–915 / 925–960 MHz). (standard; not re-read)

## Module and radio datasheets / manuals
- **[E22]** EBYTE, *E22-400TXXX Data Sheet* (2022). https://www.cdebyte.com/pdf-down.aspx?id=2179 (module datasheet; read)
- **[E220]** EBYTE, *E220-900T30D User Manual* (2020). https://www.cdebyte.com/pdf-down.aspx?id=349 (module manual; read)
- **[E32]** EBYTE, E32-433T30D listing/manual. (module; summary)
- **[LLCC68-mod]** DreamLNK, *DL-LLCC68-S datasheet* (LCSC C2894790). (module datasheet; read)
- **[RFM9x]** HopeRF RFM95W/96W/98W pages and datasheet. (module; summary)
- **[RFD900x]** RFDesign, *RFD900x DataSheet* V1.2. (datasheet; read)
- **[CC1101]** TI, *CC1101* datasheet SWRS061I. (datasheet; read)
- **[Si446x]** Silicon Labs, *Si4464/63/61/60* datasheet Rev 1.4. (datasheet; read)
- **[XBee900HP]** Digi, XBee-PRO 900HP datasheet. (datasheet; summary)
- **[nRF52840]**, **[nRF24L01+]** Nordic product specifications. (datasheets; summary)
- **[CC13xx]** TI CC1310/CC1352P product info. (vendor; summary)
- **[STM32WL]** ST STM32WLE5 datasheet; Seeed LoRa-E5. (datasheet/vendor; summary)

## Vendor / project documentation
- **[AltOS]** Altus Metrum, *AltOS Telemetry*. https://altusmetrum.org/AltOS/doc/telemetry.html (vendor docs; read)
- **[Featherweight]** Featherweight Altimeters, *GPS Tracker User's Manual*, 20 Feb 2025. (manufacturer manual; read — anecdotal claims)
- **[RadioLib]** J. Gromeš, RadioLib README. https://github.com/jgromes/RadioLib (library docs; read)
- **[Meshtastic]** Meshtastic docs: radio settings, LoRa configuration, range tests, supported devices. https://meshtastic.org/docs/ (project docs; read)
- **[SiK]** ArduPilot, SiK telemetry radio docs. https://ardupilot.org/copter/docs/common-sik-telemetry-radio.html (project docs; read)
- **[TTN-docs]** The Things Network docs: device classes, ADR; fair-use policy thread. (project docs; read/summary)
- **[Reticulum]** Reticulum Network Stack manual. https://reticulum.network/manual/ (project docs; summary)
- **[airtime-calc]** avbentem, airtime-calculator README. https://github.com/avbentem/airtime-calculator (community tool)

## Community / anecdotal
- **[TTN-records]** TTN articles: 702 km, 832 km (2020), 1336 km (2023) LoRaWAN records. (community news)
- **[Robinson20]** S. Robinson, "Frequency drift for LoRa devices, is it important?", StuartsProjects blog, 2020. (blog — anecdotal)
- **[RadioLib#507]** RadioLib discussion #507 "Range enlargement". (forum — anecdotal)
- **[SAC]** Spaceport America Cup / IREC reports (Stanford SSI 2017, Project Olympus 2022, MSU) — search summaries. (anecdotal)
- **[TTN-E32]** TTN forum "E32 'low-level' parameters". (forum — anecdotal)

## Internal cross-references used
- [08-antennas/antennas-on-rockets](../08-antennas/antennas-on-rockets.md), [antenna-polarization-and-circular-polarization](../08-antennas/antenna-polarization-and-circular-polarization.md), [yagi-uda-and-log-periodic](../08-antennas/yagi-uda-and-log-periodic.md), [helical-antennas](../08-antennas/helical-antennas.md)
- [07-noise-linearity/thermal-noise-and-noise-temperature](../07-noise-linearity/thermal-noise-and-noise-temperature.md), [noise-figure-and-friis](../07-noise-linearity/noise-figure-and-friis.md)
- [10-comms-modulation/ber-ebn0-and-shannon](../10-comms-modulation/ber-ebn0-and-shannon.md), [channel-coding-fec](../10-comms-modulation/channel-coding-fec.md)
- W1-A5 research log contradiction C1 (EBYTE sensitivity) — `research-logs/W1-A5-noise-propagation.md`

## Added by W5-E6 (2026-10-03) — choosing-and-judging-lora-antennas (CJA) and the MQTT misconception (link-budget, LoRaWAN pages)
- **[Meshtastic-ant]** Meshtastic docs, "LoRa antenna selection" (50 Ω SMA; RP-SMA not interchangeable; quarter-wave stubbies need ground planes; cable loss) and "Antenna testing" (VSWR < 2 at the tuned frequency, > 0 dBi; avoid sellers without a stated tuned frequency or with huge omni gain claims; a VNA shows match, not radiation). https://meshtastic.org/docs/hardware/antennas/ (project docs; fetched 2026-10-02) — CJA
- **[Meshtastic-start]** Meshtastic docs, "Getting started" — never power a radio without an antenna. (project docs; search summary) — CJA
- **[Meshtastic-proto]** Meshtastic protobufs: `mesh.proto` (`MeshPacket.via_mqtt`, `NodeInfo.via_mqtt`), `config.proto` (`LoRaConfig.ignore_mqtt`, `config_ok_to_mqtt`). https://github.com/meshtastic/protobufs (project source; read 2026-10-02) — link-budget and LoRaWAN pages (MQTT "range record" misconception), CJA
- **[Meshtastic-MQTT]** Meshtastic docs, "MQTT" — gateways uplink/downlink raw mesh packets to a broker; public broker. https://meshtastic.org/docs/software/integrations/mqtt/ (project docs; fetched 2026-10-02)
- **[Balanis-arr]** C. A. Balanis, *Antenna Theory*, 4th ed. (2016), ch. 4 and 6 — dipole pattern × array factor (model in `tools/verify/e6_lora_antennas.py`). (textbook) — CJA
- **[Montgomery]** D. C. Montgomery, G. C. Runger, *Applied Statistics and Probability for Engineers* — two-sample sample size. (textbook; verified by Monte-Carlo) — CJA
- **[D2-ant]** gaps/D2-reddit.md §2 rank 8 and §3a — community demand and myths (r/meshtastic). (internal gap analysis — anecdotal posts) — CJA

## Added by W5-E10 (2026-10-12) — lora-mesh-capacity-and-congestion
- **[Bor16]** M. Bor, U. Roedig, T. Voigt, J. Alonso, "Do LoRa Low-Power Wide-Area Networks Scale?", ACM MSWiM 2016 (accepted PDF read; note 64 vs 120-node internal inconsistency). (peer-reviewed)
- **[Georgiou17]** O. Georgiou, U. Raza, *IEEE WCL* 6(2):162–165, 2017, arXiv:1610.04793. (peer-reviewed)
- **[KT75]** L. Kleinrock, F. Tobagi, *IEEE Trans. Commun.* COM-23(12), 1975 (CSMA); Bertsekas & Gallager, *Data Networks*, 2nd ed. (textbook)
- **[Mesh-docs]** Meshtastic radio-settings, LoRa config, mesh-algo, device roles, position, telemetry docs; firmware `airtime.h/.cpp`, `RadioInterface.h/.cpp` (read 2026-10-03); Meshtasticator; MeshCore FAQ. (project docs / code)
- Verification: `tools/verify/e10_mesh_capacity.py` (ALL PASS).
