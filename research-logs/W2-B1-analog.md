# Research log W2-B1: 05-analog-electronics
Status: complete
Owner scope: kb/05-analog-electronics/, research-logs/W2-B1-analog.md, tools/verify/analog_*.py

## Plan
Order chosen so prerequisites come first: devices (diodes → BJT → FET) → topologies → feedback/stability
→ op-amps → low-noise → active filters → oscillators → data converters → power supplies → signal
conditioning → _index/_sources. Each page: 3–6 sources, write own-words, verify in Python, log.

- [x] diodes-schottky-pin-varactor — DONE 289 lines (kb/05-analog-electronics/diodes-schottky-pin-varactor.md) — Shockley eq., VT, Cj(V), Schottky (detectors/mixers, Vf, video resistance), PIN (Rs vs I, τ, switches/limiters), varactor C–V law, tuning ratio, Q; SRD; Zener/TVS capacitance at RF
- [x] bjt-fundamentals-small-signal — DONE — Ebers–Moll, gm=Ic/VT, hybrid-π, rπ, ro (Early), fT, fmax, Miller, bias stability, shot/rb noise, SiGe HBT
- [x] fets-mosfet-jfet-gaas-gan — DONE — square law, velocity saturation, gm/Id, JFET, GaAs MESFET/pHEMT, GaN HEMT, LDMOS, device-selection table, capacitances/fT, negative-gate bias sequencing
- [x] amplifier-topologies — DONE — CE/CS, CB/CG, CC/CD, cascode, diff pair, Darlington, mirrors, feedback amps (4 types), resistive-feedback RF gain blocks (Z0 = sqrt(RF RE)-type relations), Miller & bandwidth (OCTC)
- [x] feedback-and-stability — DONE — loop gain, Bode/Nyquist, PM/GM, dominant pole/lead-lag, capacitive load, emitter-follower VHF oscillation, cures
- [x] op-amps-real-limitations — DONE — GBW, SR/FPBW, en/in, 1/f, Ib/Ios, CMRR/PSRR vs f, output drive, RRIO, CFA, FDA; selection
- [x] low-noise-analog-design — DONE — en–in model, Ropt = en/in, NF of op-amp circuits, resistor excess noise, 1/f, ENBW, preamp design
- [x] active-filters — DONE — Sallen-Key, MFB, state-variable/biquad, tables, sensitivity, GBW needs, anti-alias design; Python verification
- [x] oscillators — DONE — Barkhausen, negative resistance, Colpitts/Clapp/Hartley/Pierce, crystal load caps, gm_crit/margin, VCO, phase-noise basics (Leeson), ring/relaxation
- [x] data-converters-adc-dac — DONE — 6.02N+1.76 derivation, ENOB/SINAD/SFDR, jitter SNR derivation, aliasing, AAF, architectures, DAC sinc, processing gain, drivers/kickback, reference noise; SDR/radar IF
- [x] power-supplies-for-rf-and-analog — DONE — LDO PSRR vs f, LDO noise, SMPS ripple/spurs as sidebands, LC/ferrite post-filter design (damping), ground bounce, sequencing, LoRa 1 A pulses on 1S (droop, brown-out), references
- [x] analog-signal-conditioning — DONE — INAs, bridges, level shifting, ADC front ends, protection (ESD/TVS/clamps), sensor filtering, isolation
- [x] _index.md, _sources.md — DONE

### Verification scripts (planned; tools/verify/)
analog_diodes.py, analog_bjt.py, analog_fet.py, analog_topologies.py, analog_stability.py,
analog_opamp.py, analog_noise.py, analog_active_filters.py, analog_oscillators.py,
analog_data_converters.py, analog_power.py, analog_signal_conditioning.py

## Log (append-only)
- 2026-09-27 — Diodes: WebFetch cannot parse PDFs but saves them; extracted with pdftotext (S1–S4). Wrote tools/verify/analog_diodes.py (VT, tempco, Schottky responsivity derivation + time-domain check, exact Bessel square-law/linear transition, Cj roll-off, PIN RS, switch IL/isolation vs exact S21, varactor tuning, TVS capacitance RL/IL). All formula checks agree.
- 2026-09-27 — Read CONVENTIONS.md, INDEX.md, HANDOFF.md, CLAUDE.md, _TASK_SPECS.md, sample page
  kb/00-math-foundations/decibels-and-log-units.md, Space Bar avionics KB (capabilities, Avionics C, design
  lessons: sensor-rail noise lesson and 1S battery + E220-900T30D radio are relevant examples). Created log.

- 2026-09-27 — Found KiCad-bundled libngspice (/Applications/KiCad/KiCad.app/Contents/Frameworks/libngspice.0.dylib); wrote tools/verify/analog_ngspice.py (ctypes runner). Detector netlist: ngspice 0.809 mV vs hand 0.842 mV. Wrote diodes page (289 lines). Next: BJT page.
- 2026-09-27 — BJT: read BFP740 datasheet (S8), IHP SG13G2 page (S9). Wrote tools/verify/analog_bjt.py (gm table, EM VCEsat closed form vs linear solve, fT hand 473 vs ngspice 477 MHz, fmax hand 70.8 vs Mason U 70.1 GHz, Miller exact, bias beta spread, Fmin/Ropt/IC_opt brute force). BJT page written. Next: FETs.
- 2026-09-27 — FETs: read Mishra GaN overview (S10), CGH40010 (S11), ATF-54143 (S12), BF862 (S13), AO3400A (S14). Wrote tools/verify/analog_fet.py (square law/fT, vsat, EKV gm/ID, JFET gm0 & noise vs BF862, PA power density & Ropt, Johnson limit, OIP3/PDC, RDS(on) fit reproduces 10 V spec, ngspice JFET curve exact). FET page written. Next: amplifier-topologies.
- 2026-09-27 — Topologies: Mini-Circuits AN-60-010 (S15). Wrote tools/verify/analog_topologies.py: sympy gain-block Zin/Av, match RF*RE=Z0^2, S21=1-RF/Z0; ngspice real-transistor block 18.6 dB/S11<-24 dB; OCTC 0.444 vs ngspice 0.445 MHz; IIP3 exp sqrt8 VT, tanh 4VT; NEW derived degeneration law A_IIP3 = sqrt8 VT (1+x)^2/sqrt|1-2x| (two-tone confirms; the common (1+gmRE)^1.5 rule is off by sqrt2 asymptotically and misses the null at x=1/2). Page written. Next: feedback-and-stability.
- 2026-09-27 — Stability: TI SSZT999 read (S16). tools/verify/analog_stability.py (+ TIA Cf sweep: Graeme rule 1.78 pF -> PM 54 deg). Page written. Next: op-amps-real-limitations.
- 2026-09-27 — Op-amps: read OPA333 (S17), MCP6002 (S18), OPA1612 (S19), THS3091 (S20), THS4551 (S21) via pdftotext; ADI MT-034/MT-048 time out (analog.com PDFs unreachable). tools/verify/analog_opamp.py (NG bandwidth, FPBW, SR=4 pi VT GBW, 1/f integral, MCP6002 fc~230 Hz inferred, ENBW, noise & DC budgets, PSRR ripple, CFA vs VFA, FDA Zin sympy, ngspice macro 99.1 kHz). Page written. Next: low-noise-analog-design.
- 2026-09-27 — Low-noise: TI SLVA043B (S22), LIGO T0900200 resistor current noise (S23), Vishay NI via search (S24). tools/verify/analog_noise.py (Ropt/Fmin brute force, correlation, transformer, paralleling, excess noise NI conversion, kT/C, Butterworth ENBW = TI table, TIA noise integration, stage NF with feedback R). Page written. Next: active-filters.
- 2026-09-27 — Active filters: tools/verify/analog_active_filters.py (sympy SK/MFB, scipy design tables, 4th-order Butterworth design & E12 check, Monte Carlo sensitivities incl. equal-component SK failure, finite GBW, SK vs MFB stop-band floor -40 vs -103 dB, AAF order, ngspice section 0.0000 dB). TI SLOA024B/SLOD006B cited (not fetched this session). Page written. Next: oscillators.
- 2026-09-27 — Oscillators: ST AN2867 formulas via search (S25). tools/verify/analog_oscillators.py (Colpitts Zin exact, Pierce gm_crit two ways, pulling 18.9 ppm/pF, drive level, Bessel Gm describing function & amplitude vs margin, Leeson, Wien poles, ngspice Colpitts 8.752 vs 8.765 MHz, VCO tuning noise). Caught & fixed own error: VCO example -123 -> -103 dBc/Hz @10 kHz. Page written. Next: data-converters-adc-dac.
- 2026-09-27 — Data converters: TI SLYT075 (S26), TI ADC3664 datasheet (S27). tools/verify/analog_data_converters.py (quantised sine SNR, ENOB/NSD, jitter MC + ADC3664 implied 232 fs vs 250 fs spec, OSR, 1st/2nd-order 1-bit SD sims 4-9 dB below linear model, ZOH, aliases, kT/C, kickback/settling, ADC NF 26.6 dB, Friis gain plan, ref noise, zone-centred fs=115.71 MSPS for 433.92 MHz). Page written. Next: power-supplies-for-rf-and-analog.
- 2026-09-27 — Power supplies: TI TPS7A20 (S28), AMS1117 via search (S29), EBYTE E22-400T33X manual v1.5 (S30: 850-1200 mA TX, >=5 V for full power). tools/verify/analog_power.py (LDO noise density, buck ripple, PSRR chain, LC damping Cd=4C Rd=Z0 -> +1.1 dB, bead resonance, pushing/AM spurs, 1S constant-power droop, ground IR in LSBs, hold-up C, ground bounce, ngspice LC check). Page written. (Coordinator resume note received mid-page; state verified on disk, no loss.) Next: analog-signal-conditioning, then _index/_sources.
- 2026-09-27 — Signal conditioning: TI INA333 (S31), TI INA180 (S32). tools/verify/analog_signal_conditioning.py (diff-amp CMRR formula vs MC, INA333 RG/offset, bridge exact vs linear, RFI filter CM->DM with/without Cd, divider/SAR settling, clamp current/back-powering, TVS pole, passive level-shift feasibility a+b/Vref<=1, shunt & continuity). Page written. Next: _index.md, _sources.md.
- 2026-09-27 — Wrote _index.md (reading order, page table, 25-question domain FAQ with anchors, gaps) and _sources.md (consolidated bibliography, read vs cited). All 12 analog_*.py scripts run clean; build_index --check: 0 missing template sections; all 05 outbound links point to existing or planned pages. Task complete.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| S1 | Skyworks APN "Design With PIN Diodes" 200312E (2021) | app note | PIN RS=W^2/((mun+mup)Q), f>1300/W^2, CT=eA/W, TFR=tau ln(1+IF/IR), TRF table, switch configs | manufacturer, high |
| S2 | Skyworks "Varactor Diodes" 200824A (2008) | app note | gamma 0.5/0.47, phi 0.7 Si/1.3 GaAs, Q=1/(2pi f Rs C), Q=10 VCO / Q=100 filter fmax rules, TCC, leakage doubling/10C | manufacturer, high |
| S3 | Avago/Broadcom HSMS-285x datasheet | datasheet | SPICE Is=3e-6, n=1.06, Rs=25, Cj0=0.18pF; Rv 8k, 40 mV/uW, TSS -57 dBm @915 MHz; 65 nH match | manufacturer |
| S4 | Avago AN969 Zero-bias Schottky detector | app note | Is sets Rv & sensitivity; ~0.52/(Is+Ib) sensitivity (text garbled in extraction) | manufacturer; extraction partial |
| S5 | Infineon ESD0P2RF (EDN announcement + datasheet listing) | datasheet/news | 0.2 pF RF TVS to 6 GHz | manufacturer |
| S6 | HP AN 918 Pulse & waveform generation with SRDs (hpmemoryproject.org) | app note | SRD snap-off, 100-200 ps pulses | historic manufacturer |
| S8 | Infineon BFP740 datasheet v2.0 | datasheet | fT 44 GHz, CCB .08 pF, VCEO 4/VCBO 13/VEBO 1.2 V, NFmin 0.45 dB @450/900 MHz @6 mA, Gms, OIP3 | manufacturer |
| S9 | IHP SG13G2 SiGe BiCMOS (IHP site, Europractice, IEDM 2010 Heinemann) | manufacturer/peer-reviewed | fT/fmax 300/500 GHz | high |
| S10 | Mishra, Parikh, Wu, Proc IEEE 90(6) 2002 AlGaN/GaN HEMT overview | peer-reviewed | material table, 2DEG density, 6-10 W/mm | high |
| S11 | Wolfspeed/MACOM CGH40010 datasheet | datasheet | VGS(th) -3.8/-3.0/-2.3, VGSQ -2.7, VGS -10/+2, VBR 84, 65% eff | manufacturer |
| S12 | Avago ATF-54143 datasheet | datasheet | E-pHEMT NF .3/.5 dB, OIP3 35.5/36.2, Vth .38, VGS -5/+1 | manufacturer |
| S13 | NXP BF862 datasheet | datasheet | IDSS 10-25 mA, yfs 35-45 mS, Ciss 10p, Crss 1.9p, en .8 nV | manufacturer |
| S14 | AOS AO3400A datasheet (via search summary) | datasheet | RDS(on) 26.5/32/48 mOhm @10/4.5/2.5 V; Vth .9/1.4 | manufacturer |
| S15 | Mini-Circuits AN-60-010 biasing constant-current MMIC amps | app note | Darlington+resistive feedback, Rbias formula, Vd tempco, choke>500 ohm, Vcc>=2Vd | manufacturer |
| S16 | TI SSZT999 (C. Wells 2017) three ways to stabilize cap loads | app note | Riso zero, ROC, DFB, RFx | manufacturer |
| S17 | TI OPA333 datasheet SBOS351E | datasheet | zero-drift specs, Zo 2k, 8 us autozero | manufacturer |
| S18 | Microchip MCP6001/2/4 DS20001733L | datasheet | GP CMOS RRIO specs | manufacturer |
| S19 | TI OPA1612 datasheet | datasheet | 1.1 nV, 1.7 pA/rtHz, 27 V/us, 40 MHz | manufacturer |
| S20 | TI THS3091 datasheet | datasheet | CFA 6000 V/us, 305 MHz G=2, 15 pA/rtHz, RF 1.78k/1.21k | manufacturer |
| S21 | TI THS4551 datasheet SBOS778D | datasheet | FDA 135 MHz, 3.3 nV, HD2/HD3 | manufacturer |
| S22 | TI SLVA043B Noise analysis in op amp circuits (2007) | app note | noise model, ENB table | manufacturer |
| S23 | F. Seifert, LIGO T0900200 resistor current noise | tech report | NI definition, type spread, popcorn | high |
| S24 | Vishay basics / thin film notes (search summary) | app note | thin film < -35 dB, metal film -40 dB | medium (summary only) |
| S25 | ST AN2867 oscillator design guide Rev 24 (search excerpts) | app note | gm_crit, gain margin >=5, DL | manufacturer |
| S26 | TI SLYT075 Clocking high-speed data converters (Bartolome et al. 2005) | app note | jitter SNR derivation | manufacturer |
| S27 | TI ADC3664 datasheet SBAS888B | datasheet | SNR/NSD/SFDR/jitter/FS | manufacturer |
| S28 | TI TPS7A20 datasheet SBVS338H | datasheet | PSRR vs f at 20/300 mA, 7 uVrms | manufacturer |
| S29 | AMS1117 datasheet (search summary) | datasheet | 0.003% Vout noise, 60-75 dB @120 Hz, dropout | medium (summary) |
| S30 | EBYTE E22-400T33X user manual v1.5 | manual | supply 3.3-5.5 V, TX 850-1200 mA, RX 11-15 mA | manufacturer |
| S31 | TI INA333 datasheet SBOS445C | datasheet | G=1+100k/RG, offset, CMRR, ranges | manufacturer |
| S32 | TI INA180 datasheet | datasheet | CSA CM range, gains, offset | manufacturer |
| S7 | Infineon BAR64-02V datasheet (via search listing) | datasheet | rf 2.1 ohm @10 mA 100 MHz, CT 0.13 pF, tau 1.55 us | manufacturer |

## Contradictions / discrepancies found
- Sigma-delta linear-model SQNR formula vs 1-bit simulation: simulated 4-9 dB lower (expected: quantiser gain/overload); noted on data-converter page as upper bound.
- HSMS-285x datasheet writes Rj = 8.33e-5 n T/(Is+Ib); exact k/q = 8.617e-5 V/K gives 3.4% higher Rj (9.08 vs 8.78 kOhm); datasheet typ Rv = 8.0 kOhm. Minor; noted on diode page.
- AN969 sensitivity ~0.52/(Is+Ib) vs own derivation gamma0 = 1/(2(Is+Ib)) = 0.5/(Is+Ib): 4% difference (likely ideality/definition). Noted.
- "Square law up to ~-20 dBm" (AN986, HSMS datasheet) holds for a 50-ohm-terminated detector (Vp=sqrt(2*50*P)); a detector conjugate-matched to its ~9 kOhm video resistance leaves square law ~20 dB lower (~-40 dBm) because of voltage step-up. Derived in analog_diodes.py sec 6. Not a contradiction but a commonly missed condition.
- Mishra 2002 Table 1 gives SiC mu=260, Eg=2.9 (6H polytype) while 4H-SiC (dominant today) is ~3.26 eV, ~900 cm2/Vs (Sze). Noted on FET page; not used in calculations.
- Rule of thumb "IIP3 improves by (1+gm RE)^(3/2)" vs exact ideal-exponential result (1+x)^2/sqrt|1-2x| (asymptotically x^1.5/sqrt2 times... i.e. sqrt2 lower at large x, null at x=0.5). Recorded on topologies page; want a textbook cross-check (Gray-Meyer ch. 5/Razavi RF Microelectronics).

## Knowledge gaps noticed (for later gap-filling)
- Crystal motional parameters on oscillators page are representative, not from a specific 32 MHz datasheet (check SX126x reference crystal).
- Thick-film noise-index values per series (0402/0603) not collected.
- ADI MT-series tutorials unreachable (analog.com timeouts) — cross-checks pending for CFA/noise/ADC content.

## Cross-domain notes (things other domains should cover/link)
- (resolved) decibels page's link to a 14-sdr-dsp data-converters page no longer present; all inbound links to 05 resolve.
- 06-rf-circuits: detectors page should reuse the Schottky responsivity/square-law derivation (05 diodes) and add log/RMS detectors; limiter & PIN switch detail; LNA page should carry frequency-dependent BJT/FET noise (4 noise parameters) — 05 covers only LF Fmin/Ropt; amplifier-stability page: K/mu (05 covers loop-gain view + follower oscillation).
- 07-noise-linearity: phase-noise -> jitter integration (needed by 05 data-converters jitter budget); Leeson/ISF detail; FM-noise from tuning-line noise derivation.
- 13-pcb-rf-layout-emc: RF rectification in op-amps/INAs (EMIRR), PA return-current routing vs sensor grounds, switcher layout spikes; referenced heavily from 05 power/op-amp/signal-conditioning pages.
- 15-lora: E220-900T30D TX current not found (E22-400T33D: 850-1200 mA); crystal vs TCXO tolerance for SX126x at high SF.
- 18-components: part tables for zero-drift op-amps, low-noise LDOs with MHz PSRR, RF TVS, MMIC gain blocks (Vd/Id), SiGe/pHEMT LNAs, SDR ADCs.
- 17-test-measurement: PSRR injection, 0.1-10 Hz noise, crystal measurement without loading (probe pulling).

## Resume instructions (what the next agent should do if this one is interrupted)
- Task complete (2026-09-27). 12 topic pages + _index.md + _sources.md in kb/05-analog-electronics/; 12 verification scripts + ngspice runner in tools/verify/analog_*.py.
- Tooling notes for future edits: WebFetch saves PDFs -> run `pdftotext -layout` on the saved file; ngspice = KiCad's libngspice via tools/verify/analog_ngspice.py (don't combine `.op` with `.ac` in one netlist). analog.com timed out all session.
- Suggested follow-ups (gap-filling wave): fetch ADI MT-001/-003/-007/-034/-047/-048 and Kitchin&Counts to cross-check; measure team battery R_int, MCU ADC ENOB; find igniter no-fire specs; external check of the degeneration IIP3 law.
