---
title: Choosing a modulation and coding scheme — a decision guide
domain: 10-comms-modulation
slug: modulation-choice-guide
tags: [modulation-choice, image-transfer, codec2, bulk-data, design-guide, LoRa, GFSK, GMSK, BPSK, QPSK, FEC, OFDM, trade-off, link-budget, Doppler, PAPR, spectral-efficiency, rocket-telemetry]
prerequisites:
  - ber-ebn0-and-shannon.md
  - digital-modulation-psk-qam-fsk.md
  - channel-coding-fec.md
related:
  - spread-spectrum-dsss-fhss-css.md
  - ofdm.md
  - synchronization-carrier-timing.md
  - packet-framing-protocols.md
  - pulse-shaping-isi.md
  - analog-modulation-am-fm-pm-ssb.md
  - ../09-propagation-link-budget/link-budget-methodology.md
  - ../15-lora-ism-radios/rocket-telemetry-radio-design.md
  - ../15-lora-ism-radios/other-ism-radios-fsk-2g4.md
  - ../19-regulations-safety/spectrum-allocation-ism-bands.md
  - ../20-projects-recipes/lora-rocket-telemetry-link.md
level: intermediate
confidence: medium
last_updated: 2026-10-14
---

# Choosing a modulation and coding scheme — a decision guide

## Questions this page answers
- For a given range, data rate, power and bandwidth, which modulation and FEC should I use?
- How do LoRa, GFSK, BPSK+FEC, QPSK+LDPC and OFDM compare in required Eb/N0, bandwidth and hardware complexity?
- Is LoRa actually more sensitive than FSK or PSK *at the same data rate*, or only because it is slower?
- What changes for a fast rocket (Doppler, antenna nulls, near-pad dynamic range)?
- When is a coherent PSK design worth the extra receiver complexity?
- When is OFDM or high-order QAM justified?
- What should I pick for a custom 433/915 MHz telemetry radio, and for a video downlink?
- Which modulation should I use to send a camera image or voice from a rocket, and how long will it take?

## TL;DR
- **First identify the limiting resource.** Power/range-limited (η ≪ 1 b/s/Hz: rockets at range, LoRa, deep space) → low-order modulation + strong FEC or orthogonal signalling. Bandwidth-limited (η > 1: video, Wi-Fi) → QAM/OFDM with coding. Complexity/cost-limited → an off-the-shelf GFSK or LoRa chip.
- **At equal information rate, what matters is required Eb/N0 (incl. implementation loss) and PA back-off.** Illustrative table (AWGN, 1e-5 BER or ≈ 1 % PER, `tools/verify/comms_choice_guide.py`):

  | Scheme | Eb/N0 req. (incl. ≈ 2 dB impl.) | RF BW at 10 kb/s | η (b/s/Hz) | PAPR / back-off | Rel. range at 10 kb/s* |
  |---|---|---|---|---|---|
  | Non-coherent GFSK, h = 1 | ≈ 15.3 dB | 20 kHz | 0.5 | 0 dB | 1.00 |
  | GMSK BT 0.5, coherent/sequence det. (est.) | ≈ 12.6 dB | 10.3 kHz | 0.97 | 0 dB | 1.37 |
  | BPSK uncoded, RRC 0.35 | ≈ 11.6 dB | 13.5 kHz | 0.74 | 3.8 dB | 1.00 |
  | BPSK + K=7 r½ soft Viterbi | ≈ 6.2 dB | 27 kHz | 0.37 | 3.8 dB | 1.86 |
  | BPSK + RS(255,223) + K=7 | ≈ 4.2 dB | 31 kHz | 0.32 | 3.8 dB | 2.32 |
  | QPSK + short LDPC/polar r½ (est.) | ≈ 4.6 dB | 13.5 kHz | 0.74 | 3.8 dB | 2.23 |
  | 16-QAM uncoded | ≈ 15.4 dB | 3.4 kHz | 2.96 | 5.6 dB | 0.52 |
  | OFDM (64 sc) QPSK + K=7 r½ + CP | ≈ 7.1 dB | ≈ 13 kHz | 0.77 | 10.5 dB | 0.77 |
  | **LoRa** SF7 / SF12, 125 kHz, CR 4/5 | **≈ 6.1 / 6.3 dB** (datasheet, 1 % PER; SF12 with LDRO ≈ 7.1 dB) | 125 kHz | 0.044 / 0.0023 | 0 dB | (at 5.47 / 0.29 kb/s) |

  *Same 1 W PA (average power reduced by PAPR back-off), free space, equal antennas and margin; relative to NC-GFSK at 10 kb/s.
- **LoRa is not magic, but it is a very good engineering package**: at the same bit rate, LoRa SF7 (≈ 6.1 dB) matches coherent BPSK with a K=7 code (≈ 6.2 dB incl. 2 dB loss) *and* keeps a constant envelope (≈ 3.8 dB more average TX power than RRC-BPSK from the same PA), with no carrier-recovery loop, good offset tolerance and cheap modules. Its costs: very low η (125 kHz for ≤ 5.5 kb/s at SF7), long packets at high SF, and weak built-in coding.
- **Rocket-specific drivers:** frequency offset (crystal ≫ Doppler at UHF; Doppler *rate* matters at high SF / narrow loops), fades from roll and antenna nulls (→ interleaving + FEC + erasure coding across frames, ground diversity), huge dynamic range from pad to apogee (receiver overload near the pad), downlink-only (no ARQ).
- **Bulk data (images, voice) is limited by duty cycle and rate, not by modulation finesse** ([Example 6](#example-6--a-camera-image-and-voice-over-a-sub-ghz-link)). Under Singapore's licence-exempt rules a 600 kB image takes 51 min at 433 MHz on LoRa SF7/500 but 38 s with GFSK 250 kb/s at 866–869 MHz. Pick the fastest modulation the link margin allows, add packet-level erasure FEC, and send thumbnails in flight.
- **Default recommendations:** (1) *keep LoRa* for long-range low-rate telemetry (tune SF/BW to the data budget); (2) for a custom higher-rate link at 433/915 MHz, **GFSK (h ≈ 0.5–1, BT 0.5) + K=7 conv or short LDPC + CRC + whitening + interleaving** on a transceiver chip or SDR; (3) **coherent BPSK/QPSK + modern FEC** only if you control both ends with an SDR/FPGA and need the last 5–9 dB; (4) **OFDM/QAM only for high-rate video** in multipath, using COTS silicon.

## Intuition (no math)
Every scheme is a point on Shannon's plane of *energy per bit* vs *bits per hertz* ([BER page](ber-ebn0-and-shannon.md)). Moving left (less energy per bit) needs either more bandwidth per bit (orthogonal signalling like LoRa/M-FSK, low-rate codes) or smarter codes; moving up (more bits per hertz) costs energy (QAM). Then hardware realities shift the points: carrier recovery and linear PAs cost complexity and power; frequency offsets and fades cost margin; short packets cost coding gain.

For a rocket, the first-order question is almost never "which modulation has the best textbook curve" but "what data rate do I really need, and what does the channel do to me during boost?" Halving the data rate buys 3 dB — the same as a good chunk of coding gain — at zero complexity. The second question is "can my receiver keep lock?" — a scheme that is 2 dB better on paper but loses sync during a 20 g boost is worse.

## The math

### Level 1 — the comparison metric
For information rate $R_b$ and a required $(E_b/N_0)_{req}$ including implementation loss $L$,
$$P_{sens}=-174+\mathrm{NF}+10\log_{10}R_b+(E_b/N_0)_{req}\ \text{dBm},$$
and with a PA of saturated power $P_{sat}$ and signal PAPR (back-off) $B$, the usable average power is $P_{sat}-B$. The link margin difference between two schemes at the same $R_b$ is therefore
$$\Delta M=\big[(E_b/N_0)_{2}-(E_b/N_0)_{1}\big]+\big[B_2-B_1\big]\ \text{dB},$$
and in free space the range ratio is $10^{\Delta M/20}$. That single number, plus bandwidth, captures most of the trade.

### Level 2 — where the table's numbers come from
- **Uncoded curves** (BPSK 9.59 dB, NC-FSK 13.35 dB, 16-QAM 13.43 dB at 1e-5): derived and Monte-Carlo verified in `comms_ber_awgn.py`.
- **K=7 r½ soft Viterbi 4.17 dB; RS+K7 2.25 dB**: union bound + Monte-Carlo in `comms_coding.py`, matching CCSDS (5.5 dB and +2.0 dB gains) [1].
- **Short LDPC/polar r½, 256 information bits:** the finite-length normal approximation gives ≈ 1.6 dB at WER 1e-4; practical short codes sit ≈ 0.5–1.5 dB above it — the table assumes +1 dB (estimate, flagged).
- **GMSK coherent**: GMSK BT 0.5 with a good (coherent / Viterbi) detector is typically within ≈ 1 dB of BPSK (estimate from the ISI of the Gaussian filter; not simulated here).
- **LoRa**: SX127x datasheet demodulator SNR (−7.5 dB at SF7 … −20 dB at SF12 in 125 kHz) converted to Eb/N0 with CR 4/5 [2]; this already includes Semtech's implementation.
- **PAPR**: 1e-4 CCDF of RRC β = 0.35 QPSK (3.8 dB) and 16-QAM (5.6 dB) from `comms_modulation_spectra.py`; OFDM 10.5 dB at 1e-3 from `comms_ofdm.py`.
- **Implementation loss** 2 dB for home-built coherent receivers, 2 dB for NC-FSK; tune these to your measured numbers.

### Level 3 — factors the table does not capture
- **Frequency offset & dynamics** ([synchronisation](synchronization-carrier-timing.md)): NC-FSK and LoRa tolerate large static offsets (fractions of deviation / of BW); coherent PSK needs acquisition and a loop wide enough for the Doppler rate; OFDM tolerates only ≈ 1–2 % of its subcarrier spacing after correction.
- **Fading** ([BER page](ber-ebn0-and-shannon.md) Level 3): uncoded BER in Rayleigh fading needs ≈ 35 dB more than in AWGN; everything then hinges on interleaving + FEC depth relative to fade duration, and on diversity. This usually outweighs the few-dB differences in the table.
- **Short packets**: coding gains shrink ([channel coding](channel-coding-fec.md)); preamble/sync overhead grows ([packet framing](packet-framing-protocols.md)).
- **Interference**: narrowband schemes (GFSK at 20 kHz) suffer less from wideband noise sources but are hit fully by co-channel narrowband signals; LoRa/DSSS spread against narrowband interference ([spread spectrum](spread-spectrum-dsss-fhss-css.md)).
- **Regulation**: ISM bands limit power, duty cycle, dwell time and sometimes bandwidth or modulation class — e.g. AS923 rules in Singapore ([ISM bands](../19-regulations-safety/spectrum-allocation-ism-bands.md)). A scheme that needs 10× the airtime can violate duty-cycle limits.

## Design equations & rules of thumb

| Rule | Consequence |
|---|---|
| Halving $R_b$ = +3 dB margin = ×1.41 free-space range | always the cheapest "coding gain" |
| Coherent PSK vs NC-FSK ≈ 3.8 dB (uncoded) | needs carrier recovery |
| Soft-decision K=7 r½ ≈ 5.4 dB over uncoded BPSK at 1e-5 | doubles bandwidth |
| Soft vs hard decoding ≈ 2 dB | insist on soft bits |
| PA back-off ≈ PAPR: 0 (FSK/LoRa), ≈ 4 (RRC QPSK), ≈ 6 (16-QAM), ≈ 10 dB (OFDM) | constant envelope wins on power-limited links |
| η > 1 b/s/Hz ⇒ bandwidth-limited regime | QAM/OFDM territory |
| Oscillator ppm × f ≫ Doppler at UHF | budget offsets from crystals first |
| Fading margin ≫ modulation differences | spend effort on diversity/interleaving |

## Worked examples

### Example 1 — Is LoRa really better than a custom BPSK+FEC link?
Same 1 W PA, same antennas, target ≈ 5.5 kb/s. LoRa SF7/125 kHz: 6.1 dB Eb/N0, 0 dB back-off. Custom BPSK + K=7 soft Viterbi at 5.5 kb/s: 6.2 dB (with 2 dB implementation loss) and 3.8 dB RRC back-off (or ≈ 1 dB with unfiltered/lightly filtered BPSK, at the cost of spectral splatter). LoRa comes out ≈ 1–4 dB *better* in usable margin, with off-the-shelf hardware. A custom coherent design wins only with a stronger code (RS+K7 or LDPC: another 2 dB), careful implementation (< 1 dB loss), and a nonlinear-PA-friendly format (OQPSK/GMSK). Verdict: keep LoRa for the long-range, low-rate job; build custom only for higher rates or specific needs (ranging, soft-bit access, erasure coding).

### Example 2 — Higher-rate telemetry (50 kb/s) at 915 MHz
LoRa can't do 50 kb/s at useful sensitivity (SF7/500 kHz gives ≈ 21.9 kb/s). Options: GFSK h = 1 NC at 50 kb/s needs $-174+2+47+15.3=-109.7$ dBm; GMSK/coherent + K=7 r½ (≈ 6.2 dB, constant envelope with OQPSK/MSK-type modulation) needs −118.8 dBm — 9 dB better, ≈ ×2.9 free-space range, occupied bandwidth ≈ 100–120 kHz (100 kbaud coded, MSK-like). A transceiver chip that exposes soft bits, plus an MCU Viterbi decoder, gets most of that.

### Example 3 — A video downlink
2 Mb/s video from the vehicle to a ground station 5 km away in a cluttered area: bandwidth-limited and multipath-prone → OFDM (Wi-Fi-class COTS radios at 2.4/5.8 GHz) with FEC, or DVB-T/analog FM video (legacy). Budget the ≈ 10 dB OFDM PAPR in the PA and expect short range compared with telemetry — video and telemetry belong on separate links.

### Example 4 — A beacon for recovery after landing
After landing, range and battery life matter, data rate doesn't (GNSS position once a minute). LoRa SF12 (−141 dBm with a 2 dB NF ground receiver) or an APRS/amateur tracker if licensed. Do not use high-rate FSK: LoRa SF12's 293 b/s (nominal; 244 b/s with LDRO) gains ≈ 15 dB over 10 kb/s from the rate alone (3 dB per halving) plus ≈ 9 dB from its lower Eb/N0 requirement.

### Example 5 — Near-pad dynamic range
At 50 m from the pad a 1 W transmitter arrives at ≈ −30 dBm at 433 MHz (0 dBi each end, FSPL ≈ 59 dB) — 110 dB above LoRa sensitivity. Strong-signal effects (LNA/ADC overload, blocking of a second receiver in the same band) matter more than modulation. Put attenuators or AGC in the ground chain for pad operations, and frequency-separate the two flight computers' links (the 433/900 MHz split already does this).

### Example 6 — A camera image and voice over a sub-GHz link
**Requirement:** a 10 kB thumbnail in flight and the 600 kB full image if possible; downlink only; Singapore licence-exempt power and duty. **Method:** fragment into 200 B packets with an 8 B header, add rate-0.8 packet erasure FEC, and allow occupancy of min(duty, 0.7) (`tools/verify/s1_image_throughput.py`; full table on [other ISM radios § bulk data](../15-lora-ism-radios/other-ism-radios-fsk-2g4.md#bulk-data-images-and-voice)).
- **433 MHz, 10 mW e.r.p., 10 %**: LoRa SF7/500 gives 1.6 kb/s goodput, so the thumbnail takes 51 s and the full image 51 min. GFSK 250 kb/s takes 4 s and 4.4 min, but its free-space range at the legal power is 51 km (vs 270 km) and only 0.7 km landed.
- **866–869 MHz, 500 mW e.r.p., no duty stated**: SF7/500 gives 7 s and 7.3 min; GFSK 250 kb/s gives 0.6 s and 38 s with 180 km free-space range. This is the best licence-exempt band for images, but the band is "under review" ([19](../19-regulations-safety/singapore-imda-rules.md)).
- **917–925 MHz, 100 mW e.r.p., 1 %**: SF7/500 takes 8.5 min for the thumbnail and 8.5 h for the full image. It is impractical for images.

**Choice.** Above about 50 kb/s the [Example 2](#example-2--higher-rate-telemetry-50-kbs-at-915-mhz) logic applies: GFSK, or better coherent MSK-type modulation with K=7 FEC, gains 9 dB at equal rate. A soft-decision code inside each packet and an erasure code across packets are complementary, not alternatives. For voice, Codec2 at 700 b/s in 400 ms frames occupies 21 % of the air at LoRa SF7/125 and 5 % at SF7/500. Only the latter fits a 10 % duty limit, and a licensed handheld does the job better.

## Practical notes
- **Measure your own implementation loss** (bench BER/PER vs calibrated level) before trusting any comparison; home-built receivers often lose 3–5 dB at first.
- **Soft bits** are the single biggest free improvement for any FEC — pick hardware that provides them (SDR, or chips with soft outputs).
- **Keep formats boring on the rocket**: constant-envelope modulation, robust sync words, CRC, whitening, interleaving, and frame counters. Complexity belongs on the ground station (diversity combining, soft decoding, SDR logging).
- **Regulatory fit** often decides between otherwise equal options (duty cycle, bandwidth, hopping requirements).

## Common mistakes & misconceptions
- **Comparing schemes by datasheet sensitivity at different data rates** — convert to Eb/N0 (or compare at equal rate) first.
- **Ignoring PA back-off** when comparing constant-envelope and linear modulations.
- **Choosing the modulation before the data budget** — a lower data rate often beats a fancier modulation.
- **Optimising AWGN dB while ignoring fading, Doppler and sync** — on a rocket those dominate.
- **Streaming images over LoRa under a duty-cycle limit** — the duty cycle, not the modulation, sets the hours; see Example 6.
- **Assuming COTS OFDM/Wi-Fi works at long range** — even its lowest rate (≈ 6 Mb/s, typical sensitivity ≈ −90 dBm) is ≈ 45 dB less sensitive than LoRa SF12, mostly because of the 20 000× higher rate; and its ARQ/association assumptions break on a one-way link.

## How to simulate / verify
- **`tools/verify/comms_choice_guide.py`** (< 1 s): regenerates the comparison table, sensitivities (NF 2 dB), free-space relative ranges at 433 MHz with PA back-off, and the equal-rate LoRa vs BPSK+K7 comparison; spot checks PASS. Inputs come from the other `comms_*.py` scripts.
- **`tools/verify/s1_image_throughput.py`** (< 1 s, 4 checks): image delivery time vs band, duty and modulation, with fragmentation and erasure FEC; Codec2 occupancy (Example 6).
- For a full design, carry these numbers into the link budget ([link budget methodology](../09-propagation-link-budget/link-budget-methodology.md)) and the project recipe ([LoRa rocket telemetry link](../20-projects-recipes/lora-rocket-telemetry-link.md)).

## Open questions / gaps
- GMSK coherent-detection and short-block LDPC/polar entries are estimates (not simulated here); a dedicated simulation (e.g. with Sionna or AFF3CT) would replace them with measured curves.
- The comparison is AWGN-only; a fading/erasure-channel version with realistic rocket fade statistics (from flight logs of RSSI vs time) would be more decisive.
- LoRa's datasheet SNR criterion is 1 % PER on a 64-byte CR 4/5 packet (per domain 15's reading of the SX1261/2 datasheet), whereas the other rows are BER 1e-5; the comparison is therefore approximate at the ≈ 1 dB level. At SF11/12 on 125 kHz, low-data-rate optimisation cuts the rate to 244 b/s (SF12) and raises the Eb/N0 to ≈ 7.1 dB.

## Sources
1. CCSDS 130.1-G-3, *TM Synchronization and Channel Coding — Summary of Concept and Rationale*, 2020 — code performance comparisons (conv ≈ 5.5 dB gain; RS concatenation +2 dB; turbo within ≈ 1 dB of limit). https://ccsds.org/Pubs/130x1g3e1.pdf (standard, informative)
2. Semtech, *SX1276/77/78/79 datasheet*, Rev. 7 — LoRa demodulator SNR per spreading factor and bit-rate formula. (datasheet)
3. B. Sklar, "Defining, designing, and evaluating digital communication systems," *IEEE Communications Magazine* 31(11):91–101, 1993 — bandwidth-efficiency plane and power/bandwidth-limited design regimes. (peer-reviewed tutorial)
4. J. G. Proakis and M. Salehi, *Digital Communications*, 5th ed., McGraw-Hill, 2008 — §4.6 (comparison of modulation methods vs Shannon). (textbook)
5. T. S. Rappaport, *Wireless Communications*, 2nd ed., 2002 — ch. 6 (choice of modulation: power efficiency, bandwidth efficiency, constant envelope). (textbook)
6. This folder's verification scripts (`tools/verify/comms_ber_awgn.py`, `comms_coding.py`, `comms_lora_cr.py`, `comms_modulation_spectra.py`, `comms_ofdm.py`, `comms_choice_guide.py`) — all numbers in the table. (derived, verified)
7. Space Bar avionics knowledge base (`~/.claude/knowledge/space-bar-avionics/`) — flown hardware: EBYTE E22-400T33D (433 MHz, 2 W) and E220-900T30D (900 MHz, 1 W) LoRa modules; downlink-only telemetry. (internal project notes)
8. `tools/verify/s1_image_throughput.py` — Example 6. (own verification)
