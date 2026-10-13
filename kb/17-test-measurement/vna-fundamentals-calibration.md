---
title: VNA fundamentals and calibration — architecture, error models (3-, 8-, 12-term), SOL/SOLT/SOLR/TRL/LRM, cal-kit definitions, port extension, dynamic range and uncertainty
domain: 17-test-measurement
slug: vna-fundamentals-calibration
tags: [vna, calibration, error-model, sol, solt, solr, unknown-thru, trl, lrm, cal-kit, offset-delay, port-extension, de-embedding, dynamic-range, ifbw, uncertainty, directivity, source-match, nanovna, librevna]
prerequisites: [../03-transmission-lines-matching/s-parameters.md, ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md, ../03-transmission-lines-matching/smith-chart.md, ../00-math-foundations/matrices-and-linear-algebra-for-networks.md]
related: [nanovna-librevna-practical.md, fixtures-and-deembedding.md, rf-power-measurement.md, lab-setup-by-budget.md, ../03-transmission-lines-matching/signal-flow-graphs-mason.md, ../03-transmission-lines-matching/time-domain-reflectometry.md, ../03-transmission-lines-matching/coax-and-cables.md, ../08-antennas/antenna-measurement.md, ../06-rf-circuits/couplers-dividers-combiners.md]
level: mixed
confidence: high
last_updated: 2026-10-12
---

# VNA fundamentals and calibration

## Questions this page answers
- What is inside a vector network analyzer and what does "directivity" or "source match" mean for it?
- Why does a VNA need calibration at all, and why exactly three standards for a one-port?
- How do you derive the open-short-load (SOL) calibration equations?
- What are the 12-term and 8-term error models, and which one does my NanoVNA/LibreVNA use?
- SOLT, SOLR (unknown thru), TRL, LRM — which calibration should I use and why?
- What are "offset delay", "C0…C3" and "L0…L3" in a calibration-kit definition, and do they matter below 1 GHz?
- What is the difference between port extension and de-embedding?
- Why does my calibration go bad when I add an SMA-to-U.FL adapter after calibrating?
- How do IF bandwidth and averaging change dynamic range and sweep time?
- How accurate is a return-loss number from a low-cost VNA?
- Is a home-made SOL kit good enough, and how do I characterise it?
- What are ECal and LibreCAL, and can I trust them?
- How do I calibrate when my DUT has a UHF, BNC, MMCX or U.FL connector?
- Should I "calibrate with a 73 Ω resistor" to measure a dipole, or set the VNA to 75 Ω?
- Does my VNA's frequency accuracy matter?

## TL;DR
- A VNA is a stimulus source plus **directional separation** (couplers or resistive bridges) plus **coherent receivers** that measure wave *ratios* (b/a) in magnitude and phase. Everything imperfect between the receivers and the DUT — leakage (directivity), mismatch (source/load match), frequency response (tracking), crosstalk — is modelled as an **error adapter** and removed by calibration [1], [2].
- **One-port = 3 error terms** (directivity e00, source match e11, reflection tracking e10e01). The measured Γ_M is a bilinear (Möbius) map of the true Γ, so **three known standards** (open, short, load) fix it exactly. Closed form (derived below, verified): e00 = Γ_M(load); e11 = (A+B)/(A−B); e10e01 = −2AB/(A−B), with A = Γ_M(open) − e00, B = Γ_M(short) − e00.
- **Two-port = 12-term** (6 forward + 6 reverse; SOLT) or **8-term/7 unknowns** (two error boxes; TRL, LRM, SOLR). SOLR ("unknown thru") needs only a *reciprocal* thru whose delay you know to within ±90° — ideal for non-insertable or different-connector DUTs.
- **TRL** (Engen & Hoer, 1979 [4]) needs no lumped standards: a thru, an unknown-but-equal reflect, and a matched line whose phase differs from the thru by **20–160°** (an 8:1 band per line). It gives the best residual directivity/match (≈ −60 dB in 7 mm coax vs −40 dB for OSL with a fixed load [1]) and is the method of choice on PCB fixtures.
- **Cal-kit definitions matter**: the open is a short line plus fringing C (C0 + C1f + C2f² + C3f³, in 10⁻¹⁵ F, 10⁻²⁷ F/Hz, 10⁻³⁶, 10⁻⁴⁵); the short a line plus L (10⁻¹² H …) [3]. Ignoring a 30 ps offset at 915 MHz turned a 35 − j20 Ω antenna into 41 − j26 Ω in our simulation.
- **Residual directivity ≈ return loss of the load you calibrated with.** A 30 dB load leaves a 20 dB-RL DUT reading anywhere from 17.6 to 23.3 dB. An adapter of VSWR 1.5 added *after* calibration degrades effective directivity to 14 dB [2].
- **Port extension** only removes delay (and optionally a loss) — exact for a matched, uniform pigtail. **De-embedding** removes a full two-port S-matrix, including connector discontinuities.
- **Calibration practice** (Level 3b): a DIY load with 0.5 nH of mounting inductance limits directivity to 37/31/22 dB at 433/915/2450 MHz; characterise DIY open/short (delay + C0 + C1·f) and enter the load as data. A UHF adapter added after an SMA cal leaves only ≈ 19 dB directivity at 433 MHz. "Calibrating with a 73 Ω resistor" is algebraically identical to renormalising to 73 Ω, but needs a standard that does not exist and leaves the Z readout wrong — calibrate at 50 Ω and **renormalise** (`s10_cal_practice.py`).
- **Dynamic range** improves 10 dB per decade of IF-bandwidth reduction (and 10 log N for N vector averages), at the cost of sweep time ∝ 1/IFBW.

## Intuition (no math)
Think of the VNA as a pair of very good ears listening to the waves going toward and coming back from the device. The ears are not perfect: some of the outgoing signal leaks straight into the "reflected" ear (poor **directivity**); the port itself is not a perfect 50 Ω, so a wave bouncing off the DUT partly reflects again off the port and comes back (**source match**); and the cables and mixers have their own frequency response (**tracking**). None of these change from one measurement to the next — they are *systematic*. So you measure a few things whose true answer you already know (a short, an open, a load, a thru), work out what the imperfections must be, and subtract them mathematically from every later measurement. That is calibration.

The catch: the answer is only as good as your knowledge of the standards, the stability of the setup (cables must not move, temperature must not drift), and whether the plane where you calibrated is really where the DUT starts. Random errors — noise, connector repeatability, a cable flexed after calibration — are *not* removed.

## The math

### Level 1 — the one-port 3-term model and SOL calibration
Signal flow graph (Rytting [1]): the "perfect reflectometer" measures a0 (incident) and b0 (reflected); between it and the DUT sits an error two-port with directivity e00, source match e11 and transmission terms e10, e01. With the DUT reflection Γ = b1/a1:

$$a_1 = \frac{e_{10}\,a_0}{1-e_{11}\Gamma},\qquad b_0 = e_{00}a_0 + e_{01}\Gamma a_1\;\Rightarrow\;
\boxed{\Gamma_M=\frac{b_0}{a_0}=e_{00}+\frac{(e_{10}e_{01})\,\Gamma}{1-e_{11}\Gamma}}$$

Only the product e10e01 (reflection tracking) appears, so there are **three** complex unknowns per frequency. The map Γ → Γ_M is bilinear (Möbius): three distinct known points determine it uniquely. Inverting:

$$\Gamma=\frac{\Gamma_M-e_{00}}{(e_{10}e_{01})+e_{11}(\Gamma_M-e_{00})}=\frac{\Gamma_M-e_{00}}{\Gamma_M e_{11}-\Delta_e},\quad \Delta_e=e_{00}e_{11}-e_{10}e_{01}.$$

**SOL closed form (ideal standards Γ_L = 0, Γ_O = +1, Γ_S = −1).** The load gives e00 = Γ_M,L directly. Define A = Γ_M,O − e00 and B = Γ_M,S − e00. Then A(1 − e11) = e10e01 and B(1 + e11) = −e10e01; eliminating e10e01:

$$e_{11}=\frac{A+B}{A-B},\qquad e_{10}e_{01}=A(1-e_{11})=\frac{-2AB}{A-B}.$$

`tools/verify/meas_vna_cal.py` §1 checks this against the general linear solve and scikit-rf's `OnePort` (errors ~10⁻¹⁶).

**General (non-ideal) standards.** Rewrite the model as linear in (e00, e11, Δe): e00 + Γ Γ_M e11 − Γ Δe = Γ_M [1]. Three standards → 3×3 system; more than three → least squares (how "overdetermined" SOL and sliding-load cals work; Copper Mountain describes the matrix form [5]). Real standards are entered via their cal-kit models (Level 3).

### Level 2 — two-port error models

**12-term model (SOLT, 3- or 4-receiver analyzers).** In the forward direction (port 1 driven) there are six terms: directivity E_DF = e00, source match E_SF = e11, reflection tracking E_RF = e10e01, load match E_LF = e22, transmission tracking E_TF = e10e32, isolation (crosstalk) E_XF = e30; six more in reverse [1], [2]. Solving the forward flow graph:

$$S_{11M}=E_{DF}+E_{RF}\frac{S_{11}-E_{LF}\Delta_S}{1-E_{SF}S_{11}-E_{LF}S_{22}+E_{SF}E_{LF}\Delta_S},\quad
S_{21M}=E_{XF}+E_{TF}\frac{S_{21}}{1-E_{SF}S_{11}-E_{LF}S_{22}+E_{SF}E_{LF}\Delta_S}$$

with Δ_S = S11S22 − S12S21. **Correction** requires all four raw measurements. With normalised quantities n11 = (S11M − E_DF)/E_RF, n21 = (S21M − E_XF)/E_TF, n12 = (S12M − E_XR)/E_TR, n22 = (S22M − E_DR)/E_RR:

$$D=(1+n_{11}E_{SF})(1+n_{22}E_{SR})-n_{21}n_{12}E_{LF}E_{LR}$$
$$S_{11}=\frac{n_{11}(1+n_{22}E_{SR})-E_{LF}n_{21}n_{12}}{D},\quad S_{21}=\frac{n_{21}\,[1+n_{22}(E_{SR}-E_{LF})]}{D}$$
$$S_{22}=\frac{n_{22}(1+n_{11}E_{SF})-E_{LR}n_{21}n_{12}}{D},\quad S_{12}=\frac{n_{12}\,[1+n_{11}(E_{SF}-E_{LR})]}{D}$$

(Rytting's slide-20 form [1]; our script §11 reproduces the true S-matrix to 2×10⁻¹⁵ using scikit-rf's 12-term coefficients.)

**SOLT procedure** [1]: (1) SOL on port 1 → E_DF, E_SF, E_RF; (2) loads on both ports → E_XF (skip unless measuring > 60–80 dB isolation — a bad isolation cal adds noise [2]); (3) thru → E_LF = (S11M − e00)/(S11M e11 − Δe) and E_TF = (S21M − E_XF)(1 − E_SF E_LF); repeat in reverse. The thru must be known (usually flush/zero-length, or a defined delay).

**8-term model (two error boxes).** If leakage is negligible and the analyzer measures all four waves on the DUT side of the transfer switch (four receivers), the system is X (port 1) — DUT — Y (port 2). In cascade (T) matrices: T_M = T_X T T_Y. Since only ratios are measured, one term normalises out → **7 unknowns** [1]. Any combination of standards giving ≥ 7 independent conditions works — this is what makes TRL, LRM, LRRM and unknown-thru possible. For a **three-receiver** analyzer, the switch changes the port-2 termination between directions; the "switch terms" Γ_F = a3/b3 (forward) and Γ_R = a0′/b0′ (reverse) convert raw data into the 8-term form, and relate the 12-term and 8-term sets (e.g. E_LF = e22 + e23e32 Γ_F/(1 − e33 Γ_F)) [1]. Without measured switch terms, 8-term cals on a 3-receiver instrument are approximations (Keysight's TRL* assumes equal source and load match [2]).

**The 16-term model** (a full 4-port error adapter, 15 unknowns) adds leakage paths that matter on wafer probes and poorly isolated fixtures; it needs ≥ 5 two-port standards [1].

### Level 2b — the calibration families

| Method | Standards | What must be known | Strengths | Weaknesses |
|---|---|---|---|---|
| **SOL** (1-port) | short, open, load | all three fully | simple, everywhere | load quality sets directivity |
| **Response / normalisation** | thru (and/or short) | the one standard | fast | leaves directivity & match errors (±0.5–1 dB ripple) [2] |
| **Enhanced response** ("1.5-port") | SOL at port 1 + thru | as SOL + thru | corrects source match in S21 | port-2 load match uncorrected [2] |
| **SOLT** (12-term) | SOL on both ports + thru | all, incl. thru | the coax workhorse | thru must be insertable & known |
| **SOLR / unknown thru** [6] | SOL both ports + any **reciprocal** thru | SOL; thru delay to ±90° | non-insertable DUTs, adaptors, fixtures | needs switch terms; sign ambiguity |
| **TRL / LRL** [4] | thru (or line), reflect, line | thru; reflect only its sign; line Z0 defines impedance | best accuracy; standards easy on PCB | 8:1 band per line; long lines at low f |
| **LRM / TRM** | thru/line, reflect, match | match defines Z0 | broadband, compact | match quality → directivity |
| **LRRM** | line, two reflects, one match | match on one port | on-wafer standard | — |
| **ECal** | electronic states | factory data | fast, few operator errors | expensive; transfer standard |

**Why TRL works (Engen & Hoer [4]).** With T-matrices, M_i = X C_i Y for thru (C_T = I), line (C_L = diag(e^{−γl}, e^{+γl}) for a matched line) and reflect. Then M_L M_T⁻¹ = X C_L X⁻¹ — an eigen-problem: X's columns are eigenvectors of the measured matrix, and its eigenvalues are e^{∓γl}. The reflect (same unknown Γ_R on both ports, sign known) fixes the last constant. Two consequences you can check: (a) the line's characteristic impedance *becomes* the reference impedance; (b) the eigenvalues become indistinguishable when e^{−γl} ≈ e^{+γl}, i.e., when the line–thru phase difference approaches 0° or 180°. Keysight's cal-kit rules require the line to stay at least ±20° away from those points [3], giving the 20°–160° window and an 8:1 frequency ratio per line. In our noise simulation (§5), the corrected-S21 error stays within ≈ 1.2× its 90° value across 20–160° but is 2.4× at 5° and 14× at 178°. For wider bands use several lines (multiline TRL, NIST [7]) or a match standard below the lowest line frequency (TRL/LRM hybrid).

**Why unknown thru works (Ferrero & Pisani [6]).** Calibrate each port by SOL (gives e00, e11, e10e01 and e22, e33, e23e32). Connect any reciprocal two-port; since det(T) = 1 for S21 = S12, taking determinants of (e10e32)T_M = A·T·B gives (e10e32)² det T_M = det A det B, so e10e32 = ±√(…) [1]. The sign is chosen from an estimate of the thru's phase — our §6: a 143 ps thru with a flush-thru estimate fails above 1.66 GHz (where the true phase passes 90°); an estimate of 120 ps works across 0–2 GHz.

### Level 3 — calibration-kit definitions and the reference plane
A mechanical standard is modelled as **an offset transmission line + a terminating element** [3]:
- **Offset delay** τ = l√ε_r / c (one-way, seconds). Coax reference plane = outer-conductor mating plane.
- **Offset loss** in GΩ/s: loss per unit length at 1 GHz × propagation speed; the VNA scales it as √f. For coax: αl = (offset loss × τ)/(2 Z_off) × √(f/10⁹) [3].
- **Offset Z0**: lossless impedance of the offset line (50 Ω nominal).
- **Open**: fringing capacitance C(f) = C0 + C1 f + C2 f² + C3 f³ with default scale factors 10⁻¹⁵ F, 10⁻²⁷ F/Hz, 10⁻³⁶ F/Hz², 10⁻⁴⁵ F/Hz³ (all Keysight VNAs use the same scaling [3]). Example: Copper Mountain's T4311 open has τ = 28.353 ps and C0 = −4.3 fF — on a Smith chart it is an arc from 0° to about −132° over 9 kHz–6.5 GHz, **not a dot** [5].
- **Short**: L(f) = L0 + L1 f + L2 f² + L3 f³ (10⁻¹² H, 10⁻²⁴ H/Hz, 10⁻³³, 10⁻⁴²).
- **Load**: usually assumed perfect (Γ = 0); "arbitrary impedance" and data-based loads exist for fixtures. Offset loads need ≥ 20° separation between the two offsets [3].
- **Data-based standards**: each piece individually measured on a reference VNA — better than polynomial models [5].

The open's phase Γ_O = e^{−j2ωτ}(1 − jωC Z0)/(1 + jωC Z0) ≈ e^{−j2ω(τ + CZ0/2)}. At 915 MHz a 50 fF fringing C alone rotates the open by −1.65°, but a 30 ps offset rotates it by −19.8° more. If both the open and short share the same unmodelled offset, the whole calibration plane is shifted by τ: every later Γ is rotated by ≈ +2ωτ. Script §2: for a 35 − j20 Ω antenna at 915 MHz, ignoring (15 ps, 50 fF) gives 37.9 − j23.1 Ω; ignoring (30 ps, 50 fF) gives 41.2 − j25.8 Ω.

### Level 3b — calibration practice: DIY standards, electronic cal, adapters, reference, renormalisation
**DIY standards and their definitions.** A home-made SMA kit is typically an open (a jack with nothing fitted, or a pin cut flush), a short (a disc soldered across the face) and a load (two 0402 100 Ω resistors in parallel from pin to flange). Each is an offset line plus a parasitic, exactly as the Level 3 model above. The load's mounting inductance sets the residual directivity: Γ ≈ jωL/(100 Ω) → with 0.5 nH, **37 / 31 / 26 / 22 dB** at 433 / 915 / 1575 / 2450 MHz (0.3 nH: 42/35/31/27 dB; 1 nH: 31/25/20/16 dB) (`s10_cal_practice.py` §A). Used with *ideal* definitions, a DIY kit with an 18 ps / 45 fF open, 15 pH short and 0.5 nH load leaves |ΔΓ| = 0.027 / 0.059 / 0.10 / 0.16 at those frequencies — a 16 dB-RL antenna at 915 MHz could read anywhere from 13.4 to 20.2 dB (§B).

**Characterising DIY standards against a trusted kit.** Calibrate with a kit whose definitions are known (a commercial kit, a borrowed one, or an electronic calibrator), then measure each DIY standard as a DUT:
1. *Short* → offset delay from the phase slope: ∠(−Γ_S) ≈ −2ωτ (its small inductance is absorbed into τ).
2. *Open* → remove e^{−j2ωτ}, solve C(f) = (1 − Γ′)/(jωZ₀(1 + Γ′)) and fit **C0 + C1·f** only — higher orders are ill-conditioned with noisy data, and a small delay error trades directly into C (in the script a 0.3 ps delay error shifts C0 from 45 to 39 fF while still reproducing Γ_open).
3. *Load* → keep it as **measured data** (a data-based standard) or fit R + jωL.
Entering only the O/S fits halves the error at 2.45 GHz (0.16 → 0.078) because the load then dominates; entering the load as data too brings it to the noise level (< 0.001 in simulation; in practice connector repeatability, ≈ 0.005–0.01) (§B). Rule of thumb: below ~500 MHz an uncharacterised DIY kit is adequate for "is the antenna matched?"; at GNSS and 2.4 GHz characterise it or buy a kit with published definitions.

**Electronic calibration (ECal) and LibreCAL.** An ECal module switches solid-state open/short/load (and thru) states whose S-parameters were measured at the factory against a primary kit; the VNA reads the stored data and solves the error model, which removes most operator errors but makes the module a *transfer standard* whose accuracy is that of its stored coefficients [2], [5]. **LibreCAL** is an open-source 4-port SMA electronic calibrator for 9 kHz–6 GHz (open, short or 50 Ω termination switchable per port), shipped with individually measured factory coefficients stored in the device, with a heater that holds the critical parts at constant temperature; it is driven from the LibreVNA-GUI, its own GUI, buttons or SCPI [14]. Its maintainers note that without valid coefficients it is "nothing more than" a switch matrix — a clone without coefficients is not a calibration kit.

**Calibrating through adapters (UHF, BNC, MMCX, U.FL).** Options, best first: (1) calibrate with standards in the DUT's own connector at the end of the adapter chain; (2) calibrate at SMA and **de-embed a characterised adapter** (measure its S-matrix once, e.g. by two one-port cals — at the SMA face and at the adapter's far face with standards of that connector type — or by unknown-thru); (3) for two-port work, **adapter removal**: two full cals with the adapter moved from one port to the other, from which the VNA computes the adapter [2]; (4) accept the error: the adapter's own return loss becomes the effective directivity. The UHF (PL-259/SO-239) family is not constant-impedance; modelling an adapter as 25 mm of 35 Ω line (illustrative) gives effective directivity **42 / 28 / 19 / 13 dB at 30 / 145 / 433 / 915 MHz** (§D) — harmless at HF, significant at 70 cm. MMCX and U.FL add poor mating repeatability: calibrate at the pigtail end and re-check after re-mating.

**External bridges and couplers.** An external directional element inside the calibrated path (a coupler to measure a high-power amplifier, a resistive bridge with an SA + TG) is corrected by a full vector calibration like the internal one; in a **scalar** set-up (bridge + SA) nothing corrects its directivity, and the reading is bounded by |Γ| ± 10^{−D/20} ([bench recipe R13](bench-measurement-recipes.md)).

**Frequency-reference accuracy.** The VNA's synthesiser error (±10–20 ppm for uncorrected crystals) does not change S-parameters of broadband DUTs: 20 ppm is 8.68 kHz at 433.92 MHz, a 0.32° phase error on 10 m of coax (§E). It matters for **high-Q** devices: a Q = 10 000 resonator at 433.92 MHz (3 dB width 43 kHz) is misplaced by 20 % of its bandwidth — crystals, SAW resonators and cavities need the VNA locked to a 10 MHz reference (LibreVNA has reference in/out [8]).

**Changing the reference impedance — renormalise, don't "calibrate for 73 Ω".** Re-referencing a reflection from 50 Ω to R is the Möbius map Γ′ = (Γ − g)/(1 − gΓ), g = (R − 50)/(R + 50). Calibrating with ideal open and short and a pure resistor R entered as a perfect load *is* that same map (both send R → 0 and keep ±1 fixed; three points fix a Möbius map) — verified to 10⁻¹² (§C). So the "73 Ω cal" is not wrong in algebra; it is a poor practice because (a) no precision 73 Ω standard exists (an SMD/leaded 73 Ω with 0.8 nH and 0.1 pF errs by 0.005 / 0.011 in Γ at 433 / 915 MHz, longer leads much more), (b) the instrument's Z readout still assumes 50 Ω unless the system Z₀ is also changed (a 70 + j5 Ω DUT then reads 47.9 + j3.4 Ω), and (c) nothing physical changes: a 73 Ω dipole on 50 Ω coax still presents VSWR 1.46 to the transmitter. Calibrate with good 50 Ω standards and renormalise in software (`Network.renormalize(73)` in scikit-rf, or the instrument's system-Z₀ setting); for genuine 75 Ω systems use 75 Ω connectors and standards.

**Port extension vs de-embedding.** Port extension moves the reference plane by a pure delay (optionally with a frequency-scaled loss): Γ_DUT = Γ_M e^{+j2ωτ}·10^{2L/20}. It is exact only for a matched, uniform line. De-embedding removes a full two-port: T_DUT = T_fix⁻¹ T_M (see [S-parameters](../03-transmission-lines-matching/s-parameters.md) and [fixtures & de-embedding](fixtures-and-deembedding.md)). Script §7 (100 mm of 1.13 mm micro-coax, v_f = 0.70, 2.5 dB/m at 1 GHz — an illustrative value, ≈ 20 % above the 2.1 dB/m Hirose fit in the [coax table](../03-transmission-lines-matching/coax-and-cables.md) — true antenna 35 − j20 Ω):

| Case | Raw at cable input | PE, delay only | PE, delay + loss | Full de-embed |
|---|---|---|---|---|
| 915 MHz, ideal cable | 53.5 − j28.9 | 35.9 − j19.2 | **35.0 − j20.0** | 35.0 − j20.0 |
| 915 MHz, + 0.15 pF U.FL discontinuity | 52.8 − j30.8 | 34.8 − j19.9 | 33.8 − j20.7 | **35.0 − j20.0** |
| 2450 MHz, + 0.15 pF | 31.6 + j17.6 | 33.5 − j20.3 | 31.8 − j21.6 | **35.0 − j20.0** |

The return-loss *magnitude* barely changes (10.8 vs 10.9 dB) — port extension matters for impedance and matching-network design, not for "is it matched?".

**Dynamic range and noise.** System dynamic range = maximum source power at the DUT − receiver noise floor (both at the test ports, at a stated IF bandwidth); receiver dynamic range = maximum receiver input − noise floor. The noise floor scales as 10 log(IFBW): 10 kHz → 100 Hz lowers it 20 dB but each point then takes ~1/IFBW ≈ 10 ms to settle. N vector (complex) averages lower noise by 10 log N (same effect as dividing IFBW by N); magnitude-only averaging does not lower the floor of a noise-like trace. Examples: LibreVNA specifies 85–105 dB S21 dynamic range at 5–2940 MHz with 0 dBm stimulus and 10 Hz IFBW, 50–60 dB above 2.94 GHz [8]; NanoVNA V2 Plus4 90 dB at 1 GHz with 20 averages [9]; NanoVNA-H4 > 70/60/40 dB in its 50 kHz–300 MHz / 300–900 MHz / 0.9–1.5 GHz bands [10].

**Uncertainty (systematic, worst-case sum).** After a full two-port cal the residuals are effective directivity E_D, source match E_S, load match E_L, tracking E_RT/E_TT and isolation E_I. To first order [2]:

$$\Delta S_{11}\approx E_D+E_S|S_{11}|^2+E_L|S_{21}S_{12}|+E_{RT}|S_{11}|,\qquad
\frac{\Delta S_{21}}{|S_{21}|}\approx\frac{E_I}{|S_{21}|}+E_S|S_{11}|+E_S E_L|S_{21}S_{12}|+E_L|S_{22}|+E_{TT}.$$

Random terms (noise, connector repeatability, cable flex, drift) add RSS on top [1]. Residuals depend mostly on the standards: in 7 mm coax at 18 GHz Rytting lists residual directivity/match of −40/−35 dB for OSL with a fixed load, −52/−41 dB with a sliding load, −60/−60 dB for TRL and −40/−40 dB for TRM [1].

## Design equations & rules of thumb

| Quantity | Relation / value | Notes |
|---|---|---|
| 1-port model | Γ_M = e00 + e10e01 Γ/(1 − e11Γ) | 3 unknowns → 3 standards |
| SOL solution | e00 = Γ_L; e11 = (A+B)/(A−B); e10e01 = −2AB/(A−B) | ideal O/S/L |
| Correction | Γ = (Γ_M − e00)/(e10e01 + e11(Γ_M − e00)) | |
| 8-term unknowns | 7 (ratio measurements) | needs 4 receivers or switch terms |
| TRL line phase | 20° ≤ \|φ_line − φ_thru\| ≤ 160° | one line covers 8:1 |
| λ/4 TRL line at centre | l = c/(4 f_c √ε_eff) | on FR-4 microstrip ε_eff ≈ 3.2–3.4 |
| Unknown thru | delay estimate within ±90° | sign of √ |
| Residual directivity | ≈ Γ of the load used | 30 dB load → −30 dB |
| Adapter after cal | effective directivity ≈ −20 log Γ_adapter | VSWR 1.5 → 14 dB, 1.1 → 26 dB, 1.05 → 32 dB |
| Noise floor vs IFBW | ΔN = 10 log(IFBW₂/IFBW₁) | time/point ≈ 1/IFBW |
| Vector averaging | −10 log N | |
| Offset delay | τ = l√ε_r/c | 10 mm PTFE (ε_r 2.1) ≈ 48 ps |
| DIY load directivity | ≈ −20 log(ωL/100 Ω) | 0.5 nH: 37 dB @ 433 MHz, 31 dB @ 915 MHz |
| Renormalise to R | Γ′ = (Γ − g)/(1 − gΓ), g = (R − 50)/(R + 50) | exact; 73 Ω dipole on 50 Ω: VSWR 1.46 regardless |
| Reference error | Δf = f·ppm; Δφ = 360° Δf τ_rt | 20 ppm: 8.7 kHz @ 434 MHz, 0.3° on 10 m coax |

## Worked examples

**Example 1 — SOL by hand (one frequency).** Raw readings at 915 MHz: load Γ_M,L = 0.035 + 0.032j, open Γ_M,O = −0.52 − 0.60j, short Γ_M,S = 0.58 + 0.55j. Then e00 = 0.035 + 0.032j; A = −0.555 − 0.632j; B = 0.545 + 0.518j; A − B = −1.100 − 1.150j; A + B = −0.010 − 0.114j → e11 = (A+B)/(A−B) = 0.0561 + 0.0450j (|e11| = 0.072, raw source match −22.9 dB). e10e01 = −2AB/(A−B) = −0.552 − 0.572j (|e10e01| = 0.795, −2.0 dB of reflection tracking). A DUT reading Γ_M = 0.20 − 0.30j corrects via Γ = (Γ_M − e00)/(e10e01 + e11(Γ_M − e00)) = 0.172 + 0.439j (|Γ| = 0.471, Z = 44.3 + j50.0 Ω) — note how different that is from the raw reading, mostly because of the −134° tracking phase of the cable. Do this in Python rather than by hand — the point is that each frequency is an independent 3-unknown problem.

**Example 2 — does my cheap load limit me?** Measuring a 915 MHz antenna whose true RL is 20 dB. Script §3: with a 40 dB load the reading is 19.2–20.9 dB; with a 30 dB load 17.6–23.3 dB; with a 20 dB load anything from 13.9 dB to "perfect". Rule: your load must be ≥ 10 dB better than the RL you want to resolve.

**Example 3 — the SMA-to-U.FL adapter added after calibration.** Calibrate at the SMA end of the cable, then add an SMA-F to U.FL adapter + 10 cm pigtail (VSWR say 1.2 at 2.4 GHz). Effective directivity drops to ≈ 21 dB; a 15 dB-RL antenna can read ~10–30 dB depending on phase (script §12 shows the VSWR 1.5 case: a 10 dB RL reads 5.3–21 dB). Fix: calibrate *at the end of the pigtail* (U.FL cal kit, e.g. MegiQ's [11]) or de-embed a characterised pigtail.

**Example 4 — reproduce a textbook uncertainty budget.** AN 1287-3's filter example (8753D, type-N; E_D = 47 dB, E_S = 36 dB, E_L = 47 dB, tracking 0.019/0.026 dB; DUT 1 dB loss, 16 dB RL): ΔS11 = 0.0088 → the 16 dB RL reads 15.53–16.49 dB, and S21 = 1 dB ± 0.054 dB. The app note prints +0.53/−0.44 dB for the reflection; our recomputation of its own numbers gives −0.47/+0.49 dB (minor arithmetic/rounding difference) [2]; S21 agrees.

**Example 5 — filter S21 on a 1.5-port VNA (NanoVNA).** Only S11 and S21 are measured; the CH1 (receive) port's match is not corrected. If CH1 has RL 15 dB and the SAW filter's output RL is 10 dB, S21 has ±0.5 dB ripple; a 10 dB pad on CH1 (after calibration includes it in the thru) cuts this to ±0.07 dB at the cost of 10 dB dynamic range (script §13). For S22/S12, turn the DUT around.

**Example 6 — TRL line for a JLCPCB fixture at 2.4 GHz.** 50 Ω microstrip on 1.6 mm FR-4, ε_eff ≈ 3.3: λ/4 at f_c = 2.4 GHz → l = 3×10⁸/(4 × 2.4×10⁹ × √3.3) = 17.2 mm longer than the thru. Usable 20–160° band: 0.53–4.3 GHz (ratio 8). For 433 and 915 MHz as well, add a second line (~96 mm at f_c = 0.43 GHz) or use LRM with 0402 100 Ω ∥ 100 Ω loads. Design details in [fixtures & de-embedding](fixtures-and-deembedding.md).

## Practical notes
- **Calibrate where you measure, with the cables you measure with.** Every adapter, cable flex or connector re-seat after cal is an uncorrected error. Tighten SMA to 0.9 N·m (8 in·lb) with a torque wrench; mate straight; never rotate the centre pin.
- **Verify every calibration**: re-measure the load (should read RL ≥ 40 dB on a good kit), the short/open (|Γ| ≈ 0 dB, phase following the kit model), and a "verification" item never used in the cal (an attenuator or a mismatched load/airline). A 20 dB SMA attenuator terminated in a load should read S11 ≈ −40 dB-ish and S21 = −20.0 ± 0.1 dB.
- **Frequency grid**: calibrate over exactly the span and points you will use; interpolated calibrations (NanoVNA-Saver, LibreVNA) are fine for smooth error terms but degrade with long cables (fast phase wrap between points). Keep point spacing below ~1/(10 × round-trip delay of the cable).
- **Power level**: keep the stimulus well below the DUT's compression (amplifiers! use −20 dBm or lower for LNAs) and the receiver's compression; high-gain amplifier S21 needs an input pad or reduced power.
- **Isolation cal**: skip it unless you really measure > 60–80 dB isolation; a noisy isolation cal injects its noise into every later S21 [2].
- **Drift**: cheap VNAs (NanoVNA V1 family) drift with temperature; recal after warm-up (10–20 min) and when the room changes. NanoRFE claims its V2 Plus4 holds calibration for > 3 months vs < 30 min for other low-cost VNAs (vendor claim) [9].
- **Architecture notes for low-cost VNAs**: NanoVNA-H/H4 generate stimulus and LO with an Si5351 clock chip whose square-wave odd harmonics are used above ~300 MHz (so dynamic range falls to ~40 dB by 1.5 GHz) [10], [12]; LibreVNA uses a MAX2871 synthesiser above 25 MHz, resistive return-loss bridges instead of couplers, two independent receivers (1st IF 60 MHz, 2nd IF 250 kHz, 16-bit ADC at 800 kS/s) and a digital step attenuator (−40…0 dBm) [8]. Both are "1.5-port" or switched 2-port designs — check whether your firmware/software measures switch terms before trusting 8-term cals.
- **Resistive bridge vs coupler**: bridges are broadband to DC-ish frequencies (good for 50 kHz–6 GHz VNAs) but cost ~6 dB each way and have finite directivity; couplers are lower loss but band-limited at low frequency. After calibration, raw directivity matters mainly for drift sensitivity [2].

## Common mistakes & misconceptions
- **"The open should be a dot at the right edge after calibration."** Only if the kit is defined as ideal. A real open is a short line + fringing C and traces an arc clockwise with frequency [5]; if you *measure your own open* after a cal done with an ideal-open definition, it will look like a perfect dot — that proves nothing.
- **"Calibration removes the cable."** It removes the cable *as it was during calibration*. Flexing a cheap cable after cal can move phase by degrees at 2 GHz.
- **"TRL is always best."** Only within its 8:1 line band and only if the line is uniform and the fixture repeatable; outside the band it is ill-conditioned (§5).
- **"Unknown thru means I know nothing about the thru."** You need it reciprocal and its delay to within ±90° (§6).
- **"Port extension = de-embedding."** Port extension is a delay (+ loss); it cannot remove the capacitance of a U.FL mated pair or a pad (§7).
- **"More averaging always helps."** Averaging lowers noise, not systematic error; averaging a drifting system averages the drift.
- **"The 12-term and 8-term models are different physics."** They describe the same hardware; 8-term + switch terms ↔ 12-term (with a constraint that reduces it to 10 independent terms) [1].
- **"Calibrate with a 73 Ω resistor so the dipole reads 1:1."** With ideal open/short this reproduces renormalisation exactly — but your resistor is not a 73 Ω standard, the Z readout is still 50 Ω-referenced, and the cable and transmitter still see VSWR 1.46. Calibrate at 50 Ω and renormalise in software.
- **"My home-made kit is fine because the load reads 45 dB after calibration."** A standard measured on the calibration it defined always looks perfect; verify with an item not used in the calibration.
- **"An ECal/LibreCAL is automatically accurate."** It is a transfer standard: only its stored coefficients make it one.
- **"A VNA measures power."** It measures *ratios*. Absolute power accuracy of the stimulus (±2 dB on low-cost units) does not affect S-parameters unless it drives the DUT into compression.

## How to simulate / verify
- `python3 tools/verify/meas_vna_cal.py` — (1) SOL closed form vs linear solve vs scikit-rf OnePort; (2) cal-kit offset/fringing C ignored; (3) imperfect load → residual directivity; (4) SOLT exact recovery with random error boxes; (5) TRL and its 20–160° noise sensitivity; (6) unknown-thru root-choice failure and fix; (7) port extension vs de-embedding at 915 MHz/2.45 GHz; (8) adapter directivity; (9) AN 1287-3 budget recomputed; (10) IFBW/averaging; (11) explicit 12-term correction formula; (12) reflection uncertainty for good/cheap kits; (13) 1.5-port S21 ripple and the pad fix.
- `python3 tools/verify/s10_cal_practice.py` — (A) DIY-load residual directivity vs frequency; (B) characterising DIY open/short against a trusted kit and the resulting DUT error (ideal vs fitted vs data-based load); (C) 73 Ω-load cal ≡ renormalisation, parasitic-standard error, wrong Z readout; (D) UHF adapter effective directivity; (E) frequency-reference effects. ALL PASS.
- scikit-rf `skrf.calibration` implements OnePort, SOLT, TwelveTerm, EightTerm, TRL, NISTMultilineTRL, UnknownThru, LRM, LRRM, TwoPortOnePath (1.5-port) — you can calibrate raw NanoVNA/LibreVNA data offline and compare methods. Caution learned while writing the script: `media.line(..., z0=65)` in scikit-rf 2.x returns a network whose *port* impedance is 65 Ω; to build a mismatched line in a 50 Ω system use `DefinedGammaZ0(freq, z0_port=50, z0=65).line(...)`.

## Open questions / gaps
- Cal-kit definitions (offset delay, C0) of the cheap SMA SOL kits shipped with NanoVNAs are not published; community measurements exist but were not verified here (see [NanoVNA practical](nanovna-librevna-practical.md)). The characterisation procedure is now in Level 3b, but no team measurement of a shipped kit exists yet; the UHF-adapter model (25 mm of 35 Ω) and the DIY-standard parasitics there are illustrative.
- The CH1 (receive-port) match of NanoVNA-H/H4 is not specified by the vendor; the 15 dB used in Example 5 is an assumption.
- Engen & Hoer [4] and Ferrero & Pisani [6] were used through Rytting's [1] and Keysight's [3] summaries, not read in the original.

## Sources
1. D. Rytting, "Network Analyzer Error Models and Calibration Methods," Agilent/ARFTG seminar slides (c. 1998–2003), mirror at emlab.uiuc.edu/ece451/appnotes/Rytting_NAModels.pdf — 1-port bilinear model and linear form, 12-term equations and SOLT steps, 16-term and 8-term (T-matrix) models, calibration families (TRL/LRM/TXYZ/UXYZ), switch terms, residual-error table, unknown-thru determinant. (app note / seminar; read)
2. Agilent AN 1287-3, "Applying Error Correction to Network Analyzer Measurements," 5965-7709E, 2002 — response/enhanced-response/full-two-port calibration, adapter effect on directivity, uncertainty examples, TRL vs TRL*, non-insertable devices. (app note; read)
3. Keysight AN 5989-4840, "Specifying Calibration Standards and Kits for Keysight Vector Network Analyzers" — offset delay/loss/Z0, open/short polynomial models and units, load types, offset-load 20° rule, TRL class table (line ±20° from thru). (app note; read)
4. G. F. Engen and C. A. Hoer, "Thru-Reflect-Line: An Improved Technique for Calibrating the Dual Six-Port Automatic Network Analyzer," *IEEE Trans. MTT* 27(12), pp. 987–993, Dec. 1979. (peer-reviewed; cited via [1], [3])
5. B. Walker (Copper Mountain Technologies), "VNA Master Class — VNA Calibration, Kits, Error Terms and Calculation," 2020 handout — open/short models with T4311 example, SOLR recommendation, data-based standards, least-squares 1-port. (vendor seminar; read)
6. A. Ferrero and U. Pisani, "Two-Port Network Analyzer Calibration Using an Unknown 'Thru'," *IEEE Microwave and Guided Wave Letters* 2(12), pp. 505–507, 1992. (peer-reviewed; cited via [1], [5])
7. R. B. Marks, "A Multiline Method of Network Analyzer Calibration," *IEEE Trans. MTT* 39(7), pp. 1205–1215, 1991. (peer-reviewed; cited)
8. J. Käsemann (jankae), LibreVNA README and "LibreVNA Preliminary Specifications" (specsheet.pdf), github.com/jankae/LibreVNA, accessed 2026-09-27. (open-source vendor docs; read)
9. NanoRFE, "NanoVNA V2" product page, nanorfe.com/nanovna-v2.html, accessed 2026-09-27 — frequency ranges, dynamic range, S11 noise floor, drift claim. (vendor; read)
10. nanovna.com (Hugen) and github.com/hugen79/NanoVNA-H README; retailer spec tables for NanoVNA-H4 dynamic range — Si5351 odd-harmonic operation, 70/60/40 dB bands. (vendor/community; read)
11. MegiQ, "Balanced and UFL Calibration Kit" user guide V3 (megiq.com). (vendor; cited from search listing)
12. J. Dunsmore, *Handbook of Microwave Component Measurements*, 2nd ed., Wiley, 2020 — ch. 2–3 (VNA architecture, calibration, uncertainty). (textbook; cited)
13. This repository: `tools/verify/meas_vna_cal.py`, `tools/verify/s10_cal_practice.py`. (verification)
14. J. Käsemann (jankae), LibreCAL README, github.com/jankae/LibreCAL, accessed 2026-10-12 — 4-port SMA eCal 9 kHz–6 GHz, open/short/50 Ω per port, individually measured factory coefficients stored on the device (downloadable by serial), temperature-controlled, LibreVNA-GUI/SCPI control. (open-source vendor docs; WebFetch summary)
