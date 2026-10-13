---
title: Periodic structures — Floquet/Bloch waves, slow-wave and Bragg lines, surface and leaky waves, EBG/mushroom surfaces and metamaterial basics (with a hype check)
domain: 03-transmission-lines-matching
slug: periodic-structures-ebg
tags: [periodic-structure, floquet, bloch, bloch-impedance, brillouin-diagram, k-beta-diagram, space-harmonics, stop-band, bragg, slow-wave, loaded-line, artificial-transmission-line, stepped-impedance, pbg, surface-wave, grounded-slab, tm0, te1, leaky-wave-antenna, frequency-scanning, ebg, mushroom, sievenpiper, high-impedance-surface, amc, artificial-magnetic-conductor, reflection-phase, metamaterial, crlh, left-handed, backward-wave, negative-index, hype-check]
prerequisites:
  - telegrapher-equations-characteristic-impedance.md
  - input-impedance-stubs-quarter-wave.md
  - ../01-circuit-theory/two-port-networks-zyh-abcd.md
  - ../02-electromagnetics/waveguides-and-cavity-resonators.md
related:
  - planar-lines-microstrip-stripline-cpwg.md
  - broadband-matching-bode-fano.md
  - microstrip-discontinuities.md
  - ../02-electromagnetics/greens-functions-and-integral-equations.md
  - ../08-antennas/patch-antennas.md
  - ../08-antennas/antennas-on-rockets.md
  - ../12-phased-arrays/planar-arrays-element-pattern-coupling.md
  - ../12-phased-arrays/beam-steering-grating-lobes.md
  - ../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md
  - ../13-pcb-rf-layout-emc/shielding-and-isolation.md
level: advanced
confidence: medium
last_updated: 2026-10-13
---

# Periodic structures — Floquet/Bloch waves, EBG surfaces and metamaterial basics

## Questions this page answers
- What happens to a wave on a transmission line loaded with identical capacitors every few millimetres?
- What are Floquet's theorem, Bloch waves and a k–β (Brillouin) diagram, and how do I read one?
- What is the Bloch impedance, and why does a periodic line have stop bands?
- How do slow-wave lines and stepped-impedance (Bragg, "PBG") lines work, and are they any use at 433 MHz?
- What are surface waves on a PCB, and how much power does a patch or printed dipole lose to them?
- How does a leaky-wave antenna steer its beam with frequency?
- What is a mushroom EBG or "artificial magnetic conductor", and can it let me mount an antenna flat on a metal airframe?
- What is a metamaterial, what is a left-handed (CRLH) line, and which metamaterial claims are hype?

## TL;DR
- **Floquet/Bloch:** in a structure that repeats every d, waves have the form $e^{-\gamma z}\times$(a function with period d). For a line cell with ABCD matrix, **$\cosh\gamma d=(A+D)/2$**. Where $|(A+D)/2|\le1$ the wave propagates (pass band, γ = jβ); where it exceeds 1 it is evanescent (**stop band**, attenuation αd per cell). The **Bloch impedance** of a symmetric cell is $Z_B=B/\sqrt{A^2-1}$ (verified: terminates any number of cells reflectionlessly).
- **Loaded (slow-wave) line:** 1 pF every 10 mm on a 50 Ω JLC microstrip slows the wave by **1.347×** at 433.92 MHz (light-loading formula $\sqrt{1+C/C'd}$ = 1.346), lowers $Z_B$ to **37.0 Ω**, and makes a stop band from **4.79 to 8.13 GHz**, so the loaded line is also a low-pass filter. A **Bragg line** of 30/80 Ω quarter-wave sections has a stop band of fractional width $(4/\pi)\arcsin(|Z_1-Z_2|/(Z_1+Z_2))$ = **60 %**, but at UHF its sections are ~47 mm each.
- **Surface waves:** a grounded slab always guides TM0. On JLC's 1.43 mm FR-4 core (εr 4.5) **β/k0 = 1.00005 / 1.0002 / 1.0016 / 1.0097** at 0.434 / 0.915 / 2.45 / 5.8 GHz; TE1 starts at 28 GHz. An exact spectral calculation gives a printed horizontal dipole's surface-wave loss: **2 % at 433 MHz, 10 % at 2.45 GHz, 22 % at 5.8 GHz**. The Jackson–Alexopoulos formula agrees to 0.5 point up to h/λ0 = 0.012 but is 5.6 points optimistic at h/λ0 = 0.048.
- **Leaky waves:** a mode with β < k0 radiates at $\sin\theta=\beta/k_0$. A periodic microstrip line uses the n = −1 space harmonic $\beta_{-1}=\beta_0-2\pi/p$: p = λg = 28.0 mm makes a 5.8 GHz broadside beam that scans **≈ 1.8° per 100 MHz**.
- **Mushroom EBG / AMC (Sievenpiper):** $L=\mu_0h$, $C=\frac{w\varepsilon_0(1+\varepsilon_r)}{\pi}\cosh^{-1}(a/g)$, $f_0=1/(2\pi\sqrt{LC})$, ±90° reflection-phase bandwidth $\sqrt{L/C}/\eta_0$, which equals **k0h**. A 5.8 GHz design on 1.43 mm FR-4 (a = 7.71 mm, g = 0.386 mm) gives in openEMS **f0 = 5.82 GHz** (model 5.80) and a **16.7 % bandwidth** (model 17.4 %). With FR-4 loss it **absorbs 33 % of the power at resonance**. At 433 MHz the same board would give only 5.6 MHz of bandwidth and needs 75 pF per cell.
- **Metamaterials:** a CRLH line (series C, shunt L, plus the host line's L and C) has a backward-wave band and, when balanced ($L_RC_L=L_LC_R$), no gap at the transition. It is a useful dispersion-engineering tool. It **does not** beat the Chu limit, Bode–Fano, or the thickness–bandwidth limit of ground-plane surfaces.

## Intuition (no math)
Shine light on a stack of glass plates with exactly the right spacing and almost all of it reflects, even though each plate reflects only a little. Every small reflection comes back in step with the others. Any repeating structure does this for waves of one particular spacing-to-wavelength ratio: a transmission line with a capacitor every centimetre, a row of vias, a patterned ground plane, an array of patches. At the frequencies where the reflections add up, the wave cannot get through (a **stop band**). In between, it gets through, but slowed and with a different apparent impedance, because it keeps being partly reflected and re-transmitted.

Floquet's theorem is the bookkeeping: if the structure looks the same after one period, the wave must also look the same after one period, apart from a constant factor (a phase shift, plus a decay in the stop band). So you only ever need to analyse **one cell**.

Two more effects come from the same picture. If the periodic wave travels slower than light along a surface, it is bound to the surface and does not radiate: a **surface wave**. On a PCB that is power quietly leaving your antenna sideways. If the period makes one of its "space harmonics" travel faster than light along the surface, that part radiates at an angle set by the frequency: a **leaky-wave antenna**.

A **mushroom surface** is a carpet of small metal patches, each connected to the ground plane by a via. Each patch-gap-via unit is a tiny parallel LC resonator. Near its resonant frequency the surface reflects a wave *in phase* instead of with the 180° flip of a plain metal sheet: it behaves like a "magnetic conductor". An antenna can then sit close to it without being shorted out. The catch is that this only works over a band whose width is set by the surface's thickness in wavelengths.

## The math

### Level 1 — the results and what each symbol means
| Quantity | Formula | Units / note |
|---|---|---|
| Floquet condition | $\cosh\gamma d=\tfrac12(A+D)$, $\gamma=\alpha+j\beta$ | d = period (m); ABCD of one cell |
| Pass / stop band | $\lvert A+D\rvert\le2$: $\gamma=j\beta$; $>2$: α > 0 | stop bands centre near $\beta d=m\pi$ |
| Bloch impedance (symmetric cell) | $Z_B=\pm B/\sqrt{A^2-1}$ | Ω; real in pass bands of lossless cells |
| Space harmonics | $\beta_n=\beta_0+2\pi n/d$ | all share one group velocity |
| Loaded line (light loading) | $\beta\approx\beta_0\sqrt{1+C_l/(C'd)}$, $Z_B\approx Z_0/\sqrt{1+C_l/(C'd)}$ | C′ = line capacitance per metre |
| Bragg stop band ($\lambda/4$ $Z_1$/$Z_2$) | $\Delta f/f_0=\frac4\pi\arcsin\frac{\lvert Z_1-Z_2\rvert}{Z_1+Z_2}$ | centred on the quarter-wave frequency |
| Leaky-wave beam | $\sin\theta_m=\beta_{-1}/k_0=(\beta_0-2\pi/p)/k_0$ | θ from broadside |
| Grounded-slab TM0 (thin) | $\beta/k_0\approx1+\tfrac12[k_0h(1-1/\varepsilon_r)]^2$ | TE1 onset $c/(4h\sqrt{\varepsilon_r-1})$ |
| Mushroom LC | $L=\mu_0\mu_rh$, $C=\frac{w\varepsilon_0(1+\varepsilon_r)}{\pi}\cosh^{-1}\frac ag$ | a = period, g = gap, w = a − g |
| AMC resonance and bandwidth | $f_0=\frac{1}{2\pi\sqrt{LC}}$; $\frac{\Delta f}{f_0}\big\rvert_{\pm90^\circ}=\frac1{\eta_0}\sqrt{\frac LC}=k_0h\,\mu_r$ | bandwidth set by thickness |
| CRLH cell | $\cos\beta p=1+\tfrac12ZY$, $Z=j(\omega L_R-\tfrac1{\omega C_L})$, $Y=j(\omega C_R-\tfrac1{\omega L_L})$ | balanced if $L_RC_L=L_LC_R$ |

**Level 1½ — the same idea with only algebra.** Take one cell of the line and write its ABCD matrix (two numbers in, two numbers out). Cascading N identical cells is the matrix to the power N. A matrix raised to a high power is dominated by its eigenvalues λ. For a lossless reciprocal cell (AD − BC = 1) the two eigenvalues multiply to 1 and add to A + D. If $|A+D|<2$ they are $e^{\pm j\beta d}$, unit magnitude: the wave just picks up a phase βd per cell and goes on for ever (pass band). If $|A+D|>2$ they are real, one bigger than 1 and one smaller: the wave shrinks by a fixed factor per cell (stop band). Everything else on this page follows from that.

### Level 2 — derivations

**1. Floquet's theorem and the Bloch condition.** Let the voltage and current at the input of cell n be the vector $\mathbf u_n=(V_n,I_n)^T$, so $\mathbf u_n=\mathbf T\mathbf u_{n+1}$ with T the cell's ABCD matrix. A wave that repeats from cell to cell apart from a factor, $\mathbf u_{n+1}=e^{-\gamma d}\mathbf u_n$, must be an eigenvector: $\det(\mathbf T-e^{\gamma d}\mathbf I)=0$. With $AD-BC=1$ (reciprocity) this gives
$$e^{2\gamma d}-(A+D)e^{\gamma d}+1=0\ \Rightarrow\ \cosh\gamma d=\frac{A+D}{2}.$$
For a lossless cell A and D are real and B, C imaginary, so (A + D)/2 is real. Then γ is either purely imaginary (pass band) or has a real part (stop band). At the band edges $\beta d=0$ or π and the group velocity is zero: the wave stands still. That is why band edges carry large stored energy and loss (useful in slow-wave resonators, harmful in filters). The script checks that the ABCD eigenvalues are $e^{\mp j\beta d}$ to 10⁻¹².

**2. Bloch impedance.** The ratio $Z_B=V_n/I_n$ for the Bloch eigenvector follows from the first row of $(\mathbf T-e^{\gamma d}\mathbf I)\mathbf u=0$: $Z_B=B/(e^{\gamma d}-A)$. For a symmetric cell (A = D) this is $Z_B=\pm B/\sqrt{A^2-1}$; the sign picks the forward or backward wave. In general, $Z_B^\pm=-2B/(A-D\mp\sqrt{(A+D)^2-4})$ (Pozar §8.1 [1]). A periodic line terminated in $Z_B$ shows $Z_B$ at its input whatever the number of cells. The script checks this for 1, 3, 10 and 37 cells. In a stop band $Z_B$ is imaginary: the line looks reactive and reflects everything.

**3. The capacitively loaded line.** Cell = d/2 of line ($Z_0$, electrical length θ/2), shunt susceptance $b=\omega C_lZ_0$ (normalised), d/2 of line. Multiplying the three matrices:
$$\cos\beta d=\cos\theta-\frac b2\sin\theta .$$
- *Light loading* ($\theta\ll1$, $b\ll1$): $1-\tfrac12(\beta d)^2\approx1-\tfrac12\theta^2-\tfrac12b\theta$, so $\beta d\approx\theta\sqrt{1+b/\theta}=\theta\sqrt{1+C_l/(C'd)}$, since $b/\theta=\omega C_lZ_0/(\omega d\sqrt{L'C'})=C_l/(C'd)$. The capacitors just add to the line's capacitance per metre: the wave is slower and the impedance lower by the same factor. Script: 1.347 exact vs 1.346 approximate, $Z_B$ = 37.05 vs 37.13 Ω.
- *First stop band:* it starts where $\cos\theta-\frac b2\sin\theta=-1$ (4.79 GHz in the example) and ends where θ = π (8.13 GHz, the unloaded Bragg frequency $c/(2d\sqrt{\varepsilon_{eff}})$), where the cell is transparent. In between, the Bloch attenuation reaches **7.6 dB per cell** at 6.46 GHz, and the script shows that a 20-cell line loses exactly 7.612 dB per added cell (plus a constant 5.8 dB end mismatch to 50 Ω).
- This is the **artificial transmission line**: an LC ladder is a lumped low-pass filter whose cutoff is the Bragg frequency of the cells. Varactor-loaded versions are tunable phase shifters and, with non-linear capacitance, pulse-sharpening "non-linear transmission lines".

**4. Stepped-impedance (Bragg) line.** Alternate quarter-wave sections of $Z_1$ and $Z_2$ at $f_0$. Writing $\theta=\tfrac\pi2f/f_0$ for each section and multiplying the two line matrices gives $\tfrac12(A+D)=\cos^2\theta-\tfrac12(Z_1/Z_2+Z_2/Z_1)\sin^2\theta$. Setting this to −1 at the band edges gives the closed form in Level 1, which the script confirms (30/80 Ω: 60.08 % both ways). Six cells give −45 dB at $f_0$. This is the "photonic band-gap (PBG) microstrip" used for harmonic suppression. Its weakness at UHF is length: for the 2nd harmonic of 433.92 MHz each section is 46.8 mm on εeff 3.40, and six cells are **≈ 560 mm** of line. A lumped low-pass filter ([RF filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md)) is the right answer there.

**5. Space harmonics, the k–β diagram and leaky waves.** The periodic factor in a Bloch wave can be Fourier-expanded, so the field is a sum of space harmonics $e^{-j\beta_nz}$ with $\beta_n=\beta_0+2\pi n/d$. A **k–β (Brillouin) diagram** plots $k_0d$ against βd. It is periodic in βd with period 2π and is usually drawn for $-\pi\le\beta d\le\pi$. The **light lines** $\beta=\pm k_0$ divide it:
- harmonics with $|\beta_n|>k_0$ are *slow* and bound to the structure (surface or guided waves);
- any harmonic with $|\beta_n|<k_0$ is *fast*: it radiates at $\sin\theta=\beta_n/k_0$, losing power continuously (**leaky wave**).
A microstrip line ($\beta_0/k_0=\sqrt{3.40}$ = 1.844) with stubs or slots every p = λg = 28.03 mm puts $\beta_{-1}=0$ at 5.8 GHz: broadside. Then $\sin\theta=\sqrt{\varepsilon_{eff}}-\lambda_0/p$ scans the beam from −7.9° at 5.4 GHz to +6.8° at 6.2 GHz, about **1.8° per 100 MHz** (script; the slope is $\sqrt{\varepsilon_{eff}}\,\Delta f/f_0$ rad). Exactly at broadside the reflections of all cells add in phase ($\beta_0p=2\pi$ is also a Bragg condition): the "open stop band". It is the classic leaky-wave problem, which is why practical designs use asymmetric or matched unit cells to scan through broadside. The same phase-matching logic gives scan blindness in printed arrays ([planar arrays](../12-phased-arrays/planar-arrays-element-pattern-coupling.md)).

**6. Surface waves on a grounded slab.** Transverse resonance across the slab ([waveguides Level 3b C](../02-electromagnetics/waveguides-and-cavity-resonators.md)) gives TM modes from $k_d\tan(k_dh)=\varepsilon_r\alpha$ and TE modes from $-k_d\cot(k_dh)=\alpha$, with $k_d^2=\varepsilon_rk_0^2-\beta^2$ and $\alpha^2=\beta^2-k_0^2$. TM0 has no cutoff. For thin slabs, expanding $\tan x\approx x$ gives $\alpha\approx k_0^2h(\varepsilon_r-1)/\varepsilon_r$, hence the Level 1 asymptote. The field decays above the board as $e^{-\alpha z}$: at 433 MHz α = 0.09 m⁻¹, so the "bound" wave extends metres above the board. That is why it couples to everything nearby and diffracts at the board edge.

*How much power goes into it.* Put a horizontal electric dipole (the dominant current of a patch or printed dipole) on the slab. In the spectral domain each transverse wavenumber $k_\rho$ sees a transverse equivalent network: a TM and a TE line in air in parallel with a short-circuited dielectric line of length h. The radiated power is
$$P=\frac{|Il|^2}{8\pi}\,\mathrm{Re}\int_0^\infty k_\rho\,\big[V^{TM}(k_\rho)+V^{TE}(k_\rho)\big]\,dk_\rho,\qquad V=\frac{1}{Y_\text{air}+Y_\text{slab}} .$$
With no slab this reduces to $\eta k^2|Il|^2/12\pi$ (script check). The interval $k_\rho<k_0$ gives the space wave. The TM0 pole at $k_\rho=\beta$ gives the surface wave as a residue, $P_{sw}=\frac{|Il|^2}{8\pi}\,\pi\beta/|dB/dk_\rho|$ (with $Y=jB$ there). Results for the 1.43 mm, εr 4.5 core:

| f | h/λ0 | TM0 β/k0 | space-wave efficiency, exact | Jackson–Alexopoulos [6] |
|---|---|---|---|---|
| 433.92 MHz | 0.0021 | 1.000051 | 98.21 % | 98.22 % |
| 915 MHz | 0.0044 | 1.000228 | 96.26 % | 96.33 % |
| 2.45 GHz | 0.0117 | 1.001647 | 90.27 % | 90.74 % |
| 5.8 GHz | 0.0277 | 1.009665 | 78.28 % | 80.54 % |
| 10 GHz | 0.0477 | 1.032148 | 64.98 % | 70.59 % |

The closed form, $e=1/[1+\tfrac34\pi k_0h\,(1-1/n^2)^3/c_1]$ with $c_1=1-1/n^2+2/(5n^4)$, is a thin-substrate result. The exact ratio converges to it as h → 0 (ratio 1.0009 at 25 µm), but it is 5.6 points optimistic by h/λ0 ≈ 0.05. For εr 10.8, h = 0.02λ0 (the case in [patch antennas](../08-antennas/patch-antennas.md)) the exact surface-wave share is **22.4 %** (J–A 19.5 %).

### Level 3 — EBG/mushroom surfaces, CRLH lines, and where the models break

**1. The mushroom high-impedance surface (Sievenpiper 1999 [2]).** At normal incidence and for a period a ≪ λ, the surface is a sheet impedance $Z_s$: the patch-gap capacitance C in parallel with the inductance of the current loop through the vias and the ground plane, $L=\mu_0\mu_rh$ (the short-circuited slab, $j\omega\mu_0h$ for thin h). Then
$$Z_s=\frac{j\omega L}{1-\omega^2LC},\qquad\Gamma=\frac{Z_s-\eta_0}{Z_s+\eta_0}.$$
- Far below $f_0$, $Z_s\to0$ and Γ → −1 (ordinary metal). At $f_0$, $Z_s\to\infty$ and **Γ = +1: an artificial magnetic conductor (AMC)**. Far above, Γ → −1 again.
- The band where $|Z_s|>\eta_0$ is where the phase lies within ±90°. Solving $|Z_s|=\eta_0$ for small detuning gives $\Delta\omega/\omega_0\approx\sqrt{L/C}/\eta_0$. At resonance $\sqrt{L/C}=\omega_0L=\omega_0\mu_0h$, so **$\Delta f/f_0\approx k_0h\,\mu_r$**: the bandwidth depends only on the thickness in wavelengths (and μr), not on how clever the patch pattern is. Costa et al. [3] show that the patch's own series inductance makes it *narrower* still.
- The edge capacitance of a gap g between coplanar strips of width w is $C=\frac{w\varepsilon_0(1+\varepsilon_r)}{\pi}\cosh^{-1}(a/g)$ (the quasi-static coplanar-strip result, restated from [2] in [4]).

*Designs on JLC 1.43 mm FR-4 (εr 4.5), a/g = 20 (script §5):*

| f0 | L | C needed | a (period) | g | a/λ0 | ±90° BW (k0h) |
|---|---|---|---|---|---|---|
| 433.92 MHz | 1.80 nH | 74.9 pF | (w·acosh(a/g) = 4.8 m: impossible with a printed gap) | — | — | 1.30 % = 5.6 MHz |
| 2.45 GHz | 1.80 nH | 2.35 pF | 43.2 mm | 2.16 mm | 0.35 | 7.3 % |
| 5.8 GHz | 1.80 nH | 0.419 pF | 7.71 mm | 0.386 mm | 0.15 | 17.4 % |

*openEMS check of the 5.8 GHz cell* (`s5_mushroom_openems.py`): one unit cell with PMC/PEC side walls (an infinite array at normal incidence), a 0.3 mm via and a TEM port, referenced to a run with a solid metal sheet at the patch plane. Pre-registered targets were f0 within 10 % and bandwidth within 30 % of the model, and |Γ| > 0.98 lossless. **All passed:** f0 = **5.819 GHz** (model 5.80 GHz; mesh ×0.7 gives 5.820), bandwidth **16.7 %** (model 17.4 %). The phase follows the simple LC curve within 4° from 4.5 to 7.5 GHz (openEMS 83° / 4° / −74° at 5.4 / 5.8 / 6.2 GHz; model 79° / 1° / −75°). The "more exact" variant with the full grounded-slab impedance $j(\eta_0/\sqrt{\varepsilon_r})\tan(k_dh)$ is *worse* (f0 5.67 GHz). Under the patches the vias force a different field than a bare slab, so do not assume that refining one part of a lumped model improves it. A lossy run (tan δ = 0.02) gives **|Γ| = 0.82 at resonance (−1.7 dB, 33 % absorbed)**. An FR-4 AMC under an antenna is an absorber as much as a reflector, which is the principle of thin "Salisbury-like" circuit-analogue absorbers.

*Surface-wave band gap.* Below $f_0$ the surface is inductive and supports bound TM surface waves, $\beta=k_0\sqrt{1+(X/\eta_0)^2}$ in the effective-medium picture. Above $f_0$ it is capacitive and supports TE waves. Around $f_0$ neither propagates in the real (periodic) structure. The TM branch flattens and hits the Brillouin-zone edge $\beta=\pi/a$, and the TE branch only becomes bound above the gap. The effective-medium model cannot predict the gap edges: for the 2.45 GHz design the TM branch would have to reach β/k0 = 1.73 at 2 GHz to touch the zone edge, while the model gives 1.016. Use a full-wave eigenmode (Floquet) simulation for the gap. The reflection-phase band and the surface-wave gap overlap but are **not the same band** [2].

*Where the model breaks:* a/λ0 above ~0.2 (the 2.45 GHz design is 0.35: treat its numbers as rough), oblique incidence (TM incidence on a mushroom is strongly angle-dependent), thick substrates (h > λ/10 in the medium), finite arrays a few cells wide (edge cells detune), and loss.

**2. Metamaterials and CRLH lines.** "Metamaterial" means a periodic structure whose cells are much smaller than the wavelength, so that it acts as an effective medium with engineered ε and μ, including negative values. The transmission-line version is the **composite right/left-handed (CRLH) line** (Caloz & Itoh [5]). The host line contributes series $L_R$ and shunt $C_R$; added series capacitors $C_L$ and shunt inductors $L_L$ give $Z=j(\omega L_R-1/\omega C_L)$ and $Y=j(\omega C_R-1/\omega L_L)$ per cell, and $\cos\beta p=1+ZY/2$.
- Below both the series and shunt resonances, Z is capacitive and Y inductive: the cell is a high-pass ladder whose wave is **backward** (phase velocity opposite to group velocity, "left-handed"). Script at 0.7 f0: βp = −0.366 rad with positive group velocity.
- If $\omega_{se}=1/\sqrt{L_RC_L}$ and $\omega_{sh}=1/\sqrt{L_LC_R}$ differ, there is a gap between them (script: making $L_L$ 1.5× too big opens 2.000–2.450 GHz). **Balanced** ($L_RC_L=L_LC_R$) closes it: at $\omega_0$, β = 0 with a finite group velocity, and $Z_B=\sqrt{L_R/C_R}=\sqrt{L_L/C_L}$.
- Example element values, 50 Ω balanced at 2.45 GHz: $L_R$ 1.62 nH, $C_R$ 0.650 pF, $L_L$ 6.50 nH, $C_L$ 2.60 pF per cell (script §6). These are 0402-size parts, so parasitics (≈ 0.4 nH ESL) are already 25 % of $L_R$: simulate with real part models.
- Uses: dual-band and wide-band phase shifters (the phase slope can be set independently of the delay), "zeroth-order" resonators whose resonant frequency does not depend on length, backfire-to-endfire leaky-wave antennas that scan through broadside without an open stop band, compact couplers.

**3. Hype check — what periodic structures and metamaterials cannot do.**
| Claim | Verdict | Why |
|---|---|---|
| "A metamaterial antenna beats the Chu limit." | **No.** | Chu–McLean $Q\ge1/(ka)^3+1/(ka)$ bounds *any* passive, linear antenna inside a sphere of radius a ([Bode–Fano/Chu](broadband-matching-bode-fano.md)). Metamaterial loading trades size for bandwidth or efficiency like any reactive loading. Papers claiming more usually omit the matching network, ohmic loss or the ground plane from the sphere. |
| "An AMC lets me put a broadband antenna flush on the airframe." | **Narrowband.** | ±90° band ≈ k0h: 1.43 mm gives 1.3 % at 433 MHz (5.6 MHz) and 7.3 % at 2.45 GHz. A metal-backed absorber obeys the same kind of thickness–bandwidth limit (Rozanov 2000 [7]), and the AMC is lossy on FR-4 (33 % absorbed at resonance). For a rocket, a slot, a conformal patch over the airframe as its ground plane, or a λ/4 cavity-backed antenna is usually better ([antennas on rockets](../08-antennas/antennas-on-rockets.md)). |
| "EBG removes surface waves." | **Only in its gap**, and only for enough rows. | A few rows give a few dB of extra isolation; the gap is narrow on thin boards and the cells are large at UHF. |
| "Negative index gives a perfect (super) lens." | **Not with real loss.** | The sub-wavelength resolution needs n = −1 almost exactly and very low loss; loss limits it to a modest improvement over a narrow band. |
| "A left-handed line is new physics." | **Old physics, new packaging.** | Backward space harmonics were analysed by Brillouin [8] and used in backward-wave oscillators in the 1950s; a CRLH line is a high-pass/low-pass LC ladder. |
| "Periodic loading makes a line lossless/faster." | **No.** | Loaded lines are slower (they add C or L), and band edges have zero group velocity, which raises loss per metre. |

## Design equations & rules of thumb
| Equation / rule | When valid | Typical value |
|---|---|---|
| $\cosh\gamma d=(A+D)/2$ | any reciprocal periodic cell | stop band where \|A+D\| > 2 |
| $Z_B=B/\sqrt{A^2-1}$ | symmetric cell | 1 pF / 10 mm on 50 Ω: 37.0 Ω at 433 MHz |
| slow-wave factor $\sqrt{1+C_l/C'd}$ | cell ≪ λ | 1.347 for 1 pF/10 mm (C′d = 1.23 pF) |
| first loaded-line stop band | up to the unloaded Bragg frequency c/(2d√εeff) | 4.79–8.13 GHz for the example |
| Bragg FBW $(4/\pi)\arcsin(\lvert Z_1-Z_2\rvert/(Z_1+Z_2))$ | λ/4 sections | 30/80 Ω: 60 % |
| leaky-wave $\sin\theta=\sqrt{\varepsilon_{eff}}-\lambda_0/p$ | n = −1 harmonic | 5.8 GHz, p = 28.0 mm: 1.8°/100 MHz |
| TM0 β/k0 ≈ 1 + ½[k0h(1−1/εr)]² | thin grounded slab | 1.43 mm FR-4: 1.0016 at 2.45 GHz |
| HED surface-wave loss, J–A | h/λ0 ≲ 0.015 | 1.43 mm FR-4: 10 % at 2.45 GHz |
| AMC: $f_0=1/2\pi\sqrt{LC}$, BW = k0h | a ≲ λ/5, normal incidence | 5.8 GHz: openEMS within 0.3 % and 1 point |
| CRLH balanced: $L_RC_L=L_LC_R$ | lumped cells ≪ λ | gap closes |

## Worked examples

### Example 1 — slowing a 433.92 MHz delay line with periodic capacitors
A λ/4 50 Ω microstrip at 433.92 MHz on JLC 2-layer (εeff 3.40) is 93.7 mm long. Load it with a 1 pF 0402 capacitor to ground every 10 mm. The cell's θ is 9.61°; with b = ωC Z0 = 0.136 the Bloch phase is βd = 12.94° per cell (slow-wave factor 1.347), so a quarter wave now needs 90/12.94 = **6.96 cells ≈ 70 mm** (−26 %). The Bloch impedance is **37.0 Ω**: to keep the line matched to 50 Ω, widen the spacing or narrow the trace so that $\sqrt{L'/(C'+C_l/d)}$ returns to 50 Ω: solving $Z_1/\sqrt{1+C_lcZ_1/(\sqrt{\varepsilon_{eff}}d)}=50$ gives a **≈ 74 Ω trace** with the same loading (ignoring the small change of εeff with width). Bonus: the loaded line stops everything from 4.79 to 8.13 GHz. Cost: 0402 ESL (≈ 0.4 nH) resonates with 1 pF at 8 GHz, and the via adds ≈ 0.5 nH ([canonical values](../00-math-foundations/canonical-values-and-conventions.md)), so above ~4 GHz the "capacitor" is an inductor and the model must include it.

### Example 2 — how much does a 2.45 GHz printed dipole on 1.6 mm FR-4 lose to surface waves?
On the 1.43 mm core (εr 4.5), h/λ0 = 0.0117, the exact calculation gives 90.3 % space-wave efficiency, so **≈ 10 % (0.44 dB)** of the power goes into the TM0 surface wave, before any dielectric or conductor loss. At 5.8 GHz it is 22 % (1.1 dB) and at 433 MHz 1.8 %. The surface wave reaches the board edge and re-radiates there: expect ripple in the pattern and a raised back lobe on boards a few wavelengths across. Mitigations: a thinner or lower-εr substrate under the antenna, cutting the substrate away, a board edge ≥ λ/4 from the element, or a ring of EBG cells (at 5.8 GHz they are 7.7 mm).

### Example 3 — a 5.8 GHz frequency-scanned leaky-wave antenna for a bench radar
On 50 Ω JLC microstrip, put narrow radiating stubs every p = 28.0 mm (λg at 5.8 GHz). The beam is broadside at 5.8 GHz and scans −7.9° to +6.8° over 5.4–6.2 GHz. Tuning the FMCW or CW source therefore steers the beam about 15° with no phase shifters. Expect a dip in gain right at broadside (the open stop band) unless each cell is matched (for example, a quarter-wave-offset pair of stubs per cell). Note that εeff of microstrip rises slightly with frequency, which speeds the scan a little; the script uses a constant 3.40.

### Example 4 — is an AMC worth it under a 433 MHz rocket antenna?
At 433.92 MHz on 1.43 mm FR-4 the AMC bandwidth is k0h = **1.3 % = 5.6 MHz**, enough in principle for the 433.05–434.79 MHz band (1.74 MHz). But each cell needs 75 pF, and a printed gap cannot provide it, so it must be a chip-capacitor-loaded grid with ±5 % capacitors (each ±5 % in C moves f0 by ∓2.5 % = ±11 MHz, twice the bandwidth). It also needs several cells per side, i.e. a structure tens of centimetres across, and on FR-4 it absorbs a third of the power at resonance. Verdict: **no**. Use the airframe as the ground plane of a monopole, slot or wrap-around patch instead.

### Example 5 — a balanced CRLH unit cell for a 2.45 GHz phase shifter
Target $Z_B$ = 50 Ω, transition at 2.45 GHz, right-handed scale 4.9 GHz: $L_R$ = 1.62 nH, $C_R$ = 0.650 pF, $L_L$ = 6.50 nH, $C_L$ = 2.60 pF. Check the balance: $L_RC_L$ = 4.22 × 10⁻²¹ = $L_LC_R$. Below 2.45 GHz the line is backward-wave (at 1.72 GHz, βp = −0.37 rad per cell); above it, forward-wave. If $L_L$ comes out 50 % high (a wrong via inductance, for example), a 2.00–2.45 GHz stop band opens: measure the S21 of a 5-cell test strip before building the device.

## Practical notes
- **Simulate one cell, not the whole array.** openEMS (or any FDTD/FEM code) with PEC/PMC walls gives normal-incidence reflection phase in under a minute (`s5_mushroom_openems.py`). Periodic (Floquet) boundaries give oblique incidence and the eigenmode band diagram. A finite array then needs a full model, because edge cells detune.
- **Fabrication on JLC:** a 0.386 mm gap and 0.3 mm vias are routine. f0 scales as $1/\sqrt{C}$ with $C\propto(1+\varepsilon_r)$, so FR-4's εr spread of 4.3–4.7 moves f0 by about ±1.8 %, well inside a 17 % band. Copper thickness and soldermask over the gaps add capacitance and pull f0 down a few per cent: re-simulate with the mask.
- **Measure reflection phase** with two horns or an open waveguide at normal incidence ([Green's functions Level 3b D](../02-electromagnetics/greens-functions-and-integral-equations.md) for the open-guide pattern), referenced to a flat copper plate of the same size (Γ = −1). This is the same reference trick as the simulation.
- **Loaded lines with real parts:** include the capacitor ESL and the via inductance. Above the part's self-resonance the "capacitive loading" becomes inductive and the stop-band structure changes.
- **Surface waves are a layout issue at 2.4 GHz and above** on 1.6 mm FR-4 (≥ 10 % for a printed dipole). At 433/915 MHz they are 2–4 %, smaller than FR-4 dielectric loss in most antennas.

## Common mistakes & misconceptions
- **Using the line's $Z_0$ for a heavily loaded line.** The wave sees the Bloch impedance (37 Ω in Example 1), not the trace impedance.
- **Expecting a stop band "at λ/2 spacing" regardless of loading.** Loading moves the lower edge down (4.79 GHz vs the 8.13 GHz Bragg frequency in the example).
- **Treating the J–A surface-wave formula as exact.** It is good to 0.5 point for h/λ0 ≲ 0.012 and 5.6 points optimistic at h/λ0 ≈ 0.05.
- **Confusing the AMC reflection-phase band with the surface-wave band gap.** They overlap but are different; the gap needs a band-diagram (eigenmode) simulation.
- **Believing a clever patch shape widens an AMC.** The bandwidth ≈ k0h·μr is fixed by the thickness; the patch's series inductance only narrows it further.
- **"A more detailed model is always better."** For the mushroom, the full-slab impedance shifted f0 to 5.67 GHz, while openEMS and the simple $\mu_0h$ model both give 5.8 GHz.
- **Forgetting loss in an FR-4 EBG.** At resonance it absorbs about a third of the incident power.
- **Metamaterial claims that ignore Chu, Bode–Fano or the thickness limit** (see the hype-check table).

## How to simulate / verify
- `python3 tools/verify/s5_bloch_ebg.py` (≈ 3 s, 17/17 checks): Bloch condition and ABCD eigenvalues, Bloch impedance termination, light-loading formulas, stop band and per-cell attenuation; Bragg-line bandwidth; leaky-wave scan; grounded-slab TM0 and the exact HED surface-wave efficiency vs Jackson–Alexopoulos (with its thin-substrate convergence); mushroom f0, ±90° bandwidth = k0h, designs at 0.434/2.45/5.8 GHz; CRLH balance, gap edges and backward-wave band.
- `~/opt/openEMS/venv/bin/python tools/verify/s5_mushroom_openems.py` (≈ 2 min; add `lossy` for the FR-4 tan δ run): unit-cell reflection phase of the 5.8 GHz mushroom. Results in `tools/verify/s5_mushroom_openems_results.txt`.
- `python3 tools/verify/s5_waveguide_extras.py` §4: the transverse-resonance surface-wave solver used here, cross-checked against `e11_greens.py` and the 12-domain values.
- scikit-rf: build one cell as a `Network`, cascade with `**` and read the Bloch phase from `np.arccos((A+D)/2)` of `n.a`.

## Open questions / gaps
- No full-wave Floquet *eigenmode* (band-diagram) calculation was run, so the mushroom surface-wave gap edges are not computed. openEMS has no eigenmode solver; this needs a phase-shift-wall FDTD run or an FEM code.
- Oblique-incidence AMC behaviour and the reflection phase of finite (e.g. 5 × 5) arrays were not simulated.
- The leaky-wave example assumes constant εeff and ignores the stub loading's effect on β0; a full-wave model of a real cell is needed for a design.
- Rozanov's absorber bound [7] is cited from knowledge; a worked comparison of an AMC with the bound for a given thickness is not yet done.
- The 08/patch-antennas page should link here for surface waves (cross-domain note for the orchestrator).

## Sources
1. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley 2012, §8.1 (periodic structures: Bloch analysis of a loaded line, Bloch impedance, k–β diagram, stop bands), §3.6 (grounded dielectric slab surface waves). (textbook)
2. D. Sievenpiper, L. Zhang, R. F. J. Broas, N. G. Alexópolous, E. Yablonovitch, "High-impedance electromagnetic surfaces with a forbidden frequency band," *IEEE Trans. MTT* 47(11):2059–2074, 1999 — LC model, AMC reflection phase, surface-wave band gap, bandwidth √(L/C)/η. (peer-reviewed; content as restated in [3], [4]; the original was not re-read this session)
3. F. Costa, S. Genovesi, A. Monorchio, "On the bandwidth of high-impedance frequency selective surfaces," *IEEE Antennas Wireless Propag. Lett.* 8:1341–1344, 2009 (arXiv:1001.0523) — parallel-LC bandwidth $(1/\zeta_0)\sqrt{L/C}$ with $L=\mu h$; series FSS inductance reduces the bandwidth. (peer-reviewed; read)
4. U.S. patent texts that restate Sievenpiper 1999, found by web search 2026-10-13 (e.g. the "Electromagnetic band-gap structure" and "Multi-resonant, high-impedance electromagnetic surfaces" families) — sheet capacitance $C=w(\varepsilon_1+\varepsilon_2)\cosh^{-1}(a/g)/\pi$ and bandwidth $\sqrt{L/C}/\sqrt{\mu_0/\varepsilon_0}$. (patent; secondary restatement)
5. C. Caloz, T. Itoh, *Electromagnetic Metamaterials: Transmission Line Theory and Microwave Applications*, Wiley/IEEE 2006, ch. 3 (CRLH transmission lines, balanced condition, dispersion) and ch. 6 (leaky-wave antennas). (textbook; cited from knowledge, dispersion re-derived in the script)
6. D. R. Jackson, N. G. Alexopoulos, "Simple approximate formulas for input resistance, bandwidth, and efficiency of a resonant rectangular patch," *IEEE Trans. AP* 39(3):407–410, 1991 (bibliographic details checked against Crossref by W5-S18b, 2026-10-13) — HED surface-wave efficiency with $c_1=1-1/n^2+2/(5n^4)$; as given in D. R. Jackson, ECE 6345 lecture notes (Univ. Houston) and arXiv:2403.18844 (equivalent εr form, algebra checked here). (peer-reviewed / lecture notes)
7. K. N. Rozanov, "Ultimate thickness to bandwidth ratio of radar absorbers," *IEEE Trans. AP* 48(8):1230–1234, 2000. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
8. L. Brillouin, *Wave Propagation in Periodic Structures*, McGraw-Hill 1946 (Dover 1953) — space harmonics, Brillouin zones, backward waves. (textbook; cited from knowledge)
9. R. E. Collin, *Foundations for Microwave Engineering*, 2nd ed., IEEE Press 2001, ch. 8 (periodic structures and filters: loaded lines, k–β diagram, Floquet's theorem). (textbook; chapter 8 title "Periodic Structures and Filters" checked against the Wiley-IEEE chapter record (doi:10.1109/9780470544662.ch8) by W5-S18b, 2026-10-13; content cited from knowledge)
10. Verification: `tools/verify/s5_bloch_ebg.py`, `tools/verify/s5_mushroom_openems.py`, `tools/verify/s5_waveguide_extras.py`. (numerical check)
