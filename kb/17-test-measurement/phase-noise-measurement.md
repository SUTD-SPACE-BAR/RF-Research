---
title: Phase-noise measurement — direct spectrum-analyzer method and its corrections, phase-detector (PLL/quadrature) method, delay-line discriminator, two-channel cross-correlation, and low-cost setups
domain: 17-test-measurement
slug: phase-noise-measurement
tags: [phase-noise, l-of-f, dbc-hz, spectrum-analyzer, noise-marker, rbw, log-average, phase-detector, pll, quadrature, double-balanced-mixer, delay-line, frequency-discriminator, cross-correlation, sound-card, tcxo, vco, reciprocal-mixing, jitter, residual-phase-noise, additive-phase-noise, amplifier-flicker]
prerequisites: [../07-noise-linearity/phase-noise-and-jitter.md, spectrum-analyzers.md, ../05-analog-electronics/oscillators.md]
related: [signal-generators-and-sources.md, sdr-as-test-equipment.md, rf-bring-up-debug-playbook.md, ../06-rf-circuits/vco-and-pll-synthesizers.md, ../04-real-components-hf/crystals-and-resonators.md, ../07-noise-linearity/dynamic-range-sfdr-blocking.md, ../11-radar/fmcw-radar.md]
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# Phase-noise measurement

## Questions this page answers
- How do I measure an oscillator's phase noise L(f) with a spectrum analyzer, and which corrections apply?
- Why does every TCXO I measure look like −98 dBc/Hz at 10 kHz?
- What is the phase-detector (PLL) method, and how do I calibrate it?
- When is a delay-line discriminator useful?
- How does cross-correlation measure noise below the instrument's own floor, and how long does it take?
- What can I do on a student budget (tinySA, SDR, sound card, mixer)?
- How does a 32 MHz TCXO's phase noise show up at 915 MHz?
- How much phase noise does an amplifier add to a clean carrier, and how do I measure it?
- Can I average phase noise away?

## TL;DR
- **Direct SA method**: L(f) = P(offset, in RBW) − P_carrier − 10 log(ENBW) (+2.51 dB if the trace was log-averaged) [1]. Our synthetic test recovers L within ≤ 0.15 dB for offsets ≥ 30× RBW (0.65 dB at 10× RBW on a steep −20 dB/decade slope). It measures AM + PM noise together and **cannot see below the analyzer's own phase noise**: SSA3021X Plus ≈ −98 dBc/Hz at 10 kHz (1 GHz) [2], tinySA Ultra −108 dBc/Hz at 100 kHz (30 MHz) [3], LibreVNA SA −103 dBc/Hz at 10 kHz (1 GHz) [4].
- The DUT must be ≥ 10 dB above the analyzer for < 0.4 dB error (equal levels read 3 dB high; 20 dB above → 0.04 dB).
- **Phase-detector method**: mix the DUT with a quiet reference in quadrature (a PLL holds 90°) in a double-balanced mixer; the baseband voltage is K_φ·Δφ; S_φ = S_v/K_φ², L = S_φ/2. Calibrate K_φ from the beat-note amplitude. If the reference is an identical oscillator, subtract 3 dB. Offsets inside the PLL bandwidth are suppressed and must be corrected.
- **Delay-line discriminator**: no reference needed, but its sensitivity relative to a phase detector is 4 sin²(πfτ): a 200 ns line is 58 dB less sensitive at 1 kHz offset (script) — good for noisy free-running VCOs (radar chirp sources), poor for crystal oscillators.
- **Cross-correlation** (two independent channels, average m cross-spectra): the uncorrelated background falls ≈ **5 log₁₀ m dB** — 10× the averaging buys 5 dB [5] (simulated: −5.0/−10.1/−15.0/−20.3 dB at m = 10/100/1000/10 000).
- **Amplifiers add residual phase noise**: a white floor $FkT_0/(2P_0)$ (−144 dBc/Hz for NF 3 dB at −30 dBm input, so drive it harder) plus 1/f noise that is nearly independent of drive (≈ −105 to −142 dBrad²/Hz at 1 Hz). Measure with a split source and arm delays matched to ≪ 1 ns [9].
- **Multiplication adds 20 log N**: a 32 MHz TCXO appears +29.1 dB higher at 915 MHz, a 26 MHz GNSS TCXO +35.6 dB higher at 1575 MHz (inside the synthesiser loop bandwidth). A −140 dBc/Hz TCXO becomes ≈ −111 dBc/Hz at 915 MHz — still below any budget analyzer.

## Intuition (no math)
A perfect oscillator is a single spectral line. A real one wanders slightly in phase, which smears a little power into "skirts" either side of the carrier. Phase noise L(f) is how much power sits in a 1 Hz slice at offset f, relative to the carrier. A spectrum analyzer can show those skirts directly — but it is itself built around an oscillator (its LO), and its skirts are added to yours. For clean crystal oscillators the analyzer's skirts are usually the bigger ones, so the display is just the analyzer's own phase noise.

The better methods cancel the carrier and look only at the fluctuations: a mixer driven by two signals at 90° gives an output voltage proportional to their phase *difference*. If the reference is much quieter than the DUT, that voltage is the DUT's phase noise, now at baseband where a cheap ADC or even a sound card can analyse it. Cross-correlation goes one step further: use two such channels with independent references and noise, and average the product of their outputs — only what both channels share (the DUT) survives.

## The math

### Level 1 — definitions and the direct method
- L(f) (dBc/Hz): single-sideband phase-noise power in 1 Hz at offset f relative to the carrier; in the small-angle regime L(f) = S_φ(f)/2 (IEEE Std 1139 convention; theory in [phase noise & jitter](../07-noise-linearity/phase-noise-and-jitter.md)).
- **Direct SA measurement** [1]:
$$\mathcal L(f)\approx P_{\text{offset}}\,[\text{dBm in RBW}]-P_{\text{carrier}}\,[\text{dBm}]-10\log_{10}(\text{ENBW}/1\,\text{Hz})+C_{\text{det}},$$
with ENBW ≈ 1.065 × RBW (Gaussian) and C_det = +2.51 dB for log-averaged noise (0 for RMS/power averaging), as derived on [spectrum analyzers](spectrum-analyzers.md). Analyzers' noise markers or phase-noise personalities apply these corrections.
- **Additive floor**: the display shows L_DUT + L_SA (in linear power): error = 10 log(1 + 10^{−X/10}) for a DUT X dB above the analyzer (3.01, 1.76, 0.97, 0.41, 0.14, 0.04 dB at X = 0, 3, 6, 10, 15, 20).
- **Frequency multiplication/division** by N: L changes by ±20 log N (phase deviation scales by N).

### Level 2 — phase-detector and discriminator methods
**Quadrature phase detector.** A double-balanced mixer driven by v_R = A cos(ω₀t) and v_D = B cos(ω₀t + π/2 + φ(t)) produces (after low-pass) v(t) = K_φ sin φ(t) ≈ K_φ φ(t) for small φ; K_φ (V/rad) is the peak amplitude of the beat note obtained when the two sources are offset in frequency (the beat is K_φ sin(Δω t)). Then
$$S_\phi(f)=\frac{S_v(f)}{K_\phi^2},\qquad \mathcal L(f)=\frac{S_v(f)}{2K_\phi^2}.$$
A PLL (loop bandwidth f_L) steers the reference to keep quadrature; below f_L the loop tracks and suppresses the measured noise by |1/(1 + G(f))|², so either keep f_L below the smallest offset of interest or correct for the loop response. If both oscillators are equally noisy and uncorrelated, the result is the sum — subtract 3 dB for one of them. The measurement floor is set by the baseband amplifier/ADC noise density e_n: L_floor = e_n²/(2K_φ²) (e.g. K_φ = 0.2 V/rad and e_n = 5 nV/√Hz → −155 dBc/Hz).

**Delay-line frequency discriminator.** Split the DUT; delay one path by τ; mix in quadrature. The phase difference is φ(t) − φ(t − τ), whose transfer function in frequency is (1 − e^{−j2πfτ}), so
$$|H(f)|^2=4\sin^2(\pi f\tau)\approx(2\pi f\tau)^2\ \ (f\ll 1/\tau).$$
The method needs no reference and tolerates drifting sources, but its sensitivity collapses close in (script §3: τ = 50 ns → −70 dB at 1 kHz; 200 ns → −58 dB; 1 µs → −44 dB) and has nulls at f = n/τ. Long delays cost loss (200 ns ≈ 40 m of v_f 0.66 coax ≈ 18 dB at 900 MHz in RG-58) that reduces K_φ. Hence it suits free-running VCOs, YIGs and radar chirp sources, not crystal references.

**Cross-correlation.** Two channels measure y = c + a and x = c + b with a, b independent instrument noise and c the DUT. The averaged cross-spectrum ⟨S_yx⟩_m = S_cc + O(1/√m) [5]: the instrument terms average down as 1/√m in amplitude, i.e. the effective floor drops 5 log₁₀ m dB — 5 dB per decade of averaging (simulation §4 matches to ±0.3 dB, and the DUT at −10 dB below each channel's background is recovered as −10.0 dB for m ≥ 1000). To see a DUT 20 dB below the single-channel background at 0 dB SNR needs m ≈ 5 × 10³ spectra per Rubiola & Vernotte [5]. Correlated instrument noise (crosstalk, shared supply, AM-to-PM of shared splitters) sets a hard floor that averaging cannot beat [5].

### Level 3 — what actually limits you
- **AM noise**: the SA measures L_PM + L_AM; mixers in saturation reject AM (a phase detector with both ports driven hard), which is one reason the phase-detector method reads lower.
- **Offset vs RBW**: the RBW skirt leaks carrier into the offset bin; an ideal Gaussian is −48 dB at 2× RBW and −108 dB at 3× RBW (script §6), but real analog RBW filters (60:3 dB shape factors ~4–15) are far worse — keep offset ≥ 5–10 × RBW and verify by halving the RBW (a genuine noise level in dBc/Hz does not change).
- **Small-angle limit**: L(f) and S_φ/2 agree only where the integrated phase deviation beyond f is ≪ 1 rad; close to a free-running VCO's carrier the spectrum becomes a Lorentzian/Gaussian line and "L(f)" loses meaning.
- **Spurs vs noise**: discrete spurs (dBc) do not scale with RBW, noise (dBc/Hz) does; changing RBW distinguishes them.

### Additive (residual) phase noise of amplifiers and other two-ports
An amplifier, multiplier, divider or mixer that carries a carrier adds its own phase noise, called **residual** or **additive** phase noise. It is a property of the two-port, measured with a clean source whose own noise is cancelled. It has two parts [9]:
- *White floor* from the amplifier's additive noise: $b_0 = S_\varphi = FkT_0/P_0$ with $P_0$ the carrier power at the amplifier **input**, so $\mathcal L_\text{floor} = FkT_0/(2P_0)$. This is the same bookkeeping as the Leeson floor ([canonical values](../00-math-foundations/canonical-values-and-conventions.md)). In dB: $\mathcal L_\text{floor} = -173.98 + \text{NF} - P_0 - 3.01$ dBc/Hz. An LNA (NF 3 dB) carrying a −30 dBm carrier gives **−144 dBc/Hz**; the same amplifier at −10 dBm gives −164; an LO buffer (NF 6 dB) at 0 dBm gives −171 (`tools/verify/s7_receiver_numbers.py` §3). **Drive the noisy stage hard.** A weak carrier through a good LNA still collects a floor that can exceed a quiet source's far-out noise.
- *Flicker (1/f) phase noise* $S_\varphi = b_{-1}/f$. Here $b_{-1}$ is set by up-conversion of the device's low-frequency fluctuations and is **roughly independent of carrier power** [9]. Measured $b_{-1}$ values span about −105 to −142 dBrad²/Hz across the amplifiers in Boudot & Rubiola's Table 1: a SiGe LPNT32 at 3.5 GHz −130, an Avantek UC573 at 0.01–0.5 GHz −141.5, X-band amplifiers −105 to −122 [9]. At −130 dBrad²/Hz, $\mathcal L$ = −133 dBc/Hz at 1 Hz and −153 at 100 Hz. The corner where white and flicker are equal is $f_c = b_{-1}P_0/(FkT_0)$: 12.5 Hz at −30 dBm, **12.5 kHz at 0 dBm** for NF 3 dB. It moves with drive level, so a quoted "corner" is meaningless without $P_0$ [9].
- *Combining stages.* White floors cascade like noise figure, so the first stage dominates. Flicker contributions are independent per stage and **add**: $m$ equal amplifiers in cascade give $+10\log m$ (two: +3 dB). $m$ in parallel, combined, give $-10\log m$ ideally, about 2.5 dB per doubling in practice [9]. Frequency multiplication by $N$ adds $20\log N$ to everything upstream, including the residual noise of the stages before the multiplier.
- *Measuring it.* Split one source into a reference arm and a DUT arm, add a phase shifter for quadrature, and drive a saturated double-balanced mixer as the phase detector (Level 2). The source's own phase noise is common to both arms and cancels, apart from a delay mismatch $\Delta\tau$ that leaks it through $4\sin^2(\pi f\Delta\tau)$, as in the delay-line discriminator. 1 ns of mismatch suppresses the source by 84 dB at 10 kHz but only 44 dB at 1 MHz, and 10 ns gives only 24 dB at 1 MHz. Match the arm lengths, or a −140 dBc/Hz source floor leaks in at −164 dBc/Hz. The mixer's own background (flicker ≈ −140 dBrad²/Hz for RF mixers, −120 for microwave mixers [9]) limits the method. Carrier-suppression bridges reach −150 to −180 dBrad²/Hz [9].
- *Why it matters here.* For receivers, the LO chain's buffers and multipliers set the far-out floor that drives reciprocal mixing ([dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)). For FMCW and Doppler radar, the residual noise of the TX/LO amplifiers is *not* cancelled by the range correlation that cancels the source's noise. For the "averaging" myth see Common mistakes: averaging never removes a two-port's residual noise either.

## Design equations & rules of thumb

| Quantity | Relation / value | Notes |
|---|---|---|
| Direct method | L = P_off − P_c − 10 log ENBW (+2.51 log-avg) | ENBW = 1.065 RBW |
| DUT above SA by X dB | error = 10 log(1 + 10^{−X/10}) | X ≥ 10 dB → < 0.4 dB |
| Offset vs RBW | offset ≥ 5–10 × RBW | halve RBW to check |
| Phase detector | L = S_v/(2K_φ²) | K_φ = beat-note peak (V/rad) |
| Two identical DUTs | subtract 3 dB | uncorrelated |
| Detector floor | e_n²/(2K_φ²) | 5 nV/√Hz, 0.2 V/rad → −155 dBc/Hz |
| Delay line | \|H\|² = 4 sin²(πfτ) | nulls at n/τ |
| Cross-correlation | background −5 log₁₀ m dB | hardware (correlated) limit remains |
| Multiplication | +20 log N | 32 → 915 MHz: +29.1 dB |
| Amplifier residual white floor | $\mathcal L = FkT_0/(2P_0)$ = −173.98 + NF − P₀ − 3.01 | NF 3 dB, −30 dBm in: −144 dBc/Hz |
| Amplifier flicker | $\mathcal L = b_{-1}/(2f)$, $b_{-1}$ ≈ independent of $P_0$; corner $f_c = b_{-1}P_0/(FkT_0)$ | −130 dBrad²/Hz: −153 dBc/Hz at 100 Hz |
| Residual test delay mismatch | source leak $4\sin^2(\pi f\Delta\tau)$ | 1 ns: −84 dB at 10 kHz, −44 dB at 1 MHz |

## Worked examples

**Example 1 — "every TCXO is −98 dBc/Hz".** An SX1262 in CW mode at 915 MHz, −10 dBm at the analyzer (Siglent SSA3021X Plus). At 10 kHz offset, RBW 1 kHz, log-averaged marker −80.5 dBm: L = −80.5 − (−10) − 10 log(1065) + 2.51 = −80.5 + 10 − 30.3 + 2.5 = **−98.3 dBc/Hz**, which equals the analyzer's own typical −98 dBc/Hz [2]: you have measured the analyzer. The radio's true phase noise is probably 10–20 dB lower. Conclusion: the direct method with this SA can only confirm "better than about −95 dBc/Hz at 10 kHz".

**Example 2 — a free-running 5.8 GHz video-transmitter or radar VCO.** Reading −75 dBc/Hz at 100 kHz offset on an analyzer specified at −96 to −97 dBc/Hz at 100 kHz (at 1 GHz; worse at 5.8 GHz): margin ≈ 20 dB → error ≈ 0.04 dB. The direct method is fine for noisy sources. For FMCW radar, the phase noise at the beat-frequency offsets sets the close-in noise floor ([FMCW radar](../11-radar/fmcw-radar.md)).

**Example 3 — phase-detector setup on a budget for a 32 MHz TCXO.** Two identical TCXOs (one pullable/VCTCXO as reference), a Mini-Circuits-class double-balanced mixer, a low-pass filter, a low-noise baseband amplifier (op-amp with ~1–5 nV/√Hz) and a sound card or 24-bit audio ADC (offsets 10 Hz–20 kHz) or an SDR/ADC for higher offsets. Calibrate: offset the VCTCXO by ~100 Hz, read the beat amplitude, e.g. 0.20 V peak → K_φ = 0.20 V/rad. Lock with a slow PLL (f_L ≈ 1 Hz) via the VCTCXO's tuning pin. Measured baseband noise at 1 kHz: 20 nV/√Hz → S_φ = (20 × 10⁻⁹/0.2)² = 10⁻¹⁴ rad²/Hz → L = 5 × 10⁻¹⁵ = −143 dBc/Hz for the pair; −146 dBc/Hz each if identical. Check the floor by driving both mixer ports from one split source (the "same-source" test): the result must be ≥ 10 dB lower.

**Example 4 — what the TCXO means at 915 MHz.** A −140 dBc/Hz (at 10 kHz) 32 MHz TCXO multiplied to 915 MHz: −140 + 29.1 = −110.9 dBc/Hz inside the synthesiser's loop bandwidth (outside it, the VCO's own noise dominates). For a LoRa receiver this sets reciprocal mixing: a blocker 1 MHz away at −40 dBm with L(1 MHz) = −120 dBc/Hz dumps −40 − 120 + 10 log(125 kHz) = −109 dBm of noise into the channel — far above the −137 dBm sensitivity. That is measured end-to-end by a blocking test ([dynamic range & blocking](../07-noise-linearity/dynamic-range-sfdr-blocking.md)), which is often the practical way to verify phase noise on a finished radio.

**Example 5 — cross-correlation budget.** A two-channel SDR-based correlator whose single-channel floor is −150 dBc/Hz at 10 kHz, measuring a DUT at −165 dBc/Hz: the DUT is 15 dB below; to push the background 25 dB down (≥ 10 dB below the DUT) needs m ≈ 10^{25/5} = 10⁵ averages; at 1 Hz resolution bandwidth for a 10 Hz offset that is 10⁵ s (28 h) — cross-correlation time explodes at close-in offsets.

## Practical notes
- **Direct method settings**: RMS detector + power averaging (or log with +2.51 dB), offset ≥ 5–10 × RBW, span wide enough to see the carrier and the offset, carrier level near the analyzer's optimum (not compressing), and several averages; subtract the analyzer's own phase noise (measure a cleaner source first) only when the DUT is ≥ 5–10 dB above it.
- **Spurs**: switching regulators, the MCU clock and PLL reference spurs appear as discrete lines; they are specified in dBc, not dBc/Hz.
- **Budget hardware**: a tinySA Ultra or Siglent can judge VCOs, cheap synthesiser boards (ADF4351, see [signal generators](signal-generators-and-sources.md)) and anything worse than ≈ −100 dBc/Hz; LibreVNA's SA mode similarly (−103 dBc/Hz at 10 kHz) [4]. For crystal-grade sources use the phase-detector method or borrow a dedicated analyzer (Keysight E5052/SSA-X, R&S FSWP; Microchip 53100A-class cross-correlators) from a lab.
- **Frequency stability vs phase noise**: very close-in (< 1 Hz) behaviour is better characterised in the time domain (Allan deviation with a counter or a phase recorder) — see [crystals and resonators](../04-real-components-hf/crystals-and-resonators.md).
- **Record**: carrier power, RBW, detector, averaging, analyzer model and its spec at the offset, so a reader can judge whether the result is DUT-limited.

## Common mistakes & misconceptions
- **Reporting the analyzer's phase noise as the DUT's** — always compare with the analyzer spec at that offset and carrier frequency.
- **Forgetting the log-average (+2.5 dB) and ENBW (−0.27 dB) corrections** when reading L manually.
- **Offset too close to the RBW** — carrier skirt leaks into the reading.
- **Mixing up dBc (spur) and dBc/Hz (noise)**.
- **Assuming L at 915 MHz equals the TCXO's datasheet value** — it is 20 log N worse inside the loop, and the VCO's own noise outside it.
- **Delay-line method on a TCXO** — tens of dB too insensitive close in.
- **Believing a cross-correlator reading without checking the correlated floor** (e.g. with a shared-source test).
- **"Phase noise can be averaged out."** Averaging acts on the *measurement*, not on the oscillator. Trace/power averaging only reduces the scatter of the estimated $L(f)$ (its mean stays put, and log-averaging biases it 2.51 dB low); cross-correlation removes the *instrument's* uncorrelated noise (5 log₁₀ m dB) but leaves the DUT's phase noise exactly where it was — that is the point of the method. In a system, an oscillator's phase noise is a random process already imprinted on every sample: reciprocal mixing, EVM, radar Doppler skirts and ADC-clock jitter SNR ([phase noise & jitter](../07-noise-linearity/phase-noise-and-jitter.md)) are not improved by averaging the received signal, because the phase error differs from packet to packet. What *does* reduce its effect: a cleaner reference/PLL, a wider loop bandwidth around a noisy VCO, coherent architectures where TX and RX share the oscillator and the delay is short (FMCW range correlation, [11 FMCW](../11-radar/fmcw-radar.md)), or tracking loops that follow slow phase wander. (Half-addressed myth from W4-D1, electronics.stackexchange.com/q/384128.)

## How to simulate / verify
- `python3 tools/verify/meas_phase_noise.py` — (1) direct SA method on a synthetic oscillator with known L(f) (error ≤ 0.15 dB at ≥ 30× RBW, 0.65 dB at 10× RBW on a steep slope); (2) additive analyzer floor; (3) delay-line sensitivity table; (4) cross-correlation convergence ≈ 5 log m; (5) 20 log N multiplication; (6) RBW-skirt leakage.
- `python3 tools/verify/s7_receiver_numbers.py` §3 — residual white floor vs drive, flicker levels and corner, cascade rule, delay-mismatch leakage.
- Theory cross-checks (L ↔ jitter integration): `tools/verify/noise_phase_jitter.py` (domain 07).

## Open questions / gaps
- No low-cost open-source cross-correlation phase-noise analyzer was evaluated; community SDR-based correlators exist but were not verified.
- The SSA3021X Plus phase-noise spec is at 1 GHz; its value at 5.8 GHz (Example 2) was not found in the datasheet read.
- The HP/Agilent product notes on the phase-detector (11729B-1) and discriminator (11729C-2) methods were not retrieved; the method descriptions here are derived from first principles and Rubiola [5].

## Sources
1. Keysight AN 150, *Spectrum Analysis Basics*, 5952-0292 — phase noise on an SA, RBW, noise-marker corrections (log-average 2.5 dB, ENBW). (app note; read)
2. Siglent, *SSA3000X Plus Data Sheet* DS0703P-E04B — SSB phase noise at 1 GHz: −95 (typ −98) dBc/Hz at 10 kHz, −96 (−97) at 100 kHz, −115 (−117) at 1 MHz for the SSA3021X Plus. (datasheet; read)
3. tinySA wiki, "TinySA4 Specification" — phase noise −108 dBc/Hz at 100 kHz, −115 dBc/Hz at 1 MHz (30 MHz carrier). (vendor docs; read)
4. LibreVNA Preliminary Specifications — SA-mode phase noise −103 dBc/Hz at 1 GHz, 10 kHz offset. (vendor; read)
5. E. Rubiola and F. Vernotte, "The cross-spectrum experimental method," arXiv:1003.0113 (2010) — ⟨S_yx⟩_m = S_cc + O(1/√m), 5 dB per decade of averaging, statistical vs hardware limit, required m. (tutorial/preprint by metrology researchers; read)
6. E. Rubiola, *Phase Noise and Frequency Stability in Oscillators*, Cambridge University Press, 2008 — phase-detector, discriminator and correlation methods. (textbook; cited)
7. IEEE Std 1139-2008, *Definitions of Physical Quantities for Fundamental Frequency and Time Metrology — Random Instabilities* — L(f) = S_φ/2 convention. (standard; cited)
8. This repository: `tools/verify/meas_phase_noise.py`, `tools/verify/s7_receiver_numbers.py`. (verification)
9. R. Boudot and E. Rubiola, "Phase noise in RF and microwave amplifiers," arXiv:1001.2047 v2 (31 Jan 2012). Read via ar5iv on 2026-10-12; the journal version was not checked. (preprint by metrology researchers) — $b_0 = FkT_0/P_0$; $b_{-1}$ roughly independent of $P_0$; Table 1 measured $b_{-1}$; cascade and parallel rules; saturated-mixer and carrier-suppression-bridge backgrounds. Also E. Rubiola, V. Giordano, arXiv:physics/0602110 (2006), which derives the amplifier white-PM term $b_0 = FkT_0/P_0$ (cited from the search listing).
