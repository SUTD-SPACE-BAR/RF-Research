---
title: Linear systems, convolution, causality and Kramers–Kronig
domain: 00-math-foundations
slug: linear-systems-convolution
tags: [lti, impulse-response, convolution, causality, hilbert-transform, kramers-kronig, dispersion, group-delay, phase-delay, dielectric-models]
prerequisites: [fourier-series-and-transform.md, laplace-transfer-functions-bode.md, complex-numbers-and-phasors.md]
related:
  - probability-random-processes-and-psd.md
  - ../02-electromagnetics/dielectrics-permittivity-loss-tangent.md
  - ../02-electromagnetics/waveguides-and-cavity-resonators.md
  - ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md
  - ../13-pcb-rf-layout-emc/stackups-and-materials.md
  - ../14-sdr-dsp/digital-filters-fir-iir.md
  - ../10-comms-modulation/matched-filter-detection.md
  - ../16-simulation-tools/em-solvers-fdtd-mom-fem.md
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Linear systems, convolution, causality and Kramers–Kronig

## Questions this page answers
- What makes a system "linear" and "time-invariant", and why do we care?
- What is an impulse response, and what does convolution actually compute?
- Why is filtering a multiplication in frequency but a convolution in time?
- What does "causal" mean mathematically, and why can't I build an ideal brick-wall filter?
- What is the Hilbert transform and where does it show up in RF?
- What are the Kramers–Kronig relations, and why must a lossy PCB dielectric have a frequency-dependent εr?
- Why does my EM or SI simulator ask for a "Djordjevic–Sarkar" or "wideband Debye" material model instead of just εr and tan δ?
- What is the difference between phase delay and group delay, and what is dispersion?
- Is a mixer a linear system?

## TL;DR
- **LTI** = linear (superposition holds) + time-invariant (a delayed input gives a delayed output). Passive RLC circuits, transmission lines, antennas, filters and small-signal amplifiers are (approximately) LTI; mixers are linear but time-*varying*; PAs in compression are nonlinear.
- An LTI system is completely described by its **impulse response** $h(t)$; the output is the **convolution** $y(t)=\int h(\tau)x(t-\tau)d\tau$ — a weighted sum of delayed copies of the input. In frequency: $Y=HX$ with $H=\mathcal F\{h\}$.
- **Causal** ⇔ $h(t)=0$ for $t<0$. Consequence: the real and imaginary parts of $H(j\omega)$ are not independent — each is the Hilbert transform of the other. A brick-wall (ideal) filter has a non-causal sinc impulse response, so it cannot be built exactly.
- **Stable (BIBO)** ⇔ $\int|h|dt<\infty$.
- **Hilbert transform** = an ideal −90° phase shifter for all positive frequencies (frequency response $-j\,\mathrm{sgn}(f)$). It builds analytic signals and SSB, and it links gain to phase in minimum-phase systems.
- **Kramers–Kronig**: for any causal material, $\varepsilon'(\omega)$ and $\varepsilon''(\omega)$ form a Hilbert pair. Loss ⇒ dispersion. A model with constant εr *and* constant tan δ at all frequencies is non-causal (half its dispersive impulse response lies at $t<0$ — verified). FR-4 measured by Djordjevic et al. has nearly constant $\varepsilon''\approx0.1$ and $\varepsilon'$ falling ≈0.14 per decade; their causal log model gives $\varepsilon'\approx4.72$ at 100 MHz, 4.63 at 433 MHz, 4.53 at 2.4 GHz, 4.44 at 10 GHz for that board.
- **Phase delay** $-\phi/\omega$ = carrier delay; **group delay** $-d\phi/d\omega$ = envelope delay. Non-constant group delay = dispersion (waveguides, microstrip, filters). In a hollow waveguide $v_pv_g=c^2$.

## Intuition (no math)
Clap your hands in a cathedral. What comes back is the building's "impulse response": the direct sound, then echoes, then a decaying reverberation. If you now play music, what you hear is every note followed by its own set of echoes, all overlapping. Convolution is exactly that bookkeeping: every instant of the input launches a scaled copy of the impulse response, and the output is the sum of all those overlapping copies. Linearity makes the copies add; time-invariance makes each copy the same shape.

Causality is the rule that echoes cannot arrive before the clap. It sounds trivial, but it has strong consequences. A filter that passes 0–1 MHz perfectly and blocks everything above would need an impulse response that starts before the input arrives — so real filters must have gradual skirts and ripple. And a material that absorbs energy at some frequencies (lossy) must also slow down waves by different amounts at different frequencies (dispersive): the absorption and the refractive index are two faces of the same causal response. You cannot choose them independently. That is Kramers–Kronig, and it is why a good PCB material model has εr that drifts downwards with frequency.

Group delay vs phase delay: a modulated carrier has two things you can time — the ripples of the carrier and the bumps of the envelope. In a dispersive medium they travel at different speeds. Information rides on the envelope, so it moves at the group velocity.

## The math

### Level 1 — superposition and discrete convolution

**Linearity**: if $x_1\to y_1$ and $x_2\to y_2$, then $ax_1+bx_2\to ay_1+by_2$. **Time invariance**: if $x(t)\to y(t)$ then $x(t-t_0)\to y(t-t_0)$.

**Discrete convolution** (sampled systems, FIR filters): with impulse response $h[k]$,
$$y[n]=\sum_{k}h[k]\,x[n-k].$$
Example: 3-sample moving average $h=[1/3,1/3,1/3]$. Its frequency response $H(e^{j\Omega})=\tfrac13(1+e^{-j\Omega}+e^{-j2\Omega})$ has $|H|=1$ at DC, 0.805 at $\Omega=\pi/4$, **zero** at $\Omega=2\pi/3$ (i.e. $f_s/3$), and phase $-\Omega$ — a pure 1-sample delay (linear phase, because $h$ is symmetric). See [digital filters](../14-sdr-dsp/digital-filters-fir-iir.md).

**Step response** = running integral (sum) of the impulse response. Measuring a step response and differentiating it is a practical way to get $h(t)$ (e.g. TDR, [time-domain reflectometry](../03-transmission-lines-matching/time-domain-reflectometry.md)).

### Level 2 — the convolution integral, frequency response, stability, delays

**Convolution integral** [1 §2.2], [2 L8]:
$$y(t)=(h*x)(t)=\int_{-\infty}^{\infty}h(\tau)\,x(t-\tau)\,d\tau.$$
Properties: commutative, associative (cascades: $h_1*h_2$), distributive (parallel paths add). Convolution with $\delta(t-t_0)$ delays by $t_0$.

**Why frequency response.** Because $e^{j2\pi ft}$ is an eigenfunction of every LTI system ([phasors](complex-numbers-and-phasors.md)), $h*e^{j2\pi ft}=H(f)e^{j2\pi ft}$ with $H(f)=\int h(t)e^{-j2\pi ft}dt$. With the convolution theorem ([Fourier](fourier-series-and-transform.md)): $Y(f)=H(f)X(f)$. Cascaded stages multiply (add in dB).

**Worked analytic convolution.** Rectangular pulse of height 1 and width $T$ into an RC low-pass, $h(t)=\frac1\tau e^{-t/\tau}u(t)$:
$$y(t)=\begin{cases}1-e^{-t/\tau}, & 0\le t<T\\ (1-e^{-T/\tau})\,e^{-(t-T)/\tau}, & t\ge T\end{cases}$$
Verified numerically in `tools/verify/math_linear_systems.py` (τ = 1 µs, T = 3 µs: peak 0.950).

**BIBO stability**: bounded input ⇒ bounded output iff $\int|h(t)|dt<\infty$. For rational $H(s)$ this is equivalent to all poles in the left half-plane ([Laplace](laplace-transfer-functions-bode.md)).

**Causality**: $h(t)=0$ for $t<0$. Physically realisable systems operating in real time are causal. (Offline DSP can use non-causal filters by buffering, which just adds latency.)

**Correlation vs convolution.** Cross-correlation $R_{xy}(\tau)=\int x^*(t)y(t+\tau)dt$ equals convolution with a time-reversed conjugate. A **matched filter** $h(t)=s^*(T-t)$ therefore correlates the input with the expected waveform and maximises output SNR in white noise — radar pulse compression and LoRa dechirping are matched filters ([matched filter detection](../10-comms-modulation/matched-filter-detection.md), [random processes](probability-random-processes-and-psd.md)).

**Phase delay and group delay.** For $H=|H|e^{j\phi(\omega)}$: $\tau_p=-\phi/\omega$, $\tau_g=-d\phi/d\omega$. A narrowband input $a(t)\cos\omega_0t$ comes out as $\approx|H|a(t-\tau_g)\cos\omega_0(t-\tau_p)$ [1 §6.2]. If $\tau_g$ is constant over the signal's band (linear phase) the envelope is undistorted; otherwise the signal is **dispersed**. Standard filter group-delay results are on the [Laplace/Bode page](laplace-transfer-functions-bode.md).

### Level 3 — Hilbert transform, causality relations, Kramers–Kronig, dispersion

**Hilbert transform.**
$$\hat x(t)=\mathcal H\{x\}(t)=\frac1\pi\,\mathrm{P.V.}\!\int_{-\infty}^{\infty}\frac{x(\tau)}{t-\tau}d\tau,\qquad \hat X(f)=-j\,\mathrm{sgn}(f)\,X(f).$$
Every positive-frequency component is shifted by −90° and every negative-frequency component by +90°: $\mathcal H\{\cos\omega_0t\}=\sin\omega_0t$ (verified). $\mathcal H\{\mathcal H\{x\}\}=-x$. Uses: analytic signal $x+j\hat x$ (one-sided spectrum; envelope and instantaneous frequency — see [phasors](complex-numbers-and-phasors.md)); SSB generation (phasing method); IQ imbalance analysis; envelope detection in software [3 ch. 12].

**Causality ⇒ Hilbert pair in frequency.** Write a causal $h(t)=h(t)u(t)$. Multiplication by the step in time becomes convolution with $U(f)=\tfrac12\delta(f)+1/(j2\pi f)$ in frequency, which yields (for real $h$, $e^{-j\omega t}$ transform convention)
$$H_I(\omega)=-\mathcal H\{H_R\}(\omega),\qquad H_R(\omega)=h_\infty+\mathcal H\{H_I\}(\omega),$$
where $H=H_R+jH_I$ and $h_\infty$ is any instantaneous (frequency-independent) part. So the real part of a causal frequency response determines the imaginary part and vice versa [3 ch. 12]. Verified numerically for a sampled RC impulse response (agreement to $10^{-14}$).

**Paley–Wiener condition.** A causal $|H(j\omega)|$ must satisfy $\int\frac{|\ln|H(j\omega)||}{1+\omega^2}d\omega<\infty$: the magnitude can have isolated zeros but cannot be zero over a whole band, and cannot fall faster than exponentially. Hence no brick-wall filter; real stopbands are merely very small [4].

**Gain–phase version.** For a *minimum-phase* $H$, $\ln H=\ln|H|+j\phi$ is itself analytic and causal-like in the right half-plane, so $\phi$ is the Hilbert transform of $\ln|H|$ (in suitable variables) — Bode's gain–phase relation ([Laplace/Bode](laplace-transfer-functions-bode.md), verified there).

**Kramers–Kronig relations for permittivity.** The polarisation of a material responds causally to the field: $P(t)=\varepsilon_0\int_0^\infty g(\tau)E(t-\tau)d\tau$. So the susceptibility $\chi(\omega)=\varepsilon_r(\omega)-\varepsilon_\infty$ is the transform of a causal, real $g(t)$. With the engineering convention $\varepsilon_r=\varepsilon'-j\varepsilon''$ ($\varepsilon''\ge0$ for loss):
$$\varepsilon'(\omega)-\varepsilon_\infty=\frac{2}{\pi}\,\mathrm{P.V.}\!\int_0^\infty\frac{\omega'\,\varepsilon''(\omega')}{\omega'^2-\omega^2}d\omega',\qquad \varepsilon''(\omega)=\frac{2\omega}{\pi}\,\mathrm{P.V.}\!\int_0^\infty\frac{\varepsilon'(\omega')-\varepsilon_\infty}{\omega^2-\omega'^2}d\omega'$$
(DC-conductivity terms $\sigma/(\omega\varepsilon_0)$ are handled separately) [5 §7.10], [6 §1.17]. Verified: the first integral reconstructs $\varepsilon'$ of a Debye model from its $\varepsilon''$ to $<10^{-4}$.
- **Debye (single relaxation)**: $\varepsilon_r=\varepsilon_\infty+\dfrac{\Delta\varepsilon}{1+j\omega/\omega_0}$ — causal; its $\varepsilon'$ drops by $\Delta\varepsilon$ around $\omega_0$ and $\varepsilon''$ peaks at $\Delta\varepsilon/2$ there [7].
- **Lorentz (resonant)**: $\varepsilon_r=\varepsilon_\infty+\dfrac{\Delta\varepsilon\,\omega_0^2}{\omega_0^2-\omega^2+j\omega\gamma}$ — atomic/molecular resonances (IR/optical), also metamaterial and ferrite-like responses.
- **Wideband Debye / Djordjevic–Sarkar (D–S)**: a continuum of Debye terms spread uniformly on a log-frequency axis between $\omega_1$ and $\omega_2$ gives [7 eq. 5]
$$\varepsilon_r(\omega)=\varepsilon_\infty'+\frac{\Delta\varepsilon'}{m_2-m_1}\,\frac{\ln\!\left(\frac{\omega_2+j\omega}{\omega_1+j\omega}\right)}{\ln10}-j\frac{\sigma}{\omega\varepsilon_0},\qquad \omega_{1,2}=10^{m_{1,2}}\ \text{rad/s}.$$
Between $\omega_1$ and $\omega_2$, $\varepsilon'$ falls linearly in $\log\omega$ by $\Delta\varepsilon'/(m_2-m_1)$ per decade and $\varepsilon''$ is nearly constant, equal to $(\pi/2)/\ln10=0.682$ times that per-decade decay [7]. So **"constant loss tangent" and "εr falling slowly with frequency" are the same physical fact seen through Kramers–Kronig.** With Djordjevic's FR-4 fit ($\varepsilon'_\infty=4.27$, $m_1=4$, $m_2=12$, 0.14 per decade) the verify script reproduces $\varepsilon''=0.0955$ (tan δ ≈ 0.020) and confirms the impulse response is causal (<0.1 % of its energy at $t<0$, a numerical-truncation residue), whereas "εr = 4.4, tan δ = 0.02 at all frequencies" puts ~50 % of its dispersive response at $t<0$.

**Why simulators care.** Frequency-domain solvers at a single frequency don't care about causality. But time-domain solvers (FDTD such as openEMS, transient SPICE with lossy lines) and broadband S-parameter → time-domain conversions (TDR, eye diagrams, pulse radar) produce non-physical precursors, instabilities or passivity violations if the material or S-parameter model is non-causal [7], [8]. Use D–S / wideband Debye materials, and causality-enforced S-parameter fits. See [dielectrics](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md), [EM solvers](../16-simulation-tools/em-solvers-fdtd-mom-fem.md). The same reasoning applies to conductor-roughness models, which also need causal forms [8].

**Dispersion in guided waves.** When the propagation constant $\beta(\omega)$ is not proportional to $\omega$, different frequencies travel at different speeds: $v_p=\omega/\beta$, $v_g=d\omega/d\beta$.
- Hollow metal waveguide (TE₁₀): $\beta=\frac{\omega}{c}\sqrt{1-(f_c/f)^2}$ ⇒ $v_p=c/\sqrt{1-(f_c/f)^2}>c$, $v_g=c\sqrt{1-(f_c/f)^2}<c$, and $v_pv_g=c^2$ (verified for WR-90, $f_c=6.557$ GHz). $v_p>c$ violates nothing: no information travels at $v_p$ ([waveguides](../02-electromagnetics/waveguides-and-cavity-resonators.md)).
- Microstrip: quasi-TEM, mild geometric dispersion ($\varepsilon_{\rm eff}$ rises with frequency) plus material dispersion (above) ([planar lines](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md)).
- Filters: group delay peaks at band edges ([Laplace/Bode](laplace-transfer-functions-bode.md)).

**What is and isn't LTI in a radio.** Mixer: $y=x\cdot\mathrm{LO}(t)$ — linear in $x$ but time-varying, so it moves energy to new frequencies (still analysable with "conversion" matrices). Sampler/ADC: linear, periodically time-varying (aliasing). PA near compression, limiter, detector diode: nonlinear. Oscillator: nonlinear (amplitude-limited), autonomous. Everything else in the signal path is LTI to a good approximation at small signal.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $y=h*x$, $Y=HX$ | LTI | |
| $\int\lvert h\rvert\,dt<\infty$ | BIBO stability | |
| $h(t)=0,\ t<0$ ⇔ $H_I=-\mathcal H\{H_R\}$ | causal, real $h$ | |
| $\mathcal H$: $-j\,\mathrm{sgn}(f)$ | Hilbert transformer | −90° for $f>0$ |
| KK: $\varepsilon'-\varepsilon_\infty=\frac2\pi\mathrm{PV}\int\frac{\omega'\varepsilon''}{\omega'^2-\omega^2}d\omega'$ | causal linear medium | |
| $\varepsilon''\approx0.682\times$(decay of $\varepsilon'$ per decade) | D–S / constant-loss band | FR-4: 0.14/dec ↔ ε″ ≈ 0.096 |
| $v_pv_g=c^2$ | hollow waveguide, air-filled | WR-90 @ 10 GHz: $v_g=0.755c$ |
| $\tau_g=-d\phi/d\omega$ | narrowband envelope | |

## Worked examples

**1. RC-smoothed digital pulse.** A 3 µs pulse into an RC with τ = 1 µs reaches $1-e^{-3}=0.950$ of full height at the end of the pulse, then decays with τ. If the pulse were 0.3 µs it would only reach $1-e^{-0.3}=0.26$ — the "narrow pulse through a slow filter" loss that matters for pulsed radar video and for power detectors reading short packets.

**2. Frequency response by inspection of a 3-tap FIR.** $h=[1,1,1]/3$ sampled at $f_s=1$ MS/s: null at 333 kHz, −1.9 dB at 125 kHz, pure 1 µs delay. A designer wanting to reject a 333 kHz spur with a trivial FIR could use exactly this.

**3. How much does FR-4's εr move between 100 MHz and your RF band?** Using the D–S fit of Djordjevic's board (parameters are sample-specific; your laminate's datasheet or measurement governs):

| f | 1 MHz | 100 MHz | 433 MHz | 915 MHz | 1575 MHz | 2.4 GHz | 5.8 GHz | 10 GHz |
|---|---|---|---|---|---|---|---|---|
| ε′ | 5.00 | 4.72 | 4.63 | 4.58 | 4.55 | 4.53 | 4.47 | 4.44 |
| tan δ | 0.019 | 0.020 | 0.021 | 0.021 | 0.021 | 0.021 | 0.021 | 0.021 |

A resonator designed with the "1 MHz datasheet" value ε′ = 5.0 but used at 2.4 GHz (ε′ = 4.53) resonates $\sqrt{5.0/4.53}-1=5$ % high — 120 MHz off at 2.4 GHz, far outside a Wi-Fi/ISM channel. Even designing with the 100 MHz value gives 2.1 %. Always use εr at the operating frequency (see [stackups and materials](../13-pcb-rf-layout-emc/stackups-and-materials.md), [JLCPCB RF manufacturing](../13-pcb-rf-layout-emc/jlcpcb-rf-manufacturing.md)).

**4. Group delay in WR-90 at 10 GHz.** $v_g=c\sqrt{1-(6.557/10)^2}=0.755c$; 1 m of guide delays the envelope 4.42 ns (vs 3.34 ns in free space). A 9–11 GHz radar chirp sees different delays at each end of its sweep — dispersion that a wideband SAR processor must correct.

**5. Non-causal S-parameters in practice.** A vendor's S-parameter file measured from 300 kHz to 6 GHz, converted to an impulse response by IFFT without extrapolation to DC and windowing, shows a "precursor" before $t=0$. That is band-limitation and missing low-frequency data, not new physics; simulators apply causality/passivity enforcement to fix it (see [component models](../04-real-components-hf/component-models-s2p-spice.md)).

## Practical notes
- **Measuring $h(t)$**: VNA time-domain transform (IFFT of $S_{21}$ with a window) or TDR/TDT; both assume LTI and band-limit the result.
- **Datasheet εr**: laminate datasheets quote εr at 1 MHz, 1 GHz or 10 GHz by different test methods (IPC-TM-650 2.5.5.x); "design εr" values often differ from "process" values. Treat the frequency and method as part of the number.
- **openEMS** supports Debye/Lorentz/Drude dispersive materials; for FR-4 a multi-term Debye fit to the D–S curve works (see [openEMS workflow](../16-simulation-tools/openems-workflow.md)).
- **Checking your own models**: after fitting a material or S-parameters, IFFT to the time domain and look for energy at $t<0$ — the same test as in the verify script.

## Common mistakes & misconceptions
1. **"Loss tangent and permittivity are independent inputs."** Only over a narrow band. Over wide bands Kramers–Kronig ties them: a lossy material must be dispersive [7].
2. **Using the 1 MHz datasheet εr at GHz** — several percent frequency error in resonators/filters and impedance errors in lines.
3. **"The ideal filter just has a very long delay."** A brick-wall response is non-causal for any finite delay (Paley–Wiener); approximations need delay *and* ripple.
4. **Confusing convolution and correlation** — correlation time-reverses (and conjugates) one signal; matched filters are correlators.
5. **Calling a mixer "nonlinear"** — an ideal multiplier is linear in the signal but time-varying; its *implementation* (diodes, switches) is nonlinear and produces spurs.
6. **"Phase velocity above c breaks relativity."** Information and energy travel at the group (or signal-front) velocity.
7. **Interpreting IFFT precursors as physics** — they are usually band-limiting or non-causal models.
8. **Sign conventions in Kramers–Kronig** differ between physics ($e^{-i\omega t}$, $\varepsilon'+i\varepsilon''$) and engineering ($e^{j\omega t}$, $\varepsilon'-j\varepsilon''$); the magnitude relations above are the same, signs of the imaginary part flip.
9. **Assuming FIR filters are always linear-phase** — only symmetric (or antisymmetric) coefficient sets are.

## How to simulate / verify
- `python3 tools/verify/math_linear_systems.py` — pulse∗RC convolution vs analytic; FFT vs direct convolution; Hilbert{cos} = sin; causal Re/Im Hilbert pair; Kramers–Kronig reconstruction of a Debye ε′; Djordjevic–Sarkar FR-4 model (ε″ = 0.682 × slope, causal impulse response) vs non-causal constant-tan δ model; WR-90 $v_pv_g=c^2$. All PASS (~20 s).
- Python: `numpy.convolve`, `scipy.signal.fftconvolve`, `scipy.signal.hilbert`, `scipy.signal.group_delay` (digital), `scikit-rf` `Network.impulse_response()` / time gating.

## Open questions / gaps
- The D–S parameters quoted are for the 62-mil FR-4 sample in [7]; JLCPCB's FR-4 (and its stated εr ≈ 4.5 at some frequency) should be characterised in 13-pcb-rf-layout-emc / 18-components-parts.
- Causality enforcement algorithms for measured S-parameters (e.g. Hilbert-based, vector fitting) are only named here; 16-simulation-tools should cover the practical workflow.

## Sources
1. A. V. Oppenheim, A. S. Willsky, S. H. Nawab, *Signals and Systems*, 2nd ed., Prentice Hall (1997): §2.1–2.3 (convolution sum/integral and LTI properties incl. causality and stability), §6.2 (linear/non-linear phase, group delay) (textbook).
2. D. Freeman, MIT 6.003 (Fall 2011), lecture 8 "Convolution", lecture 9 "Frequency response". https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/pages/lecture-notes/ (lecture notes).
3. A. V. Oppenheim, R. W. Schafer, *Discrete-Time Signal Processing*, 3rd ed., Pearson (2010), ch. 12 "Discrete Hilbert transforms" (causality relations, analytic signals) (textbook).
4. A. Papoulis, *The Fourier Integral and Its Applications*, McGraw-Hill (1962), causality and the Paley–Wiener criterion (textbook; cited for the criterion statement).
5. J. D. Jackson, *Classical Electrodynamics*, 3rd ed., Wiley (1999), §7.10 "Causality in the connection between D and E; Kramers–Kronig relations" (textbook; physics $e^{-i\omega t}$ convention).
6. S. J. Orfanidis, *Electromagnetic Waves and Antennas*, Rutgers (online, 2016 ed.), ch. 1: §1.10–1.15 simple models of dielectrics/conductors/plasmas, §1.17 "Kramers–Kronig dispersion relations". https://www.ece.rutgers.edu/~orfanidi/ewa (textbook, free).
7. A. R. Djordjević, R. M. Biljić, V. D. Likar-Smiljanić, T. K. Sarkar, "Wideband frequency-domain characterization of FR-4 and time-domain causality," *IEEE Trans. Electromagnetic Compatibility* 43(4):662–667 (2001), eqs. (2)–(7), §II measurements (ε′ decays ≈0.14/decade 10 kHz–10 GHz, ε″ ≈ 0.1). https://mtt.etf.bg.ac.rs/Mikrotalasna.Tehnika/Clanci/FR4_EMC_2001.pdf (peer-reviewed).
8. V. Dmitriev-Zdorov et al. (author per the article PDF; not re-verified), "How to enforce causality of standard and 'custom' metal roughness models," *Signal Integrity Journal*, July 2020 — derives causal Hammerstad and Cannonball-Huray roughness models; non-causal roughness models underestimate inductance, delay and impedance. https://www.signalintegrityjournal.com/articles/1796-how-to-enforce-causality-of-standard-and-custom-metal-roughness-models (trade journal).
