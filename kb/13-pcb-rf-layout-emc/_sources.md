# 13-pcb-rf-layout-emc — Sources

Consolidated bibliography for the PCB/RF layout/EMC domain. Reliability tags per CONVENTIONS §3. "Used in" abbreviations: STK stackups, GND grounding, LAY rf-layout-rules, VIA vias, CON connectors, PDN power distribution, MIX mixed-signal, EMC emc-emi, SHD shielding, THM thermal, JLC jlcpcb-rf-manufacturing, CHK checklist. Raw numbers and access notes are in `research-logs/W3-C1-pcb-emc.md`.

## Textbooks
| # | Citation | Supports | Used in |
|---|---|---|---|
| T1 | H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley, 2009 (cited from knowledge; constants re-derived) | DM/CM radiation (263e-16, 12.6e-7), grounding, shielding apertures, digital spectra, PDN | GND, EMC, SHD, PDN, MIX |
| T2 | E. Bogatin, *Signal and Power Integrity — Simplified*, 3rd ed., Pearson, 2018 (from knowledge) | return paths, reference changes, PDN target impedance, plane capacitance | GND, PDN |
| T3 | H. W. Johnson, M. Graham, *High-Speed Digital Design*, Prentice Hall, 1993 (from knowledge; ToC checked: ch. 4 transmission lines, 5 ground planes and layer stacking incl. crosstalk, 6 terminations, 7 vias — W5-S18) | return-current distribution, crosstalk ∝ 1/(1+(D/H)²), vias | GND, VIA |
| T4 | C. R. Paul, *Introduction to Electromagnetic Compatibility*, 2nd ed., Wiley, 2006 (from knowledge) | DM/CM emission models, spectra, shielding | EMC, SHD |
| T5 | B. Archambeault, *PCB Design for Real-World EMI Control*, Kluwer, 2002 (via 04 page) | decoupling effectiveness, stitching practice | PDN, VIA |
| T6 | D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 | cavity modes/Q, discontinuities, microstrip | SHD, CON, LAY |
| T7 | N. Marcuvitz, *Waveguide Handbook*, 1951; R. E. Collin, *Field Theory of Guided Waves*, 2nd ed., 1991 (from knowledge) | inductive post gratings | VIA |
| T8 | F. P. Incropera, D. P. DeWitt et al., *Fundamentals of Heat and Mass Transfer*, Wiley (from knowledge) | conduction, convection, radiation | THM |
| T9 | K. C. Gupta et al., *Microstrip Lines and Slotlines* (Douville–James mitre formula, from knowledge) | bends | LAY |

## Peer-reviewed papers and standards
| # | Citation | Supports | Used in |
|---|---|---|---|
| P1 | H. W. Shim, T. H. Hubing, "20-H rule modeling and measurements," IEEE Int. Symp. EMC, 2001. https://cecas.clemson.edu/cvel/pdf/EMCS01-939.pdf (peer-reviewed; via search summary) | 20-H rule does not reduce radiation | GND |
| P2 | M. E. Goldfarb, R. A. Pucel, "Modeling via hole grounds in microstrip," IEEE MGWL 1(6), 1991 (via 04 page) | via inductance | VIA |
| P3 | D. Deslandes, K. Wu, IEEE T-MTT 54(6), 2006; F. Xu, K. Wu, IEEE T-MTT 53(1), 2005 (rules via secondary summaries) | SIW post-wall rules | VIA |
| P4 | R. J. P. Douville, D. S. James, IEEE T-MTT 26(3), 1978 (from knowledge) | optimum mitre | LAY |
| P5 | D. Hardin, J. Fessler, D. Bush, "Spread spectrum clock generation…," IEEE EMC Symp., 1994 (from knowledge) | SSC | EMC |
| S1 | MIL-STD-464C, *Electromagnetic Environmental Effects Requirements for Systems*, 2010 (App. A). https://www.ema3d.com/wp-content/uploads/downloads/MIL-STD-464C.pdf (standard; pdftotext) | EID 16.5 dB below MNFS; MNFS definition | EMC, CHK |
| S2 | 47 CFR §15.109 (Cornell LII). https://www.law.cornell.edu/cfr/text/47/15.109 (regulation) | Class A/B radiated limits | EMC |
| S3 | IEC 61000-4-2 (from knowledge) | ESD levels/waveform | EMC |
| S4 | IPC-4412 (glass styles; via secondary summaries); IPC-6012 Class 2 plating (via JLC blog); JEDEC JESD51 (from knowledge) | glass styles, plating, θJA definitions | STK, VIA, THM |

## Manufacturer documentation, datasheets and app notes
| # | Citation | Supports | Used in |
|---|---|---|---|
| M1 | JLCPCB, "Controlled impedance PCB layer stackup," https://jlcpcb.com/impedance (2026-09-27) | prepreg thickness/Dk, mask parameters | STK, JLC |
| M2 | JLCPCB online impedance calculator, https://jlcpcb.com/pcb-impedance-calculator, run 2026-09-27 (values in log S23) | 50 Ω widths per stackup with/without mask; trapezoid model | STK, JLC, CON |
| M3 | JLCPCB, "PCB manufacturing & assembly capabilities," https://jlcpcb.com/capabilities/pcb-capabilities | tolerances, features, POFV, finishes | JLC, VIA |
| M4 | JLCPCB, "User guide to the JLCPCB impedance calculator" | NP-155F, copper, mask assumptions | STK, JLC |
| M5 | JLCPCB, "High-frequency PCB manufacturing" page; blog "Rogers PCB & PTFE PCB…" (9 Mar 2023) | Rogers/PTFE 2-layer service, prices | STK, JLC |
| M6 | JLCPCB, "Surface finishes guide," https://jlcpcb.com/help/article/jlcpcb-surface-finish | ENIG Ni/Au thickness, HASL, OSP | JLC |
| M7 | JLCPCB, "PCB assembly capabilities," https://jlcpcb.com/capabilities/pcb-assembly-capabilities | Economic vs Standard PCBA limits | JLC |
| M8 | JLCPCB blog, "PCB plating thickness" | hole wall ≈ 20–25 µm | VIA, THM |
| M9 | Rogers Corp., RO4000 series data sheet; "RO4003C and RO4350B laminates with TICER foil" (92-134, 2019) (pdftotext) | Dk/Df, TCDk, CTE, Tg, k, moisture | STK |
| M10 | Isola, 370HR Dk/Df table rev C, 2020 (pdftotext) | Dk/Df vs glass style and resin content | STK |
| M11 | Panasonic, MEGTRON 6 R-5775(N) data sheet, 2022 (pdftotext) | low-loss laminate values | STK |
| M12 | Semtech, AN1200.37 *SX1261/2 Recommendations for Best Performance*, rev 1.1, 2018 (pdftotext) | PA heat → crystal drift, thermal insulation, TCXO | LAY, THM |
| M13 | Semtech, AN1200.40 *SX1261/2 Reference Design Explanation*, rev 1.1, 2018 (pdftotext) | 2/4-layer reference layouts, crystal void, match/filter structure | LAY, PDN, THM |
| M14 | Semtech, AN1200.66 *PCB Design Guidelines for LR11xx & SX126x*; SX1261/2 datasheet (search summaries only) | VR_PA decoupling; PA choke rating | LAY, PDN |
| M15 | Texas Instruments, SWRA640H *CC13xx/CC26xx Hardware Configuration and PCB Design Considerations*, 2024 (pdftotext) | stackup distance, balun symmetry, LC-filter layout, decoupling, shields | LAY, PDN, SHD, MIX |
| M16 | Espressif, *ESP32-S3 Hardware Design Guidelines — PCB layout* (docs.espressif.com, 2026-09) | stackup, RF routing, 0201 match, crystal, antenna clearance | LAY, MIX |
| M17 | u-blox, *MAX-M5Q Hardware Integration Manual* UBX-13002460 R06 (pdftotext) | GNSS layout checklist, EMI on lines, ESD < 0.5 pF, isolation ≈ 20 dB | LAY, EMC, SHD, MIX |
| M18 | u-blox, *GNSS Antennas — RF design considerations*, UBX-15030289 R03 (pdftotext) | jammer dynamic range, digital-noise sources, isolation, C/N0 | MIX, SHD |
| M19 | u-blox, MAX-M10S integration manual UBX-20053088 (search summary) | GCPW, ground under module, integrated SAW/notch | LAY, SHD |
| M20 | Hirose, U.FL series catalogue (via W1-A4 and search) | DC–6 GHz, VSWR, 30 cycles, cable loss | CON |
| M21 | Southwest Microwave, "Optimizing test boards for 50 GHz end launch connectors" (search summary; PDF too large to fetch) | via-wall λ/4 gap, launch tapering | CON, VIA |
| M22 | J. Coonrod (Rogers), "Comparing microstrip and grounded coplanar waveguides," 2020; ROG blog "Making the most of coplanar waveguide," 2014 | GCPW practice; ENIG data via 02 page | VIA, CON, JLC |
| M23 | Würth Elektronik, WE-SHC shielding cabinets (product pages/summaries); *ABC of Shielding* | can construction, SE ≈ 60 dB 0.5–3 GHz | SHD |
| M24 | EBYTE, E22-400T33D / E220-900T30D manuals (via 15 page and LCSC/EBYTE listings) | TX current, supply, −40…+85 °C | PDN, THM |
| M25 | Analog Devices: H. Zumbahlen, "Staying well grounded," Analog Dialogue 46-06 (2012); MT-031/MT-101 (fetch timed out; from knowledge) | AGND/DGND, decoupling | GND, MIX |

## Expert articles, talks, blogs, tools and forums
| # | Citation | Supports | Used in |
|---|---|---|---|
| E1 | H. W. Ott, "Partitioning and layout of a mixed-signal PCB," PCD June 2001; "Grounding of mixed signal PCBs" tech tip (hott.shielddigitaldesign.com) (expert article) | single plane + partitioning | GND, MIX |
| E2 | R. Hartley, "How grounding controls noise and EMI in a PCB," Sierra Circuits (talk/article); AltiumLive talks (talk) | stackup: planes one dielectric away; fields carry energy | GND |
| E3 | G. Sutherland, "Tips for getting PCBs made with JLCPCB," 2025; gsuberland/jlcpcb_autogenerated_stackups (blog/tool — anecdotal) | TG155 vs TG135 gotcha; KiCad stackup export | STK, JLC |
| E4 | JLCPCB Q&A #592 (2024-12) (forum-like, unanswered) | same gotcha | STK |
| E5 | Fedevel forum, "JLCPCB controlled impedance issues for high speed boards," Dec 2024 (forum — anecdotal) | ±20 %/no report per live chat | JLC |
| E6 | Z-zero, "How to avoid getting totally skewed, part 3," 2021; Signal Integrity Journal glass-weave articles (trade) | weave-skew mitigations | STK |
| E7 | easyw, RF-tools-KiCAD (GitHub) (software) | via fence/stitching, round tracks, RF footprint wizards | LAY, VIA |
| E8 | privatedata.com hobby igniter page (via search; anecdotal) | e-match all-fire/no-fire | EMC |
| E9 | Test & Measurement Tips, tinySA Ultra article; vendor listings (trade) | pre-compliance instrument specs | EMC |
| E10 | Rocketry Forum thread "BMP390 pressure sensor interference with telemetry" (title only; 403) (forum — anecdotal) | existence of the problem | EMC |

## KB cross-references and verification scripts
- KB: [planar lines](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md) and W1-A4 scripts `tline_microstrip.py`, `tline_cpwg.py`, `tline_fd2d.py`; [PCB parasitics](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md); [capacitors](../04-real-components-hf/capacitors-at-rf-mlcc.md); [ferrites](../04-real-components-hf/ferrites-and-beads.md); [skin effect & ENIG](../02-electromagnetics/skin-effect-conductor-loss-roughness.md); [dielectrics](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md); [cavities](../02-electromagnetics/waveguides-and-cavity-resonators.md); [radiation](../02-electromagnetics/radiation-from-currents-hertzian-dipole.md); [LoRa modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md).
- Scripts (this domain): `tools/verify/pcb_stackup_widths.py`, `pcb_return_current.py`, `pcb_via_fence.py`, `pcb_layout_rules.py`, `pcb_launch.py`, `pcb_cavity_modes.py`, `pcb_emc_radiation.py`, `pcb_pdn.py`, `pcb_mixed_signal.py`, `pcb_thermal.py`.

## Added by W5-E11 (digital-termination-and-crosstalk)
- S. H. Hall, H. L. Heck, *Advanced Signal Integrity for High-Speed Digital Designs*, Wiley 2009, chs. 2–3. (textbook)
- E. Bogatin, *Signal and Power Integrity — Simplified*, 3rd ed., 2018, chs. 8, 10. (textbook)
- H. W. Johnson, M. Graham, *High-Speed Digital Design*, 1993, chs. 4–6. C. R. Paul, *Analysis of Multiconductor Transmission Lines*, 2nd ed., 2008. (textbooks)
- Verification: `tools/verify/e11_crosstalk.py` (12/14).
