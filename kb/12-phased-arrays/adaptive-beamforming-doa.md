---
title: Adaptive beamforming and direction finding — delay-and-sum, MVDR/Capon, LCMV, diagonal loading, MUSIC, Root-MUSIC, ESPRIT, spatial smoothing, CRB
domain: 12-phased-arrays
slug: adaptive-beamforming-doa
tags: [DOA, direction-finding, RDF, transmitter-hunting, body-fade, offset-attenuator, pseudo-doppler, watson-watt, adcock, triangulation, TDOA, rocket-recovery, delay-and-sum, bartlett, MVDR, capon, MPDR, LCMV, sample-covariance, SMI, reed-mallett-brennan, diagonal-loading, signal-cancellation, MUSIC, root-MUSIC, ESPRIT, spatial-smoothing, forward-backward, coherent-sources, multipath, CRB, cramer-rao, MDL, source-number, UCA, KrakenSDR, interferometry]
prerequisites: [array-factor-linear-arrays.md, beamforming-architectures.md, array-calibration.md, ../00-math-foundations/matrices-and-linear-algebra-for-networks.md, ../00-math-foundations/probability-random-processes-and-psd.md]
related: [../20-projects-recipes/phased-array-starter-build.md, ../08-antennas/antennas-on-rockets.md, ../15-lora-ism-radios/semtech-chip-family.md, tapering-sidelobe-control.md, planar-arrays-element-pattern-coupling.md, diy-phased-array-projects.md, beam-steering-grating-lobes.md, ../11-radar/mimo-radar-virtual-arrays.md, ../11-radar/detection-theory-cfar.md, ../14-sdr-dsp/iq-complex-baseband.md, ../10-comms-modulation/matched-filter-detection.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Adaptive beamforming and direction of arrival (DOA)

## Questions this page answers
- How do I find the direction of a transmitter with an array of antennas and a coherent SDR?
- What is the difference between delay-and-sum (Bartlett), Capon/MVDR and MUSIC?
- Can MUSIC really resolve two sources closer than the beamwidth? At what SNR?
- Why does MUSIC fail with multipath (coherent sources), and what is spatial smoothing?
- What is the best possible bearing accuracy (Cramér–Rao bound) for my array, SNR and number of samples?
- How many snapshots do I need for adaptive beamforming?
- Why does my MVDR beamformer cancel the very signal I'm trying to receive, and how does diagonal loading fix it?
- How does an adaptive array null a jammer?
- How do I estimate how many signals are present?
- Why does a linear array confuse front and back, and why does KrakenSDR use a circular array?
- What are ESPRIT and Root-MUSIC good for?
- Which algorithm should I use in practice?
- How do I find a landed rocket's beacon with a handheld Yagi, and should I use the peak or the null?
- What is "body fade", and what is an offset attenuator for?
- How does a pseudo-Doppler or Watson–Watt direction finder work, and how accurate is it?
- How far off will my position fix be if I take bearings from two places?
- Why does my receiver show full scale everywhere when I get close to the transmitter?

## TL;DR
- **Data model**: x(t) = A(θ)s(t) + n(t) with steering vectors a(θ) (N × 1), sample covariance R̂ = (1/K)Σx xᴴ. Every method below is a function of R̂.
- **Delay-and-sum (Bartlett)**: P(θ) = aᴴR̂a — scan a conventional beam; resolution ≈ one beamwidth. **MVDR/Capon**: P(θ) = 1/(aᴴR̂⁻¹a), weights w = R̂⁻¹a/(aᴴR̂⁻¹a) — minimum output power with unit gain toward θ; adaptively nulls interferers and resolves better than a beamwidth at high SNR. **MUSIC**: P(θ) = 1/‖E_nᴴa‖² using the noise-subspace eigenvectors — "super-resolution"; **Root-MUSIC** and **ESPRIT** give the angles in closed form for ULAs (ESPRIT needs shift invariance).
- **Accuracy**: for one source on a ULA the Cramér–Rao bound is var(u) ≥ **6/(K·SNR·(kd)²·N(N²−1))** (deterministic; ×(1 + 1/(N·SNR)) stochastic). Bartlett, MUSIC and Root-MUSIC reach it above threshold (N = 8, K = 100: 0 dB → 3.8×10⁻³ vs 3.7×10⁻³ in u ≈ 0.22°) — for a *single* source the plain beam-scan is already optimal (verified).
- **Resolution** (N = 8, K = 100, two equal uncorrelated sources): at half the Rayleigh spacing Bartlett never resolves; MVDR needs ≈ 10 dB; MUSIC 93% at 0 dB; Root-MUSIC/ESPRIT 100% at 0 dB. At 0.3 Rayleigh: MVDR needs ≈ 20 dB, MUSIC ≈ 10 dB (verified).
- **Coherent sources** (multipath: same waveform, different directions) make the signal covariance rank-deficient: MUSIC degrades or fails (errors ≈ 100× larger, 36% outright failures in our test). **Spatial smoothing** (average covariances of L-element subarrays; forward–backward averaging) restores rank at the cost of aperture: 8 elements, L = 5–6 → 100% success.
- **Adaptive beamforming with sample covariance (SMI)**: the average SINR loss is ρ = (K + 2 − N)/(K + 1) (Reed–Mallett–Brennan) — **K ≈ 2N snapshots cost 3 dB** (verified: N = 8, K = 12 → −3.5 dB; K = 64 → −0.5 dB).
- **Signal cancellation**: if the desired signal is in the training data (MPDR) and your steering vector is slightly wrong, MVDR treats the signal as interference and nulls it: SNR 20 dB, pointing error 0.02 in u → SINR −11.6 dB instead of 29 dB. **Diagonal loading** (R̂ + σ_L²I, loading 10–20 dB above noise) restores 21.7 dB (verified).
- **Field DF for recovery** ([section below](#practical-direction-finding-for-rocket-recovery)): with a 3-element handheld Yagi (7.3 dBi, 66° beam, NEC) and a 1 dB S-meter, reading the **peak** gives σ ≈ 11°, **bisecting the −3 dB edges** ≈ 3.8°, and bisecting a **null** ≈ 1–1.5° if reflections fill it only to −25 dB. With terrain multipath the 1σ budget is ≈ 6–7° (Yagi), ≈ 3° (calibrated KrakenSDR). Two bearings 1° apart from a 2 km baseline locate a target 5 km away to a median 225 m; crossing at 90° gives R·σ per axis. Close in, a 2 W beacon needs 45–80 dB of attenuation in the last 10 m: use an offset attenuator or body fade, because handheld receivers leak through their cases.
- **Source counting**: MDL on the eigenvalues works at ≥ −5 dB SNR per element with K = 100 (N = 8, two sources). **UCAs** give unambiguous 360° azimuth; a ULA cannot tell θ from its mirror image (180° − θ) (verified: identical steering vectors).

## Intuition (no math)

**Direction finding is "which delay pattern fits best".** A plane wave from direction θ imprints a specific set of phase differences on the array — its steering vector. DOA estimation compares what the array measured against the steering vectors of all candidate directions.

**Delay-and-sum just points a beam around and listens.** Where it hears the most power is the estimate. It is robust and, for one source, as accurate as anything; but two sources closer than a beamwidth blur into one bump.

**MVDR/Capon points the beam but lets it dodge.** For each look direction it builds the beam that keeps unit gain there but makes the *total* output power as small as possible — which it does by steering nulls onto every other signal. The residual power is a much sharper "spectrum": strong sources off to the side are nulled instead of leaking through sidelobes.

**MUSIC exploits the geometry of the covariance.** With M sources and N > M elements, the signals only occupy an M-dimensional corner (the signal subspace) of the N-dimensional space of possible element vectors; the rest is pure noise. The steering vectors of the true directions are *exactly perpendicular* to the noise subspace. So instead of looking for "where is the power", MUSIC looks for "which steering vectors are orthogonal to the noise", which gives very sharp peaks — much finer than the beamwidth — provided the model is exact (calibrated array, uncorrelated sources, enough SNR and snapshots).

**Why multipath breaks it.** A reflected copy of the same signal isn't a new, independent signal: it adds nothing new to the signal subspace, which stays one-dimensional. MUSIC then "sees" one strange source in a direction that is neither. Spatial smoothing slides a smaller sub-array along the array and averages; each shifted sub-array sees the two paths with different relative phases, which decorrelates them — like moving your head to tell an echo from the original.

**Why adaptive beamformers can shoot themselves in the foot.** If the wanted signal is present while the beamformer learns, and the beamformer's idea of its direction is slightly off, the wanted signal looks like "interference just next to the look direction" — and gets nulled. Diagonal loading makes the beamformer less aggressive: it pretends there is extra white noise, which limits how deep and how close to the look direction it will null.

## The math

Notation: N elements, K snapshots, M sources. a(θ) ∈ ℂ^N (ULA: a_n = e^{jkdn sinθ}), A = [a(θ₁) … a(θ_M)], x(k) = As(k) + n(k), noise white with power σ². True covariance R = A R_s Aᴴ + σ²I; sample covariance R̂ = (1/K)Σ_k x(k)x(k)ᴴ.

### Level 1 — the estimators

| Method | Spectrum / weights | Notes |
|---|---|---|
| Bartlett (conventional, DAS) | P_B(θ) = a(θ)ᴴR̂a(θ)/N² ; w = a/N | beamwidth resolution; optimal for one source |
| MVDR / Capon | P_C(θ) = 1/(aᴴR̂⁻¹a); w = R̂⁻¹a/(aᴴR̂⁻¹a) | adaptive nulls; needs K > N |
| LCMV | w = R̂⁻¹C(CᴴR̂⁻¹C)⁻¹f | several linear constraints Cᴴw = f (gains, nulls, derivatives) |
| MUSIC | P_M(θ) = 1/‖Ê_nᴴa(θ)‖² | Ê_n = eigenvectors of the N − M smallest eigenvalues |
| Root-MUSIC | roots of aᵀ(1/z)Ê_nÊ_nᴴa(z) = 0 near \|z\| = 1 | ULA only; angles from arg z |
| ESPRIT | eig of Ψ solving Ê_{s,1}Ψ ≈ Ê_{s,2} (TLS) | needs two identical shifted subarrays |
| Spatial smoothing | R̄ = (1/P)Σ_p R̂_p (L-element subarrays), FB: ½(R̄ + J R̄* J) | decorrelates coherent sources |
| CRB (1 source, ULA) | var(u) ≥ 6/(K·SNR·(kd)²·N(N²−1)) | u = sinθ, SNR per element |

### Level 1½ — two antennas, algebra only
The matrix formulas above are what you get when the following two-antenna arithmetic is written for N antennas.
- **Bearing from a phase difference.** Put two antennas $d$ apart. A wave from angle θ off broadside reaches the second antenna earlier by a path difference $d\sin\theta$, so its signal leads by the phase $\psi = 2\pi d\sin\theta/\lambda$. Measure ψ and solve: $\sin\theta = \psi\lambda/(2\pi d)$. With $d = \lambda/2$ this is simply $\sin\theta = \psi/180°$. This is the interferometer that Bartlett, MUSIC and ESPRIT all refine.
- **Phase error becomes angle error.** A phase error $\delta\psi$ gives $\delta\theta = \delta\psi\,\lambda/(2\pi d\cos\theta)$. The error is smallest at broadside and grows towards endfire as 1/cosθ. Averaging K independent snapshots divides the noise part by $\sqrt K$. Calibration errors do not average away.
- **A null is a subtraction.** Weight the second antenna by $w_2 = -e^{-j\psi_i}$ and add it to the first. A signal from the interferer's direction then gives $1 - e^{-j\psi_i}e^{j\psi_i} = 0$, so it is cancelled exactly. A signal from elsewhere survives with amplitude $|1 - e^{j(\psi-\psi_i)}|$. MVDR finds such weights by itself from the data, for every interferer at once.
- **MUSIC in one sentence.** With fewer sources than antennas, some combinations of the antenna outputs contain only noise. The true directions are the ones whose steering vector gives zero in every such combination.

*Worked number (verified, `tools/verify/s18_level15_numbers.py`).* Two whips at 433.92 MHz spaced λ/2 = 34.5 cm read a phase difference of 60°:
- **Bearing:** sinθ = 60/180, so θ = **19.5°**.
- **Single-reading error:** a 5° phase error moves this by 5°·λ/(2πd cos θ) = **1.7°**. Averaging 100 snapshots cuts the noise part to 0.17°.
- **Null steering:** to remove an interferer at 30° (ψ_i = 90°), use $w_2 = -e^{-j90°} = +j$. The interferer is cancelled completely. A wanted signal at broadside comes out with $|1 + j| = \sqrt2$ instead of 2, i.e. 3 dB weaker than the plain sum. That is the price of the null.

### Level 2 — derivations

**(a) MVDR (Capon) from first principles.** Minimise the output power E|wᴴx|² = wᴴRw subject to unit gain toward θ₀: wᴴa₀ = 1. Lagrangian ℒ = wᴴRw − λ(wᴴa₀ − 1) − λ*(a₀ᴴw − 1); setting ∂ℒ/∂w* = Rw − λa₀ = 0 gives w = λR⁻¹a₀; the constraint fixes λ = 1/(a₀ᴴR⁻¹a₀):
$$\mathbf w_{MVDR} = \frac{\mathbf R^{-1}\mathbf a_0}{\mathbf a_0^H\mathbf R^{-1}\mathbf a_0},\qquad P_{min} = \frac{1}{\mathbf a_0^H\mathbf R^{-1}\mathbf a_0}.$$
Scanning θ₀ and plotting P_min gives the Capon spectrum [1][2]. If R is the *interference-plus-noise* covariance R_in (no desired signal — possible in radar with signal-free range cells), this w also maximises SINR, SINR_opt = σ_s²·a₀ᴴR_in⁻¹a₀. In the script (N = 8, one 30 dB jammer at u = 0.45, 0 dB signal at broadside) SINR_opt = 8.97 dB, essentially the interference-free N·SNR = 9.03 dB, while the conventional beam gives −11.1 dB (the jammer leaks through a sidelobe). With the desired signal *included* (the "MPDR" case) the solution is identical in theory, but becomes fragile to model errors (see (d)).

**(b) LCMV.** Minimise wᴴRw subject to Cᴴw = f (e.g. unit gain at θ₀ *and* a zero at a predicted interferer θ₁; or derivative constraints for a flatter main beam). The same Lagrange argument gives w = R⁻¹C(CᴴR⁻¹C)⁻¹f (Frost 1972 [8]). Script: constraint null at u = −0.3 → −299 dB (numerical zero) while the adaptive part still nulls the jammer at u = 0.45 (−97 dB).

**(c) Sample-matrix inversion (SMI) convergence.** With R̂ estimated from K interference-plus-noise snapshots, the SINR of w = R̂⁻¹a₀ relative to optimum is a random variable ρ with a beta distribution, mean E[ρ] = (K + 2 − N)/(K + 1) (Reed, Mallett & Brennan 1974 [3]). Hence K = 2N − 3 gives ρ ≈ ½ (−3 dB) — the famous "2N snapshots" rule. Monte Carlo (script §4, N = 8): K = 8 → −6.6 dB (formula −6.5), 12 → −3.5 (−3.4), 16 → −2.4 (−2.3), 64 → −0.51 (−0.49), 160 → −0.19 (−0.19). For MVDR *spectra* and MUSIC the covariance must also be well estimated; K ≥ 5–10N is a comfortable working range for DF.

**(d) Signal cancellation and diagonal loading.** When the desired signal is in R̂ and the assumed steering vector ã differs from the true a₀ (pointing error, calibration error, coupling), MPDR minimises power while keeping unit gain only on ã — and the cheapest way to lower the power is to put a null on the actual signal, just beside ã. The stronger the signal, the worse (it dominates the power). Diagonal loading replaces R̂ by R̂ + σ_L²I: it limits the white-noise gain penalty of the solution (deep, close-in nulls require large, oscillating weights) and makes the beamformer robust (Carlson 1988 [9]; Van Trees ch. 6 [1]). Script §4 (N = 8, 30 dB jammer, K = 200): SNR 20 dB, Δu = 0.02 (≈1/7 beamwidth): SINR −11.6 dB unloaded, 8.7 dB with loading 10 dB above noise, 21.7 dB with 20 dB (optimum 29.0 dB); at SNR 0 dB the problem is mild (4.4 → 8.6 dB). Rule: load 10–20 dB above the noise floor, more when the signal is strong or the array poorly calibrated; loading reduces the depth of the jammer null only when the jammer is weaker than the loading level.

**(e) MUSIC.** With uncorrelated sources (R_s full rank M) and white noise, the eigendecomposition R = E_sΛ_sE_sᴴ + σ²E_nE_nᴴ has M eigenvalues > σ² whose eigenvectors span range(A), and N − M eigenvalues equal to σ² whose eigenvectors E_n satisfy E_nᴴA = 0 — because R E_n = σ²E_n implies A R_s AᴴE_n = 0 and, A having full column rank, AᴴE_n = 0. So the true steering vectors are orthogonal to the noise subspace, and P_M(θ) = 1/‖Ê_nᴴa(θ)‖² peaks there (Schmidt 1986 [4]). Requirements: M < N; a calibrated, known manifold a(θ); a correct M (see (i)); and uncorrelated sources — coherent sources reduce rank(R_s) and break the argument.

**(f) Root-MUSIC and ESPRIT.** For a ULA, a(z) = [1, z, …, z^{N−1}]ᵀ with z = e^{jkd sinθ}, and ‖Ê_nᴴa‖² = aᵀ(z⁻¹)Ê_nÊ_nᴴa(z) is a polynomial in z (coefficients = sums along the diagonals of Ê_nÊ_nᴴ). Its M roots closest to the unit circle (inside it) give the DOAs directly — no grid search, and better threshold behaviour than spectral MUSIC (Barabell 1983 [10]). ESPRIT uses the rotational invariance of two identical subarrays displaced by d (elements 1…N−1 and 2…N): their signal-subspace bases satisfy E_{s,2} = E_{s,1}Ψ with the eigenvalues of Ψ equal to e^{jkd sinθ_m} (Roy & Kailath 1989 [5]). It needs no calibrated manifold *beyond* the translational invariance, which is a practical advantage; our total-least-squares implementation is 25–40% above the CRB for one source (the maximum-overlap subarrays lose a little aperture).

**(g) Cramér–Rao bound (one source, ULA).** For deterministic signal power p and noise σ² per element over K snapshots, the Fisher information for u = sinθ is 2K(p/σ²)‖P_a^⊥ ∂a/∂u‖². With ∂a_n/∂u = jkdn·a_n, ‖P_a^⊥∂a/∂u‖² = (kd)²[Σn² − (Σn)²/N] = (kd)²N(N² − 1)/12, hence
$$\operatorname{var}(\hat u) \ge \frac{6}{K\cdot\mathrm{SNR}\cdot (kd)^2\,N(N^2-1)},$$
with the stochastic (Gaussian-signal) CRB larger by (1 + 1/(N·SNR)) [6][7]. The error in θ is σ_u/cosθ. Script §1 (N = 8, K = 100, u = 0.2): √CRB_sto = 3.68×10⁻³ at 0 dB (0.22° at θ ≈ 11.5°), 3.48×10⁻⁴ at 20 dB; Bartlett, MUSIC and Root-MUSIC achieve 3.78×10⁻³ and 3.57×10⁻⁴; MVDR 3–5% worse; below ≈ −5 dB all methods leave the bound (threshold effect: outliers). Consequences: accuracy improves as N^{3/2} (aperture × √elements), √K and √SNR — doubling the aperture halves the error even at fixed element count.

**(h) Coherent sources and spatial smoothing.** Multipath gives s₂(t) = βs₁(t): R_s has rank 1. Script §3: eigenvalues 16.8, 0.011, 0.011… — only one signal eigenvalue for two arrivals. **Forward spatial smoothing** (Shan, Wax & Kailath 1985 [11]) averages the covariances of the P = N − L + 1 overlapping L-element subarrays: R̄ = (1/P)ΣR̂_p. Each subarray sees the arrivals with a different relative phase (the subarray shift multiplies each steering vector by a different phase), so the averaged source covariance regains rank when P ≥ M. **Forward–backward** averaging, ½(R̄ + JR̄*J) with J the exchange matrix, doubles the effective number of subarrays. Cost: the effective aperture shrinks to L elements. For M coherent sources you need N ≥ 2M (forward) or N ≥ 3M/2 (FB) elements. Script: 8 elements, two coherent paths at 20 dB: unsmoothed MUSIC errors ≈ 0.03 in u and 36% failures; FSS with L = 5 or 6, FBSS with L = 6: 100% success, errors 3–4×10⁻⁴; eigenvalues after FBSS: 8.9, 3.6, 0.011 (rank 2 restored). KrakenSDR's "decorrelation" options (FBA/FBSS-type) exist for exactly this and work with ULAs [12].

**(i) How many sources? MDL.** The minimum-description-length criterion (Wax & Kailath 1985 [13]) picks k minimising −K(N−k)·ln(g_k/a_k) + ½k(2N−k)ln K, where g_k and a_k are the geometric and arithmetic means of the N − k smallest eigenvalues (equal when they are pure noise). Script §5 (N = 8, two sources): K = 20 → correct 99% at 0 dB, 35% at −5 dB; K = 100 → 100% at −5 dB; K = 500 → 100% at −10 dB. Over-estimating M is less harmful for MUSIC than under-estimating it, but KrakenSDR warns that setting the source count too high gives bad results [12].

**(j) Circular arrays and ambiguity.** A ULA only measures u = sinθ relative to its axis: a source and its mirror image across the array line produce identical steering vectors (script §6: correlation 1.000), so a ULA covers 180° with a front/back ambiguity. A uniform circular array (UCA) of radius r has a_n(φ) = e^{jkr cos(φ − φ_n)}, unique over 360° (mirror correlation 0.145 for 5 elements). KrakenSDR's UCA radius rule r = sλ/√(2(1 − cos(360°/n))) = sλ/(2 sin(π/n)) (neighbour spacing sλ, s ≈ 0.2–0.5) [14]: 5 elements, s = 0.4 → r = 0.340λ = 23.6 cm at 433 MHz; MUSIC at 10 dB SNR, 200 snapshots gives ≈ 0.3° rms azimuth error (script §6).

### Level 3 — beyond the basics

- **Maximum likelihood** DOA (deterministic or stochastic ML) attains the CRB even for correlated/coherent sources and small K, at the price of an M-dimensional search (alternating projection, IQML, WSF). Krim & Viberg's review is the map of this territory [6].
- **Wideband signals**: split into frequency bins and combine (incoherent: average spectra; coherent signal-subspace methods: focus all bins to one reference frequency). LoRa chirps (125–500 kHz) are narrowband for any hobby array (aperture fill time ≪ 1/BW).
- **Model errors dominate in practice**: unknown channel gains/phases, element positions and mutual coupling bias subspace methods by up to degrees; calibration or joint self-calibration is part of any real DF system ([calibration](array-calibration.md), [coupling](planar-arrays-element-pattern-coupling.md)).
- **Sparse/compressive DOA**, **coprime and nested arrays** (O(N²) degrees of freedom from N elements via the difference co-array), and **MIMO virtual arrays** in radar extend the same ideas ([MIMO radar](../11-radar/mimo-radar-virtual-arrays.md)).
- **Tracking**: for a moving source (a rocket), feed DOA estimates into a Kalman filter with a kinematic model; per-update accuracy from the CRB sets the measurement noise.
- **Space–time adaptive processing (STAP)** generalises MVDR to joint angle–Doppler weights for airborne radar; the RMB rule then applies with N × pulses degrees of freedom.

## Design equations & rules of thumb

| Rule | Validity | Value |
|---|---|---|
| var(u) ≥ 6/(K·SNR·(kd)²N(N²−1)) | 1 source, ULA, above threshold | N = 8, K = 100, 0 dB: σ_u = 3.5–3.7×10⁻³ |
| σ_θ = σ_u/cosθ | ULA | worse toward endfire |
| SMI loss E[ρ] = (K+2−N)/(K+1) | Gaussian training, no signal | K ≈ 2N → −3 dB |
| Diagonal loading 10–20 dB above noise | MPDR, mismatch present | restores ~20 dB in our example |
| M < N (MUSIC), N ≥ 2M (FSS), N ≥ 3M/2 (FBSS) | subspace methods | 8 elements: ≤ 5 coherent (FBSS) |
| Resolution: Bartlett ≈ Rayleigh λ/(Nd); MUSIC/Root-MUSIC ≈ 0.3–0.5 Rayleigh at 0–10 dB | K = 100, N = 8 | — |
| UCA radius r = sλ/(2 sin(π/n)), s = 0.2–0.5 | KrakenSDR rule | 5 el, s = 0.4, 433 MHz: 23.6 cm |
| K ≥ 5–10N snapshots for DF | practical | N = 5: ≥ 50 |

## Worked examples

**Example 1 — bearing accuracy of a KrakenSDR on a 433 MHz rocket beacon.** 5-element UCA (r = 23.6 cm), SNR 10 dB per element, 200 snapshots per estimate: script §6 gives ≈ 0.3° rms from noise alone. For a ULA equivalent, the CRB with N = 5, d = 0.4λ, K = 200, SNR = 10: var(u) ≥ 6/(200·10·(2π·0.4)²·5·24) = 3.96×10⁻⁶ → σ_u = 2.0×10⁻³ ≈ 0.11° at broadside. Reality is dominated by calibration/cable/coupling errors (degrees) and multipath from terrain — use spatial smoothing or a higher mast. At 10 km range, 1° ≈ 175 m cross-range.

**Example 2 — a jammer 30 dB above a 0 dB signal.** N = 8, jammer at u = 0.45 (27°): conventional beam SINR −11.1 dB; MVDR with the true interference covariance 8.97 dB; with K = 16 training snapshots about 2.4 dB less (script §4). A digital array (or at least 8 coherent channels) is required; analog single-beam arrays cannot do this.

**Example 3 — resolving two emitters 7° apart with 8 elements.** The Rayleigh resolution is λ/(Nd) = 0.25 in u (≈14°). At 0.5 Rayleigh (≈7°) and 0 dB SNR, only Root-MUSIC/ESPRIT (100%) and MUSIC (93%) separate them; Bartlett never does; MVDR needs ≈ 10 dB (script §2). Calibrate first — super-resolution depends on an accurate manifold.

**Example 4 — multipath over a runway.** Direct and ground-reflected paths from a drone beacon arrive coherent. With 8 elements, forward–backward smoothing with 6-element subarrays restores both arrivals; the price is a 6-element effective aperture (beam 25% wider).

**Example 5 — the MVDR self-nulling trap on a ground station.** Receiving a strong (20 dB SNR) rocket downlink with an 8-element adaptive array steered from GPS-telemetry pointing that is 1° off (Δu ≈ 0.017 near broadside): unloaded MPDR can null the rocket itself (≈ −10 dB SINR instead of 29 dB); loading 20 dB above noise keeps ≈ 22 dB (script §4). Either load, or train on signal-free data (e.g. between packets).

## Practical notes
- **Calibrate first**, then trust super-resolution. Channel phase errors of 5–10° or coupling bias MUSIC by fractions of a beamwidth; residual errors limit resolution before SNR does.
- **Snapshots vs bandwidth**: snapshots should be decorrelated in time; with a 2.4 MS/s KrakenSDR and a 125 kHz LoRa signal, adjacent samples are correlated — filter/decimate to the signal bandwidth first, then count K.
- **Squelch/gating**: estimate only while the signal is present (KrakenSDR's squelch) [12]; noise-only covariance gives random DOAs.
- **Normalise**: MUSIC "spectra" are not power; don't read signal strength from peak height. Capon's spectrum *is* a power estimate.
- **Numerical care**: use eigh (Hermitian), keep R̂ Hermitian ((R̂ + R̂ᴴ)/2), and add a tiny loading for invertibility.
- **UCA vs ULA**: UCA for 360° DF (vehicle roof); ULA for a larger aperture in one sector and for smoothing/ESPRIT/Root-MUSIC (which need a ULA or a virtual ULA transform) — KrakenSDR notes its decorrelation methods are designed for ULAs [12].

## Practical direction finding for rocket recovery

The array methods above are one tool among several. After landing, the rocket's antenna lies about 0.1 m above the ground, so the path is in the two-ray regime and the last GNSS fix may be stale ([antennas on rockets Example 5](../08-antennas/antennas-on-rockets.md#worked-examples), [landed link](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md)). Use the tools in this order: (1) the last downlinked fix plus the descent drift; (2) bearings from two or more places, which give a fix; (3) walk in with a handheld Yagi; (4) in the last tens of metres, an attenuator or body fade. The same tools find a jammer or an unknown emitter ([signal identification](../14-sdr-dsp/signal-identification-and-spectrum-survey.md)). A jammer transmits continuously, which suits pseudo-Doppler and Watson–Watt even better than bursty LoRa. Numbers below are from `tools/verify/s1_df_bearing.py` unless cited.

### Level 1 — what each method measures

| Method | What it measures | Hardware | Bearing error (1σ, reading only) | Weak point |
|---|---|---|---|---|
| Yagi **peak** | angle of maximum signal | 3-el Yagi + receiver with S-meter/RSSI | ≈ 11° (66° beam, 1 dB reading steps; peak is flat over ±19°) | the top of the beam is flat |
| Yagi **−3 dB edge bisection** | the two angles where the signal is 3 dB below the peak; the bearing is midway | same | ≈ 3.8° | needs a steady signal for ~20 s |
| Yagi **null** | the angle of minimum signal: the side nulls (elements horizontal, ±90°) or the rear null (elements vertical) | same | ≈ 0.9° (side) / 1.5° (rear) if reflections fill the null only to −25 dB | a null is a line, not a direction: the side nulls leave a 180° ambiguity, so resolve it with the peak; reflections fill nulls |
| **Body fade** | the minimum when your body shadows the receiver | any handheld, often with no antenna | tens of degrees (estimate) | close range only; the minimum points *behind* you |
| **Pseudo-Doppler** | phase of the tone made by switching around a ring of antennas | 4–8 whips, RF switch, one receiver/SDR | noise term ≈ λ/(πD√(K·SNR)): 0.8° (4 el, D = 0.25λ, K = 800, 10 dB) | multipath and sampling (aliasing) errors of several degrees [18] |
| **Watson–Watt / Adcock** | amplitude ratio of N–S and E–W antenna pairs, θ = atan2 | 4 monopoles + 3 coherent channels (or a goniometer) | spacing error ≤ (πd/λ)²/24 rad: 1.5° at d = 0.25λ | needs matched channels; also hurt by multipath |
| **Coherent array (KrakenSDR, MUSIC)** | phase pattern across 5 channels | KrakenSDR + 5 whips ([recipe](../20-projects-recipes/phased-array-starter-build.md)) | 0.65° with 2° phase calibration; 2.5° with a −10 dB coherent reflection | calibration, cable matching |
| **TDOA** | arrival-time differences at GNSS-timed receivers (hyperbolae) | ≥ 3 receivers with 1PPS | LoRaWAN field median ≈ 150 m position [20]; 40 m with a 20.8 ns timer, rocket node [21] | multipath at 125 kHz (c/BW = 2.4 km) |

### Level 2 — the arithmetic behind the table

**(a) Amplitude methods.** Near its peak a beam is close to Gaussian: the loss is $L(\theta)\approx 12(\theta/\theta_{3})^2$ dB. With a reading resolution of $r$ dB the peak cannot be placed better than $\pm\theta_3\sqrt{r/12}$, which is ±19° for $\theta_3$ = 66° and $r$ = 1 dB. At the −3 dB points the slope is $dL/d\theta = 24\theta/\theta_3^2 = 12/\theta_3$ dB per degree (0.18 dB/°; NEC gives 0.19). One edge is therefore read to $r\theta_3/12$, and the midpoint of two edges to that value divided by √2, or 3.8°. A deep null is far steeper than either edge, so a null reading is limited by how deeply reflections and the receiver floor fill it, not by the S-meter. The NEC Yagi used here (R/DE/D = 0.525/0.47/0.42 λ, spacings 0.15/0.12 λ, 18.6 cm boom at 434 MHz, 6 mm rod) has F/B 46 dB on paper. In the field, expect 15–25 dB, because the ground, your body and nearby metal fill the null.

**(b) Pseudo-Doppler.** Put $N$ antennas on a circle of diameter $D$ and switch the receiver around them at $f_r$ rotations per second. The carrier phase seen at element $n$ (angle $\phi_n$) from a source at bearing $\alpha$ is $\psi_n = (\pi D/\lambda)\cos(\phi_n-\alpha)$. The switching therefore phase-modulates the signal with a sinusoid at $f_r$ of amplitude $\beta=\pi D/\lambda$, and an FM detector outputs a tone with peak deviation $\Delta f=\beta f_r$. The bearing is the phase of that tone relative to the switch sequence [18]. A least-squares fit to $K$ phase samples, each with noise variance $\sigma_\phi^2 = 1/(2\,\mathrm{SNR})$, gives
$$\sigma_\alpha \approx \frac{\lambda}{\pi D\sqrt{K\cdot \mathrm{SNR}}}\ \text{rad},$$
which the Monte Carlo matches within 10 % (4 and 8 elements, 10 and 20 dB). Neighbour spacing must be ≤ λ/2 to avoid phase ambiguity [18]. At 1 kHz switching a 72 ms SF7/125 LoRa packet spans 72 rotations. However, a chirp is itself a large frequency modulation: either de-chirp before measuring the tone, or DF a plain carrier (see the beacon mode in the procedure below). Only one receiver channel is needed, which is why hobby Doppler DF units are cheap.

**(c) Watson–Watt with an Adcock array.** Two pairs of antennas, spaced $d$ apart (N–S and E–W), are each fed to a difference amplifier. For a vertically polarised wave from $\theta$ the outputs are proportional to $\sin(u\cos\theta)$ and $\sin(u\sin\theta)$, with $u=\pi d/\lambda$. The bearing estimate is $\hat\theta=\operatorname{atan2}(\sin(u\sin\theta),\sin(u\cos\theta))$. Expanding $\sin x\approx x-x^3/6$ gives the spacing ("octantal") error $\delta\theta\approx(u^2/24)\sin4\theta$. The maximum is 0.24° at d = 0.1λ and 1.5° at 0.25λ; at 0.5λ it is 7.2° exactly, where the small-spacing formula (5.9°) no longer holds. All three channels must be gain- and phase-matched, which is the same calibration problem as for any array ([array calibration](array-calibration.md)).

**(d) Two-station fix.** Each bearing is a line. Linearise the bearing from station $i$ (range $R_i$) about the target: $\partial\theta_i/\partial(x,y)=[-\Delta y_i,\ \Delta x_i]/R_i^2$. The position covariance is then $\mathbf P = (\mathbf H^T\mathbf W\mathbf H)^{-1}$ with $\mathbf W = \operatorname{diag}(1/\sigma_i^2)$. If the bearings cross at 90°, each axis of the error ellipse is $R\sigma$, which is 87 m for 1° at 5 km. With a 2 km baseline and the target 5 km away broadside (lines crossing at 23°), the ellipse is 64 m × 321 m. The Monte Carlo median miss is 225 m (90 % 527 m), which agrees with the [recipe's](../20-projects-recipes/phased-array-starter-build.md#level-2--localisation) 220 m. Rule: pick the two stations so that their bearings cross at **60–120°**, and add a third bearing or a moving update to catch blunders.

**(e) TDOA.** A pair of receivers measures $\Delta t=(r_1-r_2)/c$, which places the source on a hyperbola. For a chirp of bandwidth $B$, the timing bound is $\sigma_\tau\ge 1/(2\pi B_{rms}\sqrt{2E/N_0})$ with $B_{rms}=B/\sqrt{12}$. An 8-symbol SF7/125 preamble at 0 dB SNR gives 98 ns (29 m), which is comparable to two receivers' 30 ns RMS PPS jitter ([GNSS timing](../21-gnss/gnss-timing-1pps.md)). In the field, however, multipath at 125 kHz cannot be resolved below c/B = 2.4 km, so public LoRaWAN TDoA has a median error of about 150 m [20]. Ranging with the SX1280 and RSSI ranging are compared in [Semtech chip family § ranging](../15-lora-ism-radios/semtech-chip-family.md#ranging-and-localisation).

### Bearing-error budget (1σ, degrees, combined as RSS)

| Contribution | Yagi, −3 dB bisection | Yagi, null | Yagi, peak | KrakenSDR (calibrated) | Pseudo-Doppler (4 el, 0.25λ) |
|---|---|---|---|---|---|
| reading / noise | 3.8 | 0.9 | 11.1 | 0.65 (incl. 2° phase cal) | 0.2 |
| multipath / terrain (assumed; site-dependent) | 5 | 5 | 5 | 2.5 (−10 dB reflection) | 5 |
| operator heading / compass (assumed) | 2 | 2 | 2 | 1 (array heading) | 2 |
| declination, map plotting (assumed) | 1 | 1 | 1 | 1 | 1 |
| **total** | **6.7** | **5.6** | **12.4** | **2.9** | **5.5** |

Multipath dominates every method that reads a single bearing. Moving 100–200 m and repeating the reading averages it down faster than better hardware does. Keep compasses away from vehicles, which can deflect them by tens of degrees, and correct for local declination (look it up in the World Magnetic Model for the site).

### Close-in hunt: how much attenuation

The table gives the power received by a 7.3 dBi handheld Yagi from a landed rocket (antenna 0.1 m above flat ground, Yagi at 1.5 m, plane-earth two-ray with Γ = −1, 434.125 MHz). The last columns give the attenuation needed to keep the receiver at or below −60 dBm, where a typical S-meter or RSSI reading is still linear. The free-space column is the case where the rocket hangs in a tree or lies on a slope facing you.

| Distance | 10 mW e.r.p. (licence-exempt): two-ray / free space (dBm) | attenuation needed | 2 W, 34.65 dBm EIRP (licensed): two-ray / free space (dBm) | attenuation needed |
|---|---|---|---|---|
| 2 km | −129 / −72 | 0 / 0 dB | −107 / −49 | 0 / 11 dB |
| 1 km | −117 / −66 | 0 / 0 dB | −95 / −43 | 0 / 17 dB |
| 300 m | −96 / −55 | 0 / 5 dB | −74 / −33 | 0 / 27 dB |
| 100 m | −77 / −46 | 0 / 14 dB | −55 / −23 | 5 / 37 dB |
| 30 m | −56 / −35 | 4 / 25 dB | −34 / −13 | 26 / 47 dB |
| 10 m | −37 / −26 | 23 / 34 dB | −15 / −3 | 45 / 57 dB |
| 3 m | −16 / −15 | 44 / 45 dB | +6 / +7 | 66 / 67 dB |
| 1 m | 0 / −6 | 54–60 dB | +17 to +23 | 77–83 dB |

What this means in practice:
- **On the ground, a 10 mW beacon is near the noise floor of a handheld at 1–2 km** (−117 to −129 dBm, compared with about −124 dBm SF7/125 and −137 dBm SF12/125 sensitivity at NF 6 dB). A plain carrier received in a 500 Hz CW filter needs only about −138 dBm (−174 + 6 + 27 + 3), which is ≈ 14 dB better than SF7/125. This is the main reason to give the recovery beacon a carrier mode.
- **A passive step attenuator works only if the receiver is well shielded.** Handheld radios and scanners leak through their cases, so the S-meter pins however much attenuation is in line. The **offset attenuator** fixes this. It mixes the antenna signal in a diode with a 4 MHz oscillator and you tune the receiver 4 MHz away, where only the mixer product is present. Its level is set by the oscillator drive, from about −30 dB to more than −100 dB [17]. It does not protect the receiver front end from the on-channel signal. K0OV reports that low-cost SDR-architecture handhelds (Baofeng-type) produce spurs and desense within about 5 m of a 50 mW source, which gives false bearings [17].
- **Body fade** for the last few metres: remove the antenna, hold the receiver against your stomach and turn slowly. The minimum is when your body is between the receiver and the source, so the source is **behind you**: the body attenuates the signal, it does not reflect it [19]. Body blocking at UHF is of order 10–20 dB [23] (estimate; check your own).
- **An RTL-SDR or KrakenSDR also overloads**: reduce the RF gain first, then add a pad. A 2 W beacon within about 4 m of a 12 dBi antenna can exceed the +10 dBm damage rating of SX126x-class receivers ([ground station § overload](../15-lora-ism-radios/ground-station-design.md#link-asymmetry-and-receiver-overload-near-the-pad)).

### 433 MHz recovery procedure

*Before the flight*
1. **Give the firmware a landed beacon mode.** After landing, send a short unmodulated carrier and a slow, robust LoRa packet with the last fix (e.g. SF11/125 every 5–10 s). The SX126x can send a carrier with `SetTxContinuousWave`. Altus Metrum flight computers do the same: they send a ½ s tone every 5 s during descent and after landing [22]. Check the duty cycle. The Singapore licence-exempt rule at 433 MHz is 10 mW e.r.p. and ≤ 10 % duty. A 0.4 s carrier every 5 s (8 %) plus a 32-byte SF11/125 packet (0.99 s) every 10 s (9.9 %) is about 18 %, which is **over the limit**. A 0.3 s carrier every 6 s (5 %) plus a 32-byte SF9/125 packet (0.25 s) every 10 s (2.5 %) is 7.5 %, which fits. Otherwise operate under a licence ([19](../19-regulations-safety/singapore-imda-rules.md)).
2. **Check polarisation.** A landed rocket's axial antenna usually lies horizontal. Try the Yagi both ways and use whichever gives the stronger, cleaner pattern. Elements horizontal gives the sharp side nulls (§(a)).
3. **Calibrate.** Take a bearing on a beacon at a surveyed position at least 100 m away, note the offset, and check the compass away from the car.
4. **Prepare the map.** Mark the last fix and the expected wind drift, and set up two candidate DF points that see the landing area from directions 60–120° apart.

*In the field*
5. From each point take −3 dB bisection or null bearings (resolve null ambiguity with the peak) and plot them. A KrakenSDR on a car roof replaces this step if available ([recipe Example 1](../20-projects-recipes/phased-array-starter-build.md#1-recovery-df-kit)).
6. Head for the intersection, re-taking bearings every 100–300 m. Several updates on the move beat one precise bearing, because each new position averages different multipath.
7. When the S-meter pins, add attenuation as the table indicates, then switch to the offset attenuator. Within about 10 m, remove the antenna and use body fade.
8. Distrust bearings taken next to fences, vehicles and buildings, because their reflections are coherent with the direct signal. A sudden 180° flip near metal is usually a reflection.
9. If the signal vanishes, gain height (a ridge, or stand on the vehicle). The landed path gains about 6 dB per doubling of height ([two-ray](../09-propagation-link-budget/two-ray-ground-reflection.md)).

## Common mistakes & misconceptions
- **"MUSIC always beats beamforming."** For a single source in white noise, Bartlett is already at the CRB; MUSIC's advantage is resolution of multiple close sources — and only with good calibration.
- **"MUSIC works with multipath."** Coherent arrivals break it; use spatial smoothing (ULA) or ML methods.
- **"Super-resolution is free."** It needs SNR, snapshots, an exact array model and the right source count; its threshold is sharp.
- **"More snapshots always fix everything."** They reduce statistical error; they do not remove model (calibration/coupling) bias.
- **"MVDR is safe to use with the desired signal present."** Steering mismatch causes self-nulling; use diagonal loading or signal-free training.
- **"A linear array gives full 360° bearings."** It has a mirror ambiguity across its axis; use a UCA or two orthogonal arrays.
- **Using d > λ/2 in a DF array** without resolving ambiguities — grating lobes become false bearings ([beam steering](beam-steering-grating-lobes.md)).
- **Counting correlated samples as independent snapshots**, which makes R̂ look better conditioned than it is.
- **"Point the Yagi at the loudest direction."** The peak is flat to within 1 dB over ±19° on a 3-element Yagi. Bisect the −3 dB edges or use a null instead (3–10 times finer).
- **"A null points at the transmitter."** A Yagi's side nulls mark a *line* through you, so resolve the 180° ambiguity with the peak. With body fade the minimum points the source *behind* you.
- **"More attenuation in the coax will fix a pinned S-meter."** If the receiver leaks through its case, it will not. Use an offset attenuator, body fade or no antenna. Ordinary step attenuators work with well-shielded receivers only.
- **"One very good bearing is enough."** Terrain multipath (≈ 5° assumed) dominates the reading error. Take bearings from several positions that cross at 60–120°.
- **Taking bearings next to the car.** The steel deflects the compass and reflects the signal.
- **DF on LoRa packets with a pseudo-Doppler unit built for FM voice.** The chirp itself is a frequency sweep. De-chirp it first, or DF the beacon's plain-carrier mode.

## How to simulate / verify
- `tools/verify/array_doa.py` (~70 s): Bartlett, MVDR, MUSIC, Root-MUSIC, TLS-ESPRIT on synthetic ULA data vs the closed-form CRB; two-source resolution probabilities; coherent sources with forward and forward–backward smoothing; SMI convergence vs Reed–Mallett–Brennan; MPDR signal cancellation with/without diagonal loading; LCMV nulls; MDL source counting; 5-element UCA MUSIC and ULA mirror ambiguity.
- Libraries: `pyargus` (used by KrakenSDR's DOA software) implements Bartlett/Capon/MEM/MUSIC and smoothing; `doatools.py` and MATLAB Phased Array System Toolbox for cross-checks.
- Real data: record 5-channel IQ from a KrakenSDR, apply the same code; compare to a known transmitter bearing.
- `tools/verify/s1_df_bearing.py` (< 2 s, 13 checks): PyNEC 3-element Yagi at 434.125 MHz (E- and H-plane gain, HPBW, F/B, and peak, bisection and null reading errors); pseudo-Doppler Monte Carlo vs λ/(πD√(K·SNR)); Adcock spacing error; bearing budgets; two-station triangulation covariance vs Monte Carlo (and the recipe's 220 m); the close-in attenuation table.
- Field check: walk a known beacon from 1 km to 1 m and log the S-meter against distance and attenuator setting. This shows where your own receiver's case leakage starts.

## Open questions / gaps
- ESPRIT here uses maximum-overlap subarrays and TLS without forward–backward averaging; unitary ESPRIT or FB-ESPRIT would reduce its ≈ 25–40% excess over the CRB — not tested.
- KrakenSDR's exact algorithm list/implementation (Bartlett, Capon, MEM, MUSIC, TNA?) could not be confirmed from the wiki pages read; only "MUSIC recommended" and "decorrelation for ULA" were confirmed.
- No measured field DF accuracies for KrakenSDR at 433 MHz were sourced; see [DIY projects](diy-phased-array-projects.md).
- Practical-DF section: the multipath, compass and body-fade values in the budget are assumptions, not measurements. The −25 dB null fill-in is also assumed. All of these need a field calibration session (register §7 R18). The Moell & Curlee book [16] was not re-read in this pass; its methods are cited through K0OV's articles [17].

## Sources
1. H. L. Van Trees, *Optimum Array Processing* (Part IV of *Detection, Estimation, and Modulation Theory*), Wiley, 2002 — ch. 6 (MVDR/MPDR, LCMV, diagonal loading, mismatch), ch. 7 (adaptive beamformers, SMI), ch. 8 (ML, CRB), ch. 9 (MUSIC, Root-MUSIC, ESPRIT, spatial smoothing). (textbook)
2. J. Capon, "High-resolution frequency-wavenumber spectrum analysis," *Proc. IEEE* 57(8):1408–1418, 1969. (peer-reviewed)
3. I. S. Reed, J. D. Mallett, L. E. Brennan, "Rapid convergence rate in adaptive arrays," *IEEE Trans. Aerosp. Electron. Syst.* 10(6):853–863, 1974 — SMI, K ≈ 2N for 3 dB. (peer-reviewed; abstract)
4. R. O. Schmidt, "Multiple emitter location and signal parameter estimation," *IEEE Trans. Antennas Propag.* 34(3):276–280, 1986 — MUSIC. (peer-reviewed)
5. R. Roy, T. Kailath, "ESPRIT — estimation of signal parameters via rotational invariance techniques," *IEEE Trans. Acoust. Speech Signal Process.* 37(7):984–995, 1989. (peer-reviewed)
6. H. Krim, M. Viberg, "Two decades of array signal processing research: the parametric approach," *IEEE Signal Processing Magazine* 13(4):67–94, 1996 — review of beamforming, subspace, ML methods and bounds. (peer-reviewed review)
7. P. Stoica, A. Nehorai, "MUSIC, maximum likelihood, and Cramér–Rao bound," *IEEE Trans. Acoust. Speech Signal Process.* 37(5):720–741, 1989 — deterministic/stochastic CRB. (peer-reviewed)
8. O. L. Frost III, "An algorithm for linearly constrained adaptive array processing," *Proc. IEEE* 60(8):926–935, 1972 — LCMV. (peer-reviewed)
9. B. D. Carlson, "Covariance matrix estimation errors and diagonal loading in adaptive arrays," *IEEE Trans. Aerosp. Electron. Syst.* 24(4):397–401, 1988. (peer-reviewed)
10. A. J. Barabell, "Improving the resolution performance of eigenstructure-based direction-finding algorithms," *Proc. IEEE ICASSP*, 1983, pp. 336–339 — Root-MUSIC. (conference)
11. T.-J. Shan, M. Wax, T. Kailath, "On spatial smoothing for direction-of-arrival estimation of coherent signals," *IEEE Trans. Acoust. Speech Signal Process.* 33(4):806–811, 1985. (peer-reviewed)
12. KrakenRF, *KrakenSDR documentation wiki*, "05. KrakenSDR Web Interface Controls" — "in almost all cases" use MUSIC; decorrelation designed for ULAs; source-count warning; squelch. (vendor docs)
13. M. Wax, T. Kailath, "Detection of signals by information theoretic criteria," *IEEE Trans. Acoust. Speech Signal Process.* 33(2):387–392, 1985 — AIC/MDL. (peer-reviewed)
14. KrakenRF, KrakenSDR wiki "04. Antenna Array Setup" — UCA radius formula, spacing multiplier 0.2–0.5. (vendor docs)
15. `tools/verify/array_doa.py` — all numbers marked "script". (own verification)
16. J. Moell (K0OV), T. Curlee (WB6UZZ), *Transmitter Hunting: Radio Direction Finding Simplified*, TAB Books, 1987 — the standard amateur text on Yagi/quad RDF, body shielding and attenuators. (book — not re-read in this pass)
17. J. Moell (K0OV), "Build an Offset Attenuator", *Homing In* (updated from the May 1998 *73 Magazine* column), http://www.homingin.com/joek0ov/offatten.html — 4 MHz LO and diode mixer, receiver tuned to the offset, about −30 to > −100 dB, case leakage defeats passive attenuators, SDR-architecture handhelds unsuitable close in. (practitioner article)
18. W. E. Gerhard III, P. Tokekar, "Experimental Evaluation of a Pseudo-Doppler Direction-Finding System for Localizing Radio Tags," arXiv:2003.00386, 2020 — PDDF phase model, λ/2 spacing (≤ 0.35λ square side), HackRF + Operacake, ~330 Hz bearing rate, 4.6–22 m particle-filter fixes. (preprint)
19. Barrie Amateur Radio Club, "Getting started with RDF" (club tutorial, w4hhh.org) — body-fade procedure, minimum means the source is behind you, remove the antenna when close. (club notes — anecdotal)
20. D. Plets, N. Podevijn, J. Trogh, L. Martens, W. Joseph, "Experimental Performance Evaluation of Outdoor TDoA and RSS Positioning in a Public LoRa Network," IPIN 2018 — median TDoA error ≈ 150 m (as cited by Müller et al. 2021). (peer-reviewed conference; via citation)
21. M. Brzynska, K. Klimaszewski, K. Martin, "A Localisation and Telemetry LoRa Node for Rockets," SoftCOM 2023 — TDoA with a 20.8 ns timer, 40 m in ground tests. (peer-reviewed conference; via 15/rocket-telemetry-radio-design)
22. Altus Metrum, *The Altus Metrum System: An Owner's Manual*, https://altusmetrum.org/AltOS/doc/altusmetrum.html — ½ s RDF tone every 5 s during descent and after landing; 10 mW (v1) / 40 mW radios; default 434.550 MHz. (manufacturer manual)
23. S. L. Cotton, R. D'Errico, C. Oestges, "A review of radio channel models for body centric communications," *Radio Science* 49(6), 2014 (PMC4579845) — body shadowing of order 10–20 dB. (peer-reviewed review; search-level reading)
24. `tools/verify/s1_df_bearing.py` — every number in the practical-DF section not otherwise cited. (own verification)
