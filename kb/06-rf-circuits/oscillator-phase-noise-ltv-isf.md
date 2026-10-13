---
title: Oscillator phase noise beyond Leeson — the Hajimiri–Lee ISF (LTV) theory, flicker up-conversion, AM–PM, microphonics and g-sensitivity
domain: 06-rf-circuits
slug: oscillator-phase-noise-ltv-isf
tags: [phase-noise, oscillator, leeson, isf, impulse-sensitivity-function, ltv, hajimiri-lee, flicker-upconversion, 1-over-f3-corner, cyclostationary-noise, am-pm, varactor, microphonics, g-sensitivity, acceleration-sensitivity, vibration, rocket, tcxo, lorentzian, ring-oscillator, lc-vco]
prerequisites:
  - ../07-noise-linearity/phase-noise-and-jitter.md
  - ../05-analog-electronics/oscillators.md
  - ../04-real-components-hf/crystals-and-resonators.md
  - ../00-math-foundations/fourier-series-and-transform.md
  - ../00-math-foundations/probability-random-processes-and-psd.md
related:
  - vco-and-pll-synthesizers.md
  - frequency-multipliers-dividers.md
  - ../07-noise-linearity/shot-and-flicker-noise.md
  - ../17-test-measurement/phase-noise-measurement.md
  - ../21-gnss/gnss-on-rockets-dynamics-and-limits.md
  - ../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md
  - ../11-radar/fmcw-radar.md
  - ../04-real-components-hf/capacitors-at-rf-mlcc.md
level: advanced
confidence: medium
last_updated: 2026-10-13
---

# Oscillator phase noise beyond Leeson: ISF/LTV theory, AM–PM and vibration

## Questions this page answers
- What does Leeson's formula leave out, and why are its F and flicker corner only "fitting parameters"?
- What is the impulse sensitivity function (ISF), and how does it predict phase noise from each noise source?
- Why is the 1/f³ corner of an oscillator's phase noise usually lower than the transistor's 1/f noise corner?
- Why do symmetric waveforms (matched rise and fall times) give lower close-in phase noise?
- Why is a Colpitts oscillator quieter than its transistor noise suggests (cyclostationary noise)?
- Why do some sources write Leeson with FkT/(2Ps) and others with 2FkT/Ps, and which should I use?
- How does amplitude noise turn into phase noise in a varactor-tuned VCO (AM–PM)?
- What are microphonics, and how do I keep my oscillator from "singing" on a vibrating rocket?
- How much phase noise does a crystal's g-sensitivity add under rocket vibration, at 433 MHz, 915 MHz, GPS L1 and 24 GHz?
- Does a PLL remove vibration-induced phase noise?

## TL;DR
- **Leeson (Rubiola form, used across this KB):** $\mathcal L(f_m)=10\log\!\big[\tfrac{FkT}{2P_s}\big(1+(\tfrac{f_0}{2Q_Lf_m})^2\big)\big(1+\tfrac{f_c}{f_m}\big)\big]$, where $P_s$ is the carrier power at the input of the sustaining amplifier. It predicts slopes well but treats $F$ and $f_c$ as fitted numbers.
- **The Hajimiri–Lee theory** says that a charge $\Delta q$ injected at phase $\theta=\omega_0t$ shifts the phase permanently by $\Delta\varphi=\Gamma(\theta)\,\Delta q/q_{max}$. The periodic **ISF** $\Gamma$ turns the oscillator into a linear time-varying (LTV) system. White noise of one-sided density $\overline{i_n^2}/\Delta f$ then gives $\mathcal L(\Delta\omega)=\dfrac{\Gamma_{rms}^2\,\overline{i_n^2}/\Delta f}{2q_{max}^2\Delta\omega^2}$.
- **An ideal LC tank** has $\Gamma=-\sin\theta$ and $\Gamma_{rms}=1/\sqrt2$. With only the tank resistor's noise, this reduces exactly to $\mathcal L=(2kT/P_{tank})(f_0/2Qf_m)^2$, where $P_{tank}$ is the power dissipated in the tank. A 3000-trajectory stochastic simulation of a van der Pol oscillator matched the predicted phase-diffusion rate to 2 %. This "2kT/P" form is a different *definition* of $P$, not a different physics. Putting $P_{tank}$ into the Rubiola form reads exactly 6.02 dB too low.
- **Flicker up-conversion depends on the dc value of the ISF.** The 1/f³ corner is $f_{1/f^3}=f_{1/f}\,(\Gamma_{dc}/\Gamma_{rms})^2$. In a simulated 3-stage ring, $\Gamma_{dc}\approx0$ when rise and fall are matched. With the pull-up 0.4× weaker, $\Gamma_{dc}/\Gamma_{rms}=0.104$, so a 1 MHz device corner becomes a **10.8 kHz** phase-noise corner. Slow-current injection confirmed the predicted PM to 2 %.
- **AM–PM:** a varactor whose average capacitance depends on RF swing converts amplitude noise into phase noise: $\mathcal L_{PM}=\mathcal L_{AM}+20\log(\kappa/f_m)$. In the example, $\kappa$ rises from 0.2 to 1.3 MHz per 100 % AM as the varactor swing goes from 0.2 to 0.5 V. That adds 6 to 22 dB over the AM noise at 100 kHz offset.
- **g-sensitivity (Vig):** sine vibration gives spurs at $\pm f_v$ of $20\log(\Gamma_g A f_0/2f_v)$ dBc. Random vibration gives $\mathcal L(f)=20\log(\Gamma_g f_0\sqrt{2\,PSD}/2f)$. Nearly all quartz resonators lie within ×3 of **1×10⁻⁹/g**; the best SC-cuts reach low parts in 10¹⁰ [8].
- **Rocket numbers** (1 ppb/g, NASA-GEVS-like 14.1 g_rms profile): 433.92 MHz gives −58 dBc/Hz at 100 Hz and 1.8° rms; 915 MHz gives 3.7°; GPS L1 gives 6.4° (same as [21](../21-gnss/gnss-on-rockets-dynamics-and-limits.md)); a 24 GHz radar LO from the same reference gives **≈ 98° rms**, which is useless for coherent Doppler. A PLL does **not** remove reference g-sensitivity: it multiplies it by N, +20 log N. It does suppress the VCO's own microphonics inside its loop bandwidth.

## Intuition (no math)
An oscillator has no "home" phase. Any disturbance that moves it along its cycle is remembered for ever, because nothing restores phase. A disturbance that changes its amplitude, by contrast, is forgotten: the limiting mechanism pulls the amplitude back. Phase noise is therefore an accumulation, a random walk of phase driven by every small kick the circuit receives.

How much a kick moves the phase depends on **when** in the cycle it arrives. Push charge into an LC tank at the peak of its voltage and you mostly change the amplitude, which then recovers, so the timing barely moves. Push the same charge in at the zero crossing and you shift the crossing itself, a pure timing change that never recovers. The impulse sensitivity function is simply a plot of "phase shift per unit kick" against the moment of the kick. For a sine wave it is a sine wave 90° away from the voltage.

Two consequences follow from that picture.
- **Noise near each harmonic of the carrier matters**, not just noise near the carrier. The ISF is periodic, so it multiplies (mixes) the noise. Noise near $n f_0$ is weighted by the ISF's $n$-th Fourier coefficient and lands next to the carrier.
- **Slow noise (1/f) only gets in through the ISF's average value.** If the waveform is symmetric, so that a kick on the rising edge and the same kick on the falling edge shift the phase by equal and opposite amounts, slow disturbances cancel over each cycle. Flicker noise then barely up-converts. Asymmetric waveforms leave a net average, and the 1/f noise appears as 1/f³ phase noise.

**Microphonics** is the mechanical version of the same story. Vibration flexes the quartz blank, an inductor's turns or a ceramic capacitor (class-II MLCCs are piezoelectric), and each flex nudges the frequency. Frequency wobble at the vibration rate $f_v$ is phase modulation with index $\Delta f/f_v$. Low vibration frequencies with a few hertz of deviation make strong sidebands close to the carrier, exactly where receivers and radars care most.

## The math

### Level 1 — Leeson, the ISF result, and what each symbol means
**Leeson** [1][2]: $f_0$ carrier (Hz), $Q_L$ loaded resonator Q, $F$ sustaining-amplifier noise factor, $P_s$ (W) carrier power at the amplifier input, $f_c$ flicker corner (Hz), $kT=4.0\times10^{-21}$ J at 290 K:
$$\mathcal L(f_m)=10\log_{10}\!\left[\frac{FkT}{2P_s}\left(1+\left(\frac{f_0}{2Q_Lf_m}\right)^2\right)\left(1+\frac{f_c}{f_m}\right)\right]\ \text{dBc/Hz}.$$
Three regions: $1/f^3$ below $\min(f_c,f_0/2Q_L)$; $1/f^2$ inside the "Leeson frequency" $f_L=f_0/2Q_L$; floor $FkT/(2P_s)$ beyond. When $f_L<f_c$, as in crystal oscillators ($f_L$ of a few Hz to a few hundred Hz), the sequence is $1/f^3\to1/f$ (flicker phase noise of the amplifier) $\to$ floor [2].

**ISF** [3][4]. Inject a charge impulse $\Delta q$ into a node whose maximum charge swing is $q_{max}=C\,V_{max}$. The phase shifts by
$$\Delta\varphi=\Gamma(\omega_0t)\,\frac{\Delta q}{q_{max}},\qquad \Gamma(x+2\pi)=\Gamma(x),\qquad \Gamma(x)=\frac{c_0}{2}+\sum_{n\ge1}c_n\cos(nx+\theta_n).$$
$\Gamma$ is dimensionless and independent of $\Delta q$ (for small kicks). Define $\Gamma_{rms}^2=\overline{\Gamma^2}$ and $\Gamma_{dc}=c_0/2$.

Phase noise from a white current source of one-sided density $\overline{i_n^2}/\Delta f$ (A²/Hz), at offset $\Delta\omega=2\pi f_m$:
$$\mathcal L(\Delta\omega)=10\log_{10}\frac{\Gamma_{rms}^2\;\overline{i_n^2}/\Delta f}{2\,q_{max}^2\,\Delta\omega^2}.$$
1/f³ corner, from device noise with 1/f corner $\omega_{1/f}$:
$$\omega_{1/f^3}=\omega_{1/f}\left(\frac{\Gamma_{dc}}{\Gamma_{rms}}\right)^2.$$

### Level 1½ — the two formulas with numbers, algebra only
- **Leeson by slopes.** Far from the carrier the noise is flat at $FkT/(2P_s)$: −177 dBc/Hz for F = 1 and 0 dBm, plus NF, minus any extra drive in dB. Inside $f_L = f_0/(2Q_L)$ it rises 20 dB per decade towards the carrier, because the resonator turns amplitude jitter into accumulating phase. Below the flicker corner it rises 30 dB per decade. So $\mathcal L(f_m) \approx \text{floor} + 20\log_{10}(f_L/f_m)$ in the 1/f² region. A higher loaded Q lowers $f_L$, and every factor of 10 in Q buys 20 dB.
- **ISF as "when you kick a swing".** A small charge Δq dumped onto the tank capacitor shifts the timing (phase) by $\Gamma\,\Delta q/q_{max}$, where $q_{max} = CV_{max}$. Kicked at the voltage peak, the waveform is pushed up and down but not in time, so Γ ≈ 0 and the amplitude error dies away. Kicked at the zero crossing, the whole waveform slides in time, so |Γ| is largest and that phase error stays for ever. Noise that arrives only near the peaks therefore does little harm, which is why class-C and tail-filtered oscillators are quiet. A large swing (big $q_{max}$) dilutes every kick.

*Worked numbers (verified, `tools/verify/s18_level15_numbers.py`).*
- **Leeson:** a 433 MHz oscillator with $Q_L$ = 20, F = 2 (3 dB) and $P_s$ = 0 dBm has a floor of −174 dBc/Hz and $f_L$ = 10.8 MHz. At 100 kHz offset the 1/f² term adds 20 log(108) = 40.7 dB, giving **−133.3 dBc/Hz**, or −132.9 with a 10 kHz flicker corner.
- **ISF kick:** with C = 10 pF and $V_{max}$ = 1 V, $q_{max}$ = 10 pC. A 1 fC kick at a zero crossing (Γ ≈ 1) moves the phase by 10⁻⁴ rad.
- **ISF noise:** a white noise current of 1 pA/√Hz with $\Gamma_{rms}$ = 0.707 (a sinusoidal ISF) gives $\mathcal L$ = −142.0 dBc/Hz at 100 kHz.

### Level 2 — derivations
**(a) ISF of an ideal LC tank.** Take $L=C=1$, $\omega_0=1$, with state $v=A\cos\theta$ and $i_L=A\sin\theta$. A charge kick changes $v$ by $\Delta q/C$ but not $i_L$. The new phase satisfies $\tan\theta'=A\sin\theta/(A\cos\theta+\Delta q/C)$. To first order, $\theta'-\theta=-(\Delta q/CA)\sin\theta$. So $\Gamma(\theta)=-\sin\theta$, $\Gamma_{rms}=1/\sqrt2$, $\Gamma_{dc}=0$. The script reproduces this to $10^{-5}$ (§A). The amplitude also jumps, by $(\Delta q/C)\cos\theta$, but the limiter removes that within a few tank time constants.

**(b) From the ISF to phase noise.** By superposition, an arbitrary injected current gives
$$\varphi(t)=\frac{1}{q_{max}}\int_{-\infty}^{t}\Gamma(\omega_0\tau)\,i(\tau)\,d\tau.$$
This is linear in $i$ but time-varying. For white $i$ with two-sided density $S$ (so $\overline{i_n^2}/\Delta f=2S$):
$$\operatorname{Var}\varphi(t)=\frac{S}{q_{max}^2}\int_0^t\Gamma^2\,d\tau=\frac{\Gamma_{rms}^2S}{q_{max}^2}\,t\equiv c\,t,$$
a Wiener process (random walk). The derivative of $\varphi$ is white with two-sided density $c$. So $S_\varphi^{(2\text{-sided})}=c/\omega^2$, the one-sided $S_\varphi=c/(2\pi^2f^2)$, and $\mathcal L=S_\varphi/2=c/\Delta\omega^2$ (IEEE 1139: $\mathcal L=S_\varphi/2$). Substituting $c$ gives the Level-1 formula. Equivalently, expand $\Gamma$ in its Fourier series. Noise at $n\omega_0+\Delta\omega$ is multiplied by $c_n\cos(n\omega_0t+\theta_n)$ and integrated, giving a phase tone at $\Delta\omega$ of amplitude $c_nI_n/(2q_{max}\Delta\omega)$ (for $n\ge1$). Summing powers over all $n$ with Parseval, $\sum c_n^2\approx2\Gamma_{rms}^2$, gives the same result [3].

*Check (script §B).* A van der Pol LC oscillator (Q = 20, tank-resistor noise only) was integrated for 3000 trajectories × 400 cycles. The measured phase-variance growth rate was 1.48×10⁻⁷ rad²/s against 1.51×10⁻⁷ predicted (−2 %). The amplitude settled at the describing-function value (0.814 vs 0.816).

**(c) The tank form, and why prefactors differ by 6 dB.** For a parallel RLC tank with only $R$'s noise ($\overline{i_n^2}/\Delta f=4kT/R$), $q_{max}=CV_0$, $Q=\omega_0RC$ and $P_{tank}=V_0^2/2R$, step (b) gives
$$\mathcal L=\frac{kT}{RC^2V_0^2\Delta\omega^2}=\frac{2kT}{P_{tank}}\left(\frac{\omega_0}{2Q\Delta\omega}\right)^2.$$
This is Lee & Hajimiri's eq. (12). They reach it by counting the tank's total noise and removing half, the amplitude part, by equipartition [4]. Hajimiri & Lee note that an LTI model which assumes equal amplitude and phase shares, without the limiter removing the AM half, is twice too large [3]. Rubiola's and Leeson's $FkT/(2P_s)$ uses a different power: the carrier at the input of a sustaining amplifier with noise factor $F$ in a matched two-port loop [2]. A negative-resistance LC VCO has no such matched input, so the tank form is natural there. For a two-port oscillator (a 50 Ω amplifier around a crystal or SAW resonator) the Rubiola form is natural. Plugging $P_{tank}$ into $FkT/(2P_s)$ underestimates the noise by exactly 6.02 dB (§B). That error is the one the W4-D6 audit flagged in [05 oscillators](../05-analog-electronics/oscillators.md) (2FkT/Ps attributed to Leeson). Always state which $P$ you mean.

**(d) Flicker up-conversion and the 1/f³ corner.** Let the device noise be $\overline{i_n^2}/\Delta f\,(1+\omega_{1/f}/\Delta\omega)$ at low frequencies. Low-frequency noise is weighted only by $c_0$ (the $n=0$ term). Its contribution is $\mathcal L_{1/f}=\frac{\overline{i_n^2}}{\Delta f}\frac{c_0^2}{8q_{max}^2\Delta\omega^2}\frac{\omega_{1/f}}{\Delta\omega}$. Setting this equal to the white-noise result $\Gamma_{rms}^2\overline{i_n^2}/(2q_{max}^2\Delta\omega^2\Delta f)$ gives the corner $\omega_{1/f^3}=\omega_{1/f}c_0^2/(4\Gamma_{rms}^2)=\omega_{1/f}(\Gamma_{dc}/\Gamma_{rms})^2$ [3].

*Check (script §C–E).* The ISF of a 3-stage tanh-inverter ring was found numerically by kicking node 1 at 120 phases and timing the zero crossings 40 cycles later:

| Ring | $\Gamma_{rms}$ | $\Gamma_{dc}$ | $c_1$ | $c_2$ | 1/f³ corner (1 MHz device corner) |
|---|---|---|---|---|---|
| matched pull-up/pull-down | 0.964 | ≈ 0 (−2×10⁻⁴) | 1.33 | ≈ 0 | ≈ 0 |
| pull-up 0.4× weaker | 1.051 | 0.109 | 1.41 | 0.38 | 10.8 kHz |

Injecting a slow current ($f_0/20$) into the asymmetric ring produced 7.47 mrad of PM against 7.61 mrad predicted from $\Gamma_{dc}$. The matched ring showed about ten times less, and that residue is a threshold read-out artefact. Injecting at $f_0+f_m$ matched the $c_1$ prediction within 5 % for both rings. An LC oscillator with strong limiting (Q = 5) still had $\Gamma_{rms}=0.708$ and $\Gamma_{dc}\approx0$.

**(e) Cyclostationary noise.** Transistor noise switches with the cycle (the drain current flows only near the voltage trough in a Colpitts). Model it as $i_n(t)=i_{n0}(t)\,\alpha(\omega_0t)$, with $\alpha$ the *noise-modulating function* (peak 1). Then use the **effective ISF** $\Gamma_{eff}=\Gamma\cdot\alpha$ in every formula [3]. Noise injected when $\Gamma$ is small is harmless. A Colpitts delivers its current pulse at the voltage extreme, where $|\Gamma|$ of the tank is near zero, which is why it beats its "F" estimate.

**(f) The ISF recipe for a real circuit** (after [3], in outline):
1. List every noise source: a current source across each capacitor and a voltage source in series with each inductor. Keep track of which ones are correlated.
2. For each source, find its ISF. Use one of three routes: inject a short current pulse in a transient simulation at many phases; use the analytic waveform-derivative approximation $\Gamma\approx-\dot v/\max|\dot v|$ for near-sinusoidal nodes; or run a PSS adjoint analysis.
3. Multiply by its noise-modulating function if the source is cyclostationary. Take $\Gamma_{rms}$ and $\Gamma_{dc}$ of the effective ISF.
4. Evaluate the white and flicker formulas for each source. Add powers for uncorrelated sources and add amplitudes for correlated ones.

The output is a ranked list: which transistor, resistor or bias source dominates at each offset. Leeson cannot provide that.

**(g) ISF properties by oscillator type** (qualitative, from [3][4] and the script):

| Oscillator | ISF shape | $\Gamma_{rms}$ | $\Gamma_{dc}$ | Consequence |
|---|---|---|---|---|
| Ideal LC (sinusoidal) | $-\sin\theta$ | 0.707 | 0 | 1/f only through AM–PM or asymmetry |
| Colpitts (pulsed device current) | tank ISF × narrow NMF at the voltage extreme | effective ≪ 0.707 for device noise | small | device noise weighted down; tank R dominates |
| Cross-coupled CMOS LC (NMOS only) | near-sinusoidal, rise/fall asymmetric | ≈ 0.7 | small, non-zero | tail noise up-converts; tail filter helps |
| Complementary (NMOS + PMOS) LC | more symmetric | ≈ 0.7 | smaller | lower 1/f³ corner |
| Ring (symmetric edges) | peaked at each transition | ≈ 1 (sim: 0.96) | ≈ 0 | low 1/f³ corner, high white noise (small $q_{max}$) |
| Ring (asymmetric edges) | unequal peaks | ≈ 1 (sim: 1.05) | sim: 0.11 | 1/f³ corner ≈ 1 % of device 1/f corner |

### Level 3 — where the LTV picture needs extending
- **Close to the carrier.** A pure $1/f^2$ law implies infinite power at zero offset. The random-walk phase actually produces a **Lorentzian** line with full width $\Delta f_{FWHM}=c/2\pi=2\pi f_m^2\mathcal L(f_m)$. For the 433 MHz tank example below that is 5 mHz, which is irrelevant in practice but resolves the paradox (Demir, Mehrotra & Roychowdhury's nonlinear perturbation theory [7]; §F check).
- **Amplitude–phase coupling.** The linear ISF treats phase alone. Real oscillators convert AM to PM through nonlinear reactances (varactors, $C_{gs}(V)$) and through amplitude-dependent bias. That is the AM–PM mechanism below, and it is how low-frequency tail-current noise reaches the phase of a cross-coupled LC VCO. A tail filter, which presents a high impedance at $2f_0$, removes the $2f_0$ tail noise that the switching pair would otherwise mix to near the carrier [10].
- **Large kicks and injection locking.** For big injected signals the phase response becomes nonlinear (Adler locking, pulling; see [transmitter architectures](transmitter-architectures.md#level-2)). The ISF is a small-signal theory around the limit cycle.
- **Simulation practice.** Harmonic-balance or periodic-steady-state noise analysis (PSS/pnoise) computes the same quantities without hand ISFs ([16 harmonic balance](../16-simulation-tools/rf-circuit-simulators-harmonic-balance.md)). The ISF remains the design-intuition tool.

### AM-to-PM conversion (varactor tanks)
Let a fractional amplitude change $a=\Delta A/A$ shift the frequency by $\Delta f=\kappa a$, with $\kappa$ in Hz per unit relative AM. Then $S_{\Delta f}=\kappa^2S_a$, $S_\varphi=\kappa^2S_a/f_m^2$, and with $\mathcal L_{AM}=S_a/2$:
$$\mathcal L_{PM\leftarrow AM}(f_m)=\mathcal L_{AM}(f_m)+20\log_{10}(\kappa/f_m).$$
For a varactor, the large-signal fundamental capacitance $C_{eff}(A)=Q_1/A$ (first Fourier coefficient of the junction charge) grows with RF swing through the curvature of $C(V)$. The script uses a $C_{j0}$ = 10 pF, φ = 0.7 V, γ = 1 junction at 2 V bias in parallel with 5 pF at 433 MHz. That gives κ = 0.20 MHz per 100 % AM at 0.2 V swing and 1.31 MHz at 0.5 V. With $\mathcal L_{AM}=-130$ dBc/Hz at 100 kHz, the AM-to-PM term is −124 and −108 dBc/Hz respectively (§G). The cures are to keep the RF swing on the varactor small (tap it down), let the varactor be a small share of the tank C (lower $K_v$, band-switched capacitor banks), and use anti-series pairs. Anti-series pairs halve the swing per junction and cancel odd-order terms of $C(V)$, but even-order terms still shift the mean capacitance.

### Microphonics and acceleration sensitivity
A quartz resonator's fractional frequency follows acceleration along a sensitivity vector, $\Delta f/f_0=\boldsymbol\Gamma_g\cdot\mathbf a$, with $|\boldsymbol\Gamma_g|=\sqrt{\Gamma_1^2+\Gamma_2^2+\Gamma_3^2}$ in "per g". Vig's tutorial gives the following [8]:
- **Sine vibration** of peak $A$ (g) at $f_v$ is FM with $\Delta f=\boldsymbol\Gamma_g\cdot\mathbf Af_0$ and index $\beta=\Delta f/f_v$. For small β the first sidebands are $J_1(\beta)^2\approx(\beta/2)^2$:
$$\mathcal L'(f_v)=20\log_{10}\frac{\Gamma_gAf_0}{2f_v}\ \text{dBc (discrete lines at }\pm f_v).$$
- **Random vibration** of one-sided acceleration PSD $G(f)$ (g²/Hz) gives
$$\mathcal L(f)=20\log_{10}\frac{\Gamma_gf_0\sqrt{2G(f)}}{2f}\ \text{dBc/Hz},\qquad S_\varphi(f)=\frac{(\Gamma_gf_0)^2G(f)}{f^2}.$$
Both scale as $f_0$, so multiplication by N adds 20 log N, as any phase modulation does ([multipliers](frequency-multipliers-dividers.md)). Vig's checks are reproduced in §H. For 10 MHz, 10⁻⁹/g and 1 g sine: −46/−66/−86 dBc at 1/10/100 Hz. For 0.1 g²/Hz random: −53 dBc/Hz at 1 Hz.
- **Typical Γ** [8]: nearly all quartz resonators of every cut, from 5 MHz overtones to 500 MHz fundamentals, fall within a factor of three of 10⁻⁹/g. The best commercial SC-cuts reach low parts in 10¹⁰/g. Tuning-fork watch crystals are parts in 10⁷/g. Γ also varies with vibration frequency, rising near mounting resonances. Semtech lists 2 ppb/g as a typical crystal specification ([04 crystals](../04-real-components-hf/crystals-and-resonators.md)). Vig's environment table lists missile boost at 15 g peak.
- **LC oscillators** are microphonic through inductor turns moving, the PCB flexing under tank capacitors, shield lids moving (they are part of the tank's stray capacitance), and class-II MLCCs. X7R/X5R parts are piezoelectric: they change capacitance and *generate* voltage under stress, which is FM noise when they sit on a tuning line or in a loop filter ([MLCC page](../04-real-components-hf/capacitors-at-rf-mlcc.md)).

## Design equations & rules of thumb

| Equation | Valid when | Typical numbers |
|---|---|---|
| Leeson (Rubiola): $\frac{FkT}{2P_s}(1+(\frac{f_0}{2Q_Lf_m})^2)(1+\frac{f_c}{f_m})$ | feedback oscillator, $P_s$ at amp input | 433 MHz, $Q_L$ 20, F 10 dB, 0 dBm: −126 dBc/Hz @100 kHz, floor −167 |
| Tank form $\frac{2kT}{P_{tank}}(\frac{f_0}{2Qf_m})^2$ ×F | parallel RLC, tank-dissipated power | 12 nH, Q 30, 1 V: −131 dBc/Hz @100 kHz |
| $\mathcal L=\Gamma_{rms}^2(\overline{i_n^2}/\Delta f)/(2q_{max}^2\Delta\omega^2)$ | white, stationary source; use $\Gamma_{eff}=\Gamma\alpha$ if cyclostationary | LC: $\Gamma_{rms}=0.707$; ring ≈ 1 |
| $f_{1/f^3}=f_{1/f}(\Gamma_{dc}/\Gamma_{rms})^2$ | low-frequency noise into a node | symmetric ≈ 0; 10 % asymmetry → 1 % of $f_{1/f}$ |
| $\mathcal L_{PM}=\mathcal L_{AM}+20\log(\kappa/f_m)$ | small AM, AM→FM coefficient κ | varactor swing 0.5 V: +22 dB @100 kHz |
| $\mathcal L'(f_v)=20\log(\Gamma_gAf_0/2f_v)$ | sine vibration, β ≪ 1 | 2 ppb/g, 10 g, 200 Hz, 915 MHz: −26.8 dBc |
| $\mathcal L(f)=20\log(\Gamma_gf_0\sqrt{2G}/2f)$ | random vibration | 1 ppb/g, 0.16 g²/Hz, 433.92 MHz: −58 dBc/Hz @100 Hz |
| $\Delta f_{FWHM}=2\pi f_m^2\mathcal L(f_m)$ | 1/f² region, Lorentzian line | −131 dBc/Hz @100 kHz → 5 mHz |
| Isolator $T=\sqrt{\frac{1+(2\zeta r)^2}{(1-r^2)^2+(2\zeta r)^2}}$, $r=f/f_n$ | single-DOF mount | ζ 0.1: +14 dB at $f_n$, 0 dB at $\sqrt2f_n$, −33 dB at $10f_n$ |

Rules of thumb:
- **Maximise $q_{max}$.** Use the largest swing the devices and supply allow, and as much tank C as the tuning range permits. Phase noise falls 6 dB per doubling of swing at fixed noise.
- **Make waveforms symmetric** (matched NMOS/PMOS in complementary cross-coupled VCOs, matched rise and fall in rings) to keep the 1/f³ corner low.
- **Inject noise where Γ is small.** Use class-C/Colpitts-like current pulses at the voltage extremes and filter the tail source at $2f_0$.
- **Keep varactors lightly used.** Small RF swing on the junction and a small share of the tank C mean low $K_v$ and less AM–PM. Use C0G/NP0 capacitors in the tank, tuning line and loop filter.
- **Vibration:** pick a low-g reference and point its worst axis away from thrust, keep the VCO inside a wide PLL, and don't count on isolators below about $\sqrt2f_n$.

## Worked examples

### Example 1 — Tank-noise limit of a discrete 433 MHz LC VCO
Take $L$ = 12 nH with tank Q = 30 and 1 V peak across the tank. Then $R=Q\omega_0L$ = 979 Ω, $C=1/(\omega_0^2L)$ = 11.26 pF, and $P_{tank}=V_0^2/2R$ = 0.51 mW (−2.9 dBm). The ISF/tank formula gives
$\mathcal L$ = kT/(R C² V₀² Δω²) = −110.9 / −130.9 / −150.9 dBc/Hz at 10 k / 100 k / 1 MHz (script §F).
An active device adding as much noise as the tank ($F$ = 2) moves these 3 dB worse, to −128 dBc/Hz at 100 kHz. That sits in the range of good discrete UHF VCOs ([VCO & PLL](vco-and-pll-synthesizers.md)). Doubling the swing to 2 V buys 6 dB. Doubling Q at the same swing buys 3 dB ($R$ doubles, so $1/RC^2$ halves) and also halves the power needed; at the same *power* it buys 6 dB, which is the familiar $1/Q^2$. Halving L at the same swing doubles $C$ and $q_{max}$ but halves $R$ (more noise current), for a net 3 dB, at twice the power.

### Example 2 — Why the ring VCO in a cheap MCU or SDR clock has a high 1/f³ corner
Suppose a CMOS ring has a device 1/f corner of 1 MHz. With matched rise and fall the phase-noise 1/f³ corner is near zero. With the pull-up 0.4× weaker (a typical sizing error), $\Gamma_{dc}/\Gamma_{rms}$ = 0.104 and the corner moves to 10.8 kHz (script §E). Below 10.8 kHz the close-in noise then rises at 30 dB/decade instead of 20, which hurts integrated jitter from low frequencies. The fixes are to size for symmetric edges, or to use differential stages, where common-mode (asymmetric) noise rejection helps.

### Example 3 — g-sensitivity on a rocket: what each radio sees
Assume a 1 ppb/g TCXO and a NASA-GEVS-like random profile, 14.1 g_rms: +6 dB/oct from 20 Hz, 0.16 g²/Hz from 50 to 800 Hz, −6 dB/oct to 2 kHz. This is the same profile as the GNSS page, and the script integrates 20–2000 Hz:

| Carrier | $\mathcal L$(100 Hz) | $\mathcal L$(1 kHz) | Integrated (20–2000 Hz) | rms Δf |
|---|---|---|---|---|
| 433.92 MHz (E22 LoRa) | −58.2 dBc/Hz | −80.2 dBc/Hz | 1.76° rms | 6.1 Hz |
| 915 MHz (E220) | −51.7 | −73.7 | 3.71° | 12.9 Hz |
| 1575.42 MHz (GPS L1) | −47.0 | −69.0 | 6.39° | 22.2 Hz |
| 24.125 GHz radar LO | −23.3 | −45.3 | ≈ 98° (small-angle model invalid) | 341 Hz |

What it means:
- LoRa's chirp demodulator only cares about tens of hertz of frequency error over a packet, so 6–13 Hz rms of fast FM is harmless. The *static* boost shift (15 g × 2 ppb/g = 27 Hz at 915 MHz) matters more ([04 crystals](../04-real-components-hf/crystals-and-resonators.md), [LoRa impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)).
- GNSS loses 6.4° of its ≈ 15° PLL jitter budget.
- A coherent 24 GHz Doppler radar driven from the same class of reference is ruined unless the reference is low-g, isolated, or compensated.

### Example 4 — A motor resonance on 915 MHz
Take 10 g sine at 200 Hz (a structural resonance) and a 2 ppb/g crystal. The peak deviation is $2\times10^{-9}\cdot10\cdot915$ MHz = 18.3 Hz, β = 0.0915, and the spurs at ±200 Hz are **−26.8 dBc** (script §H). On a spectrum analyser these look alarming. For FSK/LoRa they are only an 18 Hz wobble. For a narrowband CW beacon receiver with a 100 Hz filter, the beacon smears.

### Example 5 — Does the PLL clean it up?
Take a 32 MHz TCXO × 28.6 → 915 MHz with a 100 kHz type-II loop.
- **VCO microphonics** (the LC tank shaking) at 100 Hz–1 kHz are high-pass shaped by $\approx(f/f_{BW})^2$, giving 120 dB of suppression at 100 Hz and 80 dB at 1 kHz.
- **Reference g-sensitivity** lies far inside the loop bandwidth, so it passes straight to the output with +20 log(915/32) = +29.1 dB relative to the TCXO's own sidebands. That is the same as using $f_0$ = 915 MHz in Vig's formula.
- So: put the money into the reference crystal and its mounting, not the VCO.

### Example 6 — Should I vibration-isolate the TCXO?
Consider a single-degree-of-freedom elastomer mount with $f_n$ = 100 Hz and ζ = 0.1. It **amplifies** by +2.5 dB at 50 Hz and +14 dB at 100 Hz, passes 0 dB at 141 Hz, and attenuates −17 dB at 300 Hz and −33 dB at 1 kHz (script §H; Vig shows the same shape [8]). On a rocket whose input spectrum is strongest at 50–800 Hz, an isolator tuned at 100 Hz makes things worse around 50–140 Hz. Isolation only pays when $f_n$ sits well below the band of concern, and that needs soft mounts, large sway space and shock tolerance. Usually a lower-Γ part and good orientation beat isolation.

### Example 7 — A crystal reference: Leeson in the "quartz" regime, and why vibration wins
A 32 MHz Pierce oscillator with $Q_L$ = 40 000 has a Leeson frequency $f_L=f_0/2Q_L$ = 400 Hz. Assume amplifier flicker corner 5 kHz, F = 6 dB and $P_s$ = −10 dBm. The Rubiola-form Leeson then gives −101.9 / −131.6 / −152.6 / −159.2 / −161.0 dBc/Hz at 10 Hz / 100 Hz / 1 kHz / 10 kHz / floor. The local slope near 1.4 kHz is −9.3 dB/decade, the 1/f "flicker phase" region between $f_L$ and $f_c$ (script §F). Multiplied to 915 MHz in the PLL (+29.1 dB) that is −102.5 dBc/Hz at 100 Hz and −123.4 at 1 kHz *at rest*. Under the GEVS-like vibration of Example 3 the same reference at 1 ppb/g contributes **−51.7 dBc/Hz at 100 Hz**, about 50 dB worse. On a rocket, the at-rest phase-noise specification of the reference is almost irrelevant below a few kHz; its g-sensitivity is what counts.

### Example 8 — Reading a VCO data sheet with ISF eyes
A data sheet shows −30 dB/decade below 20 kHz and −20 dB/decade above. The 20 kHz is the phase-noise 1/f³ corner. If the process's MOS 1/f corner is around 1 MHz, the corner ratio implies $(\Gamma_{dc}/\Gamma_{rms})^2\approx0.02$, i.e. $\Gamma_{dc}/\Gamma_{rms}\approx0.14$. That much waveform asymmetry, or equivalent AM–PM through the varactors, is the target for improvement. A loop bandwidth of 100–200 kHz hides the 1/f³ region entirely inside the PLL, so for a synthesiser the corner matters mainly for the loop-bandwidth choice ([VCO & PLL](vco-and-pll-synthesizers.md#example-3--choosing-the-loop-bandwidth)).

## Practical notes
- **Measuring Γ_g:** put the oscillator (or the whole board) on a shaker. Apply a known sine on each axis and read the ±$f_v$ sidebands on a spectrum analyser or phase-noise analyser. Invert $\mathcal L'=20\log(\Gamma A f_0/2f_v)$ to get Γ per axis. Without a shaker, a loudspeaker cone gives a qualitative check at low g. Measure through the PLL output for the system number. ([17 phase-noise measurement](../17-test-measurement/phase-noise-measurement.md))
- **Orientation:** the static thrust acceleration shifts frequency by $\boldsymbol\Gamma_g\cdot\mathbf a$. If the data sheet gives per-axis Γ, put the smallest component along the rocket's long axis.
- **Board practice for LC VCOs:** use C0G in tank, tuning and loop-filter positions; X7R MLCCs on a tuning line can produce audible-band FM when the board is tapped. Glue or pot heavy inductors; stitch shield lids at many points so they don't drum; keep the VCO tank away from board-flex regions such as connectors and mounting screws.
- **Simulation:** the ISF of a real circuit can be extracted in SPICE by injecting a short current pulse at many phases (`.tran` with a PWL source) and comparing zero-crossings with an unkicked run. That is exactly what `rf2_isf.py` does on behavioural models. PSS/pnoise in a harmonic-balance simulator gives the full answer.
- **Quick vibration budget for a flight radio:**
  1. Take the reference's Γ (assume 1–2 ppb/g if unknown).
  2. Take the vehicle's random-vibration PSD at the mounting point; it is often 0.04–0.2 g²/Hz across 50–800 Hz for small solid motors, so measure it with the flight computer's own accelerometer log if possible.
  3. Evaluate $\mathcal L(f)$ at the output frequency with the formula above, and integrate $S_\varphi$ over the offsets your demodulator cares about. For GNSS that is the carrier-loop bandwidth up to about 2 kHz. For LoRa only the static shift and slow drift matter. For coherent radar it is the Doppler band.
- **Two sides of one effect:** vibration sidebands are coherent across all oscillators locked to the same reference. On a rocket where GNSS, LoRa and a radar altimeter share one TCXO, all of them see the same correlated FM. That can be an advantage: a GNSS-disciplined estimate of the frequency error can correct the others.
- **Data-sheet reading:** "−130 dBc/Hz at 100 kHz" says nothing about vibration. Look for g-sensitivity (ppb/g per axis) or "phase noise under vibration", common on OCXOs and radar references, rare on cheap TCXOs.

## Common mistakes & misconceptions
- *"Leeson's F is the amplifier noise figure from the data sheet."* It is a fitting factor that absorbs cyclostationary weighting, up-conversion and loading. The ISF explains why it differs from the small-signal NF.
- *"The 1/f³ corner equals the transistor's 1/f corner."* It is lower by $(\Gamma_{dc}/\Gamma_{rms})^2$ and can be orders of magnitude lower for symmetric waveforms [3].
- *"2FkT/Ps and FkT/(2Ps) can't both be right."* They use different powers (tank-dissipated vs amplifier-input carrier). Mixing them silently gives 6 dB errors. This KB uses the Rubiola form for Leeson and labels the tank form explicitly.
- *"Bigger varactor = better VCO."* More tuning range brings more AM–PM and more tuning-line noise ([07](../07-noise-linearity/phase-noise-and-jitter.md)).
- *"A PLL removes vibration noise."* It removes the VCO's own microphonics inside its bandwidth but multiplies the reference's by N.
- *"Mounting the oscillator on rubber fixes vibration."* Only above $\sqrt2f_n$; at and near resonance it amplifies.
- *"Phase-noise numbers apply at any offset."* $\mathcal L(f)$ assumes small phase deviation. The 24 GHz vibration case (≈ 98° rms) is outside that regime, and there the carrier itself collapses into a smeared line.

## How to simulate / verify
- `python3 tools/verify/rf2_isf.py` (≈ 30 s, ALL PASS) covers: §A analytic LC ISF; §B stochastic van der Pol phase diffusion vs the Hajimiri–Lee formula and the tank/Rubiola 6.02 dB mapping; §C numerical ISF by impulse injection (LC, symmetric and asymmetric rings); §D slow and near-carrier injection vs $\Gamma_{dc}$ and $c_1$ predictions; §E 1/f³ corners; §F Leeson numbers (consistent with [07](../07-noise-linearity/phase-noise-and-jitter.md)) and the 433 MHz tank example; §G varactor AM–PM; §H Vig formulas, GEVS profile at four carriers, PLL scaling, isolator transmissibility, Lorentzian width.
- To check a real design, run PSS + pnoise (Spectre, ADS, Xyce HB) or an ngspice transient with impulse injection; measure with a phase-noise analyser or a cross-correlation SDR setup ([17](../17-test-measurement/phase-noise-measurement.md)).

## Open questions / gaps
- Rubiola's book was not re-read this session; the Leeson form follows the W4-D6 settlement (FkT/(2Ps)).
- The Hajimiri–Lee PDFs are image-equation scans: the formulas here are re-derived and verified numerically, not transcribed.
- The tail-current filtering result [10] and Demir's theory [7] are cited from memory and not re-read (their bibliographic data were checked against Crossref by W5-S18b on 2026-10-13).
- No measured g-sensitivity is available for the TCXOs in EBYTE E22/E220 modules or u-blox receivers. A shaker test is recommended before flight; it is also listed as a gap in [04](../04-real-components-hf/crystals-and-resonators.md) and [21](../21-gnss/gnss-on-rockets-dynamics-and-limits.md).
- The GEVS profile is a qualification envelope, not a measured flight spectrum for a student solid motor.
- *Resolved (W5-S17, 2026-10-13, `tools/verify/s17_leeson_check.py`):* the 07 page's −164 dBc/Hz is $\mathcal L$(10 MHz) = −163.6 dBc/Hz, which lies inside the 10.8 MHz corner; the floor is −167 dBc/Hz as stated there. The 07 wording was clarified. No discrepancy remains.

## Sources
1. D. B. Leeson, "A simple model of feedback oscillator noise spectrum," *Proc. IEEE* 54(2), 329–330, 1966. (peer-reviewed) — Leeson model.
2. E. Rubiola, *Phase Noise and Frequency Stability in Oscillators*, Cambridge Univ. Press, 2008, ch. 1–3 (Leeson effect; $b_0=FkT/P_0$; $\mathcal L=S_\varphi/2$; $f_L$ vs $f_c$ cases). (textbook; form settled by the W4-D6 audit, not re-read here)
3. A. Hajimiri, T. H. Lee, "A general theory of phase noise in electrical oscillators," *IEEE J. Solid-State Circuits* 33(2), 179–194, Feb. 1998. https://people.engr.tamu.edu/spalermo/ecen620/general_pn_theory_hajimiri_jssc_1998.pdf (peer-reviewed; read: ISF definition, LTV superposition, cyclostationary NMF, 1/f³ corner from $c_0$, LTI model "two times larger", reduction to Leeson with F)
4. T. H. Lee, A. Hajimiri, "Oscillator phase noise: a tutorial," *IEEE J. Solid-State Circuits* 35(3), 326–336, Mar. 2000. http://smirc.stanford.edu/papers/JSSC00MAR-tom.pdf (peer-reviewed; read: tank-only model with equipartition, eq. (12) and Leeson-modified (13))
5. B. Razavi, *RF Microelectronics*, 2nd ed., Prentice Hall, 2011, §8.7 (phase-noise analysis I/II, LTV). (textbook; not re-read)
6. T. H. Lee, *The Design of CMOS Radio-Frequency Integrated Circuits*, 2nd ed., Cambridge, 2004, ch. 18. (textbook; not re-read)
7. A. Demir, A. Mehrotra, J. Roychowdhury, "Phase noise in oscillators: a unifying theory and numerical methods for characterization," *IEEE Trans. Circuits Syst. I* 47(5), 655–674, 2000. (peer-reviewed; cited for the Lorentzian line shape; bibliographic data checked against Crossref by W5-S18b, 2026-10-13)
8. J. R. Vig, "Quartz crystal resonators and oscillators for frequency control and timing applications — a tutorial," rev. 8.5.2.0, 2004, slides 4-63 to 4-77 (acceleration levels, Γ vector, sine/random vibration formulas and tables, sensitivity ranges, isolation, compensation). https://www.pletronics.com/wp-content/uploads/2025/08/Vig_tutorial.pdf (technical tutorial; read)
9. R. L. Filler, "The acceleration sensitivity of quartz crystal oscillators: a review," *IEEE Trans. UFFC* 35(3), 297–305, 1988. (peer-reviewed; via [8] and 04 page)
10. E. Hegazi, H. Sjöland, A. A. Abidi, "A filtering technique to lower LC oscillator phase noise," *IEEE J. Solid-State Circuits* 36(12), 1921–1930, Dec. 2001. (peer-reviewed; cited, not re-read; bibliographic data checked against Crossref by W5-S18b, 2026-10-13)
11. NASA GSFC-STD-7000 (GEVS), random-vibration qualification envelope (shape as used in `tools/verify/gnss_tracking_loops.py`). (standard)
12. IEEE Std 1139-2008 (definitions of $\mathcal L(f)$, $S_\varphi$). (standard)
13. `tools/verify/rf2_isf.py` (this KB).
