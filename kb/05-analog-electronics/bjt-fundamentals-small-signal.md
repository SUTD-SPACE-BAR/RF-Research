---
title: BJT fundamentals and small-signal models (gm, hybrid-π, fT, fmax, noise, SiGe HBT)
domain: 05-analog-electronics
slug: bjt-fundamentals-small-signal
tags: [bjt, transconductance, hybrid-pi, early-effect, ebers-moll, ft, fmax, miller-effect, bias-stability, shot-noise, base-resistance, sige-hbt, rf-transistor]
prerequisites:
  - diodes-schottky-pin-varactor.md
  - ../01-circuit-theory/two-port-networks-zyh-abcd.md
related:
  - fets-mosfet-jfet-gaas-gan.md
  - amplifier-topologies.md
  - feedback-and-stability.md
  - low-noise-analog-design.md
  - ../06-rf-circuits/lna-design.md
  - ../06-rf-circuits/amplifier-stability-and-biasing.md
  - ../07-noise-linearity/noise-figure-and-friis.md
  - ../07-noise-linearity/shot-and-flicker-noise.md
  - ../03-transmission-lines-matching/s-parameters.md
level: mixed
confidence: high
last_updated: 2026-10-12
---

# BJT fundamentals and small-signal models (gm, hybrid-π, fT, fmax, noise, SiGe HBT)

## Questions this page answers
- Why is $V_{BE}$ "about 0.6–0.7 V", and how much does it change with current?
- What is the difference between $f_\beta$, $f_\alpha$ and $f_T$?
- How do BJTs fail?
- Why is a BJT's transconductance exactly $I_C/V_T$, whatever the transistor?
- What are $r_\pi$, $r_e$, $r_o$ and the Early voltage, and how do I get them from the bias point?
- What do $f_T$ and $f_{max}$ really mean, and why is $f_T$ not "the highest frequency the transistor works at"?
- Why does a common-emitter stage's bandwidth collapse when its gain is high (Miller effect)?
- Why should I never design a bias circuit that depends on β?
- What sets a BJT's noise, what is the optimum source resistance, and why are RF LNA transistors run at several mA?
- What's special about SiGe HBTs and why are they used for LNAs up to tens of GHz?
- Why is $BV_{CEO}$ so much lower than $BV_{CBO}$, and why do RF transistors die from 1–2 V of reverse base-emitter voltage?
- How does saturation work, and what sets $V_{CE(sat)}$?

## TL;DR
- In forward-active mode $I_C = I_Se^{V_{BE}/V_T}(1+V_{CE}/V_A)$. Consequences, valid for *every* BJT: $g_m = I_C/V_T$ (38.7 mS at 1 mA, 300 K), $r_\pi = \beta/g_m$, $r_e \approx 1/g_m$ (26 Ω at 1 mA), $r_o = V_A/I_C$, intrinsic gain $g_mr_o = V_A/V_T$ (≈ 2900 = 69 dB for $V_A$ = 75 V). Verified in `tools/verify/analog_bjt.py`.
- Hybrid-π: $r_b$ (base spreading resistance) → node b′; $r_\pi$ ∥ $C_\pi$ from b′ to e; $C_\mu$ from b′ to c; $g_mv_{\pi}$ and $r_o$ from c to e. $C_\pi = g_m\tau_F + C_{je}$.
- **$f_T$** = frequency where short-circuit current gain $|h_{21}| = 1$: $1/(2\pi f_T) = \tau_F + (C_{je}+C_\mu)/g_m$ (+ parasitic terms). Rises with $I_C$, peaks, then falls (Kirk effect). $|h_{21}| \approx f_T/f$ above $f_T/\beta$. Hand vs ngspice: 473 vs 477 MHz (script §3).
- **$f_{max}$** = frequency where *power* gain (Mason's U) = 1: $f_{max} \approx \sqrt{f_T/(8\pi r_bC_\mu)}$. Hand formula vs exact U: 70.8 vs 70.1 GHz for a SiGe-like model (script §4). Low $r_b$ and $C_\mu$ matter as much as $f_T$.
- **Miller:** $C_\mu$ appears at the input multiplied by $(1+g_mR_L')$ — a 2 pF $C_\mu$ with gain −194 looks like ~400 pF (script §5). Cascode or low-impedance loads fix it.
- **Bias:** β varies 2–4× between parts and with temperature; $I_C$ at fixed $V_{BE}$ rises ~7–8 %/K. Set $I_C$ with emitter degeneration and a stiff divider: β 100→400 moved $I_C$ only 1.01→1.10 mA vs 0.53→2.12 mA with a single base resistor (script §6).
- **Noise:** base shot noise $2qI_B$, collector shot noise $2qI_C$, $r_b$ thermal noise $4kTr_b$. Low-frequency optimum: $F_{min} = 1 + \sqrt{(1+2g_mr_b)/\beta}$, $R_{opt} = \sqrt{\beta(1+2g_mr_b)}/g_m$. For a fixed source $R_s$ the best current is $I_C \approx V_T\sqrt\beta/R_s$ — ≈ 5–8 mA for 50 Ω, matching the 6 mA at which the BFP740 is noise-specified [1].
- **SiGe HBT:** graded Ge base → built-in drift field (short $\tau_F$) and higher β, traded for heavier base doping (low $r_b$) → higher $f_T$, $f_{max}$, lower NF. Discrete example BFP740: $f_T$ = 44 GHz, $C_{CB}$ = 0.08 pF, NF$_{min}$ 0.45 dB at 450–900 MHz, $V_{CEO}$ 4 V, $V_{EBO}$ only 1.2 V [1]. IC processes reach $f_T/f_{max}$ = 300/500 GHz [2].

- **Primer:** $V_{BE} = V_T\ln(I_C/I_S)$ = 0.65 V at 1 mA for $I_S = 10^{-14}$ A (0.71 V for 10⁻¹⁵), +59 mV per decade of current. $f_\beta = f_T/\beta_0$, and $f_\alpha$ ≈ $f_T$. ngspice for the 2N3904-like model at 5.3 mA: $f_\beta$ 2.25 MHz, $f_T$ 477 MHz, $f_\alpha$ 500 MHz (`tools/verify/s3_primer.py` §3).

## Intuition (no math)
A BJT is a forward-biased base-emitter diode whose injected electrons (NPN) mostly *miss* the base contact: the base is so thin that almost all of them diffuse across it and get swept into the collector by the reverse-biased collector junction. The collector just collects; the current is set by the base-emitter voltage through the same exponential as a diode. The small base current is the fraction of carriers that recombine in the base or are back-injected into the emitter — the ratio of the two is β, a messy manufacturing parameter.

Because the collector current is an exponential of $V_{BE}$, the slope ("how many mA per mV") is proportional to the current itself: at 1 mA, each extra millivolt adds ~39 µA. This is why $g_m = I_C/V_T$ is universal — it depends on physics, not on the transistor's size or process. It is also why a BJT gives more transconductance per mA than any FET.

To make the collector current change, you must change the charge stored in the base (the diffusion "cloud" of electrons crossing it). Supplying that charge takes base current; at high frequency the base current needed to wiggle the charge grows until it equals the collector current — that frequency is $f_T$. Above it, the device still gives *power* gain for a while (a high-impedance output driven by a lower-impedance input), until the base resistance and feedback capacitance eat it; that limit is $f_{max}$.

The collector-base capacitance $C_\mu$ is a bridge from output to input. When the stage has voltage gain −A, the output side of $C_\mu$ swings A times the input in the opposite direction, so the input must supply A+1 times the charge — the capacitor looks (A+1) times bigger. That is the Miller effect.

## The math

### Level 0 — $V_{BE}$, $f_\beta$, $f_\alpha$, $f_T$ and how BJTs fail
*Day-one level; the rest of the page derives these properly.*

**Why "0.6–0.7 V".** The base-emitter junction is a diode, and $I_C = I_Se^{V_{BE}/V_T}$. Small-signal transistors have $I_S$ ≈ 10⁻¹⁵–10⁻¹⁴ A, so at 1 mA $V_{BE} = V_T\ln(I_C/I_S)$ is 0.65–0.71 V at 25 °C (script §3). Each ×10 in current adds only 59 mV, so "0.65 V" works for hand bias design over µA–10 mA. Power transistors at amps sit at 0.8–1.2 V once their internal resistances add. $V_{BE}$ falls ≈ 2 mV/K (Level 2). An NPN in forward-active mode needs $V_{BE}$ ≈ 0.65 V *and* $V_{CE}$ ≳ 0.2–0.3 V. Below that it saturates.

**Three cut-off frequencies.**
- **$f_\beta$**: the common-emitter current gain $\beta(f)$ is 3 dB below its low-frequency value $\beta_0$. Above it β falls 20 dB/decade.
- **$f_T$**: where that falling |β| reaches 1, so $f_T \approx \beta_0f_\beta$ (the gain–bandwidth product of the current gain).
- **$f_\alpha$**: the common-base current gain $\alpha = I_C/I_E$ (≈ 0.99) is 3 dB down. In the single-pole picture $f_\alpha = (\beta_0+1)f_\beta \approx f_T$. Real devices put it a little above $f_T$ because of the depletion-capacitance and $C_\mu$ terms.

ngspice on the 2N3904-like model of this page ($I_C$ = 5.3 mA, $\beta_0$ = 211): $f_\beta$ = 2.25 MHz, $f_T$ = 477 MHz (= 211 × 2.25 MHz), $f_\alpha$ = 500 MHz = 1.05 $f_T$. Older datasheets quote $f_\alpha$ or $f_{hfe}$ (= $f_\beta$); modern ones quote $f_T$ at a stated $I_C$ and $V_{CE}$. This is why a common-base stage stays wideband: its current gain holds to ≈ $f_T$, whereas the common-emitter current gain is down 3 dB at $f_T/\beta$.

**How BJTs fail.**
1. **Over-voltage.** The collector-emitter limit is $V_{CEO}$ with the base open, much lower than $V_{CBO}$ (Level 3). Inductive loads and PA collector swings of 2 $V_{CC}$ exceed it.
2. **Reverse base-emitter breakdown** at 1–7 V permanently lowers β and raises noise.
3. **Thermal runaway.** At fixed $V_{BE}$, $I_C$ rises ≈ 7 %/K. More heat gives more current, which gives more heat (Level 2, Bias stability).
4. **Second breakdown.** At high $V_{CE}$ and current, current crowds into a hot spot and the device fails *inside* the $P_{max}$ hyperbola. Stay inside the datasheet safe-operating-area (SOA) curves for the pulse length.
5. **ESD and RF overdrive** of small-geometry RF/SiGe parts.
6. **Exceeding $T_J$** (often 150 °C): $T_J = T_A + P\theta_{JA}$, and SOT-23 is ≈ 300–500 K/W (Practical notes).

### Level 1 — the working model

**Forward-active large-signal model** (NPN, $V_{BE} > 0$, $V_{BC} < 0$):
$$I_C = I_Se^{V_{BE}/V_T}\left(1+\frac{V_{CE}}{V_A}\right),\qquad I_B = \frac{I_C}{\beta},\qquad I_E = I_C + I_B = \frac{I_C}{\alpha},\quad \alpha = \frac{\beta}{\beta+1}$$
$I_S$ saturation current (A; 10⁻¹⁶–10⁻¹³ for small-signal devices), $V_T = kT/q$, $V_A$ Early voltage (V; 20–150 V discretes, a few V to tens for RF/IC devices), β = $h_{FE}$ (50–500, spread 2–4× within one part number).

**Small-signal parameters at bias $I_C$** (derivatives of the model):

| Parameter | Formula | Value at 1 mA, β = 200, $V_A$ = 75 V, 300 K |
|---|---|---|
| Transconductance | $g_m = \partial I_C/\partial V_{BE} = I_C/V_T$ | 38.7 mS |
| Input resistance (base) | $r_\pi = \beta/g_m$ | 5.17 kΩ |
| Emitter resistance | $r_e = \alpha/g_m \approx 1/g_m$ | 25.9 Ω |
| Output resistance | $r_o = V_A/I_C$ | 75 kΩ |
| Intrinsic gain | $g_mr_o = V_A/V_T$ | 2900 (69 dB), independent of $I_C$ |

**Hybrid-π with capacitances.** Base terminal → $r_b$ → internal node b′. Between b′ and e: $r_\pi$ ∥ $C_\pi$, with $C_\pi = g_m\tau_F + C_{je}$ (diffusion + depletion). Between b′ and c: $C_\mu$ (collector-base depletion, the "$C_{ob}$" or $C_{CB}$ of datasheets). Output: $g_mv_{b'e}$ ∥ $r_o$ (∥ $C_{cs}$ to substrate in ICs).

**Transition frequency** (short-circuit current gain = 1):
$$h_{21}(j\omega) = \frac{g_m - j\omega C_\mu}{1/r_\pi + j\omega(C_\pi+C_\mu)}\ \ \Rightarrow\ \ f_T \approx \frac{g_m}{2\pi(C_\pi+C_\mu)},\quad \frac{1}{2\pi f_T} = \tau_F + \frac{C_{je}+C_\mu}{g_m}$$
Above the β corner $f_\beta = f_T/\beta$, $|h_{21}| \approx f_T/f$ (a −20 dB/decade slope; "gain-bandwidth product").

**Maximum oscillation frequency** (unilateral power gain U = 1):
$$f_{max} \approx \sqrt{\frac{f_T}{8\pi r_bC_\mu}}$$

**Miller input capacitance** of a common-emitter stage with total load $R_L'$ at the collector:
$$C_{in} = C_\pi + C_\mu(1+g_mR_L')$$

### Level 2 — derivations

**Why $g_m = I_C/V_T$.** Differentiate $I_C = I_Se^{V_{BE}/V_T}$: $dI_C/dV_{BE} = I_C/V_T$. No geometry, doping or process appears. For a MOSFET in strong inversion $g_m = 2I_D/V_{ov}$ with $V_{ov}$ typically 0.1–0.3 V, i.e. 4–12× less $g_m$ per ampere than a BJT's $1/V_T$ (→ [FETs](fets-mosfet-jfet-gaas-gan.md), $g_m/I_D$ methodology).

**Early effect.** Raising $V_{CB}$ widens the collector-base depletion layer into the base, narrowing the neutral base width $W_B$. Collector current is a diffusion current $\propto n_i^2/(N_AW_B)$, so $I_C$ rises with $V_{CE}$. Extrapolating the output curves backwards they meet near $V_{CE} = -V_A$; linearising gives $r_o = V_A/I_C$. The same base-width modulation causes a small feedback conductance ($r_\mu \approx \beta r_o$), usually ignored.

**Ebers–Moll (transport form) and saturation.** With $e_f = e^{V_{BE}/V_T}-1$ and $e_r = e^{V_{BC}/V_T}-1$:
$$I_C = I_S(e_f - e_r) - \frac{I_S}{\beta_R}e_r,\qquad I_B = \frac{I_S}{\beta_F}e_f + \frac{I_S}{\beta_R}e_r$$
These are *linear* in $e_f, e_r$. When the base is overdriven (forced $\beta_{forced} = I_C/I_B < \beta_F$) both junctions are forward-biased, and solving the pair gives
$$V_{CE(sat)} = V_{BE}-V_{BC} = V_T\ln\frac{1+(\beta_{forced}+1)/\beta_R}{1-\beta_{forced}/\beta_F}$$
e.g. 35 mV at $\beta_{forced}$ = 10 and 102 mV at $\beta_{forced}$ = 100 ($\beta_F$ = 200, $\beta_R$ = 4) — confirmed by direct solution (script §2). Real $V_{CE(sat)}$ (0.1–0.3 V) is dominated by ohmic collector/emitter resistance. Saturated transistors store charge in the base and collector and are slow to turn off — why fast switches use Schottky clamps or avoid saturation.

**Deriving $f_T$.** Short the output (ac) and drive the base with current $i_b$. The internal voltage is $v_{b'e} = i_b/[1/r_\pi + j\omega(C_\pi+C_\mu)]$ and the output current $i_c = (g_m - j\omega C_\mu)v_{b'e}$. For $\omega C_\mu \ll g_m$ and $\omega(C_\pi+C_\mu) \gg 1/r_\pi$: $|i_c/i_b| \approx g_m/[\omega(C_\pi+C_\mu)]$, which equals 1 at $\omega_T = g_m/(C_\pi+C_\mu)$. Substituting $C_\pi = g_m\tau_F + C_{je}$ gives the $1/(2\pi f_T)$ sum above: at low current the depletion capacitances dominate ($f_T \propto I_C$); at moderate current $f_T \to 1/(2\pi\tau_F)$; at high current the base pushes out into the collector (**Kirk effect**), $\tau_F$ grows and $f_T$ falls. Datasheets plot $f_T$ vs $I_C$ — bias near but below the peak. Extra terms in real devices: $C_\mu(r_e+r_c)$ and collector depletion transit time.

**Deriving $f_{max}$ (sketch).** Mason's unilateral gain is the maximum power gain after lossless feedback neutralises $y_{12}$:
$$U = \frac{|y_{21}-y_{12}|^2}{4\left(\mathrm{Re}\,y_{11}\,\mathrm{Re}\,y_{22} - \mathrm{Re}\,y_{12}\,\mathrm{Re}\,y_{21}\right)}.$$
A physical shortcut gives the same answer. At $f \gg f_\beta$: (i) the only resistive part of the input is $r_b$ (the $C_\pi$ reactance is far below $r_\pi$), so a base current $i_b$ costs input power $|i_b|^2r_b$; (ii) the output current is $|h_{21}|i_b = (\omega_T/\omega)i_b$; (iii) a collector voltage $v_c$ couples through $C_\mu$ onto b′, where $C_\pi$ is the dominant impedance, giving $v_{b'e} \approx v_c C_\mu/C_\pi$ and an output current $g_mv_{b'e} = \omega_TC_\mu v_c$ in phase with $v_c$ — an output conductance $G_{out} \approx \omega_TC_\mu$. With a conjugate-matched load the output power is $|i_{out}|^2/(4G_{out})$, so
$$U \approx \frac{(\omega_T/\omega)^2|i_b|^2/(4\omega_TC_\mu)}{|i_b|^2r_b} = \frac{\omega_T}{4\omega^2r_bC_\mu} = \frac{f_T}{8\pi r_bC_\mu f^2},$$
falling 20 dB/decade and equal to 1 at the $f_{max}$ formula. The numerical U of the full hybrid-π (script §4) agrees within 1 %.

**Miller effect.** A capacitor $C$ between nodes with voltage gain $A_v = v_2/v_1$ draws $i = j\omega C(v_1 - v_2) = j\omega C(1-A_v)v_1$ from node 1 — an input capacitance $C(1-A_v)$. For a CE stage $A_v \approx -g_mR_L'$ → $C_\mu(1+g_mR_L')$. With $C_\mu$ = 2 pF, $g_m$ = 38.7 mS, $R_L'$ = 5 kΩ: $C_{in}$ = 10 + 2 × 194 = 399 pF, and with a 1 kΩ source the input pole is at 0.48 MHz — a transistor with $f_T$ of hundreds of MHz gives a sub-MHz amplifier (script §5; exact admittance agrees to 0.1 %). Cures: cascode (CB stage presents $r_e$ ≈ 26 Ω to the CE collector, so its gain ≈ −1), emitter follower driving, lower $R_L'$, or neutralisation. See [amplifier topologies](amplifier-topologies.md).

**Bias stability.** For a 4-resistor bias with Thevenin base drive $V_{Th}$, $R_{Th}$ and emitter resistor $R_E$:
$$I_C = \frac{\beta(V_{Th}-V_{BE})}{R_{Th}+(\beta+1)R_E}\ \xrightarrow{\ \beta R_E \gg R_{Th}\ }\ \frac{V_{Th}-V_{BE}}{R_E}.$$
Design: $V_{RE} \gtrsim$ 0.5–1 V (swamps $V_{BE}$ drift of −2 mV/K) and $R_{Th} \lesssim \beta_{min}R_E/10$. Sensitivity $\partial\ln I_C/\partial\ln\beta = R_{Th}/(R_{Th}+(\beta+1)R_E)$. At RF, emitter resistors are bypassed (or replaced by collector-to-base feedback bias, which self-regulates without an emitter capacitor whose inductance would degrade gain).

**Temperature.** At fixed $V_{BE}$, $d\ln I_C/dT = (E_g/q - V_{BE} + 3V_T)/(V_TT)$ ≈ 7 %/K at room temperature (script §1). A power stage biased by a fixed voltage can run away: more current → hotter → more current. Emitter ballast resistors and thermally-coupled bias diodes (or a $V_{BE}$ multiplier on the same heatsink) prevent it.

**Noise model and optimum source resistance.** Three uncorrelated (low-frequency) sources: base shot noise $\overline{i_b^2} = 2qI_B\Delta f$, collector shot noise $\overline{i_c^2} = 2qI_C\Delta f$, thermal noise of $r_b$: $\overline{v_{rb}^2} = 4kTr_b\Delta f$. Referring all to the input (→ [low-noise design](low-noise-analog-design.md) for the $e_n$–$i_n$ method):
$$e_n^2 = 4kT\left(r_b + \frac{1}{2g_m}\right),\qquad i_n^2 = 2qI_B = \frac{2kTg_m}{\beta}\qquad [\text{per Hz}]$$
(the $1/2g_m$ term is collector shot noise divided by $g_m^2$: $2qI_C/g_m^2 = 2kT/g_m$). With a source $R_s$ at temperature T, $F = 1 + (e_n^2 + i_n^2R_s^2)/(4kTR_s)$, minimised at
$$R_{opt} = \frac{e_n}{i_n} = \frac{\sqrt{\beta(1+2g_mr_b)}}{g_m},\qquad F_{min} = 1 + \frac{e_ni_n}{2kT} = 1+\sqrt{\frac{1+2g_mr_b}{\beta}}.$$
Expanding for a *given* $R_s$: $F = 1 + r_b/R_s + 1/(2g_mR_s) + g_mR_s/(2\beta)$, minimised over current at $g_m = \sqrt\beta/R_s$, i.e.
$$I_{C,opt} = \frac{V_T\sqrt\beta}{R_s},\qquad F = 1+\frac{r_b}{R_s}+\frac{1}{\sqrt\beta}.$$
For $R_s$ = 50 Ω, β = 250: $I_{C,opt}$ = 8.2 mA; $F$ = 0.66 dB with $r_b$ = 5 Ω. For a 10 kΩ sensor source: 37 µA (script §7). This is why RF LNAs run at mA and low-noise audio/sensor preamps at tens of µA, and why $r_b$ dominates at 50 Ω (0.29 nV/√Hz for 5 Ω vs 0.91 for 50 Ω).

### Level 3 — high-frequency, breakdown and technology limits
- **Frequency-dependent noise.** Above $f_T/\sqrt\beta$ the collector shot noise referred to the input grows as $(f/f_T)^2$ (because $|h_{21}|$ falls) and becomes correlated with $e_n$; NF$_{min}$ rises with $f/f_T$ and the optimum source becomes complex ($\Gamma_{opt}$). Use the datasheet's four noise parameters (NF$_{min}$, $\Gamma_{opt}$, $R_n$) — see [LNA design](../06-rf-circuits/lna-design.md) and [noise figure](../07-noise-linearity/noise-figure-and-friis.md). Rule: pick a device with $f_T$ ≥ 10–20× the operating frequency for low NF.
- **Flicker noise.** BJTs have much lower 1/f noise than MOSFETs (surface traps are away from the current path), with corners from ~10 Hz to ~1 kHz; this is one reason bipolar/SiGe oscillators have better close-in phase noise (→ [oscillators](oscillators.md), [shot & flicker noise](../07-noise-linearity/shot-and-flicker-noise.md)).
- **Breakdown.** $BV_{CBO}$ is avalanche of the collector-base junction. With the base open, avalanche-generated holes act as base current and are multiplied by β, so breakdown occurs when $M = 1+1/\beta$: $BV_{CEO} \approx BV_{CBO}/\beta^{1/n}$ ($n$ ≈ 3–6). BFP740: $V_{CBO}$ = 13 V but $V_{CEO}$ = 4 V [1]. A low base-drive impedance raises the usable $V_{CE}$ toward $BV_{CES}$ — relevant for PA stages whose collectors swing to 2× supply.
- **Reverse base-emitter stress.** Emitter-base junctions are heavily doped and break down at ~5–7 V in general-purpose parts but only ~1–2 V in RF/SiGe parts (BFP740: 1.2 V [1]). Reverse EB avalanche (even ESD or a large RF input swing on an unbiased stage) creates hot-carrier damage that permanently lowers β and raises noise. Protect LNA inputs.
- **SiGe HBT physics.** Grading Ge across the base narrows the bandgap toward the collector, creating a built-in field that accelerates carriers (shorter $\tau_F$). The reduced bandgap at the emitter end raises $I_S$ and β, which the designer spends on heavier base doping → lower $r_b$ and less Early effect/punch-through. Result: higher $f_T$ *and* $f_{max}$ and lower NF at the same lithography, while keeping silicon manufacturing [3]. Production SiGe BiCMOS reaches $f_T/f_{max}$ = 300/500 GHz (IHP SG13G2 [2]), enabling 77 GHz radar and D-band transceivers (→ [radar hardware](../11-radar/diy-radar-hardware.md)).
- **Where BJTs sit vs other devices** (→ [FETs page](fets-mosfet-jfet-gaas-gan.md) for the selection table): SiGe HBTs win on 1/f noise, $g_m$/mA, matching and oscillator phase noise; GaAs pHEMTs win on NF at 1–20 GHz; GaN/LDMOS win on power; Si BJTs are still good, cheap building blocks to ~2 GHz.

## Design equations & rules of thumb

| Quantity | Equation | Valid when | Typical |
|---|---|---|---|
| Transconductance | $g_m = I_C/V_T$ | forward active | 38.7 mS/mA (300 K) |
| Input resistance | $r_\pi = \beta/g_m$ | low frequency | 5 kΩ @ 1 mA, β = 200 |
| Output resistance | $r_o = V_A/I_C$ | — | 75 kΩ @ 1 mA, $V_A$ = 75 V |
| Intrinsic gain | $g_mr_o = V_A/V_T$ | — | 1000–6000 |
| $V_{BE}$ tempco | ≈ −2 mV/K | fixed $I_C$ | −1.8 to −2.2 |
| $I_C$ tempco at fixed $V_{BE}$ | ≈ +7–8 %/K | — | thermal runaway risk |
| Emitter-degenerated $G_m$ | $g_m/(1+g_mR_E)$ | — | ≈ $1/R_E$ if $g_mR_E \gg 1$ |
| Transition frequency | $1/(2\pi f_T) = \tau_F+(C_{je}+C_\mu)/g_m$ | — | 300 MHz (2N3904) … 44 GHz (BFP740 [1]) |
| $\beta(f)$ | $\approx f_T/f$ | $f > f_T/\beta$ | — |
| $V_{BE}$ | $V_T\ln(I_C/I_S)$ | forward active | 0.65 V @ 1 mA ($I_S$ = 10⁻¹⁴ A) |
| $f_\beta$, $f_\alpha$ | $f_\beta = f_T/\beta_0$; $f_\alpha \approx f_T$ | — | 2.25 MHz / 500 MHz for $f_T$ 477 MHz |
| Max oscillation freq. | $\sqrt{f_T/(8\pi r_bC_\mu)}$ | $f \gg f_\beta$ | — |
| Miller capacitance | $C_\mu(1+g_mR_L')$ | CE stage | ×10–×1000 |
| Stiff bias | $R_{Th} \le \beta_{min}R_E/10$, $V_{RE} \ge 0.5$–1 V | — | — |
| $F_{min}$ (LF) | $1+\sqrt{(1+2g_mr_b)/\beta}$ | $f \ll f_T/\sqrt\beta$ | 0.3–1 dB |
| Noise-optimal current | $I_C = V_T\sqrt\beta/R_s$ | LF | ~5–8 mA @ 50 Ω |
| $r_b$ noise | $\sqrt{4kTr_b}$ | — | 0.29 nV/√Hz @ 5 Ω |
| Open-base breakdown | $BV_{CEO} \approx BV_{CBO}/\beta^{1/n}$ | — | 13 V → 4 V (BFP740) |

## Worked examples

### 1. A 2N3904-class common-emitter stage — gain and bandwidth
Bias $I_C$ = 1 mA from a 5 V rail using the 4-resistor network $R_1$ = 22 kΩ, $R_2$ = 6.8 kΩ, $R_C$ = 1.5 kΩ, $R_E$ = 470 Ω (bypassed at signal frequencies). $V_{Th}$ = 1.18 V, $R_{Th}$ = 5.19 kΩ.
- β = 100 → 1.007 mA; β = 200 → 1.065 mA; β = 400 → 1.096 mA (script §6). With only an 820 kΩ base resistor, the same β spread gives 0.53–2.12 mA — the collector would saturate at β = 400 ($I_CR_C$ = 3.2 V plus $V_{RE}$).
- Small signal at 1.065 mA: $g_m$ = 41 mS, $r_\pi$ = 4.9 kΩ (β = 200). Voltage gain (bypassed, $R_L' = R_C$ ∥ $r_o$ ≈ 1.47 kΩ): $A_v = -g_mR_L' \approx -60$.
- Unbypassed emitter: $A_v \approx -R_C/(r_e+R_E) = -1500/(24+470) = -3.0$, but now stable against β and temperature and far more linear (→ [amplifier topologies](amplifier-topologies.md)).
- Miller: with $C_\mu$ ≈ 3 pF, $C_\pi$ ≈ 20 pF, the bypassed stage's $C_{in}$ ≈ 20 + 3 × 61 ≈ 200 pF; with a 600 Ω source ∥ $r_\pi$ ∥ $R_{Th}$ ≈ 470 Ω the input pole is ≈ 1.7 MHz — two decades below the device's $f_T$.

### 2. Choosing the current for a discrete 433/915 MHz SiGe LNA stage
Device: BFP740 ($f_T$ 44 GHz at 25 mA, $h_{FE}$ ≈ 250, NF$_{min}$ 0.45 dB at 450 and 900 MHz at 6 mA, $G_{ms}$ 31.5 dB at 450 MHz, OIP3 22 dBm at 15 mA [1]).
- Low-frequency optimum for a 50 Ω source: $I_{C,opt} = V_T\sqrt\beta/R_s = 25.9\ \text{mV}\times15.8/50 = 8.2$ mA — consistent with the 6 mA noise-test current in the datasheet (the true optimum is shifted by frequency-dependent noise and correlation).
- At 433 MHz, $|h_{21}| \approx f_T/f$ ≈ 100 at the $f_T$-peak bias: the device is operating at 1 % of $f_T$ → noise near its LF limit and a lot of excess gain, so unconditional stability needs resistive loading or feedback (→ [amplifier stability](../06-rf-circuits/amplifier-stability-and-biasing.md)).
- Trade-off: 6 mA for best NF vs 15 mA for OIP3 22 dBm — decide from the link's blocking environment (a rocket ground station next to other ISM users vs a quiet field) (→ [dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)).
- Protect $V_{EBO}$ = 1.2 V: a strong nearby transmitter or ESD on the antenna can reverse-bias the EB junction; use a limiter/ESD element ahead of the LNA (→ [diodes](diodes-schottky-pin-varactor.md) example 4).

### 3. $f_{max}$ of a SiGe-like device
Model: $I_C$ = 15 mA, β = 250, $\tau_F$ = 2.5 ps, $C_{je}$ = 0.3 pF, $C_\mu$ = 0.08 pF, $r_b$ = 5 Ω. $g_m$ = 0.58 S, $C_\pi$ = 1.75 pF, $f_T$ = 50.4 GHz. Hand: $f_{max} = \sqrt{50.4\times10^9/(8\pi\cdot5\cdot0.08\times10^{-12})} = 70.8$ GHz; exact Mason U = 1 at 70.1 GHz (script §4). Halving $r_b$ raises $f_{max}$ by √2 without touching $f_T$.

## Practical notes
- **Part tiers:** general purpose (2N3904/2N2222, BC847/BC857, MMBT3904 in SOT-23) to ~100 MHz of useful gain; classic RF silicon (BFR92/BFR93 class, $f_T$ ≈ 5 GHz) for VHF/UHF oscillators and buffers; SiGe HBTs (Infineon BFP420/520/640/740/840 families, NXP BFU7xx) for LNAs and low-phase-noise oscillators to 10+ GHz. Check $f_T$-vs-$I_C$ plots and S-/noise-parameter files, not just the headline.
- **Biasing RF stages:** collector-to-base feedback bias or an active bias (a PNP current mirror/regulator, or bias ICs such as the BCR4xx family) sets $I_C$ independent of β without an emitter bypass capacitor; the emitter goes straight to ground vias because a few tenths of nH of emitter inductance at GHz is significant degeneration (→ [PCB parasitics](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md)).
- **Thermal:** SOT-23 is ~300–500 K/W; 50 mW raises $T_J$ 15–25 K and shifts $V_{BE}$ ~40 mV. Watch it in precision bias and PA driver stages.
- **Matching:** monolithic pairs (e.g. dual transistors in one package) match $V_{BE}$ to ~1 mV and track thermally — use them for differential pairs, current mirrors and log amps.
- **Temperature sensing:** $\Delta V_{BE}$ between two currents, $V_T\ln(I_2/I_1)$, is proportional to absolute temperature — the basis of IC temperature sensors and bandgap references (→ [power supplies](power-supplies-for-rf-and-analog.md)).
- **ESD:** RF transistors are ESD-sensitive (low $V_{EBO}$, tiny geometries); handle accordingly (→ [lab safety/ESD](../19-regulations-safety/lab-safety-esd-high-power.md)).

## Common mistakes & misconceptions
- **Designing gain around β.** β is not controlled; gain should be set by resistor ratios ($R_C/R_E$) or feedback. $g_m$ is the reliable quantity.
- **Mixing up $f_\beta$, $f_\alpha$ and $f_T$.** $f_\beta$ is $f_T/\beta$ (MHz for a 300 MHz part); $f_\alpha$ ≈ $f_T$.
- **Using "0.7 V" for $V_{BE}$ at any current and temperature.** It is a logarithm: ±60 mV per decade of current, −2 mV/K.
- **Confusing $r_e$ and $r_\pi$.** Looking into the emitter you see ≈ $1/g_m$ (26 Ω at 1 mA); looking into the base you see $r_\pi = \beta/g_m$ (plus $(\beta+1)R_E$ with degeneration).
- **"$f_T$ is the maximum operating frequency."** $f_T$ is the unity *current*-gain frequency at a given bias; useful *power* gain exists up to $f_{max}$, which can be above or below $f_T$. In practice design at $f \ll f_T$ for gain and noise.
- **Reading $f_T$ at one current and biasing at another.** $f_T$ can drop by a factor of several at low $I_C$ or past the Kirk-effect peak.
- **Forgetting the Miller effect** and wondering why a "300 MHz transistor" amplifier has 1 MHz bandwidth.
- **Ignoring $V_{CEO}$ in RF/PA stages.** The collector can swing to twice $V_{CC}$; open-base (high-impedance bias) makes breakdown worse.
- **Using $V_T$ = 26 mV at a hot avionics-bay temperature** — $g_m$ at fixed current drops ~0.3 %/K.
- **Assuming BJT noise is just "0.9 nV/√Hz".** It depends on $I_C$ (through $1/2g_m$ and $2qI_B$) and on $r_b$; optimum current scales as $1/R_s$.

## How to simulate / verify
- **Python:** `tools/verify/analog_bjt.py` — small-signal table; Ebers–Moll saturation vs closed form; $f_T$ hand vs ngspice; $f_{max}$ vs Mason's U; Miller exact vs approximation; bias sensitivity; $F_{min}$, $R_{opt}$, $I_{C,opt}$ vs brute force.
- **ngspice (KiCad-bundled, via `tools/verify/analog_ngspice.py`)** — $f_T$ extraction (AC current into base, collector at fixed DC voltage, read $|i_c/i_b|$):
```spice
* fT extraction of a generic NPN (2N3904-like parameters)
.model QG NPN(IS=1e-14 BF=200 VAF=75 TF=300p CJE=4p VJE=0.75 MJE=0.01 CJC=3p VJC=0.75 MJC=0.01 RB=0 RE=0 RC=0)
VCC c 0 DC 5
Ib 0 b DC 25u AC 1
Q1 c b 0 QG
.ac dec 50 1MEG 2G
.end
```
  `i(vcc)` crosses magnitude 1 at 477 MHz (hand formula 473 MHz at $I_C$ = 5 mA). Sweep `Ib` to trace $f_T$ vs $I_C$; add `IKF` and `ITF`/`XTF` parameters to see high-current roll-off.
- **Primer numbers:** `tools/verify/s3_primer.py` §3 — $V_{BE}$ vs $I_S$; ngspice common-emitter $|h_{21}|$ ($f_\beta$, $f_T$) and common-base $|i_c/i_e|$ ($f_\alpha$) of the 2N3904-like model.
- **Vendor models:** use manufacturer SPICE models (Gummel–Poon or VBIC with package parasitics) and S-parameter/noise-parameter files for RF work; verify stability with K/μ from the S-parameters (→ [S-parameters](../03-transmission-lines-matching/s-parameters.md)).
- **Bench:** measure $h_{FE}$ spread across a reel; measure $V_{BE}$ tempco with a thermocouple and a constant-current bias; verify $f_T$ indirectly from $|S_{21}|$ roll-off.

## Open questions / gaps
- Frequency-dependent noise (Hawkins/van der Ziel full model with correlation) is summarised qualitatively; a quantitative treatment belongs with [LNA design](../06-rf-circuits/lna-design.md).
- BJT large-signal distortion (the exponential's intrinsic input IP3 and its improvement by degeneration) is derived in [amplifier topologies](amplifier-topologies.md); system-level IP3 is in [nonlinearity](../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md).
- 2N3904 parameters on this page are a generic textbook-style model, not a vendor model.

## Sources
1. Infineon Technologies, *BFP740 SiGe:C NPN RF bipolar transistor* datasheet v2.0. https://www.infineon.com/dgdl/Infineon-BFP740-DS-v02_00-EN.pdf?fileId=5546d46265f064ff0166389680a24ea4 — $f_T$ = 44 GHz (3 V, 25 mA), $C_{CB}$ 0.08 pF, $C_{EB}$ 0.45 pF, $h_{FE}$ 160–400, $V_{CEO}$ 4 V, $V_{CBO}$ 13 V, $V_{EBO}$ 1.2 V, NF$_{min}$/Gms/OIP3 tables 450 MHz–5.5 GHz. (datasheet)
2. IHP Microelectronics, *SiGe:C BiCMOS technologies* (SG13G2: $f_T/f_{max}$ = 300/500 GHz). https://www.ihp-microelectronics.com/services/research-and-prototyping-service/mpw-prototyping-service/sigec-bicmos-technologies ; also Heinemann et al., "SiGe HBT technology with fT/fmax of 300GHz/500GHz and 2.0 ps CML gate delay," IEDM 2010. (manufacturer / peer-reviewed)
3. J. D. Cressler, G. Niu, *Silicon-Germanium Heterojunction Bipolar Transistors*, Artech House 2003 — Ge grading, drift field, β–$r_b$ trade. (textbook)
4. P. R. Gray, P. J. Hurst, S. H. Lewis, R. G. Meyer, *Analysis and Design of Analog Integrated Circuits*, 5th ed., Wiley 2009 — ch. 1 (BJT models, Early effect, $f_T$, Kirk effect, breakdown), ch. 7 (Miller, frequency response), ch. 11 (noise, $F_{min}$ and optimum source resistance). (textbook)
5. A. S. Sedra, K. C. Smith, *Microelectronic Circuits*, 7th ed., Oxford 2015 — ch. 6 (BJT operation, Ebers–Moll, saturation, bias design), ch. 10 (high-frequency hybrid-π, Miller). (textbook)
6. P. Horowitz, W. Hill, *The Art of Electronics*, 3rd ed., Cambridge 2015 — ch. 2 (Ebers–Moll view, bias stability, thermal runaway, $V_{BE}$ tempco), ch. 8 (bipolar noise, optimum collector current). (textbook)
7. S. J. Mason, "Power gain in feedback amplifiers," *IRE Trans. Circuit Theory* CT-1 (1954) 20–25 — unilateral power gain U. (peer-reviewed)
8. MIT OpenCourseWare 6.012 *Microelectronic Devices and Circuits* lecture notes (BJT small-signal model, $f_T$). https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/ (lecture notes)
