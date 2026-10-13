# 06-rf-circuits — RF building blocks

Scope: the circuit blocks between the antenna and the baseband — amplifiers (stability/biasing, LNAs, PAs), passive networks (filters, couplers/dividers/combiners, baluns and transformers, switches/attenuators/limiters, circulators/isolators), frequency-translation and generation blocks (mixers, VCOs and PLL synthesizers, multipliers/dividers, detectors), and how they are combined into receiver and transmitter architectures. Pages apply the theory from [03 transmission lines & matching](../03-transmission-lines-matching/), [05 analog electronics](../05-analog-electronics/) and [07 noise & linearity](../07-noise-linearity/); parts catalogues live in [18](../18-components-parts/), complete projects in [20](../20-projects-recipes/). Every page has a verification script in `tools/verify/rfckt_*.py` or `tools/verify/rf2_*.py` (all end "ALL PASS"). Worked examples are chosen for 433/915 MHz LoRa telemetry, GNSS L1 and 2.45 GHz.

## Reading order (beginner → advanced)
1. [Amplifier stability and biasing](amplifier-stability-and-biasing.md) — why amplifiers oscillate; K, μ; bias tees, bias networks, GaN sequencing.
2. [LNA design](lna-design.md) — gains, noise parameters and circles, worked 433 MHz and 1575 MHz designs.
3. [RF filters](rf-filters-lc-saw-baw-cavity-microstrip.md) — technology choice, Q vs loss, microstrip and coupled-resonator design.
4. [Couplers, dividers, combiners](couplers-dividers-combiners.md) — Wilkinson, hybrids, directional couplers.
5. [Baluns and RF transformers](baluns-and-rf-transformers.md) — lattice, Marchand, TLTs, chip baluns.
6. [RF switches, attenuators, limiters](rf-switches-attenuators-limiters.md) — PIN/SOI switches, T/R, pads, LNA protection.
7. [Mixers](mixers.md) — switching mixers, spurs, image rejection, Gilbert, harmonic/subsampling.
8. [VCOs and PLL synthesizers](vco-and-pll-synthesizers.md) — loop filters, phase-noise budgets, fractional-N, DDS.
9. [Power amplifiers](power-amplifiers.md) — classes A–F, load line, Doherty, DPD, harmonics, thermal.
10. [Detectors and power meters](detectors-and-power-meters.md) — diode, log and RMS detectors.
11. [Frequency multipliers and dividers](frequency-multipliers-dividers.md) — class-C multipliers, 20 log N, prescalers.
12. [Circulators and isolators](circulators-isolators.md) — ferrite physics, PA protection, duplexing.
13. [Receiver architectures](receiver-architectures.md) — superhet, zero-IF, low-IF, direct sampling, frequency planning.
14. [Transmitter architectures](transmitter-architectures.md) — IQ up-conversion, polar, pulling, masks.
15. [AGC loops and receiver gain control](agc-loops-and-receiver-gain-control.md) — loop dynamics, attack/decay, digital AGC, gain plans, RSSI, NB/NR/ANF.
16. [PA control, protection and sequencing](pa-control-protection-and-sequencing.md) — ALC, ramping, VSWR foldback, mismatch stress, T/R and bias sequencing, class D.
17. [Duplexers, diplexers and crystal filters](duplexers-diplexers-and-crystal-filters.md) — cavity/SAW duplexers, 433+915 MHz diplexer, crystal ladder design, ceramic/MCF.
18. [Modulator and detector circuits](modulator-and-detector-circuits.md) — varactor/reactance FM, PM, balanced modulators, envelope/product detectors, discriminators.
19. [Co-site interference and transmitter intermod](co-site-interference-and-transmitter-intermod.md) — reverse IMD, antenna isolation, launch-site planning, on-board coexistence.
20. [Oscillator phase noise: ISF/LTV, AM–PM, g-sensitivity](oscillator-phase-noise-ltv-isf.md) — Hajimiri–Lee theory, flicker up-conversion, microphonics, rocket vibration.

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [amplifier-stability-and-biasing](amplifier-stability-and-biasing.md) | K, Δ, μ/μ′ derivations; stability circles; Rollett invariants; stabilisation study on real ATF-54143 data; via inductance; bias tees; BJT/pHEMT/GaN bias and sequencing; bench oscillation causes | mixed | high |
| [lna-design](lna-design.md) | G_T/G_A/G_power (operating; textbook G_P)/MAG, SCM, noise & gain circles, inductive degeneration (derived), noise measure; verified ATF-54143 LNAs at 433 MHz (0.38 dB, 22 dB) and 1575.42 MHz (0.74 dB, 19 dB); MMIC choices; ground-station LNA placement; damage budget | mixed | high |
| [power-amplifiers](power-amplifiers.md) | conduction-angle and class-F/E theory (verified), Cripps load line and contours, AFT05MS003N 433 MHz design, SKY66122 915 MHz FEM, ETSI harmonic budgets, Doherty, ET, DPD, thermal, ruggedness; linearisation beyond DPD (feedforward, Cartesian, LINC/Chireix, EER, envelope feedback) | mixed | high |
| [rf-filters-lc-saw-baw-cavity-microstrip](rf-filters-lc-saw-baw-cavity-microstrip.md) | technology survey with Q; Cohn loss formula; Richards/Kuroda; stepped-impedance LPF and coupled-line BPF on FR-4 (skrf + own FD solver); coupled-resonator design, k/Qe extraction; coupling matrix and cross-coupling | mixed | high |
| [couplers-dividers-combiners](couplers-dividers-combiners.md) | three-port theorem; Wilkinson (equal/unequal/lumped), branch-line, rat-race, Lange, coupled-line couplers (TEM vs microstrip directivity), resistive splitters, combining efficiency; non-ideal Wilkinson (lossy-arm R_opt, unequal/tied loads, uncorrelated combining, noise correlation) | mixed | high |
| [baluns-and-rf-transformers](baluns-and-rf-transformers.md) | mixed-mode parameters, lattice LC balun, Marchand (Z0o = √(RsRb)/2 limit), Guanella vs Ruthroff, LF limit, imbalance→CM, Johanson chip balun | mixed | high |
| [rf-switches-attenuators-limiters](rf-switches-attenuators-limiters.md) | series/shunt switch formulas, PIN physics, λ/4 T/R switch, FET/SOI Ron·Coff, PE4259, Pi/T pads, DSAs, diode/PIN limiters and LNA protection | mixed | high |
| [mixers](mixers.md) | switching-mixer 2/π, LO-harmonic responses, spur/image/half-IF, DBM specs, IRR vs imbalance, Hartley/Weaver, Gilbert IIP3 = 4V_T, passive mixers, APDP harmonic mixers, subsampling | mixed | high |
| [vco-and-pll-synthesizers](vco-and-pll-synthesizers.md) | loop-filter synthesis (Banerjee), ADF4351 433.92 MHz design, noise budget and jitter-optimal bandwidth, ΣΔ noise (simulated), spurs, lock time, DDS, Si5351, Leeson | mixed | high |
| [receiver-architectures](receiver-architectures.md) | superhet IF choice (image/half-IF table), dual conversion, zero-IF impairments (IIP2, DC offset, flicker), low-IF (SX126x, R820T), direct sampling (jitter), reciprocal mixing, cascade | mixed | high |
| [transmitter-architectures](transmitter-architectures.md) | IQ modulator sideband/carrier leakage, pulling and VCO plans, two-step, direct PLL modulation (LoRa/FSK), polar (delay/bandwidth), outphasing, masks and spurs | mixed | high |
| [detectors-and-power-meters](detectors-and-power-meters.md) | diode square-law theory, sensitivity & TSS (HSMS-285x), square-law→linear, AD8307/AD8318/LTC5582, waveform-dependent readings, temperature | mixed | medium |
| [frequency-multipliers-dividers](frequency-multipliers-dividers.md) | harmonic currents & optimum conduction angles, push-push/APDP, Page/Manley–Rowe limits, 20 log N and carrier collapse, dividers, dual-modulus prescalers, comb generators | mixed | high |
| [circulators-isolators](circulators-isolators.md) | non-reciprocity and the three-port theorem, Polder tensor, Faraday rotation, junction/lumped circulators, isolator PA protection numbers, T/R leakage, magnet-free circulators | mixed | medium |
| [agc-loops-and-receiver-gain-control](agc-loops-and-receiver-gain-control.md) | dB-linear AGC loop τ = 1/(KvKdKI) (level-independent), linear-VGA trap, ripple-pole damping, attack/decay/hang, digital AGC stability with delay, take-over point, SX127x/SX126x/AD9361/RTL gain control, RSSI formulas and statistics, noise blanker, LMS NR/ANF (simulated) | mixed | medium |
| [pa-control-protection-and-sequencing](pa-control-protection-and-sequencing.md) | ALC on a compressing PA, wind-up, ramp spectra (RampTime), coupler-directivity VSWR error, foldback, mismatch dissipation, T/R relay sequencing, GaN bias order, duty-cycle thermal, class D VMCD/CMCD (ngspice), protection-scheme comparison | mixed | medium |
| [duplexers-diplexers-and-crystal-filters](duplexers-diplexers-and-crystal-filters.md) | repeater isolation budget, cavity notch depth vs Qu·Δf/f0, SAW duplexers, crossover vs trap diplexer for 433/915 MHz (optimised, Monte Carlo), 4-pole crystal ladder by k–q/Dishal (C0 narrowing, ngspice check), G3UUR, MCF and ceramic IF filters | mixed | medium |
| [co-site-interference-and-transmitter-intermod](co-site-interference-and-transmitter-intermod.md) | ITU-R M.2244 isolation formulas, reverse IMD 1:1/2:1 and turnaround loss, ETSI 40/70 dB classes, blocking- and TX-noise-limited separation, Golomb-ruler channel plans, on-board 433/920 MHz + Wi-Fi → GNSS products, PIM | mixed | medium |
| [oscillator-phase-noise-ltv-isf](oscillator-phase-noise-ltv-isf.md) | Leeson (Rubiola form) vs tank form (6.02 dB definitional), ISF derivation and stochastic check, Γdc and the 1/f³ corner (ring simulations), cyclostationary NMF, AM–PM in varactor tanks, microphonics, g-sensitivity under GEVS vibration at 433/915/L1/24 GHz | advanced | medium |
| [modulator-and-detector-circuits](modulator-and-detector-circuits.md) | varactor and reactance FM, PM modulator, high-level AM, balanced modulator/SSB (filter, phasing), envelope-detector RC (ngspice), product and synchronous detection under fading, quadrature/Foster–Seeley/ratio/PLL discriminators | mixed | medium |

## Domain FAQ (top questions → page#section)
- *My LNA oscillates on the bench — where do I look?* → [stability: practical notes](amplifier-stability-and-biasing.md#practical-notes)
- *Is K > 1 enough to prove stability?* → [stability: Level 2 (c)–(d)](amplifier-stability-and-biasing.md#level-2--derivations)
- *Can a matching network stabilise a transistor?* → [stability: Level 3 invariants](amplifier-stability-and-biasing.md#level-3--invariants-hidden-instabilities-and-limits-of-the-two-port-view)
- *In what order do I power a GaN HEMT?* → [stability: Example 8](amplifier-stability-and-biasing.md#example-8--gan-hemt-turn-on--turn-off-sequence)
- *Why can't I get minimum NF and good S11 together?* → [LNA: Level 3](lna-design.md#level-3--invariants-limits-and-alternative-topologies)
- *Does my LoRa ground station need an LNA, and where?* → [LNA: Example 5](lna-design.md#example-5--lora-ground-station-is-an-lna-worth-it-and-where)
- *How close can the rocket's 2 W transmitter be to my LNA?* → [LNA: Example 6](lna-design.md#example-6--protect-the-lna-from-your-own-rocket)
- *Why isn't a PA conjugate-matched?* → [PA: Intuition and Level 2 (d)](power-amplifiers.md#level-2--derivations)
- *How much harmonic filtering does a 2 W 433 MHz transmitter need?* → [PA: Example 1](power-amplifiers.md#example-1--a-2-w-433-mhz-pa-with-an-ldmos-transistor)
- *Why can't I build a 1.7 MHz-wide 433 MHz LC filter?* → [filters: Example 1](rf-filters-lc-saw-baw-cavity-microstrip.md#example-1--433-mhz-band-filter-which-technology)
- *Why does my microstrip coupled-line filter pass 2f₀?* → [filters: Level 2 (d)](rf-filters-lc-saw-baw-cavity-microstrip.md#level-2--derivations)
- *Why does a Wilkinson need a resistor?* → [couplers: Level 2 (a)–(b)](couplers-dividers-combiners.md#level-2--derivations)
- *Why is my microstrip coupler's directivity so poor?* → [couplers: Example 6](couplers-dividers-combiners.md#example-6--10-db-and-20-db-microstrip-couplers-why-directivity-is-poor)
- *How do I connect a differential transceiver port to a 50 Ω antenna?* → [baluns: Examples 1–2](baluns-and-rf-transformers.md#worked-examples)
- *Pi/T attenuator values?* → [switches: design equations](rf-switches-attenuators-limiters.md#design-equations--rules-of-thumb)
- *Which spurs will hurt my 433 MHz superhet?* → [mixers: Example 1](mixers.md#example-1--frequency-plan-for-a-43392-mhz-superhet-with-107-mhz-if); [receivers: Level 2 (a)](receiver-architectures.md#level-2--the-numbers-that-set-each-architecture)
- *How much IQ imbalance can I tolerate?* → [mixers: Level 2 (c)](mixers.md#level-2--derivations)
- *How do I design a PLL loop filter and choose the bandwidth?* → [PLL: Level 2 (a), Example 3](vco-and-pll-synthesizers.md#example-3--choosing-the-loop-bandwidth)
- *Why do LoRa chips use low-IF instead of zero-IF?* → [receivers: Level 2 (c)](receiver-architectures.md#level-2--the-numbers-that-set-each-architecture)
- *Why is my log detector reading low on noise-like signals?* → [detectors: Level 2 (e)](detectors-and-power-meters.md#level-2--derivations)
- *Why does multiplying frequency add 20 log N of phase noise?* → [multipliers: Level 2 (e)](frequency-multipliers-dividers.md#level-2)
- *Will an isolator save my PA if the antenna breaks?* → [circulators: Example 1](circulators-isolators.md#example-1--protecting-a-2-w-433-mhz-pa-from-a-broken-antenna)
- *How fast must my AGC be to catch a LoRa preamble?* → [AGC: Level 2 (d), Example 1](agc-loops-and-receiver-gain-control.md#worked-examples)
- *Which gain do I turn down first, LNA or IF?* → [AGC: Level 2 (g)](agc-loops-and-receiver-gain-control.md#level-2--derivations)
- *How do I convert SX1276 PacketRssi/PacketSnr to dBm?* → [AGC: Level 3 RSSI](agc-loops-and-receiver-gain-control.md#level-3--rssi)
- *What ramp time should I set on an SX126x?* → [PA control: Example 2](pa-control-protection-and-sequencing.md#example-2--choosing-sx126x-ramptime)
- *How long must I wait after keying a T/R relay?* → [PA control: Example 5](pa-control-protection-and-sequencing.md#example-5--ground-station-with-a-masthead-lna-and-a-relay-switched-pa)
- *Why is class D rare at UHF?* → [PA control: Level 2 (f)–(g)](pa-control-protection-and-sequencing.md#level-2--derivations)
- *How do I share one antenna between 433 and 915 MHz?* → [duplexers: Level 2 (d)](duplexers-diplexers-and-crystal-filters.md#level-2--derivations)
- *How do I design a crystal ladder filter?* → [duplexers: Example 3](duplexers-diplexers-and-crystal-filters.md#example-3--a-24-khz-ssbdata-if-filter-from-four-10-mhz-crystals)
- *How far away must another team's transmitter be?* → [co-site: Level 2 (d)–(e)](co-site-interference-and-transmitter-intermod.md#level-2--derivations)
- *Which LoRa channels avoid intermod between teams?* → [co-site: Example 5](co-site-interference-and-transmitter-intermod.md#example-5--a-five-team-lora-plan-at-a-competition)
- *Can my ESP32's Wi-Fi jam my GPS?* → [co-site: Example 4](co-site-interference-and-transmitter-intermod.md#example-4--esp32-wi-fi-and-gps-on-one-avionics-bay)
- *Why is the 1/f³ corner lower than the transistor's 1/f corner?* → [ISF: Level 2 (d)](oscillator-phase-noise-ltv-isf.md#level-2--derivations)
- *How much phase noise does rocket vibration add?* → [ISF: Example 3](oscillator-phase-noise-ltv-isf.md#example-3--g-sensitivity-on-a-rocket-what-each-radio-sees)
- *How do I choose R and C for an envelope detector?* → [modulators: Level 2 (f)](modulator-and-detector-circuits.md#level-2--derivations)
- *Which FM detector rejects AM?* → [modulators: Level 2 (h)](modulator-and-detector-circuits.md#level-2--derivations)
- *What does a Wilkinson do with uncorrelated signals or noise?* → [couplers: non-ideal Wilkinson](couplers-dividers-combiners.md#level-3--the-non-ideal-wilkinson-and-incoherent-combining)
- *Besides DPD, how can a PA be linearised?* → [PA: linearisation beyond DPD](power-amplifiers.md#level-3--linearisation-beyond-dpd)
- *How does a superregenerative receiver work, and how far will an FS1000A/XY-MK-5V pair reach?* → [receivers: first-radio receivers](receiver-architectures.md#first-radio-receivers-crystal-sets-superregeneration-and-cheap-ook-modules), [Example 7](receiver-architectures.md#example-7--fs1000a-to-xy-mk-5v-vs-cc1101-how-far)
- *Can I use a satellite-TV LNB or an old dish with my SDR?* → [receivers: LNBs and offset dishes](receiver-architectures.md#satellite-tv-lnbs-offset-dishes-and-l-band-re-feeds), [Examples 8–9](receiver-architectures.md#example-8--an-lnb-on-an-sdr)
- *How do I make a LoRa ground node listen for a year on a battery?* → [receivers: power budget and duty cycling](receiver-architectures.md#receiver-power-budget-duty-cycling-and-lo-radiation), [Example 10](receiver-architectures.md#example-10--a-lora-ground-node-that-listens-for-a-year)
- *How does a Tayloe (N-path) detector work, and should I use 4 or 8 paths?* → [mixers: LPTV and N-path](mixers.md#level-3--lptv-analysis-conversion-matrices-noise-folding-and-n-path-tayloe-mixers), [Example 7](mixers.md#example-7--4-paths-or-8)
- *Which way round does a balun footprint go, and how do I wire an SA612?* → [baluns: practicalities](baluns-and-rf-transformers.md#balun-practicalities-footprints-dots-placement-and-the-sa612)
- *How much common mode does 0.5 dB / 5° of balun imbalance leave?* → [baluns: Level 1½](baluns-and-rf-transformers.md#level-1½--imbalance-as-a-leftover-algebra-only)
- *What is a PLL in plain arithmetic (current per degree, mV per MHz, 20 log N)?* → [PLL: Level 1½](vco-and-pll-synthesizers.md#level-1½--the-loop-as-error--gain--correction-algebra-only)
- *How fast can a PLL hop or chirp, and what limits its loop bandwidth?* → [PLL: Level 3b](vco-and-pll-synthesizers.md#level-3b--pll-dynamics-the-sampling-limit-measuring-the-loop-and-special-architectures), [Example 7](vco-and-pll-synthesizers.md#example-7--hopping-and-chirping-the-adf4351-loop-level-3b-numbers)
- *How do I split one 433 MHz antenna to four receivers?* → [couplers: transformer hybrids and multicouplers](couplers-dividers-combiners.md#level-3--broadband-transformer-hybrids-0180-multi-octave-splitters-and-receiver-multicouplers), [Example 8](couplers-dividers-combiners.md#example-8--a-433-mhz-ground-station-multicoupler-for-four-receivers)
- *How do I build a broadband HF–UHF PA?* → [PA: broadband PAs](power-amplifiers.md#level-3--broadband-pas-resistive-feedback-and-transformer-coupled-push-pull)
- *How do I do load-pull on a budget, and how does PA distortion turn into EVM?* → [PA: PA practice](power-amplifiers.md#level-3--pa-practice-doherty-offset-lines-class-j-diy-load-pull-distortion--evm-thermal-stability-neutralisation)
- *How are cross-coupled filters synthesised, and what are SAW spurious responses?* → [filters: Level 3b](rf-filters-lc-saw-baw-cavity-microstrip.md#level-3b--synthesis-from-polynomials-cameron-extracted-poles-linear-phase-saw-spurious-yig)
- *How do I specify a GNSS preselector that also notches Iridium?* → [filters: Example 7](rf-filters-lc-saw-baw-cavity-microstrip.md#example-7--specifying-a-gnss-preselector-that-also-notches-iridium)
- *Why does a CMOS LNA have induced gate noise, and how wide should the device be?* → [LNA: Level 3b](lna-design.md#level-3b--cmos-lna-noise-induced-gate-noise-power-constrained-width-noise-cancelling)

## Verification scripts (tools/verify/)
| Script | Checks | Runtime |
|---|---|---|
| rfckt_stability.py | K/Δ/μ equivalence (2×10⁵ random 2-ports), μ geometry, circles, ATF-54143 MSG/MAG vs data sheet, stabilisation, via inductance, Rollett invariants, bias arithmetic | ~5 s |
| rfckt_noise2port.py | noise-correlation cascade engine (self-test) — shared helper | <1 s |
| rfckt_atf54143_data.py | ATF-54143 S/noise tables — shared data | — |
| rfckt_lna.py | gain defs, SCM, circles, inductive degeneration, optimised 433/1575 MHz LNAs with Monte Carlo, ground-station NF | ~2.5 min |
| rfckt_pa.py | conduction angle, class F (LP), class E (ODE), Cripps, Doherty, harmonic LPF, DPD | ~2 min |
| rfckt_filters.py | Kuroda, FD Laplace microstrip solver, LPF/BPF in skrf, coupled-resonator extraction, Cohn, coupling matrix, resonator Q | ~8 min |
| rfckt_netsolve.py | nodal S-parameter solver + microstrip formulas — shared helper (self-test) | <1 s |
| rfckt_couplers.py | Wilkinson (3 kinds), branch-line, rat-race, couplers, splitter, combining | <1 s |
| rfckt_baluns.py | lattice, Marchand, Guanella/Ruthroff, LF limit, imbalance | <1 s |
| rfckt_switches.py | switch formulas, SPDT, λ/4 T/R, FET FoM, pads, limiter, PIN R | ~1 s |
| rfckt_mixers.py | switching mixer, spurs, IRR, Gilbert IIP3, APDP, subsampling, IP3 bookkeeping | <1 s |
| rfckt_pll.py | loop filter, noise budget/jitter, lock time, MASH ΣΔ, spurs, DDS, Si5351, Leeson | ~1 s |
| rfckt_rx_tx.py | IF choice, IIP2, flicker, jitter SNR, cascade, reciprocal mixing, IQ modulator, polar, pulling | <1 s |
| rfckt_detectors.py | diode sensitivity, square-law transition, TSS, log amp, waveform errors, temperature | ~1 s |
| rfckt_multipliers.py | harmonic currents, push-push, 20 log N, dividers, prescalers, combs | <1 s |
| rfckt_circulators.py | Polder tensor, Faraday rotation, circulator S-matrix, isolator protection, T/R leakage | <1 s |
| rf2_common.py | shared check/finish helpers and ngspice batch runner | — |
| rf2_isf.py | analytic and impulse-injection ISFs, stochastic vdP phase diffusion, Γdc/1/f³ corner, Leeson/tank forms, AM–PM, Vig vibration, GEVS, isolator, Lorentzian | ~30 s |
| rf2_agc.py | dB vs linear AGC loops, ripple pole, attack/decay, digital AGC with delay, gain policy, RSSI, noise blanker, LMS ALE/ANF | ~3 s |
| rf2_pa_control.py | ALC/wind-up, ramp spectra, directivity, foldback, mismatch stress, sequencing, ngspice class D (VMCD/CMCD), thermal | ~3 s |
| rf2_duplex_xtal.py | crossover vs trap diplexer, cavity notch, repeater budget, crystal ladder (k–q, C0, ngspice), G3UUR | ~3 s |
| rf2_cosite.py | M.2244 isolation, reverse IMD, ETSI classes, desense distances, Golomb plans, on-board GNSS product search | ~2 s |
| rf2_moddet.py | varactor/reactance/PM modulators, DSB/SSB, high-level AM, ngspice envelope detector, coherent/synchronous detection, discriminators, PLL demod | ~2 s |
| rf2_wilkinson_nonideal.py | lossy-arm R_opt, unbalanced/tied loads, incoherent combining, noise correlation, resistor inductance | <1 s |
| rf2_pa_linearisation.py | feedforward, Cartesian feedback, LINC, EER, envelope feedback | ~2 s |
| s14_tayloe.py | N-path sampling mixer: capacitor amplitude, harmonic responses, noise folding (4 vs 8 paths) | ~7 s |
| s14_superregen.py | superregenerative receiver selectivity, quench design law, ENBW and floor, re-radiation | ~7 s |
| s14_rx_budget.py | LNB IF and LO stability, cascade NF, offset-dish geometry, GEO look angles, duty-cycled receiver budget | <1 s |
| s15_pll_dynamics.py | exact tri-state PFD/CP simulation vs Gardner limit, −3 dB vs crossover, two-point modulation, ramp phase error, CP mismatch | ~14 s |
| s15_tlt_splitter.py | ngspice transformer hybrid/splitter: low-frequency limit, leakage compensation, multicoupler | ~3 s |
| s15_pa_practice.py | Doherty drive sweep, class J, load-pull contours, AM/AM-AM/PM → EVM, thermal stability, neutralisation | few s |
| s15_coupling_matrix.py | Cameron polynomial synthesis, folding by Givens pivots, extracted poles, linear-phase pairs | ~3 s |
| s15_cmos_lna.py | induced gate noise (Lee AACD 1998), B_opt, F_min, power-constrained width, noise cancelling | ~1 s |
| s18b_level15_numbers.py | numbers in the Level 1½ rungs of vco-and-pll-synthesizers and baluns (and other domains) | <1 s |

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
Pozar *Microwave Engineering* (ch. 7–13); Gonzalez *Microwave Transistor Amplifiers*; Cripps *RF Power Amplifiers*; Razavi *RF Microelectronics*; Lee *CMOS RF ICs*; Hong & Lancaster *Microstrip Filters*; Matthaei/Young/Jones; Maas *Microwave Mixers*; Banerjee *PLL Performance, Simulation and Design*; Edwards & Sinsky (1992); Hillbrand & Russer (1976); plus data sheets (ATF-54143, AFT05MS003N, SKY66122-11, ADF4351, BGA524N6, PGA-103+, HSMS-285x, Johanson 0433BM15A0001) read in full.

## Known gaps
- W5-E7 pages (AGC, PA control, duplexers/crystal filters, co-site, ISF, modulators) rely partly on search summaries for vendor data (AD9361 AGC, relay timings, SAW/ceramic/cavity duplexer specs); no hardware measurements. SX126x transmitter noise at 0.5–10 MHz offsets, E22/E220 TCXO g-sensitivity and installed antenna isolation on the airframe are unmeasured.
- Large-signal/parametric stability and nonlinear (harmonic-balance) stability analysis only outlined.
- ATF-54143 noise parameters below 2 GHz are vendor-extrapolated; no measured 433 MHz noise parameters.
- Sokal finite-Q class-E equations not obtained; Raab 2001 volume number to confirm.
- HSMS-285x: ideal diode sensitivity (167 mV/µW) vs data sheet (40 mV/µW) gap not fully explained; detector temperature model is low-confidence.
- Vendor spur tables for DBMs, real limiter parts, UHF circulator data sheets, SX126x reference RF networks — belong in domain 18/15.
- Lange coupler and varactor-multiplier design equations not implemented; Fay–Comstock circulator design not implemented.
- Page lengths are 133–277 lines but with long paragraphs (≈ 20–37 kB each); split if future expansion exceeds ≈ 900 lines.
