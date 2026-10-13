---
title: Validation test campaign — a pre-registered bench, field and HIL programme that turns the KB's predictions into measurements (antennas, transmit, receive, link, rocket-specific, materials/PCB, environment)
domain: 20-projects-recipes
slug: validation-test-campaign
tags: [validation, test-campaign, pre-registration, acceptance-band, uncertainty-budget, gum, decision-rule, guarded-acceptance, nanovna, litevna, tinysa, rtl-sdr, hackrf, step-attenuator, per-waterfall, ring-resonator, tdr, impedance-coupon, via-fence, doppler-rate, hil, gps-sdr-sim, hero, e-match, harmonics, e22-400t33d, e220-900t30d, noise-floor, spectrum-survey, record-everything, measured-results]
prerequisites:
  - design-review-checklists.md
  - lora-rocket-telemetry-link.md
  - ../17-test-measurement/rf-bring-up-debug-playbook.md
  - ../17-test-measurement/bench-measurement-recipes.md
  - ../17-test-measurement/lab-setup-by-budget.md
related:
  - ground-station-tracking-yagi.md
  - patch-antenna-design-walkthrough.md
  - bandpass-filter-design-walkthrough.md
  - gnss-front-end-design.md
  - lna-design-walkthrough.md
  - sdr-receiver-build.md
  - beginner-project-ladder.md
  - ../17-test-measurement/noise-figure-measurement.md
  - ../17-test-measurement/antenna-range-ota-testing.md
  - ../17-test-measurement/spectrum-analyzers.md
  - ../17-test-measurement/nanovna-librevna-practical.md
  - ../17-test-measurement/sdr-as-test-equipment.md
  - ../17-test-measurement/interference-hunting-and-rf-immunity.md
  - ../16-simulation-tools/simulation-validation.md
  - ../19-regulations-safety/singapore-imda-rules.md
  - ../19-regulations-safety/lab-safety-esd-high-power.md
level: mixed
confidence: medium
last_updated: 2026-10-14
---

# Validation test campaign — pre-registered measurements for the whole KB

Every number on this page comes from `python3 tools/verify/f2_campaign_predictions.py` (28/28 checks pass; output in
`tools/verify/f2_campaign_predictions_output.txt`), unless another script or page is named. The script recomputes the
KB's own predictions and checks that they match the pages quoted here. It also derives the uncertainty budgets and
acceptance bands. With `--schema` it prints the results-record format, and `--validate FILE.csv` checks a results file.

## Questions this page answers
- How do we test the KB's predictions with a NanoVNA, a tinySA, SDRs and our own flight hardware?
- Which tests should we run first to learn the most for the least money and time?
- What exactly counts as a pass, a fail, or "the test could not tell"?
- How wide should the acceptance band be, and how do I combine the prediction's and the measurement's uncertainty?
- How do I record a measurement so that someone else can trust it, or redo it, a year later?
- Where do measured values go in the KB, and how do I mark a prediction confirmed or refuted?
- Which of these tests are legal in Singapore as described, and which need a shielded enclosure, conducted set-up or licence?
- How can a 10 mW legal test say anything about a 2 W flight?
- How do I find out which SF/BW the EBYTE "2.4k" air rate really is?
- How do I measure FR-4 εr myself before trusting a patch-antenna simulation?

## TL;DR
- **40 tests in 9 groups.** C: calibration prerequisites (5). A: antennas (6). T: transmit (6). R: receive (5). L: link (3).
  K: rocket-specific (6). M: materials/PCB (3). E: environment (2). F: flight scoring (4). Every test has a written
  prediction, an acceptance band, a method page, an equipment list, a decision rule, and a note on what a miss means.
  They map onto the gap register's "needs real-world data" rows R01–R25 (table in §Sequencing).
- **Rules, from the team's engineering ethos.** Pre-register in a write-once file before measuring. Record raw data,
  calibration state and the config line. Report every outcome, misses first. A miss is information, not a failure to
  hide. Uncertainty travels with every number.
- **Decision rule.** The band is B = √(U_pred² + U_meas²), at k = 2. The outcome is **CONFIRMED** if |m − p| ≤ B and the
  measurement can tell the KB claim from its nearest competitor (U_meas ≤ separation/2). It is **REFUTED** if
  |m − p| > B. It is **INCONCLUSIVE** if the measurement was too coarse, and **VOID** if a validity check failed. Use
  **MEASURED** for unknowns where the KB makes no prediction. Regulatory and safety limits use guarded acceptance:
  PASS only if m + U ≤ limit.
- **Cheap tests that settle a lot.** The EBYTE air rate is identified by occupied bandwidth, not symbol time: all three
  "2.4k" candidates have T_s = 4.096 ms. Module power and current vs setting and supply. Harmonics (69/63 dBc needed at
  33 dBm; 46.5/40.5 dBc for the 10 mW test set-up). A conducted PER waterfall: 5 steps × 300 packets fixes the
  1 % point to ±0.06 dB statistically, and ±0.48 dB in total once level calibration is included. That is enough to
  tell an EBYTE module with an LNA (NF ≈ 3 dB) from a bare chip (NF 6 dB).
- **Some tests only work in a set order.** The 2.45 GHz FR-4 patch can tell the TL model from openEMS (2.2 % apart)
  only if εr is measured first. With εr unknown (±0.2) the prediction band is ±2.3 %. With a ring-resonator εr
  (U ≈ ±0.05) it shrinks to ±0.85 %. NF tests need the cheap noise source's ENR calibrated first, because the ENR
  error passes 1:1 into NF.
- **Legal and physics traps written into the plan.**
  - Never radiate test signals in GNSS bands. The patch axial-ratio test needs a shielded/absorber enclosure with
    reflections below −30 dB (a −20 dB stray wave gives ±1.7 dB of AR error).
  - 905 MHz is not a Singapore SRD band.
  - A 10 mW test scales to flight power as √P for pyro-lead current (×13.3) but as P for sensor RF rectification
    (×178). So the sensor test needs flight power under a permit, or a screened room.
- **New, falsifiable F2 estimate (low confidence).** A quasi-static bracket gives an antenna on the tube axis
  detuning by only 1–3 %. A wire taped to the fibreglass wall detunes several times more (bracket 15–27 %, probably
  high). The KB says only "a few percent". Test A2 decides this.
- **Simulation-informed predictions now exist for A2 (openEMS, W5-S11, 2026-10-13; still to be measured).** A λ/4 whip
  on the axis of a 3 mm G10 ogive over a 100 mm bulkhead: **−1.2 % at 915 MHz, −2.8 % at 433 MHz**; a conductive
  av-bay counterpoise **+3.4 %**; a printed IFA in a fibreglass tube **+0.7 %** (the opposite sign to its
  pre-registration) ([openEMS workflow Runs 3, 4c](../16-simulation-tools/openems-workflow.md)). A 3-element hand-held Yagi is predicted at
  **≈ 8.5 dBi** when fed directly from 50 Ω (NEC; [NEC modelling Example 4](../16-simulation-tools/nec-antenna-modelling.md)), not 9 dBi.

## Intuition (no math)
A prediction that has never met a measurement is a hypothesis. The campaign is how the KB earns its confidence
labels. It follows a fixed order. First, write down what you expect and how far off you will tolerate, before
touching the hardware. Next, check the measuring chain itself against something known (pads, power sensor, noise
source, frequency reference). Then measure one variable at a time and record everything needed to repeat the run.
Finally, score the result against the number you wrote down, not against the number you would have liked. A miss
is the useful outcome: it points at the assumption nobody had measured. Writing the band in advance stops the
quiet widening of tolerances after a disappointing result. Asking "could this test even tell the two explanations
apart?" stops a lucky result being called a confirmation.

The rules come from the team's own **engineering ethos**. That is a note in Marcus's Space Bar avionics knowledge
base (kept outside this repository, alongside the HIL and bench-testing methods note). It sets ten ordered tenets:
validate against independent truth, never against yourself; fix pass criteria before looking; research and test
rather than trust memory; measure before narrating a mechanism; the root cause is usually a premise nobody measured;
one variable per test; uncertainty travels with every number; record everything in files immediately; report
faithfully; and tools manage themselves while people review and decide. Its bench-testing companion adds the
hardware habits used below:
- capture from reset;
- grep every warning, then check what is *missing*;
- count drops as well as losses;
- compute loss rates against the end-of-run frame count;
- never test on `main`;
- run repeated battery power-ups.

## The math — uncertainty budgets and acceptance bands

### Level 1 — the rules every test uses
- **Standard uncertainties (GUM).** Convert each component to a standard uncertainty u:
  - rectangular limits ±a → u = a/√3;
  - U-shaped (mismatch) limits ±a → u = a/√2;
  - a certificate with coverage k → u = U/k.

  Then u_c = √(Σuᵢ²) and U = 2u_c (≈ 95 %). The same rules are used in the [bench recipes](../17-test-measurement/bench-measurement-recipes.md).
- **Acceptance band** (two-sided, pre-registered): $B=\sqrt{U_{pred}^2+U_{meas}^2}$. U_pred comes from the KB
  (tolerance on the prediction). U_meas comes from the measurement budget written for this test.
- **Discrimination.** If two hypotheses (H₀ = the KB prediction, H₁ = its nearest rival) are a distance D apart, the
  test can decide between them only if $U_{meas}\le D/2$. Write D down in the pre-registration.
- **Outcomes:**
  - CONFIRMED: |m − p| ≤ B and U_meas ≤ D/2.
  - REFUTED: |m − p| > B.
  - INCONCLUSIVE: inside B but U_meas > D/2.
  - VOID: a validity check failed (for example the leakage check). The data are kept, but not scored.
  - MEASURED: no KB prediction existed; the measurement fills a gap.
- **Guarded acceptance for limits** (regulatory or safety, upper limit L):
  - PASS if m + U ≤ L;
  - FAIL if m − U > L;
  - otherwise INDETERMINATE (re-measure with a better instrument).

  Example: a tinySA (±1.5 dB) reading of −37.0 dBm against −36 dBm is INDETERMINATE; −40.0 dBm is PASS (script S0).

### Level 2 — derivations used by specific tests
**PER waterfall precision (R1).** Model the packet error rate as $PER(P;S_0)$, where S₀ is the 1 % point and the
curve shape is the ideal LoRa shape $1-(1-SER)^{N_{sym}}$ (from `lora_css_sim.py`). With n packets at each of
several levels $P_j$, the Fisher information on S₀ is
$$I(S_0)=\sum_j\frac{n\,(\partial PER/\partial S_0)^2}{PER_j(1-PER_j)},\qquad\sigma(S_0)\ge 1/\sqrt{I}.$$
For SF7 with a 64-byte payload the 1 % point is at SNR −6.86 dB (ideal) and the slope there is 2.9 % per dB. Five
steps at +1, +0.5, 0, −0.5, −1 dB give these spreads:

| Packets per step | σ(S₀), shape known | σ(S₀), slope also fitted |
|---|---|---|
| 100 | 0.105 dB | ≈ 0.15 dB |
| 300 | 0.061 dB | ≈ 0.09 dB |
| 1000 | 0.033 dB | ≈ 0.05 dB |

Fitting a waterfall is therefore far more efficient than counting ≈ 1 500 packets at one level. (That rule, from
[noise-figure measurement](../17-test-measurement/noise-figure-measurement.md), resolves 1 % ± 0.5 % at a single
point.) The limit is the absolute level:
- source power via a power sensor: ±0.33 dB;
- step attenuator, VNA-calibrated: ±0.2 dB;
- two pads: ±0.1 dB each;
- mismatch: ±0.1 dB (U-shaped).

Those combine to U = ±0.43 dB; with the fit, **U_R1 = ±0.48 dB (k = 2)**.

**Stray reflections and axial ratio (A4).** In the rotating-linear-source method, AR = P_max/P_min. A stray wave of
relative amplitude ρ can move each reading by up to 20 log(1 ± ρ):

| Stray wave | AR error, up to |
|---|---|
| −15 dB | ±3.1 dB |
| −20 dB | ±1.7 dB |
| −25 dB | ±1.0 dB |
| −30 dB | ±0.55 dB |
| −35 dB | ±0.31 dB |

To test "AR ≤ 1.5 dB" the enclosure must keep strays at or below −30 dB.

**Attenuation and range (L1).** In free space $d_{eq}=d\,10^{A/20}$, so an attenuation error δA becomes a range error
of $10^{\delta A/20}-1$:

| δA | Range error |
|---|---|
| 0.5 dB | +6 % / −6 % |
| 1 dB | +12 % / −11 % |
| 2 dB | +26 % / −21 % |
| 3 dB | +41 % / −29 % |

**Ring resonator → εr (M1).** Resonances follow $f_n=n\,c/(2\pi r\sqrt{\varepsilon_{eff}(f_n)})$, with ε_eff from
Hammerstad–Jensen plus Kirschning–Jansen dispersion (`rfcalc.tline.microstrip_kj`). The script inverts this by
bisection. A Monte Carlo over these inputs:
- thickness measured with a micrometer: σ 15 µm;
- width measured under a microscope: σ 10 µm;
- radius: σ 10 µm;
- peak frequency: 0.05 % at k = 2;
- unknown coupling-gap loading: uniform 0–0.3 % low;
- ε_eff model form: 0.5 %.

It gives **U(εr) ≈ ±0.05 (k = 2)** for modes 2 and 3. Using the wrong h (1.43 or 1.60 mm analysed as 1.51 mm) shifts
εr by only ±0.02, because ε_eff depends weakly on W/h here.

**Patch prediction transported to the measured εr (A3).** The openEMS result (2.397 GHz at εr 4.4, h 1.6 mm,
`sim_openems_patch.py`) is carried to another εr and h by the ratio of TL-model frequencies. The sensitivities are
−11.0 % per unit εr and −1.2 % per mm of h. Combining εr, h (±0.05 mm), openEMS numerics (±0.1 %), model form
(soldermask, copper, probe: ±0.5 %) and etch (±0.17 %), the band is:

| εr knowledge | Prediction band | Ratio to the 2.2 % TL-vs-openEMS separation |
|---|---|---|
| unknown (±0.2) | ±2.26 % | 1.0 — cannot discriminate |
| ring-measured (±0.06) | ±0.85 % | 2.6 — can discriminate |

**Scaling a legal test to flight power.** These scale differently with transmit power P:
- **Induced RF current** in a lead pair is linear in the field, so it goes as √P. From 10.5 dBm conducted
  (10 mW e.r.p.) to 33 dBm is ×13.3 in current.
- **Junction rectification** gives ΔV ≈ V²/(4nV_T) ([EMC](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md)), so it
  goes as P: ×178.

A 10 mW test bounds the flight case only if its detection floor sits 22.5 dB (in power) below the allowed level.

**Saturated-PA supply model (T1).** If the PA swings rail to rail, P_out ∝ V². That gives −0.92 dB at 4.5 V and
+0.83 dB at 5.5 V. The rival hypothesis, an internally regulated PA, predicts 0 dB. A relative measurement in the
same set-up (U ≈ ±0.2 dB) separates the two even with a tinySA.

**Burst-current model (T3).** Assume a class-B-like PA, so (I_dc − I_idle) ∝ √P_out. Anchored at the datasheet
0.85–1.2 A for the E22 at 33 dBm and 0.62 A for the E220 at 30 dBm, this predicts:

| Module | Setting | Predicted burst current |
|---|---|---|
| E22-400T33D | 24 dBm | 0.37–0.49 A |
| | 27 dBm | 0.48–0.65 A |
| | 30 dBm | 0.63–0.88 A |
| | 33 dBm | 0.85–1.20 A |
| E220-900T30D | 21 dBm | 0.25 A |
| | 24 dBm | 0.34 A |
| | 27 dBm | 0.45 A |
| | 30 dBm | 0.62 A |

The structural claim is a log–log slope of 0.5 ± 0.15. A slope near 1 would mean the PA runs at fixed efficiency
(near-saturated at every step).

**Y-factor readings (C3, R5).** With $T_{hot}=290(1+ENR)$, ENR 15 dB → 9461 K, the reading is
Y = (T_hot + T_e)/(290 + T_e):

| DUT NF (dB) | 0.45 | 0.8 | 1.0 | 2.2 | 5.4 | 12 |
|---|---|---|---|---|---|---|
| Y (dB) | 14.70 | 14.36 | 14.17 | 13.02 | 10.05 | 4.76 |

The NF error equals the ENR error (1:1). An uncalibrated source (±1 dB assumed) therefore cannot test a ±0.4 dB
prediction.

**Doppler-rate threshold (K1).** The Semtech rule allows drift ≤ BW/(3·2^SF) (×16 with LDRO) over the packet. For a
constant rate, the threshold is $\dot f_{crit}=\text{limit}/T_{oa}$. The no-tracking model in `lora_css_sim.py`
allows half a bin over the payload instead. The two bracket the onset; P7 of the
[telemetry recipe](lora-rocket-telemetry-link.md) already allows "factor 2".

**L2 jamming (K3).** $1/(C/N_0)_{eff}=1/(C/N_0)+(J/S)/(QR_c)$ ([GNSS interference](../21-gnss/gnss-interference-jamming-spoofing.md)).
With S = −130 dBm, a clean C/N₀ of 45 dB-Hz, Q = 1 and R_c = 1.023 Mchip/s:

| CW jammer J | C/N₀ (dB-Hz) |
|---|---|
| −120 dBm | 43.8 |
| −110 dBm | 38.9 |
| −105 dBm | 34.7 |
| −100 dBm | 30.0 |
| −98 dBm | 28.0 |
| −95 dBm | 25.1 |
| −90 dBm | 20.1 |

### Level 3 — where the budgets break
- **Shared-assumption trap (tenet 1).** A measurement compared with a prediction that used the measured quantity
  itself is not independent. Example: "patch frequency matches openEMS after correcting εr", where εr came from the
  same patch board. Use an independent coupon (M1) and a different method (the patch recipe's three-size
  calibration set) for εr, and check the two εr values against each other.
- **Model-form uncertainty dominates and is not Gaussian.** The ±0.5 % used for ε_eff and patch model form is a
  judgement. If a REFUTED result hinges on it, report the result both with and without that term.
- **Correlated errors.** The same pad used in the source chain and in the reference measurement cancels in a
  relative measurement but adds in an absolute one. Prefer relative (A/B) designs and write down which terms cancel.
- **Field tests are not stationary.** RSSI scatters by σ = 2–6 dB. For ±0.5 dB at 95 % on the mean you need
  N ≥ (1.96σ/0.5)²: 62 packets at σ 2 dB, 554 at σ 6 dB ([OTA testing](../17-test-measurement/antenna-range-ota-testing.md)).
  Interleave the conditions (A/B/A/B) rather than measuring all of A then all of B.
- **The F2 detuning bracket is a heuristic.** It is a log-partition of quasi-static energy, with no field solver
  behind it. Its *ratio* claim (wall-taped ≫ on-axis) is the falsifiable part; its absolute values are not.

## Design equations & rules of thumb
| Quantity | Rule | Value used here |
|---|---|---|
| Acceptance band | √(U_pred² + U_meas²), k = 2 | A5 Yagi: ±1.68 dB (Q2 ±1, U_meas ±1.35) |
| Discrimination | U_meas ≤ D/2 | A3 needs a measured εr |
| Guarded limit | m + U ≤ L | 2f at 33 dBm ≤ −36 dBm → tinySA must read ≤ −37.5 dBm |
| Harmonic need (dBc) | P_ant + 36 (< 1 GHz), P_ant + 30 (≥ 1 GHz) | 33 dBm: 69/63; 10.5 dBm: 46.5/40.5; E220 24 dBm: 54 |
| PER sample size, one point | 1.96² p(1 − p)/Δ² | 1 % ± 0.5 % → 1 521 |
| PER waterfall | 5 × 300 packets | σ(S₀) ≈ 0.06–0.09 dB |
| Range from attenuation | 10^(δA/20) − 1 | 3 dB → +41 % |
| Isolation for conducted RX | leakage ≥ attenuation + 20 dB | −9 dBm source, SF12/125: ≥ 148 dB (96–108 dB with a 40 dB pad in the TX box) |
| AR error from a stray wave ρ | ±20 log(1 + ρ) | −30 dB → ±0.55 dB |
| Test → flight scaling | current ∝ √P; rectification ∝ P | ×13.3 / ×178 for 10.5 → 33 dBm |
| TDR plateau | coupon ≥ 2 × (0.99/span)·v_p/2 | NanoVNA-H4: ≥ 109 mm; LiteVNA: ≥ 26 mm |
| Quarter-wave ripple | \|Γ\|max = \|Z₀² − 50²\|/(Z₀² + 50²) | 45 Ω: RL 19.6 dB; 55 Ω: 20.4 dB (sign from TDR) |

## Test catalogue

The columns of every group table are: **ID | claim under test (KB page#section) | prediction ± band (script) |
method | equipment | pass/fail rule | a miss means / update.** "S1" to "S7" are sections of
`f2_campaign_predictions.py`; other scripts are named. Legal notes: Singapore licence-exempt limits are 10 mW e.r.p.
at 433.05–434.79 MHz (≤ 10 % duty), 500 mW e.r.p. at 866–869 MHz, and 100 mW e.r.p. at 917–925 MHz (≤ 1 % for LoRa)
([IMDA](../19-regulations-safety/singapore-imda-rules.md)). Anything above that is conducted into loads, done in a
shielded enclosure, or done under a licence or permit.

### C — calibration prerequisites (run first; every other band assumes them)
| ID | Claim | Prediction ± band | Method | Equipment | Pass/fail | Miss means / update |
|---|---|---|---|---|---|---|
| F2-C1 | Pads and cables have their nominal loss ([bench recipes, practical notes](../17-test-measurement/bench-measurement-recipes.md)) | nominal ±0.3–0.5 dB | VNA S21 of every pad and cable at each test frequency; label it | NanoVNA-H4 / LiteVNA | MEASURED: use the measured values everywhere | — |
| F2-C2 | The tinySA's absolute level is within ±1.5 dB (bench R6 assumption) | ±1.5 dB | compare against a power sensor, or a known source at 433/868/1575 MHz and −10/−40 dBm | tinySA, sensor | CONFIRMED if within ±1.5 dB | if worse, every tinySA U in this page grows; update R6 and [spectrum analyzers](../17-test-measurement/spectrum-analyzers.md) |
| F2-C3 | The cheap noise source's ENR is unknown (gap R22) | — | hot/cold load (290 K vs 77 K LN₂) or compare with a 346-class source ([NF measurement](../17-test-measurement/noise-figure-measurement.md)) | noise source, LNA, SDR/SA | MEASURED: ENR table with U ≤ ±0.2 dB, or the NF tests are flagged INCONCLUSIVE | — |
| F2-C4 | SDR frequency calibration to ≤ 0.1 ppm | ≤ 0.1 ppm | GPSDO reference, or a cellular-carrier calibration (kalibrate-rtl class) | RTL-SDR/HackRF, GPSDO | MEASURED | needed by T5, T6 and K1 |
| F2-C5 | The VNA is calibrated at the plane used | verification standard reads within ±0.1 dB / ±1° (thru), RL ≥ 35 dB (load) | SOL/SOLT, then measure an independent standard ([VNA calibration](../17-test-measurement/vna-fundamentals-calibration.md)) | VNA, cal kit, spare load | PASS before each A/M session | re-calibrate; mark the session VOID if not done |

### A — antennas
| ID | Claim | Prediction ± band | Method | Equipment | Pass/fail | Miss means / update |
|---|---|---|---|---|---|---|
| F2-A1 | A 2 mm-wire dipole of 327.9 mm resonates at 433 MHz with R ≈ 72 Ω and VSWR 1.44 ([beginner ladder, rung 4](beginner-project-ladder.md)) | 433.1 MHz ± 1.05 % (±4.5 MHz; model 1 %, cut ±1 mm, sweep 0.05 %; S1) | S11 with chokes, 1 m from objects ([NanoVNA recipe A](../17-test-measurement/nanovna-librevna-practical.md)) | NanoVNA-H4, chokes | CONFIRMED in band; R in 60–85 Ω | end-effect/diameter model wrong → update [dipoles](../08-antennas/dipoles-and-monopoles.md) |
| F2-A2 | Installed sleeve dipole resonates 2–5 % low ([telemetry recipe P9](lora-rocket-telemetry-link.md)). Detuning: on-axis in a fibreglass tube 1.0–1.6 % (433 MHz) or 1.4–2.7 % (915 MHz). Wire taped to the wall: ≥ 3× the on-axis shift (F2 bracket, S1) | P9: 403–433 MHz before trimming. F2: ratio(wall/axis) ≥ 3 | same antenna measured in free space, on axis inside the tube/cone, then taped to the wall; then the full stack (battery, rods, harness); one variable per step | NanoVNA, airframe sections | P9 CONFIRMED/REFUTED; F2 ratio CONFIRMED if ≥ 3 | "a few %" in [antennas on rockets](../08-antennas/antennas-on-rockets.md) replaced by measured numbers; closes R07 (detuning part). *Also score against the openEMS predictions* (whip on axis in a 3 mm G10 cone: −1.2 % at 915 MHz, −2.8 % at 433 MHz, shift converged to ±0.05 points; av-bay counterpoise +3.4 %; [openEMS workflow Run 3](../16-simulation-tools/openems-workflow.md)). Note that the 433 MHz openEMS value lies **above** the F2 on-axis bracket (1.0–1.6 %) and the 915 MHz value slightly **below** it (1.4–2.7 %); the geometries differ (whip in an ogive vs sleeve dipole in a tube), so A2 should measure both |
| F2-A3 | The 2.45 GHz FR-4 reference patch (37.23 × 28.81 mm) resonates where openEMS says (−2.2 % vs TL; [openEMS workflow](../16-simulation-tools/openems-workflow.md)) | f = 2.397 GHz × f_TL(εr, h)/f_TL(4.4, 1.6). At εr 4.5, h 1.51: **2.374 GHz ± 0.85 %** with the M1 εr; D = 2.2 % (S1) | S11 at the probe, port extension; M1 coupon on the **same panel** | LiteVNA (NanoVNA-H4 is noisy above 1.5 GHz) | CONFIRMED / REFUTED / INCONCLUSIVE (the last if M1 has not been run) | if it lands near the TL value, openEMS FR-4 set-up (mesh, mask) is suspect → [simulation validation](../16-simulation-tools/simulation-validation.md); closes R21 |
| F2-A4 | GNSS FR-4 patch: best-AR frequency 1575 MHz × √(4.5/Dk) ± 5 MHz; AR ≤ 1.5 dB at best; AR BW 12–18 MHz; RHCP; +1.7 ± 1.5 dBic ([patch recipe P1–P5](patch-antenna-design-walkthrough.md)) | as stated; U_meas(AR) ±0.55 dB only if strays ≤ −30 dB (S1) | rotating linear source at 15° steps, **inside a shielded absorber-lined enclosure or chamber only** (never radiate in 1559–1610 MHz; [spectrum allocation](../19-regulations-safety/spectrum-allocation-ism-bands.md)); containment check: a GNSS receiver outside shows no C/N₀ change; sky C/N₀ vs a ceramic patch (P6) as the independent check | LiteVNA S21 or SDR TX/RX pair, absorber box, Dk from M1 | per P1–P6 | AR miss: cut size/probe; frequency miss after the Dk correction: model error (P1 note) |
| F2-A5 | 6-element Yagi gain 11.2 ± 1 dBi; F/B 13 ± 3 dB; crossed-pair AR ≤ 1 dB ([ground station Q2–Q4](ground-station-tracking-yagi.md)) | P_Yagi − P_dipole = **9.05 dB ± 1.68 dB** (Q2 ±1 combined with U_meas ±1.35; S1) | gain transfer against a reference dipole on a ground-reflection range, h_r ≈ λR/(4h_t) ([OTA testing](../17-test-measurement/antenna-range-ota-testing.md), [antenna measurement](../08-antennas/antenna-measurement.md)); interleaved swaps; 10 mW e.r.p. at 434 MHz. 900 MHz Yagi: test at 868 or 920 MHz (905 MHz is not an SG SRD band) and correct with NEC | 10 mW beacon, SDR at fixed gain, dipole, masts | CONFIRMED in band | DL6WU/MoM gain or construction off → [Yagi page](../08-antennas/yagi-uda-and-log-periodic.md) |
| F2-A6 | LoRa↔GNSS antenna coupling in the airframe is −25 to −40 dB at 433 MHz ([GNSS front end G1](gnss-front-end-design.md)) | −25 … −40 dB (proj_gnss_frontend §1 Friis: −27 dB at 0.5 m) | VNA S21 between the two antenna connectors in the assembled airframe, 300 MHz–3 GHz | NanoVNA/LiteVNA | MEASURED + G1 check | redo the blocking budgets with the measured value; SAW-first if > −30 dB |

### T — transmit (EBYTE E22-400T33D, E220-900T30D; always into rated pads)
| ID | Claim | Prediction ± band | Method | Equipment | Pass/fail | Miss means / update |
|---|---|---|---|---|---|---|
| F2-T1 | Power is within ±0.5 dB of the setting (33/30/27/24 dBm). Supply dependence: saturated-PA model P ∝ V² (−0.92/+0.83 dB at 4.5/5.5 V) vs regulated (0 dB) | ±0.60 dB (sensor) / ±1.58 dB (tinySA) absolute; relative ±0.2 dB (S2; e3_bench §6) | [bench recipe R6](../17-test-measurement/bench-measurement-recipes.md): 20 dB/10 W + 20 dB/2 W pads, gated RMS or CW test mode; 4.5/5.0/5.5 V | 5 V/3 A supply, rated pads, sensor or tinySA | CONFIRMED / REFUTED per step; supply model by slope | power low → brown-out or variant (playbook A); update [modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md); R03 |
| F2-T2 | 2f and 3f meet −36/−30 dBm at the antenna port: needs **69/63 dBc at 33 dBm**, **46.5/40.5 dBc** in the 10 mW e.r.p. test set-up, 54 dBc for the E220 at 24 dBm. Module suppression X is **unknown** ([filter recipe §2](bandpass-filter-design-walkthrough.md)) | no KB value; analyser own H2 −49 dBm without a high-pass, −129 dBm with it (S2) | pads → **high-pass (≥ 40 dB at f₀)** → tinySA, RBW 100 kHz below 1 GHz / 1 MHz above; +10 dB pad "real vs analyser" check | HPF, pads, tinySA | MEASURED X; compliance by guarded acceptance | X < 25 dBc → Chebyshev N = 7 / cascade (filter recipe); R03 |
| F2-T3 | Burst current 0.85–1.2 A (E22 at 33 dBm), 0.62 A (E220 at 30 dBm); (I − I_idle) ∝ √P (slope 0.5 ± 0.15); droop < 5 % | per-step bands in Level 2 (S2) | 0.1 Ω shunt + scope at the module pins, per step and per supply; AUX vs time; 1000 packets | scope, shunt, supply | CONFIRMED if inside band and droop < 5 % | slope ≈ 1 → fixed-efficiency PA; droop → bulk C ≥ I·t/ΔV ([playbook](../17-test-measurement/rf-bring-up-debug-playbook.md)); fills the "burst current" gap |
| F2-T4 | 99 % OBW ≈ 1.05 × BW (133 kHz at 125 kHz in meas_sa.py; 131 kHz in this script's phase-continuous chirp sim). 6 dB BW at BW 500 kHz with a 100 kHz RBW: 551 kHz (averaging detector) to 641 kHz (peak max-hold model) | 99 %: 131–133 kHz ± 4 kHz; 6 dB BW ≥ 500 kHz (S2) | SA OBW function (RBW ≤ 3 kHz) for the 99 % figure; RBW 100 kHz + peak detector + max-hold for 6 dB ([spectrum analyzers ex. 4](../17-test-measurement/spectrum-analyzers.md)) | tinySA | CONFIRMED in band; IREC Mode A by guarded acceptance (≥ 500 kHz) | if the 6 dB BW < 500 kHz, Mode A needs another setting; update [band plans](../15-lora-ism-radios/ism-band-plans-duty-cycle.md) |
| F2-T5 | Static frequency error ±10 ppm typ / ±30 max if a crystal (433 MHz: ±4.3/±13 kHz); ±2.5 ppm if a TCXO (±1.1 kHz). Discriminator: drift over a 25 K self-heat ≈ 1.1 kHz (crystal) vs ≈ 0.1 kHz (TCXO) at 868 MHz ([impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)) | as stated, factor 2 on drift; U_meas ≈ 0.1 ppm (C4) | CW/test mode or preamble tone; SDR locked to the reference; 10 min of continuous TX with a thermocouple on the module | SDR + GPSDO, thermocouple | MEASURED offset; crystal-vs-TCXO decided by drift | answers "TCXO or crystal?" (telemetry recipe gaps); R24 static part |
| F2-T6 | The EBYTE "2.4k" rate is one of SF9/125, SF10/250, SF11/500 (all T_s = 4.096 ms); 9.6k = SF7/250 or SF8/500; 19.2k = SF7/500 ([SDR recipe D5](sdr-receiver-build.md)) | identified by **sweep bandwidth** (125/250/500 kHz), then slope BW/T_s (S2) | waterfall + inspectrum cursors; gr-lora_sdr decode at the identified settings; conducted through pads | RTL-SDR, pads | CONFIRMED (one candidate decodes) / REFUTED (non-standard) | write the mapping into [modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md); closes R01 |

### R — receive
| ID | Claim | Prediction ± band | Method | Equipment | Pass/fail | Miss means / update |
|---|---|---|---|---|---|---|
| F2-R1 | Conducted sensitivity = −174 + 10 log BW + NF + SNR_req: SF7/125 −124.5 (NF 6) or −127.5 (NF 3, module LNA); SF9/125 −129.5/−132.5; SF12/125 −137/−140 dBm ([LoRa sensitivity](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md)); LLCC68 (E220) has no SF10–12 at 125 kHz | datasheet ±2 dB; U_meas ±0.48 dB → band ±2.06 dB; D = 3 dB between NF hypotheses (S3) | PER waterfall, 5 steps × 300 packets; TX in its own box (−9 dBm + 40 dB pad), step attenuator, DUT in a second box; validity check: at maximum attenuation, zero packets ([NF page ex. 4](../17-test-measurement/noise-figure-measurement.md)) | 2 shield boxes, step attenuator, SX126x dev board | CONFIRMED / REFUTED per SF/BW; VOID if the leakage check fails | gives the module NF → recompute P2 of the telemetry recipe; R02 |
| F2-R2 | RSSI is linear (1.00 ± 0.05 dB/dB) from −120 to −40 dBm; its offset is unknown (gap R23) | slope ±0.05; offset MEASURED | same rig as R1, 5 dB steps | as R1 | CONFIRMED slope; offset recorded | a non-linear RSSI makes in-flight RSSI predictions (P4) untestable — use SNR |
| F2-R3 | RTL-SDR NF 5.4 dB at 437 MHz (V3, LSF; [SDR survey](../14-sdr-dsp/sdr-hardware-survey.md)); NF(G) = NF_a + 10 log(1 + 10^((G_x − G)/10)) — flat within 1 dB over the top ≈ 10 dB of gain | NF_a 5.4 ± 1.5 dB (V4/V4L unmeasured); model-fit residual RMS ≤ 0.5 dB (S3) | Y-factor with the C3-calibrated source at 6–8 gain settings | noise source, RTL-SDR | CONFIRMED / REFUTED | update the D6 RTL-SDR NF inconsistency (14 vs 17) with measured values; R11 |
| F2-R4 | RTL IIP3 ≈ −10 dBm is an *assumption* (gap R11); structural claim: IIP3 + G ≈ constant (slope −1 ± 0.3 dB/dB) above mid gain; "high" chain clip −71 ± 3 dBm at the LNA input ([SDR recipe D2](sdr-receiver-build.md)) | slope band; IIP3 MEASURED | two-tone (two generators, combiner, pads; check the combiner's own IMD with the SDR replaced by the tinySA); ADC-clip histogram | 2 sources, combiner, pads | slope CONFIRMED / REFUTED; D2 per its band | cascades in 14/20 use −10 dBm; replace with the measured curve |
| F2-R5 | Ground LNA (TQP3M9036): NF ≤ 1 dB, gain 17–20 dB, no oscillation; chain NF 2.8 dB (433, 4-way split) ([ground station S6/Q5](ground-station-tracking-yagi.md)); GNSS chain C NF 2.2 ± 0.4, chain D 0.8 ± 0.4 ([LNA recipe N2](lna-design-walkthrough.md)) | Y for a lone DUT, ENR 15 dB: 14.70/14.36/14.17/13.02 dB at NF 0.45/0.8/1.0/2.2 (S3); second-stage corrected | Y-factor, second stage measured first ([NF measurement](../17-test-measurement/noise-figure-measurement.md)) | C3-calibrated source, SDR or tinySA | CONFIRMED / REFUTED; INCONCLUSIVE if C3 was not done | input loss under-estimated (N2 note) |

### L — link
| ID | Claim | Prediction ± band | Method | Equipment | Pass/fail | Miss means / update |
|---|---|---|---|---|---|---|
| F2-L1 | Radiated 1 km test at 10 mW e.r.p.: PER < 1 % with **39.7 dB** inserted (15-km equivalent incl. 16.15 dB null); A_fail = P_rx,meas + 125.5 dB (SF7/250); free-space A_fail 59.5 dB ([telemetry recipe ex. 7, P3](lora-rocket-telemetry-link.md)) | ±3 dB (P3) → ±41/−29 % in range (S4) | step attenuator at a shielded receiver; ≥ 300 packets at 39.7 dB; 50 Ω-load validity check before every run; 60 % Fresnel clearance | LNA chain, step attenuator, shield box, masts | P3 CONFIRMED / REFUTED; VOID on a leakage-check failure | leakage or R1 failure; update link margins |
| F2-L2 | Ground-to-ground (both dipoles 1.5 m, 10 mW e.r.p.) follows two-ray: P_rx −85.5/−97.5/−109.5 dBm at 0.5/1/2 km (V-pol, medium-dry ground); slope n = 4 ± 0.5 beyond 13 m; range ≈ 3.3 km at SF9/125 with 10 dB margin ([beginner rung 7](beginner-project-ladder.md), [two-ray](../09-propagation-link-budget/two-ray-ground-reflection.md)) | two-ray ±6 dB at each point; n 4 ± 0.5; Egli (ratio form) is 21 dB more pessimistic and free space 27 dB more optimistic at 1 km — both recorded (S4). **P.1546 is not implemented in the KB** ([empirical models](../09-propagation-link-budget/empirical-path-loss-models.md)) | RSSI/SNR vs distance, ≥ 62 packets/point, GNSS-logged positions, 0.2–3 km, open flat ground | two modules, GNSS logger | CONFIRMED / REFUTED for two-ray; best-fitting model recorded | n ≈ 2 → elevated/terrain lobing; n > 4.5 → clutter; adds the first Singapore field data to 09 |
| F2-L3 | Landed rocket (antenna 0.2 m up): plane-earth PL 128.0 dB (2 m mast) / 118.4 dB (6 m) at 1 km; ranges at 33 dBm SF9/125: 7.5 km (2 m) / 13.0 km (6 m); at 10 mW e.r.p.: 2.1/3.6 km (LNA chain), 1.7 km bare (telemetry recipe ex. 5, P8) | recipe band −50/+0 % in range ≡ **PL excess 0 … +12 dB** over plane-earth (S4) | measure PL(d) at 10 mW e.r.p., SF9/125 (≤ 10 % duty), flight antenna lying in grass, 2 m and 6 m masts; **licensed-power range is inferred from the measured PL**, never transmitted | flight avionics, masts, ground chain | CONFIRMED if the PL excess is within 0–12 dB | larger excess → raise the 10 dB terrain allowance; update [09 example E](../09-propagation-link-budget/link-budget-methodology.md) |

### K — rocket-specific
| ID | Claim | Prediction ± band | Method | Equipment | Pass/fail | Miss means / update |
|---|---|---|---|---|---|---|
| F2-K1 | PER onset vs Doppler rate. 40 B frame, rate thresholds (Semtech rule / no-tracking model): SF7/125 3961/7012 Hz/s; SF8/125 1056/1892; **SF9/125 283/514 (≈ 10 g at 868 MHz)**; SF10/125 76/141; SF12/125 LDRO 82/39; SF7–9/250–500 ≥ 1131 Hz/s ([impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md); P7) | onset between the two values (factor 2; S5) | HIL: SDR replays LoRa IQ with a linear frequency ramp (0, 50, 100, 200, 300, 500, 1000 Hz/s), **cabled** through pads at high SNR into the module; control at 0 Hz/s must give PER < 1 % (interop check); ≥ 200 packets per rate | HackRF/Pluto, pads, receiver logger | CONFIRMED if the onset is inside [min, max]; REFUTED if outside | chip tracks better or worse than the rule → update the SF rule in the telemetry recipe; closes R05 (bench part) |
| F2-K2 | u-blox: no output above 500 m/s at any altitude (design assumption; AND/OR unknown); 80 km (M10 / F9P HPG ≥ 1.13); ignition jerk makes a 15 Hz PLL slip (133° at 50 g/s); FLL keeps lock; fix gap ≤ a few s ([GNSS on rockets](../21-gnss/gnss-on-rockets-dynamics-and-limits.md)) | qualitative + jerk table (S5) | gps-sdr-sim user-motion file (10 Hz epochs — check how motion is interpolated before reading jerk results), **cabled** DC block + attenuation to ≈ −130 dBm per satellite; one variable per run (speed only, altitude only, both) | HackRF/Pluto, attenuators, receiver | MEASURED AND/OR; slip/recovery CONFIRMED / REFUTED | settles the KB's AND/OR contradiction; R16 |
| F2-K3 | An E22 3rd harmonic in L2 (CH 0–2 → 1230.4–1236.4 MHz) kills L2 tracking at J ≳ −95 dBm at the GNSS input; CH 23 (1299.375 MHz) is clean ([GNSS front end G5](gnss-front-end-design.md)) | Kaplan–Hegarty curve (Level 2 table); threshold −94.9 dBm for 25 dB-Hz (S5) | **conducted**: E22 into pads → coupler into the ZED-F9P antenna feed (live sky antenna), harmonic level at the coupler measured with the tinySA; repeat with a CW generator at 1227.6 MHz; CH 23 control | ZED-F9P, coupler, pads, generator | CONFIRMED if L2 C/N₀ follows the curve within ±3 dB | different curve → receiver mitigation exists; record the measured threshold |
| F2-K4 | Pyro-lead pickup at flight power: spread leads ≤ 145 mA (upper bound, 0.2 m from 2 W), twisted < 0.4 mA; must stay ≤ 15 % of no-fire (≈ 20 mA for a 130 mA hobby e-match; no-fire value anecdotal) ([EMC, HERO table](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md), [lab safety ex. 3](../19-regulations-safety/lab-safety-esd-high-power.md)) | test at 10 mW e.r.p. scales ×13.3: the pass threshold is 1.46 mA = −43.7 dBm across a 1 Ω dummy; twisted pair ≈ −77 dBm (S5) | dummy bridge of the e-match's resistance, RF voltage tapped with a choked semi-rigid line to the tinySA (check the tap does not change the pickup by moving/choking it); flight-configured bay, each radio; armed/disarmed; or full power + thermocouple dummy under a permit | dummy bridges, tinySA, ferrites | guarded: PASS if scaled current + U ≤ 15 % of no-fire | update the pad procedure in 19; get the real no-fire rating (R17) |
| F2-K5 | Sensor RF rectification: ΔV ≈ V²/(4nV_T); with RC filters no TX-synchronous baro/IMU/ADC offset ([EMC Level 3](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md)) | offset ∝ P (slope 1 on log–log); flight/test ×178 (S5) | lock-in analysis of high-rate sensor logs against the TX schedule at 3 pad-set powers; full power only under a permit or in a screened room | flight computer, pads | slope CONFIRMED; flight bound only if the 10 mW floor is 22.5 dB below the allowed offset | add filtering; update the [interference-hunting page](../17-test-measurement/interference-hunting-and-rf-immunity.md) |
| F2-K6 | With the harmonic LPF and CH 23, keying the E22 drops L1 C/N₀ ≤ 1 dB (G3); without TX-side filtering > 10 dB (G2); MAX-M10S + SAW, E220 at 24 dBm: no further drop > 1 dB (G4) ([GNSS front end](gnss-front-end-design.md)) | per G2–G4 | G-T4: full vehicle, TX keyed into **pads/dummy load** (conducted, legal) vs into the antenna at legal power; log NAV-SAT/MON-RF; subsystems toggled one at a time | flight vehicle, u-center | CONFIRMED / REFUTED per G-ID | PA wideband noise at 1.5 GHz is the single biggest unknown (G-T3); R15 |

### M — materials and PCB
| ID | Claim | Prediction ± band | Method | Equipment | Pass/fail | Miss means / update |
|---|---|---|---|---|---|---|
| F2-M1 | JLC 2-layer FR-4 εr is 4.5 at 1.5–2.2 GHz (JLC0216A; KB range 4.3–4.7, Djordjevic–Sarkar −0.14/decade; [dielectrics](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md)); the 2-layer dielectric thickness: JLC's JLC0216A calculator template specifies a **1.43 mm core** (13 canonical table); 1.51 mm (patch recipe, 16 benchmarks) and 1.6 mm (sim_openems_patch.py) are model inputs — 1.6 mm is the finished board thickness, not the dielectric; M1 measures it | ring r 35 mm, W 2.9 mm: f₁–f₄ = 0.741/1.479/2.212/2.940 GHz at εr 4.5; extraction **U(εr) ±0.05** (S6); h measured with a micrometer | loosely gap-coupled microstrip ring, no soldermask; S21 peaks; two gap widths (the gap-loading shift must shrink with the looser gap); board thickness minus copper by micrometer. (Cavity/resonator theory: [waveguides & cavities](../02-electromagnetics/waveguides-and-cavity-resonators.md); the planned 17 cavity-perturbation page does not exist yet) | LiteVNA, JLC coupon | MEASURED εr and h; CONFIRMED if within 4.3–4.7 | feeds A3/A4 and the [stackups](../13-pcb-rf-layout-emc/stackups-and-materials.md) tables; resolves the thickness inconsistency |
| F2-M2 | Impedance coupons: JLC04161H-7628 masked 0.359 mm → 49.5 Ω (FD); ~98 % of boards in 45–55 Ω with impedance control (σ ≈ 2.1 Ω); 2-layer 2.692 mm → 49.2 Ω ([canonical width table](../13-pcb-rf-layout-emc/stackups-and-materials.md), [JLC](../13-pcb-rf-layout-emc/jlcpcb-rf-manufacturing.md)) | 49.5 ± 4.3 Ω (2σ) | TDR (needs a coupon ≥ 26 mm on a LiteVNA, ≥ 109 mm on a NanoVNA-H4; S6) plus an independent quarter-wave-ripple check (45/55 Ω → RL ≈ 20 dB peaks) on 60 and 120 mm coupons (launches cancel in the difference) ([TDR](../03-transmission-lines-matching/time-domain-reflectometry.md)) | LiteVNA, coupons | CONFIRMED in band | calculator residual, or JLC ±20 % rather than ±10 %; closes R09 |
| F2-M3 | Single via row, 0.3 mm drill: 1 mm pitch FDFD 40.5 dB at 2.45 GHz vs textbook 53.8 dB (D = 13.4 dB); 2 mm pitch FDFD 24.8 dB (the two agree within 1 dB) ([via fencing](../13-pcb-rf-layout-emc/vias-stitching-fencing.md)) | FDFD ±3 dB (page) + U_meas ±2 dB (S6) | 4-layer coupons, two probes into the L2–L3 plane pair 30 mm apart: no fence / 1 mm row / 2 mm row / plated-slot reference (sets the coupon's own leakage floor); band-averaged \|S21\|² over 1.4–1.7 and 2.2–2.7 GHz to smear cavity modes | LiteVNA, JLC coupons | CONFIRMED / REFUTED (1 mm pitch decides FDFD vs textbook) | wrong Λ(r/a) → update the 13 page's table |

### E — environment
| ID | Claim | Prediction ± band | Method | Equipment | Pass/fail | Miss means / update |
|---|---|---|---|---|---|---|
| F2-E1 | Launch-site occupancy in 433.05–434.79, 866–869 and 917–925 MHz plus band-8 levels above 925 MHz ([signal ID & survey ex. 6](../14-sdr-dsp/signal-identification-and-spectrum-survey.md)) | threshold +1.26 dB over the floor at K = 100 (+3.55 at K = 10; S7); expected bursty 433 MHz OOK/FSK devices and 920 MHz LoRaWAN; hopping intercept ≈ 0.27 for 50 ms bursts | rtl_power for hours with the flight-like antenna/LNA, a 50 Ω floor file first, then dwell IQ on chosen channels; a survey report per the 14 page | RTL-SDR, ground chain | MEASURED; channel choice recorded | update channel plans; R13 |
| F2-E2 | Man-made noise at 425 MHz (P.372-13 Table 3): city 1150 K / residential 730 K / rural 580 K ([thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md)); no KB values at 868/915 MHz | antenna-vs-load noise rise with a 2.0 dB chain: city +4.6 dB, residential +2.9, rural +2.1; quiet (100 K) −2.3 dB (S7); ±1 dB | ground chain on the antenna vs on a 50 Ω load at the LNA input (same gain, RMS detector), several elevations and azimuths, day/night; also 868/915 MHz | ground chain, SDR/tinySA | CONFIRMED for the closest environment class; MEASURED at 868/915 MHz | raises/lowers the effective NF in every budget; also gives antenna temperature vs elevation (R14) |

### F — flight scoring (already pre-registered in the recipes; listed so the campaign is complete)
| ID | Claim | Source | Scored with |
|---|---|---|---|
| F2-F1 | In-flight RSSI near apogee −67 ± 6 dBm (433 MHz, 33 dBm, station C); ascent loss < 2 %, not concentrated in the burn | [telemetry recipe P4–P5](lora-rocket-telemetry-link.md) | loss against the end-of-flight frame count; drops and losses both |
| F2-F2 | Carrier offset follows −ṙf_c/c to ±50 Hz after removing the static offset | telemetry P6, SDR recipe D4 | FEI/SDR vs GNSS velocity; also gives the ignition oscillator step (R24) |
| F2-F3 | Drift losses at high SF only as predicted; no plume dropouts | telemetry P7, P10 | per-packet loss vs flight time and look angle |
| F2-F4 | GNSS: fix kept through boost on the F9P/M10 within the K2 behaviour; RTK float during TX-heavy periods | [GNSS on rockets](../21-gnss/gnss-on-rockets-dynamics-and-limits.md), GNSS front end G3 | NAV-PVT/NAV-SAT logs vs the flight phase |

## Worked examples

### 1. Pre-registering F2-A3 (the patch) properly
1. Order a JLC 2-layer panel with the 2.45 GHz patch, the M1 ring, a THRU and the GNSS patch calibration set,
   all on **one panel**, so they share one laminate lot.
2. Write the prediction file *before* the boards arrive:
   - f_pred = 2.397 GHz × f_TL(εr_M1, h_meas)/f_TL(4.4, 1.6 mm);
   - band ±0.85 % (budget as in Level 2);
   - competing hypothesis: the TL model, 2.2 % higher; D = 2.2 %;
   - INCONCLUSIVE if U(εr_M1) > 0.1.
3. Measure M1 first. Suppose εr = 4.52 ± 0.05 and h = 1.50 mm. The prediction becomes ≈ 2.369 GHz ± 20 MHz, and the
   TL hypothesis 2.421 GHz.
4. Measure the patch.
   - 2.365 GHz → CONFIRMED (openEMS transports correctly).
   - 2.425 GHz → REFUTED (openEMS FR-4 set-up suspect).
   - Measuring the patch without M1 → INCONCLUSIVE, by the pre-registered rule.

### 2. Scoring F2-R1 for an E22 at SF9/125
The waterfall fit gives a 1 % point of −131.4 dBm, with U_meas ±0.48 dB. The NF-6 prediction is −129.5 dBm and the
band is ±2.06 dB, so |m − p| = 1.9 dB: inside the band, CONFIRMED for the datasheet claim. The fit also implies a
module NF of ≈ 4.1 dB. Report this *as measured*: the EBYTE LNA helps by ≈ 1.9 dB ± 0.5 dB. Then recompute the
telemetry recipe's P2 in an addendum. The original prediction stays untouched.

### 3. Guarded acceptance of the E22 2nd harmonic (F2-T2) in the 10 mW test set-up
With 24 dBm → 13.5 dB pad → dipole, the 2f limit is −36 dBm, i.e. ≥ 46.5 dBc. Through 40 dB of pads and a 1 dB
high-pass, the tinySA reads −79.0 dBm, so the antenna-referred level is −79 + 41 = −38.0 dBm, with U ±1.5 dB.
−38.0 + 1.5 = −36.5 ≤ −36, so this is **PASS**. Had it read −37.2 dBm, the result would be INDETERMINATE, to be
re-measured with a power-sensor-anchored set-up. It would *not* be rounded to a pass.

### 4. Is a 10 mW pyro-lead test meaningful? (F2-K4)
Target: ≤ 19.5 mA at 33 dBm (15 % of a 130 mA no-fire). At the legal 10.5 dBm conducted, the induced current is
13.3× smaller: 1.46 mA, or 1.46 mV across a 1 Ω dummy, i.e. −43.7 dBm into the tinySA through a high-impedance tap.
That is about 55 dB above the tinySA's floor, so the test resolves the threshold easily. Twisted, shorted leads
should read about −77 dBm. The same logic fails for sensor rectification (F2-K5). The offset scales as P (×178), so
a 10 mW null result says almost nothing about 2 W.

## Equipment list and cost by tier
Prices follow [lab setup by budget](../17-test-measurement/lab-setup-by-budget.md) (US$; estimates, check before
buying).

| Tier | Kit | Tests it enables |
|---|---|---|
| **≈ S$300** | NanoVNA-H4 (≈ 110); tinySA Ultra (≈ 120–130); RTL-SDR Blog V3/V4L (≈ 35–40); 30 dB/2 W + 10/20 dB pads, 50 Ω loads, SMA plumbing (≈ 50–70); ferrites | C1, C5, A1, A2, A6 (433/915), T1 (±1.6 dB), T2 (with an HPF), T3 (with a scope), T4, T6, L2, L3, E1, E2 (coarse) |
| **≈ S$2 000** | add a LiteVNA 64 (≈ 190) or LibreVNA; a used power meter + sensor (≈ 200–600, *the accuracy anchor*); step attenuator 0–70/90 dB (≈ 100–300); two shielded boxes + feed-throughs (≈ 50); HackRF/Pluto (≈ 200–350); 433/915 MHz SAW/cavity filters and a > 700 MHz high-pass (≈ 50–100); noise source + its calibration (C3); GPSDO (≈ 100–200, est.); thermocouples | everything above at full precision plus A3, A4 (with an absorber box), A5, R1–R5, L1, K1–K6, M1–M3, T5 |
| **≈ S$15 000** | benchtop VNA ≥ 6 GHz, SA with preamp + TG, 346-class noise source, lab signal generator, traceable cal kit | U_meas roughly halves (NF ±0.1–0.2 dB, power ±0.1 dB); not needed to start |
| **Campaign extras** | JLC coupon panel (ring, Z₀ coupons, via-fence set, 2.45 GHz patch, GNSS calibration set; est. US$30–60); absorber foam + a metal enclosure for 1.6 GHz (est. US$100–200, or SUTD's chamber); dummy e-match bridges; fibreglass tube/cone offcuts; a second set of flight modules for destructive tests | A2–A4, M1–M3, K4 |

Rule from the lab-setup page: one accuracy anchor (power sensor or calibrated source) that every other dBm chains
to. Without it, T1, R1 and L1 can only be scored with the ±1.5 dB tinySA budget.

## Data recording template
Each run produces **one CSV row** (one row per quantity), plus raw files whose hashes are in the row. Get the header
and JSON schema from `python3 tools/verify/f2_campaign_predictions.py --schema`. Before anything is scored, run
`--validate results.csv`. It fails on empty files, missing required fields, non-numeric values and unknown
outcomes: absent evidence is a failure, never a pass.

```
test_id,prereg_file,prereg_sha256,run_id,date_utc,operator,witness,location,dut_id,firmware,radio_config,
instruments,cal_state,setup,environment,validity_checks,raw_files,raw_sha256,quantity,measured,unit,u_c,k,
budget,predicted,band,outcome,anomalies,kb_pages,notes
```

| Field group | What to put there (required unless marked optional) |
|---|---|
| Identity | `test_id` (F2-xx); `run_id`; `date_utc`; `operator`; `witness` (optional); `location` (+ coordinates in the field) |
| Pre-registration | `prereg_file` (write-once file in the test branch) and its `prereg_sha256` at run time; `predicted` and `band` copied verbatim |
| What flew / was tested | `dut_id` (board serial/MAC, module serial, antenna ID); `firmware` (git hash + build flags + the boot CONFIG line verbatim); `radio_config` (f, SF, BW, CR, power, preamble, sync word, LDRO, LBT) |
| Calibration state | `instruments` (model/serial/firmware); `cal_state` (VNA cal type/plane/kit + verification result, SA level check, ENR table, SDR ppm, pad/cable S21 values used) |
| Conditions | `setup` (pads, attenuator settings, cables, geometry, photo file names); `environment` (temperature, humidity, supply voltage, weather) |
| Evidence | `validity_checks` (leakage/load test, containment check, "real vs analyser" test — each PASS/FAIL); `raw_files` (Touchstone, CSV, IQ, logs) and `raw_sha256` |
| Result | `quantity`, `measured`, `unit`, `u_c`, `k`, `budget` (name=value;…), `outcome` (CONFIRMED/REFUTED/INCONCLUSIVE/VOID/MEASURED/PASS/FAIL/INDETERMINATE) |
| Follow-up | `anomalies` (IDs F2-AN-nn, each with a disposition: explained / banded / open / superseded; optional); `kb_pages` to update; `notes` (optional) |

Keep raw data and capture scripts on a `test/<topic>` branch of the flight repository with a `VERIFICATION.md`, as
the bench-testing note prescribes. Raw logs stay gitignored there; commit excerpts and the CSV.

## Sequencing (cheap and high-information first)

**Value = impact (1–3) × discrimination (1–3) ÷ cost (1–3).** Impact means it gates a flight decision or many
pages. Discrimination means it can separate hypotheses or fill a true unknown.

| Phase | Tests (value) | Depends on | Gap rows closed |
|---|---|---|---|
| **0 — week 0** | write all pre-registrations; **order the JLC coupon panel** (lead time); C1, C2, C4, C5 (metrology, ½ day) | — | — |
| **1 — bench, ≈ S$300 kit** | **T6 air-rate (9)**, **T1 + T3 power/current/supply (6)**, **T2 harmonics (6)**, T5 frequency error (6), T4 OBW (3), A1 dipole (2), A6 coupling (4) | C1, C2, C4 | R01, R03, R24 (static part) |
| **2 — bench, ≈ S$2 000 kit** | C3 ENR (prerequisite), **R1 sensitivity waterfall (9)**, R2 RSSI (3), R3/R4 RTL NF/IIP3 (3), R5 LNA NF (4), **A2 installed detuning (6)**, **M1 ring εr (6)** → A3 patch (4) → A4 GNSS patch (4), M2 coupon (3), M3 via fence (3) | C3 before R3/R5; M1 before A3/A4; panel delivered | R02, R07, R09, R11, R21, R22, R23 |
| **3 — HIL and coexistence** | **K1 Doppler HIL (9)**, **K3 L2 harmonic (6)**, **K6 GNSS C/N₀ with TX (6)**, **K4 pyro pickup (6, safety)**, K2 GNSS HIL replay (4), K5 rectification (3) | T6 (settings), R1 (levels), A6 (coupling) | R05, R15, R16, R17 |
| **4 — field** | **L1 attenuator range test (6)**, L2 ground range (4), A5 Yagi (4), L3 landed (4), E2 noise floor (4), E1 site survey (before launch day) | R1, R5, E2 (to interpret L1); A5 for station gain | R13, R14 |
| **5 — flight** | F1–F4 scoring | all of the above; frozen firmware with a CONFIG line | R06, R08 (partial), R24 (dynamic) |

**Top 10 by value:**
1. T6 — the EBYTE air-rate mapping. It gates the flight SF choice and needs only an RTL-SDR.
2. R1 — the conducted PER waterfall. It anchors every link budget and measures the module NF.
3. K1 — the Doppler-rate HIL. It tests the KB's most consequential rule (SF ≤ 8 at 125 kHz during boost).
4. T1 + T3 — power, current and supply. They catch brown-out, the commonest "RF" failure.
5. T2 — harmonics. Legality, plus the unknown X that decides the filter.
6. A2 — installed antenna detuning. It tests P9 and the F2 wall-vs-axis bracket.
7. K6 + K3 — GNSS coexistence: L1 desense with TX on, and L2 harmonic jamming.
8. M1 — the ring-resonator εr. A cheap coupon that makes A3/A4 decisive and settles the 2-layer thickness inconsistency.
9. K4 — pyro-lead pickup. A safety-critical bound, measurable at legal power.
10. L1 — the attenuator range test. The end-to-end system number.

Runners-up: T5 (TCXO or crystal), E2 (site noise), A5 (station gain).

Not covered here (separate projects, see the recipes): FMCW radar (M-T1–M-T7), KrakenSDR DF (R18, A-T1–A-T6),
rocket RCS (R19), HB100 NF (R20), in-circuit Q/ESL (R10), SAW rejection at band 8 (R12), connector vibration (R25),
av-bay thermal soak (R04; fold it into the telemetry recipe's T10 pad rehearsal), and IMDA rulings (R26 — a letter,
not a measurement).

## How to update the KB from results
1. **Score first, in the results CSV.** Then write the KB; never the other way round.
2. **On the page that owns the number**, add or extend a section `## Measured results` placed just before
   `## Open questions / gaps`. Use one table row per result:
   `F2-ID | quantity | pre-registered prediction ± band | measured ± U (k) | outcome | date | data (run_id, branch/path)`.
   Never edit the original prediction text. Append a tag next to it instead, e.g.
   *"(measured 2026-11-02, F2-A3: CONFIRMED — see Measured results)"*.
3. **Refuted predictions.** Add a dated addendum under the prediction saying what was wrong and what replaces it.
   Keep the old number visible (the ethos' "conclusions drawn and withdrawn"). Fix scripts at the source, with a
   comment naming the F2 test.
4. **Confidence labels.** Use Measured / Observed / Suspected / Untested / Derived in the text. Raise a page's
   front-matter `confidence` only when its load-bearing numbers have CONFIRMED results. Lower it on a REFUTED one
   until the page is fixed.
5. **`gaps/GAP_REGISTER.md`.** Under its §7 row (R01–R26), append "measured YYYY-MM-DD, F2-xx: result, page#section".
   If that closes the unknown, move the row to §5 *Closed*, per the register's own rule (append, with page#section
   and the date). Every REFUTED or surprising result becomes a new §3 row with the next free ID. A miss is a gap
   the measurement has found.
6. **This page.** Add the outcome to a "Campaign log" table here. Keep per-test detail on the owning pages. Record
   the work in a research log, then rebuild the indexes with `python3 tools/build_index.py --check`.

## Practical notes
- **Bench builds:** TX interlocked unless a load is detected; pyro arming held off; boot CONFIG line on every run;
  capture from reset; kill anything holding the serial port before every capture.
- **Pads first, always.** The E22 at 33 dBm needs ≥ 40–43 dB in front of a tinySA, with the first pad rated ≥ 5 W.
  Never key into an open or into a VNA port ([playbook](../17-test-measurement/rf-bring-up-debug-playbook.md)).
- **Interleave A/B conditions** and repeat the first condition at the end, to expose drift.
- **One variable per run.** Where two may interact (e.g. SD logging × Wi-Fi in K6), use a 2×2.
- **Photograph every set-up.** Cable routing changes antenna results.
- **Battery, not USB,** for anything that will fly. Repeat power-ups.

## Common mistakes & misconceptions
- **"We'll decide the tolerance after we see the data."** That is how a miss becomes a pass. Bands are written first;
  later ideas go in a dated addendum.
- **"The patch matched the simulation after we fitted εr from the patch."** That is self-validation (tenet 1). Use M1.
- **"It's inside the band, so it's confirmed."** Not if U_meas could not separate the rival hypothesis: that is
  INCONCLUSIVE.
- **"The tinySA says −37 dBm, so we meet −36 dBm."** Not with ±1.5 dB of uncertainty: INDETERMINATE.
- **"A low-power test proves the full-power case."** True only for quantities that scale linearly with field, after
  scaling (pyro current ∝ √P). False for rectification (∝ P), compression and heating.
- **"A short radiated test at 1575 MHz is harmless."** Even −20 dBm EIRP is far above GNSS signal levels tens of
  metres away. Use a shielded enclosure, or measure conducted.
- **"Conducted sensitivity looks better than the datasheet — great!"** It usually means leakage. Run the
  maximum-attenuation check, and mark the run VOID if it fails.
- **"Two runs agree, so it's right."** Run-to-run agreement is blind to shared errors. Check against an independent
  method or reference.

## How to simulate / verify
- `python3 tools/verify/f2_campaign_predictions.py`: S0–S7 as described above; 28/28 checks reproduce the KB numbers
  quoted on this page (A_eq 39.7 dB, A_fail 59.5 dB, ToA 288 ms, drift limit 81 Hz, L2 threshold −95 dBm,
  26.5° per 10 g/s, OBW 133 kHz, Y 14.20 dB, via fence 41/25 dB, ground range 3.3 km, survey threshold 1.3 dB) plus
  the F2-derived bands. Output: `f2_campaign_predictions_output.txt`.
- `--schema` / `--validate FILE.csv`: the results-record format and its checker.
- Reused scripts: `lora_toa.py`, `lora_css_sim.py`, `prop_two_ray.py`, `prop_empirical.py`, `rfcalc.tline`.
  Predictions quoted from `proj_lora_link.py`, `proj_ground_station.py`, `proj_patch_gnss.py`,
  `proj_openems_gnss_patch.py`, `sim_openems_patch.py`, `proj_harmonic_filter.py`, `proj_gnss_frontend.py`,
  `proj_lna_gnss.py`, `proj_sdr_receiver.py`, `e3_bench.py`, `meas_sa.py`, `meas_noise_figure.py`,
  `pcb_via_fence.py`, `pcb_emc_radiation.py`, `reg_hero_distance.py`, `e6_beginner_numbers.py`.

## Open questions / gaps
- **No measurement has been made yet.** Every outcome column is empty until the campaign runs.
- **P.1546 and P.528 are not implemented in the KB; ITM now is** (`rfcalc itm`, 2026-10-13). L2/L3 are scored against
  two-ray and the closed-form models. For a landed antenna on a real profile ITM gives 10–50 dB *less* loss than
  two-ray ([tool landscape Example 4](../16-simulation-tools/tool-landscape-overview.md)); L3's measured PL excess
  will show which is closer for the test site, so record the ITM prediction for the site alongside F2-L3 before the test.
- **No cavity-perturbation / resonator permittivity page yet.** It was planned by W5-E11 as
  17/resonator-and-cavity-perturbation-permittivity-measurement. M1 currently relies on the microstrip models in
  rfcalc. Link it here when it exists.
- **The nose-cone detuning bracket is an F2 heuristic.** An openEMS model of a *representative* cone now exists
  (−1.2 % / −2.8 % on axis, [openEMS workflow Run 3](../16-simulation-tools/openems-workflow.md)), but not of the team's nose cone/tube, and no
  wall-taped case was simulated. Its absolute wall-taped values (15–27 %) are probably high.
- **Unknowns with no KB prediction** (MEASURED tests):
  - E22/E220 harmonic suppression X;
  - module NF;
  - RSSI offset;
  - RTL IIP3 vs gain;
  - cheap-noise-source ENR;
  - e-match no-fire current (the 130 mA used is anecdotal);
  - u-blox AND/OR;
  - man-made noise at 868/915 MHz.
- **Recipe procedures that conflict with legality** — corrected here and, on 2026-10-12 (W5-E12), on the owning pages too:
  - the patch recipe T3 (radiated AR at L1) needs a shielded enclosure;
  - ground-station S4/S5 at 905 MHz must move to 868/920 MHz in Singapore.
- **gps-sdr-sim interpolation between its 10 Hz motion epochs is unknown.** That limits K2's jerk realism.
- **Unverified tinySA RBW filter shape.** The 6 dB-BW prediction assumes a Gaussian RBW.

## Sources
1. This KB: [telemetry recipe](lora-rocket-telemetry-link.md), [ground station](ground-station-tracking-yagi.md), [patch](patch-antenna-design-walkthrough.md), [filter](bandpass-filter-design-walkthrough.md), [GNSS front end](gnss-front-end-design.md), [LNA](lna-design-walkthrough.md), [SDR receiver](sdr-receiver-build.md), [beginner ladder](beginner-project-ladder.md) — every pre-registered prediction scored here. (internal)
2. This KB, domain 17: [bench recipes](../17-test-measurement/bench-measurement-recipes.md), [bring-up playbook](../17-test-measurement/rf-bring-up-debug-playbook.md), [NF measurement](../17-test-measurement/noise-figure-measurement.md), [OTA testing](../17-test-measurement/antenna-range-ota-testing.md), [spectrum analyzers](../17-test-measurement/spectrum-analyzers.md), [lab setup](../17-test-measurement/lab-setup-by-budget.md) — methods, GUM budgets, statistics. (internal)
3. This KB: [LoRa sensitivity](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md), [impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md), [EBYTE modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md) — sensitivity rule, drift rule, module data. (internal; primary Semtech/EBYTE sources cited there)
4. This KB: [antennas on rockets](../08-antennas/antennas-on-rockets.md), [via fencing](../13-pcb-rf-layout-emc/vias-stitching-fencing.md), [stackups](../13-pcb-rf-layout-emc/stackups-and-materials.md), [EMC](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md), [GNSS on rockets](../21-gnss/gnss-on-rockets-dynamics-and-limits.md), [thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md), [signal ID & survey](../14-sdr-dsp/signal-identification-and-spectrum-survey.md), [Singapore IMDA](../19-regulations-safety/singapore-imda-rules.md), [lab safety](../19-regulations-safety/lab-safety-esd-high-power.md). (internal)
5. JCGM 100:2008, *Guide to the Expression of Uncertainty in Measurement (GUM)* — standard uncertainties, coverage factor (via the bench recipes page). (standard)
6. ISO 14253-1:2017, *Decision rules for verifying conformity* — the guarded-acceptance idea used for limits (cited from general knowledge, not re-read; the rule here is the conservative form). (standard)
7. ITU-R P.372-13 (2016), *Radio noise*, Table 3 (425 MHz man-made noise) — via the thermal-noise page. (standard)
8. E. D. Kaplan, C. J. Hegarty, *Understanding GPS/GNSS*, 3rd ed. (2017) — effective C/N₀ with interference — via the 21 interference page. (textbook)
9. Space Bar avionics knowledge base (the user's own notes, outside this repository): the engineering-ethos note and the hardware-in-the-loop and bench-testing methods note — tenets, pre-registration, record-everything, test-branch and log-capture discipline. (internal, user-provided)
10. This repository: `tools/verify/f2_campaign_predictions.py` and the scripts listed under How to simulate / verify. (verification)
