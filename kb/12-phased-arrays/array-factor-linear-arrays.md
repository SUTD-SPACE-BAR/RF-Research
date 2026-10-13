---
title: Array factor and linear arrays — pattern multiplication, beamwidth, nulls, directivity, array gain
domain: 12-phased-arrays
slug: array-factor-linear-arrays
tags: [array-factor, uniform-linear-array, ULA, pattern-multiplication, broadside, endfire, hansen-woodyard, beamwidth, HPBW, nulls, sidelobes, directivity, array-gain, SNR-gain, schelkunoff, far-field]
prerequisites: [../00-math-foundations/complex-numbers-and-phasors.md, ../00-math-foundations/fourier-series-and-transform.md, ../08-antennas/antenna-fundamentals.md]
related: [beam-steering-grating-lobes.md, planar-arrays-element-pattern-coupling.md, tapering-sidelobe-control.md, adaptive-beamforming-doa.md, beamforming-architectures.md, diy-phased-array-projects.md, ../00-math-foundations/special-functions-bessel-sinc.md, ../08-antennas/patch-antennas.md, ../08-antennas/yagi-uda-and-log-periodic.md, ../07-noise-linearity/thermal-noise-and-noise-temperature.md, ../02-electromagnetics/near-field-far-field.md, ../11-radar/mimo-radar-virtual-arrays.md, ../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md]
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Array factor and linear arrays

## Questions this page answers
- What is an "array factor" and where does the sin(Nx)/sin(x) formula come from?
- Why is the pattern of an array "element pattern × array factor", and when is that wrong?
- How narrow is the beam of an N-element array with half-wavelength spacing?
- Where are the nulls and how high is the first sidelobe of a uniform array?
- What is the difference between a broadside and an endfire array, and what is the Hansen–Woodyard trick?
- How do I calculate the directivity of an array — is it just 10·log10(N) + element gain?
- If I combine N receivers coherently, how much does my SNR improve, and why?
- Why does a transmit array's EIRP grow as N² but its receive G/T only as N?
- How far away do I need to be to measure an array's far-field pattern?
- Is an array of 4 dipoles better than a Yagi for my ground station?
- What is the connection between an array pattern and a Fourier transform / an FIR filter?
- Why does array directivity stay the same when I scan a λ/2-spaced array of isotropic elements, even though the beam gets wider?

## TL;DR
- A linear array's far-field is the **sum of the element fields with phase kx_n sinθ** (θ from broadside). For identical elements it factorises: **E(θ) = E_element(θ) · AF(θ)** ("pattern multiplication"), with AF(θ) = Σ w_n e^{jkx_n sinθ}.
- Uniform N-element array, spacing d, steered to θ₀: |AF| = |sin(Nψ/2) / (N sin(ψ/2))|, ψ = kd(sinθ − sinθ₀). It is exactly the DTFT of the weights — the array is a **spatial FIR filter** and the pattern is the Fourier transform of the aperture illumination.
- **Beamwidth** (HPBW) ≈ **0.886 λ/(N d cosθ₀)** rad = 50.8°·λ/(N d cosθ₀). 8 elements at λ/2 → 12.8° broadside, 14.8° at 30° scan (numerically verified). Beamwidth depends on the **aperture length Nd**, not on N alone.
- **Nulls** at sinθ = sinθ₀ ± mλ/(Nd); **first sidelobe** −13.26 dB for large N, but higher for small arrays: −11.3 dB (N=4), −12.8 dB (N=8), −13.15 dB (N=16) (verified).
- **Directivity** of isotropic elements: D = |Σa_n|² / ΣΣ a_m a_n* e^{−jk(x_m−x_n)u₀} sinc(k(x_m−x_n)); for d = λ/2 this collapses to **D = N at every scan angle**; for general d, broadside D ≈ 2Nd/λ; ordinary endfire D ≈ 4Nd/λ; Hansen–Woodyard endfire ≈ 1.8× more (exact sums give 1.76–1.80 for N = 5–100).
- "**10 log N + element gain**" is an *upper-bound-type approximation*: 8 elements with a cosθ (6 dBi) element at λ/2 give 14.1 dBi, not 15.0 dBi, because the elements' effective areas overlap (see [planar arrays & coupling](planar-arrays-element-pattern-coupling.md) for the Hannan limit 4πA/λ²).
- **Array (SNR) gain**: coherent signal amplitudes add (power N²), uncorrelated receiver noise powers add (N) → SNR × N (+3 dB per doubling). With a taper w, gain = |Σw|²/Σ|w|² ≤ N. Against isotropic *external* noise the array gain equals the directivity.
- **Transmit**: N PAs × P each, coherently combined → EIRP ∝ **N²** (N× power and N× gain). **Receive** G/T ∝ N.
- Far field starts at ≈ **2L²/λ** (L = aperture length): 8-el 5.8 GHz (L ≈ 0.18–0.21 m) → ≈1.3–1.7 m; ADI Phaser (L ≈ 0.1 m at 10.25 GHz) → ≈0.7 m.

## Intuition (no math)

**An array is a set of ears listening to the same wave at slightly different times.** A plane wave arriving from angle θ reaches each element a little earlier or later than its neighbour — by d·sinθ/c. If you add the element outputs directly, they only add perfectly in phase when the wave comes from straight ahead (broadside). From other directions the contributions have a progressive phase slip, and they partly cancel. The array *is* a direction-dependent filter: in space it does exactly what an FIR filter does in time — the taps are the element weights, and "frequency" is replaced by the direction's spatial frequency sinθ/λ.

**Steering is just delaying.** If you add a delay (or, for a narrowband signal, a phase shift) to each element that exactly undoes the arrival-time differences for direction θ₀, all contributions from θ₀ now add in phase: the beam points at θ₀. That's the whole idea of a phased array; [beam steering & grating lobes](beam-steering-grating-lobes.md) takes it further.

**Why the beam has a width.** Move a little off the beam direction and the phase slip between the first and last element grows. When the slip across the whole aperture reaches one full cycle (360°), the contributions go all the way around the phasor circle and sum to zero: that's the first null. The slip across the aperture is (aperture length × sin of the offset)/λ, so the first null is at sin(offset) ≈ λ/L. Longer aperture → narrower beam. The half-power point is a bit less than half-way to the null: ≈0.886λ/L for the full width.

**Why sidelobes exist.** Past the first null the phasors wrap around more than once but not an integer number of times, so a small residue remains: the sidelobes. For equal weights the biggest residue (first sidelobe) is about 21.7% of the main-beam field (−13.26 dB). Tapering the weights toward the edges softens the "edge" of the aperture and reduces these residues ([tapering](tapering-sidelobe-control.md)) — the same trade as windowing an FFT.

**Pattern multiplication.** If every element is identical and points the same way, each contributes "its own pattern × a phase". The phases depend only on positions; the pattern is common. So the total pattern is element pattern × array factor. A patch element that already favours the forward direction multiplies the array factor by its own broad forward beam: the total beam can't point where the elements themselves don't radiate.

**Array gain is about correlation.** The wanted signal is the *same* waveform at every element (after steering): amplitudes add, so N elements give N² in power. Each receiver's thermal noise is *independent*: powers add, so noise grows only N times. SNR improves N-fold. This is exactly why coherent (phase-locked) receivers matter: two unsynchronised receivers can't add amplitudes, only powers — no array gain ([beamforming architectures](beamforming-architectures.md)).

**The Fourier picture.** The far-field pattern, as a function of u = sinθ, is the Fourier transform of the illumination along the aperture. A uniform (rectangular) illumination gives a sinc-like pattern; the aperture length plays the role of the pulse duration, and the beamwidth plays the role of the bandwidth. Everything you know about windows, leakage and resolution in spectral analysis transfers ([Fourier](../00-math-foundations/fourier-series-and-transform.md)).

## The math

**Geometry and conventions (used on all 12-phased-arrays pages).** Elements at positions x_n = n·d (n = 0 … N−1) on the x axis; the array normal (broadside) is z. θ is measured **from broadside** in the x–z plane, and **u = sinθ** is the direction cosine along the array axis. Wavenumber k = 2π/λ (rad/m). Time convention e^{+jωt}. This is the phased-array convention (Mailloux, Hansen, ADI [1][2][5]). **Balanis measures θ from the array axis** [3], so his ψ = kd cosθ + β uses cos instead of sin, and his "β" is the progressive phase; translate with θ_Balanis = 90° − θ_here.

### Level 1 — the results and what each symbol means

Steering phase between adjacent elements, to point the beam at θ₀:
$$\Delta\Phi = -\,k d\sin\theta_0 = -\frac{2\pi d}{\lambda}\sin\theta_0\quad\text{(rad)}.$$
(The sign depends on whether you think of it as a lag applied to the element the wave reaches first; its magnitude 2πd sinθ₀/λ is what matters. For d = λ/2, |ΔΦ| = π sinθ₀.)

Array factor of a uniform array (weights w_n = e^{jnΔΦ}), normalised to 1 at the beam peak:
$$|AF_n(\theta)| = \left|\frac{\sin(N\psi/2)}{N\sin(\psi/2)}\right|,\qquad \psi = kd(\sin\theta-\sin\theta_0).$$

| Quantity | Formula (uniform ULA) | Notes |
|---|---|---|
| Half-power beamwidth | $\Theta_{3} \approx 0.886\,\lambda/(Nd\cos\theta_0)$ rad | valid for N ≳ 8 and not near endfire |
| Nulls | $\sin\theta = \sin\theta_0 \pm m\lambda/(Nd)$, m = 1, 2, … (m ≠ N, 2N …) | first-null beamwidth at broadside ≈ 2λ/(Nd) |
| First sidelobe | −13.26 dB (N→∞); −11.3 (N=4), −12.8 (N=8) dB | near sinθ − sinθ₀ ≈ ±1.43λ/(Nd) |
| Directivity (isotropic elements) | D = N for d = λ/2; D ≈ 2Nd/λ broadside in general | exact formula below |
| SNR gain (receiver noise) | G_A = N (uniform), = \|Σw\|²/Σ\|w\|² (taper) | uncorrelated noise, coherent signal |
| Far-field distance | $r_{ff} \approx 2L^2/\lambda$ | L = aperture length |

### Level 2 — derivations

**(a) From element fields to the array factor.** Element n, at position r_n, radiates a far field that looks like that of an element at the origin, but with a different path length. At a distant point r (unit vector û), |r − r_n| = r − û·r_n + O(r_n²/r). In the amplitude (1/r) the difference is negligible; in the phase it is not, because it is multiplied by k. So each element contributes
$$\mathbf E_n(\mathbf r) \approx w_n\,\mathbf f_n(\hat{\mathbf u})\,\frac{e^{-jkr}}{r}\,e^{+jk\,\hat{\mathbf u}\cdot\mathbf r_n},$$
where f_n is element n's own pattern (vector, about its own phase reference) and w_n its complex excitation. If all elements are **identical and identically oriented** (f_n = f),
$$\mathbf E(\mathbf r) = \mathbf f(\hat{\mathbf u})\frac{e^{-jkr}}{r}\;\underbrace{\sum_n w_n e^{jk\,\hat{\mathbf u}\cdot\mathbf r_n}}_{AF(\hat{\mathbf u})} .$$
That is **pattern multiplication**. For a linear array on x, û·r_n = x_n sinθ cosφ; in the x–z plane (φ = 0) this is x_n u. Assumptions: far field; identical element patterns (this fails for edge elements and whenever mutual coupling makes elements differ — the cure is the *active/embedded element pattern*, see [planar arrays & coupling](planar-arrays-element-pattern-coupling.md)).

**(b) Far-field condition.** The next term in the path-length expansion is (r_n² − (û·r_n)²)/(2r) ≤ (L/2)²/(2r) for an element at the edge of an aperture of length L centred on the origin. Requiring the phase error k(L/2)²/(2r) ≤ π/8 (22.5°, the usual antenna-measurement criterion) gives r ≥ 2L²/λ. Closer than that, the array is "focused at infinity" but you are not at infinity: nulls fill in and sidelobes merge. ADI use L = (N−1)d [5]; using the physical aperture Nd is slightly more conservative.

**(c) Closed form (geometric series).** With w_n = e^{jnΔΦ} = e^{−jnkd u₀}:
$$AF = \sum_{n=0}^{N-1} e^{jn\psi} = \frac{e^{jN\psi}-1}{e^{j\psi}-1} = e^{j(N-1)\psi/2}\,\frac{\sin(N\psi/2)}{\sin(\psi/2)},\qquad \psi = kd(u-u_0).$$
The phase factor e^{j(N−1)ψ/2} disappears if the phase reference is the array centre. |AF| ≤ N with equality only at ψ = 0, ±2π, … (the main beam and, if they are visible, grating lobes — [beam steering](beam-steering-grating-lobes.md)). Verified against brute-force summation to 1e−15 (`tools/verify/array_factor.py` §1).

**(d) Nulls, sidelobes.** The numerator vanishes at Nψ/2 = mπ, i.e. ψ = 2πm/N, which gives u − u₀ = mλ/(Nd). Between nulls, the maxima of the numerator sit near Nψ/2 = (m + ½)π, giving sidelobe levels ≈ 1/(N sin((2m+1)π/2N)) → 2/((2m+1)π) for large N: −13.5, −17.9, −20.8 dB… (the exact first-sidelobe peak is at Nψ/2 = 1.4303π, level −13.26 dB). The envelope falls as 1/ψ, i.e. **6 dB per octave** of angle away from the beam — slowly, which is why uniform arrays need tapering for low far-out sidelobes.

**(e) Half-power beamwidth.** For large N, sin(ψ/2) ≈ ψ/2 near the main beam, so |AF_n| ≈ |sin x / x| with x = Nψ/2. Solving sin x/x = 1/√2 gives x = 1.3916. So the half-power points are at ψ = ±2.7831/N, i.e.
$$\Delta u_{3\,\mathrm{dB}} = \frac{2\times 2.7831}{N k d} = 0.8859\,\frac{\lambda}{Nd}.$$
Near broadside Δu ≈ cosθ₀·Δθ, so Θ₃ ≈ 0.886λ/(Nd cosθ₀). Numerically (script §2): N = 8, λ/2 → 12.80° vs formula 12.69°; N = 16 → 6.36° vs 6.35°; N = 32 → 3.17° exactly. At 60° scan the formula underestimates small arrays (N = 8: 28.8° actual vs 25.4° formula) because the beam becomes asymmetric in θ. For ordinary endfire (beam along the axis), Δu is measured from u = 1 and the result is Θ₃ ≈ 2 arccos(1 − 0.443λ/(Nd)) ≈ 2√(0.886λ/(Nd)) — much wider (N = 16, λ/4: 54.4°).

**(f) Directivity.** The radiated power is ∮|AF|²|f|² dΩ. For isotropic elements on the x axis you can do the integral exactly: rotate coordinates so the array axis is the polar axis, then
$$\oint e^{jks\cos\gamma}\,d\Omega = 2\pi\int_0^\pi e^{jks\cos\gamma}\sin\gamma\,d\gamma = 4\pi\,\frac{\sin ks}{ks}.$$
Expanding |AF|² = Σ_mΣ_n w_m w_n* e^{jk(x_m−x_n)u} and integrating term by term,
$$\boxed{D(u_0) = \frac{\left|\sum_n a_n\right|^2}{\sum_m\sum_n a_m a_n^*\,e^{-jk(x_m-x_n)u_0}\,\operatorname{sinc}\!\big(k(x_m-x_n)\big)}}\qquad(\operatorname{sinc}x=\sin x/x),$$
with steering weights w_n = a_n e^{−jkx_n u₀}. For a uniform array this is D = N² / [N + 2Σ_{m=1}^{N−1}(N−m) sinc(mkd) cos(mkd u₀)] [3]. Three consequences, all confirmed by direct numerical integration over the sphere (script §4):
1. **d = λ/2 (or any multiple of λ/2): sinc(mπ) = 0, so D = |Σa|²/Σ|a|² — equal to N for uniform weights, at every scan angle.** The beam gets wider in θ when scanned, but for a line of isotropic elements the beam is a cone of revolution around the array axis whose "other" dimension shrinks correspondingly. (Real elements with a forward-facing pattern *do* lose gain with scan: [scan loss](beam-steering-grating-lobes.md).)
2. For d ≠ λ/2, broadside, large N: D → 2Nd/λ = 2L/λ (e.g. N = 50, d = 0.4λ: 40.08 exact vs 40). For d = 0.7λ scanned to 45°, a grating lobe appears and D drops from 10.9 to 5.7.
3. d = λ gives D = N again, not 2N: the extra aperture is spent on grating lobes at ±90°.

**(g) Endfire and Hansen–Woodyard.** Steering to u₀ = 1 (along the array axis) needs d < λ/2 to avoid an equal "back" lobe at u = −1 (there ψ = −2kd). Its directivity is ≈4Nd/λ, twice broadside, because the beam is a pencil around the axis rather than a fan. Hansen & Woodyard [7] showed that adding a little *extra* progressive phase, so that ψ at endfire becomes −2.94/N instead of 0, narrows the beam: the main-beam peak drops slightly (it now sits on the shoulder of the sinc) but the beam solid angle drops more. The optimisation (minimise ∫|AF|² for fixed peak; the minimum of the resulting function of z = q(k − p) is at z ≈ −1.47) gives the condition β = −(kd + 2.94/N), often rounded to π/N, and a directivity improvement of 1.789 in the large-N integral approximation [6]. Exact sums (script §4): N = 10, d = λ/4 → ordinary 10.0 (10.0 dB), HW 17.96 (12.54 dB), ratio 1.80; ratios 1.76 (N = 5) to 1.80 (N = 100). The back-lobe condition |ψ(180°)| ≈ π requires d ≈ (N−1)λ/(4N) ≈ λ/4. Price: higher sidelobes, narrow bandwidth, and sensitivity to errors — this is how long Yagis and helices get their gain ([Yagi–Uda](../08-antennas/yagi-uda-and-log-periodic.md), [helical](../08-antennas/helical-antennas.md)).

**(h) Array gain (SNR gain).** Let the element outputs be x_n = s·v_n + n_n, where v_n = e^{jkx_n u₀} is the steering-vector entry for the wanted direction and n_n is noise with covariance E[n nᴴ] = σ²R_n. The beamformer output y = wᴴx has
$$\mathrm{SNR}_{out} = \frac{|s|^2|\mathbf w^H\mathbf v|^2}{\sigma^2\,\mathbf w^H\mathbf R_n\mathbf w},\qquad G_A=\frac{\mathrm{SNR}_{out}}{\mathrm{SNR}_{element}} = \frac{|\mathbf w^H\mathbf v|^2}{\mathbf w^H\mathbf R_n\mathbf w}.$$
- **Uncorrelated receiver noise** (R_n = I, each channel with its own LNA): with conventional weights w = v, G_A = N. For a real taper, G_A = |Σw|²/Σw² (Hamming, N = 8: 5.34 = 7.28 dB instead of 9.03 dB). Monte Carlo confirms N = 2, 4, 5, 8 → 3.01, 6.03, 6.99, 9.03 dB (script §6). Van Trees calls this the *white-noise gain* [4].
- **Isotropic external noise** (a uniform sky/ground noise field): the correlation between isotropic elements a distance s apart is sinc(ks), and G_A becomes exactly the directivity formula of (f). At d = λ/2 both are N; closely spaced elements (d = 0.2λ) share correlated external noise, so their array gain (3.37 for N = 8) is less than N (script §6).
- Consequence for a **receive** system: G/T grows ∝ N (gain ∝ N, noise temperature per channel unchanged). For a **transmit** array of N PAs of P each, the field at the beam peak is N times one element's, so power density ∝ N²: **EIRP = N²·P·G_element** (8 × 20 dBm with 5 dBi elements → 43.1 dBm EIRP). Half of that N² is "more watts", half is "more directivity".

### Level 3 — general forms and limits

- **Arbitrary geometry.** AF(û) = Σ w_n e^{jk û·r_n} holds for any element positions (planar, circular, conformal, random). Circular arrays and UCAs for DF appear in [adaptive beamforming & DOA](adaptive-beamforming-doa.md) and [DIY projects](diy-phased-array-projects.md).
- **Schelkunoff polynomial** [8]. With z = e^{jψ}, AF = Σ a_n z^n is a polynomial of degree N−1; its N−1 roots, placed on the unit circle, are the pattern nulls. As θ sweeps from −90° to +90°, z moves along an arc of the unit circle of length 2kd (radians of ψ). For d = λ/2 the arc is exactly one full circle; for d > λ/2 the arc wraps past a full turn and the main beam is visited twice (grating lobe); for d < λ/2 part of the circle is "invisible" (it corresponds to evanescent, non-radiating spatial frequencies |u| > 1). This picture is the basis of null-steering and Dolph–Chebyshev synthesis ([tapering](tapering-sidelobe-control.md)).
- **Continuous-aperture limit.** A line source of length L with illumination a(x) has AF(u) = ∫a(x)e^{jkxu}dx — a Fourier transform with spatial frequency u/λ. Uniform a(x) → L·sinc(kLu/2) with HPBW 0.886λ/L; so an N-element array behaves like a line source of length **L = Nd** (each element "owns" a cell of width d). The array samples the aperture at spacing d; since the visible spatial frequencies span |u/λ| ≤ 1/λ (bandwidth 2/λ), Nyquist sampling needs d ≤ λ/2 — spatial aliasing = grating lobes ([sampling](../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md)).
- **Superdirectivity.** For d ≪ λ/2, weights can be chosen to give D far above 2L/λ (up to N² for endfire in the limit), but they alternate wildly in sign, the element currents and stored energy blow up, and tolerance/loss sensitivity makes it impractical; Hansen treats this at length [2]. The white-noise gain |wᴴv|²/wᴴw is the standard sensitivity metric: superdirective weights have tiny white-noise gain.
- **Frequency dependence.** AF depends on k: with *phase* weights fixed, the beam moves with frequency (squint); with *time-delay* weights the beam stays put but its width scales as 1/f. Derived in [beam steering](beam-steering-grating-lobes.md).
- **Where pattern multiplication breaks.** Mutual coupling makes each element's embedded pattern different (especially at the edges) and changes the element impedance with scan. Rigorous analysis uses the embedded (active) element patterns f_n(û) in the sum of (a) — still exact, but no longer a product ([planar arrays & coupling](planar-arrays-element-pattern-coupling.md)).

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| ΔΦ = 2πd sinθ₀/λ | narrowband phase steering | d = λ/2, θ₀ = 30° → 90° per element |
| AF_n = sin(Nψ/2)/(N sin(ψ/2)), ψ = kd(sinθ−sinθ₀) | uniform amplitude, equal spacing | — |
| Θ₃ ≈ 0.886λ/(Nd cosθ₀) rad = 50.8°·λ/(Nd cosθ₀) | N ≳ 8, |θ₀| ≲ 60° | 8 × λ/2: 12.8°; 16 × λ/2: 6.4°; 100 × λ/2: 1.0° |
| FNBW ≈ 2λ/(Nd) rad (broadside) | large N | 8 × λ/2: ±14.5° nulls |
| First SLL ≈ −13.26 dB | N ≥ 16 | N = 4: −11.3 dB; N = 8: −12.8 dB |
| D = N (isotropic elements) | d = λ/2, any scan | — |
| D ≈ 2Nd/λ (broadside), 4Nd/λ (endfire), ×1.8 (HW) | d < λ (no grating lobes), large N | — |
| D_array ≲ N·D_element | element effective areas do not overlap; no grating lobes | overestimates by ~1 dB for cosθ elements at λ/2 |
| G_A = \|Σw\|²/Σ\|w\|² | uncorrelated per-channel noise | uniform: N (+3 dB/doubling) |
| EIRP ∝ N²·P_element·G_element | coherent TX, one PA per element | 16 × 20 dBm, 5 dBi → 49 dBm |
| r_ff ≈ 2L²/λ | pattern measurement | 5.8 GHz, L = 0.2 m → 1.5 m |
| Endfire needs d < λ/2; HW needs d ≈ λ/4 | back-lobe suppression | — |

## Worked examples

**Example 1 — 8-element 5.8 GHz patch array (the running example of this domain).**
f = 5.8 GHz → λ = c/f = 299.79/5.8 = 51.69 mm; λ/2 = 25.84 mm. Choose d = 25.8 mm (whether this spacing is wise for scanning is on the [steering page](beam-steering-grating-lobes.md)). Aperture length L = Nd = 207 mm.
- Broadside HPBW: 0.886 × 51.69/(8 × 25.84) = 0.2215 rad = 12.7° (exact numerical value 12.80°).
- At 30° scan: 12.7°/cos30° = 14.7° (exact 14.84°); at 45°: 18.0° (exact 18.39°).
- First nulls: sinθ = ±λ/(Nd) = ±0.25 → ±14.5°. First sidelobes −12.8 dB near ±22°.
- Directivity: with isotropic elements D = 8 (9.03 dBi). Model the patch as a cosθ power pattern in the forward half-space (D_el = 4 = 6.02 dBi; a real FR-4 patch is 5–7 dBi directivity, [patch antennas](../08-antennas/patch-antennas.md)). Exact numerical integration of |f|²|AF|² gives **14.09 dBi**, whereas the naive 10 log 8 + 6.02 = 15.05 dBi. With a cos²θ element (7.78 dBi) the array gives 15.21 dBi vs naive 16.81 dBi. Realized gain is lower again by the patch efficiency (≈40–75%, i.e. −1 to −4 dB, depending on substrate) and by feed-network loss.
- Far field: 2L²/λ = 2 × 0.207²/0.0517 = 1.66 m (with L = (N−1)d = 0.181 m: 1.27 m). Measure the pattern at ≥ 2 m.

**Example 2 — the steering phase, and a cross-check.** 2.45 GHz Wi-Fi-band array, d = λ/2 = 61.2 mm, steer to 30°: ΔΦ = π sin30° = 90° per element (0°, 90°, 180°, 270° across four elements). ADI's example (d = 15 mm, 10.6 GHz, λ = 28.3 mm, 30°) gives ΔΦ = 2π(15/28.3)(0.5) = 1.67 rad = 95° [5] — the same formula.

**Example 3 — 915 MHz: four dipoles vs a Yagi.** λ = 327.6 mm; four parallel horizontal λ/2 dipoles side by side at d = λ/2 = 164 mm (aperture 0.66 m). Numerical pattern multiplication: 9.2 dBi, bidirectional (front and back), HPBW 26° in the array plane. Over a large reflector at λ/4 behind: ≈13.0 dBi (optimistic — infinite reflector, no coupling). A 0.82 m-boom 11-element Yagi reaches ≈14.3 dBi at 915 MHz (MoM, [Yagi–Uda page](../08-antennas/yagi-uda-and-log-periodic.md)). So for *fixed-pointing* gain the Yagi wins on simplicity; the array only pays off if you need **electronic** steering or several simultaneous beams, and then you need four coherent channels or a 4-way phase-shifting feed. See the ground-station discussion in [DIY projects](diy-phased-array-projects.md).

**Example 4 — SNR gain of a coherent SDR array.** A KrakenSDR has 5 coherent RTL-SDR channels [9]. Beamforming 4 of them toward a rocket beacon gives +6.0 dB SNR relative to one channel (uncorrelated tuner noise), 5 channels +7.0 dB. In free space (received power ∝ 1/r²) +6 dB is worth 2× range at the same SNR — but only if the per-channel SNR was set by receiver noise. If the channel is interference-limited from the *same* direction, beamforming doesn't help; if the interferer is elsewhere, adaptive nulling can help far more ([adaptive beamforming](adaptive-beamforming-doa.md)).

**Example 5 — broadside vs endfire vs Hansen–Woodyard, N = 10, d = λ/4.** Exact sums: broadside 5.17 (7.13 dBi; the large-N approximation 2Nd/λ = 5 → 6.99 dB), ordinary endfire 10.0 (10.0 dBi), Hansen–Woodyard 17.96 (12.54 dBi; approximation 17.89). The HW gain is why a long Yagi or axial-mode helix is "phased slower than light" along its length.

**Example 6 — transmit array EIRP.** Eight 20 dBm (100 mW) PAs, 5 dBi elements, coherent: EIRP = 20 + 10 log 8 (power) + 10 log 8 (directivity) + 5 = 43.1 dBm (≈20 W EIRP from 0.8 W total RF). Check regulatory EIRP limits before you celebrate ([ISM rules](../19-regulations-safety/spectrum-allocation-ism-bands.md)).

## Practical notes
- **Phase reference.** Put the phase reference at the array centre: the AF becomes real (for symmetric weights), which makes plots and sign conventions easier, and the steering phase for element n is −k(n − (N−1)/2) d sinθ₀.
- **Measure what you compute.** Element patterns measured in isolation are *not* the element patterns in the array. Measure the embedded element pattern (one element driven, all others terminated in 50 Ω) if you want pattern multiplication to predict reality ([planar arrays & coupling](planar-arrays-element-pattern-coupling.md)).
- **Cables and feed lines are part of the weights.** Every millimetre of unequal feed is a phase error: at 5.8 GHz in FR-4 microstrip (ε_eff ≈ 3.3) 1 mm ≈ 12.7°; at 915 MHz in RG-316-class coax (v_f ≈ 0.7) 1 cm ≈ 16°. KrakenSDR's docs ask for coax lengths matched to within 1 cm below ~900 MHz [9]. Calibrate, don't trust lengths ([array calibration](array-calibration.md)).
- **Small arrays are not "large arrays but fewer".** For N = 4 the first sidelobe is −11.3 dB, the HPBW formula is 4% optimistic, and edge effects dominate: every element is an edge element.
- **Ground stations and rockets.** A rocket 10 km away at 5.8 GHz is far-field for any array you will build; a pattern test in the lab at 1 m is not (for L ≳ 0.16 m).
- **Transmit arrays and PAs.** EIRP scales as N², but each PA sees a load that changes with scan (active reflection coefficient). Check PA stability over the scan range.

## Common mistakes & misconceptions
- **"More elements at the same aperture size give a narrower beam."** No — beamwidth depends on aperture length L = Nd. Packing more elements into the same length (d < λ/2) only improves SNR gain and grating-lobe margin; it barely changes the beam.
- **"Array gain = 10 log N + element gain, always."** Only when the elements' effective areas don't overlap and there are no grating lobes. For patch-like (cosθ) elements at λ/2 in a line the true value is ~1 dB less (example 1); for elements spaced > λ grating lobes steal gain. The upper bound in a large 2-D array is the Hannan cell gain 4πA/λ² per element.
- **"The first sidelobe is always −13 dB."** Only for large N: −11.3 dB at N = 4, −9.5 dB at N = 3.
- **Mixing angle conventions.** Balanis-style formulas use θ from the array *axis* (cosθ); phased-array literature uses θ from *broadside* (sinθ). Using the wrong one moves the beam by 90°.
- **"Scanning a λ/2 array of isotropic elements loses directivity because the beam widens."** It doesn't (D = N at all scan angles); real scan loss comes from the element pattern and mismatch.
- **"Combining two SDRs doubles SNR."** Only if they are phase-coherent (shared LO/clock and calibrated). Non-coherent power summing gives no array gain against receiver noise ([beamforming architectures](beamforming-architectures.md)).
- **"Array gain helps against everything."** It helps against noise uncorrelated between elements. Against a jammer or multipath from another direction, the relevant quantity is the sidelobe level (or adaptive nulling); against noise from the beam direction, nothing helps.
- **Measuring in the near field** (closer than 2L²/λ) and concluding "the array has no nulls".
- **Endfire with d = λ/2** — produces an equal back lobe (grating lobe at the other endfire).

## How to simulate / verify
- `tools/verify/array_factor.py` (this page): closed form vs brute-force sum; HPBW vs 0.886λ/(Nd cosθ₀); first-sidelobe table; exact vs numerically integrated directivity (isotropic and cos^q elements, dipoles); Hansen–Woodyard; Monte-Carlo SNR gain; isotropic-noise array gain = directivity. Runtime ≈30 s.
- Minimal numpy pattern (θ from broadside):
  `u=np.sin(th); AF=np.exp(1j*k*np.outer(u,x))@(a*np.exp(-1j*k*x*np.sin(th0)))` — then 20·log10(|AF|/max).
- Mutual coupling and real element patterns: NEC-2 (dipole/Yagi arrays; see [antenna simulation](../08-antennas/antenna-simulation-nec-openems.md)), openEMS FDTD for patch arrays ([openEMS workflow](../16-simulation-tools/openems-workflow.md)). MATLAB Phased Array System Toolbox is the commercial reference.
- Hardware check: two-element interferometer with an SDR (see [DIY projects](diy-phased-array-projects.md)): sweep a source across the front at > 2L²/λ and compare measured |AF| with the formula.

## Open questions / gaps
- The exact effective-aperture "overlap" penalty for finite *linear* arrays of real patches depends on the embedded element pattern — to be quantified with an openEMS model (planned for [planar arrays & coupling](planar-arrays-element-pattern-coupling.md)).
- Chapter numbers of Mailloux 3e (2018) and Hansen 2e were not checked against the physical books; citations are to topic/chapter titles.

## Sources
1. R. J. Mailloux, *Phased Array Antenna Handbook*, 2nd ed., Artech House, 2005 (3rd ed. 2018), ch. 2 "Pattern characteristics of linear and planar arrays" — conventions (θ from broadside, u = sinθ), AF, beamwidth. (textbook)
2. R. C. Hansen, *Phased Array Antennas*, 2nd ed., Wiley, 2009 — basic array characteristics, directivity, superdirectivity. (textbook)
3. C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed., Wiley, 2016, ch. 6 "Arrays: linear, planar, and circular" — AF, broadside/endfire, Hansen–Woodyard, directivity of uniform arrays (θ from axis convention). (textbook)
4. H. L. Van Trees, *Optimum Array Processing* (Part IV of *Detection, Estimation, and Modulation Theory*), Wiley, 2002, ch. 2 "Arrays and spatial filters" — array as spatial filter, array gain, white-noise gain, directivity against isotropic noise. (textbook)
5. P. Delos, B. Broughton, J. Kraft, "Phased Array Antenna Patterns—Part 1: Linear Array Beam Characteristics and Array Factor," *Analog Dialogue* 54(2), May 2020, analog.com — steering phase, 0.886λ/(Nd cosθ), far field 2D²/λ with D = (N−1)d, 95° example. (app note)
6. N. K. Nikolova, "Lecture 14: Linear array theory — Part II," McMaster University ECE 4AP/718 notes, 2025, ece.mcmaster.ca/faculty/nikolova/antenna_dload — Hansen–Woodyard derivation (z_min ≈ −1.47, 2.94/N, 1.789 factor), D ≈ 2Nd/λ, 4Nd/λ. (lecture notes)
7. W. W. Hansen, J. R. Woodyard, "A new principle in directional antenna design," *Proc. IRE* 26(3):333–345, 1938 — increased-directivity endfire condition. (peer-reviewed)
8. S. A. Schelkunoff, "A mathematical theory of linear arrays," *Bell Syst. Tech. J.* 22(1):80–107, 1943 — polynomial/unit-circle representation. (peer-reviewed)
9. KrakenRF, *KrakenSDR documentation wiki*, github.com/krakenrf/krakensdr_docs/wiki (pages "Home", "04. Antenna Array Setup"), accessed 2026-09-27 — 5 coherent channels, cable-length tolerance. (vendor docs)
10. R. C. Hansen [2] and P. W. Hannan, "The element-gain paradox for a phased-array antenna," *IEEE Trans. Antennas Propag.* 12(4):423–433, 1964 — element-cell gain 4πA/λ² (upper bound used in TL;DR). (peer-reviewed)
11. `tools/verify/array_factor.py` — all numeric values on this page not otherwise attributed. (own verification)
