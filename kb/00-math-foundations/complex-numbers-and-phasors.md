---
title: Complex numbers and phasors
domain: 00-math-foundations
slug: complex-numbers-and-phasors
tags: [complex-numbers, euler, phasor, impedance, rms, pep, complex-power, analytic-signal, negative-frequency, iq]
prerequisites: [decibels-and-log-units.md]
related:
  - fourier-series-and-transform.md
  - linear-systems-convolution.md
  - differential-equations-circuits-waves.md
  - laplace-transfer-functions-bode.md
  - ../01-circuit-theory/lumped-elements-impedance-admittance.md
  - ../01-circuit-theory/energy-storage-and-reactive-power.md
  - ../03-transmission-lines-matching/smith-chart.md
  - ../14-sdr-dsp/iq-complex-baseband.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Complex numbers and phasors

## Questions this page answers
- What is $j$, and why do engineers use $j$ instead of $i$?
- What does Euler's formula $e^{j\theta}=\cos\theta+j\sin\theta$ actually mean, and why is it everywhere in RF?
- What is a phasor, and why can I replace $d/dt$ with $j\omega$?
- Why is impedance a complex number? Is the imaginary part "not real"?
- What is the difference between RMS, peak, peak-to-peak, average power and PEP?
- Why is there a ½ in $P=\tfrac12\mathrm{Re}\{VI^*\}$ in some books but not in others?
- What is reactive power and does it heat anything?
- What is an analytic signal and a complex envelope?
- What is a negative frequency, and why does my SDR's FFT show signals at negative frequencies?
- Why does `atan(y/x)` give the wrong phase angle?

## TL;DR
- A complex number $z = x + jy = r e^{j\theta}$ is a 2-D arrow: magnitude $r=\sqrt{x^2+y^2}$ and angle $\theta = \mathrm{atan2}(y,x)$. Multiplying complex numbers **multiplies magnitudes and adds angles** — exactly what a linear circuit does to a sinusoid (scale it and shift its phase).
- Euler: $e^{j\theta}=\cos\theta + j\sin\theta$. So $\cos\omega t = \mathrm{Re}\{e^{j\omega t}\}$ and $\cos\omega t=\tfrac12(e^{j\omega t}+e^{-j\omega t})$.
- **Phasor**: for a linear time-invariant circuit in sinusoidal steady state at one frequency $\omega$, write $v(t)=\mathrm{Re}\{V e^{j\omega t}\}$ with complex $V=|V|e^{j\phi}$. Then $d/dt \to j\omega$ and every differential equation becomes algebra: $Z_R=R$, $Z_L=j\omega L$, $Z_C = 1/(j\omega C)$.
- Impedance is complex because it relates two phasors: its magnitude is the voltage/current amplitude ratio and its angle is how far the current lags the voltage. The imaginary part (reactance) represents energy that sloshes back and forth each cycle without being dissipated.
- Power with **peak** phasors: $P = \tfrac12\mathrm{Re}\{VI^*\}$ (microwave/RF texts, e.g. Pozar). With **RMS** phasors: $P=\mathrm{Re}\{VI^*\}$ (power engineering). Mixing conventions is a 3 dB error.
- Sine: $V_{\rm rms}=V_{\rm pk}/\sqrt2$, $V_{\rm pp}=2V_{\rm pk}$. PEP = average power over one RF cycle at the envelope crest. Constant-envelope signals (FSK, LoRa) have PEP = average power; a two-tone test signal has PEP = 2 × average.
- A real signal has a spectrum symmetric in $\pm f$ (two counter-rotating phasors). A complex (I/Q) signal can have energy at $+f$ only or $-f$ only; at baseband, "negative frequency" simply means "below the carrier".

## Intuition (no math)
Picture a bicycle wheel with a reflector on its rim, spinning steadily, and watch its shadow on a wall. The shadow moves up and down in a perfect sine wave. The *wheel* is the phasor; the *shadow* is the real signal you measure with an oscilloscope. Keeping track of the whole wheel (its radius = amplitude, its angle = phase) is much easier than keeping track of the shadow, because when a linear circuit acts on a sine wave it can only do two things: make the wheel bigger or smaller, and rotate it forwards or backwards in angle. It can never change how fast the wheel spins (the frequency).

A complex number is just a way of writing "an arrow on a flat plane" as a single number. The "real part" is how far it points right, the "imaginary part" how far it points up. The word "imaginary" is historical baggage — nothing about it is unreal. Multiplying by $j$ rotates an arrow 90° anticlockwise: $j\times j = -1$ is two quarter-turns, which points backwards. That is why $j$ and "90° phase shift" are the same thing, and why an inductor (whose voltage leads its current by 90°) has impedance $j\omega L$.

Why is impedance complex? A resistor turns electrical energy into heat; its current and voltage are in step. An inductor or capacitor stores energy in a field for a quarter cycle and gives it back the next quarter; its current and voltage are 90° out of step. A real component does a bit of both; the complex impedance records both effects in one number — real part = the "burns energy" part (resistance), imaginary part = the "stores and returns" part (reactance).

Negative frequency: a wheel can spin anticlockwise or clockwise. The sign of frequency is the direction of spin. A real cosine is the shadow of *two* equal wheels spinning in opposite directions (their vertical motions cancel, horizontal motions add). An I/Q receiver sees both the horizontal and vertical shadow, so it *can* tell the directions apart — a tone slightly above the carrier spins one way, below the carrier the other way.

## The math

### Level 1 — complex arithmetic

Definitions: $j^2 = -1$ (engineers use $j$ because $i$ is current). A complex number
$$z = x + jy = r\,\angle\theta = r(\cos\theta + j\sin\theta)= re^{j\theta}$$

| Operation | Rectangular | Polar |
|---|---|---|
| magnitude | $\lvert z\rvert=\sqrt{x^2+y^2}$ | $r$ |
| angle | $\theta=\mathrm{atan2}(y,x)$ | $\theta$ |
| sum $z_1+z_2$ | $(x_1+x_2)+j(y_1+y_2)$ | convert to rectangular first |
| product $z_1z_2$ | $(x_1x_2-y_1y_2)+j(x_1y_2+x_2y_1)$ | $r_1r_2\angle(\theta_1+\theta_2)$ |
| quotient $z_1/z_2$ | multiply top and bottom by $z_2^*$ | $(r_1/r_2)\angle(\theta_1-\theta_2)$ |
| conjugate $z^*$ | $x - jy$ | $r\angle-\theta$ |
| $z z^*$ | $x^2+y^2$ | $r^2$ (always real, ≥ 0) |
| $1/j$ | $-j$ | $1\angle-90°$ |

Rule of thumb: add/subtract in rectangular form, multiply/divide in polar form.

**The atan2 trap.** $\arctan(y/x)$ only returns angles in $(-90°, +90°)$ and cannot distinguish $(-25, +40)$ from $(25,-40)$. Use `atan2(y, x)` (or `numpy.angle(z)`): $-25+j40$ is at +122.0°, not −58.0° (checked numerically).

**Degrees vs radians.** $\theta$ in $e^{j\theta}$ is in radians. $1$ rad = 57.30°.

### Level 2 — Euler, phasors, impedance, power

**Euler's formula.** Expand $e^{x}=\sum x^n/n!$ with $x=j\theta$ and group even (real) and odd (imaginary) terms: the even terms are the Taylor series of $\cos\theta$ and the odd ones $j\sin\theta$. Equivalently, $f(\theta)=e^{j\theta}$ is the unique solution of $f'=jf$, $f(0)=1$; its velocity is always perpendicular to its position, so it moves round the unit circle at unit angular speed [1 §6]. Consequences:
$$\cos\theta=\frac{e^{j\theta}+e^{-j\theta}}{2},\qquad \sin\theta=\frac{e^{j\theta}-e^{-j\theta}}{2j}$$
Trig identities become exponent algebra; e.g. $\cos a\cos b = \tfrac12[\cos(a-b)+\cos(a+b)]$ — the mixer equation (see [Fourier](fourier-series-and-transform.md) modulation theorem).

**Sinusoids as rotating phasors.** A sinusoid of amplitude $A$, frequency $\omega=2\pi f$ (rad/s) and phase $\phi$ is
$$v(t)=A\cos(\omega t+\phi)=\mathrm{Re}\{\underbrace{Ae^{j\phi}}_{V}\,e^{j\omega t}\}.$$
$V=Ae^{j\phi}$ is the **phasor** — a complex constant carrying amplitude and phase; $e^{j\omega t}$ is the common rotation that all signals in the circuit share. (This KB uses peak-amplitude phasors and the cosine reference, like most RF/microwave texts [4 §1.2].)

**Why $d/dt\to j\omega$.** $\frac{d}{dt}\mathrm{Re}\{Ve^{j\omega t}\}=\mathrm{Re}\{j\omega Ve^{j\omega t}\}$, because differentiation and taking the real part commute for real $t$. So the phasor of $dv/dt$ is $j\omega V$, and of $\int v\,dt$ is $V/(j\omega)$. Complex exponentials are *eigenfunctions* of linear time-invariant systems: put $e^{j\omega t}$ in, get $H(j\omega)e^{j\omega t}$ out [2 §3.2]. That is the deep reason phasors work, and also why they only work for LTI systems in steady state.

**Deriving element impedances.**
- Resistor $v=Ri$ → $V = RI$ → $Z_R = R$.
- Inductor $v = L\,di/dt$ → $V=j\omega L I$ → $Z_L=j\omega L$ (voltage leads current by 90°).
- Capacitor $i=C\,dv/dt$ → $I=j\omega CV$ → $Z_C = \dfrac{1}{j\omega C}=-\dfrac{j}{\omega C}$ (current leads voltage by 90°).

Impedance $Z=R+jX$ (Ω): resistance $R$, reactance $X$. Admittance $Y=1/Z=G+jB$ (S): conductance $G$, susceptance $B$. Note $G\ne 1/R$ unless $X=0$. KVL and KCL hold for phasors, so all DC circuit techniques (series/parallel, dividers, nodal analysis, Thevenin) carry over with complex numbers. See [lumped elements](../01-circuit-theory/lumped-elements-impedance-admittance.md).

**Worked mini-derivation: series RLC.** KVL: $L\,di/dt+Ri+\frac1C\int i\,dt=v_s(t)$. Phasor form: $(R+j\omega L+\frac{1}{j\omega C})I = V_s$, so
$$I=\frac{V_s}{R+j(\omega L-1/\omega C)},\quad |I|=\frac{|V_s|}{\sqrt{R^2+(\omega L-1/\omega C)^2}},\quad \angle I=\angle V_s-\arctan\frac{\omega L-1/\omega C}{R}.$$
At $\omega_0=1/\sqrt{LC}$ the reactances cancel. `tools/verify/math_complex_phasors.py` integrates the ODE in the time domain for $R=10$ Ω, $L=1$ µH, $C=1$ nF at 4 MHz and confirms the steady state matches this phasor result to $6\times10^{-11}$ relative error.

**RMS, peak and friends.** For a periodic $v(t)$ with period $T$:
$$V_{\rm rms}=\sqrt{\frac1T\int_0^T v^2\,dt}.$$
Average power into resistor $R$ is $V_{\rm rms}^2/R$ for *any* waveform. For a sine only: $V_{\rm rms}=V_{\rm pk}/\sqrt2=0.707V_{\rm pk}$, $V_{\rm pp}=2\sqrt2V_{\rm rms}=2.83V_{\rm rms}$. For a square wave $V_{\rm rms}=V_{\rm pk}$; for a triangle $V_{\rm pk}/\sqrt3$.

**Instantaneous, average and complex power.** With $v=|V|\cos(\omega t+\phi_v)$, $i=|I|\cos(\omega t+\phi_i)$:
$$p(t)=v\,i=\tfrac12|V||I|\cos(\phi_v-\phi_i)+\tfrac12|V||I|\cos(2\omega t+\phi_v+\phi_i).$$
The second term averages to zero; its $2\omega$ ripple is the energy sloshing in and out of reactive elements. Define **complex power** (peak phasors)
$$S=\tfrac12VI^*=P+jQ,\qquad P=\tfrac12|V||I|\cos(\phi_v-\phi_i)=\tfrac12|I|^2R,\qquad Q=\tfrac12|I|^2X.$$
$P$ (W) is the time-average power actually delivered; $Q$ (var) is the amplitude of the reactive exchange; $|S|$ (VA) is apparent power; $\cos(\phi_v-\phi_i)$ is the power factor. With RMS phasors the ½ disappears: $S=V_{\rm rms}I_{\rm rms}^*$ [5]. The script checks $\tfrac12\mathrm{Re}\{VI^*\}$ against the numerical time average of $v(t)i(t)$. Reactive power relates to stored energy: $Q=2\omega(\overline W_m-\overline W_e)$, which is why resonance ($\overline W_m=\overline W_e$) gives a purely resistive input (see [energy storage](../01-circuit-theory/energy-storage-and-reactive-power.md), [resonance and Q](../01-circuit-theory/resonance-and-q.md)).

**Maximum power transfer** with complex impedances: a source $V_s$, $Z_s$ delivers the most power to $Z_L=Z_s^*$ (conjugate match), and that "available power" is $P_{\rm av}=|V_s|^2/(8R_s)$ with peak $V_s$. See [network theorems](../01-circuit-theory/network-theorems-max-power-transfer.md).

### Level 3 — envelopes, analytic signals, negative frequency, conventions

**Average power vs PEP vs peak instantaneous power.** For a modulated carrier $v(t)=a(t)\cos(\omega_ct+\theta(t))$ with slowly varying envelope $a(t)\ge 0$:
- Average power: $\overline{a^2}/(2R)$.
- **Peak envelope power (PEP)**: $\max(a)^2/(2R)$ — the average power over one RF cycle at the envelope crest; this is the definition used by the US amateur rules [6] and by PA datasheets.
- Peak instantaneous power: $\max(a)^2/R$ = 2 × PEP (the carrier's own 3 dB crest).
- PAPR (as used in comms) usually means PEP/average (envelope PAPR); some DSP texts include the carrier crest (+3 dB). State which.
Examples (verified): a two-tone test with equal tones has PEP/avg = 3.01 dB and instantaneous-peak/avg = 6.02 dB. FSK, GFSK and LoRa chirps have constant envelope: PEP = average (0 dB envelope PAPR), which is why their PAs can run near saturation.

**Complex envelope (baseband equivalent).** Any real bandpass signal near carrier $f_c$ can be written
$$x(t)=\mathrm{Re}\{\tilde x(t)\,e^{j2\pi f_ct}\},\qquad \tilde x(t)=I(t)+jQ(t)=a(t)e^{j\theta(t)}$$
so $x(t)=I(t)\cos2\pi f_ct - Q(t)\sin2\pi f_ct$. $\tilde x$ is the phasor generalised to a slowly *time-varying* phasor. A quadrature downconverter multiplies by $e^{-j2\pi f_ct}$ (i.e. by $\cos$ and $-\sin$) and low-pass filters, recovering $\tilde x(t)/2$ [3]. A tone at $f_c+\Delta f$ becomes $e^{+j2\pi\Delta ft}$ (positive frequency); at $f_c-\Delta f$ it becomes $e^{-j2\pi\Delta f t}$ (negative frequency). The script confirms a 2 MHz + 50 kHz tone lands at +50 kHz and 2 MHz − 50 kHz at −50 kHz. See [IQ and complex baseband](../14-sdr-dsp/iq-complex-baseband.md).

**Negative frequency, precisely.** $e^{j\omega t}$ with $\omega>0$ rotates anticlockwise; with $\omega<0$ clockwise. Real signals satisfy $X(-f)=X^*(f)$ (Hermitian spectrum), so the negative half carries no extra information; complex signals need both halves because $+f$ and $-f$ are genuinely different rotations [3], [7]. A LoRa up-chirp at complex baseband sweeps from $-B/2$ to $+B/2$ — in RF terms from $f_c-B/2$ to $f_c+B/2$. Numerical check: the FFT of $e^{j\omega_0 n}$ has one line at $+\omega_0$; the FFT of $\cos\omega_0n$ has two lines of half height at $\pm\omega_0$.

**Analytic signal.** $z(t)=x(t)+j\hat x(t)$, where $\hat x$ is the Hilbert transform of $x$ (a −90° phase shift of every positive-frequency component; see [linear systems](linear-systems-convolution.md)). Its spectrum is $2X(f)$ for $f>0$ and zero for $f<0$. $|z(t)|$ is the envelope and $\arg z(t)$ the instantaneous phase; the instantaneous frequency is $\frac1{2\pi}\frac{d}{dt}\arg z$. The complex envelope is $\tilde x(t)=z(t)e^{-j2\pi f_ct}$. Verified: `scipy.signal.hilbert` on an AM signal recovers the $1+m\cos$ envelope and has zero energy at negative frequencies.

**Sign conventions.** Engineering uses $e^{+j\omega t}$; physics uses $e^{-i\omega t}$. Translating: replace $j$ by $-i$. Then an inductor is $-i\omega L$, a lossy dielectric is $\varepsilon'+i\varepsilon''$ instead of $\varepsilon'-j\varepsilon''$, and outgoing waves are $e^{i(kr-\omega t)}$ instead of $e^{j(\omega t-kr)}$. Always check which convention a paper uses before copying a formula with a $\pm j$ in it (this KB uses $e^{j\omega t}$, per CONVENTIONS §4.5).

**Limits of phasors.** Phasors assume (1) linearity, (2) time invariance, (3) a single frequency, (4) steady state. Transients need Laplace/time-domain methods ([Laplace](laplace-transfer-functions-bode.md), [ODEs](differential-equations-circuits-waves.md)); multiple frequencies need superposition (one phasor analysis per frequency) or Fourier methods; nonlinear circuits (mixers, PAs in compression) create new frequencies and need harmonic balance or time-domain simulation ([RF simulators](../16-simulation-tools/rf-circuit-simulators-harmonic-balance.md)). The product of two phasors is *not* the phasor of the product of two signals.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $Z_L=j\omega L$, $\lvert Z_L\rvert = 2\pi fL$ | ideal inductor | 10 nH at 433 MHz: +j27.2 Ω |
| $Z_C=1/(j\omega C)$, $\lvert Z_C\rvert=1/(2\pi fC)$ | ideal capacitor | 3.3 pF at 433 MHz: −j111 Ω; 100 nF at 433 MHz: −j0.0037 Ω (but see self-resonance, [capacitors at RF](../04-real-components-hf/capacitors-at-rf-mlcc.md)) |
| $f_0=1/(2\pi\sqrt{LC})$ | lossless LC | 10 nH resonates at 433 MHz with 13.5 pF |
| $S=\tfrac12VI^*$ | peak phasors | |
| $S=V_{\rm rms}I_{\rm rms}^*$ | RMS phasors | |
| $P_{\rm av}=\lvert V_s\rvert^2/(8R_s)$ | peak EMF, conjugate load | 1 W available from 50 Ω needs 20 V peak EMF |
| $V_{\rm rms}=V_{\rm pk}/\sqrt2$ | sine only | |
| PEP $=\max(a)^2/2R$ | envelope $a(t)$ | two-tone: 2 × avg |
| $x=I\cos\omega_ct-Q\sin\omega_ct$ | bandpass signal | |
| $\mathrm{atan2}(y,x)$, not $\arctan(y/x)$ | always | |

## Worked examples

**1. Reactances at 433 MHz.** $\omega = 2\pi\times433\times10^6=2.721\times10^9$ rad/s.
- 10 nH: $X_L=\omega L=27.2$ Ω → $Z=+j27.2$ Ω.
- 3.3 pF: $X_C=-1/(\omega C)=-111.4$ Ω → $Z=-j111.4$ Ω.
- In series: $Z=j(27.2-111.4)=-j84.2$ Ω (net capacitive). They would resonate at $1/(2\pi\sqrt{10\,\text{nH}\times3.3\,\text{pF}})=876$ MHz; to resonate 10 nH at 433 MHz you need $C=1/(\omega^2L)=13.5$ pF.

**2. Driving a monopole (complex load) from a 50 Ω radio.** A quarter-wave monopole over a ground plane has input impedance near $Z_L\approx36.5+j21.3$ Ω (half the λ/2-dipole value; see [dipoles and monopoles](../08-antennas/dipoles-and-monopoles.md)). The radio is a 50 Ω source with 1 W available, i.e. peak EMF $V_s=\sqrt{8\cdot50\cdot1}=20$ V.
- $I = 20/(50+36.5+j21.3)=20/(89.08\angle13.83°)=0.2245\angle-13.83°$ A (peak).
- $P_L=\tfrac12|I|^2R_L = \tfrac12(0.2245)^2(36.5)=0.920$ W.
- Check via reflection: $\Gamma=(Z_L-50)/(Z_L+50)$, $|\Gamma|=0.283$, $1-|\Gamma|^2=0.920$ ✓ — mismatch loss 0.36 dB, VSWR 1.79.
- Load voltage $V_L=IZ_L=9.49\angle16.4°$ V peak; $S=\tfrac12V_LI^*=0.920+j0.537$ VA: 0.54 var of reactive power sloshes into the antenna's near field each cycle. A series capacitor of $X=-21.3$ Ω (17.3 pF at 433 MHz) cancels it (then match 36.5 → 50 Ω; see [impedance matching](../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md)).

**3. Two-path multipath as phasor addition.** Direct ray amplitude 1, ground-reflected ray amplitude 0.6 arriving with relative phase $\varphi$. Received amplitude $|1+0.6e^{j\varphi}|$:

| φ | amplitude | level vs direct only |
|---|---|---|
| 0° | 1.60 | +4.08 dB |
| 90° | 1.17 | +1.34 dB |
| 150° | 0.566 | −4.94 dB |
| 180° | 0.40 | −7.96 dB |

A rocket climbing away sweeps $\varphi$ continuously, so the received level ripples between +4.1 and −8.0 dB (see [two-ray model](../09-propagation-link-budget/two-ray-ground-reflection.md)).

**4. Polar ↔ rectangular with the quadrant trap.** $Z=25-j40$ Ω: $|Z|=47.2$ Ω, $\angle Z=-58.0°$. $Z=-25+j40$ (e.g. a de-embedded result with a sign error, or an active device): $\arctan(40/-25)=-58.0°$ is *wrong*; atan2 gives +122.0°.

**5. LoRa chirp in I/Q.** A 125 kHz LoRa channel centred at 433.175 MHz (an example ISM frequency — check your band plan) is received by an SX127x/SX126x's quadrature downconverter. At complex baseband the up-chirp sweeps linearly from −62.5 kHz to +62.5 kHz: the first half of each symbol is at *negative* baseband frequency, meaning 433.1125–433.175 MHz. A real-only (non-IQ) receiver would fold −62.5…0 onto 0…+62.5 kHz and could not tell up-chirps from down-chirps.

**6. PEP of a two-tone PA test.** Two equal tones at 10 dBm each into 50 Ω: average power = 13.01 dBm (powers add, uncorrelated frequencies), envelope peak amplitude = 2 × single-tone amplitude → PEP = 4 × 10 mW = 40 mW = 16.02 dBm (3 dB above average). A PA with P1dB = 15 dBm will clip this test signal although its *average* is 2 dB below P1dB. See [nonlinearity/IP3](../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md).

## Practical notes
- **VNA and simulators report complex numbers**: $S_{11}$ as real/imag, mag/angle or dB/angle; Smith charts are polar plots of $\Gamma$ ([Smith chart](../03-transmission-lines-matching/smith-chart.md)). Touchstone files state their format in the `#` option line (RI, MA or DB).
- **Measuring phase** on a scope: cursor time difference $\Delta t$ → $\phi=360°\cdot\Delta t\cdot f$. At 433 MHz, 100 ps = 15.6°; probe and cable delays dominate, so phase is measured with a VNA, not a scope.
- **Phasor bookkeeping in code**: use complex dtype (`numpy.complex128`), `np.abs`, `np.angle`, `np.conj`; keep angles in radians internally.
- **Datasheets** give impedances like "Z = 12 − j35 Ω at 433 MHz" for chip antennas or PA outputs; the sign of $X$ tells you whether to cancel with an inductor ($X<0$) or a capacitor ($X>0$).
- **Scope "Vpp" to power**: 1 Vpp sine into 50 Ω = 0.354 V rms = 2.5 mW = +3.98 dBm.

## Common mistakes & misconceptions
1. **"The imaginary part isn't physical."** Reactance and reactive power are completely physical: they are the stored field energy and the current needed to shuttle it. Reactive current still heats the *resistive* parts of wires and matching components (loss ∝ $|I|^2R$) [5].
2. **Mixing peak and RMS phasors** — using $P=\mathrm{Re}\{VI^*\}$ with peak values doubles the power (3 dB error). Microwave texts (e.g. Pozar) use peak phasors with ½; power-system texts use RMS without ½ [4], [5].
3. **Using arctan instead of atan2** — wrong quadrant for negative real parts.
4. **Applying phasors to transients or nonlinear circuits.** Phasors are single-frequency steady-state tools. Switch-on transients, PA compression, mixers and oscillator start-up require time-domain or harmonic-balance methods.
5. **Multiplying phasors of different frequencies.** Only signals at the same frequency can be combined as phasors; different frequencies are handled one at a time (superposition) or with Fourier methods.
6. **Sine vs cosine reference.** A phasor of $A\sin\omega t$ is $-jA$ (cosine reference). Mixing references causes 90° errors, especially when comparing I and Q channels.
7. **Believing negative frequencies are "fake" or "aliases".** For complex signals they are distinct, meaningful components (rotation direction; below-carrier offsets). For *real* signals they are redundant mirror images [3], [7] (forum confusion — e.g. DSP Stack Exchange Q431).
8. **Sign convention errors when copying physics formulas** ($e^{-i\omega t}$) — loss terms and wave directions flip sign.
9. **Forgetting that RMS = peak/√2 only for sines** — noise, square waves and modulated signals differ; use the definition.
10. **Confusing PEP with peak instantaneous power** (factor of 2) and envelope PAPR with sample-level PAPR.
11. **Treating $|Z|$ as resistance** — a 50 Ω magnitude impedance like $30+j40$ Ω is a poor match to 50 Ω ($|\Gamma|=0.5$).

## How to simulate / verify
- `python3 tools/verify/math_complex_phasors.py` — Euler, atan2, series-RLC phasor vs ODE time-domain solution, complex power vs time average, RMS/PEP of a two-tone, Hilbert envelope and one-sided spectrum, cos vs complex-exponential FFTs, and IQ sign of frequency. All PASS.
- SPICE `.ac` analysis is exactly phasor analysis (small-signal, linearised). `.tran` shows the true time response including transients ([SPICE](../16-simulation-tools/spice-circuit-simulation.md)).
- scikit-rf: `rf.Network` stores complex S-parameters; `ntwk.z` gives complex impedance matrices.

## Open questions / gaps
- None significant for the maths. The monopole impedance figure (36.5 + j21.3 Ω) is the textbook thin-wire value; real rocket-mounted monopoles differ strongly — see 08-antennas/antennas-on-rockets.

## Sources
1. H. R. Miller, *18.03 Supplementary Notes*, MIT (2012), §5 "The algebra of complex numbers", §6 "The complex exponential", §10 "Operators and the exponential response formula", §16 "Frequency response". https://math.mit.edu/classes/18.03/sup/sup0.pdf (lecture notes).
2. A. V. Oppenheim, A. S. Willsky, S. H. Nawab, *Signals and Systems*, 2nd ed., Prentice Hall (1997), §3.2 "The response of LTI systems to complex exponentials"; §1.3 exponential and sinusoidal signals (textbook).
3. R. Lyons, *Quadrature Signals: Complex, But Not Complicated*, tutorial (2000; v2 2008), sections "Representing real signals using complex phasors", "Representing quadrature signals in the frequency domain", "A quadrature-sampling example". https://dspguru.com/dsp/tutorials/quadrature-signals/ ; https://www.dsprelated.com/showarticle/192.php (app note/tutorial).
4. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley (2012), §1.2 (time-harmonic phasor form of Maxwell's equations, peak phasors), §1.6 "Energy and power" (complex Poynting theorem, ½Re{VI*}); §2.2–2.3 (power flow on a line: §2.2 field analysis of lines, §2.3 the terminated lossless line) (textbook; section numbers checked by W5-S18 (2026-10-13) against the Wiley 4th-ed. ToC transcribed in gaps/D4-curriculum.md §3.1; the earlier "§2.2" alone was narrowed to §2.2–2.3).
5. University of Illinois ECE 330, Lecture 2 "Complex power" (2020), peak vs RMS phasor forms of $S$. https://courses.grainger.illinois.edu/ece330/sp2020/lectures/ECE330_02.pdf (lecture notes).
6. 47 CFR §97.3(b), definition of PEP. https://www.ecfr.gov/current/title-47/chapter-I/subchapter-D/part-97/subpart-A/section-97.3 (standard/regulation).
7. Signal Processing Stack Exchange, "What is the physical significance of negative frequencies?" Q431 (2011). https://dsp.stackexchange.com/questions/431 (forum — anecdotal; used for the misconception list only).
