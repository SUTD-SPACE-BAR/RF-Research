---
title: Volterra series and weakly nonlinear analysis — kernels, the method of nonlinear currents, IIP3 with memory, AM–PM, behavioural PA models and DPD
domain: 07-noise-linearity
slug: volterra-series-and-nonlinear-analysis
tags: [volterra-series, volterra-kernels, nonlinear-transfer-function, method-of-nonlinear-currents, harmonic-input-method, intermodulation, IIP3, memory-effects, second-order-interaction, bias-network, IM3-asymmetry, sweet-spot, AM-PM, describing-function, wiener-hammerstein, saleh, rapp, memory-polynomial, GMP, digital-predistortion, indirect-learning, ACLR]
prerequisites:
  - nonlinearity-p1db-ip3-intermod.md
  - ../00-math-foundations/linear-systems-convolution.md
  - ../00-math-foundations/fourier-series-and-transform.md
  - ../00-math-foundations/complex-numbers-and-phasors.md
related:
  - dynamic-range-sfdr-blocking.md
  - receiver-cascade-analysis.md
  - ../06-rf-circuits/power-amplifiers.md
  - ../06-rf-circuits/lna-design.md
  - ../06-rf-circuits/mixers.md
  - ../06-rf-circuits/transmitter-architectures.md
  - ../05-analog-electronics/bjt-fundamentals-small-signal.md
  - ../16-simulation-tools/rf-circuit-simulators-harmonic-balance.md
  - ../10-comms-modulation/ofdm.md
level: advanced
confidence: medium
last_updated: 2026-10-13
---

# Volterra series and weakly nonlinear analysis

## Questions this page answers
- What is a Volterra series, and how is it different from the power series $y=a_1x+a_2x^2+a_3x^3$?
- How do I compute IM3 and IIP3 of a circuit with capacitors, inductors and feedback, where the "coefficients" depend on frequency?
- What is the method of nonlinear currents?
- Why does an amplifier's IM3 change with tone spacing, and why are the lower and upper IM3 products sometimes unequal?
- Why can emitter or source degeneration make IM3 almost vanish (a "sweet spot")?
- When does the power-series / Volterra model stop being valid?
- What is AM–PM conversion physically, and how does it come out of the Volterra kernels?
- What are the Saleh, Rapp and memory-polynomial models, and how do they relate to digital predistortion?
- Why does my two-tone IIP3 measurement change when I change the tone spacing?
- Does a constant-envelope LoRa transmitter need any of this?

## TL;DR
- A **power series** ($y=\sum a_nx^n$) describes a *memoryless* nonlinearity: the output depends only on the input at the same instant. Real RF circuits have **memory**: capacitors, inductors, bias networks, thermal time constants. A **Volterra series** is a power series with memory, $y(t)=\sum_n\int\!\cdots\!\int h_n(\tau_1,\dots,\tau_n)\prod x(t-\tau_i)\,d\tau_i$. Its Fourier transforms $H_n(f_1,\dots,f_n)$ are "nonlinear transfer functions".
- **IM3 with memory:**
  - for two tones of amplitude A, the IM3 at $2f_1-f_2$ has amplitude $\tfrac34|H_3(f_1,f_1,-f_2)|A^3$;
  - the per-tone IIP3 amplitude is $A_\text{IIP3}^2=\tfrac43|H_1(f)/H_3(f_1,f_1,-f_2)|$, which reduces to $\tfrac43|a_1/a_3|$ for a memoryless cubic;
  - checked exactly (< 0.5 %) on a Wiener–Hammerstein block (filter → cubic → filter).
- **Method of nonlinear currents.** Solve the *linear* circuit repeatedly. At order n, each nonlinear element becomes a current source driven by lower-order voltages. For a transconductor $i=g_1v+g_2v^2+g_3v^3$ with a series feedback impedance $Z(\omega)$:
$$g_{3,\text{eff}}=g_3-\tfrac23g_2^2\!\!\sum_{\text{pairs}}\frac{Z(\omega_\text{pair})}{1+g_1Z(\omega_\text{pair})}.$$
  This **second-order interaction** depends on Z at the *difference* frequency $f_2-f_1$ and at $2f$. That is why IM3 depends on tone spacing and on baseband and bias impedances.
- **Worked case** (BJT at 1 mA, $R_E$ = 25 Ω bypassed above 1 MHz):
  - IM3 changes by **31 dB** as tone spacing goes from 0.1 to 5 MHz;
  - IIP3 moves from **+3.5 dBm** (spacing ≪ 1 MHz, where degeneration acts and nearly cancels $g_3$: a sweet spot) to **−12.6 dBm** (spacing ≫ 1 MHz: the bare BJT, $A_\text{IIP3}=2\sqrt2V_T$ = 73.5 mV);
  - lower and upper IM3 differ by up to **9.2 dB**;
  - Volterra matches a time-domain ODE simulation within 0.32 dB (`e11_volterra.py`).
- **Limits.** The series converges only for weak nonlinearity. For tanh, the cubic (3rd-order) IM3 prediction is within 0.1 dB at 30 dB below P1dB, is −1.2 dB off at A = 0.3, and **−3.1 dB off at A = 0.5** (near compression). Near saturation use harmonic balance, describing functions or behavioural models.
- **AM–PM** in Volterra terms: the complex third-order kernel $H_3(f,f,-f)$ makes the fundamental's gain $G(A)=H_1+\tfrac34H_3A^2$ change *phase* with amplitude. Behavioural models fit AM–AM and AM–PM directly:
  - **Saleh** (TWT): $A(r)=\frac{2.1587r}{1+1.1517r^2}$, $\Phi(r)=\frac{4.0033r^2}{1+9.104r^2}$;
  - **Rapp** (solid-state, AM–AM only);
  - the **memory polynomial**, $y(n)=\sum_k\sum_ma_{km}x(n-m)|x(n-m)|^{k-1}$: a pruned Volterra series, and the standard DPD basis.

## Intuition (no math)
A power-series amplifier is like a spring that gets stiffer the more you stretch it: the restoring force depends only on the stretch *now*. Feed it two tones and it produces mixing products whose sizes follow from the coefficients alone.

A real transistor stage is a spring attached to dampers and masses: bias capacitors, emitter bypass capacitors, supply inductors, its own junction capacitances. When two tones 200 kHz apart go in, the squared term creates a 200 kHz "beat" current and a 2f current. These currents flow through the bias network, whose impedance at 200 kHz may be completely different from its impedance at RF. They create small voltages back at the transistor's input, which then *mix again* with the original tones and produce more third-order products. Whether these add to or cancel the device's own cubic term depends on the impedance at the beat frequency. So the same transistor can have a very different IM3 at 200 kHz spacing than at 20 MHz spacing. That is a **memory effect**.

A Volterra series is the bookkeeping that tracks every such path. The first-order kernel is the ordinary frequency response. The second-order kernel says how two input frequencies combine into a sum or difference frequency, including the impedances along the way. The third-order kernel says how three combine. The method of nonlinear currents is the practical way to fill in the kernels for a circuit: solve the linear circuit, inject the squared terms as new current sources, solve again, and so on.

## The math

### Level 1 — what the kernels are and what you compute

| Symbol | Meaning | Units (y current, x voltage) |
|---|---|---|
| $H_1(f)$ | small-signal transfer function | A/V |
| $H_2(f_a,f_b)$ | gain from $x(f_a)x(f_b)$ to $y(f_a+f_b)$ | A/V² |
| $H_3(f_a,f_b,f_c)$ | gain from $x(f_a)x(f_b)x(f_c)$ to $y(f_a+f_b+f_c)$ | A/V³ |

For an input $A\cos\omega_1t+A\cos\omega_2t$, with kernels symmetric in their arguments:

| Product | Frequency | Output amplitude |
|---|---|---|
| fundamental | $f_1$ | $|H_1(f_1)|A$ (+ compression terms $\tfrac34\cdot2H_3(f_1,f_2,-f_2)A^3$ …) |
| IM2 | $f_2\pm f_1$ | $|H_2(f_2,\pm f_1)|A^2$ |
| HD2 | $2f_1$ | $\tfrac12|H_2(f_1,f_1)|A^2$ |
| IM3 (lower) | $2f_1-f_2$ | $\tfrac34|H_3(f_1,f_1,-f_2)|A^3$ |
| IM3 (upper) | $2f_2-f_1$ | $\tfrac34|H_3(f_2,f_2,-f_1)|A^3$ |
| HD3 | $3f_1$ | $\tfrac14|H_3(f_1,f_1,f_1)|A^3$ |

$$A_\text{IIP3}^2=\frac43\left|\frac{H_1(f_1)}{H_3(f_1,f_1,-f_2)}\right|\qquad\text{(per-tone amplitude; } P=A^2/2R\text{).}$$
For a memoryless block $H_n=a_n$, and these reduce to the table in [nonlinearity](nonlinearity-p1db-ip3-intermod.md).

### Level 1½ — from a power series to "kernels", algebra only
- **Start memoryless.** Write the amplifier as $y = a_1x + a_3x^3$, with $a_3 < 0$ for compression. Put in two tones of amplitude $A$ and expand the cube. The term at $2f_1 - f_2$ has amplitude $\tfrac34|a_3|A^3$, while the wanted output is $a_1A$.
- **IM3 relative to the tone** is therefore $\tfrac34|a_3/a_1|A^2$. It grows as $A^2$: one dB more drive gives 2 dB worse IM3 in dBc.
- **IIP3.** The input where the two would be equal is $A_{IIP3}^2 = \tfrac43|a_1/a_3|$. In dB, IM3 (dBc) = $2(P_{in} - IIP3)$.
- **Add memory.** A Volterra kernel is the same coefficient allowed to depend on the frequencies involved: $a_1 \to H_1(f)$ and $a_3 \to H_3(f_a, f_b, f_c)$. The lower product uses $H_3(f_1, f_1, -f_2)$ and the upper one uses $H_3(f_2, f_2, -f_1)$. If a bias network or a matching network makes these two numbers differ, the two IM3 sidebands differ, and IIP3 changes with tone spacing. A plain power series can never show this.

*Worked numbers (verified, `tools/verify/s18_level15_numbers.py`, including a direct two-tone FFT).* Take $a_1$ = 10 (20 dB) and $a_3$ = −4/3 V⁻² in a 50 Ω system:
- **IIP3:** $A_{IIP3} = \sqrt{10}$ = 3.16 V, i.e. +20 dBm per tone.
- **IM3:** at −10 dBm per tone (A = 0.1 V) the IM3 is $\tfrac34(0.1333)(0.01)$ = 10⁻³ of the tone, i.e. **−60 dBc**, which is 2 × (−10 − 20) dB.
- **Memory:** if a baseband impedance makes $|H_3|$ 1.2× larger at the lower product, the lower sideband reads 1.6 dB higher than the upper one.

### Level 2 — derivations

**1. Definition and frequency-domain kernels.** A causal, time-invariant, weakly nonlinear system with fading memory can be written
$$y(t)=\sum_{n=1}^{N}\int\!\!\cdots\!\!\int h_n(\tau_1,\ldots,\tau_n)\,x(t-\tau_1)\cdots x(t-\tau_n)\,d\tau_1\cdots d\tau_n .$$
The n-th term is an n-fold convolution, and $h_1$ is the impulse response. The n-dimensional Fourier transform $H_n(f_1,\dots,f_n)$ can always be **symmetrised** (averaged over all permutations of its arguments) without changing y. Symmetric kernels are assumed from here on.

**2. Where the 3/4 comes from (the harmonic-input / probing method).** Write the input as a sum of complex exponentials, $x=\sum_{q=\pm1,\pm2}\tfrac A2e^{j\omega_qt}$, with $\omega_{-q}=-\omega_q$. The third-order term is then
$$y_3=\sum_{q_1,q_2,q_3}\left(\tfrac A2\right)^3H_3(\omega_{q_1},\omega_{q_2},\omega_{q_3})e^{j(\omega_{q_1}+\omega_{q_2}+\omega_{q_3})t}.$$
The frequency $2\omega_1-\omega_2$ arises from the ordered triples (1,1,−2), (1,−2,1) and (−2,1,1): **3 permutations**. Its complex amplitude is $3(A/2)^3H_3(\omega_1,\omega_1,-\omega_2)$. Adding the conjugate at $-(2\omega_1-\omega_2)$ gives a cosine of amplitude $2\cdot3(A/2)^3|H_3|=\tfrac34A^3|H_3|$.

The same counting gives the other entries of the Level 1 table. The fundamental's compression term $(\omega_1,\omega_1,-\omega_1)$ has 3 permutations, the cross-compression $(\omega_1,\omega_2,-\omega_2)$ has 6, and HD3 has 1. The **probing method** inverts this: to find $H_n$ of a circuit, drive it with n incommensurate exponentials, collect the coefficient of $e^{j(\omega_1+\cdots+\omega_n)t}$, and divide by $n!$ (for distinct frequencies).

**3. Cascades: the Wiener–Hammerstein block.** Take a linear filter A(f), a memoryless polynomial $\sum a_nu^n$, then a linear filter B(f). Then
$$H_n(f_1,\dots,f_n)=a_nA(f_1)\cdots A(f_n)\,B(f_1+\cdots+f_n).$$
The output filter is evaluated at the **sum (output) frequency**, and the input filter at each input frequency. The script's case (2nd-order low-pass in, 1st-order low-pass out, tones at 4 and 4.25 in units where $f_s$ = 64) agrees with simulation to 10⁻⁵.

**4. The method of nonlinear currents.** Expand every nonlinear element in a power series about its bias point. For a voltage-controlled current source, $i=g_1v+g_2v^2+g_3v^3$.
1. **Order 1:** solve the linear circuit, in which the device is just $g_1$, with the actual source. This gives the first-order node voltages $v^{(1)}(\omega)$.
2. **Order 2:** set the external sources to zero. Place a current source $i_{NL}^{(2)}=g_2v^{(1)}(\omega_a)v^{(1)}(\omega_b)$ in parallel with each $g_1$, at $\omega_a+\omega_b$, and solve the *same* linear circuit at $\omega_a+\omega_b$. This gives $v^{(2)}$.
3. **Order 3:** inject $i_{NL}^{(3)}=2g_2\,\overline{v^{(1)}v^{(2)}}+g_3v^{(1)}v^{(1)}v^{(1)}$ (overline = symmetrised over the arguments) at $\omega_a+\omega_b+\omega_c$, and solve again.

Every step is a linear AC analysis. This is exactly how SPICE-style "distortion analysis" and Volterra-based circuit tools work (Maas; Wambacq & Sansen) [1][2].

**5. Worked derivation: a degenerated transconductor.** Let a transconductor $i=g_1v+g_2v^2+g_3v^3$ have control voltage $v=v_s-Z(\omega)i$, where Z is emitter or source degeneration, possibly bypassed. Define $H_v(\omega)=1/(1+g_1Z(\omega))$ and $P(\omega)=Z(\omega)/(1+g_1Z(\omega))$.
- **Order 1:** $i_1=g_1H_v\,v_s$ and $v_1=H_v\,v_s$.
- **Order 2:** $i_2=g_1v_2+g_2v_1v_1$ with $v_2=-Z\,i_2$, so $i_2=g_2v_1(\omega_a)v_1(\omega_b)H_v(\omega_a+\omega_b)$ and $v_2=-g_2P(\omega_a+\omega_b)\,v_1(\omega_a)v_1(\omega_b)$.
- **Order 3:** $i_3=g_1v_3+2g_2v_1v_2+g_3v_1^3$ with $v_3=-Z\,i_3$. Symmetrising the $v_1v_2$ term over the three ways of choosing which argument comes from $v_1$:
$$H_3(\omega_a,\omega_b,\omega_c)=\Big[g_3-\tfrac23g_2^2\big(P(\omega_a+\omega_b)+P(\omega_a+\omega_c)+P(\omega_b+\omega_c)\big)\Big]H_v(\omega_a)H_v(\omega_b)H_v(\omega_c)H_v(\omega_a+\omega_b+\omega_c).$$

For the **lower IM3** $(\omega_1,\omega_1,-\omega_2)$ the pairs are $2\omega_1$, $\omega_1-\omega_2=-\Delta\omega$ and $-\Delta\omega$:
$$g_{3,\text{eff}}^{(\text{low})}=g_3-\tfrac23g_2^2\left[P(2\omega_1)+2P(-\Delta\omega)\right],\qquad g_{3,\text{eff}}^{(\text{up})}=g_3-\tfrac23g_2^2\left[P(2\omega_2)+2P(+\Delta\omega)\right].$$
Three consequences:
1. **Spacing dependence.** IM3 depends on $Z(\Delta\omega)$, the impedance at the *beat* frequency, which is usually the bias network, decoupling or baseband. This is the dominant "electrical memory effect" of PAs and LNAs.
2. **Asymmetry.** $P(-\Delta\omega)=P(\Delta\omega)^*$. When P is complex (Δω near a bias-network corner) and $P(2\omega)$ also contributes, the two IM3 sidebands differ.
3. **Sweet spot.** For a BJT, $g_1=I_C/V_T$, $g_2=g_1/(2V_T)$ and $g_3=g_1/(6V_T^2)$. With $Z(\Delta\omega)=R_E$, $Z(2\omega)\approx0$ (bypassed at RF only) and $g_1R_E=1$: $\tfrac23g_2^2\cdot2\cdot\frac{R_E}{2}=\tfrac{g_1}{6V_T^2}=g_3$. The cubic term **cancels**, which is why the script's IM3 is −94 dBc at 0.1 MHz spacing. With full degeneration at all frequencies ($Z(2\omega)=R_E$ as well), $g_{3,\text{eff}}=g_3-g_2^2R_E=-g_3/2$: the sign flips.

**6. IIP3 with memory (numbers from the script).** Take $I_C$ = 1 mA ($g_1$ = 40 mS), $R_E$ = 25 Ω bypassed with a 1 MHz corner ($Z=R_E/(1+jf/f_c)$), tones near 20 MHz:

| Tone spacing | 1 kHz | 100 kHz | 1 MHz | 10 MHz | 100 MHz |
|---|---|---|---|---|---|
| $A_\text{IIP3}$ (mV per tone) | 473 | 468 | 114 | 75 | 74 |
| (dBm in 50 Ω, illustrative) | +3.5 | +3.4 | −8.9 | −12.5 | −12.6 |

At wide spacing the circuit is the bare BJT, with $A_\text{IIP3}=\sqrt{\tfrac43g_1/g_3}=2\sqrt2V_T$ = 73.5 mV, the classic result. **A two-tone test at 1 MHz spacing would mis-predict the 100 kHz-spaced interference behaviour by 12 dB.** That is why tone spacing must match the interference scenario ([nonlinearity, practical notes](nonlinearity-p1db-ip3-intermod.md)).

**7. AM–PM from the kernels.** For a single tone of amplitude A, the describing-function gain at the fundamental, to third order, is
$$G(A)=H_1(\omega)+\tfrac34H_3(\omega,\omega,-\omega)A^2 .$$
- If $H_3/H_1$ is real, only |G| changes: AM–AM (compression if negative, expansion if positive).
- If it has an imaginary part, $\angle G$ changes with A: **AM–PM**, approximately $\Delta\phi\approx\tfrac34\,\mathrm{Im}(H_3/H_1)A^2$ rad.

In the transconductor, $H_3(\omega,\omega,-\omega)$ contains $P(2\omega)$ and $P(0)$. A degeneration or bias impedance that is reactive at 2ω therefore produces AM–PM. Nonlinear capacitances ($C_{je}$, $C_{gd}$ versus voltage) do the same through nonlinear *charge* sources, $i=dq(v)/dt$, in the method of nonlinear currents. The script's single-tone check (30 MHz corner, 20 MHz tone) gives 0.004° at 4 mV against the Volterra prediction of 0.004°. That is tiny, because weakly nonlinear small-signal AM–PM is tiny. Large AM–PM (degrees) appears only near compression, where third order is no longer enough.

### Level 3 — limits of the model, behavioural models and the bridge to DPD

**Convergence and truncation.** A Volterra series of a memoryless nonlinearity is its Taylor series, so it converges only within the Taylor radius. tanh(x), for example, has poles at $x=\pm j\pi/2$. Long before that, *truncation* error dominates. The script compares the exact two-tone IM3 of tanh with the cubic prediction:

| Per-tone amplitude A | 0.05 | 0.1 | 0.2 | 0.3 | 0.5 | 0.7 |
|---|---|---|---|---|---|---|
| exact/cubic IM3 (dB) | −0.04 | −0.14 | −0.56 | −1.23 | −3.14 | −5.51 |

tanh's single-tone $A_\text{1dB}$ = 0.713 (a pure cubic predicts 0.660). So **third-order Volterra is good to ~0.5 dB up to about 10 dB below P1dB**, and fails at compression. Fifth-order terms (5:1 slope) take over near saturation, exactly as the 5 dB/dB IM3 slope of limiters in [nonlinearity](nonlinearity-p1db-ip3-intermod.md) shows. The near-cancellation sweet spot is also where fifth-order terms dominate the residual: the script's 0.32 dB disagreement (its one miss) is at −94 dBc, exactly there. For strongly driven PAs, use **harmonic balance** ([RF circuit simulators](../16-simulation-tools/rf-circuit-simulators-harmonic-balance.md)), load-pull data, or behavioural models fitted to measurement.

**Other limits.**
- Volterra assumes time invariance and fading memory. Long thermal memory (ms to s), charge trapping in GaN (asymmetric capture and emission time constants), and hysteresis are only approximately representable.
- The number of kernel coefficients grows as $M^n$ for memory depth M. That is why practical models prune the series.

**Behavioural (complex-baseband) models.** For bandpass PAs, model the complex envelope $\tilde x$ instead of the RF waveform. Only odd-order terms that fall back in band survive: $\tilde y=\sum_{k\,\text{odd}}a_k\tilde x|\tilde x|^{k-1}$.
- **Saleh (1981, TWT):** $A(r)=\frac{\alpha_ar}{1+\beta_ar^2}$, $\Phi(r)=\frac{\alpha_\phi r^2}{1+\beta_\phi r^2}$, with $(\alpha_a,\beta_a,\alpha_\phi,\beta_\phi)=(2.1587,1.1517,4.0033,9.1040)$. Saturation is at $r=1/\sqrt{\beta_a}$ = 0.932 with output $\alpha_a/(2\sqrt{\beta_a})$ = 1.006, and AM–PM there is 22.4°. (One secondary source gives $\alpha_\phi$ = 4.033; see Open questions.) [4]
- **Rapp (1991, solid-state PA):** $A(r)=\frac{Gr}{[1+(Gr/A_\text{sat})^{2p}]^{1/(2p)}}$, with no AM–PM. Smoothness p ≈ 2–3 for LDMOS/GaAs PAs. With p = 2, input P1dB is at 0.875 $A_\text{sat}/G$. [5]
- **Wiener / Hammerstein / Wiener–Hammerstein:** a linear filter and a static nonlinearity in cascade. Their kernels are products of filter responses (Level 2, §3).
- **Memory polynomial (Kim & Konstantinou 2001):** $\tilde y(n)=\sum_{k\,\text{odd}}^{K}\sum_{m=0}^{M}a_{km}\tilde x(n-m)|\tilde x(n-m)|^{k-1}$. This is the diagonal of the discrete Volterra series. It is linear in the coefficients, so it is fitted by least squares. **GMP** (generalised memory polynomial, Morgan et al. 2006) adds lagging and leading envelope cross-terms. [6][7]

**DPD.** A predistorter P is placed before the PA so that $PA(P(x))\approx Gx$.
- **Indirect learning:** fit a *post*-inverse $\hat P$ with $\hat P(y/G)\approx z$ (the PA input), then copy it in front of the PA. With the memory-polynomial basis, this is one least-squares solve per iteration.
- **The script's case:** a Wiener–Hammerstein PA (3-tap filters, Rapp p = 2 with AM–PM, filtered 16-QAM at ~8 dB back-off):
  - a memoryless 7th-order polynomial models the PA at **NMSE −25 dB**, and a memory polynomial (K = 7, M = 3) at **−59 dB**;
  - **ACLR** is −39.1 dBc without DPD, **−56.1 dBc** with memoryless DPD and **−60.4 dBc** with memory-polynomial DPD;
  - the memory DPD gained 4.3 dB. That missed the pre-set 5 dB criterion, and it is a lesson: purely *linear* memory (filters) inflates the modelling NMSE but does not create spectral regrowth. DPD with memory pays off when the memory is *nonlinear* (bias-network beat frequencies as in §5, thermal and trapping effects).
- **Over-drive:** a first attempt at 0.35 rms (too close to saturation) made the DPD worsen ACLR. A predistorter cannot create power beyond saturation; it expands peaks into clipping. Back-off or crest-factor reduction must come first.

Memoryless DPD results for this KB's PA models are in [power amplifiers](../06-rf-circuits/power-amplifiers.md).

## Design equations & rules of thumb

| Equation / rule | When valid | Typical value |
|---|---|---|
| IM3 $=\tfrac34|H_3(f_1,f_1,-f_2)|A^3$ | weakly nonlinear, any memory | — |
| $A_\text{IIP3}^2=\tfrac43|H_1/H_3|$ | per-tone amplitude | bare BJT: $2\sqrt2V_T$ = 73.5 mV |
| $H_n=a_n\prod A(f_i)\,B(\sum f_i)$ | Wiener–Hammerstein | exact |
| $g_{3,\text{eff}}=g_3-\tfrac23g_2^2\sum P(\omega_\text{pair})$ | degenerated transconductor | depends on Z at Δf and 2f |
| BJT sweet spot | $g_1R_E\approx1$ at Δf, bypassed at 2f | IM3 near-null (fifth order dominates) |
| Full degeneration | $Z=R_E$ at all f | $g_{3,\text{eff}}=g_3-g_2^2R_E$ |
| 3rd-order model accurate to ~0.5 dB | ≲ 10 dB below P1dB | tanh: A ≤ 0.2 |
| AM–PM ≈ $\tfrac34\,\mathrm{Im}(H_3/H_1)A^2$ rad | weak drive | small (≪ 1°) far below compression |
| Saleh TWT saturation | $r=1/\sqrt{\beta_a}$ | 0.932 → 1.006, AM–PM 22° |
| Rapp p = 2 | solid-state PA | P1dB at 0.875 $A_\text{sat}$ |
| Memory polynomial K = 5–7, M = 2–4 | DPD for 5–20 MHz signals | NMSE −40 to −50 dB typical |
| Two-tone spacing = your interference spacing | measuring IIP3 | 200 kHz–2 MHz for LoRa plans |

## Worked examples

### Example 1 — IM3 of an LNA whose bias network resonates near the LoRa channel spacing
A 915 MHz BJT LNA has its emitter at RF ground through a capacitor. The DC bias resistor $R_E$ = 25 Ω is bypassed only above ~1 MHz, because the designer used a 6.4 nF capacitor. Two interferers 200 kHz apart (adjacent LoRa channels) sit below the bypass corner. From the script's table, $A_\text{IIP3}$ is about **+3.4 dBm-equivalent** at 100 kHz spacing and **−12.6 dBm** at 10 MHz. The 200 kHz case sits on the steep part of the transition, and its lower and upper IM3 differ by several dB. **The design lesson** is not to "use degeneration for IIP3". It is that the *baseband* impedance at the emitter and the bias node sets IM3 for close-spaced interferers. Make it deliberate, either low (large bypass, a short to ground at Δf) or a controlled real value, and characterise IIP3 at the spacing you care about. A low baseband impedance gives the bare-device IIP3 at all spacings, which is predictable. A deliberately chosen $Z(\Delta f)$ can buy a sweet spot, but it is sensitive to bias current and temperature.

### Example 2 — reading an asymmetric two-tone measurement
A spectrum analyser shows a PA's lower IM3 at −32 dBc and upper at −27 dBc at 5 MHz spacing, and both equal at 50 kHz spacing. Memoryless models cannot produce an asymmetry. It points to a complex $Z(\Delta f)$ (bias or supply decoupling with a corner or resonance near 5 MHz) interacting with second-order products, or to thermal memory. Probe the drain or collector supply ripple at Δf. Adding a low-ESR capacitor that is effective at 5 MHz, or reducing the bias-feed inductance, usually equalises the sidebands. A memory-polynomial DPD can then remove what is left.

### Example 3 — how far can I trust IIP3 extrapolation?
Measure a gain block at −30 dBm per tone: IM3 is at −70 dBc, so IIP3 = −30 + 70/2 = **+5 dBm**. At −10 dBm per tone, the cubic rule predicts IM3 at −30 dBc. The tanh-like device instead shows about −31 dBc, because at A ≈ 0.3 of the tanh scale the exact/cubic ratio is −1.2 dB. At −5 dBm (near P1dB) the IM3 is about 3 dB below the extrapolation. The IIP3 is still a valid figure of merit; just don't use it to predict products near compression.

### Example 4 — Saleh model and back-off for an OFDM video link
A 5.8 GHz OFDM link with a TWT-like (Saleh) amplifier: at saturation input (r = 0.932) the output is 1.006 with 22° of AM–PM. At 6 dB input back-off (r = 0.466) the AM–AM gain is $2.1587/(1+1.1517\cdot0.217)$ = 1.72, against 2.16 small-signal (−2.0 dB compression), and AM–PM is $4.0033\cdot0.217/(1+9.104\cdot0.217)$ = 0.29 rad = 16.6°. Even at 6 dB back-off a TWT-like PA is strongly nonlinear in phase. For OFDM with its ≈ 10 dB PAPR ([OFDM](../10-comms-modulation/ofdm.md)), operate ≥ 8–10 dB backed off, or use DPD. Solid-state (Rapp-like) PAs have much less AM–PM at the same back-off.

### Example 5 — why LoRa doesn't care
LoRa CSS is constant-envelope: $|\tilde x|$ is constant. Every behavioural-model term $\tilde x|\tilde x|^{k-1}$ is then just a constant gain and phase times $\tilde x$. No spectral regrowth arises from AM–AM or AM–PM, and the PA can run saturated. The Volterra view still matters for the *receiver*, where two strong interferers form IM3 in the LNA and mixer. That is where Example 1 applies.

## Practical notes
- **Simulators:** harmonic balance (Qucs-S, ngspice with HB support where available, commercial ADS/AWR) handles strong nonlinearity. Volterra or "distortion analysis" is fast and gives insight, but only for weak signals. SPICE `.disto` (where supported) implements the method of nonlinear currents.
- **Measuring memory:** sweep the two-tone spacing (e.g. 10 kHz–20 MHz) and record lower and upper IM3 separately. Flat and symmetric means memoryless. A spacing-dependent or asymmetric result means electrical or thermal memory. Use a source combiner with ≥ 30 dB isolation ([nonlinearity measurement notes](nonlinearity-p1db-ip3-intermod.md)).
- **Baseband termination:** for LNAs, mixers and PAs, the impedance presented at Δf (DC to tens of MHz) is a design parameter. Use large, low-ESR bypassing close to the device, and short bias feeds.
- **Behavioural-model identification:** use the real signal (OFDM, QAM) at the real power, time-align input and output to a fraction of a sample, and fit by least squares. Check conditioning: high-order polynomials are ill-conditioned, so orthogonal bases help.

## Common mistakes & misconceptions
- **Forgetting the symmetrisation factor.** Using an unsymmetrised $H_3$ with the 3/4 factor, or a symmetrised one without it, gives IM3 errors of up to 9.5 dB (a factor of 3).
- **Treating the bias network as "DC only".** Its impedance from DC to a few times the signal bandwidth is part of the RF nonlinearity.
- **"IIP3 is a single number for a device."** With memory it depends on tone spacing and on the source, load and bias impedances at f, 2f and Δf. The script's example spans 16 dB.
- **"Lower and upper IM3 are always equal."** Only for memoryless (or real-kernel) systems.
- **"A higher-order polynomial fit is a better PA model."** Without memory terms, the error floor stays (−25 dB NMSE in the script, however high K goes).
- **"DPD can fix a saturated PA."** It cannot add output power beyond saturation. Over-driven DPD *increased* ACLR in the first script run.
- **Using power-series coefficients measured at one frequency to predict IM3 at another**, when there are reactive elements.
- **"AM–PM is a large-signal effect only."** It exists from third order as soon as kernels are complex, but it is small far below compression.

## How to simulate / verify
- **By hand:** the method of nonlinear currents needs only linear AC analysis. Any SPICE `.ac` run with injected current sources at $2f$, $\Delta f$ and $2f_1-f_2$ (scaled by $g_2v_1^2$ etc.) reproduces the Level 2 results for a real schematic.
- **Bench:** two signal generators through a hybrid combiner, plus a spectrum analyser, sweeping the spacing (see [spectrum analysers](../17-test-measurement/spectrum-analyzers.md)).
- `python3 tools/verify/e11_volterra.py` (≈ 3 s): **9/11 checks**; output in `tools/verify/e11_volterra_output.txt`. It covers:
  - Wiener–Hammerstein kernel vs FFT;
  - method of nonlinear currents vs an RK4 time-domain simulation of the degenerated BJT at five spacings (worst 0.32 dB; miss vs the 0.3 dB bound, at the −94 dBc sweet spot);
  - IIP3 vs spacing; tanh truncation table; AM–PM from $H_3$;
  - Saleh and Rapp properties; memory-polynomial fit; indirect-learning DPD (memory-DPD gain 4.3 dB vs the 5 dB bound).
- Related: `tools/verify/noise_ip3_twotone.py` (memoryless two-tone and cascade, 07 domain) and `tools/verify/rfckt_pa.py` (memoryless DPD on a Rapp PA, 06 domain).

## Open questions / gaps
- A measured two-tone spacing sweep on a real LNA (e.g. the 06/lna-design part) to confirm the predicted spacing dependence has not been done.
- **Saleh α_φ: 4.0033, not 4.033 (resolved by W5-S18, 2026-10-13, medium–high confidence).** The value 4.0033 appears in three sources that do not depend on one another: the MathWorks `comm.MemorylessNonlinearity` default, which cites Saleh 1981; arXiv:1206.1722; and arXiv:2404.19463, which takes it from Zhang et al., *IEEE TIFS* 16, 2021. The value 4.033 appears only in the IEEE 802.16 impairment slides 802161pp-00_15 (read) and in one patent. The other three Saleh parameters are all given to five significant figures (2.1587, 1.1517, 9.1040), so 4.033 looks like a dropped digit. Saleh's paper itself is paywalled and its table was not seen. The difference matters little in practice: the AM–PM at saturation is 22.37° with 4.0033 and 22.53° with 4.033.
- Nonlinear capacitance (charge-source) kernels and a full BJT/FET Volterra model with $C_\pi$, $C_\mu$ were not implemented. Neither was a mixer (time-varying Volterra / LPTV) analysis; D4 #40 covers that separately.
- Thermal and trapping memory models (e.g. a low-pass-filtered power feedback term) were not simulated.
- The DPD comparison used a PA with linear memory only. A PA with bias-network (nonlinear) memory would show the benefit of memory DPD more clearly.

## Sources
1. S. A. Maas, *Nonlinear Microwave and RF Circuits*, 2nd ed., Artech House 2003, ch. 4 (Volterra-series and power-series analysis; method of nonlinear currents; examples). (textbook)
2. P. Wambacq, W. Sansen, *Distortion Analysis of Analog Integrated Circuits*, Kluwer 1998, chs. 3–6 (Volterra kernels of feedback circuits, second-order interaction, degeneration and IM3 cancellation). (textbook)
3. B. Razavi, *RF Microelectronics*, 2nd ed., 2011, §2.2.6–2.2.8 (nonlinear dynamic systems, Volterra series, method of nonlinear currents). (textbook)
4. A. A. M. Saleh, "Frequency-independent and frequency-dependent nonlinear models of TWT amplifiers," *IEEE Trans. Commun.*, 29(11):1715–1720, 1981. Parameter values cross-checked with MathWorks `comm.MemorylessNonlinearity` documentation (4.0033) and an IEEE 802.16 impairment presentation (4.033), via search 2026-10-13. (peer-reviewed / documentation)
5. C. Rapp, "Effects of HPA-nonlinearity on a 4-DPSK/OFDM-signal for a digital sound broadcasting system," *Proc. 2nd European Conf. Satellite Communications*, Liège, 1991, pp. 179–184. (conference; cited from knowledge)
6. J. Kim, K. Konstantinou, "Digital predistortion of wideband signals based on power amplifier model with memory," *Electronics Letters*, 37(23):1417–1418, 2001. (peer-reviewed)
7. D. R. Morgan, Z. Ma, J. Kim, M. G. Zierdt, J. Pastalan, "A generalized memory polynomial model for digital predistortion of RF power amplifiers," *IEEE Trans. Signal Process.*, 54(10):3852–3860, 2006; L. Ding et al., *IEEE Trans. Commun.*, 52(1):159–165, 2004 (indirect learning with memory polynomials). (peer-reviewed)
8. J. Vuolevi, T. Rahkonen, *Distortion in RF Power Amplifiers*, Artech House 2003 (electrical and thermal memory effects; IM3 asymmetry from baseband impedance). (textbook; cited from knowledge)
9. S. C. Cripps, *RF Power Amplifiers for Wireless Communications*, 2nd ed., Artech 2006, ch. 9 (AM–PM, memory). (textbook)
10. Verification: `tools/verify/e11_volterra.py`. (numerical check)
