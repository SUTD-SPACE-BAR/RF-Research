---
title: S-parameters
domain: 03-transmission-lines-matching
slug: s-parameters
tags: [s-parameters, scattering-matrix, power-waves, pseudo-waves, renormalisation, mixed-mode, touchstone, t-parameters, group-delay, stability, power-gain, de-embedding]
prerequisites:
  - reflections-vswr-return-loss-mismatch.md
  - ../01-circuit-theory/two-port-networks-zyh-abcd.md
  - ../00-math-foundations/matrices-and-linear-algebra-for-networks.md
related:
  - signal-flow-graphs-mason.md
  - smith-chart.md
  - time-domain-reflectometry.md
  - ../06-rf-circuits/amplifier-stability-and-biasing.md
  - ../06-rf-circuits/lna-design.md
  - ../04-real-components-hf/component-models-s2p-spice.md
  - ../17-test-measurement/vna-fundamentals-calibration.md
  - ../17-test-measurement/fixtures-and-deembedding.md
level: mixed
confidence: high
last_updated: 2026-10-14
---

# S-parameters

## Questions this page answers
- What exactly are S-parameters, and why do we use waves instead of voltages and currents at RF?
- What do $S_{11}$, $S_{21}$, $S_{12}$, $S_{22}$ mean physically, and what does "referenced to 50 Ω" mean?
- What is the difference between Kurokawa power waves and Marks–Williams pseudo-waves, and when does it matter?
- How do I convert S to Z, Y or ABCD, change the reference impedance, or cascade networks (T-parameters)?
- How do I check that a measured S-matrix is physical (reciprocal, lossless, passive)?
- What are mixed-mode (differential/common) S-parameters?
- How do I read a Touchstone (.s2p) file, and why is the column order S11 S21 S12 S22?
- How do I get group delay from S21? What are K and μ?

## TL;DR
- Incident and reflected **waves** at port $i$: $a_i=\dfrac{V_i+Z_{0}I_i}{2\sqrt{Z_0}}$, $b_i=\dfrac{V_i-Z_{0}I_i}{2\sqrt{Z_0}}$ (real reference $Z_0$, peak phasors; $|a|^2/2$ is power in watts). $\mathbf b=\mathbf S\mathbf a$; $S_{ij}=b_i/a_j$ with all other ports terminated in $Z_0$ (so $a_k=0$).
- $S_{11}$ = input reflection coefficient with a matched load; $S_{21}$ = forward transmission (gain/loss) with matched terminations; $|S_{21}|^2$ = transducer gain between 50 Ω terminations.
- VNAs measure S because waves can be separated with directional couplers and matched terminations are stable at RF — opens and shorts (needed for Z/Y) make active devices oscillate and are hard to realise.
- For **complex** reference impedances there are two inequivalent definitions: Kurokawa **power waves** ($b=(V-Z_R^*I)/2\sqrt{\mathrm{Re}Z_R}$; $|a|^2-|b|^2$ is exactly delivered power; zero reflection = conjugate match) and Marks–Williams **pseudo-waves** (w.r.t. the line's $Z_0$; consistent with travelling waves and cascading, but power is not simply $|a|^2-|b|^2$). For real $Z_0$ they coincide (scikit-rf `s_def='power'|'pseudo'|'traveling'`).
- Physical checks: reciprocal ⇔ $\mathbf S=\mathbf S^T$; lossless ⇔ $\mathbf S^H\mathbf S=\mathbf I$; passive ⇔ eigenvalues of $\mathbf I-\mathbf S^H\mathbf S\ge0$.
- $\mathbf Z=Z_0(\mathbf I+\mathbf S)(\mathbf I-\mathbf S)^{-1}$; ABCD for cascading voltages/currents; **T-parameters** for cascading waves (`T_total = T_A T_B`), inverse for de-embedding. T conventions differ between books — state yours.
- **Mixed-mode**: $S_{dd}$, $S_{cc}$, $S_{dc}$, $S_{cd}$ with 100 Ω differential / 25 Ω common-mode references (for 50 Ω single-ended ports). A 6 mm skew at 2.4 GHz converts ≈ −16.5 dB of differential signal into common mode.
- Group delay $\tau_g=-d\angle S_{21}/d\omega$ (1 m of VF 0.66 cable: 5.05 ns). Stability: $K>1$ and $|\Delta|<1$, or $\mu>1$.

## Intuition (no math)
At DC or low frequency we characterise a box by measuring voltages with ports open and currents with ports shorted (Z and Y parameters). At RF, "open" and "short" are hard to make (a short piece of wire is an inductor; an open end radiates and has fringing capacitance), active devices oscillate when terminated in reactive loads, and voltage and current vary along every connecting cable. What *is* easy at RF is to launch a wave down a 50 Ω cable, terminate the other ports in 50 Ω, and measure what comes back and what comes out, with directional couplers that separate forward and reverse waves.

So S-parameters describe a network as a wave router: of the wave you send into port 1, a fraction $S_{11}$ bounces back, $S_{21}$ comes out of port 2, and so on. Magnitudes squared are power fractions; phases are delays. Because the ports are terminated in the reference impedance, what you measure doesn't depend on the cable lengths — only the reference plane moves the phases, which is why calibration defines "where the port is".

## The math

### Level 1 — definitions (real reference impedance)
With $Z_0$ real (usually 50 Ω) and peak-phasor $V_i$, $I_i$ (current into port $i$):
$$a_i=\frac{V_i+Z_0I_i}{2\sqrt{Z_0}},\qquad b_i=\frac{V_i-Z_0I_i}{2\sqrt{Z_0}},\qquad V_i=\sqrt{Z_0}(a_i+b_i),\quad I_i=\frac{a_i-b_i}{\sqrt{Z_0}}.$$
Power into port $i$: $P_i=\tfrac12(|a_i|^2-|b_i|^2)$. For a two-port
$$\begin{bmatrix}b_1\\b_2\end{bmatrix}=\begin{bmatrix}S_{11}&S_{12}\\S_{21}&S_{22}\end{bmatrix}\begin{bmatrix}a_1\\a_2\end{bmatrix}.$$
Useful dB language: *return loss* $=-20\log|S_{11}|$; *insertion loss* $=-20\log|S_{21}|$ (passive); *gain* $=20\log|S_{21}|$ (amplifier); *isolation* $=-20\log|S_{12}|$.

### Level 2 — conversions, properties, operations

**S ↔ Z, Y, ABCD.** From $\mathbf V=\sqrt{Z_0}(\mathbf a+\mathbf b)$, $\mathbf I=(\mathbf a-\mathbf b)/\sqrt{Z_0}$ and $\mathbf V=\mathbf Z\mathbf I$:
$$\mathbf Z=Z_0(\mathbf I+\mathbf S)(\mathbf I-\mathbf S)^{-1},\qquad \mathbf S=(\mathbf Z-Z_0\mathbf I)(\mathbf Z+Z_0\mathbf I)^{-1},\qquad\mathbf Y=\mathbf Z^{-1}.$$
Two-port S → ABCD (Pozar Table 4.2):
$$A=\frac{(1+S_{11})(1-S_{22})+S_{12}S_{21}}{2S_{21}},\quad B=Z_0\frac{(1+S_{11})(1+S_{22})-S_{12}S_{21}}{2S_{21}},$$
$$C=\frac{(1-S_{11})(1-S_{22})-S_{12}S_{21}}{2S_{21}Z_0},\quad D=\frac{(1-S_{11})(1+S_{22})+S_{12}S_{21}}{2S_{21}}.$$
All verified against scikit-rf (`tools/verify/tline_sparams.py`). Frickey (1994) gives the full table including complex, unequal port impedances.

**Reciprocity, losslessness, passivity.**
- Reciprocal (no ferrites/active parts): $\mathbf Z=\mathbf Z^T\Leftrightarrow\mathbf S=\mathbf S^T$.
- Lossless: power in = power out for any excitation ⇒ $\mathbf a^H\mathbf a=\mathbf b^H\mathbf b=\mathbf a^H\mathbf S^H\mathbf S\mathbf a$ ⇒ $\mathbf S^H\mathbf S=\mathbf I$ (unitary). For a lossless two-port: $|S_{11}|=|S_{22}|$, $|S_{11}|^2+|S_{21}|^2=1$ — a lossless network cannot be matched at one port and mismatched at the other.
- Passive: $\mathbf I-\mathbf S^H\mathbf S$ positive semidefinite; its eigenvalues are the dissipated fractions for the eigen-excitations. Measured data that violate passivity (small negative eigenvalues) indicate calibration error and cause non-causal/unstable time-domain simulations; tools offer "passivity enforcement".

**Changing the reference impedance (renormalisation).** One-port: with $r=(Z_0'-Z_0)/(Z_0'+Z_0)$, $\Gamma'=(\Gamma-r)/(1-r\Gamma)$ — a Möbius map ([Smith chart](smith-chart.md)). N-port: convert to Z and back with the new $Z_0'$ (scikit-rf `renormalize_s`). Example: a filter measured in 50 Ω but used between 75 Ω ports.

**Cascading: T-parameters.** Rearranging waves as port-1 quantities in terms of port-2 quantities gives a matrix that multiplies along a chain. scikit-rf's convention (Dobrowolski): $\begin{bmatrix}b_1\\a_1\end{bmatrix}=\mathbf T\begin{bmatrix}a_2\\b_2\end{bmatrix}$ with
$$\mathbf T=\begin{bmatrix}S_{12}-\dfrac{S_{11}S_{22}}{S_{21}}&\dfrac{S_{11}}{S_{21}}\\[2mm]-\dfrac{S_{22}}{S_{21}}&\dfrac1{S_{21}}\end{bmatrix},\qquad\mathbf T_{A\to B}=\mathbf T_A\mathbf T_B.$$
Other books order the vectors as $[a_1;b_1]=\mathbf T[b_2;a_2]$, which permutes and changes signs of entries — always check before mixing formulas. **De-embedding**: if $\mathbf T_\text{meas}=\mathbf T_\text{fix}\mathbf T_\text{DUT}$, then $\mathbf T_\text{DUT}=\mathbf T_\text{fix}^{-1}\mathbf T_\text{meas}$ (scikit-rf: `fixture.inv ** meas`). Verified. Practice (2x-thru, TRL) → [fixtures & de-embedding](../17-test-measurement/fixtures-and-deembedding.md).

**Group delay.** $\tau_g(\omega)=-\dfrac{d\,\angle S_{21}}{d\omega}$ (unwrap the phase first). For a TEM line $\tau_g=\ell/v_p$: 5.054 ns for 1 m at VF 0.66 (script). Group-delay ripple indicates dispersion (filters near band edges, SAW filters), important for wideband modulations and chirp (LoRa CSS tolerates it well; FMCW radar and OFDM less so).

**Power gains of a two-port (preview for amplifiers).** With source and load reflection coefficients $\Gamma_S$, $\Gamma_L$ and $\Gamma_\text{in}=S_{11}+\dfrac{S_{12}S_{21}\Gamma_L}{1-S_{22}\Gamma_L}$, $\Gamma_\text{out}=S_{22}+\dfrac{S_{12}S_{21}\Gamma_S}{1-S_{11}\Gamma_S}$:
$$G_T=\frac{(1-|\Gamma_S|^2)|S_{21}|^2(1-|\Gamma_L|^2)}{|1-\Gamma_S\Gamma_\text{in}|^2|1-S_{22}\Gamma_L|^2},$$
$$G_A=\frac{(1-|\Gamma_S|^2)|S_{21}|^2}{|1-S_{11}\Gamma_S|^2(1-|\Gamma_\text{out}|^2)},\qquad G_{power}=\frac{|S_{21}|^2(1-|\Gamma_L|^2)}{(1-|\Gamma_\text{in}|^2)|1-S_{22}\Gamma_L|^2}.$$
$G_{power}$ is the operating power gain $P_L/P_{in}$ (textbooks write $G_P$; the KB writes $G_{power}$ so it cannot be confused with the processing gain $G_{proc}$ of [spread spectrum](../10-comms-modulation/spread-spectrum-dsss-fhss-css.md)). $G_T\le G_A$ and $G_T\le G_{power}$, with equality under output/input conjugate match respectively; $G_T=|S_{21}|^2$ for 50 Ω terminations (all checked over 500 random terminations). Derivation via signal-flow graphs: [Mason's rule](signal-flow-graphs-mason.md).

**Stability (preview).** $\Delta=S_{11}S_{22}-S_{12}S_{21}$. Rollett: $K=\dfrac{1-|S_{11}|^2-|S_{22}|^2+|\Delta|^2}{2|S_{12}S_{21}|}$; unconditionally stable iff $K>1$ and $|\Delta|<1$. Edwards–Sinsky single-parameter test $\mu=\dfrac{1-|S_{11}|^2}{|S_{22}-\Delta S_{11}^*|+|S_{12}S_{21}|}>1$ (and its dual μ′) — the distance from the Smith-chart centre to the nearest unstable load. If stable, maximum available gain $MAG=\left|\dfrac{S_{21}}{S_{12}}\right|(K-\sqrt{K^2-1})$, achieved by simultaneous conjugate match (checked: $G_T(\Gamma_{Sm},\Gamma_{Lm})=MAG$). Full treatment → [amplifier stability](../06-rf-circuits/amplifier-stability-and-biasing.md), [LNA design](../06-rf-circuits/lna-design.md).

### Level 3 — waves with complex references, and mixed-mode

**Power waves (Kurokawa 1965).** For a reference $Z_R$ (possibly complex, e.g. the conjugate of a source impedance):
$$a=\frac{V+Z_RI}{2\sqrt{\mathrm{Re}Z_R}},\qquad b=\frac{V-Z_R^*I}{2\sqrt{\mathrm{Re}Z_R}},\qquad\Gamma_p=\frac{Z_L-Z_R^*}{Z_L+Z_R}.$$
Then $\tfrac12(|a|^2-|b|^2)$ is exactly the power delivered, $|a|^2/2$ is the available power of a source with internal impedance $Z_R$, and $\Gamma_p=0$ means *conjugate* match. These are natural for amplifier gain and noise theory.

**Pseudo-waves (Marks & Williams 1992).** On a real (possibly lossy) line the physical travelling waves are defined w.r.t. the line's characteristic impedance $Z_0$, generally complex. Pseudo-waves w.r.t. an arbitrary reference $Z_R$:
$$a=\frac{\sqrt{\mathrm{Re}Z_R}}{2|Z_R|}(V+Z_RI),\qquad b=\frac{\sqrt{\mathrm{Re}Z_R}}{2|Z_R|}(V-Z_RI),\qquad\Gamma=\frac{Z_L-Z_R}{Z_L+Z_R}.$$
With $Z_R=Z_0$ these *are* the travelling waves of the line — required for multiline TRL calibration and for consistent cascading of lossy-line sections; but $\tfrac12(|a|^2-|b|^2)$ is not the net power when $Z_R$ is complex (script: −0.00065 vs the true 0.00363 in a test case). VNAs calibrated with TRL on lossy lines produce pseudo-wave S-parameters referenced to the line's $Z_0$; renormalising to 50 Ω needs $Z_0$ (via the line's capacitance). For real references — the everyday 50 Ω case — all definitions coincide (script checks scikit-rf's three `s_def` options).

**Mixed-mode S-parameters (Bockelman & Eisenstadt 1995).** For a pair of single-ended ports (1, 2) forming a differential port, define differential and common voltages/currents $V_d=V_1-V_2$, $I_d=(I_1-I_2)/2$, $V_c=(V_1+V_2)/2$, $I_c=I_1+I_2$, with reference impedances $Z_d=2Z_0$ (100 Ω) and $Z_c=Z_0/2$ (25 Ω). The 4-port single-ended matrix transforms by an orthogonal matrix $\mathbf M$ into
$$\mathbf S_\text{mm}=\begin{bmatrix}\mathbf S_{dd}&\mathbf S_{dc}\\\mathbf S_{cd}&\mathbf S_{cc}\end{bmatrix}=\mathbf M\mathbf S\mathbf M^{-1}.$$
$S_{dd21}$ is the wanted differential transmission; $S_{cd21}$ (differential in → common out) measures mode conversion — the source of EMI and of degraded common-mode rejection. For two ideal matched lines with an electrical skew $\Delta\theta$: $|S_{dd21}|=|\cos(\Delta\theta/2)|$, $|S_{cd21}|=|\sin(\Delta\theta/2)|$ (script, via scikit-rf `se2gmm`). Differential pairs: [planar lines](planar-lines-microstrip-stripline-cpwg.md); baluns: [baluns](../06-rf-circuits/baluns-and-rf-transformers.md).

**Touchstone format.** Text files `.sNp` (v1.x) or `.ts` (v2.0/2.1, IBIS Open Forum). Option line `# <freq unit> <param S|Y|Z|H|G> <format MA|DB|RI> R <ref>`, e.g. `# MHz S MA R 50`. Each 2-port frequency line lists **S11, S21, S12, S22** — a historical quirk (for N ≥ 3 the order is row-wise S11 S12 S13…). Noise parameters may follow the S-data in 2-port files. Version 2.1 (ratified Jan 2024) adds more flexible per-port reference definitions. scikit-rf reads/writes both (`rf.Network('x.s2p')`, `ntw.write_touchstone()`); round-trip verified.

## Design equations & rules of thumb

| Equation | When valid | Notes |
|---|---|---|
| $a=(V+Z_0I)/2\sqrt{Z_0}$, $b=(V-Z_0I)/2\sqrt{Z_0}$ | real $Z_0$ | $P=\tfrac12(|a|^2-|b|^2)$ |
| $S_{ij}=b_i/a_j\,|_{a_k=0,k\neq j}$ | all ports in $Z_0$ | |
| $\mathbf Z=Z_0(\mathbf I+\mathbf S)(\mathbf I-\mathbf S)^{-1}$ | equal real $Z_0$ | Frickey for general |
| $\mathbf S=\mathbf S^T$ / $\mathbf S^H\mathbf S=\mathbf I$ | reciprocal / lossless | sanity-check measured data |
| $\Gamma'=(\Gamma-r)/(1-r\Gamma)$ | 1-port renormalisation | $r=(Z_0'-Z_0)/(Z_0'+Z_0)$ |
| $\mathbf T_\text{tot}=\mathbf T_A\mathbf T_B$; $\mathbf T_\text{DUT}=\mathbf T_\text{fix}^{-1}\mathbf T_\text{meas}$ | 2-ports | convention-dependent entries |
| $\tau_g=-d\angle S_{21}/d\omega$ | | 1 m VF 0.66: 5.05 ns |
| $K>1,|\Delta|<1$ or $\mu>1$ | unconditional stability | check at all f incl. out of band |
| $MAG=|S_{21}/S_{12}|(K-\sqrt{K^2-1})$ | K > 1 | MSG = |S21/S12| if K < 1 |
| $Z_d=2Z_0$, $Z_c=Z_0/2$ | mixed-mode refs | 100 Ω / 25 Ω |

## Worked examples

### Example 1 — reading a LoRa SAW filter's S21
A 433 MHz SAW filter datasheet `.s2p`: at 433.9 MHz, $S_{21}=0.79\angle{-112°}$ → insertion loss $-20\log0.79=2.05$ dB; $S_{11}=0.2\angle{40°}$ → RL 14 dB. Phase slope: if $\angle S_{21}$ goes from −100° to −124° between 433.4 and 434.4 MHz, $\tau_g=24°/(360°\times1\text{ MHz})=67$ ns — typical for SAW (acoustic waves are slow). Lossless check: $|S_{11}|^2+|S_{21}|^2=0.04+0.62=0.66$ → 34 % of the power is dissipated (that is the 2 dB loss, less the 0.18 dB mismatch).

### Example 2 — is my measured amplifier data physical and stable?
Illustrative device (script): $S_{11}=0.55\angle{-150°}$, $S_{12}=0.06\angle{40°}$, $S_{21}=3.2\angle{75°}$, $S_{22}=0.45\angle{-35°}$. $|\Delta|=0.225$, $K=1.421$, $\mu=1.224$ → unconditionally stable at this frequency. $|S_{21}|^2=10.1$ dB, $MAG=13.4$ dB (simultaneous conjugate match), $MSG=17.3$ dB. Repeat at *every* frequency where the device has gain — most oscillations happen out of band.

### Example 3 — mode conversion from a skewed differential pair
A 100 Ω differential pair to a 2.4 GHz balanced chip antenna has 6 mm length mismatch (in air for simplicity; on FR-4 multiply the electrical skew by $\sqrt{\varepsilon_\text{eff}}$). $\Delta\theta=2\pi\times2.4\text{ GHz}\times6\text{ mm}/c=17.3°$ → $|S_{cd21}|=\sin(8.6°)=0.150$ = −16.5 dB, $|S_{dd21}|=\cos(8.6°)=0.989$ (−0.1 dB). The differential loss is negligible, but 2.2 % of the power becomes common-mode current — a radiator on the cable/board.

### Example 4 — renormalising a 75 Ω component
A 75 Ω TV-type splitter measured with a 50 Ω VNA reads $S_{11}=0.2$ (real) at a frequency where it is perfectly matched in its own system. $r=(75-50)/(75+50)=0.2$ → $\Gamma'=(0.2-0.2)/(1-0.04)=0$. The "bad" 50 Ω return loss (14 dB) is purely the reference change.

## Practical notes
- **Reference planes**: S-parameters are defined at calibrated reference planes. The phase of $S_{11}$ is meaningless unless you know where the plane is (a 1 mm error on FR-4 microstrip at 2.4 GHz, $\varepsilon_\text{eff}\approx3.3$, is ≈ 5.2° one way, ≈ 10.5° on $S_{11}$).
- **Vendor models**: component and transistor `.s2p` files are measured on specific test fixtures (pad sizes, substrate, via counts). Using them on a different layout needs pad models or re-extraction ([component models](../04-real-components-hf/component-models-s2p-spice.md)).
- **Small-signal only**: S-parameters are linear; for PAs under compression use large-signal methods (load-pull, X-parameters).
- **Check before you trust**: run reciprocity, passivity and (for passive parts) causality checks on measured data before building a design on it. scikit-rf: `rf.network.passivity(s)`, `rf.network.reciprocity(s)`.
- **NanoVNA limitations**: two-port NanoVNAs measure S11 and S21 only (one direction); reverse parameters require flipping the DUT (and assume the "full two-port" correction is approximated).

## Common mistakes & misconceptions
- **"$S_{21}$ is the gain in my circuit."** Only between 50 Ω terminations. With other terminations use $G_T$.
- **"$|S_{11}|$ small means the device is lossless/efficient."** A 50 Ω resistor has $S_{11}=0$.
- **Mixing T-parameter conventions** from different books — the matrices differ in ordering and sign.
- **Confusing power waves and pseudo-waves** when reference impedances are complex — use power waves for gain/noise with complex source impedances, pseudo-waves for lossy-line calibration; they coincide for 50 Ω real.
- **Touchstone column order**: 2-port lines are S11 S21 S12 S22, not S11 S12 S21 S22.
- **Stability checked only in band** — K and μ must be > 1 at all frequencies where the device has gain.
- **Using dB magnitudes to cascade** — cascading requires complex S/T (phases matter; mismatch ripples).

## How to simulate / verify
- `tools/verify/tline_sparams.py` — conversions vs scikit-rf, power vs pseudo waves (complex reference), unitarity/reciprocity/passivity, renormalisation, mixed-mode with skew, T-matrix cascade and de-embedding, group delay, Touchstone round trip and column order, power-gain identities, K/Δ/μ/MAG with simultaneous conjugate match. All pass.
- scikit-rf essentials:

```python
import skrf as rf
amp = rf.Network('device.s2p')
print(amp.z0[0], amp.s_db[0])          # reference impedances; S in dB at first frequency
amp.plot_s_smith(m=0, n=0)             # S11 on the Smith chart
stab = amp.stability                   # Rollett K vs frequency
gd = amp.group_delay[:, 1, 0]          # group delay of S21
amp75 = amp.copy(); amp75.renormalize(75)
dut = fixture.inv ** measured           # de-embed a characterised fixture
diff = four_port.copy(); diff.se2gmm(p=2)   # mixed-mode (ports 1,2 -> in; 3,4 -> out)
```

## Open questions / gaps
- Causality checking/enforcement and rational fitting (vector fitting) of S-parameters for SPICE are only mentioned (→ [16-simulation-tools](../16-simulation-tools/spice-circuit-simulation.md)).
- Noise parameters in Touchstone and noise-wave formalism → [07-noise-linearity](../07-noise-linearity/noise-figure-and-friis.md).
- X-parameters / large-signal characterisation not covered.

## Sources
1. K. Kurokawa, "Power waves and the scattering matrix," *IEEE Trans. MTT*, vol. 13, no. 2, pp. 194–202, Mar. 1965. (peer-reviewed)
2. R. B. Marks and D. F. Williams, "A general waveguide circuit theory," *J. Res. NIST*, vol. 97, no. 5, pp. 533–562, 1992, doi:10.6028/jres.097.024 (free); erratum 2014. (peer-reviewed)
3. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley 2012 — §4.3 (S-matrix, generalized S-parameters, power waves), §4.4 (ABCD, Table 4.2 conversions), §4.5 (signal-flow graphs), §12.1–12.3 (power gains, stability, K–Δ and μ). (textbook)
4. D. A. Frickey, "Conversions between S, Z, Y, h, ABCD, and T parameters which are valid for complex source and load impedances," *IEEE Trans. MTT*, vol. 42, no. 2, pp. 205–211, Feb. 1994. (peer-reviewed)
5. D. E. Bockelman and W. R. Eisenstadt, "Combined differential and common-mode scattering parameters: theory and simulation," *IEEE Trans. MTT*, vol. 43, no. 7, pp. 1530–1539, Jul. 1995. (peer-reviewed)
6. J. M. Rollett, "Stability and power-gain invariants of linear twoports," *IRE Trans. Circuit Theory*, vol. 9, no. 1, pp. 29–32, 1962; M. L. Edwards and J. H. Sinsky, "A new criterion for linear 2-port stability using geometrically derived parameters," *IEEE Trans. MTT*, vol. 40, no. 12, pp. 2303–2311, 1992. (peer-reviewed)
7. Hewlett-Packard/Agilent/Keysight, *S-Parameter Design*, Application Note 154 (5952-1087), 1990 — https://www.keysight.com/us/en/assets/7018-06743/application-notes/5952-1087.pdf. (app note)
8. IBIS Open Forum, *Touchstone® File Format Specification*, Version 2.0 (2009) and Version 2.1 (ratified 26 Jan 2024) — https://ibis.org/touchstone_ver2.1/touchstone_ver2_1.pdf. (standard)
9. J. A. Dobrowolski, *Scattering Parameters in RF and Microwave Circuit Analysis and Design*, Artech House 2016, pp. 65–68 — T-parameter convention used by scikit-rf. (textbook)
10. scikit-rf 2.0.1 documentation — `Network`, `s_def`, `renormalize`, `se2gmm`, `s2t` — https://scikit-rf.readthedocs.io/. (software documentation)
11. Verification: `tools/verify/tline_sparams.py`. (numerical check)
