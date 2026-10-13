---
title: Synchronisation — carrier, frequency, symbol timing and frame
domain: 10-comms-modulation
slug: synchronization-carrier-timing
tags: [synchronisation, carrier-recovery, PLL, Costas-loop, loop-filter, frequency-offset, CFO, Cramer-Rao, timing-recovery, Gardner, Mueller-Muller, early-late, interpolator, frame-sync, preamble, sync-word, Doppler, rocket, TCXO]
prerequisites:
  - matched-filter-detection.md
  - digital-modulation-psk-qam-fsk.md
  - pulse-shaping-isi.md
  - ../06-rf-circuits/vco-and-pll-synthesizers.md
related:
  - packet-framing-protocols.md
  - ofdm.md
  - spread-spectrum-dsss-fhss-css.md
  - ber-ebn0-and-shannon.md
  - ../04-real-components-hf/crystals-and-resonators.md
  - ../07-noise-linearity/phase-noise-and-jitter.md
  - ../09-propagation-link-budget/multipath-fading-doppler.md
  - ../14-sdr-dsp/nco-ddc-duc.md
  - ../14-sdr-dsp/software-demodulation.md
  - ../15-lora-ism-radios/rocket-telemetry-radio-design.md
level: mixed
confidence: high
last_updated: 2026-10-14
---

# Synchronisation — carrier, frequency, symbol timing and frame

## Questions this page answers
- What has to be synchronised in a digital receiver, and in what order?
- How does a Costas loop recover the carrier of a BPSK/QPSK signal that has no carrier component?
- How do I choose the loop bandwidth and damping, and compute the loop-filter gains?
- How much phase jitter does a carrier loop add, and how much does that cost in BER?
- How do I estimate a frequency offset, and what is the best possible accuracy (Cramér–Rao bound)?
- How do Gardner and Mueller–Müller timing recovery work, and which needs what?
- How do I find the start of a packet (preamble, sync word), and what threshold do I use?
- How big is the Doppler shift on a rocket, how fast does it change, and how do I handle it?
- Why is a ±10 ppm crystal a bigger problem than Mach-3 Doppler at 433 MHz?
- Should I estimate carrier phase with a block (feed-forward) estimator or a Costas loop?
- What is residual-carrier PSK and why do deep-space links use it?
- How does polyphase-filterbank timing recovery work, and how many arms do I need?
- Can I get symbol timing in one shot with an FFT?
- How accurately can cross-correlation measure a time delay, and why normalise it?

## TL;DR
- A coherent receiver must estimate: **frequency offset** (Doppler + oscillator error), **carrier phase**, **symbol timing**, and **frame/packet start**. Typical burst-receiver order: detect preamble → coarse frequency → timing → fine frequency/phase (Costas/PLL) → frame sync [1], [2].
- **Oscillator error usually dominates Doppler** at UHF: ±10 ppm at 433 MHz = ±4.3 kHz per end, while 1000 m/s gives 1.44 kHz (433 MHz), 3.05 kHz (915 MHz), 5.26 kHz (GPS L1). Doppler *rate* at 10 g of **range** acceleration is 142 Hz/s (433 MHz) / 299 Hz/s (915 MHz); the range acceleration seen by a station is $\ddot R = \mathbf a\cdot\hat{\mathbf r} + v_\perp^2/R$, up to ≈ 1.4× the vehicle's acceleration near the pad ([15 impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md#doppler-rate-seen-from-the-ground--the-line-of-sight-rotation-term)). Use TCXOs (±0.5–2.5 ppm) or estimate and remove offset per packet.
- **Costas loop:** multiply I and Q to get a phase-error signal without a carrier (BPSK: $e=IQ$; QPSK: $e=\mathrm{sgn}(I)Q-\mathrm{sgn}(Q)I$). A second-order (PI) loop with noise bandwidth $B_n$ tracks phase with jitter $\sigma_\phi^2\approx\frac{B_nT}{E_s/N_0}\big(1+\frac{1}{2E_s/N_0}\big)$ (1.9° rms at $B_nT=0.01$, 10 dB — verified), follows a frequency *step* with zero steady-state error, and lags a frequency *ramp* by $\dot\omega/\omega_n^2$ rad (verified).
- **Loop-filter gains** for detector gain $K_p$ and NCO gain $K_0$: $\theta=\frac{B_nT}{\zeta+1/(4\zeta)}$, $K_1=\frac{4\zeta\theta}{(1+2\zeta\theta+\theta^2)K_pK_0}$, $K_2=\frac{4\theta^2}{(1+2\zeta\theta+\theta^2)K_pK_0}$ (Rice [3]); ζ ≈ 0.707, $B_nT$ ≈ 0.005–0.05.
- **Frequency estimation:** an FFT peak with parabolic interpolation reaches the Cramér–Rao bound $\mathrm{var}(\hat f)\ge\frac{6f_s^2}{(2\pi)^2\,\mathrm{SNR}\,N(N^2-1)}$ at moderate SNR (verified at 10 dB, N = 256). For M-PSK, raise to the M-th power to strip modulation; unambiguous range $\pm f_s/(2M)$ [1].
- **Timing:** Gardner TED (2 samples/symbol, works before carrier lock, phase-independent — verified) $e=\mathrm{Re}\{y^*_{n-1/2}(y_n-y_{n-1})\}$; Mueller–Müller (1 sample/symbol, needs decisions and carrier) $e=\mathrm{Re}\{\hat a^*_{n-1}y_n-\hat a^*_ny_{n-1}\}$ [4], [5].
- **Frame sync:** correlate against a known sync word; set the threshold from the allowed false-alarm rate; beware frequency offset (a 3.2 ms coherent correlation loses 25 dB at 1 kHz offset — see [matched filter](matched-filter-detection.md)).

## Intuition (no math)
The transmitter and receiver each have their own crystal. Even if both are nominally 433.000 MHz, they differ by kilohertz, and the moving rocket adds Doppler. The receiver sees the constellation spinning. It must also decide *when* in each symbol to take its sample — the sample clocks differ too, so the ideal sampling instant slowly slides. And it must know where a packet begins.

Each of these is solved by a small feedback loop or a one-shot estimate:

- A **phase-locked loop** compares the received phase with a local oscillator (NCO), and nudges the NCO. A carrier loop for BPSK can't compare against a carrier that isn't there (it's suppressed by the ±1 data), so a **Costas loop** uses a trick: the product $I\cdot Q$ is proportional to $\sin 2\phi$ regardless of which data bit was sent, so it points toward lock either way. The price is an ambiguity: the loop can lock 180° off, which is resolved by a known sync word or differential coding.
- **Timing loops** look at the signal around the decision instant. Gardner's detector looks at the sample *halfway* between two symbols: if the symbols differ, a correctly timed receiver sees the halfway sample near zero; if it is early or late, the halfway sample leans toward one symbol, and its sign (relative to the transition direction) tells which way to move.
- **Frequency estimates** are like measuring the spin rate of the constellation: long observations give sharper estimates (error falls as $N^{-3/2}$).
- **Frame sync** is a matched filter for a known bit pattern.

The *loop bandwidth* is the key design knob: wide loops follow fast changes (Doppler rate, phase noise) but let more noise through; narrow loops are quiet but slow and lose lock under dynamics.

## The math

### Level 1 — what the offsets look like
Received complex baseband after a nominal down-conversion:
$$r(t)=e^{j(2\pi\Delta f\,t+\theta)}\sum_na_np(t-nT-\tau)+w(t),$$
with frequency offset $\Delta f$ (Hz), phase θ (rad), timing offset τ (s). Doppler for radial velocity $v$ (m/s) at carrier $f_c$: $f_D=v f_c/c$; rate $\dot f_D=\dot v f_c/c$. Oscillator error: $\Delta f_{osc}=\epsilon_{ppm}\cdot10^{-6}f_c$ per end; the two ends add (worst case) or combine as root-sum-square (statistically).

| Carrier | 1 ppm | 300 m/s | 1000 m/s | 10 g Doppler rate |
|---|---|---|---|---|
| 433 MHz | 433 Hz | 433 Hz | 1444 Hz | 142 Hz/s |
| 868/915 MHz | 868/915 Hz | 869/916 Hz | 2.90/3.05 kHz | 284/299 Hz/s |
| 1575.42 MHz (GPS L1) | 1575 Hz | 1576 Hz | 5.26 kHz | 515 Hz/s |
| 2.44 GHz | 2.44 kHz | 2.44 kHz | 8.14 kHz | 798 Hz/s |

The "10 g" column is a range acceleration $\ddot R$ (a·r̂ + v⊥²/R), not the accelerometer reading; a station 0.5–2 km from the pad sees 13.7–15.3 g on the 11.1 g reference flight ([15 impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md#doppler-rate-seen-from-the-ground--the-line-of-sight-rotation-term)). Normalised quantities that matter: $\Delta f\,T$ (offset per symbol — sets correlation loss and whether a loop can pull in) and $\dot f_D T^2$.

### Level 1½ — each offset as "how far it moves in one symbol", algebra only
The formula above has three unknowns (Δf, θ, τ). Each is easiest to judge by how far it moves during one symbol of length T.
- **A frequency offset is a phase that walks.** An offset Δf turns the constellation by 360°·Δf·T every symbol. QPSK decisions fail once the walk between corrections reaches 45° (BPSK: 90°), so Δf must be removed before the decisions are made.
- **The two crystals add.** Each end is off by ε ppm, so the worst case is Δf = 2ε·f_c.
- **Correlation loss.** Integrating over one symbol while the phase walks shrinks the result by sinc(ΔfT) = sin(πΔfT)/(πΔfT). Keeping ΔfT below about 0.2 keeps the loss under 0.5 dB.
- **A clock offset is a slipping sample.** If the two symbol clocks differ by ε, the sampling instant moves by ε·T per symbol and slips one whole symbol after 1/ε symbols. Timing recovery must follow this drift.

*Worked number (verified, `tools/verify/s18b_level15_numbers.py`).* 433.92 MHz, 9600 baud (T = 104 µs):
- **Two ±10 ppm crystals:** Δf up to 8.68 kHz, i.e. **325° per symbol**. The constellation spins almost a full turn every symbol, so a preamble/FFT frequency estimate (Level 2b) is needed before any loop can lock.
- **Two ±2 ppm TCXOs:** 1.74 kHz, 65° per symbol, ΔfT = 0.18. The correlation loss is only **0.47 dB**, but a carrier loop is still needed to remove the phase walk.
- **Symbol clocks 100 ppm apart** (an uncalibrated MCU clock): one symbol slip every **10 000 symbols** (about 1 s at 9600 baud).

### Level 2 — carrier recovery with a PLL / Costas loop
**Phase detector.** De-rotate by the NCO estimate $\hat\theta$: $y=r\,e^{-j\hat\theta}$, phase error $\phi=\theta-\hat\theta$.
- Data-aided / pilot: $e=\mathrm{Im}\{y\,a^*\}\approx|a|^2\sin\phi$.
- Decision-directed: replace $a$ by the decision $\hat a$.
- BPSK Costas: $e=\mathrm{Re}\{y\}\mathrm{Im}\{y\}=\tfrac{A^2}{2}\sin2\phi$ (independent of the data sign) — stable points at $\phi=0,\pi$: 180° ambiguity.
- QPSK Costas: $e=\mathrm{sgn}(I)Q-\mathrm{sgn}(Q)I$ — 90° ambiguity [1], [6].

**Loop.** A proportional-plus-integral loop filter $F(z)=K_1+K_2/(1-z^{-1})$ drives an NCO $\hat\theta_{n+1}=\hat\theta_n+K_0v_n$. Linearised ($\sin\phi\approx\phi$), this is a second-order type-2 PLL with natural frequency $\omega_n$ and damping ζ; its one-sided noise bandwidth is $B_n=\frac{\omega_n}{2}\big(\zeta+\frac1{4\zeta}\big)$. The discrete-time gain formulas in the TL;DR follow from matching the continuous design by the bilinear transform with $\theta=B_nT/(\zeta+1/4\zeta)$ [3 App. C], [7].

**Phase jitter.** At high SNR the detector noise is white; the loop passes a fraction $2B_nT$ of it. For a pilot/decision-directed loop $\sigma_\phi^2=B_nT/(E_s/N_0)$; for the BPSK Costas loop the $I\cdot Q$ product adds noise×noise terms, the **squaring loss**: $\sigma_\phi^2=\frac{B_nT}{E_s/N_0}\left(1+\frac{1}{2E_s/N_0}\right)$ [6], [7]. Simulated at $E_s/N_0=10$ dB, $B_nT=0.01$: 1.91° rms vs 1.86° predicted. BER cost of a static phase error φ for BPSK: $Q\big(\sqrt{2E_b/N_0}\cos\phi\big)$; for 2° the loss is $20\log\cos2°=0.005$ dB — negligible. Jitter matters for 16-QAM and up, and when the loop must be wide to track phase noise or dynamics.

**Tracking dynamics** (type-2 loop): phase step → error decays to zero; frequency step → zero steady-state phase error (the integrator absorbs it); frequency ramp (Doppler rate) → steady-state error $\phi_{ss}=\dot\omega/\omega_n^2$ (verified: 0.0060 rad simulated vs 0.0056 predicted). A type-3 loop (extra integrator) removes the ramp error at the cost of stability margin. The pull-in (acquisition) range of a PLL is limited to roughly its bandwidth; beyond that use a **frequency-locked loop (FLL)** or an open-loop estimate first. GNSS receivers routinely use FLL-assisted PLLs for exactly this reason [8].

### Level 2b — frequency-offset estimation
**Single tone / pilot / preamble of known symbols** (strip modulation by multiplying by $a_n^*$). The ML estimator is the peak of the periodogram; FFT with zero-padding plus parabolic interpolation gets close to it. The Cramér–Rao bound for a complex tone of $N$ samples, SNR ρ per sample, sample rate $f_s$ (Rife & Boorstyn [9]):
$$\mathrm{var}(\hat f)\ \ge\ \frac{6f_s^2}{(2\pi)^2\rho N(N^2-1)}\quad[\mathrm{Hz}^2].$$
Accuracy improves as $N^{-3/2}$: doubling the preamble length improves the rms frequency error by 2.8×. The estimator reaches the bound above a threshold SNR (outliers below it). Simulation: N = 256, ρ = 10 dB → rms error 3.00e-5 $f_s$ vs CRB 3.01e-5 $f_s$. Cheap alternatives: the phase of the lag-1 autocorrelation $\hat f=\frac{f_s}{2\pi}\arg\sum r_nr^*_{n-1}$ (Kay-type; unbiased range $\pm f_s/2$) [10].

*Derivation of this bound (Fisher information for amplitude, phase and frequency; phase referenced to the block centre; threshold effect): [estimation theory](../00-math-foundations/estimation-theory-ml-map-crb.md).*

**Non-data-aided (M-PSK):** $r^M$ removes the modulation ($a^M$ constant), leaving a tone at $M\Delta f$; estimate and divide by $M$. Range $\pm f_s/(2M)$ (±0.125 cycles/symbol for QPSK at 1 sample/symbol); the $M$-th power raises the noise, so it needs more samples [1]. Verified for QPSK at 0.03 cycles/symbol.

**FSK / discriminator receivers:** frequency offset appears as a DC shift of the discriminator output. Average over a DC-balanced preamble (e.g. 0101…) and subtract (AFC). Most ISM chips do this automatically during the preamble.

### Level 2c — symbol timing recovery
**Timing-error detectors (TED)** produce a signal whose mean ("S-curve") is zero at the right instant and odd around it.
- **Early–late gate:** $e=|y(nT+\tau+\delta)|^2-|y(nT+\tau-\delta)|^2$; uses the symmetry of the matched-filter output peak. Robust, needs ≥ 2 samples/symbol, phase-independent (magnitudes).
- **Gardner (1986)** [4]: at 2 samples/symbol, $e_n=\mathrm{Re}\{y^*_{n-1/2}\,(y_n-y_{n-1})\}$. Works on BPSK/QPSK without decisions and without carrier lock (verified: output unchanged by a carrier rotation), which is why it is the usual first timing loop in burst receivers. Needs symbol transitions (whitened data) and excess bandwidth (β > 0); its S-curve flattens as β → 0.
- **Mueller–Müller (1976)** [5]: at 1 sample/symbol, $e_n=\mathrm{Re}\{\hat a^*_{n-1}y_n-\hat a^*_ny_{n-1}\}$. Decision-directed, needs carrier phase lock; efficient for high-rate modems. PySDR implements this form with a fractional-delay interpolator [2].
- **Zero-crossing / transition trackers** in FSK and simple slicer receivers (a digital PLL on bit edges).

Simulated S-curves (RRC β = 0.35, noiseless, 32 samples/symbol) both cross zero at the correct instant with opposite signs on either side. The TED output feeds a PI loop filter (same design equations as above, with the TED gain as $K_p$) that controls a **fractional interpolator** (Farrow cubic, or polyphase filterbank) rather than the ADC clock [3 ch. 8], [11].

**Clock offset.** A symbol-clock error of ε ppm makes the ideal sample drift by $\epsilon\cdot10^{-6}$ symbols per symbol; a 100-ppm mismatch drifts one whole symbol in $10^4$ symbols — longer packets than that need a tracking loop, not just an initial estimate.

### Level 2d — feed-forward estimators, residual carrier, polyphase and FFT timing, cross-correlation delay (W5-S8)
All numbers are from `tools/verify/s8_sync_extras.py` (34/34 PASS).

**Feed-forward ML-type phase recovery (Viterbi & Viterbi) versus the Costas loop.**
- *Where the estimator comes from.* For M-PSK with unknown data, average the likelihood over the M possible symbols. At low SNR the leading term of that average depends on the phase only through $\mathrm{Re}\{(r_ke^{-j\theta})^M\}$, so the block estimate is
$$\hat\theta=\frac1M\arg\sum_{k=1}^{N}F(|r_k|)\,e^{jM\arg r_k},$$
with a weighting $F(|r|)=|r|^m$. The plain M-th power is m = M; m = 0 uses the phase only [16].
- *Accuracy.* The modified CRB for N symbols is $1/(2N\,E_s/N_0)$ rad². For QPSK at 10 dB and N = 32 (bound 2.3° rms), the plain $r^4$ is 1.52× the bound (2.8°). Weighting with m = 1 or 0 brings it to 1.11× or 1.16×. At 3 dB the $r^4$ estimator is 6.4× the bound, because noise×signal cross terms dominate. This is the feed-forward counterpart of the Costas loop's squaring loss.
- *Ambiguity.* The estimate is only known modulo 2π/M (±45° for QPSK). Successive blocks must be **unwrapped**: choose the branch nearest the previous estimate. An unwrapping error is a cycle slip.
- *Equivalence.* A block of N symbols has the same noise as a first-order loop with $B_nT=1/(2N)$, since $\sigma^2=B_nT/(E_s/N_0)=$ MCRB.
- *When to use which.* Use the block estimator for bursts, highly parallel hardware (coherent optical receivers use it at tens of Gbaud) and phase noise that is white over a block. Use a loop for continuous signals with frequency drift. The loop tracks a ramp, while a block estimator needs a separate frequency estimate first.

**Residual-carrier PSK.** Phase-modulate the carrier by $\pm\beta$ instead of ±90°: $s(t)=\sqrt{2P}\cos(\omega t+\beta d(t))$ with $d=\pm1$ (often on a square-wave subcarrier). Expanding the cosine shows a **carrier line of power $P\cos^2\beta$** and **data power $P\sin^2\beta$**.

| β | Carrier | Data |
|---|---|---|
| 30° | −1.25 dB | −6.02 dB |
| 60° | −6.02 dB | −1.25 dB |
| 80° | −15.2 dB | −0.13 dB |

(The spectral line is measured by FFT in the script.) An ordinary PLL locks to the line, with no squaring loss and no 180° ambiguity. It works at data rates so low that a Costas loop would need an impractically narrow $B_nT$. The carrier-loop SNR is $P\cos^2\beta/(N_0B_L)$. This is the classic deep-space and two-way-Doppler tracking format. For a rocket it is a way to get **Doppler velocity** from the carrier loop independently of the data.

Example: C/N0 = 40 dB-Hz and β = 60° put 34 dB-Hz in the carrier, so a 10 Hz loop runs at 24 dB loop SNR. The data at 100 b/s get Eb/N0 = 40 − 1.25 − 20 = 18.8 dB.

**Polyphase-filterbank timing recovery** (harris and Rice [17]). Design the matched filter at P times the sample rate and split it into P polyphase arms $h_p[n]=h[nP+p]$. Each arm is the matched filter for a timing offset of p/P of a sample. The timing loop selects the arm, and slips one input sample when the index wraps. This merges matched filtering and fractional interpolation into one filter, and it is what GNU Radio's *Polyphase Clock Sync* does.
- The timing-error detector is the **ML TED**. The non-data-aided log-likelihood is $\Lambda(\tau)\propto\sum_k|y(kT+\tau)|^2$, and its derivative gives $e_k=\mathrm{Re}\{y^*(kT+\tau)\,y'(kT+\tau)\}$. Here $y'$ is the output of a second bank that holds the *derivative* of the matched filter. The script's S-curve crosses zero exactly at the correct instant.
- With P = 32 the worst-case quantisation is T/64, which costs **0.004 dB** of peak and leaves ISI at **−33.5 dB** for RRC β = 0.35. So 32 arms is ample for 16-QAM, and 8–16 suffice for QPSK.

**FFT (square-law) feed-forward timing** (Oerder and Meyr [18]). The squared magnitude of a band-limited signal with excess bandwidth β > 0 contains a spectral line at the symbol rate, and its phase is the timing offset. With $N_s$ = 4 samples per symbol,
$$\frac{\hat\tau}{T}=-\frac1{2\pi}\arg\sum_k|x_k|^2e^{-j2\pi k/N_s}.$$
It is one-shot, non-data-aided and carrier-independent, which suits bursts. Simulated at 10 dB with 256 symbols and β = 0.5, the rms error is **0.009 T**. It fails as β → 0 because the line vanishes, and it needs ≥ 3–4 samples per symbol, because $|x|^2$ doubles the bandwidth.

**Normalised cross-correlation (NCC) delay estimation.**
$$\rho_{xy}(\tau)=\frac{\sum_nx^*[n]\,y[n+\tau]}{\sqrt{\sum|x|^2\sum|y|^2}},\qquad|\rho|\le1\ \text{(Cauchy–Schwarz)}.$$
Normalisation makes the peak height independent of signal level. A fixed threshold (say |ρ| > 0.5) then means the same thing for weak and strong signals, which is why it is used for sync-word and template detection. Compute it with FFTs. For sub-sample delay, fit a parabola to the three samples around the (phase-aligned) peak.
- The **Cramér–Rao bound** for the delay of a known waveform in white noise is
$$\mathrm{var}(\hat\tau)\ge\frac{1}{8\pi^2B_{rms}^2\,E/N_0},\qquad B_{rms}^2=\frac{\int f^2|S(f)|^2df}{\int|S(f)|^2df},$$
in the complex-envelope convention of the [canonical page](../00-math-foundations/canonical-values-and-conventions.md); in the real-passband form the denominator is $(2\pi B_{rms})^2\cdot2E/N_0$. For a flat band of width B, $B_{rms}=B/\sqrt{12}$.
- Simulated with a 4× oversampled noise-like signal at E/N0 = 31 dB: NCC plus parabolic interpolation gives 0.042 samples rms against a bound of 0.043, with a bias of −0.001 samples.
- *Example:* B = 1 MHz at E/N0 = 30 dB gives σ_τ = **12.3 ns (3.7 m)**: wider bandwidth or more energy gives finer ranging.
- When *both* signals are noisy (TDOA between two receivers), the effective E/N0 is lower. Pre-whitening the cross-spectrum (generalised cross-correlation, Knapp and Carter [19]) sharpens the peak in coloured noise or multipath.


### Level 3 — frame synchronisation, optimality, and joint estimation
**Frame sync.** Correlate the (soft) received stream with the known sync word $s_i\in\pm1$: $\Lambda(k)=\sum_iy_{k+i}s_i$. Massey showed the optimum rule for a sync word embedded in random data also includes a data-dependent correction term, $\Lambda'=\sum_i\big[y_is_i-\frac{N_0}{2}\ln\cosh\frac{2y_i}{N_0}\big]$ (BPSK, soft) — the plain correlation is a good high-SNR approximation [12]. Hard-decision alternative: accept if the Hamming distance to the sync word is ≤ E. Choose words with low autocorrelation sidelobes (Barker-like, or CCSDS's 32-bit ASM 0x1ACFFC1D) so partial overlaps don't trigger [13]. Detection and false-alarm probabilities: [packet framing](packet-framing-protocols.md) and [matched filter](matched-filter-detection.md).

**Order and joint estimation.** Estimates interact: frequency offset rotates the phase during a timing estimate; timing errors reduce the energy seen by the phase detector. The robust sequence for bursts: (1) energy/preamble detection with a non-coherent or frequency-tolerant detector; (2) coarse CFO from the preamble; (3) timing (Gardner, phase-independent); (4) fine CFO + phase (Costas/decision-directed PLL); (5) frame sync (resolves the Costas ambiguity) [1], [2], [14].

**Bounds.** The modified Cramér–Rao bounds for phase, frequency and timing (Mengali & D'Andrea [14]) show that all three improve with observation energy $NE_s/N_0$; frequency additionally as $N^2$, timing with the pulse's mean-square bandwidth (sharper pulses, larger β → better timing estimates).

**OFDM and CSS** have their own sync methods — Schmidl–Cox repeated-half preamble for OFDM ([OFDM](ofdm.md)); dechirp-and-FFT offset estimation for LoRa ([spread spectrum](spread-spectrum-dsss-fhss-css.md), [LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md)).

## Design equations & rules of thumb

| Equation / rule | When valid | Typical values |
|---|---|---|
| $f_D=vf_c/c$; $\dot f_D=af_c/c$ | line-of-sight radial | 1000 m/s @ 433 MHz = 1.44 kHz |
| Oscillator offset $=\epsilon_{ppm}f_c$ per end | XO ±10–50 ppm, TCXO ±0.5–2.5 ppm | 433 MHz ±10 ppm = ±4.3 kHz |
| $B_n=\frac{\omega_n}{2}(\zeta+\frac1{4\zeta})$ | 2nd-order PLL | ζ = 0.707 → $B_n=0.53\,\omega_n$ |
| $K_1,K_2$ from $B_nT$, ζ (Rice) | PI loop filter | $B_nT$ = 0.005–0.05 |
| $\sigma_\phi^2=\frac{B_nT}{E_s/N_0}(1+\frac1{2E_s/N_0})$ | BPSK Costas, linear region | 1.9° @ 10 dB, $B_nT$ = 0.01 |
| $\phi_{ss}=\dot\omega/\omega_n^2$ | type-2 loop, frequency ramp | keep < 10–20° |
| $\mathrm{var}\hat f\ge6f_s^2/[(2\pi)^2\rho N(N^2-1)]$ | tone/pilot, above threshold | error ∝ $N^{-3/2}$ |
| M-th power CFO range $\pm f_s/(2M)$ | M-PSK, NDA | QPSK: ±0.125 $R_s$ |
| Coherent correlation loss $20\log|\mathrm{sinc}(\Delta fT)|$ | sync words, preambles | keep $\Delta fT<0.2$ |
| Gardner: 2 sps, phase-independent; M&M: 1 sps, needs carrier | TEDs | Gardner first in bursts |
| $\hat\theta=\frac1M\arg\sum|r|^me^{jM\arg r}$; MCRB $1/(2NE_s/N_0)$ | feed-forward M-PSK phase | QPSK 10 dB, N = 32: $r^4$ 1.5×, m = 1 1.1× MCRB |
| Carrier $P\cos^2\beta$, data $P\sin^2\beta$ | residual-carrier PM | β = 60°: −6.0 / −1.25 dB |
| Polyphase arms P → worst timing error T/(2P) | PFB timing | P = 32: 0.004 dB, ISI −33.5 dB |
| $\hat\tau/T=-\frac1{2\pi}\arg\sum|x_k|^2e^{-j2\pi k/N_s}$ | Oerder–Meyr, β > 0, $N_s\ge4$ | 0.009 T rms at 10 dB, 256 symbols |
| $\mathrm{var}\,\hat\tau\ge1/(8\pi^2B_{rms}^2E/N_0)$, $B_{rms}=B/\sqrt{12}$ (flat) | delay estimation | 1 MHz, 30 dB: 12.3 ns |

## Worked examples

### Example 1 — Offset budget for a 433 MHz rocket downlink
Flight computer XO ±10 ppm, ground SDR ±0.5 ppm GPSDO-disciplined, peak velocity 700 m/s. Worst-case offset $= 4.33+0.22+1.01=5.6$ kHz. For LoRa at 125 kHz bandwidth that is 4.5 % of BW — well inside Semtech's ±25 %-of-BW static tolerance; the Doppler *rate* is the LoRa limit at high SF ([LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)). For a 10 kb/s GFSK link with ±5 kHz deviation, it exceeds the deviation: the receiver needs a wide acquisition bandwidth (≈ Carson + 2×5.6 kHz ≈ 31 kHz), then AFC, then a narrower filter — or a TCXO on the rocket (±2 ppm → 0.87 kHz + Doppler 1.0 kHz). Temperature and vibration on the pad and in flight shift an XO further; TCXO is cheap insurance ([crystals](../04-real-components-hf/crystals-and-resonators.md)).

### Example 2 — Carrier loop for a coherent BPSK rocket link
BPSK at 10 kbaud, 915 MHz, peak acceleration 10 g during boost → Doppler rate 299 Hz/s. Choose ζ = 0.707 and $B_n=50$ Hz ($B_nT=0.005$): $\omega_n=2B_n/(\zeta+1/4\zeta)=94.3$ rad/s. Ramp error $\phi_{ss}=2\pi\cdot299/94.3^2=0.211$ rad = **12.1°** (BPSK loss $20\log\cos12°=0.2$ dB — fine; for QPSK marginal). Jitter at $E_s/N_0=6$ dB (coded operating point): $\sigma^2=0.005/3.98\cdot(1+0.126)=1.41\times10^{-3}$ → 2.2° rms. A ground station near the pad sees more than the motor's 10 g, because the range acceleration includes $v_\perp^2/R$: 13.7 g at 2 km on the 11.1 g reference flight ([15 impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md#doppler-rate-seen-from-the-ground--the-line-of-sight-rotation-term)) → ≈ 410 Hz/s, ramp error 16.6° (BPSK loss 0.37 dB); 15.3 g at 0.5 km → 458 Hz/s, 18.5° (0.46 dB). The 50 Hz loop still holds for BPSK. If the rocket experiences 30 g, the ramp error triples to 36° — too much: widen $B_n$ to ≈ 90 Hz or add a third integrator/FLL assist.

### Example 3 — Preamble length for a frequency estimate
The goal is a residual CFO small enough that the phase drifts well under 1 rad across the packet, so the phase loop only has to trim. With a 32-symbol known preamble at $E_s/N_0=6$ dB (ρ = 4), CRB: $\sigma_f=\frac{f_s}{2\pi}\sqrt{\frac{6}{4\cdot32\cdot(32^2-1)}}=\frac{f_s}{2\pi}\cdot6.77\times10^{-3}=1.08\times10^{-3}f_s$. At 10 kbaud that is 10.8 Hz rms — over a 200-symbol packet (20 ms) the residual rotates 0.22 cycles (1.4 rad) at 1σ, so a tracking loop is still needed; doubling the preamble to 64 symbols cuts it to 3.8 Hz (0.48 rad).

### Example 4 — Why the discriminator FSK radio "just works"
A GFSK discriminator sees a 2 kHz offset as a DC level of 2 kHz × (volts per Hz). With a 0101 preamble the average is the offset; subtracting it centres the slicer. No phase recovery is needed, and timing is recovered from bit transitions. The cost is ≈ 4 dB of sensitivity versus coherent BPSK ([BER page](ber-ebn0-and-shannon.md)) — often a good trade on a dynamic rocket.

### Example 5 — Timing drift between two crystals
TX and RX symbol clocks differ by 20 ppm. Over a 255-byte packet at 20 kbaud (2040 symbols at BPSK) the drift is 0.04 symbol — within the ±0.1 T tolerance of β = 0.35 pulses ([pulse shaping](pulse-shaping-isi.md)), so an initial timing estimate suffices; for 10× longer frames you must track.

## Practical notes
- **Carry the loops in the NCO domain**, not the RF synthesiser: SDRs correct offset digitally; chip radios provide AFC registers. See [NCO/DDC](../14-sdr-dsp/nco-ddc-duc.md).
- **Phase noise** of cheap synthesisers puts a floor under carrier-loop jitter and constrains how narrow $B_n$ may be ([phase noise](../07-noise-linearity/phase-noise-and-jitter.md)).
- **Loop gain depends on signal amplitude** for most detectors ($K_p\propto A^2$ or $A$): normalise with AGC or the loop bandwidth changes with signal strength.
- **Cycle slips** (a Costas loop jumping by 180°) invert all subsequent bits in BPSK — differential encoding or periodic sync words bound the damage.
- **Hang-up:** a PLL starting near the unstable point (180° from lock) can linger; a small frequency offset or dithering helps.
- **Rocket specifics:** during motor burn, vibration modulates XO frequency (acceleration sensitivity ~1 ppb/g for good crystals, much worse for cheap ones) — another reason for TCXOs and loops wide enough to follow; near apogee the Doppler passes through zero and reverses.
- **Test** by injecting a known offset and ramp from an SDR/arbitrary waveform generator; log the loop state (NCO frequency) — it is a free velocity sensor.

## Common mistakes & misconceptions
- **Designing only for Doppler** and forgetting oscillator tolerance (and its temperature drift), which is usually larger at UHF.
- **Loop bandwidth in the wrong units** — $B_nT$ (normalised) vs $B_n$ in Hz vs $\omega_n$ in rad/s; the formulas above keep them distinct.
- **Costas-loop 180°/90° ambiguity** not resolved → all data inverted or rotated; use the sync word or differential coding.
- **Using Mueller–Müller before the carrier is locked** (it needs decisions); use Gardner or early–late first.
- **Gardner with β ≈ 0 pulses or long runs of identical symbols** — the S-curve collapses; whiten the data.
- **Long coherent preamble correlations with an unknown offset** — the correlation peak vanishes ($|\mathrm{sinc}(\Delta fT)|$).
- **Assuming the CRB is reached at low SNR** — estimators have a threshold below which errors jump to large outliers.
- **Using the plain M-th power at low SNR.** The $r^M$ weighting amplifies noise; a smaller exponent (|r| or phase only) is closer to the bound, and below ≈ 5 dB a decision-directed or data-aided estimator is better still.
- **Forgetting to unwrap block phase estimates.** Each block is ambiguous by 2π/M; without unwrapping, the decoded data rotate by 90° at random block boundaries.
- **Oerder–Meyr at 2 samples/symbol or with β ≈ 0.** The square-law line at 1/T aliases or vanishes; use ≥ 4 samples/symbol and real excess bandwidth.
- **Un-normalised correlation thresholds.** A raw correlation peak scales with signal amplitude, so a fixed threshold either misses weak signals or false-triggers on strong noise; normalise (NCC) or use a CFAR-style threshold.
- **Expecting cross-correlation delay accuracy from the sample interval.** Accuracy is set by $B_{rms}$ and E/N0 (sub-sample interpolation reaches the CRB); the sample interval only matters if you skip interpolation.

## How to simulate / verify
- **`tools/verify/comms_sync.py`** (≈ 2 s): Costas-loop jitter vs linear theory with squaring loss; zero mean error under frequency step; ramp error $\dot\omega/\omega_n^2$; Gardner and Mueller–Müller S-curves and Gardner's carrier-phase invariance; FFT-interpolation frequency estimator vs CRB; 4th-power QPSK CFO; Doppler/ppm/loop numbers on this page. All PASS.
- **`tools/verify/s8_sync_extras.py`** (≈ 3 s, 34/34 PASS; output `s8_sync_extras_output.txt`): Viterbi & Viterbi variance vs MCRB for weightings m = 0, 1, 4 at 10 and 3 dB; residual-carrier line power; ML-TED S-curve and polyphase quantisation loss; Oerder–Meyr rms error; NCC bounds, amplitude invariance and sub-sample accuracy vs the delay CRB; plus the 5G NR numerology used on the [OFDM page](ofdm.md).
- **PySDR "Synchronization" chapter** [2] gives runnable Python for coarse CFO (squaring + FFT), Mueller–Müller with interpolation, a Costas loop and frame sync.
- **GNU Radio:** *FLL Band-Edge* (coarse frequency), *Symbol Sync* (Gardner/M&M/early-late with polyphase or MMSE interpolators), *Costas Loop* (orders 2/4/8), *Correlation Estimator* (frame sync with phase/timing estimate), *Frequency Xlating FIR* (apply a known CFO).
- **Bench:** use a signal generator's FM/ramp function or an SDR script to sweep frequency at the expected Doppler rate while measuring BER/PER.

## Open questions / gaps
- Crystal acceleration sensitivity (g-sensitivity) values for common TCXO/XO parts were not researched; domain 04/18 should add them — they matter during motor burn.
- LoRa's own tolerance to frequency offset and drift (and the SX127x "low data rate optimise" rule) belongs to domain 15.
- A combined simulation of preamble CFO estimate → Gardner → Costas on a Doppler-ramped burst would validate the recommended ordering end-to-end.

## Sources
1. J. G. Proakis and M. Salehi, *Digital Communications*, 5th ed., McGraw-Hill, 2008 — ch. 5 (carrier and symbol synchronisation: ML estimation, PLL, Costas, decision-directed loops, M-th power, timing recovery). (textbook)
2. M. Lichtman, *PySDR*, "Synchronization" chapter, https://pysdr.org/content/sync.html — recommended order (coarse freq → timing → fine freq → frame), squaring/FFT CFO with range ±fs/(2N), M&M timing with interpolation, Costas loop, Barker/Zadoff–Chu frame sync. (online textbook)
3. M. Rice, *Digital Communications: A Discrete-Time Approach*, Pearson Prentice Hall, 2009 — ch. 7 (carrier phase sync), ch. 8 (symbol timing sync, interpolators), App. C (loop-filter design: $K_1,K_2$ from $B_nT$, ζ). (textbook)
4. F. M. Gardner, "A BPSK/QPSK timing-error detector for sampled receivers," *IEEE Trans. Communications* COM-34(5):423–429, 1986. (peer-reviewed, primary)
5. K. H. Mueller and M. Müller, "Timing recovery in digital synchronous data receivers," *IEEE Trans. Communications* COM-24(5):516–531, 1976. (peer-reviewed, primary)
6. J. P. Costas, "Synchronous communications," *Proc. IRE* 44(12):1713–1718, 1956 — the Costas loop. (peer-reviewed, primary)
7. F. M. Gardner, *Phaselock Techniques*, 3rd ed., Wiley, 2005 — loop bandwidth, damping, noise bandwidth, squaring loss, tracking errors, acquisition. (textbook)
8. E. D. Kaplan and C. J. Hegarty (eds.), *Understanding GPS/GNSS: Principles and Applications*, 3rd ed., Artech House, 2017 — ch. 8 (FLL-assisted PLL, DLL, dynamics stress). (textbook)
9. D. C. Rife and R. R. Boorstyn, "Single-tone parameter estimation from discrete-time observations," *IEEE Trans. Inf. Theory* IT-20(5):591–598, 1974 — CRB for frequency. (peer-reviewed)
10. S. Kay, "A fast and accurate single frequency estimator," *IEEE Trans. Acoustics, Speech, Signal Processing* 37(12):1987–1990, 1989. (peer-reviewed)
11. L. Erup, F. M. Gardner, R. A. Harris, "Interpolation in digital modems — Part II: Implementation and performance," *IEEE Trans. Communications* 41(6):998–1008, 1993 — Farrow interpolators for timing. (peer-reviewed)
12. J. L. Massey, "Optimum frame synchronization," *IEEE Trans. Communications* 20(2):115–119, 1972. (peer-reviewed)
13. CCSDS 131.0-B-5, *TM Synchronization and Channel Coding*, 2023 — §9 attached sync marker 1ACFFC1D (32-bit), 034776C7272895B0 (64-bit). https://ccsds.org/Pubs/131x0b5.pdf (standard)
14. U. Mengali and A. N. D'Andrea, *Synchronization Techniques for Digital Receivers*, Plenum, 1997 — modified CRBs, feedforward/feedback estimators, joint estimation. (textbook)
15. H. Meyr, M. Moeneclaey, S. A. Fechtel, *Digital Communication Receivers: Synchronization, Channel Estimation, and Signal Processing*, Wiley, 1998. (textbook)
16. A. J. Viterbi, A. M. Viterbi, "Nonlinear estimation of PSK-modulated carrier phase with application to burst digital transmission," *IEEE Trans. Inf. Theory* IT-29(4):543–551, 1983. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
17. f. j. harris, M. Rice, "Multirate digital filters for symbol timing synchronization in software defined radios," *IEEE JSAC* 19(12):2346–2357, 2001 — polyphase filterbank with derivative-filter ML TED. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
18. M. Oerder, H. Meyr, "Digital filter and square timing recovery," *IEEE Trans. Commun.* 36(5):605–612, 1988. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
19. C. H. Knapp, G. C. Carter, "The generalized correlation method for estimation of time delay," *IEEE Trans. ASSP* 24(4):320–327, 1976. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
20. J. G. Proakis, M. Salehi (ref. 1), ch. 5 (ML phase and timing estimation, NDA estimators); CCSDS 401.0-B, *Radio Frequency and Modulation Systems — Part 1*, residual-carrier PCM/PSK/PM modulation index guidance (cited from knowledge, not re-read). (textbook / standard)
21. Verification: `tools/verify/s8_sync_extras.py` (W5-S8). (numerical check)
