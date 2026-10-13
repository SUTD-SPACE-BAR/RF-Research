---
title: Signal-flow graphs, Mason's rule and mismatch uncertainty
domain: 03-transmission-lines-matching
slug: signal-flow-graphs-mason
tags: [signal-flow-graph, mason-gain-rule, mismatch-uncertainty, power-measurement, transducer-gain, directivity, vna-error-model, ripple]
prerequisites:
  - s-parameters.md
  - reflections-vswr-return-loss-mismatch.md
related:
  - smith-chart.md
  - ../17-test-measurement/rf-power-measurement.md
  - ../17-test-measurement/vna-fundamentals-calibration.md
  - ../06-rf-circuits/lna-design.md
  - ../07-noise-linearity/receiver-cascade-analysis.md
level: intermediate
confidence: high
last_updated: 2026-09-27
---

# Signal-flow graphs, Mason's rule and mismatch uncertainty

## Questions this page answers
- What is a signal-flow graph and how do I draw one for a two-port between a source and a load?
- How does Mason's gain rule work, step by step?
- Where do $\Gamma_\text{in}=S_{11}+S_{12}S_{21}\Gamma_L/(1-S_{22}\Gamma_L)$ and the transducer-gain formula come from?
- Why can't I measure RF power more accurately than about ±0.1–0.6 dB even with a perfect power sensor?
- How much does a mismatched source (like a LoRa module) and a mismatched antenna reduce delivered power, and can a mismatch ever *increase* it?
- Why does my SWR meter read 1.2 on a perfect dummy load?
- Where do the periodic ripples in a cable's insertion loss come from?

## TL;DR
- A **signal-flow graph** turns the wave equations $b=Sa$ into a picture: one node per wave ($a_1,b_1,a_2,b_2,\dots$), one branch per S-parameter or reflection coefficient. Source: node $b_s$ feeding $a_1$ with a reflection branch $\Gamma_S$ from $b_1$ to $a_1$; load: branch $\Gamma_L$ from $b_2$ to $a_2$.
- **Mason's rule**: $T=\dfrac{\sum_kP_k\Delta_k}{\Delta}$, $\Delta=1-\sum L_i+\sum L_iL_j-\sum L_iL_jL_k+\dots$ over loops and sets of *non-touching* loops; $\Delta_k$ is $\Delta$ with loops touching path $k$ removed. Verified against direct linear solves on random graphs (error 10⁻¹⁵) and symbolically (sympy).
- Results: $\Gamma_\text{in}=S_{11}+\dfrac{S_{12}S_{21}\Gamma_L}{1-S_{22}\Gamma_L}$; $\dfrac{b_2}{b_s}=\dfrac{S_{21}}{(1-S_{11}\Gamma_S)(1-S_{22}\Gamma_L)-S_{12}S_{21}\Gamma_S\Gamma_L}$ → the transducer gain $G_T$.
- Source → load directly: $P_L=P_\text{av}\dfrac{(1-|\Gamma_S|^2)(1-|\Gamma_L|^2)}{|1-\Gamma_S\Gamma_L|^2}$. Maximum ($=P_\text{av}$) at $\Gamma_L=\Gamma_S^*$; with a mismatched source a *mismatched* (conjugate) load can take more power than a 50 Ω load.
- **Mismatch uncertainty**: when the phases are unknown, the measured power is off by a factor $|1-\Gamma_S\Gamma_L|^{-2}$, i.e. between $-20\log(1+|\Gamma_S||\Gamma_L|)$ and $-20\log(1-|\Gamma_S||\Gamma_L|)$ dB. Generator VSWR 1.5 + sensor VSWR 1.2: ±0.16 dB; VSWR 2 source + VSWR 1.5 sensor: +0.60/−0.56 dB. The distribution is U-shaped; its standard deviation is ≈ worst-case/√2.
- **Directivity**: a coupler/bridge with directivity $D$ (as a linear leakage) adds up to $|D|$ to the measured |Γ|: 20 dB directivity → a perfect load can read VSWR 1.22.
- **Two mismatches $\ell$ apart**: insertion-loss ripple $20\log\frac{1+|\Gamma_1\Gamma_2|}{1-|\Gamma_1\Gamma_2|}$ dB peak-to-peak with period $v_p/2\ell$.

## Intuition (no math)
Waves bounce. A wave enters a two-port; part comes straight back ($S_{11}$), part goes through ($S_{21}$), hits the load, part of *that* reflects back into the two-port, part of that leaks backward through $S_{12}$ to the input, and so on forever. Each "bounce path" multiplies gains; all bounce paths add up. A signal-flow graph is a map of every possible bounce, and Mason's rule is a bookkeeping trick that sums the infinite series of bounces in closed form — the loops contribute geometric series $1/(1-L)$.

Mismatch uncertainty is the same idea applied to measurement. A power meter connected to a slightly mismatched source reflects a little of the wave back; the source re-reflects a little of that; this re-reflected wave adds to the original with a phase that depends on the cable length and frequency — which you don't know. So your reading could be slightly high or slightly low, and no calibration of the meter alone can fix it, because the error depends on *both* reflection coefficients and their relative phase.

## The math

### Level 1 — drawing the graph
Rules (Pozar §4.5): each port has two nodes, $a_i$ (incident) and $b_i$ (reflected). A branch from node $x$ to node $y$ with gain $g$ means "$y$ receives $g\cdot x$". A node's value is the sum of all incoming branches. For a two-port between source and load:
- $a_1\xrightarrow{S_{11}}b_1$, $a_1\xrightarrow{S_{21}}b_2$, $a_2\xrightarrow{S_{22}}b_2$, $a_2\xrightarrow{S_{12}}b_1$;
- load: $b_2\xrightarrow{\Gamma_L}a_2$; source: $b_s\xrightarrow{1}a_1$ and $b_1\xrightarrow{\Gamma_S}a_1$, where $b_s$ is the wave a source would launch into a matched load ($|b_s|^2=P_\text{av}(1-|\Gamma_S|^2)$ for peak-normalised waves, $P_\text{av}$ = available power).

### Level 2 — Mason's gain rule and its applications
**Rule.** For a path from source node to sink node:
$$T=\frac{1}{\Delta}\sum_kP_k\Delta_k,\qquad\Delta=1-\sum_iL_i+\sum_{\text{pairs}}L_iL_j-\sum_{\text{triples}}L_iL_jL_k+\cdots$$
$P_k$: gain of the $k$-th forward path (no node visited twice). $L_i$: loop gains; the pairs/triples include only mutually **non-touching** loops (no shared node). $\Delta_k$: the same determinant built from loops that do not touch path $k$. `tools/verify/tline_mason.py` implements this generically (enumerating simple paths, simple cycles and non-touching sets) and matches the direct solution of the node equations $(\mathbf I-\mathbf A)\mathbf x=\mathbf e$ on 40 random graphs to 6×10⁻¹⁶.

**Input reflection with a load.** From $a_1$ to $b_1$: paths $P_1=S_{11}$ and $P_2=S_{21}\Gamma_LS_{12}$; one loop $L_1=S_{22}\Gamma_L$ (touching $P_2$, not $P_1$). So
$$\Gamma_\text{in}=\frac{S_{11}(1-S_{22}\Gamma_L)+S_{21}\Gamma_LS_{12}}{1-S_{22}\Gamma_L}=S_{11}+\frac{S_{12}S_{21}\Gamma_L}{1-S_{22}\Gamma_L}.$$
**Source to output wave.** From $b_s$ to $b_2$: one path $S_{21}$; loops $S_{11}\Gamma_S$, $S_{22}\Gamma_L$, $S_{21}\Gamma_LS_{12}\Gamma_S$; the first two don't touch each other:
$$\frac{b_2}{b_s}=\frac{S_{21}}{1-S_{11}\Gamma_S-S_{22}\Gamma_L-S_{21}S_{12}\Gamma_L\Gamma_S+S_{11}\Gamma_SS_{22}\Gamma_L}=\frac{S_{21}}{(1-S_{11}\Gamma_S)(1-S_{22}\Gamma_L)-S_{12}S_{21}\Gamma_S\Gamma_L}.$$
Power to the load $P_L=\tfrac12|b_2|^2(1-|\Gamma_L|^2)$ divided by $P_\text{av}=\tfrac12|b_s|^2/(1-|\Gamma_S|^2)$ gives the transducer gain $G_T$ of the [S-parameters page](s-parameters.md) — both symbolic identities verified with sympy, and $G_T$ numerically.

**Source straight into a load.** Remove the two-port ($S_{21}=S_{12}=1$, $S_{11}=S_{22}=0$): loop $\Gamma_S\Gamma_L$, so the wave into the load is $b_s/(1-\Gamma_S\Gamma_L)$ and
$$\boxed{P_L=P_\text{av}\frac{(1-|\Gamma_S|^2)(1-|\Gamma_L|^2)}{|1-\Gamma_S\Gamma_L|^2}}$$
(checked against a Thevenin circuit calculation). Special cases: $\Gamma_S=0$ → $P_\text{av}(1-|\Gamma_L|^2)$ (the ordinary mismatch loss); $\Gamma_L=\Gamma_S^*$ → $P_\text{av}$ exactly (conjugate match); $\Gamma_L=0$ with $\Gamma_S\neq0$ → $P_\text{av}(1-|\Gamma_S|^2)$ — less than the conjugate case. So "matching the antenna to 50 Ω" is optimal only if the source is 50 Ω.

### Level 3 — measurement uncertainty from mismatch
**Power measurement.** A power sensor of reflection $\Gamma_L$ on a source of $\Gamma_S$ measures $P_L$ above, but the quantity usually wanted is the power the source would deliver to a *perfect* 50 Ω load, $P_{Z_0}=P_\text{av}(1-|\Gamma_S|^2)$. The ratio is
$$\frac{P_L}{P_{Z_0}}=\frac{1-|\Gamma_L|^2}{|1-\Gamma_S\Gamma_L|^2}.$$
The numerator is known (sensor calibration factor corrects it); the denominator depends on the unknown relative phase. **Mismatch uncertainty limits:**
$$M_u=-20\log_{10}(1\mp|\Gamma_S||\Gamma_L|)\ \text{dB}\quad(+\text{ for }1-,\ -\text{ for }1+).$$

| Source | Load / sensor | $|\Gamma_S||\Gamma_L|$ | limits (dB) | std for uniform phase |
|---|---|---|---|---|
| VSWR 1.5 generator | VSWR 1.2 sensor | 0.018 | +0.159 / −0.157 | 0.111 |
| VSWR ~1.3 uncorrected VNA port | VSWR 2 DUT | 0.043 | +0.386 / −0.370 | 0.267 |
| LoRa module ~VSWR 2 (assumed) | VSWR 1.5 cheap sensor | 0.067 | +0.599 / −0.561 | 0.409 |

With uniformly distributed phase the error has a U-shaped (arcsine-like) distribution — values near the limits are *more* likely than near zero — with standard deviation ≈ limit/√2 (script: Monte-Carlo 0.111 dB vs 0.113). Uncertainty budgets (e.g. following ISO GUM practice as described in power-meter application notes) therefore combine mismatch terms as U-shaped contributors (divide the limit by √2), then RSS them with sensor calibration, linearity and noise terms. Minimising it: use a well-matched sensor, add a good 6–10 dB attenuator at the source (improves $|\Gamma_S|$ by twice the attenuation in dB), or measure $\Gamma_S$ and $\Gamma_L$ with a VNA and correct.

**Reflection measurement with finite directivity.** A reflectometer (coupler or bridge) measures $\Gamma_m\approx E_D+E_R\Gamma(1+E_S\Gamma+\cdots)$ — directivity $E_D$, source match $E_S$, tracking $E_R$ — the standard one-port error model; VNA calibration (SOL) solves for these three terms ([VNA calibration](../17-test-measurement/vna-fundamentals-calibration.md)). Uncorrected, $|\Gamma_m|$ lies within $|\Gamma|\pm|E_D|$ (to first order): 20 dB directivity (|E_D| = 0.1) makes a perfect load read up to VSWR 1.222, a true VSWR 1.22 read between 1.00 and 1.50 (script). This is why a cheap SWR bridge can't verify "1.1:1".

**Ripple from separated mismatches.** A 50 Ω line of electrical length θ between reflections $\Gamma_1$, $\Gamma_2$: $S_{21}\propto\dfrac{e^{-j\theta}}{1-\Gamma_1\Gamma_2e^{-2j\theta}}$ → insertion-loss ripple $20\log\frac{1+|\Gamma_1\Gamma_2|}{1-|\Gamma_1\Gamma_2|}$ dB peak-to-peak, period $\Delta f=v_p/(2\ell)$. Two VSWR ≈ 1.22 / 1.35 connectors ($|\Gamma|$ 0.10 / 0.15) 10 cm apart in PTFE cable: 0.26 dB p-p every 1.05 GHz (script). The period tells you the spacing — the frequency-domain twin of [TDR](time-domain-reflectometry.md).

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $T=\sum P_k\Delta_k/\Delta$ | any linear flow graph | — |
| $\Gamma_\text{in}=S_{11}+S_{12}S_{21}\Gamma_L/(1-S_{22}\Gamma_L)$ | two-port + load | unilateral ($S_{12}=0$): $\Gamma_\text{in}=S_{11}$ |
| $P_L=P_\text{av}(1-|\Gamma_S|^2)(1-|\Gamma_L|^2)/|1-\Gamma_S\Gamma_L|^2$ | source → load | max at $\Gamma_L=\Gamma_S^*$ |
| $M_u=-20\log(1\mp|\Gamma_S\Gamma_L|)$ | unknown phase | 1.5 & 1.2 VSWR: ±0.16 dB |
| std ≈ $M_u/\sqrt2$ | uniform phase (U-shaped) | — |
| $|\Gamma_m|\in|\Gamma|\pm|E_D|$ | uncorrected reflectometer | 20 dB: ±0.1 |
| Ripple p-p $=20\log\frac{1+|\Gamma_1\Gamma_2|}{1-|\Gamma_1\Gamma_2|}$, period $v_p/2\ell$ | two discontinuities | 0.1 & 0.15: 0.26 dB |
| An attenuator of $A$ dB improves source match: $|\Gamma_S'|\le|\Gamma_\text{pad}|+|\Gamma_S|10^{-A/10}$ | power measurement | 10 dB pad: ×0.1 |

## Worked examples

### Example 1 — measuring the E22 module's output power
You connect the 433 MHz module (assume its output is VSWR ≈ 2, |Γ_S| = 0.33 — not specified in the module data seen) through a 20 dB, 5 W attenuator (VSWR 1.15, |Γ| = 0.07) to an RF power meter (VSWR 1.2). The attenuator's input faces the module: $|\Gamma_S||\Gamma_\text{pad}|=0.33\times0.07=0.023$ → ±0.2 dB; on the meter side the module's mismatch is suppressed by 40 dB round trip, so $|\Gamma_{S,\text{eff}}|\approx0.07+0.33\times0.01=0.073$ and $0.073\times0.091=0.0067$ → ±0.06 dB. Plus attenuator calibration (±0.1–0.2 dB typ.) and meter accuracy. Realistic total ≈ ±0.3 dB: a reading of 32.7 dBm is consistent with the nominal 33 dBm.

### Example 2 — can a "mismatched" antenna receive more power?
Suppose the module output impedance really is 30 + j15 Ω ($\Gamma_S=-0.21+j0.23$, |Γ_S| = 0.31). Into a perfect 50 Ω antenna it delivers $P_\text{av}(1-0.094)=0.906P_\text{av}$; into an antenna with $\Gamma_L=\Gamma_S^*$ (i.e. $Z_L=30-j15$ Ω, VSWR 1.89!) it delivers $P_\text{av}$ — 0.43 dB more. Practical caution: a PA's "output impedance" isn't a linear source impedance (see [matching page, Level 3](impedance-matching-lumped-and-distributed.md)), so for EBYTE modules simply present 50 Ω as the manufacturer intends.

### Example 3 — the cheap SWR meter on a dummy load
A meter with 20 dB directivity reads VSWR 1.15 on your known-good 50 Ω dummy load. That is within its ±0.1 |Γ| error band (reading could be 1.00–1.22) — the meter, not the load, is the limit. A NanoVNA after SOL calibration has a much better *effective* directivity (order 35–45 dB with a decent cal kit — an estimate, not a datasheet figure), so it can resolve VSWR ≈ 1.02–1.04.

## Practical notes
- Draw the graph whenever you cascade mismatched blocks (antenna – cable – filter – LNA): the loops $\Gamma_i\Gamma_{i+1}$ between adjacent blocks are what create ripple and uncertainty.
- For receivers, the same algebra describes how an LNA's input match and the antenna's match interact (noise figure with mismatched source → [LNA design](../06-rf-circuits/lna-design.md)).
- Put a well-matched attenuator in front of a power meter when measuring a transmitter — it protects the meter and reduces mismatch uncertainty.
- In VNA error models, the "source match" and "load match" terms are exactly $\Gamma_S$ and $\Gamma_L$ of this page; 12-term calibration removes them (→ 17-test-measurement).

## Common mistakes & misconceptions
- **Counting touching loops as non-touching** in Mason's rule — they must share no node.
- **Forgetting $\Delta_k$** (loops that don't touch the path) — the most common algebra slip.
- **"A calibrated power sensor is accurate to its datasheet spec."** Only for a perfectly matched source; mismatch uncertainty is additional and often dominant.
- **Adding mismatch uncertainties linearly as if normal** — they are U-shaped; worst-case add linearly, statistical combination uses limit/√2 before RSS.
- **Assuming a 50 Ω load always maximises power** — only if the source is 50 Ω (then $\Gamma_S^*=0$).

## How to simulate / verify
- `tools/verify/tline_mason.py` — generic Mason implementation vs direct solve (random graphs), sympy derivations of Γ_in and b₂/b_s, transducer gain vs Pozar's formula, source–load power formula vs circuit, conjugate-match optimum, mismatch-uncertainty limits and Monte-Carlo distribution, directivity-limited VSWR, ripple from two mismatches. All pass.
- scikit-rf: cascade `Network`s with `**` and inspect ripple; `rf.network.s2t` for T-parameter chains; `rf.calibration` for the one-port (E_D, E_S, E_R) error model.

## Open questions / gaps
- EBYTE module output impedance / source match is not published in the sources consulted; examples assume values.
- Full ISO-GUM uncertainty budgets for power meters (sensor cal factor, linearity, zero, noise) belong to [RF power measurement](../17-test-measurement/rf-power-measurement.md).

## Sources
1. S. J. Mason, "Feedback theory — some properties of signal flow graphs," *Proc. IRE*, vol. 41, pp. 1144–1156, 1953; and "Feedback theory — further properties of signal flow graphs," *Proc. IRE*, vol. 44, pp. 920–926, 1956. (peer-reviewed)
2. D. M. Pozar, *Microwave Engineering*, 4th ed., 2012 — §4.5 (signal-flow graphs, Mason's rule, TRL example), §12.1 (power gains). (textbook)
3. N. Kuhn, "Simplified signal flow graph analysis," *Microwave Journal*, Nov. 1963 — the source/load graph conventions used in HP/Keysight notes. (trade journal; as cited in AN 154)
4. Hewlett-Packard/Keysight, *S-Parameter Design*, AN 154 (5952-1087), 1990 — flow graphs for amplifier gain. (app note)
5. Keysight Technologies, *Fundamentals of RF and Microwave Power Measurements (Part 3): Power Measurement Uncertainty per International Guides*, AN 1449-3 — mismatch uncertainty, U-shaped distribution treatment. (app note; general content, not re-fetched this session)
6. G. F. Engen, *Microwave Circuit Theory and Foundations of Microwave Metrology*, IEE/Peregrinus 1992 — mismatch factor, reflectometer error models. (textbook)
7. Verification: `tools/verify/tline_mason.py`. (numerical check)
