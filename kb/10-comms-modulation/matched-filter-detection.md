---
title: Matched filter and signal detection
domain: 10-comms-modulation
slug: matched-filter-detection
tags: [matched-filter, correlator, SNR, 2E/N0, maximum-likelihood, MAP, Neyman-Pearson, pulse-compression, detection, whitening, sync-word]
prerequisites:
  - ../00-math-foundations/linear-systems-convolution.md
  - ../00-math-foundations/fourier-series-and-transform.md
  - ../00-math-foundations/probability-random-processes-and-psd.md
related:
  - ber-ebn0-and-shannon.md
  - pulse-shaping-isi.md
  - digital-modulation-psk-qam-fsk.md
  - synchronization-carrier-timing.md
  - packet-framing-protocols.md
  - spread-spectrum-dsss-fhss-css.md
  - ../11-radar/pulsed-radar-and-pulse-compression.md
  - ../11-radar/detection-theory-cfar.md
  - ../11-radar/ambiguity-function-waveforms.md
  - ../14-sdr-dsp/digital-filters-fir-iir.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Matched filter and signal detection

## Questions this page answers
- What is a matched filter and why is it "optimal"?
- Why is the best possible output SNR 2E/N0 no matter what shape the pulse has?
- Is a matched filter the same thing as a correlator?
- Why does my receiver need a root-raised-cosine filter if the transmitter already has one?
- How much do I lose if I use a plain RC or crystal IF filter instead of a true matched filter?
- How does a radar compress a long chirp into a short pulse, and what does that have to do with LoRa?
- How do I set a threshold to detect a preamble or sync word with a given false-alarm rate?
- Why does a small frequency offset destroy my sync-word correlator on a fast rocket?
- What changes when the noise is not white?

## TL;DR
- For a known pulse $s(t)$ of energy $E$ in white Gaussian noise (two-sided PSD $N_0/2$), the linear filter that maximises the output SNR at the sampling instant $T$ is $h(t)=k\,s^*(T-t)$ — the pulse **time-reversed and conjugated**. Its peak output SNR is **$2E/N_0$**, independent of pulse shape (verified for three shapes in `tools/verify/comms_matched_filter.py`).
- Sampling a matched filter at $t=T$ is *exactly* the same as **correlating** the input with the pulse over $[0,T]$. Integrate-and-dump is the matched filter for rectangular pulses; a root-raised-cosine receive filter is the matched filter for RRC transmit pulses.
- In AWGN the matched-filter (correlator) outputs are a **sufficient statistic**: nothing useful is thrown away, and minimum-distance decisions on them are maximum-likelihood. That is why every BER formula on [the BER page](ber-ebn0-and-shannon.md) starts with a correlator.
- Detectability depends on **energy**, not peak power or bandwidth. A long, low-power pulse is as detectable as a short, strong one of equal energy — the basis of [spread spectrum](spread-spectrum-dsss-fhss-css.md), LoRa chirps and [radar pulse compression](../11-radar/pulsed-radar-and-pulse-compression.md). A chirp of time–bandwidth product $TB$ compresses to width ≈ $1/B$ (gain ≈ $TB$).
- Cheap substitutes cost little: a single-pole RC filter on a rectangular pulse, optimised at $B_{3dB}T\approx0.2$, loses only **0.89 dB**. Wrong sampling time costs $20\log_{10}(1-|\tau|/T)$ for rectangular pulses (**2.5 dB at a quarter symbol**).
- A coherent correlator of length $T$ loses $|\mathrm{sinc}(\Delta f\,T)|^2$ with frequency offset $\Delta f$: a 32-bit sync word at 10 kbit/s (3.2 ms) loses **6.9 dB at 200 Hz and 24.7 dB at 1 kHz**. Doppler and crystal offsets must be removed first, or the correlation split into shorter pieces combined non-coherently.
- Detection with a threshold: coherent $P_D=Q\big(Q^{-1}(P_{FA})-\sqrt{2E/N_0}\big)$; unknown phase (envelope) $P_D=Q_1\big(\sqrt{2E/N_0},\sqrt{-2\ln P_{FA}}\big)$ (Marcum Q). For $P_D=0.9$, $P_{FA}=10^{-6}$ you need $2E/N_0$ ≈ 15.6 dB coherent, 16.2 dB non-coherent (i.e. $E/N_0$ = 12.6/13.2 dB, the radar χ of [detection theory](../11-radar/detection-theory-cfar.md); the KB's link and radar budgets quote SNR as $E/N_0$ — [conventions](../00-math-foundations/canonical-values-and-conventions.md)).

## Intuition (no math)
Imagine listening for a specific tune in a noisy room. The best strategy is to know the tune in advance and continuously ask "how much does what I hear right now resemble the tune?" — multiplying what you hear by your memory of the tune, note by note, and adding up. When the tune is really there and aligned with your memory, every note adds up in the same direction; the random noise adds up in random directions and partly cancels. That running "resemblance score" is correlation, and a filter whose impulse response is the tune played backwards computes it automatically for every possible alignment.

Why "backwards"? A filter's output is the input convolved with its impulse response, and convolution flips one of the two signals. Flipping the template first makes convolution become correlation.

Why is the result independent of pulse shape? Because the filter collects *all the energy* of the pulse into one instant, while the noise it lets through depends only on how much energy the filter itself has. Any shape with the same energy gives the same peak-to-noise ratio. Shape still matters for other things — occupied bandwidth, interference between neighbouring symbols, resolution in radar — but not for single-pulse detectability.

## The math

### Level 1 — the result
Input $x(t)=s(t)+w(t)$, where $s(t)$ is a known pulse (V) of energy $E=\int|s(t)|^2dt$ (J, into 1 Ω) and $w(t)$ is white Gaussian noise with two-sided PSD $N_0/2$ (W/Hz). Pass $x$ through a linear time-invariant filter $h(t)$ and sample at $t=T$:
$$y(T) = \underbrace{\int s(\tau)h(T-\tau)\,d\tau}_{\text{signal } y_s(T)} + \underbrace{\int w(\tau)h(T-\tau)\,d\tau}_{\text{noise } y_n(T)}.$$
Define output SNR $=|y_s(T)|^2/E[|y_n(T)|^2]$. The maximum over all $h$ is
$$\mathrm{SNR}_{max}=\frac{2E}{N_0},\qquad\text{achieved by } h(t)=k\,s^*(T-t).$$

### Level 1½ — "correlate with the known pulse", algebra only
The integral above is a weighted sum. Write it with samples and the result follows from two lines of arithmetic.
- **Set-up.** The pulse is N samples of amplitude A. The noise samples are independent with variance σ². Multiply each received sample by the known pulse sample and add them up.
- **Signal adds in amplitude, noise adds in power.** The signal part of the sum is NA. The noise part has variance Nσ². So the output SNR is (NA)²/(Nσ²) = N·A²/σ², which is N times the per-sample SNR, i.e. a gain of 10 log N dB.
- **The same thing as 2E/N0.** The pulse energy (into 1 Ω) is E = NA²/f_s. White noise of two-sided density N0/2 sampled at f_s has σ² = (N0/2)·f_s. Substituting gives N·A²/σ² = 2E/N0, the Level 1 result. Budgets in this KB quote E/N0 instead (see [canonical values](../00-math-foundations/canonical-values-and-conventions.md#level-2--where-each-factor-of-two-comes-from)).
- **Any mismatch costs SNR.** Summing over twice the pulse length adds N more noise samples and no signal, so the SNR falls by 3 dB. A wrongly shaped template loses SNR in the same way.

*Worked number (verified, `tools/verify/s18b_level15_numbers.py`, including a Monte Carlo of the sum).* A pulse of 16 samples with A = 1 V in noise of σ = 2 V has a per-sample SNR of 0.25 (−6.0 dB). The correlator output SNR is 16 × 0.25 = 4, i.e. **+6.0 dB** (a gain of 12.0 dB). Summing 32 samples instead gives 2 (+3.0 dB): **3.0 dB lost** to the mismatched window.

### Level 2 — derivation (Cauchy–Schwarz)
In the frequency domain, with $S(f)$ and $H(f)$ the Fourier transforms,
$$y_s(T)=\int_{-\infty}^{\infty}H(f)S(f)e^{j2\pi fT}\,df,\qquad E[|y_n|^2]=\frac{N_0}{2}\int_{-\infty}^{\infty}|H(f)|^2\,df.$$
The Cauchy–Schwarz inequality $\left|\int a\,b\,df\right|^2\le\int|a|^2df\int|b|^2df$ with $a=H$ and $b=Se^{j2\pi fT}$ gives
$$\mathrm{SNR}=\frac{\left|\int HSe^{j2\pi fT}df\right|^2}{\frac{N_0}{2}\int|H|^2df}\le\frac{\int|H|^2df\int|S|^2df}{\frac{N_0}{2}\int|H|^2df}=\frac{2}{N_0}\int|S(f)|^2df=\frac{2E}{N_0}$$
(Parseval for the last step). Equality holds iff $a\propto b^*$: $H(f)=k\,S^*(f)e^{-j2\pi fT}$, whose inverse transform is $h(t)=k\,s^*(T-t)$ [1], [2 §4.2], [3].

Two properties follow at once:
- **Causality/realisability:** $h(t)$ is zero for $t<0$ only if $s(t)$ is zero for $t>T$; you must wait until the whole pulse has arrived before sampling.
- **Output waveform = autocorrelation.** With $k=1$, $y_s(t)=\int s(\tau)s^*(\tau-(t-T))\,d\tau=R_s(t-T)$. The peak value is $R_s(0)=E$. The output does *not* look like the input pulse — the matched filter is a detector, not a waveform-preserving filter.

**Correlator equivalence.** At the sampling instant,
$$y(T)=\int x(\tau)\,s^*(\tau)\,d\tau,$$
which is multiply-and-integrate. For a rectangular pulse this is an **integrate-and-dump**. Checked numerically: convolution with the reversed pulse at $t=T$ equals the correlator to machine precision.

**Discrete time.** For samples $x[n]$ and a template $s[n]$ of length $L$, the matched FIR filter has taps $h[n]=s^*[L-1-n]$; `np.convolve(x, np.conj(s[::-1]))` or `np.correlate(x, s)` compute the same thing. Output SNR at the peak is $\sum|s[n]|^2/\sigma^2$ where $\sigma^2$ is the per-sample complex noise variance — the discrete version of $E/N_0$ in complex-baseband units (see the convention note below).

**Convention trap: 2E/N0 or E/N0?** For a *real* passband pulse with energy $E$ and two-sided noise PSD $N_0/2$, the peak SNR is $2E/N_0$. In *complex baseband*, if $s(t)=\mathrm{Re}\{\tilde s(t)e^{j2\pi f_ct}\}$, the complex envelope has energy $\tilde E=2E$, and with noise PSD $N_0/2$ on each of I and Q the peak SNR is written $\tilde E/N_0$ — the same number. **KB convention:** "SNR" in link and radar budgets means $E/N_0$ (the radar χ, as in the [radar range equation](../11-radar/radar-range-equation.md)); $2E/N_0$ is used only as the real-passband matched-filter peak ratio on this page. Both are verified in the script; do not mix the two conventions in one calculation.

**From SNR to error probability — why the matched filter gives the BER formulas.** For binary antipodal signals $\pm s(t)$ the MF output at $T$ is $\pm E+n$ with $\mathrm{var}(n)=EN_0/2$ (using $k=1$), so $P_b=Q\big(E/\sqrt{EN_0/2}\big)=Q(\sqrt{2E/N_0})$ — the BPSK result. More generally for two signals $s_0,s_1$, the optimum filter is matched to the difference $s_1-s_0$, whose energy is $d^2$ (squared Euclidean distance), giving $P_b=Q(\sqrt{d^2/2N_0})$ [2 §4.2], [4].

### Level 2b — likelihoods, ML and MAP decisions
With $M$ possible signals $s_m(t)$ and orthonormal basis functions $\phi_j(t)$ spanning them ($D$ dimensions), project the received signal: $r_j=\int r(t)\phi_j(t)dt$. In AWGN the $r_j$ are independent Gaussians with means $s_{mj}$ and variance $N_0/2$, and the noise outside the signal space is independent of everything that matters — so the vector $\mathbf r$ is a **sufficient statistic** (the theorem of irrelevance) [2 §4.1], [5]. The likelihood is
$$p(\mathbf r\mid m)=(\pi N_0)^{-D/2}\exp\!\left(-\frac{\|\mathbf r-\mathbf s_m\|^2}{N_0}\right).$$
- **Maximum likelihood (ML):** choose $m$ minimising $\|\mathbf r-\mathbf s_m\|^2$, i.e. maximising $\langle\mathbf r,\mathbf s_m\rangle-E_m/2$: *correlate, subtract half the energy, pick the largest.* For equal-energy signals, just pick the largest correlation.
- **MAP** with priors $p_m$: maximise $\langle\mathbf r,\mathbf s_m\rangle-E_m/2+\tfrac{N_0}{2}\ln p_m$. The threshold moves toward the less likely symbol; MIT 6.02 works this out for bipolar signalling with unequal priors [6 §9.4].

### Level 3 — generalisations and limits
**Coloured noise.** If the noise PSD $S_n(f)$ is not flat, the SNR-maximising filter is
$$H(f)=k\,\frac{S^*(f)}{S_n(f)}e^{-j2\pi fT},\qquad \mathrm{SNR}_{max}=\int\frac{|S(f)|^2}{S_n(f)}df.$$
Interpretation: a whitening filter $1/\sqrt{S_n(f)}$ followed by a filter matched to the whitened pulse. Frequencies where the noise is strong are de-emphasised. This is relevant when a strong narrowband interferer sits inside your channel [1], [7].

**Detection (is a signal there at all?).** Binary hypothesis test $H_0$: $r=w$; $H_1$: $r=s+w$. The Neyman–Pearson lemma says the most powerful test at a given false-alarm probability $P_{FA}$ compares the likelihood ratio with a threshold; in AWGN with a known signal this reduces to thresholding the matched-filter output [7].
- *Known signal including phase (coherent):* normalise the MF output so noise has unit variance; the signal term is $\sqrt{2E/N_0}$. Threshold $\gamma=Q^{-1}(P_{FA})$, $P_D=Q\big(Q^{-1}(P_{FA})-\sqrt{2E/N_0}\big)$.
- *Unknown phase (envelope / non-coherent):* compute $|y(T)|$ from I and Q correlators. Under $H_0$ the envelope is Rayleigh, so $P_{FA}=e^{-\gamma^2/2}$, $\gamma=\sqrt{-2\ln P_{FA}}$ (unit per-rail noise). Under $H_1$ it is Rician, giving $P_D=Q_1(\sqrt{2E/N_0},\gamma)$ with $Q_1$ the Marcum Q-function [7], [8].
Both are verified by Monte-Carlo; the non-coherent penalty at $P_D=0.9$, $P_{FA}=10^{-6}$ is only ≈ 0.6 dB. This is the same mathematics as radar detection and CFAR ([detection theory](../11-radar/detection-theory-cfar.md)).

**Pulse compression.** A linear-FM (chirp) pulse of duration $T$ sweeping bandwidth $B$ has an autocorrelation of main-lobe width ≈ $1/B$ ($-3$ dB width $0.886/B$, checked numerically for $TB=50$). The matched filter therefore turns a long, low-peak-power pulse into a short, high-peak one; compression ratio ≈ $TB$. Energy and hence detection SNR are unchanged ($2E/N_0$); what improves is *time resolution* (radar range resolution $c/2B$). Binary phase codes (Barker, m-sequences) do the same with discrete chips [9], [10]. Sidelobes (−13.3 dB for an unweighted chirp) and Doppler sensitivity are the price; see [ambiguity function](../11-radar/ambiguity-function-waveforms.md).

**Where "optimal" stops being true.** The matched filter maximises SNR at one instant for one known pulse in additive Gaussian noise. It is not optimal against ISI (a sequence of overlapping pulses — see [equalisation](pulse-shaping-isi.md)), against unknown frequency offsets larger than about $1/(2T)$, in impulsive noise, or when the pulse is distorted by multipath (then the "right" template is the received, distorted pulse — the RAKE receiver idea).

## Design equations & rules of thumb

| Equation | When valid | Typical values / notes |
|---|---|---|
| $h(t)=s^*(T-t)$; FIR taps $h[n]=s^*[L-1-n]$ | known pulse, white noise | RRC TX ⇒ RRC RX |
| $\mathrm{SNR}_{peak}=2E/N_0$ (real) $=\tilde E/N_0$ (complex envelope) | any pulse shape | E = pulse energy |
| $y_s(t)=R_s(t-T)$, peak $E$ | matched filter output | output shape = autocorrelation |
| RC filter on rect pulse: best $B_{3dB}T=0.20$, loss 0.89 dB | single-pole RC | crystal/LC IF approx. |
| Timing loss, rectangular pulse: $20\log_{10}(1-|\tau|/T)$ | integrate-and-dump | 0.9 dB at 0.1T, 2.5 dB at 0.25T, 6 dB at 0.5T |
| CFO loss of coherent correlator: $20\log_{10}|\mathrm{sinc}(\Delta f\,T)|$ | length-$T$ coherent integration | 0.6 dB at $\Delta fT=0.2$, 3 dB at $\Delta fT=0.44$, null at $\Delta fT=1$ |
| $P_D=Q(Q^{-1}(P_{FA})-\sqrt{2E/N_0})$ | coherent detection | 15.6 dB for 0.9 / 1e-6 |
| $P_D=Q_1(\sqrt{2E/N_0},\sqrt{-2\ln P_{FA}})$ | non-coherent detection | 16.2 dB for 0.9 / 1e-6 |
| Compressed width ≈ $1/B$; gain ≈ $TB$ | LFM chirp | TB = 100 → 20 dB |
| $H(f)=S^*(f)e^{-j2\pi fT}/S_n(f)$ | coloured noise | whiten then match |

## Worked examples

### Example 1 — Energy per bit of a weak telemetry signal
Received power $P=-118$ dBm $=1.58\times10^{-15}$ W at 10 kbit/s BPSK ($T_b=100$ µs). Bit energy $E_b=PT_b=1.58\times10^{-19}$ J. With NF = 6 dB, $N_0=kT_0\cdot10^{0.6}=4.0\times10^{-21}\cdot3.98=1.59\times10^{-20}$ W/Hz. $E_b/N_0=9.9$ (9.96 dB) and the matched-filter peak SNR is $2E_b/N_0 = 19.9$ (13.0 dB). The receiver never "sees" a positive SNR in a wide bandwidth, but after collecting 100 µs of energy the decision variable stands 4.5 σ clear of the threshold — BER ≈ $Q(4.46)\approx 4\times10^{-6}$.

### Example 2 — Detecting a 32-bit sync word
A downlink frame starts with a 32-bit sync word, BPSK, at the edge of coverage where $E_b/N_0=6$ dB. Correlating over all 32 bits gives $E=32E_b$ → $2E/N_0=10\log_{10}(2\cdot32)+6=24.1$ dB. With a non-coherent (envelope) detector and a threshold for $P_{FA}=10^{-6}$ per test position, $P_D$ is essentially 1 (the requirement for 0.9 is 16.2 dB). If the receiver tests $10^4$ positions per second, $P_{FA}=10^{-6}$ means one false trigger every ≈ 100 s, which a CRC then rejects (see [packet framing](packet-framing-protocols.md)).

But add **frequency offset**: a 433 MHz rocket at 300 m/s gives 433 Hz of Doppler, plus ±10 ppm crystals on both ends (up to ±8.7 kHz combined). Over the 3.2 ms sync word, a 1 kHz residual offset costs 24.7 dB (script §5) — the 24 dB of margin vanishes. Remedies: (a) coarse frequency correction before correlation ([synchronisation](synchronization-carrier-timing.md)); (b) split the 32 bits into 4 segments of 8 bits (0.8 ms each, combined non-coherently; the per-segment loss at 1 kHz is still $20\log_{10}|\mathrm{sinc}(0.8)|\approx12.6$ dB — 1 kHz needs even shorter segments, and non-coherent combining itself costs ≈ 1–2 dB); (c) a bank of correlators at frequency hypotheses spaced ≈ $1/(2T)$ = 156 Hz; (d) use a non-coherent modulation (FSK) whose detector tolerates offset up to a fraction of the tone spacing.

### Example 3 — Cost of a non-matched IF filter
A simple receiver whose only post-detection selectivity is a single-pole low-pass, receiving rectangular-pulse data. The single-pole analysis (script §2) says the best you can do is a 0.89 dB loss at $B_{3dB}\approx0.2R_b$. For $BT\gg1$ the loss relative to the matched filter tends to $1/(\pi B T)$, because the filter's noise bandwidth is $\pi B/2$ while the matched filter's is $1/(2T)$. A filter with $B_{3dB}=2R_b$ (common in cheap receivers to tolerate frequency drift) therefore loses $10\log_{10}(2\pi)\approx8$ dB — about 7 dB more than the optimum single pole. Frequency tolerance and matched filtering pull in opposite directions — which is why frequency correction lets you narrow the filter.

### Example 4 — Pulse compression numbers (radar tie-in)
LFM pulse: $T=10$ µs, $B=10$ MHz, $TB=100$. Compressed −3 dB width ≈ $0.886/B=89$ ns; range resolution $c/2B=15$ m instead of $cT/2=1.5$ km for an uncompressed 10 µs pulse; peak-power reduction for the same detection range ≈ 20 dB. Details in [pulse compression](../11-radar/pulsed-radar-and-pulse-compression.md).

### Example 5 — LoRa as a matched-filter bank
A LoRa SF7 symbol is one of 128 cyclically shifted chirps. Multiplying by a down-chirp ("dechirping") turns each candidate into a pure tone at a different frequency; a 128-point FFT is then 128 correlators in parallel, one per symbol — a bank of matched filters, one per hypothesis, followed by "pick the largest magnitude": the non-coherent M-ary orthogonal detector of [the BER page](ber-ebn0-and-shannon.md). See [chirp spread spectrum](spread-spectrum-dsss-fhss-css.md).

## Practical notes
- **Sample at the peak.** The matched filter only delivers $2E/N_0$ at the right instant. Symbol timing recovery (Gardner, Mueller–Müller; see [synchronisation](synchronization-carrier-timing.md)) exists to find it. Oversample (≥ 2–4 samples/symbol) so a fractional-delay interpolator can hit the peak.
- **RRC in both ends.** With RRC pulse shaping the receive RRC is simultaneously the matched filter and the second half of the Nyquist (zero-ISI) response — both goals met by one filter ([pulse shaping](pulse-shaping-isi.md)). Mismatched roll-off between TX and RX (e.g. 0.35 vs 0.5) produces small ISI and ≈ 0.1–0.3 dB loss.
- **FIR length.** Truncating an RRC to ±4–8 symbols keeps mismatch loss < 0.1 dB; shorter filters raise both loss and spectral sidelobes.
- **Fixed point.** Correlators in an MCU/FPGA need accumulator headroom of $\log_2 L$ bits over the input width.
- **Correlating against hard-limited signals** (1-bit ADC or sign of samples) costs ≈ 2 dB (π/2 in SNR) at low SNR — the same number as hard-decision decoding loss.
- **Frequency offset** is the usual killer of long coherent correlations: keep $\Delta f\,T\ll0.5$ (< 0.2 for < 0.6 dB loss).

## Common mistakes & misconceptions
- **"The matched filter preserves the pulse shape."** It maximises SNR at one instant; its output is the pulse's autocorrelation (a triangle for a rectangular pulse).
- **Forgetting the conjugate** for complex baseband templates. Correlating with $s$ instead of $s^*$ gives garbage for any template with a phase slope (chirps, QPSK sequences).
- **Using $E/N_0$ and $2E/N_0$ interchangeably.** Pick the real-passband or complex-baseband convention and stick to it; a factor-of-two slip is a 3 dB error.
- **Believing a wider bandwidth pulse is more detectable.** At fixed energy, bandwidth changes resolution and robustness to interference, not detection SNR.
- **Matched filtering a pulse that multipath has already smeared** with the clean template — the loss can be several dB; equalise or use a RAKE/channel-matched template.
- **Ignoring frequency offset in long preamble correlators** — see Example 2.
- **Setting a detection threshold by eye.** Derive it from the desired $P_{FA}$ and the measured noise level; adapt it if the noise floor moves (CFAR idea).

## How to simulate / verify
- **`tools/verify/comms_matched_filter.py`** (≈ 5 s): (1) output SNR = 2E/N0 for rectangular, half-sine and windowed-sinc pulses, convolution = correlator; (2) RC-filter mismatch optimum $B T=0.20$, loss 0.89 dB; (3) LFM compression width 0.886/B and complex-baseband SNR convention; (4) coherent and non-coherent $P_D$ vs Monte-Carlo; (5) CFO and timing-offset losses. All PASS.
- **Python sketch:**
  ```python
  y = np.correlate(rx, template, mode='valid')     # np.correlate conjugates the 2nd argument
  peak = np.argmax(np.abs(y)); snr_est = np.abs(y[peak])**2 / np.var(y[far_from_peak])
  ```
- **GNU Radio:** *Correlation Estimator* (sync-word/preamble detection with threshold and timing/phase estimates), *Root Raised Cosine Filter* taps via `firdes.root_raised_cosine`, *FFT Filter* for long templates.
- **Bench check:** transmit a known sync word from a signal generator or SDR; plot the correlator magnitude; verify the peak height tracks $\sqrt{E}$ as you step attenuation, and that sidelobes are where the autocorrelation of your word predicts.

## Open questions / gaps
- Multi-segment (non-coherent combining) correlator loss vs segment length under Doppler, with exact formulas, would help rocket preamble design; currently only the single-segment sinc loss is derived here (see also [synchronisation](synchronization-carrier-timing.md)).
- Hard-limiting correlation loss (≈ 2 dB) is stated from the standard low-SNR result; not independently simulated here.

## Sources
1. G. L. Turin, "An introduction to matched filters," *IRE Trans. Information Theory* IT-6(3):311–329, 1960 — derivation, coloured-noise form, radar applications. (peer-reviewed)
2. J. G. Proakis and M. Salehi, *Digital Communications*, 5th ed., McGraw-Hill, 2008 — §4.1 (signal space, sufficient statistics), §4.2 (optimum receiver, matched filter, correlator). (textbook)
3. D. O. North, "An analysis of the factors which determine signal/noise discrimination in pulsed-carrier systems," RCA Labs Report PTR-6C, 1943; reprinted *Proc. IEEE* 51(7):1016–1027, 1963 — original matched filter. (peer-reviewed, historical)
4. B. Sklar, *Digital Communications*, 2nd ed., Prentice Hall, 2001 — ch. 3 (matched filter, correlator, "2E/N0"). (textbook)
5. J. M. Wozencraft and I. M. Jacobs, *Principles of Communication Engineering*, Wiley, 1965 — signal-space and theorem of irrelevance. (textbook)
6. MIT 6.02, Fall 2012, lecture notes ch. 9 "Noise" §9.4 (BER with unequal priors, optimal threshold). https://ocw.mit.edu/courses/6-02-introduction-to-eecs-ii-digital-communication-systems-fall-2012/ (lecture notes)
7. S. M. Kay, *Fundamentals of Statistical Signal Processing, Vol. II: Detection Theory*, Prentice Hall, 1998 — Neyman–Pearson, matched filter detector, generalised matched filter, envelope detection. (textbook)
8. H. L. Van Trees, *Detection, Estimation, and Modulation Theory, Part I*, Wiley, 1968 (reprinted 2001) — likelihood-ratio tests, random-phase detection and Marcum Q. (textbook)
9. M. A. Richards, *Fundamentals of Radar Signal Processing*, 2nd ed., McGraw-Hill, 2014 — ch. 4 (matched filter, LFM compression, ≈ −13 dB range sidelobes). (textbook)
10. M. I. Skolnik, *Introduction to Radar Systems*, 3rd ed., McGraw-Hill, 2001 — §5.2 (matched filter, mismatch loss of simple filters). (textbook)
11. M. Lichtman, *PySDR: A Guide to SDR and DSP using Python*, "Synchronization" and "Pulse Shaping" chapters, https://pysdr.org — practical correlation/frame-sync with Barker and Zadoff–Chu sequences. (online textbook)
