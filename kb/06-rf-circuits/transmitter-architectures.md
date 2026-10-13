---
title: Transmitter architectures (direct up-conversion, two-step, polar, IQ-modulator impairments, masks, spurs)
domain: 06-rf-circuits
slug: transmitter-architectures
tags: [transmitter, direct-upconversion, iq-modulator, sideband-suppression, carrier-leakage, lo-pulling, two-step, superheterodyne-transmitter, polar, eer, outphasing, spectral-mask, aclr, harmonics, spurious, lora-tx]
prerequisites:
  - mixers.md
  - power-amplifiers.md
  - vco-and-pll-synthesizers.md
related:
  - receiver-architectures.md
  - rf-filters-lc-saw-baw-cavity-microstrip.md
  - ../10-comms-modulation/digital-modulation-psk-qam-fsk.md
  - ../14-sdr-dsp/nco-ddc-duc.md
  - ../19-regulations-safety/certification-fcc-ce-imda.md
  - ../15-lora-ism-radios/rocket-telemetry-radio-design.md
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Transmitter architectures

## Questions this page answers
- How does an IQ (direct up-conversion) transmitter work, and what limits its spectral purity?
- What causes carrier (LO) leakage and the unwanted sideband, and how good must I and Q be?
- Why do direct-conversion transmitters get "pulled" by their own PA, and how is the VCO frequency planned to avoid it?
- When is a two-step (IF) transmitter better?
- How do polar (envelope-and-phase) and outphasing transmitters work, and what is hard about them?
- How does a LoRa/FSK transmitter differ from a QAM/OFDM one?
- What masks and spurious limits apply, and where do harmonics and spurs come from?

## TL;DR
- **Direct up-conversion (IQ modulator)**: baseband I/Q DACs → reconstruction filters → quadrature mixer at $f_{LO}=f_{RF}$ → PA. Simple and integrated (AD9361, most SDRs). Impairments: **unwanted sideband** from gain/phase imbalance (0.1 dB/1° → 39.6 dB suppression, 0.3 dB/3° → 30.1 dB, 1 dB/5° → 22.8 dB; formula = IRR, verified), **carrier leakage** from DC offsets (1 % → −40 dBc, 0.1 % → −60 dBc), LO harmonics, DAC images, and **LO pulling** by the PA output.
- **VCO frequency plan**: a VCO at $f_{RF}$ or $2f_{RF}$ coincides with the PA output or its 2nd harmonic and is injection-pulled; use a VCO at e.g. $4/3\,f_{RF}$ (divide/multiply), or an offset LO (verified plan check).
- **Two-step (IF) transmitter**: modulate at a fixed IF, filter, then up-convert: better image/LO suppression and avoids pulling, at the cost of an extra LO and an RF image filter.
- **Constant-envelope modulations** (FSK, GFSK, LoRa CSS) need no IQ amplitude path: the PLL/VCO is modulated directly (or a DDS/fractional-N is steered), and the PA runs saturated at best efficiency; spectral purity is set by the PLL (phase noise, spurs) and the harmonic filter.
- **Polar transmitters** split the signal into envelope $A(t)$ and phase $\varphi(t)$ — each far wider-band than the composite (16-QAM RC 0.35: 99 % bandwidth 1.05 → 2.12 (envelope) and 3.43 (phase-modulated carrier) symbol rates) — and require tight path alignment: EVM ≈ 1 % per 0.01 symbol of delay mismatch (0.02 → 1.9 %, 0.1 → 9.6 %, simulated).
- **Masks**: in-band ACLR/spectral mask from PA nonlinearity (DPD, back-off, [PA page](power-amplifiers.md)), close-in phase noise, and DAC/modulator noise; out-of-band harmonics and spurs from the PA, LO and DAC images — typically −30 to −54 dBm limits (ETSI EN 300 220 [3]) → 60–70 dB below a 2 W carrier.

## Intuition (no math)
Any bandpass signal can be written as a cosine carrier multiplied by an in-phase waveform I(t) plus a sine carrier multiplied by a quadrature waveform Q(t). An IQ modulator does exactly that with two mixers and a 90° LO splitter. If the two paths are not identical — slightly different gain, not quite 90° — part of the signal appears mirrored on the other side of the carrier (the "unwanted sideband"), and any DC in I or Q multiplies the LO into a pure carrier tone (carrier leakage). These are the same imbalances as in the receiver, seen from the other side.

In a direct-conversion transmitter the oscillator runs at the same frequency as the power amplifier's output. A few milliwatts of the PA's watt-level output leaking back to the VCO is enough to pull it off frequency (injection pulling), especially when the PA's output is modulated. So the VCO is placed at a different frequency and divided or mixed down, or the modulation is done at an IF.

For signals whose amplitude is constant — FSK and LoRa — the problem is much easier: you only need to steer the phase/frequency of an oscillator, then let a saturated PA amplify it efficiently. Polar transmitters try to extend this efficiency to amplitude-varying signals by modulating the PA's supply with the envelope while a constant-envelope phase-modulated carrier drives it; the difficulty is that the envelope and phase are nonlinear functions of I and Q with much wider spectra, and they must be recombined with near-perfect timing.

## The math

### Level 1
- Bandpass signal: $s(t)=I(t)\cos\omega_ct-Q(t)\sin\omega_ct=\mathrm{Re}\{[I+jQ]e^{j\omega_ct}\}=A(t)\cos[\omega_ct+\varphi(t)]$ with $A=\sqrt{I^2+Q^2}$, $\varphi=\arg(I+jQ)$.
- Sideband suppression (IQ imbalance, gain ratio $g$, phase error φ): $\frac{1+2g\cos\varphi+g^2}{1-2g\cos\varphi+g^2}$ — identical to the receiver IRR ([mixers](mixers.md#level-2--derivations)).
- Carrier leakage: DC offsets $(d_I,d_Q)$ on a signal of amplitude $a$ produce an LO tone at $20\log(\sqrt{d_I^2+d_Q^2}/a)$ dBc.
- EVM $=\sqrt{\overline{|e|^2}/\overline{|s|^2}}$.

### Level 2
**(a) Sideband and carrier.** With a Q path of gain $g$ and phase error φ, a baseband tone $e^{j\omega_mt}$ becomes $\frac{1+ge^{j\varphi}}{2}e^{j\omega_mt}+\frac{1-ge^{j\varphi}}{2}e^{-j\omega_mt}$ (after taking the analytic part of the RF), giving the suppression ratio above; DC offsets add a constant that up-converts to the carrier. Check G in `rfckt_rx_tx.py` reproduces the formula exactly for several imbalances.

**(b) Injection pulling.** An oscillator of loaded Q $Q_L$ perturbed by an injected signal of relative amplitude $\rho=V_{inj}/V_{osc}$ at offset Δω locks if $\Delta\omega<\frac{\omega_0}{2Q_L}\rho$ (Adler's condition) and is frequency-modulated (pulled) otherwise [2]. With the PA at the VCO frequency, $\rho$ from board coupling can be −40 to −60 dB — enough to pull a low-Q on-chip VCO by tens of kHz. Hence VCO ≠ $f_{RF}$, $2f_{RF}$: typical plans use $f_{VCO}=\frac43f_{RF}$ (VCO mixed with VCO÷4) or $2f_{RF}$ with a divider only when the PA is off-chip and well isolated.

**(c) Polar decomposition bandwidth.** $A(t)=|I+jQ|$ and $e^{j\varphi(t)}=(I+jQ)/A$ are nonlinear: near envelope zeros the phase jumps rapidly, so both spectra extend far beyond the signal bandwidth (script H: 2× and 3.3× for 16-QAM). A timing error τ between the paths gives an error vector ≈ $\tau\,\dot A$ — linear in τ — so the EVM ≈ $\tau\cdot\text{rms}(\dot A)/\text{rms}(A)$ (≈ 1 % per 1 % of a symbol period here). Envelope-tracking (ET) avoids the strict alignment by modulating the supply only coarsely while the PA remains linear.

**(d) Outphasing (LINC/Chireix).** $s=A\cos(\omega t+\varphi)$ = $\frac{A_{max}}{2}[\cos(\omega t+\varphi+\theta)+\cos(\omega t+\varphi-\theta)]$ with $\cos\theta=A/A_{max}$: two constant-envelope signals amplified by saturated PAs and summed. A lossless (Chireix) combiner gives load modulation (efficiency) but distortion; a Wilkinson combiner is linear but wastes the out-of-phase power ([combiners](couplers-dividers-combiners.md#level-2--derivations)).

**(e) Where spurs come from.** DAC images at $f_s\pm f_{bb}$ (sinc-shaped), LO harmonics mixing with baseband ($3f_{LO}\pm f_{bb}$ from a switching modulator), PLL reference/fractional spurs, PA harmonics, and supply-switching spurs (DC-DC converters modulate the carrier). Each needs a filter or a frequency-plan decision.

### Level 3 — architecture choices in practice
| Architecture | Strength | Weakness | Typical use |
|---|---|---|---|
| Direct IQ up-conversion | integration, wideband, any modulation | IQ imbalance, LO leakage, pulling | SDR transceivers, cellular, AD9361 |
| Two-step / IF | cleaner LO, easier filtering | extra LO + filters | high-performance radios, older designs |
| Direct VCO/PLL modulation | simplest, efficient, constant envelope | only FM/FSK/CSS-type modulation; PLL bandwidth limits data rate (two-point modulation fixes it) | LoRa, FSK, GFSK, Bluetooth, telemetry |
| Polar / EER | efficiency with amplitude modulation | alignment, envelope-modulator bandwidth | cellular handsets (some), research |
| Envelope tracking | efficiency gain with linear PA | supply-modulator design | cellular PAs |
| Outphasing | saturated PAs | combiner trade-offs | base stations, research |
| DDS / direct digital RF | agility, no analogue IQ | DAC spurs, power consumption | test equipment, radars |

Calibration (LO leakage nulling via DC offset trim, IQ gain/phase trim, DPD) is standard in integrated transmitters.

## Design equations & rules of thumb

| Quantity | Equation / value | Example |
|---|---|---|
| Sideband suppression | $\frac{1+2g\cos\varphi+g^2}{1-2g\cos\varphi+g^2}\approx4/(\epsilon^2+\varphi^2)$ | 0.1 dB/1° → 39.6 dB |
| Carrier leakage | $20\log(d/a)$ | 1 % → −40 dBc |
| Polar delay tolerance | EVM ≈ 1 % per 0.01 T_sym (16-QAM, RC 0.35) | 5 % of a symbol → 4.8 % |
| Envelope bandwidth | ≈ 2× signal bandwidth (99 %) | phase path ≈ 3–4× |
| Adler lock range | $\Delta\omega_L=\frac{\omega_0}{2Q}\frac{V_{inj}}{V_{osc}}$ | pulling risk estimate |
| Harmonic/spurious target | limit − P_out (dBc) | +33 dBm, −36 dBm → −69 dBc |

## Worked examples

### Example 1 — LoRa/FSK telemetry transmitter
The SX126x generates LoRa chirps and FSK by steering its fractional-N PLL (constant envelope), then a PA (+22 dBm internal on SX1262) — no IQ modulator, no carrier-leakage problem, PA efficiency near saturation. Spectral purity then depends on (i) PLL phase noise and spurs (adjacent-channel leakage), (ii) harmonics — the internal PA plus the reference matching network's low-pass must bring 2f₀/3f₀ below the regulatory limits, and an external PA (EBYTE E22-400T33D, 2 W) needs its own harmonic filter ([PA page](power-amplifiers.md#example-1--a-2-w-433-mhz-pa-with-an-ldmos-transistor)).

### Example 2 — SDR (AD9361/Pluto-class) as a test transmitter
Uncalibrated IQ balance of 0.3 dB / 3° gives only ≈ 30 dB image suppression and 1 % DC offset −40 dBc carrier leakage; the chip's built-in calibration improves both substantially. For transmitting a clean single tone, offset it from the LO (e.g. +250 kHz baseband) so the LO leakage and image can be distinguished and filtered in measurement.

### Example 3 — Choosing a VCO plan for a 915 MHz direct up-conversion transmitter
VCO at 915 MHz: coincides with the PA output → pulling. VCO at 1830 MHz ÷2: coincides with the PA's 2nd harmonic → still pulled. VCO at 1220 MHz, mixed with its own ÷4 output (1220 − 305 = 915 MHz, i.e. ×3/4): nearest PA harmonic 305 MHz away (script I); the mixing products at 1220 + 305 MHz and the VCO feedthrough must be filtered. Many integrated transceivers use such fractional relationships or a ÷2/÷3 selectable path.

### Example 4 — Polar transmitter timing budget
16-QAM at 1 Msym/s with RC 0.35: keeping EVM below 2 % requires envelope/phase alignment within ≈ 0.02 symbol = 20 ns; the envelope path (supply modulator) needs ≈ 2 MHz bandwidth and the phase path (PLL modulation) ≈ 3.4 MHz — hard for a PLL, hence two-point modulation (VCO + divider) in polar designs.

## Practical notes
- **Reconstruction filters** after the DACs set the DAC-image level; with a sinc droop, images at $f_s-f_{bb}$ are attenuated only slightly — oversample.
- **LO leakage calibration:** trim DC offsets on I and Q while observing the carrier on a spectrum analyser (or the chip's internal observation receiver).
- **TX turn-on:** PA ramp-up transients cause spectral splatter and VCO pulling; ramp the PA power (LoRa chips ramp automatically) and keep the PLL loop bandwidth wide enough to recover.
- **Supply spurs:** a DC-DC converter at 1–3 MHz on the PA or VCO supply appears as ±f_sw sidebands; filter or synchronise it.
- **Test:** spectrum analyser for mask, harmonics (with a notch/high-pass to protect the analyser's dynamic range) and spurs; a vector signal analyser (or SDR) for EVM.

## Common mistakes & misconceptions
- *"Direct-conversion TX is always clean because there is no IF."* IQ imbalance and DC offsets create the image and carrier; the LO can be pulled.
- *"Harmonics are the PA's problem."* LO harmonics, DAC images and switching spurs also land out of band.
- *"Polar is just AM + FM."* The envelope and phase components are much wider than the signal and must be precisely aligned.
- *"LoRa needs a linear PA."* It is constant envelope; a saturated/efficient PA is fine — but the harmonic filter is mandatory.
- *"If it passes in conducted tests it will pass radiated."* Radiation from the PA/matching area and cables can exceed conducted numbers.

## How to simulate / verify
- `tools/verify/rfckt_rx_tx.py` sections G–I: IQ modulator sideband suppression and carrier leakage, polar delay-mismatch EVM and bandwidth expansion, VCO/PA frequency-plan check.
- `tools/verify/rfckt_pa.py`: harmonic budgets, DPD/ACLR.
- GNU Radio / Python for EVM and mask simulations with measured PA models; spectrum/vector analysers for verification.

## Open questions / gaps
- Adler pulling magnitude for a specific VCO/PA layout is not quantified (depends on isolation, VCO Q).
- Two-point modulation (VCO + divider) for wideband PLL-based FSK is only mentioned.
- DAC image/sinc planning is covered only qualitatively here (see domain 14 NCO/DUC).

## Sources
1. B. Razavi, *RF Microelectronics*, 2nd ed., 2011, ch. 4 (transmitter architectures: direct, two-step, polar, outphasing; IQ mismatch, carrier feedthrough, LO pulling). (textbook)
2. R. Adler, "A study of locking phenomena in oscillators," *Proc. IRE*, 34(6), pp. 351–357, June 1946 (injection locking/pulling). (peer-reviewed)
3. ETSI EN 300 220-1 V3.1.1 (2017-02) spurious-domain limits (−54 dBm broadcast bands, −36 dBm other < 1 GHz, −30 dBm > 1 GHz). (standard)
4. F. H. Raab et al., "Power amplifiers and transmitters for RF and microwave," *IEEE Trans. MTT*, 50(3), pp. 814–826, 2002 (EER, ET, outphasing, polar). (peer-reviewed)
5. H. Chireix, "High power outphasing modulation," *Proc. IRE*, 23(11), pp. 1370–1392, 1935; D. C. Cox, "Linear amplification with nonlinear components," *IEEE Trans. Commun.*, 22(12), pp. 1942–1945, 1974. (peer-reviewed)
6. Semtech SX1261/2 data sheet (PLL-based LoRa/FSK modulation, +22 dBm PA on SX1262). (datasheet)
