---
title: Transformers and coupled inductors
domain: 01-circuit-theory
slug: transformers-coupled-inductors
tags: [transformer, coupled-inductors, mutual-inductance, coupling-coefficient, leakage-inductance, magnetising-inductance, impedance-transformation, autotransformer, tapped-inductor, capacitive-divider, coupled-resonators, dot-convention]
prerequisites:
  - lumped-elements-impedance-admittance.md
  - resonance-and-q.md
  - two-port-networks-zyh-abcd.md
related:
  - passive-filter-design-prototypes.md
  - ../06-rf-circuits/baluns-and-rf-transformers.md
  - ../04-real-components-hf/ferrites-and-beads.md
  - ../04-real-components-hf/inductors-at-rf.md
  - ../02-electromagnetics/magnetic-materials-permeability.md
  - ../02-electromagnetics/inductance-capacitance-from-fields.md
  - ../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md
  - ../05-analog-electronics/oscillators.md
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Transformers and coupled inductors

## Questions this page answers
- What is mutual inductance, and what does the coupling coefficient k mean?
- How does an ideal transformer transform impedance (and why by the turns ratio squared)?
- What are leakage and magnetising inductance, and how do they limit a real transformer's bandwidth?
- How do I model two coupled inductors in a circuit simulator?
- How does a tapped inductor or a capacitive divider act as an impedance transformer in a tank?
- How do I measure k from the frequency splitting of two coupled resonators?
- Why does a transmission-line (Guanella/Ruthroff) transformer work at much higher frequencies than a conventional one?
- Why is |k| always ≤ 1?

## TL;DR
- Coupled inductors: $V_1=j\omega L_1I_1+j\omega MI_2$, $V_2=j\omega MI_1+j\omega L_2I_2$, with $M=k\sqrt{L_1L_2}$, $|k|\le1$ (energy must be non-negative).
- **Ideal transformer** ($k=1$, $L\to\infty$, lossless), turns $N_1{:}N_2=n{:}1$: $V_1=nV_2$, $I_1=-I_2/n$, $Z_{in}=n^2Z_L$. Impedance scales with the **square** of the turns ratio.
- **Real transformer = leakage + magnetising + ideal core** ("cantilever" model): leakage $L_1(1-k^2)$ in series, magnetising $k^2L_1$ in shunt, ideal ratio $n_{eff}=k\sqrt{L_1/L_2}$. Exact at every frequency (script-verified). The same network also has an exact **T-equivalent** $(L_1-M,\ M,\ L_2-M)$.
- Bandwidth: low-frequency −3 dB edge ≈ $(R_s\parallel R_L')/(2\pi L_m)$; high-frequency edge ≈ $(R_s+R_L')/(2\pi L_{leak})$ — plus winding capacitance and core loss in real parts. Example 1:4 (50 → 200 Ω), $L_1=2\ \mu$H, k = 0.995: 2.0 MHz to 790 MHz computed vs 2.0 MHz / 798 MHz estimated.
- **Tank taps as transformers**: a tightly coupled tap at fraction $t$ of the turns makes a load $R$ look like $R/t^2$; a capacitive divider (C1 top, C2 bottom, R across C2) makes it look like $\approx R(1+C_2/C_1)^2$, accurate when $\omega C_2R\gg1$ (11 % error at $\omega C_2R=2.7$).
- **Coupled resonators** split into two modes; $k=(f_h^2-f_l^2)/(f_h^2+f_l^2)$ — the standard way to measure inter-resonator coupling for filter design.
- At RF, conventional wound transformers are limited by leakage and winding capacitance; **transmission-line transformers** absorb these parasitics into a line and reach GHz ([baluns and RF transformers](../06-rf-circuits/baluns-and-rf-transformers.md)).

## Intuition (no math)
Current in one coil creates magnetic flux; if some of that flux threads a second coil, changing the current in the first induces a voltage in the second. **Mutual inductance** $M$ measures how much. The **coupling coefficient** $k$ is the fraction of "shared" flux: $k=1$ means every line of flux from one coil links the other (an ideal iron- or ferrite-cored transformer); $k\approx0.01$–$0.1$ is typical for two air-core coils or chip inductors near each other.

In an ideal transformer each turn of either winding sees the same volts-per-turn, so voltage scales with turns; power in = power out, so current scales inversely. An impedance is voltage over current, so it scales with the turns ratio *squared*. A 1:2 turns transformer turns 50 Ω into 200 Ω.

Real transformers leak: some flux from the primary misses the secondary. That un-shared flux behaves like a small inductor in series with the winding — the **leakage inductance** — which blocks high frequencies. And the core needs magnetising current to set up the flux at all; that current flows in the **magnetising inductance**, which appears in parallel and shorts out low frequencies. The useful band sits between the two.

## The math

### Level 1 — coupled inductor equations and the ideal transformer

With dotted terminals and currents into the dots:
$$\begin{bmatrix}V_1\\V_2\end{bmatrix}=j\omega\begin{bmatrix}L_1&M\\M&L_2\end{bmatrix}\begin{bmatrix}I_1\\I_2\end{bmatrix},\qquad M=k\sqrt{L_1L_2}.$$
This is just a Z-matrix ([two-ports](two-port-networks-zyh-abcd.md)). With a load $Z_L$ on port 2 ($V_2=-I_2Z_L$):
$$Z_{in}=j\omega L_1+\frac{\omega^2M^2}{j\omega L_2+Z_L}.$$
**Ideal limit.** Let $k\to1$ and $L_1,L_2\to\infty$ with $L_1/L_2=n^2$ fixed. Then $Z_{in}\to n^2Z_L$. The script shows convergence (50 Ω target from 200 Ω and $n=1/2$): $k=0.9$, $L_1=1\ \mu$H gives $24.8+j31.7\ \Omega$; $k=0.99999$, $L_1=1$ mH gives $49.999+j1.3\ \Omega$.

For inductances on a common core, $L\propto N^2$ (for the same magnetic path), so $n=N_1/N_2=\sqrt{L_1/L_2}$.

### Level 2 — equivalent circuits

**T-equivalent** (shared ground between windings): series $L_1-M$ on port 1, series $L_2-M$ on port 2, shunt $M$ in the middle. It reproduces the Z-matrix exactly; one leg can be a *negative* inductance when $L_1$ and $L_2$ differ a lot — fine for analysis, not a physical part.

**Cantilever (leakage–magnetising) model**, referred to the primary:
$$L_{leak}=L_1(1-k^2)\ \text{(series)},\qquad L_m=k^2L_1\ \text{(shunt)},\qquad n_{eff}=k\sqrt{L_1/L_2}\ \text{(ideal transformer)}.$$
This is also exact (all three models agree to machine precision in `tools/verify/circuits_transformers.py`) and makes the bandwidth limits obvious. Note $n_{eff}$ differs from the turns ratio by the factor $k$.

**Bandwidth of a wideband transformer.** Source $R_s$, load reflected to the primary $R_L'=n^2R_L$:
- Low end: $L_m$ shunts the reflected load. −3 dB when $X_{L_m}=R_s\parallel R_L'$: $f_L\approx\dfrac{R_s\parallel R_L'}{2\pi L_m}$.
- High end: $L_{leak}$ in series with $R_s+R_L'$: $f_H\approx\dfrac{R_s+R_L'}{2\pi L_{leak}}$.
Ratio $f_H/f_L\approx\dfrac{(R_s+R_L')^2}{R_sR_L'}\cdot\dfrac{k^2}{1-k^2}$ — a 1:1-matched transformer with $k=0.995$ spans ≈ 400:1. Winding self-capacitance, core permeability roll-off ($\mu'$ falling, $\mu''$ rising with frequency) and core loss further limit the top end ([magnetic materials](../02-electromagnetics/magnetic-materials-permeability.md), [ferrites](../04-real-components-hf/ferrites-and-beads.md)).

### Level 3 — taps, dividers, coupled resonators and limits

**Tapped inductor (autotransformer).** A coil of total inductance $L$ tapped at a fraction $t$ of its turns from ground, load $R$ from tap to ground. For $k=1$ the input admittance is exactly $\dfrac{t^2}{R}+\dfrac{1}{j\omega L}$: the tank sees $R/t^2$ in parallel with the full coil. For looser coupling the transformation is weaker (script §5: 20 % tap, 50 Ω load → 1251 Ω at $k=0.999$, 1552 Ω at 0.8, 2453 Ω at 0.5, vs 1250 Ω ideal). Air-wound coils have $k\approx0.5$–0.8 between sections, so tap positions are usually tuned empirically.

**Capacitive divider.** C1 from the tank top to the tap, C2 from tap to ground, load $R$ across C2. Converting $R\parallel C_2$ to series form and back:
$$R_p\approx R\left(1+\frac{C_2}{C_1}\right)^2,\qquad C_{eq}\approx\frac{C_1C_2}{C_1+C_2},\qquad\text{valid for }Q_2=\omega C_2R\gg1.$$
At 433.92 MHz with $C_1=2$ pF, $C_2=20$ pF, $R=50\ \Omega$ ($Q_2=2.73$): exact $R_p=6.72$ kΩ vs 6.05 kΩ approximate. The divider is a Colpitts oscillator's feedback network and the coupling method of many narrowband tank filters; unlike a tap it needs no magnetic coupling and costs only capacitors.

**Coupled resonators.** Two identical LC resonators with mutual inductance $M=kL$ have even and odd modes at $f_{e,o}=\dfrac{1}{2\pi\sqrt{(L\pm M)C}}$, hence
$$k=\frac{f_o^2-f_e^2}{f_o^2+f_e^2}$$
(script §6 recovers k = 0.01/0.05/0.1 exactly: e.g. 22 nH/433.92 MHz tanks with k = 0.05 split to 423.5 and 445.2 MHz). For capacitive or mixed coupling the same formula gives the net coupling. Band-pass filter synthesis specifies the required $k_{i,i+1}=\mathrm{FBW}/\sqrt{g_ig_{i+1}}$ ([filter prototypes](passive-filter-design-prototypes.md)); you set the spacing or coupling capacitor until the measured split matches.

**Why $|k|\le1$.** Stored magnetic energy $W=\tfrac12L_1I_1^2+MI_1I_2+\tfrac12L_2I_2^2$ must be ≥ 0 for all currents; that quadratic form is positive semi-definite iff $M^2\le L_1L_2$.

**Transmission-line transformers.** Winding the two conductors as a transmission line (twisted pair or coax on a ferrite core) makes the inter-winding capacitance and leakage inductance part of a line of characteristic impedance $Z_0$; energy is transferred by the line mode rather than by core flux, so the high-frequency limit is set by line length (≲ λ/8) rather than leakage. The ferrite only has to suppress the common-mode current. Guanella (equal-delay) and Ruthroff (bootstrap) 1:4 designs are the classic examples; see [baluns and RF transformers](../06-rf-circuits/baluns-and-rf-transformers.md).

## Design equations & rules of thumb

| Quantity | Equation | Notes |
|---|---|---|
| Mutual inductance | $M=k\sqrt{L_1L_2}$ | $|k|\le1$ |
| Ideal impedance ratio | $Z_{in}=(N_1/N_2)^2Z_L$ | common core, $k\to1$ |
| Leakage (primary-referred) | $L_1(1-k^2)$ | k = 0.99 → 2 % of $L_1$ |
| Magnetising | $k^2L_1$ | — |
| Effective ratio | $n_{eff}=k\sqrt{L_1/L_2}$ | — |
| Low cutoff | $f_L\approx(R_s\parallel R_L')/(2\pi L_m)$ | choose $X_{L_m}\ge5\times$ this at $f_{min}$ for flatness |
| High cutoff | $f_H\approx(R_s+R_L')/(2\pi L_{leak})$ | minus winding C effects |
| Tap transformation | $R/t^2$ | tight coupling |
| Capacitive divider | $R(1+C_2/C_1)^2$ | $\omega C_2R\gg1$ |
| Coupling from split | $k=(f_h^2-f_l^2)/(f_h^2+f_l^2)$ | identical resonators |

## Worked examples

### 1. A 1:4 impedance (1:2 turns) wideband transformer, 50 → 200 Ω
$L_1=2\ \mu$H, $L_2=8\ \mu$H, $k=0.995$ → $L_m=1.98\ \mu$H, $L_{leak}=19.95$ nH, reflected load $200/4=50\ \Omega$. Estimates: $f_L=25/(2\pi\cdot1.98\ \mu\text{H})=2.01$ MHz; $f_H=100/(2\pi\cdot19.95\text{ nH})=798$ MHz. The exact coupled-inductor computation gives a −3 dB band of 2.009 MHz – 790.7 MHz. Real ferrite-cored parts reach this only if the core is still magnetic at the top frequency — a type 43 core's permeability falls above tens of MHz ([ferrites](../04-real-components-hf/ferrites-and-beads.md)).

### 2. Loading a 433.92 MHz tank with a 50 Ω LNA through a capacitive tap
Tank: 22 nH. To keep $Q_L\approx20$ with $Q_u=45$, the external loading must be $Q_e=1/(1/20-1/45)=36$, i.e. $R_e=Q_eX_0=36\cdot60=2.16$ kΩ. With $R=50\ \Omega$, need $(1+C_2/C_1)^2\approx43$ → $C_2/C_1\approx5.6$. Series combination must equal the tank capacitance 6.12 pF: $C_1\approx7.2$ pF, $C_2\approx40$ pF. Check $Q_2=\omega C_2R=5.5$ — acceptable (≈3 % error); fine-tune in simulation.

### 3. Measuring coupling of two 915 MHz resonators
Weakly probe two coupled tanks with a VNA and read the two peaks at 890 and 942 MHz: $k=(942^2-890^2)/(942^2+890^2)=0.0567$. A 3-pole 0.1 dB Chebyshev with FBW 10 % needs $k_{12}=0.1/\sqrt{1.0316\cdot1.1474}=0.0919$ — move the resonators closer or increase the coupling capacitor.

## Practical notes
- **Chip "transformers" and baluns** (Mini-Circuits, Johanson, Murata LTCC) specify insertion loss, amplitude/phase balance and return loss over a band; they are small transmission-line or LTCC structures, not wound cores. For LoRa/ISM, a 1:1 or 1:4 LTCC balun is typical where a transceiver has a differential RF port ([baluns](../06-rf-circuits/baluns-and-rf-transformers.md)).
- **Unintended coupling** between adjacent chip inductors (k ≈ 0.01–0.05 at 1 mm spacing, depending on orientation) detunes filters and matching networks. Place them at right angles or add spacing/ground between them; include coupling in EM simulation if critical.
- **Measure k of a wound transformer** by measuring $L_{1}$ with the secondary open ($L_{1,oc}=L_1$) and shorted ($L_{1,sc}\approx L_1(1-k^2)$): $k=\sqrt{1-L_{1,sc}/L_{1,oc}}$.
- **Current-mode coupling** in common-mode chokes is the same physics with $k\approx1$ and the windings connected so that differential currents cancel their flux ([ferrites and beads](../04-real-components-hf/ferrites-and-beads.md)).

## Common mistakes & misconceptions
- **"Impedance ratio = turns ratio."** It is the turns ratio *squared*.
- **"k = 1 means ideal."** It also requires infinite magnetising inductance (or at least $X_{L_m}\gg$ circuit impedances) and no loss.
- **Ignoring the dots.** Reversing one winding flips the sign of $M$; in the T-model that swaps $L-M$ for $L+M$ and changes the answer completely.
- **Using the turns ratio directly with loose coupling.** For $k<1$ the effective ratio is $k\sqrt{L_1/L_2}$ and there is series leakage to account for.
- **Assuming capacitive taps are frequency-independent.** The divider ratio holds only for $\omega C_2R\gg1$; at low Q the transformed resistance and the effective tank capacitance both shift.
- **Expecting a ferrite-core transformer to work at any frequency.** Above the material's ferromagnetic resonance the core becomes lossy and non-magnetic; the device then behaves like an air-core transformer with low $L_m$.

## How to simulate / verify
- `python3 tools/verify/circuits_transformers.py` — verifies the equivalence of the coupled, T and cantilever models, the ideal-transformer limit, the wideband-transformer band edges, the capacitive-divider and tap transformations, and the coupled-resonator k formula.
- SPICE: two inductors plus a `K1 L1 L2 0.995` coupling statement; `.ac` sweep; watch the dot convention (the first node of each inductor is the dotted end).
- scikit-rf: build the Z-matrix $j\omega[[L_1,M],[M,L_2]]$ directly with `rf.Network(frequency=f, z=Z)`.
- EM: openEMS/Sonnet to extract k between adjacent chip inductors or PCB spirals ([EM solvers](../16-simulation-tools/em-solvers-fdtd-mom-fem.md)).

## Open questions / gaps
- Quantitative coupling coefficients between common 0402/0603 chip inductors versus spacing and orientation are not tabulated here; would need EM simulation or measurement (flagged for 13-pcb-rf-layout-emc).

## Sources
1. J. B. Hagen, *Radio-Frequency Electronics*, 2nd ed., Cambridge UP, 2009 — ch. 4 (transformers, coupled circuits, taps and capacitive dividers). (textbook)
2. C. Bowick, *RF Circuit Design*, 2nd ed., Newnes, 2008 — ch. 2–3 (tapped-C and tapped-L impedance transformation in tanks). (textbook)
3. J. Sevick, *Transmission Line Transformers*, 4th ed., Noble/SciTech, 2001 — Guanella and Ruthroff transformers, bandwidth limits. (textbook)
4. G. Guanella, "Novel matching systems for high frequencies," *Brown-Boveri Review*, 31, 327–329, 1944; C. L. Ruthroff, "Some broad-band transformers," *Proc. IRE*, 47(8), 1337–1342, 1959. (peer-reviewed/historical)
5. J.-S. Hong, M. J. Lancaster, *Microstrip Filters for RF/Microwave Applications*, 2nd ed., Wiley, 2011 — §8.1 coupling-coefficient extraction from mode splitting. (textbook)
6. C. R. Paul, *Inductance: Loop and Partial*, Wiley-IEEE, 2010 — mutual inductance, energy argument for $|k|\le1$. (textbook)
7. Verification script `tools/verify/circuits_transformers.py` (this KB).
