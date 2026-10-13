# 09-propagation-link-budget — Sources

Consolidated bibliography for the propagation and link-budget domain. Reliability tags per CONVENTIONS §3. "Used in" lists the pages that cite each item. Items marked *cited, not re-read* were used from standard textbook knowledge or secondary descriptions; their formulas were independently checked where possible.

## Textbooks
| # | Citation | Used for | Used in |
|---|---|---|---|
| T1 | T. S. Rappaport, *Wireless Communications: Principles and Practice*, 2nd ed., Prentice Hall, 2002 — ch. 4 (Friis, two-ray, diffraction, log-distance, Okumura/Hata/COST-231, exponents Table 4.2), ch. 5 (small-scale fading, delay spread, coherence, Clarke, LCR/AFD). (textbook) | two-ray, knife-edge, empirical models, fading | friis, link budget, two-ray, empirical, multipath, margin, diffraction, fresnel |
| T2 | A. Goldsmith, *Wireless Communications*, Cambridge UP, 2005 — ch. 2 (path loss, two-ray critical distance, shadowing), ch. 3 (statistical multipath), ch. 7 (diversity). (textbook) | two-ray, outage, diversity | two-ray, multipath, margin |
| T3 | J. D. Parsons, *The Mobile Radio Propagation Channel*, 2nd ed., Wiley, 2000. (textbook) | plane earth, roughness, fading, delay spreads, Egli discussion | two-ray, multipath |
| T4 | S. R. Saunders, A. Aragón-Zavala, *Antennas and Propagation for Wireless Communication Systems*, 2nd ed., Wiley, 2007. (textbook) | Fresnel/clearance, diffraction methods comparison, ionosphere | fresnel, diffraction, ionosphere |
| T5 | J. S. Seybold, *Introduction to RF Propagation*, Wiley, 2005. (textbook) | Fresnel, k-factor, atmosphere/rain, foliage, ionosphere | fresnel, atmospheric, ionosphere |
| T6 | C. A. Balanis, *Antenna Theory*, 4th ed., Wiley, 2016 — §2.12 polarisation/PLF, §2.14–2.18 aperture, Friis, radar equation. (textbook) | Friis, aperture, PLF | friis, polarisation |
| T7 | T. A. Milligan, *Modern Antenna Design*, 2nd ed., Wiley-IEEE, 2005 — ch. 1 (polarisation mismatch, AR formula). (textbook) | AR mismatch formula | polarisation |
| T8 | W. L. Stutzman, *Polarization in Electromagnetic Systems*, 2nd ed., Artech House, 2018. (textbook) | Poincaré sphere | polarisation |
| T9 | J. D. Kraus, R. J. Marhefka, *Antennas for All Applications*, 3rd ed., McGraw-Hill, 2002. (textbook) | aperture–directivity from thermodynamics | friis |
| T10 | D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — §14.2. (textbook) | Friis, EIRP | friis |
| T11 | B. Sklar, *Digital Communications*, 2nd ed., Prentice Hall, 2001 — ch. 5 (link analysis), ch. 15 (fading). (textbook) | G/T, C/N0, margin | link budget, margin |
| T12 | K. Davies, *Ionospheric Radio*, Peter Peregrinus/IEE, 1990. (textbook) *cited, not re-read* | layers, secant law, MUF, absorption | ionosphere |
| T13 | P. Misra, P. Enge, *Global Positioning System*, 2nd ed., Ganga-Jamuna, 2006 — ch. 5. (textbook) | 40.3 TEC/f², iono-free combination | ionosphere |
| T14 | L. F. McNamara, *Radio Amateur's Guide to the Ionosphere*, Krieger, 1994. (textbook) *cited, not re-read* | MUF/LUF/FOT practice, SID, storms, grey line, NVIS | space weather, HF modes |
| T15 | M. P. M. Hall, *Effects of the Troposphere on Radio Communication*, Peter Peregrinus, 1979; M. P. M. Hall, L. W. Barclay, M. T. Hewitt (eds.), *Propagation of Radiowaves*, IEE, 1996. (textbooks) *cited, not re-read* | refractivity, ducts, trapping | anomalous |
| T16 | J. R. Wait, *Electromagnetic Waves in Stratified Media*, Pergamon 1962 / IEEE Press 1996. (textbook) *cited via LFMF* | ground-wave residue series | ground wave |
| T17 | ARRL, *The ARRL Handbook* (2010 ch. 30, J. Taylor K1JT, "EME", https://wsjt.sourceforge.io/Hbk_2010_Ch30_EME.pdf) and *ARRL Antenna Book* propagation chapters. (handbook) | EME loss table, libration, Doppler, Faraday; VHF/HF operating practice | anomalous, HF modes, ground wave |

## Peer-reviewed papers and reports
| # | Citation | Used for | Used in |
|---|---|---|---|
| P1 | H. T. Friis, "A note on a simple transmission formula," *Proc. IRE* 34(5), 254–256 (1946). | transmission formula | friis, link budget |
| P2 | K. Bullington, "Radio propagation at frequencies above 30 megacycles," *Proc. IRE* 35(10), 1122–1136 (1947). | equivalent knife edge | diffraction |
| P3 | K. Bullington, "Radio propagation fundamentals," *Bell Syst. Tech. J.* 36(3), 593–626 (1957), https://archive.org/details/bstj36-3-593 | plane earth, surface wave, minimum effective height chart | two-ray |
| P4 | J. Epstein, D. W. Peterson, "An experimental study of wave propagation at 850 Mc," *Proc. IRE* 41(5), 595–611 (1953). | multiple-edge method | diffraction |
| P5 | J. Deygout, "Multiple knife-edge diffraction of microwaves," *IEEE Trans. AP* 14(4), 480–489 (1966). | Deygout method | diffraction |
| P6 | W. S. Ament, "Toward a theory of reflection by a rough surface," *Proc. IRE* 41(1), 142–146 (1953). | roughness factor | two-ray |
| P7 | J. J. Egli, "Radio propagation above 40 MC over irregular terrain," *Proc. IRE* 45(10), 1383–1391 (1957) (ratio form via Wikipedia "Egli model"). | Egli model | empirical |
| P8 | M. Hata, "Empirical formula for propagation loss in land mobile radio services," *IEEE Trans. Veh. Technol.* 29(3), 317–325 (1980); Y. Okumura et al., *Rev. ECL* 16, 825–873 (1968). *cited via textbooks* | Okumura–Hata | empirical |
| P9 | R. H. Clarke, "A statistical theory of mobile-radio reception," *BSTJ* 47(6), 957–1000 (1968). | Clarke model | multipath |
| P10 | S. O. Rice, "Mathematical analysis of random noise," *BSTJ* 23–24 (1944–45). | Rician distribution | multipath |
| P11 | H. Suzuki, "A statistical model for urban radio propagation," *IEEE Trans. Commun.* 25(7), 673–680 (1977). | composite fading | margin |
| P12 | E. N. Gilbert, *BSTJ* 39, 1253–1265 (1960); E. O. Elliott, *BSTJ* 42, 1977–1997 (1963). | burst channel | margin |
| P13 | Y. A. Doroshkin et al., "Experimental study of LoRa modulation immunity to Doppler effect in CubeSat radio communications," *IEEE Access* 7, 75721–75731 (2019). (abstract only) | LoRa static Doppler immunity | multipath |
| P14 | É. Dieudonné, A. Kameni, L. Pichon, D. Monchaux, "Radio frequency attenuation by a rocket plume using diffraction theory and finite element modeling," 7th EUCASS, 2017, doi:10.13009/EUCASS2017-21, https://www.eucass.eu/doi/EUCASS2017-021.pdf (conference paper) | plume attenuation vs look angle (M-V stage, 300 MHz in-flight data by Kinefuchi et al.) | link budget |
| P15 | A. G. Longley, P. L. Rice, ESSA Tech. Rep. ERL 79-ITS 67 (1968). (technical report) | ITM | empirical |
| P16 | M. A. Weissberger, ECAC-TR-81-101 (1982). (technical report) *cited via secondary sources* | foliage model | atmospheric |
| P17 | COST Action 231 final report (1999), ch. 4. (technical report) | COST-231 Hata | empirical |
| P18 | K. A. Norton, *Proc. IRE* 24(10), 1367–1387 (1936) and 25(9), 1203–1236 (1937); A. Sommerfeld, *Ann. Phys.* 28, 665 (1909); G. Millington, *Proc. IEE* 96(III), 53–64 (1949). *cited from standard knowledge* | surface wave, mixed paths | ground wave |
| P19 | R. W. Heron, L. F. McNamara, "Transequatorial VHF propagation through equatorial plasma bubbles," *Radio Science* (1979). *cited via S25* | eTEP mechanism | anomalous |
| P20 | J. D. Turton, D. A. Bennetts, S. F. G. Farmer, "An introduction to radio ducting," *Meteorological Magazine* 117, 245–254 (1988). *cited from standard knowledge; λ_max coefficient re-derived* | trapped wavelength | anomalous |
| P21 | "Improved method of estimating temperatures at meteor peak heights," *Atmos. Meas. Tech.* 14, 4157 (2021), https://amt.copernicus.org/articles/14/4157/2021/ | underdense decay exp(−16π²Dt/λ²) | anomalous |
| P22 | "The May 2024 geomagnetic storm: UK experience and perspective," *R. Soc. Open Sci.* 13, 251943 (2026), doi:10.1098/rsos.251943 (*via search summary*) | Dst −412 nT, GNSS errors to 60 m | space weather |
| P23 | D. S. Murti, *GNSS ionospheric scintillation studies in Singapore*, M.Eng. thesis, NTU, 2015, https://dr.ntu.edu.sg/handle/10356/65415 (thesis, PDF read) | Singapore S4 occurrence statistics 2012–2014 | space weather |

## Standards (ITU-R, NTIA, IEEE, GPS)
| # | Citation | Used for | Used in |
|---|---|---|---|
| S1 | ITU-R P.372-13 (09/2016) *Radio noise*. | antenna/sky noise in budgets | link budget |
| S2 | ITU-R P.525-5 (11/2024) *Calculation of free-space attenuation*. | FSPL constant 32.4 | friis, link budget |
| S3 | ITU-R P.526-14 (01/2018) *Propagation by diffraction*. | Fresnel zones, 60 % rule, J(v), rounded obstacles, Bullington/multiple edges | fresnel, diffraction |
| S4 | ITU-R P.527-6 (09/2021) *Electrical characteristics of the surface of the Earth* (legacy P.527-3 categories in Attachment). | ground constants | two-ray |
| S5 | ITU-R P.528-4 (08/2019) aeronautical propagation, 125 MHz–15.5 GHz. | air-to-ground model scope | empirical, two-ray |
| S6 | ITU-R P.531-13 (09/2016) ionospheric effects on Earth–space paths. | TEC, Faraday, delay, scintillation, Table 3 | ionosphere, polarisation |
| S7 | ITU-R P.676-11 (09/2016) *Attenuation by atmospheric gases*, Annex 1. | line-by-line gas model (implemented) | atmospheric, link budget |
| S8 | ITU-R P.833-9 (09/2016) *Attenuation in vegetation*. | woodland model and Table 1 | atmospheric |
| S9 | ITU-R P.838-3 (03/2005) *Specific attenuation model for rain*. | k, α regression (implemented) | atmospheric |
| S10 | ITU-R P.840-8 (08/2019) *Attenuation due to clouds and fog*. | Kl double-Debye (implemented) | atmospheric |
| S11 | ITU-R P.1546-6 (08/2019) point-to-area 30–4000 MHz. | scope | empirical |
| S12 | ITU-R P.1812-7/-8 (2023/2025) path-specific 30 MHz–6 GHz. | scope | empirical |
| S13 | ITU-R P.1411, P.452, P.453, P.530, P.533, P.1239, P.2108 (current revisions). *scope only* | model scopes, refractivity, fixed-link availability, HF | empirical, fresnel, margin, ionosphere |
| S14 | ITU-R P.2109-2 (08/2023) *Prediction of building entry loss*. | building entry loss (implemented) | atmospheric |
| S15 | NTIA/ITS *Irregular Terrain Model (ITM)*, https://its.ntia.gov/software/itm/, https://github.com/NTIA/itm | ITM scope | empirical |
| S16 | IEEE Std 145-2013 antenna terms. | polarisation handedness, AR | polarisation |
| S17 | IS-GPS-200 GPS interface specification. | GNSS frequencies, Klobuchar | ionosphere |
| S18 | ITU-R P.533-14 (08/2019) *Method for the prediction of the performance of HF circuits* (PDF read). | control points, basic MUF eqs 1–6, elevation eq. 13, field strength 17–28, absorption form, LUF, equatorial scatter | HF modes, space weather |
| S19 | ITU-R P.1239-3 (02/2012) and P.1239-4 (08/2023) *ITU-R reference ionospheric characteristics*; coefficient data COEFF01W–12W (ITU-R SG3, github.com/ITU-R-Study-Group-3/ITU-R-HF). | foF2/M(3000)F2/foEs maps (implemented), foE formula | HF modes, space weather, anomalous |
| S20 | ITU-R P.368-10 (08/2022) *Ground-wave propagation prediction method for frequencies between 10 kHz and 30 MHz*; P.368-7 (1992). | ground-wave method, Millington, conditions | ground wave |
| S21 | ITU-R P.534-6 (09/2021) *Method for calculating sporadic-E field strength*. | Es field strength, Phillips rule, statistics | anomalous |
| S22 | ITU-R P.453-14 (08/2019) *The radio refractive index* (PDF read: N formula, gradients, M-units, ducts). | refractivity, ducting | anomalous, fresnel |
| S23 | ITU-R P.527-6 (09/2021), P.832-4 (07/2015) ground electrical characteristics / conductivity atlas. | ground constants | ground wave |
| S24 | NOAA SWPC documentation: NOAA Space Weather Scales; D-RAP documentation; Planetary K-index; Station K and A indices; phenomena pages (CME, coronal holes, solar wind, flares, scintillation, TEC); JSON data services. https://www.swpc.noaa.gov/ | scales, HAF, PCA, K/A, CME timing | space weather |
| S25 | Australian Bureau of Meteorology Space Weather Services, *Transequatorial Radio Propagation*. https://www.sws.bom.gov.au/Educational/5/2/3 | aTEP/eTEP characteristics | anomalous, space weather |
| S26 | IAGA IGRF-14 coefficients (igrf14coeffs.txt, NOAA NGDC). | dip, dip latitude, modip, gyrofrequency | all W5-E4 pages |

## Datasheets, lecture notes and community sources
| # | Citation | Used for | Used in |
|---|---|---|---|
| D1 | Semtech, *SX1261/2 Data Sheet* Rev 1.2 (2019) and Rev 2.2 (2024). | sensitivity, frequency-offset tolerance, Freq_drift_max = BW/(3·2^SF), ToA | link budget, multipath |
| D2 | Chengdu Ebyte, E22-400TXXX data sheet (2022); E220-900T30D user manual. | Tx power, bands (sensitivity claim rejected) | link budget |
| L1 | G. L. Stüber, EE6604 Week 7 lecture notes, Georgia Tech (2019). (lecture notes) | Hata/COST-231 forms, validity (with noted discrepancies) | empirical |
| C1 | The Things Network articles on 702 km (2017) and 832 km (2020) LoRaWAN balloon records. (news — anecdotal) | free-space sanity check | friis |
| C2 | Meshtastic "Range tests" documentation. (community — anecdotal) | ground vs elevated ranges | fresnel, empirical |
| D3 | SILSO (Royal Observatory of Belgium) sunspot number V2.0 files; NOAA SWPC solar-cycle JSON (fetched 2026-10-02). (data) | SC24/SC25 extrema, 2026 status, F10.7 | space weather |
| D4 | ITU-R SG3 *ITURHFProp* (P.533 v14.2 / P.372 v14.3) example outputs and C source. https://github.com/ITU-R-Study-Group-3/ITU-R-HF (reference software) | validation of foF2/M3000/foE/basic MUF; P.372 Fam constants; absorption implementation | HF modes |
| D5 | NTIA/ITS *LFMF* (C++) and *LFMF-test-data*. https://github.com/NTIA/LFMF (reference software) | ground-wave algorithm and 5 reference cases | ground wave |
| D6 | WSJT-X User Guide (K1JT et al.) — WSPR/FT8/MSK144/Q65 parameters; Reverse Beacon Network; PSKReporter; VOACAP. (software documentation) | real-time propagation reporting and prediction tools | HF modes, anomalous |

| S17-1 | D. A. Vallado, *Fundamentals of Astrodynamics and Applications*, 4th ed. (2013); Vallado, Crawford, Hujsak, Kelso, "Revisiting Spacetrack Report #3", AIAA 2006-6753. (textbook / peer-reviewed) | two-body, J2, SSO, look angles; SGP4/SDP4 and TLEs | satellite links |
| S17-2 | WMO OSCAR/Space "Meteor-M N2-3" (2025-06-09); sigidwiki "LRPT". (agency database / community wiki) | Meteor-M orbit and LRPT parameters (no EIRP) | satellite links |
| S17-3 | Gpredict AppStream metadata; hamlib rigctld(1)/rotctld(1) man pages. (software documentation) | SGP4/SDP4, Doppler tuning, ports 4532/4533, -x uplink | satellite links |

## Verification scripts (this KB)
| Script | Verifies |
|---|---|
| `tools/verify/prop_fspl.py` | FSPL constants and table, aperture argument, flux/field (incl. 44.77 constant check), ERP, far field, balloon record |
| `tools/verify/prop_link_budget.py` | `Link` class; 433/915 MHz examples; range tables; G/T–C/N0 cross-check; landed pointer |
| `tools/verify/prop_fresnel_horizon.py` | Fresnel exact vs paraxial vs ITU; horizons; bulge; clearance heights; descent altitudes; elevation angles |
| `tools/verify/prop_two_ray.py` | two-ray (H/V, lossy ground), 40 dB/dec, Brewster, min effective height, lobing nulls/rate/depth, landed and pad cases, Ament roughness |
| `tools/verify/prop_knife_edge.py` | exact vs approximate J(v), v forms, Deygout/Epstein–Peterson/Bullington |
| `tools/verify/prop_empirical.py` | Hata/COST-231/Egli/log-distance with validity flags; Egli constant check |
| `tools/verify/prop_doppler_fading.py` | Doppler/Doppler-rate vs LoRa limits, Rayleigh/Rician outage (analytic + MC), LCR/AFD, coherence, diversity |
| `tools/verify/prop_margin.py` | lognormal/Suzuki margins (median-referenced), RSS vs linear, Gilbert–Elliott repetition, toy flight |
| `tools/verify/prop_atmospheric.py` | P.676-11 line-by-line, P.838-3, P.840, P.833/Weissberger, P.2109-2 |
| `tools/verify/prop_ionosphere.py` | plasma frequency, MUF/skip/hop geometry, GNSS delay, iono-free, Faraday, S4 scaling |
| `tools/verify/prop_polarization.py` | Jones vs AR formula, special cases, rocket attitude geometry |
| `tools/verify/prop2_igrf.py` | own IGRF-14 synthesis; dip/dip latitude/modip/fH; validated at Boulder, Kototabang, Chumphon, Trivandrum, Jicamarca |
| `tools/verify/prop2_space_weather.py` | SC25 data, F10.7–SSN relation, flare classes/HAF, absorption theory, K→A, CME/flare timing, PCA, P.1239 foE, GNSS TEC, P.533 scatter factors |
| `tools/verify/prop2_ccir.py` | P.1239 foF2/M(3000)F2/foEs maps and P.533 basic MUF, validated against ITURHFProp (≤ 0.07 MHz foF2; 27.98 vs 27.77 MHz MUF) |
| `tools/verify/prop2_hf_paths.py` | hop limits, Singapore→Perth/Darwin/Sydney MUF tables, absorption, rough P.533 SNR, skip, NVIS, grey line, o/x split, P.372 Fam |
| `tools/verify/prop2_vhf_anomalous.py` | refractivity, −157 N/km, λ_max WKB, ducted LoRa, Es (P.534, foEs maps), meteor, aircraft scatter, EME table, TEP geometry |
| `tools/verify/prop2_ground_wave.py` | LFMF re-implementation (5/5 reference cases), field-strength tables, Norton p, V vs H, coverage, Millington |
| `tools/verify/s17_satellite_pass.py` | orbit classes, slant range/footprint, Singapore pass simulation (two-body + J2), Doppler/Doppler rate with analytic R̈ vs finite differences, keyhole, transponder Doppler, 437 MHz/LoRa/LRPT budgets, GEO elevations |
| `tools/verify/s17_doppler_rate_los.py` | range acceleration a·r̂ + v⊥²/R (symbolic + rocket trajectory), per-packet LoRa drift from stations near the pad |
