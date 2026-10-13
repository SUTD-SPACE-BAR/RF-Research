---
title: Mixers (diode, Gilbert, passive FET, spurs, image rejection, IQ, harmonic and subsampling mixers)
domain: 06-rf-circuits
slug: mixers
tags: [mixer, frequency-conversion, double-balanced-mixer, diode-ring, gilbert-cell, passive-mixer, conversion-loss, lo-drive, isolation, ip3, spurious, spur-chart, half-if, image-rejection, hartley, weaver, iq-mixer, iq-imbalance, harmonic-mixer, apdp, subsampling, lptv, conversion-matrix, noise-folding, cyclostationary, n-path, tayloe, quadrature-sampling-detector, qsd, softrock, mixer-first]
prerequisites:
  - ../00-math-foundations/complex-numbers-and-phasors.md
  - ../00-math-foundations/fourier-series-and-transform.md
  - ../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md
  - baluns-and-rf-transformers.md
related:
  - receiver-architectures.md
  - transmitter-architectures.md
  - vco-and-pll-synthesizers.md
  - frequency-multipliers-dividers.md
  - ../14-sdr-dsp/iq-complex-baseband.md
  - ../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md
  - ../18-components-parts/mixers-plls-vcos-parts.md
  - ../11-radar/fmcw-radar.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Mixers

## Questions this page answers
- How does multiplying two sine waves shift a signal in frequency, and why do I get both sum and difference?
- Why is a diode double-balanced mixer's conversion loss about 6 dB, and what is the theoretical minimum?
- What do "Level 7", LO drive, isolation and IP3 mean on a Mini-Circuits mixer data sheet?
- What is a spur chart, and which m × n products hurt a 433 MHz receiver with a 10.7 MHz IF?
- What is the image frequency and the half-IF spur?
- How does an image-reject (Hartley) or IQ mixer cancel the image, and how much imbalance can I tolerate?
- What is a Gilbert cell, and what limits its linearity?
- What are passive FET mixers and why are they used in modern CMOS radios?
- What is a harmonic mixer, and why does an anti-parallel diode pair mix with 2 × LO?
- Can I "mix" by sampling (subsampling), and what does it cost in noise?
- What is a conversion matrix, and why is a mixer a linear periodically time-varying (LPTV) circuit?
- Why does a passive switching mixer fold noise from 3·LO, 5·LO … into its output?
- How does a Tayloe (quadrature sampling) detector reach < 1 dB conversion loss, and what sets its bandwidth?
- Why does a 4-path mixer respond at 3·LO with the sidebands swapped?

## TL;DR
- A mixer multiplies the RF by an LO. With a sinusoidal LO, $\cos\omega_R t\cos\omega_L t=\frac12[\cos(\omega_R-\omega_L)t+\cos(\omega_R+\omega_L)t]$. Practical mixers **switch** (commutate) the signal with a square-wave LO: the IF amplitude is $2/\pi$ of the RF → **3.92 dB ideal conversion loss** (SSB); real diode DBMs are 5–7 dB. Because the switching waveform contains odd LO harmonics, the mixer also converts RF near 3·LO (−9.5 dB relative), 5·LO (−14 dB) … (verified).
- **Every mixer converts two RF bands to the same IF**: the wanted $f_{LO}\pm f_{IF}$ and its **image** $f_{LO}\mp f_{IF}$. For 433.92 MHz with a 10.7 MHz IF and low-side LO (423.22 MHz) the image is 412.52 MHz; with high-side LO, 455.32 MHz. Close-in higher-order spurs are the **2×2 "half-IF"** response at $f_{RF}\mp f_{IF}/2$ (428.57 MHz, only 5.35 MHz away) and 3×3 responses at ±IF/3 — they must be rejected by the RF pre-selector or by mixer balance (spur chart computed in the script).
- **Diode DBMs** (ring + two baluns) are passive, broadband, need LO power (Level 7 = +7 dBm, Level 17, Level 23), give ≈ 30 dB LO–RF isolation at the top of their range, NF ≈ conversion loss + 0.5 dB, and IIP3 ≈ LO power + 10 dB as a rule of thumb (+16 dBm in Mini-Circuits' worked example) [1][2].
- **Image-reject/IQ mixers**: image rejection ratio $\text{IRR}=\frac{1+2g\cos\varphi+g^2}{1-2g\cos\varphi+g^2}$ ($g$ amplitude ratio, $\varphi$ phase error) ≈ $4/(\epsilon^2+\varphi^2)$. 0.1 dB and 1° → 39.6 dB; 0.5 dB and 2° → 29.5 dB; 1 dB and 10° → 19.6 dB (formula and IQ simulation agree to $10^{-12}$ dB). Analogue IRR beyond ≈ 40 dB needs calibration.
- **Gilbert cell**: two cross-coupled differential pairs switched by the LO; conversion gain ≈ $(2/\pi)g_mR_L$. An undegenerated BJT pair has an input IP3 amplitude of exactly $4V_T$ ≈ 103 mV (≈ −9.7 dBm available from 50 Ω); emitter degeneration $I_0R_E$ = 100 mV raises IIP3 by 14 dB for 9.3 dB less gain (verified).
- **Passive FET (current-commutating) mixers** switch current into a transimpedance amplifier with little voltage swing on the switches → high linearity, low flicker noise; 25 % duty-cycle four-phase LOs are the norm in CMOS SDR chips [3].
- **APDP harmonic mixer**: an anti-parallel diode pair's current is an odd function of voltage, so only products with $m+n$ odd leave it: the 2·LO − RF product is produced while LO − RF and 2·LO are cancelled (to −200 dB in simulation) — mix at mm-wave with an LO at half the frequency. **Subsampling mixers** fold wideband noise: NF penalty ≈ $10\log(2B/f_s)$ (500 MHz noise bandwidth sampled at 10 MHz: +20 dB) unless filtered before the sampler.
- **LPTV / N-path:** for small signals a pumped mixer is linear but periodically time-varying; a **conversion matrix** links the sidebands $\omega+k\omega_{LO}$. An ideal N-path (1/N-duty) sampling mixer — the **Tayloe detector** for N = 4 — holds each capacitor at $\mathrm{sinc}(\pi/N)$ = 0.900 of the source EMF (I = 1.80 A differential), has a single-pole baseband response at $f_p=1/(2\pi NR_sC)$ (50 Ω, 0.80 µF → 1 kHz; Q 3500 at 7 MHz), responds only at $(1+kN)f_{LO}$ (3LO −9.5 dB **mirrored**, 5LO −14 dB), folds noise to $F=1/\mathrm{sinc}^2(\pi/N)$ = **0.91 dB** (N = 4) or 0.22 dB (N = 8), and presents ≈ 4.3 $R_s$ in band (verified by simulation and ngspice).

## Intuition (no math)
A mixer is a fast switch. Imagine the RF signal passing through a switch that flips its polarity every half LO cycle — multiplying it by +1, −1, +1, −1. Seen in the frequency domain, flipping the polarity at rate $f_{LO}$ slides the whole spectrum up and down by $f_{LO}$: a component at 433.92 MHz appears at 433.92 − 423.22 = 10.7 MHz and at 857 MHz. A filter keeps one. The flip is a square wave, which also contains 3·LO, 5·LO …, so signals near those frequencies are converted too — a mixer is a many-input device, and the art of frequency planning is to make sure nothing unwanted sits on any of those inputs.

The image is the mixer's blind spot: the switch cannot tell whether the RF was 10.7 MHz above or below the LO; both land at 10.7 MHz. Either filter the image out before the mixer, or use two mixers driven by LOs 90° apart (I and Q). In the I/Q outputs the wanted signal and the image rotate in opposite directions (positive vs negative frequency), and a 90° phase shift plus a sum separates them. The cancellation depends on the two paths being identical — a 1° or 0.1 dB mismatch limits it to about 40 dB.

"Balanced" mixers use symmetry to cancel what you don't want: in a single-balanced mixer the LO appears at the RF and IF ports only as a common-mode signal and cancels; a double-balanced mixer cancels both LO and RF at the IF port and suppresses the even-order spurs. How well depends on the baluns and diode matching.

## The math

### Level 1 — definitions
- Conversion gain $G_c=P_{IF}/P_{RF}$ (single sideband); conversion loss $CL=-G_c$ (dB). Double-sideband measurements (both RF sidebands present, e.g. noise) read 3 dB lower [1].
- Isolations: LO→RF, LO→IF, RF→IF (dB).
- Intercepts: $\text{OIP3}=P_{IF}+\Delta_{IM3}/2$, $\text{IIP3}=\text{OIP3}+CL$ where $\Delta_{IM3}$ = IF-tone-to-IM3 difference. Mini-Circuits example: −10 dBm RF → −17 dBm IF, IM3 −69 dBm: $\Delta$ = 52 dB, OIP3 = +9 dBm, IIP3 = +16 dBm (reproduced, check H) [1].
- Spurious response: an RF input at $f$ produces IF output when $|mf\pm nf_{LO}|=f_{IF}$; order $=|m|+|n|$.
- Image: $f_{im}=2f_{LO}-f_{RF}$.

### Level 2 — derivations

**(a) Switching mixer conversion gain.** A ±1 square wave of frequency $f_L$ has the Fourier series $s(t)=\frac{4}{\pi}\sum_{k\text{ odd}}\frac{(-1)^{(k-1)/2}}{k}\cos k\omega_Lt$. Multiplying $A\cos\omega_Rt$ by the $k=1$ term gives IF amplitude $\frac{4}{\pi}\cdot\frac{A}{2}=\frac{2}{\pi}A$ → $20\log(2/\pi)=-3.92$ dB. The $k=3$ term converts RF near $3f_L$ with gain $2/(3\pi)$ (−9.5 dB relative), $k=5$ at −14 dB, etc. (checks A1–A2). A diode ring approximates this with the diodes' on-resistance and finite switching time adding ≈ 1–3 dB: typical DBMs are 5–7 dB [2].

**(b) Image and half-IF.** Any RF with $|f-f_{LO}|=f_{IF}$ converts, so both $f_{LO}\pm f_{IF}$ do. The 2×2 product $|2f-2f_{LO}|=f_{IF}$ is satisfied at $f=f_{LO}\pm f_{IF}/2$ — for a low-side LO, $f_{RF}-f_{IF}/2$ (the "half-IF" spur), which is uncomfortably close to the wanted signal when the IF is small. Its level depends on the second-order nonlinearity (balanced mixers suppress it). Choose the IF so that $f_{IF}/2$ is outside the pre-selector passband with enough rejection ([receiver architectures](receiver-architectures.md)).

**(c) Image-reject mixer and IQ imbalance.** Downconvert with $\cos\omega_Lt$ and $-g\sin(\omega_Lt+\varphi)$ ($g$ = gain ratio, φ = phase error) and combine as $I+jQ$. A positive-frequency input (wanted) and a negative-frequency input (image) separate with ratio
$$\text{IRR}=\frac{|1+ge^{j\varphi}|^2}{|1-ge^{j\varphi}|^2}=\frac{1+2g\cos\varphi+g^2}{1-2g\cos\varphi+g^2}\approx\frac{4}{\epsilon^2+\varphi^2}\quad(g=1+\epsilon)$$
[3 ch.4][4]. The same expression gives the "mirror image" level of a zero-IF receiver or the sideband suppression of an IQ modulator ([transmitter architectures](transmitter-architectures.md)). Hartley architecture: I and Q IF paths, a 90° shift in one (RC-CR or polyphase filter), then sum → image cancelled. Weaver: a second quadrature mixing stage replaces the 90° shifter (easier to make broadband), at the cost of a secondary image that needs mild filtering [5].

**(d) Gilbert cell and differential-pair linearity.** The differential output current of a BJT pair with tail $I_0$ is $\Delta I=I_0\tanh(v_d/2V_T)$. Expanding $\tanh u\approx u-u^3/3$ with $u=v_d/2V_T$: $a_1=I_0/2V_T$, $a_3=-I_0/(24V_T^3)$. The input IP3 amplitude is $A_{IP3}=\sqrt{\frac43\left|\frac{a_1}{a_3}\right|}=4V_T$ ≈ 103 mV (check E1; two-tone simulation 103.5 mV). With an ideal switching quad on top, the mixer's conversion gain is $(2/\pi)g_mR_L$ and its IIP3 is that of the RF pair. Emitter degeneration linearises the RF pair (check E2: +14 dB IIP3 for −9.3 dB gain at $I_0R_E$ = 100 mV) [3][6].

**(e) APDP harmonic mixing.** Two anti-parallel diodes with $i=I_s(e^{v/nV_T}-1)$ each give terminal current $i=2I_s\sinh(v/nV_T)$ — odd in $v$. For $v=V_L\cos\omega_Lt+V_R\cos\omega_Rt$, an odd function contains only products $m\omega_R\pm n\omega_L$ with $m+n$ odd; with $m=1$, $n$ must be even: $2\omega_L-\omega_R$ survives, $\omega_L-\omega_R$ and $2\omega_L$ are absent from the terminal current (they circulate in the loop). Check F: 2LO−RF present, LO−RF and 2LO at −207 dB relative (numerical floor) [7].

**(f) Subsampling.** A sampler at $f_s$ is a mixer with an LO comb at all multiples of $f_s$; any noise within the sampler's analogue bandwidth $B$ folds onto the baseband $[0,f_s/2]$ about $2B/f_s$ times, raising the noise floor by $10\log(2B/f_s)$ unless the input is band-limited first (check G) [8]. Sampling (track-and-hold) mixers are used in RF-sampling ADCs and SDRs ([sampling](../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md)).

### Level 3 — noise, LO issues and advanced topologies
- **Mixer noise figure**: a passive mixer's SSB NF ≈ its conversion loss (plus ≈ 0.5 dB for a diode DBM [1]); DSB NF is 3 dB lower when both sidebands carry signal (direct conversion, radiometers). LO phase noise and LO AM noise are transferred to the IF (reciprocal mixing, see [phase noise](../07-noise-linearity/phase-noise-and-jitter.md)).
- **LO drive and linearity**: DBM compression occurs roughly when the RF approaches the LO level minus 10 dB [1]; higher-level mixers (Level 17/23, or multiple diodes per arm) trade LO power for IP3.
- **Isolation limits**: LO leakage to RF radiates through the antenna and self-mixes (DC offsets in zero-IF); LO→IF leakage must be filtered; isolation degrades at the top of the balun's range (≈ 30 dB typical for DBMs [1]).
- **Passive current-mode mixers** with 25 % duty-cycle LO avoid the overlap of I and Q switches, give higher conversion gain and lower noise than overlapping 50 % IQ LOs (Razavi's analysis [3]), and are the norm in SAW-less CMOS receivers; harmonic-rejection mixers weight several phases to cancel the 3rd and 5th LO harmonic responses [3].
- **Sub-harmonic IQ mixers** and **N-path filters** extend the switching idea to tunable high-Q filtering [3].

### Level 3 — LPTV analysis: conversion matrices, noise folding and N-path (Tayloe) mixers

**(a) Why LPTV.** The LO is large and periodic; the RF is small. Linearising every nonlinear element about the LO-driven operating point leaves a *linear* circuit whose element values vary periodically: a conductance $g(t)=\sum_kG_ke^{jk\omega_Lt}$ (and similarly capacitances). A small-signal voltage containing sidebands $V_n$ at $\omega_0+n\omega_L$ produces a current $i(t)=g(t)v(t)$ with sidebands $I_m=\sum_nG_{m-n}V_n$. Stacking sidebands $n=-K\dots K$ gives $\mathbf I=\mathbf G\mathbf V$, a Toeplitz **conversion matrix**. Embedding it in the linear circuit at each sideband frequency (each sideband sees its own port impedances) yields conversion gain, port impedances and the image and harmonic responses in one solve. This is how harmonic-balance simulators and Maas's diode-mixer theory compute small-signal behaviour [7][9]. For an ideal switch closed during 1/N of the period, $G_k=\frac{G_{on}}{N}\mathrm{sinc}(k\pi/N)e^{-jk\pi/N}$.

**(b) Noise is cyclostationary.** The noise of a pumped element (shot noise of a diode with $I(t)$, thermal noise of a switch with $R(t)$) has a periodically varying variance. Its sidebands at $\omega+k\omega_L$ are correlated, described by a noise *correlation* matrix with the same sideband indexing. Noise from **every** sideband that maps onto the IF adds: the source's own thermal noise at the image and at each LO harmonic band is converted along with the signal. That is **noise folding**. For an ideal ±1 commutator (50 % duty), the white source noise passes with unchanged density while the wanted signal gets $(2/\pi)^2$. SSB $F=\pi^2/4$ (3.92 dB, the image band included); DSB, with signal in both sidebands, 0.91 dB.

**(c) N-path sampling mixer (Tayloe detector, quadrature sampling detector).** A source EMF $v_s$ with resistance $R_s$ (antenna, or a 50 Ω pad) drives a 1-of-N commutator, typically a 74CBT3253/FST3253-class analogue multiplexer clocked at 4× by a divide-by-4 Johnson counter. Each path ends on a capacitor C, and each capacitor is connected for 1/N of every period [10]. With $NR_sC\gg T_{LO}$ and in steady state, the average current into a capacitor over its window is zero. So the capacitor voltage equals the **window average** of $v_s$: for $v_s=A\cos(\omega_Lt+\theta)$ it is $A\,\mathrm{sinc}(\pi/N)\cos(\theta-\theta_k)$, i.e. 0.9003A for N = 4. Combining $I=v_0-v_2$, $Q=v_1-v_3$ gives $|I+jQ|$ = 1.80A: the "less than 1 dB conversion loss" Tayloe claimed against 5–8 dB for diode mixers [10]. The capacitors charge through $R_s$ only 1/N of the time, so the baseband has one pole at $f_p=1/(2\pi NR_sC)$ and the RF passband is $2f_p$ wide, tracking the LO. That is a high-Q band-pass at the RF node (the **N-path filter**) [11][12].

- *Harmonic responses.* Window averaging weights a tone at $k f_L$ by $\mathrm{sinc}(k\pi/N)$. The I/Q combination keeps only $k\equiv1\ (\mathrm{mod}\ N)$: for N = 4, k = 1, −3, 5, −7 … The response at 3LO is 1/3 (−9.54 dB) and lands on the **opposite** baseband sideband, i.e. mirrored; 5LO is 1/5 (−13.98 dB) and upright. DC, 2LO and 4LO cancel in the differential outputs (< −60 dB in the ideal model). A low-pass before the QSD is mandatory: a 21 MHz broadcaster appears in a 7 MHz QSD's output only 9.5 dB down.
- *Noise folding.* Every band $k\equiv1\ (\mathrm{mod}\ N)$ contributes the source's noise with weight $\mathrm{sinc}^2(k\pi/N)$, and $\sum_{k\equiv1}\mathrm{sinc}^2(k\pi/N)=1$. So the ideal N-path's complex (image-rejecting) output has $F=1/\mathrm{sinc}^2(\pi/N)$: **1.23 (0.91 dB) for N = 4**, 1.05 (0.22 dB) for N = 8, π²/4 (3.92 dB) for N = 2 (where the image band folds in). Switch resistance adds $\approx R_{sw}/R_s$ to F. The baseband amplifier's noise, referred through the high-impedance capacitor node, usually dominates real QSD receivers [11][12].
- *Input impedance.* The RF node is a staircase of the capacitor voltages, whose fundamental is $\mathrm{sinc}^2(\pi/N)$ = 0.81 of the EMF. In band, the QSD therefore looks like ≈ $R_s\,s/(1-s)$ = **4.28 $R_s$** (≈ 214 Ω for a 50 Ω source, |Γ| ≈ 0.62) and is low-impedance out of band. A QSD is not a 50 Ω load. The harmonic content of that staircase is re-radiated towards the antenna, which is why practical SDR front ends put an LNA or pad and a filter ahead of it.
- *Limits.* The upper frequency is set by the switch's ability to turn fully on and off within a quarter period (Tayloe notes this [10]). Clock-edge skew between paths becomes IQ phase error (IRR limit, see (c) of Level 2). Charge injection and LO feedthrough produce DC offsets as in any zero-IF receiver. 25 % duty with a double-balanced (differential-input) QSD gives the best NF/conversion-loss trade among switch-based converters [12].

## Design equations & rules of thumb

| Quantity | Equation | Typical |
|---|---|---|
| Ideal switching mixer CL | $20\log(\pi/2)$ = 3.92 dB | diode DBM 5–7 dB |
| Odd-harmonic responses | $2/(k\pi)$ relative $2/\pi$: 1/k | 3LO −9.5 dB, 5LO −14 dB |
| Image | $2f_{LO}-f_{RF}$ | 433.92/10.7 MHz: 412.52 or 455.32 MHz |
| Half-IF (2×2) | $f_{RF}\mp f_{IF}/2$ | 428.57 MHz (low-side LO) |
| IRR | $\frac{1+2g\cos\varphi+g^2}{1-2g\cos\varphi+g^2}\approx4/(\epsilon^2+\varphi^2)$ | 0.1 dB/1° → 39.6 dB |
| Mixer IP3 | OIP3 $=P_{IF}+\Delta/2$; IIP3 = OIP3 + CL | DBM: IIP3 ≈ $P_{LO}$ + 10 dB |
| Diode-mixer IP3 vs P1dB | IP3 ≈ P1dB + 15 dB (diode), + 10 dB (FET) | rule of thumb [2] |
| Diff-pair IIP3 amplitude | $4V_T$ ≈ 103 mV | degeneration raises it |
| Gilbert gain | $(2/\pi)g_mR_L$ | |
| Subsampling noise | $+10\log(2B/f_s)$ | filter before sampling |
| DBM NF | ≈ CL + 0.5 dB | [1] |
| N-path cap voltage | $A\,\mathrm{sinc}(\pi/N)$ (window average) | N = 4: 0.900 A; I = 1.80 A |
| N-path bandwidth | baseband pole $1/(2\pi NR_sC)$, RF BW twice that | 50 Ω, 0.80 µF: 1 kHz / 2 kHz |
| N-path noise folding | $F=1/\mathrm{sinc}^2(\pi/N)$ (ideal switches) | N = 4: 0.91 dB; N = 8: 0.22 dB |
| N-path harmonic responses | $(1+kN)f_{LO}$ at $1/\lvert1+kN\rvert$; negative k mirrored | 3LO −9.5 dB mirrored, 5LO −14 dB |
| N-path in-band $Z_{in}$ | $R_s\,\mathrm{sinc}^2/(1-\mathrm{sinc}^2)$ | 4.28 $R_s$ |

## Worked examples

### Example 1 — Frequency plan for a 433.92 MHz superhet with 10.7 MHz IF
Low-side LO 423.22 MHz: image 412.52 MHz (21.4 MHz below the signal); half-IF spur 428.57 MHz; 3×3 responses at 426.79 and 419.65 MHz (≈ ±IF/3 from LO). High-side LO 444.62 MHz: image 455.32 MHz; half-IF 439.27 MHz; 3×3 at 441.05/448.19 MHz (script B). A 433 MHz SAW (≈ 1.6 MHz wide, [filters](rf-filters-lc-saw-baw-cavity-microstrip.md)) rejects all of these by tens of dB; a wide LC pre-selector (10 % = 43 MHz) does not reject the half-IF spur at all — rely on the mixer's 2nd-order suppression (DBM) or pick a higher IF (e.g. 45 or 70 MHz). The 10.7 MHz ceramic IF filter then sets the selectivity.

### Example 2 — Using a Level 7 DBM
A Level 7 DBM driven with +7 dBm LO: conversion loss ≈ 6 dB, SSB NF ≈ 6.5 dB, IIP3 ≈ +15 to +17 dBm (rule: LO + 10 dB; Mini-Circuits worked example +16 dBm) [1][2]. Terminate *all* ports broadband in 50 Ω (especially the IF port: a reactive IF filter directly on a DBM reflects the sum frequency and degrades IP3 and spurs — use a diplexer or a pad). For the LO, a PLL output of 0 dBm needs a buffer amplifier with ≥ 10 dB gain.

### Example 3 — How good must an IQ receiver be?
An SDR (zero-IF or low-IF) receiving a weak LoRa signal at +200 kHz next to a strong signal at −200 kHz relies on IRR: 0.5 dB/2° analogue imbalance gives 29.5 dB — a 40 dB stronger neighbour's image would be 10 dB *above* the wanted signal. Digital IQ calibration (estimate $g$, φ from test tones or blind statistics) routinely reaches 50–60 dB (see [receiver architectures](receiver-architectures.md) and [IQ baseband](../14-sdr-dsp/iq-complex-baseband.md)).

### Example 4 — Gilbert-cell mixer input level
Undegenerated BJT Gilbert cell: IIP3 amplitude ≈ 103 mV at the RF pair input; if that input is a 50 Ω match, IIP3 ≈ −9.7 dBm (available). With a preceding 15 dB LNA the cascade IIP3 referred to the antenna is ≈ −25 dBm — too low for a site with strong interferers; add degeneration (I₀R_E = 100 mV: +14 dB) or use a passive mixer (see [receiver cascade](../07-noise-linearity/receiver-cascade-analysis.md)).

### Example 5 — 24 GHz radar front end with a harmonic mixer
Mixing a 24.125 GHz echo with an APDP driven by a 12.06 GHz LO: IF = 2 × 12.06 − 24.125 GHz (tens of MHz for Doppler/FMCW); the LO's fundamental and 2nd harmonic do not appear at the terminals, easing filtering, and a 12 GHz source is cheaper than a 24 GHz one. Conversion loss is higher (≈ 8–15 dB typical) than a fundamental mixer [7]. See [FMCW radar](../11-radar/fmcw-radar.md).

### Example 6 — A Tayloe detector for a 7 MHz QRP SDR
Target 1 kHz baseband (−3 dB) behind a 50 Ω antenna port: $C=1/(2\pi\cdot4\cdot50\cdot1000)$ = **0.796 µF** per path (0.82 µF film/C0G-class in practice). The RF passband is 2 kHz wide at 7 MHz, Q = 3500, and it tracks the LO (a 28 MHz clock into a ÷4 Johnson counter). A 1 µV EMF gives 0.90 µV on each capacitor and 1.80 µV on the differential I and Q, with $F_{mixer}$ ≈ 0.91 dB before the op-amps. The baseband instrumentation amplifier then sets the NF: its input sees the high capacitor impedance, so choose a low-voltage-noise, low-current-noise part, and give it gain to bring µV signals above the sound card's floor. The input is ≈ 214 Ω in band, so expect a poor return loss (≈ 4 dB) unless a pad or LNA precedes it. Put a 7 MHz low-pass or band-pass ahead: the 21 MHz (3LO) response is only 9.5 dB down and lands on the opposite sideband (script C). The `s14_tayloe.py` ngspice deck (7 MHz, 50 Ω, 10 nF, 10 kHz offset) gives a 0.8935 V capacitor beat for a 1 V EMF vs 0.8932 V predicted.

### Example 7 — 4 paths or 8?
An 8-path detector (12.5 % duty, three-bit counter, two 4:1 muxes) lowers noise folding from 0.91 to 0.22 dB. Its first harmonic responses move to 7LO and 9LO (−16.9/−19.1 dB) instead of 3LO/5LO, which eases the pre-filter. The capacitor voltage rises from 0.900 A to 0.974 A. The cost is a clock at 8× the LO, more switch-skew-sensitive phases and a polyphase combination of 8 outputs. For an HF SDR the 4-path is enough; for a wideband mixer-first receiver the 8-path's harmonic rejection is usually the reason to choose it [11].

## Practical notes
- **Port terminations:** DBMs are specified with all ports in 50 Ω; mismatches (especially at the IF at the sum frequency) degrade IP3 and isolation. A 3 dB pad on the IF port is a cheap fix.
- **LO purity:** LO harmonics and phase noise mix with signals at the corresponding RF offsets; filter the LO, and keep LO spurs (e.g. PLL reference spurs) below the level at which a strong adjacent signal would be converted onto the IF.
- **Balance:** use matched diode quads/rings (e.g. Schottky ring packages) and symmetric balun layout; LO–RF isolation of 30–40 dB is typical, 50–60 dB needs care.
- **Active mixers** (Gilbert-based ICs such as ADI/NXP parts) need little LO power (−10 to 0 dBm) and give gain, but have lower IIP3 and higher NF than passive DBMs; check the datasheet's input impedance (often not 50 Ω).
- **Measure spurs** with a two-generator setup: sweep a single RF tone across the band with the LO fixed and watch the IF output on a spectrum analyser for every frequency that produces an IF response — that is your measured spur chart.

## Common mistakes & misconceptions
- *"A mixer has one input."* It converts signals at the image, at LO harmonics (3LO, 5LO …) and at all m × n combinations; each needs filtering or suppression.
- *"Conversion loss 6 dB means NF 6 dB, done."* Also add LO noise, and in a zero-IF receiver flicker noise and DC offsets.
- *"Image rejection mixers remove the need for an RF filter."* Analogue IRR is ≈ 25–40 dB; strong images still need filtering or calibration.
- *"Higher LO power is always better."* Beyond the rated level, conversion loss barely improves; IP3 rises but LO leakage and heat rise too.
- *"The Gilbert cell is linear because it's differential."* Differential pairs cancel even-order terms, not odd: IIP3 of a bare pair is only 4V_T.
- *"The half-IF spur is negligible."* With a low IF and a wide pre-selector it is often the worst close-in spur.
- *"Sampling is free mixing."* Noise and interferers from every Nyquist zone within the sampler bandwidth fold in.
- *"A Tayloe detector has gain, so it beats physics."* The 1.80 A differential output is a voltage ratio into a high-impedance capacitor node with ≈ 4.3 R_s input impedance, not a power gain. Its noise factor is still ≥ 1/sinc²(π/4).
- *"The QSD's narrow bandwidth means I don't need an RF filter."* It responds at 3LO (mirrored) and 5LO at only −9.5 and −14 dB.
- *"A mixer is nonlinear, so linear circuit analysis can't apply."* For small signals around the LO it is linear and periodically time-varying. Conversion matrices treat it exactly.
- *"Passive mixer noise = its conversion loss, end of story."* Folded noise from LO harmonic bands is part of that number; with an N-path and complex output it drops to 1/sinc²(π/N).

## How to simulate / verify
- `tools/verify/s14_tayloe.py` (16/16 PASS, output in `s14_tayloe_output.txt`): vectorised ideal-switch 4-path QSD — capacitor amplitude sinc(π/4), single-pole bandwidth, Tayloe 0.796 µF example, harmonic responses and mirroring, noise folding from deterministic harmonic transfer functions (N = 4 and 8) and a Monte Carlo white-noise run, in-band input impedance 4.28 R_s, and an ngspice switch-level transient at 7 MHz.
- `tools/verify/rfckt_mixers.py`: ideal switching mixer and LO-harmonic responses (FFT), spur/image/half-IF finder for any plan, IRR formula vs IQ simulation, Gilbert/diff-pair IIP3 (two-tone) with degeneration, APDP harmonic-mixing selection rule, subsampling noise folding, IP3 bookkeeping reproducing the Mini-Circuits worked example.
- SPICE transient + FFT with a diode ring model; harmonic balance (Qucs-S, commercial) for accurate conversion loss and spur tables; GNU Radio / Python to model IQ imbalance and calibration.
- Bench: signal generators + spectrum analyser; for IQ imbalance, inject a tone and measure the mirror.

## Open questions / gaps
- Vendor spur tables (m × n rejection in dBc at stated RF/LO levels) are part-specific and not reproduced; add typical values from a specific DBM data sheet in domain 18.
- The 25 %-duty passive-mixer conversion-gain comparison is quoted from Razavi's treatment. The N-path window-average result (sinc(π/N), noise folding, Z_in) is now derived and simulated, but only for ideal switches with an ideal (noiseless, infinite-impedance) baseband load; switch R, baseband amplifier noise and clock skew are not modelled.
- The original Tayloe article's publication venue and date were not confirmed (only a transcription and the 2001 patent were read).
- Diode-ring conversion loss vs LO drive was not simulated (only the ideal switching limit).

## Sources
1. Mini-Circuits, *AN-00-009: Understanding Mixers – Terms Defined, and Measuring Performance* (conversion loss/gain, SSB vs DSB, compression within ≈ 10 dB of LO, ≈ 30 dB isolation at top of band, NF ≈ CL + 0.5 dB, IP3 worked example). https://www.minicircuits.com/pages/pdfs/an00009.pdf (app note; read in full)
2. Mini-Circuits, *AN-00-010: How to select a mixer*; *AN-00-001: Figure of merit of mixer intermod performance* (IP3 ≈ P1dB + 15 dB diode / + 10 dB FET; IP3 ≈ LO + 10 dB). https://www.minicircuits.com/app/AN00-010.pdf (app notes; via search summary)
3. B. Razavi, *RF Microelectronics*, 2nd ed., Prentice Hall, 2011, ch. 4 (transceiver architectures, IQ mismatch, image rejection), ch. 6 (mixers: passive/active, Gilbert, 25 % duty cycle, harmonic-rejection). (textbook)
4. D. M. Pozar, *Microwave Engineering*, 4th ed., 2012, ch. 13 (oscillators and mixers: mixer characteristics, balanced and image-reject mixers). (textbook)
5. D. K. Weaver, "A third method of generation and detection of single-sideband signals," *Proc. IRE*, 44(12), pp. 1703–1705, 1956; R. V. L. Hartley, US patent 1,666,206 (1928). (peer-reviewed / patent)
6. B. Gilbert, "A precise four-quadrant multiplier with subnanosecond response," *IEEE J. Solid-State Circuits*, SC-3(4), pp. 365–373, Dec. 1968. (peer-reviewed)
7. S. A. Maas, *Microwave Mixers*, 2nd ed., Artech House, 1993 (diode mixers, APDP subharmonic mixers); M. Cohn, J. E. Degenford, B. A. Newman, "Harmonic mixing with an antiparallel diode pair," *IEEE Trans. MTT*, 23(8), pp. 667–673, 1975. (textbook / peer-reviewed)
8. R. G. Vaughan, N. L. Scott, D. R. White, "The theory of bandpass sampling," *IEEE Trans. Signal Process.*, 39(9), pp. 1973–1984, 1991 (noise folding in subsampling). (peer-reviewed)
9. S. A. Maas, *Nonlinear Microwave and RF Circuits*, 2nd ed., Artech House, 2003, ch. on LPTV/conversion-matrix analysis and mixer noise (with [7]). (textbook; not re-read)
10. D. Tayloe, US patent 6,230,000 B1, "Product detector and method therefor," 2001 (commutated capacitors as a tracking band-pass, < 1 dB vs 7–8 dB conversion loss); D. Tayloe, "Ultra Low Noise, High Performance, Zero IF Quadrature Product Detector and Preamplifier" (< 1 dB loss, Q 3500 at 7 MHz, +30 dBm IP3 claim, bandwidth set by 4(R_sys + R + R_switch)C; read via a transcription, venue/date unconfirmed). (patent / magazine)
11. C. Andrews, A. C. Molnar, "A passive mixer-first receiver with digitally controlled and widely tunable RF interface," *IEEE J. Solid-State Circuits*, 45(12), 2010; A. Ghaffari, E. A. M. Klumperink, M. C. M. Soer, B. Nauta, "Tunable high-Q N-path band-pass filters: modeling and verification," *IEEE JSSC*, 46(5), 2011 (N-path impedance, harmonic folding, 4- vs 8-path). (peer-reviewed; cited for context, results re-derived here)
12. M. C. M. Soer, *Analysis and comparison of switch-based frequency converters*, MSc thesis, University of Twente, 2007 (Tayloe/van Graas/QSD analysis; 25 % double-balanced best NF vs conversion loss). https://essay.utwente.nl/58276 (thesis)
