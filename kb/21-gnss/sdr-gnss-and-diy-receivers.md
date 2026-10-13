---
title: SDR GNSS and DIY receivers — GNSS-SDR, SoftGNSS, Pocket SDR, RTL-SDR/HackRF reception, MAX2769/MAX2771 front ends, gps-sdr-sim (conducted only — never radiate) and a learning path to your own receiver
domain: 21-gnss
slug: sdr-gnss-and-diy-receivers
tags: [gnss, sdr, software-receiver, gnss-sdr, softgnss, pocket-sdr, rtklib, rtl-sdr, r820t2, hackrf, bladerf, pluto, usrp, max2769, max2771, front-end, bias-tee, tcxo, if-sampling, 2-bit-adc, gps-sdr-sim, gnss-simulator, spoofing-legal, conducted-test, learning-path]
prerequisites: [gnss-receiver-architecture-acquisition-tracking.md, gnss-signals-and-codes.md, ../14-sdr-dsp/sdr-hardware-survey.md, ../14-sdr-dsp/iq-complex-baseband.md]
related: [gnss-interference-jamming-spoofing.md, gnss-on-rockets-dynamics-and-limits.md, ../14-sdr-dsp/gnu-radio-and-software-stack.md, ../18-components-parts/rf-transceiver-ics.md, ../18-components-parts/lna-pa-gain-block-mmics.md, ../08-antennas/gnss-antennas.md, ../19-regulations-safety/spectrum-allocation-ism-bands.md, ../20-projects-recipes/gnss-front-end-design.md]
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# SDR GNSS and DIY receivers

## Questions this page answers
- Can I receive GPS with an RTL-SDR or HackRF, and what else do I need?
- What software turns recorded samples into a position (GNSS-SDR, SoftGNSS, Pocket SDR, RTKLIB)?
- How do dedicated GNSS front-end chips (MAX2769B, MAX2771) differ from a general-purpose SDR?
- How would I build my own GNSS receiver for learning — what are the steps?
- Is it legal to transmit simulated GPS signals with gps-sdr-sim? How do I test a receiver safely?
- What sample rate, bit depth and oscillator accuracy do I need?
- Could a software receiver be better than a u-blox on a rocket?

## TL;DR
- **A GNSS SDR = active antenna + (LNA/SAW) + RF front end/SDR + software** doing acquisition, tracking, navigation-message decoding and PVT — exactly the blocks of the [receiver page](gnss-receiver-architecture-acquisition-tracking.md), but in your code.
- **RTL-SDR** (R820T2 tuner, 24–1766 MHz, ≈ 2.4 MS/s, 8-bit IQ) covers L1/L2/L5 and its 2.048 MS/s rate just holds the C/A main lobe; it needs a **bias-tee-powered active antenna** (or an LNA + SAW at the antenna) and a **TCXO** (a 25 ppm crystal puts L1 39 kHz off). Fed straight from a passive patch it reaches only ≈ 41.5 dB-Hz at the minimum signal level; with an LNA at the antenna ≈ 50.6 dB-Hz (`tools/verify/gnss_sdr_frontend.py`, assumed SDR NF 6 dB).
- **GNSS front-end ICs** deliver 1–3-bit IF/IQ samples from a GNSS-optimised chain: MAX2769B (L1, cascaded NF ≈ 1.4–1.5 dB, IF filters ≈ 2.5–24 MHz) [ref. parts page]; **MAX2771** (multiband L1/L2/L5) — used by **Pocket SDR** (T. Takasu, author of RTKLIB): 2/4/8-channel front ends, L1 band 1525–1610 MHz or L2/L5/L6 1160–1290 MHz, IF bandwidth up to 36 MHz, up to 32–48 MS/s, Cypress EZ-USB FX2/FX3, software in Python/C/C++ supporting almost every civil signal (GPS L1C/A, L1C, L2C, L5; GLONASS FDMA + CDMA; Galileo E1/E5/AltBOC/E6; QZSS incl. L6; BeiDou B1I/B1C/B2a/B2I/B2b/B3I; NavIC; SBAS) [1].
- **Software**: GNSS-SDR (C++, GPL-3.0; GPS L1 C/A, Galileo E1, GLONASS, BeiDou B1I/B3I, L2C, L5/E5a, E6B…; RTL-SDR via gr-osmosdr, USRP, Pluto/FMCOMMS, files) [2]; Borre et al.'s **SoftGNSS** (MATLAB, the classic teaching receiver) [3]; Pocket SDR [1]; RTKLIB for PVT/RTK/PPK from observables.
- **gps-sdr-sim** generates baseband GPS L1 C/A for HackRF, bladeRF, Pluto, USRP [4]. **Transmitting GNSS signals over the air is illegal without authorization and dangerous (aviation, timing infrastructure)**; its own README connects the SDR TX to the receiver through a **DC block and a 50–60 dB fixed attenuator** — cabled, conducted only, ideally inside a shielded box [4].
- **For rockets**: a software receiver lets you choose loop bandwidths, add IMU/trajectory aiding and remove the 500 m/s firmware limit — but a receiver *designed or modified* for airborne use above 600 m/s is export-controlled (EAR 7A105) ([rocket page](gnss-on-rockets-dynamics-and-limits.md#level-3--export-controls-and-how-u-blox-implements-limits)). Recording raw IF on a rocket and processing it on the ground is a research-grade alternative.

## Intuition (no math)
A u-blox module hides thousands of correlators and a navigation filter behind a serial port. A software-defined GNSS receiver puts the analogue part (antenna, LNA, filter, mixer, ADC) in hardware and everything after the ADC in code you can read and change. The analogue part needs care because the signal is so weak — that's why dedicated GNSS front-end chips exist: they have a low noise figure at 1.5 GHz, the right IF filters, and they deliberately output only 1–3 bits per sample (enough, as quantisation costs only ≈ 0.5–2 dB) to keep the data rate low. A general-purpose SDR like an RTL-SDR works too if you put a good LNA in front and use a stable oscillator.

Then you write (or run) the classic pipeline: FFT-based acquisition to find each satellite's code phase and Doppler, tracking loops to follow them, bit and frame synchronisation, ephemeris decoding, pseudoranges and a least-squares fix. Each step is a few hundred lines of Python — a superb way to understand what your flight-computer GNSS is doing.

## The math

### Level 1 — the hardware budget
**Noise cascade** (`gnss_sdr_frontend.py`, T_ant = 100 K, signal −125.5 dBm):

| Chain | T_sys | C/N₀ |
|---|---|---|
| passive patch → 2 m coax (1.5 dB) → SDR (NF 6 dB assumed) | 1441 K | 41.5 dB-Hz |
| patch → LNA (NF 0.8 dB, 20 dB) → SAW (1.5 dB) → coax → SDR | 179 K | 50.6 dB-Hz |
| patch → SAW (1 dB) → LNA → SAW → coax → SDR | 274 K | 48.7 dB-Hz |
| commercial active antenna (28 dB, NF 2 dB) → 5 m coax (3 dB) → SDR | 273 K | 48.7 dB-Hz |

A SAW ahead of the LNA costs ≈ 2 dB here but protects against your own transmitters ([interference page](gnss-interference-jamming-spoofing.md)). LNA candidates (BGA524N6, MAX2659, AT2659) are in [LNA parts](../18-components-parts/lna-pa-gain-block-mmics.md); filters in [filter parts](../18-components-parts/filter-parts-saw-ceramic-ltcc.md).

**Sampling**: complex sampling must cover the main lobe(s): C/A 2.05 MS/s; BOC(1,1) 4.09 MS/s; full E1 CBOC 24.6 MS/s; L5/E5a 20.5 MS/s; B1I + L1 + G1 together ≈ 47 MS/s. Data rates: RTL-SDR cu8 at 2.048 MS/s = 4.1 MB/s (0.25 GB per minute); 2-bit IQ at 4.092 MS/s = 2.05 MB/s; HackRF ci8 at 10 MS/s = 20 MB/s (script) ([sampling](../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md)).

**Oscillator**: offset $\Delta f = \epsilon f_{L1}$: 0.5 ppm → 0.79 kHz; 1 ppm → 1.58 kHz; 25 ppm → 39.4 kHz (script) — either use a TCXO SDR (RTL-SDR Blog V3/V4 have 1 ppm TCXOs per the [hardware survey](../14-sdr-dsp/sdr-hardware-survey.md)) or widen the acquisition search. The code rate is off by the same fraction (25 ppm → 25.6 chips/s), which matters for long coherent integrations and must be corrected in tracking.

### Level 1½ — the three budget sums, algebra only
- **Noise temperatures add.** $T_{sys} = T_{ant} + T_1 + T_2/G_1 + \dots$, with $T = 290(F-1)$ for each stage. The gain of the first stage divides the noise of everything behind it.
- **C/N0 from T_sys.** $kT$ in dBm/Hz is $-198.6 + 10\log T$, so $C/N_0 = P_r + 198.6 - 10\log T_{sys}$ (dB-Hz).
- **Sampling and storage.** The complex sample rate must cover the main lobe (2 × the chip rate for BPSK). Bytes per second = sample rate × bytes per complex sample.
- **Acquisition search.** Number of cells = (Doppler span ÷ bin width) × code phases (2 per chip).

*Worked number (verified, `tools/verify/s18b_level15_numbers.py`).* A simplified chain without the SAW and coax of the table: patch $T_{ant}$ = 100 K, LNA with NF 0.8 dB (58.7 K) and 20 dB gain, then an SDR with NF 6 dB (865 K). $T_{sys}$ = 100 + 58.7 + 865/100 = **167.3 K**, so C/N0 = −125.5 + 198.6 − 22.2 = **50.9 dB-Hz**. Without the LNA, $T_{sys}$ = 965 K and C/N0 = **43.3 dB-Hz**. With a 1 ppm TCXO the search spans ±(5 + 1.58) kHz = 13.2 kHz. In 500 Hz bins that is 27 bins × 2046 half-chip code phases = **55 242 cells** per satellite.

### Level 2 — the software pipeline (what each stage must do)
1. **Capture**: record 30–60 s of IQ (or IF) with the antenna under open sky; note the exact centre frequency, sample rate, format and IF.
2. **Acquisition**: for each PRN, parallel code-phase FFT search over Doppler bins (± 5 kHz + oscillator offset, 500 Hz bins for 1 ms coherent), non-coherent accumulation; threshold on peak/second-peak or a CFAR test. Expected sensitivity: ≈ 44 dB-Hz for 1 ms, ≈ 36 dB-Hz for 10 × 1 ms non-coherent (`gnss_acquisition.py`).
3. **Tracking**: carrier NCO + Costas PLL (2nd order, B_n ≈ 15–25 Hz while pulling in, then narrower) with FLL assist; code NCO + early–prompt–late correlators and a normalised E−L DLL (B_n ≈ 1–2 Hz, carrier-aided). Lock detectors; C/N₀ estimator (e.g. narrow-band/wide-band power ratio).
4. **Bit and frame sync**: 20-ms bit edges (histogram of prompt sign changes), LNAV preamble 10001011 every 6 s with parity check; extract TOW from the HOW word.
5. **Ephemeris decoding**: subframes 1–3 → orbit and clock; apply satellite clock, relativistic and group-delay terms per IS-GPS-200.
6. **Observables**: pseudorange from the transmit time (TOW + code phase + bit/ms counts) at a common receive epoch; Doppler; carrier phase.
7. **PVT**: least squares with clock bias (`gnss_dop_errors.py`), Klobuchar and tropospheric models; or export RINEX and use RTKLIB.

Borre et al.'s book walks through all seven stages in MATLAB with a recorded data set [3]; GNSS-SDR implements them as GNU Radio blocks configured by a text file and can run in real time with RTL-SDR/USRP/Pluto sources or on files [2]; Pocket SDR provides `pocket_acq`, `pocket_trk` and PVT utilities and a real-time GUI/web front end [1].

### Level 3 — front-end architectures and advanced uses
**Dedicated GNSS front ends.** Typical structure: LNA → image-reject mixer to a low IF (a few MHz) → selectable IF filter → AGC → 1–3-bit ADC with sign/magnitude outputs, plus a PLL synthesiser from a 10–40 MHz TCXO. Advantages over a general SDR: NF ≈ 1.5 dB including LNA, GNSS-matched filters, low-bit outputs, low power. Classic parts: Maxim/ADI **MAX2769B** (L1 GPS/Galileo/GLONASS; via [transceiver ICs](../18-components-parts/rf-transceiver-ics.md)), **MAX2771** (multiband; Pocket SDR's FE uses it — the repository ships its datasheet in the FE_2CH hardware folder [1]); others mentioned in the literature (NTLab NT1065 four-channel, SiGe SE4110L used in early teaching samplers) were not checked in this pass.

**General SDRs**: HackRF (1–6 GHz, 8-bit, ≤ 20 MS/s), bladeRF/USRP/Pluto (12-bit, tens of MS/s) can capture wide multi-band GNSS (e.g. full E1 or L5) and transmit (for simulators — conducted only). See the [hardware survey](../14-sdr-dsp/sdr-hardware-survey.md) for specs and supply status.

**Raw IF recording on a rocket.** A small front end (e.g. a 2-channel MAX2771 board) writing 2-bit IQ at 4–8 MS/s (2–4 MB/s) to an SD card captures everything the antenna saw; post-flight you can run tracking loops of any bandwidth, aided by the IMU-integrated trajectory (a deep/vector-tracking experiment) — the DLR sounding-rocket approach of trajectory aiding, done offline [5]. Export-control caution applies to receivers designed for > 600 m/s airborne use; processing your own recorded data for research is a grey area — check before publishing raw data (DLR could not release theirs [6]).

**Simulators and spoofing research.** gps-sdr-sim builds the GPS L1 C/A signal for a given broadcast ephemeris (RINEX nav file), static location or user-motion file (ECEF/LLH at 10 Hz, up to 30 000 samples by default), and writes 1/8/16-bit IQ at 2.6 MS/s by default (2.5 MS/s for USRP2) [4]. With a user-motion file it can play a rocket trajectory into a receiver under test — the cheapest way to test u-blox behaviour above 500 m/s and through high jerk *on a cable*. The same tool is what makes spoofing easy; that is why GNSS receivers implement spoofing detection ([interference page](gnss-interference-jamming-spoofing.md)).

## Design equations & rules of thumb

| Item | Rule / value | Source |
|---|---|---|
| Put the LNA at the antenna | NF of the first stage dominates; ≈ +9 dB C/N₀ vs bare SDR | script |
| Complex sample rate | ≥ main-lobe width (2.05 MS/s C/A; 4.09 BOC(1,1); 20.5 L5) | script |
| ADC bits | 2 bits ≈ 0.55 dB loss; 1 bit 1.96 dB | `gnss_acquisition.py` |
| Oscillator | ≤ 1 ppm TCXO, or widen search by ±ε·f_L | script |
| Data rate | f_s × bits/sample × 2 (IQ) / 8 bytes/s | arithmetic |
| Simulator testing | cabled, DC block + attenuator to ≈ −130 dBm; never radiate | [4] |

## Worked examples
**1 — First GPS fix with an RTL-SDR (learning project).** Hardware: RTL-SDR with TCXO and bias-tee (enable it), a 3–5 V active GNSS antenna on a window sill or roof. Record: centre 1575.42 MHz, 2.048 MS/s, gain fixed (AGC off), 60 s → 250 MB. Process with GNSS-SDR's RTL-SDR configuration (GPS L1 C/A, 8 channels) or SoftGNSS after converting to its format. Expect 6–10 satellites at 38–48 dB-Hz; first fix after ≈ 30–40 s of data (the ephemeris wait — [TTFF page](ttff-agps-almanac-ephemeris.md)).

**2 — A Python acquisition demo from the KB.** `tools/verify/gnss_acquisition.py` already contains a C/A generator and an FFT acquisition; point it at an RTL-SDR file (convert cu8 with $(u-127.5)/127.5$ — [software stack](../14-sdr-dsp/gnu-radio-and-software-stack.md)), resample to 4.092 MS/s or regenerate the replica at 2.048 MS/s, add the oscillator offset to the Doppler search, and print peak/mean ratios per PRN. Satellites above ≈ 40 dB-Hz appear with 1 ms coherent; weaker ones need 10–20 ms non-coherent.

**3 — Testing the flight GNSS through a simulated boost.** Generate a user-motion file for a 15 g, 3 s burn to 600 m/s with gps-sdr-sim; play it from a HackRF at minimum TX gain through a DC block and enough fixed attenuation to land near −130 dBm per satellite at the u-blox RF input (measure the TX level first; e.g. −10 dBm out needs ≈ 120 dB — the README's 50–60 dB fixed attenuator assumes a much lower TX output) [4]; put the receiver and attenuator chain in a shielded box. Log NAV-PVT and observe the 500 m/s cut-off and loss of lock at ignition. Note that gps-sdr-sim models only GPS L1 C/A.

## Practical notes
- **Bias tee**: the active antenna needs DC on the coax (RTL-SDR Blog bias tee, or an external bias-T); a DC block is mandatory before any SDR TX port or test equipment that can't take DC.
- **Gain**: set fixed gain so the noise floor sits a few dB above the SDR's own noise; an AGC chasing noise does no harm, but strong out-of-band signals (cellular, your LoRa) can saturate the RTL-SDR — add a GNSS SAW/bandpass.
- **USB throughput and dropped samples** corrupt tracking; check sample counters and use a fast disk.
- **Licensing**: GNSS-SDR GPL-3.0 [2]; Pocket SDR switched its default FFT backend to PocketFFT (BSD) from FFTW3 (GPL) for licensing reasons [1].
- **Legality** (Singapore and elsewhere): GNSS bands are receive-only for the public; Singapore lists GNSS receivers as exempt equipment, not transmitters ([spectrum allocation](../19-regulations-safety/spectrum-allocation-ism-bands.md)). Radiating a simulator or repeater, even weakly, can disrupt aircraft and network timing for kilometres ([J/S numbers](gnss-interference-jamming-spoofing.md#level-1--interference-to-signal-arithmetic)).

## Common mistakes & misconceptions
- **"I can see GPS on the waterfall."** You can't — it's ≈ 18 dB below the noise in its band; you see it only after correlation.
- **"Any SDR works without an LNA."** Bare SDRs have NFs of several dB plus coax loss; put ≥ 20 dB of low-NF gain at the antenna.
- **"A 1 ppm TCXO means no Doppler search."** 1 ppm is still 1.6 kHz at L1 — you must search, just less widely.
- **"A 50 dB attenuator makes over-the-air simulator use safe."** No: the attenuator is for a *cabled* connection; any radiation is unlawful.
- **"Software receivers are automatically better on rockets."** Only if you implement high-dynamics tracking (wide 3rd-order loops, FLL assist, aiding) — and mind export controls.

## How to simulate / verify
- `python3 tools/verify/gnss_sdr_frontend.py` — front-end cascades and C/N₀, sample/data rates, oscillator offsets, simulator attenuation. ALL PASS.
- `python3 tools/verify/gnss_acquisition.py` — FFT acquisition and quantisation loss; `gnss_tracking_loops.py` — loop design; `gnss_signals_link.py` — C/A code generator.
- Recorded data sets: GNSS-SDR and Borre's book provide sample files; Pocket SDR provides IF capture and offline tools [1][2][3].

## Open questions / gaps
- RTL-SDR R820T2 noise figure at 1.5 GHz was assumed (6 dB), not measured; see [hardware survey](../14-sdr-dsp/sdr-hardware-survey.md) and [NF measurement](../17-test-measurement/noise-figure-measurement.md).
- MAX2771 datasheet values (NF, IF filters, ADC modes) were not extracted in this pass.
- The planned project page [GNSS front-end design](../20-projects-recipes/gnss-front-end-design.md) (domain 20) should build on this page.

## Sources
1. T. Takasu, *Pocket SDR — An Open-Source GNSS SDR*, ver. 0.20 (README, 2026-08-08) and repository (FE_2CH/HW incl. MAX2771 datasheet; FE 8CH 3-bit samples). https://github.com/tomojitakasu/PocketSDR (open-source project, primary)
2. GNSS-SDR project, README (main branch) — supported signals by band, GPL-3.0, front-end interfaces (gr-osmosdr, USRP, FMCOMMS2/Pluto, files). https://github.com/gnss-sdr/gnss-sdr (open-source project, primary)
3. K. Borre, D. M. Akos, N. Bertelsen, P. Rinder, S. H. Jensen, *A Software-Defined GPS and Galileo Receiver: A Single-Frequency Approach*, Birkhäuser, 2007 — SoftGNSS MATLAB receiver, front-end and acquisition/tracking chapters. (textbook; general reference)
4. T. Ebinuma, *gps-sdr-sim* README — supported SDRs (Pluto, bladeRF, HackRF, USRP), user-motion files (10 Hz), 2.6 MS/s default, 1/8/16-bit IQ, "TX port … connected to the GPS receiver under test through a DC block and a fixed 50-60dB attenuator". https://github.com/osqzss/gps-sdr-sim (open-source project, primary)
5. M. Markgraf, O. Montenbruck et al., "A Low Cost GPS System for Real-Time Tracking of Sounding Rockets," 2001 — trajectory aiding concept. https://archive.org/details/nasa_techdoc_20010069267 (conference)
6. B. Braun et al., "First Test of a Multi-Constellation, Multi-Frequency GNSS Receiver on Board a Sounding Rocket," *Eng. Proc.* 126:39, 2026 — data-release restriction (> 600 m/s). https://doi.org/10.3390/engproc2026126039 (conference)
7. Analog Devices/Maxim, *MAX2769 Universal GPS Receiver* data sheet — NF, IF filter options (via [rf-transceiver-ics](../18-components-parts/rf-transceiver-ics.md)). https://www.analog.com/media/en/technical-documentation/data-sheets/max2769.pdf (datasheet)
