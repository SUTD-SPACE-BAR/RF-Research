# 10-comms-modulation — sources

Consolidated bibliography for this domain. Each page also carries its own numbered source list; this file groups them by type, says what each supports and how reliable it is. "Accessed" sources (fetched and read during research, 2026-09-27) are marked **[read]**; the others are standard references cited for the textbook-level result they are universally known for (sections given where known) and whose results were *derived or numerically verified independently* in `tools/verify/comms_*.py` rather than copied.

## Textbooks
| Ref | Citation | Used for (pages) |
|---|---|---|
| T1 | J. G. Proakis and M. Salehi, *Digital Communications*, 5th ed., McGraw-Hill, 2008 | ch. 3 modulation & PSDs; ch. 4 optimum detection, BER, Shannon comparison; ch. 5 synchronisation; ch. 9 Nyquist/RC/equalisation; ch. 11 multicarrier; ch. 12 spread spectrum (all pages) |
| T2 | B. Sklar, *Digital Communications: Fundamentals and Applications*, 2nd ed., Prentice Hall, 2001 | matched filter, ISI/RRC, bandwidth-efficiency plane, MSK/OQPSK (BER, matched filter, pulse shaping, digital modulation) |
| T3 | S. Haykin, *Communication Systems*, 4th ed., Wiley, 2001 | AM/FM/SSB, noise figures of merit, FM threshold, pre-/de-emphasis; non-coherent FSK, DPSK (analog, BER) |
| T4 | B. P. Lathi and Z. Ding, *Modern Digital and Analog Communication Systems*, 4th ed., Oxford UP, 2009 | amplitude/angle modulation, noise in analog systems (analog) |
| T5 | A. Goldsmith, *Wireless Communications*, Cambridge UP, 2005 | fading BER (ch. 6), OFDM (ch. 12) (BER, OFDM) |
| T6 | T. S. Rappaport, *Wireless Communications: Principles and Practice*, 2nd ed., Prentice Hall, 2002 | delay spread & coherence bandwidth (ch. 5), modulation choice, π/4-QPSK, GMSK (ch. 6), equalisation (ch. 7) |
| T7 | S. Lin and D. J. Costello Jr., *Error Control Coding*, 2nd ed., Pearson, 2004 | block/cyclic/BCH/RS, convolutional & Viterbi, turbo, LDPC (channel coding) |
| T8 | M. Rice, *Digital Communications: A Discrete-Time Approach*, Pearson Prentice Hall, 2009 | loop-filter design equations (App. C), carrier & timing sync, interpolators (synchronisation) |
| T9 | U. Mengali and A. N. D'Andrea, *Synchronization Techniques for Digital Receivers*, Plenum, 1997 | modified CRBs, feedforward/feedback estimators (synchronisation) |
| T10 | H. Meyr, M. Moeneclaey, S. A. Fechtel, *Digital Communication Receivers*, Wiley, 1998 | synchronisation & channel estimation (synchronisation) |
| T11 | F. M. Gardner, *Phaselock Techniques*, 3rd ed., Wiley, 2005 | PLL bandwidth, damping, squaring loss, tracking error (synchronisation) |
| T12 | S. M. Kay, *Fundamentals of Statistical Signal Processing, Vol. II: Detection Theory*, Prentice Hall, 1998 | Neyman–Pearson, matched-filter detector, envelope detection (matched filter) |
| T13 | H. L. Van Trees, *Detection, Estimation, and Modulation Theory, Part I*, Wiley, 1968/2001 | likelihood-ratio tests, random-phase detection (matched filter) |
| T14 | J. M. Wozencraft and I. M. Jacobs, *Principles of Communication Engineering*, Wiley, 1965 | signal space, theorem of irrelevance (matched filter) |
| T15 | M. K. Simon and M.-S. Alouini, *Digital Communication over Fading Channels*, 2nd ed., Wiley, 2005 | average BER in fading (BER) |
| T16 | M. A. Richards, *Fundamentals of Radar Signal Processing*, 2nd ed., McGraw-Hill, 2014; M. I. Skolnik, *Introduction to Radar Systems*, 3rd ed., 2001 | matched filter, LFM compression, mismatch loss (matched filter) |
| T17 | J. B. Anderson, T. Aulin, C.-E. Sundberg, *Digital Phase Modulation*, Plenum, 1986 | CPM spectra (digital modulation) |
| T18 | S. W. Golomb, *Shift Register Sequences*, 1967/1982 | m-sequence properties (spread spectrum) |
| T19 | A. J. Viterbi, *CDMA: Principles of Spread Spectrum Communication*, Addison-Wesley, 1995; M. K. Simon et al., *Spread Spectrum Communications Handbook*, McGraw-Hill, 1994 | CDMA capacity, coding vs spreading (spread spectrum) |
| T20 | E. D. Kaplan and C. J. Hegarty (eds.), *Understanding GPS/GNSS*, 3rd ed., Artech House, 2017 | FLL-assisted PLL, C/A acquisition (sync, spread spectrum) |
| T21 | R. van Nee and R. Prasad, *OFDM for Wireless Multimedia Communications*, Artech House, 2000 | OFDM (ofdm) |
| T22 | D. Bertsekas and R. Gallager, *Data Networks*, 2nd ed., Prentice Hall, 1992, ch. 4 (multiaccess communication) — recalled | ALOHA, slotted ALOHA, stability, CSMA (multiple-access-and-duplexing) |
| T23 | B. Razavi, *RF Microelectronics*, 2nd ed., Prentice Hall, 2011, §3.6 — recalled | duplexing, multiple access, duplexer requirements (multiple-access-and-duplexing); also uses T6 ch. 9 and T1 ch. 16 |

## Peer-reviewed papers (primary results)
| Ref | Citation | Used for |
|---|---|---|
| P1 | C. E. Shannon, "A Mathematical Theory of Communication," *BSTJ* 27, 1948 — §19 (2TW dimensions), §25 Thm 17, §26 peak power **[read]** https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf | capacity, noise-like signals, PAPR remark |
| P2 | H. Nyquist, "Certain topics in telegraph transmission theory," *Trans. AIEE* 47:617–644, 1928 | zero-ISI criterion |
| P3 | J. R. Carson, "Notes on the theory of modulation," *Proc. IRE* 10(1):57–64, 1922 | Carson's rule |
| P4 | E. H. Armstrong, *Proc. IRE* 24(5):689–740, 1936 | wideband FM |
| P5 | S. O. Rice, "Noise in FM receivers," in *Time Series Analysis*, Wiley, 1963 | FM threshold (clicks) |
| P6 | G. L. Turin, "An introduction to matched filters," *IRE Trans. IT* 6(3):311–329, 1960; D. O. North, RCA PTR-6C 1943 / *Proc. IEEE* 51(7), 1963 | matched filter |
| P7 | J. W. Craig, *Proc. IEEE MILCOM* 1991, pp. 571–575 | exact M-PSK SER integral |
| P8 | Y. Polyanskiy, H. V. Poor, S. Verdú, *IEEE Trans. IT* 56(5):2307–2359, 2010 | finite-blocklength normal approximation |
| P9 | S. Pasupathy, "Minimum shift keying," *IEEE Comm. Mag.* 17(4):14–22, 1979 | MSK PSD, 99 % bandwidth |
| P10 | K. Murota and K. Hirade, "GMSK modulation…," *IEEE Trans. Comm.* 29(7):1044–1050, 1981 | GMSK |
| P11 | R. W. Hamming, *BSTJ* 29(2):147–160, 1950 | Hamming codes |
| P12 | I. S. Reed and G. Solomon, *J. SIAM* 8(2):300–304, 1960 | RS codes |
| P13 | R. C. Bose & D. K. Ray-Chaudhuri, *Inf. Control* 3(1), 1960; A. Hocquenghem, *Chiffres* 2, 1959 | BCH |
| P14 | A. J. Viterbi, *IEEE Trans. IT* 13(2):260–269, 1967; G. D. Forney, *Proc. IEEE* 61(3):268–278, 1973; *Concatenated Codes*, 1966 | Viterbi algorithm, concatenation |
| P15 | C. Berrou, A. Glavieux, P. Thitimajshima, *Proc. ICC* 1993, pp. 1064–1070 | turbo codes |
| P16 | R. G. Gallager, *IRE Trans. IT* 8(1):21–28, 1962; D. J. C. MacKay & R. M. Neal, *Electronics Letters* 32(18), 1996 | LDPC |
| P17 | E. Arıkan, *IEEE Trans. IT* 55(7):3051–3073, 2009 | polar codes |
| P18 | G. D. Forney, *IEEE Trans. IT* 18(3):363–378, 1972 | MLSE |
| P19 | S. U. H. Qureshi, "Adaptive equalization," *Proc. IEEE* 73(9):1349–1387, 1985; B. Widrow & M. E. Hoff, *IRE WESCON* 1960 | equalisers, LMS |
| P20 | F. M. Gardner, *IEEE Trans. Comm.* 34(5):423–429, 1986 | Gardner TED |
| P21 | K. H. Mueller and M. Müller, *IEEE Trans. Comm.* 24(5):516–531, 1976 | M&M TED |
| P22 | J. P. Costas, "Synchronous communications," *Proc. IRE* 44(12):1713–1718, 1956 | Costas loop |
| P23 | D. C. Rife and R. R. Boorstyn, *IEEE Trans. IT* 20(5):591–598, 1974; S. Kay, *IEEE Trans. ASSP* 37(12):1987–1990, 1989 | frequency CRB & estimators |
| P24 | L. Erup, F. M. Gardner, R. A. Harris, *IEEE Trans. Comm.* 41(6):998–1008, 1993 | interpolators |
| P25 | J. L. Massey, "Optimum frame synchronization," *IEEE Trans. Comm.* 20(2):115–119, 1972 | frame sync |
| P26 | R. L. Pickholtz, D. L. Schilling, L. B. Milstein, *IEEE Trans. Comm.* 30(5):855–884, 1982 | spread-spectrum tutorial |
| P27 | R. Gold, *IEEE Trans. IT* 13(4):619–621, 1967 | Gold codes |
| P28 | L. Vangelista, "Frequency shift chirp modulation: the LoRa modulation," *IEEE SP Letters* 24(12):1818–1821, 2017 | CSS model |
| P29 | J. Tapparel et al., *IEEE SPAWC* 2020 (arXiv:2002.08208); M. Knight & B. Seeber, *Proc. GRCon* 2016 | LoRa coding chain (Hamming, interleaver, Gray, whitening) |
| P30 | A. Maleki et al., "A tutorial on chirp spread spectrum for LoRaWAN," arXiv:2310.10503, 2023 **[read abstract]** | CSS tutorial (preprint) |
| P31 | R. W. Chang, *BSTJ* 45(10):1775–1796, 1966; S. B. Weinstein & P. M. Ebert, *IEEE Trans. Comm. Tech.* 19(5):628–634, 1971; A. Peled & A. Ruiz, *ICASSP* 1980 | OFDM origins, DFT, cyclic prefix |
| P32 | T. M. Schmidl & D. C. Cox, *IEEE Trans. Comm.* 45(12):1613–1621, 1997; P. H. Moose, *IEEE Trans. Comm.* 42(10):2908–2914, 1994 | OFDM sync |
| P33 | T. Pollet, M. Van Bladel, M. Moeneclaey, *IEEE Trans. Comm.* 43(2/3/4):191–193, 1995 | OFDM CFO/phase-noise sensitivity |
| P34 | S. H. Han & J. H. Lee, *IEEE Wireless Comm.* 12(2):56–65, 2005 | PAPR reduction |
| P35 | W. W. Peterson & D. T. Brown, *Proc. IRE* 49(1):228–235, 1961 | cyclic codes for error detection |
| P36 | P. Koopman & T. Chakravarty, *Proc. DSN* 2004, pp. 145–154 | CRC polynomial selection |
| P37 | S. Cheshire & M. Baker, *IEEE/ACM Trans. Networking* 7(2):159–169, 1999 | COBS |
| P38 | S. Lin, D. J. Costello, M. J. Miller, *IEEE Comm. Mag.* 22(12):5–17, 1984 | ARQ |
| P39 | B. Sklar, *IEEE Comm. Mag.* 31(11):91–101, 1993 | design regimes (choice guide) |
| P-MA1 | N. Abramson, "The ALOHA system — another alternative for computer communications," *AFIPS Conf. Proc.* 37 (FJCC), 281–285, 1970 (located) | pure ALOHA S = Ge^(−2G), max 1/2e — re-derived and simulated (multiple-access-and-duplexing) |
| P-MA2 | L. G. Roberts, "ALOHA packet system with and without slots and capture," *ACM SIGCOMM CCR* 5(2):28–42, 1975 (recalled) | slotted ALOHA, capture (multiple-access-and-duplexing) |
| P-MA3 | L. Kleinrock and F. A. Tobagi, "Packet switching in radio channels: Part I — carrier sense multiple-access modes and their throughput-delay characteristics," *IEEE Trans. Commun.* COM-23(12):1400–1416, 1975 (located) | non-persistent CSMA throughput — re-derived and simulated (multiple-access-and-duplexing) |
| P-MA4 | D. Croce et al., "Impact of LoRa imperfect orthogonality: analysis of link-level performance," *IEEE Commun. Lett.* 22(4):796–799, 2018 (via domain 15) | inter-SF rejection ≈ −16 dB (multiple-access-and-duplexing) |

## Standards and official documents
| Ref | Citation | Used for |
|---|---|---|
| S1 | CCSDS 131.0-B-5, *TM Synchronization and Channel Coding* (Blue Book), Sept. 2023 **[read]** https://ccsds.org/Pubs/131x0b5.pdf | K=7 (171,133) conv + puncturing, ≥ 3-bit soft; RS(255,223)/(255,239), field poly, interleaving; turbo; LDPC; ASM 1ACFFC1D; randomisers |
| S2 | CCSDS 130.1-G-3, *TM Sync & Channel Coding — Summary of Concept and Rationale* (Green Book), June 2020 **[read]** https://ccsds.org/Pubs/130x1g3e1.pdf | BI-AWGN limits 0.2/−0.5/−0.8/−1.1/−1.6 dB; block-length limits; code gains; quantisation losses; Viterbi node-sync |
| S3 | CCSDS 133.0-B-2, *Space Packet Protocol*, June 2020 **[read]** https://ccsds.org/Pubs/133x0b2e2.pdf | primary header field widths |
| S4 | CCSDS 132.0-B-3, *TM Space Data Link Protocol* | transfer frame, FECF |
| S5 | IS-GPS-200 Rev. N (NAVSTAR GPS interface specification) https://www.navcen.uscg.gov/sites/default/files/pdf/gps/IS-GPS-200N.pdf | C/A code definition, PRN taps, minimum power |
| S6 | GPS.gov, *L1 C/A PRN Code Assignments*, Jan. 2026 ed. **[read]** https://www.gps.gov/sites/default/files/2026-02/L1CA-PRN-code-assignments-2026-Jan_2.pdf | SBAS PRN G2 delays & first chips (Gold-code verification) |
| S7 | NTIA Manual, Annex J "Guidance for Determination of Necessary Bandwidth," Jan. 2021 **[read]** https://www.ntia.gov/files/ntia/publications/j_21_1.pdf | Carson K = 1, NBFM 11/16 kHz, digital FM & PSK/QAM necessary bandwidth, ITU-R SM.328 GMSK/MSK K-factors |
| S8 | IEEE Std 802.11-2020 §17 (OFDM PHY) | 802.11a numerology, EVM limits |
| S9 | 3GPP TS 36.211 (LTE physical channels); TS 38.212 (NR coding); TS 45.004 (GSM GMSK) | LTE numerology, 5G LDPC/polar, GMSK BT 0.3 |
| S10 | ETSI EN 300 744 (DVB-T); ETSI EN 302 307-1 (DVB-S2) | DVB-T modes; APSK constellations |
| S11 | Bluetooth SIG, *Core Specification* v5.4 | GFSK parameters, hopping |
| S12 | TAPR / APRS WG, *APRS Protocol Reference* v1.0.1, 2000 | Bell-202 AFSK 1200 baud |
| S13 | IETF RFC 6330 (RaptorQ) | fountain codes across packets |

## Lecture notes, application notes, datasheets, online texts
| Ref | Citation | Used for |
|---|---|---|
| L1 | MIT 6.02 *Digital Communication Systems*, Fall 2012, ch. 9 "Noise" (and ch. 8–10) **[read ch. 9]** https://ocw.mit.edu/courses/6-02-introduction-to-eecs-ii-digital-communication-systems-fall-2012/ | bipolar BER (erfc form), unequal priors, SNR |
| L2 | M. Lichtman, *PySDR*, chapters "Pulse Shaping" and "Synchronization" **[read]** https://pysdr.org | RC/RRC, BW = Rs(1+β) (two-sided), β 0.2–0.5, sync order, CFO range ±fs/2N, M&M, Costas, frame sync |
| L3 | E. Jacobsen, "Understanding and Relating Eb/No, SNR, and other Power Efficiency Metrics," dsprelated.com **[read]** https://www.dsprelated.com/showarticle/168.php | metric definitions, factor-of-two pitfalls |
| L4 | P. Koopman, *CRC Polynomial Zoo* **[read]** https://users.ece.cmu.edu/~koopman/crc/ | polynomial HD/length tables |
| L5 | G. Cook, *Catalogue of parametrised CRC algorithms* (RevEng) https://reveng.sourceforge.io/crc-catalogue/ | CRC parameter sets and check values |
| L6 | Semtech, *SX1276/77/78/79 datasheet*, Rev. 7 | LoRa demodulator SNR per SF, bit-rate formula |
| L7 | Keysight/Agilent AN 150, *Spectrum Analysis Basics* | Bessel-null deviation measurement |
| L8 | Circuit Design Inc., "FM capture effect" **[search summary]** https://www.cdt21.com/design_guide/fm-capture-effect/ | qualitative capture effect |
| L9 | MathWorks Communications Blockset "AWGN Channel" documentation **[search summary]** | complex-noise variance split |
| L10 | P. Karn, *libfec*; J. Gaeddert, *liquid-dsp*; GNU Radio `gr-fec`; AFF3CT; Sionna (software documentation) | practical FEC libraries |

## Forums (used only for misconceptions / questions)
| Ref | Citation | Used for |
|---|---|---|
| F1 | comp.dsp thread "BER performance of BPSK and QPSK" (dsprelated.com/showthread/comp.dsp/104982); DSPLog BPSK BER article | QPSK-vs-BPSK per-bit confusion (forum — anecdotal) |
| F2 | TI E2E "CC1120: Carson's rule(s)"; ST community STM32WL FSK bandwidth thread (search results) | FSK bandwidth confusion (forum — anecdotal) |
| F3 | radiomuseum.org "FM capture ratio"; FM-DX tuner guide (search results) | typical capture-ratio claims 1–2 dB (forum — unverified) |

## Internal project context
| Ref | Citation | Used for |
|---|---|---|
| I1 | Space Bar avionics knowledge base, `~/.claude/knowledge/space-bar-avionics/` (flight-software-lessons.md, avionics-b-v3-primary-fc.md, avionics-c-secondary-fc.md) | EBYTE E22-400T33D / E220-900T30D, downlink-only telemetry, protocol-versioning lessons |

## Reliability notes and discrepancies
- **MSK 99 % bandwidth:** NTIA Annex J (citing ITU-R SM.328) lists K = 1.28 for unfiltered MSK; the analytic PSD and simulation give 1.18 Rb (Pasupathy, Sklar). GMSK K-factors from the same table match simulation (1.03/0.91/0.86). Reported as unresolved.
- **Block-length penalty:** CCSDS Green Book (sphere-packing bound) ≈ 1.3 dB from 100 → 1000 bits; PPV normal approximation 1.6 dB. Different bounds; both quoted.
- **K=7 r½ Viterbi at 1e-5:** 4.17 dB (union bound; Monte-Carlo agrees), consistent with CCSDS's ≈ 5.5 dB gain over 9.6 dB.
- **WebFetch summariser errors caught:** it claimed a 2-bit CCSDS packet version field (the standard says 3 bits) and misreported PySDR's bandwidth definition; the primary texts were read directly (pdftotext / targeted re-fetch) and are what the pages use.

## Added by W5-E11 (mimo-capacity-and-channel-estimation)
- D. Tse, P. Viswanath, *Fundamentals of Wireless Communication*, Cambridge 2005, chs. 3, 5, 7–9 — https://web.stanford.edu/~dntse/papers/book121004.pdf. (textbook)
- S. M. Alamouti, *IEEE JSAC* 16(8), 1998; L. Zheng, D. Tse, *IEEE Trans. IT* 49(5), 2003; E. Telatar, *ETT* 10(6), 1999. (peer-reviewed)
- M. Biguesh, A. B. Gershman, *IEEE Trans. SP* 54(3), 2006 (training-based MIMO estimation); B. Hassibi, B. Hochwald, *IEEE Trans. IT* 49(4), 2003. (peer-reviewed)
- Verification: `tools/verify/e11_mimo.py` (27/27).
