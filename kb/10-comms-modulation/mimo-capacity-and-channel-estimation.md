---
title: MIMO — channel model, capacity by SVD and water-filling, diversity vs multiplexing, Alamouti, channel estimation (LS/MMSE, OFDM pilots), and diversity for a rocket ground station
domain: 10-comms-modulation
slug: mimo-capacity-and-channel-estimation
tags: [mimo, simo, miso, spatial-multiplexing, diversity, svd, water-filling, ergodic-capacity, outage, rayleigh, keyhole, rank, condition-number, mrc, egc, selection-diversity, alamouti, stbc, diversity-multiplexing-tradeoff, channel-estimation, least-squares, mmse, pilots, comb-pilots, dft-interpolation, ofdm, mimo-ofdm, polarisation-diversity, ground-station]
prerequisites:
  - ber-ebn0-and-shannon.md
  - ofdm.md
  - ../00-math-foundations/matrices-and-linear-algebra-for-networks.md
  - ../00-math-foundations/estimation-theory-ml-map-crb.md
  - ../00-math-foundations/probability-random-processes-and-psd.md
related:
  - ../09-propagation-link-budget/multipath-fading-doppler.md
  - ../09-propagation-link-budget/two-ray-ground-reflection.md
  - ../11-radar/mimo-radar-virtual-arrays.md
  - ../12-phased-arrays/adaptive-beamforming-doa.md
  - ../15-lora-ism-radios/ground-station-design.md
  - ../08-antennas/antennas-on-rockets.md
  - ../08-antennas/antenna-polarization-and-circular-polarization.md
  - multiple-access-and-duplexing.md
  - synchronization-carrier-timing.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# MIMO — capacity, diversity, Alamouti and channel estimation

## Questions this page answers
- What does "MIMO" actually buy: more range, more speed, or both?
- How do you derive MIMO capacity, and where do the SVD and water-filling come from?
- Why does capacity grow with min(Nt, Nr) at high SNR, and why does a line-of-sight rocket link get no multiplexing gain?
- What is the difference between diversity and multiplexing, and what is the diversity–multiplexing trade-off?
- How does the Alamouti code work, and why is it 3 dB worse than receive diversity?
- How do least-squares and MMSE channel estimation work, and how many pilots do I need?
- How should pilots be spaced in an OFDM system, and what goes wrong if they are too sparse?
- What is water-filling, and when is it worth knowing the channel at the transmitter?
- Can two antennas on the rocket help more than two at the ground station?
- Should my LoRa ground station use two antennas, and how far apart?
- What are zero-forcing, MMSE and V-BLAST detectors?
- Why does the condition number of the channel matrix matter?
- What space-time codes exist beyond Alamouti, and why is there no rate-1 code for four antennas?
- How much better is ML than zero-forcing or LMMSE detection, and what is the LMMSE output SINR?
- If the transmitter knows the channel, how much better than Alamouti can it do?
- How do Wi-Fi and LTE get channel state information to the transmitter (sounding, feedback, reciprocity)?
- Should two antennas on a rocket be fed the same signal or an Alamouti pair?

## TL;DR
- **Model:** $\mathbf y=\mathbf H\mathbf x+\mathbf n$ with $N_t$ transmit and $N_r$ receive antennas, $\mathbf H\in\mathbb C^{N_r\times N_t}$ (entry $h_{ij}$ = gain from transmit j to receive i), and noise $\mathcal{CN}(0,N_0\mathbf I)$.
- **Capacity with H known at the receiver:** $C=\log_2\det(\mathbf I+\frac{\rho}{N_t}\mathbf H\mathbf H^H)=\sum_i\log_2(1+\frac{\rho}{N_t}\sigma_i^2)$, where $\sigma_i$ are the singular values of H. If the transmitter also knows H, **water-filling**, $p_i=(\mu-N_0/\sigma_i^2)^+$, is optimal. In the script, water-filling gains 0.94 b/s/Hz at 0 dB on a random 4×4 channel, and nothing at 20 dB.
- **Rich scattering** (i.i.d. Rayleigh): ergodic capacity at high SNR grows by **min(Nt, Nr) b/s/Hz per 3 dB** (simulated 0.98, 1.96, 3.88, 1.97 for 1×1, 2×2, 4×4, 4×2). **Line of sight with close antennas** (a rocket 10 km away): H is rank 1, so you get array gain ($\sigma_1^2=N_tN_r$) but **no multiplexing**.
- **Diversity:**
  - *L*-branch MRC on Rayleigh fading makes the BER fall as SNR⁻ᴸ. With BPSK at 10 dB per branch, BER is 2.3×10⁻² for L = 1, 1.6×10⁻³ for L = 2 and 9.7×10⁻⁶ for L = 4 (closed form = simulation).
  - **Alamouti** (2 Tx, 1 Rx) gets the same diversity order 2 *without* a second receiver, at **3 dB less SNR** than 1×2 MRC (it splits the power between the two transmitters). With 2 Rx it gives diversity 4. Rate-1 orthogonal codes exist only for 2 antennas (rate ¾ for 3–4). Transmit CSI (MRT) recovers the 3 dB.
- **Detectors (2×2 QPSK, 20 dB):** ZF 9.6×10⁻³, LMMSE 6.5×10⁻³, ML 5.3×10⁻⁴. ZF and LMMSE have diversity 1, ML diversity 2. At a fixed 4 b/s/Hz, two QPSK streams beat Alamouti-16QAM below ≈ 15 dB and lose above it: the DMT in practice.
- **Two antennas on an airframe:** feeding the same signal to both makes interference nulls when their spacing is a large fraction of λ. An Alamouti pair (or any orthogonal transmit diversity) gives the *power* sum, with no nulls. It needs a coherent receiver and two pilots, which LoRa/FSK modules cannot do.
- **Channel estimation** with T pilot symbols per antenna and orthogonal pilots ($\mathbf X\mathbf X^H=T\mathbf I$):
  - LS MSE = $\sigma^2/T$; MMSE MSE = $1/(1+T/\sigma^2)$, which is better at low SNR (0.20 vs 0.25 at 0 dB, T = 4);
  - you need at least $N_t$ pilot symbols per coherence interval.
- **OFDM comb pilots** must sample the channel's frequency response at least at its delay-spread "Nyquist" rate: spacing $D\le N/L$, i.e. $D\,\Delta f\le1/\tau_\text{max}$. With N = 64 and 8 taps, D = 8 is exactly enough (DFT-interpolation MSE equals the noise floor σ²L/Np = −25 dB), while D = 16 aliases (MSE −6 dB).
- **Ground station:**
  - two receivers with **selection diversity** turn a 9.5 % chance of a > 10 dB Rayleigh fade into 0.9 %, but only if the branches are decorrelated;
  - at a correlation of 0.81 the outage is 3.3 %, and at 0.98 it is 7.2 %;
  - for LOS rocket links, fades come from the rocket's antenna pattern, polarisation and ground reflection, so **polarisation diversity** and **height diversity** work better than spacing. For the two-ray null at 433 MHz, 16.7° elevation, the height spacing is λ/(2 sin ψ) = **1.2 m**.

## Intuition (no math)
With one antenna at each end, a radio channel is a single pipe whose width fluctuates as multipath interferes. With several antennas at each end and a rich-scattering environment, each transmit antenna's signal reaches each receive antenna by a different mixture of paths. The combined "mixing matrix" H can be undone, like solving simultaneous equations, so you can send several independent streams on the same frequency at the same time. That is **spatial multiplexing**: speed. The singular value decomposition shows that H is secretly a set of independent parallel pipes, one per singular value, so capacity is a sum of single-pipe capacities.

You can instead use the extra antennas to send the *same* information along several independently fading paths. All of them are rarely in a deep fade at once, so the link becomes reliable. That is **diversity**: robustness, which turns into range or margin. There is a fundamental trade between the two. Using the antennas for more streams leaves less redundancy against fading.

Multiplexing needs the paths to be *different*. If the antennas are close together and the other end is far away in clear line of sight, every antenna sees essentially the same single path and the matrix has only one useful "pipe". This is the usual case for a rocket telemetry link. The extra antennas then give a stronger signal (array gain) and protection against nulls (diversity), not extra streams.

To undo H the receiver must *know* H. It learns it from **pilots**, known symbols sent periodically. Pilots cost airtime, and they must be dense enough in time and frequency to follow the channel's changes. That is the channel-estimation problem.

## The math

### Level 1 — results and symbols

| Quantity | Formula | Notes |
|---|---|---|
| Channel | $\mathbf y=\mathbf H\mathbf x+\mathbf n$ | ρ = total transmit SNR, $P/N_0$ |
| Capacity (receiver CSI, equal power) | $C=\log_2\det\!\left(\mathbf I_{N_r}+\frac{\rho}{N_t}\mathbf H\mathbf H^H\right)$ b/s/Hz | = $\sum\log_2(1+\frac{\rho}{N_t}\sigma_i^2)$ |
| Capacity (transmitter CSI) | $\sum_i\log_2(1+p_i\sigma_i^2/N_0)$, $p_i=(\mu-N_0/\sigma_i^2)^+$, $\sum p_i=P$ | water-filling |
| 1×1 Rayleigh ergodic | $\mathbb E[\log_2(1+\rho|h|^2)]=\log_2e\cdot e^{1/\rho}E_1(1/\rho)$ | 10 dB: 2.91 vs AWGN 3.46 b/s/Hz |
| MRC output SNR | $\gamma=\rho\sum_i|h_i|^2$ | diversity order L |
| BPSK, L-branch MRC, Rayleigh | $P_b=\left(\frac{1-\mu}2\right)^L\sum_{k=0}^{L-1}\binom{L-1+k}{k}\left(\frac{1+\mu}2\right)^k$, $\mu=\sqrt{\frac{\bar\gamma}{1+\bar\gamma}}$ | high SNR: $\propto\bar\gamma^{-L}$ |
| LS channel estimate | $\hat{\mathbf H}=\mathbf Y\mathbf X^H(\mathbf X\mathbf X^H)^{-1}$ | MSE per entry $\sigma^2/T$ (orthogonal pilots) |
| MMSE estimate (i.i.d. unit-variance H) | $\hat{\mathbf H}=\mathbf Y\mathbf X^H(\mathbf X\mathbf X^H+\sigma^2\mathbf I)^{-1}$ | MSE $1/(1+T/\sigma^2)$ |
| OFDM pilot spacing | frequency $D_f\le\frac{1}{\tau_\text{max}\Delta f}$; time $D_t\le\frac{1}{2f_DT_\text{sym}}$ | sampling theorem on H(f, t) |

### Level 1½ — the same ideas with algebra only
- **Two streams, two antennas.** If $y_1=h_{11}x_1+h_{12}x_2$ and $y_2=h_{21}x_1+h_{22}x_2$ (noise aside), the receiver can solve these two simultaneous equations for $x_1$ and $x_2$, provided the equations are not nearly the same. "Nearly the same" means the rows of H are almost parallel, i.e. the matrix is close to singular. The SVD measures exactly how far from singular it is: the smaller singular value tells you how weak the second stream is.
- **Capacity adds up.** Each independent pipe of gain $\sigma_i$ carries $\log_2(1+\text{SNR}_i)$ bits per second per hertz, and the total is the sum. Two pipes at 10 dB each carry about 2 × 3.46 = 6.9 b/s/Hz, against 3.46 for one.
- **Diversity multiplies small probabilities.** If each of two independent antennas is in a deep fade 10 % of the time, both are in a fade 10 % × 10 % = 1 % of the time.
- **Estimation averages noise.** Sending a known pilot T times and averaging cuts the noise variance of the channel estimate by T.

### Level 2 — derivations

**1. Capacity via the SVD.** For a fixed H, the mutual information with Gaussian input of covariance $\mathbf Q=\mathbb E[\mathbf x\mathbf x^H]$ is $I=\log_2\det(\mathbf I+\mathbf H\mathbf Q\mathbf H^H/N_0)$ (the entropy of a Gaussian vector is $\log\det(\pi e\,\mathbf R)$, and $I=h(\mathbf y)-h(\mathbf n)$).
1. Write $\mathbf H=\mathbf U\boldsymbol\Sigma\mathbf V^H$, with U and V unitary and Σ diagonal with $\sigma_1\ge\sigma_2\ge\dots$.
2. Precode with V, $\mathbf x=\mathbf V\tilde{\mathbf x}$, and combine with $\mathbf U^H$, $\tilde{\mathbf y}=\mathbf U^H\mathbf y$. Then $\tilde{\mathbf y}=\boldsymbol\Sigma\tilde{\mathbf x}+\tilde{\mathbf n}$, where $\tilde{\mathbf n}=\mathbf U^H\mathbf n$ is still white because U is unitary.
3. The channel is now $r=\operatorname{rank}\mathbf H$ independent scalar channels $\tilde y_i=\sigma_i\tilde x_i+\tilde n_i$.

With equal power $P/N_t$ per antenna (the best choice when the transmitter does not know H), $\det(\mathbf I+\frac{\rho}{N_t}\mathbf H\mathbf H^H)=\prod(1+\frac{\rho}{N_t}\sigma_i^2)$, because the determinant is invariant under the unitary similarity. The script confirms log-det = Σ log to 10⁻⁹.

**2. Water-filling (transmitter knows H).** Maximise $\sum_i\log(1+p_i\lambda_i/N_0)$, with $\lambda_i=\sigma_i^2$, subject to $\sum p_i=P$ and $p_i\ge0$. Lagrangian: $\mathcal L=\sum\log(1+p_i\lambda_i/N_0)-\nu(\sum p_i-P)$. Setting $\partial\mathcal L/\partial p_i=0$ gives $\frac{\lambda_i/N_0}{1+p_i\lambda_i/N_0}=\nu$, so $p_i=\frac1\nu-\frac{N_0}{\lambda_i}$. The KKT conditions clip this at zero: $p_i=(\mu-N_0/\lambda_i)^+$, with water level $\mu=1/\nu$ set by $\sum p_i=P$.

Picture a vessel whose floor height at position i is $N_0/\lambda_i$. Pour in water of volume P: weak eigen-channels (high floor) get little or no power. The script's closed form equals a numerical SLSQP optimum at 0, 10 and 20 dB. Water-filling helps most at low SNR: 3.76 vs 2.82 b/s/Hz at 0 dB, but only 20.77 vs 20.74 at 20 dB.

**3. High-SNR slope.** For large ρ, $C\approx\sum_{i=1}^{r}\log_2\frac{\rho\sigma_i^2}{N_t}=r\log_2\rho+\text{const}$. Each doubling of power adds r b/s/Hz. For i.i.d. Rayleigh, $r=\min(N_t,N_r)$ almost surely. These are the **degrees of freedom**, or multiplexing gain.

For a pure LOS channel between two small, distant arrays, $\mathbf H=\mathbf a_r\mathbf a_t^T$ (outer product of steering vectors) has rank 1, with $\sigma_1^2=N_tN_r$ for unit-modulus entries. The capacity is then $\log_2(1+\rho N_r)$: array gain, but no extra streams. A LOS channel regains rank only when the array apertures satisfy $d_td_r\gtrsim\lambda R/N$ (the Rayleigh spacing). At R = 10 km and 433 MHz, with N = 2, that is $d_td_r$ ≈ 3500 m², which is impossible on a rocket.

**4. Ergodic 1×1 Rayleigh capacity.** With $|h|^2=X\sim\text{Exp}(1)$, $\mathbb E\ln(1+\rho X)=\int_0^\infty\ln(1+\rho x)e^{-x}dx$. Integrating by parts gives $\int_0^\infty\frac{\rho}{1+\rho x}e^{-x}dx=e^{1/\rho}E_1(1/\rho)$, where $E_1$ is the exponential integral. Dividing by ln 2 converts to bits. The closed form matches Monte Carlo (2.906 vs 2.909 at 10 dB). Fading costs only 0.55 b/s/Hz of *ergodic* capacity at 10 dB, but its *outage* behaviour is far worse, and outage is what a short packet sees.

**5. Diversity and MRC.** For one symbol s sent over L independent branches $y_i=h_is+n_i$, the receiver that maximises output SNR (Cauchy–Schwarz) is $z=\sum h_i^*y_i$, giving $\gamma=\rho\sum|h_i|^2$, a sum of L exponentials. Averaging $Q(\sqrt{2\gamma})$ over that distribution gives the closed form in Level 1. At high SNR, $P_b\approx\binom{2L-1}{L}(4\bar\gamma)^{-L}$, so the slope in a log–log BER plot is −L. **Selection** diversity (pick the strongest branch) keeps the same order L with less gain. **Equal-gain combining** sits in between.

**6. Alamouti.** Transmit $(s_1,s_2)$ from antennas 1 and 2 in slot 1, and $(-s_2^*,s_1^*)$ in slot 2, each at half power. With one receive antenna and a channel constant over two slots, $r_1=(h_1s_1+h_2s_2)/\sqrt2+n_1$ and $r_2=(-h_1s_2^*+h_2s_1^*)/\sqrt2+n_2$. Combining, $\hat s_1=h_1^*r_1+h_2r_2^*$ and $\hat s_2=h_2^*r_1-h_1r_2^*$. The cross terms cancel exactly, giving $\hat s_i=\frac{|h_1|^2+|h_2|^2}{\sqrt2}s_i+\text{noise}$: diversity order 2 with linear decoding, at rate 1, and with *no* channel knowledge at the transmitter. Because the power is split, the SNR is half that of 1×2 MRC. The script shows Alamouti at 12 dB = MRC at 9 dB (2.51×10⁻³ vs 2.45×10⁻³) [2].

**7. Diversity–multiplexing trade-off (Zheng–Tse).** At high SNR, define the multiplexing gain $r=\lim R/\log_2\rho$ and the diversity gain $d=-\lim\log P_e/\log\rho$. For i.i.d. Rayleigh and long enough blocks, the optimal trade-off $d^*(r)$ is the piecewise-linear curve joining the points $(k,(N_t-k)(N_r-k))$ for $k=0,\dots,\min(N_t,N_r)$. For 2×2 that is (0, 4), (1, 1), (2, 0). You cannot have full diversity 4 *and* full multiplexing 2 at once. Alamouti sits at d = 4 only at r = 0, and V-BLAST spatial multiplexing at r = 2 with d → 0 [1][3].

**8. Least-squares and MMSE channel estimation.** Stack T pilot vectors into $\mathbf X\in\mathbb C^{N_t\times T}$, so that $\mathbf Y=\mathbf H\mathbf X+\mathbf N$.
- **LS** minimises $\|\mathbf Y-\mathbf H\mathbf X\|_F^2$, which gives $\hat{\mathbf H}=\mathbf Y\mathbf X^H(\mathbf X\mathbf X^H)^{-1}$ (needs $T\ge N_t$). The error is $\mathbf N\mathbf X^H(\mathbf X\mathbf X^H)^{-1}$, with total MSE $N_r\sigma^2\operatorname{tr}(\mathbf X\mathbf X^H)^{-1}$. Under a pilot-energy constraint $\operatorname{tr}(\mathbf X\mathbf X^H)=N_tT$, this is minimised by **orthogonal pilots** $\mathbf X\mathbf X^H=T\mathbf I$, giving per-entry MSE $\sigma^2/T$.
- **MMSE** (Bayesian; H i.i.d. $\mathcal{CN}(0,1)$): the linear MMSE estimator is $\hat{\mathbf H}=\mathbf Y\mathbf X^H(\mathbf X\mathbf X^H+\sigma^2\mathbf I)^{-1}$, with per-entry MSE $(1+T/\sigma^2)^{-1}$. It is always ≤ LS. It approaches LS at high SNR and helps at low SNR (0.20 vs 0.25 at 0 dB).

Both match Monte Carlo to < 1 % (script §3). The general estimation theory is on the [estimation page](../00-math-foundations/estimation-theory-ml-map-crb.md): LS = ML for Gaussian noise, and the MMSE estimator's form follows from the Gaussian prior.

**9. OFDM pilots as sampling.** In OFDM ([OFDM page](ofdm.md)) each subcarrier sees $H_k=\sum_{l=0}^{L-1}h_le^{-j2\pi kl/N}$. Comb pilots every D subcarriers give $H_{Dm}$, which is the $N_p=N/D$-point DFT of h, aliased if $L>N_p$.
- **DFT interpolation:** take the $N_p$-point IDFT of the pilot estimates, keep the first L taps (the rest is noise), zero-pad to N and FFT. This is exact when $N_p\ge L$, and the noise is reduced by $L/N_p$: MSE = $\sigma^2L/N_p$.
- In physical units, $N_p\ge L$ means $D\le N/L$, i.e. $D\,\Delta f\le1/\tau_\text{max}$: **pilot spacing in Hz must be below the coherence bandwidth** (the frequency-domain sampling theorem).
- In time, scattered pilots must satisfy $D_t\le1/(2f_DT_\text{sym})$ (Doppler Nyquist).

The script (N = 64, 8-tap exponential channel, 25 dB pilot SNR) gives −28.0 / −25.0 / −6.1 dB at D = 4 / 8 / 16, with the first two matching the theory (−28.0 / −25.0 dB) and D = 16 aliasing. Linear interpolation is 10–17 dB worse at D = 4 and 8.

**10. Detecting spatially multiplexed streams (without transmitter CSI).** The receiver knows $\hat{\mathbf H}$ and must separate the streams in $\mathbf y=\mathbf H\mathbf x+\mathbf n$. The standard detectors, in order of complexity:
- **Zero-forcing:** $\hat{\mathbf x}=(\mathbf H^H\mathbf H)^{-1}\mathbf H^H\mathbf y$, the least-squares inverse. Stream k's post-detection SNR is $\rho/[N_t(\mathbf H^H\mathbf H)^{-1}_{kk}]$. Noise enhancement is severe when H is ill-conditioned, and the diversity per stream is only $N_r-N_t+1$.
- **Linear MMSE:** $\hat{\mathbf x}=(\mathbf H^H\mathbf H+\tfrac{N_t}{\rho}\mathbf I)^{-1}\mathbf H^H\mathbf y$, which trades residual interference against noise and is always at least as good as ZF.
- **Successive interference cancellation (V-BLAST):** detect the strongest stream, subtract it, repeat. With MMSE filtering at each step, MMSE-SIC achieves the receiver-CSI capacity of Level 2 §1.
- **Maximum likelihood:** $\hat{\mathbf x}=\arg\min_{\mathbf x\in\mathcal S^{N_t}}\|\mathbf y-\mathbf H\mathbf x\|^2$. Full diversity $N_r$ per stream, with cost exponential in $N_t$; sphere decoding reduces the average cost.

### Level 2b — space-time block codes, detectors compared, MIMO-OFDM and CSI sounding (W5-S8)
All numbers in this subsection are from `tools/verify/s8_alamouti_mimo.py` (28/28 PASS).

**11. Alamouti as an orthogonal matrix, and with two receivers.** Write one Alamouti block as a 2×2 matrix whose rows are time slots and whose columns are antennas: $\mathbf A=\begin{pmatrix}s_1&s_2\\-s_2^*&s_1^*\end{pmatrix}$. Then $\mathbf A^H\mathbf A=(|s_1|^2+|s_2|^2)\mathbf I$, and this orthogonality is what makes the linear combiner of §6 exact. Equivalently, stacking $(r_1,r_2^*)$ gives an *effective* channel matrix $\mathbf H_\text{eff}$ whose columns are orthogonal with norm² $\|\mathbf h\|^2$, so the matched filter $\mathbf H_\text{eff}^H$ decouples $s_1$ and $s_2$ with no noise enhancement. With $N_r$ receive antennas, combine each antenna's two outputs and add over antennas: $\hat s_i=\frac{1}{\sqrt2}\|\mathbf H\|_F^2s_i+\text{noise}$. That gives diversity $2N_r$ with the SNR of $2N_r$-branch MRC **at half the power**. Checked: 2×2 Alamouti at 12 dB equals 4-branch MRC at 9 dB (2.25×10⁻⁵ vs 2.26×10⁻⁵), and at 10 dB it beats 1×2 MRC at 10 dB by 15× (1.1×10⁻⁴ vs 1.6×10⁻³).

**12. Orthogonal designs beyond two antennas** (Tarokh, Jafarkhani and Calderbank [11]). A complex orthogonal design is an $T\times N_t$ matrix of $\pm s_i,\pm s_i^*$ with $\mathbf G^H\mathbf G=(\sum|s_i|^2)\mathbf I$. It gives full diversity $N_tN_r$ with symbol-by-symbol linear decoding.
- A **rate-1** complex design exists **only for $N_t=2$** (Alamouti).
- For 3 and 4 antennas the best are **rate ¾**: 3 symbols in 4 slots. The script checks a 4×4 example with rows $(s_1,s_2,s_3,0)$, $(-s_2^*,s_1^*,0,s_3)$, $(-s_3^*,0,s_1^*,-s_2)$, $(0,-s_3^*,s_2^*,s_1)$; dropping a column gives the 3-antenna code.
- **Rate ½** designs exist for any $N_t$.
- *Real* designs (for BPSK/PAM) reach rate 1 for 2, 4 and 8 antennas.
- **Quasi-orthogonal** codes (Jafarkhani) recover rate 1 for 4 antennas, at the cost of pairwise rather than single-symbol decoding and some diversity at low SNR.

This is why practical systems with more than two transmitters combine Alamouti pairs with antenna switching or precoding rather than use rate-¾ codes. Example: LTE's 4-port transmit diversity is SFBC with frequency-switched transmit diversity, FSTD (from knowledge of TS 36.211, not re-checked).

**13. Transmit CSI changes the answer: MRT versus Alamouti.** If the transmitter knows $\mathbf h$ (MISO), **maximum-ratio transmission** $\mathbf x=\frac{\mathbf h^*}{\|\mathbf h\|}s$ makes the received amplitude $\|\mathbf h\|$. That is exactly 1×2 MRC: diversity 2 *and* array gain 2. Checked: MRT 2×1 at 10 dB = 1.61×10⁻³ = 1×2 MRC. Alamouti, which needs no transmit CSI, gets the same diversity but loses the 3 dB of array gain. The 3 dB is the price of not knowing the channel at the transmitter. For a MIMO channel the generalisation is SVD (eigen-) beamforming, $\mathbf x=\mathbf V\tilde{\mathbf x}$, with water-filling over the eigenmodes (§1–2).

**14. Detectors for spatial multiplexing, numerically (2×2, QPSK, two streams).**

| Total SNR ρ | ZF BER | LMMSE BER | ML BER |
|---|---|---|---|
| 10 dB | 7.8×10⁻² | 5.4×10⁻² | 2.9×10⁻² |
| 20 dB | 9.6×10⁻³ | 6.5×10⁻³ | 5.3×10⁻⁴ |
| 30 dB | 1.0×10⁻³ | 6.8×10⁻⁴ | 6.3×10⁻⁶ |

- ZF falls 10× per decade of SNR (slope 0.98): diversity $N_r-N_t+1=1$. Its post-detection SNR is $\frac{\rho/N_t}{[(\mathbf H^H\mathbf H)^{-1}]_{kk}}$, an exponential variable for 2×2, and the ZF BER equals single-branch Rayleigh at a bit SNR of $\rho/(2N_t)$ (9.6×10⁻³ at 20 dB, closed form = MC).
- **LMMSE** is 1.5–2 dB better than ZF at low and moderate SNR but has the same slope. Its output SINR for stream k (after removing the estimator's bias) is
$$\mathrm{SINR}_k=\frac{1}{\left[(\mathbf I+\tfrac{\rho}{N_t}\mathbf H^H\mathbf H)^{-1}\right]_{kk}}-1,$$
which the script confirms within 0.1 dB on fixed channels. The derivation: the LMMSE error covariance is $(\mathbf I+\frac{\rho}{N_t}\mathbf H^H\mathbf H)^{-1}$ for unit-power symbols, and the biased estimate has $\mathrm{SINR}_\text{biased}=1/\mathrm{MSE}_k$, so the unbiased SINR is $1/\mathrm{MSE}_k-1$.
- **ML** has slope 1.93: diversity $N_r=2$ per stream, at a cost of $|\mathcal S|^{N_t}$ = 16 metric evaluations per vector here.

**15. The diversity–multiplexing trade-off at a fixed rate.** At 4 b/s/Hz on a 2×2 channel you can send Alamouti with 16-QAM (rate 1, diversity 4) or two QPSK streams (rate 2, diversity 2 with ML). Symbol error rates from the script:
- 10 dB: Alamouti-16QAM 1.1×10⁻¹, SM-QPSK 5.3×10⁻²;
- 20 dB: 3.4×10⁻⁴ vs 1.0×10⁻³;
- 30 dB: < 3×10⁻⁶ vs 2.3×10⁻⁵.

Multiplexing wins at low SNR (QPSK's larger distance) and diversity wins at high SNR (steeper slope). This is the DMT of §7 seen at one operating point, and it is why 802.11n/LTE switch between STBC and spatial multiplexing with link adaptation.

**16. Imperfect CSI and a channel that changes inside the block.**
- *Pilot noise.* With LS estimates from T pilots per antenna (each antenna at half power, so the estimate error variance is $2/(\rho T)$), Alamouti 2×1 at 20 dB loses **4.8 dB with T = 1** and **1.4 dB with T = 4** relative to perfect CSI. The loss lies between $10\log(1+1/T)$ and $10\log(1+2/T)$. Spend at least 4 pilots per antenna, or use MMSE estimation (§8).
- *Time variation.* Alamouti assumes $\mathbf h$ is constant over the two slots. If the slot-2 channel has correlation r with slot 1, the cross terms no longer cancel and an **error floor** appears: at 40 dB, BER = 0 (r = 1), 7.5×10⁻⁵ (r = 0.99), 2.1×10⁻³ (r = 0.95). For Jakes fading, $r=J_0(2\pi f_DT_s)$. At 433 MHz and 300 m/s ($f_D$ = 433 Hz) and 10 kbaud, r = 0.98, enough for a floor of order 10⁻⁴–10⁻³. A *LOS* rocket link does not fade like Jakes, though: the bulk Doppler is a common rotation that the carrier loop removes, and pattern changes from roll (1–5 Hz) are slow compared with any symbol pair.
- *Space-frequency coding (SFBC)* instead pairs adjacent OFDM subcarriers, which needs the channel to be flat over two subcarriers rather than constant over two symbols. LTE 2-port transmit diversity is SFBC.

**17. MIMO-OFDM.** With a cyclic prefix longer than the channel, each subcarrier k is its own narrowband MIMO channel, $\mathbf y_k=\mathbf H_k\mathbf x_k+\mathbf n_k$. Everything above (capacity, Alamouti, ZF/MMSE/ML) applies per subcarrier, with $\mathbf H_k=\sum_l\mathbf H[l]e^{-j2\pi kl/N}$ ([OFDM](ofdm.md)). The extra tools are:
- **STBC across symbols or SFBC across subcarriers** (802.11n STBC; LTE SFBC);
- **cyclic delay diversity (CDD)**: transmit the same OFDM symbol from antenna 2 cyclically delayed by δ samples. The receiver sees one SISO channel $H_k=h_1+h_2e^{-j2\pi k\delta/N}$, so spatial diversity becomes frequency selectivity, invisible to the receiver and standard-compatible. Uncoded, it gives **no** gain (per-subcarrier BER at 15 dB = 1×1 Rayleigh, 7.6×10⁻³ vs 7.7×10⁻³); the gain appears only through FEC with interleaving across subcarriers;
- **per-antenna orthogonal pilots** in time, frequency or code (Example 6).

**18. CSI acquisition: sounding and feedback.** Precoding (MRT, SVD beamforming, multi-user zero-forcing) needs $\mathbf H$ at the *transmitter*. There are two routes:
- **Reciprocity (TDD).** The uplink and downlink share a frequency, so the transmitter estimates $\mathbf H^T$ from the other end's pilots. The air channel is reciprocal but the RF chains are not, so the TX and RX chain gains and phases must be calibrated relative to each other ([array calibration](../12-phased-arrays/array-calibration.md)). Massive-MIMO base stations work this way.
- **Explicit feedback (FDD, or Wi-Fi).** The transmitter sends a sounding packet, the receiver estimates $\mathbf H$, compresses it and sends it back. In 802.11ac/ax this is a null-data-packet announcement, then an NDP of training fields only, then a "compressed beamforming" report quantising the right singular vectors as Givens rotation angles. LTE/NR instead feed back a codebook index (PMI), a rank (RI) and a quality indicator (CQI). These protocol details are from knowledge of the standards and were not re-checked against them.

In both routes the CSI must still be valid when it is used: **feedback delay ≪ coherence time** (≈ 0.42/$f_D$ = 1 ms at $f_D$ = 433 Hz). That is why closed-loop MIMO is a slow-mobility tool, and why open-loop Alamouti/CDD is the fallback when the channel moves.

### Level 3 — what the simple models leave out
- **Correlation and keyholes.** Real channels have antenna correlation, $\mathbf H=\mathbf R_r^{1/2}\mathbf H_w\mathbf R_t^{1/2}$ (Kronecker model), which reduces both capacity and diversity. "Keyhole" channels (propagation through a single narrow aperture, e.g. a tunnel) are rank-1 even with rich scattering at both ends.
- **Imperfect CSI.** Channel-estimation error acts as extra noise of variance ≈ MSE × signal power. With LS pilots it caps the effective SNR at about $T/\sigma^2$ per stream. The optimal pilot overhead trades estimation quality against data time. For block fading of coherence length $T_c$ symbols, roughly $N_t$ of every $T_c$ symbols should be pilots at high SNR (Hassibi & Hochwald).
- **Outage capacity.** For slow fading (a packet shorter than the coherence time, as for LoRa), the relevant figure is $C_\epsilon$, the rate supported with probability 1 − ε. Diversity is what improves it. Ergodic capacity is a long-codeword idea.
- **Massive MIMO and beamforming.** With many antennas and channel knowledge, the transmitter can steer energy (maximum-ratio transmission). This is the comms counterpart of the arrays in [12-phased-arrays](../12-phased-arrays/adaptive-beamforming-doa.md). MIMO radar's virtual array ([11](../11-radar/mimo-radar-virtual-arrays.md)) is a different use of the same matrix algebra.
- **The two ends differ.** The degrees of freedom are limited by the *angular spread* seen at each end. A ground station sees a rocket as a point (tiny spread), while the rocket may see ground reflections plus the direct ray.

## Design equations & rules of thumb

| Rule | When valid | Number |
|---|---|---|
| $C=\sum\log_2(1+\frac{\rho}{N_t}\sigma_i^2)$ | receiver CSI | 4×4 at 10 dB (random draw): 9.76 b/s/Hz |
| Slope = min(Nt, Nr) b/s/Hz per 3 dB | rich scattering, high SNR | 2×2: +2 per 3 dB |
| LOS rank needs $d_td_r\gtrsim\lambda R/N$ | two small arrays | 10 km, 433 MHz: impossible on a rocket |
| Water-filling gain | transmitter CSI | large at low SNR, ≈ 0 at high SNR |
| MRC BER ∝ $\bar\gamma^{-L}$ | independent Rayleigh | L = 2 at 10 dB: 1.6×10⁻³ |
| Alamouti = 1×2 MRC − 3 dB | 2 Tx, 1 Rx, flat quasi-static | rate 1, no transmitter CSI |
| Pilots ≥ $N_t$ per coherence block | MIMO estimation | orthogonal (Hadamard, DFT) |
| LS MSE $\sigma^2/T$; MMSE $1/(1+T/\sigma^2)$ | orthogonal pilots | T = 4 at 0 dB: 0.25 / 0.20 |
| $D_f\Delta f\le1/\tau_\text{max}$; $D_t\le1/(2f_DT_s)$ | OFDM scattered pilots | 1 µs delay spread → pilots ≤ 1 MHz apart |
| Selection outage $\approx p^L$ | independent branches | 10 dB margin: 9.5 % → 0.9 % (L = 2) |
| Spatial decorrelation ≈ 0.4–0.5 λ | rich isotropic scattering (Jakes) | 433 MHz: ≈ 0.3 m |
| Height diversity spacing λ/(2 sin ψ) | two-ray ground reflection | 433 MHz, 16.7°: 1.2 m |
| Alamouti 2×$N_r$ = $2N_r$-branch MRC − 3 dB | quasi-static over 2 slots | 2×2 at 12 dB: 2.3×10⁻⁵ (BPSK) |
| Rate-1 complex orthogonal STBC only for $N_t$ = 2; rate ¾ for 3–4; ½ for any | Tarokh et al. | linear single-symbol ML decoding |
| MRT (transmit CSI) = MRC; Alamouti = MRC − 3 dB | MISO | the 3 dB is the value of transmit CSI |
| LMMSE SINR$_k$ = $1/[(\mathbf I+\frac{\rho}{N_t}\mathbf H^H\mathbf H)^{-1}]_{kk}-1$ | linear MMSE detection | ≥ ZF SINR; same diversity $N_r-N_t+1$ |
| Diversity per stream: ZF/MMSE $N_r-N_t+1$; ML $N_r$ | spatial multiplexing | 2×2 at 30 dB: ZF 1.0×10⁻³, ML 6.3×10⁻⁶ |
| Pilot-noise loss ≈ $10\log(1+1/T)$ … $10\log(1+2/T)$ | LS, T pilots per antenna | T = 4: 1.4 dB |
| Alamouti error floor when $r=J_0(2\pi f_DT_s)<1$ | channel varies between slots | r = 0.99 → ≈ 10⁻⁴ |
| CSI feedback delay ≪ coherence time ≈ 0.42/$f_D$ | closed-loop precoding | $f_D$ = 433 Hz → 1 ms |

## Worked examples

### Example 1 — 2×2 MIMO Wi-Fi in the pad area vs at range
A 5.8 GHz 2×2 802.11n video link in a cluttered pad area (rich scattering, SNR 25 dB): the ergodic 2×2 capacity is about 1.96 × (25/3) ≈ 13–14 b/s/Hz, against ≈ 7.5 b/s/Hz for 1×1, so roughly double the throughput. With the rocket at 3 km in clear sky, H becomes rank-1. The second stream collapses, and the link falls back to one stream with array and diversity gain: ≈ log₂(1 + 2ρ). This matches the KB's matrices-page conclusion ([matrices](../00-math-foundations/matrices-and-linear-algebra-for-networks.md) Ex. 5). In practice 802.11n rate adaptation drops to single-stream MCS at range.

### Example 2 — how many pilots for a 4×4 OFDM SDR experiment
Take N = 1024 subcarriers at Δf = 15 kHz (15.36 MHz bandwidth) and a delay spread of up to 2 µs (urban). Coherence-bandwidth sampling requires $D_f\le1/(2\times10^{-6}\cdot15\times10^3)$ = 33 subcarriers, so choose 12 with margin (LTE uses 6 per port, staggered). With 4 transmit antennas, use **orthogonal pilot patterns**: each antenna's pilots on disjoint subcarriers, or the same subcarriers with orthogonal codes, so that $\mathbf X\mathbf X^H$ is diagonal. In time, at 433 MHz and walking speed ($f_D$ ≈ 2 Hz) pilots are needed every ~1/(2·2·71 µs) ≈ 3500 symbols. For a rocket at 300 m/s ($f_D$ ≈ 430 Hz at 433 MHz) the limit is every ~16 symbols. Note that LoRa's long symbols (8 ms at SF12/125 kHz) make *any* coherent tracking hard, which is why LoRa is non-coherent ([LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)).

### Example 3 — two receivers at the LoRa ground station
The E22 module is a single receiver, so MRC is impossible. **Packet-level selection diversity** with two receivers is easy: forward every CRC-valid packet and drop duplicates.
- **Independent branches:** if each receiver loses a packet with probability p (fades plus noise), the pair loses $\approx p^2$. Against Rayleigh fades deeper than the 10 dB margin, p = 9.5 % per receiver becomes 0.9 %.
- **The catch:** the branches must fade *independently*. For a rocket in LOS the dominant "fades" are:
  1. **rocket antenna pattern nulls and roll modulation**, common to both ground antennas, so spatial diversity at the ground does not help. Only a second antenna *on the rocket*, or a different pattern, helps ([antennas on rockets](../08-antennas/antennas-on-rockets.md));
  2. **polarisation mismatch** as the rocket rolls and pitches. Two ground antennas of orthogonal polarisation (or one circular), feeding the two receivers, are *uncorrelated* for this effect. **Polarisation diversity is the most useful ground-station diversity** ([polarisation](../08-antennas/antenna-polarization-and-circular-polarization.md));
  3. **ground-reflection (two-ray) nulls** at low elevation. Two antennas at different heights decorrelate when separated by about half the null spacing. At 433 MHz with the rocket 3 km up at 10 km range (ψ = 16.7°), the null spacing is λ/(2 sin ψ) = 1.2 m, so mount the second Yagi about 0.6 m higher or lower. At 1 km altitude and 20 km range (ψ = 2.9°) it is 6.9 m.
- **Correlation matters:** in the script's correlated-Rayleigh check, an envelope correlation of 0.81 already raises the selection outage from 0.9 % to 3.3 %. Diversity with two co-polarised antennas 20 cm apart looking at a point source is nearly useless.

### Example 4 — reading the channel matrix from a 2×2 SDR measurement
Two ADALM-Pluto or LimeSDR channels transmit orthogonal pilot sequences, $\mathbf X=\begin{pmatrix}1&1&1&1\\1&-1&1&-1\end{pmatrix}$, so $\mathbf X\mathbf X^H=4\mathbf I$. The receiver computes $\hat{\mathbf H}=\mathbf Y\mathbf X^H/4$ (LS), then its singular values. A condition number $\sigma_1/\sigma_2$ < 3 indicates usable multiplexing; > 30 means effectively rank-1. Indoors the ratio is typically single-digit. Pointed at a distant LOS target, it grows rapidly. Synchronise the TX and RX clocks (shared reference) or the estimate rotates during the pilot block ([synchronisation](synchronization-carrier-timing.md)).

### Example 5 — capacity of a 2×2 channel by hand
Take $\mathbf H=\begin{pmatrix}1&0.5\\0.5j&1\end{pmatrix}$ and ρ = 10 (10 dB total transmit SNR, equal power, receiver CSI).
1. Compute $\mathbf H\mathbf H^H$ and its eigenvalues, or use `numpy.linalg.svd`: $\sigma^2$ = 1.957 and 0.543.
2. $C=\log_2(1+5\cdot1.957)+\log_2(1+5\cdot0.543)$ = 3.43 + 1.89 = **5.32 b/s/Hz**, against 3.46 for a 1×1 link with |h| = 1.

With a nearly singular channel, $\mathbf H=\begin{pmatrix}1&0.95\\0.95&1\end{pmatrix}$ (two antennas that see almost the same thing), the singular values are 1.95 and 0.05 (condition number 39). Capacity falls to 4.34 b/s/Hz, and almost all of it comes from the first stream. The second stream is 32 dB weaker than the first.

### Example 6 — pilot overhead in real standards
| System | Pilot density | Time pilots | Overhead |
|---|---|---|---|
| 802.11a/g (20 MHz) | 4 continuous pilots of 52 used subcarriers (phase tracking) + 2 long training symbols per packet | per packet | ≈ 8 % (preamble) + 7.7 % (pilots) |
| 802.11n 2×2 | HT-LTF: one training symbol per spatial stream | per packet | grows with streams |
| LTE (1–2 ports) | cell reference signal on every 6th subcarrier per port, staggered | 2 OFDM symbols per 0.5 ms slot per port | ≈ 5 % (1 port), 10 % (2 ports) |
| DVB-T | scattered pilots every 12th carrier, shifted by 3 each symbol | every symbol | ≈ 8 % |

These spacings follow the Level 2 rules: 15 kHz × 6 = 90 kHz ≪ 1/(5 µs). The KB's [OFDM page](ofdm.md) gives the numerology. Values are from knowledge of the standards, not re-checked against the documents.

### Example 7 — two antennas on the rocket: same signal, switching, or Alamouti?
A wrap-around pair or two whips on opposite sides of a 10 cm airframe are fed from one transmitter.
- **Same signal to both (a splitter):** the far field is the *amplitude* sum, $|(h_1+h_2e^{j\phi})/\sqrt2|^2$, which ripples between +3 dB and a null whenever the path difference reaches λ/2. At 433 MHz the antennas are only 0.14 λ apart (52°), so free-space ripple stays between +3.0 and +2.1 dB. In practice the airframe shadows each antenna on the far side, so the two patterns differ. At 2.44 GHz the spacing is 0.81 λ and there are real interference nulls around the vehicle.
- **Alamouti from two coherent transmit chains:** the receiver sees the *power* sum $|h_1|^2+|h_2|^2$ (script: flat 0 dB, the same as one antenna at full power). There are no interference nulls in any direction, and a shadowed antenna is covered by the other. The chains need a common clock but **no** phase calibration (any fixed offset is absorbed into $h_1,h_2$). The receiver must be coherent and estimate both channels from per-antenna pilots. It needs an SDR or custom modem: LoRa and FSK modules cannot do it. Non-coherent receivers would need differential STBC (Tarokh–Jafarkhani 2000, from knowledge).
- **Antenna switching on alternate packets** (Practical notes) is the module-friendly approximation: selection diversity across packets rather than within a symbol pair.
- Time variation is not the issue for a LOS rocket link (item 16): roll at 1–5 rev/s is slow compared with a 0.1 ms symbol pair at 10 kbaud.

## Practical notes
- **Hardware:** true MIMO needs phase-coherent receive (and transmit) chains: shared LO and clock. Options are 2×2 SDRs (LimeSDR, Pluto with the 2nd channel enabled, USRP B210), or COTS Wi-Fi/LTE chips, which do it internally. LoRa modules are single-chain. Use them for packet-selection diversity only.
- **Calibration:** relative gain and phase between chains drift with temperature. For beamforming, calibrate as in [array calibration](../12-phased-arrays/array-calibration.md). For spatial multiplexing, the channel estimate absorbs the chain mismatch automatically.
- **Antenna spacing:** for diversity in rich scattering, ≥ λ/2 (0.35 m at 433 MHz) decorrelates. Toward a point source in LOS, spacing must be very large or replaced by polarisation or height diversity.
- **Combining LoRa packets:** with two receivers at the ground station, log the RSSI/SNR of both. Over a flight, this measures the branch correlation directly, which is useful for deciding whether the second receiver is worth carrying.

- **Dual-receiver ground-station recipe:**
  1. Build two identical receive chains (antenna → filter/LNA → E22 or SX1262 module → microcontroller or Pi), sharing one clock for timestamps.
  2. Choose the diversity type: orthogonal linear polarisations (or one RHCP and one LHCP antenna), or a vertical separation of λ/(2 sin ψ)/2 at the expected low-elevation geometry.
  3. Log for every packet: received yes/no, RSSI, SNR and timestamp, on both chains.
  4. Afterwards compute the branch correlation of RSSI(t) and the joint loss probability. If joint loss ≈ the product of individual losses, the diversity works.
  5. Forward the first CRC-valid copy of each packet (by sequence number) to the tracking and display software.

- **Rocket-side diversity:** two antennas on the airframe (e.g. wrap-around halves or two whips 180° apart), each feeding its own transmitter on a different channel or time slot, attack the pattern-null fades that ground diversity cannot. The receivers combine at packet level. The cost is mass, power and spectrum. Alternatively, one transmitter can switch antennas on alternate packets: a crude form of transmit selection diversity, needing no feedback.
- **Coherence time on a rocket link:** with a slowly rolling rocket (1–5 rev/s), the pattern-induced fading has a period of 0.2–1 s. A LoRa SF12 packet (1–2 s) spans several roll cycles, so it averages over them, while an SF7 packet (≈ 50 ms) sees a frozen channel. Diversity matters most for the short, fast packets.
- **Interference rejection:** two receive antennas can also *null* an interferer, by combining with weights $\mathbf w\propto\mathbf R^{-1}\mathbf h$ (MMSE/MVDR, see [adaptive beamforming](../12-phased-arrays/adaptive-beamforming-doa.md)). That needs coherent chains, so it is an SDR ground-station project, not a module one.

## Common mistakes & misconceptions
- **Confusing receive diversity with MIMO.** Two antennas and two receivers at the ground station (SIMO) give diversity and array gain, but no multiplexing. That needs multiple *transmit* antennas too.
- **Adding power from the second antenna in Alamouti and calling it a gain.** Total transmit power is fixed; the gain is in fading robustness, not SNR.
- **"MIMO doubles my range."** Spatial multiplexing doubles *rate* in rich scattering, at the same range. Diversity improves reliability (fade margin), which can be traded for range. A LOS long-range link gets array gain, not multiplexing.
- **"More antennas always help capacity."** Only up to the channel rank. Correlated or LOS channels saturate.
- **Spacing ground antennas a few wavelengths apart for a LOS rocket link** and expecting independent fading. The rocket is a point source, so use polarisation or height diversity.
- **Too few pilots for the delay spread** (comb spacing $D\Delta f>1/\tau_\text{max}$): the channel estimate aliases, and the D = 16 case in the script is 19 dB worse.
- **Forgetting that Alamouti needs the channel constant over two symbols**, and that it gives no array gain at the transmitter (−3 dB relative to MRC).
- **"Rate-1 STBC for four antennas."** Complex orthogonal designs with rate 1 exist only for two antennas. Four-antenna orthogonal codes are rate ¾ or lower; rate-1 quasi-orthogonal codes give up single-symbol decoding.
- **Judging LMMSE by its biased output.** The LMMSE estimate is scaled down; compute SINR after removing that bias ($1/\mathrm{MSE}-1$, not $1/\mathrm{MSE}$), or the SINR is overstated by up to 1 in linear terms.
- **Expecting ZF or LMMSE to deliver receive diversity on an $N\times N$ channel.** They give diversity $N_r-N_t+1 = 1$; only ML or SIC-type detectors approach $N_r$.
- **Feeding two rocket antennas the same signal and calling it diversity.** It is a two-element array with interference nulls. Orthogonal transmit diversity (Alamouti, or at least antenna switching) is what removes them.
- **Expecting cyclic delay diversity to help uncoded OFDM.** It only turns spatial diversity into frequency selectivity; a code across subcarriers has to collect it.
- **Using stale CSI for precoding.** If the feedback delay approaches the coherence time, MRT/SVD beamforming can be worse than open-loop Alamouti.
- **Using non-orthogonal pilots** from the two transmitters. $\mathbf X\mathbf X^H$ becomes ill-conditioned and the LS error explodes.
- **Treating ergodic capacity as what a short packet sees.** For quasi-static fading, use outage.

## How to simulate / verify
- **By hand:** `numpy.linalg.svd(H)` gives the singular values. Then $C=\sum\log_2(1+\rho\sigma_i^2/N_t)$, and water-filling is about ten lines (see `waterfill()` in the script).
- **Monte Carlo:** draw $\mathbf H$ as i.i.d. complex Gaussians (`(randn+1j*randn)/sqrt(2)`), average the capacity for ergodic results, or take a percentile for outage capacity.
- **Bench:** two-receiver RSSI logging at the ground station during a static test (rocket on a pole, rotated through 360° in roll) measures the pattern-null correlation before any flight.
- `python3 tools/verify/e11_mimo.py` (≈ 1 s): **27/27 checks**; output in `tools/verify/e11_mimo_output.txt`. It covers log-det = SVD; water-filling vs numerical optimum; ergodic 1×1 closed form; high-SNR slopes; rank-1 LOS; MRC BER for L = 1, 2, 4; Alamouti vs MRC; LS/MMSE MSE; OFDM comb-pilot DFT interpolation and aliasing; selection outage with correlation; two-ray height-diversity spacing.
- `python3 tools/verify/math_matrices.py` (00 domain) has the SVD-capacity and water-filling basics.
- `python3 tools/verify/s8_alamouti_mimo.py` (≈ 6 s): **28/28 PASS**; output in `tools/verify/s8_alamouti_mimo_output.txt`. It covers Alamouti 2×1/2×2 vs 2-/4-branch MRC; rate-¾ orthogonal design ($\mathbf G^H\mathbf G$); MRT vs MRC vs Alamouti; 2×2 ZF/LMMSE/ML BER and slopes; ZF closed form; LMMSE SINR formula; Alamouti-16QAM vs SM-QPSK at 4 b/s/Hz; pilot-noise loss and the time-variation error floor; CDD; the airframe two-antenna pattern.
- GNU Radio: the `gr-mimo`-style examples, or two USRP channels with a known pilot burst, measure H. The SDR pages are in [14-sdr-dsp](../14-sdr-dsp/sdr-hardware-survey.md).

## Open questions / gaps
- The LOS-MIMO rank condition ($d_td_r\gtrsim\lambda R/N$) is stated from knowledge (Bøhagen–Orten–Øien style analysis), not derived here.
- No measured branch-correlation data for a Space Bar ground station exist yet. Recording dual-receiver RSSI during a flight would settle polarisation- vs spatial-diversity choices.
- Detectors (ZF/LMMSE/ML) and MRT are now simulated (Level 2b). Multi-user precoding, MMSE-SIC with ordering, sphere decoding and massive-MIMO channel hardening are still only named.
- The 802.11ac/ax sounding sequence, LTE 4-port SFBC+FSTD and PMI/RI/CQI feedback are described from knowledge of the standards, not re-read.
- MIMO-OFDM pilot patterns of specific standards (802.11n HT-LTF, LTE CRS ports) are described qualitatively.

- The roll-rate figures (1–5 rev/s) in the practical notes are typical hobby-rocket values from knowledge, not measured Space Bar data.
- The packet-level diversity benefit for LoRa should be validated against flight logs before the KB recommends the hardware cost.

## Sources
1. D. Tse, P. Viswanath, *Fundamentals of Wireless Communication*, Cambridge 2005, ch. 3 (diversity, MRC, Alamouti, BER of L-branch combining), ch. 5 (capacity, water-filling, outage), chs. 7–9 (MIMO channel modelling, SVD capacity, degrees of freedom, LOS rank, diversity–multiplexing trade-off). Free draft: https://web.stanford.edu/~dntse/papers/book121004.pdf. (textbook)
2. S. M. Alamouti, "A simple transmit diversity technique for wireless communications," *IEEE J. Sel. Areas Commun.*, 16(8):1451–1458, 1998. (peer-reviewed)
3. L. Zheng, D. N. C. Tse, "Diversity and multiplexing: a fundamental tradeoff in multiple-antenna channels," *IEEE Trans. Inf. Theory*, 49(5):1073–1096, 2003. (peer-reviewed)
4. E. Telatar, "Capacity of multi-antenna Gaussian channels," *Eur. Trans. Telecommun.*, 10(6):585–595, 1999. (peer-reviewed)
5. M. Biguesh, A. B. Gershman, "Training-based MIMO channel estimation: a study of estimator tradeoffs and optimal training signals," *IEEE Trans. Signal Process.*, 54(3):884–893, 2006. (peer-reviewed; LS/MMSE and optimal orthogonal training)
6. B. Hassibi, B. M. Hochwald, "How much training is needed in multiple-antenna wireless links?" *IEEE Trans. Inf. Theory*, 49(4):951–963, 2003. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
7. J.-J. van de Beek, O. Edfors, M. Sandell, S. K. Wilson, P. O. Börjesson, "On channel estimation in OFDM systems," *Proc. IEEE VTC*, 1995, pp. 815–819 (DFT-based estimation). (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
8. J. G. Proakis, M. Salehi, *Digital Communications*, 5th ed., McGraw-Hill 2008, §13.4 (diversity BER closed form), ch. 15 (multiple-antenna systems). (textbook)
9. A. Goldsmith, *Wireless Communications*, Cambridge 2005, ch. 7 (diversity, selection/EGC/MRC), ch. 10 (MIMO). (textbook)
10. Verification: `tools/verify/e11_mimo.py`. (numerical check)
11. V. Tarokh, H. Jafarkhani, A. R. Calderbank, "Space–time block codes from orthogonal designs," *IEEE Trans. Inf. Theory* 45(5):1456–1467, 1999 — orthogonal designs, rate-1 complex only for 2 Tx, rate-½ for any $N_t$, rate-¾ for 3–4 Tx. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
12. H. Jafarkhani, "A quasi-orthogonal space–time block code," *IEEE Trans. Commun.* 49(1):1–4, 2001; V. Tarokh, H. Jafarkhani, "A differential detection scheme for transmit diversity," *IEEE JSAC* 18(7):1169–1174, 2000. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
13. D. Tse, P. Viswanath (ref. 1), §3.3 (transmit diversity, Alamouti, MRT), §8.3 (linear receivers: ZF, MMSE, MMSE-SIC; MMSE SINR formula). (textbook)
14. Verification: `tools/verify/s8_alamouti_mimo.py` (W5-S8). (numerical check)
