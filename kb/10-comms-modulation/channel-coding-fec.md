---
title: Channel coding and forward error correction (FEC)
domain: 10-comms-modulation
slug: channel-coding-fec
tags: [FEC, channel-coding, Hamming, Golay, BCH, Reed-Solomon, convolutional-code, Viterbi, puncturing, turbo-code, LDPC, polar-code, interleaving, coding-gain, soft-decision, LoRa-coding-rate, CCSDS]
prerequisites:
  - ber-ebn0-and-shannon.md
  - ../00-math-foundations/matrices-and-linear-algebra-for-networks.md
  - ../00-math-foundations/probability-random-processes-and-psd.md
related:
  - packet-framing-protocols.md
  - modulation-choice-guide.md
  - digital-modulation-psk-qam-fsk.md
  - spread-spectrum-dsss-fhss-css.md
  - ../15-lora-ism-radios/lora-phy-css-math.md
  - ../15-lora-ism-radios/rocket-telemetry-radio-design.md
  - ../09-propagation-link-budget/link-margin-availability.md
  - ../09-propagation-link-budget/multipath-fading-doppler.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Channel coding and forward error correction (FEC)

## Questions this page answers
- What does forward error correction actually buy me in dB, and why is "coding gain" quoted at a specific BER?
- What do (n, k), code rate, minimum distance and "corrects t errors" mean?
- How do Hamming, Golay, BCH and Reed–Solomon block codes differ, and when is each appropriate?
- How does a convolutional code and the Viterbi decoder work, and what is the K = 7, rate-½ "NASA standard" code?
- Why is soft-decision decoding about 2 dB better than hard-decision?
- What are turbo, LDPC and polar codes, and are they practical on a microcontroller?
- What is interleaving, and how deep must it be for my fading or spinning-rocket channel?
- What does LoRa's coding rate CR 4/5 … 4/8 really do for me?
- Which FEC libraries can I use for a custom radio?
- For short telemetry packets, how close to Shannon can any code get?
- What are trellis-coded modulation (TCM) and bit-interleaved coded modulation (BICM), and why did BICM win?
- How does belief-propagation decoding of an LDPC code actually work?

## TL;DR
- A code adds $n-k$ redundant bits to $k$ information bits (rate $r=k/n$). With minimum distance $d$ it corrects $t=\lfloor(d-1)/2\rfloor$ errors or detects $d-1$. **Coding gain** = reduction in required $E_b/N_0$ (per *information* bit) at a stated BER vs uncoded BPSK (9.6 dB at 1e-5).
- **Numbers (AWGN, BPSK, BER 1e-5; verified in `tools/verify/comms_coding.py` unless noted):**

  | Code | Eb/N0 @ 1e-5 | Gain |
  |---|---|---|
  | Uncoded BPSK | 9.6 dB | 0 |
  | Hamming(7,4), hard | 9.2 dB | 0.4 dB |
  | Golay(23,12), hard | 7.3–7.5 dB | 2.1–2.3 dB (depends on decoded-error approximation) |
  | RS(255,223), hard bits | 6.3 dB | 3.3 dB |
  | Conv. K=7 r=½ (171,133), hard Viterbi | 6.5 dB | 3.1 dB |
  | Conv. K=7 r=½, soft Viterbi | **4.2 dB** | **5.4 dB** (CCSDS: ≈ 5.5 dB) |
  | RS(255,223) + K=7 conv, ideal interleaving | **2.3 dB** | 7.3 dB (CCSDS: +2.0 dB over conv) |
  | Turbo r=½, k = 8920 (CCSDS) | ≈ 1 dB | ≈ 8.5 dB (CCSDS Green Book, not re-simulated) |
  | Rate-½ binary capacity limit | 0.19 dB | – |
- **Soft beats hard by ≈ 2–2.4 dB** (2.35 dB from the K=7 union bounds; CCSDS: "> 2 dB"; 3-bit quantisation recovers most, 8-bit is within 0.2 dB of unquantised) [3].
- **Modern codes** (turbo 1993, LDPC 1962/1996, polar 2009) approach capacity within ≈ 0.5–1 dB for long blocks; for **short packets** the finite-length penalty dominates (≈ 1.6 dB above the limit for 256 information bits at rate ½, WER 1e-4 — see [BER page](ber-ebn0-and-shannon.md)).
- **Interleaving** turns burst errors (fades, interference, rocket spin nulls) into scattered ones the decoder can fix; depth must exceed burst length, at the cost of latency = depth × codeword.
- **LoRa CR 4/5–4/8** are tiny Hamming-type codes: 4/5 and 4/6 only *detect*; 4/7 and 4/8 correct one bit per codeword; with LoRa's diagonal interleaver that means one wrong chirp per block. In an idealised AWGN model the net gain in Eb/N0 at 1 % PER is only **≈ 0–0.4 dB** (CR 4/7) and CR 4/8 is slightly *worse* than 4/5 (`comms_lora_cr.py`); the benefit is robustness to isolated symbol hits (interference, bursts), paid for with 1.4–1.6× air time.
- **Coded modulation:** TCM gains 3.0 dB (4-state) or 3.6 dB (8-state) over uncoded QPSK on 8-PSK with *no* bandwidth growth (verified $d^2_\text{free}$ = 4.0 / 4.586). BICM (binary LDPC/turbo + interleaver + Gray QAM) is ≈ 0.2 dB from the constellation limit and far better on fading channels, which is why modern standards use it.
- **Belief propagation** (tanh-rule sum-product) on a random (3,6)-regular LDPC with n = 1008: FER 3 % at 2.0 dB and 0/400 at 2.5 dB (`s8_info_coding.py`).
- Practical libraries: Phil Karn's **libfec** (Viterbi, RS), **liquid-dsp** (Hamming, Golay, conv, RS), **GNU Radio gr-fec** (CC, polar, LDPC), **AFF3CT** (turbo/LDPC/polar, research-grade), **Sionna** (Python/TF, 5G LDPC/polar).

## Intuition (no math)
Noise flips bits at random. If you send each bit once, a flipped bit is simply wrong. If you add structured redundancy, the receiver can notice that the received pattern is "not a legal codeword" and move to the nearest legal one. The key is *distance*: legal codewords are chosen so that any two differ in many positions, so a few flips still leave the received word closer to the right codeword than to any other.

Redundancy costs energy: at a fixed transmit power and information rate, sending more bits means less energy per transmitted bit, so each coded bit is *more* likely to be flipped. Good codes win anyway because their error correction more than compensates. Bad or small codes (a single parity bit, Hamming(7,4) with hard decisions) barely break even.

**Soft decisions** tell the decoder not just "0 or 1" but how confident the demodulator was. A bit that barely crossed the threshold is a prime suspect; a strong one is almost certainly right. Throwing that information away (hard decisions) costs about 2 dB — roughly a factor 1.6 in power.

**Convolutional codes** smear each input bit across many output bits through a shift register; the Viterbi decoder finds the most likely path through all possible register states. **Turbo and LDPC codes** use huge, random-looking structures that no one can decode exactly — instead, simple local decoders exchange beliefs back and forth until they agree. That iterative trick is what finally reached within a fraction of a dB of Shannon's limit.

Codes assume errors are scattered. Real channels produce bursts — a deep fade as a rocket rolls, a nearby transmitter keying up. **Interleaving** shuffles the order of bits over the air so that a burst lands as isolated errors spread over many codewords.

## The math

### Level 1 — parameters and gains
| Symbol | Meaning |
|---|---|
| $(n,k)$ | codeword length, information bits; rate $r=k/n$ |
| $d_{min}$ (block) / $d_{free}$ (convolutional) | minimum Hamming distance between codewords |
| $t=\lfloor(d-1)/2\rfloor$ | guaranteed correctable errors; or detect $d-1$; or correct $e$ erasures + $t'$ errors if $e+2t'<d$ |
| $E_c=rE_b$ | energy per coded (channel) bit |
| Coding gain $G=(E_b/N_0)_{uncoded}-(E_b/N_0)_{coded}$ at target BER | dB; depends on the BER |
| Asymptotic soft gain $\approx10\log_{10}(r\,d)$; hard ≈ $10\log_{10}(r(t+1))$ | high SNR limit |

Examples: K=7 r=½: $10\log_{10}(0.5\cdot10)=7.0$ dB asymptotic (soft), 5.4 dB actually achieved at 1e-5 — the gap is the "error-coefficient" penalty (36 information bit errors per $d_{free}$ event).

**Bounds on what block codes can do.** Singleton: $d\le n-k+1$ (Reed–Solomon codes meet it — *maximum-distance separable*). Hamming (sphere-packing) bound: $\sum_{i=0}^{t}\binom ni\le2^{n-k}$ (binary); codes meeting it are *perfect* — the Hamming codes ($t=1$) and the binary Golay(23,12) ($t=3$).

### Level 2 — the classical codes

**Linear block codes.** Codewords $\mathbf c=\mathbf mG$ (generator matrix $G$, $k\times n$); parity-check matrix $H$ with $G H^T=0$. Received $\mathbf r=\mathbf c+\mathbf e$; syndrome $\mathbf s=\mathbf rH^T=\mathbf eH^T$ depends only on the error. Syndrome decoding looks up the most likely $\mathbf e$ for each $\mathbf s$.

*Hamming codes* $(2^m-1,\,2^m-1-m)$, $d=3$: the columns of $H$ are all nonzero $m$-bit patterns, so a single error's syndrome *is* its position [4]. Hamming(7,4): with hard decisions its gain at 1e-5 is only **0.4 dB** — the rate loss (4/7 → −2.4 dB per coded bit) eats most of the correction. Extended Hamming(8,4) adds overall parity: $d=4$, corrects 1 and detects 2. *Golay(23,12)* ($d=7$, corrects 3) gives **≈ 2.1–2.3 dB** hard (the spread is the usual uncertainty in how many information bits a failed bounded-distance decode corrupts).

*Cyclic codes, BCH.* If every cyclic shift of a codeword is a codeword, the code is generated by a polynomial $g(x)$ dividing $x^n-1$; encoding is polynomial division — the same shift-register hardware as a CRC ([packet framing](packet-framing-protocols.md)). BCH codes choose $g(x)$ with prescribed roots in $GF(2^m)$ to guarantee $d\ge2t+1$, decoded algebraically (Berlekamp–Massey + Chien search) [1 ch. 6–7], [5].

*Reed–Solomon (RS).* Non-binary BCH codes over $GF(2^m)$: symbols of $m$ bits, $n=2^m-1$, $d=n-k+1$, corrects $t=(n-k)/2$ **symbol** errors (or $n-k$ erasures) [6]. RS(255,223) over bytes corrects 16 byte errors per 255-byte codeword — any burst of up to $8(t-1)+1=121$ bits, because a burst only damages the bytes it touches. That makes RS the natural outer code behind a convolutional or Viterbi inner code whose errors come in bursts. CCSDS specifies RS(255,223) (E = 16) and RS(255,239) (E = 8) with field polynomial $x^8+x^7+x^2+x+1$ and interleaving depth I = 1, 2, 3, 4, 5 or 8 [2 §4]. On its own with hard BPSK bits: 6.3 dB at 1e-5 (3.3 dB gain).

**Convolutional codes.** A rate-$1/n$ code with constraint length $K$ passes the data through a $K$-bit shift register; each input bit produces $n$ output bits, each the modulo-2 sum of taps given by a generator (octal notation). The CCSDS/NASA standard: $K=7$, $r=\tfrac12$, $G_1=171_8$, $G_2=133_8$ (with an inverter on one output in CCSDS for transition density), punctured to 2/3, 3/4, 5/6, 7/8 [2 §3]. The script derives its weight spectrum from the state diagram: $d_{free}=10$, information-weight coefficients $B_{10},B_{12},B_{14},B_{16}=36,211,1404,11633$ (only even weights occur).

*Viterbi decoding.* The encoder is a finite-state machine with $2^{K-1}=64$ states; every possible input sequence is a path through the **trellis**. Maximum-likelihood sequence decoding picks the path whose output is closest to the received sequence — in Euclidean distance for soft inputs (equivalently maximum correlation $\sum y_ic_i$ with $c_i=\pm1$), Hamming distance for hard. The Viterbi algorithm keeps, for each state, only the best ("survivor") path into it: at each step, **add** branch metrics, **compare** the two candidates, **select** the better (ACS). Complexity $\propto2^{K-1}$ per bit, independent of message length; decisions are released after a traceback depth of ≈ 5K–7K bits [7], [8].

*Performance bounds* (union bound over error events, verified against Monte-Carlo within the expected factor): soft $P_b\le\sum_dB_dQ\big(\sqrt{2dr\,E_b/N_0}\big)$; hard $P_b\le\sum_dB_dP_2(d)$ with $P_2(d)$ the probability that $\ge d/2$ of $d$ BSC bits flip, crossover $p=Q(\sqrt{2rE_b/N_0})$. Results: soft 4.17 dB, hard 6.52 dB at 1e-5; Monte-Carlo soft Viterbi 1.4e-5 at 4.0 dB.

**Why soft decisions gain ≈ 2 dB.** For a binary-input channel, hard slicing turns a Gaussian channel into a binary symmetric channel; at low SNR the capacity ratio tends to $2/\pi$ (−1.96 dB), the same factor as hard-limiting a correlator ([matched filter](matched-filter-detection.md)). CCSDS: 8-bit quantisation < 0.2 dB from ideal; hard > 2 dB loss; recommends ≥ 3-bit soft decisions [2 §3.2.4], [3 §4].

### Level 3 — concatenation, iterative codes and the short-block regime
**Concatenated codes** (Forney 1966): inner convolutional code with soft Viterbi, outer RS on bytes, a symbol interleaver between them so that Viterbi bursts spread over several RS codewords. Simulation with measured Viterbi *byte* error rates and ideal interleaving: 2.25 dB at 1e-5 overall — 1.9 dB better than the convolutional code alone, matching the CCSDS figure of ≈ 2.0 dB [3 §3.3.3]. This was the Voyager-era deep-space standard.

**Turbo codes** (Berrou, Glavieux, Thitimajshima 1993): two recursive systematic convolutional encoders in parallel, the second fed through a long pseudo-random interleaver. Decoding alternates two soft-in/soft-out (BCJR/MAP) decoders that exchange *extrinsic* log-likelihood ratios; after 8–18 iterations performance comes within ≈ 0.5–1 dB of capacity for long blocks [9]. CCSDS turbo codes: 16-state components, rates ½, ⅓, ¼, ⅙, $k$ = 1784–8920 bits; the Green Book notes they come within ≈ 1 dB of the rate-½ limit and 1.5 dB better than RS+conv [2 §6], [3 §7]. Downsides: latency (the whole block), an "error floor" at low BER, and decoder memory.

**LDPC codes** (Gallager 1962; rediscovered by MacKay & Neal 1996): linear block codes with a sparse $H$. Represented as a Tanner graph (variable nodes ↔ check nodes), decoded by belief propagation / min-sum, which is massively parallel [10]. Irregular, optimised LDPC codes can be within hundredths of a dB of capacity at very long lengths; practical codes: CCSDS (8160,7136) rate ≈ 7/8 and the AR4JA family (½, ⅔, ⅘), DVB-S2, Wi-Fi 802.11n/ac/ax, 5G NR data channels [2 §7], [11].

**Polar codes** (Arıkan 2009): recursively combining channels "polarises" them into almost-perfect and almost-useless sub-channels; information goes on the good ones, frozen bits on the bad. Successive-cancellation decoding provably achieves capacity as $n\to\infty$; with CRC-aided list decoding they are excellent at *short* lengths — which is why 5G NR uses them for control channels [12], [11].

**Coded modulation: TCM and BICM (W5-S8).** Binary codes on BPSK/QPSK pay for redundancy with bandwidth. **Coded modulation** instead adds redundancy by enlarging the constellation, keeping the symbol rate (and bandwidth) fixed.
- **Trellis-coded modulation** (Ungerboeck 1982 [16]). Send 2 information bits per symbol on 8-PSK instead of QPSK, with a rate-⅔ convolutional code choosing the point. **Set partitioning** splits 8-PSK into subsets with growing minimum distance: squared distances 0.586 → 2 → 4 for unit energy. The code protects the bits that select the subset, and the uncoded bit selects a point within it. Distance is then measured in Euclidean terms along trellis paths, $d^2_\text{free}$, and the asymptotic gain over uncoded QPSK ($d^2=2$) is $10\log(d^2_\text{free}/2)$.
  - The script's parity-check search (natural mapping, worst-case label distances) gives $d^2_\text{free}$ = **4.000 for the 4-state code** (limited by parallel transitions, the antipodal pair inside a subset) and **4.586 for the 8-state code**: **3.0 dB and 3.6 dB** with no bandwidth expansion.
  - Decoding is a Viterbi algorithm with Euclidean branch metrics.
  - TCM was the V.32/V.34 modem technology. It is optimal for AWGN at moderate complexity, but its diversity on fading channels is limited by the number of distinct symbols in an error event.
- **Bit-interleaved coded modulation** (Zehavi 1992; Caire–Taricco–Biglieri 1998). Put a strong *binary* code (turbo/LDPC), a bit interleaver and a Gray mapper in front of any QAM. The demapper computes a per-bit LLR, $L(b_i)=\ln\frac{\sum_{s:b_i=0}e^{-|y-s|^2/N_0}}{\sum_{s:b_i=1}e^{-|y-s|^2/N_0}}$, and the binary decoder never sees the constellation.
  - BICM gives up a little capacity: with Gray 16-QAM at 2 b/symbol it needs 5.30 dB against 5.09 dB for the full constellation-constrained limit ([BER page Level 3b](ber-ebn0-and-shannon.md)).
  - In exchange, the bit interleaver gives *much* better diversity on fading channels, and one code serves every modulation order.
  - That is why Wi-Fi, LTE/NR and DVB-S2 use BICM, and TCM survives mainly in legacy modems.

**Belief propagation, concretely (W5-S8).** Represent an LDPC code by its Tanner graph: variable nodes (bits) and check nodes (parity equations), joined by an edge wherever H has a 1. In the LLR domain with channel LLR $L_v=2y_v/\sigma^2$ (BPSK, +1 ↔ bit 0), each iteration does three things:
1. **Variable → check:** $m_{v\to c}=L_v+\sum_{c'\ne c}m_{c'\to v}$, i.e. everything the bit knows except what this check told it.
2. **Check → variable** (the "tanh rule", exact for a parity check): $m_{c\to v}=2\,\mathrm{artanh}\prod_{v'\ne v}\tanh(m_{v'\to c}/2)$. **Min-sum** approximates it by $\prod\mathrm{sgn}\cdot\min|m|$, usually with a 0.7–0.8 scaling or an offset.
3. **Decide** $\hat b_v=[L_v+\sum_cm_{c\to v}<0]$, and stop as soon as the syndrome is zero.

On a cycle-free graph this computes the exact bit-wise posteriors. With cycles it is an approximation that works extremely well when the cycles are long. Density evolution gives the threshold of the (3,6)-regular ensemble at ≈ 1.1 dB Eb/N0 (Richardson–Urbanke, cited from knowledge), against 0.19 dB for any rate-½ binary code. The script builds a **random (3,6)-regular code with n = 1008** and decodes it with 50 iterations of sum-product: FER 0.23 / 0.03 / 0 (of 400 frames) and BER 1.5×10⁻² / 1.5×10⁻³ / 0 at Eb/N0 = 1.5 / 2.0 / 2.5 dB. That is ≈ 2 dB from the rate-½ limit with a randomly drawn code of 63 bytes of information, against 8.4 dB for uncoded BPSK at 10⁻⁴. Optimised irregular, structured codes (QC-LDPC in Wi-Fi, NR, CCSDS AR4JA) gain a further few tenths of a dB and are hardware-friendly. The same message-passing idea, on 64-ary symbols instead of bits, decodes Q65's repeat-accumulate code, and FT8 uses BP plus ordered-statistics decoding on its (174,91) LDPC ([weak-signal modes](weak-signal-digital-modes.md#level-2--why-ft8-works-at-21-db-and-how-close-to-the-limit-it-is)).

**The short-block regime** matters for telemetry. A 32-byte frame is 256 information bits; the normal approximation (BER page) says no rate-½ code can do better than ≈ 1.6 dB Eb/N0 at WER 1e-4 at that length. Good practical short codes: tail-biting convolutional codes (no tail overhead), CRC-aided polar list decoding, short LDPC (e.g. CCSDS telecommand LDPC(128,64)), extended BCH. Turbo/LDPC advantages largely evaporate below a few hundred bits.

**Interleaving.** A *block interleaver* writes $D$ codewords as rows and transmits by columns: a burst of length $\le D$ symbols touches each codeword at most once (checked in the script). A *convolutional (Forney/Ramsey) interleaver* achieves the same with half the memory and delay. Required depth: burst duration × symbol rate ≤ depth × (correctable errors per codeword). Latency ≈ $D\,n$ symbols each way. For slow fading, the interleaver must span several fade durations (coherence times) to help; if the fade lasts longer than the whole interleaver, only ARQ or diversity helps ([multipath](../09-propagation-link-budget/multipath-fading-doppler.md)).

**What LoRa's coding rate does** (details of the PHY in [LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md)). Reverse-engineering and Semtech documentation show: 4 data bits per codeword; CR 4/5 adds one parity bit ($d=2$, detect only); CR 4/6 adds two ($d=2$ at best for any (6,4) binary code — verified by exhaustive search — so detect only); CR 4/7 is Hamming(7,4) ($d=3$, corrects 1); CR 4/8 is extended Hamming(8,4) ($d=4$, corrects 1, detects 2). A **diagonal interleaver** spreads each codeword's bits across $4+\text{CR}$ consecutive chirps, and each chirp carries one bit of each of SF codewords, so a single wrong chirp costs at most one bit per codeword; Gray mapping makes the common ±1-bin error (from residual frequency/timing offset) a single bit error [13], [14]. Under an idealised AWGN model (non-coherent $2^{SF}$-ary symbol errors, uniformly random wrong symbol, bit-level Hamming decoding, 32-byte packets, 1 % PER) the script finds:

| | CR 4/5 | CR 4/6 | CR 4/7 | CR 4/8 |
|---|---|---|---|---|
| SF7: required Eb/N0 | 6.6 dB | 7.3 | 6.2 | 6.9 |
| SF12: required Eb/N0 | 5.1 dB | 5.8 | 5.0 | 5.6 |
| Air time vs 4/5 | 1.0× | 1.2× | 1.4× | 1.6× |

(Monte-Carlo precision ≈ ±0.2 dB.) So in white noise the Hamming codes roughly pay for their own overhead and no more. Per *symbol* (the SNR a datasheet quotes), CR 4/8 works at ≈ 1.5–1.8 dB lower SNR than 4/5 — but with 1.6× the symbols, which is about what the extra energy alone would buy. The real value of CR 4/7–4/8 is against *isolated* symbol hits (a colliding packet, a brief interferer, a single timing slip). For a meaningful coding gain on a custom LoRa-rate link, add an outer code (e.g. RS over the payload, or packet-level erasure coding across frames).

## Design equations & rules of thumb

| Equation / rule | When valid | Typical values |
|---|---|---|
| $t=\lfloor(d-1)/2\rfloor$; erasures $e+2t'<d$ | any code | RS(255,223): t = 16 bytes |
| $G_{asym,soft}\approx10\log_{10}(rd)$ | high SNR, soft ML | K=7 r=½: 7.0 dB (5.4 at 1e-5) |
| soft vs hard ≈ 2 dB; 3-bit soft ≈ 0.2–0.3 dB from ideal | BPSK/AWGN | CCSDS: 8-bit < 0.2 dB |
| Viterbi complexity $2^{K-1}$ ACS/bit; traceback ≈ 5K–7K | conv codes | K=7: 64 states, 35–50 bits |
| RS burst correction $m(t-1)+1$ bits | RS over $GF(2^m)$ | 121 bits for RS(255,223) |
| Interleaver depth $D\ge$ burst length / correctable symbols per codeword | bursty channels | latency $D\cdot n$ |
| Concatenated RS(255,223)+K7: ≈ 2.3 dB @1e-5 | ideal interleaving | deep-space classic |
| Turbo/LDPC long blocks: within 0.5–1 dB of limit | k ≥ several thousand | error floor at 1e-7–1e-9 |
| Short blocks: add ≈ 1.6 dB (256 b), 2.4 dB (100 b) to the rate limit | WER 1e-4, rate ½ | normal approximation |
| TCM gain $10\log(d^2_\text{free}/d^2_\text{uncoded})$ | AWGN, high SNR | 8-PSK 4/8 states: 3.0/3.6 dB over QPSK |
| BICM loss vs CM capacity | Gray mapping | 16-QAM at 2 b/sym: ≈ 0.2 dB |
| BP check update $2\,\mathrm{artanh}\prod\tanh(m/2)$; min-sum ≈ sgn·min | LDPC decoding | min-sum with ≈ 0.75 scaling: a few tenths of a dB loss (literature value, not simulated) |
| (3,6)-regular LDPC BP threshold ≈ 1.1 dB | rate ½, n → ∞ | n = 1008: FER 3 % at 2.0 dB |

## Worked examples

### Example 1 — What coding does to range
10 kb/s rocket link, NF 6 dB, 2 dB implementation loss (continuing the [BER page](ber-ebn0-and-shannon.md) example): uncoded BPSK needs −116.4 dBm; K=7 soft Viterbi −121.8 dBm (5.4 dB); RS+conv concatenated −123.7 dBm (7.3 dB). In free space each 6 dB doubles range, so the concatenated code gives ×2.3 range — or, at the same range, lets you drop from 2 W to 0.37 W. The costs: 2.3× the symbol rate ($1/r$ = 2 × 255/223) and therefore bandwidth, plus decoder latency of one RS codeword (≈ 2040 bits ≈ 0.2 s at 10 kb/s with I = 1).

### Example 2 — Interleaver for a rolling rocket
Suppose the vehicle's antenna pattern has a null that sweeps past the ground station twice per revolution at 4 rev/s, each null ≈ 20 ms long (illustrative; measure your own). At 10 kb/s coded, a null wipes ≈ 200 bits = 25 bytes. RS(255,223) corrects 16 bytes per codeword, so one burst per codeword is not correctable with I = 1. With I = 2 each codeword sees ≤ 13 bytes of the burst — correctable, provided the next null (125 ms later = 1250 bits = 156 bytes) falls in a different codeword pair. Latency grows to 2 × 255 bytes = 408 ms. If latency matters more than recovering every frame, prefer shorter frames with CRC and accept losses, or use antenna diversity.

### Example 3 — Is Hamming(7,4) worth it on its own?
Hard decisions, BPSK, 1e-5: 9.2 dB vs 9.6 dB uncoded — 0.4 dB for 75 % more bandwidth. Not worth it as the only code. It *is* worth it (with interleaving) when the error pattern is "occasional isolated bad symbol", e.g. LoRa CR 4/7 against short interference.

### Example 4 — Picking an FEC for a custom 433 MHz GFSK telemetry radio
Constraints: ESP32-S3-class MCU, 20 kb/s air rate, 64-byte frames, downlink only (no ARQ). A K=7 r=½ convolutional code with 3-bit soft Viterbi (libfec or liquid-dsp) costs a few percent of a 240 MHz core at 10 kb/s information rate and gives ≈ 5 dB if the GFSK demodulator can deliver soft bits (discriminator output amplitude). Add a CRC-16 for frame validation, whiten the data, and interleave within the frame. If the radio chip only outputs hard bits, expect ≈ 3 dB instead; an RS(255,223)-shortened outer code (e.g. RS(96,64) shortened) on hard bits is then attractive because it is cheap and burst-tolerant.

### Example 5 — Coding rate vs sensitivity on an EBYTE-class LoRa module
Changing CR from 4/5 to 4/8 at SF12/125 kHz raises time-on-air by ≈ 60 % and does *not* change the datasheet demodulation SNR (−20 dB), but PER near sensitivity improves because more single-symbol errors are corrected; in pure noise the gain in energy terms is ≈ 0 (table above). Going from SF11 to SF12 instead also doubles air time but gains ≈ 2.5 dB of sensitivity — usually the better trade for range ([LoRa sensitivity](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md)).

## Practical notes
- **Soft bits from real radios.** Many ISM chips expose only hard bits; SDR receivers and some chips (via RSSI/discriminator output) can give soft values. Check before counting on soft-decision gain.
- **Termination / tail-biting.** A convolutional code must be terminated with $K-1$ zero bits (rate loss $(K-1)/k$ — 6 bits per 256-bit frame = 0.1 dB) or made tail-biting (no loss, more complex decoding).
- **Puncturing** raises the rate by deleting coded bits in a fixed pattern; the Viterbi decoder inserts zero-confidence (erasure) metrics. Rate ¾ K=7 still gives ≈ 3.5–4 dB at 1e-5 (CCSDS figure 4-10 curves; not re-simulated).
- **Randomise the data** (scrambler/whitening) before FEC so the symbol synchroniser sees transitions; CCSDS uses $x^{17}+x^{14}+1$ (legacy $x^8+x^7+x^5+x^3+1$) [2 §10].
- **Undetected errors.** A decoder that fails can output a *wrong* codeword; always validate with a CRC after decoding ([packet framing](packet-framing-protocols.md)). CCSDS notes RS with E = 16 has an extremely low undetected error rate, E = 8 "low enough for some applications" [2 §4].
- **Sync before decoding.** At the Eb/N0 where a strong code works (raw BER 1e-2–1e-1), the demodulator's carrier/timing loops and the frame synchroniser must still work; CCSDS notes some commercial Viterbi decoders' node synchronisation fails below ≈ 4 dB [3 §6].
- **Libraries:** Karn libfec (C, SIMD Viterbi for K=7/K=9, RS(255,223) with CCSDS dual-basis option); liquid-dsp `fec` module (Hamming(7,4)/(8,4)/(12,8), Golay(24,12), SEC-DED, conv & punctured conv, RS via libfec); GNU Radio `gr-fec` (CC encoder/decoder, polar, LDPC, tagged-stream and async variants); AFF3CT (C++ toolbox and simulator); Sionna (TensorFlow, 5G LDPC/polar); scikit-commpy (Python conv/Viterbi, LDPC).

## Common mistakes & misconceptions
- **Comparing coded and uncoded curves on Ec/N0 or SNR axes.** Always use Eb/N0 per *information* bit, or the rate loss is hidden.
- **Quoting coding gain without the BER.** The K=7 code gains 5.4 dB at 1e-5 but ≈ 3 dB at 1e-3 and 7 dB asymptotically.
- **"LoRa CR 4/8 doubles my range."** It corrects single-symbol errors; in white noise its net energy gain is ≈ 0 dB, and it costs 60 % air time.
- **Hard-slicing before the decoder** without realising it costs ≈ 2 dB.
- **No interleaver on a fading channel** — FEC designed for random errors fails on bursts; conversely, an interleaver longer than the allowed latency is useless.
- **Forgetting the CRC** after FEC: decoders produce undetected errors when overwhelmed.
- **Believing turbo/LDPC help 50-byte packets as much as 1-kB blocks.** Finite-length penalties dominate short blocks.
- **"TCM and BICM are the same thing."** TCM designs the code jointly with the constellation for Euclidean distance (best on AWGN); BICM separates them with a bit interleaver (slightly worse on AWGN, much better on fading, and one code for all QAM orders).
- **Counting LDPC iterations as a fixed cost.** With a syndrome check, decoding stops early at high SNR; the worst case (near threshold) sets the latency budget.
- **Feeding BP with LLRs of the wrong scale.** For BPSK the channel LLR is $2y/\sigma^2$; using raw y (or the wrong σ) degrades sum-product noticeably (min-sum is scale-invariant).
- **Mismatched puncturing/polynomial conventions** (octal 171/133 vs 133/171 order, CCSDS output inversion, bit ordering) — the most common reason a "standard" Viterbi decoder produces garbage against another implementation.

## How to simulate / verify
- **`tools/verify/comms_coding.py`** (≈ 2 min): K=7 (171,133) free distance and weight spectrum; soft/hard union bounds; Monte-Carlo soft/hard Viterbi; Hamming/extended-Hamming/LoRa-CR minimum distances; Hamming(7,4) syndrome correction; RS(255,223) alone and concatenated (Monte-Carlo Viterbi byte errors); block-interleaver burst check; Hamming(7,4)/Golay hard gains; asymptotic gain; RS burst length. All PASS.
- **`tools/verify/comms_lora_cr.py`** (≈ 6 s): idealised LoRa CR 4/5…4/8 PER model at SF7 and SF12.
- **`tools/verify/s8_info_coding.py`** (≈ 10 s, 16/16 PASS): 8-PSK TCM free distance by parity-check search (4- and 8-state), BICM vs CM capacity, and a random (3,6)-regular LDPC (n = 1008) with sum-product decoding at 1.5/2.0/2.5 dB.
- **GNU Radio:** `gr-fec` *FEC Extended Encoder/Decoder* with CC (K=7), polar or LDPC definitions; *BER* measurement with a known PRBS; for LoRa, `gr-lora_sdr` (EPFL) implements the Hamming/interleaver chain [14].
- **Checklist when your decoder "doesn't work":** polynomial order and inversion, bit order (MSB/LSB first), puncture pattern phase, soft-bit sign convention (+ = 0?), traceback depth, termination.

## Open questions / gaps
- Turbo and CCSDS LDPC numbers are quoted from CCSDS documents, not re-simulated. A generic (3,6)-regular LDPC with BP is now simulated (`s8_info_coding.py`); the CCSDS AR4JA codes themselves are not. The random code's rate is nominally ½ (dependent rows of H, if any, raise it slightly).
- TCM gains are verified only as asymptotic $d^2_\text{free}$ values; no TCM BER simulation was run.
- The LoRa CR model ignores soft decoding (possible on SDR receivers), the header's fixed CR 4/8, low-data-rate optimisation (SF−2 bits per symbol) and real interference statistics; domain 15 should cross-check against published PER measurements.
- Rocket-spin burst statistics (null duration, rate) are illustrative; no measured data found.

## Sources
1. S. Lin and D. J. Costello Jr., *Error Control Coding*, 2nd ed., Pearson Prentice Hall, 2004 — linear block codes, BCH (ch. 6), RS (ch. 7), convolutional codes and Viterbi (ch. 11–12), turbo (ch. 16), LDPC (ch. 17), coding gain. (textbook)
2. CCSDS 131.0-B-5, *TM Synchronization and Channel Coding* (Blue Book), Sept. 2023 — §3 convolutional K=7 r=½ G1=171/G2=133 octal, puncturing 2/3–7/8, ≥ 3-bit soft (§3.2.4); §4 RS(255,223)/(255,239), F(x)=x⁸+x⁷+x²+x+1, I = 1–5, 8; §6 turbo; §7 LDPC; §10 pseudo-randomiser. https://ccsds.org/Pubs/131x0b5.pdf (standard)
3. CCSDS 130.1-G-3, *TM Synchronization and Channel Coding — Summary of Concept and Rationale* (Green Book), June 2020 — §3.3 capacity limits and code comparison (conv ≈ 5.5 dB gain, +2.0 dB with RS, turbo within ≈ 1 dB), §4 quantisation (hard > 2 dB loss, 8-bit < 0.2 dB), d_free = 10, §6 Viterbi node-sync limitation, §7 turbo codes within ≈ 0.8 dB at 1e-6. https://ccsds.org/Pubs/130x1g3e1.pdf (standard, informative)
4. R. W. Hamming, "Error detecting and error correcting codes," *Bell System Technical Journal* 29(2):147–160, 1950. (peer-reviewed, primary)
5. R. C. Bose and D. K. Ray-Chaudhuri, "On a class of error correcting binary group codes," *Information and Control* 3(1):68–79, 1960; A. Hocquenghem, "Codes correcteurs d'erreurs," *Chiffres* 2:147–156, 1959. (peer-reviewed)
6. I. S. Reed and G. Solomon, "Polynomial codes over certain finite fields," *J. SIAM* 8(2):300–304, 1960. (peer-reviewed, primary)
7. A. J. Viterbi, "Error bounds for convolutional codes and an asymptotically optimum decoding algorithm," *IEEE Trans. Inf. Theory* IT-13(2):260–269, 1967. (peer-reviewed, primary)
8. G. D. Forney Jr., "The Viterbi algorithm," *Proc. IEEE* 61(3):268–278, 1973; and *Concatenated Codes*, MIT Press, 1966. (peer-reviewed)
9. C. Berrou, A. Glavieux, P. Thitimajshima, "Near Shannon limit error-correcting coding and decoding: Turbo-codes," *Proc. IEEE ICC* 1993, pp. 1064–1070. (peer-reviewed)
10. R. G. Gallager, "Low-density parity-check codes," *IRE Trans. Inf. Theory* IT-8(1):21–28, 1962; D. J. C. MacKay and R. M. Neal, "Near Shannon limit performance of low density parity check codes," *Electronics Letters* 32(18):1645, 1996. (peer-reviewed)
11. 3GPP TS 38.212, *NR; Multiplexing and channel coding* — LDPC for data channels, polar codes for control. (standard)
12. E. Arıkan, "Channel polarization: a method for constructing capacity-achieving codes for symmetric binary-input memoryless channels," *IEEE Trans. Inf. Theory* 55(7):3051–3073, 2009. (peer-reviewed)
13. M. Knight and B. Seeber, "Decoding LoRa: realizing a modern LPWAN with SDR," *Proc. GNU Radio Conference* 1(1), 2016 — Hamming codes, diagonal interleaver, Gray mapping, whitening in LoRa. (conference paper)
14. J. Tapparel, O. Afisiadis, P. Mayoraz, A. Balatsoukas-Stimming, A. Burg, "An open-source LoRa physical layer prototype on GNU Radio," *IEEE SPAWC* 2020 (arXiv:2002.08208) — gr-lora_sdr implementation of the full coding chain. (peer-reviewed)
15. P. Karn, *libfec* (Viterbi and Reed–Solomon library, KA9Q), https://github.com/quiet/libfec (mirror); J. Gaeddert, *liquid-dsp* `fec` module documentation, https://liquidsdr.org (software documentation)
16. G. Ungerboeck, "Channel coding with multilevel/phase signals," *IEEE Trans. Inf. Theory* IT-28(1):55–67, 1982 — set partitioning, 4/8-state 8-PSK codes (3.0/3.6 dB). (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge, d²free re-derived in the script)
17. E. Zehavi, "8-PSK trellis codes for a Rayleigh channel," *IEEE Trans. Commun.* 40(5):873–884, 1992; G. Caire, G. Taricco, E. Biglieri, "Bit-interleaved coded modulation," *IEEE Trans. Inf. Theory* 44(3):927–946, 1998. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
18. T. Richardson, R. Urbanke, *Modern Coding Theory*, Cambridge 2008 — Tanner graphs, sum-product/min-sum, density evolution, (3,6) threshold. (textbook; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
19. J. G. Proakis, M. Salehi, *Digital Communications*, 5th ed., 2008, chs. 7–8 (TCM, LDPC and iterative decoding). (textbook)
20. Verification: `tools/verify/s8_info_coding.py` (W5-S8). (numerical check)
