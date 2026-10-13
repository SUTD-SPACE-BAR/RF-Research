---
title: SDRs as test equipment — RTL-SDR, HackRF, ADALM-Pluto (and Airspy/SDRplay) as spectrum analyzer, power meter, signal generator and noise-figure meter; calibration and accuracy limits
domain: 17-test-measurement
slug: sdr-as-test-equipment
tags: [sdr, rtl-sdr, hackrf, pluto, adalm-pluto, airspy, sdrplay, spectrum-analyzer, power-meter, signal-generator, noise-figure, dbfs, calibration, iq-imbalance, image, dc-spike, dynamic-range, rtl_power, hackrf_sweep, gnu-radio, sdrangel, pattern-measurement]
prerequisites: [spectrum-analyzers.md, ../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md, ../05-analog-electronics/data-converters-adc-dac.md]
related: [noise-figure-measurement.md, antenna-range-ota-testing.md, signal-generators-and-sources.md, rf-power-measurement.md, lab-setup-by-budget.md, ../14-sdr-dsp/sdr-hardware-survey.md, ../14-sdr-dsp/iq-complex-baseband.md, ../14-sdr-dsp/fft-spectral-analysis-windows.md, ../15-lora-ism-radios/ground-station-design.md]
level: intro
confidence: medium
last_updated: 2026-10-03
---

# SDRs as test equipment

## Questions this page answers
- Can an RTL-SDR, HackRF or Pluto replace a spectrum analyzer for my LoRa and GNSS work?
- How do I turn "dBFS" into dBm, and how accurate is it?
- What are the spikes and mirror signals I see on SDR spectra — are they real?
- Can I use a HackRF or Pluto as a signal generator for receiver testing?
- Can an SDR measure noise figure?
- What SDR setup do I need to log antenna patterns or range-test RSSI?

## TL;DR
- **SDRs measure relative power well and absolute power only after calibration.** At fixed gain, frequency and temperature, a two-point calibration against a known source gives ±0.5 dB over the linear range (tens of dB); change any setting and recalibrate.
- **Dynamic range**: 8-bit SDRs (RTL-SDR, HackRF) have ≈ 50 dB ideal full-scale SNR (less in practice) and ≈ 45–50 dB SFDR; 12-bit (Pluto, Airspy, SDRplay) ≈ 74 dB ideal. FFT processing gain lowers the per-bin noise floor (1024 points, 8-bit ideal: −77 dBFS with the real-sample formula, −80 dBFS for complex IQ with 0 dBFS = full-scale complex tone), but spurs, the DC spike and **IQ-imbalance images** limit what you can trust: 0.5 dB/3° imbalance → image only 28 dB down (formula and simulation agree).
- **Know the limits** [1], [2], [3]: RTL-SDR Blog V4 — 500 kHz–1.766 GHz, 2.4 MHz stable bandwidth, 1 ppm TCXO, 8-bit; HackRF One — 1 MHz–6 GHz, 2–20 MS/s, 8-bit, half-duplex, **max input −5 dBm** (+10 dBm theoretically with the RX amp off), TX 0–15 dBm (up to 4 GHz), −10…0 dBm at 4–6 GHz; ADALM-Pluto — AD9363, 325 MHz–3.8 GHz, 200 kHz–20 MHz bandwidth, 12-bit, USB streams ≤ 4 MS/s without drops, RSSI 100 dB range ±2 dB.
- **As a spectrum analyzer**: sweep by hopping (rtl_power, hackrf_sweep, SDRangel); discard capture edges and the DC region; use offset tuning; treat anything near −f (image) or at the centre (DC) with suspicion.
- **As a signal generator** (HackRF, Pluto): uncalibrated level, harmonics and LO leakage — always add a band-pass/low-pass filter and a calibrated attenuator chain, and verify with an SA.
- **As a noise-figure meter**: an SDR is a good Y-factor *ratio* detector (linearity and stability are all it needs) — SDRangel has a noise-figure plugin for 346-class noise sources [4]. SDRs' own NF is poor and gain-dependent (independent measurements, Libre Space Foundation 2020 via the [SDR survey](../14-sdr-dsp/sdr-hardware-survey.md#level-2--comparing-receivers-quantitatively): RTL-SDR Blog V3 (R820T2) **5.4 dB at 437 MHz** but 11.9 dB at 1280 MHz, Pluto 6.1 dB at 437 MHz; Rowetel: HackRF One 11.1 dB at 435 MHz; one amateur measurement of an E4000-tuner RTL-SDR: 13.6–17 dB at 700 MHz vs a datasheet ≈ 4 dB [5]) — put an LNA in front.

## Intuition (no math)
An SDR is a spectrum analyzer with the back end replaced by a computer: a tuner mixes a slice of spectrum down to baseband, an ADC digitises it, and software does the rest. That makes it wonderfully flexible (record everything, post-process, demodulate LoRa packets while measuring their power) but it lacks what makes a lab analyzer trustworthy: a calibrated, flat gain path, a preselector that rejects images, and a high-resolution ADC with low spurs. The tuner's gain changes with frequency, temperature and settings; its zero-IF architecture puts a DC spike in the middle and a mirror image of strong signals on the other side. So an SDR is an excellent *comparator* — pattern measurements, before/after checks, Y-factor ratios, RSSI logging — and a mediocre *absolute* instrument unless you calibrate it for exactly the setting you use.

## The math

### Level 1 — the working relations
- **ADC**: SNR_ideal = 6.02·N_bits + 1.76 dB (8 bits → 49.9 dB, 12 → 74.0 dB, 14 → 86.0 dB). Noise density relative to full scale: −SNR − 10 log(f_s/2) dBFS/Hz.
- **FFT processing gain**: per-bin noise floor = −SNR − 10 log(N/2) dBFS for real samples (1024 points → −77 dBFS at 8 bits); for complex IQ data, with 0 dBFS = a full-scale complex tone, the noise spreads over all N bins: −SNR − 10 log N (−80 dBFS for 1024 points at 8 bits; W5-E9 simulation) and −SNR − 10 log f_s dBFS/Hz ([FFT scaling](../14-sdr-dsp/fft-spectral-analysis-windows.md)); bin width f_s/N; ENBW 1.5 bins (Hann).
- **Calibration**: P(dBm) = (reading_dBFS − c)/m, fitted at ≥ 2 known levels at the same gain/frequency.
- **Image rejection** from gain error g (linear) and phase error φ:
  $$\text{IRR}=10\log_{10}\frac{1+2g\cos\varphi+g^2}{1-2g\cos\varphi+g^2}.$$
- **Tone power from an FFT**: sum |X_k|² over the window main lobe and divide by Σw² (energy normalisation) — immune to scalloping (a Hann window's peak bin reads up to −1.42 dB low at half-bin offset).

### Level 2 — why the limitations occur
**IQ imbalance.** A zero-IF receiver forms I = cos(ωt), Q = g sin(ωt + φ). Writing Q in terms of e^{±jωt}, the complex signal I + jQ has components at +ω (amplitude (1 + g e^{jφ})/2) and −ω (amplitude (1 − g e^{−jφ})/2); their power ratio is the IRR above. Script §2 confirms by FFT: 0.1 dB/1° → 39.6 dB; 0.5 dB/3° → 28.2 dB; 1 dB/5° → 22.8 dB. A strong 915 MHz LoRa carrier 200 kHz above the tuned centre therefore also appears 200 kHz *below* it at −25…−40 dBc — a phantom signal.

**DC offset and LO leakage.** Mixer imbalance and LO self-mixing produce a spike at 0 Hz; flicker noise raises the floor near it. Offset-tune so the signal of interest is away from centre (and away from capture edges where the anti-alias filter rolls off).

**Gain calibration.** The dBFS reading = P_in + G(f, gain, T) − (ADC full-scale). G drifts with temperature and varies by several dB across frequency and between gain steps. In our synthetic model (floor −95 dBFS in the measurement bin, soft compression at −3 dBFS, 25 dB conversion offset), a two-point calibration at −80/−50 dBm is within ±0.5 dB from −110 to −35 dBm; below it noise adds (+3.0 dB error at −120 dBm), above it compression subtracts (−3.5 dB at −25 dBm) (script §3). Real devices must be characterised the same way at the actual gain setting.

**Sweeping.** With usable bandwidth ≈ 75 % of the sample rate per hop: RTL-SDR (2.4 MS/s) needs 56 hops per 100 MHz, Pluto over USB (4 MS/s) 32, HackRF (20 MS/s) 7; sweep time is dominated by retune/settle time per hop (driver-dependent; hackrf_sweep is optimised for this) (script §4).

### Level 3 — noise figure and sensitivity of SDRs
An SDR's input-referred noise depends on its LNA gain setting; at maximum gain its NF may approach the tuner datasheet, at lower gains it degrades as the ADC's quantisation noise and later stages dominate. Measuring it: Y-factor with a calibrated noise source is the reliable route; an MDS (3 dB-rise) measurement is a cross-check. The amateur measurement in [5] of an E4000-based RTL-SDR at 700 MHz gave 17.0 dB (MDS method) and 13.6 dB (Y-factor with a generator-made noise source), against a tuner datasheet NF near 4 dB — illustrating both the gap between chip and dongle and the spread between methods (not independently verified). Independent board-level measurements (Libre Space Foundation 2020: RTL-SDR V3 5.4 dB at 437 MHz, 11.9 dB at 1280 MHz) are tabulated in the [SDR survey](../14-sdr-dsp/sdr-hardware-survey.md#level-2--comparing-receivers-quantitatively). For receivers, the fix is an LNA (NF ≈ 0.5–1 dB, gain 15–20 dB) at the antenna; then the SDR's own NF matters little (Friis, [receiver cascade](../07-noise-linearity/receiver-cascade-analysis.md)).

## Design equations & rules of thumb

| Item | Value / rule | Notes |
|---|---|---|
| 8-bit SDR dynamic range | ~50 dB ideal, ~45–50 dB SFDR practical | RTL-SDR, HackRF |
| 12-bit SDR | ~74 dB ideal | Pluto, Airspy, SDRplay (14-bit RSPdx 86 dB) |
| Image rejection | 0.5 dB/3° → 28 dB | offset-tune, IQ correction |
| Absolute accuracy | ±0.5 dB after calibration at the same settings; several dB otherwise | recalibrate for each gain/frequency |
| HackRF max input | −5 dBm (safe), +10 dBm theoretical with amp off [2] | use pads |
| HackRF TX | 5–15 dBm (10 MHz–2.17 GHz), 13–15 dBm (2.17–2.74 GHz), 0–5 dBm (2.74–4 GHz), −10…0 dBm (4–6 GHz) [2] | filter harmonics |
| Pluto | 325 MHz–3.8 GHz, ≤ 20 MHz BW, 12-bit, USB ≤ 4 MS/s no drops [3] | RSSI ±2 dB over 100 dB |
| RTL-SDR V4 | 0.5–1766 MHz, 2.4 MHz stable, 1 ppm TCXO [1] | 8-bit |
| FFT tone power | sum main-lobe bins / Σw² | avoids scalloping |

## Worked examples

**Example 1 — logging an antenna pattern at 433 MHz with an RTL-SDR (see [antenna range](antenna-range-ota-testing.md)).** Source: a CW tone (LoRa module in test mode or a signal generator) 20–30 m away. RTL-SDR at fixed gain (AGC off), tuned 100 kHz below the tone (offset tuning), 2.4 MS/s, 8192-point FFT with Hann window, summing ±3 bins around the tone (§5: exact regardless of bin position). Verify linearity: insert a 10 dB pad — the reading must drop 10.0 ± 0.3 dB; if not, reduce gain. Average ≥ 16 FFTs per angle. Result: relative pattern to ±0.5 dB; absolute gain via a reference dipole.

**Example 2 — "is my ground-station LNA oscillating?"** Sweep 50 MHz–1.7 GHz with rtl_power (or hackrf_sweep to 6 GHz) with the LNA powered and the antenna replaced by a 50 Ω load. A real oscillation is a strong line that does not move when you change the SDR's centre frequency by a non-multiple of the hop step, and that scales 1:1 with an inserted pad; a tuner spur or image moves or changes non-linearly.

**Example 3 — calibrating RSSI of a LoRa SDR ground station.** Generator (or calibrated LoRa transmitter) → pads (calibrated) → step attenuator → SDR input. At the operating gain, measure the tone/packet power in dBFS at −100, −80 and −60 dBm; fit slope and intercept; record temperature. The fit then converts field recordings into dBm at the antenna port (subtract the known feedline loss) — much more trustworthy than the SX127x/SX126x chip RSSI.

**Example 4 — HackRF as a test signal source for sensitivity testing.** Transmit a recorded LoRa packet (IQ file) at 915 MHz. HackRF output at 915 MHz is 5–15 dBm maximum [2] and its level is not calibrated; set a moderate level, measure it once with a power meter/SA through a low-pass filter (harmonics!), then add 100–120 dB of calibrated attenuation in a shielded path ([noise-figure page, Example 4](noise-figure-measurement.md)). HackRF's own broadband noise and LO leakage at high attenuation settings can reach the DUT around the pads — shield it.

**Example 5 — Y-factor NF of a GNSS LNA with a Pluto** (SDRangel noise-figure plugin [4]): 346B noise source (ENR table), LNA, a second 20 dB LNA, Pluto at fixed gain, 2 MHz bandwidth at 1575 MHz. Calibrate with the noise source into the second LNA + Pluto (Y₂), then insert the DUT (Y₁₂): second-stage correction as in [noise-figure measurement](noise-figure-measurement.md). Pluto's absolute level doesn't matter; its linearity over the ~15 dB on/off range does — check by inserting a 3 dB pad (Y must not change).

## Practical notes
- **Protect the input**: SDR front ends die easily. HackRF: max −5 dBm [2]; RTL-SDR tuners likewise sub-0 dBm (limiter diodes help). Never connect a transmitter; use ≥ 40 dB of pads or a coupler, and a DC block if bias-T power is present.
- **Turn off AGC** and fix gain for any measurement; note the gain setting in the log.
- **Reference**: lock to a GPSDO where possible (HackRF and Pluto accept external clocks; the RTL-SDR V4 has a 1 ppm TCXO [1]) — needed to measure LoRa carrier offsets in ppm.
- **Software**: `rtl_power`/`hackrf_sweep` for wide sweeps; SDR++, SDRangel (includes spectrum, noise-figure, radio-astronomy and LoRa demodulator plugins), GNU Radio for custom measurements; Python (pyrtlsdr, SoapySDR, pyadi-iio for Pluto) for scripted pattern/RSSI logging.
- **Filters**: a band-pass filter in front (433 or 915 MHz SAW/cavity) removes out-of-band overload (FM broadcast, cellular) that otherwise creates intermodulation and false signals.
- **Temperature**: gain drifts; recheck a reference level every session (record-everything).
- **Cost/benefit**: an RTL-SDR (≈ US$30–40) + tinySA (≈ US$60–150) + NanoVNA (≈ US$100) is the minimum "RF lab"; see [lab setup by budget](lab-setup-by-budget.md).

## Common mistakes & misconceptions
- **Reading dBFS as dBm.**
- **Leaving AGC on** during a pattern or range test.
- **Believing the mirror image** of a strong signal (IQ imbalance) or the DC spike.
- **Overloading** with out-of-band signals and "discovering" intermod products.
- **Using an uncalibrated HackRF level** as the known stimulus for a sensitivity claim.
- **Comparing SDR noise-floor screenshots** taken at different gain, RBW (FFT size) and sample rate.
- **Assuming the SDR is linear** without the 10 dB pad test.

## How to simulate / verify
- `python3 tools/verify/meas_sdr.py` — (1) ideal ADC dynamic range and per-bin floor; (2) IQ-imbalance image: formula vs simulated FFT; (3) synthetic dBFS→dBm calibration curve with noise and compression, linear range after two-point cal; (4) sweep hop counts; (5) tone power from FFT bins without scalloping.
- Cross-check an SDR's calibrated reading against the tinySA and a power meter at one level (three-instrument check).

## Open questions / gaps
- Measured NF: R820T2 (V3) 5.4 dB at 437 MHz (11.9 dB at 1280 MHz), Pluto 6.1 dB at 437 MHz and 4.1 dB at 1280 MHz (Libre Space Foundation 2020), HackRF One 11.1 dB at 435 MHz (Rowetel) — see the [SDR survey](../14-sdr-dsp/sdr-hardware-survey.md#level-2--comparing-receivers-quantitatively). Not found: the V4 (R828D) at any frequency, any of them at 915 or 1575 MHz, and linearity. The E4000 figure is one amateur measurement. (Corrected 2026-10-03, W5-E9/D6 #14: this line previously said no authoritative NF measurements existed, contradicting 14.)
- Pluto maximum TX power and the AD9363's noise figure were not captured from the ADI wiki (table not rendered).
- Hop/retune times in script §4 are assumptions, not measurements.

## Sources
1. RTL-SDR Blog, "RTL-SDR Blog V4" product/launch pages (rtl-sdr.com) — R828D + RTL2832U, 500 kHz–1.766 GHz (built-in HF upconverter), up to 3.2 MHz bandwidth (2.4 MHz stable), 1 ppm TCXO, bias-T, input filtering. (vendor; search summary + product pages)
2. Great Scott Gadgets, *HackRF One* documentation (hackrf.readthedocs.io) — 1 MHz–6 GHz, 2–20 Msps, 8-bit, half-duplex, max input −5 dBm (+10 dBm with amp off in theory), TX power vs frequency table. (vendor docs; read)
3. Analog Devices Wiki, "ADALM-PLUTO Detailed Specifications" — AD9363, 325 MHz–3.8 GHz, 200 kHz–20 MHz BW, 12-bit, 61.44 MSPS–65.1 kSPS, EVM ≤ −40 dB, USB 2.0 up to 4 MSPS without drops, RSSI 100 dB (±2 dB). (vendor wiki; read)
4. SDRangel noise-figure plugin readme (github.com/f4exb/sdrangel). (open-source docs; search summary)
5. "Noise Figure Measurements of RTL-SDR Dongles" (IDC-Online reprint of an amateur blog article) — E4000 dongle at 700 MHz: 17.0 dB (MDS), 13.6 dB (Y-factor); datasheet ≈ 4 dB. (blog — anecdotal)
6. This repository: `tools/verify/meas_sdr.py`. (verification)
