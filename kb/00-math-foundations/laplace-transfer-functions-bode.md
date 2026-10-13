---
title: Laplace transform, transfer functions and Bode plots
domain: 00-math-foundations
slug: laplace-transfer-functions-bode
tags: [laplace, transfer-function, poles, zeros, bode, stability, phase-margin, minimum-phase, group-delay, s-plane]
prerequisites: [complex-numbers-and-phasors.md, differential-equations-circuits-waves.md]
related:
  - linear-systems-convolution.md
  - fourier-series-and-transform.md
  - ../01-circuit-theory/passive-filter-design-prototypes.md
  - ../01-circuit-theory/transient-and-step-response.md
  - ../01-circuit-theory/resonance-and-q.md
  - ../05-analog-electronics/feedback-and-stability.md
  - ../05-analog-electronics/active-filters.md
  - ../06-rf-circuits/vco-and-pll-synthesizers.md
  - ../06-rf-circuits/amplifier-stability-and-biasing.md
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Laplace transform, transfer functions and Bode plots

## Questions this page answers
- What is the Laplace variable $s$, and how is it related to $j\omega$?
- What are poles and zeros *physically*, and why does their position tell me whether a circuit rings, decays or oscillates?
- How do I sketch a Bode plot by hand?
- What are damping ratio, natural frequency and Q, and how do they relate to overshoot and peaking?
- What do phase margin and gain margin mean, and why do amplifiers and PLLs oscillate?
- What is a minimum-phase system, and why does a delay or a right-half-plane zero make control harder?
- What is group delay, and why does a narrow filter delay my signal?
- Why is rise time × bandwidth ≈ 0.35?

## TL;DR
- The Laplace transform $F(s)=\int_{0^-}^\infty f(t)e^{-st}dt$ with complex $s=\sigma+j\omega$ turns linear ODEs with initial conditions into algebra; $d/dt\to s$. The transfer function $H(s)=Y(s)/X(s)$ is the ratio of output to input transforms with zero initial conditions.
- Setting $s=j\omega$ gives the frequency response (phasor gain) $H(j\omega)$ — provided the system is stable. Impedances in $s$: $R$, $sL$, $1/(sC)$.
- **Poles** (roots of the denominator) are the system's natural modes $e^{p t}$. Left half-plane (Re $p<0$) → decaying; on the $j\omega$ axis → sustained oscillation; right half-plane → growth (instability, or an oscillator starting up). Distance from the axis = decay rate; height = ringing frequency.
- **Second order**: $H=\omega_n^2/(s^2+2\zeta\omega_ns+\omega_n^2)$, $Q=1/(2\zeta)$. Peaking for $\zeta<1/\sqrt2$: peak $1/(2\zeta\sqrt{1-\zeta^2})$; step overshoot $e^{-\pi\zeta/\sqrt{1-\zeta^2}}$ ($\zeta=0.5$ → 16 %).
- **Bode sketching**: each real pole: −20 dB/decade after its corner, phase −45° at the corner, spanning 0.1× to 10× (3 dB and 5.7° worst errors); each real zero: the mirror image. Complex pole pair: −40 dB/dec, −180°, peak near $\omega_n$.
- **Stability of feedback** (loop gain $L(j\omega)$): phase margin = $180°+\angle L$ at $|L|=1$; aim ≥ 45–60°. Gain margin = $-20\log|L|$ where $\angle L=-180°$.
- **Minimum phase**: all zeros in the left half-plane; magnitude determines phase (Bode gain–phase relation: roughly −90° per −20 dB/dec of slope). Delays and RHP zeros add phase lag without changing magnitude.
- **Group delay** $\tau_g=-d\phi/d\omega$ (s). RC low-pass: $\tau_g(0)=RC$. A resonator of loaded Q at $f_0$: $\tau_g=2Q/\omega_0$ — a Q = 10 filter at 433 MHz delays by 7.35 ns. Single-pole rise time × bandwidth $=\ln9/(2\pi)=0.35$.

## Intuition (no math)
Think of hitting a bell. It rings at a certain pitch and dies away at a certain rate. Those two numbers — ringing frequency and decay rate — are the bell's "natural mode", and every linear circuit has a few such modes. A pole is just a compact way of writing one mode: its height above the axis is the ringing frequency, its distance to the left of the axis is how fast it dies. Poles on the left: modes die (stable). On the axis: ring forever (an ideal oscillator). On the right: grow (unstable — or an oscillator starting up, which then limits).

The Laplace transform generalises the phasor. Phasors handle $e^{j\omega t}$ — steady sinusoids. Laplace handles $e^{st}$ with complex $s$ — sinusoids that are growing or decaying. That covers switch-on transients, ringing and instability. Walk along the imaginary axis ($s=j\omega$) and you get back to the ordinary frequency response.

A Bode plot is the frequency response on log–log paper (dB vs log frequency) plus phase. On those axes every pole and zero becomes a straight-line "bend", so you can sketch complex responses by adding bends. Bode plots are how you read filter datasheets, design loop filters for PLLs, and check whether an amplifier will oscillate.

A feedback loop oscillates when a signal goes round the loop and comes back the same size and in step with itself (phase shift of 360°, i.e. 180° from the inverting feedback plus 180° from lags). Phase margin measures how far you are from that: how many degrees of extra lag you could tolerate at the frequency where loop gain is 1.

Group delay: a narrow filter can only respond slowly (it can't tell frequencies within its bandwidth apart any faster than 1/bandwidth), so it delays the envelope of the signal passing through. Sharper filters → longer delay → more ringing on pulses.

## The math

### Level 1 — transfer functions with $s$ as "$j\omega$ plus decay"

Replace each component by its $s$-domain impedance and solve the circuit with algebra:
$$Z_R=R,\qquad Z_L=sL,\qquad Z_C=\frac{1}{sC}.$$
Example, RC low-pass (series R, shunt C, output across C):
$$H(s)=\frac{V_{\rm out}}{V_{\rm in}}=\frac{1/(sC)}{R+1/(sC)}=\frac{1}{1+sRC}=\frac{1}{1+s/\omega_c},\qquad \omega_c=\frac1{RC}.$$
Put $s=j\omega$: $|H|=1/\sqrt{1+(\omega/\omega_c)^2}$, $\angle H=-\arctan(\omega/\omega_c)$. At $\omega=\omega_c$: −3.01 dB and −45°. Far above: $|H|\approx\omega_c/\omega$ → falls 20 dB per decade.

Units: $s$ has units of s⁻¹ (rad/s or neper/s). Frequency in Hz: $f=\omega/2\pi$.

### Level 2 — the Laplace transform, poles/zeros, second-order systems, Bode sketching

**Definition** (one-sided, lower limit $0^-$ so impulses at $t=0$ are included) [1 §9], [2 §25–27]:
$$F(s)=\int_{0^-}^{\infty}f(t)e^{-st}\,dt,\qquad s=\sigma+j\omega.$$

| $f(t)$, $t\ge0$ | $F(s)$ |
|---|---|
| $\delta(t)$ | $1$ |
| $u(t)$ (step) | $1/s$ |
| $t$ | $1/s^2$ |
| $e^{-at}$ | $1/(s+a)$ |
| $te^{-at}$ | $1/(s+a)^2$ |
| $\sin\omega_0t$ | $\omega_0/(s^2+\omega_0^2)$ |
| $\cos\omega_0t$ | $s/(s^2+\omega_0^2)$ |
| $e^{-at}\sin\omega_dt$ | $\omega_d/((s+a)^2+\omega_d^2)$ |
| $f(t-T)u(t-T)$ | $e^{-sT}F(s)$ (delay) |
| $df/dt$ | $sF(s)-f(0^-)$ |
| $\int_0^tf\,d\tau$ | $F(s)/s$ |
| $(f*g)(t)$ | $F(s)G(s)$ |

(Pairs checked symbolically with sympy in `tools/verify/math_laplace_bode.py`.)

**Initial and final value theorems.** $f(0^+)=\lim_{s\to\infty}sF(s)$; $f(\infty)=\lim_{s\to0}sF(s)$ if all poles of $sF(s)$ are in the left half-plane. E.g. step into $5/(s+2)$ settles at 2.5 (verified).

**Transfer function, poles and zeros.** For an LTI circuit,
$$H(s)=K\frac{(s-z_1)(s-z_2)\cdots}{(s-p_1)(s-p_2)\cdots}.$$
Partial fractions split the response into modes: $H(s)=\sum_k \frac{r_k}{s-p_k}$ ⇒ impulse response $h(t)=\sum_k r_ke^{p_kt}$ (distinct poles). Example: $(s+3)/((s+1)(s+2))=2/(s+1)-1/(s+2)$ (verified with `scipy.signal.residue`). Each real pole contributes a decaying exponential with time constant $-1/p$; each complex pair $p=-\alpha\pm j\omega_d$ contributes $e^{-\alpha t}\cos(\omega_dt+\phi)$ [2 §27].

**Geometric view of $H(j\omega)$.** $|H(j\omega)|=|K|\prod|j\omega-z_i|/\prod|j\omega-p_k|$ and $\angle H=\sum\angle(j\omega-z_i)-\sum\angle(j\omega-p_k)$. Walking up the $j\omega$ axis, the response peaks when you pass close to a pole and dips near a zero [1 §9.4], [2 §28]. A high-Q resonator has poles very close to the axis — hence a sharp peak.

**The second-order system.** The universal form (series RLC, LC filters, PLLs, mechanical resonators):
$$H(s)=\frac{\omega_n^2}{s^2+2\zeta\omega_ns+\omega_n^2},\qquad p_{1,2}=-\zeta\omega_n\pm j\omega_n\sqrt{1-\zeta^2}.$$
$\omega_n$ = natural (undamped) frequency; $\zeta$ = damping ratio; $Q=1/(2\zeta)$. Derivation of these from circuit ODEs: [differential equations](differential-equations-circuits-waves.md). Key results (all verified numerically):

| Quantity | Formula | ζ = 0.1 | ζ = 0.3 | ζ = 0.5 | ζ = 0.707 |
|---|---|---|---|---|---|
| $\lvert H(j\omega_n)\rvert$ | $1/(2\zeta)=Q$ | 5.0 | 1.67 | 1.0 | 0.707 (−3 dB) |
| resonant peak | $1/(2\zeta\sqrt{1-\zeta^2})$ ($\zeta<1/\sqrt2$) | 5.03 (+14.0 dB) | 1.75 (+4.8 dB) | 1.155 (+1.25 dB) | none |
| peak frequency | $\omega_n\sqrt{1-2\zeta^2}$ | 0.990ω_n | 0.906ω_n | 0.707ω_n | — |
| step overshoot | $e^{-\pi\zeta/\sqrt{1-\zeta^2}}$ | 73 % | 37 % | 16.3 % | 4.3 % |
| ringing frequency | $\omega_d=\omega_n\sqrt{1-\zeta^2}$ | | | | |
| 2 % settling time | ≈ $4/(\zeta\omega_n)$ | | | | |

$\zeta=1/\sqrt2$ is the 2nd-order Butterworth (maximally flat, no peak). $\zeta=1$ is critically damped. The widely quoted "peak = $1/(2\zeta)$" is the value *at* $\omega_n$; the true maximum is slightly higher and lower in frequency [3].

**Bode sketching rules** [3], [1 §6.2]. Write $H$ as products of standard factors; in dB they *add*, and so do phases.

| Factor | Magnitude asymptote | Phase | Worst error of asymptote |
|---|---|---|---|
| constant $K$ | $20\log\lvert K\rvert$ flat | 0° (or 180° if $K<0$) | 0 |
| $s$ (zero at origin) | +20 dB/dec, 0 dB at ω = 1 | +90° | 0 |
| $1/s$ (integrator) | −20 dB/dec | −90° | 0 |
| $1/(1+s/\omega_c)$ | 0, then −20 dB/dec above $\omega_c$ | 0 → −90°, −45° at $\omega_c$, straight line from $0.1\omega_c$ to $10\omega_c$ | 3.01 dB at $\omega_c$; 5.71° at $0.1\omega_c$ and $10\omega_c$ |
| $1+s/\omega_z$ (LHP zero) | 0, then +20 dB/dec | 0 → +90° | same |
| $1-s/\omega_z$ (RHP zero) | 0, then +20 dB/dec | 0 → **−90°** | same |
| complex pole pair ($\omega_n,\zeta$) | 0, then −40 dB/dec; peak ≈ $Q$ near $\omega_n$ | 0 → −180° over $\omega_n10^{\mp\zeta}$ | large if ζ small |
| delay $e^{-sT}$ | 0 dB | $-\omega T$ (linear in ω; on a log axis it plunges) | — |

**Feedback stability.** For a negative-feedback loop with loop gain $L(s)=A(s)\beta(s)$, the closed loop $A/(1+L)$ has poles where $L(s)=-1$. On a Bode plot:
- crossover frequency $\omega_c$: $|L(j\omega_c)|=1$ (0 dB);
- **phase margin** $\mathrm{PM}=180°+\angle L(j\omega_c)$;
- **gain margin** $\mathrm{GM}=-20\log|L(j\omega_{180})|$ where $\angle L=-180°$.
PM relates to closed-loop damping: for the common loop $L=K/(s(1+s/p))$ the closed loop is second-order with $\zeta\approx\mathrm{PM}/100$ for PM ≲ 60° (a rule of thumb, not exact). PM = 45° gives roughly 20–25 % step overshoot; 60° gives ~9 %. (Nyquist's criterion is the rigorous version; see [feedback and stability](../05-analog-electronics/feedback-and-stability.md).)

### Level 3 — regions of convergence, minimum phase, group delay, gain–phase relations

**$s$ versus $j\omega$ precisely.** The bilateral Laplace transform $\int_{-\infty}^\infty f e^{-st}dt$ converges in a vertical strip (region of convergence, ROC). For causal signals the ROC is to the right of the rightmost pole. The Fourier transform is the Laplace transform on the $j\omega$ axis, so it exists (as an ordinary function) only if the ROC includes that axis — i.e. a causal system has a frequency response only if all its poles are in the left half-plane [1 §9.2, §9.7]. An unstable system's "$H(j\omega)$" computed by substitution is meaningless as a steady-state response.

**Minimum-phase, all-pass and non-minimum-phase.** Any rational stable $H$ factors as $H=H_{\min}\,H_{\rm ap}$: a minimum-phase part (all poles and zeros in the LHP) and an all-pass part $\prod\frac{s-z_i}{s+z_i^*}$ with $|H_{\rm ap}(j\omega)|=1$. For a given magnitude response, the minimum-phase version has the least phase lag and least group delay [1 §6.2]. Examples of non-minimum phase: a pure delay $e^{-sT}$ (cable, propagation, digital pipeline), an RHP zero (boost-converter control-to-output; some feed-forward amplifier paths). Verified: $(s+1)/(s+2)$ and $(1-s)/(s+2)$ have identical magnitude, but the second accumulates ~180° extra lag at high frequency. Practical consequence: non-minimum-phase lag eats phase margin, limiting achievable loop bandwidth (e.g. digital delay in an SDR-based AGC or a PLL with a divider/pipeline delay).

**Bode gain–phase relation.** For a stable minimum-phase $H$, with $A(u)=\ln|H(j\omega)|$ and $u=\ln(\omega/\omega_0)$,
$$\angle H(j\omega_0)=\frac1\pi\int_{-\infty}^{\infty}\frac{dA}{du}\,\ln\coth\frac{|u|}{2}\,du.$$
The weight $\ln\coth(|u|/2)$ is sharply concentrated near $u=0$ and integrates to $\pi^2/2$, so a constant slope of $-20n$ dB/decade (i.e. $dA/du=-n$) gives $-n\cdot90°$. This is why "−20 dB/dec ↔ −90°" and why you cannot have steep magnitude roll-off near crossover without large phase lag. Verified numerically: the integral reproduces $-\arctan\omega$ for a real pole from its magnitude alone. This is a special case of the Hilbert-transform / Kramers–Kronig relations: see [linear systems](linear-systems-convolution.md).

**Phase delay and group delay.** For $H(j\omega)=|H|e^{j\phi(\omega)}$:
$$\tau_p=-\frac{\phi(\omega)}{\omega}\quad(\text{phase delay}),\qquad \tau_g=-\frac{d\phi}{d\omega}\quad(\text{group delay}).$$
A narrowband signal $a(t)\cos\omega_0t$ passing through $H$ emerges approximately as $|H(j\omega_0)|\,a(t-\tau_g)\cos(\omega_0(t-\tau_p))$: the *envelope* is delayed by $\tau_g$ and the *carrier phase* by $\tau_p$ [1 §6.2.2]. A pure delay has $\tau_g=\tau_p=T$ at all frequencies (linear phase: no distortion). Non-constant $\tau_g$ across a signal's bandwidth distorts it (dispersion; ISI in data links; chirp smearing). Standard results (verified):
- RC low-pass: $\tau_g=\dfrac{\tau}{1+(\omega\tau)^2}$ → $\tau$ at DC, $\tau/2$ at the corner.
- Single-tuned resonator (bandpass, loaded $Q$) at centre: $\tau_g=2Q/\omega_0=1/(\pi B_{3\rm dB})$ where $B_{3\rm dB}=f_0/Q$.
- Filters with sharper skirts (Chebyshev, elliptic) have larger group-delay peaks near the band edges than Butterworth; Bessel filters are designed for flat $\tau_g$ ([passive filters](../01-circuit-theory/passive-filter-design-prototypes.md)).
On a VNA, group delay is computed as a finite-difference phase slope over an "aperture"; wide apertures smooth noise but hide ripple [5].

**Rise time and bandwidth.** Single pole: step response $1-e^{-t/\tau}$; 10 %→90 % takes $\tau\ln9=2.197\tau$; with $f_{3\rm dB}=1/(2\pi\tau)$, $t_rf_{3\rm dB}=\ln9/(2\pi)=0.3497$ (verified). Multi-pole Gaussian-like responses give ≈0.34–0.36; systems with peaking give larger products with overshoot.

**Where Laplace/phasor methods stop.** Linear time-invariant only. Time-varying (mixers, switched-capacitor, sampling) and nonlinear (PA compression, oscillator amplitude limiting) systems need other tools (harmonic balance, describing functions, conversion matrices). Distributed elements (transmission lines) give transcendental $H(s)$ (e.g. $e^{-s\ell/v}$, $\tanh$) rather than rational functions, but the frequency-domain ideas still apply ([telegrapher equations](../03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md)).

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $f_c=1/(2\pi RC)$ | 1st-order RC | 10 kΩ, 1 nF → 15.9 kHz |
| $t_r=2.2RC$; $t_rf_{3\rm dB}=0.35$ | single pole | 15.9 kHz → 22 µs |
| $\omega_n=1/\sqrt{LC}$; $\zeta=\frac{1}{2R}\sqrt{L/C}$ | L series, C shunt, load R, ideal source | see example 2 |
| $Q=1/(2\zeta)$ | 2nd order | |
| overshoot $=e^{-\pi\zeta/\sqrt{1-\zeta^2}}$ | 2nd order, no zeros | ζ = 0.5 → 16 % |
| PM $=180°+\angle L(j\omega_c)$ | feedback loops | target 45–60° |
| ζ ≈ PM/100 | PM ≲ 60°, 2-pole loop | rule of thumb |
| $\tau_g=2Q/\omega_0$ | single resonator at centre | Q = 10 @ 433 MHz → 7.35 ns |
| −20 dB/dec ↔ −90° | minimum phase | |
| delay: $\phi=-\omega T$ | pure delay | 1 m RG-58 ≈ 5 ns → −787° at 433 MHz |

## Worked examples

**1. RC filter on a power-detector output.** A log detector's output feeds an ADC through $R=10$ kΩ, $C=1$ nF: $f_c=15.9$ kHz; rise time 22 µs. A LoRa SF7 symbol (1.02 ms) is ~46 rise times — fine for envelope/RSSI; a 1 µs radar pulse would be smeared to ~22 µs (bandwidth too low by ~20×; see [detectors](../06-rf-circuits/detectors-and-power-meters.md)).

**2. A single LC low-pass section.** Series $L=22$ nH, shunt $C=6.8$ pF, 50 Ω load, driven from an ideal voltage source: $H(s)=1/(s^2LC+sL/R+1)$, so $f_n=1/(2\pi\sqrt{LC})=411$ MHz and $\zeta=\frac{1}{2\cdot50}\sqrt{22\,\text{nH}/6.8\,\text{pF}}=0.569$. Peak $+0.58$ dB near 244 MHz; at 433 MHz: −1.6 dB, −95°; at the 866 MHz 2nd harmonic only −12.4 dB (−40 dB/dec asymptote not yet reached). Lesson: one section is nowhere near enough for a transmitter harmonic filter; you need higher order, proper doubly-terminated design, and to include the source impedance (see [passive filter design](../01-circuit-theory/passive-filter-design-prototypes.md), [RF filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md)).

**3. Phase margin of a type-1 loop.** $L(s)=K/(s(1+s/p))$ with $K=2\pi\times10$ kHz and $p=2\pi\times30$ kHz. Solve $|L(j\omega_c)|=1$: $f_c=9.53$ kHz. $\angle L=-90°-\arctan(9.53/30)=-107.6°$ → PM = 72.4°. Closed loop: $\omega_n=\sqrt{Kp}=2\pi\times17.3$ kHz, $\zeta=p/(2\omega_n)=0.87$ → 0.4 % overshoot. Adding a 10 µs pipeline delay would subtract $360°\times9.53\text{ kHz}\times10\,\mu\text{s}=34°$ of phase margin at crossover — the reason delays matter in digital loops. (PLL specifics: [VCO and PLL](../06-rf-circuits/vco-and-pll-synthesizers.md).)

**4. Group delay of a 433 MHz bandpass.** A single-resonator filter with loaded Q = 10 at 433 MHz ($B_{3\rm dB}=43.3$ MHz): $\tau_g=2Q/\omega_0=7.35$ ns at centre. A SAW filter with 1 MHz bandwidth is effectively much higher order and has group delays of order 1 µs — irrelevant to LoRa data (symbols ≥ 1 ms) but it matters for ranging/time-of-flight measurements and for pulse radars. Group-delay *variation* across the channel is what distorts signals.

**5. Poles to time response.** A resonance measured on a VNA at 433 MHz with $Q=50$: $\zeta=0.01$, pole real part $-\zeta\omega_n=-2.72\times10^7$ s⁻¹ → ringing decays with time constant 36.8 ns (≈16 RF cycles per $e$-fold). A PCB power-rail resonance with Q = 5 at 100 MHz rings for $1/(\zeta\omega_n)=1/(0.1\times6.28\times10^8)=15.9$ ns time constant.

**6. Cable delay is non-minimum-phase.** 1 m of solid-PE coax (velocity factor 0.66) delays 5.05 ns: $\phi(433\text{ MHz})=-787°$; group delay 5.05 ns flat. On a VNA, $S_{21}$ phase wraps every 198 MHz. Use "electrical delay" / port extension to remove it before reading a DUT's phase ([VNA fundamentals](../17-test-measurement/vna-fundamentals-calibration.md)).

## Practical notes
- **Reading datasheet Bode plots**: op-amp open-loop gain plots show GBW (gain × frequency constant along the −20 dB/dec line) and phase margin at unity gain. Capacitive loads add a pole → lost phase margin → ringing.
- **Measuring loop gain**: inject a small signal across a series resistor in the loop and measure with a frequency-response analyser or VNA (bench technique in [feedback and stability](../05-analog-electronics/feedback-and-stability.md)).
- **SPICE** `.ac` produces Bode plots directly; `.tran` shows ringing/overshoot. Compare pole positions (`.pz` in ngspice) with the ringing you see.
- **Group delay measurement** on a VNA: set the aperture deliberately; report it.
- **RF amplifier stability** (K-factor, μ) is a two-port generalisation of the same pole-location question; see [amplifier stability](../06-rf-circuits/amplifier-stability-and-biasing.md).

## Common mistakes & misconceptions
1. **Substituting $s=j\omega$ into an unstable $H(s)$** and calling it the frequency response — it is not observable in steady state.
2. **"A pole at 1 MHz" without saying rad/s or Hz** — factor $2\pi$ errors are the most common Bode mistake. Write $s/\omega_c$ with $\omega_c=2\pi f_c$.
3. **Taking the resonant peak as exactly $1/(2\zeta)$** and at exactly $\omega_n$ — true peak is $1/(2\zeta\sqrt{1-\zeta^2})$ at $\omega_n\sqrt{1-2\zeta^2}$ [3].
4. **"Phase margin of 0° means it oscillates at the gain crossover frequency; 5° is fine."** Small PM gives large peaking and ringing even though technically stable; component tolerances and temperature eat the margin.
5. **Ignoring RHP zeros and delays** because the magnitude plot looks benign; phase tells the truth.
6. **Confusing phase delay with group delay** — for a carrier through a filter they differ; the envelope (information) moves at the group delay.
7. **Assuming all filters have flat group delay** — Chebyshev/elliptic filters (and SAWs) have significant ripple; affects pulse shape and PSK/QAM EVM.
8. **Forgetting the $0^-$ initial conditions** when using Laplace to solve switch-on transients — the $-f(0^-)$ terms in the derivative rule carry stored energy.
9. **Believing Bode asymptotes are exact** — they are off by 3 dB at corners and can be badly off near lightly damped poles.
10. **Q confusion**: $Q=1/(2\zeta)$ for the 2nd-order low-pass form; for a bandpass, $Q=f_0/B_{3\rm dB}$ — same pole Q, but make sure which response you are reading ([resonance and Q](../01-circuit-theory/resonance-and-q.md)).

## How to simulate / verify
- `python3 tools/verify/math_laplace_bode.py` — sympy Laplace pairs; residues; Bode asymptote errors (3.01 dB, 5.71°); 2nd-order peak/peak-frequency/Q/overshoot for ζ = 0.1, 0.3, 0.5; Butterworth flatness; RC and resonator group delay; minimum- vs non-minimum-phase; Bode gain–phase integral; final-value theorem; rise time × bandwidth. All PASS.
- Python: `scipy.signal.lti`, `freqs`, `bode`, `step`, `residue`, `tf2zpk`; `python-control` for margins (`control.margin`).
- SPICE: `.ac dec 100 1k 1G` and plot `db(v(out))`, `ph(v(out))`; `.pz` for pole–zero.

## Open questions / gaps
- The PM ↔ ζ and PM ↔ overshoot rules of thumb are approximate; the feedback page (05-analog) should tabulate exact values for the standard loop shapes.
- Nyquist criterion and conditionally stable loops are only mentioned; they belong in 05-analog-electronics/feedback-and-stability.

## Sources
1. A. V. Oppenheim, A. S. Willsky, S. H. Nawab, *Signals and Systems*, 2nd ed., Prentice Hall (1997): §6.2 (magnitude–phase representation, linear/non-linear phase, group delay, log-magnitude/Bode plots), §6.5–6.6 (first- and second-order systems), ch. 9 (Laplace transform: §9.2 ROC, §9.4 geometric evaluation of the Fourier transform from the pole–zero plot, §9.7 causality/stability), ch. 11 (feedback) (textbook).
2. H. R. Miller, *18.03 Supplementary Notes*, MIT (2012): §15 natural frequency and damping ratio; §16 frequency response; §25–27 Laplace transform and pole diagram; §28 amplitude response and the pole diagram. https://math.mit.edu/classes/18.03/sup/sup0.pdf (lecture notes).
3. E. Cheever, "The asymptotic Bode diagram: derivation of approximations," Swarthmore College Linear Physical Systems Analysis. https://lpsa.swarthmore.edu/Bode/BodeHow.html (lecture notes) — asymptote rules and errors; its "peak = 1/(2ζ)" is the value at $\omega_n$ (exact peak derived here).
4. D. Freeman, MIT 6.003 (Fall 2011), lectures 6 (Laplace), 11 (CT frequency response and Bode plot), 12–13 (CT feedback and control). https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/pages/lecture-notes/ (lecture notes).
5. Keysight Technologies, E5080B VNA help, "Group delay" (definition, aperture). https://helpfiles.keysight.com/csg/e5080b/Tutorials/Group_Delay6_5.htm (manufacturer documentation).
6. H. W. Bode, *Network Analysis and Feedback Amplifier Design*, Van Nostrand (1945), ch. 13–14 (gain–phase relations) (textbook, historical; cited for the gain–phase integral, re-derived/verified numerically here).
