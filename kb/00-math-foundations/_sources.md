# 00-math-foundations — Sources

Consolidated bibliography for the maths-foundations domain. Each entry: full citation, URL if public, what it supports (→ pages), and reliability. "Read" means the text was actually read (in full or the cited sections) during the research pass on 2026-09-27; "located" means the bibliographic record was confirmed but the text was not re-read; "recalled" means section numbers are from memory of the table of contents and should be verified before quoting. Page abbreviations: dB = decibels-and-log-units, CX = complex-numbers-and-phasors, FT = fourier-series-and-transform, LB = laplace-transfer-functions-bode, LS = linear-systems-convolution, VC = vector-calculus-for-em, PR = probability-random-processes-and-psd, DE = differential-equations-circuits-waves, SF = special-functions-bessel-sinc, MX = matrices-and-linear-algebra-for-networks, NM = numerical-methods-overview, RM = math-roadmap-for-rf.

## Textbooks
| # | Citation | Supports | Status / reliability |
|---|---|---|---|
| T1 | A. V. Oppenheim, A. S. Willsky, S. H. Nawab, *Signals and Systems*, 2nd ed., Prentice Hall, 1997. §1.3, §2.1–2.4, §3.2–3.5, §4.3–4.5, §6.2, §6.5–6.6, ch. 8, ch. 9 (§9.2, §9.4, §9.7), ch. 11 | CX, FT, LB, LS, DE, RM | textbook; recalled section numbers (standard, high confidence) |
| T2 | A. V. Oppenheim, R. W. Schafer, *Discrete-Time Signal Processing*, 3rd ed., Pearson, 2010, ch. 12 (discrete Hilbert transforms) | LS | textbook; recalled |
| T3 | A. V. Oppenheim, G. C. Verghese, *Signals, Systems and Inference*, Pearson, 2015 (MIT 6.011 notes), ch. 9 random processes, ch. 10 PSD | PR, RM | textbook; located |
| T4 | R. N. Bracewell, *The Fourier Transform and Its Applications*, 3rd ed., McGraw-Hill, 2000 — chapters "The basic theorems", "The two domains", "The discrete Fourier transform and the FFT" | FT | textbook; chapter titles cited, numbers not verified |
| T5 | A. Papoulis, S. U. Pillai, *Probability, Random Variables and Stochastic Processes*, 4th ed., McGraw-Hill, 2002 | PR | textbook; ch. 9 General Concepts, 11 Spectral Representation, 12 Spectral Estimation confirmed from catalogue listings (W5-S18, 2026-10-13) |
| T6 | A. Papoulis, *The Fourier Integral and Its Applications*, McGraw-Hill, 1962 (Paley–Wiener) | LS | textbook; recalled |
| T7 | D. P. Bertsekas, J. N. Tsitsiklis, *Introduction to Probability*, 2nd ed., Athena Scientific, 2008 (MIT 6.041) | PR, RM | textbook; recalled |
| T8 | E. Kreyszig, *Advanced Engineering Mathematics*, 10th ed., Wiley, 2011 — ch. 1–2 ODEs, ch. 12 PDEs | DE, RM | textbook; ch. 1, 2, 12 titles confirmed (Wiley India product page) and §12.4 d'Alembert (NTNU course plan) (W5-S18, 2026-10-13) |
| T9 | D. J. Griffiths, *Introduction to Electrodynamics*, 4th ed., Pearson 2013 / Cambridge 2017 — ch. 1 (§1.2–1.6), §9.1, §9.4, §9.5 | VC, DE, RM | textbook; ch. 1 sections partly confirmed by search |
| T10 | F. T. Ulaby, U. Ravaioli, *Fundamentals of Applied Electromagnetics*, 7th ed., Pearson, 2015 — ch. 3 vector analysis | VC | textbook; recalled |
| T11 | J. D. Jackson, *Classical Electrodynamics*, 3rd ed., Wiley, 1999 — §7.10 Kramers–Kronig | LS | textbook; recalled (physics $e^{-i\omega t}$ convention) |
| T12 | S. J. Orfanidis, *Electromagnetic Waves and Antennas*, Rutgers (free online), ch. 1 (§1.10–1.15 material models, §1.17 Kramers–Kronig), ch. 15 (radiation fields, retarded potentials) | LS, VC, RM | textbook (free); 2016-edition ToC checked by W5-S18 on 2026-10-13 (§1.10–1.15, §1.17 and ch. 15 confirmed) |
| T13 | D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — §1.2, §1.6, §2.1, §2.2–2.3, §3.3, §4.2–4.4, conversion table (Table 4.2, number not verified) | CX, VC, DE, MX | textbook; section numbers checked against the Wiley ToC in gaps/D4-curriculum.md §3.1 (W5-S18, 2026-10-13); §4.1 → §4.2 corrected on the matrices page |
| T14 | C. R. Paul, *Introduction to Electromagnetic Compatibility*, 2nd ed., Wiley, 2006 — ch. 3 signal spectra | FT | textbook; via S7 |
| T15 | H. Taub, D. L. Schilling, *Principles of Communication Systems*, 2nd ed., McGraw-Hill, 1986 (FM/Carson); S. Haykin, *Communication Systems*, 4th ed., Wiley, 2001 | SF | textbooks; recalled — no ToC found for T&S 2nd ed. or Haykin 4th ed. section level (W5-S18, 2026-10-13); still unverified |
| T16 | C. A. Balanis, *Antenna Theory*, 4th ed., Wiley, 2016 — ch. 6 (§6.8 Dolph–Tschebyscheff), ch. 12 (apertures) | SF | textbook; checked against the Wiley ToC in gaps/D4-curriculum.md §3.2 (W5-S18, 2026-10-13) |
| T17 | G. Strang, *Introduction to Linear Algebra*, 5th ed., Wellesley-Cambridge, 2016 | MX, RM | textbook; recalled chapters |
| T18 | D. Tse, P. Viswanath, *Fundamentals of Wireless Communication*, Cambridge, 2005 — ch. 7 (MIMO capacity via SVD). https://web.stanford.edu/~dntse/papers/book121004.pdf | MX | textbook (free draft); located |
| T19 | H. L. Van Trees, *Optimum Array Processing*, Wiley, 2002; *Detection, Estimation, and Modulation Theory Part I* | MX, RM | textbooks; recalled |
| T20 | W. H. Press et al., *Numerical Recipes*, 3rd ed., Cambridge, 2007 | NM, RM | textbook; ch. 4, 9, 12, 13, 17, 20 confirmed against numerical.recipes contents (W5-S18, 2026-10-13) |
| T21 | A. Taflove, S. C. Hagness, *Computational Electrodynamics: The FDTD Method*, 3rd ed., Artech House, 2005 | NM, RM | textbook; recalled |
| T22 | R. F. Harrington, *Field Computation by Moment Methods*, Macmillan 1968 / IEEE Press 1993 | NM | textbook; recalled |
| T23 | J.-M. Jin, *The Finite Element Method in Electromagnetics*, 3rd ed., Wiley-IEEE, 2014 — ch. 3–4 1-D/2-D FEM, ch. 8 Vector Finite Elements, ch. 9 Absorbing Boundary Conditions | NM | textbook; chapter titles via publisher sample ToC/O'Reilly previews (search summaries) (W5-S18, 2026-10-13); ch. 9 corrected on the numerical-methods page |
| T24 | H. W. Bode, *Network Analysis and Feedback Amplifier Design*, Van Nostrand, 1945 | LB | textbook (historical); gain–phase integral verified numerically, text not read |
| T25 | S. W. Smith, *The Scientist and Engineer's Guide to DSP*, https://www.dspguide.com | FT | textbook (free) |
| T26 | OpenStax, *Calculus Volume 3*, 2016, §6.5, §6.7, §6.8. https://openstax.org/books/calculus-volume-3/pages/6-5-divergence-and-curl | VC | textbook (free) |

## Lecture notes and courses
| # | Citation | Supports | Status |
|---|---|---|---|
| L1 | H. R. Miller, *18.03 Supplementary Notes*, MIT, Spring 2012. https://math.mit.edu/classes/18.03/sup/sup0.pdf — §2–6, 8, 10, 12, 15, 16, 20, 21–28 | CX, LB, DE, RM | read (table of contents + preface via pdftotext) |
| L2 | D. Freeman, MIT 6.003 Signals and Systems, Fall 2011 (25 lectures; L6 Laplace, L8 convolution, L9 frequency response, L11 Bode, L12–13 feedback, L14–20 Fourier, L21–22 sampling, L23–24 modulation). https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/pages/lecture-notes/ | FT, LB, LS, RM | lecture list read |
| L3 | MIT 6.011 Signals, Systems and Inference (Spring 2018), lecture 18 "Power spectral density". https://ocw.mit.edu/courses/6-011-signals-systems-and-inference-spring-2018/ | PR, RM | slides read (text sparse) |
| L4 | B. Osgood, *Lecture Notes for EE 261: The Fourier Transform and its Applications*, Stanford. http://cau.ac.kr/~mhhgtx/courses/AdvancedMath/references/FTandApplications.pdf ; https://see.stanford.edu/Course/EE261 | FT, RM | located |
| L5 | E. Cheever, "The asymptotic Bode diagram: derivation of approximations," Swarthmore LPSA. https://lpsa.swarthmore.edu/Bode/BodeHow.html | LB | read; its "2nd-order peak 1/(2ζ)" is the value at ωₙ (see Contradictions) |
| L6 | Michigan State University EM Research Group, *EMC Module 3: Signals and Spectra*, §3.3 trapezoidal waveforms. https://www.egr.msu.edu/emrg/sites/default/files/content/module3_signals_and_spectra.pdf | FT | read (pdftotext) |
| L7 | University of Illinois ECE 330, Lecture 2 "Complex power" (2020). https://courses.grainger.illinois.edu/ece330/sp2020/lectures/ECE330_02.pdf | CX | located via search summary |
| L8 | MIT OCW 18.01, 18.02, 18.06, 6.041, 6.013 course pages (6.013 prerequisites: complex numbers, vector operators, matrices, calculus, RLC, Maxwell, Fourier) | RM | course pages located |

## Peer-reviewed papers
| # | Citation | Supports | Status |
|---|---|---|---|
| P1 | A. R. Djordjević, R. M. Biljić, V. D. Likar-Smiljanić, T. K. Sarkar, "Wideband frequency-domain characterization of FR-4 and time-domain causality," *IEEE Trans. EMC* 43(4):662–667, Nov. 2001. https://mtt.etf.bg.ac.rs/Mikrotalasna.Tehnika/Clanci/FR4_EMC_2001.pdf | LS | read in full (pdftotext); eqs. (2)–(7) re-derived/verified |
| P2 | J. R. Klauder, A. C. Price, S. Darlington, W. J. Albersheim, "The theory and design of chirp radars," *BSTJ* 39(4):745–808, 1960. https://archive.org/details/bstj39-4-745 | FT | located; chirp results verified numerically |
| P3 | S. O. Rice, "Mathematical analysis of random noise," *BSTJ* 23(3):282–332, 1944; 24(1):46–156, 1945. https://archive.org/details/bstj23-3-282 ; https://archive.org/details/bstj24-1-46 | PR | located; results verified numerically |
| P4 | C. L. Dolph, "A current distribution for broadside arrays which optimizes the relationship between beam width and side-lobe level," *Proc. IRE* 34(6):335–348, 1946. https://ieeexplore.ieee.org/document/1697083/ | SF | abstract; maths verified with scipy chebwin |
| P5 | C.-W. Ho, A. E. Ruehli, P. A. Brennan, "The modified nodal approach to network analysis," *IEEE Trans. Circuits Syst.* 22(6):504–509, 1975. https://web.engr.oregonstate.edu/~karti/ece521/mna.pdf | MX | metadata/abstract |
| P6 | K. S. Yee, "Numerical solution of initial boundary value problems involving Maxwell's equations in isotropic media," *IEEE Trans. AP* 14(3):302–307, 1966, doi:10.1109/TAP.1966.1138693; stability corrected by A. Taflove, M. E. Brodwin, *IEEE Trans. MTT* 23(8):623–630, 1975 | NM | metadata via search; FDTD behaviour verified with own 1-D code |
| P7 | J. W. Cooley, J. W. Tukey, "An algorithm for the machine calculation of complex Fourier series," *Math. Comp.* 19(90):297–301, 1965 | NM | recalled citation |
| P8 | T. Liebig, A. Rennings, S. Held, D. Erni, "openEMS – a free and open source equivalent-circuit (EC) FDTD simulation platform…," *Int. J. Numerical Modelling*, 2013 | NM | located (volume/pages not verified) |
| P9 | F. H. Read, "Improved extrapolation technique in the boundary element method to find the capacitances of the unit square and cube," *J. Comput. Phys.* 133:1–5, 1997 (0.3667874·4πε₀L); E. Goto, Y. Shi, N. Yoshida, *J. Comput. Phys.* 100:105–115, 1992 (0.3667892) — both via S. Mukhopadhyay, N. Majumdar, arXiv:0704.1563 (2007) Table 2 | NM | table read (pdftotext); benchmark used in verify |

## Standards and reference works
| # | Citation | Supports | Status |
|---|---|---|---|
| S1 | B. N. Taylor, A. Thompson, NIST SP 811 (2008), §8.7 logarithmic quantities and units. https://www.nist.gov/pml/special-publication-811/nist-guide-si-chapter-8 | dB | read (§8.7) |
| S2 | ITU-R Recommendation P.526-14 (01/2018), *Propagation by diffraction*, §2.7 (eqs. 6–7), §4.1 (eqs. 26–31). https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.526-14-201801-I!!PDF-E.pdf | SF | read (pdftotext) |
| S3 | NIST *Digital Library of Mathematical Functions*, ch. 7, 10, 14, 18. https://dlmf.nist.gov | SF, PR, RM | reference; values cross-checked via scipy |
| S4 | 47 CFR §97.3(b) (definition of PEP). https://www.ecfr.gov/current/title-47/chapter-I/subchapter-D/part-97/subpart-A/section-97.3 | CX | definition text via search |

## Application notes, manufacturer documentation, trade articles
| # | Citation | Supports | Status |
|---|---|---|---|
| A1 | A. Winter, *dB or not dB?*, Rohde & Schwarz 1MA98 (v12e 2015; current v14e 2024). http://courses.ece.ubc.ca/elec391/1MA98_12e.pdf ; https://www.rohde-schwarz.com/appnote/1MA98 | dB, RM | read in full; two typos noted (Contradictions) |
| A2 | W. Kester, *MT-001* (SNR = 6.02N + 1.76 dB), Analog Devices. https://www.analog.com/media/en/training-seminars/tutorials/MT-001.pdf | dB | located |
| A3 | W. Kester, *MT-003* (SINAD, ENOB, SNR, THD, SFDR; dBFS vs dBc), Analog Devices. https://www.analog.com/media/en/training-seminars/tutorials/MT-003.pdf | dB | located |
| A4 | Keysight, *Spectrum Analyzers: Noise and Sensitivity* (3123-1734). https://www.keysight.com/us/en/assets/3123-1734/white-papers/Spectrum-Analyzers-Noise-and-Sensitivity.pdf | dB | search summary |
| A5 | Keysight E5080B help, "Group delay". https://helpfiles.keysight.com/csg/e5080b/Tutorials/Group_Delay6_5.htm | LB | read |
| A6 | Keysight AN 1287-3, *Applying Error Correction to Network Analyzer Measurements* | MX | recalled (model re-derived and verified) |
| A7 | A.H. Systems, "Antenna factor calculations and deviations." https://www.ahsystems.com/resources/articles/antenna-factor-calculations ; TDK antenna paper part 3 https://www.tti.com/content/dam/ttiinc/manufacturers/tdk/PDF/antenna_paper_part3.pdf | dB | search summary; constant re-derived (29.77 vs 29.79) |
| A8 | "GNSS Solutions: Measuring GNSS signal strength," *Inside GNSS*, Nov/Dec 2010. https://insidegnss.com/measuring-gnss-signal-strength/ | dB | read |
| A9 | R. Lyons, *Quadrature Signals: Complex, But Not Complicated* (2000; v2 2008). https://dspguru.com/dsp/tutorials/quadrature-signals/ | CX, RM | read (pdftotext, section headings + intro) |
| A10 | V. Dmitriev-Zdorov et al., "How to enforce causality of standard and 'custom' metal roughness models," *Signal Integrity Journal*, July 2020. https://www.signalintegrityjournal.com/articles/1796-how-to-enforce-causality-of-standard-and-custom-metal-roughness-models | LS | search summary; author from PDF filename |
| A11 | openEMS documentation. https://docs.openems.de/intro.html | NM | search summary |
| A12 | J. Jensen, "The concepts of noise bandwidth and cumulative noise." https://www.jensign.com/noisebandwidth/index.html | PR | search summary; ENBW re-derived |
| A13 | SciPy documentation (`scipy.special`, `scipy.signal.windows.chebwin`). https://docs.scipy.org/doc/scipy/reference/special.html | SF | software docs |

## Forum and community evidence (anecdotal — used only for "Common mistakes" and "Questions")
| # | Source | Used for |
|---|---|---|
| F1 | Physics Forums, "Confusion with dB equation — 10 or 20?" https://www.physicsforums.com/threads/confusion-with-db-equation-10-or-20.641850/ | dB: 10 vs 20 log confusion |
| F2 | All About Circuits, "dB level of summation of two sounds of unequal level." https://forum.allaboutcircuits.com/threads/db-level-of-summation-of-two-sounds-of-unequal-level.206535/ | dB: adding levels |
| F3 | EDAboard, "how to calculate EIRP with antenna gain in dBiC." https://www.edaboard.com/threads/how-to-calculate-eirp-with-antenna-gain-in-dbic.286680/ | dB: dBic vs dBi |
| F4 | Signal Processing Stack Exchange Q431, "What is the physical significance of negative frequencies?" https://dsp.stackexchange.com/questions/431 | CX: negative frequency |
| F5 | Physics Forums, "Intuition on divergence and curl." https://www.physicsforums.com/threads/intuition-on-divergence-and-curl.881895/ | VC: curl misconceptions |
| F6 | EmbeddedRelated, G. Kirilow, "Here comes the noise!" https://www.embeddedrelated.com/showarticle/1674.php | PR: RSS noise addition |

## Contradictions and corrections recorded against sources
- **R&S 1MA98 Table 6-1** lists the −3 dB voltage ratio as 0.798; correct value 0.708. Its §5.8 example swaps a unit label (dB(V/m) vs dB(µV/m)).
- **Reference temperature for −174 dBm/Hz**: R&S uses 293 K (−173.93 dBm/Hz); the KB uses T₀ = 290 K (−173.98). Both round to −174.
- **NIST SP 811 vs industry**: SI rules preclude "dBm"; industry/ITU use it universally.
- **Antenna-factor constant**: 29.77 dB/m with exact c; many references quote 29.79 (c = 3×10⁸ m/s rounding).
- **Second-order resonant peak**: Swarthmore notes (and many web sources) give the peak as 1/(2ζ) — that is $|H(j\omega_n)|$; the true maximum is $1/(2\zeta\sqrt{1-\zeta^2})$ at $\omega_n\sqrt{1-2\zeta^2}$.
- **Unit-square-plate capacitance**: Maxwell's 1878 estimate 0.3607·4πε₀L (40.14 pF for 1 m) is still quoted; accurate modern value 0.36679·4πε₀L = 40.81 pF (Goto 1992; Read 1997).
- **Uniform-array sidelobe**: −13.26 dB is the continuous-aperture (sinc) value; an 8-element uniform array's first sidelobe is −12.8 dB.

## Sources added by W5-E6 (2026-10-02/03) for the beginner pages
Page abbreviations: BC = rf-concepts-for-beginners, RL = rf-learning-roadmap. Verification: `tools/verify/e6_beginner_numbers.py` (43/43 PASS).

| # | Citation | Supports | Status / reliability |
|---|---|---|---|
| E1 | BIPM, *The International System of Units (SI Brochure)*, 9th ed., 2019 — exact $c$, $h$, $e$, $k$. https://www.bipm.org/en/publications/si-brochure | BC (λ, photon energy, kT, kTB) | standard; constants used numerically |
| E2 | M. Tschurlovits, "What is 'ionizing radiation'?", IAEA-CN-67/153, 1997 (ICRU 33, Attix 4–25 eV, BEIR ~34 eV/ion pair, EURATOM 100 nm ⇔ 12.4 eV). https://www.osti.gov/etdeweb/servlets/purl/593131 | BC §10 | conference paper; read (pdftotext) |
| E3 | ICNIRP 2020 RF guidelines, *Health Physics* 118(5):483–524 (heating as the established mechanism). | BC §10 | peer-reviewed guideline; via 19/rf-exposure-safety |
| E4 | ITU-R V.431-8 (2015), frequency-band nomenclature. | BC §1 | standard; recalled, not re-read |
| E5 | gaps/D2-reddit.md §2–§4 — community thread counts (53 learning-path threads, 1 006 comments, regex-counted) for books, videos, instruments and advice. | RL ("community consensus (n threads)") | internal gap analysis; ranking signal only |
| E6 | gaps/D4-curriculum.md §3 — fetched tables of contents (Pozar 4e, Balanis 4e, Razavi 2e, Lee CMOS 2e, Mailloux 3e, Richards 2e, Lyons 3e, AoE 3e, ARRL Handbook 96e structure, Antenna Book 24e, EMRFD, Skolnik 3e) and MIT 6.013/6.776/LL course maps. | RL (read-first chapters, Pozar → KB map) | internal; ToCs fetched by W4-D4 |
| E7 | D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley 2012 (international adaptation 2021). | RL | textbook; edition checked by search 2026-10-02 |
| E8 | ARRL, *ARRL Handbook*, 101st ed. (2024); *ARRL Antenna Book*, 25th ed. (2023). | RL | handbooks; editions checked by search 2026-10-02 |
| E9 | M. Steer, *Microwave and RF Design*, 3rd ed., 5 vols., NC State University Libraries, 2019, CC BY-NC 4.0. https://repository.lib.ncsu.edu/handle/1840.20/36776 | RL | open textbook; URL resolved 2026-10-02 |
| E10 | M. Lichtman, *PySDR*. https://pysdr.org ; S. W. Smith, *DSP Guide*. https://www.dspguide.com ; S. J. Orfanidis, *EWA*. https://eceweb1.rutgers.edu/~orfanidi/ewa/ | RL | free textbooks (Orfanidis server refuses scripts) |
| E11 | MIT OCW 6.013 (2009), 6.003 (2011), 6.450 (2006), 6.776 (2005), RES.LL-001 (2007), RES.LL-003 (2011) — URLs in RL Sources, all resolved 2026-10-02. | RL | lecture notes |
| E12 | Textbooks named in RL's book table: Balanis 4e (2016); Stutzman & Thiele 3e (2012); Hayward, Campbell & Larkin *EMRFD* (2003/2009); Horowitz & Hill 3e (2015); Bowick, Blyler & Ajluni 2e (2008); Lee *Planar Microwave Engineering* (2004) and *CMOS RFIC* 2e (2004); Razavi 2e (2011); Skolnik 3e (2001); Richards 2e (2014); Mailloux 3e (2018); Lyons 3e (2010); Bogatin 3e (2018); Ott (2009); Kaplan & Hegarty 3e (2017). | RL | textbooks; Bowick and Lee *Planar* chapter details recalled |
| E13 | Meshtastic docs, "Antenna testing" (refers to Andreas Spiess VNA tutorials) and "Getting started" (never power without an antenna). https://meshtastic.org/docs/ | RL, BC | project docs |

## Sources added by W5-E5 (2026-10-02/03) for the estimation pack
Page abbreviations: ZT = z-transform-and-discrete-time-systems, EST = estimation-theory-ml-map-crb, KF = kalman-filter-and-state-estimation. All formulas used were re-derived on the pages and verified in `tools/verify/est_ztransform.py`, `est_crb.py`, `est_kalman.py` (all ALL PASS).

| # | Citation | Supports | Status / reliability |
|---|---|---|---|
| Z1 | A. V. Oppenheim, R. W. Schafer, *Discrete-Time Signal Processing*, 3rd ed., Pearson, 2010 — ch. 3 (z-transform, ROC, inverse, unilateral), ch. 5 (transform analysis), §7.1–7.2 (impulse invariance, bilinear) | ZT | textbook; recalled section numbers (= T2) |
| Z2 | R. G. Lyons, *Understanding Digital Signal Processing*, 3rd ed., Prentice Hall, 2011 — §6.3–6.5 (z-transform, IIR analysis), ch. 10 (CIC), ch. 11 (exponential averager) | ZT | textbook; chapters recalled |
| Z3 | R. Schreier, G. C. Temes, *Understanding Delta-Sigma Data Converters*, Wiley-IEEE, 2005 — NTF/STF, in-band noise vs OSR | ZT | textbook; recalled; formula simulated |
| Z4 | E. B. Hogenauer, "An economical class of digital filters for decimation and interpolation," *IEEE Trans. ASSP* 29(2):155–162, 1981 | ZT | peer-reviewed; recalled; identity verified |
| Z5 | E. I. Jury, *Theory and Application of the z-Transform Method*, Wiley, 1964 | ZT (stability test) | textbook; recalled; 2nd-order case verified |
| Z6 | M. Rice, *Digital Communications: A Discrete-Time Approach*, Pearson, 2009, App. C (PLL loop-filter gains) | ZT | textbook; via 10-comms sync page |
| K1 | S. M. Kay, *Fundamentals of Statistical Signal Processing, Vol. I: Estimation Theory*, Prentice Hall, 1993 — ch. 2–4, 6–8, 10–13 | EST, KF | textbook; chapter structure recalled |
| K2 | Y. Bar-Shalom, X. R. Li, T. Kirubarajan, *Estimation with Applications to Tracking and Navigation*, Wiley, 2001 — ch. 2–3, 5 (KF, NEES/NIS §5.4), 6 (motion models, α-β), 10 (EKF) | EST, KF | textbook; recalled |
| K3 | D. Simon, *Optimal State Estimation*, Wiley, 2006 — ch. 5, 13, 14 | KF | textbook; recalled |
| K4 | P. D. Groves, *Principles of GNSS, Inertial, and Multisensor Integrated Navigation Systems*, 2nd ed., Artech House, 2013 — ch. 3, ch. 14 (INS/GNSS integration) | KF | textbook; recalled |
| K5 | R. E. Kalman, "A new approach to linear filtering and prediction problems," *J. Basic Eng.* 82(1):35–45, 1960, doi:10.1115/1.3662552 | KF | peer-reviewed; located |
| K6 | P. R. Kalata, "The tracking index: a generalized parameter for α-β and α-β-γ target trackers," *IEEE Trans. AES* 20(2):174–182, 1984 | KF | peer-reviewed; closed forms via Wikipedia summary, verified against DARE |
| K7 | T. R. Benedict, G. W. Bordner, *IRE Trans. Automatic Control* 7(4):27–32, 1962 | KF | peer-reviewed; relation compared numerically |
| K8 | W. T. Higgins, "A comparison of complementary and Kalman filtering," *IEEE Trans. AES* 11(3):321–325, 1975, doi:10.1109/TAES.1975.308081 | KF | peer-reviewed; abstract; equivalence verified numerically |
| K9 | S. J. Julier, J. K. Uhlmann, "Unscented filtering and nonlinear estimation," *Proc. IEEE* 92(3):401–422, 2004; E. A. Wan, R. van der Merwe, IEEE AS-SPCC 2000 | KF | peer-reviewed; recalled |
| K10 | C. F. Van Loan, "Computing integrals involving the matrix exponential," *IEEE Trans. Autom. Control* 23(3):395–404, 1978 | KF | peer-reviewed; recalled; method reproduced |
| K11 | Z. Chen et al., "Weak in the NEES?: Auto-tuning Kalman filters with Bayesian optimization," arXiv:1807.08855, 2018 | KF | peer-reviewed conference; search summary |
| K12 | D. C. Rife, R. R. Boorstyn, "Single-tone parameter estimation from discrete-time observations," *IEEE Trans. IT* 20(5):591–598, 1974 | EST | peer-reviewed; bounds re-derived and MC-verified |
| K13 | H. L. Van Trees, *Detection, Estimation, and Modulation Theory, Part I*, Wiley, 1968/2001 (= T19) — CRB, Bayesian bound, threshold | EST | textbook; recalled |
| K14 | MIT LL / IEEE NH *Radar Systems Course*, "Parameter estimation and tracking, Part 1" (2010) https://gmoein.github.io/files/MIT%20Graduate%20Radar%20Course/Radar%202009%20A_15%20Parameter%20Estimation%20and%20Tracking%20Part%201.pdf | EST | lecture notes; read as text |

**Convention note (EST, recorded for the consistency audit):** with a power-preserving complex envelope the complex-baseband matched-filter SNR equals E/N₀ and a coherent real matched filter's peak SNR is 2E/N₀ (agrees with 11-radar/ambiguity-function-waveforms); the convention note on 10-comms-modulation/matched-filter-detection uses a different scaling (Ẽ = 2E with N₀/2 per I and Q). Flagged, not edited.
