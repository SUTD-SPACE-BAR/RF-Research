# 20-projects-recipes — sources

The recipes are built mainly on this KB's own domain pages and their verification scripts (listed per
page in each recipe's "Sources"). External sources consulted directly or relied on through those pages:

## Primary technical sources (datasheets, standards, app notes, papers)
| # | Source | Type | Used in | Notes |
|---|---|---|---|---|
| 1 | Semtech, *SX1261/2 Datasheet* Rev 1.2 (2019) — §4.1.2 per-packet drift rule BW/(3·2^SF), ×16 with LDRO; sensitivity tables; time-on-air | datasheet | telemetry, SDR, checklists (via kb/15 and `rfcalc/lora.py`) | read by W2-B6 from the rendered page |
| 2 | Semtech, *SX1276/77/78/79 Datasheet* Rev 7 (2020) / AN1200.13 — time-on-air formula | datasheet | telemetry (via `rfcalc`) | |
| 3 | EBYTE, *E22-400TXXX Data Sheet*, *E220-900T30D User Manual*; E22-400M33S product page (cdebyte.com, 2026-09-29) | module datasheets | telemetry, parts tables | air-rate mapping not published |
| 4 | Infineon, *BGA524N6 Data Sheet* Rev 3.0 (2014-01-24) — electrical table (IP1dB −16 dBm, IIP3 −9 dBm, IIP3_oob −5 dBm) and feature list (−12 / −4 dBm); read from a distributor PDF mirror 2026-10-02 | datasheet | LNA, GNSS front end | internal inconsistency documented |
| 5 | Infineon, *AN420: BGA524N6 low-power LNA for GNSS (0201)* Rev 1.0 (2015) | app note | LNA | 1.8 V / 1.5 V results |
| 6 | Broadcom/Avago, *ATF-54143 Data Sheet* — S- and noise parameters 3 V/60 mA | datasheet | LNA (via `rfckt_atf54143_data.py`) | |
| 7 | TDK/EPCOS B39431B3710U410 (B3710) SAW, 433.00–434.71 MHz, IL ≤ 2.7 dB; B39871B3744H110 (B3744), 868.3 MHz, 600 kHz, 290 Ω // 1.3 pF | datasheets (distributor summaries) | ground station, filter | search-summary level; confirm on the PDF before ordering |
| 8 | Mini-Circuits LFCN-490+ / LFCN-1000+ data sheets (via kb/18) | datasheets | filter, GNSS front end | power ratings 8.5 / 10 W |
| 9 | Yaesu, G-5500DC instruction manual / product page — 58 s per 360° azimuth, 67 s per 180° elevation | manufacturer | ground station | search-summary level |
| 10 | IMDA, *TS SRD* Issue 1 Rev 3 (2023), *TS UWB* Issue 1 (2016), Exemption Notification First Schedule — via [singapore-imda-rules](../19-regulations-safety/singapore-imda-rules.md) | regulator | all recipes | authoritative for Singapore limits |
| 11 | IREC 2026 DTEG / Student Band Plan Rev D — via [international rules](../19-regulations-safety/international-rules-for-competitions.md) | competition rules | telemetry, checklists | |
| 12 | u-blox, *ZED-F9P Integration Manual* (UBX-18010802), *MAX-M10S Integration Manual* (UBX-20053088) — via [GNSS antennas](../08-antennas/gnss-antennas.md) and [u-blox integration](../21-gnss/gnss-receiver-integration-u-blox.md) | integration manuals | GNSS front end, LNA, patch | |
| 13 | P. C. Sharma, K. C. Gupta, "Analysis and optimized design of single feed circularly polarized microstrip antennas," *IEEE Trans. AP* 31(6), 1983 | peer-reviewed | patch | design rule rederived in the page, paper not read in full |
| 14 | C. A. Balanis, *Antenna Theory* 4th ed. (2016), ch. 14 (patches, CP) — via kb/08 | textbook | patch | |
| 15 | E. D. Kaplan, C. J. Hegarty (eds.), *Understanding GPS/GNSS* 3rd ed. (2017) — effective C/N0 with interference — via kb/21 | textbook | GNSS front end | |
| 16 | J. Tapparel et al., "An open-source LoRa physical layer prototype on GNU Radio," IEEE SPAWC 2020; gr-lora_sdr | peer-reviewed + code | SDR | |
| 17 | SigMF specification v1.2 | standard | SDR | |
| 18 | Texas Instruments IWR6843 / AWR1843 / DCA1000 product information — via [FMCW radar](../11-radar/fmcw-radar.md), [DIY radar](../11-radar/diy-radar-hardware.md) | datasheets | FMCW | |
| 19 | KrakenRF KrakenSDR documentation; Analog Devices CN0566 (Phaser); PySDR "Hands-on with Phaser" — via [DIY arrays](../12-phased-arrays/diy-phased-array-projects.md) | vendor docs / online textbook | phased array | |
| 20 | G. Hoch (DL6WU), long-Yagi design data via DL6WU.BAS (KY4Z/W6NBI/G3SEK) — via [Yagi page](../08-antennas/yagi-uda-and-log-periodic.md) and `ant_yagi.py` | design data | ground station | |
| 21 | T. Liebig, openEMS / CSXCAD v0.37 (EC-FDTD) | software | patch | all full-wave results in the patch recipe |
| 22 | JLCPCB/LCSC parts database snapshot 2026-07-08 (local `jlcpcb-components.sqlite3`) | distributor data | every parts table | prices change; USD qty 1–9 |

## Internal (user-provided)
| # | Source | Used in |
|---|---|---|
| 23 | Space Bar avionics knowledge base (`~/.claude/knowledge/space-bar-avionics/`): fleet capabilities, Avionics B V3.1 and C V1.1 feature summaries, design lessons, engineering ethos, HIL/bench methods | all recipes (requirements, ethos, bring-up practice) |
| 24 | Coordinator / W5-E1 cross-domain findings (2026-10-02): E22 CH 0–6 3f in GPS/GLONASS L2 (since extended to CH 0–9); legal-vs-licensed landed ranges; 866–869 MHz best exempt band for the E220; 77–81 GHz UWB-only rule; consistency audit #3 and #9 | telemetry, GNSS front end, FMCW, checklists |

## Verification scripts written for this domain (`tools/verify/`)
`proj_lora_link.py`, `proj_ground_station.py`, `proj_harmonic_filter.py`, `proj_patch_gnss.py`,
`proj_openems_gnss_patch.py` (openEMS venv), `proj_lna_gnss.py`, `proj_gnss_frontend.py`,
`proj_sdr_receiver.py`, `proj_fmcw.py`, `proj_phased_array.py`, `proj_preflight_rf.py`.
They reuse `tools/rfcalc` and the domain scripts `ant_yagi.py`, `ant_patch.py`, `rfckt_atf54143_data.py`,
`circuits_filter_prototypes.py` (values), `gnss_self_interference.py` (formula), without modifying them.
