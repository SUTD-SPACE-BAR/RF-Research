# 16-simulation-tools — bibliography

Full citations for sources used in `kb/16-simulation-tools/`. Reliability tags follow CONVENTIONS §3.
"Read" = the text/source was read directly (raw docs, source code, PDF text); "cited" = relied on via
textbook knowledge or a WebFetch/search summary (treated with caution per CONVENTIONS rule 8).
Pages using each source are in brackets.

## Textbooks and monographs
1. A. Taflove and S. C. Hagness, *Computational Electrodynamics: The Finite-Difference Time-Domain Method*, 3rd ed., Artech House, 2005 — Yee algorithm, Courant stability, numerical dispersion, PML, NF2FF. (textbook; cited) [em-solvers, openems-workflow, simulation-validation]
2. R. F. Harrington, *Field Computation by Moment Methods*, Macmillan, 1968 (IEEE Press reprint 1993). (textbook; cited) [em-solvers, nec]
3. W. C. Gibson, *The Method of Moments in Electromagnetics*, 2nd ed., CRC Press, 2014. (textbook; cited) [em-solvers, nec]
4. J.-M. Jin, *The Finite Element Method in Electromagnetics*, 3rd ed., Wiley-IEEE Press, 2014 — vector Helmholtz weak form, edge elements, ABC/PML, ports. (textbook; cited) [em-solvers, simulation-validation]
5. K. S. Kundert, J. K. White, A. Sangiovanni-Vincentelli, *Steady-State Methods for Simulating Analog and Microwave Circuits*, Kluwer, 1990. (textbook; cited) [harmonic-balance]
6. S. A. Maas, *Nonlinear Microwave and RF Circuits*, 2nd ed., Artech House, 2003. (textbook; cited) [harmonic-balance]
7. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — matching, filters, S/ABCD cascades, microstrip synthesis. (textbook; cited) [spice, python-rf-toolkit, calculators, landscape]
8. G. Matthaei, L. Young, E. M. T. Jones, *Microwave Filters, Impedance-Matching Networks, and Coupling Structures*, Artech House, 1980. (textbook; cited) [spice]
9. B. C. Wadell, *Transmission Line Design Handbook*, Artech House, 1991. (handbook; cited) [calculators]
10. W. L. Oberkampf and C. J. Roy, *Verification and Validation in Scientific Computing*, Cambridge UP, 2010. (textbook; cited) [simulation-validation]

## Manuals and tool documentation
11. G. J. Burke and A. J. Poggio, *Numerical Electromagnetics Code (NEC) — Method of Moments*, LLNL UCID-18834, 1981, Parts I–III. https://www.nec2.org/ (manual; cited, card formats cross-checked against PyNEC API) [nec, installing]
12. G. J. Burke, *NEC-4.2 Method of Moments*, LLNL, 2011. (manual; cited) [nec]
13. H. Vogt, G. Atkinson, P. Nenzi et al., *Ngspice User's Manual* v41+, https://ngspice.sourceforge.io/docs.html — analyses incl. `.sp` port syntax, control language. (manual; cited + behaviour tested with ngspice-47) [spice, installing]
14. openEMS documentation source `doc-src/` (install: package, requirements, clone-build-install, check; concepts) and Python API source (`ports.py`, `nf2ff.py`, `openEMS.pyx`, `openems.cpp`), github.com/thliebig/openEMS-Project, master 2026-09-25; https://docs.openems.de (docs and source; read) [installing, openems-workflow, em-solvers]
15. openEMS Python tutorials `Simple_Patch_Antenna.py`, `MSL_NotchFilter.py` (v0.37). (tool documentation; read) [openems-workflow]
16. scikit-rf documentation v2.x, https://scikit-rf.readthedocs.io/ (tool documentation; cited + API tested with 2.0.1) [python-rf-toolkit]
17. T. Molteno, python-necpp / PyNEC 2.3.4, https://github.com/tmolteno/python-necpp ; PyPI metadata. (tool documentation; read + tested) [nec, installing]
18. KiCad source `common/transline_calculations/*.cpp` (gitlab.com/kicad/code/kicad, master 2026-09). (source; read) [calculators]
19. Qucs-S project page https://ra3xdh.github.io/ ; Homebrew tap `ra3xdh/homebrew-qucs-s` cask files. (tool documentation; read) [installing, spice, harmonic-balance]
20. xnec2c README, github.com/KJ7LNW/xnec2c. (tool documentation; read) [installing, nec]
21. AWS Labs Palace documentation https://awslabs.github.io/palace/ ; github.com/awslabs/palace (Apache-2.0). (tool documentation; cited via WebFetch + GitHub API) [em-solvers]
22. OpenParEM, https://openparem.org/ (GPLv3, v2.1 May 2025). (tool documentation; cited via WebFetch) [em-solvers]
23. MEEP (github.com/NanoComp/meep, GPL-2.0; conda-forge pymeep 1.34 osx-arm64), gprMax (GPL-3.0), Elmer FEM — repository/package metadata, 2026-09-29. (metadata; read) [em-solvers]
24. RadarSimPy documentation https://radarsimx.github.io/radarsimpy/ (installation, free tier). (tool documentation; cited via WebFetch) [python-rf-toolkit]
25. PyPI metadata for scikit-commpy 0.8.0, pyargus 1.1, pyadi-iio 0.0.21, pyrtlsdr 0.5.0 (2026-09-27). (metadata; read) [python-rf-toolkit]

## Vendor documents (licences, limits)
26. Ansys Help, "HFSS Student Limitations" (v25.1) — 64 000 3-D elements, 8 000 surface, 2 000 2-D triangles, ≤ 4 cores, Linux unsupported. (vendor; cited via WebFetch, consistent with search snippet) [em-solvers, landscape]
27. Cadence, "AWR University Program FAQ" (PDF) — 6-month free academic Microwave Office licence, personal Windows PC, Macs not supported. https://awr.cadence.com/support/AWR_University_FAQ.pdf (vendor; PDF text read) [harmonic-balance, installing, em-solvers]
28. Keysight PathWave University Program docs, https://docs.keysight.com/university/ (vendor; search-level) [harmonic-balance]
29. R. Lewallen, EZNEC website https://www.eznec.com/ — EZNEC Pro+ v7.0 free, NEC-2D internal, no support. (vendor; cited via WebFetch) [nec]
30. Sonnet Software, "Sonnet Lite Information" (help v18) — 64 MB memory limit. (vendor; cited via WebFetch; level/port limits only from secondary listings — unverified) [em-solvers, harmonic-balance]
31. JLCPCB, "User Guide to the JLCPCB Impedance Calculator" — mask and copper assumptions. (vendor; cited via WebFetch) [calculators]
32. Saturn PCB Design, Saturn PCB Toolkit pages https://saturnpcb.com/ (vendor; search-level) [calculators]
33. Homebrew formula/cask metadata (`brew info`): ngspice 47, ltspice 26.0.2 (pkg), wine-stable (disabled 2026-09-01), gnuradio 3.10.12 (deprecated), xquartz 2.8.6. (package metadata; read) [installing]

## Peer-reviewed papers and standards
34. K. S. Yee, "Numerical solution of initial boundary value problems involving Maxwell's equations in isotropic media," *IEEE Trans. Antennas Propag.*, 14(3):302–307, 1966. (peer-reviewed) [openems-workflow]
35. T. Liebig, A. Rennings, S. Held, D. Erni, "openEMS — a free and open source equivalent-circuit (EC) FDTD simulation platform…," *Int. J. Numerical Modelling*, DOI 10.1002/jnm.1875, 2012. (peer-reviewed) [openems-workflow]
36. S. M. Rao, D. R. Wilton, A. W. Glisson, "Electromagnetic scattering by surfaces of arbitrary shape," *IEEE Trans. Antennas Propag.*, 30(3):409–418, 1982. (peer-reviewed) [em-solvers]
37. J. C. Rautio and R. F. Harrington, "An electromagnetic time-harmonic analysis of shielded microstrip circuits," *IEEE Trans. MTT*, 35(8):726–730, 1987. (peer-reviewed) [em-solvers]
38. L. W. Nagel, *SPICE2*, UC Berkeley ERL Memo M520, 1975; C.-W. Ho, A. E. Ruehli, P. A. Brennan, "The modified nodal approach to network analysis," *IEEE Trans. CAS*, 22(6):504–509, 1975. (primary / peer-reviewed) [spice]
39. B. Gustavsen and A. Semlyen, "Rational approximation of frequency domain responses by vector fitting," *IEEE Trans. Power Delivery*, 14(3):1052–1061, 1999. (peer-reviewed) [python-rf-toolkit]
40. A. Arsenovic et al., "scikit-rf: an open source Python package for microwave network creation, analysis, and calibration," *IEEE Microwave Magazine*, 23(1):98–105, 2022. (peer-reviewed) [python-rf-toolkit]
41. E. Hammerstad and Ø. Jensen, "Accurate models for microstrip computer-aided design," IEEE MTT-S Digest, 1980, 407–409; H. A. Wheeler, *IEEE Trans. MTT* 25(8):631–647, 1977; G. Ghione and C. U. Naldi, *Electronics Letters* 20(4):179–181, 1984 and *IEEE Trans. MTT* 35(3):260–267, 1987. (peer-reviewed) [calculators, openems-workflow]
42. R. C. Melville, P. Feldmann, J. Roychowdhury, "Efficient multi-tone distortion analysis of analog integrated circuits," Proc. IEEE CICC, 1995. (peer-reviewed) [harmonic-balance]
43. L. F. Richardson, *Phil. Trans. R. Soc. A* 226:299–361, 1927; P. J. Roache, *J. Fluids Eng.* 116(3):405–413, 1994; I. B. Celik et al., *J. Fluids Eng.* 130(7):078001, 2008. (peer-reviewed) [simulation-validation]
44. ASME V&V 20-2009; IEEE Std 1597.1-2008 and 1597.2-2010 (CEM validation, FSV). (standards) [simulation-validation]
45. IPC-2141A, *Design Guide for High-Speed Controlled Impedance Circuit Boards*, 2004. (standard) [calculators]
46. G. Hoch (DL6WU), "Extremely long Yagi antennas," *VHF Communications* 3/1982. (magazine; cited via ant_yagi.py) [nec]

## Expert articles
47. L. B. Cebik (W4RNL), NEC-2 modelling articles incl. "When not to use NEC," https://antenna2.github.io/cebik/ (expert articles; cited) [nec]

## Internal
48. Space Bar avionics knowledge base: `engineering-ethos.md`, `simulation-validation-methods.md` (~/.claude/knowledge/space-bar-avionics/). (internal) [simulation-validation]
49. This repository's verification scripts: `tools/verify/sim_ngspice_examples.py`, `sim_nec_vs_mom.py`, `sim_openems_msl.py`, `sim_openems_patch.py`, `sim_harmonic_balance.py` (W3-C2); `analog_ngspice.py` (W2-B1); `tline_fd2d.py`, `tline_microstrip.py`, `tline_cpwg.py`, `tline_matching.py` (W1-A4); `ant_mom_wire.py`, `ant_mom_general.py`, `ant_yagi.py`, `ant_patch.py` (W1-A6); `noise_*.py`, `prop_*.py` (W1-A5); `lora_*.py` (W2-B6); `em_skin_depth.py` (W1-A3); `array_factor.py` (W2-B5); `radar_detection_cfar.py` (W2-B4). (verification)
