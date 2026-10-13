# 08-antennas — bibliography

Full citations for all sources used in `kb/08-antennas/`. Reliability tags follow CONVENTIONS §3.
"Read" = the text (or PDF via pdftotext) was read by the research agent; "cited" = relied on via
textbook/secondary summary. Pages that use each source are listed in brackets.

## Textbooks and handbooks
1. C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed., Wiley, 2016 — fundamental parameters (ch. 2), linear wires (4), loops (5), integral equations/MoM and mutual impedance (8), broadband dipoles/matching/baluns (9), Yagi (10), LPDA (11), apertures (12), horns incl. optimum design (13), microstrip (14), reflectors (15), measurements (17). (textbook; cited) [all pages]
2. J. D. Kraus and R. J. Marhefka, *Antennas for All Applications*, 3rd ed., McGraw-Hill, 2002 — beam solid angle and D ≈ 41 253/θφ, helices (normal and axial mode, gain/HPBW formulas), loops, apertures. (textbook; cited) [fundamentals, helical, loop, horn]
3. S. J. Orfanidis, *Electromagnetic Waves and Antennas*, Rutgers, 2016 (free online) — transmitting/receiving antennas, effective area, linear antennas (Si/Ci impedance), Hallén/Pocklington MoM, apertures. https://eceweb1.rutgers.edu/~orfanidi/ewa/ (textbook) [fundamentals, dipoles, loops, simulation, horn]
4. W. L. Stutzman and G. A. Thiele, *Antenna Theory and Design*, 3rd ed., Wiley, 2012; W. L. Stutzman, *Polarization in Electromagnetic Systems*, Artech, 1993 — polarization, PLF closed form. (textbooks; cited) [polarization]
5. J. L. Volakis (ed.), *Antenna Engineering Handbook*, 5th ed., McGraw-Hill, 2019 — incl. D. R. Jackson, ch. 7 "Microstrip Antennas". (handbook; cited via Jackson's notes) [patch]
6. R. Garg, P. Bhartia, I. Bahl, A. Ittipiboon, *Microstrip Antenna Design Handbook*, Artech, 2001; J. R. James and P. S. Hall (eds.), *Handbook of Microstrip Antennas*, IEE, 1989 — CP single-feed rules, stacked/aperture-coupled patches. (handbooks; cited secondarily) [patch]
7. R. W. P. King, *The Theory of Linear Antennas*, Harvard, 1956 — thickness parameter Ω, King–Middleton theory. (textbook; cited) [dipoles]
8. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — microstrip synthesis, surface waves. (textbook; cited) [patch]
9. ARRL, *The ARRL Antenna Book*, 24th ed., 2019 — dipole length vs diameter, EFHW, radials, loops, baluns. (handbook; cited) [dipoles, loops, baluns]
10. J. Sevick, *Transmission Line Transformers*, 4th ed., Noble, 2001 — Guanella/Ruthroff. (book; cited) [baluns]
11. R. F. Harrington, *Field Computation by Moment Methods*, 1968; W. C. Gibson, *The Method of Moments in Electromagnetics*, 2nd ed., CRC, 2014 — Galerkin MoM used in our scripts. (textbooks; cited) [simulation]
12. A. Taflove and S. C. Hagness, *Computational Electrodynamics: The FDTD Method*, 3rd ed., Artech, 2005. (textbook; cited) [simulation]
13. S. Silver (ed.), *Microwave Antenna Theory and Design*, MIT Rad. Lab. vol. 12, 1949 — paraboloid aperture efficiency. (textbook; cited via Balanis) [horn]
14. B. Rama Rao et al., *GPS/GNSS Antennas*, Artech, 2013; P. Misra and P. Enge, *GPS: Signals, Measurements, and Performance*, 2nd ed., 2006. (textbooks; cited) [gnss]
15. K.-L. Wong, *Planar Antennas for Wireless Communications*, Wiley, 2003. (textbook; cited) [pcb]

## Peer-reviewed papers
16. H. E. King and J. L. Wong, "Characteristics of 1 to 8 wavelength uniform helical antennas," *IEEE Trans. Antennas Propag.* AP-28(2), 291–296, 1980. https://astro.abhinav.ac.in/Literature/Antennae/king&wong_antenna%20characteristics.pdf (peer-reviewed; READ) [helical]
17. D. T. Emerson, "The gain of the axial-mode helix antenna," *ARRL Antenna Compendium* vol. 4, 64–68, 1995. https://www.cv.nrao.edu/~demerson/cs/helix.htm (peer-level; READ summary pages) [helical]
18. J. D. Kraus, "Helical beam antennas," *Electronics* 20, 109–111, 1947. (cited) [helical]
19. C. C. Kilgus, "Resonant quadrifilar helix," *IEEE TAP* AP-17, 349–351, 1969; "Shaped-conical radiation pattern performance of the backfire quadrifilar helix," AP-23, 392–397, 1975. (peer-reviewed; cited) [helical]
20. D. R. Jackson and N. G. Alexopoulos, "Simple approximate formulas for input resistance, bandwidth, and efficiency of a resonant rectangular patch," *IEEE TAP* 39(3), 407–410, 1991. (peer-reviewed; formulas READ via Jackson's notes) [patch]
21. E. O. Hammerstad, "Equations for microstrip circuit design," *Proc. 5th EuMC*, 268–272, 1975. (peer-reviewed; cited) [patch]
22. D. M. Pozar, "Rigorous closed-form expressions for the surface-wave loss of printed antennas," *Electron. Lett.* 26, 954–956, 1990. (peer-reviewed; cited via Jackson) [patch]
23. H. A. Wheeler, "Fundamental limitations of small antennas," *Proc. IRE* 35, 1479–1484, 1947; "The radiansphere around a small antenna," *Proc. IRE* 47, 1325–1331, 1959. (peer-reviewed; cited) [small-antenna-limits, measurement]
24. L. J. Chu, "Physical limitations of omni-directional antennas," *J. Appl. Phys.* 19, 1163–1175, 1948. (peer-reviewed; cited) [small-antenna-limits]
25. R. F. Harrington, "Effect of antenna size on gain, bandwidth, and efficiency," *J. Res. NBS* 64D, 1–12, 1960. (peer-reviewed; cited) [small-antenna-limits]
26. J. S. McLean, "A re-examination of the fundamental limits on the radiation Q of electrically small antennas," *IEEE TAP* 44(5), 672–676, 1996. (peer-reviewed; result VERIFIED numerically) [small-antenna-limits]
27. R. E. Collin and S. Rothschild, "Evaluation of antenna Q," *IEEE TAP* 12, 1964; H. L. Thal, "New radiation Q limits for spherical wire antennas," *IEEE TAP* 54(10), 2006; M. Gustafsson, C. Sohl, G. Kristensson, "Physical limitations on antennas of arbitrary shape," *Proc. R. Soc. A* 463, 2007. (peer-reviewed; cited) [small-antenna-limits]
28. A. D. Yaghjian and S. R. Best, "Impedance, bandwidth, and Q of antennas," *IEEE TAP* 53(4), 1298–1324, 2005. (peer-reviewed; cited) [fundamentals, small-antenna-limits]
29. S. R. Best, "A discussion on the significance of geometry in determining the resonant behavior of fractal and other non-Euclidean wire antennas," *IEEE APM* 45(3), 9–28, 2003. https://ieeexplore.ieee.org/document/1232160/ (peer-reviewed; abstract) [small-antenna-limits, pcb]
30. C.-T. Tai and C. S. Pereira, "An approximate formula for calculating the directivity of an antenna," *Proc. IEEE* 64(2), 235–236, 1976. (peer-reviewed; cited) [fundamentals]
31. R. L. Carrel, "The design of log-periodic dipole antennas," *IRE Int. Conv. Rec.* pt. 1, 61–75, 1961 (PDF at hamwaves.com/lpda/doc/carrel.1961.pdf); D. E. Isbell, "Log periodic dipole arrays," *IRE TAP* AP-8, 260–267, 1960; P. C. Butson and G. T. Thompson, "A note on the calculation of the gain of log-periodic dipole antennas," *IEEE TAP* AP-24, 105–106, 1976. (peer-reviewed; cited) [yagi]
32. H. Yagi, "Beam transmission of ultra short waves," *Proc. IRE* 16, 1928. (historical; cited) [yagi]
33. P. S. Carter, "Circuit relations in radiating systems...," *Proc. IRE* 20(6), 1932 — induced EMF. (cited) [dipoles]
34. G. Guanella, "Novel matching systems for high frequencies," *Brown-Boveri Rev.* 31, 1944; C. L. Ruthroff, "Some broad-band transformers," *Proc. IRE* 47, 1959. (cited) [baluns]
35. J. Ruze, "Antenna tolerance theory — a review," *Proc. IEEE* 54(4), 633–640, 1966. (cited) [horn]
36. W. E. McKinzie III, "A modified Wheeler cap method for measuring antenna efficiency," IEEE AP-S Symp., 1997. (peer-reviewed; abstract) [measurement]
37. K. Kinefuchi, K. Okita, I. Funaki, T. Abe, "Prediction of in-flight radio frequency attenuation by a rocket plume," *J. Spacecraft Rockets* 52(2), 2015. https://arc.aiaa.org/doi/10.2514/1.A32957 (peer-reviewed; abstract READ) [rockets]
38. P. C. Ribeiro Filho, A. F. Tinoco-S., D. C. Nascimento, J. C. da S. Lacava, "A telemetry antenna design for a sounding rocket competition," *IEEE APM* 59, 2017; "Flush-mounted telemetry antenna design for a sounding rocket competition," IEEE APS 2013. (peer-reviewed; abstract) [rockets, patch]

## Standards
39. IEEE Std 145-1993, *Definitions of Terms for Antennas* (current: 145-2013). https://www.ece.mcmaster.ca/faculty/nikolova/antenna_dload/IEEEStandard_AntennaTerms.pdf (standard; READ) [fundamentals, polarization, measurement]
40. IEEE Std 149-1979 (R2008), *Standard Test Procedures for Antennas*. (standard; cited) [measurement, polarization]
41. IS-GPS-200, *Navstar GPS Space Segment / Navigation User Interfaces* — L1 C/A minimum received power. https://www.gps.gov/technical/icwg/ (standard; cited) [fundamentals, gnss]
42. ITU-R P.372, *Radio noise*. (standard; cited) [loops]

## Manufacturer application notes, datasheets and manuals
43. TI DN007 (SWRU120D), *2.4-GHz Inverted F Antenna*. https://www.ti.com/lit/pdf/swru120 (app note; READ) [pcb]
44. TI DN023 (SWRA228), *868 MHz, 915 MHz and 955 MHz Inverted F Antenna*, F. Kervel. https://www.ti.com/lit/swra228 (app note; READ — note: the WebFetch summariser hallucinated this document's contents; values here are from the pdftotext of the PDF) [pcb]
45. TI DN024 (SWRA227), *Monopole PCB Antenna with Single or Dual Band Option*, R. Wallace. https://www.ti.com/lit/pdf/swra227 (app note; READ) [fundamentals, pcb, small-antenna-limits]
46. TI AN043 (SWRA117), *Small Size 2.4 GHz PCB antenna*, A. Andersen. https://www.ti.com/lit/pdf/swra117 (app note; READ) [pcb, baluns]
47. TI AN058 (SWRA161), *Antenna Selection Guide*, R. Wallace. https://www.ti.com/lit/pdf/swra161 (app note; READ; practice good, introductory physics loose) [fundamentals, pcb, small-antenna-limits, measurement]
48. u-blox, *GNSS antennas — RF design considerations for u-blox GNSS receivers*, UBX-15030289 R03, 2019. https://content.u-blox.com/sites/default/files/products/documents/GNSS-Antennas_AppNote_(UBX-15030289).pdf (app note; READ) [gnss, rockets, patch, polarization]
49. u-blox, *ZED-F9P Integration Manual*, UBX-18010802 R16. https://content.u-blox.com/sites/default/files/ZED-F9P_IntegrationManual_UBX-18010802.pdf (manual; READ antenna sections) [gnss]
50. u-blox, *MAX-M10S Integration Manual*, UBX-20053088. https://content.u-blox.com/sites/default/files/MAX-M10S_IntegrationManual_UBX-20053088.pdf (manual; search summary only — PDF exceeded fetch size) [gnss]
51. Johanson Technology, *433 MHz ISM Antenna SMD 0433AT62A0020E* datasheet v3.0, 2018. https://www.johansontechnology.com/datasheets/antennas/0433AT62A0020.pdf (datasheet; READ) [pcb]
52. Ignion, *TRIO mXTEND NN03-310 User Manual*, Dec 2025. https://ignion.io/files/UM_NN03-310.pdf (manual; READ performance tables) [pcb]
53. Espressif, *ESP Hardware Design Guidelines — ESP32-S3 PCB Layout Design*. https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html (guideline; READ) [pcb]
54. Fair-Rite Products, *43 Material Data Sheet* (and 31/61). https://fair-rite.com/43-material-data-sheet/ (manufacturer data; search level) [baluns]
55. Palomar Engineers, *Ferrite Mix Selection*. (vendor; practice) [baluns]
56. NASA GSFC Wallops, *NASA Sounding Rockets User Handbook*, 810-HB-SRP, July 2015 — §5.6 telemetry antennas, §5.9.3 GPS. https://www.nasa.gov/wp-content/uploads/2023/09/sounding-rocket-program-handbook.pdf (government handbook; READ) [rockets]
57. Altus Metrum, *Owner's Manual for Altus Metrum Rocketry Electronics*. https://altusmetrum.org/AltOS/doc/altusmetrum.html (manufacturer manual; READ antenna parts) [dipoles, rockets, yagi]

## Expert articles, design programs and tool documentation
58. G. Hoch (DL6WU), "Extremely long Yagi antennas," *VHF Communications* 3/1982; "More gain with Yagi antennas," 4/1977 — as implemented in *DL6WU.BAS* (KY4Z, W6NBI, G3SEK). http://www.ifwtech.co.uk/g3sek/diy-yagi/ (design data; program text READ; original articles not read) [yagi]
59. L. B. Cebik (W4RNL), articles at https://antenna2.github.io/cebik/ — "Appreciating DL6WU wide-band long-boom Yagi design", "When not to use NEC" (amod128), axial-mode helices, J-poles. (expert articles; READ selected) [yagi, simulation, dipoles, helical]
60. hamwaves.com, *Log-Periodic Dipole Array Calculator* documentation. https://hamwaves.com/lpda/en/index.html (design notes; READ) [yagi]
61. NEC-2 Manual Part III, Section II "Structure Modeling Guidelines" (Burke & Poggio, LLNL, 1981). https://www.nec2.org/part_3/secii.html (manual; READ) [simulation]
62. openEMS documentation — Simple Patch Antenna tutorial; NF2FF. https://docs.openems.de/python/openEMS/Tutorials/Simple_Patch_Antenna.html (tool docs; search level) [patch, simulation]
63. D. R. Jackson, "Introduction to Microstrip Antennas," U. Houston ECE 5318/6345 notes. https://courses.egr.uh.edu/ECE/ECE5318/Introduction%20to%20Microstrip%20Antennas.pdf (lecture notes; READ) [patch]
64. C. Counselman (W1HIS), "Common-Mode Chokes," YCCC draft, 2006. https://remoteqth.com/img/ZAW-WIKI/cmcc/CommonModeChokesW1HIS.pdf (expert article; READ summary) [baluns]
65. P. Wade (W1GHZ), *Online Microwave Antenna Book*; "Helical Feed Antennas," 2002. http://www.w1ghz.org/antbook/conf/Helical_feed_antennas.pdf (expert practice; cited) [horn]
66. RadioNugget, "Building a Quadrifilar Helical (QFH) Antenna" (137 MHz). https://radionugget.com/en/blog/qfh (hobbyist; practice only) [helical]

## Internal and cross-domain references
67. Space Bar avionics knowledge base (`~/.claude/knowledge/space-bar-avionics/`) — the reader's radios (E22-400T33D 433 MHz 2 W; E220-900T30D 900 MHz 1 W), GNSS (ZED-F9P with L1-only flown antenna; MAX-M10S U.FL). (internal) [fundamentals, rockets, gnss, pcb]
68. KB 02-electromagnetics: `boundary-conditions-reflection-refraction.md`, `dielectrics-permittivity-loss-tangent.md`, `tools/verify/em_fresnel_radome.py` — nose-cone wall and CFRP numbers. (KB) [rockets]

## W5-E2 additions (2026-10-02) — slot, HF wire, inductive/RFID/NFC/WPT, wideband, lens, identification pages
69. H. G. Booker, "Slot aerials and their relation to complementary wire aerials (Babinet's principle)," *J. IEE* IIIA 93(4), 620–626, 1946. https://digital-library.theiet.org/content/journals/10.1049/ji-3a-1.1946.0150 (peer-reviewed; abstract read: resonant slot ≈ 485 Ω) [slot]
70. P. Wade (W1GHZ), *Online Microwave Antenna Book*, ch. 7 "Slot antennas." http://www.w1ghz.org/antbook/ch7_part1.pdf — Stevenson 1948 conductance, Elliott–Kurtz lengths, Stegen data, WR-90 design sheet (expert article; READ via pdftotext) [slot]
71. A. F. Stevenson, "Theory of slots in rectangular waveguides," *J. Appl. Phys.* 19, 24–38, 1948; R. S. Elliott, *Antenna Theory and Design*, 1981 (cited via [70]) [slot]
72. Y. Yoshimura, "A microstripline slot antenna," *IEEE Trans. MTT* 20(11), 1972; D. M. Pozar, "Microstrip antenna aperture-coupled to a microstripline," *Electron. Lett.* 21(2), 1985; Y. Mushiake, "Self-complementary antennas," *IEEE APM* 34(6), 1992; H. W. Ott, *Electromagnetic Compatibility Engineering*, 2009 (cited) [slot, wideband]
73. L. Varney (G5RV), "The G5RV multiband antenna... up-to-date." http://www.popular-hifi.com/shack/ant_g5rv/g5rv.pdf (expert article; READ) [wire]
74. G. H. Brown, R. F. Lewis, J. Epstein, "Ground systems as a factor in antenna efficiency," *Proc. IRE* 25(6), 753–787, 1937 (peer-reviewed; cited via summaries) [wire]
75. J. C. Sprott, "Optimal length of random wire antenna," UW–Madison technote, 2012/2022. https://sprott.physics.wisc.edu/technote/randwire.htm (READ); VE3EED "best random wire lengths" list (club/forum — anecdotal; numerically evaluated) [wire]
76. A. Kurs et al., "Wireless power transfer via strongly coupled magnetic resonances," *Science* 317, 83–86, 2007 (peer-reviewed; abstract read) [inductive]
77. NXP, *AN11755 PN7150 Antenna Design and Matching Guide*, rev. 1.7, 2019. https://www.nxp.com/docs/en/application-note/AN11755.pdf (app note; READ) [inductive]
78. TI, *bq500212A* data sheet (WPC A5/A11 transmitter). https://www.ti.com/lit/ds/symlink/bq500212a.pdf (datasheet; READ) [inductive]
79. S. S. Mohan, M. Hershenson, S. Boyd, T. Lee, "Simple accurate expressions for planar spiral inductances," *IEEE JSSC* 34(10), 1419–1424, 1999 (peer-reviewed; read, coefficients checked numerically); F. W. Grover, *Inductance Calculations*, 1946 (cited); K. Finkenzeller, *RFID Handbook*, 3rd ed., 2010 (cited); A. P. Sample, D. T. Meyer, J. R. Smith, *IEEE TIE* 58(2), 2011 (cited); C. R. Valenta and G. D. Durgin, *IEEE Microwave Mag.* 15(4), 2014 (cited) [inductive]
80. S. Stearns (K6OIK), "All about the discone antenna," *QEX* Jan/Feb 2007 (expert article; READ via pdftotext) [wideband]
81. P. J. Gibson, "The Vivaldi aerial," 9th EuMC, 101–105, 1979 (abstract); V. H. Rumsey, *Frequency Independent Antennas*, 1966; J. D. Dyson, *IRE TAP* 7(2), 1959 (cited) [wideband]
82. R. K. Luneburg, *Mathematical Theory of Optics*, 1944/1964; D. G. Berry, R. G. Malech, W. A. Kennedy, *IEEE TAP* 11(6), 1963; J. Huang and J. A. Encinar, *Reflectarray Antennas*, 2008; D. M. Pozar, S. D. Targonski, H. D. Syrigos, *IEEE TAP* 45(2), 1997 (cited) [lens]
83. MyEmbeddedStuff (June 2026), Nodak Mesh (2026), Meshtastic docs, Medium "Testing LoRa antennas at 915 MHz" (search snippet only), TTN forum — stock-antenna measurements and gateway experience (blogs/forums — anecdotal) [identification]
84. Hackaday, "Identify that antenna by sight," 2022 (article) [identification]; A. D. Yaghjian and S. R. Best, *IEEE TAP* 53(4), 2005 (Q_Z) [dipoles]; H. F. Mathis, "A short proof that an isotropic antenna is impossible," *Proc. IRE* 39(8), 970, 1951 (cited) [polarization]

## Verification scripts (this domain)
- `tools/verify/ant_dipole.py` — directivities, R_r (numeric vs Si/Ci), 73.08 + j42.52 Ω, monopole, beamwidths.
- `tools/verify/ant_mom_wire.py` — parallel-wire Galerkin MoM: dipole resonance vs thickness, finite-radius impedance, energy check.
- `tools/verify/ant_mom_general.py` — general wire MoM with junctions/loads/PEC ground: monopole, radials vs droop, folded dipoles, loops, helices.
- `tools/verify/ant_yagi.py` — mutual impedance check, DL6WU algorithm + MoM (433/915 MHz), 3-element optimisation, LPDA equations.
- `tools/verify/ant_patch.py` — TL model + Jackson CAD, directivity (two-slot vs CAD), CP two-mode model.
- `tools/verify/ant_small_limits.py` — McLean Q by stored-energy integration, bandwidth limits, loops, ferrite rods.
- `tools/verify/ant_aperture.py` — A_e, beamwidth approximations, apertures, dish taper/spillover, optimum horn, far field.
- `tools/verify/ant_helix.py` — Kraus vs King & Wong vs Emerson.
- `tools/verify/ant_polarization.py` — IEEE sense, PLF, reflection, rotating source.
- `tools/verify/ant_rocket.py` — look angle/pattern loss, link budgets, plume cone.
- `tools/verify/ant_measurement.py` — far-field error, three-antenna method, Wheeler cap, range reflections, averaging.
- `tools/verify/ant2_slot.py` — Babinet numbers, MoM strip → slot, offset feed, WR-90 slotted array (reproduces W1GHZ), array factor of alternating offsets.
- `tools/verify/ant2_slot_openems.py` (+ `_results.txt`) — openEMS: free slot (Babinet check 488 Ω), PCB slots on infinite/finite FR-4, offset feed, 915 MHz edge notch.
- `tools/verify/ant2_hf_wire.py` (+ `_output.txt`) — PyNEC: random wire impedances and length study, fan/crossed and trap dipoles, inverted-V, OCF, G5RV, NVIS, vertical ground loss.
- `tools/verify/ant2_inductive.py` (+ `_output.txt`) — Neumann/Maxwell M, η_max derivation, Mohan vs filament, 13.56 MHz coil + exact C1/C2 vs AN11755, Q trade-off, Qi tank, UHF RFID range, Kurs plausibility.
- `tools/verify/ant2_wideband.py` (+ `_output.txt`) — cone/bow-tie impedance, NEC discone, P.372 receive penalty table, spiral/Vivaldi sizes.
- `tools/verify/ant2_lens.py` (+ `_output.txt`) — hyperbolic lens, Luneburg ray trace, lens gain/loss/mass, quantisation loss, reflectarray bandwidth.
- `tools/verify/ant2_ident.py` (+ `_output.txt`) — λ/4 length table, mismatch loss, collinear and dish gain.
- `tools/verify/ant2_qa.py` (+ `_output.txt`) — conductor loss, tip voltage, wrong-band mismatch, dipole near metal, bent tips, RLC equivalent/bandwidth, HT stubby, mag-mount, far-field harvesting.
