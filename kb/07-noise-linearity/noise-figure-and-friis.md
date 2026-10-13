---
title: Noise figure, noise temperature and the Friis cascade formula
domain: 07-noise-linearity
slug: noise-figure-and-friis
tags: [noise-figure, noise-factor, noise-temperature, friis, cascade, LNA, noise-matching, noise-parameters, mixer-noise, SSB, DSB]
prerequisites: [thermal-noise-and-noise-temperature.md, ../00-math-foundations/decibels-and-log-units.md, ../03-transmission-lines-matching/smith-chart.md, ../03-transmission-lines-matching/s-parameters.md]
related: [receiver-cascade-analysis.md, sensitivity-and-mds.md, dynamic-range-sfdr-blocking.md, ../06-rf-circuits/lna-design.md, ../06-rf-circuits/mixers.md, ../06-rf-circuits/receiver-architectures.md, ../17-test-measurement/noise-figure-measurement.md, ../09-propagation-link-budget/link-budget-methodology.md]
level: mixed
confidence: high
last_updated: 2026-10-02
---

# Noise figure, noise temperature and the Friis cascade formula

## Questions this page answers
- What exactly is noise figure, and how is it different from noise factor and noise temperature?
- Why must the LNA go first, right at the antenna?
- Why does 3 dB of cable in front of my LNA cost me 3 dB, but 3 dB of cable after it costs almost nothing?
- How do I compute the noise figure of a chain of amplifiers, filters, cables and mixers?
- Why does my mixer datasheet quote a "DSB" noise figure and why is the "SSB" one 3 dB worse?
- What are Fmin, Rn and Γopt, and why is the input match for lowest noise not the match for highest gain?
- What are noise circles?
- Can a noise figure be negative, or can a cascade be quieter than its first stage?

## TL;DR
- **Noise factor** $F$ = (SNR at input)/(SNR at output) when the input source is at $T_0$ = 290 K. **Noise figure** NF = $10\log_{10}F$ dB. **Equivalent noise temperature** $T_e = T_0(F-1)$. They are three views of the same number: NF 1 dB ↔ 75 K; 3 dB ↔ 289 K; 6 dB ↔ 865 K.
- **Friis (1944) cascade:** $F_\text{tot} = F_1 + \frac{F_2-1}{G_1} + \frac{F_3-1}{G_1G_2} + \dots$ with **linear** available gains, or $T_e = T_{e1} + T_{e2}/G_1 + \dots$. Later stages are suppressed by the gain in front of them.
- **Loss before the first amplifier adds directly:** a lossy line $L$ at 290 K followed by an amplifier gives $F = L\cdot F_\text{amp}$ (NF in dB simply add). 3 dB of cable + a 1 dB LNA = 4 dB. After a 20 dB LNA the same cable costs ~0.04 dB (verified `noise_cascade.py`).
- Consequence for Marcus: a 433/915 MHz ground station with 10 m of coax to the module loses the full cable loss (≈2.6 dB at 915 MHz) of sensitivity; a masthead LNA recovers ~6 dB (`noise_cascade.py` examples A1–A3). For GNSS, an active antenna vs a passive patch on 3 m of RG-174 is the difference between NF ≈ 1.2 dB and ≈ 7.5 dB (≈ 9 dB of $C/N_0$).
- **Mixers:** a DSB noise figure (noise and "signal" in both sidebands) is ~3 dB lower than the SSB figure that applies to a normal single-sideband receiver.
- **Noise matching:** $F = F_\text{min} + \frac{4r_n|\Gamma_s-\Gamma_\text{opt}|^2}{(1-|\Gamma_s|^2)|1+\Gamma_\text{opt}|^2}$. The source reflection giving minimum NF ($\Gamma_\text{opt}$) is generally not the conjugate of the device input ($S_{11}^*$), so lowest NF and best gain/return-loss cannot both be had without feedback tricks (see [06-rf-circuits/lna-design](../06-rf-circuits/lna-design.md)).

## Intuition (no math)
Every stage of a receiver adds a little noise of its own. Noise figure tells you *how much worse the SNR gets* passing through the stage, when the stage is fed from a standard 290 K source. A perfect noiseless amplifier has NF = 0 dB: it amplifies the input signal and input noise equally. A real LNA with NF = 1 dB makes the SNR 1 dB worse.

Now chain stages together. The first stage adds its noise directly to the weak antenna signal. The second stage's noise is added *after* the first stage has amplified everything by $G_1$ — so compared with the (now large) signal, the second stage's noise is $G_1$ times less important. This is why the first stage dominates: with 20 dB of LNA gain, a noisy module behind it (NF 6 dB) matters only a little.

A **lossy** first stage — a cable, a filter, a switch, an ESD protection network — is the worst possible first stage. It has "gain" less than one (so it *raises* the importance of everything behind it) *and* it adds thermal noise. A 3 dB cable halves the signal while leaving the thermal noise floor where it was, so the SNR is halved before anything else happens. That lost SNR can never be recovered by gain later.

**Noise matching** is the less-obvious part. A transistor's internal noise can be modelled as a noise voltage and a noise current at its input. With a low source impedance, the current noise flows into it without developing much voltage, but the voltage noise dominates; with a high source impedance the opposite. There is a sweet-spot source impedance ($Z_\text{opt}$, or $\Gamma_\text{opt}$) where the total is smallest: that gives $F_\text{min}$. That sweet spot depends on the transistor's noise physics, while the impedance that gives maximum power transfer depends on its signal (small-signal) input impedance. They differ, so an LNA designer chooses a compromise — the subject of noise circles.

## The math

### Level 1 — definitions and the cascade formula
Symbols: $S_i, N_i$ = available signal/noise power at input; $S_o, N_o$ at output; $G$ = available power gain (linear); $k$ Boltzmann's constant; $B$ noise bandwidth; $T_0$ = 290 K.

- Noise factor (IEEE definition, input source at $T_0$):
  $$F = \frac{S_i/N_i}{S_o/N_o} = \frac{N_o}{G\,kT_0B}\qquad(\ge 1)$$
- Noise figure: $\text{NF} = 10\log_{10}F$ dB. Noise temperature: $T_e = T_0(F-1)$; conversely $F = 1 + T_e/T_0$.
- Output noise of a stage fed by a source at temperature $T_s$: $N_o = kB\,G\,(T_s + T_e)$.
- **Cascade (Friis):**
  $$F_\text{tot} = F_1 + \frac{F_2 - 1}{G_1} + \frac{F_3 - 1}{G_1G_2} + \cdots,\qquad T_{e,\text{tot}} = T_{e1} + \frac{T_{e2}}{G_1} + \frac{T_{e3}}{G_1G_2} + \cdots$$
- Passive lossy stage at $T_0$ with loss $L$: $F = L$, $G = 1/L$.

### Level 2 — derivations
**(a) Why $N_o = G\,kB(T_s + T_e)$ defines $T_e$.** A noisy linear two-port can be replaced by a noiseless copy with an extra noise source at its input of temperature $T_e$, chosen so that the output noise is unchanged. Because uncorrelated powers add, the input-referred noise is $kB(T_s + T_e)$ and the output is $G$ times that.

**(b) Noise factor from $T_e$.** With $T_s = T_0$, $F = N_o/(GkT_0B) = (T_0 + T_e)/T_0 = 1 + T_e/T_0$. The definition *requires* the source to be at $T_0$; that is why "NF" is a property of the device measured under a standard condition, not of the system (see Level 3 for the system version).

**(c) Friis cascade [1].** Two stages, available gains $G_1, G_2$, temperatures $T_{e1}, T_{e2}$, source at $T_s$. Output of stage 1: $G_1kB(T_s + T_{e1})$. Stage 2 adds its own $T_{e2}$ at its input and amplifies:
$$N_o = G_2\left[G_1kB(T_s + T_{e1}) + kBT_{e2}\right] = G_1G_2\,kB\left(T_s + T_{e1} + \frac{T_{e2}}{G_1}\right).$$
So the cascade looks like a single stage with gain $G_1G_2$ and $T_e = T_{e1} + T_{e2}/G_1$. Induction adds more stages. Substituting $T_e = T_0(F-1)$ gives the $F$ form. The derivation assumes (i) **available** gains (each stage's gain as delivered into the next stage's actual input impedance and the noise figure measured with the actual source impedance of the preceding stage — for 50 Ω-matched blocks the datasheet values apply), (ii) uncorrelated stage noise, (iii) the same noise bandwidth for all stages (or referral to the narrowest), (iv) linear operation. A Monte-Carlo simulation injecting independent Gaussian noise at each stage input matches the formula to 0.003 dB (`noise_cascade.py`, verification 1).

**(d) Loss in front of an amplifier.** Stage 1 = passive loss $L$ at $T_0$: $F_1 = L$, $G_1 = 1/L$. Then
$$F_\text{tot} = L + \frac{F_2-1}{1/L} = L\,F_2 \quad\Rightarrow\quad \text{NF}_\text{tot} = L_\text{dB} + \text{NF}_2 .$$
This is exact (at $T_0$) and is the single most important rule in receiver front-end design.

**(e) The first stage bounds the cascade.** Since every $F_i \ge 1$ and gains are positive, $F_\text{tot} \ge F_1$. You can never beat the first stage. You can approach it only by making $G_1$ large compared with $(F_2-1)$.

**(f) SSB vs DSB noise figure of a mixer.** A mixer with LO at $f_{LO}$ translates both $f_{LO} + f_{IF}$ and $f_{LO} - f_{IF}$ (signal band and image band) to the same IF. With a broadband 290 K source, thermal noise from *both* bands appears at the IF.
- If the *signal* also exists in both bands (a DSB measurement with a broadband noise source, or a direct-conversion receiver where the "image" is the other half of the same signal), the SNR ratio sees signal and noise doubled together: $F_\text{DSB}$.
- In a normal heterodyne receiver the signal occupies one sideband only, but the image-band noise still arrives (unless filtered). The output noise is the same but the output signal is half: $F_\text{SSB} = 2F_\text{DSB}$ (+3.01 dB) for equal conversion gain in both sidebands (`noise_friis_nparams.py` §4). With an image-reject filter before the mixer, the image noise is removed and the relation changes — always check which definition a datasheet uses. Y-factor measurements with a broadband noise source on a mixer measure DSB unless the image is filtered [8].

### Level 3 — noise parameters, noise matching and circles
**Two-port noise model.** Any linear noisy two-port can be represented by a noiseless two-port preceded by a noise voltage $v_n$ in series and a noise current $i_n$ in shunt at its input, partially correlated (Rothe & Dahlke 1956 [3]). Driving it from a source admittance $Y_s = G_s + jB_s$ whose own noise current has mean-square $4kT_0G_sB$:
$$F = 1 + \frac{\overline{|i_n + v_nY_s|^2}}{4kT_0G_sB}.$$
Split $i_n = i_u + Y_c v_n$ into a part uncorrelated with $v_n$ and a part fully correlated (correlation admittance $Y_c$). Define $R_n = \overline{v_n^2}/(4kT_0B)$ (noise resistance) and $G_u = \overline{i_u^2}/(4kT_0B)$. Then
$$F = 1 + \frac{G_u + R_n|Y_s + Y_c|^2}{G_s}.$$
Minimising over $Y_s$ gives the four **noise parameters**: $B_\text{opt} = -B_c$, $G_\text{opt} = \sqrt{G_u/R_n + G_c^2}$, $F_\text{min} = 1 + 2R_n(G_\text{opt} + G_c)$, and $R_n$, with the classical result (IRE standard, Haus et al. 1960 [4]):
$$F = F_\text{min} + \frac{R_n}{G_s}\,|Y_s - Y_\text{opt}|^2 .$$
In reflection-coefficient form with $r_n = R_n/Z_0$:
$$F = F_\text{min} + \frac{4r_n\,|\Gamma_s - \Gamma_\text{opt}|^2}{(1-|\Gamma_s|^2)\,|1+\Gamma_\text{opt}|^2}.$$
Both forms are verified against the first-principles $v_n$–$i_n$ model to machine precision in `noise_friis_nparams.py` §2.

**What the parameters mean.** $F_\text{min}$ is the best possible NF of the device at that bias and frequency. $\Gamma_\text{opt}$ is the source reflection that achieves it. $r_n$ is the *sensitivity* to mismatch from $\Gamma_\text{opt}$: a device with small $r_n$ tolerates a sloppy input match; large $r_n$ punishes it. The noise figure depends on the **source** impedance only, not on the load.

**Noise circles.** For a target $F$, define $N = \frac{F-F_\text{min}}{4r_n}|1+\Gamma_\text{opt}|^2$. The locus of $\Gamma_s$ with that $F$ is a circle on the Smith chart:
$$C_F = \frac{\Gamma_\text{opt}}{N+1},\qquad R_F = \frac{\sqrt{N(N+1-|\Gamma_\text{opt}|^2)}}{N+1}.$$
(Checked numerically: points on the computed 0.5 dB circle all evaluate to $F_\text{min}$ + 0.5 dB.) Overlaying noise circles with available-gain circles and stability circles is the standard graphical LNA design method — detailed in [06-rf-circuits/lna-design](../06-rf-circuits/lna-design.md).

**Noise match vs gain match.** Illustrative pHEMT parameters $F_\text{min}$ = 0.5 dB, $\Gamma_\text{opt}$ = 0.5∠60°, $r_n$ = 0.10: presenting $\Gamma_\text{opt}$ gives 0.50 dB; simply using a 50 Ω source gives 0.72 dB; conjugate-matching to an input $S_{11}$ of 0.6∠120° (i.e. $\Gamma_s$ = 0.6∠−120°) gives 1.91 dB (`noise_friis_nparams.py` §3). Inductive source degeneration in LNAs is the common trick that moves the input impedance toward $\Gamma_\text{opt}^*$ so both can be nearly satisfied.

**System (operating) noise factor.** When the source is not at $T_0$ (an antenna of temperature $T_a$), the useful quantity is the system temperature $T_\text{sys} = T_a + T_{e,\text{tot}}$. ITU-R P.372 writes the same thing referred to a lossless antenna, including antenna-circuit and line losses: $f = f_a + (f_c-1) + l_c(f_t-1) + l_cl_t(f_r-1)$ [5] — structurally the Friis formula with the external noise factor $f_a$ in front.

**Beyond simple Friis.** (i) If a stage's input is mismatched, use its NF *at the actual source impedance* and the *available* gain of the stage in front — datasheet 50 Ω values are only valid if everything is 50 Ω. (ii) Correlated noise between stages (e.g., LO noise feeding two mixers, or a feedback loop) breaks the uncorrelated assumption. (iii) Stages with different bandwidths: noise from a wideband early stage can alias or fold (e.g. ADC Nyquist zones, image bands) and must be counted per band. (iv) A preprint (arXiv 2209.00287, 2022) defines "stage-wise" noise factors from the in-situ SNR at each stage and shows the total is their product; this is a different definition, not a contradiction of Friis, which uses the standard $T_0$-source definition [9].

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $F = 1 + T_e/T_0$ | any linear two-port, source at 290 K | NF 0.5 dB ↔ 35 K; 1 dB ↔ 75 K; 2 dB ↔ 170 K; 6 dB ↔ 865 K; 10 dB ↔ 2610 K |
| $F_\text{tot} = F_1 + (F_2-1)/G_1 + \dots$ | linear gains, matched/available gains | LNA 1 dB/15 dB + 6 dB module → 1.31 dB |
| $\text{NF}_\text{tot} = L_\text{dB} + \text{NF}_2$ | loss at 290 K before a stage | 2.6 dB coax + 6 dB module = 8.6 dB |
| "LNA gain ≥ (NF_rest − 1) × 10" | keeps later-stage penalty < ~0.4 dB | with NF_rest = 6 dB (F=4), want $G_1 \gtrsim$ 15–20 dB |
| $F_\text{SSB} = 2F_\text{DSB}$ | equal sideband conversion gain, no image filter | DSB 7 dB → SSB 10 dB |
| $F = F_\text{min} + \frac{4r_n|\Gamma_s-\Gamma_\text{opt}|^2}{(1-|\Gamma_s|^2)|1+\Gamma_\text{opt}|^2}$ | linear two-port, fixed bias/frequency | pHEMT at 1 GHz: $F_\text{min}$ 0.2–0.5 dB, $r_n$ 0.05–0.2 (device-dependent) |
| $T_\text{sys} = T_a + T_{e,\text{tot}}$ | system noise with a real antenna | GNSS 100 K + 90 K |

## Worked examples

**Example 1 — a three-stage heterodyne front end.** LNA: NF 1 dB, G 15 dB. Passive mixer: conversion loss 6 dB, NF 6 dB (SSB). IF amplifier: NF 4 dB, G 20 dB.
- Linear: $F_1 = 1.259$, $G_1 = 31.62$; $F_2 = 3.981$, $G_2 = 0.251$; $F_3 = 2.512$.
- $F_\text{tot} = 1.259 + 2.981/31.62 + 1.512/(31.62\times0.251) = 1.259 + 0.0943 + 0.190 = 1.544$ ⇒ **NF = 1.89 dB**.
- The IF amplifier contributes more than the mixer because the mixer's *loss* amplifies its importance. (Checked `noise_friis_nparams.py` §1: 1.885 dB both ways.)

**Example 2 — where to put the LNA on a ground station.** Chain (all at 290 K): 3 dB cable, LNA (NF 0.8 dB, G 20 dB), LoRa module (NF 6 dB).
- Cable first: NF = 3.0 + [0.8 dB LNA + module] = **3.91 dB**.
- LNA first: NF = **1.04 dB**.
- No LNA at all: NF = 3 + 6 = **9.0 dB**.
(`noise_cascade.py` "loss BEFORE vs AFTER" section.) Moving the LNA from the receiver end to the antenna end is worth 2.9 dB here; the LNA versus nothing is worth 8 dB — at the cost of linearity (the cascade IIP3 falls from −2 to −22 dBm; see [dynamic-range-sfdr-blocking](dynamic-range-sfdr-blocking.md)).

**Example 3 — 915 MHz station with a SAW filter.** SAW (1.5 dB) → LNA (0.7 dB, 18 dB) → 10 m coax (2.6 dB) → SX1262-class module (NF 6 dB). Cascade NF = **2.55 dB**, vs 8.6 dB with the module at the end of the coax alone. In SF12/BW125 terms the sensitivity improves from −134.4 to −140.5 dBm (`noise_cascade.py` A1/A2). Note that the SAW's 1.5 dB appears one-for-one in the NF because it is first — the price of blocking protection.

**Example 4 — GNSS active antenna.** Patch feed loss 0.3 dB → LNA1 (0.8 dB, 17 dB) → SAW (1.2 dB) → LNA2 (1.5 dB, 12 dB) → 3 m RG-174 (~4.2 dB) → receiver (NF 3 dB, assumed). Cascade NF **1.19 dB**, of which the patch loss and LNA1 are 92 % of the noise (per-stage breakdown in `noise_cascade.py`). Remove the active electronics and use a passive patch on the same cable: NF **7.50 dB**, a $C/N_0$ loss of 8.8 dB at $T_a$ = 100 K. The net gain of the active chain (23.3 dB) stays within the 30 dB maximum external gain the u-blox MAX-M10S accepts in its default low-gain mode [10].

**Example 5 — an SSB receiver with a DSB-specified mixer.** A mixer datasheet quotes NF = 7 dB (DSB). In a superhet without image filtering, use 10 dB; with a good image-reject filter in front, the image-band noise is that of the filter's stopband termination (still ~290 K if the filter is reflective and the source is 290 K), so the effective figure depends on the filter — compute with the image noise explicitly.

## Practical notes
- **Measure the NF of what you build, not what the datasheet says.** Board losses (input matching network Q, ESD diode capacitance, a U.FL connector and a few cm of 1.13 mm cable at 1.5 GHz) add directly to NF. The Y-factor method with a calibrated noise source (ENR) is standard; see [17-test-measurement/noise-figure-measurement](../17-test-measurement/noise-figure-measurement.md) and Keysight AN 57-1 [8].
- **Second-stage correction:** a noise-figure analyzer measures the NF of DUT + analyzer and subtracts the analyzer's contribution using the Friis formula; with a low-gain DUT the correction becomes large and uncertain.
- **The LNA must be stable** with every source impedance the antenna might present (see [06-rf-circuits/amplifier-stability-and-biasing](../06-rf-circuits/amplifier-stability-and-biasing.md)); a masthead LNA facing a detuned antenna (ice, rain, wet foliage) can oscillate.
- **Bias-tee and power:** masthead LNAs are usually fed over the coax; include the bias-tee insertion loss in the chain.
- **LNA gain is not free:** more first-stage gain lowers NF but lowers the cascade IIP3 and P1dB by the same number of dB. Near a launch site with other transmitters (range radar, other teams' telemetry, 2 W of your own 433 MHz), too much LNA gain is a common cause of desensitisation.
- **LoRa modules:** the EBYTE E22/E220 UART modules include a PA and LNA; their effective NF is not specified. Treat the Semtech chip value (~6 dB, implied by the SX126x sensitivity table) as a conservative upper bound unless you measure it.

## Common mistakes & misconceptions
- **Putting NF in dB into the Friis formula** (or gains in dB). Convert to linear, compute, convert back.
- **"More gain later fixes a lossy front end."** No — after a loss, the SNR is already degraded; $F_\text{tot} \ge L\,F_2$.
- **"The LNA should go near the receiver where it is protected/powered."** Every dB of feeder between antenna and LNA is a dB of NF. Put it at the antenna (masthead), protect it with a limiter and a filter whose losses you account for.
- **Thinking the cascade can be quieter than the first stage.** $F_\text{tot} \ge F_1$ always.
- **Confusing SSB and DSB mixer figures** (3 dB error), or using a broadband Y-factor result for an image-rejecting receiver.
- **Using the conjugate input match and expecting $F_\text{min}$.** $\Gamma_\text{opt} \ne S_{11}^*$ in general (1.4 dB penalty in the example).
- **Quoting NF of an attenuator at other than 290 K as its loss.** A cold attenuator (e.g. a feeder at 250 K) has NF < loss; a hot one has NF > loss ($T_e = (L-1)T_p$).
- **Applying NF when the source is not at 290 K.** For a sky-pointing antenna use $T_\text{sys} = T_a + T_e$ rather than $-174 + \text{NF}$; the latter is conservative when $T_a < 290$ K and optimistic when $T_a > 290$ K (city, HF).
- **Forum myth: "negative noise figure."** A passive or active two-port referenced to a 290 K source cannot have NF < 0 dB. Claims of negative NF usually come from mis-calibrated measurements or from a cold, active termination (e.g. an actively cooled input) being mislabelled.

## How to simulate / verify
- **Measuring an SDR's NF**: use the dBFS/Hz scaling and power (not log) averaging of [14 FFT & windows](../14-sdr-dsp/fft-spectral-analysis-windows.md) with a calibrated input level or a noise source; measured NFs of common SDRs are tabulated in [14 SDR hardware survey](../14-sdr-dsp/sdr-hardware-survey.md), and the bench method in [17 noise-figure measurement](../17-test-measurement/noise-figure-measurement.md).
- `tools/verify/noise_cascade.py` — Friis cascade library with per-stage contributions, Monte-Carlo verification, worked ground-station and GNSS chains.
- `tools/verify/noise_friis_nparams.py` — derives noise parameters from a $v_n$–$i_n$ correlated model, verifies both standard $F(\Gamma_s)$ forms, noise-circle formulas, noise vs conjugate match, SSB/DSB.
- **scikit-rf:** `skrf.Network` supports noise parameters (`nfmin`, `g_opt`, `rn`) for devices supplied with noise data in Touchstone files; cascading noisy networks with `**` computes the cascade NF including mismatch — use it to check a hand calculation with real LNA S-parameter + noise files.
- **SPICE `.noise`** gives input-referred noise voltage of a circuit; convert to NF with $F = 1 + \overline{v_{n,\text{in}}^2}/(4kT_0R_sB)$ where $v_{n,\text{in}}$ excludes the source resistor's own noise.
- **Qucs-S / harmonic-balance tools** compute NF and noise circles for LNA design ([16-simulation-tools/rf-circuit-simulators-harmonic-balance](../16-simulation-tools/rf-circuit-simulators-harmonic-balance.md)).

## Open questions / gaps
- The effective NF of EBYTE E22-400T33D / E220-900T30D modules (with their integrated LNA and T/R switch) is not published; a Y-factor measurement would settle it (cross-domain: 15, 17).
- Real noise parameters for candidate LNAs (e.g. Mini-Circuits, Qorvo, Infineon sub-GHz and L1 LNAs) belong to [18-components-parts](../18-components-parts/lna-pa-gain-block-mmics.md); the example values here are illustrative.

## Sources
1. H. T. Friis, "Noise figures of radio receivers," *Proc. IRE* 32(7), 419–422 (1944). (peer-reviewed) — definition of noise figure for general two-ports; cascade formula.
2. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley 2012, §10.2 (noise figure, cascade, lossy line) and §12.3 (low-noise amplifier design, noise circles). (textbook)
3. H. Rothe and W. Dahlke, "Theory of noisy fourpoles," *Proc. IRE* 44(6), 811–818 (1956). (peer-reviewed) — $v_n$–$i_n$ representation.
4. H. A. Haus et al., "IRE standards on methods of measuring noise in linear twoports, 1959," *Proc. IRE* 48(1), 60–68 (1960). (standard) — $F = F_\text{min} + (R_n/G_s)|Y_s - Y_\text{opt}|^2$.
5. ITU-R P.372-13 (09/2016), §2 eq. (1)–(5). https://www.itu.int/rec/R-REC-P.372/en (standard) — operating noise factor with antenna/line losses.
6. B. Razavi, *RF Microelectronics*, 2nd ed., 2011, §2.3.4–2.3.6 (noise figure, cascade, noise matching) and ch. 6 (mixer noise, SSB/DSB). (textbook)
7. T. H. Lee, *The Design of CMOS Radio-Frequency Integrated Circuits*, 2nd ed., Cambridge 2004, ch. 11–12 (noise, LNA design, noise parameters, inductive degeneration). (textbook)
8. Keysight, *Fundamentals of RF and Microwave Noise Figure Measurements*, AN 57-1 (5952-8255E); and *Noise Figure Measurement Accuracy — The Y-Factor Method*, AN 57-2. https://www.keysight.com/us/en/assets/7018-06808/application-notes/5952-8255.pdf (app note) — definitions, Y-factor, second-stage correction, mixer DSB/SSB measurement caveats.
9. arXiv:2209.00287, "Correction to Friis noise factors" (2022). (preprint, not peer-reviewed) — alternative in-situ definition; noted, not adopted.
10. u-blox, *MAX-M10S Data sheet* UBX-20035208: external gain at RF_IN max 30 dB (low-gain mode), 40 dB (bypass); tracking sensitivity −166/−167 dBm with a good external LNA. https://www.u-blox.com (datasheet)
11. `tools/verify/noise_cascade.py`, `tools/verify/noise_friis_nparams.py` (this KB).
