# 06-rf-circuits — sources (domain bibliography)

Consolidated list of the sources cited in the 20 pages of this domain (14 from W2-B2, 6 added by W5-E7: AGC = agc-loops-and-receiver-gain-control, PAC = pa-control-protection-and-sequencing, DUP = duplexers-diplexers-and-crystal-filters, COS = co-site-interference-and-transmitter-intermod, ISF = oscillator-phase-noise-ltv-isf, MOD = modulator-and-detector-circuits; W5-E7 also extended CPL and PA). Page abbreviations: STAB = amplifier-stability-and-biasing, LNA = lna-design, PA = power-amplifiers, FILT = rf-filters-lc-saw-baw-cavity-microstrip, CPL = couplers-dividers-combiners, BAL = baluns-and-rf-transformers, SW = rf-switches-attenuators-limiters, MIX = mixers, PLL = vco-and-pll-synthesizers, RX = receiver-architectures, TX = transmitter-architectures, DET = detectors-and-power-meters, MULT = frequency-multipliers-dividers, CIRC = circulators-isolators. Reliability tags as in CONVENTIONS.md. "Read" = full text read in this task; otherwise used via summary/abstract or as a standard textbook reference.

## Textbooks
| Source | Used for | Pages |
|---|---|---|
| D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — ch. 4, 6, 7, 8, 9, 10, 12, 13 | power gains, stability circles, K/μ, noise circles (ch. 12); dividers/couplers/hybrids (ch. 7); filters, Richards/Kuroda, stepped impedance, coupled-line BPF (ch. 8); ferrites/circulators (ch. 9); PIN control circuits (ch. 10); mixers (ch. 13); cavity Q (ch. 6) | STAB, LNA, FILT, CPL, BAL, SW, MIX, CIRC |
| D. M. Pozar, *Microwave and RF Design of Wireless Systems*, Wiley, 2001 | receiver architectures, frequency planning | RX |
| G. Gonzalez, *Microwave Transistor Amplifiers: Analysis and Design*, 2nd ed., Prentice Hall, 1997 | stability (ch. 3), noise/LNA and balanced amplifiers (ch. 4) | STAB, LNA |
| S. C. Cripps, *RF Power Amplifiers for Wireless Communications*, 2nd ed., Artech House, 2006 | load line, load-pull contours, reduced conduction angle, class F, Doherty; harmonic currents | PA, MULT |
| A. Grebennikov, *RF and Microwave Power Amplifier Design*, 2nd ed., McGraw-Hill, 2015 | class E with finite feed inductance, harmonic tuning | PA |
| B. Razavi, *RF Microelectronics*, 2nd ed., Prentice Hall, 2011 | LNA topologies (ch. 5), mixers incl. passive/25 % duty (ch. 6), transceiver architectures, IQ mismatch, DC offset, IIP2, pulling (ch. 4), oscillators/PLLs (ch. 8–10) | LNA, MIX, RX, TX, PLL |
| T. H. Lee, *The Design of CMOS Radio-Frequency Integrated Circuits*, 2nd ed., Cambridge, 2004 | inductively degenerated LNA noise | LNA |
| H. A. Haus, R. B. Adler, *Circuit Theory of Linear Noisy Networks*, Wiley/MIT, 1959 | noise-measure invariance | LNA |
| G. L. Matthaei, L. Young, E. M. T. Jones, *Microwave Filters, Impedance-Matching Networks, and Coupling Structures*, Artech House, 1980 | g-value tables, loss, coupled-line/interdigital/combline | FILT, PA |
| J.-S. Hong, M. J. Lancaster, *Microstrip Filters for RF/Microwave Applications*, Wiley, 2001/2011 | microstrip filters, coupling-coefficient/Qe extraction, coupled-resonator design, cross-coupling | FILT |
| R. J. Cameron, C. M. Kudsia, R. R. Mansour, *Microwave Filters for Communication Systems*, Wiley, 2007/2018 | coupling-matrix synthesis/analysis | FILT |
| A. I. Zverev, *Handbook of Filter Synthesis*, Wiley, 1967 | helical-resonator Q (empirical) | FILT |
| S. A. Maas, *Microwave Mixers*, 2nd ed., Artech House, 1993; *Nonlinear Microwave and RF Circuits*, 2nd ed., 2003 | diode/APDP mixers; multipliers and dividers | MIX, MULT |
| D. Banerjee, *PLL Performance, Simulation, and Design*, 5th ed., 2017 (free, TI) | loop-filter equations, noise sources, spurs, lock time | PLL |
| W. F. Egan, *Phase-Lock Basics*, 2nd ed., Wiley-IEEE, 2008 | loop dynamics, noise transfer | PLL |
| C. Bowick, *RF Circuit Design*, 2nd ed., Newnes, 2008 | lumped L-network/balun matching | BAL |
| J. Sevick, *Transmission Line Transformers*, 4th ed., Noble, 2001 | Guanella/Ruthroff TLTs | BAL |
| A. Suárez, R. Quéré, *Stability Analysis of Nonlinear Microwave Circuits*, Artech House, 2003 | large-signal / parametric stability (scope) | STAB |
| S. M. Sze, K. K. Ng, *Physics of Semiconductor Devices*, 3rd ed., Wiley, 2007 | PIN high-injection resistance | SW |
| R. K. Mongia et al., *RF and Microwave Coupled-Line Circuits*, 2nd ed., Artech House, 2007 | coupler directivity compensation (background) | CPL |
| *Reference Data for Engineers*, 9th ed., Newnes, 2002 | attenuator equations (re-derived) | SW |
| A. Papoulis, *Probability, Random Variables and Stochastic Processes* | log of Rayleigh variable (Euler constant) | DET |

## Peer-reviewed papers
| Source | Used for | Pages |
|---|---|---|
| M. L. Edwards, J. H. Sinsky, "A new criterion for linear 2-port stability using a single geometrically derived parameter," IEEE T-MTT 40(12):2303–2311, 1992 (**read**) | μ, μ′ test, geometric margin, one auxiliary condition suffices | STAB, LNA |
| J. M. Rollett, "Stability and power-gain invariants of linear twoports," IRE Trans. CT-9:29–32, 1962 | K factor, embedding invariants | STAB |
| M. Platzker, W. Struble, K. T. Hetzler, "Instabilities diagnosis and the role of K in microwave circuits," IEEE IMS 1993 (abstract) | K insufficient with RHP poles; NDF | STAB |
| "Unconditional stability analysis of N-port networks based on structured singular value computation," arXiv:2406.19342, 2024 (preprint) | N-port stability | STAB |
| H. Rothe, W. Dahlke, "Theory of noisy fourpoles," Proc. IRE 44(6):811–818, 1956 | noise parameters | LNA |
| H. Hillbrand, P. Russer, "An efficient method for computer aided noise analysis of linear amplifier networks," IEEE Trans. CAS-23(4):235–238, 1976 | noise-correlation matrices (implemented in rfckt_noise2port.py) | STAB, LNA |
| D. K. Shaeffer, T. H. Lee, "A 1.5-V, 1.5-GHz CMOS low noise amplifier," IEEE JSSC 32(5):745–759, 1997 | inductive degeneration noise theory | LNA |
| F. H. Raab, "Maximum efficiency and output of class-F power amplifiers," IEEE T-MTT 49(6):1162–1166, 2001 (volume number flagged — a search result said vol. 47) | class-F efficiency table (reproduced by LP) | PA |
| F. H. Raab, "Idealized operation of the class E tuned power amplifier," IEEE Trans. CAS-24(12):725–735, 1977 | class-E constants | PA |
| N. O. Sokal, A. D. Sokal, "Class E …," IEEE JSSC SC-10(3):168–176, 1975; N. O. Sokal, "Class-E RF power amplifiers," QEX Jan/Feb 2001 (PDF not reachable) | class-E concept and finite-Q design | PA |
| F. H. Raab et al., "Power amplifiers and transmitters for RF and microwave," IEEE T-MTT 50(3):814–826, 2002 | classes, Doherty, ET/EER, outphasing | PA, TX |
| W. H. Doherty, Proc. IRE 24(9):1163–1182, 1936 | Doherty amplifier | PA |
| L. Ding et al., IEEE Trans. Commun. 52(1):159–165, 2004; D. R. Morgan et al., IEEE Trans. SP 54(10), 2006 | memory-polynomial DPD | PA |
| S. B. Cohn, "Dissipation loss in multiple-coupled-resonator filters," Proc. IRE 47(8):1342–1348, 1959 | filter loss formula (verified) | FILT |
| S. B. Cohn, "Parallel-coupled transmission-line-resonator filters," IRE T-MTT 6(2):223–231, 1958 | coupled-line BPF | FILT |
| R. Garg, I. J. Bahl, "Characteristics of coupled microstriplines," IEEE T-MTT 27(7):700–705, 1979 | even/odd modal parameters (implemented, FD-checked) | FILT, CPL |
| E. Hammerstad, Ø. Jensen, IEEE MTT-S Digest 1980; M. Kirschning, R. H. Jansen, Electron. Lett. 18, 1982 | microstrip models (via scikit-rf) | FILT |
| W. W. Macalpine, R. O. Schildknecht, Proc. IRE 47(12):2099–2105, 1959 | helical resonators | FILT |
| R. Ruby, "Review and comparison of bulk acoustic wave FBAR, SMR technology," IEEE Ultrasonics Symp., 2007 | BAW background | FILT |
| E. J. Wilkinson, IRE T-MTT 8(1):116–118, 1960 | Wilkinson divider | CPL |
| J. Lange, IEEE T-MTT 17(12):1150–1151, 1969 | Lange coupler | CPL |
| S. B. Cohn, IEEE T-MTT 16(2):110–116, 1968 | multi-section Wilkinson | CPL |
| N. Marchand, Electronics 17:142–145, 1944; K. S. Ang, I. D. Robertson, IEEE T-MTT 49(2):402–406, 2001 | Marchand balun | BAL |
| C. L. Ruthroff, Proc. IRE 47(8):1337–1342, 1959; G. Guanella, Brown Boveri Review 31:327–329, 1944 | TLTs | BAL |
| D. E. Bockelman, W. R. Eisenstadt, IEEE T-MTT 43(7):1530–1539, 1995 | mixed-mode S-parameters | BAL |
| B. Gilbert, IEEE JSSC SC-3(4):365–373, 1968 | Gilbert cell | MIX |
| D. K. Weaver, Proc. IRE 44(12):1703–1705, 1956; R. V. L. Hartley, US 1,666,206 (1928) | image-reject architectures | MIX |
| M. Cohn, J. E. Degenford, B. A. Newman, IEEE T-MTT 23(8):667–673, 1975 | APDP harmonic mixing | MIX |
| R. G. Vaughan, N. L. Scott, D. R. White, IEEE Trans. SP 39(9):1973–1984, 1991 | bandpass sampling, noise folding | MIX |
| D. B. Leeson, Proc. IEEE 54(2):329–330, 1966 | oscillator phase-noise model | PLL |
| T. A. D. Riley, M. A. Copeland, T. A. Kwasniewski, IEEE JSSC 28(5):553–559, 1993 | ΣΔ fractional-N noise | PLL |
| H. T. Nicholas, H. Samueli, Proc. 41st Freq. Control Symp., 1987 | DDS truncation spurs | PLL |
| R. Adler, Proc. IRE 34(6):351–357, 1946; B. Razavi, IEEE JSSC 39(9):1415–1424, 2004 | injection locking/pulling, ILFDs | TX, MULT |
| H. Chireix, Proc. IRE 23(11), 1935; D. C. Cox, IEEE Trans. Commun. 22(12), 1974 | outphasing/LINC | TX |
| C. H. Page, J. Res. NBS 56(4), 1956; J. M. Manley, H. E. Rowe, Proc. IRE 44(7), 1956 | multiplier efficiency limits | MULT |
| R. L. Miller, Proc. IRE 27(7):446–457, 1939 | regenerative divider | MULT |
| D. Polder, Phil. Mag. 40:99–115, 1949; H. Bosma, IEEE T-MTT 12(1):61–72, 1964; C. E. Fay, R. L. Comstock, IEEE T-MTT 13(1):15–27, 1965 | ferrite tensor, junction circulators | CIRC |
| N. A. Estep et al., Nature Physics 10:923–927, 2014; N. Reiskarimian, H. Krishnaswamy, Nature Communications 7:11217, 2016 | magnet-free circulators | CIRC |
| "An overview of the effects of out-of-band interference on GNSS receivers," NAVIGATION 67(1):143, 2020 (summary) | LNA vs filter placement | LNA |
| IEEE conference paper on PIN limiter spike leakage/recovery (IEEE Xplore doc. 22029) (summary) | limiter behaviour | SW |

## Standards / regulations
| Source | Used for | Pages |
|---|---|---|
| ETSI EN 300 220-1 V3.1.1 (2017-02), SRD 25–1000 MHz (limits via ST AN4305 summary) | spurious limits −54/−36/−30 dBm → harmonic-filter budgets | PA, TX |
| 47 CFR §15.205, §15.209 (eCFR) | restricted bands (2690–2900 MHz), 500 µV/m at 3 m | PA |

## Data sheets (manufacturer)
| Part | Key data used | Pages |
|---|---|---|
| Avago/Broadcom ATF-54143 (**read**) | S- and noise-parameter tables (3 V/60 mA), bias design, ratings, Curtice model | STAB, LNA |
| Mini-Circuits PGA-103+ rev. C (**read**) | 0.05–4 GHz gain block: gain/NF/OIP3/P1dB, 5 V 97 mA, +21 dBm max input | STAB, LNA |
| Infineon BGA524N6 rev. 3.5 (**read**) | GNSS LNA 19.6 dB/0.55 dB/2.5 mA, IP1dB, IIP3, 0 dBm max input | LNA, SW |
| u-blox ZED-F9P Integration Manual UBX-18010802 R16 (**read**) | active-antenna requirements, ESD, bias tee | LNA, FILT |
| NXP/Freescale AFT05MS003N rev. 0 (**read**) | 3 W LDMOS: gain/efficiency, Coss, RθJC, Zload table, ruggedness | PA, CIRC |
| Skyworks SKY66122-11 (**read**) | 863–928 MHz FEM: +30 dBm at 640 mA, harmonics, ruggedness, LNA NF | PA |
| Johanson 0433BM15A0001 (**read**) | 433 MHz chip balun/LPF for TI CC110x | BAL |
| Coilcraft 0603CS / 0805CS (product data) | inductor SRF/DCR | STAB, LNA |
| Analog Devices HMC920 (summary) | active bias controller | STAB |
| pSemi PE4259, PE4302/PE4312 (summaries) | SPDT switch, DSA | SW |
| MACOM MA4L062-134 / limiter modules (summary) | PIN limiter flat/spike leakage | SW |
| Analog Devices ADF4351 rev. 0 (**read**) | PFD limits, ICP, Kv, PN_SYNTH, PN1_f, VCO noise, harmonics, spurs, prescaler limits | PLL, MULT |
| Texas Instruments LMX2594 (summary) | FoM −236 dBc/Hz, 1/f −129, 10 MHz–15 GHz | PLL |
| Silicon Labs/Skyworks Si5351 + AN619 (summaries) | VCO 600–900 MHz, multisynth range | PLL |
| Semtech SX1261/2 (search excerpt) | low-IF receiver; +22 dBm PA | RX, TX |
| Analog Devices AD9361 (product facts) | zero-IF 70 MHz–6 GHz, 200 kHz–56 MHz | RX |
| Agilent/Avago HSMS-285x (**read**) | zero-bias Schottky: TSS, γ, SPICE | DET, SW |
| Analog Devices AD8307, AD8318, LTC5582 (summaries) | log/RMS detector specs | DET |
| Raltron RSF-433.920-1600 (DigiKey data); Murata SAFFB1G56KB0F0A (data-sheet summary) | SAW filters | FILT |

## Application notes / vendor technical articles
| Source | Used for | Pages |
|---|---|---|
| TriQuint (Qorvo), "Biasing GaN on SiC HEMT devices" (**read**) | pinch-off voltages, drift, dissipation | STAB |
| J. Bellantoni, TriQuint, "Bias techniques for GaN and pHEMT depletion mode devices," 2014 (**read** in part) | bias-circuit requirements | STAB |
| Mini-Circuits blog, "RF/microwave bias tees from theory to practice" | choke/cap rules | STAB |
| Mini-Circuits AN-00-009 "Understanding mixers" (**read**); AN-00-010, AN-00-001 (summaries) | mixer terms, IP3 conventions and rules of thumb | MIX, RX |
| Qorvo design hub "BAW vs SAW"; EDN "The difference between BAW and SAW filters" | Q, frequency limits, TCF | FILT |
| pSemi "What is Ron Coff?"; Marki "Why SOI?"; Tower Semiconductor press release 2020 | switch FoM | SW |
| G. Hiller, "Design with PIN diodes," Alpha/Skyworks APN1002; Microsemi *PIN Diode Circuit Designers' Handbook* | PIN switch/limiter design | SW |
| HP/Agilent AN 923, AN 986, AN 1089/1124 (background) | Schottky detector theory, package models | DET |
| B. Brannon, ADI AN-756 | jitter-limited SNR | RX |
| ADI AN-1363 (bias controllers) | bias sequencing | STAB |

## Secondary / community sources (used for context, not physics claims)
| Source | Used for | Pages |
|---|---|---|
| I. Rosu (VA3IUL), "Bias circuits for RF devices" (qsl.net) | BJT tempco, topologies, bias-loop oscillation | STAB |
| RTL-SDR community documentation (Uni Regensburg RTL2832U notes; M. Bavaro GNSS blog) | R820T IF and RTL2832U ADC details | RX |
| Microwaves & RF product news (VidaRF drop-in circulator) | UHF circulator example specs | CIRC |

## Added by W5-E7 (2026-10)
| Source | Type | Used for | Pages |
|---|---|---|---|
| A. Hajimiri, T. H. Lee, "A general theory of phase noise in electrical oscillators," *IEEE JSSC* 33(2), 179–194, 1998 (read) | peer-reviewed | ISF, LTV phase noise, 1/f³ corner, cyclostationary noise | ISF |
| T. H. Lee, A. Hajimiri, "Oscillator phase noise: a tutorial," *IEEE JSSC* 35(3), 326–336, 2000 (read) | peer-reviewed | tank-form phase noise (2kT/P), Leeson-modified form | ISF |
| E. Rubiola, *Phase Noise and Frequency Stability in Oscillators*, CUP, 2008 | textbook | Leeson FkT/(2Ps) form (per W4-D6) | ISF |
| A. Demir, A. Mehrotra, J. Roychowdhury, *IEEE TCAS-I* 47(5), 2000 | peer-reviewed | Lorentzian line shape | ISF |
| E. Hegazi, H. Sjöland, A. Abidi, *IEEE JSSC* 36(12), 2001 | peer-reviewed | tail-noise filtering | ISF |
| J. R. Vig, quartz resonator/oscillator tutorial, rev. 8.5.2.0, 2004 (read) | tutorial | g-sensitivity, vibration-induced sidebands | ISF |
| NASA GSFC-STD-7000 (GEVS) random-vibration envelope | standard | rocket vibration profile | ISF |
| Semtech SX1276/77/78/79 data sheet rev. 4 (read) | datasheet | AGC triggers, LNA gain table, RSSI formulas | AGC |
| Semtech SX1261/2 data sheet (read) | datasheet | RssiPkt/SnrPkt, RampTime | AGC, PAC |
| ADI AD9361 UG-570; AD8367/AD8368 data sheets (search summaries only) | app note / datasheet | AGC modes, loop time constant | AGC |
| B. Widrow et al., *Proc. IEEE* 63(12), 1975; S. F. Boll, *IEEE Trans. ASSP* 27(2), 1979 | peer-reviewed | LMS line enhancer/notch; spectral subtraction | AGC |
| R. G. Lyons, *Understanding DSP*, 3rd ed., §13.30 | textbook | digital AGC | AGC |
| Tohtsu CX-140D / CX-600NC, Teledyne RF3xx relay data (search summaries) | vendor | relay operate/release times | PAC |
| A. Grebennikov, *RF and Microwave PA Design*, 2nd ed.; F. H. Raab et al., *IEEE T-MTT* 50(3), 2002 | textbook / peer-reviewed | class D (VMCD/CMCD), switching PAs | PAC |
| W. Hayward, "Designing narrow-bandwidth ladder filters," 2019 (read); Hayward, Campbell, Larkin, *EMRFD*, ARRL 2003 | notes / handbook | crystal ladder k–q method, C0 narrowing, G3UUR | DUP |
| M. Dishal, *Proc. IRE* 37(9) 1949 and 39(11) 1951; S. B. Cohn, *Proc. IRE* 47(8) 1959 | peer-reviewed | coupled-resonator design and alignment; min-loss design | DUP |
| A. I. Zverev, *Handbook of Filter Synthesis*, 1967 | textbook | crystal filters | DUP |
| repeater-builder.com duplexer guide; W6NBC *The Cavity Duplexer*; BCD-440, Jiesai vendor specs (search summaries) | ham / vendor | repeater duplexer figures | DUP |
| Sanan RBD0943G4G band-8 TC-SAW duplexer (search summary) | datasheet | SAW duplexer isolation/loss | DUP |
| Murata SFELF10M7FA00, CFWLA455KBFA (search summaries) | datasheet | ceramic IF filter specs | DUP |
| ITU-R Report M.2244 (2011) (read) | standard/report | antenna isolation formulas and tables | COS |
| ETSI EN 300 086 V2.1.2 §7.7 (read) | standard | transmitter intermodulation attenuation 40/70 dB | COS |
| W. B. Davenport, *J. Appl. Phys.* 24(6), 1953 | peer-reviewed | hard-limiter weak-signal suppression | COS |
| MIL-HDBK-237D; ITU-R SM.337 (via M.2244) | standard | co-site framework; separation validity | COS |
| H. L. Krauss, C. W. Bostian, F. H. Raab, *Solid State Radio Engineering*, 1980; K. K. Clarke, D. T. Hess, *Communication Circuits*, 1971; S. Haykin, M. Moher, *Communication Systems*, 5th ed. | textbooks | modulators, envelope detector, discriminators | MOD |
| E. H. Armstrong, *Proc. IRE* 24(5), 1936 | peer-reviewed | indirect FM | MOD |
| H. Bosma, *Philips Res. Rep. Suppl.* 10, 1967 | report | noise correlation C = kT(I − SS^H) | CPL |
| H. S. Black, US 1,686,792 (1928); H. Seidel, *BSTJ* 50(9), 1971; P. B. Kenington, *High-Linearity RF Amplifier Design*, 2000 | patent / peer-reviewed / textbook | feedforward | PA |
| V. Petrovic, C. N. Smith (1983); M. Johansson, L. Sundström, *Electron. Lett.* 30(14), 1994 | conference / peer-reviewed | Cartesian feedback | PA |
| H. Chireix, *Proc. IRE* 23(11), 1935; D. C. Cox, *IEEE Trans. Commun.* 22(12), 1974; L. R. Kahn, *Proc. IRE* 40(7), 1952 | peer-reviewed | outphasing, LINC, EER | PA |
