# 02-electromagnetics — Sources

Consolidated bibliography for the electromagnetics domain (W1-A3, 2026-09-27). Reliability tags per
CONVENTIONS §3. "Read" = full text or the relevant section was fetched and read in this session;
"abstract" = only abstract/summary seen; "knowledge" = cited from prior knowledge at chapter/section
level (site blocked or book not available) — facts from these were re-derived and numerically verified
in `tools/verify/em_*.py` wherever possible. Page abbreviations: CON constants, MAX Maxwell, PW plane
waves/polarization, POY Poynting, BC boundary/reflection, SK skin effect, DI dielectrics, MAG magnetic
materials, QS quasi-static, RAD radiation/Hertzian dipole, NF near/far field, WG waveguides/cavities,
LC inductance/capacitance.

## Textbooks
| # | Citation | Used for | Used in | Status |
|---|---|---|---|---|
| T1 | D. J. Griffiths, *Introduction to Electrodynamics*, 4th ed., 2013 — ch. 7–11, App. C (textbook) | Maxwell's correction, Poynting theorem, reflection, potentials, dipole radiation, Larmor, units | CON MAX POY BC RAD | knowledge |
| T2 | D. K. Cheng, *Field and Wave Electromagnetics*, 2nd ed., Addison-Wesley 1989 — ch. 3, 6, 7, 8 (textbook) | time-harmonic Maxwell, charge relaxation, plane waves, good conductors, reflection, L and C | MAX PW BC SK LC | knowledge |
| T3 | S. Ramo, J. R. Whinnery, T. Van Duzer, *Fields and Waves in Communication Electronics*, 3rd ed., Wiley 1994 — ch. 2–6, 8, 10 (textbook) | circuit concepts from fields, energy flow in circuits and coax, skin effect/Bessel wire, waveguides, cavities | POY SK QS WG LC PW | knowledge |
| T4 | R. F. Harrington, *Time-Harmonic Electromagnetic Fields*, McGraw-Hill 1961 / IEEE Press 2001 — ch. 1–3 (textbook) | complex Poynting theorem, magnetic currents, duality, uniqueness | MAX POY RAD | knowledge |
| T5 | C. A. Balanis, *Advanced Engineering Electromagnetics*, 2nd ed., Wiley 2012 — ch. 1–3, 5 (textbook) | constitutive parameters, polarisation mechanisms, duality, oblique incidence, pseudo-Brewster | MAX BC DI MAG | knowledge |
| T6 | C. A. Balanis, *Antenna Theory*, 4th ed., Wiley 2016 — §2.2.4, §2.12, ch. 3–5 (textbook) | field regions, polarization/PLF, vector potentials, infinitesimal/small dipole, small loop | CON PW QS RAD NF | knowledge |
| T7 | D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley 2012 — §1.2–1.8, §2.1, §2.7, §3.1–3.8, ch. 6, ch. 9 (textbook) | loss tangent, plane waves, perturbation loss, microstrip loss, waveguide eq. 3.96, cavity Q eq. 6.46, ferrite Polder tensor | MAX PW POY BC SK DI MAG QS WG | knowledge |
| T8 | J. D. Jackson, *Classical Electrodynamics*, 3rd ed., Wiley 1999 — §6.7–6.8, ch. 9, units appendix (textbook) | dispersive energy, radiation from localized sources, Gaussian↔SI | CON POY RAD | knowledge |
| T9 | H. A. Haus, J. R. Melcher, *Electromagnetic Fields and Energy*, Prentice Hall 1989; free at MIT OCW RES.6-001 and https://web.mit.edu/6.013_book/www/ — ch. 1–3, 7, 10 (textbook, free) | integral laws, EQS/MQS conditions, τ_em² = τ_eτ_m | MAX QS | chapter list confirmed online; content knowledge |
| T10 | S. J. Orfanidis, *Electromagnetic Waves and Antennas*, Rutgers (free online) — ch. 2, 4–8 (textbook, free) | plane waves (ch. 2; polarization §2.5, lossy media §2.6–2.7), birefringent media (ch. 4), reflection/multilayers/oblique incidence/film applications (ch. 5–8) | PW BC | site HTTP 403 on 2026-09-27; knowledge. Chapter numbers checked against the 2016 ToC by W5-S18b (2026-10-13) |
| T11 | R. P. Feynman, R. B. Leighton, M. Sands, *The Feynman Lectures on Physics* Vol. II — ch. 17, 18, 23, 24, 27 (textbook, free) | Maxwell equations, flux-rule exceptions, energy flow examples, cavities, waveguides | MAX POY WG | site HTTP 403; knowledge |
| T12 | C. R. Paul, *Introduction to Electromagnetic Compatibility*, 2nd ed., Wiley 2006 — §8.1, ch. 10 (textbook) | DM/CM emission constants (reproduced from first principles), shielding | RAD NF | knowledge + verified |
| T13 | C. R. Paul, *Inductance: Loop and Partial*, Wiley/IEEE 2010 (textbook) | loop vs partial inductance | LC | knowledge |
| T14 | H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley 2009 — ch. 6, 12 (textbook) | near-field shielding, DM/CM radiation with ground factor | RAD NF | knowledge |
| T15 | H. W. Johnson, M. Graham, *High-Speed Digital Design*, Prentice Hall 1993 (textbook) | knee frequency, lumped criterion, via-inductance formula (discrepancy C12) | QS LC | knowledge |
| T16 | E. Bogatin, *Signal and Power Integrity — Simplified*, 3rd ed., 2018 (textbook) | 0.35/t_r, 20 % rule | QS | knowledge |
| T17 | M. Born, E. Wolf, *Principles of Optics*, 7th ed., 1999 — §1.4 (textbook) | optics handedness convention | PW | knowledge |
| T18 | T. Milligan, *Modern Antenna Design*, 2nd ed., 2005 (textbook) | polarization mismatch of two elliptical antennas (formula verified) | PW | knowledge + verified |
| T19 | N. W. Ashcroft, N. D. Mermin, *Solid State Physics*, 1976 — ch. 1 (textbook) | Drude collision time | MAX | knowledge |
| T20 | R. E. Collin, *Foundations for Microwave Engineering*, 2nd ed., 2001 (textbook) | waveguides, cavities | WG | knowledge |
| T21 | B. Lax, K. J. Button, *Microwave Ferrites and Ferrimagnetics*, 1962 (textbook) | Polder tensor, Kittel | MAG | knowledge |
| T22 | E. M. Purcell, D. J. Morin, *Electricity and Magnetism*, 3rd ed., 2013 — App. H (textbook) | radiation "kink" picture | RAD | knowledge |
| T23 | D. J. Kozakoff, *Analysis of Radome-Enclosed Antennas*, 2nd ed., Artech 2010 (textbook) | half-wave/thin-wall/A-sandwich walls | BC | knowledge |
| T24 | F. W. Grover, *Inductance Calculations*, 1946/2004; E. B. Rosa, *Bull. Bur. Stand.* 4, 301 (1908); J. C. Maxwell, *Treatise*, 1873 (handbook/classic) | straight-wire partials, coaxial-loop M (verified numerically) | LC | knowledge + verified |
| T25 | J. D. Kraus, R. J. Marhefka, *Antennas for All Applications*, 3rd ed., 2002 (textbook) | near/far fields | NF | knowledge |
| T26 | B. C. Wadell, *Transmission Line Design Handbook*, Artech 1991 (handbook) | line L′/C′ formulas | LC | knowledge |
| T27 | A. von Hippel (ed.), *Dielectric Materials and Applications*, 1954 (handbook) | classic dielectric tables | DI | knowledge |

## Standards and reference data
| # | Citation | Used for | Used in | Status |
|---|---|---|---|---|
| S1 | NIST CODATA 2022 values (physics.nist.gov/cuu/Constants): μ0 1.256 637 061 27(20)×10⁻⁶, ε0 8.854 187 8188(14)×10⁻¹², Z0 376.730 313 412(59) Ω, α 7.297 352 5643(11)×10⁻³; Mohr, Newell, Taylor, Tiesinga, *Rev. Mod. Phys.* 97, 025002 (2025), arXiv:2409.03787 (standard) | constants | CON (all) | read |
| S2 | CODATA 2018: Tiesinga et al., *Rev. Mod. Phys.* 93, 025010 (2021) (standard) | 2018 α/μ0 for comparison | CON | knowledge (values standard) |
| S3 | BIPM, *SI Brochure*, 9th ed. (2019, updated), §2.3.1 and Table 1 (standard) | 2019 redefinition; μ0/ε0/Z0 now measured; exact relations | CON | read (PDF text) |
| S4 | ITU-R P.527-6 (09/2021), *Electrical characteristics of the surface of the Earth* (standard) | pure/sea-water double-Debye model (implemented), penetration depth eq. 4 | MAX PW BC DI | read |
| S5 | ITU-R P.368-10 (08/2022), ground-wave propagation (standard) | sea water εr 70, σ 5 S/m | MAX PW BC | read (captions) |
| S6 | CRC Handbook of Chemistry and Physics, "Electrical resistivity of pure metals" (293 K: Ag 1.587, Cu 1.678, Au 2.214, Al 2.650, Ni 6.93 ×10⁻⁸ Ω·m) (handbook) | skin-depth tables | SK | read (table mirror) |
| S7 | IEEE Std 145-2013 (antenna terms), IEEE Std 211-2018 (propagation terms) (standard) | polarization handedness definitions | PW | via secondary sources only |
| S8 | IEEE Std 149-2021 (antenna test procedures) (standard) | far-field range criterion | NF | knowledge |
| S9 | ICNIRP 2020 guidelines, *Health Physics* 118(5):483–524, Table 5 (standard) | general-public reference level f/200 W/m² (400–2000 MHz) | POY NF | knowledge — 19-regulations to confirm |
| S10 | IEC/EIA waveguide designations (WR-xx) (standard) | WR dimensions | WG | knowledge (dimensions standard) |

## Peer-reviewed papers
| # | Citation | Used for | Used in | Status |
|---|---|---|---|---|
| P1 | A. R. Djordjević, R. M. Biljić, V. D. Likar-Smiljanić, T. K. Sarkar, "Wideband frequency-domain characterization of FR-4 and time-domain causality," *IEEE Trans. EMC* 43(4), 662–667 (2001) | FR-4 10 Hz–12 GHz data; wideband Debye model and fitted parameters | DI SK | read |
| P2 | P. G. Huray, O. Oluwafemi, J. Loyer, E. Bogatin, X. Ye, "Impact of copper surface texture on loss: a model that works," DesignCon 2010 | snowball model eqs. 8–10, validation to 50 GHz, Hammerstad context | SK | read |
| P3 | S. Groiss, I. Bardi, O. Biro, K. Preis, K. R. Richter, *IEEE Trans. Magn.* 32(3), 894–897 (1996) | Groiss roughness formula | SK | abstract; formula via S-A2 |
| P4 | E. Hammerstad, Ø. Jensen, IEEE MTT-S Digest 1980, 407–409; Hammerstad & Bekkadal, *Microstrip Handbook*, 1975; S. P. Morgan, *J. Appl. Phys.* 20, 352 (1949) | roughness formula, microstrip Z0/ε_eff (reference for FD solver) | SK LC | via P2 / knowledge |
| P5 | D. Castles et al., *Scientific Reports* 6, 22714 (2016), PMC4778131 | printed ABS ε' 2.57, tanδ 0.0047 @15 GHz | DI | read (summary) |
| P6 | Kuzmanić et al., *Progress in Additive Manufacturing* (2023), PMC9942642 | PLA/ABS εr vs infill | DI | read (summary) |
| P7 | "Complex permittivity and anisotropy measurement of 3D-printed PLA…," IEEE CoBCom 2016, Xplore 7843900 | PLA ε' ≈ 2.75, anisotropy, tanδ 0.012–0.016 | DI | abstract |
| P8 | K. A. Işık et al., "Permittivity characterization of 3D-printed materials at millimeter waves," arXiv:2607.16937 (2026) (preprint) | PLA/resin 70–110 GHz | DI | read (HTML summary) |
| P9 | U. Kaatze, *J. Chem. Eng. Data* 34, 371–374 (1989) | water relaxation time 8.27 ps @25 °C | DI | abstract |
| P10 | M. Boulé, "DC power transported by two infinite parallel wires," *Am. J. Phys.* 92(1), 14–22 (2024), arXiv:2305.11827 | energy flow in circuits | POY | abstract |
| P11 | B. S. Davis, L. Kaplan, "Poynting vector flow in a circular circuit," *Am. J. Phys.* 79, 1155 (2011), arXiv:1207.2173 | energy flow in circuits | POY | abstract |
| P12 | R. H. Romer, *Am. J. Phys.* 50, 1089 (1982) | "what do voltmeters measure" | MAX | knowledge |
| P13 | J. L. Snoek, *Physica* 14, 207–217 (1948) | Snoek's limit | MAG | knowledge |
| P14 | T. Nakamura, *J. Appl. Phys.* 88, 348 (2000); *J. Appl. Phys.* 63, 3765 (1988) | Snoek's limit form and generalisation | MAG | abstract |
| P15 | C. Kittel, *Phys. Rev.* 73, 155 (1948) | FMR formulas | MAG | knowledge |
| P16 | A. E. Ruehli, *IBM J. Res. Dev.* 16(5), 470–481 (1972) | partial inductance | LC | knowledge |
| P17 | Y. Cassivi et al., *IEEE MWCL* 12(9), 333–335 (2002); D. Deslandes, K. Wu, *IEEE T-MTT* 54(6), 2516–2526 (2006) | SIW equivalent width, design rules | WG | knowledge |
| P18 | S. A. Schelkunoff, *Bell Syst. Tech. J.* 17, 17–48 (1938) | impedance concept for shielding | NF | knowledge |
| P19 | C. R. Sullivan, *IEEE Trans. Power Electron.* 14(2), 283–291 (1999) | Litz optimisation | SK | knowledge |
| P20 | "Modeling curved carbon fiber composite structures in TLM," arXiv:1502.01227; CFRP shielding studies (ResearchGate 241633450 etc.) | CFRP conductivity ranges | BC DI | abstract/summary — medium |

## Application notes, datasheets and trade articles
| # | Citation | Used for | Used in | Status |
|---|---|---|---|---|
| A1 | Rogers Corp., RO4000 series datasheet (RO4003C/RO4350B process/design Dk, Df) — incl. JLCPCB mirror static.jlcpcb.com/pdf/ROGERS_Datasheet.pdf (datasheet) | laminate values | DI | read (snippets) |
| A2 | Y. Shlepnev (Simberian), "From snowballs to cannonballs," 2019; "Unified approach to interconnect conductor surface roughness modelling," EPEPS 2017 (app note/conference) | Huray parameterisation, Cannonball critique, Groiss transition function | SK | read |
| A3 | Polar Instruments AP8155, surface-roughness effect on loss (app note) | model validity ranges, typical parameters | SK | read |
| A4 | J. Coonrod (Rogers), "The impact of final plated finishes on insertion loss for high-frequency PCBs," *PCD&F*, 2 Mar 2018 (trade, measured) | ENIG/ImAg/ImSn/OSP loss data | SK | read (summary) |
| A5 | G. Milad (Uyemura), "Minimizing signal transmission loss in high-frequency circuits," 2020 (trade) | thick vs thin Ni, EPIG | SK | read |
| A6 | Electroless-nickel property summaries (ScienceDirect Topics; Armoloy) (industry) | P content, magnetism | SK MAG | search summaries — medium |
| A7 | Fair-Rite 43 material datasheet; 61-material highlight (datasheet) | μi 800, 3500 G, 10⁵ Ω·cm | MAG | read |
| A8 | Palomar Engineers, "Ferrite mix selection" (vendor) | mix vs frequency | MAG | read |
| A9 | Ansys HFSS help: Groiss and Huray models (vendor docs) | model notes (non-causal Groiss) | SK | read (partial) |
| A10 | MathWorks "Polarized fields"; E. Gentzsch, Thorlabs "Polarization handedness convention" (2017) (vendor docs) | IEEE-RCP = optics-LCP | PW | search summaries |
| A11 | L. Simonovich, *Signal Integrity Journal* articles on laminate anisotropy and Cannonball-Huray (trade) | anisotropy not published by suppliers | DI SK | titles/abstracts (site 403) |

## Forums and videos (misconceptions only — no physics claims rest on these)
| # | Citation | Used for |
|---|---|---|
| F1 | Veritasium, "The Big Misconception About Electricity," YouTube, Nov 2021, and follow-up Stack Exchange/Reddit/blog debate | energy-flow misconception (POY) |
| F2 | Physics Forums / Stack Exchange threads on RHCP vs LHCP conventions | handedness confusion (PW) |
| F3 | Common skin-effect explanations ("current flows only on the surface") on tutorial sites | skin-effect misconception (SK) |
| F4 | PCB-vendor blogs claiming ENIG adds 1–3 dB/inch at 10 GHz and Ni μr ≈ 500 | example of unreliable claims contradicted by A4 (SK, contradiction C8) |

## Verification scripts (tools/verify/)
em_constants.py · em_maxwell.py · em_plane_waves.py · em_poynting.py · em_fresnel_radome.py ·
em_skin_depth.py · em_dielectrics.py · em_magnetics.py · em_quasistatic.py · em_hertzian_dipole.py ·
em_nearfield.py · em_waveguides.py · em_inductance.py

## Added by W5-E11 (greens-functions-and-integral-equations)
- R. F. Harrington, *Field Computation by Moment Methods*, 1968/1993. (textbook)
- W. C. Gibson, *The Method of Moments in Electromagnetics*, 2nd ed., CRC 2014. (textbook)
- W. C. Chew, *Waves and Fields in Inhomogeneous Media*, IEEE Press 1995 (dyadic and layered-media Green's functions). (textbook)
- K. A. Michalski, J. R. Mosig, "Multilayered media Green's functions in integral equation formulations," *IEEE Trans. AP* 45(3), 1997. (peer-reviewed)
- J. C. Rautio, R. F. Harrington, *IEEE Trans. MTT* 35(8), 1987 (shielded planar MoM, basis of Sonnet). (peer-reviewed)
- C.-O. Hwang, M. Mascagni, *J. Electrostatics*, 2004 (square-plate capacitance 0.36 ± 0.01). (peer-reviewed)
- Verification: `tools/verify/e11_greens.py` (15/15).
