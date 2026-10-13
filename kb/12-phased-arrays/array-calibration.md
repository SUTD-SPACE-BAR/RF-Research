---
title: Array calibration — error sources, REV, mutual-coupling self-calibration, near-field and far-field methods, coherent-SDR noise-source calibration
domain: 12-phased-arrays
slug: array-calibration
tags: [calibration, channel-errors, REV, rotating-element-electric-field-vector, mutual-coupling-calibration, near-field-probe, far-field-beacon, noise-source, KrakenSDR, coherent-SDR, cross-correlation, fractional-delay, self-calibration, error-budget, temperature-drift, lookup-table]
prerequisites: [array-factor-linear-arrays.md, tapering-sidelobe-control.md, beamforming-architectures.md, phase-shifters-ttd-components.md]
related: [planar-arrays-element-pattern-coupling.md, adaptive-beamforming-doa.md, diy-phased-array-projects.md, beam-steering-grating-lobes.md, ../00-math-foundations/matrices-and-linear-algebra-for-networks.md, ../08-antennas/antenna-measurement.md, ../17-test-measurement/antenna-range-ota-testing.md, ../17-test-measurement/sdr-as-test-equipment.md, ../14-sdr-dsp/sdr-hardware-survey.md]
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# Array calibration

## Questions this page answers
- Why does a phased array need calibration at all, if every channel is "identical"?
- What errors does calibration remove, and which does it not?
- How accurately must I calibrate to get −25 dB (or −30 dB) sidelobes?
- How can I calibrate an analog phased array with only a power meter or spectrum analyser (REV method)?
- How does KrakenSDR make five RTL-SDR tuners phase-coherent, and why do the antenna cables still have to be equal?
- Can an array calibrate itself using coupling between its own elements?
- What is near-field probe calibration and when is it worth it?
- How do I calibrate a digital (SDR) array with a beacon in the far field?
- How often must I recalibrate — after every retune? Every temperature change?
- How do I measure the delay between two SDR channels to a fraction of a sample?
- What calibration does a DOA array need beyond receiver phase and gain?

## TL;DR
- **Every channel differs**: cables, connectors, LNAs, phase-shifter states, VGAs, mixers, PLL lock phase, ADC timing, and each element's embedded pattern. Typical *uncalibrated* spreads: ±1–2 dB and tens of degrees (random LO phase after every retune in SDR arrays: anywhere in 360°).
- **What you need**: for a sidelobe floor 10 dB below the design level, (σ_a² + σ_φ²) ≤ N·η_t·10^{(SLL−10)/10}: **8 elements, −25 dB → 0.29 dB / 1.9° rms; 64 elements, −30 dB → 0.44 dB / 3.0°; 64 elements, −40 dB → 0.14 dB / 0.9°** (script §4). Pointing is far less sensitive than sidelobes ([beam steering](beam-steering-grating-lobes.md) §(h)).
- **Coherent SDR arrays (KrakenSDR)**: a switched-in common noise source is cross-correlated against a reference channel; integer + fractional sample delay and complex gain are estimated and removed after every retune [1]. The phase estimate is extremely precise — std = √((2/s + 1/s²)/(2M)) rad (s = noise-source SNR, M samples): 0.02° for 65 536 samples at 20 dB (verified). **Only the path from the injection point onward is calibrated**: antennas and cables before the switch are not — hence "cables equal to within 1 cm below ~900 MHz" (1 cm ≈ 7° at 400 MHz, 14° at 800 MHz) [2].
- **REV (rotating-element electric-field vector, Mano & Katagi 1982 [3])**: with all elements on and a far-field probe, rotate one element's phase through its states and record only *power*; P(Δ) = A + B cos(Δ + ψ) yields that element's complex excitation relative to the total field. Needs ≥ 3 states per element (N·2^P readings for a full sweep). Our simulation: 6-bit, 20 dB SNR, 2° phase-shifter state error → 0.07 dB / 0.44° estimation error; Taylor-25 sidelobes restored from −8.4 dB to −23.2 dB (design −24.4) in three passes.
- **Mutual-coupling self-calibration (Aumann, Fenn & Willwerth 1989 [4])**: transmit on one element, receive on its neighbours; equal-geometry pairs must see equal coupling, so the ratios expose the channel errors. Least-squares solution recovers 1 dB / 25° errors to 0.004 dB / 0.03° ideally; **edge elements** (whose coupling differs by 10% / 30%) leave 0.18 dB / 1.6° and 0.64 dB / 4.4° residuals. There is an exact ±1 "parity" ambiguity (π on alternate elements) resolved only by prior knowledge that errors are < 90° or one external measurement (derived and verified).
- **Near-field probe scanning** measures the aperture field directly (back-projection/holography): the gold standard for large arrays, needs a scanner. **Far-field beacon** calibration of a *digital* array is trivial (each channel's complex output for a known plane wave); of an analog array, use REV or on/off toggling.
- **DOA arrays** need more than receiver calibration: element positions, mutual coupling and embedded-pattern differences distort the steering vector; calibrate against sources at known bearings or estimate them jointly (self-calibration) ([DOA](adaptive-beamforming-doa.md)).

## Intuition (no math)

**Beamforming is bookkeeping of phases; calibration makes the books honest.** The steering vector you *compute* assumes every channel adds the same delay and gain. In reality each channel is a slightly different piece of cable, amplifier and chip. The array doesn't care what you *think* the phases are — it adds what *arrives*. Calibration measures each channel's actual complex gain and subtracts the differences in the weights.

**Two kinds of error.** Some errors live in the electronics (receiver gain, cable length, PLL phase) — these are the same for all directions and can be measured by injecting a known signal. Others live in the antenna (element position, mutual coupling, the element's own pattern) — these depend on direction and can only be measured with a signal arriving *through the air*. A noise source at the receiver input fixes the first kind and is blind to the second.

**Power-only calibration (REV) — the trick.** With everything switched on, the far-field probe sees the sum of all elements. If you rotate the phase of one element, its small phasor rotates around the tip of the "everything else" phasor; the received power goes up and down sinusoidally. The depth of that ripple tells you how big the element's contribution is; where the maximum occurs tells you its phase. No phase-measuring receiver is needed.

**Coupling-based self-calibration — the trick.** Two identical pairs of neighbours, the same distance apart, must couple identically. If one pair *measures* 3 dB and 20° different from the other, that difference must be in the electronics. Enough such comparisons pin down every channel — except for errors that look identical in all comparisons (a symmetry of the problem), which is why one sign ambiguity remains.

**Why coherent SDRs must recalibrate after every retune.** Sharing a reference clock locks all tuners' frequencies, but each synthesiser settles at its own random phase every time it relocks, and the USB sample streams start at different instants. The noise source provides a common signal, so each retune is followed by a few milliseconds of "listen to the noise, measure the differences, correct" [1].

## The math

### Level 1 — the error model

Channel n's measured output for a far-field plane wave from û:
$$x_n = g_n\,e^{j\phi_n}\;f_n(\hat u)\;e^{jk\,\hat u\cdot(\mathbf r_n+\delta\mathbf r_n)}\;s + \text{noise},$$
where g_n e^{jφ_n} is the *channel* (receiver/feed) error, f_n the embedded element pattern (coupling, edge effects), δr_n the position error. Electronic calibration estimates c_n = g_n e^{jφ_n} and applies w_n → w_n/c_n; antenna-level calibration also models f_n and δr_n.

| Method | Measures | Equipment | Calibrates antennas too? | Speed |
|---|---|---|---|---|
| Injected noise/tone (KrakenSDR) | c_n from injection point on | built-in source + switches | no | ms, after every retune |
| Internal coupler manifold | c_n from element coupler on | cal network in the array | partly (not radiators) | fast, in service |
| REV (power only) | complex excitation incl. radiators | far-field probe + power meter | yes (in probe direction) | N·(3…2^P) readings |
| On/off or Hadamard switching | same as REV | far-field probe, receiver | yes | N…2N readings |
| Mutual coupling (Aumann) | t_n, r_n from element pairs | array's own T/R | radiators assumed identical | N² pair measurements |
| Near-field probe scan | aperture field → each element | planar scanner + VNA | yes, fully | slow, lab |
| Far-field beacon (digital array) | complex response to a plane wave | beacon ≥ 2L²/λ away | yes (in beacon direction) | one snapshot |
| Sources of opportunity (self-cal) | c_n and geometry jointly | none extra | yes, statistically | during operation |

### Level 1½ — calibration with algebra only
- **What one channel does to the signal.** Each receiver channel multiplies what its antenna delivers by an unknown gain $g_n$ and turns its phase by an unknown $\phi_n$ (cable length, filter, mixer, ADC clock). Calibration means measuring these numbers and dividing them out.
- **The injected-tone method in two lines.** Feed the same tone into every channel. Channel n then reads $x_n = g_ne^{j\phi_n}\times(\text{tone})$. Divide by channel 1: $x_n/x_1 = (g_n/g_1)e^{j(\phi_n-\phi_1)}$. That ratio is the correction, and the unknown tone itself has cancelled. Only *differences* between channels matter for steering, so a common error is harmless.
- **What leftover errors cost.** Small random leftovers of $\sigma_\phi$ radians rms phase and $\sigma_a$ (fractional) amplitude do two things:
  - The beam peak drops by about $e^{-\sigma_\phi^2}$. This is tiny.
  - A sidelobe "floor" appears at about $(\sigma_a^2+\sigma_\phi^2)/N$ of the peak power (uniform weights). This is what spoils nulls and low sidelobes.
  So calibration targets are set by the sidelobes and nulls you need, not by the gain.

*Worked numbers (verified, `tools/verify/s18_level15_numbers.py`, including a Monte-Carlo check of the floor).* An 8-channel array left with 10° rms phase error (0.175 rad):
- **Gain:** it loses only 0.13 dB.
- **Sidelobes:** its sidelobe floor sits near 0.0305/8, i.e. **−24 dB**. That already fills the −25 dB sidelobes of a tapered design and limits nulls to about 24 dB depth.
- **After calibration:** 2° rms pushes the floor to −38 dB.

These are the numbers behind the "how good must calibration be" rule in Level 2.

### Level 2 — derivations

**(a) How good must calibration be?** Residual errors after calibration that are uncorrelated between channels create the sidelobe floor of [tapering](tapering-sidelobe-control.md) §(f): SLL_floor ≈ (σ_a² + σ_φ²)/(Nη_t). Requiring the floor to sit 10 dB below the design SLL: σ_a² + σ_φ² ≤ Nη_t·10^{(SLL−10)/10}. Splitting equally between amplitude and phase (script §4): 8 × Taylor-25 (η_t = 0.90) → 0.29 dB and 1.9°; 16 × Taylor-30 → 0.22 dB / 1.5°; 64 × Taylor-30 → 0.44 dB / 3.0°; 64 × Taylor-40 → 0.14 dB / 0.9°. Larger arrays tolerate larger per-channel errors (the floor falls as 1/N). Correlated residuals (e.g. a temperature gradient across the board) produce discrete lobes, not a floor, and need tighter control.

**(b) REV (rotating-element electric-field vector) — derivation.** All elements on, far-field probe in the calibration direction; the total field is E₀ = Σ E_n. Add a phase Δ to element n only: E(Δ) = (E₀ − E_n) + E_n e^{jΔ} = a + b e^{jΔ}. The received power is
$$P(\Delta) = |a|^2 + |b|^2 + 2|a||b|\cos(\Delta + \arg b - \arg a) \equiv A + B\cos(\Delta + \psi).$$
Fit A, B, ψ by linear least squares on the basis {1, cosΔ, sinΔ} (any ≥ 3 distinct states). Then |a|² + |b|² = A and |a||b| = B/2 give |b|² = (A − √(A² − B²))/2 and |a|² = (A + √(A² − B²))/2 — with the two roots swappable, so choose |b| < |a| (true when no single element dominates, i.e. N ≳ 3). With b/a = (|b|/|a|)e^{jψ}, the element's excitation relative to the total field is E_n/E₀ = (b/a)/(1 + b/a). Equivalently the amplitude ratio k = |b|/|a| = (√P_max − √P_min)/(√P_max + √P_min), because √P_max = |a| + |b| and √P_min = |a| − |b|. (Note: (P_max − P_min)/(P_max + P_min) = 2k/(1 + k²), not k; a recent summary [5] quotes the latter expression as the amplitude ratio — it agrees only for k ≪ 1.) Doing this for all N elements gives all channel errors up to one common complex factor; set weights w_n = target_n/ĉ_n and repeat (the fit is better once the array is near its target, because the "everything else" phasor is then well defined). Script §1 (8 elements, 1 dB / 20° true errors, Taylor-25 target): perfect measurements → exact; 6-bit states with 20 dB power SNR and 2° state errors → 0.07 dB / 0.44° after one pass, SLL −23.2 dB after three passes; 3- or 4-bit phase shifters with 4° state errors still reach −23.2…−24.2 dB. REV's known limits [5]: accuracy is bounded by the phase-shifter state accuracy (the rotation *is* the reference), the ripple depth shrinks as 1/N so large arrays need high SNR, and it calibrates only for the probe direction (coupling-induced pattern differences elsewhere remain).

**(c) Noise-source (common-signal) calibration of coherent receivers.** Inject the same wideband noise z(t) into all channels: x_n[k] = c_n z[k − τ_n] + v_n[k]. (i) *Integer delay*: the peak of the cross-correlation |Σ_k x₀*[k] x_n[k + ℓ]| over ℓ. (ii) *Fractional delay*: after removing the integer part, the cross-spectrum X₀*(f)X_n(f) ∝ e^{−j2πfτ_frac}; its phase slope gives τ_frac. Estimate the slope from the correlation between bins far apart (we use bins M/4 apart) — adjacent-bin phase differences are so small that noise biases them badly (a pitfall we hit: 0.3-sample truth estimated as −1.5 samples with adjacent bins; 0.2988 with M/4 spacing — script §2). (iii) *Complex gain*: ĉ_n/ĉ₀ = Σx₀*x_n/Σ|x₀|² after delay alignment. The phase error of (iii) for M samples with per-channel SNR s of the injected noise is
$$\sigma_\phi^2 \approx \frac{1}{2M}\left(\frac{2}{s} + \frac{1}{s^2}\right)\ \text{rad}^2,$$
confirmed by Monte Carlo: s = 20 dB, M = 1024 → 0.18°; M = 65 536 → 0.022°; s = 10 dB, M = 65 536 → 0.075° (script §2). So the *statistical* error of noise-source calibration is negligible; the *systematic* errors (antenna side, switch-path differences, element patterns) dominate. An uncorrected 0.3-sample skew at 2.4 MS/s (125 ns) is a 45° phase error at a 1 MHz baseband offset — which is why sub-sample alignment matters for wideband DOA and TDOA.

**(d) Mutual-coupling calibration — derivation and its blind spot.** Transmit from element m (channel t_m), receive on n (channel r_n): M_mn = t_m c_mn r_n, where c_mn is the element-to-element coupling. Assume (1) *translation invariance* — c depends only on the separation (true away from edges), and (2) *reciprocity* — c_mn = c_nm. Then, e.g., M_{m,m+1}/M_{m,m−1} = r_{m+1}/r_{m−1}: the receive errors of two neighbours of m, with t_m and c cancelling. A full least-squares fit (alternating updates of t, r and c) solves all of them (script §3: 1 dB / 25° errors recovered to 0.004 dB / 0.03° with −80 dB measurement noise). **Blind spot (gauge freedom)**: the substitution t_m → t_m z^m, r_n → r_n z^{−n}, c_k → c_k z^k leaves every M_mn = t_m c_{n−m} r_n unchanged; reciprocity (c_k = c_{−k}) forces z = z^{−1}, i.e. z = ±1. So the method cannot distinguish the true solution from one with **π added to every other element** (verified: zero change in all M_mn). It is resolved by an external far-field check or by assuming errors ≪ 90° (the least-squares solution started from zero phase never flipped in 20 trials). **Edge effects** violate translation invariance: perturbing the coupling of pairs involving edge elements by 10% / 30% leaves 0.18 dB / 1.6° and 0.64 dB / 4.4° rms residuals (script §3) — use dummy edge elements or exclude edge pairs. Aumann et al. also used the measured coupling to *predict* the patterns [4].

**(e) Far-field beacon with a digital array.** With a source at known direction û_c in the far field (distance ≥ 2L²/λ), the snapshot vector x = s·C·a(û_c) + v, with C = diag(c_n). The estimate ĉ_n = x_n/a_n(û_c) (averaged over many snapshots) calibrates everything in that direction, including element-pattern differences at û_c. Sweeping several beacon directions (or rotating the array on a turntable) builds a direction-dependent table, or fits a coupling matrix C_mc so that a_true(û) ≈ C_mc·a_ideal(û) for all û — the standard "array manifold calibration" for DF systems.

**(f) Self-calibration with sources of opportunity.** When the array sees several signals from unknown but distinct directions, the signal-subspace structure of the covariance can be used to estimate channel gains/phases *and* the directions together (Weiss & Friedlander's eigenstructure method [7]), at the cost of identifiability conditions (enough sources, good SNR) and local optima. Useful for arrays that can't be taken to a range.

### Level 3 — practical system issues

- **Frequency dependence**: channel errors vary with frequency (cable delay = phase slope; filter group delay). Calibrate *delay* (slope) and *phase* (offset) separately, or at each channel/subband. Pure length differences are easiest to fix as delays.
- **Temperature**: beamformer ICs drift ±2.5–3 dB in gain over −40…+85 °C (ADAR1000 data sheet [6]); coax phase drifts with temperature too. Store calibration tables indexed by temperature (on-chip sensors) or recalibrate in service with an internal network.
- **State-dependent errors**: phase shifter and attenuator states interact; a full calibration is a 2-D table over (phase code, gain code) per channel, or at least a per-state correction measured once on a VNA ([components](phase-shifters-ttd-components.md)).
- **Mutual coupling and scan**: correcting *channel* errors does not fix coupling-induced pattern changes with scan; those belong to the design (embedded patterns) or to a coupling-matrix correction in digital arrays ([coupling](planar-arrays-element-pattern-coupling.md)).
- **Calibration of TX arrays**: the same methods apply on transmit (REV with a far-field receiver; coupling method uses both directions). PA compression makes gain calibration power-dependent.

## Design equations & rules of thumb

| Rule | Validity | Value |
|---|---|---|
| Required residual: σ_a² + σ_φ² ≤ Nη_t·10^{(SLL−10)/10} | floor 10 dB below design | 8 el −25 dB: 0.29 dB/1.9° |
| REV: P(Δ) = A + B cos(Δ + ψ); \|b\|² = (A − √(A²−B²))/2 | ≥ 3 states, N ≳ 3 | 8 × 64 = 512 readings (6-bit sweep) |
| Noise-source phase error: σ_φ² = (2/s + 1/s²)/(2M) | common injected noise | 20 dB, 65 536 samples → 0.022° |
| Cable phase: 360°·ΔL/(v_f λ₀) | coax | 1 cm RG-58 (v_f 0.66) at 433 MHz: 7.9° |
| Skew phase: 360°·f_bb·Δt | sampling misalignment | 125 ns @ 1 MHz: 45° |
| Mutual-coupling cal: ambiguity = π on alternate elements | reciprocal, translation-invariant | resolve with one far-field check |
| Beacon distance ≥ 2L²/λ | far-field cal | 0.2 m at 5.8 GHz → 1.5 m |
| Recalibrate SDR arrays after every retune/re-lock | fractional-N PLLs, USB streams | automatic in KrakenSDR |

## Worked examples

**Example 1 — KrakenSDR at 433 MHz: what the noise source does and doesn't fix.** After a retune, the DAQ firmware switches the noise source into all five inputs and aligns sample delay and phase to CH0 [1]. With the noise ≈ 20 dB above the tuner noise and ≈ 65 k samples per estimate, the phase uncertainty is ≈ 0.02° (script §2) — perfect. What remains uncorrected: coax from antennas to the box (1 cm difference in RG-58-class cable, v_f ≈ 0.66: λ_cable = 0.6928 m × 0.66 = 0.457 m → 7.9° at 433 MHz, consistent with the docs' "≈7° at 400 MHz" [2]), antenna placement errors (1 cm = 5.2° of geometric phase at 433 MHz for a broadside source, more off-axis), and coupling between the whips. For bearing accuracy these systematic terms dominate: cut all five cables from one reel to the same length, and check the array against a known transmitter.

**Example 2 — REV calibration of an 8-element 5.8 GHz analog array.** Beacon horn at ≥ 2 m (far field for L ≈ 0.2 m), SDR or power meter measuring received power. For each element, step its phase shifter through 8 states (3-bit subset of its 6-bit range is enough): 64 readings; fit A, B, ψ; compute each channel's complex error; apply; repeat twice. Our simulation (script §1) shows a Taylor-25 design recovers ≈ −23 to −24 dB sidelobes, even with 4° state errors in the phase shifters. Total ≈ 200 power readings — a few minutes with Python automation.

**Example 3 — error budget for the same array.** Target −25 dB peak sidelobes with an 8-element Taylor-25: residuals ≤ 0.29 dB / 1.9° rms for a floor at −35 dB. ADAR1000-class beamformers already have 0.2 dB / 2° RMS *state* errors [6] — so after REV channel calibration, state-error calibration (per-state table) becomes the next limit if you want the full −25 dB.

**Example 4 — self-calibrating a T/R array with its own coupling.** 8-element transmit/receive array; measure all 56 ordered pairs (transmit on m, receive on n). With a 10% edge-coupling asymmetry (edges see a different environment), expect ≈ 0.2 dB / 1.6° residual — adequate for −25 dB sidelobes at N = 8 (budget 0.29 dB / 1.9°). Add terminated dummy elements at the ends to reduce the asymmetry, and do one far-field check to rule out the alternating-π ambiguity.

**Example 5 — calibrating a 2-channel Pluto interferometer.** Pluto's two RX channels share one LO, so their phase difference is stable after a tune but not zero (different paths). Split a CW beacon (or noise) with a Wilkinson into both inputs through equal cables, record the phase difference, subtract it in software; repeat after every retune (the AD9361 re-lock can move it) and after temperature changes.

## Practical notes
- **Inject as close to the antennas as possible.** Everything upstream of the injection point is uncalibrated; if you build a switch box, put it at the antenna feed, or measure the antenna-side cables with a VNA once and store their phases.
- **Use a common source at an equal distance.** For beacon calibration of a digital array place the beacon on the array boresight in the far field, and correct for the known geometry if it's off-axis.
- **Log everything**: store the calibration vectors with frequency, temperature, time, firmware version. Plot them over time — drifts reveal thermal or connector problems.
- **Beware multipath** in beacon/REV calibration outdoors: a ground reflection adds a second "plane wave" and biases the channel estimates by up to the reflection-to-direct ratio; use absorber, height, or a directive beacon.
- **Recalibrate after moving cables** — flexing coax changes phase by degrees at GHz frequencies.
- **Check calibration by scanning** a known source: the peak should land within a fraction of a beamwidth of the true angle and sidelobes should match the model.

## Common mistakes & misconceptions
- **"The noise source calibrates the whole array."** It calibrates from the injection point onward only; antenna cables, the antennas and their coupling are untouched.
- **"Calibrate once and forget."** SDR arrays need recalibration after every retune; all arrays drift with temperature and cable movement.
- **"Shared 10 MHz reference = calibrated."** It gives frequency lock, not phase or timing alignment.
- **"REV needs a phase-measuring receiver."** It is power-only — that's its point — but its accuracy is limited by the phase-shifter state accuracy.
- **Estimating fractional delay from adjacent-bin phase differences** — too noise-sensitive; use widely separated bins or fit the unwrapped phase with weights.
- **Using mutual-coupling calibration without checking the parity ambiguity** — the method cannot see a π flip on alternate elements.
- **Calibrating in the near field** of the array (closer than 2L²/λ) and applying the result to far-field beams — the per-element path lengths differ by more than the calibration accuracy.

## How to simulate / verify
- `tools/verify/array_calibration.py` (~20 s): REV simulation with noise and phase-shifter state errors (estimation accuracy and sidelobe recovery), noise-source phase-error formula vs Monte Carlo, integer/fractional delay estimation (robust long-lag slope), mutual-coupling least-squares calibration with edge perturbations and the ±1 gauge check, accuracy budget table.
- Hardware: two coherent channels (Pluto, B210, KrakenSDR) + a Wilkinson splitter + a noise source (a cheap wideband amplified noise diode) reproduce the noise-source method; a far-field beacon and a turntable reproduce beacon/pattern calibration ([OTA testing](../17-test-measurement/antenna-range-ota-testing.md)).

## Open questions / gaps
- The original Mano & Katagi paper and the 2023 MDPI method-comparison paper (Electronics 12(3):489) were not accessible (abstract / 403); REV equations here are re-derived. The exact form of the classic "k and X" solution formulas was not checked against the original.
- KrakenSDR's Heimdall DAQ internals (how often it re-checks calibration, thresholds) were not documented on the pages read; statements rely on the KrakenSDR wiki and Crowd Supply descriptions.
- Near-field (holographic back-projection) calibration is described only qualitatively; no worked example.

## Sources
1. KrakenRF, *KrakenSDR documentation wiki*, github.com/krakenrf/krakensdr_docs/wiki (Home; Web Interface Controls) and Crowd Supply KrakenSDR page — software-activated noise source with switches, correlation against CH0, automatic coherence calibration on frequency change. (vendor docs)
2. KrakenRF, KrakenSDR wiki "04. Antenna Array Setup" — cable lengths identical within 1 cm up to ≈900 MHz; ≈14° at 800 MHz / ≈7° at 400 MHz per cm. (vendor docs)
3. S. Mano, T. Katagi, "A method for measuring amplitude and phase of each radiating element of a phased array antenna," *Electronics and Communications in Japan* 65-B(5):58–64, 1982 — REV method. (peer-reviewed; abstract read)
4. H. M. Aumann, A. J. Fenn, F. G. Willwerth, "Phased array antenna calibration and pattern prediction using mutual coupling measurements," *IEEE Trans. Antennas Propag.* 37(7):844–850, 1989. (peer-reviewed; abstract read)
5. "Phased array calibration based on rotating-element harmonic electric-field vector with time modulation," arXiv:2504.16107, 2025 — summary of classic REV power expression, amplitude-ratio formula and limitations (≥ 3 states, phase-shifter accuracy, amplitude ambiguity, noise sensitivity vs N). (preprint)
6. Analog Devices, *ADAR1000* data sheet Rev. B — RMS gain/phase error 0.2 dB/2°, gain drift vs temperature, on-chip temperature sensor. (datasheet)
7. A. J. Weiss, B. Friedlander, "Eigenstructure methods for direction finding with sensor gain and phase uncertainties," *Circuits, Systems and Signal Processing* 9(3):271–300, 1990 — self-calibration. (peer-reviewed; cited from standard DOA literature, not read)
8. R. J. Mailloux, *Phased Array Antenna Handbook*, 2nd ed., 2005, ch. 7 (array error effects) — tolerance/error budgets. (textbook)
9. M. Lichtman, *PySDR* "Hands-on with Phaser" — Phaser per-channel phase/gain calibration files. (tutorial)
10. `tools/verify/array_calibration.py` — all numbers marked "script". (own verification)
