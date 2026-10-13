---
title: VCOs and PLL frequency synthesizers (integer-N, fractional-N, loop filters, phase noise, spurs, DDS)
domain: 06-rf-circuits
slug: vco-and-pll-synthesizers
tags: [vco, pll, synthesizer, charge-pump, loop-filter, phase-margin, integer-n, fractional-n, sigma-delta, mash, phase-noise, jitter, reference-spur, lock-time, dds, adf4351, lmx2594, si5351, leeson, dll, gardner-limit, cycle-slip, two-point-modulation, fmcw-ramp, offset-pll, charge-pump-mismatch, bleed-current]
prerequisites:
  - ../05-analog-electronics/oscillators.md
  - ../00-math-foundations/laplace-transfer-functions-bode.md
  - ../07-noise-linearity/phase-noise-and-jitter.md
related:
  - mixers.md
  - receiver-architectures.md
  - transmitter-architectures.md
  - frequency-multipliers-dividers.md
  - ../04-real-components-hf/crystals-and-resonators.md
  - ../05-analog-electronics/diodes-schottky-pin-varactor.md
  - ../14-sdr-dsp/nco-ddc-duc.md
  - ../17-test-measurement/phase-noise-measurement.md
  - ../18-components-parts/mixers-plls-vcos-parts.md
  - ../11-radar/fmcw-radar.md
  - ../21-gnss/gnss-receiver-architecture-acquisition-tracking.md
level: mixed
confidence: high
last_updated: 2026-10-14
---

# VCOs and PLL frequency synthesizers

## Questions this page answers
- How does a phase-locked loop turn a 25 MHz crystal into a clean 433.92 MHz or 3.5 GHz signal?
- What are Kvco, Kφ (charge-pump gain) and N, and how do they set the loop bandwidth?
- How do I design a passive loop filter for a given bandwidth and phase margin?
- Which noise sources dominate close to the carrier and far out, and what is the best loop bandwidth?
- What is the "normalised phase-noise floor" (PN_SYNTH, figure of merit) on a PLL data sheet?
- How does fractional-N work, and where does sigma-delta noise go?
- Where do reference spurs come from and how do I suppress them?
- How long does a PLL take to lock or hop?
- When should I use a DDS or a clock generator like the Si5351 instead?
- How does a VCO's resonator Q set its phase noise (Leeson)?
- What is the difference between a PLL and a DLL, and why do FPGAs have both?
- How fast can the loop be relative to the reference before the PFD's sampling makes it unstable (Gardner limit)?
- Why does a big frequency hop take much longer to lock than the linear model says (cycle slips)?
- How do I measure my PLL's loop bandwidth on the bench?
- How does two-point modulation let a PLL send FSK faster than its loop bandwidth?
- How well does a PLL follow an FMCW chirp, and what happens at the start of the ramp?
- What is an offset (translation) PLL and why is it quieter?
- Why does charge-pump mismatch raise in-band noise in a fractional-N PLL, and what does a bleed current do?

## TL;DR
- A PLL compares the divided VCO phase with a reference in a phase-frequency detector (PFD), pumps current $\pm I_{CP}$ into a loop filter, and steers the VCO so that $f_{VCO}=N\,f_{PFD}$. Open-loop gain $G(s)=\dfrac{K_\phi K_{VCO}Z(s)}{Ns}$ with $K_\phi=I_{CP}/2\pi$ (A/rad) and $K_{VCO}$ in rad/s/V.
- **Passive 2nd-order filter (3rd-order loop)** (Banerjee's method, verified): $T_1=(\sec\varphi-\tan\varphi)/\omega_c$, $T_2=1/(\omega_c^2T_1)$, $A_0=C_1+C_2=\frac{K_\phi K_{VCO}}{N\omega_c^2}\sqrt{\frac{1+\omega_c^2T_2^2}{1+\omega_c^2T_1^2}}$, $C_1=A_0T_1/T_2$, $C_2=A_0-C_1$, $R_2=T_2/C_2$. ADF4351 at 433.92 MHz (VCO 3471.36 MHz ÷ 8, f_PFD 25 MHz, N = 138.8544, I_CP 2.5 mA, K_V 40 MHz/V), 50 kHz / 50°: **C1 = 2.66 nF, C2 = 17.4 nF, R2 = 503 Ω** — crossover 49.9 kHz, PM 50.00°. An extra R3–C3 pole (1 kΩ, 290 pF) adds 33 dB at f_PFD for ≈ 7° of phase margin.
- **In-band noise**: $L_{in}=PN_{SYNTH}+10\log f_{PFD}+20\log N$ (+ flicker $PN_{1/f}+10\log(10\text{ kHz}/f)+20\log(f_{RF}/1\text{ GHz})$). ADF4351: $PN_{SYNTH}$ = −221 dBc/Hz, $PN_{1/f}$ = −118 dBc/Hz [5] → −104 dBc/Hz at the VCO, **−122 dBc/Hz at 433.92 MHz** (÷8 = −18 dB). LMX2594: FoM −236 dBc/Hz, 1/f −129 dBc/Hz, 10 MHz–15 GHz [6]. Higher f_PFD (fractional-N) lowers in-band noise by 10 log f_PFD − 20 log N = −10 log f_PFD net.
- **Loop bandwidth is a noise trade-off**: reference/PFD noise is low-passed, VCO noise high-passed. In the modelled ADF4351 case RMS jitter (1 kHz–10 MHz) is 600/357/**248**/266/341/466 fs for 10/20/**50**/100/200/400 kHz loops — optimum where in-band noise meets the VCO curve.
- **Fractional-N ΣΔ noise** (MASH 1-1-1): $L(f)=\frac{(2\pi)^2}{12f_{PFD}}\left[2\sin\frac{\pi f}{f_{PFD}}\right]^{4}$ before loop filtering (simulated MASH matches to 0.1 dB); it rises 40 dB/decade, so the loop must filter it — the 3rd pole matters.
- **Reference spurs**: leakage $I_L$ gives $\beta=2K_VI_L|Z(f_{PFD})|/f_{PFD}$, spur $=20\log(\beta/2)$: negligible (−168 dBc) at 25 MHz PFD with 1 nA, but −50 dBc at 200 kHz PFD with 10 nA → high PFD frequencies and extra filter poles. Measured PFD spurs (ADF4351 −80 dBc typ [5]) come mostly from mismatch and coupling.
- **Lock time** (linear): 1 MHz hop settles to 1 kHz in ≈ 34 µs with the 50 kHz loop; the VCO band-select calibration of integrated-VCO parts adds more. Big hops in narrow loops **cycle-slip**: 30 MHz in a 10 kHz loop takes 409 µs vs 220 µs linear (exact PFD simulation, Level 3b).
- **Dynamics (Level 3b):** sampling costs ≈ 4° of PM at f_c = f_ref/10 and 18° at f_ref/5; Gardner's series-RC limit $\omega_n^2<\omega_i^2/[\pi(\pi+\omega_i\tau_2)]$ is a linearisation (the exact piecewise analysis is looser); **two-point modulation** gives $1+(g-1)(1-H)$; a type-2 loop tracks an FMCW ramp with phase error $2\pi RA_0/(K_\phi K_{VCO})$; 1 % charge-pump mismatch folds ΣΔ noise up by ≈ 34 dB in band, which a bleed current removes.
- **DDS**: resolution $f_{clk}/2^{N}$ (125 MHz, 32 bit: 29 mHz); phase-truncation spurs ≤ −6.02·P dBc (P = phase bits; verified at −48.1 dBc for P = 8); output ∝ sinc(f/f_clk) (−2.4 dB at 0.4 f_clk). **Si5351**: integer/fractional PLL at 600–900 MHz + fractional multisynth (8 + 1/1 048 575 … 900) → any frequency ≈ 2.5 kHz–200 MHz, e.g. 10.7 MHz = 600 MHz ÷ (56 + 8/107) exactly [8].

## Intuition (no math)
A VCO is a tunable oscillator: fine short-term but it wanders. A crystal is rock-steady but fixed. A PLL marries them: it continually compares the (divided-down) VCO with the crystal and nudges the VCO so their phases stay aligned. Divide the VCO by N before comparing and the VCO is forced to run at exactly N times the reference.

The loop bandwidth decides who is in charge at each offset from the carrier. Inside the bandwidth the loop is fast enough to correct the VCO's wander, so the output inherits the reference's noise (multiplied by N — the phase error of a slow reference is multiplied along with its frequency, 20 log N). Outside the bandwidth the loop is too slow, and the output shows the VCO's own noise. So you choose the bandwidth where the two curves cross, like handing over from a steady but slow referee to a fast but nervous one.

Fractional-N lets N be non-integer by dithering the divider between integers (e.g. 138 and 139) in a pseudo-random pattern whose average is 138.8544. The dithering is itself phase noise, but a sigma-delta modulator pushes it to high offsets where the loop filter removes it. The price is a more demanding filter and some fractional spurs; the gain is a high reference frequency (less multiplication of PFD noise) and fine frequency steps.

A DDS skips feedback entirely: a counter (phase accumulator) steps through a sine table at a fixed clock, and a DAC outputs the samples. It can hop frequency instantly with micro-hertz resolution, but its spurs and top frequency are limited by the DAC.

## The math

### Level 1 — loop quantities
- PFD/charge pump: average current $i=K_\phi\,\theta_e$, $K_\phi=I_{CP}/2\pi$ A/rad.
- VCO: $\omega=\omega_0+K_{VCO}v_{tune}$, i.e. phase $\theta=K_{VCO}\int v\,dt$ → transfer $K_{VCO}/s$.
- Divider: $\theta_{div}=\theta_{VCO}/N$.
- Open loop: $G(s)=\frac{K_\phi K_{VCO}Z(s)}{Ns}$; closed loop from reference phase to output phase $N\frac{G}{1+G}$; from VCO noise to output $\frac{1}{1+G}$.
- Phase margin $\varphi=180°+\angle G(j\omega_c)$ at the crossover $|G(j\omega_c)|=1$; loop bandwidth ≈ $\omega_c$. The closed-loop −3 dB point is higher: 1.56/1.67/1.70 × f_c at PM 60/50/40° for the passive 3rd-order loop (verified in s15_pll_dynamics.py C; corrected 2026-10-13 from "≈ 1.2–1.5×").

### Level 1½ — the loop as "error × gain = correction", algebra only
- **Measure the error.** The PFD compares the divided VCO with the reference and finds the phase error θₑ. The charge pump turns it into an average current $I_{CP}\theta_e/2\pi$.
- **Turn the error into a correction.** The loop filter turns that current into a tuning voltage, and the VCO turns the voltage into a frequency change $\Delta f = K_V\Delta v$. The divider makes the comparison at $f_{VCO}/N$.
- **Stop when the error is gone.** The correction continues until θₑ averages zero, i.e. $f_{VCO} = N f_{ref}$. The loop bandwidth says how fast this happens.
- **Noise is multiplied too.** Inside the loop bandwidth the output copies the reference's phase wander multiplied by N, so its phase noise rises by 20 log N. Dividing the output by M lowers it by 20 log M. Outside the bandwidth the VCO's own noise shows.

*Worked number (verified, `tools/verify/s18b_level15_numbers.py`), using this page's ADF4351 plan.* With I_CP = 2.5 mA, each degree of error gives **6.94 µA** of average current. With K_V = 40 MHz/V, a 1 MHz move needs **25 mV** of tuning. The VCO at 3471.36 MHz from 25 MHz has 20 log(138.85) = **42.9 dB**; ÷8 subtracts 18.1 dB, so the net factor is 20 log(433.92/25) = 24.8 dB. A TCXO at −140 dBc/Hz at 1 kHz therefore gives **−115.2 dBc/Hz** at 433.92 MHz inside the loop. The full budget in the worked example adds the chip's flicker noise and reaches ≈ −112 dBc/Hz.

### Level 2 — derivations

**(a) Loop-filter synthesis.** The 2nd-order passive filter ($C_1$ in parallel with $R_2+C_2$) has
$$Z(s)=\frac{1+sT_2}{sA_0(1+sT_1)},\quad T_2=R_2C_2,\quad T_1=\frac{R_2C_1C_2}{C_1+C_2},\quad A_0=C_1+C_2 .$$
The loop phase is $-180°+\arctan\omega T_2-\arctan\omega T_1$, maximum at $\omega=1/\sqrt{T_1T_2}$. Setting that maximum at $\omega_c$ with value φ gives $\tan\varphi=\frac{\omega_c(T_2-T_1)}{1+\omega_c^2T_1T_2}=\frac{\omega_c(T_2-T_1)}{2}$ which with $T_2=1/(\omega_c^2T_1)$ solves to $T_1=(\sec\varphi-\tan\varphi)/\omega_c$. Then $|G(j\omega_c)|=1$ fixes $A_0$ [1 ch. 23–25]. Check A1: the synthesised filter hits 49.9 kHz and 50.00°.

**(b) Noise transfer.** A phase-noise source inside the loop at the reference/PFD/charge-pump/divider appears at the output multiplied by $N G/(1+G)$ (low-pass, gain N in band); the VCO's own noise by $1/(1+G)$ (high-pass); the loop-filter resistor's noise voltage $v_n=\sqrt{4kTR_2}$ is converted to phase by $K_{VCO}/s$ and then high-pass-shaped like the VCO: $L_{R}(f)=\frac12\left(\frac{K_{V,Hz}|v_{VCO}(f)|}{f}\right)^2|1/(1+G)|^2$. With a 40 MHz/V VCO the R2 contribution in the example is ≈ −141 dBc/Hz at 10–100 kHz (433.92 MHz output) — minor here, dominant for high-Kv, low-noise designs.

**(c) PLL figure of merit.** In band, the synthesizer's own noise normalised to 1 Hz PFD rate and N = 1 is $PN_{SYNTH}$ (a.k.a. FoM); at the output $L=PN_{SYNTH}+10\log f_{PFD}+20\log N$ [5]. Since $N=f_{out}/f_{PFD}$, $L=PN_{SYNTH}+20\log f_{out}-10\log f_{PFD}$: doubling $f_{PFD}$ improves in-band noise by 3 dB.

**(d) ΣΔ quantisation noise.** A MASH of order m produces a divider sequence $y=\text{frac}+(1-z^{-1})^mq$ with $q$ white, variance 1/12. The VCO-referred phase error is $2\pi\sum(y-\text{frac})$ = $2\pi(1-z^{-1})^{m-1}q$, whose two-sided PSD per Hz at sample rate $f_{PFD}$ is $\frac{(2\pi)^2}{12f_{PFD}}|2\sin(\pi f/f_{PFD})|^{2(m-1)}$ = $L(f)$. For m = 3 it grows 40 dB/decade; with f_PFD = 25 MHz it is −92.8 dBc/Hz at 1 MHz open loop (check D), attenuated by the closed-loop low-pass to ≈ −161 dBc/Hz at 1 MHz with the 50 kHz loop (at 433.92 MHz).

**(e) Leakage spurs.** Leakage $I_L$ must be replaced every PFD cycle by a short charge-pump pulse; that current waveform's fundamental at $f_{PFD}$ is $2I_L$, producing tuning ripple $v_1=2I_L|Z(f_{PFD})|$ and FM index $\beta=K_{V,Hz}v_1/f_{PFD}$; narrow-band FM spurs at $\pm f_{PFD}$ of $20\log(\beta/2)$ dBc (check E). Dead-zone/anti-backlash pulses and up/down current mismatch produce spurs in the same way with $I_L$ replaced by the mismatch charge; fractional spurs appear at offsets of $f_{PFD}\cdot\text{frac}$ harmonics and are layout- and modulus-dependent.

**(f) Leeson's model.** A feedback oscillator with loaded resonator Q $Q_L$, noise factor F, signal power $P_s$ and flicker corner $f_c$:
$$L(f_m)=10\log\left[\frac{FkT}{2P_s}\left(1+\left(\frac{f_0}{2Q_Lf_m}\right)^2\right)\left(1+\frac{f_c}{f_m}\right)\right]$$
[4]. Doubling $Q_L$ lowers the close-in $1/f^2$ region by 6 dB (check H). Integrated wideband VCOs have low Q (≈ 10–20) and compensate with multiple bands and high power; discrete VCOs with ceramic coaxial resonators ($Q$ ≈ 200–500) are 10–20 dB quieter.

### Level 3 — architectures and limits
- **Integer-N**: $f_{PFD}$ = channel spacing (e.g. 25 kHz), so N is huge and in-band noise poor (+20 log N); loop bandwidth ≤ f_PFD/10 → slow. Fine for fixed-frequency LO.
- **Fractional-N**: high $f_{PFD}$, fine steps; ΣΔ noise and fractional spurs must be handled (dither, MASH order, spur-avoidance frequency plans).
- **Offset/translation loops**, **multi-loop** and **PLL + DDS hybrids** (DDS as tunable reference) combine fine resolution with low noise.
- **VCO topologies**: LC cross-coupled (on-chip), Colpitts/Clapp/Hartley with varactors (discrete), ceramic-resonator and YIG oscillators; Kvco must be large enough to cover the band with margin but small to limit noise from the tuning line (loop-filter R and supply noise). Varactor tuning (C–V curve) makes Kvco vary across the band → loop bandwidth varies; integrated parts compensate $I_{CP}$ (the ADF4351 does [5]).
- **Pulling and pushing**: load changes (PA switching on) pull the VCO (ADF4351: 90 kHz into 2:1 VSWR open-loop [5]); supply changes push it (1 MHz/V). Buffer, regulate, and keep the loop bandwidth wide enough to correct during TX turn-on.
- **Jitter and ADC clocks**: RMS jitter $\sigma_t=\sqrt{2\int L(f)\,df}/(2\pi f_0)$ limits ADC SNR to $-20\log(2\pi f_{in}\sigma_t)$ (see [data converters](../05-analog-electronics/data-converters-adc-dac.md)).

### Level 3b — PLL dynamics, the sampling limit, measuring the loop, and special architectures
All numbers in this section come from `tools/verify/s15_pll_dynamics.py`. Its core is an **exact event-driven simulator**: a tri-state PFD and ideal charge pump drive a state-space loop filter and a VCO; the state is propagated between edges with a matrix exponential, and divider edges are found by root-finding. It contains no averaging and no linearisation. The loop is the page's ADF4351 example: 50 kHz / 50°, C1 2.66 nF, C2 17.4 nF, R2 503 Ω, without the R3–C3 pole unless stated.

**(g) PLL vs DLL.** A *PLL* controls an oscillator's **frequency**, so phase is the integral of the control signal. That is why it can multiply (f_out = N f_ref), why it is at least type 1, and why the VCO's own jitter *accumulates* between corrections. A *DLL* controls the **delay** of a voltage-controlled delay line (VCDL) that the reference itself passes through. It locks the delay to one reference period, or a fraction of it, so that taps give evenly spaced phases. The control-to-phase path has no integrator, so the loop is first-order and unconditionally stable. Each output edge is a reference edge plus a single pass through the line, so delay-line jitter does **not** accumulate. On the other hand, a DLL cannot synthesise a new frequency without extra edge-combining logic, and it passes reference jitter straight through [10]. In the script's model (check H), with identical per-period random jitter σ, a VCO in a first-order loop with crossover f_c settles at an RMS edge error of $\sigma/\sqrt{2\beta-\beta^2}$, $\beta=2\pi f_c/f_{ref}$. That is 1.37σ at f_ref/20 and 2.87σ at f_ref/100, against 1.00σ for the DLL.
- **Where you meet them.** MCU clock trees (STM32 and similar) use PLLs, because they must multiply a crystal. FPGA clock managers come in both kinds: older Xilinx DCMs were DLL-based (deskew, phase shift, simple multiply/divide by edge synthesis), while 7-series MMCM/PLL blocks are true PLLs with VCOs. DDR interfaces use DLLs for DQS/DQ phase alignment.
- **Do not confuse it with the GNSS "DLL".** The code-tracking delay-lock loop in a GNSS receiver ([GNSS tracking](../21-gnss/gnss-receiver-architecture-acquisition-tracking.md)) aligns a replica PRN code with early/late correlators. It shares the name and the idea (lock a delay, not a frequency), but it is a DSP loop.

**(h) The sampled-loop (Gardner) limit.** The PFD compares phase only once per reference period T, so a CP-PLL is a sampled system. Gardner's analysis uses the simplest filter: a series R–C (no C1). Define $K=I_{CP}K_{VCO}/(2\pi N)$ (with $K_{VCO}$ in rad/s/V), $a=KTR$ and $b=KT^2/C$. The linearised one-step map is $e_{n+1}=(1-a-b)e_n-u_n$, $u_{n+1}=u_n+be_n$, with characteristic polynomial $z^2-(2-a-b)z+(1-a)$. The Jury test reduces to $2a+b<4$. Since $\omega_n^2=K/C$, $\tau_2=RC$ and $\omega_i=2\pi/T$, this is exactly **Gardner's 1980 condition** $\omega_n^2<\omega_i^2/[\pi(\pi+\omega_i\tau_2)]$ [11] (check A1). At ζ = 0.707 it gives $\omega_nT<1.035$, i.e. $f_n<0.165\,f_{ref}$.
- **Faithful-reporting caveat.** The loop is only *piecewise* smooth. When the divider lags, the speed-up during the UP pulse moves the very edge that ends the pulse, so straight linearisation is not exact. Kuznetsov et al. [12] analyse the exact discrete model and find that the locked state is stable for $b<4$, provided $a<1$. In their notation β = b/2 < 2 and α = a < 1; a ≥ 1 is *local VCO overload*, where the divided frequency is driven to ≤ 0 during a DN pulse. The exact simulator sides with them: points that violate Gardner's inequality but satisfy b < 4 decay (a = 0.3, b = 3.6 or 3.9; a = 0.9, b = 2.4), and b = 4.3 grows by about 10⁴ in 300 cycles (check A2). At b = 3 (their degenerate β = 3/2 point, where period-3 cycles merge with lock), decay is very slow. For ζ = 0.707 the binding exact limit is therefore overload, a < 1, i.e. $\omega_nT<0.71$.
- **For design, none of this binds.** Real loops use C1 (plus R3–C3), and the practical rule f_c ≤ f_ref/10 sits far inside every version of the limit.
- **What sampling costs a normal 3rd-order loop.** The impulse-sampled loop gain is the alias sum $L(e^{j\omega T})=\sum_kG(j(\omega+k\omega_{ref}))$ [13]. Applied to the Banerjee 50° design (check A3), the phase margin becomes:

| f_c / f_ref | PM with sampling | step overshoot: continuous model | impulse-invariant model | exact PFD sim |
|---|---|---|---|---|
| 1/100 | 50.0° | 28.1 % | 28.1 % | 28.1 % |
| 1/30 | 49.6° | 28.1 % | 28.3 % | 28.3 % |
| 1/10 | 45.9° | 28.1 % | 30.9 % | 30.9 % |
| 1/5 | 32.3° | 28.1 % | 63.0 % | 63.0 % |
| 1/4 | 18.6° | 28.1 % | 124 % | 124 % |

  The f_ref/10 rule therefore costs about 4° of phase margin. Above f_ref/5 the continuous model is badly wrong, while the impulse-invariant (z-domain) model stays exact. (Overshoot is taken on the cycle-averaged frequency. The tuning voltage sampled at the edges carries a ≈ 10 % per-cycle sawtooth from the R2–C1 path.)

**(i) Lock time: linear settling, cycle slips and slew.** In the linear regime the loop settles exponentially at a rate set by ζω_n, so the time to reach a tolerance grows only with ln(Δf/tol). For a 2nd-order loop the error envelope is $\Delta f\,e^{-\zeta\omega_nt}/\sqrt{1-\zeta^2}$, so $t_{lock}\approx\ln\!\big(\Delta f/(\text{tol}\sqrt{1-\zeta^2})\big)/(\zeta\omega_n)$ [1], [2]. A tri-state PFD stays sign-correct beyond ±2π but **slips cycles**: its average output saturates between I_CP/2 and I_CP. The pump-saturated slew rate is $K_VI_{CP}/(C_1+C_2)$, which is 5.0 MHz/µs here. The exact simulator gives these times to |Δf_VCO| < 1 kHz (check B):

| Loop | VCO hop | linear model | exact PFD sim | cycle slips |
|---|---|---|---|---|
| 50 kHz | 1 MHz | 29.7 µs | 29.8 µs | 0 |
| 50 kHz | 10 MHz | 40.4 µs | 41.1 µs | 0 |
| 50 kHz | 60 MHz | 45.8 µs | 51.8 µs | 1 |
| 10 kHz | 3 MHz | 155 µs | 155 µs | 0 |
| 10 kHz | 30 MHz | 220 µs | **409 µs** | 23 |

  The 34 µs in the TL;DR is the same 1 MHz hop with the R3–C3 pole (PM ≈ 43°). Slips begin when the linear peak phase error approaches 2π, which scales as $\Delta f/(N f_n)$. Narrow loops and big hops therefore slip, and their lock time stops following the linear model. Fixes:
  - switched-bandwidth "fast-lock": raise I_CP and switch in a smaller R2 to keep the PM (the ADF4351 does this through its SW pin; it also has a cycle-slip-reduction mode [5]);
  - pre-steer VTUNE;
  - cut the hop size with a VCO band select.

  In integrated-VCO parts the band-select calibration (tens of µs) usually dominates anyway [5].

**(j) Measuring the loop bandwidth on the bench.** Know what each method reads before you start. For the 50 kHz / 50° design, the closed loop |H| has its −3 dB point at **83 kHz = 1.67 f_c** and peaks by 2.6 dB at 0.63 f_c. The VCO-noise transfer |1/(1+G)| peaks by 2.6 dB at **1.59 f_c**, which is the "shoulder" or hump on a phase-noise plot. Across PM 40/50/60° the −3 dB point is 1.70/1.67/1.56 f_c (check C). The rule of thumb "f_3dB ≈ f_c" is therefore optimistic by about 1.6×.
  1. **Phase-noise plot.** Read the hump frequency and divide by ≈ 1.6 to estimate f_c. Hump height grows as the PM falls (closed-loop peaking 1.7/2.6/4.0 dB at 60/50/40°).
  2. **Reference FM sweep.** Drive the REF input from a generator with small FM at f_m and read the output deviation with an analyser's FM demodulator (or with Bessel nulls). Deviation_out/(N·deviation_in) = |H(f_m)| directly. Keep the deviation small enough that the PFD stays linear.
  3. **Frequency-step response.** Toggle N (or the FRAC word) and watch frequency against time (modulation-domain or analyser FM demod). Then:
     - PM from the overshoot: 39.5/28.1/18.8 % ↔ 40/50/60°;
     - $f_c\approx0.47/t_{peak}$ from the time to the first peak (0.46–0.51 across 40–60°, scale-invariant).

     Pitfall: forcing the textbook 2nd-order type-2 formulas onto a 3rd-order loop's step reads ζ = 0.53 and f_3dB = 75 kHz instead of 83 kHz.
  4. **Probing VTUNE.** Probing it directly adds probe capacitance to C3/C1, and the trace shows the per-cycle sawtooth. Use a ≥ 1 MΩ, low-capacitance probe through a series resistor, or avoid the method.

**(k) Two-point modulation.** If the modulation enters only through the divider (fractional-N word), the output follows it through H(s): a low-pass that rounds off data above the loop bandwidth. If it enters only at VTUNE, it is high-passed by 1 − H, and the loop removes long runs of 1s. Applying both, the divider path plus g × the ideal VTUNE amplitude, gives an output of
$$\frac{\Delta f_{out}}{\Delta f_{wanted}}=H+g(1-H)=1+(g-1)(1-H),$$
which is flat for g = 1. A gain mismatch leaves an error (g − 1) only *above* the loop bandwidth; DC remains exact (check D). With g = 1.05 the response is −0.10/+0.52 dB, and with g = 0.90 it is −1.13/+0.21 dB. In a 2-FSK test at 100 kbit/s NRZ through the 50 kHz loop:

| Scheme | worst bit-centre deviation |
|---|---|
| single-point (divider only) | 69 % of nominal |
| two-point, matched | 100 % |
| two-point, g = 1.05 | 98.5 % |

K_VCO varies with tuning voltage and temperature, so practical designs calibrate g. The alternative is digital pre-emphasis of the divider modulation by 1/H [14], [15]. For context see [transmitter architectures](transmitter-architectures.md) and [modulator circuits](modulator-and-detector-circuits.md).

**(l) FMCW chirps through a PLL.** A linear ramp at R Hz/s is a quadratic phase input. A type-2 loop (VCO integrator plus the filter's C) tracks it with **zero frequency error** but a constant phase error. Using the filter's low-frequency asymptote $Z\approx1/(sA_0)$,
$$\theta_{e,ss}=\frac{2\pi R\,A_0}{K_\phi K_{VCO}}\quad(\text{divider-referred, }K_{VCO}\text{ in rad/s/V}),$$
which is 0.126 rad for 100 MHz/ms at the 3.47 GHz VCO with this loop (check E; the formula and simulation agree to 4 digits). The cost is at the **chirp start**: the frequency error peaks at ≈ 270 kHz (≈ R/(2πf_c)) and takes 26 µs to fall below 1 kHz. Use that time as a blanking interval, or remove it with one of these:
- feed-forward of the ramp into VTUNE (two-point again);
- a type-3 loop (an extra integrator, harder to stabilise);
- a triangular ramp, which avoids the sawtooth's big flyback step.

Ramp linearity is set by how much of this transient falls inside the processed sweep ([FMCW radar](../11-radar/fmcw-radar.md)).

**(m) Offset (translation) PLL.** Mix the VCO with a fixed offset LO and phase-lock the low IF to the reference with N ≈ 1, instead of dividing the VCO by a large N. The PFD/CP floor is then multiplied by 20 log N_IF ≈ 0 dB instead of 20 log N. For a 433.92 MHz output mixed with a 410 MHz LO and a 23.92 MHz IF locked at N = 1, the in-band chip floor is −221 + 10 log(23.92 MHz) = **−147 dBc/Hz**, against −122 dBc/Hz for the direct ADF4351 plan (check F). The offset LO's phase noise now appears 1:1 at the output, and the mixer's image and spurs must be filtered out. The scheme pays off when the offset LO can be a fixed, very clean source (crystal-multiplied, SAW, or a narrow-loop integer-N), as in GSM translation-loop transmitters and test-equipment synthesisers.

**(n) Charge-pump non-linearity and fractional spurs/noise.** With up/down current mismatch δ, the charge per cycle is $Q=I_{CP}\,\Delta t\,(1\pm\delta/2)$. Equivalently, $Q\propto\Delta t+(\delta/2)|\Delta t|$: a linear term plus an absolute-value term [16]. The |·| term intermodulates the ΣΔ quantisation noise, which is shaped to high offsets, and **folds** part of it back in band. In the script (check G) the MASH 1-1-1 sequence at 25 MHz PFD gives the following VCO-referred, open-loop, 10–100 kHz levels:

| CP up/down mismatch | in-band ΣΔ noise | change |
|---|---|---|
| 0 (ideal) | −144 dBc/Hz | — |
| 1 % | −110 dBc/Hz | +34 dB |
| 5 % | −96 dBc/Hz | +48 dB |
| 10 % | −90 dBc/Hz | +54 dB |

At 1 % the folded noise is already close to the ADF4351's −104 dBc/Hz in-band floor, and at 5 % it exceeds it. For deterministic fractions the same non-linearity produces **fractional spurs**. The cure is to keep the CP in one region. A constant **offset/bleed current** forces a static phase offset, so every pulse has the same polarity and |Δt| = Δt: in the model the folded noise returns to the ideal level. Vendors expose this (e.g. the ADF5355/ADF5356 "bleed current" setting [17]). Other cures are CP current matching or calibration, and folded-noise cancellation [18]. The cost is a slightly higher reference spur, because the offset charge is replaced every cycle.

## Design equations & rules of thumb

| Quantity | Equation | Notes / example |
|---|---|---|
| Open loop | $G=K_\phi K_VZ/(Ns)$ | $K_\phi=I_{CP}/2\pi$ |
| 2nd-order passive filter | $T_1=\frac{\sec\varphi-\tan\varphi}{\omega_c}$, $T_2=\frac1{\omega_c^2T_1}$, $A_0$ as above | Banerjee [1] |
| Phase margin | 45–60° typical | 50° → ≈ 20–30 % overshoot |
| Loop bandwidth | ≤ f_PFD/10 (integer), set by noise optimum (frac-N) | 50 kHz at 25 MHz PFD |
| In-band noise | $PN_{SYNTH}+10\log f_{PFD}+20\log N$ | ADF4351: −221; LMX2594: −236 |
| Flicker | $PN_{1/f}+10\log(10\text{k}/f)+20\log(f/1\text{G})$ | ADF4351: −116/−118 |
| Divide-by-M output | $L_{out}=L_{VCO}-20\log M$ (until the divider floor) | ÷8: −18.1 dB |
| ΣΔ (MASH-3) noise | $\frac{(2\pi)^2}{12f_{PFD}}(2\sin\frac{\pi f}{f_{PFD}})^4$ | needs 3rd/4th-order loop filter |
| Leakage spur | $20\log(K_VI_L|Z(f_{PFD})|/f_{PFD})$ | high f_PFD → negligible |
| Jitter | $\sigma_t=\sqrt{2\int L\,df}/(2\pi f_0)$ | 248 fs in the example |
| DDS resolution / spur | $f_{clk}/2^N$; ≤ −6.02P dBc | AD9850-class 32-bit |
| DDS amplitude | sinc($f/f_{clk}$) | −2.4 dB at 0.4 f_clk |
| Leeson close-in | ∝ $(f_0/2Q_Lf_m)^2$ | 2× Q → −6 dB |
| Closed-loop −3 dB | 1.56–1.70 × f_c (PM 60–40°) | 83 kHz for the 50 kHz/50° loop |
| Sampled-loop PM loss | alias sum $\sum_kG(j(\omega+k\omega_{ref}))$ | −4° at f_ref/10, −18° at f_ref/5 |
| Gardner limit (series RC) | $2a+b<4$ ⇔ $\omega_n^2<\omega_i^2/[\pi(\pi+\omega_i\tau_2)]$ | ζ 0.707: f_n < 0.165 f_ref (linearised; exact: b < 4, a < 1) |
| Slew (cycle-slipping) | $df/dt=K_VI_{CP}/(C_1+C_2)$ | 5 MHz/µs in the example |
| Step-response bench fit | $f_c\approx0.47/t_{peak}$; overshoot 39/28/19 % ↔ PM 40/50/60° | passive 3rd-order loop |
| Two-point modulation | $H+g(1-H)$; error $(g-1)(1-H)$ | 5 % mismatch → +0.5 dB above BW |
| Ramp phase error (type 2) | $2\pi RA_0/(K_\phi K_{VCO})$ | 0.126 rad at 100 MHz/ms |
| PLL vs DLL jitter | PLL: $\sigma/\sqrt{2\beta-\beta^2}$, β = 2πf_c/f_ref; DLL: σ | 2.9σ vs 1σ at f_ref/100 |
| CP mismatch δ | $Q\propto\Delta t+(\delta/2)|\Delta t|$ | 1 % → +34 dB in-band ΣΔ noise |

## Worked examples

### Example 1 — ADF4351 as a 433.92 MHz LO (or low-power transmitter)
- Plan: 25 MHz reference, $f_{PFD}$ = 25 MHz (≤ 32 MHz frac-N limit [5]); VCO 3471.36 MHz (inside 2.2–4.4 GHz), output divider ÷8 → 433.92 MHz; N = 138.8544 (INT 138, FRAC/MOD = 0.8544 → e.g. MOD 625, FRAC 534). Output power −4 to +5 dBm [5].
- Loop: $I_{CP}$ = 2.5 mA (of 0.31–5 mA), $K_V$ = 40 MHz/V, 50 kHz / 50°: C1 2.66 nF (2.7 nF), C2 17.4 nF (18 nF), R2 503 Ω (510 Ω); optional R3 1 kΩ, C3 290 pF (270 pF) → PM ≈ 43°, 33 dB more rejection at 25 MHz.
- Predicted phase noise at 433.92 MHz: ≈ −112 dBc/Hz at 1 kHz (reference and PLL chip together, not TCXO-limited: the assumed −140 dBc/Hz @ 1 kHz, 25 MHz TCXO alone gives −115.2 dBc/Hz at 433.92 MHz, +24.8 dB = 20 log(433.92/25), i.e. 42.9 dB to the 3.47 GHz VCO minus 18.1 dB for ÷8; the ADF4351's 1/f noise adds an equal −115.3 dBc/Hz and its in-band floor −122.2 dBc/Hz, so the sum is −111.8 dBc/Hz, `rfckt_pll.py` B), −117 at 10 kHz, −123 at 100 kHz, −152 at 1 MHz; 248 fs RMS jitter (1 kHz–10 MHz). The data sheet's measured −100 dBc/Hz at 3 kHz from 2111 MHz [5] scales to ≈ −114 dBc/Hz at 434 MHz — consistent.
- Harmonics: the ADF4351 output has 2nd/3rd harmonics of only −19/−13 dBc (fundamental VCO output) [5] — as an LO for a DBM that is often acceptable; as a transmitter it needs a low-pass filter ([filters](rf-filters-lc-saw-baw-cavity-microstrip.md)).

### Example 2 — Why 433 MHz from 3.47 GHz ÷ 8 is quieter than a 433 MHz VCO locked directly
Dividing by 8 lowers phase noise by 18 dB (phase deviation divides by 8); the high-Q-per-area on-chip VCO at 3.5 GHz plus division beats a low-frequency on-chip VCO. The in-band PLL floor also scales by 20 log N at the VCO and then −18 dB at the output, so it is equivalent to a PLL whose N counted 433.92/25.

### Example 3 — Choosing the loop bandwidth
From the budget (script B): at 10 kHz bandwidth the VCO noise dominates from 10 to 100 kHz (L(10k) = −101 dBc/Hz), jitter 600 fs; at 400 kHz the PLL floor dominates out to 400 kHz and the loop starts to pass the ΣΔ noise, jitter 466 fs; 50 kHz gives the minimum ≈ 248 fs. For a LoRa receiver LO, *reciprocal mixing* matters more than jitter: a blocker 1 MHz away at −30 dBm mixes the LO's −152 dBc/Hz noise into the channel: −30 − 152 + 10 log(125 kHz) = −131 dBm — just below a SF12 signal at −137 dBm; hence the need for good far-out VCO noise ([receiver architectures](receiver-architectures.md)).

### Example 4 — ΣΔ noise at 25 MHz PFD
Open loop, MASH-3 at 25 MHz: −92.8 dBc/Hz at 1 MHz offset (VCO-referred), rising 40 dB/decade. After the 50 kHz 3rd-order loop and ÷8: −156 dBc/Hz at 100 kHz, −161 at 1 MHz, −170 at 3 MHz — below the VCO contribution everywhere. With a 400 kHz loop the same noise would be ≈ 41 dB higher at 1 MHz (−120 dBc/Hz; computed with the same script functions) — why wide loops need higher-order filters or lower-order modulators.

### Example 5 — Si5351 for a 10.7 MHz BFO/second LO
25 MHz crystal, PLL to 600 MHz (integer ×24), multisynth 56 + 8/107 → 10.700 000 MHz exactly (script G). Si5351 outputs are CMOS square waves (rich in odd harmonics — filter if used for a mixer that is sensitive to LO harmonics) with jitter of tens of ps, good for HF and IF LOs, not for a low-noise UHF LO [8].

### Example 6 — DDS for FM/FSK modulation or a sweep generator
AD9850-class DDS (125 MHz clock, 32-bit FTW): 29 mHz resolution; FTW(10.7 MHz) = 367 649 201; with a 14-bit (or 12-bit) phase-to-amplitude path, truncation spurs ≤ −84 (−72) dBc; output sinc droop −2.4 dB at 50 MHz; an anti-alias LPF below ≈ 0.4 f_clk removes images at f_clk ± f_out.

### Example 7 — Hopping and chirping the ADF4351 loop (Level 3b numbers)
- *Hop*: 1/10/60 MHz VCO hops lock to 1 kHz in 29.8/41.1/51.8 µs (exact PFD simulation, 50 kHz loop, no R3–C3); the 60 MHz hop slips one cycle. With a 10 kHz loop, a 30 MHz hop slips 23 cycles and takes 409 µs, against 220 µs linear. To hop fast, keep the loop wide (fast-lock) and the hops small, or pre-steer the tune voltage.
- *Measure it*: expect the phase-noise hump at ≈ 80 kHz, a closed-loop −3 dB of 83 kHz, and a 28 % overshoot with its peak 9.4 µs after a frequency step (0.47/9.4 µs = 50 kHz).
- *FSK*: 100 kbit/s 2-FSK through the divider alone keeps only 69 % of the deviation at the worst bit centre; two-point with a 5 % VTUNE-gain error keeps 98.5 %.
- *Chirp*: 100 MHz/ms on the VCO gives a 0.126 rad steady phase lag, a 270 kHz error at chirp start, and < 1 kHz error after 26 µs. Blank that part of the sweep.

## Practical notes
- **Loop filter components:** C0G/film for C1/C3 (piezoelectric X7R can microphonically modulate the VCO), low-leakage capacitors near the charge pump, keep the filter physically close to CP and VTUNE pins, guard the VTUNE trace (high impedance, sensitive).
- **Supplies:** the VCO supply (VVCO) is highly sensitive: use a low-noise LDO (≤ 10 nV/√Hz class) and RC filtering; supply noise × pushing (1 MHz/V) becomes FM.
- **Reference:** a TCXO/OCXO's phase noise is multiplied by 20 log(f_out/f_ref); a clean reference matters more than anything for close-in noise. Square-wave references need slew rate.
- **Lock detect and hop time:** integrated-VCO parts spend tens of µs on band selection; for fast hopping use "fast lock" modes (temporarily higher I_CP and lower R2) or pre-calibrated bands.
- **Debug:** a spectrum analyser with a phase-noise mode or an SDR can show loop peaking (a hump at the loop bandwidth → too little phase margin), spurs at f_PFD and fractional spurs.
- **ADIsimPLL / TI PLLatinum Sim** model all of the above with vendor data; use them for final design.

## Common mistakes & misconceptions
- *"Wider loop bandwidth is always better."* It suppresses VCO noise but passes more reference, PFD and ΣΔ noise and reduces spur filtering.
- *"The PLL output is as clean as the crystal."* Only within the loop bandwidth, and multiplied by 20 log(f_out/f_ref).
- *"Kvco from the data sheet is a constant."* It varies with tuning voltage and band; check phase margin at the extremes.
- *"Fractional-N is noisier than integer-N."* Usually the opposite in band, because f_PFD is much higher; the cost is spurs and ΣΔ noise far out.
- *"A 3rd-order loop is unstable."* A 3rd-order PLL (2nd-order filter) is conditionally stable only in the sense of phase margin; design with 45–60° and it is fine.
- *"A DDS is spur-free because it's digital."* Phase truncation, DAC nonlinearity and images create spurs; −6.02·P dBc bounds the first.
- *"Dividing a noisy signal can't make it cleaner."* Division by M reduces phase noise by 20 log M (down to the divider's own floor).
- *"A DLL is just a PLL with a delay line."* A DLL adjusts delay, not frequency: it is first-order, does not accumulate jitter, and cannot multiply frequency by itself (Level 3b g).
- *"The loop bandwidth is where the phase-noise hump is."* The hump (VCO-noise peaking) is at ≈ 1.6 f_c and the closed-loop −3 dB point is ≈ 1.67 f_c for 50° PM; neither equals the open-loop crossover.
- *"Gardner's limit says the loop goes unstable at f_ref/6."* That figure comes from a linearised series-RC model, and the exact piecewise-smooth model is looser. What matters in practice is the PM lost to sampling: about 4° at f_ref/10 and 18° at f_ref/5.
- *"A PFD can't lose lock, so big hops are just slower linear settling."* It cannot false-lock, but it slips cycles and slews at a rate set by I_CP/(C1+C2), so big hops take much longer than the linear model predicts.
- *"Modulating the fractional-N word is enough for any data rate."* The loop low-passes it; above the loop bandwidth you need two-point modulation or pre-emphasis.
- *"Charge-pump mismatch only causes reference spurs."* In fractional-N it also folds ΣΔ noise into the band (+34 dB at 1 % in the model); bleed/offset current is the standard cure.

## How to simulate / verify
- `tools/verify/s15_pll_dynamics.py`: exact event-driven PFD/CP simulator; Gardner vs exact sampled-loop stability; PM vs f_c/f_ref (alias sum, impulse-invariant, exact sim); lock time with cycle slips; bench bandwidth signatures; two-point modulation and FSK eye; FMCW ramp error; offset PLL floor; CP-mismatch noise folding and the bleed cure; PLL vs DLL jitter accumulation (≈ 15 s).
- `tools/verify/rfckt_pll.py`: loop-filter synthesis and check, 3rd pole, full phase-noise budget with jitter vs bandwidth (ADF4351 data), lock-time step response, MASH 1-1-1 simulation vs closed form, leakage-spur estimates, DDS truncation spurs and sinc, Si5351-style fraction search, Leeson.
- Vendor tools: ADIsimPLL (ADI), PLLatinum Sim (TI), Skyworks ClockBuilder for Si5351.
- Measurement: phase-noise analyser or spectrum analyser (dBc/Hz with RBW/noise-marker corrections; see [phase-noise measurement](../17-test-measurement/phase-noise-measurement.md)).

## Open questions / gaps
- The reference TCXO phase-noise profile in the budget is an assumed typical curve, not a specific part; replace with the actual TCXO data.
- ADF4351 VCO noise at 3.47 GHz uses the 3.3 GHz data-sheet row; close-in (1 kHz) value is extrapolated.
- Fractional *spurs* (as opposed to ΣΔ noise) are not modelled numerically. Level 3b(n) models the CP-mismatch mechanism for noise folding, but the spur levels depend on MOD, dithering and layout.
- The CP-mismatch folding numbers are open-loop and VCO-referred, from an idealised linear + |x| model. They exclude dead-zone and turn-on transients and are not calibrated against a measured part.
- Gardner vs Kuznetsov: the event simulator supports the exact b < 4 result at the points tested; the full (a, b) map was not swept.
- LMX2594 figures are from TI's product summary, not a full data-sheet read.

## Sources
1. D. Banerjee, *PLL Performance, Simulation, and Design*, 5th ed., Dog Ear Publishing / Texas Instruments (free PDF), 2017 — loop-filter design equations (2nd/3rd/4th order passive), noise sources, spurs, lock time. (textbook)
2. W. F. Egan, *Phase-Lock Basics*, 2nd ed., Wiley-IEEE, 2008 — loop dynamics and noise transfer. (textbook)
3. B. Razavi, *RF Microelectronics*, 2nd ed., 2011, ch. 8–10 (oscillators, PLLs, integer-/fractional-N synthesizers, ΣΔ). (textbook)
4. D. B. Leeson, "A simple model of feedback oscillator noise spectrum," *Proc. IEEE*, 54(2), pp. 329–330, Feb. 1966. (peer-reviewed)
5. Analog Devices, *ADF4351 Wideband Synthesizer with Integrated VCO* data sheet rev. 0: PFD 32 MHz (frac-N)/45 MHz (int-N), I_CP 0.312–5 mA, K_V 40 MHz/V, PN_SYNTH −220/−221 dBc/Hz, PN1_f −116/−118 dBc/Hz, in-band formula, VCO open-loop noise, harmonics −19/−13 dBc, PFD spurs −80 dBc, pulling 90 kHz, pushing 1 MHz/V. https://www.analog.com/media/en/technical-documentation/data-sheets/adf4351.pdf (datasheet; read via pdftotext)
6. Texas Instruments, *LMX2594 15-GHz Wideband PLLatinum RF Synthesizer* product page/data sheet summary (10 MHz–15 GHz, FoM −236 dBc/Hz, 1/f −129 dBc/Hz, PFD up to 300 MHz frac / 400 MHz int). https://www.ti.com/product/LMX2594 (datasheet summary)
7. T. A. D. Riley, M. A. Copeland, T. A. Kwasniewski, "Delta-sigma modulation in fractional-N frequency synthesis," *IEEE J. Solid-State Circuits*, 28(5), pp. 553–559, May 1993. (peer-reviewed; ΣΔ noise model)
8. Silicon Labs (Skyworks), *Si5351A/B/C-B* data sheet and AN619 (VCO 600–900 MHz, multisynth ratios 8 + 1/1 048 575 to 900, outputs to 200 MHz; R dividers to ≈ 2.5 kHz). https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-sheets/Si5351-B.pdf (datasheet; via summaries)
9. H. T. Nicholas, H. Samueli, "An analysis of the output spectrum of direct digital frequency synthesizers in the presence of phase-accumulator truncation," *Proc. 41st Annual Frequency Control Symposium*, 1987, pp. 495–502. (peer-reviewed; −6.02P bound)
10. J. G. Maneatis, "Low-jitter process-independent DLL and PLL based on self-biased techniques," *IEEE J. Solid-State Circuits*, 31(11), pp. 1723–1732, Nov. 1996 (bibliographic details checked via citing documents). (peer-reviewed; DLL vs PLL structure and jitter)
11. F. M. Gardner, "Charge-pump phase-lock loops," *IEEE Trans. Commun.*, COM-28(11), pp. 1849–1858, Nov. 1980. (peer-reviewed; linearised sampled-loop stability limit, re-derived here)
12. N. V. Kuznetsov, A. S. Matveev, M. V. Yuldashev, R. V. Yuldashev, "Nonlinear analysis of charge-pump phase-locked loop: the hold-in and pull-in ranges," *IEEE Trans. Circuits Syst. I*, 68(10), pp. 4049–4061, 2021; arXiv:2005.00864 (read). (peer-reviewed; exact discrete model, stability for β < 2 with α < 1, overload, critique of linearisation)
13. J. P. Hein, J. W. Scott, "z-domain model for discrete-time PLL's," *IEEE Trans. Circuits Syst.*, 35(11), pp. 1393–1400, 1988. (peer-reviewed; impulse-invariant model of the sampled loop)
14. M. H. Perrott, T. L. Tewksbury, C. G. Sodini, "A 27-mW CMOS fractional-N synthesizer using digital compensation for 2.5-Mb/s GFSK modulation," *IEEE J. Solid-State Circuits*, 32(12), pp. 2048–2060, Dec. 1997. (peer-reviewed; pre-emphasis alternative to two-point modulation)
15. US 7 579 922, "Two-point modulation polar transmitter architecture and method for performance enhancement" (patent; two-point gain matching to ≈ 5 % with calibration). (patent — practice)
16. B. Razavi, "An alternative analysis of noise folding in fractional-N synthesizers," *Proc. IEEE ISCAS*, 2018 (UCLA copy: https://www.seas.ucla.edu/brweb/papers/Conferences/BR_ISCAS_18.pdf). (peer-reviewed; linear + absolute-value CP model)
17. Analog Devices, AN-1460 *Upgrading from the ADF5355 to the ADF5356* (bleed current/polarity register). https://www.analog.com/en/resources/app-notes/an-1460.html (app note)
18. R. Gaied, E. Hegazi, "Charge-pump folded noise cancelation in fractional-N phase-locked loops," *IEEE Trans. Circuits Syst. II*, 2014, doi:10.1109/TCSII.2014.2319691. (peer-reviewed; folded-noise cancellation)
