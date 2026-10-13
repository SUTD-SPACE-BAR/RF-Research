# 11-radar — Sources

Consolidated bibliography for the radar domain. Reliability tags per CONVENTIONS §3. "Used in" lists the pages that cite each item (abbreviations: RRE range equation, RCS, DET detection/CFAR, PUL pulsed/pulse compression, AMB ambiguity, CW CW/Doppler, FMCW, MIMO, CLU clutter/MTI, SAR, DIY hardware). Items marked *cited, not re-read* were not retrievable during the 2026-09-27/29 sessions; the facts used from them were re-derived and numerically verified in `tools/verify/radar_*.py` or are marked as approximate on the page. Items marked *abstract/snippet* were read only as abstracts or search summaries.

## Textbooks
| # | Citation | Used for | Used in |
|---|---|---|---|
| T1 | M. I. Skolnik, *Introduction to Radar Systems*, 3rd ed., McGraw-Hill, 2001 — ch. 1 introduction, ch. 2 radar equation (incl. Pd/Pfa, integration, RCS and fluctuations), ch. 3 MTI and pulse Doppler, ch. 4 tracking, ch. 5 detection of signals in noise, ch. 6 information from radar signals (accuracy, ambiguity, pulse compression), ch. 7 clutter, ch. 10 transmitters; RCS table (section number not verified). (textbook) *cited, not re-read*. **Chapter map checked by W5-S18 (2026-10-13)** against gaps/D4-curriculum.md §3.19 (chapters 1–11, medium confidence) and a catalogue ToC via search (ch. 3 = §3.1 Doppler/MTI intro, §3.2 delay-line cancelers, §3.3 staggered PRFs …). The earlier entry's "CW/FM-CW in ch. 1–3" and "ch. 14 (SAR)" do not match that map: CW/FM-CW as a chapter (ch. 3) is the 2nd-edition layout, as recalled, and no ch. 14 appears in the 3rd-ed. chapter list. The 3rd-ed. location of the CW/FM-CW and SAR material is unverified. | radar equation forms, Swerling, MTI improvement factors, staggered PRF, constant-γ clutter, typical RCS values (approximate) | RRE, RCS, DET, PUL, CW, CLU, SAR, AMB |
| T2 | M. A. Richards, *Fundamentals of Radar Signal Processing*, 2nd ed., McGraw-Hill, 2014 — ch. 2 (RCS statistics), 4 (waveforms, matched filter, LFM), 5 (sampling), 6 (detection, CFAR), 7 (measurements/CRLB), 8 (SAR). (textbook) *cited, not re-read* | detection theory, Albersheim validity, stretch processing/RVP, straddle loss, backprojection | DET, PUL, AMB, FMCW, RCS, SAR |
| T3 | M. A. Richards, J. A. Scheer, W. A. Holm (eds.), *Principles of Modern Radar, Vol. I: Basic Principles*, SciTech, 2010 — ch. 2, 5, 15, 16, 17, 20. (textbook) *cited, not re-read* | loss budgets, clutter characteristics, threshold detection, CFAR, binary integration, Doppler processing, pulse-compression waveforms | RRE, DET, PUL, CLU |
| T4 | N. Levanon, E. Mozeson, *Radar Signals*, Wiley-IEEE Press, 2004. (textbook) *cited, not re-read* | AF definition/convention, LFM/NLFM, Barker, Frank, P3/P4, Costas, pulse trains | PUL, AMB |
| T5 | B. R. Mahafza, *Radar Systems Analysis and Design Using MATLAB*, 3rd ed., CRC, 2013 — ch. 2. (textbook) *cited, not re-read* | radar-equation forms (search, bistatic) | RRE |
| T6 | E. F. Knott, J. F. Shaeffer, M. T. Tuley, *Radar Cross Section*, 2nd ed., Artech House, 1993/SciTech 2004. (textbook) *cited, not re-read* | PO integral, canonical shapes, corner reflectors, RAM, measurement | RCS |
| T7 | C. F. Bohren, D. R. Huffman, *Absorption and Scattering of Light by Small Particles*, Wiley, 1983, ch. 4. (textbook) | Mie coefficients (implemented) | RCS, CLU |
| T8 | C. A. Balanis, *Advanced Engineering Electromagnetics*, 2nd ed., Wiley, 2012, ch. 11–13. (textbook) *cited, not re-read* | sphere/cylinder scattering, PO, GTD | RCS |
| T9 | G. W. Stimson, *Introduction to Airborne Radar*, 2nd ed., SciTech, 1998. (textbook) *cited, not re-read* | low/medium/high PRF, ambiguity resolution | PUL |
| T10 | L. V. Blake, *Radar Range-Performance Analysis*, Munro, 1986. (textbook) *cited, not re-read* | beam-shape loss 1.6 dB, noise-temperature bookkeeping (beam-shape value reproduced numerically: 1.67 dB) | RRE |
| T11 | P. M. Woodward, *Probability and Information Theory, with Applications to Radar*, Pergamon, 1953. (textbook) *cited, not re-read* | ambiguity function, volume invariance (verified numerically) | AMB |
| T12 | P. Z. Peebles Jr., *Radar Principles*, Wiley, 1998. (textbook) via [P2] | non-coherent integration-gain formula | DET |
| T13 | H. D. Griffiths, C. J. Baker, *An Introduction to Passive Radar*, Artech House, 2017. (textbook) *cited, not re-read* | bistatic geometry, CAF, direct-path cancellation, broadcast-signal ambiguity | RRE, AMB, DIY |
| T14 | V. C. Chen, *The Micro-Doppler Effect in Radar*, Artech House, 2011. (textbook) *cited, not re-read* | rotor/human/bird micro-Doppler | CW |
| T15 | G. L. Charvat, *Small and Short-Range Radar Systems*, CRC, 2014. (textbook) *cited, not re-read* | hobby-scale CW/FMCW design lineage | CW |
| T16 | M. Soumekh, *Synthetic Aperture Radar Signal Processing with MATLAB Algorithms*, Wiley, 1999. (textbook) *cited, not re-read* | SAR phase history, ω-k algorithm | SAR |
| T17 | I. G. Cumming, F. H. Wong, *Digital Processing of Synthetic Aperture Radar Data*, Artech House, 2005. (textbook) *cited, not re-read* | RDA, RCMC, stripmap D/2 | SAR |
| T18 | R. J. Doviak, D. S. Zrnić, *Doppler Radar and Weather Observations*, 2nd ed., Academic, 1993. (textbook) *cited, not re-read* | η = π⁵|K|²Z/λ⁴, Gaussian-beam resolution volume | CLU |
| T19 | J. B. Billingsley, *Low-Angle Radar Land Clutter*, SciTech, 2002. (textbook) *cited, not re-read* | exponential windblown clutter spectra (qualitative) | CLU |
| T20 | J. R. Guerci, *Space-Time Adaptive Processing for Radar*, 2nd ed., Artech House, 2014; J. Ward, MIT LL TR-1015 (1994). (textbook/report) *cited, not re-read* | STAP, clutter ridge | CLU |
| T21 | J. Li, P. Stoica (eds.), *MIMO Radar Signal Processing*, Wiley, 2009. (textbook) *cited, not re-read* | MIMO virtual aperture theory | MIMO |

## Peer-reviewed papers and standards
| # | Citation | Used for | Used in |
|---|---|---|---|
| P1 | W. J. Albersheim, "A closed-form approximation to Robertson's detection characteristics," *Proc. IEEE* 69(7), 839 (1981). (peer-reviewed) *via [P2], MATLAB doc* | Albersheim equation (verified ≤ 0.3 dB) | DET |
| P2 | M. A. Richards, "Noncoherent Integration Gain, and its Approximation," Georgia Tech memo, 9 June 2010. https://bpb-us-e1.wpmucdn.com/sites.gatech.edu/dist/5/462/files/2016/12/Noncoherent-Integration-Gain-Approximations.pdf (lecture notes) | Gc = N, Gnc = N^α, exact Marcum form, α values | DET |
| P3 | D. A. Shnidman, "Determination of required SNR values," *IEEE Trans. AES* 38(3), 1059–1064 (2002). (peer-reviewed) *coefficients via search snippets; verified numerically* | Shnidman equation (verified ≤ 0.82 dB) | DET |
| P4 | D. W. Tufts, A. J. Cann, "On Albersheim's detection equation," *IEEE Trans. AES* 19(4), 643–646 (1983). (peer-reviewed) *cited, not re-read* | Albersheim accuracy | DET |
| P5 | P. Swerling, "Probability of detection for fluctuating targets," *IRE Trans. IT* 6(2), 269–308 (1960). (peer-reviewed) *cited, not re-read* | Swerling models | DET, RCS |
| P6 | J. I. Marcum, "A statistical theory of target detection by pulsed radar," *IRE Trans. IT* 6(2), 59–267 (1960). (peer-reviewed) *cited, not re-read* | Marcum Q, non-coherent detection | DET |
| P7 | H. Rohling, "Radar CFAR thresholding in clutter and multiple target situations," *IEEE Trans. AES* 19(4), 608–621 (1983). (peer-reviewed) *cited, not re-read; formula verified* | OS-CFAR | DET |
| P8 | V. G. Hansen, J. H. Sawyers, "Detectability loss due to 'greatest of' selection in a cell-averaging CFAR," *IEEE Trans. AES* 16(1), 115–118 (1980). (peer-reviewed) *cited, not re-read; formulas verified* | GO/SO-CFAR Pfa | DET |
| P9 | H. M. Finn, R. S. Johnson, "Adaptive detection mode with threshold control…," *RCA Review* 29, 414–464 (1968). (peer-reviewed) *cited, not re-read* | CA-CFAR origin | DET |
| P10 | G. V. Trunk, "Range resolution of targets using automatic detectors," *IEEE Trans. AES* 14(5), 750–755 (1978). (peer-reviewed) *cited, not re-read* | SO-CFAR | DET |
| P11 | J. Neyman, E. S. Pearson, *Phil. Trans. R. Soc. A* 231, 289–337 (1933). (peer-reviewed) | Neyman–Pearson lemma | DET |
| P12 | G. H. Robertson, "Operating characteristics for a linear detector of CW signals in narrow-band Gaussian noise," *BSTJ* 46(4), 755–774 (1967). (peer-reviewed) *cited, not re-read* | Robertson curves | DET |
| P13 | F. J. Harris, "On the use of windows for harmonic analysis with the DFT," *Proc. IEEE* 66(1), 51–83 (1978). (peer-reviewed) *table reproduced numerically* | ENBW, processing and scalloping losses (Hamming scalloping 1.78 dB in paper vs 1.75 dB computed for 0.54/0.46; 1.78 dB = scalloping of the 25/46 "exact" Hamming) | RRE, PUL |
| P14 | B. L. Lewis, F. F. Kretschmer, "Linear frequency modulation derived polyphase pulse compression codes," *IEEE Trans. AES* 18(5), 637–641 (1982). (peer-reviewed) *cited, not re-read* | P3/P4 codes | PUL |
| P15 | R. L. Frank, "Polyphase codes with good nonperiodic correlation properties," *IEEE Trans. IT* 9(1), 43–45 (1963). (peer-reviewed) *cited, not re-read* | Frank code | PUL |
| P16 | R. H. Barker, "Group synchronizing of binary digital systems," in *Communication Theory*, Butterworths, 1953. (proceedings) *cited, not re-read* | Barker codes (verified) | PUL |
| P17 | J. P. Costas, "A study of a class of detection waveforms having nearly ideal range–Doppler ambiguity properties," *Proc. IEEE* 72(8), 996–1009 (1984); S. W. Golomb, H. Taylor, *Proc. IEEE* 72(9), 1143–1163 (1984). (peer-reviewed) *cited, not re-read* | Costas arrays, Welch construction (verified) | AMB |
| P18 | A. Dürr, B. Schweizer, C. Waldschmidt, "Leakage phase noise mitigation for monostatic FMCW radar sensors using carrier transmission," IEEE IMS 2019 (Ulm author copy). https://mwt-www.e-technik.uni-ulm.de/public/papers/2019/2019_IMS_Duerr_Leakage_Phase_Noise_Mitigation_For_Monostatic_FMCW_Radar_Sensors_Using_Carrier_Transmission.pdf (peer-reviewed) | range-correlation formula, ~30 dB isolation, leakage mechanisms | FMCW, CW |
| P19 | M. C. Budge, M. P. Burt, "Range correlation effects in radars," IEEE National Radar Conf. 1993. (peer-reviewed) *via [P18]* | range-correlation effect | FMCW, CW |
| P20 | S. Ayhan et al., "Impact of frequency ramp nonlinearity, phase noise, and SNR on FMCW radar accuracy," *IEEE Trans. MTT* 64(10), 3290–3301 (2016). (peer-reviewed) *metadata only* | nonlinearity types and accuracy | FMCW |
| P21 | V. C. Chen, F. Li, S.-S. Ho, H. Wechsler, "Micro-Doppler effect in radar: phenomenon, model, and simulation study," *IEEE Trans. AES* 42(1), 2–21 (2006). (peer-reviewed) *cited, not re-read* | rotor micro-Doppler, blade flash rule | CW |
| P22 | C. R. Vaughn, "Birds and insects as radar targets: a review," *Proc. IEEE* 73(2), 205–227 (1985). (peer-reviewed) *abstract* | prolate-spheroid/dipole bird models | RCS |
| P23 | R. Nakamura, K. Suzuki, H. Hadama, "RCS measurements of various drones at 24 GHz," *IEICE Comm. Express* 9(7) (2020). (peer-reviewed letter) *abstract* | drone mean RCS −8.1 to −19.1 dBsm | RCS, RRE |
| P24 | EC JRC / EMSL, "RCS measurements of pedestrian dummies and humans in the 24/77 GHz frequency bands" (2013, JRC78619). (report) *abstract* | human RCS ranges | RCS, RRE |
| P25 | "Measurement results of vehicular RCS characteristics for 79 GHz millimeter band," IEEE conf. 2017 (Xplore 8311576); X-band drone RCS studies (Semkin et al.; Quevedo et al., IET RSN 2019). (peer-reviewed) *abstract/snippet* | vehicle log-normal RCS; X-band drone RCS −15 to −5 dBsm | RCS |
| P26 | I. S. Reed, J. D. Mallett, L. E. Brennan, "Rapid convergence rate in adaptive arrays," *IEEE Trans. AES* 10(6), 853–863 (1974). (peer-reviewed) *cited, not re-read; verified by MC* | SMI loss (K+2−N)/(K+1) | CLU |
| P27 | J. S. Marshall, W. McK. Palmer, "The distribution of raindrops with size," *J. Meteorology* 5, 165–166 (1948). (peer-reviewed) *cited, not re-read* | DSD and Z–R (mismatch 296R^1.47 vs 200R^1.6 noted) | CLU |
| P28 | V. Gregers-Hansen, R. Mital, "An improved empirical model for radar sea clutter reflectivity," *IEEE Trans. AES* 48(4), 3512–3524 (2012). (peer-reviewed) *cited, not used numerically* | NRL sea-clutter model | CLU |
| P29 | F. C. Robey et al., "MIMO radar theory and experimental results," Asilomar 2004; H. Sun et al., "Analysis and comparison of MIMO radar waveforms," Int. Radar Conf. 2014. (peer-reviewed) *cited, not re-read* | MIMO principles, TDM/BPM/DDM comparison | MIMO |
| P30 | M. E. Yanik, M. Torlak, "Near-field 2-D SAR imaging by millimeter-wave radar for concealed item detection," IEEE RWS 2019. (peer-reviewed) *abstract* | TI IWR1443 rail SAR imaging | SAR |
| P31 | G. L. Charvat, A. J. Fenn, B. T. Perry, "The MIT IAP radar course: Build a small radar system capable of sensing range, Doppler, and synthetic aperture (SAR) imaging," IEEE Radar Conf. 2012; MIT OCW RES.LL-003 (IAP 2011). (peer-reviewed / lecture notes) *abstract + course pages* | coffee-can radar architecture, modes | RRE, FMCW, SAR, DIY |
| S1 | ITU-R Recommendations P.676, P.838, P.840 (as implemented in `tools/verify/prop_atmospheric.py`, domain 09, and the P.840 water-permittivity model here). (standard) | gas/rain attenuation, water permittivity | RRE, RCS, CLU |
| S2 | IMDA, "Technical Specification — Short Range Devices," IMDA TS SRD Issue 1 Rev 3, September 2023, Table 1. (regulation) | Singapore radar bands and limits (77–81 GHz absent from TS SRD; it is exempt as UWB under the Exemption Notification item 17 + IMDA TS UWB Issue 1, Oct 2016, Table 1: mean −3 dBm/MHz, peak 55 dBm/50 MHz) | RRE, CW, FMCW, DIY |

## Application notes, datasheets and vendor documentation
| # | Citation | Used for | Used in |
|---|---|---|---|
| A1 | V. Dham, "Programming Chirp Parameters in TI Radar Devices," TI SWRA553A (2017, rev. 2020). https://www.ti.com/lit/pdf/swra553 (app note) | chirp formulas, IF limits, timing tables, Table 1 (re-derived) | FMCW, RRE, MIMO, DIY |
| A2 | S. Rao, "Introduction to mmwave Sensing: FMCW Radars," TI training slides. (app note/training) | FMCW fundamentals, sign convention, design procedure, radar equation with T_meas | FMCW, RRE |
| A3 | S. Rao, "MIMO Radar," TI SWRA554A (2017/2018). https://www.ti.com/lit/an/swra554a/swra554a.pdf (app note) | virtual arrays, TDM/BPM | MIMO, FMCW, DET |
| A4 | TI TIDEP-01012 / TIDUEN5A cascade imaging radar reference design (2019/2020). (reference design) *summary* | 12×16, 192/86 virtual, ~1.4° | MIMO |
| A5 | TI product pages IWR6843, AWR1843, AWR2944 (accessed 2026-09-27). (datasheet) | device specs | RRE, FMCW, DIY |
| A6 | Infineon BGT60TR13C data sheet. (datasheet) *snippet* | 58–63.5 GHz, 1TX/3RX AiP, >5 GHz, 12-bit 4 MSps | FMCW, DIY |
| A7 | Acconeer A121 data sheet (v1.x). (datasheet) *snippet* | 60 GHz PCR, ≤20 m, mm/µm accuracy | DIY |
| A8 | Analog Devices CN0566 circuit note / EVAL-CN0566-RPIZ; M. Lichtman, *PySDR* "Hands-on with Phaser". (circuit note / online textbook) | Phaser architecture | FMCW, DIY |
| A9 | ST Engineering Electronics (AgilSense), HB100 data sheet V2.02 (2022). (datasheet) | HB100 specs | CW, DIY |
| A10 | InnoSenT IPM-165 data sheet v8.5 (2014) and W. Weidmann, InnoSenT Application Note III. (datasheet / app note) | IPM-165 specs, IF amplifier practice, FSK, 44 Hz per km/h | CW, RRE, DIY |
| A11 | Mini-Circuits ZX95-2536C+ VCO data sheet (rev. A). (datasheet) | tuning table used for nonlinearity simulation | FMCW, DIY |
| A12 | ADI ADALM-PLUTO specifications wiki; KrakenRF KrakenSDR product pages. (vendor) *snippet* | SDR/passive-radar hardware facts | DIY |

## Project reports, forums and other (secondary)
| # | Citation | Used for | Used in |
|---|---|---|---|
| R1 | H. Forstén, hforsten.com (6 GHz FMCW radar, SAR imaging, autofocus) and github.com/Ttl/fmcw3. (project report) | DIY FMCW and SAR practice | FMCW, SAR, DIY |
| R2 | Coffee-can radar student build reports (coffeecanradar.wordpress.com 2017; Union College capstones 2020). (project report) | parts list, ramp settings | DIY, RRE |

## Added by W5-E5 (2026-10-03) for radar-tracking-monopulse-and-trackers (TRK)
| # | Citation | Used for | Used in |
|---|---|---|---|
| TK1 | A. W. Doerry, D. L. Bickel, *Notes on Amplitude versus Phase Comparison Monopulse Antennas for Radar*, Sandia SAND2024-06153, May 2024. https://www.osti.gov/servlets/purl/2429954 (government report) *read in full as text* | k_m definition, σ_θ = θ/(k_m√(2SNR)), optimum squint 0.415 θ_g, amplitude ≡ phase monopulse | TRK |
| TK2 | MIT LL / IEEE NH Section *Radar Systems Course*, "Parameter estimation and tracking, Part 1" (2010). https://gmoein.github.io/files/MIT%20Graduate%20Radar%20Course/Radar%202009%20A_15%20Parameter%20Estimation%20and%20Tracking%20Part%201.pdf (lecture notes) *read as text* | 10:1 beam splitting at ~13 dB, lobing/conical scan/monopulse, split gate, servo | TRK |
| TK3 | S. M. Sherman, D. K. Barton, *Monopulse Principles and Techniques*, 2nd ed., Artech House, 2011. (textbook) *cited via TK1, not re-read* | monopulse theory | TRK |
| TK4 | Y. Bar-Shalom, E. Tse, "Tracking in a cluttered environment with probabilistic data association," *Automatica* 11(5):451–460 (1975); Y. Bar-Shalom, T. E. Fortmann, *Tracking and Data Association*, Academic Press, 1988. (peer-reviewed / textbook) *recalled; PDAF re-implemented* | PDA equations | TRK |
| TK5 | S. S. Blackman, R. Popoli, *Design and Analysis of Modern Tracking Systems*, Artech House, 1999. (textbook) *recalled* | gating, GNN, JPDA, MHT, M-of-N | TRK |
| TK6 | Y. Bar-Shalom, X. R. Li, T. Kirubarajan, *Estimation with Applications to Tracking and Navigation*, Wiley, 2001; P. R. Kalata, IEEE T-AES 20(2):174–182, 1984. (textbook / peer-reviewed) | α-β trackers, converted measurements, IMM | TRK |
| — | Skolnik T1 ch. 4 (tracking radar) and Richards T2 ch. 7 (measurements) also cited on TRK, not re-read. | | TRK |

## Verification scripts (this domain)
`tools/verify/radar_detection_cfar.py`, `radar_range_equation.py`, `radar_rcs.py`, `radar_pulse_compression.py`, `radar_ambiguity.py`, `radar_cw_doppler.py`, `radar_fmcw.py`, `radar_mimo.py`, `radar_clutter_mti.py`, `radar_sar.py`, `radar_diy.py` — all print **ALL PASS** (2026-09-29); `est_radar_tracking.py` (tracking page, 2026-10-03) — **ALL PASS**.

## Added by W5-E8 (2026-10-12) — pulse-Doppler page (abbreviation PD)
| # | Citation | Used for | Used in |
|---|---|---|---|
| L1 | R. M. O'Donnell, "Radar Systems Engineering, Lecture 14: Airborne Pulse Doppler Radar," IEEE New Hampshire Section / AES Society Radar Systems Course (MIT LL material), 2010; mirror gmoein.github.io/files/MIT Graduate Radar Course/. (lecture notes) *READ via pdftotext* | PRF classes, X-band PRF ranges and duty (HPRF 100–300 kHz < 50 %, MPRF 10–30 kHz ~5 %, LPRF 1–3 kHz ~0.5 %), eclipsing 1–2 dB, 3-PRF HPRF, 7-PRF MPRF example | PD |
| L2 | R. M. O'Donnell, "Radar Systems Engineering, Lecture 13: Clutter Rejection — Doppler Filtering," same course, 2009. (lecture notes) *READ* | CPI/filter bank, MTD (8-pulse bank, zero-velocity filter, clutter map), ASR-9 40 dB Doppler sidelobes, CRT formula | PD |
| P32 | W. H. Long, D. H. Mooney, W. A. Skillman, "Medium PRF for the AN/APG-66 Radar," *Proc. IEEE* 73(2):301–311, 1985. (peer-reviewed) *cited via L1, not read* | MPRF sets, M-of-N | PD |
| P33 | G. V. Trunk, S. Brockett, "Range and velocity ambiguity resolution," Proc. IEEE National Radar Conf., 1993. (peer-reviewed) *cited, not read; method re-implemented* | clustering ambiguity resolution | PD |
| P34 | J. W. Taylor Jr., G. Brunins, "Design of a new airport surveillance radar (ASR-9)," *Proc. IEEE* 73(2):284–289, 1985; O'Donnell & Cartledge, MIT LL ATC-69, 1977 (MTD). (peer-reviewed / report) *via L2* | MTD, ASR-9 | PD |
| R3 | A. Stove (Thales UK), "Medium-PRF radar waveform design and understanding," Oxford Mathematical Institute study-group problem, 2011, maths.ox.ac.uk/node/8863. (problem statement; read) | blind zones, multi-PRF bursts, inverse design problem | PD |
| — | Textbooks T1 (Skolnik ch. 3), T2 (Richards ch. 3–5), T3 (POMR ch. 17), T9 (Stimson) above are also cited by PD (*cited, not re-read*). | data cube, PRF regimes, CRT | PD |

Verification: `tools/verify/e8_pulse_doppler.py` (ALL PASS, 2026-10-12); figure `kb/11-radar/figures/e8-range-doppler-and-blind-zones.png`.

## Added by W5-E10 (2026-10-12) — radar-applications-gpr-through-wall-sensing
- D. J. Daniels (ed.), *Ground Penetrating Radar*, 2nd ed., IET 2004; Davis & Annan, *Geophys. Prosp.* 37(5) 1989 (material table via UBC GPG). (textbook / peer-reviewed)
- F. Adib, D. Katabi, "See Through Walls with WiFi!", SIGCOMM 2013; F. Adib et al., "3D Tracking via Body Radio Reflections", NSDI 2014. (peer-reviewed; read)
- Y. Ma et al., "WiFi Sensing with CSI: A Survey", ACM Comput. Surv. 52(3) 2019; IEEE Std 802.11bf-2025. (peer-reviewed / standard)
- R. Maggiora et al., *Sci. Rep.* 9:11964 (2019) harmonic radar; K. Rasilainen, V. Viikari, *IJAP* 2015:565734; RECCO R9 quick guide; Mazzaro et al., *IEEE TAES* 50(1) 2014; US 6,057,765. (peer-reviewed / manual / patent)
- J. Desbonnet, RCWL-0516 reverse engineering (GitHub); Hi-Link HLK-LD2410 manual V1.03. (community / datasheet)
- Verification: `tools/verify/e10_radar_apps.py` (ALL PASS).
