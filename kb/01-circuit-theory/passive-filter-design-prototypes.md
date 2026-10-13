---
title: Passive LC filter design from low-pass prototypes
domain: 01-circuit-theory
slug: passive-filter-design-prototypes
tags: [filter, butterworth, chebyshev, elliptic, cauer, bessel, g-values, insertion-loss-method, frequency-transformation, impedance-scaling, group-delay, finite-q, harmonic-filter, bandpass, coupled-resonator, j-inverter, image-parameter, constant-k, m-derived, zobel]
prerequisites:
  - lumped-elements-impedance-admittance.md
  - resonance-and-q.md
  - two-port-networks-zyh-abcd.md
  - ../00-math-foundations/laplace-transfer-functions-bode.md
related:
  - transformers-coupled-inductors.md
  - energy-storage-and-reactive-power.md
  - ../03-transmission-lines-matching/s-parameters.md
  - ../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md
  - ../18-components-parts/filter-parts-saw-ceramic-ltcc.md
  - ../04-real-components-hf/capacitors-at-rf-mlcc.md
  - ../04-real-components-hf/inductors-at-rf.md
  - ../20-projects-recipes/bandpass-filter-design-walkthrough.md
  - ../19-regulations-safety/spectrum-allocation-ism-bands.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Passive LC filter design from low-pass prototypes

## Questions this page answers
- How do I design an LC low-pass, high-pass, band-pass or band-stop filter from tables?
- What are the g-values in filter tables and how do I scale them to 50 Ω and my frequency?
- Butterworth, Chebyshev, elliptic or Bessel — which should I use?
- What filter order do I need for a given attenuation?
- How do I design a harmonic filter for a 433 MHz LoRa power amplifier?
- Can I build a 902–928 MHz band-pass filter from chip inductors and capacitors? Why is the insertion loss so high?
- Why do the textbook band-pass element values come out as 0.3 pF and 100 nH?
- How much loss will component Q add to my filter?
- What is group delay and why does a sharp filter distort pulses?
- Why is my Bessel filter's cutoff in the wrong place?
- What are constant-k and m-derived filters, and should I still design with the image-parameter method?

## TL;DR
- **Method**: pick a response (Butterworth, Chebyshev, elliptic, Bessel) and order $N$ → read or compute normalised **g-values** (1 Ω, 1 rad/s) → **impedance-scale** by $Z_0$ and **frequency-scale** to $\omega_c$ → optionally **transform** LP→HP/BP/BS → add parasitics and finite Q → simulate → tune.
- Scaling: series $L=g_kZ_0/\omega_c$, shunt $C=g_k/(Z_0\omega_c)$.
- Butterworth $g_k=2\sin\frac{(2k-1)\pi}{2N}$; Chebyshev by a closed-form recursion (reproduces the Matthaei/Pozar tables to <3×10⁻⁴, script-verified).
- **Order needed** (Chebyshev, ripple $L_r$ dB, attenuation $A$ dB at $\omega_s/\omega_c$): $N\ge\cosh^{-1}\sqrt{\frac{10^{A/10}-1}{10^{L_r/10}-1}}\big/\cosh^{-1}(\omega_s/\omega_c)$.
- **433.92 MHz harmonic filter**, 0.1 dB ripple edge at 520 MHz: 5-pole Chebyshev gives only **25.5 dB at 868 MHz**; 7-pole gives **44.6 dB**; a 5th-order **elliptic** with its first zero placed on 867.8 MHz gives **62 dB with realistic Q** (99 dB ideal). Pass-band loss 0.56–0.85 dB with inductor Q = 40.
- **915 MHz band-pass**: the direct LP→BP transform yields unbuildable values (0.8 nH ∥ 36 pF, 100 nH + 0.3 pF). Use **coupled resonators** (J-inverters): 3.3 nH resonators with 0.84–2.0 pF coupling caps. With Q ≈ 52 parts: **2.6 dB loss for a 90 MHz-wide filter, ≈9 dB for 902–928 MHz** — narrow ISM filters need SAW/ceramic parts.
- **Loss from finite Q**: band-pass mid-band $\Delta L\approx4.343\sum g_k/(\mathrm{FBW}\,Q_u)$ dB; in general $\Delta L\approx8.686\,\delta\,\tau_g$ (δ = ω/Q for LP elements, ω₀/2Q for BP resonators). Both verified numerically.
- **Image-parameter (Zobel) filters** — constant-k sections plus m-derived sections (attenuation pole at $f_c/\sqrt{1-m^2}$) and m = 0.6 end half-sections — still work: a 10-reactor composite for the 433 MHz case gives 80 dB at 2f and ≥ 30 dB return loss to 0.92 $f_c$, but its response near cutoff is not controlled (−4.8 dB at $f_c$) and it needs more parts and loss (1.17 dB) than an insertion-loss design; use it for intuition and quick traps, not for a specified response.
- Group delay rises steeply at the band edge of sharp filters (Chebyshev N=5, 0.5 dB: 4.2 s at DC → 10.6 s at cutoff, normalised). Bessel is flat but its tables are usually **delay-normalised** (3-dB point at 1.76 rad/s for N=3) — rescale before use.

## Intuition (no math)
An LC ladder is a chain of alternating "gates": series inductors that get harder to push through as frequency rises, and shunt capacitors that leak more to ground as frequency rises. Each extra element adds another step of rejection above cutoff (about 6 dB per octave per element far out), and the art is choosing element values so that in the passband the reactances cancel into a nearly perfect 50 Ω path while in the stopband they compound.

The standard families are different compromises:
- **Butterworth** — as flat as possible at DC; gentle knee; moderate delay variation.
- **Chebyshev** — allow small, equal ripples in the passband and get a much sharper knee for the same number of parts.
- **Elliptic (Cauer)** — allow ripple in *both* bands and put **transmission zeros** (parallel-resonant traps) at chosen stopband frequencies: the sharpest transition for a given order, and deep notches exactly where you need them (e.g. a PA's 2nd harmonic).
- **Bessel (Thomson)** — sacrifice sharpness for constant delay, so pulses pass without ringing.

A **prototype** is a filter designed once for 1 Ω and a 1 rad/s cutoff. Everything else — 50 Ω, 433 MHz, band-pass — is a change of units (scaling) or a change of variable (frequency transformation) applied to that one design. That is why published tables of g-values can serve every application.

## The math

### Level 1 — responses, order and scaling

Filters are specified via the **insertion loss** (power loss ratio) $P_{LR}=P_{av}/P_{L}=1/|S_{21}|^2$ for a doubly terminated network. Normalised to cutoff $\omega_c=1$:

| Family | $\lvert S_{21}(\omega)\rvert^2$ | Notes |
|---|---|---|
| Butterworth | $1/(1+\omega^{2N})$ | −3.01 dB at ω = 1; asymptote 20N dB/decade |
| Chebyshev | $1/\big(1+\varepsilon^2T_N^2(\omega)\big)$, $\varepsilon^2=10^{L_r/10}-1$ | equal ripple $L_r$ up to ω = 1; $T_N(\omega)=\cosh(N\cosh^{-1}\omega)$ for ω > 1 |
| Elliptic | $1/\big(1+\varepsilon^2R_N^2(\omega)\big)$ | $R_N$ = Chebyshev rational function; finite zeros in stopband |
| Bessel | all-pole with maximally flat group delay | poor selectivity; linear phase |

Order selection (to meet $A$ dB at $\omega_s$): Butterworth $N\ge\dfrac{\log_{10}\left[(10^{A/10}-1)/(10^{L_r/10}-1)\right]}{2\log_{10}\omega_s}$ (with $L_r=3.01$ dB for the usual 3-dB definition); Chebyshev as in the TL;DR. Example: 45 dB at $868/520=1.669$ with 0.1 dB ripple needs Chebyshev $N\ge7.05$ — the script shows N = 7 reaching 44.6 dB, consistent.

**Scaling** a prototype (source $g_0=1$ Ω, elements $g_1\dots g_N$, load $g_{N+1}$) to impedance $Z_0$ and cutoff $\omega_c$:
$$L_k=\frac{g_kZ_0}{\omega_c},\qquad C_k=\frac{g_k}{Z_0\,\omega_c},\qquad R_{load}=g_{N+1}Z_0\ \text{(or }Z_0/g_{N+1}\text{)}.$$
In the ladder, odd-indexed elements are shunt C and even-indexed series L (or the dual: series L first). $g_{N+1}$ is a resistance if $g_N$ is a shunt C and a conductance if $g_N$ is a series L.

### Level 2 — g-values and frequency transformations

**Butterworth:** $g_k=2\sin\!\left[\dfrac{(2k-1)\pi}{2N}\right]$, $g_{N+1}=1$.

**Chebyshev** (ripple $L_r$ dB): $\beta=\ln\coth\dfrac{L_r}{17.37}$, $\gamma=\sinh\dfrac{\beta}{2N}$, $a_k=\sin\dfrac{(2k-1)\pi}{2N}$, $b_k=\gamma^2+\sin^2\dfrac{k\pi}{N}$;
$g_1=2a_1/\gamma$, $g_k=\dfrac{4a_{k-1}a_k}{b_{k-1}g_{k-1}}$; $g_{N+1}=1$ ($N$ odd) or $\coth^2(\beta/4)$ ($N$ even — even-order Chebyshev filters need unequal terminations, one reason odd orders are preferred).

Values reproduced by `tools/verify/circuits_filter_prototypes.py` (and checked against Matthaei/Pozar tables):

| Response | N | $g_1\dots g_{N}$ |
|---|---|---|
| Butterworth | 5 | 0.6180, 1.6180, 2.0000, 1.6180, 0.6180 |
| Chebyshev 0.1 dB | 3 | 1.0316, 1.1474, 1.0316 |
| Chebyshev 0.1 dB | 5 | 1.1468, 1.3712, 1.9750, 1.3712, 1.1468 |
| Chebyshev 0.5 dB | 5 | 1.7058, 1.2296, 2.5408, 1.2296, 1.7058 |
| Bessel (τ(0) = 1 s) | 3 | 1.2550, 0.5528, 0.1922 (series-L first) |
| Bessel (τ(0) = 1 s) | 5 | 0.9303, 0.4577, 0.3312, 0.2090, 0.0718 |
| Elliptic 0.1 dB / 50 dB | 5 | C1 0.8967; L2 1.0385 ∥ C2 0.3124; C3 1.7117; L4 1.2549 ∥ C4 0.1109; C5 1.0583 (zeros at 1.756, 2.680 rad/s) |

The elliptic row was obtained by fitting a doubly-terminated ladder to SciPy's elliptic transfer function with the transmission zeros fixed (max error < 0.001 dB); Zverev's handbook tabulates such designs directly. The Bessel ladder reproduces SciPy's delay-normalised Bessel response exactly; its 3-dB frequency is 1.756 rad/s (N=3) and 2.427 rad/s (N=5), so **divide the g-values by the 3-dB frequency if you want the 3-dB point at 1 rad/s**.

**Frequency transformations** ($\omega_0=\sqrt{\omega_1\omega_2}$, $\mathrm{FBW}=(\omega_2-\omega_1)/\omega_0$):

| Prototype element | Low-pass | High-pass | Band-pass | Band-stop |
|---|---|---|---|---|
| series $g_k$ (L) | $L=\dfrac{g_kZ_0}{\omega_c}$ | series $C=\dfrac{1}{g_kZ_0\omega_c}$ | series $L=\dfrac{g_kZ_0}{\omega_0\mathrm{FBW}}$, $C=\dfrac{\mathrm{FBW}}{\omega_0g_kZ_0}$ | series $L\parallel C$: $L=\dfrac{g_kZ_0\mathrm{FBW}}{\omega_0}$, $C=\dfrac{1}{\omega_0g_kZ_0\mathrm{FBW}}$ |
| shunt $g_k$ (C) | $C=\dfrac{g_k}{Z_0\omega_c}$ | shunt $L=\dfrac{Z_0}{g_k\omega_c}$ | shunt $L\parallel C$: $L=\dfrac{Z_0\mathrm{FBW}}{\omega_0g_k}$, $C=\dfrac{g_k}{\omega_0Z_0\mathrm{FBW}}$ | shunt series-LC: $L=\dfrac{Z_0}{\omega_0g_k\mathrm{FBW}}$, $C=\dfrac{g_k\mathrm{FBW}}{\omega_0Z_0}$ |

The band-pass mapping is $\omega'=\dfrac{1}{\mathrm{FBW}}\left(\dfrac{\omega}{\omega_0}-\dfrac{\omega_0}{\omega}\right)$: the response is geometrically (not arithmetically) symmetric about $\omega_0$.

### Level 3 — real-world corrections

**Finite component Q.** With uniform unloaded Q the lossy response is the lossless one evaluated at a complex-shifted frequency, which gives the general **delay–loss rule**
$$\Delta L(\omega)\approx8.686\,\delta\,\tau_g(\omega)\ \text{dB},\qquad \delta=\omega/Q\ (\text{LP/HP elements}),\quad\delta=\omega_0/(2Q_u)\ (\text{BP resonators}).$$
At band-pass centre this reduces to Cohn's formula $\Delta L_0\approx4.343\sum_kg_k/(\mathrm{FBW}\,Q_u)$ dB. The script confirms the LP rule to <1 % (0.847 dB simulated vs 0.844 dB predicted at 433.92 MHz with Q = 40) and the BP formula to within ~5 % (2.61 vs 2.67 dB; 8.96 vs 9.41 dB). Consequences: loss scales with **1/FBW** and with the **sum of g** (i.e. with order and sharpness); it is largest at the band edges where $\tau_g$ peaks; and deep elliptic notches are limited by the Q of the trap (99 dB ideal → 62 dB with Q = 40/300).

**Impedance inverters and coupled resonators.** For narrow band-pass filters the direct transform produces extreme values (tiny series C, huge series L, sub-nH shunt L). The fix is to replace series resonators by shunt resonators separated by **admittance inverters** $J$ (realised as small coupling capacitors or a capacitive π), giving the **coupled-resonator** design (Matthaei ch. 8; Hong & Lancaster ch. 3). With identical shunt resonators $L_r$, $C_r$ (susceptance slope $b=\omega_0C_r$) and terminations $Y_0$:
$$J_{01}=\sqrt{\frac{Y_0\,b\,\mathrm{FBW}}{g_0g_1}},\quad J_{k,k+1}=\frac{\mathrm{FBW}\,b}{\sqrt{g_kg_{k+1}}},\quad J_{N,N+1}=\sqrt{\frac{Y_0\,b\,\mathrm{FBW}}{g_Ng_{N+1}}},$$
internal coupling $C_{k,k+1}=J_{k,k+1}/\omega_0$; end coupling $C_{01}=J_{01}/\big(\omega_0\sqrt{1-(J_{01}/Y_0)^2}\big)$; each resonator's own shunt capacitor is reduced by the adjacent coupling capacitances (the end ones by $C_{01}/[1+(\omega_0C_{01}Z_0)^2]$). You choose $L_r$ to get convenient values. The approximations are narrow-band; the 10 % design in the script lands 0.7 % high and is re-centred by scaling all capacitors by 1.018.

**Group delay.** $\tau_g=-d\phi/d\omega$. Prototype delays (script §5): Butterworth N=5: 3.24 s at DC, 5.15 s at 0.9ω_c; Chebyshev 0.5 dB N=5: 4.21 s → 6.84 s at 0.9ω_c → 10.6 s at ω_c. Scaled delay is $\tau/\omega_c$ (e.g. ÷ 2π·520 MHz → ns). For LoRa or FSK signals whose bandwidth is ≪ the filter's, delay variation is irrelevant; for radar pulses or wideband data it causes ringing and inter-symbol interference.

**Parasitics and limits.** Every inductor has SRF, every capacitor ESL; pads add ~0.05–0.2 pF, and ground vias ~0.3–0.6 nH ([PCB parasitics](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md)). In an elliptic LPF the shunt-capacitor ground via inductance creates spurious series resonances that can ruin stopband attenuation at 2–3 GHz; use two vias per shunt capacitor and simulate with vendor S-parameter models ([component models](../04-real-components-hf/component-models-s2p-spice.md)).

### Level 3b — image-parameter filters (constant-k and m-derived)
Before the insertion-loss method became practical, filters were designed by the **image-parameter method** (Campbell, Zobel 1923). It is still the language behind "constant-k" and "m-derived" sections in old handbooks and amateur designs, and it explains *why* a shunt series-LC trap gives a notch.

**Image parameters of a section.** A symmetric T section has series arms $Z_1/2$ and a shunt arm $Z_2$; the π section has shunt arms $2Z_2$ and series arm $Z_1$. The **image impedance** is the termination that, placed on one side, makes the other side look the same; for the T and π,
$$Z_{iT}=\sqrt{Z_1Z_2\Big(1+\frac{Z_1}{4Z_2}\Big)},\qquad Z_{i\pi}=\frac{Z_1Z_2}{Z_{iT}},\qquad \cosh\gamma=1+\frac{Z_1}{2Z_2},$$
where $\gamma=\alpha+j\beta$ is the image propagation constant per section (from the section's ABCD matrix: $Z_{iT}=\sqrt{B/C}$, $\cosh\gamma=A$; checked to machine precision, `tools/verify/s6_image_filters.py` §1). A cascade of identical sections terminated in its image impedance has exactly $N\gamma$ of loss and phase — the idea is "design each section in isolation".

**Constant-k low-pass.** $Z_1=j\omega L$, $Z_2=1/(j\omega C)$, so $Z_1Z_2=L/C=R_0^2$ is constant (hence the name). Then $Z_{iT}=R_0\sqrt{1-(\omega/\omega_c)^2}$ with $\omega_c=2/\sqrt{LC}$, giving the design equations $L=2R_0/\omega_c$, $C=2/(R_0\omega_c)$. In the stop band $\alpha=2\cosh^{-1}(\omega/\omega_c)$ Np per section. For $R_0$ = 50 Ω, $f_c$ = 520 MHz: L = 30.61 nH (two 15.3 nH arms in a T), C = 12.24 pF; one section gives 19.1 dB at 867.8 MHz and 27.2 dB at 1301.8 MHz (image-matched). Its weakness is the image impedance: it falls from $R_0$ to 0 (T) or rises to ∞ (π) across the pass band, so a section between real 50 Ω terminations is mismatched near cutoff.

**m-derived sections.** Keep $Z_{iT}$ unchanged but reshape the arms: series $mZ_1$, shunt $Z_2/m+\frac{1-m^2}{4m}Z_1$ (0 < m < 1). For the low-pass this shunt arm is $mC$ in series with $\frac{1-m^2}{4m}L$ — a series resonator that **shorts the line at** $\omega_\infty=\omega_c/\sqrt{1-m^2}$, an attenuation pole you can place on a harmonic: for 867.8 MHz with $f_c$ = 520 MHz, m = 0.8006 (shunt arm 9.80 pF + 3.43 nH). The same section's $Z_{i\pi}$ varies with m, and **m = 0.6** makes it flattest: within 4.0 % of $R_0$ up to $0.8f_c$ (10.5 % to $0.9f_c$), against 67 % for the constant-k π. Bisected m = 0.6 half-sections are therefore used as **end terminations**: their inner face presents the constant-k $Z_{iT}$ and their outer face presents ≈ $R_0$ (they also add a pole at $f_c/\sqrt{0.64}=1.25f_c$).

**Composite filter for the 433 MHz harmonic case** (same $f_c$ = 520 MHz as Example A): m = 0.6 half-section – constant-k T – m-derived T (pole on 2f) – m = 0.6 half-section. After merging series inductors: 24.5 – 27.6 – 21.4 nH in series; shunt arms 3.67 pF + 16.3 nH (ends, pole 650 MHz), 12.24 pF, and 9.80 pF + 3.43 nH (pole 868 MHz) — 6 inductors and 4 capacitors. Doubly terminated in 50 Ω (script §4):

| Design | Reactors | IL @ 433.92 MHz ($Q_L$ 40, $Q_C$ 300) | 2f / 3f attenuation | Pass-band match |
|---|---|---|---|---|
| Image-parameter composite | 10 | 1.17 dB | 79.6 / 58.8 dB | RL ≥ 30 dB to 480 MHz (ideal), but 6.9 dB at 505 MHz, |S21| −4.8 dB at 520 MHz |
| Chebyshev 0.1 dB, N = 7 (Example A) | 7 | 0.85 dB | 44.7 / 73.1 dB | RL ≥ 16.4 dB to the 520 MHz ripple edge, by design |
| Elliptic N = 5 (Example A) | 7 (5 + 2 trap C) | 0.64 dB | 61.6 / 71.0 dB | RL ≥ 16.4 dB to the edge |

The composite works — better than expected near DC — but the image method cannot guarantee the response, because real terminations are not the image impedances near cutoff and the section interactions are ignored. The insertion-loss method specifies $|S_{21}|^2$ exactly and synthesises the minimum number of elements for it, which is why it replaced the image method for anything with a specification.

## Design equations & rules of thumb

| Item | Equation / rule | Notes |
|---|---|---|
| Scale L | $L=g Z_0/\omega_c$ | 50 Ω, 520 MHz: g = 1 → 15.3 nH |
| Scale C | $C=g/(Z_0\omega_c)$ | 50 Ω, 520 MHz: g = 1 → 6.12 pF |
| Chebyshev order | $N\ge\cosh^{-1}\sqrt{(10^{A/10}-1)/(10^{L_r/10}-1)}/\cosh^{-1}(\omega_s/\omega_c)$ | — |
| Asymptotic roll-off | ≈ 20N dB/decade (6N dB/octave) | all-pole types |
| Ripple ↔ return loss | $RL=-10\log_{10}(1-10^{-L_r/10})$ | 0.1 dB ↔ 16.4 dB; 0.01 dB ↔ 26.4 dB; 0.5 dB ↔ 9.6 dB |
| BP mid-band loss | $4.343\sum g/(\mathrm{FBW}\,Q_u)$ dB | Cohn |
| General loss | $8.686\,\delta\,\tau_g$ | uniform Q |
| Harmonic LPF edge | ripple edge ≈ 1.1–1.25 × carrier | trade loss vs 2f rejection |
| Narrow BP from chip L | FBW ≲ 5 % ⇒ IL of several dB | use SAW/BAW/ceramic |
| Constant-k LP | $L=2R_0/\omega_c$, $C=2/(R_0\omega_c)$; $\alpha=2\cosh^{-1}(\omega/\omega_c)$ Np/section | 50 Ω, 520 MHz: 30.6 nH, 12.2 pF |
| m-derived pole | $\omega_\infty=\omega_c/\sqrt{1-m^2}$; shunt $mC$ + $\frac{1-m^2}{4m}L$ | pole on 2f of 433.92: m = 0.80 |
| End sections | bisected m = 0.6 half-sections | $Z_{i\pi}$ within 4 % to 0.8 $f_c$ |

## Worked examples

### A. Harmonic low-pass filter after a 433.92 MHz LoRa PA
**Goal:** pass 433.92 MHz with < 1 dB loss and good return loss; attenuate 2f = 867.8 MHz, 3f = 1301.8 MHz. Regulatory spurious limits for SRDs are typically in the −30 to −54 dBm range depending on region and band (see [spectrum allocation](../19-regulations-safety/spectrum-allocation-ism-bands.md)); with a +33 dBm carrier and a PA whose raw 2nd harmonic is, say, −25 dBc (+8 dBm), you need ≳ 45–60 dB at 2f. (Module makers such as EBYTE include a filter; this example is for a discrete PA design.)

Choose 0.1 dB Chebyshev (in-band return loss 16.4 dB) with ripple edge $f_c=520$ MHz (20 % margin for tolerances).

| Design | Elements (50 Ω) | IL @ 433.92 (Q_L 40, Q_C 300) | Atten. @ 2f / 3f / 4f |
|---|---|---|---|
| Chebyshev N=5 | 7.02 pF – 20.98 nH – 12.09 pF – 20.98 nH – 7.02 pF | 0.56 dB | 25.6 / 45.8 / 59.1 dB |
| Chebyshev N=7 | 7.23 pF – 21.77 nH – 12.83 pF – 24.08 nH – 12.83 pF – 21.77 nH – 7.23 pF | 0.85 dB | 44.7 / 73.1 / 91.7 dB |
| Elliptic N=5, zero on 2f ($f_c$ = 494.3 MHz) | 5.77 pF – (16.72 nH ∥ 2.012 pF) – 11.02 pF – (20.20 nH ∥ 0.714 pF) – 6.81 pF | 0.64 dB | 61.6 / 71.0 / 52.4 dB |

(All from `tools/verify/circuits_filter_prototypes.py` §6; the ideal elliptic reaches 99 dB at 2f — finite Q of the trap limits it to 62 dB.) Practical realisation: round to E24/E48 values (e.g. 5.6 pF, 16 nH ∥ 2.0 pF, 11 pF, 20 nH ∥ 0.7 pF, 6.8 pF), use C0G capacitors rated ≥ 50 V and high-Q wirewound/ceramic inductors with SRF well above 1.3 GHz, then **re-tune on the bench**: parasitic pad capacitance lowers the trap frequencies. Check element stress: at 2 W in 50 Ω the line voltage is 14 V peak and currents are 0.28 A peak — well within 0402/0603 ratings, but the trap's internal circulating current is Q-times larger near its resonance ([reactive power](energy-storage-and-reactive-power.md)).

### B. 915 MHz band-pass (3-pole Chebyshev 0.1 dB)
**(i) Direct transform, FBW = 10 %:** shunt resonators 0.843 nH ∥ 35.9 pF and a series resonator 99.8 nH + 0.303 pF. The 0.84 nH is comparable to a via; 100 nH is near its SRF at 915 MHz; 0.3 pF is a pad. Not buildable.

**(ii) Coupled shunt resonators** with $L_r=3.3$ nH ($C_r=9.17$ pF): $C_{01}=C_{34}=2.04$ pF, $C_{12}=C_{23}=0.843$ pF, resonator shunt capacitors 6.81, 7.48, 6.81 pF. Simulated: ripple band ≈ 870–960 MHz, 3-dB bandwidth 131 MHz. With Q_L = 60 (Coilcraft 0402HP-3N3 has Q ≈ 66 at 900 MHz) and Q_C = 400: **mid-band IL 2.6 dB** (Cohn estimate 2.67 dB). Rejection: 92 dB at 433.92 MHz, 45 dB at 1830 MHz, 50 dB at 2745 MHz.

**(iii) The same topology for 902–928 MHz (FBW 2.84 %):** coupling capacitors 0.97 and **0.24 pF** (below practical tolerance) and **IL ≈ 9.0 dB**. A 9 dB loss in front of a LoRa receiver adds 9 dB to its noise figure. This is the quantitative reason ISM front-ends use SAW filters (typ. 1.5–3 dB IL for this bandwidth) or ceramic/LTCC parts ([filter parts](../18-components-parts/filter-parts-saw-ceramic-ltcc.md)).

## Practical notes
- **Component choice.** Capacitors: C0G/NP0, RF series (Murata GJM/GQM, Johanson, ATC), ±0.1 pF or ±2 %. Inductors: wirewound ceramic (Coilcraft 0402HP/0603HP, Murata LQW) for Q; multilayer (Murata LQG) are cheaper but Q ≈ 10–20 lower. Check SRF ≥ 2–3× the highest frequency where the element must still be an inductor — for harmonic filters that means SRF above 3f.
- **Layout.** Keep shunt capacitors' ground connections short with ≥ 2 vias; place series inductors in line with 50 Ω traces; orient adjacent inductors at 90° to reduce coupling; keep the input and output ends of the filter physically separated or shielded, otherwise stopband "leakage" around the filter (tens of dB at GHz) defeats the design ([RF layout](../13-pcb-rf-layout-emc/rf-layout-rules.md)).
- **Tolerance.** Run a Monte-Carlo (±2 % L, ±0.1 pF C) in the simulator; a 0.1 dB Chebyshev may degrade to ~0.5 dB ripple and ~12 dB return loss — acceptable for a harmonic filter.
- **Tuning.** Most practical UHF filters are tuned once on a VNA with the final layout, then frozen. Expect trap resonances to move down by a few percent due to pad capacitance.
- **Power handling.** Shunt capacitor voltage ≈ line voltage (14 V peak at 2 W/50 Ω); trap LC elements see circulating current. Inductor current rating (Irms) must cover the RF current plus DC if biased.

## Common mistakes & misconceptions
- **Forgetting that even-order Chebyshev prototypes have $g_{N+1}\ne1$.** An N = 4, 0.5 dB design has a 1.984 Ω load — built between 50 Ω ports it mismatches. Use odd N or an impedance-transforming design.
- **Using delay-normalised Bessel tables as if 3-dB-normalised.** Your cutoff will be 1.76× (N = 3) to 2.43× (N = 5) higher than intended.
- **Designing a harmonic LPF with its cutoff at the carrier.** Ripple edges and 3-dB points are not the same; put the ripple edge 10–25 % above the carrier.
- **Ignoring component Q** and then being surprised by several dB of loss in a narrow band-pass. Compute $4.343\sum g/(\mathrm{FBW}Q_u)$ *before* committing to a lumped design.
- **Trusting ideal elliptic notch depths.** 80–100 dB notches collapse to 40–60 dB with real Q, and to less with via inductance and coupling around the filter.
- **Arithmetic-symmetric band-pass expectations.** LP→BP transformed responses are symmetric on a log-frequency axis; lower skirt is steeper in hertz.
- **Treating an image-parameter cutoff like a ripple edge.** The constant-k $f_c$ is where attenuation starts in an image-matched chain; between 50 Ω terminations the composite above is already −1 dB at 0.97 $f_c$ and −4.8 dB at $f_c$, with poor return loss — leave more margin, or use the insertion-loss method.
- **Stopband measured through a poor layout.** 70 dB of theoretical rejection requires a shielded, well-grounded layout; open-board coupling often limits you to 40–50 dB at GHz.

## How to simulate / verify
- `python3 tools/verify/circuits_filter_prototypes.py` — computes g-values and checks them against tables, simulates prototypes (Butterworth −3.01 dB at ω = 1, Chebyshev ripple and stopband formula), verifies Bessel against SciPy, fits the elliptic ladder, checks the delay–loss rule, designs examples A and B with finite Q, and cross-checks example A against scikit-rf to $10^{-15}$.
- scikit-rf: `rf.media.DefinedGammaZ0(freq, z0_port=50)` provides `.inductor()`, `.capacitor()`, `.shunt_capacitor()`, `.shunt_inductor()`; cascade with `**`. Replace ideal elements with vendor `.s2p` files for realism.
- `python3 tools/verify/s6_image_filters.py` — image impedance and γ vs ABCD, constant-k stop-band attenuation, m-derived pole, m = 0.6 flatness, composite 433 MHz filter vs Chebyshev N = 5/7 with finite Q. All pass.
- Free design tools: QUCS-S filter synthesis, RFSim99, Marki/"Filter Solutions" (Nuhertz) and Iowa Hills filter designer produce ladder values; LTspice for `.ac` checks; openEMS/Sonnet Lite for layout effects ([simulation tools](../16-simulation-tools/tool-landscape-overview.md)).
- Bench: NanoVNA/LibreVNA two-port measurement; verify stopband with ≥ 70 dB dynamic range (LibreVNA) — the NanoVNA's ~60–70 dB range may limit what you can see.

## Open questions / gaps
- Elliptic values here are fitted numerically rather than taken from Zverev's tables; they satisfy the response to < 0.001 dB but have not been cross-checked against a printed table entry (low risk).
- Regulatory harmonic limits for Singapore IMDA vs ETSI EN 300 220 vs FCC Part 15 are summarised in domain 19, not here.

## Sources
1. G. L. Matthaei, L. Young, E. M. T. Jones, *Microwave Filters, Impedance-Matching Networks, and Coupling Structures*, McGraw-Hill 1964 / Artech reprint 1980 — §4.05 (Butterworth/Chebyshev element formulas and Tables 4.05-1/2), §4.07 (maximally flat delay), §4.13 (dissipation loss), ch. 8 (coupled-resonator band-pass via inverters). (textbook)
2. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — §8.3 (insertion-loss method, Tables 8.3–8.4), §8.4 (scaling and transformations), §8.5 (implementation). (textbook)
3. A. I. Zverev, *Handbook of Filter Synthesis*, Wiley, 1967 — elliptic and Bessel ladder tables, normalisation conventions. (textbook)
4. A. B. Williams, F. J. Taylor, *Electronic Filter Design Handbook*, 4th ed., McGraw-Hill, 2006 — order nomographs, delay tables, LC implementation. (textbook)
5. J.-S. Hong, M. J. Lancaster, *Microstrip Filters for RF/Microwave Applications*, 2nd ed., Wiley, 2011 — ch. 3 (J/K inverter formulas, coupled-resonator design). (textbook)
6. S. B. Cohn, "Dissipation loss in multiple-coupled-resonator filters," *Proc. IRE*, 47(8), 1342–1348, 1959 — mid-band loss vs g-values and Q. (peer-reviewed)
7. M. B. Steer, *Microwave and RF Design IV: Modules*, §2.7 "Butterworth and Chebyshev filters", LibreTexts, 2026 — closed-form g-values incl. $\beta=\ln\coth(L_r/17.37)$. https://eng.libretexts.org/Bookshelves/Electrical_Engineering/Electronics/Microwave_and_RF_Design_IV:_Modules_(Steer)/02:_Filters/2.07:_Butterworth_and_Chebyshev_Filters (textbook, open)
8. Stanford EE133 "Cookbook Filter Guide" (2002) — Butterworth/Chebyshev/Bessel tables and LP→BP recipe. https://web.stanford.edu/class/ee133/handouts/labs/EE133filterCookbook.pdf (lecture notes)
9. Coilcraft 0402HP datasheet, Doc 526 (2023) — Q ≈ 66 at 900 MHz for 3.3 nH. (datasheet)
10. Verification script `tools/verify/circuits_filter_prototypes.py` (this KB).
11. O. J. Zobel, "Theory and design of uniform and composite electric wave-filters," *Bell System Technical Journal*, vol. 2, no. 1, pp. 1–46, 1923 — constant-k and m-derived sections, composite filters. (peer-reviewed, historical)
12. D. M. Pozar, *Microwave Engineering*, 4th ed., 2012, §8.2 (image-parameter method: image impedances, constant-k and m-derived sections, composite filters); Matthaei, Young & Jones (above), ch. 3. (textbook)
13. Verification script `tools/verify/s6_image_filters.py` (this KB). (numerical check)
