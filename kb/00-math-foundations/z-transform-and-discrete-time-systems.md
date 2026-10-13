---
title: The z-transform and discrete-time systems — ROC, poles and zeros, stability, Laplace↔z mappings, difference equations
domain: 00-math-foundations
slug: z-transform-and-discrete-time-systems
tags: [z-transform, discrete-time, difference-equation, roc, poles, zeros, unit-circle, stability, jury, dtft, bilinear-transform, impulse-invariance, matched-z, euler, partial-fractions, final-value-theorem, iir, ema, digital-pll, sigma-delta, cic, state-space]
prerequisites: [laplace-transfer-functions-bode.md, linear-systems-convolution.md, complex-numbers-and-phasors.md, fourier-series-and-transform.md]
related:
  - kalman-filter-and-state-estimation.md
  - estimation-theory-ml-map-crb.md
  - ../14-sdr-dsp/digital-filters-fir-iir.md
  - ../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md
  - ../14-sdr-dsp/multirate-dsp-decimation-cic.md
  - ../14-sdr-dsp/nco-ddc-duc.md
  - ../10-comms-modulation/synchronization-carrier-timing.md
  - ../06-rf-circuits/vco-and-pll-synthesizers.md
  - ../05-analog-electronics/data-converters-adc-dac.md
  - ../05-analog-electronics/feedback-and-stability.md
level: mixed
confidence: high
last_updated: 2026-10-02
---

# The z-transform and discrete-time systems

## Questions this page answers
- What is the z-transform, and what does $z^{-1}$ mean physically?
- How do I turn a difference equation (the code in my firmware loop) into a transfer function, and back?
- What is the region of convergence (ROC), and why can two different sequences have the same $X(z)$?
- Why must the poles of a digital filter be inside the unit circle?
- How do I get the frequency response of a digital filter from $H(z)$?
- How is the z-plane related to the s-plane, and what is $z=e^{sT}$?
- Bilinear transform or impulse invariance — which should I use to digitise an analogue filter, and why does the bilinear transform need prewarping?
- How do I compute the inverse z-transform (partial fractions)?
- How much lag and how much noise reduction does a simple exponential moving average give my barometer?
- How do I model a digital PLL, a sigma-delta modulator or a CIC filter with $H(z)$?
- How can I tell quickly whether a second-order recursion is stable?

## TL;DR
- **Definition:** $X(z)=\sum_{n}x[n]z^{-n}$, a power series in the complex variable $z$. Multiplying by $z^{-1}$ delays a sequence by one sample, so a difference equation $\sum a_ky[n-k]=\sum b_kx[n-k]$ becomes $H(z)=\frac{\sum b_kz^{-k}}{\sum a_kz^{-k}}$ — the coefficient lists you pass to `scipy.signal.lfilter(b, a, x)`.
- **ROC:** the set of $z$ where the series converges — always an annulus bounded by poles. The same algebraic $X(z)$ is a different signal for a different ROC: $1/(1-az^{-1})$ is $a^nu[n]$ for $|z|>|a|$ and $-a^nu[-n-1]$ for $|z|<|a|$ (verified).
- **Causal and stable ⇔ all poles strictly inside the unit circle** ($|p|<1$). The ROC is then $|z|>\max|p|$, which contains the unit circle.
- **Frequency response** is $H(z)$ on the unit circle: $H(e^{j\omega})$ with $\omega=2\pi f/f_s$ rad/sample. It repeats every $2\pi$; $\omega=\pi$ is the Nyquist frequency $f_s/2$.
- **s ↔ z:** sampling maps $s$ to $z=e^{sT}$: the $j\Omega$ axis wraps onto the unit circle, the left half-plane into the disc, a pole at $s$ with damping $\zeta$ and natural frequency $\omega_n$ lands at radius $e^{-\zeta\omega_nT}$ and angle $\omega_nT\sqrt{1-\zeta^2}$.
- **Digitising analogue designs:** *impulse invariance* $h[n]=Th_a(nT)$ keeps the time response but aliases (an RC with $f_c=f_s/10$ gets +2.6 dB DC gain and a −7.8 dB instead of −14.2 dB floor at $f_s/2$). *Bilinear* $s=\frac2T\frac{1-z^{-1}}{1+z^{-1}}$ never aliases and preserves stability but warps frequency, $\Omega=\frac2T\tan\frac\omega2$ — prewarp critical frequencies.
- **EMA** $y[n]=y[n-1]+\alpha(x[n]-y[n-1])$ at 100 Hz with α = 0.1: pole 0.9, τ = 94.9 ms, $f_{3\rm dB}$ = 1.68 Hz, **90 ms DC lag**, noise std ×0.229 (variance ×α/(2−α)).
- **Quick stability test** for $z^2+a_1z+a_2$: stable ⇔ $|a_2|<1$ and $|a_1|<1+a_2$ (the stability triangle; verified on 20 000 random cases). Resonator 3 dB width ≈ $2(1-r)$ rad/sample.
- **Loop models:** a PI digital PLL is $z^2+(K_p+K_i-2)z+(1-K_p)=0$; a first-order ΣΔ is $Y=X+(1-z^{-1})E$ (in-band noise ∝ $\pi^2/3\mathrm{OSR}^3$, 9 dB/octave); a CIC is $\big(\frac{1-z^{-R}}{1-z^{-1}}\big)^N$. All verified in `tools/verify/est_ztransform.py`.

## Intuition (no math)
A microcontroller loop does not see a continuous signal — it sees a list of numbers, one per tick. Every digital filter, PLL, control law or estimator running in firmware is a rule of the form "new output = some mix of the latest input, a few old inputs and a few old outputs". The z-transform is the bookkeeping that turns such rules into algebra.

The trick is to give "one tick ago" a symbol, $z^{-1}$. Then "the output equals 0.9 of the previous output plus 0.1 of the input" becomes $Y=0.9z^{-1}Y+0.1X$, which you can solve like any equation: $Y/X=0.1/(1-0.9z^{-1})$. That ratio, the transfer function, tells you everything about the rule: how it responds to a step, to noise, to a sinusoid.

Just as in the Laplace world, the transfer function has **poles** — values of $z$ where it blows up — and each pole is a natural mode of the recursion. A pole at $z=0.9$ means the recursion forgets its past by a factor 0.9 every tick. A pole at $z=1$ means it never forgets (an integrator, an accumulator — the NCO phase register). A pole at $z=1.05$ means each tick amplifies the past by 5 %, and the output runs away: unstable. So the rule is: **poles inside the unit circle decay; on it, persist; outside, explode.** A complex pole pair at radius $r$ and angle $\theta$ rings at $\theta$ radians per sample while decaying by $r$ each sample.

Walking around the unit circle, $z=e^{j\omega}$, gives the frequency response — a pole near the circle makes a peak at its angle, a zero on the circle makes a notch. Because $\omega$ and $\omega+2\pi$ are the same point, the response repeats: that is aliasing seen from the filter's side.

Finally, the bridge to analogue: sampling a continuous system every $T$ seconds turns its natural modes $e^{st}$ into $e^{snT}=(e^{sT})^n$, so an s-plane pole $s$ becomes a z-plane pole $z=e^{sT}$. The rest of this page is how to use that map — exactly, approximately (bilinear), or by copying the impulse response.

## The math

### Level 1 — delays, difference equations and transfer functions

Let $x[n]$ be the input sample at tick $n$ (sample period $T$ s, rate $f_s=1/T$ Hz) and $y[n]$ the output. A **linear constant-coefficient difference equation** (the general LTI recursion) is
$$\sum_{k=0}^{N}a_k\,y[n-k]=\sum_{k=0}^{M}b_k\,x[n-k],\qquad a_0=1.$$
Replace each $x[n-k]$ by $z^{-k}X(z)$ and each $y[n-k]$ by $z^{-k}Y(z)$ (zero initial conditions):
$$H(z)=\frac{Y(z)}{X(z)}=\frac{b_0+b_1z^{-1}+\dots+b_Mz^{-M}}{1+a_1z^{-1}+\dots+a_Nz^{-N}}.$$
If all $a_k=0$ for $k\ge1$ this is an **FIR** filter (finite impulse response, no feedback); otherwise **IIR** (recursive). In code, `scipy.signal.lfilter(b, a, x)` implements exactly this equation with `a[0]=1`.

**Example (EMA).** The exponential moving average used everywhere in firmware,
$$y[n]=y[n-1]+\alpha\,(x[n]-y[n-1])=(1-\alpha)\,y[n-1]+\alpha\,x[n],$$
has $H(z)=\dfrac{\alpha}{1-(1-\alpha)z^{-1}}$: one pole at $z=1-\alpha$, DC gain $H(1)=1$. Its impulse response is $\alpha(1-\alpha)^n$ — a sampled exponential with time constant $\tau=-T/\ln(1-\alpha)\approx T/\alpha$ for small α.

**Frequency response.** Feed $x[n]=e^{j\omega n}$; the output is $H(e^{j\omega})e^{j\omega n}$. So the gain at frequency $f$ is $|H(e^{j\omega})|$ with $\omega=2\pi f/f_s$ (rad/sample), and the phase is $\angle H$. For the EMA,
$$|H(e^{j\omega})|^2=\frac{\alpha^2}{1-2(1-\alpha)\cos\omega+(1-\alpha)^2}.$$

### Level 2 — definition, ROC, pairs, properties, inversion, stability

**Definition** (bilateral) [1 ch. 3]:
$$X(z)=\sum_{n=-\infty}^{\infty}x[n]\,z^{-n},\qquad z\in\mathbb C.$$
With $z=re^{j\omega}$ this is the DTFT of $x[n]r^{-n}$: the z-transform is to the DTFT what the Laplace transform is to the Fourier transform — it adds an exponential weighting so that growing or merely bounded sequences converge.

**Region of convergence.** The series converges absolutely where $\sum|x[n]|r^{-n}<\infty$, which depends only on $r=|z|$, so the ROC is an annulus $r_-<|z|<r_+$, bounded by poles and containing none. Rules (derived from the geometric series):
- right-sided (causal) sequence → ROC outside the outermost pole, $|z|>r_-$;
- left-sided (anti-causal) → inside the innermost pole;
- two-sided → a ring between poles;
- finite-length → the whole plane except possibly $0$ and/or $\infty$.

*Worked derivation.* $x[n]=a^nu[n]$: $\sum_{n\ge0}(az^{-1})^n=1/(1-az^{-1})$ if $|az^{-1}|<1$, i.e. $|z|>|a|$. For $x[n]=-a^nu[-n-1]$: $-\sum_{m\ge1}(a^{-1}z)^m=-\frac{a^{-1}z}{1-a^{-1}z}=\frac{1}{1-az^{-1}}$ if $|z|<|a|$. Same formula, disjoint ROCs — so **an $H(z)$ without its ROC is not a complete description**; in practice "causal" is implied and the ROC is "outside the largest pole". Both sums are evaluated numerically in the verify script (§1).

**Common pairs** (causal, ROC as stated):

| $x[n]$ | $X(z)$ | ROC |
|---|---|---|
| $\delta[n]$ | $1$ | all $z$ |
| $\delta[n-k]$ | $z^{-k}$ | $z\neq0$ ($k>0$) |
| $u[n]$ | $\dfrac{1}{1-z^{-1}}$ | $\lvert z\rvert>1$ |
| $a^nu[n]$ | $\dfrac{1}{1-az^{-1}}$ | $\lvert z\rvert>\lvert a\rvert$ |
| $na^nu[n]$ | $\dfrac{az^{-1}}{(1-az^{-1})^2}$ | $\lvert z\rvert>\lvert a\rvert$ |
| $r^n\cos(\omega_0n)u[n]$ | $\dfrac{1-r\cos\omega_0\,z^{-1}}{1-2r\cos\omega_0\,z^{-1}+r^2z^{-2}}$ | $\lvert z\rvert>r$ |
| $r^n\sin(\omega_0n)u[n]$ | $\dfrac{r\sin\omega_0\,z^{-1}}{1-2r\cos\omega_0\,z^{-1}+r^2z^{-2}}$ | $\lvert z\rvert>r$ |

**Properties** (each follows by substituting into the defining sum):

| Property | Time domain | z domain |
|---|---|---|
| Linearity | $ax_1+bx_2$ | $aX_1+bX_2$ |
| Delay | $x[n-k]$ | $z^{-k}X(z)$ |
| Exponential weighting | $a^nx[n]$ | $X(z/a)$ (poles scale by $a$) |
| Differentiation in z | $nx[n]$ | $-z\,dX/dz$ |
| Convolution | $x*h$ | $X(z)H(z)$ |
| Time reversal | $x[-n]$ | $X(1/z)$ |
| Accumulation | $\sum_{k\le n}x[k]$ | $X(z)/(1-z^{-1})$ |
| Initial value (causal) | $x[0]$ | $\lim_{z\to\infty}X(z)$ |
| Final value (if it exists) | $\lim_{n\to\infty}x[n]$ | $\lim_{z\to1}(1-z^{-1})X(z)$ |

The final-value theorem is valid only if $(1-z^{-1})X(z)$ has all poles inside the unit circle. For a unit step into $H$, $\lim y[n]=H(1)$ — the DC gain (verified, §5).

**Poles, zeros and geometric evaluation.** Factor $H(z)=b_0\frac{\prod_i(1-z_iz^{-1})}{\prod_k(1-p_kz^{-1})}$. On the unit circle,
$$|H(e^{j\omega})|=|b_0|\frac{\prod_i|e^{j\omega}-z_i|}{\prod_k|e^{j\omega}-p_k|}\quad(\text{for }M=N),$$
so the gain at frequency ω is a ratio of distances from the point $e^{j\omega}$ to the zeros and poles. A pole at radius $r$ close to 1 produces a peak whose −3 dB width is $\approx2(1-r)$ rad/sample, i.e. $\approx(1-r)f_s/\pi$ Hz (verified for $r=0.99$: 0.0201 vs 0.0200). A zero exactly on the circle is a perfect notch (e.g. $1+z^{-1}$ nulls $f_s/2$; $1-z^{-R}$ nulls every multiple of $f_s/R$).

**Stability and causality.** A system is BIBO-stable iff $\sum|h[n]|<\infty$, i.e. iff the ROC contains the unit circle. Combined with causality (ROC outside the outermost pole):
$$\boxed{\text{causal LTI system is stable}\iff\text{all poles satisfy }|p_k|<1.}$$
A pole *on* the circle (an accumulator, $1/(1-z^{-1})$) is marginally stable: bounded input can give unbounded output (a constant input to an integrator). Zeros do not affect stability.

*Second-order shortcut (Jury/Schur–Cohn).* $z^2+a_1z+a_2$ has both roots inside the unit circle iff
$$|a_2|<1\quad\text{and}\quad|a_1|<1+a_2 .$$
This "stability triangle" in the $(a_1,a_2)$ plane is used to bound filter coefficients and tracker gains (e.g. the α-β filter on the [Kalman page](kalman-filter-and-state-estimation.md), whose characteristic polynomial $z^2-(2-\alpha-\beta)z+(1-\alpha)$ gives $0<\alpha<2$, $0<\beta<4-2\alpha$). Checked against a root test on 20 000 random coefficient pairs with zero disagreements.

**Inverse z-transform.** Three methods [1 §3.3]:
1. *Partial fractions* (the workhorse). For distinct poles, $H(z)=\sum_k\frac{r_k}{1-p_kz^{-1}}+(\text{polynomial in }z^{-1}\text{ if }M\ge N)$, with residues $r_k=\big[(1-p_kz^{-1})H(z)\big]_{z=p_k}$. Each term inverts to $r_kp_k^nu[n]$. `scipy.signal.residuez` does this. Example: $H=\frac{1+0.5z^{-1}}{(1-0.9z^{-1})(1+0.4z^{-1})}$ gives $r=1.0769$ at $p=0.9$ and $r=-0.0769$ at $p=-0.4$, so $h[n]=1.0769(0.9)^n-0.0769(-0.4)^n$ (reproduces `lfilter` to 10⁻¹²). Repeated poles give $n^m p^n$ terms.
2. *Long division* — expand $H(z)$ as a power series in $z^{-1}$; the coefficients are $h[n]$. This is what running the recursion does.
3. *Contour integral* $x[n]=\frac{1}{2\pi j}\oint X(z)z^{n-1}dz$ (residue theorem) — the theory behind 1.

**Unilateral transform and initial conditions.** For recursions started at $n=0$ with stored state, use $X^+(z)=\sum_{n\ge0}x[n]z^{-n}$, whose delay property carries the past: $\mathcal Z^+\{y[n-1]\}=z^{-1}Y^+(z)+y[-1]$. For $y[n]=ay[n-1]+x[n]$, $y[-1]=y_0$:
$$Y^+(z)=\frac{X^+(z)+a\,y_0}{1-az^{-1}}\;\Rightarrow\;y[n]=\underbrace{(h*x)[n]}_{\text{zero-state}}+\underbrace{a\,y_0\,a^n}_{\text{zero-input}} .$$
With a unit step, $a=0.7$, $y_0=2$: $y[n]=\frac{1-0.7^{n+1}}{0.3}+1.4\cdot0.7^n$ (matches direct recursion to 4×10⁻¹⁶). The zero-input part is how a filter's start-up transient (e.g. initialising an EMA at 0 instead of the first sample) decays at the pole's rate.

**Frequency response, group delay and linear phase.** $H(e^{j\omega})=|H|e^{j\phi(\omega)}$, group delay $\tau_g=-d\phi/d\omega$ in samples. A symmetric FIR of length $L$ has exactly linear phase with $\tau_g=(L-1)/2$ samples (31 taps → 15 samples, verified). A single real pole at $p$ has DC group delay $p/(1-p)$ samples — the EMA's lag (next section). Minimum-phase, all-pass and the "phase follows magnitude" ideas carry over from the [Laplace page](laplace-transfer-functions-bode.md) with "left half-plane" replaced by "inside the unit circle"; an all-pass section is $\frac{z^{-1}-p^*}{1-pz^{-1}}$.

### Level 3 — sampling, s↔z mappings, discrete models of loops and converters

**Why $z=e^{sT}$.** Sample a continuous signal with Laplace transform $X_a(s)$ at $t=nT$. The sampled impulse train $x_s(t)=\sum x_a(nT)\delta(t-nT)$ has Laplace transform $\sum x_a(nT)e^{-snT}$, which is $X(z)$ evaluated at $z=e^{sT}$. Conversely the spectrum of the samples is the analogue spectrum repeated every $f_s$:
$$X(e^{j\omega})=\frac1T\sum_{k=-\infty}^{\infty}X_a\!\left(j\frac{\omega-2\pi k}{T}\right)$$
— the aliasing formula ([sampling](../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md)). The map $z=e^{sT}$ sends each horizontal strip of height $2\pi/T$ in the s-plane onto the whole z-plane, which is why it cannot be inverted uniquely: frequencies $f$ and $f+kf_s$ are the same point on the unit circle.

Under $z=e^{sT}$ (verified, §10):
- $s=j\Omega$ → $|z|=1$, angle $\Omega T$;
- left half-plane → inside the unit circle (stable ↔ stable);
- $s=-\zeta\omega_n\pm j\omega_n\sqrt{1-\zeta^2}$ → radius $r=e^{-\zeta\omega_nT}$, angle $\theta=\omega_nT\sqrt{1-\zeta^2}$; inversely $\omega_n=|\ln z|/T$, $\zeta=-\mathrm{Re}(\ln z)/|\ln z|$;
- lines of constant damping become logarithmic spirals; constant $\omega_n$ become closed curves.

The same map links continuous and discrete **state-space** models: $\dot{\mathbf x}=\mathbf A\mathbf x$ sampled exactly gives $\mathbf x_{k+1}=\mathbf F\mathbf x_k$ with $\mathbf F=e^{\mathbf AT}$, and $\mathrm{eig}(\mathbf F)=e^{\mathrm{eig}(\mathbf A)T}$ (verified). The poles of $H(z)=\mathbf C(z\mathbf I-\mathbf F)^{-1}\mathbf G+\mathbf D$ are the eigenvalues of $\mathbf F$. This is the discrete model a Kalman filter propagates ([Kalman](kalman-filter-and-state-estimation.md)).

**Digitising an analogue prototype.** We want $H(z)$ that "behaves like" a given $H_a(s)$. The exact map $s=\frac1T\ln z$ makes $H_a$ a non-rational function of $z$, so we need approximations [1 §7.1–7.2], [2 ch. 6]:

*1. Impulse invariance.* Choose $h[n]=T\,h_a(nT)$. With $H_a(s)=\sum_k\frac{A_k}{s-s_k}$, $h_a(t)=\sum A_ke^{s_kt}$ and
$$H(z)=\sum_k\frac{T\,A_k}{1-e^{s_kT}z^{-1}} .$$
Poles map exactly ($p_k=e^{s_kT}$) but the frequency response is the *aliased* sum above, so it is good only if $|H_a(j\Omega)|$ is negligible beyond $\pi/T$. Unusable for high-pass or band-stop prototypes. Zeros do *not* map by $e^{sT}$.

*2. Bilinear transform* (Tustin). Derive it from trapezoidal integration: $y=\int x\,dt$ becomes $y[n]=y[n-1]+\frac T2(x[n]+x[n-1])$, i.e. $\frac{Y}{X}=\frac T2\frac{1+z^{-1}}{1-z^{-1}}$. Equating this with $1/s$:
$$s=\frac{2}{T}\,\frac{1-z^{-1}}{1+z^{-1}},\qquad z=\frac{1+sT/2}{1-sT/2}.$$
On the unit circle $z=e^{j\omega}$: $s=j\frac2T\tan\frac\omega2$, so the **entire** $j\Omega$ axis maps once onto the circle, the LHP maps inside the disc (stability preserved), and there is no aliasing — at the price of the frequency warping
$$\Omega=\frac2T\tan\frac\omega2,\qquad\omega=2\arctan\frac{\Omega T}{2}.$$
Low frequencies are nearly undistorted ($\Omega\approx\omega/T$); $\Omega\to\infty$ is squeezed into $\omega=\pi$ — every bilinear design of an all-pole low-pass has its zeros at $z=-1$ ($f_s/2$). **Prewarping**: to hit a critical frequency $f_c$ exactly, design the analogue prototype at $\Omega_c=2f_s\tan(\pi f_c/f_s)$. The [digital filter page](../14-sdr-dsp/digital-filters-fir-iir.md) uses this for IIR design; the Rice PLL loop-filter gains on the [synchronisation page](../10-comms-modulation/synchronization-carrier-timing.md) also come from it. Bilinear does not preserve group delay shape (Bessel prototypes lose their flat delay).

*3. Matched-z.* Map every pole *and* zero by $e^{sT}$ (zeros at infinity to $z=-1$), then fix the gain at one frequency. Simple and pole-exact; frequency response only approximate.

*4. Euler mappings (what naïve code does).* Forward Euler $s\approx(z-1)/T$ (i.e. $x_{k+1}=x_k+T\dot x_k$) maps the LHP to the half-plane left of $z=1$, so a stable fast pole with $|s|T>2$ becomes **unstable** ($s=-3\times10^4$ at $T=10^{-4}$ → $z=-2$, verified). Backward Euler $s\approx(1-z^{-1})/T$ maps the LHP into the circle $|z-\tfrac12|<\tfrac12$ — always stable but over-damped. This is why integrating a stiff sensor model with a large time step blows up, and why rocket simulators use RK4 or exact discretisation ([numerical methods](numerical-methods-overview.md)).

**Discrete-time loops and converters.**

*Digital PLL / Costas loop / NCO.* An NCO phase accumulator $\hat\theta[n+1]=\hat\theta[n]+K_0v[n]$ is $\frac{K_0z^{-1}}{1-z^{-1}}$ (a pole at $z=1$ — the integrator that makes the loop track phase). With a phase detector of gain $K_d$ and a PI loop filter $F(z)=K_p+\frac{K_i}{1-z^{-1}}$ (absorbing $K_dK_0$ into the gains), the loop gain is $L(z)=F(z)\frac{z^{-1}}{1-z^{-1}}$ and the closed-loop characteristic equation $1+L=0$ is
$$z^2+(K_p+K_i-2)\,z+(1-K_p)=0 .$$
Two poles at $z=1$ in $L$ (NCO + integral path) make it **type 2**: zero steady-state phase error to a frequency step (verified: error → 0 to machine precision). Apply the triangle test: stable iff $0<K_p<2$ and $0<K_i<4-2K_p$. Worked numbers below.

*Sigma-delta (ΣΔ) modulator.* First order: integrator $v[n]=v[n-1]+x[n]-y[n-1]$, quantiser $y[n]=v[n]+e[n]$. Eliminating $v$:
$$Y(z)=X(z)+(1-z^{-1})\,E(z)\qquad(\text{STF}=1,\ \text{NTF}=1-z^{-1}).$$
This identity is exact (verified to 2×10⁻¹⁶ on a 1-bit simulation); the only approximation is treating $e$ as white with variance $\Delta^2/12$. The NTF has a zero at DC, $|{\rm NTF}(e^{j\omega})|=2\sin(\omega/2)$, so in-band noise for oversampling ratio OSR is
$$P_{\rm in-band}\approx\frac{\Delta^2}{12}\cdot\frac1\pi\int_0^{\pi/\mathrm{OSR}}\!\!\omega^2d\omega=\frac{\Delta^2}{12}\frac{\pi^2}{3\,\mathrm{OSR}^3}\qquad(\text{2nd order: }\tfrac{\Delta^2}{12}\tfrac{\pi^4}{5\,\mathrm{OSR}^5}),$$
i.e. 9 dB (first order) or 15 dB (second order) lower noise per doubling of OSR. The same $(1-z^{-1})^m$ shaping is the fractional-N divider noise on the [PLL synthesiser page](../06-rf-circuits/vco-and-pll-synthesizers.md); ADC context is on the [data converters page](../05-analog-electronics/data-converters-adc-dac.md).

*CIC decimator.* $N$ integrators $\frac1{1-z^{-1}}$ at the high rate and $N$ combs $1-z^{-R}$ give $H(z)=\big(\frac{1-z^{-R}}{1-z^{-1}}\big)^N=\big(\sum_{k=0}^{R-1}z^{-k}\big)^N$: the integrator poles at $z=1$ are cancelled exactly by comb zeros, so it is an FIR (moving-sum) filter built without multipliers, with DC gain $R^N$ (512 for $R=8,N=3$) — hence the register growth $N\log_2R$ bits. Integer wrap-around arithmetic is what makes the uncancelled-in-practice pole harmless ([multirate DSP](../14-sdr-dsp/multirate-dsp-decimation-cic.md)).

**Where the z-transform stops.** It handles linear time-invariant recursions. It does not directly describe: decimation/interpolation (time-varying — use polyphase/multirate identities), quantisation and overflow (nonlinear — limit cycles, the ΣΔ quantiser itself), parameter-varying filters (a Kalman filter with time-varying gain, an EKF), or saturating loops (a PLL out of lock). For these, the z-domain model is a small-signal or steady-state linearisation.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $H(z)=\sum b_kz^{-k}/\sum a_kz^{-k}$ | any LTI recursion, $a_0=1$ | `lfilter(b, a, x)` |
| stable ⇔ all $\lvert p_k\rvert<1$ | causal | |
| $z^2+a_1z+a_2$: $\lvert a_2\rvert<1$, $\lvert a_1\rvert<1+a_2$ | 2nd-order section | α-β tracker, PLL |
| $\omega=2\pi f/f_s$; $\omega=\pi\leftrightarrow f_s/2$ | | |
| $z=e^{sT}$: $r=e^{-\zeta\omega_nT}$, $\theta=\omega_nT\sqrt{1-\zeta^2}$ | exact sampling of modes | 50 Hz, ζ 0.3 @ 1 kHz → r = 0.910 |
| resonator 3 dB width $\approx2(1-r)$ rad/sample | $r\to1$ | r = 0.99 → 0.02 rad/s.  |
| EMA: $\tau=-T/\ln(1-\alpha)\approx T/\alpha$; DC delay $(1-\alpha)/\alpha$ samples | first-order IIR | α = 0.1 → 9 samples |
| EMA white-noise variance ratio $\alpha/(2-\alpha)$; ENBW $\approx\frac{\alpha}{2-\alpha}\frac{f_s}{2}$ | | α = 0.1 → 0.0526, 2.63 Hz @ 100 Hz |
| Bilinear $s=\frac2T\frac{1-z^{-1}}{1+z^{-1}}$; prewarp $\Omega_c=2f_s\tan(\pi f_c/f_s)$ | any prototype | 1 kHz @ 10 kHz → 1034.25 Hz |
| Impulse invariance $H=\sum\frac{TA_k}{1-e^{s_kT}z^{-1}}$ | band-limited low-/band-pass | aliasing if $f_c\gtrsim f_s/10$ |
| Forward Euler unstable if $\lvert s\rvert T>2$ (real pole) | explicit integration | |
| PLL char. eq. $z^2+(K_p+K_i-2)z+(1-K_p)$ | PI filter + NCO | $B_nT$ = 0.01 → $K_p$ = 0.0263, $K_i$ = 3.5×10⁻⁴ |
| ΣΔ in-band noise $\frac{\Delta^2}{12}\frac{\pi^{2m}}{(2m+1)\mathrm{OSR}^{2m+1}}$ | order m, linear model | 3(2m+1) dB/octave |
| CIC gain $R^N$, growth $N\log_2R$ bits | | R = 8, N = 3 → 9 bits |

## Worked examples

**1. Barometer smoothing on a flight computer (EMA).** Baro samples at $f_s=100$ Hz, $y[n]=y[n-1]+0.1(x[n]-y[n-1])$.
- Pole $p=0.9$; time constant $\tau=-0.01/\ln0.9=94.9$ ms (≈ $T/\alpha$ = 100 ms).
- −3 dB frequency: solve $|H|^2=\tfrac12$ → $\cos\omega=\frac{1+p^2-2\alpha^2}{2p}=0.99444$ → $\omega=0.1055$ rad/sample → **1.678 Hz** (the analogue estimate $1/2\pi\tau$ = 1.677 Hz).
- Lag: DC group delay $p/(1-p)=9$ samples = **90 ms**. In boost at 200 m/s that is 18 m of altitude lag; near apogee the altitude lag vanishes (v → 0) but any velocity derived by differencing the smoothed altitude is delayed by 90 ms too.
- Noise: for white input of variance σ², output variance $\frac{\alpha}{2-\alpha}\sigma^2=0.0526\sigma^2$ (derivation: $\sum h^2=\alpha^2\sum p^{2n}=\alpha^2/(1-p^2)$); std ×0.229 (simulated 0.0526). A baro with 0.5 m rms noise gives 0.115 m after the EMA. Equivalent noise bandwidth $0.0526\times50=2.63$ Hz = 1.57 × $f_{3\rm dB}$ (the analogue RC value is π/2 = 1.571).
- Moral: noise reduction and lag are tied by the single pole; to get both low noise and low lag, use a model (a Kalman filter fusing the accelerometer — [Kalman page, worked example](kalman-filter-and-state-estimation.md#worked-examples)).

**2. Digitising a 1 kHz RC low-pass at 10 kS/s.** $H_a=\omega_c/(s+\omega_c)$, $\omega_c=2\pi\cdot1000$, $T=10^{-4}$ s ($\omega_cT=0.628$).
- *Impulse invariance:* $H(z)=\frac{\omega_cT}{1-e^{-\omega_cT}z^{-1}}=\frac{0.6283}{1-0.5335z^{-1}}$. DC gain $0.6283/(1-0.5335)=1.347$ (+2.59 dB): the aliased spectral copies add up at DC; divide by it to normalise. At $f_s/2$: $0.6283/(1+0.5335)$ → −7.75 dB, whereas the analogue filter is −14.15 dB at 5 kHz — the stop-band is ruined by aliasing.
- *Bilinear, no prewarp:* $H(z)=\frac{\omega_c(1+z^{-1})}{(2f_s+\omega_c)+(\omega_c-2f_s)z^{-1}}$. At 1 kHz the gain is −3.16 dB (the digital 1 kHz corresponds to the analogue 1034.25 Hz). At $f_s/2$ the gain is exactly 0 (zero at $z=-1$).
- *Bilinear, prewarped:* design the RC at $\Omega_c=2\cdot10^4\tan(0.1\pi)=2\pi\cdot1034.25$ rad/s → exactly −3.010 dB at 1 kHz.
- Choice: bilinear (prewarped) for frequency-selective filters; impulse invariance when you need the time response of a band-limited system (e.g. reproducing a sensor's analogue anti-alias filter in a simulator).

**3. Designing a digital PLL/Costas loop.** Requirement: $B_nT=0.01$, ζ = 0.707. With $\theta=B_nT/(\zeta+1/4\zeta)=0.009428$: $K_p=\frac{4\zeta\theta}{1+2\zeta\theta+\theta^2}=0.02631$, $K_i=\frac{4\theta^2}{1+2\zeta\theta+\theta^2}=3.51\times10^{-4}$ (with $K_dK_0=1$). Characteristic polynomial $z^2-1.97334z+0.97369$: poles at $|z|=0.98676$. The analogue type-2 loop with the same $B_n$ has $\omega_nT=2B_nT/(\zeta+1/4\zeta)=0.01886$, whose poles mapped by $e^{sT}$ are within 6×10⁻⁷ of the digital ones — the design is a faithful discretisation. Numerically integrating $|H_{cl}(e^{j\omega})|^2$ gives $B_nT$ = 0.01009 (target 0.01). Triangle check: $0<K_p<2$ and $0<K_i<4-2K_p$ hold by orders of magnitude, so the loop has huge gain margin; it is the *phase-detector nonlinearity* (cycle slips), not linear instability, that limits it ([synchronisation](../10-comms-modulation/synchronization-carrier-timing.md), [GNSS tracking loops](../21-gnss/gnss-receiver-architecture-acquisition-tracking.md)).

**4. How much does oversampling buy a 1-bit ΣΔ?** Levels ±1 (Δ = 2, $\Delta^2/12=1/3$), half-scale sine input, $2^{17}$ samples. Simulated in-band noise vs linear model:

| OSR | 1st order sim / model | 2nd order sim / model |
|---|---|---|
| 32 | −47.7 / −44.8 dB | −64.1 / −67.1 dB |
| 64 | −55.1 / −53.8 dB | −79.0 / −82.2 dB |
| 128 | −63.6 / −62.8 dB | −94.5 / −97.2 dB |

Slopes: 7.9 dB/octave (first order; model 9.0 — first-order loops are tonal) and 15.2 dB/octave (second order; model 15.1). The linear model is good to ~3 dB here; with near-full-scale inputs 1-bit loops fall further short (4–9 dB in the [data-converter page's](../05-analog-electronics/data-converters-adc-dac.md) simulations), so real designs are checked by simulation exactly like this.

**5. A structural/servo resonance seen by a 1 kHz control loop.** A fin-servo linkage mode at 50 Hz with ζ = 0.3 sampled at 1 kHz has z-plane poles at $r=e^{-0.3\cdot2\pi\cdot50/1000}=0.910$, $\theta=2\pi\cdot50\sqrt{1-0.09}/1000=0.300$ rad. A notch filter for it puts zeros at $e^{\pm j0.314}$ (50 Hz) on the circle and poles at the same angle with radius ≈ 0.95 to set the notch width $\approx2(1-0.95)f_s/2\pi$ ≈ 16 Hz. Recovering $\omega_n$ and ζ from fitted digital poles uses $\omega_n=|\ln z|/T$, $\zeta=-\mathrm{Re}\ln z/|\ln z|$ (verified round trip).

## Practical notes
- **Write the recursion and $H(z)$ side by side** in firmware comments; it makes coefficient sign errors (the classic $a_1$ vs $-a_1$ convention clash between textbooks and `lfilter`) obvious. SciPy/MATLAB use $a$ with $+a_kz^{-k}$ in the denominator.
- **Use second-order sections** (biquads, `sosfilt`) for IIR filters above order ~4; high-order direct forms have poles that move hugely with coefficient rounding ([digital filters, Level 3](../14-sdr-dsp/digital-filters-fir-iir.md)).
- **Poles close to $z=1$ need precision.** An EMA with α = 10⁻⁴ in float32 has a pole at 0.9999 that is stored with ~7 significant digits — fine — but a sum like $y+\alpha(x-y)$ with large DC offset loses low bits; subtract the offset or use float64/fixed-point with guard bits.
- **Initialise recursions sensibly**: start an EMA at the first sample, not 0, or the zero-input transient (decaying at $p^n$) masquerades as a real signal — a launch detector watching smoothed acceleration can false-trigger on a bad initial state.
- **Sample-rate changes move every pole.** A filter designed for 100 Hz is a different filter at 50 Hz (same coefficients, $\omega$ doubles); derive coefficients from physical time constants and $T$ at run time if the loop rate can vary.
- **Control and estimator loops add delay**: each sample of computational delay is a factor $z^{-1}$, i.e. a phase lag $\omega$ rad at frequency ω — it eats phase margin exactly like a transport delay in the s-domain ([feedback and stability](../05-analog-electronics/feedback-and-stability.md)).

## Common mistakes & misconceptions
1. **"$H(z)$ defines the system."** Not without the ROC: causal and anti-causal sequences share the same rational $X(z)$. In engineering practice causality is assumed, so the ROC is outside the outermost pole.
2. **Confusing $z$ and $z^{-1}$ forms.** $\frac{1}{1-0.9z^{-1}}=\frac{z}{z-0.9}$ — same system; reading poles from the wrong form (or from MATLAB's descending powers of $z$ vs SciPy's ascending powers of $z^{-1}$) gives reciprocal "poles".
3. **Treating $\omega$ as Hz.** $\omega$ is rad/sample; $f=\omega f_s/2\pi$. Many "the filter is at the wrong frequency" bugs are a missing $f_s$ or $2\pi$.
4. **Using the bilinear transform without prewarping** — edges shift towards DC (1 kHz at 10 kS/s lands where the analogue 1034 Hz is).
5. **Using impulse invariance for high-pass/band-stop** — aliasing makes it fail; it also does not map zeros by $e^{sT}$.
6. **Forward-Euler-integrating fast dynamics** — stable continuous systems become unstable when $|s|T>2$.
7. **Assuming a pole on the unit circle is "just barely stable".** An accumulator is marginally stable: a constant (or slowly biased) input grows without bound — the reason gyro-bias integration drifts and why integrators in loops need anti-windup.
8. **Applying the final-value theorem when $(1-z^{-1})X(z)$ has poles on or outside the circle** — the "limit" it returns does not exist.
9. **Equating noise reduction with lag-free smoothing.** A one-pole filter reduces variance by $\alpha/(2-\alpha)$ and delays by $(1-\alpha)/\alpha$ samples; you cannot improve one without worsening the other without a model.
10. **Forgetting that digital frequency responses repeat** — a "low-pass" also passes $f_s\pm f$, so the analogue anti-alias filter is not optional ([sampling](../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md)).

## How to simulate / verify
- `python3 tools/verify/est_ztransform.py` (≈ 1.5 s, **ALL PASS**): pairs by direct summation incl. causal/anti-causal ROC; `residuez` inverse; stability; unilateral transform with initial conditions; final value; freqz = DTFT; EMA worked-example values; bilinear map, warping, prewarp vs `scipy.signal.bilinear`; impulse invariance and matched-z; $z=e^{sT}$ round trip; digital PLL poles, type-2 behaviour and $B_nT$; first/second-order ΣΔ identity and in-band noise; CIC identity; FIR group delay; stability triangle vs roots; Euler mappings; resonator width; state-space $e^{\mathbf AT}$ poles.
- Python: `scipy.signal` (`lfilter`, `freqz`, `group_delay`, `tf2zpk`, `zpk2sos`, `residuez`, `bilinear`, `bilinear_zpk`, `cont2discrete` for ZOH/bilinear/Euler discretisation of state-space models). `cont2discrete(..., method='zoh')` gives the exact $e^{\mathbf AT}$ discretisation used by Kalman filters.
- Plot a pole–zero map (`tf2zpk` + the unit circle) for every filter you put in firmware; check every pole radius is < 1 with margin for coefficient quantisation.

## Open questions / gaps
- Limit cycles and overflow oscillations in fixed-point IIR sections are only summarised (see [digital filters](../14-sdr-dsp/digital-filters-fir-iir.md)); no fixed-point simulation here.
- Zero-order-hold (ZOH) discretisation and the modified z-transform (for systems with fractional sample delay) are mentioned only via `cont2discrete`; derivations not given.
- The ΣΔ linear model is checked only for 1-bit first/second order with a sine input; higher-order loops (stability limits, maximum stable amplitude) are not covered.

## Sources
1. A. V. Oppenheim, R. W. Schafer, *Discrete-Time Signal Processing*, 3rd ed., Pearson (2010): ch. 3 (z-transform, ROC properties, inverse by partial fractions/power series, properties, unilateral transform), ch. 5 (transform analysis: pole–zero/geometric frequency response, all-pass, minimum phase, linear phase), §7.1–7.2 (impulse invariance and the bilinear transform with warping). (textbook; section numbers from the 3rd-ed. table of contents as recalled — high confidence, standard)
2. R. G. Lyons, *Understanding Digital Signal Processing*, 3rd ed., Prentice Hall (2011): §6.3–6.5 (z-transform, IIR analysis, poles/zeros), ch. 6 IIR design methods (impulse invariance, bilinear), ch. 10 (CIC filters), ch. 11 (signal averaging incl. the exponential averager). (textbook; chapter numbers as recalled; §6.3–6.5 per gap-row D4 #12)
3. A. V. Oppenheim, A. S. Willsky, S. H. Nawab, *Signals and Systems*, 2nd ed., Prentice Hall (1997): ch. 10 (z-transform, ROC, relation to the DTFT), §7.1–7.4 (sampling, aliasing). (textbook)
4. M. Rice, *Digital Communications: A Discrete-Time Approach*, Pearson (2009), App. C (discrete-time PLL loop-filter design from $B_nT$ and ζ via the bilinear transform) — gains reproduced and their poles compared with $e^{sT}$ of the analogue loop in the verify script. (textbook; via the KB's [synchronisation page](../10-comms-modulation/synchronization-carrier-timing.md))
5. R. Schreier, G. C. Temes, *Understanding Delta-Sigma Data Converters*, Wiley-IEEE (2005), ch. 2–4 (first/second-order modulators, NTF/STF, in-band noise $\pi^{2L}/((2L+1)\mathrm{OSR}^{2L+1})$). (textbook; recalled — formula re-derived on this page and checked by simulation)
6. E. B. Hogenauer, "An economical class of digital filters for decimation and interpolation," *IEEE Trans. ASSP* 29(2):155–162 (1981) — CIC structure and register growth. (peer-reviewed; recalled citation, identity verified numerically)
7. E. I. Jury, *Theory and Application of the z-Transform Method*, Wiley (1964) — stability criterion (the second-order case used here was verified against a root test). (textbook; recalled)
8. SciPy documentation, `scipy.signal` (lfilter, freqz, residuez, bilinear, cont2discrete, group_delay). https://docs.scipy.org/doc/scipy/reference/signal.html (docs) — tools used for verification.
