# 07-noise-linearity — Sources

Consolidated bibliography for the noise and linearity domain. Reliability tags per CONVENTIONS §3. "Used in" lists the pages that cite each item. Items marked *cited, not re-read* were not retrievable during the 2026-09-27 session; the facts used from them were re-derived and numerically verified.

## Textbooks
| # | Citation | Used for | Used in |
|---|---|---|---|
| T1 | D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — ch. 10 (noise and nonlinear distortion), §12.3 (LNA design, noise circles). (textbook) | noise temperature, lossy-line noise, cascade NF, IP3/dynamic range, noise circles | thermal, Friis, nonlinearity, dynamic range |
| T2 | B. Razavi, *RF Microelectronics*, 2nd ed., Prentice Hall, 2011 — ch. 2 (nonlinearity, noise, sensitivity, dynamic range), ch. 4 (architectures, zero-IF), ch. 6 (mixers), §8.7 (phase noise), ch. 9–10 (PLLs). (textbook) | power-series analysis, 9.6 dB result, cascaded IIP3, desensitisation, flicker in zero-IF, reciprocal mixing | all pages |
| T3 | T. H. Lee, *The Design of CMOS Radio-Frequency Integrated Circuits*, 2nd ed., Cambridge UP, 2004 — ch. 11 (noise), 12 (LNA design), 13 (distortion), 18 (phase noise). (textbook) | noise models, noise parameters, inductive degeneration, sweet spots, phase-noise theory | Friis, shot/flicker, nonlinearity, phase noise |
| T4 | C. A. Balanis, *Antenna Theory*, 4th ed., Wiley, 2016 — §2.17 antenna temperature. (textbook) | pattern-weighted brightness temperature, efficiency term | thermal |
| T5 | W. Kester (ed.), *Data Conversion Handbook*, Newnes/Analog Devices, 2005 — ch. 2 (ADC specs, aperture jitter, SNR). (textbook) *cited, not re-read* | SNR vs jitter, processing gain, ADC NF | phase noise, dynamic range |

## Peer-reviewed papers and standards
| # | Citation | Used for | Used in |
|---|---|---|---|
| P1 | J. B. Johnson, "Thermal agitation of electricity in conductors," *Phys. Rev.* 32, 97–109 (1928). (peer-reviewed) | measurement of thermal noise | thermal |
| P2 | H. Nyquist, "Thermal agitation of electric charge in conductors," *Phys. Rev.* 32, 110–113 (1928). (peer-reviewed) | transmission-line derivation, quantum form | thermal |
| P3 | H. B. Callen, T. A. Welton, "Irreversibility and generalized noise," *Phys. Rev.* 83, 34–40 (1951). (peer-reviewed) | fluctuation–dissipation theorem, zero-point term | thermal |
| P4 | R. Q. Twiss, "Nyquist's and Thevenin's theorems generalized for nonreciprocal linear networks," *J. Appl. Phys.* 26, 599–602 (1955). (peer-reviewed) | noise of general passive networks | thermal |
| P5 | W. Schottky, "Über spontane Stromschwankungen in verschiedenen Elektrizitätsleitern," *Ann. Phys.* 362(23), 541–567 (1918). (peer-reviewed) | shot noise | shot/flicker |
| P6 | H. T. Friis, "Noise figures of radio receivers," *Proc. IRE* 32(7), 419–422 (1944). (peer-reviewed) | noise figure definition, cascade formula | Friis, cascade |
| P7 | H. Rothe, W. Dahlke, "Theory of noisy fourpoles," *Proc. IRE* 44(6), 811–818 (1956). (peer-reviewed) | vn–in two-port noise representation | Friis |
| P8 | H. A. Haus et al., "IRE standards on methods of measuring noise in linear twoports, 1959," *Proc. IRE* 48(1), 60–68 (1960). (standard) | F = Fmin + (Rn/Gs)|Ys − Yopt|² | Friis |
| P9 | D. B. Leeson, "A simple model of feedback oscillator noise spectrum," *Proc. IEEE* 54(2), 329–330 (1966), doi:10.1109/PROC.1966.4682. (peer-reviewed) | Leeson's model | phase noise |
| P10 | A. Hajimiri, T. H. Lee, "A general theory of phase noise in electrical oscillators," *IEEE JSSC* 33(2), 179–194 (1998). (peer-reviewed) | ISF theory, flicker up-conversion | phase noise, shot/flicker |
| P11 | D. W. Allan, "Statistics of atomic frequency standards," *Proc. IEEE* 54(2), 221–230 (1966). (peer-reviewed) | Allan variance, flicker floor | shot/flicker |
| P12 | A. L. McWhorter, "1/f noise and germanium surface properties," in *Semiconductor Surface Physics*, U. Pennsylvania Press, 1957. (monograph) | trap model of 1/f noise | shot/flicker |
| P13 | F. N. Hooge, "1/f noise," *Physica B+C* 83(1), 14–23 (1976). (peer-reviewed) | mobility-fluctuation model | shot/flicker |
| P14 | A. A. M. Saleh, "Frequency-independent and frequency-dependent nonlinear models of TWT amplifiers," *IEEE Trans. Commun.* 29(11), 1715–1720 (1981). (peer-reviewed) | AM–AM/AM–PM model | nonlinearity |
| P15 | C. E. Shannon, "A mathematical theory of communication," *Bell Syst. Tech. J.* 27, 379–423, 623–656 (1948). (peer-reviewed) | Eb/N0 ≥ −1.59 dB bound | sensitivity |
| S1 | ITU-R Recommendation P.372-13 (09/2016), *Radio noise*. https://www.itu.int/rec/R-REC-P.372/en (standard) | Fa definition, eq. (1) operating noise factor, Pn = Fa + B − 204 dBW, Table 1 man-made/galactic coefficients (0.3–250 MHz), Tables 2–5 incl. 425 MHz measured values, galactic f^−2.75 scaling | thermal, Friis |
| S2 | IEEE Std 1139-2008, definitions for frequency and time metrology — random instabilities. (standard) | L(f) = Sφ(f)/2 | phase noise |
| S3 | IS-GPS-200, Navstar GPS interface specification: L1 C/A minimum received power −158.5 dBW. https://www.gps.gov/technical/icwg/ (standard) | GNSS C/N0 examples | cascade, sensitivity |

## Application notes, datasheets and lecture notes
| # | Citation | Used for | Used in |
|---|---|---|---|
| A1 | Keysight, *Fundamentals of RF and Microwave Noise Figure Measurements*, AN 57-1 (5952-8255E). https://www.keysight.com/us/en/assets/7018-06808/application-notes/5952-8255.pdf (app note) | NF definitions, attenuator NF = loss, Y-factor | thermal, Friis |
| A2 | Keysight, *Noise Figure Measurement Accuracy — The Y-Factor Method*, AN 57-2. (app note) *cited, not re-read* | second-stage correction, mixer DSB/SSB measurement | Friis |
| A3 | W. Kester, "Converting Oscillator Phase Noise to Time Jitter," ADI MT-008. https://www.analog.com/media/en/training-seminars/tutorials/MT-008.pdf (app note) *cited, not re-read (timeouts)* | integration method, SNR vs jitter | phase noise |
| A4 | W. Kester, "ADC Noise Figure — An Often Misunderstood and Misinterpreted Specification," ADI MT-052. https://www.analog.com/media/en/training-seminars/tutorials/MT-052.pdf (app note) *cited, not re-read (timeouts)* | ADC NF formula | dynamic range |
| A5 | Semtech, *SX1261/2 Data Sheet*, Rev 1.2 (June 2019), https://cdn.sparkfun.com/assets/6/b/5/1/4/SX1262_datasheet.pdf, and Rev 2.2 (Dec 2024). (datasheet) | LoRa/FSK sensitivity table, demodulator SNR table, IIP3 −5 dBm, blocking 88/90/99 dB, ACR 60/72 dB, CCR 5/19 dB, image attenuation 35/54 dB, Freq_drift_max = BW/(3·2^SF), TCXO recommendation | sensitivity, nonlinearity, dynamic range, phase noise, shot/flicker, cascade |
| A6 | Semtech, AN1200.22 "LoRa Modulation Basics" (2015). (app note) | sensitivity formula | sensitivity |
| A7 | Chengdu Ebyte, *E22-400TXXX Data Sheet* (2022), https://www.cdebyte.com/products/E22-400T33D. (datasheet) | E22-400T33D: SX1268, 410.125–493.125 MHz, 33 dBm, "−147 dBm at 2.4 kbps" (contradicted), 2.4–62.5 kbps | sensitivity |
| A8 | Chengdu Ebyte, *E220-900T30D User Manual*, https://www.cdebyte.com/products/E220-900T30D. (datasheet) | LLCC68, 850.125–930.125 MHz, 30 dBm, "−147/−148 dBm at 2.4 kbps" (contradicted) | sensitivity |
| A9 | u-blox, *MAX-M10S Data sheet* UBX-20035208, https://cdn.sparkfun.com/assets/7/5/9/a/a/MAX-M10S_DataSheet_UBX-20035208.pdf. (datasheet) | sensitivity figures, external gain limits 30/40 dB | Friis, cascade, sensitivity |
| A10 | Mini-Circuits, blog "Third-Order Intercept Point (IP3) and P1dB"; AN-00-009 "Understanding Mixers". https://www.minicircuits.com/app/AN00-009.pdf (app note) | IP3 definition and extrapolation | nonlinearity |
| L1 | A. Jha, "3rd-order intercept point," Columbia Integrated Systems Lab notes (2006). http://www.columbia.edu/~ky2181/EE6314/iip3AJ.pdf (lecture notes) | two-tone expansion, IIP3 = √(4a₁/3a₃) | nonlinearity |
| X1 | arXiv:2209.00287, "Correction to Friis noise factors" (2022). (preprint) | alternative in-situ definition — noted, not adopted | Friis |

## Verification scripts (this KB)
| Script | Verifies |
|---|---|
| `tools/verify/noise_thermal.py` | kT₀B, Planck ratio, resistor noise, lossy-passive Te vs slice model, P.372 tables, galactic scaling, Tsys, log-average bias, noise bandwidths |
| `tools/verify/noise_friis_nparams.py` | Friis, L·F rule, noise parameters from vn–in model (machine precision), noise circles, noise vs conjugate match, SSB/DSB |
| `tools/verify/noise_cascade.py` | cascade library + Monte-Carlo Friis check + two-tone cascade IIP3 check + level diagram + A/B/C example chains |
| `tools/verify/noise_ip3_twotone.py` | symbolic two-tone products, 9.64 dB, compression/blocking/XMOD relations, FFT measurements on 4 nonlinearities, IM2 slope |
| `tools/verify/noise_dynamic_range.py` | SFDR, ADC NF, processing gain, gain before ADC, desense, co-site blocking, pre-selection |
| `tools/verify/noise_phase_jitter.py` | L(f) integration (3 methods), ADC SNR, Leeson, reciprocal mixing, multiplication, EVM, FMCW, PLL in-band floor |
| `tools/verify/noise_sensitivity.py` | sensitivity formula, SX126x table, Eb/N0, bit-rate floor, EBYTE check, MDS, LoRa time on air |
| `tools/verify/noise_shot_flicker.py` | Poisson shot noise, 50 mV crossover, BJT en, 1/f per decade, zero-IF penalty, Allan deviation |

## Added by W5-E11 (volterra-series-and-nonlinear-analysis)
- S. A. Maas, *Nonlinear Microwave and RF Circuits*, 2nd ed., Artech 2003, ch. 4. (textbook)
- P. Wambacq, W. Sansen, *Distortion Analysis of Analog Integrated Circuits*, Kluwer 1998. (textbook)
- A. A. M. Saleh, *IEEE Trans. Commun.* 29(11), 1981 (TWT AM-AM/AM-PM; α_φ = 4.0033 — the 4.033 in the IEEE 802.16 slides is a dropped digit; see volterra page Open questions, W5-S18). (peer-reviewed)
- C. Rapp, Proc. 2nd ECSC, 1991 (solid-state PA model). J. Kim, K. Konstantinou, *Electron. Lett.* 37(23), 2001 (memory polynomial). D. R. Morgan et al., *IEEE Trans. SP* 54(10), 2006 (GMP). (peer-reviewed)
- Verification: `tools/verify/e11_volterra.py` (9/11).
