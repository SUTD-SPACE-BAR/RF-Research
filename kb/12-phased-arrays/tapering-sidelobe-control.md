---
title: Tapering and sidelobe control — uniform, binomial, Dolph–Chebyshev, Taylor n̄, cosine-on-pedestal, taper efficiency, random-error floors, monopulse
domain: 12-phased-arrays
slug: tapering-sidelobe-control
tags: [taper, amplitude-weighting, sidelobe-level, SLL, binomial-array, dolph-chebyshev, taylor-nbar, cosine-on-pedestal, hamming, taper-efficiency, beam-broadening, random-errors, error-budget, element-failure, monopulse, bayliss, pattern-synthesis, schelkunoff, woodward-lawson]
prerequisites: [array-factor-linear-arrays.md, ../00-math-foundations/special-functions-bessel-sinc.md, ../00-math-foundations/fourier-series-and-transform.md]
related: [beam-steering-grating-lobes.md, planar-arrays-element-pattern-coupling.md, adaptive-beamforming-doa.md, array-calibration.md, phase-shifters-ttd-components.md, ../08-antennas/horn-reflector-aperture-antennas.md, ../14-sdr-dsp/fft-spectral-analysis-windows.md, ../11-radar/radar-range-equation.md]
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Tapering and sidelobe control

## Questions this page answers
- Why does a uniformly weighted array have −13 dB sidelobes, and how do I get lower ones?
- What do Dolph–Chebyshev and Taylor tapers actually do, and which should I use?
- How much gain and beamwidth do I lose by tapering?
- Is an array taper the same thing as an FFT window?
- What is n̄ in a Taylor taper and how do I choose it?
- How accurately must I set the element amplitudes and phases to actually achieve −30 dB sidelobes?
- What happens to the sidelobes if a few elements fail?
- How do I calculate the sidelobe "floor" caused by random errors?
- Why do transmit arrays often stay uniform while receive arrays are tapered?
- What is a monopulse (sum/difference) pattern and why does it need its own taper (Bayliss)?
- Can I get zero sidelobes (binomial array)? Why doesn't everyone do that?
- How do I put a null on an interferer with a fixed taper?

## TL;DR
- The pattern is the Fourier transform of the aperture weights. A uniform aperture has a hard edge → sinc pattern → first sidelobe **−13.26 dB** (large N), falling only 6 dB/octave. Tapering softens the edge: **lower sidelobes, wider beam, less gain** — the same trade as FFT windows (ADI make this analogy explicitly [5]).
- **Taper efficiency** η_t = |Σa_n|²/(N Σ|a_n|²) is the directivity (and receive-SNR) loss factor for an array with independent per-element noise. Typical: Taylor 25 dB ≈ −0.45 dB, Taylor 30 dB ≈ −0.68 dB, Taylor 40 dB ≈ −1.15 dB, Hamming −1.44 dB, Blackman ≈ −2.2 dB (N = 32, verified).
- **Dolph–Chebyshev** [2]: match the AF, a polynomial of degree N−1 in cos(ψ/2), to T_{N−1}(x₀cos(ψ/2)) with x₀ = cosh(arccosh R/(N−1)) → **all sidelobes exactly equal** at 1/R and the narrowest beam for that level. 8 elements, 30 dB: weights 0.262/0.519/0.812/1, HPBW 16.45° vs 12.80° uniform; spacing must stay below d/λ = 1 − arccos(1/x₀)/π.
- **Taylor n̄** [3]: keep the first n̄−1 nulls Chebyshev-like (near-equal sidelobes at the design level) and let the rest fall like the uniform sinc. Robust, monotonic weights, higher efficiency than Chebyshev for large N; the standard radar taper. n̄ = 3–6 is typical; small arrays can't reach the design level (N = 8, 30 dB, n̄ = 4 → only −28.3 dB).
- **Binomial** weights (1:4:6:4:1…) give *no* sidelobes at d = λ/2 but a wide beam (HPBW ≈ 1.06/√(N−1) rad), very low efficiency and huge dynamic range (1:6435 for N = 16). Mostly of historical interest.
- **Random errors set a floor**: average sidelobe level ≈ **(σ_a² + σ_φ²)/(N η_t)** relative to the beam peak (σ_a fractional amplitude, σ_φ radians); Monte Carlo agrees within 0.1 dB. To hold a −30 dB design with 64 elements, you need roughly **0.5 dB / 3° rms** (floor −40 dB); 1 dB / 5° gives a −34 dB floor and a median far-out peak sidelobe of −26 dB.
- **Element failures**: fraction p dead → gain loss 20 log(1−p) (−0.45 dB at 5%) and floor ≈ p(1−p)/(N η_t) (−30.6 dB for 5% of 64).
- **Practical small arrays**: 8 elements with 0.5 dB / 2.8° steps (ADAR1000-class) and 0.3 dB / 3° calibration residuals turn a 25 dB design into ≈ −21.9 dB (median) and a 30 dB design into ≈ −24.5 dB. Design 5 dB better than you need.
- **Monopulse**: split the aperture into halves, form Σ and Δ; Δ/Σ gives an angle error signal (16 × λ/2 uniform: 0.22 per degree). A Taylor-weighted Σ with sign-flipped halves gives poor Δ sidelobes (≈ −10 dB); the Bayliss taper is the Δ-pattern analogue of Taylor.
- *Monopulse slope k_m, angle accuracy σ_θ = θ/(k_m√(2 SNR)) and tracking loops: [radar tracking](../11-radar/radar-tracking-monopulse-and-trackers.md).*

## Intuition (no math)

**The edge is where sidelobes come from.** The array pattern is the Fourier transform of how strongly each part of the aperture is excited. A uniform excitation stops abruptly at the edges; an abrupt step contains lots of high "spatial frequencies", and those show up as sidelobes far from the main beam. Tapering — exciting the edge elements more weakly than the centre — smooths the step. It is exactly what a window does to an FFT: Hamming, Hann, Blackman and Chebyshev windows are array tapers with different names ([FFT windows](../14-sdr-dsp/fft-spectral-analysis-windows.md)).

**The price.** A tapered aperture uses its edges less, so it behaves like a slightly smaller aperture: the beam gets wider (typically 15–40%) and the gain drops (0.4–2 dB). On *receive* with a digital array, you apply the taper in software, and the loss is just an SNR loss η_t. On *transmit*, tapering means running some PAs below full power — you waste PA capability — so many radars transmit uniform and taper only on receive.

**Chebyshev vs Taylor.** Chebyshev pushes *every* sidelobe to exactly the same level: optimal in the "narrowest beam for a given peak sidelobe" sense, but it spends effort holding far-out sidelobes up at the design level and for large arrays its edge elements become weirdly large ("edge spikes"), wasting power and making it error-sensitive. Taylor keeps only the first few sidelobes at the design level and lets the rest decay naturally; the weights are smooth, efficient and robust. For big arrays, Taylor is almost always preferred.

**Errors refill what the taper removed.** Every amplitude or phase error acts like a small random extra source whose power spreads over all directions. With a few percent error on each of N elements, this forms a noise-like floor at about (error variance)/N below the main beam. A −40 dB taper is worthless if your calibration only supports a −30 dB floor.

## The math

Conventions as in [array factor](array-factor-linear-arrays.md): symmetric real weights a_n, d = λ/2 unless stated, ψ = kd(u − u₀), u = sinθ.

### Level 1 — definitions

| Quantity | Definition | Meaning |
|---|---|---|
| Sidelobe level (SLL) | max sidelobe power / main-beam power (dB) | peak, not average |
| Taper efficiency | η_t = \|Σa_n\|²/(N Σ\|a_n\|²) | directivity/SNR loss vs uniform (independent element noise) |
| Beam broadening | HPBW_taper / HPBW_uniform | typically 1.1–1.8 |
| Edge taper | a_edge/a_max (dB) | Taylor 30 dB: ≈ −12 dB |
| Error floor | ≈ (σ_a² + σ_φ²)/(N η_t) | average sidelobe from random errors |

### Level 2 — derivations

**(a) Taper efficiency.** Directivity of a λ/2-spaced array of isotropic elements is D = |Σa|²/Σ|a|² ([array factor](array-factor-linear-arrays.md) §(f)); uniform gives N, so D_taper/D_uniform = |Σa|²/(NΣ|a|²) = η_t. By the Cauchy–Schwarz inequality η_t ≤ 1 with equality only for uniform weights: **the uniform taper maximises gain**; everything else trades gain for sidelobes. The same ratio is the white-noise SNR gain loss on receive.

**(b) Binomial array.** Choose AF = (1 + z)^{N−1} with z = e^{jψ}: all N−1 zeros sit at z = −1 (ψ = π). At d = λ/2 the visible region is exactly one turn of the unit circle, so the only zero is at the edge of visible space and the pattern |cos(ψ/2)|^{N−1} has no sidelobes at all. Weights are binomial coefficients: 1:2:1, 1:4:6:4:1, … The beam is |cos^{N−1}(πu/2)|, HPBW ≈ 1.06/√(N−1) rad (verified to <0.6% for N = 3–16), D ≈ 1.77√N for large N [6] — compare N for uniform. N = 16 has a 6435:1 amplitude ratio. That's why nobody uses it beyond N ≈ 5.

**(c) Dolph–Chebyshev (derivation).** For a symmetric array with centre reference, AF(ψ) = Σ a_n cos(mψ/2) summed over odd (even N) or even (odd N) m ≤ N−1. Because cos(mx) is a polynomial of degree m in cos x (it *is* T_m(cos x)), AF is a polynomial P(x) of degree N−1 in x = cos(ψ/2). Chebyshev polynomials T_M(x) (M = N−1) oscillate between ±1 for |x| ≤ 1 and grow monotonically for x > 1 — faster than any other polynomial of degree M bounded by 1 on [−1, 1] ([special functions](../00-math-foundations/special-functions-bessel-sinc.md)). Set
$$AF(\psi) = T_{N-1}\!\big(x_0\cos(\psi/2)\big),\qquad T_{N-1}(x_0) = R\ \Rightarrow\ x_0 = \cosh\!\Big(\frac{\operatorname{arccosh}R}{N-1}\Big).$$
At the beam peak (ψ = 0) the argument is x₀ and AF = R; as ψ moves away, the argument x₀cos(ψ/2) enters [−1, 1] where |T| ≤ 1: every sidelobe peaks at exactly 1, i.e. SLL = 1/R. Among all polynomials of degree N−1 with |P| ≤ 1 on that interval and P = R at the peak, the Chebyshev one reaches its first zero soonest — the narrowest main beam (Dolph's optimality [2]). **Weights**: AF is a trigonometric polynomial with N coefficients, so sampling it at N points ψ_m = 2πm/N and inverting the DFT gives the weights exactly. `tools/verify/array_taper.py` §1 implements this and matches `scipy.signal.windows.chebwin` to 4e−16: N = 8, 30 dB → x₀ = 1.18066, weights 0.262, 0.519, 0.812, 1 (symmetric), all sidelobes −30.00 dB, HPBW 16.45°, η_t = 0.842; the Balanis/Nikolova N = 10, 26 dB example (x₀ = 1.08515, edge-normalised weights 1 : 1.357 : 1.974 : 2.496 : 2.789 [6]) is reproduced as 1 : 1.355 : 1.968 : 2.479 : 2.769 (their hand calculation rounds x₀; 0.8% difference at the centre). **Spacing limit**: at endfire the argument is x₀cos(πd/λ); it must stay ≥ −1 or an endfire lobe exceeds the design level: d/λ ≤ 1 − arccos(1/x₀)/π (0.822λ for N = 8, 30 dB) [6].
**Beamwidth** for large N follows from the continuous limit (the "ideal" Chebyshev/Taylor pattern cos(π√(u'² − A²)), u' = Nd·u/λ, A = arccosh(R)/π): half power where cosh(π√(A² − u'²)) = R/√2, giving
$$\mathrm{HPBW}_u \approx \frac{2\lambda}{\pi N d}\sqrt{\operatorname{arccosh}^2 R - \operatorname{arccosh}^2(R/\sqrt2)} .$$
This is a lower bound; finite arrays are wider (30 dB: ideal ×1.19 of uniform; exact N = 16 ×1.25, N = 8 ×1.29). The textbook broadening factor f = 1 + 0.636[(2/R)cosh√(arccosh²R − π²)]² (valid only for SLL ≳ 21 dB) gave 5–10% *less* broadening than the exact patterns in our checks (N = 8–32) — use exact numerics.

**(d) Taylor n̄ (line source, sampled).** Taylor [3] started from the ideal pattern above (all sidelobes equal, unrealisable because it has infinite far-out sidelobes and needs an edge singularity) and the uniform sinc (zeros at integers u' = n). He keeps the ideal pattern's zeros for n < n̄, stretched by σ so that the n̄-th zero lands exactly on the integer n̄, then uses the uniform zeros beyond:
$$u'_n = \pm\sigma\sqrt{A^2 + (n-\tfrac12)^2}\ (n<\bar n),\qquad u'_n = \pm n\ (n\ge\bar n),\qquad \sigma = \frac{\bar n}{\sqrt{A^2+(\bar n-\tfrac12)^2}} .$$
The aperture distribution is a short cosine series g(p) = 1 + 2Σ_{m=1}^{n̄−1}F(m)cos(mp) with
F(m) = (−1)^{m+1}·Π_{n=1}^{n̄−1}[1 − m²/(σ²(A² + (n−½)²))] / (2Π_{j≠m}(1 − m²/j²)), and sampling g at the element positions gives array weights. σ > 1 is the beam broadening relative to the ideal pattern. Our own implementation equals `scipy.signal.windows.taylor` to 2e−16 (script §3). Results: N = 32, n̄ = 5, 30 dB → −30.2 dB, HPBW ×1.267, η_t = 0.855 (−0.68 dB), edge −12.0 dB; N = 32, n̄ = 6, 40 dB → −40.1 dB, ×1.41, η_t 0.767, edge −19.2 dB. **Small N**: sampling a line source with few elements misses the design level (N = 8: 25 dB/n̄ = 3 → −24.4 dB; 30 dB/n̄ = 4 → −28.3 dB). **Choosing n̄**: larger n̄ → slightly higher efficiency and narrower beam, but eventually the taper becomes non-monotonic with rising edge elements; numerically (N = 200) the largest monotonic n̄ is 3, 5, 7, 9, 11 for 20, 25, 30, 35, 40 dB. Stay a little below that.

**(e) Cosine-on-pedestal and window families.** a(x) = p + (1−p)cos^m(πx/L) is the classic hardware-friendly taper (and the illumination of horn-fed reflectors, [horns & reflectors](../08-antennas/horn-reflector-aperture-antennas.md)). N = 32 results (script §4): cos on −20 dB pedestal: −22.7 dB SLL, ×1.27, η_t = 0.856; cos² on −20 dB pedestal: −39.8 dB, ×1.44, 0.749; Hamming: −41.8 dB, ×1.50, 0.717 (−1.44 dB); Hann: −31.5 dB, ×1.58, 0.688; Blackman: −58.1 dB, ×1.80, 0.597; Gaussian (σ = N/5): −43.1 dB, ×1.55, 0.692. Taylor gives the best efficiency for a given peak SLL among smooth tapers; Chebyshev gives the narrowest beam.

**(f) Random excitation errors → sidelobe floor.** Write each excitation as a_n(1 + δ_n)e^{jε_n} with independent zero-mean δ_n (variance σ_a²) and ε_n (variance σ_φ²). For small errors the error field Σa_n(δ_n + jε_n)e^{jkx_n u} has expected power (σ_a² + σ_φ²)Σ|a_n|² in *every* direction (no preferred direction, because the errors are uncorrelated), while the main-beam power is |Σa_n|². The ratio is
$$\overline{SLL}_{err} \approx \frac{\sigma_a^2+\sigma_\phi^2}{\;|\sum a_n|^2/\sum|a_n|^2\;} = \frac{\sigma_a^2+\sigma_\phi^2}{N\,\eta_t},$$
the classic tolerance result (Elliott [8]; Mailloux ch. 7 [1]). The expected main-beam power drops by |E e^{jε}|² = e^{−σ_φ²} (Gaussian phase errors). Monte Carlo (script §5, 1500 trials each): N = 64 Taylor 30 dB with 1 dB / 5° → floor −34.20 dB vs formula −34.19 dB; 0.5 dB / 3° → −39.57 vs −39.56 dB; N = 8 uniform with 1 dB / 10° → −22.5 vs −22.6 dB. The *peak* sidelobe is what specs care about: the actual pattern is the design pattern plus a Rayleigh-like random field, so with a −34 dB floor on a −30 dB design the median far-out peak is ≈ −26 dB and the 90th percentile −24.7 dB (N = 64). Amplitude error in dB converts as σ_a ≈ 0.115 σ_dB. Correlated errors (e.g. one bad subarray, a temperature gradient) are worse than this formula: they produce *lobes*, not a floor.

**(g) Element failures.** If each element fails (a_n → 0) independently with probability p, the mean excitation is (1−p)a_n and the fluctuation variance is p(1−p)a_n². Main beam: 20 log(1−p). Floor: p(1−p)Σa²/((1−p)²|Σa|²)… normalised to the degraded peak ≈ p/((1−p)Nη_t); Monte Carlo agrees with p(1−p)/(Nη_t) relative to the *undegraded* peak within 0.2 dB (N = 64: 2% → −34.3 dB, 5% → −30.7 dB, 10% → −27.8 dB). Graceful degradation is a real advantage of active arrays over a single-PA feed.

**(h) Monopulse sum and difference.** For tracking, form Σ = Σ a_n s_n and Δ = Σ sgn(x_n)a_n s_n (halves in anti-phase). Near boresight Δ/Σ ≈ j·k_m·u, a linear, SNR-independent angle discriminant — the basis of tracking radars and some ground-station trackers. 16 × λ/2, uniform: slope 12.6 per unit u = 0.22 per degree (script §6); Taylor-30 halves: 0.17 per degree. The Δ pattern of a sign-flipped Taylor taper has high sidelobes (−9.6 dB vs its peak) because the weights jump at the centre; **Bayliss** (1968) derived the Δ-pattern analogue of Taylor, with controlled sidelobes; large radars use separate Σ (Taylor) and Δ (Bayliss) weightings from the same elements. Angle-noise estimate: σ_θ ≈ 1/(slope·√(2·SNR)) — for the 16-element uniform case at 20 dB SNR, ≈0.3° (≈1/20 of the 6.4° beam; not simulated here — see [DOA](adaptive-beamforming-doa.md) for estimator variance and the CRB).

### Level 3 — synthesis beyond tapers

- **Schelkunoff zero placement**: AF = a_{N−1}Π(z − z_i); put zeros at the u-values of known interferers (a fixed null-steered pattern). Moving one zero to u_j is equivalent to subtracting a scaled beam pointed at u_j — the deterministic ancestor of adaptive nulling ([adaptive beamforming](adaptive-beamforming-doa.md)).
- **Woodward–Lawson** (frequency-sampling): sum of N orthogonal sinc beams at u_m = m·λ/(Nd) with chosen amplitudes → shaped beams (sector/cosecant²). **Fourier/window** design: truncate the ideal aperture distribution and window it.
- **Convex optimisation** (min-max SLL with nulls, constraints on dynamic range) solves modern problems exactly for moderate N (CVX/cvxpy); phase-only synthesis serves TX arrays with saturated PAs.
- **Planar arrays**: separable (x-Taylor × y-Taylor) weights give low sidelobes in principal planes and much lower on diagonals; circular-aperture Taylor (Taylor 1960) or Hansen one-parameter distributions give rotationally uniform sidelobes. Efficiency of a separable taper is η_x·η_y.
- **Density tapering (thinning)**: keep all active elements at full power (efficient TX) but remove elements with probability rising toward the edge; the average pattern follows the taper, with a random floor ≈ 1/N_active.
- **Adaptive arrays** go beyond fixed tapers: they place nulls on actual interferers from data (MVDR/LCMV), achieving −40 to −60 dB rejection in specific directions without low sidelobes everywhere.

## Design equations & rules of thumb

| Taper (N = 32 unless stated) | Peak SLL | HPBW ×uniform | η_t (dB) | Edge |
|---|---|---|---|---|
| Uniform | −13.2 dB | 1.00 | 0 | 0 dB |
| cos on −10 dB pedestal | −20.0 | 1.16 | −0.33 | −9 dB |
| Taylor 25 dB n̄=3 (N=8) | −24.4 | 1.20 | −0.45 | −8 dB |
| Dolph 30 dB (N=16) | −30.0 | 1.25 | −0.64 | — |
| Taylor 30 dB n̄=5 | −30.2 | 1.27 | −0.68 | −12 dB |
| Taylor 35 dB n̄=5 (N=16) | −34.8 | 1.34 | −0.93 | −15 dB |
| cos² on −20 dB pedestal | −39.8 | 1.44 | −1.25 | −20 dB |
| Taylor 40 dB n̄=6 | −40.1 | 1.41 | −1.15 | −19 dB |
| Hamming | −41.8 | 1.50 | −1.44 | −22 dB |
| Blackman | −58.1 | 1.80 | −2.24 | −50 dB |

| Rule | Validity |
|---|---|
| x₀ = cosh(arccosh R/(N−1)) | Dolph–Chebyshev design |
| d/λ ≤ 1 − arccos(1/x₀)/π | Chebyshev no endfire lobe |
| Error floor ≈ (σ_a² + σ_φ²)/(Nη_t); σ_a ≈ 0.115·σ_dB | uncorrelated errors |
| Peak sidelobe ≈ design SLL degraded by floor (median ≈ floor + 8 dB for N = 64) | Monte Carlo guidance |
| Failures p: ΔG = 20 log(1−p); floor ≈ p(1−p)/(Nη_t) | random failures |
| Design margin: target SLL − 5 dB | small DIY arrays with 0.3–0.5 dB / 3° residuals |

## Worked examples

**Example 1 — tapering the 8-element 5.8 GHz array.** (Script §7.) Options, ideal → with ADAR1000-class 0.5 dB amplitude steps, 2.8° phase steps at 30° scan and 0.3 dB / 3° rms calibration residuals (400 Monte Carlo trials):

| Taper | Ideal SLL | HPBW | η_t | Realistic SLL (median / 90th pct) |
|---|---|---|---|---|
| Uniform | −12.8 dB | 12.8° | 0 dB | −12.4 / −11.9 dB |
| Taylor 25 dB n̄=3 | −24.4 dB | 15.3° | −0.45 dB | −21.4 / −20.1 dB |
| Dolph 25 dB | −25.0 dB | 15.4° | −0.48 dB | −21.9 / −20.4 dB |
| Dolph 30 dB | −30.0 dB | 16.5° | −0.75 dB | −24.5 / −22.8 dB |
| Hamming | −33.6 dB | 20.4° | −1.75 dB | −24.7 / −22.1 dB |

Conclusion: for an 8-element DIY array, a 25–30 dB Chebyshev/Taylor design realistically delivers −20 to −25 dB; Hamming costs 1.75 dB and 60% more beamwidth for no practical gain over Dolph-30. On *receive* with digital weights, the taper is free to change per application (uniform for max SNR when there's no interference; tapered when a strong signal elsewhere must be suppressed).

**Example 2 — error budget for a 64-element −30 dB receive array.** Taylor 30 dB n̄ = 5: η_t = 0.855. To keep the error floor 10 dB below the design (−40 dB): σ_a² + σ_φ² ≤ 64 × 0.855 × 10⁻⁴ = 0.0055. Split: σ_a = 0.5 dB (0.0576 → 0.0033) and σ_φ = 2.7° (0.047 rad → 0.0022). Monte Carlo with 0.5 dB / 3°: floor −39.6 dB, median far-out peak −29.5 dB (script §5). With 1 dB / 5° the floor rises to −34 dB and the median peak to −26 dB: the array no longer meets −30 dB in most builds. Also allow for failures: 2% dead elements add a −34 dB floor on their own.

**Example 3 — binomial vs uniform, N = 5.** Binomial 1:4:6:4:1 at λ/2: no sidelobes, HPBW 30.3°, D = 3.66 (5.6 dBi), η_t = 0.73. Uniform: −12 dB sidelobes, HPBW 20.8°, D = 5 (7.0 dBi). A Dolph 25 dB taper would sit in between (≈23°, ≈6.6 dBi).

**Example 4 — monopulse for a tracking ground station.** Two halves of a 16-element λ/2 array (or two antennas of a 2-element interferometer), uniform: Δ/Σ slope 0.22/° near boresight. With 20 dB SNR per pulse/sample, the angle-noise estimate ≈ 1/(0.22·√200) ≈ 0.3° — the servo (or electronic beam) can hold a rocket within ≈1/20 of the 6.4° beam. At 915 MHz the same electrical array is 2.6 m long, which is why hobby trackers use a pair of Yagis in a Σ/Δ hybrid, or GPS-telemetry pointing, instead.

## Practical notes
- **Where to apply the taper.** Digital arrays: in the DSP (free, per-beam). Analog beamformer ICs: VGA/attenuator per channel (ADAR1000 ≥ 31 dB range in ≤ 0.5 dB steps) — but attenuators change phase slightly; calibrate phase *at each gain setting* ([phase shifters & components](phase-shifters-ttd-components.md)). Passive corporate feeds: unequal Wilkinson splits (hard beyond ≈10 dB ratios on PCB).
- **Transmit tapering wastes PA power**: the total radiated power is Σ|a_n|² × P_max; with a Taylor-30 taper and equal PAs you give up ≈1.5–2 dB of EIRP (η_t plus the unused PA headroom). Many radars use uniform TX + tapered RX.
- **Tapers interact with noise figure**: in an analog beamformer, attenuating an element *after* its LNA hardly changes system NF; attenuating *before* the LNA does. Put gain control after the LNA.
- **Measure sidelobes at > 2L²/λ** with an absorber-lined path; ground reflections easily fill −25 dB sidelobes in a car park test.
- **Chebyshev for large N** has edge weights that rise ("spiky" ends) and becomes error-sensitive — use Taylor above ~20 elements.

## Common mistakes & misconceptions
- **"A −40 dB taper gives −40 dB sidelobes."** Only with calibration errors ≲ 0.25 dB / 1.5° for N ≈ 64 (floor −44 dB); otherwise the random floor dominates.
- **"Tapering improves SNR."** It *reduces* white-noise SNR by η_t; it improves the signal-to-*interference* ratio when interference arrives in the sidelobes.
- **"Tapering narrows the beam."** It widens it (15–80%).
- **Using a window with zero end-weights** (the symmetric Hann/Blackman in many libraries): the end elements then do nothing — use N + 2-point windows trimmed, or a periodic variant.
- **Expecting the design SLL from a small array** (N = 8, Taylor 30 dB n̄ = 4 → −28.3 dB). Check the sampled pattern, not the continuous design.
- **Choosing n̄ too large** → non-monotonic weights with rising edges.
- **Ignoring amplitude-dependent phase** of step attenuators — it is a correlated error, producing lobes rather than a floor.
- **Tapering a transmit array with saturated PAs** by "turning down" some PAs — their efficiency drops and total EIRP falls more than η_t suggests.

## How to simulate / verify
- `tools/verify/array_taper.py` (~20 s): own Dolph–Chebyshev (polynomial + inverse DFT) and Taylor n̄ (Taylor 1955 formulas) vs scipy windows; equal-ripple check; large-N beamwidth formula; binomial beamwidth and directivity; window/pedestal comparison table; Monte-Carlo random-error floors, gain loss, peak-sidelobe percentiles, failures; monopulse Σ/Δ slopes and Δ sidelobes; 8-element realistic-quantisation table.
- scipy: `scipy.signal.windows.chebwin(N, at=SLL)` and `scipy.signal.windows.taylor(N, nbar, sll)` produce array weights directly (normalise to max = 1).
- For planar arrays use the outer product of two linear tapers (separable) or evaluate a circular Taylor on the element radii.

## Open questions / gaps
- Bayliss difference taper not implemented numerically (only described); a Bayliss implementation would let the DIY page quantify a proper Σ/Δ tracking array.
- The origin/statement of the "largest monotonic n̄" rule of thumb in the literature (often linked to 2A² + ½) was not verified; the page reports only our numerical monotonicity limits.
- The textbook Dolph beam-broadening factor formula underestimated exact broadening by 5–10% in our checks; its original derivation (Van der Maas / Stegen) was not consulted.

## Sources
1. R. J. Mailloux, *Phased Array Antenna Handbook*, 2nd ed., Artech House, 2005, ch. 3 "Pattern synthesis for linear and planar arrays" and ch. 7 "Array error effects". (textbook)
2. C. L. Dolph, "A current distribution for broadside arrays which optimizes the relationship between beam width and side-lobe level," *Proc. IRE* 34(6):335–348, 1946. (peer-reviewed)
3. T. T. Taylor, "Design of line-source antennas for narrow beamwidth and low side lobes," *IRE Trans. Antennas Propag.* AP-3(1):16–28, 1955, doi:10.1109/TPGAP.1955.5720407. (peer-reviewed)
4. R. C. Hansen, *Phased Array Antennas*, 2nd ed., Wiley, 2009 — linear/planar synthesis, Taylor n̄ properties, tolerances. (textbook)
5. P. Delos, B. Broughton, J. Kraft, "Phased Array Antenna Patterns — Part 3: Sidelobes and Tapering," *Analog Dialogue* 54(3), July 2020 — taper/window analogy. (app note)
6. N. K. Nikolova, "Lecture 15: Linear arrays — Part III (binomial and Dolph–Tschebyscheff arrays)," McMaster University notes, 2025, following Balanis 4e §6.8 — binomial HPBW 1.06/√(N−1), D ≈ 1.77√N, N = 10/26 dB worked example, d_max = λ(1 − arccos(1/x₀)/π). (lecture notes)
7. C. A. Balanis, *Antenna Theory*, 4th ed., Wiley, 2016, §6.8 (nonuniform arrays: binomial, Dolph–Tschebyscheff) — including the beam-broadening-factor formula checked here. (textbook)
8. R. S. Elliott, "Mechanical and electrical tolerances for two-dimensional scanning antenna arrays," *IRE Trans. Antennas Propag.* 6(1):114–120, 1958 — sidelobe level vs random errors. (peer-reviewed; abstract read)
9. E. T. Bayliss, "Design of monopulse antenna difference patterns with low sidelobes," *Bell Syst. Tech. J.* 47(5):623–650, 1968 — difference-pattern analogue of Taylor. (peer-reviewed; from standard-text citation, not read)
10. H. L. Van Trees, *Optimum Array Processing*, Wiley, 2002, ch. 3 "Synthesis of linear arrays and apertures" — windows, Dolph–Chebyshev, Taylor, Villeneuve, null steering, least-squares synthesis. (textbook)
11. `tools/verify/array_taper.py` — all numerical values marked "script" and the tables. (own verification)
