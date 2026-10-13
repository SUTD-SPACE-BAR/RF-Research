---
title: Fourier series and the Fourier transform
domain: 00-math-foundations
slug: fourier-series-and-transform
tags: [fourier, spectrum, harmonics, sinc, emi, parseval, convolution, modulation, chirp, pulsed-rf, dft, time-bandwidth]
prerequisites: [complex-numbers-and-phasors.md, decibels-and-log-units.md]
related:
  - linear-systems-convolution.md
  - laplace-transfer-functions-bode.md
  - special-functions-bessel-sinc.md
  - probability-random-processes-and-psd.md
  - numerical-methods-overview.md
  - ../14-sdr-dsp/fft-spectral-analysis-windows.md
  - ../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md
  - ../13-pcb-rf-layout-emc/emc-emi-fundamentals.md
  - ../11-radar/pulsed-radar-and-pulse-compression.md
  - ../15-lora-ism-radios/lora-phy-css-math.md
  - ../12-phased-arrays/array-factor-linear-arrays.md
level: mixed
confidence: high
last_updated: 2026-10-02
---

# Fourier series and the Fourier transform

## Questions this page answers
- What does it mean that "every signal is a sum of sine waves"?
- Why does a square wave contain only odd harmonics, and how big are they?
- Why do fast clock edges cause EMI hundreds of MHz above the clock frequency?
- Could my flight computer's 24 MHz or 40 MHz clock interfere with my 433/900 MHz LoRa receiver?
- What is a sinc function and why does it appear everywhere?
- What is the time–bandwidth product, and why can't a signal be both short and narrowband?
- What do Parseval's theorem, the convolution theorem and the modulation theorem say, in plain words?
- What does the spectrum of a radar pulse train look like?
- What does the spectrum of a chirp (radar or LoRa) look like, and why is its bandwidth B regardless of length?
- How is the DFT/FFT related to the "real" Fourier transform?
- Why is an antenna's far-field pattern the Fourier transform of its aperture?

## TL;DR
- **Fourier series**: a periodic signal with period $T$ is a sum of harmonics at $n f_0$, $f_0=1/T$: $x(t)=\sum_n c_ne^{j2\pi nf_0t}$, $c_n=\frac1T\int_T x(t)e^{-j2\pi nf_0t}dt$. Real signals: $c_{-n}=c_n^*$, one-sided amplitude $2|c_n|$.
- **Fourier transform** (KB convention, $f$ in Hz): $X(f)=\int x(t)e^{-j2\pi ft}dt$, $x(t)=\int X(f)e^{j2\pi ft}df$. No $2\pi$ factors to remember.
- Key pair: a rectangular pulse of width $\tau$ ↔ $\tau\,\mathrm{sinc}(f\tau)$, $\mathrm{sinc}(u)=\sin(\pi u)/(\pi u)$: nulls at $k/\tau$, first sidelobe −13.3 dB, −3 dB full width $0.886/\tau$.
- Square wave (±A, 50 %): odd harmonics only, amplitude $4A/(\pi n)$. Real clock (trapezoid, width $\tau$, edge $t_r$): harmonics $2A\frac{\tau}{T}|\mathrm{sinc}(n\tau/T)\,\mathrm{sinc}(nt_r/T)|$; envelope flat, then −20 dB/dec above $1/(\pi\tau)$, then −40 dB/dec above $1/(\pi t_r)$. **Edge rate, not clock rate, sets the high-frequency EMI.**
- Theorems: delay ↔ linear phase; multiply by $\cos 2\pi f_ct$ ↔ shift spectrum to $\pm f_c$ (half amplitude each) — this *is* mixing/modulation; convolution ↔ multiplication (filters); energy is the same in both domains (Parseval/Rayleigh); compress in time ↔ stretch in frequency.
- Time–bandwidth: rms duration × rms bandwidth ≥ $1/(4\pi)$ (equality for Gaussians). A chirp beats "short = wide" by being *long and wide*: its spectrum is ~flat over the swept bandwidth $B$ and its TB product is large — for LoRa, $T_sB=2^{SF}$ (128 to 4096).
- Pulsed RF (pulse width $\tau$, PRF $f_p$): lines at $f_c\pm kf_p$ under a sinc envelope with nulls at $f_c\pm k/\tau$.
- DFT: $N$ samples at $f_s$ give bins every $f_s/N$ and assume the record repeats; leakage and windows are covered in [FFT and windows](../14-sdr-dsp/fft-spectral-analysis-windows.md).

## Intuition (no math)
A prism splits white light into colours; a Fourier transform splits a signal into frequencies. It answers: "how much of each pure tone, and at what phase, do I need to add up to rebuild this waveform?" A spectrum analyser does this physically by sweeping a narrow filter; an FFT does it numerically.

Sharp features need high frequencies. A smooth sine needs one frequency. A square wave has vertical edges; to build a vertical edge out of smooth sines you need ever-higher harmonics, each smaller than the last. If the edges are not vertical but take 1 ns to rise, you don't need harmonics much beyond a few hundred MHz — the spectrum falls off faster above about $1/(\pi\times1\,\text{ns})\approx320$ MHz. That's why EMI engineers care about *edge rates*: slowing an edge from 0.3 ns to 3 ns can drop the 900 MHz content by 20 dB, without changing the clock frequency.

Short in time means wide in frequency. A camera flash (short) contains every colour; a laser (a long, steady wave) contains one. A 1 µs radar pulse occupies about 1 MHz; a 1 ns pulse occupies about 1 GHz. You can't have a pulse that is both 1 ns long and 1 kHz wide. The one loophole is to make the pulse *long* and sweep its frequency (a chirp): it is long (lots of energy, good for range) yet wide (good for resolution) — exactly what radar pulse compression and LoRa do.

Multiplying two signals in time shifts spectra around (that's what a mixer does); passing a signal through a filter multiplies its spectrum by the filter's response. These two ideas — "multiply here, convolve there" — are most of RF signal processing.

## The math

### Level 1 — harmonics and line spectra

**Fourier series in sine–cosine form.** A periodic signal with period $T$ (fundamental $f_0=1/T$) can be written
$$x(t)=a_0+\sum_{n=1}^{\infty}A_n\cos(2\pi nf_0t+\phi_n)$$
$a_0$ = DC (average) value; $A_n$ = amplitude of the $n$-th harmonic (V); $\phi_n$ = its phase. Plotting $A_n$ against $nf_0$ gives a **line spectrum** — what a spectrum analyser shows for a clock.

**Square wave, ±A, 50 % duty.** Only odd harmonics, with $A_n=\frac{4A}{\pi n}$: fundamental $1.273A$, 3rd $0.424A$ (−9.5 dB), 5th $0.255A$ (−14 dB), 7th $0.182A$ (−16.9 dB). The amplitudes fall as $1/n$, i.e. **−20 dB per decade** of frequency. The fundamental alone carries $8/\pi^2 = 81$ % of the power. (All verified numerically.) A 0-to-$V$ logic square wave is this with $A=V/2$ plus a DC term $V/2$.

**Why odd only?** A 50 % square wave has half-wave symmetry, $x(t+T/2)=-x(t)$ (after removing DC); even harmonics cannot have that symmetry, so their coefficients vanish. Any duty-cycle error brings even harmonics back.

**Frequency resolution.** Two tones $\Delta f$ apart can only be distinguished if you observe for $T_{\rm obs}\gtrsim1/\Delta f$ — the time–bandwidth idea at its simplest.

### Level 2 — complex series, the transform, and its theorems

**Complex exponential series.** Using $\cos\theta=\tfrac12(e^{j\theta}+e^{-j\theta})$ ([phasors](complex-numbers-and-phasors.md)):
$$x(t)=\sum_{n=-\infty}^{\infty}c_ne^{j2\pi nf_0t},\qquad c_n=\frac1T\int_{t_0}^{t_0+T}x(t)e^{-j2\pi nf_0t}dt.$$
The complex exponentials are orthogonal over one period, which is why each $c_n$ is found by "projecting" onto one of them [1 ch. 3], [2 L15]. For real $x$: $c_{-n}=c_n^*$, $A_n=2|c_n|$, $\phi_n=\angle c_n$. **Parseval (power form):** $\frac1T\int_T|x|^2dt=\sum|c_n|^2$ — average power is the sum of the powers in each harmonic.

**Gibbs phenomenon.** Truncating the series of a discontinuous signal leaves an overshoot of ≈8.95 % of the jump next to the edge, however many terms you keep; it gets narrower, not smaller (verified with 101 odd harmonics) [1 §3.4]. Physical relevance: band-limiting a fast edge (a filter or a limited-bandwidth scope) produces ringing of this size.

**The Fourier transform.** Let $T\to\infty$: lines merge into a continuum. With frequency $f$ in Hz:
$$X(f)=\int_{-\infty}^{\infty}x(t)e^{-j2\pi ft}\,dt,\qquad x(t)=\int_{-\infty}^{\infty}X(f)e^{j2\pi ft}\,df.$$
Units: if $x$ is in V, $X$ is in V/Hz (V·s). In $\omega$ form, $X(\omega)=\int x e^{-j\omega t}dt$ and $x=\frac1{2\pi}\int X e^{j\omega t}d\omega$ (Oppenheim & Willsky convention [1 ch. 4]). The $f$ form (Bracewell's [3]) is symmetric and is used throughout this KB. Physics texts often flip the sign of the exponent (tied to the $e^{-i\omega t}$ time convention).

**Relation between series and transform.** If one period of a periodic signal is $p(t)$ with transform $P(f)$, then $c_n=\frac1T P(n/T)$: the line spectrum is the single-pulse spectrum **sampled** at multiples of $f_0$. This is the key to pulse trains and clock spectra.

**Transform pairs worth knowing** ($a,\tau>0$)

| $x(t)$ | $X(f)$ | Notes |
|---|---|---|
| $\mathrm{rect}(t/\tau)$ (1 for $\lvert t\rvert<\tau/2$) | $\tau\,\mathrm{sinc}(f\tau)$ | nulls at $k/\tau$; −3 dB full width $0.886/\tau$; sidelobe −13.26 dB |
| $\Lambda(t/\tau)$ (triangle, base $2\tau$) | $\tau\,\mathrm{sinc}^2(f\tau)$ | rect ∗ rect; sidelobes −26.5 dB |
| $e^{-\pi t^2}$ | $e^{-\pi f^2}$ | Gaussian is its own transform |
| $e^{-at}u(t)$ | $\dfrac{1}{a+j2\pi f}$ | RC low-pass impulse response |
| $\delta(t)$ | $1$ | impulse contains all frequencies equally |
| $1$ | $\delta(f)$ | DC |
| $e^{j2\pi f_ct}$ | $\delta(f-f_c)$ | a single rotating phasor = one line |
| $\cos 2\pi f_ct$ | $\tfrac12[\delta(f-f_c)+\delta(f+f_c)]$ | two half-height lines |
| $\sum_k\delta(t-kT)$ | $\frac1T\sum_n\delta(f-n/T)$ | comb ↔ comb (sampling theory) |
| $\mathrm{sinc}(Bt)$ | $\frac1B\mathrm{rect}(f/B)$ | ideal low-pass (non-causal) |
| $u(t)$ (step) | $\tfrac12\delta(f)+\dfrac{1}{j2\pi f}$ | |

**Theorems** (each is a one-line substitution in the integral; see [1 §4.3–4.5], [3 "The basic theorems"]):

| Time domain | Frequency domain | RF meaning |
|---|---|---|
| $ax+by$ | $aX+bY$ | superposition |
| $x(t-t_0)$ | $X(f)e^{-j2\pi ft_0}$ | delay = linear phase (group delay; cable length) |
| $x(t)e^{j2\pi f_ct}$ | $X(f-f_c)$ | frequency shift (complex mixing, NCO) |
| $x(t)\cos 2\pi f_ct$ | $\tfrac12[X(f-f_c)+X(f+f_c)]$ | **modulation theorem**: AM, mixers, upconversion |
| $x(at)$ | $\frac1{\lvert a\rvert}X(f/a)$ | **similarity/scaling**: shorter ↔ wider |
| $dx/dt$ | $j2\pi f\,X(f)$ | derivatives emphasise high frequencies (edges) |
| $x*h$ | $X\,H$ | **convolution theorem**: filtering |
| $x\,h$ | $X*H$ | windowing, gating, mixing |
| $x^*(t)$ | $X^*(-f)$ | real $x$ ⇒ Hermitian spectrum |
| $X(t)$ | $x(-f)$ | duality |
| $\int\lvert x\rvert^2dt$ | $\int\lvert X\rvert^2df$ | **Parseval/Rayleigh**: energy conserved |

All five of Parseval, convolution, modulation, scaling and shift are checked in `tools/verify/math_fourier.py` (DFT versions).

**Energy vs power spectra.** For finite-energy signals (single pulses) $|X(f)|^2$ is the energy spectral density (J/Hz into 1 Ω). For power signals (clocks, carriers, noise) use line powers $|c_n|^2$ or the power spectral density (W/Hz), defined via autocorrelation — see [random processes and PSD](probability-random-processes-and-psd.md).

**Trapezoidal clock spectrum (the EMI workhorse).** Model a clock of amplitude $A$ (0 to $A$), period $T$, pulse width $\tau$ measured at the 50 % points, rise = fall time $t_r$. A trapezoid is a rectangle of width $\tau$ convolved with a rectangle of width $t_r$ (normalised to unit area) — convolving with the short rect is what "smooths" the edges into ramps. By the convolution theorem its single-pulse spectrum is the product of two sincs, and sampling at $n/T$ gives [4 §3.3], [5]:
$$|c_n| = A\frac{\tau}{T}\left|\mathrm{sinc}\!\left(\frac{n\tau}{T}\right)\right|\left|\mathrm{sinc}\!\left(\frac{nt_r}{T}\right)\right|,\qquad A_n=2|c_n|\ (n\ge1).$$
Bounding $|\mathrm{sinc}(u)|\le\min(1,1/(\pi|u|))$ gives a three-segment **envelope**: flat at $2A\tau/T$ up to $f=1/(\pi\tau)$, then −20 dB/decade, then −40 dB/decade above $f=1/(\pi t_r)$. Verified: FFT of a sampled 25 MHz, 3.3 V, 2 ns-edge trapezoid matches the formula to $<10^{-4}A$ at all harmonics tested.

### Level 3 — uncertainty, pulsed RF, chirps, DFT, and space-domain Fourier

**Time–bandwidth product.** With rms duration $\sigma_t$ and rms bandwidth $\sigma_f$ (second moments of $|x|^2$ and $|X|^2$ about their centroids),
$$\sigma_t\,\sigma_f\ \ge\ \frac{1}{4\pi}$$
with equality only for a Gaussian pulse (verified numerically: 0.0796). This is the signal-processing form of the uncertainty principle [3 "The two domains"], [6]. Other width definitions give other constants: for a rect pulse, null-to-null bandwidth $\times\tau=2$, −3 dB bandwidth $\times\tau=0.886$. "Bandwidth ≈ 1/duration" is the working rule; always state which width definition.

**Rise time and bandwidth.** For a single-pole (RC-like) response, 10–90 % rise time $t_r$ and −3 dB bandwidth $f_{3\rm dB}$ satisfy $t_rf_{3\rm dB}=\ln 9/(2\pi)=0.35$ (see [Laplace/Bode](laplace-transfer-functions-bode.md)). Scopes with Gaussian-like responses have 0.35–0.45.

**Pulsed RF spectrum.** A carrier $\cos2\pi f_ct$ gated by a pulse train of width $\tau$ and period $T_p=1/f_p$ (PRF) is (pulse train) × (carrier). By the modulation theorem the spectrum is the pulse train's line spectrum shifted to $\pm f_c$:
- lines spaced $f_p$ apart around $f_c$,
- under a $\mathrm{sinc}((f-f_c)\tau)$ envelope with nulls at $f_c\pm k/\tau$,
- main-lobe null-to-null width $2/\tau$,
- the carrier line itself is down by $20\log_{10}(\tau/T_p)$ from the peak-envelope amplitude (duty-cycle factor), and average power = peak power × duty.
Verified for $\tau=100$ ns, PRF 1 MHz. A single pulse gives the continuous envelope; a finite train of $N$ pulses turns each line into a sinc of width $\sim f_p/N$. See [pulsed radar](../11-radar/pulsed-radar-and-pulse-compression.md).

**Linear-FM chirp spectrum.** $s(t)=\mathrm{rect}(t/T)\,e^{j\pi\mu t^2}$ with sweep rate $\mu=B/T$ (Hz/s). Its instantaneous frequency is $f_i(t)=\mu t$, sweeping $-B/2\ldots+B/2$. By the **stationary-phase** argument, the transform at frequency $f$ is dominated by the instant $t=f/\mu$ when the chirp passes through $f$, so the magnitude spectrum is approximately $\sqrt{1/\mu}\,\mathrm{rect}(f/B)$ — flat over $B$ — with Fresnel-integral ripples at the edges that shrink as the time–bandwidth product $TB$ grows [7] (exact form in terms of Fresnel integrals: [special functions](special-functions-bessel-sinc.md)). Verified for $TB=200$: −6 dB width = 0.98 B, 99 % energy width = 1.03 B. After a matched filter the chirp compresses to a pulse of width ≈ $1/B$: compression ratio = $TB$.
- **LoRa**: symbol duration $T_s=2^{SF}/B$, so $T_sB=2^{SF}$ — from 128 (SF7) to 4096 (SF12). With $B=125$ kHz, $T_s=1.024$ ms at SF7 and 32.8 ms at SF12. The large TB product is the processing gain that lets LoRa demodulate below the noise floor (see [LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md), [spread spectrum](../10-comms-modulation/spread-spectrum-dsss-fhss-css.md)).
- **FMCW radar** uses the same chirp; beat frequency after dechirping is $\mu\cdot$(round-trip delay) ([FMCW](../11-radar/fmcw-radar.md)).

**The DFT.** For $N$ samples $x[n]=x(n/f_s)$:
$$X[k]=\sum_{n=0}^{N-1}x[n]e^{-j2\pi kn/N},\quad k=0\ldots N-1;\qquad x[n]=\frac1N\sum_kX[k]e^{j2\pi kn/N}.$$
Bin $k$ is at frequency $kf_s/N$ (bins above $N/2$ are negative frequencies). The DFT samples the spectrum of the *periodically repeated* record, so a tone that does not complete an integer number of cycles in the record "leaks" into neighbouring bins; windows trade leakage against resolution. Zero-padding interpolates the spectrum but does not add resolution. The FFT is just a fast $O(N\log N)$ algorithm for the DFT ([numerical methods](numerical-methods-overview.md)). Scaling to physical units (dBm per bin, dBm/Hz) and window corrections belong to [FFT and windows](../14-sdr-dsp/fft-spectral-analysis-windows.md); sampling/aliasing to [sampling](../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md). Parseval in DFT form: $\sum|x[n]|^2=\frac1N\sum|X[k]|^2$ (verified).

**Fourier optics / antennas.** In the far field, the radiation pattern of an aperture (or line source) is the spatial Fourier transform of its illumination, with the variable $u=\sin\theta/\lambda$ playing the role of frequency. A uniformly illuminated aperture of length $D$ gives a $\mathrm{sinc}(Du)$ pattern: first null at $\sin\theta=\lambda/D$, sidelobes −13.3 dB. An array's array factor is the discrete-time Fourier transform of its element weights, so tapering the weights (a "window") lowers sidelobes at the cost of beamwidth — the same trade as spectral windows. Circular apertures give the jinc/Airy pattern (Bessel $J_1$). See [array factor](../12-phased-arrays/array-factor-linear-arrays.md), [tapering](../12-phased-arrays/tapering-sidelobe-control.md), [special functions](special-functions-bessel-sinc.md).

**Convergence fine print.** The transform exists in the ordinary sense for absolutely integrable signals; sinusoids, steps and combs need generalised functions (delta "functions"). Fourier series converge in the mean-square sense for finite-power signals and pointwise to the midpoint at jumps (Dirichlet conditions) [1 §3.4], [3].

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $A_n=4A/(\pi n)$, odd $n$ | ideal ±A square wave | 3rd harmonic −9.5 dBc, 5th −14 dBc |
| $A_n = 2A\frac{\tau}{T}\lvert\mathrm{sinc}(n\tau/T)\mathrm{sinc}(nt_r/T)\rvert$ | trapezoid, $t_r=t_f$ | see example 2 |
| envelope breaks at $1/(\pi\tau)$ and $1/(\pi t_r)$ | trapezoid | 1 ns edge → 318 MHz |
| $c_n=P(n/T)/T$ | periodic repetition of pulse $p$ | |
| null-to-null BW $=2/\tau$; −3 dB BW $=0.886/\tau$ | rect pulse (baseband two-sided / RF) | 1 µs pulse: 2 MHz / 0.886 MHz |
| $\sigma_t\sigma_f\ge1/(4\pi)$ | rms widths | Gaussian equality |
| $t_rf_{3\rm dB}\approx0.35$ | single-pole system | 1 ns ↔ 350 MHz |
| lines at $f_c\pm kf_p$, nulls $f_c\pm k/\tau$ | pulsed carrier | |
| chirp spectrum ≈ flat over $B$ | $TB\gg1$ | LoRa $TB=2^{SF}$ |
| bin spacing $f_s/N$ | DFT | 2.4 MS/s, N = 2048: 1.17 kHz |
| Gibbs overshoot 8.95 % of jump | truncated series / brick-wall filter | |

## Worked examples

**1. 3.3 V, 50 % logic square wave.** DC = 1.65 V; the AC part is a ±1.65 V square wave. Fundamental amplitude $4(1.65)/\pi=2.10$ V peak; 3rd = 0.70 V; 5th = 0.42 V; 7th = 0.30 V. Ideal edges ⇒ the 101st harmonic is still 21 mV. Real edges cut this off (next example).

**2. Clock harmonics near your LoRa bands.** 25 MHz, 3.3 V, 50 % clock with 2 ns edges: breakpoints $1/(\pi\cdot20\text{ ns})=15.9$ MHz and $1/(\pi\cdot2\text{ ns})=159$ MHz. The 17th harmonic (425 MHz) has amplitude $2(3.3)(0.5)|\mathrm{sinc}(8.5)\,\mathrm{sinc}(0.85)|=21.0$ mV peak = 83.4 dBµV (rms) on the trace; with 0.5 ns edges it would be 115 mV (98.2 dBµV) — 15 dB worse. Other cases computed with the same formula:

| clock | harmonic | freq | duty | edge | amplitude on trace |
|---|---|---|---|---|---|
| 24 MHz (e.g. Teensy 4.1 crystal) | 18th | 432 MHz | exactly 50 % | 1 ns | ≈ 0 (even harmonic) |
| 24 MHz | 18th | 432 MHz | 49 % | 1 ns | 45 mV pk (90 dBµV) |
| 40 MHz (e.g. ESP32 crystal) | 23rd | 920 MHz | 50 % | 1 ns | 7.9 mV pk (75 dBµV) |
| 40 MHz | 23rd | 920 MHz | 50 % | 0.3 ns | 80 mV pk (95 dBµV) |

The 24 MHz case shows that "even harmonics vanish" is fragile: a 1 % duty-cycle error restores the 18th harmonic to within a few dB of the envelope. These are *voltages on a trace*, not received power — how much couples into the LoRa receiver depends on loop area, shielding and layout ([EMC fundamentals](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md), [mixed-signal layout](../13-pcb-rf-layout-emc/mixed-signal-layout.md)). But a LoRa receiver at −137 dBm sensitivity (32 nV) is ~120 dB below a 45 mV harmonic, so even −120 dB of isolation is marginal. Pick clock frequencies whose harmonics miss your channels, slow edges (series resistors, drive-strength settings), and use spread-spectrum clocking where available.

**3. Radar pulse spectrum.** A 5.8 GHz radar sends 1 µs pulses at PRF 1 kHz. Lines every 1 kHz around 5.8 GHz under a sinc envelope with first nulls at 5.8 GHz ± 1 MHz (null-to-null 2 MHz); −3 dB envelope width 0.886 MHz. Duty = $10^{-3}$, so average power is 30 dB below peak, and the carrier line is $20\log(10^{-3})=-60$ dB below the peak envelope amplitude (i.e. −30 dB in power relative to the average). A receiver needs ≈1 MHz of bandwidth to pass the pulse; range resolution $c\tau/2 = 150$ m.

**4. LoRa SF7 symbol spectrum.** $B=125$ kHz, $T_s=2^7/125\text{ kHz}=1.024$ ms, $TB=128$. The symbol's spectrum is nearly flat across 125 kHz with small Fresnel ripples at the band edges; the occupied bandwidth is set by $B$, not by the symbol length (unlike a 1 ms rectangular pulse, which would occupy ~2 kHz). After dechirping, all the symbol energy collapses into one FFT bin of width $1/T_s = B/2^{SF} = 977$ Hz, while noise is spread over all $2^{SF}=128$ bins — a $10\log_{10}128 = 21$ dB processing gain. At SF12 the bin is $125\,000/4096 = 30.5$ Hz and the gain 36 dB.

**5. What scope bandwidth do I need to see a 1 ns edge?** Using $t_rf_{3\rm dB}\approx0.35$: 350 MHz for the edge itself; for <3 % error on the measured rise time, choose a scope/probe system ≥3× faster, ~1 GHz.

**6. SDR FFT resolution.** An RTL-SDR at 2.4 MS/s with a 2048-point FFT: bins of $2.4\times10^6/2048=1.17$ kHz; record length 0.853 ms. To resolve two LoRa channels 125 kHz apart is trivial; to resolve the 977 Hz dechirped bins of SF7 (example 4) you need ≥ 1.024 ms of data (≥ 2458 samples), and for SF12's 30.5 Hz bins ≥ 32.8 ms (≈ 78 600 samples at 2.4 MS/s) — i.e. one whole symbol, as the time–bandwidth rule predicts.

## Practical notes
- **Spectrum analyser vs FFT**: an analyser with RBW narrower than the line spacing shows individual harmonics; with RBW wider than the line spacing (e.g. radar PRF 1 kHz, RBW 100 kHz) it shows the *envelope*, and the displayed level depends on RBW ("pulse desensitisation"). See [spectrum analysers](../17-test-measurement/spectrum-analyzers.md).
- **EMC scans** show clock harmonics as a picket fence; the envelope slope tells you about rise time: −40 dB/dec above $1/(\pi t_r)$.
- **Spread-spectrum clocking** dithers the clock frequency, smearing each harmonic line over a band; it reduces *peak* readings in a given RBW but not total power.
- **Scope FFTs** use windows; the reading of a single tone depends on the window's coherent gain and scalloping loss — use flat-top windows for amplitude.
- **Don't trust "odd harmonics only"**: real duty cycles differ from 50 % and edges are asymmetric.

## Common mistakes & misconceptions
1. **Forgetting the negative-frequency half.** For a real signal, a line of complex amplitude $c_n$ at $+nf_0$ has a twin at $-nf_0$; the physical (one-sided) amplitude is $2|c_n|$, power $2|c_n|^2$ (for $n\ne0$). Factor-of-2 (6 dB) errors come from this.
2. **Mixing $f$ and $\omega$ conventions** — misplaced $2\pi$ factors in transforms and in Parseval.
3. **"Clock frequency sets EMI."** Edge rate sets the upper spectrum; a slow 1 MHz clock with 0.5 ns edges can radiate more at 500 MHz than a 50 MHz clock with 5 ns edges.
4. **"A short pulse at frequency $f_c$ contains only $f_c$."** A gated carrier occupies ~$2/\tau$ around $f_c$ (key-clicks, splatter). The sharper the gating edges, the wider the splatter — PA ramping exists for this reason.
5. **"Zero-padding increases FFT resolution."** It interpolates; resolution is set by record length.
6. **Believing the chirp's bandwidth is $1/T$.** For $TB\gg1$ the bandwidth is the swept range $B$.
7. **Calling the sinc's first null the bandwidth without saying so** — null-to-null, −3 dB, 99 % power and rms bandwidths differ by factors of 2 or more.
8. **Fourier-series coefficients vs spectral density units** — lines are in V (or V²), continuous spectra are in V/Hz (or V²/Hz); don't compare them directly.
9. **Assuming Gibbs ringing is a measurement artefact to be "fixed" with more bandwidth** — it's intrinsic to a sharp frequency cutoff; a gentler roll-off (Gaussian-like) removes it.
10. **Numpy's `sinc` is the normalised one** ($\sin\pi x/\pi x$); some textbooks and MATLAB's older toolboxes define $\sin x/x$.
11. **"Series resistors on digital lines are only for signal integrity."** They also set the edge rate: with the trace/load capacitance they form a low-pass that raises $t_r$, and the trapezoid envelope above $1/(\pi t_r)$ falls 40 dB/dec instead of 20 dB/dec. Slowing a clock edge from 0.5 ns to 2 ns moves that corner from 637 MHz to 159 MHz: the 433 MHz harmonic content drops by $20\log_{10}(\pi\cdot433\text{ MHz}\cdot2\text{ ns}) = 8.7$ dB and everything above ~640 MHz by $20\log_{10}4 = 12$ dB (envelope bound above; exact lines from the sinc product). That is an EMC/self-desense tool for a board carrying a 433/868/915 MHz receiver or a GNSS front end, besides damping ringing (source termination). Use the slowest edge the timing budget allows ([13 EMC](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md)). (Half-addressed myth from W4-D1, electronics.stackexchange.com/q/195616.)

## How to simulate / verify
- `python3 tools/verify/math_fourier.py` — square-wave and trapezoid coefficients vs FFT, Gibbs 8.95 %, sinc widths/sidelobes, Parseval, convolution and modulation theorems, pulsed-RF line spacing and nulls, Gaussian TB = 1/(4π), LFM chirp width and LoRa $TB=2^{SF}$, DFT bin spacing. All PASS.
- To see a clock spectrum: generate a trapezoid in numpy, `np.fft.rfft`, plot $20\log_{10}(2|c_n|)$ vs $nf_0$ on log-frequency axes, overlay the envelope.
- SPICE: `.four` gives Fourier coefficients of a transient waveform; `.tran` + FFT in ngspice/LTspice shows clock spectra including real driver edges ([SPICE](../16-simulation-tools/spice-circuit-simulation.md)).

## Open questions / gaps
- The chirp spectrum's exact Fresnel form is only summarised here; derivation is left to the radar domain ([pulse compression](../11-radar/pulsed-radar-and-pulse-compression.md)) and special-functions page.
- Coupling from on-board clock harmonics into the LoRa front end is a layout question for 13-pcb-rf-layout-emc; this page only gives source spectra.

## Sources
1. A. V. Oppenheim, A. S. Willsky, S. H. Nawab, *Signals and Systems*, 2nd ed., Prentice Hall (1997): ch. 3 (Fourier series; §3.4 convergence/Gibbs, §3.5 properties incl. Parseval), ch. 4 (CT Fourier transform; §4.3 properties, §4.4 convolution, §4.5 multiplication), ch. 8 (modulation) (textbook).
2. D. Freeman, *MIT 6.003 Signals and Systems*, Fall 2011, lectures 14–16 (Fourier representations, series, transform), 19–20 (relations among Fourier representations; applications), 23–24 (modulation). https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/pages/lecture-notes/ (lecture notes).
3. R. N. Bracewell, *The Fourier Transform and Its Applications*, 3rd ed., McGraw-Hill (2000): chapters "The basic theorems", "The two domains" (equivalent width, uncertainty), "The discrete Fourier transform and the FFT" (textbook; chapter titles cited — numbering not re-verified).
4. Michigan State University EM Research Group, *EMC Module 3: Signals and Spectra*, §3.3 "Trapezoidal waveforms" (spectral bounds; after C. R. Paul, *Introduction to Electromagnetic Compatibility*, 2nd ed., Wiley 2006, ch. 3). https://www.egr.msu.edu/emrg/sites/default/files/content/module3_signals_and_spectra.pdf (lecture notes).
5. C. R. Paul, *Introduction to Electromagnetic Compatibility*, 2nd ed., Wiley (2006), ch. 3 "Signal spectra — the relationship between the time and frequency domains" (textbook).
6. B. Osgood, *Lecture Notes for EE 261: The Fourier Transform and its Applications*, Stanford University (also AMS 2019 book). http://cau.ac.kr/~mhhgtx/courses/AdvancedMath/references/FTandApplications.pdf ; https://see.stanford.edu/Course/EE261 (lecture notes).
7. J. R. Klauder, A. C. Price, S. Darlington, W. J. Albersheim, "The theory and design of chirp radars," *Bell System Technical Journal* 39(4):745–808 (1960). https://archive.org/details/bstj39-4-745 (peer-reviewed) — chirp spectrum, Fresnel ripples, compression ratio = TB.
8. S. W. Smith, *The Scientist and Engineer's Guide to Digital Signal Processing*, ch. 8 (DFT), ch. 11 (Fourier transform pairs). https://www.dspguide.com (textbook, free online).
