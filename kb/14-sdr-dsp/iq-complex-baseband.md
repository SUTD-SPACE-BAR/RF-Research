---
title: IQ signals and complex baseband in SDRs — quadrature mixing, negative frequencies, IQ imbalance, DC spike and offset tuning
domain: 14-sdr-dsp
slug: iq-complex-baseband
tags: [iq, complex-baseband, quadrature, analytic-signal, hilbert, negative-frequency, zero-if, low-if, iq-imbalance, image-rejection, dc-offset, lo-leakage, offset-tuning, fs-over-4, sdr]
prerequisites: [../00-math-foundations/complex-numbers-and-phasors.md, sampling-aliasing-bandpass-sampling.md, ../00-math-foundations/fourier-series-and-transform.md]
related: [nco-ddc-duc.md, fft-spectral-analysis-windows.md, multirate-dsp-decimation-cic.md, software-demodulation.md, sdr-hardware-survey.md, ../06-rf-circuits/receiver-architectures.md, ../06-rf-circuits/mixers.md, ../10-comms-modulation/digital-modulation-psk-qam-fsk.md, ../10-comms-modulation/synchronization-carrier-timing.md, ../10-comms-modulation/ofdm.md, ../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md, ../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# IQ signals and complex baseband in SDRs

## Questions this page answers
- Why do SDRs deliver *complex* samples (I and Q) instead of ordinary real numbers?
- What is a "negative frequency" on my SDR's waterfall?
- How does a quadrature (IQ) mixer turn an RF signal into I and Q, and how does a transmitter go back?
- What is that spike right in the middle of my SDR spectrum, and how do I get rid of it?
- Why do I see a faint mirror copy of a strong signal on the opposite side of the centre frequency (HackRF, Pluto, LimeSDR)?
- How much image rejection does 0.1 dB of gain error and 1° of phase error give me?
- What is "offset tuning", and what does it *not* protect me from?
- Is the RTL-SDR a zero-IF receiver?
- How do I correct IQ imbalance in software?
- What are analytic signals and the Hilbert transform used for in practice?
- How many Hz off will my 433.92 MHz signal appear for a given ppm error?

## TL;DR
- A real RF signal near $f_c$ is completely described by a slowly-varying complex number $\tilde x(t) = I(t) + jQ(t)$: $x(t) = \mathrm{Re}\{\tilde x(t)e^{j2\pi f_ct}\} = I\cos2\pi f_ct - Q\sin2\pi f_ct$. The SDR hands you $\tilde x[n]$. Basics on [complex numbers & phasors](../00-math-foundations/complex-numbers-and-phasors.md).
- **Negative baseband frequency = below the tuned centre.** A signal at $f_c + \Delta$ appears at $+\Delta$; one at $f_c-\Delta$ at $-\Delta$. Only a *complex* (two-channel) signal can tell the two apart — a single real mixer folds them on top of each other.
- **IQ imbalance** (Q-path gain ratio $g$, phase error $\varphi$) makes $y = \mu\tilde x + \nu\tilde x^*$: every signal at $+\Delta$ gets a mirror image at $-\Delta$, down by the **image rejection ratio** $\mathrm{IRR} = \dfrac{1+2g\cos\varphi+g^2}{1-2g\cos\varphi+g^2}\approx\dfrac{4}{\varepsilon^2+\varphi^2}$. 0.1 dB/1° → 39.6 dB; 0.5 dB/2° → 29.5 dB; 1 dB/5° → 22.8 dB.
- **The centre (DC) spike** in zero-IF SDRs comes from LO leakage self-mixing, baseband/ADC offsets, and even-order distortion of strong signals. Cures: DC calibration, a DC-blocking filter ($y[n]=x[n]-x[n-1]+\alpha y[n-1]$, −3 dB at ≈ $(1-\alpha)f_s/2\pi$: 382 Hz for $\alpha=0.999$ at 2.4 MS/s), or **offset tuning**.
- **Offset tuning**: tune the LO a few hundred kHz away, then shift digitally with an NCO; the spike and 1/f noise land outside your channel filter (script: spike suppressed by 86 dB). Catch: your channel now receives the **image of whatever sits at the mirror frequency** $f_{LO}-(f_{sig}-f_{LO})$ — check it's quiet.
- **RTL-SDR (R820T2/R828D) is low-IF, not zero-IF**: the tuner outputs a real IF ≈ 3.57 MHz and the RTL2832U digitises it and forms I/Q digitally, so it has no LO-leakage DC spike [8]. Older E4000 dongles were zero-IF.
- Blind **Gram–Schmidt IQ correction** (remove the I-correlated part of Q, equalise powers) takes 29 dB IRR to 47 dB with 16k samples and 71 dB with 262k; accuracy ∝ √(averaging length) [5].
- Frequency error scales with carrier: 1 ppm at 433.92 MHz = 434 Hz; 20 ppm = 8.7 kHz; 0.5 ppm at 1575.42 MHz = 788 Hz.

Verified by `tools/verify/dsp_iq.py` (all PASS).

## Intuition (no math)
Picture the RF signal as a spinning arrow (phasor) whose length is the amplitude and whose angle is the phase. The carrier makes it spin at 433.92 million turns per second — far too fast to watch. A quadrature downconverter is a strobe light flashing at exactly the carrier rate: in its light the carrier's rotation disappears and you see only the slow extra wobble — the modulation. To record that wobble completely you need two numbers per instant: how far the arrow points "east" (I, in-phase) and how far "north" (Q, quadrature). One number alone (just I) would be the arrow's shadow on a wall: you could not tell clockwise from anticlockwise drift.

Clockwise vs anticlockwise drift is precisely "below vs above" the strobe frequency, and that is what negative and positive frequencies on your waterfall mean. It's also why complex sampling gives you twice the viewable span of real sampling ([sampling](sampling-aliasing-bandpass-sampling.md)).

Real hardware builds the two "shadows" with two mixers driven by LO signals 90° apart, followed by two filters and two ADCs. If the two paths aren't perfectly matched — one slightly louder, or the LOs not exactly 90° apart — the arrow's path is squashed into an ellipse. An ellipse is the sum of a big circle turning one way and a small circle turning the other way: that small reverse circle is the **image**, a faint ghost at the mirror frequency. And if anything leaks a constant (the LO bleeding into the input and mixing with itself, or an amplifier offset), you get an arrow that doesn't rotate at all: a spike at exactly 0 Hz — the **DC spike**.

## The math

### Level 1 — the representation and what each symbol means
- $f_c$ (Hz): tuned centre (LO) frequency. $\tilde x(t) = I(t) + jQ(t)$: complex baseband (complex envelope), units of volts (or ADC counts / full-scale units in an SDR).
- Passband ↔ baseband: $x(t) = \mathrm{Re}\{\tilde x(t)e^{j2\pi f_ct}\} = I(t)\cos(2\pi f_ct) - Q(t)\sin(2\pi f_ct)$ (script §3 checks the identity).
- Amplitude and phase: $A(t) = |\tilde x| = \sqrt{I^2+Q^2}$, $\theta(t) = \mathrm{atan2}(Q,I)$; instantaneous frequency offset from $f_c$: $\Delta f(t) = \frac{1}{2\pi}\frac{d\theta}{dt}$.
- Frequency mapping: RF $f_c+\Delta \to$ baseband $+\Delta$ (script §2: $f_c \pm 150$ kHz → ±150 kHz; a single real mixer gives lines at both ±150 kHz for either input — the ambiguity).
- Power: with this (unscaled) convention the RF average power is $\tfrac12\overline{|\tilde x|^2}$ into a unit load. Some texts and many SDR drivers scale by √2 so the powers match; keep track when converting dBFS to dBm (see [FFT scaling](fft-spectral-analysis-windows.md)).
- A carrier offset $\delta f$ (from ppm error or Doppler) multiplies the baseband by $e^{j2\pi\delta f t}$ — the whole spectrum slides by $\delta f$; it is removed by multiplying by $e^{-j2\pi\delta f t}$ (an NCO). $\delta f = f_c\times\text{ppm}\times10^{-6}$.

### Level 1½ — I and Q as a clock hand, algebra only
- **Two mixers, 90° apart.** The receiver multiplies the signal by cos and by −sin of the LO and low-pass filters both. For an input of amplitude A whose phase relative to the LO is θ, this gives I = A cos θ and Q = A sin θ. The point (I, Q) is the tip of a clock hand of length A at angle θ.
- **Frequency is how fast the hand turns.** A signal Δ above the LO makes θ grow by 360°·Δ per second, so the hand turns counter-clockwise. A signal Δ below the LO turns it clockwise. That is the sign information a single real mixer cannot give.
- **Offsets are a slow turn.** A carrier error δf (ppm × f_c) adds a steady rotation of δf turns per second. Multiplying by $e^{-j2\pi\delta f t}$ turns it back.
- **Imbalance makes a mirror.** If the Q path has gain 1 + ε and a phase error φ (radians), part of every signal appears at −Δ. Its level relative to the wanted signal is the image rejection ratio, about $4/(\varepsilon^2+\varphi^2)$.

*Worked number (verified, `tools/verify/s18b_level15_numbers.py`).* At 2.4 MS/s, a 1 ppm error at 433 MHz (433 Hz) turns the hand once every **2.31 ms**, i.e. only **0.065° per sample**. That is invisible sample to sample but wrecks a long coherent average. A Q path that is 1 % high and 1° off gives an image only **40.0 dB** down (the exact formula and the 4/(ε²+φ²) shortcut agree). A 1° phase error alone gives 41.2 dB.

### Level 2 — quadrature demodulation, spectra, the analytic signal, and impairments
**Demodulation.** Multiply the real RF by $2\cos 2\pi f_ct$ and $-2\sin 2\pi f_ct$:
$$x\cdot2\cos\omega_ct = I + I\cos2\omega_ct - Q\sin2\omega_ct,\qquad x\cdot(-2\sin\omega_ct) = Q - I\sin2\omega_ct - Q\cos2\omega_ct .$$
Low-pass filters remove the $2\omega_c$ terms, leaving $I$ and $Q$. In complex notation this is one operation, $x(t)\cdot2e^{-j\omega_ct} = \tilde x + \tilde x^*e^{-j2\omega_ct}$, followed by a low-pass. In spectra: a real signal's transform is $X(f) = \tfrac12[\tilde X(f-f_c) + \tilde X^*(-f-f_c)]$ — a copy of the baseband spectrum at $+f_c$ and a mirrored, conjugated copy at $-f_c$. Downconversion slides the $+f_c$ copy to 0 and pushes the $-f_c$ copy to $-2f_c$, where the filter removes it. The baseband spectrum $\tilde X(f)$ has no symmetry requirement: it can be lopsided, which is what lets it carry the separate upper and lower halves of the RF band.

**Modulation (transmit, DUC).** The reverse: $x(t) = I\cos\omega_ct - Q\sin\omega_ct$ from two DACs and a quadrature modulator. Transmit-side impairments mirror the receive ones: IQ imbalance creates an image sideband at $f_c - \Delta$ when you transmit at $f_c+\Delta$, and baseband DC offset or LO feedthrough creates a carrier "spike" at $f_c$ (visible on a spectrum analyser when a HackRF/Pluto transmits).

**Analytic signal and Hilbert transform.** The analytic signal $z(t) = x(t) + j\hat x(t)$, with $\hat x$ the Hilbert transform (frequency response $-j\,\mathrm{sgn}(f)$: −90° on positive frequencies, +90° on negative), has $Z(f) = 2X(f)$ for $f>0$ and $0$ for $f<0$; and $z(t) = \tilde x(t)e^{j\omega_ct}$ [2 ch. 12], [3 §2.1]. So "throw away the negative frequencies" and "quadrature downconvert" are the same idea. Uses in SDR DSP: converting a *real* sample stream (e.g. from a real ADC sampling an IF) to complex; AM envelope detection $|z|$; SSB generation (phasing method); instantaneous frequency for FM/FSK. Script §9: `scipy.signal.hilbert` leaves $7\times10^{-32}$ of the energy at negative frequencies and recovers an AM envelope to $7\times10^{-4}$. Practical Hilbert transformers are FIR filters (odd length, antisymmetric, every other tap zero) and can't work near DC or $f_s/2$ ([FIR design](digital-filters-fir-iir.md)).

**IQ imbalance — derivation of the image.** Model the receiver with an ideal I path and a Q path of gain $g$ (ratio to I) and phase error $\varphi$ (LO not exactly 90° apart):
$$y = I + jg\,(I\sin\varphi + Q\cos\varphi).$$
Substituting $I = (\tilde x+\tilde x^*)/2$, $Q = (\tilde x-\tilde x^*)/2j$ and collecting terms:
$$y = \mu\,\tilde x + \nu\,\tilde x^*,\qquad \mu = \frac{1+g e^{j\varphi}}{2},\qquad \nu = \frac{1-g e^{-j\varphi}}{2}.$$
The $\tilde x^*$ term is the conjugate of the wanted signal: its spectrum is mirrored about DC ($\tilde X^*(-f)$). A signal at $+\Delta$ therefore produces an image at $-\Delta$ with power ratio
$$\mathrm{IRR} = \frac{|\mu|^2}{|\nu|^2} = \frac{1+2g\cos\varphi+g^2}{1-2g\cos\varphi+g^2}.$$
For small errors, writing $g = 1+\varepsilon$: numerator ≈ 4, denominator ≈ $\varepsilon^2+\varphi^2$, so $\mathrm{IRR}\approx4/(\varepsilon^2+\varphi^2)$ with $\varphi$ in radians. The same formula appears for analogue image-reject (Hartley/Weaver) receivers [4]. Script §4: simulation matches the formula to 0.01 dB at four points; the small-error form is within 0.35 dB even at 1 dB/5°.

**DC offset — where the spike comes from.** In a zero-IF (direct-conversion) receiver the LO sits at the centre of the band [4], [9]:
1. *LO self-mixing:* LO power leaks to the LNA/mixer input (substrate, bond wires, antenna reflection) and mixes with the LO itself → a DC term that also changes when the antenna environment changes.
2. *Baseband offsets:* amplifier and ADC offsets in the I and Q paths.
3. *Even-order distortion:* a strong blocker's second-order product $a_2x^2$ contains a DC and low-frequency term (its envelope squared) that lands exactly on the zero-IF channel — the reason zero-IF receivers need a high IIP2 ([nonlinearity](../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md)).
4. *Flicker (1/f) noise* of the baseband stages, which raises the floor within a few kHz of DC.
None of these exist at DC in the RF domain, so they are artefacts of *where you tuned*, not signals.

**DC blocker.** The one-pole/one-zero high-pass $H(z) = (1-z^{-1})/(1-\alpha z^{-1})$ has a zero exactly at DC and a pole just inside it. Near DC, $|1-e^{-j\omega}|^2\approx\omega^2$ and $|1-\alpha e^{-j\omega}|^2\approx(1-\alpha)^2+\alpha\omega^2$, so the half-power point is at $\omega\approx(1-\alpha)/\sqrt{2-\alpha}\approx1-\alpha$ rad/sample, i.e. $f_{-3\text{dB}}\approx(1-\alpha)f_s/2\pi$ (script §7: 382.2 Hz vs 382.0 Hz for $\alpha = 0.999$ at 2.4 MS/s). It also removes any *wanted* content within that notch — fatal for FSK with long runs of one symbol or for narrowband CW sitting on the LO — and its IIR recursion needs care in fixed point ([filters](digital-filters-fir-iir.md)).

**Offset tuning.** Tune the hardware to $f_{LO} = f_{sig} - f_{off}$. The wanted channel appears at $+f_{off}$ in the samples; the spike stays at 0. Multiply by $e^{-j2\pi f_{off}n/f_s}$ ([NCO](nco-ddc-duc.md)) to bring the channel to 0 Hz — the spike is now at $-f_{off}$, in the stop-band of the channel filter, and is removed along with everything else when you decimate ([multirate](multirate-dsp-decimation-cic.md)). Script §8: with $f_{off}=400$ kHz, 2 MS/s and a 255-tap channel filter the spike is suppressed by 86 dB and the channel is untouched (error $1.6\times10^{-4}$). Requirements: $f_{off} > B/2 +$ (filter transition) + (spike/flicker skirt), and $f_{off} + B/2 <$ roughly 0.4 $f_s$ so the channel stays out of the band-edge roll-off.

**The image trade in offset tuning (and low-IF).** Because of the $\nu\tilde x^*$ term, whatever sits at the mirror frequency $f_{LO} - f_{off}$ in RF puts its image on top of your channel, attenuated only by the IRR. In zero-IF tuning ($f_{off}=0$) the image of the wanted signal lands on itself (a self-image that only degrades EVM, not a separate interferer); in offset tuning or low-IF the image comes from a *different* frequency, which may hold a strong signal. This is the same trade as a low-IF receiver, where analogue polyphase filters provide the image rejection.

### Level 3 — frequency-dependent imbalance, estimation, architectures, noise conventions
**Frequency-dependent imbalance.** The model above has constant $g,\varphi$ (mixer/LO imbalance). The I and Q baseband filters and ADCs are also never identical, so $\mu,\nu$ become functions of frequency, $\mu(f),\nu(f)$, and the IRR varies across the band — typically worst near the band edges where the analogue filters' responses diverge. Compensation then needs a short FIR in the cross-path ($y_c = y + w * y^*$) rather than one complex coefficient [6].

**Blind estimation.** Most natural signals (noise, QPSK, OFDM, a crowd of FM stations) are *circular* (proper): $E[\tilde x^2] = 0$, equivalently $E[I^2]=E[Q^2]$ and $E[IQ]=0$. Imbalance breaks circularity: $E[y^2] = 2\mu\nu E|\tilde x|^2\neq0$. So the statistics of the received samples reveal the imbalance without any pilot signal.
- *Gram–Schmidt / moment method* [5]: remove the DC; estimate the phase error from the correlation $\rho = E[IQ]/E[I^2]$ and subtract $\rho I$ from Q (orthogonalise); then scale Q so $E[Q^2] = E[I^2]$. Script §6 shows 29.4 → 46.8 dB (16 384 samples) and 28.2 → 71.4 dB (262 144 samples). The residual is estimation noise, ∝ $1/\sqrt{N}$, so the achievable IRR grows by ~10 dB per 10× more averaging.
- *Circularity-based* [6]: choose $w$ to make $E[y_c^2]=0$; extends to frequency-selective imbalance with an adaptive FIR.
- Integrated transceivers (AD936x, LMS7002M) run factory or on-chip RX/TX quadrature calibration and "tracking" loops; leaving these enabled (driver default) is usually better than DIY correction. Non-circular signals (BPSK, a single strong tone, AM) bias blind estimators — use known test tones or average over a busy band.

**Receiver architectures in one paragraph.** *Superheterodyne*: one or more real IFs, image rejected by RF filtering before the first mixer, final IF often sampled by a real ADC (bandpass sampling) and converted to IQ digitally — no analogue IQ imbalance and no DC spike, at the cost of filters. *Zero-IF (direct conversion)*: LO at band centre, IQ mixers and two baseband ADCs — cheap and wideband (AD936x in Pluto/USRP B2x0/bladeRF, LMS7002M in LimeSDR, MAX2837 in HackRF), with DC spike and IQ image. *Low-IF*: LO offset by an IF of order the channel bandwidth; complex (polyphase) filtering for the image; the RTL-SDR's R820T2/R828D delivers a *real* IF ≈ 3.57 MHz (or 4.57 MHz) to one ADC input of the RTL2832U, which samples at 28.8 MS/s and does the final complex conversion and decimation digitally [8]. *Direct RF sampling*: the ADC sees RF (HF receivers such as RX888, RFSoC), and the whole "IQ" step is a digital NCO + filter ([NCO/DDC](nco-ddc-duc.md)). Full treatment: [receiver architectures](../06-rf-circuits/receiver-architectures.md).

**The $f_s/4$ trick (real → complex without multipliers).** If a real IF is sampled so that it sits at $f_s/4$, multiplying by $e^{-j\pi n/2}$ is multiplication by the sequence $1, -j, -1, j, \ldots$ — just sign flips and swaps of I and Q. Follow with a half-band low-pass and decimate by 2 to get complex baseband at $f_s/2$. Airspy and many FPGA front ends use variants of this; see [multirate](multirate-dsp-decimation-cic.md).

**Noise in complex baseband.** Real bandpass white noise of two-sided PSD $N_0/2$ becomes complex baseband noise whose I and Q parts are independent, each with variance $N_0B$ in bandwidth $B$ under the unscaled convention (or $N_0/2$ per dimension per Hz under the energy-normalised convention used in [BER](../10-comms-modulation/ber-ebn0-and-shannon.md) — that page's "3 dB simulation error" is this bookkeeping). Complex AWGN is circular. An SDR's FFT of pure noise is flat across $\pm f_s/2$; a "tilt" or a mirror-symmetric bump pattern indicates frequency-dependent imbalance or filter mismatch.

**Why complex at all?** A complex sample stream at $f_s$ carries the same information as a real stream at $2f_s$ (two real numbers per sample). The advantages are practical: the spectrum can be centred on 0 so a channel of bandwidth $B$ needs only $f_s\gtrsim B$; frequency shifting is a single complex multiply (no images); phase and instantaneous frequency are directly available (atan2); matched filtering and synchronisation algorithms ([sync](../10-comms-modulation/synchronization-carrier-timing.md)) work naturally on phasors.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $x = I\cos\omega_ct - Q\sin\omega_ct = \mathrm{Re}\{\tilde xe^{j\omega_ct}\}$ | any bandpass signal | — |
| RF $f_c+\Delta$ → baseband $+\Delta$ | complex downconversion | below centre = negative |
| $\mathrm{IRR} = \frac{1+2g\cos\varphi+g^2}{1-2g\cos\varphi+g^2}\approx\frac{4}{\varepsilon^2+\varphi^2}$ | frequency-flat imbalance | 0.1 dB/1°: 39.6 dB; 0.5 dB/2°: 29.5 dB; 1 dB/5°: 22.8 dB |
| Image of signal at $+\Delta$ appears at $-\Delta$, level $-\mathrm{IRR}$ dBc | IQ receivers/transmitters | a −20 dBm signal → −50 dBm image at 30 dB IRR |
| DC blocker $f_{-3dB}\approx(1-\alpha)f_s/2\pi$ | $\alpha\to1$ | $\alpha$=0.999, 2.4 MS/s: 382 Hz |
| Offset: $B/2+\text{skirt} < f_{off} < 0.4f_s - B/2$ | offset tuning | LoRa BW125 at 2 MS/s: 200–600 kHz |
| Mirror (image) frequency $= 2f_{LO} - f_{sig}$ | offset tuning, low-IF | check it's quiet |
| $\delta f = f_c\,\text{ppm}\times10^{-6}$ | oscillator error | 1 ppm @ 433.92 MHz = 434 Hz |
| Blind correction IRR ∝ $10\log_{10}N$ | Gram–Schmidt / moment | 16 k samples ≈ 47 dB; 262 k ≈ 71 dB |

## Worked examples

**1 — Receiving a LoRa BW125 channel at 433.92 MHz on a zero-IF SDR (Pluto/HackRF/LimeSDR) with offset tuning.** Choose $f_s = 2.0$ MS/s. The channel spans ±62.5 kHz; the DC spike plus flicker skirt is a few kHz wide; the channel filter needs a transition band. Take $f_{off} = 400$ kHz: $f_{LO} = 433.52$ MHz; the channel occupies +337.5…+462.5 kHz in the samples, well inside 0.4 $f_s$ = 800 kHz. The mirror band is $2f_{LO} - f_{sig}$ = 433.12 MHz ± 62.5 kHz. At 30 dB IRR, a −60 dBm SRD transmitter at 433.12 MHz would put a −90 dBm image onto your channel — at the ground station that might be stronger than your rocket at long range (LoRa SF12 decodes around −137 dBm/−20 dB SNR). Before launch day, look at 433.06–433.18 MHz on the waterfall; if busy, flip the offset to −400 kHz (mirror at 434.72 MHz) instead. Then NCO-shift by −400 kHz and decimate by 4 to 500 kS/s ([multirate Example 1](multirate-dsp-decimation-cic.md)).

**2 — How much image does a strong nearby signal create?** A 2 W (33 dBm) E22 module transmitting 50 m from the ground station, antenna gains 2 dBi each, free-space loss at 433.92 MHz over 50 m is $20\log_{10}(4\pi\cdot50/0.691) = 59.2$ dB ([Friis](../09-propagation-link-budget/friis-free-space-path-loss.md)) → about −22 dBm at the SDR input (before any LNA saturation question!). With 0.5 dB/2° imbalance (IRR 29.5 dB) it creates a −52 dBm ghost at the mirror frequency. Blind correction to 60 dB drops that to −82 dBm. The real lesson: at these levels you are also near the SDR's compression point — reduce gain first ([dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)).

**3 — DC blocker vs offset tuning for 2-FSK telemetry.** A 9.6 kbit/s 2-FSK signal with ±4.8 kHz deviation centred on the LO: the spectrum has energy near DC during long runs of identical bits only if the data isn't whitened; the tones themselves are at ±4.8 kHz. A DC blocker with $\alpha = 0.9999$ at 2.4 MS/s notches ±38 Hz — harmless to the tones, but the spike's *skirt* (flicker noise, LO-leakage wander) can be kHz wide. Offset tuning by 200 kHz is the robust choice.

**4 — Frequency error budget for a waterfall search.** A non-TCXO SDR (±20 ppm) at 433.92 MHz: ±8.7 kHz; a 1 ppm TCXO (RTL-SDR Blog V3/V4): ±434 Hz; the flight radio's own crystal (say ±10 ppm → ±4.3 kHz) adds. Rocket Doppler at 300 m/s: $f\,v/c$ = 434 Hz. So the LoRa packet can be ~±13 kHz from nominal with cheap parts — ~10 % of BW125. Search a window at least that wide, then let the demodulator's CFO estimator lock ([LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md), [sync](../10-comms-modulation/synchronization-carrier-timing.md)). Calibrate an SDR's ppm against a known carrier (GSM/LTE base station with `kalibrate`, or a GNSS-disciplined source).

**5 — Why RTL-SDR (R820T2) shows no big centre spike but HackRF does.** R820T2: low-IF at ≈ 3.57 MHz; the RTL2832U's ADC offset appears at the IF's DC, which after digital conversion sits ≈ 3.57 MHz from the display centre — outside the 2.4 MHz window. HackRF (MAX2837 zero-IF): the LO is at display centre, so self-mixing and baseband offsets appear exactly at 0 Hz, and HackRF users are routinely advised to offset-tune (forum advice; see [hardware survey](sdr-hardware-survey.md)).

## Practical notes
- **Spot an image vs a real signal**: retune the SDR by +100 kHz. Real signals move −100 kHz on the display; images of signals move +100 kHz (they mirror about the centre). Changing the sample rate doesn't move either — but it does move aliases ([sampling](sampling-aliasing-bandpass-sampling.md)).
- **Leave the driver's DC and IQ correction on** unless you know better: SoapySDR exposes `setDCOffsetMode`/`setIQBalanceMode`; the AD936x driver runs RF DC, BB DC and quadrature tracking by default; gr-osmosdr exposes DC/IQ "mode" options (manual/automatic). These act before your code sees samples.
- **Don't correct IQ imbalance on a single strong tone or on BPSK** with a blind estimator — they are non-circular and will bias it; average over a busy band or inject a known tone.
- **Transmit spike**: when a zero-IF SDR transmits at $f_c$, residual LO feedthrough radiates a carrier at $f_c$ (often only 30–40 dB below the signal if uncalibrated). Offset-transmit the same way: put your signal at $+f_{off}$ digitally so the spike isn't in your channel — and make sure the spike itself is legal where you transmit.
- **Sign conventions bite**: some tools put I in the real part and some hardware swaps I/Q, which mirrors the spectrum (LSB ↔ USB, chirp up ↔ down). If a LoRa decoder finds nothing but the waterfall looks fine, try conjugating the samples.
- **Sample formats**: RTL-SDR delivers unsigned 8-bit I,Q interleaved (offset binary, subtract 127.5); HackRF signed 8-bit; Pluto/USRP 12-bit in signed 16-bit (`sc16`); host libraries often convert to `complex64` (`fc32`). DC from mis-handling the 127.5 offset looks exactly like a hardware DC spike.

## Common mistakes & misconceptions
1. **"Negative frequencies aren't physical."** In baseband they mean "below $f_c$" and carry independent information. In passband, real signals have mirror-symmetric spectra — the negative half is redundant there, not in baseband.
2. **"The centre spike is a signal at my tuning frequency."** It's an artefact of zero-IF conversion. Retune a little: a real carrier moves, the spike stays at the centre.
3. **"Offset tuning removes all LO problems."** It moves the DC spike out of the channel but exposes the channel to the image of the mirror frequency. Check that frequency.
4. **"IQ imbalance only matters for high-order QAM."** It also creates ghost signals from strong neighbours, which can desense a weak narrowband channel regardless of its modulation.
5. **"A DC blocker is harmless."** It notches whatever wanted content sits near DC, and a too-aggressive $\alpha$ (e.g. 0.99) removes a 3.8 kHz-wide slice at 2.4 MS/s.
6. **"RTL-SDRs are zero-IF like HackRF."** R820T2/R828D-based dongles are low-IF with digital IQ formation; the E4000 was zero-IF. (PySDR's architecture chapter groups RTL-SDR with direct-conversion SDRs [7] — see Contradictions in the log.)
7. **Mixing by $e^{+j\omega t}$ vs $e^{-j\omega t}$**: $\times e^{-j2\pi f_0n/f_s}$ shifts the spectrum *down* by $f_0$ (brings a signal at $+f_0$ to 0). Getting the sign wrong moves the signal to $2f_0$.
8. **Treating $|I|$ or $|Q|$ alone as the amplitude.** Use $\sqrt{I^2+Q^2}$; I alone oscillates at the offset frequency.

## How to simulate / verify
- `python3 tools/verify/dsp_iq.py` (≈ 1 s): real vs complex spectra; quadrature downconversion sign; upconversion identity; IRR formula vs simulation at four imbalance points; small-error approximation; Gram–Schmidt correction vs averaging length; DC-blocker −3 dB width; offset tuning spike removal; analytic signal and AM envelope; ppm table. All PASS.
- Model imbalance yourself: `y = x.real + 1j*g*(np.sin(phi)*x.real + np.cos(phi)*x.imag)`; FFT it and read the mirror line.
- GNU Radio: `IQ Imbalance Generator`/`DC Offset Generator` style blocks (or a Python block with the line above) → `QT GUI Frequency Sink` to watch images; `DC Blocker` block for the high-pass; `Frequency Xlating FIR Filter` for offset tuning + channel filter + decimation in one block ([GNU Radio](gnu-radio-and-software-stack.md)).
- On hardware: inject a CW tone from a signal generator (or a NanoVNA's output) at $f_c + 200$ kHz, read the image at $f_c - 200$ kHz with calibration on and off, and repeat across the band to see frequency-dependent imbalance.

## Open questions / gaps
- Measured IRR and DC-spike levels for specific SDRs (HackRF, Pluto, LimeSDR Mini, bladeRF) with and without driver calibration are not tabulated here; would need a bench measurement (domain 17) or a sourced review.
- The exact R820T/R828D IF options (3.57 MHz vs 4.57 MHz vs others, as set by the librtlsdr driver) are taken from community documentation, not the (non-public) Rafael Micro datasheet.
- Frequency-dependent imbalance correction (adaptive FIR) is described but not simulated.

## Sources
1. R. G. Lyons, *Understanding Digital Signal Processing*, 3rd ed., Prentice Hall (2011), ch. 8 "Quadrature signals" and §13 (DSP tricks incl. $f_s/4$ translation, DC removal). (textbook) — IQ representation, negative frequency, DC blocker, $f_s/4$ mixing.
2. A. V. Oppenheim, R. W. Schafer, *Discrete-Time Signal Processing*, 3rd ed., Pearson (2010), ch. 12 "Discrete Hilbert transforms" (analytic sequences, FIR Hilbert transformers, bandpass sampling of complex signals). (textbook)
3. J. G. Proakis, M. Salehi, *Digital Communications*, 5th ed., McGraw-Hill (2008), §2.1 (bandpass and lowpass signal representation, complex envelope, analytic signal). (textbook)
4. B. Razavi, *RF Microelectronics*, 2nd ed., Prentice Hall (2011), ch. 4 (heterodyne, direct-conversion, image-reject and low-IF receivers; DC offsets, LO leakage, even-order distortion, I/Q mismatch and IRR expression). (textbook)
5. F. E. Churchill, G. W. Ogar, B. J. Thompson, "The correction of I and Q errors in a coherent processor," *IEEE Trans. Aerospace and Electronic Systems* AES-17(1):131–137 (1981). (peer-reviewed) — Gram–Schmidt style IQ gain/phase correction. *Cited from the literature; not re-read this session.*
6. L. Anttila, M. Valkama, M. Renfors, "Circularity-based I/Q imbalance compensation in wideband direct-conversion receivers," *IEEE Trans. Vehicular Technology* 57(4):2099–2113 (2008). (peer-reviewed) — blind, frequency-selective compensation. *Cited from the literature; not re-read.*
7. M. Lichtman, *PySDR*, ch. "IQ Sampling" (sections Receiver Architectures, DC Spike and Offset Tuning), https://pysdr.org/content/sampling.html (accessed 2026-09-27). (online textbook)
8. superkuh, "rtl-sdr and GNU Radio with Realtek RTL2832U, E4000 and R820T," http://superkuh.com/rtlsdr.html (community documentation; accessed via search summary 2026-09-27) — R820T low-IF 3.57/4.57 MHz into the RTL2832U I input, digital IQ, no DC spike; E4000 zero-IF. (forum/community — anecdotal but consistent with librtlsdr source)
9. A. A. Abidi, "Direct-conversion radio transceivers for digital communications," *IEEE J. Solid-State Circuits* 30(12):1399–1410 (1995). (peer-reviewed) — DC offset mechanisms, LO leakage, flicker noise, even-order distortion in zero-IF. *Cited from the literature; not re-read.*
10. KB: [complex numbers & phasors](../00-math-foundations/complex-numbers-and-phasors.md) (complex envelope, analytic signal basics), [BER page](../10-comms-modulation/ber-ebn0-and-shannon.md) (complex noise conventions), [OFDM](../10-comms-modulation/ofdm.md) (image of subcarrier k onto −k).
