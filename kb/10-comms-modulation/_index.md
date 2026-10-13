# 10-comms-modulation — Communications, modulation and coding

How information is put onto a carrier and got back out through noise: analog modulation (AM/FM/PM/SSB), digital modulation (OOK, FSK/MSK/GFSK/GMSK, PSK, QAM, APSK), detection theory and the matched filter, BER vs Eb/N0 and Shannon's limit, pulse shaping and ISI, spread spectrum (DSSS, FHSS, chirp/LoRa), OFDM, forward error correction, synchronisation (carrier, frequency, timing, frame), packet framing and link protocols, and a decision guide for choosing a scheme. Written for designing custom radios and rocket telemetry links (433/868/915 MHz LoRa and FSK, GNSS), with every key number verified by a script in `tools/verify/comms_*.py`. Hardware (PAs, mixers, LNAs) lives in 06; noise/sensitivity in 07; propagation and link budgets in 09; radar waveforms in 11; SDR/DSP implementation in 14; LoRa specifics in 15.

## Reading order (beginner → advanced)
1. [Analog modulation — AM, DSB, SSB, VSB, FM, PM](analog-modulation-am-fm-pm-ssb.md) — the carrier-modulation ideas and Bessel/Carson maths everything else builds on.
2. [Digital modulation — OOK, FSK/MSK/GMSK, PSK, QAM, APSK](digital-modulation-psk-qam-fsk.md) — constellations, bits vs symbols, bandwidth, PAPR, EVM.
3. [Matched filter and signal detection](matched-filter-detection.md) — why the correlator is optimal; 2E/N0; detection thresholds.
4. [BER, Eb/N0 and the Shannon limit](ber-ebn0-and-shannon.md) — the central page: conversions, BER derivations, capacity, −1.59 dB, finite-length limits, fading.
5. [Pulse shaping, ISI and equalisation](pulse-shaping-isi.md) — Nyquist criterion, RC/RRC, eye diagrams, ZF/MMSE/DFE.
6. [Synchronisation — carrier, frequency, timing, frame](synchronization-carrier-timing.md) — Costas/PLL, CFO estimation, Gardner/M&M, Doppler on rockets.
7. [Channel coding and FEC](channel-coding-fec.md) — Hamming to LDPC/polar, soft decisions, interleaving, what LoRa's CR buys.
8. [Packet framing and protocols](packet-framing-protocols.md) — preamble, sync word, CRC, whitening, PER, ARQ vs FEC, rocket frame design.
9. [Spread spectrum — DSSS, FHSS, CSS, CDMA](spread-spectrum-dsss-fhss-css.md) — processing gain, Gold codes (GPS C/A), LoRa chirps.
10. [OFDM](ofdm.md) — DFT subcarriers, cyclic prefix, PAPR, CFO sensitivity, Wi-Fi/LTE/DVB-T.
11. [Choosing a modulation and coding scheme](modulation-choice-guide.md) — decision guide and comparison table.
12. [Multiple access and duplexing](multiple-access-and-duplexing.md) — FDMA/TDMA/CDMA/OFDMA, ALOHA and CSMA throughput, FDD vs TDD, duplexers, launch-day channel plan.
13. [MIMO capacity and channel estimation](mimo-capacity-and-channel-estimation.md) — SVD capacity, diversity, Alamouti/STBC, detectors, CSI.
14. [Weak-signal digital modes](weak-signal-digital-modes.md) — FT8/WSPR/JT65/Q65 as near-limit low-rate designs, compared with LoRa.

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [analog-modulation-am-fm-pm-ssb](analog-modulation-am-fm-pm-ssb.md) | AM power & envelope detection, DSB-SC/SSB/VSB, FM/PM Bessel spectra, Carson, FM SNR (3β²/2), threshold, capture, pre-/de-emphasis, NBFM, APRS | mixed | high |
| [digital-modulation-psk-qam-fsk](digital-modulation-psk-qam-fsk.md) | signal space, OOK/BPSK/QPSK/OQPSK/π/4/8PSK/QAM/APSK, CPFSK/MSK/GFSK/GMSK (h, BT, 99 % BW), PSD, PAPR & PA back-off, EVM | mixed | high |
| [matched-filter-detection](matched-filter-detection.md) | Cauchy–Schwarz derivation, correlator, 2E/N0 conventions, ML/MAP, coloured noise, Neyman–Pearson & Marcum Q, pulse compression, CFO/timing loss | mixed | high |
| [ber-ebn0-and-shannon](ber-ebn0-and-shannon.md) | Eb/N0 ↔ Es/N0 ↔ SNR ↔ C/N0, Q-function, BER of all common schemes, Shannon–Hartley, −1.59 dB, BI-AWGN limits, finite blocklength, Rayleigh fading, sensitivity examples | mixed | high |
| [pulse-shaping-isi](pulse-shaping-isi.md) | Nyquist ISI criterion, RC/RRC formulas, roll-off, truncation, eye diagrams, channel ISI, ZF/MMSE/DFE/MLSE, LMS | mixed | high |
| [synchronization-carrier-timing](synchronization-carrier-timing.md) | offset budget (ppm vs Doppler), PLL/Costas design & jitter, FLL, CRB frequency estimation, M-th power, Gardner/M&M/early–late, frame sync | mixed | high |
| [channel-coding-fec](channel-coding-fec.md) | block codes (Hamming, Golay, BCH, RS), convolutional/Viterbi, soft vs hard, concatenation, turbo, LDPC, polar, short blocks, interleaving, LoRa CR, libraries | mixed | high |
| [packet-framing-protocols](packet-framing-protocols.md) | preamble, sync-word P_FA/P_miss, CRC maths & parameters, whitening, COBS, PER, optimal frame length, ARQ/HARQ, erasure coding, CCSDS-lite rocket frames | mixed | high |
| [spread-spectrum-dsss-fhss-css](spread-spectrum-dsss-fhss-css.md) | processing gain, jamming margin, m-sequences, Gold/GPS C/A, FHSS, CSS/LoRa dechirp, CFO–timing coupling, CDMA, RAKE, LPI | mixed | high |
| [ofdm](ofdm.md) | IFFT construction, CP & one-tap EQ, pilots, PAPR, CFO/phase-noise ICI, Schmidl–Cox, numerology, when to use it | mixed | high |
| [modulation-choice-guide](modulation-choice-guide.md) | comparison table (Eb/N0, BW, η, PAPR, relative range), decision rules, rocket-specific recommendations | intermediate | medium |
| [multiple-access-and-duplexing](multiple-access-and-duplexing.md) | FDMA/TDMA/CDMA/OFDMA/SDMA, pure & slotted ALOHA derived and simulated (1/2e, 1/e), N-sender survival, capture, non-persistent CSMA (Kleinrock–Tobagi), hidden terminals, TDMA guards on GNSS time, FDD duplexer isolation & desense, TDD T/R switch, near-far, EBYTE channel grids, launch-day plan | mixed | high |
| [mimo-capacity-and-channel-estimation](mimo-capacity-and-channel-estimation.md) | MIMO model, SVD capacity & water-filling derived, DoF slope, LOS rank-1, MRC/Alamouti BER, DMT, LS/MMSE estimation, OFDM pilot spacing (DFT interpolation), ground-station polarisation/height diversity; S8: Alamouti 2×2, orthogonal STBC, MRT, ZF/LMMSE/ML detectors, fixed-rate DMT, imperfect CSI, CDD/SFBC, CSI sounding, two-antenna rocket feed | mixed | high |
| [weak-signal-digital-modes](weak-signal-digital-modes.md) | FT8/FT4/WSPR/JT65/JT9/Q65/FST4 parameters, SNR in 2500 Hz → Eb/N0, why FT8 decodes at −21 dB, NC-MFSK capacity limits, LoRa SF12 comparison, PSK31/RTTY/APRS/DMR/D-STAR, FT8-style beacon | mixed | high |

## Verification scripts (all print PASS/FAIL; run `python3 tools/verify/<name>`)
| Script | Checks | Runtime |
|---|---|---|
| `comms_ber_awgn.py` | Monte-Carlo vs closed-form BER (11 schemes), required-Eb/N0 table, Shannon & BI-AWGN limits vs CCSDS, finite-length normal approximation, Rayleigh fading | ≈ 2 s |
| `comms_matched_filter.py` | 2E/N0 for any pulse, correlator equivalence, RC mismatch loss, LFM compression, Pd (coherent/Marcum), CFO & timing losses | ≈ 5 s |
| `comms_modulation_spectra.py` | tone orthogonality, 99 % bandwidths (MSK/GMSK/BPSK), PAPR (constellation & RRC-filtered), EVM = 1/√SNR, phase jumps | ≈ 2 s |
| `comms_pulse_shaping.py` | RC zero-ISI & folded spectrum, RRC truncation ISI/OOB, eye vs timing offset, ZF/MMSE/DFE vs matched-filter bound | < 1 s |
| `comms_analog_fm.py` | Bessel lines, Carson power, FM SNR = 3β²/2 & threshold, AM figures of merit, de-emphasis gain, capture effect | ≈ 3 s |
| `comms_coding.py` | K=7 (171,133) spectrum, soft/hard bounds & Viterbi MC, Hamming/Golay/RS, concatenated RS+conv, interleaver | ≈ 2 min |
| `comms_lora_cr.py` | idealised LoRa CR 4/5–4/8 PER model (SF7, SF12) | ≈ 6 s |
| `comms_sync.py` | Costas jitter & squaring loss, ramp error, Gardner/M&M S-curves, CRB frequency estimation, 4th-power CFO, Doppler table | ≈ 2 s |
| `comms_spread_spectrum.py` | m-sequences, GPS C/A Gold codes vs IS-GPS-200/gps.gov, DSSS vs jammers, CSS dechirp & CFO shift, GPS link numbers | < 1 s |
| `comms_ofdm.py` | CP/one-tap EQ, PAPR CCDF, CFO ICI, Schmidl–Cox, 802.11a/LTE/DVB-T numerology | < 1 s |
| `comms_crc_framing.py` | CRC check values & properties, PER, sync-word thresholds, PN9, ARQ, optimal frame length, erasure coding | ≈ 2 s |
| `comms_choice_guide.py` | comparison table & relative ranges for the decision guide | < 1 s |
| `est_multiple_access.py` | ALOHA/slotted ALOHA sims, N-sender survival, capture, np-CSMA sim vs formula, LoRa ToA vs rfcalc, TDMA/FDMA plan numbers, duplexer isolation, desense, near-far | ≈ 2 s |
| `s8_weak_signal_ebn0.py` | weak-signal mode Eb/N0 table, NC/coherent M-FSK capacity limits, FT8 finite-length, LoRa short-message comparison | ≈ 25 s |
| `s8_alamouti_mimo.py` | Alamouti 2×1/2×2, OSTBC orthogonality, MRT, ZF/LMMSE/ML, DMT at 4 b/s/Hz, CSI error, CDD, airframe pattern | ≈ 6 s |
| `s8_outage_capacity.py` | outage/ergodic capacity, water-filling in time, truncated inversion, adaptive QAM, LoRa SF adaptation | ≈ 1 s |
| `s8_info_coding.py` | entropy, BSC vs BI-AWGN, CM/BICM capacity, sphere hardening, TCM d²free, (3,6) LDPC belief propagation | ≈ 10 s |
| `s8_sync_extras.py` | Viterbi & Viterbi vs MCRB, residual carrier, ML TED/polyphase, Oerder–Meyr, NCC delay vs CRB, 5G NR numerology | ≈ 3 s |

## Domain FAQ (top questions → page#section)
- *How do I convert SNR to Eb/N0 (and why is my simulation 3 dB off)?* → [ber-ebn0-and-shannon#The math](ber-ebn0-and-shannon.md#level-1--definitions-units-and-the-conversions), [#Common mistakes](ber-ebn0-and-shannon.md#common-mistakes--misconceptions)
- *What Eb/N0 do I need for BER 1e-5?* → [ber-ebn0-and-shannon#TL;DR](ber-ebn0-and-shannon.md#tldr)
- *Does LoRa beat Shannon / how can it work below the noise floor?* → [ber-ebn0-and-shannon Example 2](ber-ebn0-and-shannon.md#example-2--what-ebn0-does-lora-actually-run-at), [spread-spectrum#Intuition](spread-spectrum-dsss-fhss-css.md#intuition-no-math)
- *How wide is my FSK/GFSK signal?* → [digital-modulation#Level 1](digital-modulation-psk-qam-fsk.md#level-1--representation-rates-and-bandwidth)
- *What is Carson's rule and the FM threshold?* → [analog-modulation#Level 2](analog-modulation-am-fm-pm-ssb.md#level-2--spectra-and-detection)
- *RC vs RRC, and how many taps?* → [pulse-shaping-isi#TL;DR](pulse-shaping-isi.md#tldr)
- *How big is rocket Doppler and how do I handle it?* → [synchronization#Level 1](synchronization-carrier-timing.md#level-1--what-the-offsets-look-like), [#Worked examples](synchronization-carrier-timing.md#worked-examples)
- *How much does FEC buy, and what does LoRa CR 4/8 do?* → [channel-coding-fec#TL;DR](channel-coding-fec.md#tldr)
- *Which CRC, and what sync-word error tolerance?* → [packet-framing-protocols#Level 2](packet-framing-protocols.md#level-2--each-component)
- *Should I use OFDM for my rocket link?* → [ofdm Example 2](ofdm.md#example-2--why-ofdm-is-wrong-for-a-10-kbs-rocket-telemetry-link)
- *Which modulation should I use?* → [modulation-choice-guide](modulation-choice-guide.md)
- *Can several rockets share one LoRa channel? What is ALOHA throughput?* → [multiple-access#Level 2](multiple-access-and-duplexing.md#level-2--random-access-aloha-slotted-aloha-capture-and-csma), [Worked example 1](multiple-access-and-duplexing.md#worked-examples)
- *Duplexer or T/R switch? FDD or TDD?* → [multiple-access#Level 3](multiple-access-and-duplexing.md#level-3--fdmatdmacdmaofdma-in-practice-duplexing-near-far-and-a-launch-day-plan)
- *How does FT8 decode at −21 dB, and is it better than LoRa?* → [weak-signal-digital-modes#Level 2](weak-signal-digital-modes.md#level-2--why-ft8-works-at-21-db-and-how-close-to-the-limit-it-is), [Example 2](weak-signal-digital-modes.md#worked-examples)
- *Ergodic or outage capacity for a telemetry packet? How much does adaptive modulation or SF adaptation buy?* → [ber-ebn0-and-shannon#Level 3c](ber-ebn0-and-shannon.md#level-3c--capacity-of-fading-channels-ergodic-outage-and-adaptive-modulation-w5-s8)
- *Feed two rocket antennas the same signal or an Alamouti pair?* → [mimo Example 7](mimo-capacity-and-channel-estimation.md#example-7--two-antennas-on-the-rocket-same-signal-switching-or-alamouti)

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
Proakis & Salehi *Digital Communications* (5e); Sklar *Digital Communications* (2e); Haykin *Communication Systems* (4e); Lathi & Ding; Goldsmith *Wireless Communications*; Rappaport *Wireless Communications*; Lin & Costello *Error Control Coding*; Rice *Digital Communications: A Discrete-Time Approach*; Mengali & D'Andrea; Shannon 1948; Nyquist 1928; Gardner 1986; CCSDS 131.0-B-5 / 130.1-G-3 / 133.0-B-2; IS-GPS-200; NTIA Annex J; MIT 6.02 notes; PySDR; Koopman CRC Zoo.

## Known gaps
- Multiple access: measured adjacent-channel selectivity/blocking and TX phase noise of the EBYTE modules are not in the KB (needed to close near-far budgets on a shared range); ALOHA stability/back-off and LoRaWAN-scale simulations not covered.
- Turbo/LDPC/polar performance quoted from CCSDS/literature, not re-simulated; short-block LDPC/polar and coherent GMSK rows of the choice guide are estimates.
- LoRa-specific numbers (datasheet SNR criterion, CFO tolerance, inter-SF rejection, LDRO) deferred to domain 15; the LoRa CR model here is idealised.
- Discriminator (G)FSK detector loss vs ideal NC-FSK: simulated for one configuration in [14 software demodulation](../14-sdr-dsp/software-demodulation.md) (2-FSK h = 1: +0.07 dB; 2-GFSK h = 0.5, BT = 0.5: +1.41 dB at BER 10⁻³, `tools/verify/dsp_demod.py`); the dependence on h, BT and pre-detection bandwidth is still not mapped.
- 802.11 EVM limits: values checked against 802.11 working-group documents (W5-S18b, 2026-10-13); the clause-17 table number is unconfirmed. DVB-T carrier counts (1705/6817) and T = 7/64 µs were confirmed from secondary sources (R&S, a university lecture). The guard fractions ¼–1/32 come from secondary sources only. ETSI EN 300 744 itself could not be downloaded.
- No measured rocket fade/burst statistics; interleaver/erasure-coding examples are illustrative.
- Crystal g-sensitivity during motor burn (affects sync) not covered (domains 04/18).
- Analog land-mobile (TIA-603/ETSI) pre-emphasis and SINAD definitions not fetched.
