# 04-real-components-hf — Sources

Consolidated bibliography for the real-components domain. Reliability tags per CONVENTIONS §3. "Used in" lists the citing pages.

## Manufacturer application notes and technical documents
| # | Citation | Supports | Used in |
|---|---|---|---|
| M1 | R. Fiore (ATC), "Capacitors in coupling and DC blocking applications," *Circuit Designer's Notebook*, Doc 001-927 Rev. E, 2005 (Kyocera-AVX). https://rfs.kyocera-avx.com/userFiles/uploads/pdfs/capacitors_in_coupling.pdf (app note) | FSR/ESR table (100A/600S), parallel resonance 1.6 GHz, edge mounting, IL criterion | MLCC |
| M2 | Murata, "GJM series high-frequency high-Q chip capacitors," catalog C-29-C (Modelithics-hosted). https://www.modelithics.com/models/Vendor/Murata/GJM15.pdf (datasheet) | Cu electrodes, C0G range, ESR/Q specs, tolerance codes | MLCC, resonance (01) |
| M3 | Johanson Technology, "Multi-layer high-Q capacitors" catalog, 2022. https://www.johansontechnology.com/docs/2818/johanson-technology-multi-layer-high-q-capacitors8--4-2022_VRkwKZd.pdf (datasheet) | SRF/ESR/Q/current charts; oriented capacitors | MLCC, reactive power (01) |
| M4 | Kyocera-AVX, "Low inductance capacitors — introduction" (LICC/IDC/LICA). https://media.digikey.com/pdf/Data%20Sheets/AVX%20PDFs/LICC.pdf (datasheet) | ESL by style for 100 nF parts (1206 1200 pH … LICA 25 pH) | MLCC |
| M5 | KEMET, "General information — ceramic capacitors" (F9000), 2007. https://content.kemet.com/datasheets/F9000_K.pdf (technical note) | Class 1/2, EIA RS-198 code table, ageing law, de-ageing, equivalent circuit | MLCC |
| M6 | Johanson Dielectrics, "Ceramic capacitor aging made simple." https://www.johansondielectrics.com/tech-notes/ceramic-capacitor-aging-made-simple/ (app note) | Ageing rates (X7R/X5R 2.5 %, Y5V 7 %/decade-hour), 1000 h reference | MLCC |
| M7 | M. Fortunato, "Temperature and voltage variation of ceramic capacitors…," Maxim tutorial 5527, 2012 (ADI). https://www.analog.com/en/technical-articles/temperature-and-voltage-variation-ceramic-capacitor--maxim-integrated.html (app note; figures via search summary — page fetch timed out) | 4.7 µF 6.3 V 0603 X5R → 0.33 µF at 5 V | MLCC |
| M8 | Murata, "What are impedance/ESR frequency characteristics in capacitors?" https://article.murata.com/en-us/article/impedance-esr-frequency-characteristics-in-capacitors (manufacturer article) | ESR mechanisms vs frequency; SRF vs size | MLCC |
| M9 | Murata, "MLCC S-parameter measurement conditions." https://www.murata.com/en-us/tool/data/sparameterdata/sparameter-mlcc/condition (documentation) | Shunt modes, jigs, substrates, de-embedding | MLCC, models |
| M10 | Coilcraft, "Chip inductors — 0402HP series (1005)," Doc 526, 2023. https://www.coilcraft.com/getmedia/54459dcc-b821-4a9d-b91e-0416ea86a9b2/0402hp.pdf (datasheet) | L/Q/SRF/DCR/Irms table, fixtures, TCL | inductors, models, reactive power (01), filters (01) |
| M11 | Coilcraft, "S-parameters for high-frequency circuit simulations," Doc 1721, 2023. https://www.coilcraft.com/getmedia/35dbfd16-8483-4ef7-bb07-9b28a04f6dcc/doc1721_When-to-Use-S-parameters.pdf (app note) | Model-generated S-params, de-embedding, on-board SRF lower, small-signal only | inductors, models |
| M12 | Murata, "LQG15HS series" catalog O05E11 (Modelithics-hosted). https://www.modelithics.com/models/Vendor/Murata/LQG15HS.pdf (datasheet) | Multilayer inductor Q/SRF/DCR (Q ≈ 29 @ 900 MHz for 10 nH) | inductors |
| M13 | Vishay, "Frequency response of thin film chip resistors," Technical Note 60107, 2009. https://www.vishay.com/docs/60107/freqresp.pdf (app note) | 0.1–40 GHz model, internal parasitics by case, trim/termination effects | resistors, models |
| M14 | Vishay, FC series thin-film high-frequency resistors, datasheet 60093. https://www.vishay.com/docs/60093/fcseries.pdf (datasheet) | RF thin-film resistor range | resistors |
| M15 | Yageo, RC0402 general-purpose chip resistor datasheet. https://datasheet.octopart.com/RC0402FR-07100KL-Yageo-datasheet-8324255.pdf (datasheet) | 62.5 mW rating, 70 → 155 °C derating | resistors |
| M16 | C. Burket, "Ferrite beads demystified," *Analog Dialogue* 50-02, 2016 / ADI AN-1368 (reprint: Power Systems Design). https://www.powersystemsdesign.com/articles/ferrite-bead-demystified/95/10031 (app note) | Bead model, DC-bias collapse, bead–cap resonance, damping methods | ferrites |
| M17 | Fair-Rite, "How to choose ferrite components for EMI suppression," catalog technical section (14th ed.). https://taccomms.org/wp-content/uploads/2019/ham_radio/Choose-Ferrite-For-Emi.pdf (technical note) | Complex permeability, $L_0$, $H=1.256NI/\ell_m$, material table | ferrites |
| M18 | Fair-Rite material data sheets 31, 43, 61. https://fair-rite.com/43-material-data-sheet/ (datasheet) | µᵢ, resistivity, Curie T, frequency ranges | ferrites |
| M19 | Texas Instruments, "Quad flat no-lead (QFN) package comparison tables." https://www.ti.com/pdfs/logic/qfncompare.pdf (manufacturer data) | Average lead R/L/C by package | package |
| M20 | A. Fagnani, "Understanding flip chip QFN (HotRod™) and standard QFN performance differences," TI SLVAEE1, 2019. https://www.ti.com/lit/pdf/slvaee1 (app note) | Bondwire resistance, loop inductance 1.0 vs 1.4 nH | package |
| M21 | Semtech, "SX1261/2 data sheet," rev. 1.2, 2019. https://cdn.sparkfun.com/assets/6/b/5/1/4/SX1262_datasheet.pdf (datasheet) | Crystal spec, FERR_L, drift limit/LDRO, trim caps, TCXO block | crystals, package |
| M22 | Semtech, "LoRa® modulation crystal oscillator guidance," AN1200.14 rev. 2.1, 2018. https://www.mouser.com/pdfdocs/an120014-xo-guidance-lora-modulation.pdf (app note) | Crystal spec table, ±25 % BW tolerance, g-sensitivity, recommended XO/TCXO | crystals |
| M23 | Semtech, "SX1261/2 recommendations for best performance," AN1200.37 rev. 1.1, 2018. https://cdn.sparkfun.com/assets/f/f/b/4/2/SX1262_AN-Recommendations_for_Best_Performance.pdf (app note) | PA self-heating drift, thermal isolation, TCXO guidance | crystals |
| M24 | STMicroelectronics, AN2867 oscillator design guide. https://www.st.com/resource/en/application_note/an2867-guidelines-for-oscillator-design-on-stm8afals-and-stm32-mcusmpus-stmicroelectronics.pdf (app note; via search summary) | $C_L$ formula, $g_{m,crit}$, gain margin | crystals |
| M25 | IQD, "A guide to AT-cut crystals." https://www.iqdfrequencyproducts.com/en/news?d=at-cut-crystals (manufacturer article) | Cut angle, inflection ≈ 25 °C | crystals |
| M26 | JLCPCB, "Controlled impedance PCB layer stackup." https://jlcpcb.com/impedance (manufacturer documentation) | JLC04161H-7628: 0.2104 mm 7628 prepreg, Dk 4.4 | PCB parasitics, package |
| M27 | Murata, "SimSurfing" design support software. https://www.murata.com/en-us/tool/simsurfing (tool) | Models incl. DC bias/temperature | models, MLCC, ferrites |

## Technical reports, monographs and expert newsletters
| # | Citation | Supports |
|---|---|---|
| R1 | J. R. Vig, "Quartz crystal resonators and oscillators … a tutorial," US Army SLCET-TR-88-1 rev. 8.5.2.0, 2004. https://www.pletronics.com/wp-content/uploads/2025/08/Vig_tutorial.pdf (tutorial) | Oscillator classes/comparison, pulling example, acceleration environments, vibration sidebands |
| R2 | D. W. Knight, "An introduction to the art of solenoid inductance calculation," v0.20, 2016. https://coil32.net/files/Dave_Knight/Solenoids.pdf (monograph) | Nagaoka coefficient, Lundin, Wheeler accuracy, Rosa corrections |
| R3 | H. W. Johnson, "Via inductance" / "Via inductance II," HSDD Online Newsletter vol. 6 no. 4 & 8. https://www.sigcon.com/Pubs/news/6_04.htm ; https://www.sigcon.com/Pubs/news/6_08.htm (expert newsletter) | Via loop formula; predicted vs measured values |
| R4 | Qucs technical documentation, "Microstrip via hole" (Goldfarb–Pucel model). https://qucs.sourceforge.net/tech/node83.html (software documentation) | Via inductance/resistance formulas |
| R5 | B. Archambeault, "Eliminating the myths about PCB power/ground plane decoupling," *Interference Technology*. https://interferencetechnology.com/eliminating-the-myths-about-printed-circuit-board-powerground-plane-decoupling/ (expert article) | Anti-resonance of mixed capacitor values |

## Peer-reviewed papers
| # | Citation | Supports |
|---|---|---|
| P1 | M. E. Goldfarb, R. A. Pucel, "Modeling via hole grounds in microstrip," *IEEE MGWL*, 1(6), 135–137, 1991. | Via inductance |
| P2 | R. Lundin, "A handbook formula for the inductance of a single-layer circular coil," *Proc. IEEE*, 73(9), 1428–1429, 1985. | Nagaoka coefficient approximation |
| P3 | H. A. Wheeler, "Simple inductance formulas for radio coils," *Proc. IRE*, 16(10), 1398–1400, 1928. | Wheeler formula |
| P4 | R. G. Medhurst, "H.F. resistance and self-capacitance of single-layer solenoids," *Wireless Engineer*, 1947. | Proximity effect, coil self-capacitance |
| P5 | A. E. Ruehli, "Inductance calculations in a complex IC environment," *IBM J. Res. Dev.*, 16(5), 470–481, 1972. | Partial inductance |
| P6 | R. Bechmann, A. D. Ballato, T. J. Lukaszek, "Higher-order temperature coefficients of … alpha-quartz," *Proc. IRE*, 50(8), 1812–1822, 1962. (not re-fetched) | AT-cut cubic |
| P7 | R. L. Filler, "The acceleration sensitivity of quartz crystal oscillators: a review," *IEEE Trans. UFFC*, 35(3), 297–305, 1988. | g-sensitivity |
| P8 | B. Gustavsen, A. Semlyen, "Rational approximation of frequency domain responses by vector fitting," *IEEE Trans. Power Delivery*, 14(3), 1052–1061, 1999. | Passive/causal macromodels |
| P9 | arXiv:2101.06016, "Impact of phase noise and oscillator stability on ultra-narrow-band-IoT waveforms for satellite." (preprint; via search summary) | LoRa in-frame drift expression |

## Textbooks
| # | Citation | Supports |
|---|---|---|
| T1 | F. W. Grover, *Inductance Calculations: Working Formulas and Tables*, 1946 (Dover 2004). | Wire/strip/mutual inductance |
| T2 | C. R. Paul, *Inductance: Loop and Partial*, Wiley-IEEE, 2010. | Loop vs partial inductance |
| T3 | H. W. Johnson, M. Graham, *High-Speed Digital Design*, Prentice Hall, 1993. | Vias, ground planes, return current |
| T4 | D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012. | Microstrip formulas, S-matrix properties |
| T5 | C. Bowick, *RF Circuit Design*, 2nd ed., Newnes, 2008. | Component behaviour at RF, air coils |
| T6 | R. Ludwig, G. Bogdanov, *RF Circuit Design*, 2nd ed., Pearson, 2009. | HF resistor/capacitor/inductor models |
| T7 | T. H. Lee, *The Design of CMOS Radio-Frequency Integrated Circuits*, 2nd ed., Cambridge UP, 2004. | Bondwires, degeneration, package effects |
| T8 | H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley, 2009. | Ferrites, CM chokes, decoupling |
| T9 | C. R. Paul, *Introduction to Electromagnetic Compatibility*, 2nd ed., Wiley, 2006. | Ferrites, chokes |
| T10 | W. Hayward, R. Campbell, B. Larkin, *Experimental Methods in RF Design*, ARRL, 2003. | Attenuators/terminations for test |

## Forum / secondary articles (misconceptions only)
| # | Citation | Used for |
|---|---|---|
| F1 | All About Circuits forum "Common decoupling cap — why 100 nF" (thread 102031), "Decoupling capacitors" (90980); Hackaday "Capacitor decoupling chaos…" (2025). (forum — anecdotal) | "100 nF + 10 nF" misconception (MLCC) |
| F2 | All About Circuits technical article on crystal load capacitance; Electronics-Notes load-capacitance article. (secondary) | "C_x = C_L" misconception, stray range (crystals) |
| F3 | Altium "How to use (and not use) a ferrite bead…"; All About Circuits "Choosing and using ferrite beads". (secondary) | Bead–capacitor peaking reports (ferrites) |

## Software
| # | Citation | Used for |
|---|---|---|
| S1 | scikit-rf v2.0.1 (`skrf.media.MLine`, `Network.is_passive`, Touchstone I/O, `VectorFitting`). https://scikit-rf.readthedocs.io | Cross-checks in all component scripts |

## Verification scripts (this KB)
`tools/verify/components_mlcc.py`, `components_inductors.py`, `components_resistors.py`, `components_ferrite_bead.py`, `components_pcb_parasitics.py`, `components_bondwire.py`, `components_crystal.py`, `components_s2p_models.py`.
