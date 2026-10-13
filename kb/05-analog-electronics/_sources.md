# 05-analog-electronics — sources

Consolidated bibliography for the domain. Each page's own "Sources" section gives the specific
facts taken from each item; this list groups them by type. Reliability tags follow CONVENTIONS §3.
"Read" = text actually retrieved and checked this session (PDFs via WebFetch + pdftotext);
"cited" = standard reference used for scope/derivation cross-checks but not re-read this session.

## Textbooks (cited)
| Ref | Full citation | Used on |
|---|---|---|
| AoE | P. Horowitz, W. Hill, *The Art of Electronics*, 3rd ed., Cambridge University Press, 2015 | all pages |
| Sedra | A. S. Sedra, K. C. Smith, *Microelectronic Circuits*, 7th ed., Oxford University Press, 2015 | diodes, BJT, topologies |
| GHLM | P. R. Gray, P. J. Hurst, S. H. Lewis, R. G. Meyer, *Analysis and Design of Analog Integrated Circuits*, 5th ed., Wiley, 2009 | diodes, BJT, FETs, topologies, stability, oscillators |
| Razavi-A | B. Razavi, *Design of Analog CMOS Integrated Circuits*, 2nd ed., McGraw-Hill, 2017 | FETs, topologies |
| Razavi-RF | B. Razavi, *RF Microelectronics*, 2nd ed., Prentice Hall, 2011 | oscillators |
| Razavi-DC | B. Razavi, *Principles of Data Conversion System Design*, IEEE Press, 1995 | data converters |
| Lee | T. H. Lee, *The Design of CMOS Radio-Frequency Integrated Circuits*, 2nd ed., Cambridge, 2004 | topologies (OCTC), oscillators |
| Sze | S. M. Sze, K. K. Ng, *Physics of Semiconductor Devices*, 3rd ed., Wiley, 2007 | diodes, FETs |
| Cressler | J. D. Cressler, G. Niu, *Silicon-Germanium Heterojunction Bipolar Transistors*, Artech House, 2003 | BJT (SiGe) |
| Jespers | P. G. A. Jespers, B. Murmann, *Systematic Design of Analog CMOS Circuits*, Cambridge, 2017 | FETs (gm/ID) |
| Franco | S. Franco, *Design with Operational Amplifiers and Analog Integrated Circuits*, 4th ed., McGraw-Hill, 2015 | stability |
| Graeme | J. G. Graeme, *Photodiode Amplifiers: Op Amp Solutions*, McGraw-Hill, 1996 | stability, low-noise |
| M&C | C. D. Motchenbacher, J. A. Connelly, *Low-Noise Electronic System Design*, Wiley, 1993 | low-noise |
| Ott | H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley, 2009 | low-noise |
| W&T | A. B. Williams, F. J. Taylor, *Electronic Filter Design Handbook*, 4th ed., McGraw-Hill, 2006 | active filters |
| Schaumann | R. Schaumann, M. E. Van Valkenburg, *Design of Analog Filters*, Oxford, 2001 | active filters |
| S&T | R. Schreier, G. C. Temes, *Understanding Delta-Sigma Data Converters*, Wiley-IEEE, 2005 | data converters |
| Kester | W. Kester (ed.), *The Data Conversion Handbook*, Analog Devices/Newnes, 2005 (free from ADI; not retrievable this session) | data converters |
| Jung | W. Jung (ed.), *Op Amp Applications Handbook*, Analog Devices/Newnes, 2005 | op-amps, signal conditioning |
| Kitchin | C. Kitchin, L. Counts, *A Designer's Guide to Instrumentation Amplifiers*, 3rd ed., Analog Devices, 2006 (not retrievable) | signal conditioning |
| E&M | R. W. Erickson, D. Maksimović, *Fundamentals of Power Electronics*, 2nd ed., Springer, 2001 | power supplies |
| Gonzalez | G. Gonzalez, *Microwave Transistor Amplifiers*, 2nd ed., Prentice Hall, 1997 | topologies (feedback amps) |
| EMRFD | W. Hayward, R. Campbell, B. Larkin, *Experimental Methods in RF Design*, ARRL, 2003 | oscillators |
| Clarke-Hess | K. K. Clarke, D. T. Hess, *Communication Circuits: Analysis and Design*, Addison-Wesley, 1971 | oscillators (Bessel Gm) |

## Peer-reviewed papers and standards
| Ref | Citation | Used on | Status |
|---|---|---|---|
| Mishra02 | U. K. Mishra, P. Parikh, Y.-F. Wu, "AlGaN/GaN HEMTs — an overview of device operation and applications," *Proc. IEEE* 90(6):1022–1031, 2002. http://my.ece.ucsb.edu/Mishra/classfiles/overview.pdf | FETs | read |
| Heinemann10 | B. Heinemann et al., "SiGe HBT technology with fT/fmax of 300 GHz/500 GHz and 2.0 ps CML gate delay," IEDM 2010 (+ IHP SG13G2 pages) | BJT | read (abstract/vendor page) |
| Mason54 | S. J. Mason, "Power gain in feedback amplifiers," *IRE Trans. Circuit Theory* CT-1:20–25, 1954 | BJT | cited |
| Leeson66 | D. B. Leeson, "A simple model of feedback oscillator noise spectrum," *Proc. IEEE* 54(2):329–330, 1966 | oscillators | cited |
| HajLee98 | A. Hajimiri, T. H. Lee, "A general theory of phase noise in electrical oscillators," *IEEE JSSC* 33(2):179–194, 1998 | oscillators | cited |
| Rubiola05 | E. Rubiola, "The Leeson effect — phase noise in quasilinear oscillators," arXiv:physics/0502143, 2005 (Eqs. 1.4, 1.26, 1.39: $\mathcal L=S_\varphi/2$, $S_\varphi$ floor $FkT_0/P_0$ at the amplifier input) | oscillators (Leeson prefactor, W5-E9) | read by W4-D6 |
| LeeHaj00 | T. H. Lee, A. Hajimiri, "Oscillator phase noise: a tutorial," *IEEE JSSC* 35(3):326–336, 2000 ($2FkT/P_{sig}$, tank-power form) | oscillators | cited |
| Middlebrook75 | R. D. Middlebrook, "Measurement of loop gain in feedback systems," *Int. J. Electronics* 38(4):485–512, 1975 | stability | cited |
| Middlebrook78 | R. D. Middlebrook, "Design techniques for preventing input-filter oscillations in switched-mode regulators," Powercon 5, 1978 | power supplies | cited |
| IEEE1241 | IEEE Std 1241-2010, ADC terminology and test methods | data converters | cited |
| IEC61000-4-2 | IEC 61000-4-2, ESD immunity test | signal conditioning | cited |

## Application notes and technical reports (read unless noted)
| Ref | Citation / URL | Used on |
|---|---|---|
| SKY-PIN | Skyworks, *Design With PIN Diodes*, 200312E (2021). https://www.skyworksinc.com/-/media/SkyWorks/Documents/Products/1-100/Design_With_PIN_Diodes_200312E.pdf | diodes |
| SKY-VAR | Skyworks, *Varactor Diodes*, 200824A (2008). https://www.skyworksinc.com/-/media/SkyWorks/Documents/Products/1-100/200824A.pdf | diodes |
| AN969 | Avago, *The Zero Bias Schottky Detector Diode*, AN 969 (text extraction partial) | diodes |
| AN986 | Avago, *Square Law and Linear Detection*, AN 986 (search excerpt). https://www.rf-microwave.com/app/resources/uploads/diodes/AN986.pdf | diodes |
| AN918 | HP, *Pulse and Waveform Generation with Step Recovery Diodes*, AN 918. https://hpmemoryproject.org/an/pdf/an_918.pdf (identified) | diodes |
| AN178 | Infineon, *ESD Protection for RF Antennas*, AN178 (identified) + EDN ESD0P2RF announcement | diodes |
| MC-AN60-010 | Mini-Circuits, *Biasing of constant current MMIC amplifiers (ERA series)*. https://www.minicircuits.com/appdoc/AN60-010.html | topologies |
| SSZT999 | C. Wells, *Three ways to stabilize op amp capacitive loads*, TI SSZT999 (2017). https://www.ti.com/lit/pdf/sszt999 | stability |
| SBOA418/626 | TI, isolation-resistor and stability white papers (identified, not read) | stability |
| SLOD006B | R. Mancini (ed.), *Op Amps for Everyone*, TI SLOD006B (2002) (cited) | stability, op-amps, filters |
| SLOA024B | J. Karki, *Analysis of the Sallen-Key Architecture*, TI SLOA024B (cited) | active filters |
| SLVA043B | TI, *Noise Analysis in Operational Amplifier Circuits*, SLVA043B (2007). https://www.ti.com/lit/an/slva043b/slva043b.pdf | low-noise |
| SBOA128 | TI, *EMI Rejection Ratio of Operational Amplifiers* (identified) | op-amps |
| MT-034 | ADI, *MT-034 Current Feedback Op Amps* (identified; analog.com timed out) | op-amps |
| LIGO-T0900200 | F. Seifert, *Resistor Current Noise Measurements*, LIGO T0900200-v1 (2009). https://dcc.ligo.org/public/0002/T0900200/001/current_noise.pdf | low-noise |
| Vishay-basics | Vishay, *Basics of Linear Fixed Resistors* (search summary). https://www.vishay.com/docs/28771/basics.pdf | low-noise |
| AN2867 | STMicroelectronics, *AN2867 Oscillator design guide*, Rev 24 (2026) (search excerpts). https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm8afals-stm32-mcus-and-mpus-stmicroelectronics.pdf | oscillators |
| SLYT075 | E. Bartolome et al., *Clocking high-speed data converters*, TI SLYT075 (2005). https://www.ti.com/lit/pdf/slyt075 | data converters |

## Datasheets (read)
| Part | Maker / doc | Used on |
|---|---|---|
| HSMS-285x | Avago/Broadcom zero-bias Schottky. https://media.digikey.com/pdf/Data%20Sheets/Avago%20PDFs/HSMS-285x.pdf | diodes |
| BAR64-02V | Infineon PIN (values via vendor listing) | diodes |
| ESD0P2RF | Infineon 0.2 pF RF TVS (listing/announcement) | diodes |
| BFP740 | Infineon SiGe:C HBT v2.0. https://www.infineon.com/dgdl/Infineon-BFP740-DS-v02_00-EN.pdf?fileId=5546d46265f064ff0166389680a24ea4 | BJT, FETs |
| BF862 | NXP N-JFET. https://www.nxp.com/docs/en/data-sheet/BF862.pdf | FETs, low-noise |
| ATF-54143 | Avago E-pHEMT. https://www.modelithics.com/models/Vendor/Avago/ATF-54143.pdf | FETs |
| CGH40010 | Wolfspeed/MACOM 10 W GaN HEMT. https://cdn.macom.com/datasheets/CGH40010.pdf | FETs |
| AO3400A | AOS 30 V N-MOSFET (search summary). https://www.aosmd.com/res/datasheets/AO3400A.pdf | FETs |
| MCP6002 | Microchip DS20001733L | op-amps, low-noise |
| OPA333 | TI SBOS351E zero-drift | op-amps |
| OPA1612 | TI bipolar audio op-amp | op-amps, low-noise |
| THS3091 | TI current-feedback amplifier | op-amps |
| THS4551 | TI fully differential amplifier SBOS778D | op-amps, data converters |
| ADC3664 | TI 14-bit 125 MSPS ADC SBAS888B | data converters |
| TPS7A20 | TI low-noise LDO SBVS338H | power supplies |
| AMS1117 | AMS LDO (search summary) | power supplies |
| E22-400T33X | EBYTE user manual v1.5 | power supplies |
| INA333 | TI zero-drift INA SBOS445C | signal conditioning |
| INA180 | TI current-sense amplifier | signal conditioning |

## Lecture notes and software documentation
- MIT OCW 6.012 *Microelectronic Devices and Circuits* (BJT small-signal model, fT). https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/ (lecture notes, cited)
- SciPy signal documentation (filter prototypes used for design tables). https://docs.scipy.org/doc/scipy/reference/signal.html
- ngspice (shared library bundled with KiCad; driven by `tools/verify/analog_ngspice.py`).

## Team-internal records
- Space Bar avionics knowledge base (`~/.claude/knowledge/space-bar-avionics/`): Avionics C power architecture; flight-computer design lessons (pyro continuity, pyro backfeed, under-rated TVS, magnetometer supply noise, pyro gate drive at 3.3 V). Used for worked-example context only.
