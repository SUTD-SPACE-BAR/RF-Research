---
title: Packet framing and link protocols — preambles, sync words, CRC, whitening, ARQ vs FEC
domain: 10-comms-modulation
slug: packet-framing-protocols
tags: [packet, frame, preamble, sync-word, access-code, header, CRC, polynomial, Hamming-distance, whitening, scrambling, PN9, ARQ, HARQ, FEC, erasure-coding, PER, telemetry, CCSDS, space-packet, COBS]
prerequisites:
  - ber-ebn0-and-shannon.md
  - channel-coding-fec.md
  - synchronization-carrier-timing.md
related:
  - matched-filter-detection.md
  - modulation-choice-guide.md
  - digital-modulation-psk-qam-fsk.md
  - ../15-lora-ism-radios/rocket-telemetry-radio-design.md
  - ../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md
  - ../15-lora-ism-radios/ground-station-design.md
  - ../20-projects-recipes/lora-rocket-telemetry-link.md
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Packet framing and link protocols — preambles, sync words, CRC, whitening, ARQ vs FEC

## Questions this page answers
- What goes into a radio packet, and why each part?
- How long should my preamble be, and what makes a good sync word?
- How do I set the sync-word error tolerance for a given false-alarm rate?
- Which CRC polynomial should I use, what does "HD = 4 up to 32 751 bits" mean, and what is the chance a corrupted frame passes the CRC?
- Why do FSK radios "whiten" data, and how does PN9 whitening work?
- How does packet error rate relate to bit error rate, and what frame length maximises throughput?
- When should I use ARQ (retransmission) versus FEC — and what can a downlink-only rocket link do instead of ARQ?
- How should I design a rocket telemetry frame (headers, counters, versions), and what can I borrow from CCSDS?

## TL;DR
- Typical frame: **preamble** (receiver AGC/timing/frequency acquisition) → **sync word** (frame alignment) → **header** (length, type, version, source, sequence number — protect it) → **payload** → **CRC** → optional FEC/interleaving around it all, with **whitening** so the bit stream has transitions and no spectral lines.
- **PER ≈ 1 − (1 − p)^N** for $N$ bits with independent errors: at BER 1e-4, 64/256/1024/4096-bit frames lose 0.6/2.5/9.7/34 % (verified).
- **Sync-word threshold** (32-bit word, accept ≤ E errors): false alarm per position 2.3e-10 (E = 0), 1.2e-7 (E = 2), **1.28e-6 (E = 3)**, 9.7e-6 (E = 4); miss at channel BER 1e-2: 27 %, 0.4 %, **0.029 %**, 0.0016 %. E ≈ 2–4 is the usual compromise; the CRC catches the false alarms.
- **CRC:** detects all bursts ≤ r bits, all odd-weight errors if $(x+1)$ divides $g(x)$, and all errors of weight < HD up to a length limit. CRC-16/CCITT (0x1021) has **HD = 4 up to 32 751 data bits** (verified from the order of $x$; matches Koopman). For a badly corrupted frame, undetected probability ≈ $2^{-r}$: 3.9e-3 (CRC-8, verified), 1.5e-5 (CRC-16), 2.3e-10 (CRC-32). Use Koopman's tables to pick polynomials for your length [1], [2].
- **Know your CRC parameters**: width, polynomial, init, reflect-in/out, xor-out. Check values for "123456789": CRC-16/CCITT-FALSE 0x29B1, CRC-16/ARC 0xBB3D, CRC-16/KERMIT 0x2189, CRC-32 0xCBF43926, CRC-32C 0xE3069283 (all verified).
- **Whitening:** XOR with a PN sequence (PN9 $x^9+x^5+1$ in many ISM chips; CCSDS $x^{17}+x^{14}+1$). An all-zeros payload becomes a stream with no run longer than 9 bits (verified).
- **Optimal payload length** for throughput with $H$ overhead bits at BER $p$: $L^*=-\tfrac H2+\sqrt{\tfrac{H^2}4-\tfrac{H}{\ln(1-p)}}\approx\sqrt{H/p}$ (855 bits for H = 80, p = 1e-4; verified).
- **Downlink-only rocket links can't use ARQ.** Use FEC inside frames and *erasure coding across frames*: a systematic (10, 8) code cuts residual frame loss from 10 % to 2.3 % at 25 % overhead (verified); repeat critical event frames (apogee, deploy) several times.
- **CRC ≠ correctness of meaning:** a stale protocol definition on one end yields "plausible garbage that passes CRC" (Space Bar flight-software lesson) — version every wire format.

## Intuition (no math)
A receiver listening to noise has to answer, continuously: *Is there a packet? Where does it start? Is it intact? What is it?* Each part of a frame answers one question.

- The **preamble** is a known, repetitive pattern (1010… for FSK, repeated chirps for LoRa, training symbols for OFDM). It gives the automatic gain control time to settle, and the frequency and timing loops something easy to lock to.
- The **sync word** (access code) is a specific bit pattern that is unlikely to appear by chance and unlike shifted copies of itself. When the receiver's correlator sees it, it knows exactly where the payload begins. Allowing a couple of bit errors in it makes detection robust at low SNR, at the cost of more false triggers on noise.
- The **header** says how long the frame is and what it contains. If the length field is corrupted, the receiver reads the wrong number of bytes — so headers are often separately protected.
- The **CRC** is a checksum computed by polynomial division: if the frame changes, the remainder almost certainly changes. It *detects*; it doesn't correct.
- **Whitening** scrambles the bits with a known pseudo-random pattern so that long runs of 0s or 1s (common in telemetry — zeros in unused fields) don't starve the receiver's clock recovery or create DC offsets and spectral spikes.

Then you decide what to do about errors: **retransmit** (ARQ) — requires a return channel and time; or **correct** (FEC) — costs bandwidth all the time. A rocket downlink without an uplink must rely on FEC, repetition and redundancy across packets.

## The math

### Level 1 — frame efficiency, airtime and PER
Frame fields (bits): preamble $P$, sync $S$, header $H_d$, payload $L$, CRC $r$; FEC rate $R_c$. Airtime at bit rate $R_b$ (on air):
$$T_{frame}=\frac{P+S+(H_d+L+r)/R_c}{R_b},\qquad \eta_{frame}=\frac{L}{P+S+(H_d+L+r)/R_c}.$$
Packet error rate for independent bit errors with probability $p$ over the $N$ protected bits:
$$\mathrm{PER}=1-(1-p)^N\approx Np\quad(Np\ll1).$$
(With FEC, use the *decoded* word error rate instead; bit errors after a Viterbi decoder are bursty, so the independence formula underestimates correlated losses — see [channel coding](channel-coding-fec.md).)

### Level 2 — each component
**Preamble length.** Long enough for the receiver's AGC to settle, carrier/frequency estimation to reach the needed accuracy (error ∝ $N^{-3/2}$ — [synchronisation](synchronization-carrier-timing.md)), and timing recovery to converge; plus the receiver's duty-cycled wake-up interval if it sleeps. ISM FSK chips typically need 16–64 bits; LoRa uses a programmable number of up-chirps (8 by default in Semtech chips — domain 15); 802.11a uses 16 µs of short + long training symbols.

**Sync-word detection.** Hard-decision rule: accept at position $k$ if the Hamming distance between the received $N$ bits and the sync word is ≤ E. For random data (no packet) each position is a false alarm with
$$P_{FA}=2^{-N}\sum_{i=0}^{E}\binom Ni,$$
and a genuine word at channel BER $p$ is missed with
$$P_{miss}=1-\sum_{i=0}^{E}\binom Nip^i(1-p)^{N-i}.$$
Table in the TL;DR (verified). Soft correlation ([matched filter](matched-filter-detection.md)) is ≈ 2 dB better than hard; Massey's rule gives the optimum [3]. Good words have low autocorrelation sidelobes (so partial overlaps with the preamble don't trigger) and low correlation with the preamble pattern; examples: CCSDS ASM 0x1ACFFC1D (32 bits) [4], Barker-13 for short codes, and chip-vendor defaults (commonly cited: 0xD391 for TI CC1101, 0x2DD4 for Si443x-family radios — unverified here, check the datasheet; change it from the default to avoid decoding strangers' traffic).

**CRC mathematics.** Treat the $k$-bit message as a polynomial $m(x)$ over GF(2). With generator $g(x)$ of degree $r$, transmit $c(x)=m(x)x^r+\big(m(x)x^r\bmod g(x)\big)$ — divisible by $g(x)$. An error pattern $e(x)$ goes undetected iff $g(x)\mid e(x)$ [5]. Consequences:
- $g$ has ≥ 2 terms → all single-bit errors detected.
- $(x+1)\mid g$ → all odd-weight errors detected (CRC-16/CCITT = $(x+1)\times$ a primitive degree-15 polynomial — verified).
- Two-bit errors $x^i(x^j+1)$ undetected only if $g$'s primitive factor divides $x^j+1$, i.e. $j$ is a multiple of the order of $x$ (32 767 for CCITT-16) → **HD ≥ 4 for codewords up to 32 767 bits** (32 751 data bits) — exactly Koopman's tabulated value for 0x8810 (Koopman notation of 0x1021) [1].
- All bursts of length ≤ $r$ detected; longer bursts pass with probability ≈ $2^{-(r-1)}$ (length $r+1$) or $2^{-r}$.
- For a frame so corrupted that it is effectively random, $P_{undetected}\approx2^{-r}$ (verified for CRC-8 by Monte-Carlo). The probability a *random-error* frame passes is much lower when few bits are wrong, because all errors below HD are caught.

Koopman's CRC Zoo lists "best" polynomials by width, HD and data length; e.g. 16-bit 0xd175 (Koopman notation) keeps HD = 4 to 32 751 bits and HD = 6 to 93 bits, and 0xac9a gives HD = 5 up to 241 bits — better than CCITT for short telemetry frames [1], [2]. **The polynomial alone does not define a CRC**: initial value, bit reflection and final XOR differ between "CRC-16" variants — always test against a check value.

**Whitening / scrambling.** XOR the payload (after the sync word) with a PN sequence starting from a known seed at each frame (additive scrambler, no error propagation). PN9 ($x^9+x^5+1$, period 511, 256 ones) in many ISM chips; CCSDS uses $x^{17}+x^{14}+1$ (period 131 071), with a legacy $x^8+x^7+x^5+x^3+1$ (255) that can create spectral lines at 1/255 of the symbol rate [4]. Purposes: guarantee transitions for timing recovery, DC balance for discriminator/AC-coupled receivers, and a smooth spectrum (regulatory masks, no tones). A *self-synchronising* scrambler (multiplicative, e.g. in 802.11b) needs no seed alignment but multiplies errors.

**Byte-stream framing on wires** (MCU ↔ radio module, flight processor ↔ coprocessor UART): use a framing scheme that can resynchronise after a dropped byte — COBS (consistent overhead byte stuffing, ≤ 1 byte per 254 overhead) or SLIP/HDLC byte stuffing, plus a CRC [6].

### Level 3 — throughput, ARQ, HARQ and erasure coding
**Optimal frame length.** With $H$ overhead bits per frame and BER $p$, throughput per transmitted bit is $\eta(L)=\frac{L}{L+H}(1-p)^{L+H}$. Setting $d\eta/dL=0$: $L^2+HL+H/\ln(1-p)=0$, so
$$L^*=-\frac H2+\sqrt{\frac{H^2}{4}-\frac{H}{\ln(1-p)}}\approx\sqrt{H/p}\ \ (p\ll1).$$
H = 80, p = 1e-4 → $L^*=855$ bits (107 bytes), peak η = 0.83 (verified). Too-short frames waste overhead; too-long frames are lost too often. In fading channels the optimum shifts shorter (frames should be ≪ the fade duration or ≫ it with interleaving).

**ARQ.** Stop-and-wait: send, wait for ACK; efficiency $(1-\mathrm{PER})T_f/(T_f+T_{ack}+2T_{prop})$ (0.75 for 50 ms frames, 10 ms ACK, 10 % PER). Go-back-N and selective repeat keep the pipe full. Expected transmissions per frame $1/(1-\mathrm{PER})$ [7]. **Hybrid ARQ**: type I = FEC + ARQ on failure; type II/incremental redundancy = send extra parity only when needed; chase combining = soft-combine repeats (used in LTE/5G).

**Downlink-only links** (Space Bar's rocket telemetry is deliberately half-duplex downlink-only — no ground→rocket commands [8]): no ARQ, so
- FEC within frames (conv/RS/LDPC) for random errors;
- **erasure coding across frames** for lost frames: send $k$ data frames plus $n-k$ parity frames computed byte-wise by a systematic MDS (RS) code, or use fountain/Raptor codes (RFC 6330). With a (10, 8) code and 10 % independent frame loss, a block fails to decode 7.0 % of the time, but since received data frames are still usable, the residual data-frame loss drops to **2.3 %** (vs 10 %) for 25 % overhead (verified);
- **repetition of critical events** (launch detect, apogee, deployment, pyro continuity changes) in several subsequent frames;
- **deterministic decimation** of high-rate sensor data to fit the air rate (budget against the *on-air* bit rate, not the UART rate) [8].

**CCSDS as a template.** A CCSDS Space Packet has a 6-octet primary header: version (3 bits), type (1), secondary-header flag (1), APID (11 bits — identifies the data source/type), sequence flags (2), sequence count (14 bits), data length (16 bits, = data-field octets − 1); data field 1–65 536 octets [9]. The TM Transfer Frame wraps packets with spacecraft/virtual-channel IDs, frame counters and an optional 16-bit Frame Error Control Field (CRC), and the sync-and-coding sublayer adds the ASM, randomiser and FEC [4], [10]. A "CCSDS-lite" rocket frame can borrow: an APID-like source/type field, per-type sequence counters (loss accounting), a length field, a version field, and a CRC — without the full stack.

## Design equations & rules of thumb

| Equation / rule | When valid | Typical values |
|---|---|---|
| PER = $1-(1-p)^N$ | independent errors | 256 bits @ 1e-4 → 2.5 % |
| $P_{FA}=2^{-N}\sum_{i\le E}\binom Ni$ per position | random data | 32-bit, E = 3: 1.28e-6 |
| $P_{miss}=1-\sum_{i\le E}\binom Nip^i(1-p)^{N-i}$ | channel BER p | E = 3, 1e-2: 2.9e-4 |
| CRC undetected ≈ $2^{-r}$ (heavy corruption) | random garbage model | CRC-16: 1.5e-5 |
| HD ≥ 4 up to (order of $x$) − r data bits | $g=(x+1)p(x)$, $p$ primitive | CCITT-16: 32 751 |
| $L^*\approx\sqrt{H/p}$ | throughput-optimal payload | H = 80, 1e-4: ≈ 855–894 bits |
| ARQ transmissions $1/(1-\mathrm{PER})$ | independent losses | PER 10 % → 1.11 |
| (n,k) erasure code recovers any $n-k$ lost frames | MDS/RS across frames | (10,8): 10 % → 2.3 % residual |
| Preamble ≥ AGC + CFO + timing acquisition time | burst receivers | 16–64 bits FSK |

## Worked examples

### Example 1 — Frame budget for a 10 kb/s telemetry downlink
Preamble 32 bits, sync 32 bits, header 4 bytes (version 4 b, type 4 b, source 8 b, sequence 16 b… plus length 8 b), payload 20 bytes, CRC-16: total $32+32+40+160+16=280$ bits → 28.0 ms airtime, η = 160/280 = 57 %, maximum 35.7 frames/s. At BER 1e-4 (on the 216 CRC-protected bits) PER = 2.1 %. Doubling the payload to 40 bytes raises η to 73 % and PER to 3.7 % — net useful throughput goes from 5.59 to 7.00 kb/s.

### Example 2 — Sync-word threshold
32-bit sync word, 10 kb/s: the correlator tests $10^4$ positions per second. With E = 3, false triggers occur at $1.28\times10^{-6}\times10^4=0.013$ per second (≈ one every 78 s), each rejected by the CRC after reading one frame length — harmless. Miss probability at a channel BER of 1e-2 (near sensitivity for an FEC-protected link) is 2.9e-4, far below the payload PER. With E = 0 the miss probability would be 27 % — a common cause of "range is much worse than the link budget says".

### Example 3 — Choosing a CRC for 32-byte frames
Data length ≈ 256 bits. CRC-16/CCITT: HD = 4 (detects all 1-, 2-, 3-bit errors). Koopman's 0xac9a (Koopman notation) gives HD = 5 up to 241 bits — slightly too short; 0xd175 gives HD = 4 (and HD = 6 only to 93 bits). For HD ≥ 5 at 256 bits use a 16-bit polynomial from the zoo's HD = 5 column for ≥ 256 bits or step up to a 24/32-bit CRC (CRC-32: HD = 6 up to 268 bits per Koopman's 32-bit analysis — cited, not re-verified). What matters most: *consistently* implement the same parameters at both ends and log the check value in your protocol document.

### Example 4 — Erasure coding across frames for the rocket downlink
Measured frame loss during ascent 10 % (fades from vehicle roll). Add 2 parity frames per 8 data frames (RS over bytes, frame-aligned): residual data-frame loss 2.3 % for 25 % more airtime. Alternatively repeat every frame twice (100 % overhead) → residual 1 % if losses are independent, but much worse if losses come in bursts longer than the frame spacing — interleave the parity frames in time so a single fade doesn't take out both a data frame and its protection.

### Example 5 — Optimal payload at a poor BER
Overhead H = 112 bits (preamble + sync + header + CRC), BER 1e-3 (edge of coverage, uncoded): $L^*\approx\sqrt{112/10^{-3}}\approx335$ bits; exact formula gives ≈ 283 bits (≈ 35 bytes), peak throughput ≈ 48 % of the air rate. At BER 1e-5 the optimum grows to ≈ 3.3 kbit — so adaptive frame length (or FEC) pays off when the link varies widely.

## Practical notes
- **Protect the length field** (duplicate it, give the header its own CRC, or use fixed-length frames); a corrupted length can make the receiver swallow the next frame's preamble.
- **Sequence counters per packet type + a source ID** make loss accounting unambiguous (which frames were missed, from which flight computer) — use them to measure PER in flight and on the bench [8].
- **Version the wire format** and generate all parsers from one definition; a mismatched mirror "passes CRC" while decoding garbage [8].
- **Time-tag** frames (GNSS time or a monotonic counter) so the ground station can reconstruct timing despite decimation and losses.
- **Endianness and bit order** (MSB-first on air vs little-endian structs) must be written down; CRCs often hide byte-order bugs until a length changes.
- **Transparent-mode modules** (EBYTE E22/E220) packetise the UART stream themselves: your frames may be split or merged across air packets; put your own sync/CRC inside and size writes to the module's packet length (domain 15).
- **Hardware CRC and whitening** in radio chips are convenient but inflexible; if you need a specific polynomial or HD, disable them and do it in software.

## Common mistakes & misconceptions
- **"CRC-16" as a complete specification.** There are dozens of CRC-16 variants; the polynomial, init, reflection and xor-out must all match.
- **Believing a CRC pass means the data is correct.** It means the bits probably weren't corrupted in transit; semantic mismatches (protocol versions, byte order) pass CRC.
- **Using PER = N·p at high BER** — use $1-(1-p)^N$; and remember errors after FEC are bursty.
- **Zero-tolerance sync-word matching** at low SNR, losing packets that would have decoded.
- **No whitening on FSK** with telemetry full of zeros → DC drift, lost bit sync, spectral lines.
- **Budgeting telemetry against the UART baud rate** instead of the on-air rate after preamble, sync, header, CRC and FEC.
- **Retransmission schemes on a half-duplex downlink-only design** — there is no return path; design for loss instead.

## How to simulate / verify
- **`tools/verify/comms_crc_framing.py`** (≈ 2 s): six CRC check values; CCITT-16 structure, order of $x$ (32 767) and HD-4 length (32 751); burst and odd-weight detection; CRC-8 undetected fraction ≈ $2^{-8}$; PER formula vs Monte-Carlo; sync-word $P_{FA}$/$P_{miss}$ table; PN9 period/balance/run length; ARQ numbers; optimal frame length; (10,8) erasure coding. All PASS.
- **CRC catalogues:** Greg Cook's "Catalogue of parametrised CRC algorithms" (reveng) lists width/poly/init/refin/refout/xorout/check for hundreds of CRCs [11]; Koopman's zoo for polynomial *quality* [1].
- **Bench PER measurement:** transmit N numbered frames at a fixed level; count missing sequence numbers and CRC failures separately; sweep attenuation to build PER vs received power; compare with PER from BER using the formula above.

## Open questions / gaps
- Vendor default sync words, preamble lengths and hardware CRC/whitening polynomials per chip (SX126x FSK, CC1101, Si446x, SX127x LoRa header CRC) should be tabulated in domain 15/18; only PN9 and CCITT-16 behaviour were verified here.
- CRC-32 HD-vs-length values are quoted from Koopman's published analysis, not recomputed (weight-5/6 searches are expensive).
- Measured frame-loss statistics for spinning rockets (burst lengths) are not available; Example 4 is illustrative.

## Sources
1. P. Koopman, *CRC Polynomial Zoo* (Carnegie Mellon University), https://users.ece.cmu.edu/~koopman/crc/ and 16-bit table https://users.ece.cmu.edu/~koopman/crc/crc16.html — implicit-+1 notation; 0x8810 (CCITT) and 0xc002 (IBM) HD = 4 to 32 751 bits; 0xd175 HD = 4 to 32 751, HD = 6 to 93; 0xac9a HD = 5 to 241. (academic web resource)
2. P. Koopman and T. Chakravarty, "Cyclic redundancy code (CRC) polynomial selection for embedded networks," *Proc. IEEE/IFIP DSN* 2004, pp. 145–154. (peer-reviewed)
3. J. L. Massey, "Optimum frame synchronization," *IEEE Trans. Communications* 20(2):115–119, 1972. (peer-reviewed)
4. CCSDS 131.0-B-5, *TM Synchronization and Channel Coding*, Sept. 2023 — §9 ASM (1ACFFC1D, 034776C7272895B0), §10 pseudo-randomiser ($x^{17}+x^{14}+1$; legacy $x^8+x^7+x^5+x^3+1$ with 1/255 spectral-line warning). https://ccsds.org/Pubs/131x0b5.pdf (standard)
5. W. W. Peterson and D. T. Brown, "Cyclic codes for error detection," *Proc. IRE* 49(1):228–235, 1961. (peer-reviewed, primary)
6. S. Cheshire and M. Baker, "Consistent overhead byte stuffing," *IEEE/ACM Trans. Networking* 7(2):159–169, 1999. (peer-reviewed)
7. S. Lin, D. J. Costello Jr., M. J. Miller, "Automatic-repeat-request error-control schemes," *IEEE Communications Magazine* 22(12):5–17, 1984. (peer-reviewed)
8. Space Bar avionics knowledge base, "Flight software architecture & lessons (Avionics B)", `~/.claude/knowledge/space-bar-avionics/flight-software-lessons.md` — downlink-only half-duplex telemetry, deterministic decimation against air rate, one-source-of-truth wire protocol with version and per-type sequence counters. (internal project notes)
9. CCSDS 133.0-B-2, *Space Packet Protocol* (Blue Book), June 2020 — §4.1 packet structure: 6-octet primary header (3-bit version, type, secondary-header flag, 11-bit APID, 2-bit sequence flags, 14-bit sequence count, 16-bit data length), data field 1–65 536 octets. https://ccsds.org/Pubs/133x0b2e2.pdf (standard)
10. CCSDS 132.0-B-3, *TM Space Data Link Protocol* — transfer frame header, frame error control field (CRC-16). (standard)
11. G. Cook, "Catalogue of parametrised CRC algorithms" (CRC RevEng), https://reveng.sourceforge.io/crc-catalogue/ — check values used above. (reference catalogue)
12. M. Luby et al., RFC 6330, *RaptorQ Forward Error Correction Scheme for Object Delivery*, IETF, 2011. (standard)
