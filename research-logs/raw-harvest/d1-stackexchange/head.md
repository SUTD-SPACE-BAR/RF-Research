# D1 — Stack Exchange gap analysis (W4-D1)

Status: **complete** (2026-09-29; KB state checked at 173 pages). Owner: W4-D1. Log: `research-logs/W4-D1-stackexchange.md`.

## 0. Method (short)

- **Source of questions.** Stack Exchange API 2.3, queried with `curl` (raw JSON, so titles, scores and
  view counts are exact; WebFetch summaries were not used, per CONVENTIONS rule 8). 90 list queries, sorted
  by votes (plus `hot` for rf/antenna/ham): electronics.SE ×48 tags (rf, antenna, impedance-matching,
  transmission-line, radio, lora, sdr, power-amplifier, noise(+rf), oscillator, pll, filter+rf,
  pcb-design+rf, emc, radar, smith-chart, vna, spectrum-analyzer, mixer, balun, coaxial, gps, wireless,
  modulation, adc, operational-amplifier+noise/+stability, crystal, microstrip, 433mhz, receiver,
  transmitter, transceiver, dipole, lna, phase-noise, shielding, ground-plane, FM, AM, ferrite,
  impedance+rf, decoupling+rf); ham.SE top-300 overall + 17 tags (antenna-theory, propagation,
  coaxial-cable, feed-line, impedance-matching, license, legal, software-defined-radio, rfi, balun, yagi,
  antenna-tuner, grounding, rtl-sdr, uhf, satellites, measurement); dsp.SE ×21 tags (radar, sdr, fft,
  modulation, beamforming, doa, array-signal-processing, digital-communications, demodulation,
  synchronization, chirp, gnuradio, sampling, doppler, matched-filter, ofdm, pll, decimation,
  window-functions, fsk, snr). There are no `emi`, `network-analyzer`, `rf-amplifier` or `noise-figure`
  tags on electronics.SE; `emc`, `vna` and `power-amplifier` were used instead.
- **Selection.** 6 792 distinct questions harvested → top-N per tag (N = 4–80 depending on how relevant
  the tag is) → 886 → 200 removed by hand as off-topic (power-grid "transmission lines", audio mixers and
  amplifiers, USB/HDMI/RS-485 digital, ham operating etiquette/callsign admin, audio/speech DSP) →
  **686 questions classified** (electronics 418, ham 147, dsp 121).
- **Coverage check.** For each question: pick a domain; compare with FAQ.md (rebuilt 2026-09-29, 160
  pages; 173 by the end of the run) and the "Questions this page answers" list of every page (re-extracted live, because pages kept
  landing during the run); grep kb/ for the key terms; open the section when unsure. **covered** = a page
  clearly answers this specific question (a listed question, or a section/worked example that does);
  **partial** = the topic is there but the specific point, misconception or practical step is not;
  **missing** = nothing usable. A spot-check of 10 "covered" rows downgraded 4 (the penetration-vs-frequency
  and carrier-vs-data-rate myths were not actually stated anywhere). Rows in domains that grew during the
  run (06, 11, 12, 13, 14, 17, 18, 19) were re-checked at the end; 41 rows were re-assessed and 34 upgraded after the new
  06 receiver-architectures/frequency-multipliers, 11 fmcw/cw-doppler/ambiguity, 12 beamforming-architectures,
  13 stackups, 14 nco-ddc/multirate and 17 spectrum-analyzers/rf-power pages landed. A second, late pass
  (same day, KB at 173 pages) upgraded 19 more rows and downgraded none, using the new 11 clutter-and-mti /
  mimo-radar-virtual-arrays, 14 software-demodulation, 16 spice-circuit-simulation / openems-workflow, 17 oscilloscopes /
  phase-noise-measurement and 19 certification / lab-safety pages.
- **Caveat.** Domains 13 (1 page written), 16 (4), 18 (2) and 20 (0) were mostly still unwritten at check
  time, so many of their "missing" rows will be closed by pages already planned in INDEX.md. §2 marks each
  cluster **planned** (the INDEX already has a page for it) or **NEW** (no page is planned; needs a new
  page or a new section).

## 1. Summary

**686 questions: 411 covered (59.9 %) · 188 partial (27.4 %) · 87 missing (12.7 %).**

| Site | covered | partial | missing | total |
|---|---|---|---|---|
| electronics.SE | 253 | 110 | 55 | 418 |
| ham.SE | 75 | 52 | 20 | 147 |
| dsp.SE | 83 | 26 | 12 | 121 |

| Domain | covered | partial | missing | total | comment |
|---|---|---|---|---|---|
| 00 math | 9 | 0 | 0 | 9 | fully covered |
| 01 circuits | 8 | 2 | 0 | 10 | |
| 02 EM | 21 | 5 | 1 | 27 | gaps: iron-powder cores, shielding practice |
| 03 lines/matching | 59 | 18 | 3 | 80 | strong; gaps: bends, radial stubs, ladder line, tuners, digital termination |
| 04 components | 17 | 12 | 1 | 30 | gaps: crystal layout, 32.768 kHz, core measurement |
| 05 analog | 21 | 14 | 0 | 35 | practical op-amp recipes are partial |
| 06 RF circuits | 34 | 19 | 5 | 58 | gaps: superregen, DLL, LNB, diplexers/duplexers |
| 07 noise/linearity | 10 | 7 | 0 | 17 | phase-noise measurement pitfalls |
| 08 antennas | 67 | 26 | 12 | 105 | biggest demand; **GNSS receiver operation absent**; slot/lens/random-wire/fan-dipole absent |
| 09 propagation | 15 | 10 | 5 | 30 | gaps: penetration-vs-frequency myth, WPT/harvesting, practical HF |
| 10 comms | 39 | 13 | 3 | 55 | strong; niche sync methods partial |
| 11 radar | 26 | 7 | 5 | 38 | strong after fmcw/cw/ambiguity/MIMO/clutter pages; SAR, terminology, hobby modules pending |
| 12 phased arrays | 6 | 13 | 7 | 26 | **adaptive beamforming / DOA** is the gap |
| 13 PCB/EMC | 3 | 6 | 31 | 40 | **largest gap** (only the stackups page written) |
| 14 SDR/DSP | 40 | 9 | 5 | 54 | gaps: signal ID, SDR hardware, FFT-bin zeroing |
| 15 LoRa/ISM | 12 | 8 | 0 | 20 | hardware-integration details partial |
| 16 simulation | 3 | 1 | 0 | 4 | SPICE + openEMS pages closed 3; tool landscape pending |
| 17 test & meas. | 19 | 11 | 2 | 32 | VNA/SA/scope/phase-noise good; SDR-as-instrument, bench practice pending |
| 18 parts | 0 | 1 | 1 | 2 | connectors |
| 19 regulations/safety | 2 | 5 | 5 | 12 | spectrum allocation pending; lab-safety/certification pages lack lightning, grounding, fixes |
| 20 projects | 0 | 1 | 1 | 2 | beginner "first radio" recipes |

Where demand concentrates (share of the 686): antennas 15 %, transmission lines/matching 12 %, RF
circuits 8 %, comms 8 %, SDR/DSP 8 %, PCB/EMC 6 % — and PCB/EMC has by far the worst coverage (8 %
covered). Highest-traffic uncovered single questions: GPS 1 PPS (125 k views), USB connector shield
grounding (139 k), Baofeng-to-walkie-talkie legality (154 k), higher-frequency penetration (110 k),
32.768 kHz crystals (88 k), beginner "what do I need for a basic RF circuit" (86 k), zeroing FFT bins
(122 votes, 58 k).

## 2. Top 40 missing/partial topics (ranked)

Rank score = relevance (1–3, to building radios/radars/LoRa/arrays/antennas for this reader) ×
[log10(Σviews) + log10(Σvotes)] × (1 + 0.15·n) × (1 + 0.3·missing share). n = questions in the cluster;
row numbers refer to §4. "Target" says where the answer belongs and whether that page is **planned**
(already in INDEX.md) or **NEW**.

| Rank | Topic cluster | n (missing) | Σvotes / Σviews | Rows (§4) | Target | What the answer needs |
|---|---|---|---|---|---|---|
| 1 | PCB ground planes, pours and splits | 11 (10) | 176 / 66.7 k | 239, 245, 246, 283, 284, 285, 287, 289, 371, 381, 477 | 13/grounding-and-return-paths + 13/mixed-signal-layout (planned) | When (almost never) to split a plane vs partitioning over one plane; pour or not on 2-layer RF boards; stitching of pours; no floating islands; pour clearance next to CPWG; ground under crystals/oscillators; the return-current picture for each case, using JLC 2/4-layer examples. |
| 2 | Adaptive beamforming and DOA estimation | 14 (7) | 91 / 12.2 k | 4, 5, 6, 10, 12, 13, 14, 15, 16, 17, 51, 52, 93, 601 | 12/adaptive-beamforming-doa (planned) | A non-matrix explanation of adaptive nulling; conventional vs MVDR/SMI; why adaptive nulls are narrower than the beam; diagonal loading for robustness; MUSIC in practice (snapshots, source-count estimation, coherent sources and spatial smoothing, grid bias); TDOA/GCC; hands-on radio direction finding (fox hunting, Watson-Watt, pseudo-Doppler). |
| 3 | RF layout rules, launches and review | 11 (6) | 106 / 57.0 k | 206, 301, 347, 348, 352, 395, 397, 398, 400, 403, 404 | 13/rf-layout-rules, 13/connectors-and-launches, 13/rf-pcb-review-checklist (planned) | General RF PCB rules; when trace bends (mitred vs curved) matter, with numbers checked in openEMS; radial/butterfly stubs; matched via transitions (return vias, anti-pads, via delay); soldering RG316 straight to a board and edge-launch SMA/MMCX footprints; a layout-review checklist. |
| 4 | **GNSS receiver operation** | 7 (6) | 307 / 213.2 k | 274, 275, 276, 277, 278, 282, 632 | **NEW** — e.g. 08/gnss-receiver-operation (20/gnss-front-end-design covers only the RF chain) | TTFF (cold/warm/hot), almanac vs ephemeris, A-GNSS; channels and correlators; satellite clocks and the control segment; 1 PPS and timing receivers; 10–25 Hz nav rates vs dynamics; GNSS is receive-only; 10 MHz/1 PPS/GPSDO. For rockets add dynamic-platform models, CoCom altitude/velocity limits and re-acquisition after boost. |
| 5 | Spectrum allocation, band ID and certification | 9 (3) | 178 / 207.8 k | 122, 125, 364, 457, 536, 552, 567, 580, 617 | 19/spectrum-allocation-ism-bands (planned); 19/certification-fcc-ce-imda (written 09-29; add failure-fix section) | Why 433.05–434.79 MHz is everywhere (ITU Region-1 ISM, cheap SAW-resonator OOK), where the 2.4 GHz ISM band came from (and the water-resonance myth); using band plans to identify signals (e.g. airband); whether ham HTs may be used on FRS/PMR, legality of cellular-band SDR; a pre-compliance test workflow and common fixes. |
| 6 | Bench test practice | 10 (2) | 113 / 94.1 k | 173, 295, 461, 476, 512, 514, 608, 638, 668, 671 | 17/rf-bring-up-debug-playbook, 17/sdr-as-test-equipment, 17/antenna-range-ota-testing (planned); 17/oscilloscopes-and-probing-for-rf (written 09-29) already closed the scope-FFT, probe-pickup and 50 Ω-input questions | Quick "is it transmitting" checks; measuring amplifier/generator output impedance; pulse spectra on an SA (line vs envelope); reading antenna-analyser R/X/SWR (sign ambiguity of X); calibrating an SWR meter with known loads; shield box + step attenuator for sensitivity/"bad reception" tests; near-field scanners; on-air tuning practice. |
| 7 | EMC/EMI practice and RF immunity | 11 (8) | 313 / 179.3 k | 236, 241, 242, 243, 248, 440, 466, 543, 600, 624, 634 | 13/emc-emi-fundamentals (planned) + 19/certification-fcc-ce-imda (written 09-29; add fixes) | Fixing a failed radiated-emissions test on a cable; Y-capacitors and SMPS CM filtering; edge-rate/series-R control; twisting and loop area; immunity (GSM 217 Hz buzz via audio rectification, GFCI trips, VDSL/cable RFI); hunting solar-inverter and neighbour RFI. (Near-field-probe hunting is now in 17/oscilloscopes-and-probing-for-rf.) |
| 8 | Antenna types not yet in the KB | 11 (5) | 151 / 84.2 k | 129, 147, 171, 175, 181, 566, 573, 611, 628, 646, 654 | **NEW** sections/page in 08 (e.g. 08/other-antenna-types) | Slot and aperture antennas in metal enclosures (laptops, rocket bodies); lens antennas and why they are rare below mm-wave; random-wire/end-fed non-resonant antennas + unun; fan/multiband dipoles; off-centre-fed dipoles; dual-band 315/433 PCB antennas; on-metal antennas; RFID/NFC reader coils and their matching; lumped L/C models of antennas; how feed-point impedance varies along an antenna. |
| 9 | Via stitching, via fences and edge plating | 5 (4) | 80 / 41.9 k | 154, 244, 251, 258, 349 | 13/vias-stitching-fencing (planned) | Stitch spacing rules (fraction of λ in the dielectric) and where they come from; why boards have plated edges and via rows along the edge; via fences along CPWG vs around chip antennas (never fence the radiator); how many vias is enough (link 04 via inductance). |
| 10 | Shielding and shield grounding | 9 (4) | 217 / 189.8 k | 189, 279, 370, 377, 465, 499, 500, 501, 502 | 13/shielding-and-isolation (planned) | Connector shell to chassis vs signal ground (direct, RC, ferrite); cable shields bonded at one or both ends (depends on frequency); shield-can design (seams, apertures, via fence under the can lip); electric vs magnetic shielding and why a sheet works but a wrap does not; foil and Faraday-cage tests with seams. |
| 11 | Superregenerative and simple discrete radios | 8 (3) | 90 / 94.4 k | 126, 137, 139, 140, 166, 271, 273, 448 | 06/receiver-architectures (add superregen section) + NEW beginner recipe in 20 | How superregen modules (XY-MK-5V) work — quench, poor selectivity, re-radiation — and what to replace them with (superhet OOK modules, CC1101); discrete FM receivers; one-transistor FM "bug" transmitters; AM modulator/detector circuits; crystal-radio detectors. |
| 12 | SDR hardware and practical SDR noise/spurs | 5 (0) | 35 / 49.9 k | 112, 113, 642, 679, 680 | 14/sdr-hardware-survey (planned), 17/sdr-as-test-equipment (planned) | SDR vs oscilloscope; SDR architectures (R820T tuner + RTL2832, AD936x zero-IF, direct sampling, RFSoC); USB/host noise fixes (ferrites, shielding, powered hubs); telling switcher spur combs from real signals; limits of an SDR as a spectrum analyser. |
| 13 | Practical op-amp/analog gaps | 8 (0) | 154 / 134.8 k | 238, 369, 383, 387, 388, 389, 466, 524 | 05/op-amps-real-limitations, 05/analog-signal-conditioning (add) | Choosing resistor values (noise vs bias current vs loading); bias path for AC-coupled non-inverting stages; noise gain < 1 stability trap in attenuators; compensating a MOSFET inside the loop; noise gain of summing amps; curing GSM-buzz RF rectification; 4–20 mA and differential long sensor lines. |
| 14 | DSP spectral-analysis pitfalls | 6 (2) | 234 / 197.0 k | 60, 64, 66, 67, 105, 120 | 14/fft-spectral-analysis-windows + 14/digital-filters-fir-iir (add) | Why zeroing FFT bins is a poor filter (circular convolution, time-domain aliasing, ringing) and what to do instead; estimating SNR from a noisy record; overlap-add vs overlap-save explained; windowing vs editing the spectrum; windows as smoothing kernels. |
| 15 | Station/lab safety | 6 (3) | 88 / 121.6 k | 170, 288, 551, 595, 610, 622 | 19/lab-safety-esd-high-power (written 09-29; add sections) | Why an ESD strap has a 1 MΩ series resistor; lightning protection and station/antenna grounding; DC-grounded antennas for static bleed; RF vs safety vs DC grounds; mobile-install power/ground. (ESD handling, TX-without-antenna and pyro RF safety are now covered.) |
| 16 | SDR signal identification and application recipes (unknown-signal ID, pagers, AIS, ATSC) | 4 (2) | 54 / 6.3 k | 70, 493, 605, 614 | 14/software-demodulation (written 09-29; add a signal-ID section) + 14/gnu-radio-and-software-stack (planned) | Workflow from an unknown signal to its modulation and baud (bandwidth, spectral lines/cyclostationarity, sigidwiki, inspectrum/URH); worked AIS (GMSK) and POCSAG examples; ATSC/DVB-T reception in GNU Radio. (AFSK, AM/FM/SSB, QPSK and OOK decoding are now covered by 14/software-demodulation.) |
| 17 | Penetration vs frequency (myth) | 3 (0) | 45 / 114.6 k | 165, 462, 482 | 09/atmospheric-rain-attenuation (add + Common mistakes) | Frequency trend of wall, glass and foliage loss from ~0.1 to 100 GHz (ITU-R P.2040/P.2109 data), with the exceptions; say explicitly that "higher frequency penetrates better" is wrong in general; metallised glass and through-glass couplers. |
| 18 | LoRa hardware integration | 5 (0) | 19 / 15.1 k | 212, 325, 327, 330, 336 | 20/lora-rocket-telemetry-link (planned) + 15/semtech-chip-family (add) | Walk through the SX127x (RFO/PA_BOOST) and SX126x reference matching, harmonic filter and RF switch; minimal BOM for a bare chip; how multi-SF gateway demodulators (SX1301/2) work; coexistence with ultra-narrowband (SigFox); a simple star/TDMA network. |
| 19 | Magnetic cores | 7 (1) | 101 / 40.0 k | 252, 254, 255, 256, 532, 676, 677 | 04/ferrites-and-beads, 04/inductors-at-rf (add); 17/fixtures-and-deembedding (planned) | Iron powder vs ferrite (mixes, μ, loss, Q); identifying an unknown core by measuring AL and Q; gapped cores; CM-choke equivalent circuits; measuring rod/toroid μ and loss vs frequency with a VNA; why cable ferrites are less common now. |
| 20 | RF connectors | 2 (1) | 31 / 49.9 k | 157, 665 | 18/connectors-and-cables-parts (planned) | U.FL vs I-PEX MHF generations (which mate), mating cycles, loss and frequency limits; assembling PL-259/N/SMA connectors (crimp vs solder). |
| 21 | Crystal/clock practicalities | 4 (1) | 203 / 197.6 k | 223, 224, 391, 393 | 04/crystals-and-resonators (add) | Why 32.768 kHz (2^15, tuning-fork cut, parabolic tempco); crystal layout rules and why app notes disagree; MCU internal RC accuracy vs a crystal; RC-oscillator temperature drift. |
| 22 | Antenna conductor material and construction | 5 (1) | 75 / 98.7 k | 334, 542, 564, 653, 684 | 08/dipoles-and-monopoles (add) | Material barely changes resonant length (diameter and insulation do) but does change loss; loss numbers for Cu/Al/steel/brass at HF–UHF; tip voltage vs power (corona, capacitor ratings); effect of bent tips. |
| 23 | Specialty front-end filtering | 6 (0) | 56 / 18.6 k | 266, 268, 380, 467, 473, 581 | 06/rf-filters-lc-saw-baw-cavity-microstrip (add), 06/lna-design Common mistakes | Diplexer design; repeater duplexers (pass/notch cavities); multi-band handset front ends; the "RC filter after the LNA lowers noise" myth; rejecting an out-of-band blocker (e.g. 5.8 GHz); loaded Q of critically coupled resonators. |
| 24 | Beginner starter path for a first RF circuit | 1 (0) | 44 / 86.5 k | 455 | **NEW** 20/first-rf-projects (or a section in 00/math-roadmap-for-rf) | Minimum bench (NanoVNA, tinySA, RTL-SDR, dummy load, attenuators) and three graded first builds with pass/fail tests. |
| 25 | Niche synchronisation methods | 6 (1) | 32 / 12.1 k | 29, 46, 47, 75, 87, 118 | 10/synchronization-carrier-timing (add) | Feed-forward ML vs Costas phase recovery; residual-carrier PSK (mod index < 90°); polyphase-filterbank timing recovery; FFT-based symbol sync; normalised cross-correlation for time-delay estimation; time-frequency matched filtering. |
| 26 | Matching concepts not yet explained | 5 (1) | 34 / 20.0 k | 264, 267, 312, 343, 503 | 03/impedance-matching-lumped-and-distributed (add) | How a matching network's internal reflections cancel (energy view); all-capacitor (tapped-C) matching; using an IC's impedance/S11 table; "negative inductance" in extracted models; AC (series-C) termination. |
| 27 | SAR/DBS and RF imaging (Doppler-to-azimuth, RF cameras, mechanically scanned radars, array outlines) | 4 (2) | 66 / 8.3 k | 95, 148, 153, 196 | 11/sar-and-imaging (planned); 11/mimo-radar-virtual-arrays (written 09-29) closed the virtual-array question | Doppler beam sharpening and SAR basics; "RF camera" resolution limits (aperture/λ); mechanically scanned radars; why array outlines are octagonal/circular. |
| 28 | Receiver power drain and LO leakage | 3 (1) | 100 / 19.8 k | 439, 445, 570 | 06/receiver-architectures (add) | Where receiver current goes (LNA, LO/PLL, ADC, DSP) and duty-cycling; why a transmitter cannot sense receivers except through LO leakage; why phones transmit so little. |
| 29 | Receive-site noise and interference | 3 (0) | 78 / 68.6 k | 456, 545, 618 | 07/thermal-noise-and-noise-temperature (ITU-R P.372 man-made noise), 07/dynamic-range-sfdr-blocking | Man-made noise levels and how to reduce them at the antenna; why signals superpose without "interfering" (linearity plus selectivity); why satellites split uplink and downlink bands (co-site desense). |
| 30 | PLL/DLL comparison and PLL bench tests | 3 (1) | 39 / 32.8 k | 85, 410, 415 | 06/vco-and-pll-synthesizers (add) | PLL vs DLL (what each locks, jitter behaviour, uses in MCUs/FPGAs); measuring a PLL's loop bandwidth on the bench (phase-noise hump, step or modulation response). |
| 31 | Simulation tool landscape | 1 (0) | 14 / 25.1 k | 475 | 16/tool-landscape-overview (planned); 16/spice-circuit-simulation and 16/openems-workflow (written 09-29) closed the LTspice and openEMS questions | Free RF tools compared (QUCS-S, ngspice/LTspice, openEMS, Sonnet Lite, scikit-rf, NEC) and when to use which. |
| 32 | Radar processing terminology (fast/slow time, "video", A-scope) | 3 (1) | 34 / 15.7 k | 90, 91, 427 | GLOSSARY + 11/pulsed-radar-and-pulse-compression (terms); 11/clutter-and-mti (written 09-29) now covers MTI | Name fast-time vs slow-time explicitly (the pages use the idea without the words); define radar "video" (detected/baseband signal); historical A-scope/PPI displays. |
| 33 | Analog/voice-mode odds and ends | 9 (2) | 217 / 60.3 k | 360, 361, 362, 535, 540, 555, 578, 583, 631 | 10/analog-modulation-am-fm-pm-ssb, 10/modulation-choice-guide (add) | FM stereo multiplex (pilot, 38 kHz DSB-SC); the LSB/USB convention; SSB audio bandwidth; why Morse/CW is efficient; AM+FM on one carrier vs QAM; bandwidth (not carrier) sets data rate; Wi-Fi vs Ethernet capacity; co-channel FM separation limits. |
| 34 | Multichannel coherence and array calibration | 4 (0) | 24 / 14.9 k | 9, 18, 111, 633 | 12/array-calibration (planned) | Measuring and correcting inter-channel delay/phase; steering-vector wavelength for wideband (LFM) signals; beamspace/subarray post-processing; building a coax phasing harness (λ/4 transformers, velocity factor). |
| 35 | RF switch and PA failure modes | 4 (0) | 30 / 9.7 k | 324, 406, 659, 674 | 06/rf-switches-attenuators-limiters, 06/power-amplifiers (add) | Why RF switches die (hot switching, ESD, overdrive, missing DC blocks); switch vs 0 Ω jumper option; how mismatch risk to a PA varies with frequency; reading cross-needle meters. |
| 36 | Balun practical details | 4 (0) | 23 / 7.2 k | 203, 204, 209, 405 | 06/baluns-and-rf-transformers (add) | Why balun footprints get bridged in single-ended builds; polarity/dot convention; where to place the balun; Gilbert-cell (SA612) LO feed-through vs external baluns. |
| 37 | Hobby radar modules and detectors | 3 (0) | 25 / 20.4 k | 431, 432, 433 | 11/diy-radar-hardware (planned) | RCWL-0516 (self-oscillating mixer) analysis; wideband radar-detector receivers; adding a horn or lens to a patch-antenna radar module (gain and legality). |
| 38 | Wireless power transfer and RF harvesting | 5 (4) | 128 / 122.5 k | 443, 450, 471, 534, 539 | **NEW** page (e.g. 09/wireless-power-and-energy-harvesting) | Inductive vs resonant vs radiative power transfer and their efficiency/range limits; rectenna efficiency vs input power; exposure limits (link 19/rf-exposure-safety); a simple inductive link circuit. |
| 39 | Handheld and vehicle antennas | 7 (0) | 105 / 180.5 k | 550, 565, 568, 589, 602, 616, 649 | 08/dipoles-and-monopoles (add) | HT whips vs longer aftermarket whips (claims vs physics); the radio and hand as counterpoise; mag-mount capacitive coupling to the roof; bull-bar and roof mounting; radial-less verticals and RF in the shack. |
| 40 | Feedlines and tuners (ladder line vs coax, twisted pair, ATU placement and function, transmitting without a tuner, SWR "ghosts") | 8 (0) | 92 / 45.5 k | 215, 584, 585, 599, 613, 660, 666, 673 | 03/coax-and-cables, 03/reflections-vswr-return-loss-mismatch (add) | Loss of ladder/window line vs coax at high SWR; why twisted pair is not used as RF feedline; what an antenna tuner does and does not fix (feedline loss), antenna-end vs shack tuner; safe practice without meters; echo delay vs symbol time for "ghosts". |

Below the cut (ranks 41–46): practical HF propagation (rows 562, 572, 577, 591, 621, 629); phase-noise
measurement leftovers — additive PN of amplifiers, bistatic FMCW, curve interpolation (101, 407, 414);
chirp factor-of-2 pitfall and non-RF ranging (22, 428, 429, 435); digital-line termination demos (344,
517, 521, 522); misc (291, 417, 615); satellite LNBs/radio astronomy (497, 557). Unclustered singletons,
all minor partials: 44, 150, 217, 219, 233, 340, 356, 382, 434, 464, 498, 538, 574 (noise blanker —
missing), 651.

## 3. Misconceptions seen in the wild, and whether the KB addresses them

✅ = explicitly corrected in a page's "Common mistakes" (or main text); ◐ = the physics is there but the
myth is not called out; ✗ = not addressed.

| Misconception (as it appears in questions) | Example | KB | Where / what to add |
|---|---|---|---|
| A higher-dBi antenna "adds power" / always gives more range | https://electronics.stackexchange.com/q/36031 | ✅ | 08/antenna-fundamentals ("5 dBi gain adds 5 dB") |
| Higher frequencies penetrate walls better | https://electronics.stackexchange.com/q/33537 (110 k views) | ✗ | 09/atmospheric-rain-attenuation: add frequency trend + myth (09/friis only covers the free-space version) |
| A longer ¼-wave whip is better | https://electronics.stackexchange.com/q/132051 | ◐ | 08/dipoles-and-monopoles explains cutting length; add "longer ≠ better" explicitly |
| Transmission-line effects only start at λ/2 | https://electronics.stackexchange.com/q/178112 | ✅ | 02/quasi-static-vs-full-wave (λ/10 rule derived; "only a 10 MHz clock") |
| Impedance matching wastes ≥ 50 % of the power | https://electronics.stackexchange.com/q/449645 | ✅ | 01/network-theorems-max-power-transfer |
| Zeroing FFT bins is a good (brick-wall) filter | https://dsp.stackexchange.com/q/6220 (122 votes) | ✗ | 14/fft-spectral-analysis-windows or 14/digital-filters-fir-iir Common mistakes |
| Zero-padding increases frequency resolution | https://dsp.stackexchange.com/q/741 (228 k views) | ✅ | 14/fft-spectral-analysis-windows #3 |
| Complex sampling "breaks" Nyquist | https://dsp.stackexchange.com/q/672 | ✅ | 14/sampling-aliasing-bandpass-sampling #2 |
| Receiving below the noise floor beats Shannon | https://dsp.stackexchange.com/q/15206, https://electronics.stackexchange.com/q/321186 | ✅ | 10/ber-ebn0-and-shannon, 07/sensitivity-and-mds |
| Feed-line length changes SWR / must be cut to a magic length | https://electronics.stackexchange.com/q/68394, https://ham.stackexchange.com/q/1628 | ✅ | 03/reflections-vswr-return-loss-mismatch |
| Reflected power always destroys the transmitter | https://electronics.stackexchange.com/q/335912 | ✅ | 03/reflections ("Reflected power burns the PA"), 06/power-amplifiers ruggedness |
| A lossy coax "limits" the SWR the transmitter sees (so it's fine) | https://ham.stackexchange.com/q/9722 | ✅ | 03/reflections ("a long lossy cable makes a bad antenna look good") |
| High SWR causes ghosts/ISI on HF receive | https://ham.stackexchange.com/q/15508 | ◐ | 03/reflections: add echo-delay vs symbol-time argument |
| An RC filter after the LNA lowers the noise | https://electronics.stackexchange.com/q/664603 | ✗ | 06/lna-design Common mistakes |
| Phase noise can be averaged out | https://electronics.stackexchange.com/q/384128 | ◐ | 17/phase-noise-measurement explains averaging vs cross-correlation in the text; not listed as a mistake |
| A 5/8-wave vertical always beats a ¼-wave | https://ham.stackexchange.com/q/1142 | ✅ | 08/dipoles-and-monopoles |
| A ¼-wave needs no ground because it is resonant | https://electronics.stackexchange.com/q/480508 | ✅ | 08/dipoles-and-monopoles |
| Element metal (Al vs Cu) changes the resonant length | https://ham.stackexchange.com/q/9451, https://ham.stackexchange.com/q/1388 | ✗ | 08/dipoles-and-monopoles (only insulation is covered) |
| A chirp's phase is 2π(f0 + kt)·t, so the sweep "doubles" | https://dsp.stackexchange.com/q/93704 | ✗ | 11/pulsed-radar or 11/fmcw-radar Common mistakes (phase is the integral of frequency) |
| The FMCW ADC must sample the whole chirp bandwidth | https://dsp.stackexchange.com/q/96462 | ✅ | 11/fmcw-radar (IF/ADC-limited range) |
| Always split analog and digital ground planes | https://electronics.stackexchange.com/q/306862 | ✗ | 13/grounding-and-return-paths / mixed-signal-layout (planned) |
| Fill every free area with ground copper | https://electronics.stackexchange.com/q/48567 | ◐ | 08/pcb-and-chip-antennas corrects it for antennas only; 13 needed |
| Via fences around a chip antenna reduce its noise | https://electronics.stackexchange.com/q/41871 | ✗ | 13/vias-stitching-fencing (planned) |
| Soldermask must always be removed over RF traces | https://electronics.stackexchange.com/q/381259 | ✅ | 13/stackups-and-materials, 03/planar-lines (quantified effect) |
| GPS receivers talk to the satellites | https://ham.stackexchange.com/q/21314 | ✗ | NEW GNSS receiver-operation page |
| A matching network just moves the reflection elsewhere | https://electronics.stackexchange.com/q/676831 | ◐ | 03/impedance-matching: add an energy-conservation explanation |
| A coil (inductor) should make a good antenna | https://electronics.stackexchange.com/q/58027 | ✅ | 08/loop-antennas, 08/pcb-and-chip-antennas (TI AN058 "air-core inductor" caveat) |
| Higher carrier frequency means higher data rate | https://electronics.stackexchange.com/q/504401 | ◐ | 10/ber-ebn0-and-shannon: say it explicitly |
| 2.4 GHz was chosen because it is water's resonance | https://electronics.stackexchange.com/q/125692 | ◐ | 02/dielectrics mentions the oven is not at the water peak; 19/spectrum-allocation should give the ISM history |
| A 377 Ω antenna is "more efficient" than a 50 Ω one | https://ham.stackexchange.com/q/1243, https://electronics.stackexchange.com/q/400665 | ✅ | 08/antenna-fundamentals (antenna as 50 ↔ 376.7 Ω transformer; efficiency = R_rad/(R_rad+R_loss)) |
| Different LoRa SFs don't interfere with each other | https://electronics.stackexchange.com/q/415645 | ✅ | 15/lora-impairments-doppler-drift-timing |
| Slowing edges with series resistors is only about signal integrity | https://electronics.stackexchange.com/q/195616 | ◐ | 00/fourier explains the spectrum; 13/emc should cover series-R/edge-rate control |

Overall: of 32 misconceptions, 15 are corrected explicitly, 8 half-way, 9 not at all. The KB's existing
"Common mistakes" sections are strong wherever a page exists (03, 08, 14, 15 especially). The
uncorrected myths sit in unwritten domains (13, GNSS operation) or are practical/DSP items that pages
touch but never state as myths.

## 4. Full table

Columns: # (row id used above) | question (exact SE title) | URL | site/tag it was harvested from |
votes/views at harvest (2026-09-27) | domain | status | KB page(#section) that answers it | note on what is
missing. Rows re-checked on 2026-09-29 are marked "(re-checked)".

