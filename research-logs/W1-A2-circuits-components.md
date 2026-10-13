# Research log W1-A2: 01-circuit-theory + 04-real-components-hf
Status: complete
Owner scope: kb/01-circuit-theory/, kb/04-real-components-hf/, research-logs/W1-A2-circuits-components.md,
tools/verify/circuits_*.py, tools/verify/components_*.py

## Plan
Order: foundational circuit pages first (they are prerequisites for component pages), then components,
then _index/_sources for both domains. Each page: research 3–6 sources, write, verify in Python, log.

### 01-circuit-theory
(ALL 8 PAGES + _index + _sources DONE 2026-09-27)
- [x] lumped-elements-impedance-admittance — done (kb/01-circuit-theory/lumped-elements-impedance-admittance.md; verify circuits_impedance_basics.py) — V–I laws, reactance vs f, Z/Y, series/parallel algebra, reactance charts
- [x] network-theorems-max-power-transfer — done (verify circuits_power_transfer.py) — KCL/KVL, nodal/mesh, Thevenin/Norton, superposition, MPT, conjugate match, 50% efficiency, power vs noise vs efficiency match
- [x] resonance-and-q — done (verify circuits_resonance_q.py) — series/parallel resonance, energy Q, Qu/QL/Qe, BW, series<->parallel conversion, component Q, IL vs Q
- [x] passive-filter-design-prototypes — done (verify circuits_filter_prototypes.py) — Butterworth/Chebyshev/elliptic/Bessel g-values, scaling, transforms, group delay, finite-Q; 433 MHz harmonic LPF + 915 MHz BPF worked examples (verify w/ scikit-rf)
- [x] two-port-networks-zyh-abcd — done (verify circuits_two_port.py) — Z/Y/h/ABCD/T, conversions, cascading, reciprocity/symmetry/lossless
- [x] transformers-coupled-inductors — done (verify circuits_transformers.py) — ideal xfmr, k, leakage/magnetising L, impedance transformation, tapped L / cap divider matching
- [x] transient-and-step-response — done (verify circuits_transient.py) — RC/RL/RLC, damping, 0.35/tr, ringing
- [x] energy-storage-and-reactive-power — done (verify circuits_reactive_power.py) — complex power, PF, stored energy, reactive power in tanks, cap voltage ratings
- [x] _index.md, _sources.md (01)

### 04-real-components-hf
(ALL 8 PAGES + _index + _sources DONE 2026-09-27)
- [x] resistors-at-rf — done (verify components_resistors.py) — thin/thick film, parasitics, package size, terminations/attenuators, power derating
- [x] capacitors-at-rf-mlcc — done (verify components_mlcc.py) — dielectric classes, DC-bias/temp derating, ESR/ESL/SRF, Q, DC-block vs bypass by SRF, parallel anti-resonance, RF-grade parts, voltage ratings in tanks
- [x] inductors-at-rf — done (verify components_inductors.py) — air-core, wirewound ceramic, multilayer, thin-film; Q vs f; SRF; saturation; Wheeler/Nagaoka verified
- [x] ferrites-and-beads — done (verify components_ferrite_bead.py) — R vs X curves, DC-bias collapse, bead–cap resonance, Fair-Rite materials, CM chokes, when a bead hurts
- [x] pcb-parasitics-traces-vias-pads — done (verify components_pcb_parasitics.py) — trace L, via L formula, pad C, plane gaps, ground-return L; quantified
- [x] crystals-and-resonators — done (verify components_crystal.py) — BVD model, series/parallel resonance, CL calc, ESR, drive, pullability, XO/TCXO/VCXO/OCXO/MEMS, ppm→Hz at 433/915, LoRa TCXO need, aging, AT-cut cubic
- [x] package-parasitics-bondwires — done (verify components_bondwire.py) — bondwire L, QFN EP inductance, lead L by package, many ground pins
- [x] component-models-s2p-spice — done (verify components_s2p_models.py) — vendor S-param files & models, simulator use, pitfalls
- [x] _index.md, _sources.md (04)

### Verification scripts (tools/verify/)
- circuits_filter_prototypes.py, circuits_resonance_q.py, circuits_two_port.py, circuits_transient.py,
  circuits_power_transfer.py, components_mlcc_srf.py, components_air_coil.py, components_pcb_parasitics.py,
  components_crystal.py, components_ferrite_bead.py (names may be adjusted; see log)

## Log (append-only)
- 2026-09-27 — Read CONVENTIONS.md, INDEX.md, HANDOFF.md, CLAUDE.md. Created this log.
- 2026-09-27 — Filter prototype sources: Steer *Microwave and RF Design IV* (LibreTexts, open textbook) §2.7 Butterworth/Chebyshev g-value formulas; Stanford EE133 filter cookbook (Butterworth/Chebyshev/Bessel tables). Bessel ladder values in cookbook are delay-normalised (to verify in Python).
- 2026-09-27 — MLCC: ATC/Kyocera-AVX "Circuit Designer's Notebook: Capacitors in coupling and DC blocking" (Fiore): ATC100A101 100 pF FSR 1000 MHz ESR 0.072 Ω; 600S101 (0603) 100 pF FSR 1340 MHz; 100A270 27 pF 1870 MHz; 600S560 56 pF 1890 MHz; 100A160 16 pF 2410 MHz; 600S390 39 pF 2340 MHz; first parallel resonance of 100A101 flat-mounted 1.6 GHz, edge-mount suppresses (usable to ~2.4 GHz); caps can be used above FSR if net |Z| small; several tenths dB IL acceptable.
- 2026-09-27 — Murata GJM (Modelithics-hosted catalog C-29-C): Cu electrodes, C0G 0±30 ppm/°C −55..125 °C; ESR spec ≤300 mΩ (1–5 pF), ≤250 mΩ (5–10 pF) at 1 GHz Boonton 34A; ≤400 mΩ (10–33 pF) at 500 MHz; Q≥1000 (≥30 pF) or ≥400+20C at 1 MHz.
- 2026-09-27 — Johanson high-Q catalog: SRF strongly substrate/pad/measurement dependent (charts on 16 mil RO4003, series mount, horizontal orientation); vertical orientation eliminates parallel resonances & lowers L; horizontal lowers coupling.
- 2026-09-27 — KEMET F9000 general info: Class 1 εr 80–300, no ageing; Class 2 BaTiO3 ferroelectric; EIA RS-198 code table (X/Y/Z low T; 2/4/5/6/7/8 high T; A..V tolerance letters incl. R=±15%, S=±22%, V=+22/−82%); ageing log law, 1000 h reference, de-age 150 °C 1 h. Johanson Dielectrics ageing note: X7R/X5R −2.5 %/decade-hour, Y5V −7 %/decade-hour.
- 2026-09-27 — Maxim/ADI tutorial 5527 (Fortunato 2012) via search summary: 4.7 µF 6.3 V 0603 X5R at 5 V → 0.33 µF (−92.9 %). analog.com timed out (fetch failed) — fact taken from search-result summary + widely reproduced.
- 2026-09-27 — Ferrite beads: Burket, "Ferrite Beads Demystified", Analog Dialogue 50-02 (2016) / AN-1368 via Power Systems Design reprint: model of Tyco BMB2A1000LN2 (L=1.208 µH, Cpar=1.678 pF, Rdc=0.3 Ω, Rac=1.082 kΩ); at 50 % rated current inductance can fall up to 90 %; TDK MPZ1608S101A 100 Ω→10 Ω at 100 MHz @50 % rated I; bead+10 nF resonance ≈2.5 MHz, +10 dB gain; damping methods A/B/C.
- 2026-09-27 — Fair-Rite: "How to choose ferrite components for EMI suppression" (catalog 14th ed. technical section): Z = jωL0(µs'−jµs''), L0 = 4πN²·1e-9/C1 (C1 = Σl/A, cm⁻¹); H = 1.256 N I / lm (Oe); material table 73 (1–25 MHz), 31 (1–300 MHz), 43/44 (20–300 MHz), 61 (200+ MHz). Datasheets: 43 NiZn µi 800 ρ 1e5 Ω·cm Tc>130 °C; 31 MnZn µi 1500 ρ 3000 Ω·cm Tc>130 °C; 61 NiZn µi 125 ρ 1e8 Ω·cm Tc>300 °C (inductive to 25 MHz, suppression >200 MHz).
- 2026-09-27 — Decoupling anti-resonance: Archambeault ("Eliminating myths about PCB power/ground plane decoupling", Interference Technology) — adding second value gives no noticeable HF improvement; different values → anti-resonance peaks; trade-off: spread SRFs keep damping.

- 2026-09-27 — Coilcraft 0402HP datasheet (Doc 526, rev 12/20/23): full L/Q/SRF/DCR/Irms table (e.g. 10N: L 9.98@900 MHz, 10.4@1.7 GHz, Q 62/90, SRF 4.7 GHz, DCR 0.11 Ω, 1.3 A; 47N: 49.0/58.9 nH, SRF 2.4 GHz). Fixtures: L at test freq with SMD-F in 4286; Q with 4287A+16197; SRF with 8722ES + SMD-D. NOTE: simple one-pole L_eff = L0/(1-(f/fSRF)^2) over-predicts the measured L rise using the datasheet SRF (check in components_inductor script) → contradiction/limitation logged.
- 2026-09-27 — Knight, "An introduction to the art of solenoid inductance calculation" v0.20 (2016): Nagaoka kL def (Ls = µ π r² N² kL / ℓ), Lorenz elliptic form, Lundin 1985 handbook formula (<3 ppm), kL(ℓ/D=1)=0.688423, Wheeler 1928 (derived 1925) a²N²/(9a+10b) µH inches ±1% for b>0.8a; metric form kW25 = 1/(1+0.45 D/ℓ) ±0.33% for ℓ≥0.4D.
- 2026-09-27 — Via inductance: Goldfarb & Pucel, IEEE MGWL 1(6) 135–137, 1991 (formula via Qucs technical docs node83); H. Johnson "Via inductance" & "Via inductance II" HSDD newsletters vol 6 #4/#8: loop L between planes (µ/2π)·h·ln(s/r) per via (go+return ⇒ ×2); example r=0.005", h=0.040": s=0.017" predicted 0.49 nH measured 0.46; s=0.12" predicted 1.29 measured 1.41.
- 2026-09-27 — Semtech AN1200.14 rev 2.1 (2018) XO guidance: crystal spec table (26–32 MHz, Rs 30/40 Ω, C0 ≤7 pF, CL 6–12 pF, FTOL ±10/±30 ppm, g-sens 2 ppb/g typ), ±25 % BW offset tolerated at 10 % PER, recommend low-g crystal for mobile/vibration. Semtech AN1200.37 (2018) best performance: PA self-heating drifts XO; thermal isolation cuts; TCXO below −20 °C/above 70 °C or long +22 dBm packets. SX1261/2 datasheet rev 1.2 (2019): crystal 32 MHz, CL 10 pF, C0 0.6 typ, Rs 30/60 Ω, Cm 1.3–2.5 fF, drive ≤100 µW; FERR_L ±25 % BW (and SF12 ±50 ppm, SF11 ±100, SF10 ±200 ppm, tighter applies); internal trim caps 11.3–33.4 pF in 0.47 pF steps; OSC_TRM ±15 ppm min; TCXO via 220 Ω + 10 pF to XTA, clipped sine ≤1.2 Vpp, DIO3 1.6–3.3 V; LoRaWAN end-device ±30 ppm total; Freq_drift_max formula is an image — BW/(3·2^SF) inferred from search summaries (10.2 Hz at SF12/BW125; ×16 with LDRO) — medium confidence.
- 2026-09-27 — Packages: TI "QFN package comparison tables": avg lead L 20-pin SOIC 5.01 nH, SSOP 3.50, TSSOP 2.81, TVSOP 2.56, QFN 1.18 nH (C 0.72/0.42/0.32/0.34/0.25 pF); 16-pin QFN 0.82 nH; 14-pin 0.79 nH. TI SLVAEE1 (Fagnani 2019): Cu bondwire 1 mm × 50.8 µm ≈ 8.6 mΩ; HotRod flip-chip 1 nH vs std QFN 1.4 nH switching loop.
- 2026-09-27 — Vishay tech note 60107 "Frequency response of thin film chip resistors" (2009): 0.1–40 GHz, NiCr on alumina, 50–1000 Ω; lumped model (internal C, L; external LC, CG); internal C: 0201 0.0206 pF, 0402 0.0262 pF (flip), 0402 wrap 0.0392 pF/0.121 nH, 0603 0.0403 pF; low values inductive, high values capacitive; smaller case better; flip > wrap; edge-sense trim > S-cut > L-cut.
- 2026-09-27 — Murata MLCC S-parameter measurement conditions page: shunt mode (1-port/2-port shunt), Yokowo PC-SMA jigs, microstrip 100 µm glass-epoxy (≤8.5 GHz) or 160 µm fluorine CPW (≤20 GHz), land/via de-embedded; no DC bias. Coilcraft Doc 1721 (2023): RF inductor S-params are generated from a fitted SPICE model (first resonance only), de-embedded 50 Ω, exclude board; simulated SRF higher than on-board; small-signal only (no saturation); use Modelithics substrate-scalable models or measure on intended PCB.
- 2026-09-27 — Vig, "Quartz crystal resonators and oscillators … a tutorial", SLCET-TR-88-1 rev 8.5.2.0 (Jan 2004): XO 1e-5–1e-4, TCXO 1e-6, MCXO 1e-8–1e-7, OCXO 1e-8 (incl. env + 1 yr aging); analog TCXO ~20× improvement, OCXO >1000×; comparison table (TCXO aging 5e-7/yr, temp stab 5e-7 −55..85); pulling Δf/f = C1/(2(C0+CL)), example C0 5 pF, C1 14 fF, CL 20 pF; acceleration table (missile boost 15 g peak; 1e-9/g reference oscillators); vibration phase excursion Δφ = ΓA f0/fv.
- 2026-09-27 — Semtech SX1261/2 DS: Freq_drift_max formula image not extractable; search summaries (Semtech forum + arXiv 2101.06016) give BW/(3·2^SF) (10.2 Hz SF12/BW125; ×16 with LDRO → ~160 Hz). One summary wrote Rs/(3·2^SF), which is dimensionally inconsistent with the 10.2 Hz figure — logged as contradiction; adopt BW/(3·2^SF) = Rs/3 (medium confidence).
- 2026-09-27 — ST AN2867 (oscillator design guide): CL = CL1·CL2/(CL1+CL2) + Cs; gain margin ≥5 (search summary; st.com PDF timed out).
- 2026-09-27 — AT-cut: IQD guide (35°15′ cut, inflection ~25 °C, symmetric about 25 °C); cubic coefficients from Bechmann-type model (≈1.1e-4 ppm/K³; ≈−0.085 ppm/K per arcmin) are from memory of Bechmann/Ballato/Lukaszek 1962 — flag medium confidence; verify self-consistency numerically.
- 2026-09-27 — Rise time: Keysight AN 5988-8008 & 5989-5733: 0.35/BW for Gaussian/single-pole, ~0.4–0.45 for maximally-flat scope responses. PA load-line: Cripps WAMICON 2005 tutorial; Ropt ≈ (Vdd−Vknee)²/(2 Pout) (AAC load-pull article).
- 2026-09-27 — WROTE lumped-elements-impedance-admittance.md + tools/verify/circuits_impedance_basics.py; network-theorems-max-power-transfer.md + tools/verify/circuits_power_transfer.py (all asserts pass).
- 2026-09-27 — WROTE resonance-and-q.md (+circuits_resonance_q.py: BW=f0/Q, energy Q, loaded Q, IL=-20log(1-QL/Qu), group delay 2QL/w0, L-match BW≈2/Qn verified; approx weakens Qn<3). WROTE passive-filter-design-prototypes.md (+circuits_filter_prototypes.py: g-values vs tables <3e-4; Bessel table = delay-normalised series-L-first, matches scipy exactly; elliptic N=5 ladder fitted to scipy; delay-loss rule dL=8.686·δ·τg verified <1%; Cohn formula within ~5%; 433 MHz LPF & 915 MHz BPF examples; scikit-rf cross-check 1e-15).
- 2026-09-27 — WROTE two-port-networks-zyh-abcd.md (+circuits_two_port.py: all conversion-table entries vs scikit-rf 1.3e-13, ABCD/T cascade, reciprocity/lossless tests, examples). WROTE transformers-coupled-inductors.md (+circuits_transformers.py: coupled = T = cantilever model exact; 1:4 xfmr band 2.0 MHz–791 MHz vs estimates 2.0/798; cap-divider approx error 11% at Q2=2.7; tap transformation vs k; k from mode split exact).
- 2026-09-27 — Coordinator resume message received (said I was "about to write the filter script" — stale; filter page+script were already done). Continuing with transient-and-step-response.
- 2026-09-27 — WROTE transient-and-step-response.md (+circuits_transient.py: tr·f3dB 0.34–0.41 across 11 responses; RLC overshoot formula exact; cascade rule −3…−10 %; probe ringing 119 MHz). WROTE energy-storage-and-reactive-power.md (+circuits_reactive_power.py: Tellegen balance, Q=2w(Wm−We), L-match element vars = Qn·P, elliptic LPF internal 23.8 V pk at 2 W, loop antenna 386 V pk).
- 2026-09-27 — WROTE kb/01-circuit-theory/_index.md and _sources.md. Starting 04 with capacitors-at-rf-mlcc.
- 2026-09-27 — Kyocera-AVX LICC PDF: ESL (100 nF parts) 1206 1200 pH, 0805 800, 0603 700, 0612 LICC 170, 0508 130, 0306 110, IDC 50–60, LICA 25 pH. Contrast: ATC 600S 0603 FSR-implied ESL 0.12–0.14 nH (series-thru microstrip) → logged as measurement-configuration discrepancy.
- 2026-09-27 — WROTE capacitors-at-rf-mlcc.md (+components_mlcc.py: implied ESL, SRF tables, DC-block S21 table, cap Q, anti-resonance 100nF||100pF → 20.8 Ω @ 503 MHz; |Z|(433.92) 3.3 Ω vs 1.36 Ω alone).
- 2026-09-27 — Murata LQG15HS catalog (O05E11): Q min 8 @100 MHz; typical Q 10 nH = 27/29/35/33/28 at 0.8/0.9/1.8/2.0/2.4 GHz; 22 nH 23/24 @0.8/0.9 GHz; SRF min 3400 (10N), 1900 (22N); DCR.
- 2026-09-27 — WROTE inductors-at-rf.md (+components_inductors.py: Nagaoka via elliptic = Neumann numerical integral = Lundin to <1e-6; Wheeler max err 0.331% for l≥0.4D, −10.6% at l=0.1D; Rosa km(N) computed (→0.337); air-coil examples; Coilcraft L(f) inconsistency quantified; skin depth).
- 2026-09-27 — WROTE ferrites-and-beads.md (+components_ferrite_bead.py: Burket bead model |Z| peak 1.08 kΩ @112 MHz, 229 Ω capacitive @433.92 MHz; bead+10nF +27 dB @1.45 MHz (Burket measured +10 dB for other parts); damping A/B/C compared — C best; DC-bias L→10 % gives 82 Ω @100 MHz; CM choke Zcm/Zdm).
- 2026-09-27 — WROTE resistors-at-rf.md (+components_resistors.py: flat R=sqrt(L/C) ≈89 Ω for 0.4 nH/0.05 pF; 10 % error frequencies; Vishay internal parasitics negligible vs mount; 2×100 Ω termination +7 dB RL; π/T pad values & power split (20 dB pad: 1.64 W of 2 W in input shunt); derating).
- 2026-09-27 — JLCPCB impedance page (via search): JLC04161H-7628 prepreg 0.2104 mm, Dk 4.4.
- 2026-09-27 — WROTE pcb-parasitics-traces-vias-pads.md (+components_pcb_parasitics.py: wire 0.82 nH/mm; microstrip L' 0.31–0.33 nH/mm, C' 0.11–0.12 pF/mm (HJ cross-check ~5%); GP via 0.54 nH (1.6 mm) vs 0.015 nH (0.21 mm); Johnson loop formula reproduces 0.49/1.29 nH; coupled vias 4→0.29 nH; pad C via wide-microstrip model (SMA pad +0.65 pF); slot stub estimate 1.4 nH/10 mm).
- 2026-09-27 — WROTE package-parasitics-bondwires.md (+components_bondwire.py: bondwire tables (1 mm 25 µm 0.82 nH), over-plane/arc/parallel effects, TI package L table reactances, EP ground path estimates, degeneration −0.34 dB (1 nH, 915 MHz), ground bounce 1.4 V (0.5 A, 0.5 nH), bondwire R (Cu 8.3 mΩ vs TI 8.6)).
- 2026-09-27 — WROTE crystals-and-resonators.md (+components_crystal.py: BVD Lm 13.1 mH, Q 87.7k, pulling −8.41 ppm/pF, fL +89 ppm numerically checked; SX126x trim range +33/−39 ppm (consistent with datasheet ±15 min/±30 typ); gm_crit 0.545 mA/V; LoRa ±25%BW → ppm tables; drift limit table; AT-cut equiripple ±2.5/±7.5/±14 ppm; g-shift, vibration sidebands, Doppler rate 305 Hz/s @915 MHz).
- 2026-09-27 — WROTE 04 _index.md and _sources.md; forum sweep (AAC/Hackaday decoupling, crystal load caps, bead peaking) added as anecdotal sources; all 16 scripts pass; link check: 0 unresolved (all links to existing or INDEX-planned pages); template/front-matter check passed for all 16 pages.
- 2026-09-27 — WROTE component-models-s2p-spice.md (+components_s2p_models.py: series/shunt extraction exact, Touchstone round trip, fixture sensitivity table (0.1 Ω: series 209 % vs shunt 0.2 %), pad-induced SRF shift 4.69→3.92 GHz, reference-plane phase, passivity detection of +0.17 dB error). Next: 04 _index/_sources.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| 1 | Pozar, Microwave Engineering 4e | textbook | all 01 pages; microstrip, S-matrix | cited by section, not re-fetched |
| 2 | Matthaei/Young/Jones; Zverev; Williams & Taylor; Hong & Lancaster | textbook | filter tables, J-inverters, dissipation | g-values re-derived & verified numerically |
| 3 | Steer, Microwave & RF Design (LibreTexts) §2.7 | open textbook | Butterworth/Chebyshev formulas | fetched |
| 4 | Stanford EE133 filter cookbook | lecture notes | Bessel/Chebyshev tables | fetched; Bessel delay-normalised (verified) |
| 5 | Cripps (book + WAMICON tutorial); AAC load-pull article | textbook/tutorial | load-line match | secondary for formula |
| 6 | Keysight AN 5988-8008 / 5989-5733 | app note | 0.35 vs 0.4–0.45 | via search summary |
| 7 | ATC/Kyocera-AVX coupling-capacitor notebook | app note | FSR/ESR/orientation | fetched, extracted |
| 8 | Murata GJM catalog; Murata S-param conditions; SimSurfing FAQ | datasheet/doc | ESR/Q, shunt measurement | fetched |
| 9 | Johanson high-Q catalog; Johanson Dielectrics ageing | datasheet/app note | orientation, ageing | fetched |
| 10 | KEMET F9000 | tech note | EIA codes, ageing law | fetched |
| 11 | Kyocera-AVX LICC | datasheet | ESL by case | fetched |
| 12 | Maxim/ADI tutorial 5527 | app note | DC-bias example | fetch timed out; search summary |
| 13 | Coilcraft 0402HP datasheet; Doc 1721 | datasheet/app note | inductor data; S-param generation | fetched |
| 14 | Murata LQG15HS catalog | datasheet | multilayer Q | fetched |
| 15 | Knight solenoid monograph; Lundin 1985; Wheeler 1928 | monograph/peer-reviewed | air-coil formulas | fetched Knight; formulas verified 3 ways |
| 16 | Burket ferrite beads (ADI) via PSD reprint | app note | bead model/damping | fetched reprint |
| 17 | Fair-Rite EMI guide + 31/43/61 sheets | tech note/datasheet | materials | fetched |
| 18 | Goldfarb & Pucel (via Qucs doc); H. Johnson via newsletters | peer-reviewed/expert | via inductance | fetched; Johnson numbers reproduced |
| 19 | JLCPCB impedance page | manufacturer | stackup | via search summary |
| 20 | TI QFN comparison tables; TI SLVAEE1 | manufacturer data/app note | package L/C, bondwire R | fetched |
| 21 | Vishay TN 60107; Yageo RC0402 | app note/datasheet | resistor parasitics, derating | 60107 fetched; Yageo via search |
| 22 | Semtech SX1261/2 DS, AN1200.14, AN1200.37 | datasheet/app note | crystal/TCXO/LoRa limits | fetched (drift formula image not extractable) |
| 23 | Vig quartz tutorial | tech report | oscillator classes, g-sensitivity | fetched |
| 24 | ST AN2867; IQD AT-cut guide | app note/article | load caps, gm_crit; AT-cut | AN2867 via search summary |
| 25 | Archambeault decoupling myths | expert article | anti-resonance | via search summary |
| 26 | AAC/Hackaday/Altium/electronics-notes | forum/secondary | misconceptions only | anecdotal |

## Contradictions / discrepancies found
- C0G/NP0 temperature range: KEMET F9000 general info states NP0 ±30 ppm/°C over −55…+85 °C; Murata GJM catalog (and EIA-198 C0G) state 0±30 ppm/°C over −55…+125 °C. Treat C0G as ±30 ppm/°C to 125 °C for modern parts; old KEMET text uses a narrower range.
- LoRa in-packet drift limit: SX1261/2 DS formula is an image; search summaries give BW/(3·2^SF) (10.2 Hz @ SF12/BW125) but one summary writes Rs/(3·2^SF) — dimensionally inconsistent with the 10.2 Hz figure. Adopted BW/(3·2^SF); medium confidence.
- Chip-inductor L(f): single-pole model L0/(1−(f/fSRF)²) with the datasheet SRF over-predicts the measured L rise for Coilcraft 0402HP (e.g. 10N: model 11.5 nH @1.7 GHz vs 10.4 datasheet). Datasheet SRF (SMD-D fixture) is lower than an "intrinsic" SRF inferred from L(f); explained by fixture/pad capacitance and distributed winding capacitance (see inductors page).
- Blog/secondary sources quote inconsistent 0402 MLCC ESL (0.2–0.4 nH vs 0.5–0.7 nH). ESL is mounting-dependent; KB uses values derived from ATC measured SRFs and vendor statements, not blogs.
- MLCC ESL: AVX quotes 0603 ≈ 700 pH (100 nF, PCB-mounted) while ATC 600S 0603 series-thru SRF data imply 0.12–0.14 nH. Not a contradiction of physics — ESL depends on mounting/measurement loop (series-thru over plane vs shunt with vias) and internal electrode count; page states ESL is a mounted-part property.
- Bessel ladder tables (Stanford EE133 / Matthaei) are delay-normalised (τ(0)=1 s), not 3-dB-normalised; convention difference, not error — flagged on filter page.

## Knowledge gaps noticed (for later gap-filling)
- In-circuit Q of JLCPCB-available chip inductors (e.g. Murata LQG/LQW, Sunlord SDCL/LQW-equivalents) at 433/915 MHz — needs bench data.
- Coupling coefficient between adjacent 0402/0603 chip inductors vs spacing/orientation — needs EM sim.
- Elliptic LPF values fitted numerically, not cross-checked against a printed Zverev table entry.

## Cross-domain notes (things other domains should cover/link)
- 15-lora-ism-radios / 09-propagation: rocket boost-phase Doppler RATE (≈305 Hz/s at 915 MHz for 100 m/s²) exceeds SF12 in-packet drift limits even with LDRO → recommend low SF during boost; crystal g-sensitivity steps at ignition/burnout. Derived on crystals page; W2-B6 should treat in rocket-telemetry-radio-design.
- 19-regulations: SRD harmonic/spurious limits (ETSI EN 300 220, IMDA, FCC 15.247/15.249) — needed by 01 filter page's 433 MHz harmonic LPF example (linked to spectrum-allocation-ism-bands).
- 06-rf-circuits: SAW/ceramic filter insertion loss numbers for 902–928 MHz to contrast with the 9 dB lumped design (filter page); baluns/transmission-line transformers (transformers page links there); PA load-pull and harmonic terminations (network-theorems page).
- 13-pcb-rf-layout-emc: filter layout (ground vias per shunt cap, input/output isolation), inter-inductor coupling.
- 03-transmission-lines-matching: power-wave vs pseudo-wave S-parameters for complex references (two-port page defers there).
- 18-components-parts: JLCPCB-stocked RF-grade C0G caps and wirewound inductors.

## Resume instructions (what the next agent should do if this one is interrupted)
- TASK COMPLETE (2026-09-27): all 8 pages of 01-circuit-theory and all 8 pages of 04-real-components-hf written, plus _index.md and _sources.md for both; 16 verification scripts in tools/verify/ (circuits_*.py ×8, components_*.py ×8) all pass.
- Possible follow-ups (gap filling, not required): bench-measure JLCPCB-stocked inductor Q and mounted MLCC ESL; EM-simulate pad capacitance and chip-inductor coupling on JLC stackups; cross-check elliptic values vs Zverev tables; confirm SX1261/2 Freq_drift_max formula from latest datasheet; fetch Bechmann AT-cut coefficients from a primary source.
