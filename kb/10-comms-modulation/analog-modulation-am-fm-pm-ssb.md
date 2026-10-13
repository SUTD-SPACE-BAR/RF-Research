---
title: Analog modulation — AM, DSB, SSB, VSB, FM and PM
domain: 10-comms-modulation
slug: analog-modulation-am-fm-pm-ssb
tags: [AM, DSB-SC, SSB, VSB, FM, PM, NBFM, modulation-index, Bessel, Carson-rule, FM-threshold, capture-effect, pre-emphasis, de-emphasis, envelope-detector, APRS, AFSK, LSB-USB-convention, speech-crest-factor, PEP-average, speech-processor, RF-clipping, ALC, flat-topping, necessary-bandwidth, CW, Morse, emission-designator]
prerequisites:
  - ../00-math-foundations/complex-numbers-and-phasors.md
  - ../00-math-foundations/fourier-series-and-transform.md
  - ../00-math-foundations/special-functions-bessel-sinc.md
related:
  - digital-modulation-psk-qam-fsk.md
  - ber-ebn0-and-shannon.md
  - ../06-rf-circuits/mixers.md
  - ../06-rf-circuits/receiver-architectures.md
  - ../06-rf-circuits/transmitter-architectures.md
  - ../07-noise-linearity/sensitivity-and-mds.md
  - ../14-sdr-dsp/software-demodulation.md
  - ../17-test-measurement/spectrum-analyzers.md
  - ../19-regulations-safety/amateur-radio-licensing.md
  - ../19-regulations-safety/spectrum-allocation-ism-bands.md
  - ../06-rf-circuits/pa-control-protection-and-sequencing.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Analog modulation — AM, DSB, SSB, VSB, FM and PM

## Questions this page answers
- How much of an AM signal's power actually carries the message?
- What is the difference between AM, DSB-SC, SSB and VSB, and when does each need a coherent receiver?
- What is the FM modulation index, and how do Bessel functions give the FM spectrum?
- How wide is an FM signal (Carson's rule), and how good is that rule?
- Why does FM give better audio SNR than AM, and what is the "FM threshold"?
- What is the capture effect, and why can two FM stations not be heard at once while two AM aircraft can?
- What are pre-emphasis and de-emphasis (75 µs / 50 µs), and how many dB do they buy?
- How is APRS / 1200-baud packet sent over an NBFM radio, and what bandwidth does it use?
- How do I calibrate FM deviation with a spectrum analyser?
- Why is LSB used below 10 MHz and USB above, and where must the dial be relative to a band edge?
- How wide is an SSB voice signal, and why is the audio cut at about 300 Hz and 2.7–3 kHz?
- What is the PEP-to-average ratio of SSB speech, and why does it matter for the power amplifier?
- What does a speech processor (compressor or RF clipper) do, and what goes wrong when it or the mic gain is set too high?
- What is ALC on an SSB transmitter, and what is "flat-topping"?
- What is the necessary bandwidth of CW, AM, SSB and FM, and why is Morse code so power-efficient?
- Can I put AM and FM on the same carrier to send two signals at once — is that just QAM?

## TL;DR
- **AM (DSB-LC):** $s(t)=A_c[1+\mu m(t)]\cos\omega_ct$. Total power $P_c(1+\mu^2/2)$ for tone modulation → at best **1/3** of the power is in the sidebands. Envelope-detector figure of merit (output SNR ÷ baseband-equivalent SNR) $=\mu^2/(2+\mu^2)$: −4.8 dB at μ = 1, −6.2 dB at μ = 0.8 (verified).
- **DSB-SC and SSB** with coherent detection have figure of merit **1** (0 dB); SSB uses half the bandwidth of DSB. They need a carrier reference (pilot, or manual tuning for SSB voice). **VSB** keeps a vestige of one sideband so DC/low frequencies survive (analog TV).
- **FM/PM:** instantaneous frequency $f_c+k_fm(t)$; peak deviation $\Delta f$; modulation index $\beta=\Delta f/f_m$. Tone FM spectrum = lines at $f_c\pm nf_m$ with amplitudes $J_n(\beta)$; carrier vanishes at β = 2.405, 5.520, 8.654 (a standard deviation-calibration trick).
- **Carson's rule** $B_T\approx2(\Delta f+W)$ holds ≥ 99 % of the power for tone FM with β ≥ 1 (verified). NBFM voice: ±5 kHz/3 kHz → **16 kHz**; ±2.5 kHz/3 kHz → **11 kHz**; broadcast mono ±75 kHz/15 kHz → **180 kHz** (NTIA emission designators 16K0F3E, 11K0F3E, 180KF3E).
- **FM SNR gain above threshold:** $\mathrm{SNR}_o=\tfrac32\beta^2\,\mathrm{SNR}_C$ (tone), verified by simulation to 0.1 dB. β = 5 → +15.7 dB over baseband; de-emphasis adds **13.2 dB (75 µs)** or **10.2 dB (50 µs)** for W = 15 kHz.
- **Threshold:** below ≈ **10 dB carrier-to-noise ratio in the IF (Carson) bandwidth**, "clicks" appear and output SNR collapses (simulated: 0.1 dB short at 10 dB CNR, 8.8 dB short at 7 dB, 16.8 dB short at 4 dB).
- **Capture effect:** a limiter + discriminator follows the stronger of two co-channel FM signals and suppresses the weaker by more than the input ratio (simulated output SIR 14.5 dB for a 6 dB input D/U). AM has no such effect.
- **SSB practice:** LSB below 10 MHz, USB at 10 MHz and above (and on VHF/UHF and for all data modes); this is convention, not physics. Voice is filtered to ≈ 300–2700 Hz (necessary bandwidth 2K70J3E). **Unprocessed speech has an SSB PEP/average of ≈ 12–15 dB** (simulated TTS speech 13.3–15.1 dB over a sentence; ≈ 12–14 dB while talking), so a 100 W PEP transmitter averages only ≈ 4–5 W. The exam figure "2.5:1" (4 dB) corresponds to heavily processed speech. RF clipping by 12 dB plus re-filtering raises average power ≈ 5 dB at the same PEP (`tools/verify/s2_speech_crest.py`).
- **Necessary bandwidth (ITU-R SM.1138):** Morse $B_n = 5B$ (B ≈ 0.8 × WPM: 100 Hz at 25 WPM, 52 Hz at 13 WPM); AM $2M$; SSB $M - M_{low}$; FM $2M + 2DK$ (Carson). CW's advantage is bandwidth: a 100 Hz filter has 14.3 dB less noise than a 2.7 kHz SSB filter, at the same power.
- **APRS** = 1200 baud Bell-202 AFSK (1200/2200 Hz tones) fed into an NBFM voice radio — convenient but ≈ 8 dB less sensitive than direct NC-FSK and ≈ 15 dB less than LoRa at a similar bit rate (threshold-limited estimate, Example 5).

## Intuition (no math)
A carrier is a pure sine wave. To carry a message you must vary something about it: its **amplitude** (AM) or its **angle** — frequency (FM) or phase (PM).

*AM* is the simplest to picture: the envelope of the carrier traces the audio waveform, and a diode plus capacitor (envelope detector) recovers it. But most of the transmitted power sits in the unchanging carrier, which carries no information. Suppress the carrier (DSB-SC) and you save power but the envelope no longer follows the message — the receiver must regenerate the carrier exactly. Throw away one of the two mirror-image sidebands (SSB) and you also halve the bandwidth; this is why HF voice and amateur long-distance work use SSB.

*FM* keeps the amplitude constant and moves the frequency up and down with the message. Because the information is in *when* the zero crossings happen, not in the amplitude, amplitude noise is removed by a limiter — and if you swing the frequency widely (large deviation), a given amount of noise-induced wobble in the zero crossings becomes small relative to the wanted swing. You buy SNR with bandwidth. The trade breaks when the noise is strong enough to occasionally spin the phase a full turn around the origin: each such event produces a "click", and output SNR falls off a cliff — the FM threshold.

Why can't you hear two FM stations at once? The limiter/discriminator measures the instantaneous frequency of the *sum*, which is dominated by the stronger signal; the weaker one only adds a small wobble. In AM, both envelopes add linearly and you hear both — which is why aviation voice (AM) lets controllers hear a "blocked" transmission.

## The math

### Level 1 — definitions and power
Carrier $A_c\cos(2\pi f_ct)$, message $m(t)$ normalised to $|m|\le1$, message bandwidth $W$ (Hz).

| Scheme | Signal | Bandwidth | Power (tone, $m=\cos\omega_mt$) |
|---|---|---|---|
| AM (DSB-LC) | $A_c[1+\mu m(t)]\cos\omega_ct$ | $2W$ | $\frac{A_c^2}{2}(1+\frac{\mu^2}{2})$; sidebands $\frac{\mu^2/2}{1+\mu^2/2}$ of total |
| DSB-SC | $A_cm(t)\cos\omega_ct$ | $2W$ | all in sidebands |
| SSB (USB/LSB) | $\frac{A_c}{2}[m\cos\omega_ct\mp\hat m\sin\omega_ct]$ | $W$ | one sideband |
| VSB | DSB filtered with a vestigial-symmetric response | $W+$ vestige | – |
| PM | $A_c\cos[\omega_ct+k_pm(t)]$ | ≈ $2(\Delta f+W)$ | $A_c^2/2$ (constant) |
| FM | $A_c\cos[\omega_ct+2\pi k_f\!\int m\,d\tau]$ | ≈ $2(\Delta f+W)$ | $A_c^2/2$ (constant) |

$\hat m$ is the Hilbert transform of $m$ (every frequency component shifted by −90°). Peak frequency deviation $\Delta f=k_f\max|m|$ (Hz); **deviation ratio** $D=\Delta f/W$; for a tone, **modulation index** $\beta=\Delta f/f_m$ (rad) — the peak phase excursion. PM and FM are the same thing with a differentiator/integrator in front: FM of $m$ = PM of $\int m$.

### Level 2 — spectra and detection

**AM power and envelope detection.** With $m=\cos\omega_mt$, $s=A_c\cos\omega_ct+\frac{\mu A_c}{2}[\cos(\omega_c+\omega_m)t+\cos(\omega_c-\omega_m)t]$: carrier power $A_c^2/2$, each sideband $\mu^2A_c^2/8$. At $\mu=1$ (100 % modulation) the two sidebands together hold $1/3$ of the power. Overmodulation ($\mu>1$) makes $1+\mu m$ negative, the envelope folds, and an envelope detector distorts badly.

**Coherent detection** multiplies by a local carrier $\cos(\omega_ct+\theta)$ and low-pass filters: the output is $\tfrac12A_cm(t)\cos\theta$ for DSB-SC. A phase error θ scales the output (a 90° error gives nothing); a frequency error makes the output beat. For SSB a frequency error shifts every audio component by the same Hz (the "Donald Duck" effect), which voice tolerates for a few tens of Hz; a phase error merely rotates components (inaudible). That is why SSB voice works with a free-running local oscillator but DSB-SC does not [1], [2].

**FM spectrum from Bessel functions.** For $m=\cos\omega_mt$ the complex envelope is $e^{j\beta\sin\omega_mt}$. This is periodic in $t$; its Fourier series is the generating function of the Bessel functions of the first kind,
$$e^{j\beta\sin\theta}=\sum_{n=-\infty}^{\infty}J_n(\beta)e^{jn\theta},$$
so
$$s(t)=A_c\sum_{n=-\infty}^{\infty}J_n(\beta)\cos\big[(\omega_c+n\omega_m)t\big].$$
Lines at $f_c\pm nf_m$ with amplitude $A_cJ_n(\beta)$; $J_{-n}=(-1)^nJ_n$. Power conservation: $\sum_nJ_n^2(\beta)=1$ (the envelope is constant, so the total power is too). Checked in the script by FFT of a synthesised FM signal against `scipy.special.jv`. See [special functions](../00-math-foundations/special-functions-bessel-sinc.md) for $J_n$ itself.
- *Narrowband FM* ($\beta\ll1$): $J_0\approx1$, $J_{\pm1}\approx\pm\beta/2$, the rest negligible — two sidebands like AM but in quadrature with the carrier.
- *Wideband FM*: significant lines extend to $|n|\approx\beta+1$.

**Carson's rule.** Keeping lines up to $|n|=\beta+1$ gives $B_T=2(\beta+1)f_m=2(\Delta f+f_m)$ [3]. For a general message of bandwidth $W$: $B_T\approx2(\Delta f+W)=2W(D+1)$. The script computes the power inside: 99.8 % (β = 0.5), 99.9 % (β = 1), 99.8 % (β = 2), 99.4 % (β = 5), 99.0 % (β = 10). The rule under-estimates the 1 %-power bandwidth for real programme material with large D; some texts use $2(\Delta f+2W)$ for that. Regulators use Carson with $K=1$: $B_n=2M+2KD$ [4].

**FM demodulation.** Limit (remove amplitude), then produce a voltage proportional to instantaneous frequency: slope/Foster–Seeley/ratio/quadrature detectors in analog; in DSP, $f_i[n]=\frac{f_s}{2\pi}\arg(r[n]r^*[n-1])$ ([software demodulation](../14-sdr-dsp/software-demodulation.md)). A PLL demodulator tracks the phase and outputs its VCO control voltage.

### Level 2b — noise performance (above threshold)
Define the **channel SNR** $\mathrm{SNR}_C$ = received signal power / noise power in the *message* bandwidth $W$ (the SNR a baseband system would get with the same power). The figure of merit $\Gamma=\mathrm{SNR}_o/\mathrm{SNR}_C$ compares schemes fairly [1], [2]:

| Scheme | $\Gamma$ | Notes |
|---|---|---|
| DSB-SC coherent | 1 | verified |
| SSB coherent | 1 | half the bandwidth of DSB |
| AM envelope, high SNR | $\dfrac{\mu^2\overline{m^2}}{1+\mu^2\overline{m^2}}$ → $\dfrac{\mu^2}{2+\mu^2}$ (tone) | ≤ 1/3; verified at μ = 0.5, 0.8 |
| FM (tone) | $\tfrac32\beta^2$ | verified at β = 4 |
| FM (general) | $3D^2\,\overline{m^2}$ (with $|m|\le1$) | |
| PM (general) | $k_p^2\overline{m^2}$ | |

*Derivation for FM (complex-baseband form).* Received $r=A_ce^{j\phi(t)}+n(t)$, $n$ complex white with PSD $N$. At high SNR the phase noise is $\psi\approx\mathrm{Im}\{ne^{-j\phi}\}/A_c$, white with PSD $N/(2A_c^2)$. The discriminator outputs $\frac1{2\pi}\frac{d\psi}{dt}$, whose PSD is $f^2N/(2A_c^2)$ — noise rises as $f^2$ (**parabolic output noise**). Integrating over $|f|<W$: output noise power $NW^3/(3A_c^2)$. The signal output is $\Delta f\cos\omega_mt$ with power $\Delta f^2/2$. Hence $\mathrm{SNR}_o=\frac{3A_c^2\Delta f^2}{2NW^3}=\frac32\left(\frac{\Delta f}{W}\right)^2\frac{A_c^2}{NW}=\frac32\beta^2\mathrm{SNR}_C$ [1 ch. 2], [2]. The simulation (β = 4, CNR 13–25 dB) matches to ±0.1 dB.

**Pre-emphasis / de-emphasis.** Because FM output noise grows as $f^2$ while programme energy is concentrated at low audio frequencies, the transmitter boosts high audio frequencies (pre-emphasis, a zero at $f_1=1/(2\pi\tau)$) and the receiver cuts them back (de-emphasis, a pole at $f_1$). The signal is unchanged; the noise is reduced by
$$I=\frac{\int_0^Wf^2df}{\int_0^W\frac{f^2}{1+(f/f_1)^2}df}=\frac{(W/f_1)^3}{3\left[W/f_1-\arctan(W/f_1)\right]}.$$
For broadcast FM (W = 15 kHz): τ = 75 µs (Americas, Korea) → $f_1=2.12$ kHz, **13.2 dB**; τ = 50 µs (Europe, most of Asia) → $f_1=3.18$ kHz, **10.2 dB** (closed form and numerical integral agree in the script) [1], [2]. Land-mobile NBFM uses a +6 dB/octave pre-emphasis across the 300–3000 Hz voice band (phase-modulation-like), with the same purpose (unverified exact standard curve — see gaps).

### Level 3 — threshold, clicks, capture, and limits of the theory
**FM threshold.** The linearised analysis assumes the noise phasor is much smaller than the carrier. When it occasionally exceeds it, the resultant can encircle the origin, adding a $2\pi$ phase step whose derivative is an impulse — a click with energy spread across the audio band. Rice's analysis gives the click rate as a function of CNR; the practical result is a knee at **CNR ≈ 10 dB in the IF (≈ Carson) bandwidth**, below which output SNR drops much faster than linearly [5]. The simulation (β = 4, IF = Carson): shortfall vs linear theory 0.0 dB at 13 dB CNR, 0.1 dB at 10 dB, 8.8 dB at 7 dB, 16.8 dB at 4 dB. Threshold-extension demodulators (PLL, FM with feedback) move the knee down by a few dB. Wider deviation raises $\Gamma$ but also widens the IF, raising the noise in it — so for a fixed received power there is an optimum deviation that just keeps CNR above threshold. That is the classic FM power–bandwidth trade.

**Capture.** With a wanted signal of amplitude 1 and an interferer of amplitude $a<1$ at offset frequency $f_d$, the resultant phase is $\phi_1+\arctan\frac{a\sin\theta}{1+a\cos\theta}$ ($\theta$ = phase difference). The discriminator output contains the wanted modulation plus an interference term whose size falls rapidly as $a\to0$ — the weaker signal is suppressed more than proportionally. As $a\to1$ the output jumps between the two ("capture ratio" = input D/U needed for a specified suppression; good broadcast tuners quote 1–2 dB, (forum/marketing figures — unverified)). Simulated (limiter-discriminator, 3 kHz audio): D/U 1/3/6/10 dB → output SIR 8.3/11.0/14.5/18.6 dB.

**Where the analysis breaks.** $\Gamma$ values assume a high SNR, an ideal limiter, and no IF filtering distortion. With large deviation relative to the IF filter, or a frequency offset that pushes the signal into the filter skirt (e.g. Doppler plus crystal error on a rocket), the discriminator output is distorted even without noise.


## SSB in practice — sideband conventions, speech statistics and processing

### Which sideband, and where the dial sits
SSB is named by the sideband kept. **USB** puts the audio spectrum above the suppressed-carrier ("dial") frequency, the right way up. **LSB** puts it below, inverted. Amateur voice convention is **LSB below 10 MHz (160, 80, 40 m)** and **USB at 10 MHz and above (20 m and up, and all VHF/UHF SSB)**. Data modes (FT8, PSK31, WSPR) use USB on every band, and 60 m (5 MHz) is USB by regulation in most countries. The usual explanation is historical rather than technical. Early filter exciters used a ≈ 9 MHz sideband filter mixed with a ≈ 5–5.5 MHz VFO. The sum (14 MHz) keeps the sideband sense and the difference (≈ 3.5–4 MHz) inverts it, so one filter gave USB on 20 m and LSB on 75/80 m, and the habit stuck (unverified — forum-level history; ham.stackexchange q/1336). Physically the two sidebands are equivalent: the same message, the same power and the same bandwidth.

**Band-edge rule.** An LSB signal occupies roughly dial − 3 kHz … dial, so the dial must be ≥ 3 kHz above a lower band edge. A USB signal occupies dial … dial + 3 kHz, so the dial must be ≥ 3 kHz below an upper edge. This is the same "whole emission inside the band" rule the [canonical page](../00-math-foundations/canonical-values-and-conventions.md) applies to LoRa channels.

### How wide is SSB voice
Speech intelligibility lives in about 300–3000 Hz. Below 300 Hz there is mostly voiced-pitch energy that adds peak power but little intelligibility, and it is also where the carrier-suppression notch and hum sit. Above about 3 kHz there is fricative detail. Transmit filters are typically 2.4–2.7 kHz wide (≈ 300–2700 Hz). ITU-R SM.1138 computes the necessary bandwidth as $B_n = M - M_{low}$: 3000 − 300 = 2.7 kHz → **2K70J3E** [10]. NTIA uses 2K80J3E for commercial SSB [4]. A "wide" 3.5–4 kHz SSB transmission buys fidelity at the cost of about 1.5 dB more receiver noise (10 log(4/2.8)) and wider spacing.

### Speech PEP/average — why the PA is mostly idle
For SSB the RF envelope is the magnitude of the analytic signal, $|m(t) + j\hat m(t)|$, so

$$\frac{\mathrm{PEP}}{P_{avg}} = \frac{\max|m + j\hat m|^2}{\overline{|m + j\hat m|^2}}.$$

A single tone gives 1 (0 dB) and the standard two-tone test gives 2 (3.01 dB). Speech is far peakier. Vowels are pitch pulses (100–250 Hz) exciting formant resonances, so each pitch period starts with a sharp peak that decays. Syllables and pauses modulate everything at 3–5 Hz.

| Signal (300–2700 Hz) | Audio crest factor | SSB PEP/avg, whole sentence | SSB PEP/avg, talk frames only |
|---|---|---|---|
| single tone | 3.0 dB | 0.0 dB (1:1) | — |
| two tones | 6.0 dB | 3.0 dB (2:1) | — |
| TTS speech, 4 voices (macOS `say`) | 16.2–17.7 dB | **13.3–15.1 dB (21–32:1)** | 11.9–13.6 dB |
| source–filter speech model (long pauses) | 22.0 dB | 19.2 dB | 12.2 dB |

(`tools/verify/s2_speech_crest.py`. "Talk frames" are 20 ms frames within 30 dB of the loudest frame.) Text-to-speech is smoother than a live talker close to a microphone, so treat these as lower bounds. Published values agree: a 17 dB typical unprocessed SSB PAPR (US patent 4,410,764 [12]) and ≈ 14 dB for a male voice (forum-level). Average SSB power is commonly quoted as 10–20 % of PEP. **The exam answer of ≈ 2.5:1 (4 dB) for "normal voice" [13] is not what unprocessed speech measures.** It is close to what heavy processing achieves (see below), so quote the measurement condition with any PEP/average figure. The consequences:
- A linear PA must be rated for the **PEP** (IMD is specified at PEP with the two-tone test), but its heating and supply current follow the **average**. An unprocessed 100 W PEP voice transmitter delivers ≈ 4–5 W average while talking.
- Receivers hear roughly the average (syllabic) power. Raising average power at a fixed PEP is the whole purpose of speech processing.
- Constant-envelope modes (FM, FSK, LoRa) have PEP/average = 1. That is why they can use saturated class-C/E PAs, and why a LoRa module's "2 W" is both its peak and its average.

### Speech processing, ALC and flat-topping
| Processing (equal PEP, TTS "Daniel") | PEP/avg (talk) | Average power gain |
|---|---|---|
| none | 13.6 dB | 0 dB (4.4 W of 100 W PEP) |
| envelope ("RF") clip 6 dB + re-filter | 10.9 dB | +2.8 dB |
| RF clip 12 dB + re-filter | 8.9 dB | **+5.1 dB** (≈ 13 W) |
| RF clip 18 dB + re-filter | 8.3 dB | +6.1 dB |
| compressor 10:1 above −20 dB, 1 ms attack, **no look-ahead** | 16.1 dB | −1.9 dB (worse: onsets pass before the gain drops) |
| same compressor **with 1 ms look-ahead** | 9.3 dB | +4.9 dB |

- **Clipping** (audio, IF or "RF" envelope clipping) cuts every peak above a threshold. It creates in-band distortion and, at RF, splatter, so it must be followed by a sideband filter. That filter partly **re-peaks** the signal: each clipped flat top contains components the filter removes, which brings overshoot back. The gain therefore saturates (+5 dB at 12 dB clip, only +6 dB at 18 dB). Hershberger's controlled-envelope SSB (CESSB) removes the overshoot and reports ≈ 3.8 dB more peak reduction, ≈ +140 % average at equal PEP versus ≈ +80 % for fast look-ahead ALC [11]. A 1980s patent quotes 18 dB of SSB clipping reducing PAPR by about 8 dB and plain compression by only about 1 dB [12]; the simulation reproduces both trends.
- **Compression** (a fast AGC on the audio) raises quiet syllables. Without look-ahead, the first peak of each syllable passes at full gain, which is why the plain compressor above made PEP/avg *worse*. Digital processors delay the audio by a few milliseconds so the gain is already down when the onset arrives.
- **ALC** is the transmitter's own peak limiter: it measures PA output or drive and throttles the exciter gain. It should act only on rare peaks, slower than syllables. Driving the rig so ALC is always active turns it into a fast amplitude modulator, which adds IMD. For data modes through an SSB rig, set the audio so ALC never acts ([PA control § ALC](../06-rf-circuits/pa-control-protection-and-sequencing.md)).
- **Flat-topping** is what happens when drive exceeds the PA's linear range: the envelope peaks are clipped *after* the sideband filter, with no filter to clean up. The result is splatter, IMD products several kHz either side and distorted audio, which is the classic "too much mic gain" or "processor set too high" complaint (General-class G4D03). A two-tone test on a scope (a trapezoid or envelope with sharp cusps) shows flat-topping directly.
- Rule of thumb: set the processor to about 10 dB of compression or clipping, with ALC only flickering. That is worth ≈ 4–6 dB of average talk power, close to one S-unit (6 dB). Beyond that, distortion grows faster than intelligibility.

### AM and FM on one carrier, versus QAM
Amplitude and phase are the two independent coordinates of a carrier's complex envelope $A(t)e^{j\phi(t)}$, so a carrier *can* carry one signal in its amplitude and another in its phase or frequency. QAM/APSK does exactly that with digital symbols (ITU class D, "amplitude and angle modulated"), and AM stereo (C-QUAM) did it with analogue audio. There is no free lunch. (1) Total throughput is still bounded by $B\log_2(1+\mathrm{SNR})$ for the occupied bandwidth ([Shannon](ber-ebn0-and-shannon.md)). (2) The amplitude part makes the envelope non-constant, so the PA must be linear. (3) Band-limiting an FM signal converts FM to AM (the filter's slope turns frequency swings into amplitude changes), and a nonlinear PA converts AM to PM, so the two "channels" leak into each other unless the system is designed as a joint 2-D constellation. That is why practical systems use QAM with a matched receiver rather than an AM + FM pair.

## Necessary bandwidth of analogue emissions, and why CW is efficient
The **necessary bandwidth** is the bandwidth "just sufficient" for the required information rate and quality (RR No. 1.152). ITU-R SM.1138 gives the formulas used in licences and emission designators [10]. The designator grammar, digital modes and the out-of-band/spurious domains are on the [spectrum page](../19-regulations-safety/spectrum-allocation-ism-bands.md#emission-designators-and-necessary-bandwidth).

| Emission | Necessary bandwidth $B_n$ | Example → designator |
|---|---|---|
| CW Morse (on–off carrier) | $B_n = BK$; K = 5 for fading circuits, 3 non-fading; B (baud) ≈ 0.8 × WPM [4] | 25 WPM: 5 × 20 = 100 Hz → 100HA1A; 13 WPM: 52 Hz |
| Tone-keyed Morse on AM (MCW) | $BK + 2M$ | 20 Bd, 1 kHz tone → 2K10A2A |
| AM, DSB full carrier | $2M$ | M = 3 kHz → 6K00A3E; broadcast M = 4.5–10 kHz → 9K00–20K0A3E |
| SSB, full / reduced carrier | $M$ | 3K00H3E / R3E |
| SSB, suppressed carrier | $M - M_{low}$ | 300–3000 Hz → 2K70J3E |
| VSB | $M$ + vestige | analogue TV vision |
| FM / PM telephony | $2M + 2DK$, K = 1 (Carson) | ±5 kHz → 16K0F3E; ±2.5 kHz → 11K0F3E; broadcast 180KF3E |
| FSK data | $B + 2DK$, K ≈ 1.2 | 100 Bd, 170 Hz shift → 304HF1B |

`tools/verify/s2_necessary_bandwidth.py` reproduces every SM.1138 sample designator.

**Why Morse/CW is so efficient.** At 25 WPM the information rate is about 20 baud, and the keyed carrier needs only ≈ 100 Hz, so a receiver can use a 100–500 Hz filter. At equal transmitter power, the noise in the detection bandwidth is $10\log_{10}(2700/100)$ = **14.3 dB lower** than for 2.7 kHz SSB (10.3 dB with a 250 Hz filter, 7.3 dB with 500 Hz). The ear-brain also acts as a narrow (tens of Hz) filter and correlates the known tone pitch over time. In addition, all of the transmitter's power sits in one carrier: CW's PEP/average while key-down is 1, against SSB speech's ≈ 13 dB. Together these give CW its well-known 10–20 dB advantage over SSB voice for marginal contacts. It is the same narrow-bandwidth argument that makes FT8/WSPR and low-rate LoRa work far below the noise in a voice channel ([BER and Shannon](ber-ebn0-and-shannon.md)).

**Key clicks** are the out-of-band emission of CW. The keying envelope's edges set the spectrum, not the dot rate: a hard on/off edge has sinc sidelobes falling only 20 dB/decade, while a few-millisecond raised-cosine ramp confines the signal to a few hundred hertz. The ramp-shape spectra and SX126x RampTime choice are worked in [PA control § ramps and key clicks](../06-rf-circuits/pa-control-protection-and-sequencing.md). SM.1138's K = 5 is effectively an allowance for keying shaped well enough that the 5th harmonic of the dot rate is the highest one needed.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $P_{AM}=P_c(1+\mu^2/2)$ | tone AM | μ = 1 → sidebands 33 % |
| $\Gamma_{AM}=\mu^2/(2+\mu^2)$ | envelope, high SNR | −4.8 dB at μ = 1 |
| $\Gamma_{DSB-SC}=\Gamma_{SSB}=1$ | coherent | SSB BW = W |
| FM lines $A_cJ_n(\beta)$ at $f_c\pm nf_m$ | tone FM/PM | carrier null β = 2.405 |
| $B_T=2(\Delta f+W)$ (Carson) | ≥ 99 % power, tone, β ≥ 1 | NBFM 11/16 kHz; FM bcast 180 kHz |
| $\Gamma_{FM}=\tfrac32\beta^2$ (tone), $3D^2\overline{m^2}$ | above threshold | β = 5 → 15.7 dB |
| De-emphasis gain $\frac{(W/f_1)^3}{3[W/f_1-\arctan(W/f_1)]}$ | $f_1=1/2\pi\tau$ | 75 µs → 13.2 dB; 50 µs → 10.2 dB |
| FM threshold CNR ≈ 10 dB in IF BW | limiter-discriminator | PLL demod: a few dB lower |
| NBFM 12 dB SINAD ≈ threshold region | voice receivers | ≈ −120 dBm class |
| SSB PEP/avg $=\max|a|^2/\overline{|a|^2}$, $a=m+j\hat m$ | any SSB signal | tone 0 dB, two-tone 3 dB, unprocessed speech ≈ 12–15 dB |
| Processing gain at equal PEP | RF clip + filter | 6/12/18 dB clip → +2.8/+5.1/+6.1 dB average |
| $B_n$: CW $BK$ (K = 5), B ≈ 0.8·WPM; AM $2M$; SSB $M-M_{low}$; FM $2M+2DK$ | SM.1138 | 100 Hz @ 25 WPM; 6K00A3E; 2K70J3E; 16K0F3E |
| CW vs SSB noise advantage $10\log(B_{SSB}/B_{CW})$ | equal power | 14.3 dB (100 Hz vs 2.7 kHz) |

## Worked examples

### Example 1 — NBFM channel widths
25 kHz-channel voice: $\Delta f=5$ kHz, $W=3$ kHz → $B_T=2(5+3)=16$ kHz; $D=1.67$. 12.5 kHz channel: $\Delta f=2.5$ kHz → $B_T=11$ kHz, $D=0.83$. The figure of merit drops from $3D^2\overline{m^2}$ = 8.3·$\overline{m^2}$ to 2.1·$\overline{m^2}$ — narrowing the channel costs ≈ 6 dB of audio SNR above threshold, which is why narrowbanding was unpopular.

### Example 2 — Is an NBFM voice receiver at −120 dBm above threshold?
Receiver NF = 6 dB → $N_0=-168$ dBm/Hz. IF ≈ Carson = 16 kHz → noise $-168+42.0=-126.0$ dBm → **CNR = 6.0 dB: below threshold**. $\mathrm{SNR}_C$ (in W = 3 kHz) = $-120-(-168+34.8)=13.2$ dB; linear theory would promise $13.2+10\log_{10}(1.5\cdot1.67^2)=19.4$ dB, but the click region costs ≈ 10 dB (simulation at 7 dB CNR: 8.8 dB short). The familiar "12 dB SINAD at ≈ 0.2 µV (−121 dBm)" handheld sensitivity figure is exactly this near-threshold regime.

### Example 3 — Calibrating deviation with the first carrier null
Modulate with a 1.000 kHz tone and raise the audio level until the carrier line on a spectrum analyser (or SDR FFT) disappears: β = 2.405, so $\Delta f=2.405$ kHz. For ±5 kHz calibration use the second null (β = 5.520) at $f_m=5/5.520=906$ Hz. This works because $J_0(\beta)=0$ exactly at those β; no deviation meter needed [6].

### Example 4 — Broadcast FM SNR budget
Mono, $\Delta f=75$ kHz, W = 15 kHz → β = 5 → $\Gamma=15.7$ dB; 75 µs de-emphasis +13.2 dB; total ≈ 29 dB over a baseband system of the same power. Carson BW 180 kHz. The price is 12× the bandwidth of AM (15 kHz).

### Example 5 — APRS / packet over NBFM
Bell-202 AFSK: mark 1200 Hz, space 2200 Hz, 1200 baud, fed into the microphone input of a 2 m FM radio (144.39 MHz in North America, 144.800 MHz in Europe) [7]. The RF signal is FM of an FSK audio tone: occupied bandwidth ≈ Carson with $W\approx2.2$ kHz plus keying sidebands, ≈ 12–16 kHz for ≈ 3–3.5 kHz deviation. Sensitivity is limited by the FM threshold (~10 dB CNR in ~15 kHz: $-168+41.8+10\approx-116$ dBm with 6 dB NF) plus the audio-FSK detector — for 1200 b/s that is an *effective* Eb/N0 of ≈ $-116-(-168+30.8)\approx21$ dB, versus ≈ 6 dB for LoRa or ≈ 13.4 dB for direct NC-FSK at the same bit rate. Pre-/de-emphasis mismatch between radios alters the relative levels of the two tones ("twist"), a common cause of APRS decode failures. APRS trackers are still popular for rocket recovery because receivers and digipeaters are everywhere — but they require an amateur licence ([amateur licensing](../19-regulations-safety/amateur-radio-licensing.md)).

### Example 6 — PA and supply budget for an SSB voice transmitter
A 100 W PEP linear PA at 50 % efficiency at PEP (class AB) drawing from 13.8 V. Two-tone test: average 50 W, so at full two-tone drive the PA dissipates ≈ 50–60 W. Unprocessed speech (talk-only PEP/avg ≈ 13 dB) averages ≈ 5 W out, so most of the PA's dissipation is then its class-AB idle bias, and efficiency at the average power is far below 50 %. With a 12 dB RF clipper (+5 dB) the average rises to ≈ 13 W of RF. The power supply and heatsink must still handle the two-tone or digital-mode (FT8 = constant envelope: 100 % duty at 100 W for 13 s) case, which is far harsher than voice. Size for the data mode, not for speech.

### Example 7 — Necessary bandwidth of a 13 WPM Morse beacon and its SNR advantage
B = 0.8 × 13 = 10.4 Bd; $B_n$ = 5B = 52 Hz → 52H0A1A. Received in a 100 Hz filter vs a 2.7 kHz SSB filter, the noise is 14.3 dB lower, so at equal SNR in the detection bandwidth a 1 W CW beacon matches an SSB signal of ≈ 27 W *average* power, which is ≈ 500 W PEP of unprocessed speech at 13 dB PEP/average. This is rough: the ear's integration helps CW further, while speech needs a higher SNR than a single tone to be understood. This is why recovery beacons and fox-hunt transmitters on 2 m/70 cm often key a carrier or a tone rather than speak.

## Practical notes
- **AM transmitters**: modulating the final stage's supply (high-level) or a low-level stage followed by a linear amplifier. SSB requires a linear PA; FM tolerates class-C.
- **Measuring AM depth**: trapezoid or envelope on a scope; on a spectrum analyser, each sideband is $20\log_{10}(\mu/2)$ dBc (−6 dB at 100 %).
- **FM on an SDR**: complex samples → `np.angle(x[1:]*np.conj(x[:-1]))` → de-emphasis (single-pole IIR) → decimate. Quadrature demod gain = $f_s/(2\pi\Delta f)$ for unit output.
- **Frequency error in FM** only offsets the output DC (AC-coupled audio doesn't care) until it pushes the signal into the IF filter skirt. For a rocket at 433 MHz with ±1 kHz Doppler plus crystal error, keep the IF ≥ Carson + 2×max offset.
- **SSB carrier reinsertion**: offset error ≤ ≈ 20–50 Hz for natural voice; data over SSB (e.g. HF digital modes) needs much tighter tuning or AFC.
- **Setting up SSB drive:** with a two-tone test or a steady "ahhh", raise mic gain until ALC just begins to act on peaks; add processing until compression reads ≈ 10 dB; listen on a separate receiver or SDR waterfall for splatter more than 3 kHz from the dial.
- **Measuring PEP:** an average-reading wattmeter reads ≈ 4–15 % of PEP on unprocessed voice; use a peak-reading meter, a scope on a sampler, or an SDR's envelope display.
- **Limiters** must really limit: an FM receiver without enough IF gain before the limiter loses the capture advantage and AM noise suppression.
- **Circuits for these modulations** (varactor modulators, envelope-detector RC choice, FM discriminators): see [06 modulator and detector circuits](../06-rf-circuits/modulator-and-detector-circuits.md#level-3--choosing-a-circuit).

## Common mistakes & misconceptions
- **Confusing β, D and Δf.** β is defined for a single tone ($\Delta f/f_m$); D uses the highest message frequency ($\Delta f/W$). "Modulation index 5 kHz" mixes up deviation with index.
- **Carson's rule as a hard edge.** It is an estimate containing ≈ 98–99 % of power; spectral masks require checking the skirts.
- **"FM is always better than AM."** Only above threshold. Near the edge of coverage, FM falls off a cliff while AM degrades gracefully; SSB is more power-efficient than either for voice at long range.
- **"Wider deviation always improves FM."** It improves the above-threshold SNR but raises the threshold level (wider IF). For weak signals there is an optimum.
- **Forgetting de-emphasis** in an SDR FM receiver: the audio sounds harsh and noisy (13 dB more high-frequency noise at 75 µs).
- **Using envelope detection on DSB-SC or SSB** — the envelope is not the message.
- **"SSB speech has a PEP/average of 2.5:1."** That is the exam answer. Unprocessed speech measures ≈ 12–17 dB (≈ 15–50:1). Only heavy, well-designed processing gets near 2.5:1. Always state processing and averaging when quoting the ratio.
- **"LSB vs USB is chosen for propagation reasons."** It is convention: the sidebands are physically equivalent. The one technical rule is to keep the whole emission inside the band (LSB dial ≥ 3 kHz above the lower edge).
- **"More compression is always louder."** Past ≈ 10–15 dB, re-peaking after the filter limits the gain (+6 dB at 18 dB clip in the simulation) while distortion and splatter keep growing. Flat-topping in the PA is the worst case: unfiltered clipping.
- **"A compressor and a clipper do the same thing."** A slow or non-look-ahead compressor lets syllable onsets through at full gain and can even worsen PEP/average (−1.9 dB in the simulation). Clipping acts on every peak, but must be filtered.
- **"CW is efficient because Morse is a clever code."** The gain is bandwidth (and a constant envelope): ≈ 100 Hz instead of 2.7 kHz at equal power. Morse's variable-length code adds a little; FT8-style coding adds much more.
- **"AM + FM on one carrier doubles capacity for free."** It is a 2-D modulation like QAM, bounded by Shannon in the occupied bandwidth, and FM-to-AM and AM-to-PM conversion couple the two unless it is designed as one constellation.
- **Assuming capture protects you from interference** in all cases: when D/U approaches 0–1 dB the output flips between signals and is unusable.

## How to simulate / verify
- **`tools/verify/comms_analog_fm.py`** (≈ 3 s): FM line spectrum vs $J_n(\beta)$; $\sum J_n^2=1$; carrier-null β values; Carson power fractions; FM discriminator SNR vs $\tfrac32\beta^2$ and the threshold collapse; AM envelope and DSB-SC figures of merit; de-emphasis gains; capture-effect SIR; NBFM/broadcast Carson numbers. All PASS.
- **`tools/verify/s2_speech_crest.py`** (≈ 10 s): tone and two-tone sanity checks; SSB PEP/average of macOS text-to-speech speech (4 voices) and of a source–filter speech model; envelope clipping and compression (with and without look-ahead) at equal PEP. All PASS. Feed your own WAV file into `stats()` to measure your voice.
- **`tools/verify/s2_necessary_bandwidth.py`** (≈ 2 s): SM.1138 necessary-bandwidth formulas and designators, CW WPM → bandwidth, RR Appendix 1 notation. All PASS.
- **GNU Radio:** *Frequency Mod*, *NBFM Transmit/Receive*, *WBFM Receive* (includes de-emphasis), *AM Demod*, *Hilbert* (for SSB phasing method); *Channel Model* for noise; *QT GUI Frequency Sink* to see Bessel lines.
- **Bench:** SDR + signal generator: verify Carson bandwidth with the analyser's occupied-BW function; calibrate deviation by the Bessel-null method; measure 12 dB SINAD sensitivity and confirm it corresponds to CNR ≈ 6–10 dB in the IF bandwidth.

## Open questions / gaps
- Land-mobile (TIA-603 / ETSI EN 300 086) pre-emphasis characteristic and exact 12 dB SINAD test definition were not fetched; stated qualitatively.
- Capture-ratio figures (1–2 dB) come from receiver-marketing/forum sources; the simulation shows the effect but not a standard IHF capture-ratio measurement.
- Speech statistics come from text-to-speech and a synthetic model, not a calibrated recording of real talkers through real microphones. A measurement on a live voice (and on the team's actual SSB rig) would firm up the 12–15 dB figure.
- The LSB/USB history is forum-level; a primary historical source (1950s–60s exciter designs) was not read.
- The APRS effective-Eb/N0 comparison is an estimate using the ~10 dB threshold rule; a full AFSK-over-FM BER simulation would firm it up.

## Sources
1. S. Haykin, *Communication Systems*, 4th ed., Wiley, 2001 — ch. 2 (AM, DSB-SC, SSB, VSB, angle modulation, Bessel spectrum, Carson's rule, noise in CW modulation, figures of merit, FM threshold, pre-/de-emphasis). (textbook)
2. B. P. Lathi and Z. Ding, *Modern Digital and Analog Communication Systems*, 4th ed., Oxford University Press, 2009 — ch. 4–5 (amplitude and angle modulation), ch. 10 (noise in analog systems). (textbook)
3. J. R. Carson, "Notes on the theory of modulation," *Proc. IRE* 10(1):57–64, 1922 — bandwidth of FM, the result behind Carson's rule. (peer-reviewed, historical)
4. NTIA, Manual of Regulations and Procedures for Federal Radio Frequency Management, Annex J (Jan. 2021) — AM $B_n=2M$, SSB $B_n=M$, FM $B_n=2M+2KD$ with K = 1; examples 11K0F3E (M = 3 kHz, D = 2.5 kHz), 16K0F3E, 180KF3E. https://www.ntia.gov/files/ntia/publications/j_21_1.pdf (standard/regulatory)
5. S. O. Rice, "Noise in FM receivers," in *Time Series Analysis* (M. Rosenblatt, ed.), Wiley, 1963, pp. 395–422 — click model of the FM threshold. (peer-reviewed chapter)
6. Keysight/Agilent, "Spectrum Analysis Basics," Application Note 150 — FM measurements using Bessel nulls. (app note)
7. TAPR / APRS Working Group, *APRS Protocol Reference* v1.0.1, 2000 — APRS over AX.25 with 1200 baud Bell-202 AFSK (1200/2200 Hz). (standard / community specification)
8. E. H. Armstrong, "A method of reducing disturbances in radio signaling by a system of frequency modulation," *Proc. IRE* 24(5):689–740, 1936 — wideband FM noise advantage. (peer-reviewed, historical)
9. Circuit Design Inc., "FM capture effect," RF Design Guide, https://www.cdt21.com/design_guide/fm-capture-effect/ — qualitative capture behaviour in narrowband data radios. (app note)
10. ITU-R, *Recommendation SM.1138-3 (10/2019)*, Annex 1 — necessary-bandwidth formulas and sample designators (100HA1A, 2K70J3E, 6K00A3E, 16K0F3E, 180KF3E, 304HF1B). https://www.itu.int/dms_pubrec/itu-r/rec/sm/R-REC-SM.1138-3-201910-I!!PDF-E.pdf (standard)
11. D. L. Hershberger (W9GR), "Controlled envelope single sideband," *QEX*, Nov/Dec 2014 — filter overshoot after clipping, overshoot compensation, ≈ 3.8 dB peak reduction, +140 % vs +80 % (look-ahead ALC) average power at equal PEP. https://www.arrl.org/files/file/QEX_Next_Issue/2014/Nov-Dec_2014/Hershberger_QEX_11_14.pdf (technical journal)
12. US Patent 4,410,764, "Speech processor for processing analog signals" — typical 17 dB unprocessed SSB PAPR; compression ≈ 1 dB, 18 dB clipping ≈ 8 dB PAPR reduction (as quoted in its background). https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4410764 (patent — background claims, not peer-reviewed)
13. NCVEC, *Amateur Extra (E8A06/E8C05) and General (G4D01–G4D03, G4D08–G4D10) question pools* — the "≈ 2.5:1" speech PEP/average and 52 Hz (13 WPM) answers, used here as the questions people are taught. (exam pool)
