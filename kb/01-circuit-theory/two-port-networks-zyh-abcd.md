---
title: Two-port networks — Z, Y, h, ABCD and T parameters
domain: 01-circuit-theory
slug: two-port-networks-zyh-abcd
tags: [two-port, z-parameters, y-parameters, h-parameters, abcd, chain-matrix, transmission-matrix, t-parameters, cascade, reciprocity, symmetry, lossless, image-impedance, attenuator]
prerequisites:
  - lumped-elements-impedance-admittance.md
  - network-theorems-max-power-transfer.md
  - ../00-math-foundations/matrices-and-linear-algebra-for-networks.md
related:
  - ../03-transmission-lines-matching/s-parameters.md
  - ../03-transmission-lines-matching/signal-flow-graphs-mason.md
  - passive-filter-design-prototypes.md
  - transformers-coupled-inductors.md
  - ../05-analog-electronics/bjt-fundamentals-small-signal.md
  - ../04-real-components-hf/component-models-s2p-spice.md
  - ../17-test-measurement/fixtures-and-deembedding.md
level: intermediate
confidence: high
last_updated: 2026-09-27
---

# Two-port networks — Z, Y, h, ABCD and T parameters

## Questions this page answers
- What is a two-port network and why describe circuits that way?
- What do Z, Y, h and ABCD parameters mean physically, and how are they measured?
- Which parameter set should I use for series, parallel or cascaded connections?
- How do I convert between Z, Y, h, ABCD (and S)?
- How do I find the input impedance and voltage gain of a two-port with a load?
- How can I tell from the matrix whether a network is reciprocal, symmetric or lossless?
- Why are ABCD matrices so convenient for ladder filters and transmission lines?
- What are T-parameters and why do different textbooks disagree on them?
- Why are transistor data given as h-parameters (low frequency) but S-parameters (RF)?

## TL;DR
- A **two-port** is any linear network seen through two terminal pairs. Four quantities ($V_1,I_1,V_2,I_2$, currents *into* each port) are linked by a 2×2 matrix; choose which two are independent and you get Z, Y, h or ABCD.
- **Z** (open-circuit impedances): $\mathbf V=\mathbf Z\mathbf I$. **Y** (short-circuit admittances): $\mathbf I=\mathbf Y\mathbf V$. **h** (hybrid): $[V_1,I_2]^T=\mathbf h[I_1,V_2]^T$ — natural for BJTs. **ABCD** (chain): $[V_1,I_1]^T=\mathbf{A}[V_2,-I_2]^T$ — **cascade = matrix product**.
- Combination rules: series–series connections add **Z**; parallel–parallel add **Y**; series–parallel add **h**; cascades multiply **ABCD** (or **T** for wave quantities).
- Building blocks: series impedance $\begin{bmatrix}1&Z\\0&1\end{bmatrix}$, shunt admittance $\begin{bmatrix}1&0\\Y&1\end{bmatrix}$, lossless line $\begin{bmatrix}\cos\beta\ell&jZ_0\sin\beta\ell\\ jY_0\sin\beta\ell&\cos\beta\ell\end{bmatrix}$, ideal transformer $n{:}1$: $\begin{bmatrix}n&0\\0&1/n\end{bmatrix}$.
- Terminated two-port: $Z_{in}=\dfrac{AZ_L+B}{CZ_L+D}=Z_{11}-\dfrac{Z_{12}Z_{21}}{Z_{22}+Z_L}$; $V_2/V_1=Z_L/(AZ_L+B)$.
- **Reciprocal**: $Z_{12}=Z_{21}$, $Y_{12}=Y_{21}$, $h_{12}=-h_{21}$, $AD-BC=1$, $S_{12}=S_{21}$. **Symmetric**: $Z_{11}=Z_{22}$, $A=D$. **Lossless**: all $Z_{ij}$ (and $Y_{ij}$) purely imaginary; $A,D$ real and $B,C$ imaginary (reciprocal case); $\mathbf S^H\mathbf S=\mathbf I$.
- At RF, open and short circuits are hard to make and destabilise active devices, so measurements use **S-parameters** with 50 Ω terminations ([S-parameters](../03-transmission-lines-matching/s-parameters.md)); convert to Z/Y/ABCD for circuit algebra. All conversions on this page are verified against scikit-rf to $10^{-13}$.

## Intuition (no math)
Once you stop caring about the inside of a circuit, all that matters is how the voltages and currents at its two ports relate. Because the network is linear, any two of the four port quantities determine the other two — you just need four numbers (per frequency) saying how. Different "parameter sets" are simply different choices of which two quantities you treat as the inputs:
- **Z-parameters** answer "if I push these currents in, what voltages appear?" You measure them with the other port **open**.
- **Y-parameters** answer "if I apply these voltages, what currents flow?" — measured with the other port **shorted**.
- **h-parameters** mix the two, matching how a transistor naturally behaves: input looks like a small resistance driven by current, output like a current source with a large shunt resistance.
- **ABCD** expresses the input side in terms of the output side, which is exactly what you need when the output of one block *is* the input of the next: you multiply the matrices in order.

The same physics is in all of them; picking the right one turns a messy nodal analysis into one line of algebra.

## The math

### Level 1 — definitions (currents flow *into* both ports)

$$\begin{bmatrix}V_1\\V_2\end{bmatrix}=\begin{bmatrix}Z_{11}&Z_{12}\\Z_{21}&Z_{22}\end{bmatrix}\begin{bmatrix}I_1\\I_2\end{bmatrix},\quad Z_{ij}=\left.\frac{V_i}{I_j}\right|_{I_k=0,\,k\ne j}$$
$$\begin{bmatrix}I_1\\I_2\end{bmatrix}=\mathbf Y\begin{bmatrix}V_1\\V_2\end{bmatrix},\quad \mathbf Y=\mathbf Z^{-1},\quad Y_{ij}=\left.\frac{I_i}{V_j}\right|_{V_k=0}$$
$$\begin{bmatrix}V_1\\I_2\end{bmatrix}=\begin{bmatrix}h_{11}&h_{12}\\h_{21}&h_{22}\end{bmatrix}\begin{bmatrix}I_1\\V_2\end{bmatrix}\quad(h_{11}\ [\Omega],\ h_{12},h_{21}\ [\,\text{–}\,],\ h_{22}\ [\text{S}])$$
$$\begin{bmatrix}V_1\\I_1\end{bmatrix}=\begin{bmatrix}A&B\\C&D\end{bmatrix}\begin{bmatrix}V_2\\-I_2\end{bmatrix}\quad(A,D\ [\,\text{–}\,],\ B\ [\Omega],\ C\ [\text{S}])$$
The minus sign in ABCD makes the output current flow *out of* port 2 and into the next stage, so for a cascade $\mathbf{A}_{tot}=\mathbf{A}_1\mathbf{A}_2\cdots$.

Physical meaning of ABCD: $A=V_1/V_2$ with port 2 open (inverse open-circuit voltage gain), $B=V_1/(-I_2)$ with port 2 shorted (transfer impedance), $C=I_1/V_2$ open, $D=I_1/(-I_2)$ shorted (inverse current gain). For BJTs: $h_{11}=h_{ie}$ (input resistance), $h_{21}=h_{fe}=\beta$, $h_{22}=h_{oe}$, $h_{12}=h_{re}$ (reverse voltage feedback, ~10⁻⁴).

### Level 2 — conversions and terminated two-ports

With $\Delta_Z=Z_{11}Z_{22}-Z_{12}Z_{21}$ (and similarly $\Delta_h$, $\Delta_Y$):

| to ↓ from → | Z | ABCD | h |
|---|---|---|---|
| **Z** | — | $\dfrac1C\begin{bmatrix}A&AD-BC\\1&D\end{bmatrix}$ | $\dfrac{1}{h_{22}}\begin{bmatrix}\Delta_h&h_{12}\\-h_{21}&1\end{bmatrix}$ |
| **ABCD** | $\dfrac1{Z_{21}}\begin{bmatrix}Z_{11}&\Delta_Z\\1&Z_{22}\end{bmatrix}$ | — | $\dfrac{1}{h_{21}}\begin{bmatrix}-\Delta_h&-h_{11}\\-h_{22}&-1\end{bmatrix}$ |
| **h** | $\dfrac{1}{Z_{22}}\begin{bmatrix}\Delta_Z&Z_{12}\\-Z_{21}&1\end{bmatrix}$ | $\dfrac1D\begin{bmatrix}B&AD-BC\\-1&C\end{bmatrix}$ | — |
| **Y** | $\mathbf Z^{-1}$ | $\dfrac1B\begin{bmatrix}D&-(AD-BC)\\-1&A\end{bmatrix}$ | $\dfrac{1}{h_{11}}\begin{bmatrix}1&-h_{12}\\h_{21}&\Delta_h\end{bmatrix}$ |

ABCD → S (equal real reference $Z_0$):
$$S_{11}=\frac{A+B/Z_0-CZ_0-D}{\Sigma},\ S_{12}=\frac{2(AD-BC)}{\Sigma},\ S_{21}=\frac{2}{\Sigma},\ S_{22}=\frac{-A+B/Z_0-CZ_0+D}{\Sigma},\ \Sigma=A+\frac{B}{Z_0}+CZ_0+D.$$
(The Z-, Y- and h-forms of this are tabulated in Pozar Table 4.2 and, for complex reference impedances, in Frickey 1994.)

**Terminated two-port.** Driving port 1 and loading port 2 with $Z_L$ ($V_2=-I_2Z_L$):
$$Z_{in}=\frac{AZ_L+B}{CZ_L+D}=Z_{11}-\frac{Z_{12}Z_{21}}{Z_{22}+Z_L},\qquad\frac{V_2}{V_1}=\frac{Z_L}{AZ_L+B}.$$
With a source $V_s,Z_s$, $V_2/V_s=Z_L/(AZ_L+B+CZ_sZ_L+DZ_s)$ — the formula used for the transducer gain of every ladder filter in [filter prototypes](passive-filter-design-prototypes.md). In h-parameters, $Z_{in}=h_{11}-\dfrac{h_{12}h_{21}Z_L}{1+h_{22}Z_L}$ and $A_v=\dfrac{-h_{21}Z_L}{h_{11}+\Delta_hZ_L}$.

**Interconnection rules** (valid when the "port condition" holds — the current entering one terminal of a port equals that leaving the other; check this when connecting non-isolated two-ports in series):

| Connection | Add |
|---|---|
| series–series (feedback: current sampled, voltage mixed) | Z |
| parallel–parallel (shunt–shunt feedback) | Y |
| series input / parallel output | h |
| parallel input / series output | g ($=\mathbf h^{-1}$) |
| cascade | multiply ABCD (or T) |

### Level 3 — network properties and wave-based matrices

**Reciprocity** (no active devices, ferrites, or plasmas): $Z_{12}=Z_{21}$ ⇔ $Y_{12}=Y_{21}$ ⇔ $h_{12}=-h_{21}$ ⇔ $\det(\text{ABCD})=AD-BC=1$ ⇔ $S_{12}=S_{21}$. **Symmetry** (ports interchangeable): additionally $Z_{11}=Z_{22}$, $A=D$, $S_{11}=S_{22}$. **Lossless**: $\operatorname{Re}Z_{ij}=0$ for all $i,j$; for a reciprocal lossless network $A,D$ are real and $B,C$ purely imaginary; the S-matrix is unitary, $\mathbf S^H\mathbf S=\mathbf I$ (verified for an L-section in the script). **Passive**: $\mathbf Z+\mathbf Z^H$ positive semi-definite.

**Image impedance** of a symmetric network: $Z_{im}=\sqrt{B/C}$ — the termination that makes $Z_{in}$ equal the load. For a lossless line it is $Z_0$; for the 3 dB π-attenuator of the example it is exactly 50 Ω. Image-parameter ("constant-k", "m-derived") filters were designed this way before insertion-loss synthesis.

**T-parameters (transfer scattering).** For cascading in terms of waves, define $[b_1,a_1]^T=\mathbf T[a_2,b_2]^T$ or a variant; then $\mathbf T_{tot}=\mathbf T_1\mathbf T_2\cdots$. **Conventions differ between textbooks and tools** (ordering of $a$/$b$, which port is "input"), so never mix T-matrices from different sources without checking; Frickey (1994) lists consistent sets. The script uses scikit-rf's convention and confirms $\mathbf T(\text{cascade})=\mathbf T_1\mathbf T_2\mathbf T_3$ to $10^{-15}$. T-matrices are the natural tool for **de-embedding** fixtures: $\mathbf T_{DUT}=\mathbf T_{A}^{-1}\mathbf T_{meas}\mathbf T_{B}^{-1}$ ([fixtures and de-embedding](../17-test-measurement/fixtures-and-deembedding.md)).

**Why S-parameters at RF.** Z, Y, h require ideal opens or shorts at the far port. At GHz these are hard to realise (a "short" 5 mm long is 0.1λ at 3 GHz on FR-4), and presenting an open/short to a transistor can make it oscillate. S-parameters are measured with matched loads and remain well-defined for any passive or stable active device; they convert exactly to the others at each frequency ([S-parameters](../03-transmission-lines-matching/s-parameters.md)).

**Noise and multi-ports.** Two-port noise is described by an extra 2×2 correlation matrix (equivalently $F_{min},R_n,\Gamma_{opt}$) that transforms with the same matrix algebra ([noise figure](../07-noise-linearity/noise-figure-and-friis.md)). N-port generalisations (Z, Y, S of any size) follow the same definitions; the ABCD chain form exists only for 2n-ports split into equal input/output groups.

## Design equations & rules of thumb

| Element | ABCD | Notes |
|---|---|---|
| Series $Z$ | $\begin{bmatrix}1&Z\\0&1\end{bmatrix}$ | Z-matrix does not exist (singular) |
| Shunt $Y$ | $\begin{bmatrix}1&0\\Y&1\end{bmatrix}$ | Y-matrix does not exist |
| Line $Z_0,\ \beta\ell$ | $\begin{bmatrix}\cos\beta\ell&jZ_0\sin\beta\ell\\jY_0\sin\beta\ell&\cos\beta\ell\end{bmatrix}$ | lossy: $\beta\ell\to-j\gamma\ell$ (cosh/sinh) |
| Ideal transformer $N_1{:}N_2=n{:}1$ | $\begin{bmatrix}n&0\\0&1/n\end{bmatrix}$ | Z, Y do not exist |
| Π (Y₁, Z₃, Y₂) | $\begin{bmatrix}1+Y_2Z_3&Z_3\\Y_1+Y_2+Y_1Y_2Z_3&1+Y_1Z_3\end{bmatrix}$ | attenuators, Pi matches |
| T (Z₁, Y₃, Z₂) | $\begin{bmatrix}1+Z_1Y_3&Z_1+Z_2+Z_1Z_2Y_3\\Y_3&1+Z_2Y_3\end{bmatrix}$ | — |
| 50 Ω π-attenuator, $K=10^{A/20}$ | $R_{sh}=Z_0\frac{K+1}{K-1}$, $R_{se}=Z_0\frac{K^2-1}{2K}$ | 3 dB: 292.4 Ω / 17.6 Ω |

## Worked examples

### 1. L-section at 433.92 MHz
Series 22 nH ($jX=j59.98\ \Omega$) followed by shunt 6.1 pF ($jB=j16.63$ mS):
$\mathbf A=\begin{bmatrix}1&j59.98\\0&1\end{bmatrix}\begin{bmatrix}1&0\\j0.01663&1\end{bmatrix}=\begin{bmatrix}0.0025&j59.98\\j0.01663&1\end{bmatrix}$.
Checks: $A$, $D$ real and $B$, $C$ imaginary (lossless, reciprocal); $AD-BC=1$. With a 50 Ω load, $Z_{in}=(0.0025\cdot50+j59.98)/(j0.8316+1)=29.56+j35.40\ \Omega$ — computed both from ABCD and from Z-parameters in `tools/verify/circuits_two_port.py`.

### 2. A 3 dB 50 Ω π attenuator
$K=10^{3/20}=1.4125$: shunt resistors 292.4 Ω, series 17.61 Ω. The cascade $\mathbf A=\mathbf Y_{sh}\mathbf Z_{se}\mathbf Y_{sh}$ is symmetric ($A=D$), reciprocal ($AD-BC=1$), $S_{11}=0$, $S_{21}=-3.000$ dB, image impedance 50.000 Ω. Nearest E96 values 294 Ω and 17.8 Ω. (Chip-resistor parasitics at RF: [resistors at RF](../04-real-components-hf/resistors-at-rf.md).)

### 3. Common-emitter BJT stage from h-parameters
$h_{ie}=2.5$ kΩ, $h_{re}=2\times10^{-4}$, $h_{fe}=100$, $h_{oe}=20\ \mu$S, load 2 kΩ. Then $\Delta_h=0.05-0.02=0.03$, $A_v=-100\cdot2000/(2500+0.03\cdot2000)=-78.1$ and $Z_{in}=2500-\dfrac{2\times10^{-4}\cdot100\cdot2000}{1+0.04}=2461.5\ \Omega$. Converting to Z gives $Z_{12}=10\ \Omega$ but $Z_{21}=-5$ MΩ — grossly non-reciprocal, as any amplifier must be. (Script §4b.)

## Practical notes
- **Use ABCD for ladders and cascades, Y for shunt feedback and transistor π-models, Z for series feedback, h for BJT datasheet parameters, S for anything measured above ~100 MHz.**
- **Numerical pitfalls:** a pure series element has no Z-matrix and a pure shunt element no Y-matrix (they are singular). Converting a near-ideal through through Z or Y is ill-conditioned; ABCD and S are always safe for passive parts.
- **Reference impedance.** S-parameters depend on the port reference impedance; Z, Y, h, ABCD do not. When importing a vendor `.s2p` file check the `# Hz S MA R 50` header line for the reference ([component models](../04-real-components-hf/component-models-s2p-spice.md)).
- **Ground-referenced vs floating ports.** Most RF two-ports share a common ground; the "port condition" required for series connection rules may be violated when you connect two such networks in series — use a full nodal simulation instead.

## Common mistakes & misconceptions
- **Sign of $I_2$.** Z, Y, h use current *into* port 2; ABCD uses $-I_2$ (out of port 2). Mixing conventions gives wrong signs in $B$ and $D$.
- **Multiplying Z-matrices for a cascade.** Only ABCD (or T) matrices multiply for cascades; Z matrices *add* for series–series connections.
- **Assuming $S_{21}=V_2/V_1$.** $S_{21}$ is a wave ratio with matched terminations; $V_2/V_1=Z_L/(AZ_L+B)$ depends on the load.
- **Taking T-parameters from one book and a formula from another.** Conventions differ; verify with a known cascade first.
- **Reciprocity test on measured data.** Small asymmetries ($S_{12}\ne S_{21}$ by 0.01 dB) are measurement error, not physics, for passive parts.

## How to simulate / verify
- `python3 tools/verify/circuits_two_port.py` — tests all conversion formulas on this page against scikit-rf for 200 random networks (max error 1.3×10⁻¹³), checks cascading via ABCD and T products, and reproduces the three worked examples.
- scikit-rf: `skrf.network.s2z, s2y, s2h, s2a, s2t` and inverses; `ntwk.z`, `ntwk.y`, `ntwk.a` properties; cascade with `**`; de-embed with `ntwk_fixture.inv ** meas ** ...`.
- SPICE: extract Z-parameters with AC current sources at each port (one at a time), Y with AC voltage sources and zero-volt ammeters.

## Open questions / gaps
- None significant; complex-reference-impedance conversions (power waves vs pseudo-waves) are left to [S-parameters](../03-transmission-lines-matching/s-parameters.md).

## Sources
1. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — §4.2 (Z and Y matrices, reciprocity, losslessness), §4.3 (S-matrix), §4.4 (ABCD matrix, Table 4.1 of common two-ports, Table 4.2 conversions). (textbook)
2. D. A. Frickey, "Conversions between S, Z, Y, h, ABCD, and T parameters which are valid for complex source and load impedances," *IEEE Trans. Microwave Theory Tech.*, 42(2), 205–211, 1994. (peer-reviewed)
3. R. Ludwig, G. Bogdanov, *RF Circuit Design: Theory and Applications*, 2nd ed., Pearson, 2009 — ch. 4 (single- and multi-port networks, interconnection rules, conversion table). (textbook)
4. A. S. Sedra, K. C. Smith, *Microelectronic Circuits*, 7th ed., Oxford UP, 2015 — two-port feedback topologies and h-parameter transistor models. (textbook)
5. scikit-rf developers, *scikit-rf documentation*, v2.0 — `skrf.network` conversion functions and T-parameter convention. https://scikit-rf.readthedocs.io (software documentation)
6. Verification script `tools/verify/circuits_two_port.py` (this KB).
