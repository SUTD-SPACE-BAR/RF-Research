# 12-phased-arrays — bibliography

Consolidated bibliography for `kb/12-phased-arrays/`. Reliability tags per CONVENTIONS §3.
"READ" = full text (HTML, or PDF via pdftotext of the WebFetch-saved file) was read by the research
agent (W2-B5, 2026-09-27/29); "abstract" = only the abstract/search summary was read; "cited" = relied on
from standard-text knowledge and re-derived/verified numerically in `tools/verify/array_*.py`.
Page abbreviations: AF array-factor-linear-arrays · ST beam-steering-grating-lobes · PL planar-arrays-element-pattern-coupling ·
TP tapering-sidelobe-control · AR beamforming-architectures · PS phase-shifters-ttd-components · CAL array-calibration ·
DOA adaptive-beamforming-doa · DIY diy-phased-array-projects.

## Textbooks and handbooks
| # | Citation | Used for | Status | Pages |
|---|---|---|---|---|
| T1 | R. J. Mailloux, *Phased Array Antenna Handbook*, 2nd ed., Artech House, 2005 (3rd ed. 2018) — ch. 2 pattern characteristics of linear/planar arrays, ch. 3 synthesis, ch. 6 element pattern & mutual impedance, ch. 7 array error effects, ch. 8 limited-field-of-view & wideband feeds (subarrays, time delay) | conventions, grating lobes, errors, subarrays | cited; 2nd-ed. chapter numbers checked by W5-S18 (2026-10-13) against the contents page of a library-hosted copy (via search summary: ch. 6 "Summary of Element Pattern and Mutual Impedance Effects", ch. 7 "Array Error Effects" p. 353, ch. 8 "Special Array Feeds for Limited Field-of-View and Wideband Arrays" p. 379 incl. multiple-beam systems) and the 3rd-ed. ToC in gaps/D4-curriculum.md §3.7. **3rd-ed. numbering differs from ch. 8 on:** ch. 8 = multiple-beam antennas, ch. 9 = limited field-of-view and wideband; ch. 2, 3, 4, 6, 7 have the same scope in both | AF, ST, PL, TP, AR, CAL |
| T2 | R. C. Hansen, *Phased Array Antennas*, 2nd ed., Wiley, 2009 | directivity, superdirectivity, synthesis, coupling, blindness, multibeam feeds | cited | AF, ST, PL, TP, AR |
| T3 | C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed., Wiley, 2016 — ch. 6 arrays (linear, planar, circular; §6.8 binomial & Dolph–Tschebyscheff), ch. 8 mutual impedance | AF, HW endfire, uniform-array directivity, Dolph broadening factor | cited (via Nikolova's notes) | AF, ST, PL, TP |
| T4 | H. L. Van Trees, *Optimum Array Processing* (DEMT Part IV), Wiley, 2002 — ch. 2 arrays & spatial filters, ch. 3 synthesis, ch. 6 optimum beamformers (MVDR/MPDR/LCMV, loading), ch. 7 adaptive (SMI), ch. 8–9 parameter estimation (ML, CRB, MUSIC, Root-MUSIC, ESPRIT, smoothing) | array gain, white-noise gain, beamformers, DOA | cited | AF, ST, TP, AR, DOA |
| T5 | M. Skolnik (ed.), *Radar Handbook*, 3rd ed., McGraw-Hill, 2008 — ch. 13 J. Frank & J. D. Richards, "Phased array radar antennas" | scan loss, fill time, TTD/subarrays | cited | ST |
| T6 | D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 | ABCD/S conversions, hybrids | cited | PS |
| T7 | S. K. Koul, B. Bhat, *Microwave and Millimeter Wave Phase Shifters*, vols. I–II, Artech House, 1991 | phase-shifter families (scope) | cited, not read | PS |
| T8 | G. L. Charvat, *Small and Short-Range Radar Systems*, CRC Press, 2014 | switched-array radar builds | cited (publisher page) | DIY |
| T9 | Not consulted (planned in the task list; gap): A. K. Visser, *Array and Phased Array Antenna Basics*, Wiley 2005; R. L. Haupt, *Antenna Arrays: A Computational Approach*, Wiley 2010; W. L. Stutzman & G. A. Thiele, *Antenna Theory and Design*, 3rd ed., 2012 | — | not read | — |

## Lecture notes, app notes, tutorials
| # | Citation | Used for | Status | Pages |
|---|---|---|---|---|
| A1 | P. Delos, B. Broughton, J. Kraft, "Phased Array Antenna Patterns — Part 1: Linear Array Beam Characteristics and Array Factor," *Analog Dialogue* 54(2), May 2020. http://www.oh3ac.fi/ADI_PhasedArrayAntennaPatterns_part1.pdf ; analog.com/en/resources/analog-dialogue/articles/phased-array-antenna-patterns-part1.html (app note) | ΔΦ = 2πd sinθ/λ (95° example), HPBW 0.886λ/(Nd cosθ), 2D²/λ, element factor | READ | AF, ST |
| A2 | Same authors, "Part 2: Grating Lobes and Beam Squint," *Analog Dialogue* 54(2), June 2020. analog.com/media/en/analog-dialogue/volume-54/number-2/phased-array-antenna-patterns-part-2-grating-lobes-and-beam-squint.pdf (app note) | d_max = λ/(1+\|sinθ\|), squint formula, TTD/hybrid | READ | ST, AR |
| A3 | Same authors, "Part 3: Sidelobes and Tapering," *Analog Dialogue* 54(3), July 2020. analog.com/media/en/analog-dialogue/volume-54/number-3/phased-array-antenna-patterns-part-3-sidelobes-and-tapering.pdf (app note) | taper/window analogy, θ_RES, QSLL −7.5 dB @ 2 bits, 6 dB/bit | READ | ST, TP, PL |
| A4 | N. K. Nikolova, McMaster University ECE antenna lectures 14 ("Linear array theory II") and 15 ("Linear arrays III: binomial and Dolph–Tschebyscheff"), 2025. ece.mcmaster.ca/faculty/nikolova/antenna_dload/current_lectures/ (lecture notes) | HW derivation (2.94/N, 1.789), D ≈ 2Nd/λ, binomial HPBW/D, Dolph N = 10 example, d_max | READ | AF, TP |
| A5 | P. Delos, "System-level LO phase noise model for phased arrays with distributed phase-locked loops," Analog Devices technical article, 2018 (reprint: embeddedcomputing.com) (app note) | correlated reference vs uncorrelated VCO noise, 10 log N | READ (reprint) | AR |
| A6 | P. Delos, M. Jones, M. Robertson, "RF transceivers enable forced spurious decorrelation in digital beamforming phased arrays," Analog Devices / *Microwave Journal*, 2018 (app note) | 10 log N for uncorrelated noise & spurs, LO offset + NCO decorrelation | abstract (search summary) | AR |
| A7 | M. Lichtman, *PySDR: A Guide to SDR and DSP using Python*, ch. "Hands-on with Phaser," pysdr.org/content/phaser (tutorial) | CN0566 architecture, spacing, calibration files, steering formula | READ | PS, CAL, DIY, AR, ST |
| A8 | Analog Devices, *ADALM-PHASER (CN0566) Phased Array Exploration Platform* wiki and CN0566 circuit note, wiki.analog.com/resources/eval/user-guides/circuits-from-the-lab/cn0566 (app note) | platform description | READ (landing page only) | DIY |

## Peer-reviewed papers
| # | Citation | Used for | Status | Pages |
|---|---|---|---|---|
| P1 | W. W. Hansen, J. R. Woodyard, "A new principle in directional antenna design," *Proc. IRE* 26(3):333–345, 1938 | HW endfire | cited (via A4; verified numerically) | AF |
| P2 | S. A. Schelkunoff, "A mathematical theory of linear arrays," *Bell Syst. Tech. J.* 22(1):80–107, 1943 | polynomial/unit-circle view, null placement | cited | AF, TP |
| P3 | C. L. Dolph, "A current distribution for broadside arrays which optimizes the relationship between beam width and side-lobe level," *Proc. IRE* 34(6):335–348, 1946 | Dolph–Chebyshev | cited (derived & verified) | TP |
| P4 | T. T. Taylor, "Design of line-source antennas for narrow beamwidth and low side lobes," *IRE Trans. Antennas Propag.* AP-3(1):16–28, 1955, doi:10.1109/TPGAP.1955.5720407 | Taylor n̄ | citation confirmed; formulas re-derived & verified vs scipy | TP |
| P5 | R. S. Elliott, "Mechanical and electrical tolerances for two-dimensional scanning antenna arrays," *IRE Trans. Antennas Propag.* 6(1):114–120, 1958 | random-error sidelobe formula | abstract | TP |
| P6 | E. T. Bayliss, "Design of monopulse antenna difference patterns with low sidelobes," *Bell Syst. Tech. J.* 47(5):623–650, 1968, archive.org/details/bstj47-5-623 | Bayliss Δ taper; polynomial table of A, ξ₁…ξ₄, p₀ (Fig. 4); line-source sine series | READ (W5-E8, archive.org text) | TP, SYN |
| P7 | E. D. Sharp, "A triangular arrangement of planar-array elements that reduces the number needed," *IRE Trans. Antennas Propag.* 9(2):126–129, 1961 | 13.4% saving | abstract (verified numerically) | PL |
| P8 | P. W. Hannan, "The element-gain paradox for a phased-array antenna," *IEEE Trans. Antennas Propag.* 12(4):423–433, 1964, doi:10.1109/TAP.1964.1138237 | embedded element gain 4πA/λ² cosθ | abstract | AF, ST, PL |
| P9 | P. W. Hannan, "Proof that a phased-array antenna can be impedance matched for all scan angles," *Radio Science* 2(3):361–369, 1967 | wide-angle matching possibility | title/venue | PL |
| P10 | H. A. Wheeler, "Simple relations derived from a phased-array antenna made of an infinite current sheet," *IEEE Trans. Antennas Propag.* 13(4):506–514, 1965 | secθ/cosθ scan resistance | cited, not read | PL |
| P11 | D. M. Pozar, D. H. Schaubert, "Scan blindness in infinite phased arrays of printed dipoles," *IEEE Trans. Antennas Propag.* 32(6):602–610, 1984 | Floquet–surface-wave blindness | abstract | PL |
| P12 | D. M. Pozar, "The active element pattern," *IEEE Trans. Antennas Propag.* 42(8):1176–1178, 1994 | AEP predicts scan performance | abstract | PL |
| P13 | P.-S. Kildal, A. Vosoogh, S. Maci, "Fundamental directivity limitations of dense array antennas: a numerical study using Hannan's embedded element efficiency," *IEEE Antennas Wireless Propag. Lett.*, 2015, doi:10.1109/LAWP.2015.2473136 (author version publications.lib.chalmers.se/records/fulltext/230414/local_230414.pdf) | e_emb = 1 − Σ\|S\|², Hannan asymptote πd_xd_y/λ² | READ | PL |
| P14 | C. J. Miller, "Minimizing the effects of phase quantization errors in an electronically scanned array," *Proc. 1964 Symp. Electronically Scanned Array Techniques and Applications*, RADC-TDR-64-225, vol. 1, pp. 17–38 | quantisation lobes, decorrelation | cited, not read | ST |
| P15 | M. Longbrake, "True time delay beamsteering for radar," *Proc. IEEE NAECON*, 2012 | TTD vs phase | cited via A2 | ST |
| P16 | S. Stein, "On cross coupling in multiple-beam antennas," *IRE Trans. Antennas Propag.* 10(5):548–557, 1962 | orthogonal-beam condition | cited, not read | AR |
| P17 | J. Butler, R. Lowe, "Beam-forming matrix simplifies design of electronically scanned antennas," *Electronic Design* 9:170–173, 1961 | Butler matrix | cited, not read | AR |
| P18 | W. Rotman, R. F. Turner, "Wide-angle microwave lens for line source applications," *IEEE Trans. Antennas Propag.* 11(6):623–632, 1963 | Rotman lens | cited, not read | AR |
| P19 | S. Mano, T. Katagi, "A method for measuring amplitude and phase of each radiating element of a phased array antenna," *Electronics and Communications in Japan* 65-B(5):58–64, 1982 | REV | abstract (method re-derived) | CAL |
| P20 | H. M. Aumann, A. J. Fenn, F. G. Willwerth, "Phased array antenna calibration and pattern prediction using mutual coupling measurements," *IEEE Trans. Antennas Propag.* 37(7):844–850, 1989 | mutual-coupling calibration | abstract (method re-derived) | CAL |
| P21 | "Phased array calibration based on rotating-element harmonic electric-field vector with time modulation," arXiv:2504.16107, 2025 (html) | classic REV summary, limitations | READ (summary) | CAL |
| P22 | A. J. Weiss, B. Friedlander, "Eigenstructure methods for direction finding with sensor gain and phase uncertainties," *Circuits Syst. Signal Process.* 9(3):271–300, 1990 | self-calibration | cited, not read | CAL |
| P23 | J. Capon, "High-resolution frequency-wavenumber spectrum analysis," *Proc. IEEE* 57(8):1408–1418, 1969 | MVDR/Capon | cited (derived) | DOA |
| P24 | I. S. Reed, J. D. Mallett, L. E. Brennan, "Rapid convergence rate in adaptive arrays," *IEEE Trans. Aerosp. Electron. Syst.* 10(6):853–863, 1974 | SMI, K ≈ 2N | abstract (reproduced by MC) | DOA |
| P25 | O. L. Frost III, "An algorithm for linearly constrained adaptive array processing," *Proc. IEEE* 60(8):926–935, 1972 | LCMV | cited | DOA |
| P26 | B. D. Carlson, "Covariance matrix estimation errors and diagonal loading in adaptive arrays," *IEEE Trans. Aerosp. Electron. Syst.* 24(4):397–401, 1988 | diagonal loading | cited | DOA |
| P27 | A. J. Barabell, "Improving the resolution performance of eigenstructure-based direction-finding algorithms," *Proc. IEEE ICASSP*, 1983, pp. 336–339 | Root-MUSIC | cited | DOA |
| P28 | R. O. Schmidt, "Multiple emitter location and signal parameter estimation," *IEEE Trans. Antennas Propag.* 34(3):276–280, 1986 | MUSIC | cited (derived) | DOA |
| P29 | T.-J. Shan, M. Wax, T. Kailath, "On spatial smoothing for direction-of-arrival estimation of coherent signals," *IEEE Trans. ASSP* 33(4):806–811, 1985 | spatial smoothing | cited | DOA |
| P30 | M. Wax, T. Kailath, "Detection of signals by information theoretic criteria," *IEEE Trans. ASSP* 33(2):387–392, 1985 | MDL/AIC | cited | DOA |
| P31 | P. Stoica, A. Nehorai, "MUSIC, maximum likelihood, and Cramér–Rao bound," *IEEE Trans. ASSP* 37(5):720–741, 1989 | CRB | cited (derived) | DOA |
| P32 | R. Roy, T. Kailath, "ESPRIT — estimation of signal parameters via rotational invariance techniques," *IEEE Trans. ASSP* 37(7):984–995, 1989 | ESPRIT | cited | DOA |
| P33 | H. Krim, M. Viberg, "Two decades of array signal processing research: the parametric approach," *IEEE Signal Process. Mag.* 13(4):67–94, 1996 | DOA review | abstract | DOA |

## Data sheets and vendor documentation
| # | Citation | Used for | Status | Pages |
|---|---|---|---|---|
| D1 | Analog Devices, *ADAR1000 8–16 GHz 4-channel X/Ku-band beamformer*, data sheet Rev. B (7/2022), analog.com/media/en/technical-documentation/data-sheets/adar1000.pdf | all ADAR1000 specs (NF 8 dB, IIP3 −7 dBm, 2.8°/2° rms, 0.5 dB/0.2 dB rms, 121 beams, 20 ns, currents) | READ (distributor mirror) | ST, PS, CAL, DIY |
| D2 | Analog Devices, *ADTR1107 6–18 GHz front-end IC* | Psat 25 dBm, gains, NF 2.5 dB | abstract (search summary) | PS |
| D3 | Analog Devices, *ADAR4002 0.5–19 GHz true time delay unit* | 7-bit, 508 ps/4 ps, 254 ps/2 ps, DSA | abstract | PS |
| D4 | Analog Devices HMC647A / HMC649A / HMC642A 6-bit digital phase shifters; HMC928 analog phase shifter (obsolete); ADL5390 vector multiplier | band, LSB, rms errors, IL | abstract | PS |
| D5 | Qorvo QPC2108 2.5–4 GHz 6-bit phase shifter; RFMW pricing | rms < 2.8°, < 0.4 dB; US$171 (1–24) | abstract | PS |
| D6 | pSemi PE44820 8-bit phase shifter 1.7–2.2 GHz | 1.4° steps | abstract | PS |
| D7 | Anokiwave (Qorvo) AWMF-0108 26.5–29.5 GHz beamformer | 5-bit phase/gain, NF 5 dB, etc. | abstract | PS |
| D8 | Mini-Circuits JSPHS-2484+ voltage-variable phase shifter, minicircuits.com/pdfs/JSPHS-2484+.pdf | phase-vs-voltage table, IL, max power | READ | PS, DIY |
| D9 | KrakenRF, KrakenSDR documentation wiki (github.com/krakenrf/krakensdr_docs/wiki: Home, 03 Background Theory, 04 Antenna Array Setup, 05 Web Interface Controls); krakensdr_doa and heimdall_daq_fw repositories; Crowd Supply page & pricing updates | specs, noise-source calibration, UCA radius rule, spacing multiplier, cable tolerance, MUSIC recommendation, decorrelation for ULA, source count, squelch, price history | READ (wiki pages; repos only at README level) | AF, AR, CAL, DOA, DIY |
| D10 | RTL-SDR.com, KerberosSDR quickstart guide (rtl-sdr.com/ksdr) and product listings | 4 ch, noise source, disconnect antennas when syncing, Linux native | abstract | DIY |
| D11 | Analog Devices EngineerZone threads on Pluto Rev C 2nd channel; ADI HDL Pluto project docs; plutoplus/plutoplus GitHub issue #66 | Pluto Rev C/D 2R2T | abstract (forum — anecdotal) | DIY |
| D12 | DigiKey listing EVAL-CN0566-RPIZ | ≈ US$2,875 | abstract (search) | DIY |
| D13 | G. L. Charvat, course pages (sites.google.com/view/glcharvat — IAP 2012 MIMO/phased array) and MIT Professional Education "Build a multi-channel search and track radar" | switched-array/phased-array teaching builds | READ (landing pages) | DIY |
| D14 | RF Essentials, "Beamforming network | Butler matrix & Rotman lens" glossary, rfessentials.com | qualitative Butler/Rotman; its crossover numbers contradicted | READ (summary) — low reliability | AR |

## Internal KB pages relied on (consistency)
- [14-sdr-dsp/sdr-hardware-survey](../14-sdr-dsp/sdr-hardware-survey.md) — 2026-09 SDR prices/specs (Pluto, B210, KrakenSDR US$749–775).
- [15-lora-ism-radios/ism-band-plans-duty-cycle](../15-lora-ism-radios/ism-band-plans-duty-cycle.md), [lora-sensitivity-and-link-budget](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md) — Singapore 433 MHz 10 mW e.r.p.; SF9/125 ≈ −129 dBm.
- [08-antennas/patch-antennas](../08-antennas/patch-antennas.md), [yagi-uda-and-log-periodic](../08-antennas/yagi-uda-and-log-periodic.md) — patch dimensions/efficiency; Yagi gains (433/915 MHz, MoM).
- [00-math-foundations/special-functions-bessel-sinc](../00-math-foundations/special-functions-bessel-sinc.md) — Dolph–Chebyshev 8-element/30 dB weights (identical to ours: 0.262/0.519/0.812/1).

## Own verification scripts
`tools/verify/array_factor.py`, `array_steering.py`, `array_planar.py` (uses `ant_mom_wire.py` from 08-antennas),
`array_taper.py`, `array_architecture.py`, `array_components.py`, `array_calibration.py`, `array_doa.py`, `array_diy.py`.

## Added by W5-E8 (2026-10-12)
Page abbreviations: SYN array-pattern-synthesis · CON conformal-and-cylindrical-arrays · STK stacking-and-arraying-yagis.

| # | Citation | Used for | Status | Pages |
|---|---|---|---|---|
| E1 | P. M. Woodward, *J. IEE* 93(IIIA):1554–1558, 1946; P. M. Woodward, J. D. Lawson, *J. IEE* 95(37):363–370, 1948 | sampled-beam synthesis | cited, not read (re-derived, verified) | SYN |
| E2 | H. Steyskal, "Synthesis of antenna patterns with prescribed nulls," *IEEE Trans. AP* 30(2):273–279, 1982 | projection null steering | cited, not read (re-derived, verified) | SYN |
| E3 | S. P. Applebaum, "Adaptive arrays," *IEEE Trans. AP* 24(5):585–598, 1976 | cancellation-beam picture | cited | SYN |
| E4 | H. Lebret, S. Boyd, "Antenna array pattern synthesis via convex optimization," *IEEE Trans. SP* 45(3):526–532, 1997 | min-max/null synthesis as LP/SOCP | cited, not read (verified vs Dolph) | SYN |
| E5 | R. S. Elliott, *Antenna Theory and Design*, rev. ed., Wiley-IEEE, 2003, ch. 5 | Taylor/Bayliss, perturbation synthesis | cited | SYN |
| E6 | C. A. Balanis, *Antenna Theory* 4e, ch. 7 (§7.3–7.5 synthesis), §6.12 (circular arrays), ch. 8 (mutual impedance) | method set | cited | SYN, CON, STK |
| E7 | L. Josefsson, P. Persson, *Conformal Array Antenna Theory and Design*, Wiley-IEEE, 2006 | conformal arrays, polarization, sector illumination | cited, not read | CON |
| E8 | R. F. Harrington, *Time-Harmonic Electromagnetic Fields*, 1961, ch. 5; C. A. Balanis, *Advanced Engineering Electromagnetics* 2e, ch. 11–12 | cylindrical-wave solutions, 2-D MoM | cited (derivations redone, MoM own) | CON |
| E9 | R. E. Munson, "Conformal microstrip antennas and microstrip phased arrays," *IEEE Trans. AP* 22(1):74–78, 1974 | wraparound antennas | cited, not read | CON |
| E10 | B. Sheleg, *Proc. IEEE* 56(11):2016–2027, 1968; D. E. N. Davies, "Circular arrays," in Rudge et al., *Handbook of Antenna Design* vol. 2, 1983; C. P. Mathews, M. D. Zoltowski, *IEEE Trans. SP* 42(9):2395–2407, 1994 | phase modes, matrix-fed circular arrays, UCA-ESPRIT | cited, not read (identity verified) | CON |
| E11 | J. D. Moell, T. N. Curlee, *Transmitter Hunting*, TAB, 1987 | pseudo-Doppler DF practice | cited (amateur literature) | CON |
| E12 | I. White (G3SEK), "Stacking Yagi antennas," ifwtech.co.uk/g3sek/stacking/stacking2.htm | capture areas, 2.5–2.9 dB, DL6WU λ/(2 sin(B/2)) | READ (raw HTML) — amateur engineering literature | STK |
| E13 | L. B. Cebik (W4RNL), "2-meter Yagi stacks, part 1," antenna2.github.io/cebik/content/vhf/2mstack.html | NEC stack increments and gain-peak spacings over ground | WebFetch summary only (rule 8) — amateur | STK |
| E14 | ARRL *Antenna Book* 24e (2019), VHF/UHF systems chapter; DJ9BV "Optimum stacking distances" (DUBUS); K7MEM calculator | harnesses, stacking formula | cited / search summaries — amateur | STK |
| E15 | NASA GSFC Wallops, *Sounding Rockets User Handbook*, 2015, §5.6 (via 08 antennas-on-rockets) | wraparound telemetry antennas | via KB | CON |

Own verification: `tools/verify/e8_synthesis.py`, `e8_conformal.py`, `e8_yagi_stack.py` (PyNEC); figures in `kb/12-phased-arrays/figures/e8-*.png`.
