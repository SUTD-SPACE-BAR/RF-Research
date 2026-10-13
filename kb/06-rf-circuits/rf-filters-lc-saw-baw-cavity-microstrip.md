---
title: RF filters — technologies (LC, helical, cavity, ceramic, SAW, BAW, LTCC) and microstrip/coupled-resonator design
domain: 06-rf-circuits
slug: rf-filters-lc-saw-baw-cavity-microstrip
tags: [filter, bandpass, lowpass, saw, baw, fbar, cavity, helical, ceramic, ltcc, microstrip, stepped-impedance, coupled-line, hairpin, interdigital, combline, richards, kuroda, coupling-matrix, coupled-resonator, unloaded-q, insertion-loss, cameron-synthesis, generalized-chebyshev, folded-matrix, extracted-pole, linear-phase, trisection, triple-transit-echo, yig]
prerequisites:
  - ../01-circuit-theory/passive-filter-design-prototypes.md
  - ../01-circuit-theory/resonance-and-q.md
  - ../03-transmission-lines-matching/input-impedance-stubs-quarter-wave.md
  - ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md
  - ../03-transmission-lines-matching/s-parameters.md
related:
  - lna-design.md
  - power-amplifiers.md
  - receiver-architectures.md
  - couplers-dividers-combiners.md
  - ../02-electromagnetics/waveguides-and-cavity-resonators.md
  - ../02-electromagnetics/dielectrics-permittivity-loss-tangent.md
  - ../04-real-components-hf/inductors-at-rf.md
  - ../04-real-components-hf/capacitors-at-rf-mlcc.md
  - ../13-pcb-rf-layout-emc/stackups-and-materials.md
  - ../18-components-parts/filter-parts-saw-ceramic-ltcc.md
  - ../20-projects-recipes/bandpass-filter-design-walkthrough.md
  - ../16-simulation-tools/openems-workflow.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# RF filters: technologies and distributed / coupled-resonator design

This page picks up where [passive filter design from prototypes](../01-circuit-theory/passive-filter-design-prototypes.md) stops (g-values, frequency transformations, lumped LC ladders, a 433 MHz harmonic LPF and a 915 MHz lumped BPF). Here: which *technology* to choose, how resonator Q sets insertion loss, how transmission-line filters are derived (Richards, Kuroda, stepped impedance, coupled lines, hairpin, interdigital, combline), and the general coupled-resonator / coupling-matrix method (Hong & Lancaster) used for every narrowband filter from LC to cavity.

## Questions this page answers
- Should my filter be LC, SAW, BAW, ceramic, helical, cavity or microstrip?
- Why can't I build a 1.7 MHz-wide 433 MHz filter from chip inductors?
- How does unloaded Q set a band-pass filter's insertion loss?
- How do Richards' transformation and the Kuroda identities turn a lumped filter into stubs and lines?
- How do I design a stepped-impedance microstrip low-pass or a parallel-coupled-line band-pass filter?
- Why does my microstrip coupled-line filter have a spurious passband at twice the centre frequency?
- What are coupling coefficients and external Q, and how do I extract them from an EM simulation?
- What is a coupling matrix and how do cross-couplings create transmission zeros?
- Why is my 2.45 GHz microstrip filter on FR-4 so lossy?
- What SAW filter should go in front of a GNSS or 433 MHz receiver, and what insertion loss should I expect?
- How do I get a coupling matrix from a specification with prescribed transmission zeros (Cameron's method)?
- Why do I have to re-synthesise all the couplings when I add a cross-coupling?
- Can a filter put a notch on Iridium right next to the GNSS band, and how much does resonator Q matter?
- What is an extracted-pole filter?
- How do I make a filter with flat group delay (linear phase)?
- Why does my SAW filter have ripple in its passband and group delay (triple-transit echo)?
- How does a YIG tunable filter work, and why does it not go below ~2 GHz?

## TL;DR
- **Insertion loss of a band-pass filter is set by resonator Q and fractional bandwidth**: $IL_0\approx4.343\sum g_i/(\text{FBW}\cdot Q_u)$ dB (Cohn). Verified to < 3 % for a 3-pole filter. Consequence: a 433 MHz filter only 1.74 MHz wide (the 433.05–434.79 MHz band, FBW 0.4 %) needs $Q_u$ in the thousands (58 dB loss with Q = 60 LC; 0.9 dB with Q = 4000) — i.e. SAW, helical or cavity, never chip LC.
- **Unloaded Q by technology** (computed or vendor): chip wire-wound L ≈ 30–90; microstrip λ/2 at 2.45 GHz ≈ 47 on 0.8 mm FR-4 (tanδ 0.02) and ≈ 126 on RO4350B (computed); helical ≈ 500–1000 at 433 MHz for 0.5–1 inch cans (empirical $Q\approx50S\sqrt{f}$); air coaxial cavity at 433 MHz ≈ 4000–7000 (conductor-loss limit, computed); SAW ≈ 1000–1500, BAW ≈ 2500–5000 [9].
- **SAW** (≲ 2.5–3 GHz, cheap, 1.5–3 dB IL, TCF ≈ −45 ppm/°C, TC-SAW −15 to −25) and **BAW/FBAR** (1.5–6+ GHz, higher Q and power handling, TCF ≈ −20 to −30 ppm/°C) dominate narrowband front ends [9][10]. Examples: Raltron RSF-433.920-1600 (433.92 MHz, 1.6 MHz BW, 2.4 dB, 3 × 3 mm) [11]; Murata SAFFB1G56KB0F0A (1561–1602 MHz GNSS, ≤ 2.0 dB, 50 Ω, JLCPCB/LCSC stock) [12].
- **Richards' transformation** $\Omega=\tan(\beta l)$ maps L → short stub of $Z=L$, C → open stub of $Y=C$ (commensurate λ/8 lines at $f_c$); **Kuroda identities** (derived here: series stub $Z_a$ + UE $Z_b$ ≡ UE $(Z_a+Z_b)$ + shunt stub $Z_b(Z_a+Z_b)/Z_a$) move stubs apart and convert series stubs to shunt ones. Responses repeat every $4f_c$.
- **Stepped-impedance LPF** (7-pole 0.1 dB Chebyshev, 3 GHz, 0.8 mm FR-4, 110/20 Ω lines 0.27/5.56 mm wide, 40.5 mm long): 0.75 dB loss at 2.45 GHz (0.18 dB lossless), −34.6 dB at 4.9 GHz (scikit-rf, with dispersion and loss).
- **Parallel-coupled-line BPF** (2.45 GHz, 3-pole 0.5 dB, FBW 6 %): $Z_{0e}/Z_{0o}$ = 65.1/40.8 Ω (ends) and 53.8/46.7 Ω (inner); on 0.8 mm FR-4: W/S = 1.34/0.33 mm and 1.52/1.67 mm, ≈ 17 mm per section; ideal ripple reproduced exactly; unequal even/odd phase velocities of microstrip turn the (ideally null) 2f₀ response into a −5.8 dB spurious passband. Expected loss ≈ 6.6 dB on FR-4 vs 2.5 dB on RO4350B.
- **Synthesis from polynomials** (`s15_coupling_matrix.py`):
  - *Method:* Cameron's recursion gives F and P for any prescribed zeros, Feldtkeller gives E, residues give the transversal matrix, and rotations reach the folded form.
  - *Quadruplet* (0.1 dB, zeros ±2.05): $M_{14}=-0.125$, with the main couplings re-synthesised.
  - *GNSS with an Iridium zero* (N = 5): +10 dB at 1616 MHz, but Q_u 500 fills the null to 35 dB.
  - *Linear phase:* a real-axis zero pair cuts the group-delay variation from 31 % to 11 %.
  - *SAW TTE* ripple has period 1/(2τ). *YIG* tunes at 28 GHz/T and stops at γ·4πMs/3 ≈ 1.66 GHz.
- **Coupled-resonator design** (works for any resonator type): $k_{i,i+1}=\text{FBW}/\sqrt{g_ig_{i+1}}$, $Q_e=g_0g_1/\text{FBW}$; extract $k=(f_e^2-f_o^2)/(f_e^2+f_o^2)$ from the two split resonances of a coupled pair and $Q_e=\omega_0\tau_{S11}(\omega_0)/4$ from reflection group delay (both verified). A **coupling matrix** with a negative cross-coupling in a quadruplet adds a pair of transmission zeros (λ ≈ ±2.05 for $M_{14}=-0.12$), raising rejection at λ = ±1.6 from −14 to −21 dB.

## Intuition (no math)
Every band-pass filter is a chain of resonators that pass energy to each other. Each resonator rings at the centre frequency; the strength of coupling between neighbours sets the bandwidth, and the coupling to the outside world (the "external Q") sets the match. The prototype g-values just tell you how strongly each pair must be coupled so the passband comes out flat or equiripple. This view is independent of what the resonators are made of — an LC tank, a quarter-wave line, a helix in a can, a machined cavity, an acoustic wave on a crystal. That is why one design method covers all of them.

Loss is where the technologies differ. In a narrowband filter, energy bounces back and forth inside the resonators many times before it leaves — roughly $Q_{loaded}\approx1/\text{FBW}$ times. Each bounce loses a fraction $1/Q_u$. So the loss scales as (number of bounces) × (loss per bounce) ≈ $Q_{loaded}/Q_u$. A narrow filter from poor resonators is a heater. A 0.4 %-wide filter at 433 MHz needs resonators hundreds of times better than a chip inductor — so you buy an acoustic filter (a SAW converts the electrical signal into a sound wave on a crystal whose Q is ~1000) or you build a metal cavity.

Transmission lines behave like inductors and capacitors when short, and like resonators when a quarter or half wavelength long. Microstrip filters exploit this: a thin high-impedance line is a series inductor, a wide low-impedance line is a shunt capacitor, two lines running side by side a quarter-wave long couple energy like a pair of resonators. Because lines are periodic in frequency, microstrip filters have spurious passbands at multiples of the design frequency — and because microstrip's two coupled modes travel at different speeds (part of the field is in air), the rejection at 2f₀ is worse than the ideal theory says.

## The math

### Level 1 — the loss formula and the design numbers
For an all-pole band-pass filter from a low-pass prototype $g_0\dots g_{N+1}$, fractional bandwidth FBW $=(f_2-f_1)/f_0$ and resonators of unloaded Q $Q_u$:
$$IL_0\approx4.343\,\frac{\sum_{i=1}^Ng_i}{\text{FBW}\;Q_u}\ \text{dB}\qquad(\text{Cohn 1959 [1]; Matthaei §4.13 [2]})$$
Coupled-resonator design values (Hong & Lancaster [3] ch. 8):
$$k_{i,i+1}=\frac{\text{FBW}}{\sqrt{g_ig_{i+1}}},\qquad Q_{e1}=\frac{g_0g_1}{\text{FBW}},\qquad Q_{eN}=\frac{g_Ng_{N+1}}{\text{FBW}}$$

### Level 2 — derivations

**(a) Richards' transformation.** A short-circuited lossless stub of characteristic impedance $Z$ and length $l$ has $Z_{in}=jZ\tan\beta l$; an open stub has $Y_{in}=jY\tan\beta l$. Define $\Omega=\tan\beta l$. Then the stub looks exactly like an inductor $L=Z$ (or capacitor $C=Y$) in the normalised frequency variable $\Omega$. Choosing all stubs λ/8 long at the cutoff $f_c$ puts $\Omega=1$ at $f_c$, so the lumped prototype's response at $\omega/\omega_c$ reappears at $\tan(\pi f/4f_c)$: identical at $f_c$, compressed near $2f_c$ (where $\Omega\to\infty$) and periodic with period $4f_c$ [4 §8.4][3]. (At half the cutoff the stub reactance is 17 % below the lumped value — check A.)

**(b) Kuroda identity (derived).** Richards' stubs end up either in series (hard to build in microstrip) or crowded together at one node. A *unit element* (UE: a line of length λ/8 at $f_c$ and impedance $Z$, ABCD $\frac{1}{\sqrt{1+\Omega^2}}\begin{bmatrix}1&jZ\Omega\\ j\Omega/Z&1\end{bmatrix}$) can be added at the ports (it only adds delay in a matched system) and then shifted through stubs. Multiply the ABCD of a series stub $Z_a$ and a UE $Z_b$, and of a UE $Z_c$ and a shunt stub $Z_d$:
$$\begin{bmatrix}1-\tfrac{Z_a}{Z_b}\Omega^2 & j(Z_a+Z_b)\Omega\\ j\Omega/Z_b&1\end{bmatrix}\ \text{vs}\ \begin{bmatrix}1-\tfrac{Z_c}{Z_d}\Omega^2 & jZ_c\Omega\\ j\Omega(\tfrac1{Z_c}+\tfrac1{Z_d})&1\end{bmatrix}$$
(common factor $1/\sqrt{1+\Omega^2}$ omitted). They are equal when $Z_c=Z_a+Z_b$ and $Z_d=Z_b(Z_a+Z_b)/Z_a$ — the first Kuroda identity (with $n^2=1+Z_a/Z_b$ this is Pozar's Table 8.7 form [4]); its dual swaps series/shunt. Verified numerically (check A1).

**(c) Stepped-impedance low-pass.** A short line of impedance $Z$ and electrical length $\theta\ll\pi/2$ has the ABCD of a series inductance $Z\theta/\omega$ plus shunt capacitances $\theta/(2Z\omega)$ at each end. With $Z=Z_h\gg Z_0$ the series part dominates (inductor); with $Z=Z_l\ll Z_0$ the shunt part dominates (capacitor). So
$$\beta l_L=g_k\frac{Z_0}{Z_h}\ \ (\text{inductor}),\qquad \beta l_C=g_k\frac{Z_l}{Z_0}\ \ (\text{capacitor})$$
evaluated at $f_c$ [4 §8.6]. The approximation worsens as $\theta$ grows and neglects the parasitic shunt C of the inductive lines and the step discontinuities, so the cutoff shifts slightly and the stopband is shallower than the lumped prototype — confirmed below.

**(d) Parallel-coupled-line band-pass.** A coupled-line section a quarter-wave long at $f_0$ with ports on opposite ends of the two lines (the other ends open) is equivalent to an admittance inverter $J$ between two λ/4 lines. Matching the image parameters gives (Pozar §8.8 [4]; Cohn 1958 [5]):
$$Z_0J_1=\sqrt{\frac{\pi\,\text{FBW}}{2g_0g_1}},\quad Z_0J_n=\frac{\pi\,\text{FBW}}{2\sqrt{g_{n-1}g_n}},\quad Z_0J_{N+1}=\sqrt{\frac{\pi\,\text{FBW}}{2g_Ng_{N+1}}}$$
$$Z_{0e}=Z_0\left[1+JZ_0+(JZ_0)^2\right],\qquad Z_{0o}=Z_0\left[1-JZ_0+(JZ_0)^2\right].$$
In a homogeneous (TEM) medium both modes travel at the same speed and the response has a null at $2f_0$. In microstrip the even mode has more field in the dielectric ($\varepsilon_{e,even}>\varepsilon_{e,odd}$), the sections are no longer simultaneously λ/2 at $2f_0$, and a spurious passband appears there (−5.8 dB in the example; check D2). Remedies: wiggly/over-coupled edges, stripline, suspended substrate, or a cascaded low-pass [3 ch. 5].

**(e) Coupling coefficient and external Q from simulation.** For two identical resonators coupled by any mechanism, symmetry splits the resonance into an even mode (magnetic wall, $f_e$) and an odd mode (electric wall, $f_o$). For synchronously tuned resonators
$$k=\pm\frac{f_e^2-f_o^2}{f_e^2+f_o^2}$$
(the sign distinguishes electric from magnetic coupling). For the lumped case of two parallel LC resonators joined by $C_c$: $f_e=1/2\pi\sqrt{LC_r}$, $f_o=1/2\pi\sqrt{L(C_r+2C_c)}$, giving exactly $k=C_c/(C_r+C_c)$ (check E2). The external Q of the input resonator follows from the reflection group delay of the singly loaded resonator: $Q_e=\omega_0\tau_{S11}(\omega_0)/4$ (check E3 recovers 10.26 vs 10.32 designed). In an EM solver (openEMS, Sonnet), sweep gap or tap position, extract $k$ and $Q_e$ curves, and read off the geometry that gives the required values [3 ch. 7].

**(f) Where the loss formula comes from.** Each resonator at the band centre stores energy $W_i$ proportional to $g_i/\text{FBW}$ relative to the power flowing through; dissipation per resonator is $\omega_0W_i/Q_u$; summing and converting the fractional power lost to dB ($4.343\times$ the fraction for small losses) gives the formula. It is exact to first order for small losses; check F: Q = 40/60/100/300 → simulated 3.43/2.30/1.39/0.46 dB vs formula 3.49/2.32/1.39/0.46 dB.

### Level 3 — coupling matrices, cross-coupling, and physical limits
- **Coupling matrix.** Normalise the filter to a lowpass variable $\lambda=\frac{1}{\text{FBW}}\left(\frac{f}{f_0}-\frac{f_0}{f}\right)$. With an $N\times N$ symmetric coupling matrix $M$ (off-diagonal = couplings normalised by FBW, diagonal = resonator detuning) and source/load terms $R_1, R_N$:
$$S_{21}=-2j\sqrt{R_1R_N}\,[A^{-1}]_{N1},\quad S_{11}=1+2jR_1[A^{-1}]_{11},\quad A=\lambda I-jR+M$$
[6][3 ch. 8]. For an inline all-pole Chebyshev $M_{i,i+1}=1/\sqrt{g_ig_{i+1}}$, $R_1=1/g_0g_1$, $R_N=1/g_Ng_{N+1}$ — reproduces the prototype exactly (check G1, error $10^{-15}$).
- **Cross-couplings** between non-adjacent resonators create multiple signal paths whose phases cancel at chosen frequencies: transmission zeros. A cascaded quadruplet (CQ) with negative $M_{14}$ gives a symmetric pair (quasi-elliptic response); a trisection (CT) gives one zero on one side. Negative coupling = opposite sign of the main-line coupling (e.g. electric vs magnetic). Synthesis of general matrices (Cameron's method) allows prescribed zeros and group-delay equalisation [6]; it is worked through and verified in Level 3b below.
- **Physical Q limits.** Conductor Q of a cavity scales with size/skin depth, $Q_c\sim(\text{size})/\delta_s$; dielectric Q is bounded by $1/\tan\delta$ weighted by the filling factor. FR-4 at 2.45 GHz ($\tan\delta\approx0.02$) caps microstrip Q near 50 regardless of copper; low-loss laminates reach 100–250; high-εr ceramic TEM resonators reach several hundred in tiny volume; dielectric resonators and waveguide cavities several thousand to >10 000 [4 ch. 6][3 ch. 1].
- **Acoustic filters.** A SAW device launches a surface wave with an interdigital transducer (IDT); the finger period equals the acoustic wavelength, $f_0=v/\lambda_{IDT}$ with $v\approx3000$–4000 m/s — so a 433 MHz IDT has a period of only ≈ 7–9 µm and a 2.5 GHz one ≈ 1.5 µm, which is why SAW tops out around 2.5–3 GHz. A BAW/FBAR is a thin piezoelectric film (e.g. AlN) resonating in thickness, $f\approx v/2t$; ladder or lattice networks of such resonators form the filter, with higher Q and better power handling [9][10]. Both have a strong temperature coefficient (a 433 MHz SAW at −45 ppm/°C shifts 1.2 MHz over 60 °C — comparable to its bandwidth), limited power (typ. ≤ +30 dBm), and are ESD-sensitive.

### Level 3b — synthesis from polynomials (Cameron), extracted poles, linear phase, SAW spurious, YIG
All numbers come from `tools/verify/s15_coupling_matrix.py`. Every synthesised matrix is checked against its polynomials, typically agreeing to 1e-14.

**(a) The filtering function.** For a lossless two-port with N resonators and $n_{fz}$ prescribed transmission zeros $\omega_k$ (normalised low-pass variable λ ≡ ω here), $S_{21}=P(s)/[\varepsilon E(s)]$ and $S_{11}=F(s)/[\varepsilon_RE(s)]$. The generalised Chebyshev function $C_N=F/P=\cosh\sum_k\cosh^{-1}x_k$, with $x_k=(\omega-1/\omega_k)/(1-\omega/\omega_k)$, is equiripple in the passband and has the prescribed zeros. Cameron's recursion builds F without any root-finding [6], [15]: start with $U_0=1$, $V_0=0$ and repeat
$$U_{n}=(\omega-\tfrac1{\omega_n})U_{n-1}+(\omega^2-1)\sqrt{1-\tfrac1{\omega_n^2}}\,V'_{n-1},\qquad V'_{n}=(\omega-\tfrac1{\omega_n})V'_{n-1}+\sqrt{1-\tfrac1{\omega_n^2}}\,U_{n-1},$$
with $1/\omega_n=0$ for zeros at infinity. Then F = U_N (monic), $P=\prod(\omega-\omega_k)$, and $\varepsilon=\frac{1}{\sqrt{10^{RL/10}-1}}\left|\frac{P(1)}{F(1)}\right|$.
- Convert to s = jω. Make P monic in s and multiply it by j when $N-n_{fz}$ is even; this keeps S11 and S21 orthogonal on the jω axis. Then $E$ follows from the Feldtkeller (energy) equation $EE^*=FF^*/\varepsilon_R^2+PP^*/\varepsilon^2$: take its N left-half-plane roots. Here $\varepsilon_R=1$ for $n_{fz}<N$.
- **Pitfall found while scripting:** converting P(ω) to P(s) leaves a factor of $(-j)^{n_{fz}}$. If P is not renormalised to monic before applying the j rule, every response with an *odd* number of finite zeros comes out wrong: it is non-unitary, and the matrix disagrees with the polynomials.
- Check A1: N = 4, 0.1 dB ripple (RL 16.43 dB) with zeros at ±2.05 gives RL 16.43 dB, ripple 0.100 dB, zeros at ±2.05, and $\big||S_{11}|^2+|S_{21}|^2-1\big|$ < 1e-14.

**(b) From polynomials to a coupling matrix.**
1. *Transversal (N+2) matrix* [16]. Form $y_{21}$ and $y_{22}$ from E + F: with $m_1$ and $n_1$ the alternating real/imaginary parts of the coefficients, N even gives $y_{21}=(P/\varepsilon)/m_1$ and $y_{22}=n_1/m_1$; N odd swaps $m_1$ and $n_1$. Take the residues $r_{21,k}$ and $r_{22,k}$ at the poles $j\lambda_k$. Then $M_{kk}=-\lambda_k$, $M_{Lk}=\sqrt{r_{22,k}}$ and $M_{Sk}=r_{21,k}/\sqrt{r_{22,k}}$. This is N parallel resonators, each coupled to both source and load. It reproduces the polynomials exactly but cannot be built.
2. *Similarity rotations.* $M\to RMR^T$ with a plane (Givens) rotation leaves the response unchanged. A sequence of such rotations annihilates entries until a buildable topology remains. **Folded form:** main line plus cross-couplings on the two anti-diagonals. Cameron gives the pivot table [16]; the script instead searches, for each element in turn, for a pivot that zeroes it without refilling earlier zeros, and confirms response invariance to 1e-15.
3. *The quadruplet* (check B1) needs 6 rotations: $M_{S1}=M_{4L}=0.9419$, $M_{12}=M_{34}=0.8049$, $M_{23}=0.7138$, **$M_{14}=-0.1252$**. Compare Example 6, which added $M_{14}=-0.12$ to the inline values without re-synthesis. It gets similar stopband rejection (−21.4 vs −20.9 dB at λ = 1.6) but its in-band RL degrades to 10.2 dB (0.43 dB ripple). **Synthesis restores the exact 16.4 dB / 0.1 dB passband.** Cross-couplings always need the main couplings re-synthesised.

**(c) Asymmetric zeros: a GNSS preselector with an Iridium null.** Take the passband 1559–1610 MHz (f₀ 1584.3 MHz, FBW 3.22 %). Iridium at 1616–1626 MHz maps to λ = 1.231–1.615, so put one zero at 1621 MHz (λ = 1.423) with N = 5 and RL 20 dB. The folded matrix has self-couplings (detuned resonators: M11 +0.03, M33 −0.56) and a single cross-coupling M24 = +0.337, because an asymmetric response needs the diagonal and both anti-diagonals (check C1).

| Q_u | mid-band IL | worst rejection over 1616–1626 MHz (re mid-band): with TZ | all-pole N = 5 | null depth at 1621 MHz |
|---|---|---|---|---|
| ∞ | 0.02 dB | 15.1 dB | 4.8 dB | ideal (> 100 dB) |
| 3000 | 0.28 dB | 15.3 dB | 5.0 dB | 50.8 dB |
| 1000 | 0.81 dB | 15.6 dB | 5.4 dB | 41.2 dB |
| 500 | 1.60 dB | 15.9 dB | 5.9 dB | 35.0 dB |

The zero buys ≈ 10 dB at the 1616 MHz edge, which is 0.4 % of f₀ from the passband edge. Finite Q fills the null (35 dB at Q_u = 500) and costs passband loss. To actually protect a GNSS receiver next to an Iridium transmitter you need more zeros, higher order and Q_u ≳ 1000 (ceramic or cavity), and in practice the LNA's own linearity counts too ([GNSS interference](../21-gnss/gnss-interference-jamming-spoofing.md), [co-site](co-site-interference-and-transmitter-intermod.md)).

**(d) Linear phase: real-axis zeros.** Transmission zeros on the *real* s axis ($s=\pm\sigma$, entered as $\omega_k=\pm j\sigma$) leave |S21| on the jω axis without nulls but equalise group delay. For N = 6 and RL 20 dB, the group-delay variation over |λ| ≤ 0.8 falls from **30.6 % to 11.0 %** of the mean with σ = 1.2. The cost is rejection: 33.7 dB instead of 42.7 dB at λ = 2. The folded matrix adds one cross-coupling, **M25 = +0.110, of the same sign as the main line**; opposite-sign cross-couplings make jω-axis zeros instead (check D1). Use it where delay flatness matters: wideband radar pulses, GNSS inter-signal bias, PSK data near the band edge.

**(e) Trisection.** N = 3 with one zero at λ = +2.5: the folded N = 3 matrix *is* a trisection (triplet), with $M_{13}=+0.443$ and detuned resonators (M22 −0.43). The zero lands at +2.500 (check E1). Cascaded trisections and quadruplets (CT/CQ) are how real filters place zeros individually.

**(f) Extracted poles.** Instead of cross-coupling, hang a resonator on a **non-resonating node** (NRN: a frequency-independent node, e.g. a line section, with susceptance $B_N$) at the filter input. At the resonator's own frequency it presents an infinite admittance and shorts the NRN, so the transmission zero sits exactly at that resonator's frequency, whatever $B_N$ and the other couplings are. In 5 random trials the null fell within 2e-4 of λ_z (check F1). This lets each zero be tuned independently and suits waveguide/cavity diplexers [17]. Synthesis "extracts" the pole from the polynomials first and then synthesises the remainder. Only the analysis is checked here.

**(g) SAW spurious responses.**
- *Triple-transit echo (TTE).* The signal reflected back and forth between the two IDTs arrives 2τ late, where τ = L/v is the transit time. This gives $H\propto e^{-j\omega\tau}(1+a\,e^{-j2\omega\tau})$: amplitude ripple of $20\log\frac{1+a}{1-a}$ dB p-p with period **1/(2τ)**, and group-delay ripple ≈ **4τa p-p** (check G1). For a 433 MHz SAW with 3.16 mm between IDT centres on ST-quartz (v ≈ 3158 m/s, τ = 1.0 µs) and a −30 dB TTE: 0.55 dB p-p ripple every 500 kHz (three ripples across a 1.6 MHz passband) and 127 ns p-p delay ripple. At −40 dB TTE: 0.17 dB and 40 ns.
- *Other spurs:* bulk-acoustic-wave spurs above the passband, direct electromagnetic feedthrough setting the far-out rejection floor, and the "flyback" mentioned in Practical notes. Cures are unidirectional or impedance-mismatched IDT designs, absorbers, and a cheap LC low-pass for far-out rejection [18].

**(h) YIG tunable filters.** A polished single-crystal YIG sphere resonates in uniform precession at **f = γμ₀H₀**, with γ = 28 GHz/T (2.8 MHz/Oe). The sphere's demagnetising field cancels from the resonance condition. 2/8/18 GHz need 71/286/643 mT. The sphere must be saturated (internal field > 0), so the lowest usable frequency is ≈ **γ·4πMs/3**: 1.66 GHz for pure YIG (4πMs ≈ 1780 G, the value in [magnetic materials](../02-electromagnetics/magnetic-materials-permeability.md)), and ≈ 0.56 GHz for Ga-doped YIG with 4πMs ≈ 600 G. This is a different limit from the circulator's below-resonance criterion f ≳ γ·4πMs in [circulators](circulators-isolators.md). The unloaded Q is ≈ f/(γΔH): ΔH = 0.5 Oe gives ≈ 7100 at 10 GHz and ≈ 2100 at 3 GHz. Coupling loops around 2–4 spheres make multi-octave tunable band-pass or band-stop filters. Their uses are spectrum-analyser preselectors and wideband ESM receivers; the costs are a heavy electromagnet, ms-scale tuning, and a low power threshold above which spin-wave effects limit the signal [19].

## Design equations & rules of thumb

| Quantity | Equation | Typical |
|---|---|---|
| BPF mid-band loss | $4.343\sum g_i/(\text{FBW}\,Q_u)$ dB | 3-pole 0.1 dB ($\sum g$ = 3.21), FBW 10 %, Q 60 → 2.3 dB |
| Coupling | $k_{i,i+1}=\text{FBW}/\sqrt{g_ig_{i+1}}$ | FBW 10 %, 3-pole: 0.092 |
| External Q | $Q_e=g_0g_1/\text{FBW}$ | 10.3 |
| Split-mode extraction | $k=(f_e^2-f_o^2)/(f_e^2+f_o^2)$ | EM sim of a coupled pair |
| Group-delay $Q_e$ | $Q_e=\omega_0\tau_{S11}(\omega_0)/4$ | singly loaded resonator |
| Richards | L ↔ short stub $Z=L$, C ↔ open stub $Y=C$, λ/8 at $f_c$ | response periodic in $4f_c$ |
| Stepped impedance | $\beta l=gZ_0/Z_h$ (L), $gZ_l/Z_0$ (C) | $Z_h$ 100–130 Ω, $Z_l$ 15–25 Ω |
| Coupled line | $Z_{0e,o}=Z_0[1\pm JZ_0+(JZ_0)^2]$ | end sections need the tightest gap |
| Microstrip Q (λ/2) | $Q=\beta/(2\alpha)$ | 47 FR-4 0.8 mm; 126 RO4350B 0.508 mm (2.45 GHz) |
| Helical resonator | $Q_u\approx50\,S_{[in]}\sqrt{f_{[MHz]}}$ | 1-inch can at 433 MHz ≈ 1000 [7] |
| Coax cavity (air, Cu) | $Q_c=\beta/2\alpha_c$, $\alpha_c=\frac{R_s(1/a+1/b)}{2\eta\ln(b/a)}$ | 433 MHz, b = 25 mm: ≈ 4400 |
| SAW/BAW TCF | SAW ≈ −45; TC-SAW −15…−25; FBAR −20…−30 ppm/°C | [9][10] |
| Cameron recursion | $U_n=(\omega-\frac1{\omega_n})U_{n-1}+(\omega^2-1)c_nV'_{n-1}$, $V'_n=(\omega-\frac1{\omega_n})V'_{n-1}+c_nU_{n-1}$, $c_n=\sqrt{1-\omega_n^{-2}}$ | F = U_N; ε from RL at ω = 1 |
| Feldtkeller | $EE^*=FF^*/\varepsilon_R^2+PP^*/\varepsilon^2$ | E from its LHP roots |
| Transversal | $M_{kk}=-\lambda_k$, $M_{Lk}=\sqrt{r_{22k}}$, $M_{Sk}=r_{21k}/\sqrt{r_{22k}}$ | then rotate to folded |
| Cross-coupling sign | opposite to main line → jω-axis zeros; same → real-axis (delay) zeros | CQ M14 < 0; linear-phase M25 > 0 |
| SAW TTE | period $1/(2\tau)$, ripple $20\log\frac{1+a}{1-a}$ p-p, delay ≈ 4τa p-p | −30 dB, 1 µs: 0.55 dB, 127 ns |
| YIG sphere | $f=\gamma\mu_0H_0$ (28 GHz/T); $f_{min}\approx\gamma\,4\pi M_s/3$; $Q\approx f/(\gamma\Delta H)$ | 1.66 GHz (pure YIG); Q ≈ 7000 at 10 GHz |

Choosing a technology (pick the cheapest that meets loss, selectivity, size, power and temperature):

| Need | Good choice |
|---|---|
| Harmonic low-pass after a PA (any band < 3 GHz) | LC chip (C0G + wire-wound L) or stepped-impedance microstrip |
| Wide (≥ 10 %) pre-selector at UHF | LC coupled resonators, LTCC or ceramic module |
| Narrow (≤ 1 %) receive filter 300 MHz–2.5 GHz | SAW (433/868/915 MHz, GNSS) |
| Narrow, 1.5–6 GHz, higher power / steeper | BAW/FBAR (Wi-Fi coexistence, cellular) |
| Ground-station 433 MHz, need < 1 dB loss and power handling | helical or coaxial cavity |
| Tunable / high-power | combline cavity with tuning screws |
| ≥ 5 GHz, prototype on a PCB | coupled-line / hairpin / interdigital on low-loss laminate |

## Worked examples

### Example 1 — 433 MHz band filter: which technology?
The 433.05–434.79 MHz ISM/SRD band (used for 433 MHz LoRa; national rules in [spectrum allocation](../19-regulations-safety/spectrum-allocation-ism-bands.md)) is 1.74 MHz wide → FBW = 0.4 %. For a 3-pole 0.1 dB response:
- chip LC, $Q_u$ = 60: $IL\approx4.343\times3.21/(0.004\times60)=58$ dB → impossible;
- helical, $Q_u$ ≈ 1000: 3.5 dB;
- coaxial cavity, $Q_u$ ≈ 4000: 0.9 dB;
- SAW: Raltron RSF-433.920-1600-3030, 1.6 MHz BW, 2.4 dB IL in 3 × 3 mm [11] — the practical answer for an on-board receiver.
For a ground station with an LNA, put the cavity (or nothing) before the LNA and the SAW after it (see [LNA design](lna-design.md#example-5--lora-ground-station-is-an-lna-worth-it-and-where)).

### Example 2 — 433 MHz 3-pole coupled-resonator LC pre-selector (FBW 10 %)
3-pole 0.1 dB Chebyshev: g = 1.0316, 1.1474, 1.0316. $k_{12}=k_{23}=0.1/\sqrt{1.0316\times1.1474}=0.0919$; $Q_e=1.0316/0.1=10.32$. Topology: three shunt LC resonators, coupled by series capacitors $C_c$, with series input/output capacitors $C_e$ from 50 Ω.
1. Pick $L$ = 22 nH → total node capacitance $C_t=1/(\omega_0^2L)=6.12$ pF.
2. $C_c=kC_t=0.56$ pF.
3. External coupling: $Q_e=\omega_0C_tR_p$ → required parallel resistance $R_p=619\ \Omega$; a series $C_e$ from 50 Ω transforms 50 Ω up to $R_p$ when $C_e=1/(\omega_0R_0\sqrt{R_p/R_0-1})=2.18$ pF, which also adds ≈ 1.43 pF of parallel capacitance.
4. Resonator capacitors: $C_1=C_3=C_t-C_{p,e}-C_c=3.55$ pF, $C_2=C_t-2C_c=4.99$ pF.
Result (ideal parts, script E): −3 dB band centred at 436.9 MHz (+0.7 %), 61.5 MHz wide, ≤ 0.2 dB ripple; with Q = 60 inductors: 2.3 dB mid-band loss. The 0.56 pF coupling capacitors are comparable to pad parasitics (0.1–0.2 pF) — choose a smaller L to raise them: with 8.2 nH, $C_t$ = 16.4 pF, $C_c$ = 1.51 pF, $C_e$ = 3.86 pF, $C_1=C_3$ = 11.9 pF, $C_2$ = 13.4 pF (same method). Always tune on the bench or in simulation with vendor part models.

### Example 3 — Stepped-impedance harmonic LPF for a 2.4 GHz transmitter
7-pole 0.1 dB Chebyshev, $f_c$ = 3 GHz, JLCPCB-style 0.8 mm FR-4 (εr 4.4, tanδ 0.02, 35 µm Cu): $Z_h$ = 110 Ω → W = 0.27 mm; $Z_l$ = 20 Ω → W = 5.56 mm; 50 Ω feed 1.53 mm. Section lengths (C-L-C-L-C-L-C): 3.89, 6.07, 6.91, 6.71, 6.91, 6.07, 3.89 mm (total 40.5 mm). scikit-rf `MLine` (Hammerstad–Jensen + Kirschning–Jansen dispersion, losses): |S21| = −0.75 dB at 2.45 GHz (−0.18 dB lossless; FR-4 costs 0.57 dB), −3 dB at 3.06 GHz, −34.6 dB at 4.9 GHz, −41.2 dB at 7.35 GHz; stopband ≥ 24 dB from 5 to 9 GHz. The lumped prototype would give −42.9 dB at 4.9 GHz — the difference is the stepped-impedance approximation. Step-discontinuity models and a final EM check (openEMS) would shift the lengths by a few percent. The 5.56 mm-wide low-Z sections are ≈ 0.1 λg at 3 GHz; do not make them wider than ≈ λg/8 or transverse resonances appear.

### Example 4 — Parallel-coupled-line BPF at 2.45 GHz
3-pole 0.5 dB Chebyshev (g = 1.5963, 1.0967, 1.5963), FBW 6 % (≈ 2.38–2.52 GHz):

| Section | $JZ_0$ | $Z_{0e}$ | $Z_{0o}$ | W (mm) | S (mm) | ε_e even/odd | λ/4 (mm) |
|---|---|---|---|---|---|---|---|
| 1, 4 | 0.2430 | 65.10 | 40.80 | 1.34 | 0.33 | 3.55/2.89 | 17.06 |
| 2, 3 | 0.0712 | 53.82 | 46.69 | 1.52 | 1.67 | 3.49/3.14 | 16.80 |

(0.8 mm FR-4; widths/gaps from Garg–Bahl formulas [8], which agree with an independent 2-D finite-difference Laplace solution within 3.7 % — the FD solver itself agrees with Hammerstad–Jensen within 1.1 %.) Ideal TEM response: 0.50 dB ripple, −34 dB at 2.2 and 2.7 GHz, perfect null at 4.9 GHz; with microstrip's unequal mode velocities the 2f₀ response rises to −5.8 dB. Loss: $Q_u$ of the lines ≈ 47 on FR-4 → Cohn estimate 6.6 dB; on RO4350B ($Q_u$ ≈ 126) 2.5 dB. **Lesson: for a narrow microstrip filter above ~1 GHz use a low-loss laminate or buy a ceramic/SAW/BAW part.** A hairpin filter folds the same half-wave coupled resonators into U shapes to save area; an interdigital filter uses λ/4 lines grounded at alternate ends (compact, wide stopband to ≈ 3f₀); a combline uses λ/8 lines loaded by capacitors (short, easily tuned) [3][2].

### Example 5 — Front-end SAW for GNSS
A GNSS SAW such as Murata SAFFB1G56KB0F0A (1561–1602 MHz, ≤ 2.0 dB, 50 Ω) [12] placed *after* the first LNA costs only $(10^{0.2}-1)/G_{LNA}$ in noise factor: with a 19.6 dB LNA (BGA524N6), 0.006 → +0.02 dB. Placed *before* the LNA it adds its full ≈ 1.5–2 dB to NF but protects against a nearby 433/915 MHz transmitter. u-blox asks for ≈ 40 dB out-of-band rejection in the active antenna [13].

### Example 6 — Cross-coupled quadruplet (coupling-matrix demo)
Start from a 4-pole 0.1 dB inline matrix ($M_{12}=M_{34}=1/\sqrt{g_1g_2}$, …). Add $M_{14}=-0.12$: two transmission zeros appear at λ ≈ ±2.05 and the rejection at λ = ±1.6 improves from −14.2 to −21.4 dB (script G). Physically: in a square of four resonators, couple 1 and 4 with the opposite type of coupling (e.g. a capacitive probe where the others are inductive irises). Re-optimise the other couplings to restore the passband ripple. Exact synthesis (Level 3b b) gives $M_{14}=-0.125$ with re-synthesised main couplings, and restores RL from 10.2 to 16.4 dB.

### Example 7 — Specifying a GNSS preselector that also notches Iridium
Spec: pass 1559–1610 MHz (FBW 3.22 %) with RL ≥ 20 dB, and maximise rejection at Iridium 1616–1626 MHz.
- An all-pole N = 5 gives only 4.8 dB at 1616 MHz: the band edges are only 6 MHz (0.4 %) apart.
- One zero at 1621 MHz (λ = 1.423) raises this to 15.1 dB. The folded matrix: $M_{S1}=M_{5L}=1.011$; main line 0.861/0.538/0.538/0.861; $M_{24}=0.337$; self-couplings 0.03/0.04/−0.56/0.04/0.03. Realise it as a folded ceramic or cavity filter with one cross-coupling between resonators 2 and 4.
- The finite Q of a ceramic monoblock (Q_u ≈ 500) costs 1.6 dB in band and fills the null to 35 dB (Level 3b c).

Conclusion: for a GNSS antenna near an Iridium modem, use a vendor GNSS/Iridium-rejecting SAW or BAW, more poles and zeros, and good LNA linearity. One printed zero is not enough.

## Practical notes
- **Component choice for LC filters:** C0G/NP0 capacitors (stable, high Q); wire-wound or air-core inductors; place inductors at right angles to reduce mutual coupling; ground each shunt element with its own via(s). Model pads (≈ 0.1–0.2 pF) and via inductance (≈ 0.5–1 nH) — they matter for sub-pF couplings.
- **PCB material:** JLCPCB standard FR-4 is fine for harmonic LPFs and wide filters at ≤ 1 GHz; for narrow filters above ~1 GHz, the FR-4 loss tangent dominates. Check the fab's stated εr/tanδ at your frequency (see [stackups](../13-pcb-rf-layout-emc/stackups-and-materials.md)).
- **Tuning:** every printed filter needs a tuning allowance: design with EM simulation, build, measure with a NanoVNA/LibreVNA, and adjust lengths (or use trimmer caps/tuning screws for LC/cavity).
- **SAW/BAW usage:** follow the vendor matching (many SAWs are not 50 Ω internally and need a series L/shunt C match); respect the maximum input power; watch the stopband "flyback" far from the passband (some SAWs have poor rejection at several GHz, so add a cheap LPF if harmonics or far-out blockers matter); ESD-protect the antenna port.
- **Cavity filters for ground stations:** commercial 433 MHz cavity band-pass filters give < 1 dB loss and tens of watts handling; helical filters (e.g. Toko/Temwell-style cans) are smaller and cheaper with a few dB loss.
- **Group delay:** narrow filters add delay (≈ $N/(\pi\,\text{BW})$ order of magnitude) and delay ripple at the band edges — relevant for GNSS inter-signal delay budgets and wideband radar pulses.
- **Other distributed PCB structures** (stubs, spurlines, radial stubs, pads) and where each is covered: [03 stubs § zoo](../03-transmission-lines-matching/input-impedance-stubs-quarter-wave.md#a-zoo-of-distributed-pcb-structures-where-each-is-covered); classic image-parameter (constant-k, m-derived) filters: [01 passive filters § Level 3b](../01-circuit-theory/passive-filter-design-prototypes.md#level-3b--image-parameter-filters-constant-k-and-m-derived).

## Common mistakes & misconceptions
- *"Higher order = better."* More sections add loss ($\propto\sum g_i$) and group delay; use the lowest order meeting the rejection mask, or add transmission zeros instead.
- *"A 1 dB-loss filter costs 1 dB of sensitivity no matter where it is."* Only if it is before the LNA; after a high-gain LNA its effect on NF is tiny.
- *"The microstrip filter will have the textbook stopband."* Unequal even/odd velocities, radiation, and box modes create spurious responses; stepped-impedance filters are shallower than lumped prototypes.
- *"I can make a very narrow filter on FR-4 if I just add sections."* Loss explodes as 1/(FBW·Q).
- *"SAW filters are 50 Ω and flat to 6 GHz."* Check the matching network and the far-out rejection in the data sheet.
- *"Kuroda identities change the response."* They are exact identities in the Richards domain; they only change the realisation.
- *"Add a cross-coupling to an inline design and keep the other couplings."* The zeros appear but the passband degrades: in the Example 6 case RL falls from 16.4 to 10.2 dB. Re-synthesise the whole matrix (Level 3b b).
- *"Any cross-coupling makes a notch."* Only one of *opposite* sign to the main-line path puts zeros on the jω axis. A same-sign cross-coupling gives real-axis zeros, which flatten group delay but reduce selectivity.
- *"A transmission zero gives infinite rejection."* Only with lossless resonators: Q_u = 500 limits the null to ≈ 35 dB in the GNSS example.
- *"SAW passband ripple means a bad part."* A ripple with period 1/(2τ) is the triple-transit echo, a design trade (TTE level vs insertion loss). Check it against your group-delay budget.
- *"YIG filters work at any frequency."* The sphere must be saturated, so pure YIG stops near γ·4πMs/3 ≈ 1.7 GHz; doped YIG goes lower.
- *"Coupling coefficient is the gap."* $k$ depends on the resonator field distribution; extract it (split-mode method) rather than guessing.

## How to simulate / verify
- `tools/verify/rfckt_filters.py` (≈ 8 min, dominated by the FD solver): Kuroda identity and Richards mapping, a quasi-static 2-D finite-difference Laplace solver for (coupled) microstrip validated against Hammerstad–Jensen and used to check Garg–Bahl, the stepped-impedance LPF in scikit-rf `MLine`, the coupled-line BPF (ideal TEM and inhomogeneous), coupled-resonator LC BPF with split-mode $k$ and group-delay $Q_e$ extraction, Cohn's loss formula, coupling-matrix responses (inline and CQ), resonator Q of several technologies.
- `tools/verify/s15_coupling_matrix.py` (W5-S15, ≈ 3 s): Cameron recursion and Feldtkeller E(s), transversal matrix from residues, folding by Givens rotations (response invariance), quadruplet vs Example 6, asymmetric GNSS/Iridium N = 5 with Q_u sweep, linear-phase N = 6, trisection, extracted pole on an NRN, SAW TTE ripple, YIG numbers. ALL PASS.
- Lumped prototypes and the 433/915 MHz LC examples: `tools/verify/circuits_filter_prototypes.py` (domain 01).
- For layout-level accuracy: openEMS/Sonnet EM simulation of the printed structure including discontinuities, then VNA measurement. See [openEMS workflow](../16-simulation-tools/openems-workflow.md).

## Open questions / gaps
- The helical-resonator Q formula is the empirical Macalpine–Schildknecht/Zverev result; not re-derived and not checked against a measured part.
- Coaxial-cavity Q is conductor-loss-only (ends, shorting plate and tuning screws reduce it, often by 20–40 %) — no measured 433 MHz cavity data gathered.
- Folding in `s15_coupling_matrix.py` uses a pivot *search*, not Cameron's closed-form rotation table. Fully canonical cases (n_fz = N, ε_R ≠ 1, M_SL ≠ 0) and the extraction step of extracted-pole *synthesis* are not implemented (only analysed).
- The YIG figures (ΔH, 4πMs of doped garnets) and the SAW velocity are typical literature values, not taken from a specific part.
- Tapped-line external-Q formulas for hairpin/interdigital filters are not given; extraction by simulation is recommended instead.
- Vendor SAW data used here are from distributor summaries (Raltron) and the Murata data sheet; a table of JLCPCB-stocked SAW/BAW parts belongs in [filter parts](../18-components-parts/filter-parts-saw-ceramic-ltcc.md).

## Sources
1. S. B. Cohn, "Dissipation loss in multiple-coupled-resonator filters," *Proc. IRE*, 47(8), pp. 1342–1348, Aug. 1959. (peer-reviewed; loss formula, reproduced numerically)
2. G. L. Matthaei, L. Young, E. M. T. Jones, *Microwave Filters, Impedance-Matching Networks, and Coupling Structures*, Artech House, 1980 — ch. 4 (prototypes, loss), ch. 8–10 (coupled-line, interdigital, combline). (textbook)
3. J.-S. Hong, M. J. Lancaster, *Microstrip Filters for RF/Microwave Applications*, Wiley, 2001 (2nd ed. 2011) — ch. 5 (lowpass/bandpass microstrip), ch. 7 (coupling-coefficient and Qe extraction), ch. 8–9 (coupled-resonator design, cross-coupled filters). (textbook)
4. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — §8.4 (Richards, Kuroda Table 8.7), §8.6 (stepped impedance), §8.8 (coupled-line BPF), ch. 6 (resonators, cavity Q). (textbook)
5. S. B. Cohn, "Parallel-coupled transmission-line-resonator filters," *IRE Trans. MTT*, 6(2), pp. 223–231, Apr. 1958. (peer-reviewed)
6. R. J. Cameron, C. M. Kudsia, R. R. Mansour, *Microwave Filters for Communication Systems*, Wiley, 2007 (2nd ed. 2018) — coupling-matrix synthesis and analysis. (textbook)
7. W. W. Macalpine, R. O. Schildknecht, "Coaxial resonators with helical inner conductor," *Proc. IRE*, 47(12), pp. 2099–2105, 1959; A. I. Zverev, *Handbook of Filter Synthesis*, Wiley, 1967 (helical-filter design curves, $Q\approx50S\sqrt f$). (peer-reviewed / textbook; empirical formula quoted)
8. R. Garg, I. J. Bahl, "Characteristics of coupled microstriplines," *IEEE Trans. MTT*, 27(7), pp. 700–705, July 1979 (even/odd capacitance model implemented and FD-checked here). (peer-reviewed)
9. Qorvo design hub, "BAW vs. SAW RF filters" (Q 1000–1500 vs 2500–5000, SAW ≲ 2.5 GHz, power handling), https://www.qorvo.com/design-hub/blog/baw-vs-saw-rf-filters ; EDN, "The difference between BAW and SAW filters" (TCF values). (app note / trade press)
10. R. Ruby, "Review and comparison of bulk acoustic wave FBAR, SMR technology," *Proc. IEEE Ultrasonics Symposium*, 2007. (peer-reviewed; background for BAW physics)
11. Raltron RSF-433.920-1600-3030-TR-NS2 SAW filter: 433.92 MHz, 2.4 dB, 1.6 MHz, 3 × 3 mm (DigiKey product data). (datasheet summary)
12. Murata SAFFB1G56KB0F0A GNSS SAW filter data sheet (1561.1/1575.42/1602 MHz, IL ≤ 2.0 dB, 50 Ω); LCSC C91647. (datasheet)
13. u-blox ZED-F9P Integration Manual UBX-18010802 R16, Table 39. (manufacturer manual)
14. E. Hammerstad, Ø. Jensen, "Accurate models for microstrip computer-aided design," *IEEE MTT-S Digest*, 1980; M. Kirschning, R. H. Jansen, "Accurate model for effective dielectric constant of microstrip with validity up to millimetre-wave frequencies," *Electron. Lett.*, 18, 1982 (models used via scikit-rf MLine). (peer-reviewed)
15. R. J. Cameron, "General coupling matrix synthesis methods for Chebyshev filtering functions," *IEEE Trans. MTT*, 47(4), pp. 433–442, Apr. 1999 (recursion for F/P, N×N coupling-matrix synthesis and folding). (peer-reviewed; bibliographic details verified via citing records)
16. R. J. Cameron, "Advanced coupling matrix synthesis techniques for microwave filters," *IEEE Trans. MTT*, 51(1), pp. 1–10, Jan. 2003 (N+2 transversal matrix, folded/arrow forms, fully canonical case). (peer-reviewed)
17. J. D. Rhodes, R. J. Cameron, "General extracted pole synthesis technique with applications to low-loss TE011 mode filters," *IEEE Trans. MTT*, MTT-28(9), Sept. 1980 (page numbers not confirmed). (peer-reviewed; cited)
18. D. Morgan, *Surface Acoustic Wave Devices*, 2nd ed., Elsevier/Academic Press, 2007 — triple-transit echo, bulk-wave and feedthrough spurious responses. (textbook; cited, not re-read)
19. P. S. Carter, "Magnetically-tunable microwave filters using single-crystal yttrium-iron-garnet resonators," *IRE Trans. MTT*, 9(3), pp. 252–260, May 1961; J. Helszajn, *YIG Resonators and Filters*, Wiley, 1985. (peer-reviewed / textbook; cited, not re-read)
20. `tools/verify/s15_coupling_matrix.py` (this KB; W5-S15).
