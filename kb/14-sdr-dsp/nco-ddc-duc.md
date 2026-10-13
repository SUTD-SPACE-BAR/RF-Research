---
title: NCOs, digital down-conversion (DDC) and up-conversion (DUC) — phase accumulators, spurs, CORDIC and real SDR chains
domain: 14-sdr-dsp
slug: nco-ddc-duc
tags: [nco, dds, phase-accumulator, tuning-word, phase-truncation, sfdr, dither, lut, cordic, ddc, duc, cic, direct-sampling, rtl2832u, ad9361, rfsoc, frequency-correction, doppler, fsk]
prerequisites: [iq-complex-baseband.md, multirate-dsp-decimation-cic.md, digital-filters-fir-iir.md, sampling-aliasing-bandpass-sampling.md]
related: [fpga-for-sdr.md, sdr-hardware-survey.md, software-demodulation.md, fft-spectral-analysis-windows.md, ../07-noise-linearity/phase-noise-and-jitter.md, ../06-rf-circuits/vco-and-pll-synthesizers.md, ../10-comms-modulation/synchronization-carrier-timing.md, ../10-comms-modulation/digital-modulation-psk-qam-fsk.md, ../12-phased-arrays/beamforming-architectures.md, ../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md, ../18-components-parts/adcs-dacs-for-sdr.md]
level: mixed
confidence: high
last_updated: 2026-10-14
---

# NCOs, digital down-conversion (DDC) and up-conversion (DUC)

## Questions this page answers
- How does a numerically controlled oscillator (NCO / DDS) make a sine wave from a counter?
- What frequency resolution does a 32-bit or 48-bit phase accumulator give?
- Why does an NCO have spurs, and how many phase and amplitude bits do I need for a given SFDR?
- Is it really "6 dB per phase bit"?
- What does dithering do for an NCO?
- What is CORDIC and why do FPGAs use it?
- What is inside the digital down-converter of an RTL-SDR, an AD9361, an RFSoC or an FPGA SDR?
- How do I build a DDC for a direct-sampling HF receiver, and a DUC for a transmitter?
- How do I correct ppm error or rocket Doppler with an NCO?
- How do I generate phase-continuous FSK digitally?

## TL;DR
- **NCO** = phase accumulator (adds a tuning word FTW every clock, wraps at $2^N$) + phase-to-amplitude conversion (LUT or CORDIC). $f_{out} = \mathrm{FTW}\cdot f_s/2^N$; resolution $f_s/2^N$ (32 bits at 61.44 MHz: 14.3 mHz; 48 bits at 5 GS/s: 18 µHz). Wrap-around of the accumulator *is* the phase wrap at 2π — free and exact.
- **Phase truncation** (only the top $P$ of $N$ accumulator bits address the LUT) makes a periodic phase error and hence spurs. Simulation: **worst-case SFDR = 6.02P − 3.92 dB** exactly (P = 8/10/12: 44.2/56.3/68.3 dB), typical tuning words ≈ 6.02P. Forcing the tuning word odd (Nicholas & Samueli's modification) makes the worst case 6.02P [2]. So the popular "6 dB/bit" is the typical, not guaranteed, figure.
- **Amplitude quantisation** of the LUT output (A bits): SNR ≈ 6.02A + 1.76 dB (script: 8/12/16 bits → 50.0/74.0/98.1 dB).
- **Phase dither** (random LSBs added before truncation) turns spurs into a noise floor: P = 10 went from 56.3 dB to 88.8 dB SFDR.
- **CORDIC** computes sin/cos (or magnitude/atan2) with shifts and adds: ≈ 1 bit (6.02 dB) of accuracy per iteration, constant gain $K = 1.64676$.
- **DDC** = NCO mixer → CIC (big ÷R) → compensating/half-band FIRs → channel filter. Script: a 16-bit, 64 MS/s direct-sampling HF chain to 250 kS/s delivers a −66 dBFS CW at exactly the right level and puts a +40 dB blocker 600 kHz away at −135.6 dB — with a **bit-true integer CIC**; the same CIC built with float64 `cumsum` over 2²¹ samples was wrong by a factor of ~4000.
- **DUC** mirrors it: interpolate (FIR/half-band/CIC), mix up with the NCO, DAC. A +50 kHz baseband tone appears only at $f_c$ + 50 kHz (other sideband −111 dB).
- **Frequency correction** is just an NCO: 12.5 ppm at 433.92 MHz = 5424 Hz; rocket Doppler at 300 m/s ≈ 434 Hz.

Verified by `tools/verify/dsp_nco.py` (all PASS).

## Intuition (no math)
Picture a clock hand that jumps forward by a fixed angle every tick of the sample clock. The bigger the jump, the faster it goes round — that's the frequency. The hand's angle is stored as a binary number that simply overflows back to zero after a full turn, so going round and round costs nothing. To turn the angle into a sine-wave sample, look it up in a table (or compute it). That is a numerically controlled oscillator: a counter plus a lookup.

Tables cost memory, so real NCOs throw away the fine bits of the angle before the lookup. The hand then sits slightly "behind" where it should be, by an amount that repeats in a pattern — and any repeating error in a signal shows up as spurs (unwanted tones) in its spectrum. More address bits make the error smaller; each extra bit halves it (~6 dB less spur). Jiggling the angle randomly before truncating (dither) breaks the repeating pattern, so the spur energy spreads out as low-level noise.

A digital down-converter uses the NCO exactly like an analogue mixer uses a local oscillator — but with a perfect 90° I/Q split, no leakage, no DC offset, and instantaneous, phase-continuous retuning — then filters and throws away samples to reach a manageable rate. The up-converter does the reverse.

## The math

### Level 1 — the phase accumulator
- Accumulator width $N$ bits, clock $f_s$, tuning word FTW (integer): phase $\phi[n] = (n\cdot\mathrm{FTW}) \bmod 2^N$, representing $2\pi\phi/2^N$ rad.
- Output frequency $f_{out} = \mathrm{FTW}\,f_s/2^N$ ($0\le\mathrm{FTW}<2^{N-1}$ for $0\le f<f_s/2$; for complex outputs, FTW $\ge 2^{N-1}$ are negative frequencies).
- Resolution $\Delta f = f_s/2^N$; rounding the ideal FTW gives an error ≤ $f_s/2^{N+1}$ (script §1: 6.4 mHz ≤ 7.2 mHz bound for 12.3456789 MHz at 61.44 MHz, 32 bits).
- Examples: 24-bit at 28.8 MHz → 1.72 Hz; 32-bit at 61.44 MHz → 14.3 mHz; 48-bit at 5 GHz → 17.8 µHz.
- **Complex NCO** outputs $\cos\theta - j\sin\theta$ (for down-conversion, $e^{-j\theta}$) from the same phase; multiplying the input by it shifts the spectrum by $-f_{out}$ ([IQ](iq-complex-baseband.md)).
- **Phase-continuous hopping**: changing FTW changes only the *rate* of phase advance, never the phase itself — FSK and chirps generated this way have no phase jumps (script §9: largest phase step = $2\pi f_{max}/f_s$).

### Level 2 — spurs, amplitude quantisation, dither, CORDIC
**Phase truncation.** Only the top $P$ bits address the phase-to-amplitude converter; the discarded $N-P$ bits form a phase error $\epsilon[n]\in[0, 2\pi2^{-P})$ that is periodic (period set by the discarded part of FTW). For small errors $e^{j(\theta+\epsilon)}\approx e^{j\theta}(1+j\epsilon)$: the output is the ideal tone plus the tone *phase-modulated* by a periodic sawtooth-like sequence — i.e. discrete sidebands. Each extra phase bit halves the maximum phase error, so the spurs drop ≈ 6.02 dB per bit. Nicholas & Samueli derived the spectrum exactly with number-theoretic methods; the worst-case spur for a conventional accumulator is $-(6.02P - 3.92)$ dBc, and a small modification — making the effective tuning word odd, e.g. by setting the accumulator's LSB — reduces the worst case by 3.92 dB to $-6.02P$ dBc [2], [4]. Script §2 reproduces both to 0.01 dB for P = 6–12 (conventional worst case 32.20/44.24/56.28/68.32 dB; odd-FTW 48.13/60.20/72.25 dB for P = 8/10/12; random tuning words ≈ 6.02P). The 3.92 dB is $-20\log_{10}\mathrm{sinc}(\tfrac12)$ — the same number as rectangular-window scalloping loss ([FFT](fft-spectral-analysis-windows.md)).

**Amplitude quantisation.** Storing the LUT values with $A$ bits adds error $\le\tfrac12$ LSB per sample; for "busy" phase sequences it behaves as white noise with SNR ≈ $6.02A+1.76$ dB (script §3: 49.97/74.03/98.09 dB for A = 8/12/16). For short periodic phase sequences it produces harmonic spurs instead. Balanced designs choose $A \approx P$ to $P+2$ and pick the SFDR target as the smaller of the two limits.

**LUT size reduction.** A $P$-bit phase needs a $2^P$-word table; quarter-wave symmetry (sin in the first quadrant only, with reflections and sign flips) cuts it by 4 (script §5, exact with a half-LSB phase offset); further tricks (Sunderland coarse/fine tables, Taylor-series correction with a multiplier) trade a multiplier for memory. FPGA DDS IP (e.g. Xilinx DDS Compiler) exposes exactly these choices.

**Dither.** Adding a random integer uniformly distributed over the discarded bits before truncation makes $\epsilon[n]$ random instead of periodic: the spur power spreads over the band as a noise floor. Script §4: P = 10 worst-case tuning word, SFDR 56.3 → 88.8 dB. The total error power is unchanged (actually slightly larger), so dither suits applications that care about spurs (spectrum monitoring, radar, receivers where a spur could mask a weak signal) more than about integrated noise.

**CORDIC (Volder 1959 [5]).** Rotate the vector $(x,y)$ by $\theta$ in steps of $\pm\arctan2^{-i}$:
$$x_{i+1} = x_i - d_iy_i2^{-i},\quad y_{i+1} = y_i + d_ix_i2^{-i},\quad z_{i+1} = z_i - d_i\arctan2^{-i},\quad d_i = \mathrm{sign}(z_i).$$
Each step is two shifts and three adds (the arctan constants are a small table). After $n$ steps $z\to0$ and $(x,y)$ is rotated by $\theta$ and scaled by $K_n = \prod_{i=0}^{n-1}\sqrt{1+2^{-2i}}\to1.646760$ (script §6: 1.646760258), a constant removed once. Starting from $(1/K, 0)$ gives $(\cos\theta, \sin\theta)$. Accuracy improves ≈ 1 bit (6.02 dB) per iteration (script: max error 7.8×10⁻³, 4.8×10⁻⁴, 3.0×10⁻⁵, 1.9×10⁻⁶ at 8/12/16/20 iterations). *Vectoring mode* (drive $y\to0$) returns magnitude × K and $\mathrm{atan2}(y,x)$ — the core of an FPGA FM discriminator or AM detector ([demodulation](software-demodulation.md)). In FPGAs CORDIC is pipelined one iteration per stage [6]; LUTs + DSP-slice multipliers often win when block RAM is plentiful ([FPGA](fpga-for-sdr.md)).

**The DDC chain.** For an input $x[n]$ (real from a direct-sampling ADC, or complex from an IQ front end):
1. **Mix**: $v[n] = x[n]e^{-j2\pi f_{NCO}n/f_s}$ — the channel moves to 0 Hz (a real input's mirror image moves to $-2f_{NCO}$ and is filtered away).
2. **CIC ÷R** (multiplier-free, large factor) — [multirate](multirate-dsp-decimation-cic.md).
3. **Compensating FIR / half-band(s)** ÷2…÷4 — flatten droop, provide alias protection.
4. **Channel filter** (possibly a matched RRC filter) at the final rate.
Script §7 builds this bit-true: 16-bit ADC codes at 64 MS/s, 32-bit accumulator with 20-bit phase and 16-bit LUT, integer CIC (R = 64, N = 5, 31-bit products + 30 bits growth = 61-bit registers, int64 wrap-around), 121-tap least-squares compensator ÷4 → 250 kS/s. A −60 dBFS CW 12 kHz above the NCO comes out at −66.02 dB (the −6.02 dB is the real-to-complex split), pass-band flat to 0.000 dB between 12 and 90 kHz (0.58 dB of droop compensated), and a +40 dB blocker 600 kHz away (which aliases to 100 kHz) ends up 135.6 dB down. The same CIC implemented with float64 cumulative sums was wrong by a relative factor of ~4×10³: integrators must be integers ([filters](digital-filters-fir-iir.md)).

**The DUC chain** is the transpose: channel/pulse-shaping filter → interpolating half-bands/FIR → CIC interpolator (with pre-compensation) → complex mix up by the NCO → take the real part (or feed an IQ DAC pair) → DAC with sinc-droop correction ([sampling](sampling-aliasing-bandpass-sampling.md)). Script §8: 1 MS/s baseband, ×16 interpolation, NCO at 3 MHz, real DAC output — the +50 kHz tone appears at 3.05 MHz (−6.03 dB, the real-part split) and nothing at 2.95 MHz (−111 dB): a digital single-sideband modulator with perfect image rejection.

### Level 3 — real implementations, coherence, and limits
**What real SDRs do.**
- *RTL-SDR (RTL2832U)*: the R820T2/R828D tuner delivers a real low IF (≈ 3.57 MHz, or 4.57 MHz for 8 MHz DVB-T settings); the RTL2832U samples it at 28.8 MS/s, digitally mixes the IF to 0 Hz with an internal NCO and resamples to the rate you ask for [8], [9] (the librtlsdr driver programs the IF frequency and a fractional resampling ratio derived from the 28.8 MHz crystal — details from driver source, not a public datasheet). The ppm correction adjusts both.
- *Airspy R2/Mini*: a 12-bit real ADC at 20 MS/s (Mini: lower rates) digitises the tuner's IF and the *host* library converts to IQ (a DDC in software) [10].
- *AD9361/AD9363/AD9364 (Pluto, USRP B2x0, bladeRF 2.0)*: zero-IF — tuning is done by the RF synthesiser, not an NCO; the digital path is decimation only (HB3/DEC3, HB2, HB1, programmable FIR) [7]. Fine frequency corrections are made by retuning the RF PLL or in the host/FPGA with an NCO.
- *AMD/Xilinx RFSoC*: RF ADCs sample directly at several GS/s; each converter tile has a DDC with a 48-bit NCO, complex mixer and fixed decimation stages (vendor documentation as summarised by the helper research; not re-read) [11].
- *FPGA SDRs*: Ettus RFNoC DDC/DUC blocks (CIC + half-bands + NCO); HackRF Pro's iCE40 gateware includes a DC blocker, an $f_s/4$ shifter and 1–32× decimation/interpolation [12].

**NCO spur vs clock jitter.** An NCO's output phase noise is the sample clock's phase noise scaled by $f_{out}/f_s$ (a DDS divides, so it *reduces* clock phase noise by $20\log_{10}(f_s/f_{out})$) plus the truncation/quantisation floor. In a DDC the NCO is a digital multiplier — its "phase noise" is only its spurs and quantisation; the analogue clock jitter has already been applied at the ADC ([phase noise](../07-noise-linearity/phase-noise-and-jitter.md)).

**Phase coherence across channels.** Multiple DDCs for an antenna array (phased array, DOA, KrakenSDR-style coherent receivers) must start their NCOs with known phase: reset all accumulators on a common sync pulse, clock them from a common reference, and calibrate the residual analogue phase differences with a common noise source ([beamforming](../12-phased-arrays/beamforming-architectures.md), [array calibration](../12-phased-arrays/array-calibration.md)). A free-running NCO retune generally leaves an arbitrary phase offset — fine for one receiver, fatal for an array.

**NCOs inside loops.** Every digital PLL, Costas loop and frequency-locked loop ([synchronisation](../10-comms-modulation/synchronization-carrier-timing.md)) ends in an NCO whose FTW is the loop filter's output; Doppler tracking in a GNSS receiver is a carrier NCO plus a code NCO. The resolution and update rate of the FTW set the finest frequency step and the loop's quantisation noise.

**Direct Digital Synthesis (DDS) chips** (e.g. ADI AD9850/AD9910-class) are an NCO + DAC on one die, used as agile signal sources and as reference generators for PLLs ([VCO & PLL](../06-rf-circuits/vco-and-pll-synthesizers.md)). Their datasheet SFDR is dominated by the DAC's non-linearity, not by truncation, once $P\ge14$ or so [3].

## Design equations & rules of thumb

| Equation / rule | When valid | Typical values |
|---|---|---|
| $f_{out} = \mathrm{FTW}f_s/2^N$; $\Delta f = f_s/2^N$ | phase accumulator | 32-bit @ 61.44 MHz: 14.3 mHz |
| FTW rounding error ≤ $f_s/2^{N+1}$ | exact frequency requests | 7.2 mHz @ 61.44 MHz |
| Worst-case SFDR (phase trunc.) = 6.02P − 3.92 dB | conventional accumulator | P = 12: 68.3 dB |
| Worst-case SFDR = 6.02P dB | odd-FTW (LSB forced) accumulator | P = 12: 72.2 dB |
| Amplitude SNR ≈ 6.02A + 1.76 dB | busy phase sequence | A = 16: 98 dB |
| Choose $A\approx P$…$P+2$ | balanced LUT | 14/16 bits for ~80–90 dB |
| Dither: spurs → noise | P-bit truncation | P = 10: 56 → 89 dB SFDR |
| CORDIC: ~1 bit per iteration, $K = 1.64676$ | rotation/vectoring | 16 iterations ≈ 16 bits |
| Quarter-wave LUT: ¼ memory | sin/cos | $2^{P-2}$ words |
| DDC: NCO → CIC ÷R → comp FIR → channel FIR | high-rate ADC | 64 MS/s → 250 kS/s |
| CIC registers = input bits + $N\log_2 R$ | integer, wrap-around | 31 + 30 = 61 bits |
| Correction = $-f_c\cdot$ppm$\times10^{-6}$ | ppm error | 12.5 ppm @ 433.92 MHz: 5.42 kHz |

## Worked examples

**1 — Choosing NCO widths for an 80 dB SFDR FPGA DDC.** Target: NCO spurs below −80 dBc so they never mask a signal the 12-bit ADC (≈ 74 dB SNR, more after processing gain) could see. Conventional accumulator: $P \ge (80+3.92)/6.02 = 13.9$ → **P = 14** (worst case 80.4 dB). With the odd-FTW trick P = 14 gives 84.3 dB; with phase dither even P = 12 comfortably beats 80 dB. Amplitude: A = 16 bits (98 dB) — matches an 18-bit DSP-slice multiplier input with margin. LUT: $2^{14}$ phases → quarter-wave table of 4096 × 16 bits = one or two block RAMs. Accumulator: 32 bits at 61.44 MHz gives 14 mHz steps — ample for Doppler tracking.

**2 — An HF direct-sampling receiver (RX888-class, 16-bit, 64 MS/s) tuned to 7.1 MHz.** As in script §7: NCO at 7.1 MHz (FTW = round(7.1/64 × 2³²) = 476 472 934; actual 7.099 999 994 MHz), CIC R = 64, N = 5 → 1 MS/s (droop 0.58 dB at 90 kHz; first-alias rejection > 110 dB), 121-tap compensator ÷4 → 250 kS/s. Registers: 16-bit × 16-bit mixer products (31 bits) + 30 bits CIC growth = 61 bits. On a PC this is done by the host (SDR++/SDR# for RX888 run exactly this in software); in an FPGA it costs ~10 adders (CIC) + one time-shared DSP slice. To listen to an SSB signal, add a final ÷~5 to 48 kS/s and demodulate ([demodulation](software-demodulation.md)).

**3 — Correcting a ground-station SDR's ppm error and a rocket's Doppler.** A non-TCXO SDR measured −12.5 ppm low against a GNSS-disciplined reference: at 433.92 MHz its samples show signals 5424 Hz high → set the NCO 5424 Hz lower (or use the driver's ppm setting, which moves the RF LO and sample rate together). Rocket: 300 m/s radial velocity → Doppler $f v/c$ = 434 Hz; boost-phase range acceleration 100 m/s² — the **range** acceleration $\ddot R = \mathbf a\cdot\hat{\mathbf r} + v_\perp^2/R$ seen by the station, up to ≈ 1.4× the vehicle's acceleration near the pad ([15 impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md#doppler-rate-seen-from-the-ground--the-line-of-sight-rotation-term)) → Doppler *rate* 145 Hz/s, i.e. 0.15 Hz across a 1 ms LoRa SF7 symbol — negligible within a symbol but a 145 Hz drift across a 1 s SF12 packet ([LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)). A per-packet CFO estimate from the LoRa preamble programs the NCO; a 32-bit NCO at 500 kS/s steps in 116 µHz, far finer than needed.

**4 — Generating 2-GFSK telemetry for an SDR transmitter.** Baseband at 1 MS/s: Gaussian-filter the ±1 bit stream (BT = 0.5), scale to ±4.8 kHz deviation, and feed it to the NCO's FTW input each sample — the accumulator integrates frequency into phase, giving continuous-phase FSK with no discontinuities (script §9). Output $e^{j\phi[n]}$ → interpolate to the SDR's rate → DUC/RF. The same structure generates LoRa-style chirps (FTW ramped linearly) — see [LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md) and [digital modulation](../10-comms-modulation/digital-modulation-psk-qam-fsk.md).

## Practical notes
- **GNU Radio**: `Signal Source` is an NCO (float or complex); `Frequency Xlating FIR Filter` = NCO + FIR + decimation (DDC in one block); `Rotator` for pure frequency shifts; `Frequency Mod` block = phase accumulator for FM/FSK; `Complex to Arg` + differentiator for FM demod ([GNU Radio](gnu-radio-and-software-stack.md)).
- **Floating-point NCOs in software** should keep the phase as an integer accumulator (or wrap the float phase every sample) — accumulating `phase += 2*pi*f/fs` in float32 for hours drifts and loses precision.
- **Test an NCO** by generating a long record and computing SFDR with a Blackman–Harris window; sweep the tuning word, including worst-case patterns (discarded bits = 100…0 binary).
- **Spurs in SDR spectra that move when you change the digital offset but not the RF LO** are candidates for NCO/decimation artefacts; ones that move with the RF LO come from the analogue side.
- **Retuning glitches**: changing an RF PLL causes a settling transient (tens of µs to ms); changing an NCO is instantaneous — hop with the NCO within the ADC bandwidth where possible.

## Common mistakes & misconceptions
1. **"NCO SFDR is 6 dB per phase bit, guaranteed."** Worst case is 3.92 dB worse unless the accumulator uses the odd-FTW trick or dither.
2. **Using too few accumulator bits** — frequency steps too coarse for loops (a 16-bit accumulator at 1 MS/s steps in 15 Hz).
3. **Treating CORDIC's gain as a variable** — it depends only on the number of iterations; pre-scale once.
4. **Building CIC integrators in floating point** — precision collapses on long records (script §7).
5. **Forgetting the −6 dB real-to-complex split** when mixing a real ADC stream with a complex NCO — the complex output carries half the real tone's amplitude (the other half went to the mirror, which is filtered away).
6. **Assuming zero-IF transceivers (AD936x) have a DDC NCO for tuning** — they tune with the RF LO; add your own NCO for fine shifts and offset tuning ([IQ](iq-complex-baseband.md)).
7. **Expecting multiple NCOs/receivers to be phase-coherent after retuning** without a synchronised reset and calibration.

## How to simulate / verify
- `python3 tools/verify/dsp_nco.py` (≈ 2 s): accumulator resolution and FTW error; phase-truncation SFDR (worst case 6.02P − 3.92 dB, odd-FTW 6.02P, random ≈ 6.02P); LUT amplitude SNR; dither; quarter-wave LUT; CORDIC gain and convergence; bit-true direct-sampling DDC with integer CIC and float-CIC pitfall; DUC single-sideband check; phase-continuous FSK; ppm numbers. All PASS.
- For FPGA work: write the same bit-true model in Python (integers, explicit wrap/round), generate test vectors, and compare with HDL simulation output sample-for-sample ([FPGA](fpga-for-sdr.md)).

## Open questions / gaps
- The RTL2832U's internal NCO/resampler word lengths and filter responses are not publicly documented; described from driver behaviour and community sources.
- RFSoC DDC details (48-bit NCO, decimation options per generation) come from the helper's search summaries of AMD PG269, not a re-read of the document.
- DAC-related DDS spurs (image, non-linearity) are not modelled.

## Sources
1. J. Tierney, C. M. Rader, B. Gold, "A digital frequency synthesizer," *IEEE Trans. Audio Electroacoustics* AU-19(1):48–57 (1971). (peer-reviewed) — the phase-accumulator/LUT NCO.
2. H. T. Nicholas III, H. Samueli, "An analysis of the output spectrum of direct digital frequency synthesizers in the presence of phase-accumulator truncation," *Proc. 41st IEEE Annual Frequency Control Symposium* (1987), pp. 495–502. (peer-reviewed conference) — exact spur spectrum; worst case and the 3.922 dB modification. *Result confirmed via search summaries (Semantic Scholar; ADI technical article [4]) and reproduced by simulation; paper not re-read.*
3. W. Kester, "Fundamentals of Direct Digital Synthesis (DDS)," Analog Devices Tutorial MT-085 (2008), https://www.analog.com/media/en/training-seminars/tutorials/mt-085.pdf; and Analog Devices, "A Technical Tutorial on Digital Signal Synthesis" (1999). (app notes) — DDS architecture, truncation spurs, DAC effects. *Cited from search listing; not re-read.*
4. Analog Devices, "An Almost Pure DDS Sine Wave Tone Generator," technical article, https://www.analog.com/en/resources/technical-articles/an-almost-pure-dds-sine-wave-tone-generator.html (app note) — restates the Nicholas–Samueli 3.922 dB worst-case reduction and SFDR_min = 6.02W. *From search summary.*
5. J. E. Volder, "The CORDIC trigonometric computing technique," *IRE Trans. Electronic Computers* EC-8(3):330–334 (1959). (peer-reviewed)
6. R. Andraka, "A survey of CORDIC algorithms for FPGA based computers," *Proc. ACM/SIGDA 6th Int. Symp. FPGAs* (1998), pp. 191–200. (peer-reviewed conference)
7. Analog Devices, AD9361/AD9363/AD9364 general description and *AD9361 Reference Manual UG-570* — RX decimation chain (manufacturer docs; see [multirate](multirate-dsp-decimation-cic.md) source 7).
8. superkuh, "rtl-sdr and GNU Radio with Realtek RTL2832U, E4000 and R820T," http://superkuh.com/rtlsdr.html (community documentation) — R820T low IF into the RTL2832U, digital IQ generation.
9. RTL-SDR Blog, "RTL-SDR Blog V3 dongles user guide" and "About RTL-SDR," https://www.rtl-sdr.com (manufacturer) — 28.8 MHz sampling, supported rates; R820T datasheet (2011 preliminary, leaked copy) for 3.57/4.57 MHz IF. (via helper research)
10. Airspy, product pages for Airspy R2 and Mini, https://airspy.com (manufacturer) — 12-bit ADC at 20 MSPS, host-side IQ conversion. (via helper research)
11. AMD/Xilinx, *Zynq UltraScale+ RFSoC RF Data Converter* product guide PG269 (NCO frequency conversion section) (manufacturer docs) — *from search summaries only (unverified).*
12. Great Scott Gadgets, HackRF documentation "gateware" (HackRF Pro iCE40UP5K: DC blocker, $f_s/4$ shifter, 1–32× decimation/interpolation), https://github.com/greatscottgadgets/hackrf/blob/main/docs/source/gateware.rst (manufacturer docs; via helper research)
13. f. j. harris, *Multirate Signal Processing for Communication Systems* (2004/2021), chapters on digital down-/up-converters and NCOs. (textbook)
