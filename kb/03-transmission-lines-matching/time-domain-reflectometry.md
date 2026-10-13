---
title: Time-domain reflectometry (TDR) and VNA time-domain analysis
domain: 03-transmission-lines-matching
slug: time-domain-reflectometry
tags: [tdr, time-domain, vna, inverse-fft, windowing, kaiser, gating, impedance-profile, fault-location, nanovna, resolution, aliasing, lattice-diagram, bounce-diagram, bergeron, reactive-termination, ringing, masking, ghost-reflections, signal-integrity]
prerequisites:
  - reflections-vswr-return-loss-mismatch.md
  - s-parameters.md
  - ../00-math-foundations/fourier-series-and-transform.md
related:
  - coax-and-cables.md
  - planar-lines-microstrip-stripline-cpwg.md
  - ../14-sdr-dsp/fft-spectral-analysis-windows.md
  - ../17-test-measurement/vna-fundamentals-calibration.md
  - ../17-test-measurement/nanovna-librevna-practical.md
  - ../17-test-measurement/fixtures-and-deembedding.md
  - ../13-pcb-rf-layout-emc/digital-termination-and-crosstalk.md
  - ../01-circuit-theory/transient-and-step-response.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Time-domain reflectometry (TDR) and VNA time-domain analysis

## Questions this page answers
- How does a TDR show the impedance along a cable or PCB trace?
- How do I tell a capacitive from an inductive discontinuity on a TDR trace, and how big is it?
- How can a VNA (or NanoVNA) produce a TDR plot from frequency data?
- What sets the spatial resolution and the maximum distance ("alias-free range")?
- What do the minimum / normal / maximum windows do?
- What are low-pass vs band-pass modes, and gating?
- How do I find a bad connector or a kink in a long antenna feed?
- How do I draw a lattice (bounce) diagram, and what does it look like for a capacitive or inductive load?
- Why does a fast logic edge ring and overshoot at the end of a long trace, and how big is the overshoot?
- Why is the second step on my TDR trace smaller than the first, and what are the small "ghost" steps after it?

## TL;DR
- A TDR launches a fast step into the line and records the reflection vs time. The reflected fraction $\rho(t)$ maps to impedance: $Z(t)=Z_0\dfrac{1+\rho(t)}{1-\rho(t)}$ (first-order; later features are distorted by earlier reflections and loss). Distance $=v_pt/2$.
- Shapes: higher-Z section → positive step; lower-Z → negative; **series inductance → positive bump**, **shunt capacitance → negative dip**; open → +1, short → −1. Bump areas give the element: $L=2Z_0\int\rho\,dt$, $C=-\dfrac{2}{Z_0}\int\rho\,dt$ (verified: 3 nH and 1.5 pF recovered to < 0.6 % from band-limited data).
- A VNA does the same numerically: measure $S_{11}$ on a harmonic grid $f_n=n\Delta f$, extrapolate DC, window, inverse-FFT (**low-pass mode**). Step rise time (10–90 %) ≈ **0.45 / 0.99 / 1.48 ÷ span** for minimum / normal / maximum window; impulse width ≈ 0.60 / 0.98 / 1.39 ÷ span (Keysight AN 1287-12; reproduced here within 2 % with Kaiser β = 0 / 6 / 13).
- **Resolution** in distance ≈ (width × $v_p$)/2; two equal events need ≈ 1.25× that for a 3 dB dip between them. NanoVNA to 900 MHz: ≈ 11 cm in RG-58 (normal window); 3 GHz: ≈ 3.3 cm; 6 GHz: ≈ 1.6 cm.
- **Alias-free range**: $1/\Delta f$ in time → $v_p/(2\Delta f)$ distance. 101 points over 900 MHz: 11 m in VF 0.66 cable; use more points or a narrower span for long feeders.
- **Lattice (bounce) diagrams** (Level 2b): first wave $v_1=V_sZ_0/(R_s+Z_0)$, reflections $\Gamma_L$, $\Gamma_S$, voltage = sum of passed waves. A reactive load is a circuit driven by **$2v_i(t)$ behind $Z_0$**: a capacitor reflects $v_1(1-2e^{-t/Z_0C})$, an inductor $v_1(2e^{-tZ_0/L}-1)$. Lattice, FDTD and IFFT agree to ≤ 0.4 % for R, C, L, RC and series-LR loads. A 15 Ω driver into 150 mm of 50 Ω line and a 5 pF input overshoots **+64 %**; a series resistor making Rs = Z0 removes it. TDR "ghosts" fall by ρ² per section round trip.
- **Windows** trade resolution for sidelobes: minimum −13 dB impulse sidelobes (fine detail, ringing), normal −44 dB, maximum ≈ −75 dB or lower. **Band-pass mode** (no DC needed, any span) gives magnitude-only fault location with 2× wider impulses. **Gating** removes chosen responses (e.g. connectors) before transforming back.

## Intuition (no math)
Send a step voltage down a 50 Ω cable. As long as the edge travels through 50 Ω, nothing comes back. When it meets a section of higher impedance, part of the step reflects with the same sign (voltage rises); a lower impedance reflects with opposite sign. A small series inductor briefly "looks like" a high impedance while the current through it is changing — a short positive blip; a small shunt capacitor briefly looks like a short while it charges — a short negative blip. The time at which each feature returns tells you where it is (half the round-trip time times the propagation speed), the height tells you how big the impedance change is, and the shape tells you what kind of discontinuity it is.

A VNA measures the same information one frequency at a time. Because the system is linear, the response to a step is just the inverse Fourier transform of the frequency response (times the step's spectrum). The catch: the VNA only measures up to a maximum frequency (so the "step" has a finite rise time and ripples), at discrete frequency steps (so the time record repeats — aliases), and not at DC (so DC must be extrapolated). Windowing smooths the abrupt band edge to suppress the ripples, at the cost of a slower edge.

## The math

### Level 1 — reading a TDR
- Reflection coefficient at the discontinuity: $\rho=\dfrac{Z-Z_0}{Z+Z_0}$ ⇒ $Z=Z_0\dfrac{1+\rho}{1-\rho}$. A step to $\rho=+0.2$ on a 50 Ω system means a 75 Ω section (script: 74.8 Ω).
- Distance: $d=v_p\,t/2=VF\cdot c\,t/2$. For VF 0.66: 9.9 cm per ns of round trip.
- A section shorter than the rise-time distance never reaches its full plateau — its apparent impedance is too close to $Z_0$.

### Level 2 — lumped discontinuities and the VNA transform

**Series L.** A small series inductor $L$ between two $Z_0$ lines has $\Gamma(j\omega)=\dfrac{j\omega L}{2Z_0+j\omega L}\approx\dfrac{j\omega L}{2Z_0}$ for $\omega L\ll2Z_0$. Multiplying by $j\omega$ is differentiation, and the incident is a step $u(t)$, so the reflected step response is $\rho(t)\approx\dfrac{L}{2Z_0}\delta(t)$ smoothed by the rise time: a positive bump of area $L/(2Z_0)$ → $L=2Z_0\int\rho\,dt$. Exactly: $\rho(t)=e^{-t/\tau}$ with $\tau=L/(2Z_0)$, area $\tau$.
**Shunt C.** $\Gamma=\dfrac{-j\omega CZ_0}{2+j\omega CZ_0}$ → negative bump of area $CZ_0/2$ → $C=-\dfrac{2}{Z_0}\int\rho\,dt$; exact time constant $\tau=Z_0C/2$.
The *areas* survive band-limiting and windowing (they are the DC value of $\Gamma/j\omega$), which is why they are the robust way to size a discontinuity. Script: 2.991 nH (true 3 nH) and 1.496 pF (true 1.5 pF) from a 3 GHz, 1000-point low-pass transform.

**Low-pass transform.** Measure $S_{11}(f_n)$ at $f_n=n\Delta f$, $n=1\ldots N$ (span $F=N\Delta f$). Extrapolate $S_{11}(0)$ (real; since $\mathrm{Re}\,S$ is even in $f$, fit $a+bf^2$ through the lowest points — a poor DC estimate adds an offset to the whole step response), build the Hermitian spectrum $S(-f)=S^*(f)$, multiply by a window $W(f)$, inverse-FFT:
$$h[k]=\frac1M\sum_{n=-N}^{N}W_nS_ne^{j2\pi nk/M},\qquad \rho[k]=\sum_{m\le k}h[m],\qquad t_k=\frac{k}{M\Delta f}$$
($M$ = FFT length after zero-padding, which interpolates but adds no resolution). The impulse response $h$ is real because of the Hermitian extension; the step response $\rho$ is its running sum.

**Resolution.** With no window (rectangular), the impulse is a sinc of main-lobe width $\sim1/F$ with −13 dB sidelobes. A Kaiser window with parameter β widens the main lobe and lowers the sidelobes. Numerical results (script, 3 GHz span) vs Keysight's table [1]:

| Window | Kaiser β | Step rise 10–90 % (× 1/span) | LP impulse width 50 % (× 1/span) | Impulse sidelobes |
|---|---|---|---|---|
| Minimum | 0 | 0.443 (Keysight 0.45) | 0.603 (0.60) | −13 dB (−13) |
| Normal | 6 | 0.986 (0.99) | 0.977 (0.98) | −44 dB (−44) |
| Maximum | 13 | 1.462 (1.48) | 1.388 (1.39) | −98 dB (Keysight −75) |

(The maximum-window sidelobe level differs, so Keysight's "maximum" is evidently not exactly β = 13; the widths match.) Band-pass impulses are 2× wider for the same span [1].

**Distance resolution** of equal-size events: distance ≈ (impulse width) × $v_p$/2; our two-event test (two 5 Ω series resistors) needed 1.25× that for a 3 dB dip: 135 mm at 0.9 GHz, 40 mm at 3 GHz, 20 mm at 6 GHz in VF 0.66 cable, scaling exactly as 1/span.

**Alias-free range.** Sampling in frequency at $\Delta f$ makes the time response periodic with period $1/\Delta f$. For reflection, the unambiguous one-way distance is $v_p/(2\Delta f)=v_p(N)/(2F)$: 101 points over 900 MHz → 11 m (VF 0.66); 401 points over 3 GHz → 13 m. Reflections from beyond the range fold back ("alias") and appear at wrong positions; a feature that moves when you change the number of points is an alias [1].

### Level 2b — lattice (bounce) diagrams with resistive and reactive terminations

A lattice (bounce, Bergeron) diagram tracks each travelling wave on a distance–time chart: distance across the page, time down it, each wave a diagonal line of slope ±1/v. It is the time-domain picture behind every TDR trace and every ringing logic edge. All results here are checked in `tools/verify/s5_tdr_lattice.py`, which solves each case three independent ways: the lattice bookkeeping, a telegrapher-equation FDTD, and the frequency-domain ABCD solution inverse-FFT'd. They agree to ≤ 0.4 % of the step.

**Resistive ends (algebra).** A source $V_s$ (step) with resistance $R_s$ drives a line $Z_0$ of one-way delay T into a load $R_L$.
1. The first wave is set by the divider the source sees, because the line looks like $Z_0$ until a reflection returns: $v_1=V_s\,Z_0/(R_s+Z_0)$.
2. At the load it reflects with $\Gamma_L=(R_L-Z_0)/(R_L+Z_0)$; back at the source with $\Gamma_S=(R_s-Z_0)/(R_s+Z_0)$.
3. The voltage at any point is the sum of all waves that have passed it so far. The load voltage after the k-th arrival is $v_1(1+\Gamma_L)\sum_{m<k}(\Gamma_S\Gamma_L)^m$, which converges to the DC divider $V_sR_L/(R_s+R_L)$ because $\sum(\Gamma_S\Gamma_L)^m(1+\Gamma_L)Z_0/(R_s+Z_0)$ simplifies to exactly that.

Example: $V_s$ = 1 V, $R_s$ = 10 Ω, $Z_0$ = 50 Ω, open load (ΓL = +1, ΓS = −2/3, v1 = 0.833 V):
```
 source end (z = 0)                         load end (z = l, open)
 t = 0   +0.833 ------------------------->                      (forward wave)
 t = T                                      +0.833 reflects +0.833   V_L = 1.667
 t = 2T  arrives +0.833, reflects -0.556    V_src = 1.111
 t = 3T                                      -0.556 reflects -0.556  V_L = 0.556
 t = 4T  arrives -0.556, reflects +0.370    V_src = 0.926
 t = 5T                                      +0.370, +0.370          V_L = 1.296
 ...     load: 1.667, 0.556, 1.296, 0.803, 1.132 ... -> 1.000 V (ringing ratio Gs*GL = -0.667)
```
The script reproduces this sequence exactly. A low-impedance driver into an unterminated line therefore rings at the frequency $1/(4T)$ with a decay of $|\Gamma_S\Gamma_L|$ per round trip.

**Reactive ends (calculus).** At the load end the line is exactly equivalent to a **Thévenin source $2v_i(t)$ behind $Z_0$**, where $v_i$ is the arriving wave: from $V=v_i+v_r$ and $I=(v_i-v_r)/Z_0$ it follows that $V=2v_i-Z_0I$. Solve that one-port circuit for $V(t)$; the reflected wave is $v_r=V-v_i$. For a step $v_i=v_1u(t)$:

| Load | Circuit with $2v_1$ behind $Z_0$ | Reflected wave $v_r(t)$ | TDR shape (matched source, seen at 2T) |
|---|---|---|---|
| R | divider | $\Gamma_Lv_1$ | flat step |
| C to ground | RC charge, $\tau=Z_0C$ | $v_1(1-2e^{-t/\tau})$: −v1 (short) → +v1 (open) | dip to 0, recovering to 2v1 |
| L to ground | RL, $\tau=L/Z_0$ | $v_1(2e^{-t/\tau}-1)$: +v1 (open) → −v1 (short) | spike to 2v1, decaying to 0 |
| series L + R = Z0 | $\tau=L/2Z_0$ | $v_1e^{-t/\tau}$ | positive bump, area $v_1L/2Z_0$ |
| shunt C across a matched line | $\tau=Z_0C/2$ | $-v_1e^{-t/\tau}$ | negative bump, area $v_1Z_0C/2$ |
| R ∥ C | $\tau=(Z_0\parallel R)C$ | $\to\Gamma_Lv_1$ from −v1 | dip, settling at the R step |

In Laplace terms each end has a reflection transfer function, for example $\Gamma_C(s)=(1-s\tau)/(1+s\tau)$, an all-pass: a capacitor reflects all the energy, only delayed. With a *mismatched* source, every later arrival is another input to the same ODE. By linearity the lattice still works, but the "numbers" on the diagram become waveforms: each end convolves the arriving waveform with its reflection impulse response. The script does this on a 1 ps grid, with an exact exponential update over each step.

**Checks (script):** the matched-source capacitor and inductor formulas to 10⁻³ V; series-L bump area 29.95 ps against L/2Z0 = 30 ps (3 nH); lattice = FDTD = IFFT for Rs = 10 Ω into 200 Ω and into an open, Rs = 15 Ω into 5 pF, Rs = 50 Ω into 1 kΩ ∥ 3 pF, Rs = 50 Ω into 10 nH, and Rs = 25 Ω into 3 nH + 50 Ω.

**What a TDR shows after the first discontinuity (lattice view of masking and ghosts).** Each crossing of an interface multiplies a wave by its transmission coefficient. The round trip through an interface multiplies by $(1+\rho)(1-\rho)=1-\rho^2$. A wave trapped inside a section bounces with $-\rho$ at its far end and $-\rho$ again at its near end. For a 75 Ω, 0.5 m section inside 50 Ω cable (ρ = 0.2), the low-pass step response shows **+0.2000** at 2T1, then a step of $(1-\rho^2)(-\rho)$ = **−0.1920** (not −0.2: masking), and then a **ghost** of $(1-\rho^2)(-\rho)^3$ = **−0.0077** at $2(T_1+2T_2)$, one section round trip later. The IFFT of the cascade's $S_{11}$ (6 GHz, normal window) gives plateaux of +0.2000, +0.0080 and +0.00032, matching the lattice sums. Ghosts repeat at the section's round-trip spacing and fall by $\rho^2$ each time. That is how to tell them from real faults. [Layer peeling](#level-3--what-distorts-a-tdr) is this bookkeeping run backwards.

### Level 3 — what distorts a TDR
- **Multiple reflections and masking**: after a large discontinuity, less energy reaches later ones (the transmitted fraction is $1-\rho^2$ per crossing each way), and re-reflections create false features. First-order "impedance profiles" become wrong after large steps; *layer-peeling* algorithms invert the profile exactly for lossless lines. Keysight calls the amplitude error "masking" [1].
- **Loss**: cable attenuation (∝ √f) slows the returning edge and makes a matched lossy line look like a slowly rising impedance ("upward slope" on long cables), because $Z_0$ of a lossy line and its reference differ, and because the high-frequency content is attenuated.
- **Rise time from the source + the cable**: the effective rise time is roughly the root-sum-square of the instrument rise time and the dispersion-induced rise time.
- **Band-pass mode** (no harmonic grid, no DC) works for band-limited devices (antennas, waveguide, filters) and shows only $|h(t)|$ — no sign/shape information.
- **Gating**: select a time window around a response, transform back to frequency, and you have the S-parameters "as if" only that part existed — e.g. an antenna's return loss without the connector/cable reflections. Gates have their own transition width and edge effects (Keysight: renormalisation, gate shapes) [1]; gating cannot remove re-reflections that overlap in time.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $Z=Z_0(1+\rho)/(1-\rho)$ | first discontinuity, lossless | ρ = +0.2 → 75 Ω |
| $d=v_pt/2$ | reflection | VF 0.66: 9.9 cm/ns |
| $L=2Z_0\int\rho\,dt$; $C=-\frac2{Z_0}\int\rho\,dt$ | small lumped L / C | 1 pF ≈ −25 ps·(ρ) area |
| $t_r\approx(0.45\ldots1.48)/F$; $w_{50}\approx(0.6\ldots1.4)/F$ | VNA low-pass, min…max window | 3 GHz normal: 330 ps |
| $\Delta d\approx w_{50}v_p/2$ (×1.25 for 3 dB dip) | equal events | 3 GHz, VF 0.66: 32–40 mm |
| $d_\text{max}=v_p/(2\Delta f)$ | alias-free | 101 pts, 900 MHz: 11 m |
| Band-pass width = 2 × low-pass | fault location | — |
| $v_1=V_sZ_0/(R_s+Z_0)$; ring ratio $\Gamma_S\Gamma_L$ per 2T | resistive lattice | 10 Ω into open: 1.667, 0.556, 1.296 … V |
| load ≡ $2v_i(t)$ behind $Z_0$ | any load, reactive included | C: τ = Z0C; L: τ = L/Z0 |
| masking: next step × (1 − ρ²); ghost ∝ ρ³ | TDR after a discontinuity | 75 Ω in 50 Ω: −0.192, ghost −0.0077 |

## Worked examples

### Example 1 — find a crushed spot in a 10 m ground-station feeder (LMR-400, VF 0.85)
NanoVNA-H (up to 900 MHz shown here), 101 points: $\Delta f=9$ MHz → alias-free range $0.85c/(2\times9\text{ MHz})=14.2$ m — enough for 10 m. Normal-window resolution: $0.98/900\text{ MHz}\times0.85c/2=14$ cm. A crushed/kinked section (locally lower Z) appears as a negative dip; a water-logged connector as a capacitive dip or resistive step; a bad solder joint (series R/L) as a positive bump. If the cable were 30 m you would need ≥ 201 points or a narrower span (band-pass mode is fine for *locating* faults).

### Example 2 — sizing a pad capacitance at a U.FL launch
A 6 GHz-capable VNA (LibreVNA/LiteVNA class) on a board with an SMA → 50 Ω CPWG → U.FL: the U.FL pad shows a negative dip with area −12 ps (ρ·s). $C=-\frac{2}{50}\times(-12\text{ ps})=0.48$ pF of excess capacitance — at 2.4 GHz $\omega CZ_0=0.36$ and $|\Gamma|=\omega CZ_0/\sqrt{4+(\omega CZ_0)^2}=0.18$, i.e. RL ≈ 15 dB from the pad alone (at 433 MHz it would be RL ≈ 30 dB — harmless). Fix: a ground cut-out under the pad or a narrower pad (layout → [connectors & launches](../13-pcb-rf-layout-emc/connectors-and-launches.md)). Resolution at 6 GHz span ≈ 1.6 cm in VF 0.66 — the pad and the connector merge; the *area* still sizes the total excess C.

### Example 3 — checking a JLCPCB impedance coupon
Measured low-pass step with a 75 mm, nominally 50 Ω CPWG coupon: plateau ρ = −0.03 → $Z=50\times0.97/1.03=47.1$ Ω — consistent with the soldermask-lowered value predicted on the [planar-lines page](planar-lines-microstrip-stripline-cpwg.md) (≈ 47 Ω). The plateau must be read ≥ one rise-time distance away from the launch: with a 6 GHz span, normal window, $t_r=165$ ps ≈ 1.5 cm of line (one way, εeff 2.65) — a 75 mm coupon is long enough.

### Example 4 — a 3.3 V logic edge into a 5 pF input at the end of a 150 mm trace
JLC 2-layer 50 Ω microstrip, εeff 3.40, 150 mm: T = 0.150 × √3.40 / c = **0.923 ns**. Edge 0.5 ns (≫ the lumped limit tr/6 = 83 ps → it is a transmission line). Driver Rs = 15 Ω: v1 = 3.3 × 50/65 = 2.54 V, ΓS = −0.54. The 5 pF input charges with τ = Z0C = 250 ps < tr, so it looks nearly open and the first arrival almost doubles: the lattice/FDTD/IFFT peak is **5.41 V (+64 %)**, and the ringing (period ≈ 4T ≈ 3.7 ns) settles within 5 % only after **12.3 ns**. Add a 35 Ω series resistor (Rs = Z0): the launched wave is 1.65 V, the load doubles it to 3.30 V with **no overshoot**, settled by **1.9 ns**. The source end then sits at 1.65 V for 2T, so do not hang a second load mid-line. A real CMOS input clamps through its ESD diodes above VDD + ~0.5 V, injecting current instead of reaching 5.4 V, which is not better. Termination strategy and multi-drop rules: [digital termination](../13-pcb-rf-layout-emc/digital-termination-and-crosstalk.md).

### Example 5 — reading a NanoVNA TDR of a feeder with a 75 Ω patch cable in it
A ground-station feeder has 1 m of 50 Ω cable, a 0.5 m 75 Ω TV patch lead (VF 0.66) and more 50 Ω cable. The low-pass step shows +0.20 (75 Ω) for 2T2 = 5.1 ns, then drops by 0.192 to +0.008, and a −0.0077 ghost follows 5.1 ns later. The ghost is not a second fault: it is the wave trapped in the 75 Ω section, and it repeats at 5.1 ns spacing, 28 dB (a factor ρ² = 0.04) weaker each time. Replace the 75 Ω lead: in the frequency domain the two ends' reflections add with a phase set by the section's length, giving RL between ∞ and 8.3 dB (|Γ| = 0.385 at a quarter-wave). At 433.92 MHz this 0.5 m lead is 395° long and gives |Γ| = 0.23, **RL 12.7 dB**, on its own ([reflections](reflections-vswr-return-loss-mismatch.md)).

## Practical notes
- **Calibrate first** (SOL at the reference plane); the time-domain display inherits all calibration errors. Set the VNA's velocity factor so the distance axis is right.
- **Use low-pass mode for impedance profiling** (requires the harmonic grid; NanoVNA-Saver/NanoVNA-App and LibreVNA provide TDR views); use band-pass for fault location in band-limited systems.
- **Don't over-interpret small wiggles**: sidelobes of the window (−13 dB for minimum!) around a big reflection look like extra discontinuities.
- **Loss-induced slope**: on long thin cables (RG-174, U.FL micro-coax) the matched trace rises with distance; compare with a known-good cable of the same type.
- **A real TDR scope** (step generator + sampler; e.g. 35–150 ps edges) gives time-domain data directly with no aliasing issue; VNAs have better dynamic range. For the hobby lab, a NanoVNA/LibreVNA is the practical choice ([lab setup](../17-test-measurement/lab-setup-by-budget.md)).

## Common mistakes & misconceptions
- **Forgetting the factor 2** (round trip) or the velocity factor in distance.
- **Reading the plateau of a short section** — if the section is shorter than the rise-time distance, it never reaches its true impedance.
- **Interpreting aliases** as real faults when the cable is longer than $v_p/(2\Delta f)$.
- **Expecting more resolution from more points**: points extend *range*; only *span* (and window) sets resolution.
- **Using band-pass mode for impedance**: it gives $|h|$ only; the sign (capacitive vs inductive) is lost.
- **Gating as magic**: it removes responses separated in time, not overlapping ones; gate edges distort the band edges.
- **Using the source-side divider $R_L/(R_s+R_L)$ for the first wave.** The first wave sees $Z_0$, not the load: $v_1=V_sZ_0/(R_s+Z_0)$. The DC divider is only the final value.
- **Treating a capacitive load as "high impedance, so no reflection".** For times short compared with Z0C a capacitor is a short (ΓL = −1), and later an open (+1): a small C at the end of a line still makes the edge overshoot.
- **Reading a ghost as a second fault.** Re-reflections inside a section come back at that section's round-trip spacing, scaled by ρ² each time.
- **Taking the second step's height at face value.** After a discontinuity of ρ, later steps are masked by (1 − ρ²) (plus loss).

## How to simulate / verify
- `tools/verify/tline_tdr.py` — low-pass transform with Hermitian extension and DC extrapolation; window constants vs Keysight AN 1287-12; alias-free range; L and C discontinuity signatures and area rule; 75 Ω section impedance profile; two-event resolution vs span; scikit-rf `step_response` cross-check. All pass.
- `tools/verify/s5_tdr_lattice.py` (≈ 5 s, W5-S5, 15/15): lattice vs FDTD vs ABCD/IFFT for resistive, C, L, RC and series-LR terminations; closed-form reactive reflections; series-L bump area; the 3.3 V / 150 mm / 5 pF SI example with and without series termination; 75 Ω-section masking and ghost amplitudes vs an IFFT of S11.
- scikit-rf built-ins:

```python
import skrf as rf
n = rf.Network('cable.s1p')                       # harmonic grid f_n = n*df recommended
t, rho = n.s11.step_response(window='hamming')    # low-pass step (skrf extrapolates DC)
z = 50 * (1 + rho) / (1 - rho)                    # impedance profile
d = t * 0.66 * 299792458 / 2                       # distance axis for VF 0.66
g = n.s11.time_gate(center=2, span=0.5, t_unit='ns') # gate a 0.5 ns window around 2 ns
```

## Open questions / gaps
- Layer-peeling inversion and loss compensation are described but not implemented.
- NanoVNA-specific TDR implementation details (window defaults, DC extrapolation) not verified against the firmware source.

## Sources
1. Keysight Technologies, *Time Domain Analysis Using a Network Analyzer*, Application Note 1287-12, pub. 5989-5723EN (2012 rev.) — http://literature.cdn.keysight.com/litweb/pdf/5989-5723EN.pdf — low-pass/band-pass modes, Table 1-2/1-3 window constants, alias-free range, gating, masking. (app note)
2. Keysight Technologies, *Techniques for Time Domain Measurements (FieldFox)*, Application Note 5991-0420EN, 2014 — band-pass fault location. (app note)
3. D. M. Pozar, *Microwave Engineering*, 4th ed., 2012 — §2.3/2.6 (reflections), Point of Interest on TDR. (textbook)
4. Tektronix, *TDR Impedance Measurements: A Foundation for Signal Integrity* (app note 55W-14601) — step shapes of L/C discontinuities. (app note; general knowledge, not re-fetched this session)
5. A. V. Oppenheim and R. W. Schafer, *Discrete-Time Signal Processing*, 3rd ed., Pearson 2010 — Kaiser window β vs sidelobe level. (textbook)
6. scikit-rf 2.0.1 documentation — `Network.step_response`, `time_gate`. (software documentation)
7. Verification: `tools/verify/tline_tdr.py`, `tools/verify/s5_tdr_lattice.py`. (numerical check)
8. L. Bergeron, *Water Hammer in Hydraulics and Wave Surges in Electricity*, Wiley 1961 — the graphical (characteristic) method behind lattice diagrams, including non-linear ends. (textbook; cited from knowledge)
9. H. W. Johnson, M. Graham, *High-Speed Digital Design: A Handbook of Black Magic*, Prentice Hall 1993, ch. 4 (transmission lines, reflections, ringing) and ch. 6 (terminations). (textbook; chapter numbers checked against the publisher table of contents (sigcon.com HSDD ToC, W5-S18/S18b 2026-10-13); content cited from knowledge)
10. C. R. Paul, *Analysis of Multiconductor Transmission Lines*, 2nd ed., Wiley/IEEE 2008, ch. 4–5 (lossless-line time-domain solutions, lattice method, FDTD of the telegrapher equations with resistive and reactive terminations). (textbook; used for the FDTD termination scheme)
