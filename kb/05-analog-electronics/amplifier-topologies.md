---
title: Amplifier topologies — CE/CS, CB/CG, CC/CD, cascode, differential pair, Darlington, mirrors, feedback amplifiers, RF gain blocks
domain: 05-analog-electronics
slug: amplifier-topologies
tags: [common-emitter, common-source, common-base, common-gate, emitter-follower, source-follower, cascode, differential-pair, darlington, current-mirror, feedback-amplifier, resistive-feedback, mmic-gain-block, miller-effect, octc, bandwidth, iip3, degeneration]
prerequisites:
  - bjt-fundamentals-small-signal.md
  - fets-mosfet-jfet-gaas-gan.md
  - ../01-circuit-theory/two-port-networks-zyh-abcd.md
related:
  - feedback-and-stability.md
  - op-amps-real-limitations.md
  - low-noise-analog-design.md
  - ../06-rf-circuits/lna-design.md
  - ../06-rf-circuits/amplifier-stability-and-biasing.md
  - ../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md
  - ../18-components-parts/lna-pa-gain-block-mmics.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Amplifier topologies — CE/CS, CB/CG, CC/CD, cascode, differential pair, Darlington, mirrors, feedback amplifiers, RF gain blocks

## Questions this page answers
- What do the three basic single-transistor stages (common emitter/source, base/gate, collector/drain) each do well?
- Why does a common-base stage make a good wideband 50 Ω input, and what noise figure does that cost?
- Why is the cascode everywhere, from op-amp input stages to LNAs?
- How does a differential pair reject common-mode noise and why is it more linear than a single transistor?
- Why do MMIC gain blocks (ERA, MAR, Gali, PGA class) have a Darlington pair and two resistors, and why do I bias them through a resistor and choke?
- How do the four feedback-amplifier types change input and output impedance?
- How can I estimate the bandwidth of a multi-capacitor amplifier without solving a big polynomial?
- How much does emitter degeneration improve linearity (IIP3)?
- What is a current mirror, and how accurate is it?
- How do shunt peaking, series peaking and T-coils extend bandwidth, and by how much?
- How does a distributed (travelling-wave) amplifier get DC–20 GHz bandwidth?
- Why do balanced amplifiers with 90° hybrids have a good input match even when each amplifier is badly matched?
- What noise figure does a resistive-feedback wideband LNA have?
- Why can't I use an LNA to drive a power amplifier?
- What is crossover distortion, and why are output stages class AB?

## TL;DR
- **CE/CS:** inverting voltage gain $-g_mR_L'$, medium $R_{in}$ ($r_\pi$ for BJT), high $R_{out}$; bandwidth limited by Miller. With emitter/source degeneration $R_E$: $A_v \approx -R_C/(r_e+R_E)$, $R_{in} \approx r_\pi+(\beta+1)R_E$, more linear.
- **CB/CG:** $R_{in} \approx 1/g_m$, non-inverting gain $g_mR_L$, current gain ≈ 1, no Miller multiplication → wideband. $1/g_m$ = 50 Ω at $I_C$ = 0.52 mA; noise factor at that match ≥ 1 + 1/(2g_mR_s) = 1.76 dB (BJT), 1 + γ/α ≈ 2.2 dB (MOS) (`tools/verify/analog_topologies.py` §5).
- **CC/CD (followers):** gain ≈ 1, $R_{out} \approx 1/g_m + R_s/(\beta+1)$ — impedance converter; prone to VHF oscillation with capacitive loads (→ [feedback & stability](feedback-and-stability.md)).
- **Cascode (CE + CB):** kills Miller (the CE collector sees ≈ $1/g_m$), raises $R_{out}$ to ≈ $\beta r_o$ (BJT) or $g_mr_o^2$ (MOS), improves reverse isolation.
- **Differential pair:** $I_{C1}-I_{C2} = I_{EE}\tanh(v_d/2V_T)$; rejects common-mode via the tail source; even-order distortion cancels; intrinsic IIP3 = $4V_T$ ≈ 103 mV peak vs $\sqrt8\,V_T$ ≈ 73 mV for a single BJT (script §4).
- **Degeneration and IIP3:** for an exponential device with $x = g_mR_E$, $A_{IIP3} = \sqrt8\,V_T(1+x)^2/\sqrt{|1-2x|}$ — derived here and confirmed by two-tone simulation (×4 at $x$ = 1, ×28 at $x$ = 10, with an idealised IM3 null at $x$ = 0.5).
- **Resistive-feedback gain block:** feedback resistor $R_F$ (collector→base) + emitter resistor $R_E$ give $Z_{in} = Z_{out} = Z_0$ when $R_FR_E = Z_0^2$, and $S_{21} = 1 - R_F/Z_0$ (−9 = 19.1 dB for $R_F$ = 500 Ω, $R_E$ = 5 Ω). ngspice with a real transistor: 18.6 dB, $|S_{11}| < -24$ dB to 450 MHz (script §1). MMICs use a Darlington to make the loop gain large; bias through $R_{bias} = (V_{CC}-V_d)/I_d$ plus a choke > 500 Ω [1].
- **Bandwidth estimate (OCTC):** $\omega_{-3dB} \approx 1/\sum R_{i0}C_i$; for a CE stage it gave 0.444 MHz vs 0.445 MHz exact (script §3).
- **Feedback:** loop gain T = aβ; closed-loop gain ≈ 1/β with error ≈ 1/T; series mixing multiplies $Z_{in}$ by (1+T), shunt sampling divides $Z_{out}$ by (1+T).

- **Bandwidth extension** (`tools/verify/s3_bw_extension.py`, ngspice): shunt peaking 1.72 × at $m = L/R^2C$ = 0.414 (1.57 × flat delay at 0.32); series peaking 3.68 × (C split 55/45); bridged T-coil 2.83 × at k = 1/3 with $Z_{in}$ = R exactly; distributed amp $|S_{21}| = ng_mZ_0/2$, flat to the line cut-off (2.0 to 12.8 GHz vs a lumped 4.0 to 1.33 GHz); a balanced pair of |S11| = −9.5 dB amplifiers gives < −15.8 dB over ±10 % with unchanged gain. Resistive-feedback single-SiGe LNA NF 1.77 dB at 433 MHz.
- **Output stages:** class-B push-pull has a ±$V_{BE}$ dead band (22 % THD at 2 V peak); class AB with two-diode bias and 1 Ω emitter resistors 0.42 %; class-B efficiency $\frac{\pi}{4}V_p/V_{CC}$.
- **An LNA is not a driver:** a 3 V/5 mA LNA cannot exceed ≈ −2 dBm into 50 Ω (BGA524N6 OP1dB ≈ +2.6 dBm).

## Intuition (no math)
A transistor is a voltage-controlled current source with three terminals, so there are three ways to wire it with one terminal common to input and output:
- **Common emitter/source** — drive the control terminal, take current from the output terminal into a load resistor: voltage gain, inversion. The workhorse.
- **Common base/gate** — drive the emitter/source (a low-impedance point, because pushing current into it barely changes $V_{BE}$), take the same current out of the collector into a high impedance. It is a *current buffer*: it passes current through unchanged but moves it from a low-impedance node to a high-impedance one, which is what makes voltage gain without the Miller penalty.
- **Common collector/drain (follower)** — the output terminal follows the input minus a nearly constant $V_{BE}$ or $V_{GS}$. No voltage gain, but it can source current into a heavy load while barely loading the source: a *voltage buffer*.

Combine them and you get the useful compound stages: the **cascode** (CE feeding a CB) gets the gain of a CE stage with the bandwidth and isolation of a CB; the **differential pair** (two CE stages sharing a tail current) responds to the *difference* of two inputs and ignores what they have in common — the key to rejecting ground noise and supply noise; the **Darlington** (one follower driving another) multiplies current gain.

**Feedback** trades excess gain for everything else. Measure the output, compare it with the input, and drive the error: the closed-loop behaviour then depends on the (precise, stable) feedback network, not the (sloppy, temperature-dependent) transistor. The same idea sets input and output impedances to useful values — which is exactly how a two-resistor MMIC gain block ends up matched to 50 Ω over decades of bandwidth.

## The math

### Level 1 — the basic stages (BJT; replace $r_\pi \to \infty$, $\beta \to \infty$ for FETs)

Bias values used below: $I_C$ = 1 mA, β = 200, $V_A$ = 75 V → $g_m$ = 38.7 mS, $r_\pi$ = 5.17 kΩ, $r_e$ = 25.9 Ω, $r_o$ = 75 kΩ (script §2).

| Stage | Voltage gain | $R_{in}$ | $R_{out}$ | Example ($R_C$ = 5 kΩ, $R_E$ = 500 Ω, $R_{sig}$ = 1 kΩ) |
|---|---|---|---|---|
| CE | $-g_m(R_C\|r_o)$ | $r_\pi$ | $R_C\|r_o$ | −181, 5.2 kΩ, 4.7 kΩ |
| CE + $R_E$ | $\approx -R_C/(r_e+R_E)$ | $r_\pi+(\beta+1)R_E$ | ≈ $R_C$ | −9.5, 106 kΩ |
| CB | $g_mR_C$ | $r_e \approx 1/g_m$ | ≈ $R_C$ | +193, 25.9 Ω |
| CC | $R_E/(r_e+R_E)$ | $r_\pi+(\beta+1)R_E$ | $r_e + R_{sig}/(\beta+1)$ | 0.951, 30.8 Ω |
| Cascode | $-g_mR_L$ | $r_\pi$ | ≈ $\beta r_o$ (BJT), $g_mr_o^2$ (MOS) | $R_{out}$ ≈ 15 MΩ |

FET equivalents: CS gain $-g_m(R_D\|r_o)$; CG $R_{in} = 1/(g_m+g_{mb})$; source follower gain $g_mR_S/(1+g_mR_S)$ (less than a BJT follower because $g_m$ is lower, and body effect reduces it further in ICs).

**Differential pair.** Two matched transistors, emitters joined to a tail current $I_{EE}$:
$$I_{C1}-I_{C2} = \alpha I_{EE}\tanh\frac{v_d}{2V_T},\qquad A_{dm} = g_mR_C\ (g_m \text{ of one device at } I_{EE}/2),\qquad A_{cm} \approx -\frac{R_C}{2R_{EE}}$$
CMRR ≈ $2g_mR_{EE}$ (tail resistance $R_{EE}$; a transistor current source makes it large).

**Current mirror.** Two matched BJTs with the same $V_{BE}$: $I_{out}/I_{ref} = 1/(1+2/\beta)$ (0.990 at β = 200); a β-helper or Wilson mirror reduces the error to ~$2/\beta^2$ (script §6). Output resistance: $r_o$ (simple), ≈ $\beta r_o/2$ (Wilson), ≈ $\beta r_o$ (cascode). Widlar: $I_{out}R_E = V_T\ln(I_{ref}/I_{out})$ — 1 mA → 10 µA needs only 11.9 kΩ.

**Darlington.** Composite β ≈ $\beta_1\beta_2$; composite $V_{BE}$ ≈ 1.2–1.4 V; composite $g_m$ = $g_{m2}/2$ without a bleeder resistor (Q1's $r_e$ equals Q2's $r_\pi$, so the input voltage splits equally; script §6); slow turn-off (Q1 cannot pull charge out of Q2's base) — hence the resistor from Q2 base to emitter in practical Darlingtons and in MMICs.

**Four feedback-amplifier types** (mixing at input – sampling at output), loop gain $T = a\beta_f$:

| Type | Closed-loop quantity | $Z_{in}$ | $Z_{out}$ | Example |
|---|---|---|---|---|
| Series–shunt | voltage gain (V/V) | ×(1+T) | ÷(1+T) | non-inverting op-amp |
| Shunt–series | current gain (A/A) | ÷(1+T) | ×(1+T) | current amplifier |
| Series–series | transconductance (A/V) | ×(1+T) | ×(1+T) | degenerated CE stage ($R_E$) |
| Shunt–shunt | transresistance (V/A) | ÷(1+T) | ÷(1+T) | TIA; collector-to-base resistor |

Closed-loop gain $A = a/(1+T) \to 1/\beta_f$; relative gain error ≈ $1/T$ (1 % for T = 100; script §7); gain sensitivity to $a$ is divided by (1+T); single-pole bandwidth is multiplied by (1+T) (→ [feedback & stability](feedback-and-stability.md) for why too much T oscillates).

### Level 2 — derivations

**Emitter degeneration.** With $R_E$ in the emitter, $v_{in} = v_{be} + i_cR_E/\alpha$ and $i_c = g_mv_{be}$, so $G_m = i_c/v_{in} = g_m/(1+g_mR_E)$ → $1/R_E$ when $g_mR_E \gg 1$. The input sees $r_\pi$ plus $R_E$ reflected through the current gain: $(\beta+1)R_E$. This is local series–series feedback with $T = g_mR_E$.

**Common base as a 50 Ω input.** $R_{in} = 1/g_m$ → set $I_C = V_T/R_s$ = 0.52 mA for 50 Ω. Noise: the collector shot noise referred to the input is $e_n^2 = 2qI_C/g_m^2 = 2kT/g_m$, so $F = 1 + e_n^2/(4kTR_s) = 1 + 1/(2g_mR_s)$ = 1.5 (1.76 dB) at match, before $r_b$ and base shot noise [2]. The MOS common-gate equivalent is $F = 1+\gamma/\alpha$ ≈ 1.67 (2.2 dB, γ = 2/3). This is the price of a *resistive* broadband match; reactive (inductive-degeneration) matching avoids it (→ [LNA design](../06-rf-circuits/lna-design.md)).

**Cascode output resistance.** The CB device Q2 sits on the collector of Q1 with emitter impedance $r_{o1}$. A change in output voltage must change Q2's current via its $r_o$; the resulting emitter voltage change is fed back through $g_{m2}$: $R_{out} = r_{o2}[1+g_{m2}(r_{\pi2}\|r_{o1})] \approx \beta r_{o2}$ for a BJT (limited by $r_{\pi2}$: base current escapes) and $\approx g_{m2}r_{o2}r_{o1}$ for a MOSFET. With an ideal current-source load the cascode's voltage gain is $g_mR_{out}$ — hundreds of thousands in principle, which is how single-stage op-amps (folded/telescopic cascodes) get 60–80 dB.

**Differential pair transfer function.** With $I_{C1} = I_Se^{V_{BE1}/V_T}$, $I_{C2} = I_Se^{V_{BE2}/V_T}$, $I_{C1}+I_{C2} = \alpha I_{EE}$ and $v_d = V_{BE1}-V_{BE2}$: $I_{C1}/I_{C2} = e^{v_d/V_T}$, hence $I_{C1} = \alpha I_{EE}/(1+e^{-v_d/V_T})$ and $I_{C1}-I_{C2} = \alpha I_{EE}\tanh(v_d/2V_T)$. The function is odd → no even harmonics; the linear range is ≈ ±2$V_T$ (±50 mV). Emitter resistors in each leg widen it ≈ ×(1+$g_mR_E$).

**Intrinsic third-order intercept.** For $y = a_1x + a_2x^2 + a_3x^3$, two equal tones of amplitude A give IM3 equal to the fundamental at $A_{IIP3} = \sqrt{\tfrac43|a_1/a_3|}$ (→ [nonlinearity](../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md)).
- Single BJT, $i_c \propto e^{v/V_T}$: $a_1 = 1/V_T$, $a_3 = 1/(6V_T^3)$ → $A_{IIP3} = \sqrt8\,V_T$ = 73.1 mV peak.
- Differential pair, $\tanh(v/2V_T)$: $a_1 = 1/(2V_T)$, $a_3 = -1/(24V_T^3)$ → $A_{IIP3} = 4V_T$ = 103.4 mV.
Both confirmed by two-tone FFT (script §4). Across 50 Ω, 73 mV peak is ≈ −12.7 dBm — a bare BJT junction is quite nonlinear.

**Degeneration and IIP3 (derivation).** Series feedback through $R_E$ turns the device nonlinearity $i = a_1v_{be}+a_2v_{be}^2+a_3v_{be}^3$ into the overall $i = b_1v_{in}+b_2v_{in}^2+b_3v_{in}^3$ with (inverting the series $v_{in} = v_{be}+R_Ei$):
$$b_1 = \frac{a_1}{1+x},\qquad b_3 = \frac{a_3(1+x) - 2a_2^2R_E}{(1+x)^5},\qquad x = a_1R_E = g_mR_E .$$
For the exponential ($a_2 = I_C/2V_T^2$, $a_3 = I_C/6V_T^3$): $b_3 = \frac{I_C}{6V_T^3}\frac{1-2x}{(1+x)^5}$, hence
$$A_{IIP3} = \sqrt8\,V_T\,\frac{(1+x)^2}{\sqrt{|1-2x|}}\ \xrightarrow{x\gg1}\ \approx 2V_T\,x^{3/2}.$$
Two-tone simulation matches to 3 digits: ×2.21 at $x$ = 0.25, ×4.00 at 1, ×7.15 at 3, ×27.8 at 10 (script §4). The second-order term, fed back through $R_E$, *generates* third-order distortion of opposite sign; at $x$ = 1/2 it cancels the device's own $a_3$ — a sweet spot that exists in the ideal low-frequency model but is narrow and shifted by $r_b$, source impedance and reactances in practice. (Common rules of thumb quote a $(1+g_mR_E)^{3/2}$ improvement; the exact result above differs by $\sqrt2$ asymptotically and by more near the null.)

**Resistive-feedback gain block (derivation).** Model an ideal transconductor ($g_m \to \infty$, no base current) with emitter resistor $R_E$ (so $i_c = v_b/R_E$), feedback resistor $R_F$ from collector to base, load $R_L$. KCL at the collector: $v_c/R_L + v_b/R_E + (v_c-v_b)/R_F = 0$, so
$$A_v = \frac{v_c}{v_b} = \frac{R_L(R_E-R_F)}{R_E(R_F+R_L)},\qquad Z_{in} = \frac{R_F}{1-A_v} = \frac{R_E(R_F+R_L)}{R_E+R_L}.$$
Setting $Z_{in} = Z_0$ with $R_L = Z_0$ gives the **match condition $R_FR_E = Z_0^2$**; by symmetry $Z_{out} = Z_0$ too. With the input matched, $v_b = V_s/2$, so
$$S_{21} = A_v = 1 - \frac{R_F}{Z_0},\qquad |S_{21}| = \frac{R_F - Z_0}{Z_0}.$$
(Sympy derivation, script §1.) Design table for $Z_0$ = 50 Ω: $R_F$ = 250 → $R_E$ = 10 Ω, 12 dB; 500 → 5 Ω, 19.1 dB; 1000 → 2.5 Ω, 25.6 dB. Finite $g_m$ adds $1/g_m$ to $R_E$ (1.3 Ω at 20 mA — significant!), and finite loop gain lowers $|S_{21}|$ slightly. A single SiGe-like transistor with $R_F$ = 500 Ω, $R_E$ = 3.7 Ω (+1.3 Ω intrinsic) simulates at 18.5–18.7 dB with $|S_{11}|$ < −24 dB from 10 to 450 MHz, degrading to −10 dB at 2.5 GHz as $C_\pi$, $C_\mu$ and $r_b$ take over (script §1).

**Why MMIC gain blocks look the way they do.** The formulas above need a transistor with enormous $g_m$ and β — a Darlington pair supplies both (and the internal resistors also set DC bias). The whole thing is a two-terminal-plus-ground device whose output pin carries both RF and DC: you feed current through a resistor and choke from $V_{CC}$, $R_{bias} = (V_{CC}-V_d)/I_d$, where the device voltage $V_d$ falls ~2–3 mV/°C, so a larger $R_{bias}$ (≥ 2$V_d$ supply) holds $I_d$ steadier and makes dissipation fall as temperature rises; the choke must exceed ~500 Ω of reactance at the lowest frequency without resonating in-band [1]. Gain is flat because it is set by resistor ratios, and it rolls off where the transistor loop gain runs out (a few GHz for InGaP HBT parts).

**Open-circuit time constants (OCTC).** For an all-pole transfer function $1/(1+b_1s+b_2s^2+\dots)$ with widely spaced poles, the dominant pole is $\omega_{-3dB} \approx 1/b_1$, and $b_1 = \sum_iR_{i0}C_i$ where $R_{i0}$ is the resistance seen by capacitor $C_i$ with all *other* capacitors open [3][4]. For the CE stage (source $R_s$ + $r_b$ = $R_s'$ in parallel with $r_\pi$ = $R_s''$, load $R_L$):
$$R_{\pi0} = R_s'',\qquad R_{\mu0} = R_s'' + R_L + g_mR_s''R_L,$$
the last term being the Miller effect in OCTC form. Example ($R_s$ = 1 kΩ, $r_b$ = 50 Ω, $C_\pi$ = 10 pF, $C_\mu$ = 2 pF, $R_L$ = 5 kΩ): $R_{\pi0}$ = 873 Ω, $R_{\mu0}$ = 174.7 kΩ, $b_1$ = 358 ns → 0.444 MHz; ngspice gives 0.445 MHz (script §3). The breakdown tells you *which capacitor to attack*: here $C_\mu R_{\mu0}$ is 98 % of $b_1$ → cascode.

### Level 3 — limits and refinements
- **OCTC is conservative** (underestimates bandwidth) when zeros or complex poles exist; use short-circuit time constants for the low-frequency corner and simulate for anything with peaking.
- **Followers are not unconditionally stable:** an emitter follower with a capacitive load presents a negative real part at its input over a band near $f_T$ — the classic VHF parasitic oscillation (→ [feedback & stability](feedback-and-stability.md)).
- **Gain-bandwidth trade in feedback amplifiers:** for a single-pole core, gain × bandwidth is constant; for multistage cores the phase margin limits how much feedback can be applied.
- **Distortion in feedback amplifiers:** distortion is divided by (1+T) at frequencies where T is large — and returns as T falls with frequency. That is why op-amp distortion rises at high frequency (→ [op-amps](op-amps-real-limitations.md)).
- **Resistive-feedback noise:** $R_F$ adds noise at the input ($4kT/R_F$ current noise) and the match is resistive — gain blocks typically have NF ≈ 3–5 dB; use a dedicated LNA ahead of them for sensitivity-limited receivers (→ [receiver cascade](../07-noise-linearity/receiver-cascade-analysis.md)).
- **Distributed amplifiers** (transmission-line absorption of device capacitance) extend resistive-match bandwidth to tens of GHz — see the next subsection.

### Bandwidth extension and broadband amplifiers (peaking, T-coils, distributed, balanced, resistive-feedback LNAs)
Numbers are from `tools/verify/s3_bw_extension.py` (Python + ngspice; output in `_output.txt`). The baseline is a transconductor driving a load R in parallel with a capacitance C (device, pad, next-stage input). Its bandwidth is $f_0 = 1/(2\pi RC)$. All the techniques below use inductors or transmission lines to keep C from shorting the load, so that the same gain extends to a higher frequency. None of them increases the device's $f_T$.

**Shunt peaking** puts an inductor L in series with the load resistor. The R–L branch's impedance rises with frequency just as C starts to steal current. With $m = L/(R^2C)$, the load impedance is $Z = (R+sL)/(1+sRC+s^2LC)$:

| m | Bandwidth / $f_0$ | Peaking | Character |
|---|---|---|---|
| 0 | 1.00 | 0 | plain RC |
| 0.32 | 1.57 | 0 | flattest group delay (in-band delay spread 33 % vs 50 % for RC) |
| 0.414 ($\sqrt2-1$) | **1.72** | 0 | maximally flat magnitude (ngspice 1.722) |
| 0.5 | 1.80 | +0.25 dB | |
| 0.71 | 1.85 | +1.5 dB | maximum bandwidth, ringing on pulses |

Pick m ≈ 0.32 for pulses and eye diagrams (low overshoot) and m ≈ 0.41 for flat magnitude [4].

**Series peaking** places the inductor *between* two capacitances: the device's output capacitance $C_1$ and the load capacitance $C_2$ in parallel with R. The inductor then charges them one at a time. With $C_1 + C_2 = C$ fixed, a search for ≤ 0.1 dB peaking gives **3.68 ×** at $C_1/C$ = 0.55, m = 0.32 (ngspice 3.68 ×). The extension depends strongly on how C is split, so it is only available when the layout splits the capacitance naturally (pad vs device, die vs package).

**Bridged T-coil.** Two coupled inductors (coupling k) feed the load capacitance at their centre tap, with a bridging capacitor $C_B$ across the pair and R terminating the far end. With
$$2L(1+k) = R^2C,\qquad C_B = \frac{C(1-k)}{4(1+k)}$$
the input impedance is **exactly R at all frequencies** (ngspice: 1000.0 Ω flat), so the stage is matched as well as fast. The voltage on C has **2.83 × (2√2) the RC bandwidth at k = 1/3** with no peaking (2.72 × at k = 0.5; 2.77 × with 0.3 dB peaking at k = 0.2). T-coils are used for ESD-capacitance cancellation on high-speed I/O and for oscilloscope front ends. They need a coupled-inductor layout simulated in EM.

**Distributed (travelling-wave) amplifier.** Here the device capacitances *become* the shunt capacitors of two artificial transmission lines. The gate (input) line has a series L between taps with $C_{gs}$ at each tap; the drain (output) line likewise uses $C_{ds}$. Each line has $Z_0 = \sqrt{L/C}$ and cut-off $f_c = 1/(\pi\sqrt{LC})$. The input wave passes each device in turn, and each injects its current into the drain line, whose forward wave adds in phase if the two lines have equal phase velocity. The backward waves are absorbed in the drain-line reverse termination. Gain at low frequency:
$$|S_{21}| \approx \frac{n\,g_mZ_0}{2},$$
which grows *linearly* with the number of sections n, not exponentially as in a cascade. Line loss eventually limits n to about 4–8. ngspice (n = 4, $g_m$ = 20 mS, 0.5 pF, 50 Ω lines): |S21| = 2.00, exactly $ng_mZ_0/2$, flat to **12.8 GHz** (line cut-off 12.7 GHz). The same four devices in parallel as one lumped stage give |S21| = 4 but only 1.33 GHz, and a poor match. The distributed amplifier therefore trades half the gain for about 10 × the bandwidth, and it is matched to 50 Ω across the band [8][4]. This is how DC–20+ GHz MMIC amplifiers are built. Pozar's treatment includes line loss [9].

**Balanced amplifier.** Two identical amplifiers sit between two 90° hybrids (branch-line or Lange couplers; → [couplers](../06-rf-circuits/couplers-dividers-combiners.md)). The input hybrid splits the signal with 0°/−90°. Each amplifier's reflection returns through the hybrid with an extra 90°, so at the input port the two reflections cancel and they add in the hybrid's isolated (terminated) port. The output hybrid recombines the outputs in phase. For identical amplifiers [10]:
$$S_{11,bal} = \tfrac12(S_{11A} - S_{11B}) \to 0,\qquad S_{21,bal} = -j\tfrac12(S_{21A}+S_{21B}) \to -jS_{21A}.$$
ngspice at 433 MHz, with each amplifier deliberately mismatched ($R_{in}$ = 25 Ω, |S11| = −9.5 dB, gain 10 dB): balanced |S11| < −100 dB at the centre and ≤ −15.8 dB over ±10 %, limited by the branch-line bandwidth; gain 10.00 dB, unchanged. Consequences:
- each amplifier can be tuned for minimum NF or maximum power *without regard for its own input match*;
- output power and P1dB/IP3 rise by 3 dB;
- if one amplifier fails the gain drops by about 6 dB but the link survives;
- a mismatched antenna's reflection is dumped into the hybrid terminations instead of returning to the devices.

The costs are two hybrids (≈ 0.2–0.5 dB loss each, which adds directly to NF at the input) and twice the current.

**Resistive-feedback wideband LNAs.** The gain block of Level 2 used as an LNA. Its noise has three parts: $R_F$ injects $4kT/R_F$ of current noise at the input (≈ $R_s/R_F$ of excess noise factor, 0.41 dB for 500 Ω), plus the transistor's $r_b$, $R_E$ and shot noise. ngspice `.noise` on the single-SiGe-transistor stage of Worked example 1 gives **NF = 1.77 dB at 433 MHz**. That is good for a decade-wide matched stage, though worse than a narrowband inductively degenerated LNA (≈ 0.5–1 dB → [LNA design](../06-rf-circuits/lna-design.md)). Darlington MMIC gain blocks are typically 3–5 dB. Shunt-feedback (or noise-cancelling) CMOS LNAs use the same idea for multiband receivers. Raising $R_F$ lowers the noise but also raises the gain, and the gain must stay low enough for the match condition $R_FR_E = Z_0^2$.

**Why an LNA is a poor transmitter driver.** An LNA is a class-A stage biased for noise, not power. Its linear output is capped at about $\tfrac12V_{pk}I_{bias}$, and into a 50 Ω load at only $\tfrac12I_{bias}^2\cdot50$ Ω:
- **A 3 V, 5 mA LNA** has an ideal ceiling of 8 dBm with an optimum 500 Ω load, but only −2 dBm into 50 Ω. The BGA524N6 GNSS LNA's real OP1dB is ≈ +2.6 dBm (19.6 dB gain, IP1dB −16 dBm; [canonical values](../00-math-foundations/canonical-values-and-conventions.md)). A 2 W PA module or discrete PA needing 0–20 dBm of drive would push it into compression, and then harmonics, spectral regrowth and AM-PM fail the emission mask.
- **Its input and output are matched for noise**, not conjugately. It is often only conditionally stable, and a PA input whose impedance changes with drive level can make it oscillate.
- **Its bias, thermal design and ESD structures assume µW signals.** A driver stage (gain block or driver amplifier at 5 V, 60 mA: 20.8 dBm ideal ceiling) is the right part. Use the transceiver's own PA output, or a gain block of the [18 MMIC table](../18-components-parts/lna-pa-gain-block-mmics.md) with OP1dB ≥ the required drive + 6–10 dB of back-off.

### Output stages — class A, class B and class AB push-pull
Numbers are from `tools/verify/s3_bw_extension.py` §7 (ngspice, ±5 V, 100 Ω load, 2 V peak, 1 kHz). An op-amp, audio amplifier or line driver ends in an output stage that must source and sink load current with low output impedance:
- **Class A.** A single follower biased by a resistor or current source conducts all the time. It is linear, but the bias current must exceed the peak load current, so a resistor-biased follower is at most 25 % efficient (50 % with an inductor or transformer load).
- **Class B.** A complementary NPN/PNP emitter-follower pair (push-pull) conducts one transistor per half-cycle. Ideal efficiency is $\frac{\pi}{4}\frac{V_p}{V_{CC}}$: 79 % at full swing, 31 % at 2 V on ±5 V. With no bias, both transistors are off for |input| < $V_{BE}$ ≈ 0.6 V. That **crossover dead band** gives THD = **22 %** in the simulation, and the fundamental falls to 1.12 V peak.
- **Class AB.** Pre-bias the bases about two $V_{BE}$ apart (two diodes, or a $V_{BE}$ multiplier on the same heatsink so that the bias tracks temperature), with small emitter resistors (here 1 Ω) to stabilise the quiescent current. In the simulation THD falls to **0.42 %** with 2 mA bias, and the fundamental is 1.92 V peak. Negative feedback around the stage, as inside every op-amp, reduces the remainder. Thermal runaway (→ [BJT bias](bjt-fundamentals-small-signal.md)) is the class-AB design risk, which is why the bias element must be thermally coupled.
- **Rail-to-rail CMOS outputs** use common-source devices instead of followers, so the swing reaches the rails at light load, at the cost of a higher output impedance. **Open-drain/collector** outputs (comparators, I²C) sink only (→ [comparators](analog-signal-conditioning.md#comparators-schmitt-triggers-and-timers)).

RF power amplifiers reuse the same class letters with resonant loads (→ [power amplifiers](../06-rf-circuits/power-amplifiers.md)).

## Design equations & rules of thumb

| Quantity | Equation | Valid when | Typical |
|---|---|---|---|
| Degenerated transconductance | $g_m/(1+g_mR_E)$ | — | ≈ $1/R_E$ |
| Degenerated CE gain | $-R_C/(r_e+R_E)$ | $\beta \gg 1$ | resistor-ratio gain |
| CB input resistance | $1/g_m$ | — | 50 Ω at 0.52 mA |
| CB/CG matched NF | $1+1/(2g_mR_s)$ / $1+\gamma/\alpha$ | resistive match | 1.8 / 2.2 dB |
| Follower output resistance | $1/g_m + R_s/(\beta+1)$ | — | tens of Ω |
| Cascode $R_{out}$ | $\beta r_o$ (BJT), $g_mr_o^2$ (MOS) | — | MΩ |
| Diff-pair linear range | ±$2V_T$ ≈ ±50 mV (×(1+$g_mR_E$) degenerated) | — | — |
| Diff-pair CMRR | $2g_mR_{EE}$ | — | 60–100 dB |
| IIP3 amplitude, exp | $\sqrt8\,V_T(1+x)^2/\sqrt{|1-2x|}$ | LF, $x = g_mR_E$ | 73 mV at $x$ = 0 |
| IIP3 amplitude, diff pair | $4V_T$ | undegenerated | 103 mV |
| Simple mirror ratio | $1/(1+2/\beta)$ | — | 0.99 |
| Widlar | $I_oR_E = V_T\ln(I_{ref}/I_o)$ | — | — |
| Darlington | $\beta_1\beta_2$; $g_m = g_{m2}/2$ | no bleeder | — |
| Gain-block match | $R_FR_E = Z_0^2$ | high loop gain | 500 Ω · 5 Ω |
| Gain-block gain | $|S_{21}| = (R_F - Z_0)/Z_0$ | matched | 19.1 dB @ 500 Ω |
| MMIC bias | $R_{bias} = (V_{CC}-V_d)/I_d$; choke $X_L$ > 500 Ω | — | $V_{CC} \ge 2V_d$ [1] |
| OCTC bandwidth | $\omega_{-3dB} \approx 1/\sum R_{i0}C_i$ | dominant pole | — |
| Feedback | $A = a/(1+T)$; $Z$ ×/÷ (1+T) | — | error ≈ 1/T |
| Shunt peaking | $m = L/(R^2C)$ | 0.32 flat delay / 0.414 flat magnitude | 1.57 × / 1.72 × |
| Series peaking | L between $C_1$ and $C_2\|R$ | split-dependent | up to ≈ 3.7 × (≤ 0.1 dB) |
| Bridged T-coil | $2L(1+k) = R^2C$, $C_B = C(1-k)/4(1+k)$ | constant $Z_{in}$ = R | 2.83 × at k = 1/3 |
| Distributed amp | $\lvert S_{21}\rvert ≈ ng_mZ_0/2$, $f_c = 1/(\pi\sqrt{LC})$ | lossless lines | n ≈ 4–8 |
| Balanced amp | $S_{11} = (S_{11A}-S_{11B})/2$, $S_{21} = -j(S_{21A}+S_{21B})/2$ | identical amps | +3 dB P1dB; −6 dB if one fails |
| Class-A output ceiling | $\tfrac12V_{pk}I_{bias}$; into 50 Ω $\tfrac12I_{bias}^2\cdot50$ | — | −2 dBm at 5 mA |
| Class-B efficiency | $\tfrac{\pi}{4}V_p/V_{CC}$ | ideal | 78.5 % max |

## Worked examples

### 1. Designing a 50 Ω, 19 dB feedback gain stage for 50–500 MHz
Goal: a discrete gain stage between a 433 MHz SAW filter and an SDR input.
1. Gain target 19 dB → $|S_{21}|$ = 9 → $R_F = Z_0(1+9)$ = 500 Ω.
2. Match: $R_E' = Z_0^2/R_F$ = 5 Ω total. Choose $I_C$ = 20 mA → $1/g_m$ = 1.3 Ω, so the external $R_E$ = 3.7 Ω (use 3.9 Ω, or two 7.5 Ω in parallel to halve ESL).
3. Device: $f_T$ ≫ 10 × 500 MHz for enough loop gain; a SiGe HBT (e.g. BFP740 class at reduced current, or a BFR-class device if the band stops at a few hundred MHz).
4. DC: collector from 8 V through 150 Ω + choke (≈ 5 V at the collector); base divider from the collector through a separate choke so it does not load the RF (DC feedback stabilises $I_C$); DC-block $R_F$ with a capacitor.
5. Result (ngspice, script §1): 18.5–18.7 dB, $|S_{11}|$ −27 to −24 dB up to 450 MHz, −18 dB at 900 MHz. The 0.5 dB shortfall vs ideal comes from finite loop gain ($r_b$, β).
6. Alternative: a catalogue MMIC gain block does all of this in SOT-89 with better flatness; bias it from 5 V with $R_{bias} = (5 - V_d)/I_d$ — e.g. for $V_d$ = 3.3 V and $I_d$ = 35 mA, 49 Ω (check $V_{CC} \ge 2V_d$ guidance [1]; with 5 V you will see more drift than from 7–8 V).

### 2. Where the bandwidth goes in a CE stage — and the cascode fix
From the OCTC example: 98 % of $b_1$ is $C_\mu R_{\mu0}$ (Miller). Add a cascode: Q1's collector now sees ≈ $1/g_{m2}$ ≈ 26 Ω, so $R_{\mu0,Q1} = R_s'' + 26 + g_mR_s''\cdot26$ ≈ 1.8 kΩ instead of 175 kΩ. The new dominant terms are $C_\pi R_s''$ (8.7 ns) and Q2's $C_\mu$ at the output ($C_\mu R_L$ = 10 ns), so $b_1$ ≈ 22 ns → ≈ 7 MHz: a 16× bandwidth improvement at the same gain.

### 3. Linearising an IF stage by degeneration
An undegenerated BJT at 1 mA has $A_{IIP3}$ = 73 mV peak. With $R_E$ = 100 Ω ($x$ = 3.87): ratio $(4.87)^2/\sqrt{6.74}$ = 9.1 → 668 mV, at the cost of gain dropping by (1+x) = 4.87 (13.8 dB). Net: IIP3 up 19 dB, gain down 13.8 dB → OIP3 up ≈ 5 dB. Linearity per unit gain improves because the feedback suppresses distortion more than gain.

## Practical notes
- **Bypass capacitors are part of the topology.** An emitter bypass capacitor's ESL at UHF leaves unintended degeneration and can create negative input resistance; at RF prefer grounded emitters with collector-feedback bias.
- **Followers into cables or ADC inputs** need a series resistor (tens of Ω) at the output to isolate capacitive load.
- **Differential signalling** on PCBs (ADC inputs, mixer IFs) exploits the pair's CMRR — keep the two paths symmetric (→ [mixed-signal layout](../13-pcb-rf-layout-emc/mixed-signal-layout.md)).
- **MMIC gain blocks:** mount on a solid ground with multiple vias under the ground pads; bias chokes need SRF above the top frequency (→ [inductors at RF](../04-real-components-hf/inductors-at-rf.md)); watch dissipation ($V_d\cdot I_d$, plus $I_d^2R_{bias}$ in the resistor).
- **Mirrors and ratios:** thermal coupling matters — use dual transistors or ICs for accurate mirrors; add emitter resistors (degeneration) to reduce $V_{BE}$ mismatch effects.

## Common mistakes & misconceptions
- **"A common-base stage has no gain."** It has current gain ≈ 1 but full voltage gain $g_mR_L$; it is a current buffer.
- **Forgetting that a follower's output impedance includes the source impedance divided by β.** Driving a follower from 100 kΩ gives ~500 Ω output, not 26 Ω.
- **Using a Darlington MMIC gain block as an LNA** — NF 3–5 dB; good for gain after the LNA, not before. (A single high-$f_T$ transistor with resistive feedback can reach ≈ 1.8 dB — ngspice, Bandwidth-extension section — still behind a narrowband LNA.)
- **Biasing an MMIC gain block straight from a regulator without a resistor.** They are current-controlled devices; a voltage source can cause thermal runaway [1].
- **Assuming degeneration always reduces IM3 monotonically.** The exact behaviour has a null and a $\sqrt{|1-2x|}$ term; small $R_E$ can move you across the null (phase flip of IM3).
- **Expecting peaking to beat the device limit.** Peaking redistributes the RC charging; it cannot exceed $f_T$-related limits, and over-peaking (m > 0.5) rings on pulses.
- **Adding stages to a distributed amplifier for more gain.** Its gain grows only linearly with n, and line loss soon wins; cascade two DAs instead.
- **Judging a balanced amplifier's devices by the input return loss.** The hybrid hides each amplifier's mismatch, including a failed or oscillating half; check the isolated-port power.
- **Driving a PA with an LNA or "a spare gain block of any kind".** Check OP1dB against the required drive plus back-off.
- **Unbiased (class-B) complementary followers** in linear circuits — crossover distortion at every zero crossing.
- **Thinking feedback extends bandwidth for free** — it trades gain; and with multiple poles, too much loop gain causes peaking and oscillation.

## How to simulate / verify
- **Python + ngspice:** `tools/verify/analog_topologies.py` — sympy derivation of the gain-block equations; ngspice S21/S11 of a real-transistor feedback stage; OCTC vs ngspice exact pole; two-tone IIP3 of exp, tanh and degenerated stages vs the closed forms; CB noise; mirror/Darlington checks; feedback scaling.
- **The gain-block netlist** (ngspice/LTspice):
```spice
* single-transistor resistive-feedback gain block, RF=500, RE=3.7 (+1/gm ~1.3), 50-ohm ports
.model QS NPN(IS=5e-16 BF=250 VAF=30 TF=2.5p CJE=0.3p CJC=0.08p RB=5 RE=0 RC=2)
VCC vcc 0 DC 8
Rbias vcc ch 150
Lch ch c 10u
Q1 c b e QS
RE e 0 3.7
RF c bf 500
CF bf b 100n
RB1 c bb 10k
LB bb b 10u
RB2 b 0 2.65k
Vin src 0 DC 0 AC 1
Rsrc src in 50
Cin in b 100n
Cout c out 100n
Rload out 0 50
.ac dec 20 1MEG 20G
.end
```
  $S_{21} = 2v_{out}/v_{src}$; $Z_{in} = v_{in}/[(v_{src}-v_{in})/50]$.
- **Bandwidth extension and output stages:** `tools/verify/s3_bw_extension.py` (+ `_output.txt`) — shunt-peaking table and ngspice check; series-peaking optimum; bridged T-coil constant-R input and bandwidth; 4-section distributed amplifier vs a lumped stage; branch-line balanced amplifier S11/S21; `.noise` NF of the gain block; class-B vs class-AB THD; class-A output ceiling of an LNA.
- **Two-tone IIP3 in SPICE:** two sine sources at $f_1$, $f_2$, long `.tran`, FFT of the output; or harmonic balance in Qucs-S.
- **Bench:** NanoVNA for S21/S11 of gain stages; two signal generators + combiner + spectrum analyser (or SDR) for IM3 (→ [test & measurement](../17-test-measurement/spectrum-analyzers.md)).

## Open questions / gaps
- The degeneration IM3 null at $g_mR_E$ = 1/2 is derived for an ideal exponential at low frequency; not yet checked against measured data or a textbook statement.
- Distributed-amplifier section uses lossless artificial lines; line loss, gate-line attenuation and the optimum number of sections are not derived (→ Pozar [9]).
- Bridged T-coil formulas are verified numerically (constant-R input) rather than derived here.
- Specific MMIC gain-block part data (Vd, Id, NF, OIP3) left to [18 gain-block MMICs](../18-components-parts/lna-pa-gain-block-mmics.md).

## Sources
1. Mini-Circuits, *AN-60-010: Biasing of constant current MMIC amplifiers (e.g., ERA series)*. https://www.minicircuits.com/appdoc/AN60-010.html — Darlington-in-resistive-feedback structure, $R_{bias} = (V_{CC}-V_d)/I_{bias}$, $V_d$ tempco −2 to −3 mV/°C, choke > 500 Ω, $V_{CC} \ge 2V_d$. (app note)
2. P. R. Gray, P. J. Hurst, S. H. Lewis, R. G. Meyer, *Analysis and Design of Analog Integrated Circuits*, 5th ed., Wiley 2009 — ch. 3 (single-stage and cascode amplifiers, differential pair tanh law), ch. 4 (current mirrors, Widlar, Wilson), ch. 5 (Darlington), ch. 8 (feedback), ch. 11 (noise of CB/CG stages). (textbook)
3. A. S. Sedra, K. C. Smith, *Microelectronic Circuits*, 7th ed., Oxford 2015 — ch. 7–10 (basic stages, cascode, differential pair, feedback topologies, open-circuit time constants). (textbook)
4. T. H. Lee, *The Design of CMOS Radio-Frequency Integrated Circuits*, 2nd ed., Cambridge 2004 — ch. 9 (OCTC/SCTC bandwidth estimation), ch. 12 (LNA noise of common-gate). (textbook)
5. B. Razavi, *Design of Analog CMOS Integrated Circuits*, 2nd ed., McGraw-Hill 2017 — ch. 3–5 (CS/CG/CD, cascode, differential pair, mirrors), ch. 8 (feedback). (textbook)
6. P. Horowitz, W. Hill, *The Art of Electronics*, 3rd ed., Cambridge 2015 — ch. 2 (practical transistor stages, Darlington, mirrors, differential amplifiers), ch. 2x/x-chapters on RF gain blocks. (textbook)
7. G. Gonzalez, *Microwave Transistor Amplifiers: Analysis and Design*, 2nd ed., Prentice Hall 1997 — ch. 4 (broadband feedback and balanced amplifiers). (textbook)
8. E. L. Ginzton, W. R. Hewlett, J. H. Jasberg, J. D. Noe, "Distributed amplification," *Proc. IRE* 36(8), 956–969, 1948 — the travelling-wave amplifier, gain ≈ n g_m Z_0/2. (peer-reviewed)
9. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley 2012 — §12.4 (broadband amplifiers: balanced, distributed with line loss, differential). (textbook)
10. K. Kurokawa, "Design theory of balanced transistor amplifiers," *Bell System Technical Journal* 44(8), 1675–1698, 1965 — balanced amplifier S-parameters with quadrature hybrids. (peer-reviewed)
