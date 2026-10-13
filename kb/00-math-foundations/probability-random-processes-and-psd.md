---
title: Probability, random processes and power spectral density
domain: 00-math-foundations
slug: probability-random-processes-and-psd
tags: [probability, gaussian, rayleigh, rician, exponential, chi-square, poisson, q-function, erfc, autocorrelation, psd, wiener-khinchin, white-noise, enbw, noise, fading, clt]
prerequisites: [decibels-and-log-units.md, fourier-series-and-transform.md]
related:
  - linear-systems-convolution.md
  - special-functions-bessel-sinc.md
  - ../07-noise-linearity/thermal-noise-and-noise-temperature.md
  - ../07-noise-linearity/shot-and-flicker-noise.md
  - ../07-noise-linearity/phase-noise-and-jitter.md
  - ../09-propagation-link-budget/multipath-fading-doppler.md
  - ../09-propagation-link-budget/link-margin-availability.md
  - ../10-comms-modulation/ber-ebn0-and-shannon.md
  - ../11-radar/detection-theory-cfar.md
  - ../17-test-measurement/spectrum-analyzers.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Probability, random processes and power spectral density

## Questions this page answers
- Why is thermal noise Gaussian?
- Why do noise *powers* add but noise *voltages* don't?
- What does "nV/√Hz" mean, and how do I turn a noise density into an rms voltage?
- What is a power spectral density, and what does the Wiener–Khinchin theorem say?
- What is "white" noise and why is it an idealisation?
- What is equivalent noise bandwidth (ENBW), and why is it not the −3 dB bandwidth?
- What are the Rayleigh and Rician distributions, and how much fade margin does my link need?
- What is the Q-function / erfc, and how does it give bit-error rates?
- Why does averaging make a spectrum-analyser noise trace smoother, and by how much?
- How do I set a detection threshold for a given false-alarm rate?
- Where does shot noise's $2qI$ come from?

## TL;DR
- A zero-mean noise voltage's **rms = standard deviation σ**; its power into R is $\sigma^2/R$. Independent (uncorrelated) sources add **variances (powers)**: $\sigma_{\rm tot}=\sqrt{\sigma_1^2+\sigma_2^2}$ (two equal → ×√2 = +3 dB). Fully correlated sources add amplitudes.
- **PSD** $S(f)$ (W/Hz, V²/Hz) is the Fourier transform of the autocorrelation $R(\tau)=E[x(t)x(t+\tau)]$ (**Wiener–Khinchin**). Through an LTI filter: $S_y=|H|^2S_x$. Power in a band = ∫ PSD.
- **Densities in V/√Hz** are square roots of one-sided PSDs: $v_{\rm rms}=e_n\sqrt{B}$ for flat noise. 50 Ω at 290 K: 0.895 nV/√Hz open-circuit ($\sqrt{4kTR}$); 1 kΩ: 4.0 nV/√Hz. Shot noise: $\sqrt{2qI}$ = 17.9 pA/√Hz at 1 mA.
- **ENBW** $=\frac{1}{|H_{\max}|^2}\int_0^\infty|H(f)|^2df$: single-pole RC = $\frac\pi2f_{3\rm dB}$ (1.571×); Butterworth order n = $\frac{\pi/2n}{\sin(\pi/2n)}f_{3\rm dB}$ (1.111, 1.047, 1.026 for n = 2, 3, 4); Gaussian = 1.065 × −3 dB width.
- Narrowband Gaussian noise: I and Q independent Gaussians; **envelope Rayleigh**, **power exponential**. Signal + noise (or LOS + multipath): envelope **Rician** with K-factor. Rayleigh fading: P(fade deeper than x dB below mean) ≈ $10^{-x/10}$ → 10 dB margin for 10 %, 20 dB for 1 %, 30 dB for 0.1 % outage. With K = 10 dB, 1 % needs only 6.2 dB.
- **Q-function** $Q(x)=\tfrac12\mathrm{erfc}(x/\sqrt2)$ = tail of a unit Gaussian: Q(1) = 0.159, Q(3) = 1.35×10⁻³, Q(4.75) = 10⁻⁶. BPSK: BER = $Q(\sqrt{2E_b/N_0})$ → 10⁻⁵ at 9.6 dB.
- Averaging N independent noise-power readings: relative std $1/\sqrt N$ (χ² with 2N degrees of freedom); 100 averages → ±0.4 dB.
- **CLT**: sums of many small independent effects tend to Gaussian — why thermal noise (many electrons) is Gaussian, and why OFDM/multi-signal composites look Gaussian.

## Intuition (no math)
Noise is the sum of an astronomical number of tiny, independent pushes — electrons jostled by heat. Add up many independent random pushes and you get the bell curve, whatever each individual push looks like (the central limit theorem). That's why receiver noise is modelled as Gaussian.

Why powers add: two independent noise voltages are sometimes in step and sometimes opposed. On average the "in step" and "opposed" cancel in the cross term, so the average of the *square* (power) is the sum of the individual squares. Voltages add like the sides of a right-angled triangle: 3 µV and 4 µV of independent noise make 5 µV, not 7.

A power spectral density answers "how is this noise's power spread over frequency?" White noise is spread evenly, like white light. A filter reshapes it: the PSD after the filter is the PSD before times the filter's *power* response. The total noise you get depends on the filter's "effective width" — the equivalent noise bandwidth — which is always a bit wider than the −3 dB width because real filters have skirts that let extra noise in.

Fading: in a room full of reflections, the received signal is the sum of many echoes with random phases — just like noise, it becomes Gaussian in I and Q, and its strength (envelope) follows a Rayleigh distribution. Deep fades are not rare: 1 % of the time the signal is 20 dB below its average. If there is a strong direct path (a rocket in line of sight to a ground station), fades are much shallower — the Rician case.

## The math

### Level 1 — mean, variance, the bell curve, and adding noise

For a random quantity $X$: mean $\mu=E[X]$, variance $\sigma^2=E[(X-\mu)^2]$, standard deviation $\sigma$. For a zero-mean noise voltage, $\sigma$ **is** the rms voltage.

Gaussian (normal) $X\sim\mathcal N(\mu,\sigma^2)$: 68.3 % of samples within ±1σ, 95.4 % within ±2σ, 99.73 % within ±3σ. Peaks beyond 3.3σ happen 0.1 % of the time and beyond 3.9σ 0.01 % of the time (instantaneous crest ≈ 11.8 dB at 10⁻⁴ — verified).

Adding independent noises: $\sigma_{\rm tot}^2=\sum\sigma_i^2$. In dB: independent equal powers add +3 dB; see the power-sum table on the [decibel page](decibels-and-log-units.md).

Noise density: a datasheet "$e_n=4$ nV/√Hz" means the noise power in 1 Hz corresponds to 4 nV rms; in bandwidth $B$ (flat noise), $v_{\rm rms}=e_n\sqrt B$. Over 1 MHz: $4\times1000=4$ µV rms.

### Level 2 — distributions, random processes, PSD, ENBW

**Distributions used in RF** (verified numerically where marked):

| Distribution | PDF | Mean, variance | Where it appears |
|---|---|---|---|
| Gaussian $\mathcal N(\mu,\sigma^2)$ | $\frac{1}{\sqrt{2\pi}\sigma}e^{-(x-\mu)^2/2\sigma^2}$ | $\mu$, $\sigma^2$ | thermal noise; I and Q of noise; sums (CLT) |
| Uniform $[a,b]$ | $1/(b-a)$ | $(a+b)/2$, $(b-a)^2/12$ | random phase; quantisation error (Δ²/12) |
| Rayleigh (param σ) | $\frac{r}{\sigma^2}e^{-r^2/2\sigma^2}$, $r\ge0$ | $\sigma\sqrt{\pi/2}$, $(2-\pi/2)\sigma^2$; $E[r^2]=2\sigma^2$ | envelope of narrowband noise; multipath without LOS ✓ |
| Rician (ν, σ) | $\frac{r}{\sigma^2}e^{-(r^2+\nu^2)/2\sigma^2}I_0\!\left(\frac{r\nu}{\sigma^2}\right)$ | $E[r^2]=\nu^2+2\sigma^2$ | sine + noise envelope; LOS + multipath; $K=\nu^2/2\sigma^2$ ✓ |
| Exponential (mean $\bar P$) | $\frac1{\bar P}e^{-p/\bar P}$ | $\bar P$, $\bar P^2$ | power of narrowband noise / Rayleigh-faded signal ✓ |
| Chi-square, $k$ d.o.f. (gamma) | $\propto x^{k/2-1}e^{-x/2}$ | $k$, $2k$ | sum of $k$ squared unit Gaussians; averaged noise powers ($k=2N$) ✓ |
| Poisson (rate λT) | $P(n)=\frac{(\lambda T)^n}{n!}e^{-\lambda T}$ | $\lambda T$, $\lambda T$ | photon/electron counts → shot noise ✓ |
| Log-normal | $\ln X$ Gaussian | | large-scale shadowing (dB values Gaussian) |

($I_0$ is the modified Bessel function; see [special functions](special-functions-bessel-sinc.md).)

**Q-function and erfc** [5 §7]:
$$Q(x)=\frac{1}{\sqrt{2\pi}}\int_x^\infty e^{-u^2/2}du=\tfrac12\mathrm{erfc}\!\left(\frac{x}{\sqrt2}\right),\qquad \mathrm{erfc}(z)=\frac{2}{\sqrt\pi}\int_z^\infty e^{-t^2}dt.$$
$P(X>\mu+x\sigma)=Q(x)$. Values: Q(1) = 0.1587, Q(2) = 0.02275, Q(3) = 1.350×10⁻³, Q(4.753) = 10⁻⁶. Useful bound for $x>0$: $Q(x)<\tfrac12e^{-x^2/2}$. BER of antipodal signalling (BPSK) in AWGN $=Q(\sqrt{2E_b/N_0})$: 10⁻³ at 6.8 dB, 10⁻⁵ at 9.6 dB (verified). Non-coherent binary FSK: $\tfrac12e^{-E_b/2N_0}$ → 10⁻³ at 10.9 dB. See [BER and Eb/N0](../10-comms-modulation/ber-ebn0-and-shannon.md).

**Random processes.** A random process $x(t)$ is a random waveform. It is **wide-sense stationary (WSS)** if its mean is constant and its autocorrelation depends only on the lag: $R_x(\tau)=E[x(t)x(t+\tau)]$. It is **ergodic** (in the practical sense) if time averages of one long record equal ensemble averages — what lets you measure noise statistics with one capture [1 ch. 9], [2 ch. 9]. $R_x(0)=E[x^2]$ is the average power.

**Power spectral density and Wiener–Khinchin** [1 ch. 10], [2 ch. 12]:
$$S_x(f)=\int_{-\infty}^\infty R_x(\tau)e^{-j2\pi f\tau}d\tau,\qquad R_x(\tau)=\int S_x(f)e^{j2\pi f\tau}df,\qquad E[x^2]=\int_{-\infty}^{\infty}S_x(f)\,df.$$
Equivalently $S_x(f)=\lim_{T\to\infty}\frac1TE|X_T(f)|^2$ (expected periodogram). Verified for an AR(1) process: Welch-estimated PSD matches $1/|1-ae^{-j2\pi f}|^2$ and the sum of $R[m]$ equals $S(0)$.

**One-sided vs two-sided.** Engineers usually quote one-sided PSDs $G(f)=2S(f)$ for $f\ge0$ so that power $=\int_0^\infty G\,df$. Johnson noise $4kTR$ V²/Hz and shot noise $2qI$ A²/Hz are one-sided; the two-sided values are $2kTR$ and $qI$. Mixing them is a 3 dB error.

**LTI filtering of random processes.** $S_y(f)=|H(f)|^2S_x(f)$ and $R_y=h*h^{-}*R_x$ (with $h^-(t)=h(-t)$) [1 ch. 10]. For white input $S_x=N_0/2$: output power $=\frac{N_0}{2}\int|H|^2df$.

**White noise.** $S(f)=N_0/2$ for all $f$, $R(\tau)=\frac{N_0}{2}\delta(\tau)$: uncorrelated from one instant to the next, infinite total power — an idealisation valid when the noise is flat over the bandwidth of interest (thermal noise is flat to ~THz at room temperature, where $hf\sim kT$). Noise specified as $N_0$ = −174 dBm/Hz (one-sided density at 290 K) is the standard receiver model.

**Equivalent noise bandwidth.**
$$B_n=\frac{1}{|H(f_0)|^2}\int_0^\infty|H(f)|^2df$$
— the width of a rectangular filter with the same peak gain that passes the same white-noise power. Results (verified by integration):

| Filter | $B_n/B_{3\rm dB}$ |
|---|---|
| 1st order (RC) | $\pi/2=1.571$ |
| Butterworth n = 2 | 1.111 |
| Butterworth n = 3 | 1.047 |
| Butterworth n = 4 | 1.026 |
| Butterworth n → ∞ | → 1 |
| Gaussian (typical analyser RBW) | $\sqrt{\pi/(4\ln2)}=1.065$ |
| Single-tuned bandpass (Q) | $\pi/2\times$ its 3 dB bandwidth $f_0/Q$ |

Closed form for Butterworth: $\frac{\pi/2n}{\sin(\pi/2n)}$. Receiver noise-floor calculations should use $B_n$, not $B_{3\rm dB}$; for high-order channel filters the difference is small, for RC-filtered detectors it is 2 dB.

**Narrowband noise and envelopes.** Bandpass Gaussian noise can be written $n(t)=n_I(t)\cos\omega_ct-n_Q(t)\sin\omega_ct$ where $n_I,n_Q$ are independent zero-mean Gaussians each with the same variance $\sigma^2$ as $n(t)$ [3]. The envelope $r=\sqrt{n_I^2+n_Q^2}$ is Rayleigh; the instantaneous power $r^2/2$ (or $|n_I+jn_Q|^2$ in complex-baseband units) is exponential. Adding a sinusoid of amplitude $A$ gives a Rician envelope with $K=A^2/(2\sigma^2)$ — which becomes nearly Gaussian around $A$ for large K. Rice's 1944–45 papers derived these results [3].

### Level 3 — detection, averaging, shot noise, and multipath statistics

**Threshold detection in noise.** With a square-law (power) detector on complex Gaussian noise of mean power $\bar P_n$, the probability that noise alone exceeds threshold $T$ is $P_{fa}=e^{-T/\bar P_n}$. So $T/\bar P_n=\ln(1/P_{fa})$: 13.8 (11.4 dB) for $P_{fa}=10^{-6}$ (verified). This is the core of CFAR radar detection ([detection theory](../11-radar/detection-theory-cfar.md)); with a signal present, the detection probability involves the Rician CDF (Marcum Q-function).

**Averaging.** The average of $N$ independent exponential power samples is gamma-distributed ($\chi^2_{2N}/2N$) with relative standard deviation $1/\sqrt N$ (verified for N = 10, 100). In dB, 100 averages give +0.41/−0.46 dB (1σ). Averaging does **not** lower the noise floor's mean; it reduces its fluctuation, which makes weak CW tones visible. Averaging *log* values biases the mean low by 2.51 dB ([decibels](decibels-and-log-units.md)). Radar non-coherent integration and GNSS/LoRa correlators exploit the same $\sqrt N$ statistics (coherent integration gains $N$ in SNR; non-coherent gains less).

**Shot noise from Poisson arrivals (Campbell's theorem).** Current made of discrete charges $q$ arriving as a Poisson process of rate $\lambda=I/q$ has a white PSD (two-sided) $q^2\lambda=qI$, i.e. one-sided $2qI$ A²/Hz, up to frequencies ~1/(transit time) [4]. Verified by simulating Poisson counts at 10 GS/s for 1 mA: PSD within 0.1 % of $2qI$. At 1 mA: $\sqrt{2qI}=17.9$ pA/√Hz. Details: [shot and flicker noise](../07-noise-linearity/shot-and-flicker-noise.md).

**Johnson–Nyquist noise.** Open-circuit voltage PSD of a resistor: $4kTR$ (one-sided) → 0.895 nV/√Hz for 50 Ω, 4.0 nV/√Hz for 1 kΩ at 290 K; the available power into a matched load is $kTB$ independent of R (verified: −113.98 dBm in 1 MHz). Derivation from thermodynamics: [thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md).

**Partially correlated sources.** For correlation coefficient $\rho$: $\sigma_{\rm tot}^2=\sigma_1^2+\sigma_2^2+2\rho\sigma_1\sigma_2$. $\rho=0$: powers add; $\rho=1$: amplitudes add; $\rho=-1$: cancel. Amplifier noise models with correlated $e_n$ and $i_n$ need this (noise-figure optimum source impedance).

**Fading statistics** (connect to [multipath fading](../09-propagation-link-budget/multipath-fading-doppler.md), [link availability](../09-propagation-link-budget/link-margin-availability.md)). Fade margin $M$ needed for outage probability $P_{\rm out}$, relative to mean received power (computed; Rayleigh closed form $M=-10\log_{10}(-\ln(1-P_{\rm out}))$):

| K-factor | 10 % outage | 1 % | 0.1 % |
|---|---|---|---|
| Rayleigh (K = 0, no LOS) | 9.8 dB | 20.0 dB | 30.0 dB |
| K = 0 dB (Rician) | 8.6 | 18.7 | 28.7 |
| K = 3 dB | 7.0 | 16.2 | 26.1 |
| K = 6 dB | 5.0 | 11.5 | 20.0 |
| K = 10 dB | 3.0 | 6.2 | 9.5 |
| K = 15 dB | 1.6 | 3.0 | 4.3 |

(Here "K = 0 dB" means equal LOS and scattered power; the Rayleigh row is K = 0 linear. Numbers from `scipy.stats.rice`, cross-checked by Monte Carlo.) Diversity (two antennas, frequency hopping, LoRa's spreading does *not* help against flat fading) cuts these margins sharply.

**Cyclostationarity.** Modulated signals are not strictly WSS — their statistics repeat at the symbol rate or carrier. Averaging over a random time origin makes them WSS for PSD purposes; cyclostationary features are used for signal detection/classification in SDR.

**Estimating a PSD.** A single periodogram's variance equals its mean squared (each bin is ~exponential) — it never converges by making the FFT longer. Welch's method averages periodograms of overlapping windowed segments; variance falls as $1/K_{\rm segments}$ (see [FFT and windows](../14-sdr-dsp/fft-spectral-analysis-windows.md)).

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $\sigma_{\rm tot}=\sqrt{\sum\sigma_i^2}$ | independent sources | 3 µV ⊕ 4 µV = 5 µV |
| $v_{\rm rms}=e_n\sqrt{B_n}$ | flat density | 4 nV/√Hz, 1 MHz → 4 µV |
| $\sqrt{4kTR}$ (open circuit) | 290 K | 50 Ω: 0.895 nV/√Hz; 1 kΩ: 4.0 nV/√Hz |
| $kTB$ available | any R | −174 dBm/Hz + 10 log B |
| $\sqrt{2qI}$ | shot noise, $f\ll1/\tau_{\rm transit}$ | 1 mA → 17.9 pA/√Hz |
| $S_y=\lvert H\rvert^2S_x$ | LTI | |
| $B_n=\frac\pi2f_{3\rm dB}$ | RC | 15.9 kHz RC → 25.0 kHz |
| $Q(x)=\frac12\mathrm{erfc}(x/\sqrt2)$ | | Q(4.75) = 10⁻⁶ |
| Rayleigh: $P(\text{fade}>M)\approx10^{-M/10}$ | $M\gtrsim10$ dB | 20 dB ↔ 1 % |
| $T=\bar P_n\ln(1/P_{fa})$ | square-law detector, Gaussian noise | $P_{fa}=10^{-6}$ → +11.4 dB |
| relative std of N-average = $1/\sqrt N$ | independent samples | 100 → ±0.4 dB |

## Worked examples

**1. Noise of a 125 kHz LoRa channel filter vs a simple RC.** A receiver with a steep 125 kHz channel filter (think Butterworth n ≥ 4 or better): $B_n\approx1.03\times125$ kHz → noise floor $-174+10\log(128.8\,\text{kHz})+NF=-122.9+NF$ dBm — negligible difference from using 125 kHz. A power detector filtered by an RC with $f_{3\rm dB}=15.9$ kHz passes noise in $B_n=25.0$ kHz, 2 dB more than its −3 dB width suggests.

**2. Fade margin for a rocket telemetry link.** During ascent a ground station at 3 km typically has strong line of sight plus a ground reflection and airframe-induced scatter; suppose measurements show $K\approx10$ dB. For 99 % availability of each packet: 6.2 dB margin above the *mean* received level. If the rocket tumbles or lands behind terrain and LOS is lost (Rayleigh), the same 99 % would need 20 dB. Design the budget for the phase that matters (e.g. recovery beacon after landing is often non-LOS). See [LoRa rocket telemetry](../15-lora-ism-radios/rocket-telemetry-radio-design.md), [link margin](../09-propagation-link-budget/link-margin-availability.md).

**3. Spectrum-analyser averaging.** A −130 dBm CW spur sits in a displayed noise floor of −125 dBm (RBW 1 kHz). Without averaging the noise trace fluctuates with a standard deviation of 5.6 dB (the spread of $10\log_{10}$ of an exponential variable) and hides the spur; with 100 trace averages (RMS/power averaging) the floor is steady to ±0.4 dB and the spur shows as a +1.2 dB bump ($10\log(1+10^{-0.5})=1.19$ dB). Reducing RBW to 100 Hz lowers the floor 10 dB and makes it obvious.

**4. Radar/beacon detection threshold.** Receiver noise after the matched filter has mean power $\bar P_n$. To get one false alarm per $10^6$ range–Doppler cells, set $T=13.8\bar P_n$ (11.4 dB). A non-fluctuating (Rician) target then needs a single-pulse SNR of 11.2 dB for $P_d=0.5$ and 13.2 dB for $P_d=0.9$ (computed from the non-central χ² / Marcum-Q form; consistent with Albersheim's classic values; see [detection theory](../11-radar/detection-theory-cfar.md)).

**5. Adding amplifier noise sources.** An op-amp with $e_n=4$ nV/√Hz and $i_n=1$ pA/√Hz, fed from a 1 kΩ source (4.0 nV/√Hz thermal): $i_nR_s=1$ nV/√Hz. Total input noise density $\sqrt{4^2+4^2+1^2}=5.74$ nV/√Hz (assuming uncorrelated). Over a 100 kHz ENBW: 1.8 µV rms. The source's own noise is 4.0 of that 5.74 → noise figure $20\log(5.74/4.0)=3.1$ dB.

**6. Shot noise of a detector diode.** A Schottky detector biased at 10 µA: $\sqrt{2qI}=1.79$ pA/√Hz; into its ~2.6 kΩ video resistance ($kT/qI$) that is 4.7 nV/√Hz — comparable to thermal noise of a few kΩ resistor, which is why detector video amplifiers must be low-noise ([detectors](../06-rf-circuits/detectors-and-power-meters.md)).

## Practical notes
- **Detectors matter**: spectrum analysers' "sample", "RMS", "average (log)" and "peak" detectors give different readings on noise; for noise power use RMS detector + power averaging ([spectrum analysers](../17-test-measurement/spectrum-analyzers.md)).
- **SDR noise measurements**: compute power as mean of $|I+jQ|^2$ over many samples; convert to dBm/Hz using the ENBW of your FFT window (e.g. Hann window ENBW = 1.5 bins).
- **Gaussian assumption breaks** for impulsive interference (switching regulators, spark gaps, lightning, other ISM users): tails are heavier than Gaussian and BER predictions from Q-functions become optimistic.
- **Fading statistics need measurement**: K-factor depends strongly on geometry; log RSSI during flights and fit a Rician K (that's the "record everything" ethos in practice).

## Common mistakes & misconceptions
1. **Adding noise voltages linearly** (or dB values) — add powers (variances) for independent sources (forum confusion is common; see [6]).
2. **Using the −3 dB bandwidth for noise** instead of ENBW — up to 2 dB error for low-order filters.
3. **One-sided/two-sided PSD mix-ups** — $N_0$ vs $N_0/2$, $4kTR$ vs $2kTR$: 3 dB errors in SNR and BER.
4. **Treating nV/√Hz as if it scales linearly with bandwidth** — it scales with √B.
5. **Assuming the rms of noise equals its "peak/√2"** — noise has no fixed peak; quote peaks as a probability (e.g. 3.3σ at 10⁻³).
6. **Believing averaging lowers the noise floor** — it lowers the variance, not the mean (except coherent averaging of a repetitive signal, which raises SNR).
7. **Designing fade margin for Rayleigh when LOS exists (or vice versa)** — 20 dB vs 6 dB for 1 % outage.
8. **Using Gaussian tail formulas for impulsive or interference-dominated channels.**
9. **Confusing ergodic with stationary** — a stationary process can fail to be ergodic (e.g. a random but fixed DC offset per unit); a single capture then does not reveal ensemble statistics.
10. **Forgetting that I and Q of narrowband noise each carry the full noise variance** — so complex-baseband SNR definitions must be consistent (per-component vs total).

## How to simulate / verify
- `python3 tools/verify/math_probability_psd.py` — Q-function values and BPSK BER; Rayleigh fade probabilities and envelope moments; Rician fades vs `scipy.stats.rice`; averaging statistics; Poisson variance and **shot-noise PSD = 2qI by simulation**; Wiener–Khinchin for AR(1); ENBW of RC/Butterworth/Gaussian; noise addition; Johnson noise; CLT; Gaussian peak factors; fade-margin table entries; CFAR threshold. All PASS.
- Python: `scipy.stats` (norm, rayleigh, rice, expon, chi2, poisson, gamma), `scipy.special.erfc`, `scipy.signal.welch`.
- SPICE `.noise` analysis integrates $|H|^2$-weighted noise densities from every resistor and device — exactly the ENBW/PSD machinery above.

## Open questions / gaps
- Measured Rician K-factors for rocket-to-ground links at 433/915 MHz are not in the KB; 09-propagation and 15-lora should look for flight data (or Marcus's own logs).
- Marcum Q-function detection curves are deferred to 11-radar.

## Sources
1. A. V. Oppenheim, G. C. Verghese, *Signals, Systems and Inference*, Pearson (2015) / MIT 6.011 course notes: ch. 9 "Random processes", ch. 10 "Power spectral density" (Wiener–Khinchin, LTI filtering of WSS processes); MIT 6.011 Spring 2018 lecture 18 "Power spectral density". https://ocw.mit.edu/courses/6-011-signals-systems-and-inference-spring-2018/ (lecture notes/textbook).
2. A. Papoulis, S. U. Pillai, *Probability, Random Variables and Stochastic Processes*, 4th ed., McGraw-Hill (2002): ch. 4–6 (distributions, functions of random variables), ch. 9 (stochastic processes: stationarity, correlation), ch. 11 "Spectral Representation", ch. 12 "Spectral Estimation" (textbook; Part 2 chapter titles ch. 9 "General Concepts" to ch. 16 confirmed from catalogue/bookseller listings of the 4th ed. via search by W5-S18, 2026-10-13; ch. 4–6 scope as recalled).
3. S. O. Rice, "Mathematical analysis of random noise," *Bell System Technical Journal* 23(3):282–332 (1944) and 24(1):46–156 (1945). https://archive.org/details/bstj23-3-282 ; https://archive.org/details/bstj24-1-46 (peer-reviewed) — shot noise/Campbell's theorem, narrowband noise representation, envelope of sine plus noise (Rician).
4. D. P. Bertsekas, J. N. Tsitsiklis, *Introduction to Probability*, 2nd ed., Athena Scientific (2008) / MIT 6.041: ch. 3 (continuous random variables, normal), ch. 5 (limit theorems, CLT), ch. 6 (Bernoulli and Poisson processes) (textbook/lecture notes).
5. NIST *Digital Library of Mathematical Functions*, ch. 7 "Error functions, Dawson's and Fresnel integrals" (§7.2 definitions of erf/erfc). https://dlmf.nist.gov/7 (standard reference).
6. Forum evidence (anecdotal, for the misconception list): EmbeddedRelated, G. Kirilow, "Here comes the noise!" https://www.embeddedrelated.com/showarticle/1674.php ; industry explainer on RSS noise addition. (forum/blog — anecdotal).
7. J. Jensen (jensign.com), "The concepts of noise bandwidth and cumulative noise." https://www.jensign.com/noisebandwidth/index.html (technical note) — ENBW definition, RC = π/2 × f3dB (re-derived here).
