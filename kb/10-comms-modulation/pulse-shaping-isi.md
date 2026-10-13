---
title: Pulse shaping, intersymbol interference and equalisation
domain: 10-comms-modulation
slug: pulse-shaping-isi
tags: [pulse-shaping, ISI, Nyquist-criterion, raised-cosine, root-raised-cosine, roll-off, eye-diagram, equalisation, zero-forcing, MMSE, DFE, LMS, delay-spread, partial-response]
prerequisites:
  - ../00-math-foundations/fourier-series-and-transform.md
  - ../00-math-foundations/linear-systems-convolution.md
  - matched-filter-detection.md
related:
  - digital-modulation-psk-qam-fsk.md
  - ber-ebn0-and-shannon.md
  - synchronization-carrier-timing.md
  - ofdm.md
  - ../09-propagation-link-budget/multipath-fading-doppler.md
  - ../09-propagation-link-budget/two-ray-ground-reflection.md
  - ../14-sdr-dsp/digital-filters-fir-iir.md
  - ../14-sdr-dsp/multirate-dsp-decimation-cic.md
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Pulse shaping, intersymbol interference and equalisation

## Questions this page answers
- Why can't I just send rectangular pulses?
- What is intersymbol interference (ISI) and where does it come from?
- What is the Nyquist ISI criterion, and what is the minimum bandwidth for a given symbol rate?
- What is the difference between a raised-cosine and a root-raised-cosine filter, and why do we split it between TX and RX?
- How does the roll-off factor β trade bandwidth against timing sensitivity and PAPR?
- How long should my RRC FIR filter be?
- How do I read an eye diagram?
- Does my rocket telemetry link need an equaliser?
- What are zero-forcing, MMSE and decision-feedback equalisers, and which should I use?

## TL;DR
- A pulse shape $p(t)$ gives **zero ISI** iff $p(nT)=0$ for all $n\neq0$, equivalently iff its spectrum *folded* at multiples of $1/T$ is flat: $\sum_k P(f-k/T)=T$ (**Nyquist criterion**, Nyquist 1928 [1]). Minimum bandwidth: $1/(2T)$ one-sided baseband, i.e. an RF width equal to the symbol rate.
- **Raised cosine (RC)** with roll-off β meets it with RF occupied width **$(1+\beta)R_s$** (one-sided baseband $(1+\beta)R_s/2$). Typical β = 0.2–0.5 (wireless), 0.35 (satellite classic), 0.22 (DVB-S), 0.05–0.2 (modern DVB-S2X).
- Split it as **root-raised-cosine (RRC) at TX and RRC at RX**: the RX RRC is then both the matched filter (max SNR, [matched filter](matched-filter-detection.md)) and the second half of the zero-ISI response. RC at both ends is *wrong* (gives RC², which has ISI).
- **Filter length:** truncating an RRC (β = 0.35) to ±4 symbols leaves ISI at −36 dB (after RRC⊗RRC) and out-of-band power −43 dB; ±8 symbols → −50 dB / −50 dB; ±16 → −59 / −64 dB (verified). Small β needs longer filters.
- **Timing sensitivity:** worst-case binary eye opening at 0.1 T sampling error is 61 % (β = 0.2), 72 % (0.35), 79 % (0.5), 90 % (1.0) — larger β, more forgiving timing, more bandwidth, lower PAPR.
- **Channel ISI** appears when multipath delay spread approaches ≈ 10 % of a symbol. A rocket-to-ground link (ground-reflection delay ≈ tens of ns) at ≤ 100 kbaud needs **no equaliser**; the reflection causes *fading*, not ISI. Wideband links (≥ 1 Mbaud, urban multipath) do.
- **Equalisers:** zero-forcing inverts the channel but amplifies noise (3.2 dB in the worked example); MMSE balances ISI and noise (always ≥ ZF); a DFE cancels post-cursor ISI from past decisions with no noise enhancement (best of the three here: 1.1e-4 vs 6.7e-4 MMSE vs 1.0e-3 ZF, vs 3.1e-2 unequalised). OFDM sidesteps the problem ([OFDM](ofdm.md)).

## Intuition (no math)
A rectangular pulse has a sharp edge, and sharp edges need infinite bandwidth (its spectrum is a sinc that decays only as $1/f$). Transmitted as-is, a rectangular-pulse PSK signal splashes energy far into neighbouring channels — the 99 % bandwidth of rectangular BPSK is about 20 times the bit rate ([digital modulation](digital-modulation-psk-qam-fsk.md)). So we filter. But filtering smears each pulse in time, so it overlaps its neighbours: **intersymbol interference**. At the moment the receiver samples symbol $n$, the tails of symbols $n-1$, $n+1$, … add to (or subtract from) the value, shrinking the margin against noise or causing errors outright.

Nyquist's insight: overlap is fine as long as every other pulse is passing through **zero** at the exact sampling instant of each symbol. A sinc pulse does that (zeros every $T$) and uses the least possible bandwidth, but its tails decay so slowly that a tiny timing error lets many tails add up. The raised-cosine family adds a little extra bandwidth (the "roll-off" or "excess bandwidth" β) to make the tails die off much faster, so small timing errors are tolerable and the filter can be short.

Splitting the raised cosine into two square-root halves puts half the shaping in the transmitter (to limit the spectrum on air) and half in the receiver (to reject noise optimally). Neither half alone is ISI-free; the cascade is.

ISI can also be caused by the channel: an echo arriving a sizeable fraction of a symbol late adds a delayed copy of the previous symbol. An **equaliser** is a filter at the receiver that tries to undo this. Whether you need one depends on the echo delay relative to the symbol duration: nanosecond echoes don't matter to 100 µs symbols.

## The math

### Level 1 — the formulas
Symbol period $T=1/R_s$; roll-off $0\le\beta\le1$.

**Raised-cosine impulse response** (normalised to $p(0)=1$):
$$p_{RC}(t)=\mathrm{sinc}\!\left(\frac tT\right)\frac{\cos(\pi\beta t/T)}{1-(2\beta t/T)^2},\qquad \mathrm{sinc}(x)=\frac{\sin\pi x}{\pi x}.$$
At $|t|=T/(2\beta)$ the expression is $0/0$; its limit is $\frac\pi4\mathrm{sinc}\big(\frac1{2\beta}\big)$.

**Raised-cosine spectrum** (one-sided baseband, $f\ge0$):
$$P_{RC}(f)=\begin{cases}T,&0\le f\le\frac{1-\beta}{2T}\\[2pt]\frac T2\left[1+\cos\!\left(\frac{\pi T}{\beta}\Big(f-\frac{1-\beta}{2T}\Big)\right)\right],&\frac{1-\beta}{2T}<f\le\frac{1+\beta}{2T}\\[2pt]0,&f>\frac{1+\beta}{2T}\end{cases}$$
Bandwidth: **baseband one-sided $(1+\beta)/(2T)$; RF (or complex-baseband two-sided) width $(1+\beta)/T$.** PySDR writes $BW=R_s(\beta+1)$ and explicitly means the two-sided width [2].

**Root-raised cosine:** $|P_{RRC}(f)|=\sqrt{P_{RC}(f)}$, and
$$p_{RRC}(t)=\frac{\sin\!\big(\pi\frac tT(1-\beta)\big)+4\beta\frac tT\cos\!\big(\pi\frac tT(1+\beta)\big)}{\pi\frac tT\left[1-\left(4\beta\frac tT\right)^2\right]}\quad(\text{up to scaling}),$$
with limits $1-\beta+4\beta/\pi$ at $t=0$ and $\frac{\beta}{\sqrt2}\left[(1+\frac2\pi)\sin\frac{\pi}{4\beta}+(1-\frac2\pi)\cos\frac{\pi}{4\beta}\right]$ at $|t|=T/(4\beta)$ [3 §9.2], [4].

### Level 2 — deriving the Nyquist criterion
Received, sampled signal (after all filtering, overall pulse $p(t)$, noise $n$):
$$y(kT)=a_k\,p(0)+\underbrace{\sum_{m\neq k}a_m\,p\big((k-m)T\big)}_{\text{ISI}}+n_k.$$
Zero ISI requires $p(nT)=\delta_n$ (Kronecker delta, with $p(0)=1$). Sampling $p(t)$ at rate $1/T$ multiplies it by an impulse train; in the frequency domain that *periodises* the spectrum:
$$\sum_n p(nT)\,\delta(t-nT)\ \longleftrightarrow\ \frac1T\sum_k P\!\left(f-\frac kT\right).$$
The left side equals $\delta(t)$ exactly when $p(nT)=\delta_n$, whose transform is 1. Hence
$$\boxed{\ \sum_{k=-\infty}^{\infty}P\!\left(f-\frac kT\right)=T\quad\text{for all }f\ }$$
[1], [3 §9.2], [5]. Consequences:
- If $P(f)=0$ for $|f|>1/(2T)$, the only solution is the ideal brick wall $P=T\,\mathrm{rect}(fT)$ ↔ sinc pulse. So **$1/(2T)$ is the minimum baseband bandwidth** — two real symbols per second per hertz (Shannon's $2BT$ dimensions again).
- With a little extra bandwidth, any spectrum whose roll-off is *odd-symmetric* about $1/(2T)$ ("vestigial symmetry") works. The raised cosine is the smooth member of this family; its folded spectrum is flat (checked to 1e-15 in the script for β = 0 … 1).

**Why split into RRC + RRC.** Transmit filter $G_T(f)$, channel flat, receive filter $G_R(f)$. Matched filtering requires $G_R=G_T^*$; zero ISI requires $G_TG_R=P_{RC}$. Both hold with $|G_T|=|G_R|=\sqrt{P_{RC}}$ — the RRC. The RRC's own impulse response does *not* have zeros at $nT$.

**Tail decay and timing sensitivity.** The sinc ($\beta=0$) tails decay as $1/t$; the sum of their magnitudes at a timing offset diverges (worst-case eye closes for *any* offset with infinitely long data). The RC tails decay as $1/t^3$ for $\beta>0$, making the worst-case ISI sum finite. The worst-case (peak-distortion) eye opening at offset $\tau$ is
$$\text{eye}(\tau)=p(\tau)-\sum_{n\neq0}|p(nT+\tau)|,$$
computed in the script: β = 0.35 gives 1.00, 0.72, 0.41, 0.10 at τ = 0, 0.1T, 0.2T, 0.3T. Random data is kinder than the worst case; the eye diagram shows the distribution.

**Eye diagram.** Overlay the received waveform in windows of 2 symbols triggered at the symbol clock. Vertical opening at the best instant = noise margin; horizontal opening = timing margin; slope of the eye sides = sensitivity to timing error; thickness of the crossing region = timing jitter / ISI [2], [6].

### Level 3 — channel ISI and equalisation
**Channel model.** A multipath channel with discrete echoes, after matched filtering and symbol-rate sampling, becomes an FIR filter $c_0,c_1,\dots,c_L$ acting on the symbols: $y_k=\sum_{j}c_ja_{k-j}+n_k$. Rules of thumb (Rappaport [7]): ISI is negligible when the rms delay spread $\tau_{rms}\lesssim0.1T$; the coherence bandwidth $B_c\approx1/(5\tau_{rms})$ — if the signal bandwidth exceeds $B_c$ the channel is frequency-selective and needs equalisation (or OFDM).

**Zero-forcing (ZF) linear equaliser.** Choose FIR taps $w$ so that $w*c\approx\delta$ (delayed): in the frequency domain $W=1/C$. Removes ISI completely (for infinite length) but where $|C(f)|$ is small it multiplies noise by $1/|C|^2$ — **noise enhancement**. For the script's channel ($c=[0.857,0,0.514]$, a −4.4 dB echo 2 symbols late) the 21-tap ZF enhances noise by 3.2 dB.

**MMSE linear equaliser.** Minimise $E|w^Hy-a_{k-D}|^2$. Solution (Wiener–Hopf):
$$w=\big(\mathbf H\mathbf H^T+\sigma^2\mathbf I\big)^{-1}\mathbf H\,\mathbf e_D,$$
with $\mathbf H$ the channel convolution matrix over the equaliser span and $\mathbf e_D$ selecting the decision delay. As $\sigma^2\to0$ it becomes ZF; at high noise it backs off from inverting deep notches. Always at least as good as ZF in MSE and usually in BER.

**Decision-feedback equaliser (DFE).** A feed-forward filter handles pre-cursor ISI; a feedback filter subtracts the post-cursor ISI computed from *past decisions*: $\hat a_k=\mathrm{dec}\{\sum w_iy_{k-i}-\sum_{j\ge1}b_j\hat a_{k-j}\}$. Because the feedback uses noiseless decisions, it causes no noise enhancement; the price is error propagation after a wrong decision. In the example the DFE (feedback = channel post-cursors) reaches 1.1e-4 vs 6.7e-4 for MMSE and 1.0e-3 for ZF, against a matched-filter bound (all path energy collected, no ISI) of 3.9e-6 at Eb/N0 = 10 dB.

**Maximum-likelihood sequence estimation (MLSE).** The Viterbi algorithm over the channel's state (previous $L$ symbols) is optimal for known ISI [8]; complexity $M^L$ per symbol. Used in GSM receivers.

**Adaptive equalisers.** Channels change; the taps are learned from a training sequence (preamble) and tracked in decision-directed mode with LMS, $w\leftarrow w+\mu\,e_k^*\,\mathbf y_k$ (Widrow–Hoff), or RLS for faster convergence. Fractionally spaced (T/2) equalisers are insensitive to sampling phase [9].

**Deliberate ISI.** Partial-response signalling (duobinary: $p(t)$ spans two symbols with known, controlled ISI) and GMSK (Gaussian filter with BT < 1 spreads each bit over ≈ $1/BT$ bits) trade a little SNR or receiver complexity for narrower spectra. Faster-than-Nyquist signalling does the same beyond the Nyquist rate.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| Zero ISI ⟺ $p(nT)=\delta_n$ ⟺ $\sum_kP(f-k/T)=T$ | overall TX·channel·RX response | Nyquist 1928 |
| Min. bandwidth $1/(2T)$ baseband; $R_s$ RF width | β = 0 (sinc) | unrealisable |
| RC/RRC occupied RF width $(1+\beta)R_s$ | RC/RRC | β = 0.35 → 1.35 Rs |
| RRC span ±4 / ±8 / ±16 symbols → ISI −36 / −50 / −59 dB | β = 0.35, after RRC⊗RRC | ±6–8 is typical |
| Worst-case eye at 0.1 T offset: 61/72/79/90 % | β = 0.2/0.35/0.5/1.0 | binary |
| ISI negligible if $\tau_{rms}<0.1T$ | multipath | rocket link: ns vs µs |
| $B_c\approx1/(5\tau_{rms})$ | 50 % correlation coherence BW | Rappaport |
| ZF noise enhancement $\propto\int 1/|C(f)|^2$ | linear ZF | 3.2 dB in example |
| MMSE $w=(HH^T+\sigma^2I)^{-1}He_D$ | linear MMSE | ≥ ZF |
| LMS $w\leftarrow w+\mu e^*y$ | adaptive | μ ≪ 1/(taps·power) |

## Worked examples

### Example 1 — Bandwidth and taps for a 20 kb/s QPSK downlink
$R_s=10$ kbaud. With β = 0.35 the RF occupied width is $1.35\times10=13.5$ kHz (6.75 kHz each side of the carrier); with β = 0.2, 12 kHz but ≈ 1.3 dB more PAPR ([digital modulation](digital-modulation-psk-qam-fsk.md)) and a tighter timing budget. At 8 samples/symbol and span ±8 symbols the RRC has $2\cdot8\cdot8+1=129$ taps; at 80 ksample/s that is ≈ 10 M multiply-accumulates per second for a real filter on each of I and Q — trivial for an ESP32-S3 or any SDR host. Use a polyphase interpolator to avoid multiplying zeros ([multirate DSP](../14-sdr-dsp/multirate-dsp-decimation-cic.md)).

### Example 2 — Does a rocket link need an equaliser?
Rocket at 10 km altitude, ground station 5 km downrange with its antenna 5 m above flat ground. Direct path $\sqrt{5000^2+9995^2}=11\,175.9$ m, ground-reflected path $\sqrt{5000^2+10\,005^2}=11\,184.8$ m: extra path 8.9 m ≈ **30 ns** delay. At 10 kbaud ($T=100$ µs) the echo is $3\times10^{-4}T$ — no ISI at all. What the reflection *does* do is add a copy with a phase that changes as the rocket moves, causing slow fading nulls ([two-ray](../09-propagation-link-budget/two-ray-ground-reflection.md)). Even at 1 Mbaud (1 µs) the echo is 3 % of a symbol. Conclusion: equalisers are irrelevant for rocket telemetry; fade margin, diversity and FEC with interleaving are what matter ([channel coding](channel-coding-fec.md)).

### Example 3 — Timing budget from the eye
With β = 0.35 and a requirement that worst-case ISI costs ≤ 3 dB (eye ≥ 0.71), the sampling instant must be within ≈ ±0.1 T of ideal (script: 0.717 at 0.1 T). At 10 kbaud that is ±10 µs — easy for a timing-recovery loop, but a free-running receiver clock 50 ppm off drifts by 10 µs in 0.2 s, i.e. within one long packet. Hence timing recovery ([synchronisation](synchronization-carrier-timing.md)).

### Example 4 — Equaliser comparison (script §5)
BPSK, symbol-spaced channel $[0.857, 0, 0.514]$ (echo at 2T, −4.4 dB), Eb/N0 = 10 dB:

| Receiver | BER |
|---|---|
| AWGN / matched-filter bound (both paths' energy collected) | 3.9e-6 |
| No equaliser | 3.1e-2 |
| Zero-forcing, 21 taps (noise enhancement 3.2 dB) | 1.0e-3 |
| MMSE, 21 taps | 6.7e-4 |
| DFE (feedback = channel post-cursor) | 1.1e-4 |

The gap to the matched-filter bound is what MLSE or OFDM-with-coding would claw back.

### Example 5 — Sinc vs RC tails
A sinc pulse at 0.1 T timing error: tail contributions decay only as $1/n$, so the worst-case sum over a long random sequence grows like a harmonic series — the worst-case eye is closed. With β = 0.35 the same offset leaves 72 % of the eye. This is why nobody uses β = 0 in practice even though it would save 35 % bandwidth.

## Practical notes
- **Normalisation:** decide whether your RRC taps are normalised for unit energy ($\sum h^2=1$, convenient for matched filtering and noise scaling) or unit DC gain; mixing them rescales Eb/N0 in simulations.
- **Filter delay:** a symmetric FIR of $N$ taps delays by $(N-1)/2$ samples; the TX+RX pair by $N-1$. Account for it when comparing TX and RX bits.
- **Analog filters also cause ISI:** SAW/crystal IF filters have group-delay ripple near their edges; a narrow filter centred off the signal (from frequency offset) adds asymmetric distortion. Leave margin or equalise.
- **DAC images:** the TX RRC shapes the baseband, but the DAC's zero-order hold images at multiples of the sample rate still need an analog reconstruction filter ([data converters](../05-analog-electronics/data-converters-adc-dac.md)).
- **FSK chips** (SX126x, CC1101 …) use Gaussian shaping, not RRC — the Nyquist criterion does not apply; ISI is accepted and handled by the detector.
- **Mismatched roll-off** (TX β = 0.35, RX β = 0.5) leaves residual ISI of a few percent and ≈ 0.1–0.3 dB loss; match them when you control both ends.

## Common mistakes & misconceptions
- **Using RC filters at both TX and RX.** The cascade RC·RC is not Nyquist; the eye partially closes. Use RRC at both ends (or RC at one end and nothing — losing the matched-filter benefit).
- **"An RRC filter has zero ISI."** Only the RRC⊗RRC cascade does.
- **One-sided vs two-sided bandwidth.** $(1+\beta)R_s$ is the RF occupied width; $(1+\beta)R_s/2$ is the one-sided baseband width. Datasheets and forums mix these [2].
- **Truncating the RRC too short** (±2 symbols) — both ISI and spectral regrowth appear; a spectrum analyser shows raised shoulders.
- **Evaluating the eye at the wrong sample phase** in an oversampled simulation and concluding the filter is broken.
- **Blaming ISI for fading.** Nanosecond multipath on a kilobaud link produces flat fading, which no equaliser can fix.
- **ZF on deep spectral nulls** — noise blows up; use MMSE or DFE.

## How to simulate / verify
- **`tools/verify/comms_pulse_shaping.py`** (< 1 s): zero crossings and folded-spectrum flatness of RC for β = 0…1; RRC⊗RRC residual ISI and out-of-band power vs span; worst-case eye vs timing offset for four roll-offs; two-path channel with ZF, MMSE and DFE equalisers vs matched-filter bound. All PASS.
- **Eye diagram in Python:** reshape the matched-filter output into rows of 2 symbols × sps samples (`y[:n*sps].reshape(-1, 2*sps)`) and plot all rows.
- **GNU Radio:** *Root Raised Cosine Filter* / `firdes.root_raised_cosine(gain, fs, Rs, beta, ntaps)`; *Polyphase Arbitrary Resampler*; *QT GUI Eye Sink*; *Linear Equalizer* and *Decision Feedback Equalizer* blocks with LMS/CMA adaptive algorithms (see [GNU Radio stack](../14-sdr-dsp/gnu-radio-and-software-stack.md)).
- **Bench:** an SDR capturing your transmitter with a known PRBS; plot the eye and measure the occupied bandwidth; compare with the design β.

## Open questions / gaps
- The rocket-geometry delay estimate uses flat ground; a quantified multipath delay-spread measurement for launch sites (terrain, pad structures) was not found.
- Equaliser comparison uses one fixed channel; a sweep over echo delay/amplitude with MLSE would show where each method breaks down.

## Sources
1. H. Nyquist, "Certain topics in telegraph transmission theory," *Trans. AIEE* 47(2):617–644, 1928 — zero-ISI criterion and minimum bandwidth. (peer-reviewed, primary)
2. M. Lichtman, *PySDR*, "Pulse Shaping" chapter, https://pysdr.org/content/pulse_shaping.html — RC formula, $BW=R_s(1+\beta)$ as two-sided width, β = 0.2–0.5 typical, RRC split, eye-diagram margins, 101-tap example. (online textbook)
3. J. G. Proakis and M. Salehi, *Digital Communications*, 5th ed., McGraw-Hill, 2008 — §9.2 (Nyquist criterion, raised cosine, RRC), ch. 9 (equalisation: ZF, MMSE, DFE, MLSE). (textbook)
4. B. Sklar, *Digital Communications*, 2nd ed., Prentice Hall, 2001 — §3.3 (ISI, pulse shaping, RRC), eye patterns. (textbook)
5. S. Haykin, *Communication Systems*, 4th ed., Wiley, 2001 — ch. 4 (baseband pulse transmission, Nyquist channel, eye pattern, adaptive equalisation). (textbook)
6. MIT 6.02 lecture notes (Fall 2012) ch. 8–10 (ISI, eye diagrams, deconvolution). https://ocw.mit.edu/courses/6-02-introduction-to-eecs-ii-digital-communication-systems-fall-2012/ (lecture notes)
7. T. S. Rappaport, *Wireless Communications*, 2nd ed., Prentice Hall, 2002 — ch. 5 (delay spread, coherence bandwidth $B_c\approx1/5\sigma_\tau$, flat vs frequency-selective fading), ch. 7 (equalisation). (textbook)
8. G. D. Forney Jr., "Maximum-likelihood sequence estimation of digital sequences in the presence of intersymbol interference," *IEEE Trans. Inf. Theory* IT-18(3):363–378, 1972. (peer-reviewed)
9. S. U. H. Qureshi, "Adaptive equalization," *Proc. IEEE* 73(9):1349–1387, 1985 — ZF/MMSE/DFE, LMS, fractionally spaced equalisers. (peer-reviewed review)
10. B. Widrow and M. E. Hoff, "Adaptive switching circuits," *IRE WESCON Convention Record* pt. 4, pp. 96–104, 1960 — LMS algorithm. (peer-reviewed, historical)
