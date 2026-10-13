---
title: Digital modulation — OOK, FSK/MSK/GMSK, PSK, QAM, APSK
domain: 10-comms-modulation
slug: digital-modulation-psk-qam-fsk
tags: [OOK, ASK, FSK, CPFSK, MSK, GFSK, GMSK, BPSK, QPSK, OQPSK, pi/4-DQPSK, 8PSK, QAM, APSK, constellation, signal-space, spectral-efficiency, PAPR, EVM, modulation-index]
prerequisites:
  - ../00-math-foundations/complex-numbers-and-phasors.md
  - ../00-math-foundations/fourier-series-and-transform.md
  - ../14-sdr-dsp/iq-complex-baseband.md
  - matched-filter-detection.md
related:
  - ber-ebn0-and-shannon.md
  - pulse-shaping-isi.md
  - analog-modulation-am-fm-pm-ssb.md
  - synchronization-carrier-timing.md
  - modulation-choice-guide.md
  - ofdm.md
  - ../06-rf-circuits/power-amplifiers.md
  - ../06-rf-circuits/transmitter-architectures.md
  - ../15-lora-ism-radios/other-ism-radios-fsk-2g4.md
  - ../17-test-measurement/spectrum-analyzers.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Digital modulation — OOK, FSK/MSK/GMSK, PSK, QAM, APSK

## Questions this page answers
- What is the difference between bit rate, symbol rate and baud?
- What does a constellation diagram actually represent?
- How wide is an FSK signal — is it just twice the deviation?
- What is the modulation index of FSK, and why are h = 0.5 (MSK) and h = 1 special?
- What are MSK, GFSK and GMSK, and what does "BT = 0.3" mean?
- Why do satellites use OQPSK or π/4-QPSK instead of plain QPSK?
- How many bits per second per hertz can BPSK, QPSK, 16-QAM or 64-QAM deliver?
- What is PAPR, and why does 16-QAM force me to run my PA backed off?
- What is EVM, and how does it relate to SNR?
- Which modulations can be demodulated without recovering the carrier phase?
- Why do cheap 433 MHz remotes use OOK and most ISM data radios use GFSK?

## TL;DR
- **Bits vs symbols:** each symbol carries $k=\log_2M$ coded bits, so $R_s = R_b/(k\,r)$ (baud = symbols/s). Occupied bandwidth scales with $R_s$, noise immunity with $E_b/N_0$.
- **Linear modulations (ASK/PSK/QAM)** with root-raised-cosine pulses occupy $B=(1+\beta)R_s$ (two-sided RF width) → spectral efficiency $\eta = k\,r/(1+\beta)$ b/s/Hz: BPSK 0.74, QPSK 1.48, 16-QAM 2.96, 64-QAM 4.44 at β = 0.35, uncoded.
- **FSK family:** modulation index $h=2f_{dev}/R_b$ (tone spacing × bit time). $h=0.5$ is MSK (minimum spacing for *coherent* orthogonality); $h=1$ is the minimum for *non-coherent* orthogonality. 99 % occupied bandwidth: **MSK 1.18 Rb, GMSK BT = 0.5 → 1.03 Rb, BT = 0.3 → 0.91 Rb, BT = 0.25 → 0.86 Rb** (simulated; GMSK values match ITU-R SM.328). Carson-style estimate: $B\approx R_b+2f_{dev}$.
- **Constant-envelope (FSK/MSK/GMSK)** signals have 0 dB PAPR → PA can run saturated (class C/E, max efficiency). Filtered QPSK has ≈ 3.8 dB PAPR (at 1e-4 CCDF, β = 0.35), 16-QAM ≈ 5.6 dB: that much PA back-off, i.e. a 2 W PA delivers ≈ 0.55 W average with 16-QAM.
- **OQPSK (max 90° jump) and π/4-QPSK (135°)** avoid the 180° zero-crossings of QPSK, so filtered envelopes dip less — kinder to nonlinear PAs.
- **Power efficiency ranking at 1e-5 (Eb/N0, uncoded):** BPSK = QPSK 9.6 dB < DBPSK 10.3 < coherent FSK 12.6 < 8-PSK 13.0 < NC-FSK 13.4 ≈ 16-QAM 13.4 < 64-QAM 17.8 dB (from [BER page](ber-ebn0-and-shannon.md)).
- **EVM** (rms error-vector / rms reference) of a noise-limited signal is $1/\sqrt{\mathrm{SNR}}$: 10 % ↔ 20 dB, 3.2 % ↔ 30 dB (verified).
- **No-carrier-recovery options:** OOK (envelope), NC-FSK/GFSK (discriminator or tone energy), DBPSK/π/4-DQPSK (differential), CSS/LoRa. Each costs 0.7–4 dB vs coherent PSK, but tolerates frequency offset and is cheap — which is why ISM radios are mostly GFSK.

## Intuition (no math)
Every modern radio signal can be written as a slowly varying complex number — the **complex envelope** $I+jQ$ — riding on a carrier. $I$ is how much cosine, $Q$ how much sine. A *constellation diagram* is just a scatter plot of that complex number at the moments the receiver makes its decisions. Modulations differ only in which points they allow and how they move between them:

- **OOK/ASK:** the point sits on the real axis at different distances from the origin (amplitude).
- **PSK:** the points sit on a circle (fixed amplitude, different phases).
- **QAM:** the points form a grid (amplitude *and* phase).
- **APSK:** points on a few concentric rings — a compromise between the grid and the circle.
- **FSK:** the point spins around the circle at different *speeds* (frequency = rate of phase change). Its amplitude never changes.

More points per symbol means more bits per symbol and less bandwidth per bit, but the points are packed closer together for the same average power, so noise confuses them sooner. That is the fundamental bandwidth-vs-power trade (see the Shannon plane on the [BER page](ber-ebn0-and-shannon.md)).

The movement between points matters for hardware. If the envelope passes through zero (QPSK jumping 180°), the transmitted amplitude has to dip to zero and come back — a nonlinear power amplifier distorts these dips and spreads energy into neighbouring channels. Constant-envelope schemes (FSK, MSK, GMSK) never dip, so they can use cheap saturated amplifiers. That is why a rocket beacon or an ISM module almost always uses (G)FSK, and why Wi-Fi's 64-QAM needs a linear, backed-off PA.

## The math

### Level 1 — representation, rates and bandwidth
A passband signal with carrier $f_c$ and complex envelope $\tilde s(t)=I(t)+jQ(t)$:
$$s(t)=\mathrm{Re}\{\tilde s(t)e^{j2\pi f_ct}\}=I(t)\cos 2\pi f_ct - Q(t)\sin 2\pi f_ct.$$
For **linear** modulation, $\tilde s(t)=\sum_n a_n\,p(t-nT_s)$ where $a_n$ are complex constellation points and $p(t)$ a pulse shape (rectangular, RRC, half-sine…).

| Quantity | Formula | Units |
|---|---|---|
| Symbol rate | $R_s = R_b/(k\,r)$, $k=\log_2M$ | baud (symbol/s) |
| RRC occupied bandwidth (RF, two-sided) | $B=(1+\beta)R_s$ | Hz |
| Spectral efficiency (RRC) | $\eta=R_b/B=k\,r/(1+\beta)$ | b/s/Hz |
| FSK modulation index | $h=\Delta f_{tones}\,T_b = 2f_{dev}/R_b$ (binary) | – |
| FSK bandwidth (Carson-style) | $B\approx R_b+2f_{dev}=R_b(1+h)$ | Hz |
| MSK/GMSK 99 % bandwidth | $K\cdot R_b$, K = 1.18 (MSK), 1.03 (BT 0.5), 0.91 (BT 0.3) | Hz |
| EVM (rms) | $\sqrt{\overline{|r-a|^2}/\overline{|a|^2}}$ | % or dB ($20\log_{10}$) |
| PAPR | $\max|s|^2/\overline{|s|^2}$ (or a CCDF percentile) | dB |

The regulator's version of these (necessary bandwidth) is in NTIA Annex J: for digital FM $B_n=R/\log_2S+2KD$ with $K\approx0.89$–1.2, and for PSK/QAM $B_n=2KR/\log_2S$ with $K$ set by the RRC roll-off [7] — cross-reference [spectrum allocation](../19-regulations-safety/spectrum-allocation-ism-bands.md).

### Level 1½ — I and Q as two knobs, algebra only
- **Two amplitudes make one carrier.** $I\cos\omega t - Q\sin\omega t$ is a single sinusoid of amplitude $\sqrt{I^2+Q^2}$ and phase $\mathrm{atan2}(Q,I)$. A constellation point is one (I, Q) setting held for one symbol.
- **Bits to symbols.** Each symbol carries k = log₂M coded bits. With FEC of rate r, only r of them are information, so $R_s = R_b/(k\,r)$.
- **Symbols to bandwidth.** With root-raised-cosine pulses of roll-off β, $B = (1+\beta)R_s$. QPSK carries 2 bits per symbol, so at the same bit rate it needs half the bandwidth of BPSK.
- **FSK moves the frequency instead.** Two tones $2f_{dev}$ apart give the index $h = 2f_{dev}/R_b$ and a Carson-style width $R_b(1+h)$.

*Worked number (verified, `tools/verify/s18b_level15_numbers.py`).*
- **One point:** I = +1, Q = −1 gives $\cos\omega t + \sin\omega t = \sqrt2\cos(\omega t - 45°)$: amplitude **1.414**, phase **−45°**, the point 1 − j.
- **One link:** 9600 b/s QPSK with rate-½ FEC and β = 0.35: R_s = 9600/(2 × 0.5) = 9600 baud, B = **12.96 kHz**, η = 0.74 b/s/Hz. Uncoded GFSK at 9600 b/s with h = 0.5 needs about **14.4 kHz**.

### Level 2 — the schemes one by one

**Signal space and distance.** Pick orthonormal basis functions (for I/Q modulation: $\phi_1=\sqrt{2/T}\,p(t)\cos$, $\phi_2=-\sqrt{2/T}\,p(t)\sin$). Each symbol is a point; the squared Euclidean distance $d^2$ between points, measured in units of $E_b$, sets the error rate through $Q(\sqrt{d^2/2N_0})$ ([matched filter](matched-filter-detection.md)). The figure of merit is $d_{min}^2/E_b$:

| Modulation | $M$ | $d_{min}^2/E_b$ | Relative to BPSK |
|---|---|---|---|
| BPSK, QPSK | 2, 4 | 4 | 0 dB |
| OOK, coherent orthogonal FSK | 2 | 2 | −3 dB |
| 8-PSK | 8 | $4\cdot3\sin^2(\pi/8)=1.76$ | −3.6 dB |
| 16-QAM | 16 | $6k/(M-1)=1.6$ | −4.0 dB |
| 64-QAM | 64 | $36/63=0.571$ | −8.5 dB |

(For square M-QAM $d_{min}^2=6E_s/(M-1)=6kE_b/(M-1)$.) The BER-table differences are these numbers adjusted for the number of nearest neighbours.

**OOK / ASK.** $a_n\in\{0,A\}$ (OOK) or several amplitudes (M-ASK). Average energy per bit $E_b = A^2T/4$ for OOK (half the bits are "off"). Coherent detection: $P_b=Q(\sqrt{E_b/N_0})$; envelope (non-coherent) detection at high SNR is ≈ $\tfrac12e^{-E_b/2N_0}$ with an SNR-dependent optimal threshold. Spectrum: a carrier line (the mean of $a_n$) plus the data sidebands. Pros: trivially simple transmitters and super-regenerative/envelope receivers; cons: 3 dB worse than BPSK at best, peak power is twice average, the threshold must track the signal level (AGC), and interference looks like "on".

**BPSK.** $a_n\in\{\pm1\}$ → $s(t)=\pm A\cos(2\pi f_ct)$ during a bit. Best binary power efficiency; spectrum of rectangular BPSK is $\propto\mathrm{sinc}^2(fT_b)$ with main lobe (null-to-null) $2R_b$ containing 90.3 % of the power and a 99 % bandwidth of **20.6 Rb** (the $f^{-2}$ sidelobes decay slowly) — hence the need for pulse shaping ([pulse shaping](pulse-shaping-isi.md)). Needs a coherent carrier reference (Costas loop, [synchronisation](synchronization-carrier-timing.md)), with a 180° ambiguity resolved by differential encoding or a known sync word.

**QPSK.** $a_n\in\{e^{j(\pi/4+m\pi/2)}\}$; Gray-coded, it is two independent BPSKs on I and Q. Same BER per bit as BPSK and half the bandwidth for the same $R_b$. Rectangular QPSK: 99 % bandwidth 10.3 Rb. When I and Q flip together the phase jumps 180° and, after filtering, the envelope passes through zero.

**OQPSK (offset / staggered QPSK).** Delay Q by $T_s/2$ so I and Q never change at the same instant: the maximum phase step is 90° and the filtered envelope never reaches zero. Same BER and spectrum as QPSK, much less spectral regrowth after a nonlinear PA. Used in IEEE 802.15.4 (as O-QPSK with half-sine pulses — which is MSK in disguise) and in many satellite links [1 §3.3], [2].

**π/4-QPSK / π/4-DQPSK.** Alternate between two QPSK constellations rotated by 45°; each symbol's information is a phase *change* of ±45° or ±135°. Maximum jump 135° (no zero crossing), guaranteed phase transition every symbol (helps timing recovery), and differential detection possible. Used in TETRA, North American TDMA and Bluetooth EDR (2 Mb/s) [3].

**M-PSK.** $M$ points on a circle; $d_{min}=2\sqrt{E_s}\sin(\pi/M)$. 8-PSK is the last PSK worth using — beyond it, QAM gives more distance for the same average energy.

**Square M-QAM.** Two $\sqrt M$-level PAMs. Levels $\pm1,\pm3,\ldots$ scaled; $E_s=\frac{2(M-1)}{3}\left(\frac d2\right)^2$. Every extra bit per symbol costs about 3 dB (asymptotically 6 dB per bit per dimension). Constellation PAPR (peak point over average): **16-QAM 2.55 dB, 64-QAM 3.68 dB** (verified) — and filtering adds more.

**APSK.** Concentric rings, e.g. 16-APSK = 4 + 12 points, 32-APSK = 4 + 12 + 16 (DVB-S2 [8]). Fewer amplitude levels than QAM of the same order, so it tolerates a satellite's travelling-wave-tube amplifier better, and the ring radii can be pre-distorted.

**FSK and CPFSK.** Binary FSK sends $f_c\pm f_{dev}$. Tone spacing $\Delta f=2f_{dev}$, modulation index $h=\Delta f\,T_b$.
- *Orthogonality.* Two tones over one bit are orthogonal (zero correlation) for coherent detection when $\Delta f=k/(2T_b)$, $k=1,2,\dots$; for non-coherent detection (unknown phases) the complex correlation $|\int e^{j2\pi\Delta f t}dt|/T_b$ must vanish, which needs $\Delta f=k/T_b$. At $\Delta f=1/(2T_b)$ the non-coherent correlation magnitude is $2/\pi=0.64$ — far from orthogonal (verified). So MSK ($h=0.5$) demodulated non-coherently is *not* the "NC-FSK" of the BER table; it performs worse than $h=1$ with a tone-energy detector [1 §3.3], [4].
- *Continuous phase.* If the frequency switches without a phase jump (CPFSK — what a VCO or a phase-accumulator synthesiser naturally does), the phase is $\phi(t)=\pi h\sum_n a_n q(t-nT)$ with $q$ the integral of the frequency pulse. Phase continuity makes the spectrum fall off as $f^{-4}$ instead of $f^{-2}$.
- *Discriminator detection.* Most ISM chips demodulate (G)FSK with a frequency discriminator (or its digital equivalent, $\arg(r_nr_{n-1}^*)$), then slice. It is simple and tolerant of frequency offset up to a fraction of $f_{dev}$ (the offset appears as a DC shift the slicer must remove — why FSK packets need DC-balanced, whitened data; see [packet framing](packet-framing-protocols.md)). Its sensitivity is typically within ≈ 1–3 dB of the ideal NC-FSK curve depending on $h$ and filtering [4], [5].

**MSK.** CPFSK with $h=0.5$ ($f_{dev}=R_b/4$). Equivalent to OQPSK with half-sine pulse shaping on each rail, so it can be detected coherently with BPSK-like performance ($P_b=Q(\sqrt{2E_b/N_0})$ with a two-bit observation) [4]. Constant envelope, main lobe $1.5R_b$ wide, 99 % bandwidth **1.18 Rb**, sidelobes decaying as $f^{-4}$. PSD: $S(f)\propto\left[\frac{\cos 2\pi fT_b}{1-16f^2T_b^2}\right]^2$.

**GMSK / GFSK.** Pass the NRZ data through a Gaussian low-pass filter (3-dB bandwidth $B$) before the frequency modulator. $BT$ = filter bandwidth × bit time. Smaller BT → narrower spectrum but more ISI (each bit's frequency pulse spreads over ≈ $1/BT$ bits):
- GSM: GMSK, $BT=0.3$, $h=0.5$ [9]. 99 % bandwidth 0.91 Rb; ISI costs < 1 dB with a good receiver.
- Bluetooth LE 1M: GFSK $BT=0.5$, $h=0.45$–0.55; Bluetooth BR: $BT=0.5$, $h=0.28$–0.35 [10].
- ISM transceivers (TI CC1101/CC1120, Silicon Labs Si446x, Semtech SX126x FSK mode) let you choose BT (typically 0.3–1.0) and deviation; GFSK with $h\approx0.5$–1 and BT = 0.5 is a sane default for a custom telemetry link (see [other ISM radios](../15-lora-ism-radios/other-ism-radios-fsk-2g4.md)).
"GFSK" is the general term (any $h$); "GMSK" means $h=0.5$ exactly.

**M-FSK.** $M$ tones, $\log_2M$ bits per symbol. *Improves* power efficiency with $M$ (non-coherent 128-FSK needs 6.3 dB at 1e-5) while bandwidth grows as $M/\log_2M$ — the opposite trade to QAM. LoRa's CSS is an M-ary orthogonal scheme in this family ([spread spectrum](spread-spectrum-dsss-fhss-css.md)).

### Level 3 — spectra, PAPR and error-vector metrics
**PSD of linear modulation.** For i.i.d. zero-mean symbols of variance $\sigma_a^2$ and pulse $p(t)\leftrightarrow P(f)$, the complex-envelope PSD is $S(f)=\frac{\sigma_a^2}{T_s}|P(f)|^2$ (plus spectral lines if the mean is nonzero, e.g. OOK) [1 §3.4]. Hence the spectrum is set *entirely* by the pulse: rectangular → $\mathrm{sinc}^2$, RRC → band-limited to $(1\pm\beta)/2T_s$. Constellation choice changes the power, not the shape. This is why a spectrum analyser cannot tell QPSK from 16-QAM with the same pulse and symbol rate.

**PSD of CPM (FSK/MSK/GMSK)** is not given by a simple formula except special cases; it depends on $h$ and the frequency pulse. For integer $h$ (e.g. $h=1$ FSK) the spectrum contains discrete tones at $\pm f_{dev}$ carrying significant power — wasted for data but handy for spotting the signal on an SDR waterfall [11].

**Sidelobe decay rule.** A signal whose $n$-th derivative is the first discontinuous one has a spectrum decaying as $f^{-2(n+1)}$ in power: rectangular PSK (discontinuous) $f^{-2}$; MSK (continuous phase, discontinuous frequency) $f^{-4}$; GMSK (smooth) faster than any power.

**PAPR and PA back-off.** The PA must handle the peak; its efficiency and linearity are specified at the average. For RRC-filtered signals the simulated 1e-4 CCDF points are: QPSK 5.1 dB (β = 0.2), 3.8 dB (β = 0.35), 3.2 dB (β = 0.5); 16-QAM 5.6 dB (β = 0.35). Lower roll-off → longer ringing → higher PAPR. Clipping the peaks causes spectral regrowth (ACLR) and EVM; digital predistortion or back-off fixes it ([power amplifiers](../06-rf-circuits/power-amplifiers.md)). OFDM is much worse (≈ 10 dB, see [OFDM](ofdm.md)). Shannon §26 already noted that a *peak*-power constraint lowers capacity relative to an average-power constraint [12].

**EVM and MER.** $\mathrm{EVM_{rms}}=\sqrt{\sum|r_n-a_n|^2/\sum|a_n|^2}$, where $a_n$ are ideal points (normalisation — to average or peak power — must be stated). With only AWGN, $\mathrm{EVM_{rms}}=1/\sqrt{\mathrm{SNR}}$ (SNR per symbol after the matched filter, i.e. $E_s/N_0$); in dB, $\mathrm{EVM_{dB}}=-\mathrm{SNR_{dB}}$. MER (modulation error ratio) is the same quantity expressed as an SNR. Standards cap transmitter EVM so that it degrades the link only slightly, e.g. IEEE 802.11a/g requires ≈ −16 dB for 16-QAM rate ½ and −25 dB for 64-QAM rate ¾ [13]. The full ladder is BPSK ½ −5, QPSK ½ −10, QPSK ¾ −13, 16-QAM ½ −16, 16-QAM ¾ −19, 64-QAM ⅔ −22, 64-QAM ¾ −25 dB, plus BPSK ¾ −8 dB in 802.11a and 64-QAM ⅚ −28 dB in 802.11n (values checked 2026-10-13 against the same table as reproduced in IEEE 802.11 TGn document 11-06/0448 and later HE/EHT draft text; the clause-17 table number itself not checked).

## Design equations & rules of thumb

| Equation / rule | When valid | Typical values |
|---|---|---|
| $R_s=R_b/(k\,r)$ | any | QPSK r = ½: $R_s=R_b$ |
| $B_{RRC}=(1+\beta)R_s$ (RF width) | linear mod, RRC | β = 0.2–0.5 |
| $\eta=kr/(1+\beta)$ | linear mod | QPSK 1.48 b/s/Hz at β = 0.35 |
| $h=2f_{dev}/R_b$; coherent orthogonal $h=0.5k$; non-coherent $h=k$ | binary FSK | MSK h = 0.5 |
| $B\approx R_b+2f_{dev}$ | (G)FSK, $h\lesssim2$ | 10 kb/s, ±5 kHz → 20 kHz |
| $B_{99}=1.18R_b$ (MSK), $1.03$ (GMSK 0.5), $0.91$ (0.3), $0.86$ (0.25) | CPM, h = 0.5 | verified |
| $B_{99}$ rect BPSK $=20.6R_b$; main lobe $2R_b$ holds 90.3 % | unfiltered PSK | never transmit unfiltered PSK |
| $d_{min}^2=6kE_b/(M-1)$ | square M-QAM | 16-QAM 1.6 Eb |
| constellation PAPR 16-QAM 2.55 dB, 64-QAM 3.68 dB | before filtering | + 2–3 dB after RRC |
| PAPR@1e-4, RRC β=0.35: QPSK 3.8 dB, 16-QAM 5.6 dB | simulated | PA back-off ≈ PAPR |
| $\mathrm{EVM}=1/\sqrt{\mathrm{SNR}}$ | AWGN-limited | 10 % ↔ 20 dB |

## Worked examples

### Example 1 — Bandwidth of a 10 kb/s GFSK rocket downlink
Option A: GFSK, $h=0.5$ ($f_{dev}=2.5$ kHz), BT = 0.5. 99 % bandwidth ≈ $1.03\times10$ kHz = **10.3 kHz**. Carson-style estimate $R_b+2f_{dev}=15$ kHz (conservative).
Option B: $h=1$ ($f_{dev}=5$ kHz) for proper non-coherent orthogonality: $B\approx R_b(1+h)=20$ kHz (plus tones at ±5 kHz). It buys better NC-FSK sensitivity and more frequency-offset tolerance; costs 2× bandwidth.
Doppler at 433 MHz for 700 m/s (≈ Mach 2) is $\pm700/0.692=\pm1.0$ kHz — 40 % of the option-A deviation. A discriminator receiver sees this as a DC offset that its slicer must track; with ±10 ppm crystals (±4.3 kHz each end) the offset can exceed the deviation entirely unless AFC or a TCXO is used ([synchronisation](synchronization-carrier-timing.md)).

### Example 2 — QPSK for the same 10 kb/s
Uncoded QPSK, RRC β = 0.35: $R_s=5$ kbaud, $B=6.75$ kHz; η = 1.48 b/s/Hz. With rate-½ FEC: $R_s=10$ kbaud, $B=13.5$ kHz, but ≈ 5.4 dB less power needed ([channel coding](channel-coding-fec.md)).

### Example 3 — PA back-off penalty with a 2 W PA
The E22-400T33D-class 2 W (33 dBm) module PA is designed for constant-envelope LoRa. Suppose a custom design reuses a 2 W saturated PA:
- GFSK/GMSK: run at 33 dBm average.
- QPSK, RRC β = 0.35: back off by ≈ 3.8 dB → 29.2 dBm (0.83 W) average.
- 16-QAM: ≈ 5.6 dB → 27.4 dBm (0.55 W).
For a power-limited rocket link, the 16-QAM option pays twice: 3.8 dB more Eb/N0 (13.4 vs 9.6 dB) *and* 5.6 dB less average transmit power — ≈ 9 dB worse than GMSK-coherent-class performance, for bandwidth you probably don't need.

### Example 4 — Translating a measured EVM into link margin
An SDR measures 7 % rms EVM on your QPSK ground-station signal at a strong level. That is an SNR ceiling of $-20\log_{10}0.07=23.1$ dB from transmitter/receiver impairments alone (phase noise, IQ imbalance, PA distortion). Near sensitivity (Es/N0 ≈ 12.6 dB for QPSK at 1e-5) the thermal noise dominates and the 23 dB impairment floor costs only $10\log_{10}(1+10^{(12.6-23.1)/10})=0.4$ dB. For 64-QAM (needs ≈ 25 dB Es/N0) the same 7 % EVM would make 1e-5 unreachable.

### Example 5 — Bits vs baud on an EBYTE-style datasheet
A radio lists "air data rate 9.6 kbps" in 4-FSK mode. Then $k=2$ and the symbol rate is 4.8 kbaud; bandwidth follows 4.8 kbaud and the deviation, not 9.6 k. If FEC rate ½ is on and the 9.6 kbps is the *user* rate, the channel carries 19.2 kb/s = 9.6 kbaud. Always establish which rate a datasheet quotes (NTIA explicitly warns to use the transmitted RF rate including overhead [7]).

## Practical notes
- **Generating FSK:** a fractional-N PLL modulated directly (most ISM chips) gives true CPFSK; filtering the data first (Gaussian) is done digitally. Generating QPSK/QAM needs an IQ modulator (or a DAC-based SDR) and a linear PA ([transmitter architectures](../06-rf-circuits/transmitter-architectures.md)).
- **Receiving:** coherent PSK/QAM requires carrier and timing recovery and an AGC; (G)FSK with discriminator needs only timing and a DC/offset tracker — much simpler to get working at low SNR and with Doppler.
- **IQ imbalance and phase noise** show up as constellation distortion (ellipse, rotation smear) and set an EVM floor; they matter for 16-QAM and up, rarely for BPSK/FSK.
- **Spectral masks** (e.g. ISM duty-cycle bands) are specified at a resolution bandwidth; unfiltered FSK with small $h$ still has wide skirts — use Gaussian shaping.
- **Choosing $h$:** $h=0.5$ for spectral efficiency with a coherent or sequence detector; $h\approx0.7$–1 for simple non-coherent/discriminator receivers and offset tolerance; larger $h$ for very high offset (cheap crystals, fast Doppler) at the cost of bandwidth.
- **LoRa modules (E22/E220)** use CSS, not these modulations, but the SX126x silicon inside also offers GFSK — a useful fallback mode for higher data rates at short range.

## Common mistakes & misconceptions
- **"Baud = bits per second."** Only for binary modulation without coding. 4-FSK at 9600 baud carries 19 200 b/s.
- **"FSK bandwidth = 2 × deviation."** It is ≈ $2f_{dev}+R_b$ (Carson-style), because the data transitions add sidebands; for small $h$ the data term dominates (MSK: 99 % in 1.18 Rb although $2f_{dev}=0.5R_b$).
- **Deviation vs peak-to-peak.** Some datasheets and papers quote total (peak-to-peak) deviation; $h=2f_{dev}/R_b$ uses the peak deviation $f_{dev}$ from the carrier. NTIA explicitly warns about this [7]. A factor-of-two error here makes $h$ wrong.
- **"MSK is FSK with h = 0.5, so non-coherent FSK receivers work fine with it."** Tones $1/(2T)$ apart are not orthogonal without phase knowledge; non-coherent MSK loses several dB versus $h=1$ NC-FSK.
- **"Higher-order QAM is always better."** It is better only when bandwidth is the constraint; on a power-limited link it costs Eb/N0 *and* PA back-off.
- **"The constellation determines the spectrum."** The pulse shape and symbol rate do; the constellation only scales it.
- **"OQPSK has better BER than QPSK."** Identical in AWGN; its advantage is envelope behaviour through nonlinear amplifiers.
- **Quoting EVM without normalisation** (to rms or peak) — 64-QAM's peak and average normalisations differ by 3.7 dB.

## How to simulate / verify
- **`tools/verify/comms_modulation_spectra.py`** (≈ 2 s): tone orthogonality (coherent vs non-coherent), 99 % bandwidths (MSK analytic 1.182 Rb vs simulated 1.19; GMSK BT 0.5/0.3/0.25 = 1.03/0.91/0.86 Rb; rectangular BPSK 20.6 Rb), constellation and RRC-filtered PAPR, EVM = 1/√SNR, maximum phase jumps of QPSK/π/4-DQPSK/OQPSK. All PASS.
- **BER curves:** `tools/verify/comms_ber_awgn.py` covers the detection side.
- **GNU Radio:** *Constellation Modulator* (PSK/QAM with RRC), *GFSK Mod/Demod*, *GMSK Mod*, *Quadrature Demod* (discriminator); view with *QT GUI Constellation Sink* and *Frequency Sink*. PySDR's digital modulation chapter walks through the same constellations in Python [6].
- **Bench:** an SDR (Pluto, HackRF) plus a spectrum analyser: verify occupied bandwidth (99 % OBW function) and, for PSK/QAM, EVM with a vector signal analysis tool (e.g. inspectrum, GNU Radio constellation + EVM probe).

## Open questions / gaps
- NTIA/ITU-R SM.328 list $K=1.28$ for unfiltered MSK 99 % bandwidth while the analytic PSD (and simulation) give 1.18 Rb; the source of the ITU figure (different definition?) is unresolved.
- The IEEE 802.11 EVM values were checked on 2026-10-13 against the allowed-relative-constellation-error table as reproduced in 802.11 working-group documents (TGn 11-06/0448; HE/EHT draft text). The standard itself was not read, so the clause-17 table number (Table 17-18) and subclause (§17.3.9.7.4) are still unconfirmed.
- Discriminator-detector loss vs ideal NC-FSK as a function of $h$ and BT is given only as a range (1–3 dB). Two points are now simulated in [14 software demodulation](../14-sdr-dsp/software-demodulation.md) (`tools/verify/dsp_demod.py`): 2-FSK $h$ = 1 → +0.07 dB, 2-GFSK $h$ = 0.5, BT = 0.5 → +1.41 dB at BER 10⁻³ (Carson-width pre-detection filter, integrate-and-dump); the full $h$/BT map is still open.

## Sources
1. J. G. Proakis and M. Salehi, *Digital Communications*, 5th ed., McGraw-Hill, 2008 — ch. 3 (digital modulation schemes, CPFSK/MSK, PSD of linearly modulated signals §3.4), ch. 4 (detection). (textbook)
2. B. Sklar, *Digital Communications*, 2nd ed., Prentice Hall, 2001 — ch. 4 and ch. 9 (OQPSK, MSK, bandwidth definitions, bandwidth-efficiency plane). (textbook)
3. T. S. Rappaport, *Wireless Communications*, 2nd ed., Prentice Hall, 2002 — ch. 6 (π/4-QPSK, GMSK, spectral efficiency, constant-envelope modulation). (textbook)
4. S. Pasupathy, "Minimum shift keying: a spectrally efficient modulation," *IEEE Communications Magazine* 17(4):14–22, 1979 — MSK as OQPSK with sinusoidal weighting, PSD, 99 % bandwidth. (peer-reviewed)
5. K. Murota and K. Hirade, "GMSK modulation for digital mobile radio telephony," *IEEE Trans. Communications* COM-29(7):1044–1050, 1981 — Gaussian pre-modulation filter, BT trade-off. (peer-reviewed)
6. M. Lichtman, *PySDR*, "Digital Modulation" and "IQ Sampling" chapters, https://pysdr.org (online textbook)
7. NTIA, *Manual of Regulations and Procedures for Federal Radio Frequency Management*, Annex J "Guidance for Determination of Necessary Bandwidth," Jan. 2021 ed. — digital FM $B_n=R/\log_2S+2KD$; ITU-R SM.328 K-factors for MSK/GMSK; PSK/QAM $B_n=2KR/\log_2S$; warnings on RF rate and deviation definitions. https://www.ntia.gov/files/ntia/publications/j_21_1.pdf (standard/regulatory)
8. ETSI EN 302 307-1, *DVB-S2*, V1.4.1, 2014 — 16APSK (4+12) and 32APSK (4+12+16) constellations. (standard)
9. 3GPP TS 45.004, *GSM/EDGE Modulation* — GMSK with BT = 0.3 at 270.833 kbit/s. (standard)
10. Bluetooth SIG, *Bluetooth Core Specification* v5.4, Vol. 2 Part A (BR: GFSK BT 0.5, h 0.28–0.35) and Vol. 6 Part A (LE: BT 0.5, h 0.45–0.55). (standard)
11. J. B. Anderson, T. Aulin, C.-E. Sundberg, *Digital Phase Modulation*, Plenum, 1986 — CPM spectra, integer-h spectral lines. (textbook)
12. C. E. Shannon, "A Mathematical Theory of Communication," BSTJ 1948, §26 (peak-power limitation). (peer-reviewed)
13. IEEE Std 802.11-2020, §17 (OFDM PHY: transmitter constellation error limits). (standard)
