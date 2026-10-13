# 21-gnss — bibliography

Reliability tags: (standard) (manufacturer) (peer-reviewed) (conference) (textbook) (government)
(open-source project) (vendor blog — anecdotal) (forum — anecdotal) (internal = user's notes / another KB page).
"Read" = full text consulted (PDFs via pdftotext, or Browser pane); "summary" = abstract/search-result level only.
Page key: SIG = signals-and-codes, RX = receiver-architecture, ROC = on-rockets, INT = u-blox integration,
IFJ = interference, RTK = rtk-ppp, ERR = error-sources-dop, TTFF = ttff, TIM = timing-1pps, SDR = sdr-diy.

## Interface specifications (signals)
| Source | Used for | Pages |
|---|---|---|
| U.S. Space Force, *IS-GPS-200N*, 1 Aug 2022 — C/A and L2C codes, Table 3-Va minimum powers (3 dBi linear antenna), max levels, LNAV structure, fit interval. https://www.navcen.uscg.gov/sites/default/files/pdf/gps/IS-GPS-200N.pdf (standard; read) | signal table, powers, message timing | SIG, TTFF |
| *IS-GPS-705J* (L5), 2022 — Table 3-III powers, 10.23 Mcps codes, NH codes, 100 sps. https://www.navcen.uscg.gov/sites/default/files/pdf/gps/IS-GPS-705J.pdf (standard; read) | L5 row | SIG |
| *IS-GPS-800J* (L1C), 2022 — Table 3.2-1 powers, BOC/TMBOC, 10230-chip codes, overlay, LDPC. https://www.navcen.uscg.gov/sites/default/files/pdf/gps/IS-GPS-800J.pdf (standard; read) | L1C row | SIG |
| European Union, *Galileo OS SIS ICD Issue 2.1*, Nov 2023 — chip/symbol rates, CBOC, AltBOC, Table 12 powers, Table 14 code lengths. https://www.gsc-europa.eu/sites/default/files/sites/all/files/Galileo_OS_SIS_ICD_v2.1.pdf (standard; read) | Galileo rows | SIG |
| CSNO, *BDS-SIS-ICD-B1I-3.0*, 2019 — −163 dBW, 2.046 Mcps, D1/D2, NH20. http://www.beidou.gov.cn/xt/gfxz/201902/P020190227593621142475.pdf (standard; read) | B1I row, D1/D2 | SIG, TTFF |
| CSNO, *BDS-SIS-ICD-B1C-1.0*, 2017 — Table 4-4 powers, BOC/QMBOC, secondary code. http://en.beidou.gov.cn/SYSTEMS/ICD/ (standard; read) | B1C row | SIG |
| Russian Institute of Space Device Engineering, *GLONASS ICD Ed. 5.1*, 2008 — L1 −161 dBW. https://www.unavco.org/help/glossary/docs/ICD_GLONASS_5.1_(2008)_en.pdf (standard; summary) | GLONASS power | SIG |
| ESA Navipedia, "GLONASS Signal Plan", "GLONASS Navigation Message". https://gssc.esa.int/navipedia/ (encyclopedia, ESA; read via WebFetch) | FDMA plan, string/frame structure | SIG, TTFF |

## u-blox documentation
| Source | Used for | Pages |
|---|---|---|
| *ZED-F9P-04B Data sheet* UBX-21044850 R05 (HPG 1.32), 2024. https://content.u-blox.com/sites/default/files/ZED-F9P-04B_DataSheet_UBX-21044850.pdf (manufacturer; read) | limits 4 g/80 km/500 m/s, rates, TTFF, sensitivity, signals, RTCM, interfaces, V_BCKP, NF 9.5 dB, TP 30 ns | all |
| *ZED-F9P Data sheets* UBX-17051259 R02 (2018, -00B HPG 1.00; SparkFun mirror) and R09 (2023, -01B HPG 1.12); UBX-21023276 R04 (2024, -02B HPG 1.13). (manufacturer; read) | per-firmware altitude limit 50 → 80 km | ROC |
| *ZED-F9P Integration manual* UBX-18010802 R16. https://content.u-blox.com/sites/default/files/ZED-F9P_IntegrationManual_UBX-18010802.pdf (manufacturer; read) | RTK config, dynamic models, timing, security, interference, I²C, RESET_N, V_BCKP, checklists | RX, ROC, INT, IFJ, RTK, TIM, TTFF |
| *u-blox F9 HPG 1.32 Interface Description* UBX-22008968 R01, 2022. https://content.u-blox.com/sites/default/files/documents/u-blox-F9-HPG-1.32_InterfaceDescription_UBX-22008968.pdf (manufacturer; read) | UBX frame, NAV-PVT, TIM-TP, MON-RF, CFG-VALSET, key IDs | INT, TIM, IFJ |
| *MAX-M10S Data sheet* UBX-20035208 R08 (SPG 5.10). https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf (manufacturer; read) | limits, rates, TTFF/AssistNow, sensitivity, defaults (9600 baud), NF 1.5 dB, RF_IN 0 dBm, V_BCKP 28 µA | all |
| *MAX-M10S Integration manual* UBX-20053088 R05 (+ rendered Fig. 27). https://content.u-blox.com/sites/default/files/MAX-M10S_IntegrationManual_UBX-20053088.pdf (manufacturer; read) | front-end chain, LNA modes, out-of-band immunity, AssistNow, memory permanence, RESET_N, UART, antenna supervisor, timepulse | INT, IFJ, TTFF, TIM, ROC |
| *u-blox M10 SPG 5.10 Interface Description* UBX-21035062. https://content.u-blox.com/sites/default/files/u-blox-M10-SPG-5.10_InterfaceDescription_UBX-21035062.pdf (manufacturer; read in part) | key IDs identical to F9 | INT |
| *u-blox 8 / M8 Receiver Description* UBX-13003221 R28. https://content.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_UBX-13003221.pdf (manufacturer; read in part) | M8 airborne model limits (50 km, 100 m/s vertical) | ROC |
| u-blox Support Community: "Clarifying the velocity limit of 500 m/sec" (2016, staff answer); "U-blox M10S velocity and altitude operational limits" (2023); "What is your real experience of sending RTCM messages over LORA?" (2026). https://portal.u-blox.com (forum — staff answer = medium, others anecdotal; read via Browser pane) | AND/OR evidence; RTCM ≈ 700–750 B/s | ROC, RTK |

## Rockets, export control, flight evidence
| Source | Used for | Pages |
|---|---|---|
| J. Y. Kim, U.S. Office of Space Commerce, "U.S. Export Controls on GPS/GNSS Equipment," 18 Mar 2022. https://www.space.commerce.gov/wp-content/uploads/2022-03-US-export-controls-GPS-GNSS-equipment.pdf (government; read) | EAR 7A105 (600 m/s, MTCR 11.A.3), USML XII(d), XI(c)(10) | ROC, IFJ, SDR |
| M. Markgraf, O. Montenbruck, F. Hassenpflug, P. Turner, B. Bull, "A Low Cost GPS System for Real-Time Tracking of Sounding Rockets," 15th ESA PAC Symposium, Biarritz, 2001 (NTRS 20010069267). https://archive.org/details/nasa_techdoc_20010069267 (conference; read) | 15–18 g tracking, aiding, oscillator offset, antennas | ROC, RX, SDR |
| B. Braun, M. Markgraf, L. Rheinwald, S. Weiß, M. Hörschgen-Eggers, "First Test of a Multi-Constellation, Multi-Frequency GNSS Receiver on Board a Sounding Rocket," *Eng. Proc.* 126:39, 2026. https://elib.dlr.de/214653/1/engproc-126-00039.pdf (conference, open access; read) | MAPHEUS-15 results, loop settings, jamming above 25 km, roll, data restriction | ROC, IFJ, SIG, SDR |
| BigRedBee, "High Altitude GPS operation," 2018/2023. https://shop.bigredbee.com/blogs/news/high-altitude-gps-operation (vendor blog — anecdotal; read) | AND claim, 50 km cut-off on a 61 km flight | ROC |
| Rocketry Forum threads ("USC and GPS", "GPS g limits?", "Highest Altitude GPS?") (forum — anecdotal; search summaries only, site blocked automated reading) | boost lock-loss reports | ROC |
| Bull et al., "Flight Performance Evaluation of Three GPS Receivers for Sounding Rocket Tracking," 2002 (NTRS 20020060112) (conference; NOT read — HTTP 403) | — | gap |

## Corrections, errors, ionosphere
| Source | Used for | Pages |
|---|---|---|
| T. Takasu, RTKLIB `src/rtcm3e.c`. https://github.com/tomojitakasu/RTKLIB (open-source code; read) | MSM field widths, 1005/1230 sizes | RTK |
| NovAtel, "RTCMV3 standard logs" — 16 SV × 4 signals MSM4 3593 / MSM7 5929 bits. https://docs.novatel.com/OEM7/Content/Logs/RTCMV3_Standard_Logs.htm (manufacturer docs; summary) | size cross-check | RTK |
| RTCM SC-104, *RTCM 10403.3/10403.4* (standard; not read — paywalled; cited via u-blox and RTKLIB) | — | RTK |
| Singapore Land Authority, SiReNT "Our Services" / Customer Handbook. https://app.sla.gov.sg/sirent/About/OurServices (government; summary) | NTRIP RTK in Singapore | RTK |
| SparkFun, GPS-RTK2 hookup guide (vendor tutorial; summary) — claims ≈ 1–2 kB/s RTCM (appears high) | contradiction note | RTK (log) |
| O. Montenbruck, P. Steigenberger, A. Hauschild, "Multi-GNSS signal-in-space range error assessment," *Adv. Space Res.* 61(12):3020–3038, 2018 (peer-reviewed; abstract summary) | SISRE | ERR |
| "Signal-in-space range error and positioning accuracy of BDS-3," *Sci. Rep.* 12, 2022 (peer-reviewed; summary) | BDS-3 SISRE | ERR |
| S. Andoh et al., "Ionospheric scintillations associated with equatorial plasma bubbles in Southeast Asia during the ascending and maximum phases of Solar Cycle 25," *Earth Planets Space* 78:199, 2026. https://link.springer.com/article/10.1186/s40623-026-02527-3 (peer-reviewed, open access; read in part) | SE-Asian scintillation morphology, dip-equator stations | ERR |
| ITU-R P.531 (via [09 ionosphere page](../09-propagation-link-budget/ionospheric-hf-propagation.md)) (standard; internal) | TEC, S4 | ERR |
| J. Saastamoinen, AGU Geophys. Monogr. 15, 1972 (formulas as reproduced in textbooks; cross-checked numerically) | troposphere | ERR |

## SDR and DIY
| Source | Used for | Pages |
|---|---|---|
| T. Takasu, *Pocket SDR* ver. 0.20 README and repository. https://github.com/tomojitakasu/PocketSDR (open-source project; read) | MAX2771 FE, channels, bands, rates, signals | SDR |
| GNSS-SDR README. https://github.com/gnss-sdr/gnss-sdr (open-source project; read in part) | signals, GPL-3.0, front ends | SDR |
| T. Ebinuma, *gps-sdr-sim* README. https://github.com/osqzss/gps-sdr-sim (open-source project; read) | simulator, cabled test set-up | SDR, IFJ |
| EBYTE, *E22-400T33D/S User Manual* v1.5 (distributor mirror). https://robu.in/wp-content/uploads/2024/07/E22-400T33X_UserManual_EN_v1.5-1.pdf (manufacturer; read) | channel raster, no harmonic spec | IFJ |
| EBYTE E22-400T30D-V2 product page (vendor; summary) — spurious ≤ −60 dBc | harmonic assumption | IFJ |

## Textbooks (general references, not re-read in this pass)
- E. D. Kaplan, C. J. Hegarty (eds.), *Understanding GPS/GNSS: Principles and Applications*, 3rd ed., Artech House, 2017 — acquisition/tracking formulas (ch. 8), interference (ch. 9), errors and DOP. (textbook) — RX, ROC, IFJ, ERR, TIM, TTFF
- P. Misra, P. Enge, *Global Positioning System: Signals, Measurements, and Performance*, 2nd ed., 2006. (textbook) — SIG, RX, ERR, RTK
- P. J. G. Teunissen, O. Montenbruck (eds.), *Springer Handbook of Global Navigation Satellite Systems*, 2017. (textbook) — RX, RTK, ERR
- K. Borre, D. M. Akos, N. Bertelsen, P. Rinder, S. H. Jensen, *A Software-Defined GPS and Galileo Receiver*, Birkhäuser, 2007. (textbook) — RX, SDR
- D. W. Allan, N. Ashby, C. C. Hodge, *The Science of Timekeeping*, HP AN 1289, 1997. (app note) — TIM

## Internal
- Space Bar avionics knowledge base (`~/.claude/knowledge/space-bar-avionics/`): Avionics B (ZED-F9P, L1-only antenna, LoRa RTK bridge, E22-400T33D, Teensy 4.1 + ESP32-S3), Avionics C (MAX-M10S, U.FL+ESD, timepulse, buffered UART, E220-900T30D), I²C 100 kHz lesson, GPS recovery-ladder lesson, inter-processor clock steps. (internal)
- KB pages linked throughout: 08 gnss-antennas, 09 ionospheric-hf-propagation, 10 spread-spectrum, 14 SDR pages, 15 LoRa pages (`lora_toa.py`), 18 parts pages, 19 regulations. (internal)
