# 14-sdr-dsp — bibliography

Consolidated sources for the domain. Page keys: **SA** sampling, **IQ** iq-complex-baseband, **FFT** fft-spectral-analysis-windows, **FIL** digital-filters-fir-iir, **MR** multirate-dsp-decimation-cic, **NCO** nco-ddc-duc, **DEM** software-demodulation, **HW** sdr-hardware-survey, **SW** gnu-radio-and-software-stack, **FPGA** fpga-for-sdr, **FE** sdr-front-end-protection-and-filtering, **SID** signal-identification-and-spectrum-survey (FE/SID added by W5-E3, 2026-10-02). Reliability tags per CONVENTIONS §3. "Not re-read" marks items cited from the literature or search summaries without fetching the full text this session; their key claims were re-derived or reproduced numerically where possible (see each page's "How to simulate / verify").

## Textbooks
| Source | Used for | Pages |
|---|---|---|
| A. V. Oppenheim, R. W. Schafer, *Discrete-Time Signal Processing*, 3rd ed., Pearson (2010) — ch. 4 (sampling, rate change, polyphase), 5 (linear phase, group delay), 6 (structures, quantisation, limit cycles), 7 (filter design, Kaiser, equiripple), 8–10 (DFT, FFT, spectral analysis, STFT), 12 (Hilbert transforms) | derivations throughout | SA, IQ, FFT, FIL, MR |
| R. G. Lyons, *Understanding Digital Signal Processing*, 3rd ed., Prentice Hall (2011) — ch. 2 (sampling, bandpass sampling), 3–4 (DFT/FFT, windows), 5–6 (FIR/IIR), 8 (quadrature signals), 10 (sample-rate conversion, CIC), 12 (fixed point), 13 (DSP tricks: DC removal, fs/4, FM/AM demod) | practical methods | SA, IQ, FFT, FIL, MR, DEM |
| f. j. harris, *Multirate Signal Processing for Communication Systems*, Prentice Hall (2004); 2nd ed. River Publishers (2021) | FIR length rule $A/22$, polyphase, half-band, CIC, channelisers, DDC/DUC (sections not re-read) | FIL, MR, NCO, FPGA |
| R. E. Crochiere, L. R. Rabiner, *Multirate Digital Signal Processing*, Prentice Hall (1983) | multistage optimisation, structures, filter banks | MR |
| P. P. Vaidyanathan, *Multirate Systems and Filter Banks*, Prentice Hall (1993) | noble identities, polyphase, filter banks | MR |
| J. G. Proakis, D. G. Manolakis, *Digital Signal Processing*, 4th ed., Pearson (2007) — ch. 6, 9–10, 14 | bandpass sampling, structures, spectrum estimation | SA, FFT, FIL |
| J. G. Proakis, M. Salehi, *Digital Communications*, 5th ed., McGraw-Hill (2008) — §2.1, §4.5 | complex envelope; non-coherent BFSK/M-FSK error rates | IQ, DEM |
| M. Rice, *Digital Communications: A Discrete-Time Approach*, Pearson (2009) — ch. 7–8 | carrier/timing synchronisation, interpolators | DEM |
| B. Razavi, *RF Microelectronics*, 2nd ed., Prentice Hall (2011) — ch. 4 | receiver architectures, DC offset, IQ mismatch/IRR | IQ |
| M. Bellanger, *Digital Processing of Signals*, 3rd ed., Wiley (2000) | FIR length estimate (as commonly cited; checked numerically) | FIL |
| U. Meyer-Baese, *Digital Signal Processing with Field Programmable Gate Arrays*, 4th ed., Springer (2014) | fixed-point FIR/CIC/CORDIC on FPGAs | FPGA |

## Peer-reviewed papers and technical reports
| Source | Used for | Pages |
|---|---|---|
| C. E. Shannon, "Communication in the presence of noise," *Proc. IRE* 37(1):10–21 (1949) | sampling theorem | SA |
| R. G. Vaughan, N. L. Scott, D. R. White, "The theory of bandpass sampling," *IEEE Trans. SP* 39(9):1973–1984 (1991), doi:10.1109/78.134430 (abstract-level) | bandpass-sampling windows, pathology of minimum rate, noise folding | SA |
| A. Kohlenberg, "Exact interpolation of band-limited functions," *J. Appl. Phys.* 24(12):1432–1436 (1953) (not re-read) | second-order sampling | SA |
| F. J. harris, "On the use of windows for harmonic analysis with the DFT," *Proc. IEEE* 66(1):51–83 (1978) | window figures of merit (Table 1 compared numerically; small discrepancies logged) | FFT |
| A. H. Nuttall, "Some windows with very good sidelobe behavior," *IEEE Trans. ASSP* 29(1):84–91 (1981) (not re-read) | window corrections/extensions | FFT |
| J. F. Kaiser, R. W. Schafer, "On the use of the I0-sinh window for spectrum analysis," *IEEE Trans. ASSP* 28(1):105–107 (1980) (not re-read) | Kaiser window | FFT |
| J. F. Kaiser, "Nonrecursive digital filter design using the I0-sinh window function," *Proc. IEEE ISCAS* (1974) | Kaiser design formulas | FIL |
| G. Heinzel, A. Rüdiger, R. Schilling, "Spectrum and spectral density estimation by the DFT…," MPI Gravitationsphysik report (2002), https://holometer.fnal.gov/GH_FFT.pdf (PDF 403 this session) | $S_1$/$S_2$/NENBW scaling (re-derived) | FFT |
| P. D. Welch, "The use of FFT for the estimation of power spectra…," *IEEE Trans. Audio Electroacoust.* AU-15(2):70–73 (1967) | Welch averaging | FFT |
| J. W. Cooley, J. W. Tukey, "An algorithm for the machine calculation of complex Fourier series," *Math. Comp.* 19(90):297–301 (1965) | FFT | FFT |
| T. W. Parks, J. H. McClellan, "Chebyshev approximation for nonrecursive digital filters with linear phase," *IEEE Trans. Circuit Theory* CT-19(2):189–194 (1972); McClellan, Parks, Rabiner, *IEEE Trans. Audio Electroacoust.* AU-21(6):506–526 (1973) | equiripple design | FIL |
| O. Herrmann, L. R. Rabiner, D. S. K. Chan, "Practical design rules for optimum FIR lowpass digital filters," *BSTJ* 52(6):769–799 (1973) | length estimates | FIL |
| E. B. Hogenauer, "An economical class of digital filters for decimation and interpolation," *IEEE Trans. ASSP* ASSP-29(2):155–162 (1981) | CIC response, register growth, wrap-around, pruning | MR, NCO |
| J. Tierney, C. M. Rader, B. Gold, "A digital frequency synthesizer," *IEEE Trans. Audio Electroacoust.* AU-19(1):48–57 (1971) | NCO/DDS | NCO |
| H. T. Nicholas, H. Samueli, "An analysis of the output spectrum of DDFS in the presence of phase-accumulator truncation," *Proc. 41st IEEE Freq. Control Symp.*, pp. 495–502 (1987) (via search summaries; reproduced numerically) | worst-case truncation spur, 3.922 dB odd-FTW modification | NCO |
| J. E. Volder, "The CORDIC trigonometric computing technique," *IRE Trans. Electron. Comput.* EC-8(3):330–334 (1959) | CORDIC | NCO, FPGA |
| R. Andraka, "A survey of CORDIC algorithms for FPGA based computers," *FPGA '98*, pp. 191–200 (1998) | pipelined CORDIC | NCO, FPGA |
| F. E. Churchill, G. W. Ogar, B. J. Thompson, "The correction of I and Q errors in a coherent processor," *IEEE Trans. AES* AES-17(1):131–137 (1981) (not re-read) | Gram–Schmidt IQ correction | IQ |
| L. Anttila, M. Valkama, M. Renfors, "Circularity-based I/Q imbalance compensation in wideband direct-conversion receivers," *IEEE Trans. Veh. Technol.* 57(4):2099–2113 (2008) (not re-read) | blind/frequency-selective IQ compensation | IQ |
| A. A. Abidi, "Direct-conversion radio transceivers for digital communications," *IEEE JSSC* 30(12):1399–1410 (1995) (not re-read) | DC offset, LO leakage, even-order distortion | IQ |
| F. M. Gardner, "A BPSK/QPSK timing-error detector for sampled receivers," *IEEE Trans. Commun.* COM-34(5):423–429 (1986) | Gardner TED | DEM |
| J. P. Costas, "Synchronous communications," *Proc. IRE* 44(12):1713–1718 (1956) | Costas loop | DEM |
| L. Vangelista, "Frequency shift chirp modulation: the LoRa modulation," *IEEE SP Letters* 24(12):1818–1821 (2017) | LoRa dechirp demodulation | DEM |
| J. Tapparel, O. Afisiadis, P. Mayoraz, A. Balatsoukas-Stimming, A. Burg, "An open-source LoRa physical layer prototype on GNU Radio," *IEEE SPAWC* (2020), arXiv:2002.08208; https://github.com/tapparelj/gr-lora_sdr | gr-lora_sdr features and structure | SA, MR, DEM, SW |
| S. Kumar, F. Kaltenberger, "Latency measurements of USRP-based SDR platforms," EURECOM preprint (2018), https://sumiteurecom.github.io/latency-measurements-usrp.pdf | host-path latency | SW, FPGA |

## Independent measurement reports
| Source | Used for | Pages |
|---|---|---|
| A. Csete, S. Christiansen (Libre Space Foundation), "Evaluation of SDR Boards and Toolchains," v1.0 (2020), https://gitlab.com/librespacefoundation/sdrmakerspace/sdreval/-/raw/master/Report/pdf/Evaluation_of_SDR_Boards-1.0.pdf | measured NF, TX power, Pluto throughput, clock ppm | HW |
| D. Rowe, "Measuring SDR Noise Figure in Real Time," Rowetel (2018), https://www.rowetel.com/wordpress/?p=5867 | NF at 435 MHz with/without LNA | HW |
| KA7OEI, "Measuring signal dynamics of the RX-888 Mk2" (2023), http://ka7oei.blogspot.com/2023/09/measuring-signal-dynamics-of-rx-888-mk2.html | RX888 floor/clipping vs gain | HW |
| D. Estévez, "Running the AD9361 at 122.88 Msps" (2023), https://destevez.net/2023/02/running-the-ad9361-at-122-88-msps/ | bladeRF out-of-spec mode | HW |

## App notes, datasheets and manufacturer documentation
| Source | Used for | Pages |
|---|---|---|
| W. Kester, ADI MT-002 "What the Nyquist criterion means…" (2009) (PDF timeout) | Nyquist zones, AAF | SA |
| W. Kester, ADI MT-085 "Fundamentals of DDS" (2008); ADI "A Technical Tutorial on Digital Signal Synthesis" (1999); ADI technical article "An Almost Pure DDS Sine Wave Tone Generator" (search summaries) | DDS architecture, 3.922 dB result | NCO |
| Analog Devices, AD9361 (Rev E), AD9363 (Rev D), AD9364 datasheets (distributor mirrors); *AD9361 Reference Manual UG-570*; ADI developer docs "AD9361, AD9364 and AD9363 — general description" | RF specs; RX decimation chain HB3/HB2/HB1/FIR | MR, NCO, HW |
| Analog Devices, ADALM-PLUTO wiki (specs, customising, hacking) https://wiki.analog.com/university/tools/pluto | Pluto ranges, 4 MS/s streaming statement, AD9364 setting | MR, HW |
| Analog Devices, HDL reference designs https://github.com/analogdevicesinc/hdl; libiio https://github.com/analogdevicesinc/libiio (v1.0.0, 2026-09-22); pyadi-iio | Zynq + AD936x designs; IIO stack | SW, FPGA |
| Lime Microsystems, LMS7002M datasheet (MyriadRF wiki); Crowd Supply LimeSDR pages | LMS7002M specs, Lime boards | HW |
| Rafael Micro, R820T preliminary datasheet (2011; copy on rtl-sdr.com) | tuner NF, IF, image rejection | HW, IQ |
| Ettus Research, B200/B210 spec sheet; UHD manual (general, sync, stream args, E3xx, B200); product pages; RFNoC getting started; NI N210 EOL notice | USRP specs, O/U semantics, RFNoC | HW, SW, FPGA |
| Great Scott Gadgets, HackRF docs (hackrf_one, hardware_components, sampling_rate, setting_gain, gateware) and HackRF Pro page | HackRF One/Pro specs and gateware | HW, FPGA, NCO |
| RTL-SDR Blog: V3 user guide, V4 release and product pages, V4 end-of-line, V4L availability, buy page, "About RTL-SDR" | RTL-SDR specs, supply status, throughput | HW, MR |
| Airspy, SDRplay (incl. RSPdx-R2 datasheet V1.1, 2026), Nuand bladeRF, KrakenRF, MicroPhase AntSDR, RX-888 product pages | receiver/transceiver specs, prices (2026-09) | HW |
| AMD/Xilinx: Zynq-7000 Product Selection Guide (XMP097); UG479 (DSP48E1, via controlpaths.com summary); PG269 RF Data Converter (search summary); RFSoC-PYNQ 4x2 overview | FPGA resources, RFSoC | FPGA, NCO |
| Xilinx PG140 CIC Compiler; Intel AN455 CIC compensation (not re-read) | CIC practice | MR |

## Software documentation
| Source | Used for | Pages |
|---|---|---|
| GNU Radio: releases (3.10.12.0, 2025-02-20), gnuradio4 releases (4.0.0 RC3, 2026-09-22), runtime headers (block.h, sync_block.h, tags.h, throttle.h), wiki (via summaries), 3.10.0 release news | versions, block model, tags, throttle | SW |
| VOLK https://github.com/gnuradio/volk; gr-osmosdr https://github.com/osmocom/gr-osmosdr; SoapySDR wiki https://github.com/pothosware/SoapySDR/wiki | SIMD kernels; driver abstraction | SW |
| SigMF specification and schema https://github.com/sigmf/SigMF (v1.2.x) | recording format | SW |
| liquid-dsp https://github.com/jgaeddert/liquid-dsp; SDR++, GQRX, SDRangel, CubicSDR, SDR#, SDR Console, inspectrum, URH, direwolf, rtl_433 repositories/pages | applications and libraries | SW, DEM |
| SciPy `scipy.signal` documentation | design/verification tools | FIL, all scripts |
| G. Cook, CRC RevEng catalogue https://reveng.sourceforge.io/crc-catalogue/ | CRC check values (reproduced) | DEM |
| TAPR AX.25 v2.2 (1998), APRS Protocol Reference v1.0 (2000) (not re-read) | APRS example | DEM |

## Online textbooks and community sources
| Source | Used for | Pages |
|---|---|---|
| M. Lichtman, *PySDR: A Guide to SDR and DSP using Python*, https://pysdr.org (chapters: IQ Sampling, Frequency Domain, Synchronization, Pulse Shaping, Digital Modulation, Pluto/RTL-SDR/USRP in Python, IQ Files and SigMF) | practical SDR/DSP; 4/5 rule; throughput notes | SA, IQ, FFT, DEM, SW |
| superkuh, "rtl-sdr and GNU Radio…" http://superkuh.com/rtlsdr.html (community; search summary) | R820T low-IF vs E4000 zero-IF | IQ, NCO |
| RTL-SDR.com reviews/blog posts (SDR# guide, Pluto hack, RSP1A release, FobosSDR) | practical caveats | HW |
| DSP StackExchange Qs 672, 16330, 8785, 66390, 11560; ham.SE 20461; GNU Radio mailing list (2017-08) — via helper research (forum — anecdotal) | common confusions for "Common mistakes" sections | FFT, IQ, SW, HW |

## Added by W5-E3 (front-end protection; signal identification), 2026-10-02
| Source | Used for | Pages |
|---|---|---|
| W. A. Gardner, "Exploitation of spectral redundancy in cyclostationary signals," *IEEE Signal Processing Magazine* 8(2):14–36 (1991), doi:10.1109/79.81007 (citation verified; not re-read) | cyclostationarity, CAF/SCF definitions | SID |
| M. Lichtman, S. Brown, "Cyclostationary Signal Processing," *PySDR*, https://pysdr.org/content/cyclostationary.html (read) | CAF/SCF, \|x\| FFT shortcut, conjugate SCF at 2f_c ± α, OFDM CP cycle frequency, FSM/TSM/FAM | SID |
| P. Ciblat, P. Loubaton, E. Serpedin, G. B. Giannakis, *IEEE Trans. IT* 48(7):1922–1934 (2002) (abstract) | symbol-rate estimator consistency, N^-3/2 | SID |
| O. A. Dobre et al., *IET Communications* 1(2):137–156 (2007); A. Swami, B. M. Sadler, *IEEE Trans. Commun.* 48(3):416–429 (2000) (not re-read) | modulation classification surveys, cumulants | SID |
| Signal Identification Wiki, sigidwiki.com (**community wiki**; raw pages read 2026-09-29/10-02) | catalogue entries (AIS, APRS, POCSAG, FLEX, ADS-B, LoRa, GSM, DMR, TETRA, Iridium, HD Radio, FT8, ionosonde, ATSC, DAB, Zigbee, Sigfox, TPMS, RNSS) | SID |
| Osmocom rtl-sdr `src/rtl_power.c` (master; read) | hop plan, bins, crop, linear averaging, uncalibrated "dbm" | SID |
| 3GPP TS 36.211 (LTE numerology; general knowledge, checked arithmetically) | OFDM CP lengths | SID |
| RTL-SDR Blog V4 datasheet v1.0 (2024), https://www.rtl-sdr.com/wp-content/uploads/2024/12/RTLSDR_V4_Datasheet_V_1_0.pdf (read) | triplexer/notch, desense test method, bias tee 4.5 V/180 mA | FE, SID |
| Mini-Circuits VLM-33-S+ limiter datasheet, https://www.minicircuits.com/pdfs/VLM-33-S+.pdf (read) | limiter leakage and ratings | FE |
| Infineon ESD0P2RF-02LS datasheet (distributor summary) | 0.2 pF, ±5.3 V RF TVS | FE |
| rtl-sdr.com forum, "Can I use the SDR very close to the RF source?" (forum — anecdotal; search summary) | R820T +10 dBm, protection-diode clipping | FE |
| B. Razavi, *RF Microelectronics*, 2nd ed. (2011), ch. 2, 4 | non-linearity, desensitisation, harmonic mixing | FE |
| ARRL Handbook (general practice) | grounding, lightning, receiver protection | FE |
| This repository: `tools/verify/e3_frontend.py`, `tools/verify/e3_signal_id.py` | verification | FE, SID |

## Added by W5-E6 (2026-10-03) — sdr-gain-staging-and-reception-recipes (GS)
| Source | Supports | Page |
|---|---|---|
| Osmocom rtl-sdr `src/tuner_r82xx.c` and `src/librtlsdr.c` (master; read 2026-10-02) — R82xx LNA/mixer/VGA step tables, VGA 16.3 dB manual / 26.5 dB auto, 29-value gain list, `rtlsdr_set_agc_mode` | gain table, AGC | GS |
| RTL-SDR.com, "New R820T driver with LNA/mixer/VGA gain settings" (2014) (community blog) | independent stage control | GS |
| NOAA OSPO message MSG_20250820_1410 (NOAA-15/19 decommissioned 19/13 Aug 2025); NOAA NESDIS POES end-of-life notice (operator notices; search summaries) | NOAA APT ended | GS |
| USRadioguy Meteor status page (fetched 2026-10-02); sigidwiki LRPT (QPSK 72 kBd, 120 kHz) (community) | Meteor-M LRPT 137.9 MHz | GS |
| RTL-SDR.com, 9A4QV 137 MHz V-dipole article; "Meteor M2-3 now in orbit…" (community/manufacturer blog) | antenna, M2-3 antenna issue | GS |
| AMSAT "Amateur radio on the ISS"; ARISS notices (amateur-satellite organisations) | ISS 145.800/145.825/437.800/145.990 MHz | GS |
| aprs.world frequency list; hamradio.my (community — anecdotal) | APRS 144.390 MHz SG/MY | GS |
| gr-lora_sdr README (SF5–12; SF5/6 not SX126x-compatible) https://github.com/tapparelj/gr-lora_sdr (read 2026-10-02) | LoRa recipe | GS |
| rtl_433 README (bands, default 433.92 MHz, ≈ 380 listed protocols) https://github.com/merbanan/rtl_433 (read 2026-10-02) | rtl_433 recipe | GS |
| ITU-R P.372-13 Table 1 man-made noise lines (via 07/thermal-noise-and-noise-temperature) | masthead-LNA benefit | GS |
| This repository: `tools/verify/e6_gain_staging.py` (27/27 PASS) | verification | GS |
