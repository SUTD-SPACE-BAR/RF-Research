---
title: Radar detection theory and CFAR — Pd, Pfa, Swerling targets, Albersheim/Shnidman, integration gain, CA/OS/GO/SO-CFAR
domain: 11-radar
slug: detection-theory-cfar
tags: [detection, neyman-pearson, pfa, pd, roc, swerling, marcum-q, rice, albersheim, shnidman, noncoherent-integration, coherent-integration, cfar, ca-cfar, os-cfar, go-cfar, so-cfar, cfar-loss, binary-integration]
prerequisites:
  - ../00-math-foundations/probability-random-processes-and-psd.md
  - ../00-math-foundations/special-functions-bessel-sinc.md
  - ../10-comms-modulation/matched-filter-detection.md
related:
  - radar-range-equation.md
  - radar-cross-section.md
  - pulsed-radar-and-pulse-compression.md
  - fmcw-radar.md
  - clutter-and-mti.md
  - mimo-radar-virtual-arrays.md
  - ../07-noise-linearity/sensitivity-and-mds.md
  - ../14-sdr-dsp/fft-spectral-analysis-windows.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Radar detection theory and CFAR

## Questions this page answers
- What SNR does a radar actually need to "see" a target, and where do numbers like 13 dB come from?
- What are probability of detection (Pd) and probability of false alarm (Pfa), and how are they traded?
- What is the Neyman–Pearson criterion and why does it lead to "compare the magnitude with a threshold"?
- Why does a fluctuating target (a drone, a person) need so much more SNR than a steel sphere?
- What are the Swerling I–IV models and which one should I use for my target?
- How accurate are Albersheim's and Shnidman's equations?
- Is non-coherent integration gain really √N? (No — it is closer to N^0.7–N^0.85.)
- What is CFAR, why does my FMCW radar need it, and how do I set the threshold multiplier?
- CA-CFAR vs OS-CFAR vs GO/SO-CFAR — which one should I use and what do they cost?
- How many false alarms per second will my range–Doppler map produce at Pfa = 10⁻⁶?
- What is CFAR loss and how many reference cells do I need?

## TL;DR
- Detection is a threshold test on the (matched-filtered, magnitude-detected) output. In complex Gaussian noise of power σ², a **single-pulse square-law threshold T gives Pfa = exp(−T/σ²)** exactly; T sets Pfa, and SNR then sets Pd.
- **Required single-pulse SNR at Pfa = 10⁻⁶** (exact, verified): non-fluctuating (Swerling 0) **11.2 / 13.2 / 14.5 dB** for Pd = 0.5 / 0.9 / 0.99; Swerling 1 (Rayleigh-fluctuating) **12.8 / 21.1 / 31.4 dB**. The 8 dB (Pd 0.9) to 17 dB (Pd 0.99) "fluctuation loss" is why drones and people are hard to detect reliably with a single look.
- **Coherent integration** of N pulses/chirps (e.g. the Doppler FFT) gives an SNR gain of exactly **N**. **Non-coherent integration** (summing magnitudes, e.g. across frames or across MIMO virtual channels before detection) gives **G ≈ N^α with α ≈ 0.84 at N = 2 falling to ≈ 0.72 at N = 100** (Pd 0.9, Pfa 10⁻⁶) — much better than the folklore √N. For pulse-to-pulse fluctuating targets it can even exceed N (diversity gain: 14.9 dB for N = 10, Swerling 2).
- **Albersheim's equation** (non-fluctuating) is within **0.3 dB** of exact; **Shnidman's equation** (Swerling 0–4) was within **0.82 dB worst-case, 0.15 dB mean** of exact over a 135-point grid (N = 1–30, Pd 0.5–0.99, Pfa 10⁻⁴–10⁻⁸) — use them for quick range-equation work (`tools/verify/radar_detection_cfar.py`).
- **CFAR** replaces the unknown noise/clutter power by an estimate from neighbouring "reference" cells. **CA-CFAR** (cell-averaging) with the threshold α × (mean of N cells) has **Pfa = (1 + α/N)⁻ᴺ** independent of the noise level. The price is **CFAR loss**: for a Swerling 1 target at Pd 0.9, Pfa 10⁻⁶ it is **4.3 / 2.0 / 1.0 / 0.5 dB for N = 8 / 16 / 32 / 64** reference cells.
- **OS-CFAR** (ordered statistic, take the k-th smallest of N, k ≈ 3N/4) has **Pfa = ∏ (N−i)/(N−i+α), i = 0…k−1**; it tolerates interfering targets in the window (a 15 dB target with an equal neighbour: CA-CFAR Pd drops 0.77 → 0.51, OS-CFAR keeps 0.72). **GO-CFAR** protects clutter edges; **SO-CFAR** resolves closely spaced targets.
- False-alarm *rate* is Pfa × (cells tested per second). A 256 × 128 range–Doppler map at 20 frames/s tests 655 360 cells/s, so Pfa = 10⁻⁶ still gives ~0.66 false alarms per second — decide Pfa from the rate you can tolerate, and use a tracker (M-of-N confirmation) to clean up.

- *Trackers, M-of-N confirmation, gating and data association (NN, PDA): [radar tracking](radar-tracking-monopulse-and-trackers.md).*

## Intuition (no math)
A radar receiver output is mostly noise that wiggles randomly. Occasionally a noise peak is large; very rarely it is huge. A target adds a steady (or fluctuating) bump in one range/Doppler cell. Detection is simply drawing a horizontal line — the threshold — and declaring "target" whenever the output pokes above it.

- Put the line **high** and you almost never raise a false alarm, but you also miss weak targets.
- Put it **low** and you catch weak targets but drown in false alarms.

The noise statistics tell you exactly how often noise alone crosses a line of a given height, so you place the line to get the false-alarm probability you can live with. Then the question is only: how big must the target bump be to cross that line, say, 90 % of the time? That is the "required SNR".

**Why fluctuating targets are expensive.** A sphere reflects the same power from any angle. A drone or a person is a collection of many small reflectors whose echoes add with random phases; as the aspect changes, they sometimes add up and sometimes cancel, so the echo power jumps around (exponentially distributed for many equal scatterers). If you want 90 % detection, you must survive the deep fades — you pay for the bad looks, not the average. More independent looks (frequency agility, several scans, several MIMO channels) average the fades out.

**Why CFAR is needed.** The "noise" level is not constant in real radars: rain, ground clutter near the radar, the TX-leakage skirt in an FMCW radar, receiver gain changes, temperature. A fixed threshold tuned in the lab either floods you with false alarms in clutter or goes deaf in quiet regions. CFAR (constant false-alarm rate) estimates the local background from the cells around the one being tested and scales the threshold to it — like judging whether someone is shouting by comparing with the people standing next to them rather than with an absolute decibel number.

## The math

### Level 1 — hypotheses, Pfa, Pd, and the single-pulse result
After matched filtering (see [matched filter](../10-comms-modulation/matched-filter-detection.md), [pulse compression](pulsed-radar-and-pulse-compression.md), or the range FFT of an [FMCW radar](fmcw-radar.md)), each resolution cell gives one complex sample $x$:

- $H_0$ (no target): $x = w$, with $w \sim \mathcal{CN}(0,\sigma^2)$ — circular complex Gaussian, $\sigma^2/2$ per real part.
- $H_1$ (target): $x = s + w$, $s = A e^{j\phi}$ with unknown phase $\phi$ uniform on $[0,2\pi)$.

Single-sample **SNR** $\chi = A^2/\sigma^2$ (dimensionless; the SNR the [radar range equation](radar-range-equation.md) delivers). Test statistic: square-law detector $z = |x|^2$ (the linear detector $|x|$ gives the same decisions for a single sample).

- **Probability of false alarm** $P_{FA} = P(z > T \mid H_0)$. Under $H_0$, $|x|^2$ is exponential with mean $\sigma^2$, so
$$P_{FA} = e^{-T/\sigma^2}\quad\Longleftrightarrow\quad T = \sigma^2\ln(1/P_{FA}).$$
For $P_{FA} = 10^{-6}$, $T/\sigma^2 = 13.8$ (11.4 dB above the mean noise power).
- **Probability of detection** $P_D = P(z > T\mid H_1)$. For a non-fluctuating target ($|x|$ is Rician):
$$P_D = Q_1\!\left(\sqrt{2\chi},\ \sqrt{2T/\sigma^2}\right) = Q_1\!\left(\sqrt{2\chi},\ \sqrt{-2\ln P_{FA}}\right),$$
where $Q_1(a,b) = \int_b^\infty x\,e^{-(x^2+a^2)/2} I_0(ax)\,dx$ is the Marcum Q-function ($I_0$ = modified Bessel function, see [special functions](../00-math-foundations/special-functions-bessel-sinc.md)).

**Required SNR** is the $\chi$ that solves $P_D(\chi, P_{FA}) = P_D^{\text{wanted}}$. It is also called the *detectability factor* $D_0$.

### Level 1½ — a detection budget with a calculator
The Marcum Q-function is needed only for exact $P_D$. Everything a radar budget uses can be done with logs:
1. **Set the line from the false-alarm rate you can tolerate.** Noise crosses a threshold $T$ with probability $e^{-T/\sigma^2}$, so $T/\sigma^2 = \ln(1/P_{FA})$. The false-alarm *rate* is $P_{FA}$ × (cells tested per second).
2. **Get the SNR you need from Albersheim's equation** (Level 3). It uses only logs: $A = \ln(0.62/P_{FA})$, $B = \ln(P_D/(1-P_D))$, and SNR [dB] = $(6.2 + 4.54/\sqrt{1.44})\log_{10}(A + 0.12AB + 1.7B)$ for a single pulse. It agrees with the exact answer to within 0.3 dB.
3. **Pay for not knowing σ².** CA-CFAR estimates σ² by averaging $N$ neighbouring cells and sets the threshold α times that average, with $\alpha = N(P_{FA}^{-1/N} - 1)$. Because the estimate is noisy, α is always larger than $\ln(1/P_{FA})$. The gap in dB is a first estimate of the CFAR loss; the exact loss for fluctuating targets is in Level 3.

*Worked numbers (verified, `tools/verify/s18_level15_numbers.py`).* Take $P_{FA}$ = 10⁻⁶.
- **Threshold:** $\ln(10^6)$ = 13.8, so the line sits 11.4 dB above the mean noise.
- **False-alarm rate:** a 256 × 128 range–Doppler map at 20 frames/s tests 655 360 cells/s, so it gives 0.66 false alarms per second.
- **Required SNR:** for $P_D$ = 0.9, $A$ = 13.34 and $B$ = 2.20. Albersheim then gives **13.1 dB** (exact: 13.2 dB).
- **CFAR price:** a 16-cell CA-CFAR needs α = 16(10^{6/16} − 1) = 21.9, i.e. 13.4 dB. That is 2.0 dB above the known-noise line.

### Level 2 — derivations

**Neyman–Pearson criterion.** Radar cannot assign sensible prior probabilities or costs to "target present", so instead of minimising average cost we *maximise $P_D$ subject to $P_{FA} = \alpha$* [13]. Choose the decision region $R_1$ (decide $H_1$) to maximise
$$J = \int_{R_1} p(x|H_1)\,dx - \lambda\left(\int_{R_1} p(x|H_0)\,dx - \alpha\right) = \int_{R_1}\big[p(x|H_1) - \lambda p(x|H_0)\big]dx + \lambda\alpha .$$
$J$ is largest when $R_1$ contains exactly the points where the bracket is positive:
$$\Lambda(x) = \frac{p(x|H_1)}{p(x|H_0)} \gtrless \lambda \quad\text{(likelihood-ratio test, LRT)},$$
with $\lambda$ set so that $P_{FA} = \alpha$.

**Unknown phase → envelope detector.** With $p(x|H_0) = \frac{1}{\pi\sigma^2}e^{-|x|^2/\sigma^2}$ and $p(x|H_1,\phi) = \frac{1}{\pi\sigma^2}e^{-|x - Ae^{j\phi}|^2/\sigma^2}$, averaging over uniform $\phi$ gives
$$\Lambda(x) = e^{-A^2/\sigma^2}\, I_0\!\left(\frac{2A|x|}{\sigma^2}\right).$$
$I_0$ is monotonically increasing, so the LRT is equivalent to $|x| \gtrless T'$: **the optimum detector for a known-shape echo of unknown phase is matched filter → magnitude → threshold** [1 §6.2], [9]. If the phase were known (it never is in radar), the test would be on $\mathrm{Re}\{x e^{-j\phi}\}$ and $P_D = Q\big(Q^{-1}(P_{FA}) - \sqrt{2\chi}\big)$ — about 0.5 dB better at typical operating points (see [matched filter page](../10-comms-modulation/matched-filter-detection.md)).

**Distributions.** Under $H_0$ the envelope $r = |x|$ is Rayleigh; under $H_1$ it is Rice:
$$p(r|H_1) = \frac{2r}{\sigma^2}\exp\!\left(-\frac{r^2 + A^2}{\sigma^2}\right)I_0\!\left(\frac{2Ar}{\sigma^2}\right).$$
Integrating from $\sqrt T$ gives the Marcum-Q result (verified in the script against the non-central χ² form and Monte-Carlo, to 10⁻⁶).

**Fluctuating targets — the Swerling models [8].** Real RCS fluctuates (see [radar cross section](radar-cross-section.md)). Swerling's four cases combine two pdfs of the RCS $\sigma_{RCS}$ with two correlation times:

| Model | RCS pdf (mean $\bar\sigma$) | Physical picture | Decorrelation |
|---|---|---|---|
| Swerling 0 (or 5) | constant | sphere, corner reflector, calibration target | — |
| Swerling 1 | exponential: $p(\sigma) = \frac{1}{\bar\sigma}e^{-\sigma/\bar\sigma}$ (χ², 2 dof) | many comparable scatterers (aircraft, drone, car at random aspect) | scan-to-scan (constant within a dwell) |
| Swerling 2 | exponential | same, but frequency-agile or fast-tumbling | pulse-to-pulse |
| Swerling 3 | χ², 4 dof: $p(\sigma) = \frac{4\sigma}{\bar\sigma^2}e^{-2\sigma/\bar\sigma}$ | one dominant scatterer plus many small ones (missile body, rocket, person?) | scan-to-scan |
| Swerling 4 | χ², 4 dof | same, pulse-to-pulse | pulse-to-pulse |

**Swerling 1, single pulse — a closed form.** Conditional on $\sigma$, the echo is $\mathcal{CN}$ plus noise; averaging over the exponential RCS makes $x$ itself $\mathcal{CN}(0, \sigma^2(1+\bar\chi))$, so $|x|^2$ is exponential with mean $\sigma^2(1+\bar\chi)$:
$$P_D = e^{-T/[\sigma^2(1+\bar\chi)]} = P_{FA}^{\,1/(1+\bar\chi)} \quad\Longrightarrow\quad \bar\chi_{req} = \frac{\ln P_{FA}}{\ln P_D} - 1 .$$
For $P_{FA} = 10^{-6}$, $P_D = 0.9$: $\bar\chi = 13.8155/0.10536 - 1 = 130.1$ → **21.1 dB**, versus 13.2 dB for Swerling 0. The difference is the **fluctuation loss** (8 dB here; 17 dB at $P_D = 0.99$).

**N-pulse integration.** Suppose $N$ samples of the same cell are available (N chirps of an FMCW frame, N pulses in a dwell, N virtual channels).

- *Coherent* integration: $y = \sum_n x_n e^{-j\phi_n}$ with the phase progression $\phi_n$ known or searched over (the Doppler FFT searches over it). Signal adds as amplitude ($N A$, power $N^2A^2$), noise as power ($N\sigma^2$): **gain = N exactly** [4] (MC: 9.05 dB for N = 8, 18.06 dB for N = 64). Then apply the single-pulse curves with $\chi \to N\chi$.
- *Non-coherent* (post-detection) integration: $z = \sum_n |x_n|^2$. Under $H_0$, $z \sim \text{Gamma}(N, \sigma^2)$, so the threshold is $T = \sigma^2\,\Gamma^{-1}_{\text{inc}}(N, P_{FA})$ (inverse regularised upper incomplete gamma). Under $H_1$ (Swerling 0), $2z/\sigma^2$ is non-central χ² with $2N$ degrees of freedom and non-centrality $2N\chi$:
$$P_D = \Pr\left[\chi'^2_{2N}(2N\chi) > 2T/\sigma^2\right],$$
which is Marcum's generalised $Q_N$ [9], [4 eqs. 10–11]. Swerling 2 is even simpler — each $x_n \sim \mathcal{CN}(0,\sigma^2(1+\chi))$, so $P_D = \Gamma_{\text{inc}}\big(N, T/[\sigma^2(1+\chi)]\big)$. Swerling 1 and 3 are the Swerling 0 result averaged over the RCS pdf; Swerling 4 is averaged per pulse. All five were checked against direct Monte-Carlo (agreement within 0.004 in $P_D$).

**Non-coherent integration gain.** Define $G_{nc}(N) = \chi_{req}(1)/\chi_{req}(N)$ (single-sample SNR ratio) and write $G_{nc} = N^\alpha$ [4]. The exact values (Swerling 0, $P_D = 0.9$, $P_{FA} = 10^{-6}$):

| N | 2 | 5 | 10 | 30 | 100 |
|---|---|---|---|---|---|
| α | 0.840 | 0.813 | 0.792 | 0.757 | 0.722 |

So $G_{nc}(10) \approx 7.9$ dB, not the 5 dB a √N law predicts. α tends to 0.5 only when the single-sample SNR is absurdly low (tens of millions of pulses) [4]. For Richards' example ($P_{FA} = 10^{-8}$, $P_D = 0.8$, N = 10) the exact square-law answer is 13.68 → 5.63 dB, $G_{nc}$ = 8.05 dB, α = 0.805 (Richards read 8.3 dB off a linear-detector graph) [4].

For *fluctuating* targets with independent samples (Swerling 2/4), non-coherent integration also averages out the fades, so the gain can exceed N: Swerling 2, $P_D$ 0.9, N = 10 → **14.9 dB** gain. This "diversity gain" is why frequency agility and multiple looks help so much against fluctuating targets.

### Level 3 — closed-form approximations, CFAR, and limits

**Albersheim's equation [5], [6].** An empirical fit to Robertson's curves [14] for a non-fluctuating target and *linear* detector, N non-coherently integrated samples:
$$A = \ln\frac{0.62}{P_{FA}},\quad B = \ln\frac{P_D}{1-P_D},\quad \chi_{1,N}\,[\text{dB}] = -5\log_{10}N + \left(6.2 + \frac{4.54}{\sqrt{N+0.44}}\right)\log_{10}\!\big(A + 0.12AB + 1.7B\big).$$
Usual validity: $10^{-7}\le P_{FA}\le10^{-3}$, $0.1\le P_D\le0.9$, $1\le N\le 8096$ [1]. Verified: within 0.28 dB of the exact *square-law* result and 0.09 dB of a Monte-Carlo *linear* detector (N = 10, $P_{FA}$ = 10⁻⁴, $P_D$ = 0.9: Albersheim 3.89 dB, MC linear 3.98 dB, exact square-law 4.14 dB). Linear and square-law detectors differ by only ~0.1–0.3 dB [4].

**Shnidman's equation [7].** Covers Swerling 0–4, square-law detector:
$$K = \infty,\,1,\,N,\,2,\,2N \ \ (\text{SW }0,1,2,3,4),\qquad \alpha_S = \begin{cases}0 & N<40\\ 1/4 & N\ge 40\end{cases}$$
$$\eta = \sqrt{-0.8\ln[4P_{FA}(1-P_{FA})]} + \operatorname{sgn}(P_D-0.5)\sqrt{-0.8\ln[4P_D(1-P_D)]}$$
$$X_\infty = \eta\left(\eta + 2\sqrt{N/2 + (\alpha_S - 1/4)}\right)$$
$$C_1 = \frac{((17.7006P_D - 18.4496)P_D + 14.5339)P_D - 3.525}{K},\quad C_2 = \frac{1}{K}\left[e^{27.31P_D - 25.14} + (P_D - 0.8)\left(0.7\ln\frac{10^{-5}}{P_{FA}} + \frac{2N-20}{80}\right)\right]$$
$$C_{dB} = C_1\ (0.1\le P_D\le0.872),\quad C_1 + C_2\ (0.872 < P_D \le 0.99);\qquad \chi_{1,N} = \frac{10^{C_{dB}/10}X_\infty}{N}.$$
Claimed accuracy < 1 dB (mostly < 0.5 dB) for $0.1\le P_D\le0.99$, $10^{-9}\le P_{FA}\le10^{-3}$, $1\le N\le100$ [7]. **Verified**: max error 0.82 dB, mean 0.15 dB, 96 % of the grid within 0.5 dB; the worst cases are Swerling 1 and 3 at $P_D = 0.99$ with N = 30 (Shnidman ~0.6 dB optimistic).

**CA-CFAR [12].** Test the cell under test (CUT) $z_0$ against $\alpha\hat\mu$, where $\hat\mu = \frac1N\sum_{i=1}^N z_i$ over N reference cells (split either side of the CUT, with a few **guard cells** between so the target's own spread does not leak into the estimate). In homogeneous exponential noise of unknown mean μ, $\sum z_i \sim \text{Gamma}(N,\mu)$ and
$$P_{FA} = E\!\left[e^{-\alpha\hat\mu/\mu}\right] = \left(1 + \frac{\alpha}{N}\right)^{-N}\quad\Longrightarrow\quad \alpha = N\left(P_{FA}^{-1/N} - 1\right),$$
using the moment-generating function of the Gamma distribution. μ has cancelled: the false-alarm rate is **constant** whatever the noise level. For a Swerling 1 target in the CUT, $z_0$ is exponential with mean $\mu(1+\bar\chi)$, so
$$P_D = \left(1 + \frac{\alpha}{N(1+\bar\chi)}\right)^{-N}.$$
As $N\to\infty$, $(1+\alpha/N)^{-N}\to e^{-\alpha}$ and CA-CFAR becomes the known-noise detector. Example: N = 16, $P_{FA}$ = 10⁻³ → α = 8.64 (9.4 dB), compared with 6.91 (8.4 dB) for known noise — the CFAR has to set the bar higher because its noise estimate is itself noisy.

**CFAR loss** = required SNR with CFAR − required SNR with known noise (Swerling 1, $P_D$ 0.9, $P_{FA}$ 10⁻⁶, exact):

| N reference cells | 8 | 16 | 32 | 64 | 128 |
|---|---|---|---|---|---|
| CA-CFAR loss (dB) | 4.27 | 2.01 | 0.97 | 0.48 | 0.24 |

Rule of thumb from the table: the loss roughly halves each time N doubles. 16–32 cells is the common compromise; more cells lower the loss but make the window straddle clutter boundaries.

**OS-CFAR [10].** Sort the N reference cells and use the k-th smallest, $z_{(k)}$, as the noise estimate (Rohling suggested $k \approx 3N/4$). By the Rényi representation, $z_{(k)} = \mu\sum_{i=0}^{k-1}E_i/(N-i)$ with $E_i$ i.i.d. unit exponentials, so the MGF gives
$$P_{FA} = \prod_{i=0}^{k-1}\frac{N-i}{N-i+\alpha}.$$
(Verified: N = 16, k = 12, $P_{FA}$ = 10⁻³ → α = 7.42, MC 1.01 × 10⁻³.) Up to $N-k$ interfering targets in the window are simply sorted out of the estimate. Its extra loss in clean noise is small (a fraction of a dB more than CA for N ≈ 16–32) [10], [2].

**GO- and SO-CFAR [11], [17].** Split the window into leading and lagging halves (n = N/2 cells each, sums $S_1, S_2$). **Greatest-of** uses $\alpha\max(S_1,S_2)$ — robust at *clutter edges* (it will not under-estimate when half the window is in rain); **smallest-of** uses $\alpha\min(S_1,S_2)$ — keeps *two close targets* from masking each other but raises false alarms at clutter edges. Closed forms (verified by MC):
$$P_{FA}^{SO} = 2\sum_{i=0}^{n-1}\binom{n+i-1}{i}(2+\alpha)^{-(n+i)},\qquad P_{FA}^{GO} = 2(1+\alpha)^{-n} - P_{FA}^{SO}.$$

**Where these models break.**
- Clutter is often not exponential/Rayleigh: sea and land clutter at low grazing angles are spiky (Weibull, log-normal, K-distributed). A CA-CFAR designed for exponential noise then gives a *much* higher Pfa than designed. Remedies: log-CFAR, Weibull/K-CFAR, or clutter maps (see [clutter and MTI](clutter-and-mti.md)).
- Reference cells must be independent and identically distributed. In an FMCW range profile, windowing (Hann) correlates adjacent bins; in 2-D range–Doppler maps the zero-Doppler column and the TX-leakage bins are not "noise-like". Exclude them or use a separate threshold.
- The "SNR" in all formulas is the SNR *at the detector input after all integration*, including processing losses (window, straddle); see [radar range equation — losses](radar-range-equation.md).

**Binary (M-of-N) integration.** Declare a detection only if at least M of N looks cross the threshold:
$$P = \sum_{k=M}^{N}\binom{N}{k}p^k(1-p)^{N-k},$$
applied to both $p = P_D$ and $p = P_{FA}$. 2-of-3 with a per-look $P_{FA}$ of 10⁻⁴ gives ≈ 3 × 10⁻⁸. Binary integration costs roughly 1–2 dB relative to optimum non-coherent integration but is simple and robust to spiky interference; a tracker's "confirm after M hits in N scans" logic is the same thing [2].

## Design equations & rules of thumb

| Equation | When valid | Typical numbers |
|---|---|---|
| $P_{FA} = e^{-T/\sigma^2}$ | single sample, complex Gaussian noise, square-law/linear | $P_{FA}$ = 10⁻⁶ ⇒ T = 13.8σ² (11.4 dB) |
| $P_D = Q_1(\sqrt{2\chi},\sqrt{-2\ln P_{FA}})$ | Swerling 0, single sample | $P_D$ 0.9 @ 10⁻⁶ needs 13.2 dB |
| $\chi = \ln P_{FA}/\ln P_D - 1$ | Swerling 1, single sample | 21.1 dB (Pd .9, 10⁻⁶); 31.4 dB (Pd .99) |
| Coherent gain = N | phase-stable target within the CPI | 128 chirps ⇒ 21.1 dB |
| Non-coherent gain ≈ N^α, α ≈ 0.72–0.84 | Swerling 0, N = 2–100 | N = 12 virtual channels ⇒ 8.5 dB (SW1: 8.2 dB) |
| Albersheim | SW0, $10^{-7}\le P_{FA}\le10^{-3}$, $0.1\le P_D\le0.9$ | ±0.3 dB |
| Shnidman | SW0–4, N ≤ 100, $P_D$ 0.1–0.99 | < 1 dB (typ. 0.15 dB) |
| CA-CFAR: $\alpha = N(P_{FA}^{-1/N}-1)$ (× mean) | homogeneous exponential background | N = 16, 10⁻³ ⇒ α = 8.64 |
| OS-CFAR: $\prod_{i<k}(N-i)/(N-i+\alpha) = P_{FA}$ | k ≈ 3N/4 | N = 16, k = 12, 10⁻³ ⇒ α = 7.42 |
| CFAR loss ≈ halves per doubling of N | SW1, $P_D$ 0.9, $P_{FA}$ 10⁻⁶ | 2.0 dB at N = 16 |
| False alarms/s = $P_{FA}\times$ cells/s | independent cells | 256 × 128 × 20 fps × 10⁻⁶ = 0.66/s |

## Worked examples

**Example 1 — What SNR must my 77 GHz radar budget for a drone vs a car?** Pd 0.9, Pfa 10⁻⁶, one frame (the Doppler FFT has already done the coherent integration, so the SNR below is the post-FFT value in the target's range–Doppler cell).
- Car at moderate aspect, dominated by a few big flat surfaces → treat as Swerling 3 (one dominant scatterer): single look **17.3 dB**.
- Small quadcopter (plastic body, motors, battery, many comparable scatterers) → Swerling 1: **21.1 dB**.
- Calibration corner reflector → Swerling 0: **13.2 dB**.
If the TX–RX MIMO virtual channels (12 on a 3TX × 4RX TI chip, see [MIMO](mimo-radar-virtual-arrays.md)) are summed non-coherently before detection, as TI's reference chain does [15], and the fluctuation is common to all channels (same look, Swerling 1 scan-to-scan), the exact non-coherent gain for N = 12 is 8.2 dB (21.14 → 12.96 dB), close to the Swerling 0 value of 8.5 dB. The per-channel requirement for the drone is therefore ≈ 13.0 dB. (Beamforming the 12 channels coherently instead would give the full 10.8 dB, but only in the beam direction.)

**Example 2 — Setting a CA-CFAR on an FMCW range profile.** 256-bin range FFT, Hann window (adjacent bins correlated, so skip one guard bin each side), 2 × 8 = 16 reference bins, target Pfa 10⁻⁴:
$$\alpha = 16\,(10^{4/16} - 1) = 16\,(1.778 - 1) = 12.45\ (10.95\text{ dB above the local mean}).$$
With known noise the threshold would be $\ln 10^4 = 9.21$ (9.6 dB). Budget the ~1.4 dB higher threshold (plus the loss from the estimate's randomness) as the CFAR loss — about 2 dB for N = 16.

**Example 3 — False-alarm budget.** TI-style frame: 256 range × 128 Doppler cells, 20 frames/s → 655 360 cells/s. Tolerating one false detection per 10 s requires Pfa ≈ 1/(6.55 × 10⁶) ≈ 1.5 × 10⁻⁷. Moving from 10⁻⁶ to 1.5 × 10⁻⁷ costs only 0.46 dB of SNR for a Swerling 0 target at Pd 0.9 (exact: 13.18 → 13.65 dB) — lowering Pfa is cheap in SNR because the noise tail falls off exponentially. Alternatively accept 10⁻⁵ and let a 2-of-3 tracker confirmation cut false tracks by ~3 × 10⁻¹⁰ per cell-triple.

**Example 4 — Why the √N rule under-sells integration.** A rocket-tracking radar gets 10 independent-noise looks at a nearly constant (Swerling 0) nose-on target per dwell and can only integrate non-coherently (phase unstable). Required per-look SNR at Pd 0.9, Pfa 10⁻⁶: exact 5.27 dB (Albersheim 4.99 dB), versus 13.18 dB single look → **7.9 dB gain**. A √N assumption (5 dB) would under-estimate detection range by a factor $10^{(7.9-5)/40} = 1.18$ (18 %).

## Practical notes
- **Measure the noise, don't assume it.** Record a range–Doppler map with the radar pointed at the sky (or a load), histogram $|x|^2$ in cells away from DC and leakage, and check that it is exponential (a straight line on a log-count vs power plot). Deviations mean spurs, ADC problems or clutter, and your Pfa will not be what you designed.
- **Guard cells:** with a Hann/Hamming window the main lobe spans ~4 bins; use 1–2 guard cells per side in range and Doppler, more for strong targets whose sidelobes spread.
- **2-D CFAR** on range–Doppler maps: either a full 2-D window (cross- or rectangle-shaped), or the cheaper "CA along Doppler, then confirm with CA along range" used in TI's mmWave SDK demos [15]. Doppler-first CFAR handles range-dependent noise (e.g. the phase-noise skirt near zero range).
- **Zero-Doppler / DC:** stationary clutter and TX leakage pile up there. Either suppress it (static-clutter removal = subtract the mean over chirps, an MTI in disguise; see [clutter and MTI](clutter-and-mti.md)) or exclude it from both CUT and references.
- **Fixed-point hardware:** TI's hardware accelerator CFAR works on log-magnitude data; a log-CFAR averages logs (geometric mean), which changes the α-to-Pfa relation — use the vendor's documented mapping or calibrate α by Monte-Carlo on recorded noise.
- **Choose Pfa from the application:** a people-counter tolerates a few false blips per minute; a rocket-tracking gate that re-points an antenna should require M-of-N confirmation.

## Common mistakes & misconceptions
- **"13 dB SNR is enough to detect anything."** Only for a steady target at Pd 0.9, Pfa 10⁻⁶ and a single look. A fluctuating target (Swerling 1) needs 21 dB for the same Pd, or several independent looks.
- **"Non-coherent integration gives √N."** Exact results give N^0.72–N^0.84 for practical N [4]; the √N limit only applies at vanishing single-sample SNR. Using √N under-predicts range.
- **"Integrating more pulses always helps equally."** Coherent integration only works while the target stays in one range/Doppler cell and the phase is stable (range migration, acceleration, and VCO phase noise limit it; see [FMCW](fmcw-radar.md)).
- **Mixing up the SNR definitions.** Albersheim/Shnidman give the *single-sample* SNR needed when N samples are integrated, not the post-integration SNR. Coherent integration results are applied as "single-pulse SNR × N".
- **Applying CA-CFAR to spiky clutter.** Designed Pfa 10⁻⁶ can become 10⁻³ in Weibull sea clutter. Validate on recorded data.
- **Letting the target leak into its own reference cells** (no guard cells, or window sidelobes): the threshold rises with the target and it suppresses itself ("self-masking").
- **Thinking Pfa is a rate.** It is a per-test probability. Rate = Pfa × tests per second.
- **Using a fixed threshold on an FMCW range profile.** The noise floor there is range-dependent (phase-noise skirt near leakage, IF high-pass filter slope, 1/f noise at low beat frequencies); CFAR — or at least a range-dependent threshold — is essential.

## How to simulate / verify
- `tools/verify/radar_detection_cfar.py` (~2 min): exact Swerling 0–4 Pd via non-central χ²/Gamma/numerical averaging, Monte-Carlo cross-checks, Albersheim and Shnidman accuracy maps, integration-gain exponents, CA/OS/GO/SO-CFAR Pfa formulas vs Monte-Carlo, CFAR-loss table, masking demo. **ALL PASS.**
- Quick calculators in Python: `scipy.special.gammainccinv(N, pfa)` gives the non-coherent threshold; `scipy.stats.ncx2.sf(2*T, 2*N, 2*N*chi)` gives Swerling 0 Pd; `(np.log(pfa)/np.log(pd) - 1)` gives Swerling 1 single-pulse SNR.
- To validate your own CFAR: feed it recorded "no-target" frames and count exceedances per cell; then inject synthetic targets of known SNR into recorded noise to measure Pd — more honest than simulated Gaussian noise.
- MATLAB Phased Array Toolbox equivalents: `albersheim`, `shnidman`, `rocsnr`, `phased.CFARDetector` (not required; the Python script covers the same ground).

## Open questions / gaps
- CFAR performance in non-Gaussian clutter (Weibull/K) is only described qualitatively here; a numerical treatment (log-t CFAR, clutter-map CFAR) belongs with [clutter and MTI](clutter-and-mti.md) and is not yet verified.
- Which Swerling model best fits small hobby rockets (fibreglass vs carbon airframes, fins, motor case) is not established in the literature found; Swerling 1/3 are assumptions (see [radar cross section](radar-cross-section.md)).
- The exact α-to-Pfa mapping of TI's hardware-accelerator log-domain CFAR was not checked against TI documentation.
- Binary-integration optimum M for given N (≈ 1.5√N rule quoted in textbooks) not verified numerically here.

## Sources
1. M. A. Richards, *Fundamentals of Radar Signal Processing*, 2nd ed., McGraw-Hill, 2014 — ch. 6 (threshold detection, Swerling models, Albersheim/Shnidman, CFAR). (textbook)
2. M. A. Richards, J. A. Scheer, W. A. Holm (eds.), *Principles of Modern Radar, Vol. I: Basic Principles*, SciTech, 2010 — ch. 15 (threshold detection), ch. 16 (CFAR, binary integration). (textbook)
3. M. I. Skolnik, *Introduction to Radar Systems*, 3rd ed., McGraw-Hill, 2001 — ch. 2 (radar equation: Pd/Pfa, integration, fluctuating targets) and ch. 5 "Detection of Signals in Noise" (detectors, integrators, CFAR); chapter map checked against gaps/D4-curriculum.md §3.19 by W5-S18. (textbook)
4. M. A. Richards, "Noncoherent Integration Gain, and its Approximation," Georgia Tech technical memo, 9 June 2010 — https://bpb-us-e1.wpmucdn.com/sites.gatech.edu/dist/5/462/files/2016/12/Noncoherent-Integration-Gain-Approximations.pdf — Gc = N, Gnc definition, N^α with 0.5 < α < 1, Peebles' formula, Albersheim use. (lecture notes, textbook author)
5. W. J. Albersheim, "A closed-form approximation to Robertson's detection characteristics," *Proc. IEEE*, vol. 69, no. 7, p. 839, July 1981. (peer-reviewed)
6. D. W. Tufts, A. J. Cann, "On Albersheim's detection equation," *IEEE Trans. AES*, vol. 19, no. 4, pp. 643–646, 1983. (peer-reviewed)
7. D. A. Shnidman, "Determination of required SNR values," *IEEE Trans. AES*, vol. 38, no. 3, pp. 1059–1064, July 2002 — coefficients re-typed and verified numerically here. (peer-reviewed)
8. P. Swerling, "Probability of detection for fluctuating targets," *IRE Trans. Information Theory*, vol. IT-6, no. 2, pp. 269–308, April 1960. (peer-reviewed)
9. J. I. Marcum, "A statistical theory of target detection by pulsed radar," *IRE Trans. Information Theory*, vol. IT-6, no. 2, pp. 59–267, April 1960. (peer-reviewed)
10. H. Rohling, "Radar CFAR thresholding in clutter and multiple target situations," *IEEE Trans. AES*, vol. 19, no. 4, pp. 608–621, July 1983 — OS-CFAR, k ≈ 3N/4. (peer-reviewed)
11. V. G. Hansen, J. H. Sawyers, "Detectability loss due to 'greatest of' selection in a cell-averaging CFAR," *IEEE Trans. AES*, vol. 16, no. 1, pp. 115–118, 1980 — GO/SO Pfa expressions (verified by MC here). (peer-reviewed)
12. H. M. Finn, R. S. Johnson, "Adaptive detection mode with threshold control as a function of spatially sampled clutter-level estimates," *RCA Review*, vol. 29, pp. 414–464, 1968 — origin of CA-CFAR. (peer-reviewed)
13. J. Neyman, E. S. Pearson, "On the problem of the most efficient tests of statistical hypotheses," *Phil. Trans. R. Soc. A*, vol. 231, pp. 289–337, 1933. (peer-reviewed)
14. G. H. Robertson, "Operating characteristics for a linear detector of CW signals in narrow-band Gaussian noise," *Bell Syst. Tech. J.*, vol. 46, no. 4, pp. 755–774, 1967. (peer-reviewed)
15. S. Rao, "MIMO Radar," TI application report SWRA554A, 2017/2018 — per-virtual-antenna 2-D FFTs summed non-coherently into a pre-detection matrix. https://www.ti.com/lit/an/swra554a/swra554a.pdf (app note)
16. P. Z. Peebles Jr., *Radar Principles*, Wiley, 1998 — non-coherent integration-gain formula (as quoted in [4]). (textbook)
17. G. V. Trunk, "Range resolution of targets using automatic detectors," *IEEE Trans. AES*, vol. 14, no. 5, pp. 750–755, 1978 — SO-CFAR. (peer-reviewed)
18. `tools/verify/radar_detection_cfar.py` — all numbers on this page marked "exact", "verified" or "MC". (verification script)
