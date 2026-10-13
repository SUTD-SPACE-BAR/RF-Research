# 17-test-measurement — bibliography

Full citations for sources used in `kb/17-test-measurement/`. Reliability tags follow CONVENTIONS §3.
"Read" = the raw text (PDF via pdftotext, or raw HTML) was read by the research agent (W3-C3, 2026-09-27/29);
"summary" = only a search/WebFetch summary was available (numbers quoted from it are flagged in the pages);
"cited" = relied on via a secondary source. Pages using each source are in brackets
(vna = vna-fundamentals-calibration, nano = nanovna-librevna-practical, sa = spectrum-analyzers,
scope = oscilloscopes-and-probing-for-rf, pwr = rf-power-measurement, nf = noise-figure-measurement,
pn = phase-noise-measurement, range = antenna-range-ota-testing, sdr = sdr-as-test-equipment,
gen = signal-generators-and-sources, lab = lab-setup-by-budget, fix = fixtures-and-deembedding,
play = rf-bring-up-debug-playbook, bench = bench-measurement-recipes [W5-E3, 2026-10-02]).

## Application notes, primers and seminar notes
1. D. Rytting, "Network Analyzer Error Models and Calibration Methods," Agilent/ARFTG seminar slides, mirror emlab.uiuc.edu/ece451/appnotes/Rytting_NAModels.pdf — 1-port 3-term, 12/16/8-term models, calibration families, switch terms, residual-error table, unknown-thru determinant. (seminar/app note; read) [vna, nano]
2. Agilent AN 1287-3, *Applying Error Correction to Network Analyzer Measurements*, 5965-7709E, 2002 — response/enhanced-response/two-port cal, adapter effects, uncertainty examples, TRL/TRL*, non-insertable devices. (app note; read) [vna, nano, fix, play]
3. Keysight AN 5989-4840, *Specifying Calibration Standards and Kits for Keysight Vector Network Analyzers* (ucsb.edu mirror) — offset delay/loss/Z0, C0–C3 and L0–L3 models and scaling, load types, TRL class table (±20° rule). (app note; read) [vna, fix]
4. B. Walker (Copper Mountain Technologies), *VNA Master Class — VNA Calibration, Kits, Error Terms and Calculation*, 2020 handout — open/short models (T4311 example), SOLR, data-based standards, least-squares 1-port. (vendor seminar; read) [vna, fix]
5. Agilent AN 1287-12, *Time Domain Analysis Using a Network Analyzer*, 5989-5723EN (qsl.net mirror) — response-resolution Table 1-3, alias-free range, windows. (app note; read) [nano]
6. Keysight AN 150, *Spectrum Analysis Basics*, 5952-0292 (2016; electrooptical.net mirror) — architecture, ST = k·span/RBW², detectors, noise-as-a-signal corrections (1.05 dB, 2.5 dB, ENBW 1.05–1.13), DANL/NF, internal distortion, preselection, phase noise on an SA. (app note; read) [sa, pn, play]
7. Keysight AN 1303, *Spectrum and Signal Analyzer Measurements and Noise*, 5966-4008E. (app note; cited) [sa]
8. C. Rauscher, V. Janssen, R. Minihold, *Fundamentals of Spectrum Analysis*, Rohde & Schwarz, 2001. (primer/textbook; cited) [sa]
9. Keysight AN 1449-2, *Fundamentals of RF and Microwave Power Measurements (Part 2): Power Sensors and Instrumentation*, 5988-9214EN (cloudinary mirror) — sensor types, square-law region to ≈ −20 dBm, transition to ≈ 0 dBm, thermocouple −30…+20 dBm, wide-range diode −70…+20 dBm. (app note; read) [pwr, play]
10. Keysight AN 1449-1 and 1449-3 (Parts 1 and 3) — definitions; uncertainty budgets and mismatch. (app notes; cited) [pwr]
11. Keysight AN 57-2, *Noise Figure Measurement Accuracy — The Y-Factor Method*, 5952-3706E (qsl.net mirror) — ENR, Y-factor, calibration and second-stage correction, ENR choice, jitter, loss/temperature/mismatch. (app note; read) [nf, play]
12. Keysight AN 57-3, *10 Hints for Making Successful Noise Figure Measurements*, 5980-0288EN (repeater-builder mirror). (app note; read) [nf]
13. Keysight AN 57-1, *Fundamentals of RF and Microwave Noise Figure Measurements*, 5952-8255E. (app note; cited) [nf]
14. Maxim/ADI AN 2875, "Three Methods of Noise Figure Measurement." (app note; summary) [nf]
15. Tektronix, *ABCs of Probes* primer (download.tek.com 02_ABCs-of-Probes-Primer) — t_r ≈ 0.35/BW (0.40–0.45 > 1 GHz), 3–5× rule, probe capacitance table, 10× 500 Ω probes for 50 Ω inputs, 11 pF + 6-inch lead rings at ~140 MHz. (vendor primer; read) [scope, play]
16. TI AN058 (SWRA161), *Antenna Selection Guide* — PCB-antenna VNA method with semi-rigid cable. (app note; cited via domain 08) [fix]
17. TI DN024 (SWRA227) — CTIA OTA metrics. (app note; cited via domain 08) [range]

## Standards
18. IEEE Std 149-1979 (R2008), *IEEE Standard Test Procedures for Antennas*. (standard; cited via Balanis/domain 08) [range]
19. IEEE Std 370-2020, *Electrical Characterization of Printed Circuit Board and Related Interconnects at Frequencies up to 50 GHz* (2x-thru de-embedding). (standard; cited via scikit-rf docs) [fix]
20. IEEE Std 1139-2008, *Definitions of Physical Quantities for Fundamental Frequency and Time Metrology — Random Instabilities*. (standard; cited) [pn]
21. CTIA, *Test Plan for Wireless Device Over-the-Air Performance*. (industry standard; cited) [range]

## Peer-reviewed papers, preprints and textbooks
22. G. F. Engen and C. A. Hoer, "Thru-Reflect-Line: An Improved Technique for Calibrating the Dual Six-Port Automatic Network Analyzer," *IEEE Trans. MTT* 27(12), pp. 987–993, 1979. (peer-reviewed; cited via [1], [3]) [vna, fix]
23. A. Ferrero and U. Pisani, "Two-Port Network Analyzer Calibration Using an Unknown 'Thru'," *IEEE Microwave and Guided Wave Letters* 2(12), pp. 505–507, 1992. (peer-reviewed; cited) [vna]
24. R. B. Marks, "A Multiline Method of Network Analyzer Calibration," *IEEE Trans. MTT* 39(7), pp. 1205–1215, 1991. (peer-reviewed; cited) [vna]
25. E. Rubiola and F. Vernotte, "The cross-spectrum experimental method," arXiv:1003.0113, 2010. (tutorial preprint; read) [pn]
26. E. Rubiola, *Phase Noise and Frequency Stability in Oscillators*, Cambridge University Press, 2008. (textbook; cited) [pn]
27. J. Dunsmore, *Handbook of Microwave Component Measurements*, 2nd ed., Wiley, 2020. (textbook; cited) [vna]
28. C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed., Wiley, 2016, ch. 17. (textbook; cited) [range]
29. H. Johnson and M. Graham, *High-Speed Digital Design*, Prentice Hall, 1993; H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley, 2009. (textbooks; cited) [scope]

## Vendor documentation and datasheets
30. nanovna.com (Hugen) overview; hugen79/NanoVNA-H README; ttrftech/NanoVNA README; DiSlord/NanoVNA-D README. (community/vendor; read) [nano, vna, lab]
31. NanoRFE, "NanoVNA V2" page, nanorfe.com/nanovna-v2.html. (vendor; read) [nano, vna, lab]
32. Zeenko, LiteVNA page and *LiteVNA User Guide* (randl.com mirror). (vendor; read) [nano]
33. J. Käsemann, LibreVNA README and *Preliminary Specifications* (github.com/jankae/LibreVNA). (open-source vendor; read) [vna, nano, sa, pn]
34. NanoVNA-Saver README (github.com/NanoVNA-Saver/nanovna-saver). (open-source docs; read) [nano]
35. nVhelp, oristopo.github.io/nVhelp — NanoVNA output-level measurements. (community docs; WebFetch summary) [nano]
36. tinySA wiki (tinysa.org): Specification (tinySA, tinySA Ultra), Limitations. (vendor docs; read) [sa, pn, gen, nf]
37. Siglent, *SSA3000X Plus Data Sheet* DS0703P-E04B. (datasheet; read) [sa, pn]
38. Analog Devices, AD8307 and AD8318 datasheets (foxdelta and octopart mirrors). (datasheets; read) [pwr]
39. Analog Devices, ADF4351 datasheet Rev. 0 (utoronto mirror). (datasheet; read) [gen]
40. Great Scott Gadgets, HackRF One documentation (hackrf.readthedocs.io). (vendor docs; read) [sdr, gen]
41. Analog Devices Wiki, ADALM-PLUTO Detailed Specifications. (vendor wiki; read) [sdr]
42. RTL-SDR Blog V4 product pages (rtl-sdr.com). (vendor; summary) [sdr]
43. Semtech, SX1261/2 datasheet — sensitivity conditions. (datasheet; read) [nf, play]
44. MegiQ, Balanced and UFL Calibration Kit user guide. (vendor; listing) [vna, nano]
45. scikit-rf 2.0.1 documentation/docstrings: `skrf.calibration` (OnePort, SOLT, TwelveTerm, TRL, UnknownThru…) and `skrf.calibration.deembedding` (IEEEP370 2x-thru classes, OpenShort…). (open-source docs; read) [vna, fix]
46. SDRangel noise-figure plugin readme (github.com/f4exb/sdrangel). (open-source docs; summary) [nf, sdr]

## Forums, blogs and retailers (anecdotal / indicative)
47. hugen79/NanoVNA-H issue #18 and nanovna-users@groups.io threads (Si5351 drive levels, output level, common-mode chokes, antenna measurement). (forum — anecdotal; search snippets) [nano]
48. "Noise Figure Measurements of RTL-SDR Dongles" (IDC-Online reprint of an amateur article). (blog — anecdotal; read) [sdr]
49. Price listings: R&L Electronics, SeeSii, Siglent NA store, Saelig, rtl-sdr.com review (2026). (retailer — indicative) [lab, nano]

## Internal
50. Space Bar avionics knowledge base (~/.claude/knowledge/space-bar-avionics/): engineering-ethos, flight-computer-design-lessons, hil-bench-testing-methods, avionics-b-v3-primary-fc. (team notes) [play]
51. This repository: `tools/verify/meas_*.py` (12 scripts). (verification) [all]

## Added by W5-E3 (bench-measurement-recipes, 2026-10-02)
52. Hewlett-Packard/Keysight, *Spectrum Analysis… Pulsed RF*, Application Note 150-2 (5952-1039), https://www.keysight.com/us/en/assets/7018-06767/application-notes/5952-1039.pdf — line vs pulse spectrum, α_L = 20 log(τ·PRF), α_P = 20 log(τ·K·B), K ≈ 1.5, validity conditions. (app note; read) [bench]
53. JCGM 100:2008 (GUM), *Evaluation of measurement data — Guide to the expression of uncertainty in measurement*. (standard; general use) [bench]
54. M. L. Crawford, "Generation of standard EM fields using TEM transmission cells," *IEEE Trans. EMC* 16(4):189–195 (1974), doi:10.1109/TEMC.1974.303364. (peer-reviewed; citation/abstract) [bench]
55. M. P. Robinson et al., "Analytical formulation for the shielding effectiveness of enclosures with apertures," *IEEE Trans. EMC* 40(3):240–248 (1998). (peer-reviewed; cited) [bench]
56. R. Brewer (Laird), "Design considerations for minimizing large aperture effects in shielding," *Interference Technology* (2002). (trade article; WebFetch summary) [bench]
57. Keysight PNA help, "Hot S22 Measurement," https://na.support.keysight.com/pna/help/WebHelp9_9/Tutorials/Hot_S22_Measurement.htm. (manufacturer docs; search summary) [bench]
58. IZ7BOJ, "Power and current characterization on SX1268 LoRa module (E22-400M30S)," blog (2022). (blog — anecdotal; WebFetch summary) [bench]
59. Mini-Circuits, VLM-33-S+ limiter datasheet (also used in 14/sdr-front-end-protection-and-filtering). (datasheet; read) [bench]
60. This repository: `tools/verify/e3_bench.py`. (verification) [bench]

## Added by W5-E10 (2026-10-12) — interference-hunting-and-rf-immunity
61. J. Brown (K9YC), *A Ham's Guide to RFI, Ferrites, Baluns, and Audio Interfacing*, Rev. 7, 2019. http://audiosystemsgroup.com/RFI-Ham.pdf (expert tutorial) [rfi]
62. BEAMA, *The RCD Handbook* (selection and application of RCDs). (industry guide) [rfi]
63. ARRL, "GFCI and AFCI Devices," https://www.arrl.org/gfci-and-afci-devices ; M. Gruber (ed.), *The ARRL RFI Book*, 3rd ed., 2010. (organisation / book) [rfi]
64. J. Moell (K0OV), HomingIn "Equipment Ideas for Radio Foxhunting" (body fade, offset attenuator). (practitioner) [rfi]
65. Pololu, "Dealing with Motor Noise"; Hackaday "Ferrites versus Ethernet in the ham shack" (2024); ISPreview (Aberhosan SHINE, 2020). (app note / blog / news) [rfi]
66. This repository: `tools/verify/e10_rfi.py`. (verification) [rfi]

## Added by W5-E11 (resonator-and-cavity-perturbation-permittivity-measurement)
- D. M. Pozar, *Microwave Engineering*, 4th ed., §6.6–6.7 (coupling, perturbation). (textbook)
- L. F. Chen et al., *Microwave Electronics: Measurement and Materials Characterization*, Wiley 2004. (textbook)
- J. Krupka et al., *J. Eur. Ceram. Soc.* 21, 2001 (SPDR); M. D. Janezic, J. Baker-Jarvis, *IEEE Trans. MTT* 47(10), 1999 (split cylinder; IPC TM-650 2.5.5.13). (peer-reviewed / standard)
- J. Baker-Jarvis, E. J. Vanzura, W. A. Kissick, NIST TN 1355-R, 1993 (transmission/reflection). R. B. Marks, *IEEE Trans. MTT* 39(7), 1991 (multiline). (report / peer-reviewed)
- Verification: `tools/verify/e11_permittivity.py` (15/17).
