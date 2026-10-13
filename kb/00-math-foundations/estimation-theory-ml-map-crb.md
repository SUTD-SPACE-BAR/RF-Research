---
title: Estimation theory — bias, variance, least squares, ML, MAP/MMSE, Fisher information and the Cramér–Rao bound (with frequency, phase and time-delay CRBs)
domain: 00-math-foundations
slug: estimation-theory-ml-map-crb
tags: [estimation, estimator, bias, variance, mse, consistency, efficiency, least-squares, wls, blue, gauss-markov, maximum-likelihood, map, mmse, bayesian, fisher-information, cramer-rao, crb, crlb, nuisance-parameters, rms-bandwidth, frequency-estimation, phase-estimation, time-delay, ranging, pseudorange, carrier-phase, lora-timing, threshold-effect]
prerequisites: [probability-random-processes-and-psd.md, matrices-and-linear-algebra-for-networks.md, fourier-series-and-transform.md]
related:
  - kalman-filter-and-state-estimation.md
  - z-transform-and-discrete-time-systems.md
  - ../10-comms-modulation/synchronization-carrier-timing.md
  - ../10-comms-modulation/matched-filter-detection.md
  - ../11-radar/ambiguity-function-waveforms.md
  - ../11-radar/radar-tracking-monopulse-and-trackers.md
  - ../11-radar/detection-theory-cfar.md
  - ../12-phased-arrays/adaptive-beamforming-doa.md
  - ../21-gnss/gnss-receiver-architecture-acquisition-tracking.md
  - ../21-gnss/gnss-error-sources-dop.md
  - ../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md
level: mixed
confidence: high
last_updated: 2026-10-02
---

# Estimation theory — least squares, ML, MAP/MMSE and the Cramér–Rao bound

## Questions this page answers
- What makes an estimator "good" — bias, variance, MSE, consistency, efficiency?
- Why is the "unbiased" variance estimator (divide by N−1) not the one with the smallest error?
- What is least squares, and when is it the best possible estimator?
- What is maximum likelihood, and how is it related to least squares and to a matched filter?
- What is the difference between MAP and MMSE, and how does a prior change the answer?
- What is the Fisher information and the Cramér–Rao bound (CRB), and how do I derive it?
- What is the best possible accuracy for estimating a tone's frequency or phase in noise?
- What sets the best possible ranging accuracy for a radar, a GNSS receiver or a LoRa timestamp, and what is "rms bandwidth"?
- Why does carrier-phase GNSS reach millimetres when code ranging gives metres?
- Why do estimators suddenly get much worse than the CRB at low SNR (the threshold effect)?
- How well can I estimate vertical velocity from barometer samples alone?

## TL;DR
- An **estimator** is a function of noisy data. Judge it by **bias** $b=E[\hat\theta]-\theta$ and **variance**; their sum $\mathrm{MSE}=b^2+\mathrm{var}$ is what you usually care about. Unbiasedness is not sacred: for Gaussian data the ML variance estimator (÷N) has *lower* MSE than the unbiased one (÷(N−1)) — 0.855× at N = 10 (verified).
- **Least squares** for the linear model $\mathbf z=\mathbf H\boldsymbol\theta+\mathbf w$: $\hat{\boldsymbol\theta}=(\mathbf H^T\mathbf W\mathbf H)^{-1}\mathbf H^T\mathbf W\mathbf z$ with $\mathbf W=\mathbf R^{-1}$ and covariance $(\mathbf H^T\mathbf R^{-1}\mathbf H)^{-1}$. It is the best linear unbiased estimator (Gauss–Markov) and, for Gaussian noise, the ML estimator and efficient. GNSS position + DOP is exactly this ([DOP](../21-gnss/gnss-error-sources-dop.md)).
- **Maximum likelihood** maximises $p(\mathbf z|\boldsymbol\theta)$. For a known waveform in white Gaussian noise it *is* correlation: tone frequency = periodogram peak, delay = matched-filter peak. ML is asymptotically unbiased and efficient (reaches the CRB) above a threshold SNR.
- **Bayesian:** with a prior $p(\theta)$, **MAP** maximises the posterior; **MMSE** is the posterior mean. For Gaussian prior and likelihood they coincide and give the precision-weighted average $\hat\theta=\frac{\theta_0/\sigma_0^2+\sum z_i/\sigma^2}{1/\sigma_0^2+N/\sigma^2}$ — algebraically the **Kalman measurement update**.
- **CRB:** any unbiased estimator has $\mathrm{cov}(\hat{\boldsymbol\theta})\succeq\mathbf J^{-1}$, with Fisher information $\mathbf J=E[\nabla\ln p\,\nabla\ln p^T]$. For complex white noise of variance σ² and mean $\boldsymbol\mu(\boldsymbol\theta)$: $J_{ij}=\frac2{\sigma^2}\mathrm{Re}\sum\frac{\partial\mu^*}{\partial\theta_i}\frac{\partial\mu}{\partial\theta_j}$.
- **Key CRBs** (complex samples, SNR per sample $\rho=A^2/\sigma^2$, N samples; all MC-verified): frequency $\mathrm{var}(\hat\omega)\ge\frac{6}{\rho N(N^2-1)}$ rad²/sample² (∝ N⁻³); phase $\frac{1}{2N\rho}$ referenced to the block centre ($\approx4\times$ that at $n=0$); amplitude $\frac{\sigma^2}{2N}$; **time delay** $\sigma_\tau\ge\frac{1}{2\pi B_{rms}\sqrt{2\,\mathrm{SNR}}}$ with SNR the integrated (matched-filter) SNR and $B_{rms}=B/\sqrt{12}$ for a flat spectrum.
- **Same formula, three systems:** a 10 MHz radar chirp at 20 dB → 0.58 m; GPS C/A code at 45 dB-Hz with a 2 Hz loop in a ±1.023 MHz front end → 1.1 m (a d = 1 DLL achieves 1.7 m); a LoRa SF7/125 kHz 8-chirp preamble → 69 m at sensitivity, 9 m at +10 dB/chip. Using the **carrier phase** multiplies the information by $1+(f_c/B_{rms})^2$ — the reason RTK reaches millimetres (once the integer cycles are resolved).
- **Threshold effect:** below an integrated SNR of roughly 12–16 dB (depending on how many cells are searched), outliers dominate and the MSE departs from the CRB by orders of magnitude (frequency, N = 64: ×663 at −6 dB/sample vs ×1.03 at −3 dB; delay over 512 cells: ×1200 at 10 dB, ×33 at 13 dB, ×1.0 at 16 dB).

## Intuition (no math)
Every measurement in an RF or avionics system is an *estimate*: a range from an echo, a frequency offset from a preamble, an altitude from a pressure sensor, a position from four pseudoranges. Estimation theory answers two questions: what is the best way to turn noisy data into a number, and how good can that number possibly be?

**Averaging is the seed of everything.** Average N independent readings and the noise shrinks by √N. If some readings are noisier than others, give each a weight proportional to 1/variance — the trusted ones count more. That one idea, generalised to many unknowns, is least squares; generalised to "what is most probable given the data", it is maximum likelihood; and when you also have a prior belief ("the rocket is on the pad, altitude is about the site elevation"), mixing the prior and the data in proportion to their confidences is Bayesian estimation — and the Kalman filter is that mixing done recursively, every time step.

**The Cramér–Rao bound is a sharpness argument.** Imagine plotting the probability of the observed data as a function of the unknown parameter (the likelihood). If the likelihood has a sharp peak, a small change of parameter makes the data very improbable, so the data pin the parameter down well. If it is a broad hump, many parameter values fit equally well. The curvature of the log-likelihood at its peak — the Fisher information — measures that sharpness, and its inverse is the smallest variance any unbiased estimator can achieve.

**Why bandwidth sets ranging accuracy.** A delay estimate is like finding the position of an edge. A signal with fast edges (high bandwidth) changes rapidly when shifted, so a small shift produces a large change in the received waveform — high information. A slow, smooth signal barely changes. The relevant measure is the *rms bandwidth* — how far, on average, the signal's energy sits from the centre of its spectrum. That is why a 10 MHz chirp ranges far better than a 125 kHz LoRa chirp, and why tracking the 1.5 GHz **carrier** (whose "edges" are 1.5 GHz cycles) beats tracking the 1 MHz code by a factor of thousands — once you know which cycle you are on.

**Accuracy is not resolution.** Resolution is about separating two targets (≈ 1/bandwidth). Accuracy is how precisely you can locate *one* isolated peak — much finer than the peak width when SNR is high: a 15 m radar range cell can locate a target to 0.5 m.

**And it breaks at low SNR.** The CRB describes small errors around the true peak. When noise is strong enough that a *different* peak somewhere else occasionally wins, errors jump to "completely wrong" — the threshold effect. A tone or delay search over many cells needs enough integrated SNR that noise alone almost never produces the biggest peak — the same physics as a detection threshold.

## The math

### Level 1 — bias, variance, averaging and weighting

Data $z_1,\dots,z_N$, unknown $\theta$. An estimator $\hat\theta(z_1..z_N)$ is any rule.
- Bias $b=E[\hat\theta]-\theta$; variance $\mathrm{var}(\hat\theta)=E[(\hat\theta-E\hat\theta)^2]$; mean-square error
$$\mathrm{MSE}=E[(\hat\theta-\theta)^2]=b^2+\mathrm{var}(\hat\theta).$$
- **Sample mean** of $z_i=\theta+w_i$ with independent noise of std σ: unbiased, variance $\sigma^2/N$ (std $\sigma/\sqrt N$). 25 readings of std 2 → std 0.4 (verified).
- **Weighted mean** when reading $i$ has std $\sigma_i$: $\hat\theta=\frac{\sum z_i/\sigma_i^2}{\sum1/\sigma_i^2}$, variance $\frac{1}{\sum1/\sigma_i^2}$ — precisions (1/variance) add. Two equally good sensors halve the variance; a sensor 3× noisier adds only 1/9 as much information.

### Level 2 — properties, least squares, maximum likelihood, Bayesian estimation

**Estimator properties** [1 ch. 2]. *Unbiased*: $b=0$ for all θ. *Consistent*: $\hat\theta\to\theta$ in probability as $N\to\infty$. *Efficient*: unbiased and attains the CRB. *Asymptotically efficient*: attains it as $N\to\infty$ (ML does, under regularity). Example of the bias–variance trade (verified, N = 10, Gaussian): $\hat\sigma^2_{ML}=\frac1N\sum(z_i-\bar z)^2$ has mean $\frac{N-1}{N}\sigma^2$ (biased) and MSE $\frac{2N-1}{N^2}\sigma^4$; the unbiased $\frac1{N-1}\sum$ has MSE $\frac{2\sigma^4}{N-1}$ — larger. Minimum-MSE estimators are generally biased.

**Linear model and least squares** [1 ch. 4, 6, 8], [6]. Many problems linearise to
$$\mathbf z=\mathbf H\boldsymbol\theta+\mathbf w,\qquad E[\mathbf w]=0,\ \mathrm{cov}(\mathbf w)=\mathbf R,$$
with $\mathbf z$ ($m\times1$) data, $\boldsymbol\theta$ ($n\times1$) unknowns, $\mathbf H$ the known observation matrix. Minimising the weighted squared residual $(\mathbf z-\mathbf H\boldsymbol\theta)^T\mathbf W(\mathbf z-\mathbf H\boldsymbol\theta)$ (set the gradient $-2\mathbf H^T\mathbf W(\mathbf z-\mathbf H\boldsymbol\theta)$ to zero):
$$\hat{\boldsymbol\theta}=(\mathbf H^T\mathbf W\mathbf H)^{-1}\mathbf H^T\mathbf W\mathbf z,\qquad\mathrm{cov}(\hat{\boldsymbol\theta})=(\mathbf H^T\mathbf R^{-1}\mathbf H)^{-1}\ \text{for}\ \mathbf W=\mathbf R^{-1}.$$
*Gauss–Markov theorem*: with $\mathbf W=\mathbf R^{-1}$ this is the **best linear unbiased estimator** (BLUE) for *any* noise distribution with that covariance. With half the samples 4× noisier than the rest, weighting cuts the velocity variance of a line fit to 0.22× that of unweighted LS (verified). Numerically, solve via QR/`lstsq`, not by inverting $\mathbf H^T\mathbf H$ ([matrices](matrices-and-linear-algebra-for-networks.md)). In GNSS, $\mathbf H$ holds line-of-sight unit vectors and a clock column, $\mathbf R=\sigma_{UERE}^2\mathbf I$, and $(\mathbf H^T\mathbf H)^{-1}$ is the DOP matrix.

*Straight-line fit (velocity from altitude samples).* Fit $h_k=h_0+vt_k$ to $N$ samples at rate $f_s$, white noise σ. With $\mathbf H=[\mathbf 1,\ \mathbf t]$:
$$\mathrm{var}(\hat v)=\frac{12\,\sigma^2f_s^2}{N(N^2-1)}\quad(\text{verified by MC}),$$
the same $N^{-3}$ law as frequency estimation below (velocity is the "frequency" of a linear ramp).

**Maximum likelihood** [1 ch. 7]. $\hat{\boldsymbol\theta}_{ML}=\arg\max_{\boldsymbol\theta}p(\mathbf z;\boldsymbol\theta)$. For Gaussian noise $p\propto\exp[-\tfrac12(\mathbf z-\boldsymbol\mu(\boldsymbol\theta))^T\mathbf R^{-1}(\mathbf z-\boldsymbol\mu(\boldsymbol\theta))]$, so ML = nonlinear weighted least squares; for the linear model it is exactly the WLS solution above. Properties: invariance ($\widehat{g(\theta)}_{ML}=g(\hat\theta_{ML})$); asymptotically unbiased, Gaussian and efficient. Signal-processing instances:
- Known waveform $s$ with unknown complex amplitude and delay in white noise: maximise $|\sum_nz[n]s^*(nT-\tau)|$ over τ — the **matched filter / correlator peak** ([matched filter](../10-comms-modulation/matched-filter-detection.md)).
- Complex tone of unknown $A,\omega,\phi$: maximise $|\sum z[n]e^{-j\omega n}|$ — the **periodogram peak**, refined between FFT bins ([synchronisation](../10-comms-modulation/synchronization-carrier-timing.md), [FFT](../14-sdr-dsp/fft-spectral-analysis-windows.md)).

**Bayesian estimation: MAP and MMSE** [1 ch. 10–12], [2 ch. 2]. Treat θ as random with prior $p(\theta)$. Bayes: $p(\theta|\mathbf z)\propto p(\mathbf z|\theta)p(\theta)$.
- **MMSE** estimator (minimises $E[(\hat\theta-\theta)^2]$ averaged over prior and noise) = posterior mean $E[\theta|\mathbf z]$.
- **MAP** = posterior mode. Equal to MMSE for symmetric unimodal posteriors (Gaussian); different for skewed or multimodal ones (e.g. an integer-ambiguity posterior in RTK).

*Gaussian–Gaussian derivation.* Prior $\theta\sim\mathcal N(\theta_0,\sigma_0^2)$, data $z_i=\theta+w_i$, $w_i\sim\mathcal N(0,\sigma^2)$. The log-posterior is $-\frac{(\theta-\theta_0)^2}{2\sigma_0^2}-\sum\frac{(z_i-\theta)^2}{2\sigma^2}+$const, a quadratic in θ: complete the square to get a Gaussian with
$$\frac1{P}=\frac1{\sigma_0^2}+\frac N{\sigma^2},\qquad\hat\theta=P\Big(\frac{\theta_0}{\sigma_0^2}+\frac{\sum z_i}{\sigma^2}\Big)=\theta_0+K(\bar z-\theta_0),\quad K=\frac{\sigma_0^2}{\sigma_0^2+\sigma^2/N},\quad P=(1-K)\sigma_0^2 .$$
The gain form is the scalar **Kalman update** (prior = prediction, $\bar z$ = measurement); see the [Kalman page](kalman-filter-and-state-estimation.md). Verified: the posterior mean's Bayesian MSE equals $P$ (0.963 vs 0.962), better than data-only ML (1.003 vs 1.000). For the vector linear-Gaussian model the same algebra gives $\hat{\boldsymbol\theta}=\boldsymbol\theta_0+\mathbf K(\mathbf z-\mathbf H\boldsymbol\theta_0)$, $\mathbf K=\mathbf P_0\mathbf H^T(\mathbf H\mathbf P_0\mathbf H^T+\mathbf R)^{-1}$, $\mathbf P=(\mathbf I-\mathbf K\mathbf H)\mathbf P_0$.

**Linear MMSE and the orthogonality principle** [1 ch. 12]. If only means and covariances are known (no Gaussian assumption), the best *linear* estimator of θ from $\mathbf z$ is
$$\hat{\boldsymbol\theta}=E[\boldsymbol\theta]+\mathbf C_{\theta z}\mathbf C_{zz}^{-1}(\mathbf z-E[\mathbf z]),\qquad \mathbf P=\mathbf C_{\theta\theta}-\mathbf C_{\theta z}\mathbf C_{zz}^{-1}\mathbf C_{z\theta}.$$
It is characterised by the **orthogonality principle**: the error $\boldsymbol\theta-\hat{\boldsymbol\theta}$ is uncorrelated with every datum. For the linear model $\mathbf C_{\theta z}=\mathbf P_0\mathbf H^T$, $\mathbf C_{zz}=\mathbf H\mathbf P_0\mathbf H^T+\mathbf R$ — the Kalman gain again. For Gaussian data LMMSE = MMSE; otherwise the Kalman filter is still the best *linear* filter (a useful fact when sensor noise is not Gaussian).

**Recursive least squares (RLS).** Processing one measurement at a time with the Gaussian update above, starting from a vague prior ($P_0\to\infty$), reproduces the batch LS answer exactly (verified: RLS of a constant = batch mean, $P=\sigma^2/N$). RLS is a Kalman filter with $\mathbf F=\mathbf I$, $\mathbf Q=0$; adding a "forgetting factor" λ < 1 (discounting old data) is equivalent to adding process noise so the estimate can follow a slowly changing parameter — e.g. tracking a drifting sensor bias or an antenna-tracker pointing offset.

**Which estimator when.**

| Situation | Estimator | Why |
|---|---|---|
| Linear model, known noise covariance, no prior | WLS (= ML if Gaussian) | BLUE; efficient for Gaussian |
| Nonlinear model, many samples, good SNR | ML (iterate: Gauss–Newton / Levenberg–Marquardt) | asymptotically efficient |
| Known waveform in white noise (delay, frequency, phase) | correlator/periodogram peak + interpolation | this *is* ML |
| Useful prior information (pad altitude, previous track) | MAP / MMSE (Gaussian: precision-weighted) | uses all information |
| Parameters evolve in time with known dynamics | Kalman filter (recursive MMSE) | [Kalman page](kalman-filter-and-state-estimation.md) |
| Outliers / heavy tails (multipath, glitches) | robust (Huber, median, gating) | LS is fragile to outliers |

### Level 3 — Fisher information, the CRB and the classic RF bounds

**Scalar CRB derivation** [1 ch. 3], [3]. Let $p(\mathbf z;\theta)$ be the likelihood and $s(\mathbf z;\theta)=\partial\ln p/\partial\theta$ the *score*. Regularity ($\int\partial p/\partial\theta\,d\mathbf z=0$) gives $E[s]=0$. For an unbiased estimator, differentiate $\int\hat\theta\,p\,d\mathbf z=\theta$ with respect to θ: $E[\hat\theta\,s]=1$, hence $E[(\hat\theta-\theta)s]=1$. By Cauchy–Schwarz,
$$1=E[(\hat\theta-\theta)s]^2\le E[(\hat\theta-\theta)^2]\,E[s^2]\;\Rightarrow\;\mathrm{var}(\hat\theta)\ge\frac{1}{J(\theta)},\qquad J=E[s^2]=-E\Big[\frac{\partial^2\ln p}{\partial\theta^2}\Big].$$
Equality holds iff $s=J(\theta)(\hat\theta-\theta)$ — an efficient estimator exists only when the score has this form (it does for the sample mean; it does not exactly for frequency or delay, where ML is only asymptotically efficient). Information from independent data adds: $J_{\rm total}=\sum J_i$.

**Vector CRB and the Fisher information matrix (FIM).** $J_{ij}=E\big[\frac{\partial\ln p}{\partial\theta_i}\frac{\partial\ln p}{\partial\theta_j}\big]$; for any unbiased estimator $\mathrm{cov}(\hat{\boldsymbol\theta})-\mathbf J^{-1}$ is positive semidefinite, so $\mathrm{var}(\hat\theta_i)\ge[\mathbf J^{-1}]_{ii}$. Two Gaussian special cases cover almost all RF work:
- Real Gaussian, known covariance $\mathbf R$, mean $\boldsymbol\mu(\boldsymbol\theta)$: $J_{ij}=\frac{\partial\boldsymbol\mu^T}{\partial\theta_i}\mathbf R^{-1}\frac{\partial\boldsymbol\mu}{\partial\theta_j}$ (for the linear model, $\mathbf J=\mathbf H^T\mathbf R^{-1}\mathbf H$, so WLS is efficient).
- Complex circular white noise, variance σ² per complex sample (σ²/2 per I and Q): $J_{ij}=\frac{2}{\sigma^2}\mathrm{Re}\sum_n\frac{\partial\mu^*[n]}{\partial\theta_i}\frac{\partial\mu[n]}{\partial\theta_j}$.

*Nuisance parameters.* Unknown extras (amplitude, carrier phase, clock bias) can only *reduce* the information about the parameter you want: $[\mathbf J^{-1}]_{11}=(J_{11}-\mathbf J_{12}\mathbf J_{22}^{-1}\mathbf J_{21})^{-1}\ge1/J_{11}$. If the cross-terms vanish (decoupled), there is no penalty. *Transformations:* for $\mathbf g(\boldsymbol\theta)$, $\mathrm{cov}(\hat{\mathbf g})\succeq\frac{\partial\mathbf g}{\partial\boldsymbol\theta}\mathbf J^{-1}\frac{\partial\mathbf g}{\partial\boldsymbol\theta}^T$ — e.g. range $R=c\tau/2$ gives $\sigma_R=\frac c2\sigma_\tau$; angle from $u=\sin\theta$ gives $\sigma_\theta=\sigma_u/\cos\theta$ ([DOA CRB](../12-phased-arrays/adaptive-beamforming-doa.md)).

**CRB for a complex tone** (amplitude $A$, frequency ω rad/sample, phase φ) [4], [1 §3.11]. Model $\mu[n]=Ae^{j(\omega n+\phi)}$, $n=0..N-1$, SNR per sample $\rho=A^2/\sigma^2$. Derivatives: $\partial\mu/\partial A=e^{j\psi}$, $\partial\mu/\partial\omega=jAn\,e^{j\psi}$, $\partial\mu/\partial\phi=jAe^{j\psi}$. Then $J_{AA}=2N/\sigma^2$ and the $A$ cross-terms vanish (real × imaginary), while
$$\begin{pmatrix}J_{\omega\omega}&J_{\omega\phi}\\J_{\phi\omega}&J_{\phi\phi}\end{pmatrix}=\frac{2A^2}{\sigma^2}\begin{pmatrix}\sum n^2&\sum n\\\sum n&N\end{pmatrix},\qquad\det=\Big(\frac{2A^2}{\sigma^2}\Big)^2\frac{N^2(N^2-1)}{12}.$$
Inverting:
$$\mathrm{var}(\hat\omega)\ge\frac{6}{\rho N(N^2-1)},\qquad\mathrm{var}(\hat\phi_{n=0})\ge\frac{2N-1}{\rho N(N+1)},\qquad\mathrm{var}(\hat A)\ge\frac{\sigma^2}{2N}.$$
In Hz at sample rate $f_s$: $\mathrm{var}(\hat f)\ge\frac{6f_s^2}{(2\pi)^2\rho N(N^2-1)}$ — the form on the [synchronisation page](../10-comms-modulation/synchronization-carrier-timing.md). The ω–φ coupling comes from $\sum n\ne0$: if time is measured from the **centre** of the block, $\sum n=0$, the parameters decouple and $\mathrm{var}(\hat\phi_c)\ge\frac{1}{2N\rho}$ — the same as for known frequency; at $n=0$ the bound is ≈4× worse (3.91× at N = 64) because a frequency error rotates the extrapolated phase. All three bounds are reached by the ML estimator at 10 dB per sample, N = 64 (MSE/CRB = 0.96, 0.99, 1.01; verified). **Dual:** frequency accuracy depends on rms *duration* exactly as delay accuracy depends on rms bandwidth: $\sigma_\omega\approx1/(T_{rms}\sqrt{2N\rho})$ with $T_{rms}=N/\sqrt{12}$ samples.

**CRB for time delay — the ranging bound** [1 §3.11], [5], [7]. Model $\mu[n]=a\,s(nT_s-\tau)$, $a$ an unknown complex amplitude (unknown carrier phase), white complex noise σ². Then $\partial\mu/\partial\tau=-a\,s'(nT_s-\tau)$ and
$$J_{\tau\tau}=\frac{2|a|^2}{\sigma^2}\sum_n|s'(nT_s-\tau)|^2=2\,\mathrm{SNR}\,(2\pi B_{rms})^2,\qquad\mathrm{SNR}=\frac{|a|^2\sum|s|^2}{\sigma^2},\qquad B_{rms}^2=\frac{\int f^2|S(f)|^2df}{\int|S(f)|^2df},$$
using Parseval ($s'\leftrightarrow j2\pi fS$). SNR here is the matched-filter output (integrated) SNR. The cross-terms between τ and $a$ are proportional to the spectral centroid $\int f|S|^2df$; they vanish for a spectrum centred on zero (verified for a Gaussian pulse: cross-terms ~10⁻¹⁶), so not knowing the amplitude and carrier phase costs nothing. Hence
$$\boxed{\sigma_\tau\ge\frac{1}{2\pi B_{rms}\sqrt{2\,\mathrm{SNR}}},\qquad\sigma_R=\frac{c}{2}\sigma_\tau\ (\text{two-way}),\quad\sigma_\rho=c\,\sigma_\tau\ (\text{one-way})}$$
— the form used on the [ambiguity-function page](../11-radar/ambiguity-function-waveforms.md). With a power-preserving complex envelope, SNR equals $E/N_0$ of the real passband signal, giving the textbook $\sigma_\tau=1/(2\pi B_{rms}\sqrt{2E/N_0})$; $2E/N_0$ is also the peak SNR of a real (coherent) matched filter. rms bandwidths: flat spectrum of width $B$ → $B/\sqrt{12}$ (LFM chirp, LoRa chirp); Gaussian pulse $e^{-t^2/2\sigma_t^2}$ → $1/(2\sqrt2\pi\sigma_t)$ (verified); rectangular chips (BPSK) → **infinite** for an unlimited band, so the GNSS code bound depends on the receiver front-end bandwidth: ±1.023 MHz around the GPS C/A main lobe gives $B_{rms}$ = 342.7 kHz = 0.335 $R_c$ (computed). This is the formal reason narrow early–late correlators and wide front ends improve code tracking ([GNSS receivers](../21-gnss/gnss-receiver-architecture-acquisition-tracking.md)).

*MC check (Gaussian pulse, σ_t = 4 samples, 512-sample window, random carrier phase):* MSE/CRB = 1.06 at 20 dB and 1.00 at 16 dB integrated SNR.

**Carrier-phase ranging.** If the carrier phase is *not* a nuisance (the receiver tracks it coherently, as a GNSS carrier loop does), the model is $a\,s(t-\tau)e^{-j2\pi f_c\tau}$ with $a$ fixed, and the information becomes
$$J_{\tau\tau}=2\,\mathrm{SNR}\,(2\pi)^2\big(B_{rms}^2+f_c^2\big)\qquad(\text{verified: ratio }1+(f_c/B_{rms})^2).$$
For GPS L1, $(f_c/B_{rms})^2\approx(1575.42/0.3427)^2=2.1\times10^7$: the bound improves by a factor ≈ 4600 in σ. The catch is that the log-likelihood now oscillates with period λ = 19 cm — a forest of nearly equal peaks (integer ambiguity). The CRB describes accuracy *around the right peak*; picking the right peak is a separate (integer) estimation problem — what RTK "fix" does ([RTK/PPP](../21-gnss/rtk-ppp-and-corrections.md)).

**The threshold effect and other bounds.** The CRB is a local, small-error bound. When a search spans many independent cells (FFT bins, range cells), noise occasionally produces a larger peak than the signal — an *outlier* with error of order the search span. Then the MSE rises far above the CRB (verified: frequency estimation, N = 64: MSE/CRB = 1.06 at 0 dB/sample, 1.03 at −3 dB, **663 at −6 dB**, 8900 at −9 dB; delay over 512 cells: 10 dB integrated → 7.9 % outliers, MSE ×1200; 13 dB → 0.17 % outliers, ×33; 16 dB → ×1.0). Rule: the threshold integrated SNR is roughly where noise-only peak probability over the search space becomes small — about the detection threshold for Pfa ≈ 1/(cells), i.e. 12–16 dB for 10²–10³ cells ([detection](../11-radar/detection-theory-cfar.md)). Bounds that capture this (Barankin, Ziv–Zakai) exist [3]. Also: biased estimators (and Bayesian ones using a prior) can have MSE *below* the classical CRB; the Bayesian CRB (Van Trees) adds the prior's information $E[-\partial^2\ln p(\theta)/\partial\theta^2]$.

**When models are wrong.** CRBs assume the model (white noise, known waveform, no multipath). Coloured noise, multipath, clock errors and calibration biases usually dominate real systems; the CRB is then a floor that tells you whether improving SNR can still help.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $\mathrm{MSE}=b^2+\mathrm{var}$ | always | |
| weighted mean: $1/P=\sum1/\sigma_i^2$ | independent | two equal sensors → ½ variance |
| WLS: $(\mathbf H^T\mathbf R^{-1}\mathbf H)^{-1}\mathbf H^T\mathbf R^{-1}\mathbf z$, cov $(\mathbf H^T\mathbf R^{-1}\mathbf H)^{-1}$ | linear model | GNSS fix, calibration fits |
| line-fit slope: $\mathrm{var}(\hat v)=12\sigma^2f_s^2/(N(N^2-1))$ | white noise | 0.5 m, 100 Hz, 0.5 s → 0.49 m/s |
| Gaussian update $K=\sigma_0^2/(\sigma_0^2+\sigma^2/N)$, $P=(1-K)\sigma_0^2$ | linear-Gaussian | prior 5 m + 4×2 m → 0.98 m |
| CRB: $\mathrm{var}\ge1/J$, $J=-E[\partial^2\ln p]$ | unbiased, regular | |
| complex white noise: $J_{ij}=\frac2{\sigma^2}\mathrm{Re}\sum\mu_i'^*\mu_j'$ | σ² per complex sample | |
| tone: $\mathrm{var}(\hat\omega)\ge6/(\rho N(N^2-1))$ | above threshold | N = 64, 10 dB → σ_ω = 1.5×10⁻³ rad/sample |
| tone phase: $1/(2N\rho)$ (centre), $(2N-1)/(\rho N(N+1))$ ($n=0$) | | ≈ 4× at $n=0$ |
| delay: $\sigma_\tau\ge1/(2\pi B_{rms}\sqrt{2\,\mathrm{SNR}})$ | integrated SNR above threshold | |
| $B_{rms}$: flat $B/\sqrt{12}$; Gaussian $1/(2\sqrt2\pi\sigma_t)$; BPSK in ±$R_c$: 0.335 $R_c$ | | GPS C/A 342.7 kHz |
| carrier phase: info × $(1+f_c^2/B_{rms}^2)$ | phase coherent, ambiguity resolved | GPS L1: σ ÷ 4600 |
| threshold: integrated SNR ≳ 12–16 dB | search over 10²–10³ cells | |

## Worked examples

**1. Vertical velocity from a barometer alone.** Baro at 100 Hz with 0.5 m rms white noise. A least-squares line over the last 0.5 s (N = 50): $\sigma_v=\sqrt{12\cdot0.25\cdot10^4/(50\cdot2499)}$ = **0.49 m/s**; over 1 s (N = 100): **0.17 m/s** (both MC-verified). The $N^{-3/2}$ law means doubling the window improves velocity 2.8× — but the window also lags: a line fit's velocity is the average over the window, i.e. delayed by half of it (0.25–0.5 s), and under 10 g boost the true velocity changes 25–50 m/s in that time. This tension is why the accelerometer must be fused in (next page's worked example).

**2. Prior plus data: pad altitude.** Survey/GNSS says the pad is at 100 m ± 5 m (1σ); four baro-derived altitudes at ±2 m each average to $\bar z$. Posterior: $K=25/(25+1)=0.962$, $\hat h=100+0.962(\bar z-100)$, σ = **0.98 m** (data alone 1.00 m; prior alone 5 m) — the prior adds little because the data are much better, exactly as the precisions predict ($1/25+4/4$).

**3. Frequency of a beacon tone.** 64 complex samples at 10 kS/s, 10 dB SNR per sample: $\sigma_\omega=\sqrt{6/(10\cdot64\cdot4095)}=1.51\times10^{-3}$ rad/sample → $\sigma_f=1.51\times10^{-3}\cdot10^4/2\pi$ = **2.4 Hz**, with a 6.4 ms record whose FFT bin is 156 Hz — 65× finer than a bin. The ML search is reliable down to about −3 dB per sample (integrated 15 dB) and collapses by −6 dB.

**4. GNSS pseudorange: code vs carrier.** GPS C/A at C/N₀ = 45 dB-Hz, DLL noise bandwidth $B_n$ = 2 Hz (equivalent averaging time $1/(2B_n)$ = 0.25 s, so $2E/N_0=(C/N_0)/B_n=1.58\times10^4$), ±1.023 MHz front end ($B_{rms}$ = 342.7 kHz): $\sigma_\tau=1/(2\pi\cdot342.7\times10^3\cdot\sqrt{1.58\times10^4})$ = 3.7 ns → **σ_ρ = 1.11 m**. The KB's DLL formula for a d = 1 chip early–late correlator gives **1.70 m** at the same conditions ([GNSS tracking table](../21-gnss/gnss-receiver-architecture-acquisition-tracking.md)) — 1.53× the bound; narrower correlators with wider front ends close the gap. With the carrier phase tracked, the bound shrinks by ≈4600 to ~0.2 mm (in practice mm-level carrier-phase noise, limited by multipath and the ambiguity fix).

**5. LoRa timestamp accuracy (TDoA).** An SF7/125 kHz preamble of 8 up-chirps = 1024 chips, sampled at the chip rate, chirp sweeps the full BW so $B_{rms}=125/\sqrt{12}$ = 36.1 kHz. At the SF7 demodulation limit (≈ −7.5 dB SNR per chip, integrated 22.6 dB): $\sigma_\tau$ = 0.231 µs → **69 m** one-way. At +10 dB per chip: **9.2 m**. Real LoRa TDoA is dominated by gateway clock synchronisation (1 µs of clock error = 300 m) and multipath, not by this bound — but the bound says sub-10 m is physically available at high SNR with 500 kHz bandwidth and well-synchronised receivers. Assumes the CFO has been removed so the 8 chirps add coherently ([LoRa timing](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)).

**6. Radar range accuracy.** A 10 MHz LFM chirp ($B_{rms}$ = 2.89 MHz) at 20 dB integrated SNR: $\sigma_R=\frac c2\cdot\frac{1}{2\pi\cdot2.89\times10^6\cdot\sqrt{200}}$ = **0.58 m** inside a 15 m resolution cell (the [ambiguity page](../11-radar/ambiguity-function-waveforms.md) MC gives 0.54 m). Monopulse angle accuracy is the angular analogue ([radar tracking](../11-radar/radar-tracking-monopulse-and-trackers.md)).

**7. GNSS position as weighted least squares (DOP).** Four satellites — one at the zenith, three at 30° elevation spaced 120° in azimuth. Unknowns (E, N, U, clock); rows of $\mathbf H$ are $[-\hat{\mathbf u}^T,1]$. By symmetry the horizontal block of $\mathbf H^T\mathbf H$ is $1.125\,\mathbf I$ → HDOP $=\sqrt{2/1.125}$ = **4/3**; the vertical–clock block $\begin{pmatrix}1.75&-2.5\\-2.5&4\end{pmatrix}$ (det 0.75) gives VDOP $=\sqrt{4/0.75}$ = **2.31** and TDOP $=\sqrt{7/3}$ = 1.53. With σ_UERE = 3 m, vertical σ = 6.9 m (MC: ratio 1.0006). Vertical is worse because all satellites are above the horizon — the clock and height columns are correlated (the large off-diagonal −2.5). Adding a prior on altitude (baro!) breaks that correlation, which is one reason GNSS/baro fusion helps the vertical channel most ([DOP page](../21-gnss/gnss-error-sources-dop.md)).

## Practical notes
- **Measure σ, don't assume it.** Bound calculations need the actual noise level after filtering; compute it from data (static logs on the pad, noise-only captures) and check whiteness — correlated noise (baro turbulence, quantisation of a slowly varying signal) makes $N$ samples worth far fewer than $N$ independent ones.
- **The CRB is a sanity check on claims.** If a datasheet or paper claims better accuracy than the CRB for its bandwidth and SNR, it is using more information (carrier phase, priors, longer integration) or is wrong.
- **Biases and calibration usually dominate.** CRBs describe random error only. Baro altitude is biased by weather and Mach effects; GNSS by ionosphere and multipath; radar by calibration and glint. Track random and systematic budgets separately, and characterise sensors (bias, scale, thermal drift) before trusting a bound.
- **Interpolate between bins.** A grid search (FFT bins, sample-spaced correlation lags) has its own quantisation error (≈ bin/√12); refine with parabolic interpolation or a local optimiser to reach the CRB.
- **Know your SNR definition.** Per-sample vs integrated; complex (I+Q) vs per-component; $E/N_0$ vs $2E/N_0$. State it with every bound ([matched-filter convention note](../10-comms-modulation/matched-filter-detection.md)).

## Common mistakes & misconceptions
1. **"Unbiased is always better."** MSE is what matters; shrinkage (biased) estimators and Bayesian estimates often win.
2. **Confusing resolution with accuracy** — a 15 m range cell can measure range to 0.5 m at 20 dB SNR.
3. **Applying the CRB below threshold** — at low integrated SNR, outliers dominate and errors are orders of magnitude above the bound.
4. **Using −3 dB bandwidth instead of rms bandwidth** in ranging bounds; for spectra with sharp skirts or chips the difference is large (rectangular chips have unbounded $B_{rms}$ — the front-end filter sets it).
5. **Forgetting nuisance parameters** — unknown clock bias, amplitude or phase can couple to the parameter of interest (e.g. ω and φ at $n=0$) and inflate its bound; decouple by referencing to the block centre or using symmetric spectra.
6. **Treating correlated samples as independent** — oversampling a band-limited noise process does not add information beyond the Nyquist rate.
7. **Inverting $\mathbf H^T\mathbf H$ explicitly** for ill-conditioned fits — use QR/SVD.
8. **Quoting carrier-phase accuracy without the ambiguity problem** — millimetres only after the integer cycle count is right.
9. **Believing the CRB is achievable by any algorithm** — it is a bound; a poor estimator (e.g. integer-bin FFT peak) can be far worse.
10. **Expecting least squares to shrug off outliers** — one multipath-corrupted pseudorange or one baro glitch can drag an LS fit arbitrarily far; gate on residuals (χ² test, see [Kalman NIS](kalman-filter-and-state-estimation.md)) or use a robust cost.
11. **Assuming more sensors always help equally** — information adds as 1/σ²; a sensor three times noisier contributes one ninth as much, and a *biased* sensor can make the fused answer worse.

## How to simulate / verify
- `python3 tools/verify/est_crb.py` (≈ 10 s, **ALL PASS**): DOP for the Example-7 geometry (analytic + MC) and RLS = batch LS; sample mean efficiency; ML vs unbiased variance MSE; line-fit LS and WLS covariance by MC; Gaussian MAP/MMSE = Kalman-gain form; complex tone ML (FFT + bounded refinement) vs CRB for frequency, phase (start and centre) and amplitude; threshold sweep; Gaussian-pulse delay ML vs CRB with random carrier phase, FIM decoupling, outlier fractions; carrier-phase information ratio; GPS C/A $B_{rms}$, pseudorange CRB vs DLL formula; LoRa and radar worked numbers.
- Recipe for any new estimator: (1) write the likelihood; (2) compute the FIM (analytically or by finite differences of $\boldsymbol\mu(\boldsymbol\theta)$); (3) Monte-Carlo the estimator at several SNRs; (4) plot MSE/CRB — it should approach 1 above threshold.

## Open questions / gaps
- Ziv–Zakai / Barankin bounds for the threshold region are named, not derived; threshold SNRs here come from simulation.
- Multipath-limited ranging bounds (two-path CRB) and GNSS narrow-correlator/multipath envelopes are not covered — candidates for 21-gnss.
- The KB's [matched-filter page](../10-comms-modulation/matched-filter-detection.md) and [ambiguity page](../11-radar/ambiguity-function-waveforms.md) state the complex-baseband SNR convention differently (2E/N₀ vs E/N₀); this page uses the power-preserving envelope (complex SNR = E/N₀, coherent real matched-filter peak = 2E/N₀). Flagged for the consistency audit.

## Sources
1. S. M. Kay, *Fundamentals of Statistical Signal Processing, Vol. I: Estimation Theory*, Prentice Hall (1993): ch. 2 (MVU, bias), ch. 3 (CRLB, FIM, general Gaussian CRLB, sinusoidal parameter and range/delay examples), ch. 4 (linear model), ch. 6 (BLUE), ch. 7 (MLE), ch. 8 (least squares), ch. 10–12 (Bayesian, MMSE/MAP, LMMSE), ch. 13 (Kalman). (textbook; chapter structure as recalled — standard)
2. Y. Bar-Shalom, X. R. Li, T. Kirubarajan, *Estimation with Applications to Tracking and Navigation*, Wiley (2001): ch. 2 (estimation basics, MAP/MMSE/LS/ML, CRLB), ch. 3 (linear estimation, static case). (textbook; recalled)
3. H. L. Van Trees, *Detection, Estimation, and Modulation Theory, Part I*, Wiley (1968/2001): §2.4 (CRB, Bayesian bound), threshold behaviour and Barankin/Ziv–Zakai discussion; with K. L. Bell (eds.), *Bayesian Bounds for Parameter Estimation and Nonlinear Filtering/Tracking*, Wiley-IEEE (2007). (textbooks; recalled)
4. D. C. Rife, R. R. Boorstyn, "Single-tone parameter estimation from discrete-time observations," *IEEE Trans. Inf. Theory* IT-20(5):591–598 (1974) — CRBs for amplitude, frequency and phase; threshold of the ML estimator. (peer-reviewed; results re-derived above and MC-verified)
5. M. I. Skolnik, *Introduction to Radar Systems*, 3rd ed., McGraw-Hill (2001), §6.3 (theoretical accuracy of range, Doppler and angle; effective/rms bandwidth). (textbook; cited via the MIT LL course notes [8])
6. G. Strang, *Introduction to Linear Algebra*, 5th ed. (2016), ch. 4 (least squares, QR). (textbook)
7. E. D. Kaplan, C. J. Hegarty (eds.), *Understanding GPS/GNSS: Principles and Applications*, 3rd ed., Artech House (2017), ch. 8 (DLL thermal-noise jitter) — via the KB's [GNSS receiver page](../21-gnss/gnss-receiver-architecture-acquisition-tracking.md), whose formula is reproduced in the verify script (1.70 m). (textbook)
8. MIT Lincoln Laboratory / IEEE New Hampshire Section, *Radar Systems Course*, lecture "Parameter estimation and tracking, Part 1" (2010): rms error $k_M/\sqrt{S/N}$ form, accuracy vs resolution. https://gmoein.github.io/files/MIT%20Graduate%20Radar%20Course/Radar%202009%20A_15%20Parameter%20Estimation%20and%20Tracking%20Part%201.pdf (lecture notes; read as text)
