# Research log W2-B3: 10-comms-modulation
Status: complete
Owner scope: kb/10-comms-modulation/ ; research-logs/W2-B3-comms.md ; tools/verify/comms_*.py

## Plan
Order: BER/Shannon first (everything else leans on Eb/N0 and Q-function results), then matched
filter (derivation used by BER page), digital modulation, pulse shaping, analog modulation,
coding, sync, spread spectrum, OFDM, framing, choice guide, _index, _sources.
- [x] ber-ebn0-and-shannon (kb/10-comms-modulation/ber-ebn0-and-shannon.md; verified tools/verify/comms_ber_awgn.py ALL PASS) — Q-function, BER derivations BPSK/QPSK/MPSK/MQAM/FSK coh+noncoh/DPSK/OOK, Eb/N0<->SNR<->C/N0, Shannon-Hartley, -1.59 dB, bandwidth-efficiency plane; MC script
- [x] matched-filter-detection (verified tools/verify/comms_matched_filter.py ALL PASS) — Cauchy-Schwarz derivation, correlator equivalence, 2E/N0, ML/MAP, Neyman-Pearson, pulse compression link
- [x] digital-modulation-psk-qam-fsk (verified comms_modulation_spectra.py) — signal space, OOK..APSK, CPFSK/MSK/GFSK/GMSK, spectra, spectral efficiency, PAPR, EVM
- [x] pulse-shaping-isi (verified comms_pulse_shaping.py) — Nyquist ISI criterion, RC/RRC, roll-off, eye diagram, multipath ISI, ZF/MMSE/DFE
- [x] analog-modulation-am-fm-pm-ssb (verified comms_analog_fm.py) — AM/DSB/SSB/VSB, envelope vs coherent, FM/PM, Bessel, Carson, FM SNR, threshold, capture, emphasis, NBFM/APRS
- [x] channel-coding-fec (verified comms_coding.py + comms_lora_cr.py) — Hamming, BCH, RS, conv+Viterbi, turbo, LDPC, polar, interleaving, coding gain, soft/hard, LoRa CR
- [x] synchronization-carrier-timing (verified comms_sync.py) — PLL/Costas, CFO estimation, Gardner/M&M/early-late, frame sync, Doppler for rockets
- [x] spread-spectrum-dsss-fhss-css (verified comms_spread_spectrum.py) — processing gain, jamming margin, m-seq/Gold, FHSS, CSS, CDMA, LPI
- [x] ofdm (verified comms_ofdm.py) — DFT subcarriers, CP, orthogonality, PAPR, CFO sensitivity, pilots, Wi-Fi/LTE/DVB numerology
- [x] packet-framing-protocols (verified comms_crc_framing.py) — preamble, sync word, header, CRC, whitening, ARQ vs FEC, PER vs BER, rocket frame design
- [x] modulation-choice-guide (numbers: comms_choice_guide.py) — decision guide + comparison table
- [x] _index.md, _sources.md
- [x] verification scripts tools/verify/comms_*.py (12 scripts, all PASS on final run)

## Log (append-only)
- 2026-09-27 — Read CONVENTIONS.md, INDEX.md, HANDOFF.md, _TASK_SPECS.md, example page (00/decibels). Folder kb/10-comms-modulation empty. Created this log. Read Space Bar avionics KB (downlink-only half-duplex LoRa, framed packets with CRC, protocol version, per-type sequence counters) for rocket examples.
- 2026-09-27 — Read Shannon 1948 (pdftotext), MIT 6.02 ch9, CCSDS 131.0-B-5, CCSDS 130.1-G-3, PySDR pulse shaping + sync. Key facts in Sources table S1-S5. WebFetch cannot parse PDFs but saves them; pdftotext on saved file works (scratchpad/comms/).
- 2026-09-27 — Read Jacobsen Eb/N0 article, Koopman CRC zoo (16-bit table), NTIA Annex J (necessary bandwidth). Forum sweep: QPSK=BPSK per bit (dsplog/comp.dsp), complex noise N0/2 per dimension (MATLAB AWGN doc) -> Common mistakes. PySDR BW=Rs(1+beta) confirmed as two-sided (complex baseband) width — note one-sided vs two-sided confusion.

- 2026-09-27 — Wrote tools/verify/comms_ber_awgn.py (MC vs theory 11 schemes, req Eb/N0 table, Shannon, BI-AWGN limits 0.187/-0.495/-0.794/-1.073 dB vs CCSDS 0.2/-0.5/-0.8/-1.1, PPV normal approx, Rayleigh). All PASS. Wrote page ber-ebn0-and-shannon.
- 2026-09-27 — Wrote tools/verify/comms_coding.py: K=7 (171,133) dfree=10, B_d=36/211/1404/11633 computed; soft union bound 1e-5 @ 4.17 dB (MC 1.4e-5 @ 4.0 dB), hard 6.52 dB (2.35 dB penalty); RS(255,223) hard alone 6.29 dB @1e-5; concatenated (MC Viterbi byte errors + ideal interleaving) 2.25 dB @1e-5 => +1.9 dB over conv (CCSDS ~2.0). Hamming/LoRa CR d_min checks. All PASS. Updated BER page to 4.2 dB (was 4.4 from memory).
- 2026-09-27 — Wrote comms_matched_filter.py (2E/N0 3 pulses, RC mismatch BT=0.20 loss 0.89 dB, LFM width 0.886/B, Pd coherent/Marcum, CFO sinc loss: 32-bit sync @10 kbps loses 6.9 dB @200 Hz, 24.7 dB @1 kHz). Wrote matched-filter-detection page.
- 2026-09-27 — Wrote comms_modulation_spectra.py: tone orthogonality (coh 1/2T, nc 1/T; nc corr at 1/2T = 2/pi), 99% OBW MSK 1.18 Rb analytic (sim 1.19), GMSK BT .5/.3/.25 = 1.03/0.91/0.86 Rb (matches ITU-R SM.328 via NTIA), rect BPSK 20.6 Rb, main lobe 90.3%; PAPR const 16QAM 2.55, 64QAM 3.68 dB; RRC .35 QPSK 3.75 dB, 16QAM 5.64 dB @1e-4 CCDF; beta .2 -> 5.1 dB, .5 -> 3.2 dB; EVM=1/sqrt(SNR); phase jumps QPSK 180/pi4 135/OQPSK 90. All PASS.
- 2026-09-27 — Wrote digital-modulation-psk-qam-fsk page. Wrote comms_pulse_shaping.py (RC zero-ISI & folded spectrum beta 0..1; RRC span +-4/8/16 -> ISI -36/-50/-59 dB, OOB -43/-50/-64 dB; eye at 0.1T: 61/72/79/90% for beta .2/.35/.5/1; EQ example none 3.1e-2, ZF 1.0e-3 (3.2 dB enh), MMSE 6.7e-4, DFE 1.1e-4, MFB 3.9e-6). All PASS. Wrote pulse-shaping-isi page.
- 2026-09-27 — Wrote comms_analog_fm.py (Bessel lines vs FFT, sum Jn^2=1, nulls 2.405/5.520/8.654, Carson power 99-99.9%, FM SNR = 1.5 beta^2 SNR_C to 0.1 dB, threshold: 0.1 dB short @10 dB CNR, 8.8 @7, 16.8 @4; AM FOM mu=0.8/0.5 OK (mu=1 converges slowly - envelope touches zero); de-emphasis 13.2/10.2 dB; capture SIR 8.3/11/14.5/18.6 dB for D/U 1/3/6/10). Fixed a 2*pi phase bug found during testing. All PASS. Searched APRS (Bell 202 1200/2200 Hz, 144.39 MHz) and FM capture ratio (forum/marketing 1-2 dB, marked unverified). Wrote analog-modulation page. Session was interrupted by API limit once, resumed.
- 2026-09-27 — Wrote comms_lora_cr.py (idealised LoRa CR model: 32-byte pkt, 1% PER, SF7 Eb/N0 6.6/7.3/6.2/6.9 dB for CR4/5..4/8; SF12 5.1/5.8/5.0/5.6 -> Hamming codes give ~0-0.4 dB net in AWGN; per-symbol SNR 1.5-1.8 dB lower for 4/8 at 1.6x airtime). Added Hamming(7,4) 0.42 dB / Golay 2.1-2.3 dB hard gains, asymptotic 7.0 dB, RS burst 121 bits to comms_coding.py (rerun ALL PASS). Wrote channel-coding-fec page.
- 2026-09-27 — Wrote comms_sync.py (Costas jitter 1.91 vs 1.86 deg theory w/ squaring loss; freq-step zero error; ramp error (domega/dt)/wn^2; Gardner & M&M S-curves, Gardner phase-invariant; FFT+parabolic freq estimator = CRB at 10 dB N=256; 4th-power QPSK CFO; Doppler/ppm table). ALL PASS. Wrote synchronization-carrier-timing page (loop gains from M. Rice 2009 App. C, from memory of the textbook — formulas verified by the loop simulation matching theory).
- 2026-09-27 — Wrote comms_spread_spectrum.py: m-seq props; GPS C/A PRN1 1440, PRN2 1620 octal; SBAS PRN120/131/133/138 via G2 delay match gps.gov Jan-2026 table (0671/1226/0046/1327); Gold xcorr {-65,-1,63}; DSSS N=63 vs broadband & CW jammer at J/S +13 dB (BER 6.4e-3/5.1e-3 vs theory 6.0e-3; fixed a passband->baseband jammer-power factor-2 during testing); CSS dechirp/FFT & 1-bin CFO shift SF7/SF12; GPS C/A PSD -191.6 dBm/Hz. ALL PASS. Wrote spread-spectrum page.
- 2026-09-27 — Wrote comms_ofdm.py (CP exact recovery EVM -307 dB vs CP-short -19 dB; PAPR@1e-3 10.5 dB sim vs 10.4 approx for 52 sc; CFO ICI SIR 28.8/20.8/14.7 dB @ eps .02/.05/.1 = (pi eps)^2/3; Schmidl-Cox eps err <0.016; 802.11a/LTE/DVB-T numerology). ALL PASS. Wrote ofdm page.
- 2026-09-27 — Wrote comms_crc_framing.py (6 CRC check values; CCITT-16 = (x+1)*primitive, order 32767 -> HD4 to 32751 = Koopman; bursts<=16, odd weights; CRC-8 undetected 2^-8 MC; PER formula MC; sync-word Pfa/Pmiss table; PN9; ARQ; optimal frame length 855 bits H=80 p=1e-4; (10,8) erasure 10%->2.3%). ALL PASS. Fetched CCSDS 133.0-B-2 (Space Packet header: 3-bit version, type, sec-hdr flag, 11-bit APID, 2-bit seq flags, 14-bit seq count, 16-bit length; data 1-65536 octets) — WebFetch's summary wrongly said 2-bit version; pdftotext of the standard used. Wrote packet-framing-protocols page (uses Space Bar flight-software lessons for rocket frame design).
- 2026-09-27 — Wrote comms_choice_guide.py (comparison table, NF 2 dB sensitivities, relative free-space range incl. PA back-off; LoRa SF7 at equal rate ~= BPSK+K7 w/ 2 dB impl loss, and LoRa +3.8 dB from constant envelope). Wrote modulation-choice-guide page (confidence medium: GMSK-coherent and short-LDPC rows are estimates).
- 2026-09-27 — Wrote _index.md (reading order, page table, script table, domain FAQ, gaps) and _sources.md (grouped bibliography, [read] markers, discrepancies). Link check of all 13 files: 0 broken/unplanned links. Cross-checked domain 15 (Semtech 1 % PER 64 B criterion, LDRO 244 b/s at SF12, Doppler-rate limit) and 00 (Carson 99.9/99.4 %) — consistent; added LDRO note (SF12 Eb/N0 ~7.1 dB) and links to lora-impairments page. Final run: all 12 comms_*.py scripts OVERALL PASS. Task complete.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| S1 | Shannon 1948 BSTJ "A Mathematical Theory of Communication" (Harvard mirror PDF) | peer-reviewed | Thm 17 (§25, p.43 of reprint) C=W log(1+P/N); §19 2TW dimensions; §26 peak-power bound Thm 20; ideal signals approximate white noise | primary |
| S2 | MIT 6.02 F2012 ch.9 "Noise" (OCW) | lecture notes | bipolar BER = 0.5 erfc(sqrt(Es/N0)), SNR definitions §9.3-9.5 | good |
| S3 | CCSDS 131.0-B-5 TM Sync & Channel Coding Blue Book (Sep 2023) | standard | conv K=7 r=1/2 G=171/133 octal, puncture 2/3..7/8, >=3-bit soft; RS(255,223) E=16/(255,239) E=8, F(x)=x^8+x^7+x^2+x+1, I=1..5,8; turbo 16-state r=1/2..1/6 k=1784..8920; LDPC 7/8, AR4JA 1/2,2/3,4/5; ASM 1ACFFC1D; randomizer x^17+x^14+1 (legacy x^8+x^7+x^5+x^3+1) | authoritative |
| S4 | CCSDS 130.1-G-3 TM Sync & Channel Coding Summary of Concept and Rationale (Green Book, Jun 2020) | standard (informative) | BI-AWGN capacity asymptotes 0.2/-0.5/-0.8/-1.1/-1.6 dB for r=1/2,1/3,1/4,1/6,0; block-length penalty (100 vs 1000 bits ~1.3 dB); conv 5.5 dB gain @1e-5, +2 dB with RS, turbo within ~1 dB; hard decision >2 dB loss, 8-bit <0.2 dB; dfree=10 | authoritative |
| S6 | Jacobsen, "Understanding and Relating Eb/No, SNR, and other Power Efficiency Metrics", dsprelated.com/showarticle/168.php | practitioner article | Es=Ps/Rs, Ec=Es/k, Eb=Ps/Rb; Es/N0=SNR only when noise BW = Rs; factor-of-two pitfalls | good |
| S7 | Koopman CRC Zoo (users.ece.cmu.edu/~koopman/crc/, crc16.html) | academic web resource | implicit +1 notation; 0x8810 (CCITT 0x1021) & 0xc002 (0x8005) HD=4 to 32751 bits; 0xd175 HD=4 32751, HD=6 93; 0xac9a HD=5 241 | authoritative (Koopman CMU) |
| S8 | NTIA Manual Annex J "Guidance for Determination of Necessary Bandwidth" (Jan 2021) | standard/regulatory | Carson Bn=2M+2KD K=1; NBFM M=3k D=2.5k ->11 kHz; D=5k ->16 kHz; digital FM Bn=R/log2S+2KD (K 0.89-1.2); ITU-R SM.328 99% OBW K: CPFSK 1.62, MSK 1.28, GMSK BT1.0 1.15, 0.5 1.03, 0.3 0.91, 0.25 0.86; PSK/QAM Bn=2KR/log2S | authoritative |
| S9 | GPS.gov L1 C/A PRN Code Assignments, Jan 2026 edition (PDF, pdftotext) | official table | SBAS PRN G2 delays & first-10-chip octal values used to verify Gold-code generator | authoritative |
| S10 | CCSDS 133.0-B-2 Space Packet Protocol (June 2020), pdftotext | standard | primary header field widths §4.1.3 | authoritative |
| S5 | PySDR (Lichtman) ch. Pulse Shaping, Synchronization (pysdr.org) | lecture notes / online textbook | RC formula, BW=Rs(1+beta), beta 0.2-0.5, sync order coarse freq -> timing -> Costas -> frame; Nth-power FFT CFO range +-fs/(2N); M&M code | good, practitioner |

## Contradictions / discrepancies found
- MSK 99 % occupied bandwidth: NTIA Annex J (quoting ITU-R SM.328) gives K = 1.28 (Bn = 1.28 R) for unfiltered MSK, but the analytic MSK PSD integral (and Pasupathy 1979 / Sklar) gives 1.18 R; my simulation gives 1.19 R. GMSK K values in the same table (1.03/0.91/0.86) match simulation exactly. Page reports 1.18 and flags the ITU/NTIA number.
- CCSDS 130.1-G-3 quotes ~1.3 dB between 100- and 1000-bit blocks (Shannon 1959 sphere-packing bound, WER 1e-4, unconstrained input); PPV normal approximation gives 1.6 dB. Different bounds; both reported.
- K=7 r=1/2 soft Viterbi at BER 1e-5: my memory said 4.4 dB; union bound computed 4.17 dB, MC 1.4e-5 at 4.0 dB, CCSDS says 5.5 dB gain over 9.6 dB -> 4.1 dB. Pages use ~4.2 dB (unquantised soft); 3-bit quantisation adds ~0.2-0.3 dB.

## Knowledge gaps noticed (for later gap-filling)
- Turbo/LDPC/polar curves not re-simulated (quoted from CCSDS); short-block LDPC/polar and coherent-GMSK rows in the choice guide are estimates.
- Discriminator (G)FSK loss vs ideal NC-FSK vs h/BT not simulated.
- 802.11 EVM table and DVB-T carrier counts quoted from memory of standards.
- FM capture-ratio figures only from forum/marketing sources; land-mobile pre-emphasis/SINAD definitions not fetched.
- No measured rocket fade/burst statistics (interleaver/erasure examples illustrative).
- Crystal g-sensitivity (motor-burn vibration) for sync budgets.
- LoRa CR model ignores LDRO and soft decoding.

## Cross-domain notes (things other domains should cover/link)
- 15-lora: its lora-phy-css-math / lora-sensitivity pages give the Semtech SNR criterion (1 % PER, 64 B, CR4/5, SX1261/2 datasheet) and LDRO rate (SF-2 bits/symbol). My pages now cite that; my comms_lora_cr.py model ignores LDRO (noted on channel-coding page). Consistency: domain 15's ideal Eb/N0 5.7-6.7 dB at 1 % PER agrees with my 6.1/6.3 dB datasheet-derived numbers.
- 14-sdr-dsp (not yet written when this domain was done): pages linked from here — iq-complex-baseband, digital-filters-fir-iir, multirate-dsp-decimation-cic, fft-spectral-analysis-windows, nco-ddc-duc, software-demodulation, gnu-radio-and-software-stack. They should cover RRC/polyphase implementation, Farrow interpolators, FM/FSK/PSK demod code, and reference tools/verify/comms_*.py.
- 04/18: crystal & TCXO g-sensitivity (ppb/g) and temperature drift for rocket sync budgets (synchronization page gap).
- 19: ISM rules for FHSS/DSSS/LoRa (dwell time, channel counts, AS923 Singapore) referenced from spread-spectrum and choice guide.
- 11-radar: matched filter / pulse compression / Marcum Q detection here are consistent with radar detection pages; radar pages should link matched-filter-detection.md.
- 09: fade statistics for rocket links (roll nulls) would sharpen interleaver/erasure examples.

## Resume instructions (what the next agent should do if this one is interrupted)
- TASK COMPLETE (2026-09-27). All 11 planned pages + _index.md + _sources.md written in kb/10-comms-modulation/; 12 verification scripts tools/verify/comms_*.py all PASS.
- Future work = the gaps listed above (e.g. add comms_ldpc_bp.py, comms_fsk_discriminator.py; fetch IEEE 802.11 EVM table; rocket fade statistics from flight RSSI logs).
