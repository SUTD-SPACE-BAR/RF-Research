---
title: Noise-figure measurement — Y-factor method (derived), ENR and noise sources, second-stage correction, cold-source/gain method with a spectrum analyzer, SDR-based NF, hot/cold loads, and conducted LoRa sensitivity testing with a step attenuator
domain: 17-test-measurement
slug: noise-figure-measurement
tags: [noise-figure, y-factor, enr, noise-source, 346b, second-stage-correction, cold-source, gain-method, spectrum-analyzer, sdr, sdrangel, hot-cold-load, liquid-nitrogen, lna, sensitivity, per, step-attenuator, lora, shielding]
prerequisites: [../07-noise-linearity/noise-figure-and-friis.md, ../07-noise-linearity/thermal-noise-and-noise-temperature.md, ../07-noise-linearity/sensitivity-and-mds.md, spectrum-analyzers.md]
related: [sdr-as-test-equipment.md, signal-generators-and-sources.md, rf-power-measurement.md, rf-bring-up-debug-playbook.md, ../06-rf-circuits/lna-design.md, ../07-noise-linearity/receiver-cascade-analysis.md, ../15-lora-ism-radios/lora-sensitivity-and-link-budget.md, ../15-lora-ism-radios/ground-station-design.md, ../08-antennas/gnss-antennas.md]
level: mixed
confidence: high
last_updated: 2026-10-02
---

# Noise-figure measurement

## Questions this page answers
- How does the Y-factor method work, and how do I derive the noise figure from "noise source on / off"?
- What is ENR, and should I use a 6 dB or a 15 dB ENR noise source?
- Why must I "calibrate" the noise-figure setup before inserting the LNA (second-stage correction)?
- Can I measure an LNA's noise figure with a tinySA, a Siglent analyzer or an SDR — and how accurately?
- What are the cheap noise sources on AliExpress good for?
- How do I measure my LoRa ground-station receiver's real sensitivity with a step attenuator, and why does my receiver look better than the datasheet?
- How many packets do I need to count to claim "1 % PER at −137 dBm"?

## TL;DR
- **Y-factor**: Y = N_on/N_off = (T_on + T_e)/(T_off + T_e) ⇒ T_e = (T_on − Y T_off)/(Y − 1), with ENR = (T_on − T_off)/T0 [1]. Two steps: calibrate the instrument alone (Y₂ → T₂), then with the DUT (Y₁₂ → T₁₂, gain G₁), then **T₁ = T₁₂ − T₂/G₁**. Simulated end to end: an LNA of NF 1.20 dB, 18 dB gain in front of a 12 dB-NF instrument reads 1.200 dB corrected and **1.91 dB uncorrected**.
- **Choose ENR ≈ DUT NF + a few dB**: 6 dB ENR for NF up to ≈ 16–18 dB, 15 dB ENR above [1]. The NF error from an ENR error equals the ENR error (0.1 dB → 0.1 dB) at all practical NFs; the error from Y-noise explodes when NF ≫ ENR (0.05 dB Y error → 0.43 dB at NF 15 dB with 6 dB ENR, 0.10 dB with 15 dB ENR).
- **Correct the noise-source temperature**: a 300 K noise source treated as 290 K adds +0.13 dB at NF 0.5 dB, +0.12 dB at 1 dB.
- **Gain (cold-source) method with an SA**: terminate the DUT input in 50 Ω, measure output noise density N_out (dBm/Hz), NF = N_out + 174 − G. Needs the DUT noise ≥ 10 dB above the analyzer floor (a 20 dB LNA into a tinySA *without* LNA is 6.5 dB *below* its floor). Accuracy = gain error + absolute level error: ±2 dB with a tinySA (±2 dB level spec), ±0.7–0.9 dB with a Siglent-class SA, better only with a power-meter-calibrated setup.
- **Cheap noise sources** (uncalibrated avalanche/zener + MMIC modules) are excellent broadband stimuli for filter sweeps with an SA, **not** Y-factor sources unless you calibrate their ENR against a known source.
- **Hot/cold loads** (290 K room load vs 77 K load in liquid nitrogen) give absolute NF with no calibrated source: Y = 3.80 dB for a 1 dB NF; a 0.02 dB Y error costs only 0.014 dB.
- **Conducted sensitivity test**: generator → fixed pads → step attenuator → DUT in a shielded box; the leakage around the attenuators must be ≥ attenuation + 20 dB (≥ 127 dB to test −137 dBm from a −30 dBm generator). Semtech specifies LoRa sensitivity at **1 % PER, 64-byte payload** [5]; resolving 1 % ± 0.5 % needs ≈ 1 500 packets.

## Intuition (no math)
A noise-figure meter asks one question: how much noise does the amplifier add, compared with the thermal noise already coming from a 50 Ω source at room temperature? You can't just measure the output noise, because you don't know the gain and the instrument adds its own noise. The trick is to feed the amplifier two *known* noise levels — "cold" (room temperature, noise source off) and "hot" (noise source on, equivalent to a resistor thousands of kelvin hot) — and look at the ratio of the two output powers. If the amplifier added no noise, the ratio would be the full hot/cold ratio; the more noise it adds (a constant "pedestal" on both readings), the closer the ratio gets to 1. That ratio, the Y-factor, gives the added noise directly, and the difference of the two outputs gives the gain.

The instrument's own noise is removed the same way: measure the instrument alone first, then subtract its contribution scaled by the DUT gain (Friis). For sensitivity testing of a whole receiver, you do not measure noise at all — you feed a known, very weak real signal and count packets; the whole difficulty is making sure the signal really is as weak as you think (leakage) and counting enough packets.

## The math

### Level 1 — definitions and the working equations
- Noise factor F = 1 + T_e/T0, NF = 10 log F; T0 = 290 K (see [NF & Friis](../07-noise-linearity/noise-figure-and-friis.md)).
- **ENR** (current definition [1]): ENR = (T_on − T_off)/T0, ENR_dB = 10 log ENR; calibrated ENR tables are referenced to T_off = T0.
- **Y-factor**: Y = N_on/N_off = (T_on + T_e)/(T_off + T_e) ⇒ **T_e = (T_on − Y·T_off)/(Y − 1)**.
- If T_off = T0: F = ENR/(Y − 1), i.e. **NF = ENR_dB − 10 log(Y − 1)**.
- **DUT gain from the same data** [1]: G₁ = (N₁₂,on − N₁₂,off)/(N₂,on − N₂,off).
- **Second-stage correction**: T₁ = T₁₂ − T₂/G₁ (Friis inverted).
- **Gain method**: NF = N_out(dBm/Hz) − (−174 dBm/Hz) − G(dB), with the DUT input terminated at T0.

### Level 2 — derivation and error sensitivity
Let the noise source present an available noise temperature T_s to the DUT (bandwidth B, available gain G). Output noise power N = kBG(T_s + T_e). With T_s ∈ {T_on, T_off}:
$$Y=\frac{T_{on}+T_e}{T_{off}+T_e}\;\Rightarrow\;T_e(Y-1)=T_{on}-Y T_{off}\;\Rightarrow\;T_e=\frac{T_{on}-YT_{off}}{Y-1}.$$
Nothing depends on k, B or G — which is why the method is robust: only a *ratio* of two noise powers at the same instrument setting is needed, plus the ENR. With T_off = T0 and T_on = T0(ENR + 1): T_e = T0(ENR + 1 − Y)/(Y − 1) ⇒ F = 1 + T_e/T0 = ENR/(Y − 1).

**Error sensitivity** (script §2). Differentiating NF(Y, ENR): ∂NF/∂ENR_dB → 1 when Y ≫ 1 (an ENR table error goes straight into NF); ∂NF_dB/∂Y_dB = −Y/(Y − 1) (exact for T_off = T0, since F = ENR/(Y − 1)) grows without bound as Y → 1, i.e. when the DUT's own noise swamps the source's excess noise (NF ≫ ENR). Numbers for a 0.05 dB Y error: NF 1 dB → 0.066 dB (ENR 6) / 0.052 dB (ENR 15); NF 15 dB → 0.43 / 0.10 dB; NF 25 dB → 2.9 / 0.52 dB. This is the quantitative reason for AN 57-2's "6 dB ENR up to about 16–18 dB NF" rule [1]. The *advantages* of low ENR for low-NF DUTs are smaller internal power levels (less instrument non-linearity) and a smaller change in the source's reflection coefficient between on and off (6 dB sources have a built-in pad) — important for LNAs whose noise and gain depend on source impedance [1].

**Averaging.** Each noise-power estimate has relative standard deviation 1/√(Bτ) (B = measurement bandwidth, τ = integration time); averaging N readings reduces jitter by √N [1]. For σ(Y) = 0.02 dB (0.46 %) with both on and off readings: Bτ ≈ 2/(0.0046²) ≈ 10⁵ — e.g. 4 MHz × 25 ms. Narrow-band measurements need longer integration.

**Second-stage error** (script §1): uncorrected, the reading is NF of T₁ + T₂/G₁. For a 1.2 dB LNA: gain 10 dB + 12 dB-NF instrument → 4.48 dB; 18 dB + 25 dB-NF (a bare SA) → 8.00 dB; 30 dB + 25 dB → 2.13 dB; 18 dB + 6 dB → 1.35 dB. Always calibrate, and reduce T₂ with a low-NF preamp at the instrument input (AN 57-3 hint [2]).

### Level 3 — temperature, loss and mismatch corrections
- **T_off ≠ T0**: the ENR table assumes 290 K; a source at 300 K raises both T_on and T_off by 10 K. Uncorrected, the computed NF is high by +0.131 dB (true 0.5 dB), +0.117 dB (1 dB), +0.074 dB (3 dB) (script §3). Analyzers correct this if you enter the source temperature [1].
- **Loss before the DUT** (adaptor, cable, DC block, bias-T) at physical temperature T0 adds its loss in dB to the measured NF — subtract it. **Loss after the DUT** is part of "stage 2": inside the calibration loop it is corrected automatically; outside it (e.g. a pad added after cal to tame a high-gain DUT) it must be entered (3 dB after a 15 dB DUT raises a 1.2 dB reading by 1.07 dB) [1].
- **Mismatch**: noise-figure mismatch errors cannot be corrected with scalar data (they depend on the DUT's noise parameters), so minimise them: use a low-ENR source with good match, an isolator only if its loss is characterised [1]. Noise parameters and noise circles: [LNA design](../06-rf-circuits/lna-design.md).
- **Hot/cold loads**: with T_h = 290 K and T_c = 77 K (a 50 Ω termination in liquid nitrogen), T_e = (T_h − Y T_c)/(Y − 1). Y is small (4.62 dB at NF 0.5 dB, 1.15 dB at 5 dB) but the method has no ENR uncertainty; the real uncertainty is the cold load's *effective* temperature at the DUT plane (the cable into the dewar has loss and a temperature gradient — characterise it or put the LNA close).

## Design equations & rules of thumb

| Quantity | Relation / value | Notes |
|---|---|---|
| Y-factor NF (T_off = T0) | NF = ENR_dB − 10 log(Y − 1) | ENR in linear inside log: F = ENR/(Y−1) |
| General | T_e = (T_on − Y T_off)/(Y − 1) | any T_off |
| Second stage | T₁ = T₁₂ − T₂/G₁ | calibrate first |
| ENR choice | 6 dB for NF ≲ 16–18 dB; 15 dB above [1] | |
| ENR error | → equal NF error (dB) | ENR table ±0.1–0.2 dB typical |
| T_off error | +0.12 dB at NF 1 dB for 10 K | enter source temperature |
| Jitter | σ/mean ≈ 1/√(Bτ) per reading | average √N |
| Gain method | NF = N_out + 174 − G | DUT noise ≥ 10 dB above SA floor |
| Loss before DUT | subtract L (dB) | at T0 |
| LoRa NF from sensitivity | NF = S + 174 − 10 log BW − SNR_req | SX1262 SF7: 6.5 dB |
| Sensitivity-test isolation | ≥ (P_gen − P_target) + 20 dB | shielded box, good cables |
| PER sample size | N ≈ 1.96² p(1−p)/Δ² | 1 % ± 0.5 % → 1 521 |

## Worked examples

**Example 1 — Y-factor with a 346B-class source (ENR 15.2 dB at 1.575 GHz) on a GNSS LNA, instrument = SA + 20 dB preamp (NF_sys ≈ 5 dB).** Calibration: Y₂ reading → T₂ ≈ 627 K. With the LNA: N₁₂,on/N₁₂,off = Y₁₂; suppose Y₁₂ = 14.0 dB (25.1) and the gain from the power difference is 17.5 dB (56.2). T₁₂ = (T_on − Y₁₂·290)/(Y₁₂ − 1), T_on = 290(1 + 10^{1.52}) = 290 × 34.1 = 9 889 K → T₁₂ = (9 889 − 25.1 × 290)/24.1 = (9 889 − 7 279)/24.1 = 108 K; T₁ = 108 − 627/56.2 = 96.8 K → NF = 10 log(1 + 96.8/290) = **1.25 dB**. Uncorrected (108 K) it would read 1.38 dB. Subtract any adaptor loss in front (e.g. 0.1 dB SMA-to-SMA → 1.15 dB).

**Example 2 — gain method with a tinySA Ultra (script §4).** LNA with G = 20 dB (measured on the VNA ±0.2 dB), NF 1.5 dB: output noise density −174 + 1.5 + 20 = −152.5 dBm/Hz. The tinySA Ultra with its internal LNA on (NF ≈ 5–6 dB) has a floor ≈ −168 dBm/Hz: 15.5 dB margin — floor subtraction is easy (a 0.5 dB floor mis-read costs 0.02 dB). Without its LNA (NF ≈ 28 dB) the floor is −146 dBm/Hz, 6.5 dB *above* the DUT noise: a 0.5 dB floor mis-read would cost 2.9 dB — use a second LNA (40 dB total) and treat both as the DUT. But the tinySA's absolute level accuracy is ±2 dB [3], so NF = 1.5 ± 2.2 dB worst case — enough to find a broken LNA, useless for comparing 0.8 vs 1.2 dB parts. With a Siglent SSA3021X Plus (±0.7 dB) the budget is ±0.9 dB; to do better, calibrate the SA's noise-level reading at the frequency with a power meter and a CW tone (±0.1–0.2 dB), then ±0.3–0.4 dB is feasible.

**Example 3 — LoRa receiver NF from sensitivity.** SX1262 datasheet: SF7/125 kHz −124 dBm, SF9 −129 dBm, SF12 −137 dBm at 1 % PER [5]; with required SNRs of −7.5/−12.5/−20 dB the implied NF is 6.5/6.5/6.0 dB (script §6). If your measured SF12 sensitivity is −133 dBm, the front end is ≈ 4 dB worse than the chip — look for matching-network loss, a lossy SAW, a bad LNA bias, or interference/desense from the MCU ([RF bring-up playbook](rf-bring-up-debug-playbook.md)).

**Example 4 — conducted sensitivity test of a 433 MHz ground station (E22-400 or SX1278 board).**
1. Transmitter: a second LoRa module sending numbered 64-byte packets (or a generator with LoRa waveform playback), at a known conducted power: measure it once with the power meter (e.g. +10.0 dBm) — or better, a module set to its lowest power (−9 dBm on SX1262-class parts) to reduce the attenuation and isolation needed.
2. Fixed pads (e.g. 30 + 30 dB, calibrated at 433 MHz) then a **step attenuator** (0–110 dB in 1 or 10 dB steps; mechanical HP 8494/8496 types are cheap used; programmable ones allow automation), then the DUT.
3. **Isolation**: put the transmitter *and* the DUT in separate shielded boxes (metal tins with RF-tight lids, filtered DC/USB), use double-shielded or semi-rigid cables, and verify: with the attenuator at maximum, the DUT must see *no* packets and its RSSI must sit at the noise floor. From −30 dBm to −137 dBm needs 107 dB of attenuation and > 127 dB of leakage suppression (script §6) — a phone-sized unshielded setup leaks far more, so receivers "look better than the datasheet".
4. Step down 1 dB at a time near the knee; count ≥ 1 500 packets per step near 1 % PER (≈ 400 packets at 10 % PER ± 3 %). Record the PER waterfall, RSSI and SNR reported by the chip (cross-check the chip's RSSI calibration against the known level).
5. Repeat at the band edges and with the flight TCXO temperature extremes (frequency offset matters for LoRa; see [LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)).

**Example 5 — hot/cold load for an absolute check of a GNSS LNA** (script §7): NF 1.0 dB → Y = 3.80 dB between a room-temperature and an LN2-immersed load. A measured Y of 3.78 dB (0.02 dB low) gives NF 1.014 dB — excellent, provided the cold load's effective temperature (77 K plus the warming by the connecting cable's loss) is known to a few kelvin.

## Practical notes
- **Noise sources**: HP/Agilent 346A (ENR ≈ 5–6 dB) and 346B (≈ 15 dB), 10 MHz–18 GHz, driven by a 28 V pulse, are the workhorses; used units are common — check that the ENR table (label or file) is present. NoiseCom and others make equivalents. The SDRangel noise-figure plugin supports 346-family sources or any source "supplied with accurate ENR calibration data" [4].
- **Cheap noise sources** (avalanche-diode/zener + MMIC boards, often sold as "noise source 1 MHz–3.5 GHz"): high but *uncalibrated* and frequency-dependent output; great as a broadband stimulus for measuring filter responses with an SA (normalise with a thru), for checking an SDR's gain flatness, or as a relative "hot" source for A/B comparisons of LNAs. For absolute NF, calibrate their ENR at your frequencies against a 346-class source or a hot/cold load. (Forum knowledge; unverified specifics.)
- **Switching the source**: automate on/off (a 28 V supply switched by a MOSFET from a GPIO) and alternate often — gain drift between on and off readings is a major error source.
- **Shield and filter**: stray signals (Wi-Fi, LTE, the MCU clock) in the measurement band corrupt noise measurements; use a band-pass filter in the IF/SA path and a shielded enclosure; check the "off" spectrum for spurs (AN 57-3 [2]).
- **Linearity**: a 15 dB ENR source into a 40 dB-gain chain can compress the instrument; insert a characterised pad after the DUT [1].
- **Bias**: power the LNA through a clean, filtered supply; switching regulators create spurs that look like extra noise. Active GNSS antennas: bias through a bias-T and measure with the antenna replaced by the noise source.
- **SDR-based NF**: an SDR with fixed gain (AGC off) is a perfectly good *ratio* meter for Y-factor (it only needs linearity and stability, not absolute calibration): SDRangel's plugin automates the on/off sequencing and ENR interpolation [4]. Keep the SDR's input level well below its compression and watch its own spurs; see [SDR as test equipment](sdr-as-test-equipment.md).

## Common mistakes & misconceptions
- **Skipping calibration / second-stage correction** — an 18 dB LNA into a bare SA reads 8 dB instead of 1.2 dB.
- **Using a 15 dB ENR source on a 0.5 dB LNA with a sensitive input match** — the on/off impedance change shifts the LNA's noise; prefer a 6 dB source.
- **Using a 6 dB ENR source on a 20 dB-NF mixer** — Y ≈ 0.17 dB, hopeless jitter.
- **Forgetting the adaptor in front of the DUT** — every 0.1 dB of input loss is 0.1 dB of NF.
- **Measuring "NF" of an LNA with the gain method and a ±2 dB SA** and reporting 0.1 dB resolution.
- **Treating an uncalibrated AliExpress noise source as ENR 30 dB** because the listing says so.
- **Sensitivity tests with leaky setups** — the transmitter's radiated leakage reaches the DUT around the attenuator; the DUT then works at "−150 dBm". Always verify with the attenuator at maximum.
- **Too few packets** — 100 packets cannot distinguish 1 % from 3 % PER.

## How to simulate / verify
- `python3 tools/verify/meas_noise_figure.py` — (1) end-to-end Y-factor with second-stage correction and the uncorrected errors; (2) NF sensitivity to Y and ENR errors vs NF for 6/15 dB ENR; (3) noise-source temperature error; (4) gain method: margins above the SA floor, floor-subtraction error, uncertainty budgets; (5) loss corrections; (6) LoRa NF from sensitivity, attenuation/isolation plan, PER sample sizes; (7) hot/cold load.
- Cascade checks against [receiver cascade analysis](../07-noise-linearity/receiver-cascade-analysis.md) (`tools/verify/noise_cascade.py`).

- SDR-based NF and noise-density readings need the dBFS/Hz scaling, ENBW and power-averaging rules (log-average bias −2.51 dB) of [14 FFT & windows](../14-sdr-dsp/fft-spectral-analysis-windows.md); measured NFs of common SDRs for comparison are in [14 SDR hardware survey](../14-sdr-dsp/sdr-hardware-survey.md).

## Open questions / gaps
- No verified ENR data for low-cost noise-source modules; a calibration campaign (against a 346B or hot/cold load) would make them usable.
- The LoRa required-SNR values (−7.5/−12.5/−20 dB) are the commonly quoted Semtech demodulator thresholds; see domain 15 for their sourcing.
- Cold-source (vector-corrected) NF on VNAs (Keysight PNA option) is not covered in detail.

## Sources
1. Keysight AN 57-2, *Noise Figure Measurement Accuracy — The Y-Factor Method*, 5952-3706E — ENR definition (T_on − T_off)/T0, Y-factor, calibration and second-stage correction (eqs 2-10 to 2-18), low vs high ENR choice (6 dB up to NF ≈ 16–18 dB), jitter/averaging, loss and temperature corrections, mismatch cannot be corrected with scalar data. (app note; read)
2. Keysight AN 57-3, *10 Hints for Making Successful Noise Figure Measurements*, 5980-0288EN — preamplifier use, shielding, interference, linearity. (app note; read)
3. tinySA wiki, "Specification" (tinySA Ultra: ±2 dB level accuracy after calibration, LNA NF 5 dB). (vendor docs; read)
4. SDRangel "Noise figure" channel plugin readme, github.com/f4exb/sdrangel/…/noisefigure/readme.md — Y-factor with ENR tables; 346-family or other calibrated sources. (open-source docs; search summary)
5. Semtech, *SX1261/2 datasheet* — LoRa sensitivity conditions (PER 1 %, 64-byte payload, 8-symbol preamble, CR 4/5, CRC on, explicit header) and values (SF7/125 kHz −124 dBm…). (datasheet; read)
6. Keysight AN 57-1, *Fundamentals of RF and Microwave Noise Figure Measurements*, 5952-8255E — definitions, direct/gain method. (app note; cited)
7. Maxim/ADI AN 2875, "Three Methods of Noise Figure Measurement" — gain, Y-factor and noise-figure-meter methods. (app note; cited via summary)
8. This repository: `tools/verify/meas_noise_figure.py`. (verification)
