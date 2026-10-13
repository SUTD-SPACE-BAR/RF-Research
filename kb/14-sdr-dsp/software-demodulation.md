---
title: Software demodulation — FM, AM, SSB, FSK/GFSK, PSK, LoRa and a complete packet pipeline in DSP
domain: 14-sdr-dsp
slug: software-demodulation
tags: [demodulation, fm, quadrature-demod, polar-discriminator, de-emphasis, am, envelope, ssb, phasing, fsk, gfsk, discriminator, non-coherent, bpsk, qpsk, costas, gardner, timing-recovery, lora, dechirp, packet, crc, aprs, ax25, rtl_433, gnu-radio, noise-blanker, impulsive-noise, spectral-subtraction, noise-reduction, auto-notch, if-shift, passband-tuning, roofing-filter]
prerequisites: [iq-complex-baseband.md, multirate-dsp-decimation-cic.md, digital-filters-fir-iir.md, nco-ddc-duc.md, ../10-comms-modulation/analog-modulation-am-fm-pm-ssb.md, ../10-comms-modulation/digital-modulation-psk-qam-fsk.md]
related: [fft-spectral-analysis-windows.md, gnu-radio-and-software-stack.md, sdr-hardware-survey.md, fpga-for-sdr.md, ../10-comms-modulation/matched-filter-detection.md, ../10-comms-modulation/synchronization-carrier-timing.md, ../10-comms-modulation/pulse-shaping-isi.md, ../10-comms-modulation/ber-ebn0-and-shannon.md, ../10-comms-modulation/packet-framing-protocols.md, ../10-comms-modulation/spread-spectrum-dsss-fhss-css.md, ../15-lora-ism-radios/lora-phy-css-math.md, ../15-lora-ism-radios/ground-station-design.md, ../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md]
level: mixed
confidence: high
last_updated: 2026-10-14
---

# Software demodulation — FM, AM, SSB, FSK/GFSK, PSK, LoRa and a complete packet pipeline

## Questions this page answers
- How do I demodulate FM from IQ samples in one line of code?
- What sample rates and filters does a broadcast-FM or NBFM receiver chain need, and what is de-emphasis?
- How do I demodulate AM and SSB (USB/LSB) from complex baseband?
- What is the best way to demodulate FSK/GFSK telemetry — discriminator or matched filters — and how much does the cheap way lose?
- How does a software QPSK receiver lock onto carrier and symbol timing (Costas loop, Gardner)?
- How is LoRa demodulated in software, and why is its error rate exactly that of M-ary FSK?
- How do I go from IQ samples to verified packets (preamble, sync word, length, CRC)?
- How would I decode APRS (AX.25 AFSK) or 433 MHz OOK sensors with an SDR?
- Why does my demodulated SSB sound like Donald Duck, or my FSK decode with inverted bits?
- What does a noise blanker do, and where must it go in an SDR receiver chain?
- Does DSP noise reduction improve weak-signal sensitivity?
- What are IF shift, passband tuning and roofing filters, and can an SDR have a digital roofing filter?

## TL;DR
- **FM**: instantaneous frequency $= \frac{f_s}{2\pi}\arg\big(x[n]\,x^*[n-1]\big)$ (polar discriminator). Exact for the phase step, amplitude-independent (script: error 5×10⁻¹¹ Hz). Broadcast FM: channel ~200 kHz, run the discriminator at ≥ 200–250 kS/s, then 50 µs (75 µs in the Americas) de-emphasis and decimate to 48 kHz audio.
- **AM**: $|x[n]|$ minus its mean (envelope) or $\mathrm{Re}\{x\,e^{-j\hat\theta}\}$ after carrier recovery (synchronous). **SSB**: shift so the carrier (suppressed) is at 0 Hz, low-pass to the audio bandwidth, take the real part; USB keeps positive frequencies, LSB negative (or conjugate first). A tuning error of Δ shifts every audio tone by Δ.
- **FSK/GFSK**: optimum non-coherent detection = two (or M) correlators; BER $\tfrac12e^{-E_b/2N_0}$ for orthogonal BFSK (script matches). The cheap **discriminator + integrate-and-dump** detector lost only 0.07 dB for 2-FSK with h = 1, and **1.41 dB for 2-GFSK with h = 0.5, BT = 0.5** at BER 10⁻³ (10.94 → 12.35 dB Eb/N0) in the script's configuration.
- **QPSK**: RRC matched filter → Gardner timing loop → Costas carrier loop → decision. Script (τ = 0.37 sample, CFO 1.5×10⁻³ cycles/sample): BER within ≈ 0.2–0.3 dB of theory. A sign error in the Gardner detector makes the loop lock on the zero crossings (BER 0.5) — a classic bug found while building the check.
- **LoRa**: multiply by a down-chirp, FFT of length $2^{SF}$, pick the peak bin. That is non-coherent orthogonal $M$-FSK with $M = 2^{SF}$: script SF7 SER 1.5×10⁻³ at −8 dB SNR vs exact formula 1.6×10⁻³. A CFO of one bin ($BW/2^{SF}$ = 977 Hz at SF7/BW125) shifts *every* symbol by one — estimate CFO from the preamble first (script estimate 3.312 vs 3.3 bins).
- **Packets**: burst detect → CFO from preamble → timing → sync-word search (allow ~1 bit error) → length → payload → CRC. Script GFSK frame (29 bytes, 9.6 kbit/s, 2 kHz CFO) PER: 0.58 @ 11 dB, 0.27 @ 12 dB, 0.05 @ 13 dB, 0.03 @ 14 dB Eb/N0. CRC check values verified (CCITT-FALSE 0x29B1, X-25/AX.25 0x906E).

- **Receiver DSP features** ([section](#receiver-dsp-features-in-software--noise-blanker-noise-reduction-auto-notch-if-shift-roofing)): blank impulses in the **wide path before decimation**, with a median-based threshold. LoRa SF7 at −8 dB SNR with 0.5 % impulses 40 dB up: SER 0.70 → 0.0013 (AWGN-only 0.0010); blanking after the decimation filter gives only 0.028. Spectral-subtraction NR raises band SNR (−7.3 → −1.0 dB) but **not** in-bin SNR (10.4 → 10.5 dB). IF shift is a change of $\omega_0$ in $h_{LP}[n]e^{j\omega_0n}$. A digital filter can never be a roofing filter. Verified by `tools/verify/s7_noise_blanker.py`.

Verified by `tools/verify/dsp_demod.py` (all PASS, ≈ 4 s).

## Intuition (no math)
Once the SDR has brought a signal to complex baseband, every demodulator is a question about the spinning arrow $I + jQ$ ([IQ](iq-complex-baseband.md)): *how long is it* (AM), *how fast is it turning* (FM/FSK), *which way does it point* (PSK), or *which of M patterns does it match best* (FSK correlators, LoRa). FM is the easiest: compare each sample with the previous one and measure the angle between them — that angle, per sample, is the frequency. AM is just the arrow's length. SSB is a shifted copy of the audio itself, so you shift it back.

Digital modes add two chores. First, the receiver's clock and oscillator never match the transmitter's, so a digital receiver must *synchronise*: find where each symbol starts (timing) and, for PSK, what "zero phase" means (carrier). Second, the output is bits, so you need framing: find the start of a packet, read its length, and check its CRC. Most of the code in a real software receiver is synchronisation and framing, not demodulation.

## The math

### Level 1 — the demodulators in one line each
With complex baseband $x[n]$ at rate $f_s$ ([IQ](iq-complex-baseband.md)):

| Signal | Demodulator | Output |
|---|---|---|
| FM / FSK | $\hat f[n] = \frac{f_s}{2\pi}\arg(x[n]x^*[n-1])$ | Hz; divide by the peak deviation for normalised audio |
| AM (envelope) | $a[n] = \lvert x[n]\rvert - \overline{\lvert x\rvert}$ | message (DC = carrier removed) |
| AM (synchronous) | $a[n] = \mathrm{Re}\{x[n]e^{-j\hat\theta[n]}\}$ | better at low SNR and in selective fading |
| USB | shift carrier to 0 Hz, LPF 0…3 kHz, $\mathrm{Re}\{\cdot\}$ | audio |
| LSB | as USB on $x^*[n]$ (or keep $-3\ldots0$ kHz) | audio |
| BPSK/QPSK | matched filter, sample at symbol centre, rotate by $e^{-j\hat\theta}$, slice | symbols |
| M-FSK / LoRa | correlate against each tone (FFT after dechirp for LoRa), pick max | symbol index |

Key parameters: FM deviation $\Delta f$ (broadcast 75 kHz; NBFM 2.5 or 5 kHz), modulation index $h = 2\Delta f/R_b$ for binary FSK, Carson bandwidth $2(\Delta f + f_m)$ ([analog modulation](../10-comms-modulation/analog-modulation-am-fm-pm-ssb.md)).

### Level 2 — derivations and the synchronisation loops
**Polar discriminator.** If $x[n] = A[n]e^{j\phi[n]}$, then $x[n]x^*[n-1] = A[n]A[n-1]e^{j(\phi[n]-\phi[n-1])}$, whose argument is the phase increment over one sample — exactly $2\pi\bar f/f_s$ where $\bar f$ is the mean frequency over that sample interval, independent of amplitude (script §1: error 4.9×10⁻¹¹ Hz; scaling the input by 3.7 changes nothing). Valid while $|\Delta\phi| < \pi$, i.e. $|f| < f_s/2$ including deviation, offset and noise excursions. The alternative *derivative* form $\hat f = \frac{f_s}{2\pi}\frac{I\dot Q - Q\dot I}{I^2 + Q^2}$ avoids the atan but needs a good differentiator (script: 14 Hz error of 5 kHz with a central difference); in FPGAs the atan is computed by a CORDIC in vectoring mode ([NCO/CORDIC](nco-ddc-duc.md)). GNU Radio's `Quadrature Demod` block is the polar discriminator with gain $f_s/(2\pi\Delta f)$ [8].

**FM de-emphasis.** Broadcast FM pre-emphasises audio with a zero at $1/(2\pi\tau)$ (τ = 50 µs → 3183 Hz; 75 µs → 2122 Hz), so the receiver applies a one-pole low-pass $1/(1+s\tau)$ after the discriminator — noise, which rises with frequency at an FM discriminator's output (triangular PSD), is cut most ([analog modulation](../10-comms-modulation/analog-modulation-am-fm-pm-ssb.md)). Digital version by the bilinear transform (script §2: −3.07 dB at 3183 Hz at 48 kS/s; see prewarping in [filters](digital-filters-fir-iir.md)).

**AM.** $x = (1+m)e^{j(\omega_\delta n + \theta)}$ with a residual offset $\omega_\delta$: $|x| = 1+m$ regardless of $\omega_\delta,\theta$, so the envelope detector needs no carrier recovery (script §3: exact). The synchronous detector needs $\hat\theta$ from a PLL on the carrier but has no threshold effect and handles selective fading (where the carrier fades more than the sidebands) better.

**SSB.** A USB signal is the analytic signal of the audio, $a[n] + j\hat a[n]$, shifted up by the carrier ([IQ](iq-complex-baseband.md)): it has only positive frequencies relative to the carrier. In complex baseband, demodulation is a frequency shift that puts the (suppressed) carrier at 0 Hz followed by $\mathrm{Re}\{\cdot\}$ (script §4: other sideband −137 dB; audio recovered to 5×10⁻⁵). If the shift is wrong by Δ, every audio tone moves by Δ (script: 700 Hz → 2300 Hz for a 3 kHz error, "Donald Duck"), and choosing the wrong sideband mirrors the audio spectrum. Because the carrier is suppressed there is nothing to lock to; the operator (or an AFC on a pilot) tunes it.

**Non-coherent FSK — the optimum.** For binary FSK with tone spacing $2\Delta f = h R_b$, a receiver that correlates each bit against both tones and compares envelopes is optimum without phase knowledge. For orthogonal tones ($h$ = 1, 2, …; "wideband" FSK) the bit error rate is $P_b = \tfrac12 e^{-E_b/2N_0}$ [5] (script §5: 2.17×10⁻² / 3.32×10⁻³ / 1.65×10⁻⁴ at 8/10/12 dB vs 2.13×10⁻² / 3.37×10⁻³ / 1.81×10⁻⁴). $E_b/N_0$ for BER 10⁻³: 10.94 dB. Coherent detection of the same signal would need ≈ 1 dB less; MSK/GMSK ($h$ = 0.5) detected coherently as OQPSK gets back to BPSK performance (6.8 dB at 10⁻³) — see [BER](../10-comms-modulation/ber-ebn0-and-shannon.md).

**Discriminator detection — the practical one.** Most ISM FSK chips and simple SDR decoders use pre-detection band-pass (channel) filter → discriminator → post-detection low-pass/integrate-and-dump → slicer. It is insensitive to carrier phase, tolerant of CFO (it appears as a DC offset, removable by averaging the preamble), and simple. Its loss depends on $h$, BT, the pre-detection bandwidth and the post-detection filter. Script §6 (pre-detection filter ≈ Carson bandwidth $(h+1)R_b$, integrate-and-dump over the bit, 8 samples/bit):
- 2-FSK, $h$ = 1: 11.02 dB at BER 10⁻³ (**+0.07 dB** vs ideal non-coherent),
- 2-GFSK, $h$ = 0.5, BT = 0.5: 12.35 dB (**+1.41 dB**).
The GFSK loss comes from the smaller frequency separation and the Gaussian filter's ISI. Treat these as representative for this receiver design, not universal: a narrower pre-detection filter trades noise against ISI, and more elaborate detectors (multi-symbol, Viterbi on the CPM trellis) recover most of the loss. This closes, for these parameters, a gap noted in [10-comms](../10-comms-modulation/_index.md).

**Coherent PSK receiver.** Chain: AGC → RRC matched filter ([pulse shaping](../10-comms-modulation/pulse-shaping-isi.md)) → timing recovery → carrier recovery → slicer. Loops are covered in depth in [synchronisation](../10-comms-modulation/synchronization-carrier-timing.md); here, the implementation choices:
- *Timing (Gardner [3])*: at 2 samples/symbol or more, $e_k = \mathrm{Re}\{y^*_{k-1/2}(y_k - y_{k-1})\}$, where $y_{k-1/2}$ is the interpolated mid-point between symbol samples. It needs no carrier lock (works under CFO). A PI loop filter adjusts the fractional sampling instant; a cubic (Farrow) interpolator provides the samples ([multirate](multirate-dsp-decimation-cic.md)). With the sign reversed, the loop still converges — to the *zero crossings* — and the constellation smears to BER 0.5; the script documents this.
- *Carrier (Costas [4])*: rotate by $e^{-j\hat\theta}$; QPSK phase detector $e = \mathrm{sgn}(\mathrm{Re}\,z)\,\mathrm{Im}\,z - \mathrm{sgn}(\mathrm{Im}\,z)\,\mathrm{Re}\,z$; a second-order loop (phase + frequency integrator) tracks CFO. It leaves a 90° ambiguity — resolve it with a known sync word or differential encoding.
- Script §7 (QPSK, RRC β = 0.35, 4 samples/symbol, timing offset 0.37 sample, CFO 1.5×10⁻³ cycles/sample, random phase): BER 6.2×10⁻³ vs theory 5.95×10⁻³ at 5 dB, 1.0×10⁻³ vs 7.7×10⁻⁴ at 7 dB — ≈ 0.2–0.3 dB implementation loss from loop jitter.
- A CFO larger than the Costas pull-in range needs a coarse estimate first (FFT of $x^4$ for QPSK, or a frequency-locked loop such as GNU Radio's `FLL Band-Edge`).

**LoRa demodulation.** A LoRa symbol $s\in\{0,\ldots,M-1\}$, $M = 2^{SF}$, is an up-chirp cyclically shifted by $s$ ([LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md)): sampled at $f_s = BW$, $x_s[n] = \exp\!\big(j2\pi(\frac{n^2}{2M} + (\frac{s}{M} - \frac12)n)\big)$. Multiplying by the conjugate base chirp removes the quadratic phase and leaves $e^{j2\pi sn/M}$ — a pure tone at bin $s$. An $M$-point FFT is therefore a bank of $M$ orthogonal correlators and picking the largest magnitude is **non-coherent detection of M-ary orthogonal signals** [7], [5]. Its symbol error rate for SNR per symbol $E_s/N_0 = M\cdot\mathrm{SNR}$ (SNR measured in the bandwidth BW) is
$$P_s = 1 - \int_0^\infty 2u\,e^{-(u^2 + E_s/N_0)}\,I_0\!\big(2u\sqrt{E_s/N_0}\big)\big(1-e^{-u^2}\big)^{M-1}du .$$
Script §8 (SF7, 6000 symbols): SER 1.5×10⁻³ at SNR −8 dB (formula 1.61×10⁻³), 3.45×10⁻² at −10 dB (3.80×10⁻²). The dechirp FFT is also where the ≈ $10\log_{10}M$ processing gain comes from (21 dB at SF7). Two impairments dominate in practice ([LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)):
- *CFO* shifts the dechirped tone: a CFO of $k$ bins (bin = $BW/M$) adds $k$ to every symbol (script §9: exactly +1 for one bin). Fractional CFO spreads energy into two bins (up to ~3.9 dB loss at half a bin — the rectangular-window scalloping loss, [FFT](fft-spectral-analysis-windows.md)).
- *Timing offset* also shifts the tone (a time shift of a chirp is a frequency shift), so CFO and STO are coupled; LoRa resolves them with up-chirps in the preamble and down-chirps in the sync field. Script §9 estimates a 3.3-bin CFO from 8 preamble chirps with a 16×-padded FFT: 3.312 bins.
A full receiver (gr-lora_sdr [6]) adds preamble detection, fractional CFO/STO estimation and correction, sync-word check, Gray demapping, diagonal deinterleaving, Hamming decoding, dewhitening, header and payload CRC.

### Level 3 — from bits to packets, and real protocols
**Packet pipeline** (script §10; frame = 4-byte 0xAA preamble, 0x2DD4 sync word, length byte, payload, CRC-16/CCITT-FALSE):
1. *Burst detection*: short-term power above a threshold (or a preamble correlator). Widen the detected window by a few bits — the script's first version cut the burst tail and silently lost the CRC field (0 bit errors, 62 % packet loss).
2. *CFO removal*: average the discriminator output over the 1010… preamble (balanced, so the data do not bias it).
3. *Timing*: choose the sampling phase that maximises the eye opening over the preamble (a simple, robust batch method; streaming receivers use Gardner/M&M loops).
4. *Frame sync*: correlate the sliced bits with the sync word, allowing ~1 error in 16 bits ([framing](../10-comms-modulation/packet-framing-protocols.md) gives the false-alarm/miss trade).
5. *Parse and check*: length → payload → CRC. Script: CRC-16/CCITT-FALSE check value 0x29B1 and CRC-16/X-25 0x906E verified; PER 1.00 / 0.58 / 0.27 / 0.05 / 0.03 at 9 / 11 / 12 / 13 / 14 dB Eb/N0 for 232-bit frames with 2 kHz CFO and random timing.
Compared with the matched-filter-bound BER, the steep PER curve is expected: $\mathrm{PER}\approx1-(1-P_b)^{232}$.

**Real protocol example 1 — APRS (AX.25 over AFSK).** Common for rocket and balloon trackers. The RF is NBFM (typically ±3 kHz deviation) carrying Bell-202 audio FSK: 1200 Hz (mark) and 2200 Hz (space) at 1200 baud. Chain: SDR at 2.4 MS/s → shift to the channel (e.g. 144.39 MHz in North America; frequencies are regional) → decimate to ~48 kS/s → polar discriminator → (optional de-emphasis) → audio AFSK demodulator (two tone correlators or a second discriminator on the audio) → bit clock recovery → **NRZI decode** (a 0 bit is a tone change) → HDLC: flags 0x7E, remove stuffed 0 after five 1s → AX.25 frame → FCS check (CRC-16/X-25, check value 0x906E). Direwolf implements the audio half; `rtl_fm | direwolf` is the classic one-liner [10].

**Real protocol example 2 — 433 MHz OOK/FSK sensors (rtl_433).** Weather stations, tyre-pressure sensors and key fobs at 433.92 MHz use OOK or FSK with pulse-width or Manchester coding. rtl_433 samples at 250 kS/s (default), detects pulses on the envelope ($|x|$) or on the discriminator output, measures pulse and gap widths, and matches them against ≈ 380 device decoders (the rtl_433 README lists 380, numbered up to [386], 44 of them disabled by default; checked 2026-10-03) [10]. A good template for a custom rocket beacon decoder: record IQ ([SigMF](gnu-radio-and-software-stack.md)), inspect pulses in inspectrum/URH, then write the decoder.

**Real protocol example 3 — LoRa from the rocket.** Record the flight at 1 MS/s with an RTL-SDR ([ground station](../15-lora-ism-radios/ground-station-design.md)); decode offline with gr-lora_sdr at the flight SF/BW/CR; per-packet CFO gives Doppler and oscillator drift. Chain design: [multirate Example 1](multirate-dsp-decimation-cic.md).

**Where the losses hide.** Implementation loss in software receivers typically comes from: loop jitter (0.1–0.5 dB), fixed quantisation of the discriminator/atan (negligible in float), mismatch between the channel filter and the signal (0.5–2 dB for a crude brick-wall), CFO outside the loop's pull-in (catastrophic), and dropped samples (catastrophic — watch for overflows, [software stack](gnu-radio-and-software-stack.md)).

### Receiver DSP features in software — noise blanker, noise reduction, auto-notch, IF shift, roofing
The front-panel features of a classic communications receiver are a few lines of DSP in an SDR. The **order** matters more than the algorithm: wide path at the SDR rate (noise blanker) → decimating channel filter (with IF shift) → AGC → demodulator → audio-only NR/ANF. The roofing filter sits upstream of all of these and is analog. The analog and ham-receiver view, with a CW-in-impulse example and LMS line-enhancer numbers, is on [AGC loops §receiver DSP features](../06-rf-circuits/agc-loops-and-receiver-gain-control.md#level-3--receiver-dsp-features). This section adds the SDR implementation and a LoRa case. All numbers are from `tools/verify/s7_noise_blanker.py`.

**Noise blanker (NB).** Man-made impulsive noise (ignition, arcing, switch-mode edges, [P.372 caveat](../07-noise-linearity/thermal-noise-and-noise-temperature.md#external-noise-itu-r-p372)) is sparse and strong. A Bernoulli–Gaussian model captures it: each sample is, with probability $p$, hit by an extra Gaussian burst much stronger than the background. Middleton's class-A model is the physical version [12].
- *Threshold from a robust noise estimate.* For complex Gaussian noise $|x|$ is Rayleigh, with median $\sigma\sqrt{\ln2}$. So $\hat\sigma = \mathrm{median}|x|/\sqrt{\ln 2}$, and sparse impulses barely move it. With impulses on 0.5 % of samples 40 dB above the noise, the rms estimate read 7.07σ, the mean-based estimate 1.48σ and the median estimate **1.004σ** (§1). In pure noise the false-blank fraction at a threshold $k\hat\sigma$ is $P(|x|>k\sigma) = e^{-k^2}$: 1.2 × 10⁻⁴ at 3σ, 1.1 × 10⁻⁷ at 4σ.
- *Action.* **Zero** the flagged samples plus a guard of ±1–2 samples, which catches the ringing of the SDR's own anti-alias filter. Alternatives are to **clip** them to the threshold (a noise limiter, which keeps the phase) or to **interpolate** across the gap (best for audio). In AWGN, blanking a fraction $p$ of the samples costs $-10\log_{10}(1-p)$ of SNR: 0.04 / 0.22 / 0.97 dB at 1 / 5 / 20 % (§3).
- *Placement.* Blank in the **widest path, before any decimating filter**. A filter of bandwidth $B$ stretches an impulse to about $1/B$ and lowers its peak, so after the filter the impulse no longer crosses the threshold, yet it still corrupts the symbols.
- *LoRa demonstration (§2).* SF7 at −8 dB SNR, wide path at 4 × BW (500 kS/s), impulses on 0.5 % of the wide-path samples at 40 dB above the noise, which raises the *average* noise by 17 dB:

| Receiver | SER |
|---|---|
| AWGN only (no impulses) | 0.0010 |
| impulses, no blanker | **0.70** |
| zeroing blanker in the wide path (1.5 % of samples blanked) | **0.0013** |
| clipper in the wide path | 0.0030 |
| zeroing blanker after the decimation filter | 0.028 |

  The dechirp FFT spreads an impulse over every bin, but the impulse's energy is many times the symbol energy, so "LoRa averages impulses out" fails once they are strong. For a launch-site ground station near generators and vehicles, run the blanker at the SDR rate in the offline decoder or flowgraph.
- *Cost.* Strong **wanted or adjacent** signals in the wide path also cross the threshold. The blanker then chops them, which splatters (an intermodulation-like artefact). Raise the threshold, or gate the blanker on impulsiveness (high kurtosis of the wideband power) rather than on level.

**Noise reduction (NR).** There are two families. The LMS adaptive line enhancer is covered on the [06 page](../06-rf-circuits/agc-loops-and-receiver-gain-control.md#level-3--receiver-dsp-features). Here is **spectral subtraction** [13]. In the STFT domain each time–frequency cell gets a gain
$$G = \max\!\big(1 - \alpha\,\hat P_n/|Z|^2,\ \beta\big),$$
with $\hat P_n$ the noise power per bin (measured in pauses, or by minimum statistics), $\alpha \ge 1$ an over-subtraction factor and $\beta$ a floor. In §4, three tones at +10 dB per bin in white noise ($\alpha$ = 2, $\beta$ = 0.01) gave a band SNR of −7.3 → −1.0 dB, but an SNR **inside the occupied bins** of 10.4 → 10.5 dB. NR removes noise from cells that hold no signal. It cannot separate signal from noise within a cell. It makes a signal more pleasant to listen to and easier to see, **not more detectable**. Its signature artefact is **musical noise**: empty cells where the noise happened to exceed $\alpha\hat P_n$ pass with high gain and are heard as random warbling tones. In §4, 1.8 % of the empty cells passed with a gain above 0.5 (that needs $|Z|^2 > 2\alpha\hat P_n$). For exponentially distributed cell power the probability is $e^{-2\alpha} = e^{-4}$ = 1.8 %. The cures are gain smoothing over time (decision-directed / Ephraim–Malah [14]) and a higher floor β. Never put NR ahead of a data demodulator: the time-varying gain distorts the symbols.

**Auto-notch (ANF).** The LMS prediction-error version is on the 06 page. Two software alternatives: in the STFT domain, find persistent bins (high mean, low variance across frames) and zero them; for data, measure the carrier and place a fixed IIR notch ([digital filters](digital-filters-fir-iir.md)), so that no adaptive filter chases the wanted signal.

**IF shift and passband tuning.** A software channel filter is a real low-pass prototype modulated to a complex band-pass: $h[n] = h_{LP}[n]e^{j\omega_0n}$, so $H(\omega) = H_{LP}(\omega-\omega_0)$. Moving the passband therefore means changing $\omega_0$ only, with no redesign. Equivalently, shift the signal by −Δ with an [NCO](nco-ddc-duc.md), filter with the fixed filter and shift back. **IF shift** moves the passband relative to the (fixed) demodulation carrier. In §5 a 300–2700 Hz USB filter has an interferer at 2.6 kHz inside the passband (0 dB rejection). Shifting the passband by −300 Hz (to 0–2400 Hz) puts the interferer **60 dB** down, and a 1 kHz speech component is unchanged (< 0.1 dB). **Passband tuning** (PBT, "twin PBT") cascades two filters shifted in opposite directions to vary the width. In software you simply design the width you want.

**Roofing filters, and why an SDR cannot have a digital one.** In a superheterodyne the roofing filter is the first narrow filter after the first mixer, e.g. a 3–15 kHz crystal filter at a 45–70 MHz first IF ([crystal filters](../06-rf-circuits/duplexers-diplexers-and-crystal-filters.md)). It keeps strong neighbours out of the high-gain IF stages and the later mixer, so their intermodulation and blocking are never exercised. In an SDR everything inside the ADC's analog bandwidth reaches the ADC: the anti-alias and preselector filters and the tuner's IF filter are the real "roof". Strong signals anywhere in that bandwidth use up ADC headroom, create ADC spurs and IMD, and pull the AGC down *before* any digital filter acts. A digital filter is a perfect channel filter but never a roofing filter, because it cannot protect what comes before it. Narrowing the decimation or the display bandwidth does not help. Narrowing the analog bandwidth (a preselector, the tuner's IF bandwidth setting, or a lower ADC rate behind a real anti-alias filter) does ([front-end protection](sdr-front-end-protection-and-filtering.md), [dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)).

## Design equations & rules of thumb

| Equation / rule | When valid | Typical values |
|---|---|---|
| $\hat f = \frac{f_s}{2\pi}\arg(x[n]x^*[n-1])$ | FM/FSK, $\lvert f\rvert<f_s/2$ | exact per-sample phase step |
| Discriminator rate ≥ Carson BW | FM | WBFM ≥ 200–250 kS/s; NBFM 12.5–25 kS/s |
| De-emphasis corner $1/(2\pi\tau)$ | broadcast FM | 50 µs: 3183 Hz; 75 µs: 2122 Hz |
| $P_b = \tfrac12e^{-E_b/2N_0}$ | non-coherent orthogonal BFSK | 10.94 dB for 10⁻³ |
| Discriminator loss | 2-FSK h=1 / 2-GFSK h=0.5 BT=0.5 | +0.07 / +1.41 dB (script config) |
| Gardner $e = \mathrm{Re}\{y^*_{k-1/2}(y_k-y_{k-1})\}$ | ≥ 2 samples/symbol, PSK/QAM | sign error → locks on zero crossings |
| QPSK Costas $e = \mathrm{sgn}(I)Q - \mathrm{sgn}(Q)I$ | decision-directed | 90° ambiguity |
| LoRa: dechirp + $2^{SF}$-pt FFT = non-coherent M-FSK | $f_s = BW$ (or decimate to it) | SF7 SER 1.6×10⁻³ at −8 dB |
| LoRa bin = $BW/2^{SF}$ | CFO sensitivity | SF7/125k: 977 Hz; SF12: 30.5 Hz |
| PER ≈ $1-(1-P_b)^L$ | independent bit errors | L = 232 bits |
| Blanker threshold $k\cdot\mathrm{median}\lvert x\rvert/\sqrt{\ln2}$; false-blank $e^{-k^2}$ | complex Gaussian background | k = 4: 1.1 × 10⁻⁷ |
| Blanking loss $-10\log_{10}(1-p)$ | fraction p blanked, AWGN | 5 %: 0.22 dB |
| Spectral subtraction $G=\max(1-\alpha\hat P_n/\lvert Z\rvert^2,\beta)$ | audio/visual NR only | musical-noise cells $e^{-2\alpha}$ |
| Complex BPF $h_{LP}[n]e^{j\omega_0n}$ | IF shift / passband tuning | 300 Hz shift: +60 dB on an edge interferer |

## Worked examples

**1 — Broadcast FM receiver on an RTL-SDR.** Tune to the station, $f_s$ = 2.4 MS/s. Decimate by 10 to 240 kS/s with a low-pass at ±100 kHz (the MPX baseband with stereo pilot at 19 kHz, L−R subcarrier at 38 kHz and RDS at 57 kHz fits in ±60 kHz; the RF deviation is ±75 kHz). Polar discriminator at 240 kS/s → mono audio = MPX low-passed at 15 kHz → 50 µs de-emphasis → decimate by 5 to 48 kHz. Cost ≈ one 40-tap filter at 240 kS/s + one atan per sample: trivial. GNU Radio's `WBFM Receive` block packages the discriminator and de-emphasis.

**2 — 9.6 kbit/s GFSK rocket telemetry (as from an ISM FSK chip).** $h$ = 1 (±4.8 kHz deviation), BT = 0.5. Channel filter ±(9.6 + CFO margin) kHz; 10 samples/bit at 96 kS/s; discriminator; preamble-based CFO removal; sync-word search; CRC. From the script, PER ≈ 5 % at 13 dB Eb/N0 for a 29-byte frame. With the receiver noise figure and bandwidth, that sets the sensitivity: $P_{min} = -174 + NF + 10\log_{10}R_b + E_b/N_0 = -174 + 6 + 39.8 + 13 = -115$ dBm for 5 % PER ([sensitivity](../07-noise-linearity/sensitivity-and-mds.md)). Compare LoRa SF7/BW125 at roughly −123 dBm (datasheet class, [LoRa sensitivity](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md)).

**3 — LoRa SF9/BW125 symbol error budget.** $M$ = 512, bin = 244 Hz. A 433.92 MHz TCXO ground station (1 ppm → 434 Hz) plus a 10 ppm flight crystal (4.3 kHz) plus Doppler (±434 Hz at 300 m/s): up to ~5.2 kHz ≈ 21 bins of CFO — far outside any tolerance if uncorrected; the preamble estimator removes the integer and fractional parts before payload demodulation. The residual after estimation must stay ≪ 0.5 bin (122 Hz) across the packet; at a Doppler rate of 145 Hz/s (100 m/s² of range acceleration — the **range** acceleration $\ddot R = \mathbf a\cdot\hat{\mathbf r} + v_\perp^2/R$ seen by the station, up to ≈ 1.4× the vehicle's acceleration near the pad ([15 impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md#doppler-rate-seen-from-the-ground--the-line-of-sight-rotation-term))) a 0.5 s SF9 packet drifts 73 Hz — ~0.3 bin, a measurable loss; SF12's 30.5 Hz bins are far more sensitive.

**4 — Decoding an APRS beacon from a balloon.** 1200 baud AFSK in NBFM. SDR at 1.2 MS/s → ÷25 → 48 kS/s → discriminator → direwolf. Weak-signal performance is limited by the AFSK-on-FM double modulation (roughly 10–15 dB worse than a well-designed GFSK link at the same bit rate — an estimate, not simulated here), which is why rocket telemetry designers prefer direct GFSK or LoRa.

## Practical notes
- **GNU Radio blocks**: `Quadrature Demod`, `WBFM Receive`, `NBFM Receive`, `AM Demod`, `Complex to Mag`, `Costas Loop`, `Symbol Sync` (Gardner/M&M/…, with polyphase interpolators), `Polyphase Clock Sync`, `FLL Band-Edge`, `Correlate Access Code - Tag Stream`, `Binary Slicer`; gr-lora_sdr for LoRa [6], [8].
- **Always look before decoding**: waterfall and constellation/eye views catch CFO, IQ swap (conjugate the samples to test), clipping and wrong sample rate faster than any BER counter.
- **Sign/rotation conventions**: an IQ swap or spectral inversion ([sampling](sampling-aliasing-bandpass-sampling.md)) turns USB into LSB, inverts FSK bits and turns LoRa up-chirps into down-chirps.
- **Keep the discriminator's input rate comfortably above the signal bandwidth** (≥ 2× the Carson bandwidth) so that noise-driven phase jumps do not exceed ±π too often (clicks).
- **AGC before PSK loops**: loop gains assume a fixed signal amplitude; without AGC the loop bandwidth changes with signal level.
- **Offline decoding** of recorded IQ is the best way to develop: repeatable, debuggable, and it lets you compare decoders on the same data.

## Common mistakes & misconceptions
1. **Taking `np.diff(np.angle(x))` without unwrapping** — phase wraps give ±2π spikes. Use $\arg(x[n]x^*[n-1])$.
2. **Running the FM discriminator at too low a rate** (deviation + offset near $f_s/2$) — distortion and clicks.
3. **Forgetting de-emphasis** — tinny, hissy broadcast audio.
4. **Gardner sign or interpolation-phase errors** — the loop locks happily on the wrong point. Check the eye at the chosen instant.
5. **Assuming the discriminator is "just as good" as matched filters** — true for $h \approx 1$ (0.07 dB here), not for GFSK with $h$ = 0.5 (1.4 dB here).
6. **Ignoring CFO in LoRa** — one bin of CFO decodes every symbol wrong by one; the CRC then fails for all packets although the waterfall looks perfect.
7. **Cutting the burst window tight** — tail bits (CRC) lost (the bug found in this page's script).
8. **Averaging over data to estimate CFO** in FSK — use the balanced preamble.
9. **SSB "Donald Duck" audio** — tuning error; fix the frequency, not the filter.
10. **Noise blanker after the channel filter**, or a threshold set from the rms level. The filter smears impulses below threshold (SER 0.028 vs 0.0013 in the LoRa demo), and the rms estimate is inflated 7× by the impulses themselves. Blank in the wide path and use a median-based level.
11. **"DSP noise reduction improves sensitivity."** It removes noise only from cells without signal. In-bin SNR, and hence decodability, is unchanged (10.4 → 10.5 dB). NR before a data demodulator makes things worse.
12. **"A sharp digital filter is my roofing filter."** Everything inside the analog bandwidth already hit the ADC (and the AGC detector). Only analog filtering ahead of the ADC protects dynamic range.

## How to simulate / verify
- `python3 tools/verify/dsp_demod.py` (≈ 4 s): FM (polar and derivative) discriminators, WBFM level, de-emphasis, AM envelope and synchronous, SSB phasing and demodulation, non-coherent BFSK BER vs theory, discriminator 2-FSK/2-GFSK loss, QPSK receiver with Gardner + Costas vs theory, LoRa SF7 dechirp SER vs exact M-FSK integral, LoRa CFO shift and preamble estimate, CRC check values, end-to-end GFSK packet PER curve. All PASS.
- `python3 tools/verify/s7_noise_blanker.py` (≈ 2 s, ALL PASS): robust (median) impulse threshold vs rms/mean, false-blank rate $e^{-k^2}$, LoRa SF7 SER in Bernoulli–Gaussian impulsive noise (no blanker / wide-path blanker / clipper / blanker after decimation), blanking loss, spectral subtraction band vs in-bin SNR and musical-noise fraction, IF shift with a modulated low-pass prototype.
- Companion scripts in domain 10: `tools/verify/comms_matched_filter.py` (matched filter/correlator detection), `comms_pulse_shaping.py` (RRC/raised-cosine, ISI), `comms_sync.py` (carrier and timing recovery), `comms_analog_fm.py` (FM theory: Carson bandwidth, threshold), `comms_lora_cr.py` (LoRa coding rates) — see [10 synchronisation](../10-comms-modulation/synchronization-carrier-timing.md) and [10 pulse shaping](../10-comms-modulation/pulse-shaping-isi.md).
- Practice on recordings: capture a local broadcast FM station and an APRS or 433 MHz sensor burst as SigMF, then decode them in Python with the one-liners above before moving to GNU Radio flowgraphs ([software stack](gnu-radio-and-software-stack.md)).

## Open questions / gaps
- Discriminator loss was simulated for one receiver configuration (Carson-width pre-detection filter, integrate-and-dump); the dependence on pre-detection bandwidth and BT is not mapped.
- APRS/AX.25 and rtl_433 details are from general knowledge of the standards/software, not re-read this session; the AFSK-vs-GFSK penalty is an estimate.
- LoRa implementation losses of gr-lora_sdr vs Semtech silicon are not quantified here (domain 15).

## Sources
1. R. G. Lyons, *Understanding Digital Signal Processing*, 3rd ed., Prentice Hall (2011), ch. 13 (DSP tricks incl. FM and AM demodulation algorithms), ch. 8 (quadrature signals). (textbook)
2. M. Rice, *Digital Communications: A Discrete-Time Approach*, Pearson/Prentice Hall (2009), ch. 7 (carrier phase synchronisation), ch. 8 (symbol timing synchronisation, interpolation). (textbook)
3. F. M. Gardner, "A BPSK/QPSK timing-error detector for sampled receivers," *IEEE Trans. Communications* COM-34(5):423–429 (1986). (peer-reviewed)
4. J. P. Costas, "Synchronous communications," *Proc. IRE* 44(12):1713–1718 (1956). (peer-reviewed)
5. J. G. Proakis, M. Salehi, *Digital Communications*, 5th ed., McGraw-Hill (2008), §4.5 (non-coherent detection; binary and M-ary orthogonal FSK error probabilities). (textbook)
6. J. Tapparel, O. Afisiadis, P. Mayoraz, A. Balatsoukas-Stimming, A. Burg, "An open-source LoRa physical layer prototype on GNU Radio," *IEEE SPAWC* (2020), arXiv:2002.08208; code https://github.com/tapparelj/gr-lora_sdr (SF5–12, CR 4/5–4/8, implicit/explicit header, soft decoding; tested vs SX1276/SX1262). (peer-reviewed + code)
7. L. Vangelista, "Frequency shift chirp modulation: the LoRa modulation," *IEEE Signal Processing Letters* 24(12):1818–1821 (2017). (peer-reviewed) — dechirp + DFT demodulation, orthogonality.
8. GNU Radio project, block documentation (Quadrature Demod, WBFM/NBFM Receive, Costas Loop, Symbol Sync, FLL Band-Edge, Correlate Access Code), https://wiki.gnuradio.org (docs; wiki not directly reachable this session — see [software stack](gnu-radio-and-software-stack.md)).
9. M. Lichtman, *PySDR*, chapters "Synchronization", "Pulse Shaping", "Digital Modulation", https://pysdr.org (online textbook).
10. TAPR, *AX.25 Link Access Protocol for Amateur Packet Radio* v2.2 (1998) and *APRS Protocol Reference* v1.0 (2000); J. Langner (WB2OSZ), Dire Wolf software modem, https://github.com/wb2osz/direwolf; B. Larsson et al., rtl_433, https://github.com/merbanan/rtl_433. (standards + software docs) — *from general knowledge; not re-read this session.*
11. G. Cook, "Catalogue of parametrised CRC algorithms" (CRC RevEng), https://reveng.sourceforge.io/crc-catalogue/ — CRC-16/CCITT-FALSE (0x29B1) and CRC-16/X-25 (0x906E) check values (reproduced in the script). (docs)
12. D. Middleton, "Statistical-physical models of electromagnetic interference," *IEEE Trans. Electromagnetic Compatibility* EMC-19(3):106–127 (1977). (peer-reviewed; cited, not re-read) — class-A/B impulsive-noise models; the Bernoulli–Gaussian model used here is the simplest class-A-like case.
13. S. F. Boll, "Suppression of acoustic noise in speech using spectral subtraction," *IEEE Trans. ASSP* 27(2):113–120 (1979). (peer-reviewed; cited, not re-read) — magnitude/power spectral subtraction, musical noise.
14. Y. Ephraim, D. Malah, "Speech enhancement using a minimum mean-square error short-time spectral amplitude estimator," *IEEE Trans. ASSP* 32(6):1109–1121 (1984). (peer-reviewed; cited, not re-read) — decision-directed gain smoothing.
15. `tools/verify/s7_noise_blanker.py` (this KB) — all receiver-DSP-feature numbers; the median-of-Rayleigh threshold is derived ($F(r)=1-e^{-r^2/\sigma^2}$ = ½ at $r=\sigma\sqrt{\ln2}$).
