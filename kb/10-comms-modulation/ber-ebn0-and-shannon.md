---
title: Bit error rate, Eb/N0 and the Shannon limit
domain: 10-comms-modulation
slug: ber-ebn0-and-shannon
tags: [BER, Eb/N0, Es/N0, SNR, C/N0, Q-function, erfc, BPSK, QPSK, QAM, FSK, DPSK, Shannon, capacity, spectral-efficiency, fading]
prerequisites:
  - ../00-math-foundations/decibels-and-log-units.md
  - ../00-math-foundations/probability-random-processes-and-psd.md
  - matched-filter-detection.md
related:
  - digital-modulation-psk-qam-fsk.md
  - channel-coding-fec.md
  - modulation-choice-guide.md
  - packet-framing-protocols.md
  - ../07-noise-linearity/thermal-noise-and-noise-temperature.md
  - ../07-noise-linearity/sensitivity-and-mds.md
  - ../09-propagation-link-budget/link-budget-methodology.md
  - ../09-propagation-link-budget/multipath-fading-doppler.md
  - ../15-lora-ism-radios/lora-sensitivity-and-link-budget.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Bit error rate, Eb/N0 and the Shannon limit

## Questions this page answers
- What is Eb/N0, and why do communications engineers use it instead of plain SNR?
- How do I convert between Eb/N0, Es/N0, SNR, C/N and C/N0 without losing (or gaining) 3 dB?
- Where does BER = Q(√(2Eb/N0)) for BPSK come from, and how is Q related to erfc?
- Why does QPSK have the same bit error rate as BPSK even though it sends twice as many bits?
- What Eb/N0 do I need for a BER of 1e-5 with BPSK, FSK, DPSK, 8-PSK, 16-QAM or 64-QAM?
- How much worse is non-coherent FSK than coherent BPSK, and why?
- How do I turn a required Eb/N0 into a receiver sensitivity in dBm for my 10 kbps rocket link?
- What is the Shannon limit, and why is it −1.59 dB?
- LoRa works at −20 dB SNR — does it beat Shannon?
- How much does a short packet (100–300 bits) cost compared with Shannon's infinite-block limit?
- Why is my simulated BER curve exactly 3 dB away from the textbook curve?
- How bad is Rayleigh fading for BER, and why does the curve become a straight line on a log plot?
- What are entropy and mutual information, and why are soft decisions worth about 2 dB?
- How close can QPSK, 8-PSK or 16-QAM get to Shannon, and what is BICM?
- What is the difference between ergodic and outage capacity, and which applies to a short telemetry packet?
- How much does adaptive modulation (or LoRa spreading-factor adaptation) recover in a fading channel?

## TL;DR
- **Eb/N0** = energy per *information* bit divided by the one-sided noise PSD. It is the bandwidth-independent "fair" power metric: $E_b/N_0 = (C/N_0)/R_b$, i.e. in dB **Eb/N0 = C/N0 − 10 log₁₀ Rb**. SNR depends on which bandwidth you measure noise in: $\mathrm{SNR}=(E_b/N_0)(R_b/B_N)$.
- Key results on AWGN (Gray mapping, coherent detection unless stated), all verified by Monte-Carlo in `tools/verify/comms_ber_awgn.py`:

  | Scheme | BER formula | Eb/N0 @ 1e-3 | @ 1e-5 | @ 1e-6 |
  |---|---|---|---|---|
  | BPSK, QPSK | $Q(\sqrt{2E_b/N_0})$ | 6.8 dB | **9.6 dB** | 10.5 dB |
  | DBPSK (differential detection) | $\tfrac12 e^{-E_b/N_0}$ | 7.9 | 10.3 | 11.2 |
  | Coherent BFSK / coherent OOK (avg Eb) | $Q(\sqrt{E_b/N_0})$ | 9.8 | 12.6 | 13.5 |
  | Non-coherent BFSK | $\tfrac12 e^{-E_b/2N_0}$ | 10.9 | **13.4** | 14.2 |
  | 8-PSK | $\approx\tfrac23 Q(\sqrt{6E_b/N_0}\sin\tfrac{\pi}{8})$ | 10.0 | 13.0 | 14.0 |
  | 16-QAM | $\approx\tfrac34 Q(\sqrt{\tfrac45 E_b/N_0})$ | 10.5 | 13.4 | 14.4 |
  | 64-QAM | $\approx\tfrac{7}{12} Q(\sqrt{\tfrac{2}{7} E_b/N_0})$ | 14.8 | 17.8 | 18.8 |
  | Non-coherent 128-ary FSK (≈ LoRa SF7 core) | integral, §Level 2 | 4.5 | 6.3 | 6.9 |
- **Shannon–Hartley:** $C = B\log_2(1+S/N)$. With $\eta=R_b/B$ it becomes $E_b/N_0 \ge (2^\eta-1)/\eta$: **0 dB at 1 b/s/Hz, 1.76 dB at 2, 5.7 dB at 4, and −1.59 dB (= ln 2) as η → 0**. Nothing beats this; LoRa does not (it runs at ≈ 6 dB Eb/N0 at η ≈ 0.002–0.04 b/s/Hz).
- Uncoded BPSK at 1e-5 sits **≈ 9.6 − (−1.6) ≈ 11.2 dB** from the ultimate limit; that gap is what coding (K=7 conv ≈ 5.4 dB, turbo/LDPC within ≈ 1 dB of the rate-limited bound) recovers. Binary-input rate-½ codes cannot go below **0.19 dB**; short blocks cost extra (≈ 2.4 dB for 100 information bits at rate ½, WER 1e-4).
- **Sensitivity** = −174 dBm/Hz + NF + 10 log₁₀ Rb + Eb/N0(required) + implementation loss. A 10 kbps uncoded BPSK link at 1e-5 with NF = 6 dB needs **−118.4 dBm** before implementation loss.
- **Flat Rayleigh fading** turns the waterfall into a straight line: BPSK needs ≈ **44 dB** average Eb/N0 for 1e-5 (vs 9.6 dB on AWGN). The cure is diversity, interleaving + coding, or margin — not a better modulation.
- **Fading capacity** (10 dB mean SNR): ergodic 2.91 b/s/Hz (AWGN 3.46), but the **1 % outage capacity is 0.14 b/s/Hz**. A short packet sees outage, and 1 b/s/Hz at 1 % outage needs 20 dB mean SNR. Two- and four-branch diversity raise $C_{1\%}$ to 1.31 and 3.21 b/s/Hz. Adaptive QAM recovers most of the ergodic figure; LoRa's SF ladder is the same idea in 2.5 dB steps.
- **Information theory in one line each:** entropy = bits needed to describe a source; capacity = maximum mutual information; hard decisions cost 1.6 dB at rate ½ (1.96 dB as r → 0); 16-QAM sits 0.3 dB from Shannon at 2 b/symbol, and Gray BICM loses only 0.2 dB more.

## Intuition (no math)
A digital receiver makes a decision every symbol: "which of the allowed waveforms did the transmitter most likely send?" Thermal noise nudges the received point away from where it should be. An error happens when the nudge pushes it across the decision boundary to the region of a different symbol. Two things decide how often that happens:

1. **How far apart the allowed signals are** (their Euclidean distance in "signal space" — see [digital modulation](digital-modulation-psk-qam-fsk.md)).
2. **How big the noise nudges are** (the noise standard deviation after the receiver's filter).

For Gaussian noise the probability of a large nudge falls off extremely fast (like $e^{-x^2/2}$), which is why BER curves plunge — a "waterfall" — once the signal is a bit stronger than the noise. Every extra dB near 1e-5 buys roughly a factor of 10 in error rate for BPSK.

Why energy **per bit** rather than signal power? Because the receiver's matched filter collects all the energy of a symbol no matter how long the symbol lasts. Halve the bit rate and each bit lasts twice as long, so it carries twice the energy for the same transmitter power — same BER at half the power. Eb/N0 bakes this in, so a 300 b/s link and a 10 Mb/s link that use the same modulation have the same BER curve versus Eb/N0. Plain SNR does not: it depends on how wide a filter you measured the noise with.

Shannon's result is a speed limit, not a modulation. It says that for a given ratio of signal power to noise *per unit of bandwidth*, there is a maximum rate of error-free information flow, and it can be approached only with long, clever codes whose transmitted signals look like noise. If bandwidth is free (η → 0), the best you can ever do is 0.693 J of bit energy per unit of noise PSD — the famous −1.59 dB. Everything we build sits some dB to the right of that line; channel coding closes the gap, spreading or low-rate modulation trades bandwidth for it.

## The math

### Level 1 — definitions, units and the conversions

| Symbol | Meaning | Unit |
|---|---|---|
| $C$ (or $S$, $P_r$) | received carrier/signal power | W |
| $N_0$ | one-sided noise power spectral density, $N_0 = kT_{sys}$ | W/Hz |
| $R_b$, $R_s$ | information bit rate, symbol rate | bit/s, symbol/s (baud) |
| $M$, $k=\log_2 M$ | constellation size, coded bits per symbol | – |
| $r$ (or $R$) | FEC code rate (information bits / coded bits) | – |
| $E_b = C/R_b$ | energy per information bit | J |
| $E_s = C/R_s = k\,r\,E_b$ | energy per channel symbol | J |
| $E_c = r\,E_b$ | energy per coded bit | J |
| $B_N$ | noise bandwidth of the measurement or receiver filter | Hz |

The noise power in a (real, passband) bandwidth $B_N$ is $N = N_0 B_N$. At $T_0=290$ K, $kT_0 = -174$ dBm/Hz (see [thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md)); with noise figure NF, $N_0 = -174 + \mathrm{NF}$ dBm/Hz.

**The conversion chain (all in dB):**
$$\frac{C}{N_0}\,[\mathrm{dB\text{-}Hz}] = C\,[\mathrm{dBm}] - N_0\,[\mathrm{dBm/Hz}]$$
$$\frac{E_b}{N_0} = \frac{C}{N_0} - 10\log_{10}R_b \qquad \frac{E_s}{N_0} = \frac{E_b}{N_0} + 10\log_{10}(k\,r)$$
$$\mathrm{SNR} = \frac{C}{N} = \frac{E_b}{N_0} + 10\log_{10}\frac{R_b}{B_N} = \frac{E_s}{N_0} + 10\log_{10}\frac{R_s}{B_N}$$

So $E_s/N_0 = \mathrm{SNR}$ **only** when the noise bandwidth equals the symbol rate — which is exactly the case for an ideal matched filter (noise bandwidth of a matched filter for a pulse of duration $T_s$ is $1/T_s$ in passband terms) [6]. When someone quotes "SNR" without saying in what bandwidth, you cannot convert it to Eb/N0.

**The Q-function.** For a standard normal variable $Z\sim\mathcal N(0,1)$,
$$Q(x) = P(Z>x) = \frac{1}{\sqrt{2\pi}}\int_x^\infty e^{-u^2/2}\,du = \tfrac12\,\mathrm{erfc}\!\left(\frac{x}{\sqrt2}\right).$$
Useful facts: $Q(0)=0.5$; $Q(x)\approx \dfrac{e^{-x^2/2}}{x\sqrt{2\pi}}$ for $x>3$ (within 10 %); Chernoff bound $Q(x)\le\tfrac12 e^{-x^2/2}$; $Q(4.265)=10^{-5}$, $Q(4.753)=10^{-6}$.

**The master formula for binary signalling.** Two equally likely signals separated by Euclidean distance $d$ in signal space, white Gaussian noise of variance $N_0/2$ per dimension, minimum-distance (maximum-likelihood) decision:
$$P_b = Q\!\left(\frac{d/2}{\sqrt{N_0/2}}\right) = Q\!\left(\sqrt{\frac{d^2}{2N_0}}\right).$$
- Antipodal (BPSK): $s_{0,1}=\pm\sqrt{E_b}$, $d^2 = 4E_b$ → $P_b=Q(\sqrt{2E_b/N_0})$.
- Orthogonal (coherent BFSK): $d^2 = 2E_b$ → $P_b=Q(\sqrt{E_b/N_0})$, 3 dB worse.
- On-off (OOK) with average energy $E_b$ (on-energy $2E_b$, off 0): $d^2=2E_b$ → same as orthogonal.

The ratio $d_{min}^2/E_b$ is the *power efficiency* of a constellation; all the dB differences in the TL;DR table come from it (plus nearest-neighbour counts).

### Level 1½ — from a received power to a bit error rate, arithmetic only
The table and the Q-function above reduce to four subtractions and one table look-up.
1. **Noise density:** N0 = −174 + NF (dBm/Hz).
2. **Carrier-to-noise density:** C/N0 = C − N0 (dB-Hz).
3. **Energy per bit:** Eb/N0 = C/N0 − 10 log Rb (dB).
4. **Bit error rate:** convert Eb/N0 to linear and, for BPSK, read Pb = Q(√(2Eb/N0)) from a Q table.
- **Backwards:** a Q table gives Q(4.265) = 10⁻⁵. So BPSK needs 2Eb/N0 = 4.265² = 18.2, i.e. Eb/N0 = **9.6 dB**, and the link needs C/N0 = 9.6 + 10 log Rb.

*Worked number (verified, `tools/verify/s18b_level15_numbers.py`).* A −120 dBm signal, NF 6 dB, 9600 b/s BPSK: N0 = −168 dBm/Hz, C/N0 = **48.0 dB-Hz**, Eb/N0 = 48.0 − 39.8 = **8.18 dB** (6.58 linear). Then √(2 × 6.58) = 3.63 and Pb = Q(3.63) ≈ **1.4 × 10⁻⁴**. For 10⁻⁵ the link needs C/N0 = 49.4 dB-Hz, i.e. 1.4 dB more signal.

### Level 2 — derivations

**BPSK from first principles.** Transmit $s(t)=\pm\sqrt{2E_b/T_b}\cos(2\pi f_c t)$ for $0\le t<T_b$. Receive $r(t)=s(t)+w(t)$ with $w$ white Gaussian, two-sided PSD $N_0/2$. Correlate with the unit-energy basis $\phi(t)=\sqrt{2/T_b}\cos(2\pi f_c t)$ (this is the [matched filter](matched-filter-detection.md)):
$$z = \int_0^{T_b} r(t)\phi(t)\,dt = \pm\sqrt{E_b} + n, \qquad n=\int_0^{T_b} w(t)\phi(t)\,dt.$$
$n$ is Gaussian with mean 0 and variance $E[n^2]=\iint \tfrac{N_0}{2}\delta(t-u)\phi(t)\phi(u)\,dt\,du = \tfrac{N_0}{2}\int\phi^2 = N_0/2$. With the threshold at zero (optimal for equal priors), an error given "+" was sent is $P(n<-\sqrt{E_b}) = Q(\sqrt{E_b}/\sqrt{N_0/2}) = Q(\sqrt{2E_b/N_0})$. By symmetry this is the total BER [1 §4.3], [2 ch. 9 eq. 9.9–9.10 (written with erfc)].

**QPSK = two BPSKs.** QPSK puts one bit on the cosine and one on the sine carrier. The two basis functions are orthogonal, so the noise projections on them are independent, and each rail is a BPSK with energy $E_s/2 = E_b$ per bit. Hence $P_b = Q(\sqrt{2E_b/N_0})$, identical to BPSK *per bit*; the symbol error rate is $P_s = 1-(1-P_b)^2\approx 2P_b$. At equal $E_s/N_0$, QPSK is 3 dB worse than BPSK — because each symbol's energy is shared by two bits. This is the single most common confusion in forum threads [11].

**M-PSK.** Points $\sqrt{E_s}e^{j2\pi m/M}$. The nearest neighbours are at distance $d=2\sqrt{E_s}\sin(\pi/M)$; each point has two of them, so by the union bound
$$P_s \approx 2Q\!\left(\sqrt{2E_s/N_0}\,\sin\frac{\pi}{M}\right), \qquad P_b\approx \frac{P_s}{k}\ \text{(Gray)}.$$
The exact symbol error probability has Craig's single finite integral [12]:
$$P_s = \frac1\pi\int_0^{(M-1)\pi/M}\exp\!\left(-\frac{E_s}{N_0}\frac{\sin^2(\pi/M)}{\sin^2\theta}\right)d\theta,$$
verified against simulation for 8-PSK in the script. Going from QPSK to 8-PSK costs $10\log_{10}\frac{2\sin^2(\pi/4)}{3\sin^2(\pi/8)} \approx 3.6$ dB of Eb/N0 for 1.5× the bits per symbol.

**Square M-QAM.** A square $M$-QAM is two independent $\sqrt M$-level PAMs (I and Q). For $L$-PAM with levels $\pm1,\pm3,\dots,\pm(L-1)$ times $d/2$, the symbol error is $2(1-1/L)Q(\sqrt{d^2/2N_0})$ (inner points have two neighbours, the two outer ones have one). Average symbol energy of the QAM is $E_s = (M-1)d^2/6$. Substituting and Gray-mapping:
$$P_b \approx \frac{4}{k}\left(1-\frac{1}{\sqrt M}\right)Q\!\left(\sqrt{\frac{3k}{M-1}\frac{E_b}{N_0}}\right).$$
This nearest-neighbour form is accurate below $P_b\approx10^{-2}$ (checked against Monte-Carlo for 16- and 64-QAM to within the MC error) [1 §4.3], [3]. Each doubling of $M$ (one more bit/symbol) costs ≈ 3 dB of $E_s/N_0$ per added bit at high order — the price of bandwidth efficiency.

**Coherent orthogonal BFSK.** Two tones with spacing $\Delta f = 1/(2T_b)$ (the minimum for coherent orthogonality) or any multiple. Correlate against both; the decision variable $z_1-z_0$ has signal $\pm\sqrt{E_b}$ and noise variance $N_0$ (two independent $N_0/2$ terms), so $P_b = Q(\sqrt{E_b}/\sqrt{N_0}) = Q(\sqrt{E_b/N_0})$ — the $d^2=2E_b$ case.

**Non-coherent BFSK.** The receiver does not know the carrier phase, so it measures the *envelope* at each tone (tones must now be spaced by $1/T_b$ or a multiple for orthogonality with unknown phase). Normalise so the complex noise at each correlator has variance $N_0$. The noise-only branch envelope $R_0$ is Rayleigh, $P(R_0>r)=e^{-r^2/N_0}$; the signal branch envelope $R_1$ is Rician with $p(r)=\frac{2r}{N_0}e^{-(r^2+E_b)/N_0}I_0(2r\sqrt{E_b}/N_0)$. An error occurs when $R_0>R_1$:
$$P_b = \int_0^\infty p(r)\,e^{-r^2/N_0}\,dr = \tfrac12 e^{-E_b/2N_0},$$
where the integral is done by completing the square and using $\int_0^\infty x e^{-a x^2}I_0(bx)dx = \frac{1}{2a}e^{b^2/4a}$ [1 §4.5], [3]. At 1e-5 it needs 13.35 dB — only 0.75 dB more than *coherent* BFSK, but 3.8 dB more than BPSK. This is why cheap FSK radios (no carrier recovery) pay about 4 dB versus a coherent PSK design at the same rate.

**DBPSK.** Information is in the phase *change* between consecutive symbols; the receiver computes $\mathrm{Re}\{z_k z_{k-1}^*\}$. The previous symbol acts as a noisy phase reference. The exact result is $P_b=\tfrac12 e^{-E_b/N_0}$ [1 §4.5] — 0.75 dB worse than BPSK at 1e-5 (10.34 vs 9.59 dB), in exchange for no carrier-phase recovery and immunity to 180° phase ambiguity.

**Non-coherent M-ary orthogonal FSK** (the core of chirp spread spectrum / LoRa, see [spread spectrum](spread-spectrum-dsss-fhss-css.md)). With one Rician branch and $M-1$ Rayleigh branches,
$$P_s = 1-\int_0^\infty p_{\text{Rice}}(r)\left(1-e^{-r^2/N_0}\right)^{M-1}dr,\qquad P_b=\frac{M/2}{M-1}P_s,$$
with $E_s = kE_b$. The equivalent closed form $P_s=\sum_{n=1}^{M-1}(-1)^{n+1}\binom{M-1}{n}\frac{1}{n+1}e^{-\frac{n}{n+1}E_s/N_0}$ is exact but numerically useless beyond $M\approx 30$ (catastrophic cancellation — the verify script integrates instead). Required Eb/N0 at 1e-5 falls as $M$ grows: 13.4 dB ($M=2$), 10.6 (4), 8.1 (16), 6.3 dB (128). As $M\to\infty$ the requirement tends to ln 2 = −1.59 dB — orthogonal signalling achieves the Shannon limit, at the cost of bandwidth growing like $M/\log_2 M$ [1 §4.4], [4].

### Level 3 — generalisations, bounds and where approximations break

**Union bound and nearest-neighbour approximation.** For any constellation, $P_s\le \frac1M\sum_i\sum_{j\ne i}Q(d_{ij}/\sqrt{2N_0})$. At high SNR only the minimum-distance terms matter: $P_s\approx \bar N_{min}\,Q(d_{min}/\sqrt{2N_0})$, with $\bar N_{min}$ the average number of nearest neighbours. Bit errors: with Gray mapping, a nearest-neighbour symbol error flips one bit, so $P_b\approx P_s/k$. With natural binary mapping $P_b$ can be up to ~2× worse for PSK/QAM.

**Low-SNR breakdown.** The Gray approximations overestimate or underestimate by >10 % above $P_b\approx 10^{-2}$; use exact expressions (or simulation) near the operating point of strong codes, where the *raw* channel BER is 1e-2 to 1e-1.

**Fading.** In flat Rayleigh fading the instantaneous SNR $\gamma$ is exponential with mean $\bar\gamma$. Averaging the AWGN BER over it gives, for coherent BPSK with perfect channel knowledge,
$$\bar P_b = \tfrac12\left(1-\sqrt{\frac{\bar\gamma}{1+\bar\gamma}}\right)\approx\frac{1}{4\bar\gamma},$$
and for non-coherent BFSK $\bar P_b = 1/(2+\bar\gamma)$ [5 ch. 6], [13]. The BER now falls only 10× per 10 dB — the error rate is dominated by deep fades, not by noise. For 1e-5 you need ≈ 44 dB (BPSK) or 50 dB (NC-FSK) average Eb/N0 (script §6). A rocket link with a spinning vehicle and ground multipath sees fading-like dropouts, which is why interleaving + FEC and antenna/ground-station diversity matter more than the last dB of modulation efficiency (see [channel coding](channel-coding-fec.md), [multipath](../09-propagation-link-budget/multipath-fading-doppler.md)).

**Shannon–Hartley.** For a channel of bandwidth $B$ with average signal power $S$ and white Gaussian noise power $N=N_0B$, Shannon's Theorem 17 gives the capacity [7 §25]
$$C = B\log_2\!\left(1+\frac{S}{N}\right)\ \text{bit/s}.$$
*Sketch of why:* a signal of bandwidth $B$ and duration $T$ is described by $2BT$ independent samples (Shannon §19 — the sampling theorem as geometry). A codeword is a point in $2BT$-dimensional space; noise adds a random vector whose length concentrates at $\sqrt{2BT\,N}$, so the received point lies on a thin shell around the sent one; the received vector lies in a sphere of radius $\sqrt{2BT(S+N)}$. The number of non-overlapping noise spheres that fit is the volume ratio $\left(\frac{S+N}{N}\right)^{BT}$, i.e. $BT\log_2(1+S/N)$ bits in time $T$. Shannon also showed the capacity-achieving signals must look statistically like white noise [7 §25] — a point relevant to both PAPR and "noise-like" spread-spectrum signals.

**Spectral efficiency and the Eb/N0 bound.** Let $\eta=R_b/B$ (bit/s/Hz). Writing $S=E_bR_b$ and $N=N_0B$, reliable communication at $R_b\le C$ requires $\eta\le\log_2(1+\eta E_b/N_0)$, i.e.
$$\boxed{\ \frac{E_b}{N_0}\ \ge\ \frac{2^\eta-1}{\eta}\ }\qquad \lim_{\eta\to0}\frac{2^\eta-1}{\eta}=\ln2 = 0.693 = -1.59\ \mathrm{dB}.$$
Values: η = 0.5 → −0.82 dB; 1 → 0 dB; 2 → 1.76 dB; 4 → 5.74 dB; 6 → 10.2 dB; 8 → 15.0 dB. Plotting uncoded schemes on the (Eb/N0, η) plane (Nyquist bandwidth $B=R_s$): BPSK (9.6 dB, 1 b/s/Hz), QPSK (9.6, 2), 8-PSK (13.0, 3), 16-QAM (13.4, 4), 64-QAM (17.8, 6), NC-BFSK (13.4, ≈0.5), 128-FSK (6.3, ≈0.05). Everything is 7–11 dB to the right of the bound at 1e-5. Schemes left of η ≈ 1 are *power-limited* (deep space, rockets at range, LoRa); right of it are *bandwidth-limited* (Wi-Fi, cable) [1 §4.6], [3 ch. 9].

**Constrained-input capacity.** If the channel input is restricted to ±1 (BPSK, the case for every binary code on a BPSK/QPSK link), the capacity is lower. For code rate $r$, the minimum Eb/N0 is where $C_{\text{BI-AWGN}}(rE_b/N_0)=r$. Computed by Gauss–Hermite quadrature in the script: **0.19 dB (r = ½), −0.50 dB (⅓), −0.79 dB (¼), −1.07 dB (⅙)**, matching the CCSDS Green Book values 0.2 / −0.5 / −0.8 / −1.1 dB [8 §3.3]. So a rate-½ binary code has an inherent 1.8 dB handicap versus the ultimate limit.

**Finite block length.** Shannon's limit assumes infinitely long codewords. For $n$ channel uses and word error probability $\varepsilon$, the normal approximation of Polyanskiy–Poor–Verdú [9] gives $\log_2 M^*\approx nC-\sqrt{nV}\,Q^{-1}(\varepsilon)+\tfrac12\log_2 n$ with channel dispersion $V=\frac{P(P+2)}{2(P+1)^2}\log_2^2 e$ for the real AWGN channel. At rate ½ and WER 1e-4 it gives minimum Eb/N0 ≈ **3.0 dB for 64 information bits, 2.4 dB for 100, 1.6 dB for 256, 0.8 dB for 1000, 0.3 dB for 10 000**. The CCSDS Green Book, using Shannon's 1959 sphere-packing bound instead, quotes ≈ 1.3 dB between 100- and 1000-bit blocks (normal approximation: 1.6 dB) and "just over 0.5 dB" from 1000 to 10 000 (normal approximation: 0.57 dB) [8 §3.3.2]. Rocket telemetry packets are short (32–255 bytes), so expect to live 1.5–3 dB above the asymptotic limit even with a perfect code.

### Level 3b — information-theory basics: entropy, mutual information, constellation capacity and signal-space geometry (W5-S8)
Numbers in this subsection are from `tools/verify/s8_info_coding.py` (16/16 PASS).

**Entropy.** A source emitting symbol i with probability $p_i$ has entropy $H=-\sum_ip_i\log_2p_i$ bits per symbol, the minimum average number of bits needed to describe it losslessly (Shannon's source-coding theorem) [16].
- Binary entropy: $H_2(p)=-p\log_2p-(1-p)\log_2(1-p)$, for example $H_2(0.11)=0.50$.
- *Telemetry example* (illustrative probabilities): a flight-state field with five states at probabilities 0.60/0.20/0.10/0.05/0.05 has H = 1.67 bits. A Huffman code reaches 1.70 bits, against 3 bits fixed-length.
- Source coding like this is how FT8 fits a QSO into 77 bits ([weak-signal modes](weak-signal-digital-modes.md)). It matters as much as channel coding when every bit costs energy.

**Mutual information and capacity.** For channel input X and output Y, $I(X;Y)=H(Y)-H(Y|X)$ is the number of bits per channel use that Y reveals about X. **Capacity is the maximum of I over the input distribution**, and the channel-coding theorem says every rate below it is achievable with vanishing error.
- **BSC** with crossover p: $C=1-H_2(p)$.
- **Real AWGN with Gaussian input**: $C=\tfrac12\log_2(1+\mathrm{SNR})$ per real dimension. Two dimensions per complex sample, at 2B real samples per second, gives Shannon–Hartley.
- **Hard versus soft decisions.** Slicing BPSK to bits turns the channel into a BSC with $p=Q(\sqrt{2E_c/N_0})$. At rate ½ the minimum Eb/N0 rises from **0.19 dB (soft) to 1.77 dB (hard)**, a 1.6 dB loss. As $r\to0$ the loss tends to $10\log_{10}(\pi/2)$ = **1.96 dB**. This is the information-theoretic root of the "soft decisions are worth about 2 dB" rule on the [coding page](channel-coding-fec.md#level-2--the-classical-codes).

**Constellation-constrained (CM) capacity.** With equiprobable points from a fixed constellation $\mathcal S$ of size M,
$$C_\mathcal S=\log_2M-\mathbb E\left[\log_2\frac{\sum_{s'\in\mathcal S}e^{-|y-s'|^2/N_0}}{e^{-|y-s|^2/N_0}}\right]\quad\text{b/symbol}.$$
At Es/N0 = 10 dB: QPSK 1.99, 8-PSK 2.68, 16-QAM 3.17, against the Shannon 3.46 b/symbol. For 2 b/symbol, Shannon needs 4.77 dB; 16-QAM CM needs 5.09 dB. At 2.5 b/symbol 16-QAM needs 7.26 dB and 8-PSK 8.71 dB, because QAM uses the amplitude dimension.
- **BICM** (bit-interleaved coded modulation, Caire–Taricco–Biglieri [17]) feeds a binary code through an interleaver and a Gray mapper, and the demapper hands per-bit LLRs to the decoder. Its capacity is the sum of the per-bit mutual informations. With Gray 16-QAM it is a further 0.2 dB from CM at 2 b/symbol (5.30 dB) and indistinguishable at 10 dB. That small loss is why Wi-Fi, LTE/NR and DVB-S2 all use BICM with LDPC/turbo codes rather than TCM.
- **Shaping gain.** A uniform square constellation can never reach Shannon at high SNR. The ultimate shaping loss is $10\log(\pi e/6)$ = **1.53 dB**, recovered only by making the points Gaussian-like (probabilistic shaping, as in 5G/optical systems).

**Signal-space geometry.** A block of n real noise samples is a random vector whose squared length per dimension, $\|\mathbf n\|^2/n$, has mean $\sigma^2$ and standard deviation $\sigma^2\sqrt{2/n}$: 0.45 at n = 10, 0.045 at n = 1000 (simulated). In high dimension the noise therefore lives on a thin shell (**sphere hardening**). That is why the sphere-packing argument in the Shannon–Hartley sketch above becomes exact as n → ∞. A good code places $2^{nR}$ codewords so that their noise shells do not overlap, and long codes are needed to make the shells thin. Short blocks have "fat" shells, which is the finite-length penalty of the previous paragraph seen geometrically.

### Level 3c — capacity of fading channels: ergodic, outage, and adaptive modulation (W5-S8)
Numbers are from `tools/verify/s8_outage_capacity.py` (29/29 PASS). Take a flat Rayleigh channel with instantaneous SNR $\gamma=\rho|h|^2$, $|h|^2\sim$ Exp(1), and mean SNR ρ. What "capacity" means depends on how long a codeword is compared with the fade and on who knows $h$ [18], [19].

**1. Ergodic capacity (codeword spans many fades, receiver knows h).** $\bar C=\mathbb E[\log_2(1+\gamma)]=\log_2e\cdot e^{1/\rho}E_1(1/\rho)$. At 10 dB it is **2.91 b/s/Hz**, against 3.46 on AWGN (derivation: [MIMO page §4](mimo-capacity-and-channel-estimation.md#level-2--derivations)). By Jensen's inequality fading always lowers it, but only modestly.

**2. Transmitter also knows h.** The transmitter can adapt power over time by water-filling: $P(\gamma)/\bar P=(1/\gamma_0-1/\gamma)^+$, with the cutoff $\gamma_0$ set by the average-power constraint (Goldsmith–Varaiya [20]). At 10 dB it gives **2.98 b/s/Hz** (cutoff −1.2 dB), only 0.07 above receiver-only CSI. At 0 dB it gives 1.03 against 0.86: adaptation pays at low SNR.
- **Channel inversion** (constant received SNR, the "power control" a mobile network uses) has capacity $\log_2(1+1/\mathbb E[1/\gamma])$. For Rayleigh fading $\mathbb E[1/\gamma]=\infty$, so it gives **zero**: you cannot invert the deepest fades.
- **Truncated inversion** (invert only when γ > γ₀, otherwise stay silent) gives **2.66 b/s/Hz** at 10 dB, with the optimum cutoff at 4.8 dB and the link off 26 % of the time.

**3. Outage capacity (codeword shorter than a fade: one packet, one channel draw).** The rate R fails whenever $\log_2(1+\gamma)<R$:
$$P_\text{out}(R)=1-\exp\!\left(-\frac{2^R-1}{\rho}\right),\qquad C_\varepsilon=\log_2\!\left(1-\rho\ln(1-\varepsilon)\right)\approx\log_2(1+\rho\varepsilon).$$
- At 10 dB: $C_{1\%}$ = **0.14 b/s/Hz** and $C_{10\%}$ = 1.04, against the 2.91 ergodic. Delivering 1 b/s/Hz with 1 % outage needs **20.0 dB** mean SNR (0 dB on AWGN). That 20 dB is the [Rayleigh fade margin](../09-propagation-link-budget/link-margin-availability.md) seen from the capacity side. At 10 dB, $P_\text{out}$(1 b/s/Hz) = 9.5 %, the same number as the KB's "10 dB margin ⇒ 9.5 % loss".
- With L-branch MRC, $C_\varepsilon=\log_2(1+\rho\,G_L^{-1}(\varepsilon))$, where $G_L^{-1}$ is the inverse regularised gamma function. At 10 dB and 1 %: **0.14 → 1.31 (L = 2) → 3.21 b/s/Hz (L = 4)**. Diversity, not power, is what fixes outage.
- *Which one applies to telemetry?* A LoRa packet (50 ms–2 s) is usually shorter than the fading coherence time at a static ground station, so **outage** is the right model. A long interleaved stream through fast fading sees **ergodic** capacity.

**4. Adaptive modulation and coding (the practical version of item 2).** Goldsmith–Chua [21] bound M-QAM's BER by $\mathrm{BER}\le0.2\exp\!\left(-\frac{1.5\gamma}{M-1}\right)$. This is conservative: the exact 16- and 64-QAM BER at the bound's SNR is 4×10⁻⁴ and 3×10⁻⁴ for a 10⁻³ target. Solving for M gives $M(\gamma)=1+K\gamma$ with $K=-1.5/\ln(5\,\mathrm{BER})$ = 0.283 at 10⁻³, a **5.5 dB SNR gap** to Shannon.
- **Continuous rate with power water-filling** on Kγ, at 20 dB mean SNR: **4.22 b/s/Hz**, against 5.88 ergodic capacity.
- **Discrete rates at constant power** ({off, BPSK, QPSK, 16-, 64-, 256-QAM}, each used only above the SNR where it meets 10⁻³): **3.25 b/s/Hz**, with the link off 4.7 % of the time.
- **Fixed BPSK** cannot meet 10⁻³ average BER at 20 dB mean SNR at all (2.5×10⁻³). It needs **24.0 dB**.

Adaptation recovers most of the fading loss without diversity. It needs a feedback path and a channel that changes more slowly than the feedback loop.

**5. LoRa spreading-factor adaptation as the analogue.** Each SF step trades a factor ≈ 2 in rate for 2.5 dB of SNR threshold (canonical −7.5 … −20 dB, [canonical values](../00-math-foundations/canonical-values-and-conventions.md)). On slow Rayleigh fading, with a packet lost whenever the instantaneous SNR is below threshold, the goodput $R_b(\mathrm{SF})(1-P_\text{out})$ is maximised by:

| Mean SNR (125 kHz) | Best-goodput SF | Its goodput / P_out | Fixed SF12 goodput / P_out |
|---|---|---|---|
| −20 dB | SF12 | 108 b/s / 63 % | 108 b/s / 63 % |
| −15 dB | SF10 | 359 b/s / 63 % | 214 b/s / 27 % |
| −10 dB | SF8 | 1150 b/s / 63 % | 265 b/s / 9.5 % |
| −5 dB | SF7 | 3116 b/s / 43 % | 284 b/s / 3.1 % |
| 0 dB | SF7 | 4578 b/s / 16 % | 290 b/s / 1.0 % |

Throughput-optimal adaptation runs at **≈ 63 % packet loss**: with Rayleigh fading the optimum puts the mean SNR exactly at threshold. That is right for bulk data with ARQ and wrong for telemetry, where every packet counts. A reliability-constrained rule ("the fastest SF with $P_\text{out}\le1\%$") needs the mean SNR **20 dB above threshold**.
- LoRaWAN's network-side **ADR** does a cautious version: it takes the best SNR of the last ≈ 20 uplinks, subtracts the SF's threshold and a margin (10 dB in the Semtech-style algorithm; 15 dB by default in The Things Stack), and steps SF down by one per 3 dB (2.5 dB in TTS) of excess [22]. For example, a best SNR of −5 dB at SF12 with a 10 dB margin gives ⌊(−5 + 20 − 10)/3⌋ = 1 step, to SF11.
- **For a rocket, ADR is too slow and in the wrong direction.** Range doubles in seconds (6 dB, i.e. 2.4 SF steps), and there is no uplink history to learn from. Fix the SF from the worst-case link budget plus fade margin, or pre-schedule it by flight phase (for example SF7 on the pad, SF10–12 for ascent and descent at range) with a multi-SF gateway or one receiver per SF at the ground station ([rocket radio design](../15-lora-ism-radios/rocket-telemetry-radio-design.md)).

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $E_b/N_0 = C/N_0 - 10\log R_b$ (dB) | always; $R_b$ = *information* rate | 10 kbps → subtract 40 dB |
| $E_s/N_0 = E_b/N_0 + 10\log(k r)$ | $k$ bits/symbol, code rate $r$ | QPSK uncoded: +3.01 dB |
| $\mathrm{SNR}=E_s/N_0 + 10\log(R_s/B_N)$ | $B_N$ = noise bandwidth used for SNR | RRC β=0.35, $B_N\approx R_s$ for matched filter |
| $P_{sens} = -174 + \mathrm{NF} + 10\log R_b + (E_b/N_0)_{req} + L_{impl}$ dBm | AWGN, 290 K | $L_{impl}$ 1–3 dB |
| $P_b = Q(\sqrt{2E_b/N_0})$ | BPSK/QPSK coherent, Gray | 9.6 dB @ 1e-5 |
| $P_b = \tfrac12 e^{-E_b/2N_0}$ | non-coherent BFSK, tone spacing $k/T_b$ | 13.4 dB @ 1e-5 |
| $P_b = \tfrac12 e^{-E_b/N_0}$ | DBPSK | 10.3 dB @ 1e-5 |
| $E_b/N_0 \ge (2^\eta-1)/\eta$ | Shannon, infinite blocks | −1.59 dB as η→0 |
| $\bar P_b\approx 1/(4\bar\gamma)$ | BPSK, flat Rayleigh, high SNR | 44 dB @ 1e-5 |
| "each 3 dB of Eb/N0 = 2× data rate at fixed range" | fixed modulation/coding | halve Rb → +3 dB margin |
| near 1e-5, BPSK BER changes ≈ 10× per 1 dB | AWGN only | not in fading |
| $C=1-H_2(p)$ | BSC (hard decisions) | rate ½ needs 1.77 dB vs 0.19 dB soft |
| $C_\varepsilon=\log_2(1-\rho\ln(1-\varepsilon))$ | flat Rayleigh, one fade per codeword | 10 dB, 1 %: 0.14 b/s/Hz |
| $P_\text{out}(R)=1-e^{-(2^R-1)/\rho}$ | flat Rayleigh | 1 b/s/Hz at 10 dB: 9.5 % |
| $\bar C=\log_2e\,e^{1/\rho}E_1(1/\rho)$ | ergodic, receiver CSI | 10 dB: 2.91 b/s/Hz |
| Adaptive QAM gap $K=-1.5/\ln(5\,\mathrm{BER})$ | Goldsmith–Chua bound | 10⁻³: K = 0.283 (5.5 dB) |
| Shaping loss of uniform constellations ≤ 1.53 dB | high SNR | πe/6 |

## Worked examples

### Example 1 — Required received power for a 10 kbps rocket telemetry downlink
Target: BER 1e-5 at $R_b=10$ kbit/s, receiver NF = 6 dB (a module-class receiver; a ground-station LNA could bring this to ≈ 1 dB — see [LNA design](../06-rf-circuits/lna-design.md)).

1. Noise PSD: $N_0 = -174 + 6 = -168$ dBm/Hz.
2. Bit-rate term: $10\log_{10}(10^4) = 40$ dB.
3. Uncoded coherent BPSK: $(E_b/N_0)_{req}=9.59$ dB → $C/N_0 = 49.6$ dB-Hz → $C = -168 + 49.6 = -118.4$ dBm. Add 2 dB implementation loss (imperfect sync, filter mismatch) → **−116.4 dBm**.
4. Non-coherent FSK instead (the usual cheap-radio mode): $13.35 + 2 = 15.4$ dB → **−112.6 dBm** — 3.8 dB worse, i.e. ≈ 65 % of the BPSK range in free space ($10^{-3.76/20}=0.65$).
5. BPSK + K=7, r=½ convolutional code with soft Viterbi decoding (≈ 4.2 dB at 1e-5, union bound and Monte-Carlo in `comms_coding.py`; see [channel coding](channel-coding-fec.md)) → $−168+40+4.2+2 = $ **−121.8 dBm**, now 5.4 dB better than uncoded; note that the *channel symbol rate* doubles to 20 ksym/s, so bandwidth doubles.

At a free-space path loss slope of 20 dB/decade, 5.4 dB is a factor 1.86 in range. (Verified: `comms_ber_awgn.py` §4, `comms_coding.py` §2–3.)

### Example 2 — What Eb/N0 does LoRa actually run at?
The SX127x datasheet lists the demodulator's required SNR (in the 125 kHz channel) as −7.5 dB at SF7 and −20 dB at SF12 [10]. With coding rate 4/5:
- SF7: $R_b = 7\cdot\frac{125\,000}{2^7}\cdot\frac45 = 5469$ b/s. $C/N_0 = -7.5 + 10\log_{10}(125\,000) = -7.5+50.97 = 43.47$ dB-Hz. $E_b/N_0 = 43.47 - 37.38 = $ **6.1 dB**.
- SF12: $R_b = 12\cdot\frac{125\,000}{4096}\cdot\frac45 = 293$ b/s. $C/N_0 = -20 + 50.97 = 30.97$ dB-Hz. $E_b/N_0 = 30.97-24.67 = $ **6.3 dB**. With low-data-rate optimisation (mandatory at SF11/12 on 125 kHz; only SF − 2 = 10 bits per symbol) $R_b=244$ b/s and $E_b/N_0\approx$ **7.1 dB**.

So the required Eb/N0 is ≈ 6 dB at every SF — consistent with non-coherent orthogonal $2^{SF}$-ary signalling (6.3 dB at 1e-5 for M = 128 from the table; LoRa's datasheet criterion and its weak Hamming code shift this a little). The *SNR* is negative only because the information rate is tiny compared with the 125 kHz bandwidth (η = 0.0023 b/s/Hz at SF12). The Shannon bound at that η is −1.59 dB, so LoRa sits ≈ 8 dB from capacity: robust and simple, not magical. Detail belongs to [LoRa sensitivity](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md).

### Example 3 — Capacity of that LoRa channel
At SNR = −7.5 dB (0.178) in 125 kHz: $C = 125\,000\log_2(1.178) = 29.5$ kbit/s, versus the 5.47 kbit/s LoRa SF7 actually delivers. A near-capacity code at the same received power could carry ≈ 5× the data; alternatively, at the same data rate, a good code could work ≈ 6–7 dB weaker (Example 1 step 5 shows that a 1960s-era convolutional code recovers ≈ 5.4 dB of the ≈ 11 dB gap).

### Example 4 — SNR per sample in a simulation
You simulate QPSK at 8 samples per symbol with complex white noise across the full sample rate $f_s = 8R_s$. You set "SNR = 10 dB" as signal power over total noise power per sample. Then $E_s/N_0 = \mathrm{SNR}\cdot f_s/R_s$ → $10 + 10\log_{10}8 = 19.0$ dB, and $E_b/N_0 = 19.0 - 3.0 = 16.0$ dB. If you forget the $f_s/R_s$ factor your BER curve lands 9 dB away from theory. (Complex noise of total variance $\sigma^2$ has $\sigma^2/2$ per I and Q; the matched filter then reduces the in-band noise.)

### Example 5 — 16-QAM versus QPSK in a fixed bandwidth
You have 50 kHz and need 100 kbit/s: η = 2 → QPSK at $R_s = 50$ ksym/s just fits with β ≈ 0 (not practical) — with β = 0.35 you need 67.5 kHz. 16-QAM at 25 ksym/s occupies 33.8 kHz with β = 0.35 and fits, but needs 13.4 dB instead of 9.6 dB Eb/N0 at 1e-5: **3.8 dB more power** to save bandwidth. The Shannon bound at η = 2 is 1.76 dB, so coding could let 16-QAM-class efficiency work at ≈ 5–7 dB.

### Example 6 — what rate can a fading link promise 99 % of the time?
A ground-station receiver sees a mean SNR of 10 dB in a 125 kHz channel with Rayleigh-like fading, and each packet is shorter than a fade.
- **Ergodic thinking:** 2.91 b/s/Hz × 125 kHz = 364 kb/s. That is wrong for single packets.
- **Outage at 1 %:** $C_{1\%}$ = log₂(1 − 10 ln 0.99) = 0.138 b/s/Hz, i.e. **17 kb/s**, about 20× less.
- **Two decorrelated receivers** ([MIMO page](mimo-capacity-and-channel-estimation.md#worked-examples)): with MRC, $C_{1\%}$ = 1.31 b/s/Hz, i.e. **164 kb/s**. Packet-level selection (all a pair of LoRa modules can do) gives 1.04 b/s/Hz, i.e. 130 kb/s.

Diversity buys about 8–10× in guaranteed rate here, far more than 3 dB of extra transmit power would (3 dB more power raises $C_{1\%}$ only from 0.14 to 0.26 b/s/Hz). The same reasoning drives the polarisation- and height-diversity recommendations on the MIMO page.

## Practical notes
- **Implementation loss is real.** Carrier-phase jitter, timing jitter, frequency offset, ADC quantisation, filter mismatch, phase noise and AGC error typically add 1–3 dB over the textbook curve for a careful design; cheap integrated FSK transceivers can be worse. Budget it explicitly in the [link budget](../09-propagation-link-budget/link-budget-methodology.md).
- **Datasheet sensitivity has a definition.** Radio ICs quote sensitivity at a stated BER (0.1 % is common for FSK modes) or packet error rate. Compare radios only at the same criterion; converting 0.1 % BER to 1e-5 costs ≈ 2.4 dB for NC-FSK.
- **BER is not what the user sees.** Telemetry frames are lost when *any* bit is wrong and the CRC fails: $\mathrm{PER}\approx 1-(1-P_b)^{N}$ for $N$ bits with independent errors. See [packet framing](packet-framing-protocols.md).
- **Coding changes the operating point.** A coded link works with raw channel BER of 1e-2 or worse; your demodulator, synchronisers and AGC must function at that SNR, which is often the real limit (the CCSDS Green Book notes some commercial Viterbi decoders' node-sync fails below ≈ 4 dB Eb/N0 [8 §6]).
- **Measure C/N0, not "SNR".** On an SDR ground station, estimate carrier power and the noise floor density separately (dBm and dBm/Hz); their difference is C/N0 in dB-Hz, which converts to Eb/N0 for any bit rate.
- **Gray coding** is essentially free — always use it for PSK/QAM.

## Common mistakes & misconceptions
- **"SNR and Eb/N0 are the same thing."** Only when noise bandwidth equals bit rate. SNR = Eb/N0 + 10 log(Rb/B). LoRa at −20 dB SNR has Eb/N0 ≈ +6 dB.
- **"QPSK needs 3 dB more power than BPSK."** Per bit it needs the same; per symbol it needs 3 dB more because each symbol carries two bits [11].
- **The 3 dB simulation error.** Complex baseband noise with variance $N_0$ total means $N_0/2$ per real dimension. Generating $\sigma = \sqrt{N_0}$ on *each* of I and Q doubles the noise and shifts the curve 3 dB. The MATLAB/Octave AWGN function documents this split explicitly [14].
- **Q vs erfc.** $Q(x)=\tfrac12\mathrm{erfc}(x/\sqrt2)$. Writing $\tfrac12\mathrm{erfc}(\sqrt{2E_b/N_0})$ for BPSK is wrong (it is $\tfrac12\mathrm{erfc}(\sqrt{E_b/N_0})$) — a 3 dB error.
- **Using the coded-bit energy as Eb.** Eb is energy per *information* bit. With rate-½ coding $E_c = E_b/2$; the coding gain must beat this 3 dB "loss" before it helps.
- **One-sided vs two-sided N0.** Textbooks model white noise with two-sided PSD $N_0/2$ over ±∞; the noise power in an RF bandwidth $B$ is $N_0B$. kT = −174 dBm/Hz is the one-sided $N_0$.
- **"LoRa (or DSSS) beats the noise floor / Shannon."** Processing gain lets a signal be demodulated when its power is below the noise power *in the whole occupied bandwidth*, but its Eb/N0 is still positive and well above −1.59 dB.
- **Using AWGN curves for a fading channel.** The difference at 1e-5 is ≈ 35 dB. Either add fade margin from a fading model or design for diversity/interleaving.
- **Forgetting that Shannon's limit assumes infinite block length.** For 100-bit packets the realistic floor is ≈ 2.4 dB, not −1.59 dB or 0.19 dB.
- **Using ergodic capacity for a short packet.** If the packet is shorter than the fade, the relevant number is outage capacity, often 10–20× smaller at 1 % outage.
- **"Channel inversion / power control fixes fading."** Full inversion has zero capacity on Rayleigh because the deepest fades need unbounded power; truncate it (accept outage) or use diversity.
- **Running throughput-optimal rate adaptation on telemetry.** Maximising goodput in Rayleigh fading puts the operating point at ≈ 63 % packet loss. Telemetry needs a reliability-constrained rule (≈ 20 dB above threshold for 1 % loss) or diversity.
- **"Entropy is the number of bits in the field."** A 3-bit flight-state field with skewed probabilities carries ≈ 1.7 bits of information; source coding before channel coding saves energy.
- **Quoting BER at the wrong layer.** Raw demodulator BER, post-FEC BER and packet error rate differ by orders of magnitude; say which one.
- **"A higher carrier frequency means a higher data rate."** The carrier does not appear in $C = B\log_2(1+\mathrm{SNR})$; only the bandwidth and SNR do. A 125 kHz LoRa channel carries the same bits at 433 MHz as at 2.4 GHz. Higher carriers correlate with higher rates for practical reasons: wide channels are only *allocated* there (20–160 MHz Wi-Fi at 2.4/5 GHz, GHz-wide mm-wave bands vs a 1.74 MHz-wide 433 MHz SRD band), and antennas, filters and matching networks are easiest to build with a fractional bandwidth of a few to ~10 % — 10 % of 60 GHz is 6 GHz, 10 % of 433 MHz is 43 MHz. Against that, at fixed antenna gains the free-space path loss rises 20 log f, so the *SNR* term usually falls with frequency ([Friis](../09-propagation-link-budget/friis-free-space-path-loss.md)). (Half-addressed myth from W4-D1, electronics.stackexchange.com/q/504401.)

## How to simulate / verify
- **`tools/verify/comms_ber_awgn.py`** (runs in ~2 s): Monte-Carlo vs closed form for BPSK, QPSK, 8-PSK (plus exact Craig SER), 16/64-QAM, coherent/non-coherent BFSK, DBPSK, non-coherent 8-FSK, OOK; required-Eb/N0 table; Shannon bound; BI-AWGN capacity limits vs CCSDS; finite-block normal approximation; Rayleigh-fading BER; the 10 kbps sensitivity example. All checks PASS.
- **`tools/verify/s8_outage_capacity.py`** (≈ 1 s, 29/29 PASS): outage capacity closed forms vs Monte Carlo (1×1 and L-branch MRC), ergodic with receiver CSI, water-filling in time, channel inversion and truncated inversion, Goldsmith–Chua adaptive QAM (continuous and discrete), LoRa SF-adaptation goodput table and ADR step. Output in `s8_outage_capacity_output.txt`.
- **`tools/verify/s8_info_coding.py`** (≈ 10 s, 16/16 PASS): entropy and Huffman example, hard vs soft binary-input limits, CM/BICM capacity of QPSK/8-PSK/16-QAM, shaping gain, sphere hardening (plus the TCM and LDPC belief-propagation checks used on the coding page).
- **Minimal Python pattern** (the piece most people get wrong is the noise scale):
  ```python
  import numpy as np
  EbN0 = 10**(ebn0_db/10); k = 2              # QPSK: 2 bits/symbol, Es = 1
  N0 = 1/(k*EbN0)
  noise = np.sqrt(N0/2)*(np.random.randn(n) + 1j*np.random.randn(n))
  ```
  At $s$ samples per symbol with unit-energy RRC pulses, scale per-sample noise variance by $s$ (or measure after the matched filter).
- **GNU Radio:** the *Channel Model* block's "noise voltage" $V$ sets the RMS amplitude of the complex noise added to every sample (power split equally between I and Q — confirm by measuring the variance of the block's output with zero input). With signal power $P_s$ per sample and $s$ samples per symbol, $E_s/N_0 = P_s\,s/V^2$, so choose $V=\sqrt{P_s\,s/(E_s/N_0)}$; then measure BER with a known PRBS (see [SDR demodulation](../14-sdr-dsp/software-demodulation.md)).
- **Bench:** a signal generator + calibrated attenuators + the receiver under test; step power down until BER/PER hits the criterion; convert the level to Eb/N0 using a measured noise floor. Compare with the table to find your implementation loss.

## Open questions / gaps
- The Semtech demodulator-SNR figures are specified for 1 % PER on a 64-byte, CR 4/5 test packet (SX1261/2 datasheet, as reported in [LoRa sensitivity](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md)), not for BER 1e-5; the ≈ 6 dB Eb/N0 figure is therefore a packet-level criterion, and domain 15's ideal-receiver simulation gives 5.7–6.7 dB for the same criterion.
- Finite-blocklength numbers use the normal approximation (Gaussian input); for BPSK input at short lengths the bound is slightly higher. A table of exact BI-AWGN finite-length bounds would be a useful addition.
- Non-Gaussian impairments (impulsive noise, interference from co-channel ISM users) are not covered here.

## Sources
1. J. G. Proakis and M. Salehi, *Digital Communications*, 5th ed., McGraw-Hill, 2008 — ch. 4 (§4.1–4.6: optimum detection, BER of PSK/QAM/orthogonal/non-coherent signalling, comparison vs Shannon). (textbook)
2. MIT 6.02 *Introduction to EECS II: Digital Communication Systems*, Fall 2012, lecture notes ch. 9 "Noise" (§9.3–9.5: bipolar BER in erfc form, unequal priors, SNR). https://ocw.mit.edu/courses/6-02-introduction-to-eecs-ii-digital-communication-systems-fall-2012/ (lecture notes)
3. B. Sklar, *Digital Communications: Fundamentals and Applications*, 2nd ed., Prentice Hall, 2001 — ch. 4 (detection, BER) and ch. 9 (bandwidth-efficiency plane, modulation/coding trade-offs). (textbook)
4. S. Haykin, *Communication Systems*, 4th ed., Wiley, 2001 — ch. 6 (passband digital transmission; non-coherent FSK, DPSK derivations). (textbook)
5. A. Goldsmith, *Wireless Communications*, Cambridge University Press, 2005 — ch. 6 (performance in fading: average BER expressions). (textbook)
6. E. Jacobsen, "Understanding and Relating Eb/No, SNR, and other Power Efficiency Metrics," dsprelated.com, 2011. https://www.dsprelated.com/showarticle/168.php — Es = Ps/Rs, Ec, Eb definitions; Es/N0 = SNR only when noise BW = Rs; factor-of-two pitfalls. (practitioner article)
7. C. E. Shannon, "A Mathematical Theory of Communication," *Bell System Technical Journal* 27, 1948 — §19 (2TW dimensions), §25 Theorem 17 (C = W log(1+P/N); ideal signals resemble white noise), §26 (peak-power constraint). Reprint: https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf (peer-reviewed, primary)
8. CCSDS 130.1-G-3, *TM Synchronization and Channel Coding — Summary of Concept and Rationale* (Green Book), June 2020 — §3.3 (BI-AWGN capacity asymptotes 0.2/−0.5/−0.8/−1.1/−1.6 dB; block-size-dependent sphere-packing limits), §6 (Viterbi node-sync limitation ≈ 4 dB). https://ccsds.org/Pubs/130x1g3e1.pdf (standard, informative)
9. Y. Polyanskiy, H. V. Poor, S. Verdú, "Channel Coding Rate in the Finite Blocklength Regime," *IEEE Trans. Inf. Theory* 56(5):2307–2359, 2010 — normal approximation and AWGN dispersion. (peer-reviewed)
10. Semtech, *SX1276/77/78/79 datasheet*, Rev. 7 (2020) — LoRa spreading-factor table with demodulator SNR (−7.5 dB SF7 … −20 dB SF12) and bit-rate formula. https://www.semtech.com/products/wireless-rf/lora-connect/sx1276 (datasheet)
11. comp.dsp thread "BER performance of BPSK and QPSK" (dsprelated.com/showthread/comp.dsp/104982) and DSPLog "Bit error rate for BPSK modulation" — recurrent confusion about QPSK vs BPSK per bit vs per symbol. (forum — anecdotal; used only for the misconception)
12. J. W. Craig, "A new, simple and exact result for calculating the probability of error for two-dimensional signal constellations," *Proc. IEEE MILCOM* 1991, pp. 571–575. (peer-reviewed)
13. M. K. Simon and M.-S. Alouini, *Digital Communication over Fading Channels*, 2nd ed., Wiley, 2005 — ch. 8 (average BER over Rayleigh/Rician). (textbook)
14. MathWorks, Communications Blockset "AWGN Channel" documentation — complex input: variance of each quadrature component is half the specified noise variance. (documentation)
15. T. S. Rappaport, *Wireless Communications: Principles and Practice*, 2nd ed., Prentice Hall, 2002 — §6.x (modulation performance in AWGN and fading). (textbook)
16. T. M. Cover, J. A. Thomas, *Elements of Information Theory*, 2nd ed., Wiley 2006 — ch. 2 (entropy, mutual information), ch. 5 (Huffman), ch. 7 (channel capacity, BSC), ch. 9 (Gaussian channel, sphere packing). (textbook)
17. G. Caire, G. Taricco, E. Biglieri, "Bit-interleaved coded modulation," *IEEE Trans. Inf. Theory* 44(3):927–946, 1998. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
18. D. Tse, P. Viswanath, *Fundamentals of Wireless Communication*, Cambridge 2005, ch. 5 (§5.4 outage and ergodic capacity of fading channels, transmitter CSI and water-filling over time, channel inversion). Free draft: https://web.stanford.edu/~dntse/papers/book121004.pdf (textbook)
19. A. Goldsmith, *Wireless Communications* (ref. 5), ch. 4 (capacity of fading channels: ergodic, outage, water-filling, truncated inversion) and ch. 9 (adaptive modulation and coding). (textbook)
20. A. J. Goldsmith, P. P. Varaiya, "Capacity of fading channels with channel side information," *IEEE Trans. Inf. Theory* 43(6):1986–1992, 1997. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
21. A. J. Goldsmith, S.-G. Chua, "Variable-rate variable-power MQAM for fading channels," *IEEE Trans. Commun.* 45(10):1218–1230, 1997 — BER bound 0.2 exp(−1.5γ/(M−1)). (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
22. The Things Industries, "Adaptive Data Rate" documentation (default margin 15 dB, NStep = margin/2.5), https://www.thethingsindustries.com/docs/reference/adr/ ; ADR-TTN literature (margin_db 10 dB, 20 uplinks, NStep = margin/3), e.g. arXiv:2111.00401. (documentation / peer-reviewed; secondary for the Semtech algorithm)
23. J. G. Proakis, M. Salehi (ref. 1), ch. 6 (information theory: entropy, mutual information, capacity of BSC/AWGN and of constrained signal sets) and ch. 13 (fading channels: outage). (textbook)
24. Verification: `tools/verify/s8_outage_capacity.py`, `tools/verify/s8_info_coding.py` (W5-S8). (numerical check)
