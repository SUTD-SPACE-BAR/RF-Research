---
title: Measuring εr and tanδ — cavity perturbation, split-post/split-cylinder, ring and two-line methods, resonator coupling and Q₀ (DIY with a NanoVNA)
domain: 17-test-measurement
slug: resonator-and-cavity-perturbation-permittivity-measurement
tags: [permittivity, dielectric-constant, loss-tangent, Dk, Df, cavity-perturbation, split-post-dielectric-resonator, split-cylinder, ring-resonator, two-line-method, multiline, free-space-method, NRW, resonator-coupling, unloaded-Q, loaded-Q, coupling-coefficient, critical-coupling, nanovna, litevna, fr-4, jlcpcb, fibreglass, nose-cone, radome]
prerequisites:
  - vna-fundamentals-calibration.md
  - nanovna-librevna-practical.md
  - ../02-electromagnetics/dielectrics-permittivity-loss-tangent.md
  - ../02-electromagnetics/waveguides-and-cavity-resonators.md
  - ../01-circuit-theory/resonance-and-q.md
related:
  - ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md
  - ../03-transmission-lines-matching/microstrip-discontinuities.md
  - ../13-pcb-rf-layout-emc/stackups-and-materials.md
  - ../08-antennas/antennas-on-rockets.md
  - ../08-antennas/antenna-measurement.md
  - ../02-electromagnetics/boundary-conditions-reflection-refraction.md
  - fixtures-and-deembedding.md
  - bench-measurement-recipes.md
level: mixed
confidence: medium
last_updated: 2026-10-14
---

# Measuring εr and tanδ — cavity perturbation, split resonators, ring and two-line methods, and resonator coupling

## Questions this page answers
- How do I measure the dielectric constant and loss tangent of FR-4 (or my JLCPCB stack-up) with a NanoVNA?
- What is cavity perturbation, and where do the frequency-shift and Q formulas come from?
- What are split-post and split-cylinder resonators, and why do labs use them?
- How does a microstrip ring resonator give εeff, and how do I turn that into εr?
- What is the two-line method, and why do the connectors cancel out?
- What do under-coupled, critically coupled and over-coupled mean, and how do I get the unloaded Q from a measured loaded Q?
- What is the εr of my rocket's fibreglass nose cone, and how do I measure it?
- Why do different labs and datasheets quote different Dk for the "same" FR-4?

## TL;DR
- **Every resonator method works the same way.** A resonance frequency measures stored energy, which gives ε′. The resonance Q measures loss, which gives ε″ = ε′ tanδ. Transmission-line methods measure phase per length (giving εeff) and attenuation (giving loss).
- **Cavity perturbation** (thin rod or strip parallel to E at the E-maximum of a rectangular TE10p cavity):
  - $\frac{f_0-f_s}{f_0}=2(\varepsilon_r'-1)\frac{V_s}{V_c}$ and $\frac1{Q_s}-\frac1{Q_0}=4\varepsilon_r''\frac{V_s}{V_c}$;
  - checked against a 2-D finite-difference eigen-solution, the error is ≤ 1.3 % for a 1.5 mm-radius FR-4 rod (Δf/f = 0.5 %) and 3.2 % for εr = 10;
  - in a 100 × 100 × 30 mm box (TE101 at 2.12 GHz), a 3 mm FR-4 rod shifts the resonance by about 10 MHz, which is easy to see on a LiteVNA.
- **Q₀ from what you measure.** You measure the loaded Q (QL), which includes the coupling. For a two-port with equal weak coupling, $Q_0=Q_L/(1-|S_{21}(f_0)|)$. For a one-port, $Q_0=Q_L(1+\beta)$, with $\beta=(1\mp|\Gamma_0|)/(1\pm|\Gamma_0|)$. Under- versus over-coupling is told apart by whether the S11 loop encloses the Smith-chart centre (phase swing < 180° or ≈ 360°). The script recovers Q₀ to < 1 % except for extreme over-coupling (|S21| = −0.5 dB, −1.0 %).
- **DIY ring resonator on JLC 2-layer FR-4:**
  - geometry: a 50 Ω ring with 164.7 mm mean circumference (r = 26.2 mm, n = 1 at ~1 GHz), gap-coupled to two feed lines;
  - extraction: $\varepsilon_\text{eff}=(nc/Lf_n)^2$, then invert Hammerstad–Jensen/Kirschning–Jansen for εr;
  - **gap loading biases εr high by +1.8 % (1 mm gaps) to +2.5 % (0.25 mm gaps)**. A model-based fit that includes the gap capacitance removes the bias;
  - FR-4's tanδ ≈ 0.018 limits Q₀ to about 55–60, and the loss tangent comes back within 5 % after the conductor Q is removed.
- **Two-line method:** two lines differing in length by ΔL, through the same connectors. The eigenvalues of $\mathbf A_2\mathbf A_1^{-1}$ are $e^{\pm\gamma\Delta L}$ whatever the connectors are, which gives εeff and α directly. It is broadband and needs no resonator.
- **Fibreglass nose cone:**
  - expect εr ≈ **4.0–4.6** (a Lichtenecker mixing estimate for 30–50 % E-glass with 0–3 % voids) and tanδ ≈ 0.01–0.02;
  - measure a flat witness coupon with the same lay-up, by free-space transmission (2 mm panel: 9.8° insertion phase at 2.45 GHz, 21.7° at 5.8 GHz) or by perturbation of a thin strip in a DIY cavity;
  - **thickness uncertainty dominates** the free-space method: +0.1 mm on 2 mm gives −3.3 % in εr.
- Verified by `tools/verify/e11_permittivity.py` (15/17 checks; the misses are reported below).

## Intuition (no math)
A resonator is an energy store that sloshes energy between electric and magnetic fields at one frequency. Put a little dielectric where the electric field is strong and the field polarises it, storing extra electric energy for the same field. More stored energy at the same "stiffness" means a slower slosh: the frequency drops. How far it drops tells you how strongly the material polarises (ε′). If the material also absorbs a little energy each cycle (ε″), the resonance becomes broader and lower: the Q falls.

The "perturbation" trick is to use a sample so small that it barely changes the field shape. Then the change in frequency is simply proportional to (sample volume) × (field² at the sample) × (εr − 1), divided by the total stored energy, and you can calculate it in closed form. Bigger samples or higher εr bend the field, and the simple formula starts to drift.

A **ring resonator** is a loop of microstrip whose circumference is a whole number of wavelengths. Measuring where the loop resonates gives the wavelength on the board, hence εeff, hence εr. It measures the actual PCB you will build on, including resin content, glass style and copper roughness. Its weakness is the feed: the coupling gaps add capacitance that makes the loop look slightly longer.

**Coupling** is how much the outside world loads the resonator. With weak coupling you see a faint, sharp resonance close to the resonator's own (unloaded) Q. With strong coupling you see a strong, broad resonance whose width is mostly set by the ports. Critical coupling (β = 1) is where the port absorbs exactly as much as the resonator wastes, and a one-port resonance then reflects nothing at f₀. You always measure the loaded Q. You need the coupling to work back to the unloaded Q, which is the only one that tells you about the material.

## The math

### Level 1 — the working formulas

| Method | Measured | Formula | Symbols |
|---|---|---|---|
| Cavity perturbation (rod ∥ E at E-max, TE10p) | $f_0, f_s, Q_0, Q_s$ | $\varepsilon_r'=1+\dfrac{f_0-f_s}{2f_s}\dfrac{V_c}{V_s}$, $\ \varepsilon_r''=\dfrac{V_c}{4V_s}\left(\dfrac1{Q_s}-\dfrac1{Q_0}\right)$ | $V_s$ sample, $V_c$ cavity volume |
| Ring resonator | $f_n$ (n = 1, 2, …) | $\varepsilon_\text{eff}=\left(\dfrac{nc}{2\pi r_mf_n}\right)^2$ → invert microstrip model for εr | $r_m$ mean radius |
| Two-line | $S$ of lines $L_1$, $L_2$ | $\gamma=\dfrac{\ln\lambda_\text{eig}}{L_2-L_1}$, $\varepsilon_\text{eff}=\left(\dfrac{c\beta}{\omega}\right)^2$ | λ_eig eigenvalue of $A_2A_1^{-1}$ |
| Free-space slab | $S_{21}$ through a panel of thickness t | fit $T(\varepsilon_r,t)$ (Level 2) | — |
| Loss from Q | $Q_0$ | $\tan\delta\approx\dfrac{1}{qQ_d}$, $\dfrac1{Q_d}=\dfrac1{Q_0}-\dfrac1{Q_c}$ | q filling factor |

Coupling and Q:
- $Q_L=f_0/\Delta f_{3\,\text{dB}}$;
- one-port: $Q_0=Q_L(1+\beta)$;
- two-port: $Q_0=Q_L(1+\beta_1+\beta_2)$, and with $\beta_1=\beta_2$, $|S_{21}(f_0)|=2\beta/(1+2\beta)$, so $Q_0=Q_L/(1-|S_{21}|)$.

### Level 2 — derivations

**1. Cavity perturbation.** Start from Maxwell's curl equations for the unperturbed mode $(\mathbf E_0,\mathbf H_0,\omega_0)$ and the perturbed one $(\mathbf E,\mathbf H,\omega)$ inside PEC walls. The perturbed cavity contains a sample with $\Delta\varepsilon=\varepsilon_0(\varepsilon_r-1)$ in volume $V_s$.
1. Dot the perturbed curl equations with $\mathbf E_0^*$ and $\mathbf H_0^*$, and the conjugated unperturbed equations with E and H.
2. Subtract, integrate over the cavity, and use the divergence theorem. The surface terms vanish on PEC walls because $\hat n\times\mathbf E=0$.

The result is exact:
$$\frac{\omega-\omega_0}{\omega}=-\frac{\int_{V_s}\Delta\varepsilon\,\mathbf E\cdot\mathbf E_0^*\,dV}{\int_{V_c}(\varepsilon_0\,\mathbf E\cdot\mathbf E_0^*+\mu_0\,\mathbf H\cdot\mathbf H_0^*)\,dV}.$$
The **perturbation approximation** sets $\mathbf E\approx\mathbf E_0$, $\mathbf H\approx\mathbf H_0$ in the denominator. At resonance the electric and magnetic energies are equal, so the denominator is $2\varepsilon_0\int|\mathbf E_0|^2dV$. It also needs the field *inside the sample*:
- for a thin rod or strip **parallel to E**, tangential E is continuous, so $\mathbf E_\text{in}\approx\mathbf E_0$;
- for a sample **perpendicular to E**, it is the normal D that is continuous, so $E_\text{in}\approx E_0/\varepsilon_r$. A depolarisation factor then enters, which is why rods are always placed along E.

For TE101 in an $a\times b\times d$ box, $E_y=E_m\sin(\pi x/a)\sin(\pi z/d)$, so $\int|E|^2dV=E_m^2abd/4$. A full-height rod at the centre has $|E|=E_m$, so
$$\frac{\omega-\omega_0}{\omega}\approx-\frac{(\varepsilon_r-1)E_m^2V_s}{2E_m^2V_c/4}=-2(\varepsilon_r-1)\frac{V_s}{V_c}.$$
Now let $\varepsilon_r=\varepsilon'-j\varepsilon''$ (with $e^{j\omega t}$). The frequency shift becomes complex, $\omega=\omega_r+j\omega_i$ with $Q=\omega_r/(2\omega_i)$. The real part gives the ε′ formula. The imaginary part gives $\Delta(1/Q)=4\varepsilon''V_s/V_c$. This matches the standard forms in Pozar §6.7 and in ASTM D2520 (the latter from knowledge) [1][2].

**2. Coupling and loaded Q (one-port).** Near resonance, model the resonator as a parallel RLC with $Q_0=\omega_0RC$, coupled to a line $Z_0$ through a lossless network. Referred to the resonator, the line is a conductance $G_\text{ext}$. Define $\beta=G_\text{ext}R$, so $Q_\text{ext}=Q_0/\beta$ and
$$\frac1{Q_L}=\frac1{Q_0}+\frac1{Q_\text{ext}}\Rightarrow Q_0=Q_L(1+\beta).$$
At resonance the input reflection, referred to the right plane, is $\Gamma_0=\frac{1-\beta}{1+\beta}$. The magnitude alone gives two roots:
- **under-coupled:** $\beta=\frac{1-|\Gamma_0|}{1+|\Gamma_0|}$, and the S11 locus does not enclose the Smith-chart centre;
- **over-coupled:** $\beta=\frac{1+|\Gamma_0|}{1-|\Gamma_0|}$, the locus encloses the centre, and the phase swings by ≈ 360°.

$Q_L$ comes from the half-power width of the absorbed power $1-|S_{11}|^2$, which is a Lorentzian. Both rules are checked against an exact circuit in the script (§2).

**3. Coupling (two-port, transmission).** With input and output couplings $\beta_1$, $\beta_2$, $|S_{21}(f_0)|=\frac{2\sqrt{\beta_1\beta_2}}{1+\beta_1+\beta_2}$ and $Q_0=Q_L(1+\beta_1+\beta_2)$. For a symmetric fixture, $\beta_1=\beta_2=\beta$, so $|S_{21}|=\frac{2\beta}{1+2\beta}$ and $1+2\beta=\frac{1}{1-|S_{21}|}$. That gives $Q_0=Q_L/(1-|S_{21}|)$. **Weak coupling** (|S21| < −20 dB) makes $Q_L\approx Q_0$ and the result insensitive to unequal coupling. It is the standard choice for material measurement, at the cost of signal-to-noise.

**4. Ring resonator.** A closed loop of mean radius $r_m$ resonates when its circumference is n guided wavelengths: $2\pi r_m=n\lambda_g$, so $f_n=\frac{nc}{2\pi r_m\sqrt{\varepsilon_\text{eff}(f_n)}}$. Inverting gives $\varepsilon_\text{eff}(f_n)$. Then solve the microstrip model, Hammerstad–Jensen plus Kirschning–Jansen dispersion ([planar lines](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md)), for the εr that reproduces that εeff at that frequency, at the measured W, h and t.

**Loss tangent.** Total $1/Q_0=1/Q_c+1/Q_d+1/Q_r$ (conductor, dielectric, radiation).
- $Q_c=\beta/(2\alpha_c)$ comes from the conductor-loss formula (include roughness).
- For microstrip, $Q_d=1/(q\tan\delta)$, with filling factor $q=\frac{\varepsilon_r(\varepsilon_\text{eff}-1)}{\varepsilon_\text{eff}(\varepsilon_r-1)}$ (≈ 0.88 for 50 Ω on FR-4).
- Radiation from a ring is small when $r_m\gg W$ and h ≪ λ.

**Gap-loading bias.** The coupling gaps put a series $C_s$ and shunt $C_p$ at the ring (see the Kirschning gap model in [discontinuities](../03-transmission-lines-matching/microstrip-discontinuities.md)). They add capacitance at two voltage maxima, which lowers every $f_n$ by about the same fraction, and that biases εr high. Weaker coupling (bigger gaps) shrinks $C_s$ but not $C_p$, which tends to an open-end capacitance. A bias therefore remains even for weak coupling: +1.8 % in the script for 1 mm gaps. Two remedies:
- fit the full circuit model (ring + gap model) to the measured $f_n$, which takes the bias to ≈ 0 in the script;
- use two rings of different circumference and difference them.

**5. Two-line method.** Let the measured ABCD (or T) matrix of each line include unknown, identical input and output error boxes X and Y: $\mathbf A_i=\mathbf X\mathbf L_i\mathbf Y$. Then $\mathbf A_2\mathbf A_1^{-1}=\mathbf X\,\mathbf L_2\mathbf L_1^{-1}\,\mathbf X^{-1}=\mathbf X\,\mathbf L_{\Delta L}\,\mathbf X^{-1}$. This is a similarity transform, so its **eigenvalues** equal those of a uniform line of length ΔL, $e^{\pm\gamma\Delta L}$, whatever X and Y are. The result is $\gamma=\alpha+j\beta$ with a $2\pi m/\Delta L$ phase ambiguity, resolved by choosing ΔL short enough or using a rough εeff estimate. This is the core of multiline TRL (Marks 1991) [5]. It assumes the two connectors are *repeatable*, and that both lines have the same cross-section and impedance.

**6. Free-space transmission through a slab.** At normal incidence, a slab of thickness t and index $n=\sqrt{\varepsilon_r}$ in air has interface reflection $\Gamma=\frac{1-n}{1+n}$ and internal transit $P=e^{-jk_0nt}$. Normalised to the empty (air) path:
$$S_{21}^\text{norm}=\frac{(1-\Gamma^2)P}{1-\Gamma^2P^2}e^{+jk_0t}.$$
For a thin, low-loss slab, $\angle S_{21}\approx-k_0t(\sqrt{\varepsilon_r'}-1)$ and $|S_{21}|$ in dB ≈ $-8.686\cdot\frac{k_0t\varepsilon_r''}{2\sqrt{\varepsilon_r'}}$ (plus a small mismatch term). Fitting the full complex expression over a band (Nicolson–Ross–Weir uses S11 and S21 together) gives ε′ and ε″. The thickness enters directly as $k_0t$, so **any thickness error maps one-to-one into √εr error**.

### Level 3 — what the formulas leave out, and laboratory methods

**Validity of perturbation.**
1. **Field change in and near the sample.** The exact rod solution, inside and outside, includes Bessel-function corrections of order $(k_0r\sqrt{\varepsilon_r})^2$ and depends on the rod cross-section, and the sample perturbs the field around it. In the FD check (100 mm cavity, 2.12 GHz) the frequency-shift error was −1.3 % for r = 1.5 mm (εr 4.4), −2.8 % for r = 3 mm, −0.7 % for r = 6 mm (partial cancellation between in-rod field enhancement and the cosine fall-off of the cavity field across a wide rod), and −3.4 % for εr = 10 at r = 1.5 mm. The loss term is affected more: 1/Q is under-predicted by 3–9 %, rising with rod size.
2. **Sample holes.** Inserting a sample needs a hole in the cavity wall. Holes below cut-off leak little, but they shift $f_0$. Measure $f_0$ with the hole present and the sample removed.
3. **Calibration against a reference sample** (PTFE, εr 2.05; or a quartz rod, εr ≈ 3.8) absorbs most of the geometry error. This is how ASTM D2520 practice is usually done.

**Split-post dielectric resonator (SPDR).** A thin sheet sample (e.g. a 0.2–1.6 mm PCB laminate) is slid into the gap between two low-loss dielectric resonator pucks in a metal enclosure. The TE01δ mode has E parallel to the sheet, so there is no depolarisation, and the sheet sees a strong, nearly uniform field. The analysis is a rigorous Rayleigh–Ritz or mode-matching computation per fixture, supplied as tabulated $K(\varepsilon_r,h)$:
$$\varepsilon_r'=1+\frac{f_0-f_s}{hf_0K(\varepsilon_r',h)},\qquad\tan\delta=\frac{1/Q_s-1/Q_{DR}-1/Q_c}{p_{es}},$$
where $p_{es}$ is the electric filling factor of the sample. Typical uncertainty is ±0.3 % in ε′ and ~2×10⁻⁵ resolution in tanδ, at fixed frequencies of 1–20 GHz (Krupka et al.) [3]. SPDRs are the reference method for laminate Dk/Df and give in-plane values.

**Split-cylinder resonator** (NIST; IPC TM-650 2.5.5.13). A TE011 cylindrical cavity is cut in half across its axis, and the sheet sample is clamped between the halves. Mode-matching analysis handles the fringing in the gap. It is broadband in the sense that several TE01p modes give several frequencies, and it also measures in-plane permittivity (Janezic & Baker-Jarvis) [4].

**Clamped stripline and full-sheet resonance** (IPC TM-650 2.5.5.5/2.5.5.6) measure out-of-plane or effective values on unclad laminate. **These different methods give different "Dk" for anisotropic glass-weave materials** (see the [dielectrics page](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md)), which is one reason datasheets differ.

**Transmission/reflection (NRW, NIST TN 1355).** Measure S11 and S21 of a sample filling a coax airline or waveguide section, or a large panel in free space. The method inverts for both ε and μ. It fails (ill-conditioned) at frequencies where the sample is a multiple of λ/2 thick, and very thin samples give poor loss resolution. Baker-Jarvis et al. derive the uncertainty propagation and iterative alternatives [6].

**Anisotropy.** Ring and microstrip methods measure mostly the vertical (z) component of permittivity, because microstrip E is mostly vertical. SPDR and split-cylinder measure the in-plane components. On 7628-style FR-4 these can differ by a few percent. Use the method whose field orientation matches your application.

**Conductor roughness** makes a ring or two-line measurement report a higher "design Dk" than an SPDR on the same laminate: the rough copper slows the wave and adds loss that a smooth-copper model attributes to the dielectric. That is a feature, because it is what your circuit sees. Rogers' "design Dk" values are exactly this.

## Design equations & rules of thumb

| Rule | When valid | Typical number |
|---|---|---|
| $\Delta f/f=2(\varepsilon'-1)V_s/V_c$ | thin sample ∥ E at E-max of TE10p | 3 mm FR-4 rod in 100 × 100 mm box: 4.9×10⁻³ (10 MHz at 2.12 GHz) |
| $\Delta(1/Q)=4\varepsilon''V_s/V_c$ | same | tanδ 0.02 rod: 2.5×10⁻⁴ |
| Keep Δf/f ≲ 1–2 % | perturbation accuracy ~1–3 % | size the sample accordingly |
| Weak coupling: \|S21\| < −20 dB | material Q measurement | QL ≈ Q0 within ~10 % |
| $Q_0=Q_L/(1-|S_{21}|)$ | symmetric two-port | exact for an ideal coupled resonator |
| $Q_0=Q_L(1+\beta)$ | one-port | resolve over/under coupling from the Smith loop |
| $f_n=nc/(2\pi r_m\sqrt{\varepsilon_\text{eff}})$ | ring, $r_m\gg W$ | r = 26 mm: 1, 2, 3, 4 GHz on 1.5 mm FR-4 |
| Ring Q₀ on FR-4 | tanδ ≈ 0.018 | 55–60 (dielectric-limited) |
| Gap-loading bias | uncorrected ring | +1.8 % (1 mm gap) to +2.5 % (0.25 mm) in εr |
| $\Delta\phi\approx k_0t(\sqrt{\varepsilon_r}-1)$ | thin slab, normal incidence | 2 mm, εr 4.4: 9.8° at 2.45 GHz |
| $\delta\varepsilon_r/\varepsilon_r\approx-2\,\delta t/t$ (thin slab, phase-dominated) | free-space method | 5 % thickness error → −3.3 % (fit) |

## Worked examples

### Example 1 — DIY ring resonator for the JLC 2-layer board (εr and tanδ of "your" FR-4)
**Design.** Use JLC 2-layer 1.6 mm (JLC0216A: **1.43 mm core**, [canonical width table](../13-pcb-rf-layout-emc/stackups-and-materials.md#canonical-50-ω-width-table)). A 50 Ω line is W ≈ 2.76 mm bare for εr ≈ 4.35 (2.69 mm masked from JLC's calculator at its εr 4.5). The script's synthetic test uses h = 1.51 mm as a **model input** (W 2.91 mm); because W/h is set by Z0 = 50 Ω, εeff and the ring size are the same to 0.03 % for either h (scratch re-run with `tline_microstrip`), so the numbers below hold for the 1.43 mm board. The target is n = 1 near 1 GHz with harmonics at 2, 3 and 4 GHz:
- mean circumference $L=c/(f_1\sqrt{\varepsilon_\text{eff}})$ = **164.7 mm**, mean radius 26.2 mm;
- two 50 Ω feed lines ending 1.0 mm from the ring at diametrically opposite points, with edge-launch SMAs;
- order the board **without soldermask over the ring** (mask adds ~2–3 % to εeff), or deliberately with it, if that is what you want to characterise.

**Measure** S21 with a LiteVNA (H4 is OK for n = 1; use LiteVNA or LibreVNA for 2–4 GHz). Use ≥ 1001 points and a 50 MHz span around each peak, after a through calibration. In the script's model, |S21| at the peaks is −47 / −40 / −37 / −34 dB, with QL ≈ 55–59.

**Extract.** If $f_1$ = 0.9919 GHz, then $\varepsilon_\text{eff}=(c/(0.1647\cdot0.9919\times10^9))^2$ = 3.368. Inverting Kirschning–Jansen at W, h and f gives εr = 4.429, which is 1.8 % above the true 4.35 because of gap loading. A model-based fit (ring + Kirschning gap model, script §3) returns **4.350**. For loss, Q₀ = 54.9. Remove $Q_c$ (from α_c ≈ 0.4 dB/m at 1 GHz for smooth copper; add a roughness factor for real copper). The resulting $Q_d$ with q = 0.88 gives tanδ = **0.0176** (true 0.018).

**Measure the actual h and W** with calipers or a microscope cross-section (JLC states a 1.43 mm core for its 1.6 mm 2-layer board; 1.51 mm is a common model input, not JLC's stated dielectric). A 5 % error in h gives roughly 1–2 % in εr; inverting with h = 1.51 mm when the board's core is 1.43 mm (W 2.76 mm) gives εr +0.5 % high at 1 GHz (K-J inversion, scratch check).

### Example 2 — two-line method on the same panel
Put two 50 Ω lines, 30 mm and 130 mm long, with identical SMA launches, on the same panel. Measure both, then form $A_2A_1^{-1}$ (scikit-rf: `rf.Network` → `.a`) and take the eigenvalues. The script's synthetic data include a launch model (0.6 nH, 0.35 pF and a 2 mm 60 Ω neck) that would wreck a single-line measurement. The method recovers εr = 4.3500 and tanδ = 0.0180 at 0.5, 1, 2.45 and 4 GHz. **The result is broadband**, so it shows the slow fall of FR-4 Dk with frequency. ΔL = 100 mm is about 0.6 λg at 1 GHz: choose ΔL so that $\beta\Delta L$ stays away from multiples of π over your band, or use three lines (multiline TRL).

### Example 3 — DIY cavity for small samples (2.1 GHz)
**Cavity:** solder a 100 × 100 × 30 mm rectangular box from copper-clad FR-4 offcuts, or use a die-cast aluminium box of similar size. TE101 is at $f=\frac c2\sqrt{a^{-2}+d^{-2}}$ = **2.120 GHz**, with E vertical (along the 30 mm dimension), maximum at the centre. Couple it with two small loops or probe SMAs on the side walls, weakly (|S21| ≈ −25 dB). A soldered copper-clad box gives Q₀ of roughly 1 000–3 000.

**Sample:** a 2 × 3 mm × 30 mm strip of the material, standing vertically through the centre (through a 4 mm hole in the lid, or glued to a thin foam spacer). $V_s/V_c$ = 6 mm²/(100 mm × 100 mm) = 6×10⁻⁴. For εr = 4.4−j0.07 the predicted shift is Δf/f = 2(3.4)(6×10⁻⁴) = **4.1×10⁻³ (8.7 MHz)** and Δ(1/Q) = 4(0.07)(6×10⁻⁴) = 1.7×10⁻⁴, so an empty Q₀ of 2 000 drops to about 1 500. Both changes are easy to see on a LiteVNA. The formula holds for any thin cross-section, provided the strip is parallel to E and spans the full height.

### Example 4 — the εr of the rocket's fibreglass nose cone
1. **What to expect.** Hand-laid or filament-wound E-glass/epoxy mixes glass (εr 6.1–6.6) and cured epoxy (≈ 3.0–3.6) with some voids. A Lichtenecker logarithmic mixing estimate gives 4.09 / 4.35 / 4.63 for 30 / 40 / 50 % glass by volume, minus about 0.15 for 3 % voids. **So expect 4.0–4.6**, with tanδ 0.01–0.02. The [dielectrics page](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md) found no published value for hobby lay-ups.
2. **Get a sample.** Measure an offcut from the cone's open end, or make a **flat witness panel** with the same cloth, resin and number of plies during the lay-up. A curved cone wall cannot be used directly in either method.
3. **Measurement A — free-space transmission** (cheap; needs a flat panel ≥ 3–4 λ across, e.g. 30 × 30 cm at 5.8 GHz):
   - put two identical 5.8 GHz patch or horn antennas 30–50 cm apart on a rail, connected to the LiteVNA ports;
   - do a "through" normalisation with the panel absent, insert the panel normal to the axis, and record S21 from 2–6 GHz;
   - fit the slab formula. For a 2 mm panel at εr 4.4 the insertion phase is −9.8° at 2.45 GHz and −21.7° at 5.8 GHz, with |S21| ≈ −0.7 dB at 5.8 GHz.

   Time-gate the multipath (VNA time-domain mode) and measure the thickness at several points with a micrometer. **A 0.1 mm thickness error (5 %) gives −3.3 % in εr**, more than all the VNA errors.
4. **Measurement B — cavity perturbation** (Example 3): cut a 2–3 mm-wide strip from the panel or offcut and use it as the sample. This needs only the strip's cross-sectional area, measured to a few %, and gives ε″ as well.
5. **Use the result.** Feed εr and t into the radome/wall transmission model in [boundary conditions](../02-electromagnetics/boundary-conditions-reflection-refraction.md) and the nose-cone detuning procedure in [antennas on rockets](../08-antennas/antennas-on-rockets.md). A 3 mm wall at εr 4.4 detunes a 915 MHz whip by a few percent, and that matters more than the < 0.1 dB of loss.

### Example 5 — reading Q₀ from a coupled resonator
A one-port resonance (e.g. a cavity with one coupling loop) shows |S11| min = 0.536 at 0.98225 GHz, with QL = 117.8 from the half-power width of $1-|S_{11}|^2$. On the Smith chart the resonance loop encloses the centre (phase swing ≈ 353°), so the resonator is **over-coupled**: $\beta=(1+0.536)/(1-0.536)$ = 3.31 and $Q_0=117.8\times4.31$ = **508**. The circuit's true value is 509. Had you assumed under-coupling, β = 0.30 and Q₀ = 153, a factor of 3.3 wrong. For material measurement, reduce the coupling until |S11| at resonance is above about 0.8 *and* under-coupled.

## Practical notes
- **Calibrate where it matters.** For resonance frequency, only the frequency accuracy matters, and NanoVNA/LiteVNA synthesisers are accurate to a few ppm. For Q and |S21| a through-normalisation is enough. For the two-line method do a full 2-port calibration (or none, since the method cancels identical connectors).
- **Temperature and moisture.** FR-4 Dk rises with absorbed water (0.1–0.3 %), and so does fibreglass, especially with voids. Dry samples (2 h at 105 °C) or record the conditions. Hand-laid composites can absorb more.
- **Frequency dependence.** FR-4 Dk falls ≈ 0.1 per decade. The ring gives values at each $f_n$ and the two-line method gives a continuous curve. Use the value at your operating frequency (433/915 MHz, 1.575 GHz).
- **Sample-holder effects in cavities.** Lid holes, tape and foam supports (εr ≈ 1.03) all shift $f_0$ a little. Measure the empty cavity *with* the supports in place.
- **Ring practicalities.** Keep $r_m\ge5W$ to limit curvature effects. Keep the feed lines short and straight. Avoid soldermask over the gaps (it changes $C_s$). A tiny asymmetry splits degenerate modes into doublets, so measure both peaks and average.
- **Fixtures** (SMA launches, de-embedding): [fixtures and de-embedding](fixtures-and-deembedding.md). VNA basics: [VNA fundamentals](vna-fundamentals-calibration.md).

**Which method for which job (reader's situations):**

| Job | Best DIY method | Equipment | Expected accuracy |
|---|---|---|---|
| Dk/Df of the JLC stack-up you route on | ring resonator + two-line on a test coupon | LiteVNA/LibreVNA, edge SMAs | εr ±1–2 % (model-fitted), tanδ ±10–20 % |
| Fibreglass, PLA or ABS (small pieces) | cavity perturbation (strip ∥ E) | copper-clad box, LiteVNA | εr ±2–3 %, tanδ ±10 % |
| Large flat panel (radome, witness coupon) | free-space transmission | two antennas, rail, time gating | εr ±3–5 % (thickness-limited) |
| Certified laminate data | SPDR / split cylinder (lab service) | — | εr ±0.3 %, tanδ ~10⁻⁵ |

## Common mistakes & misconceptions
- **Using loaded Q as the material Q.** With strong coupling, QL can be several times smaller than Q₀ (the script's 1 pF coupling: QL = 30 vs Q₀ = 528).
- **Assuming under-coupling from |S11| alone.** The magnitude has two solutions. Look at the Smith-chart loop.
- **Putting the perturbation sample perpendicular to E.** The internal field is then $E_0/\varepsilon_r$, the frequency shift is much smaller, and depolarisation corrections are needed.
- **Samples too large for perturbation.** Δf/f > 2–3 % needs an exact (numerical) model or calibration with known samples.
- **Forgetting the gap capacitance in ring measurements**, which biases εr high by 1–3 %.
- **Using the full board thickness for h** on a 4-layer stack-up, or not measuring h. On JLC 2-layer, 1.43 mm (core) vs 1.6 mm (board) is a 12 % difference in h.
- **Comparing Dk values from different methods** (SPDR vs ring vs datasheet "1 MHz" value) as if they were the same quantity.
- **"Fibreglass is εr ≈ 4.8, like G10."** G10 is a pressed, glass-rich laminate. Hobby lay-ups are usually more resin-rich and have voids: expect 4.0–4.6, and measure it.

## How to simulate / verify
`python3 tools/verify/e11_permittivity.py` (≈ 25 s) runs five checks; output is in `tools/verify/e11_permittivity_output.txt`:
1. **Cavity perturbation vs a 2-D FD eigen-solution** of the TE10p problem (scipy sparse shift-invert, complex εr gives Q). The empty-cavity TE101 is within 10⁻⁵ of analytic. **15/17 checks** pass overall. The two misses:
   - εr = 10 at r = 1.5 mm gives a 3.2 % ε′ error, against a 3 % pre-set bound;
   - the transmission-method Q₀ is −1.04 % at extreme over-coupling (|S21| = −0.5 dB), against a 1 % bound.
2. **Coupling:** exact series-C-coupled parallel-RLC circuits, transmission and reflection methods, with automatic over/under-coupling detection.
3. **Ring resonator** with the Kirschning gap model and dispersive microstrip; uncorrected and model-based εr; tanδ after Q_c removal.
4. **Two-line eigenvalue method** with arbitrary launch error boxes.
5. **Free-space slab fit** with noise; thickness sensitivity; Lichtenecker mixing estimates.

For the real board, model the ring in openEMS (see the [openEMS workflow](../16-simulation-tools/openems-workflow.md); `tools/verify/e11_discontinuities_openems.py` shows the port and mesh set-up for microstrip).

## Open questions / gaps
- No measured data for JLC FR-4 or Space Bar fibreglass yet. The recipe above should be run, and the results added to [stackups](../13-pcb-rf-layout-emc/stackups-and-materials.md) and [dielectrics](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md).
- SPDR and split-cylinder equations are given in outline from knowledge of Krupka et al. and Janezic & Baker-Jarvis. The fixture-specific $K(\varepsilon_r,h)$ tables were not obtained.
- The ASTM D2520 formulas are cited from knowledge; the KB derivation and Pozar's agree with them.
- The non-monotonic perturbation error with rod radius (−1.3 % at 1.5 mm, −2.8 % at 3 mm, −0.7 % at 6 mm) is attributed to competing field corrections. An analytic rod-in-cavity check would confirm it.
- Anisotropic (in-plane vs vertical) εr of hand-laid fibreglass is unknown.

## Sources
1. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley 2012, §6.7 (cavity perturbation: material and shape perturbations), §6.6 (excitation of resonators: coupling coefficient, critical coupling, Q_L/Q_0/Q_e). (textbook)
2. L. F. Chen, C. K. Ong, C. P. Neo, V. V. Varadan, V. K. Varadan, *Microwave Electronics: Measurement and Materials Characterization*, Wiley 2004, chs. 2 (resonator theory and coupling), 5–6 (resonant-perturbation methods), 4 (free-space methods). (textbook; chapter-level, from knowledge)
3. J. Krupka, A. P. Gregory, O. C. Rochard, R. N. Clarke, B. Riddle, J. Baker-Jarvis, "Uncertainty of complex permittivity measurements by split-post dielectric resonator technique," *J. Eur. Ceram. Soc.*, 21:2673–2676, 2001. (peer-reviewed; from knowledge)
4. M. D. Janezic, J. Baker-Jarvis, "Full-wave analysis of a split-cylinder resonator for nondestructive permittivity measurements," *IEEE Trans. MTT*, 47(10):2014–2020, 1999; IPC TM-650 2.5.5.13. (peer-reviewed / standard; from knowledge)
5. R. B. Marks, "A multiline method of network analyzer calibration," *IEEE Trans. MTT*, 39(7):1205–1215, 1991. (peer-reviewed)
6. J. Baker-Jarvis, E. J. Vanzura, W. A. Kissick, *Transmission/Reflection and Short-Circuit Line Methods for Measuring Permittivity and Permeability*, NIST Technical Note 1355(-R), 1993. (government report)
7. A. M. Nicolson, G. F. Ross, "Measurement of the intrinsic properties of materials by time-domain techniques," *IEEE Trans. Instrum. Meas.*, 19(4):377–382, 1970; W. B. Weir, *Proc. IEEE*, 62(1):33–36, 1974 (NRW). (peer-reviewed)
8. ASTM D2520, *Standard Test Methods for Complex Permittivity of Solid Electrical Insulating Materials at Microwave Frequencies and Temperatures to 1650 °C* (method B: resonant cavity perturbation). (standard; from knowledge)
9. K. Lichtenecker, "Die Dielektrizitätskonstante natürlicher und künstlicher Mischkörper," *Phys. Z.* 27:115–158, 1926 (logarithmic mixing rule). (peer-reviewed; from knowledge)
10. This KB: [planar lines](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md) (H-J/K-J models used for the inversion), [discontinuities](../03-transmission-lines-matching/microstrip-discontinuities.md) (gap model), [dielectrics](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md); verification `tools/verify/e11_permittivity.py`. (numerical check)
