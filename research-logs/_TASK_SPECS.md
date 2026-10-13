# Task specs for every agent wave (so any session can (re)launch a task)

Each agent prompt = (1) the standard preamble below + (2) the task's scope/content list.

## Standard preamble (paste into every research-agent prompt)
> You are research agent **<ID>** building part of a large RF/analog engineering knowledge base
> at `/Users/marcusquek/Documents/RF Physics`. Step 0 (mandatory): read CONVENTIONS.md and
> INDEX.md; create your log `research-logs/<ID>-<short>.md` with a plan before researching;
> update it after every page and every ~3 sources (crash-recovery record). Load WebSearch/WebFetch
> via ToolSearch `select:WebSearch,WebFetch`; read pages/PDFs with WebFetch (no curl downloads).
> Python (numpy/scipy/sympy/matplotlib/scikit-rf) available — verify formulas, scripts in
> `tools/verify/<domain>_*.py`. Reader: Marcus, SUTD Singapore rocketry avionics (EBYTE LoRa
> E22-400T33D 433 MHz 2 W, E220-900T30D 900 MHz 1 W; u-blox ZED-F9P/MAX-M10S; KiCad + JLCPCB),
> wants to build radios/radars/LoRa/phased arrays/antennas/analog circuits and learn the math
> from any level. Pages substantial (250–700 lines), exact template, layered math, worked
> examples, common mistakes, how to simulate. Textbooks/peer-reviewed/standards/app notes first;
> light forum sweep for questions & misconceptions. Own words only. Only write inside owned
> folders; note cross-domain needs in log. If resuming, read the existing log and continue.
> Final reply ≤ 250 words.

## Wave 1 (launched 2026-09-27) — see HANDOFF.md; scopes = INDEX.md slugs for:
W1-A1 00 · W1-A2 01+04 · W1-A3 02 · W1-A4 03 · W1-A5 07+09 · W1-A6 08

## Wave 2
### W2-B1 — 05-analog-electronics
Diodes (Schottky, PIN, varactor, step-recovery; detectors, limiters, tuning); BJT physics &
small-signal (hybrid-π, gm, fT, fmax, Early, noise); FETs (MOSFET, JFET, GaAs pHEMT, GaN HEMT,
SiGe HBT — which to use at which frequency/power); amplifier topologies (CE/CS, CB/CG, CC/CD,
cascode, differential, Darlington, feedback amps, Miller effect); feedback & stability (loop gain,
phase/gain margin, compensation, Nyquist, oscillation causes and cures); op-amps real limits (GBW,
slew, noise voltage/current density, input bias, CMRR/PSRR, stability with capacitive loads,
current-feedback amps for video/IF); oscillators (Barkhausen, negative resistance, Colpitts/
Clapp/Hartley/Pierce/crystal/VCO, start-up, phase noise basics); data converters (sampling,
quantisation SNR = 6.02N+1.76, ENOB, SFDR, jitter-limited SNR, aliasing, ADC architectures SAR/
pipeline/ΣΔ, DAC images & sinc roll-off, anti-alias filters, ADC drivers); power supplies for RF
and analog (LDO PSRR vs frequency, switching regulator noise/spurs, ripple filtering, ferrite/LC
filters, ground bounce, low-noise references); active filters (Sallen-Key, MFB, state-variable,
component sensitivity); low-noise analog design (en/in, noise matching, source impedance, 1/f,
resistor noise); analog signal conditioning (instrumentation amps, bridges, ADC front-ends,
protection). Sources: Horowitz & Hill *Art of Electronics* 3e; Sedra & Smith; Gray & Meyer;
Razavi *Design of Analog CMOS ICs*; Jung *Op Amp Applications Handbook* (ADI, free); TI/ADI app
notes; Kester *Data Conversion Handbook*; Motchenbacher & Connelly *Low-Noise Electronic Design*.

### W2-B2 — 06-rf-circuits
LNA design (stability K/μ, noise/gain circles, input/output matching, inductive degeneration,
biasing, commercial MMICs); PAs (classes A/AB/B/C/D/E/F, efficiency, load-line & load-pull, Cripps
method, harmonic filtering, linearity vs efficiency, DPD, thermal); mixers (diode single/double/
triple-balanced, Gilbert cell, conversion gain/loss, LO drive, isolation, image rejection, IQ
mixers, spurs chart); RF filters (LC, helical, cavity/combline, ceramic coaxial, SAW/BAW,
microstrip: stepped-impedance, coupled-line, hairpin, interdigital; Richards/Kuroda; design
walkthrough); couplers/dividers/combiners (Wilkinson, branch-line, rat-race, Lange, directional
couplers, coupling/directivity); baluns & RF transformers (Marchand, lumped LC, transmission-line
transformers Guanella/Ruthroff, ferrite); RF switches/attenuators/limiters (PIN, FET/SOI switches,
Pi/T attenuators, step attenuators, limiters for LNA protection); VCO & PLL synthesizers (integer-N,
fractional-N, loop filter design, phase noise contributions, reference spurs, lock time, ADF4351/
LMX2594 class parts, DDS); receiver architectures (superhet, image frequency, dual conversion,
direct conversion/zero-IF with DC offset & IQ imbalance, low-IF, direct sampling); transmitter
architectures (direct upconversion, polar, harmonic/spur masks); detectors/power meters (diode
detectors, log amps, RMS detectors); multipliers/dividers; circulators/isolators; amplifier
stability & biasing (bias tees, sequencing for GaAs/GaN, oscillation). Sources: Pozar; Gonzalez
*Microwave Transistor Amplifiers*; Cripps *RF Power Amplifiers for Wireless Communications*;
Razavi *RF Microelectronics*; Lee; Maas *Microwave Mixers*; Matthaei/Young/Jones; Hong & Lancaster
*Microstrip Filters for RF/Microwave Applications*; Banerjee *PLL Performance, Simulation and
Design* (free, TI); Egan; Mini-Circuits/ADI/Qorvo/Skyworks app notes; EMRFD.

### W2-B3 — 10-comms-modulation  (and W2-B7 — 14-sdr-dsp: split out 2026-09-27 when the agent limit rose to 10)
10: analog modulation (AM/DSB/SSB/FM/PM, Carson's rule, FM capture/threshold, pre-emphasis);
digital modulation (OOK/ASK/FSK/GFSK/MSK/GMSK/BPSK/QPSK/OQPSK/8PSK/QAM/APSK, constellations,
spectral efficiency, PAPR); BER vs Eb/N0 derivations (coherent/non-coherent), Shannon capacity &
limit (−1.59 dB); pulse shaping & ISI (Nyquist, RRC, roll-off, eye diagrams); spread spectrum
(DSSS processing gain, FHSS, CSS, jamming margin); OFDM (subcarriers, CP, PAPR, sync); channel
coding (block/Hamming, RS, convolutional/Viterbi, turbo, LDPC, polar, interleaving, coding gain);
synchronisation (Costas loop, PLL carrier recovery, Gardner/Mueller-Müller timing, frame sync,
frequency offset estimation); matched filter & detection (derivation, SNR gain); framing &
protocols (preambles, sync words, CRC, ARQ, packet error rate vs BER).
14: sampling theorem, aliasing, bandpass sampling; IQ & complex baseband; FIR/IIR design (windows,
Parks-McClellan, bilinear), fixed-point; multirate (decimation, interpolation, CIC, half-band,
polyphase); FFT spectral analysis (windows, ENBW, scalloping, processing gain, Welch); NCO/DDC/
DUC; SDR hardware survey (RTL-SDR, Airspy, SDRplay, HackRF, PlutoSDR, LimeSDR, bladeRF, USRP,
KrakenSDR — specs: ADC bits, BW, NF, IIP3, price); GNU Radio/SoapySDR/liquid-dsp/PySDR; software
demodulation (FM, AM, FSK, PSK, LoRa via gr-lora_sdr); FPGA for SDR. Sources: Proakis & Salehi;
Sklar; Haykin; Rappaport; Lyons *Understanding DSP*; Oppenheim & Schafer; Harris *Multirate
Signal Processing*; PySDR (pysdr.org); GNU Radio wiki; Ettus/ADI docs.

### W2-B4 — 11-radar
Radar range equation (derivation, monostatic/bistatic, with losses, integration gain coherent/
non-coherent, search vs track forms); RCS (sphere/plate/corner reflector formulas, Swerling
models, RCS of drones/people/rockets, dBsm); pulsed radar (range resolution, PRF, range/Doppler
ambiguities, duty cycle, pulse compression LFM/Barker/phase codes, matched filter, sidelobes/
windowing); CW & Doppler radar (Doppler equation, micro-Doppler, HB100/CDM324 modules); FMCW
(beat frequency derivation, range/velocity resolution, chirp parameters, range-Doppler FFT, IF
bandwidth, phase noise & leakage, TI AWR/IWR 77 GHz, Infineon BGT60, ADI Phaser); detection
theory (Neyman-Pearson, Pd/Pfa, Albersheim/Shnidman, CFAR CA/OS); ambiguity function &
waveform design; clutter & MTI/pulse-Doppler; SAR & imaging (range-Doppler algorithm, backprojection,
DIY SAR); MIMO radar & virtual arrays (TDM/DDM, angle estimation); DIY radar hardware (MIT
coffee-can radar, 24 GHz modules, TI mmWave kits, HackRF/Pluto passive radar, KrakenSDR passive
radar; tracking a rocket with radar). Sources: Skolnik *Introduction to Radar Systems* & *Radar
Handbook*; Richards *Fundamentals of Radar Signal Processing*; Richards/Scheer/Holm *Principles of
Modern Radar*; Mahafza *Radar Systems Analysis and Design Using MATLAB*; Levanon & Mozeson; MIT OCW
6.S02 / MIT LL "Introduction to Radar Systems" lectures; TI mmWave app notes (SWRA553 etc.).

### W2-B5 — 12-phased-arrays
Array factor derivation (ULA), broadside/endfire, beamwidth, directivity of arrays; steering &
grating lobes (d ≤ λ/(1+|sin θ0|)), scan loss (cos^n), beam squint with phase shifters vs TTD;
planar arrays, element pattern, active element pattern/active reflection coefficient, mutual
coupling, scan blindness; tapering (Taylor, Dolph-Chebyshev, binomial, taper efficiency); beam-
forming architectures (analog RF/IF/LO phase shifting, digital, hybrid, subarrays); components
(ADAR1000, HMC phase shifters/VGAs, Anokiwave beamformers, TTD); calibration (mutual-coupling
method, near-field probes, rotating element electric field vector REV, far-field); adaptive
beamforming & DOA (delay-and-sum, MVDR/Capon, LCMV, MUSIC, ESPRIT, Root-MUSIC, CRB); DIY projects
(ADI Phaser CN0566, KrakenSDR 5-channel DOA, coherent RTL-SDR arrays, Pluto-based arrays, 5.8 GHz
patch arrays, MIT phased array radar). Sources: Mailloux *Phased Array Antenna Handbook*; Hansen
*Phased Array Antennas*; Van Trees *Optimum Array Processing*; Balanis ch.6; Haupt *Antenna Arrays*;
Visser *Array and Phased Array Antenna Basics*; ADI "Phased Array Antenna Patterns" series (Delos,
Broughton, Kraft); Krim & Viberg 1996 review.

### W2-B6 — 15-lora-ism-radios
LoRa PHY maths (CSS chirps, SF/BW/CR, symbol time 2^SF/BW, time-on-air formula (Semtech AN1200.13),
low-data-rate optimisation, processing gain, demodulation SNR limits per SF, sensitivity), orthogonality
of SFs, capture effect, frequency-offset/Doppler tolerance (critical for rockets), drift and TCXO;
Semtech chips (SX1276/78, SX1262/68, LLCC68, LR1110/1120/1121, LR2021, SX1280 2.4 GHz with ranging);
modules (EBYTE E22/E220/E32 series incl. their UART config modes, RFM95/96, Heltec, RAK) — what the
EBYTE "air data rate" settings map to (SF/BW/CR); LoRaWAN vs raw LoRa; other ISM radios (CC1101/CC1310/
CC1352, Si4463, nRF24/nRF52, ESP-NOW, 2.4 GHz FLRC/GFSK, telemetry radios SiK/RFD900); rocket telemetry
radio design (Doppler, dynamic range near pad, antenna orientation, packet design, FEC, ground-
station diversity, what amateur rocketry teams have flown/achieved — altitude records with LoRa, e.g.
university teams, Spaceport America Cup, ASTRA/SEDS; high-altitude balloon LoRa records); ground-station
design (Yagi + LNA + SAW, tracking, antenna rotators, diversity, SDR monitoring); ISM band plans &
duty cycle (AS923 for Singapore, EU868, US915, IN865; 433 MHz rules; power limits — link 19).
Sources: Semtech datasheets & AN1200.xx; Vangelista 2017 "Frequency Shift Chirp Modulation: The LoRa
Modulation"; Bor & Roedig; Knight & Seeber (gr-lora reverse engineering); Tapparel et al. (EPFL
gr-lora_sdr); Ghanaatian 2019 LoRa BER; LoRa Alliance regional parameters; EBYTE manuals; Meshtastic docs.

## Wave 3
### W3-C1 — 13-pcb-rf-layout-emc
Stackups & materials (FR-4 variants, Rogers RO4003C/4350B, Isola, Megtron; JLCPCB stackups JLC04161H-7628
etc., their εr and impedance calculator; hybrid stackups; cost), grounding & return paths (why
split planes hurt, return current distribution under microstrip, ground stitching), vias (inductance,
stitching pitch λ/10–λ/20, via fences for CPWG, backdrilling/stubs), RF layout rules (placement,
shortest RF paths, matching network placement, keep-outs, component orientation, 0402 vs 0201,
pad-to-trace transitions, tapering), connectors & launches (SMA edge-launch optimisation, U.FL,
coax-to-microstrip transitions), shielding cans & isolation (cavity resonances of cans, absorbers),
EMC/EMI (DM vs CM radiation, cable radiation, filtering, spread spectrum clocks, pre-compliance
testing with near-field probes & SA), PDN & decoupling for RF (target impedance, bead+cap resonance,
supply isolation for PAs/VCOs), mixed-signal layout (ADC grounding, digital noise into RF, clock
routing), JLCPCB RF manufacturing (impedance control options, tolerances, via-in-pad, ENIG vs HASL
loss, controlled-dielectric, minimum features), thermal management for PAs. Sources: Ott; Bogatin
*Signal and Power Integrity—Simplified*; Johnson & Graham; Archambeault; Montrose; TI/ADI/Qorvo/
Semtech layout app notes (e.g. Semtech SX126x reference design layout guide, TI SWRA367?); Rick
Hartley talks; Eric Bogatin articles; JLCPCB docs.

### W3-C2 — 16-simulation-tools + tools/
Tool landscape (what to use for circuit/RF/EM/system/antenna/radar simulation; free vs commercial);
SPICE (ngspice, LTspice, Qucs-S, Xyce; AC/noise/transient; S-param analysis; RF models; harmonic
balance in Qucs/QucsStudio/ADS/Xyce); RF circuit sims (QucsStudio, ADS, AWR MWO, Sonnet Lite, RFSim99,
SimSmith); EM solvers (openEMS FDTD, MEEP, Elmer FEM, Palace, OpenParEM, gprMax, Sonnet, HFSS, CST,
FEKO, EMerge?); NEC modelling (4nec2, xnec2c, MMANA-GAL, PyNEC/necpp); openEMS workflow (install on
Apple Silicon, patch antenna and microstrip examples, CSXCAD, Python interface, meshing rules);
Python RF toolkit (scikit-rf, numpy, pyrf? radarsimpy, pyargus, commpy, gnuradio, pyAAF);
impedance/RF calculators (Saturn PCB Toolkit, KiCad calculator, AppCAD, JLC calculator, Qucs
transcalc); simulation validation (convergence, mesh studies, comparing to analytic/measurement,
port de-embedding, the team's V&V ethos); installing tools on macOS (Homebrew ngspice, openEMS build,
Qucs-S, xnec2c, Docker/Wine options for Windows tools). ALSO build `tools/rfcalc/` — a small tested
Python package of calculators used across the KB (dB/power conversion, FSPL/Friis/link budget,
Fresnel/horizon, noise cascade, IP3 cascade, L-network/pi matching, microstrip/CPWG Z0, coax Z0,
skin depth, resonance/Q, radar range equation, FMCW parameters, array factor, LoRa time-on-air &
sensitivity) with unit tests validated against KB worked examples. Actually install ngspice/openEMS
if feasible via Homebrew/pip (document exactly what was done).

### W3-C3 — 17-test-measurement
VNA fundamentals & calibration (error models 8/12-term, SOLT/SOL/TRL/Unknown-thru, cal kit
definitions, uncertainty, port extension), NanoVNA/LibreVNA practical guide (models, firmware,
accuracy vs frequency, NanoVNA-Saver, pitfalls), spectrum analysers (RBW/VBW, DANL, detectors,
phase noise, preamps, tinySA, RSA/Siglent/Rigol budget options), oscilloscopes & RF probing
(bandwidth, sampling, probes, near-field probes), RF power measurement (thermal/diode sensors,
directional couplers, attenuators), noise-figure measurement (Y-factor, cold-source, noise sources,
SDR-based), phase-noise measurement, antenna range/OTA testing (DIY), SDR as test equipment,
signal generators and sources (ADF4351 boards, SG, tinySA as gen), lab setup by budget tier
(S$500/S$3k/S$15k), fixtures & de-embedding (TRL fixtures, AFR). Sources: Keysight/R&S/Anritsu app
notes & primers (Keysight AN 1287-3 VNA cal, AN 150 spectrum analysis basics, AN 57-2), Dunsmore
*Handbook of Microwave Component Measurements*, NanoVNA docs/groups.io, LibreVNA docs.

### W3-C4 — 18-components-parts
Survey + selection guidance with real part numbers, key specs, price bands, availability at LCSC/JLC,
Mouser, Digikey: RF transceivers (Semtech, TI CC1xxx, ADI AD936x/ADRV, Lime LMS7002M, Nordic, SiLabs,
ST S2-LP/STM32WL), LNAs/PAs/gain blocks (Mini-Circuits PSA/PMA/GALI/ERA, Qorvo QPL/TQP, ADI HMC,
Guerrilla RF, Skyworks SKY65/66, NXP BGU, Infineon BGA), mixers/PLLs/VCOs (ADF4351/4371, LMX2594/2572,
HMC830, Si5351 for low freq), RF switches/attenuators (PE42xx, HMC, SKY13), filters (Murata SAW/ceramic,
Mini-Circuits LTCC, Johanson), connectors & cables (SMA/SMB/MMCX/U.FL/W.FL/N/BNC/2.92 mm; frequency limits;
cable assemblies), PCB substrates (Rogers etc., availability and cost at JLCPCB/PCBWay), ADCs/DACs for
SDR (AD9361 inside, LTC2208, AD9208, RFSoC), sourcing & eval boards (Mini-Circuits/ADI EVBs, cheap
modules on AliExpress and their pitfalls), RF modules (LoRa, GNSS, Wi-Fi/BLE modules, SiK radios).

### W3-C5 — 19-regulations-safety + GLOSSARY.md
Spectrum allocation & ISM bands worldwide (ITU regions, 433.05–434.79, 863–870, 902–928, 2.4, 5.8,
24, 60, 77 GHz), Singapore IMDA rules (Short Range Devices spec, power limits for 433/866–869/920–925
MHz, radar bands, LoRa AS923), amateur radio licensing (Singapore IMDA amateur licence classes and exam,
US FCC Technician/General; what ham licence allows for rocketry telemetry & higher power), RF exposure
(ICNIRP 2020, FCC MPE, calculation of safe distance), certification (FCC Part 15/ID, CE RED, IMDA
equipment registration; when modules' certification carries over), lab safety (ESD, high-power RF,
batteries, PA burns). GLOSSARY.md at root: every acronym used across the KB (harvest by grepping kb/).

### W3-C6 — 20-projects-recipes
End-to-end worked design walkthroughs that stitch the KB together with numbers, parts, layout, tests:
LoRa rocket telemetry link (requirements → link budget → module/antenna choice → packet design →
ground station → range test plan), ground-station tracking Yagi (+LNA, rotator/manual tracking),
patch antenna design walkthrough (calc → openEMS → fab at JLC → NanoVNA tune), FMCW radar build,
phased-array starter build, LNA design walkthrough (GNSS or 433 MHz), SDR receiver build, band-pass
filter design walkthrough, GNSS front-end design, design-review checklists (RF schematic review, RF
layout review, bring-up checklist).

## Wave 4 — gap analysis (write only to gaps/)
Each agent: collect as many real questions as possible from its sources (aim ≥ 300 per agent),
dedupe, classify by domain, then check each against the KB (grep/read) → status covered / partial /
missing, with the page that answers it. Output `gaps/<ID>-<source>.md` with a table
| question | source URL | domain | status | KB page | note |, plus a ranked list of the top
missing topics. Also record misconceptions seen in the wild and whether the KB addresses them.
- W4-D1: Stack Exchange (electronics.stackexchange tags rf, antenna, impedance-matching, transmission-line,
  radio, lora, sdr, pcb-design+rf; ham.stackexchange; dsp.stackexchange radar/sdr tags) — top-voted
  & most-viewed.
- W4-D2: Reddit (r/rfelectronics, r/amateurradio, r/antennas, r/RTLSDR, r/sdr, r/AskElectronics,
  r/ElectricalEngineering, r/meshtastic, r/rocketry, r/radar).
- W4-D3: EEVblog RF & microwave forum, QRZ/eHam forums, Hackaday comments, groups.io (nanovna-users,
  LibreVNA), YouTube (W2AEW, Rohde & Schwarz, Keysight, Andreas Spiess LoRa, Tech Minds, Robert
  Feranec, Phil's Lab, The Signal Path, HB9BLA) video comment sections and transcripts.
- W4-D4: Curriculum coverage — tables of contents of the canonical textbooks (Pozar, Balanis, Razavi,
  Lee, Skolnik, Richards, Mailloux, Horowitz & Hill, Proakis, Rappaport, Ott, Bogatin) and university
  syllabi (MIT 6.013/6.776/6.S02, Stanford EE133/EE252/EE314, Berkeley EE142/EE242, Georgia Tech,
  TU Delft) → which sections have no KB counterpart.
- W4-D5: RF engineer interview questions, textbook end-of-chapter problem types, ham licence exam
  question pools (US Tech/General/Extra pools are public; Singapore RAE syllabus) → coverage check.
- W4-D6: Internal consistency audit of all kb pages: numeric constants and typical values stated in
  more than one place (kT, skin depth, εr of FR-4, FSPL constants, dipole impedance, LoRa sensitivity
  numbers, Kraus helix gain, polarization handedness, sign conventions e^{jωt}), notation, contradictory
  claims, broken links (run tools/build_index.py --check). Output gaps/D6-consistency-audit.md with
  each issue, files+lines, and proposed resolution.
Orchestrator then merges into gaps/GAP_REGISTER.md (ranked), and plans Wave 5.

## Wave 5 — gap filling
Slices of GAP_REGISTER.md by domain group; each agent fixes consistency issues in its slice and writes
missing pages/sections, marking register rows resolved with the page link.

## Wave 6 — final audit
Second consistency audit (fresh eyes), link check, rebuild INDEX/FAQ, GLOSSARY refresh, HANDOFF update.

## Wave 5 slice agents (from gaps/GAP_REGISTER.md §6) — generic prompt (used from 2026-10-03)
> You are gap-filling agent **W5-Sn** … implementing slice **Sn "<theme>"** of `gaps/GAP_REGISTER.md`.
> Step 0: read CONVENTIONS.md, INDEX.md, GAP_REGISTER §3 rows for your items + §6 Sn row (file list, cautions,
> start conditions) + the orchestrator notes at the end of the register; kb/00-math-foundations/canonical-values-
> and-conventions.md (use its values). Create research-logs/W5-Sn-<short>.md (plan, progress, resume
> instructions); on PAUSE message: finish current edit, Status paused, stop. WebSearch/WebFetch via ToolSearch;
> Python + tools/rfcalc + PyNEC + openEMS (~/opt/openEMS) available; scripts tools/verify/sn_*.py.
> Edit ONLY the files named in the Sn row (surgical Edit, re-read first, bump last_updated); no _index.md edits
> unless the row says so; new pages allowed where the row says "new". Close each row in GAP_REGISTER §5 with
> page#section and remove it from §3. Layered maths, scripts verify numbers, Common mistakes, sources, own words.
> Final reply ≤250 words: items closed, sections added, verification, open leftovers.
