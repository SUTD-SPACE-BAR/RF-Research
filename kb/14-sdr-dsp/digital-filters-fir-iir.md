---
title: Digital filters — FIR and IIR design, linear phase, length estimates, stability and fixed-point effects
domain: 14-sdr-dsp
slug: digital-filters-fir-iir
tags: [fir, iir, window-method, kaiser, parks-mcclellan, remez, equiripple, least-squares, linear-phase, group-delay, bilinear-transform, prewarping, butterworth, chebyshev, elliptic, biquad, sos, quantisation, fixed-point, filter-length]
prerequisites: [../00-math-foundations/linear-systems-convolution.md, ../00-math-foundations/laplace-transfer-functions-bode.md, sampling-aliasing-bandpass-sampling.md, fft-spectral-analysis-windows.md]
related: [multirate-dsp-decimation-cic.md, nco-ddc-duc.md, fpga-for-sdr.md, software-demodulation.md, iq-complex-baseband.md, ../01-circuit-theory/passive-filter-design-prototypes.md, ../05-analog-electronics/active-filters.md, ../10-comms-modulation/pulse-shaping-isi.md, ../10-comms-modulation/matched-filter-detection.md, ../12-phased-arrays/tapering-sidelobe-control.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Digital filters — FIR and IIR design, linear phase, length estimates, stability and fixed-point effects

## Questions this page answers
- What is the difference between an FIR and an IIR filter, and which should I use in an SDR?
- How many taps does my FIR need for a given transition band and stop-band attenuation?
- Window method, least-squares or Parks–McClellan (remez) — which and why?
- What is linear phase / group delay, and why do demodulators care?
- How do I turn an analogue Butterworth/Chebyshev/elliptic design into a digital IIR, and what is prewarping?
- Why did my high-order IIR blow up when I put it in fixed point (or even float32)?
- How many coefficient bits do I need for 80 dB of stop-band?
- How many accumulator bits does a fixed-point FIR need?
- How expensive (multiplies per second) is a channel filter for a LoRa channel?
- Why is my filter's output delayed, and by how much?
- Can I filter by taking an FFT, zeroing the unwanted bins and taking the inverse FFT?

## TL;DR
- **FIR** $y[n]=\sum_{k=0}^{N-1}h[k]x[n-k]$: always stable, exact **linear phase** if the taps are symmetric (constant group delay $(N-1)/2$ samples), easy in fixed point, costs $N$ multiplies per output ($\approx N/2$ with symmetry). **IIR** (recursive): 5–20× fewer multiplies for sharp magnitude specs, but non-linear phase, can be unstable, and is sensitive to coefficient quantisation — always implement as cascaded second-order sections (biquads).
- **FIR length rule of thumb (harris)**: $N \approx \dfrac{A}{22}\cdot\dfrac{f_s}{\Delta f}$ taps ($A$ = stop-band attenuation in dB, $\Delta f$ = transition width). Checked against the true minimum Parks–McClellan length on four specs: within 7 % (e.g. 60 dB, $\Delta f/f_s$ = 0.05: estimate 55, true 59). Kaiser's and Bellanger's estimates are within 7 % too.
- **Design method**: Parks–McClellan (equiripple, minimax) gives the fewest taps for a peak-error spec; least-squares minimises total error energy; Kaiser-window designs are simple but need ~25–45 % more taps (74 vs 59; 252 vs 173).
- **IIR orders** for one spec (0.5 dB ripple, 60 dB, transition 0.20→0.24 $f_s$): Butterworth 32, Chebyshev I/II 12, **elliptic 7** — vs a 59-tap FIR.
- **Bilinear transform** $s = \frac{2}{T}\frac{1-z^{-1}}{1+z^{-1}}$ warps frequency: $\Omega = \frac{2}{T}\tan(\omega/2)$. **Prewarp** critical edges ($\Omega_c = 2f_s\tan(\pi f_c/f_s)$) or a 15 kHz edge at 48 kS/s lands at 11.86 kHz. `scipy.signal.butter(..., fs=)` prewarps for you.
- **Quantisation**: a 10th-order elliptic low-pass with 16-bit coefficients in direct form has a pole at |z| = 1.96 (**unstable**); the same coefficients as 5 biquads stay stable with 0.05 dB error. FIR coefficient quantisation limits the stop-band to ≈ 6 dB per bit (script: 8→36, 12→59, 16→81 dB).
- **Fixed-point FIR accumulator**: data bits + coefficient bits + $\lceil\log_2N\rceil$ guard bits (16 + 18 + 7 = 41 bits for 83 taps — fits a 48-bit DSP48 accumulator).

Verified by `tools/verify/dsp_filters.py` (all PASS).

## Intuition (no math)
A digital filter is a recipe for mixing the current input sample with a few past inputs (and, for IIR, past outputs). An **FIR** filter only looks at past inputs through a fixed-length "window" of weights — like a moving average with carefully chosen weights. Whatever goes in leaves after $N$ samples, so it can never run away. An **IIR** filter feeds its own output back, like an analogue RC or LC circuit that "rings": it can make very sharp filters with few coefficients, but feedback brings the analogue problems with it — ringing, phase distortion near the band edge, and the possibility of oscillation if the coefficients are slightly off.

Sharpness costs time. To tell apart two frequencies $\Delta f$ apart a filter has to watch the signal for roughly $1/\Delta f$ seconds; so a filter with a narrow transition band needs many taps (FIR) or poles very close to the unit circle (IIR). Deep stop-bands cost extra taps on top of that, roughly linearly in dB.

"Linear phase" means every frequency is delayed by exactly the same time, so the waveform shape passes through undistorted — important for data signals (eye diagrams, chirps), less so for audio. Symmetric FIR taps give it for free; IIR filters cannot have it (except by processing blocks forwards and backwards offline).

## The math

### Level 1 — specifications and structures
- Normalised frequency $\omega = 2\pi f/f_s$ rad/sample (or $f/f_s$ cycles/sample). A digital filter scales with $f_s$ ([sampling](sampling-aliasing-bandpass-sampling.md)).
- **Low-pass spec**: pass-band edge $f_p$, stop-band edge $f_{st}$, transition $\Delta f = f_{st}-f_p$; pass-band ripple $\delta_1$ (peak deviation, linear; in dB $R_p \approx 17.37\,\delta_1$ peak-to-peak for small $\delta_1$); stop-band attenuation $A = -20\log_{10}\delta_2$ dB.
- **FIR**: $y[n] = \sum_{k=0}^{N-1}h[k]x[n-k]$; transfer function $H(z) = \sum h[k]z^{-k}$ (zeros only). $N$ taps, "order" $N-1$.
- **IIR**: $y[n] = \sum_{k=0}^{M}b_kx[n-k] - \sum_{k=1}^{P}a_ky[n-k]$, $H(z) = B(z)/A(z)$ (poles and zeros). Stable iff all poles satisfy $|p|<1$.
- **Frequency response** $H(e^{j\omega}) = H(z)|_{z=e^{j\omega}}$; magnitude in dB and phase $\phi(\omega)$; **group delay** $\tau_g(\omega) = -d\phi/d\omega$ (samples) = delay of the envelope of a narrowband signal at $\omega$.
- Cost: an FIR needs $N$ multiply–accumulates (MACs) per output sample; a biquad needs 5.

### Level 1½ — two filters you can do by hand
You do not need $z$ to understand the two simplest filters; $H(z)$ is just their bookkeeping.
- **Moving average (FIR).** $y[n] = \tfrac14(x[n]+x[n-1]+x[n-2]+x[n-3])$. At DC every sample is the same, so the output equals the input (gain 1). Now feed a tone at $f_s/4$, whose samples are 1, 0, −1, 0, …: any four consecutive samples add to zero, so that tone is removed completely. The same happens at $f_s/2$ (1, −1, 1, −1). In general an $N$-tap average has gain $\left|\dfrac{\sin(N\pi f/f_s)}{N\sin(\pi f/f_s)}\right|$, with nulls at multiples of $f_s/N$. Its output lags by $(N-1)/2$ samples at every frequency, because the taps are symmetric (linear phase).
- **Exponential average (IIR, one pole).** $y[n] = y[n-1] + \alpha\,(x[n] - y[n-1])$. Each new sample moves the output a fraction α of the way towards the input. After a step the remaining error shrinks by $(1-\alpha)$ per sample, so the time constant is about $1/\alpha$ samples. Equivalently the −3 dB frequency is about $\alpha f_s/2\pi$ for small α. One multiply and one memory cell do what a long FIR would need many taps for, but the phase is not linear.
- **Which to use.** An FIR is used where the phase must stay linear, for example to keep a pulse shape or the data symbols intact. An IIR is used where cost matters and the phase does not, for example to smooth an RSSI reading or a sensor value.

*Worked numbers (verified, `tools/verify/s18_level15_numbers.py`).*
- **Moving average:** at $f_s$ = 1 kHz the 4-tap average passes 100 Hz with gain 0.769 (−2.3 dB), nulls 250 Hz and 500 Hz exactly, and delays everything by 1.5 ms.
- **Exponential average:** with α = 0.1 at $f_s$ = 100 Hz the time constant is 0.095 s (≈ 10 samples) and the exact −3 dB point is 1.68 Hz (the small-α estimate gives 1.59 Hz). See [z-transform](../00-math-foundations/z-transform-and-discrete-time-systems.md) for the same filter written as $H(z)$.

### Level 2 — FIR design, linear phase, IIR design
**Window method.** The ideal low-pass with cut-off $\omega_c$ has impulse response $h_d[n] = \frac{\omega_c}{\pi}\mathrm{sinc}\big(\frac{\omega_c}{\pi}(n-\frac{N-1}{2})\big)$, infinitely long. Truncate and taper: $h[n] = h_d[n]w[n]$. Multiplication by $w$ convolves the ideal brick-wall response with the window's transform $W(e^{j\omega})$ ([FFT windows](fft-spectral-analysis-windows.md)), so (i) the transition width is set by the window's main-lobe width, ∝ $1/N$, and (ii) the ripple is set by the window's sidelobe *area* — independent of $N$. Kaiser's window gives an adjustable trade with closed-form design formulas [5], [1 §7.5]:
$$\beta = \begin{cases}0.1102(A-8.7) & A>50\\ 0.5842(A-21)^{0.4}+0.07886(A-21) & 21\le A\le50\\ 0 & A<21\end{cases},\qquad N \approx \frac{A-7.95}{2.285\,\Delta\omega}+1,\ \ \Delta\omega = 2\pi\Delta f/f_s .$$
Script §1: for $A$ = 70 dB, $\Delta f/f_s$ = 0.05 the formulas give $N$ = 88, β = 6.755 (identical to `scipy.signal.kaiserord`), and the resulting filter reaches 68.8 dB — the formula is approximate by 1–2 dB. Because β (not $N$) sets the sidelobe level, adding taps does not fix a shortfall; design for $A$ + 2 dB instead (71.4 dB with $N$ = 91).

**Least squares (LS).** Choose $h$ to minimise the weighted integrated squared error $\int W(\omega)|H(e^{j\omega})-D(\omega)|^2d\omega$ — a linear least-squares problem with a closed-form solution (`firls`). LS minimises error *energy*: good when what matters is total out-of-band noise power (e.g. decimation filters where many aliasing bands add up), worse for a peak spec (script §3: for 61 taps, LS had 2.2 dB lower total weighted error than equiripple, but a stop-band peak of −49 dB vs −66 dB).

**Parks–McClellan (equiripple, minimax).** Minimise the *maximum* weighted error $\max_\omega W(\omega)|H-D|$. For linear-phase FIRs, the alternation theorem says the optimum has at least $L+2$ equal-height extrema of alternating sign ($L$ = number of cosine terms), and the Remez exchange algorithm finds it [3], [4]. With weights $W = 1/\delta_1$ in the pass-band and $1/\delta_2$ in the stop-band it gives the **shortest filter** meeting a peak spec. Useful length estimates (script §2, true minimum found by searching `remez` lengths):

| Spec ($f_p$, $f_{st}$ as fraction of $f_s$; ripple; $A$) | True min (PM) | Kaiser est. | Bellanger | harris $A/(22\Delta f/f_s)$ | Kaiser *window* design |
|---|---|---|---|---|---|
| 0.20, 0.25; 0.1 dB; 60 dB | 59 | 55 | 57 | 55 | 74 |
| 0.10, 0.12; 0.1 dB; 80 dB | 173 | 170 | 175 | 182 | 252 |
| 0.40, 0.45; 0.5 dB; 50 dB | 41 | 39 | 41 | 45 | 60 |
| 0.05, 0.07; 0.05 dB; 90 dB | 201 | 198 | 201 | 205 | 287 |

with Kaiser's estimate for equiripple filters $N \approx \dfrac{-20\log_{10}\sqrt{\delta_1\delta_2}-13}{14.6\,\Delta f/f_s}+1$ [1 §7.7], Bellanger's $N\approx\frac23\log_{10}\!\big(\frac{1}{10\delta_1\delta_2}\big)\frac{f_s}{\Delta f}$ [7], and harris' $N\approx\frac{A}{22}\frac{f_s}{\Delta f}$ [6] (which ignores pass-band ripple — fine for the usual 0.1 dB). More refined formulas exist (Herrmann–Rabiner–Chan [8]); all are starting points — always check the designed response.

**Linear phase.** If $h[n] = h[N-1-n]$ (symmetric), $H(e^{j\omega}) = e^{-j\omega(N-1)/2}A(\omega)$ with $A$ real, so $\tau_g = (N-1)/2$ samples at every frequency (script §4: exactly 30.000 samples for 61 taps). Four types exist [1 §5.7]: I (odd $N$, symmetric — any response), II (even $N$, symmetric — forced zero at $f_s/2$, no high-pass), III (odd, antisymmetric — zeros at 0 and $f_s/2$; Hilbert transformers, differentiators), IV (even, antisymmetric — zero at DC). Symmetry halves the multiplies (pre-add $x[n-k]+x[n-N+1+k]$ then multiply), which is why FPGA DSP slices have pre-adders ([FPGA](fpga-for-sdr.md)). If delay matters more than phase linearity (e.g. a control loop or low-latency audio), a **minimum-phase** FIR with the same magnitude has most of its energy up front and much less delay.

**IIR from analogue prototypes.** Design the analogue filter, then map $s\to z$ [1 §7.1–7.3], [2 ch. 6]:
- *Butterworth*: $|H(j\Omega)|^2 = 1/(1+(\Omega/\Omega_c)^{2N})$ — maximally flat, monotonic, gentlest roll-off.
- *Chebyshev I*: equiripple pass-band, monotonic stop-band; *Chebyshev II* (inverse): flat pass-band, equiripple stop-band (with zeros).
- *Elliptic (Cauer)*: equiripple in both — the minimum order for a given spec, worst phase/group-delay.
- *Bessel*: maximally flat group delay; its phase property is **not** preserved by the bilinear transform.
The analogue prototypes are the same ones used for LC ladders ([passive filters](../01-circuit-theory/passive-filter-design-prototypes.md)) and active filters ([active filters](../05-analog-electronics/active-filters.md)).

**Bilinear transform and prewarping.** Substituting $s = \frac{2}{T}\frac{1-z^{-1}}{1+z^{-1}}$ maps the whole $j\Omega$ axis once onto the unit circle and the left half-plane into the unit disc — so stable analogue filters stay stable and there is no aliasing. On the unit circle, $z=e^{j\omega}$ gives $s = j\frac{2}{T}\tan(\omega/2)$, i.e.
$$\Omega = \frac{2}{T}\tan\frac{\omega}{2}\quad\Longleftrightarrow\quad f_{digital} = \frac{f_s}{\pi}\arctan\!\left(\frac{\pi f_{analog}}{f_s}\right).$$
Frequencies are compressed towards $f_s/2$. To land an edge exactly at $f_c$, design the analogue prototype at the prewarped $\Omega_c = 2f_s\tan(\pi f_c/f_s)$. Script §5: a 4th-order Butterworth at 15 kHz, $f_s$ = 48 kS/s, lands at 11 859 Hz without prewarp (matching the arctan formula) and at 15 000 Hz with it. Only one frequency per band edge can be matched exactly; the rest of the response is warped, which is harmless for piecewise-constant specs. *Impulse invariance* (sampling the analogue impulse response) preserves time-domain shape but aliases, so it is only suitable for strongly band-limited low-pass designs.

*The z-transform behind these designs (ROC, z-plane stability, the bilinear map derived from trapezoidal integration, impulse invariance and matched-z compared, Euler mappings): [z-transform and discrete-time systems](../00-math-foundations/z-transform-and-discrete-time-systems.md).*

**IIR vs FIR cost.** Script §6 (pass-band 0.20 $f_s$, stop-band 0.24 $f_s$, 0.5 dB, 60 dB): Butterworth needs order 32, Chebyshev I and II 12, elliptic 7 (4 biquads ≈ 20 multiplies/sample) versus a 59-tap equiripple FIR (30 multiplies with symmetry). The IIR advantage grows for narrower transitions but comes with non-constant group delay — script §9: a 6th-order Butterworth at 0.2 $f_s$ has 2.7 samples delay at DC rising to 6.7 samples near the edge — which smears data symbols near the band edge.

### Level 3 — structures, quantisation, fixed point
**Structures.** Direct form I/II implements $B(z)/A(z)$ literally; the *transposed* direct form II has better numerical behaviour in floating point; the *cascade of second-order sections* (SOS/biquads) factors the filter into pairs of complex-conjugate poles and zeros; lattice and state-space forms are alternatives with better sensitivity. For FIRs: direct (tapped delay line), transposed (good for FPGA pipelining — the adder chain is registered), folded/symmetric, polyphase (multirate, [multirate](multirate-dsp-decimation-cic.md)), and FFT fast convolution (overlap-save/overlap-add) for very long filters, where the cost per output drops from $N$ to about $4\log_2(2N)$ real multiplies.

**Coefficient sensitivity.** The roots of a high-degree polynomial are extremely sensitive to its coefficients when roots cluster — and a narrow low-pass IIR has all its poles clustered near $z=1$. Script §7: a 10th-order elliptic low-pass (edge at 0.025 $f_s$, 80 dB) with coefficients rounded to 16 bits in direct form has a pole at |z| = 1.96 — unstable. The identical design as five 16-bit biquads keeps every pole inside the circle (max 0.998) with 0.05 dB pass-band error. Rule: never implement an IIR above order 2 in direct form; use `sos` output (`scipy.signal.*(..., output='sos')`, `sosfilt`). Narrowband IIRs at high sample rates are the hardest case — decimate first.

**FIR coefficient quantisation.** Rounding taps to $B$ bits adds an error sequence of variance ≈ $q^2/12$ per tap ($q = 2^{-(B-1)}$ relative to the largest tap scale), whose spectrum is roughly flat, so it sets a stop-band floor that improves ≈ 6 dB per bit. Script §8 (a 137-tap, 100 dB design): 8 bits → 35.8 dB, 10 → 46.7, 12 → 58.7, 14 → 71.3, 16 → 80.8, 18 → 93.2 dB (fitted slope 5.9 dB/bit). Rule of thumb: coefficient bits ≈ $A/6 + 2$ (e.g. 16–18 bits for 80–90 dB), which is why FPGA DSP slices have 18-bit coefficient inputs. Linear phase survives quantisation (symmetry is exact).

**Fixed-point arithmetic.**
- *Word growth*: a $B_x$-bit × $B_h$-bit product needs $B_x+B_h$ bits; summing $N$ products needs $\lceil\log_2N\rceil$ guard bits in the worst case (tighter: $\log_2\sum|h|$). Example: 16-bit samples, 18-bit taps, 83 taps → 16+18+7 = 41-bit accumulator.
- *Round-off noise*: truncating the output to $B_y$ bits adds white noise of $q_y^2/12$; for IIRs this noise is shaped (amplified) by the recursive part, often by tens of dB for narrowband poles — another reason to decimate before narrow IIRs.
- *Overflow and scaling*: scale so that the internal nodes cannot overflow for the expected signals ($L_\infty$ / $L_1$ norms for guaranteed no-overflow, $L_2$ for "rarely"); use saturation, never wrap-around, in IIR feedback paths.
- *Limit cycles*: IIRs in fixed point can sustain small oscillations with zero input (granular limit cycles) or large ones after overflow; FIRs cannot [1 §6.9–6.10].
- *Q-format*: "Q1.15" means 1 sign/integer bit and 15 fractional bits; multiply Q1.15 × Q1.17 → Q2.32; keep track on paper.

**Floating point is not a cure-all.** float32 has a 24-bit mantissa (≈ 144 dB dynamic range). It is ample for FIRs and SOS IIRs but a high-order direct-form IIR can still fail; and accumulating long sums (e.g. a running phase or an integrator) loses precision — CIC filters and NCO phase accumulators use integers for exactly this reason ([multirate](multirate-dsp-decimation-cic.md), [NCO](nco-ddc-duc.md)).

**Simplest useful IIRs in SDR code.** The exponential averager $y[n] = y[n-1] + \alpha(x[n]-y[n-1])$ (time constant ≈ $1/\alpha$ samples; used for AGC, power meters, display averaging); the DC blocker $H = (1-z^{-1})/(1-\alpha z^{-1})$ ([IQ](iq-complex-baseband.md)); FM de-emphasis (one pole) ([demodulation](software-demodulation.md)).

## Design equations & rules of thumb

| Equation / rule | When valid | Typical values |
|---|---|---|
| $N\approx\frac{A}{22}\frac{f_s}{\Delta f}$ (harris) | equiripple FIR, small ripple | 60 dB, Δf = 0.05 fs → 55 (true 59) |
| $N\approx\frac{-20\log\sqrt{\delta_1\delta_2}-13}{14.6\,\Delta f/f_s}+1$ (Kaiser) | equiripple FIR | within ~7 % |
| $N\approx\frac{A-7.95}{2.285\cdot2\pi\Delta f/f_s}+1$, β formula | Kaiser *window* FIR | ~25–45 % longer than PM; design for A+2 dB |
| $\tau_g = (N-1)/2$ samples | symmetric FIR | 83 taps at 500 kS/s: 82 µs |
| $\Omega_c = 2f_s\tan(\pi f_c/f_s)$ | bilinear prewarp | 15 kHz @ 48 kS/s: else lands 11.86 kHz |
| Butterworth order $N\ge\frac{\log(10^{A/10}-1)}{2\log(f_{st}/f_p)}$ | analogue/bilinear (prewarped) | [sampling](sampling-aliasing-bandpass-sampling.md) AAF examples |
| Order: elliptic < Chebyshev < Butterworth | same spec | 7 : 12 : 32 (script) |
| Coefficient bits ≈ A/6 + 2 | FIR stop-band floor | 80 dB → 16 bits |
| Accumulator bits = $B_x + B_h + \lceil\log_2 N\rceil$ | fixed-point FIR | 16+18+7 = 41 |
| IIR: SOS only, never high-order direct form | always | 16-bit tf unstable, SOS fine |
| Cost: $N$ MAC/output ($N/2$ folded); IIR ~5 per biquad | per output sample | ×output rate for MAC/s |

## Worked examples

**1 — LoRa BW125 channel filter after decimating to 500 kS/s.** Pass ±62.5 kHz, stop from ±80 kHz, 0.1 dB ripple, 60 dB rejection (adjacent LoRa channels are usually 200 kHz or more away, so 60 dB is generous). $\Delta f/f_s$ = 17.5/500 = 0.035; harris: $60/(22\times0.035)$ = 78 taps; the script's true Parks–McClellan minimum is **83 taps**, group delay 41 samples = 82 µs. Complex data: 83 real-coefficient taps × 2 (I and Q) × 500 kS/s = 83 M real MACs/s (≈ 42 M folded) — negligible for a PC (GNU Radio's FIR kernels use VOLK SIMD), heavy but feasible for a Cortex-M7. For LoRa the sharpness is not critical: the dechirp FFT itself rejects out-of-band noise; the filter's job is to prevent aliasing when decimating.

**2 — Why not filter at the SDR's 2.4 MS/s directly?** The same transition (17.5 kHz) at 2.4 MS/s is $\Delta f/f_s$ = 0.0073 → harris ≈ 374 taps × 2.4 MS/s ≈ 0.9 G real MACs/s per rail. Multistage decimation (CIC or half-bands first, then this 83-tap filter at the low rate) cuts that by more than 10× — see [multirate Example 1](multirate-dsp-decimation-cic.md).

**3 — FM de-emphasis as a digital IIR.** Broadcast FM uses a 50 µs (most of the world) or 75 µs (Americas, South Korea) time constant: corner $f_c = 1/(2\pi\tau)$ = 3183 Hz (50 µs). At an audio rate of 48 kS/s, prewarp: $\Omega_c = 2\cdot48000\tan(\pi\cdot3183/48000)$ = 2π × 3230 Hz — design the analogue prototype with a 3230 Hz corner so that after the bilinear map the digital corner is exactly 3183 Hz (without prewarping the error is only 1.5 % here, because 3.2 kHz ≪ $f_s/2$; it matters for edges above ~$f_s/10$). One pole, one zero, 3 multiplies per sample. Details: [software demodulation](software-demodulation.md), [analog modulation (pre-/de-emphasis)](../10-comms-modulation/analog-modulation-am-fm-pm-ssb.md).

**4 — Fixed-point budget for an FPGA channel filter.** 16-bit ADC-derived samples, 83 taps, 70 dB stop-band target: coefficient bits ≈ 70/6 + 2 ≈ 14 → use the DSP slice's native 18 bits (≈ 90 dB floor available). Accumulator 16 + 18 + 7 = 41 bits (fits the 48-bit DSP48 accumulator). Output: round to 16 bits (adds noise 98 dB below full scale — far below the input noise). Throughput: at 500 kS/s and a 100 MHz FPGA clock, one DSP slice can time-share all 83 taps (200 clocks available per sample).

**5 — Choosing IIR vs FIR for a telemetry receiver's audio-band filter.** A 2-FSK demodulator's post-discriminator low-pass (data filter) at 9.6 kbit/s: phase matters (eye opening), so use a linear-phase FIR (or a Gaussian/RRC matched filter per [pulse shaping](../10-comms-modulation/pulse-shaping-isi.md)). An audio monitor for a voice channel: phase doesn't matter, and a 4th-order elliptic IIR (2 biquads) is ~8× cheaper than the equivalent FIR.

## Practical notes
- **In Python**: `scipy.signal.remez` (equiripple; use `fs=` argument), `firls`, `firwin` (window method, `window=('kaiser', beta)`), `kaiserord`; IIR `butter/cheby1/cheby2/ellip(..., output='sos', fs=fs)` + `sosfilt`/`sosfiltfilt` (zero-phase offline). Always plot `freqz`/`sosfreqz` and check the spec.
- **In GNU Radio**: `firdes.low_pass(gain, fs, cutoff, transition, window)` (window method — note it takes a *transition width*, and its length follows from the window's design rule), `optfir.low_pass(...)` for equiripple, the `Filter Design Tool` (`gr_filter_design`), `IIR Filter` block (takes feed-forward/feedback taps — keep orders low), `Frequency Xlating FIR Filter` (mix + filter + decimate) ([GNU Radio](gnu-radio-and-software-stack.md)).
- **Filter delay adds up** across a chain: every linear-phase FIR contributes $(N-1)/2$ samples at *its* rate. For a half-duplex link or a radar range gate, total it up.
- **Edge effects**: `lfilter` output starts with a transient of length $N$; `filtfilt` doubles the order and removes phase but is non-causal (offline only).
- **Complex-coefficient filters** (a real low-pass modulated by $e^{j\omega_0n}$) filter one side of the spectrum only — the basis of offset-channel filtering and polyphase channelisers.
- **Test with real signals**, not just the magnitude plot: pass an impulse (check the taps), a step (ringing/overshoot), and a chirp through the filter.

## Common mistakes & misconceptions
1. **"More taps always means a sharper filter."** Only with the design re-run for the new length; the window method's stop-band floor is set by the window (β), not $N$.
2. **Specifying cut-off without transition width.** "A 100 kHz low-pass" is not a spec. Give $f_p$, $f_{st}$, ripple and $A$.
3. **Implementing high-order IIRs as one transfer function** (`b, a = butter(10, ...)`; `lfilter(b, a, x)`) — numerically fragile even in float64 for narrow bands. Use SOS.
4. **Forgetting to prewarp** when mapping an analogue design with the bilinear transform (or using tools that don't) — edges move towards DC.
5. **Assuming IIR filters "have no delay".** They have less latency than an equivalent linear-phase FIR, but their group delay varies strongly with frequency and peaks near the band edge.
6. **Quantising FIR taps to 8 bits** and expecting 60 dB: the floor is ≈ 36 dB.
7. **Normalisation confusion**: MATLAB/older scipy normalise frequency to Nyquist (1 = $f_s/2$); many texts use cycles/sample (0.5 = $f_s/2$); GNU Radio uses Hz with an explicit $f_s$. A factor-of-2 error puts your cut-off in the wrong place.
8. **Using a Bessel prototype through the bilinear transform** to get linear phase — the warping destroys the flat group delay; use an FIR.
9. **Ignoring gain of the filter** — a decimating FIR designed with unity DC gain passes a full-scale signal fine, but sums of several interferers can still overflow fixed point; check $\sum|h|$.
10. **"Zeroing FFT bins is a perfect brick-wall filter."** Block FFT → zero bins → IFFT multiplies the block's DFT by an ideal mask, which in time is *circular* convolution with a periodic sinc: (i) a signal that is not bin-centred is spread over every bin by the rectangular block window (Dirichlet leakage ∝ 1/(πm) at m bins away), so the part leaked into the kept bins survives — with N = 1024 and the cut-off at bin 200, an off-bin interferer at bin 300.5 is rejected by only **31 dB**, and the swept "stop-band" is ≈ −20 dB just past the edge and ≈ −27 dB 50 bins away; (ii) the circular wrap and the block-by-block processing create discontinuities at every block edge — an in-band tone streamed through it has errors 350× larger at block boundaries than mid-block, i.e. spurs at multiples of $f_s/N$; (iii) the operation is time-varying, so it has no true frequency response. It only *looks* perfect in toy tests whose tones sit exactly on bin centres (270 dB "rejection"). The FFT-domain filter that works is **fast convolution**: design an FIR (e.g. 255-tap Kaiser, β = 8.6: −88 dB stop-band, 105 dB at bin 300.5) and apply it with **overlap-save/overlap-add**, which matches direct convolution to 1e-15 — `tools/verify/fix_fft_bin_zeroing.py`. (Myth flagged by W4-D1 from dsp.stackexchange.com/q/6220; the standard treatment is Oppenheim & Schafer's sections on block convolution and the DFT [1].)

## How to simulate / verify
- `python3 tools/verify/fix_fft_bin_zeroing.py` (< 1 s): why FFT bin-zeroing is a poor filter (on-bin vs off-bin interferer, swept response, block-edge errors) and the overlap-save FIR that replaces it. ALL PASS.
- `python3 tools/verify/dsp_filters.py` (≈ 2 s): Kaiser formulas and achieved attenuation; four-spec comparison of length estimates vs true minimum Parks–McClellan length; LS vs equiripple; linear-phase group delay; bilinear prewarping; IIR order comparison and elliptic spec check; 16-bit direct-form vs SOS stability; FIR coefficient bits vs stop-band; Butterworth group delay; LoRa channel filter length. All PASS.
- Quick design loop: design → `freqz` → check pass-band ripple and stop-band → quantise taps (`np.round(h*2**(B-1))/2**(B-1)`) → re-check → simulate on a two-tone test signal.
- For fixed-point bit-true simulation, model the arithmetic in Python with integers (or `numpy` int64) exactly as the FPGA will do it, then compare with float ([FPGA](fpga-for-sdr.md)).

## Open questions / gaps
- harris' $A/22$ rule is quoted from his book as commonly cited; the exact section was not re-read this session.
- Round-off noise gain of IIR structures (quantitative) and limit-cycle bounds are described, not simulated.
- Minimum-phase FIR design (e.g. `scipy.signal.minimum_phase`) and its delay savings not demonstrated numerically.

## Sources
1. A. V. Oppenheim, R. W. Schafer, *Discrete-Time Signal Processing*, 3rd ed., Pearson (2010): ch. 5 (linear-phase systems, group delay, minimum phase, generalised linear phase types), ch. 6 (structures, coefficient quantisation, round-off noise, limit cycles), ch. 7 (bilinear transform, window method, Kaiser formulas, optimum equiripple approximation and length estimate), ch. 8 §8.7 (linear convolution with the DFT: circular vs linear convolution, overlap-add/overlap-save block convolution — the basis of mistake 10). (textbook)
2. R. G. Lyons, *Understanding Digital Signal Processing*, 3rd ed., Prentice Hall (2011): ch. 5 (FIR), ch. 6 (IIR, bilinear, cascaded biquads), ch. 12 (fixed-point formats and overflow). (textbook)
3. T. W. Parks, J. H. McClellan, "Chebyshev approximation for nonrecursive digital filters with linear phase," *IEEE Trans. Circuit Theory* CT-19(2):189–194 (1972). (peer-reviewed)
4. J. H. McClellan, T. W. Parks, L. R. Rabiner, "A computer program for designing optimum FIR linear phase digital filters," *IEEE Trans. Audio Electroacoustics* AU-21(6):506–526 (1973). (peer-reviewed)
5. J. F. Kaiser, "Nonrecursive digital filter design using the I0-sinh window function," *Proc. IEEE Int. Symp. Circuits and Systems* (1974), pp. 20–23. (peer-reviewed conference) — Kaiser window formulas (as reproduced in [1] §7.5).
6. f. j. harris, *Multirate Signal Processing for Communication Systems*, Prentice Hall (2004; 2nd ed. River Publishers 2021), ch. 3 (FIR design; the $N\approx(f_s/\Delta f)(A/22)$ estimate). (textbook) — *section not re-read this session.*
7. M. Bellanger, *Digital Processing of Signals: Theory and Practice*, 3rd ed., Wiley (2000), ch. 5 (FIR length estimate). (textbook) — *formula as commonly cited; cross-checked numerically here.*
8. O. Herrmann, L. R. Rabiner, D. S. K. Chan, "Practical design rules for optimum finite impulse response lowpass digital filters," *Bell System Technical Journal* 52(6):769–799 (1973). (peer-reviewed)
9. J. G. Proakis, D. G. Manolakis, *Digital Signal Processing*, 4th ed., Pearson (2007), ch. 9–10 (structures, design, quantisation effects). (textbook)
10. SciPy documentation, `scipy.signal` (remez, firls, firwin, kaiserord, butter/cheby1/cheby2/ellip, bilinear, sosfilt), https://docs.scipy.org/doc/scipy/reference/signal.html. (docs) — tools used in the verification script.
