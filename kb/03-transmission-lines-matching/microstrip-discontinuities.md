---
title: Microstrip discontinuities — open ends, gaps, steps, bends and mitres, T-junctions and vias
domain: 03-transmission-lines-matching
slug: microstrip-discontinuities
tags: [microstrip, discontinuity, open-end, end-effect, length-extension, kirschning-jansen-koster, hammerstad, gap, dc-block, step-in-width, bend, corner, mitre, mitred-bend, douville-james, t-junction, tee, via, goldfarb-pucel, excess-capacitance, equivalent-circuit, openems, qucs]
prerequisites:
  - planar-lines-microstrip-stripline-cpwg.md
  - input-impedance-stubs-quarter-wave.md
  - s-parameters.md
related:
  - time-domain-reflectometry.md
  - impedance-matching-lumped-and-distributed.md
  - ../04-real-components-hf/pcb-parasitics-traces-vias-pads.md
  - ../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md
  - ../06-rf-circuits/couplers-dividers-combiners.md
  - ../13-pcb-rf-layout-emc/rf-layout-rules.md
  - ../13-pcb-rf-layout-emc/vias-stitching-fencing.md
  - ../16-simulation-tools/openems-workflow.md
  - ../16-simulation-tools/em-solvers-fdtd-mom-fem.md
  - ../17-test-measurement/resonator-and-cavity-perturbation-permittivity-measurement.md
level: mixed
confidence: medium
last_updated: 2026-10-14
---

# Microstrip discontinuities — open ends, gaps, steps, bends and mitres, T-junctions and vias

## Questions this page answers
- Why is my open-circuit stub resonating low, and how much shorter should I cut it?
- What is an "excess capacitance" and why do discontinuities look like little L and C networks?
- Why does a 75 % mitre perform worse than a 57 % one?
- What is the Kirschning–Jansen–Koster open-end formula, and how accurate is it?
- Does a 90° corner in a 50 Ω trace matter at 433 MHz, 915 MHz, 2.4 GHz or 5.8 GHz?
- How much should I mitre a bend? Is 45° chamfering always right?
- Can a gap in a microstrip work as a DC block?
- How big is the parasitic of a step in width (for example a 2.8 mm trace necking down to an SMA or U.FL pad)?
- How do I model a microstrip T-junction in a power splitter or stub filter?
- How much inductance does a ground via add to a shorted stub?
- When do the closed-form models stop working and I have to run an EM simulation?

## TL;DR
- Every place where a microstrip changes shape stores extra field energy. Excess **electric** energy behaves like a shunt capacitor, and excess **magnetic** energy like a series inductor. A few fF and pH are enough for a good model below ~10 GHz on PCB substrates.
- **Open end:** the fringing field makes the line look **Δl ≈ 0.35–0.45 h longer**. On the 2-layer board (h 1.51 mm, εr 4.5, 50 Ω) Δl = **0.60 mm** by Kirschning–Jansen–Koster (KJK), which is a 0.6 mm cut-back on a 44.4 mm λ/4 stub at 915 MHz. On JLC-7628 (h 0.21 mm), Δl = **0.085 mm**, which is negligible. Three closed forms agree within 5 % for 50 Ω lines. openEMS, converged to 0.5 % between meshes, gives **11–18 % more** than KJK. That is a **pre-registered miss**, but it amounts to only 0.07 mm.
- **90° square corner** (2-layer, 50 Ω): KJK gives C = 0.31 pF and L = 42 pH per arm. That predicts **|S11| −28 / −19.5 / −12 dB at 0.915 / 2.45 / 5.8 GHz**, and openEMS agrees within **0.7 dB**. On JLC-7628 the same corner is −45 / −36.5 / −29 dB, so it is harmless.
- **Optimal mitre (Douville & James 1978):** $x/d = 0.52 + 0.65\,e^{-1.35W/h}$ (d = corner diagonal = W√2). This gives **57 %** for 50 Ω on FR-4. In openEMS it improves the 2-layer corner by **16 dB at 2.45 GHz (−36 dB)**. A 50 % mitre gives −29 dB and a 75 % mitre −24 dB.
- **Gaps** are weak series capacitors: 0.07–0.11 pF on 1.5 mm FR-4, |S21| ≈ −16 dB at 2.45 GHz. **They are not DC blocks at UHF.** Use a capacitor, or an interdigital or coupled-line section.
- **Steps in width:** the parasitics are tiny (2.8 → 1.0 mm: 23 fF, 60 pH). What matters is the *length* of the narrow section, which acts as a short high-Z line. Gupta's step formula is only valid for W1/W2 ≤ 3.5.
- **T-junctions** (Hammerstad 1981) mainly shift the reference planes: by 0.34 mm along the main arm and 1.9 mm along the side arm on the 2-layer board. |S11| stays within 0.1 dB of the ideal −9.54 dB up to 2.45 GHz. On JLC-7628 the junction is ideal to 5.8 GHz.
- **Via to ground (Goldfarb–Pucel):** 0.50 nH through 1.51 mm with a 0.3 mm drill, which makes a shorted stub look **1.6 mm longer** at 915 MHz. On 0.21 mm prepreg it is 15 pH. Verified by `tools/verify/e11_discontinuities.py` (15/18 checks) and `e11_discontinuities_openems.py`.

## Intuition (no math)
A uniform microstrip has a fixed ratio of electric to magnetic energy per millimetre, and that ratio *is* its characteristic impedance. Wherever the strip ends, widens, turns or branches, the field near the change differs from the field of the uniform line. It bulges out past an open end, crowds into the outside corner of a bend, and spreads into the extra metal of a junction. The difference between the real field and "two ideal lines butted together" is the **excess** field.

- Excess charge, as at an open end, a wide corner or a step to a wider line, stores electric energy. It acts as a **shunt capacitance**.
- Current that has to swerve or crowd, as round a corner, through a step to a narrower line or down a via, stores excess magnetic energy. It acts as a **series inductance**.

An open end is the clearest case. The charge does not stop at the copper edge: field lines curl out beyond it and down to the ground plane. The end therefore holds a little more charge than an ideal open, which is the same as a slightly longer line. A square corner has a patch of copper on the outside of the bend that carries almost no current but adds capacitance to ground. Cutting it off (mitring) removes that capacitance, while the narrower path round the inside slightly increases the inductance. At the right mitre the two effects cancel, which is why the optimum is near 50–60 % and not 100 %.

The size of every parasitic scales with the substrate height h. That is the main practical lesson: **on a thin prepreg (JLC-7628, h = 0.21 mm) all of these effects are 7× smaller** than on a 1.5 mm two-layer board. Below about 1 GHz on thin boards you can usually ignore them.

## The math

### Level 1 — the equivalent circuits and the numbers that matter

| Discontinuity | Equivalent circuit | Size scale | Rule-of-thumb value (50 Ω, FR-4) |
|---|---|---|---|
| Open end | shunt $C_{oc}$, or extra length $\Delta l$ | $\Delta l\sim0.4h$ | 0.60 mm (h 1.51), 0.085 mm (h 0.21) |
| Gap, spacing s | π-network: series $C_s$, shunt $C_{p1}$, $C_{p2}$ | $C_s\sim0.1$ pF at s ≪ h | |S21| ≈ −16 dB at 2.45 GHz (h 1.51) |
| Step W1 → W2 | shunt $C$, series $L_1$, $L_2$ | fF, pH | 2.8 → 1.0 mm: 23 fF, 60 pH |
| 90° corner | T-network: $L$–$C$–$L$ | $C\propto W$, $L\propto h$ | 0.31 pF, 42 pH/arm (h 1.51) |
| Mitred corner | T-network with smaller C | | best near $x/d$ = 57 % |
| T-junction | shifted reference planes + transformer + shunt $B_T$ | $d\sim0.055\,D$ | plane shifts 0.34 / 1.9 mm (h 1.51) |
| Via to ground | series $R + j\omega L$ | $L\approx\frac{\mu_0h}{2\pi}\ln\frac{2h}{r}$ | 0.50 nH (1.51 mm, 0.3 mm drill) |

**Δl and C are the same thing.** An open-end capacitance equals the capacitance of the extra line length:
$$C_{oc}=C'\,\Delta l=\frac{\sqrt{\varepsilon_\text{eff}}}{c\,Z_0}\,\Delta l .$$
Here $C'$ (F/m) is the line capacitance per metre, $Z_0$ (Ω) and $\varepsilon_\text{eff}$ come from [planar lines](planar-lines-microstrip-stripline-cpwg.md), and c = 299 792 458 m/s. For 50 Ω on the 2-layer board, 0.60 mm ↔ 74 fF.

**Is it significant?** Compare the parasitic reactance with $Z_0$. A shunt C matters when $\omega CZ_0$ approaches 0.1, which gives |S11| ≈ −26 dB. A series L matters when $\omega L/Z_0$ approaches 0.1. For a small symmetric T-network the reflection is approximately $|S_{11}|\approx\tfrac12|\omega CZ_0-2\omega L/Z_0|$. The C and L terms partly cancel, and mitring exploits exactly that.

### Level 2 — where the models come from, and the formulas

**Quasi-static "excess" method.** Solve the static problem twice, once for the real geometry and once for semi-infinite uniform lines meeting at the reference plane. The difference in total charge at 1 V is the excess capacitance (Silvester & Benedek 1972), and the difference in magnetic flux at 1 A (computed with the dielectric removed) is the excess inductance. All the classical closed forms (Garg & Bahl 1978, Gupta et al.) are curve fits to such solutions or to measurements. The improved-resonator measurements of Kirschning, Jansen & Koster (1981–83) underlie the most widely used CAD models (Qucs, and the default in many simulators).

**Open end (KJK 1981).** With $u=W/h$ and $\varepsilon_\text{eff}$ the effective permittivity (using the dispersive value at frequency f, as Qucs does):
$$\frac{\Delta l}{h}=\frac{Q_1Q_3Q_5}{Q_4},\qquad Q_1=0.434907\,\frac{\varepsilon_\text{eff}^{0.81}+0.26}{\varepsilon_\text{eff}^{0.81}-0.189}\cdot\frac{u^{0.8544}+0.236}{u^{0.8544}+0.87},$$
$$Q_2=1+\frac{u^{0.371}}{2.358\varepsilon_r+1},\quad Q_3=1+\frac{0.5274\arctan\!\left(0.084\,u^{1.9413/Q_2}\right)}{\varepsilon_\text{eff}^{0.9236}},$$
$$Q_4=1+0.0377\arctan\!\left(0.067u^{1.456}\right)\left[6-5e^{0.036(1-\varepsilon_r)}\right],\quad Q_5=1-0.218e^{-7.5u}.$$
The stated error is below 2.5 % for 0.01 ≤ u ≤ 100 and εr ≤ 50 [1][2]. Two simpler forms are in common use:
- the Hammerstad–Bekkadal form, quoted in the [stubs page](input-impedance-stubs-quarter-wave.md): $\Delta l/h=0.412\frac{(\varepsilon_\text{eff}+0.3)(u+0.264)}{(\varepsilon_\text{eff}-0.258)(u+0.8)}$;
- Hammerstad (1981): $\Delta l/h=0.102\frac{u+0.106}{u+0.264}\left[1.166+\frac{\varepsilon_r+1}{\varepsilon_r}\left(0.9+\ln(u+2.475)\right)\right]$.

At εr 4.5 the script shows all three within 5 % for 0.5 ≤ u ≤ 2. They diverge by up to 15 % at u = 0.1 and u = 8.

**Gap (Kirschning; Qucs) — π-network.** Normalise $w_1=W_1/h$ and $s_n=s/h$, and use $W_2/W_1\ge1$. Then
$$C_s\,[\text{F}]=5\times10^{-10}h\,e^{-1.86s_n}Q_1\left[1+4.19\left(1-e^{-0.785\sqrt{1/w_1}\,W_2/W_1}\right)\right],$$
$Q_1=0.04598(0.03+w_1^{Q_5})(0.272+0.07\varepsilon_r)$, $Q_5=1.23/[1+0.12(W_2/W_1-1)^{0.9}]$. The shunt capacitances are the open-end capacitances scaled by $(Q_2+Q_{3,4})/(Q_2+1)$, where $Q_2=0.107(w_1+9)s_n^{3.23}+2.09s_n^{1.05}\frac{1.5+0.3w_1}{1+0.6w_1}$ and $Q_{3,4}=e^{-0.5978(W_2/W_1)^{\pm1.35}}-0.55$. Valid ranges: 0.1 ≤ W/h ≤ 3, 1 ≤ εr ≤ 15, s/h ≥ 0.1, 0.2–18 GHz [2][3]. As $s\to\infty$, $C_s\to0$ and each side becomes an open end.

**Step in width (Gupta et al.).** For W1 > W2:
- $C\,[\text{pF}]=\sqrt{W_1W_2}\,[\text{m}]\left[(10.1\log\varepsilon_r+2.33)\frac{W_1}{W_2}-12.6\log\varepsilon_r-3.17\right]$, valid for εr ≤ 10 and 1.5 ≤ W1/W2 ≤ 3.5;
- $\frac{L_s}{h}\,[\text{nH/m}]=40.5\left(\frac{W_1}{W_2}-1\right)-75\log\frac{W_1}{W_2}+0.2\left(\frac{W_1}{W_2}-1\right)^2$, within 5 % for W1/W2 ≤ 5 at W2 = h.

$L_s$ is split between the two sides in proportion to each line's inductance per metre, $L'=Z_0\sqrt{\varepsilon_\text{eff}}/c$ [3][4].

**Square corner and 50 % mitre (KJK 1983).** The model is a T-network: series L in each arm and shunt C at the centre.
- Corner: $C\,[\text{pF}]=W\,[\text{m}]\left[(10.35\varepsilon_r+2.5)\frac Wh+2.6\varepsilon_r+5.64\right]$ and $L\,[\text{nH}]=220h\,[\text{m}]\left[1-1.35e^{-0.18(W/h)^{1.39}}\right]$.
- 50 % mitre: $C=W[(3.93\varepsilon_r+0.62)W/h+7.6\varepsilon_r+3.80]$ pF and $L=440h[1-1.062e^{-0.177(W/h)^{0.947}}]$ nH.

Valid for 0.2 ≤ W/h ≤ 6, 2.36 ≤ εr ≤ 10.4, up to 14 GHz (f·h ≤ 12 GHz·mm), with stated precision ≈ 0.3 % [2]. The older Garg–Bahl corner gives $C/W$ = $(9.5\varepsilon_r+1.25)W/h+5.2\varepsilon_r+7.0$ pF/m for W/h ≥ 1 and $L/h=100(4\sqrt{W/h}-4.21)$ nH/m for the total series inductance [3][4]. Its C is within 3 % of KJK here and its |S11| is about 1 dB lower.

**Optimal mitre (Douville & James 1978)** [5]. The mitre fraction is $M=x/d$, where d = W√2 is the corner diagonal and x is the cut-back from the outer corner. The fit is
$$M=0.52+0.65\,e^{-1.35W/h}\qquad(W/h\ge0.25,\ \varepsilon_r\le25;\ \text{measured }0.25\le W/h\le2.75,\ 2.5\le\varepsilon_r\le25).$$
It is independent of εr. They reported VSWR < 1.1 for any mitre within ±4 % (of d) of the formula. Example values: M = 98.4 % at u = 0.25, 69 % at u = 1, 57 % at u = 1.85, 53 % at u = 3, and 52 % for wide lines. Geometrically, the removed triangle has legs of $2MW$ along the two outer edges.

**T-junction (Hammerstad 1981; Qucs `mstee`).** Each arm is first mapped to an equivalent parallel-plate width $D=\eta_0h/(Z\sqrt{\varepsilon_\text{eff}})$, with first higher-order-mode frequency $f_p\,[\text{GHz}]=0.4Z/h\,[\text{mm}]$. The model then has three parts:
- **main-arm reference-plane shift:** $d_x=0.055D_2\frac{Z_x}{Z_2}\left[1-2\frac{Z_x}{Z_2}(f/f_{p,x})^2\right]$;
- **side-arm shift:** $d_2=\sqrt{D_aD_b}\,[0.5-R(0.05+0.7e^{-1.6R}+0.25RQ-0.17\ln R)]$, with $R=\sqrt{Z_aZ_b}/Z_2$ and $Q=f^2/(f_{p,a}f_{p,b})$;
- **ideal transformers** with $T_x^2=1-\pi(f/f_{p,x})^2[(Z_x/Z_2)^2/12+(0.5-d_2/D_x)^2]$, and a small shunt susceptance $B_T$ (its formula is in [2]).

The physics: the junction's electrical centre is not at the geometric centre, and the coupling to the side arm falls as the higher-order mode in the junction area approaches cut-off.

**Via to ground (Goldfarb & Pucel 1991).** For barrel radius r and length h:
$$L=\frac{\mu_0}{2\pi}\left[h\ln\frac{h+\sqrt{r^2+h^2}}{r}+\frac32\left(r-\sqrt{r^2+h^2}\right)\right],\qquad R=R_{dc}\sqrt{1+f/f_\delta},\quad f_\delta=\frac{\rho}{\pi\mu_0t^2}.$$
It was verified against numerical solutions and measurements for $h<0.03\lambda_0$ [6]. It reproduces the 0.54 nH (1.6 mm, 0.3 mm drill) that the [04 parasitics page](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md) uses.

**Deriving the small-discontinuity reflection (why C and L partly cancel).** Take a symmetric T-network with series $jX$ in each arm ($X=\omega L$) and shunt susceptance $B=\omega C$, between lines of impedance $Z_0$. Normalise: $x=X/Z_0$, $b=BZ_0$, both ≪ 1. Looking in from port 1 with port 2 matched:
$$z_\text{in}=jx+\frac{1}{jb+\dfrac{1}{1+jx}}\approx jx+(1+jx)\left[1-jb(1+jx)\right]\approx1+j(2x-b)+O(x^2,b^2,xb).$$
Then
$$\Gamma=\frac{z_\text{in}-1}{z_\text{in}+1}\approx\frac{j(2x-b)}{2}\quad\Rightarrow\quad|S_{11}|\approx\tfrac12\left|\omega CZ_0-\frac{2\omega L}{Z_0}\right|.$$
Three consequences follow:
1. Both parasitics grow linearly with frequency, so |S11| rises 6 dB per octave. The script's corner values follow this: −28 dB at 0.915 GHz and −19.5 dB at 2.45 GHz.
2. A capacitive discontinuity can be cancelled by a little extra series inductance, and the reverse. Mitring removes C while the narrower current path adds L. The optimum mitre is where $\omega CZ_0\approx2\omega L/Z_0$, which is why it is not 100 %.
3. The transmission phase also shifts, by about $-(b/2+x)$ rad. That is the "electrically shorter than the path length" effect of bends noted by Lee and Wikipedia.

**Deriving Δl from the end capacitance.** An ideal open line of length $l$ has input admittance $Y_\text{in}=jY_0\tan\beta l$. Add an end capacitance with $\omega C_{oc}=Y_0\tan\beta\Delta l$. For $\beta\Delta l\ll1$, $C_{oc}\approx Y_0\beta\Delta l/\omega=\Delta l\sqrt{\varepsilon_\text{eff}}/(cZ_0)$. The tangent-addition formula then shows that the loaded line behaves exactly as an open line of length $l+\Delta l$. Δl is therefore frequency-independent only while $C_{oc}$ is.

**Validity ranges at a glance** (from [1]–[6]; outside these, run an EM solver):

| Model | W/h | εr | Other limits | 2-layer 50 Ω (u 1.85) | JLC-7628 50 Ω (u 1.77) |
|---|---|---|---|---|---|
| KJK open end | 0.01–100 | 1–50 | error < 2.5 % | inside | inside |
| Hammerstad open end | wide | — | < 1.7 % (stated) | inside | inside |
| Kirschning gap | 0.1–3 | 1–15 | s/h ≥ 0.1; 0.2–18 GHz | inside | inside |
| Gupta step (C) | — | ≤ 10 | 1.5 ≤ W1/W2 ≤ 3.5 | ratio dependent | ratio dependent |
| KJK corner / 50 % mitre | 0.2–6 | 2.36–10.4 | f·h ≤ 12 GHz·mm | to 7.9 GHz | to 57 GHz |
| Douville–James mitre | ≥ 0.25 (evidence 0.25–2.75) | 2.5–25 | VSWR < 1.1 within ±4 % | inside | inside |
| Hammerstad tee | — | — | f ≪ f_p (0.4 Z/h GHz·mm) | f_p 13 GHz | f_p 95 GHz |
| Goldfarb–Pucel via | — | — | h < 0.03 λ0 | to 6 GHz | to 43 GHz |

### Level 3 — dispersion, radiation, and when the closed forms fail

**Frequency dependence.** All the models above are quasi-static plus small corrections. KJK makes Δl frequency-dependent only through $\varepsilon_\text{eff}(f)$, which gives less than 1 % change to 6 GHz on 1.5 mm FR-4. The full-wave openEMS result rises by about 5 % from 0.9 to 2.45 GHz. The real higher-order effects are three:
1. **Radiation from the discontinuity.** It grows as $(h/\lambda_0)^2$: |Γ| of the 2-layer open end falls from 0.998 at 0.9 GHz to **0.982 at 5.8 GHz**, so 3.5 % of the power is radiated. The square bend shows |S21| = −0.47 dB at 5.8 GHz, of which only 0.31 dB is mismatch; the rest is radiation and surface waves.
2. **Surface-wave launching.** The TM0 surface wave of the grounded slab has no cut-off. Every discontinuity couples a little power into it (see [Green's functions](../02-electromagnetics/greens-functions-and-integral-equations.md) Level 3).
3. **Higher-order modes in wide junctions.** The T-junction model's $f_p$ is 13 GHz for 50 Ω on 1.51 mm and 95 GHz on 0.21 mm. As f approaches $f_p/3$, the junction stops being lumped.

**Interaction between nearby discontinuities.** Each model assumes uniform line on both sides for at least a few h. Discontinuities closer than ~2–3 h interact through their higher-order evanescent fields: a stub right at a T, two bends forming a U, a step right at a pad. Cascading their models then misses the coupling. In the [coupled-resonator filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md) the gaps and open ends interact in exactly this way, which is why filter tools use EM-extracted libraries.

**When the closed forms fail.** Use a 2.5-D or 3-D EM solver (openEMS, Sonnet; see [EM solvers](../16-simulation-tools/em-solvers-fdtd-mom-fem.md)) when any of these apply:
- you are outside the fitted ranges: the step for W1/W2 > 3.5 (e.g. 2.8 mm → 0.5 mm into a U.FL pad, ratio 5.6), the corner for W/h > 6 or εr < 2.36, or the gap for W/h > 3;
- the strip is CPWG or has ground pour nearby. Every formula here assumes open microstrip, and none covers coplanar grounds;
- the copper is thick compared with h. On 0.1 mm prepreg, 35 µm copper is t/h = 0.35, which the models do not include;
- f·h > 10–12 GHz·mm: 1.5 mm FR-4 above ~7 GHz;
- discontinuities are closer than 2–3 h to each other;
- you need better than ~1 dB or ~1° accuracy, for example in a filter or coupler that sets a frequency to 0.5 %.

**What the openEMS check found** (pre-registered, `e11_discontinuities_openems.py`). The FDTD model used a zero-thickness PEC strip, lossless εr 4.5, h 1.51 mm and the thirds-rule mesh. Two discontinuities were checked:
1. **Square bend:** openEMS |S11| agreed with the KJK corner model **within 0.7 dB from 1 to 6 GHz** (−28.8 / −20.2 / −15.3 / −11.6 dB vs −28.2 / −19.5 / −15.4 / −12.3 dB at 0.9 / 2.45 / 4.0 / 5.8 GHz). The KJK 50 % mitre model predicted −29.8 dB at 2.45 GHz; openEMS gave −29.4 dB.
2. **Open end:** the measured Δl was **+11.5 % (W/h 1.85) and +18 % (W/h 0.5) above KJK**. It was stable between two meshes (0.38 → 0.19 mm cells, change 0.5 %), so it is not a mesh artefact. This missed the pre-registered ±10 % band. Possible causes: KJK was fitted to measurements on real metallisation and at particular εr; the full-wave field near an open end differs from the quasi-static field; the FDTD zero-thickness edge model differs from reality. The difference was not resolved here. It is 0.07 mm, or 0.4° of phase at 2.45 GHz on this board.

## Design equations & rules of thumb

| Rule | When valid | Value on the 2-layer board / JLC-7628 |
|---|---|---|
| $\Delta l_{oc}\approx0.4h$ (KJK for accuracy) | 0.5 ≤ W/h ≤ 2 | 0.60 mm / 0.085 mm |
| $C_{oc}=\Delta l\sqrt{\varepsilon_\text{eff}}/(cZ_0)$ | any | 74 fF / 10 fF |
| Square corner $|S_{11}|$ | KJK range | −28 / −19.5 / −12 dB at 0.915 / 2.45 / 5.8 GHz; −45 / −36.5 / −29 dB |
| Optimum mitre $M=0.52+0.65e^{-1.35W/h}$ | W/h ≥ 0.25 | 57 % / 58 % |
| Curved bend radius ≥ 3W | low reflection alternative (Lee) | — |
| Gap is a ~0.1 pF series C | s ≈ 0.1–0.5 mm | not a DC block below ~10 GHz |
| Step parasitic ≪ the high-Z section it creates | W1/W2 ≤ 3.5 | model the narrow segment as a line |
| T-junction: shift the side-arm reference plane by $d_2$ | f ≪ $f_p$ | 1.9 mm / 0.27 mm |
| Via: $L\approx\frac{\mu_0h}{2\pi}\ln\frac{2h}{r}$ (G–P exact) | $h<0.03\lambda_0$ | 0.50 nH / 15 pH |
| Ignore all of these | h ≤ 0.2 mm and f ≤ 1 GHz | — |

## Worked examples

### Example 1 — trimming a 915 MHz λ/4 open stub on the 2-layer board
The line is 50 Ω (W 2.80 mm, h 1.51 mm, εr 4.5) with dispersive $\varepsilon_\text{eff}$ = 3.40 at 915 MHz, so the ideal length is $\lambda_g/4=c/(4f\sqrt{\varepsilon_\text{eff}})$ = **44.40 mm**. The KJK open end adds Δl = 0.601 mm, so draw the stub **43.80 mm** long. Without the correction the stub resonates 1.4 % low, at 903 MHz instead of 915 MHz. For a notch filter aimed at a 915 MHz interferer, a 12 MHz error is more than a LoRa channel. The openEMS Δl (0.67 mm) would give 43.73 mm. The 0.07 mm difference is 0.15 % in frequency and below FR-4's εr tolerance (±0.2 in εr ≈ ±2 % in frequency).

### Example 2 — does a square corner in my LoRa feed matter?
On the 2-layer board, the KJK corner model at 915 MHz gives $\omega CZ_0$ = 2π·0.915e9·0.31e-12·50 = 0.089 and $\omega L/Z_0$ = 0.005, so **|S11| ≈ −28 dB**, return loss 28 dB and mismatch loss 0.007 dB. That is harmless at 915 MHz. At 2.45 GHz it is −19.5 dB, and two corners in series can add to about −14 dB in the worst phase. A 57 % mitre brings each corner to −36 dB (openEMS). On JLC-7628 the corner is −45 dB at 915 MHz, so draw whatever you like. **Conclusion for the reader's boards:** mitre on 2-layer boards at 2.4 GHz and above. Mitre everywhere if you like, because it costs nothing. Never claim that a square corner "radiates" at 433 MHz.

### Example 3 — the 2.8 mm trace meeting a U.FL pad
The 2.8 mm (50 Ω) trace narrows to 0.5 mm for 2 mm before the pad. The step ratio 5.6 is outside Gupta's range. Extrapolating anyway gives C ≈ 46 fF and L ≈ 0.2 nH, which are small. The dominant effect is the **2 mm of 0.5 mm-wide line (109 Ω, εeff 3.06)**. At 2.45 GHz, $\beta l$ = 2π·2.45e9·√3.06·2e-3/c = 0.18 rad, a series reactance of about $jZ_\text{high}\tan\beta l$ ≈ j20 Ω, which gives |S11| ≈ −14 dB. At 915 MHz it is j7.3 Ω and −23 dB. Fix it by tapering, by using CPWG with a narrow trace (0.9–1.0 mm on this board, see [planar lines](planar-lines-microstrip-stripline-cpwg.md)), or by compensating with a small shunt pad capacitance (as in [TDR](time-domain-reflectometry.md) Ex. 2). Verify a launch with EM simulation or TDR, because the closed forms do not cover it.

### Example 4 — shorted stub through a via
A shorted λ/4 stub (a DC return for a bias tee) on the 2-layer board ends in one 0.3 mm via. Goldfarb–Pucel gives L = 0.497 nH (h = 1.51 mm, this page's 2-layer model input; 0.54 nH for the [canonical](../00-math-foundations/canonical-values-and-conventions.md) 1.6 mm via), so X = 2.86 Ω at 915 MHz. The equivalent extra length is $\arctan(X/Z_0)/\beta$ = arctan(0.057)/35.3 rad/m = **1.6 mm**, so shorten the stub by 1.6 mm. Two vias 1 mm apart give 0.38 nH (from the 04 page, including mutual coupling), or about 1.2 mm. On JLC-7628 the via is 15 pH, which is negligible.

### Example 5 — a Wilkinson or T-splitter at 2.45 GHz
For a symmetric 50 Ω T on the 2-layer board at 2.45 GHz, Hammerstad's model gives |S11| = −9.62 dB, against the ideal 1/3 = −9.54 dB. The reference planes are shifted by $d_\text{main}$ = 0.31 mm and $d_\text{side}$ = 1.84 mm from the centre lines. The side-arm shift is the one to account for: 1.84 mm is 10° at 2.45 GHz, so the λ/4 arm of a Wilkinson measured from the main-line centre should be about 1.8 mm shorter. On JLC-7628 the shifts are 0.05 mm and 0.27 mm (≈ 1.4°), small enough to ignore except in couplers.

### Example 6 — a 5.8 GHz feed on JLC-7628 with four corners and a T
On JLC-7628 (0.36 mm, 50 Ω masked) at 5.8 GHz a square corner is −29 dB. Four of them in series, worst case adding in phase, give about −17 dB, which is still acceptable for a video transmitter (mismatch loss 0.09 dB). Mitring them (58 %) puts each below −40 dB. The 50 Ω T-junction shifts the side-arm reference plane by 0.27 mm (5° at 5.8 GHz). That matters if the T feeds a 2-element patch array whose phasing sets the beam direction: 5° of phase error at λ/2 element spacing tilts the beam by about arcsin(0.087/π) ≈ 1.6° ([array factor](../12-phased-arrays/array-factor-linear-arrays.md)). Include it, or simulate the feed in openEMS.

## Practical notes
- **Order of importance on PCB RF paths:** connector launches and pad transitions, then via transitions, then stubs and open ends that set a frequency, then T-junction plane shifts, and only then bends. Bends are almost never the cause of a failed 433/915 MHz design.
- **Curved bends** (radius ≥ 3W) are as good as an optimal mitre but take more area. KiCad's "round corners" or arc tracks make them easy. A 45° double-bend ("chamfered corner" done as two 45° turns) is also excellent.
- **Do not mitre CPWG naively.** The ground gaps also bend; keep the gap constant round the corner and stitch vias at both sides of the turn ([vias & fencing](../13-pcb-rf-layout-emc/vias-stitching-fencing.md)).
- **Gaps for coupling filters** need EM simulation or the KJK gap model with interaction checks. Etch tolerance (±20 µm on 0.1–0.2 mm gaps) changes $C_s$ by 10–20 %.
- **Soldermask over an open end** raises Δl slightly, because extra dielectric sits in the fringing field. No closed form covers it.
- **Test coupons:** a ring or straight λ/2 resonator on the panel measures εr *and* calibrates your open-end model. The [permittivity page](../17-test-measurement/resonator-and-cavity-perturbation-permittivity-measurement.md) gives the recipe.
- **Qucs-S and KiCad:** Qucs-S includes the MOPEN, MGAP, MSTEP, MCORN, MMBEND, MTEE, MCROSS and MVIA models used here, so circuit-level simulation of microstrip layouts is free (see [RF circuit simulators](../16-simulation-tools/rf-circuit-simulators-harmonic-balance.md)).

## Common mistakes & misconceptions
- **Using the full board thickness as h on a 4-layer board.** Every discontinuity scales with the distance to the reference plane (0.21 mm on JLC-7628), so 1.6 mm overestimates the parasitics by 7×.
- **Trusting a simulator's default discontinuity model blindly.** ADS, AWR, Qucs and Sonnet libraries differ by model choice (KJK, Hammerstad, Gupta). Know which one is used and whether you are inside its range.
- **"A 90° corner reflects badly, so always round traces."** On thin 4-layer prepregs the corner is −36 dB at 2.45 GHz. On thick 2-layer boards it matters above ~2 GHz.
- **"Mitre 100 % (cut through to the inside corner)" or "always cut at 45° to half the width".** The optimum is 52–70 % of the diagonal for normal W/h. Over-mitring (75 %) is *worse* than 50 % (openEMS: −24 vs −29 dB at 2.45 GHz) because it adds too much inductance.
- **"A gap in the trace is a DC-blocking capacitor."** It is ~0.1 pF, about −j650 Ω at 2.45 GHz. Use a 0402 capacitor.
- **Forgetting the open end when cutting a stub to length.** Δl ≈ 0.4 h is 1.4 % of a λ/4 stub at 915 MHz on 1.5 mm FR-4, an error that does not trim out once the board is etched.
- **Applying a closed-form model outside its range** (step ratios above 3.5, CPWG, thick copper). They silently extrapolate.
- **Cascading discontinuity models that are closer than 2–3 h.** The evanescent fields interact.
- **Thinking the T-junction is at its geometric centre.** The side-arm reference plane moves by ~1.3 h on FR-4.

## How to simulate / verify
- **Measurement:** a TDR (or a VNA in time-domain mode, see [TDR](time-domain-reflectometry.md)) shows each discontinuity as a capacitive dip or an inductive bump. The area of the dip gives C (or L) directly: $C\approx\frac{2}{Z_0V_\text{step}}\int\Delta V\,dt$ for a small shunt C. This is the bench check of the numbers on this page.
- `python3 tools/verify/e11_discontinuities.py` (≈ 5 s) implements all the closed forms (KJK open end, both Hammerstad open ends, Kirschning gap, Gupta step, KJK and Garg–Bahl corners, KJK 50 % mitre, Douville–James mitre, Hammerstad tee, Goldfarb–Pucel via). It prints tables for both of the reader's boards and compares them with the openEMS data. Result: 15/18 checks. The 3 misses are reported above (open-end openEMS vs KJK ×2, and the open-end model spread at extreme u).
- `~/opt/openEMS/venv/bin/python tools/verify/e11_discontinuities_openems.py` (≈ 12 min on the M-series Mac) runs the FDTD open ends (two widths, two meshes) and bends (square, 50 %, Douville–James, 75 %). Results are in `e11_discontinuities_openems_results.txt` and `data/e11_openems_discontinuities.npz`.
- **Method note for openEMS open ends:** the MSL port's Z/β extraction is ill-conditioned inside a standing wave (the first attempt gave εeff 3.79 instead of 3.40). The script therefore subtracts a matched "through" run on the identical mesh: Γ = (V_open − V_thru)/V_thru, with β taken from the through run. It also uses PML on all open sides, because MUR walls trapped slab surface waves and the end criterion was never reached.
- Circuit level: Qucs-S `MOPEN`/`MCORN`/… elements, or scikit-rf with the functions from the script.

## Open questions / gaps
- The openEMS vs KJK open-end discrepancy (+11 to +18 %) is not explained. Next steps: a 3-D quasi-static excess-charge solve, or a check against Sonnet or published spectral-domain Δl data. Finite-thickness copper and soldermask over the end are not modelled.
- The Garg–Bahl corner coefficients are cited from knowledge of Gupta et al. and were not re-read in the book. They agree with KJK to 3 % in C, but their inductance is 2.3× KJK's, and the split between arms is assumed.
- No closed form for CPWG discontinuities (bends, T-junctions, open ends with side grounds) was found; only EM simulation covers them.
- T-junction, step and gap models were not EM-checked here, only implemented from the published forms.
- **Attribution note (resolved; checked by W5-S18 on 2026-10-13):** the [stubs page](input-impedance-stubs-quarter-wave.md) now attributes the 0.412 open-end formula to Hammerstad (1975) as reproduced in Wadell. It also notes that Qucs implements the different 1981 Hammerstad form (the 0.102 one) and Kirschning–Jansen–Koster. All of them give ≈ 0.39 h for 50 Ω on FR-4.

## Sources
1. M. Kirschning, R. H. Jansen, N. H. L. Koster, "Accurate model for open end effect of microstrip lines," *Electronics Letters*, 17(3):123–125, 1981. (peer-reviewed; equations via [2])
2. S. Jahn et al., *Qucs Technical Papers*, §11 "Microstrip components": corner/mitred bend (eqs. 11.84–11.88), open (11.185–11.192), gap (11.193–11.201), step (11.202–11.206), tee (11.207–11.218), via (11.232–11.234), https://qucs.sourceforge.net/tech/node74.html (read via the LaTeX alt text with curl, 2026-10-03), and the qucs-core sources `msopen.cpp`, `msgap.cpp`, `msstep.cpp`, `mscorner.cpp`, `msmbend.cpp`, `mstee.cpp`, `msvia.cpp` (GitHub Qucs/qucs). (open-source simulator documentation; the corner and mitre formulas there come from M. Kirschning, R. H. Jansen, N. H. L. Koster, "Measurement and computer-aided modeling of microstrip discontinuities by an improved resonator method," *IEEE MTT-S Digest*, pp. 495–497, 1983)
3. K. C. Gupta, R. Garg, I. Bahl, P. Bhartia, *Microstrip Lines and Slotlines*, 2nd ed., Artech House, 1996, ch. 3 (discontinuities: step, bend, gap, T; excess-charge method). (textbook; step formula confirmed via [2]; bend formula from knowledge)
4. R. Garg, I. J. Bahl, "Microstrip discontinuities," *Int. J. Electronics*, 45(1):81–87, 1978. (peer-reviewed; via [3])
5. R. J. P. Douville, D. S. James, "Experimental study of symmetric microstrip bends and their compensation," *IEEE Trans. MTT*, 26(3):175–182, 1978. Formula and ranges confirmed from two secondary sources: the Wikipedia "Microstrip" article (raw text) and the leleivre.com mitre calculator source. (peer-reviewed, via secondary)
6. M. E. Goldfarb, R. A. Pucel, "Modeling via hole grounds in microstrip," *IEEE Microwave Guided Wave Lett.*, 1(6):135–137, 1991. (peer-reviewed; via [2])
7. E. Hammerstad, "Computer-aided design of microstrip couplers with accurate discontinuity models," *IEEE MTT-S Int. Symp. Digest*, pp. 54–56, 1981 (T-junction and open-end models). (peer-reviewed; via [2])
8. P. Silvester, P. Benedek, "Equivalent capacitances of microstrip open circuits," *IEEE Trans. MTT*, 20(8):511–516, 1972 (excess-charge method). (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
9. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley 2012, §4.6 (discontinuities and modal analysis). T. H. Lee, *Planar Microwave Engineering*, Cambridge 2004, pp. 173–174 (curved bends, r ≥ 3W). (textbooks)
10. Verification: `tools/verify/e11_discontinuities.py`, `tools/verify/e11_discontinuities_openems.py` (this KB; openEMS python interface in ~/opt/openEMS). (numerical check)
