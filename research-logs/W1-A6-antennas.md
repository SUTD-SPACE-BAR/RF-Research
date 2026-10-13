# Research log W1-A6: 08-antennas
Status: complete
Owner scope: kb/08-antennas/ ; research-logs/W1-A6-antennas.md ; tools/verify/ant_*.py

## Plan
Order chosen so foundations exist before dependent pages; verification scripts written alongside.
- [x] antenna-fundamentals — DONE (kb/08-antennas/antenna-fundamentals.md) — pattern, D, G, realized gain, efficiencies, Ae=λ²G/4π (derived), beamwidth–D approximations (Kraus, Tai–Pereira), Rr, Zin, bandwidth defs, reciprocity, EIRP/ERP, dBi/dBd, "antennas don't amplify"
- [x] dipoles-and-monopoles — DONE — current distribution, λ/2 pattern, 73+j42.5 Ω (derive via Si/Ci), shortening vs wire diameter, folded dipole, monopole 36.5 Ω, finite ground, drooping radials, whips on small boards, common-mode, sleeve dipole, EFHW 49:1, J-pole, loaded short monopoles, top loading
- [x] loop-antennas — DONE — small-loop Rr ∝ (A/λ²)², efficiency, mag loops, large loops, ferrite rods, receive-only loops
- [x] patch-antennas — DONE — TL & cavity models, W/L/εeff/ΔL (Hammerstad), feeds, BW vs h/εr, efficiency, surface waves, CP, stacked; worked designs 1575.42 / 2450 / 5800 / 915 MHz on FR-4 & Rogers (Python); openEMS notes
- [x] helical-antennas — DONE — normal vs axial mode, Kraus design, Kraus gain overestimate (King & Wong 1980; Emerson 1995), QFH
- [x] yagi-uda-and-log-periodic — DONE — parasitic mechanism, DL6WU method, gain vs boom, 433/915 MHz designs, LPDA (Carrel τ, σ)
- [x] horn-reflector-aperture-antennas — DONE — aperture efficiency, pyramidal horn optimum, dish gain, taper vs spillover, feeds
- [x] pcb-and-chip-antennas — DONE — IFA/PIFA/meander, chip antennas & ground-plane dependence, pi matching, TI DN007/DN024/AN043/AN058, ESP32 module rules
- [x] gnss-antennas — DONE — RHCP, patch vs helix, active antennas, ground plane, AR, PCV, multipath, bands, u-blox guidance, rocket-body failures
- [x] antenna-matching-and-baluns — DONE — CM currents, choke/sleeve/current baluns, ferrite 31/43, Guanella/Ruthroff, measuring CM current, "SWR changes when I touch the cable"
- [x] antenna-measurement — DONE — S11 limits, far-field distance, pattern measurement, ranges, gain comparison/3-antenna, Wheeler cap, SDR DIY
- [x] antennas-on-rockets — DONE — wraparound, blade/stub, nose-cone monopoles, CF/Al blocking, detuning, axial nulls, spin modulation, CP choice, plume attenuation, recovery orientation
- [x] small-antenna-limits — DONE — Chu, McLean, Wheeler radian sphere, efficiency–BW, fractal/tiny claims
- [x] antenna-polarization-and-circular-polarization — DONE — AR, IEEE handedness, CP generation, PLF, reflection handedness flip
- [x] antenna-simulation-nec-openems — DONE — NEC-2 method, segmentation rules, tools, openEMS for patches, limits, verification
- [x] _index.md, _sources.md — DONE

Verification scripts planned (tools/verify/):
- ant_dipole.py — integrate λ/2 dipole & short-dipole patterns → D; Rr/Xin via Si/Ci (73.1 + j42.5 Ω); monopole halves; general-length dipole Rr
- ant_fundamentals.py — Ae from G, Kraus/Tai-Pereira beamwidth approximations vs exact, EIRP example
- ant_patch.py — patch W/L/εeff/ΔL for the 4 frequency/substrate cases; Q/BW estimates
- ant_loop.py — small-loop Rr, loss resistance, efficiency; ferrite rod
- ant_helix.py — Kraus axial-mode gain vs King–Wong/Emerson; QFH dimensions
- ant_yagi.py — DL6WU element lengths 433/915; LPDA Carrel design
- ant_aperture.py — horn optimum, dish gain, taper efficiency
- ant_small_limits.py — Chu/McLean Q vs ka, BW bounds for chip antennas at 433/915
- ant_polarization.py — AR ↔ PLF, CP-vs-linear mismatch

## Log (append-only)
- 2026-09-27 — Searched helix gain (King&Wong, Emerson); read NRAO Emerson pages and King&Wong PDF (pdftotext). KW peak gain formula confirmed from 2 sources: Gp=8.3(πD/λp)^(√(N+2)−1)(NS/λp)^0.8[tan12.5°/tanα]^(√N/2). Read Jackson UH microstrip notes (CAD formulas). Read TI DN007, DN023, DN024, AN058 via pdftotext.
- 2026-09-27 — Read u-blox GNSS antenna AN (pdftotext), Kinefuchi 2015 abstract, Lacava-group rocket antenna abstracts, Altus Metrum manual, DL6WU.BAS (curl'd text — protocol says WebFetch; noted), Cebik DL6WU, hamwaves LPDA, NEC-2 guidelines, IEEE Std 145-1993 (pdftotext).
- 2026-09-27 — Wrote & ran verification scripts (all in tools/verify/):
  * ant_dipole.py: D(short)=1.500, D(λ/2)=1.641 (2.15 dBi), D(λ)=2.411, D(1.25λ)=3.28 (5.16 dBi); Rr numeric = Si/Ci closed form to 3 decimals; Z(λ/2)=73.08+j42.52 Ω; monopole 36.54+j21.26 Ω, 5.16 dBi; HPBW 78.1°/90°/47.8°.
  * ant_mom_wire.py (own thin-wire MPIE Galerkin MoM, parallel wires): λ/2 dipole a=1e-4λ → 80.1+j44.6 Ω at exactly 0.5λ; resonant length K=0.976 (λ/d=5e4), 0.968 (5e3), 0.958 (1e3), 0.951 (500), 0.943 (250), 0.930 (100) with R_res≈72 Ω; 433 MHz 2 mm wire resonant dipole 327.9 mm; 915 MHz 1.5 mm 154.2 mm. Energy check Prad/Pin=1.000 after fixing a phi-integration bug (trapezoid on a periodic grid dropped half the peak column → 0.2 dB optimistic D; fixed with periodic rectangle rule).
  * ant_yagi.py: DL6WU algorithm (from DL6WU.BAS) + MoM: 433 MHz 11 el 1.72 m boom: DL6WU est 14.44 dBi vs MoM 14.20 dBi, F/B 16.3 dB, Zin(plain DE resonated 335 mm)=52 Ω; 15 el 2.78 m: 16.06 vs 15.87 dBi; 915 MHz 11 el 0.82 m: 14.44 vs 14.26 dBi; 16 el 1.45 m: 16.38 vs 16.25 dBi. DL6WU gain formula ≈0.2 dB optimistic (Cebik NEC also ≈0.2 dB below formula). 3-el 433 MHz optimised: 9.15 dBi, F/B 15 dB, Zin 11 Ω (needs match). Mutual Z12 MoM vs induced-EMF differ 1–7 Ω (definition: induced-EMF assumes sinusoidal currents referred to maxima; MoM two-port with open/shorted gaps).
  * ant_patch.py: TL-model + Jackson CAD. 2.45 GHz FR-4 1.6 mm: W 37.23, L 28.81 mm, BW 2.6%, e_rad 40%, G≈2 dBi; RO4003C: 40.56×32.06 mm, e 76%, G 5.2 dBi; L1 FR-4 57.9×45.1 mm e 30%; ceramic εr20 4 mm: 29.4×20.3 mm BW 0.75%; 5.8 GHz RO4350B 0.762: 16.93×13.29 mm; 915 FR-4: 98.8×77.1 mm, e 20%, G −1 dBi; 915 air 6 mm 162×152 mm G 9 dBi. Jackson check: εr 2.2, h/λ 0.02 → BW 2.8% (notes: ~3%). CP two-mode model: AR=0 dB needs split f0/Q; 3-dB-AR BW ≈ half the VSWR-2 BW.
  * ant_small_limits.py: numeric stored-energy Q of TM01 = McLean 1/(ka)^3+1/(ka) exactly (all ka); Chu circuit energy gives same; Hansen form (1+3k²a²)/(k³a³(1+k²a²)) higher by up to 12% at ka 0.5. Bounds: 433 MHz a=20 mm → Q≥172 → ≤1.79 MHz VSWR-2 BW at 100% eff; 915 MHz a=15 mm → ≤14.2 MHz (<26 MHz band). Loops: 433 MHz 30 mm/1 mm wire loop eff 29%; 14.2 MHz 1 m mag loop 68% (conductor loss only), 7.1 MHz 16%.
  * ant_aperture.py: Ae table; Kraus 41253/θ² over-estimates narrow cos^n beams ~0.4–0.5 dB, Tai–Pereira within 0.1 dB for n≥10; uniform aperture D→4πA/λ²; dish cos^q feed max aperture eff ≈0.82–0.85 with edge illumination −10 to −12 dB; optimum pyramidal horn e_ap=0.512 (15 dBi @5.8 GHz WR-159 → 132.8×98.9 mm).
  * ant_helix.py: Kraus − King&Wong ≈ 3.0–3.5 dB; Kraus − Emerson 3.7 (2.5λ) to 5.5 dB (6.25λ). 435 MHz 10-turn (1.72 m) → ~13 dBic realistic, not 16.6.
  * ant_polarization.py: (x−jy)/√2 is RHCP for e^{+jωt}, +z (numerically verified); PLF closed form = Jones overlap (1e-15); 3-dB-AR antenna vs linear wave −1.76…−4.76 dB; PEC reflection flips handedness; spinning linear TX: linear RX 2 nulls/rev, CP RX constant −3 dB with phase slope = roll rate.
  * ant_rocket.py: axial dipole loss vs look angle (e.g., 10 km alt, 2 km range → 11.3° → −16 dB); link margins still 26–64 dB free-space LOS for 433 MHz 2 W / 915 MHz 1 W vs SF9; LOS enters 22° plume cone above h = d/tan22°.
- 2026-09-27 — Wrote tools/verify/ant_mom_general.py (general polyline thin-wire MoM with junctions; PEC ground by mirroring). Results: dipole reproduces parallel solver exactly (80.07+j44.60 Ω); λ/4 monopole (a=1e-3λ) image 42.8+j22.8 Ω, 5.19 dBi; ground-plane antenna 4×λ/4 radials: horizontal 22.8 Ω, droop 30° 43.3 Ω, 45° 55.0 Ω, 60° 66.4 Ω (so ~50 Ω near 35–40°), peak D 1.5–2.0 dBi at horizon; folded dipole equal conductors 288 Ω (4×72), unequal a_fed=1e-3/a_other=3e-3 λ → 480 Ω vs derived formula (1+ln(s/a1)/ln(s/a2))²·72 = 479 Ω, reversed 198 vs 192 Ω; small loop: MoM Rr matches 20π²(C/λ)^4 within ~5% for C≤0.07λ, but is +24% at C=0.136λ and ~2× at 0.23λ; axial-mode helix over PEC (pitch 12.8°): N=10, C=1.1λ, L=2.5λ → 12.56 dBic (King&Wong 13.2, Emerson 12.85, Kraus 16.6) — independent confirmation that Kraus is ~4 dB optimistic; right-hand winding → RHCP (LHCP −16 dBic on axis).
- 2026-09-27 — (resumed after API limit) patch-antennas page written; added Jackson CAD directivity D≈3/(pc1)·εr tanc²/(εr+tan²) to ant_patch.py: two-slot vs CAD differ 0.2–0.4 dB (PCB) and ~0.8–1 dB (air, ceramic).
- 2026-09-27 — helical page: MoM helix convergence N=10,C=1.1λ: 12.37/12.56/12.68 dBic at 12/16/24 seg/turn; C sweep 0.9/1.0/1.2/1.3λ → 11.1/11.7/13.4/11.1 dBic; Zin ≈ 100−j65 Ω (short vertical feed wire).
- 2026-09-27 — loop page: MoM circular full-wave loop (a=5e-4λ, 433 MHz): C=0.9λ 97−j276; 1.0λ 120−j97; 1.05λ 138−j9 Ω (resonant), D=3.6 dBi on axis; 1.1λ 164+j85 Ω.
- 2026-09-27 — gnss page: noise cascade example (T_A 100 K): passive+3 dB coax+NF3 → 965 K (43.3 dB-Hz at −125.5 dBm); passive+0.3 dB+NF1.5 → 249 K (49.1); active 28 dB/NF2 +5 dB coax → 272 K (48.8).
- 2026-09-27 — ant_measurement.py: uniform-aperture on-axis gain error at 0.5/1/2/4×(2D²/λ) = −0.53/−0.13/−0.03/−0.008 dB; three-antenna σ_G = 0.174 dB for 0.2 dB σ_meas; ripple for −10/−20/−30 dB reflection: +2.4/−3.3, ±0.9, ±0.3 dB; specular point 17° below boresight for 1.5 m masts at 10 m.
- 2026-09-27 — LESSON: WebFetch's summariser HALLUCINATED DN023 content (claimed 100×100 mm ground, 85–90% efficiency) — actual PDF says 31×45 mm ground, −0.12 dBi max gain. Always pdftotext the saved PDF and read the text directly.
- 2026-09-27 — Read CONVENTIONS.md, INDEX.md, HANDOFF.md, avionics knowledge base (EBYTE E22-400T33D 433 MHz 2 W, E220-900T30D 900 MHz 1 W, ZED-F9P active antenna (flown L1-only), MAX-M10S U.FL). Created this log.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| S1 | Emerson, "The Gain of the Axial-Mode Helix Antenna", ARRL Antenna Compendium Vol 4 (1995) pp 64-68; https://www.cv.nrao.edu/~demerson/cs/helix.htm | peer-level (ARRL, NEC study of ~10,000 helices) | helical: Kraus optimistic by up to 4-5 dB; Gmax(dB)=10.25+1.22L-0.0726L^2 (L in λ, 2-7λ); Ropt=0.2025-0.0079L+0.000515L^2 λ; λ/2 square ground ≈ infinite; radial ground −3.5 dB | high |
| S2 | King & Wong, "Characteristics of 1 to 8 wavelength uniform helical antennas", IEEE TAP AP-28(2):291-296, Mar 1980 (pdf via astro.abhinav.ac.in) | peer-reviewed (measured) | measured gain factor 4.2-7.7 vs Kraus 15; HPBW factor 61-70 vs 52; peak gain at C/λ≈1.135 (fixed length), 1.155 (N=5) → 1.07 (N=35); gain-BW product 24000-31500 vs 41250; AR<1.5 dB for 0.8<C/λ<1.2; doubling N gives <3 dB; phase centre ~L/4 from feed; Z≈140 Ω helix | high |
| S3 | Jackson, "Introduction to Microstrip Antennas", U. Houston ECE5318/6345 notes (courses.egr.uh.edu) | lecture notes (author of JA-1991 CAD formulas) | patch CAD formulas: BW, Qsp, Qc, Qd, Qsw, e_r^hed, p, c1, Redge, Rin=Redge cos²(πx0/L); W=1.5L typical, W<2L; BW ≈3% at h/λ0=0.02, εr=2.2; foam ~10%; probe issue h>0.05λ0; E-plane edge diffraction | high |
| S4 | TI DN007 / SWRU120D "2.4-GHz Inverted F Antenna" (2007, rev 2019) | app note | IFA 25.7×7.5 mm, 1 mm FR-4, gain 1.1/3.3/1.6 dBi by plane, RL<-15 dB, >300 MHz BW(<10% refl), pi-network recommended | high (measured) |
| S5 | TI DN023 / SWRA228 "868/915/955 MHz Inverted F Antenna" (Kervel) | app note | 43×20 mm IFA on 0.8 mm FR-4, ground 31×45 mm, max gain −0.12 dBi, ~50 MHz BW(<10% refl), 955 MHz only ~25 MHz; keep ground ≥5 mm from antenna sides, side ground ≥15 mm; tune via L6 | high (measured) |
| S6 | TI DN024 / SWRA227 "Monopole PCB Antenna with Single or Dual Band Option" (Wallace) | app note | meander monopole 38×25 mm, 1.6 mm FR-4, GND 43×63 mm; CTIA OTA: TRP eff 97.7% (868), peak gain 5.05 dBi; SWR 1.8 unmatched; pi match 1.8 nH/2.7 pF; BW 73 MHz @SWR2 | high (measured; efficiency uncertainty unstated) |
| S7 | TI AN058 / SWRA161 "Antenna Selection Guide" (Wallace) | app note | chip antenna datasheet numbers are for their test board; same-area board: 868 MHz 91% vs 169 MHz 7% efficiency; wire/cable antennas; spectrum-analyser sweep BW method; VNA semi-rigid method, port extension; NOTE contains sloppy physics ("antenna is basically an air-core inductor", "λ/2 dipole produces most power at the ends") — do not cite for physics | medium (practice good, theory sloppy) |

| S8 | u-blox, "GNSS antennas — RF design considerations for u-blox GNSS receivers", app note UBX-15030289 R03 (2019) | app note | GNSS: active LNA 15 dB enough ≤5 m cable, ≤26 dB needed, >35 dB overload; active antenna if cable >10 cm; LNA 3–20 mA; 25×25 mm patch optimal, <17×17 moderate; ground 50×50–70×70 mm; AR example min at 50 mm, ~10 dB at 100 mm ground; centre freq shifts with ground size; chip/linear ≈3 dB polarization loss; chip PCB 80×40 avg C/N0 43.4 vs 24×15 34.7 dBHz; helix ground +2–3 dB; "fibreglass airfoil attenuates GNSS"; jammer dynamic range 6–12 dB; shielding 30–40 dB | high (manufacturer) |
| S9 | Kinefuchi, Okita, Funaki, Abe, "Prediction of in-flight RF attenuation by a rocket plume", J. Spacecraft & Rockets 52(2), 2015 | peer-reviewed | M-V 2nd stage, P-band; strong attenuation at look angles <22° from aft axis; CFD+FD²TD Drude model matches flight | high (abstract only) |
| S10 | Ribeiro Filho, Tinoco-S., Nascimento, Lacava, "A Telemetry Antenna Design for a Sounding Rocket Competition", IEEE APM 59, 2017 (+ 2013 IEEE conf "Flush-mounted telemetry antenna design...") | peer-reviewed | flush circumferential microstrip array on student rocket + truncated-corner CP patch ground antenna | high (abstract only) |
| S11 | Altus Metrum owner's manual (altusmetrum.org/AltOS/doc/altusmetrum.html) | manufacturer manual | ~7 in λ/4 wire at 435 MHz toward nose; carbon fibre & metal bays RF-opaque → SMA + external antenna; some "carbon" is black fibreglass; Arrow 440-3/440-5 Yagis for RDF | medium-high |
| S12 | G3SEK/KY4Z/W6NBI DL6WU.BAS (ifwtech.co.uk/g3sek/diy-yagi/dl6wu-gg.bas) implementing Hoch "Extremely Long Yagi Antennas", VHF Comms 3/82 | design program (data from DL6WU) | DL6WU spacings 0.2 refl, then 0.075,0.180,0.215,0.250,0.280,0.300,0.315,0.330,0.345,0.360,0.375,0.390,0.400,0.400λ; director length fit (K1−K2 lnN)(1−K3 e^{−K4 N}) per d/λ table; reflector from X=+20 Ω; DE formula ×1.02 for folded dipole; boom corr 733BD(0.055−BD)−504BD(0.03−BD) of BD (bonded), half if insulated; gain 9.2+3.39 ln(BL) dBd; tolerance ±0.003λ | high (NOTE: fetched by curl, text only) |
| S13 | Cebik, "Appreciating DL6WU wide-band long-boom Yagi design" (antenna2.github.io/cebik) | expert article (NEC) | 432 MHz 4 mm: refl 0.491λ, DE 0.476λ; NEC gains 12 el 2.85λ 14.73 dBi; 19 el 5.6λ 17.21; 26 el 8.4λ 18.59; 2:1 SWR 405–452 MHz | high |
| S14 | hamwaves.com LPDA calculator (Carrel 1961 pdf hosted there) | design notes | τ, σ, cot α=4σ/(1−τ), σopt=0.243τ−0.051, Bar=1.1+7.7(1−τ)²cotα, Bs=B·Bar, N=1+ln Bs/ln(1/τ), Zc feeder formula | medium-high |
| S15 | NEC-2 manual part III, Section II "Structure modeling guidelines" (nec2.org) | manual (LLNL, Burke & Poggio 1981) | Δ<0.1λ (0.05λ critical), Δ>1e-3λ, Δ/a>8 thin kernel (>2 min), EK Δ/a≥2 (≥0.5), junction rules, ground models, patch ≥25/λ², no ground stake, no circumferential current | high |
| S16 | Cebik, "When not to use NEC" (amod128) | expert article | non-round/flat elements, PCB antennas with substrate, IS/UM limits | medium |
| S17 | IEEE Std 145-1993 Definitions of Terms for Antennas (McMaster copy) | standard | defs: directivity, gain (excl. mismatch & polarization), realized gain (incl. mismatch, excl. polarization), radiation efficiency, effective area =λ²G/4π, far field 2D²/λ, reactive near field λ/2π, sense of polarization (clockwise viewed in direction of propagation = right-hand) | high |
| S18 | openEMS Simple Patch Antenna tutorial (docs.openems.de) | tool docs | patch at 2.4 GHz with lumped port + nf2ff box | high |
| S19 | McKinzie 1997 modified Wheeler cap (Semantic Scholar); Wang thesis "Design and construction of a Wheeler cap test set-up" (diva-portal) | peer-reviewed / thesis | Wheeler cap method & modified version | medium (abstract level) |
| S20 | Espressif ESP32-S3 Hardware Design Guidelines, PCB layout (docs.espressif.com) | manufacturer | module antenna beyond board edge, feed near edge, cut-outs; (15 mm keep-out figure from third-party blog — verify) | medium |
| S21 | Fair-Rite 43 data sheet; Palomar ferrite mix selection | manufacturer / vendor | 31 MnZn 1–300 MHz CM suppression; 43 NiZn 20–250 MHz; 61 for VHF/UHF | medium |
| S22 | NASA GSFC Wallops, NASA Sounding Rockets User Handbook 810-HB-SRP (July 2015) §5.6, §5.9.3 (pdftotext: tool-results/nasa_srp.txt) | government handbook | wraparound S-band antennas linearly polarized, omni, nulls at nose & tail; quadraloop CP command antennas phased aft/broadside; CP helix ground antennas; GPS L1 wraparound + preamp; pyro vs antenna documentation | high |
| S23 | u-blox ZED-F9P Integration Manual UBX-18010802 R16 (pdftotext tool-results/f9p.txt) | manufacturer manual | active antenna required; 17–50 dB total gain incl. losses (ideal 30–40), NF<4 dB (system ~3), group delay ≤10 ns, out-of-band rej 40 dB, element 3 dBic L1/2 dBic L2 on 150 mm ground, AR ≤2 dB zenith, PCV<10 mm, ESD mandatory, 120 nH bias-T, patch ground ≥100–150 mm, C/N0>40 for RTK, L1&L2 enable together, helix OK without ground | high |
| S24 | MAX-M10S integration manual (search-result summary only; PDF > fetch limit) | manufacturer | internal LNA (low-gain default; bypass for active antennas), internal SAW, LTE B13 notch | medium |
| S25 | TI AN043 (SWRA117) Small Size 2.4 GHz PCB antenna (pdftotext) | app note | 15.2×5.7 mm IFA; coax placement changes f by 5–10 MHz, RL by 3–4 dB; BW 250 MHz free → 100 MHz in laptop; thickness compensation | high |
| S26 | Johanson 0433AT62A0020 datasheet v3.0 (pdftotext) | datasheet | EVB1: −4.0 dBi avg, RL≥9.5 dB; larger PCB: −7.2 dBi avg, RL ≥5 dB; pi network | high |
| S27 | Ignion NN03-310 TRIO mXTEND user manual (Dec 2025, pdftotext) | manufacturer | 698–960 MHz >50–55% eff, 1.1–1.5 dBi, 142×60 mm board, clearance 40×12 mm | high |
| S28 | Espressif ESP32-S3 PCB layout guidelines (WebFetch) | manufacturer | antenna beyond edge; feed near edge; cut-outs; ≥15 mm clearance; CLC match; don't centre module | high |
| S29 | C. Counselman W1HIS, Common-Mode Chokes (2006 YCCC draft; pdftotext) | expert article | ≥1 kΩ resistive chokes, often 3–6 kΩ; binocular ferrite designs; commercial choke overheating | medium-high |

## Contradictions / discrepancies found
- Helix gain: Kraus G=15(C/λ)²NS/λ vs King&Wong measured (gain factor 4.2–7.7 instead of 15) vs Emerson NEC (Kraus optimistic by up to 4–5 dB). Resolution: Kraus assumed Hansen–Woodyard phase velocity + G≈41250/HPBW² ignoring minor lobes; measured G·HPBW² is 24000–31500 (King&Wong). Use Emerson or KW formula for design.
- Dipole impedance: textbook induced-EMF 73.1+j42.5 Ω applies at exactly λ/2 with an assumed sinusoidal current; our MoM (a=1e-4λ) gives 80.1+j44.6 Ω at exactly λ/2 and 72 Ω resistive at resonance (0.484λ). Not a contradiction of physics — different definitions; pages state both.
- Small-antenna Q: Hansen's form of Chu (1+3k²a²)/(k³a³(1+k²a²)) vs McLean 1/(ka)³+1/(ka): differ up to 12% near ka≈0.5; numeric stored-energy integral and Chu's circuit energy both reproduce McLean exactly.
- Small-loop R_r = 20π²(C/λ)^4 underestimates by 24% at C=0.136λ and ~2× at 0.23λ (MoM) — formula only valid C ≲ 0.07–0.1λ.
- DL6WU gain formula 9.2+3.39 ln(B/λ) dBd is ≈0.1–0.25 dB optimistic vs our MoM (and Cebik's NEC).
- Carrel LPDA gain contours reported ~1–2 dB optimistic by later work (Butson & Thompson 1976) — cited secondarily.
- Patch directivity: two-slot pattern integration vs Jackson CAD D≈3/(pc1): differ 0.2–0.4 dB (PCB substrates), ~0.8–1 dB (air, ceramic).
- WebFetch summary of TI DN023 was fabricated (100×100 mm ground, 85–90% efficiency); the PDF says 31×45 mm ground and −0.12 dBi max gain. Always pdftotext.
- TI AN058 states physics loosely ("antenna basically an air core inductor", "λ/2 dipole produces most power at the ends"); both are wrong as physics statements — current (and radiation source strength) is maximum at the centre of a λ/2 dipole. Use AN058 for practice only.

## Knowledge gaps noticed (for later gap-filling)
- APCP (amateur) motor plume attenuation at 433/915 MHz: no data found; only M-V P-band (Kinefuchi 2015).
- Nose-cone detuning magnitude and whip-on-flight-computer gain: need openEMS models of team hardware.
- QFH dimensions not verified numerically (general MoM could model it).
- Primary papers not read: Butson&Thompson 1976, Thal 2006, Gustafsson 2007, Kilgus 1969/75, Garg CP rule ΔS/S=1/(2Q0), IEEE Std 149, Ludwig wire-grid equal-area rule.
- MAX-M10S internal LNA NF/blocking specs (PDF too large to fetch); UHF ferrite bead impedance at 433/915 MHz; EBYTE stock antenna specs.
- Cross-code NEC-2 vs our MoM table for DL6WU Yagis; ITC proceedings sweep for wraparound/telemetry antenna papers (DTIC AD1105046 was 403).
- EZNEC licence status (freeware v7?) to confirm.

## Cross-domain notes (things other domains should cover/link)
- 02-electromagnetics already covers nose-cone wall loss & CFRP shielding (em_fresnel_radome.py) — linked from antennas-on-rockets; numbers consistent.
- 09: polarization-mismatch-loss should use the IEEE handedness & PLF closed form verified in ant_polarization.py; Fresnel-zone numbers for recovery phase.
- 15: rocket-telemetry-radio-design / ground-station-design should link antennas-on-rockets (axial null table, CP ground antenna recommendation) and yagi page designs.
- 16: add an openEMS worked example of the 2.45 GHz FR-4 inset patch (validate inset depth) and a nose-cone detuning model.
- 17: antenna-range-ota-testing should link antenna-measurement.

## Resume instructions (what the next agent should do if this one is interrupted)
- TASK COMPLETE (2026-09-27): all 15 topic pages + _index.md + _sources.md written in kb/08-antennas/; 11 verification scripts in tools/verify/ant_*.py (ant_dipole, ant_mom_wire, ant_mom_general, ant_yagi [~3.5 min], ant_patch, ant_small_limits, ant_aperture, ant_helix, ant_polarization, ant_rocket, ant_measurement) all run. Links/anchors checked (all resolve or point to INDEX-planned pages).
- Follow-up work belongs to gap-filling waves: see "Knowledge gaps noticed" above.
