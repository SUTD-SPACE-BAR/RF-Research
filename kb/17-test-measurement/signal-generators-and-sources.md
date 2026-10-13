---
title: Signal generators and sources — lab generators, ADF4351/MAX2870 synthesiser boards (harmonics, spurs, phase noise, filtering), Si5351 clocks, tinySA as a generator, noise sources, calibrated and step attenuators
domain: 17-test-measurement
slug: signal-generators-and-sources
tags: [signal-generator, adf4351, max2870, si5351, synthesizer, pll, harmonics, low-pass-filter, spurs, phase-noise, tinysa, hackrf, noise-source, attenuator, step-attenuator, calibration, receiver-test, leakage]
prerequisites: [spectrum-analyzers.md, ../06-rf-circuits/vco-and-pll-synthesizers.md, ../01-circuit-theory/passive-filter-design-prototypes.md]
related: [noise-figure-measurement.md, phase-noise-measurement.md, rf-power-measurement.md, sdr-as-test-equipment.md, lab-setup-by-budget.md, ../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md, ../07-noise-linearity/sensitivity-and-mds.md, ../18-components-parts/mixers-plls-vcos-parts.md]
level: mixed
confidence: medium
last_updated: 2026-09-29
---

# Signal generators and sources

## Questions this page answers
- What signal source do I need to test a LoRa receiver, a filter or an LNA?
- Are the cheap ADF4351 / MAX2870 boards usable as signal generators, and what must I add?
- Why does my Si5351 "sine" have strong harmonics?
- Can a tinySA or HackRF be my signal generator?
- How do I make an accurate −130 dBm signal?
- How do I pick and calibrate attenuators and step attenuators?

## TL;DR
- **Lab generators** (used HP 8648/8656, Agilent ESG, Rigol DSG800, Siglent SSG3000X) give calibrated level (±1 dB typ), clean spectra, modulation and −127 dBm-class minimum output — the right tool for receiver sensitivity.
- **ADF4351 boards** (35 MHz–4.4 GHz; output −4/−1/+2/+5 dBm ±1 dB; divided outputs have H2 −20 dBc and **H3 −10 dBc**; PFD spurs −80 dBc; VCO phase noise −111 dBc/Hz at 100 kHz from 3.3 GHz) [1] are square-ish sources: fine as an LO or a "is it working" tone, but need a **7th-order LPF** (Butterworth) or a 5th–7th-order Chebyshev to reach −50 dBc harmonics (script).
- **Si5351** clock outputs are square waves: H3 −9.5 dBc, H5 −14 dBc at 50 % duty; a 45 % duty adds H2 at −16 dBc (script). Filter or accept.
- **tinySA Ultra as a generator**: sine 100 kHz–800 MHz with harmonics < −40 dBc, −115…−19 dBm in 1 dB steps, ±2 dB accuracy from −72 to −19 dBm (less below); above 800 MHz a square-wave "cleanest" mode to 4.4 GHz or a "highest accuracy" mode with possible strong spurs to 5.4 GHz [2]. A remarkably useful cheap receiver-test source.
- **Level accuracy of very weak signals is an attenuation-and-isolation problem**: −137 dBm from −10 dBm needs 127 dB of calibrated pads *and* ≥ 147 dB of isolation around them; starting from −80 dBm needs 57 dB and ≥ 77 dB. Calibrated pads (VNA-measured at the test frequency) cut a 90 dB stack's uncertainty from ±1.05 to ±0.17 dB worst case.
- **In-band phase noise** of an ADF4351 at 915 MHz (f_PFD 25 MHz) ≈ −113 dBc/Hz from the datasheet normalisation (PN = −220 + 10 log f_PFD + 20 log N, then −20 log(divider)) — better than any budget analyzer can measure.

## Intuition (no math)
A signal generator is three things: a frequency (synthesiser), a waveform (ideally a pure sine), and a known power (a levelled output followed by a calibrated attenuator). Cheap synthesiser boards nail the first — they are PLLs locked to a crystal — but their output stage is a digital-ish divider that produces something closer to a square wave, and their level is only "about" what the register says. That is fine for an LO or a quick check but not for measuring a filter's stopband or a receiver's sensitivity. You fix the waveform with a low-pass filter and the level with a power meter plus calibrated attenuators.

Making a very small signal is harder than it looks: the attenuators do their job on the cable, but the generator itself, its power cable and the DUT's own leads radiate and pick up. If the leakage path is only 100 dB down while you need 127 dB of attenuation, the receiver sees the leakage, not your carefully attenuated signal.

## The math

### Level 1 — the relations you need
- **Square-wave harmonics** (duty d): relative amplitude of harmonic n = |sin(nπd)|/(n|sin(πd)|); at d = 0.5, odd harmonics 20 log(1/n) (−9.5, −14.0, −16.9 dBc for n = 3, 5, 7), even harmonics zero.
- **Butterworth LPF attenuation**: A(f) = 10 log[1 + (f/f_c)^{2n}]; **Chebyshev** (ripple ε): A = 10 log[1 + ε² T_n²(f/f_c)] (design: [filter prototypes](../01-circuit-theory/passive-filter-design-prototypes.md)).
- **PLL in-band noise** (ADF4351 datasheet method [1]): PN_VCO = PN_floor + 10 log f_PFD + 20 log N, with PN_floor ≈ −220 dBc/Hz (normalised); divided output: −20 log D. Flicker term: PN = PN_1f + 10 log(10 kHz/f) + 20 log(f_RF/1 GHz), PN_1f ≈ −116 dBc/Hz [1].
- **Attenuator stack**: total = Σ A_i; uncertainty worst case Σ u_i, RSS √Σ u_i²; pad-to-pad mismatch per interface 20 log(1 ± Γ_aΓ_b).
- **Low-level signal**: P_DUT = P_gen − Σ A_i; leakage must satisfy P_leak ≤ P_DUT − 20 dB.

### Level 2 — derivations and what they imply
**Square waves.** A pulse train of duty d has Fourier coefficients c_n ∝ sin(nπd)/n. At d = 0.5 all even terms vanish; a small asymmetry (duty 48 %) creates H2 at −24 dBc, 45 % at −16 dBc, 40 % at −10 dBc (script §1). The ADF4351 datasheet values (H2 −19…−20 dBc, H3 −10…−13 dBc) [1] are consistent with a nearly symmetric square-ish divider output with some band-limiting.

**Clean-up filter.** To bring H2 (−20 dBc) and H3 (−10 dBc) to −50 dBc, the filter must provide ≥ 30 dB at 2f₀ and ≥ 40 dB at 3f₀. With the cut-off at 1.2f₀ (to keep the passband flat), ideal prototypes give (script §2): 5th-order Butterworth 22/40 dB (insufficient at 2f₀), **7th-order Butterworth 31/56 dB**, 5th-order Chebyshev (0.1 dB) 25/46 dB (marginal), **7th-order Chebyshev 44/73 dB**. The same ratios hold at 433 and 915 MHz. Real LC filters at GHz have finite Q and parasitic re-entries (SRF of the capacitors), so measure the built filter's S21 to at least 5f₀ on a VNA. For a single frequency, a band-pass (SAW, ceramic, cavity) filter is easier and also removes sub-harmonics and PFD spurs.

**Synthesiser phase noise.** Inside the loop bandwidth the output noise is the reference/PFD noise multiplied by N; outside it, the VCO's open-loop noise. For 915 MHz from a 3.66 GHz VCO (÷4) with f_PFD = 25 MHz: N = 146.4, PN_VCO = −220 + 74.0 + 43.3 = −102.7 dBc/Hz, output −114.8 dBc/Hz; adding the flicker term at 10 kHz (−116.8 dBc/Hz) gives ≈ −112.6 dBc/Hz (script §3). Lowering f_PFD to 10 MHz costs ≈ 3 dB. The datasheet's open-loop VCO values (−111 dBc/Hz at 100 kHz, −134 at 1 MHz from 3.3 GHz; ≈ 12 dB lower after ÷4) [1] govern larger offsets.

### Level 3 — levels, leakage and noise sources
- **Isolation**: generator chassis radiation is set by its *internal* level, not by an external pad; so reduce the generator's own output (use its internal attenuator) before adding external pads. Shield the DUT (metal box with filtered supply leads) and use double-shielded cables; verify with the RF off/attenuator at maximum ([noise-figure page](noise-figure-measurement.md)).
- **Generator broadband noise** is attenuated along with the carrier, so at the DUT it falls toward kT; it only matters when the generator output is used without much attenuation (e.g. testing blocking with a strong interferer: the interferer's phase noise and broadband noise can desense the receiver more than the blocking mechanism you meant to test — the reciprocal-mixing trap of [phase noise](phase-noise-measurement.md)).
- **Noise sources** (for NF and broadband sweeps): calibrated 346-class diode sources (ENR 5–6 or 15 dB) and uncalibrated avalanche/zener + MMIC modules; see [noise-figure measurement](noise-figure-measurement.md).
- **Step attenuators**: mechanical (HP 8494/8495/8496 families: 0–11, 0–70, 0–110 dB) are repeatable to ~0.1 dB but each step's error must be calibrated; programmable/digital attenuator ICs (PE43xx-class) are convenient but have limited isolation at high attenuation and small-signal compression limits.

## Design equations & rules of thumb

| Item | Rule / value | Notes |
|---|---|---|
| Square wave H3/H5/H7 | −9.5/−14.0/−16.9 dBc | 50 % duty |
| Duty 45 % | H2 −16 dBc | even harmonics appear |
| ADF4351 | 35 MHz–4.4 GHz; −4…+5 dBm ±1 dB; H2 −20, H3 −10 dBc (divided) [1] | PFD spurs −80 dBc [1] |
| Clean to −50 dBc | 7th-order Butterworth or 5–7th-order Chebyshev, f_c ≈ 1.2 f₀ | measure S21 to 5f₀ |
| ADF4351 in-band PN | ≈ −113 dBc/Hz at 915 MHz, f_PFD 25 MHz | datasheet formula |
| tinySA Ultra gen | −115…−19 dBm; ±2 dB to −72 dBm; H < −40 dBc below 800 MHz [2] | square wave above 800 MHz |
| HackRF TX | 5–15 dBm at 10 MHz–2.17 GHz [3] | uncalibrated, needs filter |
| Pad stack | calibrate each pad at the test frequency | ±0.05 dB each achievable |
| Isolation | ≥ attenuation + 20 dB | shield + good cables |

## Worked examples

**Example 1 — a 915 MHz test tone from an ADF4351 board.** Set 915 MHz (VCO 3.66 GHz ÷ 4), output +5 dBm. Raw spectrum on the SA: fundamental +4 dBm (±1 dB [1]), H2 ≈ −16 dBm (−20 dBc), H3 ≈ −6 dBm (−10 dBc), small spurs at ±25 MHz (PFD, −80 dBc [1]). Add a 7th-order LPF with f_c ≈ 1.1 GHz: H2 → ≤ −46 dBm, H3 → ≤ −62 dBm (script: 31/56 dB). Then a 10 dB pad to isolate the filter from the load, and measure the final level once with a power meter. Good enough for LNA gain/compression checks and as an LO; not calibrated enough for sensitivity without the power-meter step.

**Example 2 — Si5351 as a 433 MHz source?** The Si5351 is specified to about 200 MHz; odd-harmonic operation (as the NanoVNA does) gives a weak and dirty 433 MHz. Use it for crystal/clock replacement, IF injection or HF work; for 433 MHz use an ADF4351/MAX2870 or the tinySA.

**Example 3 — sensitivity test of an SX1278 433 MHz receiver with a tinySA Ultra as the source.** The tinySA can only produce CW/AM/FM, not LoRa — so use it to measure the receiver's CW **RSSI calibration** and blocking, and use a second LoRa module for PER tests. Levels: tinySA at −70 dBm (±2 dB [2]) → calibrated 30 dB pad (30.08 dB measured) → DUT at −100.1 dBm; for −130 dBm add another 30 dB — isolation needed ≥ 80 dB beyond the 60 dB of pads, so put the tinySA and DUT in separate tins.

**Example 4 — attenuator stack budget.** Four uncalibrated pads (30 + 30 + 10 + 20 dB, ±0.2–0.3 dB each) give 90 dB ± 1.05 dB worst case (±0.53 dB RSS); VNA-calibrated to ±0.03–0.05 dB each: ±0.17 dB worst case (±0.09 dB RSS). With pad SWR 1.2 the three interfaces add up to ±0.21 dB of mismatch ripple; SWR 1.05 pads only ±0.015 dB (script §4). Calibrate the *assembled* stack as one two-port on the VNA if possible (for > 80 dB the VNA's dynamic range becomes the limit — calibrate pads individually and sum).

**Example 5 — LoRa waveform source.** For true PER sensitivity tests you need a LoRa-modulated signal: a second radio (known conducted power, measured with a power meter) or an SDR replaying an IQ recording (HackRF/Pluto; filter and calibrate as in [SDR as test equipment](sdr-as-test-equipment.md)). Reduce its output at the source first (radio set to its minimum power, e.g. −9 dBm on SX126x-class parts) to lower the isolation requirement.

## Practical notes
- **Buying used**: HP 8648A/B/C (100 kHz–1/2/3.2 GHz), HP 8656B (to 990 MHz), Agilent E4400B/E4421B ESG are common on the used market; check the output attenuator (a clicking relay stack) and the level accuracy against a power meter; a failed reverse-power protection is common after someone keyed a transmitter into it.
- **New budget generators**: Siglent SSG3000X, Rigol DSG800 series; the Siglent SSA3000X Plus analyzers include a tracking generator option useful for filter sweeps.
- **Synthesiser boards**: power them from a clean LDO (switching noise → spurs), use a good 10/25 MHz reference (TCXO or external GPSDO), and shield the board (tin box) — they also radiate.
- **Reverse power**: never let a transmitter feed back into a generator; use a circulator/isolator or a high-value pad.
- **Label every pad** with its measured loss at 433/868/915/1575/2450 MHz and its SWR; store the .s2p files.
- **Frequency accuracy**: a 25 MHz reference at ±10 ppm puts a 915 MHz output ±9 kHz off — relevant for LoRa, whose receivers tolerate only a fraction of the channel bandwidth of carrier offset (see [LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)).

## Common mistakes & misconceptions
- **Trusting register-set output levels** on synthesiser boards (±1 dB at best, more with a mismatched load).
- **Measuring a filter's stopband with an unfiltered ADF4351** — the source's own harmonics fall in the stopband and look like filter leakage.
- **Stacking uncalibrated pads for a −130 dBm claim.**
- **Ignoring leakage** — the generator radiates, the DUT picks up.
- **Using a noisy interferer in a blocking test** and attributing the desense to the receiver.
- **Driving a DUT input with DC-coupled generator output** without a DC block when the DUT has bias.

## How to simulate / verify
- `python3 tools/verify/meas_siggen.py` — (1) square-wave harmonics vs duty; (2) LPF order for −50 dBc (Butterworth/Chebyshev); (3) ADF4351 in-band phase-noise estimate; (4) attenuator-stack uncertainty and mismatch; (5) low-level budget and isolation.
- Filter prototypes: `tools/verify/circuits_filter_prototypes.py` (domain 01); build the LPF in SPICE/QUCS with real component models ([component models](../04-real-components-hf/component-models-s2p-spice.md)).

## Open questions / gaps
- MAX2870 specifics (23.5 MHz–6 GHz, harmonics, phase noise) were not verified against its datasheet here.
- Used-equipment model ranges are from general knowledge; confirm with the specific unit's manual.
- Si5351 upper frequency (~200 MHz) quoted from general knowledge (the NanoVNA pages say "up to ~300 MHz" in their use).

## Sources
1. Analog Devices, *ADF4351 Wideband Synthesizer with Integrated VCO* datasheet Rev. 0 — 35 MHz–4.4 GHz (VCO 2.2–4.4 GHz, ÷1…64), output −4…+5 dBm in 3 dB steps ±1 dB, H2 −19/−20 dBc and H3 −13/−10 dBc (fundamental/divided), VCO phase noise table, normalised floor −220/−221 dBc/Hz, 1/f −116/−118 dBc/Hz, PFD spurs −80 dBc, in-band noise formula. (datasheet; read, utoronto mirror)
2. tinySA wiki, "TinySA4 Specification" — signal-generator section (levels, accuracy, harmonics, modes above 800 MHz). (vendor docs; read)
3. Great Scott Gadgets, *HackRF One* documentation — TX power vs frequency. (vendor docs; read)
4. Keysight AN 150 and AN 1449-series — generator and level-accuracy background. (app notes; cited)
5. This repository: `tools/verify/meas_siggen.py`. (verification)
