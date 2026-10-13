---
title: Beam steering and grating lobes — visible space, scan loss, beam broadening, squint vs true time delay, phase-quantisation lobes
domain: 12-phased-arrays
slug: beam-steering-grating-lobes
tags: [beam-steering, progressive-phase, grating-lobes, visible-space, u-space, scan-loss, beam-broadening, beam-squint, true-time-delay, TTD, instantaneous-bandwidth, aperture-fill-time, phase-quantization, quantization-lobes, phase-shifter-bits, pointing-error, subarrays]
prerequisites: [array-factor-linear-arrays.md, ../00-math-foundations/complex-numbers-and-phasors.md]
related: [planar-arrays-element-pattern-coupling.md, tapering-sidelobe-control.md, beamforming-architectures.md, phase-shifters-ttd-components.md, array-calibration.md, diy-phased-array-projects.md, ../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md, ../05-analog-electronics/data-converters-adc-dac.md, ../08-antennas/patch-antennas.md, ../11-radar/fmcw-radar.md]
level: mixed
confidence: high
last_updated: 2026-10-03
---

# Beam steering and grating lobes

## Questions this page answers
- What phase do I put on each element to point the beam at 40°?
- What is a grating lobe and why is it "spatial aliasing"?
- What element spacing can I use if I only need to scan ±30° (or ±60°)?
- Is λ/2 spacing always safe?
- Why does the beam get wider and the gain drop as I steer away from broadside?
- What is beam squint, and when do I need true-time delay instead of phase shifters?
- How much bandwidth can a phase-shifter-steered array handle?
- How many phase-shifter bits do I need? Do more bits give finer beam pointing?
- What are quantisation lobes and how high are they with a 4-bit phase shifter?
- Why does my beam point at the wrong angle when I change frequency?
- How accurately can I point the beam if my element phases have random errors?
- What is "visible space" and "u-space"?

## TL;DR
- **Steering** to θ₀: progressive phase ΔΦ = −kd sinθ₀ per element (only needed modulo 360° for narrowband signals). In **u = sinθ** the pattern simply *slides* by u₀ = sinθ₀ without changing shape; in θ it widens as **1/cosθ₀**.
- The array factor is **periodic in u with period λ/d**. Copies of the main beam — **grating lobes** — sit at u = u₀ ± mλ/d. They are visible when |u| ≤ 1. No grating-lobe *peak* in visible space requires **d ≤ λ/(1+|sinθ₀,max|)**: λ/2 for ±90°, 0.536λ for ±60°, 0.586λ for ±45°, 0.667λ for ±30°. To keep even the grating lobe's *skirt* out (first null at the horizon) use **d ≤ λ(1−1/N)/(1+|sinθ₀|)** — for N = 8 at ±60° that is 0.469λ, i.e. slightly *less* than λ/2. Design at the **highest** frequency.
- **Scan loss**: a large planar aperture's gain falls as the projected area, **cosθ₀** (−3 dB at 60°), times the mismatch factor (1 − |Γ_active(θ₀)|²). Real embedded element patterns behave like cos^1.2…cos^1.5 (−3.6…−4.5 dB at 60°). Beam broadening: ×1.15 at 30°, ×1.41 at 45°, ×2 at 60° (more for small N: ×2.25 for N = 8).
- **Beam squint** with phase shifters: sinθ_peak = (f₀/f) sinθ₀ (verified numerically to 0.001°); small-signal Δθ ≈ −(Δf/f₀) tanθ₀. Lower frequencies squint *away* from broadside.
- **Instantaneous bandwidth** of a phase-steered array (band-edge gain loss 3 dB): **B/f₀ = Θ₃,broadside/sinθ₀ = 0.886λ/(L sinθ₀)** — i.e. **B ≈ 0.886/T_fill** where T_fill = L sinθ₀/c is the aperture fill time. For 1 dB edge loss, 0.59× that. At 60° scan: B(%) ≈ 2 × HPBW(°) (3 dB) or ≈ 1.2 × HPBW(°) (1 dB). True-time delay (TTD) removes squint; subarray-level TTD removes most of it but creates lobes at band edges.
- **Phase quantisation** with P bits: rms error LSB/√12, gain loss = −20 log sinc(2^−P) (0.91 / 0.22 / 0.056 / 0.014 dB for 2/3/4/5 bits). **Worst-case quantisation lobe = $20\log_{10}\tan(\pi/2^{P+1})$** (mnemonic ≈ −6.02P + 4.4 dB, up to 0.5 dB optimistic) (−7.7, −14.0, −20.1, −26.2, −32.2 dB for 2–6 bits), independent of N and taper, at scan angles sinθ₀ = n/2^P (n odd) — this confirms ADI's −7.5 dB at 2 bits and is ≈4.4 dB worse than the often-quoted 1/2^{2P}. Phase dither lowers it by ≈6.5 dB.
- **Pointing resolution is not the phase-shifter LSB**: a 2-bit 30-element array can step its beam by ≈1–1.4°, far finer than its 3.4° beam. Random phase errors σ_φ move the beam by only ≈0.62σ_φ/√N beamwidths.

## Intuition (no math)

**Steering is sliding a window over a periodic pattern.** Plot the array factor against u = sinθ instead of θ. It is a periodic comb of identical main beams, spaced λ/d apart (in u), with sidelobes between them. Steering does not change this comb; it slides it sideways by u₀. What you can actually *see* in the real world is only the slice |u| ≤ 1 — "visible space" — because sinθ can't exceed 1. If the spacing between comb teeth (λ/d) is at least 2, only one tooth fits in the window at a time, however you slide it: that's d ≤ λ/2. If the teeth are closer, sliding the comb to steer the beam eventually drags a second tooth into the window: a **grating lobe**, a full-strength copy of the main beam pointing somewhere you didn't want it.

**Why "spatial aliasing".** The elements sample the incoming wavefront in space. A wave from angle θ has a spatial frequency sinθ/λ along the array. Sampling at interval d can only distinguish spatial frequencies within a band of width 1/d; two directions whose sinθ differs by λ/d produce *identical* element phases — the array literally cannot tell them apart (ADI make exactly this analogy with ADC under-sampling [3]). A direction-finding array with d > λ/2 therefore has ambiguous bearings (KrakenSDR's spacing rule is exactly this, [DIY projects](diy-phased-array-projects.md)).

**Why gain drops when you scan.** Seen from an angle, a flat aperture looks foreshortened — its projected area is A·cosθ. Less capture area means less gain and a wider beam in the scan plane. On top of that, each element's own pattern falls off toward the horizon and, because of mutual coupling, its impedance changes with scan angle so more power reflects ([planar arrays & coupling](planar-arrays-element-pattern-coupling.md)).

**Why phase shifters squint.** Steering really needs *time delays*: the wave reaches the far element later by L sinθ₀/c, the same for every frequency. A phase shifter gives a fixed *phase*, which equals the right delay at only one frequency. At a lower frequency that phase corresponds to a longer delay, so the beam swings further out; at a higher frequency it swings back toward broadside. For a narrowband signal (LoRa, a CW beacon) this is irrelevant; for a wideband chirp or a wide band plan it smears the beam.

**Why coarse phase shifters make "extra" lobes.** Rounding the ideal linear phase ramp to a few discrete values leaves a sawtooth-shaped error across the aperture. A *periodic* error is itself a little diffraction grating: it radiates its own beams (quantisation lobes) in predictable directions. Make the error look random instead (dither), and the energy spreads into a low, even floor.

## The math

Conventions as in [array factor](array-factor-linear-arrays.md): elements at x_n = nd, θ from broadside, u = sinθ, k = 2π/λ, e^{+jωt}.

### Level 1 — results

| Quantity | Formula | Example (d = λ/2 unless stated) |
|---|---|---|
| Steering phase per element | ΔΦ = −kd sinθ₀ (mod 2π) | 30° → −90°; 45° → −127.3° |
| TTD per element | Δτ = d sinθ₀/c | 25.84 mm, 60° → 74.6 ps |
| Grating lobe positions | u_m = sinθ₀ + mλ/d, m = ±1, ±2… | d = 0.6λ, θ₀ = 41.8° → u₋₁ = −1 (horizon) |
| No-GL spacing (peak) | d ≤ λ/(1+\|sinθ₀,max\|) | ±60° → 0.536λ |
| No-GL spacing (skirt) | d ≤ λ(1−1/N)/(1+\|sinθ₀,max\|) | N = 8, ±45° → 0.513λ |
| Beamwidth vs scan | Θ₃(θ₀) ≈ Θ₃(0)/cosθ₀ | 8 el: 12.8° → 14.8° (30°), 28.8° (60°) |
| Scan loss (ideal large aperture) | G(θ₀)/G(0) = cosθ₀·(1−\|Γ(θ₀)\|²) | −1.5 dB at 45°, −3.0 dB at 60° |
| Squint (phase steering) | sinθ = (f₀/f) sinθ₀; Δθ ≈ −(Δf/f₀) tanθ₀ | 5.8 GHz ± 75 MHz at 45° → ±0.75° |
| Inst. bandwidth (3 dB edge loss) | B/f₀ = Θ₃(0)/sinθ₀ | 16 el, 60° → 12.8% |
| Phase-quantisation rms error, gain loss | σ = 2π/(2^P√12); ΔG = −20 log sinc(2^−P) | 4 bits: 6.5°, 0.056 dB |
| Worst quantisation lobe | $20\log_{10}\tan(\pi/2^{P+1})$ (≈ −6.02P + 4.4 dB) | 4 bits: −20.1 dB |

### Level 2 — derivations

**(a) Steering is a shift in u.** With w_n = a_n e^{−jkx_n u₀}, AF(u) = Σ a_n e^{jkx_n(u−u₀)} = A(u − u₀), where A is the unsteered pattern. So in u the pattern shape is invariant. The half-power points of the unsteered beam are at u = ±Δu/2 with Δu = 0.886λ/(Nd) (uniform); after steering, θ± = arcsin(u₀ ± Δu/2), and for Δu ≪ cosθ₀, Θ₃ ≈ Δu/cosθ₀. Near endfire (u₀ + Δu/2 > 1) the approximation fails and the beam merges with the horizon. Numerically (`tools/verify/array_steering.py` §2): N = 8 broadens ×1.159 / 1.436 / 2.253 at 30 / 45 / 60°, N = 32 ×1.155 / 1.416 / 2.010, against 1/cosθ₀ = 1.155 / 1.414 / 2.000.

**(b) Periodicity and grating lobes.** Because x_n = nd, e^{jknd(u + λ/d)} = e^{jkndu}·e^{j2πn} = e^{jkndu}: AF(u) is periodic with period λ/d. Main-beam replicas sit at u_m = u₀ + mλ/d. A replica is *visible* if |u_m| ≤ 1. For the worst replica (m = −sign(u₀)) to stay outside,
$$\left|u_0\right| - \frac{\lambda}{d} \le -1\;\Longrightarrow\; d \le \frac{\lambda}{1+|\sin\theta_{0,\max}|}.$$
This is ADI's eq. (12) [3]; e.g. 10 GHz, ±50° → 17 mm. But a replica is not a spike; it has the width of the main beam, and its near-side null is at u_m ± λ/(Nd). Keeping that null outside visible space gives the stricter
$$d \le \frac{\lambda\,(1-1/N)}{1+|\sin\theta_{0,\max}|}.$$
For N = 8 and ±60° this is 0.469λ; for N = 64 it is 0.528λ (script §1). Two corollaries: (i) at broadside (u₀ = 0) there is no grating lobe for any d < λ — a fixed-beam array can use d ≈ 0.7–0.9λ to get more aperture per element; (ii) for a wideband array, evaluate d/λ at the **highest** frequency.

**(c) Scan loss.** For a large planar array whose elements each occupy area A_cell, Hannan showed the embedded (active) element gain cannot exceed (4πA_cell/λ²)cosθ [9]: the cell's projected area. The array gain at scan angle θ₀ is then
$$G(\theta_0) = N\,\frac{4\pi A_{cell}}{\lambda^2}\cos\theta_0\,\big(1-|\Gamma_a(\theta_0)|^2\big),$$
with Γ_a the *active* reflection coefficient (the reflection each element sees when all are driven with the scan phase). With a perfect match at all angles, the loss is 10 log cosθ₀: −0.6, −1.5, −3.0, −4.7 dB at 30, 45, 60, 70°. Practical embedded patterns are often fitted as cos^n θ with n ≈ 1.2–1.5 (−3.6 to −4.5 dB at 60°), and patch arrays can be much worse if a surface wave causes scan blindness ([planar arrays & coupling](planar-arrays-element-pattern-coupling.md)). This is why practical scan is usually limited to ±45–60°; ±60° in both planes needs three or four flat faces to cover a hemisphere.

**(d) Beam squint (phase-shifter steering).** The phase shifters are set at f₀: Φ_n = −k₀x_n u₀ (mod 2π; the modulo is irrelevant because e^{jΦ} is periodic). At another frequency f (k = k₀f/f₀) the array factor is Σ a_n e^{j(kx_n u − k₀x_n u₀)}, which peaks where kx_n u = k₀x_n u₀ for all n, i.e.
$$\sin\theta_{peak} = \frac{f_0}{f}\sin\theta_0,\qquad \Delta\theta \approx -\frac{\Delta f}{f_0}\tan\theta_0 \ \ (\text{small }\Delta f).$$
ADI's eq. (14) is the same thing written as Δθ = arcsin((f₀/f)sinθ₀) − θ₀ [3]. The numerical beam peak agrees to 0.001° (script §4); the small-signal form is poor at large scan (60°, f/f₀ = 0.9: 74.2° exact vs 69.9°). Lower frequencies squint more and away from broadside. At broadside there is no squint.

**(e) Instantaneous bandwidth.** The gain *toward the intended direction θ₀* at frequency f is |AF| evaluated at a squint offset. With squint Δθ_edge = (B/2f₀)tanθ₀ at the band edges and a scanned beamwidth Θ₃(0)/cosθ₀, setting the band-edge loss to 3 dB (Δθ_edge = half the scanned beamwidth) gives
$$\frac{B}{f_0} = \frac{\Theta_3(0)}{\sin\theta_0} = \frac{0.886\,\lambda}{L\sin\theta_0}\quad\Longleftrightarrow\quad B\,T_{fill}\approx 0.886,\qquad T_{fill} = \frac{L\sin\theta_0}{c}.$$
The script (§5) finds the numerically exact 3-dB bandwidth within 0.5% of this for N = 8–32, and the 1-dB bandwidth at 0.59× it. The **aperture fill time** form is the physical one: a pulse shorter than the time it takes the wavefront to cross the projected aperture cannot be "caught" coherently by fixed phase shifts. Rule of thumb at 60° scan: B(%) ≈ 2 × Θ₃(0)(°) for 3 dB, ≈ 1.2 × Θ₃(0)(°) for 1 dB. A 32-element λ/2 array (Θ₃ = 3.2°) scanned to 45° supports only ≈4.6% with ≤1 dB edge loss — a 10 GHz radar with a 1 GHz chirp (10%) needs TTD.

**(f) True-time delay and subarrays.** TTD sets τ_n = x_n sinθ₀/c, i.e. phase −kx_n u₀ at *every* frequency: no squint (beamwidth still ∝ 1/f). The delay span is (N−1)d sinθ₀/c: 8 elements at 25.84 mm, 60° → 523 ps (3.0 cycles at 5.8 GHz); 32 elements → 2.3 ns (13.4 cycles) (script §10). Element-level TTD is costly, so large arrays use **TTD at the subarray level and phase shifters within each subarray**. Then only the subarray pattern squints; it is M times wider (M elements per subarray) and tolerates M× more bandwidth. The price: at band edges the squinted subarray pattern no longer suppresses the array factor's "subarray grating lobes" (period λ/(Md) in u), so lobes pop up. Script §6: 4 subarrays of 8 at 45° and ±10% frequency keep the peak within 0.4° of 45° (phase-only drifts to 51.8° / 40.0°), but the highest lobe rises from −13.2 to −7.0 dB and the gain drops 1.16 dB. ADI note that in hybrid digital arrays the digital stage can implement the TTD for free [3] ([architectures](beamforming-architectures.md)).

**(g) Phase quantisation.** A P-bit phase shifter has LSB = 2π/2^P. Rounding the ideal ramp leaves an error ε_n ∈ [−LSB/2, LSB/2].
- *If the errors behave randomly* (uniform, independent): σ² = LSB²/12, and the expected main-beam power is |E e^{jε}|² = sinc²(LSB/2π) = sinc²(2^−P) (normalised sinc), i.e. ΔG ≈ σ² nepers: 0.91, 0.22, 0.056, 0.014 dB for 2–5 bits (script §7). The scattered power forms an average sidelobe floor ≈ σ²/(N η_t) relative to the peak (η_t = taper efficiency) — the same law as random errors in [tapering](tapering-sidelobe-control.md).
- *But for a linear phase ramp the errors are periodic*, not random: the error is a sampled sawtooth. Its Fourier components radiate **quantisation lobes**. The worst case occurs when the error alternates between 0 and ±LSB/2 on successive elements, so that all spatial harmonics of the sawtooth alias into the same direction; this happens at sinθ₀ = n/2^P (n odd) for d = λ/2 [3]. Computing the error pattern |AF_quantised − AF_ideal|² over all scan angles (script §7) gives a worst-case lobe of **−7.7, −14.0, −20.1, −26.2, −32.2 dB for 2–6 bits**, i.e. exactly **$20\log_{10}\tan(\pi/2^{P+1})$** (fit ≈ −6.02P + 4.4 dB, which is 0.5 dB high at P = 3–6), the same for N = 8, 16, 32, 100 and for uniform, Hamming or Taylor tapers (the lobe is set by the bits, not the aperture). ADI report "about −7.5 dB" at 2 bits and 6 dB/bit [3]. The frequently quoted peak level 1/2^{2P} (−6.02P dB) — attributed to Miller [7] and reproduced in the standard texts [1] — is ≈4.4 dB optimistic for this worst case; a single-harmonic analysis of a continuous ramp gives 1/(2^P − 1)² (−9.5 dB at 2 bits). Treat 1/2^{2P} as a typical level and −6.02P + 4.4 dB as the design worst case.
- *Mitigation*: add a known pseudo-random phase offset to each element (e.g. by using different feed-line lengths, or in the calibration table) and subtract it before rounding. The error becomes decorrelated: for a 100-element Hamming array the worst lobe drops from −13.8 to −20.4 dB (3 bits) and from −19.9 to −26.3 dB (4 bits) (script §7). Beamformer ICs with 6–7 bits (ADAR1000: 2.8° steps [10]) put the worst lobe below −32 dB, usually beneath the random-error floor from calibration residuals.

**(h) Pointing resolution and pointing error.** The beam can be moved in steps much finer than the LSB suggests, because pointing follows the *average slope* of the phase across the whole aperture. Setting half the array to 0 and half to one LSB shifts the beam by the least-squares slope 1.5·LSB/N per element, i.e. δu ≈ 1.5·LSB/(πN) for d = λ/2 (ADI's θ_RES ≈ sin⁻¹(LSB/(Nπ)) is the same scaling without the 1.5 [3]; script §8: 2-bit, 30 elements → 1.43° numerically vs 0.96° from ADI's expression, against a 3.4° beamwidth). With random phase errors of standard deviation σ_φ, the least-squares slope error gives
$$\sigma_u = \frac{\sigma_\phi\,\lambda}{2\pi d}\sqrt{\frac{12}{N(N^2-1)}}\approx 0.62\,\frac{\sigma_\phi}{\sqrt N}\,\Delta u_{3\,\mathrm{dB}},$$
confirmed by Monte Carlo (§9): 8 elements with 10° rms phase error → 0.039 beamwidths (≈0.5°). Pointing is robust; sidelobes are what suffer.

### Level 3 — general and advanced

- **Planar arrays**: u = sinθcosφ, v = sinθsinφ; visible space is the unit circle u² + v² ≤ 1 and grating lobes form a 2-D lattice (rectangular or triangular) — the triangular lattice saves ≈13% of elements for the same scan cone ([planar arrays](planar-arrays-element-pattern-coupling.md)).
- **Grating lobes you can't see still matter.** A grating lobe just beyond the horizon (|u_m| slightly > 1) corresponds to an evanescent/surface-grazing Floquet mode; when it crosses into visible space the element impedance changes abruptly (Wood's anomaly) and in dielectric-loaded arrays can trigger scan blindness ([coupling page](planar-arrays-element-pattern-coupling.md)).
- **Sparse, thinned and aperiodic arrays.** Irregular positions break the periodicity, so grating lobes smear into a sidelobe floor whose average level is ≈1/N_elements relative to the peak (random arrays). This buys a narrow beam from few elements (radio astronomy, KrakenSDR-style DF with large baselines resolved by multiple baselines) at the cost of high average sidelobes.
- **Limited-field-of-view arrays** (e.g. a GEO satellite, ±9° to cover the Earth [3]) use large d and big elements or overlapped subarrays; grating lobes are allowed as long as they fall off the region of interest.
- **Frequency scanning** turns squint into a feature: a serpentine-fed or leaky-wave array steers its beam by changing frequency (sinθ ∝ (f − f₀) slope), a classic low-cost radar trick.
- **Wideband digital arrays**: per-element digitisation lets DSP apply true delays (fractional-delay filters) per frequency bin; the squint and bandwidth limits then move to the ADC/clock alignment ([architectures](beamforming-architectures.md)).

## Design equations & rules of thumb

| Rule | When valid | Typical numbers |
|---|---|---|
| d ≤ λ_min/(1+\|sinθ_max\|) | no GL peak in visible space, design at the highest frequency | ±45° → 0.586λ; ±60° → 0.536λ |
| d ≤ λ_min(1−1/N)/(1+\|sinθ_max\|) | no GL skirt (first null at horizon) | N = 8, ±60° → 0.469λ |
| Fixed broadside beam: d < λ | no scanning | 0.7–0.9λ gives more gain per element |
| Θ₃(θ₀) ≈ Θ₃(0)/cosθ₀ | \|θ₀\| ≲ 60°, N ≳ 16 | small N: add 5–13% at 60° |
| Scan loss ≈ 10n·log cosθ₀, n ≈ 1–1.5 | large array, good element match | 60°: −3 to −4.5 dB |
| sinθ = (f₀/f) sinθ₀ | phase-shifter steering | lower f → further from broadside |
| B/f₀ ≈ Θ₃(0)/sinθ₀ (3 dB); ×0.59 (1 dB) | phase-shifter steering, uniform | 60°: B% ≈ 2×HPBW°(3 dB) |
| TTD span = (N−1)d sinθ_max/c | TTD per element | 8 × λ/2 @ 5.8 GHz, 60°: 523 ps |
| σ_quant = LSB/√12; ΔG ≈ σ² | random-like rounding | 4 bits: 6.5°, 0.056 dB |
| Worst quantisation lobe $20\log_{10}\tan(\pi/2^{P+1})$ (≈ −6.02P + 4.4 dB) | periodic rounding, d = λ/2, any N | 3 bits −14 dB; 4 bits −20 dB; 6 bits −32 dB |
| σ_u ≈ 0.62σ_φ/√N beamwidths | random phase error σ_φ (rad) | N = 8, 10° → 0.04 BW |
| Bits needed: P ≳ (SLL_design + 4.4)/6 | quantisation lobes below design SLL | −25 dB design → ≥5 bits (or 4 + dither) |

## Worked examples

**Example 1 — the 8-element 5.8 GHz patch array: spacing, scan range, beamwidth, scan loss, bits.**
λ = 51.69 mm (5.8 GHz). A 5.8 GHz patch on RO4350B is ≈17 × 13 mm, on 1.6 mm FR-4 ≈15–16 mm wide ([patch antennas](../08-antennas/patch-antennas.md)), so d = λ/2 = 25.84 mm leaves ≈9 mm between patch edges — fine.
- *Grating lobes*: with d = 25.84 mm (0.500λ) no grating-lobe peak can ever enter; the skirt (first null of the lobe) stays out up to **48.6°** (N = 8). With d = 28 mm (0.542λ): 57.8° / 38.0°. With d = 31 mm (0.6λ): 41.9° / 27.3° (script §10). The 5.8 GHz band tops out at 5.875 GHz, where 25.84 mm is 0.506λ — negligible change. **Choose 25.8 mm and limit scan to ±45°.**
- *Beamwidth*: 12.8° broadside, 14.8° at 30°, 18.4° at 45°.
- *Scan loss*: with a cos^1.3 embedded pattern, −0.8 dB at 30°, −2.0 dB at 45°. Broadside realized gain ≈ 14 dBi (directivity from [array factor](array-factor-linear-arrays.md) example 1) minus patch and feed losses.
- *Squint*: across 5.725–5.875 GHz at 45°: +0.76°/−0.73°; across a 5.65–5.95 GHz FPV band at 45°: +1.5°/−1.4° — tiny against the 18.4° beam. Phase shifters are fine; no TTD needed.
- *Bits*: 4-bit (22.5°) phase shifters: rms error 6.5°, gain loss 0.056 dB, worst quantisation lobe −20.1 dB. Added coherently to the uniform array's own −12.8 dB first sidelobe, the worst total sidelobe over 0–45° becomes **−10.8 dB** (script §11); with a 25 dB Taylor taper (ideal −24.4 dB for N = 8) 4 bits give worst-case −17.2 dB, 5 bits −20.3 dB, 6 bits −22.2 dB. So: 4 bits is enough for a uniform array; a low-sidelobe design wants ≥6 bits (or dither + calibration). The beam can be stepped in increments of ≈1.4° or less, far below the 12.8° beamwidth.

**Example 2 — a 2.44 GHz ground-station array that must scan ±60°.** λ = 122.9 mm. Peak criterion: d ≤ 122.9/(1 + 0.866) = 65.8 mm; with the N = 8 skirt margin, ≤ 57.6 mm (0.469λ). Beamwidth at 60° is ≈ 2× broadside, and scan loss ≈ −3.6 dB (cos^1.2). Covering a rocket's trajectory from pad (near horizon) to apogee (near zenith) with a single flat panel therefore costs ≈4 dB and doubles the beam at the ends: tilting the panel ≈45° up toward the expected trajectory halves the scan range needed.

**Example 3 — ADI Phaser (CN0566).** d = 14 mm at 10.25 GHz is 0.479λ [4]: no grating-lobe peak at any scan, skirt margin to 55.9°. Its ADAR1000 beamformers have 2.8° phase steps (7 bits, [10]) → worst quantisation lobe ≈ −38 dB — invisible under calibration errors. An FMCW chirp from its ADF4159 of a few hundred MHz around 10 GHz (≲5%) against the 8-element beam (12.8°) at 30°: 3-dB IBW = 12.8°·π/180/0.5 = 45% — no squint problem.

**Example 4 — a wideband radar that does need TTD.** 32 elements, λ/2 at 10 GHz, 45° scan, 1 GHz chirp (10%). 3-dB IBW = 3.18°·(π/180)/sin45° = 7.8%; 1-dB IBW 4.6% (script §5). A 10% chirp loses > 3 dB at its edges and smears range-angle coupling. Options: element-level TTD (span (N−1)d sinθ₀/c = 31 × 15 mm × 0.707/c ≈ 1.1 ns), four 8-element subarrays with TTD (bandwidth ×4 for the subarray squint, but −7 dB lobes at ±10%), or digital beamforming per subarray.

**Example 5 — calibration residual → pointing error.** After calibration, 8 channels with 10° rms phase residual: σ_u = 0.0086 → ≈0.5° at broadside, 0.04 beamwidths (script §9). For a tracking ground station with a 12.8° beam this is irrelevant; the same residual raises the sidelobe floor by σ²/N ≈ 0.030/8 → −24 dB, which matters only for low-sidelobe designs.

## Practical notes
- **Measure the direction of the scan sign once.** Positive ΔΦ may steer left or right depending on channel ordering, the phase-shifter convention (does "+" mean advance or delay?) and mixer sidebands (a high-side LO *inverts* phase). Test with a source at a known angle before writing tracking code.
- **Phase shifters wrap, delays don't.** With phase shifters, program ΔΦ·n mod 360°. With TTD, the full delay span matters (523 ps for the 8-element 5.8 GHz array at 60°).
- **Phase-shifter amplitude-vs-phase variation** (typ. ±0.3–0.5 dB across states in beamformer ICs) is a separate, *correlated-with-state* error; calibrate it in the gain table ([phase shifters](phase-shifters-ttd-components.md), [calibration](array-calibration.md)).
- **Grating lobes on transmit** radiate real power in unwanted directions (and at full EIRP) — a regulatory and interference issue, not just a pattern blemish.
- **Scan loss is also a transmit problem**: the active reflection coefficient at large scan angles reflects power back into each PA; PAs with poor reverse isolation can go unstable or distort ([planar arrays & coupling](planar-arrays-element-pattern-coupling.md)).
- For LoRa-type narrowband telemetry (≤ 500 kHz) squint is zero for practical purposes; even hopping across the whole 902–928 MHz band (2.8%) squints the beam only ±1.4° at 60°.

## Common mistakes & misconceptions
- **"Spacing must always be λ/2."** Only for scanning to the horizon. Limited-scan arrays can use λ/(1+sinθ_max); fixed broadside arrays up to almost λ.
- **"λ/2 spacing guarantees no grating-lobe trouble."** The *peak* never enters, but for small N the grating lobe's skirt rises at the horizon beyond ≈48° (N = 8) — and d/λ grows at the top of the band.
- **Designing spacing at the centre frequency** of a wide band. Use the highest frequency.
- **"Phase-shifter resolution = beam-pointing resolution."** No: pointing follows the aperture-average slope; a 2-bit phase shifter can point a 30-element beam to ≈1° [3].
- **"More bits lower the sidelobes."** More bits lower the *quantisation lobes*; the design sidelobe level is set by the amplitude taper. Conversely, a −35 dB Taylor taper is pointless with 3-bit phase shifters (worst lobe −14 dB).
- **"Squint is a TTD problem."** Reversed: squint is caused by phase shifters; TTD cures it.
- **"Scan loss is just cosθ."** That is the ideal projected-aperture limit; element pattern shape and active mismatch usually add 0.5–2 dB at 60°, and patch arrays can have blind angles.
- **Using the small-signal squint formula at large scan** (60°, −10%: 69.9° predicted vs 74.2° actual).
- **Believing the beam must be steerable to ±90°.** Beyond ~60° the beam is twice as wide, the gain −3 to −5 dB and the match poor; use more faces or tilt the panel.

## How to simulate / verify
- `tools/verify/array_steering.py` (≈4 min): grating-lobe limits (peak and skirt), beam broadening, scan-loss table, exact squint vs formula, instantaneous-bandwidth search vs Θ₃/sinθ₀, TTD and subarray-TTD patterns, phase-quantisation worst-case lobe search (FFT error patterns) with and without dither, pointing resolution and Monte-Carlo pointing error, all worked-example numbers.
- To see a grating lobe for yourself: in the numpy one-liner from [array factor](array-factor-linear-arrays.md), set d = 0.7λ and sweep θ₀ from 0 to 45°; watch a second main beam enter from −90° at θ₀ = 25.4°.
- Hardware: with a 2-channel coherent SDR and two antennas at d = λ (e.g. 2 × 12.2 cm at 2.45 GHz), move a source and see the phase difference wrap — the bearing ambiguity *is* the grating lobe.

## Open questions / gaps
- The 1/2^{2P} quantisation-lobe formula's original derivation (Miller 1964) was not read; its attribution is from secondary memory. The numerical worst case on this page is self-consistent with ADI [3].
- Measured embedded-element scan-loss exponents for FR-4 patch arrays at 5.8 GHz were not found; the cos^1.2–1.5 range is a common modelling assumption, not a measurement.

## Sources
1. R. J. Mailloux, *Phased Array Antenna Handbook*, 2nd ed., Artech House, 2005, ch. 2 (grating lobes, scan, u-space), ch. 7 "Array error effects" (random and quantisation errors), ch. 8 (wideband arrays, time delay, subarrays). (textbook)
2. R. C. Hansen, *Phased Array Antennas*, 2nd ed., Wiley, 2009 — grating lobes, scan loss, quantisation lobes, subarrays and time delay. (textbook)
3. P. Delos, B. Broughton, J. Kraft, "Phased Array Antenna Patterns — Part 2: Grating Lobes and Beam Squint," *Analog Dialogue* 54(2), June 2020, and "Part 3: Sidelobes and Tapering," 54(3), July 2020, analog.com — d_max = λ/(1+|sinθ|), squint formula, hybrid/TTD remarks, θ_RES, worst-case QSLL angles and ≈ −7.5 dB at 2 bits, 6 dB/bit. (app note)
4. M. Lichtman, *PySDR*, ch. "Hands-on with Phaser," pysdr.org/content/phaser, accessed 2026-09-27 — CN0566 element spacing 14 mm, 10.25 GHz. (tutorial)
5. C. A. Balanis, *Antenna Theory*, 4th ed., Wiley, 2016, ch. 6 — scanning arrays, grating lobes (θ-from-axis convention). (textbook)
6. H. L. Van Trees, *Optimum Array Processing*, Wiley, 2002, ch. 2 — visible region, spatial sampling, broadband arrays. (textbook)
7. C. J. Miller, "Minimizing the effects of phase quantization errors in an electronically scanned array," *Proc. 1964 Symp. Electronically Scanned Array Techniques and Applications*, RADC-TDR-64-225, vol. 1, pp. 17–38 — quantisation lobes and decorrelation (cited via [1][2]; not read). (conference)
8. J. Frank, J. D. Richards, "Phased array radar antennas," ch. 13 in M. Skolnik (ed.), *Radar Handbook*, 3rd ed., McGraw-Hill, 2008 — scan loss, bandwidth/fill time, TTD and subarrays. (textbook)
9. P. W. Hannan, "The element-gain paradox for a phased-array antenna," *IEEE Trans. Antennas Propag.* 12(4):423–433, 1964 — embedded element gain ≤ 4πA/λ² cosθ. (peer-reviewed)
10. Analog Devices, *ADAR1000 8–16 GHz 4-channel X/Ku-band beamformer* product page/data sheet, analog.com — ≥31 dB gain range, 360° phase, ≤2.8° phase and ≤0.5 dB gain steps. (datasheet)
11. M. Longbrake, "True time delay beamsteering for radar," *Proc. IEEE NAECON*, 2012 — TTD vs phase steering (cited by [3]). (conference)
12. `tools/verify/array_steering.py` — all numbers marked "script". (own verification)
