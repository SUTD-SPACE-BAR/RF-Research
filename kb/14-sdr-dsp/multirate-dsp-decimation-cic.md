---
title: Multirate DSP — decimation, interpolation, polyphase and half-band filters, CIC filters, channelisers
domain: 14-sdr-dsp
slug: multirate-dsp-decimation-cic
tags: [multirate, decimation, interpolation, resampling, polyphase, noble-identities, half-band, cic, hogenauer, droop-compensation, bit-growth, multistage, channeliser, polyphase-filter-bank, fs-over-4, farrow, lora, rtl-sdr]
prerequisites: [sampling-aliasing-bandpass-sampling.md, digital-filters-fir-iir.md, iq-complex-baseband.md]
related: [nco-ddc-duc.md, fpga-for-sdr.md, fft-spectral-analysis-windows.md, software-demodulation.md, gnu-radio-and-software-stack.md, sdr-hardware-survey.md, ../10-comms-modulation/synchronization-carrier-timing.md, ../10-comms-modulation/pulse-shaping-isi.md, ../15-lora-ism-radios/lora-phy-css-math.md, ../15-lora-ism-radios/ground-station-design.md, ../12-phased-arrays/beamforming-architectures.md]
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Multirate DSP — decimation, interpolation, polyphase and half-band filters, CIC filters, channelisers

## Questions this page answers
- How do I get from my SDR's 2.4 MS/s down to the ~500 kS/s a LoRa decoder wants, cheaply and without aliasing?
- What is decimation vs downsampling, and interpolation vs upsampling?
- What is a polyphase filter and why does it save a factor of M?
- Why are half-band filters everywhere (AD936x, FPGAs), and what makes them cheap?
- How does a CIC filter work, why does it need no multipliers, how many bits does it need, and what is "droop"?
- How do I compensate CIC droop?
- How do I resample by a non-integer ratio like 5/24?
- How should I split a big decimation factor into stages?
- How can one FFT receive 8 or 64 channels at once (polyphase filter bank channeliser)?
- What is the $f_s/4$ trick for turning real samples into complex ones?

## TL;DR
- **Decimate by M** = low-pass filter, then keep every M-th sample. **Interpolate by L** = insert L−1 zeros (creating L−1 images), then low-pass with gain L. Resample by $L/M$ = both, with one filter.
- The decimation filter only has to stop what would **alias into the band you keep**: for a final pass-band $f_p$ at output rate $f_s/M$, the stop-band starts at $f_s/M - f_p$, not at $f_s/2M$. The transition in between is "don't care" (a later filter removes it). This single observation makes early stages very short (23 taps for 2.0 MS/s → 500 kS/s in the LoRa example).
- **Polyphase** implementation (noble identities) runs the filter at the *output* rate: $N$ MACs per output instead of $N\cdot M$ (script: 63 vs 252). Equivalent output to 7×10⁻¹⁶.
- **Half-band** filters (band edges symmetric about $f_s/4$) have every second tap exactly zero and a centre tap of ½ — about ¼ of the multiplies of a general FIR of the same length; they are the standard ÷2 stage.
- **CIC** (Hogenauer): N integrators at the input rate, ÷R, N combs at the output rate — no multipliers. $|H(f)| = \left|\frac{\sin(\pi fRM)}{\sin(\pi f)}\right|^N$, DC gain $(RM)^N$, register width $B_{in} + N\log_2(RM)$ bits, and two's-complement **wrap-around in the integrators is harmless** (bit-exact check in the script). Droop at $f_{s,out}/8$ with N = 4: 0.90 dB; rejection of the first alias band: 68.5 dB. A 31-tap compensator flattens 2.31 dB of droop to 0.05 dB.
- **LoRa on an RTL-SDR**: run at 2.0 MS/s tuned 400 kHz low; NCO shift; 23-tap polyphase ÷4 → 500 kS/s; 83-tap channel filter → in-channel aliases of +20 dB interferers end up 80 dB down, at 53 M MAC/s per rail — 17× cheaper than one 374-tap filter at 2.4 MS/s. At 2.4 MS/s use a 5/24 rational resampler instead.
- A **polyphase FFT channeliser** splits a band into M channels for the cost of one prototype filter plus one M-point FFT — script: 8 channels, output equal to brute-force mix-filter-decimate to 3×10⁻¹¹, adjacent-channel leakage ≤ −90 dB.

Verified by `tools/verify/dsp_multirate_cic.py` (all PASS).

## Intuition (no math)
An SDR samples far faster than most signals need — 2.4 MS/s to receive a 125 kHz LoRa channel, 61.44 MS/s to receive a 1 MHz telemetry band. Carrying all those samples costs CPU, USB bandwidth and disk. Decimation throws most of them away, but you can only throw away samples if you first remove everything that would "fold" into your band when the rate drops ([sampling](sampling-aliasing-bandpass-sampling.md)): once the rate is lower, the spectrum wraps around more tightly and things that were far away land on top of you.

Filtering and then discarding 3 out of every 4 outputs is wasteful — why compute outputs you throw away? Polyphase filtering rearranges the arithmetic so you only compute the outputs you keep. Doing it in several stages is cheaper still, because the first stages can be sloppy (their job is only to protect what's left) and the expensive sharp filter runs last, at the lowest rate.

A CIC filter is the extreme case: a running sum over the last R samples (a moving average), repeated N times, computed with nothing but adders. It's crude — its pass-band sags (droop) — but it is almost free, so hardware uses it for the first huge decimation (÷8 to ÷1000s) and fixes the sag with a small FIR afterwards.

## The math

### Level 1 — the operations and rates
- **Downsampling** (compressor) $y[m] = x[mM]$; **decimation** = anti-alias filter + downsampling. Output rate $f_s/M$.
- **Upsampling** (expander) $u[n] = x[n/L]$ if $L\mid n$, else 0; **interpolation** = upsampling + anti-imaging filter with pass-band gain $L$. Output rate $Lf_s$.
- **Rational resampling** by $L/M$: upsample by L, filter once (cut-off at the lower of the two Nyquist limits), downsample by M.
- For **complex** data at rate $f_s$ the usable band is $\pm f_s/2$; after ÷M it is $\pm f_s/2M$.
- **Cost** is measured in multiply–accumulates per second (MAC/s) = taps per output × output rate (for polyphase structures).

### Level 2 — spectra, polyphase, half-band, CIC
**What downsampling does to the spectrum.** With $\omega$ in rad/sample,
$$Y(e^{j\omega}) = \frac1M\sum_{k=0}^{M-1}X\!\left(e^{j(\omega-2\pi k)/M}\right):$$
the spectrum is stretched by M and M shifted copies are added — every band $[2\pi k/M \pm \pi/M]$ of the input lands on top of baseband [1 §4.6], [3 ch. 2]. Script §1: at 1 MS/s → 250 kS/s, a 300 kHz tone appears at 50 kHz with full amplitude if unfiltered, and 78 dB down behind a 63-tap filter.

**What upsampling does.** $U(e^{j\omega}) = X(e^{j\omega L})$: the spectrum is compressed by L, and L−1 **images** appear at multiples of the input rate (script §3: three equal images at −12 dB relative to the zero-stuffed signal's scale); the interpolation filter with gain L removes them (worst image −99 dB, level restored to 0.00 dB).

**Only the aliasing bands matter.** Say the final wanted band is $|f|\le f_p$ at output rate $f_{so} = f_s/M$. After downsampling, input frequencies $f$ land at $f - kf_{so}$. Only inputs within $f_p$ of a multiple of $f_{so}$ can land on the wanted band. So the decimator needs stop-bands only around $kf_{so}\pm f_p$ ($k\ne0$) — for a single-stage low-pass, a stop-band from $f_{so} - f_p$ upwards. Content between $f_p$ and $f_{so} - f_p$ aliases into the *transition* region of the output, where the next (channel) filter removes it [2 ch. 7], [3]. The transition band ratio $\Delta f/f_s$ is therefore large and the filter short (harris' length rule, [filters](digital-filters-fir-iir.md)).

**Noble identities and polyphase decomposition.** (i) Filtering with $H(z^M)$ then downsampling by M equals downsampling then filtering with $H(z)$; (ii) upsampling by L then $H(z^L)$ equals $H(z)$ then upsampling [1 §4.7], [4]. Split any FIR into M **polyphase components** $E_k(z) = \sum_p h[pM+k]z^{-p}$, so $H(z) = \sum_{k=0}^{M-1}z^{-k}E_k(z^M)$. By identity (i) each $E_k$ runs at the low rate on the sub-sequence $x_k[m] = x[mM-k]$ (a commutator deals samples round-robin to the branches), and the branch outputs are summed. Total work: $N$ MACs per *output* sample — M times less than filtering at the input rate and discarding. Script §2 checks equality to 7×10⁻¹⁶. Interpolators use the transposed structure (each branch produces one of the L output phases) — same saving.

**Half-band filters.** Design a symmetric low-pass whose pass-band edge $f_p$ and stop-band edge $f_s/2 - f_p$ are symmetric about $f_s/4$, with equal ripples. Its zero-phase amplitude obeys $A(f) + A(f_s/2 - f) = 1$, which forces $h[c] = 1/2$ at the centre and $h[c\pm2k] = 0$ for all $k\ne0$ [3 ch. 8], [4]. Script §4: a 31-tap equiripple design has taps at even offsets below 5×10⁻⁶, centre 0.50000, and $A(f)+A(0.5-f) = 1$ to 10⁻⁵. Only 17 of 31 taps are non-zero, and with symmetry plus the trivial centre tap about 8–9 multiplies per output are needed, at the *output* rate. The price: the transition is centred on $f_s/4$, so after ÷2 the region near the new Nyquist frequency contains aliases — keep the wanted band below $f_p$. Cascades of half-bands are the standard ÷2ⁿ chain (AD936x HB1/HB2/HB3 [7]; GNU Radio and liquid-dsp half-band decimators).

**CIC filters (Hogenauer 1981 [5]).** A moving sum over $D = RM$ samples has
$$H_1(z) = \sum_{k=0}^{RM-1}z^{-k} = \frac{1 - z^{-RM}}{1 - z^{-1}},$$
an integrator $1/(1-z^{-1})$ followed by a comb $1-z^{-RM}$. Cascade N of them: $H(z) = \left(\frac{1-z^{-RM}}{1-z^{-1}}\right)^N$. Put all N integrators at the input rate, decimate by R, and use the noble identity to move the combs after the decimator, where $z^{-RM}$ becomes $z^{-M}$ (M = "differential delay", usually 1 or 2). The result needs **no multipliers and no coefficient storage** — only $2N$ adders and $NM$ registers at the low rate. Its response at input-rate frequency $f$ (cycles/sample):
$$|H(f)| = \left|\frac{\sin(\pi fRM)}{\sin(\pi f)}\right|^N,\qquad H(0) = (RM)^N.$$
In terms of the output-rate frequency $\nu = fR$ and for large R, $|H|/H(0)\approx|\mathrm{sinc}(M\nu)|^N$, with nulls at every multiple of $f_{so}/M$ — exactly where the aliasing bands are centred, which is why a crude moving average works as an anti-alias filter for a narrow pass-band.

*Register width.* The gain $(RM)^N$ means the output needs $B_{out} = B_{in} + \lceil N\log_2(RM)\rceil$ bits. The integrators on their own grow without bound for a DC input — yet with two's-complement arithmetic that simply *wraps* modulo $2^{B_{out}}$, the final comb outputs are still exactly right, because the whole filter is a finite-impulse-response map whose true output fits in $B_{out}$ bits and modular arithmetic is exact for sums and differences [5]. Script §5: 12-bit input, R = 8, N = 4 → 24-bit registers; the bit-exact wrapped implementation equals the exact convolution; with 22-bit registers it fails. Hogenauer also shows how many LSBs each later stage can discard ("pruning") while keeping the output error bounded.

*Droop and alias rejection* (script §6, N = 4, M = 1):

| Pass-band edge $\nu_p$ (× $f_{so}$) | Droop at edge | Rejection of first alias band ($1-\nu_p$) |
|---|---|---|
| 1/16 (0.0625) | 0.22 dB | 94.3 dB |
| 1/8 (0.125) | 0.90 dB | 68.5 dB |
| 1/4 (0.25) | 3.65 dB | 41.8 dB |

Rejection grows by ≈ 23.6 dB per extra stage at $\nu_p = 1/16$ (N = 3/4/5: 70.7/94.3/117.9 dB), droop by only ≈ 0.056 dB. So CICs suit decimating to a rate at least ~8× the wanted bandwidth; then a conventional FIR does the final sharp filtering.

*Droop compensation.* Follow the CIC with a short FIR (at the CIC output rate, often also decimating by 2 or 4) whose pass-band response is $1/|\mathrm{sinc}(M\nu)|^N$ (an "inverse-sinc" shape) and whose stop-band removes what the CIC let through. Script §7: R = 16, N = 4, pass-band to 0.2 $f_{so}$ has 2.31 dB droop; a 31-tap least-squares compensator makes the total ripple 0.054 dB. Xilinx/Intel CIC IP cores and ADI DDC cores are built this way [3], [8].

**CIC interpolators** are the mirror image: combs at the low rate, zero-stuff by R, integrators at the high rate; used in DUCs ([NCO/DDC/DUC](nco-ddc-duc.md)). Their register growth is computed per stage.

### Level 3 — multistage design, arbitrary resampling, channelisers, fs/4 conversion
**Multistage optimisation.** For a total decimation $M = M_1M_2\cdots M_K$ the cost is $\sum_i N_i f_{s,i}$, where $N_i\propto A/(\Delta f_i/f_{s,i-1})$. Early stages see a huge relative transition band (they only protect the final band) and are short; the final stage runs slowest. Crochiere & Rabiner showed that 2–3 stages with decreasing factors ($M_1 > M_2 > \ldots$) are usually near-optimal, with savings of an order of magnitude over one stage for large M [2 ch. 5]. Practical recipe: CIC (large R) or cascaded half-bands for everything down to ~4–8× the wanted bandwidth → compensating/half-band FIR → final channel filter (e.g. RRC matched filter, [pulse shaping](../10-comms-modulation/pulse-shaping-isi.md)).

**Rational and arbitrary resampling.** A ratio $L/M$ with small integers uses a polyphase interpolator with L phases, of which only the phases needed for each output are computed (`scipy.signal.resample_poly`, GNU Radio `Rational Resampler`). Script §8b: 2.4 MS/s × 5/24 = 500 kS/s keeps a 50 kHz tone at 0.00 dB and puts a 700 kHz interferer's alias 116 dB down. For irrational or time-varying ratios (clock-drift compensation, symbol timing recovery), use a polyphase bank with many phases (e.g. 32–256) and interpolate between neighbouring phases, or a **Farrow** structure (polynomial interpolation whose coefficients are fixed FIRs and whose fractional delay μ is a run-time input) — the same machinery as the interpolators in [timing recovery](../10-comms-modulation/synchronization-carrier-timing.md). GNU Radio's `PFB Arbitrary Resampler` and liquid-dsp's `msresamp` implement these.

**Polyphase filter bank (PFB) channeliser.** To split a band into M equally spaced channels, each mixed to baseband, filtered by a prototype low-pass $h$ and decimated by M:
$$y_k[m] = \sum_n h[n]\,x[mM-n]\,e^{j2\pi kn/M} = \sum_{q=0}^{M-1}e^{j2\pi kq/M}\,(E_q * x_q)[m],$$
with $E_q[p] = h[pM+q]$ and $x_q[m] = x[mM-q]$. The inner sums are the polyphase branches (computed once for all channels) and the outer sum over $q$ is an M-point inverse DFT. So all M channels cost one prototype filter plus one FFT per M input samples, versus M separate mixers and filters [3 ch. 9], [4]. Script §10 (M = 8, 96-tap Kaiser prototype): each channel equals brute-force mix-filter-decimate to 3×10⁻¹¹, and a tone in channel 3 leaks ≤ −90 dB into the others. Variants: **oversampled** (output rate 2× channel spacing) channelisers avoid the gaps and aliasing at channel edges and let a signal straddling two channels be recovered; **synthesis** banks (IFFT + polyphase) combine channels for multi-channel transmitters; M can be hundreds (radio astronomy, spectrum monitoring, digital beamforming front ends — [beamforming](../12-phased-arrays/beamforming-architectures.md)).

**$f_s/4$ real-to-complex conversion.** A real ADC sampling an IF at $f_s/4$ (e.g. the RTL2832U digitises the R820T2's real IF; Airspy converts real ADC samples on the host [see [hardware survey](sdr-hardware-survey.md)]) can form I/Q by multiplying by $e^{-j\pi n/2} = 1, -j, -1, j, \ldots$ — sign changes and I/Q swaps only — then a half-band low-pass (gain 2) and ÷2. Half the half-band's taps are zero *and* half the mixed samples are zero on each rail, so it is extraordinarily cheap. Script §9: a tone at +100 kHz on a 1 MHz real IF (4 MS/s) is recovered at 0.00 dB with its image at −90.6 dB.

## Design equations & rules of thumb

| Equation / rule | When valid | Typical values |
|---|---|---|
| Decimator stop-band starts at $f_s/M - f_p$ | final band $\lvert f\rvert\le f_p$ protected later | 2.0 MS/s ÷4, $f_p$ 80 kHz: stop from 420 kHz |
| Polyphase cost $N\cdot f_{s,out}$ MAC/s | FIR decimator | vs $N f_{s,in}$ direct |
| Half-band: $h[c]=\tfrac12$, $h[c\pm2k]=0$ | edges symmetric about $f_s/4$ | ~¼ of a general FIR's multiplies |
| CIC $\lvert H\rvert = \lvert\sin(\pi fRM)/\sin(\pi f)\rvert^N$ | input-rate f | nulls at $k f_{so}/M$ |
| CIC gain $(RM)^N$; width $B_{in}+N\log_2(RM)$ | wrap-around OK | 12 bit, R=8, N=4 → 24 bit |
| CIC droop ≈ $-20N\log_{10}\lvert\mathrm{sinc}(M\nu_p)\rvert$ | large R | N=4, $\nu_p$=1/8: 0.90 dB |
| CIC alias rejection ≈ $-20N\log_{10}\lvert\mathrm{sinc}(M(1-\nu_p))\rvert$ | large R | N=4, 1/8: 68.5 dB; 1/16: 94.3 dB |
| Use CIC down to ≥ 8× wanted BW, then FIR | — | then compensate droop |
| 2–3 stages, decreasing factors | multistage, large M | ≥ 10× saving |
| Channeliser cost: 1 prototype + 1 M-pt FFT per M samples | uniform channels | M = 8…1024 |

## Worked examples

**1 — Receiving a LoRa BW125 channel at 433.92 MHz with an RTL-SDR (the reference design).**
*Goal*: complex samples at 500 kS/s (4 samples per chip, a common gr-lora_sdr oversampling), channel centred at 0 Hz, no aliases, minimum CPU.
- *Front end*: RTL-SDR Blog V3/V4 (R820T2/R828D low-IF, [IQ](iq-complex-baseband.md)); choose $f_s$ = **2.0 MS/s** (integer ratio 4 to 500 kS/s; RTL-SDRs accept rates up to ≈ 2.56 MS/s without drops [9]). Tune $f_{LO}$ = 433.52 MHz (offset 400 kHz) so the channel sits at +400 kHz, clear of the centre and of the band-edge roll-off (±0.8 MHz usable).
- *Stage 1*: multiply by $e^{-j2\pi\cdot400\text{k}\cdot n/f_s}$ ([NCO](nco-ddc-duc.md)); then a polyphase ÷4 low-pass with pass-band ±80 kHz and stop-band from $500 - 80 = 420$ kHz: $\Delta f/f_s = 340/2000 = 0.17$ → harris ≈ 60/(22×0.17) ≈ 16 taps; the script uses **23 taps** (77.8 dB stop-band). Cost 23 × 0.5 MS/s = 11.5 M MAC/s per rail.
- *Stage 2*: channel filter at 500 kS/s, pass ±62.5 kHz, stop from ±80 kHz, 60 dB: **83 taps** ([filters Example 1](digital-filters-fir-iir.md)), 41.5 M MAC/s per rail.
- *Check* (script §8a): +20 dB interferers placed so that two of them alias *into* the channel after ÷4 end up −80 dB relative to their input level; the wanted 120 kHz-wide band passes with +0.01 dB. Total 53 M MAC/s per rail vs 898 M for one 374-tap filter at 2.4 MS/s — **17× cheaper**. In GNU Radio, stages 1 and 2's mixing + filtering + decimation map onto one `Frequency Xlating FIR Filter` (decimation 4) followed by an optional `FIR Filter`.
- *If you must stay at 2.4 MS/s* (e.g. a recording made that way): resample by **5/24** with a polyphase rational resampler (script §8b) or decimate by 2 to 1.2 MS/s and resample by 5/12.
- *Or give the decoder 250 kS/s* (2 samples/chip): add a half-band ÷2 (≈ 9 multiplies/output) — gr-lora_sdr works with lower oversampling but timing/CFO estimation is more robust with more.

**2 — CIC + compensator for an FPGA DDC.** A 14-bit ADC at 64 MS/s must deliver a 125 kHz LoRa channel at 500 kS/s (total ÷128). Plan: NCO → CIC with R = 64, N = 5, M = 1 → 1 MS/s → 2× decimating compensating FIR → 500 kS/s.
- Pass-band edge at the CIC output: $\nu_p$ = 62.5/1000 = 0.0625 → droop 0.28 dB, first-alias rejection 117.9 dB (N = 4 would give 94.3 dB, N = 3 70.7 dB).
- Registers: 14 + 5 × log₂64 = **44 bits** — fits a 48-bit DSP-slice accumulator, or use Hogenauer pruning to trim later stages.
- The compensator (≈ 30–60 taps) runs at 1 MS/s — 30–60 M MAC/s, one DSP slice time-shared at 100+ MHz. The CIC itself uses 10 adders and no multipliers. See [FPGA for SDR](fpga-for-sdr.md).

**3 — What the AD9361 (Pluto, B200, bladeRF 2.0) does for you.** Its receive path is: analogue low-pass filters → 12-bit ADC → HB3/DEC3 (÷1, 2 or 3) → HB2 (÷1 or 2) → HB1 (÷1 or 2) → a programmable FIR of 16–128 taps (÷1, 2 or 4, gain −12 to +6 dB) [7]. Maximum total decimation 3 × 2 × 2 × 4 = 48. The driver designs the FIR for the requested sample rate and bandwidth. The chip's own lower limit is commonly quoted as ≈ 2.08 MS/s without the FIR's ÷4 and ≈ 521 kS/s with it; ADI specifies Pluto from 65.1 kS/s to 61.44 MS/s [11], consistent with the Pluto FPGA adding a further ÷8 (521/8 = 65.1 kS/s) — treat the 521 kS/s/÷8 decomposition as inferred, not documented here. Pluto's USB 2 link, not the chip, usually sets the practical ceiling (≈ 4–12 MS/s sustained depending on host — sources disagree, see [hardware survey](sdr-hardware-survey.md)). For LoRa on a Pluto, request 1 or 2 MS/s from the chip, then decimate on the host as in Example 1.

**4 — Watching every LoRa channel in the 433 MHz ISM band at once.** 433.05–434.79 MHz fits in a 2.0 MS/s capture. A 16-channel critically sampled PFB gives 125 kHz-spaced channels at 125 kS/s — but LoRa channels are not on a 125 kHz grid, so a signal would straddle two channels. Use a 2×-oversampled channeliser with 32 channels at 62.5 kHz spacing, each output 125 kS/s wide… or simpler: a 32-channel PFB at 62.5 kHz spacing whose adjacent pairs are recombined, or just run several Example-1 chains in parallel (cheap on a PC). For a *detector* rather than decoder, a single long FFT per LoRa symbol after dechirping is even cheaper ([LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md)).

**5 — Transmitting (interpolation).** A 250 kS/s baseband FSK waveform must reach a HackRF that needs ≥ 8 MS/s for clean filtering (MAX2837 baseband filter limits, [hardware survey](sdr-hardware-survey.md)): interpolate ×32 as ×4 (FIR) × ×2 × ×2 × ×2 (half-bands), or a CIC ×8 with pre-compensation. The images each stage creates must be below your spectral-mask requirement — transmitting images is transmitting spurious emissions ([regulations](../19-regulations-safety/spectrum-allocation-ism-bands.md)).

## Practical notes
- **GNU Radio blocks**: `Frequency Xlating FIR Filter` (NCO + polyphase decimating FIR), `Rational Resampler` (designs its own Kaiser-window filter unless you pass taps), `PFB Decimator`, `PFB Channelizer` and `PFB Synthesizer`, `PFB Arbitrary Resampler`, `FIR Filter` with decimation. Build taps with `firdes`/`optfir` ([GNU Radio](gnu-radio-and-software-stack.md)).
- **Python**: `scipy.signal.resample_poly(x, up, down, window=...)` (polyphase, handles rational ratios, fine for offline IQ files); `scipy.signal.decimate` uses an IIR by default (non-linear phase) — pass `ftype='fir'` for data signals. Avoid `scipy.signal.resample` (FFT-based, assumes periodicity) on long recordings.
- **Latency** accumulates across stages: a 23-tap stage at 2 MS/s adds 5.5 µs; an 83-tap filter at 500 kS/s adds 82 µs; CICs add $N(RM-1)/2$ input samples.
- **Fixed-point CICs**: register widths from the formula, wrap-around allowed in integrators, and never saturate them (saturation breaks the modular-arithmetic argument).
- **Check aliasing empirically**: sweep a signal-generator tone across the SDR's whole span and watch whether anything appears in your final channel — cheap way to validate a decimation chain and the SDR's own internal filters.

## Common mistakes & misconceptions
1. **"Decimating is just `x[::M]`."** Without a filter everything from the other $M-1$ zones aliases in at full strength (script §1).
2. **"The decimation filter must cut off at $f_s/2M$."** Only the bands that fold onto the *final* pass-band need rejecting; over-specifying makes early stages 5–10× longer than necessary.
3. **Forgetting the gain of L after zero-stuffing** (interpolated signal 20log₁₀L dB too low) — or of $(RM)^N$ in a CIC (shift right by $N\log_2(RM)$ bits).
4. **Using a CIC for the final sharp filtering.** Its pass-band droops and its transition is soft; follow it with a compensating FIR.
5. **Too few CIC register bits** — the output silently becomes wrong (script: 2 bits short fails). Too *many* is harmless except for area.
6. **Saturating arithmetic in CIC integrators** — must be wrap-around.
7. **Assuming a critically sampled channeliser can receive a signal anywhere** — signals at channel boundaries are attenuated/aliased; oversample the channeliser or align channels.
8. **Using an IIR `decimate` on modulated data** and wondering why the eye closes — non-linear phase.

## How to simulate / verify
- `python3 tools/verify/dsp_multirate_cic.py` (≈ 1 s): aliasing with/without filter; polyphase equivalence; interpolation images; half-band tap structure and symmetry; bit-exact integer CIC with wrap-around vs exact convolution; CIC formula, droop and alias rejection; droop compensator; the full RTL-SDR LoRa chain (both 2.0 and 2.4 MS/s variants) with interferer tests and MAC counts; $f_s/4$ conversion; PFB channeliser vs brute force. All PASS.
- To validate your own chain: feed a complex chirp sweeping $-f_s/2\ldots f_s/2$ through it and plot the output power vs input frequency — that is the chain's *aliased* frequency response, the most honest test.

## Open questions / gaps
- The RTL2832U's internal decimation chain (from 28.8 MS/s) and its alias rejection at each supported rate are undocumented publicly; not characterised here.
- Pluto's lower rate limit: ADI specifies 65.1 kS/s; the split into AD9361 ≈ 521 kS/s × FPGA ÷8 is inferred, not verified in the HDL/driver source.
- Hogenauer's register-pruning formulas are described, not implemented.
- Oversampled (2×) channeliser not simulated.

## Sources
1. A. V. Oppenheim, R. W. Schafer, *Discrete-Time Signal Processing*, 3rd ed., Pearson (2010), §4.6 (changing the sampling rate: downsampling, upsampling, rational ratios), §4.7 (multirate techniques: noble identities, polyphase decomposition, multistage decimation). (textbook)
2. R. E. Crochiere, L. R. Rabiner, *Multirate Digital Signal Processing*, Prentice Hall (1983), chs. 2–3 (basic theory, structures), ch. 5 (multistage implementations and optimal stage factors), ch. 7 (filter banks). (textbook)
3. f. j. harris, *Multirate Signal Processing for Communication Systems*, Prentice Hall (2004; 2nd ed. River Publishers 2021): polyphase decimators/interpolators, half-band filters, cascaded integrator-comb filters, polyphase channelisers, arbitrary resamplers. (textbook) — *chapter numbering not re-verified.*
4. P. P. Vaidyanathan, *Multirate Systems and Filter Banks*, Prentice Hall (1993), ch. 4 (multirate building blocks, polyphase), ch. 5 (maximally decimated filter banks). (textbook)
5. E. B. Hogenauer, "An economical class of digital filters for decimation and interpolation," *IEEE Trans. Acoustics, Speech, Signal Processing* ASSP-29(2):155–162 (1981). (peer-reviewed) — CIC structure, response, register growth, wrap-around, pruning.
6. R. G. Lyons, *Understanding Digital Signal Processing*, 3rd ed., Prentice Hall (2011), ch. 10 (sample-rate conversion, polyphase filters, CIC filters and compensation). (textbook)
7. Analog Devices, "AD9361, AD9364 and AD9363 — general description" (ADI developer documentation) and *AD9361 Reference Manual UG-570*: RX path HB3/DEC3 (÷1/2/3), HB2 (÷1/2), HB1 (÷1/2), programmable 16–128-tap FIR (÷1/2/4, gain −12/−6/0/+6 dB). https://developer.analog.com/docs/system-level/solutions/reference-designs/fmcomms2/common/ad9361_ad9363_ad9364_general_description.html (manufacturer docs; from search summary 2026-09-27)
8. Xilinx/AMD *CIC Compiler* product guide PG140 and Intel/Altera AN455 "Understanding CIC compensation filters" (app notes) — CIC + compensator practice. *Cited from general knowledge; not re-read.*
9. RTL-SDR.com, "About RTL-SDR," https://www.rtl-sdr.com/about-rtl-sdr/ — 3.2 MS/s max (unstable), 2.56 MS/s highest without dropped samples. (manufacturer/community blog; via helper research 2026-09-27)
10. J. Tapparel et al., "An open-source LoRa physical layer prototype on GNU Radio," IEEE SPAWC 2020, arXiv:2002.08208; code https://github.com/tapparelj/gr-lora_sdr. (peer-reviewed + code) — oversampled LoRa receiver input.
11. Analog Devices, ADALM-PLUTO specifications, https://wiki.analog.com/university/tools/pluto/devs/specs (manufacturer wiki; via helper research 2026-09-27) — 65.1 kSPS–61.44 MSPS, 200 kHz–20 MHz bandwidth, "up to 4 MSPS" without dropped samples over USB.
