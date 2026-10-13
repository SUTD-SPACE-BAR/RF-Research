---
title: Weak-signal digital modes — FT8, FT4, WSPR, JT65, JT9, Q65, FST4, PSK31, RTTY, APRS, DMR/D-STAR — and what they teach about low-rate telemetry
domain: 10-comms-modulation
slug: weak-signal-digital-modes
tags: [FT8, FT4, WSPR, JT65, JT9, JT4, Q65, FST4, FST4W, WSJT-X, PSK31, Varicode, RTTY, APRS, AX.25, DMR, D-STAR, weak-signal, SNR-2500, Eb/N0, non-coherent-MFSK, LDPC, OSD, Costas-array, a-priori-decoding, LoRa-comparison, beacon, telemetry]
prerequisites:
  - ber-ebn0-and-shannon.md
  - digital-modulation-psk-qam-fsk.md
  - channel-coding-fec.md
related:
  - spread-spectrum-dsss-fhss-css.md
  - synchronization-carrier-timing.md
  - packet-framing-protocols.md
  - modulation-choice-guide.md
  - analog-modulation-am-fm-pm-ssb.md
  - multiple-access-and-duplexing.md
  - ../15-lora-ism-radios/lora-sensitivity-and-link-budget.md
  - ../15-lora-ism-radios/lora-phy-css-math.md
  - ../09-propagation-link-budget/ionospheric-hf-propagation.md
  - ../09-propagation-link-budget/hf-propagation-modes-and-prediction.md
  - ../14-sdr-dsp/software-demodulation.md
  - ../19-regulations-safety/amateur-radio-licensing.md
level: mixed
confidence: high
last_updated: 2026-10-14
---

# Weak-signal digital modes (FT8, WSPR, JT65, Q65 …) and what they teach about low-rate telemetry

## Questions this page answers
- How can FT8 decode a signal 21 dB below the noise? Does it beat Shannon?
- What does "SNR −21 dB in 2500 Hz" mean, and how do I turn it into Eb/N0 or a received power in dBm?
- What modulation and coding do FT8, FT4, WSPR, JT65, JT9, Q65 and FST4 use?
- How close are these modes to the theoretical limit, and why are they so much better than RTTY or PSK31?
- Is FT8 better or worse than LoRa SF12 at the same bit rate?
- Why does FT8 fail on auroral (high-Doppler-spread) paths while FT4 survives?
- What are a-priori (AP) decoding and ordered-statistics decoding, and are they fair?
- What do PSK31/Varicode, RTTY, APRS, DMR and D-STAR actually send over the air?
- Could I use an FT8- or WSPR-style waveform for a rocket recovery beacon?

## TL;DR
- **"SNR in 2500 Hz" is an amateur convention**: signal power over the noise in a 2.5 kHz reference bandwidth, whatever the signal's own width. Convert with **Eb/N0 = SNR₂₅₀₀ + 10 log₁₀(2500/R_b)**, i.e. C/N0 = SNR₂₅₀₀ + 34.0 dB-Hz.
- **FT8** (Franke, Somerville and Taylor [1]): a 77-bit message plus a 14-bit CRC, an **LDPC(174,91)** code, **8-GFSK** at 6.25 baud (6.25 Hz tone spacing, 50 Hz occupied), and 58 data symbols plus three 7×7 Costas sync arrays (79 symbols, 12.64 s, in a 15 s slot). Its decoding threshold on AWGN (50 % decode probability, no a-priori information) is **−20.8 dB**. With maximum a-priori information it is −22.7 dB.
- **Why −21 dB works:** 77 bits in 12.64 s is only **6.09 b/s**. In a 6.25 Hz symbol bandwidth, −21 dB in 2500 Hz is **Es/N0 = +5.0 dB per symbol**, and the energy per information bit is **Eb/N0 ≈ 5.3 dB**, sync energy included. That is an ordinary, healthy Eb/N0. It is **1.1 dB above the capacity of single-symbol non-coherent 8-FSK at FT8's rate** and 6.7 dB above Shannon's −1.4 dB at η = 0.12 b/s/Hz. The "−21 dB" is just the 26 dB ratio between 2500 Hz and 6 b/s. There is no magic and no Shannon violation.
- **All modern WSJT-X modes cluster at Eb/N0 ≈ 4.2–5.4 dB**, counting all transmitted energy (FT4 4.6, FT8 5.3, Q65-60A 5.2, FST4-60 4.3, FST4W-120 5.4). The older RS/convolutional modes need 6.3–9 dB (JT9A 6.3, WSPR 6.4, JT65A 7.1, JT4A 9.1). Uncoded PSK31 needs ≈ 9 dB and RTTY ≈ 14 dB.
- **Against LoRa:** the datasheet SF12 limit (−20 dB in 125 kHz) is Eb/N0 ≈ 6.3 dB per payload bit at the nominal 293 b/s (DE = 0; with the LDRO that SF12/125 requires the rate is 244 b/s and Eb/N0 7.1 dB). That is **−3 dB in 2500 Hz**, a number that sounds poor only because the rate is 48× higher. For the same short message (≈ 80 bits), an idealised LoRa SF12 receiver needs **≈ 3 dB more Eb/N0 than FT8**. LoRa's preamble and header overhead and its weak Hamming code cost that 3 dB; the modulation is not to blame. Both are non-coherent orthogonal M-FSK at heart. LoRa's own 4096-ary signal set could work at ≈ 0 dB Eb/N0 with a strong code.
- **Lesson for telemetry:** at very low SNR a constant-envelope non-coherent M-FSK signal works well when it has (a) a strong soft-decision code (LDPC/QRA with BP + OSD), (b) source coding so that few bits are sent, (c) sync that costs ≲ 25 % of the energy, and (d) long symbols. The price is rate (bits per second) and stability: tone spacing 6.25 Hz is 0.014 ppm at 433 MHz.

## Intuition (no math)
A weak-signal mode is a radio that **trades speed for sensitivity as far as it will go**. FT8 sends only about 13 characters every 15 seconds. Each tone lasts 0.16 s, and the receiver listens for it with a filter only 6 Hz wide. A 6 Hz filter lets in 400 times less noise than a 2500 Hz SSB filter, so a signal that is "21 dB below the noise in 2500 Hz" is actually about 5 dB *above* the noise in the filter that matters.

That reframing explains most of the "below the noise" mystery. The rest comes from three engineering choices:
1. **Many tones, chosen non-coherently.** With 8 possible tones per symbol, each decision carries 3 bits. The receiver only has to find which filter has the most energy, so it needs no carrier phase. HF paths scramble phase, so that is a necessity.
2. **A strong code with soft decisions.** The receiver tells the decoder how confident it is about every bit. The LDPC decoder (and, if that fails, an exhaustive-ish ordered-statistics search) finds the codeword.
3. **Squeezing the message.** A call sign, a grid square and a report are compressed into exactly 77 bits. Fewer bits mean more energy per bit.

What you give up is speed and tolerance of frequency smear. If the ionosphere spreads each tone over more than the 6.25 Hz spacing (auroral paths), the tones blur together and FT8 fails, even at high SNR.

LoRa is surprisingly close in spirit. After dechirping, a LoRa symbol is one of 2^SF orthogonal "tones", detected non-coherently by an FFT. LoRa is faster and wider, and it carries a lot of preamble and only a tiny Hamming code, so it sits a few dB behind FT8 per bit.

## The math

### Level 1 — the conversions and the mode table
**Symbols.** SNR₂₅₀₀ = received signal power / noise power in 2500 Hz (dB). $R_b$ = information bit rate (user bits over the whole transmission time, b/s). $T_s$ = channel-symbol duration (s). $N_0 = kT_{sys}$ (W/Hz). With $P$ the received power:
$$\frac{C}{N_0}=\mathrm{SNR}_{2500}+10\log_{10}2500=\mathrm{SNR}_{2500}+34.0\ \text{dB-Hz},\qquad
\frac{E_b}{N_0}=\frac{C}{N_0}-10\log_{10}R_b,\qquad \frac{E_s}{N_0}=\frac{C}{N_0}+10\log_{10}T_s .$$
Here $E_b$ counts **all** transmitted energy, sync included, so it is the fair figure for a link budget. The sensitivity in dBm is $P_{min}=-174+\mathrm{NF}+C/N_0$ (canonical $kT_0$ = −174 dBm/Hz).

**Parameters and thresholds** (WSJT-X User Guide Table 7 [2] and, for FT8/FT4, the QEX paper [1]; thresholds are SNR₂₅₀₀ at **50 % decode probability**, AWGN, no a-priori information). The derived columns are from `tools/verify/s8_weak_signal_ebn0.py`.

| Mode | FEC (n,k) | Modulation | Baud | BW (Hz) | Sync energy | Tx time (s) | Info bits | SNR₂₅₀₀ (dB) | $R_b$ (b/s) | Es/N0 (dB) | **Eb/N0 (dB)** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FT8 | LDPC (174,91) | 8-GFSK, BT 2 | 6.25 | 50 | 0.27 | 12.64 | 77 | −20.8 | 6.09 | 5.2 | **5.3** |
| FT4 | LDPC (174,91) | 4-GFSK, BT 1 | 20.83 | 83.3 | 0.15 | 5.04 | 77 | −17.5 | 15.3 | 3.3 | **4.6** |
| JT4A | K=32 r=½ conv (206,72) | 4-FSK | 4.375 | 17.5 | 0.50 | 47.1 | 72 | −23 | 1.53 | 4.6 | 9.1 |
| JT9A | K=32 r=½ conv (206,72) | 9-FSK | 1.736 | 15.6 | 0.19 | 49.0 | 72 | −26 | 1.47 | 5.6 | 6.3 |
| JT65A | RS (63,12) | 65-FSK | 2.692 | 177.6 | 0.50 | 46.8 | 72 | −25 | 1.54 | 4.7 | 7.1 |
| Q65-15A | QRA (63,13) | 65-FSK | 6.667 | 433 | 0.26 | 12.8 | 77 | −22 | 6.02 | 3.7 | 4.2 |
| Q65-60A | QRA (63,13) | 65-FSK | 1.667 | 108 | 0.26 | 51.0 | 77 | −27 | 1.51 | 4.8 | 5.2 |
| Q65-300A | QRA (63,13) | 65-FSK | 0.289 | 19 | 0.26 | 293.8 | 77 | −33 | 0.26 | 6.4 | 6.8 |
| FST4-60 | LDPC (240,101) | 4-GFSK | 3.09 | 12.4 | 0.25 | 51.8 | 77 | −28 | 1.49 | 1.1 | 4.3 |
| WSPR | K=32 r=½ conv (162,50) | 4-FSK | 1.465 | 5.9 | 0.50 | 110.6 | 50 | −31 | 0.45 | 1.3 | 6.4 |
| FST4W-120 | LDPC (240,74) | 4-GFSK | 1.46 | 5.9 | 0.25 | 109.3 | 50 | −32 | 0.46 | 0.3 | 5.4 |

The guide rounds the thresholds to whole dB, so the Eb/N0 column is good to about ±0.5 dB. For comparison, PA3FWM's table [3] (no FEC) gives RTTY at −5 dB with 32 b/s (**Eb/N0 ≈ 14 dB**) and PSK31 at −10 dB with 31 b/s (**≈ 9 dB**). Those figures have no stated error criterion.

### Level 1½ — the same ideas with algebra only
- **Bandwidth bookkeeping.** Noise power is proportional to bandwidth. Going from a 2500 Hz reference to a 6.25 Hz tone filter removes $10\log(2500/6.25)=26.0$ dB of noise. So −21 dB in 2500 Hz is +5.0 dB in each tone filter.
- **Bits per symbol.** One of 8 tones carries $\log_2 8=3$ coded bits. FT8 sends 174 coded bits in 58 tones and 21 sync tones. Its 77 user bits therefore get 77/79 of a symbol's energy each, which is why Eb/N0 (5.3 dB) is close to Es/N0 (5.2 dB).
- **Slower is more sensitive, dB for dB.** Halving the bit rate at the same Eb/N0 halves the required power: −3 dB on SNR₂₅₀₀. That is why Q65-60A (1.5 b/s) is 5 dB "better" than Q65-15A (6 b/s) and WSPR (0.45 b/s) is 10 dB "better" than FT8, with almost the same Eb/N0.
- **A fair comparison is Eb/N0, not SNR₂₅₀₀.** On that scale every mode in the table is within 5 dB of every other, and the modern LDPC/QRA modes lie within about 1.2 dB of each other.

### Level 2 — why FT8 works at −21 dB, and how close to the limit it is
**1. The signal set.** FT8 is continuous-phase 8-FSK, with tone spacing equal to the keying rate (modulation index h = 1, orthogonal tones over a symbol) and Gaussian smoothing (BT = 2) of the frequency steps to keep sidelobes low [1]. The envelope is constant except for 20 ms raised-cosine ramps at the ends, so a saturated class-C or class-E PA can transmit it without intermodulation. The receiver correlates each symbol interval against the 8 tones and keeps the **magnitudes** $|C_i|$. That is non-coherent orthogonal detection, the same detector as LoRa's dechirp-and-FFT ([spread spectrum](spread-spectrum-dsss-fhss-css.md)) and as the non-coherent M-FSK row of the [BER page](ber-ebn0-and-shannon.md#level-2--derivations).

**2. Soft metrics and block detection.** For each coded bit $x_j$ the demapper forms $L_j=K\,(\max_{i:x_j=1}|C_i|-\max_{i:x_j=0}|C_i|)$ (QEX eq. in §6 [1]). WSJT-X also correlates against all $8^N$ waveforms of N = 2 or 3 consecutive symbols. On AWGN this **non-coherent block detection** exploits the phase continuity of CPFSK across symbols: +0.7 dB for FT8 and +1.6 dB for FT4. It needs the channel to keep phase over N symbols, so the gain vanishes on fast-fading paths.

**3. The decoder.** Belief propagation (BP) on the LDPC Tanner graph runs first ([channel coding](channel-coding-fec.md#level-3--concatenation-iterative-codes-and-the-short-block-regime)). If BP fails, **ordered-statistics decoding (OSD)** takes the 91 most reliable independent positions, re-encodes, and tests low-weight flips of them. OSD is close to maximum-likelihood decoding for a short code, and it is affordable because k = 91. Every candidate must also pass the 14-bit CRC, which keeps false decodes rare. On AWGN the thresholds are −19.6 dB (single-symbol, BP), −20.3 dB (block detection, BP) and −20.8 dB (block detection, BP + OSD) [1 Table 5].

**4. Bounds, computed for FT8's own signal set.** The capacity of single-symbol non-coherent 8-FSK with ideal soft metrics is the mutual information
$$C_{NC}(E_s/N_0)=\log_2M-\mathbb E\left[\log_2\frac{\sum_{j=1}^{M}I_0\!\left(2\sqrt{E_s}\,|r_j|/N_0\right)}{I_0\!\left(2\sqrt{E_s}\,|r_1|/N_0\right)}\right],$$
where $r_1$ is the correlator that holds the signal. The script evaluates it by Monte Carlo (Level 3 of the [BER page](ber-ebn0-and-shannon.md) shows the same construction for BPSK).
- FT8 carries 77/58 = 1.33 information bits per data symbol. This needs **Es/N0 ≥ 4.1 dB**, or **Eb/N0 ≥ 4.2 dB** once the sync symbols are counted. FT8 achieves 5.3 dB: **1.1 dB from its constellation's limit**.
- If the receiver knew the phase (coherent 8-FSK), the limit would be 1.2 dB. That is what coherence would be worth, if HF allowed it.
- The unconstrained Shannon bound at η = 6.09/50 = 0.12 b/s/Hz is −1.4 dB.
- **Finite length.** With the normal approximation $k\approx nC-\sqrt{nV}\,Q^{-1}(\varepsilon)$ (n = 58 symbols, dispersion V from the same Monte Carlo), the penalty term vanishes at ε = 0.5. That is exactly the 50 % criterion WSJT-X quotes, so the 4.2 dB limit already applies. Raising the decode probability to 90 % costs +0.8 dB in theory. FT8's measured curve [1 Fig. 7] rises from 50 % to ≈ 90 % over roughly the same 0.8–1 dB.

**5. Sync overhead.** The three 7×7 Costas arrays are 21 of 79 symbols, 27 % of the energy (1.1 dB). A Costas array has a nearly ideal two-dimensional (time × frequency) autocorrelation: a single sharp peak with sidelobes of at most one hit. So a search over time offset (DT) and audio frequency finds candidates reliably at the decoding threshold. FT4 spends 15 % on sync and Q65/FST4 about 25 %.

**6. A-priori (AP) decoding.** During a QSO the receiver already "knows" at least 62 of the 77 bits when it answers a CQ (both call signs, the message type). Fixing them as known reduces the search to about 15 bits, which is worth ≈ 2 dB on AWGN (−22.7 dB) and up to 10 dB on badly disturbed channels [1 Table 6]. It is a legitimate use of prior information, the same idea as known-header decoding, but the reported SNR then refers to a smaller message. Do not compare an AP threshold with another mode's no-AP threshold.

### Level 3 — channels, the older modes, and limits of the comparison
- **Doppler spread versus tone spacing.** On the ITU high-latitude-moderate channel (10 Hz frequency spread), FT8 (6.25 Hz spacing) never reaches 50 % decodes without AP, while FT4 (20.8 Hz spacing) reaches −12.2 dB [1 Table 6]. Rule: **tone spacing must exceed the channel's Doppler spread**. JT65B/C, JT9B–H and the Q65 B–E submodes widen the spacing for scatter and EME paths [2]. For a rocket the analogue is a Doppler *rate* during boost (142 Hz/s at 10 g of range acceleration, 433 MHz, from the [sync page](synchronization-carrier-timing.md); a station near the pad sees up to ≈ 1.4× the vehicle's acceleration because of the $v_\perp^2/R$ term, [15 impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md#doppler-rate-seen-from-the-ground--the-line-of-sight-rotation-term)), which moves an FT8 tone by 22.7 Hz (3.6 tone spacings) within one 0.16 s symbol and by ≈ 1.8 kHz over a 12.64 s transmission. An FT8-style waveform is therefore only usable from a stationary or slowly moving transmitter.
- **Why the older modes need more Eb/N0.**
  - *WSPR* is effectively non-coherent binary FSK: the known sync bit selects the tone pair. It uses a K = 32 convolutional code with sequential decoding and a 31-bit zero tail, which spends 38 % of the coded bits on the tail (−2.1 dB). At the guide's −31 dB (6.4 dB Eb/N0) it sits *below* the single-symbol non-coherent-BFSK limit (6.9 dB). That is possible only if the decoder exploits phase continuity across symbols, as WSJT-X's block detection does; whether current wsprd does this was not confirmed here. Older literature quotes −28 to −29 dB [3], which would put WSPR 1.5–2.5 dB above that limit.
  - *JT65* uses a Reed–Solomon code over 64-ary symbols, an algebraic code that WSJT-X decodes with the Franke–Taylor soft-decision algorithm. RS codes are not designed for soft decoding, and half of JT65's energy is sync. It sits 2.1 dB above the non-coherent 64-FSK limit.
  - *JT4* is 50 % sync with a binary data alphabet.
- **Q65's QRA code** is a Q-ary repeat-accumulate code over GF(64), decoded by non-binary belief propagation directly on 64-ary symbol likelihoods, so there is no bit-demapping loss. Its 12-bit CRC sits in two punctured (not transmitted) symbols, so it costs no airtime [2]. With 65-FSK the coherent limit at its rate is ≈ −0.1 dB; Q65-60A achieves 5.2 dB.
- **Multipass subtraction.** After decoding, WSJT-X regenerates the waveform, estimates the complex channel gain $g(t)$ by low-pass filtering $s(t)r^*(t)$, subtracts it and decodes again. This recovers weaker signals underneath strong ones on the same frequency [1 §6], a form of successive interference cancellation ([multiple access](multiple-access-and-duplexing.md)).
- **What the comparison leaves out.** WSJT-X thresholds come from the developers' simulations of their own decoder, with a known frequency and time search range. LoRa figures are datasheet or idealised-model numbers. Real-world losses (audio-chain non-linearity, clock error, interference from other users in the passband) are outside both.

### Other amateur digital modes in one paragraph each
- **PSK31.** BPSK at 31.25 baud with raised-cosine amplitude shaping between phase reversals. The occupied width is about 60 Hz. **Varicode** gives common characters short codewords (space and `e` are one and two bits), with `00` as the separator that no codeword contains, so plain lower-case text is cheaper than upper case. There is **no FEC**, so one hit garbles one character. It decodes at roughly −10 dB in 2500 Hz (Eb/N0 ≈ 9 dB [3]); differential detection keeps it simple. QPSK31 adds a K = 5 convolutional code.
- **RTTY.** Two-tone FSK, 45.45 baud, 170 Hz shift, 5-bit ITA2 (Baudot) with a start bit and 1–2 stop bits. Only 5 of every 7–7.5 bit-times carry data (≈ 30–32 b/s). It is detected with two filters and a comparator. It is ≈ −5 dB in 2500 Hz, an Eb/N0 of ≈ 14 dB [3]: uncoded non-coherent BFSK with wide filters.
- **CW.** On–off keying read by ear or by a narrow filter. Thresholds depend on the operator: about −12 to −18 dB in 2500 Hz depending on speed, i.e. Eb/N0 13–16 dB [3].
- **APRS packet.** AX.25 frames (with a CRC-16 FCS) sent as **Bell-202 AFSK**: 1200 baud with 1200/2200 Hz audio tones on an NBFM voice transmitter. It has no FEC, and its sensitivity is set by FM threshold plus the AFSK demodulator ([analog modulation](analog-modulation-am-fm-pm-ssb.md)). APRS is a frame format, not a weak-signal mode. It is useful as a model for position-report *content* (lat/long, altitude, course and speed in a few tens of bytes).
- **DMR** (ETSI TS 102 361): 4-FSK at 4800 symbols/s (9.6 kb/s) in a 12.5 kHz channel, with **two-slot TDMA** on a 30 ms slot structure. **D-STAR DV:** 0.5-GMSK at 4.8 kb/s in a 6.25 kHz channel, split into ≈ 2.4 kb/s AMBE voice, 1.2 kb/s FEC and 1.2 kb/s slow data (about 900 b/s usable). These are voice systems built for SNRs well above 0 dB in the channel, the opposite design point from FT8. Their details are from secondary sources ([log](../../research-logs/W5-S8-comms-phy.md)).

## Design equations & rules of thumb

| Equation / rule | When valid | Typical values |
|---|---|---|
| $E_b/N_0=\mathrm{SNR}_{2500}+34.0-10\log R_b$ | any mode; $R_b$ = user bits / Tx time | FT8 −20.8 dB, 6.09 b/s → 5.3 dB |
| $E_s/N_0=\mathrm{SNR}_{2500}+34.0+10\log T_s$ | per channel symbol | FT8: +5.2 dB at −20.8 dB |
| $P_{min}=-174+\mathrm{NF}+C/N_0$ dBm | 290 K | FT8, NF 6 dB: −154.8 dBm |
| Halve $R_b$ at fixed Eb/N0 → −3 dB SNR₂₅₀₀ | same code family | Q65-15A → 60A: −5 dB for 4× slower |
| Tone spacing ≳ Doppler spread | non-coherent MFSK | FT8 6.25 Hz fails at 10 Hz spread |
| Frequency stability ≪ tone spacing over the Tx time | MFSK weak-signal | 6.25 Hz = 0.014 ppm at 433 MHz |
| Modern LDPC/QRA modes: Eb/N0 ≈ 4.2–5.4 dB | 50 % decode, AWGN, no AP | 1–2 dB above the NC-MFSK limit |
| Sync energy 15–27 % (0.7–1.4 dB) | Costas / pseudo-random sync | FT8 27 %, FT4 15 % |

## Worked examples

### Example 1 — FT8's −21 dB, step by step
1. Reference noise: 2500 Hz → C/N0 = −20.8 + 34.0 = 13.2 dB-Hz.
2. Per symbol (T = 0.160 s): Es/N0 = 13.2 + 10 log 0.16 = 13.2 − 8.0 = **+5.2 dB**. Each tone is about 3.3× above the noise in its own 6.25 Hz bin.
3. Per user bit ($R_b$ = 77/12.64 s = 6.09 b/s): Eb/N0 = 13.2 − 7.85 = **5.3 dB**.
4. Limits: single-symbol non-coherent 8-FSK at 1.33 b/symbol, sync counted, gives 4.2 dB; coherent 8-FSK gives 1.2 dB; Shannon at η = 0.12 gives −1.4 dB.

So FT8 is a well-designed, near-limit non-coherent system. The −21 dB is a statement about the reference bandwidth, not about beating noise.

### Example 2 — FT8 versus LoRa SF12 at the same bit rate
- **Datasheet view.** SF12/125 kHz/CR 4/5 needs −20 dB in 125 kHz ([canonical values](../00-math-foundations/canonical-values-and-conventions.md)), which is −3.0 dB in 2500 Hz at the nominal (DE = 0) 293 b/s and Eb/N0 = 6.3 dB per payload bit. With NF 6 dB the LoRa sensitivity is −137.0 dBm, against −154.8 dBm for FT8. The 17.8 dB difference is **16.8 dB of bit-rate ratio** (293 vs 6.09 b/s) plus **1.0 dB of Eb/N0**.
- **Same message, all energy counted.** Send a 10-byte message (80 bits, close to FT8's 77) at SF12 with LDRO, an explicit header and CRC: 18 payload symbols plus 12.25 preamble symbols. With an ideal non-coherent 4096-ary detector and no correction (CR 4/5 only detects), 50 % packet success needs Es/N0 = 12.5 dB. Counting all 30.25 symbols' energy over 80 bits gives Eb/N0 = **8.3 dB**, which is **3.0 dB worse than FT8's 5.3 dB**. At 10 % and 1 % PER the LoRa figures are 9.4 and 10.3 dB.
- **At FT8's 6.09 b/s,** LoRa-style signalling would therefore need about −17.8 dB in 2500 Hz, against FT8's −20.8 dB.
- **Where the 3 dB goes.** The preamble (12.25 of 30.25 symbols, 2.3 dB) and the weak code. LoRa's own 4096-ary signal set at 8 b/symbol has a non-coherent capacity limit of ≈ 0 dB Eb/N0. The datasheet's 6.3 dB therefore leaves ≈ 6 dB that a strong soft-decision code could recover, at the cost of decoder complexity the chip does not have.
- **What LoRa buys with it:** ≈ 50× the rate, ±25 % of BW frequency tolerance (kHz, not Hz), no time-slotting, and a single-chip receiver.

### Example 3 — reading an FT8 signal report as a power
A ground station with NF 6 dB decodes your beacon at "−15 dB". The received power is −15 + 34.0 − 174 + 6 = **−149.0 dBm**. Because WSJT-X estimates the SNR from the decoded tones, its reports near threshold are rough and clipped (JT65 reports are limited to −30…−1 dB [2]). Use the report as a ±2–3 dB indicator, not a calibrated measurement.

### Example 4 — could a rocket recovery beacon use an FT8-style waveform?
After landing, the airframe is stationary, so a slow MFSK beacon is attractive. On 433 MHz at the Singapore 10 mW e.r.p. limit, with NF 6 dB at the receiver, an FT8-class waveform needs −154.8 dBm, which is 17.8 dB (×7.8 in free-space range) better than LoRa SF12/125 kHz. There are three catches:
1. **Stability.** 6.25 Hz is 0.014 ppm at 433 MHz, and the tone must stay well inside one spacing for the whole 12.6 s. A typical TCXO tempco of order 0.1 ppm/°C is 43 Hz per °C at 433 MHz, so even a slow cool-down of the board after landing can drift the tone by several spacings within one transmission. You need a GNSS-disciplined or ovenised reference, or wider tones (FT4-like 20.8 Hz, or Q65-style B–E spacings). The decoder's exact drift tolerance is not published in [1] or [2].
2. **Timing.** FT8 needs both ends on UTC to well under a second. A landed rocket with a GNSS fix has this.
3. **Rules and tools.** On an ISM SRD band the waveform must meet that band's limits ([Singapore rules](../19-regulations-safety/singapore-imda-rules.md)). Amateur bands need a licence ([amateur licensing](../19-regulations-safety/amateur-radio-licensing.md)). Using the name "FT8" for a non-conforming variant is against the designers' published terms [1 §9].

A practical middle path is LoRa SF12 at the narrowest bandwidth the module allows (SX127x 7.8 kHz: 15.3 b/s with LDRO, about −15 dB in 2500 Hz), or a custom MFSK on an SX126x/Si4463 in FSK mode with an SDR receiver.

### Example 5 — WSPR's −31 dB in perspective
WSPR's 50 bits in 110.6 s is 0.45 b/s. At −31 dB, Eb/N0 = 2.98 + 3.45 = **6.4 dB**, about 1 dB *worse* per bit than FT8. The 10 dB lower SNR comes from being 13× slower (11.3 dB). PA3FWM's −29 dB with half the energy treated as sync gives "≈ 5 dB" [3]. Both statements are consistent; they differ only in how sync energy is booked.

## Practical notes
- **Clocks.** Every WSJT-X mode needs UTC on both ends (NTP or GNSS) and an audio chain with no AGC/ALC pumping. Overdriving an SSB transmitter's audio input creates intermodulation copies of the tones.
- **Hardware for beacons.** WSPR and FT8 transmitters are often built from an Si5351 clock generator switched between tones by a microcontroller. The tones are clean only if the reference is stable to ≪ 1 Hz. On UHF this needs a TCXO plus GNSS correction.
- **Software.** WSJT-X is GPLv3 and its decoders are not public domain. The protocol definitions are public [1 §9]. Independent embedded encoders and decoders exist (for example kgoba's `ft8_lib` in C); check the licence before reusing them in flight code.
- **Data payload.** FT8's free-text type carries at most 13 characters, and the telemetry type 71 bits (18 hex digits) [1 Table 1]. That is enough for a compressed lat/long/altitude (about 50–60 bits at metre resolution over a launch site).
- **SNR reports** from different programs are not on the same scale. WSJT-X's are derived from the decoded tones; a waterfall reading is a rough guide only.

## Common mistakes & misconceptions
- **"FT8 works below the noise, so it beats Shannon."** Per bit it needs +5.3 dB Eb/N0, against a limit of −1.4 dB at its spectral efficiency. "Below the noise" refers to a 2500 Hz reference bandwidth that is 400× wider than the symbol filter.
- **Comparing modes by SNR₂₅₀₀ alone.** WSPR's −31 dB and FT8's −21 dB differ by bit rate, not by quality. Compare Eb/N0, or required power at equal bit rate.
- **Mixing threshold definitions.** WSJT-X thresholds are 50 % decode probability. LoRa datasheet thresholds are a low PER on a test packet. Going from 50 % to 90 % costs about 1 dB for FT8.
- **Quoting the AP threshold (−22.7 or −24 dB) as FT8's sensitivity.** AP decoding assumes most of the message is already known.
- **Ignoring sync energy.** Some tables subtract it (WSPR "5 dB"), others include it (6.4 dB). Say which.
- **Expecting FT8 to work on auroral, EME or moving-platform paths.** Doppler spread or Doppler rate larger than 6.25 Hz destroys it. Use wider-spaced submodes or FT4.
- **"LoRa is worse than FT8 because of chirps."** The chirp is just a way of making non-coherent M-FSK tolerant of frequency offset. The 3 dB per bit goes on preamble overhead and the Hamming code.
- **Thinking PSK31 or RTTY have error correction.** They have none, hence 9–14 dB Eb/N0.

## How to simulate / verify
- **`python3 tools/verify/s8_weak_signal_ebn0.py`** (≈ 25 s): **34/34 PASS**; output in `tools/verify/s8_weak_signal_ebn0_output.txt`. It builds the mode table (SNR₂₅₀₀ → C/N0 → Es/N0 → Eb/N0); computes the "why −21 dB" decomposition; Monte-Carlo capacity of non-coherent and coherent orthogonal M-FSK, and from it each mode's limit, including FT8's normal-approximation penalty at 50 % and 90 %; the Shannon and finite-k energy-limited bounds; the LoRa SF12 short-message model (payload symbol count, exact NC-4096-FSK SER, all-energy Eb/N0 at 50/10/1 % PER), and LoRa's own 4096-ary capacity limit; and the worked-example numbers.
- **WSJT-X itself** can add calibrated noise to a recorded `.wav` ("Degrade S/N of .wav file") to measure decode probability against SNR, the method behind the published thresholds [2].
- For your own MFSK telemetry, simulate with the soft metric $L_j$ above and any LDPC decoder (for example AFF3CT, or Sionna, from the [channel coding](channel-coding-fec.md) page).

## Open questions / gaps
- WSJT-X Table 7 rounds thresholds to 1 dB. Only FT8/FT4 have 0.1 dB values (QEX), so the other Eb/N0 values are ±0.5 dB.
- The LoRa comparison uses an idealised receiver (no header correction, ideal NC detection, LDRO treated as 4096-ary). Real SX126x performance is about 1 dB worse ([LoRa sensitivity](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md)).
- PSK31, RTTY and CW thresholds come from a practitioner table with no stated error criterion [3]. DMR and D-STAR parameters are from secondary summaries, not the ETSI/JARL texts.
- Not verified here: the claim that block detection explains why WSPR's −31 dB lies below the single-symbol NC-BFSK limit. An independent simulation of wsprd would settle it.
- An FT8-style UHF beacon has not been tested by the team. Its frequency-drift budget should be measured (TCXO plus GNSS) before relying on it.

## Sources
1. S. Franke (K9AN), B. Somerville (G4WJS), J. Taylor (K1JT), "The FT4 and FT8 Communication Protocols," *QEX*, July/August 2020, pp. 7–17. https://wsjt.sourceforge.io/FT4_FT8_QEX.pdf — message types, CRC-14, LDPC(174,91), GFSK pulses (BT 1/2), Costas arrays, soft demapper, block detection, BP + OSD, AP decoding, multipass subtraction, Tables 5–6 thresholds and Fig. 7 decode curves. (peer-reviewed magazine; primary, by the designers)
2. WSJT Development Group, *WSJT-X 2.5 User Guide*, §17 "Protocol Specifications" and Table 7 "Parameters of Slow Modes" (FEC, (n,k), Q, keying rate, bandwidth, sync energy, Tx duration, 50 % threshold in 2500 Hz); §7 on signal-report conventions. https://wsjt.sourceforge.io/wsjtx-doc/ (software documentation, primary)
3. P.-T. de Boer (PA3FWM), "Signal/noise ratio of digital amateur modes," technote tn09b. https://www.pa3fwm.nl/technotes/tn09b.html — SNR₂₅₀₀ and Eb/N0 for RTTY, PSK31, CW variants, WSPR, JT65; footnotes on sync energy. (practitioner note; no error criterion stated)
4. D. Tse, P. Viswanath, *Fundamentals of Wireless Communication*, Cambridge 2005, §5.2 (capacity in the power-limited regime) and §B (information measures) — background for the constrained-capacity bounds. (textbook)
5. J. G. Proakis, M. Salehi, *Digital Communications*, 5th ed., McGraw-Hill 2008, §4.5 (non-coherent M-ary orthogonal detection) and §6.5 (channel capacity of M-ary orthogonal signals). (textbook)
6. Y. Polyanskiy, H. V. Poor, S. Verdú, "Channel coding rate in the finite blocklength regime," *IEEE Trans. Inf. Theory* 56(5), 2010 — normal approximation used for the 50 %/90 % penalty. (peer-reviewed)
7. M. P. C. Fossorier, S. Lin, "Soft-decision decoding of linear block codes based on ordered statistics," *IEEE Trans. Inf. Theory* 41(5):1379–1396, 1995 — OSD. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
8. J. P. Costas, "A study of a class of detection waveforms having nearly ideal range–Doppler ambiguity properties," *Proc. IEEE* 72(8):996–1009, 1984 — Costas arrays. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
9. Semtech, SX1276/77/78/79 and SX1261/2 datasheets — LoRa SNR thresholds, ToA formula, LDRO. (datasheet; via [canonical values](../00-math-foundations/canonical-values-and-conventions.md))
10. ETSI TS 102 361-1 (DMR air interface) and JARL D-STAR specification — cited via secondary summaries (sigidwiki, LIMARC "D-STAR Basics"); not read in the original. (standard, secondary access)
11. Verification: `tools/verify/s8_weak_signal_ebn0.py`. (numerical check)
