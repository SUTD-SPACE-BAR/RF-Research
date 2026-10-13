---
title: Radar tracking — sequential lobing, conical scan, amplitude/phase monopulse, range and Doppler gates, α-β/Kalman trackers, gating and data association, and tracking a rocket (radar or GNSS-cued antenna)
domain: 11-radar
slug: radar-tracking-monopulse-and-trackers
tags: [tracking-radar, monopulse, amplitude-comparison, phase-comparison, sum-difference, monopulse-slope, sequential-lobing, conical-scan, crossover-loss, angle-accuracy, beam-splitting, split-gate, early-late-gate, range-gate, velocity-gate, servo, track-while-scan, alpha-beta, kalman-tracker, polar-to-cartesian, gating, mahalanobis, nearest-neighbour, pda, jpda, mht, track-initiation, m-of-n, rocket-tracking, antenna-tracker, gnss-pointing, yagi, rssi-step-track]
prerequisites:
  - ../00-math-foundations/kalman-filter-and-state-estimation.md
  - ../00-math-foundations/estimation-theory-ml-map-crb.md
  - detection-theory-cfar.md
  - radar-range-equation.md
related:
  - ambiguity-function-waveforms.md
  - diy-radar-hardware.md
  - cw-and-doppler-radar.md
  - fmcw-radar.md
  - ../12-phased-arrays/tapering-sidelobe-control.md
  - ../12-phased-arrays/adaptive-beamforming-doa.md
  - ../12-phased-arrays/beamforming-architectures.md
  - ../06-rf-circuits/couplers-dividers-combiners.md
  - ../20-projects-recipes/ground-station-tracking-yagi.md
  - ../15-lora-ism-radios/ground-station-design.md
  - ../21-gnss/gnss-on-rockets-dynamics-and-limits.md
level: mixed
confidence: high
last_updated: 2026-10-03
---

# Radar tracking — monopulse, gates, trackers and data association

## Questions this page answers
- How does a tracking radar measure angle more finely than its beamwidth?
- What are sequential lobing, conical scan and monopulse, and why did monopulse win?
- How do sum and difference (Σ/Δ) beams work, and what is the "monopulse slope"?
- How accurate is monopulse angle measurement for a given SNR and beamwidth?
- What is the difference between amplitude-comparison and phase-comparison monopulse?
- How does a split-gate (early–late) range tracker work?
- How do α-β and Kalman trackers fit into a radar, and how do I convert range/azimuth to x/y?
- What is gating, and what are nearest-neighbour, PDA, JPDA and MHT association?
- Can I track my rocket with a ground radar or an antenna tracker, and how fast must it slew?
- How do I point a telemetry Yagi at a rocket from its downlinked GNSS, and how much does latency matter?
- Is RSSI-based "step tracking" of a LoRa signal good enough to point an antenna?

## TL;DR
- **Angle tracking = comparing two or more beams.** Sequential lobing and conical scan compare beams *in time* (several pulses), so target fluctuation between pulses corrupts the angle (20 % pulse-to-pulse fluctuation → 0.063 beamwidth error with no noise at all; monopulse: zero). **Monopulse** compares them *simultaneously* on every pulse, so it is immune to amplitude fluctuation.
- **Amplitude monopulse:** two beams squinted by ±θ_s, combined by a hybrid into Σ = (v₁+v₂)/√2 and Δ = (v₁−v₂)/√2. For Gaussian beams of width θ_b, exactly $\Delta/\Sigma=\tanh(4\ln2\,\theta\theta_s/\theta_b^2)$; near boresight $\Delta/\Sigma\approx k_m\theta/\theta_{3\Sigma}$. The normalised **monopulse slope** $k_m$ is 1.0–2.2 for squints of 0.3–0.5 θ_b (1.44 at 0.4 θ_b, Gaussian beams; 1.62 for the optimum uniform aperture per Sandia), at a one-way crossover loss of $12.04(\theta_s/\theta_b)^2$ dB.
- **Accuracy:** $\sigma_\theta\approx\dfrac{\theta_{3\Sigma}}{k_m\sqrt{2\,\mathrm{SNR}_\Sigma}}$ (MC: ratio 1.014); about **10:1 beam splitting at 13 dB SNR**, $\theta/(2.2\sqrt{\rm SNR})$ as a rule of thumb. Phase monopulse (two apertures, $\Delta/\Sigma=j\tan(kd\sin\theta/2)$) gives the same accuracy for the same aperture and reaches the array CRB (MC: 1.005).
- **Range tracking:** early and late gates straddle the matched-filter peak; for a rectangular pulse the discriminator $(L-E)/(L+E)=2\varepsilon/T$ is exactly linear over ±T/2. Doppler (velocity) gates do the same in frequency. Gates close a loop — usually an α-β or Kalman tracker.
- **Trackers:** α-β (fixed gain, steady-state Kalman — Kalata's tracking index), α-β-γ, or Kalman/EKF in Cartesian coordinates with converted measurements: cross-range σ = R·σ_θ (20 m at 10 km for 2 mrad); conversion bias $R\sigma_\theta^2/2$ is negligible unless σ_θ is large.
- **Gating and association:** accept measurements with Mahalanobis distance $\boldsymbol\nu^T\mathbf S^{-1}\boldsymbol\nu<\gamma$ (9.21 for 99 %, 2-D). Expected false measurements per gate = clutter density × gate area. With 0.8 false per gate, nearest-neighbour lost 24 % of tracks in 60 scans and PDA 4.3 %; with 4 per gate, 79 % vs 47 % (MC).
- **Rocket geometry:** peak elevation rate ≈ v/d for a station d from the pad: 28.6°/s at 500 m, 2.9°/s at 5 km for 250 m/s. A DIY 1.2 m S-band dish (5.8° beam) with monopulse at 15 dB measures angle to 0.46° (8 m at 1 km).
- **GNSS-cued antenna pointing:** with 5 Hz telemetry and 0.6 s latency, pointing at the last reported position errs by 5.1° (p95) at 1 km; extrapolating with the reported velocity cuts it to 1.0°, a constant-acceleration Kalman predictor to **0.26°** — pointing loss $12.04(\varepsilon/\theta_3)^2$ dB is then negligible for any Yagi. **RSSI step-tracking** is poor (≈ 7° per measurement pair for a 40° beam with 1.5 dB RSSI noise).

## Intuition (no math)
A search radar asks "is anything there?". A tracking radar asks "exactly where is it, and where will it be next?". Two problems are mixed together: **measuring** angle, range and Doppler on each look (a parameter-estimation problem), and **filtering** those measurements into a smooth track and a prediction (a state-estimation problem), with the extra difficulty of deciding which echo belongs to which target (data association).

**Measuring angle finer than a beamwidth.** A single beam tells you only that the target is somewhere inside it. But if you have two overlapping beams squinted slightly left and right, a target exactly in the middle returns equal signals in both, a target a little to the left returns more in the left beam. The *imbalance* tells you the direction and size of the pointing error — like judging a sound's direction from which ear hears it louder. Early radars did this by switching one beam between two positions (sequential lobing) or spinning a squinted beam around the axis (conical scan): the echo's amplitude is then modulated, and the phase of that modulation tells you which way to steer. The weakness is time: if the target's echo strength changes between looks (it always does — targets scintillate), the radar mistakes that change for an angle error.

**Monopulse** fixes this by forming both beams at once from the same pulse — hence "mono" pulse. A microwave hybrid adds the two beam outputs (the sum, Σ, a normal beam) and subtracts them (the difference, Δ, which has a sharp null on boresight). The ratio Δ/Σ is zero on boresight and grows linearly with the angle error, with a sign that says which side. Because Δ and Σ come from the same echo, fluctuations cancel in the ratio. The noise in Δ sets the accuracy, which improves as $1/\sqrt{\rm SNR}$: at a typical detection SNR of 13 dB, angle is measured to about a tenth of the beamwidth.

**Range and Doppler** are tracked the same way: two gates slightly early and late in time (or slightly low and high in frequency) straddle the echo; their imbalance steers the gate.

**Then filtering.** Each measurement is noisy; the tracker blends them with a motion model (constant velocity, constant acceleration) — exactly the α-β or Kalman filter of the [Kalman page](../00-math-foundations/kalman-filter-and-state-estimation.md). Its prediction tells the radar where to look next and how big a "gate" to accept echoes in. With clutter, several echoes may fall in the gate: take the closest (nearest neighbour), or blend them weighted by their probability of being the target (PDA).

**For a rocket**, the hard part is not measurement but geometry: it climbs fast and close, so the antenna must slew quickly; a narrow beam loses it immediately unless it is cued — and the best cue is the rocket's own GNSS position in the telemetry, predicted forward by a Kalman filter to cancel the telemetry latency.

## The math

### Level 1 — beams, ratios and gates

Let $v(\theta)$ be the voltage pattern of a beam with half-power width $\theta_b$. A Gaussian approximation of the main lobe is $v(\theta)=\exp(-2\ln2\,\theta^2/\theta_b^2)$ (power $v^2$ is half at $\theta=\theta_b/2$). Two beams squinted at $\pm\theta_s$ receive $v_1=v(\theta-\theta_s)$ and $v_2=v(\theta+\theta_s)$ from a target at angle θ.
- **Sequential lobing/conical scan:** compare $v_1$ and $v_2$ on successive pulses; error signal ∝ $v_1-v_2$.
- **Monopulse:** form $\Sigma=(v_1+v_2)/\sqrt2$ and $\Delta=(v_1-v_2)/\sqrt2$ simultaneously (a lossless 180° hybrid — rat-race or magic-T, see [couplers](../06-rf-circuits/couplers-dividers-combiners.md)); the angle estimate is $\hat\theta=\frac{\theta_{3\Sigma}}{k_m}\mathrm{Re}\{\Delta/\Sigma\}$.
- **Range gate:** sample the matched-filter output at $t_0-T/2$ (early, E) and $t_0+T/2$ (late, L); steer $t_0$ to make $E=L$.
- **Crossover loss:** a squinted beam is down by $12.04(\theta_s/\theta_b)^2$ dB on boresight (one way; doubled for transmit+receive on the same squinted beam, as in conical scan) — 1.93 dB at $\theta_s=0.4\theta_b$.

### Level 2 — lobing, conical scan and monopulse derived; accuracy; range and Doppler gates

**Gaussian-beam monopulse ratio (exact).** $\frac{v_1}{v_2}=\exp\!\big(-\tfrac{2\ln2}{\theta_b^2}[(\theta-\theta_s)^2-(\theta+\theta_s)^2]\big)=e^{8\ln2\,\theta\theta_s/\theta_b^2}$, so
$$\frac{\Delta}{\Sigma}=\frac{v_1/v_2-1}{v_1/v_2+1}=\tanh\!\Big(\frac{4\ln2\,\theta\,\theta_s}{\theta_b^2}\Big)\quad(\text{verified to }10^{-16}).$$
The ratio is odd in θ, independent of target amplitude and phase, linear near boresight with slope $4\ln2\,\theta_s/\theta_b^2$ per radian, and saturates (monotonic, so still invertible by arctanh) further out. Expressed per sum-beam width, $k_m=4\ln2\,(\theta_s/\theta_b)(\theta_{3\Sigma}/\theta_b)$:

| Squint θ_s/θ_b | Sum-beam width θ₃Σ/θ_b | $k_m$ (per θ₃Σ) | Crossover loss (one way) |
|---|---|---|---|
| 0.3 | 1.148 | 0.95 | 1.08 dB |
| 0.4 | 1.302 | 1.44 | 1.93 dB |
| 0.5 | 1.560 | 2.16 | 3.01 dB |
| 0.6 | 1.943 | 3.23 | 4.33 dB |

(Computed for Gaussian beams.) More squint gives more slope but a broader, weaker sum beam (lower SNR and gain) — the optimum for Σ on transmit and receive is $\theta_s=\theta_b/\sqrt{8\ln2}=0.425\,\theta_b$ (Worked example 2). For a uniformly illuminated aperture split into squinted beams, Doerry and Bickel find the optimum squint 0.415 λ/D with $k_m$ = 1.62 V/V/beamwidth and $\sigma_\theta\approx\theta_g/(2.19\sqrt{\rm SNR})$ [3]; textbooks quote $k_m$ ≈ 1.2–2 depending on feed and normalisation [1], [2]. **Always state which beamwidth $k_m$ is normalised to.**

**Two-axis monopulse.** A four-horn (or four-quadrant array) feed with outputs A (top-left), B (top-right), C (bottom-left), D (bottom-right) forms $\Sigma=A+B+C+D$, $\Delta_{az}=(A+C)-(B+D)$, $\Delta_{el}=(A+B)-(C+D)$ (and an unused diagonal $A+D-B-C$ that is terminated). The receiver needs three phase-matched channels (or time-shares Δ channels); the detector forms $\mathrm{Re}\{\Delta\Sigma^*\}/|\Sigma|^2$, which needs Σ and Δ phase-aligned — channel phase mismatch rotates part of Δ into the quadrature (Im) output and reduces the effective slope by $\cos\phi_{err}$. Phased arrays form Σ and Δ in the beamformer with separate tapers: Taylor for Σ, **Bayliss** for Δ to keep difference sidelobes low ([tapering](../12-phased-arrays/tapering-sidelobe-control.md)).

**Phase-comparison monopulse.** Two identical apertures (or array halves) with phase centres $d$ apart receive $a_{1,2}=e^{\pm jkd\sin\theta/2}$. Then
$$\frac{\Delta}{\Sigma}=\frac{a_1-a_2}{a_1+a_2}=j\tan\frac{kd\sin\theta}{2}\quad(\text{verified}),$$
purely imaginary; the angle is read from the phase difference $\arg(x_1x_2^*)=kd\sin\theta$. Unambiguous only for $|kd\sin\theta|<\pi$; if $d>\lambda/2$ (typical — the halves are many wavelengths across), the ambiguity is resolved by the sum beam's width. Amplitude and phase monopulse are equivalent in accuracy for the same total aperture [3]; dishes favour amplitude (squinted feed horns), flat arrays favour phase (array halves).

**Angle accuracy (thermal noise).** With independent noise of equal power σ² in the Σ and Δ channels (the hybrid is lossless and orthogonal), $\mathrm{Re}\{\Delta/\Sigma\}$ near boresight has error ≈ $\mathrm{Re}\{n_\Delta/\Sigma\}$ of variance $\sigma^2/(2|\Sigma|^2)=1/(2\,\mathrm{SNR}_\Sigma)$. Dividing by the slope:
$$\boxed{\sigma_\theta\approx\frac{\theta_{3\Sigma}}{k_m\sqrt{2\,\mathrm{SNR}_\Sigma}}}\qquad(\text{MC at 20 dB, Gaussian beams: measured/formula = 1.014}).$$
SNR is the *sum-channel* SNR (not a single beam's). Integrating $N$ pulses (or averaging $N$ estimates) multiplies the SNR by $N$. At 13 dB, $\sigma_\theta/\theta_{3\Sigma}=1/(1.44\sqrt{40})$ = 0.110 — the classic "10:1 beam splitting at detection threshold" [4]. For phase monopulse with per-element SNR $\rho_e$: $\mathrm{var}(\sin\hat\theta)=1/(\rho_e(kd)^2)$, exactly the two-element case of the array [DOA Cramér–Rao bound](../12-phased-arrays/adaptive-beamforming-doa.md) $6/(\rho_e(kd)^2N(N^2-1))$ with N = 2 (MC: 1.005). This is the angular counterpart of the delay CRB on the [estimation page](../00-math-foundations/estimation-theory-ml-map-crb.md): aperture plays the role of bandwidth.

**Sequential lobing and conical scan.** In conical scan a single beam, squinted by θ_s, rotates about the boresight axis at the scan rate. A target at offset ε in direction $\phi_t$ sees the beam at distance $\psi^2=\varepsilon^2+\theta_s^2-2\varepsilon\theta_s\cos(\phi-\phi_t)$, so the echo amplitude is $\propto\exp(4\ln2\,\varepsilon\theta_s\cos(\phi-\phi_t)/\theta_b^2)\approx1+m\cos(\phi-\phi_t)$ with modulation depth
$$m=\frac{4\ln2\,\theta_s\,\varepsilon}{\theta_b^2}\quad(\text{verified: 0.05543 vs 0.05545}),$$
the same slope as monopulse, and the modulation **phase** gives the error direction (verified: 30°). The error signal is extracted by synchronous detection against the scan reference (sine and cosine) and drives the azimuth and elevation servos [4]. Drawbacks: it needs several pulses per scan, so any echo amplitude variation at frequencies near the scan rate — target scintillation, propeller modulation, or deliberate *inverse-gain jamming* — is indistinguishable from angle error (MC: 20 % rms pulse-to-pulse fluctuation, 8 positions per scan, no noise → 0.063 θ_b rms error; monopulse → 4×10⁻¹⁸); and the transmit beam is also squinted, so the two-way crossover loss applies. Variants (COSRO/LORO: conical scan on receive only) hide the scan rate from a jammer.

**Range tracking — split gate.** The matched-filter output of a rectangular pulse of width $T$ is a triangle $1-|t|/T$. Gates at $\pm T/2$ about the gate centre, with the echo peak offset by ε:
$$E=\tfrac12-\tfrac{\varepsilon}{T},\quad L=\tfrac12+\tfrac{\varepsilon}{T}\;\Rightarrow\;\frac{L-E}{L+E}=\frac{2\varepsilon}{T}\quad(|\varepsilon|<T/2;\ \text{verified}).$$
Normalising by $L+E$ removes amplitude dependence (an AGC'd discriminator). This is the same early–late structure as a GNSS DLL or a symbol-timing loop ([GNSS tracking](../21-gnss/gnss-receiver-architecture-acquisition-tracking.md), [synchronisation](../10-comms-modulation/synchronization-carrier-timing.md)); its noise floor is set by the delay CRB (rms bandwidth). Digital radars implement it as sub-sample interpolation of the range-profile peak.

**Doppler (velocity) gate.** A narrow filter (or FFT bin pair) straddling the echo Doppler gives a frequency discriminator; the loop tracks radial velocity and provides clutter rejection (the target sits in a clean Doppler cell). Frequency accuracy follows the tone CRB (rms duration), ~$1/(2\pi T_{rms}\sqrt{2\,\mathrm{SNR}})$.

**Angle servo.** The angle error drives a type-2 servo (zero steady-state error to constant angular velocity), whose bandwidth is the same noise-vs-lag trade as a PLL or α-β filter: noise jitter ∝ $\sqrt{B_n}$, lag to angular acceleration $\ddot\theta/\omega_n^2$ [4].

### Level 3 — tracking filters, coordinates, gating, association, rocket and telemetry trackers

**Track filters in a radar.** The measurement vector is $\mathbf z=[R,\ \theta_{az},\ \theta_{el},\ (\dot R)]$ with independent errors set by the CRBs above. Options:
1. **Decoupled α-β per coordinate** (range, azimuth, elevation) with Kalata gains — cheap, used in classic track-while-scan (TWS) systems; but straight-line motion is curved in polar coordinates, so it lags crossing targets.
2. **Cartesian Kalman filter with converted measurements.** Convert $(R,\theta)$ to $(x,y)$ and use the converted covariance $\mathbf R_{xy}=\mathbf J\,\mathrm{diag}(\sigma_R^2,\sigma_\theta^2)\mathbf J^T$, $\mathbf J=\partial(x,y)/\partial(R,\theta)$ (MC agreement 0.06 %); the cross-range std is $R\sigma_\theta$ — at 10 km with 2 mrad, **20 m**, vs 5 m along range: the error ellipse is long and thin, and rotates with the target's bearing, so R must be recomputed every scan. The naive conversion is biased by $\approx R\sigma_\theta^2/2$ along range (0.02 m here — negligible; it matters for $R\sigma_\theta^2\gtrsim\sigma_R$, e.g. long-range bearing-only sensors); debiased conversions exist [7].
3. **EKF/UKF with polar measurements directly** ($\mathbf h(\mathbf x)=[\sqrt{x^2+y^2},\ \mathrm{atan2}(x,y)]$) — standard for radars with Doppler.
Kinematic model: CV (DWNA) for cruising targets, CA or Singer for manoeuvres, IMM to switch between them (rockets: boost / coast / descent).

**Track initiation and maintenance.** Detections ("plots") pass a CFAR threshold ([detection](detection-theory-cfar.md)); a tentative track starts from one or two unassociated plots (two-point initialisation gives position and velocity with known covariance), is **confirmed** after M detections in N scans (e.g. 2-of-3 or 3-of-5) and **deleted** after several consecutive misses. The binary M-of-N logic converts a per-cell false-alarm probability into a much lower false-track rate.

**Gating.** With innovation $\boldsymbol\nu=\mathbf z-\mathbf H\hat{\mathbf x}^-$ and covariance $\mathbf S$, the Mahalanobis distance $d^2=\boldsymbol\nu^T\mathbf S^{-1}\boldsymbol\nu$ is $\chi^2_m$ for the true target. Accept if $d^2<\gamma$; the gate probability $P_G=F_{\chi^2_m}(\gamma)$: γ = 9.21 for $P_G$ = 0.99 (m = 2). Gate volume $V=c_m\gamma^{m/2}\sqrt{\det\mathbf S}$ ($c_2=\pi$, $c_3=4\pi/3$); expected false measurements per gate $=\lambda_cV$ for clutter density $\lambda_c$ (per m² here). Larger S (long prediction, coasting, high Q) → larger gate → more clutter accepted — the reason trackers degrade during missed detections.

**Data association** [5], [6], [7].
- **Nearest neighbour (NN):** use the in-gate measurement with smallest $d^2$; treat it as certain. Simple; fails in clutter because a false plot occasionally wins and the filter, believing it, moves the gate away from the target.
- **Global nearest neighbour (GNN):** for many tracks, solve the assignment problem (Hungarian/auction) minimising total $d^2$ so two tracks cannot take the same plot.
- **PDA (probabilistic data association)** [5]: update with *all* validated measurements weighted by their association probabilities. With Poisson clutter, $e_i=\exp(-d_i^2/2)$, $b=\lambda_c\sqrt{\det(2\pi\mathbf S)}\,\frac{1-P_DP_G}{P_D}$, $\beta_i=\frac{e_i}{b+\sum e_j}$, $\beta_0=\frac{b}{b+\sum e_j}$ (none correct). Combined innovation $\boldsymbol\nu=\sum\beta_i\boldsymbol\nu_i$, $\hat{\mathbf x}=\hat{\mathbf x}^-+\mathbf K\boldsymbol\nu$, and
$$\mathbf P=\beta_0\mathbf P^-+(1-\beta_0)(\mathbf I-\mathbf K\mathbf H)\mathbf P^-+\mathbf K\Big[\sum\beta_i\boldsymbol\nu_i\boldsymbol\nu_i^T-\boldsymbol\nu\boldsymbol\nu^T\Big]\mathbf K^T ,$$
the last term inflating P to reflect association uncertainty. **JPDA** extends it to several nearby targets sharing measurements; **MHT** (multiple-hypothesis tracking) keeps alternative association histories and decides later — best and most expensive.
- **MC comparison** (2-D CV target, T = 1 s, σ_w = 0.5 m/s², σ_v = 10 m, $P_D$ = 0.9, 99 % gate, 60 scans, 300 runs; steady-state gate area ≈ 3970 m²):

| Clutter density | false per gate | NN track loss | PDA track loss | rms error (kept tracks) NN / PDA |
|---|---|---|---|---|
| 2×10⁻⁵ m⁻² | 0.08 | 0.7 % | 0.3 % | 8.8 / 8.2 m |
| 2×10⁻⁴ m⁻² | 0.79 | 24 % | 4.3 % | 17.5 / 10.3 m |
| 1×10⁻³ m⁻² | 3.97 | 79 % | 47 % | 43 / 37 m |

Rule: keep $\lambda_cV\lesssim0.1$ for NN (by CFAR threshold, Doppler filtering of clutter, or smaller gates); above that, use PDA/JPDA; above a few per gate, reduce clutter at the signal-processing level — no association logic survives it for long.

**Tracking a rocket with a ground radar.** Geometry dominates. For a vertical climb at speed $v$ seen from horizontal distance $d$, elevation $\theta=\arctan(h/d)$ changes at $\dot\theta=vd/(d^2+h^2)$, peaking at $v/d$ near the pad: **28.6°/s at d = 500 m, 2.9°/s at 5 km** for 250 m/s (verified; see [DIY radar](diy-radar-hardware.md) for the full geometry). The DIY S-band design of [range-equation Example D](radar-range-equation.md) (1.2 m dishes, 5.8° beam, ~5 km for 0.01 m² at 15 dB) would, with a monopulse feed and $k_m$ ≈ 1.6, measure angle to $5.8°/(1.6\sqrt{63})$ = **0.46°** — 8 m at 1 km — and range to well under a metre (delay CRB, [ambiguity page](ambiguity-function-waveforms.md)). The practical architecture: acquire with a **cue** (pad position + launch time, then the rocket's GNSS telemetry), close the angle loop on monopulse once the echo is in the beam, run a Kalman tracker in ENU with an IMM (boost / coast), and use the radar's range and Doppler as **independent truth** for the flight computer's estimator — the team's validation ethos. Doppler alone (a fixed, upward-looking CW radar near the rail) is the easiest first step ([CW and Doppler](cw-and-doppler-radar.md)).

**RF-telemetry ground-station tracking (pointing a Yagi from GNSS telemetry).** No radar is needed when the rocket reports its own position. Pipeline: decode packet → GNSS position/velocity (+ fix time) → convert geodetic to local ENU at the station → **predict** to the time the antenna will actually be pointing (fix age + LoRa airtime + processing + rotator response) → az/el → rotator or operator display. Error budget:
- **Pointing loss** of a Gaussian main beam: $L=12.04(\varepsilon/\theta_3)^2$ dB (0.75 dB at a quarter beamwidth, 3 dB at half; verified).
- **GNSS position error** (≈ 2–5 m) → angle error ≈ σ/range: 0.05° at 3 km — negligible.
- **Latency**: pointing at a stale position errs by roughly (angular rate × latency). Simulated ascent (60 m/s² for 2.5 s, apogee 738 m, 10 m/s drift), telemetry 5 Hz with 3 m / 0.3 m/s noise and 0.6 s latency:

| Station distance | peak el. rate | last fix (p95 / max) | + velocity extrapolation | CA Kalman predictor |
|---|---|---|---|---|
| 1 km | 8.3°/s | 5.1° / 5.9° | 1.0° / 1.4° | **0.26° / 0.96°** |
| 5 km | 1.7°/s | 1.1° / 1.2° | 0.21° / 0.27° | 0.06° / 0.21° |

With a 40° Yagi even the worst raw case costs < 0.3 dB; the binding constraints are **rotator slew rate** (a G-5500-class elevation drive at ≈ 2.7°/s cannot follow 8°/s — see the [ground-station recipe](../20-projects-recipes/ground-station-tracking-yagi.md)), **telemetry dropouts** during boost (bridge them by predicting with a ballistic/IMM model), and the near-pad overhead pass (keyhole at high elevation for az/el mounts). Narrow beams (dishes, 11-element Yagis, S-band radar) make the predictor essential.
- **RSSI step-tracking** (sequential lobing on the received signal strength): offsetting the antenna by ±δ and comparing RSSI gives a dB difference $4\cdot12.04\,\varepsilon\delta/\theta_3^2$; with θ₃ = 40°, δ = 10° and 1.5 dB RSSI noise (quantisation, fading, packet-to-packet variation) the error is **≈ 7° per pair** — and the offsets themselves cost 0.75 dB. It is a fallback when telemetry position is lost, not a primary method. A true monopulse ground station (two Yagis + hybrid, or two coherent SDR channels doing phase comparison — [DOA](../12-phased-arrays/adaptive-beamforming-doa.md)) would track the RF itself on every packet.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| Gaussian beams: $\Delta/\Sigma=\tanh(4\ln2\,\theta\theta_s/\theta_b^2)$ | main lobe | |
| $k_m=4\ln2\,(\theta_s/\theta_b)(\theta_{3\Sigma}/\theta_b)$ | per sum-beam width | 1.44 at θ_s = 0.4 θ_b |
| crossover loss $12.04(\theta_s/\theta_b)^2$ dB one way | Gaussian beam | 1.9 dB at 0.4 |
| $\sigma_\theta=\theta_{3\Sigma}/(k_m\sqrt{2\,\mathrm{SNR}_\Sigma})$ | thermal noise, near boresight | 13 dB → θ/9 to θ/10 |
| rule of thumb $\sigma_\theta\approx\theta/(2.2\sqrt{\rm SNR})$ | optimum squint, uniform aperture [3] | |
| phase monopulse $\Delta/\Sigma=j\tan(kd\sin\theta/2)$; var(u) = 1/(ρ_e (kd)²) | 2 apertures | = array CRB, N = 2 |
| conical-scan depth $m=4\ln2\,\theta_s\varepsilon/\theta_b^2$ | small ε | |
| split gate $(L-E)/(L+E)=2\varepsilon/T$ | rect pulse, ±T/2 gates | 1 µs → linear ±75 m |
| cross-range σ = R σ_θ; conversion bias ≈ Rσ_θ²/2 | polar → Cartesian | 10 km, 2 mrad → 20 m / 0.02 m |
| gate: $d^2<\gamma$, γ = 9.21 (2-D, 99 %) | | |
| false per gate $\lambda_cV$, $V=\pi\gamma\sqrt{\det\mathbf S}$ (2-D) | Poisson clutter | NN OK if ≲ 0.1 |
| peak elevation rate ≈ $v/d$ | vertical climb, station at d | 250 m/s, 500 m → 28.6°/s |
| pointing loss $12.04(\varepsilon/\theta_3)^2$ dB | Gaussian main beam | ¼ beam → 0.75 dB |

## Worked examples

**1. Monopulse accuracy for a DIY S-band rocket tracker.** 1.2 m dish at 3 GHz, θ₃ ≈ 5.8°, sum-channel SNR 15 dB (31.6), $k_m$ ≈ 1.6: $\sigma_\theta=5.8°/(1.6\sqrt{63.2})$ = **0.456°** = 7.96 mrad → **8.0 m** cross-range at 1 km. Integrating 10 pulses (+10 dB) gives 0.144° (2.5 m). Compare range: a 10 MHz chirp at the same SNR gives ~1 m (CRB). So the error ellipse is wider than it is long, and the Kalman tracker's R must be anisotropic and rotate with the line of sight.

**2. Choosing the squint.** With Gaussian beams and the sum beam used on both transmit and receive, the angle noise scales as $1/(\text{slope}\times|\Sigma(0)|^2)$ with slope $\propto\theta_s$ and $|\Sigma(0)|^2\propto e^{-4\ln2\,\theta_s^2/\theta_b^2}$. Maximising $\theta_se^{-4\ln2\,\theta_s^2/\theta_b^2}$ gives the optimum $\theta_s=\theta_b/\sqrt{8\ln2}$ = **0.425 θ_b** — close to Sandia's 0.415 for a uniform aperture [3]. The optimum is shallow: going from 0.4 to 0.5 θ_b raises the slope by 1.9 dB but costs 4.3 dB of two-way SNR (2.2 dB in √SNR), a net −0.23 dB; 0.4 θ_b is only 0.03 dB from optimum and 0.5 θ_b 0.26 dB (verified). So designs cluster at θ_s ≈ 0.4 θ_b, with $k_m$ ≈ 1.4–1.6 depending on pattern and normalisation.

**3. Conical scan vs monopulse on a scintillating target.** A target whose echo amplitude varies 20 % rms from pulse to pulse, eight pulses per scan, no receiver noise: conical scan's angle error is **0.063 θ_b rms** (for a 5.8° beam, 0.37° — comparable to the thermal error at 15 dB); monopulse's is zero because Σ and Δ fluctuate together. Drones and rockets with spinning or vibrating parts make this real.

**4. Range-gate discriminator for a 1 µs pulse.** $T$ = 1 µs → gates ±0.5 µs; discriminator $2\varepsilon/T$ is linear for |ε| < 0.5 µs, i.e. ±75 m of range error, slope 2 per µs (0.013 per metre). Beyond that the gate loses the target and must re-acquire.

**5. Gating in clutter.** A 2-D tracker with steady-state innovation covariance giving a 99 % gate of 3970 m², in clutter of 2×10⁻⁴ false plots per m², accepts 0.79 false plots per scan on average. Over 60 scans, nearest neighbour lost 24 % of tracks; PDA lost 4.3 % with rms error 10.3 m vs 17.5 m. Cutting clutter by 10× (stricter CFAR, Doppler filtering) brings both to < 1 % — fix clutter in the signal processing first.

**6. Pointing the telemetry Yagi.** From 1 km, with 0.6 s total latency, aiming at the last reported fix gives up to 5.9° error (0.26 dB loss for a 40° Yagi, 1.2 dB for a 20° beam); with a CA Kalman predictor ≤ 1° (≤ 0.03 dB). Recommendation: always predict to "now + rotator delay", log the commanded and actual pointing with the packets, and size the rotator for the near-pad elevation rate (≈ v/d) or stand further back.

## Practical notes
- **Phase-match the Σ and Δ channels** (cables, LNAs, filters) and calibrate with a boresight source; a channel phase error φ scales the slope by cos φ and puts part of the angle signal in quadrature. Check the Δ null depth on a range — it sets the boresight bias.
- **Low-elevation multipath** (ground reflection) corrupts elevation monopulse within about a beamwidth of the horizon — the image target causes large biases and "nodding"; GNSS-cued tracking does not have this problem.
- **Glint** (angle noise from extended targets) scales with target size; for a rocket at km range it is negligible, for a drone at tens of metres it is not.
- **Servo and mount**: rotator backlash, encoder resolution and wind loading often exceed the RF angle error; log encoder angles.
- **Time-stamp everything** (detections, GNSS fixes, rotator angles) on a common clock (GNSS PPS); latency compensation is only as good as the timestamps.
- **For the ground station**, prefer a fixed or hand-pointed wide beam near the pad and a predictor-driven narrow beam far away; plan the keyhole (overhead pass) and the elevation-rate limit before flight day.

## Common mistakes & misconceptions
1. **"Angle accuracy is limited to the beamwidth."** Monopulse measures to ~1/10 of a beamwidth at 13 dB and better at higher SNR; resolution of two targets is a different matter.
2. **Quoting $k_m$ without saying which beamwidth it is normalised to** (single beam, sum beam, or λ/D) — numbers differ by 30 % or more.
3. **Using the single-beam SNR in the accuracy formula** — it is the sum-channel SNR.
4. **Ignoring crossover loss** in the range equation of a conical-scan or lobing radar (two-way, ~2–4 dB).
5. **Running an α-β tracker in polar coordinates for crossing targets** — straight lines are curves in (R, θ); filter in Cartesian or use an EKF.
6. **Using a fixed Cartesian R** for converted measurements — the ellipse rotates with bearing and stretches with range.
7. **Nearest-neighbour association in dense clutter** — track seduction; quantify false measurements per gate first.
8. **Pointing at the last telemetry fix** — latency × angular rate; predict to the actual pointing time.
9. **Expecting a Yaesu-class rotator to follow the boost from close in** — size by $v/d$.
10. **Treating RSSI step-track as precise** — fading and quantisation give several degrees of error per measurement.

## How to simulate / verify
- `python3 tools/verify/est_radar_tracking.py` (≈ 10 s, **ALL PASS**): Gaussian-beam monopulse closed form, slope, squint table, crossover loss; monopulse angle-noise MC vs formula and beam splitting; phase monopulse vs array CRB; conical-scan modulation depth/phase and fluctuation sensitivity vs monopulse; split-gate S-curve; polar→Cartesian covariance and bias; gate threshold and area; NN vs PDAF in three clutter densities; pointing loss; GNSS-cued pointing with raw / extrapolated / Kalman-predicted aim at 1 and 5 km; RSSI step-track accuracy; worked numbers.
- For your own tracker: simulate truth + detections with $P_D$ and Poisson clutter, run the filter, and report track loss, rms error and NEES/NIS ([Kalman consistency](../00-math-foundations/kalman-filter-and-state-estimation.md)).
- Antenna measurement: map Σ and Δ patterns on a range or with a drone-carried beacon; fit $k_m$ from the Δ/Σ slope.

## Open questions / gaps
- No measured Σ/Δ patterns of a real hobby monopulse feed; the slopes here are for Gaussian beams (and Sandia's uniform aperture).
- IMM, JPDA and MHT are described, not simulated; manoeuvring-target (boost/burnout) association not tested.
- Multipath (low-angle) elevation error and glint were not modelled.
- The rotator dynamics in the pointing simulation are ideal (instant slew); see the [ground-station recipe](../20-projects-recipes/ground-station-tracking-yagi.md) for rate-limited results.

## Sources
1. S. M. Sherman, D. K. Barton, *Monopulse Principles and Techniques*, 2nd ed., Artech House (2011) — Σ/Δ formation, monopulse ratio and slope, normalisation conventions, thermal-noise angle error (the σ_θ form reproduced by [3]). (textbook; not re-read — cited via [3])
2. M. I. Skolnik, *Introduction to Radar Systems*, 3rd ed., McGraw-Hill (2001), ch. 4 (tracking radar: sequential lobing, conical scan, amplitude/phase monopulse, servo, range tracking, glint, low-angle tracking, TWS) and §6.3 (accuracy). (textbook; cited, not re-read)
3. A. W. Doerry, D. L. Bickel, *Notes on Amplitude versus Phase Comparison Monopulse Antennas for Radar*, Sandia report SAND2024-06153 (May 2024). https://www.osti.gov/servlets/purl/2429954 — difference-pattern definition with the √2 hybrid, normalised slope $k_m$, $\sigma_\theta=\theta_{ref}/(k_m\sqrt{2\,\mathrm{SNR}})$ with sum-beam SNR, optimum squint 0.415 θ_g and $k_m$ = 1.62 for a uniform aperture, ≈ θ/(2.2√SNR), amplitude ≡ phase monopulse within 1.4 %. (government lab report; read in full as text)
4. MIT Lincoln Laboratory / IEEE New Hampshire Section, *Radar Systems Course*, "Parameter estimation and tracking, Part 1" (2010): accuracy ∝ 1/√(S/N), 10:1 beam splitting at ~13 dB, amplitude/phase monopulse feeds and hybrids, sequential lobing, conical-scan modulation and block diagram, split-gate range tracking, type-II servos. https://gmoein.github.io/files/MIT%20Graduate%20Radar%20Course/Radar%202009%20A_15%20Parameter%20Estimation%20and%20Tracking%20Part%201.pdf (lecture notes; read as text)
5. Y. Bar-Shalom, E. Tse, "Tracking in a cluttered environment with probabilistic data association," *Automatica* 11(5):451–460 (1975); Y. Bar-Shalom, T. E. Fortmann, *Tracking and Data Association*, Academic Press (1988). (peer-reviewed / textbook; recalled — PDAF equations re-implemented and tested here)
6. S. S. Blackman, R. Popoli, *Design and Analysis of Modern Tracking Systems*, Artech House (1999) — gating, GNN, JPDA, MHT, track initiation/M-of-N. (textbook; recalled)
7. Y. Bar-Shalom, X. R. Li, T. Kirubarajan, *Estimation with Applications to Tracking and Navigation*, Wiley (2001) — α-β trackers, converted measurements and their bias, IMM. (textbook; recalled)
8. P. R. Kalata, "The tracking index: a generalized parameter for α-β and α-β-γ target trackers," *IEEE Trans. AES* 20(2):174–182 (1984); T. R. Benedict, G. W. Bordner, *IRE Trans. Automatic Control* 7(4):27–32 (1962) — track-while-scan smoothing. (peer-reviewed; via the [Kalman page](../00-math-foundations/kalman-filter-and-state-estimation.md))
9. M. A. Richards, *Fundamentals of Radar Signal Processing*, 2nd ed., McGraw-Hill (2014), ch. 7 (measurements and estimation accuracy). (textbook; cited, not re-read)
10. Yaesu G-5500DC rotation-time figures (58 s/360° az, 67 s/180° el) — via the KB [ground-station recipe](../20-projects-recipes/ground-station-tracking-yagi.md). (manufacturer specification)
