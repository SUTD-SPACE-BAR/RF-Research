# Research log W5-S8: Comms PHY extensions (10-comms-modulation)
Status: complete
Owner scope: new kb/10-comms-modulation/weak-signal-digital-modes.md; extend 10/mimo-capacity-and-channel-estimation, 10/ber-ebn0-and-shannon, 10/synchronization-carrier-timing, 10/ofdm, 10/channel-coding-fec; row in 10/_index.md; slug in tools/taxonomy.md; tools/verify/s8_*.py; GAP_REGISTER §3/§5/§8 rows for G-10-02, -03, -05, -06, -07, -08. Avoid 10/matched-filter-detection.

## Plan
- [x] G-10-02 — DONE (mimo page Level 2b items 11–18, Example 7, table rows, mistakes; s8_alamouti_mimo.py 28/28) — extend mimo page: Alamouti 2×2 (diversity 4), orthogonal STBC beyond 2 Tx (rate limits), ZF/MMSE/ML spatial-multiplexing BER sim, Alamouti with channel-estimation error and time variation, MIMO-OFDM (SFBC, per-subcarrier), CSI sounding/feedback. Script s8_alamouti_mimo.py.
- [x] G-10-03 — DONE (new page weak-signal-digital-modes; s8_weak_signal_ebn0.py 34/34) — new 10/weak-signal-digital-modes: FT8/FT4/WSPR/JT65/Q65/JT9/PSK31/RTTY/APRS/DMR-D-STAR; SNR in 2.5 kHz → Eb/N0; coding; vs LoRa SF12 and Shannon; why −21 dB. Script s8_weak_signal_ebn0.py.
- [x] G-10-05 — DONE (ber page Level 3c, Example 6; s8_outage_capacity.py 29/29) — ber-ebn0 page: outage/ergodic capacity closed forms + MC, adaptive modulation, LoRa ADR analogue. Script s8_outage_capacity.py.
- [x] G-10-08 — DONE (ber Level 3b; coding page Coded modulation + Belief propagation; s8_info_coding.py 16/16) — ber-ebn0 (entropy, mutual info, signal-space geometry) + channel-coding-fec (TCM, BICM, belief propagation) short L3 sections.
- [x] G-10-06 — DONE (sync Level 2d; s8_sync_extras.py) — sync page: feed-forward ML (Viterbi&Viterbi) vs Costas, residual-carrier PSK, polyphase timing recovery, FFT symbol sync, normalised cross-correlation delay estimation.
- [x] G-10-07 — DONE (ofdm Level 3b; s8_sync_extras.py §6) — ofdm page: 5G NR numerology table, LTE/Wi-Fi on an analyser (RB loading, DC null), router MIMO antennas.
- [x] GAP_REGISTER close rows (C133–C138, §3 marked, §8 change log); _index row + FAQ + scripts table, taxonomy slug — DONE — (§5 C-numbers, §3 marks, §8 change log); _index + taxonomy.

## Log (append-only)
- 2026-10-13 — Step 0 done: read CONVENTIONS, GAP_REGISTER §3 rows/§6 S8/orchestrator notes, canonical values (LoRa SNR −7.5…−20 dB, 2.5 dB/SF; E/N0 conventions), 10/_index, MIMO page (E11; already has Alamouti 2×1 BER, DMT, LS/MMSE, ZF/MMSE/SIC/ML named), ber-ebn0 page.

- 2026-10-13 — fetched FT4/FT8 QEX paper (wsjt.sourceforge.io/FT4_FT8_QEX.pdf, read as PDF): 77-bit payload, CRC-14, LDPC(174,91), FT8 8-GFSK BT=2, T=0.160 s, 79 symbols (58 data + 3×7 Costas), FT4 4-GFSK BT=1, T=0.048 s, 105 symbols; thresholds = SNR2500 at 50 % decode probability; Table 5 (FT8 −19.6 N=1 BP, −20.3 block BP, −20.8 BP+OSD AWGN; FT4 −15.3/−16.9/−17.5); Table 6 (max AP −22.7 FT8, −19.5 FT4; fading channels). Block detection over N=1–3 symbols, OSD, multipass subtraction.
- 2026-10-13 — WSJT-X 2.5.4 User Guide PDF (VK5PAS mirror, pdftotext): §17 protocol specs + Table 7 (FEC, (n,k), Q, keying rate, BW, sync energy, Tx duration, threshold for all slow modes: FST4, FT4, FT8, JT4, JT9, JT65, Q65, WSPR, FST4W); WSPR K=32 r=1/2 162 symbols, data bit MSB + sync LSB; Q65 (65,15) punctured to (63,13), 12-bit CRC in punctured symbols.
- 2026-10-13 — PA3FWM tn09b (Eb/N0 of amateur modes: RTTY −5 dB/32 b/s → 14 dB; PSK31 −10 dB/31 b/s → 9 dB; WSPR −29 dB; footnote about sync energy). DMR/D-STAR parameters from search summaries (DMR 4FSK 4800 sym/s 9.6 kb/s 2-slot TDMA 30 ms in 12.5 kHz; D-STAR DV 0.5 GMSK 4.8 kb/s = 2.4 voice + 1.2 FEC + 1.2 data, 6.25 kHz) — secondary sources.
- 2026-10-13 — 5G NR max NRB (270/273/135 FR1; 264 FR2) confirmed via 3GPP R4 draft + iBwave poster (secondary). LoRaWAN ADR: Semtech-style margin 10 dB, 20 uplinks, NStep = margin/3; TTS default 15 dB and /2.5 (thethingsindustries.com docs).
- 2026-10-13 — wrote tools/verify/s8_weak_signal_ebn0.py (25/25 PASS). Findings: modern LDPC/QRA modes cluster at 4.2–5.4 dB Eb/N0 (all energy incl. sync); FT8 1.1 dB above single-symbol NC-8FSK capacity at its rate; FT4 and WSPR (with block detection) beat single-symbol NC limit; ideal LoRa SF12 with 10-byte payload needs ≈ 3 dB more Eb/N0 than FT8 (preamble/header overhead).
- 2026-10-13 — new page kb/10-comms-modulation/weak-signal-digital-modes.md written (FT8 −21 dB explained; mode table; LoRa comparison; other modes).
- 2026-10-13 — s8_alamouti_mimo.py 28/28: Alamouti 2×2 = 4-branch MRC −3 dB; rate-3/4 OSTBC orthogonality; MRT = MRC; 2×2 QPSK ZF/MMSE/ML 9.6e-3/6.5e-3/5.3e-4 at 20 dB; DMT at 4 b/s/Hz (crossover ~15 dB); pilot loss 4.8/1.4 dB (T=1/4); time-variation floor; CDD; airframe two-antenna pattern. MIMO page extended (Level 2b, Example 7).
- 2026-10-13 — s8_outage_capacity.py 29/29 and s8_info_coding.py 16/16 (entropy, BSC vs BI-AWGN 1.77 vs 0.19 dB, CM/BICM, shaping 1.53 dB, sphere hardening, TCM d²free 4.0/4.586, (3,6) LDPC n=1008 BP: FER 0.23/0.03/0 at 1.5/2.0/2.5 dB). ber page Level 3b (info theory) and 3c (fading capacity, adaptive modulation, LoRa SF adaptation) added.
- 2026-10-13 — s8_sync_extras.py 34/34 (V&V r^4 1.52× MCRB at 10 dB, m=1 1.11×; residual-carrier split; ML TED; P=32 PFB 0.004 dB; Oerder–Meyr 0.009 T; NCC 0.96× CRB; NR numerology; LTE idle −13.2 dB). Sync Level 2d and OFDM Level 3b written. Coding page: TCM/BICM/BP sections.
- 2026-10-13 — GAP_REGISTER: C133–C138 appended, §3 rows marked, change log. 10/_index (page row, scripts, FAQ, reading order), taxonomy slug; build_index.py --check: 0 broken links, 0 control chars, 0 missing sections. All 5 scripts PASS (141 checks).

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
| 1 | Franke, Somerville, Taylor, QEX Jul/Aug 2020 | peer-reviewed-ish magazine (primary designers) | FT8/FT4 parameters and thresholds | primary |
| 2 | WSJT-X 2.5.4 User Guide §17 | software documentation (primary) | all slow-mode parameters | primary |
| 3 | P.-T. de Boer PA3FWM tn09b | practitioner note | RTTY/PSK31 Eb/N0 | secondary |
| 4 | thethingsindustries.com ADR docs; ADR-TTN papers | documentation | ADR margin | secondary |

## Contradictions / discrepancies found
- WSPR threshold: WSJT-X 2.5 guide Table 7 says −31 dB; older docs/PA3FWM say −28/−29 dB. At −31 dB WSPR's Eb/N0 (6.4 dB) is below the single-symbol NC-BFSK capacity limit (6.9 dB), which requires multi-symbol detection; not confirmed that wsprd does this. Recorded on the page (Level 3, Open questions).
- FT4 threshold: QEX −17.5 dB vs guide Table 7 −17 (rounding). Used QEX.
- Truncated channel inversion at 10 dB Rayleigh computes to 2.66 b/s/Hz with Goldsmith's formula (cutoff 4.8 dB); I had expected ~2 from memory — the script value stands.
## Knowledge gaps noticed (for later gap-filling)
- No first-hand SDR captures of LTE/NR/Wi-Fi spectra; analyser descriptions are from standards knowledge.
- WSPR block-detection claim (why −31 dB beats the single-symbol NC-BFSK limit) unverified; an independent wsprd simulation would settle it.
- FT8 decoder drift tolerance not published; an FT8-style UHF beacon needs a measured TCXO/GNSS drift budget.
- Several classic papers (Tarokh 1999, Viterbi&Viterbi, Oerder–Meyr, harris–Rice, Ungerboeck, Goldsmith–Chua/Varaiya, Caire BICM) cited from knowledge — candidates for the S18 citation-verification pass.
- ETSI DMR and JARL D-STAR parameters only via secondary sources.
## Cross-domain notes (things other domains should cover/link)
- 15/rocket-telemetry-radio-design and 15/lora-sensitivity-and-link-budget could link 10/weak-signal-digital-modes (Example 2: LoRa vs FT8 per bit; Example 4: FT8-style recovery beacon) and 10/ber-ebn0-and-shannon#level-3c (SF adaptation, ADR unsuitable for rockets).
- 17/spectrum-analyzers could link 10/ofdm#level-3b for LTE/Wi-Fi/NR signal appearance.
- 08/antennas-on-rockets could link 10/mimo Example 7 (two-antenna feed: coherent nulls vs Alamouti).
## Resume instructions
Task complete (2026-10-13). Nothing to resume.

(Original instructions:) If interrupted: check the Plan boxes above; each item is an independent section. Re-read the target page, find whether the section heading named in the plan already exists, and continue from the first unchecked item. Scripts live in tools/verify/s8_*.py and print PASS/FAIL.
