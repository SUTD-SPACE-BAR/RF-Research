---
title: Low-noise amplifier (LNA) design
domain: 06-rf-circuits
slug: lna-design
tags: [lna, noise-figure, noise-circles, gain-circles, transducer-gain, available-gain, simultaneous-conjugate-match, inductive-degeneration, phemt, atf-54143, gnss, lora, 433mhz, 1575mhz, induced-gate-noise, power-constrained-noise-optimisation, noise-cancelling, balun-lna, cmos-lna]
prerequisites:
  - amplifier-stability-and-biasing.md
  - ../03-transmission-lines-matching/s-parameters.md
  - ../03-transmission-lines-matching/smith-chart.md
  - ../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md
  - ../07-noise-linearity/noise-figure-and-friis.md
related:
  - rf-filters-lc-saw-baw-cavity-microstrip.md
  - rf-switches-attenuators-limiters.md
  - receiver-architectures.md
  - couplers-dividers-combiners.md
  - ../07-noise-linearity/thermal-noise-and-noise-temperature.md
  - ../07-noise-linearity/receiver-cascade-analysis.md
  - ../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md
  - ../04-real-components-hf/inductors-at-rf.md
  - ../15-lora-ism-radios/ground-station-design.md
  - ../20-projects-recipes/lna-design-walkthrough.md
  - ../20-projects-recipes/gnss-front-end-design.md
  - ../17-test-measurement/noise-figure-measurement.md
level: mixed
confidence: high
last_updated: 2026-10-14
---

# Low-noise amplifier (LNA) design

## Questions this page answers
- What is the difference between transducer, available, operating and maximum available gain?
- What are noise parameters (Fmin, Γopt, Rn) and how do I use them?
- Why can't I have minimum noise figure and a perfect input match at the same time — and how do people get both?
- How do I draw noise circles and gain circles and choose a source impedance?
- How does inductive source degeneration give a real 50 Ω input without a noisy resistor?
- How do I design a discrete pHEMT LNA for 433 MHz or for GPS L1 (1575.42 MHz), step by step?
- Why does my LNA need a resistor or feedback if I want it stable?
- How much does inductor Q matter for LNA noise figure?
- Should the LNA go before or after the SAW filter?
- Does my LoRa ground station actually benefit from an LNA, and where should it go?
- Which ready-made LNA MMICs are good at 433 MHz and at GNSS L1?
- How much power will destroy an LNA, and how close can the rocket's transmitter be?
- What is induced gate noise, and why does a MOSFET have a nonzero minimum noise figure?
- How wide should the transistor in a CMOS LNA be for a given current budget?
- How do noise-cancelling (CG–CS / balun) wideband LNAs beat the 1 + γ/α limit of a common-gate input?

## TL;DR
- **Noise is set by the source impedance the transistor sees**, not by the input return loss: $F=F_{min}+\frac{R_n}{G_s}|Y_s-Y_{opt}|^2$. The best source reflection $\Gamma_{opt}$ is generally *not* $S_{11}^*$, so a noise-matched LNA typically has 8–10 dB input return loss unless you use feedback (source inductance) or a balanced design.
- **Four gains**: transducer $G_T$ (what you measure between 50 Ω ports), available $G_A$ (depends only on $\Gamma_S$; used with noise circles), operating $G_{power}$ (textbook $G_P$; depends only on $\Gamma_L$; not the processing gain $G_{proc}$ of [spread spectrum](../10-comms-modulation/spread-spectrum-dsss-fhss-css.md)), and MAG (simultaneous conjugate match, needs K>1). $G_T\le G_A,G_{power}\le$ MAG.
- **Noise circles** (centre $\Gamma_{opt}/(N+1)$, radius $\sqrt{N(N+1-|\Gamma_{opt}|^2)}/(N+1)$, $N=\frac{F-F_{min}}{4R_n/Z_0}|1+\Gamma_{opt}|^2$) and **available-gain circles** on the same Smith chart show the NF–gain trade. Low $R_n$ (pHEMTs: ≈ 2 Ω for the ATF-54143) makes noise circles huge — noise match is forgiving; losses dominate.
- **Inductive source degeneration** makes $\mathrm{Re}\,Z_{in}=\omega_TL_s$ without resistor noise. For a CMOS FET the channel-noise contribution is $F-1=\gamma g_{d0}R_s(\omega_0/\omega_T)^2$ (derived & verified), but in practice the **gate-inductor loss** dominates: a 51 nH, Q = 20 gate inductor at 1575 MHz alone costs ≈ 1.8 dB.
- For a discrete pHEMT, 0.5 nH of source inductance at 1575 MHz moves $S_{11}^*$ onto $\Gamma_{opt}$ (distance 0.52 → 0.05) with NFmin unchanged (0.348 → 0.344 dB) — but it lowers high-frequency stability.
- Verified designs (ATF-54143, 3 V/60 mA, real data-sheet S/noise data, realistic 0603/0402 parts, unconditionally stable 0.1–10 GHz, 100 % stable in ±5 % tolerance Monte Carlo): **433 MHz: NF 0.38 dB, G 22.1 dB** (needs 1.5 kΩ + 82 pF drain-gate feedback); **1575.42 MHz: NF 0.74 dB, G 19.2 dB**. MMIC alternatives: Mini-Circuits PGA-103+ (433 MHz: 22.1 dB, NF 0.5 dB, OIP3 +39 dBm), Infineon BGA524N6 (GNSS: 19.6 dB, 0.55 dB, 2.5 mA).
- **Placement**: put the LNA before cable loss (masthead). For a 433 MHz LoRa ground station with 3 dB of cable and an SX126x (implied NF ≈ 6 dB), a masthead LNA takes system NF from 9.0 dB to 0.55 dB — 8.5 dB SNR or ×2.7 free-space range if the antenna sees 290 K, but only 4.6 dB if man-made noise raises $T_{ant}$ to 1000 K.
- **Protect it**: GNSS LNAs are often rated for only 0 dBm input (BGA524N6). A 2 W, 433 MHz transmitter 10 m from a 10 dBi Yagi already delivers ≈ 0 dBm; at 3 m, ≈ +10 dBm.

## Intuition (no math)
An LNA has one job: raise the signal above the noise of everything that follows *while adding as little noise of its own as possible*. Because later stages' noise is divided by the LNA gain (Friis), the first stage's noise figure dominates the whole receiver (see [noise figure and Friis](../07-noise-linearity/noise-figure-and-friis.md)).

A transistor's internal noise can be pictured as two noise generators at its input: a noise *voltage* in series and a noise *current* in parallel, partly correlated. With a very low source impedance the voltage generator dominates; with a very high one the current generator dominates. Somewhere in between — at the complex optimum $Z_{opt}$ — their combined effect relative to the source's own thermal noise is smallest. That minimum is $F_{min}$. $R_n$ tells you how quickly things get worse as you move away from $Z_{opt}$.

Nothing forces $Z_{opt}$ to equal the impedance that gives maximum power transfer (the conjugate of the input impedance). The physics of noise and the physics of signal gain are different, so the noise-optimum and gain-optimum points on the Smith chart are usually some distance apart. Designing an LNA is choosing a point between them — and adding feedback that moves them together.

Losses before the transistor are fatal: a lossy input matching network is a resistor at room temperature adding thermal noise *before* any gain. 0.3 dB of loss in the input inductor adds 0.3 dB to the noise figure. That is why LNA designers obsess over inductor Q, why they avoid resistors at the input, and why the best place for the LNA is right at the antenna, before any cable or filter loss.

## The math

### Level 1 — gains, noise parameters, and the design targets

**Power gains** (Pozar §12.1 [1]; waves referenced to $Z_0$; $\Gamma_{in},\Gamma_{out}$ as in [stability](amplifier-stability-and-biasing.md)):
$$G_T=\frac{P_L}{P_{avs}}=\frac{(1-|\Gamma_S|^2)\,|S_{21}|^2\,(1-|\Gamma_L|^2)}{|1-\Gamma_S\Gamma_{in}|^2\,|1-S_{22}\Gamma_L|^2}$$
$$G_A=\frac{P_{avn}}{P_{avs}}=\frac{(1-|\Gamma_S|^2)|S_{21}|^2}{|1-S_{11}\Gamma_S|^2(1-|\Gamma_{out}|^2)},\qquad G_{power}=\frac{P_L}{P_{in}}=\frac{|S_{21}|^2(1-|\Gamma_L|^2)}{(1-|\Gamma_{in}|^2)|1-S_{22}\Gamma_L|^2}$$
With 50 Ω terminations ($\Gamma_S=\Gamma_L=0$) $G_T=|S_{21}|^2$. Since $P_L\le P_{avn}$ and $P_{in}\le P_{avs}$, $G_T\le G_A$ and $G_T\le G_{power}$.

**Two-port noise** (Rothe–Dahlke/IRE representation [2]): with source admittance $Y_s=G_s+jB_s$,
$$F=F_{min}+\frac{R_n}{G_s}\,|Y_s-Y_{opt}|^2\quad\Longleftrightarrow\quad F=F_{min}+\frac{4R_n}{Z_0}\frac{|\Gamma_s-\Gamma_{opt}|^2}{(1-|\Gamma_s|^2)\,|1+\Gamma_{opt}|^2}$$
$F_{min}$ (linear; NF in dB = $10\log F$), $\Gamma_{opt}$ (or $Y_{opt}$), and $R_n$ (Ω) are the four real **noise parameters**. Data sheets list them per frequency; e.g. ATF-54143 at 3 V/60 mA, 1.9 GHz: NFmin 0.42 dB, $\Gamma_{opt}=0.27\angle116°$, $R_n/50=0.04$ [3].

**Design targets for an LNA:** $\Gamma_S$ near $\Gamma_{opt}$ (noise); $\Gamma_L$ chosen for gain/output match ($\Gamma_L=\Gamma_{out}^*$ gives maximum $G_T$ for that $\Gamma_S$); unconditional stability over all frequencies with gain; linearity (IIP3, P1dB) adequate for the strongest interferers.

### Level 2 — derivations

**(a) Transducer gain.** Model the source as a wave generator $b_s$ with reflection $\Gamma_S$; the available power is $P_{avs}=|b_s|^2/(1-|\Gamma_S|^2)$. The wave into the amplifier is $a_1=b_s/(1-\Gamma_S\Gamma_{in})$ (multiple reflections between source and input sum as a geometric series). With the load, $b_2=S_{21}a_1/(1-S_{22}\Gamma_L)$, and $P_L=|b_2|^2(1-|\Gamma_L|^2)$. Dividing gives $G_T$ above; the script checks the closed form against this wave computation to $10^{-15}$ (check A1).

**(b) Available gain** is $G_T$ with the load conjugately matched to the output ($\Gamma_L=\Gamma_{out}^*$); substituting and simplifying with $\Gamma_{out}=S_{22}+S_{12}S_{21}\Gamma_S/(1-S_{11}\Gamma_S)$ gives $G_A$ — a function of $\Gamma_S$ only, which is why it pairs naturally with noise circles (also a function of $\Gamma_S$ only).

**(c) Simultaneous conjugate match (SCM).** Requiring $\Gamma_S=\Gamma_{in}^*(\Gamma_L)$ and $\Gamma_L=\Gamma_{out}^*(\Gamma_S)$ leads to a quadratic for each [1 §12.3]:
$$\Gamma_{MS}=\frac{B_1\pm\sqrt{B_1^2-4|C_1|^2}}{2C_1},\quad \Gamma_{ML}=\frac{B_2\pm\sqrt{B_2^2-4|C_2|^2}}{2C_2}$$
$B_1=1+|S_{11}|^2-|S_{22}|^2-|\Delta|^2$, $B_2=1+|S_{22}|^2-|S_{11}|^2-|\Delta|^2$, $C_1=S_{11}-\Delta S_{22}^*$, $C_2=S_{22}-\Delta S_{11}^*$; take the root with $|\Gamma|<1$ (minus sign when $B>0$). A passive solution exists iff $K>1$ and $|\Delta|<1$, and then $G_T=\text{MAG}=|S_{21}/S_{12}|(K-\sqrt{K^2-1})$ (check B1).

**(d) Noise circles.** Setting $F$ constant in the Γ form of the noise equation and defining
$$N=\frac{F-F_{min}}{4R_n/Z_0}\,|1+\Gamma_{opt}|^2$$
gives $|\Gamma_s-\Gamma_{opt}|^2=N(1-|\Gamma_s|^2)$. Expanding and completing the square:
$$\left|\Gamma_s-\frac{\Gamma_{opt}}{N+1}\right|^2=\frac{N\left(N+1-|\Gamma_{opt}|^2\right)}{(N+1)^2}$$
a circle with centre $C_F=\Gamma_{opt}/(N+1)$ and radius $R_F=\sqrt{N(N+1-|\Gamma_{opt}|^2)}/(N+1)$ [1 §12.3]. As $F\to F_{min}$ the circle shrinks to the point $\Gamma_{opt}$; the centres all lie on the line from the origin to $\Gamma_{opt}$. Because $N\propto1/R_n$, a small $R_n$ gives big circles (forgiving). Check C1 evaluates $F$ at 72 points on each circle with an independent noise-correlation engine: error $<10^{-15}$.

**(e) Available-gain circles.** With $g_a=G_A/|S_{21}|^2$: centre $C_A=\dfrac{g_aC_1^*}{1+g_a(|S_{11}|^2-|\Delta|^2)}$, radius $R_A=\dfrac{\sqrt{1-2K|S_{12}S_{21}|g_a+|S_{12}S_{21}|^2g_a^2}}{|1+g_a(|S_{11}|^2-|\Delta|^2)|}$ (check C2).

**(f) Unilateral approximation.** If $S_{12}\approx0$, $G_{TU}=\frac{1-|\Gamma_S|^2}{|1-S_{11}\Gamma_S|^2}|S_{21}|^2\frac{1-|\Gamma_L|^2}{|1-S_{22}\Gamma_L|^2}$, and the error is bounded by $\frac{1}{(1+U)^2}<\frac{G_T}{G_{TU}}<\frac{1}{(1-U)^2}$ with $U=\frac{|S_{11}S_{12}S_{21}S_{22}|}{(1-|S_{11}|^2)(1-|S_{22}|^2)}$. For the ATF-54143 at 1575 MHz, $U=0.106$ → −0.87 to +0.97 dB: the unilateral shortcut is not accurate enough for a high-gain FET (check D).

**(g) Inductive source degeneration** (the CMOS LNA workhorse; Shaeffer & Lee [4], Razavi [5 ch.5]). Model: gate inductor $L_g$, gate–source capacitance $C_{gs}$, transconductance $g_m$, source inductor $L_s$; drain output shorted (cascode). Let $i_g$ be the gate current. The source node carries $i_g$ plus the drain current $g_mv_{gs}+i_d$ ($i_d$ = channel noise), so $v_s=j\omega L_s(i_g+g_mv_{gs}+i_d)$ with $v_{gs}=i_g/(j\omega C_{gs})$. Around the input loop:
$$v_{src}=i_g\Big[R_s+j\omega(L_g+L_s)+\frac{1}{j\omega C_{gs}}+\underbrace{\frac{g_mL_s}{C_{gs}}}_{=\omega_TL_s}\Big]+j\omega L_si_d$$
So $Z_{in}=j\omega(L_g+L_s)+\frac{1}{j\omega C_{gs}}+\omega_TL_s$, with $\omega_T=g_m/C_{gs}$: **a real part without a resistor**. Choose $L_s=R_s/\omega_T$ and $L_g+L_s=1/(\omega_0^2C_{gs})$. At resonance $i_g=(v_{src}-j\omega_0L_si_d)/(2R_s)$ and the output current is
$$i_{out}=\frac{g_m i_g}{j\omega_0C_{gs}}+i_d=\frac{\omega_T}{j2\omega_0R_s}v_{src}+\frac{i_d}{2}$$
Two results: the effective transconductance is $G_m=\omega_T/(2\omega_0R_s)$ (the input network's voltage gain $Q_{in}=1/(2\omega_0C_{gs}R_s)$ multiplies $g_m$), and the degeneration feedback **halves** the channel-noise current at the output. With $\overline{i_d^2}=4kT\gamma g_{d0}$ and $\overline{v_{src}^2}=4kTR_s$:
$$F=1+\gamma g_{d0}R_s\left(\frac{\omega_0}{\omega_T}\right)^2\qquad(\text{channel noise only})$$
Adding gate-induced noise (correlated with $i_d$) gives Shaeffer–Lee's full result, whose *power-constrained* optimum is quoted as $F_{min,P}\approx1+2.4\frac{\gamma}{\alpha}\frac{\omega_0}{\omega_T}$ for long-channel values [4]. An exact nodal solve gives ≈ 2.0 instead of 2.4 at the optimum $Q_L\approx3.8$, and this is distinct from the device's $F_{min}$ (Level 3b). Losses in $L_g$ add $R_{Lg}/R_s$ directly. All three closed forms are checked against a direct circuit solve (checks E1–E3).

### Level 3 — invariants, limits, and alternative topologies

- **Lossless feedback and noise.** Series (source) inductance is lossless feedback: it adds nothing to the noise correlation matrix in impedance form, so it barely changes $F_{min}$ but rotates $S_{11}$. For the ATF-54143 at 1575 MHz, 0.5 nH moves $S_{11}^*$ from $0.64\angle153°$ to $0.23\angle117°$, onto $\Gamma_{opt}=0.24\angle106°$ (check J). The general statement is Haus & Adler's: the **minimum noise measure** $M=(F-1)/(1-1/G_A)$ is invariant under lossless embedding [6] — so feedback can make noise match and power match coincide but cannot beat the device's intrinsic noise measure. Cost: less gain and, as the [stability page](amplifier-stability-and-biasing.md#example-4--the-source-via-you-forgot) shows, lower high-frequency stability margin.
- **Noise measure, not NF, orders a cascade**: with two candidate first stages, the one with lower $M$ should go first; a low-NF, low-gain stage can lose to a slightly noisier high-gain stage.
- **Balanced LNA**: two identical LNAs between 90° hybrids. Each can be noise-matched with poor $S_{11}$; the reflections cancel at the input port and go to the hybrid's terminated port. Input return loss is excellent, output P1dB is +3 dB, but hybrid loss (≈ 0.1–0.3 dB) adds to NF [5][see [couplers](couplers-dividers-combiners.md)].
- **Shunt (drain-gate) feedback**: a resistor $R_f$ (with DC block) from output to input flattens gain and lowers low-frequency gain — the key to unconditional stability of high-gain devices at UHF (worked example 2). Its thermal noise adds roughly $R_s/R_f$ to $F-1$ for $R_f\gg R_s$; with 1.5 kΩ this is modest.
- **Common-gate / resistive-feedback CMOS LNAs** give broadband 50 Ω match ($1/g_m=R_s$) at the cost of $F\ge1+\gamma/\alpha$ (≈ 2.2 dB with $\gamma=2/3$, $\alpha=1$) unless noise-cancelling topologies are used [5].
- **Noise temperature view.** For very low NF (satellite/radio astronomy), use $T_e=T_0(F-1)$: 0.38 dB ≈ 26 K, 0.74 dB ≈ 54 K. Antenna temperature can be comparable or larger, especially at UHF near cities (man-made noise), so below ≈ 0.5 dB NF improvements often do not improve real sensitivity [see [thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md)].
- **Limits of the linear noise model.** Noise parameters are small-signal; under strong blockers the LNA compresses and NF rises (desensitisation). Flicker noise is irrelevant at RF except for its upconversion in oscillators and zero-IF receivers.

### Level 3b — CMOS LNA noise: induced gate noise, power-constrained width, noise cancelling
These matter mainly for integrated designs, but they explain data-sheet NF limits of CMOS front ends (SX126x-class radios, GNSS SoCs). Numbers come from `tools/verify/s15_cmos_lna.py`.

**(a) The MOSFET's four noise parameters.** Two noise currents act in a MOSFET [4], [14]:
- *Drain (channel) noise* $\overline{i_d^2}=4kT\gamma g_{d0}$, with γ = 2/3 in long-channel saturation.
- *Induced gate noise* $\overline{i_g^2}=4kT\delta g_g$, with $g_g=\omega^2C_{gs}^2/(5g_{d0})$ and δ = 2γ. Channel potential fluctuations couple capacitively into the gate, so it rises as ω².
- The two are correlated, with c = j0.395 (long-channel) in Lee's reference directions.

With α = g_m/g_d0, the noise parameters are
$$R_n=\frac{\gamma}{\alpha g_m},\quad G_{opt}=\alpha\omega C_{gs}\sqrt{\tfrac{\delta}{5\gamma}(1-|c|^2)},\quad B_{opt}=-\omega C_{gs}\Big(1+\alpha|c|\sqrt{\tfrac{\delta}{5\gamma}}\Big),\quad F_{min}=1+\frac{2}{\sqrt5}\frac{\omega}{\omega_T}\sqrt{\gamma\delta(1-|c|^2)} .$$
A brute-force minimisation of F over Y_s reproduces all four exactly (check A1): $F_{min}$ = 0.165/0.324/0.626 dB at ω/ω_T = 0.05/0.1/0.2, and $B_{opt}$ is the "+" form, i.e. *more* inductive than resonating C_gs.
- Without gate noise, or with fully correlated noise, F_min would be 0 dB. What sets the floor is the *uncorrelated* part, the $(1-|c|^2)$ factor [14].
- Short-channel devices have γ and δ two to three times higher (Lee's pessimistic γ = 2, δ = 4 gives about 0.9 dB at ω_T/ω = 10 [14]). Some measurement studies on deep-submicron devices report induced gate noise to be less important than this long-channel model suggests (seen in search summaries only, not verified here).

**(b) Power-constrained width (PCNO).** Classical noise matching assumes a given transistor. In an IC the width W is free and the bias current is the budget. Narrow devices have high f_T but need a high-Q input network, which makes the gate noise prominent. Wide devices have low current density, so f_T and the drain noise suffer. Hence there is an optimum width [4], [14].
- *Model in the script:* inductive degeneration matched to 50 Ω ($L_s=R_s/\omega_T$, $L_g$ resonates $C_{gs}$), the full nodal noise solve with correlated gate noise, a long-channel square law, and 0.18 µm-like parameters ($C_{ox}$ 8.6 fF/µm², µ 300 cm²/Vs; illustrative).
- *At 1575.42 MHz:* the optimum is **W = 519 µm, i.e. $Q_L=1/(\omega_0C_{gs}R_s)=3.77$, at every bias current.** This lies inside Lee's 3–5, and his estimate $W_{opt}\approx1/(3\omega LC_{ox}R_s)$ = 435 µm. It is about 820 µm·GHz, against Lee's "very roughly 500 µm·GHz" for his process.
- *NF:* 0.53/0.34/0.25 dB at 2/5/10 mA (f_T 16/26/36 GHz), always above the device F_min of the same W (0.32/0.20/0.14 dB) because the circuit cannot present $B_{opt}$ and $G_{opt}$ at once. Without gate noise the same circuit would show 0.07/0.05/0.03 dB: gate noise dominates at the optimum.
- *Shape:* the optimum is shallow. At 5 mA, W = 200/400/800 µm gives 0.43/0.35/0.37 dB.
- *Quoted formula:* the exact model gives $F-1\approx2.0\,(\gamma/\alpha)(\omega_0/\omega_T)$ at the optimum, against the quoted $2.4(\gamma/\alpha)(\omega_0/\omega_T)$ in Level 2(g). The difference is the approximations behind the closed form. The quoted value is the power-constrained optimum, not the device $F_{min}$.
- *Sign sensitivity:* flipping the correlation sign moves the optimum to Q_L = 2.60 and 0.29 dB, so the reference-direction convention matters at the ≈ 0.06 dB / 30 %-in-W level.
- *Passive loss:* a Q = 20 gate inductor (18.8 nH) raises the 5 mA optimum to **1.06 dB**. As in Example 4, passive loss dominates.

**(c) Noise-cancelling (CG–CS) wideband LNAs.** A common-gate (CG) stage matches the input with $g_{m1}=1/R_s$, but its own noise caps F at ≥ 1 + γ/α (2.2 dB). With R₁ = 500 Ω the script gives 3.15 dB. Bruccoleri's insight [15] is that the CG device's channel noise current appears at the input node and at the CG output *with opposite signs*, whereas the signal appears with the *same* sign. Add a common-source (CS) stage that senses the input node and take $v_{out}=v_{CG}-v_{CS}$:
- the signal adds, giving $2R_1/R_s$ × the input-node voltage;
- the CG noise cancels exactly when $g_{m2}R_2=R_1/R_s$.

In the nodal check (C1) the M1 share of F − 1 is 0 at the condition and 0.8 % with g_m2 20 % low. The CS device's own noise is *not* cancelled, so NF falls as its g_m rises: n = g_m2/g_m1 = 1/2/4 gives 2.71/1.71/1.11 dB at 2×/3×/5× the current, all with 20 dB gain. Scaling the CS stage by n with R₂ = R₁/n also balances the two outputs: the **balun-LNA** [16] (inductorless, 0.1–6 GHz, NF < 3.5 dB, IIP3 > 0 dBm in 65 nm). The same feed-forward cancellation also removes the CG device's distortion.
- *For a discrete builder:* the idea transfers to any transconductor (BJT/pHEMT), but a pHEMT with a noise match already reaches 0.4–0.7 dB at UHF/L-band (Examples 2–3). Noise cancelling earns its place where a wideband (multi-octave) resistive match is required, such as an SDR front end covering 0.1–6 GHz.

## Design equations & rules of thumb

| Quantity | Equation | Notes |
|---|---|---|
| Noise factor | $F=F_{min}+\frac{R_n}{G_s}\lvert Y_s-Y_{opt}\rvert^2$ | noise params per frequency |
| Noise circle | $C_F=\frac{\Gamma_{opt}}{N+1}$, $R_F=\frac{\sqrt{N(N+1-\lvert\Gamma_{opt}\rvert^2)}}{N+1}$ | $N=\frac{F-F_{min}}{4R_n/Z_0}\lvert1+\Gamma_{opt}\rvert^2$ |
| Friis | $F=F_1+\frac{F_2-1}{G_1}+\dots$ | [07 page](../07-noise-linearity/noise-figure-and-friis.md) |
| Passive loss before LNA | NF adds dB-for-dB (at 290 K) | 0.3 dB inductor loss = +0.3 dB NF |
| Inductor loss | $R=\omega L/Q$; NF penalty ≈ $10\log(1+R/R_s)$ for a series input L | 22 nH, Q 40, 433 MHz: 1.5 Ω → 0.13 dB |
| Inductive degeneration | $\mathrm{Re}Z_{in}=\omega_TL_s$, $G_m=\frac{\omega_T}{2\omega_0R_s}$ | CMOS, cascode output |
| MOSFET F_min | $1+\frac{2}{\sqrt5}\frac{\omega}{\omega_T}\sqrt{\gamma\delta(1-|c|^2)}$; $B_{opt}=-\omega C_{gs}(1+\alpha|c|\sqrt{\delta/5\gamma})$ | 0.32 dB at ω_T/ω = 10 (long-channel) |
| Power-constrained width | $Q_L=1/(\omega_0C_{gs}R_s)\approx3$–5; $W_{opt}\approx1/(3\omega LC_{ox}R_s)$ | exact model: Q_L 3.8, F−1 ≈ 2.0(γ/α)(ω0/ω_T) |
| Noise cancelling (CG–CS) | $g_{m2}R_2=R_1/R_s$ | CS ×4: NF 1.1 dB vs CG 3.2 dB |
| Channel-noise NF | $F-1=\gamma g_{d0}R_s(\omega_0/\omega_T)^2$ | plus gate noise, $L_g$ loss |
| Noise temperature | $T_e=290(F-1)$ K | 0.5 dB → 35 K; 1 dB → 75 K |
| IIP3 of LNA | IIP3 = OIP3 − G | PGA-103+ at 0.4 GHz: 39 − 22 = +17 dBm |

Rules of thumb:
- Choose device and bias for NFmin *and* linearity: pHEMTs give NFmin ≈ 0.2–0.5 dB below 2 GHz; BJT/SiGe ≈ 0.6–1 dB; CMOS integrated ≈ 1–2 dB.
- Use the highest-Q inductor available at the input (air-core or 0603/0805 wire-wound, Q ≥ 40 at the operating frequency); the output network can use cheaper parts.
- Accept 8–10 dB input return loss for a noise-matched single-ended LNA; if a filter before the LNA needs a good 50 Ω termination, use source-inductance feedback or a balanced LNA.
- Simulate stability of the complete LNA from ≈ 10 MHz (or the lowest data point) to ≥ 3× the device $f_T$, with realistic parts, and repeat with ideal (high-Q) parts: stability must not rely on component loss.

## Worked examples

### Example 1 — Noise circles of a real device
ATF-54143 at 3 V/60 mA (data sheet [3]; values between rows interpolated, and the vendor notes that Fmin below 2 GHz is extrapolated):

| f | NFmin | Γopt | Rn | 0.5 dB circle | 1.0 dB circle | NF with 50 Ω source |
|---|---|---|---|---|---|---|
| 433 MHz | 0.15 dB | 0.34∠42° | 2 Ω | C 0.18∠42°, r 0.66 | C 0.10∠42°, r 0.82 | 0.20 dB |
| 1575 MHz | 0.35 dB | 0.29∠99° | 2 Ω | C 0.23∠99°, r 0.43 | C 0.14∠99°, r 0.71 | 0.40 dB |

Interpretation: with $R_n$ = 2 Ω, almost any source impedance near 50 Ω gives < 0.5 dB. The real enemies of noise figure for this device are (i) input-network loss, (ii) whatever resistive stabilisation you need, and (iii) layout (source vias). This is typical of modern pHEMTs and not of BJTs (larger $R_n$).

### Example 2 — 433 MHz LNA with the ATF-54143 (verified design)
Topology (the data-sheet "high-pass" style [3]): input series $C_1$ → shunt $L_1$ at the gate whose cold end goes to an RF bypass $C_2$ paralleled by $R_4$ + 100 nF (the gate bias is fed there through 10 kΩ); drain series $R_d$ → shunt $L_4$ to RF bypass $C_5$ paralleled by $R_3$ + 100 nF (drain supply from 5 V); output series $C_4$; plus a drain-to-gate feedback branch $R_f+C_f$. DC constraint: $R_d+R_3=(5-3)/(62\text{ mA})=32.3\ \Omega$. Parts modelled as 0603 wire-wound inductors (Q = 40, 0.12 pF self-capacitance → 100 nH SRF 1.45 GHz, consistent with Coilcraft 0603CS [7]) and 0402 C0G capacitors (0.4 nH ESL, Q 400). Optimised by differential evolution for minimum NF subject to μ > 1.08 from 0.1 to 10 GHz with ideal, Q = 40 and Q = 100 parts, input RL ≥ 9 dB, output RL ≥ 14 dB, gain ≥ 16 dB; then rounded to E12 values:

| Part | Value | Role |
|---|---|---|
| C1 | 100 pF | DC block (≈ 3.7 Ω at 433 MHz) |
| L1 | 100 nH | gate shunt: sets $\Gamma_S$ near $\Gamma_{opt}$; gate bias path |
| C2 | 150 pF | RF bypass of the gate feed |
| R4 | 180 Ω | low-frequency gate termination |
| Rd | 22 Ω | drain series stabiliser (carries DC) |
| L4 | 27 nH | drain shunt: output match, drain feed |
| C5 | 2.2 pF | *partial* bypass — lets R3 load the drain at RF (deliberate) |
| R3 | 10.3 Ω (use 10 Ω) | drain feed resistor / LF termination |
| C4 | 15 pF | output series match / DC block |
| Rf + Cf | 1.5 kΩ + 82 pF | drain–gate shunt feedback: kills low-frequency gain |

Performance (real parts, Q = 40): **NF 0.38 dB, $G_T$ 22.1 dB, $S_{11}$ −8.9 dB, $S_{22}$ −19.4 dB, μ ≥ 1.08 from 0.1 to 10 GHz**. With Q = 25 inductors NF is 0.39 dB (the gate shunt inductor sees a high impedance node, so its loss matters less than a series inductor's would). Monte Carlo (300 trials, ±5 % L/C, ±1 % R, Q 25–80): NF 0.38 dB mean (max 0.40), gain 22.1 ± 0.1 dB, 100 % unconditionally stable (min μ 1.07).
Without the feedback branch, the best design meeting the same stability constraints had NF 1.6 dB: at 433 MHz the device's gain at 100 MHz (MSG 34 dB) is too close in frequency to be removed by bias-feed resistors alone. **Lesson: at UHF, resistive shunt feedback is cheaper in noise than resistive loading.**
Out-of-band gain of this amplifier: +11.5 dB at 100 MHz, +17 dB at 900 MHz, +14 dB at 1.58 GHz, +12 dB at 2.4 GHz — it amplifies everything; a 433 MHz band-pass (SAW or LC) is still needed, see Example 5.

### Example 3 — GPS L1 (1575.42 MHz) LNA with the same device (verified design)
Same topology (feedback branch not needed; the optimiser drove $R_f$ to its 10 kΩ "off" limit):

| C1 | L1 | C2 | R4 | Rd | L4 | C5 | R3 | C4 |
|---|---|---|---|---|---|---|---|---|
| 82 pF | 2.7 nH | 82 pF | 470 Ω | 4.7 Ω | 4.7 nH | 2.7 pF | 27.6 Ω (27 Ω) | 56 pF |

Performance (real parts, Q = 40): **NF 0.74 dB, $G_T$ 19.2 dB, $S_{11}$ −9.4 dB, $S_{22}$ −15.2 dB, μ ≥ 1.05 (0.1–10 GHz)**; Q = 25: 0.83 dB; Q = 80: 0.66 dB — here inductor Q matters more because the 2.7 nH gate inductor carries the full signal current at a lower impedance. Monte Carlo: NF 0.71 dB mean (max 0.86 dB), 100 % stable. For comparison, the data-sheet test circuit reports 0.5 dB at 2 GHz [3] but is not constrained to unconditional stability down to 100 MHz with realistic parts.

A GNSS antenna chain for a u-blox ZED-F9P should provide 17–50 dB (ideally 30–40 dB) of gain with NF < 4 dB for the active antenna and a total system NF ≈ 3 dB, and ≈ 40 dB out-of-band rejection [8]: one stage of this LNA plus a SAW filter plus a second gain stage (e.g. a BGA524N6) is a typical recipe (see [GNSS front end](../20-projects-recipes/gnss-front-end-design.md)).

### Example 4 — CMOS inductively degenerated LNA at 1575.42 MHz (hand design)
$C_{gs}=200$ fF, $g_m=40$ mS → $f_T=31.8$ GHz; $R_s=50\ \Omega$.
1. $L_s=R_s/\omega_T=50/(2.0\times10^{11})=0.25$ nH (a bond wire or a short on-chip line).
2. $L_g+L_s=1/(\omega_0^2C_{gs})=51.0$ nH → $L_g=50.8$ nH — large, so it is usually off-chip.
3. $Q_{in}=1/(2\omega_0C_{gs}R_s)=5.05$; $G_m=\omega_T/(2\omega_0R_s)=202$ mS (5 × $g_m$).
4. Channel-noise NF with $\gamma=2/3$: $F-1=\gamma g_mR_s(\omega_0/\omega_T)^2=1.333\times0.00245=0.0033$ → 0.014 dB (optimistically tiny).
5. Gate inductor with Q = 20: $R_{Lg}=\omega_0L_g/Q=25.1\ \Omega$ → adds $R_{Lg}/R_s=0.50$ → **NF ≈ 1.8 dB**. The passive loss, not the transistor, sets the NF — the standard lesson of CMOS LNA design [5].

### Example 5 — LoRa ground station: is an LNA worth it, and where?
Receiver: an SX126x-based module; its SF12/125 kHz sensitivity of −137 dBm with a −20 dB demodulation SNR implies $NF\approx-137+174-10\log_{10}(125\,000)+20=6.0$ dB (derived; see [LoRa sensitivity](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md)). Feed: 10 m of RG-58 ≈ 3 dB at 433 MHz. LNA: Example 2 (0.38 dB, 22.1 dB).

| Configuration | System NF | $T_{sys}$ ($T_{ant}$ = 290 K) | $T_{sys}$ ($T_{ant}$ = 1000 K) |
|---|---|---|---|
| No LNA | 9.03 dB | 2320 K | 3030 K |
| LNA at the radio (after cable) | 3.45 dB | — | — |
| LNA at the antenna (masthead) | 0.55 dB | 329 K | 1039 K |
| SNR improvement (masthead) | | **8.5 dB** (range ×2.66) | **4.6 dB** (×1.71) |

The cable loss in front of the LNA cannot be recovered afterwards. For the rocket downlink, add a 433 MHz SAW/cavity filter *before* the LNA only if strong nearby signals (other telemetry, cellular, pagers) exist; otherwise place the filter after the LNA to protect NF (filter loss before the LNA adds dB-for-dB) [9].

### Example 6 — Protect the LNA from your own rocket
Rocket transmitter: EBYTE E22-400T33D, +33 dBm, with a 2.15 dBi dipole; ground-station Yagi 10 dBi. Friis at 433 MHz (λ = 0.69 m):

| Distance | Power at LNA input |
|---|---|
| 100 m | −20 dBm |
| 30 m | −10 dBm |
| 10 m | 0 dBm |
| 3 m | +10 dBm |
| 1 m | ≈ +20 dBm (near field; indicative) |

A GNSS MMIC rated for 0 dBm (BGA524N6 [10]) would be at its limit at 10 m; the ATF-54143 (+20 dBm abs. max [3]) and PGA-103+ (+21 dBm [11]) survive pad-side checkout at a few metres but not a transmitter placed next to the antenna. During pad testing, point the Yagi away, use an attenuator, or add a limiter (see [limiters](rf-switches-attenuators-limiters.md)). A PIN/Schottky limiter adds ≈ 0.2–0.5 dB before the LNA — an NF cost only worth paying where overload is realistic.

### Example 7 — Choosing an MMIC instead
| Part | Band | Gain | NF | Linearity | Supply | Notes |
|---|---|---|---|---|---|---|
| Mini-Circuits PGA-103+ | 0.05–4 GHz | 22.1 dB @ 0.4 GHz, 11 dB @ 2 GHz | 0.5 dB @ 0.4 GHz, 0.9 dB @ 2 GHz | OIP3 +39 dBm @ 0.4 GHz, P1dB +21.5 dBm | 5 V, 97 mA (3 V, 60 mA option) | E-pHEMT, SOT-89, 50 Ω without matching; input RL only ≈ 11 dB at 0.4 GHz [11] |
| Infineon BGA524N6 | 1550–1615 MHz | 19.6 dB | 0.55 dB | IP1dB −16 dBm, IIP3 −9 dBm | 1.5–3.3 V, 2.5 mA | one 8.2 nH input inductor; RF input abs. max 0 dBm [10] |
| ATF-54143 (discrete) | VHF–6 GHz | design-dependent (19–25 dB) | 0.3 dB @ 0.9 GHz, 0.5 dB @ 2 GHz (test circuit) | OIP3 +35.5 dBm @ 0.9 GHz | 3 V, 60 mA | needs matching and stabilisation [3] |

For 433 MHz, the PGA-103+ is a near drop-in LNA with superb linearity (good near strong transmitters); a discrete pHEMT buys ≈ 0.1–0.2 dB. For GNSS, the BGA524N6 is tiny and frugal but fragile against out-of-band power; place a SAW before it if the rocket's own 433/900 MHz transmitters are close.

## Practical notes
- **Source/emitter grounding:** use several vias directly at each source pad (the ATF-54143 S-parameters include four 0.5 mm vias [3]); any extra inductance shifts both match and stability.
- **Input inductor:** wire-wound (Coilcraft 0603HP/0603CS, Murata LQW) or air-core; avoid multilayer chip inductors at the LNA input (Q ≈ 10–20). Keep the input trace short and on a low-loss path; each 0.1 dB of loss before the device is 0.1 dB of NF.
- **Bias noise:** the LNA's supply and gate bias must be quiet; LDO noise at low frequency modulates gain (AM sidebands) and can upconvert. Filter with RC after the regulator.
- **ESD:** antenna ports need ESD protection with low capacitance (< 0.5 pF at 1.5 GHz) — u-blox makes it mandatory on RF_IN [8].
- **Measuring NF:** with a noise source and spectrum analyser (Y-factor), subtract cable/fixture loss; see [noise figure measurement](../17-test-measurement/noise-figure-measurement.md). A NanoVNA can verify S-parameters and gain but not NF.
- **Oscillation check:** after building, sweep a spectrum analyser 10 MHz–6 GHz with the input terminated and then open/shorted (worst case for conditional instability).
- **Active GNSS antenna feed:** DC is supplied up the coax through a bias tee (inductor with high impedance in the GNSS bands [8]); the LNA board needs its own RF choke, regulator and reverse-polarity protection.

## Common mistakes & misconceptions
- *"Maximum gain = minimum noise."* No: the gain optimum ($\Gamma_{MS}$) and noise optimum ($\Gamma_{opt}$) differ; the NF at the gain optimum can be several tenths of a dB worse.
- *"An LNA with bad S11 is a bad LNA."* A noise-matched LNA normally has 8–10 dB return loss; judge it by NF, gain, stability and linearity (unless a preceding filter needs a good termination).
- *"Adding a 50 Ω resistor across the input fixes the match."* It fixes S11 and adds ≈ 3 dB of NF.
- *"The LNA goes after the SAW filter so it doesn't overload."* Only if interference forces it; the filter's 1.5–3 dB loss adds directly to NF [9].
- *"An LNA at the receiver end of a long cable helps as much as at the antenna."* The cable loss before it is unrecoverable (Example 5).
- *"The data-sheet NF is what I'll get."* The data-sheet circuit uses optimum parts and layout, sometimes not unconditionally stable; realistic Q and stabilisation cost 0.2–0.5 dB.
- *"CMOS LNAs have NF limited by the transistor."* At low GHz, gate-inductor loss usually dominates (Example 4).
- *"F_min = 1 + 2.4(γ/α)(ω/ω_T) is the MOSFET's minimum noise figure."* That is the *power-constrained* optimum of an inductively degenerated LNA. The device's own F_min is lower: $1+\frac{2}{\sqrt5}\frac{\omega}{\omega_T}\sqrt{\gamma\delta(1-|c|^2)}$.
- *"Gate and drain noise each impose a noise-figure floor."* Only their *uncorrelated* parts do. With fully correlated noise a noise match would reach 0 dB.
- *"A wideband matched LNA can't beat 3 dB NF."* Resistive or common-gate matching alone can't; noise cancelling removes the matching device's noise (1.1 dB at 5× current in the example).
- *"More LNA gain is always better."* Too much gain before the mixer/ADC reduces the receiver's IIP3 and blocking performance; set the gain so that the next stage's noise is suppressed by ~10 dB and no more (see [cascade analysis](../07-noise-linearity/receiver-cascade-analysis.md)).
- *"Noise figure below 0.5 dB will double my range."* Only if the antenna temperature is low; with $T_{ant}$ ≈ 290 K or higher, the returns diminish rapidly (Example 5).
- *"An RC (or any) filter after the LNA lowers the noise."* It lowers the *total* noise power only by narrowing the bandwidth; the noise *inside the signal band* — and therefore the SNR and NF — was fixed by the LNA and everything before it. A post-LNA filter can only add noise: its loss $L$ enters the Friis sum as $(L-1)/G_1$ and it raises the following stage's contribution by $L$. Example: LNA NF 1 dB / G 20 dB, then a 3 dB-loss filter, then a 6 dB-NF receiver → cascade NF 1.23 dB vs 1.10 dB without the filter (Friis, [noise figure & Friis](../07-noise-linearity/noise-figure-and-friis.md)). A resistive RC section is also a poor RF filter (lossy, low selectivity, its resistors are noise sources). Where a post-LNA filter *does* pay: (i) rejecting blockers/images before the mixer or ADC ([dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)); (ii) **anti-alias/noise-folding** before a sampler that has no channel filter — 2 GHz of LNA noise bandwidth sampled at 100 MS/s folds 2000/50 = 40× (16 dB) of noise into the first Nyquist zone ([sampling](../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md)); (iii) a detector or power meter that integrates everything it sees. In all three it protects the *later* stages; it never improves the LNA's NF. (Myth flagged by W4-D1, electronics.stackexchange.com/q/664603.)

## How to simulate / verify
- `tools/verify/rfckt_lna.py`: gain definitions vs wave analysis, SCM, noise and gain circles, unilateral bounds, inductive-degeneration closed forms, the two ATF-54143 designs (differential-evolution optimisation, E12 rounding, finite-Q and parasitic models, tolerance Monte Carlo), source-inductance noise analysis, ground-station system NF and damage budget. Runtime ≈ 2–3 min.
- `tools/verify/s15_cmos_lna.py` (W5-S15): MOSFET noise parameters with induced gate noise (brute-force vs closed form), power-constrained width optimisation of the inductively degenerated LNA (nodal noise solve), CG–CS noise cancelling. ALL PASS, ≈ 1 s.
- `tools/verify/rfckt_noise2port.py`: chain/admittance/impedance noise-correlation engine (Hillbrand & Russer [12]), self-tested against the classical formula, attenuator NF = loss, and Friis.
- `tools/verify/rfckt_atf54143_data.py`: the device's S- and noise-parameter tables.
- scikit-rf: `Network.set_noise_a(...)`, `Network.nf(z)`, `nf_circle`, `gain_circle`, `stability_circle` — useful for quick plots; cross-check its noise cascade against the engine above.
- For final design, simulate with the vendor's `.s2p`/noise file (or nonlinear model) plus EM-simulated layout (openEMS / Sonnet) including vias and pads, then measure: S-parameters with a VNA, NF with a noise source, stability with terminations varied.

## Open questions / gaps
- The ATF-54143 noise parameters below 2 GHz are vendor-extrapolated [3]; the 433 MHz design uses the 0.5 GHz row. A measured noise-parameter set at 433 MHz would firm up Example 2.
- Component models (constant Q, single self-capacitance, constant ESL) are first-order; a real design should use vendor S-parameter models of the exact inductors/capacitors (see [component models](../04-real-components-hf/component-models-s2p-spice.md)).
- The SX126x implied NF (6 dB) is derived from sensitivity and demodulator SNR; domain 15 should confirm with measured data.
- The Shaeffer–Lee full expression is not re-derived symbolically. It is reproduced numerically (Level 3b), with a 2.0 vs 2.4 factor difference attributed to the closed form's approximations. The correlation sign convention changes the optimum width by ≈ 30 %. All of this uses long-channel parameters; short-channel γ, δ and c are process-dependent.

## Sources
1. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012, §12.1 (power gains), §12.3 (conjugate match, constant-gain and noise circles, LNA design). (textbook)
2. H. Rothe, W. Dahlke, "Theory of noisy fourpoles," *Proc. IRE*, 44(6), pp. 811–818, 1956; IRE standards on noise parameters. (peer-reviewed; background)
3. Avago/Broadcom, *ATF-54143 Low Noise Enhancement Mode Pseudomorphic HEMT* data sheet: S- and noise parameters at 3 V/60 mA (Fmin < 2 GHz extrapolated), typical NF/Ga/OIP3/P1dB at 0.9 and 2 GHz, absolute maximum ratings (RF input +20 dBm), application circuit and bias design. https://www.modelithics.com/models/Vendor/Avago/ATF-54143.pdf (datasheet)
4. D. K. Shaeffer, T. H. Lee, "A 1.5-V, 1.5-GHz CMOS low noise amplifier," *IEEE J. Solid-State Circuits*, 32(5), pp. 745–759, May 1997; and T. H. Lee, *The Design of CMOS Radio-Frequency Integrated Circuits*, 2nd ed., Cambridge, 2004, ch. 12. (peer-reviewed / textbook)
5. B. Razavi, *RF Microelectronics*, 2nd ed., Prentice Hall, 2011, ch. 5 (LNA topologies: CS with inductive degeneration, CG, feedback, noise cancelling). (textbook)
6. H. A. Haus, R. B. Adler, *Circuit Theory of Linear Noisy Networks*, Wiley/MIT, 1959 (noise measure and its invariance). (textbook; cited for the invariance result)
7. Coilcraft 0603CS ceramic chip inductors (e.g. 0603CS-R10: 100 nH, SRF 1.4 GHz). https://www.coilcraft.com/en-us/products/rf/ceramic-core-chip-inductors/ (datasheet)
8. u-blox, *ZED-F9P Integration Manual*, UBX-18010802, R16: Table 39 active-antenna recommendations (17–50 dB gain, NF < 4 dB, 40 dB OOB rejection), §4.8.4 (30–40 dB ideal, system NF ≈ 3 dB, ESD mandatory), §4.5 EOS/ESD. https://content.u-blox.com/sites/default/files/ZED-F9P_IntegrationManual_UBX-18010802.pdf (manufacturer manual)
9. "An overview of the effects of out-of-band interference on GNSS receivers," *NAVIGATION* (J. Inst. of Navigation), 67(1), p. 143, 2020 — filter-first vs LNA-first trade. https://navi.ion.org/content/67/1/143 (peer-reviewed; summary level)
10. Infineon, *BGA524N6 GNSS LNA* data sheet rev. 3.5, 2021: 19.6 dB, 0.55 dB, 2.5 mA, IP1dB −16 dBm, IIP3 −9 dBm, RF input abs. max 0 dBm, 8.2 nH input inductor. https://www.infineon.com/part/BGA524N6 (datasheet)
11. Mini-Circuits, *PGA-103+* data sheet rev. C. https://www.minicircuits.com/pdfs/PGA-103+.pdf (datasheet)
12. H. Hillbrand, P. H. Russer, "An efficient method for computer aided noise analysis of linear amplifier networks," *IEEE Trans. Circuits Syst.*, CAS-23(4), pp. 235–238, Apr. 1976. (peer-reviewed; method implemented in tools/verify/rfckt_noise2port.py)
13. G. Gonzalez, *Microwave Transistor Amplifiers*, 2nd ed., Prentice Hall, 1997, ch. 4 (noise, LNA design, balanced amplifiers). (textbook)
14. T. H. Lee, "The design of narrowband CMOS RF low-noise amplifiers," in *Analog Circuit Design* (AACD workshop), 1998 — MOSFET noise parameters with induced gate noise (eqs. 10–24: R_n, B_opt = −ωC_gs(1 + α|c|√(δ/5γ)), G_opt, F_min), Q_sP 3–5, W_opt ≈ 1/(3ωLC_oxR_s), ≈ 500 µm·GHz. http://smirc.stanford.edu/papers/aacd98p-tom.pdf (conference/workshop paper; read via pdftotext)
15. F. Bruccoleri, E. A. M. Klumperink, B. Nauta, "Wide-band CMOS low-noise amplifier exploiting thermal noise canceling," *IEEE J. Solid-State Circuits*, 39(2), pp. 275–282, Feb. 2004, doi:10.1109/JSSC.2003.821786. (peer-reviewed)
16. S. C. Blaakmeer, E. A. M. Klumperink, D. M. W. Leenaerts, B. Nauta, "Wideband balun-LNA with simultaneous output balancing, noise-canceling and distortion-canceling," *IEEE J. Solid-State Circuits*, 43(6), pp. 1341–1350, June 2008, doi:10.1109/JSSC.2008.922736 (65 nm, 0.1–6 GHz, 15 dB, NF < 3.5 dB, IIP3 > 0 dBm). (peer-reviewed)
