# Research log W5-S7: Receiver, noise and DSP depth (GAP_REGISTER slice S7)
Status: complete (2026-10-13)
Owner scope (edit only): kb/07-noise-linearity/{thermal-noise-and-noise-temperature, dynamic-range-sfdr-blocking, nonlinearity-p1db-ip3-intermod, sensitivity-and-mds}.md; kb/17-test-measurement/phase-noise-measurement.md; kb/14-sdr-dsp/{software-demodulation, fft-spectral-analysis-windows}.md; tools/verify/s7_*.py; gaps/GAP_REGISTER.md (§3 → §5 rows for my items only).
Do NOT edit: 07/phase-noise-and-jitter, any _index.md, 07/volterra-series-and-nonlinear-analysis (W5-E11), other 17 pages (W5-S10).

## Plan
- [x] G-07-01 — 07/thermal-noise: new section "Radiometry" (total-power & Dicke radiometers, ΔT = Tsys/√(Bτ) derivation, gain-fluctuation term, beam efficiency, SDR sun/sky worked example, interferometry basics). Script tools/verify/s7_radiometer.py.
- [x] G-14-01 — 14/software-demodulation: new section "Receiver DSP features" (noise blanker, spectral subtraction / LMS ANR, auto-notch, IF shift / passband tuning, roofing filters). Script tools/verify/s7_noise_blanker.py (numpy demo on impulsive noise).
- [x] G-07-02 — 07/dynamic-range: plain-language boxes (superposition + selectivity; too close = saturation; cheap SDR vs communications receiver: preselection, IP3, reciprocal mixing), one number each.
- [x] G-14-02 — 14/fft: SNR estimation from a record, zoom FFT / sliding DFT, inter-bin estimators (parabolic, Jacobsen, Quinn) vs CRB, why random-data ASK spectrum looks triangular in dB, wavelets paragraph. Script tools/verify/s7_interbin_estimators.py.
- [x] G-07-04 — 07/sensitivity: S-meter calibration (S9 = −73 dBm HF, 6 dB/S-unit, VHF S9 = −93 dBm); 17/phase-noise-measurement: additive (residual) phase noise of amplifiers, "phase noise can be averaged out" myth.
- [x] G-07-03 — 07/nonlinearity: L3 Volterra derivation (kernels, 3rd-order kernel → IM3 with memory, AM–PM, memory polynomial as truncated Volterra), linking W5-E11's planned 07/volterra page. Possibly small script.
- [x] Close rows in GAP_REGISTER §5 (C88–C93), removed from §3.

## Log (append-only)
- 2026-10-12 — read CONVENTIONS, GAP_REGISTER (§3 rows 28/45/67/68/82/86, §6 S7, orchestrator notes), canonical-values. W5-E11 page 07/volterra-series-and-nonlinear-analysis not yet present (E11 in progress) — will link it as planned page (listed in INDEX? check).
- 2026-10-13 — sources: NRAO Essential Radio Astronomy ch.3 (radiometer eqs 3.154/3.158/3.162, T_A = A_eS/2k eq 3.48, η_B eq 3.58, fringe spacing §3.7.1); Learmonth quiet-Sun bulletins (410 MHz 25–50 sfu; 2024-01-11: 42 sfu). Wrote tools/verify/s7_radiometer.py (ALL PASS). G-07-01 DONE: 07/thermal-noise new subsection "Radiometry — when the noise is the signal" (L1/L2/L3 incl. interferometry), Example 7 (SDR Sun Y-factor, G/T), 6 design rows, 5 mistakes, TL;DR, 4 questions, sources 11–13. Note: my first mental estimate of Sun ΔT (~50 K) was wrong — script gives 61 K at 35 sfu.
- 2026-10-13 — found 06/agc-loops-and-receiver-gain-control (W5-E7) already covers NB/ALE/ANF conceptually with a CW demo (rf2_agc.py §H); so 14 section written as the SDR-implementation complement + LoRa case, linking 06, no duplication. Wrote tools/verify/s7_noise_blanker.py (ALL PASS). G-14-01 DONE: 14/software-demodulation new subsection "Receiver DSP features in software — noise blanker, noise reduction, auto-notch, IF shift, roofing" + TL;DR, 3 questions, 4 design rows, mistakes 10–12, verify bullet, sources 12–15 (Middleton 1977, Boll 1979, Ephraim–Malah 1984 cited not re-read).
- 2026-10-13 — wrote tools/verify/s7_interbin_estimators.py (ALL PASS): noise-free bias N=64: parabolic-rect 0.166, parabolic-Hann 0.016, Jacobsen 2.9e-4, Candan 7.3e-5, Quinn1/2 2.9e-4, Grandke-Hann 5e-8 bins; RMSE/√CRB at 20 dB/sample: parabolic-rect 25, parabolic-Hann 3.0, Jacobsen/Candan 1.53, Quinn1 1.27, Quinn2 1.13, Grandke-H 1.84; zoom FFT D=64 Nz=4096 → 3.8 Hz bins; SDFT exact (8.7e-14), damped float32 r=0.9999 err 4.8e-5; M2M4 QPSK 4000 sym unbiased ≥0 dB (std 0.39 dB at 0 dB; fails at −5 dB: mean −6.2, std 8 dB); spectral SNR est 2.97 vs 3.00 dB; OOK: carrier line = A²/4 (half the power), continuum (A²T/4)sinc², smoothed sidelobe envelope −13/−19/−25/−31 dB at 1/2/4/8 R_b (−20 dB/dec), 16-pt RBW fills first null (−52.6 → −4.5 dB). PAUSED before writing the 14/fft page section.
- 2026-10-13 (resumed) — G-14-02 DONE: 14/fft new subsection "Beyond the bin grid — sub-bin estimators, zoom FFT, sliding DFT, SNR estimation, data spectra, wavelets" (estimator table vs CRB, zoom FFT, SDFT, SNR estimation, OOK "triangular" explanation, wavelet paragraph); old L3 paragraph shortened to point to it; 5 questions, TL;DR, 6 design rows, mistakes 12–14, verify bullet, sources 11–18.
- 2026-10-13 — wrote tools/verify/s7_receiver_numbers.py (ALL PASS). G-07-02 DONE: 07/dynamic-range three "Plain-language box" blockquotes in Intuition (superposition+selectivity 126 dB; 1 W at 1 m ≈ +9 dBm, −35 dBm at 155 m; cheap SDR vs comms receiver: preselection, IIP3, RMDR 56 vs 96 dB (illustrative L), 8-bit ADC ceiling), 3 questions, 2 mistakes, verify bullet, source note. RMDR phase-noise values are illustrative (no sourced R820T PLL phase-noise number found) — recorded as gap.
- 2026-10-13 — G-07-04 DONE: 07/sensitivity Level 3 "S-meters and S-units" (IARU R.1 via Wikipedia/hamwaves; band noise in S-units; LoRa below S-meter), design row, mistake, question, source 9. 17/phase-noise-measurement new subsection "Additive (residual) phase noise of amplifiers and other two-ports" (Boudot & Rubiola arXiv:1001.2047: white floor, flicker b−1 table range, corner vs drive, cascade/parallel, split-source measurement with delay-mismatch leak), TL;DR, 3 design rows, 2 questions, verify, source 9. Myth "phase noise can be averaged out" was already called out in 17 Common mistakes (verified present 2026-10-12) — now cross-referenced from the new section.
- 2026-10-13 — wrote tools/verify/s7_volterra_memory.py (ALL PASS after adding a 2ω-reactive path: with a pure one-pole envelope filter and real a3 the IM3 sidebands are equal in magnitude — asymmetry needs complex P(Δ) AND a P(2ω) term, consistent with W5-E11's page). G-07-03 DONE: 07/nonlinearity Level 3 "Volterra series, memory effects and AM–PM" bridge paragraph linking E11's volterra page (no duplication), 2 questions, 2 mistakes, verify bullet, sources 9–11. Closed all six rows → GAP_REGISTER §5 C88–C93; §3 rows removed; change-log line added. build_index.py --check: 0 broken links, 0 missing sections (INDEX/FAQ rebuilt, 283 pages).

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| 1 | Condon & Ransom, Essential Radio Astronomy ch. 3 (NRAO online) | textbook | radiometer eqs, T_A of point source, η_B, fringe spacing | read via WebFetch (exact eq. numbers asked) |
| 2 | Learmonth daily quiet-Sun bulletins (BoM SWS list archive) | observatory data | 410 MHz 25–50 sfu | units not stated on page; sfu assumed |
| 3 | Boudot & Rubiola arXiv:1001.2047 (ar5iv) | preprint | amplifier residual PN, Table 1 b−1 | read |
| 4 | Wikipedia "S meter", hamwaves.com | secondary | IARU R.1 values | R.1 text not retrieved |
| 5 | Jacobsen–Kootsookos 2007; Candan 2011 (listings + forum transcription) | peer-reviewed / column | estimators | formulas re-derived and verified numerically |
| 6 | Quinn 1994/97, Grandke 1983, Jacobsen–Lyons 2003, Pauluzzi–Beaulieu 2000, Boll 1979, Ephraim–Malah 1984, Middleton 1977, Mallat 2009, Schetzen, Wambacq–Sansen, Vuolevi 2001, Kim–Konstantinou 2001, Morgan 2006 | peer-reviewed / textbooks | citations | cited, not re-read; all formulas used were verified by script |

## Contradictions / discrepancies found
- None between sources. Self-correction: my first hand estimate of the Sun's ΔT_A (≈ 50 K) was wrong; script gives 61 K at 35 sfu.
- Candan's tan(π/N)/(π/N) factor came from a forum transcription; confirmed numerically (bias 2.9e-4 → 7.3e-5 bin).

## Knowledge gaps noticed (for later gap-filling)
- Sourced phase noise of cheap SDR tuner PLLs (R820T/R828D, AD9363) — the RMDR numbers on 07/dynamic-range box 3 are illustrative.
- SDR gain stability (dB rms over minutes vs temperature) — limits the radiometry Example 7; bench measurement.
- Quiet-Sun flux at 915 MHz and burst statistics; IARU R.1 primary text; whether common transceivers follow 6 dB/S-unit.

## Cross-domain notes (things other domains should cover/link)
- 17/noise-figure-measurement could link 07/thermal-noise#radiometry for the sky-vs-load and Sun-noise G/T method (S10/E10 own 17 pages; not edited).
- 06/agc-loops receiver DSP section could link back to 14/software-demodulation#receiver-dsp-features (06 owned by W5-E7).
- 12/adaptive-beamforming-doa (KrakenSDR) could cite the interferometer fringe/correlator results.

## Resume instructions
Task complete. Nothing to resume. Scripts: tools/verify/s7_radiometer.py, s7_noise_blanker.py, s7_interbin_estimators.py, s7_receiver_numbers.py, s7_volterra_memory.py (all ALL PASS).
