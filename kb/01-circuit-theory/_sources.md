# 01-circuit-theory — Sources

Consolidated bibliography for the circuit-theory domain. Reliability tags per CONVENTIONS §3. "Used in" lists the pages that cite each item.

## Textbooks
| # | Citation | Used for | Used in |
|---|---|---|---|
| T1 | D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012. | Impedance/admittance, power waves, Z/Y/ABCD/S matrices (Tables 4.1–4.2), resonators and Q (ch. 6), filter insertion-loss method, g-value tables, transformations (ch. 8), noise figure of two-ports (ch. 12), complex Poynting theorem (§1.6). (textbook) | all pages |
| T2 | C. Bowick, J. Blyler, C. Ajluni, *RF Circuit Design*, 2nd ed., Newnes, 2008. | Component reactance, resonant circuits, loaded Q, L-network Q/bandwidth, tapped-C/tapped-L transformation, stress in matching networks. (textbook) | lumped, resonance, transformers, reactive power |
| T3 | J. B. Hagen, *Radio-Frequency Electronics: Circuits and Applications*, 2nd ed., Cambridge UP, 2009. | Impedance, resonant and coupled circuits, transformers. (textbook) | lumped, resonance, transformers |
| T4 | R. Ludwig, G. Bogdanov, *RF Circuit Design: Theory and Applications*, 2nd ed., Pearson, 2009. | Lumped vs distributed; two-port interconnections and conversion tables. (textbook) | lumped, two-port |
| T5 | G. L. Matthaei, L. Young, E. M. T. Jones, *Microwave Filters, Impedance-Matching Networks, and Coupling Structures*, McGraw-Hill 1964 / Artech 1980. | g-value formulas and tables (§4.05), max-flat-delay (§4.07), dissipation loss (§4.13), coupled-resonator band-pass (ch. 8). (textbook) | filter, resonance |
| T6 | A. I. Zverev, *Handbook of Filter Synthesis*, Wiley, 1967. | Elliptic and Bessel tables, normalisation conventions. (textbook) | filter |
| T7 | A. B. Williams, F. J. Taylor, *Electronic Filter Design Handbook*, 4th ed., McGraw-Hill, 2006. | Order selection, delay and step responses of filter families. (textbook) | filter, transient |
| T8 | J.-S. Hong, M. J. Lancaster, *Microstrip Filters for RF/Microwave Applications*, 2nd ed., Wiley, 2011. | J/K inverters, coupled-resonator synthesis, coupling-coefficient extraction. (textbook) | filter, transformers |
| T9 | S. C. Cripps, *RF Power Amplifiers for Wireless Communications*, 2nd ed., Artech House, 2006. | Load-line vs conjugate match; output-network loss. (textbook) | network theorems, reactive power |
| T10 | G. Gonzalez, *Microwave Transistor Amplifiers: Analysis and Design*, 2nd ed., Prentice Hall, 1997. | Noise vs gain match, noise circles. (textbook) | network theorems |
| T11 | A. Agarwal, J. H. Lang, *Foundations of Analog and Digital Electronic Circuits*, Morgan Kaufmann, 2005 (MIT 6.002). | KCL/KVL, node method, Thévenin/Norton, first/second-order transients. (textbook) | network theorems, transient |
| T12 | H. W. Johnson, M. Graham, *High-Speed Digital Design: A Handbook of Black Magic*, Prentice Hall, 1993. | Rise time–bandwidth, probe ground-lead ringing. (textbook) | transient |
| T13 | K. Ogata, *Modern Control Engineering*, 5th ed., Prentice Hall, 2010. | Second-order step response and overshoot. (textbook) | transient |
| T14 | A. S. Sedra, K. C. Smith, *Microelectronic Circuits*, 7th ed., Oxford UP, 2015. | h-parameter models, feedback two-port topologies. (textbook) | two-port |
| T15 | J. Sevick, *Transmission Line Transformers*, 4th ed., Noble/SciTech, 2001. | Guanella/Ruthroff transformers. (textbook) | transformers |
| T16 | C. R. Paul, *Inductance: Loop and Partial*, Wiley-IEEE, 2010. | Mutual inductance, energy bound on k. (textbook) | transformers |
| T17 | W. Hayward, R. Campbell, B. Larkin, *Experimental Methods in RF Design*, ARRL, 2003. | Resonator Q measurement, filter loss vs Q. (textbook) | resonance |
| T18 | M. B. Steer, *Microwave and RF Design* (vols I–IV, "Modules"), NC State / LibreTexts, 2019–2026. §2.7 Butterworth and Chebyshev filters. https://eng.libretexts.org/Bookshelves/Electrical_Engineering/Electronics/Microwave_and_RF_Design_IV:_Modules_(Steer)/02:_Filters/2.07:_Butterworth_and_Chebyshev_Filters (textbook, open access) | Closed-form Butterworth/Chebyshev g-values. | lumped, filter |

## Peer-reviewed papers and classic reports
| # | Citation | Used for |
|---|---|---|
| P1 | R. M. Foster, "A reactance theorem," *Bell Syst. Tech. J.*, 3(2), 259–267, 1924. | Monotonic reactance of lossless one-ports. |
| P2 | K. Kurokawa, "Power waves and the scattering matrix," *IEEE Trans. MTT*, 13(2), 194–202, 1965. | Power-wave reflection coefficient, mismatch factor. |
| P3 | D. A. Frickey, "Conversions between S, Z, Y, h, ABCD, and T parameters which are valid for complex source and load impedances," *IEEE Trans. MTT*, 42(2), 205–211, 1994. | Conversion formulas, T-parameter conventions. |
| P4 | S. B. Cohn, "Dissipation loss in multiple-coupled-resonator filters," *Proc. IRE*, 47(8), 1342–1348, 1959. | Mid-band loss $4.343\sum g/(\mathrm{FBW}Q_u)$. |
| P5 | B. D. H. Tellegen, "A general network theorem, with applications," *Philips Res. Rep.*, 7, 259–269, 1952. | Complex power balance. |
| P6 | L. J. Chu, "Physical limitations of omni-directional antennas," *J. Appl. Phys.*, 19, 1163–1175, 1948. | Minimum Q of small antennas (reactive power example). |
| P7 | G. Guanella, "Novel matching systems for high frequencies," *Brown-Boveri Review*, 31, 327–329, 1944; C. L. Ruthroff, "Some broad-band transformers," *Proc. IRE*, 47(8), 1337–1342, 1959. | Transmission-line transformers. |
| P8 | L. W. Nagel, "SPICE2: A computer program to simulate semiconductor circuits," UC Berkeley ERL-M520, 1975. (technical report) | Modified nodal analysis. |

## Application notes, lecture notes, datasheets
| # | Citation | Used for |
|---|---|---|
| A1 | Stanford EE133, "Cookbook Filter Guide," Winter 2002. https://web.stanford.edu/class/ee133/handouts/labs/EE133filterCookbook.pdf (lecture notes) | Butterworth/Chebyshev/Bessel tables; Bessel delay normalisation (verified). |
| A2 | Keysight, "Understanding oscilloscope frequency response and its effect on rise-time accuracy," AN 5988-8008; "Evaluating oscilloscope bandwidths for your application," AN 5989-5733. https://www.keysight.com/us/en/assets/7018-01129/application-notes/5988-8008.pdf (app note) | 0.35 vs 0.4–0.45 rise-time products. |
| A3 | S. C. Cripps, "High efficiency PA" tutorial, WAMICON 2005. http://wami.eng.usf.edu/conferences/wamicon/2005/electronic-materials/tutorials/RA-1-High-Effic-Cripps.pdf (tutorial) | Load-line match. |
| A4 | All About Circuits, "Using the load-pull technique in RF power amplifier design" (technical article). https://www.allaboutcircuits.com/technical-articles/load-line-analysis-estimating-load-pull-contours-of-an-rf-power-amplifier/ (article) | $R_{opt}\approx(V_{DD}-V_{knee})^2/2P$. |
| A5 | Coilcraft, "Chip inductors — 0402HP series (1005)," Doc 526, rev. 12/20/2023. https://www.coilcraft.com/getmedia/54459dcc-b821-4a9d-b91e-0416ea86a9b2/0402hp.pdf (datasheet) | Inductor Q, Irms, TCL used in examples. |
| A6 | Johanson Technology, "Multi-layer high-Q capacitors" catalog, 2022. https://www.johansontechnology.com/docs/2818/johanson-technology-multi-layer-high-q-capacitors8--4-2022_VRkwKZd.pdf (datasheet) | RF current ratings of high-Q MLCCs. |
| A7 | scikit-rf documentation v2.0. https://scikit-rf.readthedocs.io (software docs) | Conversion functions, T convention, media elements. |

## Forum / anecdotal (misconceptions only)
| # | Citation | Used for |
|---|---|---|
| F1 | "The maximum power transfer theorem," All About Circuits forum thread (2023). https://forum.allaboutcircuits.com/threads/the-maximum-power-transfer-theorem.193575/ (forum — anecdotal) | The "50 % efficiency" confusion. |
| F2 | "Impedance matching — why?" All About Circuits forum thread (2016). https://forum.allaboutcircuits.com/threads/impedance-matching-why.127173/ (forum — anecdotal) | Conjugate vs efficiency confusion. |

## Verification scripts (this KB)
`tools/verify/circuits_impedance_basics.py`, `circuits_power_transfer.py`, `circuits_resonance_q.py`, `circuits_filter_prototypes.py`, `circuits_two_port.py`, `circuits_transformers.py`, `circuits_transient.py`, `circuits_reactive_power.py`.
