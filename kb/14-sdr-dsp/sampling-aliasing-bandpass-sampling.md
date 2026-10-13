---
title: Sampling, aliasing and bandpass (under-)sampling
domain: 14-sdr-dsp
slug: sampling-aliasing-bandpass-sampling
tags: [sampling, nyquist, shannon, aliasing, anti-alias-filter, nyquist-zones, bandpass-sampling, undersampling, complex-sampling, noise-folding, jitter, zero-order-hold, sdr]
prerequisites: [../00-math-foundations/fourier-series-and-transform.md, ../00-math-foundations/complex-numbers-and-phasors.md, ../00-math-foundations/linear-systems-convolution.md]
related: [iq-complex-baseband.md, fft-spectral-analysis-windows.md, multirate-dsp-decimation-cic.md, digital-filters-fir-iir.md, sdr-hardware-survey.md, ../07-noise-linearity/phase-noise-and-jitter.md, ../07-noise-linearity/dynamic-range-sfdr-blocking.md, ../05-analog-electronics/data-converters-adc-dac.md, ../05-analog-electronics/active-filters.md, ../06-rf-circuits/receiver-architectures.md, ../00-math-foundations/probability-random-processes-and-psd.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Sampling, aliasing and bandpass (under-)sampling

## Questions this page answers
- What does the Nyquist–Shannon sampling theorem actually say, and where does the factor of 2 come from?
- Why does a 1.1 MHz tone show up at 100 kHz when I sample at 1 MS/s?
- What is a Nyquist zone, and why is a signal in the second zone "upside down"?
- Can I sample a 70 MHz IF (or even 433 MHz directly) with an ADC running far below twice the carrier? Which sample rates are allowed?
- Why does an SDR with a 2.4 MS/s sample rate show 2.4 MHz of spectrum, not 1.2 MHz?
- How steep does my anti-alias filter have to be?
- Why does undersampling make my noise floor worse?
- How much clock jitter can I tolerate if I sample a 433 MHz signal directly?
- Why can't I use the whole ±fs/2 span of my SDR's display?
- What sample rate should I pick to receive a 125 kHz LoRa channel?

## TL;DR
- Sampling at rate $f_s$ **replicates the spectrum every $f_s$**. A signal is recoverable iff the replicas do not overlap; for a real low-pass signal of highest frequency $f_{max}$ that means $f_s > 2f_{max}$ (Nyquist). Everything that lands on top of a replica is **aliasing**, and it cannot be removed after sampling.
- Apparent frequency of a real tone: $f_a = |f - f_s\,\mathrm{round}(f/f_s)|$ (folded into $0\ldots f_s/2$). For a complex (IQ) tone: $f_a = ((f + f_s/2) \bmod f_s) - f_s/2$.
- **Complex (IQ) sampling at $f_s$ gives an unambiguous span of $f_s$** ($-f_s/2\ldots+f_s/2$): an RTL-SDR at 2.4 MS/s shows 2.4 MHz. Real sampling at $f_s$ gives $f_s/2$.
- **Bandpass sampling**: a real band $[f_L, f_H]$ of width $B$ can be sampled alias-free iff it lies inside one Nyquist zone, i.e. $\dfrac{2f_H}{n}\le f_s\le\dfrac{2f_L}{n-1}$ for an integer $1\le n\le\lfloor f_H/B\rfloor$. Even zones come out spectrally inverted. The minimum rate $2B$ is only achievable at special positions and is "pathological" — any drift aliases [3].
- Undersampling does **not** reduce noise: wideband noise from every Nyquist zone the analog filter lets through folds on top of the signal — a penalty of ≈ $10\log_{10}$(number of zones) dB.
- Undersampling does **not** relax clock requirements: jitter-limited SNR is $-20\log_{10}(2\pi f_{in}\sigma_t)$ at the *input* frequency, e.g. 100 fs → 71 dB at 433 MHz, 1 ps → 51 dB.
- The anti-alias filter must reach the required rejection by $f_s - f_{pass}$. A brick-wall at $1.5f_c$ for 74 dB would need a 22nd-order Butterworth; 4× oversampling drops that to 4th order — which is why every SDR oversamples and then filters/decimates digitally.
- Practical usable span of an SDR is ≈ 75–85 % of $f_s$ (the rest is the digital decimation filter's transition band) — PySDR's "4/5 rule" [6].

All numbers verified by `tools/verify/dsp_sampling.py` (all PASS).

## Intuition (no math)
Film a spinning wagon wheel at 24 frames per second. If the wheel turns a little less than one spoke-spacing per frame it appears to rotate slowly *backwards*. The camera cannot tell "moved +0.9 spokes" from "moved −0.1 spokes" — both give the same frame. That is aliasing: a sampler only sees the signal at discrete instants, and many different frequencies pass through exactly the same sample values.

Seen from the frequency axis, sampling makes the spectrum repeat like wallpaper, with a period equal to the sample rate. Your signal occupies a strip of the wallpaper; if the strip is narrower than one wallpaper period and sits entirely in one "half-tile", copies never overlap and nothing is lost. The "twice the highest frequency" rule is just the special case where the strip starts at 0 Hz. If your strip is a narrow band sitting high up (an IF, or a whole ISM band), you can use a much smaller tile — as long as the strip doesn't straddle a tile edge. That's bandpass sampling.

Two things do not get cheaper when you sample slowly: **noise** (every tile's worth of noise piles onto the same strip unless you filter it away first) and **timing precision** (the sampler has to "freeze" a fast-moving waveform, so it needs a clock as clean as if it were sampling fast).

An IQ (complex) sampler takes two measurements per instant — the "cosine part" and the "sine part". That lets it tell a wheel turning forwards from one turning backwards, so a complex sampler at $f_s$ covers the full span $-f_s/2$ to $+f_s/2$; a real sampler can't tell $+f$ from $-f$ and covers only $0$ to $f_s/2$. See [IQ and complex baseband](iq-complex-baseband.md).

## The math

### Level 1 — the rules and what each symbol means
- $f_s$ (Hz, or samples per second, S/s): sample rate; $T_s = 1/f_s$ (s): sample period.
- Sampled sequence $x[n] = x(nT_s)$.
- **Nyquist rate** $2f_{max}$: minimum sample rate for a real signal band-limited to $|f| < f_{max}$. **Nyquist frequency** $f_s/2$: highest frequency representable by a given real sampler. (People mix these two up constantly.)
- **Nyquist zones**: the frequency axis cut into strips of width $f_s/2$: zone 1 = $0\ldots f_s/2$, zone 2 = $f_s/2\ldots f_s$, zone $m$ = $(m-1)f_s/2\ldots m f_s/2$. Every zone maps onto zone 1 after sampling; even zones map in reverse (spectral inversion).
- **Alias formula (real)**: a tone at $f$ appears at
  $$f_a = \left|\,f - k f_s\,\right|,\qquad k=\mathrm{round}(f/f_s).$$
  Example: $f_s = 1$ MS/s; 1.1 MHz → 0.1 MHz; 1.9 MHz → 0.1 MHz; 0.6 MHz → 0.4 MHz.
- **Alias formula (complex)**: $e^{j2\pi f t}$ appears at $f_a = ((f + f_s/2)\bmod f_s) - f_s/2$, keeping its sign. With complex sampling, +0.6 MHz at 1 MS/s appears at −0.4 MHz (not +0.4 MHz).
- **Normalised frequency**: DSP formulas use $\nu = f/f_s$ (cycles/sample, range $-\tfrac12\ldots\tfrac12$) or $\omega = 2\pi f/f_s$ (rad/sample, range $-\pi\ldots\pi$). A digital filter designed in $\omega$ scales with $f_s$.

### Level 2 — derivation by spectral replication
**Ideal sampling as multiplication by a comb.** Model the sampler as multiplying $x(t)$ by an impulse train, $x_s(t) = x(t)\sum_n \delta(t-nT_s) = \sum_n x(nT_s)\,\delta(t-nT_s)$. The Fourier transform of a comb of spacing $T_s$ is a comb of spacing $f_s$ and weight $f_s$ (see the transform table in [Fourier](../00-math-foundations/fourier-series-and-transform.md)): $\mathcal{F}\{\sum_n\delta(t-nT_s)\} = f_s\sum_k\delta(f-kf_s)$. Multiplication in time is convolution in frequency, and convolving with a shifted delta just shifts, so
$$X_s(f) = f_s\sum_{k=-\infty}^{\infty} X(f - k f_s).$$
That single line is the whole theory: **the sampled spectrum is the original spectrum plus copies shifted by every integer multiple of $f_s$.** Equivalently the DTFT of $x[n]$ is $X(e^{j\omega}) = f_s\sum_k X\big((\omega/2\pi - k)f_s\big)$, periodic in $\omega$ with period $2\pi$ [1 §4.2].

**When can we undo it?** If $X(f)=0$ for $|f|\ge f_{max}$ and $f_s > 2f_{max}$, the copies centred at $kf_s$ occupy $kf_s\pm f_{max}$ and do not overlap the $k=0$ copy. An ideal low-pass filter with gain $T_s$ and cut-off anywhere in $[f_{max}, f_s - f_{max}]$ isolates the $k=0$ copy and returns $X(f)$ exactly. In the time domain that filter's impulse response is $\mathrm{sinc}(t/T_s)$ with $\mathrm{sinc}(u) = \sin(\pi u)/(\pi u)$, giving the **Whittaker–Shannon interpolation formula**
$$x(t) = \sum_n x[n]\,\mathrm{sinc}\!\left(\frac{t-nT_s}{T_s}\right).$$
(Verified: six random tones below $f_s/2$, 801 samples, reconstructed between samples to $3\times10^{-4}$ relative error.) If $f_s \le 2f_{max}$, the tails of adjacent copies overlap; overlapped energy is indistinguishable from in-band energy and no filter can separate it — aliasing is irreversible. Shannon's 1949 paper states the theorem in this form [5]; Whittaker (1915), Nyquist (1928) and Kotelnikov (1933) had essentially the same result.

**Why "strictly greater than" matters.** A tone exactly at $f_s/2$ sampled at its zero crossings gives all zeros; at its peaks gives $\pm1,\pm1,\ldots$. The amplitude and phase are ambiguous. Real systems keep a margin.

**Anti-alias filtering.** Since aliasing is irreversible, anything above $f_s/2$ (for real sampling) that you don't want must be removed *before* the sampler by an analog **anti-alias filter (AAF)**. The requirement is set by where aliases would land: if you use the band $0\ldots f_p$, the lowest frequency that folds into it is $f_s - f_p$. So the AAF must go from passband at $f_p$ to the required rejection $A$ (dB) at $f_s - f_p$ [4]. For a Butterworth response, $|H(f)|^2 = 1/(1+(f/f_c)^{2N})$, so the order needed is
$$N \ge \frac{\log_{10}(10^{A/10}-1)}{2\log_{10}\big((f_s - f_p)/f_c\big)}.$$
With $f_c = f_p = 40$ MHz, $f_s = 100$ MS/s ($f_s - f_p = 60$ MHz) and $A = 74$ dB (a 12-bit ADC's SNR), $N = 22$ — absurd. Oversample by 4 ($f_s = 400$ MS/s, first alias source at 360 MHz) and $N = 4$. This is the fundamental reason for the SDR architecture "sample fast with a gentle analog filter, then filter sharply and decimate digitally" ([multirate](multirate-dsp-decimation-cic.md)). Required rejection can often be less than the full ADC SNR: only signals that could actually exist in the alias band (strong nearby transmitters) need to be suppressed to below your noise floor.

**Bandpass (under-)sampling.** Suppose the only energy (after an analog bandpass filter) is in $f_L \le |f| \le f_H$, bandwidth $B = f_H - f_L$. A real signal has this band plus its mirror at negative frequency. Replicas of the positive band sit at $[f_L,f_H]+kf_s$, replicas of the negative band at $[-f_H,-f_L]+kf_s$. The positive-band replicas never overlap each other if $f_s \ge B$; the danger is a negative-band replica landing on a positive-band replica. That is avoided exactly when the band sits inside a single Nyquist zone $[(n-1)f_s/2,\;nf_s/2]$:
$$ (n-1)\frac{f_s}{2}\le f_L \quad\text{and}\quad f_H\le n\frac{f_s}{2}\quad\Longrightarrow\quad \frac{2f_H}{n}\le f_s\le\frac{2f_L}{n-1}.$$
For the interval to be non-empty, $2f_H/n \le 2f_L/(n-1)$, i.e. $n\le f_H/B$. So $n = 1, 2, \ldots, \lfloor f_H/B\rfloor$ with $n=1$ being ordinary Nyquist ($f_s\ge2f_H$) [3], [2 §2.3]. The script confirms the inequality equals the "one-zone" criterion on 10 000 random cases and equals a dense multitone folding simulation on 2000 cases.

**Spectral inversion.** In an odd zone ($n$ odd) the band folds down "upright"; in an even zone it folds mirrored (60 MHz → 40 MHz and 70 MHz → 30 MHz at $f_s$ = 100 MS/s). An inverted spectrum is fixed digitally by negating every other sample ($(-1)^n x[n]$, a shift by $f_s/2$) or, in complex baseband, by conjugation.

**Complex (quadrature) sampling.** Sample $x_I(t)$ and $x_Q(t)$ of a complex baseband signal $\tilde x = x_I + jx_Q$, whose spectrum is *not* conjugate-symmetric. There is no mirror band, so the only condition is that the replicas $\tilde X(f - kf_s)$ don't overlap: $f_s \ge B$ where $B$ is the total (two-sided) occupied bandwidth. This is why an IQ SDR at 2.4 MS/s shows 2.4 MHz, and why "sample rate" and "bandwidth" are the same number on an SDR (minus filter roll-off). The total count of real numbers per second is still $2f_s$ — no free lunch.

**Noise folding (the undersampling penalty).** The sampling identity applies to power spectral densities too: a stationary process with PSD $S(f)$ becomes a sequence with PSD $\sum_k S(f-kf_s)$ (see [PSD](../00-math-foundations/probability-random-processes-and-psd.md)). If white noise of density $N_0$ reaches the ADC over a bandwidth covering $K$ Nyquist zones, every zone's noise lands in zone 1 and the density rises to $KN_0$ — an SNR penalty of $10\log_{10}K$ dB relative to a filtered signal. The script checks this directly: dropping samples without filtering keeps the full noise variance, so the density rises by $10\log_{10}8 = 9.0$ dB for $K=8$. Vaughan et al. quantify this as a function of band position [3]. Consequences: (i) undersampling *requires* a real analog bandpass filter around the wanted zone; (ii) the ADC's own thermal/quantisation noise is spread over only $f_s/2$ regardless, so its density at a low $f_s$ is higher (see ADC noise figure in [dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)).

### Level 3 — the real sampler: jitter, aperture, reconstruction, and edge cases
**Clock jitter.** A sample taken at $nT_s + \delta_n$ instead of $nT_s$ has an error $\approx \dot x(nT_s)\,\delta_n$. For $x = A\sin(2\pi f_{in}t)$, the mean-square slope is $(2\pi f_{in}A)^2/2$, so with RMS jitter $\sigma_t$ the error power is $(2\pi f_{in}A\sigma_t)^2/2$ and
$$\mathrm{SNR}_j = -20\log_{10}(2\pi f_{in}\sigma_t)\ \text{dB}.$$
The input frequency $f_{in}$ — *not* $f_s$ and not the aliased frequency — sets the slope. Monte-Carlo in the script: 100 fs gives 87.2 dB at 70 MHz and 71.3 dB at 433.92 MHz; 1 ps gives 51.3 dB at 433.92 MHz; 300 fs gives 50.5 dB at 1575.42 MHz (all within 0.05 dB of the formula). How to get $\sigma_t$ from an oscillator's phase-noise plot, and why the integration band matters, is on [phase noise and jitter](../07-noise-linearity/phase-noise-and-jitter.md).

**Aperture (finite sample-and-hold window).** A track-and-hold that averages over a window $\tau_a$ convolves the input with a rectangle, i.e. multiplies its spectrum by $\mathrm{sinc}(f\tau_a)$ before sampling. With $\tau_a$ in the picosecond range this only matters for multi-GHz inputs; the ADC's specified *full-power analog input bandwidth* (the frequency where the input network has dropped 3 dB) is the practical ceiling for bandpass sampling and is often well below the frequency where jitter kills you. Check it in the datasheet before planning to undersample 433 MHz.

**Reconstruction (DACs).** A real DAC holds each value for $T_s$ (zero-order hold), multiplying the replicated spectrum by $\mathrm{sinc}(f/f_s)$ (magnitude) with a linear phase. At $f_s/2$ the droop is $-20\log_{10}\mathrm{sinc}(0.5) = 3.92$ dB, at $0.4f_s$ 2.42 dB. The images at $kf_s\pm f$ are only partly suppressed by the sinc nulls, so a DAC needs a reconstruction (image) filter, and wideband SDR transmitters either compensate the droop digitally (inverse-sinc FIR) or keep signals near DC. Some RF DACs deliberately use images in higher zones ("mix-mode") — the transmit-side analogue of bandpass sampling.

**Signals are never strictly band-limited.** A finite-duration signal has an infinitely wide spectrum, so some aliasing always occurs; the design goal is aliased energy below the noise floor, not zero. Likewise the theorem's ideal sinc filter is non-causal and infinitely long — practical reconstruction and decimation filters trade length for transition-band width ([FIR/IIR](digital-filters-fir-iir.md)).

**Minimum-rate bandpass sampling is pathological.** At $f_s = 2B$ (possible only when $f_H/B$ is an integer), the band edges touch the zone edges; any clock drift or filter skirt aliases. Real designs add guard bands: widen $[f_L, f_H]$ to the filter's *stopband* edges before applying the rule, then pick $f_s$ in the middle of an allowed window [3].

**Higher-order (non-uniform) sampling.** Kohlenberg's second-order sampling — two interleaved uniform samplers with a chosen offset — reaches the $2B$ rate for any band position [8]. It is the basis of some quadrature-sampling and time-interleaved schemes; its sensitivity to the offset makes it rare in hobby hardware. Time-interleaved ADCs (several ADCs taking turns) suffer the related problem of interleaving spurs from gain/offset/timing mismatch.

**Quantisation and oversampling (link).** An ideal $N$-bit quantiser of a full-scale sine has SNR $6.02N + 1.76$ dB over the Nyquist band (script: 49.7/74.0/86.0 dB for 8/12/14 bits). If the wanted channel $B$ is narrower than the sampled band, filtering removes the out-of-channel noise: **processing gain** $10\log_{10}(f_s/2B)$ for real sampling or $10\log_{10}(f_s/B)$ for complex sampling at $f_s$ (the complex sampler's noise is spread over $f_s$). For 2.4 MS/s complex to 125 kHz: 12.8 dB. This assumes the quantisation noise is white, which needs enough signal/noise activity (dither) — a clean tone into an 8-bit ADC produces harmonically related spurs instead. Device-level ADC theory (ENOB, SINAD, DNL, sigma-delta) is in [data converters](../05-analog-electronics/data-converters-adc-dac.md).

## Design equations & rules of thumb

| Equation / rule | When valid | Typical values |
|---|---|---|
| $f_s > 2f_{max}$ | real low-pass signal | audio 20 kHz → 44.1/48 kS/s |
| $f_s \ge B$ (two-sided occupied BW) | complex IQ sampling | 2.4 MS/s → up to ~2 MHz usable |
| $f_a = \lvert f - f_s\,\mathrm{round}(f/f_s)\rvert$ | real sampling, apparent frequency | 1.1 MHz @ 1 MS/s → 100 kHz |
| $2f_H/n \le f_s \le 2f_L/(n-1)$, $n\le\lfloor f_H/B\rfloor$ | real bandpass sampling | 60–80 MHz: 80–120 or 53.3–60 MS/s |
| zone $m$ even → spectrum inverted | real bandpass sampling | fix with $(-1)^n x[n]$ |
| AAF: rejection $A$ at $f_s - f_p$ | real sampling, band $0\ldots f_p$ | $A$ ≈ desired alias-free dynamic range |
| Noise-folding penalty $10\log_{10}K$ | $K$ zones of white noise reach ADC | 8 zones → 9 dB |
| $\mathrm{SNR}_j = -20\log_{10}(2\pi f_{in}\sigma_t)$ | Gaussian jitter, sine input | 100 fs: 87 dB @ 70 MHz, 71 dB @ 433 MHz |
| $\mathrm{SNR}_q = 6.02N+1.76$ dB | ideal quantiser, full-scale sine, Nyquist band | 8-bit 49.9 dB, 12-bit 74.0 dB |
| Processing gain $10\log_{10}(f_s/B)$ (complex) | white noise, channel filter $B$ | 2.4 MS/s → 125 kHz: 12.8 dB |
| ZOH droop $\mathrm{sinc}(f/f_s)$ | DAC reconstruction | 3.92 dB at $f_s/2$ |
| Usable span ≈ 0.8 $f_s$ | typical SDR decimation filters | 2.4 MS/s → ~1.9–2.0 MHz [6] |

## Worked examples

**1 — The classic 70 MHz IF with 20 MHz of bandwidth (60–80 MHz).** $B = 20$ MHz, $\lfloor f_H/B\rfloor = 4$.
- $n=1$: $f_s\ge160$ MS/s (Nyquist).
- $n=2$: $2\cdot80/2 = 80 \le f_s \le 2\cdot60/1 = 120$ MS/s (band in zone 2, inverted).
- $n=3$: $53.33 \le f_s\le 60$ MS/s (zone 3, upright).
- $n=4$: $40\le f_s\le40$ MS/s — a single point, unusable in practice.
Real filters are not brick-walls. If the IF filter only reaches the needed rejection 5 MHz outside the band, treat the band as 55–85 MHz: now only $n = 1$ ($\ge170$) and $n=2$ ($85\ldots110$ MS/s) survive. A common choice is $f_s = 92.16$ or 100 MS/s (zone 2; 70 MHz appears at 22.16 or 30 MHz, inverted). Script §4.

**2 — Directly sampling the whole 433 MHz ISM band (433.05–434.79 MHz).** $B = 1.74$ MHz, so $\lfloor f_H/B\rfloor = 249$ and in principle $f_s\approx3.49$ MS/s works — but the allowed window there is 0.0 kHz wide. The largest $n$ with a window at least 2 MHz wide is $n = 20$: $43.48 \le f_s \le 45.58$ MS/s. Taking $f_s = 30$ MS/s instead ($n$ = 29 window also contains it): 433.92 MHz lands at 13.92 MHz in zone 29. The script confirms the band fits in one zone. Now the physics bill:
- The analog bandpass filter in front must suppress all other zones (0–1 GHz of FM broadcast, TV, cellular) by the full dynamic range — a SAW filter at 433.92 MHz typically gives 40–50 dB, not 70 ([RF filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md)).
- The ADC's full-power input bandwidth must exceed 435 MHz.
- For 60 dB SNR at 433.92 MHz the total jitter must be $\le 10^{-3}/(2\pi\cdot433.92\times10^6) = 367$ fs; for 70 dB, 116 fs. An ordinary 1 ps crystal oscillator limits you to 51 dB.
Direct RF undersampling works (it is how many radar and RFSoC front ends operate), but for a hobby receiver a tuner + IQ ADC is far cheaper.

**3 — "My SDR is set to 2.4 MS/s — how much can I see?"** An RTL-SDR at 2.4 MS/s delivers complex samples, so the display spans 2.4 MHz, from $f_c - 1.2$ to $f_c + 1.2$ MHz. The outer ~10 % each side is the roll-off of the RTL2832U's internal decimation filter, so ~2.0 MHz is flat. The whole 1.74 MHz 433 MHz ISM band fits in one capture centred at 433.92 MHz. (Details of that chip's internal chain: [NCO/DDC](nco-ddc-duc.md), [hardware survey](sdr-hardware-survey.md).)

**4 — Sample rate for a 125 kHz LoRa channel.** A LoRa BW125 signal occupies ±62.5 kHz about its centre. Minimum complex rate 125 kS/s; LoRa demodulators normally want an integer oversampling of the bandwidth (gr-lora_sdr uses $f_s = \text{os}\cdot BW$ with os = 4 or 8 in its examples), so 500 kS/s or 1 MS/s. Many SDRs cannot run that slowly, or have poor filters at their lowest rate, so the usual chain is: capture at 2.0 MS/s (RTL-SDR accepts any rate in roughly 0.9–3.2 MS/s), offset-tune by a few hundred kHz to dodge the DC spike ([IQ](iq-complex-baseband.md)), shift digitally, low-pass and decimate by 4 to 500 kS/s. Processing gain from 2.0 MS/s to 125 kHz: $10\log_{10}16 = 12.0$ dB — but this does not improve sensitivity relative to the *channel*, it just removes out-of-channel noise the ADC display was showing. The full numeric decimation design is Example 1 of [multirate](multirate-dsp-decimation-cic.md).

**5 — How bad is an unfiltered wideband LNA in front of an undersampling ADC?** An ADC at $f_s = 100$ MS/s with an analog input bandwidth of 500 MHz, preceded by a wideband LNA whose output noise is white to 500 MHz, collects 10 Nyquist zones of LNA noise: the in-band noise density rises by 10 dB compared with a design that bandpass-filters the wanted zone. If the LNA noise was 20 dB above the ADC's own noise, the system noise figure degrades by ≈ 10 dB. Put a filter between the LNA and the ADC.

**6 — Anti-alias filter for a 12-bit audio-rate data logger.** Sampling at 48 kS/s, band of interest 0–20 kHz, want aliases 74 dB down. The first alias source is at $48 - 20 = 28$ kHz, only 1.4× the corner: Butterworth $N = \lceil\log_{10}(10^{7.4}-1)/(2\log_{10}1.4)\rceil = 26$. Instead sample at 192 kS/s (first alias at 172 kHz, ratio 8.6): $N = 4$, then decimate by 4 digitally. Same logic as Example 1 of the script.

## Practical notes
- **Every SDR hides an anti-alias chain.** A zero-IF transceiver (AD936x, LMS7002M) has analog baseband low-pass filters before its ADCs, an ADC running at several times the output rate, and a digital half-band/FIR decimation chain; the output sample rate you set is the end of that chain. Setting a "bandwidth" parameter on such SDRs sets the analog filter; setting it wider than the sample rate lets aliasing through the analog stage (the digital chain usually still protects you). See [multirate](multirate-dsp-decimation-cic.md) and [NCO/DDC](nco-ddc-duc.md).
- **Strong out-of-band signals alias even if you can't see them.** A signal outside the displayed span can fold in through the transition band of the decimation filter; in RTL-SDR land these appear as signals that move the "wrong way" when you retune. The test: retune by $\Delta f$ — a real signal moves by $-\Delta f$ on the display; an alias or image moves by $+\Delta f$ or some other multiple.
- **Harmonics of the sample clock and of USB/switching supplies** appear as fixed spurs; they don't move with retuning of the digital NCO but may with the analog LO. RTL-SDRs show spurs at multiples of the 28.8 MHz reference (anecdotal, widely reported — see [hardware survey](sdr-hardware-survey.md)).
- **Pick $f_s$ in the middle of the allowed bandpass window**, never at an edge, and include oscillator tolerance (±50 ppm on a 100 MS/s clock is ±5 kHz — trivial) and filter skirts.
- **For direct HF sampling** (RX888, Red Pitaya, KiwiSDR-class receivers), a 30 MHz or 60 MHz low-pass filter is the AAF; the ADC sample rate (e.g. 64–130 MS/s) is chosen to leave a big transition band.
- **Timestamp and rate accuracy.** An SDR's sample rate is derived from its reference oscillator: a 1 ppm TCXO means the "2.4 MS/s" is 2.4 MS/s ± 2.4 S/s — negligible for the spectrum, but it drifts symbol timing slowly over long recordings (a LoRa decoder tracks this; a GNSS receiver must).

## Common mistakes & misconceptions
1. **"Nyquist says sample at twice the carrier."** No — twice the *bandwidth* is the true limit for bandpass signals (with the zone condition), and for complex baseband the sample rate need only equal the bandwidth.
2. **"My SDR at 2 MS/s only covers 1 MHz because of Nyquist."** Complex sampling covers ±1 MHz = 2 MHz. The $f_s/2$ limit is for real samples.
3. **"Aliasing can be filtered out afterwards."** Once folded it is indistinguishable from real in-band content. Filter before the sampler (or before each decimation stage in DSP).
4. **"Nyquist frequency" vs "Nyquist rate".** $f_s/2$ is the Nyquist frequency of a sampler; $2f_{max}$ is the Nyquist rate of a signal.
5. **"Undersampling lets me use a slow, cheap ADC and clock."** The ADC's input bandwidth and the clock's jitter must be good enough for the *RF* frequency. A 1 ps clock at 433 MHz caps you at 51 dB SNR.
6. **"Undersampling is free."** It folds noise from every zone that isn't filtered away. Budget $10\log_{10}K$ dB or use a proper bandpass filter.
7. **"$f_s = 2B$ is the bandpass sampling rate."** Only in special positions and with zero margin; use the allowed windows with guard bands.
8. **Forgetting spectral inversion** in even Nyquist zones (demodulated FSK comes out with the bits flipped; SSB turns USB into LSB).
9. **"The display edges are usable."** The last 10–20 % of the span is the decimation filter's roll-off and may contain aliases. Keep signals of interest in the middle 75–80 %.
10. **"A tone exactly at $f_s/2$ is fine."** Its amplitude depends on the sampling phase. Stay below.

## How to simulate / verify
- `python3 tools/verify/dsp_sampling.py` (≈ 1 s): alias formulas vs FFT (real & complex); bandpass-sampling rule vs one-zone criterion and vs dense multitone folding; spectral inversion; 70 MHz IF, 433 MHz ISM and LoRa examples; noise folding; jitter SNR Monte-Carlo; ideal ADC SNR and processing gain; ZOH droop; sinc reconstruction; Butterworth AAF order. All PASS.
- Quick experiment: `x = np.cos(2*np.pi*1.1e6*np.arange(4096)/1e6)` then plot `np.abs(np.fft.rfft(x))` — the peak is at 100 kHz. Sweep the frequency and watch it fold back and forth.
- With an RTL-SDR: tune so a strong FM broadcast station sits 1.3 MHz from centre with a 2.4 MS/s rate. It will appear near the edge; switch to 2.0 MS/s and see whether an alias appears at the other edge (depends on the internal filter's stop-band).
- SPICE/analog: design the AAF with the Butterworth order formula above, then simulate its attenuation at $f_s - f_p$ ([active filters](../05-analog-electronics/active-filters.md)).

## Open questions / gaps
- ADI MT-002 (Kester) could not be re-read this session (fetch timeout); the AAF requirement and Nyquist-zone content here is re-derived and consistent with the tutorial as commonly cited.
- Measured alias rejection of specific SDRs' internal decimation filters (RTL2832U at various rates, AD936x FIR options) is not tabulated — worth measuring with a signal generator (domain 17).
- Second-order (Kohlenberg) sampling is only described, not simulated.

## Sources
1. A. V. Oppenheim, R. W. Schafer, *Discrete-Time Signal Processing*, 3rd ed., Pearson (2010), §4.2 (frequency-domain representation of sampling), §4.3 (reconstruction), §4.6–4.8 (changing sample rate, practical A/D with oversampling and noise shaping). (textbook) — replication derivation, sinc interpolation, oversampling.
2. R. G. Lyons, *Understanding Digital Signal Processing*, 3rd ed., Prentice Hall (2011), ch. 2 (periodic sampling, aliasing, bandpass sampling and spectral inversion), ch. 8 (quadrature signals). (textbook) — bandpass sampling windows, inversion, complex sampling.
3. R. G. Vaughan, N. L. Scott, D. R. White, "The theory of bandpass sampling," *IEEE Trans. Signal Processing* 39(9):1973–1984 (1991), doi:10.1109/78.134430. (peer-reviewed) — allowed rates, pathology of the minimum rate, guard bands, SNR degradation from aliased out-of-band noise.
4. W. Kester, "What the Nyquist Criterion Means to Your Sampled Data System Design," Analog Devices Tutorial MT-002 (2009), https://www.analog.com/media/en/training-seminars/tutorials/MT-002.pdf. (app note) — Nyquist zones, AAF requirements, undersampling. *Cited from search summary; PDF fetch timed out.*
5. C. E. Shannon, "Communication in the presence of noise," *Proc. IRE* 37(1):10–21 (1949). (peer-reviewed) — the sampling theorem as used here.
6. M. Lichtman, *PySDR: A Guide to SDR and DSP using Python*, ch. "IQ Sampling," https://pysdr.org/content/sampling.html (accessed 2026-09-27). (online textbook) — complex sampling, receiver architectures, the "4/5" usable-bandwidth rule of thumb, DC spike/offset tuning.
7. J. G. Proakis, D. G. Manolakis, *Digital Signal Processing*, 4th ed., Pearson (2007), ch. 6 (sampling and reconstruction; sampling of bandpass signals). (textbook) — cross-check of bandpass sampling and reconstruction.
8. A. Kohlenberg, "Exact interpolation of band-limited functions," *J. Applied Physics* 24(12):1432–1436 (1953). (peer-reviewed) — second-order sampling. *Bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from memory of the literature, not re-read.*
9. KB: [phase noise and jitter](../07-noise-linearity/phase-noise-and-jitter.md) (jitter integration, MT-008 method) and [dynamic range / ADC NF](../07-noise-linearity/dynamic-range-sfdr-blocking.md) — consistent numbers (100 fs → 87 dB @ 70 MHz, 71 dB @ 433 MHz).
