# 08-antennas — Antennas

Scope: how antennas work and how to design, simulate and measure them — from the definitions
(directivity, gain, efficiency, aperture, polarization) through wire antennas (dipoles, monopoles,
loops, Yagis, LPDAs, helices), planar antennas (patches, PCB/chip antennas), aperture antennas
(horns, dishes), fundamental size limits, baluns and common-mode current, measurement and simulation
(NEC, openEMS) — with the reader's applications in focus: 433 MHz / 868–915 MHz LoRa telemetry on
rockets and ground stations, and GNSS (ZED-F9P, MAX-M10S). EM derivations of radiation live in
[02-electromagnetics](../02-electromagnetics/radiation-from-currents-hertzian-dipole.md); link budgets in
[09](../09-propagation-link-budget/link-budget-methodology.md); arrays and beamforming in
[12](../12-phased-arrays/array-factor-linear-arrays.md); balun circuits in
[06](../06-rf-circuits/baluns-and-rf-transformers.md); VNA calibration in
[17](../17-test-measurement/vna-fundamentals-calibration.md); tool installation in
[16](../16-simulation-tools/installing-tools-macos.md).

## Reading order (beginner → advanced)
1. [antenna-fundamentals](antenna-fundamentals.md) — the vocabulary and the key results (D, G, realized gain, A_e = λ²G/4π, EIRP).
2. [dipoles-and-monopoles](dipoles-and-monopoles.md) — the workhorse antennas; real cutting lengths; ground planes.
3. [antenna-polarization-and-circular-polarization](antenna-polarization-and-circular-polarization.md) — AR, RHCP/LHCP, PLF, roll.
4. [antenna-matching-and-baluns](antenna-matching-and-baluns.md) — why the coax becomes part of the antenna.
5. [antenna-measurement](antenna-measurement.md) — S11 vs efficiency; gain, pattern, AR; DIY SDR ranges.
6. [yagi-uda-and-log-periodic](yagi-uda-and-log-periodic.md) — ground-station directional antennas (DL6WU 433/915 MHz designs).
7. [helical-antennas](helical-antennas.md) — CP ground antennas; the Kraus-gain overestimate.
8. [patch-antennas](patch-antennas.md) — design equations and worked designs (L1, 2.45, 5.8 GHz, 915 MHz).
9. [pcb-and-chip-antennas](pcb-and-chip-antennas.md) — IFA/meander/chip antennas, ground-plane dependence, matching.
10. [gnss-antennas](gnss-antennas.md) — patches/helices, active antennas, u-blox requirements.
11. [antennas-on-rockets](antennas-on-rockets.md) — placement, materials, axial nulls, roll, plume, recovery.
12. [loop-antennas](loop-antennas.md) — small, magnetic and full-wave loops; ferrite rods.
13. [small-antenna-limits](small-antenna-limits.md) — Wheeler/Chu/McLean; efficiency–bandwidth; fractal claims.
14. [horn-reflector-aperture-antennas](horn-reflector-aperture-antennas.md) — aperture efficiency, horns, dishes, feeds.
15. [antenna-simulation-nec-openems](antenna-simulation-nec-openems.md) — NEC/MoM and openEMS/FDTD practice and verification.
16. [antenna-identification-guide](antenna-identification-guide.md) — recognise antenna types, band from element length, measure stock antennas.
17. [slot-antennas](slot-antennas.md) — Babinet/Booker, PCB and edge-notch slots (openEMS), slotted waveguides.
18. [multiband-and-wideband-antennas](multiband-and-wideband-antennas.md) — discone (NEC), bicone/bow-tie, Vivaldi, spirals, SDR receive antennas.
19. [wire-antennas-hf-random-wire-fan-dipole](wire-antennas-hf-random-wire-fan-dipole.md) — random wire, fan/trap dipoles, inverted-V, OCF, G5RV, NVIS (NEC).
20. [inductive-coupling-rfid-nfc-wpt](inductive-coupling-rfid-nfc-wpt.md) — mutual inductance, k²Q₁Q₂, NFC coil + matching, Qi, RFID.
21. [lens-and-reflectarray-antennas](lens-and-reflectarray-antennas.md) — mm-wave lenses, Luneburg, reflectarrays.

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [antenna-fundamentals](antenna-fundamentals.md) | pattern, D, G, realized gain, efficiencies, A_e derivation, beamwidth–D, R_r, bandwidth/Q, reciprocity, EIRP, dBi/dBd/dBic | mixed | high |
| [dipoles-and-monopoles](dipoles-and-monopoles.md) | sinusoidal current, 73 + j42.5 Ω (Si/Ci), MoM shortening vs thickness, monopole 36.5 Ω, radial droop, whips on small boards, folded dipole ratio, sleeve, J-pole, EFHW, loaded/top-loaded monopoles | mixed | high |
| [loop-antennas](loop-antennas.md) | small-loop R_r, loss/efficiency, magnetic loops, full-wave loop, ferrite rods, noise-limited reception | mixed | high |
| [patch-antennas](patch-antennas.md) | TL & cavity models, Hammerstad fringing, Jackson CAD Q/BW/efficiency, feeds, surface waves, CP mode split, designs for L1/2.45/5.8 GHz/915 MHz | mixed | high |
| [helical-antennas](helical-antennas.md) | normal/axial mode, Kraus vs King & Wong vs Emerson vs our MoM, design examples, QFH | mixed | high |
| [yagi-uda-and-log-periodic](yagi-uda-and-log-periodic.md) | parasitic mechanism, mutual impedance, DL6WU algorithm, MoM-verified 433/915 MHz designs, 3-el Yagi, stacking, crossed Yagi, LPDA (Carrel) | mixed | high |
| [horn-reflector-aperture-antennas](horn-reflector-aperture-antennas.md) | aperture efficiency, optimum pyramidal horn, dish gain, taper vs spillover, Ruze, feeds, cantenna | mixed | high |
| [pcb-and-chip-antennas](pcb-and-chip-antennas.md) | IFA/PIFA/meander/chip, TI reference designs, Johanson/Ignion data, keep-out, pi matching, ESP32 placement | mixed | high |
| [gnss-antennas](gnss-antennas.md) | bands, RHCP, patch/helix/chip, active antennas and noise cascade, ground plane, AR, PCV, u-blox F9P/M10 requirements, rocket installations | mixed | high |
| [antenna-matching-and-baluns](antenna-matching-and-baluns.md) | common-mode current, choke targets, ferrite mixes, sleeve and coax baluns, Guanella/Ruthroff, measuring CM | mixed | high |
| [antenna-measurement](antenna-measurement.md) | S11 limits, far-field criteria, ranges and reflections, gain transfer, three-antenna, Wheeler cap, AR, SDR patterns | mixed | high |
| [antennas-on-rockets](antennas-on-rockets.md) | airframe materials, axial nulls vs flight geometry, link margins, roll/CP, plume attenuation, recovery, coexistence | mixed | medium |
| [small-antenna-limits](small-antenna-limits.md) | Wheeler, Chu, McLean (verified), CP bound, FBW–Q–efficiency, Harrington, fractal/tiny-antenna claims | mixed | high |
| [antenna-polarization-and-circular-polarization](antenna-polarization-and-circular-polarization.md) | ellipse, AR, IEEE sense (verified), PLF closed form, reflection flip, CP generation, spin modulation | mixed | high |
| [antenna-simulation-nec-openems](antenna-simulation-nec-openems.md) | MoM/FDTD basics, NEC-2 rules and limits, tool comparison, AGT and convergence, openEMS setup | mixed | high |
| [slot-antennas](slot-antennas.md) | Babinet–Booker derivation (Z_s Z_d = η²/4), offset feed, cavity backing, PCB slots and 915 MHz edge notch (openEMS), slotted-waveguide design (Stevenson/Elliott), SIW, EMC slots | mixed | high |
| [wire-antennas-hf-random-wire-fan-dipole](wire-antennas-hf-random-wire-fan-dipole.md) | random wire + 9:1 unun (NEC check of "magic lengths"), EFHW vs random, fan/crossed and trap dipoles, inverted-V, OCF, G5RV, NVIS, verticals and ground loss | mixed | medium |
| [inductive-coupling-rfid-nfc-wpt](inductive-coupling-rfid-nfc-wpt.md) | Neumann/Maxwell M, k vs distance, η_max = U²/(1+√(1+U²))² derivation, Kurs 2007 check, NFC coil/Q/EMC/C1–C2 worked design (AN11755), LF/UHF RFID, Qi, far-field harvesting | mixed | high |
| [multiband-and-wideband-antennas](multiband-and-wideband-antennas.md) | conical/bow-tie impedance, discone design + NEC (VSWR and pattern tilt), self-complementary 188 Ω, Vivaldi, spirals, sleeves, multiband tricks, SDR receive noise-limited table | mixed | medium |
| [lens-and-reflectarray-antennas](lens-and-reflectarray-antennas.md) | hyperbolic and Luneburg lenses (verified), 24/77 GHz lens gains, why not at UHF, zoning, reflectarray quantisation and bandwidth | intermediate | medium |
| [antenna-identification-guide](antenna-identification-guide.md) | field guide to antenna types, band from element length, gain from size, measured mistuned stock antennas | intro | medium |
| [_sources](_sources.md) | full bibliography and list of verification scripts | — | — |

## Domain FAQ (top questions → page#section)
- *Does a 5 dBi antenna amplify my signal?* → [antenna-fundamentals#intuition-no-math](antenna-fundamentals.md#intuition-no-math)
- *Why is free-space path loss frequency dependent?* → [antenna-fundamentals#level-2--derivations](antenna-fundamentals.md#level-2--derivations)
- *How long do I cut a 433 MHz dipole?* → [dipoles-and-monopoles#level-1--the-numbers-you-use](dipoles-and-monopoles.md#level-1--the-numbers-you-use)
- *Why does my whip on the flight computer perform badly?* → [dipoles-and-monopoles#finite-ground-planes-and-small-boards](dipoles-and-monopoles.md#finite-ground-planes-and-small-boards)
- *Why does my SWR change when I touch the cable?* → [antenna-matching-and-baluns#worked-examples](antenna-matching-and-baluns.md#worked-examples)
- *What Yagi should I build for the ground station?* → [yagi-uda-and-log-periodic#worked-examples](yagi-uda-and-log-periodic.md#worked-examples)
- *Why do I lose telemetry near apogee?* → [antennas-on-rockets#level-1--look-angle-and-pattern-loss](antennas-on-rockets.md#level-1--look-angle-and-pattern-loss)
- *Linear or circular polarization for tracking a rolling rocket?* → [antenna-polarization-and-circular-polarization#worked-examples](antenna-polarization-and-circular-polarization.md#worked-examples)
- *Can I put the antenna in a carbon-fibre airframe?* → [antennas-on-rockets#level-3--fields-around-the-airframe-plume-and-spin](antennas-on-rockets.md#level-3--fields-around-the-airframe-plume-and-spin)
- *What size is a 2.45 GHz patch on FR-4, and why is it only ~2 dBi?* → [patch-antennas#worked-examples](patch-antennas.md#worked-examples)
- *Why is my GNSS patch weak inside the rocket?* → [gnss-antennas#worked-examples](gnss-antennas.md#worked-examples)
- *How much LNA gain does the ZED-F9P need?* → [gnss-antennas#design-equations--rules-of-thumb](gnss-antennas.md#design-equations--rules-of-thumb)
- *Is Kraus's helix gain formula right?* → [helical-antennas#level-2--why-axial-mode-works-and-the-realistic-gain](helical-antennas.md#level-2--why-axial-mode-works-and-the-realistic-gain)
- *Can a tiny chip antenna be efficient at 433 MHz?* → [small-antenna-limits#worked-examples](small-antenna-limits.md#worked-examples)
- *Does S11 tell me my antenna is efficient?* → [antenna-measurement#tldr](antenna-measurement.md#tldr)
- *NEC or openEMS for my design?* → [antenna-simulation-nec-openems#tool-comparison](antenna-simulation-nec-openems.md#tool-comparison)

- *How does Wi-Fi work in a metal laptop / can a metal airframe be the antenna?* → [slot-antennas#slot-in-a-ground-plane--enclosure-wi-fi-in-metal-laptops-metal-airframes](slot-antennas.md#slot-in-a-ground-plane--enclosure-wi-fi-in-metal-laptops-metal-airframes)
- *Can I put a 915 MHz antenna on my board without a keep-out?* → [slot-antennas#open-ended-notch-slot-on-a-board-edge--a-915-mhz-option](slot-antennas.md#open-ended-notch-slot-on-a-board-edge--a-915-mhz-option)
- *What random-wire length should I use?* → [wire-antennas-hf-random-wire-fan-dipole#tldr](wire-antennas-hf-random-wire-fan-dipole.md#tldr)
- *How do I design and match a 13.56 MHz NFC antenna?* → [inductive-coupling-rfid-nfc-wpt#worked-examples](inductive-coupling-rfid-nfc-wpt.md#worked-examples)
- *Is a discone really 25–1300 MHz?* → [multiband-and-wideband-antennas#discone-and-why-25-1300-mhz-needs-care](multiband-and-wideband-antennas.md#discone-and-why-251300-mhz-needs-care)
- *Does antenna length matter for a receive-only SDR?* → [multiband-and-wideband-antennas#receive-only-sdr-antennas-does-length-matter](multiband-and-wideband-antennas.md#receive-only-sdr-antennas-does-length-matter)
- *Can I add a lens to my 24 GHz radar module?* → [lens-and-reflectarray-antennas#worked-examples](lens-and-reflectarray-antennas.md#worked-examples)
- *What antenna is that, and is my stock antenna tuned?* → [antenna-identification-guide#field-guide](antenna-identification-guide.md#field-guide)
- *Can I use a 2.4 GHz antenna at 900 MHz?* → [antenna-fundamentals#common-mistakes--misconceptions](antenna-fundamentals.md#common-mistakes--misconceptions)
- *Does aluminium vs copper change my dipole length? How high is the tip voltage?* → [dipoles-and-monopoles#conductor-material-length-and-loss](dipoles-and-monopoles.md#conductor-material-length-and-loss)
- *Which antenna and how much G/T do I need to receive a CubeSat or Meteor-M, and how do I track it?* → [09 satellite links](../09-propagation-link-budget/satellite-links-doppler-tracking.md#worked-examples)

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
Balanis *Antenna Theory* (4th ed.); Kraus & Marhefka *Antennas for All Applications*; Orfanidis
*Electromagnetic Waves and Antennas* (free); Stutzman & Thiele; Volakis *Antenna Engineering Handbook*
(Jackson's microstrip chapter); IEEE Std 145 and 149; King & Wong 1980 and Emerson 1995 (helix gain);
McLean 1996 / Chu 1948 / Wheeler 1947 (small antennas); Jackson & Alexopoulos 1991 (patch CAD);
DL6WU / G3SEK (Yagis); Carrel 1961 (LPDA); TI DN007/DN023/DN024/AN043/AN058; u-blox GNSS antenna
app note and ZED-F9P integration manual; NASA Sounding Rockets User Handbook. W5-E2 additions: Booker 1946 (Babinet for slots), W1GHZ ch. 7 (slotted waveguide), Stearns 2007 (discone), Gibson 1979 (Vivaldi), Kurs 2007 (resonant WPT), NXP AN11755 (NFC matching), Mohan 1999 (spiral inductance), Varney (G5RV), Brown–Lewis–Epstein 1937 (radials).

## Known gaps
- Amateur-motor (APCP) plume attenuation at 433/915 MHz — no quantitative data found.
- Nose-cone detuning and whip-on-flight-computer performance need openEMS models of the team's actual hardware.
- QFH dimensions not numerically verified (MoM model not yet built).
- Several classic papers cited from secondary sources only (Butson & Thompson LPDA correction, Thal, Gustafsson, Kilgus, Garg CP rule); IEEE Std 149 not read directly.
- MAX-M10S LNA/blocking specifics and UHF ferrite bead impedances at 433/915 MHz to be filled from datasheets (domains 04/18).
- Cross-code NEC-2 vs our MoM comparison for the DL6WU Yagis (needs xnec2c/PyNEC install, domain 16).
- W5-E2 open items: Vivaldi/spiral/printed bow-tie not simulated (openEMS); discone NEC model only to 700 MHz; random-wire study uses idealised groundings; G5RV 20 m VSWR (Varney 1.8 vs NEC 2.3–7) and OCF balun ratio (NEC ≈ 100 Ω vs common 4:1/6:1) unresolved; microstrip-crossing slot feed and 5.8 GHz PCB slot not simulated; Qi2 MPP frequency only from secondary sources; active receive loops (MLA-30 class) and linked dipoles not yet covered; airframe slot antennas need a model of the real tube.
