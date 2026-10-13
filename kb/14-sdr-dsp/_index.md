# 14-sdr-dsp — Software-defined radio and digital signal processing

How a radio becomes software: sampling and aliasing (including bandpass/undersampling), complex (IQ) baseband and the impairments of real IQ front ends (DC spike, IQ imbalance), FFT spectral analysis and correct scaling to dBFS/Hz, FIR/IIR filter design and fixed-point effects, multirate processing (decimation, polyphase, half-band, CIC filters, channelisers), NCOs and digital down/up-conversion, software demodulators (FM, AM, SSB, FSK/GFSK, PSK, LoRa) with a complete packet pipeline, a survey of SDR hardware (RTL-SDR to USRP/RFSoC) with selection advice, the software stack (GNU Radio, UHD, libiio, SoapySDR, SigMF), and FPGAs for SDR. Written for building SDR ground stations for rocket LoRa/FSK telemetry, radar and direction-finding experiments, with every key number verified by a runnable script in `tools/verify/dsp_*.py`. Modulation/coding/synchronisation *theory* lives in [10-comms-modulation](../10-comms-modulation/_index.md); ADC device physics in 05; noise/dynamic range in [07](../07-noise-linearity/_index.md); LoRa specifics in 15; SDR-based test methods in 17; parts in 18.

## Reading order (beginner → advanced)
0. [SDR gain staging and reception recipes](sdr-gain-staging-and-reception-recipes.md) — *start here if you just bought an SDR*: how to set LNA/mixer/VGA gain (the 5–10 dB floor-lift rule), AGC, overload and phantom signals, bias-tee LNAs, and recipes for ADS-B, AIS, APRS, Meteor-M LRPT, the ISS, LoRa (gr-lora_sdr) and rtl_433; then read the theory pages below.
1. [Sampling, aliasing and bandpass sampling](sampling-aliasing-bandpass-sampling.md) — why the spectrum repeats every $f_s$, Nyquist zones, which undersampling rates work, anti-alias filters, noise folding, jitter.
2. [IQ signals and complex baseband](iq-complex-baseband.md) — why SDRs give complex samples, negative frequencies, IQ imbalance and images, the DC spike, offset tuning.
3. [FFT spectral analysis and windows](fft-spectral-analysis-windows.md) — bins, windows (ENBW, scalloping), dBFS/Hz scaling, averaging statistics, zero-padding, spectrograms.
4. [Digital filters — FIR and IIR](digital-filters-fir-iir.md) — design methods, length estimates, linear phase, bilinear transform, quantisation and fixed point.
5. [Multirate DSP — decimation, polyphase, half-band, CIC](multirate-dsp-decimation-cic.md) — the reference LoRa-on-RTL-SDR decimation chain, CIC derivation, channelisers.
6. [NCOs, DDC and DUC](nco-ddc-duc.md) — phase accumulators, spur rules, dither, CORDIC, real DDC/DUC chains.
7. [Software demodulation](software-demodulation.md) — FM/AM/SSB/FSK/PSK/LoRa in DSP, synchronisation loops, packet pipeline, APRS/rtl_433 examples.
8. [SDR hardware survey](sdr-hardware-survey.md) — specs explained, measured noise figures, device tables, what to buy for which job.
9. [GNU Radio and the software stack](gnu-radio-and-software-stack.md) — flowgraphs, drivers, apps, gr-lora_sdr, SigMF, overflows and throughput.
10. [FPGAs for SDR](fpga-for-sdr.md) — when to use one, DSP-slice budgets, fixed-point rounding, Zynq/RFSoC, open gateware, latency.
11. [SDR front-end protection and filtering](sdr-front-end-protection-and-filtering.md) — overload/blocking/IM/spurious responses, LNA-vs-SFDR trade, preselectors and skirts, limiters/TVS/arresters, bias tees, host noise.
12. [Signal identification and spectrum surveys](signal-identification-and-spectrum-survey.md) — unknown-signal workflow, cyclostationary symbol-rate and power-law tests, signal catalogue, launch-site 433/868/915 MHz survey with rtl_power.

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [sampling-aliasing-bandpass-sampling](sampling-aliasing-bandpass-sampling.md) | spectral-replication derivation, sinc reconstruction, alias formulas (real/complex), AAF order, bandpass-sampling windows $2f_H/n\le f_s\le2f_L/(n-1)$, spectral inversion, noise folding $10\log K$, jitter SNR, ZOH droop, 70 MHz IF / 433 MHz ISM / LoRa examples | mixed | high |
| [iq-complex-baseband](iq-complex-baseband.md) | complex envelope, quadrature mixing, analytic signal, IQ-imbalance image (IRR formula), DC-offset mechanisms, DC blocker, offset tuning and its image trade, low-IF RTL-SDR vs zero-IF, blind Gram–Schmidt correction, $f_s/4$ trick, ppm offsets | mixed | high |
| [fft-spectral-analysis-windows](fft-spectral-analysis-windows.md) | DFT bins, leakage, computed window table (CG, ENBW, scallop, sidelobes, 3/6 dB BW), PSD/dBFS/Hz scaling, processing gain, periodogram statistics (5.57 dB, −2.51 dB log bias), Welch, zero-padding, chirp spectrograms, SDR noise-figure measurement | mixed | high |
| [digital-filters-fir-iir](digital-filters-fir-iir.md) | window/LS/Parks–McClellan FIR, length estimates vs true minimum, linear-phase types, Butterworth/Chebyshev/elliptic, bilinear + prewarp, SOS vs direct form, coefficient bits (~6 dB/bit), accumulator growth, LoRa channel filter | mixed | high |
| [multirate-dsp-decimation-cic](multirate-dsp-decimation-cic.md) | decimation/interpolation spectra, noble identities, polyphase, half-band, CIC response/gain/register width/wrap-around/droop/compensation, multistage design, rational/Farrow resampling, PFB channeliser, AD9361 RX chain, LoRa-on-RTL-SDR chain | mixed | high |
| [nco-ddc-duc](nco-ddc-duc.md) | phase accumulator, worst-case truncation SFDR 6.02P − 3.92 dB, amplitude quantisation, dither, quarter-wave LUT, CORDIC, bit-true direct-sampling DDC, DUC, RTL2832U/AD936x/RFSoC chains, Doppler/ppm correction, CPFSK generation | mixed | high |
| [software-demodulation](software-demodulation.md) | polar FM discriminator, de-emphasis, AM, SSB, non-coherent vs discriminator FSK (loss numbers), QPSK with Gardner + Costas, LoRa dechirp = non-coherent M-FSK, CFO, packet pipeline PER curve, APRS/AX.25 and rtl_433 examples | mixed | high |
| [sdr-hardware-survey](sdr-hardware-survey.md) | spec meanings, Friis with an LNA, ADC-limited dynamic range, independent NF measurements, RX-only and transceiver tables (RTL-SDR V3/V4/V4L, Airspy, SDRplay, KrakenSDR, RX888, HackRF One/Pro, Pluto, Lime, bladeRF, USRP, AntSDR), selection by task and budget | mixed | medium |
| [gnu-radio-and-software-stack](gnu-radio-and-software-stack.md) | driver/abstraction/framework/app layers, GNU Radio 3.10 vs 4.0 RC, blocks/tags/messages/OOT/VOLK, UHD/libiio/SoapySDR, applications, gr-lora_sdr, SigMF, overflows, host throughput, latency | mixed | medium |
| [fpga-for-sdr](fpga-for-sdr.md) | when to use an FPGA, DSP48 budgets, time-sharing, accumulator/rounding/scaling, CORDIC hardware, Zynq + AD936x, RFSoC, RFNoC, openwifi, Maia SDR, HackRF Pro gateware, LiteX, latency, bit-true design flow | mixed | medium |
| [sdr-front-end-protection-and-filtering](sdr-front-end-protection-and-filtering.md) | field → dBm, nearby-TX levels, ADC clipping/blocking/IM/LO-harmonic responses, n-dB-per-dB pad test, LNA/SAW/pad cascades (NF, IIP3, SFDR), required preselection, Butterworth/Chebyshev skirts at SG/US blockers, limiter leakage vs SDR max input, TVS voltage/capacitance, bias-tee values, CM-ferrite estimate, node budget, recipes by use case | mixed | medium |
| [signal-identification-and-spectrum-survey](signal-identification-and-spectrum-survey.md) | ID workflow, fingerprints by family, \|x\|² symbol line = β/π (RRC), delay-product, x^M carrier lines, FSK discriminator², OFDM CP lag, LoRa SF from chirps, N^-3/2 estimator, Gamma-statistics occupancy thresholds, intercept probability, rtl_power hop plan, 24-row signal catalogue, receiver-artefact table, launch-site survey | mixed | medium |
| [sdr-gain-staging-and-reception-recipes](sdr-gain-staging-and-reception-recipes.md) | antenna-referred window and floor-lift penalty, librtlsdr R820T/R828D 29-step LNA/mixer table (VGA 16.3/26.5 dB), tuner vs RTL2832 AGC, 8-bit Monte-Carlo dynamic-range demo (quiet vs −45 dBm neighbour), masthead-LNA benefit vs ITU-R P.372 environment, phantom-signal tests (links front-end/signal-ID pages), recipes: ADS-B, AIS, APRS, Meteor-M LRPT (NOAA APT ended 2025), ISS, gr-lora_sdr, rtl_433 | mixed | medium |

## Verification scripts (all print PASS/FAIL; run `python3 tools/verify/<name>`)
| Script | Checks | Runtime |
|---|---|---|
| `dsp_sampling.py` | alias formulas vs FFT, bandpass-sampling rule vs brute force and multitone folding, spectral inversion, IF/ISM examples, noise folding, jitter SNR Monte-Carlo, ADC SNR, ZOH droop, sinc reconstruction, AAF order | < 1 s |
| `dsp_iq.py` | real vs complex spectra, quadrature down/up-conversion, IRR formula vs simulation, Gram–Schmidt correction vs record length, DC blocker width, offset tuning, analytic signal, ppm table | ≈ 1 s |
| `dsp_windows_fft.py` | window metrics from first principles vs harris (1978), half-bin amplitude error, PSD/dBFS/Hz scaling vs Welch, floor vs N, periodogram statistics, Welch variance and overlap, zero-padding vs resolution, processing gain, Parseval | ≈ 2 s |
| `dsp_filters.py` | Kaiser formulas, length estimates vs true Parks–McClellan minimum, LS vs equiripple, linear phase, bilinear prewarp, IIR orders, direct-form vs SOS quantisation, FIR coefficient bits, IIR group delay, LoRa channel filter | ≈ 2 s |
| `dsp_multirate_cic.py` | aliasing, polyphase equivalence, interpolation images, half-band structure, bit-exact wrap-around CIC, CIC droop/alias tables, compensator, full LoRa RTL-SDR chains, $f_s/4$ conversion, PFB channeliser vs brute force | ≈ 1 s |
| `dsp_nco.py` | accumulator resolution, phase-truncation SFDR (worst/odd-FTW/typical), LUT SNR, dither, quarter-wave LUT, CORDIC gain/convergence, bit-true DDC (integer CIC vs float pitfall), DUC SSB, CPFSK, ppm | ≈ 2 s |
| `dsp_demod.py` | FM/AM/SSB demodulators, NC-BFSK BER, discriminator FSK/GFSK loss, QPSK Gardner + Costas BER, LoRa SER vs exact M-FSK, LoRa CFO, CRC check values, packet PER curve | ≈ 4 s |
| `dsp_sdr_hardware.py` | Friis cascades for the ground station, ADC-limited dynamic range, data rates, FMCW resolution, KrakenSDR geometry, RX888 NF | < 1 s |
| `dsp_host_stack.py` | RTL cu8 conversion pitfall, SigMF round trip, host DSP throughput (machine-specific) | ≈ 1 s |
| `dsp_fpga_fixed.py` | bit-true FIR word lengths vs float, rounding biases, integer CORDIC FM discriminator, DSP-slice budgets, FPGA latency | < 1 s |
| `e3_frontend.py` | field strength, nearby-TX levels, cascades with rfcalc (NF/IIP3/SFDR), IM3 rejection, filter skirts, limiter/TVS/bias-tee budgets, pad test, antenna isolation (20/20) | < 1 s |
| `e3_signal_id.py` | β/π symbol line, delay product, power-law lines, GFSK discriminator line, OFDM CP, LoRa chirps, rtl_power plan, intercept MC, Gamma/ncx2 thresholds, N^-1.5 estimator (29/29) | ≈ 15 s |
| `e6_gain_staging.py` | floor-lift penalty, antenna-referred window vs gain, 8-bit Monte-Carlo dynamic range (scenarios A/B), librtlsdr gain-table algorithm, FM-/LO-harmonic landing table, masthead-LNA benefit vs P.372 noise | ≈ 1 s |

## Domain FAQ (top questions → page#section)
- *My SDR is set to 2.4 MS/s — why do I see 2.4 MHz and not 1.2 MHz?* → [sampling#Level 2](sampling-aliasing-bandpass-sampling.md#level-2--derivation-by-spectral-replication) (complex sampling), [IQ#Intuition](iq-complex-baseband.md#intuition-no-math)
- *Which sample rates can undersample my 70 MHz IF / the 433 MHz band?* → [sampling#Worked examples](sampling-aliasing-bandpass-sampling.md#worked-examples)
- *What is the spike in the middle of my SDR spectrum and how do I remove it?* → [IQ#Level 2](iq-complex-baseband.md#level-2--quadrature-demodulation-spectra-the-analytic-signal-and-impairments), [IQ#Worked examples](iq-complex-baseband.md#worked-examples)
- *Why is there a mirror copy of a strong signal?* → [IQ#TL;DR](iq-complex-baseband.md#tldr) (IRR formula)
- *Why does my noise floor move when I change FFT size? How do I get dBFS/Hz or dBm/Hz?* → [FFT#Level 2](fft-spectral-analysis-windows.md#level-2--leakage-window-metrics-scaling-statistics), [FFT#Worked examples](fft-spectral-analysis-windows.md#worked-examples)
- *Which window should I use?* → [FFT#TL;DR](fft-spectral-analysis-windows.md#tldr)
- *How many taps does my filter need?* → [filters#Level 2](digital-filters-fir-iir.md#level-2--fir-design-linear-phase-iir-design)
- *How do I get from 2.4 MS/s to a 125 kHz LoRa channel?* → [multirate#Worked examples](multirate-dsp-decimation-cic.md#worked-examples) (Example 1)
- *How does a CIC filter work and how many bits does it need?* → [multirate#Level 2](multirate-dsp-decimation-cic.md#level-2--spectra-polyphase-half-band-cic)
- *How many NCO phase bits for 80 dB SFDR?* → [NCO#Worked examples](nco-ddc-duc.md#worked-examples)
- *How do I demodulate FM/FSK/LoRa in software, and how good is a discriminator?* → [demodulation#Level 2](software-demodulation.md#level-2--derivations-and-the-synchronisation-loops)
- *Which SDR should I buy for LoRa monitoring / radar / DOA?* → [hardware#TL;DR](sdr-hardware-survey.md#tldr), [hardware#Worked examples](sdr-hardware-survey.md#worked-examples)
- *Does my SDR's noise figure matter behind an LNA?* → [hardware#Level 2](sdr-hardware-survey.md#level-2--comparing-receivers-quantitatively)
- *GNU Radio 3.10 or 4.0? What do "O" and "U" mean?* → [software stack#TL;DR](gnu-radio-and-software-stack.md#tldr), [#Level 3](gnu-radio-and-software-stack.md#level-3--drivers-devices-and-performance-engineering)
- *How should I record IQ?* → [software stack#TL;DR](gnu-radio-and-software-stack.md#tldr) (SigMF)
- *Do I need an FPGA?* → [FPGA#TL;DR](fpga-for-sdr.md#tldr)
- *What is this signal on my waterfall? What modulation/baud is it?* → [signal ID#Practical notes](signal-identification-and-spectrum-survey.md#step-by-step-identification-workflow), [#Level 2](signal-identification-and-spectrum-survey.md#level-2--cyclostationarity-and-the-symbol-rate-line-derivations)
- *How do I survey 433/915 MHz at a launch site?* → [signal ID Example 6](signal-identification-and-spectrum-survey.md#worked-examples)
- *Why does FM broadcast appear at 410 MHz? Does an LNA always help?* → [front end#Level 2](sdr-front-end-protection-and-filtering.md#level-2--mechanisms-and-derivations)
- *How should I set my RTL-SDR gain? Should AGC be on?* → [gain staging#Level 1](sdr-gain-staging-and-reception-recipes.md#level-1--the-window-the-floor-lift-and-the-gain-table)
- *How do I receive ADS-B / AIS / APRS / Meteor-M / the ISS / LoRa / 433 MHz sensors?* → [reception recipes](sdr-gain-staging-and-reception-recipes.md#practical-notes--reception-recipes)
- *Can I still receive NOAA APT?* → no — NOAA-15/18/19 decommissioned in 2025; [Meteor-M recipe](sdr-gain-staging-and-reception-recipes.md#recipe--meteor-m-lrpt-weather-images-noaa-apt-is-gone)
- *How do I protect my SDR from my own transmitter, ESD and lightning?* → [front end#Worked examples](sdr-front-end-protection-and-filtering.md#worked-examples)
- *How do I correct satellite Doppler on an SDR (Gpredict, hamlib), and is it needed for LoRa CubeSats?* → [09 satellite links](../09-propagation-link-budget/satellite-links-doppler-tracking.md#worked-examples)

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
Oppenheim & Schafer *Discrete-Time Signal Processing* (3e); Lyons *Understanding DSP* (3e); harris *Multirate Signal Processing for Communication Systems*; Crochiere & Rabiner *Multirate DSP*; Vaidyanathan *Multirate Systems and Filter Banks*; Proakis & Manolakis *DSP* (4e); Proakis & Salehi *Digital Communications* (5e); Rice *Digital Communications: A Discrete-Time Approach*; Razavi *RF Microelectronics* (2e); Meyer-Baese *DSP with FPGAs*; papers: Shannon 1949, Vaughan–Scott–White 1991 (bandpass sampling), harris 1978 (windows), Welch 1967, Cooley–Tukey 1965, Parks–McClellan 1972, Hogenauer 1981 (CIC), Nicholas–Samueli 1987 (NCO spurs), Volder 1959 (CORDIC), Gardner 1986, Costas 1956, Churchill 1981 / Anttila 2008 (IQ correction), Vangelista 2017 & Tapparel 2020 (LoRa); measurement reports: Libre Space Foundation SDR evaluation (2020), Rowetel (2018), KA7OEI (2023); PySDR; GNU Radio/UHD/libiio/SoapySDR/SigMF docs; ADI AD936x docs.

## Known gaps
- No bench measurements of specific SDRs' alias rejection, IRR, DC-spike level, IIP3 or blocking (only NF from independent reports); would suit domain 17.
- W5-E3 pages: RTL-SDR IIP3 (−10 dBm) in the front-end cascades is an illustrative assumption; HD Radio offsets, radiosonde baud and HF modem parameters in the signal catalogue are from general knowledge/sigidwiki; no team launch-site survey data yet.
- RTL2832U internal DDC/resampler and filter responses are undocumented publicly.
- Several documents could not be re-read this session (ADI MT-002/MT-085, Heinzel 2002 PDF, GNU Radio wiki, AMD PG269, harris' book sections); their content is re-derived or cross-checked numerically, and flagged in each page.
- Discriminator-FSK loss mapped for one filter configuration only; oversampled channelisers, Farrow resamplers, minimum-phase FIRs and IIR round-off noise gain described but not simulated.
- GNU Radio 4.0 (RC) architecture, GPU-based SDR processing and HLS flows not covered.
- Hardware prices/specs are 2026-09 snapshots and will date quickly.
