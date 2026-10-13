# 03-transmission-lines-matching — bibliography

Full citations for the sources used across this domain, grouped by type. "Pages" lists which KB pages
rely on each. Reliability tags follow CONVENTIONS.md. Accessed 2026-09-27 unless stated.

## Textbooks
| # | Citation | Used for | Pages |
|---|---|---|---|
| T1 | D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012. Ch. 2 (TL theory, Smith chart, λ/4, lossy lines), ch. 3 (coax, stripline, microstrip incl. synthesis eq. 3.197), ch. 4 (S, ABCD, flow graphs, power waves), ch. 5 (matching: L-networks, stubs, λ/4, multisection binomial/Chebyshev, tapers incl. Klopfenstein, Bode–Fano), ch. 6 (resonators), ch. 12 (gains, stability). | core derivations | all |
| T2 | R. E. Collin, *Foundations for Microwave Engineering*, 2nd ed., McGraw-Hill 1992 / IEEE Press 2001. | TEM lines, transformers | telegrapher, reflections, stubs, matching |
| T3 | S. J. Orfanidis, *Electromagnetic Waves and Antennas*, Rutgers University, free online (rev. 2016) — chapters "Transmission Lines", "Impedance Matching", "S-Parameters" (chapter numbers differ between revisions). https://eceweb1.rutgers.edu/~orfanidi/ewa/ | free derivations | telegrapher, reflections, stubs, matching |
| T4 | M. Steer, *Microwave and RF Design*, Vols. II (Transmission Lines) and III (Networks), 3rd ed., NC State University Libraries, 2019 (open access; LibreTexts mirror). | free derivations | telegrapher, stubs |
| T5 | G. L. Matthaei, L. Young, E. M. T. Jones, *Microwave Filters, Impedance-Matching Networks, and Coupling Structures*, McGraw-Hill 1964 / Artech 1980. | exact Chebyshev transformers, finite-n Fano matching | matching, Bode–Fano |
| T6 | C. Bowick, *RF Circuit Design*, 2nd ed., Newnes 2008. | L/Pi/T via virtual resistance | matching |
| T7 | G. Gonzalez, *Microwave Transistor Amplifiers*, 2nd ed., Prentice Hall 1997. | Smith chart as bilinear map, circles | Smith chart |
| T8 | S. C. Cripps, *RF Power Amplifiers for Wireless Communications*, 2nd ed., Artech 2006. | load-line vs conjugate match | matching |
| T9 | B. C. Wadell, *Transmission Line Design Handbook*, Artech House 1991. | formula survey | planar lines, stubs |
| T10 | K. C. Gupta, R. Garg, I. Bahl, P. Bhartia, *Microstrip Lines and Slotlines*, 2nd ed., Artech 1996. | microstrip limits, surface waves | planar lines |
| T11 | R. N. Simons, *Coplanar Waveguide Circuits, Components, and Systems*, Wiley 2001. | CPW/CPWG | planar lines |
| T12 | H. W. Bode, *Network Analysis and Feedback Amplifier Design*, Van Nostrand 1945. | gain–bandwidth limit | Bode–Fano |
| T13 | J. A. Dobrowolski, *Scattering Parameters in RF and Microwave Circuit Analysis and Design*, Artech 2016, pp. 65–68. | T-parameter convention (scikit-rf) | s-parameters |
| T14 | G. F. Engen, *Microwave Circuit Theory and Foundations of Microwave Metrology*, Peregrinus 1992. | mismatch factor, reflectometers | Mason |
| T15 | A. V. Oppenheim, R. W. Schafer, *Discrete-Time Signal Processing*, 3rd ed., 2010. | Kaiser window | TDR |
| T16 | P. H. Smith, *Electronic Applications of the Smith Chart*, McGraw-Hill 1969; original: "Transmission line calculator," *Electronics* 12, 29–31, Jan 1939. | Smith chart | Smith chart |
| T17 | P. J. Nahin, *Oliver Heaviside: The Life, Work, and Times of an Electrical Genius of the Victorian Age*, Johns Hopkins 2002. | history: telegrapher eqs., loading | telegrapher |
| T18 | M. W. Maxwell (W2DU), *Reflections: Transmission Lines and Antennas*, ARRL 1990 (later eds. CQ/WorldRadio). | reflected-power debate (contested in places) | reflections |

## Peer-reviewed papers and standards
| # | Citation | Used for | Pages |
|---|---|---|---|
| P1 | K. Kurokawa, "Power waves and the scattering matrix," *IEEE Trans. MTT* 13(2):194–202, 1965. | power waves | s-parameters, reflections |
| P2 | R. B. Marks, D. F. Williams, "A general waveguide circuit theory," *J. Res. NIST* 97(5):533–562, 1992, doi:10.6028/jres.097.024 (free). | pseudo-waves | s-parameters, reflections |
| P3 | D. A. Frickey, "Conversions between S, Z, Y, h, ABCD, and T parameters which are valid for complex source and load impedances," *IEEE Trans. MTT* 42(2):205–211, 1994. | conversions | s-parameters |
| P4 | D. E. Bockelman, W. R. Eisenstadt, "Combined differential and common-mode scattering parameters," *IEEE Trans. MTT* 43(7):1530–1539, 1995. | mixed-mode S | s-parameters |
| P5 | J. M. Rollett, "Stability and power-gain invariants of linear twoports," *IRE Trans. CT* 9(1):29–32, 1962. | K factor | s-parameters |
| P6 | M. L. Edwards, J. H. Sinsky, "A new criterion for linear 2-port stability using geometrically derived parameters," *IEEE Trans. MTT* 40(12):2303–2311, 1992. | μ factor | s-parameters, Smith chart |
| P7 | R. M. Foster, "A reactance theorem," *BSTJ* 3:259–267, 1924. | clockwise rule, Bode–Fano | Smith chart, Bode–Fano |
| P8 | R. M. Fano, "Theoretical limitations on the broadband matching of arbitrary impedances," *J. Franklin Inst.* 249:57–83, 139–154, 1950. | Bode–Fano | Bode–Fano |
| P9 | L. J. Chu, "Physical limitations of omni-directional antennas," *J. Appl. Phys.* 19:1163–1175, 1948. | small-antenna Q | Bode–Fano |
| P10 | J. S. McLean, "A re-examination of the fundamental limits on the radiation Q of electrically small antennas," *IEEE Trans. AP* 44(5):672–676, 1996. | $Q=1/(ka)^3+1/ka$ | Bode–Fano |
| P11 | A. D. Yaghjian, S. R. Best, "Impedance, bandwidth, and Q of antennas," *IEEE Trans. AP* 53(4):1298–1324, 2005. | $Q_Z$, VSWR bandwidth | Bode–Fano |
| P12 | A. Shlivinski, Y. Hadad, "Beyond the Bode–Fano bound: wideband impedance matching for short pulses using temporal switching of transmission-line parameters," *Phys. Rev. Lett.* 121, 204301, 2018; arXiv:1805.03704. | time-varying exception | Bode–Fano |
| P13 | R. W. Klopfenstein, "A transmission line taper of improved design," *Proc. IRE* 44:31–35, 1956, doi:10.1109/JRPROC.1956.274847. | Klopfenstein taper | matching |
| P14 | D. Kajfez, J. O. Prewitt, "Correction to 'A transmission line taper of improved design'," *IEEE Trans. MTT* 21(5):364, 1973, doi:10.1109/TMTT.1973.1128003. | taper end values | matching |
| P15 | E. Hammerstad, Ø. Jensen, "Accurate models for microstrip computer-aided design," *IEEE MTT-S Digest*, 1980, pp. 407–409. | microstrip Z0/εeff | planar lines |
| P16 | E. O. Hammerstad, "Equations for microstrip circuit design," *Proc. 5th EuMC*, 1975, pp. 268–272. | simple forms, open-end extension | planar lines, stubs |
| P17 | H. A. Wheeler, "Transmission-line properties of a strip on a dielectric sheet on a plane," *IEEE Trans. MTT* 25(8):631–647, 1977; "… strip line between parallel planes," *IEEE Trans. MTT* 26(11):866–876, 1978. | Wheeler formulas | planar lines |
| P18 | M. Kirschning, R. H. Jansen, "Accurate model for effective dielectric constant of microstrip with validity up to millimetre-wave frequencies," *Electron. Lett.* 18(6):272–273, 1982; R. H. Jansen, M. Kirschning, *AEÜ* 37:108–112, 1983. | dispersion | planar lines |
| P19 | S. B. Cohn, "Characteristic impedance of the shielded-strip transmission line," *IRE Trans. MTT* 2:52–57, 1954. | exact stripline | planar lines, FD self-test |
| P20 | G. Ghione, C. Naldi, "Analytical formulas for coplanar lines in hybrid and monolithic MICs," *Electron. Lett.* 20(4):179–181, 1984; C. P. Wen, *IEEE Trans. MTT* 17:1087–1090, 1969. | CPW/CPWG | planar lines |
| P21 | T. S. Bird, "Definition and misuse of return loss," *IEEE AP Magazine* 51(2):166–167, 2009. | RL sign | reflections |
| P22 | S. J. Mason, "Feedback theory — some properties of signal flow graphs," *Proc. IRE* 41:1144–1156, 1953; "… further properties…," *Proc. IRE* 44:920–926, 1956. | Mason's rule | Mason |
| S1 | IBIS Open Forum, *Touchstone® File Format Specification*, v2.0 (2009) and v2.1 (ratified 26 Jan 2024), https://ibis.org/touchstone_ver2.1/touchstone_ver2_1.pdf | Touchstone | s-parameters |
| S2 | IPC-2141A, *Design Guide for High-Speed Controlled Impedance Circuit Boards*, 2004 (edge-coupled approximation, via secondary sources). | diff-pair estimate | planar lines |

## Application notes, manufacturer and software documentation
| # | Citation | Used for | Pages |
|---|---|---|---|
| A1 | Keysight, *S-Parameter Design*, AN 154 (5952-1087), 1990 — https://www.keysight.com/us/en/assets/7018-06743/application-notes/5952-1087.pdf | S-parameters, flow graphs | s-parameters, Mason |
| A2 | Keysight, *Time Domain Analysis Using a Network Analyzer*, AN 1287-12 (5989-5723EN) — http://literature.cdn.keysight.com/litweb/pdf/5989-5723EN.pdf (read via a distributor copy) | TDR windows, ranges, gating | TDR |
| A3 | Keysight, *Techniques for Time Domain Measurements*, AN 5991-0420EN, 2014. | band-pass fault location | TDR |
| A4 | Keysight, *Fundamentals of RF and Microwave Power Measurements, Part 3*, AN 1449-3 (not re-fetched). | uncertainty budgets | Mason |
| A5 | Tektronix, *TDR Impedance Measurements* (not re-fetched). | TDR shapes | TDR |
| A6 | Qucs Technical Papers (S. Jahn, M. Margraf et al.) — https://qucs.sourceforge.net/tech/ (microstrip node75; coplanar) | formula implementations | planar lines, stubs |
| A7 | scikit-rf 2.0.1 docs and source — https://scikit-rf.readthedocs.io/ (media.MLine, media.CPW, media.Coaxial, taper.Klopfenstein, tlineFunctions.zl_2_total_loss, Network.se2gmm/step_response/time_gate) | cross-checks | all |
| A8 | S. D. Stearns (K6OIK), "Transmission line power paradox and its resolution," ARRL Pacificon 2014 — https://www.fars.k6ya.org/docs/K6OIK-A_Transmission_Line_Power_Paradox_and_Its_Resolution.pdf | mismatched-line loss | reflections |
| A9 | JLCPCB: "Controlled impedance PCB layer stackup" https://jlcpcb.com/impedance; "User guide to the JLCPCB impedance calculator" https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator; standard 2-layer stackup page https://jlcpcb.com/resources/custom-pcb | stackups, mask, Dk | planar lines |
| A10 | JITX docs, `jitxlib.jlcpcb.JLC04161H_7628` — https://docs.jitx.com/en/latest/jitxlib/jitxlib.jlcpcb.JLC04161H_7628.html | published JLC routing widths | planar lines |
| A11 | Microwaves101, "Why fifty ohms?" — https://www.microwaves101.com/encyclopedias/why-fifty-ohms | 50 Ω history | coax |
| A12 | Times Microwave, "Current innovations in phase stable coaxial cable design"; Microwave Journal, "Minimizing temperature induced phase errors in coaxial cables" (2017). | PTFE knee | coax |
| A13 | WA5OKO, *NanoVNA User Guide* (2020) https://amris.mbi.ufl.edu/wordpress/files/2021/01/NanoVNA-User-Guide.pdf; PA3A, *Smith Chart in the nanoVNA* (2022) https://pa3a.nl/wp-content/uploads/2022/07/Smith-Chart-in-the-nanoVNA-2022-july-ENGLISH.pdf | NanoVNA formats | Smith chart |

## Datasheets
| # | Citation | Used for |
|---|---|---|
| D1 | L-com (Times Microwave data), LMR-400 / LMR-240 / LMR-195 datasheets, rev. 2019 — https://www.l-com.com/Images/Downloadables/Datasheets/ds_LMR-400.pdf (etc.) | coax loss, VF, power |
| D2 | Belden 8240 (RG-58) technical data sheet, rev. 0.541 (2026) — https://catalog.belden.com/techdata/EN/8240_techdata.pdf | RG-58 |
| D3 | Fairview Microwave RG174 (rev 1.4), RG316 (rev 1.5) datasheets | RG-174, RG-316 |
| D4 | Pasternack RG402/U, RG405/U datasheets | semi-rigid |
| D5 | Hirose Electric, *U.FL Series* catalog (2020) | U.FL, micro-coax |
| D6 | Murata LQW15AN / LQG15HS product listings (Q ratings) | component Q |

## Forums / blogs (for "common mistakes" only)
| # | Citation | Used for |
|---|---|---|
| F1 | IZ2UUF, "The myth of reflected power" (2017), "The myth of SWR causing coax radiation" (2016), iz2uuf.net | reflected-power myths (measurement-based blog) |
| F2 | worldwidedx.com "Does cable length affect SWR?"; shop.rf.guru "Does feedline length matter" | SWR-vs-length confusion |
| F3 | ResearchGate / EE Q&A "why is 50 Ω cable real but the multimeter reads infinite" | ohmmeter confusion |
| F4 | LibreCAL GitHub PR #8 (jankae/LibreCAL) | JLC CPWG practice |

## Verification scripts (this KB)
`tools/verify/tline_telegrapher.py`, `tline_reflections.py`, `tline_input_impedance.py`, `tline_smith.py`,
`tline_matching.py`, `tline_bode_fano.py`, `tline_sparams.py`, `tline_fd2d.py`, `tline_microstrip.py`,
`tline_cpwg.py`, `tline_coax.py`, `tline_tdr.py`, `tline_mason.py` (cross-check: `em_inductance.py` by W1-A3).

## Added by W5-E10 (2026-10-12) — antenna-tuners-and-atus
- ARRL, *The ARRL Antenna Book*, 24th ed., 2019 — transmatches, L/T/Pi networks, high-SWR feedline loss. (handbook; background)
- OZ9F/N7DDC, *ATU-100 Extended Board* technical description — 7 L/7 C relay L-network, retune threshold SWR 1.3, ≥ 5 W to tune. http://www.oz9f.dk/wp-content/uploads/2020/02/ATU-100_Extended_Board_User_Manual_eng.pdf (designer manual)
- Icom America, IC-7300 specifications — internal tuner 16.7–150 Ω (SWR < 3:1). (manufacturer)
- Verification: `tools/verify/e10_tuner_loss.py` (ALL PASS).

## Added by W5-E11 (microstrip-discontinuities)
- M. Kirschning, R. H. Jansen, N. H. L. Koster, *Electronics Letters* 17(3):123–125, 1981 (open end); *IEEE MTT-S Digest* 1983, pp. 495–497 (corner, mitred bend, gap). (peer-reviewed; via Qucs)
- S. Jahn et al., *Qucs Technical Papers* §11 (microstrip components) and qucs-core `ms*.cpp` sources — https://qucs.sourceforge.net/tech/node74.html. (open-source documentation)
- K. C. Gupta, R. Garg, I. Bahl, P. Bhartia, *Microstrip Lines and Slotlines*, 2nd ed., Artech 1996 (step, bend, gap, T). (textbook)
- R. J. P. Douville, D. S. James, *IEEE Trans. MTT* 26(3):175–182, 1978 (optimum mitre). (peer-reviewed; via Wikipedia raw text + leleivre.com calculator)
- E. Hammerstad, *IEEE MTT-S Digest* 1981, pp. 54–56 (T-junction, open end). M. E. Goldfarb, R. A. Pucel, *IEEE MGWL* 1(6), 1991 (via). (peer-reviewed)
- Verification: `tools/verify/e11_discontinuities.py` (15/18), `tools/verify/e11_discontinuities_openems.py` (openEMS; results file `e11_discontinuities_openems_results.txt`).
