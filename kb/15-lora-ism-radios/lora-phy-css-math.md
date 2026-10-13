---
title: LoRa physical layer — chirp spread spectrum from first principles
domain: 15-lora-ism-radios
slug: lora-phy-css-math
tags: [lora, css, chirp, spreading-factor, bandwidth, coding-rate, time-on-air, ldro, preamble, sync-word, dechirp, fft, processing-gain]
prerequisites:
  - ../00-math-foundations/complex-numbers-and-phasors.md
  - ../00-math-foundations/fourier-series-and-transform.md
  - ../10-comms-modulation/digital-modulation-psk-qam-fsk.md
  - ../10-comms-modulation/matched-filter-detection.md
related:
  - lora-sensitivity-and-link-budget.md
  - lora-impairments-doppler-drift-timing.md
  - semtech-chip-family.md
  - rocket-telemetry-radio-design.md
  - ../10-comms-modulation/spread-spectrum-dsss-fhss-css.md
  - ../10-comms-modulation/ber-ebn0-and-shannon.md
  - ../10-comms-modulation/channel-coding-fec.md
  - ../14-sdr-dsp/iq-complex-baseband.md
  - ../14-sdr-dsp/fft-spectral-analysis-windows.md
  - ../14-sdr-dsp/software-demodulation.md
level: mixed
confidence: high
last_updated: 2026-10-14
---

# LoRa physical layer — chirp spread spectrum from first principles

## Questions this page answers
- What exactly is a LoRa chirp, and how does a chirp carry bits?
- What do spreading factor (SF), bandwidth (BW) and coding rate (CR) actually change?
- Why is the LoRa symbol time $2^{SF}/BW$, and what is a "chip"?
- How do I calculate the LoRa bit rate for a given SF, BW and CR?
- How does a LoRa receiver demodulate — why "de-chirp and FFT"?
- Where does LoRa's "processing gain" come from and how big is it?
- How long is my packet on the air (time-on-air), and why do SX127x and SX126x formulas look different?
- What are the preamble, sync word, header, CRC and low-data-rate optimisation (LDRO)?
- Why does each SF step only buy ~2.5 dB of sensitivity instead of 3 dB?
- What do the 4.25 symbols and the "+8" in the time-on-air formula mean?
- Why can't my SX1262 talk to my SX1276 at SF6?

## TL;DR
- A LoRa symbol is a linear frequency sweep (chirp) across the whole bandwidth BW; the data is the **starting frequency**, i.e. a **cyclic shift** of a base up-chirp. There are $N = 2^{SF}$ possible shifts, so each symbol carries SF bits (SF − 2 with LDRO).
- Chip rate = BW (one chip per second per hertz); symbol time $T_s = 2^{SF}/BW$ (SF7/125 kHz: 1.024 ms; SF12/125 kHz: 32.768 ms).
- Useful bit rate $R_b = (SF-2\,DE)\cdot\frac{BW}{2^{SF}}\cdot\frac{4}{4+CR}$: SF7/125/CR4/5 = 5469 b/s; SF12/125 (LDRO) = 244 b/s; SF5/500 = 62.5 kb/s (the E22's top "air rate").
- Demodulation = multiply by a conjugate base chirp ("de-chirp") → the symbol becomes a pure tone at bin $s$ → an $N$-point FFT picks the largest bin. At critical sampling the $N$ chirps are exactly orthogonal, so LoRa is **non-coherent orthogonal $M$-ary signalling with $M = 2^{SF}$**, and the FFT is the optimum correlator bank [4].
- Processing gain $=10\log_{10}2^{SF} = 3.01\,SF$ dB (21 dB at SF7, 36 dB at SF12). That is why LoRa demodulates at negative SNR: −7.5 dB (SF7) … −20 dB (SF12) per Semtech [1][2]. Our simulation of an ideal receiver reproduces these within ±1.5 dB (see *How to verify*).
- Time-on-air (SX127x form, identical to SX126x for SF7–12): $T = \left(N_{pre}+4.25+8+\max\!\left(\left\lceil\frac{8PL-4SF+28+16CRC-20IH}{4(SF-2DE)}\right\rceil(CR+4),0\right)\right)\frac{2^{SF}}{BW}$. Verified over 5820 cases in `tools/verify/lora_toa.py`; e.g. 10 B at SF7/125 = 41.216 ms, 13 B at SF12/125 = 1155.07 ms.
- LDRO must be on when $T_s \gtrsim 16$ ms (SF11 and SF12 at 125 kHz, SF12 at 250 kHz) and must match on both ends.

## Intuition (no math)
Imagine a whistle that slides smoothly from a low note to a high note in a fixed time, then jumps back and repeats. That slide is a **chirp**. A LoRa transmitter always sends slides of the same length and the same range (the bandwidth), but it can **start the slide part-way up**; when it reaches the top it wraps to the bottom and continues, so every symbol still covers the whole range in the same time. Where it starts is the message. With SF7 there are 128 possible starting points (7 bits); with SF12 there are 4096 (12 bits), but each slide takes 32 times longer.

The receiver plays its own copy of a plain slide backwards against the incoming one ("de-chirping"). Whatever the start point, the result is a **steady tone** whose pitch equals the start point. A spectrum analyser (the FFT) then shows one tall spike; its position is the symbol. Noise, by contrast, is spread evenly over all $N$ FFT bins, while the signal's whole energy lands in one bin — that concentration is the processing gain, and it grows with the slide length. Longer slides = more energy collected per decision = weaker signals decodable, at the cost of time.

Because every symbol sweeps the full band, a narrowband interferer or a frequency-selective fade only damages part of each symbol, and a constant frequency error just shifts every spike by the same amount (which the preamble measures and removes). That is the physical reason LoRa tolerates cheap crystals and multipath better than narrowband FSK — and also why a *changing* frequency error (Doppler rate on a rocket) is its weak spot (see [impairments](lora-impairments-doppler-drift-timing.md)).

## The math

### Level 1 — definitions and rates
| Symbol | Meaning | Unit | LoRa values |
|---|---|---|---|
| $BW$ | occupied (double-sided) bandwidth = chirp sweep width | Hz | 7.8, 10.4, 15.6, 20.8, 31.25, 41.7, 62.5, 125, 250, 500 kHz (SX126x/SX127x) [1][2] |
| $SF$ | spreading factor = bits per symbol | – | 6–12 (SX127x), 5–12 (SX126x) |
| $N=2^{SF}$ | chips per symbol = alphabet size $M$ | – | 32 … 4096 |
| $T_c = 1/BW$ | chip duration | s | 8 µs at 125 kHz |
| $T_s = N/BW$ | symbol duration | s | 1.024 ms (SF7/125) … 32.768 ms (SF12/125) |
| $CR\in\{1,2,3,4\}$ | coding-rate index → code rate $4/(4+CR)$ | – | 4/5, 4/6, 4/7, 4/8 |
| $DE\in\{0,1\}$ | low-data-rate optimisation flag | – | 1 when $T_s\gtrsim16$ ms |

Symbol rate $R_s = BW/2^{SF}$ [2 §6.1.1]. Raw bit rate $SF\cdot R_s$. Useful (information) bit rate:
$$R_b = (SF-2DE)\,\frac{BW}{2^{SF}}\,\frac{4}{4+CR}\quad[\text{bit/s}]$$

Computed by `tools/verify/lora_toa.py` (CR4/5, LDRO auto):

| SF | $T_s$ @125 kHz | $R_b$ @125 | $R_b$ @250 | $R_b$ @500 |
|---|---|---|---|---|
| 5 | 0.256 ms | 15 625 | 31 250 | 62 500 |
| 6 | 0.512 ms | 9 375 | 18 750 | 37 500 |
| 7 | 1.024 ms | 5 469 | 10 938 | 21 875 |
| 8 | 2.048 ms | 3 125 | 6 250 | 12 500 |
| 9 | 4.096 ms | 1 758 | 3 516 | 7 031 |
| 10 | 8.192 ms | 977 | 1 953 | 3 906 |
| 11 | 16.384 ms | 439 (LDRO) | 1 074 | 2 148 |
| 12 | 32.768 ms | 244 (LDRO) | 488 (LDRO) | 1 172 |

These reproduce the "indicative physical bit rates" in LoRaWAN RP002 (DR0 SF12/125 = 250, DR1 SF11 = 440, DR2 SF10 = 980, DR3 SF9 = 1760, DR5 SF7 = 5470, DR6 SF7/250 = 11 000 b/s) [7], confirming that RP002's SF11/SF12 values include LDRO.

### Level 2 — the waveform, de-chirping and orthogonality
**Continuous time.** The base up-chirp over one symbol $0\le t<T_s$ has instantaneous frequency (complex baseband, centred on the carrier)
$$f_0(t) = -\frac{BW}{2} + \frac{BW}{T_s}\,t ,$$
a slope of $\mu = BW/T_s = BW^2/2^{SF}$ Hz/s. Symbol $s\in\{0,\dots,N-1\}$ starts $s\,BW/N$ higher and wraps from $+BW/2$ back to $-BW/2$ at time $t_w = (N-s)T_c$. The baseband signal is $x_s(t)=\exp\!\big(j2\pi\int_0^t f_s(\tau)\,d\tau\big)$ — constant envelope, which is why cheap saturated (class-C/E) PAs work.

**Discrete time at one sample per chip** ($f_s = BW$, $t = nT_c$). Integrating and sampling gives
$$x_s[n] = \exp\!\Big(j2\pi\big[\tfrac{n^2}{2N} + (\tfrac{s}{N}-\tfrac12)\,n\big]\Big),\qquad n = 0,\dots,N-1 .$$
The wrap needs no special treatment: after the wrap the true frequency is lower by exactly $BW$, which adds a phase $-2\pi n$ per sample — an integer number of cycles, invisible at $f_s = BW$ (the frequency simply aliases). This is the discrete model used by Vangelista [4] and the EPFL receiver [5] (they write it with a $e^{j2\pi(\cdot)}$ phase exactly as here; assumption: ideal band-limited pulse shaping is ignored, which causes small aliasing distortions in the continuous-time signal [5]).

**De-chirp.** Multiply by the conjugate base chirp $x_0^*[n]$:
$$x_s[n]\,x_0^*[n] = \exp\!\big(j2\pi\,s\,n/N\big),$$
a pure complex tone at normalised frequency $s/N$. Its $N$-point DFT is
$$Y[k]=\sum_{n=0}^{N-1}e^{j2\pi (s-k)n/N} = N\,\delta[k-s] .$$
**Orthogonality.** The same sum shows $\langle x_s,x_r\rangle = \sum_n x_s[n]x_r^*[n] = N\delta_{sr}$: the $N$ chirps are an orthogonal set (verified numerically: max off-diagonal Gram term $7\times10^{-13}$ at SF7, `lora_css_sim.py`). Correlating the received vector against all $N$ candidates *is* the DFT of the de-chirped vector, computed in $O(N\log N)$. For an unknown carrier phase, the optimum (maximum-likelihood) non-coherent decision is $\hat s = \arg\max_k |Y[k]|$ [4].

**Noise and processing gain.** Let the received samples be $r[n] = A\,x_s[n]e^{j\phi} + w[n]$ with complex AWGN of variance $\sigma^2$ per sample. Because $f_s = BW$, $\sigma^2$ is the noise power in the channel bandwidth, so the (Semtech-convention) channel SNR is $\text{SNR} = A^2/\sigma^2$. After de-chirp + DFT the signal bin has amplitude $NA$ (power $N^2A^2$) while each bin's noise has variance $N\sigma^2$, so the decision-variable SNR is
$$\text{SNR}_{bin} = N\cdot\text{SNR},\qquad G_{proc} = 10\log_{10}N = 3.01\,SF\ \text{dB}.$$
Equivalently the symbol energy to noise density is $E_s/N_0 = N\cdot\text{SNR}$ and
$$\frac{E_b}{N_0} = \frac{E_s/N_0}{(SF-2DE)\cdot\frac{4}{4+CR}} = \text{SNR}+10\log_{10}\frac{2^{SF}(4+CR)}{4(SF-2DE)}\ \text{dB}.$$

**Symbol error rate.** For non-coherent orthogonal $M$-ary signalling (a standard result, see [10-comms/ber-ebn0-and-shannon](../10-comms-modulation/ber-ebn0-and-shannon.md)), normalising noise bins to unit variance, the correct bin magnitude is Rician and the $M-1$ others Rayleigh:
$$P_c = \int_0^\infty 2r\,e^{-(r^2+\gamma)}I_0(2r\sqrt{\gamma})\,\big(1-e^{-r^2}\big)^{M-1}dr,\qquad \gamma = N\cdot\text{SNR},\quad P_s = 1-P_c .$$
(The closed alternating sum $\sum_{k=1}^{M-1}(-1)^{k+1}\binom{M-1}{k}\frac{1}{k+1}e^{-k\gamma/(k+1)}$ is exact but numerically useless for $M\ge 64$.) Closed-form BER approximations for LoRa are given by Elshabrawy & Robert [9]. Numerically (`lora_css_sim.py`), SER $=10^{-3}$ needs SNR = −7.8 (SF7), −10.6, −13.3, −16.1, −19.0, −21.8 dB (SF12): **≈2.8 dB per SF step**, not 3 dB, because doubling $N$ doubles $\gamma$ (+3 dB) but also doubles the number of noise bins that might win (−0.2 dB).

### Level 3 — the full PHY: coding chain, packet structure, time-on-air, and limits
**Transmit chain** (reverse-engineered by Knight & Seeber [10] and made standard-compatible by Tapparel et al. [5]):
1. *Whitening* — XOR with a pseudo-random sequence (removes long runs; not encryption).
2. *Hamming coding* — each 4-bit nibble becomes $4+CR$ bits: (4,5) parity (detects 1 error), (4,6) punctured (detects), (4,7) Hamming (corrects 1), (4,8) extended Hamming (corrects 1, detects 2) [5].
3. *Diagonal interleaving* — a block of $SF$ codewords (each $4+CR$ bits) is written as a $SF\times(4+CR)$ matrix and read diagonally into $4+CR$ symbols of $SF$ bits, so one corrupted symbol damages at most one bit per codeword.
4. *Gray mapping* (a reverse Gray code) — adjacent FFT bins differ in one bit, so the most common error (±1 bin from residual frequency/timing offset) becomes a single-bit error that CR4/7 and CR4/8 can correct [5].
5. *Chirp modulation* of the resulting symbol values.

**Packet structure** [1][2][5][7]:
- **Preamble**: $N_{pre}$ base up-chirps (programmable; LoRaWAN uses 8; SX126x default 12, recommended ≥12 at SF5/6 [2]). Detection restarts periodically, so the receiver's programmed preamble length should equal (or, if unknown, exceed) the transmitter's [2].
- **Sync word / network identifier**: 2 up-chirps shifted by values derived from the sync-word nibbles. SX127x register `RegSyncWord` (0x39) default 0x12 (private); LoRaWAN public = 0x34 [1][7]. SX126x stores it as two bytes at 0x0740/0x0741: 0x1424 private, 0x3444 public [2 (Rev 2.2)]. A sync-word mismatch makes packets invisible — cheap "network separation", not security.
- **SFD**: 2.25 down-chirps. Together with the 2 sync symbols this is the "+4.25" in the ToA formula.
- **Header** (explicit mode only): payload length (8 bits), coding rate (3 bits), payload-CRC-present flag (1 bit) and a header checksum — 20 bits in total — always sent at CR 4/8 and reduced rate in the first interleaver block [1][2].
- **Payload**: 1–255 bytes [1][5]; **CRC**: optional 16 bits over the payload (LoRaWAN: uplink only) [7].
- **Implicit header mode** drops the header; length, CR and CRC flag must then be configured identically on both ends. SX127x SF6 *requires* implicit mode [1].

**Deriving the time-on-air formula from the block structure.** The first interleaver block is always 8 symbols at CR4/8 carrying $SF-2$ bits each, i.e. $8(SF-2)$ coded bits = $4(SF-2)$ information bits, of which 20 are the explicit header. So the payload bits that spill past the first block number
$$8PL + 16\,CRC - \big(4(SF-2) - 20\,(1-IH)\big) = 8PL - 4SF + 28 + 16CRC - 20IH .$$
Every further block has $4+CR$ symbols carrying $4(SF-2DE)$ information bits. Counting blocks:
$$n_{payload} = 8 + \max\!\left(\left\lceil\frac{8PL-4SF+28+16CRC-20IH}{4(SF-2DE)}\right\rceil (CR+4),\,0\right),$$
$$T_{packet} = \big(N_{pre} + 4.25 + n_{payload}\big)\,\frac{2^{SF}}{BW}.$$
This is exactly Semtech's SX127x formula [1 §4.1.1.7] (= AN1200.13), where $PL$ = payload bytes, $IH=1$ for implicit header, $DE=1$ with LDRO, $CR$ = 1…4. The script checks the block derivation, the SX127x form, the SX126x form and an integer replica of Semtech's SX126x driver [3] against each other for 5820 parameter combinations.

The **SX126x datasheet** (equations embedded as images; checked against the rendered Rev 1.2 page 41) writes it as $N_{sym} = N_{pre} + 4.25 + 8 + \lceil \max(8PL + N_{CRC} - 4SF + 8 + N_{hdr},0)/(4(SF-2DE))\rceil(CR+4)$ with $N_{hdr}=20$ (explicit) — identical for SF7–12. For **SF5 and SF6 on SX126x** the "+8" disappears and the constant becomes 6.25 (two extra sync symbols) [2][3]; this, and a different SF6 implementation, is why SX1261/2 SF6 is **not** compatible with SX1276 SF6 [2 §6.1.1].

Reference values (8-symbol preamble, explicit header, CRC on, CR4/5, auto-LDRO):

| Payload | SF/BW | Symbols | Time-on-air |
|---|---|---|---|
| 10 B | SF7/125 | 40.25 | 41.216 ms |
| 13 B (empty LoRaWAN frame) | SF7/125 | 45.25 | 46.336 ms |
| 13 B | SF12/125 | 35.25 | 1155.072 ms |
| 51 B | SF12/125 | 75.25 | 2465.792 ms |
| 64 B (Semtech test packet) | SF7/125 | 115.25 | 118.016 ms |

**Low-data-rate optimisation (LDRO).** With $DE=1$ the transmitter uses only $SF-2$ bits per symbol (the two LSBs of every symbol are fixed), i.e. only every fourth FFT bin is a legal symbol. This gives the receiver ±2 bins of slack against slow frequency/timing drift over long symbols [1][2][11]. Semtech: "mandated when the symbol duration exceeds 16 ms" (SX127x) [1]; "usually recommended when $T_s\ge16.38$ ms" (SX126x) [2] — the boundary case is SF11/125 kHz (16.384 ms), which LoRaWAN runs with LDRO on. Both ends must agree, otherwise every payload symbol decodes wrongly. Cost: 17 % longer ToA for a 32-byte SF9 packet in our script (the bits-per-symbol drop from 9 to 7).

**Where the idealisation breaks.**
- Real receivers must estimate carrier-frequency offset (CFO) and symbol-timing offset (STO) from the preamble. For an up-chirp a CFO of $\delta$ bins moves the de-chirped peak by $+\delta$ while a timing error of $\tau$ chips moves it by $-\tau$, so up-chirps alone cannot separate them; for the down-chirps the timing term changes sign, so peak(up) $=\delta-\tau$, peak(down) $=\delta+\tau$ and the pair resolves both — the reason for the 2.25-down-chirp SFD [5]. Residual fractional offsets cost SNR: half a bin costs 3.9 dB of peak height (`lora_css_sim.py`) and, uncorrected, makes SF9 SER at −12 dB jump from 0 to 0.5.
- The Semtech "typical demodulator SNR" table (2.5 dB per SF) is a rounded rule. An ideal receiver needs −6.9 (SF7) … −21.4 dB (SF12) for 1 % PER on the 64-byte test packet; Semtech quotes −7.5 … −20 dB. The chip is ~1.4 dB worse than ideal at SF12 (implementation loss) and apparently ~0.6–1.3 dB *better* than our ideal uncoded-CR4/5 model at SF5–7 — see [sensitivity page](lora-sensitivity-and-link-budget.md) for the discussion.
- Frequency-selective channels, Doppler *rate* and imperfect SF orthogonality are covered in [impairments](lora-impairments-doppler-drift-timing.md).

## Design equations & rules of thumb
| Equation / rule | When valid | Typical values |
|---|---|---|
| $T_s = 2^{SF}/BW$ | always | SF7/125: 1.024 ms; SF9/125: 4.096 ms; SF12/125: 32.768 ms |
| $R_b = (SF-2DE)\,BW\,2^{-SF}\,4/(4+CR)$ | nominal payload rate | 5.47 kb/s SF7/125; 244 b/s SF12/125 |
| $G_{proc} = 3.01\,SF$ dB | ideal de-chirp + FFT | 21 dB (SF7) … 36 dB (SF12) |
| SNR$_{req}\approx -7.5 - 2.5(SF-7)$ dB | Semtech rule, 1 % PER 64 B CR4/5 | −7.5 (SF7) … −20 (SF12) |
| Each +1 SF: ×2 ToA, ≈ +2.5–2.8 dB | fixed BW | range ×1.33 in free space |
| Each ×2 BW: ×½ ToA, −3 dB sensitivity | fixed SF | range ×0.71 |
| ToA formula (above) | all SX127x; SX126x SF7–12 | use `lora_toa.py` |
| LDRO on if $T_s\gtrsim 16$ ms | SX127x/SX126x | SF11–12 @125, SF12 @250 |
| Preamble ≥ 8 (SF7–12), ≥ 12 (SF5/6 SX126x) | reliable detection | LoRaWAN 8 |
| $E_b/N_0 \approx 6$ dB at 1 % PER | from Semtech table | 5.7–6.7 dB ideal (sim) |

## Worked examples
**1. Bit rate and packet rate for the primary FC's E22 at a plausible SF9/125 setting.** A 32-byte telemetry frame, 8-symbol preamble, explicit header, CRC, CR4/5, no LDRO ($T_s$ = 4.096 ms < 16 ms).
- Payload symbols: $\lceil(8\cdot32 - 36 + 28 + 16)/(4\cdot9)\rceil = \lceil 264/36\rceil = 8$ blocks × 5 = 40, plus 8 → 48.
- Total symbols: $8 + 4.25 + 48 = 60.25$; ToA $= 60.25 \times 4.096$ ms $= 246.8$ ms.
- So even transmitting back-to-back the link carries at most 4.1 frames/s. At SF7/125 the same frame takes 71.9 ms (13.9 frames/s); at SF7/500, 18.0 ms (55.6 frames/s).
This is why the Space Bar flight-software lessons insist on budgeting downlink bandwidth against the *air rate* with deterministic decimation (see [rocket telemetry design](rocket-telemetry-radio-design.md)).

**2. Processing gain and required SNR at SF12/125 kHz.** $N = 4096$ → $G_{proc} = 36.1$ dB. The ideal receiver reaches SER $10^{-3}$ at SNR = −21.8 dB, i.e. decision-bin SNR $= -21.8 + 36.1 = 14.3$ dB. $E_b/N_0 = -21.8 + 10\log_{10}(4096\cdot5/(4\cdot10)) = -21.8 + 27.1 = 5.3$ dB — comfortably above Shannon's −1.6 dB but only a few dB better than ordinary non-coherent FSK. LoRa's advantage is *not* a magic Eb/N0; it is that it can spend time (long symbols) to reach negative SNR with a simple, drift-tolerant receiver.

**3. What does the LDRO flag cost at SF12/125?** 32-byte frame: with LDRO (required) ToA = 1810 ms; the payload is 43 symbols. If one side forgot LDRO, the other would decode 12-bit symbols where only 10 were meant — CRC fails on every packet (the classic "I see RSSI but no packets at SF11/12" symptom).

**4. Time-on-air sanity check of a LoRaWAN uplink.** A LoRaWAN frame with 0 application bytes still has 13 bytes of MAC overhead (MHDR 1, DevAddr 4, FCtrl 1, FCnt 2, FPort 1, MIC 4). At SF12/125 that is 1155 ms per packet; with the EU 1 % duty cycle you may send one such frame every ~115 s ([band plans](ism-band-plans-duty-cycle.md)).

## Practical notes
- **Both ends must match**: carrier frequency (within ±25 % BW), BW, SF, sync word, IQ polarity, LDRO, header mode; in implicit mode also length/CR/CRC. The CR is carried in the explicit header, so it may differ between packets [2].
- **IQ inversion**: LoRaWAN downlinks are sent with inverted IQ so end-devices don't hear each other [7]; a receiver set to the wrong polarity sees nothing. SX126x has an erratum for long inverted-IQ packets (register 0x0736 bit 2 fix) — see [chip family](semtech-chip-family.md).
- **SF5/SF6**: only SX126x/LLCC68/LR11xx have SF5; SX127x SF6 needs implicit header and special detection registers [1]; SX126x SF6 is not air-compatible with SX127x SF6 [2].
- **Bandwidth availability**: on SX126x some narrow BWs may not be available below 400 MHz because the BW scales with frequency [2]; the LLCC68 limits SF by BW (SF≤9 at 125 kHz, ≤10 at 250, ≤11 at 500) [12].
- **Maximum payload** 255 bytes; UART modules add their own limits (E22: 240 B sub-packets; E220: 200 B) — see [modules](lora-modules-ebyte-rfm-heltec.md).
- **Occupied bandwidth**: the chirp's spectrum is close to a rectangle of width BW with sidelobes that fall as $M$ grows [13]; regulators' "20 dB bandwidth" is slightly wider than BW — check with a spectrum analyser before claiming FCC digital-modulation (≥500 kHz 6 dB BW) status ([band plans](ism-band-plans-duty-cycle.md)).

## Common mistakes & misconceptions
- **"SF is the number of chips per bit."** No: $2^{SF}$ is chips per *symbol*; SF is bits per symbol. The name is historic.
- **"125 kHz bandwidth means 125 kb/s."** No: chip rate is 125 kchip/s; the bit rate at SF7 is 5.5 kb/s and at SF12 0.24 kb/s.
- **"Higher SF is always better."** Each SF step doubles ToA for only ~2.5 dB; it quadruples collision exposure per packet-pair duration, halves update rate, and makes the link far more sensitive to Doppler *rate* and crystal drift (SF12/125 fails at a few g of radial acceleration without tracking — see [impairments](lora-impairments-doppler-drift-timing.md)). The LLCC68 in the E220 cannot run SF10–12 at 125 kHz at all.
- **"CR4/5 corrects errors."** CR4/5 and 4/6 only *detect*; correction needs 4/7 or 4/8 (and even then only one bit per codeword) [5].
- **"Implicit header is more robust."** It is only shorter (−20 bits); if the receiver's assumed length or CR is wrong, everything fails.
- **"Chirps with different SF are perfectly orthogonal."** Only quasi-orthogonal; strong other-SF signals still interfere (≈ −16 dB SIR threshold) — see [impairments](lora-impairments-doppler-drift-timing.md).
- **Using the SX127x ToA formula for SX126x SF5/6** (it under-counts by ~2 symbols), or forgetting the preamble's extra 4.25 symbols.
- **Thinking the sync word secures the link.** It is a 1-byte filter visible to any SDR; EBYTE's "key" is also not real cryptography ([modules](lora-modules-ebyte-rfm-heltec.md)).

## How to simulate / verify
- `python3 tools/verify/lora_toa.py` — ToA, bit-rate and packet-rate tables; cross-checks SX127x formula, SX126x formula, Semtech driver integer replica and the interleaver-block derivation (all agree; 5820 cases).
- `python3 tools/verify/lora_css_sim.py` (≈1 min; `QUICK=1` for seconds) — builds chirps at 1 sample/chip, checks orthogonality and the noise-free round trip, runs Monte-Carlo SER vs the exact non-coherent $M$-ary integral (agreement within MC error, e.g. SF12 at −21.5 dB: theory $4.74\times10^{-4}$, MC $4.67\times10^{-4}$), converts SER to 1 %-PER SNR and prints it beside Semtech's table, and quantifies CFO and drift effects.
- Minimal self-contained demonstration (the core of `lora_css_sim.py`, 1 sample/chip, ideal sync):

```python
import numpy as np
SF = 9; N = 2**SF; n = np.arange(N)
def chirp(s):                      # symbol s = cyclic shift of the base up-chirp
    return np.exp(2j*np.pi*(n*n/(2*N) + (s/N - 0.5)*n))
def demod(rx):                     # de-chirp with the conjugate base chirp, then FFT
    return int(np.argmax(np.abs(np.fft.fft(rx*np.conj(chirp(0))))))
rng = np.random.default_rng(1); snr_db = -14.0          # SNR in the full bandwidth
sig = 10**(-snr_db/20)/np.sqrt(2)                        # noise std per I/Q component
errs = 0
for s in rng.integers(0, N, 2000):
    rx = chirp(s) + sig*(rng.standard_normal(N) + 1j*rng.standard_normal(N))
    errs += demod(rx) != s
print(errs/2000)   # ≈ 4e-3 at SF9, −14 dB (theory 4.3e-3); −12 dB → theory 2e-5
```
- To see real LoRa: record an E22/E220 transmission with an RTL-SDR/HackRF/USRP and decode with **gr-lora_sdr** (EPFL) [5]; a waterfall at 1–2 MS/s shows the chirps directly. This is also how to determine the undocumented SF/BW behind an EBYTE "air data rate" ([modules](lora-modules-ebyte-rfm-heltec.md)).
- Semtech's LoRa Calculator (desktop tool) gives ToA and sensitivity per chip; our script matches its formula.

## Open questions / gaps
- Semtech never published the exact LoRa header bit layout or the whitening sequence; these come from reverse engineering [5][10]. Knight & Seeber [10] and Robyns et al. (multi-channel decoder, 2018) were not read in full in this pass — only via Tapparel et al. [5].
- Why Semtech's SNR table is *better* than an ideal uncoded model at SF5–7 is unresolved (possibly the table is a rounded rule rather than a measurement; the measured SX1262 SF7/125 sensitivity −124 dBm implies NF ≈ 5.9 dB with the ideal SNR, plausible).
- LR2021 "LoRa Plus" changes (higher rates, larger offset tolerance) are not yet described at PHY level here.
- Chiani & Elzanaty (IEEE IoT-J 2019, waveform & spectral analysis) and Ghanaatian et al. (ICASSP 2019, arXiv:1811.04146, receiver CFO/SFO modelling) are cited from abstracts only.

## Sources
1. Semtech, *SX1276/77/78/79 Datasheet*, Rev 7, May 2020 — §4.1.1 (SF table incl. SNR, CR overhead, LDRO "mandated > 16 ms", SF6 implicit), §4.1.1.7 time-on-air, RegSyncWord 0x39 = 0x12. https://cdn.sparkfun.com/assets/7/7/3/2/2/SX1276_Datasheet.pdf (datasheet)
2. Semtech, *SX1261/2 Datasheet*, Rev 1.2, June 2019 — §6.1.1 (SF5–12 SNR table, $R_s = BW/2^{SF}$, "one chip per second per Hz", SF6 incompatibility, BW table, LDRO ≥ 16.38 ms), §6.1.3 packet/preamble, §6.1.4 ToA; Rev 2.2 register table (sync word 0x0740/0741 = 0x3444 public / 0x1424 private). https://cdn.sparkfun.com/assets/6/b/5/1/4/SX1262_datasheet.pdf (datasheet)
3. Semtech/Lora-net, *sx126x_driver*, `src/sx126x.c` — `sx126x_get_lora_time_on_air_numerator` (quarter-symbol arithmetic, SF5/6 +2 symbols, LDRO denominator). https://github.com/Lora-net/sx126x_driver (vendor code)
4. L. Vangelista, "Frequency Shift Chirp Modulation: The LoRa Modulation," *IEEE Signal Processing Letters* 24(12):1818–1821, 2017 — first rigorous description; optimum receiver via FFT. (peer-reviewed; abstract consulted, derivation on this page is independent)
5. J. Tapparel, O. Afisiadis, P. Mayoraz, A. Balatsoukas-Stimming, A. Burg, "An Open-Source LoRa Physical Layer Prototype on GNU Radio," IEEE SPAWC 2020, arXiv:2002.08208 — TX chain (whitening, Hamming (4,5…8), diagonal interleaver, Gray), preamble/network-ID/2.25 down-chirps, CFO/STO estimation, 255-byte limit; code: https://github.com/tapparelj/gr-lora_sdr (peer-reviewed)
6. J. Robinson ("StuartsProjects"), "Frequency drift for LoRa devices, is it important?", 2020 — practical LDRO/drift context. https://stuartsprojects.github.io/2020/05/08/Frequency-drift-for-LoRa-devices-is-it-important.html (forum/blog — anecdotal)
7. LoRa Alliance, *RP002-1.0.3 LoRaWAN Regional Parameters*, 2021 — §4.1 LoRa PHY (preamble 8, sync 0x34, explicit header, CRC uplink only, CR4/5, IQ inverted downlink); AS923 DR table with indicative bit rates. https://lora-alliance.org/wp-content/uploads/2021/05/RP002-1.0.3-FINAL-1.pdf (standard)
8. A. avbentem, *airtime-calculator* README — 13-byte LoRaWAN MAC overhead. https://github.com/avbentem/airtime-calculator (community tool)
9. T. Elshabrawy, J. Robert, "Closed-Form Approximation of LoRa Modulation BER Performance," *IEEE Communications Letters* 22(9):1778–1781, 2018. (peer-reviewed; cited for existence of closed forms, not reproduced)
10. M. Knight, B. Seeber, "Decoding LoRa: Realizing a Modern LPWAN with SDR," Proc. GNU Radio Conference 2016. https://pubs.gnuradio.org/index.php/grcon/article/view/8 (conference; abstract consulted)
11. Doppler estimation and compensation techniques in LoRa direct-to-satellite communications, arXiv:2506.20858 (2025) — LDRO reduces the alphabet to $2^{SF-2}$, ×4 bin spacing. (preprint)
12. DreamLNK, *DL-LLCC68-S datasheet* (LCSC C2894790) — LLCC68 SF/BW limits and −129 dBm at SF9/125. (module datasheet)
13. A. Maleki, H. H. Nguyen, E. Bedeer, R. Barton, "A Tutorial on Chirp Spread Spectrum for LoRaWAN: Basics and Key Advances," arXiv:2310.10503, 2023 — spectral properties, interference literature. (review)
14. R. Ghanaatian, O. Afisiadis, M. Cotting, A. Burg, "LoRa Digital Receiver Analysis and Implementation," ICASSP 2019, arXiv:1811.04146. (peer-reviewed; abstract only)
