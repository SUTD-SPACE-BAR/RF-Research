---
title: Data converters — ADC and DAC fundamentals (quantisation, ENOB, SFDR, jitter, aliasing, architectures, DAC sinc, drivers, references)
domain: 05-analog-electronics
slug: data-converters-adc-dac
tags: [adc, dac, sampling, quantization-noise, snr, sinad, enob, sfdr, nsd, aperture-jitter, aliasing, nyquist-zones, anti-alias, flash, sar, pipeline, sigma-delta, time-interleaved, zero-order-hold, sinc-droop, processing-gain, oversampling, adc-driver, kickback, voltage-reference, adc-noise-figure, sdr, radar-if]
prerequisites:
  - ../00-math-foundations/fourier-series-and-transform.md
  - ../00-math-foundations/decibels-and-log-units.md
  - op-amps-real-limitations.md
related:
  - active-filters.md
  - low-noise-analog-design.md
  - power-supplies-for-rf-and-analog.md
  - analog-signal-conditioning.md
  - oscillators.md
  - ../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md
  - ../14-sdr-dsp/multirate-dsp-decimation-cic.md
  - ../14-sdr-dsp/sdr-hardware-survey.md
  - ../07-noise-linearity/phase-noise-and-jitter.md
  - ../07-noise-linearity/noise-figure-and-friis.md
  - ../18-components-parts/adcs-dacs-for-sdr.md
level: mixed
confidence: high
last_updated: 2026-10-03
---

# Data converters — ADC and DAC fundamentals (quantisation, ENOB, SFDR, jitter, aliasing, architectures, DAC sinc, drivers, references)

## Questions this page answers
- Where does SNR = 6.02N + 1.76 dB come from, and when is it wrong?
- What are SINAD, ENOB, SFDR, THD and noise spectral density (dBFS/Hz), and how do I read them off a datasheet?
- Why does clock jitter limit SNR at high input frequency, and how much jitter can I afford?
- Where will a 433 MHz or 915 MHz signal land if I sample it at 61.44 or 125 MSPS?
- How do flash, SAR, pipeline, sigma-delta and time-interleaved ADCs differ, and which suits sensors, SDR or radar?
- Why do DAC outputs droop and have images, and what is the sinc correction?
- How much does oversampling and decimation improve SNR?
- Why does my SAR ADC read wrong unless I put a capacitor at its input (charge kickback), and how do I size the RC?
- What is an ADC's noise figure, and how much gain do I need in front of it in an SDR?
- How does reference noise limit an ADC?

## TL;DR
- **Quantisation:** a uniform quantiser with step $q$ has error variance $q^2/12$ (for "busy" signals); a full-scale sine gives **SNR = 6.02N + 1.76 dB** — simulated to within 0.1 dB for N ≥ 8 (`tools/verify/analog_data_converters.py` §1).
- **ENOB** = (SINAD − 1.76)/6.02. Real 14-bit 125 MSPS ADC (TI ADC3664): SNR 77.5 dBFS at 5 MHz → 12.6 bits; 75.5 dBFS at 70 MHz; NSD −156.9 dBFS/Hz [1] (§2).
- **Jitter:** $SNR_{jitter} = -20\log_{10}(2\pi f_{in}\sigma_t)$ — independent of resolution and sample rate, set by *input* frequency (Monte Carlo agrees to 0.03 dB, §3). 1 ps at 100 MHz → 64 dB; 100 fs at 433 MHz → 71 dB. The ADC3664's SNR drop from 5 to 70 MHz implies ≈ 230 fs total jitter, matching its 250 fs aperture-jitter spec [1][2].
- **Aliasing:** any input at $f$ appears at $|f - k f_s|$ folded into 0…$f_s/2$. 433.92 MHz at 125 MSPS → 58.92 MHz (zone 7); at 61.44 MSPS → 3.84 MHz (§6). Filter *before* sampling — nothing afterwards can separate aliases.
- **Oversampling:** a Nyquist ADC gains $10\log_{10}(OSR)$ in a narrower band (3 dB/octave, 1 bit per ×4). A 125 kHz LoRa channel within 62.5 MHz gains 27 dB. **ΣΔ** noise shaping adds far more: linear theory 6.02N + 1.76 − 10log(π^{2L}/(2L+1)) + (2L+1)·10log(OSR); 1-bit simulations fall 4–9 dB short of it (§4).
- *The z-domain ΣΔ model (STF/NTF, in-band noise derivation, simulated 1st/2nd-order loops): [z-transform](../00-math-foundations/z-transform-and-discrete-time-systems.md).*
- **DAC:** zero-order hold multiplies the spectrum by sinc($f/f_s$): −3.92 dB at $f_s/2$, and images at $kf_s \pm f$ must be filtered (§5).
- **ADC NF:** $NF = P_{FS}(\text{dBm}) - SNR - 10\log(f_s/2) + 174$ ≈ 27 dB for the ADC3664 (8 dBm full scale into 200 Ω); a 1 dB LNA + 30 dB of gain brings the system to 2.3 dB (§8, §10).
- **SAR inputs** kick back charge; a "charge-bucket" capacitor ≫ $C_{sample}$ plus a small R (e.g. 1 nF: 2.9 % step with 30 pF sampling cap; R ≤ 85 Ω for 16-bit settling in 1 µs) and a driver that can recharge it are required (§7, §10). kT/C sets the minimum sampling capacitor: 8.5 pF for 16 bits at 5 V.
- **Reference noise** scales with the signal: 10 µV rms on a 2.5 V reference limits full-scale SNR to ≈ 99 dB (§9).

## Intuition (no math)
An ADC does two separate things: it takes *snapshots* at regular instants (sampling) and it *rounds* each snapshot to one of $2^N$ levels (quantising). Sampling loses nothing if the signal contains no frequencies above half the sample rate — but any frequency above that is indistinguishable from a lower one ("aliasing", like wagon wheels spinning backwards in films). Rounding adds a small error in every sample; for a busy signal that error behaves like white noise spread evenly from DC to $f_s/2$. Every extra bit halves the step and so improves SNR by 6 dB.

Timing errors matter as much as rounding: if the snapshot is taken a few femtoseconds early or late, a fast-changing signal has moved, so the sample is wrong by (slope × time error). Fast signals have steep slopes, which is why jitter limits high-frequency sampling regardless of how many bits the converter has.

If you sample much faster than you need and then digitally filter down to the band you want, you throw away most of the (spread-out) quantisation noise — oversampling. Sigma-delta converters go further: a feedback loop pushes the quantisation noise to high frequencies where the digital filter removes it, so a 1-bit quantiser can deliver 20+ bits in a narrow band.

A DAC is the reverse: it holds each value for one sample period (a staircase). The staircase has the right average but its steps create copies ("images") of the signal around multiples of the sample rate, and the holding itself slightly droops the high end of the band.

## The math

### Level 1 — definitions (IEEE Std 1241 terminology [3])

| Metric | Definition | Notes |
|---|---|---|
| Resolution N | bits; $q = V_{FS}/2^N$ | LSB size |
| SNR | signal power / noise power (excl. harmonics), dB | dBFS if referenced to full scale |
| THD | harmonic power / signal power | usually first 5–9 harmonics |
| SINAD | signal / (noise + distortion) | = SNDR |
| ENOB | $(SINAD - 1.76)/6.02$ | at a stated $f_{in}$, amplitude |
| SFDR | signal / largest spur, dBc or dBFS | matters for narrowband receivers |
| NSD | noise density, dBFS/Hz $= -SNR - 10\log(f_s/2)$ | compare ADCs of different $f_s$ |
| DNL / INL | step-width / transfer-curve errors, LSB | DNL < −1 LSB → missing codes |
| Aperture jitter $\sigma_t$ | rms sampling-instant uncertainty | fs–ps |

**Ideal quantisation SNR:** $SNR = 6.02N + 1.76$ dB (full-scale sine, Nyquist band).
**With oversampling** (noise in band B of a Nyquist converter): $SNR = 6.02N + 1.76 + 10\log_{10}\dfrac{f_s}{2B}$.
**Jitter limit:** $SNR_j = -20\log_{10}(2\pi f_{in}\sigma_t)$. Contributions add as powers: $SNR_{tot} = -10\log_{10}(10^{-SNR_q/10} + 10^{-SNR_j/10} + 10^{-SNR_{th}/10})$.
**Alias location:** $f_a = |f - kf_s|$ with k chosen so $0 \le f_a \le f_s/2$; Nyquist zone = $\lfloor f/(f_s/2)\rfloor + 1$ (even zones spectrally inverted).
**DAC ZOH:** $|H(f)| = |\sin(\pi f/f_s)/(\pi f/f_s)|$.

### Level 2 — derivations

**6.02N + 1.76 dB.** Assume the quantisation error e is uniformly distributed on $[-q/2, q/2]$ and uncorrelated with the signal (true for signals that cross many codes, with non-repeating relationship to $f_s$). Its variance is $\frac1q\int_{-q/2}^{q/2}e^2de = q^2/12$. A full-scale sine has peak $2^Nq/2$ and power $(2^Nq)^2/8$. Hence
$$SNR = 10\log_{10}\frac{(2^Nq)^2/8}{q^2/12} = 10\log_{10}\left(\tfrac32\,2^{2N}\right) = 6.02N + 1.76\ \text{dB}.$$
Simulation (§1): 49.79 dB for N = 8 (theory 49.92), 98.10 dB for N = 16 (98.08); for N = 4 the uniform-error assumption weakens (25.3 vs 25.8 dB). The formula fails for small, slow or DC signals (error becomes deterministic and signal-correlated → harmonics instead of noise); **dither** (a small added noise) restores the noise-like behaviour. The noise is spread over 0…$f_s/2$, so its density is $q^2/(12\cdot f_s/2)$ — the origin of NSD and of processing gain.

**Jitter limit (derivation).** For $v = A\sin\omega t$, a timing error $\delta t$ gives $\delta v \approx A\omega\cos(\omega t)\,\delta t$. Averaging over the sine's phase ($\overline{\cos^2} = 1/2$) and over a jitter of rms $\sigma_t$: $\overline{\delta v^2} = A^2\omega^2\sigma_t^2/2$, while the signal power is $A^2/2$, so
$$SNR_j = \frac{1}{(\omega\sigma_t)^2}\ \Rightarrow\ -20\log_{10}(2\pi f_{in}\sigma_t)$$
[2]. A Monte Carlo with random sampling instants reproduces it (§3). Consequences: (i) it depends on $f_{in}$, not $f_s$ — undersampling a 433 MHz signal needs the jitter of a 433 MHz ADC; (ii) the total $\sigma_t$ is the rss of the ADC's aperture jitter and the clock's jitter *integrated over the ADC's clock-input bandwidth* (→ [phase noise & jitter](../07-noise-linearity/phase-noise-and-jitter.md) to convert phase noise in dBc/Hz to fs); (iii) budget: for 75 dB at 70 MHz you need ≤ 404 fs total (§10).

**Oversampling / processing gain.** If only a band B of the $f_s/2$ Nyquist band is kept (digital filtering), only the fraction $2B/f_s$ of white quantisation (and thermal) noise remains: $+10\log_{10}(OSR)$ with $OSR = f_s/2B$. Each ×4 is one bit. This is why an SDR's ADC SNR "per channel" is much better than its Nyquist SNR: a 125 kHz LoRa channel within 62.5 MHz gains 27 dB (§8). It works only for noise-like errors — spurs (SFDR) do not average down.

**Sigma-delta noise shaping.** An L-th order loop filter gives quantisation noise a transfer function $(1-z^{-1})^L$, whose power grows as $(2\sin\pi f/f_s)^{2L}$. Integrating over the in-band fraction gives the linear-model result
$$SQNR = 6.02N + 1.76 - 10\log_{10}\frac{\pi^{2L}}{2L+1} + (2L+1)\,10\log_{10}OSR$$
— 9 dB/octave of OSR for L = 1, 15 dB/octave for L = 2 [4]. 1-bit simulations (§4, −6 dBFS input): L = 1, OSR = 64: 46.1 dB vs 50.8 predicted; L = 2, OSR = 64: 70.3 vs 79.2. The linear model ignores the 1-bit quantiser's signal-dependent gain and tonal behaviour, so treat it as an upper bound; practical ΣΔ ADCs use multi-bit quantisers and higher order with careful stability design. The digital decimation filter adds latency (tens of output samples) — relevant for control loops.

**DAC zero-order hold and images.** A DAC output held for $T_s$ is the ideal impulse train convolved with a rectangle of width $T_s$: multiply the spectrum by sinc($f/f_s$). In-band droop: −0.14 dB at 0.1 $f_s$, −0.91 dB at 0.25 $f_s$, −3.92 dB at 0.5 $f_s$; the first image at $f_s - f$ is only 19 dB below the signal for $f = 0.1f_s$, and equal to it at $f_s/2$ (§5). Remedies: interpolate to a higher DAC rate (images move up, sinc flattens), apply inverse-sinc digital pre-emphasis, and use an analog reconstruction filter. RF DACs deliberately use images in higher Nyquist zones ("mix-mode").

**Aliasing and bandpass sampling.** Sampling multiplies by an impulse train at $f_s$, replicating the spectrum at every $kf_s$. A signal in zone m (between $(m-1)f_s/2$ and $mf_s/2$) lands in zone 1, inverted for even m. Deliberate undersampling of an IF/RF band requires (i) a band-pass (zone) filter that removes everything outside the chosen zone, (ii) ADC analog input bandwidth covering the RF (ADC3664: 1.4 GHz at −3 dB [1]), and (iii) jitter adequate for the *RF* frequency. See [sampling & bandpass sampling](../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md).

**kT/C and the sampling capacitor.** The sampled thermal noise on a capacitor is $kT/C$ (derived in [low-noise design](low-noise-analog-design.md)). Setting it equal to quantisation noise $q^2/12$ gives $C = 12kT/q^2$: 0.08 pF for 12 bits at 3.3 V, 8.5 pF for 16 bits at 5 V, 137 pF for 18 bits, and an impossible 0.56 µF for 24 bits (§7) — which is why > 18-bit converters are ΣΔ (oversampling averages kT/C noise too) and why high-resolution SAR ADCs have tens of pF of input capacitance to drive.

**SAR input kickback and settling.** At the start of acquisition, the discharged (or previous-sample) sampling capacitor $C_s$ is connected to the input; charge sharing with an external capacitor $C_{ext}$ produces an instantaneous step of $C_s/(C_s+C_{ext})$ of the voltage difference (2.9 % for 30 pF into 1 nF, §7). The driver then must restore the voltage through the series R to within ½ LSB before the acquisition window closes: $t_{acq} \ge \tau\ln 2^{N+1}$ = 11.8 τ for 16 bits — so with $t_{acq}$ = 1 µs and $C_{ext}$ = 1 nF, R ≤ 85 Ω (§10). The R also isolates the op-amp from the capacitive load (→ [feedback & stability](feedback-and-stability.md)); vendors give recommended R–C values and driver amplifiers (→ [op-amps](op-amps-real-limitations.md) FDA section).

**ADC noise figure.** Treat the ADC as a two-port with input power $P_{FS}$ (full scale into its termination) and noise $P_{FS} - SNR$ spread over $f_s/2$: noise density $P_{FS} - SNR - 10\log(f_s/2)$ dBm/Hz; compared with −174 dBm/Hz,
$$NF_{ADC} = P_{FS} - SNR - 10\log_{10}(f_s/2) + 174\ \text{dB}.$$
ADC3664-like numbers (3.2 V p-p differential into 200 Ω = 8.06 dBm): NF ≈ 26.6 dB at 5 MHz, 28.6 dB at 70 MHz (§8). ADCs are *noisy* amplifiers with huge dynamic range; the Friis cascade (→ [noise figure & Friis](../07-noise-linearity/noise-figure-and-friis.md)) says you need enough gain ahead of them: 1 dB NF LNA + 20 dB gain → 7.7 dB system NF; +30 dB → 2.3 dB; +40 dB → 1.2 dB (§10) — traded against the loss of headroom for strong signals (→ [dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)).

**Reference noise.** An ADC measures $V_{in}/V_{ref}$; reference noise $v_{n,ref}$ therefore produces an error proportional to the input. A conservative full-scale bound: $SNR_{ref} \approx 20\log_{10}[V_{FS,rms}/v_{n,ref}]$, i.e. ≈ 99 dB for 10 µV rms on 2.5 V (§9) — adequate for 16 bits, marginal for 18–20 bits. Reference *impedance* matters too: SAR ADCs draw charge from the reference each bit trial, so it needs a low-ESR bypass (often 10 µF) and a buffer (→ [power supplies](power-supplies-for-rf-and-analog.md)).

### Level 3 — architectures and their limits

| Architecture | Principle | Resolution / speed (typical) | Strengths | Weaknesses |
|---|---|---|---|---|
| Flash | $2^N-1$ comparators in parallel | 4–8 bit, 1–10+ GS/s | fastest, 1-cycle latency | power/area double per bit; comparator offsets |
| SAR | binary search with a capacitive DAC, N cycles | 8–20 bit, 10 kS/s–10s MS/s | low power, no latency, multiplexer-friendly | input kickback, driver needs; speed/resolution trade |
| Pipeline | cascade of low-res stages with residue amplifiers | 10–16 bit, 10 MS/s–1+ GS/s | high speed with good SNR | latency (several clocks), power, needs clean clock |
| ΣΔ | oversampling + noise shaping + decimation | 16–32 bit, Hz–10s MHz BW | resolution, easy anti-alias, linearity | latency, bandwidth limited, idle tones |
| Time-interleaved | M sub-ADCs in rotation | multiplies speed by M | GS/s with pipeline/SAR cores | offset/gain/timing mismatch spurs at $kf_s/M \pm f_{in}$ |
| Integrating (dual-slope) | charge/discharge timing | 12–22 bit, < 100 S/s | excellent linearity, mains rejection | very slow |

Other practical points:
- **Where each lives:** sensor/DC measurement (ΣΔ like ADS1115-class, precision SAR); MCU internal ADCs (SAR; often 12-bit with ENOB of roughly 9–11 bits and nonlinearity — calibrate; check the specific MCU's datasheet); SDR and radar IF (pipeline/SAR at 10–250 MS/s, 12–16 bit; RF-sampling GS/s pipelines and interleaved converters for direct sampling); audio (ΣΔ).
- **Interleaving spurs:** offset mismatch → tone at $f_s/M$; gain and timing mismatch → images at $kf_s/M \pm f_{in}$; timing mismatch behaves like deterministic jitter, growing with $f_{in}$.
- **Metastability / sparkle codes** in fast flash and pipeline converters; **DNL** errors create spurs for small signals (dither helps).
- **Input structure:** unbuffered switched-capacitor inputs (need a driver and settling), buffered inputs (easier, more noise/power); differential inputs almost always for > 12 bits and high speed.
- **Radar specifics:** FMCW radars sample the beat (IF) signal: anti-alias filter + high-pass (range-dependent gain compensation, since IF amplitude falls with range) and simultaneous sampling of I/Q or multiple channels (MIMO) → multi-channel SAR/ΣΔ ADCs with matched delay (→ [FMCW radar](../11-radar/fmcw-radar.md)).

## Design equations & rules of thumb

| Quantity | Equation | Typical |
|---|---|---|
| Quantisation SNR | $6.02N + 1.76$ dB | 74 dB (12-bit), 98 dB (16-bit) |
| ENOB | $(SINAD-1.76)/6.02$ | 1–3 bits below N |
| NSD | $-SNR - 10\log(f_s/2)$ dBFS/Hz | −157 dBFS/Hz (ADC3664) |
| Processing gain | $10\log(f_s/2B)$ (real ADC; complex IQ at $f_s$: $10\log(f_s/B)$) | 1 bit per ×4 |
| Jitter SNR | $-20\log(2\pi f_{in}\sigma_t)$ | 100 fs → 71 dB at 433 MHz |
| Alias | $|f - kf_s|$ | — |
| ZOH droop | sinc($f/f_s$) | −3.92 dB at $f_s/2$ |
| kT/C capacitor | $C \ge 12kT/q^2$ | 8.5 pF (16 bit, 5 V) |
| Settling to ½ LSB | $(N+1)\ln 2\cdot\tau$ | 11.8 τ (16 bit) |
| Charge-bucket step | $C_s/(C_s+C_{ext})$ | $C_{ext}$ ≥ 20–30 × $C_s$ |
| ADC NF | $P_{FS} - SNR - 10\log(f_s/2) + 174$ | 25–35 dB |
| AAF attenuation | ≥ 6.02N + 1.76 at $f_s - f_{pass}$ (or interference-based) | → [active filters](active-filters.md) |
| ΣΔ SQNR (linear model) | $6.02N+1.76-10\log\frac{\pi^{2L}}{2L+1}+(2L+1)10\log OSR$ | upper bound for 1-bit |

## Worked examples

### 1. Reading an ADC datasheet (TI ADC3664, 14-bit, 125 MSPS) [1]
- SNR 77.5 dBFS at 5 MHz → ENOB (SNR only) 12.6 bits; ideal 14-bit would be 86.0 dB. Its noise is thermal/aperture-limited, not quantisation-limited.
- NSD −156.9 dBFS/Hz (at −20 dBFS input) ↔ SNR 78.9 dBFS at −20 dBFS: consistent with $-SNR - 10\log(62.5\text{ MHz})$ (§2).
- At 70 MHz, SNR 75.5 dBFS: the 2 dB loss implies ≈ 230 fs total jitter ≈ the 250 fs aperture spec — the datasheet was measured with a very clean clock; your clock adds to it.
- In a 125 kHz channel: −156.9 + 51.0 = −105.9 dBFS noise — the ADC can see a signal 100 dB below a full-scale blocker, *if* the blocker's spurs (SFDR 84–92 dBFS) do not land in the channel.

### 2. Direct sampling of 433 MHz (undersampling) at 125 MSPS
433.92 MHz lies in zone 7 (375–437.5 MHz) and aliases to 58.92 MHz (§6) — only 3.6 MHz from the zone edge, so anything just above 437.5 MHz folds right next to it and the zone filter would need an impossibly steep skirt. Choose $f_s$ to centre the band in a zone instead: $f_s = 2f/(m-\tfrac12)$ → 115.71 MSPS puts 433.92 MHz in the middle of zone 8 (405–463 MHz), aliasing to $f_s/4$ = 28.9 MHz (spectrally inverted) (§11). Then requirements: a band-pass (e.g. SAW) filter that rejects zones 7 and 9, jitter for 71 dB SNR at 433 MHz ≤ 100 fs, and the ADC's input bandwidth (1.4 GHz) — plus the ADC's SNR is lower at 433 MHz than at 5 MHz. Gain: ~30 dB of LNA gain for a ~2–3 dB system NF (§10). This is the architecture of many "direct-sampling" SDRs.

### 3. Gain before an SDR ADC
ADC NF ≈ 27 dB. Add a 1 dB-NF LNA with 30 dB gain → 2.3 dB system NF (§10). More gain lowers NF towards 1 dB but raises the input-referred full scale problem: a 30 dB-gain front end puts the ADC's 8 dBm full scale at −22 dBm at the antenna — a strong nearby transmitter (e.g. the team's own 2 W 433 MHz telemetry at the launch site) will clip it. Use AGC or a filter plan (→ [receiver architectures](../06-rf-circuits/receiver-architectures.md)).

### 4. Driving a 16-bit SAR ADC at 1 MSPS
Sampling capacitor 30 pF (typical order), charge bucket 1 nF C0G (2.9 % kickback), acquisition 1 µs → R ≤ 85 Ω (§10); driver: an FDA or fast precision op-amp that can recover the 2.9 % step and remain stable into 1 nF through the R (→ [op-amps](op-amps-real-limitations.md), [feedback & stability](feedback-and-stability.md)). The anti-alias filter proper sits before the driver.

### 5. Flight-computer MCU ADC channels
Battery voltage, pyro continuity current, thermistors: bandwidth of Hz–kHz, SAR ADC in the MCU. An RC at the pin (e.g. 1 kΩ + 100 nF) does both anti-aliasing and charge-bucket duty; average 16 samples for +6 dB (2 bits of processing gain for white noise, §4). Calibrate offset/gain against a reference; do not trust the ADC's reference if it is the supply rail (→ [signal conditioning](analog-signal-conditioning.md)).

## Practical notes
- **Clock:** use a low-jitter clock (crystal oscillator + clean buffer); route it as a controlled-impedance differential pair away from the analog input; its phase noise in the ADC's clock-input bandwidth is what matters.
- **Analog input:** for high-speed ADCs use the vendor's input network (balun/FDA, termination, anti-kickback RC); keep it symmetric.
- **Grounding & decoupling:** one solid ground plane; separate AVDD/DVDD supplies with filtering; place reference and supply capacitors at the pins (→ [mixed-signal layout](../13-pcb-rf-layout-emc/mixed-signal-layout.md)).
- **Digital outputs** (LVDS/CMOS) couple back into the analog input if routed near it; CMOS outputs driving long traces create current spikes — use series resistors or LVDS.
- **Testing:** coherent sampling (integer number of input cycles, prime) or windowed FFT; compute SNR/SINAD/SFDR per IEEE 1241 [3]; note FFT processing gain when reading noise floors from an FFT ($10\log(N_{FFT}/2)$ below the per-bin level).

## Common mistakes & misconceptions
- **Reading the FFT noise floor as the ADC noise floor.** The per-bin floor is $10\log(N/2)$ below the total noise (FFT processing gain, real samples; $10\log N$ for an $N$-point complex FFT of IQ data).
- **Assuming 16-bit means 96 dB.** Check SNR/ENOB at your input frequency and amplitude; MCU "12-bit" ADCs often deliver 9–11 effective bits.
- **Ignoring jitter when undersampling** — it scales with the RF frequency, not $f_s$.
- **Anti-aliasing after the gain stage that clipped the blocker** — nonlinearity creates in-band products that no filter can remove.
- **Driving a SAR ADC directly from an op-amp without the RC**, or with an RC too large to settle.
- **Using an X7R capacitor as the charge bucket or reference bypass without checking DC-bias derating** (value can drop by half).
- **Believing dither "adds noise so it's bad"** — small dither linearises the quantiser and removes signal-correlated spurs.
- **Trusting the ΣΔ linear-model SQNR for 1-bit modulators** — reality is several dB worse (§4).

## How to simulate / verify
- **Python:** `tools/verify/analog_data_converters.py` — quantised-sine SNR vs 6.02N + 1.76; ENOB/NSD of the ADC3664; jitter Monte Carlo and implied-jitter check; oversampling gains; 1st/2nd-order 1-bit ΣΔ simulation vs linear model; ZOH droop/images; alias calculator; kT/C, settling, kickback; ADC NF and Friis gain planning; reference-noise bound.
- **Behavioural simulation:** model the ADC as sample → add jitter → quantise → add noise at the NSD; feed recorded or synthetic RF (e.g. LoRa chirps from the 15 domain) through your filter chain in Python/GNU Radio to check alias and blocker scenarios (→ [GNU Radio](../14-sdr-dsp/gnu-radio-and-software-stack.md)).
- **SPICE:** simulate the driver + RC + a switched-capacitor model of the ADC input (a switch that connects a pre-charged $C_s$ at each sample) to check settling; vendors publish such models.
- **Bench:** clean signal generator + band-pass filter (to remove generator harmonics) → ADC → FFT; measure SNR vs input frequency to see the jitter slope (−20 dB/decade of $f_{in}$ once jitter dominates).

## Open questions / gaps
- The Kester *Data Conversion Handbook* / ADI MT-001, MT-003, MT-007 could not be retrieved (analog.com timeouts); derivations here are own and cross-checked with TI SLYT075, IEEE 1241 definitions and simulation.
- MCU ADC ENOB figures (ESP32-S3, i.MX RT1062 on Teensy 4.1) not yet sourced — the "9–11 bits" is a generic caution, not a measured value; measure on the actual boards.
- Time-interleaving mismatch spur formulas are stated, not derived.
- RF-sampling ADC and RF-DAC specifics (GS/s, zones, DDC/DUC) belong with [14 SDR hardware](../14-sdr-dsp/sdr-hardware-survey.md) and [18 ADCs/DACs](../18-components-parts/adcs-dacs-for-sdr.md).

## Sources
1. Texas Instruments, *ADC3664 14-bit, 125-MSPS, low-noise, low-power dual-channel ADC* datasheet SBAS888B, 2020. https://www.ti.com/lit/ds/symlink/adc3664.pdf — SNR 77.5/75.5 dBFS (5/70 MHz), NSD −156.9 dBFS/Hz, SFDR, 3.2 V p-p full scale, 250 fs aperture jitter, 1.4 GHz input bandwidth, decimation/NCO. (datasheet)
2. E. Bartolome, V. Mishra, G. Dutta, D. Smith, "Clocking high-speed data converters," TI *Analog Applications Journal* 1Q 2005, SLYT075. https://www.ti.com/lit/pdf/slyt075 — derivation of the jitter-limited SNR from signal slope and sampling uncertainty. (app note)
3. IEEE Std 1241-2010, *IEEE Standard for Terminology and Test Methods for Analog-to-Digital Converters*. (standard)
4. R. Schreier, G. C. Temes, *Understanding Delta-Sigma Data Converters*, Wiley-IEEE 2005 (2nd ed. with S. Pavan, 2017) — noise shaping, SQNR vs order and OSR, 1-bit quantiser limitations. (textbook)
5. W. Kester (ed.), *The Data Conversion Handbook*, Analog Devices/Newnes 2005 — ch. 2 (sampling, quantisation, ENOB, jitter), ch. 3 (architectures), ch. 6 (drivers). Free from ADI (not retrievable this session). (textbook)
6. B. Razavi, *Principles of Data Conversion System Design*, IEEE Press 1995 — flash, pipeline, SAR, interleaving errors. (textbook)
7. P. Horowitz, W. Hill, *The Art of Electronics*, 3rd ed., Cambridge 2015 — ch. 13 (digital meets analog: ADC/DAC types, dither, anti-aliasing). (textbook)
