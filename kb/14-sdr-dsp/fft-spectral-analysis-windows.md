---
title: FFT spectral analysis — DFT, windows, scaling to dBFS/Hz, averaging and spectrograms
domain: 14-sdr-dsp
slug: fft-spectral-analysis-windows
tags: [dft, fft, window, leakage, scalloping, enbw, processing-gain, welch, periodogram, zero-padding, psd, dbfs, noise-density, spectrogram, stft, waterfall, sdr, sub-bin-estimation, jacobsen, quinn, candan, zoom-fft, sliding-dft, snr-estimation, m2m4, ook-spectrum, wavelets]
prerequisites: [../00-math-foundations/fourier-series-and-transform.md, sampling-aliasing-bandpass-sampling.md, iq-complex-baseband.md, ../00-math-foundations/probability-random-processes-and-psd.md, ../00-math-foundations/decibels-and-log-units.md]
related: [digital-filters-fir-iir.md, multirate-dsp-decimation-cic.md, software-demodulation.md, gnu-radio-and-software-stack.md, ../17-test-measurement/spectrum-analyzers.md, ../17-test-measurement/sdr-as-test-equipment.md, ../17-test-measurement/noise-figure-measurement.md, ../07-noise-linearity/sensitivity-and-mds.md, ../10-comms-modulation/matched-filter-detection.md, ../15-lora-ism-radios/lora-phy-css-math.md, ../11-radar/fmcw-radar.md, ../12-phased-arrays/tapering-sidelobe-control.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# FFT spectral analysis — DFT, windows, scaling to dBFS/Hz, averaging and spectrograms

## Questions this page answers
- What exactly does an FFT bin represent, and how wide is it?
- Why does my SDR's noise floor drop when I increase the FFT size, while the signal stays put?
- Which window should I use — Hann, Blackman–Harris, flat-top, Kaiser — and what do ENBW and scalloping loss mean?
- How do I convert FFT output to dBFS, dBFS/Hz, or (with calibration) dBm/Hz?
- Why does a tone's level change by up to ~4 dB depending on its exact frequency?
- Does zero-padding increase resolution?
- Why is a single FFT of noise so "grassy", and how much averaging do I need?
- Why does averaging in dB give a noise floor that's 2.5 dB too low?
- How do I measure the noise figure of my SDR setup with an FFT?
- What FFT length should a spectrogram use to show a LoRa chirp clearly?
- What is the FFT's processing gain for finding weak tones?
- How do I estimate a tone's frequency to a fraction of a bin, and which 3-bin estimator gets closest to the Cramér–Rao bound?
- What are a zoom FFT and a sliding DFT, and when do I use them?
- How do I estimate the SNR of a recorded signal?
- Why does a random-data ASK/OOK spectrum look triangular in dB instead of like a sinc?
- Do wavelets help for RF signal analysis?

## TL;DR
- $N$ samples at $f_s$: bins every $\Delta f = f_s/N$, record length $T = N/f_s$, resolution ≈ $1/T$ (times a window-dependent factor). Complex SDR data gives bins over $-f_s/2\ldots f_s/2$ (`fftshift` puts DC in the middle).
- A finite record is a window; the spectrum is convolved with the window's transform (**leakage**). Windows trade main-lobe width (resolution, ENBW) for sidelobe level (dynamic range). Computed figures (script, $N$ = 1024):

| Window | ENBW (bins) | Scallop loss (dB) | Highest sidelobe (dB) | Use for |
|---|---|---|---|---|
| Rectangular | 1.00 | 3.92 | −13.3 | bin-centred/coherent tones, transients |
| Hann | 1.50 | 1.42 | −31.5 | general default |
| Hamming | 1.36 | 1.75 | −42.7 | near-in sidelobes, moderate range |
| Blackman | 1.73 | 1.10 | −58.1 | ~60 dB range |
| Blackman–Harris (4-term) | 2.00 | 0.83 | −92.0 | spur hunting, >80 dB range |
| Flat-top (Matlab/scipy) | 3.77 | 0.01 | −93.0 | amplitude (tone level) measurement |
| Kaiser β = 8.6 | 1.72 | 1.11 | −63.3 | tunable trade |

- **Scaling (complex data, window $w$, $S_1=\sum w$, $S_2=\sum w^2$)**: tone amplitude $=|X[k]|/S_1$; two-sided PSD $=|X[k]|^2/(f_sS_2)$ (units²/Hz → dBFS/Hz); per-bin noise power $=$ PSD × ENBW, with ENBW(Hz) $=$ NENBW $\cdot f_s/N$. Verified to 0.01 dB.
- **Why the floor moves**: noise per bin ∝ bin width, so doubling $N$ drops the displayed floor by 3.01 dB; a tone's level does not change. Quote noise in dBFS/Hz, not dBFS per bin.
- **Processing gain** for a tone: $10\log_{10}(N/\text{NENBW})$ (script: 4096-pt Hann lifts a −20 dB SNR tone to +14.4 dB in its bin).
- **Statistics**: one periodogram's bins are exponentially distributed — ±5.57 dB standard deviation in dB — and averaging in dB under-reads by 2.51 dB. Averaging $K$ spectra (Welch) cuts the linear std to $1/\sqrt K$; 50 % overlap with Hann gives almost-independent segments.
- **Zero-padding interpolates, it never resolves**: a 0.7-bin tone pair was correctly resolved in 0 of 60 random-phase trials with ×16 padding, and in 60/60 with a 4× longer record.
- Spectrogram of a chirp of rate $k$ (Hz/s): the smear is minimised with a window length $T\approx1/\sqrt{k}$ — about 90 µs for LoRa BW125/SF7.

- **Sub-bin frequency**: complex 3-bin estimators (Jacobsen/Candan, Quinn) reach **1.1–1.55 × the CRB**; Quinn's second is best (1.13× at 20 dB, N = 64). The dB-parabola on a rectangular window is biased by up to 0.17 bin. Zoom FFT: mix, decimate by D, FFT; bin $f_s/(DN)$. Sliding DFT: one complex multiply per sample per bin, damp it in float. SNR from a record: spectral (in-band − floor) or M2M4 (constant-modulus, reliable down to ≈ 0 dB). OOK puts **half its power in the carrier line**; the sinc² sidelobe envelope falls 20 dB/decade, and coarse RBW fills its nulls, which is the "triangular" look. Verified by `tools/verify/s7_interbin_estimators.py`.

Verified by `tools/verify/dsp_windows_fft.py` (all PASS).

## Intuition (no math)
An FFT is a bank of $N$ identical narrow filters placed side by side across the band, each $f_s/N$ wide, all measured at once from one block of samples. Each filter reports how much of the signal falls in its slot.

The filters are not perfect bricks. Their shape is set by how you cut the block out of the endless signal — the **window**. Chopping abruptly (rectangular) gives filters with a sharp top but big "skirts" (sidelobes) that let a strong signal leak into slots far away and hide weak ones. Tapering the block smoothly to zero at its ends (Hann, Blackman–Harris) tames the skirts but makes each filter a bit wider and fatter. A tone that falls between two filters is read low by both — the **scalloping loss** — unless the filters have flat tops (flat-top window), which costs even more width.

Noise is different from a tone: a tone sits in one filter whatever the filter width, but noise fills every filter in proportion to its width. So when you use more, narrower filters (bigger FFT), each one catches less noise and the floor goes down; the tone doesn't. That's why noise should be quoted *per hertz*.

Finally, a single FFT of noise is jumpy — each filter's output is a random number with a big spread. Averaging many FFTs smooths it; averaging their logarithms (dB) is subtly biased low.

## The math

### Level 1 — the DFT and what the bins mean
For $N$ samples $x[n]$ taken at $f_s$:
$$X[k] = \sum_{n=0}^{N-1} w[n]\,x[n]\,e^{-j2\pi kn/N},\qquad k = 0,\ldots,N-1,$$
with window $w[n]$ ($w=1$ is "no window" = rectangular).
- Bin $k$ is at $f_k = k f_s/N$ for $k < N/2$ and at $(k-N)f_s/N$ for $k\ge N/2$ (negative frequencies). After `np.fft.fftshift`, bin index $i$ maps to $(i - N/2)f_s/N$, and to RF $f_c + (i-N/2)f_s/N$ for SDR data.
- Bin spacing $\Delta f = f_s/N$ (Hz); record length $T = N/f_s$ (s). RTL-SDR, 2.4 MS/s, $N$ = 2048: $\Delta f$ = 1.17 kHz, $T$ = 0.853 ms (see [Fourier Example 6](../00-math-foundations/fourier-series-and-transform.md)).
- For real input use `rfft` (bins $0\ldots N/2$); for complex SDR data use the full `fft`.
- Units: $X[k]$ has the units of $x$ times "number of samples" — it must be scaled (Level 2) before it means anything physical.

### Level 1½ — what one bin does, with algebra only
Each bin is a "multiply and add" test. Bin $k$ multiplies the record by a test tone at $f_k$ turning the opposite way, then adds up the $N$ products.
- **Signal adds in amplitude.** If the signal is a complex tone exactly at $f_k$ with amplitude $A$, every product is the same number, so the sum is $|X[k]| = NA$.
- **Noise adds in power.** Noise products point in random directions, so they add like a random walk. The sum has power $N\sigma^2$, against $N^2A^2$ for the tone. The SNR in one bin is therefore $N$ times the SNR of one sample: $+10\log_{10}N$ dB. That is the FFT's processing gain for complex IQ (the [canonical convention](../00-math-foundations/canonical-values-and-conventions.md)).
- **Off-bin tones lose a little.** A tone a fraction δ of a bin away from $f_k$ turns slowly relative to the test tone, so the products no longer line up perfectly. With no window the bin keeps a fraction $\left|\dfrac{\sin\pi\delta}{\pi\delta}\right|$ of the amplitude. This is the "scalloping loss", worst at δ = ½. The leftover energy leaks into other bins, and windows trade this leakage against resolution (Level 2).

*Worked numbers (verified, `tools/verify/s18_level15_numbers.py`).* At 1 MS/s with $N$ = 1000 the bins are 1 kHz apart and the processing gain is 30 dB.
- **On a bin:** a complex tone exactly at 100 kHz gives $|X[100]|$ = 1000·A.
- **Between bins:** a tone at 100.4 kHz (δ = 0.4) reads 2.42 dB low in bin 100. Halfway between bins it would read 3.92 dB low, which is why a flat-top window is used when amplitude matters.

### Level 2 — leakage, window metrics, scaling, statistics
**Leakage.** Windowing multiplies $x$ by $w$, so the DFT samples $X_c(f) * W(f)$: every spectral line is replaced by a copy of the window's transform $W(f)$ centred on it. For the rectangular window $W$ is the Dirichlet kernel ≈ $N\,\mathrm{sinc}(fN/f_s)$ — main lobe ±1 bin to the first nulls, sidelobes at −13.3 dB decaying only 6 dB/octave. A tone exactly on a bin centre lands on the kernel's peak and all other bins sit on its nulls, so it looks "perfect"; any other frequency spreads into every bin.

**Window figures of merit** (definitions after harris [1] and Heinzel et al. [2]):
- *Coherent gain* $\mathrm{CG} = S_1/N$, $S_1 = \sum w[n]$: the factor by which the window lowers a tone's peak.
- *Equivalent noise bandwidth* $\mathrm{NENBW} = N S_2/S_1^2$ bins, $S_2 = \sum w^2[n]$: the width of a rectangular filter with the same peak gain that passes the same white-noise power. In hertz, $\mathrm{ENBW} = \mathrm{NENBW}\cdot f_s/N$.
- *Scalloping loss*: the drop in a tone's apparent level when it lies half-way between bins, $-20\log_{10}|W(\tfrac12\text{ bin})/W(0)|$.
- *Worst-case processing loss* = scalloping loss + $10\log_{10}$NENBW: the worst-case reduction of a tone's SNR per bin relative to an ideal bin-centred rectangular FFT (3.18 dB for Hann).
- *Highest sidelobe* and *sidelobe fall-off rate* (−6 dB/oct for windows with a jump at the ends, e.g. rectangular, Hamming, 4-term Blackman–Harris; −18 dB/oct for Hann and classic Blackman, which go smoothly to zero [1]).
- *3 dB / 6 dB bandwidth*: resolution measures. Two equal tones are resolvable if they are separated by more than about the 6 dB width [1].

Full computed table (script §1, periodic windows, $N$ = 1024; harris' printed values agree to their printed precision except where noted in *Common mistakes* item 8):

| Window | CG | NENBW (bins) | 3 dB BW | 6 dB BW | Scallop (dB) | WCPL (dB) | Highest sidelobe (dB) |
|---|---|---|---|---|---|---|---|
| Rectangular | 1.000 | 1.000 | 0.89 | 1.21 | 3.92 | 3.92 | −13.3 |
| Hann | 0.500 | 1.500 | 1.45 | 2.01 | 1.42 | 3.18 | −31.5 |
| Hamming (0.54/0.46) | 0.540 | 1.363 | 1.30 | 1.82 | 1.75 | 3.10 | −42.7 |
| Blackman (0.42/0.5/0.08) | 0.420 | 1.727 | 1.65 | 2.30 | 1.10 | 3.47 | −58.1 |
| Blackman–Harris 4-term (−92 dB) | 0.359 | 2.004 | 1.91 | 2.67 | 0.83 | 3.85 | −92.0 |
| Flat-top (Matlab `flattopwin` = scipy `flattop`) | 0.216 | 3.770 | 3.73 | 4.59 | 0.01 | 5.77 | −93.0 |
| Kaiser β = 6 | 0.500 | 1.467 | 1.41 | 1.96 | 1.51 | 3.17 | −43.8 |
| Kaiser β = 8.6 | 0.421 | 1.721 | 1.64 | 2.30 | 1.11 | 3.47 | −63.3 |

The Kaiser window $w[n] = I_0\big(\beta\sqrt{1-(2n/N-1)^2}\big)/I_0(\beta)$ is a near-optimal approximation to the prolate spheroidal (maximum-energy-concentration) window, with $\beta$ as a single knob: larger $\beta$ → lower sidelobes, wider main lobe [5], [8].

**Scaling to physical units** (complex baseband data, two-sided spectrum; [2], script §3):
- *Tone amplitude*: a complex tone $Ae^{j2\pi f_0 n/f_s}$ on a bin centre gives $|X[k]| = A S_1$. So the amplitude spectrum is $|X[k]|/S_1$ and the tone power in dBFS is $20\log_{10}(|X[k]|/S_1)$ if $|x|=1$ is full scale. Off-bin, the reading is low by up to the scalloping loss (script §2: exactly −3.92, −1.42, −0.83, −0.01 dB at half-bin for rect/Hann/BH/flat-top).
- *Power spectral density*: $\hat S[k] = |X[k]|^2/(f_s S_2)$ in (full-scale units)²/Hz; $10\log_{10}$ gives **dBFS/Hz**. For white noise its expectation equals the true two-sided density $N_0$ — script §3 recovers −90.00 dBFS/Hz at $N$ = 1024, 2048 and 4096, and `scipy.signal.welch(..., return_onesided=False, scaling='density')` agrees.
- *Per-bin power*: what an amplitude-normalised display ($|X|^2/S_1^2$) shows for noise is $N_0\cdot\mathrm{ENBW}$ — i.e. dBFS/Hz + $10\log_{10}$ENBW(Hz). For Hann at 2.4 MS/s and $N$ = 2048, ENBW = 1757.8 Hz (+32.45 dB): −90 dBFS/Hz shows as −57.55 dBFS per bin; at $N$ = 4096 as −60.56 dBFS.
- *Real data*: use the one-sided PSD $2|X[k]|^2/(f_sS_2)$ for $0<k<N/2$ (not doubled at DC and Nyquist) and amplitude $2|X[k]|/S_1$ (peak) or $\sqrt2|X[k]|/S_1$ (RMS).
- *Parseval check*: $\sum_k\hat S[k]\,\Delta f$ equals the mean power $\overline{|x|^2}$ (script §8: +0.005 dB). Use it to validate any home-made scaling.
- *dBFS convention*: "0 dBFS" must be defined — for SDR IQ data usually a complex sinusoid with $|x| = 1$ (full scale on both I and Q); some tools define it as a real full-scale sine (3 dB different). State it.

**Processing gain.** For a tone of power $P$ in complex white noise of total power $\sigma^2$ (input SNR $P/\sigma^2$), the tone's bin holds $P S_1^2$ and the noise per bin is $\sigma^2 S_2$, so the per-bin SNR is
$$\mathrm{SNR}_{bin} = \frac{P}{\sigma^2}\cdot\frac{S_1^2}{S_2} = \frac{P}{\sigma^2}\cdot\frac{N}{\mathrm{NENBW}}.$$
Script §7: a tone at −20 dB SNR in a 4096-point Hann FFT reads +14.4 dB in its bin (predicted 14.36 dB). This is coherent integration — it only works while the tone stays within one bin for the whole record (stable frequency, no drift over $T$).

**Statistics of the periodogram.** For Gaussian noise each bin $X[k]$ is a complex Gaussian, so $|X[k]|^2$ is exponentially distributed (chi-square with 2 degrees of freedom): its standard deviation equals its mean, however large $N$ is [5 ch. 10], [9 ch. 14]. Consequences (script §4):
- In dB the scatter is ±5.57 dB (std), which is why a single FFT of noise looks like tall grass.
- $E[10\log_{10}|X|^2] = 10\log_{10}E|X|^2 + 10\log_{10}e^{-\gamma}$ with $\gamma$ = 0.5772 (Euler's constant): **log-averaging reads noise 2.51 dB low**, while a CW tone (no fluctuation) reads correctly. Spectrum analysers in "log/video average" mode have the same bias; power (RMS) averaging does not.

**Welch's method** [3]: cut the record into $K$ segments of length $N$ (optionally overlapping), window each, average the $|X|^2$. For independent segments the normalised standard deviation falls as $1/\sqrt K$ (script §5: 0.500, 0.249, 0.125 for $K$ = 4, 16, 64); in dB, roughly $4.34/\sqrt K$ dB for large $K$. Because the window tapers segment ends, 50 % overlap with Hann recovers most of the discarded data: on the same samples, 31 half-overlapped segments gave std 0.185 vs 0.251 for 16 disjoint ones (≈ 29 effective averages from 31). Averaging reduces the *scatter* of the noise floor, not its *mean* — it helps you see a weak tone because the grass gets shorter, giving detectability that improves roughly as $5\log_{10}K$ dB (incoherent integration), versus $10\log_{10}N$ for coherent (longer FFT) integration.

**Zero-padding.** Appending zeros samples the *same* windowed spectrum $X_c * W$ on a finer grid. It gives a smoother picture and better peak-frequency interpolation, but cannot separate features closer than the window's main lobe: resolution is set by $T$. Script §6: two tones 0.7 bin apart with ×16 padding were correctly resolved in 0 % of 60 random relative phases (a naive peak-picker saw two peaks ~20 % of the time, at the wrong frequencies — a trap in itself); a 4× longer record resolved them every time.

### Level 3 — the FFT algorithm, spectrograms, estimation limits
**Why "fast".** Split $x[n]$ into even and odd samples: $X[k] = E[k] + e^{-j2\pi k/N}O[k]$, where $E,O$ are $N/2$-point DFTs, and $X[k+N/2] = E[k] - e^{-j2\pi k/N}O[k]$. Recursing $\log_2N$ times gives $\tfrac N2\log_2N$ complex multiplies instead of $N^2$ (Cooley & Tukey 1965 [4]; mixed-radix and split-radix variants; FFTW and vendor libraries pick the best automatically). A 2048-point complex FFT is ~11 k multiplies — at 2.4 MS/s a display needs only ~1170 FFTs/s, trivial on a laptop; the cost problem in SDR is filtering and resampling at high rates, not the display FFT. For a single frequency (e.g. tone detection), the **Goertzel algorithm** computes one bin with a second-order recursion, cheaper than an FFT when you need fewer than ~$\log_2N$ bins.

**Spectrogram / waterfall (short-time Fourier transform).** Slide a window of length $N$ along the signal with hop $H$, FFT each frame, stack them. Time resolution ≈ $N/f_s$, frequency resolution ≈ NENBW·$f_s/N$; their product is fixed (~1–2), the time–bandwidth uncertainty of [Fourier](../00-math-foundations/fourier-series-and-transform.md). For a **linear chirp** of rate $k$ (Hz/s) the frame sees the frequency move by $kT$ during its length $T$ while its own resolution is $\sim1/T$; the total smear $kT + 1/T$ is minimised at $T = 1/\sqrt{k}$. LoRa BW125/SF7: $k = 125\text{ kHz}/1.024\text{ ms} = 1.22\times10^8$ Hz/s → $T \approx 90\ \mu$s ≈ 90 samples at 1 MS/s (use 64 or 128); SF12: $k = 3.81\times10^6$ Hz/s → $T\approx0.51$ ms. The same logic sets FMCW radar range-FFT lengths ([FMCW](../11-radar/fmcw-radar.md)).

**Frequency estimation beyond the bin grid.** The single-tone maximum-likelihood frequency estimate is the peak of the zero-padded periodogram. Its Cramér–Rao bound is far finer than a bin at high SNR (see [sync](../10-comms-modulation/synchronization-carrier-timing.md) and [estimation theory](../00-math-foundations/estimation-theory-ml-map-crb.md), where the CRB derivation and the threshold effect are Monte-Carlo verified). The cheap 3-bin estimators are compared against that bound in [Beyond the bin grid](#beyond-the-bin-grid--sub-bin-estimators-zoom-fft-sliding-dft-snr-estimation-data-spectra-wavelets) below.

**Dynamic range of an FFT display.** Limited by (a) window sidelobes (e.g. Hann's far sidelobes of a 0 dBFS tone are still above −80 dBFS a few tens of bins away), (b) the ADC's SFDR and noise, (c) floating-point precision (single precision ≈ −140 dB relative), (d) phase noise of the SDR's LO, which puts skirts on strong signals that no window can remove ([phase noise](../07-noise-linearity/phase-noise-and-jitter.md)).

**Non-stationary and cyclostationary signals.** Welch assumes stationarity within the record. Bursty signals (LoRa packets, radar pulses) are better examined with a spectrogram, max-hold, or a burst-triggered FFT; modulation classification uses cyclic spectra — out of scope here.

### Beyond the bin grid — sub-bin estimators, zoom FFT, sliding DFT, SNR estimation, data spectra, wavelets
All numbers here are from `tools/verify/s7_interbin_estimators.py` (≈ 4 s, ALL PASS).

**Sub-bin (inter-bin) frequency estimators.** A tone at $k+\delta$ bins, $|\delta|\le\tfrac12$, puts its peak in bin $k$, and its two neighbours carry the information about $\delta$. For a rectangular window and large $N$ the DFT near the peak is $X[k+m] \propto 1/(\delta-m)$, so the neighbour-to-peak ratios give $\delta$ in closed form:

| Estimator | Formula (window) | Noise-free max bias, N = 64 | RMSE / √CRB at 20 dB per sample |
|---|---|---|---|
| Parabola on dB magnitude | $\delta = \tfrac12\frac{a-c}{a-2b+c}$, $a,b,c$ = dB of bins $k-1,k,k+1$ (rect) | 0.166 bin | 25 (bias-limited) |
| Parabola on dB magnitude | same (Hann) | 0.016 bin | 3.0 |
| Jacobsen [11] | $\delta = \mathrm{Re}\frac{X_{k-1}-X_{k+1}}{2X_k-X_{k-1}-X_{k+1}}$ (rect) | 2.9 × 10⁻⁴ | 1.53 |
| Candan [12] | Jacobsen × $\frac{\tan(\pi/N)}{\pi/N}$ (rect) | 7.3 × 10⁻⁵ | 1.53 |
| Quinn's first [13] | $\alpha_\mp=\mathrm{Re}(X_{k\mp1}/X_k)$, $\delta_1=\frac{\alpha_-}{1-\alpha_-}$, $\delta_2=\frac{-\alpha_+}{1-\alpha_+}$; use $\delta_2$ if both > 0, else $\delta_1$ (rect) | 2.9 × 10⁻⁴ | 1.27 |
| Quinn's second [13] | $\tfrac12(\delta_1+\delta_2)+\tau(\delta_2^2)-\tau(\delta_1^2)$, $\tau(x)=\tfrac14\ln(3x^2+6x+1)-\tfrac{\sqrt6}{24}\ln\frac{x+1-\sqrt{2/3}}{x+1+\sqrt{2/3}}$ (rect) | 2.9 × 10⁻⁴ | **1.13** |
| Grandke [18] (magnitudes) | $\alpha=|X_{k\pm1}|/|X_k|$ on the larger side, $\delta=\pm\frac{2\alpha-1}{\alpha+1}$ (Hann) | 5 × 10⁻⁸ | 1.84 |

The CRB is $\mathrm{var}(\hat\omega)\ge 6/(\rho N(N^2-1))$ (ρ = SNR per complex sample) [estimation theory](../00-math-foundations/estimation-theory-ml-map-crb.md). In bins that is $\sigma_\delta \ge \frac{N}{2\pi}\sqrt{6/(\rho N(N^2-1))}$: 0.0049 bin at N = 64 and 20 dB. The Monte Carlo used a random δ and phase and 4000 trials at each SNR. Three things to take from the table:
- *The log-parabola on a rectangular window is biased* by up to ⅙ bin, so beyond about 10 dB its error does not fall with SNR. On Hann the bias drops tenfold, but at 30 dB it still limits the error to 7.7 × CRB.
- *The complex-ratio estimators are essentially unbiased* and stay within 1.1–1.55 × the CRB from 0 to 30 dB per sample. Quinn's second estimator is closest to the CRB, at 1.13–1.19 ×. Candan's $\tan(\pi/N)/(\pi/N)$ factor removes the residual finite-$N$ bias of Jacobsen (4× smaller at N = 64; it matters at small N and high SNR).
- *Windowed versions trade accuracy for leakage protection*: Grandke on Hann is 1.8 × CRB, because Hann's ENBW (1.5 bins) costs SNR. Use a window when strong neighbours would bias the rectangular estimators.
Below the threshold SNR (integrated SNR ≈ 12–16 dB, [estimation theory](../00-math-foundations/estimation-theory-ml-map-crb.md)) the wrong bin $k$ is picked and every 3-bin method fails together. This is the regime of LoRa CFO estimation from a single chirp at SF7; average the chirps of the preamble first.

**Zoom FFT.** For fine resolution over a small band, mix the band centre to 0 Hz, low-pass and decimate by $D$, then FFT $N_z$ points. The bin is $f_s/(DN_z)$ and the cost is set by the $N_z$-point FFT plus the decimator, not by a $DN_z$-point FFT. Script: 1 MS/s, D = 64, $N_z$ = 4096 gives 3.8 Hz bins, as a 262 144-point FFT would, and the tone was found at 125 038.15 Hz against 125 037.30 Hz true (within one fine bin). The chirp-z transform (Bluestein) evaluates the same arc of frequencies without decimating [5].

**Sliding DFT (SDFT).** To track a few bins sample by sample, update the bin rather than recomputing it:
$$X_k[n] = e^{j2\pi k/N}\big(X_k[n-1] + x[n] - x[n-N]\big),$$
one complex multiply per sample per bin [14]. It matched the direct DFT of every window to 8.7 × 10⁻¹⁴. Its pole sits on the unit circle, so rounding errors accumulate in finite precision. The usual fix is a damping factor $r<1$: $X_k[n] = re^{j2\pi k/N}(X_k[n-1]+x[n]-r^Nx[n-N])$. In float32 with r = 0.9999 it stayed within 4.8 × 10⁻⁵ of its exact damped sum. Uses include tone detectors, the LoRa/FSK tone bank of a streaming receiver, and a running spectrum at one bin. The Goertzel algorithm (above) is the block version.

**SNR estimation from a record.** There are three routes:
- *Spectral (any signal).* Estimate the noise density $\hat N_0$ as the median of empty-band bins. Signal power = in-band power − $\hat N_0 B_{in}$. Script: QPSK band-limited signal, 3.00 dB true SNR in $f_s$, estimated **2.97 dB** (8.20 vs 8.23 dB in the 0.3 $f_s$ occupied band). It needs empty spectrum next to the signal and a flat noise floor.
- *M2M4 moments (constant-modulus signals, no spectrum needed).* With $M_2=\overline{|y|^2}$ and $M_4=\overline{|y|^4}$, a constant-modulus signal in complex Gaussian noise gives $\hat S = \sqrt{2M_2^2-M_4}$, $\hat N = M_2-\hat S$ [15]. For QPSK and 4000 symbols the mean was 0.01 / 10.00 / 20.01 dB for 0 / 10 / 20 dB true (std 0.39 / 0.11 / 0.10 dB). At −5 dB it breaks down (mean −6.2 dB, std 8 dB) because $2M_2^2-M_4$ becomes a small difference of noisy numbers.
- *Data-aided.* After decoding, re-modulate the decided symbols, subtract, and measure the residual. This is the most accurate route, and it is how receivers report EVM and SNR. LoRa chips report SNR from the dechirped peak against the other bins ([15 LoRa](../15-lora-ism-radios/lora-phy-css-math.md)).

**Why a random-data OOK/ASK spectrum looks "triangular" in dB.** On–off keying with rectangular bits of length $T$ (amplitude 0/A) is a mean $A/2$ plus a zero-mean random NRZ. Its PSD is therefore
$$S(f) = \frac{A^2}{4}\delta(f) + \frac{A^2T}{4}\,\mathrm{sinc}^2(fT).$$
**Half the power is in a carrier line** (script: 0.248 vs 0.250), and half is in the continuum (0.250). On a dB axis three effects combine. First, the carrier line sticks up above the continuum by $10\log_{10}(1/(\text{ENBW}\cdot T))$, which grows with FFT length. Second, the sidelobe envelope of $\mathrm{sinc}^2$, averaged over its oscillation, is $1/(2\pi^2f^2T^2)$: −13 / −19 / −25 / −31 dB at 1 / 2 / 4 / 8 bit rates, i.e. **−20 dB per decade**. Third, the nulls at multiples of $1/T$ are seen only when the RBW is much finer than the bit rate. With a 16-point FFT (ENBW ≈ 1.5 $R_b$) the first null reads −4.5 dB instead of −52.6 dB. A carrier spike with smooth flanks falling steeply near the centre and then more slowly looks like a tent, not like the textbook sinc. Pulse shaping (rounded edges) makes the far flanks fall at 40 dB/decade or faster. Measured continuum against theory: −9.94 / −19.37 dB at 0.5 / 1.5 $R_b$ against −9.94 / −19.49 dB.

**Wavelets in one paragraph.** A wavelet transform analyses a signal with scaled copies of one short waveform. Its tiles are narrow in time at high frequencies and narrow in frequency at low frequencies (constant Q), where the STFT uses one fixed tile size. That suits transients and multi-scale features: impulse and click detection, edge localisation, and denoising by thresholding wavelet coefficients (much as a spectral-subtraction gain thresholds STFT cells). It also underlies some compression schemes [16]. For narrowband RF work it rarely helps: modulated carriers are best matched by the STFT, by matched filters or by dechirping, because their structure is a carrier with a known bandwidth, not a multi-scale transient. Reach for wavelets when hunting impulsive interference or analysing radar pulse edges, not for demodulation.


## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $\Delta f = f_s/N$, $T = N/f_s$ | any DFT | 2.4 MS/s, 2048: 1.17 kHz, 0.85 ms |
| ENBW(Hz) = NENBW·$f_s/N$ | noise per bin | Hann 1.5 bins; 2.4 MS/s/2048: 1758 Hz |
| Tone amplitude = $\lvert X\rvert/S_1$ | complex tone, on-bin | off-bin: −scallop loss |
| PSD = $\lvert X\rvert^2/(f_sS_2)$ (two-sided) | complex data | ×2 one-sided for real data |
| dBFS/Hz = dBFS per bin − $10\log_{10}$ENBW(Hz) | noise | −57.55 dBFS/bin → −90 dBFS/Hz |
| Floor drops 3.01 dB per doubling of $N$ | white noise, per-bin display | tone level unchanged |
| Processing gain $10\log_{10}(N/\mathrm{NENBW})$ | stable tone in white noise | 4096 Hann: 34.4 dB |
| Periodogram std 5.57 dB; log-average bias −2.51 dB | Gaussian noise | use power averaging |
| Welch std ≈ $1/\sqrt K$ (linear), ≈ $4.34/\sqrt K$ dB | $K$ independent segments | $K$=100 → ±0.43 dB |
| Overlap 50 % (Hann), 60–75 % (BH, flat-top) | Welch | [2] |
| Chirp spectrogram window $T\approx1/\sqrt{k}$ | linear chirp rate $k$ | LoRa SF7/BW125: 90 µs |
| Zero-padding: interpolation only | always | resolution ≈ 6 dB BW/T |
| Jacobsen/Candan $\delta=\frac{\tan(\pi/N)}{\pi/N}\mathrm{Re}\frac{X_{k-1}-X_{k+1}}{2X_k-X_{k-1}-X_{k+1}}$ | rect window, above threshold | 1.53 × CRB |
| CRB in bins $\sigma_\delta\ge\frac{N}{2\pi}\sqrt{6/(\rho N(N^2-1))}$ | single tone, white noise | N = 64, 20 dB: 0.0049 bin |
| Zoom FFT bin $f_s/(DN_z)$ | mix + decimate by D | 1 MS/s, 64, 4096: 3.8 Hz |
| SDFT $X_k[n]=e^{j2\pi k/N}(X_k[n-1]+x[n]-x[n-N])$ | few bins, streaming | damp with r ≈ 0.9999 |
| M2M4 $\hat S=\sqrt{2M_2^2-M_4}$, $\hat N=M_2-\hat S$ | constant-modulus signal in AWGN | ±0.4 dB at 0 dB, 4000 symbols |
| OOK PSD $\frac{A^2}{4}\delta(f)+\frac{A^2T}{4}\mathrm{sinc}^2(fT)$ | random rectangular bits | sidelobe envelope −20 dB/decade |

## Worked examples

**1 — Reading the noise floor of an SDR in dBFS/Hz.** Airspy-class SDR at $f_s$ = 2.5 MS/s, $N$ = 4096, Hann, power-averaged over 200 frames. The display (amplitude-normalised, 0 dBFS = full-scale complex tone) reads −95.0 dBFS per bin in an empty stretch of band. ENBW = 1.5 × 2.5×10⁶/4096 = 915.5 Hz (29.62 dB). Noise density = −95.0 − 29.62 = **−124.6 dBFS/Hz**. Re-display with $N$ = 1024: the floor rises to −89.0 dBFS per bin but the density is still −124.6 dBFS/Hz.

**2 — Turning that into a noise figure (gain-calibrated method).** At the same gain setting, inject a CW tone from a signal generator at −70.0 dBm (level verified with a power meter, cable loss included); with a flat-top window it reads −40.0 dBFS. Calibration: dBm = dBFS − 30.0 dB. With the antenna replaced by a 50 Ω load (generator disconnected), the noise density of Example 1, −124.6 dBFS/Hz, becomes −154.6 dBm/Hz, so NF = −154.6 + 174 = **19.4 dB**. That is far worse than the tuner's datasheet NF — the signature of too little gain, so that the ADC's own noise dominates ([dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)). Raise the gain by 20 dB and repeat *both* measurements: if the tone now reads −20.0 dBFS (offset −50.0 dB) and the noise −115.0 dBFS/Hz, the density is −165.0 dBm/Hz and NF = **9.0 dB**; keep raising gain until the NF stops improving, then back off for headroom. Rules: the calibration holds only at the gain and frequency where it was made; use a flat-top window for the tone and power (not log) averaging for the noise; any density below −174 dBm/Hz at room temperature means a scaling or calibration error. The more robust method (hot/cold noise source, Y-factor) is on [noise figure measurement](../17-test-measurement/noise-figure-measurement.md).

**3 — Can I see a −130 dBm LoRa-band carrier on an RTL-SDR?** Suppose the chain NF is 6 dB → noise density −168 dBm/Hz. With $N$ = 65 536 at 2.4 MS/s and Hann, ENBW = 1.5 × 36.6 Hz = 54.9 Hz (+17.4 dB) → noise per bin −150.6 dBm. The carrier sits 20.6 dB above that — clearly visible, *if* it is stable within one 37 Hz bin over the 27 ms record. The 1 ppm TCXO wanders far less than that over 27 ms; but a transmitter crystal warming up may drift faster. A LoRa *packet* spreads its energy over 125 kHz, so it appears at −130 − (−168 + 51) = −13 dB below the noise in a 125 kHz band — invisible on the waterfall but decodable by dechirping ([LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md)): dechirping is exactly a matched FFT that re-concentrates the chirp's energy into one bin.

**4 — Choosing a window to find a weak spur next to a strong signal.** A 0 dBFS carrier and a suspected −75 dBFS spur 20 bins away. Hann sidelobes 20 bins out are roughly −31.5 − 18·log₂(20/1.5) ≈ −99 dB — marginal once noise and ADC spurs are added; Hamming's sidelobes only fall 6 dB/oct from −43 dB (≈ −66 dB at 20 bins) and would hide the spur; Blackman–Harris puts all sidelobes below −92 dB. Choose BH (or Kaiser β ≈ 10–12), accept NENBW 2.0.

**5 — Spectrogram settings for watching a rocket's LoRa bursts.** SF9, BW125: symbol 4.1 ms, chirp rate $k$ = 125 kHz/4.096 ms = 3.05×10⁷ Hz/s → optimal $T$ ≈ 181 µs. At 1 MS/s use $N$ = 128–256 with 50 % overlap; the waterfall then shows the diagonal chirps of the preamble cleanly. For a slow survey of the whole 433 MHz ISM band use $N$ = 8192 at 2.4 MS/s (0.29 kHz bins, 3.4 ms frames) with averaging.

## Practical notes
- **SDR apps' "FFT size", "RBW", "averaging" and "window"** are exactly the parameters above. SDR++/SDR#/GQRX show per-bin dBFS; changing FFT size changes the noise floor reading. GNU Radio's `QT GUI Frequency Sink` has an "average" parameter that is an IIR (exponential) average — use power averaging and note its effective $K ≈ 2/\alpha$.
- **Measure tone levels with a flat-top window** (or place the tone on a bin centre by choosing $f_s/N$). Measure noise with Hann/BH and power averaging, then convert to dBFS/Hz.
- **Watch for the DC bin and the band edges** in SDR spectra: the centre spike ([IQ](iq-complex-baseband.md)) and the decimation filter roll-off ([sampling](sampling-aliasing-bandpass-sampling.md)) are not signal.
- **Scaling in libraries**: `numpy.fft` is unnormalised; `scipy.signal.welch` defaults to one-sided density for real data — for complex data pass `return_onesided=False`; MATLAB `pwelch` similar. Check with Parseval.
- **Integer/fixed-point FFTs** in FPGAs scale by 1/2 per stage (block floating point) to avoid overflow; interpret magnitudes accordingly ([FPGA](fpga-for-sdr.md)).
- **ADC testing uses coherent sampling**: choose the test-tone frequency so an integer, prime number of cycles fits the record; then a rectangular window gives zero leakage and SFDR/SNR can be read directly (the IEEE 1241 approach) — see [data converters](../05-analog-electronics/data-converters-adc-dac.md).

## Common mistakes & misconceptions
1. **"The noise floor on my SDR is −60 dBFS."** Meaningless without the bin width. Quote dBFS/Hz, or state $N$, $f_s$ and window.
2. **"A bigger FFT improves my SNR."** It improves per-bin SNR for a *stable tone*; the channel SNR of a modulated signal is unchanged. Integrate power over the signal's bandwidth to measure its SNR.
3. **"Zero-padding increases resolution."** It only interpolates (script §6).
4. **"Averaging lowers the noise floor."** It lowers the *variance* of the floor, not its mean (unless you average in dB, which wrongly lowers it by 2.51 dB).
5. **Forgetting coherent gain / ENBW** when scaling: a Hann-windowed tone reads 6.02 dB low if you divide by $N$ instead of $S_1$; a noise density read without dividing by ENBW is off by $10\log_{10}$ENBW.
6. **"The rectangular window has no effect."** It has the worst leakage (−13 dB sidelobes) whenever the signal isn't bin-centred.
7. **Windowing a pulse/transient shorter than the record** — the window then weights the pulse by wherever it happens to fall; use a rectangular window on a gated segment.
8. **Trusting every printed window table to the last digit.** harris (1978) [1] is the classic reference and its values match direct computation for rectangular and Hann; for Hamming the printed scalloping loss (1.78 dB) differs from the analytic 1.75 dB of the 0.54/0.46 window — 1.78 dB is exactly the scalloping of the "exact" Hamming $a_0$ = 25/46 (ENBW 1.353), while harris' ENBW (1.36) and PSL (−43 dB) are the 0.54 values, so the entry mixes the two variants (W4-D6 recomputation), and printed 3/6 dB widths of Blackman and Blackman–Harris differ from computation by 0.03–0.05 bin (script §1). Nuttall (1981) [7] later corrected and extended several of harris' windows. Compute the metrics for your exact window (the script shows how).
9. **Mixing one-sided and two-sided conventions** (3 dB errors) — decide based on whether the data are real or complex.
10. **Reading a density below −174 dBm/Hz** at room temperature: always a calibration or scaling error.
11. **"Filter by zeroing FFT bins."** The same leakage that limits the rectangular window here (−13 dB sidelobes, 1/(πm) decay) limits the "filter": an off-bin interferer 100 bins past the cut-off leaks enough into the kept bins to be rejected by only ≈ 31 dB, and block processing adds edge discontinuities. Use an FIR with overlap-save instead — [digital filters, mistake 10](digital-filters-fir-iir.md#common-mistakes--misconceptions), `tools/verify/fix_fft_bin_zeroing.py`.

12. **Fitting a parabola to dB magnitudes of a rectangular-window FFT and calling it "sub-bin accuracy".** The fit is biased by up to 0.17 bin, so above about 10 dB SNR the error stops improving. Use Jacobsen/Candan or Quinn on the complex bins, or window the data first.
13. **Expecting an OOK/ASK spectrum to look like the textbook sinc.** The carrier line holds half the power, the dB scale compresses the sidelobes into a −20 dB/decade slope, and an RBW comparable to the bit rate fills the nulls.
14. **Using the M2M4 SNR estimate below ≈ 0 dB.** It becomes very noisy (std 8 dB at −5 dB with 4000 symbols). Use a spectral or data-aided estimate.

## How to simulate / verify
- `python3 tools/verify/dsp_windows_fft.py` (≈ 2 s): window metrics from first principles vs harris; half-bin amplitude errors; PSD scaling and Welch agreement; per-bin floor vs $N$; periodogram statistics (5.57 dB, −2.51 dB); Welch variance and overlap; zero-padding vs record length; processing gain; Parseval. All PASS.
- `python3 tools/verify/s7_interbin_estimators.py` (≈ 4 s, ALL PASS): noise-free bias and Monte-Carlo RMSE vs CRB for parabolic (rect/Hann), Jacobsen, Candan, Quinn 1st/2nd and Grandke estimators; zoom FFT; sliding DFT (exact and damped float32); M2M4 and spectral SNR estimation; random OOK spectrum (carrier line, sinc² continuum, sidelobe envelope, null filling by coarse RBW).
- Minimal correct PSD for SDR IQ data (complex): `f, P = scipy.signal.welch(x, fs=fs, window='hann', nperseg=4096, noverlap=2048, return_onesided=False, scaling='density'); P_dBFS_Hz = 10*np.log10(np.fft.fftshift(P)); f = np.fft.fftshift(f) + fc`.
- Tone level: `A = np.abs(np.fft.fft(x*w))/w.sum()` with `w = scipy.signal.windows.flattop(N, sym=False)`.
- GNU Radio: `QT GUI Frequency Sink` (display), `Log Power FFT` (streaming), `Stream to Vector` + `FFT` + `Complex to Mag^2` + `Integrate` for a hand-rolled power-averaged PSD ([GNU Radio](gnu-radio-and-software-stack.md)).

## Open questions / gaps
- Heinzel, Rüdiger & Schilling (2002) could not be downloaded this session (HTTP 403); their definitions (NENBW, $S_1$, $S_2$) are standard and were re-derived and verified numerically here, but their overlap recommendations are quoted from general knowledge.
- Fall-off rates quoted from harris [1] were not re-computed.
- No measured examples of a specific SDR's dBFS→dBm calibration vs frequency and gain — belongs with [SDR as test equipment](../17-test-measurement/sdr-as-test-equipment.md).

## Sources
1. F. J. harris, "On the use of windows for harmonic analysis with the discrete Fourier transform," *Proc. IEEE* 66(1):51–83 (1978), doi:10.1109/PROC.1978.10837. (peer-reviewed) — window figures of merit and Table 1 values (compared numerically here).
2. G. Heinzel, A. Rüdiger, R. Schilling, "Spectrum and spectral density estimation by the Discrete Fourier transform (DFT), including a comprehensive list of window functions and some new flat-top windows," Max-Planck-Institut für Gravitationsphysik (Albert-Einstein-Institut), technical report (2002), https://holometer.fnal.gov/GH_FFT.pdf and MPG.PuRe item 152164. (technical report) — $S_1$/$S_2$/NENBW scaling, PS vs PSD, overlap. *PDF returned HTTP 403; bibliographic details from search listing.*
3. P. D. Welch, "The use of fast Fourier transform for the estimation of power spectra: a method based on time averaging over short, modified periodograms," *IEEE Trans. Audio Electroacoustics* AU-15(2):70–73 (1967). (peer-reviewed)
4. J. W. Cooley, J. W. Tukey, "An algorithm for the machine calculation of complex Fourier series," *Mathematics of Computation* 19(90):297–301 (1965). (peer-reviewed)
5. A. V. Oppenheim, R. W. Schafer, *Discrete-Time Signal Processing*, 3rd ed., Pearson (2010), ch. 8 (DFT), ch. 9 (FFT algorithms, Goertzel), ch. 10 (Fourier analysis of signals using the DFT: windows incl. Kaiser, STFT/spectrogram, periodogram and its variance, Welch). (textbook)
6. R. G. Lyons, *Understanding Digital Signal Processing*, 3rd ed., Prentice Hall (2011), ch. 3 (DFT leakage, windows, scalloping, processing gain, zero-padding), ch. 4 (FFT). (textbook)
7. A. H. Nuttall, "Some windows with very good sidelobe behavior," *IEEE Trans. Acoustics, Speech, Signal Processing* 29(1):84–91 (1981). (peer-reviewed) — corrections/extensions to harris' windows. *Cited from the literature; not re-read.*
8. J. F. Kaiser, R. W. Schafer, "On the use of the I0-sinh window for spectrum analysis," *IEEE Trans. ASSP* 28(1):105–107 (1980). (peer-reviewed) — Kaiser window for spectrum analysis. *Cited from the literature; not re-read.*
9. J. G. Proakis, D. G. Manolakis, *Digital Signal Processing*, 4th ed., Pearson (2007), ch. 14 (power spectrum estimation: periodogram bias/variance, Bartlett, Welch, Blackman–Tukey). (textbook)
10. M. Lichtman, *PySDR*, chapters "Frequency Domain" and "IQ Sampling" (PSD calculation), https://pysdr.org (online textbook).
11. E. Jacobsen, P. Kootsookos, "Fast, accurate frequency estimators," *IEEE Signal Processing Magazine* 24(3):123–125 (2007), DSP Tips & Tricks. (magazine column; bibliographic details checked via the IEEE Xplore listing; formula re-derived and verified numerically)
12. Ç. Candan, "A method for fine resolution frequency estimation from three DFT samples," *IEEE Signal Processing Letters* 18(6):351–354 (2011). (peer-reviewed) — $\tan(\pi/N)/(\pi/N)$ bias correction. The factor was taken from a forum transcription and then confirmed here by the bias reduction from 2.9 × 10⁻⁴ to 7.3 × 10⁻⁵ bin.
13. B. G. Quinn, "Estimating frequency by interpolation using Fourier coefficients," *IEEE Trans. Signal Processing* 42(5):1264–1268 (1994); and "Estimation of frequency, amplitude, and phase from the DFT of a time series," *IEEE Trans. SP* 45(3):814–817 (1997). (peer-reviewed; cited, not re-read) — formulas re-derived from the $1/(\delta-m)$ model and verified.
14. E. Jacobsen, R. Lyons, "The sliding DFT," *IEEE Signal Processing Magazine* 20(2):74–80 (2003). (magazine; cited, not re-read) — SDFT recursion and damping.
15. D. R. Pauluzzi, N. C. Beaulieu, "A comparison of SNR estimation techniques for the AWGN channel," *IEEE Trans. Communications* 48(10):1681–1691 (2000). (peer-reviewed; cited, not re-read) — M2M4 and data-aided estimators.
16. S. Mallat, *A Wavelet Tour of Signal Processing*, 3rd ed., Academic Press (2009). (textbook; cited) — wavelet time–frequency tiling, thresholding denoising.
17. `tools/verify/s7_interbin_estimators.py` (this KB) — all numbers in "Beyond the bin grid".
18. T. Grandke, "Interpolation algorithms for discrete Fourier transforms of weighted signals," *IEEE Trans. Instrumentation and Measurement* IM-32(2):350–355 (1983). (peer-reviewed; cited, not re-read) — Hann-window magnitude interpolation $\delta=(2\alpha-1)/(\alpha+1)$, verified here to 5 × 10⁻⁸ bin.
